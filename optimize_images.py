"""
Image optimizer — resizes oversized hero images to mobile-friendly dimensions.

Problem being fixed: Playwright-measured baseline showed city/state hero
images averaged 185 KB at 1600x900 (some up to 464 KB). On a 390px-wide
mobile viewport the browser still downloads the full 1600px-wide file,
which destroys LCP on throttled mobile and caps the Lighthouse Mobile
Performance score below 73.

Policy:
    - Target max width: 1280 px (enough for retina 2x on typical 640-px
      content columns). Height scaled to preserve original aspect ratio.
    - WebP quality: 80 (down from 85). Visually indistinguishable at this
      range; saves 20-35% bytes.
    - Files already under 1280 wide AND under 150 KB are left alone.
    - Source files are overwritten in place (no format change).

Scope:
    - images/cities/*.webp  (150 files)
    - images/states/*.webp  (51 files)
    - 3 oversize files in images/ root (manually listed)

Usage:
    python optimize_images.py           # optimize in place
    python optimize_images.py --dry-run # report only, no writes

Safe to run repeatedly — already-optimized files are skipped.
"""

import os
import sys
from pathlib import Path
from PIL import Image


TARGET_WIDTH = 1280
QUALITY = 80
SIZE_THRESHOLD_KB = 150  # only touch files above this size
SKIP_IF_UNDER_WIDTH = 1280

TARGETS = [
    "images/cities",
    "images/states",
]

ROOT_TARGETS = [
    "images/hvac_ac_troubleshooting_pillar.webp",
    "images/hvac_fall_prep.webp",
    "images/hvac_safety.webp",
]


def optimize(path: Path, dry_run: bool = False):
    """Returns (action, before_kb, after_kb) tuple."""
    before_kb = path.stat().st_size // 1024
    img = Image.open(path)
    w, h = img.size

    # Skip already-optimized files
    if w <= SKIP_IF_UNDER_WIDTH and before_kb <= SIZE_THRESHOLD_KB:
        return ("skip", before_kb, before_kb)

    # Compute target dimensions preserving aspect ratio
    if w > TARGET_WIDTH:
        new_w = TARGET_WIDTH
        new_h = round(h * TARGET_WIDTH / w)
        img = img.resize((new_w, new_h), Image.LANCZOS)
    else:
        new_w, new_h = w, h  # keep dimensions, just re-encode at lower quality

    # WebP re-encode requires RGB mode
    if img.mode != "RGB":
        img = img.convert("RGB")

    if dry_run:
        return ("would-optimize", before_kb, None)

    # Save with method=6 for best compression (slower but smaller)
    img.save(path, "webp", quality=QUALITY, method=6)
    after_kb = path.stat().st_size // 1024
    return (f"resize {w}x{h}->{new_w}x{new_h}", before_kb, after_kb)


def walk_dir(d: Path, dry_run: bool):
    if not d.is_dir():
        return {"processed": 0, "skipped": 0, "before_kb": 0, "after_kb": 0}
    stats = {"processed": 0, "skipped": 0, "before_kb": 0, "after_kb": 0}
    for f in sorted(d.iterdir()):
        if f.suffix.lower() != ".webp":
            continue
        action, before, after = optimize(f, dry_run)
        stats["before_kb"] += before
        if action == "skip":
            stats["skipped"] += 1
            stats["after_kb"] += before
            continue
        stats["processed"] += 1
        if after is not None:
            stats["after_kb"] += after
            print(f"  {f.name}: {before} KB -> {after} KB ({action})")
        else:
            print(f"  {f.name}: would optimize ({before} KB, {action})")
    return stats


def main():
    dry = "--dry-run" in sys.argv
    print(f"Image optimizer ({'DRY RUN' if dry else 'WRITING'})")
    print(f"  target max width: {TARGET_WIDTH} px")
    print(f"  quality: {QUALITY}")
    print(f"  skip threshold: >{SIZE_THRESHOLD_KB} KB or >{SKIP_IF_UNDER_WIDTH} px wide")

    total_before = 0
    total_after = 0
    total_processed = 0
    total_skipped = 0

    for d in TARGETS:
        print(f"\n== {d} ==")
        s = walk_dir(Path(d), dry)
        total_before += s["before_kb"]
        total_after += s["after_kb"]
        total_processed += s["processed"]
        total_skipped += s["skipped"]
        print(f"   -> {s['processed']} processed, {s['skipped']} skipped")

    print(f"\n== images/ (specific files) ==")
    for rel in ROOT_TARGETS:
        p = Path(rel)
        if not p.exists():
            print(f"  {rel}: MISSING")
            continue
        action, before, after = optimize(p, dry)
        total_before += before
        if action == "skip":
            total_skipped += 1
            total_after += before
            print(f"  {p.name}: skip ({before} KB)")
            continue
        total_processed += 1
        if after is not None:
            total_after += after
            print(f"  {p.name}: {before} KB -> {after} KB ({action})")
        else:
            print(f"  {p.name}: would optimize ({before} KB, {action})")

    print()
    print("=" * 60)
    saved_kb = total_before - total_after
    saved_pct = round(100 * saved_kb / total_before, 1) if total_before else 0
    print(f"SUMMARY: {total_processed} files processed, {total_skipped} skipped")
    print(f"  Before: {total_before:,} KB ({total_before // 1024} MB)")
    if not dry:
        print(f"  After:  {total_after:,} KB ({total_after // 1024} MB)")
        print(f"  Saved:  {saved_kb:,} KB ({saved_pct}%)")


if __name__ == "__main__":
    main()
