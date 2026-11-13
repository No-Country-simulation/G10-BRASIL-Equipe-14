from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config import (
    ADAPTER_CASES,
    ADAPTER_NEWSLETTER_FAQ_VERSION,
    ADAPTER_SOCIAL_VERSION,
    OUTPUTS_DIR,
    PROJECT_ROOT,
)
from src.pipeline.adapters_loader import load_adapter_base_prompt
from src.utils.cases_loader import load_adapter_cases
from src.utils.provider_config import provider_config
from src.validation.adapters_validator import invalid_inputs


@dataclass(frozen=True)
class AdapterContext:
    jobs: list[dict[str, Any]]
    items: dict[str, dict[str, Any]]
    reference_period: str | None
    router_run: dict[str, Any]
    prompt_versions: dict[str, str]
    provider: str
    model: str
    temperature: float
    case_path: Path
    output_dir: Path
    project_root: Path
    header: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Executa a avaliação dos adapters LLM."
    )
    parser.add_argument(
        "--provider",
        choices=("gemini", "groq"),
        default="gemini",
        help="Provedor LLM utilizado na avaliação.",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=ADAPTER_CASES,
        help="Arquivo JSON com jobs e itens dos adapters.",
    )
    parser.add_argument(
        "--only",
        help="Executa somente jobs cujo nome contém este texto.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida o fluxo sem chamar o provedor.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=5.0,
        help="Pausa entre chamadas para respeitar limites do provedor.",
    )

    return parser


def load_and_filter_cases(
    case_path: Path,
    only: str | None,
) -> tuple[
    list[dict[str, Any]],
    dict[str, dict[str, Any]],
    str | None,
    dict[str, Any],
]:
    if not case_path.exists():
        raise ValueError(f"Arquivo de casos não encontrado: {case_path}")

    try:
        data = load_adapter_cases(case_path)
    except ValueError as exc:
        raise ValueError(f"Erro ao carregar casos: {exc}") from exc

    problems = invalid_inputs(data)
    if problems:
        details = "\n".join(f"  - {problem}" for problem in problems)
        raise ValueError(f"Casos de adapters inválidos:\n{details}")

    items = {item["id"]: item for item in data["items"]}
    jobs = [job for job in data["jobs"] if only is None or only in job.get("nome", "")]

    if not jobs:
        raise ValueError("Nenhum job de adapter foi carregado.")

    return (
        jobs,
        items,
        data.get("reference_period_newsletter"),
        data.get("router_run", {}),
    )


def prepare_execution(args: argparse.Namespace) -> AdapterContext:
    jobs, items, reference_period, router_run = load_and_filter_cases(
        case_path=args.cases,
        only=args.only,
    )
    api_key, model, temperature, api_key_name = provider_config(args.provider)

    if not args.dry_run and not api_key:
        raise ValueError(
            f"Falta a chave {api_key_name}. " "Configure-a no arquivo .env."
        )

    for job in jobs:
        load_adapter_base_prompt(job["canal"])

    mode = "dry-run" if args.dry_run else f"{args.provider}/{model}"
    prompt_versions = {
        "social": ADAPTER_SOCIAL_VERSION,
        "newsletter_faq": ADAPTER_NEWSLETTER_FAQ_VERSION,
    }
    header = (
        f"Adapters social v{prompt_versions['social']} / "
        f"newsletter_faq v{prompt_versions['newsletter_faq']} | "
        f"modo: {mode} | {len(jobs)} jobs\n"
    )

    return AdapterContext(
        jobs=jobs,
        items=items,
        reference_period=reference_period,
        router_run=router_run,
        prompt_versions=prompt_versions,
        provider=args.provider,
        model=model,
        temperature=temperature,
        case_path=args.cases,
        output_dir=OUTPUTS_DIR,
        project_root=PROJECT_ROOT,
        header=header,
    )
