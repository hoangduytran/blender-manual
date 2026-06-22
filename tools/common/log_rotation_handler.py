"""Open-file-safe handler for live ``application.log`` trimming."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TextIO

from common.log_rotation import cleanup_log, replay_temp_file
from common.log_rotation_config import RotationSettings

APPEND_MODE = "a"
UTF8_ENCODING = "utf-8"


class TrimAwareFileHandler(logging.FileHandler):
    """Divert records while preserving the inode of a live log file."""

    def __init__(self, filename, mode=APPEND_MODE, encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)
        self._divert_path: Path | None = None
        self._divert_stream: TextIO | None = None

    def emit(self, record: logging.LogRecord) -> None:
        """Write to the crash-durable buffer while a trim is active."""
        if self._divert_path is None:
            super().emit(record)
            return
        try:
            stream = self._open_divert_stream()
            stream.write(self.format(record) + self.terminator)
            stream.flush()
            os.fsync(stream.fileno())
        except Exception:
            self.handleError(record)

    def _open_divert_stream(self) -> TextIO:
        if self._divert_stream is None:
            self._divert_stream = self._divert_path.open(
                APPEND_MODE, encoding=self.encoding or UTF8_ENCODING,
            )
        return self._divert_stream

    def _begin_diversion(self, temp_file: Path) -> None:
        self.acquire()
        try:
            if self.stream is not None:
                self.stream.flush()
            replay_temp_file(self.baseFilename, temp_file)
            self._divert_path = temp_file
        finally:
            self.release()

    def _finish_diversion(self, temp_file: Path) -> None:
        self.acquire()
        try:
            if self._divert_stream is not None:
                self._divert_stream.close()
                self._divert_stream = None
            replay_temp_file(self.baseFilename, temp_file)
            self._divert_path = None
        finally:
            self.release()

    def trim_in_place(self, settings: RotationSettings) -> bool:
        """Copytruncate under diversion, then replay every concurrent record."""
        self._begin_diversion(settings.temp_file)
        try:
            return cleanup_log(
                self.baseFilename,
                max_size_bytes=settings.max_size_bytes,
                retention_seconds=settings.retention_seconds,
                min_size_bytes=settings.min_size_bytes,
                in_place=True,
                record_marker=settings.record_marker,
            )
        finally:
            self._finish_diversion(settings.temp_file)
