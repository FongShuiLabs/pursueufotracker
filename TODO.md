# PURSUE UFO Tracker — Action Queue

**Last updated: 2026-05-09 (end of build session)**

---

## 🔥 TOMORROW (2026-05-10) — Anthony to do

### 1. Bing Webmaster Tools (5 min)

Bing indexes faster than Google for new sites and feeds DuckDuckGo. We've already done Google Search Console; this is the parallel for Bing/DuckDuckGo audiences.

**Steps:**
1. Open https://www.bing.com/webmasters
2. Sign in with your Microsoft account (or click "Sign in with Google" — accepts both)
3. On the welcome screen, click **"Import from Google Search Console"**
4. Authorize Bing to read your GSC properties
5. Pick `pursueufotracker.com` from the list
6. Click **Import**

Done in ~10 seconds. Bing copies the verified property AND the sitemap automatically.

If "Import from GSC" isn't offered:
- Click **Add a site** → enter `https://pursueufotracker.com`
- Verify via DNS TXT (same Cloudflare flow as the Google verification)
- Then Sitemaps → submit `https://pursueufotracker.com/sitemap.xml`

### 2. R2 setup (5 min in Cloudflare UI)

Unlocks direct video streaming + HD downloads from your domain (currently fall back to war.gov links).

**Steps:**
1. Cloudflare dashboard → **R2 Object Storage** → **Create bucket** → name: `pursueufotracker-media`
2. Bucket settings → **Connect Domain** → `media.pursueufotracker.com`
3. **Manage R2 API Tokens** → **Create API Token** → name: `pursueufotracker-uploader` → permission: **Object Read & Write** → bucket: `pursueufotracker-media`
4. Copy the 4 strings shown (only time they'll be displayed):
   - Access Key ID
   - Secret Access Key
   - Endpoint URL
   - Account ID

Paste those 4 strings to me. I run `python -m pipeline.upload_r2` and ~5 min later all 161 files are on your CDN. Templates already wire `mirror_url` so the moment R2 lands, every file detail page becomes a real player + HD download.

---

## 🟡 THIS WEEK

### 3. Outreach launch (60-90 min)

**Only after R2 is live** so the site is feature-complete. Pre-drafted material in [OUTREACH.md](OUTREACH.md):
- X / Bluesky launch thread (5 tweets)
- Hacker News Show HN
- Reddit r/UFOs launch post (commit to replying for 4 hours)
- 5 UAP-beat journalist emails (Coulthart, Knapp, Bender, McMillan, Blumenthal)
- 5 UAP YouTube creator emails (Need to Know, That UFO Podcast, Project Unity, The Why Files, Theories of Everything)

### 4. Buttondown email signup (5 min)

For email subscribers. Get a username at buttondown.email. Tell me the username. I swap `CHANGEME` in index.html, push, Cloudflare auto-deploys. Welcome email is pre-drafted at [data/welcome-email.md](data/welcome-email.md).

### 5. Apply for Google AdSense (5 min)

Application takes 1-30 days. Apply now so it's approved by week 4 when traffic is meaningful. See [MONETIZE.md](MONETIZE.md) for full roadmap.

---

## 🟢 NEXT 1-2 WEEKS

- Wire on-site search bar to the existing search index (~10 min me-work; ask "wire search")
- Generate TikTok/Reels vertical clips from the 28 videos (auto-pipeline already built)
- Submit to Disclosure aggregators
- Monitor Search Console for "Couldn't fetch" → resolves on its own

---

## ✅ DONE 2026-05-09

- ✅ Domain registered (pursueufotracker.com)
- ✅ GitHub repo: FongShuiLabs/pursueufotracker
- ✅ Cloudflare Pages deployed, custom domain live
- ✅ war.gov CSV catalog parsed, 161-file manifest generated
- ✅ DVIDS API integrated for all 28 videos (HD MP4s + captions + thumbnails)
- ✅ All 161 files downloaded locally (3.6 GB)
- ✅ All 119 PDFs full-text extracted
- ✅ All 161 SHA-256 hashed
- ✅ All 161 OG share cards generated
- ✅ Verdict page, Top 10 page, Press kit, Drops tracker, API endpoints
- ✅ Schema.org Dataset + FAQ markup
- ✅ AI use disclosure (per-file badges + dedicated section + verdict Q&A)
- ✅ Monetization infrastructure (dormant; toggles in pipeline/config.py)
- ✅ Google Search Console verified, sitemap submitted, homepage indexed
- ✅ Schema warnings fixed (creator type, license URL)
- ✅ Homepage content expansion (intro, drop summary, FAQ, glossary)

---

When in doubt, run: `python -m pipeline.run --from build` then `git add -A && git commit -m "..." && git push`. Cloudflare auto-deploys in ~30 sec.
