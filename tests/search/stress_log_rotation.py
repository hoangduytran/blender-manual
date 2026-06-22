#!/usr/bin/env python3
"""Stress / smoke test for application.log trimming.

Spawns multiple *real process instances*, each of which imports
``tools.debug_log`` (firing the startup trim) and then writes a batch of log
lines.  As the file crosses ``MAX_SIZE_BYTES`` the next instance's startup trim
drops it back to ``MIN_SIZE_BYTES`` — so the on-disk log sawtooths and never
runs away.  A second phase exercises the in-place (watcher copytruncate) path
while a ``FileHandler`` holds the file open.

Run:     python3 tests/search/stress_log_rotation.py
Worker:  python3 tests/search/stress_log_rotation.py --worker <lines> <id>
"""
from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants — no magic numbers / strings below this block.
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "tools"
LOG_PATH = REPO_ROOT / "application.log"
TEMP_PATH = REPO_ROOT / "application.log.tmp"

BYTES_PER_KB = 1024
MAX_SIZE_BYTES = 500 * BYTES_PER_KB          # trim trigger
MIN_SIZE_BYTES = 200 * BYTES_PER_KB          # stage-2 floor
RETENTION_SECONDS = 24 * 60 * 60             # keep everything "today" → forces stage-2

SEQUENTIAL_INSTANCES = 6
LINES_PER_INSTANCE = 4000
IN_PLACE_PRELOAD_LINES = 6000
IN_PLACE_POST_TRIM_LINES = 50

WORKER_FLAG = "--worker"
FILLER_CHAR = "x"
FILLER_WIDTH = 60
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - [stress] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

WORKER_LINE_PREFIX = "WORKER"
POST_TRIM_KEY = "post_trim="
POST_WRITE_KEY = "post_write="
POST_TRIM_MARKER = "post-trim line"
EMPTY = 0
MISSING = -1

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))


# ---------------------------------------------------------------------------
# Small shared helpers
# ---------------------------------------------------------------------------

def human(num_bytes: int) -> str:
    """Render a byte count as kilobytes for readable reports."""
    return f"{num_bytes / BYTES_PER_KB:.1f} KB"


def file_size(path: Path) -> int:
    """Return *path* size in bytes, or ``EMPTY`` when it does not exist."""
    return path.stat().st_size if path.exists() else EMPTY


def make_handler(path: Path) -> logging.FileHandler:
    """Open an append-mode FileHandler with the stress formatter."""
    handler = logging.FileHandler(path, mode="a", encoding="utf-8")
    handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    return handler


def count_torn_lines(path: Path) -> tuple[int, int]:
    """Return ``(total_lines, torn_lines)``.

    A torn line is a leading continuation that appears before any timestamped
    record — i.e. a record split by a bad rewrite.
    """
    import debug_log

    if not path.exists():
        return (EMPTY, EMPTY)
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()
    torn = 0
    seen_timestamp = False
    for line in lines:
        is_record_start = debug_log.parse_timestamp(line) is not None
        if is_record_start:
            seen_timestamp = True
        elif not seen_timestamp:
            torn += 1
    return (len(lines), torn)


# ---------------------------------------------------------------------------
# Worker: one process instance — import (startup trim) then write a batch.
# ---------------------------------------------------------------------------

def run_worker(lines: int, worker_id: int) -> None:
    import debug_log  # import triggers setup_logging_from_config + startup trim

    size_after_trim = file_size(LOG_PATH)
    filler = FILLER_CHAR * FILLER_WIDTH
    for line_no in range(lines):
        debug_log.logger.info("instance %02d line %05d %s", worker_id, line_no, filler)
    flush_all_handlers()
    size_after_write = file_size(LOG_PATH)
    print(f"{WORKER_LINE_PREFIX} {worker_id} "
          f"{POST_TRIM_KEY}{size_after_trim} {POST_WRITE_KEY}{size_after_write}")


def flush_all_handlers() -> None:
    for handler in logging.getLogger().handlers:
        handler.flush()


# ---------------------------------------------------------------------------
# Phase 1 driver: sequential instances, startup os.replace trim.
# ---------------------------------------------------------------------------

def spawn_worker(lines: int, worker_id: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, __file__, WORKER_FLAG, str(lines), str(worker_id)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )


def parse_worker_report(stdout: str, worker_id: int) -> tuple[int, int]:
    """Extract ``(size_after_trim, size_after_write)`` from a worker's stdout."""
    prefix = f"{WORKER_LINE_PREFIX} {worker_id} "
    line = next((ln for ln in stdout.splitlines() if ln.startswith(prefix)), "")
    if not line:
        return (MISSING, MISSING)
    after_trim = int(line.split(POST_TRIM_KEY)[1].split()[0])
    after_write = int(line.split(POST_WRITE_KEY)[1])
    return (after_trim, after_write)


def run_sequential_phase() -> bool:
    print("\n=== phase 1: sequential instances (startup os.replace trim) ===")
    print(f"{'inst':>4}  {'size_before':>12}  {'post_trim':>12}  {'post_write':>12}")

    reset_log_files()
    peak_size = EMPTY
    for worker_id in range(SEQUENTIAL_INSTANCES):
        size_before = file_size(LOG_PATH)
        result = spawn_worker(LINES_PER_INSTANCE, worker_id)
        size_after_trim, size_after_write = parse_worker_report(result.stdout, worker_id)
        peak_size = max(peak_size, size_after_write)
        print(f"{worker_id:>4}  {human(size_before):>12}  "
              f"{human(size_after_trim):>12}  {human(size_after_write):>12}")
        if result.returncode != 0:
            print("  worker stderr:", result.stderr[-400:])

    return report_sequential_result(peak_size)


def report_sequential_result(peak_size: int) -> bool:
    final_size = file_size(LOG_PATH)
    total_lines, torn_lines = count_torn_lines(LOG_PATH)
    # A single batch can sit on top of the post-trim floor, so the upper bound
    # is the floor plus one instance's worth of writes — never unbounded growth.
    one_batch_bytes = peak_size - MIN_SIZE_BYTES
    bound_bytes = MIN_SIZE_BYTES + one_batch_bytes + MAX_SIZE_BYTES
    size_is_bounded = peak_size <= bound_bytes
    no_torn_lines = torn_lines == EMPTY
    temp_cleaned = not TEMP_PATH.exists()
    passed = size_is_bounded and no_torn_lines and temp_cleaned

    print(f"\npeak size reached : {human(peak_size)}")
    print(f"final size        : {human(final_size)}")
    print(f"final lines/torn  : {total_lines} / {torn_lines}")
    print(f"leftover temp file: {not temp_cleaned}")
    print(f"phase 1 RESULT    : {verdict(passed)}")
    return passed


# ---------------------------------------------------------------------------
# Phase 2 driver: in-place trim while a handler holds the fd open.
# ---------------------------------------------------------------------------

def preload_open_log(handler: logging.FileHandler) -> logging.Logger:
    log = logging.getLogger("inplace_test")
    log.setLevel(logging.INFO)
    log.addHandler(handler)
    log.propagate = False
    filler = "y" * FILLER_WIDTH
    for line_no in range(IN_PLACE_PRELOAD_LINES):
        log.info("preload line %05d %s", line_no, filler)
    handler.flush()
    return log


def write_post_trim_lines(log: logging.Logger, handler: logging.FileHandler) -> None:
    filler = "z" * FILLER_WIDTH
    for line_no in range(IN_PLACE_POST_TRIM_LINES):
        log.info("%s %05d %s", POST_TRIM_MARKER, line_no, filler)
    handler.flush()


def run_in_place_phase() -> bool:
    import debug_log

    print("\n=== phase 2: in-place (watcher copytruncate) path ===")
    reset_log_files()
    handler = make_handler(LOG_PATH)
    log = preload_open_log(handler)

    size_before = file_size(LOG_PATH)
    inode_before = LOG_PATH.stat().st_ino
    trimmed = debug_log.cleanup_log(
        LOG_PATH,
        max_size_bytes=MAX_SIZE_BYTES,
        retention_seconds=RETENTION_SECONDS,
        min_size_bytes=MIN_SIZE_BYTES,
        in_place=True,
    )
    size_after_trim = file_size(LOG_PATH)
    inode_after = LOG_PATH.stat().st_ino

    write_post_trim_lines(log, handler)        # same OPEN handler, post-trim
    size_final = file_size(LOG_PATH)
    handler.close()

    return report_in_place_result(
        trimmed, size_before, size_after_trim, size_final,
        inode_before, inode_after,
    )


def report_in_place_result(
    trimmed: bool, size_before: int, size_after_trim: int, size_final: int,
    inode_before: int, inode_after: int,
) -> bool:
    total_lines, torn_lines = count_torn_lines(LOG_PATH)
    last_marker = f"{POST_TRIM_MARKER} {IN_PLACE_POST_TRIM_LINES - 1:05d}"
    post_trim_writes_landed = last_marker in LOG_PATH.read_text(encoding="utf-8")

    inode_preserved = inode_before == inode_after
    trimmed_to_floor = size_after_trim <= MIN_SIZE_BYTES
    no_torn_lines = torn_lines == EMPTY
    handler_kept_writing = size_final > size_after_trim
    passed = (trimmed and inode_preserved and trimmed_to_floor
              and post_trim_writes_landed and no_torn_lines and handler_kept_writing)

    print(f"  before trim       : {human(size_before)}  inode={inode_before}")
    print(f"  trim ran          : {trimmed}")
    print(f"  after trim        : {human(size_after_trim)}  inode={inode_after}")
    print(f"  inode preserved   : {inode_preserved}")
    print(f"  after live writes : {human(size_final)}  (handler kept writing: "
          f"{handler_kept_writing})")
    print(f"  post-trim landed  : {post_trim_writes_landed}")
    print(f"  lines/torn        : {total_lines} / {torn_lines}")
    print(f"  phase 2 RESULT    : {verdict(passed)}")
    return passed


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def verdict(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def reset_log_files() -> None:
    LOG_PATH.unlink(missing_ok=True)
    TEMP_PATH.unlink(missing_ok=True)


def run_driver() -> None:
    print(f"REPO_ROOT = {REPO_ROOT}")
    print(f"config: max={human(MAX_SIZE_BYTES)}  floor={human(MIN_SIZE_BYTES)}  "
          f"instances={SEQUENTIAL_INSTANCES}  lines/instance={LINES_PER_INSTANCE}")

    phase1_passed = run_sequential_phase()
    phase2_passed = run_in_place_phase()

    all_passed = phase1_passed and phase2_passed
    print(f"\nOVERALL: {verdict(all_passed)}")
    sys.exit(EMPTY if all_passed else 1)


def is_worker_invocation() -> bool:
    return len(sys.argv) >= 2 and sys.argv[1] == WORKER_FLAG


def main() -> None:
    if is_worker_invocation():
        run_worker(int(sys.argv[2]), int(sys.argv[3]))
    else:
        run_driver()


if __name__ == "__main__":
    main()
