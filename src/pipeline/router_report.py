from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.pipeline.router_processor import CaseResult, TokenUsage


def print_case_result(
    case_name: str,
    result: CaseResult,
) -> None:
    status = "OK   " if result.passed else "FALHA"

    time_text = (
        f" ({result.duration_seconds:.2f}s)" if result.duration_seconds > 0 else ""
    )

    error_text = "" if result.passed else f" -> {'; '.join(result.errors)}"

    print(f"[{status}] {case_name}{time_text}{error_text}")

    if result.token_usage is None:
        print("        tokens: indisponível")

    else:
        usage = result.token_usage
        print(
            "        tokens: "
            f"entrada={usage['prompt_tokens']}, "
            f"saída={usage['completion_tokens']}, "
            f"total={usage['total_tokens']}"
        )

    for warning in result.warnings:
        print(f"        aviso: {warning}")


def summarize_tokens(
    results: dict[str, CaseResult],
) -> TokenUsage | None:
    available = [
        result.token_usage
        for result in results.values()
        if result.token_usage is not None
    ]

    if not available:
        return None

    return {
        "prompt_tokens": sum(usage["prompt_tokens"] for usage in available),
        "completion_tokens": sum(usage["completion_tokens"] for usage in available),
        "total_tokens": sum(usage["total_tokens"] for usage in available),
    }


def print_summary(
    *,
    passed: int,
    total_cases: int,
    total_duration: float,
    results: dict[str, CaseResult],
) -> None:
    rate = passed / total_cases * 100
    token_usage = summarize_tokens(results)

    print(f"\nTaxa de acerto: {passed}/{total_cases} " f"({rate:.0f}%)")

    if token_usage is None:
        print("\nTokens consolidados: indisponível")
    else:
        print(
            "\nTokens consolidados: "
            f"entrada={token_usage['prompt_tokens']}, "
            f"saída={token_usage['completion_tokens']}, "
            f"total={token_usage['total_tokens']}"
        )

    if total_duration > 0:
        average_duration = total_duration / total_cases

        print(
            "Tempo médio por requisição: "
            f"{average_duration:.2f}s "
            f"(Total: {total_duration:.2f}s)"
        )


def save_report(
    *,
    output_dir: Path,
    project_root: Path,
    version: str,
    provider: str,
    model: str,
    temperature: float,
    cases: list[dict[str, Any]],
    results: dict[str, CaseResult],
    total_duration: float,
    tag: str,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    passed = sum(1 for result in results.values() if result.passed)

    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    tag_suffix = f"_{tag}" if tag else ""

    output_file = (
        output_dir / f"router_v{version}_{provider}" f"{tag_suffix}_{stamp}.json"
    )

    average_duration = total_duration / len(cases) if cases else 0.0

    metadata: dict[str, Any] = {
        "prompt_version": version,
        "model": model,
        "temperature": temperature,
        "accuracy": f"{passed}/{len(cases)}",
        "case_files": [str(path) for path in cases],
        "average_duration_seconds": round(average_duration, 3),
        "total_duration_seconds": round(total_duration, 3),
        "ran_at": datetime.now().isoformat(timespec="seconds"),
        "token_usage": summarize_tokens(results),
    }

    serialized_results = {
        case_name: result.to_dict() for case_name, result in results.items()
    }

    payload = metadata | {
        "results": serialized_results,
        "outputs": {case_name: result.output for case_name, result in results.items()},
    }

    output_file.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Salvo em: " f"{output_file.relative_to(project_root)}")

    return output_file


def save_csv_report(
    *,
    output_dir: Path,
    project_root: Path,
    version: str,
    provider: str,
    cases: list[dict[str, Any]],
    results: dict[str, CaseResult],
    stamp: str,
    tag: str,
) -> Path:
    tag_suffix = f"_{tag}" if tag else ""
    output_file = (
        output_dir / f"router_v{version}_{provider}" f"{tag_suffix}_{stamp}.csv"
    )

    fieldnames = [
        "Caso de Teste",
        "Conjunto",
        "Fonte de Dados",
        "Case",
        "Acerto",
        "Tempo de Execução",
        "Tokens Consolidados (Entrada)",
        "Tokens Consolidados (Saída)",
        "Tokens Consolidados (Total)",
    ]

    with output_file.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for index, case in enumerate(cases, start=1):
            case_name = case["case"]
            result = results[case_name]
            usage = result.token_usage or {}
            source = case.get("input", {}).get("source", "desconhecida")

            writer.writerow(
                {
                    "Caso de Teste": f"CT{index:02d}",
                    "Conjunto": _dataset_label(case_name),
                    "Fonte de Dados": _source_label(source),
                    "Case": case_name,
                    "Acerto": "Ok" if result.passed else "Falha",
                    "Tempo de Execução": f"{result.duration_seconds:.2f}s",
                    "Tokens Consolidados (Entrada)": usage.get("prompt_tokens", ""),
                    "Tokens Consolidados (Saída)": usage.get(
                        "completion_tokens",
                        "",
                    ),
                    "Tokens Consolidados (Total)": usage.get("total_tokens", ""),
                }
            )

    print(f"Salvo em: {output_file.relative_to(project_root)}")

    return output_file


def _dataset_label(case_name: str) -> str:
    if case_name.startswith("real_"):
        return "Casos Reais"

    return "Casos Sintéticos"


def _source_label(source: Any) -> str:
    labels = {
        "stackoverflow": "Stack Overflow/Stack Exchange",
        "mastodon": "Mastodon",
        "hackernews": "Hacker News",
    }

    return labels.get(str(source).lower(), str(source))
