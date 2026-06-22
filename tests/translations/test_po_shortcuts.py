"""Tests for tools/translations/po_shortcuts.py.

Focus on the two correctness-sensitive parts: the raw msgstr scanner
(``parse_po``, including the plural-entry fix) and the byte-preserving in-place
edit (``_apply_to_file``).

Run: python3 -m pytest tests/translations/test_po_shortcuts.py -q
"""

from __future__ import annotations

import os
import sys

# Make the script (and the tools/ package it imports) importable.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for _p in (
    os.path.join(_REPO_ROOT, "tools"),
    os.path.join(_REPO_ROOT, "tools", "translations"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import po_shortcuts as ps  # noqa: E402


# ---------------------------------------------------------------------------
# parse_po
# ---------------------------------------------------------------------------

def test_parse_po_single_msgstr_with_continuations():
    text = (
        '#: ../../manual/x.rst:1\n'
        'msgid "hello"\n'
        'msgstr ""\n'
        '"first line "\n'
        '"second line"\n'
        '\n'
    )
    blocks = list(ps.parse_po(text))
    assert len(blocks) == 1
    block, start = blocks[0]
    assert block.startswith("msgstr")
    assert '"second line"' in block
    # start offset points at the literal 'msgstr' in the source
    assert text[start:start + 6] == "msgstr"


def test_parse_po_captures_all_plural_forms():
    # Regression: the old parser dropped every msgstr[N] after [0].
    text = (
        'msgid "one"\n'
        'msgid_plural "many"\n'
        'msgstr[0] "form zero"\n'
        'msgstr[1] "form one"\n'
        '\n'
    )
    blocks = [b for b, _ in ps.parse_po(text)]
    assert len(blocks) == 2
    assert "form zero" in blocks[0]
    assert "form one" in blocks[1]


def test_parse_po_offsets_are_exact():
    text = 'msgid "a"\nmsgstr "b"\n'
    (block, start), = list(ps.parse_po(text))
    assert text[start:start + len(block)] == block


# ---------------------------------------------------------------------------
# _apply_to_file (byte-preserving surgical edit)
# ---------------------------------------------------------------------------

def test_apply_only_edits_matching_kbd_and_preserves_rest(tmp_path):
    po = tmp_path / "blender_manual.po"
    original = (
        '# a comment\n'
        '#: ../../manual/x.rst:1\n'
        'msgid "Press :kbd:`Ctrl`"\n'
        'msgstr "Nhấn :kbd:`Ctrl`"\n'
        '\n'
        '#: ../../manual/y.rst:1\n'
        'msgid "no shortcut here"\n'
        'msgstr "không có phím tắt"\n'
    )
    po.write_text(original, encoding="utf-8")

    rules = ps._compile_table([["Ctrl", "Cmd"]])
    n = ps._apply_to_file(str(po), rules)
    result = po.read_text(encoding="utf-8")

    assert n == 1                                   # only the msgstr kbd changed
    assert 'msgstr "Nhấn :kbd:`Cmd`"' in result     # translation updated
    assert 'msgid "Press :kbd:`Ctrl`"' in result    # msgid untouched
    # everything except the one shortcut is byte-identical
    assert result == original.replace(
        'msgstr "Nhấn :kbd:`Ctrl`"', 'msgstr "Nhấn :kbd:`Cmd`"'
    )


def test_apply_no_match_leaves_file_untouched(tmp_path):
    po = tmp_path / "blender_manual.po"
    original = 'msgid "x"\nmsgstr "không có phím tắt"\n'
    po.write_text(original, encoding="utf-8")
    mtime_before = po.stat().st_mtime_ns

    n = ps._apply_to_file(str(po), ps._compile_table([["Ctrl", "Cmd"]]))

    assert n == 0
    assert po.read_text(encoding="utf-8") == original
    assert po.stat().st_mtime_ns == mtime_before     # not rewritten at all
