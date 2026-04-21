"""
Shared DIY-hazard rules for every CoolCallPro page and article.

Why this file exists
--------------------
Cool Call Pro is a referral site. Our revenue comes from readers calling a pro.
Telling them to do hazardous work themselves:
  (a) contradicts our business model — we make zero from DIY clicks
  (b) creates real liability — 90% of consumer HVAC publishers run this advice
      because they carry media-liability insurance and rely on boilerplate
      disclaimers. We should not rely on that.
  (c) undermines brand trust — if we say "call a pro" but then tell them to
      rinse the condenser, readers learn that our "call a pro" is decoration.

Editorial rule (encoded here, enforced by audit_article.py + audit_page.py):
    Cool Call Pro instructs a homeowner to do nothing beyond:
      - Replace an air filter
      - Turn a thermostat off
      - Move physical debris away from (NOT touch) the outdoor unit
      - Call a qualified HVAC technician
    Everything else is a technician task in our voice — including things the
    broader industry considers "safe DIY."

How the detection works
-----------------------
Each DIY_HAZARD_PATTERN is a compiled regex. check_diy_hazards() finds every
match and asks: is the match preceded by an explicit negation ("do not",
"never", "avoid", "won't", "must not"), or is it in a descriptive context
referring to a technician? If yes, pass. If no, fail — the writer was telling
a homeowner to do a hazardous thing.

Adding new hazards: append to DIY_HAZARD_PATTERNS. Both audit scripts pick
them up automatically.
"""

import re


# (compiled_pattern, human_readable_description)
# Each regex matches a phrase we should NEVER advise a homeowner to perform.
# If the phrase appears inside a "do not" / "never" / technician-descriptive
# clause, check_diy_hazards() lets it through.

DIY_HAZARD_PATTERNS = [
    # --- Water near the unit ------------------------------------------------
    (re.compile(r"\bgarden hose\b", re.I),
     "garden hose (water near outdoor cabinet with potentially live wiring)"),
    (re.compile(r"\brinse (?:the |your |off |out )?(?:coil|coils|fins|condenser|unit|cabinet|outside)\b", re.I),
     "rinsing condenser / coil / fins (water near live electrical)"),
    (re.compile(r"\bspray (?:the |your )?(?:unit|condenser|coil|coils|cabinet|outdoor|fins)\b", re.I),
     "spraying the unit (water near live electrical)"),
    (re.compile(r"\bpressure[- ]wash", re.I),
     "pressure washing HVAC equipment"),
    (re.compile(r"\bhot water\b(?=[^.!?]{0,60}(?:coil|fin|cabinet|line|ice|frozen))", re.I),
     "hot water near refrigerant lines / ice / coil (thermal shock)"),

    # --- Opening enclosures -------------------------------------------------
    # (Explicitly allow filter removal — filter slot is designed to open.)
    (re.compile(r"\bremove the (?!filter\b|cleanout\b|drain\b)(?:cover|panel|access(?: panel)?|grille(?! if)|cap(?! (?:of|from) the (?:drain|cleanout))|lid)", re.I),
     "removing panels/covers (access to 240V or moving parts)"),
    (re.compile(r"\btake off the (?:cover|panel|access|lid|top)", re.I),
     "removing covers"),
    (re.compile(r"\bopen the (?:cabinet|disconnect|service panel|access panel|electrical panel|electrical service panel|breaker panel|outdoor unit|condenser|terminal box|compressor terminal)", re.I),
     "opening electrical enclosures"),
    (re.compile(r"\bpull the disconnect\b", re.I),
     "pulling the outdoor disconnect (reader should leave this to technician)"),

    # --- Electrical testing as DIY ------------------------------------------
    (re.compile(r"\btest the (?:capacitor|voltage|amperage|amps|terminal|wiring|contactor|breaker)", re.I),
     "electrical testing by homeowner"),
    (re.compile(r"\bmeasure (?:voltage|current|amperage|amps|capacitance|microfarad|resistance)", re.I),
     "amateur electrical measurement"),
    (re.compile(r"\bmultimeter\b(?=[^.!?]{0,80}(?:capacitor|contactor|terminal|voltage|amperage|amps|breaker|wire|wiring))", re.I),
     "multimeter on HVAC electrical components"),
    (re.compile(r"\bclamp meter\b(?=[^.!?]{0,80}(?:yourself|homeowner|you))", re.I),
     "clamp meter operated by homeowner"),

    # --- Internal mechanical / electrical work ------------------------------
    (re.compile(r"\btouch the (?:wire|wiring|terminal|contactor|capacitor|disconnect|lug|bus bar|breaker bus|compressor)", re.I),
     "touching live components"),
    (re.compile(r"\bjumper (?:the|wire|across|the terminals)", re.I),
     "jumping terminals"),
    (re.compile(r"\bbypass the (?:switch|safety|contactor|float|limit|float switch)", re.I),
     "bypassing safety devices"),
    (re.compile(r"\bdischarge (?:a|the) capacitor", re.I),
     "capacitor discharge"),

    # --- Internal coil / component cleaning ---------------------------------
    (re.compile(r"\bclean the (?:evaporator|indoor|inside|a[-/ ]coil|condenser|outdoor) coil", re.I),
     "indoor/outdoor coil cleaning (technician job — requires panel removal)"),
    (re.compile(r"\bstraighten the fins\b", re.I),
     "fin straightening (requires fin comb on live-voltage cabinet)"),

    # --- Gas / pilot --------------------------------------------------------
    (re.compile(r"\brelight the pilot\b", re.I),
     "relighting pilot light"),
    (re.compile(r"\bturn on the gas\b", re.I),
     "manipulating gas valve"),
    (re.compile(r"\bshut off the gas valve\b(?=[^.!?]{0,80}(?:yourself|you))", re.I),
     "gas valve operation by homeowner"),

    # --- Refrigerant -------------------------------------------------------- (reinforces EPA 608)
    (re.compile(r"\brecharge the refrigerant\b(?!.{0,40}(?:is|only a|only a certified|technician|pro(?:fessional)?))", re.I),
     "refrigerant recharge (EPA 608 forbids homeowner)"),
    (re.compile(r"\badd refrigerant\b", re.I),
     "adding refrigerant (EPA 608 forbids homeowner)"),
    (re.compile(r"\btop off (?:the )?refrigerant\b", re.I),
     "topping off refrigerant (EPA 608 forbids homeowner)"),

    # --- Blind spots revealed by the 2026-04-20 QC -------------------------
    # Short-form water instructions that escaped the "garden hose" pattern
    (re.compile(r"\bhose (?:it|them) off\b", re.I),
     "'hose it off' (short-form rinse — water near live-cabinet)"),
    # Imperative panel operation (the pattern allows \"never flip the breaker\")
    (re.compile(r"\bflip the breaker\b", re.I),
     "'flip the breaker' (service-panel operation by homeowner)"),
    (re.compile(r"\bflip(?:ping)? (?:off )?the breakers?\b", re.I),
     "flipping breakers (service-panel operation by homeowner)"),
    (re.compile(r"\bswitch off the breaker\b", re.I),
     "'switch off the breaker' (service-panel operation by homeowner)"),
    # Outdoor disconnect operation
    (re.compile(r"\bcheck the disconnect\b", re.I),
     "'check the disconnect' (outdoor disconnect operation by homeowner)"),
    (re.compile(r"\bengage the disconnect\b", re.I),
     "engaging the outdoor disconnect (homeowner task)"),
    # Temperature-split / Delta-T measurements beyond the DIY cap
    (re.compile(r"\bmeasure the (?:temperature|delta|temp)\b", re.I),
     "measuring temperature differential (tool use beyond DIY cap)"),
    (re.compile(r"\bmeasure the temperature differential\b", re.I),
     "measuring Delta-T (tool use beyond DIY cap)"),
    (re.compile(r"\bhold a thermometer\b(?=[^.!?]{0,80}(?:vent|grille|return|supply))", re.I),
     "thermometer at vents (tool use beyond DIY cap)"),
    # Gas flue / vent modification by homeowner
    (re.compile(r"\binstall(?:ing)? (?:protective )?pipe caps\b", re.I),
     "installing vent pipe caps (gas flue modification)"),
    (re.compile(r"\binstall(?:ing)? .{0,40}(?:vent (?:cap|elbow|extension)|downward[- ]facing elbow)\b", re.I),
     "installing vent terminations (gas flue modification)"),
    # Foam / insulation work on refrigerant lines
    (re.compile(r"\breplace .{0,40}(?:foam|insulation) .{0,40}(?:refrigerant|copper|line|lines|suction)\b", re.I),
     "replacing refrigerant line insulation (pressurized line, technician job)"),
    (re.compile(r"\bwrap the suction line\b", re.I),
     "wrapping the suction line (pressurized refrigerant line work)"),
    # Close-proximity instructions near the unit
    (re.compile(r"\bstand near the (?:unit|condenser|outdoor|furnace)\b", re.I),
     "'stand near the unit' (close proximity to malfunctioning equipment)"),
    (re.compile(r"\bsniff near the (?:furnace|unit|gas|heater|boiler)\b", re.I),
     "'sniff near the furnace' (close proximity to gas appliance)"),
    (re.compile(r"\bwalk the length of the refrigerant lines?\b", re.I),
     "walking along refrigerant lines (close inspection)"),
    (re.compile(r"\bwalk around the (?:entire )?(?:unit|condenser|outdoor|furnace)\b", re.I),
     "walk-around inspection (close range, homeowner-diagnostic)"),
    # "Fix yourself" / DIY-endorsing framings
    (re.compile(r"\bfix (?:it )?yourself\b", re.I),
     "'fix yourself' (DIY-endorsing framing)"),
    (re.compile(r"\bstraightforward DIY task\b", re.I),
     "'straightforward DIY task' (DIY-endorsing framing)"),
    (re.compile(r"\bbasic DIY (?:task|tune[- ]up|job)\b", re.I),
     "'basic DIY' framing"),
    # Pouring water on equipment (thermal shock, electrical risk)
    (re.compile(r"\bpour(?:ing)? .{0,30}water (?:over|on|onto) (?:the )?(?:unit|coil|condenser|vent|pipe)\b", re.I),
     "pouring water on equipment"),
    # Chipping / scraping ice off equipment
    (re.compile(r"\bchip(?:ping)? (?:the )?ice\b", re.I),
     "chipping ice off equipment (fin damage + electrical risk)"),
    (re.compile(r"\bscrape (?:the )?(?:ice|snow) (?:off|from)", re.I),
     "scraping ice/snow off equipment"),
    # Inspecting refrigerant lines / coil fins (close range)
    (re.compile(r"\binspect the refrigerant line\b", re.I),
     "inspecting refrigerant lines (close proximity to pressurized line)"),
    (re.compile(r"\binspect(?:ion)? (?:the )?coil fins?\b", re.I),
     "coil-fin inspection (close range, requires cabinet proximity)"),
]


# Negation / technician-descriptive context: if any of these phrases appear
# in the ~100 chars preceding a hazard match, the hazard is allowed (the
# writer is telling the reader NOT to do it, or describing what a technician
# does).

_NEGATION_RE = re.compile(
    r"\b(?:do not|don't|never|must not|cannot|should not|shouldn't|avoid(?:ing)?|"
    r"won't|will not|isn't|is not|aren't|are not|no homeowner|not a (?:diy|homeowner)|"
    r"technician (?:will|can|should|must|is|uses|handles|performs|does|quotes)|"
    r"a technician|the technician|a pro(?:fessional)?|a qualified|an hvac|"
    r"what (?:a|the) (?:technician|pro|professional) (?:will|does|checks|measures)|"
    r"professional (?:will|can|should|must|is|uses|handles|performs|does)|"
    r"only a (?:certified|qualified|licensed|professional)|"
    r"we do not|we don't|cool call pro (?:does not|doesn't))",
    re.I,
)

# FAQ schema questions naturally contain hazardous phrases because the answer
# negates them ("Can I pour hot water on the ice?" → answer: "No."). If the
# hazard appears inside a Question "name" field, allow it.
_FAQ_QUESTION_CONTEXT = re.compile(
    r'"name"\s*:\s*"[^"]{0,200}$', re.I,
)
# Visible FAQ question button text — <button class="faq-q" ...>...<span>QUESTION</span>
_FAQ_VISIBLE_CONTEXT = re.compile(
    r'class="faq-q"[^>]*>\s*<span>[^<]{0,200}$', re.I,
)


def check_diy_hazards(html: str, source_label: str = "") -> int:
    """Check an HTML file's rendered + JSON-LD text for un-negated DIY hazards.

    Returns the count of failures. Prints PASS/FAIL lines.

    The negation window is ~500 chars backward from each match. That captures
    most "a technician will [check / use / measure] X" descriptive contexts
    and most "Do NOT attempt to..." bullet-list prefaces where the hazard sits
    in a list item 2-3 items after the introducing paragraph. Genuinely
    un-negated DIY instructions almost never have a negation 500 chars away.
    """
    suffix = f" — {source_label}" if source_label else ""
    print(f"\nDIY-HAZARD AUDIT (homeowner-advice safety){suffix}")
    fails = 0
    for pattern, description in DIY_HAZARD_PATTERNS:
        for match in pattern.finditer(html):
            start = match.start()
            context_start = max(0, start - 500)
            preceding = html[context_start:start]
            preceding_text = re.sub(r"<[^>]+>", " ", preceding)
            if _NEGATION_RE.search(preceding_text):
                continue
            # Allow hazards inside FAQ Question name fields (JSON or visible)
            if _FAQ_QUESTION_CONTEXT.search(preceding) or _FAQ_VISIBLE_CONTEXT.search(preceding):
                continue
            fails += 1
            snippet_start = max(0, start - 40)
            snippet_end = min(len(html), match.end() + 40)
            snippet = re.sub(r"\s+", " ", html[snippet_start:snippet_end]).strip()
            print(f"  [FAIL] DIY hazard: '{match.group(0)}' — {description}")
            print(f"         context: ...{snippet}...")
    if fails == 0:
        print("  [PASS] No un-negated DIY-hazard phrases detected")
    return fails


if __name__ == "__main__":
    # Allow direct invocation against a file for ad-hoc inspection
    import sys
    from pathlib import Path
    if len(sys.argv) != 2:
        print("Usage: python safety_rules.py <path-to-html>")
        sys.exit(2)
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    n = check_diy_hazards(text, source_label=sys.argv[1])
    sys.exit(0 if n == 0 else 1)
