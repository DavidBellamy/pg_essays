import json
import logging
import os

from sklearn.feature_extraction.text import TfidfVectorizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

TEXTS_CACHE_FILE = "essay_texts.json"
DOCS_DIR = "docs"
OUTPUT_FILE = os.path.join(DOCS_DIR, "topic_analysis.json")


def load_essay_texts(path=TEXTS_CACHE_FILE):
    """Load essay texts from the cached JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def compute_tfidf(texts, max_features=1000):
    """Compute TF-IDF matrix and return vectorizer + matrix."""
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words="english",
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    return vectorizer, tfidf_matrix


def extract_keywords_per_essay(vectorizer, tfidf_matrix, urls, top_n=10):
    """Extract top N keywords for each essay."""
    feature_names = vectorizer.get_feature_names_out()
    keywords = {}
    for i, url in enumerate(urls):
        row = tfidf_matrix[i].toarray().flatten()
        top_indices = row.argsort()[-top_n:][::-1]
        keywords[url] = [
            {"word": feature_names[j], "score": round(float(row[j]), 4)}
            for j in top_indices
            if row[j] > 0
        ]
    return keywords


def extract_corpus_themes(vectorizer, tfidf_matrix, top_n=20):
    """Extract top N themes across the entire corpus by mean TF-IDF score."""
    feature_names = vectorizer.get_feature_names_out()
    mean_scores = tfidf_matrix.mean(axis=0).A1
    top_indices = mean_scores.argsort()[-top_n:][::-1]
    return [
        {"word": feature_names[i], "score": round(float(mean_scores[i]), 4)}
        for i in top_indices
    ]


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)

    texts_by_url = load_essay_texts()
    urls = list(texts_by_url.keys())
    texts = list(texts_by_url.values())

    # Filter out empty texts
    pairs = [(u, t) for u, t in zip(urls, texts) if t and t.strip()]
    if not pairs:
        logger.warning("No essay texts found. Run scrape_essays.py first.")
        return
    urls, texts = zip(*pairs)
    urls, texts = list(urls), list(texts)

    logger.info("Analyzing %d essays", len(texts))
    vectorizer, tfidf_matrix = compute_tfidf(texts)

    keywords = extract_keywords_per_essay(vectorizer, tfidf_matrix, urls)
    themes = extract_corpus_themes(vectorizer, tfidf_matrix)

    result = {
        "keywords_per_essay": keywords,
        "corpus_themes": themes,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2)
    logger.info("Wrote topic analysis to %s", OUTPUT_FILE)


if __name__ == "__main__":
    main()
