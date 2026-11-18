from unittest.mock import patch, MagicMock
from src.pipeline.adapters_processor import execute_case, CaseResult


def test_execute_case_dry_run_returns_mock_output():
    job = {"canal": "linkedin", "nome": "job_teste", "itens": ["item_1"]}

    result = execute_case(
        job=job,
        items=[],
        sources={},
        system="system prompt",
        reference_period="2026-W01",
        provider="gemini",
        dry_run=True,
    )

    assert result.passed is True
    assert result.output["title"] == "dry-run"
    assert result.output["target"] == "linkedin"


@patch("src.pipeline.adapters_processor.call_llm")
@patch("src.pipeline.adapters_processor.check_output", return_value=([], []))
def test_execute_case_successful_first_try(mock_check_output, mock_call_llm):
    # Mock da resposta bem-sucedida da LLM
    mock_response = MagicMock()
    mock_response.text = (
        '{"target": "linkedin", "title": "Título válido", "body": "Corpo válido"}'
    )
    mock_response.prompt_tokens = 100
    mock_response.completion_tokens = 50
    mock_response.total_tokens = 150
    mock_call_llm.return_value = mock_response

    job = {"canal": "linkedin", "nome": "job_teste", "itens": ["item_1"]}
    item = {
        "id": "item_1",
        "input": {"id": "item_1", "interactions": []},
        "classification": {},
    }

    result = execute_case(
        job=job,
        items=[item],
        sources={},
        system="system prompt",
        reference_period=None,
        provider="gemini",
        dry_run=False,
    )

    assert result.passed is True
    assert result.retry_used is False
    assert result.token_usage["total_tokens"] == 150
    assert mock_call_llm.call_count == 1
