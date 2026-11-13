from datetime import datetime

from src.validation.adapters_validator import (
    invalid_inputs,
    check_output,
    unknown_numbers,
)


def test_invalid_inputs_accepts_adapter_case_fixture():
    from src.utils.cases_loader import load_adapter_cases
    from src.config import ADAPTER_CASES

    data = load_adapter_cases(ADAPTER_CASES)

    assert invalid_inputs(data) == []


def test_invalid_inputs_rejects_unknown_job_item():
    data = {
        "items": [],
        "jobs": [{"nome": "job", "canal": "linkedin", "itens": ["missing"]}],
    }

    problems = invalid_inputs(data)

    assert "job[0]: item de origem não encontrado: 'missing'" in problems


def test_check_output_rejects_invalid_channel_output():
    errors, warnings = check_output(
        {
            "itens_de_origem": [],
            "output": {
                "target": "unknown",
                "title": "Título",
                "body": "Conteúdo",
                "potential_engagement": "low",
            },
        },
        {},
    )

    assert any("canal desconhecido" in error for error in errors)
    assert any("ainda não está no enum" in warning for warning in warnings)


def test_validate_requires_stackoverflow_credit():
    source = {
        "se-1": {
            "id": "se-1",
            "source": "stackoverflow",
            "interactions": [
                {"author": "perguntador", "content": "pergunta"},
                {
                    "author": "respondente",
                    "content": "resposta",
                    "raw_metadata": {"is_accepted": True},
                },
            ],
        }
    }

    errors, _ = check_output(
        {
            "itens_de_origem": ["se-1"],
            "output": {
                "target": "linkedin",
                "title": "Dica técnica",
                "body": "#" * 600,
                "potential_engagement": "medium",
            },
        },
        source,
    )

    assert any("linha de crédito" in error for error in errors)


def test_unknown_numbers_ignores_dotted_library_versions():
    body = "Compatível com v1.35.0 e versão 2.4.1."

    assert unknown_numbers(body, "") == []


def test_unknown_numbers_ignores_current_year_when_isolated():
    current_year = datetime.now().year
    body = f"Atualizado em {current_year}."

    assert unknown_numbers(body, "") == []


def test_unknown_numbers_does_not_ignore_unknown_factual_numbers():
    body = "O limite recomendado é 42 requisições."

    assert unknown_numbers(body, "") == ["42"]


def test_unknown_numbers_accepts_number_present_in_source():
    body = "Configure context_window=8000."
    source = "A resposta recomenda context_window=8000."

    assert unknown_numbers(body, source) == []
