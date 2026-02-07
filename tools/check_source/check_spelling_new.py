#!/usr/bin/env python3
# Apache License, Version 2.0

"""
Check spelling for all RST files in the repository. This builds on the legacy version
with a series of improvments including the following:

- Uses multiprocessing to utilize all CPU cores.
- Batches files to reduce process overhead.
- Aggressively caches enchant lookups per process (for max performance from multiprocessing).
- Properly checks bulleted lists which were ignored by the legacy script

- TODO: more comprehensive docs.
- TODO: ensure no other elements are accidentally getting skipped in RstSpellingVisitor.
"""

import concurrent.futures
from concurrent.futures import ProcessPoolExecutor

import docutils.parsers.rst
from docutils.parsers.rst import directives, roles
import docutils

from check_spelling_config import (
    dict_custom,
    dict_ignore,
)
import os
import re


# for spelling
import enchant

# -----------------------------------------------------------------------------
# Utilities

def find_vcs_root(test, dirs=(".svn", ".git", ".hg"), default=None):
    prev, test = None, os.path.abspath(test)
    while prev != test:
        if any(os.path.isdir(os.path.join(test, d)) for d in dirs):
            return test
        prev, test = test, os.path.abspath(os.path.join(test, os.pardir))
    return default


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
RST_DIR = find_vcs_root(CURRENT_DIR)


def rst_files(path):
    for dirpath, dirnames, filenames in os.walk(path):
        # Filter out directories that start with "."
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        # Skip processing files if the current directory starts with "."
        if any(part.startswith(".") for part in dirpath.split(os.sep)):
            continue
        for filename in filenames:
            if filename.startswith("."):
                continue
            ext = os.path.splitext(filename)[1]
            if ext.lower() == ".rst":
                yield os.path.join(dirpath, filename)


def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]

# -----------------------------------------------------------------------------
# Regex + word extraction

RE_TEXT_REPLACE_ROLES_INCLUDE = ("menuselection", "guilabel", "file", "ref")
RE_TEXT_REPLACE_ROLES_EXCLUDE = ("kbd", "doc", "abbr", "term")

def regex_key_raise(x):
    raise Exception("Unknown role! " + "".join(x.groups()))

RE_TEXT_REPLACE_TABLE = (
    # Match HTML link: `Text <url>`__
    (
        re.compile(r"(`)([^`<]+)(<[^`>]+>)(`)(__)", re.MULTILINE),
        lambda x: x.groups()[1].strip(),
    ),
    # Roles with plain-text: :some_role:`Text <ref>`
    (
        re.compile(r"(:[A-Za-z_]+:)(`)([^`<]+)(<[^`>]+>)(`)", flags=re.MULTILINE),
        lambda x: x.groups()[2].strip(),
    ),
    # Roles to always include.
    (
        re.compile(r"(:(" + ("|".join(RE_TEXT_REPLACE_ROLES_INCLUDE)) + r"):)(`)([^`]+)(`)", flags=re.MULTILINE),
        lambda x: x.groups()[3].strip(),
    ),
    # Roles to always exclude.
    (
        re.compile(r"(:(" + ("|".join(RE_TEXT_REPLACE_ROLES_EXCLUDE)) + r"):)(`)([^`]+)(`)", flags=re.MULTILINE),
        lambda _: " ",
    ),
    # Ensure all roles are handled.
    (
        re.compile(r"(:[A-Za-z_]+:)(`)([^`]+)(`)", flags=re.MULTILINE),
        regex_key_raise,
    ),
    # Match substitution for removal: `|identifier|`
    (
        re.compile(r"\|[a-zA-Z0-9_]+\|"),
        lambda _: " ",
    ),
)

RE_WORDS = re.compile(
    r"\b("
    r"[A-Z]+[\-'A-Z]*[A-Z]|"
    r"[A-Za-z][\-'a-z]*[a-z]+"
    r")\b"
)

# -----------------------------------------------------------------------------
# Docutils helpers

def filedata_glossary_wash(filedata):
    """
    Only list body of text.
    """
    lines_src = filedata.splitlines()
    lines_dst = []
    in_glossary = False
    for l in lines_src:
        l_strip = l.lstrip()
        if l_strip.startswith(".. glossary::"):
            in_glossary = True
            continue
        elif in_glossary is False:
            lines_dst.append(l)
            continue
        else:
            indent = len(l) - len(l_strip)
            if indent <= 3 and l_strip:
                continue
            elif indent >= 6 or not l_strip:
                lines_dst.append(l[6:])
    return "\n".join(lines_dst)


def rst_to_doctree(filedata, filename):
    parser = docutils.parsers.rst.Parser()
    doc = docutils.utils.new_document(filename)
    doc.settings.tab_width = 3
    doc.settings.pep_references = False
    doc.settings.rfc_references = False
    doc.settings.syntax_highlight = False

    doc.settings.raw_enabled = True
    doc.settings.file_insertion_enabled = True
    doc.settings.character_level_inline_markup = False  # TODO, whats sphinx do?
    doc.settings.trim_footnote_reference_space = False  # doesn't seem important

    parser.parse(filedata, doc)
    return doc

# -----------------------------------------------------------------------------
# Context flags

RST_CONTEXT_FLAG_LITERAL = 1 << 0
RST_CONTEXT_FLAG_LITERAL_BLOCK = 1 << 1
RST_CONTEXT_FLAG_MATH = 1 << 2
RST_CONTEXT_FLAG_COMMENT = 1 << 3

# -----------------------------------------------------------------------------
# Worker logic (runs in subprocesses)

USE_ONCE = True

class RstSpellingVisitor(docutils.nodes.NodeVisitor):
    __slots__ = (
        "document",
        "skip_context",
        "check_text_fn",
    )

    def __init__(self, doc, check_text_fn):
        self.document = doc
        self.skip_context = 0
        self.check_text_fn = check_text_fn

    def visit_Text(self, node):
        if self.skip_context:
            return
        text = node.astext()
        self.check_text_fn(text)

    def depart_Text(self, node):
        pass

    def visit_math(self, node):
        self.skip_context |= RST_CONTEXT_FLAG_MATH
        raise docutils.nodes.SkipNode

    def depart_math(self, node):
        self.skip_context &= ~RST_CONTEXT_FLAG_MATH

    def visit_literal(self, node):
        self.skip_context |= RST_CONTEXT_FLAG_LITERAL
        raise docutils.nodes.SkipNode

    def depart_literal(self, node):
        self.skip_context &= ~RST_CONTEXT_FLAG_LITERAL

    def visit_literal_block(self, node):
        self.skip_context |= RST_CONTEXT_FLAG_LITERAL_BLOCK
        raise docutils.nodes.SkipNode

    def depart_literal_block(self, node):
        self.skip_context &= ~RST_CONTEXT_FLAG_LITERAL_BLOCK

    def visit_code_block(self, node):
        raise docutils.nodes.SkipNode

    def depart_code_block(self, node):
        pass

    def visit_comment(self, node):
        self.skip_context |= RST_CONTEXT_FLAG_COMMENT
        raise docutils.nodes.SkipNode

    def depart_comment(self, node):
        self.skip_context &= ~RST_CONTEXT_FLAG_COMMENT

    # This is needed to spell-check the text of items in bulleted lists
    def visit_list_item(self, node):
        #print("LIST ITEM: ", node[0])
        text = node.astext()
        self.check_text_fn(text)

    def depart_list_item(self, node):
        pass

    def visit_raw(self, node):
        #print("RAW: ", node[0])
        raise docutils.nodes.SkipNode

    def depart_raw(self, node):
        pass

    def unknown_visit(self, node):
        #print("UNKNOWN: ", node[0])
        pass

    def unknown_departure(self, node):
        pass


def check_file(filename):
    # Per-file / per-process state
    local_once_words = set()
    local_bad_words = set()
    local_word_cache = {}

    dict_spelling = enchant.Dict("en_US")

    def check_word_cached(w):
        if not w:
            return True

        w_lower = w.lower()

        if w_lower in dict_custom or w_lower in dict_ignore:
            return True

        if w_lower in local_word_cache:
            return local_word_cache[w_lower]

        ok = dict_spelling.check(w)
        local_word_cache[w_lower] = ok
        return ok

    def check_spelling_body(text):
        # Wash text or inline RST.
        for re_expr, re_replace_fn in RE_TEXT_REPLACE_TABLE:
            text = re.sub(re_expr, re_replace_fn, text)

        for re_match in RE_WORDS.finditer(text):
            w = re_match.group(0)

            if w.isupper():
                continue

            w_lower = w.lower()

            if USE_ONCE and w_lower in local_once_words:
                continue

            if check_word_cached(w):
                pass
            elif "-" in w:
                if check_word_cached(w):
                    pass
                elif all(check_word_cached(w_split) for w_split in w.split("-")):
                    pass
                else:
                    local_bad_words.add(w)
                    if USE_ONCE:
                        local_once_words.add(w_lower)
            else:
                local_bad_words.add(w)
                if USE_ONCE:
                    local_once_words.add(w_lower)

    # --- Read & parse file ---
    with open(filename, 'r', encoding='utf-8') as f:
        filedata = f.read()

        if filename.endswith(os.path.join("glossary", "index.rst")):
            filedata = filedata_glossary_wash(filedata)

        doc = rst_to_doctree(filedata, filename)

    visitor = RstSpellingVisitor(doc, check_spelling_body)
    doc.walkabout(visitor)

    return local_bad_words


def check_files_chunk(filenames):
    chunk_bad = set()
    for fn in filenames:
        chunk_bad |= check_file(fn)
    return chunk_bad

# -----------------------------------------------------------------------------
# Main

def main():
    files = list(rst_files(RST_DIR))

    all_bad_words = set()

    cpu_count = os.cpu_count() or 4
    # Batch size: enough work per process to amortize spawn/IPC overhead
    chunk_size = max(10, len(files) // (cpu_count * 4))
    chunks = list(chunked(files, chunk_size))

    # Print debugging info about CPU count and chunk count for parallelism
    #print(f"CPUs: {cpu_count}, files: {len(files)}, chunks: {len(chunks)}, chunk_size: {chunk_size}")

    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        futures = [executor.submit(check_files_chunk, ch) for ch in chunks]

        for future in concurrent.futures.as_completed(futures):
            try:
                all_bad_words |= future.result()
            except Exception as e:
                print(f"Error processing chunk: {e}")

    for w in sorted(all_bad_words, key=lambda s: s.lower()):
        print(w)

# -----------------------------------------------------------------------------
# Register dummy directives and roles

def directive_ignore(
        name, arguments, options, content, lineno,
        content_offset, block_text, state, state_machine,
):
    text = '\n'.join(content)
    return [docutils.nodes.doctest_block(text, text, codeblock=True)]

directive_ignore.content = True


def directive_ignore_recursive(
        name, arguments, options, content, lineno,
        content_offset, block_text, state, state_machine,
):
    return []

directive_ignore_recursive.content = True


# ones we want to check
directives.register_directive('index', directive_ignore)
directives.register_directive('reference', directive_ignore)
directives.register_directive('seealso', directive_ignore)
directives.register_directive('only', directive_ignore)
directives.register_directive('hlist', directive_ignore)
directives.register_directive('versionchanged', directive_ignore)
directives.register_directive('peertube', directive_ignore)
directives.register_directive('todo', directive_ignore)

# Recursive ignore
directives.register_directive('toctree', directive_ignore_recursive)
directives.register_directive('code-block', directive_ignore_recursive)
directives.register_directive('highlight', directive_ignore_recursive)
directives.register_directive('parsed-literal', directive_ignore_recursive)
directives.register_directive('autoclass', directive_ignore_recursive)
directives.register_directive('automodule', directive_ignore_recursive)
directives.register_directive('autosummary', directive_ignore_recursive)
directives.register_directive('currentmodule', directive_ignore_recursive)
directives.register_directive('function', directive_ignore_recursive)
directives.register_directive('youtube', directive_ignore_recursive)
directives.register_directive('peertube', directive_ignore_recursive)
directives.register_directive('vimeo', directive_ignore_recursive)
directives.register_directive('todolist', directive_ignore_recursive)
directives.register_directive('include', directive_ignore_recursive)


class RoleIgnore(docutils.nodes.Inline, docutils.nodes.TextElement):
    pass


def role_ignore(name, rawtext, text, lineno, inliner, options={}, content=[]):
    nodes, msgs = inliner.parse(text, lineno, memo=inliner, parent=inliner.parent)
    return [RoleIgnore(text, '', *nodes, **options)], []


class RoleIgnoreRecursive(docutils.nodes.Inline, docutils.nodes.TextElement):
    pass


def role_ignore_recursive(name, rawtext, text, lineno, inliner, options={}, content=[]):
    return [RoleIgnoreRecursive("", '', *(), **{})], []


roles.register_canonical_role('menuselection', role_ignore)
roles.register_canonical_role('guilabel', role_ignore)
roles.register_canonical_role('file', role_ignore)

roles.register_canonical_role('abbr', role_ignore_recursive)
roles.register_canonical_role('class', role_ignore_recursive)
roles.register_canonical_role('doc', role_ignore_recursive)
roles.register_canonical_role('kbd', role_ignore_recursive)
roles.register_canonical_role('mod', role_ignore_recursive)
roles.register_canonical_role('ref', role_ignore_recursive)
roles.register_canonical_role('term', role_ignore_recursive)
roles.register_canonical_role('meth', role_ignore_recursive)
roles.register_canonical_role('bl-icon', role_ignore_recursive)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
