"""Parallel PO search with SSE streaming.

Each query is dispatched to a persistent multiprocessing Pool (§18.2).
The caller iterates batches of SearchHit as each worker finishes —
use with Pool.imap_unordered for minimum first-hit latency.

Search options (all combinable):
  regex=True      — query treated as regex pattern (default); falls back to
                    substring on re.error
  case_sensitive  — case-sensitive match (default False → IGNORECASE)
  whole_word      — post-filter: reject match if the char immediately before
                    match_start or at match_end is alphanumeric or underscore
"""

from __future__ import annotations

import multiprocessing
import os
import re
import threading
from typing import Iterator, Optional
from urllib.parse import quote

from .searchable_record import SearchHit, SearchableRecord, SearchRequest
from common.constants import (  # type: ignore[import-not-found]
    EMPTY_STRING,
    FIELD_BOTH,
    FIELD_MSGID,
    FIELD_MSGSTR,
    FRAGMENT_URL_MAX_HIGHLIGHT_CHARS,
    HIT_SCORE_BASE,
    HIT_SCORE_EXACT,
    HIT_SCORE_MSGSTR_BONUS,
    SNIPPET_CONTEXT_CHARS,
)


# ---------------------------------------------------------------------------
# Fragment URL and snippet helpers
# ---------------------------------------------------------------------------

def make_fragment_url(html_page: str, section_key: str, highlight_text: str) -> str:
    """Build a Text Fragment URL for browser-native text highlighting."""
    encoded = quote(highlight_text[:FRAGMENT_URL_MAX_HIGHLIGHT_CHARS], safe=EMPTY_STRING)
    anchor = f"#{section_key}" if section_key and not section_key.startswith("#") else section_key
    return f"{html_page}{anchor}:~:text={encoded}"


def make_snippet(
    text: str,
    match_start: int,
    match_end: int,
    context: int = SNIPPET_CONTEXT_CHARS,
) -> str:
    """Return a ~240-char context snippet with the match in ``<mark>`` tags."""
    lo = max(0, match_start - context)
    hi = min(len(text), match_end + context)
    prefix = "…" if lo > 0 else ""
    suffix = "…" if hi < len(text) else ""
    before = _html_escape(text[lo:match_start])
    marked = f"<mark>{_html_escape(text[match_start:match_end])}</mark>"
    after = _html_escape(text[match_end:hi])
    return prefix + before + marked + after + suffix


def _html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------------------
# Matcher builder
# ---------------------------------------------------------------------------

def _compile_matcher(pattern: str, flags: int):
    """Return a callable(text) → match-object-or-None.

    Falls back to plain substring search when the pattern is not valid regex.
    """
    try:
        return re.compile(pattern, flags).search
    except re.error:
        needle = pattern.lower() if (flags & re.IGNORECASE) else pattern

        def _fallback(text: str):
            target = text.lower() if (flags & re.IGNORECASE) else text
            return _SubstringMatch(needle, target)

        return _fallback


class _SubstringMatch:
    """Minimal match-object replacement for plain-substring fallback."""
    __slots__ = ("_start", "_end", "_found")

    def __init__(self, needle: str, haystack: str) -> None:
        idx = haystack.find(needle)
        self._found = idx >= 0
        self._start = idx
        self._end = idx + len(needle) if idx >= 0 else 0

    def __bool__(self) -> bool:
        return self._found

    def start(self) -> int:
        return self._start

    def end(self) -> int:
        return self._end


# ---------------------------------------------------------------------------
# Whole-word boundary check
# ---------------------------------------------------------------------------

def _at_word_boundary(text: str, start: int, end: int) -> bool:
    """Return True when the span [start:end] is NOT in the middle of a word.

    Checks the character immediately before ``start`` and the character at
    ``end``.  If either is alphanumeric or an underscore the span is
    considered mid-word and the function returns False.

    Python's str.isalnum() is Unicode-aware, so Vietnamese letters count as
    word characters — "khiển" is a word, and matching "iển" inside it would
    be rejected.
    """
    if start > 0:
        prev = text[start - 1]
        if prev.isalnum() or prev == "_":
            return False
    if end < len(text):
        nxt = text[end]
        if nxt.isalnum() or nxt == "_":
            return False
    return True


# ---------------------------------------------------------------------------
# Per-batch worker (top-level so multiprocessing can pickle it by name)
# ---------------------------------------------------------------------------

def search_batch(args: tuple) -> list[SearchHit]:
    """Search one batch of SearchableRecord objects.

    ``args`` is a tuple:
      ``(batch, query, regex, case_sensitive, whole_word, field, limit)``

    Two matchers run per record:
    1. Exact   — operates on the original NFC text (tone-aware).
    2. Stripped — operates on NFD-stripped text so queries typed without an
       IME (e.g. ``trinh bo``) still match accented records (``trình bổ``).

    Whole-word filter (when whole_word=True):
      After a regex/substring match is found, the characters immediately
      before match_start and at match_end are inspected.  The hit is
      discarded if either is alphanumeric or an underscore.
    """
    batch, query, regex, case_sensitive, whole_word, field, limit = args

    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = query if regex else re.escape(query)
    matcher = _compile_matcher(pattern, flags)

    hits: list[SearchHit] = []
    for rec in batch:
        if len(hits) >= limit:
            break
        result = _record_matches(rec, field, matcher)
        if result is None:
            continue
        match_obj, match_field, matched_text = result

        # Whole-word post-filter: reject if prev/next char is alphanumeric.
        if whole_word and not _at_word_boundary(matched_text, match_obj.start(), match_obj.end()):
            continue

        # Use only the matched span for the Text Fragment so the browser can
        # find and highlight it in the rendered HTML (which has no RST markup).
        match_span = matched_text[match_obj.start():match_obj.end()]
        # Score: exact phrase match (span == query) ranks highest; translation
        # field (msgstr) ranks above source field (msgid) for the target language.
        exact = match_span.strip().lower() == query.strip().lower()
        score = (HIT_SCORE_EXACT if exact else HIT_SCORE_BASE) + (HIT_SCORE_MSGSTR_BONUS if match_field == FIELD_MSGSTR else 0.0)

        for page, key in zip(rec.html_pages, rec.section_keys):
            fragment = make_fragment_url(page, key, match_span)
            snip = make_snippet(matched_text, match_obj.start(), match_obj.end())
            hits.append(SearchHit(
                msgid=rec.msgid,
                msgstr=rec.msgstr,
                html_page=page,
                section_key=f"#{key}" if key and not key.startswith("#") else key,
                fragment_url=fragment,
                snippet=snip,
                match_field=match_field,
                score=score,
            ))
            if len(hits) >= limit:
                break
    return hits


def _record_matches(
    rec: SearchableRecord,
    field: str,
    matcher,
):
    """Return (match_object, match_field, matched_text) or None.

    Two passes per record:
    1. Exact NFC match on original text (tone-aware).
    2. Stripped fallback on pre-computed NFD-stripped text so queries typed
       without an IME (e.g. "dang hoat dong") match accented records
       ("Đang Hoạt Động").  The snippet in the result always shows the
       original accented text, not the stripped form.
    """
    if field in (FIELD_MSGID, FIELD_BOTH):
        m = matcher(rec.msgid)
        if m:
            return m, FIELD_MSGID, rec.msgid
        # Stripped fallback: re-run matcher on stripped text, but report the
        # match position mapped back onto the original so the snippet is readable.
        if rec.msgid_stripped:
            ms = matcher(rec.msgid_stripped)
            if ms:
                return ms, FIELD_MSGID, rec.msgid_stripped

    if field in (FIELD_MSGSTR, FIELD_BOTH):
        m = matcher(rec.msgstr)
        if m:
            return m, FIELD_MSGSTR, rec.msgstr
        if rec.msgstr_stripped:
            ms = matcher(rec.msgstr_stripped)
            if ms:
                return ms, FIELD_MSGSTR, rec.msgstr_stripped

    return None


# ---------------------------------------------------------------------------
# Persistent Pool (§18.2)
# ---------------------------------------------------------------------------

_pool: Optional[multiprocessing.Pool] = None
_pool_lock = threading.Lock()


def get_pool() -> multiprocessing.Pool:
    """Return the long-lived shared worker pool, creating it on first call."""
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                n = max(1, (os.cpu_count() or 2) - 2)
                _pool = multiprocessing.Pool(n)
    return _pool


def shutdown_pool() -> None:
    """Graceful pool shutdown — call from server teardown."""
    global _pool
    if _pool is not None:
        _pool.terminate()
        _pool.join()
        _pool = None


# ---------------------------------------------------------------------------
# SSE orchestration
# ---------------------------------------------------------------------------

from .index_loader import LoadedIndex


def run_parallel_search(
    idx: LoadedIndex,
    req: SearchRequest,
) -> Iterator[list[SearchHit]]:
    """Yield batches of SearchHit as each worker process finishes.

    Uses Pool.imap_unordered so the caller receives results from the fastest
    worker first — ideal for SSE streaming where the first hits should arrive
    in ~50–150 ms.

    Yields
    ------
    list[SearchHit]  — one yield per worker batch that returned ≥ 1 hit
    """
    if not req.query:
        return

    limit_per_batch = max(1, req.limit // max(1, len(idx.batches)))
    args = [
        (batch, req.query, req.regex, req.case_sensitive, req.whole_word, req.field, limit_per_batch)
        for batch in idx.batches
    ]

    pool = get_pool()
    total = 0
    for hits in pool.imap_unordered(search_batch, args):
        if hits:
            remaining = req.limit - total
            if remaining <= 0:
                break
            batch = hits[:remaining]
            total += len(batch)
            yield batch
            if total >= req.limit:
                break
