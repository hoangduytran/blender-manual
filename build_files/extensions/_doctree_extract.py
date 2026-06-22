"""Shared doctree-extraction helpers for the Sphinx build extensions.

Both ``search_index_builder`` (source language) and ``repeatable_builder``
(translated languages) walk a resolved doctree, resolve deep-link anchors, map
node source paths back to repo-relative RST paths, and serialise their result
as an atomic gzip-pickle.  That common machinery lives here so neither
extension re-implements it and the two stay byte-for-byte consistent.

Every function is pure or I/O-at-the-boundary and takes its dependencies as
parameters, so it is unit-testable without a running Sphinx application.
"""

from __future__ import annotations

import gzip
import os
import pickle
from pathlib import Path
from typing import Callable

from docutils import nodes

# tools/ is placed on sys.path by manual/conf.py (and by the test bootstrap),
# so the shared constants import cleanly here.
from common.constants import (  # type: ignore[import-not-found]
    DEFAULT_LANGUAGE,
    HTML_BUILDER_NAME,
    RST_SUFFIX,
    TEMP_SUFFIX,
)

# A mapper from a node's absolute source path (+ docname fallback) to the
# repo-relative RST path, e.g. "manual/editors/geometry_node.rst".
RelSource = Callable[["str | None", str], str]


# ---------------------------------------------------------------------------
# Deep-link anchor resolution
# ---------------------------------------------------------------------------

def nearest_section_id(node: nodes.Node) -> str:
    """Return the id of the nearest enclosing ``section`` (deep-link anchor).

    Walks ancestors until a ``section`` carrying at least one id is found.

    Args:
        node: Any doctree node.

    Returns:
        The first id of the closest enclosing identified section, or ``""``
        when the node is not inside any identified section (e.g. a stray
        top-of-document node).
    """
    current: nodes.Node | None = node
    while current is not None:
        if isinstance(current, nodes.section):
            ids = current.get("ids") or []
            if ids:
                return ids[0]
        current = current.parent
    return ""


# ---------------------------------------------------------------------------
# Source-path mapping
# ---------------------------------------------------------------------------

def make_rel_source(srcdir: Path) -> RelSource:
    """Build a mapper from an absolute node source path to a repo-relative RST path.

    Repo-relative means ``manual/<...>.rst`` — matching the PO/parser format
    (locale PO files carry the same suffix without the ``../../`` prefix).

    Args:
        srcdir: Sphinx ``app.srcdir`` (the ``manual/`` directory).

    Returns:
        A callable ``rel_source(source, docname)`` that returns the
        repo-relative RST path for *source*, falling back to
        ``<srcdir-name>/<docname>.rst`` when *source* is empty or on a
        different drive (Windows).
    """
    repo_root = srcdir.parent          # srcdir == manual/ → parent == repo root
    source_dir_name = srcdir.name      # "manual"

    def rel_source(source: "str | None", docname: str) -> str:
        if source:
            try:
                return Path(os.path.relpath(source, repo_root)).as_posix()
            except ValueError:
                pass  # different drive on Windows → fall through to docname form
        return f"{source_dir_name}/{docname}{RST_SUFFIX}"

    return rel_source


# ---------------------------------------------------------------------------
# Atomic gzip-pickle writer
# ---------------------------------------------------------------------------

def write_gzip_pickle(payload: object, out_path: Path) -> None:
    """Serialise *payload* as a gzip-compressed pickle, written atomically.

    Writes to a temporary sibling then ``os.replace()`` so a concurrent reader
    (e.g. the docs server) never sees a half-written file.  A trusted, local
    build artifact only — never unpickle an untrusted file with the loader.

    Args:
        payload: Any picklable object (the extension's envelope dict).
        out_path: Final destination path; parent directories are created.

    Raises:
        Exception: Re-raises any serialisation error after removing the temp
            file, so a previously written final artifact is left intact.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.parent / (out_path.name + TEMP_SUFFIX)
    try:
        with gzip.open(tmp_path, "wb", compresslevel=6) as handle:
            pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp_path, out_path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


# ---------------------------------------------------------------------------
# Build gating
# ---------------------------------------------------------------------------

def is_html_builder(app) -> bool:
    """True when the active builder emits HTML output."""
    return getattr(app.builder, "format", "") == HTML_BUILDER_NAME


def is_source_language(language: "str | None") -> bool:
    """True when *language* is the source language (English) or unset."""
    return language in (None, "", DEFAULT_LANGUAGE)


def is_translated_language(language: "str | None") -> bool:
    """True when *language* is a real translation target (not the source)."""
    return not is_source_language(language)
