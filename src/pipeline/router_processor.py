from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

from src.services.llm_providers import call_llm
from src.utils.json_parser import parse_llm_json
from src.validation.router_validator import (
    check_output,
    fake_output,
)
from src.config import RETRYABLE_ERROR_PREFIXES

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
            "duration_seconds": round(
                self.duration_seconds,
                3,
            ),
            "retry_used": self.retry_used,
        }

        if self.token_usage is not None:
            result["token_usage"] = self.token_usage

        if self.call_error:
            result["call_error"] = self.call_error

        return result


def _build_user_prompt(
    case: dict[str, Any],
) -> str:
    return (
        "Classifique a thread abaixo:\n\n"
        "THREAD:\n"
        f"{json.dumps(case['input'], ensure_ascii=False)}"
    )


def _merge_token_usage(
    first: TokenUsage | None,
    second: TokenUsage | None,
) -> TokenUsage | None:
    if first is None and second is None:
        return None

    return {
        "prompt_tokens": (
            (first or {}).get("prompt_tokens", 0)
            + (second or {}).get("prompt_tokens", 0)
        ),
        "completion_tokens": (
            (first or {}).get("completion_tokens", 0)
            + (second or {}).get("completion_tokens", 0)
        ),
        "total_tokens": (
            (first or {}).get("total_tokens", 0) + (second or {}).get("total_tokens", 0)
        ),
    }


def _response_token_usage(
    response: Any,
) -> TokenUsage:
    return {
        "prompt_tokens": response.prompt_tokens,
        "completion_tokens": response.completion_tokens,
        "total_tokens": response.total_tokens,
    }


def _is_retryable_error(
    errors: list[str],
) -> bool:
    return any(
        error.startswith(prefix)
        for error in errors
        for prefix in RETRYABLE_ERROR_PREFIXES
    )


def _build_correction_prompt(
    *,
    previous_response: str,
    errors: list[str],
) -> tuple[str, str]:
    correction_system = (
        "Você é um corretor de saída JSON. "
        "Corrija somente os erros informados na resposta anterior. "
        "Retorne exclusivamente um objeto JSON válido, sem markdown ou explicações. "
        "Não invente dados e preserve os valores corretos já existentes."
    )

    correction_user = (
        "RESPOSTA ANTERIOR:\n"
        f"{previous_response or '{}'}\n\n"
        "ERROS ENCONTRADOS:\n" + "\n".join(f"- {error}" for error in errors) + "\n\n"
        "Reavalie apenas o necessário e retorne o JSON corrigido."
    )

    return correction_system, correction_user


def _call_and_parse(
    *,
    provider: str,
    system: str,
    user: str,
) -> tuple[Any, TokenUsage | None, str | None, str]:
    try:
        response = call_llm(
            provider=provider,
            system=system,
            user=user,
        )

        usage = _response_token_usage(response)
        output = parse_llm_json(response.text)

        return output, usage, None, response.text

    except (KeyError, RuntimeError, TypeError, ValueError) as exc:
        return {}, None, str(exc), ""


def _execute_live_case(
    case: dict[str, Any],
    *,
    base_prompt: str,
    few_shot_prompt: str,
    provider: str,
) -> tuple[
    Any,
    float,
    TokenUsage | None,
    str | None,
    bool,
]:
    user_prompt = _build_user_prompt(case)
    started_at = time.perf_counter()

    output, first_usage, call_error, raw_response = _call_and_parse(
        provider=provider,
        system=base_prompt,
        user=user_prompt,
    )

    errors, warnings = check_output(
        output,
        case["expected"],
        case,
    )

    retry_used = False
    second_usage: TokenUsage | None = None

    should_retry = call_error is None and _is_retryable_error(errors)

    if should_retry:
        retry_used = True

        correction_system, correction_user = _build_correction_prompt(
            previous_response=raw_response, errors=errors,
        )

        (
            output,
            second_usage,
            call_error,
            _,
        ) = _call_and_parse(
            provider=provider,
            system=correction_system,
            user=correction_user,
        )

        errors, warnings = check_output(
            output,
            case["expected"],
            case,
        )

    duration = time.perf_counter() - started_at
    token_usage = _merge_token_usage(
        first_usage,
        second_usage,
    )

    return (
        output,
        duration,
        token_usage,
        call_error,
        retry_used,
    )


def execute_case(
    case: dict[str, Any],
    *,
    system: str,
    few_shot: str,
    provider: str,
    dry_run: bool = False,
    replay: dict[str, Any] | None = None,
) -> CaseResult:
    case_name = case["case"]

    if dry_run:
        output = fake_output(case)

        result = CaseResult(
            output=output,
            errors=[],
            warnings=[],
            duration_seconds=0.0,
            token_usage=None,
            call_error=None,
            retry_used=False,
        )

    elif replay is not None:
        output = replay.get(case_name, {})

        result = CaseResult(
            output=output,
            errors=[],
            warnings=[],
            duration_seconds=0.0,
            token_usage=None,
            call_error=None,
            retry_used=False,
        )

    else:
        (
            output,
            duration,
            token_usage,
            call_error,
            retry_used,
        ) = _execute_live_case(
            case,
            base_prompt=system,
            few_shot_prompt=few_shot,
            provider=provider,
        )

        result = CaseResult(
            output=output,
            errors=[],
            warnings=[],
            duration_seconds=duration,
            token_usage=token_usage,
            call_error=call_error,
            retry_used=retry_used,
        )

    result.errors, result.warnings = check_output(
        result.output,
        case["expected"],
        case,
    )

    return result
