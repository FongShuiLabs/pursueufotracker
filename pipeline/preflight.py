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
      re-verifies the served CSV mirror blob is byte-exact vs poll-state, and
      hard-fails on cluster/score-band count drift (see check-counts).

  python -m pipeline.preflight check-counts
      Recomputes every TOPIC_PAGES cluster size (vs its live match lambda) and
      the score-band totals in EXPECTED_SCORE_BANDS (vs the manifest), and fails
      on any drift, naming the prose to update. Guards against the 2026-07-16
      Drop 04 incident: "four files tied at 72" (really eight), "78 at 66"
      (really 92), and five stale cluster sizes. Runs as a warning in post-ingest
      and a hard gate in pre-push.

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

# Score-band totals that render as prose across the site. A drop that adds files
# at one of these scores silently drifts every page that hardcodes the count (the
# 2026-07-16 Drop 04 incident: "four files tied at 72" was really eight, "78 at 66"
# was really 92). When check-counts fails on a band, update BOTH the prose in the
# files below AND the number here, together.
EXPECTED_SCORE_BANDS = {72: 8, 70: 6, 66: 92, 65: 9}
_SCORE_BAND_PROSE = (
    "pipeline/build_site.py (_score_tier_phrase + _explain_witness_astronaut), "
    "generated/faq.html, generated/top-10.html, generated/glossary.html, "
    "generated/aaro-unresolved-uap.html, templates/top10.html.j2"
)


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

    # A drop that grows a cluster or a score band silently drifts every page that
    # hardcodes the count. Surface it here as a to-do (pre-push hard-blocks it).
    check_counts(warn_only=True)
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

    # Hard gate: never push cluster/score-band counts that drifted from the manifest.
    check_counts()
    print("pre-push: safe to push")


def _match(fn, f) -> bool:
    try:
        return bool(fn(f))
    except Exception:
        return False


def check_counts(warn_only: bool = False) -> None:
    """Recompute cluster + score-band counts from the manifest and flag drift vs
    the counts the site hardcodes in prose. Catches the 2026-07-16 Drop 04 class:
    TOPIC_PAGES cluster sizes and score-band totals that render across file pages,
    /faq, /top-10, /glossary, and the cluster essays.

    warn_only=True (post-ingest) prints drift without exiting, so a drop's expected
    count changes surface as a to-do. Strict (the `check-counts` subcommand and
    pre-push) hard-fails, so drifted counts can never be pushed live."""
    from . import build_site as bs
    files = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]

    def score(f):
        s = f.get("score") or {}
        return s.get("value") if isinstance(s, dict) else s

    problems: list[str] = []

    # 1. Every TOPIC_PAGES cluster: declared size vs actual lambda match count.
    #    Self-checking - imports the real match predicates, so a cluster that a
    #    drop grows (agency==CIA, score==66, dow-uap-pr, agency==DOE, ...) is caught.
    for tp in bs.TOPIC_PAGES:
        n = sum(1 for f in files if _match(tp["match"], f))
        if n != tp["size"]:
            problems.append(
                f'cluster {tp["slug"]}: declared size={tp["size"]} but {n} files '
                'match its lambda - update size + the "anchor" prose in build_site.py '
                "(and the cluster essay page if it prints the count)")

    # 2. Score-band totals referenced in prose (golden-value guard).
    counts = Counter(score(f) for f in files if score(f) is not None)
    for band, expected in sorted(EXPECTED_SCORE_BANDS.items(), reverse=True):
        actual = counts.get(band, 0)
        if actual != expected:
            problems.append(
                f"score band {band}: EXPECTED_SCORE_BANDS says {expected}, manifest "
                f"has {actual} - update the prose ({_SCORE_BAND_PROSE}) AND "
                "EXPECTED_SCORE_BANDS in preflight.py, together")

    if problems:
        for p in problems:
            print(f"  {'WARN' if warn_only else 'FAIL'}: {p}")
        if warn_only:
            print("  ^ count drift detected - fix the prose before pushing "
                  "(pre-push hard-blocks otherwise)")
            return
        sys.exit(1)
    _ok(f"{len(bs.TOPIC_PAGES)} cluster sizes + {len(EXPECTED_SCORE_BANDS)} "
        "score-band totals all match the manifest")


def main() -> int:
    cmds = {"pre-ingest": pre_ingest, "post-ingest": post_ingest,
            "pre-push": pre_push, "check-counts": check_counts}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        print(f"usage: python -m pipeline.preflight [{'|'.join(cmds)}]")
        return 2
    cmds[sys.argv[1]]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
