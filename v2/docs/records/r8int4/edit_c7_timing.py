"""verify c7's contradictions, fixed on the r8int4 tree after fnd/hc7's patches: READY-TO-ACT's one-case order stated
with its consequence for layout entry (section 0, section 1, 5.1, S-1, S-8), and every page that still carried the
mock-up at the build or at fabrication release (ARCHITECTURE section 7, the layout-constraint sheets' README,
OPERATING-ENVELOPE's pack row, V2-SPEC correction 18, the handover pages). Session wording under the owner's standing
rule of 26 September 2026. Each edit asserts its old text. Run from the worktree root."""
def edit(p, pairs):
    t = open(p).read()
    for a, b in pairs:
        assert t.count(a) == 1, (p, t.count(a), a[:100]); assert a != b; t = t.replace(a, b)
    assert chr(0x2014) not in t; open(p, 'w').write(t)
R = 'v2/docs/reviews/READY-TO-ACT.md'
edit(R, [
    ("| case EUR 168.90 and frame EUR 29.66 excl. VAT, logger GBP 349, all VERIFIED; plate blank, heaters, fans TBD | FB-PWR's enclosure conductance and the PA patch (PWR-F15) | section 5 |",
     "| case EUR 168.90 and frame EUR 29.66 excl. VAT, logger GBP 349, all VERIFIED; plate blank, heaters, fans TBD | FB-PWR's enclosure conductance and the PA patch (PWR-F15); and, while one case serves items 8 and 9 (S-1), item 9 and with it the layout entry of boards A, B, E and P | section 5 |"),
    ("Items 8 and 9 use one case, in that order (section 11, S-1). The case, its frame,",
     "Items 8 and 9 use one case, in that order (section 11, S-1): the heat-balance test needs the sealed skin and runs\n"
     "first, and the mock-up then drills the same case. Because the layout entry of boards A, B, E and P waits on item 9\n"
     "(FEA-007, section 6.1), with one case it also waits on item 8: boards A and P wait on item 8 anyway (FEA-004, the\n"
     "placement freeze of the pack and the PA's flange site), boards B and E only through this order. A second case would\n"
     "let the two run side by side; buying it is the owner's purchase decision, recorded in S-1 as the alternative and not\n"
     "taken. The case, its frame,"),
    ("layout entry of boards A, B, E and P waits on item 9, the case mock-up, FEA-007, section 6.1; their desk items do\nnot);",
     "layout entry of boards A, B, E and P waits on item 9, the case mock-up, FEA-007, section 6.1, and with one case for\nitems 8 and 9 on item 8 before it, S-1; their desk items do not);"),
    ("- **Proceeds before it:** every circuit and layout draft; the thermal limits stay PROVISIONAL meanwhile.\n- **Waits on it:** freezing the placement of the pack and the PA's flange site; the +35 C and +25 C controls leaving\n  \"proposed\"; PWR-F15's thresholds.",
     "- **Proceeds before it:** every circuit and layout draft, and the layout entry of boards C, D and E5; the thermal\n  limits stay PROVISIONAL meanwhile.\n- **Waits on it:** freezing the placement of the pack and the PA's flange site; the +35 C and +25 C controls leaving\n  \"proposed\"; PWR-F15's thresholds; and, while one case serves both tests (section 11, S-1), the case mock-up that\n  follows it in that case (section 6), so the layout entry of boards A, B, E and P."),
    ("  it is the prototype's own case (D-08a). Why: the heat test needs the sealed skin, the mock-up needs the holes, and a\n  second case buys nothing the first cannot show.",
     "  it is the prototype's own case (D-08a). Why: the heat test needs the sealed skin and the mock-up needs the holes, so\n"
     "  one case serves both in that order. Consequence since 27 September 2026 (S-8): the layout entry of boards A, B, E\n"
     "  and P waits on the mock-up and so, with one case, on the heat test before it; boards A and P wait on the heat test\n"
     "  anyway (FEA-004), boards B and E only through this order. A second case (EUR 168.90 and EUR 29.66 excl. VAT for the\n"
     "  frame, VERIFIED, section 0 item 8) would let the two run side by side and free B's and E's layout entry from the heat\n"
     "  test; it is a purchase, so it is the owner's (D-09), and it is recorded here as the alternative, not taken.\n"
     "  Reversal: the owner buys a second case; the mock-up then runs as soon as its parts are in."),
    ("  the mock-up's readings meeting the rows' minimums lift the hold; only the owner can instead accept entering layout on\n  the design basis as his residual risk.",
     "  the mock-up's readings meeting the rows' minimums lift the hold; only the owner can instead accept entering layout on\n  the design basis as his residual risk. With one case for the heat test and the mock-up (S-1) the mock-up runs after the\n  heat test, so this hold lifts no earlier than that test's end unless a second case is bought."),
])
edit('v2/docs/ARCHITECTURE.md', [
    ("unpowered mock-up in a new case of the current moulding, now recommended before the outlines and connector placements\n"
     "of boards A, B, C, E and P freeze for routing; if it has not run by then, those rows move to the boards' fabrication\n"
     "release. Nothing is asked of the owner; buying the case and the mock-up's parts stays his decision.",
     "unpowered mock-up in a new case of the current moulding. Since 27 September 2026 its checks of the rows that can move\n"
     "a board are required before the layout entry of boards A, B, E and P, and that layout entry is BLOCKED on the\n"
     "purchase (FEA-007; `CASE-FIT-UNCERTAINTIES.md` sections 1, 2 and 7; `CASE-MARGINS.md` section 7, whose earlier\n"
     "fallback to the boards' fabrication release is withdrawn); boards C, D and E5 are not held by it. Nothing is asked of\n"
     "the owner; buying the case and the mock-up's parts stays his decision."),
    ("moulding by the assembler, recommended first on the unpowered mock-up; a check that fails stops the build.",
     "moulding by the assembler: the checks of the rows that can move a board on the unpowered mock-up before the layout\n"
     "entry of boards A, B, E and P (FEA-007), the rest first on the mock-up too; a check that fails stops the build."),
])
edit('v2/docs/layout-constraints/README.md', [
    ("`v2/docs/CASE-MARGINS.md` is the case's record against Peli's own figures. Its finding 28: the targeted mock-up\n"
     "checks T1, T2, T4, T5, T6, T10 and T11 are recommended **before the outlines and connector placements of boards A, B,\n"
     "C, E and P are frozen for routing**. If the case and the mock-up parts are not bought by then, those boards enter\n"
     "layout on the nominal geometry with the OPEN rows named. The sheets name the rows that bear on each board.",
     "`v2/docs/CASE-MARGINS.md` is the case's record against Peli's own figures. Since 27 September 2026 the targeted\n"
     "mock-up's checks of the rows that can move a board are **required before the layout entry of boards A, B, E and P**,\n"
     "and that layout entry is **BLOCKED** on the purchase (FEA-007; `CASE-FIT-UNCERTAINTIES.md` sections 1, 2 and 7;\n"
     "`CASE-MARGINS.md` section 7 and finding 28). No board of the four enters layout on the nominal geometry in their\n"
     "place; boards C, D and E5 are not held by it. The sheets name the rows that bear on each board."),
])
edit('v2/docs/OPERATING-ENVELOPE.md', [
    ("M4a and M5 OPEN until the pack's hold-down and a mock-up at the build).",
     "M4a and M5 OPEN until the pack's hold-down and the targeted mock-up before boards A and P enter layout)."),
])
edit('v2/docs/V2-SPEC.md', [
    ("on a targeted unpowered mock-up recommended for the build stage",
     "on a targeted unpowered mock-up recommended for the build stage (its timing since 27 September 2026: the checks of the rows that can move a board run before the layout entry of boards A, B, E and P, which is BLOCKED on the purchase, FEA-007 and `CASE-MARGINS.md` section 7)"),
])
print("edit_c7_timing: done")
