# Drop reaction playbook (release-agnostic)

Real-time playbook for when the auto-poller fires a `[NEW DROP]` GitHub issue.
Designed so you can be live on Reddit/HN/X within a few hours of war.gov releasing
a new PURSUE drop, with every public number verified first.

**This file applies to every drop** (it was `DROP02_REACTION.md` through July 2026;
renamed because it is not Drop-02-specific). Fill the placeholders fresh each time.

**Status (2026-07-17):** four releases so far - Drop 01 (May 8), 02 (May 22), 03
(Jun 12), 04 (Jul 10). Gaps have been +14/+21/+28 days, so Drop 05 would land
early-to-mid August 2026 *if* the cadence holds (extrapolation, not an announcement).
The last drop's actual, proven Reddit post is archived in `_scratch/reddit-drop04.md` -
adapt that format; it is the format that has worked.

---

## Pre-flight checklist - DO BEFORE POSTING ANYTHING

The poller's `[NEW DROP]` issue gives you a row count, a delta, and a new CSV
SHA-256. That is NOT enough to post - CSV rows are not the same as files (war.gov
has added multi-row representations of existing PDFs before). You need the manifest
diff and a clean guard run.

1. `git pull`
2. **`python -m pipeline.preflight pre-ingest`** - fetches a verified-fresh CSV
   from war.gov (curl_cffi chrome-impersonation + session warmup) into
   `_scratch/uap-csv.csv` and hard-fails unless its SHA-256 matches `data/poll-state.json`.
   NEVER skip: `pipeline.run all` does NOT auto-fetch, and a stale scratch CSV once
   silently re-parsed an old schema.
3. **`python -m pipeline.run all`** - may take a while (videos transcribe, PDFs
   extract, OG cards regen). Note: `all` runs both the legacy `download` and
   `download-manifest` stages; the download.py id-corruption bug was fixed 2026-07-11,
   and the post-ingest guard below is the backstop if it ever recurs. War.gov may
   also add CSV columns per drop (Drop 03 added "Featured") - `parse_csv` maps by
   column NAME, so new columns are fine, but eyeball the new agency labels.
4. **`python -m pipeline.preflight post-ingest`** - hard-fails if any previously-live
   file id vanished (the 196-renamed-ids incident), junk OTHER-agency entries
   appeared (the 166-junk-pages incident), a type count shrank (the video-collapse
   incident), or new files are missing title/sha256/score. **It also now runs a
   count-drift WARNING (see step 6).** Only after the hard checks pass, note the
   genuinely NEW file IDs:
   ```bash
   git diff data/manifest.json | grep -E '^\+\s+"id":' | sed -E 's/.*"id": "([^"]+)".*/\1/'
   ```
5. Spot-check 2-3 new `generated/files/<id>.html`: title/score/summary populated
   (no empty fields), source URL resolves, SHA-256 present.
6. **RECONCILE COUNTS (the Drop-04 lesson - do not skip).** Post-ingest will print
   `WARN: score band ...` / `WARN: cluster ...` lines, because a drop almost always
   adds files at a score band or a TOPIC_PAGES cluster. For each warning:
   - Update the hardcoded count in the prose it names (score bands render in
     `pipeline/build_site.py` `_score_tier_phrase` + `_explain_witness_astronaut`,
     and in `generated/faq.html`, `generated/top-10.html`, `generated/glossary.html`,
     `generated/aaro-unresolved-uap.html`, `templates/top10.html.j2`; cluster sizes
     are the `size`/`anchor` fields in `build_site.py` TOPIC_PAGES).
   - Update `EXPECTED_SCORE_BANDS` in `pipeline/preflight.py` and the TOPIC_PAGES
     `size` to the new true values.
   - Re-run `python -m pipeline.run build` then `python -m pipeline.preflight check-counts`
     until it prints `ok: ... all match the manifest`. Also sweep hand-authored
     statics for any per-agency / total counts you're touching (see the drift memory).
7. **APPEND THE NEW DROP TO `data/drops.json`** (the `/drops`-lags lesson - it does
   NOT auto-populate). Add an entry with the verified date, file_count (NEW files,
   not row delta), type breakdown, and a summary written from the manifest. Then
   `python -m pipeline.run build-drops`. Confirm `/drops/` shows the new drop and
   the per-drop page renders. Drop URLs are **date-first**: `/drops/YYYY-MM-DD-drop-0N`
   (e.g. `/drops/2026-07-10-drop-04`), never built from the drops.json id.
8. **`python -m pipeline.preflight pre-push`** - hard-gates >25MiB deploy-killers,
   the `_redirects` ~100-rule ceiling, CSV-mirror byte drift, AND count drift.
   Then push to deploy.
9. Wait ~2 min for Cloudflare, then verify live:
   `curl -I https://pursueufotracker.com/files/<one-new-id>` -> `HTTP/2 200`,
   and open `/drops/<slug>`.
10. Update the two standing cadence claims to include this drop: the FAQ "When will
    more UFO files be released?" answer (visible + JSON-LD twin) and the `/drops`
    meta (`templates/drops_index.html.j2`), then re-run `build-drops`. Also refresh
    `/aaro-unresolved-uap`'s "latest annual report" section if AARO news moved.
11. Only NOW fill the placeholders below and post.

If any step fails, do NOT post. A wrong public claim during a high-attention drop
window costs far more than a two-hour delay.

---

## The verified-data block - FILL BEFORE POSTING

Pull every value from the `[NEW DROP]` issue and the manifest diff. **Never fill
from memory or inference (Hard Rule #7).**

| Placeholder | Source | Value |
|---|---|---|
| `DROP_N` | which release this is (05, 06, ...) | |
| `DROP_DATE` | war.gov release date (poll-state `last_change_at`) | |
| `DROP_SLUG` | `YYYY-MM-DD-drop-0N` | |
| `NEW_FILE_COUNT` | count of genuinely added file IDs in the manifest diff (NOT row delta) | |
| `REMOVED_FILE_COUNT` | removed file IDs (usually 0; flag if non-zero) | |
| `NEW_TOTAL` | archive total after this drop (manifest length) | |
| `PRIOR_TOTAL` | archive total before this drop | |
| `NEW_TYPE_BREAKDOWN` | e.g. "23 videos, 14 documents, 3 images" (from the diff) | |
| `NEW_TOP_TITLE` / `NEW_TOP_SCORE` / `NEW_TOP_ID` | highest-scoring NEW file | |
| `NEW_TOP_ONE_LINER` | one sentence from its manifest summary (verbatim-ish, no embellishment) | |
| `NEW_CSV_SHA256` | issue body / poll-state | |
| `TIME_TO_DETECT` | minutes between release and poller catch (issue timestamp vs prior poll) | |
| `HEADLINE_HOOK` | the single most interesting NEW file/angle - often the strongest post lead | |

---

## 1. Reddit r/UFOs reaction post (highest impact)

**Subreddit:** r/UFOs · **Type:** Text post (NOT link post - mods auto-remove most) ·
**Window:** weekday 9am-1pm ET, within a few hours of release. Post from the Aclosmurf
account; space >=48h from other posts on it.

Adapt `_scratch/reddit-drop04.md` (the proven Drop-04 format: lead with the single
most striking file/angle, then the verified diff, then the honest framing). Skeleton:

### Title
> War.gov just dropped Drop `[DROP_N]` of the PURSUE UFO disclosure - `[NEW_FILE_COUNT]` new files. `[HEADLINE_HOOK]`. My auto-poller caught it `[TIME_TO_DETECT]` min after release; full diff indexed.

### Body
```
Drop [DROP_N] landed at war.gov on [DROP_DATE]. My automated tracker (public GitHub Action, polls war.gov every 30 min on weekday business hours) caught it and the site is fully indexed - new files scored, audio videos transcribed, every file SHA-256 verified against war.gov's own bytes.

What actually changed, verified by URL-set comparison against the prior snapshot:
- [NEW_FILE_COUNT] new files added ([NEW_TYPE_BREAKDOWN])
- [REMOVED_FILE_COUNT] files removed
- Archive total: [NEW_TOTAL] files (up from [PRIOR_TOTAL])
- New CSV SHA-256: [NEW_CSV_SHA256]

[The headline file, 2-4 sentences, quoting the released record where possible. If a
viral claim is circulating, contrast it with what the government's own paperwork says
next to the file - that debunk-with-primary-sources angle is what worked for Drop 04.]

Highest-scoring new file:
[NEW_TOP_TITLE] - Anomalousness Index [NEW_TOP_SCORE]
[NEW_TOP_ONE_LINER]
https://pursueufotracker.com/files/[NEW_TOP_ID]

Full Drop [DROP_N] diff: https://pursueufotracker.com/drops/[DROP_SLUG]
Site: https://pursueufotracker.com

Same methodology every drop: open six-axis scoring rubric anyone can recompute, no "probability of aliens" number (not honestly computable from these files), SHA-256 on every file so you can verify the mirror matches war.gov byte-for-byte, full-text search on the PDFs, and Whisper transcripts on the audio-bearing videos (most PURSUE videos are silent sensor/FLIR captures, so transcripts are on the NASA audio files).
```

### After posting
- Reply to the top 3-5 comments within the first hour (algorithm rewards early engagement).
- Pin a comment linking `/drops/[DROP_SLUG]` so the verified diff is the top secondary click.
- Corrections go in an `UPDATE:` line on the post - never delete-and-repost.

---

## 2. Show HN + X thread (same day)

- **Show HN** (Mon-Thu 8-10am ET): title "Show HN: I indexed all `[NEW_TOTAL]` Trump
  PURSUE UFO files with transcripts and an open scoring rubric", URL the homepage,
  first comment adapted from `_scratch/READY-TO-FIRE.md` § 2 (keep its "silent sensor
  videos" transcript honesty). Reply to every top-level comment within ~4 hours.
- **X thread** (10am-1pm ET): adapt `_scratch/READY-TO-FIRE.md` § 3. Tag journalists
  on the LAST tweet only, never the first. Update the counts to this drop.

---

## 3. Email the subscriber list (when the ESP is live)

If email capture is wired (Substack/Buttondown - check `.claude/accounts.md`), send
a short "Drop `[DROP_N]` indexed, here's what changed" email the same day: the verified
diff block above + the headline file + the `/drops/[DROP_SLUG]` link. The welcome-email
draft at `data/welcome-email.md` shows the voice. This is the highest-retention channel -
a spike's traffic is anonymous, but a subscriber is reachable for the NEXT drop.

**Retired:** the journalist-pitch lane (Coulthart/Knapp/Bender/Sprague) was dropped
2026-07-02. `/press` still exists for inbound press; we do not send outbound pitches.

---

## 4. On-site

The homepage auto-updates from the manifest (new top-scorer, drop panels) after the
rebuild - no manual edit required. Optional yellow banner above the file grid on
`index.html` (remove after ~1 week or when the next drop lands):
```html
<div style="max-width:1100px;margin:24px auto 0;padding:14px 20px;background:rgba(82,255,180,.08);border:1px solid rgba(82,255,180,.3);border-radius:8px;text-align:center;font-family:'JetBrains Mono',monospace;font-size:13px;color:#52ffb4">
  🔔 DROP [DROP_N] LIVE - [NEW_FILE_COUNT] new files indexed [DROP_DATE]. <a href="/drops/[DROP_SLUG]" style="color:#52ffb4;text-decoration:underline">See the diff →</a>
</div>
```

## 5. Search engines

`index-now` runs automatically as the last stage of `pipeline.run all` (pings
Bing/Yandex/Naver/Seznam); confirm the 200 in the log. Google: re-submit
`sitemap-index.xml` in GSC, and optionally URL-inspect -> Request Indexing the new
`/drops/[DROP_SLUG]` and top new file page (the GSC inspect UI is flaky under
automation - IndexNow + natural recrawl cover it if the button won't cooperate).

---

## What NOT to do

- Don't post any number you haven't pulled fresh from the `[NEW DROP]` issue or the
  manifest diff. CSV row delta != files added.
- Don't push with drifted counts - `pre-push` now hard-blocks it, but reconcile in
  step 6 so you're not stuck at the push gate under time pressure.
- Don't forget `data/drops.json` (step 7) - without it `/drops` silently shows the
  old set even though the file pages are live.
- Don't claim "transcripts on every video" - most are silent sensor captures.
- Don't add commercial framing (affiliate/sponsor) unless the relationship is active
  that day (Hard Rule #8).
- Don't delete-and-repost an underperformer; don't tag journalists in tweet 1.

---

## Last updated

2026-07-17 - rewritten release-agnostic from the Drop-02-era draft. Folded in the
Drop 03-04 lessons: the count-drift reconciliation step (now guarded by
`preflight check-counts`), the mandatory `drops.json` hand-append, the
download.py/post-ingest backstops, the date-first drop URL, the standing cadence-claim
refresh, the retired journalist lane, and the corrected "silent videos" transcript
framing. Re-verify the Aclosmurf posting cadence and the `_scratch/reddit-drop04.md`
format the morning a drop actually lands.
