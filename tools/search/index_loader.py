"""Thread-safe search index loader with pre-partitioned batches.

Loads the gzip-compressed pickle produced by index_builder.py, caches it in
memory per language, and pre-splits records into worker batches (§18.4).

All file-naming constants (*index_filename*, *html_builder_name*,
*default_language*) come from
:class:`~translations.smart_mo_compile.ConfigRecord` so nothing is hard-coded
in this module.
"""

from __future__ import annotations

import gzip
import os
import pickle
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import TypeGuard

from .searchable_record import SearchableRecord
from common.constants import (  # type: ignore[import-not-found]
    DEFAULT_LANGUAGE,
    HTML_BUILDER_NAME,
    SEARCH_INDEX_FILENAME,
)

# Logging goes through Sphinx's logging wrapper.
from sphinx.util.logging import getLogger as _get_logger  # noqa: E402

_logger = _get_logger(__name__)


def debug_log(message: str, *args: object, **_kw: object) -> None:
    _logger.debug(message, *args)


@dataclass
class LoadedIndex:
    """Loaded index with records and pre-partitioned worker batches."""
    records: list[SearchableRecord]
    batches: list[list[SearchableRecord]]   # pre-split for Pool workers
    lang: str
    pkl_path: Path
    mtime: float = 0.0   # st_mtime of pkl_path when loaded; used to auto-reload


_cache: dict[str, LoadedIndex] = {}
_lock = threading.Lock()


def _n_workers() -> int:
    return max(1, (os.cpu_count() or 2) - 2)


def _make_batches(
    records: list[SearchableRecord],
    n: int,
) -> list[list[SearchableRecord]]:
    """Split records into *n* batches; last batch absorbs the remainder."""
    wants_single_batch = n <= 1
    has_no_records = not records
    if wants_single_batch or has_no_records:
        return [records]

    batch_size = max(1, len(records) // n)
    batches = [records[i * batch_size : (i + 1) * batch_size] for i in range(n - 1)]
    batches.append(records[(n - 1) * batch_size :])
    return [batch for batch in batches if batch]   # drop any empty trailing batch


def _pkl_path_for(
    build_dir: Path,
    lang: str,
    index_filename: str = SEARCH_INDEX_FILENAME,
    html_builder_name: str = HTML_BUILDER_NAME,
    default_language: str = DEFAULT_LANGUAGE,
) -> Path:
    """Resolve the pickle path, mirroring serve_docs.py's lang_dirs fallback.

    Parameters come from ConfigRecord so no strings are hard-coded here.
    """
    dedicated = build_dir / lang / index_filename
    fallback = build_dir / html_builder_name / index_filename

    has_dedicated_index = dedicated.exists()
    if has_dedicated_index:
        return dedicated

    is_default_language = lang == default_language
    has_fallback_index = fallback.exists()
    if is_default_language and has_fallback_index:
        return fallback

    return dedicated   # caller handles FileNotFoundError


def load_index(pkl_path: Path, lang: str) -> LoadedIndex:
    """Load and cache the search index for *lang*.

    Thread-safe: if two requests race for the same language, the second
    blocks until the first load completes, then reads from cache.
    Pre-partitions batches at load time so no slicing is needed at query time.

    The cache is mtime-aware: if *pkl_path* has been rewritten since it was
    cached (e.g. by the doctree extension for English, or a manual rebuild)
    the index is reloaded automatically — no explicit invalidate or server
    restart needed. The PO watcher's invalidate_cache() still works and is
    complementary.
    """
    try:
        mtime = pkl_path.stat().st_mtime
    except OSError:
        mtime = 0.0

    def is_cache_fresh(entry: LoadedIndex | None) -> TypeGuard[LoadedIndex]:
        """True when *entry* is cached and matches the pickle on disk."""
        return entry is not None and entry.mtime == mtime

    # Fast path: serve from cache without locking when it is already fresh.
    cached = _cache.get(lang)
    if is_cache_fresh(cached):
        return cached

    # Slow path: re-check under the lock (another thread may have just loaded),
    # then load from disk only if the cache is still stale.
    with _lock:
        cached = _cache.get(lang)
        if not is_cache_fresh(cached):
            with gzip.open(pkl_path, "rb") as fh:
                records: list[SearchableRecord] = pickle.load(fh)
            _cache[lang] = LoadedIndex(
                records=records,
                batches=_make_batches(records, _n_workers()),
                lang=lang,
                pkl_path=pkl_path,
                mtime=mtime,
            )
    return _cache[lang]


def load_index_for(
    build_dir: Path,
    lang: str,
    index_filename: str = SEARCH_INDEX_FILENAME,
    html_builder_name: str = HTML_BUILDER_NAME,
    default_language: str = DEFAULT_LANGUAGE,
) -> LoadedIndex | None:
    """Convenience wrapper that resolves the pickle path before loading.

    Returns *None* if no index file exists for *lang*.
    """
    pkl_path = _pkl_path_for(
        build_dir, lang, index_filename, html_builder_name, default_language
    )
    has_index_file = pkl_path.exists()
    if not has_index_file:
        return None
    return load_index(pkl_path, lang)


def invalidate_cache(lang: str) -> None:
    """Evict *lang* from the in-memory cache.

    The next call to load_index() for that language will re-read from disk.
    Called by POWatcher after a successful index rebuild.
    """
    with _lock:
        _cache.pop(lang, None)


def prewarm(
    build_dir: Path,
    lang: str,
    index_filename: str = SEARCH_INDEX_FILENAME,
    html_builder_name: str = HTML_BUILDER_NAME,
    default_language: str = DEFAULT_LANGUAGE,
) -> None:
    """Load the index into cache before the first request arrives.

    Intended to be called in a background daemon thread at server startup.
    """
    idx = load_index_for(build_dir, lang, index_filename, html_builder_name, default_language)
    if idx:
        debug_log(
            "Search index pre-warmed: lang=%s records=%d batches=%d",
            lang, len(idx.records), len(idx.batches),
        )
    else:
        debug_log("Search index not found for lang=%s (run make search-index)", lang)
