"""Local backup of the entire PURSUE file mirror.

Creates a single tarball containing:
- downloads/         (3.6 GB of mirrored PDFs, videos, images from war.gov + DVIDS)
- extracted/         (~30 MB of extracted text, transcripts, thumbnails)
- data/manifest.json (the full 161-file metadata)
- _scratch/uap-csv.csv (the source CSV from war.gov)

Output: <home>/Backups/pursueufotracker-YYYY-MM-DD-HHMMSS.tar.gz

Run anytime to snapshot. Safe to re-run; each run is a separate dated file.
Suggested cadence: after each new PURSUE drop is downloaded.

Tomorrow: also wire Internet Archive upload (archive.org) for permanent
public-domain backup. archive.org takes US gov works gladly and stores them
forever for free. That's the right long-term home.
"""
from __future__ import annotations
import argparse
import sys
import tarfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKUP_ROOT = Path.home() / "Backups"

INCLUDE = [
    "downloads",
    "extracted",
    "data/manifest.json",
    "_scratch/uap-csv.csv",
    "_scratch/local-paths.json",
]


def human(bytes_: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if bytes_ < 1024:
            return f"{bytes_:.1f} {unit}"
        bytes_ /= 1024
    return f"{bytes_:.1f} PB"


def main() -> int:
    ap = argparse.ArgumentParser(description="Backup the PURSUE file mirror")
    ap.add_argument("--out", default=None, help="output tarball path")
    ap.add_argument("--no-compress", action="store_true", help="skip gzip (faster, larger file)")
    args = ap.parse_args()

    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    ext = ".tar" if args.no_compress else ".tar.gz"
    out = Path(args.out) if args.out else BACKUP_ROOT / f"pursueufotracker-{stamp}{ext}"

    print(f"Backup output: {out}")
    print(f"Source root:   {ROOT}")
    print()

    total_bytes = 0
    file_count = 0
    for rel in INCLUDE:
        src = ROOT / rel
        if not src.exists():
            print(f"  skip (not present): {rel}")
            continue
        if src.is_file():
            total_bytes += src.stat().st_size
            file_count += 1
        else:
            for p in src.rglob("*"):
                if p.is_file():
                    total_bytes += p.stat().st_size
                    file_count += 1

    print(f"Source: {file_count:,} files, {human(total_bytes)} total")
    print(f"Compressing... (30-90 seconds for 3-4 GB)")
    print()

    mode = "w" if args.no_compress else "w:gz"
    with tarfile.open(out, mode) as tar:
        for rel in INCLUDE:
            src = ROOT / rel
            if src.exists():
                tar.add(src, arcname=rel)
                print(f"  + {rel}")

    final_size = out.stat().st_size
    ratio = (1 - final_size / total_bytes) * 100 if total_bytes else 0
    print()
    print(f"Done. Backup size: {human(final_size)} ({ratio:.0f}% smaller than source)")
    print(f"Restore: tar -xzf \"{out}\" -C <dest-folder>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
