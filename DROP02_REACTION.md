# Drop 02 reaction playbook

Real-time playbook for when the auto-poller fires a `[NEW DROP]` GitHub issue. Designed so you can be live on Reddit/X within 4 hours of war.gov releasing Drop 02 and journalist emails out the same day, per INCOME_PLAN.md.

Drop 02 is expected ~2026-06-07 (could slip earlier or later). When the poller actually fires, follow this file top-to-bottom.

---

## Pre-flight checklist — DO BEFORE POSTING ANYTHING

The poller's `[NEW DROP]` GitHub issue gives you: new row count, delta vs. last snapshot, new CSV SHA-256. That is not enough to post a verified public claim. You need the manifest diff too.

1. Pull latest: `git pull`
2. Open `_scratch/uap-csv.csv` and confirm row count + SHA-256 match the issue body.
3. Run pipeline: `python -m pipeline.run all` (may take a while — videos transcribe, PDFs extract, OG cards regen).
4. `git diff data/manifest.json | head -200` — note the NEW file IDs (added blocks, not CSV row count changes; some delta could be re-rows of existing files like the May 11 revision was).
5. For each genuinely new file, open `generated/files/<id>.html` and confirm:
   - Title, score, summary all populated (no `[UNKNOWN]`, no empty fields)
   - Source URL (war.gov or DVIDS) resolves
   - SHA-256 hash present
6. Compute the **verified counts** below (do NOT trust the CSV row delta as "files added" — it includes re-rows).
7. Push to deploy.
8. Wait ~2 min for Cloudflare, then `curl -I https://pursueufotracker.com/files/<one-new-id>` and confirm `HTTP/2 200`.
9. Open `/drops/` and confirm Drop 02 detail page renders.
10. Only NOW fill the placeholders below and post.

If any step fails, do NOT post. Fix it first. A wrong public claim during a high-attention drop window costs more than a 4-hour delay.

---

## The verified-data block — FILL BEFORE POSTING

Pull every value from the `[NEW DROP]` issue and the manifest diff. **Never fill from memory or inference.** Hard Rule #7.

| Placeholder | Source | Value |
|---|---|---|
| `NEW_ROW_COUNT` | issue body / `data/poll-state.json` | |
| `DELTA_ROWS` | issue body (raw CSV row delta) | |
| `NEW_FILE_COUNT` | count of genuinely added file IDs in manifest diff (NOT row delta) | |
| `REMOVED_FILE_COUNT` | count of removed file IDs (likely 0; flag in body if non-zero) | |
| `RERROW_COUNT` | files that gained additional CSV rows but are the same PDF | |
| `NEW_TOP_TITLE` | the highest-scoring NEW file's title | |
| `NEW_TOP_SCORE` | its Anomalousness Index score | |
| `NEW_TOP_ID` | its file id (for the URL) | |
| `NEW_TOP_ONE_LINER` | one sentence from its manifest summary (verbatim or close, no embellishment) | |
| `DROP02_DATE` | date war.gov released Drop 02 (from poll-state `last_change_at`) | |
| `TIME_TO_DETECT` | minutes between war.gov release and poller catch (estimate from issue timestamp vs the prior poll) | |
| `DROP02_SLUG` | `<DATE>-drop-02` (e.g. `2026-06-07-drop-02`) | |
| `NEW_CSV_SHA256` | issue body | |

Helper one-liner to extract new file IDs from the manifest diff:

```bash
git diff data/manifest.json | grep -E '^\+\s+"id":' | sed -E 's/.*"id": "([^"]+)".*/\1/'
```

---

## 1. Reddit r/UFOs reaction post

**Subreddit:** r/UFOs · **Type:** Text post (NOT link post — mods auto-remove most) · **Best window:** within 4 hours of war.gov release, weekday 9am-1pm ET if possible.

### Title — pick one after filling placeholders

The first one is the strongest if `NEW_FILE_COUNT` is meaningful (5+). The second works for any size delta. Both must be true at post time.

> Drop 02 from war.gov just landed: `[NEW_FILE_COUNT]` new PURSUE UFO files. My auto-poller caught it `[TIME_TO_DETECT]` minutes after release. Here's the diff.

> War.gov just released Drop 02 of the Trump PURSUE UFO disclosure on `[DROP02_DATE]`. `[NEW_FILE_COUNT]` new files indexed, full diff vs. Drop 01.

### Body

```
Drop 02 landed at war.gov on [DROP02_DATE]. My automated tracker (public GitHub Action, polls war.gov every 30 min during US weekday business hours) caught it within [TIME_TO_DETECT] minutes. The site is already fully indexed with the new files - scoring, transcripts on any new videos, SHA-256 hashes verified against war.gov.

What actually changed, verified by URL-set comparison against the Drop 01 snapshot:
- [NEW_FILE_COUNT] new files added
- [REMOVED_FILE_COUNT] files removed (flag here if non-zero, otherwise: "Zero files removed")
- Total CSV row count: [NEW_ROW_COUNT] (delta of [DELTA_ROWS] from Drop 01's 158)
- New CSV SHA-256: [NEW_CSV_SHA256]

Highest-scoring new file:
**[NEW_TOP_TITLE]** - Anomalousness Index [NEW_TOP_SCORE]
[NEW_TOP_ONE_LINER]
https://pursueufotracker.com/files/[NEW_TOP_ID]

Site (Drop 02 fully indexed): https://pursueufotracker.com
Drop 02 detail page: https://pursueufotracker.com/drops/[DROP02_SLUG]
Full verified diff: https://pursueufotracker.com/changes

Same methodology as Drop 01: open six-axis rubric (anyone can recompute), no "probability of aliens" number (because that's not honestly computable from these files), SHA-256 hashes on every file so you can verify the mirror matches war.gov byte-for-byte. Full text search on every PDF. Whisper transcripts on every video.

Happy to AMA on the new files, the diff against Drop 01, or the methodology.
```

### After posting
- Reply to the top 3-5 comments within the first hour (Reddit algorithm rewards early engagement).
- Pin a comment linking `/changes` so the verified diff is the most visible secondary click.
- If a comment surfaces something I missed, edit the post with an UPDATE: line rather than starting fresh. Don't delete-and-repost.

---

## 2. X / Twitter thread for Drop 02

Best window: same day, 10am-1pm ET. Tag `@ross_coulthart @LueElizondo @TheDebrief` on the last tweet only (tagging on the first tweet tanks the algorithm).

### Tweet 1 (hook)

> Drop 02 of the Trump PURSUE UFO release just landed at war.gov.
>
> [NEW_FILE_COUNT] new files. My auto-poller caught it [TIME_TO_DETECT] minutes after release. Already indexed, scored, and SHA-256 verified on the site. 🧵
>
> https://pursueufotracker.com

### Tweet 2 (the verified diff)

> What's actually new, verified by URL-set comparison against the Drop 01 snapshot:
>
> • [NEW_FILE_COUNT] files added
> • [REMOVED_FILE_COUNT] removed
> • CSV row count: [NEW_ROW_COUNT] (delta [DELTA_ROWS])
> • New SHA-256: [NEW_CSV_SHA256]
>
> Full diff: pursueufotracker.com/changes

### Tweet 3 (the headline new file)

> The highest-scoring new file in Drop 02:
>
> [NEW_TOP_TITLE]
> Anomalousness Index: [NEW_TOP_SCORE]
>
> [NEW_TOP_ONE_LINER]
>
> pursueufotracker.com/files/[NEW_TOP_ID]

### Tweet 4 (methodology reminder for new followers)

> For anyone new: the score is open six-axis rubric, weights sum to 1.00, published JSON. It's evidentiary weight that the encounter remains unexplained after conventional analysis. NOT a probability of aliens (that number isn't honestly computable).
>
> Rubric: pursueufotracker.com/data/scoring-rubric.json

### Tweet 5 (close)

> Site has the full Drop 02 detail page, the Drop 01 vs 02 diff, and SHA-256 verification on every file. Public domain so anything is free to embed, quote, screenshot.
>
> @ross_coulthart @LueElizondo @TheDebrief - methodology + diff are open if useful.
>
> pursueufotracker.com

---

## 3. Journalist update email — same-day send

One template, lightly personalized in the opening line per journalist. Send 4 separate emails (NOT a blast — blasts get reported as spam).

### Coulthart opener
> Hi Ross, follow-up to the May 8 PURSUE tracker note - Drop 02 just landed.

### Knapp opener
> Hi George, the auto-poller on the PURSUE tracker just fired - Drop 02 is live.

### Bender / McMillan opener
> Hi [Bryan/Tim], Drop 02 of the PURSUE UAP release just landed at war.gov - flagging because of the timing.

### Sprague opener
> Hi Ryan, the PURSUE auto-poller fired this morning - Drop 02 is live.

### Body (same for all four)

```
[Personalized opener above]

Detected by my auto-poller [TIME_TO_DETECT] minutes after war.gov pushed it. Already indexed, scored, transcripted, and SHA-256 verified on pursueufotracker.com.

What's verifiably new (URL-set diff against the Drop 01 snapshot):
- [NEW_FILE_COUNT] new files added
- [REMOVED_FILE_COUNT] removed
- CSV row count: [NEW_ROW_COUNT] (delta of [DELTA_ROWS] from Drop 01)
- New CSV SHA-256: [NEW_CSV_SHA256]

Highest-scoring new file:
[NEW_TOP_TITLE] - Anomalousness Index [NEW_TOP_SCORE]
[NEW_TOP_ONE_LINER]
https://pursueufotracker.com/files/[NEW_TOP_ID]

Useful links:
- Drop 02 detail page: https://pursueufotracker.com/drops/[DROP02_SLUG]
- Full verified diff: https://pursueufotracker.com/changes
- Open scoring rubric (auditable, weights sum to 1.00): https://pursueufotracker.com/data/scoring-rubric.json
- Press kit: https://pursueufotracker.com/press

Public domain on every file (17 U.S.C. § 105) so anything is free to embed, quote, or screenshot. Happy to send raw diff data, hop on a call to walk through the methodology, or just be a free factchecker on file claims.

[Your name]
[Your phone]
[Your email]
```

---

## 4. On-site banner for the existing audience

If you have a banner mechanism (currently none — could be a one-liner above the `<main>` on index.html). If not, the homepage hero already updates because the manifest changes — the new top scorer will show on the homepage automatically after the rebuild.

Manual addition (optional, ~5 min): add a yellow notice band above the file grid:

```html
<div style="max-width:1100px;margin:24px auto 0;padding:14px 20px;background:rgba(82,255,180,.08);border:1px solid rgba(82,255,180,.3);border-radius:8px;text-align:center;font-family:'JetBrains Mono',monospace;font-size:13px;color:#52ffb4">
  🔔 DROP 02 LIVE - [NEW_FILE_COUNT] new files indexed [DROP02_DATE]. <a href="/drops/[DROP02_SLUG]" style="color:#52ffb4;text-decoration:underline">See the diff →</a>
</div>
```

Remove the banner after ~1 week or when Drop 03 lands.

---

## 5. Re-ping IndexNow / search engines

The pipeline's `index-now` stage runs automatically as the last stage of `python -m pipeline.run all`. It pings Bing / Yandex / Naver / Seznam with the changed URLs. Confirm in the pipeline log that the ping returned 200.

For Google: nothing to ping (Google deprecated their submit URL). The fresh sitemap.xml + GSC's "Validate fix" / re-crawl request handles it. If you want to nudge Google, in Google Search Console > Sitemaps, re-submit `sitemap-index.xml`.

---

## What NOT to do

- Don't post any number you haven't pulled fresh from the `[NEW DROP]` issue or the manifest diff. The May 11 revision narrative got woven into Drop 01 marketing copy on bad inference and had to be cleaned up later. Don't repeat.
- Don't claim files are "new" based on CSV row delta alone — the May 11 revision showed war.gov can add CSV ROWS without adding actual new FILE URLs. Always verify against URL-set diff (already what `/changes` does).
- Don't add any commercial framing (Amazon links, sponsor framing) unless those relationships are active that day per Hard Rule #8.
- Don't delete an underperforming post and repost. Reddit/X notice and penalize.
- Don't tag journalists in the first tweet of the thread (algorithm tanks it). Tag in the last tweet only.

---

## Last updated

2026-05-29 — initial draft pre-Drop-02, per INCOME_PLAN.md week-of-Jun-1 deliverable. Will need a 5-min re-verify pass the morning Drop 02 actually lands to confirm all the URL slugs, the auto-poller's output format, and the Coulthart / Knapp / Bender / Sprague addresses are still current.
