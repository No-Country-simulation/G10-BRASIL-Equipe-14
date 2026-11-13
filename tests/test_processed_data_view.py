import duckdb
import json
from streamlit.testing.v1 import AppTest

from src import config
from src.services import processed_duckdb


def test_missing_database(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    app = AppTest.from_file("../src/views/processed_data.py", default_timeout=15).run()
    assert not app.exception
    assert "ainda não foram carregados" in app.info[0].value
    assert not (tmp_path / "communitylab_oci.duckdb").exists()


def test_filter_and_totals(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    with duckdb.connect(str(tmp_path / "communitylab_oci.duckdb")) as con:
        con.execute("""
            CREATE TABLE v_processed AS
            SELECT source, '1' AS record_id, 'Título' AS title, 'Texto' AS content,
                   'https://example.com' AS url, 'positive' AS sentiment,
                   'faq' AS suggested_route, current_timestamp AS loaded_at,
                   's3://bucket/processed/result_' || source || '_artificialintelligence.json' AS object_key
            FROM (VALUES ('mastodon'), ('hackernews')) t(source)
        """)
    app = AppTest.from_file("../src/views/processed_data.py", default_timeout=15).run()
    assert not app.exception
    assert app.metric[0].value == "2"
    assert len(app.dataframe[0].value) == 2
    app.selectbox[0].select("mastodon").run()
    assert not app.exception
    assert app.metric[1].value == "1"
    assert app.dataframe[0].value["source"].tolist() == ["mastodon"]


def test_combined_tag_filter(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    for source, tag in [('mastodon', 'artificialintelligence'), ('hackernews', 'docker')]:
        (tmp_path / f'result_{source}_{tag}.json').write_text(
            json.dumps([{'source': source, 'post_id': '1'}]), encoding='utf-8'
        )
    with duckdb.connect(str(tmp_path / 'communitylab_oci.duckdb')) as con:
        processed_duckdb.refresh(con, str(tmp_path / '*.json'))
    app = AppTest.from_file('../src/views/processed_data.py', default_timeout=15).run()
    assert not app.exception
    assert app.selectbox[1].options == ['Todas', 'artificialintelligence', 'docker']
    app.selectbox[1].select('docker').run()
    assert app.metric[1].value == '1'
    assert app.dataframe[0].value['source'].tolist() == ['hackernews']
    app.selectbox[0].select('mastodon').run()
    assert not app.exception
    assert app.metric[1].value == '0'
    assert 'Nenhum registro' in app.info[0].value
    app.selectbox[1].select('artificialintelligence').run()
    assert app.metric[1].value == '1'


def test_uninitialized_database(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    duckdb.connect(str(tmp_path / "communitylab_oci.duckdb")).close()
    app = AppTest.from_file("../src/views/processed_data.py", default_timeout=15).run()
    assert not app.exception
    assert "Não foi possível consultar" in app.error[0].value


def test_refresh_button_and_failed_refresh_preserves_snapshot(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    sample = tmp_path / "sample.json"
    sample.write_text(json.dumps([
        {"source": "hackernews", "comment_id": "42", "comment": {"text": "Conteúdo"}}
    ]), encoding="utf-8")
    monkeypatch.setattr(processed_duckdb, "configure_oci", lambda con: str(sample))
    app = AppTest.from_file("../src/views/processed_data.py", default_timeout=15).run()
    app.button[0].click().run()
    assert not app.exception
    assert app.success
    assert app.metric[0].value == "1"
    assert app.dataframe[0].value["record_id"].tolist() == ["42"]

    # Validação falha depois da substituição da tabela, exercitando o rollback real.
    sample.write_text('[{"invalid": true}]', encoding="utf-8")
    app.button[0].click().run()
    assert not app.exception
    assert "Não foi possível atualizar" in app.error[0].value
    assert app.metric[0].value == "1"
    assert app.dataframe[0].value["record_id"].tolist() == ["42"]


def test_refresh_empty_snapshot(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    sample = tmp_path / "empty.json"
    sample.write_text('[]', encoding="utf-8")
    monkeypatch.setattr(processed_duckdb, "configure_oci", lambda con: str(sample))
    app = AppTest.from_file("../src/views/processed_data.py", default_timeout=15).run()
    app.button[0].click().run()
    assert not app.exception
    assert "não contém registros" in app.info[0].value
