#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later

"""
"make update" for all platforms, git repository
"""

import argparse
import os
import sys

import make_utils
from pathlib import Path
from make_utils import call, check_output

from typing import (
    List,
)


class Submodule:
    path: str
    branch: str
    branch_fallback: str

    def __init__(self, path: str, branch: str, branch_fallback: str) -> None:
        self.path = path
        self.branch = branch
        self.branch_fallback = branch_fallback


def print_stage(text: str) -> None:
    print("")
    print(text)
    print("")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-manual", action="store_true")
    parser.add_argument("--no-locale", action="store_true")
    parser.add_argument("--git-command", default="git")
    return parser.parse_args()


def run_git(path: Path, commands: List, exit_on_error: bool = True) -> str:
    args = parse_arguments()

    return check_output([args.git_command, "-C", path] + commands, exit_on_error)


def get_manual_git_root() -> str:
    return check_output([args.git_command, "rev-parse", "--show-toplevel"])


def git_update_skip(args: argparse.Namespace, path: Path, check_remote_exists: bool = True) -> str:
    """Tests if git repo can be updated"""

    if make_utils.command_missing(args.git_command):
        sys.stderr.write("git not found, can't update manual\n")
        sys.exit(1)

    if make_utils.command_missing(args.git_command + "-lfs"):
        sys.stderr.write("git LFS not found, can't update manual\n")
        sys.exit(1)

    # Abort if a rebase is still progress.
    rebase_merge = run_git(
        path, ['rev-parse', '--git-path', 'rebase-merge'], exit_on_error=False)
    rebase_apply = run_git(
        path, ['rev-parse', '--git-path', 'rebase-apply'], exit_on_error=False)
    merge_head = run_git(
        path, ['rev-parse', '--git-path', 'MERGE_HEAD'], exit_on_error=False)
    if (
            os.path.exists(rebase_merge) or
            os.path.exists(rebase_apply) or
            os.path.exists(merge_head)
    ):
        return "rebase or merge in progress, complete it first"

    # Abort if uncommitted changes.
    changes = run_git(path, ['status', '--porcelain',
                      '--untracked-files=no', '--ignore-submodules'])
    if len(changes) != 0:
        return "you have unstaged changes"

    # Test if there is an upstream branch configured
    if check_remote_exists:
        branch = run_git(path, ["rev-parse", "--abbrev-ref", "HEAD"])
        remote = run_git(path, ["config", "branch." +
                         branch + ".remote"], exit_on_error=False)
        if len(remote) == 0:
            return "no remote branch to pull from"

    return ""


def use_upstream_workflow(args: argparse.Namespace, path: Path) -> bool:
    return make_utils.git_remote_exist([args.git_command, "-C", path], "upstream")


def work_tree_update_upstream_workflow(args: argparse.Namespace, path: Path, use_fetch: bool = True) -> str:
    """
    Update the repository using the Github style of fork organization

    Returns true if the current local branch has been updated to the upstream state.
    Otherwise false is returned.
    """

    branch_name = make_utils.git_branch([args.git_command, "-C"], path)

    if use_fetch:
        run_git(path, ["fetch", "upstream"])

    upstream_branch = f"upstream/{branch_name}"
    if not make_utils.git_branch_exists([args.git_command, "-C", path], upstream_branch):
        return "no_branch"

    retcode = call((args.git_command, "-C", path, "merge",
                   "--ff-only", upstream_branch), exit_on_error=False)
    if retcode != 0:
        return "Unable to fast forward\n"

    return ""


def work_tree_update(args: argparse.Namespace, path: Path, use_fetch: bool = True) -> str:
    """
    Update the Git working tree using the best strategy

    This function detects whether it is a github style of fork remote organization is used, or
    is it a repository which origin is an upstream.
    """

    if use_upstream_workflow(args, path):
        message = work_tree_update_upstream_workflow(args, path, use_fetch)
        if message != "no_branch":
            return message

        # If there is upstream configured but the local branch is not in the upstream, try to
        # update the branch from the fork.

    run_git(path, ["pull", "--rebase"])

    return ""


def manual_update(args: argparse.Namespace) -> str:
    """Update the root manual directory"""

    print_stage("Updating Manual Git Repository")

    return work_tree_update(args, Path(get_manual_git_root()))


def locale_exists() -> bool:
    locale_dir = os.path.join(get_manual_git_root(), "locale")
    if os.path.exists(locale_dir):
        return True

    return False


def locale_update(args: argparse.Namespace) -> str:
    """Update the translations directory"""

    if not locale_exists():
        return "locale directory not found skipping"

    print_stage("Updating manual translations Git Repository")

    locale_dir = os.path.join(get_manual_git_root(), "locale")

    return work_tree_update(args, locale_dir)


if __name__ == "__main__":
    args = parse_arguments()
    manual_skip_msg = ""
    locale_skip_msg = ""

    manual_dir = get_manual_git_root()
    locale_dir = os.path.join(get_manual_git_root(), "locale")

    if not args.no_manual:
        manual_skip_msg = git_update_skip(args, manual_dir)
        if not manual_skip_msg:
            manual_skip_msg = manual_update(args)
        if manual_skip_msg:
            manual_skip_msg = "Manual repository skipped: " + manual_skip_msg + "\n"
    if not args.no_locale:
        locale_skip_msg = git_update_skip(args, locale_dir)
        if not locale_skip_msg:
            locale_skip_msg = locale_update(args)
        if locale_skip_msg:
            locale_skip_msg = "locale repository skipped: " + locale_skip_msg + "\n"

    # Report any skipped repositories at the end, so it's not as easy to miss.
    skip_msg = manual_skip_msg + locale_skip_msg
    if skip_msg:
        print_stage(skip_msg.strip())
