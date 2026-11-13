from __future__ import annotations

import html
import json
from typing import Any

from src.config import CHANNEL_LIMITS
from src.utils.regex_patterns import HTML_TAG_RE, WHITESPACE_RE


def plain(text: str | None, limit: int) -> str:
    text = HTML_TAG_RE.sub(" ", text or "")
    text = WHITESPACE_RE.sub(" ", html.unescape(text)).strip()
    return text[:limit]


def newsletter_item(item: dict[str, Any]) -> dict[str, Any]:
    thread, classification = item["input"], item["classification"]
    first = thread["interactions"][0]
    entry = {
        key: classification.get(key)
        for key in (
            "type",
            "sentiment",
            "topics",
            "summary",
            "relevance_score",
            "suggested_route",
            "has_answer",
        )
    }
    entry.update(
        {
            "id": thread["id"],
            "source": thread["source"],
            "url": thread.get("url"),
            "author": first.get("author"),
            "title": first.get("title"),
            "content": plain(first.get("content"), 500),
            "view_count": (first.get("raw_metadata") or {}).get("view_count"),
            "answer_count": (first.get("raw_metadata") or {}).get("answer_count"),
        }
    )
    accepted = [
        interaction
        for interaction in thread["interactions"][1:]
        if (interaction.get("raw_metadata") or {}).get("is_accepted")
    ]
    if accepted:
        entry["accepted_answer"] = {
            "author": accepted[0].get("author"),
            "content": plain(accepted[0].get("content"), 800),
        }
    return entry


def build_user_prompt(
    job: dict[str, Any],
    items: list[dict[str, Any]],
    period: str | None,
) -> str:
    if job["canal"] == "newsletter":
        batch = sorted(
            (newsletter_item(item) for item in items),
            key=lambda item: -(item.get("relevance_score") or 0),
        )[:15]
        return (
            "Gere a edição da newsletter.\n"
            f"PERÍODO: {period}\n"
            f"ITENS: {json.dumps(batch, ensure_ascii=False)}"
        )

    item = items[0]
    classification = json.dumps(item["classification"], ensure_ascii=False)
    thread = json.dumps(item["input"], ensure_ascii=False)
    if job["canal"] == "faq":
        return (
            f"Gere o card de FAQ.\nCLASSIFICAÇÃO: {classification}\n"
            f"ITEM ORIGINAL: {thread}"
        )
    return (
        "Gere o conteúdo para o canal indicado.\n\n"
        f"CLASSIFICAÇÃO:\n{classification}\n\nITEM ORIGINAL:\n{thread}"
    )


def build_fix_request(errors: list[str], channel: str) -> str | None:
    asks = []

    if any(error.startswith("body com ") for error in errors):
        low, high = CHANNEL_LIMITS[channel][0:2]
        asks.append(
            f"o campo body ficou fora do limite deste canal "
            f"({low} a {high} caracteres)"
        )

    if any(error.startswith("menção com @") for error in errors):
        asks.append('há nomes com "@" no body; escreva os nomes sem "@"')

    if any(" hashtags (limite " in error for error in errors):
        min_hashtags, max_hashtags = CHANNEL_LIMITS[channel][2:4]
        asks.append(
            f"remova hashtags excedentes e deixe exatamente entre "
            f"{min_hashtags} e {max_hashtags} hashtags no final do body"
        )

    if any("sem a seção **Resposta curta:**" in error for error in errors):
        asks.append(
            "o body deve conter obrigatoriamente a seção com o rótulo exato **Resposta curta:**."
            "Substitua qualquer **Resposta:** ou **Como funciona:** por **Resposta curta:** e não crie outro rótulo"
        )

    if any("deveria começar com" in error for error in errors):
        asks.append(
            "mova exatamente [PRECISA DE REVISÃO TÉCNICA] para o início do body; "
            "depois inclua somente a pergunta reescrita, sem resposta, "
            "sem **Resposta curta:** e sem **Fonte:**"
        )

    if not asks:
        return None

    return (
        "Corrija: " + "; ".join(asks) + ". Mantenha os mesmos fatos e regras. "
        "Responda no mesmo formato JSON."
    )


def build_correction_prompt(
    *,
    previous_response: str,
    errors: list[str],
    channel: str,
) -> tuple[str, str] | None:
    fix_request = build_fix_request(errors, channel)
    if fix_request is None:
        return None

    correction_system = (
        "Você é um corretor de saída JSON. Corrija somente os erros informados. "
        "Retorne exclusivamente um objeto JSON válido, sem markdown ou explicações. "
        "Não invente dados e preserve os valores corretos já existentes."
    )
    correction_user = (
        "RESPOSTA ANTERIOR:\n"
        f"{previous_response or '{}'}\n\n"
        "ERROS ENCONTRADOS:\n"
        + "\n".join(f"- {error}" for error in errors)
        + f"\n\n{fix_request}"
    )
    return correction_system, correction_user
