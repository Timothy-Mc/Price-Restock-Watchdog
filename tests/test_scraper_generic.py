import pytest

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