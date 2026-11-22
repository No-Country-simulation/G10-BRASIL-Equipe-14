"""Geração e curadoria local de rascunhos a partir da fila FAQ do WF10."""

import json
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from tempfile import NamedTemporaryFile
from src.config import DRAFTS_DIR
from src.utils.regex_patterns import (
    DRAFT_PACKAGE_RE,
    EXECUTION_ID_RE,
    QUEUE_EXECUTION_FILE_RE,
    WHITESPACE_RE,
)


class _Paragraphs(HTMLParser):
    blocks = {"p", "li", "pre", "blockquote", "div", "br", "h1", "h2", "h3"}

    def __init__(self):
        super().__init__()
        self.current = []
        self.paragraphs = []
        self.hidden = None

    def flush(self):
        paragraph = "".join(self.current).strip()
        if paragraph:
            self.paragraphs.append(paragraph)
        self.current.clear()

    def handle_starttag(self, tag, attrs):
        if self.hidden is None and tag in {"script", "style"}:
            self.hidden = tag
        elif self.hidden is None and tag in self.blocks:
            self.flush()

    def handle_endtag(self, tag):
        if tag == self.hidden:
            self.hidden = None
        elif self.hidden is None and tag in self.blocks:
            self.flush()

    def handle_data(self, data):
        if self.hidden is None:
            self.current.append(data)


def _paragraphs(html):
    parser = _Paragraphs()
    parser.feed(html)
    parser.close()
    parser.flush()
    return parser.paragraphs


def generate_faq_package(queue_file, drafts_dir=DRAFTS_DIR):
    queue_file = Path(queue_file)
    match = QUEUE_EXECUTION_FILE_RE.search(queue_file.name)
    if not match:
        raise ValueError(
            "O nome do arquivo da fila deve terminar com o ID da execução.")
    rows = json.loads(queue_file.read_text(encoding="utf-8-sig"))
    if not isinstance(rows, list) or len(rows) != 1:
        raise ValueError("O piloto espera um item na fila FAQ.")
    return _generate_package(rows[0], match[1], drafts_dir, queue_file=queue_file.name)


def generate_faq_from_triage(result, drafts_dir=DRAFTS_DIR):
    """Gera o pacote a partir de um item elegível no retorno do WF10."""
    if result.get("success") is not True or result.get("source") != "stackoverflow":
        return None
    items = [
        item for item in result.get("items", [])
        if item.get("suggested_route") == "faq" and item.get("needs_human_review") is False
    ]
    if len(items) != 1:
        return None
    execution_id = str(result.get("execution_id", ""))
    if not EXECUTION_ID_RE.fullmatch(execution_id):
        raise ValueError(
            "O WF10 retornou um identificador de execução inválido.")
    return _generate_package(items[0], execution_id, drafts_dir)


def _generate_package(item, execution_id, drafts_dir, queue_file=None):
    batch_id = f"wf10-{execution_id}"
    target = drafts_dir / f"{batch_id}.json"
    if target.exists():
        return target

    destination = item["routing"]["destination"] if queue_file else item["suggested_route"]
    if item["source"] != "stackoverflow" or destination != "faq":
        raise ValueError(
            "O piloto espera um item Stack Exchange roteado para FAQ.")
    answers = [row for row in item["answers"] if str(
        row["answer_id"]) == str(item["answer_id"])]
    if len(answers) != 1:
        raise ValueError(
            "O ID roteado deve identificar exatamente uma resposta na fila.")
    answer = answers[0]
    owners = [key.removeprefix("owner_answer_")
              for key in answer if key.startswith("owner_answer_")]
    if len(owners) != 1:
        raise ValueError("O registro deve identificar o autor da resposta.")
    suffix = owners[0]
    paragraphs = _paragraphs(answer[f"body_answer_{suffix}"])
    if not paragraphs:
        raise ValueError(
            "A resposta precisa conter uma explicação para gerar os rascunhos.")
    author = answer[f"owner_answer_{suffix}"]["display_name"]
    link = answer[f"link_answer_{suffix}"]
    license_name = answer[f"content_license_answer_{suffix}"]
    attribution = f"Fonte: {author}, Stack Overflow. {link} | Licença: {license_name}."
    stamp = datetime.fromtimestamp(
        answer[f"creation_date_answer_{suffix}"], timezone.utc)
    iso_stamp = stamp.isoformat().replace("+00:00", "Z")
    feeling = {
        "Neutral": "neutral", "Happy": "positive", "Excited": "positive",
        "Angry": "negative", "Disappointed": "negative",
    }[answer["sentiment"]]
    title = unescape(item["title_question"]).strip()
    if not title:
        raise ValueError("A pergunta precisa ter um título.")
    faq_text = "\n\n".join(paragraphs)
    excerpt = WHITESPACE_RE.sub(" ", paragraphs[0])
    if len(excerpt) > 320:
        excerpt = excerpt[:317].rsplit(" ", 1)[0] + "…"
    drafts = [
        ("faq", title, f"{faq_text}\n\n{attribution}"),
        ("linkedin", f"Dúvida da comunidade: {title}",
         f"Uma dica da comunidade sobre esta dúvida:\n\n“{excerpt}”\n\n"
         f"Confira a explicação completa na resposta original.\n\n{attribution}"),
    ]
    package = {
        "package_id": batch_id,
        "linked_batch_id": batch_id,
        "status": "success",
        "reference_period": f"{iso_stamp}/{iso_stamp}",
        "processing_summary": {
            "total_interactions": 1,
            "sources_breakdown": {"stackoverflow": 1},
            "predominant_feeling": feeling,
            "main_topics": answer["editorial"]["topics"],
        },
        "provenance": {
            "execution_id": execution_id,
            **({"queue_file": queue_file} if queue_file else {"input": "wf10_webhook_result"}),
            "source_file": item["source_file"],
            "source_id": item["source_id"],
            "answer_id": item["answer_id"],
        },
        "suggested_content": [
            {"id": f"{batch_id}_{destination}", "target": destination, "title": title,
             "body": body, "potential_engagement": "medium", "review_status": "pending"}
            for destination, title, body in drafts
        ],
    }
    return save_new_draft_package(package, drafts_dir)


def save_new_draft_package(package, drafts_dir=DRAFTS_DIR):
    drafts_dir.mkdir(parents=True, exist_ok=True)
    target = drafts_dir / f"{package['package_id']}.json"
    try:
        with target.open("x", encoding="utf-8") as file:
            json.dump(package, file, ensure_ascii=False, indent=2)
    except FileExistsError:
        pass
    return target


def load_draft_packages(drafts_dir=DRAFTS_DIR):
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(drafts_dir.glob("wf*.json"))
        if DRAFT_PACKAGE_RE.fullmatch(path.stem)
    ]


def save_draft_review(content, status, body, drafts_dir=DRAFTS_DIR):
    package_id = content["id"].split("_", 1)[0]
    if not DRAFT_PACKAGE_RE.fullmatch(package_id):
        raise ValueError("Identificador de pacote inválido.")
    path = drafts_dir / f"{package_id}.json"
    package = json.loads(path.read_text(encoding="utf-8"))
    stored = next(
        item for item in package["suggested_content"] if item["id"] == content["id"])
    stored.update(body=body, review_status=status)
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=drafts_dir, delete=False) as temp:
        json.dump(package, temp, ensure_ascii=False, indent=2)
    Path(temp.name).replace(path)
