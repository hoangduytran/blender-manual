"""Build the source-language (English) search index directly from the doctree.

The search overlay is PO-based: each ``SearchableRecord`` is one PO entry and
the index lives at ``build/<lang>/searchindex.pkl.gz`` (built by
``tools/search/index_builder.py`` from ``locale/<lang>/LC_MESSAGES/
blender_manual.po``).  English is the *source* language and has no PO file, so
it never gets an index and the overlay returns "No results" for English pages.

This extension fills that gap.  It extracts searchable messages straight from
the doctree -- the same intermediate Sphinx renders to HTML -- using
``sphinx.util.nodes.extract_messages`` and the same dedup model as Sphinx's own
gettext builder (``sphinx/builders/gettext.py``: aggregate by message text,
locations = sorted unique ``(source, line)``).  So the index it writes is the
English analogue of what ``blender_manual.pot`` would contain.

Why ``doctree-read`` and not ``doctree-resolved``
-------------------------------------------------
Sphinx pickles the build environment **after the read phase but before the
write phase** (``sphinx/builders/__init__.py``: "save the environment" precedes
``self.write(...)``).  ``doctree-resolved`` fires during *write*, so anything
stored on ``env`` there is never persisted -- on the next incremental rebuild it
would be gone and the index would lose every unchanged document.
``doctree-read`` fires during *read*, before the pickle, so per-document records
persist in ``environment.pickle`` and survive incremental rebuilds.  Section
ids (the deep-link anchors) and the translatable text are both already present
at read time, so nothing is lost by extracting here.

Incrementality & parallelism
----------------------------
- ``sphinx-autobuild`` re-reads only changed docs, so ``doctree-read`` fires
  only for those; unchanged docs keep their records on ``env``.
- ``env-purge-doc`` drops a doc's records before it is re-read (clears stale).
- ``env-merge-info`` folds per-worker records back under ``-j auto``.
- ``build-finished`` flattens every doc's records, dedups, and writes the
  gzip-pickle -- identical format to the PO path, so the searcher/loader need
  no changes.

The extension is a no-op for translated builds: it only writes for the source
language, so it never collides with the PO-based watcher that owns
``build/<lang>/searchindex.pkl.gz`` for vi/fr/ru/zh-hans.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from docutils import nodes
from sphinx.util import logging
from sphinx.util.nodes import extract_messages

# tools/ is not on sys.path during a Sphinx build (only build_files/extensions
# is, via conf.py).  Add it so the shared search modules import cleanly.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_TOOLS = _REPO_ROOT / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from common.constants import (  # type: ignore[import-not-found]  # noqa: E402
    DEFAULT_LANGUAGE,
    HTML_SUFFIX,
    RST_SUFFIX,
    SEARCH_INDEX_FILENAME,
)
from search.index_builder import _strip_tones, write_index  # type: ignore[import]  # noqa: E402
from search.searchable_record import SearchableRecord  # type: ignore[import]  # noqa: E402

logger = logging.getLogger(__name__)

# Attribute name under which per-document occurrence lists hang off ``env``.
_ENV_ATTR = "search_index_records"

# One extracted occurrence of a message, kept as a plain tuple so it pickles
# cheaply inside environment.pickle:
#   (msgid, msgctxt, rst_rel_path, line_no, html_page, section_anchor)
Occurrence = tuple


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested without a running Sphinx)
# ---------------------------------------------------------------------------

def nearest_section_id(node: nodes.Node) -> str:
    """Return the id of the nearest enclosing ``section`` (deep-link anchor).

    Walks ancestors until a ``section`` with at least one id is found; returns
    "" when the message is not inside any identified section (e.g. a stray
    top-of-document node).
    """
    cur: nodes.Node | None = node
    while cur is not None:
        if isinstance(cur, nodes.section):
            ids = cur.get("ids") or []
            if ids:
                return ids[0]
        cur = cur.parent
    return ""


def _in_substitution_definition(node: nodes.Node) -> bool:
    """True if *node* lives inside a substitution definition.

    Mirrors Sphinx's gettext builder, which skips these so substitution bodies
    are not extracted as standalone messages.
    """
    cur: nodes.Node | None = node
    while cur is not None:
        if isinstance(cur, nodes.substitution_definition):
            return True
        cur = cur.parent
    return False


def extract_occurrences(
    doctree: nodes.document,
    docname: str,
    lang: str,
    rel_source,
) -> list[Occurrence]:
    """Extract one occurrence per translatable message in *doctree*.

    *rel_source* maps a node's absolute source path to the repo-relative RST
    path (e.g. ``manual/editors/geometry_node.rst``); injected so tests can
    supply a trivial mapper.
    """
    html_page = f"/{lang}/{docname}{HTML_SUFFIX}"
    occurrences: list[Occurrence] = []
    for node, msg in extract_messages(doctree):
        if _in_substitution_definition(node):
            continue
        text = msg
        is_blank_message = not (text and text.strip())
        if is_blank_message:
            continue
        line = node.line if node.line is not None else -1
        rst_rel = rel_source(node.source, docname)
        anchor = nearest_section_id(node)
        msgctxt = ""  # extract_messages yields no context; reserved if ever added
        occurrences.append((text, msgctxt, rst_rel, line, html_page, anchor))
    return occurrences


def aggregate(occurrences) -> list[SearchableRecord]:
    """Merge occurrences into SearchableRecords, deduped like Sphinx's Catalog.

    Records are keyed by ``(msgctxt, msgid)``; parallel ``locations`` /
    ``html_pages`` / ``section_keys`` lists are deduplicated so the same
    page+anchor+line is never listed twice.  ``msgstr`` is left empty: the
    source language has no translation, and search for it runs on ``msgid``
    only.
    """
    by_key: dict[tuple[str, str], SearchableRecord] = {}
    order: list[tuple[str, str]] = []
    for (msgid, msgctxt, rst_rel, line, html_page, anchor) in occurrences:
        key = (msgctxt, msgid)
        rec = by_key.get(key)
        if rec is None:
            rec = SearchableRecord(
                msgid=msgid,
                msgstr="",
                msgid_stripped=_strip_tones(msgid),
                msgstr_stripped="",
                locations=[],
                html_pages=[],
                section_keys=[],
                flags=[],
                msgctxt=msgctxt,
            )
            by_key[key] = rec
            order.append(key)
        rec.locations.append((rst_rel, line))
        rec.html_pages.append(html_page)
        rec.section_keys.append(anchor)

    out: list[SearchableRecord] = []
    for key in order:
        rec = by_key[key]
        seen: set[tuple] = set()
        locs: list[tuple[str, int]] = []
        pages: list[str] = []
        keys: list[str] = []
        for loc, page, anc in zip(rec.locations, rec.html_pages, rec.section_keys):
            dedup_key = (loc, page, anc)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            locs.append(loc)
            pages.append(page)
            keys.append(anc)
        rec.locations = locs
        rec.html_pages = pages
        rec.section_keys = keys
        out.append(rec)
    return out


# ---------------------------------------------------------------------------
# Sphinx wiring
# ---------------------------------------------------------------------------

def _is_source_language(app) -> bool:
    """True when this build is the source language (English)."""
    lang = app.config.language
    return lang in (None, "", DEFAULT_LANGUAGE)


def _records_store(env) -> dict:
    store = getattr(env, _ENV_ATTR, None)
    if store is None:
        store = {}
        setattr(env, _ENV_ATTR, store)
    return store


def _rel_source_factory(app):
    """Return a callable mapping an abs source path → repo-relative RST path.

    Repo-relative means ``manual/<...>.rst`` — matching the PO/parser format
    (which strips the ``../../`` prefix locale PO files carry).
    """
    root = Path(app.srcdir).parent  # srcdir == manual/ → parent == repo root
    src_name = Path(app.srcdir).name  # "manual"

    def rel_source(source: str | None, docname: str) -> str:
        if source:
            try:
                return Path(os.path.relpath(source, root)).as_posix()
            except ValueError:
                pass  # e.g. different drive on Windows
        return f"{src_name}/{docname}{RST_SUFFIX}"

    return rel_source


def on_doctree_read(app, doctree) -> None:
    """READ-phase hook: extract this document's messages onto ``env``."""
    if not _is_source_language(app):
        return
    env = app.env
    docname = env.docname or env.path2doc(doctree.get("source") or "") or ""
    if not docname:
        return
    lang = app.config.language or DEFAULT_LANGUAGE
    occurrences = extract_occurrences(
        doctree, docname, lang, _rel_source_factory(app)
    )
    _records_store(env)[docname] = occurrences


def on_env_purge_doc(app, env, docname) -> None:
    """Drop a document's records before it is re-read (clears stale entries)."""
    store = getattr(env, _ENV_ATTR, None)
    if store is not None:
        store.pop(docname, None)


def on_env_merge_info(app, env, docnames, other) -> None:
    """Fold per-worker records back into the main env under ``-j auto``."""
    dst = _records_store(env)
    src = getattr(other, _ENV_ATTR, None) or {}
    for dn in docnames:
        if dn in src:
            dst[dn] = src[dn]


def on_build_finished(app, exception) -> None:
    """Write the aggregated index once the build completes (source lang only)."""
    if exception is not None:
        return
    if getattr(app.builder, "format", "") != "html":
        return
    if not _is_source_language(app):
        return
    store = getattr(app.env, _ENV_ATTR, None)
    if not store:
        return
    occurrences = [occ for occs in store.values() for occ in occs]
    records = aggregate(occurrences)
    out_path = Path(app.outdir) / SEARCH_INDEX_FILENAME
    write_index(records, out_path)
    logger.info(
        "[search_index_builder] wrote %d records → %s", len(records), out_path
    )


def setup(app):
    app.connect("doctree-read", on_doctree_read)
    app.connect("env-purge-doc", on_env_purge_doc)
    app.connect("env-merge-info", on_env_merge_info)
    app.connect("build-finished", on_build_finished)
    return {
        "version": "1.0",
        "env_version": 1,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
