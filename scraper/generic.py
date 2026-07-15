import re

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