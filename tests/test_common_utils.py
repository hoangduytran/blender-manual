"""Tests for shared common utility helpers."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from common import utils as common_utils  # noqa: E402


class _ListLogger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def info(self, message: str, *args: object) -> None:
        self.messages.append(message % args if args else message)


def test_timing_decorator_logs_elapsed_and_result_details(monkeypatch):
    ticks = iter([10.0, 12.345])
    logger = _ListLogger()

    monkeypatch.setattr(common_utils, "perf_counter", lambda: next(ticks))

    @common_utils.timing(
        "add numbers",
        logger=logger,
        result_formatter=lambda result: f"result={result}",
    )
    def add(left: int, right: int) -> int:
        return left + right

    assert add(2, 3) == 5
    assert logger.messages == [
        "@timing start: add numbers",
        "@timing done: add numbers elapsed=2.345s result=5",
    ]


def test_format_duration_scales_for_human_logs():
    assert common_utils.format_duration(0.042) == "42.0ms"
    assert common_utils.format_duration(2.5) == "2.500s"
    assert common_utils.format_duration(125.25) == "2m05.25s"
