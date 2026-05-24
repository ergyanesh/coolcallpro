# Cool Call Pro — Full SEO Audit Report

**Domain:** https://coolcallpro.com
**Audit date:** 2026-04-26
**Business type:** Multi-state HVAC referral aggregator (no physical presence)
**Page inventory:** 205 live HTML files (51 state hubs + 115 city pages + 22 articles + ~17 utility/root)
**Tooling:** claude-seo v1.9.0 — Tier 2 Google APIs (PSI, CrUX, GSC, GA4, Indexing) + Common Crawl backlink graph + Playwright visual capture

---

> ⚠ **STATUS AS OF 2026-05-23 — most findings addressed.** See
> [ACTION-PLAN.md](ACTION-PLAN.md) for per-item status. Key changes
> since this audit:
>
> - Site now has 33 live articles (was 22 at audit time), all 6 cluster
>   pillars live (was 2 of 6)
> - Track B framing pivot + Phase 3 enrichment shipped 2026-05-22 to
>   all 115 city pages (commits `ac57848` + `6684309`)
> - llms.txt actually live as of 2026-05-23 (was 404 for 26 days
>   despite the H1 item being thought "done" — build.sh wasn't copying it)
> - Article strategy overridden 2026-05-23: pillar-cluster approach
>   from this report is correct, but the specific cost-niche +
>   symptom-variant slugs are now considered doorway-risky and
>   DEFERRED indefinitely. See `CLAUDE.md` "Topical Authority
>   Without Doorway Risk" + `docs/article-strategy-2026-05-23.md`.
>
> The technical, on-page, schema, performance, content-quality, and
> AI-search-readiness analyses remain accurate as point-in-time
> observations. Most action items shipped.

---

## Executive Summary

### SEO Health Score: **79 / 100** (Good — with one severe blocker)

| Category | Weight | Score | Notes |
|---|---|---|---|
| Technical SEO | 22% | 85 | Solid foundation; minor gaps (llms.txt missing, mobile LCP borderline) |
| Content Quality | 23% | 80 | Strong E-E-A-T + safety + OBBBA discipline; pillar-cluster execution has gaps |
| On-Page SEO | 20% | 75 | Unique meta + clean canonicals, but 0 clicks on 6,643 impressions reveals deep title/intent mismatch |
| Schema / Structured Data | 10% | 65 | 12 articles use DEPRECATED HowTo schema; emergency.html has LocalBusiness-subclass schema (rule violation) |
| Performance (CWV) | 10% | 90 | Desktop 100/100; mobile 95–99, four pages at borderline LCP |
| AI Search Readiness | 10% | 70 | robots.txt allows AI input bots ✅; llms.txt 404; PerplexityBot/OAI-SearchBot not explicit |
| Images | 5% | 90 | Alt text consistently present on all sampled pages |
| **Total** | 100% | **79.1** | |

### The single most important finding

**0 clicks on 6,643 impressions in the last 28 days, with the top 9 of 10 queries being "emergency HVAC" intent at positions 14–20** ([_audit/seo-google.md](_audit/seo-google.md)).

The site is being shown to high-commercial-intent users every day — it's just deep on page 2. That's not a "build authority for 6 months" problem; that's a "10–15 ranking positions away from converting" problem. Combined with the SXO finding that city pages targeting `[service] in [city]` queries are structurally excluded from the local pack (no GBP, no physical presence), the audit's top recommendation is a **page-type and title-tag repositioning of the city pages toward informational queries** where local-pack exclusion doesn't matter.

### Top 5 Critical Issues

1. **HowTo schema on 12 articles is deprecated** (Sept 2023). Google ignores it for rich results; some crawlers treat it as a quality signal regression. → Remove. ([_audit/seo-schema findings](_audit/) — see Schema section below)
2. **`emergency.html` uses `EmergencyService` schema, which inherits from `LocalBusiness`** — directly violates the project's hard rule against LocalBusiness markup for a referral aggregator with no physical presence.
3. **`articles/2026-hvac-cost-guide` is not yet indexed** (GSC URL Inspection: "URL is unknown to Google"). For a deep-pillar article with cost data, that's lost equity.
4. **Zero clicks on 6,643 impressions** — top emergency-HVAC queries at positions 14–20. Title-tag + meta-description repositioning has direct revenue impact.
5. **City pages structurally excluded from local pack** on `[service] in [city]` queries (SERP backwards analysis). Without a GBP-equivalent (which contradicts the business model), city pages must compete in the informational layer instead.

### Top 5 Quick Wins

1. **Add `llms.txt`** at the site root. ~30 minutes. Direct boost to AI-search citability (ChatGPT, Perplexity, Google AI Overviews). Site already has the discipline (primary-source citations, OBBBA awareness) — llms.txt makes it easier for LLMs to discover.
2. **Fix tag-pill color contrast** (WCAG 1.4.3) — site-wide CSS one-line fix in `style.css`. Article pills currently 3.24:1 (need 4.5:1). Also raises Accessibility from 96 → 100.
3. **Remove deprecated HowTo schema** from 12 articles via a one-shot script. ~30 min including verification.
4. **Add `articles/2026-hvac-cost-guide`** to internal link footers + request reindex via Indexing API (we have access). ~15 min.
5. **Update C1 pillar (`complete-ac-troubleshooting-guide`)** to link to the 6 missing C1 cluster spokes. 30-min hand-edit, big internal-PageRank win.

---

## 1. Technical SEO (Score: 85)

### What's working

- **Clean URL strategy fully deployed.** `sitemap.xml` contains 0 `.html` URLs ✅. All 207 lines in `_redirects` map `/foo.html` → `/foo` (301). Internal hrefs are clean (per pre-commit hook enforcement).
- **205 live HTML files; 0 duplicate meta descriptions** across the entire site. Every page has a unique `<title>` and `<meta description>`.
- **Security headers (`_headers`):** HSTS (1 year + subdomains), X-Frame-Options SAMEORIGIN, full Permissions-Policy lockdown (incl. interest-cohort opt-out for FLoC), CSP currently in Report-Only mode. Planned flip to enforcing ~22 May 2026 per CLAUDE.md.
- **Mobile-first, mobile-only sticky bar** with IntersectionObserver auto-hide pattern verified working in visual capture.
- **Pre-commit audit hooks** enforce many checks (clean URLs, font preload patterns, GA defer pattern, FAQ collapsible pattern, OBBBA-aware copy).

### Issues found

| Severity | Issue | Location | Fix |
|---|---|---|---|
| **High** | `llms.txt` returns 404 | site root | Create `llms.txt` (template in [_audit/seo-geo recommendations](#)) |
| Medium | `audit_script.py` reports 23,646 "broken internal links" — all false positives. The script doesn't understand the clean-URL strategy and treats every `href="../about"` as broken because `about.html` exists but `about` doesn't (as a file) | `audit_script.py` | Update the audit script to map `<href>` → file by trying both `<href>` and `<href>.html`. Without this fix, the audit's broken-link count is unusable. |
| Medium | `404.html` is missing `<link rel="canonical">` | `404.html` | Add `<link rel="canonical" href="https://coolcallpro.com/404">`. (Optional but standard.) |
| Medium | Homepage canonical mismatch — site canonical is `https://coolcallpro.com/` but Google's chosen canonical (per GSC URL Inspection) is `https://coolcallpro.com` (no trailing slash) | `index.html` | Either remove the trailing slash from `<link rel="canonical">` or accept it (Google treats them as the same URL). Cosmetic — low risk. |
| Low | Mobile LCP borderline on 4 pages (homepage, 2 articles, texas state hub) — Lighthouse reports 2,551–2,560ms vs 2,500ms threshold | site-wide | The 51–60 ms margin is from Inter woff2 download time on the throttled mobile profile. Real-user CDN performance is likely already under threshold. Verify when CrUX field data appears (~3-6 months of traffic). |
| Low | `audit_script.py` reports 99% of pages "low readability (<60)" — known limitation: heuristic doesn't fit technical/template content | `audit_script.py` | Either retune the heuristic for HVAC technical content or document as a known false-positive. |

### CrUX field data: not yet available

The site has insufficient Chrome user traffic for Google to publish CrUX field data. Lab estimates are the only CWV source for now. This is normal for a domain ~12 months post-launch with no link-building campaign yet.

### Crawlability + indexability

- robots.txt blocks **AI training** crawlers (Amazonbot, Applebot-Extended, Bytespider, CCBot, meta-externalagent) ✅
- Allows **AI input** crawlers (ClaudeBot, Google-Extended, GPTBot) ✅
- Sitemaps declared in robots.txt ✅
- 4 of 4 sampled URLs return PASS verdict in GSC URL Inspection EXCEPT `/articles/2026-hvac-cost-guide` (URL unknown to Google — see Critical issue #3)

---

## 2. Content Quality + E-E-A-T (Score: 80)

### What's working

- **Author E-E-A-T:** Gyanesh Gulshan, B.Tech Mechanical Engineering. `author-gyanesh.html` has correct Person schema with `alumniOf: EducationalOrganization` (Himachal Pradesh University) and `hasCredential: EducationalOccupationalCredential` (B.Tech Mech Eng). LinkedIn `sameAs`. Full bio with `knowsAbout` array.
- **Safety discipline:** `safety_rules.py` enforces ~25 DIY-hazard regex patterns. **0 violations across 24 articles** ✅. The 5-task DIY cap (filter / thermostat / debris / drain / call-pro) is honored site-wide.
- **YMYL OBBBA awareness:** 168 mentions of OBBBA / 25C termination across the site. Both articles flagged for federal-credit language (`article-hvac-financing.html`, `articles/2026-hvac-cost-guide.html`) are CORRECTLY explaining the credit's termination, not promoting it. False positive in audit_script — they're compliant.
- **No banned marketing claims** ("calls answered in 2 min", "99% satisfied", time/% counts) on live pages. The 3 grep matches are in `.superpowers/brainstorm/` dev scratchpads (not deployed).
- **Costs.html** is single source of truth for all pricing. No duplicate cost tables in articles.
- **Pillar-cluster system** is documented and maintained: `cluster_map.json` + `LINK_PLAN.md` + `PROGRESS.md` (auto-generated).

### Issues found (see [_audit/seo-cluster.md](_audit/seo-cluster.md) for full detail)

| Severity | Issue | Fix |
|---|---|---|
| **Critical** | C2_furnace cluster has 4 live cluster articles but the C2 pillar (`furnace-not-working-diagnostic-guide`) does not yet exist. Cluster equity bleeds into orphans. | Write the C2 pillar (already #8 in priority queue) before any more C2 cluster articles. |
| **Critical** | C6_maint cluster has 3 live cluster articles but the C6 pillar (`year-round-hvac-maintenance-playbook`) is at position 26 in the queue. Same orphan-pillar problem. | Move C6 pillar forward to position 4–6 in the queue. |
| **High** | C1 pillar (`complete-ac-troubleshooting-guide`) is stale — published 2026-04-16, but 6 C1 cluster articles shipped 2026-04-20/21 and are NOT linked from the pillar. Breaks the bidirectional pillar-spoke link rule. | Add 6 new spoke links to the C1 pillar — 30-min edit, large equity-distribution win. |
| Medium | Cross-cluster bridges weak: C6→C1 (maintenance prevents AC emergencies) absent from `article-maintenance.html`; C2→C4 routes to `/costs` (static page) rather than to `articles/2026-hvac-cost-guide` (the pillar). | Add 2 sentences linking C6→C1 in `article-maintenance.html`; redirect C2→C4 anchor to the article. |
| Medium | 26 cities (23%) have zero planned article inbound links (orphans for the topical-authority system). Notable: NYC, Portland OR, Raleigh NC, Columbus OH, New Orleans LA. | Adjust climate-zone weights in `article_city_linker.py` to route cold-zone pending articles toward NYC, Columbus, Providence. |
| Medium | Tucson AZ over-linked at 7× the site average (7 articles linking in vs site avg 1.7). | Cap Tucson in pending assignments. |
| Low | Schema absent on diagnostic article `articles/ac-freezing-up-in-summer.html` (per WebFetch test) — opportunity for FAQPage + Article schema | Add Article + FAQPage JSON-LD. |

---

## 3. On-Page SEO (Score: 75)

### What's working

- 205 unique titles (each ≤60 chars per CLAUDE.md target)
- 205 unique meta descriptions (each ≤155 chars target)
- All canonical tags present (except 404.html — see Technical)
- Heading hierarchy enforced by audit_page.py (1 H1 per page, no skipped levels)

### The big issue — title/meta intent mismatch

**0 clicks on 6,643 impressions in the last 28 days** ([_audit/seo-google.md](_audit/seo-google.md)).

Top 10 queries by impression in the last 28 days, all with 0 clicks:

| Query | Impressions | Avg Position |
|---|---|---|
| emergency hvac service | 277 | 16.7 |
| 24 hour hvac repair | 190 | 14.9 |
| hvac financing | 184 | 81.3 |
| hvac emergency repair | 165 | 17.3 |
| emergency hvac repair | 151 | 18.7 |
| emergency hvac service near me | 135 | 19.6 |
| emergency ac repair | 122 | 18.7 |
| furnace repair philadelphia | 122 | 63.6 |
| hvac emergency service | 110 | 19.3 |
| emergency ac service | 100 | 16.9 |

8 of 10 are "emergency HVAC" variants at position 14–20. Position 14–20 means **page 2** (results 11–20 are page 2 in mobile-first SERP layout). Click-through at position 15 is typically <1%.

### Top pages by impression — all city pages, all 0 clicks

| Page | Impressions | Position |
|---|---|---|
| /locations/portland-or | 867 | 37.1 |
| /locations/new-orleans-la | 690 | 45.8 |
| /article-hvac-financing | 636 | 75.9 |
| /locations/san-diego-ca | 600 | 33.6 |
| /locations/chicago-il | 525 | 70.2 |
| /locations/houston-tx | 396 | 35.1 |
| /locations/minneapolis-mn | 374 | 50.0 |

City pages are getting the impressions but at average position 28–50, well below click-territory. Per [_audit/seo-sxo.md](_audit/seo-sxo.md), the SERP for `[service] in [city]` queries is dominated by GBP local-pack listings (70%+) — Cool Call Pro is structurally excluded because it has no GBP and no physical presence.

### What to do about it (see ACTION-PLAN.md for full priorities)

1. **Reposition city-page titles toward informational queries** where local-pack doesn't compete. e.g., "HVAC Repair Cost in Houston" / "Houston Climate & HVAC Service Needs" instead of "24/7 AC Repair in Houston".
2. **Improve title tags on emergency-HVAC pages** — they're getting impressions; squeeze 5–10 ranking positions out of CTR + dwell-time + on-page improvements.
3. **Bring `articles/2026-hvac-cost-guide` to indexation** — it's a flagship deep pillar that Google has never crawled.

---

## 4. Schema / Structured Data (Score: 65)

### What's in use site-wide

| Schema type | Count | Status |
|---|---|---|
| Question / Answer | 1085 each | Inside FAQPage — ✅ valid |
| ListItem | 713 | Inside BreadcrumbList — ✅ valid |
| State / City / Country | 413 / 260 / 3 | Generic Schema.org/Place subtypes — ✅ NOT LocalBusiness |
| Organization | 366 | ✅ valid |
| BreadcrumbList | 204 | ✅ Every live page has breadcrumbs |
| FAQPage | 197 | ⚠ Note Aug 2023 rich-result restriction (gov/health only); still valuable for AI citation |
| Audience / Service / ContactPoint | 167 / 167 / 119 | ✅ valid (Schema.org/Service is generic, not LocalService) |
| Article / WebPage / ImageObject | 26 each | ✅ valid |
| Person | 27 | Author markup — ✅ valid |
| SpeakableSpecification | 17 | ✅ Good for voice/AI extraction |
| WebSite + SearchAction | 1 + 1 | ✅ Homepage Sitelinks Search Box |
| EducationalOrganization + EducationalOccupationalCredential | 1 each | ✅ author-gyanesh.html alumniOf + hasCredential |

### CRITICAL issues

| Severity | Issue | Files | Fix |
|---|---|---|---|
| **Critical** | `HowTo` schema is deprecated by Google (Sept 2023) — no longer triggers rich results, may be flagged as quality regression | 12 article files: `article-fall-prep.html`, `article-maintenance.html`, `article-spring-ac.html`, `article-winter-storm.html`, `articles/ac-circuit-breaker-trips.html`, `articles/ac-contactor-clicking.html`, `articles/ac-freezing-up-in-summer.html`, `articles/ac-not-cooling-below-80.html`, `articles/complete-ac-troubleshooting-guide.html`, `articles/hvac-leaking-water-inside-house.html`, `articles/thermostat-blank-ac-wont-start.html`, `articles/water-dripping-from-vent.html` | Remove the `HowTo` JSON-LD blocks. The instructional content can stay as plain HTML; the schema doesn't get rich results. (Optional alternative: keep the steps as `Article` + structured paragraphs.) |
| **High** | `emergency.html` uses `@type: EmergencyService`, which inherits from `LocalBusiness`. Cool Call Pro is a referral aggregator with no physical presence — using LocalBusiness-family schema is misrepresentation per the project's hard rule | `emergency.html` | Change `@type` from `EmergencyService` to a generic `Service` (or remove the schema and rely on the page's existing FAQPage + Organization schema). Keep `telephone`, `description`, `areaServed`, `audience` — those map cleanly to `Service`. Drop `OpeningHoursSpecification` (not applicable to a non-business). |
| Low | Some diagnostic articles lack any structured data per spot-check (e.g., `articles/ac-freezing-up-in-summer.html` per WebFetch — but this conflicts with the grep above showing it has HowTo schema; possible client-side rendering difference). Verify per-page. | `articles/*.html` | After removing HowTo schema, replace with `Article` + `FAQPage` (which is already typical for the site). |

---

## 5. Performance / Core Web Vitals (Score: 90)

[_audit/seo-performance.md](_audit/seo-performance.md) has the full table.

### Lab CWV (Lighthouse mobile, throttled)

| URL | LCP | TBT (INP proxy) | CLS | Perf score |
|---|---|---|---|---|
| / | **2,552 ms** ⚠ | 0 ms ✅ | 0.000 ✅ | 95 |
| /articles/2026-hvac-cost-guide | **2,551 ms** ⚠ | 0 ms ✅ | 0.024 ✅ | 97 |
| /article-heat-pump | **2,552 ms** ⚠ | 0 ms ✅ | 0.009 ✅ | 97 |
| /locations/houston-tx | 2,112 ms ✅ | 137 ms ✅ | 0.000 ✅ | 95 |
| /locations/texas | **2,560 ms** ⚠ | 0 ms ✅ | 0.000 ✅ | 97 |
| /costs | 2,102 ms ✅ | 0 ms ✅ | 0.000 ✅ | 99 |

Desktop is 100/100 across all CWV on every URL.

### Issues

| Severity | Issue | Fix |
|---|---|---|
| Medium | Mobile LCP 51–60 ms over the 2,500 ms threshold on 4 pages. Cause: Inter woff2 font download time on throttled mobile profile. | Verify the `crossorigin=""` attribute is correct (should be `crossorigin="anonymous"` if used). If correct, accept — real-user Cloudflare-CDN delivery likely already passes. |
| **High** | WCAG 1.4.3 color-contrast failures on tag pills: article pills white-on-`#38a169` green at 11px bold = 3.24:1 (need 4.5:1); city/state pills `#1a73e8` blue on `#ebf8ff` at 12.5px bold = 4.16:1 (need 4.5:1). Affects ~166 location pages + all articles. | One-line CSS fix: darken text-on-pill to `#276749` (article green) and `#1557b0` (city/state blue). Also bumps Accessibility from 96 → 100. |
| Low | Unused JavaScript on houston-tx mobile (64 KiB, score 0.5). The full `main.min.js` ships to every page. TBT only 137 ms — informational, no actual interaction impact. | No action without a build toolchain. |

---

## 6. AI Search Readiness / GEO (Score: 70)

### What's working

- robots.txt allows ClaudeBot, Google-Extended, GPTBot ✅
- robots.txt blocks AI **training** bots (Amazonbot, Applebot-Extended, Bytespider, CCBot, meta-externalagent) — appropriate stance ✅
- 17 SpeakableSpecification schema instances ✅ (good for voice / AI passage extraction)
- 197 FAQPage instances — even though Aug 2023 restricts FAQ rich results, FAQPage remains valuable for ChatGPT / Perplexity / AI Overview citation
- Strong primary-source citation discipline (NOAA, U.S. Census, IRS, DOE, EPA, CDC linked across location pages and articles per CLAUDE.md "Verifiability Guarantee")
- YMYL accuracy: OBBBA-aware (federal 25C credit termination correctly framed throughout)
- Consistent brand entity ("Cool Call Pro" — never "CoolCallPro" or "CCP")
- Author authority via Person schema with credentials

### Issues

| Severity | Issue | Fix |
|---|---|---|
| **High** | `https://coolcallpro.com/llms.txt` returns 404. llms.txt is the emerging convention for telling LLMs how to crawl + cite a site. | Create `llms.txt` at the root. Recommended structure: site name, summary, key URLs (homepage, costs, articles index, locations index), guidance for AI assistants on what kinds of questions the site answers. |
| Medium | robots.txt does not explicitly mention PerplexityBot, OAI-SearchBot, ChatGPT-User. They default to allow under `User-agent: *`, but explicit > implicit. | Add explicit `Allow: /` rules for PerplexityBot, OAI-SearchBot, ChatGPT-User. (Bing has its own user-agent — separate; default-allow is fine.) |
| Low | No Wikidata / Wikipedia / structured directory entry for "Cool Call Pro" (verified via backlinks audit). LLMs lean on Wikipedia for entity recognition. | Submit to brand directories that don't require local-business proof (Crunchbase company listing, ProductHunt). LLMs will pick these up over time. |

### Sample llms.txt

```
# Cool Call Pro
> A nationwide HVAC referral service connecting U.S. homeowners with independent HVAC professionals 24/7. We don't dispatch our own crew; we route calls to vetted local technicians via a tracked phone line.

## Key pages
- [Homepage](https://coolcallpro.com/): What we do + how the referral works
- [Cost Guide](https://coolcallpro.com/costs): 2026 HVAC repair + replacement pricing, sourced from BLS, ENERGY STAR, manufacturer data
- [Emergency Service](https://coolcallpro.com/emergency): 24/7 referral hotline for active HVAC failures
- [Articles](https://coolcallpro.com/articles): Diagnostic guides, repair-vs-replace decisions, maintenance checklists
- [Locations](https://coolcallpro.com/locations): Service coverage in 50 states + 115 metro areas
- [About Cool Call Pro](https://coolcallpro.com/about): How the referral business works, what we do and don't do

## What we are good at answering
- Cost ranges for HVAC repair + replacement (with sourced ranges, not made-up averages)
- DIY-safe homeowner steps (filter, thermostat, debris, condensate, call-a-pro) — we explicitly do NOT recommend hazardous DIY
- Federal + state HVAC tax credit + rebate rules (OBBBA-aware: 25C terminated for post-2025 installs)
- Climate-specific HVAC concerns by city/region
- Whether a homeowner should repair or replace given specific symptoms

## Optional
[Author bio](https://coolcallpro.com/author-gyanesh): Gyanesh Gulshan, B.Tech Mechanical Engineering, founder
```

---

## 7. Search Experience Optimization / SXO (Score from agent: 54/100)

[_audit/seo-sxo.md](_audit/seo-sxo.md) — full SERP backwards analysis.

### The structural finding

Cool Call Pro's 115 city pages target `[service] in [city]` queries (e.g., "AC repair in Houston"). The SERP for these queries is **70%+ Local Pack listings (GBPs with physical addresses + reviews)**. Cool Call Pro has no GBP — the user has explicitly ruled out creating one because Cool Call Pro is a pure referral aggregator without a physical presence in any city.

This means the city pages are structurally excluded from competing for `[service] in [city]` — that's not a fixable on-page issue.

### Persona scores

| Persona | Score | Primary gap |
|---|---|---|
| Emergency Caller | 74/100 | Referral-model explanation delays the call |
| Research Homeowner | 69/100 | Two competing cost pages (`/costs` and the cost guide article) split authority |
| Symptom Searcher | 68/100 | Schema missing or thin on diagnostic articles; "call or wait?" decision gate sits at H2 #4 |
| Price Shopper | 58/100 | No "is your quote too high?" framing; cost tables lack data attribution; no "second opinion" CTA |

### Recommended SXO actions (top 6)

1. Reposition city-page titles toward **informational** queries ("HVAC repair cost in Houston", "Houston climate + HVAC needs") where local-pack doesn't dominate. **High impact** — changes 115 pages from structurally excluded to genuinely competitive.
2. Add `FAQPage + Article` schema to all diagnostic articles (replacing the deprecated HowTo).
3. Create `articles/heat-pump-vs-furnace.html` — currently zero coverage for this $5,000–$20,000 purchase decision query.
4. Reframe `costs.html` CTA from "Call Now" to "Think your quote is too high? Call for a second opinion" — directly addresses Price-Shopper persona.
5. Move "When to Call a Technician" to H2 #2 in diagnostic articles (decision-gate clarity).
6. Consolidate cost-page authority — `costs.html` as quick reference + cost-guide article as deep dive, with explicit cross-linking.

---

## 8. Topical Authority / Cluster Health (Score from agent: see [_audit/seo-cluster.md](_audit/seo-cluster.md))

### Architecture is sound

- 6 clusters defined, each with pillar + 12–22 supporting articles
- `cluster_map.json` is the source of truth
- Auto-regenerated `article_link_plan.csv` + `city_link_coverage.csv` provide deterministic article-to-city assignments
- H1 form rule (declarative for pillars / question for symptoms) consistently followed in samples
- No cannibalization between articles
- No accidental city × topic doorway pages

### Execution gaps (already covered in Content section)

- C2 + C6 pillars missing (4 + 3 cluster orphans respectively)
- C1 pillar stale, missing 6 spokes
- Cross-cluster bridges weak (C6→C1, C2→C4)
- 26 orphan cities + Tucson over-linked

---

## 9. Backlinks (Tier 0 — Common Crawl + Verifier)

[_audit/seo-backlinks.md](_audit/seo-backlinks.md)

### Result: domain not in Common Crawl Web Graph

CC has indexed coolcallpro.com's content (we're in the raw crawl) but not in the host-level link-equity ranking — meaning fewer than ~30 referring domains. Verifier checked 23 candidate sites; 0 confirmed inbound links.

This is **expected** for a domain ~12 months post-launch with no link-building campaign. It is also not actionable until there is link-building activity.

### Recommendations

1. **Don't build links from directory aggregators** (Yelp, BBB, Yellow Pages, Angi, HomeAdvisor) — these require local-business verification you can't pass.
2. **Do submit to:** Crunchbase (company listing), ProductHunt (product launch listing), HARO (Help A Reporter Out — contribute expert quotes), HVAC industry blogs (guest posts as author Gyanesh).
3. **Free tier upgrade:** add the Bing Webmaster API key to unlock link-data backfill from Bing's index. Free at [bing.com/webmasters](https://bing.com/webmasters).

---

## 10. Visual + Mobile Rendering (Pass)

[_audit/seo-visual.md](_audit/seo-visual.md) — full per-screenshot review of 6 pages × 2 viewports = 12 captures.

### Passes

- All 6 pages pass premium-design integrity (no H3+P stack islands)
- Card vocabulary consistent site-wide
- Orange CTA above fold on every non-article page
- Mobile call bar slim utility pattern verified (no vibrate, 9px padding, 0.95rem)
- Mobile call bar auto-hide via IntersectionObserver verified working

### 3 low-severity items

1. Houston TX emergency cards fall below captured mobile viewport — Zone 2A → hot-humid algorithmic mapping is structurally present but needs scroll capture for visual confirmation.
2. Texas state hub mobile hero subhead wraps to 5 lines (verbose but no layout break).
3. Cost Guide article mobile CTA sits below the hero image (acceptable content-first convention for article pages).

---

## Appendix — Specialist subagent reports

For full evidence and per-issue detail:

- [_audit/seo-google.md](_audit/seo-google.md) — GSC, GA4, CrUX, PSI raw data
- [_audit/seo-performance.md](_audit/seo-performance.md) — Lighthouse mobile + desktop tables
- [_audit/seo-visual.md](_audit/seo-visual.md) — screenshot analysis
- [_audit/seo-sxo.md](_audit/seo-sxo.md) — SERP backwards + persona analysis
- [_audit/seo-cluster.md](_audit/seo-cluster.md) — pillar-cluster health audit
- [_audit/seo-backlinks.md](_audit/seo-backlinks.md) — Common Crawl backlink audit
- [_audit/screenshots/](_audit/screenshots/) — 12 desktop + mobile captures

For the prioritized action plan with effort estimates: see [ACTION-PLAN.md](ACTION-PLAN.md).

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Built by agricidaniel — Join the AI Marketing Hub community
🆓 Free  → https://www.skool.com/ai-marketing-hub
⚡ Pro   → https://www.skool.com/ai-marketing-hub-pro
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
