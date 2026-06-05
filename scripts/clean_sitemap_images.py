"""
Filter sitemap-images.xml to entries whose target location page actually deploys.

Why it exists
-------------
sitemap-images.xml was built from the 201-city xlsx but only 166 cities
have `City Page Published = Yes` in xlsx and actually deploy to the site.
The 35-entry drift sends Google Image Search 35 <loc> URLs that 404,
which Search Console flags as "Page not indexed (404)" and degrades the
overall image-sitemap trust signal.

Filter (not regenerate). The per-entry Wikimedia attribution data (title,
caption, license URL) is unique per city and cannot be recomputed from
HTML on disk. We keep blocks whose location page is tracked in git;
drop blocks whose page is missing.

Auto-invoked from:
  - build.sh (Cloudflare Pages deploy-time backstop -- Layer 1)
  - scripts/pre-commit (commit-time sync -- Layer 2, only when HTML A/D/R)

Idempotent. Safe to re-run.
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
SITEMAP = ROOT / "sitemap-images.xml"

# Match the loc -> derived slug for one <url>...</url> block
URL_BLOCK_RE = re.compile(r"  <url>.*?</url>\n", re.DOTALL)
LOC_RE = re.compile(r"<loc>https://coolcallpro\.com/locations/([^<]+)</loc>")


def tracked_location_slugs() -> set[str]:
    """Slug set of every git-tracked locations/*.html (without the .html suffix)."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "locations/*.html"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        slugs = {
            Path(line).stem
            for line in result.stdout.splitlines()
            if line.strip()
        }
        if slugs:
            return slugs
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    # Fallback: filesystem (used outside git contexts)
    return {p.stem for p in (ROOT / "locations").glob("*.html")}


def main() -> int:
    if not SITEMAP.exists():
        print(f"WARN: {SITEMAP} does not exist; nothing to clean")
        return 0

    original = SITEMAP.read_text(encoding="utf-8")
    valid_slugs = tracked_location_slugs()

    kept_blocks = []
    dropped: list[str] = []

    for block in URL_BLOCK_RE.findall(original):
        m = LOC_RE.search(block)
        if not m:
            # <url> block without a /locations/ path -- keep verbatim (defensive)
            kept_blocks.append(block)
            continue
        slug = m.group(1)
        if slug in valid_slugs:
            kept_blocks.append(block)
        else:
            dropped.append(slug)

    # Find the header (everything before the first <url> block)
    header_end = original.find("  <url>")
    if header_end == -1:
        print("ERROR: malformed sitemap-images.xml (no <url> blocks)")
        return 1
    header = original[:header_end]
    # Find the footer (everything from the last </url> onwards)
    last_url_close = original.rfind("</url>") + len("</url>") + 1  # +1 for \n
    footer = original[last_url_close:]

    new_content = header + "".join(kept_blocks) + footer
    SITEMAP.write_text(new_content, encoding="utf-8", newline="\n")

    print(f"Wrote {SITEMAP}: kept {len(kept_blocks)} entries, dropped {len(dropped)}")
    if dropped:
        print(f"  Dropped slugs ({len(dropped)}):")
        for s in dropped[:10]:
            print(f"    {s}")
        if len(dropped) > 10:
            print(f"    ... and {len(dropped) - 10} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
