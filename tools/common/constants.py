"""Shared string constants for the blender-manual build and search tools.

Import from here instead of repeating literals so a single change propagates
everywhere.  All values must match the corresponding settings in
``manual/conf.py`` (which ConfigRecord reads at runtime).
"""

from enum import Enum

# ---------------------------------------------------------------------------
# String processing
# ---------------------------------------------------------------------------

EMPTY_STRING: str = ""
DOT_SLASH: str = "./"          # prefix stripped from PO location paths via lstrip

# ---------------------------------------------------------------------------
# File extensions
# ---------------------------------------------------------------------------

RST_SUFFIX: str = ".rst"
HTML_SUFFIX: str = ".html"
PO_SUFFIX: str = ".po"
MO_SUFFIX: str = ".mo"
TEMP_SUFFIX: str = ".tmp"      # suffix for atomic-write temporary files

# ---------------------------------------------------------------------------
# Search / build defaults (mirror manual/conf.py values)
# ---------------------------------------------------------------------------

SEARCH_INDEX_FILENAME: str = "searchindex.pkl.gz"
HTML_BUILDER_NAME: str = "html"
DEFAULT_LANGUAGE: str = "en"

# ---------------------------------------------------------------------------
# Project directory / path segment names
# ---------------------------------------------------------------------------

LOCALE_DIR: str = "locale"
LC_MESSAGES: str = "LC_MESSAGES"
RST_SOURCE_DIR: str = "manual"
PO_CATALOG_NAME: str = "blender_manual"   # gettext_compact value in conf.py
PO_FILENAME: str = "blender_manual.po"

# ---------------------------------------------------------------------------
# Search field identifiers
# ---------------------------------------------------------------------------

class SearchField(str, Enum):
    """Which PO field(s) to match against during a search query.

    Being a str-enum means ``SearchField.MSGID == "msgid"`` is True, so
    existing code that checks ``field in ("msgid", "both")`` works whether
    *field* is a plain string or a SearchField member.
    """
    MSGID = "msgid"
    MSGSTR = "msgstr"
    BOTH = "both"

# Module-level aliases kept for callers that do ``from common.constants import FIELD_BOTH``.
FIELD_MSGID: str = SearchField.MSGID
FIELD_MSGSTR: str = SearchField.MSGSTR
FIELD_BOTH: str = SearchField.BOTH

# ---------------------------------------------------------------------------
# URL query-string parameter names (SearchRequest.from_qs)
# ---------------------------------------------------------------------------

QS_QUERY: str = "q"
QS_LANG: str = "lang"
QS_FIELD: str = "field"
QS_LIMIT: str = "limit"
QS_REGEX: str = "regex"
QS_CASE_SENSITIVE: str = "cs"
QS_WHOLE_WORD: str = "ww"

# ---------------------------------------------------------------------------
# SearchRequest default values
# ---------------------------------------------------------------------------

SEARCH_DEFAULT_FIELD: SearchField = SearchField.BOTH
SEARCH_DEFAULT_LIMIT: int = 200
SEARCH_DEFAULT_LANG: str = "vi"

# ---------------------------------------------------------------------------
# SearchHit scoring weights
#
# Final score = base_or_exact + msgstr_bonus.
# Possible range: 1.0 (partial msgid) · 1.5 (partial msgstr)
#               · 2.0 (exact msgid)  · 2.5 (exact msgstr)
# Higher score → sorted earlier in SSE results.
# ---------------------------------------------------------------------------

HIT_SCORE_BASE: float = 1.0
HIT_SCORE_EXACT: float = 2.0     # span matches query exactly (case-insensitive strip)
HIT_SCORE_MSGSTR_BONUS: float = 0.5  # translation field preferred over source field

# ---------------------------------------------------------------------------
# SearchHit URL / snippet sizing
#
# FRAGMENT_URL_MAX_HIGHLIGHT_CHARS — Text Fragments API payload limit.
#   Browsers have no formal cap but long URLs are silently truncated; 120 chars
#   keeps the :~:text= fragment within safe limits for all major browsers.
#
# SNIPPET_CONTEXT_CHARS — characters of context on EACH side of the match in
#   make_snippet().  Total snippet width ≤ 2×SNIPPET_CONTEXT_CHARS + match_len.
#   At the default of 60, a one-word match yields ~120-char snippets.
# ---------------------------------------------------------------------------

FRAGMENT_URL_MAX_HIGHLIGHT_CHARS: int = 120
SNIPPET_CONTEXT_CHARS: int = 60

# ---------------------------------------------------------------------------
# RST heading scanner (section_map.py)
# ---------------------------------------------------------------------------

RST_UNDERLINE_CHARS: frozenset[str] = frozenset("=-~^\"'#+*<>_")
RST_ANCHOR_NONWORD_RE: str = r"[^\w]+"   # runs of non-word chars → replaced by HYPHEN
HYPHEN: str = "-"

# ---------------------------------------------------------------------------
# Unicode normalization forms
# ---------------------------------------------------------------------------

class UnicodeNormForm(str, Enum):
    """Normalization form identifiers accepted by ``unicodedata.normalize()``.

    Being a str-enum means members can be passed directly as the *form*
    argument without an explicit ``.value`` call.
    """
    NFC  = "NFC"   # Canonical Decomposition → Canonical Composition
    NFD  = "NFD"   # Canonical Decomposition (Vietnamese tone-stripping)
    NFKC = "NFKC"  # Compatibility Decomposition → Canonical Composition
    NFKD = "NFKD"  # Compatibility Decomposition (anchor slug normalisation)

# ---------------------------------------------------------------------------
# Path and file I/O
# ---------------------------------------------------------------------------

PATH_SEP_POSIX: str = "/"
PATH_SEP_WINDOWS: str = "\\"
FILE_ENCODING: str = "utf-8"
ENCODING_ERROR_MODE: str = "replace"

# ---------------------------------------------------------------------------
# application.log size management (ApplicationLogTrimmer)
#
# LOG_MAX_SIZE_MB — trim application.log when it reaches this many megabytes.
#   The trimmer discards the oldest ~50 % (FIFO) so the file stays below the
#   limit after each trim cycle.  Range: any positive integer; default 10 MB.
#
# LOG_TRIM_ENABLED — master switch.  Can be overridden by manual/conf.py
#   (log_trim_enabled = False) to disable trimming entirely.
# ---------------------------------------------------------------------------

LOG_MAX_SIZE_MB: int = 10
LOG_TRIM_ENABLED: bool = True
