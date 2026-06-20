"""FIFO watcher that keeps application.log within a size limit.

Launched as a background daemon thread by serve_docs.py when
``log_trim_enabled = True`` is set in manual/conf.py (default: True).

Behaviour
---------
- Polls the log file size every *poll_interval* seconds (default: 60 s).
- When the file exceeds *max_size_bytes*, discards the oldest ~50 % of
  the content (FIFO: first written, first discarded).
- A single dated trim-marker line is written at the start of the retained
  content so it is immediately obvious that trimming occurred.
- Writes are atomic: content goes to a ``.tmp`` sibling first, then the
  sibling is renamed over the original so no partial line is ever visible.

Usage::

    from common.log_trimmer import ApplicationLogTrimmer

    trimmer = ApplicationLogTrimmer(
        log_path=Path("application.log"),
        max_size_bytes=10 * 1024 * 1024,   # 10 MB
    )
    trimmer.start()       # starts daemon thread; non-blocking
    # … server runs …
    trimmer.stop()        # optional — thread exits anyway when the process does
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path

_TRIM_MARKER_FMT = (
    "[LOG TRIMMED at {ts} — oldest entries removed; "
    "keeping most-recent content below {mb:d} MB limit]\n"
)


class ApplicationLogTrimmer:
    """Background daemon thread that keeps *log_path* within *max_size_bytes*.

    FIFO eviction: when the file exceeds the limit the oldest roughly half of
    the byte content is removed.  A dated marker line replaces the removed
    block so the gap in history is visible.

    Parameters
    ----------
    log_path       : path to the log file to watch (must be writable)
    max_size_bytes : file size threshold that triggers a trim
    poll_interval  : seconds between size checks (default: 60)
    """

    def __init__(
        self,
        log_path: Path,
        max_size_bytes: int,
        poll_interval: float = 60.0,
    ) -> None:
        self.log_path = log_path
        self.max_size_bytes = max_size_bytes
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    # ------------------------------------------------------------------
    # Lifecycle

    def start(self) -> None:
        """Start the background watcher thread (idempotent)."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._watch_loop,
            name="log-trimmer",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the watcher to stop and wait up to 5 s for it to exit."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    # ------------------------------------------------------------------
    # Internal

    def _watch_loop(self) -> None:
        while not self._stop_event.wait(timeout=self.poll_interval):
            try:
                self._maybe_trim()
            except Exception:
                pass

    def _maybe_trim(self) -> None:
        """Trim the log file if it exceeds the size limit."""
        if not self.log_path.exists():
            return
        if self.log_path.stat().st_size <= self.max_size_bytes:
            return

        content = self.log_path.read_bytes()

        # Find a newline boundary at or after the midpoint so we never cut
        # a log entry in half (Python's standard formatter ends every record
        # with a newline).
        mid = len(content) // 2
        nl = content.find(b"\n", mid)
        keep_from = (nl + 1) if nl != -1 else mid

        ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        mb = self.max_size_bytes // (1024 * 1024)
        marker = _TRIM_MARKER_FMT.format(ts=ts, mb=mb).encode()
        trimmed = marker + content[keep_from:]

        # Atomic write: write to .tmp then rename so no reader sees a partial file.
        tmp = self.log_path.with_suffix(".tmp")
        tmp.write_bytes(trimmed)
        tmp.replace(self.log_path)
