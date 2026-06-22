"""Immutable data model for the repeatable-record extension.

A :class:`RepeatableRecord` is one occurrence of an allowlisted, translatable
node (a title, term, reference, emphasis, …) captured from a translated build.
It is a pure value object: no docutils node references, small, and safely
picklable, so the whole inventory round-trips through a gzip-pickle and a PO
catalogue without dragging the doctree along.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RepeatableRecord:
    """One captured occurrence of a repeatable translatable node.

    Attributes:
        docname: Sphinx docname, e.g. ``"addons/node_wrangler"``.
        source_path: Repo-relative RST path, e.g. ``"manual/addons/node_wrangler.rst"``.
        source_line: 1-based source line, or ``-1`` when the node carries none.
        node_tagname: docutils ``node.tagname`` (a :class:`RepeatableTag` value).
        msgid: The source (English) message — ``node.rawsource`` survives the
            i18n transform, so this is the original even on a translated build.
        msgstr: The resolved translated text, or ``""`` when untranslated or
            identical to the source.
        html_page: Served URL of the page, e.g. ``"/vi/addons/node_wrangler.html"``.
        section_id: Nearest enclosing section anchor (deep-link target), or ``""``.
        ordinal: Deterministic per-document traversal index; disambiguates two
            occurrences that share a source line.

    Notes:
        Stable identity is ``(docname, source_line, node_tagname, ordinal)``.
        There is no pickle-level dedup: one record per occurrence.
    """
    docname: str
    source_path: str
    source_line: int
    node_tagname: str
    msgid: str
    msgstr: str
    html_page: str
    section_id: str
    ordinal: int
