"""Unit tests for the repeatable-record extension (pure logic, no Sphinx).

Covers message filtering, English-hint validation, record construction and
ordinals, the pill DOM mutation, gzip-pickle round-trip, and PO catalogue
assembly (dedup, untranslated, conflicts).

Run: python3 -m pytest tests/repeatable/test_repeatable_builder.py -q
"""

from __future__ import annotations

import gzip
import os
import pickle
import sys

from docutils import nodes
from docutils.core import publish_doctree
from docutils.utils import new_document
from docutils.frontend import get_default_settings
from sphinx import addnodes

# Make the extension modules and shared tools importable.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for _p in (
    os.path.join(_REPO_ROOT, "build_files", "extensions"),
    os.path.join(_REPO_ROOT, "tools"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pathlib import Path  # noqa: E402

import repeatable_builder as rb  # noqa: E402
import repeatable_extract as rx  # noqa: E402
from _doctree_extract import make_rel_source, write_gzip_pickle  # noqa: E402
from repeatable_record import RepeatableRecord  # noqa: E402

from common.constants import (  # noqa: E402  # type: ignore[import-not-found]
    PILL_CSS_CLASS,
    PickleEnvelopeKey,
    REPEATABLE_SCHEMA_VERSION,
)


def _context(docname: str = "addons/node_wrangler") -> rx.ExtractionContext:
    return rx.ExtractionContext(
        docname=docname,
        html_page=f"/vi/{docname}.html",
        rel_source=make_rel_source(Path("/repo/manual")),
    )


def _translated_node(factory, text: str, msgid: str):
    """Build an allowlisted node carrying *text* and flagged translated."""
    node = factory()
    node += nodes.Text(text)
    node["translated"] = True
    node.rawsource = msgid
    node.source = "/repo/manual/addons/node_wrangler.rst"
    node.line = 7
    return node


# ---------------------------------------------------------------------------
# Predicates
# ---------------------------------------------------------------------------

def test_allowlisted_tags_accepted_and_others_rejected():
    assert rx.is_repeatable_tag("title")
    assert rx.is_repeatable_tag("term")
    assert rx.is_repeatable_tag("toctree")
    assert not rx.is_repeatable_tag("paragraph")
    assert not rx.is_repeatable_tag("literal")


def test_sentence_like_rejects_period_keeps_ellipsis():
    assert rx.is_sentence_like("This is prose.")
    assert not rx.is_sentence_like("Move...")
    assert not rx.is_sentence_like("Node Wrangler")


def test_is_repeatable_message_combines_rules():
    title = nodes.title()
    assert rx.is_repeatable_message(title, "Node Wrangler")
    assert not rx.is_repeatable_message(title, "   ")
    assert not rx.is_repeatable_message(title, "A full sentence.")
    assert not rx.is_repeatable_message(nodes.paragraph(), "Node Wrangler")


# ---------------------------------------------------------------------------
# Hint validation
# ---------------------------------------------------------------------------

def test_find_terminal_hint_valid():
    hint = rx.find_terminal_hint("Màn Chắn Lọc [Mask]", "Mask")
    assert hint is not None
    assert hint.english == "Mask"
    assert hint.prefix == "Màn Chắn Lọc "


def test_find_terminal_hint_rejects_nested_compound():
    assert rx.find_terminal_hint(
        "Giao Cắt [Dao] (Intersect [Knife])", "Intersect (Knife)"
    ) is None


def test_find_terminal_hint_rejects_mismatch_empty_and_no_prefix():
    assert rx.find_terminal_hint("Foo [Bar]", "Baz") is None
    assert rx.find_terminal_hint("Foo []", "") is None
    assert rx.find_terminal_hint("[Mask]", "Mask") is None  # no translation prefix


def test_split_leaf_hint_keeps_trailing_whitespace():
    assert rb.split_leaf_hint("Foo [Bar] ", "Bar") == ("Foo ", "Bar", " ")
    assert rb.split_leaf_hint("Foo [Bar]", "Baz") is None


# ---------------------------------------------------------------------------
# Translation state
# ---------------------------------------------------------------------------

def test_node_msgstr_untranslated_is_empty():
    node = nodes.title()
    node += nodes.Text("Node Wrangler")
    assert rx.node_msgstr(node, "Node Wrangler") == ""


def test_node_msgstr_identical_source_is_empty():
    node = _translated_node(nodes.title, "Node Wrangler", "Node Wrangler")
    assert rx.node_msgstr(node, "Node Wrangler") == ""


def test_node_msgstr_returns_translation():
    node = _translated_node(nodes.title, "Trình Thao Tác Nút [Node Wrangler]", "Node Wrangler")
    assert rx.node_msgstr(node, "Node Wrangler") == "Trình Thao Tác Nút [Node Wrangler]"


# ---------------------------------------------------------------------------
# Extraction + ordinals
# ---------------------------------------------------------------------------

_RST = """
Geometry Node Editor
====================

Some intro paragraph here.

Parent
------

Jumps up a node group level.
"""


def test_extract_captures_titles_with_anchor_and_ordinals():
    doctree = publish_doctree(_RST)
    records = rx.extract_repeatable_records(doctree, _context("editors/geometry_node"))
    titles = [r for r in records if r.node_tagname == "title"]
    assert {"Geometry Node Editor", "Parent"} <= {r.msgid for r in titles}
    assert [r.ordinal for r in records] == list(range(len(records)))


def test_extract_skips_sentence_paragraph():
    doctree = publish_doctree(_RST)
    records = rx.extract_repeatable_records(doctree, _context())
    assert all("Jumps up a node group level" not in r.msgid for r in records)


def test_extract_assigns_distinct_ordinals_to_repeated_text():
    doctree = publish_doctree(
        "Title Here\n==========\n\n.. rubric:: Repeat\n\n.. rubric:: Repeat\n"
    )
    records = rx.extract_repeatable_records(doctree, _context())
    repeats = [r for r in records if r.msgid == "Repeat"]
    assert len(repeats) == 2
    assert repeats[0].ordinal != repeats[1].ordinal


# ---------------------------------------------------------------------------
# Toctree extraction
# ---------------------------------------------------------------------------

def _doc_with_toctree(toctree) -> nodes.document:
    document = new_document("test", get_default_settings())
    document += toctree
    return document


def test_toctree_caption_and_entries_paired():
    toctree = addnodes.toctree()
    toctree["rawcaption"] = "Chapters"
    toctree["caption"] = "Chương"
    toctree["rawentries"] = ["Introduction", "Advanced"]
    toctree["entries"] = [("Giới Thiệu", "intro"), (None, "advanced")]
    toctree.source = "/repo/manual/index.rst"
    toctree.line = 1

    records = rx.extract_repeatable_records(_doc_with_toctree(toctree), _context("index"))
    by_msgid = {r.msgid: r for r in records}
    assert by_msgid["Chapters"].msgstr == "Chương"
    assert by_msgid["Chapters"].node_tagname == "toctree"
    assert by_msgid["Introduction"].msgstr == "Giới Thiệu"
    assert by_msgid["Advanced"].msgstr == ""  # entry without explicit title


# ---------------------------------------------------------------------------
# Pill mutation
# ---------------------------------------------------------------------------

def test_wrap_terminal_hint_pills_only_english_suffix():
    title = _translated_node(nodes.title, "Hai Mặt [Double-sided]", "Double-sided")
    assert rb.wrap_terminal_hint(title, "Double-sided") is True

    pills = list(title.findall(rb.i18n_en_hint))
    assert len(pills) == 1
    assert pills[0].astext() == "Double-sided"
    # The Vietnamese prefix survives as a plain Text sibling, unwrapped.
    assert title.children[0].astext() == "Hai Mặt "
    # The parent title carries no pill class.
    assert PILL_CSS_CLASS not in title.get("classes", [])


def test_wrap_terminal_hint_term_renders_pill():
    term = _translated_node(nodes.term, "Màn Chắn Lọc [Mask]", "Mask")
    assert rb.wrap_terminal_hint(term, "Mask") is True
    pills = list(term.findall(rb.i18n_en_hint))
    assert pills and pills[0].astext() == "Mask"


def test_wrap_terminal_hint_skips_untranslated_and_mismatch():
    plain = nodes.title()
    plain += nodes.Text("Node Wrangler")
    assert rb.wrap_terminal_hint(plain, "Node Wrangler") is False

    mismatched = _translated_node(nodes.title, "Foo [Bar]", "Baz")
    assert rb.wrap_terminal_hint(mismatched, "Baz") is False


def test_wrap_terminal_hint_preserves_reference_target():
    ref = _translated_node(nodes.reference, "Tài Liệu [Docs]", "Docs")
    ref["refuri"] = "https://example.org"
    assert rb.wrap_terminal_hint(ref, "Docs") is True
    assert ref["refuri"] == "https://example.org"
    assert list(ref.findall(rb.i18n_en_hint))[0].astext() == "Docs"


# ---------------------------------------------------------------------------
# Grouping and envelope
# ---------------------------------------------------------------------------

def _record(docname, msgid, msgstr="", line=1, tag="title", ordinal=0) -> RepeatableRecord:
    return RepeatableRecord(
        docname=docname,
        source_path=f"manual/{docname}.rst",
        source_line=line,
        node_tagname=tag,
        msgid=msgid,
        msgstr=msgstr,
        html_page=f"/vi/{docname}.html",
        section_id="",
        ordinal=ordinal,
    )


def test_group_records_by_doc_sorts_docnames():
    records = [_record("b/two", "X"), _record("a/one", "Y")]
    grouped = rx.group_records_by_doc(records)
    assert list(grouped) == ["a/one", "b/two"]
    assert all(isinstance(v, tuple) for v in grouped.values())


def test_build_envelope_schema_and_language():
    grouped = rx.group_records_by_doc([_record("a", "X")])
    envelope = rx.build_envelope(grouped, "vi")
    assert envelope[PickleEnvelopeKey.SCHEMA_VERSION.value] == REPEATABLE_SCHEMA_VERSION
    assert envelope[PickleEnvelopeKey.LANGUAGE.value] == "vi"


def test_gzip_pickle_round_trip(tmp_path):
    grouped = rx.group_records_by_doc([_record("a", "X", msgstr="Y")])
    out = tmp_path / "repeatable.pkl.gz"
    write_gzip_pickle(rx.build_envelope(grouped, "vi"), out)

    with gzip.open(out, "rb") as fh:
        loaded = pickle.load(fh)
    records = loaded[PickleEnvelopeKey.RECORDS_BY_DOC.value]["a"]
    assert isinstance(records[0], RepeatableRecord)
    assert records[0].msgstr == "Y"
    assert loaded[PickleEnvelopeKey.LANGUAGE.value] == "vi"


# ---------------------------------------------------------------------------
# PO catalogue
# ---------------------------------------------------------------------------

def test_catalog_merges_locations_and_node_comments():
    records = [
        _record("a/one", "Mask", msgstr="Màn Chắn Lọc", line=5, tag="term"),
        _record("b/two", "Mask", msgstr="Màn Chắn Lọc", line=9, tag="title"),
    ]
    grouped = rx.group_records_by_doc(records)
    catalog, conflicts = rx.build_catalog(grouped, "vi", "Blender", "4.5")
    message = catalog.get("Mask")
    assert message.string == "Màn Chắn Lọc"
    assert ("../../manual/a/one.rst", 5) in message.locations
    assert ("../../manual/b/two.rst", 9) in message.locations
    assert "repeatable-node: term" in message.auto_comments
    assert "repeatable-node: title" in message.auto_comments
    assert conflicts == []


def test_catalog_untranslated_has_empty_string():
    grouped = rx.group_records_by_doc([_record("a", "New")])
    catalog, _ = rx.build_catalog(grouped, "vi", "Blender", "4.5")
    assert catalog.get("New").string == ""


def test_catalog_conflict_is_reported_and_deterministic():
    records = [
        _record("a", "Snap", msgstr="Bám Dính"),
        _record("b", "Snap", msgstr="Dính"),
    ]
    grouped = rx.group_records_by_doc(records)
    catalog, conflicts = rx.build_catalog(grouped, "vi", "Blender", "4.5")
    assert len(conflicts) == 1
    assert conflicts[0].msgid == "Snap"
    # Deterministic winner: first when sorted.
    assert catalog.get("Snap").string == "Bám Dính"
