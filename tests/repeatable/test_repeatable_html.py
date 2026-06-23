"""Tests for build-time repeatable pill insertion in generated navigation."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXTENSIONS_DIR = REPO_ROOT / "build_files" / "extensions"
TOOLS_DIR = REPO_ROOT / "tools"
for import_path in (EXTENSIONS_DIR, TOOLS_DIR):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from repeatable_html import (  # noqa: E402
    build_navigation_hint_index,
    rewrite_body_navigation,
    rewrite_navigation_fragment,
)
from repeatable_record import RepeatableRecord  # noqa: E402


def _record(msgid: str, msgstr: str, tagname: str = "title") -> RepeatableRecord:
    """Build one repeatable test record with navigation-relevant fields."""
    return RepeatableRecord(
        docname="getting_started/index",
        source_path="manual/getting_started/index.rst",
        source_line=1,
        node_tagname=tagname,
        msgid=msgid,
        msgstr=msgstr,
        html_page="/vi/getting_started/index.html",
        section_id="getting-started",
        ordinal=0,
    )


def test_index_requires_repeatable_navigation_record_and_original_msgid() -> None:
    """Only validated title/toctree records enter the navigation index."""
    records = [
        _record("Getting Started", "Khởi Đầu (Getting Started)"),
        _record("Not This", "Khởi Đầu (Getting Started)"),
        _record("Getting Started", "Khởi Đầu (Getting Started)", "paragraph"),
    ]

    index = build_navigation_hint_index(records)

    assert index == {"Khởi Đầu (Getting Started)": ("Getting Started",)}


def test_navigation_fragment_writes_fixed_repeatable_provenance() -> None:
    """Built navigation receives a fixed span with its English original."""
    index = build_navigation_hint_index(
        [_record("Getting Started", "Khởi Đầu (Getting Started)")]
    )
    source = (
        '<a aria-label="Khởi Đầu (Getting Started)">' "Khởi Đầu (Getting Started)</a>"
    )

    rendered = rewrite_navigation_fragment(source, index)

    assert 'aria-label="Khởi Đầu (Getting Started)"' in rendered
    assert (
        'Khởi Đầu <span class="i18n-en-hint" '
        'data-msgid="Getting Started" data-repeatable="true">'
        "Getting Started</span>"
    ) in rendered


def test_navigation_fragment_rejects_unrecorded_parentheses() -> None:
    """Parenthesized text absent from repeatable records remains plain."""
    index = build_navigation_hint_index(
        [_record("Getting Started", "Khởi Đầu (Getting Started)")]
    )
    source = '<a href="#">Khởi Đầu (bản cũ)</a>'

    assert rewrite_navigation_fragment(source, index) == source


def test_body_rewrite_is_limited_to_navigation_containers() -> None:
    """Matching prose outside generated navigation is not rewritten."""
    index = build_navigation_hint_index(
        [_record("Getting Started", "Khởi Đầu (Getting Started)")]
    )
    body = (
        "<p>Khởi Đầu (Getting Started)</p>"
        '<div class="toc-cards"><div class="card"><a href="#">'
        "Khởi Đầu (Getting Started)</a></div></div>"
        '<div class="toctree-wrapper compound"><a href="#">'
        "Khởi Đầu (Getting Started)</a></div>"
    )

    rendered = rewrite_body_navigation(body, index)

    assert rendered.startswith("<p>Khởi Đầu (Getting Started)</p>")
    assert rendered.count('data-repeatable="true"') == 2
