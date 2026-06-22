"""Debug logging utilities for Blender manual tools.

Ported from blender-git/find-replace/src/common/debug_log.py.
Changes from the original:
  - EMPTY_STRING constant replaced with literal ""
  - blender_git_config YAML loader removed; debug settings are read
    from tools/config/logging_config.ini ([debug] section) instead.
  - REPO_ROOT resolved relative to this file (tools/ → project root).

Enable debug output by setting the DEBUG environment variable:

    DEBUG=true python3 tools/serve_docs.py
    DEBUG=1 DEBUG_LEVEL=DEBUG make serve

Configuration file: tools/config/logging_config.ini
"""

from __future__ import annotations

import configparser
import logging
import logging.config
import logging.handlers
import multiprocessing
import os
import pickle
import queue as _queue
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from common.log_rotation import (
    cleanup_log,
    parse_timestamp,
    prepare_log_for_startup,
    record_delimiter,
    split_records,
)
from common.log_rotation_config import RotationSettings, load_rotation_settings
from common.log_rotation_handler import TrimAwareFileHandler

# Project root is two levels up from this file: tools/debug_log.py → project/
REPO_ROOT = Path(__file__).resolve().parents[1]
# Config lives alongside the tools that consume it: tools/config/logging_config.ini
DEFAULT_LOG_CONFIG = Path(__file__).resolve().parent / "config" / "logging_config.ini"

MAIN_PROCESS_NAME = "MainProcess"
LOG_CONTROL_SECTION = "log_control"
LOG_CONTROL_ENABLED_KEY = "enabled"
PROJECT_ROOT_CONFIG_KEY = "project_root"
LISTENER_PROCESS_NAME = "debug-log-listener"
LISTENER_JOIN_TIMEOUT_SECONDS = 5
MULTIPROCESSING_START_METHOD = "spawn"
TRUTHY_VALUES = frozenset({"true", "1", "yes", "on"})
BASIC_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
PYTEST_DEBUG_LOG_ENV = "PYTEST_DEBUG_LOG"
DEBUG_MESSAGE_FORMAT = "[DEBUG] %s"


# ---------------------------------------------------------------------------
# Debug mode detection
# ---------------------------------------------------------------------------

def _running_under_pytest() -> bool:
    """Heuristic to detect pytest execution without importing pytest."""
    if os.getenv("PYTEST_CURRENT_TEST"):
        return True
    return "pytest" in " ".join(sys.argv).lower()


def _load_debug_settings_from_config() -> None:
    """Load DEBUG and DEBUG_LEVEL from tools/config/logging_config.ini [debug] section.

    Only reads the file when the environment variables are not already set.
    Silently ignored if the file is absent or malformed.
    """
    if _running_under_pytest():
        return
    try:
        cfg = configparser.ConfigParser()
        cfg.read(str(DEFAULT_LOG_CONFIG))
        if not cfg.has_section("debug"):
            return
        if "DEBUG" not in os.environ:
            raw = cfg.get("debug", "enabled", fallback="false").lower()
            if raw in ("true", "1", "yes", "on"):
                os.environ["DEBUG"] = "true"
            else:
                os.environ["DEBUG"] = "false"
        if "DEBUG_LEVEL" not in os.environ:
            level = cfg.get("debug", "level", fallback="DEBUG").upper()
            os.environ["DEBUG_LEVEL"] = level
    except (OSError, ValueError, configparser.Error):
        pass


# Run once at import time
_load_debug_settings_from_config()


def is_debug_mode() -> bool:
    """Return True when the DEBUG environment variable enables verbose logging."""
    return os.getenv("DEBUG", "").lower() in TRUTHY_VALUES


def get_debug_level() -> str:
    """Return the configured debug level string (e.g. 'DEBUG', 'INFO')."""
    if is_debug_mode():
        return os.getenv("DEBUG_LEVEL", "DEBUG").upper()
    return "INFO"


# ``fileConfig`` resolves handler classes in the logging module namespace.
logging.TrimAwareFileHandler = TrimAwareFileHandler  # type: ignore[attr-defined]

_TRIM_SENTINEL = "__TRIM_LOG__"
_TRIM_COMMAND_LENGTH = 6
_STARTUP_PREPARED_CONFIGS: set[Path] = set()


def _find_trim_handler() -> Optional[TrimAwareFileHandler]:
    """Return the root logger's single-file trim handler, if configured."""
    for handler in logging.getLogger().handlers:
        if isinstance(handler, TrimAwareFileHandler):
            return handler
    return None


def _rotation_settings(path: Path | str) -> RotationSettings:
    return load_rotation_settings(path, REPO_ROOT)


def _prepare_startup_log(config_path: Path) -> None:
    is_main_process = multiprocessing.current_process().name == MAIN_PROCESS_NAME
    should_prepare = (
        is_main_process
        and not _running_under_pytest()
        and config_path not in _STARTUP_PREPARED_CONFIGS
    )
    if not should_prepare:
        return
    try:
        prepare_log_for_startup(_rotation_settings(config_path))
    except (OSError, ValueError, configparser.Error) as exc:
        logging.getLogger(__name__).warning(
            "[log_rotation] startup cleanup skipped: %s", exc,
        )
    finally:
        _STARTUP_PREPARED_CONFIGS.add(config_path)


def log_check_interval_seconds(path: Path | str = DEFAULT_LOG_CONFIG) -> float:
    """Return the configured watcher throttle, or zero when disabled."""
    settings = _rotation_settings(path)
    return settings.check_interval_seconds if settings.enabled else 0.0


def _log_exceeds_limit(settings: RotationSettings) -> bool:
    try:
        return settings.log_path.stat().st_size > settings.max_size_bytes
    except FileNotFoundError:
        return False


def _trim_command(settings: RotationSettings) -> tuple[object, ...]:
    return (
        _TRIM_SENTINEL,
        str(settings.log_path),
        settings.max_size_bytes,
        settings.retention_seconds,
        settings.min_size_bytes,
        settings.record_marker,
    )


def _cleanup_without_open_handler(settings: RotationSettings) -> bool:
    return cleanup_log(
        settings.log_path,
        max_size_bytes=settings.max_size_bytes,
        retention_seconds=settings.retention_seconds,
        min_size_bytes=settings.min_size_bytes,
        temp_file=settings.temp_file,
        record_marker=settings.record_marker,
    )


def maybe_trim_live_log(path: Path | str = DEFAULT_LOG_CONFIG) -> bool:
    """Dispatch one safe live trim when the configured limit is exceeded."""
    try:
        settings = _rotation_settings(path)
        should_trim = settings.enabled and _log_exceeds_limit(settings)
        if not should_trim:
            return False
        uses_listener = multiprocessing_logging_enabled()
        if uses_listener and LOG_STATE.log_queue is not None:
            LOG_STATE.log_queue.put(_trim_command(settings))
            return True
        handler = _find_trim_handler()
        if handler is not None:
            return handler.trim_in_place(settings)
        return _cleanup_without_open_handler(settings)
    except (OSError, ValueError, configparser.Error) as exc:
        logging.getLogger(__name__).warning(
            "[log_rotation] live cleanup skipped: %s", exc,
        )
        return False


def _is_trim_command(item: object) -> bool:
    is_command_tuple = isinstance(item, tuple) and len(item) == _TRIM_COMMAND_LENGTH
    return bool(is_command_tuple and item[0] == _TRIM_SENTINEL)


def _run_trim_command(command: tuple[object, ...]) -> None:
    _, log_path, max_bytes, retention_seconds, min_bytes, marker = command
    cleanup_log(
        Path(str(log_path)),
        max_size_bytes=int(max_bytes),
        retention_seconds=float(retention_seconds),
        min_size_bytes=int(min_bytes),
        in_place=True,
        record_marker=str(marker),
    )


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def _suppress_noisy_library_loggers() -> None:
    """Keep third-party transport loggers from spamming routine requests."""
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def _resolve_config_path(path: Path | str) -> Path:
    config_path = Path(path)
    if config_path.is_absolute():
        return config_path
    return (REPO_ROOT / config_path).resolve()


def _apply_record_marker(settings: RotationSettings) -> None:
    handler = _find_trim_handler()
    has_record_marker = settings.enabled and bool(settings.record_marker)
    if handler is not None and has_record_marker:
        handler.terminator = record_delimiter(settings.record_marker)


def _apply_debug_level() -> None:
    if not is_debug_mode():
        return
    level_value = logging.getLevelName(get_debug_level())
    if not isinstance(level_value, int):
        return
    root = logging.getLogger()
    root.setLevel(level_value)
    for handler in root.handlers:
        handler.setLevel(level_value)


def _configure_from_file(config_path: Path) -> None:
    logging.config.fileConfig(
        str(config_path),
        defaults={PROJECT_ROOT_CONFIG_KEY: str(REPO_ROOT)},
    )
    _apply_record_marker(_rotation_settings(config_path))
    _suppress_noisy_library_loggers()
    _apply_debug_level()


def setup_logging_from_config(path: Path | str = DEFAULT_LOG_CONFIG) -> logging.Logger:
    """Configure the root logger from an INI file, with debug-mode overrides.

    Falls back to basicConfig when the INI file is absent.
    """
    config_path = _resolve_config_path(path)
    if _running_under_pytest():
        return logging.getLogger(__name__)
    if not config_path.exists():
        level = logging.DEBUG if is_debug_mode() else logging.INFO
        logging.basicConfig(level=level, format=BASIC_LOG_FORMAT)
        return logging.getLogger(__name__)
    config = configparser.ConfigParser()
    config.read(str(config_path))
    is_enabled = config.getboolean(
        LOG_CONTROL_SECTION,
        LOG_CONTROL_ENABLED_KEY,
        fallback=True,
    )
    if not is_enabled:
        logging.disable(logging.CRITICAL)
        return logging.getLogger(__name__)
    logging.disable(logging.NOTSET)
    _prepare_startup_log(config_path)
    _configure_from_file(config_path)
    return logging.getLogger(__name__)


def _initial_logger() -> logging.Logger:
    """Configure file logging only in the original application process."""
    is_main_process = multiprocessing.current_process().name == MAIN_PROCESS_NAME
    if is_main_process and not _running_under_pytest():
        return setup_logging_from_config()
    return logging.getLogger(__name__)


logger: logging.Logger = _initial_logger()


# ---------------------------------------------------------------------------
# Multiprocessing log state
# ---------------------------------------------------------------------------

@dataclass
class _LogState:
    log_queue: Optional[multiprocessing.Queue] = None  # type: ignore[type-arg]
    log_listener_process: Optional[multiprocessing.Process] = None
    queue_handler: Optional[logging.handlers.QueueHandler] = None
    is_multiprocessing: bool = False


LOG_STATE = _LogState()

# Module-level aliases kept in sync with LOG_STATE
log_queue: Optional[multiprocessing.Queue] = None  # type: ignore[type-arg]
log_listener_process: Optional[multiprocessing.Process] = None
is_multiprocessing = False


def _sync_log_state() -> None:
    globals()["log_queue"] = LOG_STATE.log_queue
    globals()["log_listener_process"] = LOG_STATE.log_listener_process
    globals()["is_multiprocessing"] = LOG_STATE.is_multiprocessing


def _callable_name(value: object) -> str:
    module_name = getattr(value, "__module__", type(value).__module__)
    qualified_name = getattr(value, "__qualname__", type(value).__qualname__)
    return f"{module_name}.{qualified_name}"


def _payload_type_names(values: tuple[object, ...]) -> str:
    if not values:
        return "none"
    return ", ".join(type(v).__name__ for v in values)


def _pickling_preflight_error(
    target: object,
    args: tuple[object, ...],
    kwargs: Optional[dict[str, object]],
) -> str | None:
    try:
        pickle.dumps((target, args, kwargs or {}))
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"
    return None


def log_process_spawn_request(
    process_name: str,
    *,
    target: object,
    args: tuple[object, ...] = (),
    kwargs: Optional[dict[str, object]] = None,
) -> None:
    """Log a multiprocessing spawn request with pickling preflight info."""
    target_name = _callable_name(target)
    argument_types = _payload_type_names(args)
    keyword_names = ", ".join(sorted((kwargs or {}).keys())) or "none"
    pickling_error = _pickling_preflight_error(target, args, kwargs)
    status = "ok" if pickling_error is None else f"FAILED: {pickling_error}"
    debug_log(
        "[Multiprocessing] spawn name=%s target=%s arg_types=[%s] kwargs=[%s] pickling=%s",
        process_name, target_name, argument_types, keyword_names, status,
    )


# ---------------------------------------------------------------------------
# Multiprocessing logging lifecycle
# ---------------------------------------------------------------------------

def start_log_listener(queue: multiprocessing.Queue) -> None:  # type: ignore[type-arg]
    """Run in a listener process: drain the queue and emit records.

    A ``None`` item stops the listener; an E.2 trim sentinel runs the in-place
    trim on the listener-owned handler (serial drain → no divert needed).
    """
    setup_logging_from_config()
    file_handler = _find_trim_handler()
    while True:
        record = queue.get()
        if record is None:
            break
        if _is_trim_command(record):
            _run_trim_command(record)  # type: ignore[arg-type]
            continue
        if file_handler is not None:
            file_handler.handle(record)


def _remove_queue_handler() -> None:
    handler = LOG_STATE.queue_handler
    if handler is None:
        return
    logging.getLogger().removeHandler(handler)
    handler.close()
    LOG_STATE.queue_handler = None


def _route_file_logs_to_queue(queue: multiprocessing.Queue) -> None:  # type: ignore[type-arg]
    """Make the listener the only process that owns the log file."""
    root = logging.getLogger()
    for handler in list(root.handlers):
        if isinstance(handler, TrimAwareFileHandler):
            root.removeHandler(handler)
            handler.close()
    _remove_queue_handler()
    queue_handler = logging.handlers.QueueHandler(queue)
    queue_handler.setLevel(logging.DEBUG)
    root.addHandler(queue_handler)
    if is_debug_mode():
        root.setLevel(logging.getLevelName(get_debug_level()))
    LOG_STATE.queue_handler = queue_handler


def _resolve_log_queue(
    requested_queue: Optional[multiprocessing.Queue],  # type: ignore[type-arg]
) -> multiprocessing.Queue:  # type: ignore[type-arg]
    if requested_queue is not None:
        return requested_queue
    if LOG_STATE.log_queue is not None:
        return LOG_STATE.log_queue
    context = multiprocessing.get_context(MULTIPROCESSING_START_METHOD)
    return context.Queue()


def _listener_needs_start() -> bool:
    listener = LOG_STATE.log_listener_process
    return listener is None or not listener.is_alive()


def _start_listener_process(queue: multiprocessing.Queue) -> None:  # type: ignore[type-arg]
    log_process_spawn_request(
        LISTENER_PROCESS_NAME,
        target=start_log_listener,
        args=(queue,),
    )
    context = multiprocessing.get_context(MULTIPROCESSING_START_METHOD)
    listener = context.Process(
        name=LISTENER_PROCESS_NAME,
        target=start_log_listener,
        args=(queue,),
        daemon=True,
    )
    listener.start()
    LOG_STATE.log_listener_process = listener
    debug_log(
        "[Multiprocessing] started name=%s pid=%s",
        LISTENER_PROCESS_NAME,
        listener.pid,
    )


def enable_multiprocessing_logging(
    queue: Optional[multiprocessing.Queue] = None,  # type: ignore[type-arg]
    start_listener: bool = True,
) -> Optional[multiprocessing.Queue]:  # type: ignore[type-arg]
    """Activate multiprocessing logging and return the queue in use."""
    resolved_queue = _resolve_log_queue(queue)
    LOG_STATE.log_queue = resolved_queue
    if start_listener and _listener_needs_start():
        _start_listener_process(resolved_queue)
    LOG_STATE.is_multiprocessing = True
    _route_file_logs_to_queue(resolved_queue)
    _sync_log_state()
    return resolved_queue


def attach_worker_log_queue(
    queue: Optional[multiprocessing.Queue],  # type: ignore[type-arg]
) -> None:
    """Call inside worker processes to attach an existing queue without spawning."""
    LOG_STATE.log_queue = queue
    LOG_STATE.is_multiprocessing = queue is not None
    if queue is not None:
        _route_file_logs_to_queue(queue)
    else:
        _remove_queue_handler()
    _sync_log_state()


def disable_multiprocessing_logging() -> None:
    """Tear down the logging listener and queue safely."""
    if LOG_STATE.log_queue is not None:
        try:
            LOG_STATE.log_queue.put_nowait(None)
        except (_queue.Full, OSError):
            pass

    if LOG_STATE.log_listener_process is not None:
        LOG_STATE.log_listener_process.join(timeout=LISTENER_JOIN_TIMEOUT_SECONDS)
        LOG_STATE.log_listener_process = None

    _remove_queue_handler()
    LOG_STATE.log_queue = None
    LOG_STATE.is_multiprocessing = False
    _sync_log_state()
    is_main_process = multiprocessing.current_process().name == MAIN_PROCESS_NAME
    if is_main_process:
        setup_logging_from_config()


def multiprocessing_logging_enabled() -> bool:
    return bool(LOG_STATE.is_multiprocessing and LOG_STATE.log_queue is not None)


# ---------------------------------------------------------------------------
# Core debug_log function
# ---------------------------------------------------------------------------

def _debug_logging_should_skip() -> bool:
    pytest_logging_enabled = (
        os.getenv(PYTEST_DEBUG_LOG_ENV, "").lower() in TRUTHY_VALUES
    )
    is_test_suppressed = _running_under_pytest() and not pytest_logging_enabled
    has_debug_level = (
        logger.isEnabledFor(logging.DEBUG)
        or logging.getLogger().isEnabledFor(logging.DEBUG)
    )
    return is_test_suppressed or not is_debug_mode() or not has_debug_level


def _format_debug_message(message: str, args: tuple[object, ...]) -> str:
    if not args:
        return message
    try:
        return message % args
    except (TypeError, ValueError) as exc:
        return f"{message} (format error: {exc}, args: {args})"


def debug_log(message: str, *args: object, **_kwargs: object) -> None:
    """Emit a DEBUG-level log message when DEBUG mode is active.

    Supports both printf-style and f-string usage:

        debug_log("Starting server on port %s", port)
        debug_log(f"Lang dirs: {lang_dirs}")

    In multiprocessing mode the record is routed through the shared queue.
    In thread-pool mode (serve_docs.py) it logs directly from the thread.
    Each message is prefixed with [PID:xxx|process-name] for easy tracing.
    """
    if _debug_logging_should_skip():
        return
    process = multiprocessing.current_process()
    formatted = _format_debug_message(message, args)
    enhanced = f"[PID:{os.getpid()}|{process.name}] {formatted}"
    logger.debug(DEBUG_MESSAGE_FORMAT, enhanced, stacklevel=2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "attach_worker_log_queue",
    "cleanup_log",
    "debug_log",
    "disable_multiprocessing_logging",
    "enable_multiprocessing_logging",
    "get_debug_level",
    "is_debug_mode",
    "log_check_interval_seconds",
    "log_listener_process",
    "log_process_spawn_request",
    "log_queue",
    "logger",
    "maybe_trim_live_log",
    "multiprocessing_logging_enabled",
    "parse_timestamp",
    "record_delimiter",
    "setup_logging_from_config",
    "split_records",
    "start_log_listener",
    "TrimAwareFileHandler",
    "LOG_STATE",
]
