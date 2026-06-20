"""PO file reader backed by sphinx_intl.catalog.load_po.

sphinx_intl's load_po pre-reads the file to detect the charset from the
Catalog's ``Content-Type`` header entry, then re-reads with that charset —
identical to how sphinx-intl itself handles PO files during doc builds.

dump_po (sphinx_intl.catalog.dump_po) is re-exported for callers that
need to write updated PO files back to disk.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from sphinx_intl.catalog import dump_po, load_po  # noqa: F401  (dump_po re-exported)
from common.constants import DOT_SLASH, EMPTY_STRING  # type: ignore[import-not-found]


@dataclass
class POEntry:
    """One non-header entry from a .po file."""
    msgid: str
    msgstr: str
    locations: list[tuple[str, int]] = field(default_factory=list)  # (rst_rel_path, line_no)
    flags: list[str] = field(default_factory=list)


def read_po_file(po_path: Path) -> list[POEntry]:
    """Parse a .po file and return all non-header entries.

    Uses sphinx_intl.catalog.load_po which reads the charset from the
    Catalog's ``Content-Type: text/plain; charset=<enc>`` header so
    non-UTF-8 locales are decoded correctly.

    Location paths have their leading ``../../`` prefix stripped (present in
    locale PO files where the path is relative to the repo root).
    """
    catalog = load_po(str(po_path))

    entries: list[POEntry] = []
    for msg in catalog:
        if not msg.id:
            continue  # skip PO header (empty msgid)

        # babel uses str for simple messages, tuple/list for plurals
        mid = msg.id
        msgid: str = mid if isinstance(mid, str) else (str(mid[0]) if mid else EMPTY_STRING)
        ms = msg.string
        if isinstance(ms, (list, tuple)):
            msgstr: str = str(ms[0]) if ms else EMPTY_STRING
        else:
            msgstr = str(ms) if ms else EMPTY_STRING

        locations: list[tuple[str, int]] = []
        for filepath, lineno in msg.locations:
            clean = filepath.lstrip(DOT_SLASH)   # strip ../../ prefix
            locations.append((clean, lineno or 0))  # babel yields None when no :N in location

        entries.append(POEntry(
            msgid=msgid,
            msgstr=msgstr,
            locations=locations,
            flags=list(msg.flags),
        ))

    return entries
