"""
Layer 3 of the YMYL verification system: monthly refresh helper.

Surfaces every article whose YMYL log is approaching staleness (within the
next 14 days), groups the unique CLAIM URLs across all articles by source,
and prints a per-source action plan. An agent (or human) then runs
WebFetch on each unique URL once, compares the live page content to the
article CLAIM text, and either:
  (a) bumps the article's "last verified / next due" dates if the claim
      still holds, or
  (b) surfaces a fix list if the live content has drifted.

This script does NOT touch the network. It is a planning tool — pure
analysis of the existing repo state. Saves WebFetch calls by deduplicating
shared URLs across articles.

Usage:
    python scripts/ymyl_refresh_helper.py             # plan only
    python scripts/ymyl_refresh_helper.py --bump-all  # bump every log to today (use ONLY after verification)

Output:
    .ymyl_refresh_plan.md  human-readable per-source action plan
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLE_GLOBS = ["article-*.html", "articles/*.html"]
NEXT_DUE_THRESHOLD_DAYS = 14  # surface anything due within 14 days


def find_articles() -> list[Path]:
    out: list[Path] = []
    for g in ARTICLE_GLOBS:
        out.extend(REPO_ROOT.glob(g))
    return sorted(out)


def parse_log(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"YMYL VERIFICATION LOG.*?-->", text, re.DOTALL)
    if not m:
        return None
    block = m.group(0)
    last = re.search(r"last verified\s+(\d{4}-\d{2}-\d{2})", block, re.IGNORECASE)
    nxt = re.search(r"next due\s+(\d{4}-\d{2}-\d{2})", block, re.IGNORECASE)
    last_d = datetime.strptime(last.group(1), "%Y-%m-%d").date() if last else None
    nxt_d = datetime.strptime(nxt.group(1), "%Y-%m-%d").date() if nxt else None

    # Parse CLAIM blocks for url + claim summary.
    claim_blocks = re.split(r"(?=CLAIM\s+\d+:)", block)
    claims: list[dict] = []
    for cb in claim_blocks:
        if not re.match(r"CLAIM\s+\d+:", cb):
            continue
        num_match = re.match(r"CLAIM\s+(\d+):\s*(.*)", cb, re.DOTALL)
        if not num_match:
            continue
        num = num_match.group(1)
        # First-line summary
        first_line = re.sub(r"\s+", " ", num_match.group(2)[:140]).strip()
        url_match = re.search(r"URL:\s*(\S+)", cb)
        url = url_match.group(1) if url_match else None
        claims.append({"num": num, "summary": first_line, "url": url})

    return {"path": str(path), "last": last_d, "next": nxt_d, "claims": claims}


def bump_log(path: Path, today: date | None = None) -> bool:
    today = today or date.today()
    new_next = today + timedelta(days=90)
    text = path.read_text(encoding="utf-8")
    new_text = re.sub(
        r"(last verified\s+)\d{4}-\d{2}-\d{2}(\s*,\s*next due\s+)\d{4}-\d{2}-\d{2}",
        rf"\g<1>{today.isoformat()}\g<2>{new_next.isoformat()}",
        text,
        count=1,
        flags=re.IGNORECASE,
    )
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bump-all",
        action="store_true",
        help="Bump every article's last-verified to today + 90 (USE ONLY after re-verification).",
    )
    parser.add_argument(
        "--threshold-days",
        type=int,
        default=NEXT_DUE_THRESHOLD_DAYS,
        help=f"Surface logs due within N days (default: {NEXT_DUE_THRESHOLD_DAYS}).",
    )
    args = parser.parse_args()

    today = date.today()
    horizon = today + timedelta(days=args.threshold_days)

    articles = find_articles()
    if not articles:
        print("No articles found.")
        return 0

    pending_articles = []  # (article_path, log_dict)
    no_log: list[Path] = []
    for p in articles:
        info = parse_log(p)
        if info is None:
            no_log.append(p)
            continue
        if info["next"] is None or info["next"] <= horizon:
            pending_articles.append((p, info))

    # Group claims by URL (or sourceless tag) so we can re-verify each unique
    # URL just once and apply the result across every article that cites it.
    by_url: dict[str, list[tuple[Path, dict]]] = defaultdict(list)
    sourceless_count = 0
    for p, info in pending_articles:
        for claim in info["claims"]:
            url = claim["url"]
            if url:
                by_url[url].append((p, claim))
            else:
                sourceless_count += 1

    if args.bump_all:
        bumped = 0
        for p, _info in pending_articles:
            if bump_log(p, today):
                bumped += 1
        print(f"Bumped {bumped} article logs to last-verified {today}, next-due {today + timedelta(days=90)}.")
        return 0

    lines = [f"# YMYL Refresh Plan — {today.isoformat()}", ""]
    lines.append(f"Articles with YMYL logs: {len(articles) - len(no_log)}")
    lines.append(f"Articles with no YMYL log: {len(no_log)}")
    lines.append(f"Articles due within {args.threshold_days} days: {len(pending_articles)}")
    lines.append(f"Unique primary-source URLs to verify: {len(by_url)}")
    lines.append(f"Claims with no URL (skipped): {sourceless_count}")
    lines.append("")

    if no_log:
        lines.append("## Articles with no YMYL log")
        for p in no_log:
            lines.append(f"- {p.relative_to(REPO_ROOT)}")
        lines.append("")

    if not pending_articles:
        lines.append("All article YMYL logs are fresh (no action required).")
        out = "\n".join(lines)
        Path(REPO_ROOT / ".ymyl_refresh_plan.md").write_text(out, encoding="utf-8")
        print(out)
        return 0

    lines.append("## Per-source verification plan")
    lines.append("")
    lines.append("For each URL below: WebFetch → compare page content to the cited CLAIM(s) →")
    lines.append("if claims still hold, run `python scripts/ymyl_refresh_helper.py --bump-all` →")
    lines.append("if claims have drifted, edit affected articles, then bump dates manually.")
    lines.append("")

    for url, claims in sorted(by_url.items()):
        lines.append(f"### {url}")
        lines.append(f"Cited by {len(claims)} CLAIM(s) across {len(set(p for p, _ in claims))} article(s):")
        for p, claim in claims:
            rel = p.relative_to(REPO_ROOT)
            lines.append(f"- `{rel}` CLAIM {claim['num']}: {claim['summary']}")
        lines.append("")

    lines.append("## Articles by next-due date")
    for p, info in sorted(pending_articles, key=lambda x: x[1]["next"] or date.max):
        rel = p.relative_to(REPO_ROOT)
        nxt = info["next"].isoformat() if info["next"] else "?"
        days = (info["next"] - today).days if info["next"] else "?"
        lines.append(f"- {nxt} ({days}d) — {rel}")

    out = "\n".join(lines)
    Path(REPO_ROOT / ".ymyl_refresh_plan.md").write_text(out, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
