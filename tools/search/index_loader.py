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

from .searchable_record import SearchableRecord
from common.constants import (  # type: ignore[import-not-found]
    DEFAULT_LANGUAGE,
    HTML_BUILDER_NAME,
    SEARCH_INDEX_FILENAME,
)

# debug_log lives next to this file in tools/; fall back silently if absent.
try:
    from debug_log import debug_log  # type: ignore[import-not-found]
except ImportError:
    import logging as _logging
    def debug_log(message: str, *args: object, **_kw: object) -> None:  # type: ignore[misc]
        if os.getenv("DEBUG", "").lower() in {"true", "1", "yes", "on"}:
            _logging.debug(message, *args)


@dataclass
class LoadedIndex:
    """Loaded index with records and pre-partitioned worker batches."""
    records: list[SearchableRecord]
    batches: list[list[SearchableRecord]]   # pre-split for Pool workers
    lang: str
    pkl_path: Path


_cache: dict[str, LoadedIndex] = {}
_lock = threading.Lock()


def _n_workers() -> int:
    return max(1, (os.cpu_count() or 2) - 2)


def _make_batches(
    records: list[SearchableRecord],
    n: int,
) -> list[list[SearchableRecord]]:
    """Split records into *n* batches; last batch absorbs the remainder."""
    if n <= 1 or not records:
        return [records]
    bs = max(1, len(records) // n)
    batches = [records[i * bs : (i + 1) * bs] for i in range(n - 1)]
    batches.append(records[(n - 1) * bs :])
    return [b for b in batches if b]


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
    if dedicated.exists():
        return dedicated
    if lang == default_language and fallback.exists():
        return fallback
    return dedicated   # caller handles FileNotFoundError


def load_index(pkl_path: Path, lang: str) -> LoadedIndex:
    """Load and cache the search index for *lang*.

    Thread-safe: if two requests race for the same language, the second
    blocks until the first load completes, then reads from cache.
    Pre-partitions batches at load time so no slicing is needed at query time.
    """
    if lang in _cache:
        return _cache[lang]
    with _lock:
        if lang not in _cache:
            with gzip.open(pkl_path, "rb") as fh:
                records: list[SearchableRecord] = pickle.load(fh)
            n = _n_workers()
            _cache[lang] = LoadedIndex(
                records=records,
                batches=_make_batches(records, n),
                lang=lang,
                pkl_path=pkl_path,
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
    if not pkl_path.exists():
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
    import logging
    idx = load_index_for(build_dir, lang, index_filename, html_builder_name, default_language)
    if idx:
        debug_log(
            "Search index pre-warmed: lang=%s records=%d batches=%d",
            lang, len(idx.records), len(idx.batches),
        )
    else:
        logging.warning("Search index not found for lang=%s (run make search-index)", lang)
