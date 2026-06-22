"""Data model: SearchRequest, SearchableRecord, SearchHit.

All classes are pure dataclasses — zero I/O, zero dependencies
beyond the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from common.constants import (  # type: ignore[import-not-found]
    EMPTY_STRING,
    HIT_SCORE_BASE,
    QS_CASE_SENSITIVE,
    QS_FIELD,
    QS_LANG,
    QS_LIMIT,
    QS_QUERY,
    QS_REGEX,
    QS_WHOLE_WORD,
    SEARCH_DEFAULT_FIELD,
    SEARCH_DEFAULT_LANG,
    SEARCH_DEFAULT_LIMIT,
    SearchField,
)


@dataclass(frozen=True)
class SearchRequest:
    """One immutable search request: the client's URL query params, normalised.

    A boundary value object (DTO) produced from the ``/api/search`` query
    string by :meth:`from_qs` and consumed by the searcher. Frozen, so it is
    hashable and safe to share across worker threads; to derive a variant,
    use :func:`dataclasses.replace` (e.g. serve_docs forces ``field=MSGID``
    for the source language) rather than mutating in place.

    Attributes:
        query (str): Raw query text. Interpreted as a regular-expression
            pattern when ``regex`` is True, otherwise as a literal substring.
        regex (bool): Treat ``query`` as a regex pattern. Default True.
        case_sensitive (bool): Match case-sensitively. Default False.
        whole_word (bool): Reject matches that fall in the middle of a word.
            Default False. Implemented as a post-filter on the characters
            bordering the match, not via a ``\\b`` regex anchor, so it also
            works for non-ASCII (e.g. Vietnamese) text.
        field (SearchField): Which PO field(s) to search — ``MSGID``,
            ``MSGSTR``, or ``BOTH``. Default :data:`SEARCH_DEFAULT_FIELD`.
        limit (int): Maximum total hits before the SSE stream closes early.
            Default :data:`SEARCH_DEFAULT_LIMIT`.
        lang (str): Language code; selects which pickled index to load.
            Default :data:`SEARCH_DEFAULT_LANG`.
    """
    query: str
    regex: bool = True
    case_sensitive: bool = False
    whole_word: bool = False
    field: SearchField = SEARCH_DEFAULT_FIELD
    limit: int = SEARCH_DEFAULT_LIMIT
    lang: str = SEARCH_DEFAULT_LANG

    @classmethod
    def from_qs(cls, qs: dict[str, list[str]]) -> "SearchRequest":
        """Build a request from a parsed URL query string.

        Args:
            qs: The dict returned by :func:`urllib.parse.parse_qs` — each key
                maps to a list of raw string values; only the first value of
                each key is used.

        Returns:
            SearchRequest: A request with missing params filled from the
            module defaults.

        Notes:
            Fault-tolerant by design (it parses untrusted client input): an
            unknown ``field`` falls back to ``SearchField.BOTH`` and a
            non-integer ``limit`` falls back to the default, rather than
            raising. Boolean flags accept ``0/false/no`` and empty as false
            (see the nested ``parse_bool_flag``); ``query`` is
            whitespace-stripped.
        """
        query = qs.get(QS_QUERY, [EMPTY_STRING])[0].strip()
        lang = qs.get(QS_LANG, [SEARCH_DEFAULT_LANG])[0]
        raw_field = qs.get(QS_FIELD, [SEARCH_DEFAULT_FIELD])[0]
        try:
            field = SearchField(raw_field)
        except ValueError:
            field = SearchField.BOTH
        try:
            limit = int(qs.get(QS_LIMIT, [str(SEARCH_DEFAULT_LIMIT)])[0])
        except ValueError:
            limit = SEARCH_DEFAULT_LIMIT

        def parse_bool_flag(param: str, default: bool) -> bool:
            """Parse query param *param* as a boolean, or return *default* if absent."""
            raw_value = qs.get(param, [None])[0]
            if raw_value is None:
                return default
            falsy_values = ("0", "false", "no", EMPTY_STRING)
            is_truthy = raw_value.lower() not in falsy_values
            return is_truthy

        return cls(
            query=query,
            regex=parse_bool_flag(QS_REGEX, True),
            case_sensitive=parse_bool_flag(QS_CASE_SENSITIVE, False),
            whole_word=parse_bool_flag(QS_WHOLE_WORD, False),
            field=field,
            limit=limit,
            lang=lang,
        )


@dataclass(frozen=True)
class SectionRange:
    """One contiguous RST section: heading at start_line, ends before end_line."""
    start_line: int   # 1-based line of the heading underline
    end_line: int     # 1-based line of the next heading (or EOF + 1)
    anchor: str       # HTML anchor slug, e.g. "editors-3dview-3d-cursor"
    title: str        # plain heading text, e.g. "3D Cursor"


@dataclass
class SearchableRecord:
    """One unique msgid from blender_manual.po with all resolved page/section refs.

    locations[i], html_pages[i], section_keys[i] are parallel lists —
    index i points to the same occurrence of this msgid in the manual.

    msgid_stripped / msgstr_stripped are pre-computed at index-build time so
    the searcher never calls _strip_tones() on record fields at query time.
    """
    msgid: str
    msgstr: str
    msgid_stripped: str     # _strip_tones(msgid) — built once by index_builder
    msgstr_stripped: str    # _strip_tones(msgstr) — built once by index_builder
    locations: list[tuple[str, int]]  # (rst_rel_path, line_no)
    html_pages: list[str]             # derived from locations
    section_keys: list[str]           # HTML anchor slug per location
    flags: list[str] = field(default_factory=list)   # e.g. ["fuzzy"]
    msgctxt: str = ""   # gettext message context (msgctxt); "" when none.
                        # PO-derived records leave this empty (the corpus uses
                        # no msgctxt); the doctree extractor sets it if present.


@dataclass(frozen=True)
class SearchHit:
    """One result returned to the client via the SSE stream."""
    msgid: str
    msgstr: str
    html_page: str    # "/vi/editors/3dview/3d_cursor.html"
    section_key: str  # "#cursor-location"
    fragment_url: str # html_page + section_key + ":~:text=…"
    snippet: str      # HTML with <mark>…</mark>; safe to set as innerHTML
    match_field: str  # "msgid" | "msgstr"
    score: float = HIT_SCORE_BASE
