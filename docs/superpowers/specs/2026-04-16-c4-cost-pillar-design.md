# C4 Cost Pillar — Design Spec

**Article slug:** `2026-hvac-cost-guide`
**File:** `articles/2026-hvac-cost-guide.html`
**Cluster:** C4_cost (Repair & Replacement Costs)
**Type:** Pillar (equity hub, N=5 cities)
**Bucket:** 2 (Wallet) — CTA copy matches
**Target publish date:** 2026-04-16

## Goal

Build the authority hub for C4_cost by owning **interpretive** cost intent — "is my quote fair", "hidden HVAC fees", "HVAC scams", "why do quotes vary" — deliberately **differentiated from `/costs`** (which owns raw cost-table intent). Zero cannibalization.

## Non-goals

- Duplicating cost tables from `costs.html` (rule 14a in `hvac-article-writer.md`)
- Duplicating financing content from live `article-hvac-financing.html`
- Regional or equipment-type breakdowns as standalone sections (costs.html owns this)

## Primary & secondary keywords

- **Primary:** "HVAC cost guide 2026"
- **Secondary:** "is my HVAC quote fair", "hidden HVAC fees", "HVAC scams", "why do HVAC quotes vary", "HVAC rebates 2026"

## H1, title, meta

- **H1:** `The Honest 2026 HVAC Cost Guide: Every Repair, Every Replacement, Every Hidden Fee` (84 chars — H1 has no length limit)
- **`<title>`:** `The Honest 2026 HVAC Cost Guide | Cool Call Pro` (47 chars ✓)
- **Meta description:** `Know what you're actually paying. Line-by-line quote breakdown, red-flag scams, every hidden fee, and 2026 rebates. The honest HVAC cost guide.` (~150 chars, keyword-led, ends with implicit CTA)

## Section outline (6 H2s, ~4,000 words)

1. **How to read an HVAC quote line-by-line** — diagnostic fee, parts cost vs. markup, labor rate, trip/truck fee, permits, tax. What each line means + what's negotiable.
2. **Red-flag pricing patterns & common scams** — unnecessary coil replacement, leak sealant upsells, phantom refrigerant top-offs without leak search, "your compressor is shot" without pressure test, bait-and-switch service calls.
3. **Why two techs quote 3× different prices for the same job** — overhead/insurance, brand markup (Carrier vs. Goodman), referral/lead fees, season, regional labor rates. Folds regional variance + seasonal timing as subsections.
4. **Every hidden fee homeowners miss** — after-hours surcharge, warranty exclusion clauses, disposal, crane/rooftop access, refrigerant reclaim, permit, thermostat relocation, duct modification.
5. **Repair vs. replace: the cost math** — $5,000 rule, age-cost index, tax-credit arbitrage. Short — mostly anchor text pointing to C5 pillar + live `article-repair-vs-replace`.
6. **2026 rebates & tax credits** — IRA §25C ($2K heat pump / $600 AC), HEEHRA income-qualified, utility rebates (link to DSIRE). Year-stamped, high link value.

**Dropped/compressed:**
- Equipment-type cost tables → 1 callout linking to `/costs`
- Financing math → 2 sentences + link to `article-hvac-financing.html`
- Regional + seasonal → subsections inside §3, not standalone

## FAQ (18 questions, collapsible `.faq-item`, schema-matched)

Topics: fair diagnostic fee, markup norms, leak sealant safe?, refrigerant top-off without leak search?, weekend surcharge range, permit requirement, brand premium worth it?, capacitor cost truth, IRA credit how-to-claim, HEEHRA income limits, why quotes differ, should I get 3 quotes, cash vs. financing true cost, tax credit vs. rebate stacking, "free estimate" catch, disposal fee norms, when cheap quote = bad sign, duct modification cost.

## Internal linking plan

| Destination | Type | Anchor context |
|---|---|---|
| `articles/complete-ac-troubleshooting-guide.html` | Pillar ring | §5 repair-vs-replace intro |
| `article-repair-vs-replace.html` | C5 cross-cluster (live cluster-mate of C5) | §5 math |
| `article-hvac-financing.html` | C4 cluster-mate (live) | §6 rebates transition |
| `costs.html` (`/costs`) | Equipment-type tables | §3 callout |
| 5 cities from linker | Example anchors | §3 regional subsection |
| 2 state hubs from linker | Footer block | Service areas footer |

**Linker command (must run before writing):**
```
python article_city_linker.py 2026-hvac-cost-guide C4_cost 5
```

## External authorities (3)

- DOE Energy Saver — HVAC section
- ENERGY STAR federal tax credits page
- IRS §25C guidance (irs.gov) or DSIRE for rebates

## CTAs (Bucket 2 — Wallet)

- **CTA 1** (after §1): `Want an Exact Quote?` / *Get connected with a technician in your ZIP code.*
- **CTA 2** (end): `Ready to Get a Price?` / *Talk to a technician about your specific system and options.*

## Hero image prompt

Editorial photograph: a homeowner's hands holding a multi-page HVAC quote on paper at a kitchen table, afternoon natural light from a window, a pen resting on the quote. Blurred in the background: an open laptop (screen angled away, no visible content) and a coffee mug. Anchor the frame on the quote paper — line items visible but not legible (to avoid text rendering artifacts). Style: editorial photography, shallow depth of field, warm natural lighting. 16:9 (1280×720). **Filename:** `hvac_cost_guide_pillar.webp`

*Why no thermostat/phone/screen:* image models botch text displays (skill rule 5a).

## Rule softening — CLAUDE.md + skill file

**Change:** "H1 must be question-framed" is too strong.
- **CLAUDE.md:** rewrite the Article Writing bullet 1 to: *"H1 framing should match search intent. Use question form for symptom/diagnostic/decision articles. Use declarative for head-term pillars, cost guides, comparisons, and best-of lists. Primary keyword leads the H1 regardless of form."*
- **`.agents/SKILLS/hvac-article-writer.md` Instruction 1, SEO Structure §1:** same edit.
- **`audit_article.py`:** check for any H1-must-be-question assertion; relax if present.
- **Don't NOT use question form:** question form is still right for most C1/C2/C3 symptom articles.

## Done criteria

- `articles/2026-hvac-cost-guide.html` exists, renders on `localhost:8080`
- All FAQ items expand/collapse (verify visually)
- `python audit_article.py articles/2026-hvac-cost-guide.html` passes
- No cost figures drift from `costs.html`
- `cluster_map.json` status flipped `pending` → `live`
- `python generate_link_plan.py` regenerated
- `articles.html`, `author-gyanesh.html`, `sitemap.xml` updated
- CLAUDE.md + skill file rule softened
- Single git commit + push
