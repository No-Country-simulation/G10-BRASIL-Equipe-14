from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.pipeline.adapters_processor import CaseResult, TokenUsage


def print_case_result(case_name: str, result: CaseResult) -> None:
    status = "OK   " if result.passed else "FALHA"
    time_text = (
        f" ({result.duration_seconds:.2f}s)" if result.duration_seconds > 0 else ""
    )
    error_text = "" if result.passed else f" -> {'; '.join(result.errors)}"
    print(f"[{status}] {case_name}{time_text}{error_text}")

    usage = result.token_usage
    if usage is None:
        print("        tokens: indisponível")
    else:
        print(
            "        tokens: "
            f"entrada={usage['prompt_tokens']}, "
            f"saída={usage['completion_tokens']}, "
            f"total={usage['total_tokens']}"
        )
    for warning in result.warnings:
        print(f"        aviso: {warning}")


def summarize_tokens(results: dict[str, CaseResult]) -> TokenUsage | None:
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
    rate = passed / total_cases * 100 if total_cases else 0
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
    if total_duration > 0 and total_cases:
        print(
            "Tempo médio por job: "
            f"{total_duration / total_cases:.2f}s "
            f"(Total: {total_duration:.2f}s)"
        )


def save_report(
    *,
    output_dir: Path,
    project_root: Path,
    prompt_versions: dict[str, str],
    router_run: dict[str, Any],
    provider: str,
    model: str,
    temperature: float,
    case_path: Path,
    jobs: list[dict[str, Any]],
    results: dict[str, CaseResult],
    total_duration: float,
    reference_period: str | None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    output_file = output_dir / f"adapters_{provider}_{timestamp}.json"
    passed = sum(result.passed for result in results.values())

    try:
        relative_case_path = str(case_path.relative_to(project_root))
    except ValueError:
        relative_case_path = str(case_path)

    metadata = {
        "prompt_versions": prompt_versions,
        "router_run": router_run,
        "model": model,
        "temperature": temperature,
        "accuracy": f"{passed}/{len(jobs)}",
        "case_file": relative_case_path,
        "reference_period_newsletter": reference_period,
        "average_duration_seconds": round(
            total_duration / len(jobs) if jobs else 0.0, 3
        ),
        "total_duration_seconds": round(total_duration, 3),
        "ran_at": datetime.now().isoformat(timespec="seconds"),
        "token_usage": summarize_tokens(results),
    }

    cases_data = {}
    if case_path.exists():
        try:
            cases_data = json.loads(case_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    items_map = {i["id"]: i for i in cases_data.get("items", [])}

    exemplos_list = []
    for job in jobs:
        case_name = job["nome"]
        result = results.get(case_name)

        attempts_data = getattr(result, "attempts", None)
        if not attempts_data:
            output_val = result.output if result else None
            errors_val = result.errors if result else []
            attempts_data = [{"output": output_val, "errors": errors_val}]

        job_item_ids = job.get("itens", [])
        job_items = [
            items_map[itemId] for itemId in job_item_ids if itemId in items_map
        ]

        if job_items:
            origem_val = sorted(
                {i.get("origem")
                 for i in job_items if i.get("origem") is not None}
            )
        else:
            raw_origem = job.get("origem", ["sintetico"])
            origem_val = raw_origem if isinstance(
                raw_origem, list) else [raw_origem]

        if isinstance(job_item_ids, str):
            itens_val = [job_item_ids]
        elif isinstance(job_item_ids, list):
            itens_val = job_item_ids
        else:
            itens_val = [str(job_item_ids)]

        exemplo_item = {
            "nome": case_name,
            "canal": job.get("canal"),
            "itens_de_origem": itens_val,
            "origem": origem_val,
            "tentativas": attempts_data,
        }
        if job.get("nota"):
            exemplo_item["nota"] = job["nota"]

        exemplos_list.append(exemplo_item)

    payload = metadata | {
        "results": {name: result.to_dict() for name, result in results.items()},
        "exemplos": exemplos_list,
    }

    output_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Salvo em: {output_file.relative_to(project_root)}")
    return output_file


def save_csv_report(
    *,
    output_dir: Path,
    project_root: Path,
    prompt_versions: dict[str, str],
    provider: str,
    jobs: list[dict[str, Any]],
    results: dict[str, CaseResult],
    timestamp: str,
) -> Path:
    version_label = "_".join(
        f"{name}-v{version}" for name, version in prompt_versions.items()
    )
    output_file = output_dir / f"adapters_{provider}_{timestamp}.csv"
    fieldnames = [
        "Caso de Teste",
        "Canal",
        "Itens de Origem",
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
        for index, job in enumerate(jobs, start=1):
            result = results[job["nome"]]
            usage = result.token_usage or {}
            writer.writerow(
                {
                    "Caso de Teste": f"CT{index:02d}",
                    "Canal": job["canal"],
                    "Itens de Origem": ", ".join(job["itens"]),
                    "Case": job["nome"],
                    "Acerto": "Ok" if result.passed else "Falha",
                    "Tempo de Execução": f"{result.duration_seconds:.2f}s",
                    "Tokens Consolidados (Entrada)": usage.get("prompt_tokens", ""),
                    "Tokens Consolidados (Saída)": usage.get("completion_tokens", ""),
                    "Tokens Consolidados (Total)": usage.get("total_tokens", ""),
                }
            )
    print(f"Salvo em: {output_file.relative_to(project_root)}")
    return output_file
