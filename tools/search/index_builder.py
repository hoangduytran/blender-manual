"""Build the PO-based search index and write it as a gzip-compressed pickle.

CLI usage::

    python3 tools/search/index_builder.py \\
        --po    locale/vi/LC_MESSAGES/blender_manual.po \\
        --rst   manual/ \\
        --build build/vi/ \\
        --lang  vi

The output file is ``<build-dir>/searchindex.pkl.gz``.  It is written
atomically (temp file → os.replace) so a running server never reads a
partially-written file.
"""

from __future__ import annotations

import argparse
import gzip
import logging
import os
import pickle
import sys
import unicodedata
from pathlib import Path

# debug_log lives next to this file in tools/; fall back silently if absent.
try:
    from debug_log import debug_log  # type: ignore[import-not-found]
except ImportError:
    def debug_log(message: str, *args: object, **_kw: object) -> None:  # type: ignore[misc]
        if os.getenv("DEBUG", "").lower() in {"true", "1", "yes", "on"}:
            logging.debug(message, *args)

# Relative imports work when loaded as part of the package; when run as a
# standalone script (__package__ is None) we fall back to absolute imports
# after adding tools/ to sys.path.
if __package__:
    from .po_parser import POEntry, read_po_file
    from .searchable_record import SearchableRecord
    from .section_map import SectionMap, build_section_map, resolve_section_key
else:
    _TOOLS = Path(__file__).resolve().parent.parent
    if str(_TOOLS) not in sys.path:
        sys.path.insert(0, str(_TOOLS))
    from search.po_parser import POEntry, read_po_file  # type: ignore[import]
    from search.searchable_record import SearchableRecord  # type: ignore[import]
    from search.section_map import SectionMap, build_section_map, resolve_section_key  # type: ignore[import]

from common.constants import (  # type: ignore[import-not-found]
    EMPTY_STRING,
    HTML_SUFFIX,
    RST_SUFFIX,
    SEARCH_INDEX_FILENAME,
    TEMP_SUFFIX,
    UnicodeNormForm,
)


# ---------------------------------------------------------------------------
# Tone normalisation (pre-computed at build time — see §18.3 of the plan)
# ---------------------------------------------------------------------------

# đ / Đ (U+0111 / U+0110, LATIN LETTER D WITH STROKE) do not decompose via
# NFD — they are base characters with a stroke modifier that has no combining
# form.  Pre-translate them to their ASCII equivalents before NFD stripping so
# "điều" → "dieu" instead of the incorrect "ieu".
_PRECOMPOSED = str.maketrans({"đ": "d", "Đ": "D"})


def _strip_tones(text: str) -> str:
    """Remove Vietnamese diacritic marks via NFD decomposition.

    NFD decomposes precomposed characters into base + combining marks.
    Stripping code-points above U+007F leaves only ASCII base letters,
    making tone-less queries (typed without IME) match accented text.

    Special case: đ/Đ are pre-translated to d/D before NFD because
    the stroke modifier has no Unicode combining form.
    """
    return EMPTY_STRING.join(
        c for c in unicodedata.normalize(UnicodeNormForm.NFD, text.translate(_PRECOMPOSED))
        if ord(c) < 128
    )


# ---------------------------------------------------------------------------
# RST path → HTML URL
# ---------------------------------------------------------------------------

def rst_to_html_page(
    rst_rel_path: str,
    lang: str,
    rst_prefix: str,
    rst_suffix: str,
    html_suffix: str,
) -> str:
    """Convert a PO location path to the HTML URL served by serve_docs.py.

    Input : ``"manual/editors/3dview/3d_cursor.rst"``
    Output: ``"/vi/editors/3dview/3d_cursor.html"``

    All three conversion strings (*rst_prefix*, *rst_suffix*, *html_suffix*)
    come from :class:`~translations.smart_mo_compile.ConfigRecord` so they are
    never hard-coded here.
    """
    stripped = rst_rel_path.removeprefix(rst_prefix)
    without_ext = stripped.removesuffix(rst_suffix)
    return f"/{lang}/{without_ext}{html_suffix}"


# ---------------------------------------------------------------------------
# Build pipeline
# ---------------------------------------------------------------------------

def build_records(
    entries: list[POEntry],
    section_map: SectionMap,
    lang: str,
    rst_prefix: str,
    rst_suffix: str,
    html_suffix: str,
) -> list[SearchableRecord]:
    """Convert PO entries to SearchableRecord objects with pre-stripped fields."""
    records: list[SearchableRecord] = []
    for entry in entries:
        html_pages: list[str] = []
        section_keys: list[str] = []

        for rst_rel_path, line_no in entry.locations:
            html_pages.append(rst_to_html_page(rst_rel_path, lang, rst_prefix, rst_suffix, html_suffix))
            section_keys.append(
                resolve_section_key(section_map, rst_rel_path, line_no)
            )

        records.append(SearchableRecord(
            msgid=entry.msgid,
            msgstr=entry.msgstr,
            msgid_stripped=_strip_tones(entry.msgid),
            msgstr_stripped=_strip_tones(entry.msgstr),
            locations=list(entry.locations),
            html_pages=html_pages,
            section_keys=section_keys,
            flags=list(entry.flags),
        ))

    return records


def deduplicate_by_msgid(records: list[SearchableRecord]) -> list[SearchableRecord]:
    """Merge records that share the same msgid, combining their location lists.

    Some msgid strings appear in many RST files (e.g. "Add-ons" in 7 files).
    Each produces its own POEntry from the parser.  After building records,
    we merge so each unique msgid becomes exactly one SearchableRecord with
    all locations concatenated.
    """
    seen: dict[str, SearchableRecord] = {}
    for rec in records:
        if rec.msgid not in seen:
            seen[rec.msgid] = SearchableRecord(
                msgid=rec.msgid,
                msgstr=rec.msgstr,
                msgid_stripped=rec.msgid_stripped,
                msgstr_stripped=rec.msgstr_stripped,
                locations=list(rec.locations),
                html_pages=list(rec.html_pages),
                section_keys=list(rec.section_keys),
                flags=list(rec.flags),
            )
        else:
            existing = seen[rec.msgid]
            existing.locations.extend(rec.locations)
            existing.html_pages.extend(rec.html_pages)
            existing.section_keys.extend(rec.section_keys)
    return list(seen.values())


def write_index(records: list[SearchableRecord], out_path: Path) -> None:
    """Serialize records as a gzip-compressed pickle (atomic write)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.parent / (out_path.name + TEMP_SUFFIX)
    try:
        with gzip.open(tmp, "wb", compresslevel=6) as fh:
            pickle.dump(records, fh, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, out_path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def build_index(
    po_path: Path,
    rst_root: Path,
    out_path: Path,
    lang: str,
    *,
    rst_suffix: str = RST_SUFFIX,
    html_suffix: str = HTML_SUFFIX,
) -> list[SearchableRecord]:
    """Full pipeline: parse PO → scan RST → build records → write pickle."""
    rst_prefix = rst_root.name + "/"

    debug_log("Reading PO: %s", po_path)
    entries = read_po_file(po_path)
    debug_log("  %d PO entries read", len(entries))

    debug_log("Scanning RST headings: %s", rst_root)
    section_map = build_section_map(rst_root)
    debug_log("  %d RST files mapped", len(section_map))

    debug_log("Building records …")
    records = build_records(entries, section_map, lang, rst_prefix, rst_suffix, html_suffix)
    records = deduplicate_by_msgid(records)
    debug_log("  %d unique msgids", len(records))

    debug_log("Writing index: %s", out_path)
    write_index(records, out_path)
    debug_log("Done.")

    return records


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    ap = argparse.ArgumentParser(
        description="Build PO-based search index (searchindex.pkl.gz).",
    )
    ap.add_argument("--po", required=True,
                    help="Path to blender_manual.po")
    ap.add_argument("--rst", required=True,
                    help="Root directory of RST source files (manual/)")
    ap.add_argument("--build", required=True,
                    help="Output directory (e.g. build/vi/)")
    ap.add_argument("--lang", required=True,
                    help="Language code (e.g. vi, en)")
    ap.add_argument("--rst-suffix", default=RST_SUFFIX,
                    help="RST source file extension (default: .rst)")
    ap.add_argument("--html-suffix", default=HTML_SUFFIX,
                    help="HTML output page extension (default: .html)")
    ap.add_argument("--index-filename", default=SEARCH_INDEX_FILENAME,
                    help="Search index output filename (default: searchindex.pkl.gz)")
    args = ap.parse_args()

    po_path = Path(args.po)
    rst_root = Path(args.rst)
    out_path = Path(args.build) / args.index_filename

    if not po_path.is_file():
        logging.error("PO file not found: %s", po_path)
        sys.exit(1)
    if not rst_root.is_dir():
        logging.error("RST root not found: %s", rst_root)
        sys.exit(1)

    build_index(
        po_path, rst_root, out_path, args.lang,
        rst_suffix=args.rst_suffix,
        html_suffix=args.html_suffix,
    )


if __name__ == "__main__":
    _main()
