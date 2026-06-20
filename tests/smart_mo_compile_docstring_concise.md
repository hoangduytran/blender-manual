# Turn one large translation file into small files for each page

## What this script does

Translators write Vietnamese text in one large `.po` file:

```text
locale/vi/LC_MESSAGES/blender_manual.po
```

A `.po` file is easy for people to edit. Sphinx needs compiled `.mo` files to
build the translated website.

This script splits the large PO into many small MO files. Each manual page gets
its own file:

```text
build/.i18n_shards/locale/vi/LC_MESSAGES/<page-name>.mo
```

We call each small MO file a **shard**. If one page's translation changes, only
that page's shard needs to change.

English does not need translation, so `--language=en` does nothing.

## What was wrong with the old build

These facts were checked against the old repository and its installed versions
of Sphinx 9.1.0 and sphinx-autobuild 2025.8.25.

### 1. Saving a PO file did not start a live rebuild

The old command watched only the `manual/` folder. The PO file is inside the
`locale/` folder, which was not watched.

### 2. Every page used the same MO file

The old setting was:

```python
gettext_compact = "blender_manual"
```

Sphinx therefore recorded `blender_manual.mo` as a dependency of every manual
page. When that one MO file became newer, Sphinx treated every page as changed.

### 3. Sphinx checked time, not translation content

Sphinx decided to compile when the PO file was newer than the MO file. It did
not check whether any translated sentence had actually changed.

### 4. Sphinx processed the whole catalog

Its `CatalogInfo.write_mo()` function read the complete PO and wrote one
complete `blender_manual.mo`. It had no smaller page files to update by
themselves.

### 5. The old writer wrote directly to the final file

It opened the final MO path with `open(..., "wb")`. That function did not use a
temporary file, an atomic rename, or a lock for one language.

## How the new build works

### Step 1: Watch the translation file

The current live-build commands watch:

```text
locale/<language>/LC_MESSAGES
```

They run this script before Sphinx builds the website. Generated files are
ignored by the watcher.

### Step 2: Find which page uses each translation

Entries in the PO contain `#:` location comments. These comments point to RST
source files. The script uses them to connect each translation to one or more
manual pages.

### Step 3: Build one MO shard per page

The runtime Sphinx setting is:

```python
gettext_compact = False
gettext_auto_build = False
```

The first setting gives each page its own translation domain. The second stops
Sphinx from creating a competing global MO file.

Pages without translations receive a small header-only shard. Translations
whose page cannot be found go into `__orphan__.mo`.

### Step 4: Do not rewrite identical files

The script creates a shard in memory and compares its bytes with the existing
file. If the bytes are equal, it leaves the file alone. Its modification time
therefore stays unchanged.

The `i18n_shards` Sphinx extension checks each page's shard time. It returns
only pages whose shard is newer than the last time Sphinx read that page.

### Step 5: Use a cache to skip unnecessary work

A **cache** stores information from the previous successful run. The script
checks it in this order:

| Tier | What is checked | What happens on a match |
|---|---|---|
| 1 | PO modification time and size | Exit without reading the PO content |
| 2 | SHA-256 of all PO bytes | Update cached time information |
| 3 | Translation hash and page-location hash | Exit without writing shards |
| 4 | A real difference or `--force-rebuild` | Update the required shards |

If the cache contains valid page indexes, the script updates only the shards
connected to changed translations. If the cache is missing or invalid, it
safely rebuilds the full shard set.

### Step 6: Prevent two runs from writing together

Each language has a lock file. A second run waits while the first run holds the
lock.

Changed shards, snapshots, and cache data are first written to temporary files.
`os.replace()` then moves them to their final paths. The cache is written after
the shards and snapshot.

## How files are organized for many languages

Languages are kept separate by their **language code**. They are not placed in
continent folders such as `europe/`, `asia/`, or `middle-east/`.

For example, these are normal language codes:

- European examples: `de` (German), `fr` (French), `es` (Spanish).
- Asian examples: `ja` (Japanese), `ko` (Korean), `vi` (Vietnamese).
- Codes with a writing-system variant: `zh-hans` and `zh-hant`.
- Possible Middle Eastern examples: `ar` (Arabic), `he` (Hebrew), `fa`
  (Persian), but only when those catalog directories have been installed.

The examples above explain the folder design. They do not claim that every
catalog is present in this checkout. A translated language needs this input:

```text
locale/<language-code>/LC_MESSAGES/blender_manual.po
```

`--cache-dir` and `--shard-root` point to shared parent folders. The script
adds the current language code when it creates the real paths:

```text
--cache-dir=build/.translation_cache
    + language=vi  -> build/.translation_cache/vi.pkl

--shard-root=build/.i18n_shards/locale
    + language=vi  -> build/.i18n_shards/locale/vi/LC_MESSAGES/
```

The Makefile gives each language its own `--doctree-dir` and HTML output folder.

When a language is built, the same code is used in every generated area:

```text
locale/fr/LC_MESSAGES/blender_manual.po              source translation
build/.translation_cache/fr.pkl                      cache
build/.translation_cache/fr.po.snapshot              previous PO snapshot
build/.translation_cache/fr.lock                     per-language lock
build/.i18n_shards/locale/fr/LC_MESSAGES/<page>.mo   page shards
build/.doctrees/fr/                                   Sphinx reading state
build/fr/                                             generated French website
```

A larger setup stays flat and predictable:

```text
build/
├── .translation_cache/
│   ├── de.pkl, de.po.snapshot, de.lock
│   ├── ja.pkl, ja.po.snapshot, ja.lock
│   ├── vi.pkl, vi.po.snapshot, vi.lock
│   └── ar.pkl, ar.po.snapshot, ar.lock      # only if Arabic is installed
├── .i18n_shards/locale/
│   ├── de/LC_MESSAGES/<page>.mo
│   ├── ja/LC_MESSAGES/<page>.mo
│   ├── vi/LC_MESSAGES/<page>.mo
│   └── ar/LC_MESSAGES/<page>.mo            # only if Arabic is installed
├── .doctrees/
│   ├── de/
│   ├── ja/
│   ├── vi/
│   └── ar/
├── en/                                     English website; no translation cache
├── de/
├── ja/
├── vi/
└── ar/
```

The Makefile receives a space-separated list such as:

```bash
make both BF_LANGS="en de fr ja ko vi zh-hans zh-hant"
```

It runs one build for each code. `make liveboth` also starts one autobuild
worker per code. Each translated language gets its own `ConfigRecord`, lock,
cache files, shard directory, doctree directory, and HTML output directory.

Because locks and generated paths include the language code, work for `de`
does not write into the cache or shard paths used by `ja` or `vi`. Adding a
language adds another independent set of these files; it does not make one
shared cache file larger.

## Files created by the script

```text
<cache-dir>/vi.pkl          saved hashes and page indexes
<cache-dir>/vi.po.snapshot  copy used to find translation changes
<cache-dir>/vi.lock         stops two Vietnamese runs writing together
<shard-root>/vi/LC_MESSAGES/<page-name>.mo
```

## Main code path

```text
main
  -> _parse_args                  read settings into ConfigRecord
  -> _main_shard                  check PO and lock the language
  -> _shard_locked_body           check the cache
  -> _shard_tier4_run             choose a small or full rebuild
     -> _shard_tier4_partial_run  update affected pages only
     -> _catalog_to_shards        rebuild all page shards when needed
     -> _emit_shards              write files whose bytes changed
```
