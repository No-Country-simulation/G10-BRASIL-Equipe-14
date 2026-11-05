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


def test_parse_input_dispatches_by_format():
    assert parse_input('{"a": 1}', as_csv=False) == {"a": 1}
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
    assert parse_pasted_text("42") == 42
    assert parse_pasted_text("a,b\n1,2") == [{"a": "1", "b": "2"}]
    with pytest.raises(ValueError, match="JSON inválido"):
        parse_pasted_text("{oops")
    with pytest.raises(ValueError, match="CSV sem linhas"):
        parse_pasted_text("only,header")
