import argparse
import os
import re
import sys

from typing import List

from make_utils import check_output

# Reuse the centralised project constants (which mirror manual/conf.py) instead
# of duplicating literals here.  tools/ is added to the path so the import
# resolves when this util is run standalone via the Makefile.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_TOOLS = os.path.join(_REPO_ROOT, "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
from common.constants import LOCALE_DIR  # noqa: E402  # type: ignore[import-not-found]


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

# Git's per-repo marker directory, and the value git reports for
# core.sparseCheckout when sparse-checkout mode is enabled.
GIT_DIR_NAME = ".git"
SPARSE_CHECKOUT_ENABLED_VALUE = "true"


def run_git(path: str, commands: List, exit_on_error: bool = True) -> str:
    args = parse_arguments()

    return check_output([args.git_command, "-C", path] + commands, exit_on_error)


def get_manual_git_root() -> str:
    return check_output([args.git_command, "rev-parse", "--show-toplevel"])


def get_locale_dir() -> str:
    return os.path.join(get_manual_git_root(), LOCALE_DIR)


def locale_exists() -> bool:
    return os.path.isdir(get_locale_dir())


def locale_is_git_checkout(locale_dir: str) -> bool:
    """True when locale/ is itself a git checkout (the translations clone)."""
    return os.path.isdir(os.path.join(locale_dir, GIT_DIR_NAME))


def sparse_checkout_enabled(locale_dir: str) -> bool:
    """True when the locale checkout is in sparse-checkout mode."""
    setting = check_output(
        [args.git_command, "-C", locale_dir, "config", "--get", "core.sparseCheckout"],
        exit_on_error=False,
    )
    return setting.strip() == SPARSE_CHECKOUT_ENABLED_VALUE


def partial_checkout(languages: List[str]):
    """Bootstrap locale/ from scratch: clone, enable sparse, add languages."""
    manual_dir = get_manual_git_root()
    locale_dir = get_locale_dir()

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


def add_languages(locale_dir: str, languages: List[str]):
    """Download languages into an existing locale/ checkout.

    Extends the sparse-checkout set (so new languages are materialised, fetching
    their blobs on demand) and restores any language that is in the set but
    missing from the working tree (e.g. a folder removed by hand). Other
    languages -- including ones with local edits -- are left untouched.
    """
    if sparse_checkout_enabled(locale_dir):
        print(run_git(locale_dir, ["sparse-checkout", "add"] + languages))
    print(run_git(locale_dir, ["restore"] + languages, exit_on_error=False))


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
        locale_dir = get_locale_dir()
        if not locale_is_git_checkout(locale_dir):
            print(f"'{locale_dir}' exists but is not a git checkout of the "
                  "translations repo; remove it and re-run, or fix it manually.")
            sys.exit(1)
        print(f"locale/ present; adding language(s): {', '.join(languages)}")
        add_languages(locale_dir, languages)
    else:
        partial_checkout(languages)
