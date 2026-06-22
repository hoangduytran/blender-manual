"""Configuration model for single-file application log retention."""

from __future__ import annotations

import ast
import configparser
from dataclasses import dataclass
from pathlib import Path

BYTES_PER_KIBIBYTE = 1024
KIBIBYTES_PER_MEBIBYTE = 1024
BYTES_PER_MEBIBYTE = BYTES_PER_KIBIBYTE * KIBIBYTES_PER_MEBIBYTE
SECONDS_PER_HOUR = 60 * 60

ROTATION_SECTION = "log_rotation"
HANDLER_SECTION = "handler_fileHandler"
HANDLER_ARGS_KEY = "args"
PROJECT_ROOT_KEY = "project_root"
ENABLED_KEY = "enabled"
MAX_SIZE_MB_KEY = "max_size_mb"
MAX_SIZE_KB_KEY = "max_size_kb"
RETENTION_HOURS_KEY = "retention_hours"
MIN_SIZE_MB_KEY = "min_size_after_cleanup_mb"
MIN_SIZE_KB_KEY = "min_size_after_cleanup_kb"
TEMP_FILE_KEY = "temp_file"
CHECK_INTERVAL_KEY = "log_check_interval_sec"
RECORD_MARKER_KEY = "record_marker"

APPLICATION_LOG_FILENAME = "application.log"
TEMP_FILE_SUFFIX = ".tmp"
REWRITE_STAGE_SUFFIX = ".rewrite"
DEFAULT_MAX_SIZE_MB = 10.0
DEFAULT_RETENTION_HOURS = 24.0
DEFAULT_MIN_SIZE_MB = 2.0
DEFAULT_CHECK_INTERVAL_SECONDS = 300.0
DEFAULT_RECORD_MARKER = ""


@dataclass(frozen=True)
class RotationSettings:
    """Validated values used by startup and live log trimming."""

    enabled: bool
    max_size_bytes: int
    retention_seconds: float
    min_size_bytes: int
    log_path: Path
    temp_file: Path
    check_interval_seconds: float
    record_marker: str = DEFAULT_RECORD_MARKER


def _resolve_log_path(
    config: configparser.ConfigParser,
    project_root: Path,
) -> Path:
    interpolation = {PROJECT_ROOT_KEY: str(project_root)}
    try:
        raw_args = config.get(
            HANDLER_SECTION,
            HANDLER_ARGS_KEY,
            vars=interpolation,
        )
        first_arg = ast.literal_eval(raw_args)[0]
        return Path(first_arg)
    except (configparser.Error, TypeError, ValueError, SyntaxError, IndexError):
        return project_root / APPLICATION_LOG_FILENAME


def validate_rotation_settings(settings: RotationSettings) -> RotationSettings:
    """Reject unsafe or contradictory retention limits."""
    if settings.max_size_bytes <= 0:
        raise ValueError(f"{ROTATION_SECTION}.{MAX_SIZE_MB_KEY} must be positive")
    if settings.retention_seconds < 0:
        raise ValueError(f"{ROTATION_SECTION}.{RETENTION_HOURS_KEY} cannot be negative")
    if settings.min_size_bytes < 0:
        raise ValueError(f"{ROTATION_SECTION}.{MIN_SIZE_MB_KEY} cannot be negative")
    if settings.min_size_bytes > settings.max_size_bytes:
        raise ValueError("log cleanup floor cannot exceed its size limit")
    if settings.check_interval_seconds < 0:
        raise ValueError(f"{ROTATION_SECTION}.{CHECK_INTERVAL_KEY} cannot be negative")
    paths_collide = settings.log_path.resolve() == settings.temp_file.resolve()
    if paths_collide:
        raise ValueError("log path and temporary buffer path must differ")
    return settings


def _megabytes_to_bytes(megabytes: float) -> int:
    return int(megabytes * BYTES_PER_MEBIBYTE)


def _configured_size_bytes(
    config: configparser.ConfigParser,
    kilobyte_key: str,
    megabyte_key: str,
    default_megabytes: float,
) -> int:
    has_kilobyte_value = config.has_option(ROTATION_SECTION, kilobyte_key)
    if has_kilobyte_value:
        kilobytes = config.getfloat(ROTATION_SECTION, kilobyte_key)
        return int(kilobytes * BYTES_PER_KIBIBYTE)
    megabytes = config.getfloat(
        ROTATION_SECTION,
        megabyte_key,
        fallback=default_megabytes,
    )
    return _megabytes_to_bytes(megabytes)


def _read_numeric_settings(
    config: configparser.ConfigParser,
) -> tuple[int, float, int, float]:
    max_size = _configured_size_bytes(
        config,
        MAX_SIZE_KB_KEY,
        MAX_SIZE_MB_KEY,
        DEFAULT_MAX_SIZE_MB,
    )
    retention = config.getfloat(
        ROTATION_SECTION,
        RETENTION_HOURS_KEY,
        fallback=DEFAULT_RETENTION_HOURS,
    ) * SECONDS_PER_HOUR
    min_size = _configured_size_bytes(
        config,
        MIN_SIZE_KB_KEY,
        MIN_SIZE_MB_KEY,
        DEFAULT_MIN_SIZE_MB,
    )
    interval = config.getfloat(
        ROTATION_SECTION,
        CHECK_INTERVAL_KEY,
        fallback=DEFAULT_CHECK_INTERVAL_SECONDS,
    )
    return max_size, retention, min_size, interval


def _build_settings(
    config: configparser.ConfigParser,
    log_path: Path,
    project_root: Path,
) -> RotationSettings:
    interpolation = {PROJECT_ROOT_KEY: str(project_root)}
    temp_default = f"{log_path}{TEMP_FILE_SUFFIX}"
    max_size, retention, min_size, interval = _read_numeric_settings(config)
    return RotationSettings(
        enabled=config.getboolean(ROTATION_SECTION, ENABLED_KEY, fallback=False),
        max_size_bytes=max_size,
        retention_seconds=retention,
        min_size_bytes=min_size,
        log_path=log_path,
        temp_file=Path(config.get(
            ROTATION_SECTION,
            TEMP_FILE_KEY,
            vars=interpolation,
            fallback=temp_default,
        )),
        check_interval_seconds=interval,
        record_marker=config.get(
            ROTATION_SECTION,
            RECORD_MARKER_KEY,
            fallback=DEFAULT_RECORD_MARKER,
        ),
    )


def rotation_settings_from_config(
    config: configparser.ConfigParser,
    project_root: Path,
) -> RotationSettings:
    """Resolve and validate ``[log_rotation]`` from an existing parser."""
    log_path = _resolve_log_path(config, project_root)
    settings = _build_settings(config, log_path, project_root)
    return validate_rotation_settings(settings)


def load_rotation_settings(
    config_path: Path | str,
    project_root: Path,
) -> RotationSettings:
    """Read rotation settings from *config_path*."""
    config = configparser.ConfigParser()
    config.read(str(config_path))
    return rotation_settings_from_config(config, project_root)
