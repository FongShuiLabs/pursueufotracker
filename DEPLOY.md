# Going Live

The whole site is static. Every option below works.

## Recommended: Cloudflare Pages + R2 (free for our scale)

**Why:** Cloudflare's CDN has 300+ POPs worldwide, R2 has zero egress fees, both are free at our expected volume. Built for the audience we're serving (global, mobile, bandwidth-constrained).

### One-time setup (15 min)

1. **Domain.** Register one. Suggestions, ranked:
   - `pursuefiles.com` - matches the program name; durable
   - `trumpufofiles.com` - search-intent direct hit; high CTR
   - `pursue-tracker.com` - branded; works long-term
   - `uapdrops.com` - generic enough to outlast PURSUE
   - `pursuetracker.org` - .org reads as authoritative; cite-friendly
   Cost: $10-12/yr at Cloudflare Registrar (no markup).

2. **GitHub repo.** Push the project:
   ```powershell
   cd C:\Users\<your-username>\Desktop\ufo-disclosure-site
   git init
   git add .
   git commit -m "Initial commit - Trump PURSUE Tracker"
   gh repo create pursue-tracker --public --source=. --push
   ```
   The `.gitignore` already excludes `_scratch/`, `downloads/`, `generated/manifest.json` etc., so private inputs stay local.

3. **Cloudflare Pages.** dash.cloudflare.com → Workers & Pages → Create → "Pages" → Connect to Git → pick the repo. Build settings:
   - Build command: `pip install -r requirements.txt && python -m pipeline.run --from score`
   - Output directory: `.` (root - the site is at root, generated/ is below)
   - Environment variables: leave empty for now
   First build takes 2-3 min. Every subsequent `git push` triggers a redeploy.

4. **Custom domain.** Pages dashboard → Custom domains → Add → enter your domain. Cloudflare wires the DNS automatically.

5. **R2 for HD media.** When real PURSUE files are downloaded:
   - Cloudflare dash → R2 → Create bucket: `pursue-files`
   - Set custom domain `media.pursuefiles.com` (or whatever)
   - Update `pipeline/config.py` SITE_URL and add R2_MEDIA_URL constant
   - Modify download flow to upload to R2 instead of local `downloads/`
   - Templates already reference `f.local_path`; swap to R2 URL when present.

### Ongoing: each new PURSUE drop

When a new drop lands:
1. Save the war.gov page → `_scratch/war-gov-ufo-DROP-N.html`
2. Append a new entry to `data/drops.json`
3. Run `python -m pipeline.run all`
4. `git add . && git commit -m "Drop N" && git push`
5. Cloudflare auto-rebuilds. New drop is live in ~3 min.
6. Subscribers get notified via the email/RSS automation (below).

## Email + RSS subscriber pipeline

### Buttondown (recommended - free up to 100 subscribers, $9/mo to 1000)

1. Sign up at buttondown.email - get the embed code.
2. Replace `CHANGEME` in [index.html](index.html) (search "buttondown") with your username.
3. In Buttondown settings, enable "RSS-to-email" and point at `https://yourdomain.com/generated/feed.xml`.
4. Every new drop = new RSS entry = automatic email blast to subscribers.

### Beehiiv (alternative - free unlimited subscribers; sells your audience to advertisers, which is the trade)

Same setup, swap the embed URL.

### MailerLite / ConvertKit / Substack

All work; same pattern.

## Analytics

Plausible Analytics, free if you self-host on Cloudflare Workers, $9/mo cloud-hosted. Privacy-first, no cookies, GDPR-clean. Adds to trust signal.

```html
<!-- add to index.html <head> after deploy -->
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

## Search Console submissions (do these on launch day)

1. **Google Search Console** - search.google.com/search-console - add property, verify via DNS TXT record (Cloudflare makes this one click), submit `sitemap.xml`.
2. **Bing Webmaster Tools** - bing.com/webmasters - same flow, submit sitemap.
3. **DuckDuckGo** - they crawl from Bing; covered by step 2.

Expect first indexing within 24-48 hours.

## Rolling-release polling (optional - higher effort, big payoff)

You want to be the FIRST to know when a new drop lands. Two options:

### Option A: Manual poll (free, 30 sec/day)

Open war.gov/UFO once a day. Save the page if anything changed. Run pipeline. Done.

### Option B: Automated poll (one-time setup, ~30 min)

A scheduled task in Windows Task Scheduler that runs `tools/poll_war_gov.py` daily at 9am ET, computes hash of the page, and pings you on Discord/Slack/email if the hash changed. Tracks stays-the-same vs. new-drop signal.

This requires solving the Akamai 403 we hit earlier - the answer is running the poller from your Windows session (your browser-cookie context isn't blocked) via a Selenium-driven Edge or Chrome instance, OR via the Chrome MCP if you install the extension. I can write either; flag which you want.

## Launch-day checklist

```
[ ] Domain registered
[ ] GitHub repo pushed
[ ] Cloudflare Pages connected, first build green
[ ] Custom domain wired
[ ] Buttondown configured, embed code updated
[ ] Plausible analytics added
[ ] Google Search Console - verified, sitemap submitted
[ ] Bing Webmaster - verified, sitemap submitted
[ ] X / Bluesky launch thread queued (see OUTREACH.md)
[ ] r/UFOs launch post queued
[ ] Hacker News "Show HN" queued
[ ] 5 UAP-beat journalists emailed (see OUTREACH.md)
[ ] 5 UAP YouTube creators emailed (see OUTREACH.md)
```

If you do all of this in one focused day, you're discoverable globally within 48 hours.
