import pytest
from unittest.mock import patch
from src.pipeline.adapters_loader import load_adapter_base_prompt, get_system_prompt


@patch("src.pipeline.adapters_loader.load_markdown_prompt")
def test_load_adapter_base_prompt_faq_does_not_load_common_rules(mock_load_markdown):
    mock_load_markdown.return_value = "# Prompt FAQ"

    prompt = load_adapter_base_prompt("faq")

    # FAQ não deve carregar as common_rules
    assert prompt == "# Prompt FAQ"
    mock_load_markdown.assert_called_once()


@patch("src.pipeline.adapters_loader.load_markdown_prompt")
def test_load_adapter_base_prompt_linkedin_loads_common_rules(mock_load_markdown):
    mock_load_markdown.side_effect = ["# Regras Comuns", "# Prompt LinkedIn"]

    prompt = load_adapter_base_prompt("linkedin")

    # Canais padrão devem mesclar common_rules e o prompt do canal
    assert "# Regras Comuns" in prompt
    assert "# Prompt LinkedIn" in prompt
    assert mock_load_markdown.call_count == 2


def test_load_adapter_base_prompt_invalid_channel_raises_error():
    with pytest.raises(ValueError, match="Canal desconhecido"):
        load_adapter_base_prompt("canal_inexistente")


@patch("src.pipeline.adapters_loader.load_adapter_base_prompt")
def test_get_system_prompt_delegates_correctly(mock_load_base):
    mock_load_base.return_value = "System prompt mockado"

    result = get_system_prompt("instagram")

    assert result == "System prompt mockado"
    mock_load_base.assert_called_once_with("instagram")
