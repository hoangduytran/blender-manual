"""Build-time HTML rendering for repeatable navigation reading hints."""

from __future__ import annotations

import html
import re
from collections.abc import Iterable

from repeatable_extract import classify_terminal_hint, normalized
from repeatable_record import RepeatableRecord

from common.constants import (  # type: ignore[import-not-found]
    HINT_BRACKET_PAIRS,
    HintSide,
    HTML_TAG_RE,
    NAV_BODY_GROUP,
    NAV_CLOSE_GROUP,
    NAV_OPEN_GROUP,
    NAV_TOC_CARD_RE,
    NAV_TOCTREE_WRAPPER_RE,
    PILL_EN_CSS_CLASS,
    RepeatableTag,
)

_NAVIGATION_TAGS = frozenset({RepeatableTag.TITLE.value, RepeatableTag.TOCTREE.value})


def _hint_prefix_keys(lead: str, bracket: str) -> tuple[str, ...]:
    """Return normalized text prefixes for every supported hint delimiter."""
    return tuple(
        normalized(f"{lead}{open_char}{bracket}{close_char}")
        for open_char, close_char in HINT_BRACKET_PAIRS
    )


def build_navigation_hint_index(
    records: Iterable[RepeatableRecord],
) -> dict[str, tuple[str, ...]]:
    """Index validated repeatable translated navigation text by normalized msgstr."""
    indexed: dict[str, set[str]] = {}
    for record in records:
        hint = classify_terminal_hint(record.msgstr, record.msgid)
        is_english_hint = hint is not None and hint.side == HintSide.ENGLISH_BRACKET
        if record.node_tagname in _NAVIGATION_TAGS and is_english_hint:
            source = hint.source or record.msgid
            indexed.setdefault(normalized(record.msgstr), set()).add(source)
            for key in _hint_prefix_keys(hint.lead, hint.bracket):
                indexed.setdefault(key, set()).add(source)
    return {key: tuple(sorted(msgids)) for key, msgids in indexed.items()}


def _render_hint(text: str, msgids: tuple[str, ...]) -> str | None:
    """Render one validated text token as fixed pill HTML."""
    for msgid in msgids:
        hint = classify_terminal_hint(text, msgid)
        if hint is None or hint.side != HintSide.ENGLISH_BRACKET:
            continue
        return (
            f"{html.escape(hint.lead, quote=False)}"
            f'<span class="{PILL_EN_CSS_CLASS}" '
            f'data-msgid="{html.escape(hint.source or msgid, quote=True)}" '
            f'data-repeatable="true">'
            f"{html.escape(hint.bracket, quote=False)}</span>"
            f"{html.escape(hint.trailing, quote=False)}"
        )
    return None


def _rewrite_text_token(token: str, index: dict[str, tuple[str, ...]]) -> str:
    """Rewrite a plain HTML text token only when it matches the repeatable index."""
    decoded = html.unescape(token)
    key = normalized(decoded)
    msgids = index.get(key, ())
    if not msgids:
        msgids = tuple(
            msgid
            for prefix, prefix_msgids in index.items()
            if key.startswith(prefix)
            for msgid in prefix_msgids
        )
    rendered = _render_hint(decoded, msgids)
    return rendered if rendered is not None else token


def rewrite_navigation_fragment(
    fragment: str, index: dict[str, tuple[str, ...]]
) -> str:
    """Write validated repeatable pills into every text token of an HTML fragment."""
    if not fragment or not index:
        return fragment
    parts = HTML_TAG_RE.split(fragment)
    return "".join(
        part if position % 2 else _rewrite_text_token(part, index)
        for position, part in enumerate(parts)
    )


def _rewrite_containers(
    body: str, pattern: re.Pattern[str], index: dict[str, tuple[str, ...]]
) -> str:
    """Rewrite text tokens inside containers selected by *pattern*."""

    def rewrite_match(match: re.Match[str]) -> str:
        content = rewrite_navigation_fragment(match.group(NAV_BODY_GROUP), index)
        return match.group(NAV_OPEN_GROUP) + content + match.group(NAV_CLOSE_GROUP)

    return pattern.sub(rewrite_match, body)


def rewrite_body_navigation(body: str, index: dict[str, tuple[str, ...]]) -> str:
    """Write pills inside rendered toctrees and homepage navigation cards."""
    rewritten = _rewrite_containers(body, NAV_TOCTREE_WRAPPER_RE, index)
    return _rewrite_containers(rewritten, NAV_TOC_CARD_RE, index)
