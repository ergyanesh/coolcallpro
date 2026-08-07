#!/usr/bin/env python3
"""GSC Search Analytics performance report — the strategic counterpart to
gsc_index_monitor.py.

The index monitor answers "are our pages IN Google?". This answers "are they
RANKING, and for what?" — which is the question that decides whether the
content strategy is working.

Written 2026-08-07 because the only performance data on hand was a manual CSV
export from 2026-05-22 (28,866 impressions / 6 clicks / 0.8% of impressions on
page 1), and deciding anything about the site's future on 2.5-month-old numbers
was guesswork.

Auth + credentials are reused verbatim from gsc_index_monitor.py — set
GSC_SERVICE_ACCOUNT_JSON (Path A) or GSC_OAUTH_CREDENTIALS_FILE (Path B).
See docs/gsc-monitor-setup.md.

Usage:
    python scripts/gsc_performance_report.py                 # last 28d vs prior 28d
    python scripts/gsc_performance_report.py --days 90       # longer window
    python scripts/gsc_performance_report.py --out report.md # also write to file

Note on GSC's data lag: Search Analytics is typically 2-3 days behind, so the
window ends 3 days ago rather than today. Otherwise the "current" period is
diluted by days that have not finished reporting and every trend looks negative.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from typing import Any

# Reuse the credential loader + service builder + property id rather than
# duplicating them. Both scripts must always authenticate identically.
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from gsc_index_monitor import SITE_URL, build_service, get_credentials  # noqa: E402

# GSC finalises Search Analytics data ~2-3 days after the fact.
DATA_LAG_DAYS = 3

# Page buckets. Order matters — first matching prefix wins, so the more specific
# '/articles/' is tested before the root-level 'article-' fallback.
PAGE_BUCKETS = [
    ("Location pages", ("/locations/",)),
    ("Locations hub", ("/locations",)),
    ("Cluster articles", ("/articles/",)),
    ("Root articles", ("/article-",)),
    ("Cost guide", ("/costs",)),
    ("Emergency", ("/emergency",)),
]


def _q(service, start: date, end: date, dimensions: list[str],
       row_limit: int = 25000) -> list[dict[str, Any]]:
    """Paginated Search Analytics query."""
    rows: list[dict[str, Any]] = []
    start_row = 0
    while True:
        body = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": dimensions,
            "rowLimit": row_limit,
            "startRow": start_row,
        }
        resp = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
        batch = resp.get("rows", [])
        rows.extend(batch)
        if len(batch) < row_limit:
            break
        start_row += row_limit
    return rows


def _totals(rows: list[dict[str, Any]]) -> dict[str, float]:
    clicks = sum(r.get("clicks", 0) for r in rows)
    imps = sum(r.get("impressions", 0) for r in rows)
    # Position must be impression-weighted; a plain mean over rows lets a
    # 1-impression query at position 3 outweigh a 900-impression query at 40.
    pos = (sum(r.get("position", 0) * r.get("impressions", 0) for r in rows) / imps) if imps else 0.0
    return {
        "clicks": clicks,
        "impressions": imps,
        "ctr": (clicks / imps * 100) if imps else 0.0,
        "position": pos,
    }


def _delta(cur: float, prev: float) -> str:
    if prev == 0:
        return "new" if cur else "—"
    pct = (cur - prev) / prev * 100
    return f"{pct:+.0f}%"


def _bucket_of(url: str) -> str:
    path = url.replace("https://coolcallpro.com", "")
    for name, prefixes in PAGE_BUCKETS:
        if any(path.startswith(p) for p in prefixes):
            return name
    return "Other root pages"


def build_report(service, days: int) -> str:
    end = date.today() - timedelta(days=DATA_LAG_DAYS)
    start = end - timedelta(days=days - 1)
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)

    out: list[str] = []
    w = out.append

    w(f"# GSC Performance Report — generated {date.today().isoformat()}")
    w("")
    w(f"Current window: **{start} → {end}** ({days}d, ends {DATA_LAG_DAYS}d ago for GSC data lag)")
    w(f"Prior window:   {prev_start} → {prev_end} ({days}d)")
    w("")

    cur_rows = _q(service, start, end, ["query"])
    prev_rows = _q(service, prev_start, prev_end, ["query"])
    cur, prev = _totals(cur_rows), _totals(prev_rows)

    w("## Headline")
    w("")
    w("| Metric | Current | Prior | Change |")
    w("|---|---|---|---|")
    w(f"| Clicks | **{cur['clicks']:,.0f}** | {prev['clicks']:,.0f} | {_delta(cur['clicks'], prev['clicks'])} |")
    w(f"| Impressions | **{cur['impressions']:,.0f}** | {prev['impressions']:,.0f} | {_delta(cur['impressions'], prev['impressions'])} |")
    w(f"| CTR | {cur['ctr']:.3f}% | {prev['ctr']:.3f}% | — |")
    w(f"| Avg position (imp-weighted) | {cur['position']:.1f} | {prev['position']:.1f} | "
      f"{cur['position'] - prev['position']:+.1f} |")
    w(f"| Distinct queries w/ impressions | {len(cur_rows):,} | {len(prev_rows):,} | "
      f"{_delta(len(cur_rows), len(prev_rows))} |")
    w("")

    # --- The decisive chart: where do impressions actually sit in the SERP? ---
    w("## Impressions by average position")
    w("")
    w("This is the diagnostic that separates *\"we rank but nobody clicks\"* (fixable")
    w("with titles/meta) from *\"we don't rank\"* (needs authority or a different")
    w("target). Page 1 is positions 1-10.")
    w("")
    edges = [(1, 10, "1-10 (page 1)"), (11, 20, "11-20 (page 2)"),
             (21, 30, "21-30 (page 3)"), (31, 50, "31-50"), (51, 10**9, "51+")]

    def bucketise(rows: list[dict[str, Any]]) -> dict[str, float]:
        b = {label: 0.0 for _, _, label in edges}
        for r in rows:
            p, i = r.get("position", 0), r.get("impressions", 0)
            for lo, hi, label in edges:
                if lo <= p <= hi:
                    b[label] += i
                    break
        return b

    cb, pb = bucketise(cur_rows), bucketise(prev_rows)
    w("| Position | Impressions | Share | Prior share |")
    w("|---|---|---|---|")
    for _, _, label in edges:
        share = cb[label] / cur["impressions"] * 100 if cur["impressions"] else 0
        pshare = pb[label] / prev["impressions"] * 100 if prev["impressions"] else 0
        w(f"| {label} | {cb[label]:,.0f} | **{share:.1f}%** | {pshare:.1f}% |")
    w("")

    # --- Which half of the site is earning attention? ---
    w("## Performance by page type")
    w("")
    w("The strategic split: programmatic location pages vs editorial articles.")
    w("")
    page_rows = _q(service, start, end, ["page"])
    agg: dict[str, dict[str, float]] = {}
    for r in page_rows:
        b = agg.setdefault(_bucket_of(r["keys"][0]),
                           {"clicks": 0.0, "impressions": 0.0, "pos_w": 0.0, "n": 0})
        b["clicks"] += r.get("clicks", 0)
        b["impressions"] += r.get("impressions", 0)
        b["pos_w"] += r.get("position", 0) * r.get("impressions", 0)
        b["n"] += 1
    w("| Page type | URLs | Impressions | Clicks | CTR | Avg pos |")
    w("|---|---|---|---|---|---|")
    for name, b in sorted(agg.items(), key=lambda kv: -kv[1]["impressions"]):
        ctr = b["clicks"] / b["impressions"] * 100 if b["impressions"] else 0
        pos = b["pos_w"] / b["impressions"] if b["impressions"] else 0
        w(f"| {name} | {b['n']:,.0f} | {b['impressions']:,.0f} | **{b['clicks']:,.0f}** | "
          f"{ctr:.2f}% | {pos:.1f} |")
    w("")

    # --- Actionable: what is within striking distance of page 1? ---
    w("## Queries within striking distance (position 5-20, >=15 impressions)")
    w("")
    w("These are the only queries where effort has near-term upside — close enough")
    w("that a real ranking gain is plausible, with enough volume to matter.")
    w("")
    near = [r for r in cur_rows
            if 5 <= r.get("position", 999) <= 20 and r.get("impressions", 0) >= 15]
    near.sort(key=lambda r: -r.get("impressions", 0))
    if near:
        w("| Impressions | Position | Clicks | Query |")
        w("|---|---|---|---|")
        for r in near[:30]:
            w(f"| {r['impressions']:,.0f} | {r.get('position', 0):.1f} | {r.get('clicks', 0):,.0f} "
              f"| {r['keys'][0]} |")
        w("")
        w(f"Total: **{len(near)} queries**, {sum(r['impressions'] for r in near):,.0f} impressions.")
    else:
        w("**None.** Nothing is within striking distance of page 1.")
    w("")

    # --- Anything actually ON page 1? ---
    w("## Already on page 1 (position <= 10)")
    w("")
    p1 = [r for r in cur_rows if r.get("position", 999) <= 10]
    p1.sort(key=lambda r: -r.get("impressions", 0))
    if p1:
        w("| Impressions | Position | Clicks | CTR | Query |")
        w("|---|---|---|---|---|")
        for r in p1[:30]:
            ctr = r.get("clicks", 0) / r["impressions"] * 100 if r.get("impressions") else 0
            w(f"| {r['impressions']:,.0f} | {r.get('position', 0):.1f} | {r.get('clicks', 0):,.0f} "
              f"| {ctr:.1f}% | {r['keys'][0]} |")
        w("")
        w(f"Total: **{len(p1)} queries** on page 1, "
          f"{sum(r['impressions'] for r in p1):,.0f} impressions, "
          f"{sum(r.get('clicks', 0) for r in p1):,.0f} clicks.")
    else:
        w("**None.** Zero queries rank on page 1.")
    w("")

    w("## Top 25 queries by impressions")
    w("")
    w("| Impressions | Position | Clicks | Query |")
    w("|---|---|---|---|")
    for r in sorted(cur_rows, key=lambda r: -r.get("impressions", 0))[:25]:
        w(f"| {r['impressions']:,.0f} | {r.get('position', 0):.1f} | {r.get('clicks', 0):,.0f} "
          f"| {r['keys'][0]} |")
    w("")

    w("## Top 25 pages by impressions")
    w("")
    w("| Impressions | Clicks | Position | Page |")
    w("|---|---|---|---|")
    for r in sorted(page_rows, key=lambda r: -r.get("impressions", 0))[:25]:
        w(f"| {r['impressions']:,.0f} | {r.get('clicks', 0):,.0f} | {r.get('position', 0):.1f} "
          f"| {r['keys'][0].replace('https://coolcallpro.com', '')} |")
    w("")

    w("## Reference — manual CSV export, 2026-03-10 → 2026-05-20 (72d)")
    w("")
    w("The baseline this report exists to update:")
    w("")
    w("- 28,866 impressions, **6 clicks** (0.02% CTR)")
    w("- 0.8% of impressions on page 1; 40.7% at position 51+")
    w("- 3 queries at position <=12 with >=20 impressions, all with 0 clicks")
    w("- Location pages carried most impressions with zero clicks")
    w("")

    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--days", type=int, default=28,
                    help="Length of the current window in days (default 28).")
    ap.add_argument("--out", default="",
                    help="Also write the report to this path.")
    args = ap.parse_args()

    service = build_service(get_credentials())
    report = build_report(service, args.days)
    print(report)
    if args.out:
        from pathlib import Path
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"\n[wrote {args.out}]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
