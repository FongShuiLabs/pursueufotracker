# PURSUE UFO Tracker — Action Queue

**Last updated: 2026-06-03** (Drop 02 checkpoint reminder added; 4 new topic pages shipped this week; war.gov still unchanged 22 days)

---

## 📅 CHECKPOINT — Saturday 2026-06-07 (projected Drop 02 window)

Set 2026-06-03 by operator request. Calendar event also on `anthony.fong.esq@gmail.com` for Sat 6/7 9:00 AM ET.

**Step 1 — did Drop 02 actually land?**
- Check `data/poll-state.json` `last_change_at` vs the 6/3 baseline `2026-05-12T23:19:37Z` (row_count was 158)
- Or look for a `[NEW DROP]` auto-poller issue on the repo

**Step 2A — IF Drop 02 landed:** Follow [`DROP02_REACTION.md`](DROP02_REACTION.md) end-to-end. PLUS post a short UPDATE comment on the original r/UFOs viral thread (Aclosmurf account, ~5/20): *"Update — Drop 02 landed [DATE]. [N] new files indexed, scored, SHA-256 verified. Full diff: pursueufotracker.com/changes"* — and drop the homepage banner from DROP02_REACTION.md § 4.

**Step 2B — IF Drop 02 did NOT land:** Skip the full reaction post. Post a short status-check on the original r/UFOs thread: *"Status check [DATE]: war.gov still at 158 rows, no new files since May 11. Auto-poller still active. /changes has the verified diff."*

**Hard Rule #7** — every count/date in the public posts must come from live-pulled `poll-state.json` or the `[NEW DROP]` issue body. No memory, no inference. (The May 11 narrative got mis-told as "5 removed / 3 added / 28 renamed" the first time around — don't repeat.)

Also check on 6/7: r/UFOscience post (was 5/27, draft in DISTRIBUTION.md if still unposted), AdSense site review (~day 16 of the 1-14 window).

---

## 🔥 OPEN ITEMS THAT NEED YOU (operator UI / account actions)

These can't be done by Claude. Most are ~5 min each.

### 1. Reddit pending posts

- **r/UFOscience** — was scheduled Wed 5/27, overdue. Draft is paste-ready in [DISTRIBUTION.md](DISTRIBUTION.md) lines 340-341 (title) + 46-109 (body, verified-corrected). Best window: Tue-Thu 9-10am ET. Friday/weekend posting works but with softer engagement.
- **r/Python pipeline post** — eligible since 5/28. Draft was in the 5/23 chat thread (not yet saved to file). Space ≥48 hrs from r/UFOscience to avoid cross-promo flag on the `Aclosmurf` account.
- **r/datascience** — was scheduled 5/24. Status still unknown to Claude. Confirm whether it posted; if not, decide skip vs ship.

### 2. AdSense (developer@fongshuilabs.com inbox)

- **Site review status** — added 2026-05-22, **day 7** of the 1-14 window today. Approval email may have landed; quick inbox check.
- **Auto Ads UI config** — settings persist through review and activate on approval. Per the 5/22 plan: ad load LOW for pursueufotracker.com, disable Vignette + Anchor + Side rail; ad load Medium for glp1cost.org. AdSense → Ads → By site → pencil icon.

### 3. Cloudflare Email Routing for pursueufotracker.com (~5 min)

The role addresses on `/contact` (`contact@`, `press@`, `privacy@`, `legal@`, `tips@`) currently BOUNCE. CF dashboard → pursueufotracker.com zone → Email → enable → catch-all → developer@fongshuilabs.com.

### 4. Amazon Associates signup (~5 min)

Unlocks the affiliate lever (currently blocked by Hard Rule #8 until approved). Account email developer@fongshuilabs.com, payee Fong Shui Labs LLC EIN, TD business 714. Wait for approval before adding any live links.

---

## 🛰️ UPCOMING REAL-TIME EVENT — Drop 02 (~2026-06-07)

When the auto-poller fires a `[NEW DROP]` GitHub issue: **follow [DROP02_REACTION.md](DROP02_REACTION.md) top-to-bottom**. It has the pre-flight checklist, the verified-data placeholder block, and paste-ready Reddit/X/journalist templates.

Per INCOME_PLAN.md cadence around the drop:
- **Wed 6/3** — pre-Drop-02 reminder post: "Drop 02 expected in ~4 days, here's how we'll catch it."
- **Day of drop** — DROP02_REACTION.md flow.

---

## 🟢 NICE-TO-HAVE / WHEN-YOU-FEEL-LIKE-IT

- **Buttondown email signup** — if email capture matters. Subscribe form is currently a safe-fail RSS/GitHub-Watch placeholder. Welcome email pre-drafted at [data/welcome-email.md](data/welcome-email.md) (already updated to clean drop URL).
- **Video transcripts** — 28 videos still need Whisper transcription. `python -m pipeline.run transcribe` takes hours on CPU.
- **TikTok/Reels clips** — `pipeline.clip_generator` is built but needs ffmpeg in PATH.
- **Methodology page differentiator paragraph** — your call whether to add explicit "why us vs pursueindex.com" framing.
- **Clean /drops/ canonical for Drop 01** — already done this session (commit 7645667). Same pattern applies automatically to Drop 02.

---

## ✅ DONE since 2026-05-09 (the launch + post-launch work)

Most of the items the original TODO listed under "tomorrow" and "this week" have shipped. Highlights of what's been done:

- **Launch shipped** — site live, Reddit r/UFOs went viral 5/20-21 (3.1k pageviews/day spike).
- **War.gov auto-poller** — GitHub Action polling every 30 min weekday business hours (`/`hourly off-hours), `[NEW DROP]` issue on real change. Public repo (Actions minutes free).
- **War.gov May 11 revision** — caught within hours, verified diff published on `/changes` (zero PDFs added/removed; CSV restructured from 161 → 158 rows by adding multi-row representations of 9 PDFs + 1 slug rename).
- **D20 SHA-256 byte-identity verification** — proved the May 8 → May 23 D20 PDF was an identical-bytes storage rename, not a content change.
- **Monetization stack** — Auto Ads script live sitewide (pub-7264251466939264), site review applied 5/22.
- **Analytics** — Plausible Business tier, Stats API enabled (`pipeline/plausible_stats.py`).
- **Google Workspace** activated on fongshuilabs.com (`developer@fongshuilabs.com` is the daily login for AdSense/Plausible).
- **SEO push** (this session, 2026-05-28/29) — Twitter Cards on the 3 static pages that lacked them; clean `/drops/` URLs across template + sitemap + _redirects; file-page breadcrumb deep-links to category hubs (161 new file→hub links concentrating equity); category hubs cross-link each other + 6 editorial pages; homepage hero + JSON-LD corrected to verified top-5 (Hard Rule #7); zero redirect-inducing internal links sitewide.
- **DISTRIBUTION.md cleanup** (this session) — top-5 rewritten to match live data; UAE "4 min 57 sec" → real durations; Apollo "65" removed from top-5; X thread restructured; YouTube script restructured; Bender email Greece disposition corrected; r/conspiracy title softened.
- **DROP02_REACTION.md created** (this session) — real-time playbook for the next drop, every claim placeholder-driven.

---

## Pipeline shortcut

Anything site-content related: `python -m pipeline.run --from build` then commit and push. Cloudflare auto-deploys in ~30 sec, full pipeline including IndexNow ping is `python -m pipeline.run all`.
