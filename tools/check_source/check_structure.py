#!/usr/bin/env python3
# Apache License, Version 2.0

"""
This utility checks the overall structure of the manual:

- Ensures each directory contains an index file.
"""

import sys
import os


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


def main():
    if "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)

    find_subdirs_without_index(RST_DIR)


if __name__ == "__main__":
    main()
