"""Avalia o prompt do Router contra os casos de teste (issue #8 [S1-03]).

Uso (na raiz do repositório):
    uv run python -m src.pipeline.eval_router                     # Gemini (GEMINI_API_KEY no .env)
    uv run python -m src.pipeline.eval_router --provider groq     # Groq (GROQ_API_KEY no .env)
    uv run python -m src.pipeline.eval_router --dry-run           # testa o script sem chamar API
    uv run python -m src.pipeline.eval_router --only real_se      # roda só os casos cujo nome contém "real_se"
    uv run python -m src.pipeline.eval_router --cases data/prompts/tests/router_cases_reais.json --tag reais
                                                                  # roda só os 14 casos com dados reais
    uv run python -m src.pipeline.eval_router --replay data/prompts/tests/outputs/<arquivo>.json
                                                                  # reavalia saídas já salvas, sem chamar API

Critério de aceite da issue #8: 100% dos casos aprovados.
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib import error, request

try:
    from dotenv import load_dotenv
except ImportError:  # python-dotenv está no pyproject; isto só evita quebrar fora do uv
    load_dotenv = None

ROOT = Path(__file__).resolve().parents[2]
PROMPT_FILE = ROOT / "data/prompts/router.md"
TESTS_DIR = ROOT / "data/prompts/tests"
DEFAULT_CASES = [TESTS_DIR / "router_cases.json", TESTS_DIR / "router_cases_reais.json"]
OUTPUTS_DIR = TESTS_DIR / "outputs"
INPUT_SCHEMA = ROOT / "data/schemas/input_schema.json"

ENUMS = {
    "type": {"job_achievement", "testimonial", "technical_question", "course_feedback", "debate", "noise"},
    "sentiment": {"positive", "neutral", "negative"},
    "topic_category": {"frontend", "backend", "data", "ai_ml", "devops_cloud", "mobile", "dev_tools", "career", "other"},
    "original_language": {"pt", "es", "en", "other"},
    "suggested_route": {"success_case", "faq", "newsletter_only", "moderation", "discard"},
}
REQUIRED = set(ENUMS) | {"id", "source", "topics", "has_answer", "relevance_score", "summary", "justification"}
SPECIAL_KEYS = {"suggested_route_in", "min_score", "max_score"}


def load_system_prompt() -> tuple[str, str]:
    text = PROMPT_FILE.read_text(encoding="utf-8")
    version = re.search(r"^versao:\s*(\S+)", text, re.M)
    block = text.split("## SYSTEM PROMPT", 1)[1]
    match = re.search(r"```text\n(.*?)```", block, re.S)
    return match.group(1).strip(), (version.group(1) if version else "?")


def invalid_inputs(cases: list[dict]) -> list[str]:
    """Confere cada caso contra o input_schema.json do repositório (se existir)."""
    if not INPUT_SCHEMA.exists():
        return []
    try:
        import jsonschema
    except ImportError:
        return []
    schema = json.loads(INPUT_SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    problems = []
    for case in cases:
        for err in validator.iter_errors(case["input"]):
            problems.append(f"{case['case']}: {err.message}")
    return problems


def route_from_fields(out: dict) -> str:
    """Mesmas regras do router.md, na mesma ordem. É o que o nó Switch do n8n deve fazer."""
    score = out.get("relevance_score", -1)
    if out.get("type") == "noise":
        return "discard"
    if out.get("sentiment") == "negative":
        return "moderation"
    if score < 40:
        return "discard"
    if out.get("type") in ("job_achievement", "testimonial") and out.get("sentiment") == "positive" and score >= 80:
        return "success_case"
    if out.get("type") == "technical_question" and out.get("has_answer") is True and score >= 60:
        return "faq"
    return "newsletter_only"


def _post(url: str, payload: dict, headers: dict, retries: int = 3) -> dict:
    data = json.dumps(payload).encode()
    for attempt in range(retries + 1):
        req = request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
        try:
            with request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read())
        except error.HTTPError as exc:
            if exc.code in (429, 500, 503) and attempt < retries:
                wait = 15 * (attempt + 1)
                print(f"  HTTP {exc.code}: limite ou instabilidade; aguardando {wait}s...")
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {exc.code}: {exc.read().decode(errors='replace')[:300]}") from None
    raise RuntimeError("sem resposta")


def gemini_temperature(model: str) -> float:
    """O guia do Gemini 3 recomenda manter a temperatura padrão (1.0): abaixo disso o modelo pode entrar em loop."""
    if os.getenv("LLM_TEMPERATURE"):
        return float(os.environ["LLM_TEMPERATURE"])
    return 1.0 if model.startswith("gemini-3") else 0.0


def call_gemini(system: str, user: str) -> str:
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": gemini_temperature(model), "responseMimeType": "application/json"},
    }
    data = _post(url, payload, {"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"resposta sem candidatos: {json.dumps(data.get('promptFeedback', data))[:300]}")
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    if not text:
        raise RuntimeError(f"resposta vazia (finishReason={candidates[0].get('finishReason')})")
    return text


def parse_json(text: str) -> dict:
    """Aceita a resposta mesmo se o modelo embrulhar o JSON em ```json ... ```."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    return json.loads(text)


def call_groq(system: str, user: str) -> str:
    payload = {
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0")),
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }
    data = _post("https://api.groq.com/openai/v1/chat/completions", payload,
                 {"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"})
    return data["choices"][0]["message"]["content"]


def check(output: dict, expected: dict) -> tuple[list[str], list[str]]:
    """Retorna (erros, avisos). Erro reprova o caso; aviso só informa."""
    errors, warnings = [], []
    missing = REQUIRED - output.keys()
    if missing:
        errors.append(f"campos ausentes: {sorted(missing)}")
    for field, allowed in ENUMS.items():
        if field in output and output[field] not in allowed:
            errors.append(f"{field} fora do enum: {output[field]!r}")
    score = output.get("relevance_score", -1)
    if not isinstance(score, int) or not 0 <= score <= 100:
        errors.append(f"relevance_score inválido: {score!r}")
        score = -1
    if not isinstance(output.get("topics"), list) or not 1 <= len(output.get("topics") or []) <= 3:
        errors.append("topics deve ter de 1 a 3 itens")
    if len(output.get("summary") or "") > 200:
        errors.append(f"summary com {len(output['summary'])} caracteres (máx. 200)")

    final_route = route_from_fields(output)
    if output.get("suggested_route") != final_route:
        warnings.append(f"modelo sugeriu {output.get('suggested_route')!r}, as regras dão {final_route!r} (o n8n corrige)")

    for field, value in expected.items():
        if field in SPECIAL_KEYS:
            continue
        got = final_route if field == "suggested_route" else output.get(field)
        if got != value:
            errors.append(f"{field}: esperado {value!r}, veio {got!r}")
    if "suggested_route_in" in expected and final_route not in expected["suggested_route_in"]:
        errors.append(f"suggested_route: esperado um de {expected['suggested_route_in']}, veio {final_route!r}")
    if "min_score" in expected and score < expected["min_score"]:
        errors.append(f"relevance_score {score} < {expected['min_score']}")
    if "max_score" in expected and score > expected["max_score"]:
        errors.append(f"relevance_score {score} > {expected['max_score']}")
    return errors, warnings


def fake_output(case: dict) -> dict:
    """Saída simulada a partir do esperado, só para validar o script (--dry-run)."""
    exp = case["expected"]
    route = exp.get("suggested_route", (exp.get("suggested_route_in") or ["discard"])[0])
    # campos coerentes com a rota esperada, para o recálculo das regras bater
    base = {"success_case": {"type": "job_achievement", "sentiment": "positive", "relevance_score": 85},
            "faq": {"type": "technical_question", "has_answer": True, "relevance_score": 65},
            "moderation": {"sentiment": "negative", "relevance_score": 45},
            "discard": {"type": "noise", "relevance_score": 10},
            "newsletter_only": {"relevance_score": 50}}[route]
    out = {"id": case["input"]["id"], "source": case["input"]["source"], "type": "debate", "sentiment": "neutral",
           "topic_category": "other", "topics": ["teste"], "original_language": "en", "has_answer": False,
           "summary": "dry-run", "justification": "dry-run", "suggested_route": route} | base
    out |= {k: v for k, v in exp.items() if k not in SPECIAL_KEYS}
    if "min_score" in exp:
        out["relevance_score"] = max(out["relevance_score"], exp["min_score"])
    if "max_score" in exp:
        out["relevance_score"] = min(out["relevance_score"], exp["max_score"])
    return out


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # acentos no terminal do Windows
    if load_dotenv:
        load_dotenv(ROOT / ".env")

    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["gemini", "groq"], default="gemini")
    parser.add_argument("--cases", nargs="+", type=Path, help="arquivos de casos (padrão: router_cases.json + router_cases_reais.json)")
    parser.add_argument("--only", help="roda só os casos cujo nome contém este texto")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--replay", type=Path, help="JSON com saídas já geradas ({'outputs': {caso: saída}})")
    parser.add_argument("--sleep", type=float, default=5.0, help="pausa entre chamadas (rate limit do free tier)")
    parser.add_argument("--tag", default="", help="rótulo no nome do arquivo de saída (ex.: reais)")
    args = parser.parse_args()

    system, version = load_system_prompt()
    cases = []
    for path in args.cases or [p for p in DEFAULT_CASES if p.exists()]:
        cases += json.loads(path.read_text(encoding="utf-8"))
    if args.only:
        cases = [c for c in cases if args.only in c["case"]]
    problems = invalid_inputs(cases)
    if problems:
        print("Casos fora do data/schemas/input_schema.json (corrija antes de rodar):")
        for problem in problems:
            print(f"  - {problem}")
        return 2
    replay = json.loads(args.replay.read_text(encoding="utf-8"))["outputs"] if args.replay else None
    key_name = "GEMINI_API_KEY" if args.provider == "gemini" else "GROQ_API_KEY"
    if not args.dry_run and replay is None and not os.getenv(key_name):
        print(f"Falta a chave {key_name}. Crie o arquivo .env na raiz do repositório com a linha:\n{key_name}=sua_chave_aqui")
        return 2
    call = call_gemini if args.provider == "gemini" else call_groq
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite") if args.provider == "gemini" else os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    mode = "dry-run" if args.dry_run else ("replay" if replay else f"{args.provider}/{model}")
    print(f"Router v{version} | modo: {mode} | {len(cases)} casos\n")

    passed, saved, results = 0, {}, {}
    for case in cases:
        if args.dry_run:
            output = fake_output(case)
        elif replay is not None:
            output = replay.get(case["case"], {})
        else:
            user = "Classifique a thread abaixo seguindo as instruções do sistema.\n\nTHREAD:\n" + json.dumps(case["input"], ensure_ascii=False)
            try:
                output = parse_json(call(system, user))
                call_error = None
            except Exception as exc:  # resposta inválida conta como falha
                output, call_error = {}, str(exc)
                print(f"  erro na chamada/JSON: {exc}")
            time.sleep(args.sleep)
        saved[case["case"]] = output
        errors, warnings = check(output, case["expected"])
        if not args.dry_run and replay is None:
            results[case["case"]] = {"ok": not errors, "errors": errors, "warnings": warnings}
            if call_error:
                results[case["case"]]["call_error"] = call_error
        passed += not errors
        status = "OK   " if not errors else "FALHA"
        print(f"[{status}] {case['case']}" + ("" if not errors else " -> " + "; ".join(errors)))
        for w in warnings:
            print(f"        aviso: {w}")

    rate = passed / len(cases) * 100 if cases else 0
    print(f"\nTaxa de acerto: {passed}/{len(cases)} ({rate:.0f}%)")

    if not args.dry_run and replay is None:
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M")
        tag = f"_{args.tag}" if args.tag else ""
        out_file = OUTPUTS_DIR / f"router_v{version}_{args.provider}{tag}_{stamp}.json"
        meta = {"prompt_version": version, "model": model, "accuracy": f"{passed}/{len(cases)}",
                "cases_files": [str(p) for p in (args.cases or DEFAULT_CASES)], "ran_at": datetime.now().isoformat(timespec="seconds")}
        if args.provider == "gemini":
            meta["temperature"] = gemini_temperature(model)
        out_file.write_text(json.dumps(meta | {"results": results, "outputs": saved}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saídas salvas em {out_file.relative_to(ROOT)}")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
