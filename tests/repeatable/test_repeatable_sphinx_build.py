"""Integration tests: a real ``sphinx-build -b html`` of a tiny vi/en project.

Builds a minimal multilingual project in a temp dir and asserts the
repeatable_builder extension's end-to-end behaviour:

* vi build writes both artifacts; the pickle round-trips; the PO loads.
* vi HTML renders the server-side ``.i18n-en-hint`` pill for a heading and a
  definition term, with no literal ``[English]`` left in the term.
* the English (source) build writes neither artifact and emits no pill.

Run: python3 -m pytest tests/repeatable/test_repeatable_sphinx_build.py -q
"""

from __future__ import annotations

import gzip
import pickle
import sys
from pathlib import Path
from textwrap import dedent

import pytest

pytest.importorskip("sphinx.application")
from sphinx.application import Sphinx  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EXT_DIR = _REPO_ROOT / "build_files" / "extensions"
_TOOLS_DIR = _REPO_ROOT / "tools"
for _p in (_EXT_DIR, _TOOLS_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

PILL_SPAN_NODE_WRANGLER = '<span class="i18n-en-hint">Node Wrangler</span>'
PILL_SPAN_MASK = '<span class="i18n-en-hint">Mask</span>'
PILL_SPAN_MATERIALS_VI = '<span class="i18n-vi-hint">Nguyên Vật Liệu</span>'

_INDEX_RST = dedent(
    """\
    Node Wrangler
    =============

    Intro paragraph that is left untranslated.

    Mask
        The mask description body.

    .. glossary::

       Materials
          The surface appearance of an object.
    """
)

_CONF_PY = dedent(
    f"""\
    import sys
    sys.path.insert(0, {str(_EXT_DIR)!r})
    sys.path.insert(0, {str(_TOOLS_DIR)!r})

    project = "Repeatable Test"
    version = "1.0"
    extensions = ["repeatable_builder"]
    html_theme = "basic"
    locale_dirs = ["locale"]
    gettext_compact = "messages"
    repeatable_pickle_filename = "repeatable.pkl.gz"
    repeatable_po_filename = "repeatable.po"
    """
)

_PO = dedent(
    """\
    msgid ""
    msgstr ""
    "Content-Type: text/plain; charset=UTF-8\\n"

    msgid "Node Wrangler"
    msgstr "Trình Thao Tác Nút [Node Wrangler]"

    msgid "Mask"
    msgstr "Màn Chắn Lọc [Mask]"

    msgid "Materials"
    msgstr "Materials [Nguyên Vật Liệu]"
    """
)


def _write_project(root: Path) -> None:
    """Lay out a minimal Sphinx project with a vi catalogue."""
    (root / "conf.py").write_text(_CONF_PY, encoding="utf-8")
    (root / "index.rst").write_text(_INDEX_RST, encoding="utf-8")
    lc_messages = root / "locale" / "vi" / "LC_MESSAGES"
    lc_messages.mkdir(parents=True, exist_ok=True)
    (lc_messages / "messages.po").write_text(_PO, encoding="utf-8")


def _build(root: Path, out_name: str, language: "str | None") -> Path:
    """Run an in-process HTML build; return the output directory."""
    outdir = root / out_name
    doctreedir = root / f"{out_name}.doctrees"
    overrides = {"language": language} if language else {}
    app = Sphinx(
        srcdir=str(root),
        confdir=str(root),
        outdir=str(outdir),
        doctreedir=str(doctreedir),
        buildername="html",
        confoverrides=overrides,
        freshenv=True,
    )
    app.build()
    return outdir


@pytest.fixture()
def project(tmp_path: Path) -> Path:
    _write_project(tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# Translated (vi) build
# ---------------------------------------------------------------------------

def test_vi_build_writes_both_artifacts(project: Path):
    outdir = _build(project, "vi", "vi")
    assert (outdir / "repeatable.pkl.gz").is_file()
    assert (outdir / "repeatable.po").is_file()


def test_vi_pickle_round_trips_records(project: Path):
    outdir = _build(project, "vi", "vi")
    with gzip.open(outdir / "repeatable.pkl.gz", "rb") as fh:
        envelope = pickle.load(fh)
    assert envelope["language"] == "vi"
    assert envelope["records_by_doc"]  # at least one document captured
    msgids = {
        rec.msgid
        for records in envelope["records_by_doc"].values()
        for rec in records
    }
    assert {"Node Wrangler", "Mask"} <= msgids


def test_vi_po_loads_with_sphinx_intl(project: Path):
    outdir = _build(project, "vi", "vi")
    from sphinx_intl.catalog import load_po

    catalog = load_po(str(outdir / "repeatable.po"))
    ids = {message.id for message in catalog if message.id}
    assert {"Node Wrangler", "Mask"} <= ids


def test_vi_html_renders_pills_server_side(project: Path):
    outdir = _build(project, "vi", "vi")
    html = (outdir / "index.html").read_text(encoding="utf-8")
    assert PILL_SPAN_NODE_WRANGLER in html
    assert PILL_SPAN_MASK in html
    # The literal bracketed English must not survive in the term text.
    assert "[Mask]" not in html


def test_vi_glossary_term_pills_translation_in_vi_class(project: Path):
    outdir = _build(project, "vi", "vi")
    html = (outdir / "index.html").read_text(encoding="utf-8")
    # Glossary keeps the English term first; the Vietnamese is the muted pill.
    assert PILL_SPAN_MATERIALS_VI in html
    assert "[Nguyên Vật Liệu]" not in html
    assert ">Materials\n" in html or ">Materials<" in html or "Materials " in html


def test_vi_pickle_flags_glossary_records(project: Path):
    outdir = _build(project, "vi", "vi")
    with gzip.open(outdir / "repeatable.pkl.gz", "rb") as fh:
        envelope = pickle.load(fh)
    records = [
        rec
        for recs in envelope["records_by_doc"].values()
        for rec in recs
    ]
    glossary = [r for r in records if r.is_glossary]
    assert glossary and all(r.msgid == "Materials" for r in glossary)
    # Non-glossary records (heading/term) are not flagged.
    assert any(not r.is_glossary for r in records)


# ---------------------------------------------------------------------------
# Source (English) build
# ---------------------------------------------------------------------------

def test_en_build_writes_no_artifacts_and_no_pill(project: Path):
    outdir = _build(project, "en", None)
    assert not (outdir / "repeatable.pkl.gz").exists()
    assert not (outdir / "repeatable.po").exists()
    html = (outdir / "index.html").read_text(encoding="utf-8")
    assert "i18n-en-hint" not in html
