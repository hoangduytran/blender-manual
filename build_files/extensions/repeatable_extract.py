"""Pure extraction, validation and PO/pickle assembly for repeatable records.

This module holds the framework-free core of the repeatable-record extension:
message filtering, English-hint validation, record construction, and the
serialisable envelope / Babel catalogue builders.  Everything here is a pure
function (or operates only on docutils nodes passed in), so it is unit-testable
without a running Sphinx application.  The Sphinx event wiring and DOM mutation
live in ``repeatable_builder``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from difflib import SequenceMatcher
from typing import Iterable, Iterator

from babel.messages.catalog import Catalog
from docutils import nodes
from docutils.utils import unescape
from sphinx import addnodes
from sphinx.util.nodes import extract_messages

from _doctree_extract import RelSource, nearest_section_id
from repeatable_record import RepeatableRecord  # type: ignore[import-not-found]

from common.constants import (  # type: ignore[import-not-found]
    ELLIPSIS_TERMINATOR,
    EMPTY_STRING,
    HINT_BRACKET_PAIRS,
    HINT_NEAR_MISS_RATIO,
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

_EXPLICIT_REFERENCE_RE = re.compile(
    r"^`(?P<label>[^`<>]+?)\s*<[^<>]+>`_{1,2}$",
    re.DOTALL,
)


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

    lead: str  # text before the opening bracket
    bracket: str  # the bracketed secondary reading (always pilled)
    side: HintSide  # which side equals the source msgid


# ---------------------------------------------------------------------------
# Text predicates
# ---------------------------------------------------------------------------


def normalized(text: str) -> str:
    """Collapse all runs of whitespace to single spaces and strip the ends."""
    return " ".join(text.split())


def explicit_reference_label(msgid: str) -> "str | None":
    """Return the visible source label from one explicit RST link msgid."""
    match = _EXPLICIT_REFERENCE_RE.fullmatch(msgid.strip())
    if match is None:
        return None
    label = unescape(match.group("label")).strip()
    return label or None


def matches_msgid(part: str, msgid: str) -> bool:
    """True when *part* equals *msgid* ignoring whitespace runs and case.

    Case is folded so translator capitalisation drift (e.g. ``Metallic And
    Roughness`` vs the source ``Metallic and Roughness``) still matches; the
    pill text itself is rendered as the translator wrote it.
    """
    return normalized(part).casefold() == normalized(msgid).casefold()


def similarity(part: str, msgid: str) -> float:
    """Similarity ratio of *part* to *msgid* in ``[0.0, 1.0]``.

    Compares whitespace-normalised, case-folded text with
    :class:`difflib.SequenceMatcher` so a near-miss reading-hint (a dropped
    article, a stray space, minor punctuation drift) scores close to 1.0 while
    genuinely different text scores low.  Used as the near-miss gate; an exact
    match (see :func:`matches_msgid`) is handled separately and always wins.
    """
    return SequenceMatcher(
        None, normalized(part).casefold(), normalized(msgid).casefold()
    ).ratio()


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


def split_terminal_group(text: str) -> "tuple[str, str] | None":
    """Split *text* into ``(lead, bracket)`` at its terminal delimiter group.

    Tries each pair in :data:`HINT_BRACKET_PAIRS` (``[]`` then ``()``).  The
    terminal group is the last ``<open>...<close>`` run at the end of the text
    (ignoring trailing whitespace); its content must be non-nested (contain
    neither delimiter of that pair) and both lead and bracket must be non-empty.
    """
    stripped = text.rstrip()
    for open_char, close_char in HINT_BRACKET_PAIRS:
        if not stripped.endswith(close_char):
            continue
        open_index = stripped.rfind(open_char)
        if open_index == -1:
            continue
        bracket = stripped[open_index + 1 : -1]
        is_nested = open_char in bracket or close_char in bracket
        lead = text[:open_index]
        has_valid_parts = bool(bracket.strip()) and bool(lead.strip())
        if is_nested or not has_valid_parts:
            continue
        return lead, bracket
    return None


# Every delimiter character across all recognised bracket pairs.
_HINT_DELIMITER_CHARS = frozenset(
    char for pair in HINT_BRACKET_PAIRS for char in pair
)


def _contains_delimiter(text: str) -> bool:
    """True when *text* contains any recognised bracket delimiter character."""
    return any(char in text for char in _HINT_DELIMITER_CHARS)


def classify_terminal_hint(
    text: str, msgid: str, near_miss_ratio: float = HINT_NEAR_MISS_RATIO
) -> "TerminalHint | None":
    """Classify a terminal ``<lead> <open><bracket><close>`` hint against *msgid*.

    The text must end with a delimiter group (``[]`` or ``()``) whose content
    and lead are non-empty.  The bracket is the pilled secondary reading; the
    *side* is decided by which part carries *msgid* (whitespace- and
    case-insensitive, see :func:`matches_msgid`):

    * bracket == msgid  -> :attr:`HintSide.ENGLISH_BRACKET` (body content).
    * lead == msgid     -> :attr:`HintSide.ENGLISH_LEAD` (glossary term).

    Exact matches win.  Failing that, a *near-miss* — a side whose similarity to
    *msgid* is at least ``near_miss_ratio`` (see :func:`similarity`) — is still
    accepted so a typo'd reading-hint (e.g. a dropped article) is pilled "as
    written"; :func:`classify_hint_mismatch` reports these for the translator.

    Returns ``None`` for nested/empty/compound groups, or when neither side
    matches or comes close to the source msgid.
    """
    split = split_terminal_group(text)
    if split is None:
        return None
    lead, bracket = split

    if matches_msgid(bracket, msgid):
        return TerminalHint(lead=lead, bracket=bracket, side=HintSide.ENGLISH_BRACKET)
    if matches_msgid(lead, msgid):
        return TerminalHint(lead=lead, bracket=bracket, side=HintSide.ENGLISH_LEAD)

    # Near-miss fallback: accept the side closest to msgid if it clears the bar.
    # Only "clean" sides (no other delimiter characters) qualify, so ambiguous
    # compound hints such as "Giao Cắt [Dao] (Intersect [Knife])" stay unpilled.
    bracket_ratio = 0.0 if _contains_delimiter(bracket) else similarity(bracket, msgid)
    lead_ratio = 0.0 if _contains_delimiter(lead) else similarity(lead, msgid)
    if bracket_ratio >= lead_ratio and bracket_ratio >= near_miss_ratio:
        return TerminalHint(lead=lead, bracket=bracket, side=HintSide.ENGLISH_BRACKET)
    if lead_ratio > bracket_ratio and lead_ratio >= near_miss_ratio:
        return TerminalHint(lead=lead, bracket=bracket, side=HintSide.ENGLISH_LEAD)
    return None


def terminal_hint_is_exact(text: str, msgid: str) -> bool:
    """True when *text* has a terminal hint whose carrying side equals *msgid*."""
    split = split_terminal_group(text)
    if split is None:
        return False
    lead, bracket = split
    return matches_msgid(bracket, msgid) or matches_msgid(lead, msgid)


@dataclass(frozen=True)
class HintMismatch:
    """A reading-hint that was pilled as a near-miss, not an exact match.

    Attributes:
        msgid: the faithful English source the hint should have repeated.
        observed: the text the translator actually wrote on the carrying side.
        side: which side carried the (near) match.
        ratio: similarity of *observed* to *msgid* in ``[0.0, 1.0]``.
    """

    msgid: str
    observed: str
    side: HintSide
    ratio: float


def classify_hint_mismatch(
    text: str, msgid: str, near_miss_ratio: float = HINT_NEAR_MISS_RATIO
) -> "HintMismatch | None":
    """Return a :class:`HintMismatch` when *text* pills only via the near-miss path.

    ``None`` when there is no hint, or when the hint is an exact match (nothing
    to report).  Mirrors :func:`classify_terminal_hint` so the report lists
    exactly those hints that were pilled "as written" despite not matching.
    """
    hint = classify_terminal_hint(text, msgid, near_miss_ratio)
    if hint is None or terminal_hint_is_exact(text, msgid):
        return None
    observed = hint.bracket if hint.side == HintSide.ENGLISH_BRACKET else hint.lead
    observed = observed.strip()
    return HintMismatch(
        msgid=msgid, observed=observed, side=hint.side, ratio=similarity(observed, msgid)
    )


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
                node,
                msgid,
                node_msgstr(node, msgid),
                node.tagname,
                context,
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
    msgstr = (
        translated if normalized(translated) != normalized(source) else EMPTY_STRING
    )
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
        is_translated = bool(translated_title) and normalized(
            translated_title
        ) != normalized(raw_title)
        msgstr = translated_title if is_translated else EMPTY_STRING
        yield _make_record(
            toctree, raw_title, msgstr, RepeatableTag.TOCTREE.value, context
        )


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


# ---------------------------------------------------------------------------
# Misaligned reading-hint report
# ---------------------------------------------------------------------------


def collect_hint_mismatches(
    records_by_doc: dict[str, tuple[RepeatableRecord, ...]],
) -> list[tuple[RepeatableRecord, HintMismatch]]:
    """Find every translated record pilled via the near-miss path.

    Returns ``(record, mismatch)`` pairs in deterministic order so the build
    warnings and the text report are stable across runs.
    """
    found: list[tuple[RepeatableRecord, HintMismatch]] = []
    for docname in sorted(records_by_doc):
        for record in records_by_doc[docname]:
            if not record.msgstr:
                continue
            mismatch = classify_hint_mismatch(record.msgstr, record.msgid)
            if mismatch is not None:
                found.append((record, mismatch))
    return found


def format_mismatch_report(
    pairs: list[tuple[RepeatableRecord, HintMismatch]], language: str
) -> str:
    """Render the misaligned-hint pairs as a human-readable text report.

    Grouped by source msgid, each with its merged locations and the distinct
    bracket text the translator wrote, so a translator can find and fix every
    near-miss the build pilled "as written".
    """
    by_msgid: dict[str, list[tuple[RepeatableRecord, HintMismatch]]] = {}
    for record, mismatch in pairs:
        by_msgid.setdefault(mismatch.msgid, []).append((record, mismatch))

    lines = [
        f"# Misaligned reading-hints — {language}",
        "#",
        "# The bracketed reading-hint below does not exactly match its English",
        "# source. It was still pilled using your text, but please correct the",
        "# bracket so it matches the source exactly (whitespace and case aside).",
        "#",
        f"# {len(pairs)} occurrence(s) across {len(by_msgid)} source string(s).",
        "",
    ]
    for msgid in sorted(by_msgid):
        group = by_msgid[msgid]
        wrote = sorted({mismatch.observed for _, mismatch in group})
        locations = sorted(
            {(record.source_path, record.source_line) for record, _ in group}
        )
        lines.append(f"source : {msgid}")
        for observed in wrote:
            lines.append(f"wrote  : {observed}")
        for path, line in locations:
            lines.append(f"  at   : {path}:{line}")
        lines.append("")
    return "\n".join(lines)
