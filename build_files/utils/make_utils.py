#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Utility functions for make update and make tests.
"""

import shutil
import subprocess
import sys

from typing import (
    List,
    Sequence,
)


def call(cmd: Sequence[str], exit_on_error: bool = True, silent: bool = False) -> int:
    if not silent:
        print(" ".join([str(x) for x in cmd]))

    # Flush to ensure correct order output on Windows.
    sys.stdout.flush()
    sys.stderr.flush()

    if silent:
        retcode = subprocess.call(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        retcode = subprocess.call(cmd)

    if exit_on_error and retcode != 0:
        sys.exit(retcode)
    return retcode


def check_output(cmd: Sequence[str], exit_on_error: bool = True) -> str:
    # Flush to ensure correct order output on Windows.
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        if exit_on_error:
            sys.stderr.write(" ".join(cmd))
            sys.stderr.write(e.output + "\n")
            sys.exit(e.returncode)
        output = ""

    return output.strip()


def git_local_branch_exists(git_command: List, branch: str) -> bool:
    return (
        call([git_command, "rev-parse", "--verify", branch],
             exit_on_error=False, silent=True) == 0
    )


def git_remote_branch_exists(git_command: List, remote: str, branch: str) -> bool:
    return call([git_command, "rev-parse", "--verify", f"remotes/{remote}/{branch}"],
                exit_on_error=False, silent=True) == 0


def git_branch_exists(git_command: List, branch: str) -> bool:
    return (
        git_local_branch_exists(git_command, branch) or
        git_remote_branch_exists(git_command, "upstream", branch) or
        git_remote_branch_exists(git_command, "origin", branch)
    )


def git_remote_exist(git_command: List, remote_name: str) -> bool:
    """Check whether there is a remote with the given name"""
    # `git ls-remote --get-url upstream` will print an URL if there is such remote configured, and
    # otherwise will print "upstream".
    remote_url = check_output(
        (git_command + ["ls-remote", "--get-url", remote_name]))
    return remote_url != remote_name


def git_branch(git_command: List) -> str:
    # Get current branch name.
    try:
        branch = subprocess.check_output(
            [git_command, "rev-parse", "--abbrev-ref", "HEAD"])
    except subprocess.CalledProcessError as e:
        sys.stderr.write("Failed to get Blender git branch\n")
        sys.exit(1)

    return branch.strip().decode('utf8')


def command_missing(command: str) -> bool:
    # Support running with Python 2 for macOS
    if sys.version_info >= (3, 0):
        return shutil.which(command) is None
    else:
        return False
