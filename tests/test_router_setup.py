from __future__ import annotations

from pathlib import Path
import pytest
from src.pipeline.router_setup import (
    build_parser,
    load_and_filter_cases,
    load_replay_file,
    execution_mode,
)


def test_build_parser():
    """Valida se o parser cria os argumentos esperados do router[cite: 11]."""
    parser = build_parser()
    args = parser.parse_args(
        ["--provider", "groq", "--tag", "v1", "--dry-run"])

    assert args.provider == "groq"
    assert args.tag == "v1"
    assert args.dry_run is True


def test_load_and_filter_cases_missing_paths():
    """Valida erro quando arquivos de casos não existem[cite: 11]."""
    fake_path = Path("non_existent_cases.json")
    with pytest.raises(ValueError, match="Arquivos de casos não encontrados"):
        load_and_filter_cases([fake_path], only=None)


def test_load_replay_file_none():
    """Valida que retorna None se o caminho do replay for None[cite: 11]."""
    assert load_replay_file(None) is None


def test_execution_mode():
    """Valida a resolução correta da string de modo de execução[cite: 11]."""
    assert execution_mode(dry_run=True, replay=None,
                          provider="gemini", model="m1") == "dry-run"
    assert execution_mode(dry_run=False, replay={
                          "a": 1}, provider="gemini", model="m1") == "replay"
    assert execution_mode(dry_run=False, replay=None,
                          provider="groq", model="llama") == "groq/llama"
