"""Tests for the mtime-aware cache in tools/search/index_loader.py.

The English search index is rewritten by the doctree extension on every
incremental build, but English has no PO file so the MultiPOWatcher never
invalidates its cache. load_index() must therefore reload automatically when
the pickle on disk changes — otherwise search stays stale until restart.

Run: python3 -m pytest tests/search/test_index_loader_mtime.py -q
"""

from __future__ import annotations

import gzip
import os
import pickle
import sys

# Make the shared search modules importable.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_TOOLS = os.path.join(_REPO_ROOT, "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from search import index_loader  # noqa: E402
from search.index_loader import load_index  # noqa: E402
from search.searchable_record import SearchableRecord  # noqa: E402


def _rec(msgid: str) -> SearchableRecord:
    return SearchableRecord(
        msgid=msgid,
        msgstr="",
        msgid_stripped=msgid,
        msgstr_stripped="",
        locations=[("manual/x.rst", 1)],
        html_pages=["/en/x.html"],
        section_keys=["x"],
        flags=[],
    )


def _write(path, records, mtime: float) -> None:
    with gzip.open(path, "wb") as fh:
        pickle.dump(records, fh, protocol=pickle.HIGHEST_PROTOCOL)
    os.utime(path, (mtime, mtime))   # pin mtime so the change is unambiguous


def test_reloads_when_pickle_rewritten(tmp_path):
    pkl = tmp_path / "searchindex.pkl.gz"
    lang = "en-test-reload"
    index_loader._cache.pop(lang, None)

    _write(pkl, [_rec("Alpha")], mtime=1000.0)
    idx1 = load_index(pkl, lang)
    assert [r.msgid for r in idx1.records] == ["Alpha"]
    assert idx1.mtime == 1000.0

    # Rewrite with new content and a newer mtime — no explicit invalidation.
    _write(pkl, [_rec("Beta"), _rec("Gamma")], mtime=2000.0)
    idx2 = load_index(pkl, lang)
    assert [r.msgid for r in idx2.records] == ["Beta", "Gamma"]
    assert idx2.mtime == 2000.0
    assert idx2 is not idx1

    index_loader._cache.pop(lang, None)


def test_cache_hit_when_mtime_unchanged(tmp_path):
    pkl = tmp_path / "searchindex.pkl.gz"
    lang = "en-test-cachehit"
    index_loader._cache.pop(lang, None)

    _write(pkl, [_rec("Alpha")], mtime=1500.0)
    idx1 = load_index(pkl, lang)
    idx2 = load_index(pkl, lang)
    assert idx2 is idx1   # same object — no reload when mtime is identical

    index_loader._cache.pop(lang, None)
