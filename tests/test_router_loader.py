from __future__ import annotations

from unittest.mock import patch
from src.pipeline.router_loader import (
    load_prompt_files,
    load_router_base_prompt,
    load_router_few_shot_prompt,
)


@patch("src.pipeline.router_loader.load_markdown_prompt")
def test_load_prompt_files(mock_load_markdown):
    mock_load_markdown.side_effect = ["Conteúdo A", "Conteúdo B"]

    result = load_prompt_files("file1.md", "file2.md")

    assert result == "Conteúdo A\n\nConteúdo B"
    assert mock_load_markdown.call_count == 2


@patch("src.pipeline.router_loader.load_prompt_files")
def test_load_router_base_prompt(mock_load_prompt_files):
    mock_load_prompt_files.return_value = "prompt_base_unificado"

    result = load_router_base_prompt()

    assert result == "prompt_base_unificado"
    mock_load_prompt_files.assert_called_once_with(
        "system.md", "evaluation_rubric.md", "guardrails.md"
    )


@patch("src.pipeline.router_loader.load_prompt_files")
def test_load_router_few_shot_prompt(mock_load_prompt_files):
    mock_load_prompt_files.return_value = "few_shot_content"

    result = load_router_few_shot_prompt()

    assert result == "few_shot_content"
    mock_load_prompt_files.assert_called_once_with("few_shot_examples.md")