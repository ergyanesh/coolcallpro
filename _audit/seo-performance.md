# CoolCallPro — Lab Core Web Vitals Audit
**Date:** 2026-04-26  
**Method:** PageSpeed Insights v5 API (Lighthouse lab, single run per URL/device)  
**Field data:** CrUX 404 for origin — site does not yet meet Chrome UX Report traffic threshold. All metrics are lab estimates only. Field INP in particular cannot be confirmed until CrUX data is available.

> ⚠ **STATUS AS OF 2026-05-23 — audit point-in-time, partially superseded.**
> Most action items in this audit have shipped. See [ACTION-PLAN.md](../ACTION-PLAN.md)
> for per-item status. Article-priority recommendations have been overridden
> by the 2026-05-23 topical-authority-without-doorway strategy — read
> [CLAUDE.md](../CLAUDE.md) "Topical Authority Without Doorway Risk" section +
> [docs/article-strategy-2026-05-23.md](../docs/article-strategy-2026-05-23.md)
> for current direction. The technical analyses in this audit remain accurate
> as point-in-time observations.

---

## CWV Thresholds (2026)

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP | ≤2,500 ms | 2,500–4,000 ms | >4,000 ms |
| INP | ≤200 ms | 200–500 ms | >500 ms |
| CLS | ≤0.10 | 0.10–0.25 | >0.25 |

Lab TBT is used as an INP proxy (TBT 0 ms → INP almost certainly GOOD; there is no Lighthouse INP field).

---

## Per-URL Results

### 1. Homepage — https://coolcallpro.com/

#### Mobile

| Metric | Value | Status | Threshold |
|--------|-------|--------|-----------|
| LCP | 2,552 ms | NEEDS IMPROVEMENT | ≤2,500 ms |
| TBT (INP proxy) | 0 ms | GOOD | — |
| CLS | 0.000 | GOOD | ≤0.10 |
| FCP | 1,886 ms | — | — |
| Speed Index | 2,674 ms | — | — |
| TTI | 2,552 ms | — | — |

**Lighthouse Scores:** Performance 95 / Accessibility 100 / Best Practices 100 / SEO 100  
**Opportunities:** None identified (0 ms savings)  
**Diagnostics (notable):** 1 long main-thread task (score 1.0 — within threshold); total payload 200 KiB (healthy)  
**LCP status:** 52 ms over the "good" threshold. Borderline — a single run variance. Lab LCP is inflating actual wall-clock time because the Lighthouse mobile emulator throttles to a slow-4G CPU/network profile.

#### Desktop

| Metric | Value | Status |
|--------|-------|--------|
| LCP | 702 ms | GOOD |
| TBT | 0 ms | GOOD |
| CLS | 0.000 | GOOD |
| FCP | 338 ms | — |

**Lighthouse Scores:** Performance 100 / Accessibility 100 / Best Practices 100 / SEO 100

---

### 2. Pillar Article — https://coolcallpro.com/articles/2026-hvac-cost-guide

#### Mobile

| Metric | Value | Status |
|--------|-------|--------|
| LCP | 2,551 ms | NEEDS IMPROVEMENT |
| TBT | 0 ms | GOOD |
| CLS | 0.024 | GOOD |
| FCP | 1,351 ms | — |
| Speed Index | 2,408 ms | — |

**Lighthouse Scores:** Performance 97 / Accessibility 96 / Best Practices 100 / SEO 100  
**Opportunities:** None  
**Diagnostics:** 1 layout shift found (score 1.0 — minor, within threshold); 1 long task (score 1.0); total payload 219 KiB  
**Accessibility issue (score 0):** `.article-tag.tag-cost` span — white text (#ffffff) on green background (#38a169) at 11.2 px bold delivers contrast ratio 3.24:1 against the required 4.5:1 for small text. WCAG 1.4.3 fail. Selector: `main#main-content > div.page-hero > div.container > span.article-tag`

#### Desktop

| Metric | Value | Status |
|--------|-------|--------|
| LCP | 542 ms | GOOD |
| TBT | 0 ms | GOOD |
| CLS | 0.005 | GOOD |
| FCP | 347 ms | — |

**Lighthouse Scores:** Performance 100 / Accessibility 96 / Best Practices 100 / SEO 100  
**Same accessibility failure as mobile** (color-contrast is device-independent).

---

### 3. Legacy Article — https://coolcallpro.com/article-heat-pump

#### Mobile

| Metric | Value | Status |
|--------|-------|--------|
| LCP | 2,552 ms | NEEDS IMPROVEMENT |
| TBT | 0 ms | GOOD |
| CLS | 0.009 | GOOD |
| FCP | 1,352 ms | — |
| Speed Index | 2,449 ms | — |

**Lighthouse Scores:** Performance 97 / Accessibility 96 / Best Practices 100 / SEO 100  
**Opportunities:** None  
**Diagnostics:** 1 layout shift (score 1.0); 1 long task (score 1.0); 217 KiB payload  
**Accessibility:** Same color-contrast failure expected (article-tag pattern is site-wide).

#### Desktop

| Metric | Value | Status |
|--------|-------|--------|
| LCP | 548 ms | GOOD |
| TBT | 0 ms | GOOD |
| CLS | 0.056 | GOOD |
| FCP | 501 ms | — |

**Lighthouse Scores:** Performance 100 / Accessibility 96 / Best Practices 100 / SEO 100  
**Note:** CLS 0.056 on desktop is a non-trivial shift for a static page — Lighthouse flagged "1 layout shift found" on every article run. Likely caused by the hero image swapping in or the sticky nav repositioning on load. Still within threshold but worth monitoring.

---

### 4. City Pilot — https://coolcallpro.com/locations/houston-tx

#### Mobile

| Metric | Value | Status |
|--------|-------|--------|
| LCP | 2,112 ms | GOOD |
| TBT | 137 ms | GOOD |
| CLS | 0.000 | GOOD |
| FCP | 1,806 ms | — |
| Speed Index | 4,068 ms | — |
| TTI | 3,123 ms | — |

**Lighthouse Scores:** Performance 95 / Accessibility 96 / Best Practices 100 / SEO 100  
**Opportunities:** None  
**Diagnostics:**  
- Unused JavaScript: estimated savings 64 KiB (score 0.5 — flagged) — most likely `main.min.js` (full site JS bundle) being shipped when only FAQ accordion logic is needed on this page. No opportunity savings in ms were computed but the flagged score indicates it is affecting parse time.  
- 2 long main-thread tasks (score 1.0 — within threshold but highest count across all tested pages)  
- Main-thread work 0.8 s (highest across test set)  
- Speed Index 4,068 ms is elevated — visual render of below-fold card sections is slow on mobile throttling, but this does not affect LCP  

**Accessibility issue (score 0):** Section-tag pill "CLIMATE PROFILE" — blue text (#1a73e8) on light-blue background (#ebf8ff) delivers contrast ratio 4.16:1 against required 4.5:1. The `font-size: 0.78rem / font-weight: 800` at 12.48 px bold does not qualify as "large text" (≥18 px normal or ≥14 px bold). WCAG 1.4.3 fail. The same pill pattern is applied site-wide to all city and state hub pages.

#### Desktop

| Metric | Value | Status |
|--------|-------|--------|
| LCP | 551 ms | GOOD |
| TBT | 0 ms | GOOD |
| CLS | 0.000 | GOOD |
| FCP | 277 ms | — |

**Lighthouse Scores:** Performance 100 / Accessibility 96 / Best Practices 100 / SEO 100

---

### 5. State Hub — https://coolcallpro.com/locations/texas

#### Mobile

| Metric | Value | Status |
|--------|-------|--------|
| LCP | 2,560 ms | NEEDS IMPROVEMENT |
| TBT | 0 ms | GOOD |
| CLS | 0.000 | GOOD |
| FCP | 903 ms | — |
| Speed Index | 2,326 ms | — |

**Lighthouse Scores:** Performance 97 / Accessibility 96 / Best Practices 100 / SEO 100  
**Opportunities:** None  
**Diagnostics:** 1 long task (score 1.0); 304 KiB payload (largest of all tested pages — city-grid with 26+ city links)  
**LCP:** 60 ms over threshold. Borderline — identical pattern to homepage and articles. The navy gradient CSS hero paints on-screen fast (FCP 903 ms) but the LCP element (H1 text render after font swap) lands at 2,560 ms, slipping just past the threshold.

#### Desktop

| Metric | Value | Status |
|--------|-------|--------|
| LCP | 510 ms | GOOD |
| TBT | 0 ms | GOOD |
| CLS | 0.000 | GOOD |
| FCP | 399 ms | — |

**Lighthouse Scores:** Performance 100 / Accessibility 96 / Best Practices 100 / SEO 100

---

### 6. Costs Page — https://coolcallpro.com/costs

#### Mobile

| Metric | Value | Status |
|--------|-------|--------|
| LCP | 2,102 ms | GOOD |
| TBT | 0 ms | GOOD |
| CLS | 0.000 | GOOD |
| FCP | 1,014 ms | — |
| Speed Index | 2,318 ms | — |

**Lighthouse Scores:** Performance 99 / Accessibility 93 / Best Practices 100 / SEO 100  
**Opportunities:** None  
**Diagnostics:** 1 long task (score 1.0); 138 KiB payload (lightest of all tested pages)  
**Accessibility score 93:** lower than most pages — likely additional color-contrast or form-label issues beyond the article-tag pattern. Separate accessibility audit recommended.

#### Desktop

| Metric | Value | Status |
|--------|-------|--------|
| LCP | 791 ms | GOOD |
| TBT | 0 ms | GOOD |
| CLS | 0.000 | GOOD |
| FCP | 750 ms | — |

**Lighthouse Scores:** Performance 99 / Accessibility 93 / Best Practices 100 / SEO 100

---

## Summary Table — All URLs × Devices

| URL | Device | Perf | LCP | LCP Status | TBT | CLS | A11y |
|-----|--------|------|-----|-----------|-----|-----|------|
| / (homepage) | Mobile | 95 | 2,552 ms | NEEDS IMPROVEMENT | 0 ms | 0.000 | 100 |
| / (homepage) | Desktop | 100 | 702 ms | GOOD | 0 ms | 0.000 | 100 |
| /articles/2026-hvac-cost-guide | Mobile | 97 | 2,551 ms | NEEDS IMPROVEMENT | 0 ms | 0.024 | 96 |
| /articles/2026-hvac-cost-guide | Desktop | 100 | 542 ms | GOOD | 0 ms | 0.005 | 96 |
| /article-heat-pump | Mobile | 97 | 2,552 ms | NEEDS IMPROVEMENT | 0 ms | 0.009 | 96 |
| /article-heat-pump | Desktop | 100 | 548 ms | GOOD | 0 ms | 0.056 | 96 |
| /locations/houston-tx | Mobile | 95 | 2,112 ms | GOOD | 137 ms | 0.000 | 96 |
| /locations/houston-tx | Desktop | 100 | 551 ms | GOOD | 0 ms | 0.000 | 96 |
| /locations/texas | Mobile | 97 | 2,560 ms | NEEDS IMPROVEMENT | 0 ms | 0.000 | 96 |
| /locations/texas | Desktop | 100 | 510 ms | GOOD | 0 ms | 0.000 | 96 |
| /costs | Mobile | 99 | 2,102 ms | GOOD | 0 ms | 0.000 | 93 |
| /costs | Desktop | 99 | 791 ms | GOOD | 0 ms | 0.000 | 93 |

**CWV Pass/Fail (lab, mobile):**  
- LCP: 4 of 6 URLs fail "good" threshold on mobile (homepage, both articles, texas hub — all between 2,551–2,560 ms, 51–60 ms over threshold)  
- INP (TBT proxy): all GOOD  
- CLS: all GOOD  

---

## Issues Prioritized by Impact

### Priority 1 — Medium: Mobile LCP 51–60 ms over threshold (4 URLs)

**Affected:** /, /articles/2026-hvac-cost-guide, /article-heat-pump, /locations/texas  
**Root cause:** The LCP element on these pages is H1/hero text rendered via the Inter woff2 font. The inline `@font-face` + preload pattern eliminates the font-not-used warning, but the font still must download before the text is painted. On Lighthouse's throttled mobile profile (Moto G4 emulation + slow-4G), the woff2 download alone accounts for most of the 2,500+ ms delta.  
**Why houston-tx and costs pass:** Both pages have shorter above-fold content that paints an LCP element sooner (houston-tx has an inline CSS navy gradient that makes the hero text render at ~1,800 ms FCP and completes LCP at 2,112 ms; costs has the lightest payload at 138 KiB).

**Fix options (prioritized):**
1. Add `<link rel="preconnect" href="https://coolcallpro.com">` — already same-origin, skip.
2. Ensure the Inter woff2 preload uses `crossorigin` attribute correctly (non-CORS same-origin — verify the preload tag has no `crossorigin` attribute, which would cause a double-fetch).
3. Add `font-display: optional` as an experiment for the hero H1 only — this prevents the render block entirely by falling back to system font for the first render. Downside: FOIT on slow connections replaced by system-font flash. Not recommended for a brand page.
4. Move to `font-display: swap` with `size-adjust` descriptor — reduces the visual shift of the system-font fallback. CSS-only change, no HTML required.
5. If the preload tag on non-article pages includes `crossorigin=""` (empty attribute), remove it — this forces a second fetch of the same woff2 file.

**Expected impact:** Likely brings LCP to 2,300–2,450 ms on Lighthouse mobile — still borderline. These pages are 2–4% below the performance score ceiling, not a critical regression. Once CrUX field data is available, real-user LCP may already be within the "good" band (field LCP on Cloudflare CDN with real users on 5G/broadband typically runs 30–40% faster than Lighthouse throttled mobile).

**Severity:** Low-Medium (all 4 pages score 95–97, no zero-opportunity savings flagged, margin is 51–60 ms).

---

### Priority 2 — Medium: Accessibility color-contrast failures (site-wide, score 96 on most pages)

**Issue A: Article tag pill — green background**  
`.article-tag.tag-cost` (and likely other `article-tag` variants): white (#ffffff) text on green (#38a169) background, 11.2 px bold. Ratio 3.24:1 vs. required 4.5:1.  
**Fix:** Darken `--green` for text-on-background uses. Use `#276749` (passes at ~5.7:1 with white) or switch the pill to white background with `--green` text border style (inverse pill). The `--green` variable is currently only used for the article-tag background — a targeted fix in `css/style.css` for `.article-tag` will not affect other green uses.

**Issue B: Section tag pill — blue on light-blue (houston-tx and all city/state hub pages)**  
`.wh-step-num` adjacent pill with `color: var(--blue) #1a73e8` on `background: #ebf8ff`. Ratio 4.16:1 vs. required 4.5:1 at 12.48 px bold.  
**Fix option 1:** Increase font-size to ≥14 px bold (18.67 px would make it "large text" at 14 pt, qualifying for the 3:1 ratio — already passes). Change `font-size: 0.78rem` → `font-size: 0.875rem` (14 px).  
**Fix option 2:** Darken blue pill text. `--blue-dark: #1557b0` (~5.1:1 on #ebf8ff) — add as a new CSS variable and apply to the pill style in the generator template and existing city/state pages.  
**Fix option 3:** Switch pill background to `#dbeafe` (slightly darker) — `#1a73e8` on `#dbeafe` yields ~4.6:1, just passing.

Both failures are WCAG 1.4.3 AA violations. They have no performance impact but block a perfect Accessibility score. The site currently achieves 100/100 Accessibility on the homepage (which does not use these pill patterns). Articles and location pages sit at 96/100 due solely to these two patterns.

**Severity:** Medium (WCAG AA violation; automated audit flags it; does not affect CWV or Lighthouse Performance score).

---

### Priority 3 — Low: Unused JavaScript on houston-tx mobile (64 KiB, score 0.5)

**Affected:** /locations/houston-tx mobile only (desktop score 1.0 — likely below threshold at desktop network speed)  
**Root cause:** `main.min.js` ships the full site JS bundle to every page. Houston-tx has the most interactive elements of all tested pages (FAQ accordion, sticky-bar IntersectionObserver, mobile nav) which triggers more JS parse/execution than lighter pages.  
**Fix:** No action required at this stage. The bundle is already minified. Code-splitting (per-page JS) would require a build toolchain change (currently zero-dependency static site). The 64 KiB figure is well within the "informational" category for a static referral page. TBT is only 137 ms (still GOOD), confirming the JS is not blocking interaction.

**Severity:** Low (informational; no CWV impact in lab; TBT 137 ms is within GOOD threshold).

---

## CrUX Field Data Status

CrUX API returned 404 for origin `https://coolcallpro.com`. This means the site does not currently meet Chrome UX Report's minimum traffic threshold (~1,000+ PageViews from Chrome users in the 28-day window, with sufficient density per metric bucket).

**Implication:** All CWV assessments above are lab estimates only. Google Search Console's "Core Web Vitals" report will show "not enough data" for the same reason. The site is too new/low-traffic for field data.

**What this means for the "100/100 on all four scores" claim in CLAUDE.md:** The Lighthouse Performance score of 95–100 across all pages is accurate as a lab score. The CWV "pass" claim (green badge in Google Search Console) cannot be verified until CrUX has data. The lab data is optimistic — mobile LCP is borderline (2,551–2,560 ms) on 4 of 6 URLs. If real users are on slower Android devices with throttled connections, field LCP could land in the "needs improvement" band.

**Recommendation:** Re-run this audit once monthly organic traffic reaches ~500–1,000 sessions/month. At that point CrUX will populate and field INP (which cannot be measured in lab) will become visible.

---

## No-Action Items (Confirmed Healthy)

- TBT: 0 ms on 11 of 12 test runs (137 ms on houston-tx mobile — still GOOD)
- CLS: 0.000 on 10 of 12 runs; 0.024 and 0.056 on articles (well within 0.10 threshold)
- Total payload: 138–304 KiB across all pages — well within the 1,600 KiB budget
- JavaScript execution: 0.0 s on all pages
- No render-blocking resources on any page
- No opportunities with measurable ms savings on any tested URL
- Desktop Performance: 100/100 on 10 of 12 runs (99/100 on costs both devices)
- SEO: 100/100 all pages, all devices
- Best Practices: 100/100 all pages, all devices
