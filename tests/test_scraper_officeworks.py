from scraper import http
from scraper.parsers import officeworks

_HAPPY_PATH_HTML = """
<html><body>
<script>
window.__INITIAL_STATE__ = {"app":{"isFloating":null},"owProduct":{"product":{"sku":"TESTSKU1","name":"Test Copy Paper 500 Sheet Ream","edlpPrice":"12.34","ranged":{"inStore":true,"online":true}}},"owProductAvailability":{"availabilities":{}}};
</script>
</body></html>
"""

_MISSING_MARKER_HTML = "<html><body>no state blob here</body></html>"

_MALFORMED_JSON_HTML = """
<script>
window.__INITIAL_STATE__ = {"owProduct": {"product": {"edlpPrice": "12.34" "name": "Missing Comma"}}};
</script>
"""

_MISSING_KEYS_HTML = """
<script>
window.__INITIAL_STATE__ = {"owProduct": {"product": {"sku": "TESTSKU1"}}};
</script>
"""

def test_scrape_extracts_price_and_name_from_state_blob(monkeypatch):
    monkeypatch.setattr(http, "fetch_html", lambda url: _HAPPY_PATH_HTML)

    price, in_stock, name = officeworks.scrape("https://www.officeworks.com.au/shop/officeworks/p/test")

    assert price == 12.34
    assert in_stock is None
    assert name == "Test Copy Paper 500 Sheet Ream"


def test_scrape_returns_none_tuple_when_state_marker_missing(monkeypatch):
    monkeypatch.setattr(http, "fetch_html", lambda url: _MISSING_MARKER_HTML)

    assert officeworks.scrape("https://www.officeworks.com.au/shop/officeworks/p/test") == (None, None, None)


def test_scrape_returns_none_tuple_on_malformed_json(monkeypatch):
    monkeypatch.setattr(http, "fetch_html", lambda url: _MALFORMED_JSON_HTML)

    assert officeworks.scrape("https://www.officeworks.com.au/shop/officeworks/p/test") == (None, None, None)


def test_scrape_returns_none_tuple_when_price_key_missing(monkeypatch):
    monkeypatch.setattr(http, "fetch_html", lambda url: _MISSING_KEYS_HTML)

    assert officeworks.scrape("https://www.officeworks.com.au/shop/officeworks/p/test") == (None, None, None)