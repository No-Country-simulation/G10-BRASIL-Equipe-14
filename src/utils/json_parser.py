import json
from typing import Any

from src.utils.regex_patterns import CODE_FENCE_PATTERN


def remove_code_fence(text: str) -> str:
    match = CODE_FENCE_PATTERN.match(text)

    if match:
        return match.group(1).strip()

    return text.strip()


def parse_llm_json(text: str) -> dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError(
            "O texto fornecido para parsing está vazio ou não é uma string válida."
        )

    text_clean = remove_code_fence(text)

    try:
        data: Any = json.loads(text_clean)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Falha ao decodificar JSON da resposta do LLM: "
            f"{exc.msg} (linha {exc.lineno}, coluna {exc.colno})."
        ) from exc

    if not isinstance(data, dict):
        raise ValueError("A resposta do LLM deve ser um objeto JSON.")

    return data
