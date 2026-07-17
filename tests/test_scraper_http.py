import pytest
import requests

from scraper import http


class _FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def test_fetch_html_returns_response_text(monkeypatch):
    monkeypatch.setattr(
        requests.Session, "get", lambda self, url, timeout: _FakeResponse("<html>ok</html>")
    )

    assert http.fetch_html("https://example.com/product") == "<html>ok</html>"


def test_fetch_html_sets_a_user_agent_header(monkeypatch):
    captured = {}

    def fake_get(self, url, timeout):
        captured["user_agent"] = self.headers.get("User-Agent")
        return _FakeResponse("<html></html>")

    monkeypatch.setattr(requests.Session, "get", fake_get)

    http.fetch_html("https://example.com/product")

    assert captured["user_agent"] in http.USER_AGENTS


def test_fetch_html_raises_on_http_error(monkeypatch):
    monkeypatch.setattr(
        requests.Session, "get", lambda self, url, timeout: _FakeResponse("", status_code=403)
    )

    with pytest.raises(requests.HTTPError):
        http.fetch_html("https://example.com/product")
