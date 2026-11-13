from __future__ import annotations

import sys
import time

from src.pipeline.adapters_loader import load_adapter_base_prompt
from src.pipeline.adapters_processor import CaseResult, execute_case
from src.pipeline.adapters_report import (
    print_case_result,
    print_summary,
    save_csv_report,
    save_report,
)
from src.pipeline.adapters_setup import build_parser, prepare_execution
from src.validation.adapters_validator import load_sources


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = build_parser().parse_args()
    try:
        context = prepare_execution(args)
    except ValueError as exc:
        print(exc)
        return 2

    print(context.header)
    sources = load_sources()
    results: dict[str, CaseResult] = {}

    for index, job in enumerate(context.jobs):
        try:
            system = load_adapter_base_prompt(job["canal"])
            job_items = [context.items[item_id] for item_id in job["itens"]]
        except (KeyError, ValueError, FileNotFoundError) as exc:
            print(f"[ERRO] {job.get('nome', '<job sem nome>')}: {exc}")
            return 2

        result = execute_case(
            job,
            items=job_items,
            sources=sources,
            system=system,
            reference_period=context.reference_period,
            provider=context.provider,
            dry_run=args.dry_run,
        )
        results[job["nome"]] = result
        print_case_result(job["nome"], result)

        if not args.dry_run and index < len(context.jobs) - 1 and args.sleep > 0:
            time.sleep(args.sleep)

    passed = sum(result.passed for result in results.values())
    total_duration = sum(result.duration_seconds for result in results.values())
    print_summary(
        passed=passed,
        total_cases=len(context.jobs),
        total_duration=total_duration,
        results=results,
    )

    if not args.dry_run:
        report_path = save_report(
            output_dir=context.output_dir,
            project_root=context.project_root,
            prompt_versions=context.prompt_versions,
            router_run=context.router_run,
            provider=context.provider,
            model=context.model,
            temperature=context.temperature,
            case_path=context.case_path,
            jobs=context.jobs,
            results=results,
            total_duration=total_duration,
            reference_period=context.reference_period,
        )
        save_csv_report(
            output_dir=context.output_dir,
            project_root=context.project_root,
            prompt_versions=context.prompt_versions,
            provider=context.provider,
            jobs=context.jobs,
            results=results,
            timestamp=report_path.stem.rsplit("_", 1)[-1],
        )

    return 0 if passed == len(context.jobs) else 1


if __name__ == "__main__":
    sys.exit(main())
