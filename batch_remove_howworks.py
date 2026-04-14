#!/usr/bin/env python3
"""
One-time batch script: Remove "How It Works" section and FAQ CTA
from all existing location pages (city + state hub).

Changes per file:
1. Removes the "How It Works" jump link + its preceding dot separator from hero
2. Removes the entire <!-- How It Works --> section (dark bg, 3 step cards, CTA)
3. Removes the FAQ section CTA button (div below FAQ accordion)

Run: python batch_remove_howworks.py
      python batch_remove_howworks.py --dry-run   # preview only
"""

import os
import re
import sys

LOCATIONS_DIR = "locations"


def patch_file(filepath, dry_run=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. Remove "How It Works" jump link + preceding dot separator
    # Pattern: <span class="jump-link-dot"...>bullet</span>\n...<a href="#how-it-works"...>How It Works</a>\n...<span class="jump-link-dot"...>bullet</span>
    # We need to remove the link AND one of the two surrounding dot separators
    # Remove: dot + How It Works link (keep the dot before FAQs)
    content = re.sub(
        r'\s*<a href="#how-it-works" class="jump-link"[^>]*>How It Works</a>\s*'
        r'<span class="jump-link-dot"[^>]*>[^<]*</span>',
        '',
        content
    )

    # 2. Remove entire How It Works section
    # From "    <!-- How It Works -->" to the closing "</section>" before "<!-- FAQs -->"
    content = re.sub(
        r'\s*<!-- How It Works -->.*?</section>\s*(?=\s*<!-- FAQs -->)',
        '\n',
        content,
        flags=re.DOTALL
    )

    # 3. Remove FAQ section CTA (the Call Now button below the FAQ accordion)
    # It's inside a <div style="text-align: center; margin-top: 32px;"> right before
    # the closing </div></div></section> of the FAQ section
    content = re.sub(
        r'\s*<div style="text-align: center; margin-top: 32px;">\s*'
        r'<a href="tel:\+18445821795" class="btn btn-primary btn-lg btn-vibrate">'
        r'.*?</a>\s*</div>',
        '',
        content,
        flags=re.DOTALL
    )

    if content == original:
        return False  # no changes

    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return True


def main():
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("=== DRY RUN — no files will be modified ===\n")

    files = sorted(os.listdir(LOCATIONS_DIR))
    patched = 0
    skipped = 0
    errors = []

    for fname in files:
        if not fname.endswith('.html'):
            continue

        filepath = os.path.join(LOCATIONS_DIR, fname)
        try:
            changed = patch_file(filepath, dry_run)
            if changed:
                print(f"  {'WOULD PATCH' if dry_run else 'PATCHED'}: {fname}")
                patched += 1
            else:
                print(f"  SKIP (no changes needed): {fname}")
                skipped += 1
        except Exception as e:
            print(f"  ERROR: {fname} — {e}")
            errors.append(fname)

    print(f"\nDone. Patched: {patched}, Skipped: {skipped}, Errors: {len(errors)}")
    if errors:
        print(f"Error files: {errors}")


if __name__ == '__main__':
    main()
