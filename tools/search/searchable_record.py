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
    """Parsed search request from the client (URL query params → this record).

    Parameters
    ----------
    query          : raw query string; treated as regex pattern when regex=True
    regex          : treat query as a regex pattern (default True)
    case_sensitive : case-sensitive matching (default False)
    whole_word     : only accept matches not in the middle of a word (default False);
                     implemented as a post-filter on boundary characters, not \b
    field          : which PO field(s) to search: "msgid" | "msgstr" | "both"
    limit          : maximum total hits before the SSE stream closes early
    lang           : language code — selects which pickled index to load
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
        """Construct from a parsed URL query-string dict (urllib.parse.parse_qs)."""
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

        def _bool(param: str, default: bool) -> bool:
            val = qs.get(param, [None])[0]
            if val is None:
                return default
            return val.lower() not in ("0", "false", "no", EMPTY_STRING)

        return cls(
            query=query,
            regex=_bool(QS_REGEX, True),
            case_sensitive=_bool(QS_CASE_SENSITIVE, False),
            whole_word=_bool(QS_WHOLE_WORD, False),
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
