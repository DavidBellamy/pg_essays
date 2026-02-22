import json
import logging
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

ARTICLES_URL = "https://paulgraham.com/articles.html"
DATES_CACHE_FILE = "publication_dates.json"
TEXTS_CACHE_FILE = "essay_texts.json"
CSV_OUTPUT = "pg_essays_wc.csv"

MONTH_NAMES = (
    "January|February|March|April|May|June|"
    "July|August|September|October|November|December"
)
MONTH_TO_NUM = {
    "January": "01", "February": "02", "March": "03", "April": "04",
    "May": "05", "June": "06", "July": "07", "August": "08",
    "September": "09", "October": "10", "November": "11", "December": "12",
}


def create_session():
    """Return a requests.Session with retry logic."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_essay_links(session, url=ARTICLES_URL):
    """Parse the articles page and return [(title, url), ...]."""
    logger.info("Fetching article list from %s", url)
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    essays = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        title = a.get_text(strip=True)
        if not title or not href.endswith(".html"):
            continue
        if href in ("articles.html", "index.html"):
            continue
        if href.startswith("http"):
            link = href
        else:
            link = "http://www.paulgraham.com/" + href
        essays.append((title, link))

    logger.info("Found %d essay links", len(essays))
    return essays


def deduplicate_links(essays):
    """Remove duplicate URLs, keeping the first occurrence."""
    seen = set()
    unique = []
    for title, link in essays:
        if link not in seen:
            seen.add(link)
            unique.append((title, link))
    duplicates_removed = len(essays) - len(unique)
    if duplicates_removed:
        logger.info("Removed %d duplicate links", duplicates_removed)
    return unique


def fetch_essay_content(session, url):
    """Fetch a single essay and return its body text."""
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        if soup.find("body"):
            return soup.find("body").get_text(separator=" ", strip=True)
        return soup.get_text(separator=" ", strip=True)
    except requests.RequestException:
        logger.exception("Failed to fetch %s", url)
        return ""


def extract_publication_date(body_text):
    """Extract a publication date from essay body text.

    Returns a date string (YYYY-MM-01 or YYYY-01-01) or None.
    """
    if not body_text:
        return None

    snippet = body_text[:500]

    # Look for "Month YYYY" pattern (take the first match)
    match = re.search(rf"({MONTH_NAMES})\s+(\d{{4}})", snippet)
    if match:
        month_str, year = match.group(1), match.group(2)
        return f"{year}-{MONTH_TO_NUM[month_str]}-01"

    # Fallback: bare four-digit year
    match = re.search(r"\b(\d{4})\b", snippet)
    if match:
        return f"{match.group(1)}-01-01"

    return None


def query_wayback_date(session, url):
    """Query the Wayback Machine CDX API for the earliest snapshot date."""
    cdx_url = (
        "https://web.archive.org/cdx/search/cdx"
        f"?url={url}&output=json&limit=1&fl=timestamp"
    )
    try:
        resp = session.get(cdx_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if len(data) > 1:
            ts = data[1][0]  # first result after header
            return f"{ts[:4]}-{ts[4:6]}-01"
    except Exception:
        logger.debug("Wayback query failed for %s", url)
    return None


def load_dates_cache():
    """Load cached publication dates from disk."""
    try:
        with open(DATES_CACHE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_dates_cache(cache):
    """Save publication dates cache to disk."""
    with open(DATES_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def main():
    session = create_session()

    essays = fetch_essay_links(session)
    essays = deduplicate_links(essays)

    dates_cache = load_dates_cache()

    # Load existing texts cache if present
    try:
        with open(TEXTS_CACHE_FILE, "r") as f:
            texts_cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        texts_cache = {}

    data = []
    for title, link in tqdm(essays, desc="Fetching essays"):
        body_text = fetch_essay_content(session, link)
        texts_cache[link] = body_text
        word_count = len(body_text.split())

        # Resolve publication date
        if link in dates_cache:
            pub_date = dates_cache[link]
        else:
            pub_date = extract_publication_date(body_text)
            if pub_date is None:
                pub_date = query_wayback_date(session, link)
            dates_cache[link] = pub_date

        data.append({
            "Essay Title": title,
            "Essay Link": link,
            "Word Count": word_count,
            "Publication Date": pub_date,
        })

    save_dates_cache(dates_cache)

    # Save essay texts for downstream analysis
    with open(TEXTS_CACHE_FILE, "w") as f:
        json.dump(texts_cache, f)
    logger.info("Saved essay texts to %s", TEXTS_CACHE_FILE)

    df = pd.DataFrame(data)
    df.drop_duplicates(subset="Essay Link", keep="first", inplace=True)
    df.to_csv(CSV_OUTPUT, index=False, encoding="utf-8")
    logger.info("Wrote %d essays to %s", len(df), CSV_OUTPUT)


if __name__ == "__main__":
    main()
