# English reading-hint pill styling — plan

**Written:** `20260621_091708`
**Branch:** `feature/search_cache` (consider splitting to `feature/en-hint-pill`)
**Skill refs:** `project_management`, `translation-workflow`

## TL;DR

- Translated titles/nav carry an English reading-hint, e.g. `msgstr "Trình Bổ Sung [Add-ons]"`.
- Hint is **plain text inside `msgstr`** → no HTML element wraps it → pure CSS cannot target it.
- Fix: client-side JS wraps `[...]` runs in `<span class="i18n-en-hint">`; CSS renders a small muted pill.
- No `.po`, no `.rst`, no source changes. Additive theming. No-op on English build.

## Decisions / scope

- **Delimiter: `[...]` ONLY.** Parentheses `(...)` deliberately NOT matched — indistinguishable from ordinary Vietnamese parentheticals (same Latin script). Hints using `(...)` keep rendering as plain text.
- **No PO normalization now.** `( ) → [ ]` find/replace deferred (risky, manual review needed). Tracked under Follow-ups.
- **Scope of wrapping:** headings `h1–h6`, `.sidebar-tree a`, `.toctree-wrapper a`, `.related-pages a`. NOT body paragraphs (where `[...]` is often code/indices).
- **Exclusions:** never descend into `code/pre/kbd/samp/script/style`, `.headerlink`, already-wrapped `.i18n-en-hint`.
- **Gate:** runs only when `DOCUMENTATION_OPTIONS.LANGUAGE` ∉ {empty, `None`, `en`}.
- **Pill look:** uses theme vars (`--color-foreground-secondary`, `--color-background-secondary`, `--color-background-border`) → auto light/dark. Lighter borderless variant in sidebar. Print falls back to plain `[bracketed]` text.

## Files

- `build_files/theme/js/en_hint.js` — NEW. TreeWalker over SELECTORS text nodes; regex `/\[[^\][]+\]/g`; wrap matches, strip literal brackets.
- `build_files/theme/css/theme_overrides.css` — append `.i18n-en-hint` block (pill + sidebar variant + `@media print` fallback).
- `manual/conf.py` — add `"js/en_hint.js"` to `html_js_files` (furo branch only).

> Status: all three already drafted on disk (uncommitted) for review alongside this plan.

## Behaviour

- `Trình Bổ Sung [Add-ons]` → `Trình Bổ Sung` + ⟨pill: Add-ons⟩.
- Multiple hints per string supported.
- English build: script returns early → output byte-identical to before.

## Tuning knobs (all in the CSS block)

- Size: `.i18n-en-hint { font-size: 0.72em }`.
- Pill→plain: remove `background-color`/`border`/`border-radius`.
- Scope: edit `SELECTORS` array in `en_hint.js`.

## Edge cases

- `[...]` in headings that is NOT an English hint (rare in vi titles) → would also get pilled. Accepted; scope limits exposure.
- Nested/adjacent brackets `[[x]]` → inner `[^\][]+` avoids greedy span over `]`; `[x][y]` → two pills. OK.
- Empty `[]` → not matched (`+` requires ≥1 char).

## Verify

- Build vi: `make html BF_LANG=vi` (or usual vi target); hard-reload page.
  - Spot-check: addons index `Trình Bổ Sung [Add-ons]` shows pill; sidebar `[Installing Blender]` shows lighter pill; `(About Blender)` stays plain text (expected).
- Build en: confirm no `.i18n-en-hint` spans in output (script gated off).
- Print preview (vi): pill renders as `[Add-ons]` plain.
- Dark mode toggle: pill colors adapt.

## Follow-ups

- [ ] Decide whether to normalize PO hints `(English)` → `[English]` for uniform pills (separate, carefully-scoped find/replace — risky, NOT in this change).
- [ ] Optional: user toggle (show/hide hints) via a checkbox + localStorage.
- [ ] Consider moving this work onto its own `feature/en-hint-pill` branch before PR.
