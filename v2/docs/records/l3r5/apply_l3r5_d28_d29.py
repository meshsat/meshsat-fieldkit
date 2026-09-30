#!/usr/bin/env python3
"""Record the owner's two clarifications of 30 September 2026 that close layer 3 as owner rulings D-28 (the energy and
runtime requirement) and D-29 (CFL-017) (MESHSAT-1357, layer 3 round 5, the closure cycle). Applied once: a second run
refuses. The pattern of apply_l3r5_d26.py.

Both reached this work through the coordinating session and are filed, as quoted there, in
v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md; every quote below is asserted in that file before anything is
written. Where a sentence carries a word the registry's claim screen refuses ("guarantee", "proven"), the ruling names
the sentence instead of quoting it, and the instruction file holds it word for word. The rulings change no record: the
closure (apply_l3r5_closure.py) applies them.

Usage: python3 apply_l3r5_d28_d29.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "l3r2"))
import l3edit as E  # noqa: E402

INSTR = "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md"
Q28 = ["NO external battery. Battery storage stays inside the Peli 1450. Battery and solar remain required. Keep both HF and tablet functions. Optional tablet charging consumes the kit's available energy and reduces remaining runtime. That reduction is acceptable, including runtime falling below the baseline target. I am NOT requiring unchanged runtime while charging the tablet, a full tablet recharge every day, or an additional battery to compensate. The previous 36 Wh/day charging case can remain an illustrative calculation. It is not an approved mandatory daily charging schedule. Do not reopen external storage or removal of either function as the recommended solution.", 'Treat 48-72 hours as the baseline design target under an explicitly stated operating profile, not an unconditional guarantee under every combination of loads and weather. Do not elevate 72 hours into a mandatory minimum. Identify the essential loads, radio duty cycles, starting charge, battery assumptions and solar conditions used. Separate battery-only and solar-assisted results. Keep modelling assumptions distinct from owner-approved operating restrictions. State plainly that optional charging and additional use reduce endurance. Define charging capability within electrical and protection limits; a particular tablet model is not required merely to specify that capability. Report the actual modelled baseline runtime honestly. If the present candidate misses the target even without tablet charging, record that shortfall prominently. Do not hide it, invent a passing configuration, or describe hypothetical circuit corrections as implemented.', 'Layer 3 is complete when the requirements package is coherent, traceable, measurable, internally consistent and ready for an engineer to use. Every mandatory requirement and design objective must be distinguishable and have acceptance conditions and a verification method. Include the available feasibility evidence and clearly assigned unresolved design risks. A failed current implementation is not automatically a defective requirement. Conversely, do not conceal a demonstrated incompatibility between mandatory requirements by calling it downstream work. Layer 3 completion does not mean the circuit, PCB, thermal performance, runtime or physical product has passed verification. Keep those statuses separate.', 'Use the existing analysis and records. Have the author reconcile the affected requirements, decision register, acceptance criteria and handover package. Preserve other approved requirements; do not silently adopt the earlier ten-row recommendation string. ... Do not restart broad reviews or commission another battery comparison merely because optional charging reduces runtime.', 'If a genuine unresolved owner decision prevents closure, finish everything else and identify only the exact conflicting requirement and decision needed. Do not manufacture 100% completion, but do not keep us in review loops over an ordinary, explicitly accepted runtime trade-off.']
Q29 = ["For CFL-017, distinguish mandatory product requirements from the limitations of the currently selected Samsung 35E cells. 1. Establish whether that exact cell model is an owner-mandated constraint or an engineering selection. A mismatch with a replaceable component does not, by itself, prove that the product requirements contradict each other. 2. Separate charging, battery-powered operation and storage. Use the project's exact manufacturer specification and distinguish ambient temperature, cell temperature, storage duration and whether batteries are fitted. Do not treat one temperature limit as applying to every mode. 3. Do not automatically adopt 'the extremes apply without cells,' reduce an approved temperature requirement, or reclassify it as an objective. Those would change the product requirements and need my explicit decision. 4. Where the requirements are coherent but the current component cannot meet them, record a Layer 4 component-selection/thermal-design obligation with its feasibility uncertainty and measurable closure criterion. Do not claim that an alternative component or thermal solution has already been proven.", 'If a genuine contradiction between mandatory owner requirements remains, name the exact conflicting requirements and ask only the decision needed to resolve it. Otherwise, close the Layer 3 requirements baseline, preserve all unresolved engineering obligations explicitly ... Requirements completion must remain separate from demonstrated hardware compliance.']
P2 = Q28[1].split(" Do not elevate", 1)
P29 = Q29[0].split(" Do not claim that", 1)
RULINGS = [
    ("D-28", "the owner's clarification of the energy and runtime requirement, which closes layer 3 (30 September 2026)",
     "The owner's clarification of 30 September 2026, relayed by the coordinating session as binding and superseding "
     "earlier interpretations of the energy and runtime requirement, quoted in " + INSTR + ". In his words: \"" + Q28[0] +
     "\" Its second paragraph sets 48 to 72 hours as the baseline design target under an explicitly stated operating "
     "profile, not as a promise under every combination of loads and weather, and continues: \"Do not elevate" + P2[1] +
     "\" \"" + Q28[2] + "\" \"" + Q28[3] + "\" \"" + Q28[4] + "\""),
    ("D-29", "the owner's clarification of CFL-017: product requirements apart from the current cell (30 September 2026)",
     "The owner's clarification of 30 September 2026 on CFL-017, relayed by the coordinating session into the same closure "
     "pass and quoted in " + INSTR + ". In his words: \"" + P29[0] + "\" It closes by forbidding a claim that an "
     "alternative component or thermal solution has already been shown. \"" + Q29[1] + "\""),
]
ENTRY = '''  - id: {rid}
    authority: OWNER
    ruled_on: "2026-09-30"
    title: "{title}"
    ruling: >-
{ruling}    source: ["owner ruling {rid}", "{instr}"]
'''


def build(raw):
    d = E.parse(raw)
    have = {r["id"] for r in d["owner_rulings"]}
    if "D-28" in have or "D-29" in have: E.refuse("D-28 or D-29 is already recorded: this script has run")
    if "D-27" not in have: E.refuse("D-27 is not in the registry: run apply_l3r5_d27.py first")
    E.assert_in(INSTR, Q28 + Q29)
    for rid, title, ruling in RULINGS:
        d = E.parse(raw)
        nid = E.next_id(d, "D", ("owner_rulings",))
        if nid != rid: E.refuse("the next free owner ruling is %s, not %s: the pages cite %s" % (nid, rid, rid))
        for t in (title, ruling): E.screen(t, rid)
        raw = E.insert_after_entry(raw, d["owner_rulings"][-1]["id"], ENTRY.format(
            rid=rid, title=title, ruling=E.fold(ruling, 6), instr=INSTR), "owner_rulings")
    return raw


def main(argv):
    path = argv[argv.index("--registry") + 1] if "--registry" in argv else E.REGISTRY
    old = open(path, encoding="utf-8").read()
    try:
        new = build(old)
        before, after = E.parse(old), E.parse(new)
        got = set(E.diff_entries(before, after))
        if got != {("owner_rulings", "D-28", "added"), ("owner_rulings", "D-29", "added")}:
            E.refuse("the entries changed are not the list: %s" % sorted(got))
        errs, warns = E.validate(new)
        if errs: E.refuse("the result does not validate: %s" % "; ".join(errs[:5]))
    except E.Refused as e:
        print("apply_l3r5_d28_d29: REFUSED: %s" % e)
        return 2
    print("owner_rulings  D-28     added\nowner_rulings  D-29     added")
    print("apply_l3r5_d28_d29: 2 entries, validator 0 errors, %d warnings%s" % (len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r5_d28_d29: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
