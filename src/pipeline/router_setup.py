from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config import (
    DEFAULT_CASES,
    DEFAULT_TEMPERATURE,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GROQ_API_KEY,
    GROQ_MODEL,
    OUTPUTS_DIR,
    PROJECT_ROOT,
    ROUTER_VERSION,
)
from src.pipeline.router_loader import (
    load_router_base_prompt,
    load_router_few_shot_prompt,
)
from src.utils.cases_loader import load_cases, load_replay
from src.validation.router_validator import invalid_inputs


@dataclass(frozen=True)
class RouterContext:
    cases: list[dict[str, Any]]
    replay: dict[str, Any] | None
    system: str
    few_shot: str
    provider: str
    model: str
    temperature: float
    case_paths: list[Path]
    output_dir: Path
    project_root: Path
    version: str
    header: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Executa a avaliação do Router LLM.")

    parser.add_argument(
        "--provider",
        choices=("gemini", "groq"),
        default="gemini",
        help="Provedor LLM utilizado na avaliação.",
    )

    parser.add_argument(
        "--cases",
        nargs="+",
        type=Path,
        help=(
            "Arquivos de casos. Por padrão: "
            "router_cases_sinteticos.json e router_cases_reais.json."
        ),
    )

    parser.add_argument(
        "--only",
        help="Executa somente casos cujo nome contém este texto.",
    )

    execution_group = parser.add_mutually_exclusive_group()

    execution_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida o fluxo sem chamar o provedor.",
    )

    execution_group.add_argument(
        "--replay",
        type=Path,
        help="JSON com saídas já geradas.",
    )

    parser.add_argument(
        "--sleep",
        type=float,
        default=5.0,
        help="Pausa entre chamadas para respeitar limites do provedor.",
    )

    parser.add_argument(
        "--tag",
        default="",
        help="Rótulo incluído no nome do arquivo de saída.",
    )

    return parser


def load_and_filter_cases(
    case_paths: list[Path],
    only: str | None,
) -> list[dict[str, Any]]:
    missing_paths = [path for path in case_paths if not path.exists()]

    if missing_paths:
        details = "\n".join(f"  - {path}" for path in missing_paths)

        raise ValueError("Arquivos de casos não encontrados:\n" f"{details}")

    try:
        cases = load_cases(case_paths)
    except ValueError as exc:
        raise ValueError(f"Erro ao carregar casos: {exc}") from exc

    if only:
        cases = [case for case in cases if only in case.get("case", "")]

    if not cases:
        raise ValueError("Nenhum caso de avaliação foi carregado.")

    problems = invalid_inputs(cases)

    if problems:
        details = "\n".join(f"  - {problem}" for problem in problems)

        raise ValueError(
            "Casos fora do "
            "data/schemas/input_schema.json "
            "(corrija antes de rodar):\n"
            f"{details}"
        )

    return cases


def load_replay_file(
    replay_path: Path | None,
) -> dict[str, Any] | None:
    if replay_path is None:
        return None

    try:
        return load_replay(replay_path)
    except ValueError as exc:
        raise ValueError(f"Erro ao carregar replay: {exc}") from exc


def provider_config(
    provider: str,
) -> tuple[str, str, float, str]:
    configurations = {
        "gemini": (
            GEMINI_API_KEY,
            GEMINI_MODEL,
            GEMINI_TEMPERATURE,
            "GEMINI_API_KEY",
        ),
        "groq": (
            GROQ_API_KEY,
            GROQ_MODEL,
            DEFAULT_TEMPERATURE,
            "GROQ_API_KEY",
        ),
    }

    try:
        return configurations[provider]
    except KeyError as exc:
        raise ValueError(f"Provedor não suportado: {provider}") from exc


def execution_mode(
    *,
    dry_run: bool,
    replay: dict[str, Any] | None,
    provider: str,
    model: str,
) -> str:
    if dry_run:
        return "dry-run"

    if replay is not None:
        return "replay"

    return f"{provider}/{model}"


def prepare_execution(
    args: argparse.Namespace,
) -> RouterContext:
    case_paths = args.cases or list(DEFAULT_CASES)

    cases = load_and_filter_cases(
        case_paths=case_paths,
        only=args.only,
    )

    replay = load_replay_file(args.replay)
    system = load_router_base_prompt()
    few_shot = load_router_few_shot_prompt()

    api_key, model, temperature, api_key_name = provider_config(args.provider)

    if not args.dry_run and replay is None and not api_key:
        raise ValueError(
            f"Falta a chave {api_key_name}. " "Configure-a no arquivo .env."
        )

    mode = execution_mode(
        dry_run=args.dry_run,
        replay=replay,
        provider=args.provider,
        model=model,
    )

    header = f"Router v{ROUTER_VERSION} | " f"modo: {mode} | " f"{len(cases)} casos\n"

    return RouterContext(
        cases=cases,
        replay=replay,
        system=system,
        few_shot=few_shot,
        provider=args.provider,
        model=model,
        temperature=temperature,
        case_paths=case_paths,
        output_dir=OUTPUTS_DIR,
        project_root=PROJECT_ROOT,
        version=ROUTER_VERSION,
        header=header,
    )
