"""
Materialize the article <-> city linking plan to CSV.

Reads cluster_map.json + article_city_linker.py + cities_updated.xlsx
and writes three human-auditable files:

  1. article_link_plan.csv — one row per planned article:
       slug | cluster | status | 4 cities | 2 state hubs | pillar link | cluster-mate links

  2. city_link_coverage.csv — one row per published city:
       city | state | climate_type | n_articles_linking | article_slugs

  3. LINK_PLAN.md — human-readable landing page explaining the system.

Run any time the roadmap changes (new article added to cluster_map.json, new city
published in xlsx, etc.):

    python generate_link_plan.py

The CSVs are git-tracked snapshots. They are ALWAYS regeneratable from the linker,
so they can never drift from the algorithm — they are the linker's output made
visible. Do NOT hand-edit them; edit cluster_map.json or the linker instead.
"""

import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from article_city_linker import pick_cities, get_state_hubs, load_city_pools


PILLAR_N = 5       # pillars get 5 city links
CLUSTER_N = 4      # cluster articles get 4 city links


def load_cluster_map(path="cluster_map.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_article_rows(cmap):
    """Yield one row per article in cluster_map (pillar + cluster articles)."""
    for cluster_id, cluster in cmap['clusters'].items():
        pillar = cluster['pillar']
        # Pillar row
        yield {
            'slug': pillar['slug'],
            'type': 'pillar',
            'cluster_id': cluster_id,
            'cluster_name': cluster['name'],
            'title': pillar['title'],
            'filename': pillar['filename'],
            'status': pillar['status'],
            'n_cities': PILLAR_N,
        }
        # Cluster article rows
        for art in cluster['articles']:
            yield {
                'slug': art['slug'],
                'type': 'cluster',
                'cluster_id': cluster_id,
                'cluster_name': cluster['name'],
                'title': art['title'],
                'filename': art['path'],
                'status': art.get('status', 'pending'),
                'n_cities': CLUSTER_N,
                'priority': art.get('priority', ''),
                'roadmap_id': art.get('roadmap_id', ''),
            }


def write_article_link_plan(cmap, out_path="article_link_plan.csv"):
    """Write one row per article with its deterministic city picks."""
    rows = list(build_article_rows(cmap))

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'position', 'slug', 'type', 'cluster_id', 'cluster_name',
            'title', 'filename', 'status',
            'city_1', 'city_2', 'city_3', 'city_4', 'city_5',
            'state_hub_1', 'state_hub_2',
            'pillar_link', 'cross_cluster_anchor',
            'priority_rank', 'roadmap_id',
        ])

        # Build cluster_id -> pillar_filename lookup for pillar_link column
        pillar_filenames = {
            cid: c['pillar']['filename']
            for cid, c in cmap['clusters'].items()
        }
        cross_anchors = {
            cid: c['cross_cluster_anchor']['cluster']
            for cid, c in cmap['clusters'].items()
        }

        for i, row in enumerate(rows, start=1):
            cities = pick_cities(row['slug'], row['cluster_id'], row['n_cities'])
            # Pad to 5 city columns so all rows align even if N=4
            city_slugs = [c['slug'] for c in cities] + [''] * (5 - len(cities))
            state_hubs = get_state_hubs(cities, max_hubs=2)
            hub_slugs = [s[0] for s in state_hubs] + [''] * (2 - len(state_hubs))

            if row['type'] == 'pillar':
                pillar_link = '(this IS the pillar)'
            else:
                pillar_link = pillar_filenames.get(row['cluster_id'], '')

            writer.writerow([
                i,
                row['slug'],
                row['type'],
                row['cluster_id'],
                row['cluster_name'],
                row['title'],
                row['filename'],
                row['status'],
                city_slugs[0], city_slugs[1], city_slugs[2], city_slugs[3], city_slugs[4],
                hub_slugs[0], hub_slugs[1],
                pillar_link,
                cross_anchors.get(row['cluster_id'], ''),
                row.get('priority', ''),
                row.get('roadmap_id', ''),
            ])

    return len(rows)


def write_city_coverage(cmap, out_path="city_link_coverage.csv"):
    """Write one row per published city with every article slug that will link to it."""
    pools = load_city_pools()
    city_to_articles = defaultdict(list)

    for row in build_article_rows(cmap):
        cities = pick_cities(row['slug'], row['cluster_id'], row['n_cities'])
        for c in cities:
            city_to_articles[c['slug']].append((row['slug'], row['cluster_id']))

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'city_slug', 'city', 'state', 'climate_type',
            'n_planned_article_links', 'article_slugs_linking_here',
        ])

        for climate, cities in sorted(pools.items()):
            for c in cities:
                linked = city_to_articles.get(c['slug'], [])
                writer.writerow([
                    c['slug'],
                    c['city'],
                    c['state'],
                    c['climate_type'],
                    len(linked),
                    '; '.join(slug for slug, _ in linked),
                ])

    return sum(len(v) for v in pools.values()), city_to_articles


def write_landing_md(cmap, n_articles, n_cities, city_to_articles, out_path="LINK_PLAN.md"):
    """Human-readable overview explaining what the CSVs contain and how to use them."""
    linked_cities = sum(1 for v in city_to_articles.values() if v)
    orphan_cities = n_cities - linked_cities
    max_linked = max((len(v) for v in city_to_articles.values()), default=0)
    avg_linked = (sum(len(v) for v in city_to_articles.values()) / n_cities) if n_cities else 0

    over_linked = sorted(
        [(s, len(v)) for s, v in city_to_articles.items() if len(v) >= 4],
        key=lambda x: -x[1],
    )[:10]

    lines = [
        "# CoolCallPro Link Plan — Deterministic Article↔City Mapping",
        "",
        f"_Auto-generated from `cluster_map.json` + `article_city_linker.py`. Regenerate with `python generate_link_plan.py`._",
        "",
        "## What these files are",
        "",
        "The article→city and city→article mappings for CoolCallPro are **computed deterministically** by `article_city_linker.py`. These CSVs are the materialized output of that algorithm — they exist so you can audit every mapping at a glance instead of having to run the linker for each article.",
        "",
        "**Do NOT hand-edit the CSVs.** If a mapping is wrong, change the underlying inputs:",
        "- Article definitions + cluster assignments → edit `cluster_map.json`",
        "- Climate weights per cluster → edit `CLUSTER_CLIMATE_WEIGHTS` in `article_city_linker.py`",
        "- City list + climate zones → edit `cities_updated.xlsx`",
        "",
        "Then re-run `python generate_link_plan.py` and commit the new CSVs.",
        "",
        "## Files",
        "",
        "| File | What it shows | Rows |",
        "|------|---------------|------|",
        f"| `article_link_plan.csv` | Each planned article → its 4-5 city links + 2 state hubs + pillar link + cross-cluster anchor | {n_articles} |",
        f"| `city_link_coverage.csv` | Each published city → every article slug that will link to it | {n_cities} |",
        f"| `LINK_PLAN.md` (this file) | Human overview + coverage stats | — |",
        "",
        "## Coverage Summary",
        "",
        f"- **Total published cities:** {n_cities}",
        f"- **Cities receiving ≥1 article link:** {linked_cities} ({100*linked_cities/n_cities:.0f}%)",
        f"- **Orphan cities (0 planned article links):** {orphan_cities}",
        f"- **Average article links per city:** {avg_linked:.1f}",
        f"- **Max article links to any one city:** {max_linked}",
        "",
    ]

    if over_linked:
        lines.append("### Cities with 4+ planned article links (watch for crowding)")
        lines.append("")
        lines.append("| City slug | Article links |")
        lines.append("|-----------|---------------|")
        for slug, count in over_linked:
            lines.append(f"| `{slug}` | {count} |")
        lines.append("")

    lines.extend([
        "## Clusters (from cluster_map.json)",
        "",
        "| ID | Name | Pillar status | Live articles | Pending articles | Climate weights |",
        "|----|------|---------------|---------------|------------------|-----------------|",
    ])
    for cid, c in cmap['clusters'].items():
        n_live = sum(1 for a in c['articles'] if a.get('status') == 'live')
        n_pending = sum(1 for a in c['articles'] if a.get('status') == 'pending')
        weights = c.get('climate_weights', 'all_rotated')
        if isinstance(weights, dict):
            weights = ', '.join(f"{k}:{v}" for k, v in weights.items())
        lines.append(f"| {cid} | {c['name']} | {c['pillar']['status']} | {n_live} | {n_pending} | {weights} |")
    lines.append("")

    lines.extend([
        "## How to use",
        "",
        "**Before writing an article**, open `article_link_plan.csv` and find its row. You'll see exactly:",
        "- Which 4 cities to link to (in the body copy as contextual examples AND in the footer block)",
        "- Which 2 state hubs to link",
        "- Which pillar article to link to",
        "- Which cross-cluster anchor article to reference",
        "",
        "**When a new city or article is added**, re-run `python generate_link_plan.py` to refresh every mapping. The determinism guarantees that existing mappings stay the same — only the new rows change.",
        "",
        "**For end-to-end QC**, check `city_link_coverage.csv` for orphans (cities with 0 planned article links) and over-linked cities (>5 links) before scaling past 30 articles.",
    ])

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def check_state_consistency(cmap):
    """Return a list of (severity, message) for every state drift between cluster_map.json and the filesystem.

    Catches:
    - Articles marked `live` but HTML file missing
    - HTML files present in articles/ that aren't listed in cluster_map.json
    - Pillars marked `live` but filename missing
    """
    issues = []
    known_slugs = set()

    # Collect all article filenames from cluster_map
    for cluster_id, cluster in cmap['clusters'].items():
        pillar = cluster['pillar']
        known_slugs.add(pillar['slug'])
        pillar_path = Path(pillar['filename'])
        if pillar['status'] == 'live' and not pillar_path.exists():
            issues.append(('ERROR', f"Pillar {cluster_id} marked 'live' but file missing: {pillar['filename']}"))
        if pillar['status'] == 'pending' and pillar_path.exists():
            issues.append(('WARN', f"Pillar {cluster_id} marked 'pending' but file EXISTS — flip status to 'live': {pillar['filename']}"))

        for art in cluster['articles']:
            known_slugs.add(art['slug'])
            art_path = Path(art['path'])
            if art.get('status') == 'live' and not art_path.exists():
                issues.append(('ERROR', f"{cluster_id} article '{art['slug']}' marked 'live' but file missing: {art['path']}"))
            if art.get('status') == 'pending' and art_path.exists():
                issues.append(('WARN', f"{cluster_id} article '{art['slug']}' marked 'pending' but file EXISTS — flip status: {art['path']}"))

    # Check for HTML files on disk not mentioned in cluster_map
    articles_dir = Path('articles')
    if articles_dir.exists():
        for html in sorted(articles_dir.glob('*.html')):
            slug = html.stem
            if slug not in known_slugs:
                issues.append(('WARN', f"File exists but no cluster_map.json entry: {html} — add it to the right cluster"))

    # Root-level article-*.html check
    for html in sorted(Path('.').glob('article-*.html')):
        slug = html.stem
        if slug not in known_slugs:
            issues.append(('WARN', f"Root-level article missing from cluster_map.json: {html}"))

    return issues


def write_progress_dashboard(cmap, n_cities, city_to_articles, issues, out_path="PROGRESS.md"):
    """Single-file dashboard showing what's done, what's next, and any drift.

    This is the FIRST file any future session should read. It answers:
    - Where are we in the 100-article plan?
    - Which cluster is healthiest / weakest?
    - Which priority_queue entries are SKIPPED (doorway-risk) vs pending?
    - Is anything out of sync?

    Note: since 2026-05-23 the priority_queue section is INFORMATIONAL ONLY.
    For "what to write next," consult docs/article-strategy-2026-05-23.md
    (Phase 1 menu) and CLAUDE.md "Topical Authority Without Doorway Risk".
    """
    total_planned = 100
    all_articles = []
    for cid, cluster in cmap['clusters'].items():
        all_articles.append({'cluster': cid, 'slug': cluster['pillar']['slug'], 'type': 'pillar', 'status': cluster['pillar']['status'], 'title': cluster['pillar']['title']})
        for art in cluster['articles']:
            all_articles.append({'cluster': cid, 'slug': art['slug'], 'type': 'cluster', 'status': art.get('status', 'pending'), 'title': art['title'], 'priority': art.get('priority', '')})

    n_live = sum(1 for a in all_articles if a['status'] == 'live')
    n_in_progress = sum(1 for a in all_articles if a['status'] == 'in_progress')
    n_pending = sum(1 for a in all_articles if a['status'] == 'pending')

    linked = sum(1 for v in city_to_articles.values() if v)
    coverage_pct = 100 * linked / n_cities if n_cities else 0

    lines = [
        "# CoolCallPro — Progress Dashboard",
        "",
        f"_Auto-generated by `generate_link_plan.py` on {date.today().isoformat()}. Regenerate after every article ships._",
        "",
        "**This is the single source of progress truth. Read this first in any new session.**",
        "",
        "## Overall status",
        "",
        f"- **Articles live:** {n_live}",
        f"- **Articles in progress:** {n_in_progress}",
        f"- **Articles pending (in cluster_map):** {n_pending}",
        f"- **Articles planned but not yet in cluster_map:** {total_planned - len(all_articles)} (will be added as they move from the bucket roadmap into cluster assignments)",
        f"- **Target:** 100 articles",
        f"- **City coverage:** {linked}/{n_cities} ({coverage_pct:.0f}%) cities receive ≥1 planned article link",
        "",
        "## Cluster health",
        "",
        "| Cluster | Name | Pillar | Live | Pending | Next priority article |",
        "|---------|------|--------|------|---------|----------------------|",
    ]

    for cid, cluster in cmap['clusters'].items():
        pillar_status = cluster['pillar']['status']
        live = sum(1 for a in cluster['articles'] if a.get('status') == 'live')
        pending = sum(1 for a in cluster['articles'] if a.get('status') == 'pending')
        # Find the lowest-priority pending article
        pendings = [a for a in cluster['articles'] if a.get('status') == 'pending' and a.get('priority')]
        pendings.sort(key=lambda a: a.get('priority', 999))
        next_art = pendings[0]['title'] if pendings else '—'
        pillar_marker = '✓' if pillar_status == 'live' else '(pending)'
        lines.append(f"| {cid} | {cluster['name']} | {pillar_marker} | {live} | {pending} | {next_art} |")

    lines.extend([
        "",
        "## Priority queue (INFORMATIONAL ONLY since 2026-05-23)",
        "",
        "> **Do NOT pick the next article directly from this queue.** Per the",
        "> CLAUDE.md \"Topical Authority Without Doorway Risk\" rule (2026-05-23),",
        "> the queue order below is informational only. The current Phase 1 menu",
        "> of next-8 candidates lives at [`docs/article-strategy-2026-05-23.md`](docs/article-strategy-2026-05-23.md).",
        "> Many slugs below have `status=skipped` or are deferred indefinitely",
        "> (cost-niche + symptom-variant articles that would compound doorway risk).",
        "> Always pass the 3-question uniqueness test before adding any slug to",
        "> `cluster_map.json`.",
        "",
        "| # | Cluster | Type | Slug | Status |",
        "|---|---------|------|------|--------|",
    ])

    # Build status lookup
    status_lookup = {a['slug']: a['status'] for a in all_articles}
    shown = 0
    for entry in cmap.get('priority_queue', []):
        if shown >= 10:
            break
        status = status_lookup.get(entry['slug'], '?')
        if status != 'live':
            lines.append(f"| {entry['position']} | {entry['cluster']} | {entry['type']} | `{entry['slug']}` | {status} |")
            shown += 1

    lines.extend([
        "",
        "## Live articles (all 6 clusters)",
        "",
    ])
    for cid, cluster in cmap['clusters'].items():
        live_arts = [a for a in cluster['articles'] if a.get('status') == 'live']
        if not live_arts:
            continue
        lines.append(f"**{cid} — {cluster['name']}:**")
        for a in live_arts:
            lines.append(f"- `{a['slug']}` — {a['title']}")
        lines.append("")

    lines.extend([
        "## State consistency check",
        "",
    ])
    if not issues:
        lines.append("✓ No drift detected. cluster_map.json matches the filesystem.")
    else:
        errors = [msg for sev, msg in issues if sev == 'ERROR']
        warns = [msg for sev, msg in issues if sev == 'WARN']
        if errors:
            lines.append(f"**⚠ {len(errors)} ERROR(s) — must fix:**")
            for msg in errors:
                lines.append(f"- {msg}")
            lines.append("")
        if warns:
            lines.append(f"**Note — {len(warns)} warning(s):**")
            for msg in warns:
                lines.append(f"- {msg}")
            lines.append("")

    lines.extend([
        "## How to resume work in a new session",
        "",
        "1. Read this file (PROGRESS.md) first.",
        "2. Read `cluster_map.json` for full cluster/article state.",
        "3. Read `article_link_plan.csv` for any article's exact city links.",
        "4. Read `LINK_PLAN.md` for system overview and coverage details.",
        "5. Read `.agents/SKILLS/hvac-article-writer.md` for the writing procedure.",
        "6. Read the plan at `C:\\Users\\gyane\\.claude\\plans\\whimsical-strolling-riddle.md` for the original strategy.",
        "",
        "After writing any article:",
        "",
        "1. Update the article's `status` to `live` in `cluster_map.json`.",
        "2. Run `python generate_link_plan.py` — regenerates all 3 CSVs + this dashboard + LINK_PLAN.md.",
        "3. Commit both cluster_map.json AND the regenerated files.",
        "4. Push. Cloudflare Pages auto-deploys in ~60 seconds.",
    ])

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    cmap = load_cluster_map()

    print("Checking state consistency (cluster_map.json vs filesystem)...")
    issues = check_state_consistency(cmap)
    errors = [m for s, m in issues if s == 'ERROR']
    warns = [m for s, m in issues if s == 'WARN']
    if errors:
        print(f"  ERRORS: {len(errors)}")
        for m in errors:
            print(f"    - {m}")
    if warns:
        print(f"  WARNINGS: {len(warns)}")
        for m in warns[:5]:
            print(f"    - {m}")
        if len(warns) > 5:
            print(f"    ... and {len(warns) - 5} more (see PROGRESS.md)")
    if not issues:
        print("  OK — no drift detected.")

    print("Generating article_link_plan.csv...")
    n_articles = write_article_link_plan(cmap)
    print(f"  -> {n_articles} article rows")

    print("Generating city_link_coverage.csv...")
    n_cities, city_to_articles = write_city_coverage(cmap)
    print(f"  -> {n_cities} city rows")

    print("Generating LINK_PLAN.md...")
    write_landing_md(cmap, n_articles, n_cities, city_to_articles)
    print("  -> landing page with coverage stats")

    print("Generating PROGRESS.md...")
    write_progress_dashboard(cmap, n_cities, city_to_articles, issues)
    print("  -> progress dashboard (read this first in any new session)")

    # Coverage summary
    linked = sum(1 for v in city_to_articles.values() if v)
    orphans = n_cities - linked
    print()
    print(f"COVERAGE: {linked}/{n_cities} cities ({100*linked/n_cities:.0f}%) receive >=1 article link.")
    if orphans:
        print(f"NOTE: {orphans} orphan cities — grows to near-zero at 100 articles.")


if __name__ == "__main__":
    main()
