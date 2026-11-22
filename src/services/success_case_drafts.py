"""Rascunhos de caso de sucesso a partir do retorno do WF09."""

from datetime import datetime, timezone

from src.services.faq_drafts import DRAFTS_DIR, save_new_draft_package
from src.utils.regex_patterns import EXECUTION_ID_RE


def generate_success_case_from_triage(result, drafts_dir=DRAFTS_DIR):
    if result.get("success") is not True or result.get("source") != "mastodon":
        return None
    eligible = [
        item for item in result.get("items", [])
        if item["editorial"]["suggested_route"] == "success_case"
        and item["editorial"]["needs_human_review"] is False
    ]
    if len(eligible) != 1:
        return None
    execution_id = str(result.get("execution_id", ""))
    if not EXECUTION_ID_RE.fullmatch(execution_id):
        raise ValueError(
            "O WF09 retornou um identificador de execução inválido.")
    item = eligible[0]
    source_text = item["clean_text"].strip()
    if not source_text:
        raise ValueError("O caso de sucesso precisa ter um relato de origem.")
    batch_id = f"wf09-{execution_id}"
    stamp = datetime.fromisoformat(item["created_at"])
    if stamp.tzinfo is None:
        raise ValueError(
            "O WF09 deve fornecer a data da publicação com fuso horário.")
    date = stamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    editorial = item["editorial"]
    summary = editorial["summary"].strip() or source_text
    attribution = f"Fonte: relato de {item['author']} no Mastodon. {item['url']}"
    post = f"Uma conquista compartilhada pela comunidade:\n\n“{source_text}”\n\n{attribution}"
    newsletter = f"Segundo o relato publicado no Mastodon, {summary[0].lower()}{summary[1:]}\n\n{attribution}"
    feeling = {
        "Neutral": "neutral", "Happy": "positive", "Excited": "positive",
        "Angry": "negative", "Disappointed": "negative",
    }[item["sentiment"]]
    package = {
        "package_id": batch_id,
        "linked_batch_id": batch_id,
        "status": "success",
        "reference_period": f"{date}/{date}",
        "processing_summary": {
            "total_interactions": 1,
            "sources_breakdown": {"mastodon": 1},
            "predominant_feeling": feeling,
            "main_topics": editorial["topics"],
        },
        "provenance": {
            "execution_id": execution_id,
            "input": "wf09_webhook_result",
            "source_file": item["source_file"],
            "post_id": item["post_id"],
        },
        "suggested_content": [
            {"id": f"{batch_id}_{target}", "target": target, "title": title,
             "body": body, "potential_engagement": "medium", "review_status": "pending"}
            for target, title, body in [
                ("linkedin", "Uma conquista da comunidade", post),
                ("newsletter", "Conquista da semana", newsletter),
            ]
        ],
    }
    return save_new_draft_package(package, drafts_dir)
