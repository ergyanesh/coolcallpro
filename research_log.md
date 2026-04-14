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

---
