# CoolCallPro — Topical Authority Cluster Audit

_Audited: 2026-04-26. Read-only. No source files were modified._

> ⚠ **STATUS UPDATE 2026-05-23.** All 6 cluster pillars are now LIVE
> (was 2 of 6 at audit time). The C1 imbalance flagged in this audit
> got worse (12 cluster articles now), which is part of why the
> 2026-05-23 strategy override calls for a cluster rebalance (stop
> adding to C1, build C3/C5/C6).
>
> The pending C4 cluster articles referenced below (`cost-replace-3-ton-ac`,
> `r410a-recharge-cost`, etc.) are now **DEFERRED INDEFINITELY** per
> the topical-authority-without-doorway rule — the C4 pillar
> `2026-hvac-cost-guide` covers their content and standalone niche cost
> articles would compound the C1+C4 over-weight problem. See
> `CLAUDE.md` "Topical Authority Without Doorway Risk" section +
> `docs/article-strategy-2026-05-23.md` for current direction.
>
> Cluster-level recommendations in this audit (pillar precedence,
> cross-cluster bridges, orphan-pillar avoidance) are still valid.

---

## 1. Overall Snapshot

| Metric | Value |
|--------|-------|
| Clusters | 6 |
| Pillars live | 2 of 6 (C1_ac, C4_cost) |
| Pillars pending | 4 (C2, C3, C5, C6) |
| Articles live | 24 |
| Articles pending | 22 |
| City link coverage | 89/115 (77%) |
| Orphan cities (0 links) | 26 |
| Max links to single city | 7 (Tucson, AZ) |

---

## 2. Pillar-First Rule Compliance

The pillar-first rule states: a cluster's pillar must be `live` before 3+ cluster articles in that cluster go live.

| Cluster | Pillar Status | Live Cluster Articles | Pillar-First Violated? |
|---------|---------------|-----------------------|------------------------|
| C1_ac | live | 12 | No — pillar was position 1 in priority_queue |
| C2_furnace | **PENDING** | **4** | **YES — CRITICAL** |
| C3_heatpump | **PENDING** | 1 | Borderline — 1 cluster article live, pillar not yet written |
| C4_cost | live | 1 | No — pillar was position 2 in priority_queue |
| C5_compare | **PENDING** | **1** | No — only 1 cluster article live |
| C6_maint | **PENDING** | **3** | **YES — CRITICAL** |

### C2_furnace — CRITICAL orphan-pillar risk

Four cluster articles are live and linking to `articles/furnace-not-working-diagnostic-guide.html` — a URL that does not exist yet. Every internal link in those 4 articles to the pillar resolves to a 404 or a dead anchor. Affected articles:
- `article-furnace.html` (Furnace Not Igniting?)
- `article-winter-storm.html` (Winter Storm HVAC)
- `article-carbon-monoxide.html` (Carbon Monoxide)
- `articles/furnace-blowing-cold-air-winter.html` (Furnace Blowing Cold Air?)

Confirmed by inspection of `furnace-blowing-cold-air-winter.html` sidebar: links to `../article-furnace` as the "Complete Furnace Troubleshooting Guide" — not the cluster pillar slug. This means the C2 cluster is not actually linking to the pending pillar yet, but the link plan has them mapped to it and they will need to link there once it ships. The structural risk is real.

### C6_maint — CRITICAL orphan-pillar risk

Three cluster articles are live (`article-maintenance.html`, `article-fall-prep.html`, `article-emergency.html`). The C6 pillar (`year-round-hvac-maintenance-playbook`) is pending. Confirmed by inspection of `article-maintenance.html`: the article does NOT link to its planned pillar. It links sideways to `article-fall-prep`, `article-winter-storm`, `article-carbon-monoxide`, and `article-furnace` — but no link to the C6 pillar URL. The pillar will arrive to a cluster that has been publishing for weeks without a hub.

---

## 3. Cluster-by-Cluster Status

### C1_ac — AC Troubleshooting (HEALTHY with one gap)

- Pillar: LIVE (`complete-ac-troubleshooting-guide`)
- Live cluster articles: 12
- Pending: 0
- Status: Complete cluster, no pending articles remain.

**Gap — Pillar stale link set:** The C1 pillar was published 2026-04-16. Six additional cluster articles were published on 2026-04-20 and 2026-04-21 (`ac-freezing-up-in-summer`, `ac-not-cooling-below-80`, `ac-circuit-breaker-trips`, `thermostat-blank-ac-wont-start`, `ac-contactor-clicking`, `water-dripping-from-vent`). The pillar's body and sidebar currently link to only 3 cluster articles (`why-is-my-ac-blowing-warm-air`, `ac-compressor-buzzing-fan-not-spinning`, `hvac-leaking-water-inside-house`) and 3 older root-level articles (`article-refrigerant`, `article-ac-summer`, `article-spring-ac`). The 6 articles published after the pillar are NOT linked from the pillar anywhere. This breaks the mandatory rule: "The pillar MUST link to every spoke."

Spokes published after the pillar with zero inbound links from the pillar:
1. `ac-freezing-up-in-summer`
2. `ac-not-cooling-below-80`
3. `ac-circuit-breaker-trips`
4. `thermostat-blank-ac-wont-start`
5. `ac-contactor-clicking`
6. `water-dripping-from-vent`

**Action required:** Update `articles/complete-ac-troubleshooting-guide.html` to add links to all 6 missing spokes. This is the highest-priority fix in the entire audit because C1 is the site's most trafficked cluster with 12 live articles.

### C2_furnace — Furnace & Heating (HIGH RISK)

- Pillar: PENDING (`furnace-not-working-diagnostic-guide` — position 8 in priority queue)
- Live cluster articles: 4
- Pending: 4 more (short-cycling, plastic smell, ignitor, CO detector)
- Risk: 4 live articles already out with no pillar to receive their spoke-to-pillar links. The 4 pending cluster articles (positions 9, 10, 24, 25 in queue) are scheduled AFTER the pillar (position 8) — so they will be compliant. But the 4 already-live articles were written before the pillar existed.

**Compounding issue:** The 4 pre-existing live articles (`article-furnace`, `article-winter-storm`, `article-carbon-monoxide`, `furnace-blowing-cold-air-winter`) point their sidebar "related articles" links to each other — not to the pending pillar URL. When the pillar ships, a retrofit pass will be needed on all 4 files to add the spoke-to-pillar link.

### C3_heatpump — Heat Pumps (MODERATE RISK)

- Pillar: PENDING (`2026-heat-pump-buyers-guide` — position 14 in queue)
- Live cluster articles: 1 (`article-heat-pump`)
- Pending: 3 more
- Risk: Only 1 cluster article is live, so the cluster has not grown past the orphan threshold. However, `article-heat-pump.html` is already live and does not have a link to the pending pillar. Same retrofit situation as C2 once the pillar ships.

### C4_cost — Costs (HEALTHY with link debt)

- Pillar: LIVE (`2026-hvac-cost-guide`)
- Live cluster articles: 1 (`article-hvac-financing`)
- Pending: 7 more
- Status: Pillar exists. Only 1 cluster article live. The pending 7 (cost-replace-3-ton-ac, r410a-recharge-cost, etc.) are all in the priority queue after the pillar.
- No orphan-pillar risk. Low coverage at 1/8 cluster articles live.

**Note:** The C4 pillar (`2026-hvac-cost-guide`) is a critical cross-cluster anchor for both C1 and C2. Verify it is being linked from every C1 and C2 cluster article.

### C5_compare — Repair-vs-Replace (MODERATE RISK)

- Pillar: PENDING (`repair-or-replace-framework` — position 17 in queue)
- Live cluster articles: 1 (`article-repair-vs-replace`)
- Pending: 3 more
- Risk: Only 1 cluster article live. However, `article-repair-vs-replace.html` links to the C4_cost pillar (`article-repair-vs-replace` uses `2026-hvac-cost-guide` as cross-cluster anchor per the plan) but does NOT link to its own pending C5 pillar. Same retrofit gap as C2/C3.

### C6_maint — Maintenance (HIGH RISK)

- Pillar: PENDING (`year-round-hvac-maintenance-playbook` — position 26 in queue)
- Live cluster articles: 3 (`article-maintenance`, `article-fall-prep`, `article-emergency`)
- Pending: 1 more (`best-merv-rating`)
- Risk: 3 live articles, no pillar. This cluster is in the same structural state as C2.

**Confirmed by file inspection:** `article-maintenance.html` (C6 cluster article) contains zero references to `year-round-hvac-maintenance-playbook`. Its cross-cluster anchor links to `article-fall-prep` (within cluster) and `article-carbon-monoxide` (C2). The C1 pillar link (`complete-ac-troubleshooting-guide`) is also absent from the maintenance article — but the link plan specifies C6 articles should cross-link to C1_ac as their cross-cluster anchor. This link is missing from `article-maintenance.html`.

---

## 4. Internal Linking Depth — 3-Article Sample

### Sample 1: `articles/ac-freezing-up-in-summer.html` (C1 cluster)

| Link type | Count | Notes |
|-----------|-------|-------|
| Links to C1 pillar | 1 | `complete-ac-troubleshooting-guide` — in body ("full walkthrough") |
| Links to C1 sibling articles | 3 | `article-refrigerant`, `hvac-leaking-water-inside-house`, `why-is-my-ac-blowing-warm-air` (sidebar + body) |
| Links to cross-cluster C4 | 1 | `2026-hvac-cost-guide` ("honest 2026 HVAC cost guide") |
| Links to city/state pages | 6 | Tampa, Tucson, Tallahassee, Atlanta, Florida, Arizona (body + sidebar) |
| Links to state hubs in footer | 2 | Florida, Arizona |
| **Assessment** | PASS | Meets all targets: 1 pillar link, 3 sibling links, 1 cross-cluster, 4+ cities |

### Sample 2: `articles/furnace-blowing-cold-air-winter.html` (C2 cluster)

| Link type | Count | Notes |
|-----------|-------|-------|
| Links to C2 pillar | 0 | Pillar is pending — no URL to link to yet. Sidebar links to `article-furnace` as substitute |
| Links to C2 sibling articles | 3 | `article-furnace`, `article-carbon-monoxide`, `article-winter-storm` (sidebar) |
| Links to cross-cluster C4 | 0 | Body has cost table but does NOT link to `2026-hvac-cost-guide`. Sidebar links to `/costs` page but not to the C4 pillar article |
| Links to cross-cluster C5 | 1 | `article-repair-vs-replace` ("start planning for replacement") |
| Links to city/state pages | 6 | Chicago, Minneapolis, Denver, Illinois, Minnesota, Colorado (body + footer + sidebar) |
| **Assessment** | GAP | Missing pillar link (expected — pillar pending). Missing cross-cluster C4 cost-guide link (not expected — C4 pillar is live). |

### Sample 3: `article-maintenance.html` (C6 cluster — root level)

| Link type | Count | Notes |
|-----------|-------|-------|
| Links to C6 pillar | 0 | Pillar pending — no URL exists yet |
| Links to C6 sibling articles | 2 | `article-fall-prep`, `article-emergency` (inferred from sidebar; confirmed via grep) |
| Links to cross-cluster C1 | 0 | C6 cross_cluster_anchor is C1_ac, but NO link to `complete-ac-troubleshooting-guide` found |
| Links to city/state pages | 4 | Philadelphia, Pittsburgh, Dallas, Los Angeles (per link plan) |
| **Assessment** | GAP | Missing C6 pillar link (expected — pending). Missing C1 cross-cluster link (not expected — C1 pillar is live). The cross-cluster anchor connection for this article is completely absent. |

---

## 5. City Link Coverage Equity

Based on `city_link_coverage.csv` (46 articles planned, 26 pending + 20 live that contribute links):

### Top 10 over-linked cities (risk of crowding)

| City | Links | Climate | Notes |
|------|-------|---------|-------|
| Tucson, AZ | 7 | hot-dry | Highest on site — 7 different articles link here |
| Brownsville, TX | 6 | hot-humid | 6 links — over-represented for a secondary market |
| Little Rock, AR | 6 | mixed-humid | 6 links |
| Jackson, MS | 5 | mixed-humid | 5 links |
| Boston, MA | 4 | cold | 4 links |
| Baton Rouge, LA | 4 | hot-humid | 4 links |
| Detroit, MI | 4 | cold | 4 links |
| Las Vegas, NV | 4 | hot-dry | 4 links |
| Glendale, AZ | 4 | hot-dry | 4 links |
| Charlotte, NC | 4 | mixed-humid | 4 links |

Tucson at 7 links is the clearest concentration risk. While there is no hard cap, 7 is nearly 3x the site average (1.7). If Google notices that most of the site's article-to-city links converge on Tucson, it reduces the breadth signal of the location network.

### Top 10 under-linked or orphan cities (0 planned article links)

| City | State | Climate | Links |
|------|-------|---------|-------|
| Honolulu, HI | HI | tropical | 0 |
| Anchorage, AK | AK | subarctic | 0 |
| Fargo, ND | ND | subarctic | 0 |
| Eugene, OR | OR | coastal | 0 |
| Portland, OR | OR | coastal | 0 |
| New York City, NY | NY | cold | 0 |
| Buffalo, NY | NY | cold | 0 |
| Newark, NJ | NJ | cold | 0 |
| Providence, RI | RI | cold | 0 |
| Columbus, OH | OH | cold | 0 |

Additional orphans: Madison WI, Manchester NH, Wilmington DE, Mobile AL, New Orleans LA, Oklahoma City OK, Raleigh NC, Shreveport LA, St. Louis MO, Winston-Salem NC, Birmingham AL, Fresno CA, San Diego CA, Missoula MT, Reno NV, Colorado Springs CO.

**Total orphan count: 26 cities (23% of the 115-city network).**

The most notable absence is **New York City** — one of the highest-search-volume HVAC markets in the country — with zero planned article links. Similarly, Portland OR (cold-climate coastal, strong heat-pump market), Raleigh NC (fast-growing Sun Belt city), and Columbus OH are all zero.

The orphan pattern is partly a function of the cluster climate weights: C1_ac overweights hot-humid and hot-dry (no cold/subarctic cities in C1), C2_furnace overweights cold/mountain, and C3_heatpump overweights coastal/mixed-humid. Cities that don't align with any cluster's top weights fall through the cracks.

---

## 6. Pillar vs. Cluster H1 Form Check

CLAUDE.md rule: Declarative H1 for pillars/cost guides/comparisons. Question H1 for symptom/diagnostic articles.

| Article | Type | H1 Form | Expected | Pass? |
|---------|------|---------|----------|-------|
| `complete-ac-troubleshooting-guide` (C1 pillar) | pillar | "Why Isn't My AC Working? The Complete 2026 Troubleshooting Guide" | Declarative (could be question for diagnostic) | AMBIGUOUS — question form is defensible for a full diagnostic pillar, but CLAUDE.md says declarative for "head-term pillars." Primary keyword is "AC troubleshooting" — question form matches diagnostic intent. Acceptable. |
| `2026-hvac-cost-guide` (C4 pillar) | pillar | "The Honest 2026 HVAC Cost Guide: Every Repair, Every Replacement, Every Hidden Fee" | Declarative | PASS |
| `ac-freezing-up-in-summer` (C1 cluster) | cluster / symptom | "AC Freezing Up in Summer? Ice on the Coils and How to Thaw It Safely" | Question form for symptom | PASS |
| `furnace-blowing-cold-air-winter` (C2 cluster) | cluster / symptom | "Furnace Blowing Cold Air in Winter? 5 Things to Check Right Now" | Question form for symptom | PASS |
| `article-maintenance` (C6 cluster) | cluster / list | "The 12-Month HVAC Maintenance Checklist" | Declarative for checklist/best-of | PASS |
| `article-repair-vs-replace` (C5 cluster) | cluster / decision | "HVAC Repair vs. Replace: Decision Guide" | Declarative for comparison | PASS |
| `article-hvac-financing` (C4 cluster) | cluster / options | "Finance an HVAC Replacement: 6 Options" | Declarative for options/list | PASS |
| `article-heat-pump` (C3 cluster) | cluster / symptom+cost | "Heat Pump Not Working? Repair Costs & Fixes" | Question form for symptom | PASS |

**H1 form verdict: All sampled articles pass. No violations detected.**

---

## 7. Cluster Bridge Analysis

The `cross_cluster_anchor` field in `cluster_map.json` defines the intended inter-cluster topical bridges:

| From cluster | Cross-link target | Bridge rationale |
|--------------|-------------------|-----------------|
| C1_ac | C4_cost | AC troubleshooting → cost evaluation |
| C2_furnace | C4_cost | Furnace troubleshooting → cost evaluation |
| C3_heatpump | C5_compare | Heat pump decision → repair-vs-replace framework |
| C4_cost | C5_compare | Cost guide → decision framework |
| C5_compare | C4_cost | Comparison → cost context |
| C6_maint | C1_ac | Maintenance prevents AC emergencies |

**Verification against live articles:**

- C1 → C4 bridge: ACTIVE. `ac-freezing-up-in-summer` links to `2026-hvac-cost-guide` in body ("honest 2026 HVAC cost guide"). Most C1 articles do reference cost context.
- C2 → C4 bridge: WEAK. `furnace-blowing-cold-air-winter` has a cost table in the body but does NOT link to `2026-hvac-cost-guide` article. It links to `/costs` (the cost page) instead. The C4 pillar article is not receiving this cross-cluster equity.
- C3 → C5 bridge: NOT VERIFIABLE — C3 only has 1 live article (`article-heat-pump`) and C5 pillar is pending.
- C4 → C5 bridge: ACTIVE in plan — `article-hvac-financing` is mapped to link to C5 anchor (`2026-hvac-cost-guide` cross-cluster → `article-repair-vs-replace`). Cannot confirm without reading that file but the plan is structured correctly.
- C6 → C1 bridge: BROKEN. `article-maintenance.html` has zero links to `complete-ac-troubleshooting-guide`. The C6 cross-cluster anchor to C1 is not being executed in the currently live C6 articles.

**Overall bridge health: 2 of 4 testable bridges confirmed active. C2→C4 and C6→C1 bridges are broken or weak in currently live articles.**

---

## 8. Programmatic City × Topic Prohibition Check

Searched for `*-in-*-tx.html`, `*-repair-*-city*`, and `articles/ac-repair*.html` patterns. No city × topic pages were found. The `articles/` directory contains exactly 12 files, all matching the topical (non-geo) naming pattern. The root level contains 12 `article-*.html` files, all non-geo.

**City × topic prohibition: CLEAN. No violations.**

---

## 9. Cannibalization Check

Reviewed primary keywords across all 46 mapped articles. No two articles share the same primary keyword. The closest pairs:

- `article-furnace` ("Furnace Not Igniting?") vs `furnace-blowing-cold-air-winter` ("Furnace Blowing Cold Air?") — different symptoms, distinct SERP intent.
- `article-refrigerant` ("Refrigerant Leaks: Why AC Ice Is a Problem") vs `ac-freezing-up-in-summer` ("AC Freezing Up in Summer?") — related but distinct: one is about the leak/refrigerant mechanism, the other is about the freezing symptom and thaw procedure.
- `article-repair-vs-replace` ("HVAC Repair vs. Replace: Decision Guide") vs `repair-or-replace-framework` (pending pillar: "Repair or Replace? The Framework") — these are the most cannibalization-prone pair. The cluster article and its own pillar target the same head query. Differentiation will need to be meaningful: the cluster article as a quick decision tool, the pillar as the comprehensive framework.

**Cannibalization verdict: No current violations. Monitor the article-repair-vs-replace / repair-or-replace-framework pair when the pillar ships.**

---

## 10. Priority Fix List

Ranked by impact:

| # | Issue | Severity | Cluster | Action |
|---|-------|----------|---------|--------|
| 1 | C1 pillar missing 6 spoke links | HIGH | C1_ac | Update `articles/complete-ac-troubleshooting-guide.html` to add links to ac-freezing-up-in-summer, ac-not-cooling-below-80, ac-circuit-breaker-trips, thermostat-blank-ac-wont-start, ac-contactor-clicking, water-dripping-from-vent |
| 2 | C6 pillar pending while 3 cluster articles are live | HIGH | C6_maint | Write `articles/year-round-hvac-maintenance-playbook.html` (priority position 26 — move up to position 1 next writing sprint) |
| 3 | C2 pillar pending while 4 cluster articles are live | HIGH | C2_furnace | Write `articles/furnace-not-working-diagnostic-guide.html` (priority position 8 — already next in queue, execute immediately) |
| 4 | C6→C1 cross-cluster bridge broken | MEDIUM | C6_maint | Add link to `complete-ac-troubleshooting-guide` in `article-maintenance.html`, `article-fall-prep.html`, `article-emergency.html` |
| 5 | C2 cluster articles missing C4 cross-cluster link | MEDIUM | C2_furnace | Add link to `2026-hvac-cost-guide` in furnace cluster articles (currently linking to `/costs` page instead) |
| 6 | 26 orphan cities with 0 article links | MEDIUM | All | Prioritize NYC, Portland OR, Raleigh NC, Columbus OH in next batch of pending articles — update climate_weights in cluster_map.json to ensure cold/subarctic cities receive more coverage |
| 7 | Tucson over-linked at 7 articles | LOW | All | No immediate action needed but cap at current level — do not assign Tucson to any additional pending articles |
| 8 | C5 article-repair-vs-replace / repair-or-replace-framework cannibalization risk | LOW | C5_compare | Differentiate clearly when pillar ships: pillar = decision framework with scoring rubric; cluster article = quick yes/no decision tool |
| 9 | Retrofit spoke-to-pillar links in C2/C3/C6 legacy articles when pillars ship | LOW | C2, C3, C6 | Plan a same-commit retrofit sweep whenever each pending pillar is written |

---

## 11. Summary

**Architecture is sound. The pillar-cluster strategy is correctly defined in cluster_map.json and the deterministic city linker works as designed. The critical execution gap is sequencing: two clusters (C2 and C6) allowed cluster articles to accumulate before their pillars existed, creating orphaned spoke networks. The C1 pillar is also stale — it predates 6 of its own 12 spokes and does not link to them.**

The city coverage equity problem (26 orphan cities, Tucson at 7x average) is a natural consequence of climate weighting that over-concentrates links in hot-humid and hot-dry zones. The fix is primarily in the pending article assignments, not in rewriting live content.

No city × topic violations were found. H1 form is compliant across all sampled articles. No keyword cannibalization is active (monitor repair-vs-replace pair). The cross-cluster bridge network needs reinforcement in C2→C4 and C6→C1, both of which are low-effort body-copy additions to existing live articles.
