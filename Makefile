# -*- mode: gnumakefile; tab-width: 4; indent-tabs-mode: t; -*-
# vim: tabstop=4

define HELP_TEXT
Custom Targets
==============

Convenience targets provided for building docs.

- setup                to install Sphinx in a virtual environment.
- html (default)       to build HTML documentation.
- livehtml             to auto build HTML on file changes on host on localhost.
- livehtml-direct      to auto build one language to build/<lang>/ (use with 'make serve').
- build                to build all BF_LANGS to build/<lang>/ each.
- liveall              to live-rebuild all BF_LANGS and serve them (single command).
- serve                to serve the build/ directory on localhost:8000.
- epubpdf              to convert an epub file to PDF.

Translations
------------

- update_po            to update PO message catalogs.
- report_po_progress   to check the progress/fuzzy strings.

Checking
--------

- check_structure      to check the structure of all .rst files.
- check_syntax         to check the syntax of all .rst files.
- check_spelling       to check spelling for text in RST files.
- check_spelling_new   to check spelling for text in RST files (experimental new script)

Utilities
---------

- update               to update the repository to the most recent version.
- format_py            to auto-format Python scripts.

Environment Variables
---------------------

- NO_INTERSPHINX
  When non-zero & non-empty any build-targets that run sphinx will not use
  'intersphinx' (which requires online access).

- BF_LANG
  Language code for the current build (default: en).
  Passed to Sphinx as -D language=<code> and read by conf.py.

- BF_LANGS
  Space-separated list of language codes built by 'make build' (default: auto-detected from locale/).
  Each language is built into build/<lang>/ and the sidebar language
  switcher will list exactly these codes as locally available.

endef
# HELP_TEXT (end)

# -----------
# System Vars
OS:=$(shell uname -s)

# End System Vars
# ---------------

# Use virtual environment if it exists.
SPHINX_BIN_PATH := .venv/bin/
ifeq (,$(wildcard $(SPHINX_BIN_PATH)))
	SPHINX_BIN_PATH :=
endif

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXBUILD     ?= $(SPHINX_BIN_PATH)sphinx-build
SPHINXAUTOBUILD ?= $(SPHINX_BIN_PATH)sphinx-autobuild
SOURCEDIR        = ./manual
BUILDDIR        ?= build
BF_LANG         ?= en
SPHINXOPTS      ?= -j auto -D language='$(BF_LANG)'
LATEXOPTS       ?= "-interaction nonstopmode"
SERVE_OPTS      ?=

# Auto-detect BF_LANGS from locale/ directory if not set.
# Scans for locale/<lang>/LC_MESSAGES/blender_manual.po and builds the list.
# English is always included first.
ifeq ($(origin BF_LANGS),undefined)
    _DETECTED_LANGS := $(shell \
        find locale -maxdepth 3 -name 'blender_manual.po' 2>/dev/null \
        | sed 's|locale/||;s|/LC_MESSAGES/.*||' \
        | sort -u \
        | grep -v '^en$$' \
        | tr '\n' ' ')
    BF_LANGS := en $(_DETECTED_LANGS)
endif

# Export BF_LANG so conf.py can read it via os.environ when sphinx-build runs.
export BF_LANG
export BF_LANGS


# -----------------------
# for echoing output only
ifeq ($(OS), Darwin)
	OPEN_CMD="open" # MACOS.
else
	OPEN_CMD="xdg-open" # Linux/FreeBSD.
endif
# end output for echoing
# ----------------------


ifneq ("$(shell which $(SPHINXAUTOBUILD) 2> /dev/null)", "")
	.DEFAULT_GOAL := livehtml
else
	.DEFAULT_GOAL := html
endif


# --------------------
# Check commands exist

.SPHINXBUILD_EXISTS:
	@if ! which $(SPHINXBUILD) > /dev/null 2>&1; then \
		echo -e >&2 \
			"The '$(SPHINXBUILD)' command was not found.\n"\
			"Make sure you have Sphinx installed, then set the SPHINXBUILD environment variable to\n"\
			"point to the full path of the '$(SPHINXBUILD)' executable.\n"\
			"Alternatively you can add the directory with the executable to your PATH.\n"\
			"If you don't have Sphinx installed, grab it from http://sphinx-doc.org)\n"; \
		false; \
	fi

# End command checking
# --------------------

setup:
	python3 -m venv .venv
	.venv/bin/python3 -m pip install pip --upgrade
	.venv/bin/python3 -m pip install -r requirements.txt --upgrade

# --- smart_mo_compile.py arguments (shared by html / livehtml) --------------
# Persistent shard cache: each doc gets its own .mo under
# $(BUILDDIR)/.i18n_shards/locale/<lang>/LC_MESSAGES/<slug>.mo, and the
# tiered cache + lock live under $(BUILDDIR)/.translation_cache/. Both
# directories sit under $(BUILDDIR) on purpose: `make clean` wipes them
# together with Sphinx's doctrees, so the three-piece "last good state"
# (cache + shards + doctrees) is always consistent.
SMART_MO_ARGS = --language=$(BF_LANG) \
                --cache-dir=$(BUILDDIR)/.translation_cache \
                --shard-root=$(BUILDDIR)/.i18n_shards/locale

# Live rebuilds already run Sphinx because sphinx-autobuild sees the edited PO.
# Let build_files/extensions/i18n_shards.py mark docs outdated from the generated
# shard .mo mtimes, and skip RST mtime touches that cause a second no-op rebuild.
SMART_MO_LIVE_EXTRA_ARGS = --no-touch-rst

# --- One-shot HTML build ----------------------------------------------------
html: .SPHINXBUILD_EXISTS
	@python3 tools/translations/smart_mo_compile.py $(SMART_MO_ARGS) \
	    --doctree-dir=$(BUILDDIR)/doctrees
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "To view, run:"
	@echo "  "$(OPEN_CMD) $(shell pwd)"/$(BUILDDIR)/html/index.html"

# --- Continuous-rebuild HTML server -----------------------------------------
livehtml:
	@if echo "$(BF_LANG)" | grep -q ' '; then \
	    echo "Error: BF_LANG must be a single language code, e.g. 'make livehtml BF_LANG=vi'."; \
	    echo "       To build multiple languages use 'make liveall'."; \
	    exit 1; \
	fi
	@watch_opt=""; \
	if [ -d "locale/$(BF_LANG)/LC_MESSAGES" ]; then watch_opt="--watch locale/$(BF_LANG)/LC_MESSAGES"; fi; \
	$(SPHINXAUTOBUILD) \
	    --pre-build "python3 tools/translations/smart_mo_compile.py $(SMART_MO_ARGS) --doctree-dir=$(BUILDDIR)/html/.doctrees $(SMART_MO_LIVE_EXTRA_ARGS)" \
	    $$watch_opt \
	    --ignore "*/LC_MESSAGES/*.mo" \
	    --ignore "*/LC_MESSAGES/*.hash" \
	    --ignore "*/LC_MESSAGES/*.lock" \
	    --ignore "$(BUILDDIR)/.i18n_shards/*" \
	    --ignore "$(BUILDDIR)/.translation_cache/*" \
	    --open-browser --delay 0 \
	    "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

# --- Per-language live rebuild (pair with 'make serve' in another terminal) -
livehtml-direct:
	@if echo "$(BF_LANG)" | grep -q ' '; then \
	    echo "Error: BF_LANG must be a single language code, e.g. 'make livehtml-direct BF_LANG=vi'."; \
	    exit 1; \
	fi
	@watch_opt=""; \
	if [ -d "locale/$(BF_LANG)/LC_MESSAGES" ]; then watch_opt="--watch locale/$(BF_LANG)/LC_MESSAGES"; fi; \
	$(SPHINXAUTOBUILD) \
	    --pre-build "python3 tools/translations/smart_mo_compile.py --language=$(BF_LANG) --cache-dir=$(BUILDDIR)/.translation_cache --shard-root=$(BUILDDIR)/.i18n_shards/locale --doctree-dir=$(BUILDDIR)/.doctrees/$(BF_LANG) $(SMART_MO_LIVE_EXTRA_ARGS)" \
	    $$watch_opt \
	    --ignore "*/LC_MESSAGES/*.mo" \
	    --ignore "*/LC_MESSAGES/*.hash" \
	    --ignore "*/LC_MESSAGES/*.lock" \
	    --ignore "$(BUILDDIR)/.i18n_shards/*" \
	    --ignore "$(BUILDDIR)/.translation_cache/*" \
	    --delay 0 \
	    "$(SOURCEDIR)" "$(BUILDDIR)/$(BF_LANG)" \
	    -j auto -D language='$(BF_LANG)' \
	    -d "$(BUILDDIR)/.doctrees/$(BF_LANG)" $(O)

# --- Live-rebuild all BF_LANGS + serve in one command ------------------------
liveall: ensure-lang-builds
	@echo "Stopping existing liveall listeners..."
	@python3 tools/serve_docs.py --kill --quiet $(SERVE_OPTS)
	@port=8081; \
	for lang in $(BF_LANGS); do \
	    python3 tools/serve_docs.py --port $$port --kill --quiet; \
	    port=$$((port + 1)); \
	done
	@echo "Starting live rebuilders for: $(BF_LANGS)"
	@pids=""; \
	port=8081; \
	for lang in $(BF_LANGS); do \
	    echo "  [$$lang] → $(BUILDDIR)/$$lang/ (autobuild on port $$port)"; \
	    watch_arg=""; \
	    if [ -d "locale/$$lang/LC_MESSAGES" ]; then watch_arg="--watch locale/$$lang/LC_MESSAGES"; fi; \
	    BF_LANG=$$lang BF_LANGS="$(BF_LANGS)" $(SPHINXAUTOBUILD) \
	        --pre-build "python3 tools/translations/smart_mo_compile.py --language=$$lang --cache-dir=$(BUILDDIR)/.translation_cache --shard-root=$(BUILDDIR)/.i18n_shards/locale --doctree-dir=$(BUILDDIR)/.doctrees/$$lang $(SMART_MO_LIVE_EXTRA_ARGS)" \
	        $$watch_arg \
	        --ignore "*/LC_MESSAGES/*.mo" \
	        --ignore "*/LC_MESSAGES/*.hash" \
	        --ignore "*/LC_MESSAGES/*.lock" \
	        --ignore "$(BUILDDIR)/.i18n_shards/*" \
	        --ignore "$(BUILDDIR)/.translation_cache/*" \
	        --host 127.0.0.1 --port $$port --delay 0 \
	        "$(SOURCEDIR)" "$(BUILDDIR)/$$lang" \
	        -j auto -D language="$$lang" \
	        -d "$(BUILDDIR)/.doctrees/$$lang" & \
	    pids="$$pids $$!"; \
	    port=$$((port + 1)); \
	done; \
	echo ""; \
	echo "Rebuilders running. Starting unified server at http://localhost:8000 ..."; \
	echo "Live-reload is on: edited pages refresh automatically once a rebuild finishes."; \
	echo "Press Ctrl-C to stop."; \
	python3 tools/serve_docs.py --build-dir $(BUILDDIR) --langs "$(BF_LANGS)" --restart --open $(SERVE_OPTS); \
	for pid in $$pids; do kill "$$pid" 2>/dev/null; done; \
	echo "Stopped."

# --- Ensure requested language output dirs exist before serving --------------
ensure-lang-builds:
	@for lang in $(BF_LANGS); do \
	    if [ -f "$(BUILDDIR)/$$lang/index.html" ]; then \
	        continue; \
	    fi; \
	    if [ "$$lang" != "en" ]; then \
	        if [ ! -d "locale/$$lang/LC_MESSAGES" ] || \
	           ! find "locale/$$lang/LC_MESSAGES" -type f -print -quit | grep -q .; then \
	            echo "Skipping missing $(BUILDDIR)/$$lang/: no locale/$$lang/LC_MESSAGES files."; \
	            continue; \
	        fi; \
	    fi; \
	    echo ""; \
	    echo "=== Initial build for missing language: $$lang ==="; \
	    BF_LANG=$$lang BF_LANGS="$(BF_LANGS)" \
	    $(MAKE) html-direct BF_LANG=$$lang || exit 1; \
	done

# --- Per-language HTML build for 'make build' --------------------------------
html-direct: .SPHINXBUILD_EXISTS
	@python3 tools/translations/smart_mo_compile.py \
	    --language=$(BF_LANG) \
	    --cache-dir=$(BUILDDIR)/.translation_cache \
	    --shard-root=$(BUILDDIR)/.i18n_shards/locale \
	    --doctree-dir=$(BUILDDIR)/.doctrees/$(BF_LANG)
	$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/$(BF_LANG)" \
	    -j auto -D language='$(BF_LANG)' \
	    -d "$(BUILDDIR)/.doctrees/$(BF_LANG)" $(O)

# --- Build every language in BF_LANGS to build/<lang>/ ----------------------
build: .SPHINXBUILD_EXISTS
	@echo "Building languages: $(BF_LANGS)"
	@for lang in $(BF_LANGS); do \
	    echo ""; \
	    echo "=== Building: $$lang ==="; \
	    BF_LANG=$$lang BF_LANGS="$(BF_LANGS)" \
	    $(MAKE) html-direct BF_LANG=$$lang || exit 1; \
	done
	@echo ""
	@echo "Done. Serve with: make serve"
	@echo "Or open directly:"
	@for lang in $(BF_LANGS); do \
	    echo "  "$(OPEN_CMD) $(shell pwd)/$(BUILDDIR)/$$lang/index.html; \
	done

# --- Local HTTP server with language switching --------------------------------
serve: ensure-lang-builds
	@python3 tools/serve_docs.py --build-dir $(BUILDDIR) --langs "$(BF_LANGS)" --open $(SERVE_OPTS)

# --- Translator workflow: monolithic blender_manual.pot --------------------
gettext: .SPHINXBUILD_EXISTS
	$(SPHINXBUILD) -M gettext "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) -t legacy_gettext $(O)

epubpdf: .SPHINXBUILD_EXISTS
	@$(SPHINXBUILD) -M epub "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@ebook-convert $(BUILDDIR)/epub/*.epub blender_manual.pdf \
		--pdf-default-font-size 16 \
		--pdf-mono-font-size 14 \
		--margin-left 0 \
		--margin-right 0 \
		--pdf-page-margin-left 50 \
		--pdf-page-margin-right 50 \
		--pdf-page-margin-top 50 \
		--pdf-page-margin-bottom 50 \

check_syntax:
	@python3 tools/check_source/check_syntax.py --long --title --kbd > rst_check_syntax.log
	@echo "Lines:" `cat rst_check_syntax.log | wc -l`
	@python3 tools/utils_ide/open_quickfix_in_editor.py rst_check_syntax.log
	@rm rst_check_syntax.log

check_structure:
	@python3 tools/check_source/check_images.py
	@python3 tools/check_source/check_structure.py

check_spelling:
	@python3 tools/check_source/check_spelling.py

check_spelling_new:
	@python3 tools/check_source/check_spelling_new.py

# Extra language codes passed as make targets (e.g. make checkout_locale vi fr)
# Only active when checkout_locale is actually being built.
ifneq ($(filter checkout_locale,$(MAKECMDGOALS)),)
_CHECKOUT_EXTRA := $(filter-out checkout_locale,$(MAKECMDGOALS))
endif

checkout_locale:
	@python3 ./build_files/utils/checkout_locale.py $(_CHECKOUT_EXTRA) $(LANGUAGES)

# Silently absorb extra language codes so make doesn't error on unknown targets.
# Guard ensures this only fires during a checkout_locale invocation.
ifneq ($(filter checkout_locale,$(MAKECMDGOALS)),)
ifneq ($(_CHECKOUT_EXTRA),)
$(_CHECKOUT_EXTRA):
	@:
endif
endif

update_po:
	@python3 ./tools/translations/update_po.py

report_po_progress:
	@python3 tools/translations/report_translation_progress.py --quiet \
	         `find locale/ -maxdepth 1 -mindepth 1 -type d -not -iwholename '*.git*' -printf 'locale/%f\n' | sort`

update:
	@python3 ./build_files/utils/make_update.py

format_py:
	@autopep8 --in-place --recursive .

# ----------------------
# Help for build targets

export HELP_TEXT
help:
	@echo ""
	@echo "Sphinx"
	@echo "======"
	@echo ""
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo ""
	@echo "$$HELP_TEXT"

.PHONY: help html-direct livehtml-direct build liveall ensure-lang-builds serve gettext Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option. $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile .SPHINXBUILD_EXISTS
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
