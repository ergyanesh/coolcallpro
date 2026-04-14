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
- **Notes:** ACS category counts sum slightly below the total occupied-units value (common ACS artifact, margins of error independent). NOAA station identifier verified as GHCND USW00014922 = KMSP. MCO §244.430 text verified via two independent city publications (Low/No Heat FAQ + Renter Rights page) in addition to municode listing.

---
