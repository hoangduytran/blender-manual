"""Tests for build_files/extensions/search_index_builder.py.

Covers the pure extraction/aggregation logic without spinning up a full Sphinx
build: nearest-section anchor resolution, message extraction from a real
docutils doctree, dedup, and source-language msgstr handling.

Run: python3 -m pytest tests/search/test_search_index_extension.py -q
"""

from __future__ import annotations

import os
import sys

import pytest
from docutils import nodes
from docutils.core import publish_doctree

# Make the extension and the shared search modules importable.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for _p in (
    os.path.join(_REPO_ROOT, "build_files", "extensions"),
    os.path.join(_REPO_ROOT, "tools"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import search_index_builder as ext  # noqa: E402


# ---------------------------------------------------------------------------
# nearest_section_id
# ---------------------------------------------------------------------------

def test_nearest_section_id_returns_enclosing_section():
    section = nodes.section(ids=["the-anchor"])
    para = nodes.paragraph()
    text = nodes.Text("hello")
    para += text
    section += para
    assert ext.nearest_section_id(text) == "the-anchor"


def test_nearest_section_id_picks_innermost():
    outer = nodes.section(ids=["outer"])
    inner = nodes.section(ids=["inner"])
    para = nodes.paragraph()
    para += nodes.Text("x")
    inner += para
    outer += inner
    assert ext.nearest_section_id(para) == "inner"


def test_nearest_section_id_empty_when_no_section():
    para = nodes.paragraph()
    t = nodes.Text("orphan")
    para += t
    assert ext.nearest_section_id(t) == ""


# ---------------------------------------------------------------------------
# extract_occurrences (real docutils doctree)
# ---------------------------------------------------------------------------

RST = """
Geometry Node Editor
====================

Some intro paragraph here.

Parent
------

Jumps up a node group level.
"""


def _extract():
    doctree = publish_doctree(RST)
    return ext.extract_occurrences(
        doctree,
        docname="editors/geometry_node",
        lang="en",
        rel_source=lambda src, doc: f"manual/{doc}.rst",
    )


def test_extract_finds_body_phrase_with_anchor():
    occ = _extract()
    hits = [o for o in occ if "Jumps up a node group level" in o[0]]
    assert len(hits) == 1
    msgid, msgctxt, rst_rel, line, html_page, anchor = hits[0]
    assert msgctxt == ""
    assert rst_rel == "manual/editors/geometry_node.rst"
    assert html_page == "/en/editors/geometry_node.html"
    assert anchor == "parent"          # nearest section
    assert isinstance(line, int) and line > 0


def test_extract_includes_titles():
    texts = [o[0] for o in _extract()]
    assert "Geometry Node Editor" in texts
    assert "Parent" in texts


def test_extract_skips_substitution_definitions():
    doctree = publish_doctree(
        ".. |sub| replace:: substituted text\n\nReal paragraph.\n"
    )
    texts = [
        o[0]
        for o in ext.extract_occurrences(
            doctree, "x", "en", lambda src, doc: f"manual/{doc}.rst"
        )
    ]
    assert "Real paragraph." in texts
    assert "substituted text" not in texts


# ---------------------------------------------------------------------------
# aggregate
# ---------------------------------------------------------------------------

def test_aggregate_dedups_by_msgid_and_keeps_msgstr_blank():
    occ = [
        ("Add-ons", "", "manual/addons/index.rst", 5, "/en/addons/index.html", "add-ons"),
        ("Add-ons", "", "manual/advanced/extensions/addons.rst", 10,
         "/en/advanced/extensions/addons.html", "add-ons"),
    ]
    recs = ext.aggregate(occ)
    assert len(recs) == 1
    rec = recs[0]
    assert rec.msgid == "Add-ons"
    assert rec.msgstr == "" and rec.msgstr_stripped == ""
    assert rec.msgctxt == ""
    assert len(rec.locations) == 2
    assert rec.msgid_stripped == "Add-ons"


def test_aggregate_dedups_identical_occurrences():
    same = ("Jumps up a node group level", "",
            "manual/editors/geometry_node.rst", 56,
            "/en/editors/geometry_node.html", "geometry-node-editor")
    recs = ext.aggregate([same, same, same])
    assert len(recs) == 1
    assert recs[0].locations == [("manual/editors/geometry_node.rst", 56)]
    assert recs[0].html_pages == ["/en/editors/geometry_node.html"]
    assert recs[0].section_keys == ["geometry-node-editor"]


def test_aggregate_distinct_msgids_kept_separate():
    occ = [
        ("Alpha", "", "manual/a.rst", 1, "/en/a.html", "alpha"),
        ("Beta", "", "manual/b.rst", 1, "/en/b.html", "beta"),
    ]
    recs = ext.aggregate(occ)
    assert {r.msgid for r in recs} == {"Alpha", "Beta"}


# ---------------------------------------------------------------------------
# end-to-end: extracted records are searchable via the real searcher
# ---------------------------------------------------------------------------

def test_extracted_records_are_searchable():
    pytest.importorskip("search.index_searcher")
    from search.index_searcher import search_batch

    recs = ext.aggregate(_extract())
    # search_batch args: (batch, query, regex, case_sensitive, whole_word, field, limit)
    hits = search_batch(
        (recs, "Jumps up a node group level", False, False, False, "msgid", 10)
    )
    assert hits, "phrase should be found via msgid search"
    assert any("geometry_node" in h.html_page for h in hits)
