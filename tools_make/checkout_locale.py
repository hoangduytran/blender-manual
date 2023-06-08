import argparse

import sys
import os
import requests

from pathlib import Path
from make_utils import check_output

from typing import (
    List,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--git-command", default="git")
    return parser.parse_args()


repo_url_base = "https://projects.blender.org/blender/blender-manual-translations/"
repo_url_browse = "src/branch/main/"
repo_url_git = "https://projects.blender.org/blender/blender-manual-translations.git"


def run_git(path: Path, commands: List, exit_on_error: bool = True) -> str:
    args = parse_arguments()

    return check_output([args.git_command, "-C", path] + commands, exit_on_error)


def get_manual_git_root() -> str:
    return check_output([args.git_command, "rev-parse", "--show-toplevel"])


def locale_exists() -> bool:
    locale_dir = os.path.join(get_manual_git_root(), "locale")
    if os.path.exists(locale_dir):
        return True

    return False


def get_lang_code():
    print("Enter the language code for the language you would like to checkout:")
    return str(input())


def check_lang_exists(lang: str) -> bool:
    url = repo_url_base + repo_url_browse + lang

    url_status = requests.get(url).status_code

    if url_status == 200:
        return True

    return False


def partial_checkout(lang: str):
    manual_dir = get_manual_git_root()
    locale_dir = os.path.join(manual_dir, "locale")

    print(run_git(manual_dir, ["clone", "--filter=blob:none", "--no-checkout", repo_url_git, locale_dir]))
    run_git(locale_dir, ["sparse-checkout", "set", "--cone"])
    run_git(locale_dir, ["sparse-checkout", "add", lang])
    print(run_git(locale_dir, ["checkout", "main"]))


if __name__ == "__main__":
    args = parse_arguments()

    if locale_exists():
        print("locale directory already exists quitting")
        sys.exit(1)

    lang = get_lang_code()

    if not check_lang_exists(lang):
        print("The translation files for that language do not exist")
        sys.exit(1)

    partial_checkout(lang)
