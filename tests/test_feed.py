import xml.etree.ElementTree as ET

from generate_feed import build_feed


def test_build_feed_generates_valid_xml(sample_df):
    fg = build_feed(sample_df, max_entries=20)
    xml_str = fg.atom_str(pretty=True)
    root = ET.fromstring(xml_str)

    # Atom namespace
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    assert root.tag == "{http://www.w3.org/2005/Atom}feed"
    title = root.find("atom:title", ns)
    assert title is not None
    assert "Paul Graham" in title.text


def test_build_feed_contains_entries(sample_df):
    fg = build_feed(sample_df, max_entries=20)
    xml_str = fg.atom_str(pretty=True)
    root = ET.fromstring(xml_str)

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)
    assert len(entries) == 3  # All 3 sample essays have dates


def test_build_feed_respects_max_entries(sample_df):
    fg = build_feed(sample_df, max_entries=1)
    xml_str = fg.atom_str(pretty=True)
    root = ET.fromstring(xml_str)

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)
    assert len(entries) == 1
