"""PO file watcher — rebuilds the search index and HTML when any PO changes.

``MultiPOWatcher`` is the primary class.  A single daemon thread:

  * auto-discovers every ``locale/<lang>/LC_MESSAGES/blender_manual.po`` at
    startup and on each subsequent poll (so newly added languages are picked
    up without restarting the server);
  * compares the PO mtime against the search-index mtime at startup — if the
    PO is newer the first poll fires *immediately* (no sleep) to incorporate
    edits made before the server was started;
  * diffs the new PO content against an in-memory snapshot to find exactly
    which RST files changed, then passes only those to sphinx-build so only
    the affected pages (e.g. ``snapping.html``) are rebuilt;
  * rebuilds the search-index pickle FIRST (reads the PO directly, no Sphinx
    run needed) so search results are hot within ~30 s of a PO save;
  * rebuilds HTML in a background thread so the poll loop is not blocked.

``POWatcher`` (single-language) is retained for callers that start one
watcher per language; it delegates to the same helpers.
"""

from __future__ import annotations

import logging
import subprocess
import sys
import threading
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional imports — fall back gracefully when unavailable.
# ---------------------------------------------------------------------------
try:
    from translations.smart_mo_compile import ConfigRecord as _ConfigRecord
    _HAS_CONFIG_RECORD = True
except (ImportError, SystemExit):
    _ConfigRecord = None  # type: ignore[assignment,misc]
    _HAS_CONFIG_RECORD = False

try:
    from common.constants import (  # type: ignore[import-not-found]
        LC_MESSAGES as _LC_MESSAGES,
        LOCALE_DIR as _LOCALE_DIR,
        PO_FILENAME as _PO_FILENAME,
        RST_SOURCE_DIR as _RST_SOURCE_DIR,
        SEARCH_INDEX_FILENAME as _SEARCH_INDEX_FILENAME,
    )
except ImportError:
    _LC_MESSAGES = "LC_MESSAGES"
    _LOCALE_DIR = "locale"
    _PO_FILENAME = "blender_manual.po"
    _RST_SOURCE_DIR = "manual"
    _SEARCH_INDEX_FILENAME = "searchindex.pkl.gz"

try:
    if __package__:
        from .po_parser import read_po_file as _read_po_file
    else:
        from search.po_parser import read_po_file as _read_po_file  # type: ignore[no-redef]
    _HAS_PO_PARSER = True
except ImportError:
    _read_po_file = None  # type: ignore[assignment]
    _HAS_PO_PARSER = False

try:
    from debug_log import (  # type: ignore[import-not-found]
        log_check_interval_seconds as _log_check_interval_seconds,
        maybe_trim_live_log as _maybe_trim_live_log,
    )
    _HAS_LOG_TRIM = True
except ImportError:
    _log_check_interval_seconds = None  # type: ignore[assignment]
    _maybe_trim_live_log = None  # type: ignore[assignment]
    _HAS_LOG_TRIM = False


# ---------------------------------------------------------------------------
# Type alias: {msgid: (msgstr, [rst_rel_path, ...])}
# ---------------------------------------------------------------------------
_Snapshot = dict[str, tuple[str, list[str]]]

_LOG_CONFIG_RELATIVE_PATH = Path("tools/config/logging_config.ini")
_DISABLED_LOG_CHECK_INTERVAL = 0.0
_INITIAL_LOG_CHECK_DEADLINE = 0.0


# ---------------------------------------------------------------------------
# PO snapshot helpers
# ---------------------------------------------------------------------------

def _load_po_snapshot(po_path: Path) -> _Snapshot:
    """Parse *po_path* into ``{msgid: (msgstr, [rst_rel_path, ...])}``."""
    if not _HAS_PO_PARSER or _read_po_file is None:
        return {}
    try:
        entries = _read_po_file(po_path)
        return {e.msgid: (e.msgstr, [loc[0] for loc in e.locations]) for e in entries}
    except Exception as exc:
        logging.debug("[POWatcher] snapshot load failed for %s: %s", po_path.name, exc)
        return {}


def _find_changed_rst_paths(old: _Snapshot, new: _Snapshot) -> set[str]:
    """Return RST paths whose ``msgstr`` changed between *old* and *new*.

    Returns an empty set when *old* is empty (no baseline — caller should
    fall back to a full incremental build).
    """
    if not old:
        return set()
    changed: set[str] = set()
    for msgid, (new_msgstr, rst_paths) in new.items():
        old_msgstr, _ = old.get(msgid, ("__MISSING__", []))
        if new_msgstr != old_msgstr:
            changed.update(rst_paths)
    for msgid, (_, rst_paths) in old.items():
        if msgid not in new:
            changed.update(rst_paths)
    return changed


# ---------------------------------------------------------------------------
# ConfigRecord factory
# ---------------------------------------------------------------------------

def _config_for(project_root: Path, lang: str):
    """Return a ConfigRecord for *lang*, or None if the import is unavailable."""
    if not _HAS_CONFIG_RECORD or _ConfigRecord is None:
        return None
    try:
        return _ConfigRecord.from_project(project_root, lang)
    except Exception as exc:
        logging.debug("[POWatcher] ConfigRecord.from_project failed for %s: %s", lang, exc)
        return None


# ---------------------------------------------------------------------------
# Build steps
# ---------------------------------------------------------------------------

def _rebuild_index(
    po_path: Path,
    rst_root: Path,
    build_dir: Path,
    lang: str,
    cfg=None,
) -> None:
    """Run ``index_builder.py`` as a child process.

    Reads the PO file directly — no Sphinx run required.  When *cfg* is
    provided its conf.py-derived values override index_builder's defaults.
    """
    script = Path(__file__).parent / "index_builder.py"
    cmd = [
        sys.executable, str(script),
        "--po",    str(po_path),
        "--rst",   str(rst_root),
        "--build", str(build_dir),
        "--lang",  lang,
    ]
    if cfg is not None:
        cmd += [
            f"--rst-suffix={cfg.rst_suffix}",
            f"--html-suffix={cfg.html_page_suffix}",
            f"--index-filename={cfg.search_index_filename}",
        ]
    subprocess.run(cmd, check=False)


def _rebuild_html(
    project_root: Path,
    build_dir: Path,
    lang: str,
    po_path: Path,
    cfg=None,
    changed_rst_paths: set[str] | None = None,
) -> None:
    """Recompile MO shards then run a targeted (or full) Sphinx HTML build.

    Parameters
    ----------
    changed_rst_paths
        Non-empty set  → build only those RST files (e.g. ``snapping.rst``).
        ``None`` or empty set → full incremental build.
    """
    if not po_path.exists():
        logging.warning("[POWatcher] PO file missing, skipping HTML rebuild: %s", po_path)
        return

    if cfg is None:
        cfg = _config_for(project_root, lang)
    if cfg is None:
        logging.warning(
            "[POWatcher] ConfigRecord unavailable; skipping HTML rebuild for %s", lang,
        )
        return

    # Step 1: recompile PO → per-document MO shards
    if cfg.smart_mo_script is not None and cfg.smart_mo_script.exists():
        subprocess.run(
            [
                sys.executable, str(cfg.smart_mo_script),
                f"--language={cfg.language}",
                f"--cache-dir={cfg.cache_dir}",
                f"--shard-root={cfg.shard_root}",
                f"--doctree-dir={cfg.doctree_dir}",
                "--no-touch-rst",
            ],
            check=False,
            cwd=str(project_root),
        )

    # Step 2: Sphinx HTML build — targeted when changed files are known
    cmd = [
        cfg.sphinx_build_cmd,
        "-b", cfg.sphinx_builder,
        str(cfg.srcdir), str(build_dir),
        "-j", cfg.sphinx_jobs,
        "-D", f"language={cfg.language}",
        "-d", str(cfg.doctree_dir),
        "-q",
    ]
    if changed_rst_paths:
        resolved: list[str] = []
        for rst_rel in sorted(changed_rst_paths):
            # rst_rel is e.g. "manual/editors/3dview/controls/snapping.rst"
            full = cfg.srcdir.parent / rst_rel
            if full.exists():
                resolved.append(str(full))
        if resolved:
            cmd += resolved
            logging.info(
                "[POWatcher] targeted HTML rebuild: %s",
                ", ".join(Path(p).name for p in resolved),
            )
    subprocess.run(cmd, check=False, cwd=str(project_root))


# ---------------------------------------------------------------------------
# Per-language state used by MultiPOWatcher
# ---------------------------------------------------------------------------

class _LangState:
    """Mutable state for one language tracked by MultiPOWatcher."""
    __slots__ = ("po_path", "last_mtime", "snapshot")

    def __init__(self, po_path: Path, last_mtime: float, snapshot: _Snapshot) -> None:
        self.po_path = po_path
        self.last_mtime = last_mtime
        self.snapshot = snapshot


# ---------------------------------------------------------------------------
# MultiPOWatcher — single thread, all languages
# ---------------------------------------------------------------------------

class MultiPOWatcher(threading.Thread):
    """Single daemon thread watching ALL locale/<lang>/LC_MESSAGES/blender_manual.po.

    Parameters
    ----------
    project_root : repository root (contains ``locale/`` and ``manual/``)
    build_dir    : top-level build directory (e.g. ``build/``);
                   per-language sub-dirs are derived as ``build/<lang>/``
    invalidate   : callable(lang) that evicts the in-memory search-index cache
    interval     : poll interval in seconds (default 5)
    rebuild_html : when True (default) a PO change also triggers a targeted
                   Sphinx HTML rebuild.  Set False under ``make liveall``,
                   where sphinx-autobuild already rebuilds HTML — leaving it
                   True there would double-build the same ``build/<lang>/``
                   output and doctrees.  The search-index rebuild always runs.

    The watcher re-scans ``locale/`` on every poll, so languages added after
    startup are automatically included without restarting the server.
    """

    daemon = True

    def __init__(
        self,
        project_root: Path,
        build_dir: Path,
        invalidate,
        interval: int = 5,
        rebuild_html: bool = True,
    ) -> None:
        super().__init__(name="MultiPOWatcher")
        self.project_root = project_root
        self.build_dir = build_dir
        self.invalidate = invalidate
        self.interval = interval
        self.rebuild_html = rebuild_html
        self.rst_root = project_root / _RST_SOURCE_DIR
        self._log_config_path = project_root / _LOG_CONFIG_RELATIVE_PATH
        self._log_check_interval = self._resolve_log_check_interval()
        self._next_log_check = _INITIAL_LOG_CHECK_DEADLINE

        # Per-language state; populated by _sync_langs()
        self._langs: dict[str, _LangState] = {}
        self._sync_langs()

    # ------------------------------------------------------------------
    def _discover_po_files(self) -> dict[str, Path]:
        """Return ``{lang: po_path}`` for every PO found under ``locale/``."""
        found: dict[str, Path] = {}
        locale_root = self.project_root / _LOCALE_DIR
        if not locale_root.is_dir():
            return found
        for entry in sorted(locale_root.iterdir()):
            if not entry.is_dir():
                continue
            po = entry / _LC_MESSAGES / _PO_FILENAME
            if po.is_file():
                found[entry.name] = po
        return found

    def _sync_langs(self) -> None:
        """Add newly discovered languages to ``_langs``; ignore already-tracked ones."""
        for lang, po_path in self._discover_po_files().items():
            if lang in self._langs:
                continue  # already tracked

            try:
                po_mtime = po_path.stat().st_mtime
            except FileNotFoundError:
                po_mtime = 0.0

            try:
                idx_mtime = (self.build_dir / lang / _SEARCH_INDEX_FILENAME).stat().st_mtime
            except FileNotFoundError:
                idx_mtime = 0.0

            # If the PO is newer than the index, set last_mtime=0 so the
            # first _poll() call fires an immediate rebuild (no sleep).
            if po_mtime > idx_mtime:
                last_mtime = 0.0
                logging.info(
                    "[MultiPOWatcher] %s/%s newer than index — "
                    "rebuild queued for startup",
                    lang, _PO_FILENAME,
                )
            else:
                last_mtime = po_mtime

            # Load snapshot only when we won't rebuild immediately.
            snapshot = _load_po_snapshot(po_path) if last_mtime != 0.0 else {}
            self._langs[lang] = _LangState(po_path, last_mtime, snapshot)
            logging.debug("[MultiPOWatcher] tracking %s", lang)

    # ------------------------------------------------------------------
    def run(self) -> None:
        # First check fires immediately (no sleep) so startup-stale indexes
        # are rebuilt before the first user request, not up to `interval` s later.
        self._poll_all()
        self._maybe_trim_log()
        while True:
            time.sleep(self.interval)
            self._sync_langs()   # pick up new languages added after startup
            self._poll_all()
            self._maybe_trim_log()

    def _resolve_log_check_interval(self) -> float:
        if not _HAS_LOG_TRIM or _log_check_interval_seconds is None:
            return _DISABLED_LOG_CHECK_INTERVAL
        return _log_check_interval_seconds(self._log_config_path)

    def _maybe_trim_log(self) -> None:
        """Dispatch a live trim no more often than the configured cadence."""
        if not _HAS_LOG_TRIM or _maybe_trim_live_log is None:
            return
        is_enabled = self._log_check_interval > _DISABLED_LOG_CHECK_INTERVAL
        current_time = time.monotonic()
        is_due = current_time >= self._next_log_check
        if not (is_enabled and is_due):
            return
        self._next_log_check = current_time + self._log_check_interval
        _maybe_trim_live_log(self._log_config_path)

    def _poll_all(self) -> None:
        """Check every tracked language for PO mtime changes."""
        for lang, state in list(self._langs.items()):
            try:
                mtime = state.po_path.stat().st_mtime
            except FileNotFoundError:
                continue
            if mtime == state.last_mtime:
                continue
            self._on_change(lang, state, mtime)

    def _on_change(self, lang: str, state: _LangState, new_mtime: float) -> None:
        """Handle a detected PO mtime change for *lang*."""
        state.last_mtime = new_mtime
        cfg = _config_for(self.project_root, lang)

        new_snapshot = _load_po_snapshot(state.po_path)
        changed_rst: set[str] | None = (
            _find_changed_rst_paths(state.snapshot, new_snapshot) or None
        )
        state.snapshot = new_snapshot

        if changed_rst:
            logging.info(
                "[MultiPOWatcher] %s/%s — %d RST file(s) changed: %s",
                lang, _PO_FILENAME, len(changed_rst),
                ", ".join(sorted(changed_rst)[:3]) + ("…" if len(changed_rst) > 3 else ""),
            )
        else:
            logging.info(
                "[MultiPOWatcher] %s/%s changed (full rebuild)", lang, _PO_FILENAME,
            )

        # 1. Rebuild search index first — no Sphinx run needed.
        _rebuild_index(
            state.po_path, self.rst_root,
            self.build_dir / lang, lang, cfg,
        )
        self.invalidate(lang)
        logging.info("[MultiPOWatcher] search index hot-swapped for %s", lang)

        # 2. Rebuild HTML in background — targeted to changed RST files only.
        # Skipped when rebuild_html is False (e.g. under 'make liveall', where
        # sphinx-autobuild already owns HTML rebuilds for this build/<lang>/).
        if not self.rebuild_html:
            logging.debug(
                "[MultiPOWatcher] rebuild_html=False; leaving HTML to the live "
                "builder for %s", lang,
            )
            return
        threading.Thread(
            target=_rebuild_html,
            args=(
                self.project_root, self.build_dir / lang,
                lang, state.po_path, cfg, changed_rst,
            ),
            name=f"MultiPOWatcher-html-{lang}",
            daemon=True,
        ).start()
        logging.info(
            "[MultiPOWatcher] HTML rebuild started in background for %s", lang,
        )


# ---------------------------------------------------------------------------
# POWatcher — single-language wrapper (kept for backward compatibility)
# ---------------------------------------------------------------------------

class POWatcher(threading.Thread):
    """Watch one language's PO file and rebuild its search index when it changes.

    A daemon thread that polls a single ``blender_manual.po`` every *interval*
    seconds. On each detected change it (1) rebuilds that language's search
    index synchronously, (2) evicts the in-memory cache via the *invalidate*
    callback so the next query reads the fresh index, and (3) kicks off a
    background Sphinx HTML rebuild — targeted to just the changed RST files when
    they can be determined, otherwise a full rebuild.

    Prefer :class:`MultiPOWatcher` for new code: a single thread there watches
    every language and also auto-discovers languages added after startup. This
    class is retained for existing callers that construct one watcher per
    language, and delegates to the same module-level helpers
    (``_rebuild_index``, ``_rebuild_html``, ``_load_po_snapshot``).

    Notes:
        - Runs as a ``daemon`` thread, so it does not block interpreter exit.
        - The index rebuild is synchronous (blocks the poll loop briefly); the
          HTML rebuild runs in its own short-lived thread so the watcher keeps
          polling.
        - Not thread-safe to share across threads; create one per language.
    """

    daemon = True

    def __init__(
        self,
        po_path: Path,
        rst_root: Path,
        build_dir: Path,
        lang: str,
        invalidate,
        project_root: Path | None = None,
        interval: int = 5,
    ) -> None:
        """Initialise the watcher and decide whether a startup rebuild is due.

        Args:
            po_path: Path to the language's ``blender_manual.po`` to watch.
            rst_root: Root of the RST sources (``manual/``), used to resolve
                section anchors during the index rebuild.
            build_dir: This language's output directory (``build/<lang>/``);
                the search index is written/read here.
            lang: Language code (e.g. ``"vi"``).
            invalidate: Callback ``(lang: str) -> None`` that evicts *lang* from
                the in-memory index cache after a successful rebuild.
            project_root: Repository root; defaults to ``po_path.parents[3]``
                (``locale/<lang>/LC_MESSAGES/blender_manual.po`` → repo root).
            interval: Poll interval in seconds (default 5).

        Notes:
            If the PO file is newer than the existing index (or the index is
            missing), ``_last_mtime`` is set to ``0.0`` so the first
            :meth:`run` poll fires an immediate rebuild instead of waiting for
            the next edit. The PO snapshot is loaded eagerly only when no such
            startup rebuild is queued, since a queued rebuild reloads it anyway.
        """
        super().__init__(name=f"POWatcher-{lang}")
        self.po_path = po_path
        self.rst_root = rst_root
        self.build_dir = build_dir
        self.lang = lang
        self.invalidate = invalidate
        self.project_root = project_root or po_path.parents[3]
        self.interval = interval

        try:
            po_mtime = po_path.stat().st_mtime
        except FileNotFoundError:
            po_mtime = 0.0

        try:
            idx_mtime = (build_dir / _SEARCH_INDEX_FILENAME).stat().st_mtime
        except FileNotFoundError:
            idx_mtime = 0.0

        if po_mtime > idx_mtime:
            logging.info(
                "[POWatcher] %s is newer than index — rebuild queued for startup",
                po_path.name,
            )
            self._last_mtime: float = 0.0
        else:
            self._last_mtime = po_mtime

        self._snapshot: _Snapshot = _load_po_snapshot(po_path) if self._last_mtime != 0.0 else {}

    def run(self) -> None:
        """Poll loop: check once immediately, then every *interval* seconds.

        The immediate first check lets a startup-stale index (see ``__init__``)
        be rebuilt before the first user request rather than up to *interval*
        seconds later. Runs until the process exits (daemon thread).
        """
        self._check()
        while True:
            time.sleep(self.interval)
            self._check()

    def _check(self) -> None:
        """Rebuild index + HTML if the PO file changed since the last check.

        Returns early (no-op) when the PO file is missing or its mtime is
        unchanged. On a real change it diffs the previous PO snapshot against
        the current one to find which RST files were affected, rebuilds the
        search index synchronously, invalidates the cache, then starts a
        background HTML rebuild scoped to those RST files (or a full rebuild
        when the changed set cannot be determined).
        """
        try:
            mtime = self.po_path.stat().st_mtime
        except FileNotFoundError:
            return
        if mtime == self._last_mtime:
            return
        self._last_mtime = mtime
        cfg = _config_for(self.project_root, self.lang)

        new_snapshot = _load_po_snapshot(self.po_path)
        changed_rst: set[str] | None = (
            _find_changed_rst_paths(self._snapshot, new_snapshot) or None
        )
        self._snapshot = new_snapshot

        if changed_rst:
            logging.info(
                "[POWatcher] %s — %d RST file(s): %s",
                self.po_path.name, len(changed_rst),
                ", ".join(sorted(changed_rst)[:3]) + ("…" if len(changed_rst) > 3 else ""),
            )
        else:
            logging.info("[POWatcher] %s changed (full rebuild)", self.po_path.name)

        _rebuild_index(self.po_path, self.rst_root, self.build_dir, self.lang, cfg)
        self.invalidate(self.lang)
        logging.info("[POWatcher] search index hot-swapped for %s", self.lang)

        threading.Thread(
            target=_rebuild_html,
            args=(self.project_root, self.build_dir, self.lang,
                  self.po_path, cfg, changed_rst),
            name=f"POWatcher-html-{self.lang}",
            daemon=True,
        ).start()
        logging.info("[POWatcher] HTML rebuild started in background for %s", self.lang)
