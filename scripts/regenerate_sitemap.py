"""
Regenerate sitemap.xml from the actual set of git-tracked HTML files.

Why it exists
-------------
sitemap.xml was hand-maintained and silently drifted: as of 2026-06-13 it was
13 days stale (lastmod 2026-05-24) and missing 4 live articles shipped this
week (gas-leak-vs-co-leak, heat-pump-sizing, hvac-maintenance-essentials,
should-i-switch-to-heat-pump). Google relies on sitemap.xml to prioritize
crawl + discover newly-published pages; staleness slows indexation and
contributes to "Discovered, currently not indexed" status.

Same Layer 1 + Layer 2 design as _redirects and sitemap-images.xml:

Layer 1 (deploy-time guarantee): build.sh regenerates sitemap.xml from
git-tracked HTML before deploying. Even commits that bypass the pre-commit
hook ship a current sitemap.

Layer 2 (commit-time hygiene): pre-commit regenerates whenever a tracked
HTML file is Added/Deleted/Renamed.

Source of truth: `git ls-files '*.html'` (tracked only). Untracked WIP HTML
in the working tree does NOT leak into sitemap.

Lastmod strategy: use the file's last git commit date — accurate to when
the page actually changed. Falls back to today if git history unavailable.

Filename categorization decides ordering (mirrors the original hand-curated
grouping in sitemap.xml: homepage, core service pages, articles hub, then
articles, then locations, then legal/utility, then 404 excluded).
"""

import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
SITEMAP = ROOT / "sitemap.xml"
BASE = "https://coolcallpro.com"

# Files that must NEVER appear in the sitemap (these would otherwise be
# globbed in because they're tracked HTML).
EXCLUDED_STEMS = {
    "404",                       # error page; Google should never index
    "location-template",         # generator templates (also Disallow'd in robots.txt)
    "cost-city-template",
}

# Files that ALWAYS appear at the top of the sitemap in a curated order.
# These are the high-priority pages that should be crawled first.
PRIORITY_ORDER = [
    ("",                         "Homepage"),                # index.html -> /
    ("emergency",                "Core Service Pages"),
    ("costs",                    None),
    ("safety",                   None),
    ("articles",                 "Articles Hub"),
    ("locations",                "Locations Hub"),
    ("about",                    "Company Pages"),
    ("contact",                  None),
    ("author-gyanesh",           "Author"),
    ("image-credits",            "Attribution"),
]

# Files that go LAST (legal / utility).
LEGAL_STEMS = {"privacy", "terms", "disclaimer", "advertising-disclosure"}


def tracked_html() -> list[str]:
    """All .html files git is tracking, repo-relative. Falls back to glob if no git."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.html"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if files:
            return files
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    # Fallback: glob the filesystem
    files = [f.name for f in ROOT.glob("*.html")]
    for f in (ROOT / "articles").glob("*.html"):
        files.append(f"articles/{f.name}")
    for f in (ROOT / "locations").glob("*.html"):
        files.append(f"locations/{f.name}")
    return files


def git_last_modified(rel_path: str) -> str:
    """Return YYYY-MM-DD of the file's last git commit; today if unavailable."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", rel_path],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        s = result.stdout.strip()
        if s:
            return s
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return date.today().isoformat()


def path_to_url(rel_path: str) -> str:
    """articles/foo.html -> https://coolcallpro.com/articles/foo"""
    stem = rel_path[:-5] if rel_path.endswith(".html") else rel_path
    if stem == "index":
        return f"{BASE}/"
    return f"{BASE}/{stem}"


def categorize(rel_path: str) -> tuple[int, str, str]:
    """
    Return (priority_bucket, group_label, stem) for ordering.

    Buckets:
      0 = Homepage (index)
      1 = Curated priority pages (emergency, costs, safety, articles, locations, etc.)
      2 = Individual articles (articles/*.html + root article-*.html)
      3 = Location pages (locations/*.html)
      4 = Legal / utility (privacy, terms, etc.)
      9 = Anything else (sorted alphabetically at the end)
    """
    if rel_path == "index.html":
        return (0, "Homepage", "")
    stem = rel_path[:-5] if rel_path.endswith(".html") else rel_path

    # Top-priority curated pages (and their grouping)
    priority_stems = {p[0] for p in PRIORITY_ORDER}
    if stem in priority_stems:
        # Preserve curated order
        position = next(i for i, p in enumerate(PRIORITY_ORDER) if p[0] == stem)
        return (1, "Priority", f"{position:02d}_{stem}")

    # Article pages
    if rel_path.startswith("articles/") or rel_path.startswith("article-"):
        return (2, "Articles", rel_path)

    # Location pages
    if rel_path.startswith("locations/"):
        return (3, "Locations", rel_path)

    # Legal / utility
    if stem in LEGAL_STEMS:
        return (4, "Legal", stem)

    # Anything else (shouldn't normally exist)
    return (9, "Other", stem)


def render_url_entry(url: str, lastmod: str, indent: str = "  ") -> str:
    return (
        f"{indent}<url>\n"
        f"{indent}  <loc>{url}</loc>\n"
        f"{indent}  <lastmod>{lastmod}</lastmod>\n"
        f"{indent}</url>\n"
    )


def main() -> int:
    files = tracked_html()
    if not files:
        print("ERROR: no tracked HTML files found.", file=sys.stderr)
        return 1

    # Filter out excluded stems
    files = [f for f in files if f[:-5] not in EXCLUDED_STEMS]

    # Build (bucket, group, sortkey, url, lastmod) tuples
    entries = []
    for rel in files:
        bucket, group, sortkey = categorize(rel)
        url = path_to_url(rel)
        lastmod = git_last_modified(rel)
        entries.append((bucket, group, sortkey, url, lastmod))

    # Sort: bucket asc, then sortkey asc
    entries.sort(key=lambda t: (t[0], t[2]))

    # Render with section headings (only when bucket changes)
    out = ['<?xml version="1.0" encoding="UTF-8"?>\n',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n\n']
    last_bucket = None
    headings = {
        0: "Homepage",
        1: "Core Pages",
        2: "Articles",
        3: "Locations",
        4: "Legal / Utility",
        9: "Other",
    }
    for bucket, _group, _sortkey, url, lastmod in entries:
        if bucket != last_bucket:
            out.append(f"  <!-- {headings.get(bucket, 'Other')} -->\n")
            last_bucket = bucket
        out.append(render_url_entry(url, lastmod))
    out.append("\n</urlset>\n")

    SITEMAP.write_text("".join(out), encoding="utf-8", newline="\n")
    print(f"Wrote {SITEMAP} with {len(entries)} URLs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
