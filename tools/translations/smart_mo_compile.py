#!/usr/bin/env python3
# Apache License, Version 2.0
"""Compile one large translation catalog into incremental per-document shards.

Reader orientation
------------------
Blender's translators maintain one GNU gettext PO file per language, for
example::

    locale/vi/LC_MESSAGES/blender_manual.po

The PO is human-editable source data. Sphinx renders translated HTML from
compiled binary MO catalogs. This module is the bridge between those forms:
it keeps the monolithic PO as the translator-facing source of truth, but
publishes one generated MO file per Sphinx document for runtime builds.

The surrounding build invokes this module before Sphinx. A normal build runs
it once; ``sphinx-autobuild`` runs it as a pre-build hook whenever a watched
RST or PO changes. English is the source language and is therefore a no-op.

Evidence used by this explanation
---------------------------------
The legacy behavior below is derived from the examined baseline checkout, not
from benchmark estimates or an assumed Sphinx implementation:

* its ``requirements.txt`` pins Sphinx 9.1.0 and sphinx-autobuild 2025.8.25;
* its ``Makefile`` defines ``livehtml`` as one direct sphinx-autobuild command
  with no ``--watch`` or ``--pre-build`` arguments;
* its ``manual/conf.py`` sets ``locale_dirs = ["../locale/"]`` and
  ``gettext_compact = "blender_manual"`` and does not override
  ``gettext_auto_build``;
* Sphinx 9.1.0 supplies the default ``gettext_auto_build = True`` and the
  relevant behavior in ``Builder.compile_update_catalogs()``,
  ``Environment.find_files()``, ``_has_doc_changed()``, and
  ``CatalogInfo.is_outdated()/write_mo()``; and
* sphinx-autobuild 2025.8.25 constructs its watched set as the source
  directory plus explicit ``--watch`` directories.

The replacement behavior is derived from this module, the current ``Makefile``
and ``manual/conf.py``, and ``build_files/extensions/i18n_shards.py``. Function
names are included below so each claim has a direct review route.

Shortcomings of the legacy Sphinx setup
---------------------------------------
The baseline manual build used these settings and no separate compiler::

    locale_dirs = ["../locale/"]
    gettext_compact = "blender_manual"
    # gettext_auto_build retained Sphinx's default value: True

The examined Vietnamese PO in that checkout is 15,595,446 bytes. The following
limitations follow directly from the configuration and pinned dependency code.

1. PO edits are invisible to the live watcher.

   The baseline passes ``./manual`` as sphinx-autobuild's source directory and
   supplies no ``--watch`` argument. sphinx-autobuild 2025.8.25 builds
   ``watch_dirs`` from that source directory plus explicit ``--watch`` values;
   therefore ``locale/vi/LC_MESSAGES/blender_manual.po`` is not in the watched
   set and saving it is not itself a watcher event.

2. One catalog change invalidates the whole manual.

   ``gettext_compact = "blender_manual"`` maps every document to the same
   ``blender_manual.mo`` domain. Sphinx 9.1.0
   ``Environment.find_files()`` iterates over every found document, computes
   that document's domain, and calls ``note_dependency()`` with the matching MO.
   Its outdated-file check then compares every recorded dependency mtime with
   the document's last-read time. With one shared domain, the same MO path is
   recorded and checked for every document.

3. Sphinx's automatic compiler understands timestamps, not meaning.

   Sphinx 9.1.0 ``CatalogInfo.is_outdated()`` returns true when the MO is absent
   or its mtime is older than the PO mtime. It performs no byte or semantic
   comparison. Consequently a newer PO timestamp is sufficient to select the
   catalog for ``compile_update_catalogs()``; whether a ``msgstr`` changed is
   not part of that decision.

4. Selected updates read and write the monolithic catalog.

   ``CatalogInfo.write_mo()`` opens and parses the selected PO, then opens
   ``blender_manual.mo`` and serializes the resulting catalog. Because the
   configured domain is global, that code has no per-document catalog files to
   select or preserve independently.

5. The pinned writer has neither a temporary-file commit nor a locale lock.

   ``CatalogInfo.mo_path`` places the MO beside its PO in
   ``locale/<lang>/LC_MESSAGES``. ``CatalogInfo.write_mo()`` opens that final
   path directly with ``open(..., "wb")`` and writes to it. The Sphinx method
   contains no temporary path, ``os.replace()``, or per-language file lock.

Design used here
----------------
The replacement keeps translation authoring and runtime delivery separate.
The canonical monolithic PO remains the input used by the repository's
``make gettext`` and ``tools/translations/update_po.py`` workflows. Runtime
catalogs are generated build products under::

    build/.i18n_shards/locale/<lang>/LC_MESSAGES/<document-slug>.mo

The implementation addresses the legacy problems as follows.

1. Run before Sphinx and explicitly watch translation input.

   The current Make targets call this module before one-shot builds and pass it
   through ``sphinx-autobuild --pre-build`` for live builds. Those live recipes
   also pass ``--watch locale/<lang>/LC_MESSAGES`` and explicit ``--ignore``
   globs for MO, hash, lock, shard-root, and cache-root outputs. These command
   arguments place the PO in the watched set and generated outputs in the
   ignored set.

2. Give each document its own gettext domain.

   Runtime ``conf.py`` sets ``gettext_compact = False``. Sphinx then maps a
   document such as ``modeling/meshes/introduction`` to a catalog with the same
   slug. This module resolves each PO ``#:`` source location back to an RST,
   converts it to that slug, and copies the effective message into the matching
   sub-catalog. ``i18n_shards._env_get_outdated()`` checks the shard path
   derived from each found docname, rather than a shared global MO path.

   Every RST receives a shard, including a header-only shard when the page has
   no translated messages; this is implemented by
   ``_add_empty_shards_for_untranslated()``. Effective messages with no safe,
   resolvable RST location are kept in ``__orphan__.mo``. The extension only
   asks for shard paths derived from ``env.found_docs``, so the orphan shard is
   not assigned as a dependency of every page.

3. Make this module the only runtime MO writer.

   Runtime ``conf.py`` sets ``gettext_auto_build = False`` and searches the
   generated shard root before the canonical locale tree. In Sphinx 9.1.0,
   ``Builder.compile_catalogs()`` returns immediately when that setting is
   false. A stale legacy ``blender_manual.mo`` is removed by
   ``_delete_stale_global_mo()`` after shard emission.

4. Avoid work progressively, from cheap metadata checks to targeted writes.

   The per-language cache is evaluated in increasing cost order:

   * Tier 1 compares PO ``mtime_ns`` and size and verifies that the shard tree
     still exists. A hit performs no PO content read or PO parse; the cache
     file itself has already been read by ``_read_cache()``.
   * Tier 2 computes a raw SHA-256. A hit handles a touched but byte-identical
     PO by refreshing only the cached stat fields.
   * Tier 3 parses the PO and compares two BLAKE2 hashes. The semantic hash
     contains only effective ``msgid``/``msgstr`` pairs; headers, comments,
     empty translations, and fuzzy translations do not masquerade as runtime
     content. The layout hash separately records ``msgid``-to-document routing,
     so moving a message between RST files cannot be mistaken for no change.
   * Tier 4 regenerates catalogs after a cache miss, or unconditionally when
     ``--force-rebuild`` requests bypassing tiers 1 through 3.

   A valid cache also stores the previous effective translation map and both
   ``msgid -> documents`` and ``document -> msgids`` indexes. When
   ``_partial_cache_inputs()`` validates those structures and the layout hash
   is unchanged, ``_shard_tier4_partial_run()`` diffs changed msgids, combines
   their old and current document edges, and rewrites or deletes only those
   document shards plus the orphan shard when necessary. A failed validation,
   changed layout hash, or missing shard directory returns ``False`` to
   ``_shard_tier4_run()``, which performs the full split.

5. Preserve mtimes when output bytes are unchanged.

   Each sub-catalog is serialized in memory and compared with its existing MO.
   ``_write_shard_if_changed()`` returns without opening the destination when
   the byte strings match. The shard mtime therefore remains unchanged for
   byte-identical serialized output and advances when atomic replacement writes
   different bytes.

6. Detect generated-MO changes without touching RSTs in live mode.

   Sphinx 9.1.0 ``Environment.find_files()`` obtains catalog paths from
   ``CatalogRepository.catalogs``; that repository enumerates PO files. This
   runtime shard tree contains generated MO files only, so the current
   ``i18n_shards`` extension performs the missing check explicitly: it compares
   each found document's shard mtime with ``env.all_docs[docname]`` and returns
   only documents whose shard is newer.

   Live targets pass ``--no-touch-rst`` because the PO watcher already starts
   Sphinx and the extension supplies per-shard invalidation. The watched source
   directory includes those RST files, so changing an RST mtime is itself an
   additional watcher event. One-shot recipes do not pass ``--no-touch-rst``;
   their fallback touches only RSTs selected by changed msgids or document
   shard hashes. A normalized PO snapshot and cached document hashes provide
   the baselines for that fallback.

7. Publish a consistent per-language state.

   A POSIX advisory lock serializes concurrent compiler runs for one language.
   ``_atomic_write_bytes()`` uses ``mkstemp`` followed by ``os.replace()`` for
   MO shards and cache data; ``_write_po_snapshot()`` uses the same temporary
   file and replace pattern. In both full and partial paths, the calls are
   ordered as shard updates, legacy-MO removal, snapshot write, then cache
   write. On a run where ``_read_cache()`` returns ``None``, stale doctree state
   and obsolete sidecars are removed before cache-tier evaluation.

Runtime route for reviewers
---------------------------
The orchestration path is deliberately linear::

    main
      -> _parse_args                  create one ConfigRecord
      -> _main_shard                  validate PO, create dirs, acquire lock
      -> _shard_locked_body           evaluate cache tiers 1 through 3
      -> _shard_tier4_run             select partial or full regeneration
         -> _shard_tier4_partial_run  update only affected indexes and shards
         -> _catalog_to_shards        full msgid/document partition fallback
         -> _emit_shards              write changed bytes, delete stale shards

Transient catalogs, maps, and hashes remain local to the operation that owns
them. Parsed options and all derived paths live in the same ``ConfigRecord``
instance passed through the pipeline.

Persistent artifacts
--------------------
With the current Make arguments and CLI defaults, generated state lives under
the build directory alongside the Sphinx doctrees::

    <cache_dir>/<lang>.pkl
        Stat fields, raw/semantic/layout hashes, translation baseline,
        msgid/document indexes, and per-document shard hashes.

    <cache_dir>/<lang>.po.snapshot
        Normalized previous PO used by the RST-touch fallback.

    <cache_dir>/<lang>.lock
        Per-language advisory lock file.

    <shard_root>/<lang>/LC_MESSAGES/<document-slug>.mo
        Generated runtime catalogs consumed by Sphinx.

The monolithic PO is the translator input and shard MOs are generated runtime
output. In both regeneration paths, ``_write_cache()`` is called after shard
and snapshot writes; its atomic replacement leaves either the previous cache
bytes or the newly assembled payload, rather than an in-place partial pickle.
"""

# `from __future__ import annotations` keeps type hints (e.g. `int | None`) as
# strings at runtime, so the file imports cleanly on Python 3.9 as well as 3.10+.
from __future__ import annotations

import argparse   # CLI argument parsing (--language, --srcdir, etc.).
import enum        # ConfPattern enum groups the conf.py-scraping regexes.
import fcntl      # POSIX advisory file lock (LOCK_EX) -- serialises concurrent runs.
import hashlib    # blake2b for the semantic hash; sha256 for the raw-bytes tier.
import io         # BytesIO for in-memory shard composition (byte-compare before write).
import os         # os.utime (mtime stamping), os.replace (atomic rename), os.fdopen.
import pickle     # tiered-cache file format (mtime + hashes + old_map).
import re         # conf.py scalar extraction (see ConfPattern).
import sys        # sys.stderr / sys.exit / __name__ entry point.
import tempfile   # mkstemp / NamedTemporaryFile for atomic writes to .mo, .hash, .cache.
import time       # tier-4 wall-time logging.
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath  # PurePosixPath for shard slug normalisation.

# Cache schema version. v3 adds `layout_hash`, because `#:` locations are
# runtime-significant in shard mode: they decide which document owns a msgid.
# v2 caches are still accepted and upgraded lazily; rejecting them would force
# a full Sphinx environment reread on the next live build.
_CACHE_VERSION = 3
_CACHE_COMPAT_VERSIONS = {_CACHE_VERSION, 2}

# Special slug for msgids with no resolvable `#:` location -- their shard is
# loaded by Sphinx but referenced by no doc, so its mtime invalidates nothing.
_ORPHAN_SLUG = "__orphan__"


class CacheKey(str, enum.Enum):
    """Field names of the per-language tier-cache pickle (`<cache_dir>/<lang>.pkl`).

    A str-enum so members double as the dict keys themselves: `cache[CacheKey.VERSION]`
    and `cache.get(CacheKey.VERSION)` need no `.value`, and because
    `CacheKey.VERSION == "version"` (with an identical hash), a pickle written
    with plain-string keys by an older build still validates and reads back
    here unchanged. Grouping the keys also keeps the read, validate, refresh,
    and write paths spelling every field the same way.
    """

    VERSION = "version"            # schema version int; gated by _CACHE_COMPAT_VERSIONS
    PO_MTIME_NS = "po_mtime_ns"    # tier 1: PO st_mtime_ns
    PO_SIZE = "po_size"            # tier 1: PO st_size
    RAW_HASH = "raw_hash"          # tier 2: sha256 of raw PO bytes
    SEMANTIC_HASH = "semantic_hash"  # tier 3: blake2b of effective msgid/msgstr pairs
    LAYOUT_HASH = "layout_hash"    # tier 3: blake2b of msgid -> document routing (v3+)
    OLD_MAP = "old_map"            # effective translation baseline for the next diff
    MSGID_TO_DOCS = "msgid_to_docs"  # index: msgid -> document slugs
    DOC_TO_MSGIDS = "doc_to_msgids"  # index: document slug -> msgids
    DOC_HASHES = "doc_hashes"      # per-document emitted shard hashes

# Named capture group shared by every ConfPattern below. Each regex captures
# the quoted setting value under this name, so the scraper reads
# `match.group(_CONF_VALUE)` instead of a positional `match.group(1)`.
_CONF_VALUE = "value"


class ConfPattern(enum.Enum):
    """Line-regexes that scrape scalar settings out of ``manual/conf.py``.

    These run via plain ``re.search`` (never ``exec``) so Sphinx-specific
    globals such as ``tags`` or ``sphinx.version_info`` are never evaluated.

    Each member's ``.name`` is the :class:`ConfigRecord` field the match
    populates, and each ``.value`` is a regex with a single ``(?P<value>...)``
    group capturing the quoted setting. :meth:`ConfPattern.scan` walks every
    member, so adding a setting is one line here with no scraper changes.
    """

    # blender_version = "5.3"
    blender_version = r'^blender_version\s*=\s*["\'](?P<value>[^"\']+)["\']'
    # gettext_compact = "blender_manual" (appears in the legacy_gettext branch)
    domain = r'gettext_compact\s*=\s*["\'](?P<value>[^"\']+)["\']'
    # source_suffix = [".rst"]  or  {".rst": "restructuredtext"}
    rst_suffix = r'^source_suffix\s*=\s*[\[{]\s*["\'](?P<value>[^"\']+)["\']'
    # html_page_suffix = ".html"
    html_page_suffix = r'^html_page_suffix\s*=\s*["\'](?P<value>[^"\']+)["\']'
    # search_index_filename = "searchindex.pkl.gz"
    search_index_filename = r'^search_index_filename\s*=\s*["\'](?P<value>[^"\']+)["\']'
    # html_builder_name = "html"
    html_builder_name = r'^html_builder_name\s*=\s*["\'](?P<value>[^"\']+)["\']'
    # language = "en" (source/default language)
    default_language = r'^language\s*=\s*["\'](?P<value>[^"\']+)["\']'

    @classmethod
    def scan(cls, text: str) -> dict[str, str]:
        """Return ``{field name: captured value}`` for every member that matches."""
        values: dict[str, str] = {}
        for pattern in cls:
            m = re.search(pattern.value, text, re.MULTILINE)
            if m:
                values[pattern.name] = m.group(_CONF_VALUE)
        return values


@dataclass
class ConfigRecord:
    """Parsed CLI configuration and all paths derived from it.

    The record is created once by :func:`_parse_args` and the same instance is
    passed through the build pipeline. Runtime data such as catalogs, hashes,
    and cache payloads deliberately remain outside this configuration.
    """

    # Locale code compiled by this run; e.g. "vi" ("en" is a no-op).
    language: str

    # Root containing the manual's RST sources; e.g. Path("/repo/manual").
    srcdir: Path

    # Root containing one directory per translation locale; e.g. Path("/repo/locale").
    locale_dir: Path

    # Sphinx doctree state checked during first-run cleanup;
    # e.g. Path("/repo/build/.doctrees/vi").
    doctree_dir: Path

    # Gettext catalog basename without an extension; e.g. "blender_manual".
    domain: str

    # Persistent hashes, indexes, snapshots, and locks;
    # e.g. Path("/repo/build/.translation_cache").
    cache_dir: Path

    # Root receiving generated per-document MO catalogs;
    # e.g. Path("/repo/build/.i18n_shards/locale").
    shard_root: Path

    # Bypass cache tiers 1-3 and execute tier 4; e.g. True for --force-rebuild.
    force_rebuild: bool

    # Avoid touching affected RST mtimes; e.g. True for --no-touch-rst.
    no_touch_rst: bool

    # Enable detailed diagnostic output; e.g. True for --verbose.
    verbose: bool

    # Suppress normal summary output; e.g. True for --quiet.
    quiet: bool

    # --- Optional fields populated by from_project() or left at defaults ---

    # Blender version string read from manual/conf.py; e.g. "5.3".
    blender_version: str = field(default="")

    # Path to manual/conf.py used to populate blender_version and domain;
    # e.g. Path("/repo/manual/conf.py").
    conf_py_path: Path | None = field(default=None)

    # sphinx-build executable; absolute path when the project venv is used,
    # bare "sphinx-build" as a PATH fallback.
    sphinx_build_cmd: str = field(default="sphinx-build")

    # sphinx-build -b argument; e.g. "html".
    sphinx_builder: str = field(default="html")

    # sphinx-build -j argument; e.g. "auto".
    sphinx_jobs: str = field(default="auto")

    # Absolute path to tools/translations/smart_mo_compile.py; None when the
    # script cannot be located (e.g. inside a redistributed package).
    smart_mo_script: Path | None = field(default=None)

    # RST source file extension read from conf.py source_suffix; e.g. ".rst".
    rst_suffix: str = field(default=".rst")

    # HTML output page extension read from conf.py html_page_suffix; e.g. ".html".
    html_page_suffix: str = field(default=".html")

    # Search index pickle filename read from conf.py; e.g. "searchindex.pkl.gz".
    search_index_filename: str = field(default="searchindex.pkl.gz")

    # Sphinx builder name / fallback output subdirectory read from conf.py;
    # e.g. "html" (the output dir used by 'make html' for English).
    html_builder_name: str = field(default="html")

    # Default/source language read from conf.py language setting; e.g. "en".
    # Used by index_loader to identify which language falls back to html_builder_name/.
    default_language: str = field(default="en")

    # --- Derived paths (not __init__ parameters) ---

    # Directory containing the selected locale's source catalog;
    # e.g. Path("/repo/locale/vi/LC_MESSAGES").
    po_dir: Path = field(init=False)

    # Canonical source PO read by the compiler;
    # e.g. Path("/repo/locale/vi/LC_MESSAGES/blender_manual.po").
    po_path: Path = field(init=False)

    # Obsolete monolithic MO removed after shard generation;
    # e.g. Path("/repo/locale/vi/LC_MESSAGES/blender_manual.mo").
    legacy_mo_path: Path = field(init=False)

    # Serialized tier cache for this locale;
    # e.g. Path("/repo/build/.translation_cache/vi.pkl").
    cache_path: Path = field(init=False)

    # Advisory lock preventing overlapping runs for this locale;
    # e.g. Path("/repo/build/.translation_cache/vi.lock").
    lock_path: Path = field(init=False)

    # Previous normalized PO used to detect changed translations;
    # e.g. Path("/repo/build/.translation_cache/vi.po.snapshot").
    snapshot_path: Path = field(init=False)

    # Output directory containing one generated MO file per document;
    # e.g. Path("/repo/build/.i18n_shards/locale/vi/LC_MESSAGES").
    shard_lc_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        """Resolve input directories and populate their dependent paths."""
        self.srcdir = Path(self.srcdir).resolve()
        self.locale_dir = Path(self.locale_dir).resolve()
        self.doctree_dir = Path(self.doctree_dir).resolve()
        self.cache_dir = Path(self.cache_dir).resolve()
        self.shard_root = Path(self.shard_root).resolve()

        self.po_dir = self.locale_dir / self.language / "LC_MESSAGES"
        self.po_path = self.po_dir / f"{self.domain}.po"
        self.legacy_mo_path = self.po_path.with_suffix(".mo")
        self.cache_path = self.cache_dir / f"{self.language}.pkl"
        self.lock_path = self.cache_dir / f"{self.language}.lock"
        self.snapshot_path = self.cache_dir / f"{self.language}.po.snapshot"
        self.shard_lc_dir = self.shard_root / self.language / "LC_MESSAGES"

    @staticmethod
    def _read_conf_py(conf_py_path: Path) -> dict[str, str]:
        """Extract key values from manual/conf.py without running Sphinx.

        Delegates to :meth:`ConfPattern.scan`, which uses regex so
        Sphinx-specific globals (``tags``, ``sphinx.version_info``) are never
        evaluated. Returns a dict keyed by :class:`ConfigRecord` field name
        (e.g. ``blender_version``, ``domain``) for every setting that matched.
        """
        try:
            text = conf_py_path.read_text("utf-8")
        except OSError:
            return {}
        return ConfPattern.scan(text)

    @classmethod
    def from_project(
        cls,
        project_root: Path,
        lang: str,
        *,
        build_subdir: str = "build",
        no_touch_rst: bool = True,
        quiet: bool = True,
    ) -> "ConfigRecord":
        """Create a ConfigRecord from the project root and a language code.

        Reads ``blender_version`` and the gettext domain from
        ``manual/conf.py``, locates ``sphinx-build`` in the project venv,
        and derives all build paths from *project_root* using the same
        directory layout that the Makefile expects.

        Parameters
        ----------
        project_root : absolute path to the repository root
        lang         : language code, e.g. ``"vi"``
        build_subdir : name of the top-level build directory (default ``"build"``)
        no_touch_rst : passed through to ``smart_mo_compile --no-touch-rst``
        quiet        : suppress summary lines in both smart_mo and sphinx
        """
        project_root = Path(project_root).resolve()
        build_root = project_root / build_subdir
        conf_path = project_root / "manual" / "conf.py"
        conf_values = cls._read_conf_py(conf_path)

        sphinx_cmd = "sphinx-build"
        for candidate in [
            project_root / ".venv" / "bin" / "sphinx-build",
            project_root / ".venv" / "Scripts" / "sphinx-build.exe",
        ]:
            if candidate.exists():
                sphinx_cmd = str(candidate)
                break

        smart_mo = project_root / "tools" / "translations" / "smart_mo_compile.py"

        return cls(
            language=lang,
            srcdir=project_root / "manual",
            locale_dir=project_root / "locale",
            doctree_dir=build_root / ".doctrees" / lang,
            domain=conf_values.get("domain", "blender_manual"),
            cache_dir=build_root / ".translation_cache",
            shard_root=build_root / ".i18n_shards" / "locale",
            force_rebuild=False,
            no_touch_rst=no_touch_rst,
            verbose=False,
            quiet=quiet,
            blender_version=conf_values.get("blender_version", ""),
            conf_py_path=conf_path,
            sphinx_build_cmd=sphinx_cmd,
            sphinx_builder=conf_values.get("html_builder_name", "html"),
            sphinx_jobs="auto",
            smart_mo_script=smart_mo if smart_mo.exists() else None,
            rst_suffix=conf_values.get("rst_suffix", ".rst"),
            html_page_suffix=conf_values.get("html_page_suffix", ".html"),
            search_index_filename=conf_values.get("search_index_filename", "searchindex.pkl.gz"),
            html_builder_name=conf_values.get("html_builder_name", "html"),
            default_language=conf_values.get("default_language", "en"),
        )


# All PO/MO I/O lives behind these two imports.
#   - sphinx_intl.catalog.load_po: thin wrapper over babel that matches the
#     rest of this repo's translation tooling (see tools/translations/update_po.py).
#   - babel.messages.mofile.write_mo: sphinx-intl does not expose a .mo
#     writer, so we fall back to babel directly for the binary catalog.
try:
    from sphinx_intl.catalog import load_po, dump_po
    from babel.messages.mofile import write_mo
except ImportError as exc:
    # Hard fail with a precise install hint -- the script is useless without these.
    sys.stderr.write(
        "smart_mo_compile.py: sphinx-intl and babel are required "
        "(both are Sphinx-related dependencies of this repo). "
        "Install with: pip install sphinx-intl babel\n"
    )
    sys.stderr.write(f"  ImportError: {exc}\n")
    sys.exit(2)


# ---------------------------------------------------------------------------
# Small helpers for normalising Babel Message fields.
# ---------------------------------------------------------------------------

def _msgstr_of(message) -> str:
    """Return a single string for `message.string`, even for plural forms.

    Babel exposes `Message.string` as either:
      - a str for singular entries, OR
      - a tuple[str, ...] for plural entries (one msgstr per plural form).
      - None for messages with no translation slot at all.

    We collapse plurals into a single string with `\\x01` separators so two
    plural-form messages can be compared / hashed uniformly with singular ones.
    `\\x01` is chosen because it cannot appear in a valid PO msgstr.
    """
    s = message.string
    if s is None:                # No msgstr field at all -> treat as empty.
        return ""
    # str: return as-is; tuple/list: join with the sentinel separator.
    return s if isinstance(s, str) else "\x01".join(s)


def _msgid_of(message) -> str:
    """Return a single string for `message.id`, even for plural forms.

    `Message.id` is str for singular msgids and a tuple `(singular, plural)`
    for plural-form msgids. Same collapse rule as `_msgstr_of`.
    """
    i = message.id
    return i if isinstance(i, str) else "\x01".join(i)


def _is_effective_translation(message) -> bool:
    """True iff this message contributes a translation to a compiled .mo.

    Mirrors Babel's `write_mo(use_fuzzy=False)` default and Sphinx's
    `gettext_allow_fuzzy_translations = False` setting (manual/conf.py:142).
    Both strip the same set of entries when producing the runtime catalog:

      - PO header (msgid == ""): metadata only, never translates anything.
      - Empty msgstr: the source string is used verbatim -- nothing to install.
      - Fuzzy-flagged entries: the translation is unconfirmed; Sphinx is
        configured to refuse them.

    Filtering identically here is what makes the .po <-> .mo diff converge.
    Without this filter, the on-disk fuzzy-stripped .mo "loses" thousands of
    entries that the .po still has, so every run reports them all as changed.
    """
    if not message.id:                              # Skip the PO header.
        return False
    if "fuzzy" in (message.flags or set()):         # Match Sphinx's strict policy.
        return False
    return bool(_msgstr_of(message))                # Non-empty msgstr only.


# ---------------------------------------------------------------------------
# Hashing the catalog content and building msgid->msgstr maps.
# ---------------------------------------------------------------------------

def _hash_catalog(catalog) -> str:
    """blake2b over sorted (msgid, msgstr) pairs of effective translations only.

    Stability properties this gives us:
      - PO header churn (e.g. POT-Creation-Date bumps) does NOT change the hash.
      - Toggling `fuzzy` on/off for an unaffected msgid does NOT change it.
      - The hash matches what is in the compiled .mo, so a PO -> MO -> PO
        round trip is stable.

    blake2b is used (not sha256) for speed on the 15 MB Vietnamese catalog and
    because we only need collision resistance for cache invalidation, not for
    cryptographic security.
    """
    h = hashlib.blake2b(digest_size=32)
    pairs = []
    for message in catalog:                                  # Babel iteration already skips obsolete entries.
        if not _is_effective_translation(message):
            continue
        pairs.append((_msgid_of(message), _msgstr_of(message)))
    pairs.sort()                                             # Deterministic order across runs / Babel versions.
    for msgid, msgstr in pairs:
        h.update(msgid.encode("utf-8"))
        h.update(b"\x00")                                    # NUL separator (cannot appear inside the strings).
        h.update(msgstr.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def _hash_shard_layout(catalog, config_record: ConfigRecord) -> str:
    """Hash the effective msgid -> document-slug mapping for shard placement.

    In the monolithic PO, `#:` location comments look like translator metadata,
    but this helper uses them as build data: they decide which per-document
    `.mo` shard receives each msgid. Header churn and line-number-only changes
    still collapse away, but moving an effective translation to another RST
    invalidates the hash and forces a full shard layout refresh.
    """
    msgid_to_docs = _build_msgid_to_docs(catalog, config_record)
    h = hashlib.blake2b(digest_size=32)
    rows: list[tuple[str, tuple[str, ...]]] = []
    for message in catalog:
        if not _is_effective_translation(message):
            continue
        msgid = _msgid_of(message)
        rows.append((msgid, tuple(sorted(msgid_to_docs.get(msgid, ())))))
    rows.sort()
    for msgid, slugs in rows:
        h.update(msgid.encode("utf-8"))
        h.update(b"\x00")
        for slug in slugs:
            h.update(slug.encode("utf-8"))
            h.update(b"\x00")
        h.update(b"\x00")
    return h.hexdigest()


def _msgid_to_translation(catalog) -> dict[str, str]:
    """Build `{msgid: msgstr}` for effective (non-empty, non-fuzzy) translations.

    Used to diff the previously-compiled .mo against the current .po. Both
    sides go through this filter so the diff is symmetric -- an entry that
    is fuzzy in the PO is treated as "missing" on both sides, not as "added".
    """
    out: dict[str, str] = {}
    for message in catalog:
        if not _is_effective_translation(message):
            continue
        out[_msgid_of(message)] = _msgstr_of(message)
    return out


# ---------------------------------------------------------------------------
# Mapping changed msgids back to the RST files that reference them.
# ---------------------------------------------------------------------------

def _resolve_location(
    filename: str, config_record: ConfigRecord,
) -> Path | None:
    """Resolve a `#:` location string to an existing file under srcdir, or None.

    Background: sphinx-build's gettext builder writes the .pot at
    `build/gettext/blender_manual.pot` with `#:` paths relative to
    `build/gettext/` -- e.g. `../../manual/foo.rst`. sphinx-intl then merges
    that .pot into `locale/<lang>/LC_MESSAGES/blender_manual.po` and preserves
    the `#:` strings verbatim. The result is that the `#:` paths in the .po
    are no longer meaningful relative to the .po's own directory; resolving
    `locale/vi/LC_MESSAGES/../../manual/foo.rst` lands at `locale/manual/foo.rst`,
    which does not exist.

    Strategy: ignore the leading `..` segments and look for `srcdir.name`
    (e.g. "manual") inside the path components. Anything AFTER that marker
    is the path-from-srcdir. This works regardless of how many `..` levels
    the .pot was written from.
    """
    srcdir = config_record.srcdir
    po_dir = config_record.po_dir
    p = Path(filename)
    srcdir_name = srcdir.name       # The basename to search for (e.g. "manual").
    parts = p.parts

    # Absolute paths are unusual but handle them defensively.
    if p.is_absolute():
        try:
            r = p.resolve(strict=True)
        except (OSError, FileNotFoundError):
            return None
        try:
            r.relative_to(srcdir)   # Reject anything outside the source tree.
        except ValueError:
            return None
        return r if r.is_file() else None

    # Primary candidate: srcdir-name-anchored. Scan from the right so that if
    # the path happens to contain "manual" more than once (unlikely), the
    # rightmost occurrence wins -- that is the actual srcdir marker.
    candidates: list[Path] = []
    for i in range(len(parts) - 1, -1, -1):
        if parts[i] == srcdir_name:
            tail = parts[i + 1:]                          # Components after the marker.
            if tail:
                candidates.append(srcdir.joinpath(*tail))
            break

    # Fallback candidates for unusual layouts (single .po hand-edited, etc.).
    candidates.append(po_dir / p)            # Naive: relative to .po file.
    candidates.append(srcdir / p)            # Relative to srcdir.
    candidates.append(srcdir.parent / p)     # Relative to repo root.

    # Take the first candidate that (a) resolves, (b) exists, (c) lies under srcdir.
    for cand in candidates:
        try:
            cand_r = cand.resolve()
        except OSError:
            continue
        if not cand_r.is_file():
            continue
        try:
            cand_r.relative_to(srcdir)       # Reject paths that escape srcdir.
        except ValueError:
            continue
        return cand_r
    return None


def _msgid_to_locations(
    catalog, config_record: ConfigRecord,
) -> dict[str, set[Path]]:
    """Build `{msgid: {rst_path, ...}}` for every catalog entry with `#:` lines.

    Only msgids that resolve to at least one RST under `srcdir` are included;
    entries with no resolvable locations are silently dropped (the caller
    treats "no locations" as "no docs to invalidate", which is the safe answer
    -- the .mo still gets the new translation; the affected docs will rebuild
    next time their own RST mtime changes).
    """
    out: dict[str, set[Path]] = {}
    for message in catalog:
        if not message.id:                                       # Skip header.
            continue
        # Same plural-collapse rule as elsewhere so msgid keys are consistent.
        msgid = message.id if isinstance(message.id, str) else "\x01".join(message.id)
        paths: set[Path] = set()
        for filename, _lineno in message.locations or ():        # `_lineno` not needed; mtime touch is per-file.
            resolved = _resolve_location(filename, config_record)
            if resolved is not None:
                paths.add(resolved)
        if paths:
            out[msgid] = paths
    return out


# ---------------------------------------------------------------------------
# Snapshot-based RST touching.
#
# Sphinx's per-doc gettext dependency (one doc -> one shard .mo) usually
# invalidates exactly the affected docs when smart_mo_compile rewrites a
# shard. In practice that signal can be missed -- e.g. when sphinx-autobuild
# rebuilds before the shard mtime has propagated through the doctree
# pickle, or when the build env was populated before the shard tree
# existed. To make that case self-healing, every tier-4 run also bumps the
# mtime of every RST referenced by a msgid whose effective translation
# differs from the previous run's persisted snapshot.
#
# Layout: <cache_dir>/<lang>.po.snapshot, a normalised .po written via
# sphinx_intl.catalog.dump_po(width=4096). The wide width disables babel's
# default 76-column wrap so the snapshot text is stable across runs and
# the file is suitable for direct diff/inspection if needed.
# ---------------------------------------------------------------------------


def _write_po_snapshot(catalog, snapshot_path: Path) -> None:
    """Atomically persist `catalog` as a normalised .po reference.

    Uses sphinx_intl.catalog.dump_po(width=4096) so long msgid/msgstr lines
    are not wrapped -- mirrors `msgmerge --no-wrap`. The wide width keeps
    the text representation stable across runs; without it babel's
    default 76-column wrap would produce spurious whole-file diffs.
    """
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=snapshot_path.name + ".", dir=str(snapshot_path.parent),
    )
    os.close(fd)
    try:
        dump_po(tmp, catalog, width=4096)
        os.replace(tmp, snapshot_path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _changed_msgids_vs_snapshot(current_catalog, snapshot_catalog) -> set[str]:
    """Return msgids whose effective translation differs vs the snapshot.

    Captured cases:
      - msgid present in both but msgstr changed
      - msgid added since the snapshot
      - effective state flipped (fuzzy removed, msgstr cleared, etc.)

    msgids that vanished entirely from the current catalog are NOT
    returned: the caller cannot resolve their RST location without an
    entry in the current catalog, and a vanished string normally means
    the source RST changed too (Sphinx will catch that on its own).
    """
    current_map = _msgid_to_translation(current_catalog)
    snapshot_map = _msgid_to_translation(snapshot_catalog)
    out: set[str] = set()
    for msgid, msgstr in current_map.items():
        if snapshot_map.get(msgid) != msgstr:
            out.add(msgid)
    return out


def _touch_rst_paths(paths: set[Path]) -> None:
    """Bump mtime on each RST path in `paths`."""
    now = time.time()
    for p in paths:
        try:
            os.utime(p, (now, now))
        except OSError as exc:
            sys.stderr.write(
                f"smart_mo_compile: could not touch {p}: {exc}\n"
            )


def _log_rst_touch(
    paths: set[Path], changed_count: int, missing: int,
    config_record: ConfigRecord, *, unit: str = "changed msgid(s)",
) -> None:
    """Emit the standard one-line RST touch summary."""
    if config_record.quiet:
        return
    first = next(iter(sorted(paths))) if paths else None
    try:
        first_rel = first.relative_to(config_record.srcdir.parent) if first else None
    except ValueError:
        first_rel = first
    first_hint = f" [first: {first_rel}]" if first_rel else ""
    missing_hint = f" ({missing} had no resolvable RST)" if missing else ""
    print(
        f"smart_mo_compile: touched {len(paths)} RST file(s) for "
        f"{changed_count} {unit}{missing_hint}{first_hint}"
    )


def _touch_rsts_for_msgids(
    catalog, msgids: set[str], config_record: ConfigRecord,
) -> tuple[set[Path], int]:
    """Bump mtime on every RST referenced by any msgid in `msgids`.

    Returns `(touched_paths, missing_msgids)` -- `missing_msgids` counts
    entries whose `#:` lines did not resolve to any file under `srcdir`
    (rare; usually a hand-added msgid with no location comment).

    The atime is also set to now -- preserving it would require an extra
    stat() per file and Sphinx only consults mtime anyway.
    """
    if not msgids:
        return set(), 0
    loc_map = _msgid_to_locations(catalog, config_record)
    paths: set[Path] = set()
    missing = 0
    for mid in msgids:
        per = loc_map.get(mid)
        if per:
            paths.update(per)
        else:
            missing += 1
    _touch_rst_paths(paths)
    return paths, missing


def _touch_rsts_for_snapshot_diff(
    catalog, config_record: ConfigRecord,
) -> int:
    """Touch RSTs for every msgid that changed vs the snapshot.

    First run (no snapshot yet) is a no-op: there is no baseline to diff
    against and a mass touch would invalidate every doc for no reason. In
    every other case the helper prints exactly one line so the make
    livehtml terminal makes it obvious whether the touch step found work
    to do and which file it landed on. Returns the count of RST files
    touched.
    """
    if not config_record.snapshot_path.is_file():
        if not config_record.quiet:
            print(
                "smart_mo_compile: no snapshot yet, skipping RST touch "
                "(snapshot will be created at the end of this run)"
            )
        return 0
    try:
        snapshot_catalog = load_po(str(config_record.snapshot_path))
    except Exception as exc:
        # Corrupt snapshot -- log and skip; the fresh write below heals it.
        sys.stderr.write(
            "smart_mo_compile: could not load snapshot "
            f"{config_record.snapshot_path}: {exc}\n"
        )
        return 0
    changed = _changed_msgids_vs_snapshot(catalog, snapshot_catalog)
    if not changed:
        if not config_record.quiet:
            print(
                "smart_mo_compile: snapshot diff empty "
                "(no msgstrs changed vs snapshot)"
            )
        return 0
    paths, missing = _touch_rsts_for_msgids(catalog, changed, config_record)
    _log_rst_touch(paths, len(changed), missing, config_record)
    return len(paths)


# ---------------------------------------------------------------------------
# Atomic file writes -- so a crash mid-write never leaves a torn .mo / .hash.
# ---------------------------------------------------------------------------

def _atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write `data` to `path` atomically via tempfile + os.replace.

    os.replace is atomic on POSIX (single rename(2) syscall), so readers
    either see the old file or the new file -- never a half-written one.
    The tempfile lives in the same directory as the target so the rename
    cannot cross filesystem boundaries (which would defeat atomicity).
    """
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        # On any failure (write error, permission, disk full), clean up the
        # tempfile so it does not get gitignore-leaked or confuse a later run.
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Tiered cache: mtime+size -> raw sha256 -> semantic blake2b -> slow path.
# Cache file lives at <po>.cache and contains a single pickled dict.
# ---------------------------------------------------------------------------

def _sha256_file(path: Path, chunk_size: int = 8192) -> str:
    """sha256 over the raw bytes of `path`, streaming in `chunk_size` chunks.

    Used by tier 2 as a fast (~50 ms on the 15 MB Vietnamese PO) "did the
    content change at all?" check, before falling through to the expensive
    `load_po` + semantic hash. sha256 is chosen over blake2b only because
    it's the more common file-content hash; the choice is not load-bearing.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def _read_cache(cache_path: Path) -> dict | None:
    """Load and validate the pickled tier cache, or return None.

    Returns None (silent fall-through) on any of:
      - cache file missing
      - read/unpickle error (corrupted)
      - missing/mismatched `version` key
      - missing any required field

    NEVER raises -- a bad cache must not break the build.
    """
    if not cache_path.is_file():
        return None
    try:
        with open(cache_path, "rb") as f:
            data = pickle.load(f)
    except Exception:
        # Corrupted pickle, truncated file, permission error -- treat as no cache.
        return None
    if not isinstance(data, dict):
        return None
    version = data.get(CacheKey.VERSION)
    if version not in _CACHE_COMPAT_VERSIONS:
        # Schema mismatch (older or future version) -- treat as no cache.
        return None
    required = [
        CacheKey.PO_MTIME_NS,
        CacheKey.PO_SIZE,
        CacheKey.RAW_HASH,
        CacheKey.SEMANTIC_HASH,
        CacheKey.OLD_MAP,
        CacheKey.MSGID_TO_DOCS,
        CacheKey.DOC_TO_MSGIDS,
        CacheKey.DOC_HASHES,
    ]
    if version >= 3:
        required.append(CacheKey.LAYOUT_HASH)
    if not all(k in data for k in required):
        return None
    if not isinstance(data[CacheKey.OLD_MAP], dict):
        return None
    return data


def _write_cache(cache_path: Path, payload: dict) -> None:
    """Atomically write advisory cache state; log failures without aborting.

    Shards remain authoritative. A missing or corrupt cache only makes the
    next invocation take the full tier-4 path.
    """
    try:
        data = pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL)
        _atomic_write_bytes(cache_path, data)
    except Exception as exc:
        sys.stderr.write(f"smart_mo_compile: could not write cache {cache_path}: {exc}\n")


# ---------------------------------------------------------------------------
# Shard-mode helpers. Runtime builds no longer produce a global MO.
#
# Shards = one .mo per doc slug under
#   <shard_root>/<lang>/LC_MESSAGES/<slug>.mo
# With `gettext_compact = False` in conf.py, Sphinx looks up each doc's
# translations under its own slug, so touching one shard invalidates only
# the docs that actually reference its msgids.
# ---------------------------------------------------------------------------

# Babel Catalog is imported here (and not at module top) because it is only
# needed for the shard-mode code path. Keeping the top-level imports lean
# matches the existing legacy code (which uses load_po / read_mo / write_mo).
# This is *not* an inline import in the forbidden sense -- it is module-scope.
try:
    from babel.messages.catalog import Catalog
except ImportError:  # pragma: no cover - covered by the top-level import guard.
    Catalog = None  # type: ignore[assignment]


def _doc_slug(rst_path: Path, srcdir: Path) -> str:
    """Return the Sphinx doc slug for an RST file under `srcdir`.

    Mirrors `sphinx/util/i18n.py:docname_to_domain()` with
    `gettext_compact = False`: POSIX-style forward-slash separators with
    the `.rst` suffix stripped.

    Examples
    --------
    srcdir=/repo/manual, rst=/repo/manual/modeling/meshes/intro.rst
    -> "modeling/meshes/intro"
    """
    rel = rst_path.resolve().relative_to(srcdir.resolve())
    return PurePosixPath(rel.with_suffix("").as_posix()).as_posix()


def _slug_from_resolved(resolved_rst: Path, srcdir_resolved: Path) -> str | None:
    """Cheap variant of `_doc_slug` that assumes both paths are already resolved.

    Returns None if `resolved_rst` is outside `srcdir_resolved` (defensive).
    """
    try:
        rel = resolved_rst.relative_to(srcdir_resolved)
    except ValueError:
        return None
    return PurePosixPath(rel.with_suffix("").as_posix()).as_posix()


def _build_msgid_to_docs(
    catalog, config_record: ConfigRecord,
) -> dict[str, set[str]]:
    """Build `{msgid: set of doc slugs that reference it}`.

    Iterates the per-msgid `#:` location table and converts each resolved
    RST path into a doc slug. msgids with no resolvable locations are
    omitted (the caller treats them as orphans).
    """
    loc_map = _msgid_to_locations(catalog, config_record)
    srcdir_r = config_record.srcdir
    out: dict[str, set[str]] = {}
    for msgid, paths in loc_map.items():
        slugs = {s for s in (_slug_from_resolved(p, srcdir_r) for p in paths)
                 if s is not None}
        if slugs:
            out[msgid] = slugs
    return out


def _build_doc_to_msgids(msgid_to_docs: dict[str, set[str]]) -> dict[str, set[str]]:
    """Invert `_build_msgid_to_docs` into `{doc slug: set of msgids}`."""
    out: dict[str, set[str]] = {}
    for msgid, slugs in msgid_to_docs.items():
        for slug in slugs:
            out.setdefault(slug, set()).add(msgid)
    return out


def _index_messages_by_id(catalog) -> dict[str, object]:
    """Build `{collapsed-msgid: Message}` for effective translations only."""
    return {_msgid_of(m): m for m in catalog if _is_effective_translation(m)}


def _copy_message_into(sub_catalog, message) -> None:
    """Add `message` (a babel Message) to `sub_catalog` preserving its fields.

    Locations/flags/comments/context are forwarded verbatim so the shard's
    .mo is a faithful subset of the source catalog.
    """
    sub_catalog.add(
        id=message.id,
        string=message.string,
        locations=message.locations or (),
        flags=set(message.flags or ()),
        auto_comments=list(message.auto_comments or ()),
        user_comments=list(message.user_comments or ()),
        context=message.context,
    )


def _new_sub_catalog(source_catalog):
    """Create an empty sub-catalog that inherits the source catalog headers.

    Inheriting `mime_headers` is what carries `Plural-Forms`,
    `Content-Type`, `Language`, etc. into the shard's .mo so `ngettext()`
    callsites keep working.
    """
    if Catalog is None:
        raise RuntimeError("babel.messages.catalog.Catalog is unavailable")
    sub = Catalog(locale=source_catalog.locale)
    sub.mime_headers = source_catalog.mime_headers
    return sub


def _collect_rst_slugs(config_record: ConfigRecord) -> set[str]:
    """Return doc slugs for every `.rst` under `srcdir` (recursive)."""
    srcdir_r = config_record.srcdir
    out: set[str] = set()
    for rst in srcdir_r.rglob("*.rst"):
        slug = _slug_from_resolved(rst, srcdir_r)
        if slug is not None:
            out.add(slug)
    return out


def _populate_translated_shards(
    catalog, doc_to_msgids: dict[str, set[str]], msg_by_id: dict[str, object],
) -> dict[str, object]:
    """Build the {slug: sub-catalog} map for slugs that have translations."""
    shards: dict[str, object] = {}
    for slug, msgids in doc_to_msgids.items():
        sub = _new_sub_catalog(catalog)
        for mid in sorted(msgids):
            message = msg_by_id.get(mid)
            if message is not None:
                _copy_message_into(sub, message)
        shards[slug] = sub
    return shards


def _add_empty_shards_for_untranslated(
    catalog, shards: dict[str, object], config_record: ConfigRecord,
) -> None:
    """Insert header-only shards for every RST that has no translations.

    Without these, `gettext_compact = False` triggers a `catalog not found`
    warning per untranslated doc. Empty shards are byte-stable, so once
    written they hit the skip-on-identical-bytes branch forever after.
    """
    for slug in _collect_rst_slugs(config_record):
        if slug not in shards:
            shards[slug] = _new_sub_catalog(catalog)


def _add_orphan_shard(
    catalog, shards: dict[str, object], msgid_to_docs: dict[str, set[str]],
    msg_by_id: dict[str, object],
) -> int:
    """Collect msgids with no resolvable doc and stash them in the orphan shard.

    Returns the number of orphan msgids collected. The orphan shard is
    loaded by Sphinx but referenced by no doc, so its mtime invalidates
    nothing -- it just keeps the translations reachable at runtime.
    """
    orphan_ids = [mid for mid in msg_by_id.keys() if mid not in msgid_to_docs]
    if not orphan_ids:
        return 0
    sub = _new_sub_catalog(catalog)
    for mid in sorted(orphan_ids):
        _copy_message_into(sub, msg_by_id[mid])
    shards[_ORPHAN_SLUG] = sub
    return len(orphan_ids)


def _catalog_to_shards(
    catalog, config_record: ConfigRecord,
) -> tuple[dict[str, object], dict[str, set[str]], dict[str, set[str]], int]:
    """Split `catalog` into one sub-Catalog per doc slug.

    Returns `(shards, msgid_to_docs, doc_to_msgids, orphan_count)`.

    Every RST under `srcdir` gets a shard (empty if untranslated). msgids
    with no resolvable `#:` location land in the `__orphan__` shard.
    """
    msgid_to_docs = _build_msgid_to_docs(catalog, config_record)
    doc_to_msgids = _build_doc_to_msgids(msgid_to_docs)
    msg_by_id = _index_messages_by_id(catalog)

    shards = _populate_translated_shards(catalog, doc_to_msgids, msg_by_id)
    _add_empty_shards_for_untranslated(catalog, shards, config_record)
    orphan_count = _add_orphan_shard(catalog, shards, msgid_to_docs, msg_by_id)
    return shards, msgid_to_docs, doc_to_msgids, orphan_count


def _serialize_catalog_to_bytes(catalog) -> bytes:
    """Return the canonical .mo binary for `catalog` (in-memory)."""
    buf = io.BytesIO()
    write_mo(buf, catalog)
    return buf.getvalue()


def _shard_target_path(config_record: ConfigRecord, slug: str) -> Path:
    """Return the on-disk path for the shard identified by `slug`."""
    return config_record.shard_lc_dir / f"{slug}.mo"


def _existing_shard_slugs(lc_dir: Path) -> set[str]:
    """Return the slug for every `.mo` currently under `lc_dir`."""
    if not lc_dir.is_dir():
        return set()
    out: set[str] = set()
    for mo in lc_dir.rglob("*.mo"):
        rel = mo.relative_to(lc_dir)
        out.add(PurePosixPath(rel.with_suffix("").as_posix()).as_posix())
    return out


def _write_shard_if_changed(target: Path, new_bytes: bytes) -> bool:
    """Atomic-replace `target` with `new_bytes` iff its contents differ.

    Returns True when a write occurred, False when the file was already
    byte-identical (the "Never Rewrite Identical Files" rule).
    """
    if target.is_file():
        try:
            existing = target.read_bytes()
        except OSError:
            existing = None
        if existing == new_bytes:
            return False
    target.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_bytes(target, new_bytes)
    return True


def _unlink_stale_shards(
    lc_dir: Path, desired_slugs: set[str],
) -> int:
    """Remove on-disk shards whose slug is not in `desired_slugs`.

    Returns the count of unlinked files. The orphan shard is never deleted
    here -- it is always in `desired_slugs` when it is in use.
    """
    if not lc_dir.is_dir():
        return 0
    deleted = 0
    for slug in _existing_shard_slugs(lc_dir) - desired_slugs:
        path = lc_dir / f"{slug}.mo"
        try:
            path.unlink()
            deleted += 1
        except OSError as exc:
            sys.stderr.write(
                f"smart_mo_compile: could not unlink stale shard {path}: {exc}\n"
            )
    return deleted


def _emit_shards(
    shards: dict[str, object], config_record: ConfigRecord,
) -> tuple[int, int, int]:
    """Write/skip every shard and remove stale ones.

    Returns `(written, skipped, deleted)`. Byte-identical shards are
    skipped without touching mtime (the rule that makes Sphinx see no
    invalidation for unchanged docs).
    """
    config_record.shard_lc_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    for slug, sub in shards.items():
        target = _shard_target_path(config_record, slug)
        new_bytes = _serialize_catalog_to_bytes(sub)
        if _write_shard_if_changed(target, new_bytes):
            written += 1
        else:
            skipped += 1

    deleted = _unlink_stale_shards(
        config_record.shard_lc_dir, set(shards.keys()),
    )
    return written, skipped, deleted


def _delete_stale_global_mo(mo_path: Path) -> None:
    """Remove a legacy monolithic `blender_manual.mo` if present.

    Once the shard path is active, the global .mo is dead weight and risks
    confusing Sphinx if `locale_dirs` is ever misconfigured. The file is
    gitignored, so deletion is safe.
    """
    if mo_path.is_file():
        try:
            mo_path.unlink()
        except OSError as exc:
            sys.stderr.write(
                f"smart_mo_compile: could not unlink legacy {mo_path}: {exc}\n"
            )


def _unlink_quiet(path: Path) -> bool:
    """Unlink `path` if it exists; swallow OSError. Returns True on actual removal."""
    if not path.is_file():
        return False
    try:
        path.unlink()
        return True
    except OSError as exc:
        sys.stderr.write(
            f"smart_mo_compile: could not unlink {path}: {exc}\n"
        )
        return False


def _purge_legacy_sidecars(po_path: Path, *, quiet: bool) -> None:
    """Unlink obsolete sidecar files adjacent to the canonical PO.

    An earlier compiler wrote `<po>.cache`, `<po>.hash`, and `<po>.lock`
    next to `blender_manual.po`. The current cache and lock live under
    `<cache_dir>`, and the `.hash` sidecar is no longer used. The files are
    gitignored, so removal does not remove tracked translation input.
    """
    removed: list[str] = []
    for ext in ("cache", "hash", "lock"):
        sidecar = po_path.with_name(po_path.name + f".{ext}")
        if _unlink_quiet(sidecar):
            removed.append(sidecar.name)
    if removed and not quiet:
        print(
            "smart_mo_compile: removed stale legacy sidecar(s): "
            + ", ".join(removed)
        )


def _purge_stale_environment_pickle(doctree_dir: Path, *, quiet: bool) -> bool:
    """Unlink `environment.pickle` carrying legacy global-.mo dependencies.

    The legacy code path registered every doc as depending on
    `blender_manual.mo`. After the shard flip, those entries in
    `environment.pickle` point at the (now unused) global .mo and Sphinx
    keeps treating every doc as outdated. Wiping the pickle forces a
    one-time environment rebuild; subsequent runs are no-ops because the
    presence of `<cache_dir>/<lang>.pkl` gates this purge to first-run only.

    Returns True if the pickle was unlinked (for logging by the caller).
    """
    pickle_path = doctree_dir / "environment.pickle"
    if not pickle_path.is_file():
        return False
    try:
        pickle_path.unlink()
    except OSError as exc:
        sys.stderr.write(
            f"smart_mo_compile: could not purge {pickle_path}: {exc}\n"
        )
        return False
    if not quiet:
        print(
            "smart_mo_compile: purged stale environment.pickle "
            "(legacy global-mo dependency)"
        )
    return True


def _hash_sub_catalog(catalog) -> str:
    """Stable hash for a shard sub-catalog (alias of `_hash_catalog`)."""
    return _hash_catalog(catalog)


def _build_doc_hashes(shards: dict[str, object]) -> dict[str, str]:
    """Build the persisted `{slug: semantic shard hash}` bookkeeping map.

    Partial runs copy unchanged values forward and replace entries for shards
    they rewrite or delete, keeping cache state aligned with the shard tree.
    """
    return {slug: _hash_sub_catalog(sub) for slug, sub in shards.items()}


def _cache_str_set_map(cache: dict, key: str) -> dict[str, set[str]] | None:
    """Decode a cached string-to-string-set index, or reject the whole field.

    Older pickles may contain lists or tuples, so values are normalized to
    sets. Any non-string key/member returns None and forces a full rebuild.
    Empty value sets are omitted because the indexes store relationships only.
    """
    raw = cache.get(key)
    if not isinstance(raw, dict):
        return None
    out: dict[str, set[str]] = {}
    for k, values in raw.items():
        if not isinstance(k, str):
            return None
        if not isinstance(values, (set, list, tuple)):
            return None
        value_set: set[str] = set()
        for value in values:
            if not isinstance(value, str):
                return None
            value_set.add(value)
        if value_set:
            out[k] = value_set
    return out


def _cache_str_map(cache: dict, key: str) -> dict[str, str] | None:
    """Decode a cached string-to-string map, or return None on bad schema.

    Partial regeneration trusts these fields only after every key and value
    has been validated. None tells the caller to use the full tier-4 path.
    """
    raw = cache.get(key)
    if not isinstance(raw, dict):
        return None
    out: dict[str, str] = {}
    for k, value in raw.items():
        if not isinstance(k, str) or not isinstance(value, str):
            return None
        out[k] = value
    return out


def _changed_msgids_from_maps(
    current_map: dict[str, str], old_map: dict[str, str],
) -> set[str]:
    """Return added, changed, or removed effective runtime translations.

    `_msgid_to_translation` excludes empty and fuzzy entries, so clearing a
    msgstr or marking it fuzzy appears here as removal from `current_map`.
    """
    changed = {
        msgid for msgid, msgstr in current_map.items()
        if old_map.get(msgid) != msgstr
    }
    changed.update(msgid for msgid in old_map if msgid not in current_map)
    return changed


def _msgids_to_docs_for_subset(
    catalog, msgids: set[str], config_record: ConfigRecord,
) -> dict[str, set[str]]:
    """Build `{msgid: doc slugs}` for only the requested msgids.

    This uses the `#:` location lines in the PO. It intentionally accepts
    msgids even when their current msgstr is empty/fuzzy, because those
    entries still tell us which RST needs a touch and which shard must lose
    the now-ineffective translation.
    """
    if not msgids:
        return {}
    srcdir_r = config_record.srcdir
    out: dict[str, set[str]] = {}
    for message in catalog:
        if not message.id:
            continue
        msgid = _msgid_of(message)
        if msgid not in msgids:
            continue
        slugs: set[str] = set()
        for filename, _lineno in message.locations or ():
            resolved = _resolve_location(filename, config_record)
            if resolved is None:
                continue
            slug = _slug_from_resolved(resolved, srcdir_r)
            if slug is not None:
                slugs.add(slug)
        if slugs:
            out[msgid] = slugs
    return out


def _rst_path_for_slug(config_record: ConfigRecord, slug: str) -> Path:
    """Return the RST path for a Sphinx doc slug."""
    return (
        config_record.srcdir
        / Path(*PurePosixPath(slug).parts).with_suffix(".rst")
    )


def _build_doc_shard(catalog, doc_msgids: set[str], msg_by_id: dict[str, object]):
    """Build one doc shard from a msgid set and current effective messages."""
    sub = _new_sub_catalog(catalog)
    for mid in sorted(doc_msgids):
        message = msg_by_id.get(mid)
        if message is not None:
            _copy_message_into(sub, message)
    return sub


def _copy_doc_index(index: dict[str, set[str]]) -> dict[str, set[str]]:
    """Deep-copy a `{str: set[str]}` index."""
    return {k: set(v) for k, v in index.items()}


def _partial_cache_inputs(
    cache: dict | None,
) -> tuple[dict[str, str], dict[str, set[str]], dict[str, set[str]], dict[str, str]] | None:
    """Return the four validated indexes required by partial regeneration.

    The tuple is `(old_map, msgid_to_docs, doc_to_msgids, doc_hashes)`. If any
    field is absent or malformed, returning None prevents partial mutation of
    incomplete state and makes the caller perform a full rebuild.
    """
    if cache is None:
        return None
    old_map = _cache_str_map(cache, CacheKey.OLD_MAP)
    msgid_to_docs = _cache_str_set_map(cache, CacheKey.MSGID_TO_DOCS)
    doc_to_msgids = _cache_str_set_map(cache, CacheKey.DOC_TO_MSGIDS)
    doc_hashes = _cache_str_map(cache, CacheKey.DOC_HASHES)
    if None in (old_map, msgid_to_docs, doc_to_msgids, doc_hashes):
        return None
    return old_map, msgid_to_docs, doc_to_msgids, doc_hashes


def _apply_changed_msgid_doc_moves(
    *, changed_msgids: set[str], current_map: dict[str, str],
    old_msgid_to_docs: dict[str, set[str]],
    current_changed_docs: dict[str, set[str]],
    new_msgid_to_docs: dict[str, set[str]],
    new_doc_to_msgids: dict[str, set[str]],
) -> tuple[set[str], bool]:
    """Apply changed msgids to mutable copies of both relationship indexes.

    For each msgid, remove stale doc edges, add current edges, and drop the
    msgid entirely when its translation is no longer effective. Both old and
    current doc slugs are returned because either side may need its shard
    rewritten. `orphan_changed` requests a separate orphan-shard refresh.

    Returns `(affected_doc_slugs, orphan_changed)`. The caller owns the copied
    indexes; the cache loaded from disk is not mutated.
    """
    affected_docs: set[str] = set()
    orphan_changed = False
    for mid in changed_msgids:
        old_docs = set(old_msgid_to_docs.get(mid, set()))
        current_docs = set(current_changed_docs.get(mid, set()))
        index_docs = current_docs if mid in current_map else set()
        current_orphan = mid in current_map and not current_docs
        affected_docs.update(old_docs)
        affected_docs.update(current_docs)

        if old_docs:
            for slug in old_docs - index_docs:
                msgids = new_doc_to_msgids.get(slug)
                if msgids is not None:
                    msgids.discard(mid)
                    if not msgids:
                        new_doc_to_msgids.pop(slug, None)

        if mid in current_map and index_docs:
            new_msgid_to_docs[mid] = index_docs
            for slug in index_docs:
                new_doc_to_msgids.setdefault(slug, set()).add(mid)
        else:
            new_msgid_to_docs.pop(mid, None)

        if current_orphan or (mid not in current_map and not old_docs):
            orphan_changed = True
    return affected_docs, orphan_changed


def _touch_rsts_for_doc_slugs(
    slugs: set[str], config_record: ConfigRecord, changed_count: int, *,
    unit: str = "changed msgid(s)",
) -> int:
    """Touch existing RSTs for changed slugs and return the touched count.

    Missing RSTs are reported through the standard summary; they can occur
    when a cached document was removed since the previous run.
    """
    paths = {
        path.resolve()
        for path in (
            _rst_path_for_slug(config_record, slug) for slug in slugs
        )
        if path.is_file()
    }
    missing = max(0, len(slugs) - len(paths))
    _touch_rst_paths(paths)
    _log_rst_touch(
        paths, changed_count, missing, config_record, unit=unit,
    )
    return len(paths)


def _changed_doc_slugs_from_hashes(
    current_doc_hashes: dict[str, str], cache: dict | None,
) -> set[str] | None:
    """Return doc slugs whose emitted shard hash differs from cached state.

    None means the cache does not carry trustworthy doc-hash data, usually a
    first run after cache deletion or schema upgrade. The caller can then rely
    on the environment-pickle purge to force a full read.
    """
    old_doc_hashes = _cache_str_map(cache, CacheKey.DOC_HASHES) if cache else None
    if old_doc_hashes is None:
        return None
    changed = {
        slug for slug, shard_hash in current_doc_hashes.items()
        if old_doc_hashes.get(slug) != shard_hash
    }
    changed.update(slug for slug in old_doc_hashes if slug not in current_doc_hashes)
    changed.discard(_ORPHAN_SLUG)
    return changed


def _touch_rsts_for_doc_hash_diff(
    current_doc_hashes: dict[str, str], cache: dict | None,
    config_record: ConfigRecord,
) -> int | None:
    """Touch RSTs whose generated document shard differs from cached state."""
    changed_slugs = _changed_doc_slugs_from_hashes(current_doc_hashes, cache)
    if changed_slugs is None:
        return None
    if not changed_slugs:
        if not config_record.quiet:
            print(
                "smart_mo_compile: shard diff empty "
                "(no generated document shards changed)"
            )
        return 0
    return _touch_rsts_for_doc_slugs(
        changed_slugs, config_record, len(changed_slugs),
        unit="changed doc shard(s)",
    )


@dataclass(frozen=True)
class ShardWriteResult:
    """Outcome of syncing one shard (a document shard or the orphan shard).

    Replaces the former cryptic `(written, skipped, deleted, semantic_hash)`
    4-tuple. At most one of the three counts is 1 and the rest are 0, so the
    partial-run loop can add them straight into its running totals:

      * ``written``  -- the shard's bytes changed and were atomically replaced;
      * ``skipped``  -- the shard was byte-identical, so its mtime is untouched;
      * ``deleted``  -- a stale shard with no remaining content was unlinked.

    A run that finds nothing to delete reports all three as 0.

    ``semantic_hash`` is the blake2b of the emitted sub-catalog, or ``None``
    when no shard remains (deleted, or never existed). The caller stores the
    hash under the slug, or drops the slug from its doc-hash index on ``None``.
    """

    written: int = 0
    skipped: int = 0
    deleted: int = 0
    semantic_hash: str | None = None


def _write_or_delete_doc_shard(
    *, catalog, slug: str, doc_msgids: set[str], msg_by_id: dict[str, object],
    config_record: ConfigRecord,
) -> ShardWriteResult:
    """Bring one document shard into sync with the current catalog.

    A removed RST with no remaining msgids deletes its stale shard. Otherwise
    a header-only or translated shard is emitted and identical bytes preserve
    the existing mtime. See :class:`ShardWriteResult` for the returned fields.
    """
    target = _shard_target_path(config_record, slug)
    rst_exists = _rst_path_for_slug(config_record, slug).is_file()
    if not rst_exists and not doc_msgids:
        if _unlink_quiet(target):
            return ShardWriteResult(deleted=1)
        return ShardWriteResult()

    sub = _build_doc_shard(catalog, doc_msgids, msg_by_id)
    new_bytes = _serialize_catalog_to_bytes(sub)
    if _write_shard_if_changed(target, new_bytes):
        return ShardWriteResult(written=1, semantic_hash=_hash_sub_catalog(sub))
    return ShardWriteResult(skipped=1, semantic_hash=_hash_sub_catalog(sub))


def _write_or_delete_orphan_shard(
    *, catalog, orphan_ids: set[str], msg_by_id: dict[str, object],
    config_record: ConfigRecord,
) -> ShardWriteResult:
    """Bring `__orphan__.mo` into sync with unlocated effective msgids.

    Empty input removes the old orphan shard. Otherwise the function writes
    or skips it using the same byte-identity rule as document shards. See
    :class:`ShardWriteResult` for the returned fields.
    """
    target = _shard_target_path(config_record, _ORPHAN_SLUG)
    if not orphan_ids:
        if _unlink_quiet(target):
            return ShardWriteResult(deleted=1)
        return ShardWriteResult()
    sub = _new_sub_catalog(catalog)
    for mid in sorted(orphan_ids):
        message = msg_by_id.get(mid)
        if message is not None:
            _copy_message_into(sub, message)
    new_bytes = _serialize_catalog_to_bytes(sub)
    if _write_shard_if_changed(target, new_bytes):
        return ShardWriteResult(written=1, semantic_hash=_hash_sub_catalog(sub))
    return ShardWriteResult(skipped=1, semantic_hash=_hash_sub_catalog(sub))


# ---------------------------------------------------------------------------
# CLI entry point.
# ---------------------------------------------------------------------------

def _parse_args(argv: list[str] | None = None) -> ConfigRecord:
    """Parse CLI arguments and return the pipeline's configuration record.

    Kept separate from `main()` so the dispatcher stays a thin orchestrator
    (per the project's main-only-orchestrates rule).
    """
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[1] if __doc__ else "",
    )
    ap.add_argument("--language", required=True,
                    help="Locale code (e.g. vi). 'en' is a no-op.")
    ap.add_argument("--srcdir", default="manual",
                    help="RST source dir (default: manual)")
    ap.add_argument("--locale-dir", default="locale",
                    help="Locale root (default: locale)")
    ap.add_argument("--doctree-dir", default="build/doctrees",
                    help="Doctree pickle dir")
    ap.add_argument("--domain", default="blender_manual",
                    help="gettext domain (default: blender_manual)")
    ap.add_argument("--cache-dir", default="build/.translation_cache",
                    help="Persistent shard-mode cache dir (default: build/.translation_cache)")
    ap.add_argument("--shard-root", default="build/.i18n_shards/locale",
                    help="Per-doc shard tree (default: build/.i18n_shards/locale)")
    ap.add_argument("--force-rebuild", action="store_true",
                    help="Bypass tier 1/2/3 short-circuits and always run tier 4.")
    ap.add_argument("--no-touch-rst", action="store_true",
                    help="Do not bump affected RST mtimes after shard updates.")
    ap.add_argument("--verbose", action="store_true",
                    help="Per-shard / per-tier diagnostic logging.")
    ap.add_argument("--quiet", action="store_true",
                    help="Suppress the summary line")
    parsed = ap.parse_args(argv)
    return ConfigRecord(
        language=parsed.language,
        srcdir=Path(parsed.srcdir),
        locale_dir=Path(parsed.locale_dir),
        doctree_dir=Path(parsed.doctree_dir),
        domain=parsed.domain,
        cache_dir=Path(parsed.cache_dir),
        shard_root=Path(parsed.shard_root),
        force_rebuild=parsed.force_rebuild,
        no_touch_rst=parsed.no_touch_rst,
        verbose=parsed.verbose,
        quiet=parsed.quiet,
    )


def main() -> int:
    """Dispatch one locale build and return its process exit status.

    English is the source language and therefore requires no gettext work.
    Other languages delegate all filesystem and cache work to `_main_shard`.
    """
    config_record = _parse_args()

    # Short-circuit for the source language: there is no translation pipeline,
    # so nothing to compile. Keeps `make BF_LANG=en livehtml` clean.
    if config_record.language == "en":
        if not config_record.quiet:
            print("smart_mo_compile: BF_LANG=en, nothing to do")
        return 0

    return _main_shard(config_record)


# ---------------------------------------------------------------------------
# Shard-mode entry point used by every translated runtime build.
# ---------------------------------------------------------------------------


def _shard_tier1_hit(
    config_record: ConfigRecord, cache: dict | None, mtime_ns: int, size: int,
) -> bool:
    """True iff the cached stat() pair matches the current PO *and* shards exist.

    Adds an existence check for the shard tree on top of the legacy tier-1
    rule: a missing shard root (e.g. someone wiped `build/.i18n_shards`)
    must force tier 4, even with a valid cache.
    """
    if cache is None:
        return False
    if cache.get(CacheKey.PO_MTIME_NS) != mtime_ns or cache.get(CacheKey.PO_SIZE) != size:
        return False
    return config_record.shard_lc_dir.is_dir()


def _shard_tier2_hit(
    config_record: ConfigRecord, cache: dict | None, raw_hash: str,
) -> bool:
    """True iff the raw bytes hash matches the cache *and* shards exist."""
    if cache is None:
        return False
    if cache.get(CacheKey.RAW_HASH) != raw_hash:
        return False
    return config_record.shard_lc_dir.is_dir()


def _shard_tier3_hit(
    config_record: ConfigRecord, cache: dict | None,
    semantic_hash: str, layout_hash: str,
) -> bool:
    """True iff semantic/layout hashes match the cache *and* shards exist."""
    if cache is None:
        return False
    if cache.get(CacheKey.SEMANTIC_HASH) != semantic_hash:
        return False
    if cache.get(CacheKey.LAYOUT_HASH) != layout_hash:
        return False
    return config_record.shard_lc_dir.is_dir()


def _refresh_cache_stats(cache: dict, mtime_ns: int, size: int) -> dict:
    """Return a copy of `cache` with refreshed tier-1 (mtime+size) fields."""
    out = dict(cache)
    out[CacheKey.PO_MTIME_NS] = mtime_ns
    out[CacheKey.PO_SIZE] = size
    return out


def _build_shard_cache_payload(
    *, po_mtime_ns: int, po_size: int, raw_hash: str, semantic_hash: str,
    layout_hash: str, new_map: dict[str, str],
    msgid_to_docs: dict[str, set[str]], doc_to_msgids: dict[str, set[str]],
    doc_hashes: dict[str, str],
) -> dict:
    """Assemble the complete v3 cache committed after a successful tier 4.

    `old_map` is the effective translation baseline for the next PO diff;
    `layout_hash` tracks PO `#:` placement data that affects shard routing;
    the two relationship indexes drive partial shard selection; `doc_hashes`
    records the resulting shard state. Callers collect fresh PO stat fields
    after writing the snapshot so tier 1 represents the completed run.
    """
    return {
        CacheKey.VERSION: _CACHE_VERSION,
        CacheKey.PO_MTIME_NS: po_mtime_ns,
        CacheKey.PO_SIZE: po_size,
        CacheKey.RAW_HASH: raw_hash,
        CacheKey.SEMANTIC_HASH: semantic_hash,
        CacheKey.LAYOUT_HASH: layout_hash,
        CacheKey.OLD_MAP: new_map,
        CacheKey.MSGID_TO_DOCS: msgid_to_docs,
        CacheKey.DOC_TO_MSGIDS: doc_to_msgids,
        CacheKey.DOC_HASHES: doc_hashes,
    }


def _log_shard_tier4(
    config_record: ConfigRecord, written: int, skipped: int,
    deleted: int, orphans: int, elapsed: float,
) -> None:
    """Emit the single-line tier-4 summary (verbose mode reuses the same line)."""
    if config_record.quiet:
        return
    print(
        f"smart_mo_compile: tier 4 (shard): wrote={written} skipped={skipped} "
        f"deleted={deleted} orphans={orphans} elapsed={elapsed:.2f}s"
    )


def _log_shard_tier4_partial(
    config_record: ConfigRecord, *, written: int, skipped: int, deleted: int,
    orphans: int, touched: int, changed: int, elapsed: float,
) -> None:
    """Emit the single-line partial tier-4 summary."""
    if config_record.quiet:
        return
    print(
        f"smart_mo_compile: tier 4 (shard): partial wrote={written} "
        f"skipped={skipped} deleted={deleted} touched={touched} "
        f"msgids={changed} orphans={orphans} elapsed={elapsed:.2f}s"
    )


def _shard_tier4_partial_run(
    config_record: ConfigRecord, *, catalog, cache: dict | None,
    current_map: dict[str, str], raw_hash: str, semantic_hash: str,
    layout_hash: str,
) -> bool:
    """Try the cache-guided partial tier-4 path.

    Returns True when the partial path handled the update, False when the
    caller should fall back to the full shard rebuild. The partial path is
    designed for the translator hot loop: one or a few PO msgstr edits with
    stable `#:` locations and an existing v3 cache from a prior full run.

    Routine order:
      1. validate cached translation and relationship indexes;
      2. diff effective translations and resolve changed PO locations;
      3. update copied indexes and touch affected RST files;
      4. write/delete affected doc and orphan shards only;
      5. commit the new snapshot and cache.

    Returning False occurs before shard or cache mutation.
    """
    cache_inputs = _partial_cache_inputs(cache)
    if cache_inputs is None:
        return False
    if cache.get(CacheKey.LAYOUT_HASH) != layout_hash:
        return False
    if not config_record.shard_lc_dir.is_dir():
        return False

    old_map, old_msgid_to_docs, old_doc_to_msgids, old_doc_hashes = cache_inputs
    changed_msgids = _changed_msgids_from_maps(current_map, old_map)
    if not changed_msgids:
        return False

    start = time.monotonic()
    current_changed_docs = _msgids_to_docs_for_subset(
        catalog, changed_msgids, config_record,
    )
    new_msgid_to_docs = _copy_doc_index(old_msgid_to_docs)
    new_doc_to_msgids = _copy_doc_index(old_doc_to_msgids)
    new_doc_hashes = dict(old_doc_hashes)
    affected_docs, orphan_changed = _apply_changed_msgid_doc_moves(
        changed_msgids=changed_msgids,
        current_map=current_map,
        old_msgid_to_docs=old_msgid_to_docs,
        current_changed_docs=current_changed_docs,
        new_msgid_to_docs=new_msgid_to_docs,
        new_doc_to_msgids=new_doc_to_msgids,
    )

    touched = 0
    if not config_record.no_touch_rst:
        touched = _touch_rsts_for_doc_slugs(
            affected_docs, config_record, len(changed_msgids),
        )

    msg_by_id = _index_messages_by_id(catalog)
    written = skipped = deleted = 0
    for slug in sorted(affected_docs):
        doc_msgids = set(new_doc_to_msgids.get(slug, set()))
        result = _write_or_delete_doc_shard(
            catalog=catalog,
            slug=slug,
            doc_msgids=doc_msgids,
            msg_by_id=msg_by_id,
            config_record=config_record,
        )
        written += result.written
        skipped += result.skipped
        deleted += result.deleted
        if result.semantic_hash is None:
            new_doc_hashes.pop(slug, None)
        else:
            new_doc_hashes[slug] = result.semantic_hash

    orphan_ids = {
        mid for mid in current_map
        if mid not in new_msgid_to_docs
    }
    if orphan_changed:
        result = _write_or_delete_orphan_shard(
            catalog=catalog,
            orphan_ids=orphan_ids,
            msg_by_id=msg_by_id,
            config_record=config_record,
        )
        written += result.written
        skipped += result.skipped
        deleted += result.deleted
        if result.semantic_hash is None:
            new_doc_hashes.pop(_ORPHAN_SLUG, None)
        else:
            new_doc_hashes[_ORPHAN_SLUG] = result.semantic_hash

    _delete_stale_global_mo(config_record.legacy_mo_path)
    _write_po_snapshot(catalog, config_record.snapshot_path)

    po_stat_after = config_record.po_path.stat()
    payload = _build_shard_cache_payload(
        po_mtime_ns=po_stat_after.st_mtime_ns,
        po_size=po_stat_after.st_size,
        raw_hash=raw_hash,
        semantic_hash=semantic_hash,
        layout_hash=layout_hash,
        new_map=current_map,
        msgid_to_docs=new_msgid_to_docs,
        doc_to_msgids=new_doc_to_msgids,
        doc_hashes=new_doc_hashes,
    )
    _write_cache(config_record.cache_path, payload)
    _log_shard_tier4_partial(
        config_record,
        written=written,
        skipped=skipped,
        deleted=deleted,
        orphans=len(orphan_ids),
        touched=touched,
        changed=len(changed_msgids),
        elapsed=time.monotonic() - start,
    )
    return True


def _shard_tier4_run(
    config_record: ConfigRecord, *, cache: dict | None, catalog,
    current_map: dict[str, str], raw_hash: str, semantic_hash: str,
    layout_hash: str,
) -> int:
    """Tier 4 of the shard path: load PO, split into shards, write/skip/delete.

    All work is content-addressed: shards whose bytes are byte-identical on
    disk are skipped without touching mtime, so unchanged docs are never
    invalidated. The legacy global .mo (if any) is unlinked.

    The RST-touch step runs BEFORE the snapshot/cache is refreshed. Order
    matters: calculate changed shards -> touch affected RSTs -> emit shards ->
    write fresh snapshot -> update cache. If interrupted, the old cache stays
    stale and the touch is idempotent on the next run.
    """
    start = time.monotonic()

    if (not config_record.force_rebuild and _shard_tier4_partial_run(
            config_record, catalog=catalog, cache=cache,
            current_map=current_map, raw_hash=raw_hash,
            semantic_hash=semantic_hash, layout_hash=layout_hash)):
        return 0

    shards, msgid_to_docs, doc_to_msgids, orphan_count = _catalog_to_shards(
        catalog, config_record,
    )
    doc_hashes = _build_doc_hashes(shards)

    if not config_record.no_touch_rst:
        # Sphinx only discovers catalog dependencies from .po files, while our
        # runtime shard tree is generated .mo-only. Touching affected source
        # files keeps live rebuilds working even when a Sphinx version does not
        # register those generated .mo files as dependencies.
        touched = _touch_rsts_for_doc_hash_diff(
            doc_hashes, cache, config_record,
        )
        if touched is None:
            _touch_rsts_for_snapshot_diff(catalog, config_record)

    written, skipped, deleted = _emit_shards(shards, config_record)
    _delete_stale_global_mo(config_record.legacy_mo_path)

    _write_po_snapshot(catalog, config_record.snapshot_path)

    po_stat_after = config_record.po_path.stat()
    payload = _build_shard_cache_payload(
        po_mtime_ns=po_stat_after.st_mtime_ns,
        po_size=po_stat_after.st_size,
        raw_hash=raw_hash,
        semantic_hash=semantic_hash,
        layout_hash=layout_hash,
        new_map=current_map,
        msgid_to_docs=msgid_to_docs,
        doc_to_msgids=doc_to_msgids,
        doc_hashes=doc_hashes,
    )
    _write_cache(config_record.cache_path, payload)
    _log_shard_tier4(config_record, written, skipped, deleted, orphan_count,
                     time.monotonic() - start)
    return 0


def _main_shard(config_record: ConfigRecord) -> int:
    """Validate one locale and serialize its cache/shard update with a lock.

    A missing PO is a supported no-op. Otherwise this routine creates build
    state directories, takes `<cache_dir>/<lang>.lock`, and delegates all
    cache decisions to `_shard_locked_body`. The per-language lock prevents
    overlapping autobuild triggers from publishing inconsistent artifacts.
    """
    if not config_record.po_path.is_file():
        if not config_record.quiet:
            print(
                f"smart_mo_compile: no .po at {config_record.po_path}, "
                "skipping"
            )
        return 0

    config_record.cache_dir.mkdir(parents=True, exist_ok=True)
    config_record.shard_root.mkdir(parents=True, exist_ok=True)

    with open(config_record.lock_path, "w") as lock_fp:
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_EX)
        return _shard_locked_body(config_record)


def _shard_locked_body(config_record: ConfigRecord) -> int:
    """Evaluate cache tiers in cost order while holding the language lock.

    Tier 1 compares stat metadata; tier 2 hashes raw PO bytes; tier 3 parses
    the catalog and hashes effective translations plus their shard layout.
    Each hit refreshes only cache fields learned at that tier. A miss
    delegates the already-loaded catalog and hashes to tier 4, avoiding
    duplicate work.

    On the first v3-cache run, stale global-MO doctree state and legacy PO
    sidecars are removed before tier evaluation.
    """
    po_stat = config_record.po_path.stat()
    po_mtime_ns = po_stat.st_mtime_ns
    po_size = po_stat.st_size
    cache = _read_cache(config_record.cache_path)
    first_shard_run = cache is None
    if first_shard_run:
        _purge_stale_environment_pickle(
            config_record.doctree_dir, quiet=config_record.quiet,
        )
        _purge_legacy_sidecars(
            config_record.po_path, quiet=config_record.quiet,
        )

    if (not config_record.force_rebuild
            and _shard_tier1_hit(
                config_record, cache, po_mtime_ns, po_size,
            )):
        if not config_record.quiet:
            print("smart_mo_compile: PO unchanged (tier 1: mtime+size, shard)")
        return 0

    raw_hash = _sha256_file(config_record.po_path)
    if (not config_record.force_rebuild
            and _shard_tier2_hit(config_record, cache, raw_hash)):
        assert cache is not None  # narrowed by _shard_tier2_hit
        _write_cache(
            config_record.cache_path,
            _refresh_cache_stats(cache, po_mtime_ns, po_size),
        )
        if not config_record.quiet:
            print("smart_mo_compile: PO unchanged (tier 2: raw hash, shard)")
        return 0

    catalog = load_po(str(config_record.po_path))
    current_map = _msgid_to_translation(catalog)
    semantic_hash = _hash_catalog(catalog)
    layout_hash = _hash_shard_layout(catalog, config_record)
    if (not config_record.force_rebuild
            and _shard_tier3_hit(
                config_record, cache, semantic_hash, layout_hash,
            )):
        assert cache is not None  # narrowed by _shard_tier3_hit
        refreshed = _refresh_cache_stats(cache, po_mtime_ns, po_size)
        refreshed[CacheKey.RAW_HASH] = raw_hash
        refreshed[CacheKey.LAYOUT_HASH] = layout_hash
        _write_cache(config_record.cache_path, refreshed)
        if not config_record.quiet:
            print("smart_mo_compile: PO unchanged (tier 3: semantic/layout hash, shard)")
        return 0

    return _shard_tier4_run(
        config_record, cache=cache, catalog=catalog,
        current_map=current_map, raw_hash=raw_hash,
        semantic_hash=semantic_hash, layout_hash=layout_hash,
    )


# Standard `python file.py` entry point. argparse handles --help; we propagate
# the int return code via sys.exit so shell `&&` chains work as expected.
if __name__ == "__main__":
    sys.exit(main())
