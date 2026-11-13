import pytest
from unittest.mock import patch
from src.services.llm_providers import call_llm
from src.services.llm_service import call_gemini, call_groq, LLMResponse


def test_call_llm_raises_on_unknown_provider():
    with pytest.raises(ValueError, match="Provedor desconhecido"):
        call_llm(provider="openai", system="sys", user="usr")


@patch("src.config.GEMINI_API_KEY", "")
def test_call_llm_raises_when_api_key_missing():
    with pytest.raises(ValueError, match="Falta a chave de API"):
        call_llm(provider="gemini", system="sys", user="usr")


@patch("src.services.llm_service.http_post")
def test_call_gemini_success(mock_http_post):
    mock_http_post.return_value = {
        "candidates": [{
            "content": {"parts": [{"text": '{"result": "ok"}'}]}
        }],
        "usageMetadata": {
            "promptTokenCount": 10,
            "candidatesTokenCount": 5,
            "totalTokenCount": 15
        }
    }
    
    response = call_gemini(system="sys", user="usr", api_key="fake-key")
    
    assert isinstance(response, LLMResponse)
    assert response.text == '{"result": "ok"}'
    assert response.prompt_tokens == 10
    assert response.completion_tokens == 5
    assert response.total_tokens == 15


@patch("src.services.llm_service.http_post")
def test_call_groq_success(mock_http_post):
    mock_http_post.return_value = {
        "choices": [{
            "message": {"content": '{"result": "groq_ok"}'}
        }],
        "usage": {
            "prompt_tokens": 12,
            "completion_tokens": 8,
            "total_tokens": 20
        }
    }
    
    response = call_groq(system="sys", user="usr", api_key="fake-key")
    
    assert isinstance(response, LLMResponse)
    assert response.text == '{"result": "groq_ok"}'
    assert response.total_tokens == 20