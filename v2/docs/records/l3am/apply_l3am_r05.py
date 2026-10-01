#!/usr/bin/env python3
"""L3-R05 of the independent review the owner relayed on 1 October 2026 (MESHSAT-1357; v2/docs/records/l3am/): REQ-016's
protection wording.

The protection sentence sits in REQ-016's ACCEPTANCE, not its statement: "the panel input's clamp D4 is an SMCJ28A (28 V
standoff, above the window, conducting from 31.1 V, under the 35 V bulk capacitors)". It implied that a breakdown onset
below the capacitors' rating establishes protection. The maker's sheet held in this tree
(v2/vendor/power/littelfuse-smcj-series-tvs.pdf, Littelfuse SMCJ series, revised 11/20/15, p.2, the SMCJ28A row) gives
28.0 V standoff with at most 1 uA leakage there, 31.10 to 34.40 V breakdown at 1 mA and 45.4 V maximum clamping at 33.1 A
(its 10/1000 us peak pulse rating, p.1): breakdown onset is not the protected node's maximum. The sentence stays in the
acceptance, where the pass line belongs, and is rewritten to keep three things apart: the verified normal operating
envelope (the window's pass lines, unchanged), the bounded ESD result (DECISION-31-PROTECTION-TOPOLOGY.md, the PV_IN
paragraph of section 6.3, under the session's decision 34 level of section 3), and the surge and over-voltage obligations,
unresolved: no surge level is ruled, so the disturbance, its source impedance or current, its duration and the limit are
derived at layer 4 and judged at layer 8 under rule TRN-001 (its port table), and no protection is claimed until then. A
part number closes none of them.

The statement, the window D-34 retained (at most 25 V open circuit at the panel's coldest operating temperature, 17.6 V
by the stage's input regulation, at most 100 W into the stage), is asserted byte-identical; so are the window's pass lines
(the declared 25 V, the ratings above it, R8 and R9 at 17.6 V, F2 and J_SOLAR at 10 A, the prototype's bench supply),
D4's clause restated as its standoff and its leakage there.
gen_sch_e.py is not edited (a board generator; its comment at lines 440 to 448 and D4's value text repeat the implication,
a follow-up named in DISPOSITIONS.md).

It writes, and asserts nothing else changes: REQ-016's `acceptance`, `history` (one sentence closing it), `source` (the
maker's sheet and DECISION-31 added) and `satisfied_by` (TRN-001 added beside PWR-001); in l3r2.yaml REQ-016's `impacts`
entry, whose why keeps D-34 and adds the correction, and whose layers name what the correction moves (the record now reads
changed since H3, so section 7 prints them as applied). A second run is refused. No dash character is written.

Usage: python3 v2/docs/records/l3am/apply_l3am_r05.py [--check]"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3amlib as L  # noqa: E402

STATEMENT = ("The solar input charges the pack through board E's LT8705A stage from a panel inside its declared window: an "
             "open-circuit voltage of at most 25 V at the panel's coldest operating temperature, the panel held at 17.6 V by "
             "the stage's input regulation, and at most 100 W into the stage.")
OLD_CLAUSE = ("the panel input's clamp D4 is an SMCJ28A (28 V standoff, above the window, conducting from 31.1 V, under the "
              "35 V bulk capacitors);")
NEW_CLAUSE = ("the panel input's clamp D4, an SMCJ28A, stands off 28 V (at most 1 uA there, the maker's SMCJ28A row), above "
              "the window;")
PROTECTION = (
    " Protection is judged apart from the window, under rule TRN-001 (its port table), and never by a part number or a "
    "breakdown figure: the SMCJ28A breaks down between 31.1 and 34.4 V at 1 mA and clamps at up to 45.4 V at its 33.1 A "
    "pulse (Littelfuse SMCJ series sheet, p.2), so its breakdown onset below the 35 V bulk capacitors C11 and C12 does not "
    "show that PV_P stays under 35 V in a disturbance. It passes for a disturbance only when D4's clamping voltage at that "
    "disturbance's current (from its source impedance, waveform and duration, with the part's tolerance) is at or below "
    "the lowest limit on PV_P, the capacitors' 35 V. Electrostatic discharge (IEC 61000-4-2 level 4, 8 kV contact and 15 kV "
    "air, the session's decision 34, a design level): bounded by DECISION-31-PROTECTION-TOPOLOGY.md section 6.3, the "
    "network's whole charge moving the 225 uF on PV_P by 0.005 and 0.010 V, protected with a constraint. Surge and "
    "sustained over-voltage on the panel lead: no level is ruled (DECISION-31 section 3; D-16 for the vehicle entry), so "
    "the disturbance, its source impedance or current, its duration and the limit are derived at layer 4 and judged at "
    "layer 8 under TRN-001, and this record claims no surge or over-voltage protection on PV_P until then; a reversed panel "
    "conducts through D4 (DECISION-31, note E-N1).")
HISTORY_ADD = (
    "Corrected on 1 October 2026 under the owner's relayed instruction on the independent review's finding L3-R05 "
    "(v2/docs/records/l3am/REVIEW-AS-RECEIVED.md, v2/docs/records/l3am/apply_l3am_r05.py): the acceptance read D4's "
    "breakdown onset, 31.1 V, under the 35 V bulk capacitors as protection; the maker gives 31.1 to 34.4 V at 1 mA and up "
    "to 45.4 V at 33.1 A, and breakdown onset is not the protected node's maximum. The protection sentence stays in the "
    "acceptance, rewritten to trace protection to TRN-001 and to keep the operating window, the bounded ESD result and "
    "the unresolved surge and over-voltage obligations apart. The statement, the window D-34 retained, is unchanged, and "
    "so are the window's own pass lines but D4's, which now states its standoff.")
SOURCES_ADD = ['"v2/vendor/power/littelfuse-smcj-series-tvs.pdf (p.2, the SMCJ28A row; p.1, the 10/1000 us rating)"',
               '"v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md sections 3 and 6.3 (PV_IN)"']
IMPACT_OLD_START = "  REQ-016: {rows: [L3-OD3], why: \"row L3-OD3 answered unchanged (D-34): "
IMPACT_NEW = (
    "  REQ-016: {rows: [L3-OD3], why: \"row L3-OD3 answered unchanged (D-34): REQ-016's approved window stays (25 V, 17.6 "
    "V, 100 W), its statement as H3 has it; the prepared restatement (a 200 W stage in 2S2P or 1S4P, or the window kept "
    "with the basis's array) was not taken, and the 2S2P array goes with P-01 to layer 4 as P-03; its acceptance's "
    "protection clause corrected on 1 October 2026 (the independent review's L3-R05): D4's breakdown onset no longer read "
    "as protection, protection judged apart from the window under TRN-001, the ESD result bounded and the surge and "
    "over-voltage obligations unresolved\", layers: {4: \"the panel lead's surge and over-voltage disturbance derived (its "
    "level, source impedance or current and duration), or recorded as not claimed\", 8: \"board E's D4 judged under TRN-001 "
    "against the 35 V on PV_P at that disturbance; gen_sch_e.py's comment and D4's value text brought in line\", 9: "
    "\"TEST-PLAN M7's discharge on the panel entry; a surge test only once a level is ruled\"}}")


def build():
    reg_old = open(L.REGISTRY, encoding="utf-8").read()
    data_old = open(L.DATA, encoding="utf-8").read()
    req = L.E.parse(reg_old)
    r16 = next(r for r in req["records"] if r["id"] == "REQ-016")
    if "L3-R05" in str(r16.get("history")): L.refuse("REQ-016's history names L3-R05: this script has run")
    if " ".join(str(r16["statement"]).split()) != STATEMENT: L.refuse("REQ-016's statement is not the window D-34 retained")
    acc = " ".join(str(r16["acceptance"]).split())
    new_acc = L.once(acc, OLD_CLAUSE, NEW_CLAUSE, "REQ-016's acceptance") + PROTECTION
    for t, w in ((new_acc, "REQ-016's acceptance"), (HISTORY_ADD, "REQ-016's history"), (IMPACT_NEW, "REQ-016's impacts")):
        L.screen(t, w)

    def f(block):
        b = L.E.set_folded(block, "acceptance", new_acc)
        b = L.E.append_folded(b, "history", HISTORY_ADD)
        lines, a, e = L.E._field_lines(b, "source")
        if a is None or lines[a].strip() != "source:": L.refuse("REQ-016's source is not a block list")
        b = "\n".join(lines[:e] + ["      - %s" % s for s in SOURCES_ADD] + lines[e:])
        old_sb = "      rules: [PWR-001]\n      decisions: []"
        if b.count(old_sb) != 1: L.refuse("REQ-016's satisfied_by is not PWR-001 alone")
        return b.replace(old_sb, "      rules: [PWR-001, TRN-001]\n      decisions: []")
    reg_new = L.E.replace_entry(reg_old, "REQ-016", f, "records")
    a, b = L.only_fields_changed(reg_old, reg_new, {("records", "REQ-016"): ["acceptance", "history", "satisfied_by", "source"]})
    b16 = next(r for r in b["records"] if r["id"] == "REQ-016")
    if b16["statement"] != r16["statement"]: L.refuse("REQ-016's statement moved")
    keep = acc.split(OLD_CLAUSE)
    nb = " ".join(str(b16["acceptance"]).split())
    if not (nb.startswith(keep[0]) and keep[1] in nb): L.refuse("the window's pass lines moved")
    lines = data_old.split("\n")
    k = [i for i, l in enumerate(lines) if l.startswith(IMPACT_OLD_START)]
    if len(k) != 1: L.refuse("l3r2.yaml's impacts entry for REQ-016 is not found once")
    data_new = "\n".join(lines[:k[0]] + [IMPACT_NEW] + lines[k[0] + 1:])
    x, y = L.only_keys_changed(data_old, data_new, {"impacts": "changed"})
    if [r for r in set(x["impacts"]) | set(y["impacts"]) if x["impacts"].get(r) != y["impacts"].get(r)] != ["REQ-016"]:
        L.refuse("impacts changed beyond REQ-016's entry")
    return (reg_old, reg_new), (data_old, data_new)


def main(argv):
    try:
        r, d = build()
        L.validate_registry(r[1])
    except L.Refused as e:
        print("apply_l3am_r05: REFUSED: %s" % e); return 2
    print("apply_l3am_r05: REQ-016's acceptance (the protection clause), history, source and satisfied_by; its impacts "
          "entry%s" % (" (check only, nothing written)" if "--check" in argv else ""))
    if "--check" in argv: return 0
    L.write(L.REGISTRY, *r)
    L.write(L.DATA, *d)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
