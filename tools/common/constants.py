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

# ---------------------------------------------------------------------------
# Repeatable-record extension (build_files/extensions/repeatable_builder.py)
#
# The extension extracts allowlisted translated nodes as RepeatableRecord
# values, writes a gzip-pickle inventory plus a PO catalogue, and renders the
# terminal English reading-hint as an ``.i18n-en-hint`` pill.  Output filenames
# are *configured in manual/conf.py* (``repeatable_pickle_filename`` /
# ``repeatable_po_filename``); the values below are the registration defaults
# mirrored here so tools and tests share one source of truth.
# ---------------------------------------------------------------------------

REPEATABLE_PICKLE_FILENAME: str = "repeatable.pkl.gz"
REPEATABLE_PO_FILENAME: str = "repeatable.po"
REPEATABLE_PO_DOMAIN: str = "repeatable"          # Babel Catalog domain
REPEATABLE_SCHEMA_VERSION: int = 1                # pickle envelope schema
REPEATABLE_NODE_COMMENT_PREFIX: str = "repeatable-node: "  # PO auto comment
PO_WIDTH_UNWRAPPED: int = 4096                     # dump_po width: no wrapping
PO_LOCATION_UP_PREFIX: str = "../../"             # locale/<lang>/LC_MESSAGES → repo root

# Names of the conf.py config values that override the filename defaults above.
CONF_REPEATABLE_PICKLE_FILENAME: str = "repeatable_pickle_filename"
CONF_REPEATABLE_PO_FILENAME: str = "repeatable_po_filename"

# CSS class shared by the server-side pill and the JS toctree/sidebar fallback
# (see build_files/theme/css/theme_overrides.css and theme/js/en_hint.js).
PILL_CSS_CLASS: str = "i18n-en-hint"

# English reading-hint syntax: a terminal ``<translation> [<English>]`` suffix.
HINT_OPEN_BRACKET: str = "["
HINT_CLOSE_BRACKET: str = "]"

# Sentence-likeness test: a msgid ending in a period is prose and skipped, but
# an ellipsis (an operator/menu label such as "Move...") is retained.
SENTENCE_TERMINATOR: str = "."
ELLIPSIS_TERMINATOR: str = "..."

# Sentinel line number for a node that carries no source line.
SOURCE_LINE_UNKNOWN: int = -1


class RepeatableTag(str, Enum):
    """docutils ``node.tagname`` values eligible for repeatable extraction.

    A closed set of inline/title-like nodes whose text is a short, reusable
    label (a UI string, term, or heading) rather than running prose.  Being a
    str-enum, members compare equal to their raw tagname so ``node.tagname in
    REPEATABLE_NODE_TAGNAMES`` works directly.
    """
    INLINE = "inline"
    EMPHASIS = "emphasis"
    TITLE = "title"
    TERM = "term"
    RUBRIC = "rubric"
    FIELD_NAME = "field_name"
    REFERENCE = "reference"
    STRONG = "strong"
    CAPTION = "caption"
    TOCTREE = "toctree"


# Frozen membership set derived from the enum — the single allowlist used by
# is_repeatable_tag().
REPEATABLE_NODE_TAGNAMES: frozenset[str] = frozenset(tag.value for tag in RepeatableTag)


class PickleEnvelopeKey(str, Enum):
    """Top-level keys of the repeatable gzip-pickle envelope."""
    SCHEMA_VERSION = "schema_version"
    LANGUAGE = "language"
    RECORDS_BY_DOC = "records_by_doc"
