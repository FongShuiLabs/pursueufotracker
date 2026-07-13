"""Drop-ingest and pre-push guards. Encodes the 2026-07-11/12 Drop 04 lessons
so the next drop cannot silently repeat them.

Three subcommands, run at three moments:

  python -m pipeline.preflight pre-ingest
      BEFORE `pipeline.run all` on a real drop. Fetches a verified-fresh CSV
      via poll_wargov's tested curl_cffi path, writes it to _scratch/uap-csv.csv,
      and confirms its SHA-256 matches what the poller recorded in
      data/poll-state.json. Guards against: parse-csv silently ingesting a
      stale/wrong-schema local scratch file (the "294 entries" incident).

  python -m pipeline.preflight post-ingest
      AFTER the pipeline finishes, BEFORE trusting/committing the result.
      Diffs data/manifest.json against the last committed version. Hard-fails
      on: previously-live file ids missing (the 196-renamed-ids incident),
      OTHER-agency junk entries (the 166-junk-pages incident), or a video
      count that shrank (the 118->10 dict-collision incident).

  python -m pipeline.preflight pre-push
      BEFORE `git push`. Hard-fails if any file staged/committed at HEAD
      exceeds Cloudflare Pages' 25 MiB limit (the "No deployment available"
      incident), warns if _redirects is near the ~100-rule effective ceiling,
      and re-verifies the served CSV mirror blob is byte-exact vs poll-state.

Exit code 0 = safe to proceed. Non-zero = stop and read the output.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data" / "manifest.json"
POLL_STATE = ROOT / "data" / "poll-state.json"
REDIRECTS = ROOT / "_redirects"
CF_LIMIT = 25 * 1024 * 1024  # Cloudflare Pages per-file hard limit
REDIRECT_CEILING = 100       # observed effective rule cutoff (see memory notes)


def _fail(msg: str) -> None:
    print(f"  FAIL: {msg}")
    sys.exit(1)


def _ok(msg: str) -> None:
    print(f"  ok: {msg}")


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8", cwd=ROOT)
    return r.stdout


def pre_ingest() -> None:
    """Fetch a verified-fresh CSV and confirm it matches the poller's record."""
    from .poll_wargov import _fetch_csv, CSV_OUT, _csv_row_count

    state = json.loads(POLL_STATE.read_text(encoding="utf-8"))
    expected = state.get("csv_sha256")
    print(f"pre-ingest: poller expects sha256 {expected[:16]}..., "
          f"{state.get('row_count')} rows")

    result = _fetch_csv()
    if result is None:
        _fail("live CSV fetch failed on all paths (curl_cffi + playwright). "
              "Do NOT run the pipeline on the stale scratch file.")
    csv_bytes, source = result
    got = hashlib.sha256(csv_bytes).hexdigest()
    rows = _csv_row_count(csv_bytes.decode("utf-8-sig", errors="replace"))

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    CSV_OUT.write_bytes(csv_bytes)
    _ok(f"fetched {rows} rows via {source}, wrote {CSV_OUT.name}")

    if got != expected:
        _fail(f"fresh fetch sha256 {got[:16]}... != poll-state {expected[:16]}... "
              "war.gov changed since the last poll. Re-check poll-state / wait "
              "for the poller before ingesting, so counts you publish match "
              "what the drop announcement will say.")
    _ok("fresh CSV sha256 matches data/poll-state.json - safe to run "
        "`python -m pipeline.run all`")


def post_ingest() -> None:
    """Diff the new manifest against HEAD's committed manifest."""
    old_raw = _git("show", "HEAD:data/manifest.json")
    if not old_raw.strip():
        _fail("could not read HEAD:data/manifest.json")
    old = {f["id"]: f for f in json.loads(old_raw)["files"]}
    new_files = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]
    new = {f["id"]: f for f in new_files}

    print(f"post-ingest: HEAD manifest {len(old)} files -> new manifest {len(new)}")

    missing = sorted(set(old) - set(new))
    if missing:
        print(f"  first missing ids: {missing[:8]}")
        _fail(f"{len(missing)} previously-live file ids are GONE from the new "
              "manifest. Live URLs would break (never delete/rename a file "
              "page - project Hard Rule #1). This is the download.py "
              "id-corruption signature: do not commit; revert data/ and "
              "generated/ and investigate.")
    _ok("zero previously-live ids lost")

    junk = [f["id"] for f in new_files if f.get("agency") in (None, "", "OTHER")]
    if junk:
        print(f"  first junk ids: {junk[:8]}")
        _fail(f"{len(junk)} entries have agency OTHER/empty - placeholder junk "
              "from the legacy URL-scrape path. Do not commit.")
    _ok("zero OTHER-agency junk entries")

    old_types = Counter(f.get("type") for f in json.loads(old_raw)["files"])
    new_types = Counter(f.get("type") for f in new_files)
    for t in ("video", "pdf", "image"):
        if new_types[t] < old_types[t]:
            _fail(f"{t} count SHRANK {old_types[t]} -> {new_types[t]}. Files "
                  "of an existing type never disappear in a drop (the "
                  "video-collapse signature). Do not commit.")
    _ok(f"type counts sane: {dict(new_types)} (was {dict(old_types)})")

    incomplete = [f["id"] for f in new_files
                  if f["id"] not in old and (
                      not f.get("title") or not f.get("sha256")
                      or not (f.get("score") or {}).get("value"))]
    if incomplete:
        print(f"  first incomplete: {incomplete[:8]}")
        _fail(f"{len(incomplete)} NEW files are missing title/sha256/score - "
              "the pipeline did not finish enriching them. Re-run the "
              "remaining stages before building pages.")
    _ok(f"all {len(new) - len(set(old) & set(new))} new files fully enriched")
    print("post-ingest: manifest diff is clean - safe to build/commit")


def pre_push() -> None:
    """Catch deploy-killers before they reach Cloudflare."""
    oversize = []
    for line in _git("ls-tree", "-r", "-l", "HEAD").splitlines():
        parts = line.split(None, 4)
        if len(parts) == 5 and parts[3].isdigit() and int(parts[3]) > CF_LIMIT:
            oversize.append(f"{int(parts[3]) / 1048576:.1f} MiB  {parts[4]}")
    if oversize:
        print("\n".join("  " + o for o in oversize))
        _fail(f"{len(oversize)} committed files exceed Cloudflare Pages' "
              "25 MiB limit - the deploy will silently show 'No deployment "
              "available'. Untrack them (git rm --cached) and gitignore.")
    _ok("no committed file exceeds 25 MiB")

    rules = [l for l in REDIRECTS.read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.strip().startswith("#")]
    if len(rules) > REDIRECT_CEILING:
        _fail(f"_redirects has {len(rules)} rules - past the ~{REDIRECT_CEILING} "
              "effective ceiling; rules beyond it are silently dropped.")
    margin = REDIRECT_CEILING - len(rules)
    (_ok if margin > 10 else print)(
        f"_redirects at {len(rules)}/{REDIRECT_CEILING} rules"
        + ("" if margin > 10 else f"  WARNING: only {margin} rules of headroom"))

    state = json.loads(POLL_STATE.read_text(encoding="utf-8"))
    blob = subprocess.run(["git", "cat-file", "blob", "HEAD:data/uap-data.csv"],
                          capture_output=True, cwd=ROOT).stdout
    if blob:
        got = hashlib.sha256(blob).hexdigest()
        if got != state.get("csv_sha256"):
            _fail(f"committed data/uap-data.csv blob sha256 {got[:16]}... != "
                  f"poll-state {state.get('csv_sha256', '')[:16]}... - the "
                  "served mirror is not byte-exact (check .gitattributes "
                  "-text rule, or the mirror is stale vs the latest drop).")
        _ok("served CSV mirror blob is byte-exact vs poll-state")
    print("pre-push: safe to push")


def main() -> int:
    cmds = {"pre-ingest": pre_ingest, "post-ingest": post_ingest,
            "pre-push": pre_push}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        print(f"usage: python -m pipeline.preflight [{'|'.join(cmds)}]")
        return 2
    cmds[sys.argv[1]]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
