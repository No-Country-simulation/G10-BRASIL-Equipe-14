from pathlib import Path
from src.pipeline.adapters_processor import CaseResult
from src.pipeline.adapters_report import (
    summarize_tokens,
    save_report,
    save_csv_report,
)


def test_summarize_tokens_calculates_totals():
    results = {
        "job_1": CaseResult(
            output={},
            errors=[],
            warnings=[],
            token_usage={
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
        ),
        "job_2": CaseResult(
            output={},
            errors=[],
            warnings=[],
            token_usage={
                "prompt_tokens": 200,
                "completion_tokens": 100,
                "total_tokens": 300,
            },
        ),
    }

    summary = summarize_tokens(results)

    assert summary is not None
    assert summary["prompt_tokens"] == 300
    assert summary["completion_tokens"] == 150
    assert summary["total_tokens"] == 450


def test_summarize_tokens_returns_none_when_no_usage():
    results = {
        "job_1": CaseResult(output={}, errors=[], warnings=[], token_usage=None),
    }
    assert summarize_tokens(results) is None


def test_save_report_creates_json_file(tmp_path: Path):
    results = {
        "job_1": CaseResult(
            output={"target": "linkedin", "title": "t", "body": "b"},
            errors=[],
            warnings=[],
            token_usage={
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
            duration_seconds=1.2,
        )
    }

    output_file = save_report(
        output_dir=tmp_path,
        project_root=tmp_path,
        prompt_versions={"social": "1.0", "newsletter_faq": "1.0"},
        router_run={"run": "ok"},
        provider="gemini",
        model="gemini-3.5-flash-lite",
        temperature=0.1,
        case_path=tmp_path / "cases.json",
        jobs=[{"nome": "job_1", "canal": "linkedin"}],
        results=results,
        total_duration=1.2,
        reference_period=None,
    )

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "job_1" in content
    assert "gemini-3.5-flash-lite" in content


def test_save_csv_report_creates_csv_file(tmp_path: Path):
    results = {
        "job_1": CaseResult(
            output={},
            errors=[],
            warnings=[],
            token_usage={
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
            duration_seconds=1.5,
        )
    }

    output_file = save_csv_report(
        output_dir=tmp_path,
        project_root=tmp_path,
        prompt_versions={"social": "1.0", "newsletter_faq": "1.0"},
        provider="gemini",
        jobs=[{"nome": "job_1", "canal": "linkedin", "itens": ["item_1"]}],
        results=results,
        timestamp="20261112-1200",
    )

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8-sig")
    assert "Caso de Teste" in content
    assert "CT01" in content
    assert "job_1" in content
