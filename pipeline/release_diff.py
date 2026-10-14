"""Row-by-row diff of war.gov's PURSUE CSV between releases.

The /changes page quotes counts (rows added, removed, edited) for Releases 04,
05 and 06. This module is where those counts come from, so anyone can re-run
them. It reads each release's CSV out of this repository's git history (the
commit that first held that release's rows), compares consecutive releases, and
writes data/release-diff.json, which lists every added, removed and edited row.

    python -m pipeline.release_diff            # print summary, write the JSON
    python -m pipeline.release_diff --check    # exit 1 if the JSON is stale

Rows are matched on (ID, file link). The ID is the first comma-separated token
of the Title column (e.g. "DOW-UAP-D084"). A title change therefore shows up as
an edited row, not as a removal plus an addition. The ID alone is not unique:
FBI-UAP-D014 is carried by two different documents since Release 04, which is
why the file link is part of the key.

When war.gov publishes Release 07, append one line to SNAPSHOTS (the commit that
ingested it) and re-run. Nothing here fetches from war.gov or edits any CSV.

A SNAPSHOTS ref is either a git commit or `archive:<12 hex>`, the first 12 digits
of a CSV state's SHA-256, which reads data/csv-archive/<date>-<12 hex>.csv. The
poller archives every state it sees, so a mid-release revision (a hash change
that is not a new release) can be diffed against its neighbours the same way.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
from collections import Counter

from .config import DATA_DIR, ROOT

OUT_PATH = DATA_DIR / "release-diff.json"
POLL_STATE = DATA_DIR / "poll-state.json"

# (label, Release Date value in the CSV, git commit holding data/uap-data.csv at that release)
SNAPSHOTS = [
    ("Release 03", "6/12/26", "72463170"),
    ("Release 04", "7/10/26", "e25c27c1"),
    ("Release 05", "8/7/26", "3db64f7a"),
    ("Release 06", "9/18/26", "189e0919"),
]

FIELDS = [
    "Featured", "Redaction", "Release Date", "Title", "Type", "Video Pairing",
    "PDF Pairing", "Description Blurb", "DVIDS Video ID", "Video Title", "Agency",
    "Incident Date", "Incident Location", "PDF | Image Link", "Modal Image",
    "Image Alt Text", "Image VIRIN",
]


def _git_show(ref: str) -> bytes:
    """CSV bytes for a SNAPSHOTS entry: `archive:<12 hex>` reads that state from
    data/csv-archive/ (byte-exact copies the poller saves); anything else is a git
    commit holding data/uap-data.csv."""
    if ref.startswith("archive:"):
        found = sorted((DATA_DIR / "csv-archive").glob(f"*-{ref[len('archive:'):]}.csv"))
        if len(found) != 1:
            raise SystemExit(f"{ref}: expected exactly one file in data/csv-archive/, found {len(found)}")
        return found[0].read_bytes()
    return subprocess.run(
        ["git", "show", f"{ref}:data/uap-data.csv"],
        cwd=ROOT, check=True, capture_output=True,
    ).stdout


def _rows(raw: bytes) -> list[dict]:
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))


def _row_id(r: dict) -> str:
    return (r.get("Title") or "").split(",")[0].strip()


def _link(r: dict) -> str:
    return ((r.get("PDF | Image Link") or "").strip().lower()
            or "dvids:" + (r.get("DVIDS Video ID") or "").strip())


def _key(r: dict) -> tuple[str, str]:
    return (_row_id(r), _link(r))


def _brief(r: dict) -> dict:
    return {"id": _row_id(r), "title": (r.get("Title") or "").strip(),
            "type": r.get("Type", ""), "agency": r.get("Agency", "")}


def _featured(rows: list[dict]) -> list[dict]:
    return [r for r in rows if (r.get("Featured") or "").strip()]


def _recorded_hashes() -> set[str]:
    try:
        state = json.loads(POLL_STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {h["csv_sha256"] for h in state.get("history", []) if h.get("csv_sha256")}


def _diff(old: list[dict], new: list[dict]) -> dict:
    ko, kn = {_key(r): r for r in old}, {_key(r): r for r in new}
    added = [r for k, r in kn.items() if k not in ko]
    removed = [r for k, r in ko.items() if k not in kn]
    edited = []
    for k in ko.keys() & kn.keys():
        changes = {f: [ko[k].get(f) or "", kn[k].get(f) or ""] for f in FIELDS
                   if (ko[k].get(f) or "") != (kn[k].get(f) or "")}
        if changes:
            edited.append({"id": k[0], "title": (kn[k].get("Title") or "").strip(), "fields": changes})
    # Same ID on both sides with a different file link: a re-link, not an add + remove.
    old_ids = {_row_id(r): r for r in removed}
    relinked = []
    for r in list(added):
        o = old_ids.get(_row_id(r))
        if o is not None:
            relinked.append({"id": _row_id(r), "old_link": o.get("PDF | Image Link"),
                             "new_link": r.get("PDF | Image Link")})
            added.remove(r)
            removed.remove(o)
    added_sorted = sorted(map(_brief, added), key=lambda b: b["id"])
    return {
        "rows_before": len(old), "rows_after": len(new),
        "added": added_sorted,
        "added_by_agency_type": {f"{a} | {t}": n for (a, t), n in
                                 sorted(Counter((b["agency"], b["type"]) for b in added_sorted).items())},
        "removed": sorted(map(_brief, removed), key=lambda b: b["id"]),
        "relinked": relinked,
        "edited": sorted(edited, key=lambda e: e["id"]),
        "edited_field_counts": dict(sorted(Counter(f for e in edited for f in e["fields"]).items())),
        "featured_cleared": sum(1 for e in edited if e["fields"].get("Featured", ["", ""])[1] == ""
                                and e["fields"].get("Featured", ["", ""])[0] != ""),
        "new_agency_labels": sorted({r.get("Agency", "") for r in new} - {r.get("Agency", "") for r in old}),
    }


def build() -> dict:
    recorded = _recorded_hashes()
    snaps = []
    for label, rel_date, commit in SNAPSHOTS:
        raw = _git_show(commit)
        rows = _rows(raw)
        digest = hashlib.sha256(raw).hexdigest()
        snaps.append({
            "label": label, "release_date": rel_date, "commit": commit, "rows": rows,
            "meta": {
                "label": label, "commit": commit, "rows": len(rows), "sha256_of_git_copy": digest,
                # True when the committed bytes equal the bytes war.gov served (poller's record).
                # False for copies committed before line endings were pinned (2026-07-12).
                "byte_exact_vs_poll_state": digest in recorded,
                "release_date_rows": sum(1 for r in rows if r.get("Release Date") == rel_date),
                "featured_rows": len(_featured(rows)),
                "featured_release_dates": sorted({r.get("Release Date", "") for r in _featured(rows)}),
                "duplicate_ids": sorted(i for i, n in Counter(map(_row_id, rows)).items() if n > 1),
            },
        })
    steps = []
    for a, b in zip(snaps, snaps[1:]):
        d = _diff(a["rows"], b["rows"])
        d.update({"from": a["label"], "to": b["label"]})
        # Every row flagged Featured in the older CSV: is the flag cleared in the newer one?
        newer = {_key(r): r for r in b["rows"]}
        prev_feat = [_key(r) for r in _featured(a["rows"])]
        d["previous_featured_rows"] = len(prev_feat)
        d["previous_featured_cleared"] = sum(1 for k in prev_feat
                                             if k in newer and not (newer[k].get("Featured") or "").strip())
        steps.append(d)
    first, last = snaps[0], snaps[-1]
    missing = Counter(map(_key, first["rows"])) - Counter(map(_key, last["rows"]))
    return {
        "about": "Row-by-row diff of war.gov's PURSUE CSV between releases, computed by "
                 "pipeline/release_diff.py from CSV copies in this repository's git history. "
                 "Rows match on (ID, file link); see the module docstring.",
        "snapshots": [s["meta"] for s in snaps],
        "steps": steps,
        "first_release_rows_missing_from_latest": sum(missing.values()),
    }


def _dump(obj: dict) -> str:
    return json.dumps(obj, indent=1, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    out = build()
    text = _dump(out)
    if "--check" in argv:
        current = OUT_PATH.read_text(encoding="utf-8") if OUT_PATH.exists() else ""
        if current != text:
            print("release-diff.json is stale: run python -m pipeline.release_diff")
            return 1
        print("release-diff.json is current")
        return 0
    OUT_PATH.write_text(text, encoding="utf-8", newline="\n")
    for s in out["snapshots"]:
        print(f"{s['label']}: {s['rows']} rows, commit {s['commit']}, "
              f"byte-exact vs poll-state: {s['byte_exact_vs_poll_state']}, "
              f"flagged Featured: {s['featured_rows']}, duplicate ids: {s['duplicate_ids'] or 'none'}")
    for d in out["steps"]:
        print(f"{d['from']} -> {d['to']}: {d['rows_before']} -> {d['rows_after']} rows | "
              f"added {len(d['added'])} | removed {len(d['removed'])} | relinked {len(d['relinked'])} | "
              f"edited {len(d['edited'])} {d['edited_field_counts']} | "
              f"prior Featured cleared {d['previous_featured_cleared']}/{d['previous_featured_rows']} | "
              f"new agency labels {d['new_agency_labels'] or 'none'}")
    print(f"{out['snapshots'][0]['label']} rows missing from {out['snapshots'][-1]['label']}: "
          f"{out['first_release_rows_missing_from_latest']}")
    print(f"wrote {OUT_PATH.relative_to(ROOT)}")
    return 0


def run() -> None:
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    run()
