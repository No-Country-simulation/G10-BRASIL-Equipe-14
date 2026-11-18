import json
from datetime import datetime
from pathlib import Path

import duckdb

from src.config import CURATION_DB_PATH, CURATION_EXPORT_DIR

DB_PATH = CURATION_DB_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS curadoria (
    content_id   VARCHAR PRIMARY KEY,
    package_id   VARCHAR NOT NULL,
    batch_id     VARCHAR NOT NULL,
    target       VARCHAR NOT NULL,
    title        VARCHAR,
    body         VARCHAR,
    status       VARCHAR NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')),
    reviewed_at  TIMESTAMP
)
"""


def save_review(content: dict) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DB_PATH)) as con:
        con.execute(SCHEMA)
        con.execute(
            """
            INSERT INTO curadoria
                (content_id, package_id, batch_id, target, title, body, status, reviewed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (content_id) DO UPDATE SET
                title = excluded.title,
                body = excluded.body,
                status = excluded.status,
                reviewed_at = excluded.reviewed_at
            """,
            [
                content["id"],
                content["package_id"],
                content["batch_id"],
                content["target"],
                content["title"],
                content["body"],
                content["review_status"],
                datetime.now(),
            ],
        )


def load_reviews() -> dict[str, dict]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DB_PATH)) as con:
        con.execute(SCHEMA)
        rows = con.execute("SELECT content_id, status, body FROM curadoria").fetchall()
    return {cid: {"review_status": status, "body": body} for cid, status, body in rows}
    
 
    
    
def export_approved(package: dict, contents: list[dict]) -> Path:
    """Exporta só os aprovados no formato de suggested_content. Rejeitados não entram."""
    CURATION_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    path = CURATION_EXPORT_DIR / f"pacote-{package['linked_batch_id']}-{now:%Y%m%d-%H%M%S}.json"
    payload = {
        "package_id": package["package_id"],
        "linked_batch_id": package["linked_batch_id"],
        "approved_at": now.isoformat(timespec="seconds"),
        "suggested_content": [
            {
                "target": c["target"],
                "title": c["title"],
                "body": c["body"],
                "potential_engagement": c["potential_engagement"],
            }
            for c in contents
            if c["review_status"] == "approved"
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
