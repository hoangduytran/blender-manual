"""Pure extraction, validation and PO/pickle assembly for repeatable records.

This module holds the framework-free core of the repeatable-record extension:
message filtering, English-hint validation, record construction, and the
serialisable envelope / Babel catalogue builders.  Everything here is a pure
function (or operates only on docutils nodes passed in), so it is unit-testable
without a running Sphinx application.  The Sphinx event wiring and DOM mutation
live in ``repeatable_builder``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Iterator

from babel.messages.catalog import Catalog
from docutils import nodes
from sphinx import addnodes
from sphinx.util.nodes import extract_messages

from _doctree_extract import RelSource, nearest_section_id
from repeatable_record import RepeatableRecord  # type: ignore[import-not-found]

from common.constants import (  # type: ignore[import-not-found]
    ELLIPSIS_TERMINATOR,
    EMPTY_STRING,
    HINT_CLOSE_BRACKET,
    HINT_OPEN_BRACKET,
    HintSide,
    PickleEnvelopeKey,
    PO_LOCATION_UP_PREFIX,
    REPEATABLE_NODE_COMMENT_PREFIX,
    REPEATABLE_NODE_TAGNAMES,
    REPEATABLE_PO_DOMAIN,
    REPEATABLE_SCHEMA_VERSION,
    RepeatableTag,
    SENTENCE_TERMINATOR,
    SOURCE_LINE_UNKNOWN,
)

# docutils marks a translated node with node['translated'] == True.
TRANSLATED_FLAG = "translated"

# Babel Catalog.add() uses None for "no message context".
NO_MSGCTXT = None


@dataclass(frozen=True)
class ExtractionContext:
    """Per-document inputs needed to build records, injected at the boundary.

    Attributes:
        docname: Sphinx docname of the document being extracted.
        html_page: Served URL of the document, e.g. ``"/vi/addons/x.html"``.
        rel_source: Maps a node's absolute source path to a repo-relative
            RST path (see :func:`_doctree_extract.make_rel_source`).
    """
    docname: str
    html_page: str
    rel_source: RelSource


@dataclass(frozen=True)
class TerminalHint:
    """A validated terminal ``<lead> [<bracket>]`` split of node text.

    The bracket is always the pilled secondary reading; ``side`` records which
    side carried the source msgid, so the renderer can pick the pill class.
    """
    lead: str          # text before the opening bracket
    bracket: str       # the bracketed secondary reading (always pilled)
    side: HintSide     # which side equals the source msgid


# ---------------------------------------------------------------------------
# Text predicates
# ---------------------------------------------------------------------------

def normalized(text: str) -> str:
    """Collapse all runs of whitespace to single spaces and strip the ends."""
    return " ".join(text.split())


def is_repeatable_tag(tagname: str) -> bool:
    """True when *tagname* is in the repeatable allowlist."""
    return tagname in REPEATABLE_NODE_TAGNAMES


def is_sentence_like(msgid: str) -> bool:
    """True when *msgid* reads as a sentence (ends with a period).

    An ellipsis terminator (``...``) marks an operator/menu label such as
    "Move..." and is *not* sentence-like, so it is retained.
    """
    stripped = msgid.rstrip()
    if stripped.endswith(ELLIPSIS_TERMINATOR):
        return False
    return stripped.endswith(SENTENCE_TERMINATOR)


def is_repeatable_message(node: nodes.Element, msgid: str) -> bool:
    """True when (node, msgid) is an eligible repeatable occurrence."""
    has_text = bool(msgid and msgid.strip())
    is_allowed_tag = is_repeatable_tag(node.tagname)
    return has_text and is_allowed_tag and not is_sentence_like(msgid)


# ---------------------------------------------------------------------------
# Translation state and hint validation
# ---------------------------------------------------------------------------

def node_msgstr(node: nodes.Element, msgid: str) -> str:
    """Return the resolved translated text of *node*, or ``""`` if untranslated.

    The i18n transform sets ``node['translated']`` and leaves ``node.rawsource``
    (the source *msgid*) intact while ``node.astext()`` yields the translation.
    A node flagged translated but whose text equals the source is treated as
    untranslated (empty msgstr).
    """
    is_translated = node.get(TRANSLATED_FLAG) is True
    if not is_translated:
        return EMPTY_STRING
    text = node.astext()
    is_identical_to_source = normalized(text) == normalized(msgid)
    if is_identical_to_source:
        return EMPTY_STRING
    return text


def classify_terminal_hint(text: str, msgid: str) -> "TerminalHint | None":
    """Classify a terminal ``<lead> [<bracket>]`` reading-hint against *msgid*.

    The text must end with exactly one bracket pair and have non-empty lead and
    bracket.  The bracket is the pilled secondary reading; the *side* is decided
    by which part is whitespace-equal (case-sensitive) to *msgid*:

    * bracket == msgid  -> :attr:`HintSide.ENGLISH_BRACKET` (body content).
    * lead == msgid     -> :attr:`HintSide.ENGLISH_LEAD` (glossary term).

    Returns ``None`` for nested/empty/compound brackets or when neither side
    matches the source msgid.
    """
    stripped = text.rstrip()
    has_single_pair = (
        stripped.endswith(HINT_CLOSE_BRACKET)
        and stripped.count(HINT_OPEN_BRACKET) == 1
        and stripped.count(HINT_CLOSE_BRACKET) == 1
    )
    if not has_single_pair:
        return None
    open_index = stripped.index(HINT_OPEN_BRACKET)
    bracket = stripped[open_index + 1:-1]
    lead = text[:open_index]
    has_valid_parts = bool(bracket.strip()) and bool(lead.strip())
    if not has_valid_parts:
        return None

    normalized_msgid = normalized(msgid)
    if normalized(bracket) == normalized_msgid:
        return TerminalHint(lead=lead, bracket=bracket, side=HintSide.ENGLISH_BRACKET)
    if normalized(lead) == normalized_msgid:
        return TerminalHint(lead=lead, bracket=bracket, side=HintSide.ENGLISH_LEAD)
    return None


# ---------------------------------------------------------------------------
# Record construction
# ---------------------------------------------------------------------------

def _node_line(node: nodes.Element) -> int:
    """Source line of *node*, or the unknown-line sentinel."""
    return node.line if node.line is not None else SOURCE_LINE_UNKNOWN


def is_in_glossary(node: nodes.Node) -> bool:
    """True when *node* is inside a ``.. glossary::`` directive.

    The directive wraps its definition list in an ``addnodes.glossary`` node, so
    every glossary term has one as an ancestor.
    """
    current: nodes.Node | None = node.parent
    while current is not None:
        if isinstance(current, addnodes.glossary):
            return True
        current = current.parent
    return False


def _make_record(
    node: nodes.Element,
    msgid: str,
    msgstr: str,
    tagname: str,
    context: ExtractionContext,
    is_glossary: bool = False,
) -> RepeatableRecord:
    """Build a single record (ordinal is assigned later by the caller)."""
    return RepeatableRecord(
        docname=context.docname,
        source_path=context.rel_source(node.source, context.docname),
        source_line=_node_line(node),
        node_tagname=tagname,
        msgid=msgid,
        msgstr=msgstr,
        html_page=context.html_page,
        section_id=nearest_section_id(node),
        ordinal=0,
        is_glossary=is_glossary,
    )


def _direct_node_drafts(
    doctree: nodes.document, context: ExtractionContext
) -> Iterator[RepeatableRecord]:
    """Yield records for allowlisted TextElement nodes via extract_messages."""
    for node, msgid in extract_messages(doctree):
        if is_repeatable_message(node, msgid):
            yield _make_record(
                node, msgid, node_msgstr(node, msgid), node.tagname, context,
                is_glossary=is_in_glossary(node),
            )


def _toctree_drafts(
    doctree: nodes.document, context: ExtractionContext
) -> Iterator[RepeatableRecord]:
    """Yield records for toctree captions and explicit entry titles.

    Sphinx replaces ``addnodes.toctree`` during the resolve phase, so this must
    run at read time.  Only the unambiguous source strings (``rawcaption`` /
    ``rawentries``) are captured as msgid; the paired translated value, when it
    differs, becomes the msgstr.
    """
    for toctree in doctree.findall(addnodes.toctree):
        yield from _toctree_caption_draft(toctree, context)
        yield from _toctree_entry_drafts(toctree, context)


def _toctree_caption_draft(
    toctree: addnodes.toctree, context: ExtractionContext
) -> Iterator[RepeatableRecord]:
    source = toctree.get("rawcaption")
    if not (source and source.strip()) or is_sentence_like(source):
        return
    translated = toctree.get("caption") or EMPTY_STRING
    msgstr = translated if normalized(translated) != normalized(source) else EMPTY_STRING
    yield _make_record(toctree, source, msgstr, RepeatableTag.TOCTREE.value, context)


def _toctree_entry_drafts(
    toctree: addnodes.toctree, context: ExtractionContext
) -> Iterator[RepeatableRecord]:
    raw_entries = toctree.get("rawentries") or []
    entries = toctree.get("entries") or []
    for index, raw_title in enumerate(raw_entries):
        if not (raw_title and raw_title.strip()) or is_sentence_like(raw_title):
            continue
        translated_title = _entry_title_at(entries, index)
        is_translated = bool(translated_title) and normalized(translated_title) != normalized(raw_title)
        msgstr = translated_title if is_translated else EMPTY_STRING
        yield _make_record(toctree, raw_title, msgstr, RepeatableTag.TOCTREE.value, context)


def _entry_title_at(entries: list, index: int) -> str:
    """Return the title of toctree *entries[index]*, or ``""`` if absent."""
    is_in_range = 0 <= index < len(entries)
    if not is_in_range:
        return EMPTY_STRING
    title = entries[index][0]
    return title or EMPTY_STRING


def extract_repeatable_records(
    doctree: nodes.document, context: ExtractionContext
) -> list[RepeatableRecord]:
    """Extract every repeatable occurrence in *doctree* with stable ordinals.

    Ordinals are a deterministic per-document traversal index (direct nodes
    first, then toctree records) so two occurrences sharing a source line stay
    distinguishable across rebuilds.
    """
    drafts = [
        *_direct_node_drafts(doctree, context),
        *_toctree_drafts(doctree, context),
    ]
    return [replace(draft, ordinal=index) for index, draft in enumerate(drafts)]


# ---------------------------------------------------------------------------
# Grouping and serialisation
# ---------------------------------------------------------------------------

def _record_sort_key(record: RepeatableRecord) -> tuple:
    """Deterministic ordering within a document."""
    return (record.source_line, record.node_tagname, record.ordinal, record.msgid)


def group_records_by_doc(
    records: Iterable[RepeatableRecord],
) -> dict[str, tuple[RepeatableRecord, ...]]:
    """Group records by docname, each group sorted deterministically."""
    grouped: dict[str, list[RepeatableRecord]] = {}
    for record in records:
        grouped.setdefault(record.docname, []).append(record)
    return {
        docname: tuple(sorted(grouped[docname], key=_record_sort_key))
        for docname in sorted(grouped)
    }


def build_envelope(
    records_by_doc: dict[str, tuple[RepeatableRecord, ...]], language: str
) -> dict:
    """Build the versioned gzip-pickle envelope dict."""
    return {
        PickleEnvelopeKey.SCHEMA_VERSION.value: REPEATABLE_SCHEMA_VERSION,
        PickleEnvelopeKey.LANGUAGE.value: language,
        PickleEnvelopeKey.RECORDS_BY_DOC.value: records_by_doc,
    }


# ---------------------------------------------------------------------------
# PO catalogue assembly
# ---------------------------------------------------------------------------

def _po_location(record: RepeatableRecord) -> tuple[str, int]:
    """PO location tuple ``("../../manual/<docname>.rst", line)``."""
    return (PO_LOCATION_UP_PREFIX + record.source_path, record.source_line)


def _resolve_msgstr(records: list[RepeatableRecord]) -> tuple[str, list[str]]:
    """Pick the deterministic msgstr for a msgid group; report any conflicts.

    Returns the winning (first sorted) non-empty msgstr and the sorted list of
    all distinct non-empty msgstr values — a length > 1 signals a conflict the
    caller should warn about.
    """
    distinct = sorted({r.msgstr for r in records if r.msgstr})
    winner = distinct[0] if distinct else EMPTY_STRING
    return winner, distinct


def _node_comments(records: list[RepeatableRecord]) -> list[str]:
    """Sorted, de-duplicated ``repeatable-node: <tag>`` automatic comments."""
    tags = sorted({r.node_tagname for r in records})
    return [REPEATABLE_NODE_COMMENT_PREFIX + tag for tag in tags]


def _merged_locations(records: list[RepeatableRecord]) -> list[tuple[str, int]]:
    """Sorted, de-duplicated PO locations for a msgid group."""
    return sorted({_po_location(r) for r in records})


@dataclass(frozen=True)
class CatalogConflict:
    """One msgid with more than one distinct non-empty translation."""
    msgid: str
    values: tuple[str, ...]


def build_catalog(
    records_by_doc: dict[str, tuple[RepeatableRecord, ...]],
    language: str,
    project: str,
    version: str,
) -> tuple[Catalog, list[CatalogConflict]]:
    """Build a Babel catalogue from the merged record snapshot.

    Groups every record by msgid (v1 uses no msgctxt), merging locations and
    node-tag comments and choosing a deterministic msgstr per msgid.

    Returns:
        The populated :class:`~babel.messages.catalog.Catalog` and the list of
        detected msgstr conflicts (for the caller to log).
    """
    by_msgid: dict[str, list[RepeatableRecord]] = {}
    for records in records_by_doc.values():
        for record in records:
            by_msgid.setdefault(record.msgid, []).append(record)

    catalog = Catalog(
        locale=language,
        domain=REPEATABLE_PO_DOMAIN,
        project=project,
        version=version,
        fuzzy=False,
    )
    conflicts: list[CatalogConflict] = []
    for msgid in sorted(by_msgid):
        group = by_msgid[msgid]
        msgstr, distinct = _resolve_msgstr(group)
        if len(distinct) > 1:
            conflicts.append(CatalogConflict(msgid=msgid, values=tuple(distinct)))
        catalog.add(
            msgid,
            string=msgstr,
            locations=_merged_locations(group),
            auto_comments=_node_comments(group),
            context=NO_MSGCTXT,
        )
    return catalog, conflicts
