from collections.abc import Callable
from typing import Any

from src.config import GEMINI_API_KEY, GROQ_API_KEY
from src.services.llm_service import call_gemini, call_groq, LLMResponse

ProviderFunction = Callable[[str, str, str], LLMResponse]

LLM_PROVIDERS: dict[str, dict[str, Any]] = {
    "gemini": {
        "func": call_gemini,
        "api_key": GEMINI_API_KEY,
    },
    "groq": {
        "func": call_groq,
        "api_key": GROQ_API_KEY,
    },
}


def call_llm(
    provider: str,
    system: str,
    user: str,
) -> LLMResponse:
    if provider not in LLM_PROVIDERS:
        raise ValueError(
            f"Provedor desconhecido: {provider!r}. "
            f"Opções: {', '.join(LLM_PROVIDERS)}"
        )

    config = LLM_PROVIDERS[provider]
    api_key = config["api_key"]
    function = config["func"]

    if not isinstance(api_key, str) or not api_key:
        raise ValueError(
            f"Falta a chave de API para o provedor {provider!r}. "
            "Configure a chave no arquivo .env."
        )

    if not callable(function):
        raise RuntimeError(f"Função não configurada para o provedor {provider!r}.")

    provider_function: ProviderFunction = function

    return provider_function(system, user, api_key)
