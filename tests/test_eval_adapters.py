from unittest.mock import patch, MagicMock
from pathlib import Path
from src.pipeline.eval_adapters import main


@patch("src.pipeline.eval_adapters.save_csv_report")
@patch("src.pipeline.eval_adapters.save_report")
@patch("src.pipeline.eval_adapters.execute_case")
@patch("src.pipeline.eval_adapters.load_adapter_base_prompt")
@patch("src.pipeline.eval_adapters.load_sources")
@patch("src.pipeline.eval_adapters.prepare_execution")
@patch("src.pipeline.eval_adapters.build_parser")
def test_main_execution_success(
    mock_build_parser,
    mock_prepare_execution,
    mock_execute_case,
    mock_save_report,
    mock_save_csv,
    tmp_path: Path,
):
    # Mock do argumento de linha de comando
    mock_args = MagicMock()
    mock_args.dry_run = False
    mock_args.sleep = 0.0
    mock_parser = MagicMock()
    mock_parser.parse_args.return_value = mock_args
    mock_build_parser.return_value = mock_parser

    # Mock do contexto de execução
    mock_context = MagicMock()
    mock_context.header = "Header Test"
    mock_context.jobs = [
        {"nome": "job_1", "canal": "linkedin", "itens": ["item_1"]}]
    mock_context.items = {"item_1": {}}
    mock_context.reference_period = None
    mock_context.provider = "gemini"
    mock_context.model = "gemini-3.5-flash-lite"
    mock_context.temperature = 0.1
    mock_context.case_path = tmp_path / "cases.json"
    mock_context.output_dir = tmp_path
    mock_context.project_root = tmp_path
    mock_context.prompt_versions = {"social": "1.0", "newsletter_faq": "1.0"}
    mock_context.router_run = {}
    mock_prepare_execution.return_value = mock_context

    # Mock de resultado de sucesso do caso
    mock_case_result = MagicMock()
    mock_case_result.passed = True
    mock_case_result.duration_seconds = 1.0
    mock_case_result.warnings = []
    mock_execute_case.return_value = mock_case_result

    # Mock de salvamento de relatório
    mock_report_path = tmp_path / "adapters_gemini_20261112-1200.json"
    mock_report_path.write_text("{}", encoding="utf-8")
    mock_save_report.return_value = mock_report_path

    exit_code = main()

    assert exit_code == 0
    mock_execute_case.assert_called_once()
    mock_save_report.assert_called_once()
    mock_save_csv.assert_called_once()
