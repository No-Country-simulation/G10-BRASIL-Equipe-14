import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.pipeline.adapters_setup import load_and_filter_cases, prepare_execution


def test_load_and_filter_cases_raises_when_file_not_found(tmp_path: Path):
    non_existent = tmp_path / "missing.json"
    with pytest.raises(ValueError, match="Arquivo de casos não encontrado"):
        load_and_filter_cases(non_existent, only=None)


@patch("src.pipeline.adapters_setup.load_adapter_cases")
@patch("src.pipeline.adapters_setup.invalid_inputs", return_value=[])
def test_load_and_filter_cases_success(mock_invalid, mock_load_cases, tmp_path: Path):
    dummy_file = tmp_path / "cases.json"
    dummy_file.write_text("{}", encoding="utf-8")

    mock_load_cases.return_value = {
        "items": [{"id": "item_1"}],
        "jobs": [{"nome": "job_a", "canal": "linkedin"}],
        "reference_period_newsletter": "2026-W01",
        "router_run": {"version": 1},
    }

    jobs, items, period, router_run = load_and_filter_cases(
        dummy_file, only=None)

    assert len(jobs) == 1
    assert jobs[0]["nome"] == "job_a"
    assert "item_1" in items
    assert period == "2026-W01"
    assert router_run["version"] == 1


@patch("src.pipeline.adapters_setup.load_adapter_cases")
@patch("src.pipeline.adapters_setup.invalid_inputs", return_value=["erro de schema"])
def test_load_and_filter_cases_raises_on_invalid_inputs(
    mock_invalid, mock_load_cases, tmp_path: Path
):
    dummy_file = tmp_path / "cases.json"
    dummy_file.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="Casos de adapters inválidos"):
        load_and_filter_cases(dummy_file, only=None)


@patch("src.pipeline.adapters_setup.load_and_filter_cases")
@patch("src.pipeline.adapters_setup.provider_config")
@patch("src.pipeline.adapters_setup.load_adapter_base_prompt")
def test_prepare_execution_dry_run(
    mock_load_prompt, mock_provider_config, mock_load_cases, tmp_path: Path
):
    mock_load_cases.return_value = (
        [{"nome": "job_a", "canal": "linkedin", "itens": ["item_1"]}],
        {"item_1": {}},
        None,
        {},
    )
    mock_provider_config.return_value = (
        "fake_key",
        "gemini-3.5-flash-lite",
        0.1,
        "GEMINI_API_KEY",
    )

    args = MagicMock()
    args.cases = tmp_path / "cases.json"
    args.only = None
    args.dry_run = True
    args.provider = "gemini"

    context = prepare_execution(args)

    assert context.provider == "gemini"
    assert context.model == "gemini-3.5-flash-lite"
    assert context.temperature == 0.1
    assert len(context.jobs) == 1
    assert "dry-run" in context.header
