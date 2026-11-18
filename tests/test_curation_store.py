import duckdb
import pytest

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


def test_save_review_cria_tabela_e_grava_linha(db_path):
    curation_store.save_review(make_content())

    with duckdb.connect(str(db_path)) as con:
        rows = con.execute(
            "SELECT content_id, status, body FROM curadoria"
        ).fetchall()

    assert rows == [("pkg-1_0", "approved", "Use um JSON Schema antes de publicar.")]


def test_save_review_atualiza_mesmo_id_sem_duplicar(db_path):
    curation_store.save_review(make_content(review_status="pending"))
    curation_store.save_review(
        make_content(review_status="approved", body="Texto editado.")
    )

    reviews = curation_store.load_reviews()

    assert list(reviews) == ["pkg-1_0"]
    assert reviews["pkg-1_0"] == {"review_status": "approved", "body": "Texto editado."}


def test_load_reviews_retorna_status_e_body_por_id(db_path):
    curation_store.save_review(make_content(id="a", review_status="rejected"))
    curation_store.save_review(make_content(id="b", review_status="approved"))

    reviews = curation_store.load_reviews()

    assert reviews["a"]["review_status"] == "rejected"
    assert reviews["b"]["review_status"] == "approved"


def test_load_reviews_sem_banco_cria_arquivo_e_retorna_vazio(tmp_path, monkeypatch):
    path = tmp_path / "subdir" / "curadoria.duckdb"
    monkeypatch.setattr(curation_store, "DB_PATH", path)

    assert curation_store.load_reviews() == {}
    assert path.exists()


def test_status_invalido_e_recusado_pelo_check(db_path):
    with pytest.raises(duckdb.Error):
        curation_store.save_review(make_content(review_status="publicado"))


def test_chave_obrigatoria_ausente_levanta_keyerror(db_path):
    content = make_content()
    del content["batch_id"]

    with pytest.raises(KeyError):
        curation_store.save_review(content)
        
