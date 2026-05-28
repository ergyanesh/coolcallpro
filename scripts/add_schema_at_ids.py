#!/usr/bin/env python3
"""
Add @id-based author/publisher schema references across all article HTML files.

Replaces the inline Person + Organization objects in Article schema with
@id references pointing at the canonical sources:
- Person: https://coolcallpro.com/author-gyanesh (lives on author-gyanesh.html)
- Organization: https://coolcallpro.com/#organization (lives on index.html)

Idempotent: safe to re-run. Skips blocks already using @id references.

Scope:
- Root: article-*.html (every file matching the pattern)
- Subdir: articles/*.html

Skips: author-gyanesh.html (canonical Person source), index.html (canonical
Organization source), costs.html (handled separately because of @graph).

Run from repo root: python scripts/add_schema_at_ids.py [--dry-run]
"""

import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

PERSON_ID = "https://coolcallpro.com/author-gyanesh"
ORG_ID = "https://coolcallpro.com/#organization"


def find_matching_brace(text, start_idx):
    """Given text and the index of an opening '{', return index of matching '}'."""
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


def is_already_at_id_only(obj_text: str) -> bool:
    """True iff the object text contains @id and nothing else of substance."""
    # Strip whitespace and braces
    inner = obj_text.strip().lstrip('{').rstrip('}').strip()
    # Should be just `"@id": "..."` (possibly with surrounding ws)
    return bool(re.fullmatch(r'\s*"@id"\s*:\s*"[^"]+"\s*', inner))


def replace_field_object(text: str, field_name: str, replacement_value: str):
    """Replace every occurrence of `"<field>": { ... }` with `"<field>": <replacement_value>`.
    Skips occurrences already in @id-only form.

    Right-to-left pass: collect all match positions first, then apply replacements
    from the end so earlier offsets remain valid.
    """
    pattern = re.compile(r'"' + re.escape(field_name) + r'"\s*:\s*\{')

    # Collect (match_start, open_idx, close_idx) tuples
    spans = []
    for m in pattern.finditer(text):
        open_idx = text.index('{', m.start())
        close_idx = find_matching_brace(text, open_idx)
        spans.append((m.start(), open_idx, close_idx))

    count = 0
    # Apply from end to start so earlier indexes remain valid.
    for match_start, open_idx, close_idx in reversed(spans):
        obj_text = text[open_idx:close_idx + 1]
        if is_already_at_id_only(obj_text):
            continue  # idempotent skip
        new_field_text = '"' + field_name + '": ' + replacement_value
        text = text[:match_start] + new_field_text + text[close_idx + 1:]
        count += 1
    return text, count


def process_file(path: Path, dry_run: bool):
    original = path.read_text(encoding='utf-8')
    new_text = original

    new_text, n_author = replace_field_object(
        new_text, 'author',
        '{"@id": "' + PERSON_ID + '"}'
    )
    new_text, n_publisher = replace_field_object(
        new_text, 'publisher',
        '{"@id": "' + ORG_ID + '"}'
    )

    if new_text == original:
        return 0, 0, False
    if not dry_run:
        path.write_text(new_text, encoding='utf-8')
    return n_author, n_publisher, True


def main():
    dry_run = '--dry-run' in sys.argv

    targets = []
    targets.extend(sorted(REPO_ROOT.glob('article-*.html')))
    targets.extend(sorted((REPO_ROOT / 'articles').glob('*.html')))

    skip = {'author-gyanesh.html', 'index.html', 'costs.html'}
    targets = [p for p in targets if p.name not in skip]

    total_author = 0
    total_publisher = 0
    files_changed = 0

    for path in targets:
        n_author, n_publisher, changed = process_file(path, dry_run)
        if changed:
            files_changed += 1
            total_author += n_author
            total_publisher += n_publisher
            print(f"  {path.relative_to(REPO_ROOT)}: author={n_author}, publisher={n_publisher}")

    mode = "DRY-RUN (no writes)" if dry_run else "WRITTEN"
    print(f"\n{mode} | files scanned: {len(targets)} | files changed: {files_changed} | author replaced: {total_author} | publisher replaced: {total_publisher}")


if __name__ == '__main__':
    main()
