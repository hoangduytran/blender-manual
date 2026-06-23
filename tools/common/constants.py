"""Shared string constants for the blender-manual build and search tools.

Import from here instead of repeating literals so a single change propagates
everywhere.  All values must match the corresponding settings in
``manual/conf.py`` (which ConfigRecord reads at runtime).
"""

import re
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
REPEATABLE_SCHEMA_VERSION: int = 2                # pickle envelope schema (2: +is_glossary)
REPEATABLE_NODE_COMMENT_PREFIX: str = "repeatable-node: "  # PO auto comment
PO_WIDTH_UNWRAPPED: int = 4096                     # dump_po width: no wrapping
PO_LOCATION_UP_PREFIX: str = "../../"             # locale/<lang>/LC_MESSAGES → repo root

# Plain-text report of misaligned reading-hints (see HINT_NEAR_MISS_RATIO).
REPEATABLE_MISMATCH_FILENAME: str = "repeatable_mismatch.txt"

# Names of the conf.py config values that override the filename defaults above.
CONF_REPEATABLE_PICKLE_FILENAME: str = "repeatable_pickle_filename"
CONF_REPEATABLE_PO_FILENAME: str = "repeatable_po_filename"
CONF_REPEATABLE_MISMATCH_FILENAME: str = "repeatable_mismatch_filename"

# A terminal bracket whose text is not an exact match for the source msgid is
# still pilled "as written" when its similarity to the msgid is at least this
# ratio (difflib.SequenceMatcher on whitespace-normalised, case-folded text).
# Such near-misses are almost always a typo'd reading-hint (e.g. a dropped
# article: "Install from Package Manager" vs "Install from a Package Manager",
# ratio ~0.96); they are pilled but reported so the translator can fix the
# source.  Genuinely different bracketed text (e.g. "Bar" vs "Baz", ratio ~0.67)
# stays below the bar and is left untouched.
HINT_NEAR_MISS_RATIO: float = 0.8

# CSS classes for the reading-hint pill.  The bracketed text is always the
# muted "secondary reading"; which language sits in the bracket decides the
# class (content-driven, see HintSide).  Both names are language-neutral: "en"
# is always English (the source), and the other is the target translation
# whatever it is (vi, ru, ...), so the class is "native", never "vi":
#   * body content keeps the translation first and the English in brackets
#     -> the bracket is English -> PILL_EN_CSS_CLASS.
#   * glossary terms keep the English first and the translation in brackets
#     -> the bracket is the native translation -> PILL_NATIVE_CSS_CLASS.
PILL_EN_CSS_CLASS: str = "i18n-en-hint"
PILL_NATIVE_CSS_CLASS: str = "i18n-native-hint"

# Backwards-compatible alias (the original single-class name).
PILL_CSS_CLASS: str = PILL_EN_CSS_CLASS

# English reading-hint syntax: a terminal ``<lead> <open><reading><close>``
# suffix.  Different language teams use different delimiters -- vi uses square
# brackets ("Màn Chắn Lọc [Mask]"), ru uses parentheses ("Аддоны (add-ons)") --
# so both are recognised.  False positives are prevented not by the delimiter
# but by requiring the bracketed text to equal the source msgid.
HINT_OPEN_BRACKET: str = "["
HINT_CLOSE_BRACKET: str = "]"
HINT_OPEN_PAREN: str = "("
HINT_CLOSE_PAREN: str = ")"

# Ordered (open, close) delimiter pairs tried when locating a terminal hint.
HINT_BRACKET_PAIRS: tuple[tuple[str, str], ...] = (
    (HINT_OPEN_BRACKET, HINT_CLOSE_BRACKET),
    (HINT_OPEN_PAREN, HINT_CLOSE_PAREN),
)

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


class HintSide(str, Enum):
    """Which side of a ``<lead> [<bracket>]`` reading-hint is the source msgid.

    The bracket is always the pilled, muted secondary reading; this records
    which language it holds so the renderer can pick the right pill class.

    Members:
        ENGLISH_BRACKET: the bracket equals the msgid (English-in-brackets,
            i.e. body content) -> the bracket is English.
        ENGLISH_LEAD: the lead equals the msgid (English-first, i.e. glossary
            terms) -> the bracket is the translation.
    """
    ENGLISH_BRACKET = "english_bracket"
    ENGLISH_LEAD = "english_lead"


# ---------------------------------------------------------------------------
# Repeatable navigation HTML rewriting (build_files/extensions/repeatable_html.py)
#
# Furo builds its navigation tree (sidebar toctrees, homepage cards) as already
# rendered HTML, after the doctree pill mutation has run.  To pill the terminal
# English reading-hint inside that generated markup the extension does a
# text-token rewrite over the raw HTML string, which needs three regexes.  They
# are centralised here — together with the structural CSS class names they
# target and their flags — so the patterns have a single source of truth and
# can be reused by tools and tests.
#
# NOTE: these are shallow, non-nesting matchers tuned for the flat fragments
# Furo emits; they are deliberately *not* a general-purpose HTML parser.
# ---------------------------------------------------------------------------

# Furo/Sphinx structural CSS class names whose ``<div>`` containers hold the
# navigation text eligible for rewriting.  Each is matched with word boundaries
# (``\b…\b``) so an alphanumeric/underscore-adjacent class such as "cards" or
# "scorecard" is not matched.  A hyphen counts as a boundary, so "card-header"
# *would* match — acceptable for these Furo containers.
NAV_TOCTREE_WRAPPER_CSS_CLASS: str = "toctree-wrapper"
NAV_TOC_CARD_CSS_CLASS: str = "card"

# Group names shared between the patterns below and their consumers
# (build_files/extensions/repeatable_html.py), so call sites reference groups by
# name instead of brittle positional indices.
HTML_TAG_GROUP: str = "tag"           # HTML_TAG_RE: one whole HTML tag
NAV_OPEN_GROUP: str = "open"          # NAV_*_RE: the opening <div …> tag
NAV_BODY_GROUP: str = "body"          # NAV_*_RE: the rewritable inner HTML
NAV_CLOSE_GROUP: str = "close"        # NAV_*_RE: the matching </div> tag

# Splits an HTML fragment into alternating text/tag tokens.  The single
# (named) capturing group keeps the tags in ``re.split()`` output — odd indices
# are tags, even indices are text.  The tag body tolerates a quoted ``>`` inside
# attribute values (``"…"`` or ``'…'``) so an attribute value never terminates a
# tag early.  Written verbose so each alternative is self-documenting.
HTML_TAG_RE: re.Pattern[str] = re.compile(
    rf"""
    (?P<{HTML_TAG_GROUP}>        # one whole HTML tag (kept by re.split)
        <                        #   opening angle bracket
        (?:                      #   tag body — any run of:
            [^>"']               #     a char that is not >, " or '
            | "[^"]*"            #     or a "double-quoted" attribute value
            | '[^']*'            #     or a 'single-quoted' attribute value
        )*
        >                        #   closing angle bracket
    )
    """,
    re.VERBOSE,
)


# Template for a ``<div class="… CLASS …">BODY</div>`` container matcher.  The
# three named groups (open / body / close) let the body be rewritten in place
# while the surrounding ``<div>`` is preserved verbatim.  ``re.DOTALL`` lets the
# body span newlines; the lazy ``.*?`` stops at the first ``</div>``.  Kept
# private; use the compiled NAV_*_RE patterns below.
def _nav_container_re(css_class: str) -> re.Pattern[str]:
    """Compile a navigation-container matcher for one structural CSS class."""
    return re.compile(
        rf"""
        (?P<{NAV_OPEN_GROUP}>                    # opening <div …> with the class
            <div\s+class="
            [^"]*\b{re.escape(css_class)}\b[^"]*
            ">
        )
        (?P<{NAV_BODY_GROUP}>.*?)                 # inner HTML (lazy, may span lines)
        (?P<{NAV_CLOSE_GROUP}></div>)            # matching closing tag
        """,
        re.DOTALL | re.VERBOSE,
    )


# In-page rendered toctrees emitted as ``<div class="toctree-wrapper …">``.
NAV_TOCTREE_WRAPPER_RE: re.Pattern[str] = _nav_container_re(NAV_TOCTREE_WRAPPER_CSS_CLASS)
# Homepage navigation cards emitted as ``<div class="card …">``.
NAV_TOC_CARD_RE: re.Pattern[str] = _nav_container_re(NAV_TOC_CARD_CSS_CLASS)
