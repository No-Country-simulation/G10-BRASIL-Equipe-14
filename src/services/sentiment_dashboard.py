"""Leitura analítica do snapshot, sem modificar o banco ou reavaliar com IA."""

import json
import re
from pathlib import Path

import duckdb
import pandas as pd

from src.config import DATABASE_PATH, EDITORIALS, SENTIMENTS


def timestamp(value):
    if value is None:
        return pd.NaT
    try:
        if re.fullmatch(r"\d+(\.\d+)?", str(value)):
            return pd.to_datetime(float(value), unit="s", utc=True)
        return pd.to_datetime(value, utc=True, errors="coerce")
    except (ValueError, OverflowError):
        return pd.NaT


def answer_field(answer, name):
    if name in answer:
        return answer[name]
    matches = [v for k, v in answer.items() if k.startswith(name + "_")]
    return matches[0] if len(matches) == 1 else None


def normalize(payload, object_key, loaded_at):
    """Expande todas as respostas e mantém a identidade da interação."""
    source = payload.get("source", "")
    if "clean_text" in payload:
        source, units = "mastodon", [payload]
    elif source == "hackernews":
        units = [payload.get("comment", {})]
    elif source == "stackoverflow":
        units = payload.get("answers", [])
    else:
        raise ValueError(f"Fonte não suportada no arquivo {object_key}")
    filename = str(object_key).replace("\\", "/").rsplit("/", 1)[-1]
    theme = re.sub(r"^(processed_)?result_(mastodon|stackoverflow|hackernews)_", "", filename)
    theme = theme.removesuffix(".json")
    theme = {"artificialintelligence": "artificial-intelligence"}.get(theme, theme)
    for index, unit in enumerate(units):
        editorial = unit.get("editorial") or {}
        if source == "mastodon":
            identity = unit.get("post_id")
            content, date = unit.get("clean_text"), unit.get("created_at")
            url = unit.get("url")
        elif source == "hackernews":
            identity = unit.get("id") or payload.get("comment_id")
            content, date = unit.get("text"), unit.get("time")
            url = f"https://news.ycombinator.com/item?id={identity}" if identity else None
        else:
            identity = unit.get("answer_id")
            content = answer_field(unit, "body_answer")
            date = answer_field(unit, "creation_date_answer")
            url = f"https://stackoverflow.com/a/{identity}" if identity else None
        instance = payload.get("source", "") if source == "mastodon" else ""
        route = editorial.get("suggested_route") or payload.get("suggested_route")
        route = "newsletter" if route == "newsletter_only" else route
        yield {
            "identity": f"{source}/{instance}/{identity}" if identity is not None else f"missing/{object_key}/{index}",
            "missing_id": identity is None,
            "source": source, "record_id": str(identity or ""), "theme": theme,
            "sentiment": unit.get("sentiment") if unit.get("sentiment") in SENTIMENTS else "Sem avaliação",
            "editorial": route if route in EDITORIALS else "Sem classificação",
            "topics": list(dict.fromkeys(t.strip() for t in editorial.get("topics", []) if isinstance(t, str) and t.strip())),
            "needs_review": editorial.get("needs_human_review", payload.get("needs_human_review")),
            "strength": unit.get("strength"), "confidence": unit.get("confidence"),
            "relevance": editorial.get("relevance_score"), "summary": editorial.get("summary"),
            "content": content, "url": url, "created_at": timestamp(date),
            "object_key": object_key, "loaded_at": loaded_at,
        }


def load_snapshot(database: Path = DATABASE_PATH):
    if not database.is_file():
        raise FileNotFoundError("O snapshot OCI ainda não foi carregado neste ambiente.")
    with duckdb.connect(str(database), read_only=True) as connection:
        raw = connection.execute(
            "SELECT payload, object_key, loaded_at FROM processed_records ORDER BY object_key"
        ).fetchall()
    rows = []
    for payload, key, loaded_at in raw:
        # Defesa adicional caso um snapshot seja carregado com pastas misturadas.
        if "/routing/" not in key.replace("\\", "/"):
            rows.extend(normalize(json.loads(payload), key, loaded_at))
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame, {"records": 0, "duplicates": 0, "missing_ids": 0, "conflicts": 0}
    conflicts = int((frame.groupby("identity")["sentiment"].nunique() > 1).sum())
    # Mantém uma avaliação por interação e tema. O resumo global deduplica também entre temas.
    frame = frame.sort_values(["loaded_at", "object_key"]).drop_duplicates(["identity", "theme"], keep="last")
    return frame, {
        "records": len(rows), "duplicates": len(rows) - frame.identity.nunique(),
        "missing_ids": int(frame.missing_id.sum()), "conflicts": conflicts,
    }
