"""Patch cities_updated.xlsx column 17 (local_context_html) to remove stale
OBBBA / Section 25C claims that survived the earlier HTML-only corrective
sweep (commit a5d9983). The HTML files were patched but the xlsx source
data wasn't, so any v4 regeneration reintroduced the stale content.

Same regex patterns as scripts/fix_obbba_25c_stale_claims.py applied to
xlsx column 17. Idempotent — safe to re-run.
"""
import openpyxl, re

P_OLD_TO_NEW = [
    # The "All local incentives stack with the federal IRS Section 25C..." paragraph variants.
    # Variant 1 (with $2,000/$3,200 trailer in parens):
    (re.compile(
        r'All local incentives stack with the federal '
        r'<a href="https://www\.irs\.gov/credits-deductions/energy-efficient-home-improvement-credit"[^>]*>'
        r'IRS Section 25C Energy Efficient Home Improvement Credit</a>'
        r'(?: \([^)]*\))?\.'
     ),
     'The federal Section 25C tax credit was terminated for installations after Dec 31, 2025 (OBBBA, P.L. 119-21) &mdash; the local incentives above remain active for 2026.'),
    # Variant 2 (with verbose colon-list of dollar amounts):
    (re.compile(
        r'All local incentives stack with the federal '
        r'<a href="https://www\.irs\.gov/credits-deductions/energy-efficient-home-improvement-credit"[^>]*>'
        r'IRS Section 25C Energy Efficient Home Improvement Credit</a>: '
        r'<strong>\$2,000/year for[^<]*</strong>;[^<]*'
        r'(?:<strong>[^<]*</strong>;?[^<]*)*'
        r'(?:CEE highest efficiency tier\.)?',
        re.DOTALL
     ),
     'The federal Section 25C tax credit was terminated for installations placed in service after Dec 31, 2025 by the One Big Beautiful Bill Act (Public Law 119-21); the local incentives above remain active for 2026 installs.'),
    # Variant 3 ("IRS Section 25C credit" — short link text):
    (re.compile(
        r'All local incentives stack with the federal '
        r'<a href="https://www\.irs\.gov/credits-deductions/energy-efficient-home-improvement-credit"[^>]*>'
        r'IRS Section 25C credit</a>\.'
     ),
     'The federal Section 25C tax credit was terminated for installations after Dec 31, 2025 (OBBBA, P.L. 119-21) &mdash; the local incentives above remain active for 2026.'),
    # Drop the entire "Federal Tax Credits (IRS Section 25C)" H3 block — replace with OBBBA-aware H3.
    # Permissive trailer (.*?) captures any closing sentence variant —
    # "stacks with X rebates", "non-refundable", "non-refundable and stacks with X rebates", or none.
    (re.compile(
        r'<h3[^>]*>Federal Tax Credits \(IRS Section 25C\)</h3>\s*'
        r'<p[^>]*>The '
        r'<a href="https://www\.irs\.gov/credits-deductions/energy-efficient-home-improvement-credit"[^>]*>'
        r'IRS Energy Efficient Home Improvement Credit \(Section 25C\)</a> provides a federal income tax credit of up to '
        r'<strong>\$2,000 per year for a qualifying heat pump installation</strong> \(30% of cost up to the cap\) and up to '
        r'<strong>\$600 per year for a qualifying central air conditioner or natural gas furnace</strong>\. '
        r'Equipment must meet the highest (?:CEE efficiency tier|efficiency tier set by the Consortium for Energy Efficiency \(CEE\)) '
        r'in effect at the start of the calendar year of installation\..*?</p>',
        re.DOTALL
     ),
     '<h3 style="font-size: 1.2rem; color: var(--navy); margin-top: 24px;">Federal Tax Credits — Status After OBBBA (2026)</h3>\n'
     '<p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">The federal '
     '<a href="https://www.irs.gov/credits-deductions/energy-efficient-home-improvement-credit" target="_blank" rel="nofollow noopener">'
     'Energy Efficient Home Improvement Credit (IRS Section 25C)</a> was '
     '<strong>terminated for property placed in service after Dec 31, 2025</strong> by the One Big Beautiful Bill Act '
     '(Public Law 119-21, signed July 4, 2025). HVAC equipment installed in 2026 does not qualify. '
     'For 2026 installs focus on state HEAR rebates and utility programs &mdash; check the '
     '<a href="https://www.energystar.gov/rebate-finder" target="_blank" rel="nofollow noopener">ENERGY STAR Rebate Finder</a>.</p>'),
    # Trailing sentence "[X] pair with the federal IRS Section 25C [...] described below."
    # Permissive prefix — can be "Idaho Power rebates", "These", "PPL rebates", etc.
    # Permissive credit suffix — can be "credit" or "Energy Efficient Home Improvement Credit".
    (re.compile(r' (?:[A-Z][a-z]+|[A-Za-z][^.]*? rebates) pair with the federal IRS Section 25C[^.]*? described below\.'),
     ''),
    # Aggressive sentence-level fallback: any sentence still claiming the credit
    # is currently available + quoting the $2,000 / $600 dollar amounts gets
    # replaced with the OBBBA-termination sentence. This catches paragraph
    # layouts the structured H3+P regex above doesn't match (e.g. mixed-content
    # H3 like "Permit Fees & Federal Tax Credits" where the credit claim is
    # one sentence inside a permit-focused paragraph).
    (re.compile(
        r'The '
        r'<a href="https://www\.irs\.gov/credits-deductions/energy-efficient-home-improvement-credit"[^>]*>'
        r'IRS Energy Efficient Home Improvement Credit \(Section 25C\)</a> '
        r'provides a federal income tax credit of up to '
        r'<strong>\$2,000 per year for a qualifying heat pump installation</strong>'
        r'(?:\s*\(30% of cost up to the cap\))?'
        r' and up to '
        r'<strong>\$600(?: per year)? for a qualifying central (?:air conditioner|AC)(?: or natural gas)?(?: or)? furnace</strong>\.'
        r'(?: Equipment must meet[^.]*?\.)?'
        r'(?: The credit (?:is non-refundable(?: and stacks with [^.]*? rebates)?|stacks with [^.]*? rebates)\.)?'
     ),
     'The federal Section 25C credit (<a href="https://www.irs.gov/credits-deductions/energy-efficient-home-improvement-credit" target="_blank" rel="nofollow noopener">Energy Efficient Home Improvement Credit</a>) was terminated for installations placed in service after Dec 31, 2025 by the One Big Beautiful Bill Act (Public Law 119-21).'
    ),
]

def main():
    wb = openpyxl.load_workbook('cities_updated.xlsx')
    ws = wb.active
    rows_changed = 0
    pattern_counts = [0] * len(P_OLD_TO_NEW)
    for row in ws.iter_rows(min_row=2):
        cell = row[17]  # column 18, 0-indexed = 17
        original = cell.value
        if not original or not isinstance(original, str):
            continue
        new = original
        for i, (pat, repl) in enumerate(P_OLD_TO_NEW):
            new, n = pat.subn(repl, new)
            pattern_counts[i] += n
        if new != original:
            cell.value = new
            rows_changed += 1
    wb.save('cities_updated.xlsx')
    print(f"Rows updated: {rows_changed}")
    for i, n in enumerate(pattern_counts):
        print(f"  Pattern {i+1}: {n} replacements")

if __name__ == '__main__':
    main()
