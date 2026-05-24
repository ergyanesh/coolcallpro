"""scripts/audit_articles_perfection.py

Three-in-one audit for the article perfection pass (since 2026-05-23):

  1. UNIQUENESS    -- pairwise text-similarity within a cluster (doorway-risk check)
  2. CONVERSION ARC -- presence of the 6-step funnel (per CLAUDE.md "Conversion Arc")
  3. NO GUESSWORK  -- forbidden-phrase + inline-citation check (per CLAUDE.md
                      "No Assumptions, No Guesswork in Any Article")

Generates a Markdown triage table + per-pair similarity matrix to
docs/audit-perfection-pass-YYYYMMDD.md (date-stamped, repo-tracked).

Usage:
  python scripts/audit_articles_perfection.py --cluster C1_ac C4_cost
  python scripts/audit_articles_perfection.py --all
  python scripts/audit_articles_perfection.py --article articles/ac-freezing-up-in-summer.html

Rules these three audits implement live in CLAUDE.md:
  - "Topical Authority Without Doorway Risk" (NON-NEGOTIABLE since 2026-05-23)
  - "No Assumptions, No Guesswork in Any Article" (NON-NEGOTIABLE since 2026-05-23)
  - "Conversion Arc" (NON-NEGOTIABLE since 2026-05-23)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, List, Set, Tuple

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: install beautifulsoup4 (`pip install beautifulsoup4`)", file=sys.stderr)
    sys.exit(2)


# ============================================================
# UNIQUENESS — pairwise similarity within a cluster
# ============================================================

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
    'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what',
    'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how', 'all',
    'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
    's', 't', 'just', 'don', 'now', 'as', 'if', 'about', 'between', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down',
    'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'your', 'my', 'his', 'her', 'its', 'our', 'their',
    'me', 'us', 'them', 'him', 'will', 'won', 'wouldn', 'shouldn', 'couldn',
}

# Cool Call Pro boilerplate that appears in nearly every article -- strip
# before similarity scoring to avoid false-positive overlap from the shared
# footer disclaimer, MarketCall block, "Find a pro" section, etc.
BOILERPLATE_PATTERNS = [
    r'Cool Call Pro is a free service to assist homeowners.*?Cool Call Pro\.',
    r'Same-day and 24/7 emergency services are subject to.*?capacity\.',
    r'Find a pro in.*?or browse by state.*?all locations',
    r'\(844\)\s*582-1795',
    r'Skip to main content',
    r'How this site works.*?provider and location\.',
    r'Editorial standards.*?clarity and accuracy when needed\.',
    r'Last reviewed.*?\d{4}',
    r'YMYL VERIFICATION LOG.*?-->',
]


def _strip_boilerplate(text: str) -> str:
    """Remove site-wide boilerplate from article body text before similarity scoring."""
    for pat in BOILERPLATE_PATTERNS:
        text = re.sub(pat, ' ', text, flags=re.DOTALL | re.IGNORECASE)
    return text


def _extract_body_text(html_path: Path) -> str:
    """Pull article body text WITH boilerplate STRIPPED. Use for uniqueness scoring
    (boilerplate inflates similarity). NOT suitable for arc/CTA detection."""
    soup = BeautifulSoup(html_path.read_text(encoding='utf-8'), 'html.parser')
    for tag in soup(['nav', 'header', 'footer', 'script', 'style', 'noscript']):
        tag.decompose()
    body = soup.find('article') or soup.find('main') or soup.body or soup
    text = body.get_text(separator=' ')
    text = _strip_boilerplate(text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text


def _extract_body_text_raw(html_path: Path) -> str:
    """Pull article body text WITHOUT stripping CTA/diagnostic boilerplate.
    Preserves CTAs / phone numbers / DIY-boundary language. Use for arc detection.

    Skips past the SITE-WIDE Advertising Disclosure + safety-warning boilerplate
    that prefixes every article -- otherwise arc step 1 (symptom validation in
    first 200 words) always falsely fails because the disclosure eats those words.
    """
    soup = BeautifulSoup(html_path.read_text(encoding='utf-8'), 'html.parser')
    for tag in soup(['nav', 'header', 'footer', 'script', 'style', 'noscript']):
        tag.decompose()
    body = soup.find('article') or soup.find('main') or soup.body or soup
    text = body.get_text(separator=' ')
    text = re.sub(r'\s+', ' ', text).strip()

    # Skip past site-wide safety boilerplate. Each article begins with either:
    #   (a) "Advertising Disclosure: ... HVAC systems involve high-voltage
    #        electricity, natural gas, and pressurized refrigerant. Always let
    #        a qualified technician handle live components." (~120 words)
    #   (b) Same plus a specific safety warning prefix ("If you smell natural
    #        gas..." / "If a carbon monoxide detector is alarming...") (~150 words)
    # We need to find where the actual article content begins.
    boilerplate_end_patterns = [
        # End of generic safety boilerplate
        r'Always let a qualified technician handle live components\.\s*',
        # End of CO/gas-specific safety prefix that ends with diagnosis statement
        r'Let a qualified HVAC technician handle every part of diagnosis and repair\.\s*',
        # Fallback: any "Key Takeaway" heading marks the start of article content
        r'Key Takeaway\s+',
    ]
    for pat in boilerplate_end_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            text = text[m.end():].lstrip()
            break
    return text


def _extract_h1_meta(html_path: Path) -> Dict[str, str]:
    """Pull H1, <title>, meta description for separate intent comparison."""
    soup = BeautifulSoup(html_path.read_text(encoding='utf-8'), 'html.parser')
    h1 = soup.find('h1')
    title = soup.find('title')
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    return {
        'h1': h1.get_text(strip=True).lower() if h1 else '',
        'title': title.get_text(strip=True).lower() if title else '',
        'meta_desc': (meta_desc.get('content', '') if meta_desc else '').lower(),
    }


def _word_set(text: str, min_len: int = 4) -> Set[str]:
    """Tokenize to word set, drop stop words + short tokens."""
    words = re.findall(r'[a-z]{' + str(min_len) + r',}', text.lower())
    return {w for w in words if w not in STOP_WORDS}


def _shingles(text: str, k: int = 5) -> Set[str]:
    """k-shingles (k=5 words). Captures phrase-level similarity."""
    words = re.findall(r'[a-z]+', text.lower())
    if len(words) < k:
        return set()
    return {' '.join(words[i:i + k]) for i in range(len(words) - k + 1)}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def uniqueness_audit(articles: List[Dict]) -> Dict:
    """Pairwise similarity scoring. Returns matrix + flagged pairs.

    Each article dict needs: slug, path, body_text, h1, title.
    Overlap score per pair = weighted average of:
      - Body word-set Jaccard (50%)
      - Body 5-shingle Jaccard (30%)
      - H1 word-set Jaccard (10%)
      - Title word-set Jaccard (10%)
    Overlap > 0.40 = doorway risk flag.
    """
    n = len(articles)
    pairs = []
    flagged = []

    # Pre-compute per-article token sets
    for a in articles:
        a['word_set'] = _word_set(a['body_text'])
        a['shingles'] = _shingles(a['body_text'], k=5)
        a['h1_set'] = _word_set(a['h1'], min_len=3)
        a['title_set'] = _word_set(a['title'], min_len=3)

    for i in range(n):
        for j in range(i + 1, n):
            a, b = articles[i], articles[j]
            body_jaccard = _jaccard(a['word_set'], b['word_set'])
            shingle_jaccard = _jaccard(a['shingles'], b['shingles'])
            h1_jaccard = _jaccard(a['h1_set'], b['h1_set'])
            title_jaccard = _jaccard(a['title_set'], b['title_set'])
            score = (
                0.50 * body_jaccard
                + 0.30 * shingle_jaccard
                + 0.10 * h1_jaccard
                + 0.10 * title_jaccard
            )
            pair = {
                'a': a['slug'],
                'b': b['slug'],
                'score': score,
                'body': body_jaccard,
                'shingle': shingle_jaccard,
                'h1': h1_jaccard,
                'title': title_jaccard,
            }
            pairs.append(pair)
            if score >= 0.40:
                flagged.append(pair)

    pairs.sort(key=lambda p: -p['score'])
    flagged.sort(key=lambda p: -p['score'])

    # Per-article: top-3 closest siblings
    per_article = defaultdict(list)
    for p in pairs:
        per_article[p['a']].append((p['b'], p['score']))
        per_article[p['b']].append((p['a'], p['score']))
    for slug in per_article:
        per_article[slug].sort(key=lambda x: -x[1])
        per_article[slug] = per_article[slug][:3]

    return {
        'pairs': pairs,
        'flagged': flagged,
        'per_article': dict(per_article),
    }


# ============================================================
# CONVERSION ARC — presence check for the 6-step funnel
# ============================================================

def _section_present(body: str, keywords: List[str], require_n: int = 2) -> bool:
    """At least `require_n` of the keyword groups must match in the body."""
    matches = sum(1 for kw in keywords if re.search(kw, body, re.IGNORECASE))
    return matches >= require_n


def _first_n_words(body: str, n: int) -> str:
    return ' '.join(re.findall(r'\S+', body)[:n])


def _last_n_words(body: str, n: int) -> str:
    return ' '.join(re.findall(r'\S+', body)[-n:])


def conversion_arc_audit(body_text: str, html_raw: str) -> Dict:
    """Check for the 6-step conversion arc.

    Returns dict with 'present' (list of step ids that pass) and 'missing'.
    Step detection is heuristic -- false positives possible. Triage table
    surfaces this for human review.
    """
    body = body_text
    first_200 = _first_n_words(body, 200)

    steps = {}

    # Step 1: Symptom validation in opening (first 200 words)
    # Heuristic: opening contains problem-statement language
    step1_kw = [
        r'\b(?:if|when)\s+your',
        r'\bsymptom',
        r'\bproblem',
        r'\bnoticed?',
        r'\bhappens?',
        r'\bstopped|failing|broken|not working',
        r'\bunderstand|recognize',
    ]
    steps['1_symptom'] = _section_present(first_200, step1_kw, require_n=1)

    # Step 2: Stakes escalation -- damage / risk / cost language in body
    step2_kw = [
        r'\bdamage',
        r'\brisk',
        r'\binjur',
        r'\bcost[s]? more|expensive|compounding',
        r'\bdanger|hazard',
        r'\bsafety',
        r'\bif you ignore|if left',
    ]
    steps['2_stakes'] = _section_present(body, step2_kw, require_n=2)

    # Step 3: DIY boundary explicit -- safe DIY list + stop language
    step3_kw = [
        r'\bfilter\b',
        r'\bthermostat\b',
        r'\bcondensate|drain',
        r'\bcall (?:a |the |an )?(?:pro|tech|professional|licensed)',
        r'\bdo not|don.t (?:try|attempt|open|touch)',
        r'\bsafe|safely',
    ]
    steps['3_diy_boundary'] = _section_present(body, step3_kw, require_n=3)

    # Step 4: Demystify pro process -- WHAT the tech does, with diagnostic terms
    step4_kw = [
        r'\bmultimeter|voltmeter',
        r'\bpressure|psi|manifold',
        r'\brefrigerant',
        r'\bdiagnostic|inspect',
        r'\bcapacitor|contactor|compressor',
        r'\bservice call|tune.?up',
        r'\b\d+[-\s]?(?:minute|min|hour|hr)',
        r'\btechnician will',
        r'\bwhat (?:the |a )?(?:tech|technician|pro)',
    ]
    steps['4_demystify_pro'] = _section_present(body, step4_kw, require_n=3)

    # Step 5: Trust signals + price-shop defense
    step5_kw = [
        r'\bsecond opinion',
        r'\bred flag|warning sign',
        r'\bupsell',
        r'\bask (?:the |a |for )',
        r'\blicensed|certified|insured',
        r'\bquote',
        r'\bavoid (?:being )?(?:scammed|ripped)',
        r'\bcheck (?:the |their |for )',
    ]
    steps['5_trust'] = _section_present(body, step5_kw, require_n=2)

    # Step 6: Phone CTA presence — fixed 2026-05-23 to handle articles with FAQ tail
    # (the literal "final 200 words" is usually FAQ answer text, not CTA. CTAs typically
    # sit BEFORE the FAQ section in our template.)
    # Pass criteria: >=2 phone CTAs total AND at least one CTA in the bottom 50% of body.
    words = re.findall(r'\S+', body)
    if len(words) < 100:
        steps['6_cta'] = False
    else:
        total_cta = len(re.findall(r'\(?844\)?[\s\-]?582[\s\-]?1795', body))
        bottom_half = ' '.join(words[len(words) // 2:])
        cta_in_bottom = bool(re.search(r'\(?844\)?[\s\-]?582[\s\-]?1795', bottom_half))
        steps['6_cta'] = total_cta >= 2 and cta_in_bottom

    present = [k for k, v in steps.items() if v]
    missing = [k for k, v in steps.items() if not v]

    return {
        'steps': steps,
        'present': present,
        'missing': missing,
        'score': len(present) / 6.0,
    }


# ============================================================
# NO GUESSWORK -- forbidden-phrase + inline-citation check
# ============================================================

# Phrases that REQUIRE an inline citation per CLAUDE.md "No Assumptions" rule.
# Each entry is (pattern, label). Citation = .gov/.edu URL or named source
# within 500 chars of the match, OR reference to costs.html / our xlsx.
FORBIDDEN_PHRASES = [
    (r'\bmost homeowners\b', 'most homeowners'),
    (r'\bmost HVAC systems\b', 'most HVAC systems'),
    (r'\bmost furnaces\b', 'most furnaces'),
    (r'\bmost (?:AC|air conditioner)s?\b', 'most ACs'),
    (r'\bindustry standard\b', 'industry standard'),
    (r'\bstudies show\b', 'studies show'),
    (r'\bresearch (?:indicates|shows)\b', 'research indicates'),
    (r'\bexperts (?:recommend|agree|say)\b', 'experts recommend'),
    (r'\btypically lasts?\b', 'typically lasts'),
    (r'\busually lasts?\b', 'usually lasts'),
    (r'\bleading cause\b', 'leading cause'),
    (r'\bmost common (?:cause|failure|problem)\b', 'most common cause/failure'),
    (r'\baccording to (?:data|research|studies)\b', 'according to data'),
    (r'\b(?:on )?average,? \w+ (?:cost|spend|pay)s?\b', 'average cost claim'),
    (r'\b\d+\s*%\s+of (?:homes|homeowners)\b', '% of homes/homeowners claim'),
]

# Markers that count as "inline citation" within 500 chars of the forbidden phrase.
# .gov, .edu, manufacturer domain, internal cost reference, named source pattern.
CITATION_MARKERS = [
    r'href=["\'][^"\']*\.gov[/"\']',
    r'href=["\'][^"\']*\.edu[/"\']',
    r'href=["\'][^"\']*\b(?:dsireusa|energystar|acca|ahri|ashrae|nfpa|epa|doe|irs|cdc|noaa|census|eia)\b',
    r'href=["\'][^"\']*\b(?:lennox|trane|carrier|mitsubishi|daikin|rheem|york|goodman|bosch|honeywell|johnson)\b',
    r'href=["\'][^"\']*\bcosts(?:\.html)?["\']',
    r'href=["\'][^"\']*\b2026-hvac-cost-guide',
    r'per\s+(?:the\s+)?(?:DOE|EPA|IRS|CDC|NOAA|ACCA|AHRI|ASHRAE|NFPA|ENERGY STAR|Census|ACS|EIA)',
    r'(?:DOE|EPA|IRS|CDC|NOAA|ACCA|AHRI|ASHRAE|NFPA|ENERGY STAR|Census|ACS|EIA)\s+(?:reports?|says?|recommends?|publishes?|requires?)',
]


def no_guesswork_audit(html_raw: str) -> Dict:
    """Check for forbidden phrases without inline citation within 500 chars."""
    issues = []
    for pat, label in FORBIDDEN_PHRASES:
        for m in re.finditer(pat, html_raw, re.IGNORECASE):
            start = max(0, m.start() - 250)
            end = min(len(html_raw), m.end() + 250)
            context = html_raw[start:end]
            cited = any(re.search(cm, context, re.IGNORECASE) for cm in CITATION_MARKERS)
            if not cited:
                # Find line number for the match
                line_num = html_raw[:m.start()].count('\n') + 1
                issues.append({
                    'phrase': label,
                    'match': m.group(0),
                    'line': line_num,
                })
    return {
        'count': len(issues),
        'issues': issues,
        'pass': len(issues) == 0,
    }


# ============================================================
# GSC cross-reference -- detect query cannibalization
# ============================================================

def gsc_query_cannibalization(articles: List[Dict], gsc_dir: Path) -> Dict:
    """Cross-reference article H1s against GSC Queries.csv to flag cannibalization.

    Cannibalization signal: two articles whose H1 has high overlap with the same
    GSC query AT THE SAME TIME would compete in SERPs.
    """
    queries_csv = gsc_dir / 'Queries.csv'
    if not queries_csv.exists():
        return {'warning': f'No Queries.csv at {gsc_dir}', 'pairs': []}

    queries = []
    with queries_csv.open(encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            q = (row.get('Top queries') or '').lower().strip()
            if q:
                impressions = int(row.get('Impressions', '0').replace(',', '') or 0)
                queries.append((q, impressions))

    # For each query, score against each article's H1 + title.
    # Tuned 2026-05-23: raise thresholds to filter out generic-cluster matches.
    # Only flag queries where:
    #   - impressions >= 20 (meaningful demand)
    #   - >=3 query words (specific intent, not "ac repair")
    #   - >=2 articles match at >=60% H1+title overlap (true cannibalization)
    #
    # Tuned 2026-05-23 (Batch 3): strip the " | Cool Call Pro" brand suffix
    # from the title before tokenizing. Without this, the word "call" from
    # the brand was matching "hvac service call" / "hvac call center" queries
    # on every article (since every title ends with the brand). That's not
    # real cannibalization -- Google distinguishes brand-suffix tokens.
    def _content_only(text):
        """Drop the brand suffix (everything after first ' | ') before tokenizing."""
        return text.split('|')[0].strip().lower()

    candidates = []
    for q, imp in queries:
        if imp < 20:
            continue
        q_words = set(re.findall(r'[a-z]{3,}', q))
        if len(q_words) < 3:
            continue
        matches = []
        for a in articles:
            h1_words = set(re.findall(r'[a-z]{3,}', _content_only(a.get('h1', ''))))
            title_words = set(re.findall(r'[a-z]{3,}', _content_only(a.get('title', ''))))
            overlap = len(q_words & (h1_words | title_words)) / max(1, len(q_words))
            if overlap >= 0.60:
                matches.append((a['slug'], overlap))
        if len(matches) >= 2:
            candidates.append({
                'query': q,
                'impressions': imp,
                'competing_articles': matches,
            })

    candidates.sort(key=lambda c: -c['impressions'])
    return {'pairs': candidates[:20], 'total_cannibalized_queries': len(candidates)}


# ============================================================
# MAIN: orchestrate + emit Markdown triage report
# ============================================================

def load_article_set(repo_root: Path, cluster_filter: List[str] = None,
                     article_paths: List[str] = None) -> List[Dict]:
    """Pull articles from cluster_map.json, filtered. Returns list of dicts
    with slug, cluster, type, path, body_text, h1, title, meta_desc, html_raw."""
    cm = json.loads((repo_root / 'cluster_map.json').read_text(encoding='utf-8'))
    articles = []

    if article_paths:
        # Single-article mode: just load the specified paths
        for ap in article_paths:
            p = repo_root / ap
            if not p.exists():
                print(f"  SKIP (missing): {ap}", file=sys.stderr)
                continue
            slug = p.stem
            articles.append(_build_article_dict(p, slug, '?', '?', cluster_filter=None))
        return articles

    # Cluster mode: pull live + in_progress articles
    for cid, cluster in cm.get('clusters', {}).items():
        if cluster_filter and cid not in cluster_filter:
            continue
        # Include pillar
        pillar = cluster.get('pillar', {})
        if pillar.get('status') in ('live', 'in_progress'):
            slug = pillar['slug']
            # Pillar path: articles/<slug>.html OR article-<slug>.html
            for candidate in [
                repo_root / 'articles' / f'{slug}.html',
                repo_root / f'article-{slug}.html',
                repo_root / f'{slug}.html',
            ]:
                if candidate.exists():
                    articles.append(_build_article_dict(candidate, slug, cid, 'pillar'))
                    break
        # Include cluster articles
        for a in cluster.get('articles', []):
            if a.get('status') not in ('live', 'in_progress'):
                continue
            slug = a['slug']
            for candidate in [
                repo_root / 'articles' / f'{slug}.html',
                repo_root / f'article-{slug}.html',
                repo_root / f'{slug}.html',
            ]:
                if candidate.exists():
                    articles.append(_build_article_dict(candidate, slug, cid, a.get('type', 'cluster')))
                    break

    return articles


def _build_article_dict(path: Path, slug: str, cluster: str, type_: str,
                        cluster_filter=None) -> Dict:
    html_raw = path.read_text(encoding='utf-8')
    body_text = _extract_body_text(path)         # boilerplate stripped (uniqueness)
    body_text_raw = _extract_body_text_raw(path)  # boilerplate preserved (arc detection)
    meta = _extract_h1_meta(path)
    return {
        'slug': slug,
        'cluster': cluster,
        'type': type_,
        'path': str(path.relative_to(path.parents[1])),
        'body_text': body_text,
        'body_text_raw': body_text_raw,
        'html_raw': html_raw,
        'h1': meta['h1'],
        'title': meta['title'],
        'meta_desc': meta['meta_desc'],
    }


def emit_report(articles: List[Dict], uniq: Dict, arcs: Dict, guess: Dict,
                cannibal: Dict, out_path: Path) -> None:
    """Write Markdown triage report."""
    lines = []
    lines.append(f"# Article Perfection Audit Report — {date.today().isoformat()}")
    lines.append("")
    lines.append("Generated by `scripts/audit_articles_perfection.py`. Per-article verdicts")
    lines.append("are heuristic suggestions for human review -- see CLAUDE.md sections")
    lines.append("\"Topical Authority Without Doorway Risk\", \"Conversion Arc\", and")
    lines.append("\"No Assumptions, No Guesswork in Any Article\" for the underlying rules.")
    lines.append("")
    lines.append(f"**Audit scope:** {len(articles)} articles")
    lines.append("")

    # === Section 1: per-article summary table ===
    lines.append("## Per-article verdict table")
    lines.append("")
    lines.append("| Slug | Cluster | Max overlap pair | Arc score (/6) | Missing arc steps | Guesswork issues | Verdict |")
    lines.append("|---|---|---|---:|---|---:|---|")
    for a in sorted(articles, key=lambda x: (x['cluster'], x['slug'])):
        slug = a['slug']
        top_pair = uniq['per_article'].get(slug, [(None, 0.0)])[0]
        max_overlap = top_pair[1] * 100
        arc = arcs.get(slug, {})
        guess_count = guess.get(slug, {}).get('count', 0)
        missing_steps = arc.get('missing', [])
        # Verdict heuristic
        if max_overlap >= 50 or len(missing_steps) >= 4 or guess_count >= 10:
            verdict = '**REWRITE**'
        elif max_overlap >= 40 or len(missing_steps) >= 3 or guess_count >= 5:
            verdict = '**FIX**'
        elif len(missing_steps) >= 1 or guess_count >= 1:
            verdict = 'minor-FIX'
        else:
            verdict = 'PASS'
        pair_str = f"{top_pair[0]} ({max_overlap:.0f}%)" if top_pair[0] else "n/a"
        missing_str = ", ".join(missing_steps) if missing_steps else "-"
        lines.append(
            f"| `{slug}` | {a['cluster']} | {pair_str} | "
            f"{int(arc.get('score', 0) * 6)} | {missing_str} | {guess_count} | {verdict} |"
        )
    lines.append("")

    # === Section 2: flagged uniqueness pairs ===
    lines.append("## Flagged uniqueness pairs (overlap >= 40%)")
    lines.append("")
    if not uniq['flagged']:
        lines.append("_None. All article pairs are below the 40% overlap threshold._")
    else:
        lines.append("| Article A | Article B | Overall | Body | 5-Shingle | H1 | Title |")
        lines.append("|---|---|---:|---:|---:|---:|---:|")
        for p in uniq['flagged']:
            lines.append(
                f"| `{p['a']}` | `{p['b']}` | "
                f"{p['score']*100:.0f}% | {p['body']*100:.0f}% | "
                f"{p['shingle']*100:.0f}% | {p['h1']*100:.0f}% | "
                f"{p['title']*100:.0f}% |"
            )
    lines.append("")

    # === Section 3: full pair similarity (top 20) ===
    lines.append("## Top 20 most-similar article pairs (full ranking)")
    lines.append("")
    lines.append("| # | Article A | Article B | Overlap |")
    lines.append("|---|---|---|---:|")
    for i, p in enumerate(uniq['pairs'][:20], 1):
        lines.append(f"| {i} | `{p['a']}` | `{p['b']}` | {p['score']*100:.0f}% |")
    lines.append("")

    # === Section 4: conversion arc gaps ===
    lines.append("## Conversion arc gap detail")
    lines.append("")
    lines.append("| Slug | Step 1 symptom | Step 2 stakes | Step 3 DIY | Step 4 demystify pro | Step 5 trust | Step 6 CTA |")
    lines.append("|---|---|---|---|---|---|---|")
    for a in sorted(articles, key=lambda x: (x['cluster'], x['slug'])):
        arc = arcs.get(a['slug'], {}).get('steps', {})
        cells = [
            'OK' if arc.get('1_symptom') else 'MISS',
            'OK' if arc.get('2_stakes') else 'MISS',
            'OK' if arc.get('3_diy_boundary') else 'MISS',
            'OK' if arc.get('4_demystify_pro') else 'MISS',
            'OK' if arc.get('5_trust') else 'MISS',
            'OK' if arc.get('6_cta') else 'MISS',
        ]
        lines.append(f"| `{a['slug']}` | " + " | ".join(cells) + " |")
    lines.append("")

    # === Section 5: guesswork issues ===
    lines.append("## Guesswork issues (forbidden phrases without inline citation)")
    lines.append("")
    has_any = False
    for a in sorted(articles, key=lambda x: (x['cluster'], x['slug'])):
        g = guess.get(a['slug'], {})
        if g.get('count', 0) == 0:
            continue
        has_any = True
        lines.append(f"### `{a['slug']}` ({g['count']} issues)")
        lines.append("")
        for issue in g.get('issues', [])[:10]:  # cap at 10 per article in report
            lines.append(f"- Line {issue['line']}: \"{issue['match']}\" ({issue['phrase']})")
        if g['count'] > 10:
            lines.append(f"- ...and {g['count'] - 10} more")
        lines.append("")
    if not has_any:
        lines.append("_None. All articles pass the no-guesswork check._")
        lines.append("")

    # === Section 6: GSC query cannibalization ===
    lines.append("## GSC query cannibalization (multiple articles competing for the same query)")
    lines.append("")
    if cannibal.get('warning'):
        lines.append(f"_{cannibal['warning']}_")
    elif not cannibal.get('pairs'):
        lines.append("_None. No queries detected with 2+ articles competing._")
    else:
        lines.append("| Query | Impressions | Competing articles |")
        lines.append("|---|---:|---|")
        for c in cannibal['pairs']:
            articles_str = " + ".join(f"`{s}` ({o*100:.0f}%)" for s, o in c['competing_articles'])
            lines.append(f"| {c['query']} | {c['impressions']} | {articles_str} |")
    lines.append("")

    # === Section 7: how to act on this report ===
    lines.append("## How to act on this report")
    lines.append("")
    lines.append("Per-article verdict legend:")
    lines.append("- **PASS** -- meets all 3 audits. No changes needed.")
    lines.append("- **minor-FIX** -- 1-2 small gaps. ~15-30 min per article (citations + small arc step).")
    lines.append("- **FIX** -- meaningful gaps. ~1-2 hours per article (add missing arc sections, citations, paragraph rewrites).")
    lines.append("- **REWRITE** -- substantial rework. ~3-5 hours per article (structural changes, deep arc retrofit).")
    lines.append("")
    lines.append("Pair-level decisions (for flagged uniqueness pairs):")
    lines.append("- **FIX both** -- if each can be narrowed to a distinct angle that survives 3-question test")
    lines.append("- **MERGE** -- consolidate the two into one stronger article + 301-redirect the weaker URL")
    lines.append("- **DEPRECATE** -- archive the weaker article + 301 to the stronger one")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding='utf-8')
    print(f"\nReport written: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Article perfection audit (uniqueness + conversion arc + no-guesswork)")
    parser.add_argument('--cluster', nargs='+', help='Cluster IDs (e.g. C1_ac C4_cost). Default: all.')
    parser.add_argument('--all', action='store_true', help='Audit all clusters.')
    parser.add_argument('--article', nargs='+', help='Specific article paths (skips cluster mode).')
    parser.add_argument('--gsc-dir', default='coolcallpro.com-Performance-on-Search-2026-05-22',
                        help='Path to GSC export directory for cannibalization check.')
    parser.add_argument('--out', default=None, help='Output report path. Default: docs/audit-perfection-pass-YYYYMMDD.md')
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent

    cluster_filter = args.cluster
    if args.all:
        cluster_filter = None

    print(f"Loading articles...")
    articles = load_article_set(
        repo_root,
        cluster_filter=cluster_filter,
        article_paths=args.article,
    )
    print(f"  Loaded {len(articles)} articles")
    for a in articles:
        print(f"    {a['cluster']}/{a['slug']}")

    if len(articles) < 2 and not args.article:
        print("Need >= 2 articles for uniqueness audit. Exiting.")
        sys.exit(1)

    print(f"\nRunning uniqueness audit ({len(articles) * (len(articles)-1) // 2} pairs)...")
    uniq = uniqueness_audit(articles)
    print(f"  Flagged pairs (overlap >= 40%): {len(uniq['flagged'])}")

    print(f"\nRunning conversion arc audit...")
    arcs = {}
    for a in articles:
        # Arc detection must use RAW body text (boilerplate-preserved) so CTAs are visible.
        arcs[a['slug']] = conversion_arc_audit(a['body_text_raw'], a['html_raw'])
    arc_fail = sum(1 for k, v in arcs.items() if v['score'] < 1.0)
    print(f"  Articles with arc gaps: {arc_fail}/{len(articles)}")

    print(f"\nRunning no-guesswork audit...")
    guess = {}
    for a in articles:
        guess[a['slug']] = no_guesswork_audit(a['html_raw'])
    guess_fail = sum(1 for k, v in guess.items() if not v['pass'])
    print(f"  Articles with guesswork issues: {guess_fail}/{len(articles)}")

    print(f"\nRunning GSC cannibalization cross-reference...")
    gsc_dir = repo_root / args.gsc_dir
    cannibal = gsc_query_cannibalization(articles, gsc_dir)
    if 'warning' in cannibal:
        print(f"  {cannibal['warning']}")
    else:
        print(f"  Cannibalized queries: {cannibal.get('total_cannibalized_queries', 0)}")

    out_path = Path(args.out) if args.out else (
        repo_root / 'docs' / f'audit-perfection-pass-{date.today().isoformat()}.md'
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    emit_report(articles, uniq, arcs, guess, cannibal, out_path)


if __name__ == '__main__':
    main()
