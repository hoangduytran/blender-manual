# Plan: Pull Request for `feature/new_make_for_foreign_languages`

## How the Blender Manual Project Handles PRs

Source: [Blender Developer Handbook — Pull Requests](https://developer.blender.org/docs/handbook/contributing/pull_requests/)
and [Commit Messages](https://developer.blender.org/docs/handbook/guidelines/commit_messages/)

### Key Rules from the Official Handbook

1. **PR title = commit message subject.**
   The PR text must be usable as the git commit message. Whatever you put in the
   description body becomes the commit body when the PR is squash-merged.

2. **`---` separator.**
   Put a horizontal rule (`---`) in the PR description to separate the commit
   message part (above) from extra reviewer notes that should *not* go into the
   git log (below). Use the section below `---` for testing instructions,
   screenshots, questions for the reviewer, etc.

3. **`WIP:` prefix.**
   If the design still needs agreement, prefix the title with `WIP: ` to signal
   the PR is not ready to merge. No review is expected unless you specifically
   ask. Remove `WIP:` when the PR is ready.

4. **Do not submit huge changes at once.**
   Break work into multiple smaller PRs where the changes are separable. The
   Handbook explicitly says: *"Make it easy for people to review the code by not
   submitting huge changes, but breaking up your work into multiple smaller pull
   requests and reviews."*

5. **Commit message prefix (`Module: Short description`).**
   The Blender codebase uses module prefixes:
   - `Cycles: Add …`, `Sculpt: Fix …`, `UI: …`
   - For tooling/build: `Makefile:`, `Tools:`, `Build:`
   - The Blender *manual* uses simpler formats (see git log); examples seen in
     `main`: `VR: Add Location Scouting…`, `Fix grammar and typos…`,
     `Update manual/render/…`

6. **Merge strategy.**
   Gitea supports three strategies; for this project Squash is standard for
   contributor PRs. The PR title + description become the single squashed commit.

7. **Reviewer response time.**
   Developers are expected to reply within **3 working days**. For the manual
   project, `@Blendify` (Campbell Barton, the Documentation Administrator) is
   the single reviewer auto-assigned by `.gitea/CODEOWNERS`.

8. **Big infrastructure changes → announce on devtalk first.**
   For large tooling/build changes, it is common to post a short thread on
   [devtalk.blender.org → Documentation](https://devtalk.blender.org/c/documentation/12)
   *linking to the PR*, so translators and other contributors can follow along
   and comment. The PR is still the authoritative discussion venue ("By
   discussing stuff in the PR") — devtalk is optional pre-announcement.

---

## What This PR Changes (for reference)

```
git diff main..HEAD --stat

 Makefile                               |  185 ++-
 build_files/extensions/i18n_shards.py |   91 ++
 manual/conf.py                         |   45 +-
 tools/serve_docs.py                    |  480 ++++++++
 tools/translations/smart_mo_compile.py | 2015 ++++++++++++++++
 5 files changed, 2809 insertions(+), 7 deletions(-)
```

3 commits on branch:
```
13f132c  Add multi-language live build system with incremental translation shards
5caf16b  serve_docs.py: full language coverage and locale/ auto-detection
7ad1ad9  Rename liveboth → liveall
```

**Consideration**: 2809 lines is large. The 5 files are tightly coupled so they
can't be fully split without leaving the system half-broken. However the 3
commits could reasonably become 2 PRs:
- PR 1: `Makefile + conf.py + i18n_shards.py + smart_mo_compile.py` — the core build system
- PR 2: `tools/serve_docs.py` — the local server (independently useful)

Or keep as one PR with a good description. Discuss with @Blendify.

---

## Steps to Submit

### 1. Push the branch to your fork

```bash
git push origin feature/new_make_for_foreign_languages
```

Your fork URL: `https://projects.blender.org/hoanguk/blender-manual`

### 2. Open the PR on projects.blender.org

Navigate to your fork branch and click **"New Pull Request"**.

- **Base**: `blender/blender-manual` → `main`
- **Head**: `hoanguk/blender-manual` → `feature/new_make_for_foreign_languages`

---

## PR Title (commit message subject)

```
Makefile: Add multi-language live build system for local development
```

Or, to match the manual project's plainer style:

```
Build: Add multi-language live build system (liveall, smart_mo_compile, serve_docs)
```

---

## PR Description (what goes in the git log)

```
Adds a self-contained multi-language build and serve system for local
development. Lets contributors build all available locales in one command
and switch between them in a browser sidebar, without needing a remote
server or sudo.

New Makefile targets:
- make liveall       -- live-rebuild every locale from locale/ in parallel,
                        served on :8000 with a language switcher
- make build          -- one-shot build of all locales to build/<lang>/
- make serve         -- serve build/ with the language switcher
- make livehtml-direct  -- like make livehtml but outputs to build/<lang>/
- make gettext       -- monolithic .pot for the translator workflow

BF_LANGS is now auto-detected by scanning
locale/<lang>/LC_MESSAGES/blender_manual.po; en is always first.
Override: BF_LANGS="en fr vi" make build

New files:
- tools/serve_docs.py                   -- Python stdlib HTTP server with
                                           sidebar language switcher;
                                           --kill/--restart for scripts
- tools/translations/smart_mo_compile.py -- tiered .mo cache:
                                           mtime+size → sha256 →
                                           semantic blake2b hash →
                                           shard rebuild
- build_files/extensions/i18n_shards.py -- Sphinx env-get-outdated hook
                                           that marks docs outdated from
                                           shard .mo mtimes

Backward compatible: make html and make livehtml unchanged.
No new pip dependencies. No sudo required.

Ported from the Vietnamese manual build system
(blender-manual-translations companion repo).
```

---

## Below the `---` separator (reviewer notes, not in git log)

```
---

## How to Test

1. Download a couple of locale catalogs:
       git -C locale sparse-checkout add fr ru zh-hans

2. Live-rebuild all detected languages:
       make liveall
   Open http://localhost:8000 and use the sidebar language switcher.

3. One-shot build then serve:
       make build
       make serve

4. Single language still works:
       make livehtml BF_LANG=fr

5. Override language list:
       BF_LANGS="en fr" make build

## Notes / Questions for Reviewer

- smart_mo_compile.py is ~2000 lines. The core is the 4-tier cache and the
  per-doc shard writer. Happy to trim it or split into a separate PR if preferred.
- i18n_shards.py uses the env-get-outdated event (stable API since Sphinx 1.3).
  It has no effect on make html builds — falls back to the standard Sphinx path.
- liveall uses shell & for background jobs. Works on bash/zsh (Mac, Linux).
  Windows users would need WSL or run make livehtml BF_LANG=<code> per language.
- Should this be split into two PRs (build system | serve_docs.py)?
  I can do that if it makes the review easier.
```

---

## Full PR Body (combined, paste into Gitea)

```
Adds a self-contained multi-language build and serve system for local
development. Lets contributors build all available locales in one command
and switch between them in a browser sidebar, without needing a remote
server or sudo.

New Makefile targets:
- make liveall          live-rebuild every locale from locale/ in parallel,
                        served on :8000 with a language switcher
- make build             one-shot build of all locales to build/<lang>/
- make serve            serve build/ with the language switcher
- make livehtml-direct  like make livehtml but outputs to build/<lang>/
- make gettext          monolithic .pot for the translator workflow

BF_LANGS is now auto-detected from locale/<lang>/LC_MESSAGES/blender_manual.po;
en is always first. Override: BF_LANGS="en fr vi" make build

New files:
- tools/serve_docs.py                    Python stdlib HTTP server with
                                          sidebar language switcher;
                                          --kill/--restart for scripts
- tools/translations/smart_mo_compile.py Tiered .mo cache:
                                          mtime+size → sha256 →
                                          semantic blake2b hash → shard
- build_files/extensions/i18n_shards.py  Sphinx env-get-outdated hook that
                                          marks docs outdated from shard .mo mtimes

Backward compatible: make html and make livehtml unchanged.
No new pip dependencies. No sudo required.
Ported from the Vietnamese manual build system.

---

## How to Test

1. Download locale catalogs:  git -C locale sparse-checkout add fr ru
2. make liveall                → open http://localhost:8000, use the switcher
3. make build && make serve     → verify static builds + switcher
4. make livehtml BF_LANG=fr   → single-language path still works

## Notes for Reviewer

- smart_mo_compile.py is ~2000 lines; happy to split into a separate PR.
- i18n_shards.py uses the stable env-get-outdated API (Sphinx 1.3+); no
  effect on make html builds.
- liveall uses shell & background jobs — works on bash/zsh; Windows needs WSL.
- Should this be two PRs (build system | serve_docs.py)?
```

---

## After Opening the PR

1. Verify @Blendify is auto-assigned (CODEOWNERS will do this).
2. Optionally post a 2–3 sentence note on
   [devtalk.blender.org → Documentation](https://devtalk.blender.org/c/documentation/12)
   with a link to the PR — useful given the size of this change.
3. Respond to any review comments within a day or two.
4. If @Blendify asks to split the PR, the natural split is:
   - PR A: `Makefile` + `manual/conf.py` + `build_files/extensions/i18n_shards.py`
     + `tools/translations/smart_mo_compile.py`
   - PR B: `tools/serve_docs.py`

---

Sources consulted:
- [Pull Requests — Blender Developer Handbook](https://developer.blender.org/docs/handbook/contributing/pull_requests/)
- [Commit Messages — Blender Developer Handbook](https://developer.blender.org/docs/handbook/guidelines/commit_messages/)
- [Contributing Code — Blender Developer Handbook](https://developer.blender.org/docs/handbook/contributing/)
- [Contribute to Blender — Blender 5.x Manual](https://docs.blender.org/manual/en/latest/contribute/index.html)
- `.gitea/CODEOWNERS` in this repository
