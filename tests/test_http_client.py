import requests

from src.utils import http_client


class FakeResponse:
    def __init__(self, status_code: int, headers: dict[str, str] | None = None):
        self.status_code = status_code
        self.headers = headers or {}

    def json(self):
        return {"ok": True}


def test_http_post_retries_503_with_dynamic_attempt_numbers(monkeypatch, capsys):
    responses = [
        FakeResponse(503),
        FakeResponse(503),
        FakeResponse(200),
    ]
    waits: list[int] = []

    monkeypatch.setattr(
        http_client.requests,
        "post",
        lambda *args, **kwargs: responses.pop(0),
    )
    monkeypatch.setattr(http_client.time, "sleep", waits.append)

    result = http_client.http_post("https://example.test", {}, {}, retries=2)

    assert result == {"ok": True}
    assert waits == [
        http_client.RETRY_BACKOFF_SECONDS,
        http_client.RETRY_BACKOFF_SECONDS * 2,
    ]
    assert capsys.readouterr().out.splitlines() == [
        "  HTTP 503 na tentativa 1/3: limite ou instabilidade no provedor; "
        "aguardando 5s antes da tentativa 2/3...",
        "  HTTP 503 na tentativa 2/3: limite ou instabilidade no provedor; "
        "aguardando 10s antes da tentativa 3/3...",
    ]


def test_http_post_honors_retry_after_without_exceeding_cap(monkeypatch):
    responses = [
        FakeResponse(
            429,
            {"Retry-After": str(http_client.MAX_RETRY_WAIT_SECONDS + 100)},
        ),
        FakeResponse(200),
    ]
    waits: list[int] = []

    monkeypatch.setattr(
        http_client.requests,
        "post",
        lambda *args, **kwargs: responses.pop(0),
    )
    monkeypatch.setattr(http_client.time, "sleep", waits.append)

    http_client.http_post("https://example.test", {}, {}, retries=1)

    assert waits == [http_client.MAX_RETRY_WAIT_SECONDS]


def test_http_post_raises_after_retry_limit(monkeypatch):
    response = FakeResponse(503)
    waits: list[int] = []

    monkeypatch.setattr(
        http_client.requests,
        "post",
        lambda *args, **kwargs: response,
    )
    monkeypatch.setattr(http_client.time, "sleep", waits.append)

    try:
        http_client.http_post("https://example.test", {}, {}, retries=1)
    except RuntimeError as exc:
        assert "HTTP 503" in str(exc)
    else:
        raise AssertionError("http_post deveria falhar após esgotar retries")

    assert waits == [http_client.RETRY_BACKOFF_SECONDS]
