from analyze_topics import compute_tfidf, extract_keywords_per_essay, extract_corpus_themes


def test_compute_tfidf():
    texts = [
        "Python is a great programming language for data science",
        "Machine learning uses algorithms to learn from data",
        "Startups need to find product market fit quickly",
    ]
    vectorizer, matrix = compute_tfidf(texts, max_features=50)
    assert matrix.shape[0] == 3
    assert matrix.shape[1] > 0


def test_extract_keywords():
    texts = [
        "Python is a great programming language for data science",
        "Machine learning uses algorithms to learn from data",
    ]
    urls = ["http://example.com/a.html", "http://example.com/b.html"]
    vectorizer, matrix = compute_tfidf(texts, max_features=50)
    keywords = extract_keywords_per_essay(vectorizer, matrix, urls, top_n=5)

    assert len(keywords) == 2
    assert "http://example.com/a.html" in keywords
    for kw in keywords["http://example.com/a.html"]:
        assert "word" in kw
        assert "score" in kw


def test_extract_corpus_themes():
    texts = [
        "Python is a great programming language for data science",
        "Machine learning uses algorithms to learn from data",
        "Programming languages help us build software systems",
    ]
    vectorizer, matrix = compute_tfidf(texts, max_features=50)
    themes = extract_corpus_themes(vectorizer, matrix, top_n=5)

    assert len(themes) <= 5
    assert all("word" in t and "score" in t for t in themes)
