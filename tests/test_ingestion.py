import pytest
import requests

from src.services import ingestion
from src.services.ingestion import parse_csv, parse_input, parse_json, parse_pasted_text, send_to_ingestion


def test_parse_json_valid_and_bom():
    assert parse_json(b'\xef\xbb\xbf{"a": 1}') == {"a": 1}


def test_parse_json_invalid():
    with pytest.raises(ValueError, match="linha 1"):
        parse_json("{oops")


def test_parse_json_bad_encoding():
    with pytest.raises(ValueError, match="UTF-8"):
        parse_json(b"\xff\xfe\x00")


def test_send_to_ingestion_returns_status_code(monkeypatch):
    class Resp:
        status_code = 202

    monkeypatch.setattr(ingestion.requests, "post", lambda url, json, timeout: Resp())
    assert send_to_ingestion({"ok": 1}, "http://x") == 202


def test_send_to_ingestion_propagates_network_errors(monkeypatch):
    def fake_post(url, json, timeout):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(ingestion.requests, "post", fake_post)
    with pytest.raises(requests.ConnectionError):
        send_to_ingestion({}, "http://x")


def test_parse_csv_semicolon_to_records():
    assert parse_csv(b"\xef\xbb\xbfid;source\n1;a\n2;b\n") == [
        {"id": "1", "source": "a"},
        {"id": "2", "source": "b"},
    ]


@pytest.mark.parametrize("raw,msg", [("", "vazio"), ("id;source\n", "sem linhas"), ("a;b\n1\n", "colunas"), ("a;b\n1;2;3\n", "colunas")])
def test_parse_csv_invalid(raw, msg):
    with pytest.raises(ValueError, match=msg):
        parse_csv(raw)


def test_parse_input_rejects_empty_list_and_primitives():
    with pytest.raises(ValueError, match="vazia"):
        parse_input("[]", as_csv=False)
    with pytest.raises(ValueError, match="objeto"):
        parse_input("42", as_csv=False)


def test_parse_input_dispatches_by_format():
    assert parse_input('{"a": 1}', as_csv=False) == [{"a": 1}]
    assert parse_input('[{"a": 1}, {"a": 2}]', as_csv=False) == [{"a": 1}, {"a": 2}]
    assert parse_input("a;b\n1;2", as_csv=True) == [{"a": "1", "b": "2"}]


@pytest.mark.parametrize("sep", [",", ";", "\t", "|"])
def test_parse_csv_detects_delimiter(sep):
    raw = f"id{sep}source\n1{sep}a\n2{sep}b\n"
    assert parse_csv(raw) == [{"id": "1", "source": "a"}, {"id": "2", "source": "b"}]


def test_parse_csv_quoted_header_with_other_delimiter_inside():
    assert parse_csv('"last, first";x\n"a, b";1\n') == [{"last, first": "a, b", "x": "1"}]


def test_parse_csv_rejects_duplicate_headers():
    with pytest.raises(ValueError, match="repetidas"):
        parse_csv("a;a\n1;2\n")


def test_parse_csv_wraps_csv_error():
    with pytest.raises(ValueError, match="CSV inválido"):
        parse_csv("a,b\n" + "x" * 200_000 + ",1\n")


def test_parse_pasted_text_json_scalar_and_csv_and_errors():
    with pytest.raises(ValueError, match="objeto"):
        parse_pasted_text("[1, 2]")
    with pytest.raises(ValueError, match="vazia"):
        parse_pasted_text("[]")
    assert parse_pasted_text("a,b\n1,2") == [{"a": "1", "b": "2"}]
    with pytest.raises(ValueError, match="JSON inválido"):
        parse_pasted_text("{oops")
    with pytest.raises(ValueError, match="CSV sem linhas"):
        parse_pasted_text("only,header")


VALID_RECORD = {
    "id": "1",
    "source": "mastodon",
    "url": "https://example.com/1",
    "interactions": [{"author": "a", "created_at": "2026-10-19T14:32:00Z"}],
}


def test_validate_input_accepts_object_and_list():
    from src.services.ingestion import validate_input

    assert validate_input([VALID_RECORD])[1] == []
    assert validate_input([VALID_RECORD, VALID_RECORD])[1] == []


def test_validate_input_reports_record_index():
    from src.services.ingestion import validate_input

    _, errors = validate_input([VALID_RECORD, {"id": "2"}])
    assert errors and all(e.startswith("registro 2:") for e in errors)


def test_validate_input_rejects_empty_list():
    from src.services.ingestion import validate_input

    assert validate_input([])[1]


def test_validate_input_csv_decodes_json_cells_and_drops_empty():
    import json

    from src.services.ingestion import parse_pasted_text_with_format, validate_input

    csv_text = "id,source,url,reference_period,interactions\n"
    csv_text += f'1,mastodon,https://example.com/1,,"{json.dumps(VALID_RECORD["interactions"]).replace(chr(34), chr(34) * 2)}"\n'
    data, as_csv = parse_pasted_text_with_format(csv_text)
    assert as_csv
    normalized, errors = validate_input(data, as_csv)
    assert errors == []
    assert "reference_period" not in normalized[0]


def test_validate_input_csv_without_interactions_fails():
    from src.services.ingestion import validate_input

    assert validate_input([{"id": "1", "source": "mastodon", "url": "https://example.com/1"}], True)[1]


def test_default_webhook_url_is_used_when_none_given(monkeypatch):
    captured = {}

    class Resp:
        status_code = 200

    def fake_post(url, json, timeout):
        captured["url"] = url
        return Resp()

    monkeypatch.setattr(ingestion.requests, "post", fake_post)
    send_to_ingestion({"ok": 1})
    assert captured["url"] == ingestion.N8N_INGESTION_WEBHOOK_URL


def test_default_webhook_url_falls_back_to_base_url_and_path(monkeypatch):
    import importlib

    from src import config

    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)  # ignora o .env local do desenvolvedor
    for var in ("N8N_BASE_URL", "N8N_INGESTION_WEBHOOK_PATH", "N8N_INGESTION_WEBHOOK_URL"):
        monkeypatch.delenv(var, raising=False)
    try:
        reloaded = importlib.reload(config)
        assert reloaded.N8N_INGESTION_WEBHOOK_URL == "http://localhost:5678/webhook/ingestion"
    finally:
        monkeypatch.undo()
        importlib.reload(config)


@pytest.mark.parametrize(
    "record",
    [{"id": "1"}, {**VALID_RECORD, "source": "twitter"}, {**VALID_RECORD, "url": "nope"}, {**VALID_RECORD, "x": 1}],
)
def test_validate_input_rejects_records_outside_schema(record):
    from src.services.ingestion import validate_input

    assert validate_input([record])[1]
