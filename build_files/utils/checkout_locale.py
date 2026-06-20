import argparse
import re
import sys
import os

from pathlib import Path
from make_utils import check_output

from typing import (
    List,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--git-command", default="git")
    parser.add_argument("languages", nargs="*")
    return parser.parse_args()


def prompt_for_languages() -> List[str]:
    print("Enter language code(s) to checkout (space or comma separated, e.g. fr ru zh-hans vi):")
    raw = input().strip()
    return [l for l in re.split(r"[\s,]+", raw) if l]


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




def partial_checkout(languages: List[str]):
    manual_dir = get_manual_git_root()
    locale_dir = os.path.join(manual_dir, "locale")

    print(run_git(manual_dir, [
        "clone",
        "--filter=blob:none",
        "--no-checkout",
        repo_url_git,
        locale_dir,
    ]))

    run_git(locale_dir, ["sparse-checkout", "set", "--cone"])
    print(run_git(locale_dir, ["checkout", "main"]))

    for lang in languages:
        run_git(locale_dir, ["sparse-checkout", "add", lang])


if __name__ == "__main__":
    args = parse_arguments()

    # Flatten any comma-separated values passed on the command line
    raw_langs = []
    for item in args.languages:
        raw_langs.extend(re.split(r"[\s,]+", item))
    languages = [l for l in raw_langs if l]

    if not languages:
        languages = prompt_for_languages()

    if not languages:
        print("No language(s) specified.")
        sys.exit(1)

    if locale_exists():
        print("locale directory already exists quitting")
        sys.exit(1)

    partial_checkout(languages)
