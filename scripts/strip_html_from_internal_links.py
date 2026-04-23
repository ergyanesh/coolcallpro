"""
One-off: remove .html suffixes from internal href attributes site-wide.

Why: the site's _redirects file 301s every /path.html -> /path, and every
<link rel="canonical"> already points at the clean URL. But 7,514
internal links across the site HTML still use <a href="...X.html">.

Google sees those internal links and keeps the .html versions visible in
search (GSC showed both /locations/minneapolis-mn.html at 2,416 impressions
AND /locations/minneapolis-mn at 597 impressions — two listings for what
should be one canonical page). Cleaning up internal links accelerates
Google's canonical consolidation.

What it does
------------
Replaces every href="<internal-path>.html" with href="<internal-path>"
in every site HTML file. External URLs (http://, https://, mailto:, tel:,
javascript:) and fragment-only anchors (#...) are left untouched.

Byte-preserving (newline="" preserves CRLF), idempotent (already-cleaned
files produce zero replacements on a re-run).

Scope:
  - All .html files in the repo root AND articles/, locations/ subdirs.
  - Excludes: _dist/, _snapshot/, .playwright-mcp/, deploy*/ folders,
    the GSC export folder, and any *-snapshot*/ leftovers.

Run: python scripts/strip_html_from_internal_links.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Directories to skip entirely
SKIP_DIR_PATTERNS = (
    "_dist", "_snapshot", ".playwright-mcp", "deploy ",
    "coolcallpro.com-", ".git", "node_modules",
)

# Match: href="path_that_isnt_external_or_fragment.html"
# The negative lookahead ensures we don't match http://, https://, mailto:,
# tel:, javascript:, or fragment-only (#...) hrefs.
LINK_PAT = re.compile(
    r'href="(?!https?://|mailto:|tel:|javascript:|#)([^"]+)\.html(#[^"]*)?"'
)


def should_process(path: Path) -> bool:
    s = str(path).replace("\\", "/")
    for skip in SKIP_DIR_PATTERNS:
        if f"/{skip}" in s or s.startswith(skip):
            return False
    return True


def clean_file(path: Path) -> tuple[int, int]:
    """Returns (replacements, size_delta_bytes)."""
    with path.open("r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    original_len = len(text)

    def _replace(m):
        # Group 1 = path-without-.html; Group 2 = optional #fragment
        path_part = m.group(1)
        fragment = m.group(2) or ""
        return f'href="{path_part}{fragment}"'

    new_text, n = LINK_PAT.subn(_replace, text)
    if n == 0:
        return 0, 0

    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(new_text)
    return n, len(new_text) - original_len


def main() -> int:
    files_touched = 0
    total_replacements = 0
    biggest = []
    for path in ROOT.rglob("*.html"):
        if not should_process(path):
            continue
        n, _ = clean_file(path)
        if n > 0:
            files_touched += 1
            total_replacements += n
            biggest.append((n, path.relative_to(ROOT)))

    biggest.sort(reverse=True)
    print(f"Files touched:      {files_touched}")
    print(f"Total replacements: {total_replacements}")
    if biggest:
        print("\nTop 10 files by replacement count:")
        for n, p in biggest[:10]:
            print(f"  {n:4d}  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
