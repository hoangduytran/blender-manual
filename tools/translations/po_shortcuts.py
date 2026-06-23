#! /usr/bin/env python3

"""Bulk-rewrite keyboard shortcuts (:kbd:`...`) in translated PO files.

For one language, applies a JSON-driven find/replace table to the shortcut
keys inside ``:kbd:`` roles of every ``msgstr``, across all PO files under
``locale/<lang>/``.

Edits are **surgical**: only the changed ``msgstr`` byte ranges are rewritten
and the rest of each file is copied through verbatim, so the diff shows exactly
the shortcuts that changed (and nothing else). This is why the tool parses the
raw PO text rather than round-tripping through ``sphinx_intl.catalog.dump_po``,
which rewraps and reformats every entry.

Usage::

    python3 po_shortcuts.py <LANGUAGE>     # e.g. po_shortcuts.py es
"""

import sys
import os
import re
import json

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PO_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "..", "..", "locale"))

# The find/replace table lives next to this script, not in the caller's CWD.
TABLE_FILE = os.path.join(CURRENT_DIR, "po_shortcuts_tables.json")

ROLE = 'kbd'  # Change to any other role if needed


class PoToken:
    """Literal gettext-PO syntax fragments matched while scanning msgstr blocks.

    Kept local to this standalone script (not in tools/common/constants.py)
    because the translation CLIs in this directory do not share that package
    path; mirror them there only if a non-standalone tool needs the same set.
    """

    MSGSTR = "msgstr"     # opens a translation block (also "msgstr[N]" plurals)
    CONTINUATION = '"'    # wrapped continuation line of the previous msgstr


# Path segment separating the locale subtree from the per-file report name;
# report paths are sliced immediately after it (see main()).
LC_MESSAGES = "LC_MESSAGES"

# Logging goes through Sphinx's logging wrapper — no ad-hoc logging, no print().
import logging  # noqa: E402
from sphinx.util.logging import getLogger as _get_logger  # noqa: E402

_logger = _get_logger(__name__)


def debug_log(message: str, *args: object, **_kw: object) -> None:
    _logger.debug(message, *args)


def po_files(path: str):
    """Yield the path of every ``.po`` file under *path* (recursively).

    Hidden directories and hidden files (leading dot) are skipped.

    Args:
        path: Directory to walk.

    Yields:
        str: Absolute path to each ``.po`` file found.
    """
    for dirpath, dirnames, filenames in os.walk(path):
        # Prune hidden directories in-place so os.walk does not descend them.
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in filenames:
            is_hidden = filename.startswith(".")
            is_po = os.path.splitext(filename)[1].lower() == ".po"
            if is_po and not is_hidden:
                yield os.path.join(dirpath, filename)


def parse_po(text: str):
    """Yield each raw ``msgstr`` block in *text* with its start offset.

    A "block" is the ``msgstr`` (or ``msgstr[N]`` plural) line plus its
    continuation ``"..."`` lines, joined as they appear in the file — i.e. the
    raw PO bytes, not a decoded string. Callers regex-edit the block and splice
    it back at *start*, preserving the rest of the file verbatim.

    Args:
        text: Full text of a PO file.

    Yields:
        tuple[str, int]: ``(block_text, start_char_offset)`` for each msgstr,
        including every ``msgstr[0]``, ``msgstr[1]``, ... of a plural entry.

    Notes:
        ``msgctxt``/``msgid`` are intentionally not yielded — shortcuts only
        appear in translated ``msgstr`` text. The boundary line that ends a
        block is re-examined, so back-to-back ``msgstr[N]`` plural lines are
        each captured (the previous implementation dropped all but ``[0]``).
    """
    block: list[str] = []
    start = 0
    pos = 0
    for line in text.splitlines(keepends=True):
        is_continuation = line.startswith(PoToken.CONTINUATION)
        is_msgstr_start = line.startswith(PoToken.MSGSTR)

        if block and is_continuation:
            block.append(line)
        else:
            if block:                       # current block just ended
                yield "".join(block), start
                block = []
            if is_msgstr_start:             # this same line opens a new block
                block = [line]
                start = pos

        pos += len(line)

    if block:
        yield "".join(block), start


def read_json(lang: str):
    """Load the shortcut find/replace table for *lang* from :data:`TABLE_FILE`.

    Args:
        lang: Language code whose sub-table to extract.

    Returns:
        list[tuple[str, str]] | None: The ``(find, replace)`` pairs for *lang*,
        or ``None`` if the file is missing/invalid or has no table for *lang*.
    """
    def parse_json(obj):
        """json ``object_pairs_hook``: at top level, return *lang*'s sub-table.

        Validates that the requested language table exists and has no duplicate
        find-keys; raises ValueError otherwise. Non-top-level objects pass
        through unchanged.
        """
        retval = obj
        is_top_level = isinstance(obj[0][1], list)
        if is_top_level:
            retval = None  # language table not found so far
            for tpl in obj:
                if tpl[0] == lang:  # table found?
                    retval = tpl[1]
                    break
            if retval:  # table was found?
                test_set = set(entry[0] for entry in retval)
                has_duplicates = len(test_set) < len(retval)
                if has_duplicates:
                    raise ValueError("table contains duplicate entries")
            else:
                raise ValueError("table not found")
        return retval

    try:
        with open(TABLE_FILE, "r", encoding="utf-8") as json_file:
            table = json.load(json_file, object_pairs_hook=parse_json)
    except (IOError, OSError) as err:
        debug_log("%s: cannot read data file: %s", TABLE_FILE, err)
        return None
    except json.JSONDecodeError as err:
        debug_log("%s: cannot decode data file: %s", TABLE_FILE, err)
        return None
    except ValueError as err:
        debug_log("%s: %s", TABLE_FILE, err)
        return None

    debug_log("Loaded shortcut table for %s: %d entr(y/ies)", lang, len(table))
    return table


def _compile_table(table):
    """Compile the ``(find, replace)`` table into ``:kbd:``-scoped regex rules.

    Each rule matches *find* as a whole word inside a ``:kbd:`...`` role and
    rewrites it to *replace*, leaving the surrounding role markup intact.

    Args:
        table: ``(find, replace)`` pairs from :func:`read_json`.

    Returns:
        list[tuple[re.Pattern, str]]: Compiled pattern and replacement template.
    """
    compiled = []
    for key, value in table:
        pattern_str = r'(\:' + ROLE + r'\:["\s]*?`[^`]*?)\b' + key + r'\b([^`]*?`)'
        replace = r'\1' + value + r'\2'
        compiled.append((re.compile(pattern_str, re.MULTILINE), replace))
    return compiled


def _apply_to_file(filename: str, table_compiled) -> int:
    """Apply the compiled shortcut rules to one PO file in place.

    Rewrites only the changed ``msgstr`` ranges (everything else is copied
    verbatim) and writes the file back only when something actually changed.

    Args:
        filename: Path to the PO file.
        table_compiled: Rules from :func:`_compile_table`.

    Returns:
        int: Number of substitutions made in this file (0 means untouched).
    """
    with open(filename, "r", encoding="utf-8") as f:
        text_src = f.read()

    text_dst: list[str] = []
    last_end = 0
    n_total = 0
    for msgstr, start in parse_po(text_src):
        text_dst.append(text_src[last_end:start])  # verbatim gap before block
        last_end = start + len(msgstr)

        for pattern, repl in table_compiled:
            msgstr, n = re.subn(pattern, repl, msgstr)
            n_total += n

        text_dst.append(msgstr)

    has_changes = n_total != 0
    if has_changes:
        if last_end != len(text_src):
            text_dst.append(text_src[last_end:])  # verbatim tail after last block
        with open(filename, "w", encoding="utf-8") as f:
            f.write("".join(text_dst))

    return n_total


def main(lang: str) -> None:
    """Apply the shortcut table to every PO file of *lang*.

    Args:
        lang: Language code (e.g. ``"es"``); must have a ``locale/<lang>/``
            folder and an entry in :data:`TABLE_FILE`.
    """
    lang_dir = os.path.join(PO_DIR, lang)
    if not os.path.exists(lang_dir):
        debug_log("Language folder not found: %s", lang)
        return

    table = read_json(lang)
    if not table:
        return

    table_compiled = _compile_table(table)
    debug_log("Compiled %d shortcut pattern(s) for %s", len(table_compiled), lang)

    for filename in po_files(lang_dir):
        debug_log("Scanning %s", filename)
        n_total = _apply_to_file(filename, table_compiled)
        if n_total:
            short_name = filename[filename.find(LC_MESSAGES) + len(LC_MESSAGES):]
            debug_log("%s: %d change(s).", short_name, n_total)


if __name__ == "__main__":
    # Sphinx loggers propagate to the root logger; configure a console handler so
    # this standalone script's output is visible.
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    if len(sys.argv) != 2:
        debug_log(
            "Usage: %s <LANGUAGE>   (example: %s es)",
            os.path.basename(__file__), os.path.basename(__file__),
        )
        sys.exit(2)
    main(sys.argv[1])
