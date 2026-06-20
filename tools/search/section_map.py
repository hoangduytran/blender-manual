"""RST heading scanner: builds a map of section anchor slugs per RST file.

Used by index_builder.py to resolve which section a PO location line falls in.
"""

from __future__ import annotations

import bisect
import re
import unicodedata
from pathlib import Path

from .searchable_record import SectionRange
from common.constants import (  # type: ignore[import-not-found]
    EMPTY_STRING,
    ENCODING_ERROR_MODE,
    FILE_ENCODING,
    HYPHEN,
    PATH_SEP_POSIX,
    PATH_SEP_WINDOWS,
    RST_ANCHOR_NONWORD_RE,
    RST_SUFFIX,
    RST_UNDERLINE_CHARS,
    UnicodeNormForm,
)

_UNDERLINE_CHARS = RST_UNDERLINE_CHARS

# dict[rst_rel_path, list[SectionRange]] — list sorted by start_line ascending
SectionMap = dict[str, list[SectionRange]]


def heading_to_anchor(title: str) -> str:
    """Replicate Sphinx's heading-to-anchor slug algorithm.

    Normalises unicode to NFKD, lowercases, then replaces runs of
    non-word characters with hyphens.  Matches the ``id=`` attribute Sphinx
    writes into the built HTML so our section_keys are deep-linkable.
    """
    slug = unicodedata.normalize(UnicodeNormForm.NFKD, title).lower()
    slug = re.sub(RST_ANCHOR_NONWORD_RE, HYPHEN, slug, flags=re.UNICODE)
    slug = slug.strip(HYPHEN)
    return slug


def _is_underline(line: str, title_len: int) -> bool:
    """Return True if *line* looks like an RST heading underline.

    Rules:
    - Must start at column 0 (no leading whitespace).
    - Must consist entirely of a single underline character.
    - Must be at least as long as the title.
    """
    stripped = line.rstrip()
    if not stripped:
        return False
    if line[0] in (" ", "\t"):
        return False   # indented → code block, not a heading underline
    chars = set(stripped)
    return len(chars) == 1 and chars.issubset(_UNDERLINE_CHARS) and len(stripped) >= title_len


def build_section_map(rst_root: Path) -> SectionMap:
    """Scan all .rst files under *rst_root* and return a SectionMap.

    The SectionMap maps each file's path (relative to *rst_root*, using
    forward slashes, prefixed with ``manual/``) to a list of SectionRange
    objects sorted by start_line.
    """
    section_map: SectionMap = {}

    for rst_path in sorted(rst_root.rglob(f"*{RST_SUFFIX}")):
        ranges = _scan_rst(rst_path)
        if ranges:
            # key matches the PO location format: "manual/path/to/file.rst"
            rel = rst_path.relative_to(rst_root.parent)
            key = str(rel).replace(PATH_SEP_WINDOWS, PATH_SEP_POSIX)
            section_map[key] = ranges

    return section_map


def _scan_rst(rst_path: Path) -> list[SectionRange]:
    """Return a list of SectionRange for one RST file, sorted by start_line."""
    try:
        lines = rst_path.read_text(encoding=FILE_ENCODING, errors=ENCODING_ERROR_MODE).splitlines()
    except OSError:
        return []

    ranges: list[SectionRange] = []
    n = len(lines)

    for i in range(n - 1):
        title_line = lines[i]
        under_line = lines[i + 1]
        title_stripped = title_line.rstrip()

        if not title_stripped:
            continue
        if not _is_underline(under_line, len(title_stripped)):
            continue
        # Check the title line itself isn't an underline (avoid double-underline headings
        # where the overline is mistaken for a title)
        if _is_underline(title_line, 1):
            continue

        anchor = heading_to_anchor(title_stripped)
        # start_line is 1-based; underline is at i+1 (0-based) → line i+2 (1-based)
        start = i + 2
        ranges.append(SectionRange(
            start_line=start,
            end_line=n + 1,   # placeholder; filled below
            anchor=anchor,
            title=title_stripped,
        ))

    # Fill end_line: each section ends where the next starts (or EOF+1)
    if ranges:
        fixed: list[SectionRange] = []
        for idx, sr in enumerate(ranges):
            end = ranges[idx + 1].start_line if idx + 1 < len(ranges) else n + 1
            fixed.append(SectionRange(
                start_line=sr.start_line,
                end_line=end,
                anchor=sr.anchor,
                title=sr.title,
            ))
        return fixed

    return []


def resolve_section_key(
    section_map: SectionMap,
    rst_rel_path: str,
    line_no: int,
) -> str:
    """Return the HTML anchor slug for the section containing *line_no*, or ''."""
    ranges = section_map.get(rst_rel_path, [])
    if not ranges:
        return EMPTY_STRING
    if not line_no:  # None or 0 means no line info — fall back to first section
        return ranges[0].anchor
    starts = [r.start_line for r in ranges]
    idx = bisect.bisect_right(starts, line_no) - 1
    if idx < 0:
        return EMPTY_STRING
    return ranges[idx].anchor
