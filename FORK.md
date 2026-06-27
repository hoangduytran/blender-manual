**Language / Ngôn ngữ:** English · [Tiếng Việt](FORK_VI.md)

# Blender Manual — Multilingual Build Fork

This repository is a **downstream fork** of the official
[Blender Manual](https://projects.blender.org/blender/blender-manual). It tracks
Blender's content faithfully but adds a build, translation, search and theme
toolchain aimed at **building and reading the manual in multiple languages at
once** (English plus any locale that has a PO catalogue, e.g. Vietnamese).

None of this changes the manual's *content*. Everything here is build tooling,
Sphinx extensions, and theme JavaScript layered on top of upstream. The `main`
branch is kept as a clean mirror of Blender; all fork features live on
`feature/new_make_for_foreign_languages`.

- **Upstream (Blender):** https://projects.blender.org/blender/blender-manual
- **This fork:** https://github.com/hoangduytran/blender-manual

> **Why a fork?** These changes were developed with AI assistance and are not
> being merged upstream. Publishing here keeps them available to anyone who
> wants multilingual local builds, while still letting you (and users) pull in
> Blender's ongoing manual updates — see [Staying in sync with Blender](#staying-in-sync-with-blender).

---

## Table of contents

- [Feature overview](#feature-overview)
  - [1. Multi-language build & serve](#1-multi-language-build--serve)
  - [2. Fast incremental translation builds (smart MO shards)](#2-fast-incremental-translation-builds-smart-mo-shards)
  - [3. PO-based multi-language search](#3-po-based-multi-language-search)
  - [4. Reading-hint pills (repeatable-record)](#4-reading-hint-pills-repeatable-record)
  - [5. Shared static/image assets](#5-shared-staticimage-assets)
  - [6. Theme / reading UX](#6-theme--reading-ux)
  - [7. Translation-key (:kbd:) fix](#7-translation-key-kbd-fix)
  - [8. Tooling & infrastructure](#8-tooling--infrastructure)
- [Make targets reference](#make-targets-reference)
- [Environment variables](#environment-variables)
- [Choosing your languages](#choosing-your-languages)
- [Quick start](#quick-start)
- [Day-to-day authoring & translation workflow](#day-to-day-authoring--translation-workflow)
- [Customizing images and styles](#customizing-images-and-styles)
- [Staying in sync with Blender](#staying-in-sync-with-blender)
- [Repository layout](#repository-layout)

---

## Feature overview

### 1. Multi-language build & serve

Build **every** configured language into its own output tree and serve them all
from one local site with a working language switcher.

- `make build` builds each code in `BF_LANGS` into `build/<lang>/`. English is
  always built first as the shared-asset seed language.
- `make serve` starts a unified server at <http://localhost:8000> that routes
  `/<lang>/…` to the matching build and injects a sidebar language switcher
  listing exactly the locally available languages.
- `make liveall` does both in one command: live rebuilders per language (with
  auto-reload in the browser) **plus** the unified server. Edit an `.rst` or a
  PO catalogue and the affected page rebuilds and refreshes automatically.
- `make stop` cleanly stops `liveall`/`serve` — the unified server, every
  per-language rebuilder, and any orphaned Sphinx worker processes.

Implementation: [tools/serve_docs.py](tools/serve_docs.py),
plus the `liveall` / `build` / `serve` / `stop` targets in the
[Makefile](Makefile).

### 2. Fast incremental translation builds (smart MO shards)

Blender translators maintain **one large** `blender_manual.po` per language.
Recompiling and re-rendering the whole catalogue on every edit is slow. This
fork compiles the monolithic PO into **one generated `.mo` per document** and
only rebuilds the documents whose translations actually changed.

- [tools/translations/smart_mo_compile.py](tools/translations/smart_mo_compile.py) —
  compiles `locale/<lang>/LC_MESSAGES/blender_manual.po` into per-document shards
  under `build/.i18n_shards/locale/<lang>/LC_MESSAGES/`, with a translation
  cache so unchanged documents are skipped.
- [build_files/extensions/i18n_shards.py](build_files/extensions/i18n_shards.py) —
  a Sphinx extension that marks a document *outdated* when its generated shard is
  newer than the last time Sphinx read it, so incremental builds pick up
  translation edits reliably across Sphinx versions.

The PO stays the single human-editable source of truth; the shards are a build
artefact.

### 3. PO-based multi-language search

A search overlay that works **per language**, driven directly by the PO
catalogues rather than Sphinx's default English-only index.

- Press <kbd>/</kbd> on any page to open the overlay. Results stream in over
  Server-Sent Events and deep-link to the matching **section anchor**, not just
  the page.
- Each translated language gets `build/<lang>/searchindex.pkl.gz`, built by
  [tools/search/index_builder.py](tools/search/index_builder.py) from its PO file
  (`make search-index`, also run automatically by `make build` / `make liveall`).
- English has no PO file, so
  [build_files/extensions/search_index_builder.py](build_files/extensions/search_index_builder.py)
  builds the English index straight from the doctree — the source-language
  analogue of `blender_manual.pot`.
- Search internals: [tools/search/](tools/search/) (`index_builder.py`,
  `index_loader.py`, `index_searcher.py`, `po_parser.py`, `po_watcher.py`,
  `section_map.py`, `searchable_record.py`).

### 4. Reading-hint pills (repeatable-record)

For language learners reading the translated manual, this adds small inline
**hint pills** that show the original English term next to its translation (and
glossary/near-miss information), rendered server-side.

- [build_files/extensions/repeatable_record.py](build_files/extensions/repeatable_record.py)
  and the companion `repeatable_*` extensions capture allowlisted translatable
  nodes (titles, terms, references, emphasis) into a small picklable inventory.
- Recognises glossary terms (`.i18n-vi-hint`), parenthesis-delimited hints
  (e.g. Russian `Аддоны (add-ons)`), and reports near-misses, with
  case-insensitive English matching.
- Extensions: [build_files/extensions/](build_files/extensions/)
  (`repeatable_record.py`, `repeatable_extract.py`, `repeatable_html.py`,
  `repeatable_builder.py`).

### 5. Shared static/image assets

Each translated build would otherwise copy `_static` (~10 MB) and `_images`
(~250 MB) into `build/<lang>/`. Since the screenshots are identical across
languages, that wastes disk and build time.

- [build_files/extensions/shared_assets.py](build_files/extensions/shared_assets.py)
  centralises shared assets under `build/shared/` and links each language to
  them, while still allowing **per-language overrides** (a localized screenshot
  in `locale/<lang>/…` wins over the shared English one).
- `liveall` watches the per-language override directories so swapping in a
  localized asset triggers a rebuild.

### 6. Theme / reading UX

Client-side enhancements injected into every page:

- **Zoomable image viewer** —
  [build_files/theme/js/image_viewer.js](build_files/theme/js/image_viewer.js):
  click a manual figure to open a zoomable viewer; shows the source resolution
  path.
- **Draggable sidebar splitters** —
  [build_files/theme/js/sidebar_splitter.js](build_files/theme/js/sidebar_splitter.js):
  resize the 3D-style sidebars by dragging.

### 7. Translation-key (`:kbd:`) fix

Sphinx splits `:kbd:` text on spaces, `-`, `+`, `^`, which mangles translated
key names like Vietnamese `Dấu Cộng (+) Bàn Số (NumpadPlus)` into one `<kbd>`
per word. [build_files/extensions/kbd_fix.py](build_files/extensions/kbd_fix.py)
re-joins these runs and only splits on *top-level* separators (never inside
parentheses, never on spaces).

### 8. Tooling & infrastructure

- Lightweight logging that replaced the older bounded `application.log` infra.
- Shared helpers in [tools/common/](tools/common/) (`constants.py`, `utils.py`).
- Enhancements to translation tooling: `po_shortcuts.py`, `update_po.py`,
  `file_translation_progress.py`, `rst_find_reference.py`.
- A cross-platform acceptance test suite under [tests/](tests/) (search,
  repeatable-record, shared assets, PO shortcuts, multiprocessing logging) plus
  design/plan docs.

---

## Make targets reference

Run `make help` for the authoritative list. Highlights added or changed by this
fork:

| Target | What it does |
| --- | --- |
| `make build` | Build every `BF_LANGS` language into `build/<lang>/`, then build search indexes. |
| `make remake` | `make clean` + `make build`. |
| `make liveall` | Live-rebuild all `BF_LANGS` **and** serve them at <http://localhost:8000> (single command). |
| `make serve` | Serve the existing `build/` directory with language switching. |
| `make stop` | Stop a running `liveall`/`serve` (server + per-language rebuilders + Sphinx workers). |
| `make search-index` | (Re)build `build/<lang>/searchindex.pkl.gz` for each language with a PO file. |
| `make livehtml-direct` | Auto-build a single language into `build/<lang>/` (pair with `make serve`). |
| `make html` | Stock single-language HTML build (upstream behaviour). |
| `make checkout_locale <codes>` | Fetch translation catalogues (e.g. `make checkout_locale vi fr`) from Blender's translations repo into `locale/`. |
| `make update_po` | Update PO message catalogs. |
| `make report_po_progress` | Report translation progress / fuzzy strings. |
| `make local` | Modifier: disable intersphinx for this invocation (e.g. `make remake local`). |

## Environment variables

| Variable | Meaning |
| --- | --- |
| `BF_LANG` | Language code for the current build (default `en`). Passed to Sphinx as `-D language=<code>`. |
| `BF_LANGS` | Space-separated languages built by `make build` (default: auto-detected from `locale/`). English is always prepended as the shared-asset seed, so `BF_LANGS="vi ru"` becomes `en vi ru`. |
| `NO_INTERSPHINX` | When non-empty, Sphinx targets skip intersphinx (no online access needed). |

Example — build English + Vietnamese and live-serve them:

```bash
make liveall BF_LANGS="en vi"
```

---

## Choosing your languages

**This repository ships no translation data.** The `locale/` directory is not
committed, so you are free to pull in whichever languages you want. Translations
come from Blender's own
[blender-manual-translations](https://projects.blender.org/blender/blender-manual-translations)
project, fetched with:

```bash
make checkout_locale vi          # one language
make checkout_locale vi fr ru    # several at once
make checkout_locale             # interactive: prompts for codes
```

This sparse-checks-out `locale/<lang>/LC_MESSAGES/blender_manual.po` for each
code. English needs no catalogue (it is the source language). After checking out
a language it becomes available to every build/serve target; pass the codes you
want via `BF_LANGS` (or rely on auto-detection from `locale/`).

## Quick start

```bash
# 1. Clone the fork
git clone git@github.com:hoangduytran/blender-manual.git
cd blender-manual

# 2. One-time environment setup (creates the Sphinx virtualenv)
make setup

# 3. Fetch the language(s) you want (skip for English-only)
make checkout_locale vi

# 4. Build + live-serve English plus your chosen languages
make liveall BF_LANGS="en vi"
# → open http://localhost:8000  (press '/' to search, language switcher in sidebar)

# Stop everything
make stop
```

English-only needs no `checkout_locale` step:

```bash
make liveall                 # just English
```

Building a static site without the live server:

```bash
make checkout_locale vi
make build BF_LANGS="en vi"
make serve BF_LANGS="en vi"
```

---

## Day-to-day authoring & translation workflow

The `liveall` server is the hub for both jobs: it watches your English `.rst`
sources **and** every language's PO catalogue, rebuilds only what changed, and
refreshes the browser automatically. Start it once and leave it running:

```bash
make liveall BF_LANGS="en vi"     # English + Vietnamese, live, at :8000
make stop                          # when you're done
```

What it watches (per language): `manual/**.rst`, `locale/<lang>/LC_MESSAGES`
(the PO files), the per-language override folders, and `build_files/` (theme +
extensions).

### Writing / editing English content (RST)

1. With `liveall` running, edit any page under `manual/**/*.rst`.
2. On save, every built language rebuilds; the **English** page refreshes
   immediately. Translated languages show the English text as a *fallback* for
   any new or changed string until it is translated.
3. When you have added or changed English strings, refresh the translators'
   catalogues so the new message IDs reach them:

   ```bash
   make update_po
   ```

   This updates `locale/<lang>/LC_MESSAGES/blender_manual.po` for every language
   with the new/changed `msgid`s (left untranslated or fuzzy for translators to
   fill in). Run it whenever the English source text changes, not on every edit.

### Translating into a foreign language (PO)

1. Keep `liveall` running. Open `locale/<lang>/LC_MESSAGES/blender_manual.po`
   and fill in `msgstr` entries (directly, or via the project's PO helpers in
   [tools/translations/](tools/translations/)).
2. On save:
   - `smart_mo_compile.py` recompiles **only** the document shards whose
     translations changed,
   - that language rebuilds and the browser refreshes,
   - the server's `MultiPOWatcher` rebuilds that language's **search index**,
     so search reflects your new translations live too.
3. Check coverage at any time:

   ```bash
   make report_po_progress           # translated / fuzzy / untranslated counts
   ```

### Lighter single-language alternatives

When you only care about one language, these are cheaper than `liveall`:

```bash
make livehtml BF_LANG=vi            # one language, live, served at :8000
# — or, build into build/<lang>/ and serve separately (two terminals):
make livehtml-direct BF_LANG=vi     # terminal 1: rebuilder
make serve BF_LANGS="en vi"         # terminal 2: unified server w/ switcher
```

> Reminder: `BF_LANGS` always builds English first (the shared-asset seed), so
> `BF_LANGS="vi"` is treated as `"en vi"`.

## Customizing images and styles

There are three distinct ways to add your own assets, depending on whether you
want to **replace a screenshot for one language**, **restyle the whole theme**,
or **add new content images**.

### A. Per-language image / static overrides (no code changes)

Thanks to the [shared-assets](#5-shared-staticimage-assets) extension, any
language can override or add an asset by dropping a file under
`locale/<lang>/_images/` or `locale/<lang>/_static/`, **mirroring the same
relative path** the manual uses. The override wins over the shared English copy;
everything else keeps linking to the shared tree.

```text
# Replace one English screenshot with a Vietnamese one:
locale/vi/_images/render/cycles/gpu_rendering.png   # same path as the EN image

# Add a Vietnamese-only static file (e.g. a localized CSS tweak or font):
locale/vi/_static/css/vi_overrides.css
```

- English can override its own shared assets the same way, via
  `locale/en/_images/…` and `locale/en/_static/…`.
- `make liveall` watches these override folders (`OVERRIDE_SUBDIRS = _images
  _static`), so dropping or swapping a file triggers a rebuild and browser
  refresh automatically.
- No edits to `conf.py` or the Makefile are needed — overrides are resolved by
  path at build time.

### B. Theme-wide CSS / JavaScript (all languages)

The theme's static assets live in **`build_files/theme/`** (registered as
Sphinx's `html_static_path`). To add a site-wide stylesheet or script:

1. Drop the file in the theme tree, e.g.
   `build_files/theme/css/my_overrides.css` or
   `build_files/theme/js/my_widget.js`.
2. Register it in [manual/conf.py](manual/conf.py) under the `furo` block:

   ```python
   html_css_files = [
       "css/theme_overrides.css",
       "css/version_switch.css",
       "fonts/bl-icons.css",
       "css/my_overrides.css",   # ← your stylesheet
   ]
   html_js_files = [
       "js/version_switch.js",
       "js/sidebar_splitter.js",
       "js/image_viewer.js",
       "js/my_widget.js",        # ← your script
   ]
   ```

This is exactly how the fork's own [image_viewer.js](build_files/theme/js/image_viewer.js)
and [sidebar_splitter.js](build_files/theme/js/sidebar_splitter.js) are wired
in, so follow those as working examples. Restyling existing elements is best
done in `css/theme_overrides.css` (loaded after the Furo defaults, so your rules
win).

### C. New content images (referenced from `.rst`)

For images that appear *in the manual text* (figures, screenshots you add to a
page), follow upstream Blender's convention: put the file under `manual/images/`
and reference it from the `.rst` with the normal `figure`/`image` directive.
These are shared across all languages automatically; localize one only if needed
via method **A** above.

> Tip: keep fork-specific theme assets in `build_files/theme/` and content
> images in `manual/images/`. That separation means upstream content syncs
> (which touch `manual/`) rarely collide with your theme customizations.

## Staying in sync with Blender

The whole point of the fork model: **keep Blender's content current while
keeping these tooling changes.** `main` mirrors Blender (plus the one
`nmake_locale.sh` bootstrap script); the fork
work lives on `feature/new_make_for_foreign_languages`, and you bring upstream
changes *into* that branch by **merging** (never rebasing — merging means
people who cloned the branch can `git pull` safely, no force-push).

### One-time remote setup

Already configured in the maintainer's checkout. If you cloned fresh:

```bash
git remote add upstream https://projects.blender.org/blender/blender-manual.git
git remote set-url --push upstream DISABLE   # safety: never push to Blender
```

### Routine update (run whenever Blender's manual changes)

```bash
git fetch upstream

# Update main with Blender's changes (main also carries nmake_locale.sh,
# so use a normal merge, not --ff-only — it stays clean since Blender
# never touches the bootstrap script)
git checkout main
git merge upstream/main
git push origin main

# Bring Blender's updates into the fork, keeping our tooling
git checkout feature/new_make_for_foreign_languages
git merge upstream/main          # resolve any conflicts, then:
git push origin feature/new_make_for_foreign_languages
```

Conflicts, if any, are almost always in **content** `.rst` files (take
upstream's version) rather than in the fork's `tools/`, `build_files/`, or
`Makefile` additions, which upstream never touches.

### Automated weekly sync

[.github/workflows/sync-upstream.yml](.github/workflows/sync-upstream.yml) runs
every Monday (and on demand via the Actions tab). It updates `main` (merging
Blender's changes), attempts to merge `upstream/main` into the fork branch, and
then either:

- **opens a pull request** with the merged updates (clean merge), or
- **opens an issue** listing the conflicting files (merge needs hands-on
  resolution).

Nothing is force-pushed and the fork branch is never modified directly by the
bot — you review and merge the PR.

---

## Repository layout

```
build_files/extensions/   Sphinx extensions added by the fork
  i18n_shards.py            outdated-detection for per-document MO shards
  kbd_fix.py                :kbd: re-splitting for translated key names
  search_index_builder.py   English source-language search index
  shared_assets.py          shared _static/_images across languages
  repeatable_*.py           reading-hint pill capture/render
build_files/theme/js/      theme JavaScript (image_viewer, sidebar_splitter)
tools/serve_docs.py        unified multi-language dev server
tools/translations/        smart_mo_compile.py + PO tooling
tools/search/              PO-based search index + searcher
tools/common/              shared constants/utils
tests/                     acceptance tests + design/plan docs
Makefile                   multi-language build/serve/stop targets
```

For upstream contribution guidelines, style guides, and the translation
project, see [README.md](README.md) (unchanged from Blender).
