#!/usr/bin/env python3
"""
Add @id-based Organization references across all location pages
(state hubs + city pages).

Two structural changes per page:

1. Main Organization block (top-level in @graph): inject
   `"@id": "https://coolcallpro.com/#organization",` immediately after
   `"@type": "Organization",`.

2. Service.provider inline Organization: replace the inline object
   `"provider": { "@type": "Organization", ... }` with the @id reference
   `"provider": { "@id": "https://coolcallpro.com/#organization" }`.
   The inline Organization data on the Service is purely a duplicate of the
   main Organization block on the same page.

Idempotent: detects already-@id'd blocks and skips them.

Run from repo root: python scripts/add_schema_at_ids_locations.py [--dry-run]
"""

import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

ORG_ID = "https://coolcallpro.com/#organization"
PROVIDER_REPLACEMENT = '"provider": { "@id": "' + ORG_ID + '" }'


def find_matching_brace(text, start_idx):
    depth = 0
    i = start_idx
    in_string = False
    escape = False
    while i < len(text):
        c = text[i]
        if escape:
            escape = False
            i += 1
            continue
        if c == '\\':
            escape = True
            i += 1
            continue
        if c == '"':
            in_string = not in_string
            i += 1
            continue
        if in_string:
            i += 1
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"Unmatched brace starting at index {start_idx}")


def inject_at_id_in_main_org(text):
    """Find each top-level Organization block (inside @graph, not nested under
    provider) and add @id immediately after @type. Idempotent."""
    # Pattern: "@type": "Organization", followed by whitespace then "name"
    # (top-level orgs all start with name immediately after type).
    pattern = re.compile(r'(("@type":\s*"Organization",)(\s*)("name":\s*"Cool Call Pro"))')

    count = 0
    def sub(m):
        nonlocal count
        full = m.group(0)
        # Look at the small context BEFORE this match to detect if @id is already present
        # We track via the parent function for simplicity; here we just inject
        # and let the outer scan detect existing @id.
        count += 1
        type_line = m.group(2)  # "@type": "Organization",
        ws = m.group(3)         # whitespace + indentation before "name"
        name_line = m.group(4)  # "name": "Cool Call Pro"
        return type_line + ws + '"@id": "' + ORG_ID + '",' + ws + name_line

    # First, count how many already have @id directly before the match (skip those).
    # Simpler: scan from beginning, use finditer + manual replace, skipping if @id present.
    new_text = text
    spans = list(pattern.finditer(new_text))
    inserted = 0
    # Right-to-left so positions stay valid
    for m in reversed(spans):
        # Examine 100 chars around the match: is "@id" already adjacent to this Organization?
        ctx_start = max(0, m.start() - 50)
        ctx_end = min(len(new_text), m.end() + 200)
        ctx = new_text[ctx_start:ctx_end]
        # Look between "Organization" and "name" for an @id key
        type_idx = ctx.find('"Organization"')
        name_idx = ctx.find('"name":', type_idx if type_idx >= 0 else 0)
        if type_idx >= 0 and name_idx > type_idx:
            between = ctx[type_idx:name_idx]
            if '"@id"' in between:
                continue  # already has @id between type and name
        # Inject
        type_line = m.group(2)
        ws = m.group(3)
        name_line = m.group(4)
        new_content = type_line + ws + '"@id": "' + ORG_ID + '",' + ws + name_line
        new_text = new_text[:m.start()] + new_content + new_text[m.end():]
        inserted += 1
    return new_text, inserted


def replace_provider_org(text):
    """Replace `"provider": { "@type": "Organization", ... }` with
    `"provider": { "@id": "..." }`. Returns (text, count).
    Idempotent: skips providers that are already @id-only refs."""
    pattern = re.compile(r'"provider"\s*:\s*\{')
    spans = []
    for m in pattern.finditer(text):
        open_idx = text.index('{', m.start())
        close_idx = find_matching_brace(text, open_idx)
        spans.append((m.start(), open_idx, close_idx))

    count = 0
    for match_start, open_idx, close_idx in reversed(spans):
        obj_text = text[open_idx:close_idx + 1]
        inner = obj_text.strip().lstrip('{').rstrip('}').strip()
        # Skip if already @id-only
        if re.fullmatch(r'\s*"@id"\s*:\s*"[^"]+"\s*', inner):
            continue
        # Only replace if it's an Organization
        if '"@type"' not in obj_text or '"Organization"' not in obj_text:
            continue
        text = text[:match_start] + PROVIDER_REPLACEMENT + text[close_idx + 1:]
        count += 1
    return text, count


def process_file(path: Path, dry_run: bool):
    original = path.read_text(encoding='utf-8')
    new_text = original

    new_text, n_main = inject_at_id_in_main_org(new_text)
    new_text, n_provider = replace_provider_org(new_text)

    if new_text == original:
        return 0, 0, False
    if not dry_run:
        path.write_text(new_text, encoding='utf-8')
    return n_main, n_provider, True


def main():
    dry_run = '--dry-run' in sys.argv

    targets = sorted((REPO_ROOT / 'locations').glob('*.html'))

    total_main = 0
    total_provider = 0
    files_changed = 0

    for path in targets:
        n_main, n_provider, changed = process_file(path, dry_run)
        if changed:
            files_changed += 1
            total_main += n_main
            total_provider += n_provider
            # print only first 5 and last 5 for brevity
            if files_changed <= 5 or files_changed > len(targets) - 5:
                print(f"  {path.relative_to(REPO_ROOT)}: main={n_main}, provider={n_provider}")
            elif files_changed == 6:
                print("  ...")

    mode = "DRY-RUN (no writes)" if dry_run else "WRITTEN"
    print(f"\n{mode} | files scanned: {len(targets)} | files changed: {files_changed} | main-org @id injected: {total_main} | provider @id-ref'd: {total_provider}")


if __name__ == '__main__':
    main()
