"""Pipeline orchestrator.

Usage:
    python -m pipeline.run all
    python -m pipeline.run download
    python -m pipeline.run --from extract-pdf
    python -m pipeline.run validate
"""
from __future__ import annotations
import argparse
import sys
import time

from . import (
    parse_inputs, parse_csv, download, download_from_manifest, hash_files,
    upload_r2,
    extract_pdf, thumbnail, transcribe, score, summarize,
    build_search, gen_og, build_site,
    build_verdict, build_top10, build_press_kit, build_api, build_drops,
    translate, clip_generator, validate, index_now, build_categories,
)

STAGES = [
    ("parse-inputs",       parse_inputs.parse_all),
    ("parse-csv",          parse_csv.run),
    ("download",           download.run),
    ("download-manifest",  download_from_manifest.run),
    ("hash",               hash_files.run),
    ("upload-r2",      upload_r2.run),  # no-op without _scratch/r2-creds.json
    ("extract-pdf",    extract_pdf.run),
    ("thumbnails",     thumbnail.run),
    ("transcribe",     transcribe.run),
    ("score",          score.run),
    ("summarize",      summarize.run),
    ("search-index",   build_search.run),
    ("og-cards",       gen_og.run),
    ("build",          build_site.run),
    ("build-verdict",  build_verdict.run),
    ("build-top10",    build_top10.run),
    ("build-press",    build_press_kit.run),
    ("build-api",      build_api.run),
    ("build-drops",    build_drops.run),
    ("build-categories", build_categories.run),
    ("translate",      translate.run),       # no-op without DEEPL_API_KEY
    ("clips",          clip_generator.run),  # no-op without ffmpeg
    ("index-now",      index_now.run),       # ping Bing/Yandex/Naver/Seznam
]
NAMES = [n for n, _ in STAGES]


def _run_stage(name: str, fn) -> None:
    print(f"\n=== {name} ===")
    t0 = time.time()
    fn()
    print(f"=== {name} done in {time.time() - t0:.1f}s ===")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", nargs="?", default="all", help=f"one of: all, validate, {', '.join(NAMES)}")
    ap.add_argument("--from", dest="from_stage", help="run from this stage onward")
    args = ap.parse_args()

    if args.stage == "validate":
        validate.run()
        return 0

    if args.from_stage:
        if args.from_stage not in NAMES:
            print(f"unknown stage: {args.from_stage}")
            return 2
        idx = NAMES.index(args.from_stage)
        for n, fn in STAGES[idx:]:
            _run_stage(n, fn)
        return 0

    if args.stage == "all":
        for n, fn in STAGES:
            _run_stage(n, fn)
        return 0

    if args.stage in NAMES:
        for n, fn in STAGES:
            if n == args.stage:
                _run_stage(n, fn)
                return 0

    print(f"unknown stage: {args.stage}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
