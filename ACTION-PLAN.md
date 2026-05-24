# Cool Call Pro — SEO Action Plan

**Generated:** 2026-04-26
**Companion to:** [FULL-AUDIT-REPORT.md](FULL-AUDIT-REPORT.md)
**Health Score:** 79/100

---

> ⚠ **STATUS AS OF 2026-05-23 — most of this plan has shipped.**
>
> CRITICAL items (C1-C4): **ALL DONE.** HowTo schema removed (commit
> `0352869`), EmergencyService → Service (live in emergency.html),
> cost-guide indexation (79 internal links + sitemap entry), tag-pill
> contrast (commit `1ca9d90`).
>
> HIGH items (H1-H6): **5 of 6 DONE.** llms.txt fixed 2026-05-23
> (commit `3a24108`), C1 pillar spokes (`14e3664`), H3 city-page
> repositioning shipped as Track B + Phase 3 enrichment on
> 2026-05-22 (commits `ac57848` + `6684309`), C2 furnace pillar
> live, C6 maintenance pillar live, emergency.html title-CTR
> rewrite live.
>
> MEDIUM items (M1-M9): **8 of 9 DONE.** Only M6 (orphan-city
> distribution) is partial — was 26, now 15. Simulations
> 2026-05-23 showed weight tuning alone cannot reduce further;
> waiting for more articles per `docs/article-strategy-2026-05-23.md`.
> M7 (pagespeed_check.py patch) lives in external claude-seo skill,
> not this repo.
>
> LOW items (L1-L6): **user-owned backlog** — Crunchbase, HARO,
> Bing API, etc. Out of agent scope.
>
> **H3 "test cohort then expand or pivot" recommendation is OBSOLETE.**
> The 25-day GSC re-measure on 2026-05-22 showed 0 clicks → Track B
> framing pivot was the call; shipped same day.
>
> **Article strategy in this document predates the 2026-05-23
> topical-authority-without-doorway override.** Don't apply the
> H3/H4/H5/H6 article-priority recommendations literally — read
> `CLAUDE.md` "Topical Authority Without Doorway Risk" section +
> `docs/article-strategy-2026-05-23.md` for the current Phase 1 menu.
>
> Current task list: see `NEXT-TASKS.txt` at repo root.

---

## How to read this

| Priority | Definition | Target |
|---|---|---|
| **CRITICAL** | Blocks indexing, causes penalties, or violates a hard rule | Fix this week |
| **HIGH** | Significantly impacts rankings or revenue | Fix within 1 week |
| **MEDIUM** | Optimization opportunity | Fix within 1 month |
| **LOW** | Nice-to-have | Backlog |

Effort estimates assume working at a steady pace, no major refactoring. Multiply ×2 if you need to coordinate with anyone else.

---

## CRITICAL — fix this week

### C1. Remove deprecated `HowTo` schema from 12 articles
**Effort:** ~30 min total
**Impact:** Removes Google quality-signal regression risk on 12 indexed articles
**Source:** [FULL-AUDIT-REPORT.md §4](FULL-AUDIT-REPORT.md#4-schema--structured-data-score-65)

**Files:** `article-fall-prep.html`, `article-maintenance.html`, `article-spring-ac.html`, `article-winter-storm.html`, `articles/ac-circuit-breaker-trips.html`, `articles/ac-contactor-clicking.html`, `articles/ac-freezing-up-in-summer.html`, `articles/ac-not-cooling-below-80.html`, `articles/complete-ac-troubleshooting-guide.html`, `articles/hvac-leaking-water-inside-house.html`, `articles/thermostat-blank-ac-wont-start.html`, `articles/water-dripping-from-vent.html`

**How:** One-shot Python script that removes the `<script type="application/ld+json">…@type: HowTo…</script>` block from each file. Keep the visible step-by-step content as plain HTML — only the schema goes.

**Verification:** `grep -rln '"@type"\s*:\s*"HowTo"' --include="*.html"` should return zero matches in production files.

---

### C2. Replace `EmergencyService` schema on `emergency.html`
**Effort:** ~10 min
**Impact:** Removes hard-rule violation (LocalBusiness subclass on a site with no physical presence)
**Source:** [FULL-AUDIT-REPORT.md §4](FULL-AUDIT-REPORT.md#4-schema--structured-data-score-65)

`EmergencyService` inherits from `LocalBusiness`. Change to a generic `Service` and drop `OpeningHoursSpecification`:

```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Cool Call Pro 24/7 HVAC Referral Hotline",
  "description": "24/7 referral service connecting U.S. homeowners with independent HVAC professionals for emergency AC, furnace, and heat pump repair.",
  "provider": { "@type": "Organization", "name": "Cool Call Pro", "url": "https://coolcallpro.com" },
  "serviceType": "HVAC Emergency Referral",
  "areaServed": { "@type": "Country", "name": "United States" },
  "audience": { "@type": "Audience", "audienceType": "Homeowners" }
}
```

---

### C3. Bring `articles/2026-hvac-cost-guide` to indexation
**Effort:** ~15 min
**Impact:** Unblocks indexing of a flagship pillar article currently invisible to Google
**Source:** [FULL-AUDIT-REPORT.md §3](FULL-AUDIT-REPORT.md#the-big-issue--titlemeta-intent-mismatch)

GSC URL Inspection reports "URL is unknown to Google." Three checks:

1. **Confirm the URL is in `sitemap.xml`** (it should be — `grep '2026-hvac-cost-guide' sitemap.xml`)
2. **Confirm internal pages link to it** — search for the slug in other articles + costs.html. If it's only linked from `articles.html`, that may be too few signals.
3. **Push reindex via the Indexing API** (we have credentials):
   ```
   python C:\Users\gyane\.claude\skills\seo\scripts\indexing_notify.py https://coolcallpro.com/articles/2026-hvac-cost-guide
   ```
4. Add a card link from costs.html to the cost guide article (and vice versa) for permanent linking.

---

### C4. Fix WCAG 1.4.3 color-contrast on tag pills (site-wide)
**Effort:** ~5 min CSS edit + minify + commit
**Impact:** Lighthouse Accessibility 96 → 100; affects ~166 location pages + all articles
**Source:** [_audit/seo-performance.md](_audit/seo-performance.md)

In `css/style.css`:

| Class | Current text color | Change to | Background |
|---|---|---|---|
| Article tag pills (green) | white on `#38a169` (3.24:1) | `#276749` on white | needs 4.5:1 |
| City/state section pills (blue) | `#1a73e8` on `#ebf8ff` (4.16:1) | `#1557b0` on `#ebf8ff` | gets 4.5:1 |

Then re-run `npx --yes clean-css-cli css/style.css -o css/style.min.css` per CLAUDE.md and commit.

---

## HIGH — fix within 1 week

### H1. Add `llms.txt` at site root
**Effort:** ~30 min
**Impact:** Direct boost to AI search citability (ChatGPT, Perplexity, Google AI Overviews)
**Source:** [FULL-AUDIT-REPORT.md §6](FULL-AUDIT-REPORT.md#6-ai-search-readiness--geo-score-70)

Use the draft in [FULL-AUDIT-REPORT.md §6](FULL-AUDIT-REPORT.md#sample-llmstxt). Save as `llms.txt` at project root. `build.sh` should already include it via the wildcard filter — verify with a deploy.

---

### H2. Update C1 pillar with 6 missing spoke links
**Effort:** ~30 min
**Impact:** Restores PageRank distribution to 6 underserved articles in the C1 cluster
**Source:** [_audit/seo-cluster.md](_audit/seo-cluster.md)

Edit `articles/complete-ac-troubleshooting-guide.html` and add inline links + sidebar entries for: `ac-freezing-up-in-summer`, `ac-not-cooling-below-80`, `ac-circuit-breaker-trips`, `thermostat-blank-ac-wont-start`, `ac-contactor-clicking`, `water-dripping-from-vent`.

After commit: run `python generate_link_plan.py` to refresh PROGRESS.md + the link CSVs.

---

### H3. Reposition city-page titles toward informational queries
**Effort:** ~3 hours (115 city pages, but template-driven so it's a generator change)
**Impact:** Massive — current city pages are at avg position 28–50 because SERP is GBP-locked. Repositioning escapes the local-pack exclusion.
**Source:** [_audit/seo-sxo.md](_audit/seo-sxo.md), [FULL-AUDIT-REPORT.md §3](FULL-AUDIT-REPORT.md#the-big-issue--titlemeta-intent-mismatch)

In `generate_city_pages_v3.py`, change the `<title>` template from:
- ❌ Current: "24/7 AC Repair & Emergency HVAC Service in [City], [ST]"
- ✅ Better: "[City] HVAC Cost & Climate Guide ([Year]) | Cool Call Pro"

The same goes for state hubs in `generate_state_hubs.py`. Pick 2–3 candidate title templates, regenerate one batch (e.g., 10 cities), and let it sit for 2–3 weeks to see if rankings shift before regenerating all 115. Don't change all 115 at once — do a test cohort.

---

### H4. Write the C2 furnace pillar
**Effort:** ~6–10 hours (one full pillar article)
**Impact:** Stops cluster equity bleed in C2; unblocks remaining C2 cluster article writing
**Source:** [_audit/seo-cluster.md](_audit/seo-cluster.md)

Per `cluster_map.json`, this is article #8 in the priority queue. Slug: `furnace-not-working-diagnostic-guide`. Follow `.agents/SKILLS/hvac-article-writer.md`.

Don't write any more C2 cluster articles until this pillar is live.

---

### H5. Write the C6 maintenance pillar
**Effort:** ~6–10 hours
**Impact:** Same as C2 — orphaned cluster equity recapture
**Source:** [_audit/seo-cluster.md](_audit/seo-cluster.md)

Slug: `year-round-hvac-maintenance-playbook`. Currently at position 26 in the queue — move forward to position 4–6.

---

### H6. Improve title tag CTR on emergency-HVAC pages
**Effort:** ~2 hours analysis + edit
**Impact:** 0 → some clicks on the highest-impression query cluster
**Source:** [FULL-AUDIT-REPORT.md §3](FULL-AUDIT-REPORT.md#the-big-issue--titlemeta-intent-mismatch)

Top emergency-HVAC queries (277 / 190 / 165 / 151 / 135 / 122 / 110 / 100 impressions, all at position 14–20). Audit `emergency.html` + 5–10 city pages currently ranking for these. Improve:

1. **Title:** include "free quote" / "no obligation" / "available now" — emotional + utilitarian hooks
2. **Meta description:** lead with the differentiator (24/7 / nationwide / $0 obligation)
3. **H1:** match search-intent verbatim where possible

Re-run after 14 days to measure CTR delta in GSC.

---

## MEDIUM — fix within 1 month

### M1. Add explicit AI bot rules to robots.txt
**Effort:** ~5 min
**Impact:** Defensive — explicit > implicit, especially as AI bots multiply

Add to `robots.txt`:

```
# Allow modern AI search/citation crawlers
User-agent: PerplexityBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /
```

---

### M2. Add `<link rel="canonical">` to `404.html`
**Effort:** ~2 min
**Impact:** Cosmetic / completeness

`<link rel="canonical" href="https://coolcallpro.com/404">`

---

### M3. Update `audit_script.py` to understand clean URLs
**Effort:** ~30 min
**Impact:** Restores audit_script.py as a useful tool — currently the broken-link count is unusable (23K false positives)
**Source:** [FULL-AUDIT-REPORT.md §1](FULL-AUDIT-REPORT.md#issues-found)

When checking an `<href>`, try both `<href>` and `<href>.html` against the file system. If either exists, the link is valid.

---

### M4. Add `Article` + `FAQPage` schema to remaining diagnostic articles
**Effort:** ~30 min
**Impact:** AI citation + Google rich result eligibility for FAQ
**Source:** [_audit/seo-sxo.md](_audit/seo-sxo.md)

After C1 (HowTo removal), add the standard `Article` + `FAQPage` blocks per the template in `.agents/SKILLS/hvac-article-writer.md`.

---

### M5. Cross-cluster link bridges
**Effort:** ~1 hour
**Impact:** Internal PageRank distribution across clusters
**Source:** [_audit/seo-cluster.md](_audit/seo-cluster.md)

In `article-maintenance.html`: add 2 sentences linking C6→C1 (maintenance prevents AC emergencies, see {AC troubleshooting pillar}).

In `article-furnace.html` (and other C2 articles): redirect cost-related anchors from `/costs` (static page) to `/articles/2026-hvac-cost-guide` (the cost pillar).

---

### M6. Fix orphan-city link distribution
**Effort:** ~30 min code change + regenerate
**Impact:** Equity to 26 currently-orphan cities

In `article_city_linker.py`, adjust the climate-zone weights so cold-zone pending articles preferentially route to NYC, Columbus, Providence, Buffalo, etc. (currently underweight).

Cap Tucson's per-article inbound at 2 (currently 7) — it's pulling all the hot-humid weight.

Then run `python generate_link_plan.py` and commit the regenerated CSVs + PROGRESS.md.

---

### M7. Patch `pagespeed_check.py` `KeyError: audit_details`
**Effort:** ~10 min
**Impact:** Restores PSI lab data collection in this audit's tooling

Initialize `result["audit_details"] = {}` before the audit-detail population loop (see [_audit/seo-google.md](_audit/seo-google.md)).

---

### M8. Create `articles/heat-pump-vs-furnace.html` comparison article
**Effort:** ~6–10 hours
**Impact:** New ranking surface for a $5,000–$20,000 purchase decision query that currently has zero coverage
**Source:** [_audit/seo-sxo.md](_audit/seo-sxo.md)

Comparison-format article. Per CLAUDE.md "H1 framing" rule: declarative form ("Heat Pump vs. Furnace: Which to Choose in [Year]"), not question form.

---

### M9. Reframe cost-guide CTAs for price-shopper persona
**Effort:** ~30 min
**Impact:** Addresses the lowest-scoring persona (Price Shopper, 58/100)
**Source:** [_audit/seo-sxo.md](_audit/seo-sxo.md)

In `costs.html` + `articles/2026-hvac-cost-guide`, change at least one Call Now CTA from:
- ❌ "Call Now — (844) 582-1795"
- ✅ "Got a quote that feels too high? Call us for a free second opinion — (844) 582-1795"

---

## LOW — backlog

### L1. Submit to Crunchbase / ProductHunt
**Effort:** ~1 hour
**Impact:** Provides Wikipedia/Wikidata signal for LLM entity recognition

### L2. Apply to HARO (Help A Reporter Out) as HVAC expert
**Effort:** ongoing (~30 min/week)
**Impact:** High-quality editorial backlinks over time

### L3. Add Bing Webmaster API key to claude-seo
**Effort:** ~30 min
**Impact:** Unlocks Tier 1 backlink data (free at bing.com/webmasters)

### L4. Capture below-fold scroll screenshots for visual verification
**Effort:** ~15 min
**Impact:** Confirms Houston TX climate-card mapping (NO AC / NO HEAT / WATER LEAK) renders as expected
**Source:** [_audit/seo-visual.md](_audit/seo-visual.md)

### L5. Trim Texas state hub mobile subhead from 5 lines to 2-3
**Effort:** ~5 min
**Impact:** Mobile readability polish

### L6. Re-tune `audit_script.py` readability heuristic
**Effort:** ~30 min
**Impact:** Removes the false "99% low readability" alert (currently a known limitation)

---

## Recommended week-1 sprint (in order)

If you do nothing else, do these in this order:

1. **C2** — fix EmergencyService schema (10 min)
2. **C4** — fix tag-pill color contrast (5 min)
3. **C1** — remove HowTo schema (30 min)
4. **C3** — bring cost guide to indexation (15 min)
5. **H1** — add llms.txt (30 min)
6. **H2** — update C1 pillar with missing spokes (30 min)

Total: ~2 hours for 6 high-leverage fixes that take the score from 79 to ~85 + remove all hard-rule violations + recover 6 orphan articles.

The bigger wins (H3 city-page repositioning, H4/H5 pillar writing, H6 emergency-HVAC title-CTR work) need 1–2 weeks each but are where the page-2 → page-1 migration starts.

---

## Suggested next step

To track progress, the audit can be re-run weekly. To capture a baseline today so future runs can detect drift:

```
python C:\Users\gyane\.claude\skills\seo\scripts\drift_baseline.py https://coolcallpro.com
```

After running fixes, re-audit:

```
/seo audit https://coolcallpro.com
```

Or re-audit a single category:

```
/seo schema https://coolcallpro.com
/seo content https://coolcallpro.com
```

---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Built by agricidaniel — Join the AI Marketing Hub community
🆓 Free  → https://www.skool.com/ai-marketing-hub
⚡ Pro   → https://www.skool.com/ai-marketing-hub-pro
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
