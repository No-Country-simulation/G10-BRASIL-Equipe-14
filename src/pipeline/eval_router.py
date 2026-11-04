import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from src.config import (
    DEFAULT_CASES,
    DEFAULT_TEMPERATURE,
    OUTPUTS_DIR,
    PROJECT_ROOT,
    GEMINI_API_KEY,
    GROQ_API_KEY,
    GEMINI_MODEL,
    GROQ_MODEL,
    ROUTER_VERSION,
)
from src.services.llm_service import call_gemini, call_groq
from src.utils.json_parser import parse_llm_json as parse_json
from src.utils.prompt_loader import load_router_system_prompt
from src.validation.rules_validator import (
    check_output as check,
    fake_output,
    invalid_inputs,
)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        from dotenv import load_dotenv

        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["gemini", "groq"], default="gemini")
    parser.add_argument("--cases", nargs="+", type=Path)
    parser.add_argument("--only", help="roda só os casos cujo nome contém este texto")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--sleep", type=float, default=5.0)
    parser.add_argument("--tag", default="")
    args = parser.parse_args()

    # Carrega prompt e versão
    system = load_router_system_prompt()
    version = ROUTER_VERSION

    default_case_paths = (
        [Path(p) for p in DEFAULT_CASES] if "DEFAULT_CASES" in globals() else []
    )
    target_case_paths = args.cases or [p for p in default_case_paths if p.exists()]

    cases = []
    case_paths = args.cases or [p for p in DEFAULT_CASES if p.exists()]
    for path in case_paths:
        if path.exists():
            cases += json.loads(path.read_text(encoding="utf-8"))

    if args.only:
        cases = [c for c in cases if args.only in c["case"]]

    if problems := invalid_inputs(cases):
        print("Casos inválidos encontrados:")
        for p in problems:
            print(f"  - {p}")
        return 2

    replay = (
        json.loads(Path(args.replay).read_text(encoding="utf-8"))["outputs"]
        if args.replay
        else None
    )

    active_key = GEMINI_API_KEY if args.provider == "gemini" else GROQ_API_KEY
    key_name = "GEMINI_API_KEY" if args.provider == "gemini" else "GROQ_API_KEY"

    if not args.dry_run and replay is None and not active_key:
        print(f"Falta a chave {key_name}. Configure no arquivo .env.")
        return 2

    call_fn = call_gemini if args.provider == "gemini" else call_groq
    model = GEMINI_MODEL if args.provider == "gemini" else GROQ_MODEL

    print(
        f"Router v{version} | modo: {'dry-run' if args.dry_run else f'{args.provider}/{model}'} | {len(cases)} casos\n"
    )

    passed, saved, results = 0, {}, {}
    total_duration = 0.0

    for case in cases:
        call_error = None
        duration = 0.0

        if args.dry_run:
            output = fake_output(case)
        elif replay is not None:
            output = replay.get(case["case"], {})
        else:
            user = f"Classifique a thread abaixo:\n\nTHREAD:\n{json.dumps(case['input'], ensure_ascii=False)}"
            try:
                start_time = time.perf_counter()  # Inicia a contagem do tempo
                raw = call_fn(system, user, active_key)
                duration = time.perf_counter() - start_time  # Calcula a latência
                total_duration += duration

                output = parse_json(raw)
            except Exception as exc:
                output, call_error = {}, str(exc)
                print(f"  erro: {exc}")
            time.sleep(args.sleep)

        saved[case["case"]] = output
        errors, warnings = check(output, case["expected"])

        if not args.dry_run and replay is None:
            results[case["case"]] = {
                "ok": not errors,
                "errors": errors,
                "warnings": warnings,
                "duration_seconds": round(
                    duration, 3
                ),  # Salva o tempo no log/resultado
            }
            if call_error:
                results[case["case"]]["call_error"] = call_error

        passed += not errors
        status = "OK   " if not errors else "FALHA"
        time_str = f" ({duration:.2f}s)" if duration > 0 else ""
        print(
            f"[{status}] {case['case']}{time_str}"
            + ("" if not errors else f" -> {'; '.join(errors)}")
        )
        for w in warnings:
            print(f"        aviso: {w}")

    rate = (passed / len(cases) * 100) if cases else 0
    avg_duration = (
        (total_duration / len(cases)) if len(cases) > 0 and not args.dry_run else 0.0
    )

    print(f"\nTaxa de acerto: {passed}/{len(cases)} ({rate:.0f}%)")
    if not args.dry_run and replay is None and len(cases) > 0:
        print(
            f"Tempo médio por requisição: {avg_duration:.2f}s (Total: {total_duration:.2f}s)"
        )

    if not args.dry_run and replay is None and cases:
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M")
        tag_str = f"_{args.tag}" if args.tag else ""

        case_suffix = ""
        if target_case_paths:
            first_case_name = Path(target_case_paths[0]).stem.lower()
            if "sintet" in first_case_name or "synthetic" in first_case_name:
                case_suffix = "_sinteticos"
            elif "real" in first_case_name:
                case_suffix = "_reais"
            else:
                case_suffix = f"_{first_case_name.replace('router_cases_', '')}"

        out_file = (
            OUTPUTS_DIR / f"router_v{version}_{args.provider}{case_suffix}{tag_str}_{stamp}.json"
        )

        meta = {
            "prompt_version": version,
            "model": model,
            "temperature": DEFAULT_TEMPERATURE,
            "accuracy": f"{passed}/{len(cases)}",
            "case_files": [str(p) for p in target_case_paths],
            "average_duration_seconds": round(avg_duration, 3),
            "total_duration_seconds": round(total_duration, 3),
            "ran_at": datetime.now().isoformat(timespec="seconds"),
        }

        out_file.write_text(
            json.dumps(
                meta | {"results": results, "outputs": saved},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Salvo em: {out_file.relative_to(PROJECT_ROOT)}")

    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
