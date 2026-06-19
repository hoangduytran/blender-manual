"""Outdated-document detection for generated gettext shard catalogs.

The runtime translation flow writes one `.mo` file per document under
`build/.i18n_shards/locale/<lang>/LC_MESSAGES/`. Sphinx discovers catalog
dependencies by scanning `.po` files, so generated `.mo`-only shards are not
always registered as dependencies across Sphinx versions. This extension closes
that gap by marking a document outdated when its generated shard is newer than
the last time Sphinx read that document.
"""

from __future__ import annotations

import os
from pathlib import Path

from sphinx.util import logging

try:
    from sphinx.util.i18n import docname_to_domain
except ImportError:
    def docname_to_domain(docname, compaction):
        if isinstance(compaction, str):
            return compaction
        if compaction:
            return docname.partition("/")[0]
        return docname

try:
    from sphinx.util.osutil import _last_modified_time
except ImportError:
    def _last_modified_time(source):
        return int(os.path.getmtime(source) * 1_000_000)


logger = logging.getLogger(__name__)


def _locale_roots(app):
    """Yield absolute locale roots from Sphinx's `locale_dirs` setting."""
    for locale_dir in app.config.locale_dirs:
        root = Path(locale_dir)
        if not root.is_absolute():
            root = Path(app.srcdir) / root
        yield root


def _mo_paths_for_doc(app, docname):
    """Yield possible generated `.mo` catalog paths for `docname`."""
    language = app.config.language
    if not language:
        return
    domain = docname_to_domain(docname, app.config.gettext_compact)
    for locale_root in _locale_roots(app):
        yield locale_root / language / "LC_MESSAGES" / (domain + ".mo")


def _env_get_outdated(app, env, added, changed, removed):
    """Return docs whose generated shard `.mo` is newer than the doctree."""
    if not getattr(app.builder, "use_message_catalog", True):
        return []
    if not app.config.language or app.config.language == "en":
        return []

    already_outdated = set(added) | set(changed) | set(removed)
    outdated = []
    for docname in sorted(env.found_docs - already_outdated):
        last_read = env.all_docs.get(docname)
        if last_read is None:
            continue
        for mo_path in _mo_paths_for_doc(app, docname):
            if not mo_path.is_file():
                continue
            if _last_modified_time(mo_path) > last_read:
                outdated.append(docname)
                break

    if outdated:
        logger.info(
            "i18n_shards: %d document(s) outdated by generated gettext shards",
            len(outdated),
        )
    return outdated


def setup(app):
    app.connect("env-get-outdated", _env_get_outdated)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
