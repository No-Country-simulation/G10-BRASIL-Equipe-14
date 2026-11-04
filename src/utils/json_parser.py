import json
import re


def parse_llm_json(text: str) -> dict:
    if not text or not isinstance(text, str):
        raise ValueError(
            "O texto fornecido para parsing está vazio ou não é uma string válida."
        )

    text_clean = text.strip()

    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text_clean, re.DOTALL)
    if match:
        text_clean = match.group(1)
    else:
        text_clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", text_clean)

    try:
        return json.loads(text_clean)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Falha ao decodificar JSON da resposta do LLM: {e}. Texto recebido: {text_clean[:300]}"
        ) from e
