"""Byte-exact archive of every distinct war.gov PURSUE CSV state the poller sees.

war.gov revises the CSV in place, sometimes twice in one day. The poller's state
file (data/poll-state.json) records only a hash and a row count, so before this
module existed the bytes behind most hashes were gone and what changed between
two states could not be reproduced (Release 06 at 446 and 447 rows, the second
May 11 state, June 10). Now every distinct state is kept:

    data/csv-archive/<UTC date first seen>-<first 12 hex of sha256>.csv

The file holds the exact bytes war.gov served. Nothing is re-encoded, so
`sha256(file)` starts with the 12 hex digits in its name, and anyone can check it.
`.gitattributes` marks the directory `-text` so git never converts line endings.

One file per distinct state, not per observation: if war.gov reverts to a state
that is already archived, no second copy is written (poll-state history still
records the reversal). The date is the first time the poller saw those bytes.

Standard library only: the Actions runner installs nothing but curl_cffi.

    python -m pipeline.csv_archive add _scratch/uap-csv.csv [--date YYYY-MM-DD]
        Archive a CSV by hand (e.g. a state fetched locally). Idempotent.
    python -m pipeline.csv_archive verify
        Check every file in the archive against its own filename.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = ROOT / "data" / "csv-archive"

PREFIX_LEN = 12
NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([0-9a-f]{12})\.csv$")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _date_from(stamp: str | None) -> str:
    """UTC date for the filename: the YYYY-MM-DD head of an ISO timestamp, else today."""
    if stamp and re.match(r"^\d{4}-\d{2}-\d{2}", stamp):
        return stamp[:10]
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def find(sha256: str, directory: Path | None = None) -> Path | None:
    """The archived file whose bytes hash to `sha256`, or None.

    Matches on the filename prefix first, then re-hashes the candidate, so a
    truncated or hand-edited file is never mistaken for the state it claims to be.
    """
    directory = directory or ARCHIVE_DIR
    if not directory.is_dir():
        return None
    for p in sorted(directory.glob(f"*-{sha256[:PREFIX_LEN]}.csv")):
        if NAME_RE.match(p.name) and _sha256(p.read_bytes()) == sha256:
            return p
    return None


def archive(csv_bytes: bytes, changed_at: str | None = None,
            directory: Path | None = None) -> tuple[Path, bool]:
    """Save `csv_bytes` unless that exact state is already archived.

    Returns (path, created). `changed_at` is the ISO timestamp the state was first
    seen; its date names the file. Raises on I/O failure: the poller wraps this so
    that archiving can never block drop detection.
    """
    directory = directory or ARCHIVE_DIR
    digest = _sha256(csv_bytes)
    existing = find(digest, directory)
    if existing is not None:
        return existing, False
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{_date_from(changed_at)}-{digest[:PREFIX_LEN]}.csv"
    # Write beside the target and rename into place. A run killed mid-write must
    # not leave a short file under the final name; find() would reject it, but a
    # half-file in the commit would be worse than none.
    tmp = path.with_name(f".{path.name}.tmp")
    try:
        tmp.write_bytes(csv_bytes)
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()
    return path, True


def verify(files: list[tuple[str, bytes]]) -> list[str]:
    """Problems with a set of (filename, bytes) pairs; empty list means all good.

    Takes bytes rather than paths so preflight can feed it git blobs, which is
    what actually ships (a working-tree file can be right while its blob is not).
    """
    problems: list[str] = []
    seen: dict[str, str] = {}
    for name, raw in sorted(files):
        m = NAME_RE.match(name)
        if not m:
            problems.append(f"{name}: not named <YYYY-MM-DD>-<12 hex>.csv")
            continue
        if not raw:
            problems.append(f"{name}: empty")
            continue
        got = _sha256(raw)[:PREFIX_LEN]
        if got != m.group(2):
            problems.append(f"{name}: bytes hash to {got}..., not {m.group(2)}... "
                            "(altered, truncated, or line endings converted)")
        if m.group(2) in seen:
            problems.append(f"{name}: duplicates {seen[m.group(2)]} (same state twice)")
        seen[m.group(2)] = name
    return problems


def _cli(argv: list[str]) -> int:
    if argv[:1] == ["verify"]:
        files = [(p.name, p.read_bytes()) for p in sorted(ARCHIVE_DIR.glob("*"))
                 if p.is_file()] if ARCHIVE_DIR.is_dir() else []
        problems = verify(files)
        for p in problems:
            print(f"  FAIL: {p}")
        print(f"{len(files)} archived states, {len(problems)} problem(s)")
        return 1 if problems else 0
    if argv[:1] == ["add"] and len(argv) in (2, 4):
        when = None
        if len(argv) == 4:
            if argv[2] != "--date" or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", argv[3]):
                print(__doc__)
                return 2
            when = argv[3]
        src = Path(argv[1])
        path, created = archive(src.read_bytes(), when)
        print(("archived " if created else "already archived: ") + path.relative_to(ROOT).as_posix())
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
