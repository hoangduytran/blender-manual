"""Sphinx extension: repeatable-record inventory + English-hint pills.

The translated-language counterpart of ``search_index_builder``.  On a
translated HTML build it:

1. **Extracts** allowlisted translatable nodes as :class:`RepeatableRecord`
   values at ``doctree-read`` (read phase), so records persist in
   ``environment.pickle`` and survive incremental rebuilds for free.
2. **Renders** the terminal English reading-hint ``<translation> [<English>]``
   as a ``.i18n-en-hint`` pill at ``doctree-resolved`` (a stateless per-document
   DOM mutation).
3. **Writes** ``build/<lang>/repeatable.{pkl.gz,po}`` atomically at
   ``build-finished`` from the merged record snapshot.

It is a no-op for the English/source build and for non-HTML builders.  Why the
read/write split (and why ``rawsource`` still yields the source msgid on a
translated build) is documented in
``tests/20260622_141959_repeatable-record-sphinx-extension-plan.md``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from docutils import nodes
from sphinx.util import logging
from sphinx.util.nodes import extract_messages
from sphinx_intl.catalog import dump_po

# tools/ is on sys.path during a Sphinx build via conf.py; add it defensively so
# the shared constants import cleanly when loaded outside that bootstrap.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_TOOLS = _REPO_ROOT / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from _doctree_extract import (  # noqa: E402
    is_html_builder,
    is_translated_language,
    make_rel_source,
    write_gzip_pickle,
)
from repeatable_extract import (  # noqa: E402
    ExtractionContext,
    build_catalog,
    build_envelope,
    extract_repeatable_records,
    find_terminal_hint,
    group_records_by_doc,
    is_repeatable_tag,
    normalized,
)

from common.constants import (  # type: ignore[import-not-found]  # noqa: E402
    CONF_REPEATABLE_PICKLE_FILENAME,
    CONF_REPEATABLE_PO_FILENAME,
    HINT_CLOSE_BRACKET,
    HINT_OPEN_BRACKET,
    HTML_SUFFIX,
    PILL_CSS_CLASS,
    PO_WIDTH_UNWRAPPED,
    REPEATABLE_PICKLE_FILENAME,
    REPEATABLE_PO_FILENAME,
    TEMP_SUFFIX,
)

logger = logging.getLogger(__name__)

# Attribute under which per-document records hang off the Sphinx env (so they
# are pickled with environment.pickle across incremental rebuilds).
_ENV_ATTR = "repeatable_records"

# docutils flag set by the i18n transform on a translated node.
_TRANSLATED_FLAG = "translated"

# Config-value scope: "env" so a filename change triggers a full rebuild.
_CONFIG_REBUILD_SCOPE = "env"


# ---------------------------------------------------------------------------
# Custom inline node: the English reading-hint pill
# ---------------------------------------------------------------------------

class i18n_en_hint(nodes.inline):
    """Inline node rendered as ``<span class="i18n-en-hint">English</span>``.

    Carries only a single :class:`docutils.nodes.Text` child; the HTML writer
    escapes it, so no raw markup is ever emitted.
    """


def visit_i18n_en_hint_html(self, node: i18n_en_hint) -> None:
    """HTML visitor: open the pill span with the canonical class."""
    self.body.append(self.starttag(node, "span", "", CLASS=PILL_CSS_CLASS))


def depart_i18n_en_hint_html(self, node: i18n_en_hint) -> None:
    """HTML visitor: close the pill span."""
    self.body.append("</span>")


# ---------------------------------------------------------------------------
# Pill rendering (doctree-resolved, write phase)
# ---------------------------------------------------------------------------

def split_leaf_hint(leaf_text: str, msgid: str) -> "tuple[str, str, str] | None":
    """Split a single Text leaf ``"<prefix>[<English>]<trailing-ws>"``.

    Returns ``(prefix, english, trailing)`` when the leaf ends (ignoring
    trailing whitespace) with exactly one ``[<English>]`` equal to *msgid*;
    otherwise ``None`` (the hint does not live wholly in this leaf).
    """
    stripped = leaf_text.rstrip()
    trailing = leaf_text[len(stripped):]
    has_single_pair = (
        stripped.endswith(HINT_CLOSE_BRACKET)
        and stripped.count(HINT_OPEN_BRACKET) == 1
        and stripped.count(HINT_CLOSE_BRACKET) == 1
    )
    if not has_single_pair:
        return None
    open_index = stripped.index(HINT_OPEN_BRACKET)
    english = stripped[open_index + 1:-1]
    if not english or normalized(english) != normalized(msgid):
        return None
    return leaf_text[:open_index], english, trailing


def _replace_leaf_with_pill(
    leaf: nodes.Text, prefix: str, english: str, trailing: str
) -> None:
    """Replace *leaf* with ``Text(prefix) + pill(english) [+ Text(trailing)]``."""
    pill = i18n_en_hint()
    pill += nodes.Text(english)
    replacement: list[nodes.Node] = []
    if prefix:
        replacement.append(nodes.Text(prefix))
    replacement.append(pill)
    if trailing:
        replacement.append(nodes.Text(trailing))
    leaf.parent.replace(leaf, replacement)


def wrap_terminal_hint(node: nodes.Element, msgid: str) -> bool:
    """Wrap the terminal English hint of *node* in a pill, in place.

    Validates the whole-node terminal shape, then mutates only the last Text
    leaf — the Vietnamese prefix and the parent node are left byte-for-byte
    unchanged.  Returns True when a pill was inserted.
    """
    is_translated = node.get(_TRANSLATED_FLAG) is True
    if not is_translated:
        return False
    if find_terminal_hint(node.astext(), msgid) is None:
        return False

    text_leaves = list(node.findall(nodes.Text))
    if not text_leaves:
        return False
    last_leaf = text_leaves[-1]
    split = split_leaf_hint(last_leaf.astext(), msgid)
    if split is None:
        logger.debug(
            "[repeatable_builder] hint for %r spans multiple text leaves; "
            "recorded but not pilled", msgid,
        )
        return False
    _replace_leaf_with_pill(last_leaf, *split)
    return True


def wrap_hints_in_doctree(doctree: nodes.document) -> None:
    """Pill every allowlisted node carrying a valid terminal English hint."""
    for node, msgid in extract_messages(doctree):
        if is_repeatable_tag(node.tagname):
            wrap_terminal_hint(node, msgid)


# ---------------------------------------------------------------------------
# Build gating and per-document context
# ---------------------------------------------------------------------------

def _is_repeatable_build(app) -> bool:
    """True only for a translated-language HTML build."""
    return is_html_builder(app) and is_translated_language(app.config.language)


def _build_context(app, docname: str) -> ExtractionContext:
    """Assemble the per-document extraction inputs."""
    language = app.config.language
    html_page = f"/{language}/{docname}{HTML_SUFFIX}"
    return ExtractionContext(
        docname=docname,
        html_page=html_page,
        rel_source=make_rel_source(Path(app.srcdir)),
    )


def _records_store(env) -> dict:
    """Return (creating if needed) the per-document record store on *env*."""
    store = getattr(env, _ENV_ATTR, None)
    if store is None:
        store = {}
        setattr(env, _ENV_ATTR, store)
    return store


# ---------------------------------------------------------------------------
# Lifecycle handlers
# ---------------------------------------------------------------------------

def on_doctree_read(app, doctree) -> None:
    """READ phase: extract this document's records onto the env."""
    if not _is_repeatable_build(app):
        return
    env = app.env
    docname = env.docname or env.path2doc(doctree.get("source") or "") or ""
    if not docname:
        return
    context = _build_context(app, docname)
    _records_store(env)[docname] = extract_repeatable_records(doctree, context)


def on_env_purge_doc(app, env, docname) -> None:
    """Drop a document's records before it is re-read (clears stale entries)."""
    store = getattr(env, _ENV_ATTR, None)
    if store is not None:
        store.pop(docname, None)


def on_env_merge_info(app, env, docnames, other) -> None:
    """Fold per-worker records back into the main env under ``-j auto``."""
    destination = _records_store(env)
    source = getattr(other, _ENV_ATTR, None) or {}
    for docname in docnames:
        if docname in source:
            destination[docname] = source[docname]


def on_doctree_resolved(app, doctree, docname) -> None:
    """WRITE phase: render terminal English hints as pills (stateless)."""
    if not _is_repeatable_build(app):
        return
    wrap_hints_in_doctree(doctree)


def on_build_finished(app, exception) -> None:
    """Flush the merged snapshot to pickle + PO once the build succeeds."""
    if exception is not None:
        return
    if not _is_repeatable_build(app):
        return
    env = app.env
    store = getattr(env, _ENV_ATTR, None)
    if not store:
        return
    _prune_absent_docs(store, env.found_docs)
    all_records = [record for records in store.values() for record in records]
    records_by_doc = group_records_by_doc(all_records)
    _write_artifacts(app, records_by_doc)


def _prune_absent_docs(store: dict, found_docs) -> None:
    """Remove records for docs no longer present in the project."""
    for docname in [name for name in store if name not in found_docs]:
        del store[docname]


# ---------------------------------------------------------------------------
# Artifact writing (atomic)
# ---------------------------------------------------------------------------

def _write_artifacts(app, records_by_doc: dict) -> None:
    """Write the gzip-pickle inventory and the PO catalogue atomically."""
    language = app.config.language
    outdir = Path(app.outdir)
    pickle_path = outdir / app.config.repeatable_pickle_filename
    po_path = outdir / app.config.repeatable_po_filename

    envelope = build_envelope(records_by_doc, language)
    catalog, conflicts = build_catalog(
        records_by_doc, language, app.config.project, app.config.version
    )
    for conflict in conflicts:
        logger.warning(
            "[repeatable_builder] msgid %r has conflicting translations %r; "
            "kept the first", conflict.msgid, conflict.values,
        )

    write_gzip_pickle(envelope, pickle_path)
    _write_catalog_atomic(catalog, po_path)

    total_records = sum(len(records) for records in records_by_doc.values())
    logger.info(
        "[repeatable_builder] wrote %d records across %d docs → %s, %s",
        total_records, len(records_by_doc), pickle_path.name, po_path.name,
    )


def _write_catalog_atomic(catalog, po_path: Path) -> None:
    """Write *catalog* to *po_path* via a temp sibling + os.replace."""
    po_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = po_path.parent / (po_path.name + TEMP_SUFFIX)
    try:
        dump_po(str(tmp_path), catalog, width=PO_WIDTH_UNWRAPPED, sort_output=True)
        os.replace(tmp_path, po_path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


# ---------------------------------------------------------------------------
# Sphinx registration
# ---------------------------------------------------------------------------

def setup(app):
    """Register config values, the pill node, and the lifecycle handlers."""
    app.add_config_value(
        CONF_REPEATABLE_PICKLE_FILENAME, REPEATABLE_PICKLE_FILENAME,
        _CONFIG_REBUILD_SCOPE, [str],
    )
    app.add_config_value(
        CONF_REPEATABLE_PO_FILENAME, REPEATABLE_PO_FILENAME,
        _CONFIG_REBUILD_SCOPE, [str],
    )
    app.add_node(
        i18n_en_hint, html=(visit_i18n_en_hint_html, depart_i18n_en_hint_html)
    )
    app.connect("doctree-read", on_doctree_read)
    app.connect("env-purge-doc", on_env_purge_doc)
    app.connect("env-merge-info", on_env_merge_info)
    app.connect("doctree-resolved", on_doctree_resolved)
    app.connect("build-finished", on_build_finished)
    return {
        "version": "1.0",
        "env_version": 1,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
