# Income Plan for pursueufotracker.com

Honest, sequenced, with realistic dollar ranges. The site is in technically excellent shape — the bottleneck is now traffic and activation.

**Current state** as of 2026-05-14:
- 18 Google search clicks in 5 days, pre-launch
- 0 active revenue surfaces (all built, all dormant)
- Plausible analytics live
- Site verified in Bing + Google Search Console
- Reddit / HN / journalist push not yet executed

## The blunt math

| Monthly traffic | Realistic monthly revenue |
|---|---|
| < 5K sessions | $0–50 |
| 10K sessions | $50–500 |
| 50K sessions | $500–3K |
| 100K sessions | $1.5K–8K |
| 500K sessions | $8K–30K |
| 1M+ sessions | $25K–80K |
| 1M+ + flagship sponsor | $50K–150K+ |

The original "tens to hundreds of thousands per month" target needs **sustained 1M+ sessions/month AND a flagship sponsorship deal**, or a viral news moment (Drop 02 + congressional UAP testimony combo). Achievable but not in the next 30 days.

**Realistic 90-day ceiling: $5K–15K/mo** if Reddit/HN/press push lands well, no flagship deal. Realistic 90-day floor if launch flops: $200/mo.

## Phase 1: Activate dormant revenue (this week, no traffic required)

These are sitting at 0 because they need an account/tag. Each takes ~5 min of your time.

### 1.1 Amazon Associates affiliate strip — DO THIS FIRST
- Apply: https://affiliate-program.amazon.com (~5 min, near-instant approval)
- Get your tag (e.g. `pursuefiles-20`)
- Tell me; I'll find/replace `YOURTAG` → `pursuefiles-20` in the 5 places in `index.html` + set `AMAZON_AFFILIATE_TAG` in `pipeline/config.py`
- Affiliate strip on homepage + sidebar on all 164 file pages goes live
- Books selected to match audience: Elizondo, Coulthart, Loeb, Kean, Pasulka
- **Expected:** $20–200/mo at 10K sessions; $200–2K at 100K
- **Risk:** must make 3 sales in first 180 days to keep account
- **Time to revenue:** sale 1 typically within first week of meaningful traffic

### 1.2 Email signup wire-up
- Pick: Buttondown ($9/mo, simple), ConvertKit ($9–25/mo, fancier), or Substack (free + 10% if you charge)
- I recommend **Substack** because (a) free to start, (b) you can charge readers $5/mo for premium analysis tier later, (c) Substack itself drives discovery traffic, (d) integrates with social
- Create account, tell me the URL, I wire the homepage signup form
- **The email list IS the asset.** Anyone who subscribes can be re-monetized later (paid tier, sponsored content, product launches)
- **Expected:** 1–3% of visitors convert; at 10K sessions = 100–300 subscribers/mo; at 100K = 1–3K subscribers/mo

### 1.3 Buy Me a Coffee donation button
- 5-min signup: https://buymeacoffee.com
- I add a footer link
- **Expected:** $50–500/mo from passionate readers. Free money, no maintenance.

### 1.4 Plausible upgrade decision (~$9/mo)
- Trial expires in 13 days
- Worth the $9 once you're getting real data. Cheaper than GA4's "free but harvesting" cost.
- Or migrate to GoatCounter (free, self-host) or Umami if budget-conscious

## Phase 2: Drive traffic (week of launch)

The activations in Phase 1 are useless without traffic. Launch sequence already prepared in [DISTRIBUTION.md](DISTRIBUTION.md):

### 2.1 Reddit r/UFOs self-post (Tue/Wed/Thu 9–10am ET)
- Title (new lead): "My automated tracker just caught war.gov silently editing the Trump UFO release. 161 files became 158 overnight. Here's the full diff."
- Body and protocol in DISTRIBUTION.md
- **Realistic outcome:** 1K–50K sessions in 48 hours

### 2.2 Hacker News "Show HN" (same day, 8–10am ET)
- Methodology angle, not the UFO angle (HN's audience is technical)
- Title: "Show HN: I scored all 161 Trump PURSUE UFO files with Claude and a public rubric"
- Anchor comment in DISTRIBUTION.md
- **Realistic outcome:** 5K–100K sessions if it hits the front page

### 2.3 Four journalist pitch emails (post-Reddit, same day)
- Coulthart (NewsNation), Knapp (KLAS), Bender/McMillan (Politico/The Debrief), Sprague (podcast)
- Each pre-drafted in DISTRIBUTION.md
- One cite from a tier-1 outlet = sustained 50K+ sessions for weeks

### 2.4 X / Twitter 8-tweet thread
- @-mention Coulthart, Elizondo, The Debrief
- Pre-drafted in DISTRIBUTION.md

## Phase 3: Convert traffic to revenue (during launch week)

### 3.1 Apply for Google AdSense
- Wait until you have 3-5 days of consistent traffic (50+ daily uniques)
- Apply: https://adsense.google.com
- Approval takes 1-2 weeks
- Three slots already wired: top-of-page, in-grid, footer
- **Expected:** $1–5 RPM × your sessions. At 100K sessions = $100–500/mo.
- **Not great revenue** but it's free money on infrastructure already built

### 3.2 Track conversions in Plausible
- Custom events already firing: Top5Click, Share, 404Recovery
- Add affiliate-link click tracking once tag is in
- After 1 week of launch traffic, you'll see exactly:
  - Which file pages get the most shares (= future drop priorities)
  - Which Top 5 hooks convert (= refine messaging)
  - Where traffic goes (drives next content priorities)

## Phase 4: Premium ad networks (once you qualify)

### 4.1 Ezoic (10K sessions/mo threshold)
- Better RPMs than AdSense, faster approval
- $3–10 RPM vs AdSense's $1–5
- Easier to qualify for than Mediavine

### 4.2 Mediavine / Raptive (50K / 100K sessions/mo)
- Premium networks. RPMs $15–40.
- At 100K sessions/mo: $1.5K–4K/mo just from ads
- Hard quality bar — Mediavine reviews your content
- Apply once threshold hit

## Phase 5: Direct sponsorships (where the real money lives)

Direct deals bypass ad networks entirely. UFO-niche advertisers exist:

### 5.1 Likely sponsor targets
- **Magellan TV** (documentary streamer, UFO content). They pay creators $1K–10K/mo for sustained promotion
- **Skinwalker Ranch / History Channel** brand teams
- **UFO conferences:** Contact in the Desert ($1K–5K sponsorship slot), MUFON Symposium
- **Book launches:** publishers buy newsletter slots ($500–2K/post)
- **Telescopes / sky observation gear** (Celestron, Vaonis) - $500–3K/mo for product placements
- **VPN companies** - they love UFO/conspiracy audiences. NordVPN, ExpressVPN. $1–3K/post for sponsored content

### 5.2 How to land them
- Don't pitch with <100K sessions/mo, no one cares
- Once you have a metric (e.g., "75K sessions/mo, 35% return readers"), email these companies' partnerships teams directly
- Or list yourself on Passionfroot, Hashtag Paid, or Editorial Hub (creator sponsorship marketplaces)

## Phase 6: Productize (compound the audience)

Build digital products that scale to zero marginal cost.

### 6.1 "PURSUE Drop 01 Analyst's Kit" — $19–39
- Notion template + PDF
- Curated reading order, expanded scoring notes, hi-res file index, methodology deep-dive
- Sell via Gumroad or Stripe Checkout
- **Expected:** 1–3% conversion at $29 avg = $30/100 visitors = at 10K visitors/mo = $3K/mo (if marketed well)
- Production time: 2–4 hours since most content already exists

### 6.2 Paid Substack tier — $5–10/mo
- Premium subscribers get:
  - Early-access analysis on every new drop (24h before public)
  - "What changed" diffs on war.gov revisions
  - Monthly long-form analyst piece
- **Expected:** 2–5% of free subscribers upgrade. At 1K free = 20–50 paid = $100–500/mo. At 10K = $1K–5K/mo.

### 6.3 Premium API tier — $49/mo (later)
- Bulk download SLA for journalists/researchers
- Webhook for new drops
- Custom rubric scoring on-demand
- Niche market (~10–50 customers ever) but high margin

## Phase 7: Secondary income surfaces

These are real but smaller. Worth doing once Phase 1–3 lands.

### 7.1 YouTube channel
- Walkthrough videos for each top-10 file (script template in DISTRIBUTION.md)
- AdSense + sponsorships
- Long compounding asset (videos earn for years)
- 6-month horizon before meaningful income

### 7.2 Affiliate beyond books
- Telescopes (Celestron, Vaonis Vespera)
- VPN (NordVPN — the privacy/UFO researcher angle is real)
- Sky observation apps (SkyView, Stellarium Plus)
- Print-on-demand: a single AARO patch design + Spreadshop = ~$3 margin per shirt

### 7.3 Speaking fees / consulting
- Once cited by tier-1 press, speaker bureaus take notice
- $1K–10K per speaking event after the first cite
- Cite-tracking matters — keep a press page

## What you should do RIGHT NOW (next 30 min, ranked by ROI)

1. **Apply Amazon Associates** (5 min, near-instant approval). Send me the tag.
2. **Create Substack account at `pursueufotracker.substack.com`** (5 min). Send me the URL.
3. **Submit `sitemap-index.xml` to Google Search Console** (2 min). This is in the GSC sidebar under Sitemaps.
4. **Use this week's launch window** — Tue/Wed/Thu mornings ET. DISTRIBUTION.md has everything ready.

That's the entire 30-min critical path. Phase 4+ activates as traffic arrives.

## Honest reality check

The site is in better technical shape than 99% of niche content sites. The bottleneck right now is not infrastructure — it's distribution. Until you push the Reddit/HN/journalist launch, revenue trajectory stays at $0/mo regardless of how many revenue surfaces we wire up.

**Single highest-leverage action of the next 30 days: ship the Reddit r/UFOs post during a Tue/Wed/Thu 9am ET window. Everything else compounds on top of that.**
