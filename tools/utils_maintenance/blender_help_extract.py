#!/usr/bin/env python3
# Apache License, Version 2.0

"""
This script extracts RST fro Blender's "--help",
using simple conventions & REGEX parsing.

Example:
   python tools/utils_maintenance/blender_help_extract.py /path/to/blender
"""

# Conversion from There are some cases which aren't handled (and aren't needed at the moment),
# noting for completeness.
#
# - Multi-line code-blocks as each block is currently only a single line.
# - Skip parsing text inside comment blocks (literal quoting single brackets for e.g.).

import os
import re
import subprocess
import sys

BASE_DIR = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", ".."))
HELP_RST = os.path.join(BASE_DIR, "manual", "advanced", "command_line", "arguments.rst")


def help_text_make_version_and_usage_substitution(text: str) -> str:
    text = re.sub(
        re.compile(r"^(Blender) +\d.*\n(Usage:) +(.*)$", flags=re.MULTILINE),
        lambda x: (
            "| {:s} |BLENDER_VERSION_LABEL|\n"
            "| {:s} ``{:s}``"
        ).format(x.group(1), x.group(2), x.group(3)),
        text,
    )
    return text


def help_text_make_args_literal(text: str) -> str:

    re_content_table = (
        (
            # The space at the start is important so `sub-string`
            # doesn't detect the `-string` as an argument.
            re.compile(r"(^|\s+)(\-+[A-Za-z\-]+)"),
            lambda x: "{:s}``{:s}``".format(x.group(1), x.group(2)),
        ),
    )

    re_argument_line = re.compile(r"^(\s*)(\-+[A-Za-z\-]+.*)$", flags=re.MULTILINE)

    # Special case:
    # --log "abc": Logging.
    # Becomes:
    # ``--log "abc"`: Logging.
    re_argument_line_leading_example = re.compile(r"^(\-+[A-Za-z\-]+\s.*)(: +)", flags=re.MULTILINE)

    def re_argument_line_fn(x: re.Match[str]) -> str:
        indent = x.group(1)
        content = x.group(2)

        content_prefix = ""
        match_arg_example = re_argument_line_leading_example.match(content)
        if match_arg_example is not None:
            content_prefix = "``{:s}``{:s}".format(match_arg_example.group(1), match_arg_example.group(2))
            content = content[len(content_prefix):]

        for re_expr, re_fn in re_content_table:
            content = re.sub(re_expr, re_fn, content)

        # Weak but works to replace or's with commas.
        content = content.replace("`` or ``-", "``, ``-", 1)
        return indent + content_prefix + content

    text = re.sub(re_argument_line, re_argument_line_fn, text)
    return text


def help_text_make_single_quotes_literal(text: str) -> str:
    re_table = (
        (
            re.compile(
                # Be fairly relaxed about what is accepted before a `'`
                # Space or open brackets is sufficient at the moment,
                # other characters can be added if needed.
                r"([\s\(\[\{]+)"
                r"'([^\']+)'"
            ),
            lambda x: x.group(1) + "``" + x.group(2) + "``",
        ),
        (
            re.compile(r"([-+]?<[A-Za-z_0-9\(\)]+>)"),
            lambda x: "``" + x.group(1) + "``",
        ),
    )

    for re_expr, re_fn in re_table:
        text = re.sub(re_expr, re_fn, text)

    return text


def help_text_make_title_and_dedent(text: str) -> str:
    re_title = re.compile(r"\n\n([A-Z][^:]+):$", flags=re.MULTILINE)
    title_char = "="

    def re_title_fn(x: re.Match[str]) -> str:
        heading = x.group(1)
        return (
            "\n"
            "\n"
            ".. _command-line-args-{:s}:\n"
            "\n"
            "{:s}\n"
            "{:s}\n"
        ).format(
            "".join([(c if c.isalpha() else "-") for c in heading.lower()]),
            heading,
            (title_char * len(heading)),
        )

    text = re.sub(re_title, re_title_fn, text)

    # Un-indent entirely indented blocks (directly after the title).
    lines = text.splitlines(keepends=False)
    i = 0
    while i < len(lines):
        if not (lines[i].startswith(title_char) and lines[i].strip(title_char) == ""):
            # Not a title, continue.
            i += 1
            continue

        # We have a title, check the next non-blank line.
        i_next = i + 1
        while lines[i_next] == "":
            i_next += 1
        if not lines[i_next].startswith(" "):
            # No indentation, continue.
            i = i_next
            continue

        # Measure indent and de-dent until indentation not met.
        indent_len = len(lines[i_next]) - len(lines[i_next].lstrip())
        indent = " " * indent_len
        while i_next < len(lines):
            if lines[i_next].startswith(indent):
                lines[i_next] = lines[i_next][indent_len:]
            elif lines[i_next] == "":
                pass
            else:
                break
            i_next += 1

        i = i_next

    text = "\n".join(lines)

    return text


def help_text_make_environment_variables(text: str) -> str:
    env_vars = []

    # Single lines.
    re_env = re.compile(r"^(\s*)\$([A-Z][A-Z0-9_]*)(\s+)", flags=re.MULTILINE)

    def re_env_fn(x: re.Match[str]) -> str:
        env_var = x.group(2)
        env_vars.append(env_var)
        return x.group(1) + ":" + env_var + ":" + x.group(3)

    text = re.sub(re_env, re_env_fn, text)

    def re_env_var_quote_fn(x: re.Match[str]) -> str:
        beg, end = x.span(1)
        # Ignore environment variables that were just converted into field definitions.
        if x.string[beg - 1] == ":" and x.string[end] == ":":
            # Do nothing.
            return x.group(1)

        return "``" + x.group(1) + "``"

    # Now literal quote all environment variables.
    re_env_var_quote = re.compile(r"\b({:s})\b".format("|".join(env_vars)))
    text = re.sub(re_env_var_quote, re_env_var_quote_fn, text)
    return text


def help_text_make_code_blocks(text: str) -> str:
    re_code_block = re.compile(r"^(\s*)(# .*)$", flags=re.MULTILINE)

    def re_code_block_fn(x: re.Match[str]) -> str:
        indent = x.group(1)
        content = x.group(2)
        return (
            "\n"
            "{:s}.. code-block:: sh\n"
            "\n"
            "{:s}   {:s}\n"
        ).format(indent, indent, content[1:].lstrip())

    text = re.sub(re_code_block, re_code_block_fn, text)

    return text


def help_text_as_rst(text: str) -> str:
    text_header = (
        ".. DO NOT EDIT THIS FILE, GENERATED BY '{:s}'\n"
        "\n"
        "   CHANGES TO THIS FILE MUST BE MADE IN BLENDER'S SOURCE CODE, SEE:\n"
        "   https://projects.blender.org/blender/blender/src/branch/main/source/creator/creator_args.cc\n"
        "\n"
        ".. _command_line-args:\n"
        "\n"
        "**********************\n"
        "Command Line Arguments\n"
        "**********************\n"
        "\n"
    ).format(os.path.basename(__file__))

    # Expand tabs & strip trailing space.
    text = text.expandtabs(3)
    text = "\n".join([line.rstrip() for line in text.splitlines()]) + "\n"

    text = help_text_make_version_and_usage_substitution(text)
    text = help_text_make_args_literal(text)
    text = help_text_make_single_quotes_literal(text)
    text = help_text_make_title_and_dedent(text)
    text = help_text_make_environment_variables(text)
    text = help_text_make_code_blocks(text)

    # Hack: `/?` is a special case.
    text = text.replace("\n/?\n", "\n``/?``\n", 1)

    # Apply the header last (no need for it to be parsed).
    return text_header + text


def main() -> int:
    import sys
    blender_bin = sys.argv[-1]
    output_file = HELP_RST
    if not os.path.exists(output_file):
        # If the RST doesn't exist, chances are it was moved, don't blindly write to the (old?) location.
        # The user can touch the path if this is really needed.
        print(
            "File not found: {:s}\n"
            "If this is intentional touch the destination before running!".format(output_file)
        )
        return 1

    env = os.environ.copy()
    env["ASAN_OPTIONS"] = (
        env.get("ASAN_OPTIONS", "") +
        ":exitcode=0:check_initialization_order=0:strict_init_order=0:detect_leaks=0"
    )

    text_beg = "BEGIN_BLOCK"
    text_end = "END_BLOCK"
    text = subprocess.check_output(
        [
            blender_bin,
            "--factory-startup",
            "--background",
            "--python-exit-code", "1",
            "--python-expr",
            # Code begin/end text because of Blender's chatty reporting of version and that it quit.
            (
                "print("
                "'{:s}\\n' + "
                "__import__('bpy').app.help_text(all=True) + "
                "'\\n{:s}'"
                ")"
            ).format(text_beg, text_end),
        ],
        env=env,
    ).decode("utf-8")

    # Extract between begin/end markers.
    text = text[text.find(text_beg) + len(text_beg) + 1: text.find(text_end)]

    text_rst = help_text_as_rst(text)

    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(text_rst)
    print("Updated:", os.path.relpath(output_file, BASE_DIR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
