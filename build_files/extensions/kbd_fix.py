"""Sphinx extension: fix incorrect :kbd: splitting for translated text.

Sphinx's built-in Keyboard role splits ``:kbd:`` text on spaces, ``-``, ``+``,
and ``^``.  For Vietnamese key names like ``Dấu Cộng (+) Bàn Số (NumpadPlus)``
this produces a separate ``<kbd>`` block per word or symbol because the ``+`` and
spaces are treated as compound-key separators.

This extension hooks into ``doctree-resolved`` and corrects the splitting by:

1. Scanning every element node for "kbd runs" — consecutive ``literal.kbd``
   siblings joined by thin separator Text nodes.
2. Reconstructing the original text of each run.
3. Re-splitting with a smarter algorithm that only breaks on *top-level*
   ``-``, ``+``, ``^`` characters (not inside parentheses, never on spaces).
4. Replacing the original nodes with the correctly-split ones.

The fix is only applied on translated HTML builds; English builds already
produce well-formed single-word key names so no merge is needed there.
"""

from __future__ import annotations

from docutils import nodes

from _doctree_extract import is_html_builder, is_translated_language


# ---------------------------------------------------------------------------
# Node classifiers
# ---------------------------------------------------------------------------

def _is_kbd(node: nodes.Node) -> bool:
    return isinstance(node, nodes.literal) and "kbd" in node.get("classes", [])


def _is_kbd_sep_text(node: nodes.Node) -> bool:
    """True for a Text node that could be a between-kbd separator.

    Only Text consisting entirely of ``-``, ``+``, ``^``, or space qualifies.
    Any other character means the text is surrounding prose, not part of a
    compound-key sequence.
    """
    if not isinstance(node, nodes.Text):
        return False
    text = str(node)
    return bool(text) and all(c in "-+^ " for c in text)


# ---------------------------------------------------------------------------
# Smart splitter
# ---------------------------------------------------------------------------

def _smart_split(text: str) -> list[tuple[str, bool]]:
    """Split kbd text into ``(segment, is_separator)`` pairs.

    Splits **only** on top-level ``-``, ``+``, ``^`` (depth == 0 with respect
    to ``()`` / ``[]`` bracket pairs).  Spaces are never treated as separators.

    Examples::

        'Ctrl-Alt'                          → [('Ctrl', F), ('-', T), ('Alt', F)]
        'Shift-Ctrl'                        → [('Shift', F), ('-', T), ('Ctrl', F)]
        'NumpadPlus'                        → [('NumpadPlus', F)]
        'Dấu Cộng (+) Bàn Số (NumpadPlus)' → [('Dấu Cộng (+) Bàn Số (NumpadPlus)', F)]
        'Dấu Trừ (-) Bàn Số (NumpadMinus)' → [('Dấu Trừ (-) Bàn Số (NumpadMinus)', F)]
        'Dấu Chéo (/) Bàn Số (NumpadSlash)' → [('Dấu Chéo (/) Bàn Số (NumpadSlash)', F)]
    """
    result: list[tuple[str, bool]] = []
    current: list[str] = []
    depth = 0

    for ch in text:
        if ch in "([":
            depth += 1
            current.append(ch)
        elif ch in ")]":
            depth -= 1
            current.append(ch)
        elif depth == 0 and ch in "-+^":
            if current:
                result.append(("".join(current), False))
                current = []
            result.append((ch, True))
        else:
            current.append(ch)

    if current:
        result.append(("".join(current), False))

    return result


# ---------------------------------------------------------------------------
# Per-parent fixer
# ---------------------------------------------------------------------------

def _fix_kbd_in_parent(parent: nodes.Element) -> None:
    """Find and re-merge wrongly-split kbd runs in *parent*'s children."""
    i = 0
    while i < len(parent.children):
        if not _is_kbd(parent.children[i]):
            i += 1
            continue

        # Extend the run as far as: kbd … (sep-text kbd)* …
        run_start = i
        j = i + 1
        while j < len(parent.children):
            node = parent.children[j]
            if _is_kbd(node):
                j += 1
            elif (
                _is_kbd_sep_text(node)
                and j + 1 < len(parent.children)
                and _is_kbd(parent.children[j + 1])
            ):
                j += 2
            else:
                break
        run_end = j  # exclusive

        run = parent.children[run_start:run_end]

        if len(run) <= 1:
            i += 1
            continue

        # Reconstruct the original full text.
        full_text = "".join(
            str(n) if isinstance(n, nodes.Text) else n.astext() for n in run
        )

        # Re-split with the smarter algorithm.
        parts = _smart_split(full_text)

        # Preserve the css classes from the first kbd node.
        first = run[0]
        classes = list(first.get("classes", ["kbd"]) if isinstance(first, nodes.Element) else ["kbd"])  # type: ignore[attr-defined]

        replacement: list[nodes.Node] = []
        for seg, is_sep in parts:
            if is_sep:
                replacement.append(nodes.Text(seg))
            else:
                replacement.append(nodes.literal(seg, seg, classes=classes))

        # Splice replacement in place and advance past the new nodes.
        parent.children[run_start:run_end] = replacement
        i = run_start + len(replacement)


# ---------------------------------------------------------------------------
# Doctree walker
# ---------------------------------------------------------------------------

def fix_kbd_splitting(doctree: nodes.document) -> None:
    """Walk *doctree* and fix wrongly-split kbd sequences in every element."""
    for node in doctree.findall(nodes.Element):
        _fix_kbd_in_parent(node)


# ---------------------------------------------------------------------------
# Sphinx hook
# ---------------------------------------------------------------------------

def on_doctree_resolved(app, doctree, _docname) -> None:
    """WRITE phase: fix kbd splitting for translated HTML builds only."""
    if not (is_html_builder(app) and is_translated_language(app.config.language)):
        return
    fix_kbd_splitting(doctree)


def setup(app):
    app.connect("doctree-resolved", on_doctree_resolved)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
