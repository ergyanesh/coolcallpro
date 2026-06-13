"""
GSC Indexation Monitor — daily snapshot of per-URL indexation status.

What it does
------------
1. Reads sitemap.xml to get the canonical list of URLs the site WANTS indexed.
2. Calls GSC Search Analytics API for last 28 days → gets URLs that received
   any impression (proxy for "currently indexed").
3. For URLs in sitemap WITHOUT recent impressions, calls URL Inspection API
   to get authoritative indexStatusResult.verdict + coverageState.
4. Writes:
     .gsc_state/indexed_yesterday.json   (today's PASS set, becomes yesterday tomorrow)
     .gsc_state/coverage_states.json     (latest coverageState per URL)
     .gsc_state/report-YYYY-MM-DD.md     (human-readable daily report, tracked)
5. Computes day-over-day diff (newly added + newly removed URLs).
6. Exits 1 if removed > ALERT_THRESHOLD (default 5) to trigger CI failure +
   email alert from the GitHub Action.

Why it exists
-------------
A drop from 121 → 100 indexed URLs over 3 days (caught on 2026-06-13)
revealed that NO automation existed to alert on indexation drift. By the
time the homeowner-user notices the GSC dashboard count drop, real
de-indexation can have been happening for days. This script catches drops
within 24 hours.

Auth
----
Path A (recommended): Service Account JSON. Set env var GSC_SERVICE_ACCOUNT_JSON
  to either (a) the file path to a service-account JSON, or (b) the JSON
  string itself. In GitHub Actions, store the JSON as a secret and inject
  it as an env var.
Path B (local dev): set GSC_OAUTH_CREDENTIALS_FILE to a path containing
  OAuth user credentials; the script will refresh tokens automatically.

Either way, the service account or OAuth user must be added as a "Full" or
"Restricted" user under the GSC property Settings → Users and permissions.

Quota
-----
URL Inspection API: 2,000 calls/day, 600/min per site. The site has ~220
URLs in sitemap; even a full sweep fits comfortably within quota.
Search Analytics: 1,200/min per site; one call retrieves up to 25,000 rows.

Run
---
  python scripts/gsc_index_monitor.py                   # daily check
  python scripts/gsc_index_monitor.py --dry-run         # skip API calls, validate auth + read sitemap
  python scripts/gsc_index_monitor.py --threshold 10    # alert only on drops > 10
  python scripts/gsc_index_monitor.py --full-inspect    # call URL Inspection for EVERY sitemap URL
                                                        # (otherwise only zero-impression URLs are inspected)

Reference docs (project memory):
  .agents/SKILLS/seo-google/references/search-console-api.md
  .agents/SKILLS/seo-google/references/auth-setup.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

ROOT = Path(__file__).parent.parent
SITEMAP = ROOT / "sitemap.xml"
STATE_DIR = ROOT / ".gsc_state"
SITE_URL = "sc-domain:coolcallpro.com"  # GSC property identifier

ALERT_THRESHOLD_DEFAULT = 5

# Lazy imports: required Google libraries are only imported when actually
# hitting the API, so --dry-run works even before `pip install -r requirements.txt`.


def load_sitemap_urls() -> set[str]:
    """Return the set of canonical URLs from sitemap.xml."""
    if not SITEMAP.exists():
        print(f"ERROR: {SITEMAP} not found", file=sys.stderr)
        sys.exit(1)
    tree = ET.parse(SITEMAP)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {loc.text.strip() for loc in tree.iter(f'{{{ns["sm"]}}}loc')}


def get_credentials():
    """Build google.auth credentials from env. Path A or B."""
    sa_env = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip()
    oauth_env = os.environ.get("GSC_OAUTH_CREDENTIALS_FILE", "").strip()

    if sa_env:
        from google.oauth2 import service_account  # type: ignore
        # If env contains JSON content, parse directly. Otherwise treat as path.
        if sa_env.startswith("{"):
            info = json.loads(sa_env)
        else:
            with open(sa_env, encoding="utf-8") as f:
                info = json.load(f)
        creds = service_account.Credentials.from_service_account_info(
            info,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        return creds

    if oauth_env:
        from google.oauth2.credentials import Credentials  # type: ignore
        from google.auth.transport.requests import Request  # type: ignore
        with open(oauth_env, encoding="utf-8") as f:
            info = json.load(f)
        creds = Credentials.from_authorized_user_info(
            info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        if not creds.valid and creds.refresh_token:
            creds.refresh(Request())
        return creds

    print("ERROR: No GSC credentials found.", file=sys.stderr)
    print("Set GSC_SERVICE_ACCOUNT_JSON to either a path or JSON content (Path A),", file=sys.stderr)
    print("or GSC_OAUTH_CREDENTIALS_FILE to a path with OAuth user credentials (Path B).", file=sys.stderr)
    print("See: docs/gsc-monitor-setup.md", file=sys.stderr)
    sys.exit(2)


def build_service(creds):
    """Build the Search Console API client."""
    from googleapiclient.discovery import build  # type: ignore
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def fetch_urls_with_impressions(service, days: int = 28) -> set[str]:
    """Call Search Analytics for the last N days → set of URLs receiving impressions."""
    end = date.today()
    start = end - timedelta(days=days)
    request_body: dict[str, Any] = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": ["page"],
        "rowLimit": 25000,
        "startRow": 0,
    }
    urls: set[str] = set()
    while True:
        resp = service.searchanalytics().query(
            siteUrl=SITE_URL, body=request_body
        ).execute()
        rows = resp.get("rows", [])
        if not rows:
            break
        for row in rows:
            urls.add(row["keys"][0])
        if len(rows) < request_body["rowLimit"]:
            break
        request_body["startRow"] += request_body["rowLimit"]
    return urls


def inspect_url(service, url: str) -> dict[str, Any]:
    """Single URL Inspection API call. Returns inspectionResult dict or {} on failure."""
    body = {
        "inspectionUrl": url,
        "siteUrl": SITE_URL,
    }
    try:
        resp = service.urlInspection().index().inspect(body=body).execute()
        return resp.get("inspectionResult", {})
    except Exception as e:
        return {"_error": str(e)}


def classify(inspection: dict[str, Any]) -> tuple[str, str]:
    """Extract (verdict, coverageState) from inspectionResult."""
    idx = inspection.get("indexStatusResult", {})
    verdict = idx.get("verdict", "UNKNOWN")
    coverage = idx.get("coverageState", "Unknown")
    return verdict, coverage


def previous_indexed_set() -> set[str]:
    p = STATE_DIR / "indexed_yesterday.json"
    if not p.exists():
        return set()
    try:
        return set(json.loads(p.read_text(encoding="utf-8")))
    except Exception:
        return set()


def write_state(indexed: set[str], coverage_states: dict[str, dict[str, str]]):
    STATE_DIR.mkdir(exist_ok=True)
    (STATE_DIR / "indexed_yesterday.json").write_text(
        json.dumps(sorted(indexed), indent=2),
        encoding="utf-8",
    )
    (STATE_DIR / "coverage_states.json").write_text(
        json.dumps(coverage_states, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def write_report(
    indexed: set[str],
    coverage_states: dict[str, dict[str, str]],
    added: set[str],
    removed: set[str],
    sitemap_urls: set[str],
):
    today = date.today().isoformat()
    STATE_DIR.mkdir(exist_ok=True)
    report_path = STATE_DIR / f"report-{today}.md"

    # Count coverageState reasons
    reason_counts: dict[str, int] = {}
    for url, cs in coverage_states.items():
        reason = cs.get("coverageState", "Unknown")
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

    lines = [
        f"# GSC Indexation Report — {today}",
        "",
        "## Headline",
        "",
        f"- **URLs in sitemap.xml:** {len(sitemap_urls)}",
        f"- **URLs currently indexed (PASS verdict):** {len(indexed)}",
        f"- **Day-over-day delta:** +{len(added)} added, -{len(removed)} removed",
        "",
        "## CoverageState reason distribution",
        "",
    ]
    for reason, count in sorted(reason_counts.items(), key=lambda t: -t[1]):
        lines.append(f"- **{reason}**: {count}")

    if added:
        lines += ["", f"## Newly indexed today ({len(added)})", ""]
        for u in sorted(added):
            lines.append(f"- {u}")

    if removed:
        lines += ["", f"## Newly DROPPED from index today ({len(removed)})", ""]
        for u in sorted(removed):
            cs = coverage_states.get(u, {})
            reason = cs.get("coverageState", "Unknown")
            lines.append(f"- {u} — reason: **{reason}**")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {report_path}")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip API calls; just validate sitemap + auth setup.")
    parser.add_argument("--threshold", type=int, default=ALERT_THRESHOLD_DEFAULT,
                        help=f"Alert if removed count exceeds this (default {ALERT_THRESHOLD_DEFAULT}).")
    parser.add_argument("--full-inspect", action="store_true",
                        help="Inspect EVERY sitemap URL via URL Inspection (otherwise only "
                             "URLs without recent impressions are inspected). Slower but more "
                             "authoritative.")
    args = parser.parse_args()

    sitemap_urls = load_sitemap_urls()
    print(f"Sitemap has {len(sitemap_urls)} URLs")

    if args.dry_run:
        # Just verify creds can be built
        creds = get_credentials()
        print(f"Credentials loaded: {type(creds).__name__}")
        print("Dry-run OK. Re-run without --dry-run to fetch from GSC.")
        return 0

    creds = get_credentials()
    service = build_service(creds)

    print(f"Fetching URLs with impressions (last 28d)...")
    impressions_urls = fetch_urls_with_impressions(service, days=28)
    print(f"  {len(impressions_urls)} URLs received impressions")

    # Determine which URLs need URL Inspection.
    sitemap_with_impressions = sitemap_urls & impressions_urls
    sitemap_without_impressions = sitemap_urls - impressions_urls

    if args.full_inspect:
        to_inspect = sorted(sitemap_urls)
        print(f"Full-inspect mode: inspecting all {len(to_inspect)} sitemap URLs")
    else:
        to_inspect = sorted(sitemap_without_impressions)
        print(f"Inspecting {len(to_inspect)} URLs without recent impressions")
        # Assume URLs with impressions are PASS without inspection (fast path)

    # URL Inspection: 600/min per site cap. Throttle to ~10/sec to be safe.
    coverage_states: dict[str, dict[str, str]] = {}
    indexed: set[str] = set()
    for i, url in enumerate(to_inspect, 1):
        inspection = inspect_url(service, url)
        verdict, coverage = classify(inspection)
        coverage_states[url] = {"verdict": verdict, "coverageState": coverage}
        if verdict == "PASS":
            indexed.add(url)
        if i % 25 == 0:
            print(f"  inspected {i}/{len(to_inspect)} (latest: {coverage})")
        if i % 100 == 0:
            time.sleep(2)  # extra breather every 100 calls

    # URLs with impressions but not inspected → assume indexed
    if not args.full_inspect:
        for u in sitemap_with_impressions:
            indexed.add(u)
            coverage_states.setdefault(u, {"verdict": "ASSUMED_PASS",
                                          "coverageState": "Submitted and indexed (impressions in last 28d)"})

    # Compute diff vs yesterday
    yesterday = previous_indexed_set()
    added = indexed - yesterday
    removed = yesterday - indexed

    # Persist
    write_state(indexed, coverage_states)
    report_path = write_report(indexed, coverage_states, added, removed, sitemap_urls)

    print()
    print(f"=== Result ===")
    print(f"Indexed today: {len(indexed)}")
    if yesterday:
        print(f"Indexed yesterday: {len(yesterday)}")
        print(f"+{len(added)} added, -{len(removed)} removed")
    else:
        print("First run (no yesterday snapshot to diff against)")

    if len(removed) > args.threshold:
        print()
        print(f"!!! ALERT: {len(removed)} URLs dropped from index (threshold {args.threshold})")
        print(f"See {report_path} for the full list.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
