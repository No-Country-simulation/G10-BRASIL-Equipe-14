"""Contexto analítico e cliente HTTP do WF13."""

import hashlib
import json
import os
from uuid import uuid4

import pandas as pd
import requests

from src.config import N8N_SENTIMENT_CHAT_DEFAULT_URL


def build_context(frame, filters, loaded_at, quality):
    unique = frame.drop_duplicates("identity", keep="last")

    def counts(data, column):
        return {str(k): int(v) for k, v in data.groupby(column).identity.nunique().items()}

    def cross(data, dimensions):
        return data.groupby(dimensions).identity.nunique().rename("count").reset_index().to_dict("records")

    def valid_scores(data, column):
        # Missing/invalid assessments must not be interpreted as zero.
        values = pd.to_numeric(data[column], errors="coerce")
        return values.where(values.between(0, 1))

    def score_summary(data):
        result = {}
        for column in ["strength", "confidence"]:
            values = valid_scores(data, column).dropna()
            result[column] = {
                "count": len(values),
                "missing_or_invalid_count": len(data) - len(values),
                "mean": float(values.mean()) if len(values) else None,
                "min": float(values.min()) if len(values) else None,
                "max": float(values.max()) if len(values) else None,
            }
        return result

    def theme_score(data, column, maximum):
        raw = data[column] if column in data else pd.Series(index=data.index, dtype=float)
        values = pd.to_numeric(raw, errors="coerce")
        valid = values.between(0, maximum) & ~raw.map(lambda value: isinstance(value, bool))
        if column == "relevance":
            valid &= values.mod(1).eq(0)
        values = values[valid]
        return {
            "count": len(values),
            "missing_or_invalid_count": len(data) - len(values),
            "mean": float(values.mean()) if len(values) else None,
        }

    theme_interactions = frame.drop_duplicates(["theme", "identity"], keep="last")
    scores_by_theme = [
        {
            "theme": str(theme),
            "unique_interactions": len(group),
            "confidence": theme_score(group, "confidence", 1),
            "relevance_score": theme_score(group, "relevance", 100),
        }
        for theme, group in theme_interactions.groupby("theme", sort=True)
    ]

    topics = frame.explode("topics").dropna(subset=["topics"]).drop_duplicates(["identity", "topics"])
    metrics = {
        "unique_interactions": len(unique),
        "sentiment_counts": counts(unique, "sentiment"),
        "editorial_counts": counts(unique, "editorial"),
        "source_counts": counts(unique, "source"),
        "theme_counts": counts(frame, "theme"),
        "needs_review_count": int(unique.needs_review.eq(True).sum()),
        "assessment_scores": score_summary(unique),
        "assessment_scores_by_theme": scores_by_theme,
        "assessment_score_definitions": {
            "strength": "Intensidade do sentimento atribuída pelo agente, de 0 a 1; não indica sentimento positivo ou negativo.",
            "confidence": "Confiança atribuída pelo agente à classificação de sentimento, de 0 a 1; não é uma probabilidade de acerto calibrada.",
            "aggregation": "Estatísticas sobre interações únicas do recorte. Valores ausentes ou fora de 0 a 1 são excluídos, sem substituição por zero. Não inferir outras segmentações a partir das médias gerais ou da amostra.",
        },
        "assessment_scores_by_sentiment": [
            {"sentiment": sentiment, "unique_interactions": len(group), **score_summary(group)}
            for sentiment, group in unique.groupby("sentiment", sort=True)
        ],
        "sentiment_by_editorial": cross(unique, ["editorial", "sentiment"]),
        "sentiment_by_theme": cross(frame, ["theme", "sentiment"]),
        "sentiment_by_source": cross(unique, ["source", "sentiment"]),
        "sentiment_by_theme_and_editorial": cross(frame, ["theme", "editorial", "sentiment"]),
        "top_topics": [{"topic": k, "count": v} for k, v in sorted(counts(topics, "topics").items(), key=lambda pair: (-pair[1], pair[0]))[:30]],
    }
    evidence = []
    samples = unique.sort_values(["relevance", "identity"], ascending=[False, True], na_position="last").head(15).copy()
    for column in ["strength", "confidence"]:
        samples[column] = valid_scores(samples, column)
    for row in samples.to_dict("records"):
        evidence.append({
            "id": row["identity"], "source": row["source"],
            "sentiment": row["sentiment"], "editorial": row["editorial"],
            "strength": None if pd.isna(row["strength"]) else float(row["strength"]),
            "confidence": None if pd.isna(row["confidence"]) else float(row["confidence"]),
            "topics": row["topics"][:5],
            "summary": str(row["summary"] or "")[:700],
            "content": str(row["content"] or "")[:700],
            "url": row["url"],
        })
    stamp = pd.to_datetime(loaded_at, utc=True).isoformat()
    signature = json.dumps({"loaded_at": stamp, "filters": filters, "metrics": metrics}, sort_keys=True, ensure_ascii=False)
    return {
        "snapshot_id": hashlib.sha256(signature.encode()).hexdigest(),
        "loaded_at": stamp, "filters": filters, "metrics": metrics,
        "evidence": evidence,
        "limitations": [
            "Snapshot local; não representa toda a comunidade ou um histórico de crescimento.",
            "Evidências são uma amostra de até 15 interações ordenadas por relevância; não representam a distribuição geral.",
            "Temas de coleta podem se sobrepor; o total geral deduplica interações.",
            f"Interações sem data no recorte: {int(unique.created_at.isna().sum())}.",
            f"Conflitos de sentimento no snapshot completo: {quality['conflicts']}.",
        ],
    }


def ask_agent(question, history, context, session_id):
    key = os.getenv("N8N_API_KEY", "").strip()
    if not key:
        raise ValueError("Configure N8N_API_KEY no .env e reinicie o Streamlit.")
    request_id = str(uuid4())
    payload = {
        "request_id": request_id, "session_id": session_id,
        "question": question.strip(),
        "history": [{"role": m["role"], "content": m["content"][:6000]} for m in history[-12:]],
        "context": context,
    }
    if len(json.dumps(payload, ensure_ascii=False)) > 180000:
        raise ValueError("O contexto excedeu o limite do chat. Restrinja os filtros e tente novamente.")
    try:
        response = requests.post(
            os.getenv("N8N_SENTIMENT_CHAT_WEBHOOK_URL") or N8N_SENTIMENT_CHAT_DEFAULT_URL,
            json=payload, headers={"communitylab-api-key": key}, timeout=(10, 120),
        )
    except requests.Timeout:
        raise ValueError("O agente demorou para responder. Tente novamente.") from None
    except requests.RequestException:
        raise ValueError("Não foi possível conectar ao agente. Tente novamente.") from None
    if response.status_code != 200:
        raise ValueError(f"O serviço não concluiu a análise (HTTP {response.status_code}).")
    try:
        data = response.json()
    except ValueError:
        raise ValueError("O serviço retornou uma resposta inválida.") from None
    if (not isinstance(data, dict) or data.get("status") != "success"
            or data.get("request_id") != request_id
            or data.get("snapshot_id") != context["snapshot_id"]
            or not isinstance(data.get("answer"), str) or not data["answer"].strip()):
        raise ValueError("A resposta do agente não corresponde à pergunta e ao snapshot enviados.")
    return data["answer"].strip()
