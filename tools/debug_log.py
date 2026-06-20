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
import inspect
import logging
import logging.config
import multiprocessing
import os
import pickle
import queue as _queue
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Project root is two levels up from this file: tools/debug_log.py → project/
REPO_ROOT = Path(__file__).resolve().parents[1]
# Config lives alongside the tools that consume it: tools/config/logging_config.ini
DEFAULT_LOG_CONFIG = Path(__file__).resolve().parent / "config" / "logging_config.ini"


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
    return os.getenv("DEBUG", "").lower() in {"true", "1", "yes", "on"}


def get_debug_level() -> str:
    """Return the configured debug level string (e.g. 'DEBUG', 'INFO')."""
    if is_debug_mode():
        return os.getenv("DEBUG_LEVEL", "DEBUG").upper()
    return "INFO"


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def _suppress_noisy_library_loggers() -> None:
    """Keep third-party transport loggers from spamming routine requests."""
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def setup_logging_from_config(path: Path | str = DEFAULT_LOG_CONFIG) -> logging.Logger:
    """Configure the root logger from an INI file, with debug-mode overrides.

    Falls back to basicConfig when the INI file is absent.
    """
    config_path = Path(path)
    if not config_path.is_absolute():
        config_path = (REPO_ROOT / config_path).resolve()

    if not config_path.exists():
        level = logging.DEBUG if is_debug_mode() else logging.INFO
        logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s")
        return logging.getLogger(__name__)

    cfg = configparser.ConfigParser()
    cfg.read(str(config_path))
    enabled: bool = cfg.getboolean("log_control", "enabled", fallback=True)

    if not enabled:
        logging.disable(logging.CRITICAL)
        return logging.getLogger(__name__)

    logging.config.fileConfig(
        str(config_path),
        defaults={"project_root": str(REPO_ROOT)},
    )
    _suppress_noisy_library_loggers()

    if is_debug_mode():
        debug_level = get_debug_level()
        level_value = logging.getLevelName(debug_level)
        if isinstance(level_value, int):
            root = logging.getLogger()
            root.setLevel(level_value)
            for handler in root.handlers:
                handler.setLevel(level_value)

    return logging.getLogger(__name__)


logger: logging.Logger = setup_logging_from_config()


# ---------------------------------------------------------------------------
# Multiprocessing log state
# ---------------------------------------------------------------------------

@dataclass
class _LogState:
    log_queue: Optional[multiprocessing.Queue] = None  # type: ignore[type-arg]
    log_listener_process: Optional[multiprocessing.Process] = None
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
    """Run in a listener process: drain the queue and emit records."""
    local_logger = setup_logging_from_config()
    while True:
        record = queue.get()
        if record is None:
            break
        local_logger.handle(record)


def enable_multiprocessing_logging(
    queue: Optional[multiprocessing.Queue] = None,  # type: ignore[type-arg]
    start_listener: bool = True,
) -> Optional[multiprocessing.Queue]:  # type: ignore[type-arg]
    """Activate multiprocessing logging and return the queue in use."""
    if queue is not None:
        LOG_STATE.log_queue = queue
    elif LOG_STATE.log_queue is None:
        LOG_STATE.log_queue = multiprocessing.get_context("spawn").Queue()

    if start_listener and LOG_STATE.log_queue is not None:
        needs_listener = (
            LOG_STATE.log_listener_process is None
            or not LOG_STATE.log_listener_process.is_alive()
        )
        if needs_listener:
            name = "debug-log-listener"
            log_process_spawn_request(name, target=start_log_listener,
                                      args=(LOG_STATE.log_queue,))
            listener = multiprocessing.Process(
                name=name,
                target=start_log_listener,
                args=(LOG_STATE.log_queue,),
                daemon=True,
            )
            listener.start()
            LOG_STATE.log_listener_process = listener
            debug_log("[Multiprocessing] started name=%s pid=%s", name, listener.pid)

    LOG_STATE.is_multiprocessing = LOG_STATE.log_queue is not None
    _sync_log_state()
    return LOG_STATE.log_queue


def attach_worker_log_queue(
    queue: Optional[multiprocessing.Queue],  # type: ignore[type-arg]
) -> None:
    """Call inside worker processes to attach an existing queue without spawning."""
    LOG_STATE.log_queue = queue
    LOG_STATE.is_multiprocessing = queue is not None
    _sync_log_state()


def disable_multiprocessing_logging() -> None:
    """Tear down the logging listener and queue safely."""
    if LOG_STATE.log_queue is not None:
        try:
            LOG_STATE.log_queue.put_nowait(None)
        except (_queue.Full, OSError):
            pass

    if LOG_STATE.log_listener_process is not None:
        LOG_STATE.log_listener_process.join(timeout=5)
        LOG_STATE.log_listener_process = None

    LOG_STATE.log_queue = None
    LOG_STATE.is_multiprocessing = False
    _sync_log_state()


def multiprocessing_logging_enabled() -> bool:
    return bool(LOG_STATE.is_multiprocessing and LOG_STATE.log_queue is not None)


# ---------------------------------------------------------------------------
# Core debug_log function
# ---------------------------------------------------------------------------

def debug_log(message: str, *args: object, **_kwargs: object) -> None:
    """Emit a DEBUG-level log message when DEBUG mode is active.

    Supports both printf-style and f-string usage:

        debug_log("Starting server on port %s", port)
        debug_log(f"Lang dirs: {lang_dirs}")

    In multiprocessing mode the record is routed through the shared queue.
    In thread-pool mode (serve_docs.py) it logs directly from the thread.
    Each message is prefixed with [PID:xxx|process-name] for easy tracing.
    """
    def _should_skip() -> bool:
        if _running_under_pytest():
            return os.getenv("PYTEST_DEBUG_LOG", "").lower() not in {"1", "true", "yes", "on"}
        if not is_debug_mode():
            return True
        return not (
            logger.isEnabledFor(logging.DEBUG)
            or logging.getLogger().isEnabledFor(logging.DEBUG)
        )

    if _should_skip():
        return

    proc = multiprocessing.current_process()
    pid = os.getpid()

    if args:
        try:
            formatted = message % args
        except (TypeError, ValueError) as exc:
            formatted = f"{message} (format error: {exc}, args: {args})"
    else:
        formatted = message

    enhanced = f"[PID:{pid}|{proc.name}] {formatted}"

    if LOG_STATE.is_multiprocessing and LOG_STATE.log_queue is not None:
        # Route through queue so worker-process records reach the listener.
        tmp = setup_logging_from_config()
        frame = inspect.currentframe()
        caller = None
        if frame and frame.f_back:
            caller = frame.f_back.f_back or frame.f_back
        fn = caller.f_code.co_filename if caller else __file__
        ln = caller.f_lineno if caller else 0
        fc = caller.f_code.co_name if caller else "unknown"
        record = tmp.makeRecord(
            tmp.name, logging.DEBUG, fn, ln,
            "[DEBUG] %s", (enhanced,), None, fc,
        )
        LOG_STATE.log_queue.put(record)
    else:
        logger.debug("[DEBUG] %s", enhanced, stacklevel=2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "attach_worker_log_queue",
    "debug_log",
    "disable_multiprocessing_logging",
    "enable_multiprocessing_logging",
    "get_debug_level",
    "is_debug_mode",
    "log_listener_process",
    "log_process_spawn_request",
    "log_queue",
    "logger",
    "multiprocessing_logging_enabled",
    "setup_logging_from_config",
    "start_log_listener",
    "LOG_STATE",
]
