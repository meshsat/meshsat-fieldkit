#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3 brought to the closure (MESHSAT-1357, layer 3 round 5, 30 September 2026): the owner's
clarifications D-28 (the energy and runtime requirement), D-29 (CFL-017), D-30 (the decision register) and D-31 (one
authoritative interpretation), applied by apply_l3r5_closure.py.

It writes a closure paragraph under the section's heading, replaces the gate table and the status level paragraph that
apply_layer_status_l3_r5.py wrote with the closure's (each state at this writing; the live states stay on
REQUIREMENTS-L3-R2.md section 2), adds the completion statuses kept apart, and restates the owner's part of "Whose each
remaining item is". Each replaced text is located by its own words and asserted to occur exactly once; nothing else on
the page changes. No dash character is written. It refuses unless the closure's rulings are in the registry, and a
second run is refused.

Usage: python3 apply_layer_status_l3_r5b.py [--check] [--page PATH]   (--page: a copy of the page, for the tests)
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2"))
import l3edit as E  # noqa: E402

PAGE = os.path.join(E.TOP, "v2/docs/handover/LAYER-STATUS.md")
MARK = "**The closure (30 September 2026, D-28 to D-31, `v2/docs/records/l3r5/`).**"
HEAD = "## Layer 3. Requirements\n\n"
GATE_FROM = "**The completion gate (D-21).**"
GATE_TO = "\n\n**What the session closed (30 September 2026, `v2/docs/records/l3r2/`).**"
CLOSURE = (MARK + " The owner's clarifications close layer 3's decisions: M1's runtime is a design objective of 48 to 72 "
           "hours under a stated operating profile (REQ-072, the registry's only objective), with battery storage inside "
           "the Peli 1450, no external battery, battery and solar required, HF and the tablet functions kept and optional "
           "tablet charging reducing endurance (D-28); CFL-017 closes as a requirements conflict, the Samsung 35E being "
           "the current engineering selection, and FEA-008 carries the cell and thermal design to layer 4 mode by mode "
           "(D-29); `handover/layer3/OWNER-INSTRUCTION-2026-09-30.md` with the registry's owner rulings is the one "
           "decision register and opens with the current owner brief (D-30, D-31). Rows L3-OD2 to L3-OD7 are answered "
           "by rulings D-32 to D-37 and row L3-OD1 is closed as layer 4 architecture. **The modelled baseline misses the "
           "objective even without tablet charging**: the studied in-case store stops the kit at 05 UTC of the first "
           "night (11 to 23 hours), as drawn and on the hypothetical corrected path alike, and D-06's pack alone runs "
           "2.52 h on battery; REQ-072 reads FAIL, design risk DR-01, assigned to layer 4 with DR-02 to DR-07 "
           "(`REQUIREMENTS-L3-R2.md` section 2). **No owner decision remains**; his approval of the definition "
           "re-issue (L3-C26) and his acceptance of the baseline follow the independent check of the closure.\n\n")
GATE = ("**The completion gate (D-21, and the fifth condition of D-26).** The states below are this writing's; the live "
        "state is `REQUIREMENTS-L3-R2.md` section 2, rendered from the registry and the files `l3r2.yaml` names.\n\n"
        "| Condition | At this writing | What closes it |\n|---|---|---|\n"
        "| The target is unambiguous | MET | rows L3-OD2 to L3-OD7 answered by the owner's clarifications (D-28, D-29; "
        "rulings D-32 to D-37) and row L3-OD1 closed as layer 4 architecture, on a combination whose requirements do not "
        "contradict, with the energy basis and the power path filed with accepted checks |\n"
        "| The requirement-changing owner decisions are resolved | MET | every row settled; no contradiction between "
        "mandatory owner requirements remains (D-29's test); the runtime row filled from stream l3batt's checked "
        "comparison (fnd/l3batt 63897fc3, CHECK-3) |\n"
        "| Contradictions and requirement-level TBDs are closed | NOT MET | CFL-017 is closed (D-29) and no record reads "
        "TBD; the definition re-issue is drafted (`handover/layer3/DEFINITION-REISSUE-DRAFT.md` and its change record) "
        "and waits on the owner's approving ruling (L3-C26) |\n"
        "| An independent check accepts the handover | NOT MET | CHECK-5 of L3-R2 accepted the handover as prepared with "
        "the decisions pending; the decided issue, this closure, is checked again (L3-C27) |\n"
        "| Every recorded target has a feasibility disposition (D-26) | MET | each answered row's option carries its "
        "disposition (L3-C54), on the feasibility and runtime records bound to their checked tips |\n\n"
        "**Status level (the owner's reviewer's three, D-26).** \"Requirements drafted / decisions recorded\" holds: "
        "every row settled, the mandatory requirements and the design objective distinguishable, each with its "
        "acceptance and verification method (D-28). \"Requirements baseline validated and accepted\" does not yet: the "
        "independent check of the closure, the owner's approval of the re-issue (L3-C26) and his acceptance of the "
        "baseline remain. \"Design and hardware compliant\" is a later layers' target.\n\n"
        "**Completion statuses, kept apart (D-28, D-29).** The requirements baseline: drafted, decisions recorded, not "
        "yet validated and accepted. The circuit: not verified, board A's power path as drawn fails (DR-02) and the "
        "outlet trips below its contracts (DR-03), the corrections hypothetical and not implemented. The PCB: not "
        "verified, the layouts held until layers 4 to 8 settle the energy architecture; no V2 board fabricated. The "
        "thermal design: not verified (FEA-004, FEA-008). The runtime: not met at desk against the objective (DR-01), "
        "nothing measured. The product: not built.")
WHOSE_OLD = ("**Whose each remaining item is.** The owner: rows L3-OD1 to L3-OD6 (`OWNER-DECISIONS-L3.md`), all six with the "
             "checked figures.")
WHOSE_NEW = ("**Whose each remaining item is.** The owner: no decision (D-29's test finds no contradiction between mandatory "
             "owner requirements); the approval of the definition re-issue's change record (L3-C26) and his acceptance of "
             "the baseline, after the independent check of the closure. Before the closure: rows L3-OD1 to L3-OD6 "
             "(`OWNER-DECISIONS-L3.md`), all six with the checked figures.")


def build(t):
    if MARK in t: E.refuse("the page already carries %r: this script has run" % MARK)
    d = E.parse(open(E.REGISTRY, encoding="utf-8").read())
    have = {r["id"] for r in d["owner_rulings"]}
    for rid in ("D-28", "D-29", "D-30", "D-31", "D-37"):
        if rid not in have: E.refuse("%s is not in the registry: run the closure's scripts first" % rid)
    for x in (t.count(HEAD), t.count(GATE_FROM), t.count(GATE_TO), t.count(WHOSE_OLD)):
        if x != 1: E.refuse("the page does not carry the layer 3 texts this script restates exactly once")
    for dch in E.DASHES:
        if dch in CLOSURE + GATE + WHOSE_NEW: E.refuse("a restated text carries a dash character")
    out = t.replace(HEAD, HEAD + CLOSURE)
    a = out.index(GATE_FROM); b = out.index(GATE_TO)
    out = out[:a] + GATE + out[b:]
    return out.replace(WHOSE_OLD, WHOSE_NEW)


def main(argv):
    page = argv[argv.index("--page") + 1] if "--page" in argv and argv.index("--page") + 1 < len(argv) else PAGE
    t = open(page, encoding="utf-8").read()
    try:
        new = build(t)
    except E.Refused as e:
        print("apply_layer_status_l3_r5b: REFUSED: %s" % e)
        return 2
    print("apply_layer_status_l3_r5b: the closure written, the gate and status level restated%s" % (
        " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        open(page, "w", encoding="utf-8").write(new)
        print("apply_layer_status_l3_r5b: written %s" % os.path.relpath(os.path.abspath(page), E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
