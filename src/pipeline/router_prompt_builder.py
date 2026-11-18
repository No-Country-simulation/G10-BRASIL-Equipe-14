from __future__ import annotations

import json
from typing import Any


def build_user_prompt(
    case: dict[str, Any],
) -> str:
    return (
        "Classifique a thread abaixo:\n\n"
        "THREAD:\n"
        f"{json.dumps(case['input'], ensure_ascii=False)}"
    )


def build_correction_prompt(
    *,
    previous_response: str,
    errors: list[str],
) -> tuple[str, str]:
    correction_system = (
        "Você é um corretor de saída JSON. "
        "Corrija somente os erros informados na resposta anterior. "
        "Retorne exclusivamente um objeto JSON válido, sem markdown ou explicações. "
        "Não invente dados e preserve os valores corretos já existentes."
    )

    correction_user = (
        "RESPOSTA ANTERIOR:\n"
        f"{previous_response or '{}'}\n\n"
        "ERROS ENCONTRADOS:\n" +
        "\n".join(f"- {error}" for error in errors) + "\n\n"
        "Reavalie apenas o necessário e retorne o JSON corrigido."
    )

    return correction_system, correction_user
