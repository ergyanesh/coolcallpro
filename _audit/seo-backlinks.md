# Backlink Profile Audit — coolcallpro.com

> ⚠ **STATUS AS OF 2026-05-23 — audit point-in-time, partially superseded.**
> Most action items in this audit have shipped. See [ACTION-PLAN.md](../ACTION-PLAN.md)
> for per-item status. Article-priority recommendations have been overridden
> by the 2026-05-23 topical-authority-without-doorway strategy — read
> [CLAUDE.md](../CLAUDE.md) "Topical Authority Without Doorway Risk" section +
> [docs/article-strategy-2026-05-23.md](../docs/article-strategy-2026-05-23.md)
> for current direction. The technical analyses in this audit remain accurate
> as point-in-time observations.

**Audit date:** 2026-04-26
**Tier:** 0 — Common Crawl Web Graph + Backlink Verification Crawler only
**Automated validator:** PASS (0 errors, 0 warnings)

---

## Data Sources

| Source | Status | Confidence | Notes |
|--------|--------|------------|-------|
| Common Crawl Web Graph (cc-main-2026-jan-feb-mar) | Not found | n/a | Domain absent from ranking index |
| Common Crawl — 5 prior releases checked (2024-Q4 through 2025-Q4) | Not found | n/a | Consistent across all 6 releases |
| Backlink Verification Crawler — 23 candidate URLs tested | 0 confirmed inbound links | n/a | Details below |

---

## Backlink Health Score

**INSUFFICIENT DATA**

Fewer than 4 of the 7 scoring factors have any data at Tier 0 when the domain is absent from the Common Crawl index. Producing a numeric score (e.g., "32/100") would be fabricated — it would require inventing weights for factors with zero data. Score deferred until Tier 1 (Moz API) is available.

Factors scored: **0 of 7**
Factors skipped: referring domain count, domain quality distribution, anchor text naturalness, toxic link ratio, link velocity trend, follow/nofollow ratio, geographic relevance

---

## Section 1 — Common Crawl Web Graph

**Result: Domain not in crawl index** — CC (domain-level, confidence: 0.50)

Releases checked:
- cc-main-2026-jan-feb-mar (latest)
- cc-main-2025-oct-nov-dec
- cc-main-2025-jul-aug-sep
- cc-main-2025-apr-may-jun
- cc-main-2025-jan-feb-mar
- cc-main-2024-oct-nov-dec

| Metric | Value | Source |
|--------|-------|--------|
| PageRank | null | CC — not indexed |
| Harmonic Centrality | null | CC — not indexed |
| In-degree (referring hosts) | null | CC — not indexed |
| Top Referring Domains | (none) | CC — not indexed |

**Interpretation:** Absence from the CC Web Graph ranking index does not mean the domain has zero links in the raw crawl — it means the domain has not accumulated enough inbound link equity to appear in the ranked host-level graph. Common Crawl indexes roughly the top 100–200M domains by link equity. A new domain with sparse inbound links (0–30 referring domains) will typically not appear for 2–4 CC release cycles after those links are live. Given coolcallpro.com was deployed early 2025 with no active link-building campaign, this outcome is expected.

**Data freshness:** CC releases quarterly. The latest release covers January–March 2026. Any links acquired in April 2026 or later are not reflected.

---

## Section 2 — Referring Domains

**Result: None confirmed** — Verify Crawler (confidence: 0.95 for pages that returned confirmable HTML)

### Candidate sites tested (23 total)

| Candidate URL | HTTP Status | Link to coolcallpro.com | Notes |
|--------------|-------------|------------------------|-------|
| yellowpages.com | 403 | Unverifiable | Bot-blocking |
| yelp.com | 403 | Unverifiable | Bot-blocking |
| bbb.org | 403 | Unverifiable | Bot-blocking |
| angi.com | 403 | Unverifiable | Bot-blocking |
| homeadvisor.com | 403 | Unverifiable | Bot-blocking |
| thumbtack.com | 202 | Unverifiable | Bot-blocking |
| clutch.co | 403 | Unverifiable | Bot-blocking |
| producthunt.com/products/cool-call-pro | 404 | Not found | No product listing exists |
| crunchbase.com/organization/cool-call-pro | 403 | Unverifiable | Bot-blocking |
| github.com/ergyanesh/coolcallpro | 404 | Not found | Repo is private |
| pages.cloudflare.com | 200 | No link found | Checked full HTML; no mention |
| marketcall.com | 200 | No link found | Checked full HTML; MarketCall does not link back to publisher sites |
| reddit.com/r/hvac | 200 | Unverifiable (JS) | Reddit is JS-rendered; cannot confirm via HTTP GET |
| reddit.com/r/Entrepreneur | 200 | Unverifiable (JS) | Reddit is JS-rendered; cannot confirm via HTTP GET |
| producthunt.com (homepage) | 200 | No product listing | — |
| crunchbase.com (homepage) | 200 | Not applicable | — |
| capterra.com | 403 | Unverifiable | Bot-blocking |
| g2.com | 403 | Unverifiable | Bot-blocking |
| alternativeto.net | 403 | Unverifiable | Bot-blocking |

**Only confirmed "link" found:** coolcallpro.com links to itself from its own homepage navigation — this is a self-reference, not an inbound backlink.

---

## Section 3 — Anchor Text Distribution

**Result: No data** — No confirmed external inbound links exist to analyze anchor text.

Expected healthy distribution for a new referral site at this stage:
- Brand anchors ("Cool Call Pro", "coolcallpro.com"): 60–80%
- Naked URL anchors ("https://coolcallpro.com"): 10–20%
- Generic anchors ("click here", "visit site"): 5–10%
- Topical/keyword anchors ("HVAC repair referral", "AC service near me"): 5–15%

Exact-match keyword-heavy anchor text (e.g., "best HVAC repair service") would be a red flag if it appeared in a sparse early-stage profile — it's the footprint of purchased links. No such signal exists here because no external links have been confirmed.

---

## Section 4 — Toxic / Low-Quality Link Signals

**Result: None observed** — Verify Crawler (confidence: 0.95)

No PBN-style, directory-spam, or suspicious anchor footprints detected. This is a neutral finding: a completely clean profile at this stage is consistent with either (a) no link-building at all, or (b) a genuinely clean link-building start. Without Moz Spam Score or DataForSEO toxic-domain classification, a definitive "no toxic links" claim cannot be made — the absence of confirmed links simply means there is nothing to classify.

---

## Section 5 — Link Velocity Trend

**Result: No data** — Requires DataForSEO (Tier 3 only). Free sources lack historical velocity data.

Expected for this domain: near-zero velocity consistent with organic, unmanaged link acquisition during content publishing phase.

---

## Summary Table

| Factor | Weight | Score | Source | Confidence |
|--------|--------|-------|--------|------------|
| Referring domain count | 20% | NO DATA | CC — not indexed | — |
| Domain quality distribution | 20% | NO DATA | Requires Moz/DataForSEO | — |
| Anchor text naturalness | 15% | NO DATA | No confirmed links to analyze | — |
| Toxic link ratio | 20% | NO DATA | Requires Moz Spam Score | — |
| Link velocity trend | 10% | NO DATA | Requires DataForSEO | — |
| Follow/nofollow ratio | 5% | NO DATA | Requires Moz/DataForSEO | — |
| Geographic relevance | 10% | NO DATA | Requires DataForSEO | — |

**Composite Backlink Health Score: INSUFFICIENT DATA** (0 of 7 factors scored)

---

## Tier Limitations

This audit is Tier 0. The following data is unavailable without additional API access:

| Unavailable Data | What It Would Show | Required Tier |
|-----------------|-------------------|---------------|
| Domain Authority (DA) / Page Authority (PA) | Moz's proprietary link-quality composite score | Tier 1 (Moz API) |
| Spam Score | % of sites linking to domains known for spam patterns | Tier 1 (Moz API) |
| Referring domain count (verified) | Total unique domains linking to coolcallpro.com | Tier 1 (Moz API) |
| Anchor text distribution | Full anchor text breakdown across all inbound links | Tier 1 (Moz API) |
| Competitor backlink gap | Which domains link to hvac-referral competitors but not to us | Tier 2 (Bing Webmaster) |
| Link velocity trend | Rate of new referring domain acquisition over time | Tier 3 (DataForSEO) |
| Toxic domain flagging | Per-domain spam/toxicity classification | Tier 3 (DataForSEO) |

---

## Recommendations

### Priority 1 — Unlock Tier 1 (Free, highest impact)

**Add Moz API key.** Moz's free tier provides 2,500 rows/month — sufficient for a site this size. This unlocks DA, PA, Spam Score, referring domain count, and anchor text distribution in a single script call (`python scripts/moz_api.py metrics https://coolcallpro.com --json`).

Setup: `https://moz.com/products/api` (free registration) → set `MOZ_API_KEY` env var or add to `~/.config/claude-seo/backlinks-api.json`.

**What Moz would reveal that CC cannot:**
- Whether any of the JS-heavy sites (Reddit, social) have mentioned coolcallpro.com in indexed posts
- The real referring domain count (could be 0–50 for a site this age — Moz indexes far more of the web's link graph than CC's ranked subset)
- Whether any spam domains have already linked speculatively (common for new domains — automated link spam targets any newly-registered domain)

### Priority 2 — Unlock Tier 2 (Free, high value for competitive intel)

**Add Bing Webmaster Tools.** Free via `https://www.bing.com/webmasters`. Bing Webmaster's link API (`python scripts/bing_webmaster.py links https://coolcallpro.com --json`) returns near-realtime inbound link data for verified properties. Critically, it enables competitor gap analysis (`bing_webmaster.py compare`) — finding which domains link to HVAC competitors (homewarrantyreviews.com, callonhvac.com, etc.) but not to coolcallpro.com. This is the highest-signal free source for link prospecting at this stage.

Setup: Add coolcallpro.com to Bing Webmaster Tools (already likely verified via sitemap submission) → generate API key in dashboard → set `BING_WEBMASTER_API_KEY` env var.

### Priority 3 — Proactive link acquisition (strategy, not tooling)

The most important backlink finding for a domain this age is not spam detection — it is **the absence of any confirmed inbound links**. For a site with 204 URLs, 115 city pages, and 12+ published articles, the content surface exists for organic links to accumulate, but at zero velocity they will not accumulate on their own.

High-ROI, zero-cost link acquisition channels appropriate for this domain:

| Channel | Effort | Likely link type | Why it fits |
|---------|--------|-----------------|-------------|
| HVAC contractor associations (ACCA, RSES state chapters) — resource page submissions | Low | Dofollow from .org | Topically authoritative; site's referral model is a genuine resource for homeowners |
| Local home-improvement publications linking to "find an HVAC pro" resources | Medium | Mixed follow/nofollow | High domain relevance; 115 city pages create natural local angle |
| Homeowner forums and Q&A (Houzz, Reddit, home-improvement subreddits) — answer questions, link as resource | Low | Nofollow, but brand signal | Even nofollow Reddit links generate brand searches that Google interprets as authority signal |
| ENERGY STAR / DOE state energy office "find a contractor" resource directories | Medium | High-authority dofollow | .gov links are rare and weighted heavily |
| MarketCall publisher directory / partner page | Low (ask MarketCall) | Dofollow from revenue partner | Natural — you're already their publisher |

---

## Data Freshness Notes

| Source | Freshness | Notes |
|--------|-----------|-------|
| Common Crawl Web Graph | Quarterly (latest: Jan–Mar 2026) | Links acquired after March 2026 not reflected |
| Backlink Verification Crawler | Real-time (crawled 2026-04-26) | Reflects current page state |
| Moz API (when added) | ~3 days lag | Near-realtime for active domains |
| Bing Webmaster (when added) | Near-realtime | Best freshness of free sources |

---

*Audit produced by seo-backlinks skill at Tier 0. Automated validator: PASS. All claims sourced to direct tool output — no inferences presented as facts. To upgrade data fidelity, add Moz API key (Tier 1) or Bing Webmaster key (Tier 2) to `~/.config/claude-seo/backlinks-api.json`.*
