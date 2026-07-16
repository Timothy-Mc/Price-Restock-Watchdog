import re
import json
from bs4 import BeautifulSoup

def _parse_price(text: str | None) -> float | None:
    if text is None:
        return None

    match = re.search(r'\d[\d,]*\.?\d*', text)

    if not match:
        return None
    
    cleaned = match.group(0).replace(',', '')

    try:
        return float(cleaned)
    except ValueError:
        return None
    
def _parse_availability(value: str | None) -> bool | None:
    if value is None:
        return None
    
    normalise = value.strip().lower()

    if normalise.endswith("/instock"):
        return True
    
    if normalise.endswith("/outofstock"):
        return False
    
    available_terms = {
        "in stock",
        "instock",
        "available",
        "availability: in stock",
        "yes",
    }

    unavailable_terms = {
        "out of stock",
        "outofstock",
        "sold out",
        "unavailable",
        "discontinued",
        "availability: out of stock",
        "no",
    }

    if normalise in available_terms:
        return True
    
    if normalise in unavailable_terms:
        return False
    
    return None

def _try_json_ld(soup) -> tuple[float | None, bool | None, str | None]:
    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        try:
            data = json.loads(script.string)

        except (json.JSONDecodeError, TypeError):
            continue

        products = []

        if isinstance(data, dict) and data.get("@type") == "Product":
            products.append(data)

        elif isinstance(data, dict) and "@graph" in data:
            for item in data["@graph"]:
                if isinstance(item, dict) and item.get("@type") == "Product":
                    products.append(item)

        for product in products:
            offers = product.get("offers", {})

            if not offers:
                continue

            if isinstance(offers, list):
                offers = offers[0]

            if not isinstance(offers, dict):
                continue

            price = _parse_price(offers.get("price"))
            availability = _parse_availability(offers.get("availability"))
            name = product.get("name")

            return price, availability, name
        
    return None, None, None

def _try_meta_tags(soup) -> tuple[float | None, bool | None, str | None]:
    price = None

    for property_tag in ["og:price:amount", "product:price:amount"]:
        price_tag = soup.find("meta", property=property_tag)
        if not price_tag:
            continue

        parsed_price = _parse_price(price_tag.get("content"))

        if parsed_price is not None:
            price = parsed_price
            break

    name_tag = soup.find("meta", property="og:title")
    name = name_tag.get("content") if name_tag else None

    availability_tag = soup.find("meta", property="product:availability")
    in_stock = (_parse_availability(availability_tag.get("content")) if availability_tag else None)

    return (price, in_stock, name)