# Monetization Roadmap

Phased approach. Trust is the moat — don't burn it for early ad revenue.

## Day 1 (today, no traffic required)

### Amazon Associates affiliate
- Apply: https://affiliate-program.amazon.com - free, takes 5 minutes
- Once approved (instant for most), get your tracking ID (looks like `pursuefiles-20`)
- Update [pipeline/config.py](pipeline/config.py) → set `AMAZON_AFFILIATE_TAG`
- Topic-relevant book sidebar auto-populates on every page
- Realistic earnings: $20-200/mo at 10K monthly sessions
- Must make 3 sales in first 180 days to keep account active
- **Books to recommend (curated, all UFO-canon):**
  - "Imminent" by Luis Elizondo
  - "American Cosmic" by Diana Pasulka
  - "In Plain Sight" by Ross Coulthart
  - "UFOs and the National Security State" by Richard Dolan
  - "Communion" by Whitley Strieber

### Buy Me a Coffee / Donations
- Sign up at buymeacoffee.com (or Stripe/Patreon)
- Single button in footer + dedicated /support/ page
- Audience that values "no paywall" model often donates
- Realistic: $50-500/mo from passionate subset

## Day 7 - apply for ads

### Google AdSense
- Apply: https://adsense.google.com
- Approval takes 1-30 days
- Cloudflare Pages domain pre-approved (no DNS jumping required)
- Pre-built ad slots in templates — just paste your AdSense client ID into config
- Realistic RPM (revenue per 1000 pageviews): $2-5 for US/EU traffic, $0.50-1 for global
- At 10K monthly pageviews: ~$20-50/mo

## Day 30 - flip the ads switch

Once AdSense approved AND you've had 30 days of traffic-building:
1. Set `ENABLE_ADS = True` in [pipeline/config.py](pipeline/config.py)
2. Set `ADSENSE_CLIENT_ID = "ca-pub-XXXXXXXXXXXXXXXX"`
3. Rebuild + push - ads go live across all pages

Ad slot inventory (already wired into templates, dormant until enabled):
- **Homepage:** 1 leaderboard above filter bar, 1 in-grid native card every 6 cards, 1 footer banner
- **File detail:** 1 sidebar, 1 below transcript
- **Verdict / Top 10 / Drops:** 1 in-content native, 1 footer

## Day 60-90 - upgrade ad networks

Once you hit thresholds, swap AdSense for premium:

| Network | Threshold | RPM | Notes |
|---|---|---|---|
| AdSense | None | $2-5 | Default; auto-approves most sites |
| Ezoic | 10K sessions/mo | $5-15 | Better RPM, more setup |
| Mediavine | 50K sessions/mo | $20-40 | Premium, hard to get into |
| Raptive (AdThrive) | 100K pageviews/mo | $25-50 | Premium tier; reapply when eligible |

To swap: change `AD_NETWORK` in config; templates auto-render the right script tags.

## Day 60+ - sponsorships and direct deals

At meaningful traffic (10K+ monthly), pitch direct sponsors:
- UFO podcasts (Need to Know, That UFO Podcast, Theories of Everything)
- UFO/UAP conferences (SCU, Disclosure events)
- Books and documentaries pre-launch
- Telescope/astronomy gear retailers
- VPN services (high-converting on conspiracy-adjacent audiences)

Direct sponsor CPM can be 5-10× ad network rates.

## Day 90+ - subscription tier

Once email list > 1000 subscribers:
- **Buttondown paid tier** ($5-15/mo): early-access drop alerts (24hr before public), deeper file analysis, member-only Q&A
- **Patreon tiers**: $5/mo (early alerts), $25/mo (monthly podcast/AMA), $100/mo (custom file analysis)

Realistic conversion: 1-3% of free subscribers convert to paid. At 10K free subs = $500-3000/mo.

## What NOT to do

- **No popups, no autoplay video ads, no interstitials.** Kills SEO and trust. AdSense by default doesn't do these; explicitly disable in network settings.
- **No paywall on the archive itself.** Paywalling public-domain U.S. government documents is both ethically gross and gets your AdSense account terminated.
- **No crypto/NFT/scam-adjacent ads.** Would torch credibility. Use AdSense's content category blocks.
- **No promoted "alien evidence!" affiliate junk.** Only credible books and topic-relevant gear.

## Trust-preserving copy updates

When ads go live, update these:
- [generated/press.html](generated/press.html) and [templates/press.html.j2](templates/press.html.j2): change "Free, no ads, no signup wall" to "Reader-supported. Tasteful ads + affiliate links keep the archive free. We never paywall public-domain documents."
- Add a `/about/` page explaining the funding model

## Honest revenue projection

Conservative estimates if site catches the search wave:

| Month | Monthly visits | Affiliate | AdSense | Donations | Total |
|---|---|---|---|---|---|
| 1 | 5K | $10 | (pending approval) | $50 | ~$60 |
| 2 | 25K | $50 | $75 | $100 | ~$225 |
| 3 | 75K | $150 | $250 | $200 | ~$600 |
| 6 | 200K | $500 | $1000 (Ezoic) | $400 | ~$1900 |
| 12 | 500K (Drop 5+) | $1500 | $4000 (Mediavine) | $800 | ~$6300 |

Rolling-release cadence is the multiplier — each new PURSUE drop = traffic spike + new subscribers + repeat audience. Compounds over the program's lifespan.

## My recommendation

**Today: Amazon Associates + Buy Me a Coffee.** Both are non-intrusive. Apply for AdSense on day 7. Flip display ads on day 30. Pitch sponsors at day 60. Launch paid tier at day 90.

By month 6 the site can realistically clear $1500-2500/month, which is enough to justify the operational cost (negligible) and pay for someone to help with outreach if you want to scale faster.
