# Configuration file for the Blender Manual documentation.
# created by the Sphinx 4.1.2 quickstart utility.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

from sphinx import version_info as sphinx_version

sys.path.insert(0, os.path.abspath(os.path.join("..", "build_files", "extensions")))

# Sphinx errors out on single threaded builds see T86621
sys.setrecursionlimit(2000)


def has_module(module_name):
    found = False
    try:
        __import__(module_name)
        found = True
    except ModuleNotFoundError as ex:
        if ex.name != module_name:
            raise ex
    return found


# -- Local Vars --------------------------------------------------------------

# Not used directly by Sphinx, but used by this file and the buildbot.

# Version number. Used to build paths and links.
blender_version = "5.3"
# Version label. Used only for display.
# Usually the same as blender_version, except for LTS.
blender_version_label = "5.3"

# -- Project information -----------------------------------------------------

project = "Blender {:s} Manual".format(blender_version_label)
copyright = ": This page is licensed under a CC-BY-SA 4.0 Int. License"
author = "Blender Documentation Team"

# The major project version, used as the replacement for |version|.
version = blender_version
# The full version, including alpha/beta/rc tags
# release = " ".join((blender_version, "alpha"))
release = blender_version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "404",
    "icons",
    "i18n_shards",
    "peertube",
    "reference",
    # Builds build/en/searchindex.pkl.gz from the doctree so the search overlay
    # works on the English (source) build, which has no .po file. No-op for
    # translated builds (they index from their PO via the watcher).
    "search_index_builder",
    # Translated-language counterpart of search_index_builder: extracts
    # allowlisted translated nodes as RepeatableRecord values, writes
    # build/<lang>/repeatable.{pkl.gz,po}, and renders the terminal English
    # reading-hint as an .i18n-en-hint pill. No-op for the English/source build.
    "repeatable_builder",
    # Centralises _static/_images under build/shared and references them per
    # language via symlink, so the ~250 MB image set is copied once instead of
    # per language. A language may override an asset by dropping a file under
    # locale/<lang>/_images or locale/<lang>/_static. See shared_assets.py.
    "shared_assets",
    # Fixes Sphinx's over-eager :kbd: splitting for translated text. Sphinx
    # splits on spaces, '-', '+', '^', which breaks Vietnamese key names like
    # 'Dấu Cộng (+) Bàn Số (NumpadPlus)' into per-word blocks. This extension
    # re-merges and re-splits at doctree-resolved using a smarter algorithm
    # that only breaks on top-level separators (not inside parentheses).
    "kbd_fix",
    "sphinx.ext.mathjax",
    "sphinx.ext.todo",
]

# Provides copy button next to code-blocks (nice to have but not essential).
if has_module("sphinx_copybutton"):
    extensions.append("sphinx_copybutton")

    # Exclude line numbers, prompts, and console text.
    copybutton_exclude = ".linenos, .gp, .go"

# This sometimes raises exceptions & performs online-access, make optional.
if not os.environ.get("NO_INTERSPHINX", "").strip("0"):
    extensions.append("sphinx.ext.intersphinx")

# Is there a better way to check for PDF building?
if "latex" in sys.argv:
    # To convert GIF images when making a PDF.
    extensions.append("sphinx.ext.imgconverter")
    image_converter = "magick"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["../build_files/templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
# exclude_patterns = ["_build"]

# A string of reStructuredText that will be included at the end of every
# source file that is read. This is a possible place to add substitutions
# that should be available in every file.
rst_epilog = """
.. |BLENDER_VERSION| replace:: {:s}
.. |BLENDER_VERSION_LABEL| replace:: {:s}
.. |TODO| replace:: The documentation here is incomplete, you can help by :doc:`contributing </contribute/manual/index>`.
""".format(blender_version, blender_version_label)

# Quit warnings about missing download file
# suppress_warnings = ["download.not_readable"]

# If set to a major.minor version string like "1.1", Sphinx will compare it
# with its version and refuse to build if it is too old.
needs_sphinx = "3.3"

# The default language to highlight source code in.
highlight_language = "python3"

# If true, figures, tables and code-blocks are automatically numbered if they have a caption.
numfig = False

# if set to 0, figures, tables and code-blocks are continuously numbered starting at 1.
numfig_secnum_depth = 0


# -- Options for Internationalization ----------------------------------------

# The code for the language the docs are written in.
# Any text automatically generated by Sphinx will be in that language.
language = "en"

# Directories in which to search for additional message catalogs,
# relative to the source directory.
#
# Sphinx evaluates conf.py BEFORE instantiating the builder, so the
# automatically-added `format_<name>` / `builder_<name>` tags are NOT yet
# in `tags` when this code runs. Any translator workflow that needs the
# monolithic blender_manual.pot (sphinx-intl / Weblate) must therefore
# pass `-t legacy_gettext` explicitly. The repo's `make gettext` target
# and tools/translations/update_po.py both forward this tag; ad-hoc
# `sphinx-build -b gettext` invocations need to add it manually.
if tags.has("legacy_gettext"):  # noqa: F821 (`tags` is injected by Sphinx)
    # Translator workflow: emit a monolithic blender_manual.pot.
    locale_dirs = ["../locale/"]
    gettext_compact = "blender_manual"
else:
    # Runtime build: shards win, canonical locale/ is a fallback.
    # With gettext_compact = False, Sphinx's `docname_to_domain()` returns
    # the doc slug verbatim, so each found doc depends only on its own
    # shard .mo -- killing the global-.mo fan-out that the legacy
    # `gettext_compact = "blender_manual"` setting caused.
    locale_dirs = ["../build/.i18n_shards/locale", "../locale/"]
    gettext_compact = False

# Disable Sphinx's built-in .mo writer so `tools/translations/smart_mo_compile.py`
# is the single writer of blender_manual.mo.
gettext_auto_build = False

# Strict policy: fuzzy translations are NOT installed.
gettext_allow_fuzzy_translations = False

# -- Search-tool constants ---------------------------------------------------
# These settings are read by tools/search/ (index_builder.py, index_loader.py)
# via ConfigRecord._read_conf_py() so that no path strings are hard-coded in
# the Python tools.  They also serve as explicit documentation of the project's
# file-naming conventions.

# RST source file suffix — mirrors Sphinx's built-in default and is used by
# index_builder.py to strip the suffix when mapping RST paths to HTML URLs.
source_suffix = [".rst"]

# HTML output page suffix — used by index_builder.py to produce the correct
# URL extension when converting RST locations to browsable HTML links.
html_page_suffix = ".html"

# Search index pickle filename — written by index_builder.py and read by
# index_loader.py.  Change here to rename the file in both places at once.
search_index_filename = "searchindex.pkl.gz"

# Sphinx HTML builder name — determines the output subdirectory for 'make html'
# (as opposed to 'make html-direct BF_LANG=<lang>').  Used by index_loader.py
# as a fallback location when looking for the English search index.
html_builder_name = "html"

# Command that tools/translations/update_po.py invokes to merge the generated
# .pot into each locale's .po.  Declared here so the tool name lives in one
# place: if sphinx-intl is ever renamed, or you prefer the interpreter-pinned
# module form, change it here (e.g. "python -m sphinx_intl") and update_po.py
# follows.  The value is parsed with shlex, so multi-word commands work.
sphinx_intl_command = "sphinx-intl"

# Repeatable-record extension output filenames (build_files/extensions/
# repeatable_builder.py).  The extension registers these as config values so
# they are overridable here in one place; change a name and both the pickle
# inventory and the PO catalogue follow.  Written to build/<lang>/.
repeatable_pickle_filename = "repeatable.pkl.gz"
repeatable_po_filename = "repeatable.po"
# Plain-text report of misaligned reading-hints: bracketed hints close to, but
# not exactly matching, their English source.  They are pilled "as written" and
# listed here (with build warnings) so the translator can fix the source.
repeatable_mismatch_filename = "repeatable_mismatch.txt"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "basic"

if has_module("furo"):
    html_theme = "furo"

# A dictionary of options that influence the look and feel of
# the selected theme. These are theme-specific.
html_theme_options = {}

# A list of paths that contain custom themes, either as subdirectories
# or as zip files. Relative paths are taken as relative to
# the configuration directory.
html_theme_path = []

if html_theme == "furo":
    html_theme_options = {
        "source_edit_link": "https://projects.blender.org/blender/blender-manual/_edit/main/manual/{filename}",
        "light_css_variables": {
            "color-brand-primary": "#265787",
            "color-brand-content": "#265787",
        },
    }

    html_sidebars = {
        "**": [
            "sidebar/brand.html",
            "sidebar/search.html",
            "sidebar/scroll-start.html",
            "sidebar/navigation.html",
            "sidebar/scroll-end.html",
            "sidebar/variant-selector.html",
        ]
    }

# The "title" for HTML documentation generated with Sphinx"s own templates.
# This is appended to the <title> tag of individual pages, and
# used in the navigation bar as the "topmost" element.
html_title = "Blender {:s} Manual".format(blender_version_label)

# The base URL which points to the root of the HTML documentation.
# It is used to indicate the location of document using
# The Canonical Link Relation.
html_baseurl = "https://docs.blender.org/manual/en/latest/"

# If given, this must be the name of an image file
# (path relative to the configuration directory) that is the logo of the docs,
# or URL that points an image file for the logo.
#
# Socket logo from: https://www.blender.org/about/logo
html_logo = "../build_files/theme/blender-logo.svg"

# If given, this must be the name of an image file
# (path relative to the configuration directory) that is the favicon of
# the docs, or URL that points an image file for the favicon.
html_favicon = "../build_files/theme/favicon.png"

if html_theme == "furo":
    html_css_files = [
        "css/theme_overrides.css",
        "css/version_switch.css",
        "fonts/bl-icons.css",
    ]
    html_js_files = [
        "js/version_switch.js",
        "js/sidebar_splitter.js",
    ]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["../build_files/theme"]

# Shared-assets policy: image localization is handled by same-path files under
# locale/<lang>/_images, not by Sphinx's foo.<lang>.png convention. This keeps
# every language, including English, on the shared/_images link path unless an
# explicit locale/<lang>/_images override materializes that one file locally.
figure_language_filename = "{root}{ext}"

# shared_assets extension: centralise _static/_images under build/shared and
# reference them per language via symlink (the ~250 MB image set is copied once,
# not per language). Defaults below; override per build with the BF_SHARED_* env
# vars (kept consistent with the BF_LANG/BF_LANGS convention).
shared_assets_enabled = os.environ.get("BF_SHARED_ASSETS", "1") != "0"
shared_assets_subdirs = os.environ.get("BF_SHARED_SUBDIRS", "_images _static").split()
shared_assets_link_mode = os.environ.get("BF_SHARED_LINK_MODE", "auto")
shared_assets_copy_new = os.environ.get("BF_SHARED_COPY_NEW", "1") != "0"
# Empty -> extension derives build/shared (sibling of outdir) and ../locale.
shared_assets_root = os.environ.get("BF_SHARED_ROOT", "")
shared_assets_override_root = os.environ.get("BF_SHARED_OVERRIDE_ROOT", "")

# If this is not None, a "Last updated on:" timestamp is inserted at
# every page bottom, using the given strftime() format.
# The empty string is equivalent to "%b %d, %Y"
# (or a locale-dependent equivalent).
html_last_updated_fmt = "%Y-%m-%d"

# Additional templates that should be rendered to HTML pages,
# must be a dictionary that maps document names to template names.
html_additional_pages = {
    "404": "404.html",
}

# If true, the reST sources are included in the HTML build as _sources/name.
html_copy_source = False

# If true (and html_copy_source is true as well), links to the reST sources
# will be added to the sidebar.
html_show_sourcelink = False

# If nonempty, an OpenSearch description file will be output,
# and all pages will contain a <link> tag referring to it.
# Ed. Note: URL has to be adapted, when versioning is set up.
html_use_opensearch = "https://docs.blender.org/manual/{:s}/latest".format(
    os.environ.get("BF_LANG", language)
)

# Variables available in Jinja2 templates.
# 'available_langs': language codes built by 'make both'; empty in single-lang
# builds.  'current_lang': mirrors BF_LANG / -D language passed by the
# Makefile.  Used by tools/serve_docs.py to inject the local lang switcher,
# and optionally by sidebar templates.
html_context = {
    "available_langs": os.environ.get("BF_LANGS", "").split(),
    "current_lang": os.environ.get("BF_LANG", language),
}

# If true, "(C) Copyright …" is shown in the HTML footer.
html_show_copyright = True

# If true, "Created using Sphinx" is shown in the HTML footer.
html_show_sphinx = False

# If true, the text around the keyword is shown as summary of each search result.
html_show_search_summary = True


# -- Options for HTML help output --------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "Blender Reference Manual"


# -- Options for Epub output -------------------------------------------------

# The basename for the epub file. It defaults to the project name.
# epub_basename = ""

# The HTML theme for the epub output. Since the default themes are
# not optimized for small screen space, using the same theme for HTML
# and epub output is usually not wise.
epub_theme = "epub"

# Bibliographic Dublin Core info.
# These default to their non epub counterparts.
# epub_title = ""
epub_description = "Blender Reference Manual"
# epub_author = ""
epub_publisher = "Blender Foundation"

# The language of the text. It defaults to the language option
# or "en" if the language is not set.
# epub_language = ""

epub_copyright = "This manual is licensed under a CC-BY-SA 4.0 Int. License."

# An identifier for the document. This is put in the Dublin Core metadata.
# For published documents this is the ISBN number, but you can also
# use an alternative scheme, e.g. the project homepage.
# epub_identifier = ""

# The publication scheme for the epub_identifier.
# This is put in the Dublin Core metadata.
# For published books the scheme is "ISBN".
# If you use the project homepage, "URL" seems reasonable.
# epub_scheme = ""

# A unique identifier for the document.
# This is put in the Dublin Core metadata.
# epub_uid = ""

# The cover page information. This is a tuple containing the filenames of
# the cover image and the html template.
epub_cover = (
    "_static/cover.png",
    "epub-cover.html",
)

epub_css_files = ["css/epub_overrides.css"]

# Meta data for the guide element of content.opf.
# This is a sequence of tuples containing the type,
# the uri and the title of the optional guide information.
# epub_guide = ()

# HTML files that should be inserted before the pages created by sphinx.
# The format is a list of tuples containing the path and title.
# epub_pre_files = []

# Additional files that should be inserted after the text generated by Sphinx.
# It is a list of tuples containing the file name and the title.
# epub_post_files = []

# A list of files that are generated/copied in the build directory
# but should not be included in the epub file.
epub_exclude_files = ["search.html", "404.html"]

# The depth of the table of contents in the file toc.ncx.
epub_tocdepth = 2

# This flag determines if a toc entry is inserted again at
# the beginning of its nested toc listing.
# epub_tocdup = True

# This setting control the scope of the epub table of contents.
# epub_tocscope = "default"

# This flag determines if sphinx should try to fix image formats
# that are not supported by some epub readers.
# epub_fix_images = False

# This option specifies the maximum width of images.
# epub_max_image_width = 0

# Control whether to display URL addresses.
epub_show_urls = "no"

# If true, add an index to the epub document.
# epub_use_index = True


# -- Options for LaTeX output ------------------------------------------------
# see https://github.com/sphinx-doc/sphinx/issues/3289

latex_engine = "xelatex"

# This value determines how to group the document tree into LaTeX source files.
# It must be a list of tuples
# (startdocname, targetname, title, author, theme, toctree_only).
latex_documents = [
    (
        "index",
        "blender_manual.tex",
        "Blender User Manual",
        "Blender Community",
        "manual",
    ),
]

# If given, this must be the name of an image file
# (relative to the configuration directory) that is the logo of the docs.
# It is placed at the top of the title page.

# Disable for now, causes:
# LaTeX Error: Cannot determine size of graphic in blender-logo.svg (no
# Boundin gBox).

# latex_logo = "../build_files/theme/blender-logo.svg"

# This value determines the topmost sectioning unit. It should be chosen from
# "part", "chapter" or "section".
# latex_toplevel_sectioning = "None"

# A list of document names to append as an appendix to all manuals.
# latex_appendices = []

# If true, generate domain-specific indices in addition to the general index.
# latex_domain_indices = True

# If true, add page references after internal references.
# This is very useful for printed copies of the manual.
# latex_show_pagerefs = False

# Control whether to display URL addresses.
latex_show_urls = "no"

latex_elements = {
    # The paper size ("letterpaper" or "a4paper").
    "papersize": "a4paper",

    # The font size ("10pt", "11pt" or "12pt").
    "pointsize": "10pt",

    # Additional stuff for the LaTeX preamble.

    "sphinxsetup": "hmargin=0.75in, vmargin=1in",

    "classoptions": ",openany,oneside",
    #  "babel": "\\usepackage[english]{babel}",
    # note that xelatex will use polyglossia by default,
    # but if "babel" key is redefined like above, it will use babel package.

    "fontpkg": r"""
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}
""",

    "preamble": u"""
\\renewenvironment{wrapfigure}[2]{\\begin{figure}[H]}{\\end{figure}}
\\usepackage{newunicodechar}

\\usepackage{pifont}
\\newunicodechar{✔}{\\ding{52}}
\\newunicodechar{✗}{\\ding{55}}
\\newunicodechar{✛}{\\ding{59}}
""",

}


# -- Options for manual page output ------------------------------------------

# This value determines how to group the document tree into manual pages.
# It must be a list of tuples
# (startdocname, name, description, authors, section).
man_pages = [
    (
        "index",
        "manual_docs",
        "Blender Manual Documentation Documentation",
        [""],
        1,
    ),
]

# If true, add URL addresses after links.
man_show_urls = False


# -- Options for Texinfo output ----------------------------------------------

# This value determines how to group the document tree into
# Texinfo source files. # It must be a list of tuples
# (startdocname, targetname, title, author, dir_entry,
# description, category, toctree_only)
texinfo_documents = [
    (
        "index",
        "Blender Reference Manual",
        "Blender Manual Documentation",
        "Blender Documentation Team",
        "Blender Reference Manual",
    ),
]

# A list of document names to append as an appendix to all manuals.
# texinfo_appendices = []

# If true, generate domain-specific indices in addition to the general index.
# texinfo_domain_indices = True

# Control how to display URL addresses.
# texinfo_show_urls = "footnote"

# If true, do not generate a @detailmenu in the "Top" node's menu
# containing entries for each sub-node in the document.
# texinfo_no_detailmenu = False

# -- Options for linkcheck output --------------------------------------------

linkcheck_allowed_redirects = {
    # All HTTP redirections from the source URI to
    # the canonical URI will be treated as "working".
    r'https://blender.stackexchange.com/questions/.*': r'https://blender.stackexchange.com/questions/.*/',
    r'https://blender.stackexchange.com/a/.*': r'https://blender.stackexchange.com/questions/.*/',
    r'https://blenderartists.org/t/.*': r'https://blenderartists.org/t/.*/'
}


# -- Extension configuration -------------------------------------------------

intersphinx_mapping = {
    "blender_api": (
        "https://docs.blender.org/api/{:s}/".format(blender_version),
        None,
    ),
}
peertube_instance = "https://video.blender.org/"

# If true, `todo` and `todoList` produce output, else they produce nothing.
# if not release.endswith("release"):
todo_include_todos = False
# todo_link_only = True


# ----------------------------------------------------------------------------
# Monkey Patch, without this "zh-hant" fails
#
# See: https://lists.blender.org/pipermail/bf-docboard/2017-October/005259.html


def monkey_patch_babl_locale_dash():
    try:
        from sphinx.util.i18n import CatalogInfo
    except ImportError:
        return
    CatalogInfo._write_mo_real = CatalogInfo.write_mo
    if sphinx_version >= (4, 3, 0):
        CatalogInfo.write_mo = lambda self, locale, use_fuzzy: CatalogInfo._write_mo_real(
            self,
            locale.replace("-", "_"),
        )
    else:
        CatalogInfo.write_mo = lambda self, locale: CatalogInfo._write_mo_real(
            self,
            locale.replace("-", "_"),
        )


monkey_patch_babl_locale_dash()
