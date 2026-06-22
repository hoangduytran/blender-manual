"""Behavioral tests for single-file ``application.log`` retention."""

from __future__ import annotations

import logging
import sys
import threading
from datetime import datetime
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from common import log_rotation_handler  # noqa: E402
from common.log_rotation import (  # noqa: E402
    cleanup_log,
    prepare_log_for_startup,
)
from common.log_rotation_config import (  # noqa: E402
    BYTES_PER_KIBIBYTE,
    REWRITE_STAGE_SUFFIX,
    RotationSettings,
    load_rotation_settings,
)
from common.log_rotation_handler import TrimAwareFileHandler  # noqa: E402
import debug_log  # noqa: E402
from search import po_watcher  # noqa: E402

LOG_FILENAME = "application.log"
TEMP_FILENAME = "application.log.tmp"
UTF8_ENCODING = "utf-8"
FORCE_TRIM_LIMIT_BYTES = 1
EMPTY_CLEANUP_FLOOR_BYTES = 0
SECONDS_PER_DAY = 24 * 60 * 60
STAGE_TWO_LIMIT_BYTES = 250
STAGE_TWO_FLOOR_BYTES = 150
LARGE_LIMIT_BYTES = 1024 * 1024
PAYLOAD_WIDTH = 80
STAGE_TWO_RECORD_COUNT = 4
THREAD_TIMEOUT_SECONDS = 5
WATCHER_INTERVAL_SECONDS = 300.0
INITIAL_WATCHER_DEADLINE = 0.0
SHIPPED_MAX_SIZE_KB = 200
SHIPPED_MIN_SIZE_KB = 100
SHIPPED_CHECK_INTERVAL_SECONDS = 5.0
FIRST_CHECK_TIME = 100.0
THROTTLED_CHECK_TIME = 200.0
SECOND_DUE_CHECK_TIME = 400.0

NOW = datetime(2026, 6, 22, 12, 0, 0)
OLD_TIMESTAMP = datetime(2026, 6, 20, 12, 0, 0)
RECENT_TIMESTAMP = datetime(2026, 6, 22, 11, 0, 0)
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _record(timestamp: datetime, message: str, continuation: str = "") -> str:
    text = f"{timestamp:{DATE_FORMAT}} - INFO - test - {message}\n"
    return text + continuation


def _settings(
    log_path: Path,
    *,
    enabled: bool = True,
    max_size_bytes: int = FORCE_TRIM_LIMIT_BYTES,
    min_size_bytes: int = EMPTY_CLEANUP_FLOOR_BYTES,
) -> RotationSettings:
    return RotationSettings(
        enabled=enabled,
        max_size_bytes=max_size_bytes,
        retention_seconds=SECONDS_PER_DAY,
        min_size_bytes=min_size_bytes,
        log_path=log_path,
        temp_file=log_path.with_name(TEMP_FILENAME),
        check_interval_seconds=WATCHER_INTERVAL_SECONDS,
    )


def _cleanup(
    path: Path,
    *,
    max_size_bytes: int = FORCE_TRIM_LIMIT_BYTES,
    retention_seconds: float = SECONDS_PER_DAY,
    min_size_bytes: int = EMPTY_CLEANUP_FLOOR_BYTES,
    in_place: bool = False,
) -> bool:
    return cleanup_log(
        path,
        max_size_bytes=max_size_bytes,
        retention_seconds=retention_seconds,
        min_size_bytes=min_size_bytes,
        in_place=in_place,
        now=NOW,
    )


def test_under_size_leaves_file_byte_for_byte_untouched(tmp_path: Path) -> None:
    log_path = tmp_path / LOG_FILENAME
    content = _record(RECENT_TIMESTAMP, "under limit")
    log_path.write_text(content, encoding=UTF8_ENCODING)

    trimmed = _cleanup(log_path, max_size_bytes=len(content.encode(UTF8_ENCODING)))

    assert not trimmed
    assert log_path.read_text(encoding=UTF8_ENCODING) == content


def test_age_cleanup_drops_old_records_and_keeps_recent_records(tmp_path: Path) -> None:
    log_path = tmp_path / LOG_FILENAME
    old_record = _record(OLD_TIMESTAMP, "expired")
    recent_record = _record(RECENT_TIMESTAMP, "retained")
    log_path.write_text(old_record + recent_record, encoding=UTF8_ENCODING)

    assert _cleanup(log_path)
    assert log_path.read_text(encoding=UTF8_ENCODING) == recent_record


def test_stage_two_keeps_newest_records_within_floor(tmp_path: Path) -> None:
    log_path = tmp_path / LOG_FILENAME
    records = [
        _record(RECENT_TIMESTAMP, f"record-{index}-{'x' * PAYLOAD_WIDTH}")
        for index in range(STAGE_TWO_RECORD_COUNT)
    ]
    log_path.write_text("".join(records), encoding=UTF8_ENCODING)

    assert _cleanup(
        log_path,
        max_size_bytes=STAGE_TWO_LIMIT_BYTES,
        min_size_bytes=STAGE_TWO_FLOOR_BYTES,
    )
    retained = log_path.read_text(encoding=UTF8_ENCODING)
    assert "record-3" in retained
    assert "record-2" not in retained
    assert log_path.stat().st_size <= STAGE_TWO_FLOOR_BYTES


def test_multiline_records_are_never_split(tmp_path: Path) -> None:
    log_path = tmp_path / LOG_FILENAME
    old_block = _record(OLD_TIMESTAMP, "old error", "old traceback line\n")
    recent_block = _record(
        RECENT_TIMESTAMP,
        "recent error",
        "Traceback (most recent call last):\nrecent detail\n",
    )
    log_path.write_text(old_block + recent_block, encoding=UTF8_ENCODING)

    assert _cleanup(log_path)
    assert log_path.read_text(encoding=UTF8_ENCODING) == recent_block


def test_disabled_setting_never_trims(tmp_path: Path) -> None:
    log_path = tmp_path / LOG_FILENAME
    content = _record(OLD_TIMESTAMP, "must remain")
    log_path.write_text(content, encoding=UTF8_ENCODING)

    trimmed = prepare_log_for_startup(_settings(log_path, enabled=False), now=NOW)

    assert not trimmed
    assert log_path.read_text(encoding=UTF8_ENCODING) == content


@pytest.mark.parametrize("content", ["", "malformed\ncontinuation\n"])
def test_empty_or_malformed_file_remains_usable(tmp_path: Path, content: str) -> None:
    log_path = tmp_path / LOG_FILENAME
    log_path.write_text(content, encoding=UTF8_ENCODING)

    _cleanup(log_path)
    log_path.write_text("usable\n", encoding=UTF8_ENCODING)

    assert log_path.read_text(encoding=UTF8_ENCODING) == "usable\n"


def test_startup_cleanup_uses_temp_replace_without_leftover(tmp_path: Path) -> None:
    log_path = tmp_path / LOG_FILENAME
    temp_path = tmp_path / TEMP_FILENAME
    log_path.write_text(
        _record(OLD_TIMESTAMP, "expired") + _record(RECENT_TIMESTAMP, "retained"),
        encoding=UTF8_ENCODING,
    )

    assert prepare_log_for_startup(_settings(log_path), now=NOW)
    assert "retained" in log_path.read_text(encoding=UTF8_ENCODING)
    assert not temp_path.exists()


def test_in_place_cleanup_preserves_inode(tmp_path: Path) -> None:
    log_path = tmp_path / LOG_FILENAME
    log_path.write_text(
        _record(OLD_TIMESTAMP, "expired") + _record(RECENT_TIMESTAMP, "retained"),
        encoding=UTF8_ENCODING,
    )
    inode_before = log_path.stat().st_ino

    assert _cleanup(log_path, in_place=True)

    assert log_path.stat().st_ino == inode_before
    assert "retained" in log_path.read_text(encoding=UTF8_ENCODING)


def test_handler_replays_records_written_during_trim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    log_path = tmp_path / LOG_FILENAME
    temp_path = tmp_path / TEMP_FILENAME
    handler = TrimAwareFileHandler(log_path, encoding=UTF8_ENCODING)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger = logging.getLogger("log-rotation-concurrency-test")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(handler)
    logger.info("before trim %s", "x" * PAYLOAD_WIDTH)

    cleanup_started = threading.Event()
    allow_cleanup = threading.Event()
    original_cleanup = log_rotation_handler.cleanup_log

    def delayed_cleanup(*args: object, **kwargs: object) -> bool:
        cleanup_started.set()
        assert allow_cleanup.wait(THREAD_TIMEOUT_SECONDS)
        return original_cleanup(*args, **kwargs)

    monkeypatch.setattr(log_rotation_handler, "cleanup_log", delayed_cleanup)
    settings = _settings(log_path)
    trim_thread = threading.Thread(target=handler.trim_in_place, args=(settings,))
    trim_thread.start()
    assert cleanup_started.wait(THREAD_TIMEOUT_SECONDS)
    logger.info("written during trim")
    allow_cleanup.set()
    trim_thread.join(THREAD_TIMEOUT_SECONDS)

    logger.removeHandler(handler)
    handler.close()
    assert not trim_thread.is_alive()
    assert "written during trim" in log_path.read_text(encoding=UTF8_ENCODING)
    assert not temp_path.exists()


def test_startup_replays_crash_leftover_then_deletes_temp(tmp_path: Path) -> None:
    log_path = tmp_path / LOG_FILENAME
    temp_path = tmp_path / TEMP_FILENAME
    log_path.write_text(_record(RECENT_TIMESTAMP, "before crash"), encoding=UTF8_ENCODING)
    temp_path.write_text(_record(RECENT_TIMESTAMP, "buffered at crash"), encoding=UTF8_ENCODING)
    rewrite_stage = Path(f"{temp_path}{REWRITE_STAGE_SUFFIX}")
    rewrite_stage.write_text("incomplete rewrite", encoding=UTF8_ENCODING)
    settings = _settings(
        log_path,
        max_size_bytes=LARGE_LIMIT_BYTES,
        min_size_bytes=EMPTY_CLEANUP_FLOOR_BYTES,
    )

    assert not prepare_log_for_startup(settings, now=NOW)
    content = log_path.read_text(encoding=UTF8_ENCODING)
    assert "before crash" in content
    assert "buffered at crash" in content
    assert "incomplete rewrite" not in content
    assert not temp_path.exists()
    assert not rewrite_stage.exists()


def test_cleanup_never_creates_archived_logs(tmp_path: Path) -> None:
    log_path = tmp_path / LOG_FILENAME
    log_path.write_text(
        _record(OLD_TIMESTAMP, "expired") + _record(RECENT_TIMESTAMP, "retained"),
        encoding=UTF8_ENCODING,
    )

    assert _cleanup(log_path)

    assert sorted(path.name for path in tmp_path.iterdir()) == [LOG_FILENAME]


def test_shipped_config_uses_final_limits_and_no_record_marker() -> None:
    config_path = TOOLS_DIR / "config" / "logging_config.ini"
    settings = load_rotation_settings(config_path, REPO_ROOT)

    assert settings.max_size_bytes == SHIPPED_MAX_SIZE_KB * BYTES_PER_KIBIBYTE
    assert settings.min_size_bytes == SHIPPED_MIN_SIZE_KB * BYTES_PER_KIBIBYTE
    assert settings.check_interval_seconds == SHIPPED_CHECK_INTERVAL_SECONDS
    assert settings.record_marker == ""


def test_watcher_throttles_live_trim_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    dispatches: list[Path] = []
    check_times = iter([
        FIRST_CHECK_TIME,
        THROTTLED_CHECK_TIME,
        SECOND_DUE_CHECK_TIME,
    ])
    monkeypatch.setattr(po_watcher, "_HAS_LOG_TRIM", True)
    monkeypatch.setattr(
        po_watcher,
        "_maybe_trim_live_log",
        lambda path: dispatches.append(path),
    )
    monkeypatch.setattr(po_watcher.time, "monotonic", lambda: next(check_times))
    watcher = object.__new__(po_watcher.MultiPOWatcher)
    watcher._log_config_path = TOOLS_DIR / "config" / "logging_config.ini"
    watcher._log_check_interval = WATCHER_INTERVAL_SECONDS
    watcher._next_log_check = INITIAL_WATCHER_DEADLINE

    watcher._maybe_trim_log()
    watcher._maybe_trim_log()
    watcher._maybe_trim_log()

    assert dispatches == [watcher._log_config_path, watcher._log_config_path]


class _RecordingQueue:
    def __init__(self) -> None:
        self.items: list[object] = []

    def put(self, item: object) -> None:
        self.items.append(item)


def test_multiprocessing_trim_is_serialized_through_listener_queue(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    log_path = tmp_path / LOG_FILENAME
    log_path.write_text(_record(RECENT_TIMESTAMP, "queued trim"), encoding=UTF8_ENCODING)
    inode_before = log_path.stat().st_ino
    settings = _settings(log_path)
    queue = _RecordingQueue()
    monkeypatch.setattr(debug_log, "_rotation_settings", lambda _path: settings)
    monkeypatch.setattr(debug_log.LOG_STATE, "is_multiprocessing", True)
    monkeypatch.setattr(debug_log.LOG_STATE, "log_queue", queue)

    assert debug_log.maybe_trim_live_log()
    assert len(queue.items) == 1
    command = queue.items[0]
    assert debug_log._is_trim_command(command)
    debug_log._run_trim_command(command)

    assert log_path.stat().st_ino == inode_before
