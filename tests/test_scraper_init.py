import pytest

import scraper
from scraper import ScrapeResult, scrape_url


def test_scrape_url_success_returns_populated_result(monkeypatch):
    monkeypatch.setattr(
        scraper, "scrape_generic", lambda url: (49.95, True, "Widget")
    )

    result = scrape_url("https://example.com/product")

    assert result == ScrapeResult(price=49.95, in_stock=True, name="Widget", error=None)


def test_scrape_url_no_price_found_returns_error(monkeypatch):
    monkeypatch.setattr(scraper, "scrape_generic", lambda url: (None, None, None))

    result = scrape_url("https://example.com/product")

    assert result.price is None
    assert result.error == "No Price Found"


def test_scrape_url_never_raises_on_network_exception(monkeypatch):
    def boom(url):
        raise ConnectionError("DNS resolution failed")

    monkeypatch.setattr(scraper, "scrape_generic", boom)

    result = scrape_url("https://example.com/product")

    assert result.price is None
    assert result.in_stock is None
    assert result.name is None
    assert "DNS resolution failed" in result.error


def test_scrape_url_never_raises_on_http_error(monkeypatch):
    import requests

    def boom(url):
        raise requests.HTTPError("403 Forbidden")

    monkeypatch.setattr(scraper, "scrape_generic", boom)

    result = scrape_url("https://example.com/product")

    assert result.error == "403 Forbidden"

def test_scrape_url_routes_officeworks_domain_to_its_parser(monkeypatch):
    monkeypatch.setattr(
        scraper, "scrape_generic", lambda url: (999.0, True, "Should Not Be Called")
    )
    monkeypatch.setitem(
        scraper.SITE_PARSERS, "www.officeworks.com.au", lambda url: (6.75, None, "J.Burrows Copy Paper"),
    )
    result = scrape_url("https://www.officeworks.com.au/shop/officeworks/p/test")

    assert result == ScrapeResult(price=6.75, in_stock=None, name="J.Burrows Copy Paper", error=None)


def test_scrape_url_uses_generic_for_unknown_domain(monkeypatch):
    monkeypatch.setattr(
        scraper, "scrape_generic", lambda url: (49.95, True, "Widget")
    )

    result = scrape_url("https://example.com/product")

    assert result == ScrapeResult(price=49.95, in_stock=True, name="Widget", error=None)