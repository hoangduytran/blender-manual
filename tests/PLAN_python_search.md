# Plan: Server-Side Python Search in serve_docs.py

## Problem

Sphinx search is 100 % client-side JavaScript. Two reasons it fails for Vietnamese:

1. **English Porter stemmer** strips tonal marks: `này` → `nay`, `bản` → `ban`, etc.
   The stemmer runs during `sphinx-build` when it generates `searchindex.js`.
   By the time the browser executes the JS, the Vietnamese strings are already corrupted.

2. **`field_body` nodes not indexed.** RST field lists (`:Label: value`) produce
   `field_body` docutils nodes. Sphinx's `IndexBuilder` skips these nodes, so text
   inside field lists never appears in `searchindex.js` regardless of language.

Neither issue is fixable without patching Sphinx itself. A server-side approach
bypasses both limitations.

## Proposed Solution

Intercept `GET /<lang>/search.html?q=<term>` in `serve_docs.py` and:

1. Walk `build/<lang>/**/*.html` with Python's stdlib `os.walk`.
2. Strip HTML tags with `html.parser.HTMLParser` to get plain text.
3. Do a plain `str.lower().find()` — no stemming, full Unicode.
4. Return a styled results HTML page with clickable titles and text excerpts,
   with the query term highlighted using `<mark>`.

When `?q=` is absent or empty, fall through to the existing static file handler
so the original Sphinx `search.html` page still loads normally.

---

## Implementation Steps

### Step 1 — Add imports to `serve_docs.py`

```python
import html as _html       # html.escape() for XSS-safe output
import urllib.parse        # urlparse / parse_qs for query string
```

### Step 2 — Add `_TextExtractor` class (before `DocsHandler`)

`html.parser.HTMLParser` subclass that:
- Skips tag content for: `script`, `style`, `head`, `nav`, `header`, `footer`
  (these contain menus, sidebars, JS — not page content).
- Separately captures `<title>…</title>` for the result heading.
- Joins remaining text into one whitespace-normalised string via `get_text()`.

```python
class _TextExtractor(html.parser.HTMLParser):
    _SKIP_TAGS = frozenset({"script", "style", "head", "nav", "header", "footer"})

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._chunks: list[str] = []
        self._title_buf: list[str] = []
        self._in_title = False
        self.title: str = ""

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag in self._SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
        elif tag == "title":
            self._in_title = False
            if not self.title:
                self.title = "".join(self._title_buf).strip()

    def handle_data(self, data):
        if self._in_title:
            self._title_buf.append(data)
        if self._skip_depth == 0 and not self._in_title:
            stripped = data.strip()
            if stripped:
                self._chunks.append(stripped)

    def get_text(self) -> str:
        return " ".join(self._chunks)
```

### Step 3 — Update `do_GET` in `DocsHandler`

Replace the current first line:
```python
path = self.path.split("?")[0].split("#")[0]
```
with proper `urllib.parse` parsing, then add the search intercept after the
`lang` is determined and the `version_switch.js` block:

```python
# Intercept search with Python backend when ?q= is present and non-empty
if path == f"/{lang}/search.html":
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
    query = qs.get("q", [""])[0].strip()
    if query:
        self._serve_search_results(lang, query)
        return
# ... existing static file logic follows unchanged ...
```

### Step 4 — Add `_serve_search_results` method

```python
def _serve_search_results(self, lang: str, query: str) -> None:
    page_html = self._do_search(lang, query)
    data = page_html.encode("utf-8")
    self.send_response(200)
    self.send_header("Content-Type", "text/html; charset=utf-8")
    self.send_header("Content-Length", str(len(data)))
    self.end_headers()
    try:
        self.wfile.write(data)
    except (BrokenPipeError, ConnectionResetError):
        pass
```

### Step 5 — Add `_do_search` method

```python
_SEARCH_SKIP_DIRS  = frozenset({"_static", "_sources", "_images", ".doctrees"})
_SEARCH_SKIP_FILES = frozenset({"search.html", "genindex.html",
                                 "py-modindex.html", "404.html"})

def _do_search(self, lang: str, query: str) -> str:
    base_dir = self.lang_dirs.get(lang) or os.path.join(self.build_dir, lang)
    if not os.path.isdir(base_dir):
        return self._render_search_page(lang, query, [])

    results: list[tuple[str, str, str]] = []   # (url, title, excerpt)
    q_lower = query.lower()

    for dirpath, dirnames, filenames in os.walk(base_dir):
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in _SEARCH_SKIP_DIRS and not d.startswith(".")
        )
        for fname in sorted(filenames):
            if not fname.endswith(".html") or fname in _SEARCH_SKIP_FILES:
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                raw = open(fpath, "rb").read()
            except OSError:
                continue

            ext = _TextExtractor()
            try:
                ext.feed(raw.decode("utf-8", errors="replace"))
            except Exception:
                continue

            plain = ext.get_text()
            idx = plain.lower().find(q_lower)
            if idx < 0:
                continue

            # Excerpt: ±120 chars around first match
            s = max(0, idx - 120)
            e = min(len(plain), idx + len(query) + 120)
            excerpt = ("…" if s > 0 else "") + plain[s:e] + ("…" if e < len(plain) else "")

            # Clean " — Blender Manual" suffix from page title
            title = ext.title or fname
            for sep in (" — ", " - "):
                if sep in title:
                    title = title[: title.index(sep)]
                    break

            rel = os.path.relpath(fpath, base_dir)
            url = f"/{lang}/{rel.replace(os.sep, '/')}"
            results.append((url, title, excerpt))
            if len(results) >= 50:
                break
        if len(results) >= 50:
            break

    return self._render_search_page(lang, query, results)
```

### Step 6 — Add `_highlight_excerpt` helper

Splits plain text around every case-insensitive occurrence of `query`,
escaping each segment with `_html.escape()`, and wraps each match in `<mark>`.

```python
def _highlight_excerpt(self, text: str, query: str) -> str:
    parts: list[str] = []
    t_lower = text.lower()
    q_lower = query.lower()
    q_len = len(query)
    last = 0
    while True:
        idx = t_lower.find(q_lower, last)
        if idx < 0:
            parts.append(_html.escape(text[last:]))
            break
        parts.append(_html.escape(text[last:idx]))
        parts.append(f"<mark>{_html.escape(text[idx:idx + q_len])}</mark>")
        last = idx + q_len
    return "".join(parts)
```

### Step 7 — Add `_render_search_page` method

Returns a self-contained HTML page with:
- Minimal inline CSS (matches Furo colour palette: `#2980b9` blue, `#27ae60` green)
- A re-search `<form>` so the user can refine the query
- A "← Back to <lang> manual" link
- Result count line
- Each result: linked `<h3>` title, URL breadcrumb, excerpt with `<mark>` highlights

```python
def _render_search_page(
    self, lang: str, query: str,
    results: list[tuple[str, str, str]],
) -> str:
    q_e = _html.escape(query)
    lang_e = _html.escape(lang)
    lang_name_e = _html.escape(LANG_NAMES.get(lang, lang))
    count_label = (
        f"{len(results)} result{'s' if len(results) != 1 else ''}"
        if len(results) < 50 else "50+ results"
    )

    items: list[str] = []
    for url, title, excerpt in results:
        items.append(f"""
<div class="sr">
  <h3><a href="{_html.escape(url)}">{_html.escape(title)}</a></h3>
  <div class="sr-url">{_html.escape(url)}</div>
  <p>{self._highlight_excerpt(excerpt, query)}</p>
</div>""")

    body = "".join(items) if results else f'<p class="nores">No results for <strong>{q_e}</strong>.</p>'
    count_line = f'<p class="count">{count_label} for <strong>{q_e}</strong></p>' if results else ""

    return f"""<!DOCTYPE html>
<html lang="{lang_e}">
<head>
<meta charset="UTF-8">
<title>Search: {q_e} — Blender Manual</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
     max-width:900px;margin:0 auto;padding:2rem 1rem;color:#333}}
h1{{font-size:1.4rem;color:#2980b9;margin-bottom:1rem}}
.sb{{display:flex;gap:.5rem;margin-bottom:1.5rem}}
.sb input{{flex:1;padding:.5rem .75rem;font-size:1rem;border:1px solid #ccc;border-radius:4px}}
.sb button{{padding:.5rem 1rem;background:#2980b9;color:#fff;border:none;border-radius:4px;cursor:pointer}}
.count{{color:#555;margin-bottom:1.5rem}}
.sr{{border-bottom:1px solid #eee;padding:1rem 0}}
.sr h3{{margin:0 0 .2rem;font-size:1.05rem}}
.sr h3 a{{color:#2980b9;text-decoration:none}}
.sr h3 a:hover{{text-decoration:underline}}
.sr-url{{font-size:.8rem;color:#27ae60;margin-bottom:.4rem}}
.sr p{{margin:0;color:#555;line-height:1.6}}
mark{{background:#fff176;color:inherit;padding:0 2px;border-radius:2px}}
.nores{{color:#666;font-size:1.05rem}}
.back{{color:#666;text-decoration:none;font-size:.9rem}}
.back:hover{{text-decoration:underline}}
</style>
</head>
<body>
<p><a class="back" href="/{lang_e}/">← Back to {lang_name_e} manual</a></p>
<h1>Search results</h1>
<form class="sb" method="get" action="/{lang_e}/search.html">
  <input type="search" name="q" value="{q_e}" autofocus>
  <button type="submit">Search</button>
</form>
{count_line}
{body}
</body>
</html>"""
```

---

## Constants to define at module level (outside the class)

```python
_SEARCH_SKIP_DIRS  = frozenset({"_static", "_sources", "_images", ".doctrees"})
_SEARCH_SKIP_FILES = frozenset({"search.html", "genindex.html",
                                 "py-modindex.html", "404.html"})
```

---

## Edge Cases

| Case | Handling |
|---|---|
| `?q=` absent or empty | Fall through to static `search.html` (original Sphinx search) |
| `build/<lang>/` not yet built | `_do_search` detects missing dir → returns "no results" page |
| `query` contains HTML special chars (`<>&"`) | All output goes through `_html.escape()` before insertion into HTML |
| `query` match spans a whitespace-normalised boundary | Acceptable — `get_text()` normalises whitespace; false negatives rare for long phrases |
| More than 50 results | Capped at 50; count line reads "50+ results" |
| OSError reading a file | `continue` — skip silently |
| Malformed HTML in a built page | `HTMLParser.feed()` wrapped in `try/except Exception` → skip file |

---

## Performance Notes

- ~2 300 HTML files per language in the Blender manual.
- Each file ~50–150 KB (average ~80 KB) → total ~184 MB per language.
- Local SSD read speed ~1–2 GB/s → raw IO ~ 90–180 ms.
- HTMLParser is C-backed (`html.parser` uses `_markupbase`); parsing adds ~2–3×.
- Expected wall time: **0.5–2 s** per query on a modern Mac.
- That is acceptable for a local dev server. No caching is needed for now.
- If it proves too slow, an in-memory index (built at startup with `os.walk`) can
  be added later; the `_do_search` method signature stays the same.

---

## Test Plan

1. Start the server: `make liveall` (or `make serve` after `make build`).
2. Open `http://127.0.0.1:8000/vi/search.html?q=Sử+dụng+chức+năng`.
3. Expected: results page with at least one hit linking to the keymap page.
4. Click a result link — confirm the correct page opens.
5. Search for a short English term (e.g. `render`) in `/en/search.html?q=render`.
6. Confirm 50 results are returned quickly.
7. Search for a non-existent string — confirm "No results" page renders.
8. Visit `/en/search.html` with no `?q=` — confirm original Sphinx search page loads.
9. Confirm XSS safety: search `?q=<script>alert(1)</script>` — no JS executes.
