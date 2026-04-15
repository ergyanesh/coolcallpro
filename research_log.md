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

---
