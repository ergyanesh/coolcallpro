"""
Bump <lastmod> on the 17 canonical URLs currently duplicated in GSC.

Why
---
On 2026-04-23 the GSC Pages export showed 17 URLs indexed under BOTH their
clean form and their .html form. The site's redirects work (301 or 308),
but Google hasn't re-crawled the .html URLs to see the redirect yet.
Bumping <lastmod> to today on the clean canonical tells Google the URL
is worth re-crawling -- when Google re-crawls the canonical and follows
internal links away from the .html version, consolidation accelerates.

This script is a one-off for the specific 17 pairs identified on
2026-04-23. Re-running is safe but won't have the same effect (the
lastmod values will bump to whatever "today" is).

List comes from coolcallpro.com-Performance-on-Search-2026-04-23/Pages.csv
(canonical URL = the non-.html side of each duplicate pair).
"""

import re
from datetime import date
from pathlib import Path

SITEMAP = Path(__file__).parent.parent / "sitemap.xml"

DUPLICATE_URLS = [
    "https://coolcallpro.com/about",
    "https://coolcallpro.com/article-hvac-financing",
    "https://coolcallpro.com/article-maintenance",
    "https://coolcallpro.com/article-spring-ac",
    "https://coolcallpro.com/safety",
    "https://coolcallpro.com/locations/brownsville-tx",
    "https://coolcallpro.com/locations/columbia-sc",
    "https://coolcallpro.com/locations/fort-wayne-in",
    "https://coolcallpro.com/locations/kentucky",
    "https://coolcallpro.com/locations/lincoln-ne",
    "https://coolcallpro.com/locations/lubbock-tx",
    "https://coolcallpro.com/locations/mesa-az",
    "https://coolcallpro.com/locations/minneapolis-mn",
    "https://coolcallpro.com/locations/nebraska",
    "https://coolcallpro.com/locations/new-jersey",
    "https://coolcallpro.com/locations/pittsburgh-pa",
    "https://coolcallpro.com/locations/st-louis-mo",
]


def main() -> int:
    today = date.today().isoformat()
    text = SITEMAP.read_text(encoding="utf-8")
    updates = 0
    misses = []
    for url in DUPLICATE_URLS:
        # Match the <url> block containing <loc>url</loc>, replace its <lastmod>
        pat = re.compile(
            r"(<url>\s*<loc>" + re.escape(url) + r"</loc>\s*<lastmod>)[^<]+(</lastmod>)"
        )
        new_text, n = pat.subn(rf"\g<1>{today}\g<2>", text)
        if n == 0:
            misses.append(url)
        else:
            text = new_text
            updates += 1
    SITEMAP.write_text(text, encoding="utf-8", newline="\n")
    print(f"Bumped {updates}/{len(DUPLICATE_URLS)} <lastmod> entries to {today}")
    if misses:
        print("URLs not matched in sitemap (missing or different format):")
        for u in misses:
            print(f"  {u}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
