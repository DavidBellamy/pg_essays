import os
from datetime import timezone

import pandas as pd
from feedgen.feed import FeedGenerator

CSV_INPUT = "pg_essays_wc.csv"
DOCS_DIR = "docs"
OUTPUT_FILE = os.path.join(DOCS_DIR, "feed.xml")


def build_feed(df, max_entries=20):
    """Build an Atom feed from the essay DataFrame."""
    fg = FeedGenerator()
    fg.id("https://paulgraham.com/articles.html")
    fg.title("Paul Graham Essays — Word Count Tracker")
    fg.subtitle("Latest essays from paulgraham.com with word count stats")
    fg.link(href="https://paulgraham.com/articles.html", rel="alternate")
    fg.language("en")

    # Sort by date descending, take top N
    dated = df.dropna(subset=["Publication Date"]).copy()
    dated = dated.sort_values("Publication Date", ascending=False).head(max_entries)

    for _, row in dated.iterrows():
        fe = fg.add_entry()
        fe.id(row["Essay Link"])
        fe.title(row["Essay Title"])
        fe.link(href=row["Essay Link"])
        fe.summary(f"Word count: {row['Word Count']:,}")
        pub = row["Publication Date"]
        if pd.notna(pub):
            fe.published(pub.replace(tzinfo=timezone.utc))
            fe.updated(pub.replace(tzinfo=timezone.utc))

    return fg


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)

    df = pd.read_csv(CSV_INPUT)
    if "Publication Date" in df.columns:
        df["Publication Date"] = pd.to_datetime(
            df["Publication Date"], errors="coerce"
        )

    fg = build_feed(df)
    fg.atom_file(OUTPUT_FILE)
    print(f"Feed written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
