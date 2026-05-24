# Content Scaling Strategy — Cool Call Pro

> ⚠ **SUPERSEDED 2026-05-23 for article-priority guidance.** This document
> is the original pre-cluster content plan from March 2026. The article
> roadmap and writing process are now governed by:
>
> 1. **`CLAUDE.md`** sections "Article Writing (Pillar-Cluster Topical
>    Authority System)" + "Topical Authority Without Doorway Risk"
>    (the latter added 2026-05-23 and overrides keyword-driven queues)
> 2. **`docs/article-strategy-2026-05-23.md`** — Phase 1 candidate menu
> 3. **`cluster_map.json`** — machine-readable cluster + article state
> 4. **`.agents/SKILLS/hvac-article-writer.md`** — writing-loop procedure
>
> The site-architecture diagram below is still accurate (locations + articles
> hub-and-spoke), but **DO NOT use the "Article Writing Priority Queue"
> section here as guidance** — it predates the 6-cluster pillar system
> and doorway-risk awareness. Kept for historical context only.

> Single source of truth for article planning, service pages, and internal linking architecture.
> Separate from city page template (see `city-page-programmatic-seo-16-march-2026.md`).
> **MANDATORY:** After creating or updating ANY pages, run QC checklist in `site-qc-checklist.md` before deploying.
> Created: 16 March 2026

---

## 1. Site Architecture

> **UPDATED 19 March 2026:** Architecture now includes state hub pages (hub-and-spoke model). See `hub-and-spoke-master-plan-19-march-2026.md` for the full implementation plan.

```
coolcallpro.com/
├── / (homepage)
├── /services/ac-repair              ← NEW (Priority 1)
├── /services/furnace-repair         ← NEW (Priority 1)
├── /services/hvac-replacement       ← NEW (Priority 1)
├── /services/heat-pump              ← NEW (Priority 2)
├── /services/duct-cleaning          ← NEW (Priority 3)
├── /services/hvac-maintenance       ← NEW (Priority 3)
├── /emergency.html                  ← EXISTS (covers emergency HVAC)
├── /costs.html                      ← EXISTS (covers pricing)
├── /safety.html                     ← EXISTS
├── /locations.html                  ← Directory hub (lean: 50-state grid + region tiles)
│   ├── /locations/{state}.html      ← 50 state hub pages (17 in batch 1)
│   │   └── /locations/{city-st}.html ← ~85 city/metro pages (20 live)
├── /articles.html                   ← Hub page
│   └── /articles/{slug}            ← Individual articles
├── /about.html
├── /contact.html
└── /author-gyanesh.html
```

**Key rules:**
- `/services/emergency-hvac` is NOT needed — `/emergency.html` already exists
- `/services/ac-installation` is NOT needed — merged into `/services/hvac-replacement`
- Service pages link DOWN to city pages; city pages link UP to service pages
- Articles link to both service pages and city pages contextually
- **State hubs** sit between locations.html and city pages (parent-child)
- **Never publish a state hub without at least 1 city page under it**
- **Metro consolidation** reduces 130 cities to ~85 distinct pages (see master plan for consolidation table)

---

## 2. Service Pages

### Priority Tiers

| Tier | Page | URL | Target Keywords | Build When |
|------|------|-----|-----------------|------------|
| 1 | AC Repair | `/services/ac-repair` | "ac repair near me", "ac not cooling" | Week 1 (now) |
| 1 | Furnace Repair | `/services/furnace-repair` | "furnace repair near me", "furnace not heating" | Week 1 (now) |
| 1 | HVAC Replacement | `/services/hvac-replacement` | "hvac replacement cost", "new ac unit" | Week 1 (now) |
| 2 | Heat Pump Service | `/services/heat-pump` | "heat pump installation", "heat pump vs furnace" | Week 8 (~60 cities) |
| 3 | Duct Cleaning | `/services/duct-cleaning` | "duct cleaning near me", "air duct cleaning cost" | Week 8 |
| 3 | HVAC Maintenance | `/services/hvac-maintenance` | "hvac tune up near me", "ac maintenance" | Week 8 |

### Service Page Structure

Each service page should contain:
1. **H1** — "{Service} Near You | Cool Call Pro"
2. **Intro paragraph** — what the service is, why it matters, referral disclosure
3. **Common signs you need this service** — 5-6 bullet points (problem/solution angle)
4. **Cost range section** — national averages with note that city pages have local costs
5. **City grid** — links to ALL city pages that offer this service (climate-filtered)
6. **Related articles** — 3-4 articles from relevant buckets
7. **FAQ section** — 3-5 service-specific FAQs with FAQPage schema
8. **CTA** — phone number

### Service-to-Climate Relevance Matrix

| Service Page | hot-humid | hot-dry | mixed-humid | cold | mountain |
|-------------|-----------|---------|-------------|------|----------|
| AC Repair | PRIMARY | PRIMARY | YES | YES | YES |
| Furnace Repair | secondary | secondary | YES | PRIMARY | PRIMARY |
| HVAC Replacement | YES | YES | YES | YES | YES |
| Heat Pump | YES | secondary | PRIMARY | YES | YES |
| Duct Cleaning | YES | YES | YES | YES | YES |
| HVAC Maintenance | YES | YES | YES | YES | YES |

- **PRIMARY** = featured prominently in that climate zone's city pages
- **YES** = linked from city pages
- **secondary** = linked only when contextually relevant (e.g., furnace repair in Houston = secondary)

---

## 3. Article Buckets

### Distribution (100 articles total)

| # | Bucket | Count | Revenue Impact | Climate Relevance |
|---|--------|-------|---------------|-------------------|
| 1 | Problem/Solution | 30 | HIGHEST — broken system = immediate call | Varies by problem |
| 2 | Cost Guides | 20 | HIGH — price research = buying intent | Universal |
| 3 | Seasonal/Maintenance | 20 | MEDIUM-HIGH — traffic spikes, recurring | Varies by season |
| 4 | Buying/Comparison | 15 | MEDIUM — research phase, pre-purchase | Universal |
| 5 | Educational/Explainer | 10 | LOW — builds authority, minimal calls | Universal |
| 6 | Local/City-Specific | 5 | MEDIUM — supports city pages directly | City-specific |

### Bucket 1: Problem/Solution (30 articles)

These are the money articles. Someone searching "AC blowing warm air" has a broken system RIGHT NOW.

**Article naming convention:** `/articles/{symptom-or-problem}`

**Example titles:**
- Why Is My AC Blowing Warm Air?  *(already exists)*
- AC Compressor Buzzing, Fan Not Spinning  *(already exists)*
- Furnace Blowing Cold Air in Winter  *(already exists)*
- HVAC Leaking Water Inside House  *(already exists)*
- AC Unit Freezing Up — Causes and Fixes
- Furnace Won't Ignite — Troubleshooting Guide
- Thermostat Not Reaching Set Temperature
- AC Making Grinding/Squealing Noise
- Furnace Short Cycling — Turns On and Off Repeatedly
- HVAC System Blowing Weak Airflow
- AC Running But Not Cooling House Evenly
- Furnace Pilot Light Keeps Going Out
- Heat Pump Not Switching to Heat Mode
- AC Tripping Circuit Breaker Repeatedly
- Burning Smell Coming From Furnace
- AC Condensate Drain Line Clogged
- Furnace Blower Motor Not Working
- Loud Banging Noise When Furnace Starts
- AC Refrigerant Leak Signs and What to Do
- HVAC System Producing Musty or Moldy Smell
- *...10 more based on search volume research*

**Climate tagging for Problem/Solution:**

| Tag | Relevant Climate Zones | Example Articles |
|-----|----------------------|------------------|
| ac-problem | hot-humid, hot-dry, mixed-humid, mountain | AC blowing warm, freezing up, not cooling |
| furnace-problem | cold, mountain, mixed-humid | Furnace cold air, won't ignite, short cycling |
| heat-pump-problem | mixed-humid, cold, mountain | Heat pump not switching modes |
| general-problem | ALL | Thermostat issues, weak airflow, strange smells |

### Bucket 2: Cost Guides (20 articles)

**Article naming convention:** `/articles/{service-or-equipment}-cost`

**Example titles:**
- How Much Does AC Repair Cost? (2026 Guide)
- Furnace Repair Cost Breakdown
- Central AC Installation Cost — What to Expect
- Furnace Replacement Cost by Type
- Heat Pump Installation Cost Guide
- Duct Cleaning Cost — Is It Worth It?
- HVAC Maintenance Plan Cost Comparison
- Emergency HVAC Repair — Weekend and Holiday Rates
- Mini-Split AC System Cost Guide
- Whole-House HVAC Replacement Cost
- *...10 more*

**Climate tagging:** Cost guides are universal — relevant to ALL climate zones. However, city pages should prioritize linking to cost guides that match their primary service needs (e.g., hot cities → AC cost articles, cold cities → furnace cost articles).

### Bucket 3: Seasonal/Maintenance (20 articles)

**Article naming convention:** `/articles/{season-or-task}-{topic}`

**Seasonal distribution:**

| Season | Articles | Peak Traffic | Target Climate Zones |
|--------|----------|-------------|---------------------|
| Spring | 5 | Mar-May | ALL (AC prep) |
| Summer | 5 | Jun-Aug | hot-humid, hot-dry, mixed-humid |
| Fall | 5 | Sep-Nov | ALL (furnace prep) |
| Winter | 5 | Dec-Feb | cold, mountain, mixed-humid |

**Example titles:**
- Spring AC Tune-Up Checklist  *(exists: article-spring-ac)*
- Prepare Your AC for Summer  *(exists: article-ac-summer)*
- Fall Furnace Prep Guide  *(exists: article-fall-prep)*
- Winter Storm HVAC Preparation  *(exists: article-winter-storm)*
- When to Schedule Your Annual HVAC Inspection
- How to Change Your HVAC Filter (And How Often)
- Preparing Your Heat Pump for Season Changes
- End-of-Summer AC Shutdown Checklist
- *...12 more*

### Bucket 4: Buying/Comparison (15 articles)

**Article naming convention:** `/articles/{topic-a}-vs-{topic-b}` or `/articles/best-{equipment}`

**Example titles:**
- Heat Pump vs Furnace — Which Is Right for Your Climate?  *(exists: article-heat-pump)*
- Repair vs Replace — When to Stop Fixing Your Old AC  *(exists: article-repair-vs-replace)*
- Central AC vs Mini-Split — Pros, Cons, and Costs
- Gas Furnace vs Electric Furnace
- SEER2 Ratings Explained — What Efficiency Do You Need?
- Best Thermostat Types for Energy Savings
- Single-Stage vs Two-Stage vs Variable-Speed AC
- *...8 more*

### Bucket 5: Educational/Explainer (10 articles)

**Purpose:** Topical authority building only. Low direct conversion but helps Google understand the site covers HVAC comprehensively.

**Example titles:**
- How Does a Central AC System Work?
- Understanding Your HVAC System Components
- What Is a SEER Rating and Why Does It Matter?
- Carbon Monoxide and Your Furnace — Safety Guide  *(exists: article-carbon-monoxide)*
- HVAC Refrigerant Types Explained  *(exists: article-refrigerant)*
- How HVAC Zoning Works
- *...4 more*

### Bucket 6: Local/City-Specific (5 articles)

**Purpose:** Directly supports city page authority. Only write these for top-revenue metro areas.

**Example titles:**
- HVAC Regulations in Texas — What Homeowners Need to Know
- Arizona Heat and Your AC — A Phoenix-Area Guide
- Chicago HVAC Code Requirements for Homeowners
- Florida Humidity and HVAC — Why Your System Works Harder
- Colorado High-Altitude HVAC — Why Denver Is Different

---

## 4. Article-to-Climate Relevance Matrix

This matrix determines which articles can be linked from which city pages. Each article gets climate tags; city pages pull from their relevant pool.

### Tag System

Every article gets 1-3 tags from this list:

| Tag | Applies to Climate Zones |
|-----|-------------------------|
| `all` | hot-humid, hot-dry, mixed-humid, cold, mountain |
| `hot` | hot-humid, hot-dry |
| `cold` | cold, mountain |
| `humid` | hot-humid, mixed-humid |
| `cooling` | hot-humid, hot-dry, mixed-humid |
| `heating` | cold, mountain, mixed-humid |
| `mixed` | mixed-humid |

### Example Article Tagging

| Article | Tags | Linked from which cities |
|---------|------|------------------------|
| AC Blowing Warm Air | `cooling` | Houston, Phoenix, Atlanta, Dallas, etc. |
| Furnace Won't Ignite | `heating` | Minneapolis, Denver, Chicago, Boston, etc. |
| HVAC Financing Options | `all` | ALL cities |
| Heat Pump vs Furnace | `mixed`, `heating` | Atlanta, Charlotte, Chicago, Denver, etc. |
| Spring AC Tune-Up | `all` | ALL cities |
| Prepare AC for Summer | `hot` | Houston, Phoenix, Las Vegas, Tampa, etc. |
| Fall Furnace Prep | `cold`, `mixed` | Minneapolis, Denver, Chicago, Atlanta, etc. |

---

## 5. Internal Linking Rules

### Link Budget Per Page Type

| Page Type | Outbound Links (body content, excluding nav/footer) |
|-----------|-----------------------------------------------------|
| City page | 5-7 (2-3 articles + 2-3 nearby cities + 1 hub) |
| Service page | 8-12 (city grid + 3-4 articles + hub) |
| Article | 3-5 (1-2 service pages + 1-2 city pages + 1 related article) |

### City Page Linking (current — 20 cities, 12 articles)

Each city page has 3 article link slots:
1. **Climate paragraph** → climate-relevant article
2. **Licensing paragraph** → `/costs.html`
3. **Rebates paragraph** → `/article-hvac-financing.html`

This is fine for now. The financing link is universal and correct.

### City Page Linking (at 40+ cities, 20+ articles) — ROTATION POOL

When the article count supports it, implement this logic in `update_city_pages_v2.py`:

```python
# Each climate_type has a POOL of eligible articles
ARTICLE_POOLS = {
    "hot-humid": [
        ("articles/ac-blowing-warm-air", "why your AC may blow warm air"),
        ("article-ac-summer", "preparing your AC for summer"),
        ("articles/ac-freezing-up", "what causes AC freeze-ups"),
        ("article-spring-ac", "spring AC preparation"),
        # ... more as written
    ],
    "cold": [
        ("article-furnace", "furnace troubleshooting"),
        ("article-winter-storm", "winter storm HVAC preparation"),
        ("article-fall-prep", "fall furnace preparation"),
        ("articles/furnace-wont-ignite", "furnace ignition problems"),
        # ... more as written
    ],
    # ... other climate types
}

# Rotation: use city index to offset into pool
# City 0 gets articles [0,1], City 1 gets [1,2], City 2 gets [2,3], etc.
# This ensures adjacent cities in same climate zone link to DIFFERENT articles
```

**Key rule:** Never force an irrelevant article link for the sake of variety. If only 2 articles in the pool are relevant, link to those 2. Don't link a Minneapolis page to "Prepare AC for Summer" just to be different.

### Service Page → City Page Linking

Each service page should contain a city grid:

```
## AC Repair Service Areas

Our referral network connects homeowners with AC repair professionals in:

[Atlanta, GA](locations/atlanta-ga) · [Birmingham, AL](locations/birmingham-al) · ...
```

Filter by service relevance:
- AC Repair page → all cities (AC is relevant everywhere)
- Furnace Repair page → exclude hot-dry cities OR mark as "limited furnace demand"
- Heat Pump page → prioritize mixed-humid and cold cities

### Article → Service/City Linking

Every article should contain:
1. **1-2 contextual links to service pages** where natural (e.g., "If your AC needs replacing, see our [HVAC replacement service](/services/hvac-replacement)")
2. **1-2 contextual links to city pages** using a "check availability in [City]" pattern, rotating through cities
3. **1 related article link** at the bottom ("Related: [article title]")

---

## 6. Scaling Milestones

| Milestone | Cities | Articles | Service Pages | Action Items |
|-----------|--------|----------|---------------|-------------|
| NOW | 20 | 12 | 0 | Start 3 service pages. Write problem/solution articles. |
| Week 3 | 30 | 16 | 3 live | Service pages link to 30 cities. Update city pages to link to service pages. |
| Week 5 | 40 | 20 | 3 live | **Build article rotation pool** into `update_city_pages_v2.py`. |
| Week 8 | 60 | 28 | 3+3=6 live | Add Tier 2+3 service pages. City pages now have enough link variety. |
| Week 13 | 80 | 40 | 6 live | Evaluate: which articles drive calls? Double down on those buckets. |
| Week 25 | 130 | 80 | 6 live | All cities live. Full rotation pool active. Review for thin/duplicate content. |

### Weekly Production Targets

| Content Type | Per Week | Notes |
|-------------|----------|-------|
| City pages | 10 | Programmatic via `update_city_pages_v2.py` — mainly data collection work |
| Articles | 4 | Priority: 2 problem/solution, 1 cost guide, 1 seasonal (rotate 4th slot) |
| Service pages | As milestones | Not weekly — build at milestone triggers |

### Article Writing Priority Queue

Write in this order to maximize early linking value:

**Weeks 1-4 (first 16 articles):**
- 8 problem/solution (4 AC problems, 4 furnace problems — covers both hot + cold cities)
- 4 cost guides (AC repair cost, furnace repair cost, AC installation cost, furnace replacement cost)
- 4 seasonal (1 per season — spring AC, summer AC, fall furnace, winter furnace)

**Weeks 5-8 (next 12 articles):**
- 6 problem/solution (heat pump issues, thermostat issues, airflow issues)
- 3 buying/comparison (heat pump vs furnace, repair vs replace, SEER ratings)
- 3 cost guides (heat pump cost, duct cleaning cost, maintenance plan cost)

**Weeks 9-13 (next 12 articles):**
- 4 problem/solution (noise issues, smell issues, electrical issues)
- 4 seasonal (deeper seasonal content — 2nd article per season)
- 2 buying/comparison
- 2 educational

---

## 7. Service Page → Existing Page Conflicts

| Proposed Service Page | Existing Page | Resolution |
|----------------------|---------------|------------|
| `/services/emergency-hvac` | `/emergency.html` | DO NOT create. `/emergency.html` already serves this purpose. Add city grid to existing page instead. |
| `/services/ac-installation` | Overlaps with HVAC Replacement | DO NOT create separately. Cover under `/services/hvac-replacement`. |
| `/services/ac-repair` | None | CREATE |
| `/services/furnace-repair` | None | CREATE |
| `/services/hvac-replacement` | `/costs.html` (partial overlap) | CREATE. `/costs.html` covers pricing; service page covers the service itself + city grid. Link between them. |
| `/services/heat-pump` | None | CREATE (Tier 2) |
| `/services/duct-cleaning` | None | CREATE (Tier 3) |
| `/services/hvac-maintenance` | `/article-maintenance.html` (partial) | CREATE (Tier 3). Service page = commercial intent; article = informational. Different purposes. |

---

## 8. Backlink Strategy Notes

Content alone won't rank in 3-6 months without backlinks. Minimum targets:

| Month | Backlinks/Month | Sources |
|-------|----------------|---------|
| 1-3 | 5-10 | HARO/Connectively responses, local business directories, HVAC forum profiles |
| 4-6 | 10-15 | Guest posts on home improvement blogs, local news energy/home sections |
| 7-12 | 15-20 | Consistent outreach, data-driven content that earns links naturally |

**Best link targets:** Cost guide articles and comparison articles — these are the most linkable because other sites reference pricing data.

**Do NOT buy links.** Google's spam team actively penalizes HVAC/home services sites for link schemes.

---

## 9. Updating This File

When adding new articles:
1. Add to the appropriate bucket in Section 3
2. Add climate tags in Section 4
3. If article count hits a milestone (Section 6), update the linking logic

When adding new service pages:
1. Update Section 2 tier table
2. Update the site architecture diagram in Section 1
3. Add to city page linking rules in `city-page-programmatic-seo-16-march-2026.md` Section 6
