import os

from src.services.llm_service import call_gemini, call_groq

# Dicionário de Registro (Registry) de Provedores
LLM_PROVIDERS = {
    "gemini": {"func": call_gemini, "env_key": "GEMINI_API_KEY"},
    "groq": {"func": call_groq, "env_key": "GROQ_API_KEY"},
}


def call_llm(provider: str, system: str, user: str) -> str:
    if provider not in LLM_PROVIDERS:
        raise ValueError(
            f"Provedor desconhecido: '{provider}'. Opções: {list(LLM_PROVIDERS.keys())}"
        )

    config = LLM_PROVIDERS[provider]
    api_key = os.environ.get(config["env_key"])

    if not api_key:
        raise ValueError(
            f"Falta a chave de API. Configure a variável de ambiente: {config['env_key']}"
        )

    return config["func"](system, user, api_key)
