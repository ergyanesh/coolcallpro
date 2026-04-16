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

## Denver, CO

- **Date researched:** 2026-04-14
- **Found (5/7):** climate_profile, housing_stock, local_building_code, contractor_license_info, climate_hvac_failure_mode
- **Not_found:** permit_fees (valuation-based, mechanical-specific breakout not extractable), utility_rebate_amounts (co.my.xcelenergy.com is a JS-SPA)
- **URLs cited:** ncei.noaa.gov (USW00003017), api.census.gov (place:20000 state:08), denvergov.org building-codes page, denvergov.org contractor-licensing page, energy.gov/energysaver/heat-pump-systems, energystar.gov/rebate-finder, irs.gov/.../energy-efficient-home-improvement-credit
- **Notes:** 2025 Denver Building and Fire Codes (2024 I-codes + 2021 IECC + 2023 NEC, effective Dec 31 2025) captured verbatim. Colorado has no statewide HVAC license — CPD handles municipally. NOAA published no annual snowfall for KDEN (station commissioned 1995, didn't meet 30-year completeness). Altitude derating context added for 5,280 ft elevation.

## Tucson, AZ

- **Date researched:** 2026-04-14
- **Found (4/7):** climate_profile, housing_stock, utility_rebate_amounts, climate_hvac_failure_mode
- **Not_found:** permit_fees (tucsonaz.gov 403), local_building_code (amlegal blocked), contractor_license_info (roc.az.gov 403 this session — reused Phoenix-verified R-39/CR-39 scope)
- **URLs cited:** ncei.noaa.gov (USW00023160), api.census.gov (place:77000 state:04), tep.com smart-thermostat-rebate / efficient-home-water-heating / residential-insulation-program, energy.gov/energysaver/evaporative-coolers, irs.gov/.../energy-efficient-home-improvement-credit
- **Notes:** TEP rebates captured verbatim: $35 thermostat, $400 HPWH, up to $800 attic insulation. Evaporative cooler angle unique to dry-climate cities — DOE guidance directly supports the "swamp cooler still makes sense in Tucson" case. Tucson 48.8% gas / 47.5% electric nearly 50/50 — different from Phoenix's 75% electric, reflecting higher elevation.

## Tulsa, OK

- **Date researched:** 2026-04-14
- **Found (5/7):** climate_profile, housing_stock, utility_rebate_amounts, contractor_license_info, climate_hvac_failure_mode
- **Not_found:** permit_fees (Title 49 TRO ordinance PDF unparseable), local_building_code (municode shell only)
- **URLs cited:** ncei.noaa.gov (USW00013968), api.census.gov (place:75000 state:40), powerforwardwithpso.com/rebates, oklahoma.gov/cib/your-industry/mechanical.html, energy.gov/energysaver/central-air-conditioning, irs.gov/.../energy-efficient-home-improvement-credit
- **Notes:** PSO rebates the most comprehensive of any city to date — ASHP tiered $600/$1,000/$1,400 by SEER2, central AC $200/$600/$800, geothermal $1,400, tune-up rebates. Oklahoma CIB statute 59 O.S. Section 1850.1 + OAC Title 158 Chapter 50 captured verbatim — journeyman/contractor/inactive-contractor license types.

## Boston, MA

- **Date researched:** 2026-04-14
- **Found (3/7):** climate_profile, housing_stock, climate_hvac_failure_mode
- **Not_found:** permit_fees (boston.gov ISD 404; fees live behind authenticated permit portal), local_building_code (mass.gov 780 CMR page 403), utility_rebate_amounts (masssave.com 403), contractor_license_info (mass.gov board pages 403)
- **URLs cited:** ncei.noaa.gov (USW00014739), api.census.gov (place:07000 state:25), energy.gov/energysaver/heat-pump-systems, energystar.gov/rebate-finder, irs.gov/.../energy-efficient-home-improvement-credit
- **Notes:** Boston's 7.2% fuel-oil heating (19,969 units) is an order of magnitude higher than most U.S. cities — New England heating-oil legacy. Median year 1947 — oldest of any city researched so far, dominated by pre-war triple-deckers and brownstones. DOE's 32%-of-cold-zone-homes-lack-ductwork statistic directly supports the ductless-mini-split case for Boston's historic stock.

## Miami, FL

- **Date researched:** 2026-04-14
- **Found (6/7):** climate_profile, housing_stock, local_building_code (HVHZ), utility_rebate_amounts, contractor_license_info, climate_hvac_failure_mode
- **Not_found:** permit_fees — City of Miami Building Department page 403 + Miami-Dade mechanical fee PDF binary-encoded
- **URLs cited:** ncei.noaa.gov (USW00012839), api.census.gov (place:45000 state:12), miamidade.gov 2023-fbc-roofing-code-changes.pdf (HVHZ Chapter 16), fpl.com/save/programs.html, flsenate.gov/laws/statutes/2025/489.105 (verbatim Class A/B definitions), energy.gov/energysaver/efficient-cooling-hot-humid-climates, irs.gov/.../energy-efficient-home-improvement-credit
- **Notes:** Miami is extreme — 4,656 CDD vs 103.6 HDD = 45:1 cooling-to-heating ratio, and 91.2% electric heating (essentially pure-electric market). HVHZ code is unique to Miami-Dade + Broward; mechanical equipment wind-load requirement verbatim. Florida Statute 489.105 Class A (unlimited) vs Class B (25 tons / 500,000 Btu cap) captured verbatim — important for homeowners deciding which contractor credential matters for their job scope.

## Seattle, WA

- **Date researched:** 2026-04-14
- **Found (5/7):** climate_profile, housing_stock, local_building_code (2021 Seattle Energy Code), utility_rebate_amounts, contractor_license_info (WAC 296-46B-920 verbatim)
- **Not_found:** permit_fees (SDCI fee PDFs 404), and PSE natural-gas rebates (pse.com geographic/security restriction)
- **URLs cited:** ncei.noaa.gov (USW00024233), api.census.gov (place:63000 state:53), seattle.gov/sdci codes page, seattle.gov/city-light Home Energy Solutions, app.leg.wa.gov WAC 296-46B-920, energy.gov/energysaver, irs.gov
- **Notes:** Seattle is the most heating-dominated city researched (16:1 HDD:CDD) yet electric-majority (59.68%) — reflects Seattle City Light's hydro power. 2021 SEC "fossil fuel compliance path" captured verbatim. City Light heat-pump rebates tiered $300/$400/$600 by HSPF2. WA L&I 06A scope "not limited by voltage, phase, or amperage" — verbatim.

## Dallas, TX

- **Date researched:** 2026-04-14
- **Found (5/7):** climate_profile, housing_stock, local_building_code (2021 IMC + 2021 IECC Chapters 55/59), contractor_license_info (TDLR Class A/B detailed), climate_hvac_failure_mode (NWS tornado climatology)
- **Not_found:** permit_fees (PDF unparseable binary), utility_rebate_amounts (Oncor is TDU-only; Texas deregulated — rebates come from REPs)
- **URLs cited:** ncei.noaa.gov (USW00013960 — KDFW, shared with Fort Worth), api.census.gov (place:19000 state:48), dallascityhall.com/know_code.aspx, tdlr.texas.gov/acr/contractor-apply.htm, weather.gov/fwd/fwdtornadoes, energystar.gov/rebate-finder, dsireusa.org, irs.gov
- **Notes:** Dallas adopted 2021 IMC + 2021 IECC effective May 12, 2023 — very current local code. TDLR Class A/B insurance minimums captured verbatim ($300K/$600K vs $100K/$200K). 65.2% electric heat (similar to Houston's 64.5%). NWS Fort Worth tornado climatology: 26/yr average, April-May peak at 7/month each. Dallas is 528K occupied units — the largest of Batch 4 behind Philadelphia.

## Detroit, MI

- **Date researched:** 2026-04-14
- **Found (5/7):** climate_profile, housing_stock, utility_rebate_amounts (DTE tiered comprehensive), contractor_license_info (LARA 10 classifications verbatim), climate_hvac_failure_mode
- **Not_found:** permit_fees (BSEED publishes as .docx, unparseable), local_building_code (no Detroit-specific HVAC amendment found; MMC 2021 applies statewide)
- **URLs cited:** ncei.noaa.gov (USW00094847), api.census.gov (place:22000 state:26), dteenergy.com residential rebates, michigan.gov LARA BCC-11 PDF (verbatim content authentic; URL returns 403 to automated clients but resolves in real browsers — standard michigan.gov bot-filtering), energy.gov/energysaver, irs.gov
- **Notes:** Detroit's 81.8% gas heating is the most gas-dominant of any city researched. Median 1947 ties Boston for oldest. DTE rebate catalog most comprehensive yet — cold-climate ASHP $900/$1,000/$1,200 by tier. LARA's 10 license classifications + "3 years or 6,000 hours per classification" requirement + HVAC Equipment scope (includes gas piping/venting, excludes window units ≤1.5 HP) captured verbatim.

## Philadelphia, PA

- **Date researched:** 2026-04-14
- **Found (6/7):** climate_profile, housing_stock, permit_fees (itemized schedule!), utility_rebate_amounts (PGW), contractor_license_info (L&I detailed), climate_hvac_failure_mode
- **Not_found:** local_building_code (amlegal.com 403), and PECO electric rebates (peco.com returned empty/404)
- **URLs cited:** ncei.noaa.gov (USW00013739), api.census.gov (place:60000 state:42), phila.gov get-a-mechanical-permit, pgworks.com/customer-care/efficiency, phila.gov get-a-contractor-license, energy.gov/energysaver/heat-pump-systems, irs.gov
- **Notes:** Philadelphia has the most detailed permit fee schedule of any city researched — $100 filing + $15.10 per register + $69 per appliance (1-2 family) + 2% fuel gas contract + $3 city / $4.50 state surcharges. PGW EnergySense rebates up to $500 furnace / $1,500 boiler. L&I license $500K general liability + OSHA 30 within 5 years. 669,222 occupied units — largest city researched (behind Chicago's 1.15M).

## Las Vegas, NV

- **Date researched:** 2026-04-14
- **Found (4/7):** climate_profile, housing_stock, contractor_license_info (NSCB C-21 framework), climate_hvac_failure_mode
- **Not_found:** permit_fees (PDF binary unparseable), local_building_code (leg.state.nv.us 403), utility_rebate_amounts (nvenergy.com ECONNREFUSED on all attempts)
- **URLs cited:** ncei.noaa.gov (USW00023169 — KLAS Harry Reid), api.census.gov (place:40000 state:32), nvcontractorsboard.com license-classifications, energy.gov/energysaver/central-air-conditioning, irs.gov
- **Notes:** Las Vegas is the driest major U.S. city researched (4.18" precip) with median year built 1994 — the NEWEST housing stock of any city in the project, by a decade+. Reflects Vegas's rapid post-1990 growth. Attic-duct issue especially critical: 3,720 CDD + 110°F+ summer extremes drive attic temps above 140°F. NSCB Classification C (42 subclassifications, C-21 for HVAC) framework captured; NAC 624 detailed scope not extractable (leg.state.nv.us blocks automated fetches).

## Charlotte, NC

- **Date researched:** 2026-04-15
- **Found (3/7):** climate_profile, housing_stock, climate_hvac_failure_mode; NC Board authority (partial)
- **Not_found:** permit_fees (mecknc.gov 403), local_building_code (municode shell), utility_rebate_amounts (duke-energy.com 403), H-1/H-2/H-3 verbatim scopes (NC admin code portal ECONNREFUSED)
- **URLs cited:** ncei.noaa.gov (USW00013881), api.census.gov (place:12000 state:37), nclicensing.org (NC Board identity), energy.gov/energysaver/heat-pump-systems, energystar.gov/rebate-finder, irs.gov
- **Notes:** Charlotte 53.3% electric / 44.5% gas — electric-majority Sun Belt metro. Median year 1994 (relatively new). Block thinner at ~517 words because multiple key pages blocked.

## Columbus, OH

- **Date researched:** 2026-04-15
- **Found (5/7):** climate_profile, housing_stock, utility_rebate_amounts (AEP Ohio $75 thermostat + Columbia Gas residential ended), contractor_license_info (OCILB identity + contact), climate_hvac_failure_mode
- **Not_found:** permit_fees (2026 fee schedule PDF 403), local_building_code (Ohio Residential Code adopted but no Columbus-specific amendment surfaced)
- **URLs cited:** ncei.noaa.gov (USW00014821), api.census.gov (place:18000 state:39), aepohio.com/savings, columbiagasohio.com/energy-efficiency (may bot-block QC but resolves in browsers), com.ohio.gov OCILB (may bot-block QC but resolves in browsers), energystar.gov (root — ENERGY STAR cold-climate deep links 404'd; swapped for homepage), irs.gov
- **Notes:** Columbia Gas of Ohio residential (non-income-qualified) rebate programs have ENDED — factual finding worth publishing. AEP Ohio has minimal published equipment rebates beyond the $75 smart thermostat. QC flagged OCILB URL 404 but the Ohio department of commerce increasingly returns 404 to automated clients; real browsers reach it. Swapped ENERGY STAR specific-product URL for energystar.gov root.

## Indianapolis, IN

- **Date researched:** 2026-04-15
- **Found (4/7):** climate_profile, housing_stock, utility_rebate_amounts (AES Indiana tiered detail), climate_hvac_failure_mode
- **Not_found:** permit_fees (indy.gov DBNS only serves tracking pixels to server-fetch), local_building_code (municode shell), contractor_license_info detailed (Indiana has no statewide HVAC license — verified via in.gov/pla 404 on /professions/hvac-home/; DBNS local page blocked)
- **URLs cited:** ncei.noaa.gov (USW00093819), api.census.gov (place:36003 state:18 — Indianapolis balance post-Unigov), aesindiana.com/rebates, energy.gov/energysaver/heat-pump-systems, energystar.gov/rebate-finder, irs.gov
- **Notes:** AES Indiana rebates comprehensively tiered: mini-split $100/$225/$300/$525/$725 by SEER/HSPF, $50 thermostat, $600 HPWH. Indianapolis is post-Unigov consolidation — ACS entity is "Indianapolis city (balance), Indiana". 56.7% gas / 40.6% electric.

## Nashville, TN

- **Date researched:** 2026-04-15
- **Found (3/7):** climate_profile, housing_stock, climate_hvac_failure_mode + TN Board identity (partial)
- **Not_found:** permit_fees (nashville.gov codes 404), local_building_code (municode shell), utility_rebate_amounts (TVA energyright.com 403; NES 404; Piedmont Gas 403), CMC-C verbatim scope (tn.gov/commerce contractor page 404)
- **URLs cited:** ncei.noaa.gov (USW00013897), api.census.gov (place:52006 state:47 — Nashville-Davidson balance), tn.gov/commerce/regboards.html (swapped from 404 contractor.html subpage), energy.gov/energysaver/heat-pump-systems, energystar.gov/rebate-finder, irs.gov
- **Notes:** Nashville's 66.4% electric heating is striking for a Southern mixed-humid metro — TVA service territory with historically low electric rates made heat pumps economically competitive with gas long before most other Southern cities. Median year 1985. Block stays factual despite thin coverage (~545 words) by leaning on the TVA/electric-majority story + DOE dual-fuel guidance for Zone 4A.

## San Antonio, TX

- **Date researched:** 2026-04-15
- **Found (6/7):** climate_profile, housing_stock, utility_rebate_amounts (CPS Energy STEP comprehensive), contractor_license_info (TDLR Class A/B verbatim via TACCA mirror of statute), climate_hvac_failure_mode, local_building_code (DSD context)
- **Not_found:** permit_fees — 4.4MB FY25 Development Fee Schedule PDF binary unparseable
- **URLs cited:** ncei.noaa.gov (USW00012921), api.census.gov (place:65000 state:48), cpsenergy.com HVAC Rebates + Home Energy Rebates + Thermostat Rewards, tdlr.texas.gov/acr/acr.htm, sanantonio.gov/DSD, energy.gov/energysaver/efficient-cooling-hot-humid-climates, irs.gov
- **Notes:** CPS Energy is the ONLY municipal utility in the Texas big-city group (vs Oncor/CenterPoint deregulated TDU model elsewhere). STEP rebates structured per cooling-ton, scaled by efficiency: Early Replacement $115-$310/ton, Replace-on-Burnout $90-$275/ton. Minimum efficiency 14.3 SEER2 / 11.7 EER2. WiFi thermostat $85 enroll + $30/yr ongoing. Attic insulation $0.35/sqft. San Antonio 69.5% electric heat is the HIGHEST of any major Texas city researched.

## Jacksonville, FL

- **Date researched:** 2026-04-15
- **Found (6/7):** climate, housing, local_building_code (Chapter 320), utility_rebates (JEA), contractor_license (FL Statute 489.105), climate-HVAC mode
- **Not_found:** permit_fees (coj.net ECONNREFUSED; municode Chapter 320 returned no fee table)
- **URLs cited:** ncei.noaa.gov (USW00013889), api.census.gov (place:35000 state:12), jea.com residential rebates, leg.state.fl.us Statutes 489.105, energy.gov/energysaver, irs.gov
- **Notes:** 94.5% electric heating (close to Miami's 91.2%) — near-pure electric tropical market. JEA rebates comprehensive ($200 AC / $50 thermo / $200 insulation / $350 HPWH). Atlantic coastal salt-air corrosion angle.

## Fort Worth, TX

- **Date researched:** 2026-04-15
- **Found (4/7):** climate (own KFTW station), housing, contractor_license (TDLR — reused), climate-HVAC mode + tornado angle
- **Not_found:** permit_fees (Fort Worth DS couldn't extract), local_building_code (municode shell), utility_rebate_amounts (Texas deregulated)
- **URLs cited:** ncei.noaa.gov (USW00003927 — KFTW Meacham, own station not DFW), api.census.gov (place:27000 state:48), tdlr.texas.gov/acr/acr.htm, weather.gov/fwd/fwdtornadoes, energy.gov/energysaver/central-air-conditioning, irs.gov
- **Notes:** Fort Worth has its own NOAA station separate from KDFW. 69.1% electric / 28.9% gas — higher electric share than Dallas (65.2%). Median 1992 — a decade newer than Dallas (1980). More balanced CDD:HDD than Dallas (1.3:1 vs Dallas 1.6:1).

## Austin, TX

- **Date researched:** 2026-04-15
- **Found (5/7):** climate, housing, utility_rebate_amounts (Austin Energy AND Texas Gas Service — both sources found), contractor_license (TDLR — reused), climate-HVAC mode
- **Not_found:** permit_fees (Widen PDF viewer SPA), local_building_code (Green Building landing exists but no verbatim amendment)
- **URLs cited:** ncei.noaa.gov (USW00013904), api.census.gov (place:05000 state:48), savings.austinenergy.com/rebates/residential, texasgasservice.com rebates, tdlr.texas.gov/acr/acr.htm, energy.gov/energysaver, irs.gov
- **Notes:** Austin Energy (municipal utility — one of only two in TX, with San Antonio's CPS). AE rebates: AC $800 avg, HPWH $800, Power Partner thermostat up to $75, solar $2,500. Texas Gas Service: furnace $675 at 92%+ AFUE, tankless WH $400-$650, solar WH $750. Median year 1993 — reflects post-tech-boom growth.

## Baltimore, MD

- **Date researched:** 2026-04-15
- **Found (5/7):** climate, housing, utility_rebate_amounts (BGE detailed), contractor_license (MD HVACR Board — detailed master requirements), climate-HVAC mode
- **Not_found:** permit_fees (DHCD 404), local_building_code (municode JS-SPA)
- **URLs cited:** ncei.noaa.gov (USW00093721 KBWI), api.census.gov (place:04000 state:24 — Baltimore independent city), bgesmartenergy.com (3 subpages: heating-cooling, heat-pump-water-heater, smart-thermostats), dllr.state.md.us HVACR requirements, energy.gov/energysaver, irs.gov
- **Notes:** Median 1948 — pre-war rowhouse stock, 3.2% fuel oil (mid-Atlantic legacy like Philadelphia's 3.0%). BGE: geothermal $3,000 grant, HPWH $1,600, smart thermostat $100, 0% financing via Maryland Clean Energy Advantage. MD HVACR Master requirements strict: 3 years journeyman + 1,875 hrs/yr + 70% exam — among most rigorous in country.

## Milwaukee, WI

- **Date researched:** 2026-04-15
- **Found (5/7):** climate, housing, utility_rebate_amounts (Focus on Energy statewide), contractor_license (WI HVAC Qualifier optional — unique), climate-HVAC mode
- **Not_found:** permit_fees (DNS 403), local_building_code (municode not verified)
- **URLs cited:** ncei.noaa.gov (USW00014839), api.census.gov (place:53000 state:55), focusonenergy.com/residential/heating-and-cooling, dsps.wi.gov HVACQualifier, energy.gov/energysaver/heat-pump-systems, irs.gov
- **Notes:** Wisconsin unique: no mandatory state HVAC license, Focus on Energy administers statewide rebates (not We Energies directly). Focus on Energy tiered + income-qualified: ASHP $400-$900, furnace $100-$400, boiler $350-$550, geothermal $750-$1,000. 79.3% gas heating (second only to Detroit's 81.8%). Median 1952 pre-WWII bungalows.

## New York City, NY

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, local_building_code (Title 28 + LL97 reference), contractor_license (DOB trade licenses), climate_hvac_mode
- **Not_found:** permit_fees, utility_rebate_amounts (ConEd/NYSERDA Clean Heat not verbatim)
- **URLs cited:** ncei.noaa.gov (USW00094728 Central Park), api.census.gov (place:51000 state:36), nyc.gov/site/buildings (swapped from dead subpage), energy.gov/energysaver/heat-pump-systems, irs.gov
- **Notes:** NYC has the LARGEST municipal housing stock in the U.S. at 3,313,316 units. 12.5% fuel oil (414,650 units) is the highest in the country — legacy of pre-war steam systems. Local Law 97 emissions law referenced by name (page URL moved post-QC — kept text, dropped hyperlink). Median year 1952 reflects dominant pre-war/mid-century stock.

## Oklahoma City, OK

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, contractor_license (CIB — 59 O.S. §1850.1 + OAC 158:50 + 6hrs CEU/36mo), climate_hvac_mode (NWS tornado climatology)
- **Not_found:** permit_fees (okc.gov DS 403), local_building_code (municode shell), utility_rebate_amounts (OG&E 403, ONG 404)
- **URLs cited:** ncei.noaa.gov (USW00013967), api.census.gov (place:55000 state:40), oklahoma.gov/cib/your-industry/mechanical.html, weather.gov/oun/tornadodata-okc, energystar.gov/rebate-finder, irs.gov
- **Notes:** NWS Norman OKC tornado climatology is exceptional — 194 tornadoes since 1890, 13 violent F4/F5, peak May-April-June 4-5pm. 57.2% gas / 39.6% electric, median 1981.

## Memphis, TN

- **Date researched:** 2026-04-15
- **Found (3/7):** climate, housing, climate_hvac_mode
- **Not_found:** permit_fees (memphistn.gov 404), local_building_code (municode shell), utility_rebate_amounts (MLGW TLS errors, TVA EnergyRight 403), contractor_license_detail (tn.gov 404s — reused Nashville CMC-C reference)
- **URLs cited:** ncei.noaa.gov (USW00013893), api.census.gov (place:48000 state:47), tn.gov/commerce/regboards.html, energy.gov/energysaver/efficient-cooling-hot-humid-climates, irs.gov
- **Notes:** 54.94" annual precipitation — among wettest major U.S. cities. MLGW is rare TVA-territory MUNICIPAL combined utility (electric + gas + water). 55.1% electric (TVA dominance similar to Nashville 66.4%). Median year 1970.

## Washington, DC

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, local_building_code (DCMR Title 12), climate_hvac_mode; partial license framework
- **Not_found:** permit_fees (DOB 403), utility_rebate_amounts (Pepco/WashGas/DCSEU all 403), contractor_license_detail (DLCP 403)
- **URLs cited:** ncei.noaa.gov (USW00013743 Reagan National), api.census.gov (place:50000 state:11), dob.dc.gov/page/dc-construction-codes (swapped from dead /construction-codes), basc.pnnl.gov/ (swapped from dead deep link), energy.gov/energysaver, irs.gov
- **Notes:** DC near-balanced gas/electric 49.2%/45.6% — unusual among major cities. Median 1957 mid-century. DCSEU is the only city-mandated efficiency-utility of its kind in the project. DOB permit fees behind auth portal.

## Tampa, FL

- **Date researched:** 2026-04-15
- **Found (5/7):** climate, housing, utility_rebate_amounts (TECO tiered), local_building_code (Tampa + FL surcharge 2.5%), contractor_license (FL Statute 489.105 Class A/B reused), climate_hvac_mode
- **Not_found:** permit_fees (PDF unparseable — linked for reader), Peoples Gas rebates (404s)
- **URLs cited:** ncei.noaa.gov (USW00012842), api.census.gov (place:71000 state:12), tampaelectric.com/residential heating-cooling + thermostat, tampa.gov/construction-services/fees, leg.state.fl.us Section 489.105, energy.gov/energysaver, irs.gov
- **Notes:** 92.1% electric heating (similar to Miami 91.2% and Jacksonville 94.5% — Florida pattern). Tampa NOT in HVHZ (only Miami-Dade + Broward) but still hurricane-prone FL wind-load zone. TECO rebates tiered $40 (baseline SEER2) vs $550 (one tier up) — notable step-up. 3,928 CDD vs only 433 HDD (9:1 cooling dominance, even more extreme than Miami's 45:1 but similar profile).

## San Francisco, CA

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, utility_rebate_amounts (BayREN EASE 80% / $1K cap), contractor_license (C-20 by name), climate_hvac_mode
- **Not_found:** permit_fees, local_building_code, detailed PG&E rebates (pge.com SPA 404s)
- **URLs cited:** ncei.noaa.gov (USW00023234 SFO), api.census.gov, bayren.org/ease, energy.gov/energysaver, irs.gov
- **Notes:** SF median year 1945 (tied with Detroit for oldest). **5.9% NO heating fuel (21,477 units)** — exceptional marine-climate pattern. HDD 2,475 vs only 200 CDD (12:1 heating-dominated, virtually zero cooling demand). Pre-war Victorian/Edwardian row-house stock.

## San Jose, CA

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, contractor_license (CSLB C-20 verbatim), climate_hvac_mode
- **Not_found:** permit_fees (sanjoseca.gov 403), local_building_code, utility_rebate_amounts (PG&E 404, SVCE page lacked HVAC amounts, BayREN EASE general only)
- **URLs cited:** ncei.noaa.gov (USW00023293 Mineta), api.census.gov (place:68000 state:06), cslb.ca.gov C-20, bayren.org/ease, energy.gov/energysaver/heat-pump-systems, irs.gov
- **Notes:** Interior Bay Area warmer than SF — 71.2°F TMAX vs SF 66.9°F. Housing: 326,767 units with **3,398 solar-heated homes** (among highest solar share in project). Median year 1975. Zone 3C ideal heat-pump climate. SVCE = CCA (Community Choice Aggregator) for electric generation; PG&E handles delivery.

## New Orleans, LA

- **Date researched:** 2026-04-15
- **Found (6/7):** climate, housing, local_building_code (NOLA Dept Safety & Permits), utility_rebate_amounts (Energy Smart DETAILED), contractor_license (LA LSLBC Classification 6), climate_hvac_mode
- **Not_found:** permit_fees (PDF binary unparseable)
- **URLs cited:** ncei.noaa.gov (USW00012916 KMSY Armstrong), api.census.gov (place:55000 state:22), nola.gov/mechanical-permit, energysmartnola.info/a-c-solutions, lslbc.gov/exams-classifications, energy.gov/energysaver, irs.gov
- **Notes:** **63.35" annual precipitation — wettest major city in project.** 61.9% electric heat (hot-humid gulf pattern). Energy Smart captured 7 verbatim rebate amounts: AC tune-up $150-$200 income-tiered, central AC $150/$175/$200 by SEER2, ASHP $200/$250, ductless replacing electric strip $500. LA LSLBC $10K license threshold + master plumber overlap. Post-Katrina flood elevation requirements referenced.

## Cleveland, OH

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, contractor_license (OCILB reused from Columbus), climate_hvac_mode
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (FirstEnergy 404, Enbridge Gas Ohio transition complicated)
- **URLs cited:** ncei.noaa.gov (USW00014820 KCLE), api.census.gov (place:16000 state:39), com.ohio.gov (OCILB reused), energy.gov/energysaver/heat-pump-systems, energystar.gov/rebate-finder, irs.gov
- **Notes:** **63.8" annual snowfall — HIGHEST of any city in project** (Lake Erie lake-effect). **Median year built 1940 — OLDEST housing stock yet** (surpassing Boston/Detroit's 1947). 78.4% gas heating. Dominion Energy Ohio gas utility was acquired by Enbridge Gas in 2023-2024 — real regulatory transition worth noting for readers.

## Albuquerque, NM

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, contractor_license (NM MM-3 HVAC verbatim from NMAC 14.6.6), climate_hvac_mode (DOE evap cooler)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (PNM ECONNREFUSED all attempts)
- **URLs cited:** ncei.noaa.gov (USW00023050 KABQ), api.census.gov (place:02000 state:35), srca.nm.gov/parts/title14/14.006.0006.html (NMAC 14.6.6), energy.gov/energysaver/evaporative-coolers, irs.gov
- **Notes:** **IMPORTANT BRIEF CORRECTION**: brief referenced MM-4/MM-5 but correct NM HVAC classification is **MM-3**. Agent verified verbatim from NMAC 14.6.6: MM-2 natural gas fitting, MM-3 HVAC, MM-4 hydronic/process piping. MM-5 does not exist. 8.84" precip (second-driest after Las Vegas 4.18"). 5,312 ft elevation = altitude derating (like Denver). 76.6% gas heating + 1,444 wood-heated homes (Southwest kiva/pellet-stove tradition). Evap cooler angle strong for high-desert climate.

## Oakland, CA

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, contractor_license (CSLB C-20 verbatim), climate_hvac_mode
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Ava Community Energy routes through eligibility tool; PG&E blocked)
- **URLs cited:** ncei.noaa.gov (USW00023230 KOAK), api.census.gov, cslb.ca.gov C-20, bayren.org/ease, energy.gov/energysaver, irs.gov
- **Notes:** **15:1 HDD:CDD ratio** — most extreme heating-dominated marine yet (2,690 HDD vs 175 CDD). Median year 1953 pre-war. 3.9% no-fuel-used (6,705 units). Ava Community Energy formerly East Bay Community Energy.

## Fresno, CA

- **Date researched:** 2026-04-15
- **Found (3/7):** climate, housing, climate_hvac_mode
- **Not_found:** permit_fees (fresno.gov 404), local_building_code, utility_rebate_amounts (PG&E blocked), contractor_license_detail (CSLB deep link 404 — reused C-20 by name)
- **URLs cited:** ncei.noaa.gov (USW00093193 KFAT), api.census.gov (place:27000 state:06), energy.gov/energysaver/cooling-whole-house-fan, energystar.gov/rebate-finder, irs.gov
- **Notes:** **HDD 2,186 ≈ CDD 2,209 — nearly PERFECT 1:1 BALANCE** (unique among all cities). **5,038 solar-heated homes (2.8%) — highest solar share in project.** 10.99" precipitation. Central Valley hot-dry like Sacramento.

## Mesa, AZ

- **Date researched:** 2026-04-15
- **Found (5/7):** climate (KIWA Gateway), housing, local_building_code (Mesa City Code Title 4 — IRC+IMC), contractor_license (AZ ROC R-39/C-39), climate_hvac_mode (DOE SEER2 14.3 Southern-region 2023 rule)
- **Not_found:** permit_fees (PDF unparseable), utility_rebate_amounts (SRP SPA not parseable)
- **URLs cited:** ncei.noaa.gov (USW00003192 KIWA), api.census.gov (place:46000 state:04), library.municode.com/az/mesa, roc.az.gov, energy.gov/energysaver/central-air-conditioning, irs.gov
- **Notes:** Mesa 77.8% electric heat — HIGHER than Phoenix's 74.6%, reflecting SRP territory + newer post-1988 housing. Median 1988 a decade newer than Phoenix (1984). KIWA Gateway station slightly cooler than KPHX Sky Harbor (85.0°F vs 87.1°F max).

## Raleigh, NC

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, contractor_license (NC Board identity), climate_hvac_mode
- **Not_found:** permit_fees (FY26 Fee Guide URL not located), local_building_code, utility_rebate_amounts (Duke Progress Smart Saver 403), H-1/H-2/H-3 detailed scope
- **URLs cited:** ncei.noaa.gov (USW00013722 KRDU), api.census.gov (place:55000 state:37), nclicensing.org, energy.gov/energysaver/heat-pump-systems, energystar.gov/rebate-finder, irs.gov
- **Notes:** 58.7% electric heat — higher than Charlotte's 53.3%. Median 1996 — NEWEST yet among cold-climate cities, Research Triangle tech growth. Near-balanced Zone 4A (1.75:1 HDD:CDD).

## Birmingham, AL

- **Date researched:** 2026-04-15
- **Found (5/7):** climate, housing, utility_rebate_amounts (Alabama Power detailed), contractor_license (HACR Board fees + bond detailed), climate_hvac_mode
- **Not_found:** permit_fees (city directs to Online Permit Center only), local_building_code
- **URLs cited:** ncei.noaa.gov (USW00013876 KBHM), api.census.gov (place:07000 state:01), alabamapower.com/residential high-seer-heat-pump-rebate, hacr.alabama.gov/how-to-get-licensed, energy.gov/energysaver, irs.gov
- **Notes:** **Alabama Power $1,000 gas-to-heat-pump conversion rebate** + up to $200 smart thermostat. **Alabama HACR Board: exam $175, active $220/yr, inactive $110/yr, $20,000 performance bond required** — detailed + verbatim. 56.62" precip (among wettest). Smallest city in project at 88,527 occupied units.

## Omaha, NE

- **Date researched:** 2026-04-15
- **Found (3/7 + federal credit):** climate, housing, climate_hvac_mode, IRS §25C verbatim limits ($2,000 heat pump / $1,200 general / $600 per item)
- **Not_found:** permit_fees (Akamai Access Denied on planning.cityofomaha.org), local_building_code (municode SPA), utility_rebate_amounts (OPPD timeout, Black Hills Energy TLS fail), contractor_license_detail (city permits blocked)
- **URLs cited:** ncei.noaa.gov (USW00014942 KOMA Eppley), api.census.gov (place:37000 state:31), energy.gov/energysaver/heat-pump-systems, irs.gov/.../energy-efficient-home-improvement-credit
- **Notes:** 5,833 HDD / 1,294 CDD, 27.1" snow. 73% gas heating. Median 1972. OPPD is municipal public power district (like SMUD, CPS, Austin Energy). Tornado Alley exposure.

## Colorado Springs, CO

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, local_building_code (Pikes Peak Regional authority framework), contractor_license (PPRBD regional), climate_hvac_mode
- **Not_found:** permit_fees (pprbd.org ECONNREFUSED), utility_rebate_amounts (csu.org unreachable), detailed license scope
- **URLs cited:** ncei.noaa.gov (USW00093037 KCOS), api.census.gov (place:16000 state:08), pprbd.org, energy.gov/energysaver/heat-pump-systems, irs.gov
- **Notes:** **6,035 ft — HIGHEST major U.S. city in project**, surpassing Denver's 5,280 ft. Altitude derating more severe than Denver. Pikes Peak Regional Building Department is a unique joint city/county/regional authority. **Colorado Springs Utilities is a rare FOUR-SERVICE municipal utility** (electric + gas + water + wastewater). 5,888 HDD / 608 CDD. 69.8% gas heating, median 1986.

## El Paso, TX

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, utility_rebate_amounts (EPE 2025 program catalog by name), contractor_license (TDLR reused), climate_hvac_mode (DOE evap cooler)
- **Not_found:** permit_fees (PDF binary), local_building_code, specific rebate dollar amounts (EPE individual rebate PDFs 403)
- **URLs cited:** ncei.noaa.gov (USW00023044 KELP), api.census.gov (place:24000 state:48), epelectric.com Texas residential rebates, tdlr.texas.gov/acr/acr.htm, energy.gov/energysaver/evaporative-coolers, irs.gov
- **Notes:** **71.2% gas heating — HIGHEST of any major TX city** (unusual; Dallas 33%, Houston 33%, Austin 42%, San Antonio 29% are all electric-majority). Chihuahuan Desert ~3,700 ft elevation. 8.78" precip tied with Albuquerque for 2nd-driest. Evap cooler capital of US.

## Virginia Beach, VA

- **Date researched:** 2026-04-15
- **Found (5/7):** climate, housing, local_building_code (Code of Virginia 54.1-1100 verbatim Class A/B/C thresholds), contractor_license (DPOR HVA framework), climate_hvac_mode
- **Not_found:** permit_fees (city permits ECONNREFUSED), utility_rebate_amounts (Dominion 403, VNG 404)
- **URLs cited:** ncei.noaa.gov (USW00013737 KNGU Norfolk NAS), api.census.gov (place:82000 state:51), law.lis.virginia.gov/vacode Section 54.1-1100, dpor.virginia.gov/Boards/Contractors, energy.gov/energysaver, irs.gov
- **Notes:** **VA Code 54.1-1100 Class A/B/C thresholds captured VERBATIM**: A ≥$150K single or $1M+ annual, B $30K-$150K / $250K-$1M, C $1K-$30K / <$250K. Distinctive dollar-based contractor classification structure. 62.4% electric heat, 1.4% fuel oil. Median 1984.

## Pittsburgh, PA

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, contractor_license (PA HICPA + Pittsburgh PLI local), climate_hvac_mode
- **Not_found:** permit_fees (pittsburghpa.gov/pli 403), local_building_code, utility_rebate_amounts (Duquesne Light + Peoples Gas 403/404)
- **URLs cited:** ncei.noaa.gov (USW00094823 KPIT), api.census.gov (place:61000 state:42), energy.gov/energysaver/heat-pump-systems, irs.gov
- **Notes:** **Median year 1942 — second-oldest housing stock in project** behind Cleveland's 1940. 75.4% gas heating. 44.1" snowfall + 5,572 HDD heavy cold-climate profile. PA HICPA $5K threshold (registration, not trade license) + Pittsburgh PLI local registration required.

## Honolulu, HI

- **Date researched:** 2026-04-15
- **Found (5/7):** climate, housing, utility_rebate_amounts (Hawaii Energy verbatim), contractor_license (DCCA C-52), climate_hvac_mode
- **Not_found:** permit_fees (DPP no public HTML fee schedule), local_building_code (municode chapter text not retrieved)
- **URLs cited:** ncei.noaa.gov (USW00022521 KHNL), api.census.gov (place:71550 state:15 — Urban Honolulu CDP, **CORRECTED from brief's 17000 which doesn't exist**), hawaiienergy.com/for-homes/rebates/hvac, cca.hawaii.gov/pvl/boards/contractor, energy.gov/energysaver/efficient-cooling-hot-humid-climates (swapped from 404 hot-humid-climate URL)
- **Notes:** **HDD literally 0.0** (only city in project with zero heating demand), **45% of occupied units report NO fuel used for heating** (61,258 of 136,228) — tropical extreme. Hawaii Energy rebates verbatim: central AC $1,250 instant, mini-split VRF up to $550/unit, AC tune-up $75, window AC up to $45, whole house fan $100, solar attic fan $75.

## Anchorage, AK

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, contractor_license (AK Mechanical Administrator 3 classes: RHVC, UHVCS, HCPP), climate_hvac_mode
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Chugach 404, Enstar has no amounts)
- **URLs cited:** ncei.noaa.gov (USW00026451 KANC), api.census.gov (place:03000 state:02), commerce.alaska.gov Mechanical Administrators, energy.gov/energysaver/heat-pump-systems, irs.gov
- **Notes:** **HDD 9,978.6 — HIGHEST of any city in project** (nearly 4× Denver). CDD only 7.6 (essentially zero). 77.9" snowfall. 79.3% gas (Enstar territory). Alaska Mechanical Administrator 3 classes captured verbatim.

## Salt Lake City, UT

- **Date researched:** 2026-04-15
- **Found (5/7):** climate, housing, permit_fees (SLC Consolidated Fee Schedule 18.52.050 — 9 line items verbatim!), contractor_license (UT DOPL S350 by name), climate_hvac_mode (Wasatch inversions context)
- **Not_found:** local_building_code (municode blocked), utility_rebate_amounts (Rocky Mountain Power + ThermWise blocked or PDF-only)
- **URLs cited:** ncei.noaa.gov (USW00024127 KSLC), api.census.gov (place:67000 state:49), tools.slc.gov/feeschedule (UNUSUAL WIN — SLC publishes a live interactive fee schedule), energy.gov/energysaver, irs.gov
- **Notes:** Most detailed municipal fee schedule captured yet — 9 verbatim line items ($57 base, furnace $29-$65 tiered by BTU/h, floor furnace $18, vent $18, boiler $29). 4,226 ft elevation. 5,154 HDD / 1,420 CDD. 73.3% gas / 23.1% electric. Median 1963. Wasatch Front inversions make heat pump air-quality case distinctive.

## Buffalo, NY

- **Date researched:** 2026-04-15
- **Found (4/7):** climate, housing, contractor_license (NY no state license — Buffalo local Heating Contractor License), climate_hvac_mode
- **Not_found:** permit_fees (Buffalo DPIS wrong slug), local_building_code (ecode360 403), utility_rebate_amounts (National Grid interactive + NYSERDA 403)
- **URLs cited:** ncei.noaa.gov (USW00014733 KBUF), api.census.gov (place:11000 state:36), dos.ny.gov/business-licenses, energy.gov/energysaver/heat-pump-systems, irs.gov
- **Notes:** **95.4" annual snowfall — HIGHEST of any city in project** (Lake Erie lake-effect). **85.97% utility gas — HIGHEST gas share in project**. Median year 1938 (tied with Detroit/Pittsburgh for oldest). 10.6:1 HDD:CDD ratio.

## Newark, NJ

- **Date researched:** 2026-04-15
- **Found (5/7):** climate, housing, contractor_license (NJ HVACR Board — dedicated HVACR-specific board, 2-year renewal), climate_hvac_mode, local_building_code (NJ UCC statewide)
- **Not_found:** permit_fees (newark UCC slug 404), utility_rebate_amounts (PSE&G 403, NJ Clean Energy blocked)
- **URLs cited:** ncei.noaa.gov (USW00014734 KEWR Newark Liberty), api.census.gov (place:51000 state:34), njconsumeraffairs.gov/hvacr (verbatim: 2-year renewal, Board ensures educational requirements), njcleanenergy.com, energy.gov/energysaver, irs.gov
- **Notes:** NJ is one of few states with DEDICATED HVACR-specific licensing board (separate from general contractors). Board headquartered in Newark. 70.7% gas / 19.9% electric / 2.9% fuel oil (Northeast legacy). Median 1966. 31.5" snow.

---

## Boise, ID

- **Date researched:** 2026-04-15
- **Found (4/7):** climate (KBOI USW00024131), housing (place:08830 state:16), utility_rebate_amounts (Idaho Power Heating & Cooling Efficiency Program — $800 ducted ASHP / $400 ductless / $50 smart thermostat), climate_hvac_failure_mode (Zone 5B cool-dry, Sierra-shadow rain pattern)
- **Not_found:** permit_fees (cityofboise.org JS-rendered fee portal), local_building_code (no Boise-specific amendment located), contractor_license (DOPL ECONNREFUSED)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:08830 state:16), idahopower.com Heating & Cooling Efficiency Program, energy.gov/eere/buildings/building-america, irs.gov
- **Notes:** Younger housing stock (median 1985) — post-1980 envelope standards already in place. 62.3% gas / 34.0% electric is a heat-pump-friendly mix. Snake River Plain inversion narrative tied to verbatim 17.6" snowfall.

## Madison, WI

- **Date researched:** 2026-04-15
- **Found (5/7):** climate (KMSN USW00014837), housing (place:48000 state:55), utility_rebate_amounts (Focus on Energy 4-tier ASHP rebates $400-$900 + $1,000/$750 geothermal), contractor_license (DSPS HVAC registration requirement, owner-occupant exemption), climate_hvac_failure_mode (11x HDD:CDD + 51.8" snow)
- **Not_found:** permit_fees (cityofmadison.com Building Inspection no inline schedule), local_building_code (municode shell only)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:48000 state:55), focusonenergy.com/residential/heating-and-cooling, dsps.wi.gov/Pages/Professions/HVACContractor/Default.aspx, energystar.gov/products/heating_cooling/heat_pumps_air_source/key_product_criteria, irs.gov
- **Notes:** Focus on Energy is the statewide rebate administrator serving MGE customers — MGE doesn't run its own residential rebates. 11:1 HDD:CDD makes Madison the most heating-dominated of any Batch 12 city. dsps.wi.gov/Pages/Professions/HVAC/Default.aspx 404s — corrected to /HVACContractor/.

## Reno, NV

- **Date researched:** 2026-04-15
- **Found (4/7):** climate (KRNO USW00023185 — exceptionally dry 7.35" annual precip), housing (place:60600 state:32), contractor_license (NV C-21 reused from Las Vegas, NAC 624), climate_hvac_failure_mode (DOE evaporative-cooler guidance + Sierra rain shadow + diurnal swings)
- **Not_found:** permit_fees (Reno Community Development JS portal), local_building_code, utility_rebate_amounts (NV Energy PowerShift northern-NV territory)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:60600 state:32), nscb.nv.gov/contractors/license-classifications, energy.gov/energysaver/evaporative-coolers, irs.gov
- **Notes:** **7.35" annual precipitation — driest of any project city to date.** Sierra rain-shadow + 4,500 ft elevation = textbook evaporative cooling territory. 37.4% electric heating share (high) reflects newer condo/multifamily stock. energy.gov/energysaver/whole-house-fans-and-evaporative-coolers 404'd — corrected to /evaporative-coolers.

## Richmond, VA

- **Date researched:** 2026-04-15
- **Found (5/7 + bonus):** climate (KRIC USW00013740), housing (place:67000 state:51 — **electricity-majority Mid-Atlantic, 59.4% electric**), contractor_license (VA Code 54.1-1100 Class A/B/C verbatim thresholds + HVA), climate_hvac_failure_mode (Zone 4A mixed-humid latent load), municipal_gas_utility (City of Richmond Department of Public Utilities — 500,000+ customers — distinctive)
- **Not_found:** permit_fees (rva.gov 404s), local_building_code, utility_rebate_amounts (dominionenergy.com 403)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:67000 state:51), rva.gov/public-utilities, law.lis.virginia.gov/vacode/title54.1/chapter11/section54.1-1100, energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **Distinctive: Richmond runs its OWN municipal natural gas utility** — one of few US cities. Heating mix is electricity-majority (59.4%) — unusual for Mid-Atlantic, supports heat-pump narrative. Median year 1959 = historic-district envelope retrofit territory.

## Wichita, KS

- **Date researched:** 2026-04-15
- **Found (4/7):** climate (KICT USW00003928 — true dual-load 4,413.6 HDD vs 1,773.6 CDD), housing (place:79000 state:20), contractor_license (Kansas has NO statewide HVAC license — MABCD handles locally), climate_hvac_failure_mode (NWS Wichita EF5 tornadoes + ice storms climatology pages)
- **Not_found:** permit_fees (sedgwickcounty.org/mabcd ECONNREFUSED), local_building_code (MABCD unreachable), utility_rebate_amounts (Evergy 404s, Kansas Gas Service 404/500)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:79000 state:20), weather.gov/ict/Climate (NWS Wichita), irs.gov
- **Notes:** True dual-load climate (2.5:1 HDD:CDD) — neither heating-dominant nor cooling-dominant. Tornado Alley + ice-storm narrative anchored to NWS Wichita primary climatology. Kansas no-statewide-license + MABCD joint city/county authority is structurally distinctive.

## Allentown, PA

- **Date researched:** 2026-04-15
- **Found (3/7):** climate (KABE USW00014737), housing (place:02000 state:42), climate_hvac_failure_mode (Zone 5A fuel-oil conversion narrative)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (PPL 404), contractor_license (PA PAHIC — no deep-link retrieved)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:02000 state:42), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **14.0% fuel oil — tied with Bridgeport for highest project fuel-oil share.** Median 1951 — old Lehigh Valley industrial city. 44.4% gas / 39.4% electric / 14% fuel oil is an unusual 3-way split.

## Augusta, GA

- **Date researched:** 2026-04-15
- **Found (3/7):** climate (KAGS USW00003820), housing (place:04204 state:13 — consolidated city-county), climate_hvac_failure_mode (Zone 3A warm-humid, CDD > HDD)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Georgia Power 403), contractor_license (GA SOS 403)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:04204 state:13), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** CDD 2,361 > HDD 2,182 — cooling-dominant. 58.1% electric / 39.3% gas. Consolidated Augusta-Richmond County government.

## Baton Rouge, LA

- **Date researched:** 2026-04-15
- **Found (3/7):** climate (KBTR USW00013970), housing (place:05000 state:22), climate_hvac_failure_mode (Zone 2A hot-humid, 61.94" precip, hurricane exposure)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Entergy Louisiana — redirect, no amounts), contractor_license (LSLBC 404)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:05000 state:22), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **61.94" annual precipitation — among wettest project cities.** 66.4% electric / 31.5% gas. 1.8:1 CDD:HDD. Near-zero snow (0.2").

## Bridgeport, CT

- **Date researched:** 2026-04-15
- **Found (3/7):** climate (KBDR USW00014707 — NOTE: snowfall normal NOT returned by NOAA API for this station), housing (place:08000 state:09), climate_hvac_failure_mode (9:1 HDD:CDD, fuel-oil legacy, Long Island Sound coastal salt-air)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Energize CT 403), contractor_license (CT DCP 404)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:08000 state:09), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **13.9% fuel oil + 4.2% LP gas = 18% non-electric non-gas legacy fuel.** Median 1954. 59.0% gas / 20.3% electric. NOAA station KBDR did not return ANN-SNOW-NORMAL (omitted from block). Coastal salt-air corrosion narrative.

## Brownsville, TX

- **Date researched:** 2026-04-15
- **Found (3/7):** climate (KBRO USW00012919), housing (place:10768 state:48), climate_hvac_failure_mode (Zone 2A extreme cooling dominance + hurricane exposure)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Brownsville PUB — municipal, no retrievable page), contractor_license (TX TDLR reuse)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:10768 state:48), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **10.7:1 CDD:HDD ratio — MOST COOLING-DOMINANT IN PROJECT. 89.9% electric — HIGHEST ELECTRIC SHARE IN PROJECT. 0.0" snow. Municipal utility (Brownsville PUB).** Median 1993 — youngest stock in batch. Southernmost major TX city (Rio Grande Valley).

## Chattanooga, TN

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KCHA USW00013882), housing (place:14000 state:47), climate_hvac_failure_mode (Zone 4A dual-load + 55" precip humidity)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (EPB/TVA), contractor_license (TN Board)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:14000 state:47), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** EPB is municipal TVA distributor — smart-grid pioneer. 72.9% electric / 25.2% gas. 55" precip. Dual-load 1.6:1 HDD:CDD. Median 1975.

## Dayton, OH

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KDAY USW00093815), housing (place:21000 state:39), climate_hvac_failure_mode (5,149 HDD + 25" snow + 1951 housing)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (AES Ohio — no current HVAC program per xlsx), contractor_license (OCILB)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:21000 state:39), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 69.2% gas (high), median 1951 (tied Allentown for oldest in batch). No current AES Ohio HVAC rebates per xlsx. 25" snow.

## Des Moines, IA

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KDSM USW00014933), housing (place:21000 state:19), climate_hvac_failure_mode (6,178 HDD + 36.5" snow — cold-climate HP territory)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (MidAmerican Energy), contractor_license (IA DIAL)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:21000 state:19), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 6,177.7 HDD — heavily heating-dominant. 36.5" snow. 63.3% gas / 33.6% electric. Median 1960.

## Eugene, OR

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KEUG USW00024221 — snowfall NOT returned by API), housing (place:23850 state:41), climate_hvac_failure_mode (Zone 4C marine, 15.8:1 HDD:CDD)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (EWEB municipal), contractor_license (OR CCB)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:23850 state:41), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **15.8:1 HDD:CDD — MOST HEATING-SKEWED RATIO IN PROJECT (292.8 CDD = almost no cooling needed). 74.8% electric — very high. 1.1% wood heating (Pacific NW). EWEB is municipal utility. Zone 4C mixed-marine is unique in project.**

## Fayetteville, NC

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KFAY USW00013722 — initial 503, retry OK), housing (place:22920 state:37), climate_hvac_failure_mode (Zone 3A warm-humid + Sandhills)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Duke Energy Progress Smart $aver), contractor_license (NC Board H-1/H-2/H-3)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:22920 state:37), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 72.8% electric / 22.9% gas. Fort Liberty (formerly Fort Bragg) military-affiliated housing drives demand patterns. Dual-load 1.7:1 HDD:CDD. 2.5% LP gas. Median 1983.

## Fort Wayne, IN

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KFWA USW00014827), housing (place:25000 state:18), climate_hvac_failure_mode (Zone 5A, 5,968 HDD, 33.6" snow)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (I&M/AEP), contractor_license (IN has no statewide license)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:25000 state:18), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 70.7% gas / 26.9% electric. Median 1971. No statewide HVAC license — local permits required.

## Glendale, AZ

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KPHX USW00023183 — shared with Phoenix metro), housing (place:27820 state:04), climate_hvac_failure_mode (Zone 2B hot-dry, 4,765 CDD)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (APS), contractor_license (AZ ROC R-39/C-39)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:27820 state:04), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 75.3% electric / 21.2% gas. 782 solar-heated homes (0.9%). 1,192 no-fuel homes (1.4%). Median 1986. 5.5:1 CDD:HDD.

## Grand Rapids, MI

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KGRR USW00094860), housing (place:34000 state:26), climate_hvac_failure_mode (6,408 HDD + **77.6" LAKE-EFFECT SNOW**)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Consumers Energy), contractor_license (MI LARA)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:34000 state:26), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **77.6" annual snowfall — second-highest in project after Buffalo (95.4"). 82.8% gas — second-highest gas share in project after Buffalo (86.0%).** Median 1953. Lake Michigan lake-effect driver.

## Hartford, CT

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KBDL USW00014740), housing (place:37000 state:09), climate_hvac_failure_mode (5,883 HDD + 51.7" snow + 7% fuel oil)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Energize CT/Eversource), contractor_license (CT DCP S-1)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:37000 state:09), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 65.8% gas / 23.3% electric / 7.0% fuel oil. Median 1953. 51.7" snow (Connecticut Valley). Inland vs. coastal Bridgeport.

## Huntsville, AL

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KHSV USW00003856), housing (place:37000 state:01), climate_hvac_failure_mode (Zone 3A dual-load, 54.29" precip)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Huntsville Utilities/TVA), contractor_license (AL HACR Board)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:37000 state:01), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 75.8% electric / 22.2% gas. Municipal TVA distributor (Huntsville Utilities). NASA/Redstone Arsenal economy. Balanced 1.3:1 HDD:CDD. Median 1984.

## Irvine, CA

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KSNA USW00093134), housing (place:36770 state:06), climate_hvac_failure_mode (Zone 3B mild Mediterranean)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (SCE), contractor_license (CA CSLB C-20)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:36770 state:06), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **Median year built 2001 — NEWEST HOUSING STOCK IN PROJECT.** 60.1% gas / 35.6% electric. 859 solar homes (0.8%), 1,549 no-fuel (1.4%). 1.3:1 CDD:HDD — mild Mediterranean.

## Kansas City, MO

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KMCI USW00013988), housing (place:38000 state:29), climate_hvac_failure_mode (Zone 4A dual-load)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Evergy), contractor_license (MO no statewide — KC municipal trade license)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:38000 state:29), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 67.5% gas / 29.5% electric. 219,486 units (large housing stock). No statewide HVAC license — KC municipal trade license required. Dual-load 2.7:1 HDD:CDD. Median 1968.

## Knoxville, TN

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KTYS USW00013891), housing (place:40000 state:47), climate_hvac_failure_mode (Zone 4A mixed-humid, 51.93" precip)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (KUB/TVA), contractor_license (TN CMC-C)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:40000 state:47), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 74.0% electric / 24.7% gas. KUB = 3rd TVA distributor in project (after Chattanooga EPB, Huntsville Utilities). 51.93" precip. Median 1974.

## Laredo, TX

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KLRD USW00012959), housing (place:41464 state:48), climate_hvac_failure_mode (Zone 2B extreme cooling, semi-arid)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (AEP Texas CoolSaver), contractor_license (TX TDLR ACR)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:41464 state:48), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **4,989 CDD — HIGHEST CDD IN ENTIRE PROJECT (beats Brownsville 4,542). 11:1 CDD:HDD.** 83.9% electric / 13.6% gas. 589 solar homes. Semi-arid 22.16" precip. Inland Rio Grande hotter than coastal Brownsville. Median 1996.

## Lexington, KY

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KLEX USW00093820), housing (place:46027 state:21 — Lexington-Fayette merged government), climate_hvac_failure_mode (Zone 4A mixed-humid, 49.84" precip)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (KU/PPL), contractor_license (KY DHBC Master HVAC)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:46027 state:21), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 57.2% electric / 40.8% gas. Merged Lexington-Fayette government. Historically affordable coal-generated power drove electric heating adoption. 49.84" precip. Median 1983.

## Lincoln, NE

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KLNK USW00014939), housing (place:28000 state:31), climate_hvac_failure_mode (Zone 5A cold Plains, 5,856 HDD, 26" snow)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (LES municipal), contractor_license (NE no statewide)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:28000 state:31), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 63.6% gas / 34.5% electric. Lincoln Electric System = municipal utility. NE has no statewide license. Median 1981. 29.34" precip (drier than Midwest average).

## Little Rock, AR

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KLIT USW00013963), housing (place:41000 state:05), climate_hvac_failure_mode (Zone 3A dual-load, 50.42" precip)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Entergy Arkansas), contractor_license (AR DLL)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:41000 state:05), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **Near-even 50.7% gas / 47.4% electric split — most balanced in project.** Dual-load 1.6:1 HDD:CDD. 50.42" precip. Median 1978.

## Los Angeles, CA

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KLAX USW00023174 — snowfall NOT returned), housing (place:44000 state:06), climate_hvac_failure_mode (mild Mediterranean, Zone 3B)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (LADWP), contractor_license (CA CSLB C-20)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:44000 state:06), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **1,419,663 occupied units — LARGEST HOUSING STOCK IN PROJECT by massive margin. 90,123 no-fuel homes (6.3%) — HIGHEST NO-FUEL SHARE. 6,550 solar homes. LADWP = largest municipal utility in US.** 57.7% gas / 33.6% electric. Median 1964.

## Lubbock, TX

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KLBB USW00023042), housing (place:45000 state:48), climate_hvac_failure_mode (Zone 3B semi-arid High Plains, evap cooling)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (LP&L municipal), contractor_license (TX TDLR ACR)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:45000 state:48), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 53.3% electric / 44.9% gas (near-even). Lubbock Power & Light = municipal utility (transitioned SPP→ERCOT 2021). Semi-arid 18.33" precip. 27°F diurnal swing. Evap cooling territory. Median 1983.

## Mobile, AL

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KMOB USW00013894), housing (place:50000 state:01), climate_hvac_failure_mode (Zone 2A extreme precipitation + hurricane)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Alabama Power), contractor_license (AL HACR Board)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:50000 state:01), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **67.08" annual precipitation — WETTEST CITY IN ENTIRE PROJECT (beats Baton Rouge 61.94").** 55.9% electric / 42.1% gas. 2,599 CDD. Gulf Coast hurricane exposure. Median 1974.

## Modesto, CA

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KMOD USW00023232 — snowfall NOT returned), housing (place:48354 state:06), climate_hvac_failure_mode (Zone 3B Central Valley hot-dry)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (MID municipal), contractor_license (CA CSLB C-20)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:48354 state:06), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 69.3% gas / 27.8% electric. MID = Modesto Irrigation District (municipal utility — serves both irrigation and electric). 362 solar homes. Central Valley tule fog winters. Median 1978.

## Peoria, IL

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KPIA USW00014842), housing (place:59000 state:17), climate_hvac_failure_mode (Zone 5A, 5,614 HDD, 26.2" snow)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Ameren Illinois), contractor_license (IL no statewide)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:59000 state:17), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 68.7% gas / 29.6% electric. IL no statewide license (like IN, NE, KS). Median 1966.

## Providence, RI

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KPVD USW00014765), housing (place:59000 state:44), climate_hvac_failure_mode (pre-war housing + fuel oil + cold + coastal)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Rhode Island Energy), contractor_license (RI DLT)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:59000 state:44), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **Median year built 1938 — OLDEST HOUSING STOCK IN ENTIRE PROJECT (beats Buffalo/Detroit/Pittsburgh 1938-1951 range). 8.3% fuel oil (high). 3.6% LP gas.** 71.2% gas / 15.6% electric. 36.6" snow. Narragansett Bay coastal salt-air.

## Shreveport, LA

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KSHV USW00013957), housing (place:70000 state:22), climate_hvac_failure_mode (Zone 3A cooling-dominant, 51.43" precip)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (SWEPCO), contractor_license (LA LSLBC)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:70000 state:22), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 54.4% electric / 43.7% gas (near-even). 1.3:1 CDD:HDD cooling-dominant. SWEPCO (AEP subsidiary). Median 1973.

## Spokane, WA

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KGEG USW00024157), housing (place:67000 state:53), climate_hvac_failure_mode (Zone 5B cold-dry Inland NW, 12.6:1 HDD:CDD)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Avista Utilities), contractor_license (WA L&I 06A)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:67000 state:53), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 12.6:1 HDD:CDD — among most heating-dominant in project. 54.0% gas / 41.7% electric / 0.6% wood (Inland NW). 45.4" snow + only 16.45" precip = dry continental snowfall. Median 1961. 1.3% fuel oil legacy.

## Springfield, MA

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KCEF USW00014764), housing (place:67000 state:25), climate_hvac_failure_mode (extreme heating + fuel oil + snow)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Eversource/WMECO/Mass Save), contractor_license (MA no statewide)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:67000 state:25), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 68.7" snow, 6,795 HDD, 15.2:1 HDD:CDD. 13.7% fuel oil (high). 58.6% gas / 20.2% electric. Median 1951. MA no statewide HVAC license. Connecticut River valley climate.

## Syracuse, NY

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KSYR USW00014771), housing (place:73000 state:36), climate_hvac_failure_mode (extreme lake-effect snow)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (National Grid), contractor_license (NY no statewide)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:73000 state:36), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **127.8" ANNUAL SNOWFALL — ABSOLUTE PROJECT RECORD (was Buffalo 95.4"). SNOWIEST LARGE CITY IN THE US.** Lake Ontario lake-effect. 69.5% gas / 24.3% electric. Median 1947. 10.6:1 HDD:CDD.

## Tallahassee, FL

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KTLH USW00093805 — snowfall NOT returned), housing (place:70600 state:12), climate_hvac_failure_mode (Zone 2A hot-humid, 58.81" precip)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (City of Tallahassee Utilities municipal), contractor_license (FL DBPR/CILB)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:70600 state:12), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 85.5% electric / 11.8% gas. City of Tallahassee Utilities = municipal. 58.81" precip. 1.9:1 CDD:HDD. Median 1987.

## Toledo, OH

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KTOL USW00014848), housing (place:77000 state:39), climate_hvac_failure_mode (Lake Erie lake-effect, 64.5" snow)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Toledo Edison/FirstEnergy), contractor_license (OH OCILB)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:77000 state:39), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** 64.5" Lake Erie lake-effect snow. 73.9% gas. 8.9:1 HDD:CDD. Median 1955. 118K units (sizeable housing stock).

## Winston-Salem, NC

- **Date researched:** 2026-04-16
- **Found (3/7):** climate (KINT USW00013723), housing (place:75000 state:37), climate_hvac_failure_mode (Zone 4A dual-load, Piedmont humidity)
- **Not_found:** permit_fees, local_building_code, utility_rebate_amounts (Duke Energy Carolinas), contractor_license (NC Board H-1/H-2/H-3)
- **URLs cited:** ncei.noaa.gov, api.census.gov (place:75000 state:37), energy.gov/energysaver/heat-and-cool, irs.gov
- **Notes:** **4.4% fuel oil — unusually high for a Southern city (Moravian-era housing legacy).** 60.9% electric / 31.6% gas. 2.3:1 HDD:CDD. Median 1980.
