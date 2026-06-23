"""Exercise ``sphinx.util.logging`` from spawned worker processes.

Run directly for a visible demo:

    python3 tests/test_sphinx_logging_multiprocessing.py --demo child-setup

The test forces the ``spawn`` start method because that is the hard case:
workers do not inherit the parent's configured Sphinx logger handlers.
"""

from __future__ import annotations

import multiprocessing
import queue
import subprocess
import sys
import logging as py_logging
from logging.handlers import QueueHandler
from pathlib import Path
from typing import TextIO

from sphinx.util import logging as sphinx_logging

ITERATIONS_PER_PROCESS = 3
LOG_SENTINEL = "sphinx-mp-log"
PIPED_LOG_SENTINEL = "sphinx-mp-piped-log"


class _FakeSphinxConfig:
    suppress_warnings: tuple[str, ...] = ()
    show_warning_types = False


class _FakeSphinxEnv:
    def doc2path(self, docname: str) -> str:
        return docname


class _FakeSphinxApp:
    def __init__(self) -> None:
        self._exception_on_warning = False
        self._warncount = 0
        self.config = _FakeSphinxConfig()
        self.env = _FakeSphinxEnv()
        self.messagelog: list[str] = []


def _worker_count() -> int:
    """Use CPU count minus two, while leaving tiny machines testable."""
    return max(1, multiprocessing.cpu_count() - 2)


def _setup_sphinx_logging(status: TextIO = sys.stdout, warning: TextIO = sys.stderr) -> None:
    sphinx_logging.setup(_FakeSphinxApp(), status, warning, verbosity=0)


def _setup_worker_queue_logging(log_queue: multiprocessing.Queue) -> None:
    sphinx_namespace_logger = py_logging.getLogger(sphinx_logging.NAMESPACE)
    for handler in sphinx_namespace_logger.handlers[:]:
        sphinx_namespace_logger.removeHandler(handler)
    sphinx_namespace_logger.setLevel(py_logging.DEBUG)
    sphinx_namespace_logger.propagate = False
    sphinx_namespace_logger.addHandler(QueueHandler(log_queue))


def _emit_queued_records(log_queue: multiprocessing.Queue, expected_count: int) -> int:
    sphinx_namespace_logger = py_logging.getLogger(sphinx_logging.NAMESPACE)
    emitted = 0
    while emitted < expected_count:
        try:
            record = log_queue.get(timeout=5)
        except queue.Empty:
            return emitted
        sphinx_namespace_logger.handle(record)
        emitted += 1
    return emitted


def _addition_worker(
    worker_id: int,
    *,
    setup_in_worker: bool,
    pipe_to_main: bool,
    log_queue: multiprocessing.Queue | None,
    result_queue: multiprocessing.Queue,
) -> None:
    if setup_in_worker:
        _setup_sphinx_logging()
    if pipe_to_main and log_queue is not None:
        _setup_worker_queue_logging(log_queue)

    logger = sphinx_logging.getLogger("multiprocessing_addition_demo")
    totals: list[int] = []
    for step in range(ITERATIONS_PER_PROCESS):
        left = worker_id + step
        right = step + 2
        total = left + right
        totals.append(total)
        sentinel = PIPED_LOG_SENTINEL if pipe_to_main else LOG_SENTINEL
        logger.info(
            "%s worker=%d step=%d %d+%d=%d",
            sentinel,
            worker_id,
            step,
            left,
            right,
            total,
        )
    result_queue.put((worker_id, totals))


def _run_spawned_addition_demo(mode: str) -> int:
    setup_in_worker = mode == "child-setup"
    pipe_to_main = mode == "queue-to-main"
    if mode == "parent-only":
        _setup_sphinx_logging()
    elif pipe_to_main:
        _setup_sphinx_logging()
    elif not setup_in_worker:
        sys.stderr.write(f"unknown mode: {mode}\n")
        return 2

    ctx = multiprocessing.get_context("spawn")
    result_queue = ctx.Queue()
    log_queue = ctx.Queue() if pipe_to_main else None
    workers = [
        ctx.Process(
            target=_addition_worker,
            args=(worker_id,),
            kwargs={
                "setup_in_worker": setup_in_worker,
                "pipe_to_main": pipe_to_main,
                "log_queue": log_queue,
                "result_queue": result_queue,
            },
        )
        for worker_id in range(_worker_count())
    ]

    for worker in workers:
        worker.start()

    expected_logs = len(workers) * ITERATIONS_PER_PROCESS
    emitted_logs = (
        _emit_queued_records(log_queue, expected_logs)
        if pipe_to_main and log_queue is not None
        else 0
    )

    for worker in workers:
        worker.join(20)
        if worker.is_alive():
            worker.terminate()
            return 3
        if worker.exitcode != 0:
            return worker.exitcode or 4

    results = []
    try:
        for _worker in workers:
            results.append(result_queue.get(timeout=5))
    except queue.Empty:
        return 5

    if pipe_to_main and emitted_logs != expected_logs:
        return 7
    return 0 if len(results) == len(workers) else 6


def _run_demo_subprocess(mode: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--demo", mode],
        capture_output=True,
        check=False,
        text=True,
        timeout=60,
    )


def test_parent_only_sphinx_logging_is_not_visible_from_spawned_workers():
    """Parent setup alone does not reach spawned child processes."""
    result = _run_demo_subprocess("parent-only")

    assert result.returncode == 0, result.stderr
    assert LOG_SENTINEL not in result.stdout


def test_worker_sphinx_logging_setup_is_visible_from_spawned_workers():
    """Each worker can show Sphinx logs when it configures Sphinx logging."""
    result = _run_demo_subprocess("child-setup")

    expected = _worker_count() * ITERATIONS_PER_PROCESS
    assert result.returncode == 0, result.stderr
    assert result.stdout.count(LOG_SENTINEL) == expected


def test_worker_sphinx_logging_can_pipe_records_to_main_process():
    """Workers can queue Sphinx log records for main-process terminal output."""
    result = _run_demo_subprocess("queue-to-main")

    expected = _worker_count() * ITERATIONS_PER_PROCESS
    assert result.returncode == 0, result.stderr
    assert result.stdout.count(PIPED_LOG_SENTINEL) == expected
    assert result.stdout.count(LOG_SENTINEL) == 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--demo":
        raise SystemExit(_run_spawned_addition_demo(sys.argv[2]))
    raise SystemExit("usage: test_sphinx_logging_multiprocessing.py --demo MODE")
