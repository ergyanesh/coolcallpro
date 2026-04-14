---
name: city-page-programmatic-seo
description: Single source of truth for generating and updating HVAC city pages with programmatic SEO. Covers all 16 data columns from cities_updated.xlsx, climate zone mapping, schema markup, internal linking, and content templates. Use this skill when creating new city pages OR updating existing ones.
---

# HVAC City Page Programmatic SEO

**Single source of truth** for all HVAC city page generation and updates. This document supersedes both "Building City Pages.md" and "Updates the 20 published HVAC city pages.md".

> **MANDATORY:** After generating or updating ANY pages, run the QC checklist in `site-qc-checklist.md` before deploying.

---

## 1. Data Source

**File:** `cities_updated.xlsx` (project root)

### All 16 Columns

| # | Column Name | Example Value | Used In |
|---|---|---|---|
| 1 | City | Houston | H1, breadcrumb, all paragraphs |
| 2 | State | TX | H1, breadcrumb, meta tags |
| 3 | Est. AC Install Cost | $4,500--$12,000 | Opening paragraph |
| 4 | Est. Furnace Install Cost | $3,000--$6,000 | Opening paragraph |
| 5 | Top 5 Neighborhoods | The Heights, West University Place, Meyerland, Oak Forest, Tanglewood | Opening paragraph |
| 6 | Top 5 ZIP Codes | 77024, 77005, 77019, 77007, 77008 | Opening paragraph, FAQ #3 |
| 7 | Local Permit Office Name | Houston Permitting Center | Opening paragraph, licensing paragraph, FAQ #1 |
| 8 | Local Utility Company | CenterPoint Energy | Climate paragraph, rebates paragraph, FAQ #2 |
| 9 | Population | 2,304,580 | Opening paragraph |
| 10 | Avg Summer High Temp | 95 | Climate paragraph |
| 11 | Avg Winter Low Temp | 43 | Climate paragraph |
| 12 | State SEER Minimum | SEER2 14.3 (Southeast Region) | Climate paragraph |
| 13 | Local Utility Rebates | CenterPoint Energy Standard Offer Program (up to $500/unit) | Rebates paragraph, FAQ #2 |
| 14 | State HVAC License Requirement | TX TDLR Air Conditioning & Refrigeration Contractor License | Licensing paragraph |
| 15 | Climate Zone | Zone 2A (Hot-Humid) | Hero image, climate H2, services list, internal links |
| 16 | City Page Published | Yes | Gate: only "Yes" rows get pages |

### Rules

- Only generate pages for rows where **City Page Published = "Yes"**
- **ALL 15 content columns** (everything except "City Page Published") must appear somewhere on the page
- After generating a new city page, update the xlsx column "City Page Published" to "Yes"

---

## 2. Climate Zone to Region Mapping

### Region Assignment

| Climate Zone Value | climate_type | Region (locations.html hub) | Hero Image |
|---|---|---|---|
| Zone 1A (Very Hot-Humid) | tropical | South Florida / Gulf Coast | `hot-humid-climate-hvac-houston-hero.webp` |
| Zone 2A (Hot-Humid) | hot-humid | Southeast Subtropical | `hot-humid-climate-hvac-houston-hero.webp` |
| Zone 2B (Hot-Dry) | hot-dry | Southwest Desert | `desert-climate-hvac-phoenix-hero.webp` |
| Zone 3A (Warm-Humid) | mixed-humid | Southeast Subtropical | `mixed-humid-climate-hvac-atlanta-hero.webp` |
| Zone 3B (Warm-Dry) | hot-dry | Southwest Desert / Central CA | `desert-climate-hvac-phoenix-hero.webp` |
| Zone 3C (Warm-Marine) | coastal | Pacific Coast (SF Bay, SoCal coast) | `mixed-humid-climate-hvac-atlanta-hero.webp` |
| Zone 4A (Mixed-Humid) | mixed-humid OR cold | Depends on location (see decision logic below) | varies |
| Zone 4B (Mixed-Dry) | mountain | High Desert / Southwest Interior | `mountain-climate-hvac-denver-hero.webp` |
| Zone 4C (Mixed-Marine) | coastal | Pacific Northwest | `mixed-humid-climate-hvac-atlanta-hero.webp` |
| Zone 5A (Cool-Humid) | cold | Northeast / Midwest | `cold-climate-furnace-minneapolis-hero.webp` |
| Zone 5B (Cold-Dry) | mountain | Mountain & High Plains | `mountain-climate-hvac-denver-hero.webp` |
| Zone 6A (Cold-Humid) | cold | Northeast / Midwest | `cold-climate-furnace-minneapolis-hero.webp` |
| Zone 7 (Very Cold) | subarctic | Alaska / Extreme North | `cold-climate-furnace-minneapolis-hero.webp` |

### Zone 4A Decision Logic

Zone 4A cities need manual classification:

| City | State | Assigned climate_type | Rationale |
|---|---|---|---|
| Kansas City | MO | cold | Harsh winters, cold-dominant climate |
| Philadelphia | PA | cold | Northeast location, cold winters |
| St. Louis | MO | mixed-humid | True four-season climate, humid summers |
| Charlotte | NC | mixed-humid | Southeast location, mild winters |
| Baltimore | MD | cold | Mid-Atlantic, cold winters |
| Washington | DC | mixed-humid | Mid-Atlantic but milder, humid summers |
| Nashville | TN | mixed-humid | Southeast, moderate winters |
| Louisville | KY | mixed-humid | Border South, four-season |
| Lexington | KY | mixed-humid | Border South, four-season |
| Raleigh | NC | mixed-humid | Southeast Piedmont |
| Winston-Salem | NC | mixed-humid | Southeast Piedmont |
| Wichita | KS | cold | Great Plains, harsh winters |
| Chattanooga | TN | mixed-humid | Southeast, mild winters |
| Knoxville | TN | mixed-humid | Appalachian foothills |
| Newark | NJ | cold | Northeast corridor |
| New York City | NY | cold | Northeast corridor |
| Richmond | VA | mixed-humid | Mid-Atlantic, mild winters |
| Virginia Beach | VA | mixed-humid | Coastal Mid-Atlantic |
| Dayton | OH | cold | Midwest, cold winters |

---

## 3. Page Structure (HTML sections in order)

Every city page follows this exact section order:

| # | Section | HTML Element | id |
|---|---|---|---|
| 1 | Head | `<head>` | -- |
| 2 | Top Bar | `<div class="topbar">` | -- |
| 3 | Header/Nav | `<header class="header">` | header |
| 4 | Hero | `<section class="city-hero">` | hero |
| 5 | Breadcrumb | `<div class="breadcrumb-nav">` | -- |
| 6 | Opening Paragraph | `<div class="city-context">` | -- |
| 7 | Services List | `<div class="city-services">` | services |
| 8 | Climate H2 + Paragraph | `<div class="city-context">` | -- |
| 9 | Licensing H2 + Paragraph | `<div class="city-services">` | -- |
| 10 | Rebates H2 + Paragraph | `<div class="city-services">` | -- |
| 11 | How It Works | `<section class="section section-dark">` | how-it-works |
| 12 | FAQs | `<section class="section">` | faqs |
| 13 | Nearby Service Areas | `<section class="section">` | nearby |
| 14 | Footer | `<footer class="footer">` | -- |
| 15 | Mobile Call Bar | `<div class="mobile-call-bar">` | -- |

### Head Section Must Include

- `<title>` tag: Uses `get_title()` (shorter than H1) + " | Cool Call Pro" — **max 60 characters** (hard limit). The H1 is descriptive; the title is compact. Example: "HVAC & AC Service in Dallas, TX | Cool Call Pro" (47 chars)
- `<meta name="description">` with city, state, first ZIP code — **max 155 characters** (hard limit). The script template handles this automatically.
- `<link rel="canonical">` -- clean URL, no .html
- Open Graph tags (og:type, og:title, og:description, og:url, og:site_name, og:image)
- Twitter Card tags
- Favicon links
- Stylesheet: `../css/style.min.css`
- Google Fonts (preloaded)
- GA4 (deferred)
- JSON-LD structured data (`@graph` with BreadcrumbList + FAQPage + Organization)
- Inline `<style>` block for city-specific classes

### Hero Section

```html
<section class="city-hero" id="hero">
  <div class="container">
    <span class="section-tag" style="background: rgba(255,255,255,0.1); color: #fff;">&#128205; [City], [State]</span>
    <h1>24/7 Emergency HVAC Repair &amp; AC Service in [City], [State]</h1>
    <p>Connect with independent local HVAC professionals in [City], [State_Full]. Emergency AC repair, furnace service, and system installation available 24/7.</p>
    <p style="font-size: 0.92rem; opacity: 0.75; margin-top: 10px;">We may earn a referral fee when you connect with an HVAC provider through our service.</p>
    <div style="margin-top: 28px;">
      <a href="tel:+18445821795" class="btn btn-primary btn-lg btn-vibrate">
        <span class="phone-icon">&#128222;</span> Call Now &#8212; (844) 582-1795
      </a>
    </div>
  </div>
</section>
```

The hero background image is set via inline CSS in the `<style>` block:

```css
.city-hero {
  background: linear-gradient(rgba(10, 22, 40, 0.88), rgba(10, 22, 40, 0.88)), url('../images/[HERO_IMAGE_FILE]');
  background-size: cover;
  background-position: center;
  color: white;
  padding: 100px 0 80px;
  text-align: center;
}
```

### Breadcrumb

> **UPDATED 19 March 2026:** Breadcrumb now includes state hub level. See `hub-and-spoke-master-plan-19-march-2026.md` for full architecture.

```html
<div class="breadcrumb-nav">
  <div class="container">
    <nav aria-label="Breadcrumb">
      <ol class="breadcrumb-list">
        <li><a href="../index.html">Home</a></li>
        <li><a href="../locations.html">Locations</a></li>
        <li><a href="[state-slug].html">[State_Full]</a></li>
        <li aria-current="page">[City], [State]</li>
      </ol>
    </nav>
  </div>
</div>
```

**State slug examples:** `texas.html`, `new-york.html`, `north-carolina.html`

---

## 4. Schema Markup Templates

### Why Organization, NOT LocalBusiness

Cool Call Pro is a **referral service**, not a local HVAC business. It does not:
- Employ HVAC technicians
- Operate from a local storefront
- Perform HVAC work itself
- Have a physical address per city

Using `LocalBusiness` is **factually inaccurate** and risks a Google manual action for misrepresentation. Use `Organization` instead, which correctly represents a company that connects consumers with service providers.

### Full JSON-LD Template

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://coolcallpro.com/"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Locations",
          "item": "https://coolcallpro.com/locations"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "[State_Full]",
          "item": "https://coolcallpro.com/locations/[state-slug]"
        },
        {
          "@type": "ListItem",
          "position": 4,
          "name": "[City], [State]",
          "item": "https://coolcallpro.com/locations/[slug]"
        }
      ]
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Do I need a permit to replace my AC in [City]?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. In [City], your HVAC contractor should file a mechanical permit with [Permit_Office]. Permits ensure the installation is inspected to code and protect you as the homeowner."
          }
        },
        {
          "@type": "Question",
          "name": "Are there HVAC rebates available in [City]?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "[City] homeowners served by [Utility_Company] may qualify for rebates through [Local_Utility_Rebates]. Federal tax credits of up to $2,000 for qualifying heat pumps and high-efficiency systems may also apply."
          }
        },
        {
          "@type": "Question",
          "name": "What ZIP codes do you serve in [City]?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Our network covers [City] and surrounding areas including [ZIP1], [ZIP2], [ZIP3], [ZIP4], [ZIP5]. Call (844) 582-1795 to verify service availability for your specific ZIP code."
          }
        },
        {
          "@type": "Question",
          "name": "How much does AC replacement cost in [City]?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "A standard central AC replacement in [City] typically costs between [AC_Cost]. Furnace installations range from [Furnace_Cost]. Actual costs depend on system size, efficiency rating, and installation complexity."
          }
        },
        {
          "@type": "Question",
          "name": "What SEER rating is required for new AC units in [State_Full]?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "As of 2025, new AC installations in [State_Full] ([Climate_Zone]) must meet a minimum efficiency standard of [SEER_Minimum]. Higher-efficiency units cost more upfront but reduce monthly energy bills."
          }
        }
      ]
    },
    {
      "@type": "Organization",
      "name": "Cool Call Pro",
      "url": "https://coolcallpro.com",
      "logo": "https://coolcallpro.com/images/og-homepage.png",
      "description": "Cool Call Pro is a 24/7 referral service connecting homeowners with independent HVAC professionals for AC repair, furnace installation, and emergency service.",
      "telephone": "+1-844-582-1795",
      "areaServed": {
        "@type": "City",
        "name": "[City]",
        "containedInPlace": {
          "@type": "State",
          "name": "[State_Full]"
        }
      }
    }
  ]
}
```

**Critical:** All URLs in schema (item, @id, mainEntityOfPage) must use clean URLs -- **NO .html extension**.

---

## 5. Content Templates

### 5.1 Opening Paragraph

**Data columns used:** City, State, Population, Top 5 Neighborhoods, Top 5 ZIP Codes, Est. AC Install Cost, Est. Furnace Install Cost, Local Permit Office Name

```
Need emergency HVAC repair in [City], [State_Full]? With a population of [Population],
[City] is one of [region description]'s most active HVAC markets. Whether you live in
[Neighborhood1], [Neighborhood2], [Neighborhood3], [Neighborhood4], or [Neighborhood5],
we connect you with 24/7 technicians covering [ZIP1], [ZIP2], [ZIP3], [ZIP4], and [ZIP5].
While many breakdowns are simple fixes, if your system is beyond repair, a standard AC
replacement in the area typically averages between [AC_Cost], and new furnace installations
run between [Furnace_Cost]. Ensure your contractor pulls the proper mechanical permits
through the [Permit_Office_Name]. As a referral service, we may earn a fee when you
connect with a provider through our phone line.
```

### 5.2 Climate H2 + Paragraph (5 variants)

**Data columns used:** Climate Zone, Avg Summer High Temp, Avg Winter Low Temp, State SEER Minimum, Local Utility Company

Each variant uses a **climate-specific H2** (not a generic heading).

#### hot-humid (Zone 2A)
**H2:** `Surviving [City] Summers: What Your AC Is Up Against`

```
With summer highs averaging [Avg_Summer_High]°F and humidity that pushes heat indexes even
higher, [City] homeowners rely on air conditioning from April through October. Winter lows
near [Avg_Winter_Low]°F keep heating costs moderate, but the year-round humidity demands
proper drainage and mold-resistant ductwork. As a [Climate_Zone] zone, all new AC
installations must meet a minimum [SEER_Minimum] efficiency rating. If your system is
more than 12 years old, upgrading to a higher-SEER unit can noticeably reduce your
[Utility_Company] bill. Learn more about [keeping your AC running through peak summer
heat](../article-ac-summer.html).
```

#### hot-dry (Zone 2B, Zone 3B)
**H2:** `Desert Heat and Your HVAC: What [City] Homeowners Need to Know`

```
When [City] summers push past [Avg_Summer_High]°F, your air conditioner works harder than
almost anywhere else in the country. The desert climate means low humidity but extreme
heat, making proper system sizing critical -- an undersized unit will run nonstop and fail
prematurely. Winter lows around [Avg_Winter_Low]°F mean you still need reliable heating
for a few months each year. Located in [Climate_Zone], all new installations must meet
[SEER_Minimum] efficiency standards. Proper spring preparation can extend your system's
life -- read our guide on [preparing your AC before the heat arrives](../article-spring-ac.html).
```

#### mixed-humid (Zone 3A, Zone 4A where applicable)
**H2:** `Year-Round Comfort in [City]: Dual-Season HVAC Demands`

```
[City]'s [Climate_Zone] climate means your HVAC system works year-round -- battling
[Avg_Summer_High]°F summer heat and winter lows near [Avg_Winter_Low]°F. This dual demand
makes efficiency essential, and many [City] homeowners are switching to heat pumps that
handle both heating and cooling in a single system. All new installations must meet
[SEER_Minimum] efficiency standards, and [Utility_Company] serves as the primary utility
for most [City] ZIP codes. If you're weighing a heat pump against a traditional furnace-AC
setup, our [heat pump guide](../article-heat-pump.html) breaks down the real-world
differences.
```

#### cold (Zone 5A, Zone 6A, Zone 4A where applicable)
**H2:** `[City] Winters Mean Business: Is Your Furnace Ready?`

```
[City] winters are serious, with temperatures dropping to [Avg_Winter_Low]°F during the
coldest stretches. Your furnace is not a luxury -- it is a lifeline. While summer highs
reach [Avg_Summer_High]°F and AC still matters, the real investment for [City] homeowners
is reliable, efficient heating. Located in [Climate_Zone], heating efficiency standards
are critical here. [Utility_Company] serves most [City] residents, and upgrading an aging
furnace before it fails mid-January is always cheaper than an emergency replacement.
Read our guide on [what to do when your furnace fails during a cold snap](../article-furnace.html).
```

#### mountain (Zone 5B, Zone 4B)
**H2:** `Mile-High HVAC: Why [City] Needs Specialized Equipment`

```
[City]'s high altitude creates HVAC challenges you will not find at sea level. Summer
highs reach [Avg_Summer_High]°F, but winter lows plunge to [Avg_Winter_Low]°F, and the
thin air reduces equipment efficiency by 4-5% per 1,000 feet of elevation. As a
[Climate_Zone] zone, you need contractors who understand high-altitude combustion
adjustments and properly sized blower motors. [Utility_Company] serves most [City]
residents. If you are concerned about winter reliability, our guide on
[preparing for winter storms](../article-winter-storm.html) covers backup power and
emergency heating strategies.
```

#### tropical (Zone 1A)
**H2:** `Year-Round AC in [City]: Why Cooling Never Stops`

```
In [City], air conditioning is not seasonal -- it is essential 365 days a year. With
summer highs averaging [Avg_Summer_High]°F and winter lows rarely dropping below
[Avg_Winter_Low]°F, your AC system runs nearly nonstop. The [Climate_Zone] classification
means extreme humidity that accelerates corrosion, mold growth in ductwork, and
refrigerant pressure issues. All new installations must meet [SEER_Minimum] efficiency
standards, and higher-SEER units make a real difference on your [Utility_Company] bill
when the system runs 10+ months per year. Salt air in coastal areas adds another layer of
wear -- annual maintenance is not optional here. Learn more about [keeping your AC running
through peak summer heat](../article-ac-summer.html).
```

#### coastal (Zone 3C, Zone 4C)
**H2:** `Mild Climate, Hidden HVAC Challenges in [City]`

```
[City]'s [Climate_Zone] marine climate means moderate temperatures year-round -- summer
highs around [Avg_Summer_High]°F and winter lows near [Avg_Winter_Low]°F. While the
mild weather means lower energy bills than most U.S. cities, the persistent moisture and
coastal air create unique HVAC demands: mold prevention, corrosion-resistant equipment,
and proper ventilation matter more here than raw heating or cooling power. All new
installations must meet [SEER_Minimum] efficiency standards. [Utility_Company] serves
most [City] residents. Many homeowners in this climate are switching to heat pumps that
handle both mild heating and cooling efficiently -- our [heat pump guide](../article-heat-pump.html)
breaks down the real-world differences.
```

#### subarctic (Zone 7)
**H2:** `Extreme Cold HVAC: Surviving [City] Winters Below Zero`

```
[City] faces some of the most extreme heating demands in the United States. Winter lows
plunge to [Avg_Winter_Low]°F, and temperatures can stay below freezing for months at a
time. Your furnace is your most critical home system -- a failure in January is not an
inconvenience, it is a genuine emergency that can cause frozen pipes and structural damage
within hours. Summer highs reach [Avg_Summer_High]°F, making AC useful but secondary
to heating. Located in [Climate_Zone], you need contractors experienced with cold-climate
equipment, proper insulation, and backup heating systems. [Utility_Company] serves most
[City] residents. Read our guide on [what to do when your furnace fails during a cold
snap](../article-furnace.html).
```

### 5.3 Services List (8 variants)

Each list has exactly **5 items**. At least 2 must inject `[City]`.

#### hot-humid
1. Emergency AC Repair in [City]
2. High-Humidity Duct Sealing & Mold Prevention
3. Central Air Conditioning Installation & Replacement
4. Heat Pump Installation in [City]
5. HVAC System Maintenance & Seasonal Tune-Ups

#### hot-dry
1. Emergency AC Repair in [City]
2. Desert-Climate AC Sizing & Installation
3. Evaporative-to-Refrigerated Cooling Conversion
4. Furnace Repair & Winter Heating Service in [City]
5. Ductwork Inspection, Cleaning & Sealing

#### mixed-humid
1. Emergency AC Repair in [City]
2. Furnace Repair & Heating Service in [City]
3. Heat Pump Installation & Dual-Fuel Systems
4. Central Air Conditioning Installation & Replacement
5. HVAC System Maintenance & Seasonal Tune-Ups

#### cold
1. Emergency Furnace Repair in [City]
2. High-Efficiency Furnace Installation in [City]
3. Central Air Conditioning Repair & Replacement
4. Boiler Service & Radiant Heating
5. Ductwork Inspection, Cleaning & Insulation

#### mountain
1. High-Altitude Furnace Installation in [City]
2. Emergency HVAC Repair in [City]
3. Central Air Conditioning Installation & Replacement
4. Heat Pump Systems for Mountain Climates
5. Ductwork Inspection & High-Altitude Combustion Testing

#### tropical
1. 24/7 Emergency AC Repair in [City]
2. Corrosion-Resistant AC Installation for Coastal Climates
3. Duct Cleaning & Mold Remediation in [City]
4. High-Efficiency Heat Pump Installation
5. Annual HVAC Maintenance & Hurricane-Season Prep

#### coastal
1. Emergency AC & Heating Repair in [City]
2. Heat Pump Installation in [City]
3. Corrosion-Resistant HVAC Systems for Marine Climates
4. Ductwork Inspection, Mold Prevention & Sealing
5. HVAC System Maintenance & Seasonal Tune-Ups

#### subarctic
1. Emergency Furnace Repair in [City]
2. Cold-Climate Furnace Installation in [City]
3. Boiler Service & Radiant Heating Systems
4. Backup Heating & Generator Integration
5. Ductwork Insulation & Frozen Pipe Prevention

### 5.4 Licensing Paragraph

**Data columns used:** State, State HVAC License Requirement, Local Permit Office Name, City

**H2:** `HVAC Licensing & Permits in [City], [State]`

```
Before hiring any HVAC contractor in [State_Full], verify they hold the proper
[State_HVAC_License_Requirement]. Licensed contractors carry insurance, pull permits
correctly, and stand behind their work. For [City] residents, your local permit office
is [Permit_Office_Name] -- any major installation or system replacement should have a
permit on file. Skipping permits can void manufacturer warranties and create problems
when selling your home. For a full breakdown of what HVAC work costs in your area,
see our [cost guide](../costs.html). For full statewide licensing details and
regulations, see our [State_Full HVAC guide]([state-slug].html).
```

**Note:** If the license requirement value is "No statewide HVAC license required" (e.g., Colorado), adjust the language:

```
[State_Full] does not require a statewide HVAC license, but [City] enforces local
permit requirements through [Permit_Office_Name]. Always verify your contractor carries
liability insurance and workers' compensation coverage. Any major installation or
system replacement should have a permit on file -- skipping permits can void
manufacturer warranties and create problems when selling your home. For a full
breakdown of what HVAC work costs in your area, see our [cost guide](../costs.html).
For full statewide regulations, see our [State_Full HVAC guide]([state-slug].html).
```

### 5.5 Rebates Paragraph

**Data columns used:** City, Local Utility Company, Local Utility Rebates

**H2:** `HVAC Rebates & Tax Credits in [City]`

**BANNED PHRASES:** "Don't pay full price", "save hundreds", "save hundreds -- or even thousands", "significant savings"

```
[City] homeowners served by [Utility_Company] may qualify for rebates through the
[Local_Utility_Rebates] when upgrading to qualifying high-efficiency equipment. Federal
tax credits under the Inflation Reduction Act offer up to $2,000 for heat pumps and
up to $600 for high-efficiency furnaces and central AC systems meeting current ENERGY
STAR standards. Contact [Utility_Company] directly or ask your contractor which current
incentive programs apply to your installation. For financing options beyond rebates, see
our guide on [HVAC financing and payment plans](../article-hvac-financing.html).
```

### 5.6 How It Works Section

This section is **identical across all city pages** except for city/state name injection. It is operational (not SEO content).

```
Subtitle: "From your first call to getting connected with an independent HVAC provider
in [City], [State] -- here's exactly what happens."

Card 01 - "Call and Tell Us Your Issue"
"Call our 24/7 service line and tell us your HVAC issue. Your request will be routed to
an independent professional serving [City] and surrounding areas."

Card 02 - "Connect with an HVAC Provider"
"We connect you with an independent HVAC professional serving your [City], [State] ZIP
code. Licensing, insurance, and availability vary by provider."

Card 03 - "Review Options & Schedule"
"A local [City] provider will confirm availability and discuss options. Service options
and dispatch times vary by area."
```

### 5.7 FAQ Templates (5 FAQs)

Every page must have **exactly 5 FAQs**. The first 3 are existing; FAQs 4 and 5 are new additions.

#### FAQ 1 -- Permits
**Q:** Do I need a permit to replace my AC in [City]?
**A:** Yes. In [City], your HVAC contractor should file a mechanical permit with [Permit_Office_Name]. Pulling the correct permits protects you as a homeowner and ensures work is inspected to code.

#### FAQ 2 -- Rebates
**Q:** Are there HVAC rebates available in [City]?
**A:** [City] homeowners served by [Utility_Company] may qualify for rebates through [Local_Utility_Rebates]. Federal tax credits of up to $2,000 for qualifying heat pumps and high-efficiency systems may also apply. Contact [Utility_Company] or your contractor for current program details.

#### FAQ 3 -- ZIP Coverage
**Q:** What ZIP codes do you serve in [City]?
**A:** Our network covers [City] and surrounding areas including [ZIP1], [ZIP2], [ZIP3], [ZIP4], [ZIP5]. Call (844) 582-1795 to verify service availability for your specific ZIP code.

#### FAQ 4 -- Cost (NEW)
**Q:** How much does AC replacement cost in [City]?
**A:** A standard central AC replacement in [City] typically costs between [AC_Cost]. Furnace installations range from [Furnace_Cost]. Final pricing depends on system size, efficiency rating, ductwork condition, and installation complexity. Get multiple quotes and verify each contractor is licensed through [Permit_Office_Name].

#### FAQ 5 -- SEER Rating (NEW)
**Q:** What SEER rating is required for new AC units in [State_Full]?
**A:** As of 2025, new AC installations in [State_Full] ([Climate_Zone]) must meet a minimum efficiency of [SEER_Minimum]. Higher-SEER units cost more upfront but reduce monthly energy bills on your [Utility_Company] account.

### 5.8 "Also Serving" Section (Metro Absorption) — NEW 20 March 2026

> **Only applies to metro anchor pages** that absorb nearby cities. See `project_city_build_list.md` for the full absorption map.

This section goes **between the Rebates section and How It Works section** (after section 10, before section 11 in the page structure). It adds the absorbed cities' neighborhoods and ZIPs to the anchor page, making the content genuinely unique and comprehensive.

**H2:** `Also Serving the Greater [City] Metro Area`

```html
<section class="section" id="also-serving">
  <div class="container" style="max-width: 760px;">
    <h2 style="font-size: 1.6rem; margin-bottom: 16px; color: var(--navy);">Also Serving the Greater [City] Metro Area</h2>
    <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">
      Our HVAC referral network extends beyond [City] to cover the surrounding metro area,
      including [Absorbed_City_1], [Absorbed_City_2], and [Absorbed_City_3].
    </p>
    <div style="margin-top: 20px;">
      <!-- Repeat for each absorbed city -->
      <h3 style="font-size: 1.15rem; color: var(--navy); margin-bottom: 8px;">[Absorbed_City], [State]</h3>
      <p style="font-size: 0.95rem; line-height: 1.75; color: var(--gray-700);">
        Neighborhoods: [Absorbed_Neighborhoods]. ZIP codes served: [Absorbed_ZIPs].
        Local permits through [Absorbed_Permit_Office].
      </p>
    </div>
  </div>
</section>
```

#### Metro Absorption Map (from project_city_build_list.md)

| Anchor Page | Absorbed Cities |
|---|---|
| Phoenix, AZ | Gilbert |
| San Jose, CA | Fremont, Santa Cruz |
| San Francisco, CA | Santa Rosa |
| San Diego, CA | Chula Vista |
| Denver, CO | Aurora, Boulder |
| Bridgeport, CT | Stamford |
| Miami, FL | Hialeah |
| Tampa, FL | St. Petersburg |
| Chicago, IL | Rockford |
| Des Moines, IA | Davenport |
| Springfield, MA | Pittsfield |
| Detroit, MI | Flint |
| Newark, NJ | Jersey City, Trenton |
| Las Vegas, NV | Henderson |
| Syracuse, NY | Utica |
| Cleveland, OH | Akron, Canton, Youngstown |
| Allentown, PA | Scranton |
| Dallas, TX | Arlington, Plano, Irving, Grand Prairie |
| Virginia Beach, VA | Chesapeake |
| Seattle, WA | Tacoma |

#### Rules for "Also Serving"

1. Pull neighborhoods and ZIPs from `cities_updated.xlsx` for the absorbed city
2. Each absorbed city gets its own `<h3>` with neighborhoods + ZIPs + permit office
3. Do NOT duplicate the climate paragraph, services list, or FAQs — those are shared at the state level
4. The absorbed city's data makes the anchor page MORE unique (more ZIPs, more neighborhoods, different permit offices)
5. Schema `areaServed` should list BOTH the anchor city AND absorbed cities
6. FAQ 3 (ZIP coverage) should include ZIPs from absorbed cities too

#### Updated Schema for Metro Anchor Pages

```json
"areaServed": [
  {
    "@type": "City",
    "name": "[Anchor_City]",
    "containedInPlace": { "@type": "State", "name": "[State_Full]" }
  },
  {
    "@type": "City",
    "name": "[Absorbed_City_1]",
    "containedInPlace": { "@type": "State", "name": "[State_Full]" }
  }
]
```

---

### 5.9 Nearby Service Areas Section (updated 19 March 2026)

**H2:** `Nearby HVAC Service Areas`

```html
<section class="section" id="nearby">
  <div class="container" style="max-width: 760px;">
    <h2 style="font-size: 1.6rem; margin-bottom: 16px; color: var(--navy);">Nearby HVAC Service Areas</h2>
    <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">
      We also connect homeowners with HVAC professionals in nearby cities:
      <a href="[nearby-city-1-slug].html" style="color: var(--orange); font-weight: 600;">[Nearby City 1], [State]</a>,
      <a href="[nearby-city-2-slug].html" style="color: var(--orange); font-weight: 600;">[Nearby City 2], [State]</a>,
      and <a href="[nearby-city-3-slug].html" style="color: var(--orange); font-weight: 600;">[Nearby City 3], [State]</a>.
      View all service areas on our <a href="../locations.html" style="color: var(--orange); font-weight: 600;">locations hub</a>.
    </p>
  </div>
</section>
```

#### Nearby City Assignment Rules

**Priority order for selecting 2-3 nearby links:**

1. **Same-state cities first** (if the state has other city pages)
2. **Same-region/adjacent-state cities** (geographic neighbors)
3. **Same-climate-type cities** (last resort, for isolated markets like Anchorage)

**Rules:**
- Always link to PUBLISHED or BUILT pages only (never to planned-but-not-built cities)
- Prefer larger cities over smaller ones for link equity
- Include the state hub link: `[State_Full] HVAC Guide &#8594;` → `[state-slug].html`
- Include the hub link: `View all HVAC service areas &#8594;` → `../locations.html`

#### Nearby Assignments — Published 20 Cities

| City | Nearby Links |
|---|---|
| Atlanta, GA | Augusta GA, Birmingham AL, Charlotte NC |
| Birmingham, AL | Huntsville AL, Mobile AL, Atlanta GA |
| Boston, MA | Worcester MA, Springfield MA, Providence RI |
| Charlotte, NC | Raleigh NC, Winston-Salem NC, Atlanta GA |
| Chicago, IL | Milwaukee WI, Detroit MI, Indianapolis IN |
| Dallas, TX | Fort Worth TX, Houston TX, San Antonio TX |
| Denver, CO | Colorado Springs CO, Salt Lake City UT, Albuquerque NM |
| Detroit, MI | Grand Rapids MI, Chicago IL, Toledo OH |
| Houston, TX | Dallas TX, San Antonio TX, Austin TX |
| Kansas City, MO | St. Louis MO, Wichita KS, Omaha NE |
| Las Vegas, NV | Phoenix AZ, Reno NV |
| Milwaukee, WI | Madison WI, Chicago IL, Minneapolis MN |
| Minneapolis, MN | Milwaukee WI, Madison WI, Des Moines IA |
| New Orleans, LA | Baton Rouge LA, Houston TX, Birmingham AL |
| Oklahoma City, OK | Tulsa OK, Dallas TX, Wichita KS |
| Philadelphia, PA | Pittsburgh PA, Newark NJ, Baltimore MD |
| Phoenix, AZ | Tucson AZ, Mesa AZ, Las Vegas NV |
| San Antonio, TX | Austin TX, Houston TX, Dallas TX |
| St. Louis, MO | Kansas City MO, Indianapolis IN, Memphis TN |
| Tampa, FL | Jacksonville FL, Miami FL, Tallahassee FL |

> **Note:** These assignments will be updated as new city pages are built. After each batch, re-check that all nearby links point to live pages. See `project_city_build_list.md` for the full build list and batch schedule.

---

## 6. Internal Linking Rules

> **Scaling note:** At 40+ cities and 20+ articles, implement article rotation pools and service page links. See `content-scaling-strategy-16-march-2026.md` for the full linking architecture, article buckets, and milestone triggers.

Each city page must contain **5-7 internal links** (excluding nav/footer links). Here is where each link goes:

### Climate Paragraph Links (1 link)

| climate_type | Link Target | Anchor Text Pattern |
|---|---|---|
| hot-humid | `../article-ac-summer.html` | "keeping your AC running through peak summer heat" |
| hot-dry | `../article-spring-ac.html` | "preparing your AC before the heat arrives" |
| mixed-humid | `../article-heat-pump.html` | "heat pump guide" |
| cold | `../article-furnace.html` | "what to do when your furnace fails during a cold snap" |
| mountain | `../article-winter-storm.html` | "preparing for winter storms" |
| tropical | `../article-ac-summer.html` | "keeping your AC running through peak summer heat" |
| coastal | `../article-heat-pump.html` | "heat pump guide" |
| subarctic | `../article-furnace.html` | "what to do when your furnace fails during a cold snap" |

### Licensing Paragraph (1 link)

- All climate types: `../costs.html` -- anchor: "cost guide"

### Rebates Paragraph (1 link)

- All climate types: `../article-hvac-financing.html` -- anchor: "HVAC financing and payment plans"

### Nearby Service Areas (2-4 links)

- 2-3 same-region city page links (e.g., `dallas-tx.html`)
- 1 hub link: `../locations.html` -- anchor: "locations hub"

### Link Format

All internal links in prose should use inline anchor tags with orange styling:

```html
<a href="../article-ac-summer.html" style="color: var(--orange); font-weight: 600;">keeping your AC running through peak summer heat</a>
```

---

## 7. Hero Image Assignment

### Image Files & Alt Text

| climate_type | Image File | Alt Text Template |
|---|---|---|
| hot-humid | `hot-humid-climate-hvac-houston-hero.webp` | Professional HVAC technician servicing an air conditioning unit in hot-humid climate in [City], [State] |
| hot-dry | `desert-climate-hvac-phoenix-hero.webp` | Desert climate AC system designed for extreme Southwest heat in [City], [State] |
| mixed-humid | `mixed-humid-climate-hvac-atlanta-hero.webp` | Year-round HVAC system for mixed-humid climate with seasonal temperature swings in [City], [State] |
| cold | `cold-climate-furnace-minneapolis-hero.webp` | High-efficiency furnace installation for cold climate winter protection in [City], [State] |
| mountain | `mountain-climate-hvac-denver-hero.webp` | High-altitude HVAC system engineered for mountain climate conditions in [City], [State] |
| tropical | `hot-humid-climate-hvac-houston-hero.webp` | Year-round air conditioning system for tropical climate in [City], [State] |
| coastal | `mixed-humid-climate-hvac-atlanta-hero.webp` | HVAC system for mild marine climate with coastal humidity in [City], [State] |
| subarctic | `cold-climate-furnace-minneapolis-hero.webp` | High-efficiency furnace for extreme cold subarctic conditions in [City], [State] |

### CSS Implementation

The hero image is applied as a CSS background (not an `<img>` tag) with a dark gradient overlay:

```css
.city-hero {
  background: linear-gradient(rgba(10, 22, 40, 0.88), rgba(10, 22, 40, 0.88)),
              url('../images/[IMAGE_FILE]');
  background-size: cover;
  background-position: center;
}
```

All images must be in `/images/` directory, WebP format, under 150KB.

---

## 8. URL Structure

### Rules

| Element | Format | Example |
|---|---|---|
| File path | `locations/[city]-[state].html` | `locations/houston-tx.html` |
| Canonical URL | `https://coolcallpro.com/locations/[slug]` | `https://coolcallpro.com/locations/houston-tx` |
| OG URL | Same as canonical | `https://coolcallpro.com/locations/houston-tx` |
| Schema URLs | Same as canonical | No `.html` |
| Sitemap `<loc>` | Same as canonical | No `.html` |
| Slug format | Lowercase, hyphenated | `kansas-city-mo`, `st-louis-mo`, `san-antonio-tx` |

### Clean URL Rule

**Every** `coolcallpro.com` URL in meta tags, schema JSON-LD, and sitemap must **omit** the `.html` extension. Cloudflare Pages serves both versions; canonicals must use the clean form.

This applies to:
- `<link rel="canonical">`
- `<meta property="og:url">`
- Schema JSON-LD `item`, `@id`, `url`, `mainEntityOfPage`
- Breadcrumb schema `item` URLs
- Sitemap `<loc>` URLs

**Internal `href` links within the HTML** use relative paths WITH `.html` (e.g., `../costs.html`, `houston-tx.html`).

---

## 9. Verification Checklist

Run this checklist after generating or updating any city page:

### Schema & Compliance

- [ ] No `LocalBusiness` schema anywhere on the page -- must use `Organization`
- [ ] BreadcrumbList schema present with 4 levels (Home > Locations > State > City)
- [ ] FAQPage schema present with exactly 5 questions
- [ ] All schema URLs use clean format (no `.html`)
- [ ] Metro anchor pages: `areaServed` lists both anchor city AND absorbed cities

### Content Quality

- [ ] No "save hundreds" or "save hundreds -- or even thousands"
- [ ] No "Don't pay full price"
- [ ] No "significant savings" in rebates paragraph
- [ ] Referral disclosure present in hero subtitle area
- [ ] Population figure included in opening paragraph

### Data Completeness (all 15 content columns)

- [ ] City -- in H1, breadcrumb, all sections
- [ ] State -- in H1, breadcrumb, meta tags
- [ ] Est. AC Install Cost -- in opening paragraph + FAQ 4
- [ ] Est. Furnace Install Cost -- in opening paragraph + FAQ 4
- [ ] Top 5 Neighborhoods -- in opening paragraph
- [ ] Top 5 ZIP Codes -- in opening paragraph + FAQ 3
- [ ] Local Permit Office Name -- in opening paragraph + licensing paragraph + FAQ 1
- [ ] Local Utility Company -- in climate paragraph + rebates paragraph + FAQ 2
- [ ] Population -- in opening paragraph
- [ ] Avg Summer High Temp -- in climate paragraph
- [ ] Avg Winter Low Temp -- in climate paragraph
- [ ] State SEER Minimum -- in climate paragraph + FAQ 5
- [ ] Local Utility Rebates -- in rebates paragraph + FAQ 2
- [ ] State HVAC License Requirement -- in licensing paragraph
- [ ] Climate Zone -- in climate paragraph + FAQ 5

### Page Structure

- [ ] Exactly 5 FAQs (collapsible with orange +/- icons)
- [ ] 5-7 internal links (climate article + cost guide + financing + nearby cities + hub + state guide)
- [ ] Climate-zone-specific H2 text (not generic "Why Homeowners Choose Local Pros")
- [ ] Climate-zone-specific services list (5 items, 2+ with city name)
- [ ] Nearby Service Areas section with 2-3 city links + state guide link + hub link
- [ ] "Also Serving" section present IF page is a metro anchor (see absorption map)
- [ ] 4-level breadcrumb: Home > Locations > State > City (both visible and schema)
- [ ] Mobile-responsive (mobile call bar present)

### Technical

- [ ] Canonical URL uses clean format (no `.html`)
- [ ] OG URL matches canonical
- [ ] GA4 tracking code present (deferred load)
- [ ] `../css/style.min.css` linked
- [ ] `../js/main.min.js` linked with `defer`

---

## 10. Deployment

### Step 1: Generate Pages

Output all city page HTML files to the `locations/` directory:

```
locations/
  atlanta-ga.html
  birmingham-al.html
  boston-ma.html
  charlotte-nc.html
  chicago-il.html
  dallas-tx.html
  denver-co.html
  detroit-mi.html
  houston-tx.html
  kansas-city-mo.html
  las-vegas-nv.html
  milwaukee-wi.html
  minneapolis-mn.html
  new-orleans-la.html
  oklahoma-city-ok.html
  philadelphia-pa.html
  phoenix-az.html
  san-antonio-tx.html
  st-louis-mo.html
  tampa-fl.html
```

### Step 2: Update Sitemap

For each city page, ensure a `<url>` entry exists in `sitemap.xml`:

```xml
<url>
  <loc>https://coolcallpro.com/locations/[slug]</loc>
  <lastmod>[YYYY-MM-DD]</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.8</priority>
</url>
```

- For **new** pages: add the entry
- For **updated** pages: update `<lastmod>` to today's date
- No duplicate entries

### Step 3: Update Locations Hub

After generating pages, update `locations.html`:
1. Add city links under the correct region in the Featured Locations section
2. Alphabetical order within each region
3. Active city links styled in orange

### Step 4: Copy to Deploy Folder

Copy all changed files to the current deploy folder (e.g., `deploy 16 March 2026/`):

```
deploy [DATE]/
  locations/
    [all city .html files]
  locations.html
  sitemap.xml
```

### Step 5: Image Verification

- All hero images exist in `/images/` directory
- All images are WebP format
- All images are under 150KB
- No broken image references

### Step 6: Update Data Source

After generating a new city page, update the `cities_updated.xlsx` column "City Page Published" to "Yes" for that city.

---

## Appendix: Current 20 Published Cities Reference

| City | State | Slug | Climate Zone | climate_type |
|---|---|---|---|---|
| Atlanta | GA | atlanta-ga | Zone 3A (Warm-Humid) | mixed-humid |
| Birmingham | AL | birmingham-al | Zone 3A (Warm-Humid) | mixed-humid |
| Boston | MA | boston-ma | Zone 5A (Cool-Humid) | cold |
| Charlotte | NC | charlotte-nc | Zone 3A/4A (Mixed-Humid) | mixed-humid |
| Chicago | IL | chicago-il | Zone 5A (Cool-Humid) | cold |
| Dallas | TX | dallas-tx | Zone 3A (Warm-Humid) | mixed-humid |
| Denver | CO | denver-co | Zone 5B (Cold-Dry) | mountain |
| Detroit | MI | detroit-mi | Zone 5A (Cool-Humid) | cold |
| Houston | TX | houston-tx | Zone 2A (Hot-Humid) | hot-humid |
| Kansas City | MO | kansas-city-mo | Zone 4A (Mixed-Humid) | cold |
| Las Vegas | NV | las-vegas-nv | Zone 3B (Warm-Dry) | hot-dry |
| Milwaukee | WI | milwaukee-wi | Zone 6A (Cold-Humid) | cold |
| Minneapolis | MN | minneapolis-mn | Zone 6A (Cold-Humid) | cold |
| New Orleans | LA | new-orleans-la | Zone 2A (Hot-Humid) | hot-humid |
| Oklahoma City | OK | oklahoma-city-ok | Zone 3A (Warm-Humid) | mixed-humid |
| Philadelphia | PA | philadelphia-pa | Zone 4A (Mixed-Humid) | cold |
| Phoenix | AZ | phoenix-az | Zone 2B (Hot-Dry) | hot-dry |
| San Antonio | TX | san-antonio-tx | Zone 2A (Hot-Humid) | hot-humid |
| St. Louis | MO | st-louis-mo | Zone 4A (Mixed-Humid) | mixed-humid |
| Tampa | FL | tampa-fl | Zone 2A (Hot-Humid) | hot-humid |
