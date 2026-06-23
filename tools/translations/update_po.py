#!/usr/bin/env python3
# Apache License, Version 2.0

# This script is to reduce tedious steps involved when updating PO files
# for multiple languages.
# It looks more complex then it really is, since we do multi-processing
# to update the PO files, to save some time.

import os
import sys
import shutil
import subprocess
import multiprocessing
from shlex import quote, split as shlex_split
import re

# Output goes through the logging module rather than print(). A plain stdlib
# logger is used (not sphinx.util.logging.getLogger) deliberately: the Sphinx
# wrapper inserts its own frame, so %(funcName)s/%(filename)s would always
# resolve to "logging.py:log" instead of the real caller. __main__ installs the
# console handler whose format includes the routine and file name.
import logging

_logger = logging.getLogger(__name__)


VERBOSE = False
USE_MULTI_PROCESS = True

# Fallback if manual/conf.py cannot be read or omits the setting (see
# read_sphinx_intl_command); mirrors the conf.py default.
SPHINX_INTL_COMMAND_DEFAULT = "sphinx-intl"

# Regex scraping `sphinx_intl_command = "..."` out of manual/conf.py.  Same
# shape as smart_mo_compile.ConfPattern's conf.py scrapers: an anchored
# assignment whose quoted value is captured in the named group `value`.
SPHINX_INTL_COMMAND_RE = r'^sphinx_intl_command\s*=\s*["\'](?P<value>[^"\']+)["\']'


def read_sphinx_intl_command(conf_py_path):
    """Return the sphinx-intl invocation as an argv list, read from conf.py.

    The command name lives in manual/conf.py (``sphinx_intl_command``) so a
    rename — or a switch to the interpreter-pinned ``"python -m sphinx_intl"``
    form — is a one-line edit there rather than three literals here. Scraped by
    regex (not import) so Sphinx-only globals in conf.py are never evaluated,
    matching how smart_mo_compile.py reads the same file. Falls back to
    :data:`SPHINX_INTL_COMMAND_DEFAULT` when the file or setting is absent.
    """
    command = SPHINX_INTL_COMMAND_DEFAULT
    try:
        text = open(conf_py_path, encoding="utf-8").read()
    except OSError:
        text = ""
    m = re.search(SPHINX_INTL_COMMAND_RE, text, re.MULTILINE)
    if m:
        command = m.group("value")
    # shlex so multi-word forms like "python -m sphinx_intl" split correctly.
    return shlex_split(command)


def run_git(args, with_output=False):
    cmd = ["git", *args]
    if VERBOSE:
        _logger.debug(">>>  %s", cmd)

    if not with_output:
        subprocess.check_call(
            cmd,
        )
    else:
        return subprocess.check_output(
            cmd,
        )


def run_multiprocess__single(arg_list):
    return_codes = [None] * len(arg_list)
    # Single process.
    for args_index, args in enumerate(arg_list):
        proc = subprocess.Popen([*SPHINX_INTL_CMD, *args])
        proc.wait()
        return_codes[args_index] = proc.returncode

    return return_codes


def run_multiprocess__multi(arg_list, job_total=1):
    return_codes = [None] * len(arg_list)

    # Real multi-processing.
    import time
    processes = []

    def processes_clear_finished():
        for proc_index in reversed(range(len(processes))):
            proc_cmd_index, proc = processes[proc_index]
            if proc.poll() is not None:
                del processes[proc_index]
                return_codes[proc_cmd_index] = proc.returncode

    for args_index, args in enumerate(arg_list):
        while True:
            processes_clear_finished()
            if len(processes) <= job_total:
                break
            else:
                time.sleep(0.1)

        sys.stdout.flush()
        sys.stderr.flush()

        processes.append(
            (args_index, subprocess.Popen([*SPHINX_INTL_CMD, *args])))

    while processes:
        processes_clear_finished()
        time.sleep(0.1)

    return return_codes


def run_multiprocess(arg_list, job_total=1):
    if job_total <= 1:
        return run_multiprocess__single(arg_list)
    else:
        return run_multiprocess__multi(arg_list, job_total)


# -----------------------------------------------------------------------------
# Setup Global State


if USE_MULTI_PROCESS:
    CPU_COUNT = multiprocessing.cpu_count()
else:
    CPU_COUNT = 1

# --- Environment, directory, and filename literals (declared once) ---
LANG_ENV_VAR = "LANG"              # env var Python/gettext read for the locale
UTF8_LOCALE = "en_US.UTF-8"        # value forced into LANG so output is utf-8
PARENT_DIR = os.pardir             # ".." — portable parent-directory marker
BUILD_SUBDIR = "build"             # top-level build output directory
GETTEXT_SUBDIR = "gettext"         # 'make gettext' .pot output under build/
LOCALE_SUBDIR = "locale"           # per-language .po tree at the repo root
MANUAL_SUBDIR = "manual"           # RST source root (holds conf.py)
CONF_PY_FILENAME = "conf.py"       # Sphinx config scraped for settings
POT_FILENAME = "blender_manual.pot"  # gettext template merged into each .po

# Python needs utf-8.
os.environ[LANG_ENV_VAR] = UTF8_LOCALE

# Ensure we're in the repo's base:
ROOT_DIR = os.path.normpath(os.path.join(
    os.path.abspath(os.path.dirname(__file__)), PARENT_DIR, PARENT_DIR))
os.chdir(ROOT_DIR)
LOCALE_BUILD_DIR = os.path.join(ROOT_DIR, BUILD_SUBDIR, GETTEXT_SUBDIR)

LOCALE_DIR = os.path.join(ROOT_DIR, LOCALE_SUBDIR)

POT_FILE = os.path.join(LOCALE_DIR, POT_FILENAME)

# sphinx-intl invocation as an argv list, sourced from manual/conf.py so the
# tool name is declared in one place (see read_sphinx_intl_command).
SPHINX_INTL_CMD = read_sphinx_intl_command(
    os.path.join(ROOT_DIR, MANUAL_SUBDIR, CONF_PY_FILENAME))


# -----------------------------------------------------------------------------
# Main Function

def main():

    # ---------------------
    # Update the Locale Dir
    status = run_git(["-C", LOCALE_DIR, "status"], True)

    if b"nothing to commit, working tree clean" not in status:
        sys.exit(
            "Locale directory has uncommitted changes, please stash or comment them")

    run_git(["-C", LOCALE_DIR, "pull", "--rebase"])

    # ---------------
    # Create PO Files

    if os.path.exists(LOCALE_BUILD_DIR):
        shutil.rmtree(LOCALE_BUILD_DIR)

    # Same as 'make gettext'.
    subprocess.check_call([
        "sphinx-build",
        "-t", "builder_html",
        "-b", "gettext",
        "-j", str(CPU_COUNT),
        # Source.
        MANUAL_SUBDIR,
        # Destination.
        LOCALE_BUILD_DIR,
    ])

    # -------------
    # Copy POT File

    shutil.copy(os.path.join(LOCALE_BUILD_DIR,
                POT_FILENAME), LOCALE_DIR)

    # ---------------
    # Update PO Files
    #
    # Note, this can be slow so (multi-process).

    po_lang_all = []
    for po_lang in os.listdir(LOCALE_DIR):
        if (not po_lang.startswith((".", "_")) and
                os.path.isdir(os.path.join(LOCALE_DIR, po_lang))):
            po_lang_all.append(po_lang)
    # Only for reproducible execution.
    po_lang_all.sort()

    sphinx_intl_arg_list = []
    for po_lang in po_lang_all:
        sphinx_intl_arg_list.append([
            "--config=" + os.path.join(MANUAL_SUBDIR, CONF_PY_FILENAME),
            "update",
            "--pot-dir=" + LOCALE_BUILD_DIR,
            "--language=" + po_lang,
        ])

    sphinx_intl_return_codes = run_multiprocess(
        sphinx_intl_arg_list,
        job_total=CPU_COUNT,
    )

    if set(sphinx_intl_return_codes) - {0}:
        _logger.warning("Warning, the following commands returned non-zero exit codes:")
        for returncode, arg in zip(sphinx_intl_return_codes, sphinx_intl_arg_list):
            if returncode != 0:
                _logger.warning(
                    "returncode: %s from command: %s %s",
                    returncode, " ".join(SPHINX_INTL_CMD), arg,
                )
        _logger.warning("Some manual corrections might need to be done.")
    del sphinx_intl_return_codes, sphinx_intl_arg_list

    # ---------------------
    # Print Commit Messages
    #
    # Use space prefix as shell's (bash/zsh/fish) uses this as a hint not to store in the users history.
    revision = run_git(["-C", ROOT_DIR, "rev-parse",
                       "--short", "HEAD"], True).decode('utf8').strip()
    revision = revision if revision else "Unknown"
    _logger.info("\nPo files updated, commit files using the following commands:")
    _logger.info("cd locale")
    _logger.info("git add -A")
    _logger.info("git commit -m \"Update po-files (%s)\"", revision)


if __name__ == "__main__":
    # Console handler for this standalone script. The format leads with the
    # file name, routine, and line number so every line says where it came
    # from; %(funcName)s/%(filename)s resolve to the real caller because
    # _logger is a plain stdlib logger (see the import note above).
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(filename)s:%(funcName)s:%(lineno)d %(levelname)s: %(message)s",
    )
    main()
