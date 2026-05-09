"""
Layer 2 of the YMYL verification system: weekly primary-source diff watcher.

Snapshots a fixed list of YMYL primary-source pages (IRS 25C, IRS 25D,
ENERGY STAR Federal Credits, EPA Section 608, EPA AIM Act / Tech Transitions,
DOE Heat Pump Systems) by URL and stores a content fingerprint under
``.ymyl_snapshots/``. On subsequent runs, it diffs current content against
the last snapshot and reports any *material* change (substantive text deltas
beyond timestamps and minor wording).

Usage:
    python scripts/ymyl_source_watcher.py            # fetch + diff + write report
    python scripts/ymyl_source_watcher.py --init     # snapshot only, no diff
    python scripts/ymyl_source_watcher.py --quiet    # exit 0 silently if no change

Output:
    .ymyl_snapshots/<slug>.txt        plain-text snapshot of body content
    .ymyl_snapshots/<slug>.meta.json  metadata (last fetch, hash, url)
    .ymyl_snapshots/_report.md        human-readable diff report (latest run)

This script does NOT use the WebFetch tool (which lives in the agent runtime)
— it uses urllib so the script is portable to GitHub Actions, cron, or
manual invocation. The agent's monthly refresh agent (Layer 3) handles the
LLM-driven verification of whether changes affect article claims.

Environment notes:
    - Production target: GitHub Actions runner (.github/workflows/ymyl-source-
      watcher.yml fires weekly). Standard cert chain works there out of the box.
    - Local Windows note: if you see "unable to get local issuer certificate",
      that's a Windows cert-store issue, not a script issue. Either install
      the certifi package (the script picks it up automatically) or skip
      local testing — the GitHub Actions schedule handles real verification.

Exit codes:
    0 = no material change OR --init mode
    1 = material change detected (CI/cron should surface)
    2 = fetch failure (network issue — retry)
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path

try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = REPO_ROOT / ".ymyl_snapshots"

# Primary sources monitored. Each entry: (slug, url, label).
SOURCES = [
    (
        "irs-25c",
        "https://www.irs.gov/credits-deductions/energy-efficient-home-improvement-credit",
        "IRS Section 25C Energy Efficient Home Improvement Credit",
    ),
    (
        "irs-25d",
        "https://www.irs.gov/credits-deductions/residential-clean-energy-credit",
        "IRS Section 25D Residential Clean Energy Credit",
    ),
    (
        "energystar-federal-tax-credits",
        "https://www.energystar.gov/about/federal-tax-credits",
        "ENERGY STAR Federal Tax Credits",
    ),
    (
        "epa-section-608",
        "https://www.epa.gov/section608",
        "EPA Section 608 Refrigerant Handling",
    ),
    (
        "epa-aim-tech-transitions",
        "https://www.epa.gov/climate-hfcs-reduction/regulatory-actions-technology-transitions",
        "EPA AIM Act Technology Transitions Program",
    ),
    (
        "doe-heat-pump-systems",
        "https://www.energy.gov/energysaver/heat-pump-systems",
        "DOE Heat Pump Systems",
    ),
    (
        "doe-home-upgrades",
        "https://www.energy.gov/save/home-upgrades",
        "DOE Home Upgrades / HEAR Portal",
    ),
    (
        "pacenation-pace-programs",
        "https://www.pacenation.org/pace-programs/",
        "PACENation PACE Programs (industry advocacy — watch for MO SB736 framing)",
    ),
]

USER_AGENT = "CoolCallPro-YMYL-Watcher/1.0 (+https://coolcallpro.com)"


def fetch(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
        raw = resp.read()
        ctype = resp.headers.get("Content-Type", "")
    enc_match = re.search(r"charset=([\w-]+)", ctype, re.I)
    encoding = enc_match.group(1) if enc_match else "utf-8"
    return raw.decode(encoding, errors="replace")


def extract_body_text(html: str) -> str:
    """Strip HTML to comparable body text. Removes script/style/nav so we
    don't trigger on cookie-banner or analytics shuffles."""
    html = re.sub(r"<(script|style|nav|header|footer|noscript)[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_for_diff(text: str) -> list[str]:
    """Produce a list of comparable lines. Volatile timestamp/session
    fragments removed so the diff doesn't fire on every refresh."""
    text = re.sub(r"\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|UTC|EST|EDT|GMT)?\b", "", text, flags=re.I)
    text = re.sub(r"sessionid=[A-Za-z0-9]+", "", text)
    text = re.sub(r"csrf[_-]?token=[A-Za-z0-9]+", "", text, flags=re.I)
    # Sentence-grain comparison — coarser than character-level, less noisy
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 30]


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def snapshot_paths(slug: str) -> tuple[Path, Path]:
    return SNAPSHOT_DIR / f"{slug}.txt", SNAPSHOT_DIR / f"{slug}.meta.json"


def write_snapshot(slug: str, url: str, label: str, text: str) -> None:
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    txt_path, meta_path = snapshot_paths(slug)
    txt_path.write_text(text, encoding="utf-8")
    meta_path.write_text(
        json.dumps(
            {
                "slug": slug,
                "url": url,
                "label": label,
                "fetched_at": datetime.utcnow().isoformat() + "Z",
                "fetched_date": date.today().isoformat(),
                "hash": hash_text(text),
                "byte_length": len(text),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def read_previous_snapshot(slug: str) -> tuple[str | None, dict | None]:
    txt_path, meta_path = snapshot_paths(slug)
    if not txt_path.exists() or not meta_path.exists():
        return None, None
    return txt_path.read_text(encoding="utf-8"), json.loads(meta_path.read_text(encoding="utf-8"))


def diff_summary(prev: str, curr: str) -> tuple[int, str]:
    prev_lines = normalize_for_diff(prev)
    curr_lines = normalize_for_diff(curr)
    differ = list(
        difflib.unified_diff(
            prev_lines, curr_lines, lineterm="", fromfile="previous", tofile="current", n=1,
        )
    )
    added = [ln for ln in differ if ln.startswith("+") and not ln.startswith("+++")]
    removed = [ln for ln in differ if ln.startswith("-") and not ln.startswith("---")]
    material = len(added) + len(removed)
    summary_lines = []
    if added:
        summary_lines.append(f"  + Added ({len(added)} line(s)):")
        for ln in added[:6]:
            summary_lines.append(f"      {ln[:200]}")
        if len(added) > 6:
            summary_lines.append(f"      ... and {len(added) - 6} more")
    if removed:
        summary_lines.append(f"  - Removed ({len(removed)} line(s)):")
        for ln in removed[:6]:
            summary_lines.append(f"      {ln[:200]}")
        if len(removed) > 6:
            summary_lines.append(f"      ... and {len(removed) - 6} more")
    return material, "\n".join(summary_lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", help="Snapshot only; do not diff")
    parser.add_argument("--quiet", action="store_true", help="Suppress no-change output")
    args = parser.parse_args()

    SNAPSHOT_DIR.mkdir(exist_ok=True)
    report_lines = [f"# YMYL Primary-Source Watcher Report — {date.today().isoformat()}", ""]
    material_changes = []
    fetch_errors = []

    for slug, url, label in SOURCES:
        try:
            html = fetch(url)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            fetch_errors.append((slug, url, str(exc)))
            report_lines.append(f"## ERROR  {label}\n  URL: {url}\n  {exc}\n")
            continue

        curr_text = extract_body_text(html)
        prev_text, _meta = read_previous_snapshot(slug)

        if args.init or prev_text is None:
            write_snapshot(slug, url, label, curr_text)
            report_lines.append(f"## SNAPSHOT  {label}\n  URL: {url}\n  Initial snapshot taken ({len(curr_text):,} chars).\n")
            continue

        if hash_text(curr_text) == hash_text(prev_text):
            if not args.quiet:
                report_lines.append(f"## OK  {label}\n  URL: {url}\n  No change.\n")
            continue

        material, summary = diff_summary(prev_text, curr_text)
        if material == 0:
            if not args.quiet:
                report_lines.append(f"## OK  {label}\n  URL: {url}\n  Hash differs but no material text delta (likely whitespace).\n")
        else:
            material_changes.append((slug, label, url, material))
            report_lines.append(f"## CHANGE  {label}\n  URL: {url}\n  Material delta: {material} line(s).\n{summary}\n")
            write_snapshot(slug, url, label, curr_text)

    report_lines.append("---")
    report_lines.append(f"Sources monitored: {len(SOURCES)}")
    report_lines.append(f"Material changes: {len(material_changes)}")
    report_lines.append(f"Fetch errors: {len(fetch_errors)}")

    report_path = SNAPSHOT_DIR / "_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print("\n".join(report_lines))

    if fetch_errors and not material_changes:
        return 2
    if material_changes:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
