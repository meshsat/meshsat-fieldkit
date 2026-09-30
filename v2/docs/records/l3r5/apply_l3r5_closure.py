#!/usr/bin/env python3
"""Apply the owner's clarifications D-28 (the energy and runtime requirement) and D-29 (CFL-017) to the requirements
registry: layer 3's closure (MESHSAT-1357, round 5, 30 September 2026). Applied once: a second run refuses.

What it writes, and nothing else (every other approved requirement is preserved, D-28):
  1. owner rulings that record D-28's and D-29's answers to the rows of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md,
     each naming its row and carrying the owner's words: L3-OD7 objective-48-72 (HF available, no external battery,
     the tablet's charging optional), L3-OD2 both-kept, L3-OD3 unchanged, L3-OD4 reject, L3-OD5 layer4-obligation and
     L3-OD6 mean-day in TYP. Row L3-OD1 is not answered by a ruling: the store's size and arrangement is layer 4
     architecture (l3r2.yaml's closed_as, the session's under D-21 and D-28);
  2. REQ-072 restated as the DESIGN OBJECTIVE D-28 sets (obligation OBJECTIVE, its operating profile, MUST_JUSTIFY), its
     modelled baseline added as evidence, read by runtime_reader.py from the bound runtime.out: it reads FAIL;
  3. REQ-014: the store inside the Peli 1450 and no external battery; REQ-011: the tablet's charging as a capability at the
     outlet, no tablet model needed, optional and reducing endurance; REQ-017: R138's trip named (CHECK-3 of stream
     l3batt); REQ-002 and REQ-016: kept unchanged, with D-28 named; REQ-051: CFL-017's closure named;
  4. CFL-017 resolved (D-29: the collision is with the current cell, an engineering selection, and the current thermal
     design; the requirements are coherent) and FEA-008, the layer 4 component-selection and thermal-design obligation,
     whose blocker ids are the modes of l3r2.yaml's cell_modes on the requirements page;
  5. M-02 closed by D-28.
The result is re-parsed, compared with the declared list of changed entries and validated (0 errors).

Usage: python3 apply_l3r5_closure.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2", "conditional"))
import l3edit as E  # noqa: E402
import cond as C  # noqa: E402
import runtime_reader as RR  # noqa: E402

INSTR = "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md"
PAGE = "v2/docs/handover/layer3/OWNER-DECISIONS-L3.md"
REQ_PAGE = "v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md"
RUNTIME = "v2/docs/records/l3batt/runtime.out"
DATE = "2026-09-30"
W28 = {
    "L3-OD7": "Treat 48-72 hours as the baseline design target under an explicitly stated operating profile [...] Do not "
              "elevate 72 hours into a mandatory minimum. [...] NO external battery. [...] Keep both HF and tablet functions. "
              "Optional tablet charging consumes the kit's available energy and reduces remaining runtime. That reduction is "
              "acceptable, including runtime falling below the baseline target.",
    "L3-OD2": "Keep both HF and tablet functions.",
    "L3-OD3": "Preserve other approved requirements; do not silently adopt the earlier ten-row recommendation string.",
    "L3-OD4": "Keep modelling assumptions distinct from owner-approved operating restrictions.",
    "L3-OD5": "Where the requirements are coherent but the current component cannot meet them, record a Layer 4 "
              "component-selection/thermal-design obligation with its feasibility uncertainty and measurable closure "
              "criterion.",
    "L3-OD6": "Identify the essential loads, radio duty cycles, starting charge, battery assumptions and solar conditions used.",
}
ANSWERS = [   # (row, option, source ruling, title, ruling text, extra fields)
    ("L3-OD7", "objective-48-72", "D-28", "M1's runtime: 48 to 72 hours, a design objective under the stated profile (row L3-OD7)",
     "Row L3-OD7 of %s decided by the owner's clarification D-28: M1's runtime is 48 to 72 hours, the baseline design target "
     "under the explicitly stated operating profile of REQ-072, not a mandatory minimum; no external battery; HF and the "
     "tablet functions kept, HF available and not receiving in the profile, listening an additional use; the tablet's "
     "charging optional, consuming the kit's energy and reducing endurance, which the owner accepts. Neither Option A nor "
     "Option B of the runtime comparison is adopted, and no external store is recommended (D-28)." % PAGE,
     {"m1_hf": "available", "m1_external": '"no"', "m1_tablet_charging": "optional"}),
    ("L3-OD2", "both-kept", "D-28", "Both lid items kept, the QMX HF set and the tablet bracket (row L3-OD2)",
     "Row L3-OD2 of %s decided by the owner's clarification D-28: both approved lid items stay, the QMX HF set in its lid "
     "tray (appendix 32.50 item 16a) and the tablet bracket (item 16d); no function leaves the kit. The lid pack Option "
     "A(i) would add is layer 4 architecture (row L3-OD1)." % PAGE, {}),
    ("L3-OD3", "unchanged", "D-28", "REQ-016's approved solar window unchanged (row L3-OD3)",
     "Row L3-OD3 of %s decided by the owner's clarification D-28: REQ-016's approved solar window stays unchanged; the "
     "2S2P array into a 200 W stage is a layer 4 architecture proposal with Option A(i), which would need the owner's "
     "ruling to change REQ-016." % PAGE, {}),
    ("L3-OD4", "reject", "D-28", "No deployment condition at layer 3 (row L3-OD4)",
     "Row L3-OD4 of %s decided by the owner's clarification D-28: no deployment condition is stated at layer 3; the single "
     "benchmark plane is a modelling assumption of REQ-072's profile, not an operating restriction, and the open kit's "
     "stability goes with Option A(i)'s lid pack to layer 4." % PAGE, {}),
    ("L3-OD5", "layer4-obligation", "D-29", "CFL-017 closed as a requirements conflict; the cell and thermal design a layer 4 obligation (row L3-OD5)",
     "Row L3-OD5 of %s decided by the owner's clarification D-29: judged mode by mode against the project's maker sheets, "
     "CFL-017's collisions are between the requirements (D-02, D-02a, TEST-PLAN E5, with the pack fitted) and the current "
     "cell, the Samsung 35E, an engineering selection D-06's pack carries, with the current thermal design; the "
     "requirements are coherent. CFL-017 closes as a requirements conflict, FEA-008 carries the component-selection and "
     "thermal-design obligation to layer 4 mode by mode, and no temperature requirement is reduced, read as the kit's "
     "without its cells or reclassified." % PAGE, {}),
    ("L3-OD6", "mean-day", "D-28", "M1's solar conditions: SC-37's mean day, one plane, TYP (row L3-OD6)",
     "Row L3-OD6 of %s decided by the owner's clarification D-28: REQ-072 is judged under SC-37's reference mean day at "
     "Leiden on one plane, 40 degrees facing south, in the typical array build (TYP), the worst array build (WAB) a "
     "sensitivity; a benchmark, not a promise under every combination of loads and weather; no coverage target." % PAGE,
     {"weather_build": "TYP", "weather_share": None}),
]
PROFILE = ("The essential loads of PS-IDLE-SPEC, 42.8 W at the pack terminals over its 39 loads (POWER-THERMAL.md "
           "section 4); the radio duty cycles of that state, HF available and not receiving (the QMX's USB and HDMI 5 V, "
           "0.32 W), HF listening (1.14 W more) an additional use; the tablet not charged, the USB-C outlet off; a full "
           "store at the start, aged to 80 percent of the cells' specification minimum (REQ-014), each pack to its "
           "graceful line (5 percent relative state of charge, or its lowest cell at 3.00 V under load); battery-only at "
           "+20 C and -10 C; solar-assisted on SC-37's reference mean day at Leiden on one plane, 40 degrees facing south, "
           "in the typical array build (TYP), the worst array build (WAB) a sensitivity, from starts at 06 and 18 UTC. "
           "These are modelling assumptions, not owner-approved operating restrictions (D-28).")


def baseline(rid7):
    """REQ-072's baseline evidence, every figure read from the bound runtime.out by exact keys."""
    t = open(os.path.join(E.TOP, RUNTIME), encoding="utf-8").read()
    b, sol, cov = RR.battery_only(t), RR.solar(t), RR.coverage(t)
    if not RR.reproduced(t): E.refuse("runtime.out does not read its reproduction lines as yes")
    stops = sol[("48", "NOM", "TYP")]["stops"].split("/")
    return ("The modelled baseline (the owner's clarification D-28: reported honestly, the shortfall recorded "
            "prominently), read from %s, the output of v2/docs/records/l3batt/runtime.py (stream l3batt, checked), by "
            "v2/docs/records/l3r5/runtime_reader.py for %s: with HF and the tablet kept "
            "and no tablet charging, battery-only from full, D-06's 4S3P pack runs %s h at +20 C (%s h at -10 C) and the "
            "studied in-case candidate, Option A(i)'s base 4S6P and a 4S9P lid (%s Wh usable aged at +20 C), %s h (%s h "
            "at -10 C); solar-assisted on the mean day in TYP the candidate stops at 05 UTC of the first night, hour %s "
            "from a 06 UTC start and hour %s from an 18 UTC start, as drawn (%s Wh unserved at 48 h, %s Wh at 72 h) and on "
            "the hypothetical corrected path (%s Wh at 48 h, %s Wh at 72 h, NOM) alike, in %s of 864 past September "
            "windows at 48 h and %s at 72 h. The objective's lower end is missed even without tablet charging: design "
            "risk DR-01, assigned to layer 4. The corrected path is not implemented. Reads FAIL." % (
                RUNTIME, rid7, b["D06"]["hours_20"], b["D06"]["hours_m10"], b["A35"]["usable_20"], b["A35"]["hours_20"],
                b["A35"]["hours_m10"], stops[0], stops[1], sol[("48", "DRAWN", "TYP")]["unserved"],
                sol[("72", "DRAWN", "TYP")]["unserved"], sol[("48", "NOM", "TYP")]["unserved"],
                sol[("72", "NOM", "TYP")]["unserved"], cov[("48", "NOM")][0], cov[("72", "NOM")][0]))


def fea_entry(fid, rid5):
    import yaml
    data = yaml.safe_load(open(C.L3DATA, encoding="utf-8"))
    modes = {m["id"]: m for m in data["cell_modes"]}
    ids = [i for i in ("LO-01a", "LO-01d", "LO-01e", "LO-01f", "LO-01g", "LO-01h") if i in modes]
    page = open(os.path.join(E.TOP, REQ_PAGE), encoding="utf-8").read()
    for i in ids:
        if "| %s |" % i not in page: E.refuse("%s is not on %s: render the pages first" % (i, REQ_PAGE))
    st = ("The owner's clarification D-29 judged CFL-017 mode by mode against the project's maker sheets (Samsung "
          "INR18650-35E Ver. 1.1, at the cell surface; Version 1.0, ambient): the requirements are coherent, and with the "
          "pack fitted the current cell and thermal design fall short of them in use at the envelope's +40 C by %s "
          "(LO-01a), at D-02a's +55 C operating margin by %s (LO-01d), in TEST-PLAN E5's humid dwell by %s (LO-01e), at the "
          "+71 C storage margin by %s (LO-01f) and at the -33 C storage margin by %s (LO-01g); storage inside the envelope "
          "collides only on Version 1.0 (LO-01h). A layer 4 component selection and thermal design owes each closure; no "
          "alternative cell or thermal solution is shown." % tuple(modes[i]["gap"] for i in ("LO-01a", "LO-01d", "LO-01e",
                                                                                               "LO-01f", "LO-01g")))
    acc = ("Each of %s closed by its criterion in the cell modes table of %s: a cell whose maker's sheet rates the mode's "
           "range, or a thermal design holding every cell inside its governing limits, shown by the named TEST-PLAN run "
           "with the pack fitted and a thermocouple on every cell." % (", ".join(ids), REQ_PAGE))
    closing = ("The chosen cell's maker's sheet filed in v2/vendor/battery/ with its ratings against each mode, or the "
               "thermal design's model, and the TEST-PLAN runs E3-A, E3-L, E3-O, E3-S, E4-S and E5 with the pack fitted.")
    owner = ("The session at layer 4 (the cell's selection and the thermal design); the owner for the spend on another cell "
             "(D-09) and D-06's parenthesis restated.")
    why = ("The obligation follows its parent need's place (NEED-15, deferred), as CFL-017 did; the use at +40 C it names "
           "is also FEA-004's, a core blocker.")
    files = ["v2/vendor/battery/samsung-35e-orbtronic.pdf", "v2/vendor/battery/samsung-35e-akkuzentrum.pdf",
             "v2/docs/OPERATING-ENVELOPE.md", "v2/docs/TEST-PLAN.md"]
    ev = ("The maker's sheets v2/vendor/battery/samsung-35e-orbtronic.pdf (Ver. 1.1, clauses 3.12 and 3.13) and "
          "samsung-35e-akkuzentrum.pdf (Version 1.0, clauses 3.15 and 3.16), v2/docs/OPERATING-ENVELOPE.md sections 3 and "
          "8 and v2/docs/TEST-PLAN.md's E3 to E5 rows, read for D-29 in layer 3's closure (round 5): the cell modes table "
          "of l3r2.yaml, each gap recomputed by test_l3r5.py from the figures beside it.")
    notes = ("Created by layer 3's closure (round 5) on D-29 (%s, row L3-OD5). The cell's provenance is l3r2.yaml's "
             "cell_provenance: the Samsung 35E is named in the owner's pack rulings as the pack's content, D-06 was ruled at "
             "the session's recommendation, and no ruling states the model as a product requirement." % rid5)
    for x in (st, acc, closing, owner, why, ev, notes): E.screen(x, fid)
    return ("  - id: %s\n    kind: feasibility\n    parent: NEED-15\n    title: \"the current cell and thermal design "
            "against the temperature requirements with the pack fitted (CFL-017's modes, layer 4)\"\n    statement: >-\n%s"
            "    acceptance: >-\n%s    feasibility_page: %s\n    blocker_ids: [%s]\n    closing_evidence: >-\n%s"
            "    owner: >-\n%s    blocks: [REQ-051, REQ-025, REQ-074]\n    allocated_to: [kit, procedure]\n"
            "    verification_method: [CALCULATION, MANUAL_REVIEW, PROTOTYPE_MEASUREMENT]\n    verification_phase: SCHEMATIC\n"
            "    final_phase: PROTOTYPE\n    prototype_1: deferred\n    prototype_1_basis: NEED_DEFAULT\n"
            "    satisfied_by:\n      rules: []\n      decisions: []\n    rule_coverage: NONE\n"
            "    rulings: [D-02a, D-06, D-29, %s]\n    choices: [SC-19]\n    status: FEASIBILITY_OPEN\n"
            "    evidence_result: INCONCLUSIVE\n    evidence_phase: SCHEMATIC\n    evidence_class: DESK_REVIEW\n"
            "    evidence:\n      - >-\n%s    evidence_bound_to: [%s]\n    release_effect: MUST_JUSTIFY\n"
            "    source: [\"owner ruling D-29\", \"v2/vendor/battery/samsung-35e-orbtronic.pdf\", "
            "\"v2/vendor/battery/samsung-35e-akkuzentrum.pdf\", \"v2/docs/OPERATING-ENVELOPE.md\"]\n"
            "    source_check: VERIFIED\n    notes: >-\n%s" % (
                fid, E.fold(st, 6), E.fold(acc, 6), REQ_PAGE, ", ".join(ids), E.fold(closing, 6), E.fold(owner, 6), rid5,
                E.fold(ev, 10), ", ".join("%s@%s" % (f, E.sha16(os.path.join(E.TOP, f))) for f in files), E.fold(notes, 6)))


def build(raw):
    d = E.parse(raw)
    have = {r["id"] for r in d["owner_rulings"]}
    if any(str(r.get("decides") or "").startswith("L3-OD") for r in d["owner_rulings"]):
        E.refuse("rows of layer 3 are already decided in this registry: this script has run")
    for rid in ("D-28", "D-29", "D-30"):
        if rid not in have: E.refuse("%s is not in the registry: run apply_l3r5_d28_d29.py and apply_l3r5_d30.py first" % rid)
    E.assert_in(INSTR, list(W28[r].replace("[...] ", "") for r in ("L3-OD2", "L3-OD3", "L3-OD4", "L3-OD5", "L3-OD6")))
    exp = set()
    rid_of = {}
    for row, opt, src, title, ruling, extra in ANSWERS:
        d = E.parse(raw)
        raw, rid = C.add_ruling(raw, d, row, opt, title, ruling, W28[row], DATE, extra=extra)
        raw = E.replace_entry(raw, rid, lambda b, src=src: E.set_flow(b, "source", ['"owner ruling %s"' % src, '"%s"' % INSTR,
                                                                                    '"%s"' % PAGE]), "owner_rulings")
        rid_of[row] = rid
        exp.add(("owner_rulings", rid, "added"))
    r7, r5 = rid_of["L3-OD7"], rid_of["L3-OD5"]
    stamp = "D-28 applied by %s (layer 3's closure, %s)" % (r7, DATE)
    d = E.parse(raw)
    recs = {r["id"]: r for r in d["records"]}
    # REQ-072: the design objective
    st = ("Design objective (the owner's clarification D-28, not a mandatory minimum): under the operating profile stated "
          "in objective_profile, the kit's own store inside the Peli 1450 plus its solar input keep the kit serving its "
          "loads for 48 to 72 hours of mission M1 (CONOPS section 3), 48 hours the lower end and 72 hours the upper end of "
          "the baseline design target, from a full, aged store (REQ-014). Battery-only and solar-assisted endurance are "
          "reported apart. Optional tablet charging and additional use, HF listening among it, reduce endurance, which the "
          "owner accepts (D-28).")
    acc = ("Desk: the modelled endurance under the stated profile, reported at the kit loads (the service continues within "
           "voltage, power and pack limits, and after a permitted pack cutoff the remaining supply carries the loads, "
           "D-26): battery-only in hours from full at +20 C and -10 C, and solar-assisted in hours on the mean day from full "
           "at 06 and 18 UTC, on the power path as drawn and on any corrected path named beside it as hypothetical. The "
           "objective reads met when the solar-assisted run serves the load for 48 hours or more, 72 hours reported beside "
           "it; a shortfall is reported as a design risk with its layer (D-28). Repeated with the loads and the efficiencies "
           "measured at bring-up. Prototype: the kit runs the stated profile from a full store on its solar input, fed by an "
           "array emulator following the reference day's profile, and the hours served are reported.")
    ev = baseline(r7)
    note = ("Restated by %s as the design objective the owner's clarification sets (D-28), replacing the session's SC-21 "
            "(72 hours) and the mandatory reading of D-20 and D-21 the session had taken; its shortfall is design risk DR-01 "
            "(layer 4), no longer the owner's part M-02, which D-28 closes." % stamp)
    for x in (st, acc, ev, note, PROFILE): E.screen(x, "REQ-072")
    raw = C.restate(raw, "REQ-072", stamp, statement=st, acceptance=acc)
    rt_sha = E.sha16(os.path.join(E.TOP, RUNTIME))
    def f72(b):
        b = C.set_line(b, "obligation", "OBJECTIVE", after="kind")
        b = E.set_folded(b, "objective_profile", PROFILE, after="statement")
        b = C.set_line(b, "release_effect", "MUST_JUSTIFY", after="evidence_bound_to")
        b = E.set_flow(b, "choices", [x for x in E.flow_items(b, "choices") if x != "SC-21"])
        b = E.set_flow(b, "waits_on", [x for x in E.flow_items(b, "waits_on") if x != "M-02"])
        b = E.add_list_entry(b, "evidence", ev)
        lines, a_, b_ = E._field_lines(b, "evidence_bound_to")
        b = "\n".join(lines[:b_] + ['      - "%s@%s"' % (RUNTIME, rt_sha)] + lines[b_:])
        for r in ("D-28", r7): b = C.add_ruling_ref(b, r)
        return E.append_folded(b, "notes", note)
    raw = E.replace_entry(raw, "REQ-072", f72, "records")
    # REQ-014: inside the Peli 1450, no external battery
    s14 = " ".join(recs["REQ-014"]["statement"].split())
    raw = C.restate(raw, "REQ-014", stamp, statement=s14 + " The store is inside the Peli 1450 and no external battery is "
                    "part of the kit; battery and solar are both required (D-20, D-21, D-28).")
    raw = E.replace_entry(raw, "REQ-014", lambda b: C.add_ruling_ref(b, "D-28"), "records")
    # REQ-011: the tablet's charging as a capability at the outlet
    raw = C.restate(raw, "REQ-011", stamp, acceptance=(
        "The charging capability is specified at the USB-C outlet, not by a tablet model (D-28): in the functional check a "
        "USB PD sink draws each of REQ-017's contracts within the outlet's protection limits, measured with an inline USB-C "
        "meter, the converter switched by software on its existing enable line; charging is optional and reduces endurance "
        "(REQ-072), and no daily schedule is required. The bracket is drawn and fitted, and the closed lid leaves no mark on "
        "the tablet or its bracket. A tablet model, when one is named (SC-45), is checked against this capability."))
    n11 = ("%s: charging the tablet is an optional capability within the outlet's electrical and protection limits; it "
           "consumes the kit's energy and reduces endurance, which the owner accepts, and neither a daily recharge nor a "
           "schedule is required; stream l3batt's 36 Wh a day (TABLET-BUDGET.md) stays an illustrative calculation. As drawn "
           "the outlet's current-sense shunt R138 puts its trip at 1.92 to 2.26 A, below the 3 A contracts (CHECK-3 of "
           "stream l3batt, minor 1): design risk DR-03, layer 4." % stamp)
    E.screen(n11, "REQ-011")
    raw = E.replace_entry(raw, "REQ-011", lambda b: C.add_ruling_ref(E.append_folded(b, "notes", n11), "D-28"), "records")
    n17 = ("%s: as drawn, board A's outlet shunt R138 is 10 mOhm, twice the maker's recommended 5 mOhm, so the TPS25740A's "
           "trip sits at 1.92 to 2.26 A and the 3.0 A contracts at 5, 9 and 15 V lie above it: this record's 45 W is not "
           "deliverable as drawn (CHECK-3 of stream l3batt, minor 1, a board A finding; the maker's 5 mOhm puts the trip at "
           "3.8 to 4.5 A). Design risk DR-03, layer 4; the requirement is unchanged." % stamp)
    E.screen(n17, "REQ-017")
    raw = E.replace_entry(raw, "REQ-017", lambda b: C.add_ruling_ref(E.append_folded(b, "notes", n17), "D-28"), "records")
    n02 = ("%s: HF is kept; the QMX HF set stays in its lid tray (appendix 32.50 item 16a), and its removal is not reopened "
           "as a solution." % stamp)
    raw = E.replace_entry(raw, "REQ-002", lambda b: C.add_ruling_ref(E.append_folded(b, "notes", n02), "D-28"), "records")
    n16 = ("%s ('Preserve other approved requirements'): the window stands unchanged. With REQ-072 a design objective, its "
           "shortfall under this window is design risk DR-01, not a conflict between mandatory requirements; the 2S2P array "
           "into a 200 W stage is a layer 4 proposal (P-03) that would need the owner's ruling. The interface's obligations "
           "as drawn are design risk DR-04." % stamp)
    raw = E.replace_entry(raw, "REQ-016", lambda b: C.add_ruling_ref(E.append_folded(b, "notes", n16), "D-28"), "records")
    # CFL-017 and FEA-008 (D-29)
    s29 = "D-29 applied by %s (layer 3's closure, %s)" % (r5, DATE)
    n51 = ("%s: CFL-017 closes as a requirements conflict. The margins stand unchanged, neither reduced, read as the kit's "
           "without its cells nor reclassified; with the current cell (the Samsung 35E) and the current thermal design the "
           "kit with its pack fitted does not meet them, which FEA-008 carries to layer 4 mode by mode (LO-01d to LO-01g). "
           "The test deviations measure the rest of the kit and close nothing." % s29)
    raw = E.replace_entry(raw, "REQ-051", lambda b: C.add_ruling_ref(C.add_ruling_ref(E.append_folded(b, "notes", n51), "D-29"), r5), "records")
    fid = E.next_id(E.parse(raw), "FEA", ("records",))
    res = ("%s: judged mode by mode against the project's maker sheets (Samsung INR18650-35E Ver. 1.1 and Version 1.0), "
           "the collisions are between the requirements (D-02, D-02a and TEST-PLAN E5, with the pack fitted) and the current "
           "cell, an engineering selection D-06's pack carries, with the current thermal design; the requirements are "
           "coherent, and %s carries the component-selection and thermal-design obligation to layer 4." % (s29, fid))
    E.screen(res, "CFL-017")
    def f17(b):
        b = C.set_line(b, "status", "CONFLICT_RESOLVED", after="choices")
        b = C.set_line(b, "evidence_result", "NOT_JUDGED", after="status")
        b = C.drop_field(b, "evidence_phase")
        b = E.set_folded(b, "resolved_by", res, after="status")
        for r in ("D-29", r5): b = C.add_ruling_ref(b, r)
        return E.append_folded(b, "notes", "Resolved by %s; it reads NOT_JUDGED: the obligation's reading is %s's." % (s29, fid))
    raw = E.replace_entry(raw, "CFL-017", f17, "records")
    raw = E.insert_after_entry(raw, "FEA-007", fea_entry(fid, r5), "records")
    # M-02 closed by D-28
    d = E.parse(raw)
    it = next(x for x in d["open_items"] if x["id"] == "M-02")
    raw, _ = E.remove_entry(raw, "M-02")
    closed = ("  - id: M-02\n    closed_by: D-28\n    closing_evidence: >-\n%s    title: >-\n%s" % (E.fold(
        "The owner's clarification D-28 answers the owner's part of M1's balance: M1's runtime is a design objective of 48 "
        "to 72 hours under the stated profile (REQ-072, %s), with no external battery and both lid functions kept; the "
        "shortfall is design risk DR-01, assigned to layer 4, and REQ-072 reads FAIL at desk, visible (D-20)." % r7, 6),
        E.fold(it["title"], 6)))
    raw = E.insert_at_section_end(raw, "closed_items", closed)
    exp |= {("records", r, "changed") for r in ("REQ-072", "REQ-014", "REQ-011", "REQ-017", "REQ-002", "REQ-016", "REQ-051",
                                                 "CFL-017")}
    exp |= {("records", fid, "added"), ("open_items", "M-02", "removed"), ("closed_items", "M-02", "added")}
    return raw, exp


def main(argv):
    path = argv[argv.index("--registry") + 1] if "--registry" in argv else E.REGISTRY
    old = open(path, encoding="utf-8").read()
    try:
        new, exp = build(old)
        got = set(E.diff_entries(E.parse(old), E.parse(new)))
        if got != exp: E.refuse("the entries changed are not the declared list: extra %s, missing %s" % (sorted(got - exp), sorted(exp - got)))
        errs, warns = E.validate(new)
        if errs: E.refuse("the result does not validate: %s" % "; ".join(errs[:6]))
    except (E.Refused, RR.RuntimeFormatError) as e:
        print("apply_l3r5_closure: REFUSED: %s" % e)
        return 2
    for s, i, k in sorted(got): print("%-14s %-8s %s" % (s, i, k))
    print("apply_l3r5_closure: %d entries, validator 0 errors, %d warnings%s" % (len(got), len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r5_closure: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
