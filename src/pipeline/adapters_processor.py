from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from src.services.llm_providers import call_llm
from src.utils.json_parser import parse_llm_json
from src.validation.adapters_validator import check_output
from src.pipeline.adapters_prompt_builder import (
    build_user_prompt,
    build_correction_prompt,
)

TokenUsage = dict[str, int]


@dataclass
class CaseResult:
    output: Any
    errors: list[str]
    warnings: list[str]
    duration_seconds: float = 0.0
    token_usage: TokenUsage | None = None
    call_error: str | None = None
    retry_used: bool = False

    @property
    def passed(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "ok": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "duration_seconds": round(self.duration_seconds, 3),
            "retry_used": self.retry_used,
        }
        if self.token_usage is not None:
            result["token_usage"] = self.token_usage
        if self.call_error:
            result["call_error"] = self.call_error
        return result


def _merge_token_usage(
    first: TokenUsage | None,
    second: TokenUsage | None,
) -> TokenUsage | None:
    if first is None and second is None:
        return None
    return {
        "prompt_tokens": (first or {}).get("prompt_tokens", 0)
        + (second or {}).get("prompt_tokens", 0),
        "completion_tokens": (first or {}).get("completion_tokens", 0)
        + (second or {}).get("completion_tokens", 0),
        "total_tokens": (first or {}).get("total_tokens", 0)
        + (second or {}).get("total_tokens", 0),
    }


def _call_and_parse(
    provider: str,
    system: str,
    user: str,
) -> tuple[Any, TokenUsage | None, str | None, str]:
    try:
        response = call_llm(provider=provider, system=system, user=user)
        usage = {
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
            "total_tokens": response.total_tokens,
        }
        return parse_llm_json(response.text), usage, None, response.text
    except (KeyError, RuntimeError, TypeError, ValueError) as exc:
        return {}, None, str(exc), ""


def execute_case(
    job: dict[str, Any],
    *,
    items: list[dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    system: str,
    reference_period: str | None,
    provider: str,
    dry_run: bool = False,
) -> CaseResult:
    started_at = time.perf_counter()
    if dry_run:
        return CaseResult(
            output={"target": job["canal"],
                    "title": "dry-run", "body": "dry-run"},
            errors=[],
            warnings=[],
        )

    user_prompt = build_user_prompt(job, items, reference_period)
    output, first_usage, call_error, raw_response = _call_and_parse(
        provider=provider,
        system=system,
        user=user_prompt,
    )
    errors, warnings = check_output(
        {
            "nome": job["nome"],
            "itens_de_origem": job["itens"],
            "output": output,
        },
        sources,
    )
    retry_used = False
    second_usage = None

    correction = (
        build_correction_prompt(
            previous_response=raw_response,
            errors=errors,
            channel=job["canal"],
        )
        if call_error is None
        else None
    )
    if correction:
        retry_used = True
        correction_system, correction_user = correction
        output, second_usage, call_error, _ = _call_and_parse(
            provider=provider,
            system=correction_system,
            user=correction_user,
        )

    if call_error:
        errors = [f"erro na chamada/JSON: {call_error}"]
        warnings = []
    else:
        errors, warnings = check_output(
            {
                "nome": job["nome"],
                "canal": job["canal"],
                "itens_de_origem": job["itens"],
                "output": output,
            },
            sources,
        )

    return CaseResult(
        output=output,
        errors=errors,
        warnings=warnings,
        duration_seconds=time.perf_counter() - started_at,
        token_usage=_merge_token_usage(first_usage, second_usage),
        call_error=call_error,
        retry_used=retry_used,
    )
