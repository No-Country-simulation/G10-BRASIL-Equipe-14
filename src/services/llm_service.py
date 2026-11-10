from dataclasses import dataclass
from typing import Any

from src.config import (
    DEFAULT_TEMPERATURE,
    GEMINI_API_URL,
    GEMINI_TEMPERATURE,
    GROQ_API_URL,
    GROQ_MODEL,
)
from src.utils.http_client import http_post


@dataclass(frozen=True)
class LLMResponse:
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


def _require_api_key(api_key: str) -> str:
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("A API Key do provedor não foi configurada.")

    return api_key.strip()


def _token_count(value: Any) -> int:
    return value if isinstance(value, int) and value >= 0 else 0


def _build_response(
    text: str,
    prompt_tokens: Any,
    completion_tokens: Any,
    total_tokens: Any,
) -> LLMResponse:
    if not isinstance(text, str) or not text:
        raise RuntimeError("Resposta vazia do provedor.")

    prompt = _token_count(prompt_tokens)
    completion = _token_count(completion_tokens)
    total = _token_count(total_tokens) or prompt + completion

    return LLMResponse(
        text=text,
        prompt_tokens=prompt,
        completion_tokens=completion,
        total_tokens=total,
    )


def call_gemini(
    system: str,
    user: str,
    api_key: str,
) -> LLMResponse:
    api_key = _require_api_key(api_key)

    payload = {
        "system_instruction": {
            "parts": [{"text": system}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user}],
            }
        ],
        "generationConfig": {
            "temperature": GEMINI_TEMPERATURE,
            "responseMimeType": "application/json",
        },
    }

    data = http_post(
        GEMINI_API_URL,
        payload,
        {"x-goog-api-key": api_key},
    )

    candidates = data.get("candidates") or []

    if not candidates:
        raise RuntimeError("Resposta do Gemini sem candidatos.")

    parts = candidates[0].get("content", {}).get("parts", [])

    text = "".join(part.get("text", "") for part in parts if not part.get("thought"))

    if not text:
        raise RuntimeError("Resposta vazia do Gemini.")

    usage = data.get("usageMetadata") or {}

    return _build_response(
        text=text,
        prompt_tokens=usage.get("promptTokenCount"),
        completion_tokens=usage.get("candidatesTokenCount"),
        total_tokens=usage.get("totalTokenCount"),
    )


def call_groq(
    system: str,
    user: str,
    api_key: str,
) -> LLMResponse:
    api_key = _require_api_key(api_key)

    payload = {
        "model": GROQ_MODEL,
        "temperature": DEFAULT_TEMPERATURE,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": system,
            },
            {
                "role": "user",
                "content": user,
            },
        ],
    }

    data = http_post(
        GROQ_API_URL,
        payload,
        {"Authorization": f"Bearer {api_key}"},
    )

    choices = data.get("choices") or []

    if not choices:
        raise RuntimeError("Resposta da Groq sem escolhas válidas.")

    try:
        content = choices[0]["message"]["content"]
    except (KeyError, TypeError) as exc:
        raise RuntimeError("Resposta da Groq sem conteúdo de mensagem.") from exc

    if not isinstance(content, str) or not content:
        raise RuntimeError("Resposta vazia da Groq.")

    usage = data.get("usage") or {}

    return _build_response(
        text=content,
        prompt_tokens=usage.get("prompt_tokens"),
        completion_tokens=usage.get("completion_tokens"),
        total_tokens=usage.get("total_tokens"),
    )
