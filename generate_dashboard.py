import json
import os

import pandas as pd
import plotly.express as px
import plotly.io as pio

CSV_INPUT = "pg_essays_wc.csv"
TOPIC_FILE = os.path.join("docs", "topic_analysis.json")
DOCS_DIR = "docs"
OUTPUT_FILE = os.path.join(DOCS_DIR, "index.html")


def load_data():
    """Load essay CSV and topic analysis."""
    df = pd.read_csv(CSV_INPUT)
    if "Publication Date" in df.columns:
        df["Publication Date"] = pd.to_datetime(
            df["Publication Date"], errors="coerce"
        )

    topics = None
    if os.path.exists(TOPIC_FILE):
        with open(TOPIC_FILE, "r") as f:
            topics = json.load(f)

    return df, topics


def build_histogram(df):
    """Interactive histogram of word counts."""
    fig = px.histogram(
        df, x="Word Count", nbins=30,
        title="Distribution of Word Counts",
        labels={"Word Count": "Word Count", "count": "Frequency"},
    )
    fig.update_layout(bargap=0.05)
    return fig


def build_scatter(df):
    """Interactive scatter plot of word count over time."""
    dated = df.dropna(subset=["Publication Date"]).sort_values("Publication Date")
    if dated.empty:
        return None
    fig = px.scatter(
        dated, x="Publication Date", y="Word Count",
        hover_data=["Essay Title"],
        title="Word Counts Over Time",
        trendline="lowess",
    )
    return fig


def build_cumulative(df):
    """Interactive cumulative word count line chart."""
    dated = df.dropna(subset=["Publication Date"]).sort_values("Publication Date").copy()
    if dated.empty:
        return None
    dated["Cumulative Words"] = dated["Word Count"].cumsum()
    fig = px.area(
        dated, x="Publication Date", y="Cumulative Words",
        title="Cumulative Word Count Over Time",
        hover_data=["Essay Title"],
    )
    return fig


def build_themes_chart(topics):
    """Bar chart of top corpus themes."""
    if not topics or "corpus_themes" not in topics:
        return None
    themes = topics["corpus_themes"]
    tdf = pd.DataFrame(themes)
    fig = px.bar(
        tdf, x="score", y="word", orientation="h",
        title="Top 20 Corpus Themes (TF-IDF)",
        labels={"score": "Mean TF-IDF Score", "word": "Theme"},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def build_essay_table(df):
    """HTML table of all essays, sortable via simple JS."""
    cols = ["Essay Title", "Word Count"]
    if "Publication Date" in df.columns:
        cols.append("Publication Date")

    rows = []
    for _, row in df.iterrows():
        title = row["Essay Title"]
        link = row.get("Essay Link", "")
        wc = row["Word Count"]
        date_val = ""
        if "Publication Date" in cols and pd.notna(row.get("Publication Date")):
            date_val = str(row["Publication Date"])[:10]

        title_cell = f'<a href="{link}" target="_blank">{title}</a>' if link else title
        row_html = f"<tr><td>{title_cell}</td><td>{wc:,}</td>"
        if "Publication Date" in cols:
            row_html += f"<td>{date_val}</td>"
        row_html += "</tr>"
        rows.append(row_html)

    header = "<th>Essay Title</th><th>Word Count</th>"
    if "Publication Date" in cols:
        header += "<th>Publication Date</th>"

    return f"""
    <table id="essay-table" class="sortable">
      <thead><tr>{header}</tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
    """


def generate_html(df, topics):
    """Combine all charts and table into a single HTML page."""
    total_essays = len(df)
    total_words = df["Word Count"].sum()
    avg_words = int(df["Word Count"].mean())

    charts = []
    hist_fig = build_histogram(df)
    charts.append(pio.to_html(hist_fig, full_html=False, include_plotlyjs="cdn"))

    scatter_fig = build_scatter(df)
    if scatter_fig:
        charts.append(pio.to_html(scatter_fig, full_html=False, include_plotlyjs=False))

    cum_fig = build_cumulative(df)
    if cum_fig:
        charts.append(pio.to_html(cum_fig, full_html=False, include_plotlyjs=False))

    themes_fig = build_themes_chart(topics)
    if themes_fig:
        charts.append(pio.to_html(themes_fig, full_html=False, include_plotlyjs=False))

    table_html = build_essay_table(df)

    charts_html = "\n".join(charts)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Paul Graham Essays Dashboard</title>
  <link rel="alternate" type="application/atom+xml" title="PG Essays Feed" href="feed.xml">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
           max-width: 1200px; margin: 0 auto; padding: 20px; background: #f8f9fa; }}
    h1 {{ color: #333; }}
    .stats {{ display: flex; gap: 20px; margin: 20px 0; flex-wrap: wrap; }}
    .stat-card {{ background: white; padding: 20px; border-radius: 8px;
                  box-shadow: 0 1px 3px rgba(0,0,0,0.1); flex: 1; min-width: 200px; text-align: center; }}
    .stat-card h2 {{ margin: 0; font-size: 2em; color: #e74c3c; }}
    .stat-card p {{ margin: 5px 0 0; color: #666; }}
    .chart {{ margin: 30px 0; }}
    table.sortable {{ width: 100%; border-collapse: collapse; background: white;
                      border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    table.sortable th {{ background: #333; color: white; padding: 12px; cursor: pointer;
                         text-align: left; user-select: none; }}
    table.sortable th:hover {{ background: #555; }}
    table.sortable td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
    table.sortable tr:hover {{ background: #f5f5f5; }}
    table.sortable a {{ color: #3498db; text-decoration: none; }}
    table.sortable a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>Paul Graham Essays Dashboard</h1>
  <div class="stats">
    <div class="stat-card"><h2>{total_essays:,}</h2><p>Total Essays</p></div>
    <div class="stat-card"><h2>{total_words:,}</h2><p>Total Words</p></div>
    <div class="stat-card"><h2>{avg_words:,}</h2><p>Avg Word Count</p></div>
  </div>
  <div class="chart">{charts_html}</div>
  <h2>All Essays</h2>
  {table_html}
  <script>
    document.querySelectorAll("table.sortable th").forEach(function(th, i) {{
      th.addEventListener("click", function() {{
        var table = th.closest("table");
        var tbody = table.querySelector("tbody");
        var rows = Array.from(tbody.querySelectorAll("tr"));
        var asc = th.dataset.asc !== "true";
        th.dataset.asc = asc;
        rows.sort(function(a, b) {{
          var at = a.children[i].textContent.trim();
          var bt = b.children[i].textContent.trim();
          var an = parseFloat(at.replace(/,/g, ""));
          var bn = parseFloat(bt.replace(/,/g, ""));
          if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
          return asc ? at.localeCompare(bt) : bt.localeCompare(at);
        }});
        rows.forEach(function(r) {{ tbody.appendChild(r); }});
      }});
    }});
  </script>
</body>
</html>"""
    return html


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)
    df, topics = load_data()
    html = generate_html(df, topics)
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"Dashboard written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
