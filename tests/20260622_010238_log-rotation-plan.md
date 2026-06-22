# application.log size + retention trimming (PLAN)

**Written:** `20260622_010238`
**Branch:** `feature/new_make_for_foreign_languages`
**Status:** ✅ implemented + tested (`2026-06-22`)
**Skill refs:** `development-guidelines`, `project_management`, `translation-workflow`

## Problem

- All tools log through `tools/debug_log.py` → `setup_logging_from_config()`, which
  calls `logging.config.fileConfig` on `tools/config/logging_config.ini`.
- The `[handler_fileHandler]` is a plain `logging.FileHandler` opened in **append**
  mode on `%(project_root)s/application.log`. It never rotates or trims.
- `application.log` therefore grows unbounded across runs (append-only). It is small
  today (~25 KB), but a long `make liveall` session or many restarts accumulate
  forever with no ceiling.
- Goal (from design discussion): keep the log as a **single file** `application.log`
  and trim it when it exceeds a configured size, preferring recent entries by a
  time-based retention window, with a hard floor so a single noisy day can't keep
  the file huge.

## Decision A — config lives in `logging_config.ini`, new `[log_rotation]` section

Per request, keys go in `tools/config/logging_config.ini` (the file `debug_log.py`
already reads), **not** `manual/conf.py`. New section:

```ini
[log_rotation]
enabled = true
max_size_kb = 200
retention_hours = 24
min_size_after_cleanup_kb = 100
temp_file = %(project_root)s/application.log.tmp
log_check_interval_sec = 5
```

- `enabled` — master switch; when false, behave exactly as today (no trimming).
- `max_size_kb` — trim only triggers when the file exceeds this.
- `retention_hours` — keep entries newer than `now - retention_hours` (time-based,
  more precise/flexible than "days", per the design note).
- `min_size_after_cleanup_kb` — floor for the "still too big" fallback (see Decision C).
- `temp_file` — the scratch path used as the **temp store** for both rewrite modes:
  the staging file for the startup `os.replace()` (Decision C, `in_place=False`) **and**
  the buffer file that captures concurrent writes during the locked watcher trim
  (Decision E). Interpolated with `project_root=REPO_ROOT` exactly like the
  `[handler_fileHandler] args` path, read with `cfg.get(..., fallback=str(log_path) + ".tmp")`
  so a missing key degrades to today's implicit `application.log.tmp`.

All read with `configparser` `getint`/`getfloat`/`getboolean` + `fallback=` so a
missing section or key degrades to current behaviour. Keys are **lowercase**
(configparser lowercases option names anyway; the INI examples in the design used
`MaxSizeMB` — documenting the real key names here to avoid confusion).

## Decision B — **hybrid**: startup trim (replace) + watcher trim (copytruncate)

Two trigger points, because no single one covers every entry path:

1. **Startup**, before the FileHandler opens — covers `make build` and every
   non-server invocation, where no watcher ever runs.
2. **Periodic, in the existing watcher poll loop** — covers a long-running
   `make serve` / `make liveall` session that never restarts, so the file is
   actually bounded *during* the session, not only across restarts.

Rejected the "every N writes" custom handler (complexity); the watcher already
gives us a free, throttled polling tick.

### B.1 — startup trim (the original Decision B)

`application.log` is append-mode; the cross-restart accumulation is fully addressed
by a once-per-startup trim. Trimming **before** `fileConfig` opens the handler means
we rewrite a file **nothing has open** → safe `os.replace()`, no close/reopen, no
risk to the multiprocessing log listener.

Integration point: `setup_logging_from_config()` in `tools/debug_log.py`, in the
`enabled` branch, **immediately before** `logging.config.fileConfig(...)`:

```python
if not enabled:
    logging.disable(logging.CRITICAL)
    return logging.getLogger(__name__)

_maybe_trim_log(cfg, in_place=False)   # <-- runs before any handler opens the file
logging.config.fileConfig(...)
```

`_maybe_trim_log(cfg, ...)` resolves the log path the same way the INI does
(`%(project_root)s/application.log` → `REPO_ROOT / "application.log"`). It must read
the path from the `[handler_fileHandler] args` so the two never drift — parse the
first arg of the `args` tuple, interpolating `project_root=REPO_ROOT`. Fallback to
`REPO_ROOT / "application.log"` if parsing fails.

> Guard: skip trimming under pytest (reuse `_running_under_pytest()`) unless a test
> calls the trimming function directly, so the import-time `setup_logging_from_config()`
> at module load never touches a real log during tests.

### B.2 — watcher trim (the observer already in place)

The observer is `MultiPOWatcher.run()` in `tools/search/po_watcher.py` — a daemon
thread that `time.sleep(interval)`s and re-polls every cycle. Add a log-size check
to that loop, **throttled** so we stat/trim at most once per
`log_check_interval_sec` (not on every 5 s PO poll):

```python
def run(self):
    self._poll_all()
    while True:
        time.sleep(self.interval)
        self._sync_langs()
        self._poll_all()
        self._maybe_trim_log()     # <-- throttled by wall-clock inside
```

`_maybe_trim_log()` calls the same `cleanup_log()` core (Decision C) but with
`in_place=True`, because here the file is **already open**:

- Plain mode: the root-logger `FileHandler` holds the fd in append mode.
- Multiprocessing mode: the fd lives in the **log-listener process**
  (`tools/debug_log.py`), unreachable from the watcher thread.

So `os.replace()` is **not allowed** here — swapping the inode orphans the live fd
and silently drops all subsequent log lines. The watcher path uses **copytruncate**
(in-place `ftruncate`, Decision C) **under a lock that holds back concurrent writers
for the duration of the trim, then flushes them** (Decision E) — so unlike a bare
copytruncate, **no log lines are lost**. The watcher only imports/wires this when
logging is actually configured; under pytest it is not constructed.

## Decision C — trim algorithm (single file, two-stage, two rewrite modes)

```
size = os.path.getsize(application.log)
if not enabled or size <= max_size_bytes:
    return                      # fast path: nothing to do

cutoff = now - timedelta(hours=retention_hours)
read all lines
kept = lines with parsed timestamp >= cutoff
       (+ any continuation/unparseable lines attached to a kept line — see Decision D)

# Stage 2 fallback: a single noisy day can still exceed max_size
if size_of(kept) > max_size_bytes:
    keep newest lines until total <= configured cleanup floor

rewrite application.log with kept lines     # mode depends on in_place (below)
```

- Two stages = the design's "even better" policy: first drop by age, then, only if
  still over `max_size`, drop oldest until the file is down to
  configured cleanup floor.
- **`in_place=False` (startup)** — atomic: write the configured `temp_file`
  (Decision A), then `os.replace()` it over `application.log`. No torn file if the
  process dies mid-write. Safe because no handle is open yet.
- **`in_place=True` (watcher, copytruncate)** — open the *same* file, write `kept`
  from offset 0, then `os.ftruncate(fd, len(kept))`. The inode is preserved, so the
  live FileHandler / listener fd stays valid and keeps appending at the new EOF.
  The copytruncate race (lines appended mid-rewrite getting chopped) is **eliminated**
  by the lock-and-buffer wrapper in **Decision E**: concurrent records are captured
  in a temp buffer for the duration of the locked trim and replayed afterwards, so no
  line is lost.

## Decision E — lock the log, buffer writes to a temp store, flush on release

The watcher trim (B.2 / `in_place=True`) must not lose records produced while it is
rewriting. Mechanism: **hold a lock, divert concurrent writes into the configured
`temp_file` (Decision A) as the temp store, run the trim, then flush that temp file
back into the log and release.** Using a real on-disk `temp_file` (rather than a
purely in-memory buffer) means buffered records survive even if the process dies
mid-trim — the next startup trim reads `application.log`, and a leftover non-empty
`temp_file` is replayed/cleaned on the next setup. Implementation differs by mode:

### E.1 — plain (single-process) mode

The root-logger `FileHandler` is reachable in-process. Wrap the trim:

```
fh = _find_file_handler()          # the FileHandler on the root logger
fh.acquire()                       # logging's own per-handler lock; blocks emit()
try:
    fh._divert_path = temp_file    # emit() writes to temp_file instead of the log
    cleanup_log(path, cfg, in_place=True)   # copytruncate the now-quiescent file
finally:
    fh._divert_path = None
    fh.release()
_flush_temp_into_log(temp_file, path)   # append temp_file's lines at new EOF, then DELETE temp_file
```

- The handler's existing `self.lock` already serialises `emit()`; acquiring it means
  no write touches the log during the read+truncate.
- `temp_file` is the on-disk "temp internal store": records that would have been
  written to `application.log` are appended to `temp_file` instead, then flushed back
  after the truncate so they land at the new EOF. Net effect: **zero loss, no torn
  lines**, and crash-durable (the buffer is a file, not RAM).
- **Cleanup:** `_flush_temp_into_log` removes `temp_file` once its contents are safely
  appended (`os.replace`/`os.remove` after the append `fsync`s). The trim is idempotent
  — no leftover `temp_file` after a successful run, so the file's mere existence on next
  startup signals a crashed prior trim and is replayed-then-removed before logging opens.
- Practical realisation: a thin `FileHandler` subclass whose `emit()` checks
  `_divert_path` and writes there when set. Keep it minimal — the diversion is active
  only for the sub-second trim window.

### E.2 — multiprocessing mode (log-listener process owns the fd)

The watcher thread (main process) cannot touch the listener's handler. Instead,
**route the trim through the existing log queue**, reusing the same machinery as the
`None` shutdown sentinel:

- The watcher enqueues a control sentinel (e.g. `("__TRIM__", path, cfg_dict)`).
- The listener drains the queue **serially**, so when it pops the sentinel no other
  record is being written — it runs `cleanup_log(..., in_place=True)` itself.
- Records produced meanwhile simply **queue up** — the multiprocessing `Queue` *is*
  the temp store — and are emitted in order once the trim returns. **No lock needed,
  no loss**, because the listener already processes one item at a time.

`start_log_listener()` in `tools/debug_log.py` grows a branch to recognise the trim
sentinel; the watcher chooses E.1 vs E.2 via `multiprocessing_logging_enabled()`.
Here the in-memory `Queue` is the temp store, so there is **no `temp_file` to clean
up** — it only applies to the E.1 / startup `os.replace` paths.

## Decision D — timestamp parsing matches the formatter exactly

- Formatter `datefmt = %Y-%m-%d %H:%M:%S`; every emitted line **starts** with that
  19-char stamp (verified against the live `application.log`):
  `2026-06-21 22:50:50 - INFO - root - [...] - msg`.
- `parse_timestamp(line)`: `datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")`.
- **Multi-line records** (tracebacks, the `\nShutting down.` message): a line whose
  first 19 chars don't parse is a **continuation** of the previous record. Rule:
  unparseable lines inherit the decision of the most recent parseable line (kept or
  dropped together) so we never split a record. Leading unparseable lines (no prior
  record) are dropped with the oldest block.
- Use naive local `datetime.now()` to match the naive local stamps in the log.

## Files to change

| File | Change |
|------|--------|
| `tools/config/logging_config.ini` | `[log_rotation]`; final limits + transient buffer path |
| `tools/common/log_rotation_config.py` | named config keys/defaults; validated immutable settings |
| `tools/common/log_rotation.py` | record grouping; retention; startup recovery; replace/copytruncate |
| `tools/common/log_rotation_handler.py` | open-handler diversion + durable replay |
| `tools/debug_log.py` | startup hook; live dispatch; multiprocessing queue sentinel |
| `tools/search/po_watcher.py` | throttled live check after PO polling |
| `tools/serve_docs.py` | remove competing legacy trimmer startup |
| `tests/test_log_rotation.py` | 15 behavior/config/integration tests |

## Tests (`tests/test_log_rotation.py`)

Pure-function tests on a temp file — no real `application.log`, no logging setup:

1. **under size** → file untouched (fast path).
2. **over size, age-based** → entries older than `retention_hours` dropped, newer kept.
3. **stage-2 fallback** → all entries within retention but still > `max_size` →
   trimmed down to ≤ configured cleanup floor, newest preserved.
4. **multi-line record** → a traceback / `\nShutting down.` block stays attached to
   its timestamped line (kept or dropped as a unit, never split).
5. **`enabled = false`** → no trimming regardless of size.
6. **malformed / empty file** → no crash, file left usable.
7. **startup rewrite (`in_place=False`)** → trims via `temp_file` + `os.replace`;
   **no leftover `temp_file`** afterwards; content valid.
8. **in-place rewrite (`in_place=True`)** → copytruncate keeps the same inode (fd/stat
   `st_ino` unchanged), content trimmed correctly.
9. **lock + temp-store flush (E.1)** → records written *during* the locked trim land in
   `temp_file`, get appended back at the new EOF, and `temp_file` is **deleted** after
   flush; total line set = kept ∪ during-trim, none lost.
10. **temp-file cleanup on crash path** → a pre-existing non-empty `temp_file` at
    startup is replayed into the log then removed before `fileConfig` opens.

## Out of scope / rejected

- **stdlib `RotatingFileHandler` / `TimedRotatingFileHandler`** — these create
  `.1`, `.2`, … rollover files; the requirement is an explicit **single** file.
- **Continuous "every N writes" custom handler** — rejected per Decision B
  (complexity + open-handle rewrite during long server runs).
- **Config in `manual/conf.py`** — superseded; config lives in `logging_config.ini`.

## Resolved / verification

- Active config: `200 KiB` trigger; `24 h` retention; `100 KiB` fallback floor; `5 s` check.
- One log only. No rollover files or old-log archives. `.tmp`/`.rewrite` transient only.
- Crash buffer replayed then deleted; incomplete rewrite stage discarded.
- `pytest tests -q -p no:cacheprovider` → `32 passed`.
- `ruff check` on changed Python files → clean.
- Live `make liveall` probe: `101,890 B` → `480,545 B` → `101,890 B`;
  stable after 6 s; ports `8000/8081/8082` healthy; no archive/temp logs.
