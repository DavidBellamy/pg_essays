import os
import tempfile

from visualize_wc import (
    plot_cumulative_word_count,
    plot_histogram,
    plot_word_count_over_time,
)


def test_plot_histogram(sample_df):
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "hist.png")
        plot_histogram(sample_df, path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0


def test_plot_word_count_over_time(sample_df):
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "scatter.png")
        plot_word_count_over_time(sample_df, path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0


def test_plot_cumulative_word_count(sample_df):
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "cumulative.png")
        plot_cumulative_word_count(sample_df, path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
