import responses

from scrape_essays import (
    create_session,
    deduplicate_links,
    extract_publication_date,
    fetch_essay_content,
    fetch_essay_links,
)
from tests.conftest import (
    SAMPLE_ARTICLES_HTML,
    SAMPLE_ESSAY_HTML,
    SAMPLE_ESSAY_NO_DATE_HTML,
    SAMPLE_ESSAY_REVISION_HTML,
    SAMPLE_ESSAY_YEAR_ONLY_HTML,
)


def test_create_session_retries():
    session = create_session()
    adapter = session.get_adapter("http://example.com")
    assert adapter.max_retries.total == 3
    assert 429 in adapter.max_retries.status_forcelist


def test_fetch_essay_links(mock_articles_page):
    session = create_session()
    links = fetch_essay_links(session)
    titles = [t for t, _ in links]
    urls = [u for _, u in links]
    assert "How to Think for Yourself" in titles
    assert "How to Read" in titles
    # All URLs should be full URLs
    assert all(u.startswith("http") for u in urls)


def test_fetch_essay_links_skips_non_html(mock_articles_page):
    session = create_session()
    links = fetch_essay_links(session)
    urls = [u for _, u in links]
    # photo.jpg and empty href should not appear
    assert not any("photo.jpg" in u for u in urls)
    # index.html should be skipped
    assert not any(u.endswith("/index.html") for u in urls)


@responses.activate
def test_fetch_essay_content():
    responses.add(
        responses.GET,
        "http://www.paulgraham.com/think.html",
        body=SAMPLE_ESSAY_HTML,
        status=200,
    )
    session = create_session()
    text = fetch_essay_content(session, "http://www.paulgraham.com/think.html")
    assert "thinking for yourself" in text.lower()
    assert len(text.split()) > 10


@responses.activate
def test_fetch_essay_content_error():
    responses.add(
        responses.GET,
        "http://www.paulgraham.com/missing.html",
        body="Not Found",
        status=404,
    )
    session = create_session()
    text = fetch_essay_content(session, "http://www.paulgraham.com/missing.html")
    assert text == ""


def test_extract_publication_date_month_year():
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(SAMPLE_ESSAY_HTML, "html.parser")
    body_text = soup.find("body").get_text(separator=" ", strip=True)
    date = extract_publication_date(body_text)
    assert date == "2023-07-01"


def test_extract_publication_date_revision():
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(SAMPLE_ESSAY_REVISION_HTML, "html.parser")
    body_text = soup.find("body").get_text(separator=" ", strip=True)
    date = extract_publication_date(body_text)
    assert date == "2001-04-01"


def test_extract_publication_date_year_only():
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(SAMPLE_ESSAY_YEAR_ONLY_HTML, "html.parser")
    body_text = soup.find("body").get_text(separator=" ", strip=True)
    date = extract_publication_date(body_text)
    assert date == "1993-01-01"


def test_extract_publication_date_missing():
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(SAMPLE_ESSAY_NO_DATE_HTML, "html.parser")
    body_text = soup.find("body").get_text(separator=" ", strip=True)
    date = extract_publication_date(body_text)
    assert date is None


def test_deduplicate_links():
    essays = [
        ("A", "http://www.paulgraham.com/a.html"),
        ("B", "http://www.paulgraham.com/b.html"),
        ("A duplicate", "http://www.paulgraham.com/a.html"),
        ("C", "http://www.paulgraham.com/c.html"),
    ]
    result = deduplicate_links(essays)
    assert len(result) == 3
    urls = [u for _, u in result]
    assert urls.count("http://www.paulgraham.com/a.html") == 1
    # First title should be kept
    assert result[0][0] == "A"
