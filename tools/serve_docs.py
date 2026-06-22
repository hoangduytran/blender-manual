#!/usr/bin/env python3
"""
Serve the Blender manual locally with multi-language switching.

After 'make build' builds each language into build/<lang>/, this server:
  - Routes  /          → redirect to the first BF_LANGS entry (usually /en/)
  - Routes  /<lang>/…  → serves build/<lang>/… as static files
  - Injects a small JS snippet into every HTML page that populates the
    built-in sidebar language-switcher (#version-langlist) with local links
    and re-runs via MutationObserver if version_switch.js overwrites the list
  - Injects a search overlay panel (keyboard shortcut: /) into every HTML page
    that queries the PO-based search index via /api/search (SSE streaming)
  - Returns 404 for version_switch.js requests so the remote versions.json
    fetch is suppressed (avoids CORS noise in local development)
  - Serves /api/search as an SSE endpoint powered by tools/search/

Usage:
    make serve                               # default port 8000, opens browser
    make serve SERVE_OPTS="--port 9000 --quiet"
    python3 tools/serve_docs.py --help
    python3 tools/serve_docs.py --kill       # stop existing server on that port
    python3 tools/serve_docs.py --restart --open
"""

import argparse
import dataclasses
import json
import logging
import mimetypes
import os
import signal
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Add tools/ to sys.path so 'search' package is importable
_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from common.constants import (  # type: ignore[import-not-found]  # noqa: E402
    DEFAULT_LANGUAGE,
    HTML_BUILDER_NAME,
    LC_MESSAGES,
    LOCALE_DIR,
    PO_FILENAME,
    SEARCH_INDEX_FILENAME,
    SearchField,
)

# debug_log lives next to this file in tools/; fall back silently if absent.
try:
    from debug_log import debug_log, is_debug_mode  # type: ignore[import-not-found]
except ImportError:
    def is_debug_mode() -> bool:  # type: ignore[misc]
        return os.getenv("DEBUG", "").lower() in {"true", "1", "yes", "on"}

    def debug_log(message: str, *args: object, **_kw: object) -> None:  # type: ignore[misc]
        if is_debug_mode():
            logging.debug(message, *args)

# PO-based search engine (tools/search/)
try:
    from search.index_loader import invalidate_cache, load_index_for, prewarm
    from search.index_searcher import run_parallel_search, shutdown_pool
    from search.po_watcher import MultiPOWatcher
    from search.searchable_record import SearchRequest
    _SEARCH_AVAILABLE = True
except ImportError as _e:
    logging.warning("PO search engine not available: %s", _e)
    _SEARCH_AVAILABLE = False


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


def _make_search_ui_snippet(lang: str) -> str:
    """Return the search overlay HTML+CSS+JS injected before </body>.

    Keyboard shortcut: press '/' to open.  Esc to close.

    Three independent checkboxes below the input:
      [x] Regex   [ ] Case Sensitive   [ ] Whole Word

    Options are sent as ?regex=1&cs=0&ww=0 to /api/search.
    Results stream in via SSE; each hit deep-links via Text Fragment URLs.
    """
    lang_js = json.dumps(lang)
    return f"""
<!-- PO search overlay — injected by tools/serve_docs.py -->
<style>
#ls-overlay{{
  display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);
  z-index:9999;align-items:flex-start;justify-content:center;padding-top:8vh
}}
#ls-panel{{
  background:#fff;border-radius:8px;box-shadow:0 8px 32px rgba(0,0,0,.25);
  width:min(680px,96vw);max-height:80vh;display:flex;flex-direction:column;
  overflow:hidden
}}
#ls-head{{padding:.75rem 1rem .5rem;border-bottom:1px solid #e8e8e8}}
#ls-row1{{display:flex;gap:.5rem;align-items:center}}
#ls-input{{
  flex:1;padding:.45rem .7rem;font-size:1rem;border:1px solid #ccc;
  border-radius:5px;min-width:0;outline:none
}}
#ls-input:focus{{border-color:#2980b9;box-shadow:0 0 0 2px rgba(41,128,185,.2)}}
#ls-close{{
  background:none;border:none;font-size:1.3rem;cursor:pointer;
  color:#888;padding:0 .3rem;line-height:1
}}
#ls-close:hover{{color:#333}}
#ls-opts{{display:flex;gap:.75rem;margin-top:.5rem;flex-wrap:wrap;align-items:center}}
.ls-opt{{
  display:flex;align-items:center;gap:.25rem;font-size:.8rem;
  color:#555;cursor:pointer;user-select:none
}}
.ls-opt input[type=checkbox]{{cursor:pointer;accent-color:#2980b9}}
#ls-status{{
  font-size:.8rem;color:#888;padding:.3rem 1rem .2rem;
  border-bottom:1px solid #f0f0f0;min-height:1.6rem
}}
#ls-results{{overflow-y:auto;padding:.5rem 1rem 1rem;flex:1}}
.ls-hit{{
  border-bottom:1px solid #f0f0f0;padding:.6rem 0;display:flex;
  flex-direction:column;gap:.2rem
}}
.ls-hit:last-child{{border-bottom:none}}
.ls-hit a{{
  color:#2980b9;text-decoration:none;font-size:.9rem;font-weight:500
}}
.ls-hit a:hover{{text-decoration:underline}}
.ls-breadcrumb{{font-size:.75rem;color:#27ae60;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.ls-snippet{{font-size:.85rem;color:#555;line-height:1.5}}
.ls-snippet mark{{background:#fff176;color:inherit;padding:0 1px;border-radius:2px}}
#ls-empty{{color:#888;font-size:.9rem;padding:.5rem 0}}
</style>

<div id="ls-overlay" role="dialog" aria-modal="true" aria-label="Search manual">
  <div id="ls-panel">
    <div id="ls-head">
      <div id="ls-row1">
        <input id="ls-input" type="search" placeholder="Search (Regex mode by default)…"
               autocomplete="off" aria-label="Search manual" spellcheck="false">
        <button id="ls-close" aria-label="Close search">✕</button>
      </div>
      <div id="ls-opts" role="group" aria-label="Search options">
        <label class="ls-opt" title="Treat query as a regular expression">
          <input type="checkbox" id="ls-regex" checked> Regex
        </label>
        <label class="ls-opt" title="Match uppercase and lowercase separately">
          <input type="checkbox" id="ls-cs"> Case Sensitive
        </label>
        <label class="ls-opt" title="Only match whole words (not mid-word substrings)">
          <input type="checkbox" id="ls-ww"> Whole Word
        </label>
      </div>
    </div>
    <div id="ls-status"></div>
    <div id="ls-results" role="list"></div>
  </div>
</div>

<script>
(function(){{
  var LANG = {lang_js};
  var overlay  = document.getElementById('ls-overlay');
  var panel    = document.getElementById('ls-panel');
  var input    = document.getElementById('ls-input');
  var closeBtn = document.getElementById('ls-close');
  var status   = document.getElementById('ls-status');
  var results  = document.getElementById('ls-results');
  var cbRegex  = document.getElementById('ls-regex');
  var cbCs     = document.getElementById('ls-cs');
  var cbWw     = document.getElementById('ls-ww');

  var currentES = null;
  var debTimer  = null;
  var total     = 0;

  /* ---- option checkboxes: re-search on change ---- */
  [cbRegex, cbCs, cbWw].forEach(function(cb){{
    cb.addEventListener('change', function(){{ _doSearch(input.value.trim()); }});
  }});

  /* ---- open/close ---- */
  function open(q){{
    overlay.style.display = 'flex';
    if (q !== undefined) input.value = q;
    input.focus();
    input.select();
    if (q) _doSearch(q);
  }}
  function close(){{
    overlay.style.display = 'none';
    _cancel();
  }}

  // Global hook so search.html redirect and sidebar form can open us
  window._lsOpen = open;

  document.addEventListener('keydown', function(e){{
    var tag = document.activeElement ? document.activeElement.tagName : '';
    if (e.key === '/' && tag !== 'INPUT' && tag !== 'TEXTAREA'){{
      e.preventDefault();
      open();
    }}
    if (e.key === 'Escape' && overlay.style.display !== 'none') close();
  }});
  closeBtn.addEventListener('click', close);
  overlay.addEventListener('click', function(e){{
    if (!panel.contains(e.target)) close();
  }});

  /* ---- intercept Sphinx sidebar search form ---- */
  function _interceptSphinxForms(){{
    document.querySelectorAll('form[action*="search.html"]').forEach(function(form){{
      form.addEventListener('submit', function(e){{
        e.preventDefault();
        var qf = form.querySelector('input[name="q"]');
        if (qf) open(qf.value.trim());
      }});
    }});
  }}
  if (document.readyState === 'loading'){{
    document.addEventListener('DOMContentLoaded', _interceptSphinxForms);
  }} else {{
    _interceptSphinxForms();
  }}

  /* ---- auto-open when URL has ?ls-q= (set by search.html redirect) ---- */
  (function(){{
    var params = new URLSearchParams(window.location.search);
    var lsq = params.get('ls-q');
    if (lsq){{
      if (document.readyState === 'loading'){{
        document.addEventListener('DOMContentLoaded', function(){{ open(lsq); }});
      }} else {{
        setTimeout(function(){{ open(lsq); }}, 0);
      }}
    }}
  }})();

  /* ---- search ---- */
  input.addEventListener('input', function(){{
    clearTimeout(debTimer);
    debTimer = setTimeout(function(){{ _doSearch(input.value.trim()); }}, 300);
  }});

  function _cancel(){{
    if (currentES){{ currentES.close(); currentES = null; }}
    clearTimeout(debTimer);
  }}

  function _doSearch(q){{
    _cancel();
    results.innerHTML = '';
    total = 0;
    if (!q){{ status.textContent = ''; return; }}

    status.textContent = 'Searching…';
    var url = '/api/search?q=' + encodeURIComponent(q)
            + '&lang='  + encodeURIComponent(LANG)
            + '&regex=' + (cbRegex.checked ? '1' : '0')
            + '&cs='    + (cbCs.checked    ? '1' : '0')
            + '&ww='    + (cbWw.checked    ? '1' : '0');
    var es = new EventSource(url);
    currentES = es;

    es.onmessage = function(evt){{
      var d = JSON.parse(evt.data);
      if (d.hits && d.hits.length){{
        d.hits.forEach(function(h){{ _appendHit(h); }});
      }}
      if (d.done){{
        status.textContent = total ? total + ' result' + (total !== 1 ? 's' : '') : 'No results';
        if (!total) results.innerHTML = '<div id="ls-empty">No results for <strong>' + _esc(q) + '</strong></div>';
        es.close(); currentES = null;
      }}
    }};

    es.onerror = function(){{
      status.textContent = 'Search error';
      if (es){{ es.close(); currentES = null; }}
    }};
  }}

  function _appendHit(h){{
    total++;
    var li = document.createElement('div');
    li.className = 'ls-hit';
    li.setAttribute('role', 'listitem');

    // Deep-link: page + section anchor + Text Fragment (:~:text=…)
    // Clicking opens the page, scrolls to #section, and the browser
    // highlights the matched span automatically (Chrome/Edge/Safari/Firefox).
    var href = h.fragment_url || (h.html_page + h.section_key);

    // Section label: strip leading /<lang>/ from the page path, keep section
    var pageLabel = (h.html_page || '').replace(/^\\/[^/]+\\//, '');
    var secLabel  = (h.section_key || '').replace(/^#/, '').replace(/-/g, ' ');

    var a = document.createElement('a');
    a.href = href;
    a.title = 'Open page and jump to section';
    a.textContent = pageLabel + (secLabel ? ' › ' + secLabel : '');

    // Breadcrumb: full URL path so the user can see exactly where it lives
    var bc = document.createElement('div');
    bc.className = 'ls-breadcrumb';
    bc.textContent = href.split(':~:')[0];   // strip :~:text= for display

    // Snippet with <mark>…</mark> around the matched span
    var snip = document.createElement('div');
    snip.className = 'ls-snippet';
    snip.innerHTML = h.snippet || '';

    li.appendChild(a);
    li.appendChild(bc);
    li.appendChild(snip);
    results.appendChild(li);
  }}

  function _esc(s){{
    return String(s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }}
}})();
</script>
"""


def _make_livereload_js(token: str) -> str:
    """Return the live-reload JS snippet injected just before </body>.

    `token` is the page's HTML mtime at serve time, baked in as a float. The
    snippet polls /__livereload?path=<this page> once a second; the server
    replies with the current mtime of the matching build/<lang>/… file. When
    that exceeds `token`, the page reloads with the freshly built content.

    A PO edit rebuilds only the documents referencing the changed msgid (via
    the incremental shard build + sphinx-autobuild under `make liveall`), so
    only the affected pages' mtimes advance and only those open tabs reload.
    """
    return f"""
<script>
/* live-reload injected by tools/serve_docs.py */
(function () {{
    var TOKEN = {token};
    var PATH = location.pathname;
    var DELAY = 1000;
    function poll() {{
        fetch('/__livereload?path=' + encodeURIComponent(PATH),
              {{ cache: 'no-store' }})
            .then(function (r) {{ return r.ok ? r.text() : null; }})
            .then(function (t) {{
                if (t !== null && parseFloat(t) > TOKEN) {{
                    location.reload();
                }} else {{
                    setTimeout(poll, DELAY);
                }}
            }})
            .catch(function () {{ setTimeout(poll, DELAY * 2); }});
    }}
    setTimeout(poll, DELAY);
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
    # Search index constants from ConfigRecord / conf.py (set in main())
    search_index_filename: str = SEARCH_INDEX_FILENAME
    html_builder_name: str = HTML_BUILDER_NAME
    default_language: str = DEFAULT_LANGUAGE

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        if self.quiet:
            return
        # Suppress the once-a-second live-reload polls so the console stays
        # readable; real page/asset/search requests are still logged.
        if getattr(self, "path", "").startswith("/__livereload"):
            return
        super().log_message(format, *args)

    def handle_one_request(self) -> None:
        try:
            super().handle_one_request()
        except (ConnectionResetError, BrokenPipeError):
            pass

    # ------------------------------------------------------------------
    def _url_to_fs(self, path: str) -> tuple[str | None, str | None]:
        """Map a /<lang>/… URL path to (lang, filesystem path).

        Returns (None, None) when the path carries no known language prefix.
        Shared by do_GET and the live-reload endpoint so both resolve files
        identically (per-lang dir overrides, directory-index expansion).
        """
        lang = None
        for code in self.available_langs:
            if path == f"/{code}" or path.startswith(f"/{code}/"):
                lang = code
                break
        if lang is None:
            return None, None

        sub = path[len(f"/{lang}"):]  # everything after /<lang>
        if not sub or sub == "/":
            sub = "/index.html"
        if sub.endswith("/"):
            sub += "index.html"

        base_dir = self.lang_dirs.get(lang) or os.path.join(self.build_dir, lang)
        return lang, os.path.join(base_dir, sub.lstrip("/"))

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Redirect root to default language
        if path in ("", "/"):
            self._redirect(f"/{self.default_lang}/")
            return

        # Live-reload poll endpoint (used by the injected JS snippet)
        if path == "/__livereload":
            qs = urllib.parse.parse_qs(parsed.query)
            self._handle_livereload(qs)
            return

        # PO-based search SSE endpoint — language-agnostic route
        if path == "/api/search":
            qs = urllib.parse.parse_qs(parsed.query)
            self._handle_api_search(qs)
            return

        # Detect language from URL prefix
        lang = None
        for code in self.available_langs:
            if path == f"/{code}" or path.startswith(f"/{code}/"):
                lang = code
                break

        if lang is None:
            self._send_404()
            return

        # Block version_switch.js so the remote versions.json fetch is skipped
        if path.endswith("version_switch.js"):
            self._send_404()
            return

        # Intercept Sphinx search.html → redirect to our overlay
        if path.endswith("/search.html") and _SEARCH_AVAILABLE:
            qs_dict = urllib.parse.parse_qs(parsed.query)
            q = qs_dict.get("q", [""])[0].strip()
            if q:
                self._redirect(f"/{lang}/?ls-q={urllib.parse.quote(q)}")
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
    def _handle_livereload(self, qs: dict) -> None:
        """Reply with the current mtime of the page named in ?path=.

        The injected JS passes its own location.pathname; we resolve it to the
        same build/<lang>/… file do_GET would serve and return that file's
        mtime as plain text. A missing file yields 0 so a mid-rebuild blip
        never triggers a spurious reload (the JS only reloads on a strict
        increase over the baseline baked into the page).
        """
        target = qs.get("path", [""])[0].split("?")[0].split("#")[0]
        mtime = 0.0
        if target:
            _, fs_path = self._url_to_fs(target)
            if fs_path and os.path.isfile(fs_path):
                try:
                    mtime = os.path.getmtime(fs_path)
                except OSError:
                    mtime = 0.0

        body = f"{mtime:.6f}".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    # ------------------------------------------------------------------
    def _handle_api_search(self, qs: dict) -> None:
        """SSE endpoint: /api/search?q=…&lang=…&mode=…&field=…&limit=…

        Streams ``data: {"hits":[…]}`` events as worker batches complete,
        then a final ``data: {"done":true,"total":N}`` sentinel.
        """
        if not _SEARCH_AVAILABLE:
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"search engine not available"}')
            return

        req = SearchRequest.from_qs(qs)
        # Source language (English) has no translation: its index carries empty
        # msgstr, so search must run on msgid only. (SearchRequest is frozen.)
        is_source_language = req.lang == self.default_language
        if is_source_language:
            req = dataclasses.replace(req, field=SearchField.MSGID)
        build_dir = Path(self.build_dir)

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        def send(data: dict) -> bool:
            try:
                self.wfile.write(
                    f"data: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")
                )
                self.wfile.flush()
                return True
            except (BrokenPipeError, ConnectionResetError, OSError):
                return False

        if not req.query:
            send({"done": True, "total": 0})
            return

        idx = load_index_for(
            build_dir, req.lang,
            self.search_index_filename,
            self.html_builder_name,
            self.default_language,
        )
        if idx is None:
            send({"error": f"index not found for lang={req.lang}", "done": True, "total": 0})
            return

        debug_log("api/search query=%r lang=%s regex=%s cs=%s ww=%s",
                  req.query, req.lang, req.regex, req.case_sensitive, req.whole_word)
        total = 0
        try:
            # Collect all hits so we can sort by score (exact-phrase / msgstr first).
            # Search is typically < 200 ms so collecting before sending is fine.
            all_hits = []
            for hits in run_parallel_search(idx, req):
                all_hits.extend(hits)
            all_hits.sort(key=lambda h: h.score, reverse=True)

            # Deduplicate by fragment_url so the same page+section is not listed twice.
            seen_urls: set[str] = set()
            deduped = []
            for h in all_hits:
                key = h.fragment_url or (h.html_page + h.section_key)
                if key not in seen_urls:
                    seen_urls.add(key)
                    deduped.append(h)

            payload = [
                {
                    "msgid":       h.msgid,
                    "msgstr":      h.msgstr,
                    "html_page":   h.html_page,
                    "section_key": h.section_key,
                    "fragment_url":h.fragment_url,
                    "snippet":     h.snippet,
                    "match_field": h.match_field,
                    "score":       h.score,
                }
                for h in deduped
            ]
            if payload and not send({"hits": payload}):
                return
            total = len(deduped)
        except Exception as exc:
            debug_log("api/search error: %s", exc)
            send({"error": str(exc), "done": True, "total": total})
            return

        send({"done": True, "total": total})

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

        # Baseline mtime baked into the live-reload snippet: the page reloads
        # once the server reports a newer mtime for this same file.
        try:
            token = os.path.getmtime(fs_path)
        except OSError:
            token = 0.0

        # Inject lang-switcher + search UI + live-reload before </body>
        snippet = _make_lang_switcher_js(lang, self.available_langs)
        if _SEARCH_AVAILABLE:
            snippet += _make_search_ui_snippet(lang)
        snippet += _make_livereload_js(f"{token:.6f}")

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
# Thread-pool HTTP server
# ---------------------------------------------------------------------------

class ThreadedHTTPServer(HTTPServer):
    """HTTPServer that handles each request in a bounded thread pool."""

    def __init__(
        self,
        server_address: tuple[str, int],
        RequestHandlerClass: type,
        max_workers: int = 2,
    ) -> None:
        super().__init__(server_address, RequestHandlerClass)
        self._pool = ThreadPoolExecutor(max_workers=max_workers)

    def process_request(self, request: object, client_address: object) -> None:  # type: ignore[override]
        future = self._pool.submit(
            self.finish_request, request, client_address,  # type: ignore[arg-type]
        )
        future.add_done_callback(
            lambda f: self._on_request_done(f, request, client_address)
        )

    def _on_request_done(self, future: object, request: object, client_address: object) -> None:
        from concurrent.futures import Future
        exc = future.exception() if isinstance(future, Future) else None  # type: ignore[union-attr]
        if exc:
            self.handle_error(request, client_address)  # type: ignore[arg-type]
        self.shutdown_request(request)  # type: ignore[arg-type]

    def server_close(self) -> None:
        self._pool.shutdown(wait=False)
        super().server_close()


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
    ap.add_argument("--no-search-html-rebuild", action="store_true",
                    help=(
                        "When a PO file changes, rebuild only the search index, "
                        "not HTML. Use under 'make liveall', where sphinx-autobuild "
                        "already rebuilds HTML — this avoids a double build."
                    ))
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--kill", action="store_true",
                       help="Kill process(es) listening on host:port and exit")
    group.add_argument("--restart", action="store_true",
                       help="Kill existing listener then start this server")
    group.add_argument("--resume", action="store_true",
                       help=(
                           "Read saved options from build/.serve_docs_opts and restart "
                           "with the same --build-dir/--langs/--port/--host as last time. "
                           "Works on all platforms — no shell grep/cut needed."
                       ))
    args = ap.parse_args()

    # --resume: load last-saved options from the state file, then restart.
    if args.resume:
        _default_state = os.path.join(
            args.build_dir if args.build_dir else os.path.join(project_root, "build"),
            ".serve_docs_opts",
        )
        if os.path.isfile(_default_state):
            _saved: dict[str, str] = {}
            with open(_default_state) as _sf:
                for _line in _sf:
                    _parts = _line.strip().split(None, 1)
                    if len(_parts) == 2:
                        _saved[_parts[0]] = _parts[1]
            if "--build-dir" in _saved:
                args.build_dir = _saved["--build-dir"]
            if "--langs" in _saved:
                args.langs = _saved["--langs"]
            if "--port" in _saved:
                try:
                    args.port = int(_saved["--port"])
                except ValueError:
                    pass
            if "--host" in _saved:
                args.host = _saved["--host"]
        else:
            logging.warning("No state file found at %s; using current defaults.", _default_state)
        args.restart = True
        args.resume = False

    # Scan locale/ for all installed translation catalogs.
    # English is the source language (no PO file needed) and is always first.
    locale_root = os.path.join(project_root, LOCALE_DIR)
    locale_langs: list[str] = []
    if os.path.isdir(locale_root):
        for entry in sorted(os.listdir(locale_root)):
            po = os.path.join(locale_root, entry, LC_MESSAGES, PO_FILENAME)
            if os.path.isfile(po) and entry != DEFAULT_LANGUAGE:
                locale_langs.append(entry)
    all_locale_langs: list[str] = [DEFAULT_LANGUAGE] + locale_langs

    if args.langs is not None:
        built = args.langs.split()
    else:
        built = all_locale_langs
        if len(built) > 1:
            logging.info("Auto-detected languages from locale/: %s", " ".join(built))
        else:
            logging.info("No translation catalogs found in locale/; serving English only.")

    # Merge: built langs first (preserving order), then any extra locale langs.
    seen: set[str] = set(built)
    extra = [lg for lg in all_locale_langs if lg not in seen]
    available = built + extra   # switcher shows all; routing 404s unbuilt ones

    default_lang = DEFAULT_LANGUAGE if DEFAULT_LANGUAGE in available else (available[0] if available else DEFAULT_LANGUAGE)

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

    # Build per-language directory map
    lang_dirs: dict[str, str] = {}
    html_fallback = os.path.join(args.build_dir, HTML_BUILDER_NAME)
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

    workers = max(2, (os.cpu_count() or 4) - 2)
    try:
        server = ThreadedHTTPServer((args.host, args.port), DocsHandler,
                                    max_workers=workers)
    except OSError as exc:
        logging.error("Cannot bind to %s:%s — %s", args.host, args.port, exc)
        sys.exit(1)
    logging.info("Thread pool: %d workers (cpu_count - 2)", workers)

    # Persist effective options so 'make restart' can replay them without
    # the caller needing to repeat --langs / --port / --host / --build-dir.
    _state_path = os.path.join(args.build_dir, ".serve_docs_opts")
    try:
        with open(_state_path, "w") as _sf:
            _sf.write(
                f"--build-dir {args.build_dir}\n"
                f"--langs {' '.join(built)}\n"
                f"--port {args.port}\n"
                f"--host {args.host}\n"
            )
    except OSError:
        pass  # non-fatal; restart will fall back to Makefile defaults

    # Resolve project-level search settings from ConfigRecord / manual/conf.py.
    _search_index_filename = SEARCH_INDEX_FILENAME
    _html_builder_name = HTML_BUILDER_NAME
    _default_language = DEFAULT_LANGUAGE
    try:
        from translations.smart_mo_compile import ConfigRecord as _CR
        _pcfg = _CR.from_project(Path(project_root), DEFAULT_LANGUAGE)
        _search_index_filename = _pcfg.search_index_filename
        _html_builder_name = _pcfg.html_builder_name
        _default_language = _pcfg.default_language
    except (ImportError, SystemExit, Exception):
        pass

    # Pre-warm the PO search index and start PO file watchers
    if _SEARCH_AVAILABLE:
        build_dir_path = Path(args.build_dir)

        DocsHandler.search_index_filename = _search_index_filename
        DocsHandler.html_builder_name = _html_builder_name
        DocsHandler.default_language = _default_language

        for lang in available:
            # Pre-warm: load index into cache before first request
            threading.Thread(
                target=prewarm,
                args=(build_dir_path, lang),
                kwargs={
                    "index_filename": _search_index_filename,
                    "html_builder_name": _html_builder_name,
                    "default_language": _default_language,
                },
                name=f"search-prewarm-{lang}",
                daemon=True,
            ).start()

        # MultiPOWatcher: single thread watching ALL locale/<lang>/blender_manual.po
        # rebuild_html=False under 'make liveall' — sphinx-autobuild already
        # rebuilds HTML there, so the watcher only refreshes the search index.
        MultiPOWatcher(
            project_root=Path(project_root),
            build_dir=build_dir_path,
            invalidate=invalidate_cache,
            rebuild_html=not args.no_search_html_rebuild,
        ).start()
        debug_log("MultiPOWatcher started (watching all languages, rebuild_html=%s)",
                  not args.no_search_html_rebuild)

    base_url = f"http://{args.host}:{args.port}"
    logging.info("\nServing Blender manual at %s", base_url)
    for lang in available:
        logging.info("  %s  →  %s/%s/", LANG_NAMES.get(lang, lang), base_url, lang)
    if _SEARCH_AVAILABLE:
        logging.info("  Search: %s/api/search?q=…&lang=vi&mode=regex", base_url)
    logging.info("Live-reload on: edited pages refresh automatically after rebuild.")
    logging.info("Press Ctrl-C to stop.\n")

    if args.open:
        webbrowser.open(f"{base_url}/{default_lang}/")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("\nShutting down.")
        if _SEARCH_AVAILABLE:
            shutdown_pool()
        server.server_close()


if __name__ == "__main__":
    main()
