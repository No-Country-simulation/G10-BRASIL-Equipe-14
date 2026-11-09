import json
from types import SimpleNamespace

import pytest
import requests

from src.config import MAX_UPLOAD_FILE_SIZE_BYTES

VALID_RECORD = {
    "id": "1",
    "source": "mastodon",
    "url": "https://example.com/1",
    "interactions": [{"author": "a", "created_at": "2026-10-19T14:32:00Z"}],
}


@pytest.fixture(scope="module")
def view():
    from src.views import ingestion

    return ingestion


def make_file(name: str, content: bytes | str, size: int | None = None):
    raw = content.encode() if isinstance(content, str) else content
    return SimpleNamespace(name=name, size=len(raw) if size is None else size, getvalue=lambda: raw)


class FakeStreamlit:
    def __init__(self):
        self.messages: list[tuple[str, str]] = []

    def spinner(self, *_):
        from contextlib import nullcontext

        return nullcontext()

    def __getattr__(self, kind):
        return lambda message, *a, **k: self.messages.append((kind, message))


@pytest.fixture
def fake_st(view, monkeypatch):
    fake = FakeStreamlit()
    monkeypatch.setattr(view, "st", fake)
    return fake


# --- collect_items: validação contra o input_schema.json -------------------------------------------------


def test_collect_items_accepts_valid_json_file_and_pasted_text(view):
    files = [make_file("ok.json", json.dumps(VALID_RECORD))]
    items, errors = view.collect_items(files, json.dumps([VALID_RECORD, VALID_RECORD]))
    assert errors == []
    assert [(name, len(records)) for name, records in items] == [("ok.json", 1), ("texto colado", 2)]


@pytest.mark.parametrize("content", ["42", '"texto"', "[1, 2]", "[]", '[{"a": 1}, 3]'])
def test_collect_items_rejects_non_object_json(view, content):
    items, errors = view.collect_items([make_file("bad.json", content)], "")
    assert items == []
    assert len(errors) == 1 and "**bad.json**" in errors[0]


@pytest.mark.parametrize(
    "record",
    [
        {"id": "1"},  # faltam source, url e interactions
        {**VALID_RECORD, "source": "twitter"},  # fora do enum
        {**VALID_RECORD, "url": "não é uma url"},  # formato uri
        {**VALID_RECORD, "extra": True},  # additionalProperties: false
    ],
)
def test_collect_items_rejects_records_outside_schema(view, record):
    items, errors = view.collect_items([make_file("r.json", json.dumps(record))], "")
    assert items == []
    assert "fora do schema de entrada" in errors[0]


def test_collect_items_rejects_csv_without_interactions(view):
    csv_content = "id,source,url\n1,mastodon,https://example.com/1\n"
    items, errors = view.collect_items([make_file("r.csv", csv_content)], "")
    assert items == []
    assert "interactions" in errors[0]


def test_collect_items_reports_partial_failures_across_files(view):
    files = [
        make_file("ok.json", json.dumps(VALID_RECORD)),
        make_file("broken.json", "{oops"),
        make_file("outside_schema.json", json.dumps({"id": "1"})),
        make_file("huge.json", "{}", size=MAX_UPLOAD_FILE_SIZE_BYTES + 1),
    ]
    items, errors = view.collect_items(files, "")
    assert [name for name, _ in items] == ["ok.json"]
    assert len(errors) == 3
    assert any("broken.json" in e and "JSON inválido" in e for e in errors)
    assert any("outside_schema.json" in e for e in errors)
    assert any("huge.json" in e and "limite" in e for e in errors)


# --- send_items: status HTTP e falhas parciais -----------------------------------------------------------


def stub_send(monkeypatch, view, outcomes):
    calls = iter(outcomes)

    def fake_send(payload):
        outcome = next(calls)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(view, "send_to_ingestion", fake_send)


@pytest.mark.parametrize("status", [400, 404, 500, 503])
def test_send_items_counts_non_2xx_as_failure(view, fake_st, monkeypatch, status):
    stub_send(monkeypatch, view, [status])
    assert view.send_items([("a.json", [VALID_RECORD])]) == (0, 1)
    assert ("error", "a.json: falha no envio.") in fake_st.messages
    assert ("caption", f"Status HTTP recebido: {status}") in fake_st.messages


@pytest.mark.parametrize("status", [200, 201, 202, 204])
def test_send_items_counts_2xx_as_success(view, fake_st, monkeypatch, status):
    stub_send(monkeypatch, view, [status])
    assert view.send_items([("a.json", [VALID_RECORD])]) == (1, 0)


def test_send_items_reports_partial_failure_per_record(view, fake_st, monkeypatch):
    stub_send(monkeypatch, view, [200, 500, requests.ConnectionError("down"), 202])
    items = [("a.json", [VALID_RECORD, VALID_RECORD]), ("b.csv", [VALID_RECORD, VALID_RECORD])]
    assert view.send_items(items) == (2, 2)
    errors = [m for kind, m in fake_st.messages if kind == "error"]
    assert errors == [
        "a.json, registro 2: falha no envio.",
        "b.csv, registro 1: falha de comunicação com o serviço.",
    ]


@pytest.mark.parametrize(
    ("sent", "failed", "kind", "text"),
    [(3, 0, "success", "3 de 3"), (2, 1, "warning", "Envio parcial"), (0, 2, "error", "Nenhum registro")],
)
def test_render_send_summary(view, fake_st, sent, failed, kind, text):
    view.render_send_summary(sent, failed)
    [(shown_kind, message)] = fake_st.messages
    assert shown_kind == kind and text in message
