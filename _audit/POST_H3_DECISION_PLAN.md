# Post-H3 Decision Plan

**Created:** 2026-04-26 (right after H3 cohort + Phase 1/2 audit fixes shipped to live)
**First checkpoint:** ~2026-05-03 (≈7 days after push) — "is anything moving?"
**Decision deadline:** 2026-05-17 (21 days, per H3_TEST_COHORT.md) — "expand, revert, or pivot?"

> ✅ **DECISION COMPLETE 2026-05-22 — Track B shipped.** Verdict was
> "deeper framing pivot" because Track A (title-only) failed the
> decision criteria (0 clicks on 15,315 cohort impressions, position
> improved only 0.5 places vs ≥3 required). All 115 city pages
> regenerated 2026-05-22 with the Track B template (commits
> `ac57848` + `6684309`). Cloudflare Pages had a corrupted-blob
> failure mode that required a fresh-hash redeploy; documented
> permanently as `<meta name="generator">` build-stamp in v4
> generator + `reference_cloudflare_pages_failed_upload_recovery`
> memory + `NEXT-TASKS.txt`.
>
> The "Independent tracks" recommendations in this plan (write H4
> furnace pillar + M8 heat-pump-vs-furnace + L1-L4 backlog) are
> mostly DONE — H4 + M8 + H5 maintenance pillar all shipped.
> Article-writing recommendations should now be read from
> `docs/article-strategy-2026-05-23.md` (new strategy, see
> CLAUDE.md "Topical Authority Without Doorway Risk" section).
>
> This plan is retained as historical record of the decision process.

---

## The strategic context (read first)

The H3 title test cohort is an experiment to see whether changing 10 city-page titles from `24/7 [Service] in [City], [ST]` to `[City] [Service] Repair Cost & 24/7 …` lifts CTR from page-2 invisibility.

**A bigger question sits underneath the H3 experiment:** the doorway-page hypothesis (per 2026-04-26 conversation). Google may be classifying all 115 city pages as "fake local" — pages framed as local businesses without GBP/NAP/local proof. If true, just swapping titles won't fix the underlying classifier signal; the page H1, framing, and content also need to clearly position the site as a referral aggregator, not as a local HVAC contractor.

So the post-H3 work has **two independent tracks** that the GSC data will help us pick between:

- **Track A — H3 won.** CTR + position improved on cohort cities. Action: roll out the title pattern to the other 105 cities + update the city generator. Limited additional framing work needed.
- **Track B — H3 was insufficient.** CTR/position flat or worse on cohort. Action: deeper framing pivot — rewrite H1, add prominent "we are an aggregator, not a local contractor" disclosure, possibly reduce the 115-city footprint to ~20 deeper city pages.

---

## Step 1 (now → 2026-05-03): Verify Google has re-crawled

In Google Search Console:

1. **URL Inspection** on each of the 10 cohort cities. Look for:
   - "URL is on Google" verdict
   - "Last crawled" date — should show a date AFTER 2026-04-26
   - The "Indexed page" view should show the NEW title (e.g., "Houston AC Repair Cost & 24/7 Emergency HVAC | Cool Call Pro"), not the old one

2. **Request Indexing** on any cohort city that hasn't been re-crawled by ~2026-05-03. Quota: ~10–20 URLs/day.

3. **Also URL Inspection on:**
   - `coolcallpro.com/articles/2026-hvac-cost-guide` (was unknown to Google per audit — should be discoverable now)
   - `coolcallpro.com/emergency` (title CTR rewrite needs re-crawl to take effect in SERP)
   - `coolcallpro.com/llms.txt` (new file — confirm it's reachable)

If Google hasn't re-crawled by 2026-05-03, the H3 data won't be ready. Push back the decision deadline by however many days the re-crawl takes.

---

## Step 2 (around 2026-05-10 to 2026-05-17): Read the GSC data

In Search Console → Performance → Search results, filter by URL containing each cohort city slug. Compare these metrics for **last 14 days vs the prior 14 days** (gives you the post-cohort window vs the pre-cohort window):

| Metric | What it tells us |
|---|---|
| **Total impressions** | If they go DOWN, Google is showing the page less often (could be doorway-page classifier signal) |
| **Total clicks** | The actual revenue-relevant outcome — were users clicking? |
| **Avg CTR** | The pure title CTR effect (clicks / impressions) |
| **Avg position** | Did Google rank the page higher in SERPs? (Lower number = higher rank) |

Also look at the **Top queries** filter for each cohort city. The new pattern is supposed to pull these page into a different SERP class:
- BEFORE: queries like `ac repair houston`, `hvac near me houston`
- AFTER: queries like `ac repair cost houston`, `houston ac repair`, `houston hvac cost`
- If the post-cohort queries are still the same `[service] in [city]` pattern as before, the SERP class didn't shift and the title change failed.

---

## Step 3: Choose a track based on the data

### Track A — H3 won (any of these signals)

- Cohort cities show CTR up >1% (was 0%)
- Position improved by ≥3 places
- Top queries shifted toward cost/repair patterns

**Action plan:**
1. Apply the climate-aware title pattern to the other 105 cities. Same Python script approach as the cohort.
2. Update `generate_city_pages_v4.py` so future regenerations stay correct.
3. Bump sitemap.xml `<lastmod>` for all 115 cities so Google re-crawls quickly.
4. Update H3_TEST_COHORT.md status to "rolled out."
5. Move on to article writing track + framing pivot prep (lower priority).

### Track B — H3 was insufficient (any of these signals)

- Cohort cities show CTR still ~0%
- Impressions DROPPED (signal of quality classifier kicking in)
- Position worsened or flat

**Action plan — the framing pivot:**

This is bigger work, ~6–10 hours. Update `generate_city_pages_v4.py` template:

1. **Reframe H1** — change from `24/7 [Service] Repair & Emergency HVAC Service in [City], [ST]` to a clearly-aggregator framing:
   - Option: `[City] HVAC Referral Hotline: Connect 24/7 with Independent Technicians`
   - Option: `Connect with HVAC Pros in [City], [ST] — 24/7 Referral Service`
   - Option: `[City] HVAC Service Locator: Find Independent Technicians 24/7`
2. **Add prominent above-the-fold "we route, we don't dispatch" disclosure** — a small banner or hero-paragraph clarifying we connect callers to independent local technicians, not dispatch our own crew. Currently this is in the footer disclaimer; move it to where Google's classifier sees it on first crawl.
3. **Add per-city cost summary section** matching the title's cost-intent — a 3-5 line cost range table per city (uses the costs.html data, not new figures). Solves the intent-mismatch bounce risk.
4. **Add a "What HVAC issues are common in [City]?" section** with 2-3 city-specific paragraphs pulled from the local-context column in `cities_updated.xlsx`. This adds genuine per-city differentiation that the near-duplicate classifier rewards.
5. Regen all 115 city pages from the updated generator.
6. Re-submit sitemap to Google.
7. Wait another 21 days, re-measure.

If Track B still doesn't move the needle after 21 more days: serious consideration of reducing the 115-city footprint to ~20 metros with much deeper, genuinely unique content. That's a structural decision worth its own discussion.

### Mixed signal — some climates win, some don't

If hot-zone cities improved but cold-zone didn't (or vice versa), keep the winning-climate cohorts and revert losing-climate cohorts. Then expand only the winning pattern.

---

## Independent tracks (do these regardless of H3 outcome)

These don't depend on the H3 data and shouldn't wait:

### Article writing — high priority, start now

The cluster authority work is independent of city-page strategy. The 7-10 day measurement window is a perfect time to write articles in parallel. Recommended order:

| Article | Why this order |
|---|---|
| **H4 — C2 furnace pillar** (`furnace-not-working-diagnostic-guide`) | 4 C2 cluster articles already shipped are bleeding equity because the pillar doesn't exist. Writing the pillar plugs that bleed AND links the existing articles together. |
| **M8 — Heat pump vs gas furnace** (`heat-pump-vs-gas-furnace.html` per cluster_map.json) | Replacement/comparison intent — high MarketCall payout per call (~3-5x repair payouts per industry standard). Opens new ranking surface. |
| **H5 — C6 maintenance pillar** | Lower priority because existing `article-maintenance.html` already covers most of this surface. May be possible to upgrade `article-maintenance.html` into the pillar instead of writing a new one — needs editorial decision. |

Each pillar = 6–10 hours of work (per `.agents/SKILLS/hvac-article-writer.md`). Each cluster article = 3–5 hours.

**Cadence:** A reasonable rhythm is one article per week. Either one pillar OR one pillar + one cluster article per week. Two pillars in a week is overkill — review fatigue degrades quality.

**Before drafting any pillar:** schedule a 15-min brainstorm with me to agree on slug, H1 form, 8-10 H2 headings, and which spokes to link. Then I draft, you review, I iterate. One pillar per session, never multiple.

### Backlog (low priority but doesn't wait)

- **L1** — Submit "Cool Call Pro" to Crunchbase + ProductHunt (~1 hour, your accounts)
- **L2** — Apply to HARO at helpareporter.com (~30 min sign-up)
- **L3** — Get a Bing Webmaster Tools API key (~30 min, Microsoft account)
- **M6** — Orphan-city link distribution forward-fix (~30-60 min, my work)
- **L4** — Capture Houston-TX below-fold screenshots for visual verification (~15 min, my work)

I can knock out **M6 + L4** in one short session whenever you say go.

---

## What to double-check before assuming H3 is the bottleneck

The doorway-page hypothesis is well-grounded but it's still a hypothesis. Before committing to the framing pivot in Track B, also rule out:

1. **Is the site actually being demoted, or just slow to be discovered?** A new domain with no backlinks naturally sits at page 2-5 for everything until authority builds. If you've never had a backlink campaign or PR push, position 28-50 may just mean "12-month-old domain with no authority signals."
2. **Has Google actually crawled the new content recently?** The audit was done 2026-04-26 against an older state of the site. The OBBBA / 25C corrective sweep landed on the same day. Google may not have re-crawled since.
3. **Are the GSC numbers for the WHOLE site or just city pages?** The 0-clicks pattern is concentrated on city pages targeting `[service] in [city]` queries. Articles, the homepage, costs.html may have different (better) numbers — important for diagnosis.

If after the 21-day window the GSC data is mixed (city pages flat but articles improving), the diagnosis isn't "Google demoting the site" — it's "city pages have a content/intent problem; articles are fine." That's a smaller fix than a sitewide framing pivot.

---

## Summary checklist (when 2026-05-17 arrives)

- [ ] Re-read this document
- [ ] Pull GSC data for cohort cities and compute the 4 metrics in Step 2
- [ ] Pull GSC data for the 105 control-group cities for comparison
- [ ] Pull GSC data for emergency.html, costs.html, the cost-guide article (separate experiments)
- [ ] Decide: Track A (rollout), Track B (framing pivot), or mixed (selective rollout)
- [ ] If unclear: extend the window 7–14 days for more data
- [ ] Whatever the H3 outcome: ship at least one new article during the wait period (H4 or M8)
