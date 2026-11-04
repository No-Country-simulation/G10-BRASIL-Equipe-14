from src.validation.rules_validator import route_from_fields, check_output


def test_route_from_fields_noise():
    output = {"type": "noise", "relevance_score": 50, "sentiment": "neutral"}
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
        "justification": "Justificativa válida.",
        "relevance_score": 75,
        "suggested_route": "faq",
    }
    expected = {"suggested_route": "faq", "min_score": 60}

    errors, warnings = check_output(output, expected)
    assert len(errors) == 0


def test_check_output_missing_fields():
    output = {
        "id": "123",
        # Faltam vários campos obrigatórios
        "relevance_score": 50,
    }
    expected = {"suggested_route": "discard"}

    errors, warnings = check_output(output, expected)
    assert len(errors) > 0
    assert any("campos ausentes" in err for err in errors)
