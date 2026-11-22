from __future__ import annotations

from src.pipeline.router_processor import CaseResult
from src.pipeline.router_report import (
    summarize_tokens,
    _dataset_label,
    _source_label,
)


def test_summarize_tokens():
    """Valida o somatório de tokens de múltiplos resultados de casos[cite: 13]."""
    res1 = CaseResult(output={}, errors=[], warnings=[], token_usage={
                      "prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15})
    res2 = CaseResult(output={}, errors=[], warnings=[], token_usage={
                      "prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30})
    res3 = CaseResult(output={}, errors=[], warnings=[], token_usage=None)

    results = {"c1": res1, "c2": res2, "c3": res3}
    summary = summarize_tokens(results)

    assert summary == {"prompt_tokens": 30,
                       "completion_tokens": 15, "total_tokens": 45}


def test_dataset_label():
    """Valida a rotulagem correta dos conjuntos de dados baseados no nome do caso[cite: 13]."""
    assert _dataset_label("real_stackoverflow_01") == "Casos Reais"
    assert _dataset_label("sintetico_mastodon_02") == "Casos Sintéticos"


def test_source_label():
    """Valida a tradução de rótulos de fontes de dados[cite: 13]."""
    assert _source_label("stackoverflow") == "Stack Overflow/Stack Exchange"
    assert _source_label("mastodon") == "Mastodon"
    assert _source_label("hackernews") == "Hacker News"
    assert _source_label("outro_canal") == "outro_canal"
