import pytest
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