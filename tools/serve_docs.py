#!/usr/bin/env python3
"""
Serve the Blender manual locally with multi-language switching.

After 'make build' builds each language into build/<lang>/, this server:
  - Routes  /          → redirect to the first BF_LANGS entry (usually /en/)
  - Routes  /<lang>/…  → serves build/<lang>/… as static files
  - Injects a small JS snippet into every HTML page that populates the
    built-in sidebar language-switcher (#version-langlist) with local links
    and re-runs via MutationObserver if version_switch.js overwrites the list
  - Returns 404 for version_switch.js requests so the remote versions.json
    fetch is suppressed (avoids CORS noise in local development)

Usage:
    make serve                               # default port 8000, opens browser
    make serve SERVE_OPTS="--port 9000 --quiet"
    python3 tools/serve_docs.py --help
    python3 tools/serve_docs.py --kill       # stop existing server on that port
    python3 tools/serve_docs.py --restart --open
"""

import argparse
import logging
import mimetypes
import os
import signal
import subprocess
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

# ---------------------------------------------------------------------------
# Human-readable language names — full set from the Blender manual translations
# repository (projects.blender.org/blender/blender-manual-translations).
# Unknown codes fall back to the code itself in the switcher.
# ---------------------------------------------------------------------------
LANG_NAMES: dict[str, str] = {
    "en": "English",
    "ca": "Català",
    "de": "Deutsch",
    "es": "Español",
    "fr": "Français",
    "id": "Bahasa Indonesia",
    "it": "Italiano",
    "ja": "日本語",
    "ka": "ქართული",
    "ko": "한국어",
    "nl": "Nederlands",
    "pt": "Português",
    "ru": "Русский",
    "sk": "Slovenčina",
    "sl": "Slovenščina",
    "sr": "Српски",
    "sv": "Svenska",
    "sw": "Kiswahili",
    "th": "ภาษาไทย",
    "uk": "Українська",
    "vi": "Tiếng Việt",
    "zh-hans": "中文(简体)",
    "zh-hant": "中文(繁體)",
}


def _make_lang_switcher_js(current_lang: str, available: list[str]) -> str:
    """Return the JS snippet injected just before </body>.

    version_switch.js is blocked (404) to suppress remote network fetches.
    This snippet provides a complete replacement: popover toggle for both
    buttons, a 'Local build' placeholder for the version list, and local
    /<lang>/same-path links for the language list.
    """
    lang_map = {code: LANG_NAMES.get(code, code) for code in available}
    lang_map_js = ", ".join(
        f'"{k}": "{v}"' for k, v in lang_map.items()
    )
    return f"""
<script>
/* local-dev-switcher injected by tools/serve_docs.py (replaces version_switch.js) */
(function () {{
    var LANGS = {{ {lang_map_js} }};
    var CURRENT = "{current_lang}";

    /* Minimal popover: wire click / document-click / mouseleave to show/hide */
    function makePopover(btnId) {{
        var btn = document.getElementById(btnId);
        if (!btn) return;
        var dialog = btn.nextElementSibling;
        var isOpen = false;

        function show() {{
            btn.classList.add('version-btn-open');
            btn.setAttribute('aria-pressed', 'true');
            dialog.setAttribute('aria-hidden', 'false');
            dialog.style.display = 'block';
            isOpen = true;
        }}
        function hide() {{
            btn.classList.remove('version-btn-open');
            btn.setAttribute('aria-pressed', 'false');
            dialog.setAttribute('aria-hidden', 'true');
            dialog.style.display = 'none';
            isOpen = false;
        }}

        btn.addEventListener('click', function (e) {{
            e.preventDefault();
            e.stopPropagation();
            isOpen ? hide() : show();
        }});
        document.addEventListener('click', function (e) {{
            if (isOpen && !btn.parentNode.contains(e.target)) hide();
        }});
        btn.parentNode.addEventListener('mouseleave', function () {{
            if (isOpen) hide();
        }});
    }}

    /* Version list: 'Local build' placeholder (no remote fetch) */
    function setupVersion() {{
        var list = document.getElementById('version-vsnlist');
        if (!list) return;
        while (list.firstChild) list.removeChild(list.firstChild);
        var li = document.createElement('li');
        li.setAttribute('role', 'presentation');
        li.style.cssText = 'padding:6px 4px;color:gray;font-size:90%;text-align:center';
        li.textContent = 'Local build';
        list.appendChild(li);
    }}

    /* Language list: local /<lang>/same-path links */
    function setupLang() {{
        var btn  = document.getElementById('lang-popover');
        var list = document.getElementById('version-langlist');
        if (!btn || !list) return;

        btn.textContent = LANGS[CURRENT] || CURRENT;

        while (list.firstChild) list.removeChild(list.firstChild);

        var p    = location.pathname;
        var rest = p.replace(new RegExp('^\\/' + CURRENT + '(\\/|$)'), '/') || '/';

        Object.keys(LANGS).forEach(function (code) {{
            var li = document.createElement('li');
            li.setAttribute('role', 'presentation');
            if (code === CURRENT) {{
                li.className = 'selected';
                var span = document.createElement('span');
                span.textContent = LANGS[code];
                span.setAttribute('tabindex', '-1');
                span.setAttribute('aria-current', 'page');
                li.appendChild(span);
            }} else {{
                var href = '/' + code + rest + location.search + location.hash;
                var a = document.createElement('a');
                a.href = href;
                a.textContent = LANGS[code];
                a.setAttribute('tabindex', '-1');
                a.setAttribute('role', 'menuitem');
                li.appendChild(a);
            }}
            list.appendChild(li);
        }});
    }}

    function setup() {{
        makePopover('version-popover');
        makePopover('lang-popover');
        setupVersion();
        setupLang();
    }}

    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', setup);
    }} else {{
        setup();
    }}
}})();
</script>
"""


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

class DocsHandler(BaseHTTPRequestHandler):
    build_dir: str = "build"
    lang_dirs: dict[str, str] = {}   # populated in main(); maps lang code → fs dir
    default_lang: str = "en"
    available_langs: list[str] = ["en"]
    quiet: bool = False

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        if not self.quiet:
            super().log_message(format, *args)

    def handle_one_request(self) -> None:
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    # ------------------------------------------------------------------
    def do_GET(self) -> None:
        path = self.path.split("?")[0].split("#")[0]

        # Redirect root to default language
        if path in ("", "/"):
            self._redirect(f"/{self.default_lang}/")
            return

        # Detect language from URL prefix
        lang = None
        for code in self.available_langs:
            if path == f"/{code}" or path.startswith(f"/{code}/"):
                lang = code
                break

        if lang is None:
            # Unknown prefix — 404
            self._send_404()
            return

        # Block version_switch.js so the remote versions.json fetch is skipped
        if path.endswith("version_switch.js"):
            self._send_404()
            return

        # Map URL path to filesystem path (use per-lang dir, may differ from build_dir/lang)
        sub = path[len(f"/{lang}"):]  # everything after /<lang>
        if not sub or sub == "/":
            sub = "/index.html"
        if sub.endswith("/"):
            sub += "index.html"

        base_dir = self.lang_dirs.get(lang) or os.path.join(self.build_dir, lang)
        fs_path = os.path.join(base_dir, sub.lstrip("/"))

        if not os.path.isfile(fs_path):
            self._send_404()
            return

        # Serve the file, injecting JS for HTML pages
        ctype, _ = mimetypes.guess_type(fs_path)
        ctype = ctype or "application/octet-stream"

        if "html" in ctype:
            self._serve_html(fs_path, lang, ctype)
        else:
            self._serve_static(fs_path, ctype)

    # ------------------------------------------------------------------
    def _redirect(self, location: str) -> None:
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def _send_404(self) -> None:
        self.send_response(404)
        self.end_headers()

    def _serve_static(self, fs_path: str, ctype: str) -> None:
        with open(fs_path, "rb") as fh:
            data = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _serve_html(self, fs_path: str, lang: str, ctype: str) -> None:
        with open(fs_path, "rb") as fh:
            raw = fh.read()
        text = raw.decode("utf-8", errors="replace")

        # Inject language switcher JS before </body>
        snippet = _make_lang_switcher_js(lang, self.available_langs)
        idx = text.lower().rfind("</body>")
        if idx >= 0:
            text = text[:idx] + snippet + text[idx:]
        else:
            text += snippet

        data = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass


# ---------------------------------------------------------------------------
# Process helpers
# ---------------------------------------------------------------------------

def _find_pids(port: int) -> list[int]:
    try:
        r = subprocess.run(
            ["lsof", "-ti", f"tcp:{port}", "-sTCP:LISTEN"],
            capture_output=True, text=True, check=False,
        )
        return [int(p) for p in r.stdout.strip().split() if p.isdigit()]
    except Exception:
        return []


def _kill_pids(pids: list[int]) -> None:
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            logging.info("Terminated pid %s", pid)
        except ProcessLookupError:
            pass


def _wait_for_port_release(port: int) -> bool:
    """Wait briefly for terminated listeners to release *port*."""
    for _ in range(20):
        if not _find_pids(port):
            return True
        time.sleep(0.25)
    return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Resolve project root (two levels up from this script: tools/ → project/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    ap = argparse.ArgumentParser(
        description="Serve Blender manual with local language switching.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--build-dir", default=os.path.join(project_root, "build"),
                    help="Directory produced by 'make build' (default: build/)")
    ap.add_argument("--langs", default=None,
                    help=(
                        "Space-separated language codes to serve. "
                        "Defaults to auto-detection: all locale/<lang>/LC_MESSAGES/"
                        "blender_manual.po entries found under the project root, "
                        "with 'en' always first."
                    ))
    ap.add_argument("--port", type=int, default=8000, help="TCP port (default: 8000)")
    ap.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    ap.add_argument("--open", action="store_true", help="Open browser after starting")
    ap.add_argument("--quiet", action="store_true", help="Suppress per-request logging")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--kill", action="store_true",
                       help="Kill process(es) listening on host:port and exit")
    group.add_argument("--restart", action="store_true",
                       help="Kill existing listener then start this server")
    args = ap.parse_args()

    # Scan locale/ for all installed translation catalogs.
    # English is the source language (no PO file needed) and is always first.
    locale_root = os.path.join(project_root, "locale")
    locale_langs: list[str] = []
    if os.path.isdir(locale_root):
        for entry in sorted(os.listdir(locale_root)):
            po = os.path.join(locale_root, entry, "LC_MESSAGES", "blender_manual.po")
            if os.path.isfile(po) and entry != "en":
                locale_langs.append(entry)
    all_locale_langs: list[str] = ["en"] + locale_langs

    if args.langs is not None:
        # Explicit --langs controls what routes are pre-built/served.
        # All locale/ languages are added to the switcher on top so users can
        # see every available language regardless of what was built this run.
        built = args.langs.split()
    else:
        # No --langs: serve and show all locale languages.
        built = all_locale_langs
        if len(built) > 1:
            logging.info("Auto-detected languages from locale/: %s", " ".join(built))
        else:
            logging.info("No translation catalogs found in locale/; serving English only.")

    # Merge: built langs first (preserving order), then any extra locale langs.
    seen: set[str] = set(built)
    extra = [lg for lg in all_locale_langs if lg not in seen]
    available = built + extra   # switcher shows all; routing 404s unbuilt ones

    default_lang = "en" if "en" in available else (available[0] if available else "en")

    # Handle existing listeners
    existing = _find_pids(args.port)
    if existing:
        if args.kill:
            _kill_pids(existing)
            if not _wait_for_port_release(args.port):
                logging.error("Port %s still in use; aborting.", args.port)
                sys.exit(1)
            if not args.quiet:
                logging.info("Killed. Exiting.")
            sys.exit(0)
        if args.restart:
            _kill_pids(existing)
            if not _wait_for_port_release(args.port):
                logging.error("Port %s still in use; aborting.", args.port)
                sys.exit(1)
        else:
            logging.error(
                "Port %s is already in use. Use --kill or --restart.", args.port
            )
            sys.exit(1)
    elif args.kill:
        if not args.quiet:
            logging.info("No process listening on %s:%s", args.host, args.port)
        sys.exit(0)

    # Build per-language directory map, falling back to build/html/ for the
    # default language when its dedicated <lang>/ directory hasn't been built yet
    # (e.g. after 'make html' but before 'make build').
    lang_dirs: dict[str, str] = {}
    html_fallback = os.path.join(args.build_dir, "html")
    truly_missing: list[str] = []
    for lang in available:
        dedicated = os.path.join(args.build_dir, lang)
        if os.path.isdir(dedicated):
            lang_dirs[lang] = dedicated
        elif lang == default_lang and os.path.isdir(html_fallback):
            lang_dirs[lang] = html_fallback
            logging.info(
                "No build/%s/ found; falling back to build/html/ for /%s/"
                " — run 'make build' for full multi-lang support.",
                lang, lang,
            )
        else:
            lang_dirs[lang] = dedicated  # will 404; listed in warning below
            truly_missing.append(lang)
    if truly_missing:
        logging.warning(
            "Missing build output for: %s — run 'make build' first.",
            " ".join(truly_missing),
        )

    # Configure handler class
    DocsHandler.build_dir = args.build_dir
    DocsHandler.lang_dirs = lang_dirs
    DocsHandler.default_lang = default_lang
    DocsHandler.available_langs = available
    DocsHandler.quiet = args.quiet

    try:
        server = HTTPServer((args.host, args.port), DocsHandler)
    except OSError as exc:
        logging.error("Cannot bind to %s:%s — %s", args.host, args.port, exc)
        sys.exit(1)

    base_url = f"http://{args.host}:{args.port}"
    logging.info("\nServing Blender manual at %s", base_url)
    for lang in available:
        logging.info("  %s  →  %s/%s/", LANG_NAMES.get(lang, lang), base_url, lang)
    logging.info("Press Ctrl-C to stop.\n")

    if args.open:
        webbrowser.open(f"{base_url}/{default_lang}/")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
