import json

import duckdb

from src.services.sentiment_dashboard import load_snapshot, normalize


def test_answers_use_own_ids_and_dates():
    payload = {"source": "stackoverflow", "source_id": "1", "answers": [
        {"answer_id": 10, "body_answer_99": "Solução", "creation_date_answer_99": 1700000000, "sentiment": "Neutral"},
        {"answer_id": 11, "sentiment": "Happy"},
    ]}
    rows = list(normalize(payload, "result_stackoverflow_docker.json", "2026-01-01"))
    assert [row["record_id"] for row in rows] == ["10", "11"]
    assert rows[0]["content"] == "Solução"
    assert rows[0]["created_at"].year == 2023


def test_snapshot_excludes_routes_and_preserves_themes(tmp_path):
    path = tmp_path / "test.duckdb"
    post = {"source": "mastodon.social", "post_id": "1", "clean_text": "Texto", "sentiment": "Happy", "editorial": {"suggested_route": "newsletter_only"}}
    with duckdb.connect(str(path)) as con:
        con.execute("CREATE TABLE processed_records(payload JSON, object_key VARCHAR, loaded_at TIMESTAMP)")
        for key in ["processed/result_mastodon_docker.json", "processed/result_mastodon_devops.json", "processed/routing/newsletter/copy.json"]:
            con.execute("INSERT INTO processed_records VALUES (?, ?, '2026-01-01')", [json.dumps(post), key])
    frame, quality = load_snapshot(path)
    assert len(frame) == 2
    assert frame.identity.nunique() == 1
    assert set(frame.theme) == {"docker", "devops"}
    assert set(frame.editorial) == {"newsletter"}
    assert quality["records"] == 2


def test_snapshot_preserves_sentiment_scores_for_all_sources(tmp_path):
    path = tmp_path / "scores.duckdb"
    unit = {"sentiment": "Angry", "strength": 0.7, "confidence": 0.9}
    payloads = [
        ("hackernews", {"source": "hackernews", "comment": {"id": "50071922", **unit}}),
        ("mastodon", {"source": "mastodon.social", "post_id": "1", "clean_text": "Texto", **unit}),
        ("stackoverflow", {"source": "stackoverflow", "answers": [{"answer_id": "2", **unit}]}),
    ]
    with duckdb.connect(str(path)) as connection:
        connection.execute("CREATE TABLE processed_records(payload JSON, object_key VARCHAR, loaded_at TIMESTAMP)")
        for source, payload in payloads:
            connection.execute("INSERT INTO processed_records VALUES (?, ?, '2026-11-15')", [json.dumps(payload), f"processed/result_{source}_docker.json"])
    frame, _ = load_snapshot(path)
    assert len(frame) == 3
    assert frame.strength.tolist() == [0.7] * 3
    assert frame.confidence.tolist() == [0.9] * 3
