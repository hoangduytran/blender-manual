"""Small shared utility helpers for build/serve tooling."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def format_duration(seconds: float) -> str:
    """Format elapsed seconds for compact human-facing logs."""
    if seconds < 1.0:
        return f"{seconds * 1000.0:.1f}ms"
    if seconds < 60.0:
        return f"{seconds:.3f}s"
    minutes, remaining = divmod(seconds, 60.0)
    return f"{int(minutes)}m{remaining:05.2f}s"


def _log(
    logger: object | None,
    level: str,
    message: str,
    *args: object,
) -> None:
    if logger is None:
        return
    log_method = getattr(logger, level)
    log_method(message, *args)


def timing(
    label: str | None = None,
    *,
    logger: object | None = None,
    level: str = "info",
    log_start: bool = True,
    result_formatter: Callable[[Any], str] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorate a routine and log how long it takes.

    ``logger`` may be a stdlib logger, Sphinx logger adapter, or any object with
    an ``info``-style method. ``result_formatter`` can append count/debug details
    derived from the wrapped function's return value.
    """

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        timing_label = label or func.__qualname__

        @wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            if log_start:
                _log(logger, level, "@timing start: %s", timing_label)
            started_at = perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception:
                elapsed = format_duration(perf_counter() - started_at)
                _log(logger, "warning", "@timing failed: %s elapsed=%s", timing_label, elapsed)
                raise
            elapsed = format_duration(perf_counter() - started_at)
            details = ""
            if result_formatter is not None:
                formatted = result_formatter(result)
                if formatted:
                    details = f" {formatted}"
            _log(logger, level, "@timing done: %s elapsed=%s%s", timing_label, elapsed, details)
            return result

        return wrapped

    return decorate


__all__ = ["format_duration", "timing"]
