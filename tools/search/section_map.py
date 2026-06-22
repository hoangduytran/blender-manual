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


def _read_rst_lines(rst_path: Path) -> list[str]:
    """Read *rst_path* into a list of lines, or ``[]`` if it cannot be read.

    The I/O boundary for section scanning: an unreadable file yields "no lines"
    rather than raising, so one bad file never aborts a whole index build.

    Args:
        rst_path: Path to the ``.rst`` source file.

    Returns:
        list[str]: The file's lines (newline-stripped), or ``[]`` on ``OSError``.
    """
    try:
        text = rst_path.read_text(encoding=FILE_ENCODING, errors=ENCODING_ERROR_MODE)
    except OSError:
        return []
    return text.splitlines()


def _heading_at(lines: list[str], i: int) -> SectionRange | None:
    """Return the heading defined by the line pair at index *i*, else ``None``.

    A heading is a non-blank *title* line (``lines[i]``) immediately followed by
    an RST *underline* of matching width (``lines[i + 1]``; see
    :func:`_is_underline`). Pure — depends only on its arguments.

    Args:
        lines: All lines of the file.
        i: Index of the candidate title line; ``lines[i + 1]`` must exist.

    Returns:
        SectionRange | None: A range with a **placeholder** ``end_line`` (fixed
        later by :func:`_fill_section_extents`) when a heading is found here,
        otherwise ``None``.
    """
    title_line = lines[i]
    under_line = lines[i + 1]
    title_stripped = title_line.rstrip()

    is_blank_title = not title_stripped
    if is_blank_title:
        return None
    has_underline = _is_underline(under_line, len(title_stripped))
    if not has_underline:
        return None
    # Over+underline ("===\nTitle\n===") heading: this pair is the overline,
    # not a real title — skip so the genuine title pair is used instead.
    title_is_overline = _is_underline(title_line, 1)
    if title_is_overline:
        return None

    # start_line is 1-based; underline sits at index i+1 → content at line i+2.
    start = i + 2
    return SectionRange(
        start_line=start,
        end_line=start,   # placeholder; back-filled by _fill_section_extents
        anchor=heading_to_anchor(title_stripped),
        title=title_stripped,
    )


def _detect_headings(lines: list[str]) -> list[SectionRange]:
    """Collect every heading in *lines*, in document order (placeholder extents).

    Pure pass-1 scanner: delegates each candidate line pair to
    :func:`_heading_at`. The returned ranges still need
    :func:`_fill_section_extents` to set their ``end_line``.
    """
    headings: list[SectionRange] = []
    for i in range(len(lines) - 1):
        heading = _heading_at(lines, i)
        if heading is not None:
            headings.append(heading)
    return headings


def _fill_section_extents(
    headings: list[SectionRange],
    total_lines: int,
) -> list[SectionRange]:
    """Set each section's ``end_line`` to the next section's start (or EOF + 1).

    Pure pass-2 step: a section's extent is only known once the following
    heading is seen, so the placeholder ``end_line`` values from
    :func:`_detect_headings` are replaced here to form correct half-open
    ``[start_line, end_line)`` spans.

    Args:
        headings: Headings in document order, each with a placeholder extent.
        total_lines: Line count of the file; the last section ends at
            ``total_lines + 1``.

    Returns:
        list[SectionRange]: Ranges with finalised extents (``[]`` when
        *headings* is empty).
    """
    sections: list[SectionRange] = []
    for idx, heading in enumerate(headings):
        is_last_section = idx + 1 >= len(headings)
        end = total_lines + 1 if is_last_section else headings[idx + 1].start_line
        sections.append(SectionRange(
            start_line=heading.start_line,
            end_line=end,
            anchor=heading.anchor,
            title=heading.title,
        ))
    return sections


def _scan_rst(rst_path: Path) -> list[SectionRange]:
    """Parse one RST file into the section ranges its headings define.

    Orchestration only: read the file, detect its headings, then finalise their
    extents. Each returned range's ``[start_line, end_line)`` spans from just
    after a heading underline up to (but not including) the next heading, so any
    source line maps to exactly one section. Line numbers are 1-based to match
    PO/Sphinx location references. Empty when the file has no headings or cannot
    be read.

    Args:
        rst_path: Path to the ``.rst`` source file to scan.

    Returns:
        list[SectionRange]: Sections sorted by ``start_line`` ascending.
    """
    lines = _read_rst_lines(rst_path)
    headings = _detect_headings(lines)
    return _fill_section_extents(headings, len(lines))


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
