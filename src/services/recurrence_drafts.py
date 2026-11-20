"""Pacote de recorrência a partir do lote controlado do WF11."""

import re
from collections import Counter
from datetime import datetime, timezone

from src.services.faq_drafts import DRAFTS_DIR, save_new_draft_package


def generate_recurrence_from_triage(result, drafts_dir=DRAFTS_DIR):
    if (
        result.get("success") is not True
        or result.get("source") != "hackernews"
        or not re.fullmatch(r"s4-01-recorrencia-upload[0-9a-f]{16}", result.get("tag", ""))
    ):
        return None

    items = result["items"]
    unique = {}
    for item in items:
        unique.setdefault(str(item["comment_id"]), item)
    if len(unique) < 2:
        raise ValueError("O cenário de recorrência precisa de pelo menos dois comentários distintos.")
    if len({item["post_id"] for item in unique.values()}) != 1:
        raise ValueError("O cenário de recorrência precisa de uma única discussão.")
    evidence = [
        item for item in unique.values()
        if item["suggested_route"] == "faq" and item["needs_human_review"] is False
    ]
    if not evidence:
        raise ValueError("A triagem não encaminhou orientação técnica para FAQ.")
    execution_id = str(result.get("execution_id", ""))
    if not re.fullmatch(r"[0-9]+", execution_id):
        raise ValueError("O WF11 retornou um identificador de execução inválido.")
    batch_id = f"wf11-{execution_id}"
    dates = [
        datetime.fromtimestamp(int(item["comment"]["time"]), timezone.utc)
        .isoformat().replace("+00:00", "Z")
        for item in unique.values()
    ]
    feelings = {"Neutral": "neutral", "Happy": "positive", "Excited": "positive",
                "Angry": "negative", "Disappointed": "negative"}
    counts = Counter(feelings[item["comment"]["sentiment"]] for item in unique.values())
    post = evidence[0]["post"]
    excerpts = [
        f'“{item["comment"]["text"].strip()}” (comentário {item["comment_id"]})'
        for item in evidence
    ]
    topics = list(dict.fromkeys(
        topic for item in unique.values() for topic in item["comment"]["editorial"]["topics"]
    ))
    package = {
        "package_id": batch_id,
        "linked_batch_id": batch_id,
        "status": "success",
        "reference_period": f"{min(dates)}/{max(dates)}",
        "processing_summary": {
            "total_interactions": len(unique),
            "sources_breakdown": {"hackernews": len(unique)},
            "predominant_feeling": counts.most_common(1)[0][0],
            "main_topics": topics,
        },
        "provenance": {
            "execution_id": execution_id,
            "input": "wf11_webhook_result",
            "source_file": evidence[0]["source_file"],
            "post_id": evidence[0]["post_id"],
            "comment_ids": list(unique),
            "triaged_count": len(items),
        },
        "suggested_content": [
            {"id": f"{batch_id}_{target}", "target": target, "title": title,
             "body": body, "potential_engagement": "medium", "review_status": "pending"}
            for target, title, body in [
                ("newsletter", "Dúvida recorrente: reenvio de POST após timeout",
                 f"{len(unique)} comentários distintos discutiram como evitar gravações duplicadas "
                 f"ao repetir um POST após timeout. A triagem retornou {len(items)} registros. "
                 f"Registros com o mesmo ID foram contados uma vez.\n\nFonte: {post['url']}"),
                ("faq", post["title"],
                 "Orientação registrada na discussão:\n\n" + "\n\n".join(excerpts)
                 + f"\n\nFonte: {post['url']}"),
            ]
        ],
    }
    return save_new_draft_package(package, drafts_dir)
