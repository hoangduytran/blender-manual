"""Share static/image assets across language builds (one canonical copy).

Each translated build writes a full copy of ``_static`` (~10 MB) and ``_images``
(~250 MB) into ``build/<lang>/``. The image set is byte-for-byte identical across
languages (the same English screenshots), so copying it per language wastes both
disk *and* build time.

This extension centralises every shared asset under ``build/shared/`` and lets a
language reference it instead of re-copying:

``_images`` (the expensive, fully-shared tree)
    Handled at ``builder-inited`` for a **build-time** win:
    ``build/<lang>/_images`` is a real directory, and each image inside it is a
    per-file link to ``build/shared/_images``. Sphinx's image-copy step is patched
    to write only the files that are not already in the shared tree. The first
    language seeds the shared tree; every later language copies nothing.

``_static`` (mostly shared, a few genuinely per-language JS files)
    Handled at ``build-finished`` with per-file sharing: files become links to the
    shared copy even when Sphinx generated different bytes for that language.
    A language that needs a local ``_static`` file must provide a same-path
    override under ``locale/<lang>/_static``.

Per-language overrides
    A language may override or add an asset by dropping a file under
    ``locale/<lang>/_images/`` or ``locale/<lang>/_static/`` (relative path mirrors
    the shared tree). Applied at ``build-finished``: the symlink is **unlinked
    first**, then the real bytes are copied over it (a plain copy would follow the
    symlink and corrupt the shared base for every language). A file with no shared
    counterpart is copied in as a new asset when ``shared_assets_copy_new`` is set.
    English is treated the same as every other language: ``locale/en/_images`` may
    override a shared image when needed.

No ``foo.<lang>.png`` convention
    ``manual/conf.py`` pins ``figure_language_filename`` to ``"{root}{ext}"`` for
    this shared-assets model. Image localization is intentionally same-path
    ``locale/<lang>/_images`` override, not Sphinx's language-suffixed filename
    lookup.

Resolution is purely filesystem-level: the emitted HTML keeps its existing
``../_images/foo.png`` references and resolves through the symlinks, so there is no
FOUC and crawlers / no-JS / print all work. ``make build`` builds languages
sequentially, so there is no write race on the shared tree.

Cross-platform: symlinks are used where the OS allows them unprivileged
(Linux/macOS, and Windows with Developer Mode); otherwise ``link_or_copy`` falls
back to a hardlink (NTFS, same volume) and finally to a plain copy, so the build
stays correct everywhere and only loses the disk/time saving in the worst case.
"""

from __future__ import annotations

from dataclasses import dataclass
import filecmp
import os
import shutil
import sys
from pathlib import Path
from time import perf_counter

from sphinx.environment.adapters.asset import ImageAdapter
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.display import status_iterator
from sphinx.util.osutil import copyfile, ensuredir

# tools/ is not on sys.path during a Sphinx build (only build_files/extensions
# is, via conf.py). Add it so extensions can reuse common tool helpers.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_TOOLS = _REPO_ROOT / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from common.utils import format_duration, timing  # type: ignore[import-not-found]  # noqa: E402

logger = logging.getLogger(__name__)

_HTML_BUILDERS = frozenset({"html", "dirhtml", "singlehtml"})

# Per-file asset operations (one or two lines per image/static file) are logged
# only at -vv (verbosity >= 2). The Makefile always passes -v (verbosity 1) for
# Sphinx's own progress output, so the threshold is -vv to keep the default build
# quiet and fast — thousands of INFO lines is a real wall-clock cost on large
# image sets (~6.2k lines for 3107 images). Set once in main at builder-inited.
_PER_FILE_LOG_MIN_VERBOSITY = 2
_per_file_verbosity = 0


def _set_per_file_verbosity(value: int) -> None:
    global _per_file_verbosity
    _per_file_verbosity = value


def _per_file_logging_enabled() -> bool:
    return _per_file_verbosity >= _PER_FILE_LOG_MIN_VERBOSITY


@dataclass(frozen=True)
class _ImageCopyStats:
    total: int = 0
    copied: int = 0
    already_shared: int = 0
    linked: int = 0


def _format_image_copy_timing(stats: _ImageCopyStats) -> str:
    return (
        f"images={stats.total} copied={stats.copied} "
        f"already-shared={stats.already_shared} linked={stats.linked}"
    )


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _shared_root(app) -> Path:
    """Absolute ``build/shared`` root (configurable, default sibling of outdir)."""
    configured = app.config.shared_assets_root
    if configured:
        root = Path(configured)
        if not root.is_absolute():
            root = (Path(app.confdir) / root).resolve()
        return root
    return Path(app.outdir).parent / "shared"


def _override_root(app) -> Path:
    """Absolute root under which ``<lang>/<subdir>`` override files live."""
    configured = app.config.shared_assets_override_root
    root = Path(configured) if configured else Path("../locale")
    if not root.is_absolute():
        root = (Path(app.confdir) / root).resolve()
    return root


def _current_lang(app) -> str:
    return os.environ.get("BF_LANG", app.config.language) or "en"


def _html_static_sources(app):
    """Yield ``(absolute_source_file, relative_path)`` for every html_static_path file.

    These theme/_static assets (CSS/JS/fonts/logo from ``build_files/theme``) are
    language-independent — the same bytes for every language — so the shared copy
    can be refreshed straight from the source.
    """
    for entry in getattr(app.config, "html_static_path", None) or []:
        root = Path(entry)
        if not root.is_absolute():
            root = (Path(app.confdir) / root).resolve()
        if root.is_dir():
            yield from _iter_files(root)
        elif root.is_file():
            yield root, Path(root.name)


def _sync_shared_theme_static(app, shared_static: Path) -> int:
    """Refresh shared ``_static`` theme assets from the html_static_path source.

    Makes live theme edits deterministic and language-agnostic: when a source
    asset (e.g. ``build_files/theme/css/theme_overrides.css``) changes, the shared
    copy is updated directly from source. Every language links to the shared tree,
    so the edit reaches them all without relying on Sphinx writing a changed file
    through a per-language symlink. Returns the number of files refreshed.

    Only language-independent html_static_path assets are touched. Generated,
    genuinely per-language ``_static`` files (``documentation_options.js`` etc.)
    are not under html_static_path and are left to the per-language dedup.
    """
    refreshed = 0
    for src_abs, rel in _html_static_sources(app):
        shared_file = shared_static / rel
        if shared_file.exists() and filecmp.cmp(src_abs, shared_file, shallow=False):
            continue
        ensuredir(shared_file.parent)
        if shared_file.exists() or shared_file.is_symlink():
            shared_file.unlink()
        shutil.copy2(src_abs, shared_file)
        refreshed += 1
    return refreshed


def _is_active(app) -> bool:
    if not app.config.shared_assets_enabled:
        return False
    return app.builder.name in _HTML_BUILDERS


# ---------------------------------------------------------------------------
# Linking primitives
# ---------------------------------------------------------------------------

def link_or_copy(src: Path, dst: Path, mode: str = "auto") -> str:
    """Point *dst* at *src* as cheaply as the platform allows.

    Returns the mechanism actually used: ``"symlink"``, ``"hardlink"`` or
    ``"copy"``. *dst* must not already exist (callers unlink first).
    """
    if mode in ("auto", "symlink"):
        try:
            os.symlink(os.path.relpath(src, dst.parent), dst)
            return "symlink"
        except (OSError, NotImplementedError):
            if mode == "symlink":
                raise
    if mode in ("auto", "hardlink"):
        try:
            os.link(src, dst)
            return "hardlink"
        except OSError:
            if mode == "hardlink":
                raise
    shutil.copy2(src, dst)
    return "copy"


def _remove(path: Path) -> None:
    """Remove *path* whether it is a symlink, file or directory."""
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _iter_files(root: Path):
    """Yield ``(absolute_path, relative_path)`` for every file under *root*."""
    if not root.is_dir():
        return
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            abs_path = Path(dirpath) / name
            yield abs_path, abs_path.relative_to(root)


def _progress_text(index: int, total: int) -> str:
    """Return one stable percentage label for per-file progress traces."""
    if total <= 0:
        return "[0/0 100.00%]"
    width = len(str(total))
    percent = (index / total) * 100.0
    return f"[{index:>{width}}/{total} {percent:6.2f}%]"


def _log_asset_step(
    subdir: str,
    action: str,
    index: int,
    total: int,
    rel: Path | str,
    *,
    src: Path | str | None = None,
    dst: Path | str | None = None,
    method: str | None = None,
) -> None:
    """Log one file-level shared-assets operation through Sphinx logging.

    Suppressed unless the build is verbose (-v/-vv); summary counts are logged
    separately by the callers and always shown.
    """
    if not _per_file_logging_enabled():
        return
    route = ""
    if src is not None and dst is not None:
        route = f" {src} -> {dst}"
    elif src is not None:
        route = f" {src}"
    elif dst is not None:
        route = f" {dst}"
    if method is not None:
        route = f"{route} via={method}"
    logger.info(
        "shared_assets: %s %s %s %s%s",
        subdir,
        action,
        _progress_text(index, total),
        rel,
        route,
    )


# ---------------------------------------------------------------------------
# _images — build-time sharing (builder-inited)
# ---------------------------------------------------------------------------

def _patched_copy_image_files(
    builder,
    shared_images: Path,
    out_images: Path,
    mode: str,
    configured_at: float | None = None,
):
    """Replacement for ``builder.copy_image_files`` that skips shared files.

    Writes only images not already present in the shared tree, then makes the
    per-language output file a link to the shared copy. This keeps
    ``build/<lang>/_images`` as a real directory, so a locale override can replace
    one file without materialising the whole image tree.
    """

    def _stringify_image(src: str) -> str:
        try:
            return ImageAdapter(builder.env).get_original_image_uri(src)
        except AttributeError:
            return str(src)

    @timing(
        "shared_assets: _images copy/link phase",
        logger=logger,
        result_formatter=_format_image_copy_timing,
    )
    def copy_image_files() -> _ImageCopyStats:
        images = builder.images
        if not images:
            logger.info("shared_assets: _images copy phase skipped (no images)")
            return _ImageCopyStats()
        ensuredir(shared_images)
        ensuredir(out_images)
        copied = skipped = linked = 0
        verbosity = getattr(getattr(builder, "config", None), "verbosity", 0)
        total = len(images)
        if configured_at is not None:
            logger.info(
                "shared_assets: _images copy/link phase reached after %s since configuration",
                format_duration(perf_counter() - configured_at),
            )
        logger.info(
            "shared_assets: _images copy/link phase starting (images=%d)",
            total,
        )
        for index, src in enumerate(
            status_iterator(
                images,
                __("copying images... "),
                "brown",
                total,
                verbosity,
                stringify_func=_stringify_image,
            ),
            1,
        ):
            dest = images[src]
            rel = Path(dest)
            shared_target = shared_images / dest
            out_target = out_images / dest
            src_path = builder.srcdir / src
            # Content-aware: reuse the shared copy only when its bytes still match
            # the source. A changed/replaced image (same filename, new bytes) is
            # re-copied so live edits propagate to the shared tree and, via the
            # links below + self-heal, to every language. Images are the same
            # English source across languages, so re-copying identical bytes from
            # a later language is idempotent.
            if shared_target.exists() and filecmp.cmp(src_path, shared_target, shallow=False):
                skipped += 1
                _log_asset_step(
                    "_images",
                    "shared-reuse",
                    index,
                    total,
                    rel,
                    dst=shared_target,
                )
            else:
                ensuredir(shared_target.parent)
                try:
                    # sphinx's copyfile aborts if the destination exists, so drop a
                    # stale shared copy first (the content-changed refresh case).
                    if shared_target.exists():
                        shared_target.unlink()
                    copyfile(src_path, shared_target)
                    copied += 1
                    _log_asset_step(
                        "_images",
                        "shared-copy",
                        index,
                        total,
                        rel,
                        src=src_path,
                        dst=shared_target,
                    )
                except Exception as err:  # pragma: no cover - mirrors Sphinx logging
                    logger.warning("shared_assets: cannot copy image '%s': %s", src, err)
                    continue

            if out_target.exists() or out_target.is_symlink():
                _remove(out_target)
            ensuredir(out_target.parent)
            method = link_or_copy(shared_target, out_target, mode)
            _log_asset_step(
                "_images",
                "build-link",
                index,
                total,
                rel,
                src=shared_target,
                dst=out_target,
                method=method,
            )
            linked += 1
        logger.info(
            "shared_assets: images into shared tree "
            "(copied=%d, already-shared=%d, linked=%d)",
            copied,
            skipped,
            linked,
        )
        return _ImageCopyStats(
            total=total,
            copied=copied,
            already_shared=skipped,
            linked=linked,
        )

    return copy_image_files


def _link_missing_shared_images(shared_images: Path, out_images: Path, mode: str) -> int:
    """Ensure every file in the shared tree has a per-file link in *out_images*.

    Self-heals incremental rebuilds: ``copy_image_files`` only re-links images
    referenced by the docs read this run, so on a sphinx-autobuild / live build
    (where only changed docs are read) the links for unchanged docs would be
    missing. This restores any link that is absent, leaving existing links and
    per-language override files (real bytes) untouched. No-op on the very first
    build, when the shared tree is not seeded yet.
    """
    healed = 0
    for shared_file, rel in _iter_files(shared_images):
        target = out_images / rel
        if target.exists() or target.is_symlink():
            continue
        ensuredir(target.parent)
        link_or_copy(shared_file, target, mode)
        healed += 1
    return healed


def on_builder_inited(app) -> None:
    if not _is_active(app):
        return
    _set_per_file_verbosity(getattr(app.config, "verbosity", 0) or 0)
    if "_images" not in app.config.shared_assets_subdirs:
        return

    shared_images = _shared_root(app) / "_images"
    out_images = Path(app.outdir) / "_images"
    mode = app.config.shared_assets_link_mode

    ensuredir(shared_images)
    # Do NOT wipe an existing real _images directory: incremental rebuilds
    # (sphinx-autobuild / live) only re-read changed docs, so the patched
    # copy_image_files only re-links *those* images. Wiping here would drop every
    # link for unchanged docs and leave images broken until a full rebuild. Only
    # collapse a legacy whole-dir symlink into a real dir; the per-file reconcile
    # in copy_image_files handles everything else.
    if out_images.is_symlink():
        _remove(out_images)
    ensuredir(out_images)

    healed = _link_missing_shared_images(shared_images, out_images, mode)
    if healed:
        logger.info(
            "shared_assets: _images restored %d missing link(s) from shared tree "
            "(incremental/live self-heal)",
            healed,
        )

    app.builder.copy_image_files = _patched_copy_image_files(
        app.builder,
        shared_images,
        out_images,
        app.config.shared_assets_link_mode,
        perf_counter(),
    )
    app._shared_build_started = perf_counter()
    logger.info(
        "shared_assets: _images sharing configured; timing armed until HTML finish "
        "copy/link phase: %s -> %s",
        out_images,
        shared_images,
    )
    logger.info(
        "shared_assets: next phase is READING sources (parallel -j auto workers run "
        "quietly here); progress resumes at the image copy/link phase near the end",
    )


# ---------------------------------------------------------------------------
# Build-phase progress (reading -> writing -> image copy)
# ---------------------------------------------------------------------------

def _elapsed_since_start(app) -> str:
    started = getattr(app, "_shared_build_started", None)
    if started is None:
        return "n/a"
    return format_duration(perf_counter() - started)


def on_env_before_read_docs(app, env, docnames) -> None:
    if not _is_active(app):
        return
    app._shared_read_started = perf_counter()
    logger.info(
        "shared_assets: READING phase — %d of %d documents need (re)reading "
        "(quiet under -j auto); +%s since start",
        len(docnames),
        len(env.found_docs),
        _elapsed_since_start(app),
    )


def on_env_updated(app, _env):
    if not _is_active(app):
        return []
    started = getattr(app, "_shared_read_started", None)
    if started is not None:
        logger.info(
            "shared_assets: READING done in %s; resolving references next",
            format_duration(perf_counter() - started),
        )
    return []


def on_env_check_consistency(app, env) -> None:
    if not _is_active(app):
        return
    n_docs = len(getattr(env, "all_docs", {}) or {})
    # builder.images is still empty here (filled during writing); env.images is
    # the set of distinct referenced images collected during reading.
    n_images = len(getattr(env, "images", {}) or {})
    logger.info(
        "shared_assets: WRITING phase — %d output documents to write, then "
        "%d images to copy/link into the shared tree; +%s since start",
        n_docs,
        n_images,
        _elapsed_since_start(app),
    )


# ---------------------------------------------------------------------------
# Per-file sharing + overrides (build-finished)
# ---------------------------------------------------------------------------

def _seed_or_link(
    out_file: Path,
    shared_file: Path,
    mode: str,
    *,
    force_shared: bool = False,
    subdir: str = "",
    rel: Path | str | None = None,
    index: int = 0,
    total: int = 0,
) -> str | None:
    """Reconcile a single real output file against the shared tree.

    - shared copy missing  -> copy out_file into shared, then link out_file to it
    - shared copy identical -> replace out_file with a link to shared
    - shared copy differs   -> link to shared when force_shared, else keep real
    """
    display_rel = rel if rel is not None else out_file.name
    if not shared_file.exists():
        ensuredir(shared_file.parent)
        shutil.copy2(out_file, shared_file)
        _log_asset_step(
            subdir,
            "shared-copy",
            index,
            total,
            display_rel,
            src=out_file,
            dst=shared_file,
        )
        out_file.unlink()
        method = link_or_copy(shared_file, out_file, mode)
        _log_asset_step(
            subdir,
            "build-link",
            index,
            total,
            display_rel,
            src=shared_file,
            dst=out_file,
            method=method,
        )
        return method
    files_match = filecmp.cmp(out_file, shared_file, shallow=False)
    if force_shared or files_match:
        _log_asset_step(
            subdir,
            "shared-reuse",
            index,
            total,
            display_rel,
            src=shared_file,
            dst=out_file,
        )
        out_file.unlink()
        method = link_or_copy(shared_file, out_file, mode)
        _log_asset_step(
            subdir,
            "build-link",
            index,
            total,
            display_rel,
            src=shared_file,
            dst=out_file,
            method=method,
        )
        return method
    _log_asset_step(
        subdir,
        "local-keep",
        index,
        total,
        display_rel,
        src=out_file,
    )
    return None  # genuinely per-language, keep as-is


def _dedup_subdir(
    out_dir: Path,
    shared_dir: Path,
    mode: str,
    *,
    force_shared: bool = False,
) -> None:
    """Per-file sharing of *out_dir* against *shared_dir* (e.g. ``_static``)."""
    if not out_dir.is_dir() or out_dir.is_symlink():
        return
    linked = kept = 0
    files = [
        (out_file, rel)
        for out_file, rel in _iter_files(out_dir)
        if not out_file.is_symlink()
    ]
    total = len(files)
    for index, (out_file, rel) in enumerate(files, 1):
        result = _seed_or_link(
            out_file,
            shared_dir / rel,
            mode,
            force_shared=force_shared,
            subdir=out_dir.name,
            rel=rel,
            index=index,
            total=total,
        )
        if result is None:
            kept += 1
        else:
            linked += 1
    logger.info(
        "shared_assets: %s share (linked=%d, per-language=%d, force_shared=%s)",
        out_dir.name,
        linked,
        kept,
        force_shared,
    )


def _materialize_symlinked_dir(out_dir: Path, shared_dir: Path, mode: str) -> None:
    """Turn a whole-dir symlink into a real dir of per-file links to shared.

    Needed before applying overrides to a dir that is currently a single symlink
    to the shared tree (the ``_images`` case), so individual files can diverge.
    """
    if not out_dir.is_symlink():
        return
    out_dir.unlink()
    ensuredir(out_dir)
    files = list(_iter_files(shared_dir))
    total = len(files)
    for index, (shared_file, rel) in enumerate(files, 1):
        target = out_dir / rel
        ensuredir(target.parent)
        method = link_or_copy(shared_file, target, mode)
        _log_asset_step(
            out_dir.name,
            "build-link",
            index,
            total,
            rel,
            src=shared_file,
            dst=target,
            method=method,
        )


def _apply_overrides(
    override_dir: Path,
    out_dir: Path,
    shared_dir: Path,
    *,
    copy_new: bool,
    mode: str,
) -> None:
    """Copy ``locale/<lang>/<subdir>`` files over the shared links.

    Each override is ``unlink``-ed first, then the real bytes are copied in, so a
    copy can never write through a symlink into the shared base.
    """
    if not override_dir.is_dir():
        return

    # Compatibility with older builds that used a whole-directory _images
    # symlink: expand it first so only overridden files diverge.
    if out_dir.is_symlink():
        _materialize_symlinked_dir(out_dir, shared_dir, mode)

    applied = added = skipped = 0
    files = list(_iter_files(override_dir))
    total = len(files)
    for index, (override_file, rel) in enumerate(files, 1):
        target = out_dir / rel
        has_shared = (shared_dir / rel).exists()
        if not has_shared and not copy_new:
            logger.warning(
                "shared_assets: orphan override (no shared base) skipped: %s", rel
            )
            _log_asset_step(
                out_dir.name,
                "override-skip",
                index,
                total,
                rel,
                src=override_file,
                dst=target,
            )
            skipped += 1
            continue
        if target.exists() or target.is_symlink():
            target.unlink()  # drop the shared symlink before writing real bytes
        ensuredir(target.parent)
        shutil.copy2(override_file, target)
        _log_asset_step(
            out_dir.name,
            "override-copy",
            index,
            total,
            rel,
            src=override_file,
            dst=target,
        )
        if has_shared:
            applied += 1
        else:
            added += 1
    if applied or added or skipped:
        logger.info(
            "shared_assets: %s overrides (replaced=%d, added=%d, skipped=%d)",
            out_dir.name,
            applied,
            added,
            skipped,
        )


def on_build_finished(app, exception) -> None:
    if exception is not None:
        return
    if not _is_active(app):
        return

    mode = app.config.shared_assets_link_mode
    copy_new = app.config.shared_assets_copy_new
    shared_root = _shared_root(app)
    out_root = Path(app.outdir)
    override_base = _override_root(app) / _current_lang(app)

    logger.info(
        "shared_assets: build-finished reconciliation starting for %s",
        ", ".join(app.config.shared_assets_subdirs),
    )
    # Keep shared _static theme assets in sync with their html_static_path source,
    # so a live theme edit (CSS/JS/fonts) reaches every language through its link.
    if "_static" in app.config.shared_assets_subdirs:
        refreshed = _sync_shared_theme_static(app, shared_root / "_static")
        if refreshed:
            logger.info(
                "shared_assets: _static refreshed %d theme asset(s) from source",
                refreshed,
            )
    for subdir in app.config.shared_assets_subdirs:
        out_dir = out_root / subdir
        shared_dir = shared_root / subdir
        # _images and _static are real per-language dirs with per-file shared
        # links, so each configured subdir is reconciled here.
        _dedup_subdir(
            out_dir,
            shared_dir,
            mode,
            force_shared=subdir == "_static",
        )
        _apply_overrides(
            override_base / subdir,
            out_dir,
            shared_dir,
            copy_new=copy_new,
            mode=mode,
        )


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def setup(app):
    app.add_config_value("shared_assets_enabled", True, "env")
    app.add_config_value("shared_assets_root", "", "env")
    app.add_config_value("shared_assets_subdirs", ["_images", "_static"], "env")
    app.add_config_value("shared_assets_override_root", "", "env")
    app.add_config_value("shared_assets_link_mode", "auto", "env")
    app.add_config_value("shared_assets_copy_new", True, "env")

    app.connect("builder-inited", on_builder_inited)
    app.connect("env-before-read-docs", on_env_before_read_docs)
    app.connect("env-updated", on_env_updated)
    app.connect("env-check-consistency", on_env_check_consistency)
    app.connect("build-finished", on_build_finished)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
