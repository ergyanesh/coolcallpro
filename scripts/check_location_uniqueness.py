"""
Phase 4 of the programmatic-uniqueness uplift plan.

Computes 5-word shingle uniqueness for every city page in `locations/` by
comparing each page's body shingles against the union of all OTHER city
pages' shingles. Reports any page below the configured target (default 70%).

Output:
  - Console summary (sorted worst-first)
  - `_audit/location_uniqueness.csv` — per-page metrics for downstream tooling
  - Exit code 1 if any page < HARD_FLOOR (default 65%); else 0

The 65% hard-floor matches the pinned cohort policy: small clusters of
climate-similar cities may legitimately fall in 65-69% range, but anything
under 65% is a fail. The 70% target is the median goal; pages between
65-70% emit a warning but do not fail the gate.

Usage:
    python scripts/check_location_uniqueness.py            # all city pages
    python scripts/check_location_uniqueness.py --strict   # fail at <70% instead of <65%
    python scripts/check_location_uniqueness.py --single locations/charleston-sc.html
    python scripts/check_location_uniqueness.py --top 20   # show 20 worst pages

Skips state-hub pages (same dir but different shape) — those get their own
audit in the follow-up plan.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCATIONS_DIR = REPO_ROOT / "locations"
AUDIT_DIR = REPO_ROOT / "_audit"

TARGET_UNIQUENESS = 70.0
HARD_FLOOR = 65.0  # pinned cohort policy

# Standard 51-state slug list — anything matching is a state hub, not a city.
STATE_SLUGS = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "district-of-columbia", "florida", "georgia",
    "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky",
    "louisiana", "maine", "maryland", "massachusetts", "michigan",
    "minnesota", "mississippi", "missouri", "montana", "nebraska", "nevada",
    "new-hampshire", "new-jersey", "new-mexico", "new-york",
    "north-carolina", "north-dakota", "ohio", "oklahoma", "oregon",
    "pennsylvania", "rhode-island", "south-carolina", "south-dakota",
    "tennessee", "texas", "utah", "vermont", "virginia", "washington",
    "west-virginia", "wisconsin", "wyoming",
}


def list_city_pages() -> list[Path]:
    return sorted(p for p in LOCATIONS_DIR.glob("*.html") if p.stem not in STATE_SLUGS)


def extract_main_text(html: str) -> str:
    """Strip header/footer/nav/script/style/HTML-comments down to <main> body
    text. Match the audit_article.py pattern so the tooling stays consistent."""
    m = re.search(r"<main[^>]*>(.*?)</main>", html, re.DOTALL | re.IGNORECASE)
    body = m.group(1) if m else html
    body = re.sub(r"<(script|style|nav|footer|header)[^>]*>.*?</\1>", "", body, flags=re.DOTALL | re.IGNORECASE)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", body)
    return re.sub(r"\s+", " ", text).strip()


def shingles(text: str, n: int = 5) -> set[str]:
    words = text.lower().split()
    return set(" ".join(words[i:i + n]) for i in range(len(words) - n + 1))


def compute_uniqueness(pages: list[Path]) -> list[dict]:
    all_shingles = {p.stem: shingles(extract_main_text(p.read_text(encoding="utf-8"))) for p in pages}
    results = []
    for stem, own in all_shingles.items():
        others_union: set[str] = set()
        for s2, sh in all_shingles.items():
            if s2 != stem:
                others_union |= sh
        unique = own - others_union
        pct = (len(unique) / len(own) * 100) if own else 0.0
        results.append({
            "slug": stem,
            "total_shingles": len(own),
            "unique_shingles": len(unique),
            "uniqueness_pct": round(pct, 2),
        })
    results.sort(key=lambda r: r["uniqueness_pct"])
    return results


def write_csv(results: list[dict]) -> Path:
    AUDIT_DIR.mkdir(exist_ok=True)
    out = AUDIT_DIR / "location_uniqueness.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    return out


def print_summary(results: list[dict], target: float, top_n: int = 15) -> None:
    pcts = [r["uniqueness_pct"] for r in results]
    n = len(pcts)
    median = sorted(pcts)[n // 2]
    mean = sum(pcts) / n
    below_floor = sum(1 for p in pcts if p < HARD_FLOOR)
    in_warn_band = sum(1 for p in pcts if HARD_FLOOR <= p < target)
    above_target = sum(1 for p in pcts if p >= target)

    print(f"\n== Location-page uniqueness audit ({n} city pages) ==")
    print(f"  Target:      {target:.0f}%")
    print(f"  Hard floor:  {HARD_FLOOR:.0f}%")
    print()
    print(f"  Median:      {median:.1f}%")
    print(f"  Mean:        {mean:.1f}%")
    print(f"  Min:         {pcts[0]:.1f}%")
    print(f"  Max:         {pcts[-1]:.1f}%")
    print()
    print(f"  Above target (>={target:.0f}%):  {above_target} ({above_target * 100 // n}%)")
    print(f"  Warn band ({HARD_FLOOR:.0f}-{target:.0f}%):     {in_warn_band} ({in_warn_band * 100 // n}%)")
    print(f"  HARD FLOOR (<{HARD_FLOOR:.0f}%):    {below_floor} ({below_floor * 100 // n}%)")

    if below_floor or in_warn_band:
        print(f"\n  Worst {min(top_n, below_floor + in_warn_band)} pages:")
        for r in results[:top_n]:
            if r["uniqueness_pct"] >= target:
                break
            tag = "[FAIL]" if r["uniqueness_pct"] < HARD_FLOOR else "[WARN]"
            print(f"    {tag} {r['slug']:<28} {r['uniqueness_pct']:>5.1f}%  "
                  f"({r['unique_shingles']:>4}/{r['total_shingles']:<5} unique)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="Fail at <70%% instead of <65%% (use after Phase 5 rollout completes)")
    parser.add_argument("--single", type=str,
                        help="Audit just one page (still compares against the full corpus)")
    parser.add_argument("--top", type=int, default=15,
                        help="Show top N worst pages (default 15)")
    parser.add_argument("--all", action="store_true",
                        help="Show every page, not just below-target ones (default)")
    args = parser.parse_args()

    pages = list_city_pages()
    if not pages:
        print(f"ERROR: no city pages found in {LOCATIONS_DIR}", file=sys.stderr)
        return 2

    results = compute_uniqueness(pages)
    csv_path = write_csv(results)

    target = TARGET_UNIQUENESS
    fail_at = TARGET_UNIQUENESS if args.strict else HARD_FLOOR

    if args.single:
        slug = Path(args.single).stem
        match = next((r for r in results if r["slug"] == slug), None)
        if not match:
            print(f"ERROR: {slug} not found in city corpus", file=sys.stderr)
            return 2
        verdict = "PASS" if match["uniqueness_pct"] >= fail_at else "FAIL"
        print(f"\n  {verdict}: {slug} = {match['uniqueness_pct']:.1f}% "
              f"({match['unique_shingles']}/{match['total_shingles']} unique)")
        print(f"\n  CSV report: {csv_path}")
        return 0 if match["uniqueness_pct"] >= fail_at else 1

    print_summary(results, target=target, top_n=args.top)

    if args.all:
        print(f"\n== Full results ==")
        for r in results:
            print(f"  {r['slug']:<28} {r['uniqueness_pct']:>5.1f}%")

    print(f"\n  CSV report: {csv_path}")

    failing = [r for r in results if r["uniqueness_pct"] < fail_at]
    if failing:
        print(f"\nFAIL — {len(failing)} page(s) below {fail_at:.0f}% threshold")
        return 1
    print(f"\nOK — every page meets the {fail_at:.0f}% threshold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
