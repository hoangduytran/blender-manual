#!/usr/bin/env python3
"""
******************
Update Screenshots
******************

This utility is intended to update screenshots, currently it covers:

- Preferences (preferences_section_*.png).

Once this command has finished, review:

   build/old_screenshots/index.html


Example Usage
=============

   env BLENDER_BIN=/src/blender/blender.bin BF_LANG=en ./tools/utils_maintenance/update_screenshots.py
"""


import sys
import os
import subprocess
from pathlib import Path
if "bpy" not in sys.modules:
    import tempfile

    blender = os.environ.get("BLENDER_BIN", "blender")

    command = [
        blender,
        "--factory-startup",
        "-noaudio",
        # Note: opening preferences requires window focus.
        # ideally we could work around this.
        # "--no-window-focus",
        "--no-native-pixels",
        # For preferences this wont matter, for other screen-shots it may.
        # Size is odd, this is based on the screenshot in the manual.
        "--window-geometry", "0", "0", "1440", "900",
        "--enable-event-simulate",
        "--python", __file__,
    ]

    env = os.environ.copy()

    # Needed to avoid reading "recent-files.txt" & "bookmarks.txt"
    # as well as helpfully auto-saving the preferences.
    with tempfile.TemporaryDirectory() as temp_home:
        env["HOME"] = temp_home

        subprocess.run(
            command,
            env=env,
        )
    sys.exit(0)

# -----------
# Setup Paths

ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOCALE_DIR = os.path.join(ROOT_DIR, "locale")

LANG = os.environ.get("BF_LANG", "en")

if LANG == "en":
    IMAGE_DIR_FINAL = os.path.join(ROOT_DIR, "manual", "images")
    IMAGE_DIR_PREVIEW = os.path.join(ROOT_DIR, "build", "old_screenshots")
else:
    IMAGE_DIR_FINAL = os.path.join(LOCALE_DIR, LANG, "images")
    IMAGE_DIR_PREVIEW = os.path.join(ROOT_DIR, "build", "old_screenshots", LANG)

# Ensure both destinations exist
os.makedirs(IMAGE_DIR_FINAL, exist_ok=True)
os.makedirs(IMAGE_DIR_PREVIEW, exist_ok=True)

manual_language_codes = {
    "en": "en_US",
    "ar": "ar_EG",
    "ca": "ca_AD",
    "de": "de_DE",
    "el": "el_GR",
    "es": "es",
    "fi": "fi_FI",
    "fr": "fr_FR",
    "id": "id_ID",
    "it": "it_IT",
    "ja": "ja_JP",
    "ko": "ko_KR",
    "nl": "nl_NL",
    "pt": "pt_PT",
    "ru": "ru_RU",
    "sk": "sk_SK",
    "sr": "sr_RS",
    "th": "th_TH",
    "uk": "uk_UA",
    "vi": "vi_VN",
    "zh-hans": "zh_HANS",
    "zh-hant": "zh_HANT",
}


# -------------
# Other Globals

# Workaround for previews not being generated instantly.
# Wait for this many ticks before taking a screenshot.
SCREENSHOT_WAIT_TICKS = 4

# ----------------------------------------------------------------------
# Blender Defaults


def setup_default_preferences(preferences):
    """ Set preferences useful for automation.
    """
    preferences.view.show_splash = False
    preferences.view.smooth_view = 0
    # preferences.view.use_quit_dialog = False
    preferences.filepaths.use_auto_save_temporary_files = False

    preferences.view.language = manual_language_codes.get(LANG, "en_US")

    bpy.app.use_userpref_skip_save_on_exit = False


# WARNING: do not relocate this import,
# it's important to postpone so this script can run outside of Blender.
import bpy


# ----------------------------------------------------------------------
# Blender Timer Wrapper

def run_iter_from_timer(event_iter):
    i = iter(event_iter)

    def event_step():
        ret = next(i, Ellipsis)
        if ret is Ellipsis:
            return None
        return 0.0

    bpy.app.timers.register(event_step, first_interval=0.0)


# ----------------------------------------------------------------------
# Blender Helpers

def set_developer_ui(preferences, state):
    preferences.view.show_developer_ui = state


def window_tap_key(*, window, type, unicode=None, shift=False, ctrl=False, alt=False, oskey=False):
    """
    Simulate pressing a key with modifier flags.
    """
    kw = {}
    if unicode is not None:
        kw["unicode"] = unicode
    if shift:
        kw["shift"] = True
    if ctrl:
        kw["ctrl"] = True
    if alt:
        kw["alt"] = True
    if oskey:
        kw["oskey"] = True

    yield
    window.event_simulate(type=type, value='PRESS', **kw)
    yield
    window.event_simulate(type=type, value='RELEASE')
    yield


def window_type_keys(*, window, text):
    yield
    for c in text:
        if c == '.':
            c_upper = 'PERIOD'
        elif c == ' ':
            c_upper = 'SPACE'
        else:
            c_upper = c.upper()
        yield
        yield from window_tap_key(window=window, type=c_upper, unicode=c)
        yield
    yield


def window_run_operator_from_search(*, window, operator_name):
    from bpy import context

    # Enables access to operator search
    set_developer_ui(context.preferences, True)

    yield
    yield from window_tap_key(window=window, type='F3')
    yield
    yield from window_type_keys(window=window, text=operator_name)
    yield from window_tap_key(window=window, type='RET')
    yield

    set_developer_ui(context.preferences, False)


def window_screenshot_to_filepath(*, window, filepath):
    from bpy import context
    for _ in range(SCREENSHOT_WAIT_TICKS):
        yield

    with context.temp_override(window=window):
        bpy.ops.screen.screenshot(filepath=filepath)
    yield


# ----------------------------------------------------------------------
# Screenshot Helpers

def crop(filepath, size_dst):
    import imbuf

    ibuf = imbuf.load(filepath)
    size_src = ibuf.size
    min = (
        (size_src[0] // 2) - (size_dst[0] // 2) - 1,
        (size_src[1] // 2) - (size_dst[1] // 2) - 1,
    )
    max = (
        min[0] + size_dst[0],
        min[1] + size_dst[1],
    )
    ibuf.crop(min=min, max=max)
    imbuf.write(ibuf, filepath=filepath)


def convert_png_to_webp(filepath_png):
    """
    Convert a PNG at `filepath_png` to WebP next to it, e.g. foo.png -> foo.webp.
    """
    if not filepath_png.lower().endswith(".png"):
        # Only convert PNG outputs from our screenshots/crop step.
        return filepath_png

    filepath_webp = os.path.splitext(filepath_png)[0] + ".webp"

    try:
        # Ensure cwebp is available on the system path
        subprocess.run(['cwebp', '-lossless', filepath_png, '-o', filepath_webp], check=True)
        print(f"Converted {filepath_png} to {filepath_webp}")
    except subprocess.CalledProcessError as e:
        print(f"Error during WebP conversion: {e}")

    Path(filepath_png).unlink()

    return filepath_webp


def format_size(num_bytes: int) -> str:
    """Return a human-readable size like '823 B', '15.2 KB', '3.1 MB'."""
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            if u == "B":
                return f"{int(size)} {u}"
            return f"{size:.1f} {u}"
        size /= 1024.0

CAPTURED_STEMS: list[str] = []

# New helpers to relocate old files before writing new ones
def find_file_in_dir(directory: str, stem: str) -> str | None:
    for ext in (".webp", ".png", ".jpg", ".jpeg"):
        candidate = os.path.join(directory, stem + ext)
        if os.path.exists(candidate):
            return candidate
    return None

def move_old_to_preview(stem: str) -> None:
    """
    If a file with this stem exists in IMAGE_DIR_FINAL (any supported extension),
    move it to IMAGE_DIR_PREVIEW (preserving file name).
    """

    if stem not in CAPTURED_STEMS:
        CAPTURED_STEMS.append(stem)

    old_path = find_file_in_dir(IMAGE_DIR_FINAL, stem)
    if not old_path:
        return
    dest_path = os.path.join(IMAGE_DIR_PREVIEW, os.path.basename(old_path))
    # Ensure preview dir exists
    os.makedirs(IMAGE_DIR_PREVIEW, exist_ok=True)
    # If a previous preview exists, replace it
    if os.path.abspath(old_path) == os.path.abspath(dest_path):
        return
    try:
        Path(dest_path).unlink(missing_ok=True)
    except Exception:
        pass
    Path(old_path).rename(dest_path)
    print(f"Moved old screenshot to preview: {old_path} -> {dest_path}")


# ----------------------------------------------------------------------
# Screenshot Startup

def screenshot_startup(window):
    from bpy import context

    stem = "interface_window-system_introduction_default-startup"
    move_old_to_preview(stem)
    filepath = os.path.join(
        IMAGE_DIR_FINAL,
        stem + ".png",
    )

    yield from window_screenshot_to_filepath(
        window=window,
        filepath=filepath,
    )

    convert_png_to_webp(filepath)


# ----------------------------------------------------------------------
# Screenshot Splash

def screenshot_splash_screen(window):
    from bpy import context

    # Needed otherwise userpref.blend is an empty file.
    filepath_userpref = os.path.join(
        os.environ["HOME"],
        ".config",
        "blender",
        "{:d}.{:d}".format(*bpy.app.version[:2]),
        "config",
        "userpref.blend",
    )

    os.makedirs(os.path.dirname(filepath_userpref), exist_ok=True)
    with open(filepath_userpref, 'wb') as fh:
        pass

    stem = "interface_splash_current"
    move_old_to_preview(stem)
    filepath = os.path.join(IMAGE_DIR_FINAL, stem + ".png")

    yield from window_run_operator_from_search(
        window=window,
        operator_name="wm.splash",
    )

    yield from window_screenshot_to_filepath(
        window=window,
        filepath=filepath,
    )

    os.unlink(filepath_userpref)

    yield from window_tap_key(window=window, type='ESC')

    crop(filepath, [520, 487])
    convert_png_to_webp(filepath)


# ----------------------------------------------------------------------
# Screenshot Preferences

def screenshot_preferences(window):
    from bpy import context

    prefs = context.preferences

    # We can't open preferences from a timer, use the shortcut.
    # bpy.ops.screen.userpref_show({"window": window, "screen": window.screen}, 'INVOKE_DEFAULT')
    yield from window_tap_key(window=window, ctrl=True, type='COMMA')

    prefs_window = next(
        iter([w for w in context.window_manager.windows if w.screen.is_temporary]))
    area = prefs_window.screen.areas[0]

    prefs_sections = tuple(
        e.identifier
        for e in prefs.rna_type.properties["active_section"].enum_items
    )

    for section in prefs_sections:
        stem = "editors_preferences_section_" + section.lower().replace("_", "-")
        move_old_to_preview(stem)
        filepath = os.path.join(IMAGE_DIR_FINAL, stem + ".png")

        if section == 'EXPERIMENTAL':
            set_developer_ui(prefs, True)

        setattr(prefs, "active_section", section)

        yield from window_screenshot_to_filepath(window=prefs_window, filepath=filepath)

        if section == 'EXPERIMENTAL':
            set_developer_ui(prefs, False)

        convert_png_to_webp(filepath)

    with context.temp_override(window=prefs_window):
        bpy.ops.wm.window_close()

    # import IPython
    # IPython.embed()


# ----------------------------------------------------------------------
# Generate HTML
#
# Run this after all other operations.

def generate_preview_html():
    """
    Compare OLD (moved to IMAGE_DIR_PREVIEW) vs NEW (in IMAGE_DIR_FINAL),
    but only for stems captured in this run.
    """
    html_path = os.path.join(IMAGE_DIR_PREVIEW, "index.html")
    with open(html_path, 'w', encoding='utf-8') as fh:
        fw = fh.write
        fw('<!DOCTYPE html>\n')
        fw('<html>\n')
        fw('<head>\n')
        fw('<meta charset="utf-8">\n')
        fw('<style>\n')
        fw('  body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,"Helvetica Neue",Arial,sans-serif;margin:16px}\n')
        fw('  table{table-layout:fixed;width:100%;border-collapse:collapse}\n')
        fw('  td,th{border:1px solid #ccc;vertical-align:top;padding:8px}\n')
        fw('  .cap{font:12px ui-monospace,Menlo,Consolas,monospace;color:#555;margin-top:6px}\n')
        fw('</style>\n')
        fw('</head>\n')
        fw('<body>\n')

        fw('<table>\n')
        fw('  <tr>\n')
        fw('    <th>Old Images</th>\n')
        fw('    <th>New Images (WebP)</th>\n')
        fw('  </tr>\n')

        if not CAPTURED_STEMS:
            fw('<tr><td colspan="2">No screenshots captured in this run.</td></tr>\n')

        for stem in CAPTURED_STEMS:
            old_abs = find_file_in_dir(IMAGE_DIR_PREVIEW, stem)
            new_abs = find_file_in_dir(IMAGE_DIR_FINAL, stem)

            fw('  <tr>\n')

            # Old
            fw('    <td>\n')
            if old_abs:
                old_rel = os.path.relpath(old_abs, IMAGE_DIR_PREVIEW)
                old_size = format_size(os.path.getsize(old_abs))
                old_name = os.path.basename(old_abs)
                fw(f'      <img src="{old_rel}" style="width:100%">\n')
                fw(f'      <div class="cap">{old_name} — {old_size}</div>\n')
            else:
                fw(f'      <div class="cap">Missing old file for: {stem}</div>\n')
            fw('    </td>\n')

            # New
            fw('    <td>\n')
            if new_abs:
                new_rel = os.path.relpath(new_abs, IMAGE_DIR_PREVIEW)
                new_size = format_size(os.path.getsize(new_abs))
                new_name = os.path.basename(new_abs)
                fw(f'      <img src="{new_rel}" style="width:100%">\n')
                fw(f'      <div class="cap">{new_name} — {new_size}</div>\n')
            else:
                fw(f'      <div class="cap">No new image for: {stem}</div>\n')
            fw('    </td>\n')

            fw('  </tr>\n')

        fw('</table>\n')
        fw('</body>\n')
        fw('</html>\n')


def screenshot_all(window):
    from bpy import context

    yield
    yield from screenshot_startup(window)
    # Currently not reliable for translations.
    if LANG=="en":
        yield from screenshot_splash_screen(window)
    yield from screenshot_preferences(window)

    bpy.app.use_event_simulate = False

    # Finally
    generate_preview_html()

    yield
    print(__doc__)
    sys.exit(0)


def main():
    from bpy import context

    setup_default_preferences(context.preferences)

    run_iter_from_timer(screenshot_all(context.window))


if __name__ == "__main__":
    main()
