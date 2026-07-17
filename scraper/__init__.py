import logging
from dataclasses import dataclass
from urllib.parse import urlparse

from scraper.generic import scrape_generic
from scraper.parsers import officeworks

logger = logging.getLogger(__name__)

@dataclass
class ScrapeResult:
    price: float | None
    in_stock: bool | None
    name: str | None
    error: str | None

SITE_PARSERS = {
    "www.officeworks.com.au": officeworks.scrape,
}

def scrape_url(url) -> ScrapeResult:
    domain = urlparse(url).netloc
    parser = SITE_PARSERS.get(domain, scrape_generic)
    
    try:
        price, in_stock, name = parser(url)
    except Exception as exc:
        logger.error("Scrape failed for %s: %s", domain, exc)
        return ScrapeResult(price=None, in_stock=None, name=None, error=str(exc))
    
    if price is None:
        return ScrapeResult(price=None, in_stock=None, name=None, error="No Price Found")
    
    logger.info("Scraped %s: price=%s in_stock=%s", domain, price, in_stock)
    return ScrapeResult(price=price, in_stock=in_stock, name=name, error=None)


