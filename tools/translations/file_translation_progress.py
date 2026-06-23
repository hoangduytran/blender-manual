#!/usr/bin/env python3
# Apache License, Version 2.0
# Copyright 2015 Anton Felix Lorenzen <anfelor@web.de>

'''
Module of Translation Tracker: report the number of complete strings in a file.
'''

from enum import Enum


class PoToken:
    """Literal gettext-PO syntax fragments matched by :func:`parse_line`.

    Kept local to this module (not in tools/common/constants.py) because they
    are only used here; promote them to the shared constants module if a second
    PO parser ever needs the same tokens.
    """

    MSGSTR = 'msgstr'           # start of a translation line
    EMPTY_MSGSTR = 'msgstr ""'  # an untranslated entry
    CONTINUATION = '"'          # wrapped continuation of the previous msgstr
    FLAG_COMMENT = '#,'         # flag comment line (may carry "fuzzy")
    FUZZY = 'fuzzy'             # the fuzzy flag itself


class LineKind(Enum):
    """Classification of a single PO line.

    This is an internal protocol between :func:`parse_line` (producer) and
    :func:`parse_file` (consumer); callers only ever see the integer tallies
    that :func:`parse_file` returns, never these members.
    """

    COMPLETE = 'COMPLETE'          # msgstr with text -> a real translation
    EMPTY = 'EMPTY'              # msgstr "" -> an untranslated entry
    CONTINUATION = 'CONTINUATION'  # "..." wrapped line of the previous msgstr
    FUZZY = 'FUZZY'              # #, fuzzy flag comment
    NONE = 'NONE'              # any other line (msgid, comment, blank)


def parse_file(po_filepath):
    msgstrs_complete = -1  # First lines contain a "fake" msgstr
    msgstrs_empty = 0
    msgstrs_fuzzy = 0
    last_line_was_empty_msg_str = False
    for line in open(po_filepath, encoding='utf8'):
        result = parse_line(line)
        if result == LineKind.COMPLETE or result == LineKind.EMPTY:
            msgstrs_complete += 1
            if result == LineKind.EMPTY:
                msgstrs_empty += 1
                last_line_was_empty_msg_str = True
        else:
            if result == LineKind.CONTINUATION:
                if last_line_was_empty_msg_str:
                    msgstrs_empty -= 1
            else:
                if result == LineKind.FUZZY and msgstrs_complete >= 0:
                    # ignore fuzzy on "fake" msgstr
                    msgstrs_fuzzy += 1
            last_line_was_empty_msg_str = False
    return msgstrs_complete, msgstrs_empty, msgstrs_fuzzy


def parse_line(line):
    if line.startswith(PoToken.MSGSTR):
        if line.startswith(PoToken.EMPTY_MSGSTR):
            return LineKind.EMPTY
        return LineKind.COMPLETE
    if line.startswith(PoToken.CONTINUATION):
        return LineKind.CONTINUATION
    # only search in flag comments, "fuzzy" could occur
    # in filenames ("#:"), translator e-mail ("# ") etc.
    if line.startswith(PoToken.FLAG_COMMENT) and PoToken.FUZZY in line:
        return LineKind.FUZZY
    return LineKind.NONE
