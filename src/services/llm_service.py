from src.utils.http_client import http_post
from src.config import (
    GEMINI_API_URL,
    GROQ_MODEL,
    GROQ_API_URL,
    DEFAULT_TEMPERATURE,
)


def call_gemini(system: str, user: str, api_key: str) -> str:
    url = GEMINI_API_URL

    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {
            "temperature": DEFAULT_TEMPERATURE,
            "responseMimeType": "application/json",
        },
    }

    data = http_post(url, payload, {"x-goog-api-key": api_key})

    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"Resposta do Gemini sem candidatos.")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts if not p.get("thought"))

    if not text:
        raise RuntimeError(f"Resposta vazia do Gemini.")
    return text


def call_groq(system: str, user: str, api_key: str) -> str:
    url = GROQ_API_URL

    payload = {
        "model": GROQ_MODEL,
        "temperature": DEFAULT_TEMPERATURE,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }

    data = http_post(url, payload, {"Authorization": f"Bearer {api_key}"})

    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("Resposta da Groq sem escolhas válidas.")

    return choices[0]["message"]["content"]
