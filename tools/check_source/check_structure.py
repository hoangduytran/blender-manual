#!/usr/bin/env python3
# Apache License, Version 2.0

"""
This utility checks the overall structure of the manual:

- Ensures each directory contains an index file.
"""

import sys
import os
import re
from collections import defaultdict


# if you want to operate on a subdir, e.g: "render"
SUBDIR = ""
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "..", ".."))
RST_DIR = os.path.join(ROOT_DIR, "manual", SUBDIR)


def print_title(title, underline="="):
    print(f"\n{title}\n{len(title) * underline}")


# Ensure each directory contains an index file.
def find_subdirs_without_index(root_dir):
    print_title("List of directories missing index.rst:")
    for dirpath, _dirnames, filenames in os.walk(root_dir):
        # Skip the '/manual/images' directory
        if '/manual/images' in dirpath:
            continue

        if 'index.rst' not in filenames:
            print(dirpath)


def find_rst_titles(root_dir):
    # Only match overline/underline titles using * or #
    title_pattern = re.compile(
        r'^(?P<line>[#*]{3,})\n(?P<title>.+?)\n(?P=line)$',
        re.MULTILINE
    )

    titles = defaultdict(list)

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.rst'):
                file_path = os.path.join(dirpath, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = title_pattern.search(content)
                    if match:
                        title = match.group('title').strip()
                        titles[title].append(file_path)

    # Report duplicates
    duplicates = {t: paths for t, paths in titles.items() if len(paths) > 1}
    if duplicates:
        print("Duplicate titles found:")
        for title, files in duplicates.items():
            print(f'\nTitle: "{title}"')
            for f in files:
                print(f' - {f}')
    else:
        print("All .rst titles with * or # overline/underline are unique.")


def main():
    if "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)

    find_subdirs_without_index(RST_DIR)
    find_rst_titles(RST_DIR)


if __name__ == "__main__":
    main()
