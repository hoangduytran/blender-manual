"""Tests for the shared_assets extension (asset sharing + per-language override)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EXTENSIONS_DIR = REPO_ROOT / "build_files" / "extensions"
if str(EXTENSIONS_DIR) not in sys.path:
    sys.path.insert(0, str(EXTENSIONS_DIR))

import shared_assets  # noqa: E402


def _write(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def _capture_info_logs(monkeypatch) -> list[str]:
    logs: list[str] = []

    def fake_info(message: str, *args: object, **_kw: object) -> None:
        logs.append(message % args if args else message)

    monkeypatch.setattr(shared_assets.logger, "info", fake_info)
    return logs


# ---------------------------------------------------------------------------
# link_or_copy
# ---------------------------------------------------------------------------

def test_link_or_copy_symlink(tmp_path):
    src = _write(tmp_path / "shared" / "a.png", b"PNG")
    dst = tmp_path / "lang" / "a.png"
    dst.parent.mkdir(parents=True)
    mode = shared_assets.link_or_copy(src, dst, "auto")
    assert mode == "symlink"
    assert dst.is_symlink()
    assert dst.read_bytes() == b"PNG"
    # relative symlink, resolves into the shared tree
    assert os.path.realpath(dst) == os.path.realpath(src)


def test_link_or_copy_forced_copy(tmp_path):
    src = _write(tmp_path / "shared" / "a.png", b"PNG")
    dst = tmp_path / "lang" / "a.png"
    dst.parent.mkdir(parents=True)
    mode = shared_assets.link_or_copy(src, dst, "copy")
    assert mode == "copy"
    assert not dst.is_symlink()
    assert dst.read_bytes() == b"PNG"


def test_link_or_copy_fallback_when_symlink_unavailable(tmp_path, monkeypatch):
    src = _write(tmp_path / "shared" / "a.png", b"PNG")
    dst = tmp_path / "lang" / "a.png"
    dst.parent.mkdir(parents=True)

    def boom(*_a, **_k):
        raise OSError("no symlinks here (simulated Windows)")

    monkeypatch.setattr(shared_assets.os, "symlink", boom)
    mode = shared_assets.link_or_copy(src, dst, "auto")
    # falls back to hardlink (same volume) and the bytes are still correct
    assert mode in {"hardlink", "copy"}
    assert dst.read_bytes() == b"PNG"


# ---------------------------------------------------------------------------
# _images copy patch
# ---------------------------------------------------------------------------

def test_patched_image_copy_uses_real_dir_with_per_file_links(tmp_path, monkeypatch):
    srcdir = tmp_path / "manual"
    _write(srcdir / "images" / "a.png", b"A")
    _write(srcdir / "images" / "nested" / "b.png", b"B")

    shared = tmp_path / "build" / "shared" / "_images"
    out = tmp_path / "build" / "vi" / "_images"
    builder = SimpleNamespace(
        srcdir=srcdir,
        images={
            "images/a.png": "a.png",
            "images/nested/b.png": "nested/b.png",
        },
        config=SimpleNamespace(verbosity=0),
    )
    progress_calls: list[tuple[str, int]] = []
    monkeypatch.setattr(shared_assets, "_per_file_verbosity", 2)
    info_logs = _capture_info_logs(monkeypatch)

    def fake_status_iterator(
        iterable,
        summary,
        _color,
        length,
        _verbosity,
        stringify_func=None,
    ):
        progress_calls.append((summary, length))
        for item in iterable:
            if stringify_func is not None:
                stringify_func(item)
            yield item

    monkeypatch.setattr(shared_assets, "status_iterator", fake_status_iterator)

    copy_images = shared_assets._patched_copy_image_files(builder, shared, out, "auto")
    stats = copy_images()

    assert progress_calls == [("copying images... ", 2)]
    assert "shared_assets: _images copy/link phase starting (images=2)" in info_logs
    assert stats.total == 2
    assert stats.copied == 2
    assert stats.already_shared == 0
    assert stats.linked == 2
    assert "@timing start: shared_assets: _images copy/link phase" in info_logs
    assert any(
        line.startswith("@timing done: shared_assets: _images copy/link phase elapsed=")
        and "images=2 copied=2 already-shared=0 linked=2" in line
        for line in info_logs
    )
    assert any(
        "_images shared-copy [" in line and "a.png" in line
        for line in info_logs
    )
    assert any(
        "_images build-link [" in line and "nested/b.png" in line
        for line in info_logs
    )
    step_logs = [line for line in info_logs if " [" in line]
    assert all("/2 " in line for line in step_logs)
    assert out.is_dir()
    assert not out.is_symlink()
    assert (shared / "a.png").read_bytes() == b"A"
    assert (shared / "nested" / "b.png").read_bytes() == b"B"
    assert (out / "a.png").is_symlink()
    assert (out / "nested" / "b.png").is_symlink()
    assert os.path.realpath(out / "a.png") == os.path.realpath(shared / "a.png")


def test_image_edit_refreshes_shared(tmp_path, monkeypatch):
    """A changed image (same name, new bytes) re-copies to shared (live edit)."""
    srcdir = tmp_path / "manual"
    _write(srcdir / "images" / "a.png", b"NEW-BYTES")
    shared = tmp_path / "build" / "shared" / "_images"
    out = tmp_path / "build" / "vi" / "_images"
    _write(shared / "a.png", b"OLD-BYTES")  # stale shared copy
    builder = SimpleNamespace(
        srcdir=srcdir,
        images={"images/a.png": "a.png"},
        config=SimpleNamespace(verbosity=0),
    )
    monkeypatch.setattr(shared_assets, "status_iterator", lambda it, *a, **k: iter(it))

    stats = shared_assets._patched_copy_image_files(builder, shared, out, "auto")()

    assert stats.copied == 1 and stats.already_shared == 0
    assert (shared / "a.png").read_bytes() == b"NEW-BYTES"  # shared refreshed
    assert (out / "a.png").read_bytes() == b"NEW-BYTES"


def test_image_unchanged_reuses_shared(tmp_path, monkeypatch):
    """Identical bytes are not re-copied (cheap reuse path stays)."""
    srcdir = tmp_path / "manual"
    _write(srcdir / "images" / "a.png", b"SAME")
    shared = tmp_path / "build" / "shared" / "_images"
    out = tmp_path / "build" / "vi" / "_images"
    _write(shared / "a.png", b"SAME")
    builder = SimpleNamespace(
        srcdir=srcdir,
        images={"images/a.png": "a.png"},
        config=SimpleNamespace(verbosity=0),
    )
    monkeypatch.setattr(shared_assets, "status_iterator", lambda it, *a, **k: iter(it))

    stats = shared_assets._patched_copy_image_files(builder, shared, out, "auto")()

    assert stats.already_shared == 1 and stats.copied == 0


# ---------------------------------------------------------------------------
# _dedup_subdir (the _static case)
# ---------------------------------------------------------------------------

def test_dedup_links_identical_and_keeps_divergent(tmp_path):
    shared = tmp_path / "shared" / "_static"
    out = tmp_path / "vi" / "_static"

    same = _write(out / "theme.css", b"body{}")
    nested = _write(out / "css" / "extra.css", b"a{}")
    perlang = _write(out / "documentation_options.js", b"VI-OPTS")

    shared_assets._dedup_subdir(out, shared, "auto")

    # identical files become symlinks pointing into the shared tree
    assert same.is_symlink()
    assert nested.is_symlink()
    assert os.path.realpath(same) == os.path.realpath(shared / "theme.css")
    # the shared tree was seeded with the first language's bytes
    assert (shared / "theme.css").read_bytes() == b"body{}"
    assert (shared / "css" / "extra.css").read_bytes() == b"a{}"
    # per-language file is also seeded+linked for the first language (correct bytes)
    assert perlang.read_bytes() == b"VI-OPTS"


def _theme_app(tmp_path, static_path="../build_files/theme"):
    (tmp_path / "manual").mkdir(parents=True, exist_ok=True)
    return SimpleNamespace(
        confdir=str(tmp_path / "manual"),
        config=SimpleNamespace(html_static_path=[static_path]),
    )


def test_sync_shared_theme_static_refreshes_changed_source(tmp_path):
    """An edited theme source refreshes the shared copy (the live-edit path)."""
    _write(tmp_path / "build_files" / "theme" / "css" / "theme.css", b"NEW")
    shared = tmp_path / "shared" / "_static"
    _write(shared / "css" / "theme.css", b"OLD")  # stale shared copy

    refreshed = shared_assets._sync_shared_theme_static(_theme_app(tmp_path), shared)

    assert refreshed == 1
    assert (shared / "css" / "theme.css").read_bytes() == b"NEW"


def test_sync_shared_theme_static_skips_unchanged(tmp_path):
    _write(tmp_path / "build_files" / "theme" / "css" / "theme.css", b"SAME")
    shared = tmp_path / "shared" / "_static"
    _write(shared / "css" / "theme.css", b"SAME")

    refreshed = shared_assets._sync_shared_theme_static(_theme_app(tmp_path), shared)

    assert refreshed == 0


def test_sync_refresh_reaches_all_languages_via_symlink(tmp_path):
    """Refreshing shared updates every language that links to it (the goal)."""
    _write(tmp_path / "build_files" / "theme" / "css" / "theme.css", b"NEW")
    shared = tmp_path / "shared" / "_static"
    _write(shared / "css" / "theme.css", b"OLD")
    # en and vi both link the (old) shared theme file
    for lang in ("en", "vi"):
        out = tmp_path / lang / "_static" / "css"
        out.mkdir(parents=True)
        shared_assets.link_or_copy(shared / "css" / "theme.css", out / "theme.css", "auto")

    shared_assets._sync_shared_theme_static(_theme_app(tmp_path), shared)

    # both languages now resolve to the refreshed bytes through their links
    assert (tmp_path / "en" / "_static" / "css" / "theme.css").read_bytes() == b"NEW"
    assert (tmp_path / "vi" / "_static" / "css" / "theme.css").read_bytes() == b"NEW"


def test_sync_does_not_touch_non_theme_static(tmp_path):
    """Per-language generated files are not under html_static_path -> untouched."""
    _write(tmp_path / "build_files" / "theme" / "css" / "theme.css", b"x")
    shared = tmp_path / "shared" / "_static"
    _write(shared / "documentation_options.js", b"EN-OPTS")  # not a theme source

    shared_assets._sync_shared_theme_static(_theme_app(tmp_path), shared)

    assert (shared / "documentation_options.js").read_bytes() == b"EN-OPTS"


def test_static_second_language_links_divergent_file_to_shared(tmp_path):
    shared = tmp_path / "shared" / "_static"
    # shared already holds the base file (seeded by the first language)
    _write(shared / "documentation_options.js", b"EN-OPTS")
    _write(shared / "theme.css", b"body{}")

    out = tmp_path / "vi" / "_static"
    perlang = _write(out / "documentation_options.js", b"VI-OPTS")  # differs
    theme = _write(out / "theme.css", b"body{}")  # identical

    shared_assets._dedup_subdir(out, shared, "auto", force_shared=True)

    assert theme.is_symlink()
    assert perlang.is_symlink()
    assert perlang.read_bytes() == b"EN-OPTS"
    # shared base untouched
    assert (shared / "documentation_options.js").read_bytes() == b"EN-OPTS"


def test_dedup_info_logs_shared_copy_reuse_and_links(tmp_path, monkeypatch):
    shared = tmp_path / "shared" / "_static"
    _write(shared / "theme.css", b"body{}")

    out = tmp_path / "vi" / "_static"
    _write(out / "theme.css", b"body{}")
    _write(out / "new.js", b"NEW")

    monkeypatch.setattr(shared_assets, "_per_file_verbosity", 2)
    info_logs = _capture_info_logs(monkeypatch)
    shared_assets._dedup_subdir(out, shared, "auto", force_shared=True)

    assert any(
        "_static shared-reuse [" in line and "theme.css" in line
        for line in info_logs
    )
    assert any(
        "_static shared-copy [" in line and "new.js" in line
        for line in info_logs
    )
    assert sum("_static build-link [" in line for line in info_logs) == 2
    step_logs = [line for line in info_logs if " [" in line]
    assert all("/2 " in line for line in step_logs)


# ---------------------------------------------------------------------------
# per-file logging verbosity gate
# ---------------------------------------------------------------------------

def test_per_file_logs_suppressed_by_default(tmp_path, monkeypatch):
    """Default (non-verbose) builds emit only summary counts, no per-file lines."""
    shared = tmp_path / "shared" / "_static"
    out = tmp_path / "vi" / "_static"
    _write(out / "theme.css", b"body{}")

    monkeypatch.setattr(shared_assets, "_per_file_verbosity", 0)
    info_logs = _capture_info_logs(monkeypatch)
    shared_assets._dedup_subdir(out, shared, "auto")

    # no per-file step lines...
    assert not any(" [" in line and "_static " in line for line in info_logs)
    # ...but the summary count line is still present
    assert any(line.startswith("shared_assets: _static share (linked=") for line in info_logs)


def test_per_file_logs_enabled_when_verbose(tmp_path, monkeypatch):
    shared = tmp_path / "shared" / "_static"
    out = tmp_path / "vi" / "_static"
    _write(out / "theme.css", b"body{}")

    monkeypatch.setattr(shared_assets, "_per_file_verbosity", 2)
    info_logs = _capture_info_logs(monkeypatch)
    shared_assets._dedup_subdir(out, shared, "auto")

    assert any("_static build-link [" in line for line in info_logs)


def test_on_builder_inited_sets_per_file_verbosity_from_config(tmp_path, monkeypatch):
    monkeypatch.setattr(shared_assets, "_per_file_verbosity", 0)
    app = _fake_app(tmp_path, "vi", verbosity=2)
    app.builder.images = {}
    app.builder.srcdir = tmp_path / "manual"

    shared_assets.on_builder_inited(app)

    assert shared_assets._per_file_verbosity == 2


# ---------------------------------------------------------------------------
# overrides + the cp-through-symlink footgun
# ---------------------------------------------------------------------------

def test_override_replaces_symlink_without_mutating_shared(tmp_path, monkeypatch):
    shared = tmp_path / "shared" / "_images"
    out = tmp_path / "vi" / "_images"
    override = tmp_path / "locale" / "vi" / "_images"

    _write(shared / "logo.png", b"SHARED-LOGO")
    # vi/_images/logo.png starts as a symlink to the shared base
    out.mkdir(parents=True)
    shared_assets.link_or_copy(shared / "logo.png", out / "logo.png", "auto")
    assert (out / "logo.png").is_symlink()

    _write(override / "logo.png", b"VI-LOGO")
    monkeypatch.setattr(shared_assets, "_per_file_verbosity", 2)
    info_logs = _capture_info_logs(monkeypatch)
    shared_assets._apply_overrides(
        override, out, shared, copy_new=True, mode="auto"
    )

    assert any(
        "_images override-copy [1/1 100.00%]" in line and "logo.png" in line
        for line in info_logs
    )
    # override is now a real file with the local bytes
    assert not (out / "logo.png").is_symlink()
    assert (out / "logo.png").read_bytes() == b"VI-LOGO"
    # the shared base is NOT corrupted (regression: cp-through-symlink)
    assert (shared / "logo.png").read_bytes() == b"SHARED-LOGO"


def test_override_relative_path_match_is_scoped(tmp_path):
    shared = tmp_path / "shared" / "_images"
    out = tmp_path / "vi" / "_images"
    override = tmp_path / "locale" / "vi" / "_images"

    _write(shared / "render" / "foo.png", b"SHARED-RENDER")
    _write(shared / "ui" / "foo.png", b"SHARED-UI")
    out.mkdir(parents=True)
    shared_assets.link_or_copy(shared / "render" / "foo.png", _ensure(out / "render" / "foo.png"), "auto")
    shared_assets.link_or_copy(shared / "ui" / "foo.png", _ensure(out / "ui" / "foo.png"), "auto")

    _write(override / "render" / "foo.png", b"VI-RENDER")
    shared_assets._apply_overrides(override, out, shared, copy_new=True, mode="auto")

    # only the nested render/foo.png diverged; same-basename ui/foo.png untouched
    assert (out / "render" / "foo.png").read_bytes() == b"VI-RENDER"
    assert (out / "ui" / "foo.png").is_symlink()
    assert (out / "ui" / "foo.png").read_bytes() == b"SHARED-UI"


def test_override_new_asset_copy_new_true(tmp_path):
    shared = tmp_path / "shared" / "_images"
    out = tmp_path / "vi" / "_images"
    override = tmp_path / "locale" / "vi" / "_images"
    shared.mkdir(parents=True)
    out.mkdir(parents=True)

    _write(override / "extra.png", b"VI-ONLY")
    shared_assets._apply_overrides(override, out, shared, copy_new=True, mode="auto")

    assert (out / "extra.png").read_bytes() == b"VI-ONLY"
    assert not (out / "extra.png").is_symlink()


def test_override_new_asset_copy_new_false_skips(tmp_path):
    shared = tmp_path / "shared" / "_images"
    out = tmp_path / "vi" / "_images"
    override = tmp_path / "locale" / "vi" / "_images"
    shared.mkdir(parents=True)
    out.mkdir(parents=True)

    _write(override / "extra.png", b"VI-ONLY")
    shared_assets._apply_overrides(override, out, shared, copy_new=False, mode="auto")

    assert not (out / "extra.png").exists()


def test_static_override_materializes_for_language(tmp_path):
    shared = tmp_path / "shared" / "_static"
    out = tmp_path / "vi" / "_static"
    override = tmp_path / "locale" / "vi" / "_static"

    _write(shared / "documentation_options.js", b"SHARED-OPTS")
    out.mkdir(parents=True)
    shared_assets.link_or_copy(
        shared / "documentation_options.js",
        out / "documentation_options.js",
        "auto",
    )
    assert (out / "documentation_options.js").is_symlink()

    _write(override / "documentation_options.js", b"VI-OPTS")
    shared_assets._apply_overrides(override, out, shared, copy_new=True, mode="auto")

    assert not (out / "documentation_options.js").is_symlink()
    assert (out / "documentation_options.js").read_bytes() == b"VI-OPTS"
    assert (shared / "documentation_options.js").read_bytes() == b"SHARED-OPTS"


def test_legacy_whole_dir_symlink_override_is_materialized(tmp_path):
    """Compatibility: old whole-dir _images symlinks can still be overridden."""
    shared = tmp_path / "shared" / "_images"
    out = tmp_path / "vi" / "_images"
    override = tmp_path / "locale" / "vi" / "_images"

    _write(shared / "a.png", b"SHARED-A")
    _write(shared / "b.png", b"SHARED-B")
    # whole _images dir is one symlink to the shared tree
    out.parent.mkdir(parents=True)
    os.symlink(shared, out)
    assert out.is_symlink()

    _write(override / "a.png", b"VI-A")
    shared_assets._apply_overrides(override, out, shared, copy_new=True, mode="auto")

    assert not out.is_symlink()  # expanded into a real dir
    assert (out / "a.png").read_bytes() == b"VI-A"  # override applied
    assert (out / "b.png").is_symlink()  # untouched file still shared
    assert (shared / "a.png").read_bytes() == b"SHARED-A"  # base intact


# ---------------------------------------------------------------------------
# on_build_finished end-to-end with a fake app
# ---------------------------------------------------------------------------

def _fake_app(tmp_path, lang, **config):
    build = tmp_path / "build"
    cfg = dict(
        shared_assets_enabled=True,
        shared_assets_root="",
        shared_assets_subdirs=["_images", "_static"],
        shared_assets_override_root=str(tmp_path / "locale"),
        shared_assets_link_mode="auto",
        shared_assets_copy_new=True,
        language=lang,
    )
    cfg.update(config)
    return SimpleNamespace(
        outdir=build / lang,
        confdir=tmp_path,
        builder=SimpleNamespace(name="html"),
        config=SimpleNamespace(**cfg),
    )


def test_on_builder_inited_creates_real_images_dir(tmp_path):
    app = _fake_app(tmp_path, "vi")
    app.builder.images = {}
    app.builder.srcdir = tmp_path / "manual"
    out_images = Path(app.outdir) / "_images"

    shared_assets.on_builder_inited(app)

    assert out_images.is_dir()
    assert not out_images.is_symlink()
    assert (tmp_path / "build" / "shared" / "_images").is_dir()


def test_on_builder_inited_preserves_existing_links_incremental(tmp_path):
    """Regression: an incremental rebuild must NOT wipe existing image links.

    sphinx-autobuild only re-reads changed docs, so copy_image_files re-links a
    subset. Wiping the whole dir here left images broken until a full rebuild.
    """
    app = _fake_app(tmp_path, "vi")
    app.builder.images = {}
    app.builder.srcdir = tmp_path / "manual"

    shared_images = tmp_path / "build" / "shared" / "_images"
    out_images = Path(app.outdir) / "_images"
    # shared tree already seeded (a prior full build) + a live link in the lang dir
    _write(shared_images / "a.png", b"A")
    out_images.mkdir(parents=True)
    shared_assets.link_or_copy(shared_images / "a.png", out_images / "a.png", "auto")
    assert (out_images / "a.png").is_symlink()

    shared_assets.on_builder_inited(app)

    # existing link survives the (no-op image) rebuild
    assert (out_images / "a.png").is_symlink()
    assert (out_images / "a.png").read_bytes() == b"A"


def test_on_builder_inited_self_heals_missing_links(tmp_path):
    """An emptied _images dir is repopulated from the shared tree on next build."""
    app = _fake_app(tmp_path, "vi")
    app.builder.images = {}
    app.builder.srcdir = tmp_path / "manual"

    shared_images = tmp_path / "build" / "shared" / "_images"
    out_images = Path(app.outdir) / "_images"
    _write(shared_images / "a.png", b"A")
    _write(shared_images / "nested" / "b.png", b"B")
    out_images.mkdir(parents=True)  # emptied dir (the bug's aftermath)

    shared_assets.on_builder_inited(app)

    assert (out_images / "a.png").is_symlink()
    assert (out_images / "a.png").read_bytes() == b"A"
    assert (out_images / "nested" / "b.png").read_bytes() == b"B"


def test_self_heal_does_not_clobber_override(tmp_path):
    """A per-language override (real bytes) must not be replaced by a shared link."""
    shared_images = tmp_path / "shared" / "_images"
    out_images = tmp_path / "vi" / "_images"
    _write(shared_images / "logo.png", b"SHARED")
    override = _write(out_images / "logo.png", b"VI-LOCAL")  # real file, not a link

    healed = shared_assets._link_missing_shared_images(shared_images, out_images, "auto")

    assert healed == 0
    assert not override.is_symlink()
    assert override.read_bytes() == b"VI-LOCAL"


def test_on_build_finished_dedup_and_override(tmp_path, monkeypatch):
    monkeypatch.setenv("BF_LANG", "vi")
    app = _fake_app(tmp_path, "vi")

    out = Path(app.outdir)
    _write(out / "_static" / "theme.css", b"body{}")
    _write(out / "_images" / "logo.png", b"EN-LOGO")
    _write(tmp_path / "locale" / "vi" / "_images" / "logo.png", b"VI-LOGO")

    shared_assets.on_build_finished(app, None)

    shared = tmp_path / "build" / "shared"
    assert (out / "_static" / "theme.css").is_symlink()
    assert (shared / "_static" / "theme.css").read_bytes() == b"body{}"
    # override wins, shared base seeded from the copied bytes then preserved
    assert (out / "_images" / "logo.png").read_bytes() == b"VI-LOGO"


def test_on_build_finished_applies_english_override(tmp_path, monkeypatch):
    """English is a normal language for same-path shared asset overrides."""
    monkeypatch.setenv("BF_LANG", "en")
    app = _fake_app(tmp_path, "en")

    out = Path(app.outdir)
    _write(out / "_images" / "logo.png", b"SHARED-LOGO")
    _write(tmp_path / "locale" / "en" / "_images" / "logo.png", b"EN-LOGO")

    shared_assets.on_build_finished(app, None)

    shared = tmp_path / "build" / "shared"
    assert not (out / "_images" / "logo.png").is_symlink()
    assert (out / "_images" / "logo.png").read_bytes() == b"EN-LOGO"
    assert (shared / "_images" / "logo.png").read_bytes() == b"SHARED-LOGO"


def test_on_build_finished_forces_static_to_shared(tmp_path, monkeypatch):
    monkeypatch.setenv("BF_LANG", "fr")
    app = _fake_app(tmp_path, "fr")

    shared = tmp_path / "build" / "shared" / "_static"
    _write(shared / "documentation_options.js", b"EN-OPTS")

    out = Path(app.outdir)
    doc_options = _write(out / "_static" / "documentation_options.js", b"FR-OPTS")

    shared_assets.on_build_finished(app, None)

    assert doc_options.is_symlink()
    assert doc_options.read_bytes() == b"EN-OPTS"


def test_on_build_finished_noop_when_disabled(tmp_path):
    app = _fake_app(tmp_path, "vi", shared_assets_enabled=False)
    out = Path(app.outdir)
    css = _write(out / "_static" / "theme.css", b"body{}")
    shared_assets.on_build_finished(app, None)
    assert not css.is_symlink()  # untouched
    assert not (tmp_path / "build" / "shared").exists()


def test_on_build_finished_skips_on_exception(tmp_path):
    app = _fake_app(tmp_path, "vi")
    out = Path(app.outdir)
    css = _write(out / "_static" / "theme.css", b"body{}")
    shared_assets.on_build_finished(app, RuntimeError("build failed"))
    assert not css.is_symlink()


def _ensure(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__, "-v"]))
