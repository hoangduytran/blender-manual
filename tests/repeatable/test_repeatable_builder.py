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
    HintSide,
    PILL_EN_CSS_CLASS,
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


def test_classify_body_hint_bracket_is_english():
    hint = rx.classify_terminal_hint("Màn Chắn Lọc [Mask]", "Mask")
    assert hint is not None
    assert hint.bracket == "Mask"
    assert hint.lead == "Màn Chắn Lọc "
    assert hint.side == HintSide.ENGLISH_BRACKET


def test_classify_glossary_hint_lead_is_english():
    hint = rx.classify_terminal_hint("Materials [Nguyên Vật Liệu]", "Materials")
    assert hint is not None
    assert hint.bracket == "Nguyên Vật Liệu"  # the translation is pilled
    assert hint.side == HintSide.ENGLISH_LEAD


def test_classify_paren_hint_ru_style():
    # ru keeps the English in parentheses, often lower-cased.
    hint = rx.classify_terminal_hint("Объединить (merge)", "Merge")
    assert hint is not None
    assert hint.bracket == "merge"
    assert hint.side == HintSide.ENGLISH_BRACKET


def test_explicit_reference_label_extracts_visible_msgid() -> None:
    """Explicit RST links expose their visible English source label."""
    msgid = "`Stable Release <https://www.blender.org/download/>`__"

    assert rx.explicit_reference_label(msgid) == "Stable Release"
    assert rx.explicit_reference_label("Stable Release") is None


def test_classify_paren_picks_terminal_group():
    # Earlier parenthetical aside is ignored; the terminal group is the hint.
    hint = rx.classify_terminal_hint("Режим (старый) (mode)", "Mode")
    assert hint is not None
    assert hint.bracket == "mode"
    assert hint.lead == "Режим (старый) "


def test_classify_middle_hint_can_match_source_fragment():
    text = (
        "Cài Đặt Sở Thích Người Dùng [User Preferences] "
        "__package__ (__gói_phần_mềm__)"
    )
    hint = rx.classify_terminal_hint(text, "User Preferences and __package__")

    assert hint is not None
    assert hint.bracket == "User Preferences"
    assert hint.trailing == " __package__ (__gói_phần_mềm__)"
    assert hint.source == "User Preferences"
    assert hint.side == HintSide.ENGLISH_BRACKET


def test_split_terminal_leaf_handles_parens():
    assert rb.split_terminal_leaf("Объединить (merge) ") == (
        "Объединить ",
        "merge",
        " ",
    )


def test_classify_matches_despite_case_drift():
    # Real data: source "Metallic and Roughness" vs translator "And".
    hint = rx.classify_terminal_hint(
        "Kim Loại và Độ Ráp [Metallic And Roughness]", "Metallic and Roughness"
    )
    assert hint is not None
    assert hint.side == HintSide.ENGLISH_BRACKET
    # Pill keeps the translator's text as written.
    assert hint.bracket == "Metallic And Roughness"


def test_classify_rejects_nested_compound():
    assert (
        rx.classify_terminal_hint(
            "Giao Cắt [Dao] (Intersect [Knife])", "Intersect (Knife)"
        )
        is None
    )


def test_classify_rejects_mismatch_empty_and_no_lead():
    assert rx.classify_terminal_hint("Foo [Bar]", "Baz") is None  # neither side matches
    assert rx.classify_terminal_hint("Foo []", "Foo") is None  # empty bracket
    assert rx.classify_terminal_hint("[Mask]", "Mask") is None  # no lead


# --- near-miss reading-hints: pilled "as written", reported for the translator -


# Real data: source "Install from a Package Manager" but the translator dropped
# the article in the parenthetical.
_NEAR_MISS_TEXT = "Cài Đặt từ Trình Quản Lý Gói Phần Mềm (Install from Package Manager)"
_NEAR_MISS_MSGID = "Install from a Package Manager"


def test_classify_accepts_near_miss_pilled_as_written():
    hint = rx.classify_terminal_hint(_NEAR_MISS_TEXT, _NEAR_MISS_MSGID)
    assert hint is not None
    assert hint.side == HintSide.ENGLISH_BRACKET
    # The pill keeps the translator's (imperfect) text, not the source.
    assert hint.bracket == "Install from Package Manager"


def test_classify_hint_mismatch_reports_near_miss_only():
    # Near-miss -> a mismatch to report.
    mismatch = rx.classify_hint_mismatch(_NEAR_MISS_TEXT, _NEAR_MISS_MSGID)
    assert mismatch is not None
    assert mismatch.msgid == _NEAR_MISS_MSGID
    assert mismatch.observed == "Install from Package Manager"
    assert mismatch.ratio >= 0.8
    # Exact match -> nothing to report.
    assert rx.classify_hint_mismatch("Màn Chắn Lọc [Mask]", "Mask") is None
    # Far-off bracket -> not pilled, not reported.
    assert rx.classify_hint_mismatch("Foo [Bar]", "Baz") is None


def test_collect_and_format_mismatches():
    doc = "getting_started/installing/linux"
    records_by_doc = {
        doc: (
            _record(doc, _NEAR_MISS_MSGID, msgstr=_NEAR_MISS_TEXT, line=28),
            _record(doc, "Mask", msgstr="Màn Chắn Lọc [Mask]", line=5),  # exact
        )
    }
    pairs = rx.collect_hint_mismatches(records_by_doc)
    assert len(pairs) == 1  # exact match excluded
    report = rx.format_mismatch_report(pairs, "vi")
    assert _NEAR_MISS_MSGID in report
    assert "Install from Package Manager" in report
    assert ":28" in report
    assert "Mask" not in report


def test_split_terminal_leaf_keeps_trailing_whitespace():
    assert rb.split_terminal_leaf("Foo [Bar] ") == ("Foo ", "Bar", " ")
    assert rb.split_terminal_leaf("Foo without bracket") is None


def test_split_hint_leaf_handles_middle_group():
    assert rb.split_hint_leaf("Foo [Bar] baz", "Bar") == ("Foo ", "Bar", " baz")


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
    node = _translated_node(
        nodes.title, "Trình Thao Tác Nút [Node Wrangler]", "Node Wrangler"
    )
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

    records = rx.extract_repeatable_records(
        _doc_with_toctree(toctree), _context("index")
    )
    by_msgid = {r.msgid: r for r in records}
    assert by_msgid["Chapters"].msgstr == "Chương"
    assert by_msgid["Chapters"].node_tagname == "toctree"
    assert by_msgid["Introduction"].msgstr == "Giới Thiệu"
    assert by_msgid["Advanced"].msgstr == ""  # entry without explicit title


# ---------------------------------------------------------------------------
# Glossary detection
# ---------------------------------------------------------------------------


def test_is_in_glossary_true_inside_glossary_node():
    term = nodes.term()
    item = nodes.definition_list_item("", term)
    dlist = nodes.definition_list("", item)
    addnodes.glossary("", dlist)  # parents dlist under a glossary node
    assert rx.is_in_glossary(term) is True


def test_is_in_glossary_false_for_plain_term():
    term = nodes.term()
    nodes.definition_list_item("", term)
    assert rx.is_in_glossary(term) is False


def test_extract_sets_is_glossary_flag():
    term = nodes.term()
    term += nodes.Text("Materials")
    term["translated"] = True
    term.rawsource = "Materials"
    term.source = "/repo/manual/glossary/index.rst"
    term.line = 11
    item = nodes.definition_list_item("", term, nodes.definition())
    dlist = nodes.definition_list("", item)
    document = new_document("glossary/index", get_default_settings())
    document += addnodes.glossary("", dlist)

    records = rx.extract_repeatable_records(document, _context("glossary/index"))
    materials = [r for r in records if r.msgid == "Materials"]
    assert materials and materials[0].is_glossary is True


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
    assert PILL_EN_CSS_CLASS not in title.get("classes", [])


def test_wrap_glossary_hint_pills_translation_with_native_node():
    # Glossary term: English first, native translation in brackets.
    term = _translated_node(nodes.term, "Materials [Nguyên Vật Liệu]", "Materials")
    assert rb.wrap_terminal_hint(term, "Materials") is True
    native_pills = list(term.findall(rb.i18n_native_hint))
    assert len(native_pills) == 1
    assert native_pills[0].astext() == "Nguyên Vật Liệu"
    assert not list(term.findall(rb.i18n_en_hint))  # not an English pill
    assert term.children[0].astext() == "Materials "


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


def test_wrap_repeatable_link_uses_visible_source_msgid() -> None:
    """A repeatable RST link pills only its repeated visible English label."""
    msgid = "`Stable Release <https://www.blender.org/download/>`__"
    translated = "Bản Phát Hành Ổn Định (Stable Release)"
    term = nodes.term(rawsource=msgid)
    reference = nodes.reference(
        rawsource=translated,
        refuri="https://www.blender.org/download/",
    )
    reference += nodes.Text(translated)
    term += reference
    term["translated"] = True

    assert rb.wrap_terminal_hint(term, msgid) is True
    pill = list(term.findall(rb.i18n_en_hint))[0]
    assert pill.astext() == "Stable Release"
    assert pill["msgid"] == "Stable Release"
    assert reference["refuri"] == "https://www.blender.org/download/"


def test_wrap_middle_hint_before_inline_node() -> None:
    """A heading can pill a source fragment before following inline markup."""
    msgid = "User Preferences and __package__"
    title = nodes.title(rawsource=msgid)
    title += nodes.Text("Cài Đặt Sở Thích Người Dùng [User Preferences] ")
    package = nodes.inline()
    package += nodes.Text("__package__ (__gói_phần_mềm__)")
    title += package
    title["translated"] = True

    assert rb.wrap_terminal_hint(title, msgid) is True
    pill = list(title.findall(rb.i18n_en_hint))[0]
    assert pill.astext() == "User Preferences"
    assert pill["msgid"] == "User Preferences"
    assert title.children[0].astext() == "Cài Đặt Sở Thích Người Dùng "
    assert title.children[2].astext() == " "
    assert title.children[3] is package


# ---------------------------------------------------------------------------
# Grouping and envelope
# ---------------------------------------------------------------------------


def _record(
    docname, msgid, msgstr="", line=1, tag="title", ordinal=0
) -> RepeatableRecord:
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
