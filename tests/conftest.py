import pandas as pd
import pytest
import responses

SAMPLE_ARTICLES_HTML = """
<html><body>
<table>
  <tr><td><a href="think.html">How to Think for Yourself</a></td></tr>
  <tr><td><a href="read.html">How to Read</a></td></tr>
  <tr><td><a href="think.html">How to Think for Yourself</a></td></tr>
  <tr><td><a href="index.html">Home</a></td></tr>
  <tr><td><a href="photo.jpg">A Photo</a></td></tr>
  <tr><td><a href="">Empty</a></td></tr>
</table>
</body></html>
"""

SAMPLE_ESSAY_HTML = """
<html><body>
<font size="2" face="verdana">
July 2023

The first step is to understand that thinking for yourself is not about being
contrarian. It means looking at evidence and deciding what you think is true,
rather than just going along with whatever everyone else thinks.

This is harder than it sounds, because the social pressure to conform is strong.
Even people who think of themselves as independent thinkers are often just going
along with a different group. True independent thinking means being willing to
consider ideas that would shock your own side.
</font>
</body></html>
"""

SAMPLE_ESSAY_YEAR_ONLY_HTML = """
<html><body>
<font size="2" face="verdana">
1993

Programming languages are a topic I have strong opinions about.
</font>
</body></html>
"""

SAMPLE_ESSAY_NO_DATE_HTML = """
<html><body>
<font size="2" face="verdana">
This essay has no date information whatsoever in its body text.
Absolutely none. Just text about startups and programming.
</font>
</body></html>
"""

SAMPLE_ESSAY_REVISION_HTML = """
<html><body>
<font size="2" face="verdana">
April 2001, rev. April 2003

This essay was originally written in April 2001 and revised in April 2003.
</font>
</body></html>
"""


@pytest.fixture
def sample_df():
    """A sample DataFrame mimicking pg_essays_wc.csv."""
    return pd.DataFrame({
        "Essay Title": ["Essay A", "Essay B", "Essay C"],
        "Essay Link": [
            "http://www.paulgraham.com/a.html",
            "http://www.paulgraham.com/b.html",
            "http://www.paulgraham.com/c.html",
        ],
        "Word Count": [1000, 2500, 500],
        "Publication Date": pd.to_datetime([
            "2020-01-01", "2021-06-01", "2022-03-01"
        ]),
    })


@pytest.fixture
def mock_articles_page():
    """Set up responses mock for the articles page."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "https://paulgraham.com/articles.html",
            body=SAMPLE_ARTICLES_HTML,
            status=200,
        )
        yield rsps


@pytest.fixture
def mock_essay_page():
    """Set up responses mock for a single essay."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "http://www.paulgraham.com/think.html",
            body=SAMPLE_ESSAY_HTML,
            status=200,
        )
        yield rsps
