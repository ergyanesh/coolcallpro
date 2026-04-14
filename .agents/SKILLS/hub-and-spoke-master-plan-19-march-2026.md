---
name: hub-and-spoke-master-plan
description: Master implementation plan for Cool Call Pro's hub-and-spoke SEO architecture. Covers state hub pages, metro consolidation, 50-state rollout, and the exact order of changes to existing published pages. Read this FIRST before making any structural changes to the site.
---

# Hub-and-Spoke Architecture — Master Implementation Plan

**Created:** 19 March 2026
**Status:** Planning complete. Implementation not started. User has explicitly said "Do not change anything yet" — this file IS the approved plan.
**Revenue target:** $10,000 USD within 9-12 months (phone call referrals)

> **READ THIS FIRST** before touching any location pages, state pages, or structural changes. This plan supersedes the site architecture section in `content-scaling-strategy-16-march-2026.md`.

---

## 1. Why This Architecture Exists

### The Problem
The site has data for 130 cities across ~30 states. Many same-state cities share identical SEER requirements, licensing rules, and climate content. Publishing 130 individual city pages where 40+ would be 80-85% identical to another same-state page = Google doorway page penalty risk.

### The Solution
**Hub-and-spoke + metro consolidation:**
- **50 state hub pages** — contain shared state-level content (licensing, SEER, climate zones, utility landscape)
- **~85 city/metro pages** (down from 130) — contain ONLY local-unique content (permit office, utility, neighborhoods, ZIPs, temps, costs)
- **Metro consolidation** — same-metro cities merge into one page (e.g., 7 DFW cities → 1 Dallas-Fort Worth page)

### What's Currently Live (as of 19 March 2026)
- 20 city pages in `/locations/`
- `locations.html` hub page (climate-region-based, no state directory)
- 12 root articles (`article-*.html`) + 4 subfolder articles (`articles/*.html`)
- Core pages: index, costs, emergency, safety, about, contact, articles, author-gyanesh, privacy, terms, disclaimer, advertising-disclosure, 404

---

## 2. Target Site Architecture

```
coolcallpro.com/
├── /                           ← Homepage
├── /locations                  ← Directory hub (lean: 50-state grid + city grid + region tiles)
│   ├── /locations/texas        ← State hub page (licensing, SEER, climate, utilities, city grid)
│   │   ├── /locations/houston-tx    ← City page (local data only)
│   │   ├── /locations/dallas-tx     ← Metro page (covers DFW: Dallas, Fort Worth, Arlington, etc.)
│   │   ├── /locations/san-antonio-tx
│   │   ├── /locations/austin-tx
│   │   └── ... (standalone TX cities)
│   ├── /locations/california
│   │   ├── /locations/los-angeles-ca
│   │   ├── /locations/san-francisco-bay-area-ca  ← Metro (SF, Oakland, San Jose, etc.)
│   │   └── ...
│   └── ... (all 50 states)
├── /services/ac-repair         ← Service pages (per content-scaling-strategy)
├── /services/furnace-repair
├── /services/hvac-replacement
├── /articles/                  ← Article hub + individual articles
├── /emergency.html
├── /costs.html
└── ... (other core pages)
```

### URL Structure for State Hubs

| Element | Format | Example |
|---------|--------|---------|
| File path | `locations/[state-name].html` | `locations/texas.html` |
| Canonical URL | `https://coolcallpro.com/locations/[state-name]` | `https://coolcallpro.com/locations/texas` |
| Slug format | Lowercase, hyphenated | `new-york`, `north-carolina`, `rhode-island` |

### Breadcrumb Changes

**State hub breadcrumb:**
```
Home > Locations > Texas
```

**City page breadcrumb (CHANGED from current):**
```
CURRENT: Home > Locations > Houston, TX
NEW:     Home > Locations > Texas > Houston, TX
```

City page breadcrumb schema goes from 3 ListItems to 4 ListItems.

---

## 3. Data Requirements

### states.xlsx (NEW — must be created first)

| # | Column | Example (Texas) | Purpose |
|---|--------|----------------|---------|
| 1 | State Name | Texas | H1, breadcrumb, content |
| 2 | State Abbreviation | TX | URL slug, meta tags |
| 3 | SEER2 Region | Southeast | Climate/efficiency section |
| 4 | SEER2 Minimum | SEER2 14.3 | Climate/efficiency section |
| 5 | Climate Zones Present | 2A, 2B, 3A, 3B | Climate overview |
| 6 | State HVAC License Requirement | TDLR AC & Refrigeration Contractor License | Licensing section |
| 7 | Licensing Body/Agency | Texas Dept of Licensing & Regulation | Licensing section |
| 8 | License Lookup URL | https://www.tdlr.texas.gov/... | Verification link |
| 9 | Avg AC Install Cost Range | $4,200-$12,500 | Cost section |
| 10 | Avg Furnace Install Cost Range | $3,000-$7,500 | Cost section |
| 11 | Top 3 Utility Companies | Oncor, CenterPoint, AEP Texas | Utility/rebate section |
| 12 | State Energy Office Rebate Programs | TX PACE Program, TCEQ programs | Rebate section |
| 13 | State Population | 30,503,301 | Opening paragraph |
| 14 | Neighboring States | OK, AR, LA, NM | Nearby state links |
| 15 | State Hub Published | No | Gate column |

### cities_updated.xlsx (EXISTS — 130 cities, all data complete)

No changes needed to existing data. Column 16 (City Page Published) gates which cities get pages.

---

## 4. Metro Consolidation Table

These same-metro cities merge into a single page. The "anchor" city is the page URL. Absorbed cities are mentioned in the opening paragraph, ZIP codes, and neighborhoods but do NOT get their own pages.

### Consolidations involving PUBLISHED pages (requires updating existing pages):

| Metro | Anchor (URL) | Absorbed Cities | Status |
|-------|-------------|----------------|--------|
| DFW Metroplex | dallas-tx (PUBLISHED) | Fort Worth, Arlington, Garland, Grand Prairie, Irving, Plano | H1 becomes "Dallas-Fort Worth", ZIPs/neighborhoods expand |
| Denver Metro | denver-co (PUBLISHED) | Aurora, Boulder | H1 becomes "Denver Metro", ZIPs expand |
| Las Vegas Metro | las-vegas-nv (PUBLISHED) | Henderson | ZIPs expand, mention Henderson |
| Detroit Metro | detroit-mi (PUBLISHED) | Flint | Mention Flint in coverage area |
| Tampa Bay | tampa-fl (PUBLISHED) | St. Petersburg | Mention St. Petersburg |
| Boston Metro | boston-ma (PUBLISHED) | Worcester | Mention Worcester in coverage area |

### Consolidations for NEW pages (no existing pages affected):

| Metro | Anchor (URL) | Absorbed Cities |
|-------|-------------|----------------|
| SF Bay Area | san-francisco-bay-area-ca | San Francisco, Oakland, Fremont, San Jose, Santa Cruz, Santa Rosa |
| San Diego Metro | san-diego-ca | Chula Vista |
| South Florida | miami-fl | Hialeah |
| NE Ohio | cleveland-oh | Akron, Canton, Youngstown |
| NYC Metro | new-york-city-ny | Jersey City, Newark |
| Hampton Roads | virginia-beach-va | Chesapeake |
| Seattle Metro | seattle-wa | Tacoma |
| Southern CT | bridgeport-ct | Stamford |

### Cities that remain STANDALONE (not consolidated):

Every city NOT listed in "Absorbed" above gets its own page. Examples: Columbus OH, Dayton OH, Toledo OH, Pittsburgh PA, Los Angeles CA, Sacramento CA, Jacksonville FL, Nashville TN, etc.

### Final page count estimate:
- ~85 city/metro pages (down from 130)
- 50 state hub pages
- = ~135 total location pages

---

## 5. Implementation Order (Step by Step)

### STEP 0: Create states.xlsx + populate data
- Create the Excel file with 16 columns for all 50 states
- Research and populate batch by batch (same approach as cities_updated.xlsx)
- **No published pages change**

### STEP 1: Build state hub pages for states with published city pages (17 new pages)
States: TX, FL, AZ, CO, GA, PA, NC, LA, AL, MO, MA, IL, MI, WI, MN, OK, NV

Each state hub contains:
- H1: "HVAC Service & Repair in [State] | Cool Call Pro"
- State population, climate zones overview
- SEER2 requirement for the state
- HVAC licensing requirement + licensing body + lookup URL
- Top utility companies + state rebate programs
- Cost ranges for the state
- Grid of city pages within that state (linked)
- Neighboring state links
- FAQ section (3-5 state-specific FAQs)
- CTA with phone number
- Schema: Organization + BreadcrumbList + FAQPage

**No existing pages change in this step. Purely additive.**

### STEP 2: Update locations.html (1 page)

**REMOVE from locations.html:**
- Licensing section (lines ~730-748) — moves to state pages
- Cost comparison table (lines ~671-726) — already on costs.html (duplicate)
- Detailed region card content (climate challenges, common issues, licensing) — distributes to state pages

**KEEP on locations.html:**
- Hero section
- "How it works" 3-step
- 6 climate region tiles (as quick visual navigation)
- FAQs
- CTAs
- Trust and Safety section

**ADD to locations.html:**
- "Browse by State" A-Z grid of all 50 states (17 linked, 33 "Coming Soon" text)
- Reorganized city grid grouped by state (not flat alphabetical)

**UPDATE on locations.html:**
- Schema areaServed — list all 17 states with hubs

### STEP 3: Update 20 city pages (20 pages)

Each city page gets exactly 4 changes:
1. **Breadcrumb HTML** — add state level: Home > Locations > [State] > [City], [ST]
2. **Breadcrumb Schema** — 3 ListItems → 4 ListItems (add state)
3. **Body link** — add "For statewide HVAC regulations, see our [State HVAC guide](state-slug.html)" in licensing paragraph
4. **Nearby section** — add "View all [State] service areas" link to state hub

**Additionally, 6 metro pages get expanded:**
- Dallas: H1 → "Dallas-Fort Worth", expand ZIPs/neighborhoods to cover DFW metro
- Denver: expand to cover Aurora, Boulder
- Las Vegas: expand to cover Henderson
- Detroit: mention Flint
- Tampa: mention St. Petersburg
- Boston: mention Worcester

### STEP 4: Update sitemap.xml (1 file)
- Add 17 state hub URLs (priority: 0.9)
- Update lastmod on locations.html and 20 city pages

### STEP 5: Update 16 articles (16 pages — LOWER PRIORITY, can defer)
- Add state hub links where natural ("homeowners across Texas" → texas.html)
- Keep all existing city links intact
- Additive only — no removals

### STEP 6: Build remaining 33 state hubs (as city pages are added)
**Rule: Never publish a state hub without at least 1 city page under it.**
Build state hub + first city page together as a unit.

### STEP 7: Build new city/metro pages in batches
Follow weekly cadence from content-scaling-strategy (10 city pages/week).
Priority: high-population cities in high-HVAC-demand states first.

---

## 6. What Does NOT Change

- **The 20 published city page URLs** — they keep their current URLs forever
- **Article content** — no article text is removed, only links added
- **Core pages** (costs, emergency, safety, about, contact) — no changes
- **Footer** — stays as-is for now (optional cosmetic update later)
- **Nav links** — stays as-is

---

## 7. State Hub Page Template

### Content sections (in order):

1. **Head** — title (max 60 chars), meta description (max 155 chars), canonical, OG, schema
2. **Top Bar + Header/Nav** — same as all pages
3. **Hero** — state name, population, "Connect with HVAC pros across [State]"
4. **Breadcrumb** — Home > Locations > [State]
5. **Opening paragraph** — state overview, population, climate zones present
6. **Climate Zones section** — H2, explain each zone present in the state, link to relevant articles
7. **SEER2 & Efficiency section** — state's SEER2 region and minimum, what it means for homeowners
8. **Licensing section** — state requirement, licensing body, lookup URL, what to verify
9. **Utility & Rebates section** — top 3 utility companies, state rebate programs, IRA credits
10. **Cost Overview** — state average ranges for AC install + furnace install
11. **City Pages Grid** — "Service Areas in [State]" with links to all city pages in the state
12. **Neighboring States** — "Also serving homeowners in [Neighbor1], [Neighbor2]" with links
13. **FAQs** — 3-5 state-specific questions
14. **CTA** — phone number
15. **Footer** — same as all pages

### Schema for state hub:
```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://coolcallpro.com/" },
        { "@type": "ListItem", "position": 2, "name": "Locations", "item": "https://coolcallpro.com/locations" },
        { "@type": "ListItem", "position": 3, "name": "[State]", "item": "https://coolcallpro.com/locations/[state-slug]" }
      ]
    },
    {
      "@type": "FAQPage",
      "mainEntity": [ ... ]
    },
    {
      "@type": "Organization",
      "name": "Cool Call Pro",
      "url": "https://coolcallpro.com",
      "telephone": "+1-844-582-1795",
      "description": "24/7 referral service connecting homeowners with independent HVAC professionals in [State].",
      "areaServed": {
        "@type": "State",
        "name": "[State]"
      }
    }
  ]
}
```

---

## 8. SEO Safety Checklist for This Architecture

- [ ] No doorway pages — every city page has genuinely unique local data (6+ unique data points)
- [ ] State hubs are substantive (800-1200 words of genuine state-specific content)
- [ ] No state hub published without at least 1 city page under it
- [ ] All metro consolidations mention absorbed cities by name (not hidden)
- [ ] Schema uses Organization, NEVER LocalBusiness
- [ ] 301 redirects set up IF any absorbed city URLs were ever live (currently none are — all 130 unpublished cities never had URLs)
- [ ] The 20 published city page URLs never change
- [ ] No content is removed from city pages — only links added
- [ ] Internal linking is parent-child (hub → state → city) not circular
- [ ] Title tags max 60 chars, meta descriptions max 155 chars on all new pages

---

## 9. Relationship to Other Skill Files

| Skill File | Role | How It Connects |
|-----------|------|----------------|
| This file | Master architecture plan | **Read first.** Defines what to build and in what order. |
| `city-page-programmatic-seo-16-march-2026.md` | City page template + generation rules | Use for building individual city pages. Updated to include state hub breadcrumb. |
| `content-scaling-strategy-16-march-2026.md` | Article + service page roadmap | Use for article planning and writing schedule. Architecture section defers to this file. |
| `hvac-article-writer.md` | Interactive article creation | Use when writing new articles. Updated to include state hub linking. |
| `site-qc-checklist.md` | QC before deploy | **MANDATORY** before every deploy. Updated with state hub checks. |

---

## 10. Quick Reference: Counts

| What | Count |
|------|-------|
| Total states | 50 |
| States with published city pages | 17 |
| Published city pages | 20 |
| Total cities in data sheet | 130 |
| Cities after metro consolidation | ~85 |
| Published articles | 16 (12 root + 4 subfolder) |
| State hubs to build (batch 1) | 17 |
| State hubs to build (batch 2+) | 33 |

---

*Last updated: 19 March 2026*
