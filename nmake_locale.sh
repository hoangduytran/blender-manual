#!/usr/bin/env bash
#
# nmake_locale.sh — one-shot bootstrap for the multilingual-build fork.
#
# From a fresh clone (or even from scratch), this gets you a ready-to-work
# checkout: it switches to the fork's "new make" tooling branch, wires up the
# Blender upstream remote, fetches the latest, downloads the translation
# catalogue(s) you ask for, and (optionally) sets up the environment and starts
# the live multi-language server — all in one go.
#
# Usage:
#   ./nmake_locale.sh <lang_code> [<lang_code> ...] [options]
#
# Examples:
#   ./nmake_locale.sh vi                 # Vietnamese, ready to build
#   ./nmake_locale.sh vi fr ru           # several languages at once
#   ./nmake_locale.sh vi --serve         # also launch `make liveall` at the end
#   ./nmake_locale.sh vi --no-setup      # skip the `make setup` virtualenv step
#
# Options:
#   --serve              After setup, run `make liveall BF_LANGS="en <langs>"`.
#   --build              After setup, run `make build` (static build, no server).
#   --no-setup           Skip `make setup` (use if your env is already prepared).
#   --branch <name>      Override the fork branch (default below).
#   --include_new_make   Accepted for convenience; switching to the fork branch
#                        (the "new make" tooling) is the default behaviour.
#   -h, --help           Show this help.
#
# Environment overrides:
#   REPO_URL       git remote to clone if not already inside the repo.
#   UPSTREAM_URL   Blender manual repo used for upstream syncing.

set -euo pipefail

# ---- Defaults --------------------------------------------------------------
FORK_BRANCH_DEFAULT="feature/new_make_for_foreign_languages"
REPO_URL="${REPO_URL:-git@github.com:hoangduytran/blender-manual.git}"
UPSTREAM_URL="${UPSTREAM_URL:-https://projects.blender.org/blender/blender-manual.git}"

# ---- Pretty output ---------------------------------------------------------
if [ -t 1 ]; then
    C_BOLD="$(printf '\033[1m')"; C_GREEN="$(printf '\033[32m')"
    C_YELLOW="$(printf '\033[33m')"; C_RED="$(printf '\033[31m')"
    C_RESET="$(printf '\033[0m')"
else
    C_BOLD=""; C_GREEN=""; C_YELLOW=""; C_RED=""; C_RESET=""
fi
say()  { printf '%s==>%s %s\n' "$C_GREEN$C_BOLD" "$C_RESET" "$*"; }
warn() { printf '%s!! %s%s\n' "$C_YELLOW" "$*" "$C_RESET" >&2; }
die()  { printf '%sxx %s%s\n' "$C_RED" "$*" "$C_RESET" >&2; exit 1; }

usage() { sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

# Everything lives in a function so the script is fully parsed into memory
# before it runs. That makes the `git checkout` of the fork branch safe even
# though this very file may differ between branches.
main() {
    local fork_branch="$FORK_BRANCH_DEFAULT"
    local do_setup=1 do_serve=0 do_build=0
    local langs=""

    # ---- Parse arguments ---------------------------------------------------
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help) usage 0 ;;
            --serve) do_serve=1 ;;
            --build) do_build=1 ;;
            --no-setup) do_setup=0 ;;
            --include_new_make) : ;;   # default behaviour; accepted for convenience
            --branch)
                shift; [ $# -gt 0 ] || die "--branch needs a value"
                fork_branch="$1" ;;
            --branch=*) fork_branch="${1#*=}" ;;
            --*) die "Unknown option: $1 (try --help)" ;;
            *) langs="${langs:+$langs }$1" ;;
        esac
        shift
    done

    [ -n "$langs" ] || { warn "No language code given."; usage 1; }
    command -v git  >/dev/null 2>&1 || die "git is required but not found."
    command -v make >/dev/null 2>&1 || die "make is required but not found."

    # ---- Locate or clone the repo -----------------------------------------
    local root
    if root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
        say "Using existing checkout: $root"
    else
        say "Not inside a git checkout — cloning $REPO_URL"
        git clone "$REPO_URL" blender-manual
        root="$(pwd)/blender-manual"
    fi
    cd "$root"

    # ---- Wire up the Blender upstream remote (fetch-only) ------------------
    if git remote get-url upstream >/dev/null 2>&1; then
        git remote set-url upstream "$UPSTREAM_URL"
    else
        say "Adding 'upstream' remote → $UPSTREAM_URL"
        git remote add upstream "$UPSTREAM_URL"
    fi
    git remote set-url --push upstream DISABLE 2>/dev/null || true

    # ---- Switch to the fork ("new make") branch ---------------------------
    say "Fetching latest from origin"
    git fetch origin --prune

    say "Switching to fork branch: $fork_branch"
    if git show-ref --verify --quiet "refs/heads/$fork_branch"; then
        git checkout "$fork_branch"
    elif git show-ref --verify --quiet "refs/remotes/origin/$fork_branch"; then
        git checkout -b "$fork_branch" --track "origin/$fork_branch"
    else
        die "Branch '$fork_branch' not found on origin. Check --branch."
    fi
    git pull --ff-only origin "$fork_branch" || warn "Could not fast-forward $fork_branch (local changes?). Continuing."

    # ---- Environment setup -------------------------------------------------
    if [ "$do_setup" -eq 1 ]; then
        say "Setting up the Sphinx environment (make setup)"
        make setup
    else
        say "Skipping environment setup (--no-setup)"
    fi

    # ---- Download the requested translation catalogue(s) ------------------
    say "Downloading translation catalogue(s): $langs"
    # shellcheck disable=SC2086
    make checkout_locale $langs

    # ---- Done — build/serve or print next steps ---------------------------
    local bf_langs="en $langs"
    if [ "$do_serve" -eq 1 ]; then
        say "Launching live multi-language server (Ctrl-C to stop)"
        make liveall BF_LANGS="$bf_langs"
    elif [ "$do_build" -eq 1 ]; then
        say "Building all languages (static)"
        make build BF_LANGS="$bf_langs"
        say "Done. Serve with:  make serve BF_LANGS=\"$bf_langs\""
    else
        printf '\n%s✔ Ready to work.%s You are on %s with %s downloaded.\n\n' \
            "$C_GREEN$C_BOLD" "$C_RESET" "$fork_branch" "$langs"
        printf 'Start the live multi-language site with:\n'
        printf '    %smake liveall BF_LANGS="%s"%s\n' "$C_BOLD" "$bf_langs" "$C_RESET"
        printf 'Then open http://localhost:8000  (press "/" to search).\n'
        printf 'See FORK.md (FORK_VI.md for tiếng Việt) for the full guide.\n\n'
    fi
}

main "$@"
