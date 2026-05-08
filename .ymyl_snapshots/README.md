# YMYL Primary-Source Snapshots

This directory holds plain-text snapshots and metadata for the 7 YMYL primary
sources monitored by `scripts/ymyl_source_watcher.py` (Layer 2 of the YMYL
verification system — see CLAUDE.md "YMYL Three-Layer Verification System").

**Files written here are TRACKED in git** (not gitignored). The weekly GitHub
Action `.github/workflows/ymyl-source-watcher.yml` commits refreshed snapshots
so the next week's diff has a stable baseline to compare against.

## Files

- `<slug>.txt` — plain-text snapshot of the source page body (script + style
  + nav stripped). Used as the diff baseline.
- `<slug>.meta.json` — metadata: URL, label, fetch timestamp, content hash,
  byte length.
- `_report.md` — latest run's human-readable diff report. Used by the
  weekly remote-trigger alert routine and by the GH Action to open issues.

## Sources currently monitored

| Slug | Source |
|---|---|
| `irs-25c` | IRS Section 25C Energy Efficient Home Improvement Credit |
| `irs-25d` | IRS Section 25D Residential Clean Energy Credit |
| `energystar-federal-tax-credits` | ENERGY STAR Federal Tax Credits |
| `epa-section-608` | EPA Section 608 Refrigerant Handling |
| `epa-aim-tech-transitions` | EPA AIM Act Technology Transitions Program |
| `doe-heat-pump-systems` | DOE Heat Pump Systems |
| `doe-home-upgrades` | DOE Home Upgrades / HEAR Portal |

To add or remove sources, edit `scripts/ymyl_source_watcher.py SOURCES`
**and** `audit_article.py YMYL_TOPIC_SOURCE_MATRIX` to keep the per-topic
required-link matrix in sync.
