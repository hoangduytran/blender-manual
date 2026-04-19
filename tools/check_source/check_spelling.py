#!/usr/bin/env python3
# Apache License, Version 2.0

"""
Check spelling for all RST files in the repository.

- TODO: more comprehensive docs.
"""

import argparse
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import docutils
import docutils.parsers.rst
import enchant
from docutils.parsers.rst import directives, roles

from check_spelling_config import (
    dict_custom,
    dict_ignore,
)

dict_spelling = enchant.Dict("en_US")

# Validated-word cache, keyed by raw (case-sensitive) word.
word_cache = {}


def find_vcs_root(test, dirs=(".svn", ".git", ".hg"), default=None):
    prev, test = None, os.path.abspath(test)
    while prev != test:
        if any(os.path.isdir(os.path.join(test, d)) for d in dirs):
            return test
        prev, test = test, os.path.abspath(os.path.join(test, os.pardir))
    return default


def check_word(w):
    if not w:
        return True
    if w in word_cache:
        return word_cache[w]
    w_lower = w.lower()
    if w_lower in dict_custom or w_lower in dict_ignore:
        word_cache[w] = True
        return True
    result = dict_spelling.check(w)
    word_cache[w] = result
    return result


def word_is_misspelled(w):
    # Skip acronyms (XYZ, UDIM, API...).
    if w.isupper():
        return False
    if check_word(w):
        return False
    # Hyphenated word: accept if all individual parts are valid.
    if "-" in w and all(check_word(p) for p in w.split("-")):
        return False
    return True


def regex_key_raise(m):
    raise Exception("Unknown role! " + m.group(0))


# Length-preserving wash. Each replacer returns a string of the same length
# as the original match, padding removed markup with spaces. This keeps
# offsets in washed text aligned with the raw text so positions reported
# from washed matches are valid against the original.

def _pad_keep(m, keep_idx):
    """Keep `m.group(keep_idx)` in place; pad everything else with spaces."""
    lead = m.start(keep_idx) - m.start()
    trail = m.end() - m.end(keep_idx)
    return " " * lead + m.group(keep_idx) + " " * trail


def _pad_all(m):
    return " " * len(m.group(0))


# This is used to clean up text from `docutils.nodes.NodeVisitor.visit_Text`
# which doesn't always remove inline markup. Order matters: some patterns
# overlap and only the first match is rewritten.

# RE_TEXT_REPLACE_ROLES_INCLUDE = roles whose inner text should be spellchecked
# RE_TEXT_REPLACE_ROLES_EXCLUDE = roles whose inner text should be ignored

RE_TEXT_REPLACE_ROLES_INCLUDE = ("menuselection", "guilabel", "file")
RE_TEXT_REPLACE_ROLES_EXCLUDE = (
    "abbr", "class", "doc", "kbd", "math", "mod", "ref", "term",
    # Python API reference.
    "attr", "cmdoption", "data", "envvar", "exc", "func", "meth", "obj",
    # Custom roles.
    "bl-icon",
)

RE_TEXT_REPLACE_TABLE = (
    # HTML link: `Text <url>`__ (URL may span multiple lines). Keep `Text`.
    (
        re.compile(r"(`)([^`<]+)(<[^`>]+>)(`)(__)"),
        lambda m: _pad_keep(m, 2),
    ),
    # Role with plain-text target: `:some_role:`Text <ref>``. Keep `Text`.
    (
        re.compile(r"(:[A-Za-z_]+:)(`)([^`<]+)(<[^`>]+>)(`)"),
        lambda m: _pad_keep(m, 3),
    ),
    # Include roles: keep the inner text.
    (
        re.compile(r"(:(?:" + "|".join(RE_TEXT_REPLACE_ROLES_INCLUDE) + r"):)(`)([^`]+)(`)"),
        lambda m: _pad_keep(m, 3),
    ),
    # Exclude roles: drop the whole match.
    (
        re.compile(r"(:(?:" + "|".join(RE_TEXT_REPLACE_ROLES_EXCLUDE) + r"):)(`)([^`]+)(`)"),
        _pad_all,
    ),
    # Any remaining `:role:`...`` is unexpected - fail loudly.
    (
        re.compile(r"(:[A-Za-z_]+:)(`)([^`]+)(`)"),
        regex_key_raise,
    ),
    # Substitution: `|identifier|`.
    (
        re.compile(r"\|[a-zA-Z0-9_]+\|"),
        _pad_all,
    ),
)

RE_WORDS = re.compile(
    r"\b("
    # Capital words, with optional '-' and "'".
    r"[A-Z]+[\-'A-Z]*[A-Z]|"
    # Lowercase words, with optional '-' and "'".
    r"[A-Za-z][\-'a-z]*[a-z]+"
    r")\b"
)


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
RST_DIR = find_vcs_root(CURRENT_DIR)


def rst_files(path):
    if os.path.isfile(path):
        if path.lower().endswith(".rst"):
            yield path
        return
    for dirpath, dirnames, filenames in os.walk(path):
        # Filter out directories that start with "."
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        # Skip processing files if the current directory starts with "."
        if any(part.startswith(".") for part in dirpath.split(os.sep)):
            continue
        for filename in filenames:
            # Skip files that start with "."
            if filename.startswith("."):
                continue
            ext = os.path.splitext(filename)[1]
            if ext.lower() == ".rst":
                yield os.path.join(dirpath, filename)


def main():
    parser = argparse.ArgumentParser(description="Spell-check RST files.")
    parser.add_argument(
        "path",
        nargs="?",
        default=RST_DIR,
        help="Directory or file to scan (defaults to the repository root).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="emit_all",
        help="Emit every occurrence of each bad word (default reports only the first one seen).",
    )
    args = parser.parse_args()

    # Sort so file ordering is reproducible across runs.
    files = sorted(rst_files(args.path))

    all_results = []

    # Use ProcessPoolExecutor: `enchant.Dict` is not thread-safe, and each worker
    # process gets its own dict instance via module import. Worker state is reset
    # per-file inside `check_spelling`, so task results are independent of scheduling.
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(check_spelling, fn): fn for fn in files}
        for future in as_completed(futures):
            try:
                all_results.extend(future.result())
            except Exception as e:
                print(
                    "Error processing {:s}: {:s}".format(futures[future], str(e)),
                    file=sys.stderr,
                )

    emitted = set()
    for fn, lineno, col, word in sorted(all_results):
        if not args.emit_all:
            if word in emitted:
                continue
            emitted.add(word)
        print("{:s}:{:d}:{:d}: {:s}".format(os.path.relpath(fn), lineno, col, word))

# -----------------------------------------------------------------------------
# Register dummy directives


def directive_ignore(
        name, arguments, options, content, lineno,
        content_offset, block_text, state, state_machine,
):
    """
    Wrap the directive's content as a `doctest_block` so docutils stops
    parsing it as RST. The text still reaches `visit_Text` for spell-checking
    (contrast with `directive_ignore_recursive`, which drops content entirely).
    """
    text = '\n'.join(content)
    return [docutils.nodes.doctest_block(text, text, codeblock=True)]


directive_ignore.content = True


def directive_ignore_recursive(
        name, arguments, options, content, lineno,
        content_offset, block_text, state, state_machine,
):
    """
    Ignore everything under this directive (use with care!)
    """
    return []


directive_ignore_recursive.content = True


# ones we want to check
directives.register_directive('index', directive_ignore)
directives.register_directive('reference', directive_ignore)
directives.register_directive('seealso', directive_ignore)
directives.register_directive('only', directive_ignore)
directives.register_directive('hlist', directive_ignore)
directives.register_directive('versionchanged', directive_ignore)

# directives.register_directive('glossary', directive_ignore)  # wash this data instead
# Custom directives from extensions
directives.register_directive('todo', directive_ignore)

# Recursive ignore, take care!
directives.register_directive('toctree', directive_ignore_recursive)
directives.register_directive('code-block', directive_ignore_recursive)
directives.register_directive('highlight', directive_ignore_recursive)
directives.register_directive('parsed-literal', directive_ignore_recursive)
# Python API reference.
directives.register_directive('autoclass', directive_ignore_recursive)
directives.register_directive('automodule', directive_ignore_recursive)
directives.register_directive('autosummary', directive_ignore_recursive)
directives.register_directive('currentmodule', directive_ignore_recursive)
directives.register_directive('function', directive_ignore_recursive)
# Custom directives from extensions
directives.register_directive('youtube', directive_ignore_recursive)
directives.register_directive('peertube', directive_ignore_recursive)
directives.register_directive('vimeo', directive_ignore_recursive)
directives.register_directive('todolist', directive_ignore_recursive)

# workaround some bug? docutils won't load relative includes!
directives.register_directive('include', directive_ignore_recursive)


# Dummy roles
class RoleIgnore(docutils.nodes.Inline, docutils.nodes.TextElement):
    pass


def role_ignore(
        name, rawtext, text, lineno, inliner,
        options={}, content=[],
):
    # Recursively parse the contents of the index term, in case it
    # contains a substitution (like |alpha|).
    nodes, msgs = inliner.parse(text, lineno, memo=inliner, parent=inliner.parent)
    # 'text' instead of 'rawtext' because it doesn't contain the :role:
    return [RoleIgnore(text, '', *nodes, **options)], []


class RoleIgnoreRecursive(docutils.nodes.Inline, docutils.nodes.TextElement):
    pass


def role_ignore_recursive(
        name, rawtext, text, lineno, inliner,
        options={}, content=[],
):
    return [RoleIgnoreRecursive("", "")], []


roles.register_canonical_role('menuselection', role_ignore)
roles.register_canonical_role('guilabel', role_ignore)
roles.register_canonical_role('file', role_ignore)

roles.register_canonical_role('abbr', role_ignore_recursive)
roles.register_canonical_role('class', role_ignore_recursive)
roles.register_canonical_role('doc', role_ignore_recursive)
roles.register_canonical_role('kbd', role_ignore_recursive)
roles.register_canonical_role('math', role_ignore_recursive)
roles.register_canonical_role('mod', role_ignore_recursive)
roles.register_canonical_role('ref', role_ignore_recursive)
roles.register_canonical_role('term', role_ignore_recursive)
# Python API reference.
roles.register_canonical_role('meth', role_ignore_recursive)
roles.register_canonical_role('func', role_ignore_recursive)
roles.register_canonical_role('attr', role_ignore_recursive)
roles.register_canonical_role('data', role_ignore_recursive)
roles.register_canonical_role('exc', role_ignore_recursive)
roles.register_canonical_role('obj', role_ignore_recursive)
roles.register_canonical_role('cmdoption', role_ignore_recursive)
roles.register_canonical_role('envvar', role_ignore_recursive)
# Custom directives from extensions
roles.register_canonical_role('bl-icon', role_ignore_recursive)


# -----------------------------------------------------------------------------
# Special logic to wash filedata
#
# Special Case


def filedata_glossary_wash(filedata):
    """
    Replace the glossary directive line and its term lines with blanks so
    docutils parses only the body text. Line count and column positions are
    preserved, so reported line/col numbers align with the raw file.
    """
    lines_src = filedata.splitlines()
    lines_dst = []
    in_glossary = False
    for line in lines_src:
        line_lstrip = line.lstrip()
        if line_lstrip.startswith(".. glossary::"):
            in_glossary = True
            lines_dst.append("")
            continue
        if not in_glossary:
            lines_dst.append(line)
            continue
        indent = len(line) - len(line_lstrip)
        if indent <= 3 and line_lstrip:
            # Term line - blank it so docutils ignores it.
            lines_dst.append("")
        else:
            # Body or blank - keep verbatim so columns match the raw file.
            lines_dst.append(line)
    return "\n".join(lines_dst)


# -----------------------------------------------------------------------------


def rst_to_doctree(filedata, filename):
    # filename only used as an ID
    parser = docutils.parsers.rst.Parser()
    doc = docutils.utils.new_document(filename)
    doc.settings.tab_width = 3
    doc.settings.pep_references = False
    doc.settings.rfc_references = False
    doc.settings.syntax_highlight = False

    doc.settings.raw_enabled = True  # TODO, check how this works!
    doc.settings.file_insertion_enabled = True
    doc.settings.character_level_inline_markup = False  # TODO, whats sphinx do?
    doc.settings.trim_footnote_reference_space = False  # doesn't seem important

    parser.parse(filedata, doc)
    return doc


def check_spelling(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        filedata = f.read()

    # special content handling
    if filename.endswith(os.path.join("glossary", "index.rst")):
        filedata_parsed = filedata_glossary_wash(filedata)
    else:
        filedata_parsed = filedata

    doc = rst_to_doctree(filedata_parsed, filename)

    visitor = RstSpellingVisitor(doc, filename, filedata)
    doc.walkabout(visitor)
    return visitor.results


class RstSpellingVisitor(docutils.nodes.NodeVisitor):
    __slots__ = (
        "filename",
        "filedata",
        "line_starts",
        "buffer_cursor",
        "results",
        "current_line",
    )

    def __init__(self, doc, filename, filedata):
        super().__init__(doc)
        self.filename = filename
        self.filedata = filedata
        # Offset of each source line's first character, indexed as
        # `line_starts[line - 1]`. A trailing sentinel at EOF lets the same
        # table bound a line's end via `line_starts[line]`.
        line_starts = [0]
        idx = 0
        while (idx := filedata.find("\n", idx)) != -1:
            idx += 1
            line_starts.append(idx)
        line_starts.append(len(filedata))
        self.line_starts = line_starts
        # Buffer offset past which the next `find` should search; advances as
        # chunks are located so identical text on the same source line
        # resolves to distinct positions (docutils traverses in source order).
        self.buffer_cursor = 0
        # Accumulates `(filename, line, col, word)` entries.
        self.results = []
        # Source line of the walk cursor. Any node visited with a `.line`
        # attribute resets this (via `dispatch_visit`); `visit_Text` advances
        # it by the text's newline count.
        self.current_line = 1

    def dispatch_visit(self, node):
        line = getattr(node, "line", None)
        if line:
            self.current_line = line
        return super().dispatch_visit(node)

    # -----------------------------
    # Visitors (docutils callbacks)
    #
    # Every node type not listed below falls through to `unknown_visit` /
    # `unknown_departure` (both no-ops), so container nodes (sections,
    # paragraphs, list items, references, ...) need no explicit entries.

    def visit_Text(self, node):
        text = node.astext()
        raw_lines = text.splitlines()

        # Wash inline markup that docutils may have left behind (notably RST
        # text wrapped in `doctest_block` by `directive_ignore`). Wash is
        # length-preserving so offsets in `scan_lines` align with `raw_lines`,
        # which lets us spell-check the washed form while locating chunks via
        # the raw form. Every wash pattern requires one of `:`, `` ` ``, or
        # `|` - if the chunk has none, reuse `raw_lines` directly.
        if ":" in text or "`" in text or "|" in text:
            washed = text
            for re_expr, re_replace_fn in RE_TEXT_REPLACE_TABLE:
                washed = re_expr.sub(re_replace_fn, washed)
            scan_lines = washed.splitlines()
        else:
            scan_lines = raw_lines

        line_starts = self.line_starts
        for line_idx, raw_line in enumerate(raw_lines):
            stripped = raw_line.lstrip()
            if not stripped:
                continue
            source_line = self.current_line + line_idx
            if source_line >= len(line_starts):
                break
            line_start = line_starts[source_line - 1]
            line_stop = line_starts[source_line]
            buf_offset = self.filedata.find(
                stripped, max(line_start, self.buffer_cursor), line_stop,
            )
            if buf_offset < 0:
                continue
            self.buffer_cursor = buf_offset + len(stripped)
            # Column of `raw_line[0]` in the source file (1-based). Leading
            # blank-space in the chunk and the source line need not agree, so
            # anchor at `stripped` and back out the chunk's leading spaces.
            col_base = (buf_offset - line_start) + 1 - (len(raw_line) - len(stripped))
            for m in RE_WORDS.finditer(scan_lines[line_idx]):
                w = m.group(0)
                if word_is_misspelled(w):
                    self.results.append(
                        (self.filename, source_line, col_base + m.start(), w.lower()),
                    )

        # Advance the walk cursor past this chunk.
        self.current_line += text.count("\n")

    # `SkipNode` prevents children from being visited AND skips the depart
    # call, so no matching `depart_*` is needed here.

    def visit_math(self, node):
        raise docutils.nodes.SkipNode

    def visit_math_block(self, node):
        raise docutils.nodes.SkipNode

    def visit_literal(self, node):
        raise docutils.nodes.SkipNode

    def visit_literal_block(self, node):
        raise docutils.nodes.SkipNode

    def visit_code_block(self, node):
        raise docutils.nodes.SkipNode

    def visit_comment(self, node):
        raise docutils.nodes.SkipNode

    def visit_raw(self, node):
        raise docutils.nodes.SkipNode

    def unknown_visit(self, node):
        pass

    def unknown_departure(self, node):
        pass


if __name__ == "__main__":
    main()
