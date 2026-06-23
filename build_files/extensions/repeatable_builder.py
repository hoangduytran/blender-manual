"""Sphinx extension: repeatable-record inventory + English-hint pills.

The translated-language counterpart of ``search_index_builder``.  On a
translated HTML build it:

1. **Extracts** allowlisted translatable nodes as :class:`RepeatableRecord`
   values at ``doctree-read`` (read phase), so records persist in
   ``environment.pickle`` and survive incremental rebuilds for free.
2. **Renders** validated terminal reading hints as fixed HTML pills: direct
   nodes at ``doctree-resolved`` and generated navigation at
   ``html-page-context``.
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
    TerminalHint,
    build_catalog,
    build_envelope,
    classify_terminal_hint,
    collect_hint_mismatches,
    explicit_reference_label,
    extract_repeatable_records,
    format_mismatch_report,
    group_records_by_doc,
    is_repeatable_message,
    split_terminal_group,
)
from repeatable_html import (  # noqa: E402
    build_navigation_hint_index,
    rewrite_body_navigation,
    rewrite_navigation_fragment,
)

from common.constants import (  # type: ignore[import-not-found]  # noqa: E402
    CONF_REPEATABLE_MISMATCH_FILENAME,
    CONF_REPEATABLE_PICKLE_FILENAME,
    CONF_REPEATABLE_PO_FILENAME,
    FILE_ENCODING,
    HintSide,
    HTML_SUFFIX,
    PILL_EN_CSS_CLASS,
    PILL_NATIVE_CSS_CLASS,
    PO_WIDTH_UNWRAPPED,
    REPEATABLE_MISMATCH_FILENAME,
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

    Used when the bracketed reading is English (body content). Carries only a
    single :class:`docutils.nodes.Text` child; the HTML writer escapes it, so
    no raw markup is ever emitted.
    """


class i18n_native_hint(nodes.inline):
    """Inline node rendered as ``<span class="i18n-native-hint">translation</span>``.

    Used when the bracketed reading is the native translation (glossary terms,
    which keep the English first). Language-neutral: the bracket holds whatever
    the target language is (vi, ru, ...). Same escaped-text guarantee as
    :class:`i18n_en_hint`.
    """


def visit_i18n_en_hint_html(self, node: i18n_en_hint) -> None:
    """HTML visitor: open the English pill span."""
    self.body.append(_pill_starttag(self, node, PILL_EN_CSS_CLASS))


def visit_i18n_native_hint_html(self, node: i18n_native_hint) -> None:
    """HTML visitor: open the native-translation pill span."""
    self.body.append(_pill_starttag(self, node, PILL_NATIVE_CSS_CLASS))


def _pill_starttag(self, node: nodes.Element, css_class: str) -> str:
    """Return a pill start tag carrying repeatable provenance."""
    attributes = {
        "CLASS": css_class,
        "data-repeatable": "true",
        "data-msgid": node["msgid"],
    }
    return self.starttag(node, "span", "", **attributes)


def depart_pill_html(self, node: nodes.Element) -> None:
    """HTML visitor: close a pill span (shared by both pill node types)."""
    self.body.append("</span>")


# Map the classified hint side to the pill node type that renders it.
_PILL_NODE_BY_SIDE = {
    HintSide.ENGLISH_BRACKET: i18n_en_hint,  # bracket is English (body)
    HintSide.ENGLISH_LEAD: i18n_native_hint,  # bracket is the translation (glossary)
}


# ---------------------------------------------------------------------------
# Pill rendering (doctree-resolved, write phase)
# ---------------------------------------------------------------------------


def split_terminal_leaf(leaf_text: str) -> "tuple[str, str, str] | None":
    """Split a single Text leaf ``"<lead><open><bracket><close><trailing-ws>"``.

    Returns ``(lead, bracket, trailing)`` when the leaf ends (ignoring trailing
    whitespace) with a non-empty terminal delimiter group (``[]`` or ``()``);
    otherwise ``None`` (the hint does not live wholly in this leaf).  Equality to
    the msgid is already decided at the whole-node level by
    :func:`classify_terminal_hint`; this only locates the group to split.
    """
    split = split_terminal_group(leaf_text)
    if split is None:
        return None
    lead, bracket = split
    trailing = leaf_text[len(leaf_text.rstrip()) :]
    return lead, bracket, trailing


def _replace_leaf_with_pill(
    leaf: nodes.Text, lead: str, pill: nodes.Element, trailing: str
) -> None:
    """Replace *leaf* with ``Text(lead) + pill [+ Text(trailing)]``."""
    replacement: list[nodes.Node] = []
    if lead:
        replacement.append(nodes.Text(lead))
    replacement.append(pill)
    if trailing:
        replacement.append(nodes.Text(trailing))
    leaf.parent.replace(leaf, replacement)


def _make_pill(side: HintSide, text: str, msgid: str) -> nodes.Element:
    """Build the pill node for *side* containing *text*."""
    pill = _PILL_NODE_BY_SIDE[side]()
    pill["msgid"] = msgid
    pill += nodes.Text(text)
    return pill


def _classify_repeated_text(
    node: nodes.Element, msgid: str
) -> "tuple[TerminalHint, str] | None":
    """Classify repeated text using the catalog msgid or visible link label."""
    classified = classify_terminal_hint(node.astext(), msgid)
    if classified is not None:
        return classified, msgid
    has_reference = next(node.findall(nodes.reference), None) is not None
    visible_msgid = explicit_reference_label(msgid) if has_reference else None
    if visible_msgid is None:
        return None
    classified = classify_terminal_hint(node.astext(), visible_msgid)
    return (classified, visible_msgid) if classified is not None else None


def wrap_terminal_hint(node: nodes.Element, msgid: str) -> bool:
    """Wrap the terminal reading-hint of *node* in a pill, in place.

    Classifies the whole-node terminal shape (deciding the pill class from which
    side carries the msgid), then mutates only the last Text leaf — the lead
    text and the parent node are left byte-for-byte unchanged.  Returns True
    when a pill was inserted.
    """
    is_translated = node.get(_TRANSLATED_FLAG) is True
    if not is_translated or not is_repeatable_message(node, msgid):
        return False
    repeated_text = _classify_repeated_text(node, msgid)
    if repeated_text is None:
        return False
    classified, visible_msgid = repeated_text

    text_leaves = list(node.findall(nodes.Text))
    if not text_leaves:
        return False
    last_leaf = text_leaves[-1]
    split = split_terminal_leaf(last_leaf.astext())
    if split is None:
        logger.debug(
            "[repeatable_builder] hint for %r spans multiple text leaves; "
            "recorded but not pilled",
            msgid,
        )
        return False
    lead, bracket, trailing = split
    pill = _make_pill(classified.side, bracket, visible_msgid)
    _replace_leaf_with_pill(last_leaf, lead, pill, trailing)
    return True


def wrap_hints_in_doctree(doctree: nodes.document) -> None:
    """Pill every allowlisted node carrying a valid terminal English hint."""
    for node, msgid in extract_messages(doctree):
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


def on_builder_inited(app) -> None:
    """Initialize the per-build navigation-hint index cache."""
    app.repeatable_navigation_hint_index = None


def _navigation_hint_index(app) -> dict[str, tuple[str, ...]]:
    """Return the validated repeatable navigation index for this build."""
    if app.repeatable_navigation_hint_index is None:
        store = getattr(app.env, _ENV_ATTR, None) or {}
        records = (record for doc_records in store.values() for record in doc_records)
        app.repeatable_navigation_hint_index = build_navigation_hint_index(records)
    return app.repeatable_navigation_hint_index


def _rewrite_relation_titles(context: dict, index: dict[str, tuple[str, ...]]) -> None:
    """Write fixed pill markup into previous, next, and parent page titles."""
    for relation_name in ("prev", "next"):
        relation = context.get(relation_name)
        if relation and relation.get("title"):
            relation["title"] = rewrite_navigation_fragment(relation["title"], index)
    for relation in context.get("parents") or []:
        relation["title"] = rewrite_navigation_fragment(relation["title"], index)


def on_html_page_context(app, _pagename, _templatename, context, _doctree) -> None:
    """Write validated navigation pills into HTML before template rendering."""
    if not _is_repeatable_build(app):
        return
    index = _navigation_hint_index(app)
    context["body"] = rewrite_body_navigation(context.get("body", ""), index)
    context["toc"] = rewrite_navigation_fragment(context.get("toc", ""), index)
    if "furo_navigation_tree" in context:
        context["furo_navigation_tree"] = rewrite_navigation_fragment(
            context["furo_navigation_tree"], index
        )
    _rewrite_relation_titles(context, index)

    original_toctree = context.get("toctree")
    if callable(original_toctree):

        def render_toctree(*args, **kwargs):
            rendered = original_toctree(*args, **kwargs)
            return rewrite_navigation_fragment(rendered, index)

        context["toctree"] = render_toctree


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
            "kept the first",
            conflict.msgid,
            conflict.values,
        )

    write_gzip_pickle(envelope, pickle_path)
    _write_catalog_atomic(catalog, po_path)
    _report_hint_mismatches(app, records_by_doc)

    total_records = sum(len(records) for records in records_by_doc.values())
    logger.info(
        "[repeatable_builder] wrote %d records across %d docs → %s, %s",
        total_records,
        len(records_by_doc),
        pickle_path.name,
        po_path.name,
    )


def _report_hint_mismatches(app, records_by_doc: dict) -> None:
    """Warn per misaligned reading-hint and write the collected text report.

    A misaligned hint is one pilled "as written" via the near-miss path: the
    bracket text is close to the English source but not an exact match (usually a
    translator typo). Each is logged so it shows in the build, and all are
    written to the report file so the translator has a worklist. When there are
    none, any stale report is removed so its absence means "all clean".
    """
    report_path = Path(app.outdir) / app.config.repeatable_mismatch_filename
    pairs = collect_hint_mismatches(records_by_doc)
    if not pairs:
        report_path.unlink(missing_ok=True)
        return

    for record, mismatch in pairs:
        logger.warning(
            "[repeatable_builder] reading-hint mismatch: wrote %r but the English "
            "source is %r; pilled as-written — please fix the bracket",
            mismatch.observed,
            mismatch.msgid,
            location=(record.docname, record.source_line),
        )

    report = format_mismatch_report(pairs, app.config.language)
    _write_text_atomic(report, report_path)
    logger.info(
        "[repeatable_builder] %d misaligned reading-hint(s) → %s",
        len(pairs),
        report_path.name,
    )


def _write_text_atomic(text: str, path: Path) -> None:
    """Write *text* to *path* via a temp sibling + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.parent / (path.name + TEMP_SUFFIX)
    try:
        tmp_path.write_text(text, encoding=FILE_ENCODING)
        os.replace(tmp_path, path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


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
        CONF_REPEATABLE_PICKLE_FILENAME,
        REPEATABLE_PICKLE_FILENAME,
        _CONFIG_REBUILD_SCOPE,
        [str],
    )
    app.add_config_value(
        CONF_REPEATABLE_PO_FILENAME,
        REPEATABLE_PO_FILENAME,
        _CONFIG_REBUILD_SCOPE,
        [str],
    )
    app.add_config_value(
        CONF_REPEATABLE_MISMATCH_FILENAME,
        REPEATABLE_MISMATCH_FILENAME,
        _CONFIG_REBUILD_SCOPE,
        [str],
    )
    app.add_node(i18n_en_hint, html=(visit_i18n_en_hint_html, depart_pill_html))
    app.add_node(i18n_native_hint, html=(visit_i18n_native_hint_html, depart_pill_html))
    app.connect("builder-inited", on_builder_inited)
    app.connect("doctree-read", on_doctree_read)
    app.connect("env-purge-doc", on_env_purge_doc)
    app.connect("env-merge-info", on_env_merge_info)
    app.connect("doctree-resolved", on_doctree_resolved)
    app.connect("html-page-context", on_html_page_context, priority=700)
    app.connect("build-finished", on_build_finished)
    return {
        "version": "1.2",
        "env_version": 2,  # bumped: RepeatableRecord gained is_glossary
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
