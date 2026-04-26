"""One-shot script: remove deprecated HowTo JSON-LD schema from articles.

Google deprecated HowTo rich results in September 2023 — the schema is no
longer eligible for rich snippets and is treated as a quality regression
signal by some crawlers (per FULL-AUDIT-REPORT.md §4, 2026-04-26).

This script removes only the `<script type="application/ld+json">` blocks
whose top-level `@type` is "HowTo". Any preceding `<!-- HowTo ... -->`
comment marker is also removed. All other JSON-LD blocks (Article,
FAQPage, BreadcrumbList, Organization) are preserved untouched. The
visible HTML step-by-step content stays — only the schema is removed.

Affected files (12 articles, per audit):
    article-fall-prep.html
    article-maintenance.html
    article-spring-ac.html
    article-winter-storm.html
    articles/ac-circuit-breaker-trips.html
    articles/ac-contactor-clicking.html
    articles/ac-freezing-up-in-summer.html
    articles/ac-not-cooling-below-80.html
    articles/complete-ac-troubleshooting-guide.html
    articles/hvac-leaking-water-inside-house.html
    articles/thermostat-blank-ac-wont-start.html
    articles/water-dripping-from-vent.html

Idempotent: re-running on already-cleaned files is a no-op.

Usage:
    python scripts/remove_howto_schema.py
"""

import json
import re
import sys
from pathlib import Path

TARGETS = [
    "article-fall-prep.html",
    "article-maintenance.html",
    "article-spring-ac.html",
    "article-winter-storm.html",
    "articles/ac-circuit-breaker-trips.html",
    "articles/ac-contactor-clicking.html",
    "articles/ac-freezing-up-in-summer.html",
    "articles/ac-not-cooling-below-80.html",
    "articles/complete-ac-troubleshooting-guide.html",
    "articles/hvac-leaking-water-inside-house.html",
    "articles/thermostat-blank-ac-wont-start.html",
    "articles/water-dripping-from-vent.html",
]

# Match a <script type="application/ld+json">...</script> block, capturing
# inner JSON. Non-greedy so it doesn't span multiple script blocks.
SCRIPT_RE = re.compile(
    r'<script\s+type="application/ld\+json">\s*(.*?)\s*</script>',
    re.DOTALL,
)


def is_howto(json_text: str) -> bool:
    """Return True if the JSON's top-level @type is HowTo."""
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        return False
    if isinstance(data, dict):
        return data.get("@type") == "HowTo"
    if isinstance(data, list):
        return any(isinstance(d, dict) and d.get("@type") == "HowTo" for d in data)
    return False


def remove_howto_blocks(text: str) -> tuple[str, int]:
    """Return (new_text, removed_count). Removes HowTo script tags + their
    preceding HTML HowTo comment if any."""
    removed = 0

    # Walk through script tags in REVERSE so removal indices stay valid
    matches = list(SCRIPT_RE.finditer(text))
    for m in reversed(matches):
        if not is_howto(m.group(1)):
            continue

        # Find a preceding `<!-- HowTo...-->` comment within ~120 chars before
        # the script start (allowing whitespace/newlines between).
        block_start = m.start()
        block_end = m.end()
        prefix = text[max(0, block_start - 200):block_start]
        comment_match = re.search(
            r"<!--\s*HowTo[^>]*?-->\s*\Z",
            prefix,
            re.IGNORECASE,
        )
        if comment_match:
            block_start -= len(comment_match.group(0))

        # Also consume one trailing newline + indentation if present, so we
        # don't leave a blank line in the file.
        trailing = re.match(r"[\r\n]+[ \t]*", text[block_end:])
        if trailing:
            block_end += len(trailing.group(0))

        text = text[:block_start] + text[block_end:]
        removed += 1

    return text, removed


def main() -> int:
    total_files = 0
    total_blocks = 0
    skipped = []

    for rel_path in TARGETS:
        path = Path(rel_path)
        if not path.exists():
            skipped.append(f"NOT FOUND: {rel_path}")
            continue
        original = path.read_text(encoding="utf-8")
        new_text, removed = remove_howto_blocks(original)
        if removed == 0:
            skipped.append(f"NO HOWTO: {rel_path} (already clean?)")
            continue
        path.write_text(new_text, encoding="utf-8")
        total_files += 1
        total_blocks += removed
        print(f"  - {rel_path}: removed {removed} HowTo block(s)")

    print()
    print(f"Total: {total_blocks} HowTo block(s) removed across {total_files} file(s)")
    if skipped:
        print()
        print("Skipped:")
        for s in skipped:
            print(f"  {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
