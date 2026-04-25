"""One-off corrective pass: rewrite stale 25C tax-credit claims on city/state pages.

Background: Section 25C terminated for installations after Dec 31, 2025 by OBBBA
(P.L. 119-21). The previous corrective commit (6712252) only patched the 3 main
articles; it missed the 115 city pages and 51 state hubs whose FAQ schemas, FAQ
visible text, rebates paragraphs, and dedicated H3 sections still claim the credit
is active and quote $2,000 / $600 / $3,200 amounts. This script rewrites those
4 patterns idempotently. After Option A's generator port, the generators will
emit OBBBA-aware copy directly and this script becomes obsolete.

Idempotency: each replacement is deterministic and only matches the OLD pattern,
not the NEW one. Running twice produces the same output as running once.
"""

import os, re, sys

# Pattern 1 — FAQ schema (115 city pages):
#   "...may qualify for rebates through X. Federal tax credits of up to $2,000
#    for qualifying heat pumps and high-efficiency systems may also apply."
P1_OLD = "Federal tax credits of up to $2,000 for qualifying heat pumps and high-efficiency systems may also apply."
P1_NEW = "The federal Section 25C tax credit was terminated for installations placed in service after Dec 31, 2025 (OBBBA, P.L. 119-21); check current state HEAR rebates and utility programs for what's still available in 2026."

# Pattern 2 — Rebates paragraph "$3,200/year via federal Energy Efficient Home Improvement Credit":
P2_OLD = ('Qualifying HVAC systems may also receive up to $3,200/year via the '
          '<a href="https://www.irs.gov/credits-deductions/energy-efficient-home-improvement-credit" '
          'target="_blank" rel="nofollow noopener" style="color: var(--orange-dark); font-weight: 600;">'
          'federal Energy Efficient Home Improvement Credit (IRS Section 25C)</a>.')
P2_NEW = ('The federal Section 25C credit (<a href="https://www.irs.gov/credits-deductions/'
          'energy-efficient-home-improvement-credit" target="_blank" rel="nofollow noopener" '
          'style="color: var(--orange-dark); font-weight: 600;">Energy Efficient Home Improvement Credit</a>) '
          'was terminated for installations placed in service after Dec 31, 2025 by the One Big Beautiful '
          'Bill Act (P.L. 119-21); for 2026 installs focus on state HEAR rebates and utility programs.')

# Pattern 3 — vaguer state-page FAQ "Federal tax credits may also apply..."
P3_OLD = "Federal tax credits may also apply for qualifying high-efficiency installations."
P3_NEW = "The federal Section 25C tax credit was terminated for installations after Dec 31, 2025 (OBBBA, P.L. 119-21); check current state HEAR rebates and utility programs for 2026."

# Pattern 4 — visible FAQ "Federal ENERGY STAR tax credits may also apply."
P4_OLD = "Federal ENERGY STAR tax credits may also apply."
P4_NEW = "The federal Section 25C credit was terminated for installations after Dec 31, 2025 (OBBBA, P.L. 119-21); check current state and utility programs for 2026."

# Pattern 5 — full H3 section paragraph (~41 city pages). Two CEE-phrasing
# variants exist; we accept either. Optional "non-refundable and stacks with X
# rebates" trailer; some pages omit it.
P5_RE = re.compile(
    r'<h3 style="font-size: 1\.2rem; color: var\(--navy\); margin-top: 24px;">Federal Tax Credits \(IRS Section 25C\)</h3>\s*'
    r'<p style="font-size: 1\.05rem; line-height: 1\.85; color: var\(--gray-700\);">The '
    r'<a href="https://www\.irs\.gov/credits-deductions/energy-efficient-home-improvement-credit"[^>]*>'
    r'IRS Energy Efficient Home Improvement Credit \(Section 25C\)</a> provides a federal income tax credit of up to '
    r'<strong>\$2,000 per year for a qualifying heat pump installation</strong> \(30% of cost up to the cap\) and up to '
    r'<strong>\$600 per year for a qualifying central air conditioner or natural gas furnace</strong>\. '
    r'Equipment must meet the highest (?:CEE efficiency tier|efficiency tier set by the Consortium for Energy Efficiency \(CEE\)) '
    r'in effect at the start of the calendar year of installation\.'
    r'(?: The credit is non-refundable and stacks with [^.]+? rebates\.)?</p>'
)

P5B_RE = re.compile(
    r'<h3 style="font-size: 1\.2rem; color: var\(--navy\); margin-top: 24px;">Federal Tax Credits \(IRS Section 25C\)</h3>\s*'
    r'<p style="font-size: 1\.05rem; line-height: 1\.85; color: var\(--gray-700\);">The '
    r'<a href="https://www\.irs\.gov/credits-deductions/energy-efficient-home-improvement-credit"[^>]*>'
    r'IRS Energy Efficient Home Improvement Credit \(Section 25C\)</a> provides a federal income tax credit of up to '
    r'<strong>\$2,000 per year for a qualifying heat pump installation</strong> \(30% of cost up to the cap\) and up to '
    r'<strong>\$600 per year for a qualifying central air conditioner or natural gas furnace</strong>\. '
    r'Equipment must meet the highest CEE efficiency tier in effect at the start of the calendar year of installation\.</p>'
)

P5_REPLACEMENT = (
    '<h3 style="font-size: 1.2rem; color: var(--navy); margin-top: 24px;">Federal Tax Credits — Status After OBBBA (2026)</h3>\n\n'
    '<p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">The federal '
    '<a href="https://www.irs.gov/credits-deductions/energy-efficient-home-improvement-credit" target="_blank" rel="nofollow noopener">'
    'Energy Efficient Home Improvement Credit (IRS Section 25C)</a> was '
    '<strong>terminated for property placed in service after Dec 31, 2025</strong> by the One Big Beautiful Bill Act '
    '(Public Law 119-21, signed July 4, 2025). HVAC equipment installed in 2026 does not qualify for the federal credit. '
    'If your HVAC was installed by Dec 31, 2025, you may still claim the credit on your 2025 tax return. For 2026 installations, '
    'focus on state Home Electrification and Appliance Rebates (HEAR) programs and your local utility&rsquo;s rebates &mdash; check the '
    '<a href="https://www.energystar.gov/rebate-finder" target="_blank" rel="nofollow noopener">ENERGY STAR Rebate Finder</a> for current programs in your ZIP.</p>'
)

def p5_replace(m):
    return P5_REPLACEMENT

# Pattern 6 — variants of "incentives stack with the federal IRS Section 25C credit"
# Some variants append a trailing dollar-amount note in parentheses; our regex
# accepts either form.
P6_RE = re.compile(
    r'All local incentives stack with the federal '
    r'<a href="https://www\.irs\.gov/credits-deductions/energy-efficient-home-improvement-credit"[^>]*>'
    r'IRS Section 25C Energy Efficient Home Improvement Credit</a>'
    r'(?: \([^)]*\))?\.'  # optional " (up to $3,200/year, ...)" trailer
)
P6_NEW = ('The federal Section 25C tax credit was terminated for installations after Dec 31, 2025 (OBBBA, P.L. 119-21) '
          '&mdash; the local incentives above remain active for 2026.')

# Pattern 7 — verbose variant where the link is followed by a colon and a list of
# dollar amounts in <strong> tags ($2,000/year heat pumps; $1,200/year others; etc).
# Match from "All local incentives stack with the federal" through to the next </p>.
P7_RE = re.compile(
    r'All local incentives stack with the federal '
    r'<a href="https://www\.irs\.gov/credits-deductions/energy-efficient-home-improvement-credit"[^>]*>'
    r'IRS Section 25C Energy Efficient Home Improvement Credit</a>: '
    r'<strong>\$2,000/year for[^<]*</strong>;[^<]*'
    r'(?:<strong>[^<]*</strong>;?[^<]*)*'
    r'(?:CEE highest efficiency tier\.)?',
    re.DOTALL
)
P7_NEW = ('The federal Section 25C tax credit was terminated for installations placed in service after Dec 31, 2025 by the '
          'One Big Beautiful Bill Act (Public Law 119-21); the local incentives above remain active for 2026 installs.')

EXCLUDE_DIRS = {'_dist', 'node_modules', '.git'}
TARGET_DIRS = ('locations',)

def main():
    counts = {f'P{i}': 0 for i in range(1, 8)}
    files_changed = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('deploy ')]
        # Only process files in TARGET_DIRS
        rel_root = os.path.relpath(root, '.').replace('\\', '/')
        if not any(rel_root == td or rel_root.startswith(td + '/') for td in TARGET_DIRS):
            continue
        for fn in files:
            if not fn.endswith('.html'):
                continue
            path = os.path.join(root, fn)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            original = content
            # Apply replacements
            if P1_OLD in content:
                counts['P1'] += content.count(P1_OLD)
                content = content.replace(P1_OLD, P1_NEW)
            if P2_OLD in content:
                counts['P2'] += content.count(P2_OLD)
                content = content.replace(P2_OLD, P2_NEW)
            if P3_OLD in content:
                counts['P3'] += content.count(P3_OLD)
                content = content.replace(P3_OLD, P3_NEW)
            if P4_OLD in content:
                counts['P4'] += content.count(P4_OLD)
                content = content.replace(P4_OLD, P4_NEW)
            new_content, n5 = P5_RE.subn(p5_replace, content)
            if n5:
                counts['P5'] += n5
                content = new_content
            new_content, n5b = P5B_RE.subn(p5_replace, content)
            if n5b:
                counts['P5'] += n5b
                content = new_content
            new_content, n6 = P6_RE.subn(P6_NEW, content)
            if n6:
                counts['P6'] += n6
                content = new_content
            new_content, n7 = P7_RE.subn(P7_NEW, content)
            if n7:
                counts['P7'] += n7
                content = new_content
            if content != original:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_changed += 1
    print(f"Files changed: {files_changed}")
    for k, v in counts.items():
        print(f"  {k}: {v} replacements")

if __name__ == '__main__':
    main()
