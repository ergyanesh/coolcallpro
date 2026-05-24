# CoolCallPro.com — Google API SEO Audit
> ⚠ **STATUS AS OF 2026-05-23 — audit point-in-time, partially superseded.**
> Most action items in this audit have shipped. See [ACTION-PLAN.md](../ACTION-PLAN.md)
> for per-item status. Article-priority recommendations have been overridden
> by the 2026-05-23 topical-authority-without-doorway strategy — read
> [CLAUDE.md](../CLAUDE.md) "Topical Authority Without Doorway Risk" section +
> [docs/article-strategy-2026-05-23.md](../docs/article-strategy-2026-05-23.md)
> for current direction. The technical analyses in this audit remain accurate
> as point-in-time observations.

**Date:** 2026-04-26
**Auth Tier:** 2 (Full — API key + Service Account OAuth + GA4)
**Data sources:** Google Search Console API, GA4 Data API v1beta, CrUX API, GSC URL Inspection API
**Data freshness:** GSC performance = 28-day rolling (2026-03-29 to 2026-04-25, 2-3 day lag); GA4 = 28-day rolling (1 day lag); CrUX = 28-day rolling field data

---

## 1. Core Web Vitals — CrUX Field Data

### Origin-level (coolcallpro.com)

**Result:** INSUFFICIENT DATA — CrUX returned 404 for both origin and all 4 page-level URLs.

The site does not yet have enough Chrome user traffic volume to appear in the Chrome UX Report dataset. CrUX requires a minimum monthly threshold of real-user visits (Google does not publish the exact threshold; typically ~1,000 real-user page loads per URL per 28-day period).

| URL | CrUX Status | Fallback |
|-----|-------------|---------|
| https://coolcallpro.com | No data — insufficient traffic | PSI lab data only (see note) |
| https://coolcallpro.com/articles/2026-hvac-cost-guide | No data | PSI lab data only |
| https://coolcallpro.com/locations/houston-tx | No data | PSI lab data only |
| https://coolcallpro.com/costs | No data | PSI lab data only |

**Note on PSI lab data:** `pagespeed_check.py` threw a KeyError on `audit_details` initialization (line 289 — `result["audit_details"]` key not pre-populated before the audit loop writes to it). PSI lab scores were not collected this run. This is a script bug, not an API error. Lighthouse lab data can be retrieved manually at https://pagespeed.web.dev or by patching the script.

**Implication:** No traffic-light CWV ratings (LCP / INP / CLS) can be reported from field data at this time. This is expected for a site 6 weeks post-launch.

---

## 2. GSC URL Inspection — Coverage + Indexation

**Data source:** Google Search Console URL Inspection API (real-time, not search performance data)

| URL | Verdict | Coverage State | Last Crawl (UTC) | Crawled As | Canonical Match | Rich Results |
|-----|---------|----------------|-------------------|------------|-----------------|--------------|
| https://coolcallpro.com | PASS | Submitted and indexed | 2026-04-15 04:54 | Mobile | Partial mismatch (trailing slash) | FAQ detected |
| https://coolcallpro.com/articles/2026-hvac-cost-guide | NEUTRAL | **URL unknown to Google** | Never crawled | — | No canonical found | None |
| https://coolcallpro.com/locations/houston-tx | PASS | Submitted and indexed | 2026-04-17 13:13 | Mobile | Match | Breadcrumbs + FAQ |
| https://coolcallpro.com/costs | PASS | Submitted and indexed | 2026-04-16 17:57 | Mobile | Match | Breadcrumbs + FAQ |

**Flags:**

- **Homepage canonical mismatch:** GSC reports Google canonical as `https://coolcallpro.com` but user canonical is `https://coolcallpro.com/` (trailing slash). Google treats these as the same URL in practice, but the discrepancy means the `<link rel="canonical">` tag in `index.html` has a trailing slash while Google is picking the non-slash form. Low risk, worth aligning.
- **2026-hvac-cost-guide not indexed:** Coverage state "URL is unknown to Google" — never crawled. Either the article was recently published and not yet discovered, or it is not linked from any indexed page, or it is excluded from sitemap.xml. Requires investigation.
- All pages crawled as Mobile Googlebot (expected — mobile-first indexing).
- Mobile usability verdict is `VERDICT_UNSPECIFIED` on all pages — this means the API could not assess usability (not that there are issues). Normal for lower-traffic pages.

---

## 3. GSC Search Performance — Last 28 Days

**Data source:** Google Search Console Search Analytics API
**Period:** 2026-03-29 to 2026-04-25 (GSC 2-3 day lag applied)
**Dimensions pulled:** query + page combined

### 3a. Site-Wide Summary

| Metric | Value |
|--------|-------|
| Total clicks | 0 |
| Total impressions | 6,643 |
| Site CTR | 0.00% |
| Average position | 44.9 |
| Unique queries with impressions | 993 |
| Unique pages with impressions | 74 |

**Note:** Zero clicks across 6,643 impressions and 993 queries is the defining finding of this audit. The site is being discovered and shown in SERPs but no user has clicked through in 28 days. This is consistent with all queries averaging position 44.9 — deep on page 4-5 where click-through rates approach 0%.

### 3b. Top 10 Queries by Impressions (all clicks = 0)

| Rank | Query | Impressions | Avg Position | Clicks |
|------|-------|-------------|--------------|--------|
| 1 | emergency hvac service | 277 | 16.7 | 0 |
| 2 | 24 hour hvac repair | 190 | 14.9 | 0 |
| 3 | hvac financing | 184 | 81.3 | 0 |
| 4 | hvac emergency repair | 165 | 17.3 | 0 |
| 5 | emergency hvac repair | 151 | 18.7 | 0 |
| 6 | emergency hvac service near me | 135 | 19.6 | 0 |
| 7 | emergency ac repair | 122 | 18.7 | 0 |
| 8 | furnace repair philadelphia | 122 | 63.6 | 0 |
| 9 | hvac emergency service | 110 | 19.3 | 0 |
| 10 | emergency ac service | 100 | 16.9 | 0 |

**Observation:** Queries 1-2 and 4-7 and 9-10 form a tight cluster of "emergency HVAC" intent at positions 14-20 (page 2). These are high-commercial-intent queries with meaningful impression volume. They are close to page 1 but not converting because they sit at positions 15-20. The "hvac financing" query at position 81 is a deep-page outlier pulling the average down.

### 3c. Top 10 Pages by Impressions (all clicks = 0)

| Rank | Page | Impressions | Avg Position | Clicks |
|------|------|-------------|--------------|--------|
| 1 | /locations/portland-or | 867 | 37.1 | 0 |
| 2 | /locations/new-orleans-la | 690 | 45.8 | 0 |
| 3 | /article-hvac-financing | 636 | 75.9 | 0 |
| 4 | /locations/san-diego-ca | 600 | 33.6 | 0 |
| 5 | /locations/chicago-il | 525 | 70.2 | 0 |
| 6 | /locations/houston-tx | 396 | 35.1 | 0 |
| 7 | /locations/minneapolis-mn | 374 | 50.0 | 0 |
| 8 | /locations/san-antonio-tx | 355 | 28.5 | 0 |
| 9 | /locations/sacramento-ca | 293 | 28.7 | 0 |
| 10 | /locations/louisville-ky | 257 | 39.2 | 0 |

**Observation:** Portland-OR leads with 867 impressions at position 37 — high impression volume but too deep for clicks. San Antonio (pos 28.5) and Sacramento (pos 28.7) are the closest to page 1-2 territory among high-impression pages. `/article-hvac-financing` has 636 impressions at position 75.9 — significant impression volume but far too deep; suggests broad query matching not yet ranking competitively.

**Note on `.html` URL in GSC data:** one row shows `https://coolcallpro.com/locations/columbia-sc.html` receiving impressions. This confirms a residual `.html` URL is indexed. The `_redirects` 301 should consolidate this over time.

---

## 4. GA4 Organic Traffic — Last 28 Days

**Data source:** GA4 Data API v1beta, channel grouping = Organic Search
**Period:** 2026-03-29 to 2026-04-25 (1 day lag)

### 4a. Site-Wide Organic Summary

| Metric | Value |
|--------|-------|
| Total organic sessions | 82 |
| Total users | 30 |
| Total pageviews | 620 |
| Avg daily sessions | 4.3 |
| Days with organic traffic | 19 of 28 |

**Note:** GA4 session count (82) is consistent with zero GSC clicks — these 82 sessions are likely a mix of direct/type-in, bookmark, referral traffic that GA4 is attributing to organic, plus possible internal QA sessions (the `/cities_updated.xlsx` landing page entry below confirms at least one session is an internal access).

### 4b. Top 10 Organic Landing Pages (28 days)

| Rank | Landing Page | Sessions | Users | Pageviews | Bounce Rate | Engagement Rate |
|------|-------------|----------|-------|-----------|-------------|-----------------|
| 1 | / (homepage) | 37 | 4 | 293 | 8.1% | 91.9% |
| 2 | (not set) | 7 | 1 | 0 | 100.0% | 0.0% |
| 3 | /article-hvac-financing | 6 | 2 | 53 | 0.0% | 100.0% |
| 4 | /locations | 4 | 1 | 12 | 0.0% | 100.0% |
| 5 | /articles | 3 | 1 | 23 | 0.0% | 100.0% |
| 6 | /locations/atlanta-ga | 3 | 1 | 116 | 0.0% | 100.0% |
| 7 | /locations/houston-tx | 3 | 1 | 16 | 0.0% | 100.0% |
| 8 | /articles/complete-ac-troubleshooting-guide | 2 | 1 | 5 | 0.0% | 100.0% |
| 9 | /locations/san-antonio-tx | 2 | 2 | 3 | 50.0% | 50.0% |
| 10 | /article-emergency | 1 | 1 | 7 | 0.0% | 100.0% |

**Flags:**

- **`/cities_updated.xlsx` as a landing page:** GA4 records 1 session landing on `/cities_updated.xlsx`. This means the Excel source file is publicly accessible and being crawled/visited. This is a data-exposure and crawl-budget concern — `build.sh` excludes `.xlsx` from `_dist/` per CLAUDE.md, but it may be accessible in a dev environment or via a stale Cloudflare cache path.
- **`(not set)` landing page (7 sessions):** Indicates GA4 attribution failure — sessions where the landing page dimension could not be resolved. Common causes: direct dark traffic (email links, Slack, etc.) misattributed to organic, or sessions with no page_view event fired on entry.
- **Atlanta-GA generated 116 pageviews from 3 sessions** (38.7 pages/session) — extremely high; likely an internal QA session crawling through the site starting at Atlanta.
- **Homepage engagement rate of 91.9%** on 37 sessions and only 4 unique users — suggests heavy repeat visits from a small number of users (likely the site owner / internal team). Not yet reflecting real organic homeowner traffic.

---

## 5. API Errors and Data Gaps

| Component | Status | Detail |
|-----------|--------|--------|
| CrUX field data (all URLs) | FAILED — insufficient traffic | Site below Chrome UX Report volume threshold. No LCP/INP/CLS field data available. |
| PSI Lighthouse lab scores | FAILED — script bug | `pagespeed_check.py` line 289: `KeyError: 'audit_details'` — key not initialized before write. All 4 PSI calls cancelled. |
| GSC URL Inspection | PASS (4/4) | All 4 URLs inspected. One critical finding: 2026-hvac-cost-guide not indexed. |
| GSC Search Performance | PASS | 1,462 query+page rows retrieved, aggregated successfully. |
| GA4 Organic Overview | PASS | 82 sessions, 19 active days. |
| GA4 Top Landing Pages | PASS | 23 landing pages returned. |
| GSC Sitemaps | NOT RUN | Not included in this run's scope. |

---

## Appendix: Raw Data Notes

- GSC query `gsc_query.py` returned two concatenated JSON objects (1,462 query+page rows + a separate report object). The aggregation script handled this via multi-decode.
- GSC totals object from API: `{"total_clicks": 0, "total_impressions": 6643}` — confirms zero-click figure is from the API, not an aggregation artifact.
- GA4 `top-pages` report and `organic_traffic` report returned identical landing page arrays; both are sourced from the same GA4 `runReport` call with `sessionDefaultChannelGroup == Organic Search` filter.
- PSI script fix required: in `run_pagespeed()`, `result["audit_details"] = {}` must be initialized before the audit-detail loop at line ~285.
