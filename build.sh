#!/usr/bin/env bash
# Cloudflare Pages build script.
# Copies only the deployable files to _dist/ — nothing else is served to the web.
#
# Source files (Python generators, xlsx data, internal docs, .agents, docs/)
# remain at repo root but are NEVER served by Cloudflare Pages.

set -euo pipefail

OUT="_dist"

echo "Building Cloudflare Pages deploy directory at ./$OUT"

# Layer 1 (deploy-time guarantee): regenerate _redirects from current HTML on disk.
# This is the authoritative pass — even a commit that bypassed the pre-commit hook
# cannot ship a stale redirects map, because every deploy regenerates from the
# actual files in the build context. Fails the build if regen fails.
PYTHON="$(command -v python3 || command -v python || true)"
if [ -z "$PYTHON" ]; then
    echo "ERROR: Python not found in build environment. Cannot regenerate _redirects."
    echo "Fix: ensure Cloudflare Pages build image v2 (has Python 3) is selected."
    exit 1
fi
echo "Regenerating _redirects from current HTML files..."
"$PYTHON" scripts/regenerate_redirects.py

# Layer 1 (cont): filter sitemap-images.xml to entries whose location page exists.
# Drift here sends Google Image Search dead <loc> URLs and degrades sitemap trust.
echo "Filtering sitemap-images.xml to deployed pages only..."
"$PYTHON" scripts/clean_sitemap_images.py

# Fresh output directory
rm -rf "$OUT"
mkdir -p "$OUT"

# Public folders
cp -r css js fonts images articles locations "$OUT/"

# Public root-level HTML pages
cp -f \
  index.html about.html contact.html articles.html costs.html emergency.html safety.html \
  privacy.html terms.html disclaimer.html advertising-disclosure.html author-gyanesh.html \
  image-credits.html 404.html locations.html \
  "$OUT/"

# All article-*.html pages at root
cp -f article-*.html "$OUT/"

# Static assets and config
cp -f favicon.ico favicon.svg "$OUT/"
cp -f _redirects _headers sitemap.xml sitemap-images.xml robots.txt llms.txt "$OUT/"

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
