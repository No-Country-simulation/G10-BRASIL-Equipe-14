from __future__ import annotations

import sys
import time

from src.pipeline.router_setup import build_parser, prepare_execution
from src.pipeline.router_processor import CaseResult, execute_case
from src.pipeline.router_report import (
    print_case_result,
    print_summary,
    save_report,
    save_csv_report,
)


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

    results: dict[str, CaseResult] = {}

    for index, case in enumerate(context.cases):
        result = execute_case(
            case,
            system=context.system,
            few_shot=context.few_shot,
            provider=context.provider,
            dry_run=args.dry_run,
            replay=context.replay,
        )

        case_name = case["case"]
        results[case_name] = result

        print_case_result(
            case_name,
            result,
        )

        is_live_execution = not args.dry_run and context.replay is None

        is_not_last_case = index < len(context.cases) - 1

        if is_live_execution and is_not_last_case and args.sleep > 0:
            time.sleep(args.sleep)

    passed = sum(1 for result in results.values() if result.passed)

    total_duration = sum(result.duration_seconds for result in results.values())

    print_summary(
        passed=passed,
        total_cases=len(context.cases),
        total_duration=total_duration,
        results=results,
    )

    is_live_execution = not args.dry_run and context.replay is None
    is_complete_execution = args.only is None

    if is_live_execution and is_complete_execution:
        report_path = save_report(
            output_dir=context.output_dir,
            project_root=context.project_root,
            version=context.version,
            provider=context.provider,
            model=context.model,
            temperature=context.temperature,
            cases=context.cases,
            results=results,
            total_duration=total_duration,
            tag=args.tag,
        )
        save_csv_report(
            output_dir=context.output_dir,
            project_root=context.project_root,
            version=context.version,
            provider=context.provider,
            cases=context.cases,
            results=results,
            stamp=report_path.stem.rsplit("_", 1)[-1],
            tag=args.tag,
        )

    return 0 if passed == len(context.cases) else 1


if __name__ == "__main__":
    sys.exit(main())
