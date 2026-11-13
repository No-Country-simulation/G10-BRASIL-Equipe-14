from src.config import (
    DEFAULT_TEMPERATURE,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GROQ_API_KEY,
    GROQ_MODEL,
)


def provider_config(
    provider: str,
) -> tuple[str, str, float, str]:
    configurations = {
        "gemini": (
            GEMINI_API_KEY,
            GEMINI_MODEL,
            GEMINI_TEMPERATURE,
            "GEMINI_API_KEY",
        ),
        "groq": (
            GROQ_API_KEY,
            GROQ_MODEL,
            DEFAULT_TEMPERATURE,
            "GROQ_API_KEY",
        ),
    }

    try:
        return configurations[provider]
    except KeyError as exc:
        raise ValueError(f"Provedor não suportado: {provider}") from exc
