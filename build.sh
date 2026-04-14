#!/usr/bin/env bash
# Cloudflare Pages build script.
# Copies only the deployable files to _dist/ — nothing else is served to the web.
#
# Source files (Python generators, xlsx data, internal docs, .agents, docs/)
# remain at repo root but are NEVER served by Cloudflare Pages.

set -euo pipefail

OUT="_dist"

echo "Building Cloudflare Pages deploy directory at ./$OUT"

# Fresh output directory
rm -rf "$OUT"
mkdir -p "$OUT"

# Public folders
cp -r css js images articles locations "$OUT/"

# Public root-level HTML pages
cp -f \
  index.html about.html contact.html articles.html costs.html emergency.html safety.html \
  privacy.html terms.html disclaimer.html advertising-disclosure.html author-gyanesh.html \
  404.html locations.html \
  "$OUT/"

# All article-*.html pages at root
cp -f article-*.html "$OUT/"

# Static assets and config
cp -f favicon.ico favicon.svg "$OUT/"
cp -f _redirects sitemap.xml robots.txt "$OUT/"

# Summary
echo ""
echo "=== Build summary ==="
echo "HTML files in root:     $(ls "$OUT"/*.html | wc -l)"
echo "Article pages:          $(ls "$OUT"/article-*.html 2>/dev/null | wc -l)"
echo "articles/ subdirectory: $(ls "$OUT"/articles/*.html 2>/dev/null | wc -l)"
echo "locations/ pages:       $(ls "$OUT"/locations/*.html | wc -l)"
echo "Images:                 $(ls "$OUT"/images/ | wc -l)"
echo "Total files:            $(find "$OUT" -type f | wc -l)"
echo ""
echo "Source files (Python, xlsx, MD, scripts) are NOT included in $OUT — they stay at repo root and are not exposed."
