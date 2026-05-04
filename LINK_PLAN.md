# CoolCallPro Link Plan — Deterministic Article↔City Mapping

_Auto-generated from `cluster_map.json` + `article_city_linker.py`. Regenerate with `python generate_link_plan.py`._

## What these files are

The article→city and city→article mappings for CoolCallPro are **computed deterministically** by `article_city_linker.py`. These CSVs are the materialized output of that algorithm — they exist so you can audit every mapping at a glance instead of having to run the linker for each article.

**Do NOT hand-edit the CSVs.** If a mapping is wrong, change the underlying inputs:
- Article definitions + cluster assignments → edit `cluster_map.json`
- Climate weights per cluster → edit `CLUSTER_CLIMATE_WEIGHTS` in `article_city_linker.py`
- City list + climate zones → edit `cities_updated.xlsx`

Then re-run `python generate_link_plan.py` and commit the new CSVs.

## Files

| File | What it shows | Rows |
|------|---------------|------|
| `article_link_plan.csv` | Each planned article → its 4-5 city links + 2 state hubs + pillar link + cross-cluster anchor | 46 |
| `city_link_coverage.csv` | Each published city → every article slug that will link to it | 115 |
| `LINK_PLAN.md` (this file) | Human overview + coverage stats | — |

## Coverage Summary

- **Total published cities:** 115
- **Cities receiving ≥1 article link:** 97 (84%)
- **Orphan cities (0 planned article links):** 18
- **Average article links per city:** 1.7
- **Max article links to any one city:** 6

### Cities with 4+ planned article links (watch for crowding)

| City slug | Article links |
|-----------|---------------|
| `san-antonio-tx` | 6 |
| `tucson-az` | 5 |
| `cheyenne-wy` | 5 |
| `mobile-al` | 4 |
| `san-diego-ca` | 4 |
| `louisville-ky` | 4 |
| `el-paso-tx` | 4 |
| `grand-rapids-mi` | 4 |

## Clusters (from cluster_map.json)

| ID | Name | Pillar status | Live articles | Pending articles | Climate weights |
|----|------|---------------|---------------|------------------|-----------------|
| C1_ac | AC Troubleshooting & Emergencies | live | 12 | 0 | hot-humid:0.4, tropical:0.1, hot-dry:0.25, mixed-humid:0.25 |
| C2_furnace | Furnace & Heating Emergencies | live | 4 | 4 | cold:0.5, subarctic:0.1, mountain:0.25, mixed-humid:0.15 |
| C3_heatpump | Heat Pumps & Modern Systems | pending | 1 | 3 | coastal:0.3, mixed-humid:0.4, mountain:0.3 |
| C4_cost | Repair & Replacement Costs | live | 1 | 7 | all_rotated |
| C5_compare | Repair-vs-Replace & Comparisons | pending | 2 | 2 | all_rotated |
| C6_maint | Maintenance, Safety & Seasonal | live | 3 | 1 | all_rotated |

## How to use

**Before writing an article**, open `article_link_plan.csv` and find its row. You'll see exactly:
- Which 4 cities to link to (in the body copy as contextual examples AND in the footer block)
- Which 2 state hubs to link
- Which pillar article to link to
- Which cross-cluster anchor article to reference

**When a new city or article is added**, re-run `python generate_link_plan.py` to refresh every mapping. The determinism guarantees that existing mappings stay the same — only the new rows change.

**For end-to-end QC**, check `city_link_coverage.csv` for orphans (cities with 0 planned article links) and over-linked cities (>5 links) before scaling past 30 articles.