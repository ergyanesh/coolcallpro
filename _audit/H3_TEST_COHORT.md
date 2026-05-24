# H3 City-Page Title Repositioning — Test Cohort Tracker

**Cohort applied:** 2026-04-26
**Decision deadline:** 2026-05-17 (3 weeks; minimum window for Google to re-render SERPs and accumulate enough impression/click data to be statistically meaningful)
**Scope:** 10 of 115 city pages — title attribute only (meta description and H1 untouched, so the experiment isolates title CTR effect)

> ✅ **DECISION COMPLETE 2026-05-22.** Cohort yielded 0 clicks across
> 15,315 cohort impressions over 25 days (with the caveat that hand-
> edited cohort titles were silently overwritten by Phase 2/3 regens
> on 2026-05-09, so only ~13 of 25 days carried the new title).
> Track A (expand title-only) did NOT qualify per the decision rule.
> **Outcome: Track B framing pivot** shipped 2026-05-22 as commits
> `ac57848` + `6684309`. All 115 city pages now carry cost-intent
> climate-aware titles + aggregator-framed H1 + ATF disclosure badge
> + 6-card climate grid + per-city homes-and-energy paragraph +
> 4-card repair-cost summary block.
>
> This document is retained as the experiment record. The rollback
> procedure is moot.

---

## The hypothesis

The current city-page title pattern `24/7 [Service] in [City], [ST] | Cool Call Pro` targets the GBP-locked `[service] in [city]` query class. Per GSC last 28 days (2026-04-26): 6,643 impressions across city pages → **0 clicks**, average position 28–50. The SERP for those queries is dominated by Local Pack listings (GBPs), so Cool Call Pro is structurally excluded from the click-territory positions 1–10.

The new pattern repositions the page toward **problem-driven local queries** (`[city] [service] cost`, `[city] [service] repair`) that are **NOT** GBP-locked because Google does not trigger the local pack for cost/repair queries. Same emergency CTAs stay on-page; same conversion path. The change is purely about which SERP class the page competes in.

**Predicted outcome:** test cohort cities should see higher click counts and lower average position over 2–3 weeks because they're entering a less-competitive SERP class while still attracting high-intent (problem-driven) homeowners.

---

## The 10 test cohort cities

Selected to balance:
- 4 climate types (cold / hot-humid / hot-dry / coastal+mixed)
- High-impression cities (so signal is measurable)
- Variety of dominant local problem (AC vs furnace vs heat-pump-leaning)

| City | Climate | Impressions (last 28d) | Old title | New title (≤60 chars) |
|---|---|---|---|---|
| Houston, TX | hot-humid | 396 | 24/7 AC & HVAC Repair in Houston, TX \| Cool Call Pro | Houston AC Repair Cost & 24/7 Emergency HVAC \| Cool Call Pro |
| New Orleans, LA | hot-humid | 690 | 24/7 AC & HVAC Repair in New Orleans, LA \| Cool Call Pro | New Orleans AC Repair Cost & 24/7 Emergency HVAC |
| Phoenix, AZ | hot-dry | (not in top 10) | 24/7 AC & HVAC Repair in Phoenix, AZ \| Cool Call Pro | Phoenix HVAC Repair Cost & 24/7 AC Service \| Cool Call Pro |
| Las Vegas, NV | hot-dry | (not in top 10) | 24/7 AC & HVAC Repair in Las Vegas, NV \| Cool Call Pro | Las Vegas HVAC Repair Cost & 24/7 AC Service \| Cool Call Pro |
| Chicago, IL | cold | 525 | 24/7 Furnace & HVAC Repair in Chicago, IL \| Cool Call Pro | Chicago Furnace Repair Cost & 24/7 No-Heat Service |
| Minneapolis, MN | cold | 374 | HVAC Repair in Minneapolis, MN \| Cool Call Pro | Minneapolis Furnace Repair Cost & 24/7 No-Heat Service |
| Boston, MA | cold | (not in top 10) | 24/7 Furnace & HVAC Repair in Boston, MA \| Cool Call Pro | Boston Furnace Repair Cost & 24/7 No-Heat Service |
| Atlanta, GA | mixed-humid | (not in top 10) | 24/7 AC & HVAC Repair in Atlanta, GA \| Cool Call Pro | Atlanta HVAC Repair Cost & 24/7 Emergency Service |
| San Diego, CA | coastal | 600 | 24/7 AC & HVAC Repair in San Diego, CA \| Cool Call Pro | San Diego HVAC Repair Cost & 24/7 Emergency Service |
| Portland, OR | coastal | 867 | 24/7 Heat Pump & HVAC in Portland, OR \| Cool Call Pro | Portland Heat Pump Repair Cost & 24/7 HVAC Service |

Cities NOT in the cohort (the **control group** — 105 cities) keep their original titles, so we have a direct comparison.

---

## Why these specific titles (not the audit's "Cost & Climate Guide" suggestion)

The original ACTION-PLAN.md H3 example was:
> "[City] HVAC Cost & Climate Guide ([Year]) \| Cool Call Pro"

This was rejected during the H3 conversation because "Cost & Climate Guide" reads as **educational** content (browsing, no buyer intent) — which would attract readers, not callers. Cool Call Pro's revenue model is referral phone calls from homeowners with broken HVAC, not display advertising on travel-style city guides.

The chosen pattern preserves problem-driven buyer intent while escaping the GBP lock:
- **"[Service] Repair Cost"** — homeowner with broken HVAC who wants to know what the fix costs before calling. High commercial intent. NOT GBP-locked.
- **"24/7 [Variant] Service"** — preserves the emergency framing the existing CTAs are built around.
- **Climate-aware service term**: hot-zone cities lead with AC, cold-zone cities lead with Furnace, mixed/coastal lead with HVAC. Matches the dominant local problem the homeowner is searching about.

---

## What was NOT changed (the experimental control)

- **Meta description** — left as the existing template "Need AC or HVAC repair in [City], [ST]? Cool Call Pro connects you 24/7. Call (844) 582-1795." — so we measure title CTR effect in isolation
- **H1** — left as "24/7 [Service] Repair & Emergency HVAC Service in [City], [ST]" — H1 is a strong page-relevance signal; changing it simultaneously would conflate the experiment
- **All on-page content** — emergency cards, climate profile, local data, FAQs, CTAs all unchanged
- **All other 105 city pages** — control group, untouched

---

## Measurement plan (revisit 2026-05-17 or later)

In Google Search Console:

1. **Performance → Search results** filtered by URL containing each of the 10 cohort city slugs. Compare:
   - Last 28 days (post-cohort) vs prior 28 days (control)
   - Metrics: total clicks, total impressions, average CTR, average position
2. **URL Inspection** on a sample of cohort cities (e.g., Minneapolis-MN) and a sample of control cities (e.g., Detroit-MI for similar climate) — compare indexation and ranking signals
3. **Top queries** filter — for each cohort city, see which queries it now ranks for. Should shift away from `[service] in [city]` toward `[city] [service] cost / repair / emergency`.

### Decision criteria

| Outcome at +21 days | Action |
|---|---|
| Clicks per cohort city up >50% vs prior 28d AND avg position improved by ≥3 places | EXPAND: regenerate all 105 control cities with same title pattern via the city generator |
| Clicks flat / down OR avg position degraded | REVERT: restore the 10 cohort city titles to original + retry with a different pattern |
| Mixed (some climates win, some don't) | Keep winning-climate cohorts, revert losing-climate cohorts, expand the winners to all matching-climate cities |

### Rollback procedure

If revert is needed, every old title is captured in the table above. A 10-line Python script can swap them back. The change is fully reversible.

### Skill / generator update

If we EXPAND, the city generator (`generate_city_pages_v4.py`) needs a title-template change so future regenerations stay consistent. The current generator likely has a single title template — would need to add climate-aware variants matching the cohort patterns.
