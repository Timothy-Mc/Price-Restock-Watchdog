import json

from scraper import http

_STATE_MAKER = "window.__INITIAL_STATE__ = "

def scrape(url) -> tuple[float | None, bool | None, str | None]:
    html = http.fetch_html(url)

    try:
        state = _extract_state(html)
        product = state["owProduct"]["product"]
        price = float(product["edlpPrice"])
        name = product["name"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None, None, None

    return (price, None, name)

def _extract_state(html) -> dict:
    start = html.index(_STATE_MAKER) + len(_STATE_MAKER)
    
    depth = 0
    end = None

    for i in range(start, len(html)):
        if html[i] == "{":
            depth += 1
        elif html[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    if end is None:
        raise ValueError("Unbalanced braces in __INITIAL_STATE__ blob")
    

    return json.loads(html[start:end])