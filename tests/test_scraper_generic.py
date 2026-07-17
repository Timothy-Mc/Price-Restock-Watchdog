import pytest
import requests
from bs4 import BeautifulSoup

from scraper import generic


def test_parse_price_with_valid_price():
    assert generic._parse_price("$1,299.99 AUD") == 1299.99
    assert generic._parse_price("AUD 599") == 599.0
    assert generic._parse_price("1,499") == 1499.0
    assert generic._parse_price("Price: $89") == 89.0

def test_parse_price_with_multiple_numbers_returns_first_price():
    assert generic._parse_price("Was $59.99 now $49.99") == 59.99

def test_parse_price_with_invalid_price():
    assert generic._parse_price(None) is None
    assert generic._parse_price("") is None
    assert generic._parse_price("Not a price") is None

def test_parse_availability_with_valid_values():
    assert generic._parse_availability("https://schema.org/InStock") is True
    assert generic._parse_availability("https://schema.org/OutOfStock") is False
    assert generic._parse_availability("In Stock") is True
    assert generic._parse_availability("Sold Out") is False

def test_parse_availability_with_invalid_values():
    assert generic._parse_availability(None) is None
    assert generic._parse_availability("Unknown") is None
    assert generic._parse_availability("Not a valid availability") is None


def test_try_json_ld_extracts_product_details():
    html = """
    <script type="application/ld+json">
    {
        "@type": "Product",
        "name": "Test Product",
        "offers": {
            "price": "49.95",
            "availability": "https://schema.org/InStock"
        }
    }
    </script>
    """

    soup = BeautifulSoup(html, "html.parser")

    assert generic._try_json_ld(soup) == (49.95, True, "Test Product")

def test_try_json_ld_finds_product_inside_graph():
    html = """
    <script type="application/ld+json">
    {
        "@graph": [
            {
                "@type": "Organization"
            },
            {
                "@type": "Product",
                "name": "Graph Product",
                "offers": {
                    "price": "100",
                    "availability": "https://schema.org/OutOfStock"
                }
            }
        ]
    }
    </script>
    """
    
    soup = BeautifulSoup(html, "html.parser")
    
    assert generic._try_json_ld(soup) == (100.0, False, "Graph Product")


def test_try_json_ld_uses_first_offer():
    html = """
    <script type="application/ld+json">
    {
        "@type": "Product",
        "name": "Multiple Offers Product",
        "offers": [
            {
                "price": "29.99",
                "availability": "https://schema.org/InStock"
            },
            {
                "price": "39.99",
                "availability": "https://schema.org/OutOfStock"
            }
        ]
    }
    </script>
    """

    soup = BeautifulSoup(html, "html.parser")

    assert generic._try_json_ld(soup) == (29.99, True, "Multiple Offers Product")

def test_try_json_ld_returns_none_without_offers():
    html = """
    <script type="application/ld+json">
    {
        "@type": "Product",
        "name": "No Offers Product"
    }
    </script>
    """

    soup = BeautifulSoup(html, "html.parser")

    assert generic._try_json_ld(soup) == (None, None, None)

def test_try_json_ld_no_script_tag_returns_none():
    html = "<html><body>no data here</body></html>"

    soup = BeautifulSoup(html, "html.parser")

    assert generic._try_json_ld(soup) == (None, None, None)

def test_try_json_ld_skips_malformed_json_and_uses_next_script():
    html = """
    <script type="application/ld+json">{not valid json</script>
    <script type="application/ld+json">
    {
        "@type": "Product",
        "name": "Recovered Product",
        "offers": {
            "price": "5.00",
            "availability": "https://schema.org/InStock"
        }
    }
    </script>
    """

    soup = BeautifulSoup(html, "html.parser")

    assert generic._try_json_ld(soup) == (5.00, True, "Recovered Product")

def test_try_json_ld_handles_price_as_json_number():
    html = """
    <script type="application/ld+json">
    {
        "@type": "Product",
        "name": "Numeric Price Product",
        "offers": {
            "price": 799.0,
            "availability": "https://schema.org/InStock"
        }
    }
    </script>
    """

    soup = BeautifulSoup(html, "html.parser")

    assert generic._try_json_ld(soup) == (799.0, True, "Numeric Price Product")


def test_try_meta_tags_uses_og_price():
    html = """
    <meta property="og:price:amount" content="49.95">
    <meta property="og:title" content="Test Product">
    <meta property="product:availability" content="In Stock">
    """

    soup = BeautifulSoup(html, "html.parser")

    assert generic._try_meta_tags(soup) == (
        49.95,
        True,
        "Test Product",
    )

def test_try_meta_tags_falls_back_to_product_price():
    html = """
    <meta property="product:price:amount" content="19.99">
    <meta property="og:title" content="Test Product">
    """

    soup = BeautifulSoup(html, "html.parser")

    assert generic._try_meta_tags(soup) == (
        19.99,
        None,
        "Test Product",
    )

def test_try_meta_tags_returns_none_when_no_meta_tags():
    soup = BeautifulSoup("<html></html>", "html.parser")

    assert generic._try_meta_tags(soup) == (
        None,
        None,
        None,
    )

def test_try_meta_tags_missing_availability():
    html = """
    <meta property="og:price:amount" content="99.95">
    """

    soup = BeautifulSoup(html, "html.parser")

    assert generic._try_meta_tags(soup) == (
        99.95,
        None,
        None,
    )

def test_try_meta_tags_falls_back_when_og_price_unparseable():
    html = """
    <meta property="og:price:amount" content="Contact us for pricing">
    <meta property="product:price:amount" content="29.99">
    """

    soup = BeautifulSoup(html, "html.parser")

    assert generic._try_meta_tags(soup) == (
        29.99,
        None,
        None,
    )

def test_try_css_heuristics_extracts_price_and_title():
    html = """
    <html>
        <head>
            <title>Test Product</title>
        </head>
        <body>
            <div class="product-price">$34.50</div>
        </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")

    result = generic._try_css_heuristics(soup)

    assert result == (
        34.50,
        None,
        "Test Product",
    )

def test_try_css_heuristics_without_price_returns_title():
    html = """
    <html>
        <head>
            <title>Product Without Price</title>
        </head>
        <body>
            <div class="cost">$50</div>
        </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")

    result = generic._try_css_heuristics(soup)

    assert result == (
        None,
        None,
        "Product Without Price",
    )


class _FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def test_scrape_generic_prefers_json_ld_over_other_strategies(monkeypatch):
    html = """
    <html><head>
    <meta property="og:price:amount" content="999.00" />
    <script type="application/ld+json">
    {"@type": "Product", "name": "Widget", "offers": {"price": "49.95", "availability": "https://schema.org/InStock"}}
    </script>
    </head><body><div class="price">1.00</div></body></html>
    """
    monkeypatch.setattr(requests.Session, "get", lambda self, url, timeout: _FakeResponse(html))

    price, in_stock, name = generic.scrape_generic("https://example.com/product")

    assert price == 49.95
    assert in_stock is True
    assert name == "Widget"

def test_scrape_generic_falls_back_to_meta_tags(monkeypatch):
    html = '<html><head><meta property="og:price:amount" content="59.99" /></head><body></body></html>'
    monkeypatch.setattr(requests.Session, "get", lambda self, url, timeout: _FakeResponse(html))

    price, in_stock, name = generic.scrape_generic("https://example.com/product")

    assert price == 59.99

def test_scrape_generic_falls_back_to_css_heuristics(monkeypatch):
    html = '<html><body><div class="price">$12.00</div></body></html>'
    monkeypatch.setattr(requests.Session, "get", lambda self, url, timeout: _FakeResponse(html))

    price, in_stock, name = generic.scrape_generic("https://example.com/product")

    assert price == 12.00

def test_scrape_generic_returns_none_tuple_when_no_strategy_matches(monkeypatch, caplog):
    html = "<html><body>nothing here</body></html>"
    monkeypatch.setattr(requests.Session, "get", lambda self, url, timeout: _FakeResponse(html))

    price, in_stock, name = generic.scrape_generic("https://example.com/product")

    assert (price, in_stock, name) == (None, None, None)
    assert "example.com" in caplog.text