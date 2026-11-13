import pytest
from src.utils.json_parser import parse_llm_json, remove_code_fence


def test_remove_code_fence_with_json_tag():
    text = '```json\n{"chave": "valor"}\n```'
    assert remove_code_fence(text) == '{"chave": "valor"}'


def test_remove_code_fence_without_tag():
    text = '```\n{"chave": "valor"}\n```'
    assert remove_code_fence(text) == '{"chave": "valor"}'


def test_remove_code_fence_plain_text():
    text = '{"chave": "valor"}'
    assert remove_code_fence(text) == '{"chave": "valor"}'


def test_parse_llm_json_success():
    text = '```json\n{"ok": true}\n```'
    result = parse_llm_json(text)
    assert result == {"ok": True}


def test_parse_llm_json_raises_on_invalid_json():
    with pytest.raises(ValueError, match="Falha ao decodificar JSON"):
        parse_llm_json('{"chave": malformado}')


def test_parse_llm_json_raises_on_non_dict():
    with pytest.raises(ValueError, match="deve ser um objeto JSON"):
        parse_llm_json("[1, 2, 3]")
