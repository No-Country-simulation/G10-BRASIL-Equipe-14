import json
from src.config import (
    INPUT_SCHEMA_PATH,
    PROMPT_ENUMS,
    REQUIRED_FIELDS,
    SPECIAL_KEYS,
)


def invalid_inputs(cases: list[dict]) -> list[str]:
    if not INPUT_SCHEMA_PATH.exists():
        return []
    try:
        import jsonschema
    except ImportError:
        return []
    schema = json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    problems = []
    for case in cases:
        for err in validator.iter_errors(case["input"]):
            problems.append(f"{case['case']}: {err.message}")
    return problems


def route_from_fields(out: dict) -> str:
    score = out.get("relevance_score", -1)
    if out.get("type") == "noise":
        return "discard"
    if out.get("sentiment") == "negative":
        return "moderation"
    if score < 40:
        return "discard"
    if (
        out.get("type") in ("job_achievement", "testimonial")
        and out.get("sentiment") == "positive"
        and score >= 80
    ):
        return "success_case"
    if (
        out.get("type") == "technical_question"
        and out.get("has_answer") is True
        and score >= 60
    ):
        return "faq"
    return "newsletter_only"


def check_output(output: dict, expected: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []

    # Validação de campos obrigatórios
    missing = REQUIRED_FIELDS - output.keys()
    if missing:
        errors.append(f"campos ausentes: {sorted(missing)}")

    # Validação de enums permitidos
    for field, allowed in PROMPT_ENUMS.items():
        if field in output and output[field] not in allowed:
            errors.append(f"{field} fora do enum: {output[field]!r}")

    # Validação do score
    score = output.get("relevance_score", -1)
    if not isinstance(score, (int, float)) or not 0 <= score <= 100:
        errors.append(f"relevance_score inválido: {score!r}")
        score = -1

    # Validação de tópicos
    if (
        not isinstance(output.get("topics"), list)
        or not 1 <= len(output.get("topics") or []) <= 3
    ):
        errors.append("topics deve ter de 1 a 3 itens")

    # Validação do tamanho do resumo
    if len(output.get("summary") or "") > 200:
        errors.append(f"summary com {len(output['summary'])} caracteres (máx. 200)")

    # Confere se a rota calculada bate com a sugerida
    final_route = route_from_fields(output)
    if output.get("suggested_route") != final_route:
        warnings.append(
            f"modelo sugeriu {output.get('suggested_route')!r}, as regras dão {final_route!r} (o n8n corrige)"
        )

    # Validações contra o expected do caso de teste
    for field, value in expected.items():
        if field in SPECIAL_KEYS:
            continue
        got = final_route if field == "suggested_route" else output.get(field)
        if got != value:
            errors.append(f"{field}: esperado {value!r}, veio {got!r}")

    if (
        "suggested_route_in" in expected
        and final_route not in expected["suggested_route_in"]
    ):
        errors.append(
            f"suggested_route: esperado um de {expected['suggested_route_in']}, veio {final_route!r}"
        )

    if "min_score" in expected and score < expected["min_score"]:
        errors.append(f"relevance_score {score} < {expected['min_score']}")

    if "max_score" in expected and score > expected["max_score"]:
        errors.append(f"relevance_score {score} > {expected['max_score']}")

    return errors, warnings


def fake_output(case: dict) -> dict:
    exp = case["expected"]
    route = exp.get(
        "suggested_route", (exp.get("suggested_route_in") or ["discard"])[0]
    )
    base = {
        "success_case": {
            "type": "job_achievement",
            "sentiment": "positive",
            "relevance_score": 85,
        },
        "faq": {
            "type": "technical_question",
            "has_answer": True,
            "relevance_score": 65,
        },
        "moderation": {"sentiment": "negative", "relevance_score": 45},
        "discard": {"type": "noise", "relevance_score": 10},
        "newsletter_only": {"relevance_score": 50},
    }[route]
    out = {
        "id": case["input"]["id"],
        "source": case["input"]["source"],
        "type": "debate",
        "sentiment": "neutral",
        "topic_category": "other",
        "topics": ["teste"],
        "original_language": "en",
        "has_answer": False,
        "summary": "dry-run",
        "justification": "dry-run",
        "suggested_route": route,
    } | base
    out |= {k: v for k, v in exp.items() if k not in SPECIAL_KEYS}
    if "min_score" in exp:
        out["relevance_score"] = max(out["relevance_score"], exp["min_score"])
    if "max_score" in exp:
        out["relevance_score"] = min(out["relevance_score"], exp["max_score"])
    return out
