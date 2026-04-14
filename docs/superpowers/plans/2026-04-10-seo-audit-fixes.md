# SEO Audit Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 4 SEO issues identified in the audit — remove boilerplate "How It Works" section, reduce CTAs, address dual article URL structure, and add TL;DR boxes to articles — without any visual regressions.

**Architecture:** Batch Python scripts for city page modifications (115 files), manual edits for articles (16 files), CSS addition for TL;DR styling. Generator updated for future page regeneration.

**Tech Stack:** Python (batch HTML editing), HTML/CSS (static site), Cloudflare Pages `_redirects`

---

## File Map

| Action | File(s) | Purpose |
|--------|---------|---------|
| Modify | `generate_city_pages_v3.py` | Remove "How It Works" section + FAQ CTA from template |
| Create | `batch_remove_howworks.py` | One-time script to patch all 115 existing city pages |
| Modify | `css/style.css` | Add `.tldr-box` styles |
| Modify | `css/style.min.css` | Minified version of above |
| Modify | `_redirects` | Add 301s for `/articles/` → unified URL pattern (if needed) |
| Modify | 12 root `article-*.html` files | Add TL;DR box after safety callout |
| Modify | 4 `articles/*.html` files | Add TL;DR box after safety callout |

---

### Task 1: Remove "How It Works" from City Pages

**Why:** This section is 100% identical across all 115 city pages (~150 words of boilerplate). It's the single biggest thin-content signal and was flagged as the #1 critical issue.

**What gets removed:**
- The entire `<!-- How It Works -->` `<section>` (lines 1007-1047 in generator) including its CTA
- The "How It Works" jump link in the hero section (line 947 in generator)

**What stays intact:**
- Hero section, breadcrumbs, local context, climate, services, licensing, rebates, also-serving, FAQs, recommended guides, nearby areas, footer — all untouched

**Files:**
- Modify: `generate_city_pages_v3.py` (template, for future generations)
- Create: `batch_remove_howworks.py` (one-time patch for 115 existing pages)

- [ ] **Step 1: Update the generator template**

In `generate_city_pages_v3.py`, remove the "How It Works" jump link from the hero:
```python
# REMOVE these 2 lines from the hero jump-links block (~line 947):
          <a href="#how-it-works" class="jump-link" style="color: rgba(255,255,255,0.8);">How It Works</a>
          <span class="jump-link-dot" style="color: rgba(255,255,255,0.5);">&#8226;</span>
```

Remove the entire How It Works section (lines 1007-1047):
```python
# REMOVE from "    <!-- How It Works -->" through the closing "</section>" (~40 lines)
```

- [ ] **Step 2: Write batch script to patch existing 115 city pages**

The script reads every `.html` file in `locations/` that is a city page (not a state hub), and:
1. Removes the "How It Works" jump link + its preceding dot separator
2. Removes the entire `<!-- How It Works -->` section block
3. Writes the file back

- [ ] **Step 3: Run the batch script**

```bash
python batch_remove_howworks.py
```

- [ ] **Step 4: Verify 3 sample pages visually (Houston, Denver, Miami)**

Open each in browser, confirm:
- Hero jump links show "Services" and "FAQs" only (no "How It Works")
- Page flows directly from Rebates section → Also Serving (if present) → FAQs
- No broken HTML, no orphaned closing tags

---

### Task 2: Reduce CTAs from 6 to 3 per City Page

**Why:** 6 CTA buttons on a single page feels aggressive and can trigger ad-heavy/spam signals. Reducing to 3 keeps conversion paths without looking desperate.

**Current CTAs (7 phone links total):**
1. Header nav CTA (aria-hidden, functional navigation) — **KEEP**
2. Hero section CTA button — **KEEP** (primary conversion)
3. How It Works CTA — **GONE** (removed in Task 1)
4. FAQ inline link (contextual within answer text) — **KEEP** (not a button)
5. FAQ section CTA button (below FAQ accordion) — **REMOVE**
6. Footer phone link — **KEEP** (standard footer contact)
7. Mobile call bar (sticky bottom) — **KEEP** (essential mobile UX)

**After changes:** 2 prominent CTA buttons (hero + mobile bar), 1 nav button (hidden on mobile), 1 contextual link (FAQ), 1 footer link. Clean and professional.

**Files:**
- Modify: `generate_city_pages_v3.py` (remove FAQ CTA from template)
- The batch script from Task 1 will also handle removing this from existing pages

- [ ] **Step 1: Update generator — remove FAQ section CTA**

In `generate_city_pages_v3.py`, remove the CTA block below the FAQ accordion (~lines 1116-1118):
```python
# REMOVE these 3 lines:
          <div style="text-align: center; margin-top: 32px;">
            <a href="tel:+18445821795" class="btn btn-primary btn-lg btn-vibrate"><span class="phone-icon">&#128222;</span> Call Now &#8212; (844) 582-1795</a>
          </div>
```

- [ ] **Step 2: Add FAQ CTA removal to the batch script**

The batch script (from Task 1) also removes the FAQ CTA `<div>` block from all existing city pages.

- [ ] **Step 3: Verify CTA count on sample pages**

Check Houston, Denver, Miami — confirm only Hero CTA button and mobile bar remain as prominent CTAs.

---

### Task 3: Assess Dual Article URL Structure

**Why:** 12 articles live at `/article-*.html` (root) and 4 at `/articles/*.html` (subdirectory). The audit flagged this as potentially confusing for crawlers.

**Current state:**
- Root articles are already indexed by Google with clean URLs (`/article-emergency`)
- Subdirectory articles also indexed (`/articles/why-is-my-ac-blowing-warm-air`)
- Both have proper canonicals, schema, and 301 `.html` stripping
- `articles.html` hub links to both patterns correctly

**Assessment: DO NOT MOVE the 12 root articles.**
- They're already indexed and ranking
- Moving creates 301 redirect chains (`.html → clean → new path`) which dilute PageRank
- Google has confirmed these URLs; changing them 1 month after launch is needlessly risky
- The real fix: ensure ALL future articles go in `/articles/` (which is already happening)

- [ ] **Step 1: Verify both URL patterns have proper canonicals**

Grep all article files for `<link rel="canonical"` and confirm each matches its sitemap entry.

- [ ] **Step 2: Document the decision**

Add a brief note explaining why both patterns coexist and that all new articles use `/articles/`.

---

### Task 4: Add TL;DR Summary Boxes to All 16 Articles

**Why:** TL;DR / "Quick Answer" boxes at the top of articles are heavily favored for Google featured snippets (Position 0) and AI answer engines. This was flagged as an AEO improvement.

**Placement:** After the safety callout box, before the Table of Contents. This position:
- Doesn't push the ToC below the fold
- Gives readers the key takeaway immediately
- Gets crawled early in the page content

**Styling:** New `.tldr-box` class using existing callout-box pattern, with blue/ice theme.

**Files:**
- Modify: `css/style.css` (add `.tldr-box` styles)
- Modify: `css/style.min.css` (minified)
- Modify: All 12 `article-*.html` files
- Modify: All 4 `articles/*.html` files

- [ ] **Step 1: Add TL;DR CSS styles**

Add to `css/style.css` after the existing `.callout-info` block (~line 2210):

```css
/* TL;DR summary box — article quick answers */
.tldr-box {
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 100%);
  border: 1px solid var(--ice);
  border-left: 4px solid var(--blue);
  border-radius: var(--radius);
  padding: 24px 28px;
  margin: 24px 0;
}

.tldr-box .tldr-label {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--blue);
  margin-bottom: 8px;
}

.tldr-box p {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--gray-800);
  margin: 0;
}

.tldr-box ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.tldr-box ul li {
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--gray-800);
  margin-bottom: 4px;
}
```

- [ ] **Step 2: Minify CSS**

```bash
npx --yes clean-css-cli css/style.css -o css/style.min.css
```

- [ ] **Step 3: Add TL;DR box to each article**

Insert after the safety callout `</div>` and before the `<nav class="toc">`. Each article gets a unique summary. Example for `article-emergency.html`:

```html
<div class="tldr-box">
  <div class="tldr-label">Quick Answer</div>
  <p>The 7 warning signs your HVAC is failing: strange noises, burning smells, weak airflow, short-cycling, rising energy bills, ice on the unit, and age over 15 years. If you notice any of these, schedule a professional inspection before a minor issue becomes a costly emergency.</p>
</div>
```

Each of the 16 articles needs a unique, article-specific TL;DR written from its actual content.

- [ ] **Step 4: Verify TL;DR boxes render correctly**

Open 3 articles in browser, confirm:
- Box appears between safety callout and ToC
- Styling matches the design system (blue/ice theme)
- Text is readable, no overflow issues
- Mobile responsive (check narrow viewport)

---

### Task 5: Final QC

- [ ] **Step 1: Run audit script**

```bash
python audit_script.py
```

- [ ] **Step 2: Spot-check 5 city pages across different states**

Verify: no broken HTML, correct section flow, 3 CTAs max, no "How It Works" remnants.

- [ ] **Step 3: Spot-check 3 articles**

Verify: TL;DR box present, correct placement, unique content per article.
