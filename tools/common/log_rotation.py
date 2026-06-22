"""Single-file retention policy for ``application.log``.

The module owns record grouping, startup recovery, and the two rewrite modes.
It has no dependency on the project's logging setup, so the retention rules
remain directly unit-testable.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from common.log_rotation_config import (
    BYTES_PER_MEBIBYTE,
    DEFAULT_CHECK_INTERVAL_SECONDS,
    DEFAULT_RECORD_MARKER,
    REWRITE_STAGE_SUFFIX,
    TEMP_FILE_SUFFIX,
    RotationSettings,
    validate_rotation_settings,
)

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
TIMESTAMP_LENGTH = 19
UTF8_ENCODING = "utf-8"
REPLACE_ENCODING_ERRORS = "replace"
TEXT_WRITE_MODE = "w"
BINARY_READ_WRITE_MODE = "r+b"
BINARY_READ_MODE = "rb"
BINARY_APPEND_MODE = "ab"

_Record = tuple[Optional[datetime], str]


def parse_timestamp(line: str) -> Optional[datetime]:
    """Parse a formatter timestamp at the start of *line*."""
    try:
        return datetime.strptime(line[:TIMESTAMP_LENGTH], TIMESTAMP_FORMAT)
    except (ValueError, IndexError):
        return None


def record_delimiter(marker: str) -> str:
    """Return the optional whole-record delimiter used by a file handler."""
    return f"\n{marker}\n" if marker else "\n"


def _group_by_timestamp(content: str) -> list[_Record]:
    records: list[_Record] = []
    current_timestamp: Optional[datetime] = None
    current_lines: list[str] = []
    for line in content.splitlines(keepends=True):
        timestamp = parse_timestamp(line)
        if timestamp is not None:
            if current_lines:
                records.append((current_timestamp, "".join(current_lines)))
            current_timestamp = timestamp
            current_lines = [line]
        else:
            current_lines.append(line)
    if current_lines:
        records.append((current_timestamp, "".join(current_lines)))
    return records


def _split_marked_content(content: str, delimiter: str) -> list[_Record]:
    records: list[_Record] = []
    for chunk in content.split(delimiter):
        grouped = _group_by_timestamp(chunk)
        if not grouped:
            continue
        timestamp, text = grouped[-1]
        grouped[-1] = (timestamp, text + delimiter)
        records.extend(grouped)
    return records


def split_records(content: str, marker: str = DEFAULT_RECORD_MARKER) -> list[_Record]:
    """Group continuations with their timestamped log record."""
    delimiter = record_delimiter(marker)
    has_markers = bool(marker) and delimiter in content
    if has_markers:
        return _split_marked_content(content, delimiter)
    return _group_by_timestamp(content)


def _record_size(record: _Record) -> int:
    return len(record[1].encode(UTF8_ENCODING))


def _recent_records(records: list[_Record], cutoff: datetime) -> list[_Record]:
    return [record for record in records if record[0] is not None and record[0] >= cutoff]


def _newest_records_within(records: list[_Record], limit: int) -> list[_Record]:
    newest_first: list[_Record] = []
    total = 0
    for record in reversed(records):
        record_size = _record_size(record)
        would_exceed_limit = total + record_size > limit
        if newest_first and would_exceed_limit:
            break
        newest_first.append(record)
        total += record_size
    return list(reversed(newest_first))


def _retained_text(
    content: str,
    settings: RotationSettings,
    now: datetime,
) -> str:
    records = split_records(content, settings.record_marker)
    cutoff = now - timedelta(seconds=settings.retention_seconds)
    retained = _recent_records(records, cutoff)
    retained_size = sum(_record_size(record) for record in retained)
    if retained_size > settings.max_size_bytes:
        retained = _newest_records_within(retained, settings.min_size_bytes)
    return "".join(text for _, text in retained)


def _write_via_replace(path: Path, text: str, temp_file: Path) -> None:
    rewrite_stage = Path(f"{temp_file}{REWRITE_STAGE_SUFFIX}")
    with rewrite_stage.open(TEXT_WRITE_MODE, encoding=UTF8_ENCODING) as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(rewrite_stage, path)


def _write_in_place(path: Path, text: str) -> None:
    data = text.encode(UTF8_ENCODING)
    with path.open(BINARY_READ_WRITE_MODE) as handle:
        handle.seek(0)
        handle.write(data)
        handle.truncate(len(data))
        handle.flush()
        os.fsync(handle.fileno())


def _settings_for_cleanup(
    path: Path,
    max_size_bytes: int,
    retention_seconds: float,
    min_size_bytes: int,
    temp_file: Path | str | None,
    record_marker: str,
) -> RotationSettings:
    settings = RotationSettings(
        enabled=True,
        max_size_bytes=max_size_bytes,
        retention_seconds=retention_seconds,
        min_size_bytes=min_size_bytes,
        log_path=path,
        temp_file=Path(temp_file or f"{path}{TEMP_FILE_SUFFIX}"),
        check_interval_seconds=DEFAULT_CHECK_INTERVAL_SECONDS,
        record_marker=record_marker,
    )
    return validate_rotation_settings(settings)


def _rewrite_log(
    path: Path,
    retained: str,
    settings: RotationSettings,
    in_place: bool,
) -> None:
    if in_place:
        _write_in_place(path, retained)
        return
    _write_via_replace(path, retained, settings.temp_file)


def _is_over_limit(path: Path, max_size_bytes: int) -> bool:
    try:
        return path.stat().st_size > max_size_bytes
    except FileNotFoundError:
        return False


def cleanup_log(
    log_path: Path | str,
    *,
    max_size_bytes: int,
    retention_seconds: float,
    min_size_bytes: int,
    temp_file: Path | str | None = None,
    in_place: bool = False,
    record_marker: str = DEFAULT_RECORD_MARKER,
    now: Optional[datetime] = None,
) -> bool:
    """Trim an oversized log while retaining recent whole records."""
    path = Path(log_path)
    if not _is_over_limit(path, max_size_bytes):
        return False
    settings = _settings_for_cleanup(
        path,
        max_size_bytes,
        retention_seconds,
        min_size_bytes,
        temp_file,
        record_marker,
    )
    content = path.read_text(
        encoding=UTF8_ENCODING,
        errors=REPLACE_ENCODING_ERRORS,
    )
    retained = _retained_text(content, settings, now or datetime.now())
    _rewrite_log(path, retained, settings, in_place)
    return True


def replay_temp_file(log_path: Path | str, temp_file: Path | str) -> bool:
    """Append a crash-leftover temp store, then remove it durably."""
    path = Path(log_path)
    buffered = Path(temp_file)
    if not buffered.is_file():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with buffered.open(BINARY_READ_MODE) as source, path.open(BINARY_APPEND_MODE) as target:
        while chunk := source.read(BYTES_PER_MEBIBYTE):
            target.write(chunk)
        target.flush()
        os.fsync(target.fileno())
    buffered.unlink()
    return True


def _discard_incomplete_rewrite(temp_file: Path) -> None:
    rewrite_stage = Path(f"{temp_file}{REWRITE_STAGE_SUFFIX}")
    rewrite_stage.unlink(missing_ok=True)


def prepare_log_for_startup(
    settings: RotationSettings,
    *,
    now: Optional[datetime] = None,
) -> bool:
    """Replay interrupted writes and atomically trim before a handler opens."""
    if not settings.enabled:
        return False
    _discard_incomplete_rewrite(settings.temp_file)
    replay_temp_file(settings.log_path, settings.temp_file)
    return cleanup_log(
        settings.log_path,
        max_size_bytes=settings.max_size_bytes,
        retention_seconds=settings.retention_seconds,
        min_size_bytes=settings.min_size_bytes,
        temp_file=settings.temp_file,
        record_marker=settings.record_marker,
        now=now,
    )
