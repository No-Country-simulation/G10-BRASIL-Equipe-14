from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from src.config import SENTIMENT_DASHBOARD_PATH
from src.services.sentiment_chat import ask_agent, build_context
from src.services.sentiment_dashboard import normalize
import pandas as pd


def test_context_deduplicates_and_keeps_theme_counts():
    rows = []
    for theme in ['docker', 'devops']:
        rows.extend(normalize({'source': 'mastodon.social', 'post_id': '1', 'clean_text': 'texto', 'sentiment': 'Happy'}, f'result_mastodon_{theme}.json', '2026-11-15'))
    context = build_context(pd.DataFrame(rows), {}, '2026-11-15', {'conflicts': 0})
    assert context['metrics']['unique_interactions'] == 1
    assert context['metrics']['theme_counts'] == {'devops': 1, 'docker': 1}
    assert len(context['evidence']) == 1


def test_context_includes_scores_without_double_counting_overlapping_themes():
    rows = []
    for theme in ["docker", "devops"]:
        rows.extend(normalize({"source": "mastodon.social", "post_id": "1", "clean_text": "Texto", "sentiment": "Happy", "strength": 0.7, "confidence": 0.9}, f"result_mastodon_{theme}.json", "2026-11-15"))
    rows.extend(normalize({"source": "mastodon.social", "post_id": "2", "clean_text": "Outro", "sentiment": "Neutral", "strength": 0.1, "confidence": 0.7}, "result_mastodon_docker.json", "2026-11-15"))
    context = build_context(pd.DataFrame(rows), {}, "2026-11-15", {"conflicts": 0})
    scores = context["metrics"]["assessment_scores"]
    assert scores["strength"]["count"] == 2
    assert scores["strength"]["mean"] == pytest.approx(0.4)
    assert scores["confidence"]["mean"] == pytest.approx(0.8)
    evidence = next(item for item in context["evidence"] if item["id"].endswith("/1"))
    assert evidence["strength"] == 0.7
    assert evidence["confidence"] == 0.9
    grouped = {item["sentiment"]: item for item in context["metrics"]["assessment_scores_by_sentiment"]}
    assert grouped["Happy"]["confidence"]["mean"] == 0.9


def test_missing_invalid_and_zero_scores_are_distinct():
    import json

    rows = []
    for index, score in enumerate([None, float("nan"), float("inf"), -0.1, 1.1, 0]):
        rows.extend(normalize({"source": "mastodon.social", "post_id": str(index), "clean_text": "Texto", "sentiment": "Neutral", "strength": score, "confidence": score}, "result_mastodon_docker.json", "2026-11-15"))
    context = build_context(pd.DataFrame(rows), {}, "2026-11-15", {"conflicts": 0})
    summary = context["metrics"]["assessment_scores"]["strength"]
    assert summary["count"] == 1
    assert summary["missing_or_invalid_count"] == 5
    assert summary["mean"] == 0
    assert sum(item["strength"] is None for item in context["evidence"]) == 5
    json.dumps(context, allow_nan=False)


def test_client_authentication_and_response_identity(monkeypatch):
    monkeypatch.setenv('N8N_API_KEY', 'test-key')
    def post(url, **kwargs):
        assert kwargs['headers']['communitylab-api-key'] == 'test-key'
        return Mock(status_code=200, json=lambda: {
            'status': 'success', 'request_id': kwargs['json']['request_id'],
            'snapshot_id': 'snapshot', 'answer': 'Resposta em português.',
        })
    monkeypatch.setattr('src.services.sentiment_chat.requests.post', post)
    assert ask_agent('Pergunta', [], {'snapshot_id': 'snapshot'}, 'session') == 'Resposta em português.'
    monkeypatch.setattr('src.services.sentiment_chat.requests.post', lambda *a, **kw: Mock(status_code=200, json=lambda: {'status': 'success', 'request_id': 'wrong'}))
    with pytest.raises(ValueError, match='não corresponde'):
        ask_agent('Pergunta', [], {'snapshot_id': 'snapshot'}, 'session')


def test_chat_roundtrip_and_filter_reset(monkeypatch):
    import src.views.dashboard_chat as chat
    monkeypatch.setattr(chat, 'ask_agent', lambda *a: 'Resposta de teste')
    # Isola a interface de arquivos DuckDB locais.
    rows = list(normalize({'source': 'mastodon.social', 'post_id': '1', 'clean_text': 'Texto', 'sentiment': 'Happy'}, 'result_mastodon_docker.json', '2026-11-15'))
    monkeypatch.setattr('src.services.sentiment_dashboard.load_snapshot', lambda: (pd.DataFrame(rows), {'records': 1, 'conflicts': 0}))
    app = AppTest.from_file(str(SENTIMENT_DASHBOARD_PATH), default_timeout=20).run()
    assert not app.chat_input
    assert not app.chat_message
    app.text_area(key='sentiment_question').set_value('Qual sentimento?')
    next(button for button in app.button if button.label == 'Enviar pergunta').click().run()
    assert not app.exception
    assert len(app.chat_message) == 2
    app.multiselect[1].set_value(['docker']).run()
    assert not app.exception
    assert len(app.chat_message) == 0
