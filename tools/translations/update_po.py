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
from shlex import quote
import re


VERBOSE = False
USE_MULTI_PROCESS = True


def run_git(args, with_output=False):
    cmd = ["git", *args]
    if VERBOSE:
        print(">>> ", cmd)

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
        proc = subprocess.Popen(["sphinx-intl", *args])
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
            (args_index, subprocess.Popen(["sphinx-intl", *args])))

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

# Python needs utf-8.
os.environ["LANG"] = "en_US.UTF-8"

# Ensure we're in the repo's base:
ROOT_DIR = os.path.normpath(os.path.join(
    os.path.abspath(os.path.dirname(__file__)), ".."))
os.chdir(ROOT_DIR)
LOCALE_BUILD_DIR = os.path.join(ROOT_DIR, "build", "gettext")

LOCALE_DIR = os.path.join(ROOT_DIR, "locale")

POT_FILE = os.path.join(LOCALE_DIR, "blender_manual.pot")


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
        "manual",
        # Destination.
        LOCALE_BUILD_DIR,
    ])

    # -------------
    # Copy POT File

    shutil.copy(os.path.join(LOCALE_BUILD_DIR,
                "blender_manual.pot"), LOCALE_DIR)

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
            "--config=" + os.path.join("manual", "conf.py"),
            "update",
            "--pot-dir=" + LOCALE_BUILD_DIR,
            "--language=" + po_lang,
        ])

    sphinx_intl_return_codes = run_multiprocess(
        sphinx_intl_arg_list,
        job_total=CPU_COUNT,
    )

    if set(sphinx_intl_return_codes) - {0}:
        print("Warning, the following commands returned non-zero exit codes:")
        for returncode, arg in zip(sphinx_intl_return_codes, sphinx_intl_arg_list):
            if returncode != 0:
                print("returncode:", returncode,
                      "from command:", "sphinx-intl", arg)
        print("Some manual corrections might need to be done.")
    del sphinx_intl_return_codes, sphinx_intl_arg_list

    # ---------------------
    # Print Commit Messages
    #
    # Use space prefix as shell's (bash/zsh/fish) uses this as a hint not to store in the users history.
    revision = run_git(["-C", ROOT_DIR, "rev-parse",
                       "--short", "HEAD"], True).decode('utf8').strip()
    revision = revision if revision else "Unknown"
    print("\nPo files updated, commit files using the following commands:")
    print("cd locale")
    print("git add -A")
    print(
        "git commit -m \"Update po-files ({:s})\"".format(revision))


if __name__ == "__main__":
    main()
