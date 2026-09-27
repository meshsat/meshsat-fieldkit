"""verify c7, item (6): the handover pages still carried the mock-up's earlier timing. Each line keeps its audit
wording where it records a state at e3aedb25 and gains what the layer 7 merge adopted. Run from the worktree root."""
def edit(p, pairs):
    t = open(p).read()
    for a, b in pairs:
        assert t.count(a) == 1, (p, t.count(a), a[:100]); assert a != b; t = t.replace(a, b)
    assert chr(0x2014) not in t; open(p, 'w').write(t)
T = ("before the layout entry of boards A, B, E and P, which is BLOCKED on the purchase since 27 September 2026 "
     "(FEA-007, L-07; `v2/docs/CASE-FIT-UNCERTAINTIES.md` sections 1, 2 and 7)")
edit('v2/docs/handover/ENGINEERING-QUESTIONS.md', [
    ("| **Recommended next action** | Close the desk items first (the jumper plug pick, the sealed RJ45 re-pick, the drawings of the made parts), then (c) in the same case as the heat test (EQ-05), before board B's layout entry. |",
     "| **Recommended next action** | Close the desk items first (the jumper plug pick, the sealed RJ45 re-pick; the drawings of the made parts are done, `v2/release/case-2026-09-27/`), then (c) in the same case after the heat test (EQ-05), %s; option (b) is withdrawn by that allocation (the owner's execution prompt of 27 September 2026, sections 2 and 5). With one case the mock-up follows the heat test, so boards B and E wait on that test too; a second case would decouple them (`v2/docs/reviews/READY-TO-ACT.md` S-1). |" % T),
])
edit('v2/docs/handover/CONTINUATION-BRIEF.md', [
    ("| Mock-up timing | before board outlines and connector places freeze (CASE-MARGINS section 7, seventh revision; the owner's second review, section 3) | CONOPS section \"4a. Power states\" and READY-TO-ACT 6.1 (\"at the build\") | edit owed |",
     "| Mock-up timing | %s; boards C, D and E5 not held (CASE-MARGINS section 7 since the layer 7 merge; the seventh revision's \"before outlines freeze\" and its fabrication-release fallback are withdrawn) | none: CONOPS section \"4a. Power states\", READY-TO-ACT 6.1 and S-8, ARCHITECTURE section 7, the layout-constraint README, OPERATING-ENVELOPE's pack row and REQ-019 carry it since the layer 7 merge | done at the layer 7 merge |" % T),
    ("5. Ask the owner for the authorisations on the critical path: the empty-case heat test and the case mock-up (before\n   hot-part placement and outlines freeze),",
     "5. Ask the owner for the authorisations on the critical path: the empty-case heat test and the case mock-up (the\n   heat test before hot-part placement freezes; the mock-up %s, after the heat test in the same case),"
     % T.replace("since 27 September 2026 ", "since 27 September 2026\n   ")),
])
edit('v2/docs/handover/LAYER-STATUS.md', [
    ("- The case mock-up is recommended before outlines freeze and carried to fabrication release if not run; M17g and M17x\n  fail as assumed,",
     "- The case mock-up was recommended before outlines freeze and carried to fabrication release if not run; since the\n  layer 7 merge its board-moving checks are required %s. M17g and M17x\n  fail as assumed," % T),
    ("  close before layout entry and keep the carry-over explicit per board.",
     "  close before layout entry and keep the carry-over explicit per board. (Done at the layer 7 merge: option (c) is\n  withdrawn and FEA-007 holds the layout entry of boards A, B, E and P on the mock-up.)"),
])
print("edit_c7_handover: done")
