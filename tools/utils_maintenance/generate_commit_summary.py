#!/usr/bin/env python3
# Apache License, Version 2.0

"""
This tool generates a summary list of Blender commits and their details.
This list can be used as a release checklist on projects.blender.org
for commits that need documentation change.
"""

import argparse

from pathlib import Path
from git import Repo


def print_summary(repo, commits):
    for commit_hash in commits:

        if commit_hash == "\n":
            print("")
            continue

        commit = repo.commit(commit_hash)
        commit_hash_short = commit_hash[:10]
        commit_url = "https://projects.blender.org/blender/blender/commit/" + commit_hash_short
        commit_title = commit.message.partition('\n')[0]
        commit_author = commit.author

        print("- [ ] [{}]({}) {} ({})".format(commit_hash_short,
                                              commit_url, commit_title, commit_author))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage=__doc__
    )

    parser.add_argument(
        "--commits",
        dest="commits",
        default="commits.tmp",
        required=False,
        help="Path to a file with a list of Git sha hashes of the noteworthy commits.",
        metavar="FILE")

    parser.add_argument(
        "--blender-repo",
        dest="repo_path",
        required=True,
        help="Path to the root directory of the Blender Git repository.")

    args = parser.parse_args()

    repo = Repo(Path(args.repo_path))

    commit_log = open(args.commits, 'r')
    commits = commit_log.readlines()

    print_summary(repo, commits)
