---
name: site-qc-checklist
description: Mandatory QC checklist for CoolCallPro.com. Run this BEFORE deploying any new or modified pages. Covers technical SEO, schema markup, content quality, internal linking, images, sitemap, and Core Web Vitals. Reference this skill after every build, page creation, or content update.
---

# Cool Call Pro — Site-Wide QC Checklist

**When to use:** After creating or modifying ANY page on coolcallpro.com — whether a city page, article, service page, hub page, or core page. Run the full checklist before copying files to the deploy folder.

---

## 1. HTML Head — Ordering & Required Tags

Every page MUST have these tags in this exact order at the top of `<head>`:

```html
<head>
  <meta charset="UTF-8">                          <!-- FIRST — always -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>...</title>
  <meta name="description" content="...">
  <link rel="canonical" href="https://coolcallpro.com/...">
  <!-- Then: OG tags, schema scripts, stylesheets, GA/analytics -->
</head>
```

**Rules:**
- `<meta charset="UTF-8">` MUST be the first child of `<head>` — before any `<script>`, `<link>`, or other `<meta>` tags. This prevents rendering issues and is a Core Web Vitals requirement.
- Every page MUST have a unique `<title>` tag (**max 60 characters** — hard limit, Google truncates beyond this). The title does NOT have to match the H1; use a shorter version for the title tag.
- Every page MUST have a unique `<meta name="description">` (**max 155 characters** — hard limit, Ahrefs flags anything over this)
- Every page MUST have a `<link rel="canonical">` pointing to itself (absolute URL with `https://coolcallpro.com/`)
- OG tags (`og:title`, `og:description`, `og:image`, `og:url`, `og:type`) required on all content pages

**Verification:**
```bash
# charset must be first in <head>
grep -n "<head>" *.html | head -5  # then check next line is charset
# Check for missing canonical
grep -rL "rel=\"canonical\"" *.html
# Check for missing meta description
grep -rL "meta name=\"description\"" *.html
```

---

## 2. Schema Markup — Type Rules

Cool Call Pro is a **referral service**, NOT a local HVAC company. Schema types must reflect this.

| Page Type | Allowed Schema Types | NEVER Use |
|---|---|---|
| City pages | `Organization`, `BreadcrumbList`, `FAQPage` | `LocalBusiness`, `HVACBusiness`, `HomeAndConstructionBusiness` |
| Articles | `Article`, `BreadcrumbList`, `FAQPage` (if FAQs exist) | `LocalBusiness` |
| Service pages | `Service`, `Organization`, `BreadcrumbList`, `FAQPage` | `LocalBusiness` |
| Author page | `Person`, `BreadcrumbList` | `LocalBusiness` |
| Homepage | `Organization`, `WebSite` | `LocalBusiness` |
| Hub pages | `BreadcrumbList`, `CollectionPage` | `LocalBusiness` |

**Why:** Google states that lead-gen / referral companies are NOT eligible for `LocalBusiness` schema. Using it risks a manual action or schema markup penalty.

**Organization schema template (for city/service pages):**
```json
{
  "@type": "Organization",
  "name": "Cool Call Pro",
  "url": "https://coolcallpro.com",
  "description": "24/7 referral service connecting homeowners with independent HVAC professionals in [City], [State].",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+1-844-582-1795",
    "contactType": "customer service",
    "areaServed": {
      "@type": "City",
      "name": "[City]",
      "containedInPlace": { "@type": "State", "name": "[State_Full]" }
    },
    "availableLanguage": "English"
  }
}
```

**Verification:**
```bash
# Must return 0 matches
grep -rl "LocalBusiness" *.html locations/*.html articles/*.html
grep -rl "HVACBusiness" *.html locations/*.html articles/*.html
```

---

## 3. Content Quality — No Fluff, No Unsubstantiated Claims

**Banned phrases (search and destroy):**
- "save hundreds—or even thousands"
- "Don't pay full price"
- "top-rated" / "best in class" / "industry-leading" (unless citing a specific source)
- "trusted by thousands" (unless you have the data)
- "guaranteed satisfaction" (referral service can't guarantee contractor work)
- Any dollar savings claims without a cited source

**Required transparency:**
- Every city page and service page must clearly state Cool Call Pro is a **referral service**, not an HVAC company. This can be in: top bar, body text, or footer — but at least ONE prominent location per page.
- Cost ranges must use hedging language: "typically runs", "averages", "ranges from" — never "costs exactly" or "you'll pay"

**Verification:**
```bash
grep -ri "save hundreds" *.html locations/*.html
grep -ri "Don't pay full price" *.html locations/*.html
grep -ri "top-rated" *.html locations/*.html
grep -ri "guaranteed satisfaction" *.html locations/*.html
```

---

## 4. Internal Linking — Minimum Requirements

### Per page type:

| Page Type | Min Internal Links in Body | Must Link To |
|---|---|---|
| City page | 5-7 | 2-3 nearby cities + 2-3 relevant articles + locations hub |
| Article | 3-5 | 1-2 related articles + 1 service/core page + 1-2 relevant city pages |
| Service page | 4-6 | 2-3 related articles + 2-3 city pages + costs/emergency page |
| Hub page (locations/articles) | N/A (grid links count) | Intro text should link to 1-2 top-level pages |
| Core page (costs/emergency/safety) | 3-5 | Related articles + locations hub |

### Cross-linking rules:
- **Articles MUST link to city pages** — not just the other way around. Every article should have contextual links to 1-2 relevant cities (e.g., "homeowners in Houston" → Houston city page).
- **City pages link to nearby cities** — same climate region preferred, geographically close. Never link a hot-climate city only to cold-climate cities.
- **Article links on city pages should vary by climate zone** — hot cities link to AC/cooling articles, cold cities link to furnace/heating articles.

### Link format:
- City pages use relative paths: `../article-furnace.html`, `../locations.html`
- Articles use relative paths: `locations/houston-tx.html`
- All links should have descriptive anchor text (not "click here" or "read more")

**Verification:**
```bash
# Count internal links per city page (body only, excluding nav/footer)
# Should be 5-7 per page
# Count articles linking to city pages
grep -l "locations/" article-*.html articles/*.html
```

---

## 5. Images — Format, Size, and Attributes

**Format rules:**
- ALL images must be `.webp` format. No `.png` or `.jpg` originals in the images folder.
- If a PNG/JPG source file is needed for editing, keep it in a separate `/source-images/` folder, never in `/images/`.

**Size limits:**
- Hero/banner images: max 150KB
- Inline content images: max 80KB
- Author photo: max 30KB
- Icons/logos: max 15KB

**Required attributes on every `<img>` tag:**
```html
<img src="..." alt="Descriptive alt text" width="XXX" height="XXX" loading="lazy">
```
- `alt` — descriptive, includes keyword where natural (not keyword-stuffed)
- `width` and `height` — prevents Cumulative Layout Shift (CLS)
- `loading="lazy"` — on all images EXCEPT above-the-fold hero images (those should load eagerly or omit the attribute)

**Verification:**
```bash
# No PNG/JPG in images folder
ls images/*.png images/*.jpg 2>/dev/null  # should return nothing
# Check for missing alt tags
grep -n '<img' *.html | grep -v 'alt='
# Check for missing width/height
grep -n '<img' *.html | grep -v 'width='
```

---

## 6. Sitemap — Accuracy & Priority

**File:** `sitemap.xml` (project root)

**Priority values:**
| Page Type | Priority |
|---|---|
| Homepage | 1.0 |
| Core service pages (emergency, costs, safety) | 0.9 |
| Articles hub | 0.8 |
| Individual articles | 0.7-0.8 |
| City pages | **0.8** |
| Locations hub | 0.8 |
| Author page | 0.6 |
| About, contact | 0.6 |
| Legal pages | 0.3 |

**Rules:**
- Every published page MUST be in the sitemap
- `<lastmod>` MUST be updated whenever page content changes (not just the deploy date — the actual content modification date)
- No template files or unpublished drafts in the sitemap
- URLs must match canonical URLs exactly (no trailing slashes if canonicals don't have them)

**When adding new pages:**
1. Add the `<url>` entry to sitemap.xml
2. Set correct priority per the table above
3. Set `<lastmod>` to today's date
4. Set `<changefreq>` based on type (weekly for service pages, monthly for articles/cities, yearly for legal)

**Verification:**
```bash
# Check city page priority (should be 0.8, not 0.6)
grep -A2 "locations/" sitemap.xml | grep "priority"
# Check for pages not in sitemap
# Compare HTML files against sitemap URLs
```

---

## 7. robots.txt — Template File Blocking

**File:** `robots.txt` (project root)

**Rules:**
- Template files (e.g., `location-template.html`, `cost-city-template.html`) MUST be in `Disallow`
- Published pages should NOT be disallowed
- Sitemap reference must point to `https://coolcallpro.com/sitemap.xml`
- Do not modify the Cloudflare-managed section (AI bot blocks)

**When adding new template files:**
Add a `Disallow: /template-name.html` line after the existing template blocks.

---

## 8. FAQs — Schema + HTML Sync

When a page has FAQ content:
- The FAQ HTML on the page MUST match the FAQPage schema in `<head>` exactly
- Same number of questions, same text, same answers
- Schema answers can be slightly shorter (plain text) but must not contradict the HTML

**City pages: 5 FAQs required**
1. Permit question (uses Permit_Office data)
2. Rebates question (uses Utility + Rebates data)
3. ZIP codes question (uses ZIPs data)
4. Cost question (uses AC_Cost + Furnace_Cost + SEER data)
5. License question (uses License_Requirement + Permit_Office data)

**Verification:**
```bash
# Count FAQ items per city page (should be 5)
for f in locations/*.html; do echo "$f: $(grep -c 'faq-item' $f)"; done
```

---

## 9. Deployment Checklist (run in order)

Before copying ANY files to the deploy folder:

- [ ] **1. HTML validation** — No unclosed tags, no broken entities
- [ ] **2. Schema check** — No `LocalBusiness`, correct types per Section 2
- [ ] **3. Charset ordering** — `<meta charset>` is first child of `<head>` on every page
- [ ] **4. Content check** — No banned phrases (Section 3), referral disclosure present
- [ ] **5. Internal links** — Meet minimums per Section 4, no broken relative paths
- [ ] **6. Image check** — All `.webp`, all have alt/width/height, no oversized files
- [ ] **7. Sitemap update** — New pages added, lastmod updated for changed pages, correct priorities
- [ ] **8. robots.txt** — Template files blocked, no published pages blocked
- [ ] **9. FAQ sync** — HTML matches schema, correct count per page type
- [ ] **10. Cross-page linking** — Articles link to city pages, city pages link to articles (bidirectional)
- [ ] **11. Canonical URLs** — Every page has one, matches sitemap URL exactly
- [ ] **12. Title length** — Every `<title>` tag ≤ 60 characters (rendered, with `&amp;` counting as 1 char)
- [ ] **13. Meta description length** — Every `<meta name="description">` ≤ 155 characters
- [ ] **14. Breadcrumb schema** — Every BreadcrumbList ListItem (including the last one) has an `"item"` URL
- [ ] **15. State hub architecture** — City pages have 4-level breadcrumb (Home > Locations > State > City), state hub link in licensing paragraph, state hub link in nearby section
- [ ] **16. State hub completeness** — No state hub published without at least 1 city page under it. State hub has all required sections (licensing, SEER, climate, utilities, costs, city grid, FAQs)
- [ ] **17. Metro consolidation** — Consolidated metro pages mention all absorbed cities by name. No separate pages exist for absorbed cities.
- [ ] **18. Copy to deploy folder** — Only after all checks pass

---

## 10. Common Mistakes to Avoid

These are mistakes that have actually occurred on this site:

| Mistake | What Happened | Prevention |
|---|---|---|
| `LocalBusiness` schema on city pages | Used for referral service — Google penalizes this | Always use `Organization` (Section 2) |
| Sitemap city priority 0.6 | City pages are revenue pages, need higher priority | Use 0.8 for city pages (Section 6) |
| PNG originals left in /images/ | 3MB+ files served to users | Delete PNGs after webp conversion (Section 5) |
| `<meta charset>` after GA script | Browser may misinterpret encoding | charset MUST be first in `<head>` (Section 1) |
| Stale `<lastmod>` in sitemap | Google sees no content changes | Update lastmod when content changes (Section 6) |
| Articles don't link to city pages | One-way linking wastes link equity | Bidirectional linking required (Section 4) |
| "No license" states break template | "verify they hold the proper **No state license**" — grammatically wrong | Conditional logic for license_req starting with "No" |
| Phoenix linked to Chicago as "nearby" | Climate-zone fallback picked wrong cities | Use geographic neighbor mapping for isolated cities |
| Fluff claims in rebates section | "save hundreds—or even thousands" — unsubstantiated | Factual language only (Section 3) |
| Same H1 on all city pages | Doorway page signal to Google | Vary H1 by climate zone |
| Meta description over 155 chars | Ahrefs flagged 32 pages; Google truncates | Hard limit 155 chars. Count BEFORE writing. |
| Title tag over 60 chars | Ahrefs flagged 34 pages; Google truncates | Hard limit 60 chars. Title ≠ H1 — use a shorter version. |
| BreadcrumbList last item missing `"item"` URL | Ahrefs flagged schema validation error on 22 pages | Every ListItem MUST have `"item"` URL — including the current page |
| `overflow-x: hidden` on `html` element | Breaks `position: sticky` on mobile Safari — hamburger menu scrolls away | Only set `overflow-x: hidden` on `body`, never on `html` |
| State hub published without city pages | Empty state page = thin content signal to Google | Never publish a state hub without at least 1 city page under it |
| City page missing state breadcrumb level | Breaks parent-child hierarchy for Google | City breadcrumb: Home > Locations > State > City (4 levels, not 3) |
| Same-metro cities with separate pages | Doorway page risk — 85% identical content | Use metro consolidation (see `hub-and-spoke-master-plan-19-march-2026.md`) |

---

## 11. Quick Verification Script

Run these commands from the project root after any build:

```bash
# CRITICAL checks (must all pass)
echo "=== CRITICAL ==="
echo "LocalBusiness count:" && grep -rl "LocalBusiness" locations/*.html 2>/dev/null | wc -l
echo "PNG in images:" && ls images/*.png 2>/dev/null | wc -l
echo "JPG in images:" && ls images/*.jpg 2>/dev/null | wc -l
echo "Missing canonical:" && grep -rL 'rel="canonical"' *.html locations/*.html 2>/dev/null | wc -l

# HIGH checks
echo "=== HIGH ==="
echo "Fluff phrases:" && grep -ri "save hundreds\|Don't pay full price\|top-rated\|guaranteed satisfaction" locations/*.html 2>/dev/null | wc -l
echo "Missing charset first:" # manual check needed

# SEO LENGTH checks
echo "=== SEO LENGTH ==="
python3 -c "
import re, glob
for f in sorted(glob.glob('*.html') + glob.glob('articles/*.html') + glob.glob('locations/*.html')):
    with open(f, 'r', encoding='utf-8') as fh: c = fh.read()
    tm = re.search(r'<title>([^<]+)</title>', c)
    if tm and len(tm.group(1).replace('&amp;','&')) > 60: print(f'TITLE OVER 60: {f}')
    dm = re.search(r'<meta name=\"description\"\s+content=\"([^\"]+)\"', c)
    if dm and len(dm.group(1)) > 155: print(f'DESC OVER 155: {f}')
"

# CONTENT checks
echo "=== CONTENT ==="
echo "FAQs per city page:"
for f in locations/*.html; do echo "$(basename $f): $(grep -c 'faq-item' $f)"; done
```

---

*Last updated: 2026-03-18*
*Updated after Ahrefs audit flagged 32 meta descriptions over 155 chars, 34 titles over 60 chars, 22 breadcrumb schema errors, and a sticky header CSS bug.*
