import duckdb
import pytest
import json
import re

from src.services import curation_store


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Redireciona o store para um DuckDB temporário, sem tocar em data/."""
    path = tmp_path / "curadoria.duckdb"
    monkeypatch.setattr(curation_store, "DB_PATH", path)
    return path


def make_content(**overrides):
    content = {
        "id": "pkg-1_0",
        "package_id": "pkg-1",
        "batch_id": "2026-W46",
        "target": "faq",
        "title": "Como validar um JSON?",
        "body": "Use um JSON Schema antes de publicar.",
        "review_status": "approved",
    }
    content.update(overrides)
    return content


def test_save_review_creates_table_and_inserts_row(db_path):
    curation_store.save_review(make_content())

    with duckdb.connect(str(db_path)) as con:
        rows = con.execute(
            "SELECT content_id, status, body FROM curadoria"
        ).fetchall()

    assert rows == [
        ("pkg-1_0", "approved", "Use um JSON Schema antes de publicar.")]


def test_save_review_updates_same_id_without_duplication(db_path):
    curation_store.save_review(make_content(review_status="pending"))
    curation_store.save_review(
        make_content(review_status="approved", body="Texto editado.")
    )

    reviews = curation_store.load_reviews()

    assert list(reviews) == ["pkg-1_0"]
    assert reviews["pkg-1_0"] == {"review_status": "approved",
                                  "body": "Texto editado."}


def test_load_reviews_returns_status_and_body_by_id(db_path):
    curation_store.save_review(make_content(id="a", review_status="rejected"))
    curation_store.save_review(make_content(id="b", review_status="approved"))

    reviews = curation_store.load_reviews()

    assert reviews["a"]["review_status"] == "rejected"
    assert reviews["b"]["review_status"] == "approved"


def test_load_reviews_without_db_creates_file_and_returns_empty(tmp_path, monkeypatch):
    path = tmp_path / "subdir" / "curadoria.duckdb"
    monkeypatch.setattr(curation_store, "DB_PATH", path)

    assert curation_store.load_reviews() == {}
    assert path.exists()


def test_invalid_status_is_rejected_by_check(db_path):
    with pytest.raises(duckdb.Error):
        curation_store.save_review(make_content(review_status="publicado"))


def test_missing_mandatory_key_raises_key_error(db_path):
    content = make_content()
    del content["batch_id"]

    with pytest.raises(KeyError):
        curation_store.save_review(content)


def test_export_approved_exports_only_approved_items(tmp_path, monkeypatch):
    monkeypatch.setattr(curation_store, "CURATION_EXPORT_DIR", tmp_path)
    package = {"package_id": "pkg-1", "linked_batch_id": "lote-se-001"}
    contents = [
        {"target": "faq", "title": "A", "body": "a",
            "potential_engagement": "low", "review_status": "approved"},
        {"target": "newsletter", "title": "B", "body": "b",
            "potential_engagement": "medium", "review_status": "rejected"},
        {"target": "linkedin", "title": "C", "body": "c",
            "potential_engagement": "high", "review_status": "pending"},
    ]

    path = curation_store.export_approved(package, contents)

    assert path.parent == tmp_path
    assert re.fullmatch(r"pacote-lote-se-001-\d{8}-\d{6}\.json", path.name)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert [c["title"] for c in payload["suggested_content"]] == ["A"]
    assert set(payload["suggested_content"][0]) == {
        "target", "title", "body", "potential_engagement"}
