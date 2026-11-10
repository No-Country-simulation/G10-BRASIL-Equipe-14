from __future__ import annotations

import json
from typing import Any

from src.config import (
    INPUT_SCHEMA_PATH,
    PROMPT_ENUMS,
    REQUIRED_FIELDS,
    SPECIAL_KEYS,
    SECURITY_MARKERS,
)


def invalid_inputs(cases: list[dict[str, Any]]) -> list[str]:
    if not INPUT_SCHEMA_PATH.exists():
        return [f"schema não encontrado: {INPUT_SCHEMA_PATH}"]

    try:
        import jsonschema
    except ImportError:
        return ["dependência jsonschema não instalada"]

    try:
        schema = json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"não foi possível carregar o schema: {exc}"]

    validator = jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )

    problems: list[str] = []

    for case in cases:
        case_name = case.get("case", "<caso sem nome>")

        if not isinstance(case.get("input"), dict):
            problems.append(f"{case_name}: campo 'input' deve ser um objeto")
            continue

        for error in validator.iter_errors(case["input"]):
            location = "/".join(str(part) for part in error.path)
            suffix = f" em {location}" if location else ""
            problems.append(f"{case_name}: {error.message}{suffix}")

    return problems


def route_from_fields(output: dict[str, Any]) -> str:
    score = output.get("relevance_score")

    if not isinstance(score, (int, float)) or isinstance(score, bool):
        score = -1

    if output.get("type") == "noise":
        return "discard"

    if output.get("sentiment") == "negative":
        return "moderation"

    if score < 40:
        return "discard"

    if (
        output.get("type") in ("job_achievement", "testimonial")
        and output.get("sentiment") == "positive"
        and score >= 80
    ):
        return "success_case"

    if (
        output.get("type") == "technical_question"
        and output.get("has_answer") is True
        and score >= 60
    ):
        return "faq"

    return "newsletter_only"


def expected_has_answer(case: dict[str, Any]) -> bool:
    input_data = case.get("input", {})
    interactions = input_data.get("interactions", [])

    if not isinstance(interactions, list):
        return False

    return any(
        isinstance(interaction, dict)
        and isinstance(interaction.get("raw_metadata"), dict)
        and interaction["raw_metadata"].get("is_accepted") is True
        for interaction in interactions[1:]
    )


def expected_security_case(case: dict[str, Any]) -> bool:
    input_data = case.get("input", {})
    interactions = input_data.get("interactions", [])

    if not isinstance(interactions, list) or not interactions:
        return False

    original = interactions[0]

    if not isinstance(original, dict):
        return False

    text = " ".join(
        str(original.get(field, "")) for field in ("title", "content")
    ).lower()

    return any(marker in text for marker in SECURITY_MARKERS)


def check_output(
    output: Any,
    expected: dict[str, Any],
    case: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(output, dict):
        return ["saída deve ser um objeto JSON"], warnings

    missing = REQUIRED_FIELDS - output.keys()

    if missing:
        errors.append(f"campos ausentes: {sorted(missing)}")

    extra_fields = set(output) - REQUIRED_FIELDS

    if extra_fields:
        errors.append(f"Campos adicionais não permitidos: {sorted(extra_fields)}")

    if case is not None and "has_answer" in output:
        expected_answer = expected_has_answer(case)

        if output["has_answer"] is not expected_answer:
            errors.append(
                "has_answer: esperado "
                f"{expected_answer!r} conforme raw_metadata.is_accepted"
            )
    is_security_case = case is not None and expected_security_case(case)

    if is_security_case:
        if output.get("type") != "noise":
            errors.append(
                "type deve ser 'noise' quando houver exposição " "de PII ou credencial"
            )

        score = output.get("relevance_score")

        if (
            not isinstance(score, (int, float))
            or isinstance(score, bool)
            or not 0 <= score <= 19
        ):
            errors.append(
                "relevance_score deve estar entre 0 e 19 " "para casos de segurança"
            )

        if output.get("suggested_route") not in {
            "moderation",
            "discard",
        }:
            errors.append(
                "suggested_route deve ser 'moderation' "
                "ou 'discard' para casos de segurança"
            )

    for field, allowed in PROMPT_ENUMS.items():
        if field in output and output[field] not in allowed:
            errors.append(f"{field} fora do enum: {output[field]!r}")

    score = output.get("relevance_score")

    if (
        not isinstance(score, (int, float))
        or isinstance(score, bool)
        or not 0 <= score <= 100
    ):
        errors.append(f"relevance_score inválido: {score!r}")
        normalized_score = -1
    else:
        normalized_score = score

    topics = output.get("topics")

    if (
        not isinstance(topics, list)
        or not 1 <= len(topics) <= 3
        or not all(isinstance(topic, str) for topic in topics)
    ):
        errors.append("topics deve ter de 1 a 3 itens textuais")

    summary = output.get("summary")

    if not isinstance(summary, str):
        errors.append("summary deve ser uma string")
    elif len(summary) > 200:
        errors.append(f"summary com {len(summary)} caracteres (máx. 200)")

    final_route = route_from_fields(output)

    if output.get("suggested_route") != final_route:
        warnings.append(
            f"modelo sugeriu {output.get('suggested_route')!r}, "
            f"as regras dão {final_route!r} (o n8n corrige)"
        )

    for field, value in expected.items():
        if field in SPECIAL_KEYS:
            continue

        got = final_route if field == "suggested_route" else output.get(field)

        if got != value:
            errors.append(f"{field}: esperado {value!r}, veio {got!r}")

    if "suggested_route_in" in expected:
        if final_route not in expected["suggested_route_in"]:
            errors.append(
                "suggested_route: esperado um de "
                f"{expected['suggested_route_in']}, veio {final_route!r}"
            )

    if "min_score" in expected and normalized_score < expected["min_score"]:
        errors.append(f"relevance_score {normalized_score} < {expected['min_score']}")

    if "max_score" in expected and normalized_score > expected["max_score"]:
        errors.append(f"relevance_score {normalized_score} > {expected['max_score']}")

    return errors, warnings


def fake_output(case: dict[str, Any]) -> dict[str, Any]:
    expected = case["expected"]

    route = expected.get(
        "suggested_route",
        (expected.get("suggested_route_in") or ["discard"])[0],
    )

    base: dict[str, Any] = {
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
        "moderation": {
            "sentiment": "negative",
            "relevance_score": 45,
        },
        "discard": {
            "type": "noise",
            "relevance_score": 10,
        },
        "newsletter_only": {
            "relevance_score": 50,
        },
    }[route]

    output: dict[str, Any] = {
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
    }

    output.update(base)

    output.update(
        {key: value for key, value in expected.items() if key not in SPECIAL_KEYS}
    )

    if "min_score" in expected:
        output["relevance_score"] = max(
            output["relevance_score"],
            expected["min_score"],
        )

    if "max_score" in expected:
        output["relevance_score"] = min(
            output["relevance_score"],
            expected["max_score"],
        )

    return output
