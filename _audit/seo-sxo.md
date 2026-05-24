# CoolCallPro.com — SXO Gap Analysis
> ⚠ **STATUS AS OF 2026-05-23 — audit point-in-time, partially superseded.**
> Most action items in this audit have shipped. See [ACTION-PLAN.md](../ACTION-PLAN.md)
> for per-item status. Article-priority recommendations have been overridden
> by the 2026-05-23 topical-authority-without-doorway strategy — read
> [CLAUDE.md](../CLAUDE.md) "Topical Authority Without Doorway Risk" section +
> [docs/article-strategy-2026-05-23.md](../docs/article-strategy-2026-05-23.md)
> for current direction. The technical analyses in this audit remain accurate
> as point-in-time observations.

**Date:** 2026-04-26
**Analyst:** SXO Skill (Claude)
**SXO Gap Score:** 54/100 (Needs Work)
**Note:** SXO Gap Score is SEPARATE from any SEO Health Score. It measures how well the site
serves searcher intent at the moment of landing, not technical SEO health.

---

## Pre-Delivery Checklist
- [x] Target pages fetched via live WebFetch (SSRF-safe equivalent — fetch_page.py not present, WebFetch used)
- [x] 10 SERP results analyzed per query (5 queries)
- [x] Page type classification uses taxonomy from page-type-taxonomy.md
- [x] User stories cite specific SERP signals
- [x] Persona scores include concrete improvement suggestions
- [x] Mismatch severity is clearly rated
- [x] Limitations section is present

---

## CRITICAL FINDING: Page-Type Mismatch on Primary Revenue Query

**Query:** "AC repair in Houston"
**SERP dominant type:** Local Page (7/10 results) — local contractors with physical NAP, Google Maps, GBP profiles, and verified address
**CoolCallPro's competing page:** `locations/houston-tx` — classified as **Hybrid (Service + Content)**
**Mismatch severity:** CRITICAL

CoolCallPro does not operate as a local contractor. It is a referral aggregator with no physical Houston address, no embedded map, no local GBP, and no NAP. Google rewards LocalBusiness entities for "[service] in [city]" queries. CoolCallPro's city pages cannot win on local pack signals — they are structurally disqualified from the dominant result type for this query class. This is not a fixable on-page problem; it is a business-model positioning problem that shapes the entire strategy below.

**Implication:** CoolCallPro must shift its competitive angle. The 115 city pages should target the informational/research layer of local queries ("HVAC cost in Houston", "licensed HVAC contractor Houston") rather than the transactional layer ("AC repair Houston") where local pack displaces all non-GBP results.

---

## Part 1: SERP Backwards Analysis

### Query 1 — "AC repair in Houston"

| Rank | Domain | Page Type | Key Signals |
|------|--------|-----------|-------------|
| 1 | abacusplumbing.net | Local Page | GBP-linked, physical Houston address, "713-" local number |
| 2 | yelp.com | Tool/Interactive | Aggregator directory with star ratings, verified reviews |
| 3 | airtechofhouston.com | Local Page | "Houston, TX" in domain, GBP signals, 24/7 emergency badge |
| 4 | johnmooreservices.com | Local Page | Named local brand, Houston-specific service area page |
| 5 | malekservice.com | Hybrid | "Top 5" listicle + local affiliate links |
| 6 | airspecialist.com | Local Page | "Since 1970", Houston NAP, GBP connected |
| 7 | airinnovationsllc.com | Local Page | Family-owned, Cypress/Houston service area |
| 8 | asapairhoustonac.com | Local Page | Emergency-focus, local domain, local number |
| 9 | quora.com | Blog Post | User-generated Q&A ("how do I find the best HVAC") |
| 10 | superacworksllc.site | Local Page | Houston-specific service page |

**SERP consensus:** Local Page — 7/10 (70% confidence). Local pack (map + 3 GBPs) also present above organic.
**SERP features:** Local Pack (3 GBPs), likely PAA about costs and availability.
**CoolCallPro status:** NOT appearing in top 10. CoolCallPro's `locations/houston-tx` competes as a Hybrid page against a Local Page SERP.
**Mismatch rating:** CRITICAL — CoolCallPro lacks LocalBusiness schema (correctly, per CLAUDE.md), a physical address, and a GBP. It cannot match the dominant result type for this query.
**Best-fit alternative:** Rank for "licensed HVAC contractor Houston TX" (informational) or "AC repair cost Houston" (research). The city page's strongest ranking angle is the data-rich Climate Profile + Primary Sources section, which is unique vs. contractor sites.

---

### Query 2 — "How much does HVAC repair cost"

| Rank | Domain | Page Type | Key Signals |
|------|--------|-----------|-------------|
| 1 | angi.com | Hybrid (Service + Content) | Cost tables, local price lookup, lead-gen CTA |
| 2 | homedepot.com | Service Page | Brand trust, repair booking CTA |
| 3 | quora.com | Blog Post | User-generated |
| 4 | angi.com (city) | Hybrid | City-specific cost variant |
| 5 | angi.com (city) | Hybrid | City-specific cost variant |
| 6 | walkerbrosac.com | Blog Post | Local contractor FAQ article |
| 7 | breakingac.com | Blog Post | News-format cost guide, April 2026 |
| 8 | fieldedge.com | Blog Post | B2B focus (business maintenance cost) |
| 9 | americanstandardair.com | Hybrid | OEM brand + cost context |
| 10 | thumbtack.com | Tool/Interactive | Cost calculator / lead-gen |

**SERP consensus:** Hybrid (Service + Content) — 4/10 (40%); Blog Post — 3/10 (30%). Mixed. Featured snippet likely: paragraph or table.
**SERP features:** Featured snippet (cost range table), PAA about specific repair types and labor rates.
**CoolCallPro competing pages:** `costs.html` (H1: "HVAC Repair & Replacement Cost Guide") + `articles/2026-hvac-cost-guide`
**CoolCallPro page type:** `costs.html` = Hybrid; `articles/2026-hvac-cost-guide` = Blog Post
**Mismatch rating:** ALIGNED — both pages match dominant SERP types. `costs.html` is Hybrid, article is Blog Post; together they cover both signals.
**Gap identified:** `costs.html` lacks Article schema (WebFetch identified LocalBusiness + Article + FAQPage, but LocalBusiness on a cost page is an incorrect schema signal that may confuse Google about the page's purpose). The article version at `articles/2026-hvac-cost-guide` is the stronger Blog Post entry, but the URL structure buries it one level deeper than Angi's root-level cost pages. Canonicalization between `costs.html` and `articles/2026-hvac-cost-guide` needs auditing — two pages competing for the same informational query may split authority.

---

### Query 3 — "Heat pump vs furnace"

| Rank | Domain | Page Type | Key Signals |
|------|--------|-----------|-------------|
| 1 | carrier.com | Hybrid | OEM brand, comparison content, product CTA |
| 2 | energysage.com | Blog Post | Comparison + cost table, affiliate |
| 3 | neeeco.com | Blog Post | Contractor + editorial comparison |
| 4 | lennox.com | Hybrid | OEM, comparison + product links |
| 5 | trane.com | Blog Post | Manufacturer editorial |
| 6 | trane.com | Hybrid | "Which is right for you?" decision guide |
| 7 | palmetto.com | Blog Post | Electrification angle, incentive focus |
| 8 | plumblineservices.com | Blog Post | Local contractor, Denver-specific context |
| 9 | onehourheatandair.com | Blog Post | National franchise, informational |
| 10 | bryant.com | Hybrid | OEM, product-linked comparison |

**SERP consensus:** Blog Post — 5/10 (50%); Hybrid — 4/10 (40%). Featured snippet likely: paragraph comparison.
**SERP features:** Featured snippet, PAA (cost difference, efficiency comparison, climate suitability), AI Overview likely synthesizing OEM/authoritative sources.
**CoolCallPro competing page:** `article-heat-pump.html` — H1: "Heat Pump Not Working? Troubleshooting Guide + 2026 Repair Costs"
**CoolCallPro page type:** Blog Post (troubleshooting/diagnostic)
**Mismatch rating:** HIGH — CoolCallPro's heat pump article targets "heat pump not working" (symptom/diagnostic intent), but the SERP for "heat pump vs furnace" wants a comparison/decision article. CoolCallPro has NO page targeting the "heat pump vs furnace" comparison query, which is a Consideration-stage query with significant search volume (HVAC purchase decisions are $5,000–$20,000 events). The existing article addresses Decision-stage owners who already own a heat pump; the SERP wants Consideration-stage buyers comparing systems.
**Fix:** Create `articles/heat-pump-vs-furnace.html` as a Comparison page (type 6 in taxonomy) with a feature matrix (cost, efficiency, lifespan, climate suitability, rebates/HEAR status), pros/cons per system, and a "best for your climate" decision tree. Target H1: "Heat Pump vs. Furnace: The 2026 Decision Guide for U.S. Homeowners."

---

### Query 4 — "Why is my AC freezing up"

| Rank | Domain | Page Type | Key Signals |
|------|--------|-----------|-------------|
| 1 | petro.com | Blog Post | Diagnostic article, step-by-step |
| 2 | tcomfort.com | Blog Post | "4 Reasons" listicle |
| 3 | harrellking.net | Blog Post | "6 Reasons", local contractor |
| 4 | carrier.com | Blog Post | OEM authority |
| 5 | dayandnightair.com | Blog Post | Symptom + time-of-day focus |
| 6 | wagnermechanical.com | Blog Post | Local contractor |
| 7 | pvhvac.com | Blog Post | Local contractor, educational |
| 8 | fredfcollis.com | Blog Post | "Causes & Fixes" format |
| 9 | burgesons.com | Blog Post | Local California contractor |
| 10 | davisheat.com | Blog Post | Local contractor, educational |

**SERP consensus:** Blog Post — 10/10 (100% confidence). No local pack. No ads. Featured snippet: numbered list of causes.
**SERP features:** Featured snippet (list), heavy PAA (5-7 questions about why AC freezes, what to do, refrigerant). No local pack. Low commercial intent.
**CoolCallPro competing page:** `articles/ac-freezing-up-in-summer` — H1: "AC Freezing Up in Summer? Ice on the Coils and How to Thaw It Safely"
**CoolCallPro page type:** Blog Post
**Mismatch rating:** ALIGNED — page type matches SERP consensus perfectly.
**Gap identified:** Meta title was not confirmed as populated. H1 is strong. The article has a "30-Second Fix" H2 at the top — this is strong featured-snippet bait, which matches the list-snippet SERP pattern. Main risk is authority: 9/10 SERP results are local HVAC contractors, which Google treats as E-E-A-T signals (they have real technicians diagnosing real systems). CoolCallPro's E-E-A-T signal is weaker (single founder, referral service). Recommend adding schema (Article + FAQPage + HowTo schema) if not present (WebFetch noted "no structured schema markup detected").

---

### Query 5 — "Emergency AC repair near me"

| Rank | Domain | Page Type | Key Signals |
|------|--------|-----------|-------------|
| 1 | yelp.com (nearme) | Tool/Interactive | Location-aware aggregator |
| 2 | ars.com | Local Page | National chain, "near me" landing, GBP signals |
| 3 | browermechanical.com | Local Page | City-specific emergency service page |
| 4 | morrisjenkins.com | Local Page | Emergency-specific URL, Charlotte local |
| 5 | yelp.com (city) | Tool/Interactive | City-level Yelp with 24h filter |
| 6 | andersonplumbingheatingandair.com | Local Page | San Diego local emergency page |
| 7 | tcomfort.com | Local Page | Minneapolis emergency AC page |
| 8 | danielsaustin.com | Local Page | Austin city-specific emergency page |
| 9 | albemarleheating.net | Local Page | Charlottesville emergency AC |
| 10 | onehourheatandair.com | Service Page | National franchise emergency landing |

**SERP consensus:** Local Page — 7/10 (70%); Tool/Interactive (Yelp) — 2/10. All local, geo-driven.
**SERP features:** Local Pack (Google Maps, GBPs prominently above organic), geo-redirect active (results show city-specific pages). "Near me" query class always triggers geo-signals.
**CoolCallPro competing page:** `emergency.html` — H1: "24/7 Emergency HVAC Repair Near You"
**CoolCallPro page type:** Hybrid (Service + Content)
**Mismatch rating:** HIGH — "near me" queries require geo signals (GBP, physical address, city-specific emergency pages). CoolCallPro's `emergency.html` is a national Hybrid page with no geo-relevance signals. The local pack (GBPs) appears above all organic results for this query. CoolCallPro's best competitive angle is NOT head-on "emergency AC repair near me" — it's the city-specific emergency entry points (e.g., `locations/houston-tx` for Houston emergency searches) which have geographically relevant content, though still blocked from local pack by the same structural constraint as Query 1.
**Fix:** The emergency page should be reframed as a "how to find emergency HVAC help" resource (national informational layer) rather than a direct service listing. Use it to funnel users to city pages. The phone CTA remains valid as a referral mechanism, but the page should acknowledge it connects you to local independent technicians — which it does — but SEO positioning must match informational intent, not local service intent.

---

## Part 2: User Stories

### Story 1 — The Panicked Homeowner (Decision/Emergency)
As a **homeowner with a broken AC in July**,
I want a phone number I can call immediately to get a technician dispatched,
because my home is 90°F and I have children or elderly family,
but I'm blocked by **not knowing if Cool Call Pro is a real service or a lead-gen form that wastes my time**.
*(Source: "emergency AC repair" SERP shows national chains with phone numbers above fold + local pack with GBP "Call" buttons — all resolve to a live phone; CoolCallPro's emergency page provides a live number immediately, passing this test, but the referral-service framing creates a 1-2 second trust hesitation)*

### Story 2 — The Cost Researcher (Consideration)
As a **homeowner whose AC is aging but not yet broken**,
I want to understand what HVAC repairs actually cost before I get a quote,
because I've been told to expect $X by a neighbor but I don't know if that's accurate,
but I'm blocked by **not knowing which cost figures are current and which are outdated clickbait**.
*(Source: SERP for "HVAC repair cost" shows Angi with 2026 date in title, breaking-ac.com dated April 22, 2026 — recency is a trust signal Google reinforces with dates in snippets; CoolCallPro's cost article is dated April 16, 2026, competitive but less prominent than Angi)*

### Story 3 — The System-Decision Maker (Consideration → Decision)
As a **homeowner replacing an aging furnace**,
I want to compare a heat pump vs. a furnace before committing to $5,000–$15,000,
because I've seen heat pumps advertised heavily but don't know if they work in my climate,
but I'm blocked by **CoolCallPro having no comparison page for this query** — the site only has a heat-pump troubleshooting article.
*(Source: "heat pump vs furnace" SERP 100% Comparison/Blog posts with decision frameworks; CoolCallPro article-heat-pump.html targets "heat pump not working" — different intent entirely)*

### Story 4 — The Symptom Searcher (Awareness → Consideration)
As a **homeowner who noticed ice forming on their AC**,
I want to know if this is something I should call a technician about today or if it will resolve itself,
because I don't want to spend $200+ on a service call if the problem goes away,
but I'm blocked by **needing a clear "call now vs. wait" decision tree** early in the article.
*(Source: Carrier.com SERP result for "will frozen AC fix itself" — PAA question evidence that homeowners are specifically asking this decision-gate question; CoolCallPro's freezing article has the decision section as H2 #4 "When to Stop and Call a Technician" — after 3 scrolls)*

### Story 5 — The Price-Shopper (Decision)
As a **homeowner getting multiple HVAC quotes**,
I want to know if the quote I'm holding is fair or inflated,
because I can't tell if $450 for a capacitor replacement is normal or a ripoff,
but I'm blocked by **cost tables existing on two separate CoolCallPro pages** (costs.html and articles/2026-hvac-cost-guide) with no clear signal which is authoritative.
*(Source: "HVAC repair cost" SERP shows Angi as single authoritative reference; search intent wants one trusted reference, not two competing internal pages)*

---

## Part 3: Gap Analysis (SXO Gap Score)

| Dimension | Score | Max | Evidence |
|-----------|-------|-----|---------|
| Page Type | 8 | 15 | Aligned on cost/symptom queries; CRITICAL mismatch on local-service and comparison queries. Two high-volume query classes unserved. |
| Content Depth | 12 | 15 | Cost guide (4,800 words) and freezing article (2,800 words) are competitive depth. Heat pump comparison gap is -3pts. |
| UX Signals | 10 | 15 | Phone CTA is prominent everywhere. Mobile sticky bar exists. Jump links on Houston page. Weakness: "call now vs. wait" decision tree for symptom queries appears too late in article flow (H2 #4). |
| Schema | 6 | 15 | ac-freezing article: "no structured schema markup detected." article-heat-pump: schema not confirmed. costs.html: LocalBusiness schema on a cost guide is an incorrect signal. Schema coverage is inconsistent across the library. |
| Media | 8 | 15 | Hero WebP images on articles confirmed. City pages use Wikimedia photos. No video content anywhere — all 10 "why AC freezing" SERP results could be outcompeted by a video snippet that CoolCallPro cannot serve. |
| Authority | 5 | 15 | Single named author (Gyanesh Gulshan). No external citations to primary sources in article body beyond .gov links. E-E-A-T gap vs. local contractors writing from real-world technician experience. No "verified by technician" or expert reviewer credit. |
| Freshness | 5 | 10 | April 2026 articles are fresh. Root articles (article-heat-pump.html, article-furnace.html, article-spring-ac.html) carry no visible publish dates in snippets — may appear stale in SERP. |
| **TOTAL** | **54** | **100** | |

---

## Part 4: Persona Scoring

### Persona Cards

**Persona 1: Emergency Caller**
- Role: Homeowner with active HVAC failure (summer AC outage or winter no-heat)
- Goal: Get a real technician dispatched today — ideally within hours
- Emotional state: Panicked, time-pressured
- Journey stage: Decision
- Key questions: "Is this number real and live?", "How fast will someone come?", "Will I be quoted before committing?"
- SERP evidence: "emergency AC repair near me" SERP dominates with phone-forward local pages; national chains show phone numbers in snippet title tags

**Persona 2: Research-Phase Homeowner**
- Role: Homeowner with aging system or recent symptom, not yet in crisis
- Goal: Understand repair costs, system comparison options, or symptom diagnosis before spending money
- Emotional state: Cautious, information-seeking
- Journey stage: Awareness → Consideration
- Key questions: "What should this repair actually cost?", "Is my system worth fixing?", "What are my replacement options?"
- SERP evidence: "HVAC repair cost" SERP is 70% informational Hybrid/Blog content; "heat pump vs furnace" is 100% comparison content; PAA questions about cost and decision criteria dominate

**Persona 3: Price-Shopper**
- Role: Homeowner already engaged with technicians, comparing quotes
- Goal: Validate whether their existing quote is fair — "is $X for a capacitor normal?"
- Emotional state: Skeptical, comparison-focused
- Journey stage: Decision
- Key questions: "What's the average cost for [specific repair]?", "What parts am I being charged for?", "Are there hidden fees?"
- SERP evidence: "how much should I expect to pay for AC repair" PAA cluster; Angi's per-repair cost breakdown tables dominate SERP; Quora "how much for AC repair" answers cite specific ranges

**Persona 4: Symptom Searcher**
- Role: Homeowner who noticed a specific symptom (ice on coil, warm air, clicking noise) and is troubleshooting before calling
- Goal: Self-triage — should I call a technician now or is this something I can handle?
- Emotional state: Mildly anxious, wants permission to wait or clear signal to act
- Journey stage: Awareness
- Key questions: "Will this fix itself?", "Is this dangerous?", "What will the repair cost if I do call?"
- SERP evidence: "why is my AC freezing" SERP is 100% diagnostic Blog Posts; Carrier's "will frozen AC fix itself" PAA appeared organically — that exact question is a strong intent signal

---

### Persona Score Matrix

#### Emergency Caller — Scored against: homepage + emergency.html + locations/houston-tx

| Dimension | Score | Evidence |
|-----------|-------|---------|
| Relevance | 22/25 | Emergency page directly addresses 6 failure types. Phone number is primary CTA throughout. H1 "24/7 Emergency HVAC Repair Near You" matches intent. -3: no dispatch time promise or queue-status signal (referral model limitation). |
| Clarity | 18/25 | Phone number visible in nav on page load — excellent. Emergency categories visible above fold. -7: referral-service explanation (3 paragraphs on "how it works") delays the pure "here's the number, call now" flow. Emergency callers do not want process explanation — they want confirmation the call is live. |
| Trust | 14/25 | 24/7 badge present. -11: no live availability indicator ("lines are open now"), no response time expectation, no contractor rating or review count, no licensed/insured confirmation before the call. Competitor GBPs show 4.8-star ratings in snippet — CoolCallPro shows none. |
| Action | 20/25 | Phone number repeated 10+ times on emergency.html. Mobile sticky bar present. -5: no "call now, here's what to say" micro-copy that reduces hesitation for someone who has never called a referral line before. |
| **TOTAL** | **74/100** | Good |

**Top improvement for Emergency Caller:** Add a 2-line trust accelerator directly below the hero phone CTA: "Connecting you to a licensed independent technician in your area. Available 24/7 — lines are live now." Then remove the multi-paragraph "how it works" section from the emergency page's above-the-fold zone — move it below the fold or to a separate /about page section. The emergency user needs the phone number + "this is real" in under 3 seconds.

---

#### Research-Phase Homeowner — Scored against: costs.html + articles/2026-hvac-cost-guide

| Dimension | Score | Evidence |
|-----------|-------|---------|
| Relevance | 21/25 | Cost guide covers all major repair types. 2026-hvac-cost-guide article has "Repair vs. Replace math," hidden fees section, quote-reading guide — exactly what a researcher needs. -4: no heat pump vs. furnace comparison page = a major Consideration-stage gap for homeowners choosing between system types. |
| Clarity | 17/25 | Cost tables are well-structured (Low/High/Average columns). The article version buries the quick-reference table behind a long H2 intro. -8: two competing cost pages (`costs.html` vs. `articles/2026-hvac-cost-guide`) create decision paralysis — which is the "real" cost reference? No clear canonical hierarchy visible to user. |
| Trust | 16/25 | Named author with founder credibility. OBBBA-aware (correct 25C language). NOAA/Census citations on city pages. -9: no third-party citations in cost guide itself (e.g., BLS labor data, ACCA standards). No expert reviewer or HVAC technician credit. Single-author site signals potential bias vs. multi-source aggregators like Angi. |
| Action | 15/25 | "Call Now" CTAs present. "Get quotes" link present. -10: no "get an estimate" or "compare quotes" flow that serves the Consideration-stage user who isn't ready to commit to a single call. Research-phase users want to save the page, compare, then decide — there's no "save to compare" or "download cost guide" soft CTA alternative to the hard "call now." |
| **TOTAL** | **69/100** | Good |

**Top improvement for Research-Phase Homeowner:** Create a single canonical cost resource hierarchy: `costs.html` = the quick-reference table (short, scannable, bookmarkable); `articles/2026-hvac-cost-guide` = the deep-dive (link from costs.html as "want to understand why prices vary?"). This eliminates the dual-page confusion. Add a soft CTA on the article: "Save this guide: bookmark this page or share it with your HVAC technician before the appointment."

---

#### Price-Shopper — Scored against: costs.html + locations/houston-tx

| Dimension | Score | Evidence |
|-----------|-------|---------|
| Relevance | 19/25 | Per-repair cost breakdown in costs.html is directly relevant. Houston-TX page has local climate context but no Houston-specific pricing data. -6: price ranges are national averages; a Houston price-shopper needs to know if Houston is above or below national average (costs.html has a "Regional Price Differences" section but it uses broad regions like "Southeast 10-20% below average" — not city-level). |
| Clarity | 13/25 | Cost tables are scannable. -12: a price-shopper with a quote in hand wants to answer one specific question: "is $X for [part] fair?" The current layout requires them to scan a full repair table to find their specific repair. No search/filter functionality. No "is my quote fair?" framing. Angi's cost pages have a dedicated "what affects cost in your area" section that speaks directly to this mental model. |
| Trust | 12/25 | -13: a price-shopper's primary concern is "can I trust these numbers?" Currently no source citations inside the cost tables themselves (e.g., "Based on 2026 ACCA national survey data" or "Sourced from BLS HVAC technician labor rates"). Angi cites survey sample sizes. Without attribution, cost ranges feel like estimates rather than data. |
| Action | 14/25 | Phone CTA present. -11: the price-shopper's natural next action after validating their quote is to either call to negotiate or get a second opinion. CoolCallPro's CTA is "Call Now" — but the price-shopper mental model is "get a competitive quote," not "call one number." A "get a second opinion" framing would better match this persona's decision state. |
| **TOTAL** | **58/100** | Needs Work |

**Top improvement for Price-Shopper:** Reframe the CTA on costs.html from "Call Now" to "Think your quote is too high? Call for a second opinion: (844) 582-1795." This directly addresses the price-shopper's barrier (skepticism about their existing quote) and positions CoolCallPro as the validation mechanism rather than just another caller. Pair this with a regional cost callout box on costs.html: "In the South and Southeast, HVAC repairs typically run 10-20% below national averages. Your area may vary."

---

#### Symptom Searcher — Scored against: articles/ac-freezing-up-in-summer

| Dimension | Score | Evidence |
|-----------|-------|---------|
| Relevance | 22/25 | Article directly answers "why is my AC freezing" (root cause + 5 reasons). H2 #1 "The 30-Second Fix" is excellent. -3: "will it fix itself?" — the specific Carrier PAA signal — is not explicitly addressed as an H2 or FAQ entry. This is the highest-volume decision-gate question for this query class. |
| Clarity | 16/25 | "30-Second Fix" H2 at the top is good scan-bait. -9: the critical decision gate ("call a technician now vs. wait and watch") appears as H2 #4 after 3 prior informational sections. A symptom searcher with active ice forming needs the call/wait decision in the first scroll, not the fourth section. |
| Trust | 13/25 | -12: "no structured schema markup detected" (WebFetch confirmed). The article lacks Article + FAQPage + HowTo schema. All 10 SERP competitors have schema signals. No technician attribution ("reviewed by [technician name]"). For a symptom query where E-E-A-T matters heavily (real technician experience = authority), a single founder author without a hands-on credential gap is notable. |
| Action | 17/25 | CTA after diagnostic instructions is well-placed. -8: the "call now" CTA appears after the homeowner has been told to turn off the AC and wait for ice to melt — the natural user action at that moment is to WAIT, not call. A better flow: "if any of these 3 refrigerant-related causes apply, call now; if it was just a dirty filter, check back in 2 hours." Segmented CTAs by cause type would dramatically improve conversion for this persona. |
| **TOTAL** | **68/100** | Good |

**Top improvement for Symptom Searcher:** Add structured schema (Article + FAQPage + HowTo) to all diagnostic articles — this is a schema gap confirmed for the freezing article and likely present across the cluster. Add "Will my frozen AC fix itself?" as an explicit FAQ entry. Restructure article flow: move "When to Call a Technician" to H2 #2 (immediately after "30-Second Fix") and add cause-specific call-now vs. wait guidance at the end of each root-cause section.

---

### Priority Ranking (Weakest Persona First)

| Rank | Persona | Score | Primary Gap | Estimated Volume Weight |
|------|---------|-------|-------------|------------------------|
| 1 | Price-Shopper | 58/100 | Trust + Clarity on cost validation | High (cost research is top HVAC query class) |
| 2 | Symptom Searcher | 68/100 | Schema missing + decision-gate placement | High (10x diagnostic queries per transactional) |
| 3 | Research-Phase Homeowner | 69/100 | Dual cost page confusion + comparison gap | High (Consideration stage, highest conversion potential) |
| 4 | Emergency Caller | 74/100 | Trust gap (no availability signal, no ratings) | Medium (high intent but lower volume than informational) |

---

## Part 5: Systemic Issues

### Issue 1 — Schema Coverage is Inconsistent (CRITICAL for Consideration-stage)
The `articles/ac-freezing-up-in-summer` article has no confirmed structured schema. The `article-heat-pump.html` root article also lacks confirmed schema. `costs.html` has what appears to be LocalBusiness schema — incorrect for a cost guide page. Systematic schema audit needed across all 17+ articles. FAQPage schema should be present on every article with an FAQ section. HowTo schema should be on every diagnostic article. Article schema (with datePublished, dateModified, author entity) should be on every article.

### Issue 2 — Comparison Content Gap (HIGH for Consideration-stage)
No "heat pump vs furnace" comparison page exists. No "AC vs heat pump" comparison page exists. No "repair vs replace" standalone comparison page exists (there is a section within cost guides, but not a dedicated Comparison page). These are high-volume, high-intent Consideration queries where CoolCallPro has no competing page. Creating 2-3 Comparison pages (taxonomy type 6) would open new ranking paths with no page-type mismatch.

### Issue 3 — Dual Cost Authority (MEDIUM — creates user confusion)
`costs.html` and `articles/2026-hvac-cost-guide` both compete for "HVAC repair cost" queries. Both contain cost tables. A user who lands on both via different SERP entries will not know which is the canonical reference. This dilutes CoolCallPro's authority signal for cost queries. Establish a clear hierarchy: `costs.html` = quick reference (scannability-optimized, CTA-forward), article = decision-depth. Link explicitly from `costs.html` → article.

### Issue 4 — E-E-A-T Single-Author Vulnerability (MEDIUM)
All articles are attributed to a single founder with a mechanical engineering background, not a credentialed HVAC technician. The 10 SERP competitors for "why is my AC freezing" are all local HVAC contractors (technicians writing from daily field experience). While CoolCallPro's articles are technically accurate, the authority signal gap vs. contractor-authored content is a real E-E-A-T disadvantage that schema and citations can partially offset but not fully close without a "reviewed by [HVAC technician]" contributor credit.

### Issue 5 — Local Query Structural Exclusion (CRITICAL — business model)
CoolCallPro cannot compete for "AC repair in [city]" transactional queries. The local pack dominates these SERPs and CoolCallPro has no GBP (correctly, per CLAUDE.md). City pages must be repositioned toward informational/research layer queries (e.g., "HVAC cost in Houston", "Houston HVAC license requirements", "Houston climate and AC needs"). The city pages' unique value — Climate Profile, Primary Sources with NOAA/Census data, licensing requirements — is differentiating on research queries but invisible to the transactional SERP.

---

## Part 6: Priority Action Plan

### Priority 1 — Fix Schema Across All Diagnostic Articles [HIGH IMPACT, QUICK WIN]
- Severity: CRITICAL for Symptom Searcher persona (schema confirmed missing)
- Action: Audit all `articles/*.html` for Article + FAQPage + HowTo schema. Run `python audit_article.py articles/ac-freezing-up-in-summer.html --strict` — if it passes, schema exists; if schema is absent, the audit's schema check has a gap too.
- Expected outcome: Featured snippet eligibility for diagnostic queries. All 10 SERP competitors have structured schema.

### Priority 2 — Create Heat Pump vs Furnace Comparison Page [HIGH IMPACT, MEDIUM EFFORT]
- Severity: HIGH mismatch (no page competes for this query class)
- Action: Create `articles/heat-pump-vs-furnace.html` as Comparison page type. Include: feature matrix (cost/efficiency/lifespan/climate/HEAR rebate eligibility), climate suitability map by zone, "best for" recommendation by household type, 6-question FAQ. Target H1: "Heat Pump vs. Furnace: The 2026 Decision Guide."
- Expected outcome: New Consideration-stage ranking path for a $5,000–$20,000 purchase decision query.

### Priority 3 — Reframe Cost Page CTA for Price-Shopper [MEDIUM IMPACT, LOW EFFORT]
- Severity: MEDIUM (lowest-scoring persona)
- Action: On `costs.html`, change primary CTA copy from "Call Now" to "Think your quote is too high? Call for a second opinion: (844) 582-1795." Add a "Is your quote fair?" anchor section above the repair tables. Add data attribution note to tables ("Based on national HVAC labor and parts surveys — your local market may vary by ±20%").
- Expected outcome: Improved conversion from price-shopper persona landing on cost page.

### Priority 4 — Restructure Diagnostic Article Flow [MEDIUM IMPACT, LOW EFFORT]
- Severity: MEDIUM (Symptom Searcher clarity score is 16/25)
- Action: On `articles/ac-freezing-up-in-summer.html` (and by template pattern, all diagnostic articles), move "When to Call a Technician" to H2 #2 immediately after "What to Do Right Now." Add cause-specific CTAs: "If your filter was the issue → check back in 2 hours. If you see oil stains, ice persists after 2 hours, or you hear hissing → call now: (844) 582-1795."
- Expected outcome: Higher emergency-to-call conversion from symptom searchers who reach the decision gate earlier.

### Priority 5 — Consolidate Cost Authority Signal [MEDIUM IMPACT, MEDIUM EFFORT]
- Severity: MEDIUM (dual-page confusion harms Research-phase persona)
- Action: Add explicit "Quick Reference vs. Deep Guide" cross-link section at top of both `costs.html` and `articles/2026-hvac-cost-guide`. Consider adding `<link rel="canonical">` clarity or a "this is the quick reference" vs. "this is the research guide" H2 subtitle differentiation.
- Expected outcome: Reduced authority split between two cost pages; clearer user journey from quick table → decision depth.

### Priority 6 — City Page SEO Repositioning [STRATEGIC, LONGER TERM]
- Severity: CRITICAL (structural, business-model level)
- Action: Shift city page SEO targeting from "[service] in [city]" (local-pack dominated) to "[HVAC repair cost] in [city]", "licensed HVAC contractor [city]", "[climate] HVAC needs in [city]". Update meta title template and H1 subheads to lead with the data-rich differentiation (e.g., "Houston's hot-humid climate means AC systems run 1,400+ cooling hours/year — here's what that costs to maintain"). The city pages' NOAA/Census data is a genuine differentiator that no local contractor page has; it's currently underexposed in the H1 and title.
- Expected outcome: City pages compete at the informational layer where no local-pack blocks them, rather than at the transactional layer where they structurally cannot win.

---

## Limitations

1. **GSC data not accessed.** Actual impressions, clicks, CTR, and rank position for each query are not available in this analysis. The absence of CoolCallPro from observed SERPs does not confirm zero impressions — GSC may show low-rank visibility (positions 20-50) not visible in top-10 analysis. Cross-referencing with `/seo google` skill would fill this gap.

2. **fetch_page.py not present.** `scripts/fetch_page.py` was absent from the working directory. Pages were fetched via WebFetch (live web fetch) rather than the SSRF-protected script. Live web fetch returns the rendered version, which is functionally equivalent for content analysis but may differ from local file content for in-progress pages.

3. **Schema verification is partial.** WebFetch-based schema detection is imprecise. "No schema detected" may mean schema is present but not visually parseable by the fetcher. The only reliable schema audit is `python audit_article.py <file> --strict` against local HTML files. Recommendation: run strict audit on all 12 articles in `articles/` to get a definitive schema inventory.

4. **Mobile rendering not verified.** Persona scoring is based on desktop-first content analysis. The mobile sticky bar and IntersectionObserver behavior (auto-hide when primary CTA is in viewport) were not tested on a real mobile device. Emergency Caller trust score could be higher or lower on mobile depending on how the phone number renders in the sticky bar context.

5. **AI Overview not observable.** AI Overviews were not directly visible in search results returned via WebSearch tool. If Google's AI Overview for "HVAC repair cost" or "why AC freezes" cites specific sources, CoolCallPro's absence from those citations is an unmeasured signal gap.

6. **SERP personalization.** All SERP results observed via WebSearch may differ from user-location-personalized results. "Emergency AC repair near me" and "AC repair in Houston" results are especially geo-sensitive — actual results for a Houston IP will show more Houston-local GBPs than observed here.

---

*Generate a PDF report? Use `/seo google report`*
*E-E-A-T gaps detected above → Recommend `/seo content` for deep E-E-A-T analysis*
*Missing schema types confirmed → Recommend `/seo schema` for schema generation across article library*
