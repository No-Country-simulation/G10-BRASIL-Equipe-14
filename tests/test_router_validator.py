from src.validation.router_validator import (
    check_output,
    expected_has_answer,
    route_from_fields,
)


def test_route_from_fields_noise():
    output = {
        "type": "noise",
        "relevance_score": 50,
        "sentiment": "neutral",
    }

    assert route_from_fields(output) == "discard"


def test_route_from_fields_moderation():
    output = {
        "type": "technical_question",
        "relevance_score": 70,
        "sentiment": "negative",
    }

    assert route_from_fields(output) == "moderation"


def test_route_from_fields_low_score():
    output = {
        "type": "technical_question",
        "relevance_score": 30,
        "sentiment": "neutral",
    }

    assert route_from_fields(output) == "discard"


def test_route_from_fields_success_case():
    output = {
        "type": "job_achievement",
        "sentiment": "positive",
        "relevance_score": 85,
    }

    assert route_from_fields(output) == "success_case"


def test_route_from_fields_faq():
    output = {
        "type": "technical_question",
        "has_answer": True,
        "relevance_score": 65,
        "sentiment": "neutral",
    }

    assert route_from_fields(output) == "faq"


def test_route_from_fields_invalid_score_discards():
    output = {
        "type": "technical_question",
        "sentiment": "neutral",
        "relevance_score": "invalid",
    }

    assert route_from_fields(output) == "discard"


def test_route_from_fields_boolean_score_discards():
    output = {
        "type": "technical_question",
        "sentiment": "neutral",
        "relevance_score": True,
    }

    assert route_from_fields(output) == "discard"


def test_check_output_valid():
    output = {
        "id": "123",
        "source": "github",
        "type": "technical_question",
        "sentiment": "neutral",
        "topic_category": "backend",
        "topics": ["python", "api"],
        "original_language": "en",
        "has_answer": True,
        "summary": "Resumo curto e objetivo da thread.",
        "justification": "Faixa 60-79: regra 5 (faq).",
        "relevance_score": 75,
        "suggested_route": "faq",
    }

    case = {
        "input": {
            "interactions": [
                {"content": "pergunta"},
                {
                    "content": "resposta aceita",
                    "raw_metadata": {"is_accepted": True},
                },
            ]
        },
    }

    expected = {
        "suggested_route": "faq",
        "min_score": 60,
    }

    errors, warnings = check_output(output, expected, case)

    assert errors == []
    assert warnings == []


def test_check_output_missing_fields():
    output = {
        "id": "123",
        "relevance_score": 50,
    }

    expected = {"suggested_route": "discard"}

    errors, warnings = check_output(output, expected)

    assert errors
    assert any("campos ausentes" in error for error in errors)


def test_check_output_rejects_missing_has_answer_without_crashing():
    output = {
        "id": "123",
        "source": "github",
        "type": "technical_question",
        "sentiment": "neutral",
        "topic_category": "backend",
        "topics": ["python"],
        "original_language": "en",
        "summary": "Resumo.",
        "justification": "Justificativa.",
        "relevance_score": 50,
        "suggested_route": "newsletter_only",
    }

    case = {
        "input": {
            "interactions": [
                {"content": "pergunta"},
            ]
        },
    }

    errors, warnings = check_output(
        output,
        {},
        case,
    )

    assert any("campos ausentes" in error for error in errors)


def test_check_output_rejects_extra_fields():
    output = {
        "id": "123",
        "source": "github",
        "type": "technical_question",
        "sentiment": "neutral",
        "topic_category": "backend",
        "topics": ["python"],
        "original_language": "en",
        "has_answer": False,
        "summary": "Resumo.",
        "justification": "Justificativa.",
        "relevance_score": 50,
        "suggested_route": "newsletter_only",
        "unexpected": True,
    }

    errors, warnings = check_output(output, {}, None)

    assert any("Campos adicionais" in error for error in errors)


def test_check_output_rejects_non_object_output():
    errors, warnings = check_output([], {}, None)

    assert errors == ["saída deve ser um objeto JSON"]
    assert warnings == []


def test_expected_has_answer_requires_accepted_answer():
    case = {
        "input": {
            "interactions": [
                {"content": "pergunta"},
                {
                    "content": "resposta não aceita",
                    "raw_metadata": {"is_accepted": False},
                },
            ]
        }
    }

    assert expected_has_answer(case) is False


def test_expected_has_answer_is_true_for_accepted_answer():
    case = {
        "input": {
            "interactions": [
                {"content": "pergunta"},
                {
                    "content": "resposta aceita",
                    "raw_metadata": {"is_accepted": True},
                },
            ]
        }
    }

    assert expected_has_answer(case) is True


def test_expected_has_answer_ignores_first_interaction():
    case = {
        "input": {
            "interactions": [
                {
                    "content": "pergunta",
                    "raw_metadata": {"is_accepted": True},
                },
            ]
        }
    }

    assert expected_has_answer(case) is False


def test_check_output_rejects_technical_question_for_security_case():
    case = {
        "input": {
            "interactions": [
                {
                    "title": "Dados expostos",
                    "content": (
                        "Publiquei acidentalmente um CPF e uma API key "
                        "em um log público."
                    ),
                }
            ]
        }
    }

    output = {
        "id": "t15",
        "source": "hackernews",
        "type": "technical_question",
        "sentiment": "neutral",
        "topic_category": "dev_tools",
        "topics": ["segurança"],
        "original_language": "pt",
        "has_answer": False,
        "relevance_score": 25,
        "suggested_route": "newsletter_only",
        "summary": "Pergunta técnica sobre segurança.",
        "justification": "Faixa 20-39.",
    }

    errors, _ = check_output(output, {}, case)

    assert any("type deve ser 'noise'" in error for error in errors)
    assert any("entre 0 e 19" in error for error in errors)
    assert any("moderation" in error for error in errors)
