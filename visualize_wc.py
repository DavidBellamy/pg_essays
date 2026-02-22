import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CSV_INPUT = "pg_essays_wc.csv"
DOCS_DIR = "docs"


def load_data(path=CSV_INPUT):
    """Load essay CSV and parse dates."""
    df = pd.read_csv(path)
    if "Publication Date" in df.columns:
        df["Publication Date"] = pd.to_datetime(df["Publication Date"], errors="coerce")
    return df


def plot_histogram(df, path):
    """Plot a histogram of word counts."""
    total_wc = df["Word Count"].sum()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df["Word Count"], bins=30, alpha=0.7, edgecolor="black")
    ax.set_title(
        f"Histogram of Word Counts in Paul Graham Essays\n"
        f"Total word count = {total_wc:,}"
    )
    ax.set_xlabel("Word Count")
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def plot_word_count_over_time(df, path):
    """Scatter plot of word count vs publication date with trend line."""
    dated = df.dropna(subset=["Publication Date"]).copy()
    if dated.empty:
        return

    dated = dated.sort_values("Publication Date")
    x_dates = dated["Publication Date"]
    y_wc = dated["Word Count"]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(x_dates, y_wc, alpha=0.5, s=20)

    # Trend line
    x_numeric = x_dates.map(pd.Timestamp.toordinal).astype(float)
    if len(x_numeric) > 1:
        coeffs = np.polyfit(x_numeric, y_wc, 1)
        trend = np.poly1d(coeffs)
        ax.plot(x_dates, trend(x_numeric), color="red", linewidth=2, label="Trend")
        ax.legend()

    ax.set_title("Paul Graham Essay Word Counts Over Time")
    ax.set_xlabel("Publication Date")
    ax.set_ylabel("Word Count")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def plot_cumulative_word_count(df, path):
    """Cumulative word count line chart over time."""
    dated = df.dropna(subset=["Publication Date"]).copy()
    if dated.empty:
        return

    dated = dated.sort_values("Publication Date")
    dated["Cumulative Words"] = dated["Word Count"].cumsum()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(dated["Publication Date"], dated["Cumulative Words"], linewidth=2)
    ax.fill_between(
        dated["Publication Date"], dated["Cumulative Words"], alpha=0.2
    )
    ax.set_title("Cumulative Word Count of Paul Graham Essays")
    ax.set_xlabel("Publication Date")
    ax.set_ylabel("Cumulative Word Count")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)
    df = load_data()

    plot_histogram(df, os.path.join(DOCS_DIR, "word_count_histogram.png"))

    if "Publication Date" in df.columns:
        plot_word_count_over_time(
            df, os.path.join(DOCS_DIR, "word_count_over_time.png")
        )
        plot_cumulative_word_count(
            df, os.path.join(DOCS_DIR, "cumulative_word_count.png")
        )


if __name__ == "__main__":
    main()
