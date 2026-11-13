from collections.abc import Callable
from typing import Any

import src.config as config
from src.services.llm_service import call_gemini, call_groq, LLMResponse

ProviderFunction = Callable[[str, str, str], LLMResponse]


def _get_providers() -> dict[str, dict[str, Any]]:
    return {
        "gemini": {
            "func": call_gemini,
            "api_key": config.GEMINI_API_KEY,
        },
        "groq": {
            "func": call_groq,
            "api_key": config.GROQ_API_KEY,
        },
    }


def call_llm(
    provider: str,
    system: str,
    user: str,
) -> LLMResponse:
    providers = _get_providers()
    if provider not in providers:
        raise ValueError(
            f"Provedor desconhecido: {provider!r}. " f"Opções: {', '.join(providers)}"
        )

    cfg = providers[provider]
    api_key = cfg["api_key"]
    function = cfg["func"]

    if not isinstance(api_key, str) or not api_key:
        raise ValueError(
            f"Falta a chave de API para o provedor {provider!r}. "
            "Configure a chave no arquivo .env."
        )

    if not callable(function):
        raise RuntimeError(f"Função não configurada para o provedor {provider!r}.")

    provider_function: ProviderFunction = function

    return provider_function(system, user, api_key)
