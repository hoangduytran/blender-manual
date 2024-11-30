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
    print(f"""
| Code Change |  Manual Change | Link to Documentation |
| -------- | ------- | ------- |""")

    # Collect commit details
    commit_details = []
    for commit_hash in commits:

        if commit_hash == "\n":
            print("")
            continue

        # Get commit details
        commit = repo.commit(commit_hash)
        commit_url = f"https://projects.blender.org/blender/blender/commit/{commit_hash[:10]}"
        commit_title = commit.message.partition('\n')[0]  # First line of the commit message

        # Store commit details in a tuple
        commit_details.append((commit_title, commit_url))

    # Sort commits alphabetically by title
    commit_details.sort(key=lambda x: x[0].lower())

    # Print sorted commit details
    for title, url in commit_details:
        print(f"| [{title}]({url}) |||")

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
