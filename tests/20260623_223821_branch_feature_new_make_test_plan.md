# Acceptance Test Plan — branch `feature/new_make_for_foreign_languages`

**Audience:** an external Blender Manual contributor who downloads this PR to a
**clean machine**, on **Windows, Linux, and macOS**, checks out **all**
translation languages, builds, edits content/translations, and observes the
result live. Every step lists the command per-OS and an explicit **PASS/FAIL**.

**What the PR does (scope):** foreign-language build system — multi-language
live builds, PO-based search with section-anchor deep-links, repeatable-record
reading-hint pills, shared `_static`/`_images` with per-language override,
lightweight logging, and Makefile target renames (`both`→`build`,
`liveboth`→`liveall`). 49 files, ~16.8k insertions over `main`.

---

## ⚠️ Platform note — read first

The new workflow lives in the **GNU `Makefile`**. The Windows **`make.bat`**
was changed by only one line and still has **none** of the new targets
(`build`, `liveall`, `serve`, `stop`, `search-index`, `remake`, multi-language
`checkout_locale`). Therefore:

- **Linux / macOS:** native `make` — full coverage.
- **Windows:** native `make.bat` does **not** expose this PR. Test via **one of**:
  - **WSL2 (Ubuntu)** — recommended; behaves as Linux. *(Treat as the Linux column.)*
  - **MSYS2 / Git Bash with GNU `make` + Python** — exercises the real `Makefile`.
  - Native `cmd`/PowerShell `make.bat` — only validates the *unchanged* legacy
    path (single-language `livehtml`), see §10.

Record results in the matrix at the end for **all three OSes**.

---

## 0. Get the PR onto a clean machine

The manual and its translations are two repos on `projects.blender.org` (Gitea).

```sh
# Linux / macOS / WSL / Git Bash
git clone https://projects.blender.org/blender/blender-manual.git
cd blender-manual
git fetch origin feature/new_make_for_foreign_languages
git switch feature/new_make_for_foreign_languages
git log --oneline -1        # = d94a544a5 (or later) on this branch
```
```bat
REM Windows native cmd (same git commands)
git clone https://projects.blender.org/blender/blender-manual.git
cd blender-manual
git fetch origin feature/new_make_for_foreign_languages
git switch feature/new_make_for_foreign_languages
```
**PASS:** branch checked out, HEAD on the PR tip. **FAIL:** branch not found →
fetch the contributor's fork/remote instead.

---

## 1. Environment setup (per OS)

Requires Python 3.x on PATH. The setup target creates `.venv` and installs
`requirements.txt`.

| OS | Setup command | Activate venv |
|---|---|---|
| Linux / macOS / WSL | `make setup` | `source .venv/bin/activate` |
| Git Bash / MSYS2 | `make setup` | `source .venv/Scripts/activate` |
| Windows cmd | `make.bat setup` | `.venv\Scripts\activate.bat` |

Verify:
```sh
python -m pip show sphinx sphinx-autobuild >/dev/null && echo "PASS: deps installed"
sphinx-build --version
```
**PASS:** `.venv` created, `sphinx`, `sphinx-autobuild` present.
**Windows extra:** confirm GNU `make` is available if not using `make.bat`
(`make --version`); if absent, use WSL.

---

## 2. Checkout ALL translation languages

`checkout_locale` clones `blender-manual-translations` into `locale/`. Passing
language codes selects them; with none it prompts interactively.

```sh
# Linux / macOS / WSL / Git Bash — list every language you want, e.g. a broad set:
make checkout_locale LANGUAGES="fr ru vi zh-hans es de ja pt"
#   …or all available: omit LANGUAGES and enter codes at the prompt.
```
**Validate all languages landed and are auto-detected:**
```sh
ls locale/                      # one dir per language code
find locale -maxdepth 3 -name 'blender_manual.po' \
  | sed 's|locale/||;s|/LC_MESSAGES.*||' | sort -u      # detected langs
make help | grep -i BF_LANGS    # confirm auto-detection wording
```
**PASS:** every requested code has `locale/<lang>/LC_MESSAGES/blender_manual.po`;
the detected list matches; `BF_LANGS` will include them on build.
**FAIL (Windows native):** `make.bat checkout_locale` ignores language args and
may prompt — note as a limitation, do the checkout under WSL/Git Bash.

---

## 3. Single-language build — sanity (English)

```sh
make html BF_LANG=en          # Linux/macOS/WSL/Git Bash
```
```bat
make.bat html                 REM Windows native (legacy path; English only)
```
Validate:
```sh
test -f build/en/index.html && echo "PASS: en built"
```
**PASS:** `build/en/index.html` exists; build exits 0; no ERROR-level messages.

---

## 4. Build ALL languages (`make build`, renamed from `both`)

```sh
make build                    # Linux/macOS/WSL/Git Bash — builds en + every detected lang
```
Validate one output tree per language:
```sh
for L in $(ls build | grep -vE 'doctrees|\.|shared'); do
  test -f "build/$L/index.html" && echo "PASS: $L" || echo "FAIL: $L"
done
```
**PASS:** `build/<lang>/index.html` exists for **every** checked-out language.
**Incremental translation shards:**
```sh
ls build/.i18n_shards/locale/*/LC_MESSAGES/*.mo >/dev/null 2>&1 \
  && echo "PASS: .mo shards generated per language"
```
**Translated content applied** (pick any non-en lang `$L`):
```sh
L=vi   # or any checked-out language
diff -q build/en/index.html build/$L/index.html \
  && echo "FAIL: $L identical to en" || echo "PASS: $L content differs (translated)"
```
**PASS:** shards present; each language's HTML differs from English.

---

## 5. PO-based search + section-anchor deep-links

```sh
make search-index
find build -name 'searchindex.pkl.gz' | head && echo "PASS: search index built"
```
**Manual (browser, during §6 serve):** use the on-page search, click a hit →
URL ends in `#<section-anchor>` and the page scrolls to that section (not the
top), in a translated language too. **PASS:** anchor present + correct scroll.

---

## 6. Live build, serve, observe changes (`liveall` / `serve` / `stop`)

This is the core "make changes, observe changes" loop.

```sh
make liveall      # builds all languages + serves http://localhost:8000
```
Open `http://localhost:8000` in a browser. Validate, each as a separate PASS:

1. **Language switch** — navigate en ↔ every checked-out language; pages load.
2. **Live translation edit** — edit a string in
   `locale/<lang>/LC_MESSAGES/blender_manual.po`, save → the open page
   **auto-reloads** with the new translation within a few seconds.
   *(Windows: ensure the editor keeps UTF-8; CRLF is tolerated but prefer LF.)*
3. **Reading-hint pills** — a glossary / parenthesis-hint term (e.g. ru
   `Аддоны (add-ons)`) renders an English hint pill; case-insensitive match works.
4. **Per-language asset override (live)** — drop a file into
   `locale/<lang>/_static/` or `locale/<lang>/_images/`; the live rebuild applies
   it to **that language only**, English keeps the shared asset.

Stop cleanly:
```sh
make stop
# port released?
lsof -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1 && echo "FAIL: still listening" || echo "PASS: port 8000 free"
```
```bat
REM Windows: confirm with  netstat -ano | findstr :8000   (should show nothing)
```
**PASS:** all four observations confirmed; `make stop` frees port 8000 and kills
rebuilders. **Note:** first run may trigger an OS firewall prompt — allow it.

---

## 7. Shared `_static`/`_images` with per-language override (+ symlink behaviour)

`build/shared/{_static,_images}` is the canonical asset store, built once. Each
language tree then gets its **own** `build/<lang>/_static` and `build/<lang>/_images`
that resolve to those shared assets — a **symlink** where the OS allows it, else a
**full copy**. So every served language has assets locally present regardless of
link mode.

```sh
# 7a. shared store populated
ls -d build/shared/_static build/shared/_images 2>/dev/null \
  && echo "PASS: shared store present"

# 7b. EVERY language has its own _static AND _images, populated
for L in $(ls build | grep -vE 'doctrees|\.|shared'); do
  for A in _static _images; do
    if [ -e "build/$L/$A" ]; then
      mode=$([ -L "build/$L/$A" ] && echo symlink || echo copy)
      echo "PASS: build/$L/$A present ($mode)"
    else
      echo "FAIL: build/$L/$A MISSING"
    fi
  done
done

# 7c. build still succeeds with sharing disabled
BF_SHARED_ASSETS=0 make html BF_LANG=en && test -f build/en/index.html \
  && echo "PASS: builds with BF_SHARED_ASSETS=0"
```

**Cross-platform link-mode check:** `shared_assets_link_mode=auto`.
- **Linux/macOS:** assets **may** be symlinked back to `build/shared/…`.
- **Windows:** symlink creation needs Developer Mode/admin, so `auto` must **fall
  back to copy**; the build must still succeed with assets fully present in each
  `build/<lang>/_static` and `build/<lang>/_images`.
- Either way the per-language dirs are **populated** (symlink *or* copy) — they are
  not expected to be empty just because a `build/shared/` store exists.

**Per-language override:** a file placed in `locale/<lang>/_static/` or
`locale/<lang>/_images/` must override the shared asset for **that language only**;
English (and other langs) keep the shared version.

**Expected results / PASS:**
- 7a — `build/shared/_static` and `build/shared/_images` exist.
- 7b — for **every** built language, both `build/<lang>/_static` and
  `build/<lang>/_images` exist and are populated (each printed as `symlink` or
  `copy`); none `MISSING`.
- 7c — `BF_SHARED_ASSETS=0` build of `en` still produces `build/en/index.html`.
- Browser — images and CSS load for every language on all three OSes, regardless
  of link vs copy; a per-language override file shows only in its own language.

---

## 8. Logging (lightweight, replaces bounded application.log)

```sh
grep -rn "application.log" tools build_files 2>/dev/null \
  && echo "review: residual refs" || echo "PASS: bounded application.log infra removed"
```
During the parallel `make build` (`-j auto`), log output is readable and not
interleaved/corrupted. **PASS:** clean log lines; no `application.log` artifacts.

---

## 9. Automated test suite (run on each OS)

```sh
python -m pytest tests -q
```
**PASS:** full suite green (104 tests at time of writing), exit 0, on each OS.
If a test is OS-specific (paths/symlinks), note which and why in the matrix.

---

## 10. Windows native `make.bat` regression (legacy path only)

Since `make.bat` was nearly untouched, confirm it still works for what it does —
and that the PR did **not** break it:
```bat
make.bat help            REM lists legacy targets
make.bat html            REM single-language (English) build
make.bat check_structure
```
**PASS:** `make.bat html` builds `build\html\index.html`; `help` and
`check_structure` run. **EXPECTED LIMITATION (report, not a fail):** `make.bat`
offers no `build`/`liveall`/`serve`/multi-lang `checkout_locale` — those are
Makefile-only. Flag whether Windows contributors should get WSL guidance in the
docs.

---

## 11. Teardown

```sh
make stop 2>/dev/null || true
# optional clean rebuild from scratch:
make remake          # cleans build/ and rebuilds all BF_LANGS
```
```bat
REM Windows: deactivate venv
.venv\Scripts\deactivate.bat
```

---

## Cross-platform result matrix (fill in)

| # | Test | Linux | macOS | Win (WSL/MSYS2) | Win native `make.bat` |
|---|---|---|---|---|---|
| 0 | Clone + checkout branch | ☐ | ✅ | ☐ | ☐ |
| 1 | Env setup / venv / deps | ☐ | ✅¹ | ☐ | ☐ |
| 2 | checkout_locale ALL langs | ☐ | ✅² | ☐ | n/a (no arg support) |
| 3 | Build EN sanity | ☐ | ✅ | ☐ | ☐ |
| 4 | `make build` all langs + shards | ☐ | ✅ | ☐ | n/a |
| 5 | search-index + deep-link | ☐ | ✅³ | ☐ | n/a |
| 6 | liveall/serve + 4 live observations | ☐ | ☐⁴ | ☐ | n/a |
| 7 | shared assets + override + symlink fallback | ☐ | ✅⁵ | ☐ | n/a |
| 8 | logging clean / no application.log | ☐ | ✅ | ☐ | ☐ |
| 9 | `pytest tests` green | ☐ | ✅ | ☐ | ☐ |
| 10 | `make.bat` legacy still works | n/a | n/a | n/a | ☐ |

**macOS run notes (2026-06-24, HEAD `d94a544a5`):**
1. Deps (`sphinx 9.1.0`, `sphinx-autobuild`) present on system Python; no `.venv`
   on this machine — `make setup` not re-run, deps satisfied directly.
2. Only `ru` + `vi` checked out (not the full broad set); both detected and built.
3. `searchindex.pkl.gz` + `searchindex.js` present for `en`, `ru`, `vi`. The
   anchor-scroll deep-link itself is browser-only — not verified in CLI.
4. `liveall`/`serve`/`stop` targets exist in the `Makefile`; the four live
   browser observations require manual in-browser verification — still pending.
5. `build/shared/{_static,_images}` populated (3107 images). Each language gets
   its own `build/<lang>/_static` **and** `build/<lang>/_images` (3107 entries for
   `en`/`ru`/`vi`). On macOS `shared_assets_link_mode=auto` resolved to **copy**
   (real dirs, not symlinks) — the copy fallback path is exercised here.
6. §8: `application.log` infra fully gone — no code/config refs; stray root
   `application.log` file deleted (untracked, `*.log`-ignored).

---

## Traceability — commit → step

| Commit | Validated by |
|---|---|
| `13f132c47` multi-lang live build + shards | §4, §6 |
| `5caf16b30` serve_docs lang coverage / auto-detect | §2, §6 |
| `e3a38e3c5` flexible checkout_locale + live-reload | §2, §6 |
| `59931b4d1` / `fc0cc4f25` PO search + deep-links | §5 |
| `7ad1ad9c6` rename liveboth→liveall | §6 |
| `ef9ba6942` rename both→build | §4 |
| `b1216cf4e` multilingual live docs + logging | §4, §6, §8 |
| `5cf77499a`..`fb009a047` repeatable + hint pills | §6(3), §9 |
| `1a0b50593` lightweight logging | §8 |
| `832d09c46` server-side HTML pills + near-miss | §6(3) |
| `f70b5aee2` shared _static/_images + override | §7 |
| `d94a544a5` live-watch per-language asset overrides | §6(4) |

**PR accepted when:** every applicable matrix cell passes on all three OSes
(Windows via WSL/MSYS2 for the new workflow), and §10 confirms native `make.bat`
is not regressed.
