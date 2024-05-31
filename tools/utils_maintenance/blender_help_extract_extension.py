#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later

"""
This script extracts RST fro Blender's "--command extension --help",
using simple conventions & REGEX parsing.

Example:
   python tools/utils_maintenance/blender_help_extract_extension.py /path/to/blender
"""


import os
import re
import subprocess
import sys

from typing import (
    Dict,
    List,
    Sequence,
    Tuple,
)

USE_TITLE_GROUPS = True

# Group sub-commands with titles,
# reasonably involved but makes sense.
sub_command_titles: Dict[str, Tuple[str, ...]] = {
    "Package Management": (
        "list",
        "sync",
        "update",
        "install",
        "install-file",
        "remove",
    ),
    "Repository Management": (
        "repo-list",
        "repo-add",
        "repo-remove",
    ),
    "Extension Creation": (
        "build",
        "validate",
        "server-generate",
    ),
}

sub_command_titles_reverse_map: Dict[str, str] = {
    sub_command: title
    for title, sub_commands in sub_command_titles.items()
    for sub_command in sub_commands
}

sub_command_order: List[str] = [
    sub_command
    for sub_commands in sub_command_titles.values()
    for sub_command in sub_commands
]

if not USE_TITLE_GROUPS:
    sub_command_titles = {}
    sub_command_order = []
    sub_command_titles_reverse_map = {}


BASE_DIR = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", ".."))
HELP_RST = os.path.join(BASE_DIR, "manual", "advanced", "extensions", "command_line_arguments.rst")

COMMAND_NAME = "blender --command extension"


def patch_help_text_usage(help_output: str, is_sub_command: bool) -> str:
    """
    Convert usage into code-block.

    Replace:
       usage: {COMMAND_NAME}

    With:
       usage::

              {COMMAND_NAME}
    """
    if not is_sub_command:
        # This isn't very useful for the main help text as it only shows `-h`,
        # so comment this text out.
        help_output = help_output.replace(
            "usage: " + COMMAND_NAME,
            ".. NOTE: usage is commented, currently unhelpful.\n"
            "       " + COMMAND_NAME,
        )
        return help_output

    help_output = help_output.replace(
        "usage: " + COMMAND_NAME,
        "usage::\n"
        "\n"
        "       " + COMMAND_NAME,
    )
    return help_output


def patch_help_text_positional_arguments(help_output: str) -> str:
    """
    Render positional arguments as field-list.

    Replace:
       positional arguments:
         id                    The repository identifier.

    With:
       positional arguments:
         :id:                    The repository identifier.
    """

    find = "positional arguments:\n"
    i_beg = help_output.find(find)
    if i_beg == -1:
        return help_output

    i_end = help_output.find("\n\n", i_beg)
    if i_end == -1:
        i_end = len(help_output)
    i_end += 1
    help_output_subset = help_output[i_beg:i_end]

    def re_replace_fn(match: re.Match[str]) -> str:
        groups = list(match.groups())
        groups[1] = ":{:s}:".format(groups[1])
        return "".join(groups)

    re_positional_args = re.compile(r"^(  )([a-z09-_]+)\b", re.MULTILINE)
    help_output_subset = re_positional_args.sub(re_replace_fn, help_output_subset)

    return help_output[:i_beg] + help_output_subset + help_output[i_end:]


def patch_help_text_choice(help_output: str) -> str:
    """
    Curly braces cause the ``-`` prefixed arguments not to be recognized as arguments.

    Convert:
       ``--output-type {TEXT,JSON,JSON_0}``
    To:
       ``--output-type <TEXT,JSON,JSON_0>``
    """
    def re_replace_fn(match: re.Match[str]) -> str:
        groups = list(match.groups())
        assert groups[1] == "{"
        assert groups[3] == "}"
        groups[1] = "<"
        groups[3] = ">"
        return "".join(groups)

    re_choice = re.compile("( +-[a-z-]+ +)({)([a-zA-Z0-9_,]+)(})")
    help_output = re_choice.sub(re_replace_fn, help_output)

    return help_output


def patch_help_text_all(help_output: str, is_sub_command: bool) -> str:
    """
    Transform all help text.
    """
    # NOTE: the order doesn't matter.
    help_output = patch_help_text_usage(help_output, is_sub_command)
    help_output = patch_help_text_positional_arguments(help_output)
    help_output = patch_help_text_choice(help_output)
    return help_output


def patch_help_text_main(
        help_output: str,
        sub_commands: Sequence[str],
        sub_commands_orig: Sequence[str],
) -> str:
    help_output = help_output.replace('{' + ','.join(sub_commands_orig) + '}', '')
    help_output = re.sub(r"[ \t]+(\n|\Z)", r"\1", help_output)

    if USE_TITLE_GROUPS:
        index_range = [len(help_output), 0]

        sub_command_with_lines = []

        re_sub_command = re.compile("^(    )([a-z0-9-]+)( )([^\\n]+)", re.MULTILINE)

        def re_replace_fn(match: re.Match[str]) -> str:
            sub_command = match.group(2)
            if sub_command in sub_commands:
                index_range[0] = min(index_range[0], match.start(0))
                index_range[1] = max(index_range[1], match.end(0) + 1)

                groups = list(match.groups())
                groups_copy = list(groups)
                groups_copy[1] = ":{:s}:".format(groups_copy[1])

                sub_command_with_lines.append((sub_command, "".join(groups_copy) + "\n"))

            return "".join(groups)

        help_output = re_sub_command.sub(re_replace_fn, help_output)

        sub_command_with_lines.sort(key=lambda item: sub_commands.index(item[0]))

        lines = []

        title_prev = ""

        for sub_command, line in sub_command_with_lines:
            title = sub_command_titles_reverse_map[sub_command]
            if title != title_prev:
                title_prev = title
                # Link to the title.
                lines.append("\n  `{:s}`_\n".format(title))
            lines.append(line)

        help_output_sub_commands = "".join(lines)
        del lines

        help_output = help_output[:index_range[0]] + help_output_sub_commands + help_output[index_range[1]:]

    else:
        for sub_command in sub_commands:
            help_output = help_output.replace(
                "    {:s} ".format(sub_command),
                "    :{:s}: ".format(sub_command)
            )
    return help_output


def blender_command_output(blender_bin: str, args: Sequence[str]) -> str:
    """
    Run ``blender --command`` with additional arguments.

    The output is captured and returned without any other debug text.
    """
    env = os.environ.copy()
    env["ASAN_OPTIONS"] = (
        env.get("ASAN_OPTIONS", "") +
        ":exitcode=0:check_initialization_order=0:strict_init_order=0:detect_leaks=0"
    )

    text_beg = "BEGIN_BLOCK"
    text_end = "END_BLOCK"
    text = subprocess.check_output(
        (
            blender_bin,
            "--factory-startup",
            "--python-exit-code", "1",
            # Code begin/end text because of Blender's chatty reporting of version and that it quit.
            "--python-expr", "print('{:s}')".format(text_beg),
            "--python-expr", "__import__('atexit').register(lambda: print('{:s}'))".format(text_end),
            "--command", *args,
        ),
        env=env,
    ).decode("utf-8")

    # Extract between begin/end markers.
    text = text[text.find(text_beg) + len(text_beg) + 1: text.find(text_end)]

    return text


def sub_commands_from_help_output(help_output: str) -> List[str]:
    """
    Extract a list of sub-commands from the help text.
    """
    find = "\nsubcommands:\n"
    i = help_output.find(find)
    if i == -1:
        # Should never happen, unless Python change their text.
        raise Exception("Not found! {!r}".format(find))

    i += len(find)
    beg = help_output.find("{", i)
    if beg == -1:
        sys.stderr.write("Error: could not find sub-command end '}'\n")
        sys.exit(1)
    beg += 1
    end = help_output.find("}", beg)
    if end == -1:
        sys.stderr.write("Error: could not find sub-command end '}'\n")
        sys.exit(1)

    return help_output[beg:end].split(",")


def help_text_as_rst(blender_bin: str) -> str:
    text_header = (
        ".. DO NOT EDIT THIS FILE, GENERATED BY '{:s}'\n"
        "\n"
        "   CHANGES TO THIS FILE MUST BE MADE IN BLENDER'S SOURCE CODE, SEE:\n"
        "   https://projects.blender.org/blender/blender-addons-contrib/src/branch/main/bl_pkg/bl_extension_cli.py\n"
        "\n"
        ".. _command_line-args-extensions:\n"
        "\n"
        "*********************************\n"
        "Extensions Command Line Arguments\n"
        "*********************************\n"
        "\n"
    ).format(os.path.basename(__file__))

    text = blender_command_output(blender_bin, ("extension", "--help"))

    sub_commands = sub_commands_from_help_output(text)
    sub_commands_orig = sub_commands

    if USE_TITLE_GROUPS:
        sub_commands_real = set(sub_commands)
        sub_commands_title = set(sub_command_order)
        if (sub_commands_delta := sub_commands_real - sub_commands_title):
            sys.stderr.write("Error: sub-commands missing from title-map: {!r}!\n".format(sub_commands_delta))
            sys.exit(1)
        if (sub_commands_delta := sub_commands_title - sub_commands_real):
            sys.stderr.write("Error: sub-commands from title-map not in command: {!r}!\n".format(sub_commands_delta))
            sys.exit(1)
        del sub_commands_real, sub_commands_title, sub_commands_delta

        sub_commands = list(sub_command_order)

    text = patch_help_text_all(text, False)
    text = patch_help_text_main(text, sub_commands, sub_commands_orig)
    help_output = [text_header, text + "\n\n"]

    if USE_TITLE_GROUPS:
        title_prev = ""

    for sub_command in sub_commands:

        if USE_TITLE_GROUPS:
            title = sub_command_titles_reverse_map[sub_command]
            if title != title_prev:
                title_prev = title
                help_output.append("\n\n{:s}\n{:s}\n\n".format(title, "=" * len(title)))

        text_sub_command = blender_command_output(blender_bin, ("extension", sub_command, "--help"))
        text_sub_command = patch_help_text_all(text_sub_command, True)
        title = "Subcommand: ``" + sub_command + "``"
        help_output.append(
            ".. _command-line-args-extension-{:s}:\n\n".format(sub_command) +
            title + "\n" +
            ("-" * len(title)) + "\n\n" +
            text_sub_command.rstrip() +
            "\n\n"
        )

    # Strip trailing space.
    for i in range(len(help_output)):
        help_output[i] = re.sub(r"[ \t]+(\n|\Z)", r"\1", help_output[i])

    result = "".join(help_output)

    # Remove excessive newlines.
    # Could be investigated in the generated help text but it's quite harmless to change here.
    while "\n\n\n\n" in result:
        result = result.replace("\n\n\n\n", "\n\n\n")
    result = result.rstrip("\n") + "\n"

    return result


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

    text_rst = help_text_as_rst(blender_bin)

    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(text_rst)
    print("Updated:", os.path.relpath(output_file, BASE_DIR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
