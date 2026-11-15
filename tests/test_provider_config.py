import pytest
from src.utils.provider_config import provider_config


def test_provider_config_gemini():
    api_key, model, temp, key_name = provider_config("gemini")
    assert key_name == "GEMINI_API_KEY"
    assert isinstance(temp, float)


def test_provider_config_groq():
    api_key, model, temp, key_name = provider_config("groq")
    assert key_name == "GROQ_API_KEY"


def test_provider_config_raises_on_unknown():
    with pytest.raises(ValueError, match="Provedor não suportado"):
        provider_config("openai")
