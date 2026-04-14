#!/usr/bin/env python3
"""
One-time batch script: Add TL;DR "Key Takeaway" boxes to all 16 articles.
Inserts after the callout-danger box and before the <nav class="toc"> element.

Run: python batch_add_tldr.py
     python batch_add_tldr.py --dry-run   # preview only
"""

import os
import sys

# TL;DR content for each article file
TLDR_CONTENT = {
    # Root-level articles
    "article-emergency.html": (
        "The 7 warning signs your HVAC is failing: strange noises, burning smells, weak airflow, "
        "short-cycling, spiking energy bills, ice on the unit, and system age over 15 years. "
        "Short-cycling is the most destructive &mdash; it can burn out a compressor ($1,200&ndash;$2,800 to replace). "
        "If you hear banging, clanking, or screaming sounds, turn the system off immediately and call a professional."
    ),
    "article-ac-summer.html": (
        "If your AC dies in summer, check the thermostat, circuit breaker, and air filter before calling anyone. "
        "Common summer repairs range from $150 for a capacitor to $1,200+ for a compressor. "
        "Emergency same-day service typically adds $75&ndash;$200 above standard rates. "
        "While waiting, use window or portable AC units to cool one or two rooms and protect vulnerable household members."
    ),
    "article-furnace.html": (
        "A furnace that won&rsquo;t ignite is usually caused by a failed igniter ($100&ndash;$300 to replace), "
        "dirty flame sensor ($75&ndash;$150 to clean), or faulty pressure switch ($75&ndash;$250). "
        "A cracked heat exchanger is the most serious failure at $600&ndash;$2,500, and often means full furnace "
        "replacement ($2,500&ndash;$6,000). If you smell gas, leave the house immediately and call your gas company."
    ),
    "article-maintenance.html": (
        "A maintained HVAC system lasts 15&ndash;20 years; a neglected one fails at 10&ndash;12. "
        "Change filters every 30&ndash;90 days depending on type, schedule professional tune-ups ($80&ndash;$200) "
        "once per year for each system, and follow seasonal checklists for spring cooling prep and fall heating prep. "
        "Annual maintenance agreements covering both systems typically run $150&ndash;$350/year."
    ),
    "article-spring-ac.html": (
        "Complete 7 spring AC prep steps in March or April before the first 80&deg;F day: replace the filter, "
        "rinse the outdoor condenser, flush the condensate drain, check refrigerant line insulation, test the system, "
        "update thermostat settings, and schedule a professional tune-up ($80&ndash;$160). "
        "A spring tune-up prevents the most common first-hot-day failures and avoids summer emergency premiums."
    ),
    "article-heat-pump.html": (
        "Heat pumps handle both heating and cooling, so a single component failure can disable both modes. "
        "Common causes of cold air in winter: failed reversing valve, low refrigerant, or frozen outdoor unit. "
        "Standard heat pumps lose efficiency below 35&ndash;40&deg;F; cold-climate models work down to &minus;13&deg;F. "
        "Brief cool air during a 5&ndash;15 minute defrost cycle is normal &mdash; continuous cold air is not."
    ),
    "article-hvac-financing.html": (
        "HVAC replacement costs $5,000&ndash;$12,000+ installed. Six financing options compared: "
        "manufacturer 0% APR promotions (watch for deferred interest at 26&ndash;29.99%), HELOCs (requires 680+ credit "
        "and 20% equity), personal loans, PACE financing (no credit check, secured against property tax), "
        "utility rebates, and contractor payment plans. Federal IRA tax credits can offset $2,000+ for qualifying "
        "high-efficiency systems."
    ),
    "article-fall-prep.html": (
        "Most winter furnace failures happen during the first freeze. Complete 9 fall prep steps in "
        "September&ndash;October: schedule a tune-up, replace the filter, test the thermostat, "
        "replace CO detector batteries, inspect ductwork, clear the outdoor unit, seal air leaks, "
        "check your emergency heat source, and locate gas/electrical shutoffs. "
        "Booking early means shorter waits and lower rates before peak demand hits."
    ),
    "article-winter-storm.html": (
        "Winter storms threaten HVAC systems through blocked exhaust vents, ice-encased heat pumps, "
        "power surge damage to control boards, and frozen pipes. Switch the thermostat to OFF during outages "
        "and wait 5 minutes after power returns before turning it back on. Pipes freeze when indoor temps "
        "drop below 55&deg;F &mdash; keep faucets dripping on at-risk lines and shut off the main water supply "
        "if the home will be unoccupied."
    ),
    "article-carbon-monoxide.html": (
        "Carbon monoxide is colorless, odorless, and undetectable without a CO detector. "
        "A cracked furnace heat exchanger is one of the most common residential CO sources. "
        "At 70 ppm, symptoms appear in hours; at 400+ ppm, exposure is life-threatening within 3 hours. "
        "Place CO detectors on every level and near bedrooms. Heat exchanger replacement costs "
        "$1,500&ndash;$3,500; for furnaces over 15 years old, full replacement is usually more cost-effective."
    ),
    "article-refrigerant.html": (
        "Ice on your AC usually signals a refrigerant leak, not a minor issue. You cannot legally recharge "
        "refrigerant yourself (EPA Section 608), and &ldquo;topping off&rdquo; a leaking system wastes money &mdash; "
        "the leak must be found and repaired first. R-22 (Freon) is phased out and costs $75&ndash;$175+ per pound; "
        "R-410A is current but being phased down for R-454B. "
        "Leak detection and repair typically costs vary by location and severity."
    ),
    "article-repair-vs-replace.html": (
        "Use the $5,000 rule: multiply repair cost by system age &mdash; if the result exceeds $5,000, "
        "replacement is generally smarter. AC units last 15&ndash;20 years, furnaces 20&ndash;30 years, "
        "heat pumps 15&ndash;20 years. Upgrading from SEER 10 to SEER2 18 can cut cooling energy use by "
        "40&ndash;45%, saving $300&ndash;$600+/year. If your system uses R-22 refrigerant, any major repair "
        "should trigger a replacement conversation."
    ),
    # Subdirectory articles
    "articles/ac-compressor-buzzing-fan-not-spinning.html": (
        "If your AC compressor buzzes but the condenser fan is not spinning, turn the unit off immediately &mdash; "
        "running without airflow can burn out the compressor ($1,500&ndash;$3,000+ to replace). "
        "The 4 most likely causes: failed capacitor ($90&ndash;$300), burned-out fan motor ($150&ndash;$450), "
        "stuck contactor ($100&ndash;$350), or physical debris blocking the blade ($50&ndash;$150). "
        "None are safe DIY repairs due to high-voltage components."
    ),
    "articles/furnace-blowing-cold-air-winter.html": (
        "If your furnace runs but blows cold air, check 5 things in order: thermostat set to &ldquo;Heat&rdquo; "
        "and &ldquo;Auto&rdquo; (not &ldquo;On&rdquo;), air filter (a clogged filter triggers the high-limit "
        "switch and shuts down burners), pilot light or ignitor, flame sensor (carbon buildup is the #1 most "
        "common furnace repair, $80&ndash;$200 to clean), and gas supply valve. A dirty filter or wrong thermostat "
        "setting costs nothing to fix yourself."
    ),
    "articles/hvac-leaking-water-inside-house.html": (
        "Water leaking from your HVAC indoors is most commonly caused by a clogged condensate drain line "
        "($75&ndash;$250 to clear). Turn the system off immediately and mop up standing water &mdash; "
        "mold can start growing on wet drywall within 24&ndash;48 hours. Other causes include a cracked drain pan "
        "($150&ndash;$450), frozen evaporator coil, or a disconnected drain fitting. Ask your technician to install "
        "a safety float switch ($50&ndash;$150) to prevent future overflow."
    ),
    "articles/why-is-my-ac-blowing-warm-air.html": (
        "An AC that runs but blows warm air has 5 likely causes ranked by frequency: dirty air filter "
        "($5&ndash;$30, DIY fix), thermostat set wrong ($0), dirty condenser coil (hose it off or pay $75&ndash;$250), "
        "failed run capacitor ($90&ndash;$400, professional only), or a refrigerant leak ($200&ndash;$1,200 for "
        "repair + recharge). Turn the AC off first to prevent compressor damage, then check the filter and "
        "thermostat before calling a technician."
    ),
}

TLDR_TEMPLATE = '''
                        <div class="tldr-box">
                            <div class="tldr-label">Key Takeaway</div>
                            <p>{content}</p>
                        </div>
'''


def patch_file(filepath, tldr_content, dry_run=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already patched
    if 'tldr-box' in content:
        return 'already_done'

    # Find insertion point: after callout-danger </div>, before <nav class="toc"
    # The pattern is: </div>\n\n                        <nav class="toc"
    marker = '<nav class="toc"'
    idx = content.find(marker)
    if idx == -1:
        return 'no_toc'

    # Build TL;DR HTML
    tldr_html = TLDR_TEMPLATE.format(content=tldr_content)

    # Insert before the <nav class="toc"> line
    # Find the start of that line (go back to the newline)
    line_start = content.rfind('\n', 0, idx)
    if line_start == -1:
        return 'parse_error'

    new_content = content[:line_start] + tldr_html + content[line_start:]

    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return 'patched'


def main():
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("=== DRY RUN === \n")

    patched = 0
    skipped = 0
    errors = []

    for relpath, tldr_text in TLDR_CONTENT.items():
        filepath = relpath  # relative to project root
        if not os.path.exists(filepath):
            print(f"  ERROR (not found): {relpath}")
            errors.append(relpath)
            continue

        result = patch_file(filepath, tldr_text, dry_run)

        if result == 'patched':
            print(f"  {'WOULD PATCH' if dry_run else 'PATCHED'}: {relpath}")
            patched += 1
        elif result == 'already_done':
            print(f"  SKIP (already has TL;DR): {relpath}")
            skipped += 1
        else:
            print(f"  ERROR ({result}): {relpath}")
            errors.append(relpath)

    print(f"\nDone. Patched: {patched}, Skipped: {skipped}, Errors: {len(errors)}")
    if errors:
        print(f"Error files: {errors}")


if __name__ == '__main__':
    main()
