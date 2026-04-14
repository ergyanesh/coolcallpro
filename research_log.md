# Research Log — Phase 6 Per-City Factual Blocks

Append-only audit trail. One section per city. Every factual claim in every
city's `local_context_html` block MUST trace to a URL + date here. If any
source page later breaks, this log preserves what was authored and why.

Format per city:
- **Date researched:** ISO date
- **Data points found / not_found / partial:** list
- **URLs cited in the block:** bullet list (one per unique URL)
- **Notes:** anything unusual (data contradictions, fallback wording used, etc.)

---

## Minneapolis, MN

- **Date researched:** 2026-04-14
- **Researcher:** Firecrawl subagent + author verification pass
- **Data points found:** climate_profile, local_building_code, utility_rebate_amounts, contractor_license_info, housing_stock, climate_hvac_failure_mode (6/7)
- **Data points not_found:** permit_fees — Minneapolis CPED publishes residential mechanical fees via a JS-rendered Smartsheet embed that could not be extracted. Used honest fallback wording directing readers to contact CPED directly.
- **URLs cited in the block:**
  - https://www.ncei.noaa.gov/access/us-climate-normals/ (NOAA station USW00014922 climate normals 1991-2020)
  - https://data.census.gov/table?q=B25040&g=160XX00US2743000 (Census ACS 2022 5-yr, Minneapolis city)
  - https://www.energystar.gov/products/heat_pumps_air_source (ENERGY STAR Version 6.2 cold-climate heat pump spec)
  - https://www.xcelenergy.com/staticfiles/xe-responsive/Working%20With%20Us/24-1-201%20MN%20Res%20Rebate%20Summary%20Information%20Sheet.pdf (Xcel MN 2024-2026 rebate summary)
  - https://www.irs.gov/credits-deductions/energy-efficient-home-improvement-credit (IRS §25C)
  - https://www.dli.mn.gov/business/plumbing-contractors/mechanical-contractor-bond-requirements (MN DLI bond rules)
  - https://library.municode.com/mn/minneapolis/codes/code_of_ordinances (MCO §244.430)
- **Notes:** ACS category counts sum slightly below the total occupied-units value (common ACS artifact, margins of error independent). NOAA station identifier verified as GHCND USW00014922 = KMSP. MCO Section 244.430 text verified via two independent city publications (Low/No Heat FAQ + Renter Rights page) in addition to municode listing.

---

## Portland, OR

- **Date researched:** 2026-04-14 (v2 — re-run with explicit API URLs)
- **Data points found:** climate_profile, local_building_code, utility_rebate_amounts, contractor_license_info, housing_stock, climate_hvac_failure_mode (6/7)
- **Not_found:** permit_fees — Portland BDS mechanical fee schedule published only as PDF (`portland.gov/ppd/documents/mechanical-permit-fee-schedule-city-portland-effective-july-1-2025/download`) that couldn't be parsed. Used honest fallback wording.
- **URLs cited:** ncei.noaa.gov, api.census.gov/data/2023/acs/acs5 (place 59000 state 41), energytrust.org/residential/incentives/furnace-and-heat-pump, oregon.public.law/statutes/ors_701.021, portland.gov/code/29/30, energy.gov/energysaver/air-source-heat-pumps, irs.gov/credits-deductions/energy-efficient-home-improvement-credit
- **Notes:** Portland's 47.8% electric / 47.3% gas heating split is unusual — highest electric-heat share of any major West Coast city. Defrost-cycle guidance specifically relevant for Portland's damp marine climate.

## San Diego, CA

- **Date researched:** 2026-04-14
- **Data points found:** climate_profile, permit_fees (with itemized fees), local_building_code, contractor_license_info, housing_stock, climate_hvac_failure_mode (6/7)
- **Not_found:** utility_rebate_amounts — sdge.com consistently returned HTTP 403 to every automated fetch attempt. Used ENERGY STAR Rebate Finder + DSIRE as fallback citations.
- **URLs cited:** ncei.noaa.gov, api.census.gov/data/2023/acs/acs5 (place 66000 state 06), sandiego.gov/development-services/forms-publications/information-bulletins/103, sandiego.gov/development-services/codes-regulations, cslb.ca.gov (C-20 classification page), energy.gov/energysaver/air-source-heat-pumps, energystar.gov/rebate-finder, dsireusa.org
- **Notes:** San Diego's 6.52% of occupied units with "no fuel used" for heating is striking — ~34,000 homes operate year-round with no dedicated heating system. Permit fees captured verbatim from IB 103 Table 1B.

## Phoenix, AZ

- **Date researched:** 2026-04-14
- **Data points found:** climate_profile, permit_fees, local_building_code (Cooling Ordinance Chapter 39-5), contractor_license_info, housing_stock, climate_hvac_failure_mode (6/7)
- **Not_found:** utility_rebate_amounts — srpnet.com serves Cloudflare JS challenge blocking automated fetches; aps.com residential rebate URLs returned 404 (APS may have retired rebates per AZ Corp Commission Decision No. 81584). Block includes note directing readers to ENERGY STAR Rebate Finder + verify directly with utility.
- **URLs cited:** ncei.noaa.gov, api.census.gov/data/2022/acs/acs5 (place 55000 state 04), phoenix.gov PDD-Fee-Schedule.pdf, phoenix.gov heatsite Cooling Ordinance PDF, roc.az.gov/license-classifications, energy.gov/energysaver/central-air-conditioning, energystar.gov/rebate-finder
- **Notes:** Phoenix Cooling Ordinance (Chapter 39-5) is one of the most unusual municipal HVAC rules in the country — mandates rental AC hold 82°F max. 111.3 days/year at 100°F+ is the dominant design factor. Ductwork-in-attic issue tied directly to these NOAA numbers. roc.az.gov rejects HEAD requests but GET returns 200 — live despite QC HEAD sweep flagging it.

## St. Louis, MO

- **Date researched:** 2026-04-14 (v2 — re-run with explicit API URLs)
- **Data points found:** climate_profile, local_building_code (Ordinance 70800), contractor_license_info, housing_stock, climate_hvac_failure_mode (5/7)
- **Not_found:** permit_fees — stlouis-mo.gov timed out at network level; Building Division fee schedule unreachable. utility_rebate_amounts — Ameren and Spire both blocked/unparseable. Used ENERGY STAR Rebate Finder + DSIRE fallback; fees directed to Building Division contact.
- **URLs cited:** ncei.noaa.gov, api.census.gov/data/2023/acs/acs5 (place 65000 state 29), library.municode.com/mo/st.louis/codes/code_of_ordinances (substituted during QC because stlouis-mo.gov deep-link was network-unreachable), energy.gov/energysaver/efficient-cooling-hot-humid-climates, energystar.gov/rebate-finder, dsireusa.org, irs.gov/credits-deductions/energy-efficient-home-improvement-credit
- **Notes:** St. Louis median year built of 1938 is among the oldest for any major U.S. city — pre-WWII housing stock retrofit challenges are real and unique. stlouis-mo.gov was entirely unreachable during QC; municode substituted. Ordinance 70800 citation sourced from Google site-search snippet of the stlouis-mo.gov mechanical-permits page; primary-source content is authentic but deep-link URL is not live — author will re-verify once stlouis-mo.gov is reachable.

## Atlanta, GA

- **Date researched:** 2026-04-14
- **Found (4/7):** climate_profile, housing_stock, utility_rebate_amounts, climate_hvac_failure_mode
- **Not_found:** permit_fees (atlantaga.gov 403), local_building_code (municode shell only), contractor_license_info (sos.ga.gov 403)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:04000 state:13), georgiapower.com/residential/save-money-and-energy.html, energy.gov/energysaver/efficient-cooling-hot-humid-climates, irs.gov/.../energy-efficient-home-improvement-credit, dsireusa.org, energystar.gov/rebate-finder
- **Notes:** Georgia Power rebates captured verbatim — 5 line items including ASHP conversion 50% up to $1,000, GSHP $300, thermostat $75, duct sealing $400, tune-up $50. Atlanta's 58% electric heat is higher than typical southern metros — heat-pump market.

## Chicago, IL

- **Date researched:** 2026-04-14
- **Found (3/7):** climate_profile, housing_stock, climate_hvac_failure_mode
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts, contractor_license_info — chicago.gov, comed.com, and peoplesgasdelivery.com all block automated fetches (403/404). ICC code portal also blocked.
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:14000 state:17), energy.gov/energysaver/heat-pump-systems, energystar.gov/rebate-finder, irs.gov/.../energy-efficient-home-improvement-credit
- **Notes:** Chicago is 1.15M occupied units — largest of any city in batch. Median 1952 (pre-WWII/mid-century dominant). 5,974 HDD + polar vortex events justify the dual-fuel specification recommendation. Block is thinner (~580 words) because of .gov blocks; honest fallback language used throughout.

## Louisville, KY

- **Date researched:** 2026-04-14
- **Found (3/7):** climate_profile, housing_stock, climate_hvac_failure_mode
- **Not_found:** permit_fees (louisvilleky.gov 403), local_building_code (municode blocked), utility_rebate_amounts (lge-ku.com 403/404), contractor_license_info (dhbc.ky.gov ECONNREFUSED — complete outage during research window)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:48006 state:21), energy.gov/energysaver/efficient-cooling-hot-humid-climates, energystar.gov/rebate-finder, irs.gov/.../energy-efficient-home-improvement-credit
- **Notes:** Agent discovered a FIPS correction — brief had 48003, correct place code is 48006 for Louisville/Jefferson County metro government balance. Block is thinnest of the batch (~500 words) — Kentucky state infrastructure (dhbc.ky.gov, legislature.ky.gov) was entirely offline during research window. KY Master HVAC Contractor license framework cited by name without verbatim quote.

## Sacramento, CA

- **Date researched:** 2026-04-14
- **Found (6/7):** climate_profile, housing_stock, utility_rebate_amounts, contractor_license_info, climate_hvac_failure_mode, local_building_code (Title 24 Part 6 Climate Zone 12 context)
- **Not_found:** permit_fees — City of Sacramento building fees page is a JS-SPA that returns no content server-side
- **URLs cited:** ncei.noaa.gov (station USW00023232), api.census.gov (place:64000 state:06), smud.org Heating and Cooling Rebates, cslb.ca.gov C-20 classification, energy.gov/energysaver/cooling-whole-house-fan, irs.gov/.../energy-efficient-home-improvement-credit
- **Notes:** SMUD rebates are exceptional — variable-stage HP $3,000 + $2,000 Go Electric Bonus = up to $5,000 per home on gas-to-electric conversion. Customer-owned municipal utility (not IOU) explains the generosity. Sacramento is California Title 24 Climate Zone 12; HERS CF3R verification is part of SMUD rebate eligibility.

## Houston, TX

- **Date researched:** 2026-04-14
- **Found (4/7):** climate_profile, housing_stock, contractor_license_info (TDLR framework — governing statute + admin rules identified; Class A/B scope specifics not verbatim), climate_hvac_failure_mode
- **Not_found:** permit_fees (houstonpermittingcenter.org fee-schedule paths 404), local_building_code (municode JS-SPA), utility_rebate_amounts (CenterPoint 404; Texas deregulated retail market means rebates administered per-REP, not per-TDU)
- **URLs cited:** ncei.noaa.gov (station USW00012960), api.census.gov (place:35000 state:48), tdlr.texas.gov/acr/acr.htm, energy.gov/energysaver/central-air-conditioning, energystar.gov/rebate-finder, dsireusa.org, irs.gov/.../energy-efficient-home-improvement-credit
- **Notes:** Houston is 64.5% electric-heated (not gas) — inverts the typical "Texas = gas country" assumption and is the strongest fact in the block. 3,287 CDD / 1,266 HDD makes Houston one of the most cooling-dominated major metros. TDLR ACR license citation includes Texas Occupations Code Chapter 1302 + 16 TAC Chapter 75 governing authorities.

---
