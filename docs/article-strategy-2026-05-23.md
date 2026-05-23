# Article Strategy — 2026-05-23

Versioned planning artifact. Lives in the repo so it survives any machine change.
This document is the detailed companion to the "Topical Authority Without
Doorway Risk" NON-NEGOTIABLE section in [CLAUDE.md](../CLAUDE.md).

## Decision

On 2026-05-23 we explicitly decided to publish articles for **unique editorial
value**, not for **GSC impression-share capture**. The previous priority queue
(set 2026-05-14 based on GSC evidence) over-indexed on equipment-type-swap
articles inside the same intent cluster — exactly the doorway pattern Google
penalizes. Two articles from that queue were paused 2026-05-14 and are now
permanently SKIPPED (not reframed):

- `emergency-ac-repair-cost-guide` — restated `emergency-hvac-service-cost`
- `emergency-furnace-repair-guide` — restated `emergency-hvac-service-cost`

These slugs are dead. Don't resurrect them. The SERPs they'd target are
already captured by article #1 (`emergency-hvac-service-cost`).

## The 3-question uniqueness test (MANDATORY per CLAUDE.md)

Before drafting any cluster article, write three sentences:

1. What does the homeowner LEARN here that they wouldn't learn from any of
   the live articles in this cluster?
2. What is the ONE narrative anchor that drives this piece?
3. Would Google's quality classifier perceive this as a duplicate of
   [closest existing article]? (SERP overlap check)

If you can't write all three confidently, don't write the article.

## Current cluster imbalance

| Cluster | Live | Pending | Target | Status |
|---|---:|---:|---:|---|
| C1_ac | 12 | 1 | 13 | **OVER-WEIGHTED** — stop adding |
| C2_furnace | 4 | 5 | 9 | balanced; selective additions only |
| C3_heatpump | 1 | 3 | 4 | **STARVED — priority expansion** |
| C4_cost | 3 | 7 | 10 | **DEFER niche cost articles** until mix is healthy |
| C5_compare | 4 | 0 | 4 | **STARVED — priority expansion** |
| C6_maint | 3 | 1 | 4 | **STARVED — priority expansion** |

C1 is 26% of the target (over-weight). C3/C5/C6 are only 4% each (starved).
Google reads cluster depth as topic-coverage signal — fix the imbalance before
chasing more C1 or C4 wins.

## Article type taxonomy

Doorway risk concentrates in Types A (symptoms) and C (cost-niche) when
published in volume. Types B/D/E/F/G are inherently more distinct because
they're driven by framework / data / perspective.

| Type | Description | Doorway risk | Current site count |
|---|---|---|---|
| A — Symptom-Diagnostic | "Why is my X doing Y" | Medium | 12 (C1) |
| B — Decision-Framework | "Should I X or Y" | Low | 4 (C5) |
| C — Cost-Reality | "What does X cost" | **HIGH** | 3 (C4) + 7 pending |
| D — Safety + Emergency | Specific hazard | Low | 2-3 |
| E — Seasonal + Behavioral | Calendar / habit | Low | 2 |
| F — Explainer / Educational | "Why X works the way it does" | **Very low** | **0** |
| G — Editorial / Original Data | Methodology / market report | **Very low** | **0** |

**Target mix going forward:** ~40% Type A+C combined, ~60% Types B+D+E+F+G.

## Phase 1 — Next 8 articles (drafted 2026-05-23)

These are candidates, not commitments. Each one must pass the 3-question test
in conversation with the user before being added to `cluster_map.json` and
drafted. The order is suggested but flexible.

### 1. C3_heatpump · Type F (explainer)
**Suggested H1:** "Why heat pumps work in cold weather (the physics)"
- **Learn:** the actual thermodynamics of heat pumps at sub-freezing temps —
  why coefficient of performance drops, what cold-climate heat pumps
  (CCHP) do differently, when auxiliary heat kicks in.
- **Anchor:** "even at 5°F outdoor, your heat pump is moving heat, not making it."
- **SERP check:** primary competitors are manufacturer pages (Mitsubishi,
  Bosch) and Department of Energy. Our angle: aggregator-honest, no brand bias.
**Why first:** C3 is starved (1 article). Explainer = doorway-safe. Builds
trust for the eventual heat-pump-replacement-conversion decision content.

### 2. C6_maint · Type G (editorial / methodology)
**Suggested H1:** "Our 2026 maintenance methodology: what we recommend and why"
- **Learn:** WHY each item in `article-maintenance.html` is recommended,
  what the alternative-skip costs in failure-mode probabilities, where our
  list differs from manufacturer recs and ACCA guidance and why.
- **Anchor:** "we publish our reasoning, not just our checklist."
- **SERP check:** very low — no competitor publishes their methodology.
**Why second:** editorial voice = brand differentiation. Cites the existing
checklist; doesn't replace it.

### 3. C3_heatpump · Type B (decision)
**Suggested H1:** "When to switch from gas furnace to heat pump (decision tree)"
- **Learn:** the specific cost-payback math, climate-zone applicability,
  HEAR rebate eligibility, and "you should NOT switch" scenarios.
- **Anchor:** "a decision tree, not a sales pitch."
- **SERP check:** complements `heat-pump-vs-gas-furnace.html`; that one
  compares operating cost, this one is the conversion decision frame.
**Why third:** decision-frame = doorway-safe. Builds C3 to 3+ articles.

### 4. C2_furnace · Type D (safety)
**Suggested H1:** "Gas leak vs. CO leak: telling them apart in 60 seconds"
- **Learn:** the 4 distinguishing signals (smell, symptoms, detector type,
  what to do in next 60 seconds), what to do BEFORE calling anyone.
- **Anchor:** "two different emergencies, two different first-60-second responses."
- **SERP check:** `article-carbon-monoxide.html` covers CO only;
  `article-furnace.html` doesn't cover the distinguishing question. No overlap.
**Why fourth:** Type D safety = high-value low-risk. Specific hazard,
distinct from existing CO article.

### 5. C6_maint · Type F (explainer)
**Suggested H1:** "What an HVAC technician actually does on a service call"
- **Learn:** the 12-15 specific physical actions a competent technician
  performs (visual inspection, electrical test sequence, refrigerant pressure
  check, etc.), how long each takes, what the diagnostic fee actually covers.
- **Anchor:** "you should understand what you're paying for."
- **SERP check:** addresses the implicit "am I being ripped off" question;
  no competitor publishes this transparently.
**Why fifth:** F-type explainer. Reinforces aggregator brand voice.

### 6. C5_compare · Type B (decision)
**Suggested H1:** "How to evaluate an HVAC quote (red-flag checklist)"
- **Learn:** the 8 line items that should appear on any legitimate quote,
  the 4 phrases that signal an upsell, the price-range sanity check against
  costs.html, when "free second opinion" is worth getting.
- **Anchor:** "you have leverage if you know what to look for."
- **SERP check:** C5 currently has repair-vs-replace + comparison content;
  this is the QUOTE-evaluation decision frame. Distinct.
**Why sixth:** C5 expansion + decision-frame + price-shopper persona (M9
backlog).

### 7. C3_heatpump · Type A (symptom, but uniquely framed)
**Suggested H1:** "Heat pump making ice in winter: defrost cycle vs. real problem"
- **Learn:** the difference between normal defrost cycle behavior and
  malfunction, the 30-second visual test, when ice indicates frozen coil
  vs. defrost-cycle-stuck.
- **Anchor:** "defrost cycles look alarming but aren't always broken."
- **SERP check:** would Google see this as duplicate of the C3 pillar's
  troubleshooting section? Possibly — must SERP-check before drafting.
**Why seventh:** ONE Type A allowed in this batch to round out C3. Skip if
SERP-check fails.

### 8. C4_cost · Type G (data / market report)
**Suggested H1:** "2026 HVAC cost trends: what's changed since OBBBA"
- **Learn:** the specific tax-credit timeline (25C terminated), HEAR program
  status by state, R-410A → R-454B refrigerant transition cost impact, labor
  market data.
- **Anchor:** "the regulatory environment shifted in 2026 — here's what it
  means for your wallet."
- **SERP check:** complements `2026-hvac-cost-guide.html` pillar; that one
  is the cost reference, this is the narrative + context.
**Why eighth:** Type G original-data piece. Differentiates from C4 cost-niche
pattern.

## What's DEFERRED indefinitely

The following pending slugs in `cluster_map.json` are deprioritized until
cluster mix is healthier AND each has passed the 3-question test against
the by-then-current article corpus:

- `emergency-ac-repair-cost-guide` — **SKIPPED PERMANENTLY**
- `emergency-furnace-repair-guide` — **SKIPPED PERMANENTLY**
- `emergency-weekend-hvac-cost` — overlaps with `24-hour-hvac-repair`; defer
- `cost-replace-3-ton-ac` — covered in cost-guide pillar; defer unless data
  shows winnable 3-ton-specific queries
- `r410a-recharge-cost` — covered in cost-guide; defer
- `new-furnace-installed-cost` — covered in cost-guide; defer
- `dual-run-capacitor-cost` — covered in cost-guide; defer (very narrow)
- `mini-split-installation-cost` — defer
- `central-air-no-ductwork-cost` — defer
- `furnace-short-cycling` — Type A; defer until C2 has more variety
- `furnace-burning-plastic-smell` — defer
- `co-detector-furnace-running` — defer
- `furnace-ignitor-wont-light` — defer
- `heat-pump-stuck-in-cooling` — Type A; Phase 1 may cover this
- `heat-pump-lukewarm-air` — defer
- `heat-pump-defrost-grinding` — defer
- `best-merv-rating` — Phase 1+ candidate (Type B), evaluate after batch 1

## Phase 2 + Phase 3

After Phase 1 ships, **re-pull GSC** (filter to 2026-05-22 → ship+21 days)
and re-evaluate priorities. Don't pre-commit to Phase 2 slugs from this
document — the data will tell us what to write next.

Cadence target: **1 quality article per week** (~6-10 hours per pillar /
~3-5 hours per cluster article). 67 articles remaining at that pace = ~15
months to 100. Acceptable trajectory.

## Operating principle

**The roadmap is a MENU, not a QUEUE.** This document is a menu of candidates.
The user picks from it (or proposes alternatives that pass the 3-question test)
each week. Don't grind through positions 1→8 in order if the data shifts
under us.
