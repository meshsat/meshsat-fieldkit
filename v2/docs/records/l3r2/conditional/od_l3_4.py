#!/usr/bin/env python3
"""Row L3-OD4 of OWNER-DECISIONS-L3.md: M1's deployment conditions for the lid chosen in row L3-OD2 and the array chosen
in row L3-OD3. PREPARED, NOT APPLIED. Held by the owner's review of 30 September 2026 (D-22) and his addendum (D-24) until
the checked energy basis and the checked power path are filed (both are, since round 3c; a copy is never held).

Row L3-OD7 (M1's runtime) is answered first (D-27, cond.runtime_first): this script refuses while it is unanswered,
and after an answer other than 72-required, because its restatement states M1's 72 hours; it is then restated from
the runtime comparison before it is applied.

D-26 (the owner's reviewer): "A 10 N requirement can be proposed as a chosen design target. Specify application point,
force direction/duration, slope, support surface, lid angle and load configuration. Cite the matching mechanical result
before calling the candidate a modelled PASS." So adopt records the owner's target with its full test conditions, and
feasibility item FI-05 records the studied candidate's status: FAIL where the push is at or above the lid's static tipping
figure on level ground (v2/docs/records/a1mech/README.md section 5), else INCONCLUSIVE (no result is filed for the push on
the slope). A target the candidate does not meet is never refused (D-26).

  --option adopt   requires rows L3-OD1 and L3-OD3 decided and row L3-OD2 decided (it does not apply after a reject).
                   REQ-072 gains a note that no plane band exists (the BAND table), and a new requirement (the next free
                   REQ id, parent NEED-06, prototype 1 core by the ruling) states the open kit's stability: the ground
                   slope toward the hinge (the lid's mechanical figure, or --slope-deg, the owner's, for a lid with no
                   figure), the operator push the owner sets (--push-n), the application point and direction, a static
                   push, a rigid flat surface, the lid at 100 degrees on its stay and the load configuration.
  --option reject  requires rows L3-OD1 and L3-OD3 decided and row L3-OD2 decided or not applicable: no deployment
                   condition; REQ-072 gains a note.
A plane band, were one established, would bind only the array and the weather it was derived for (l3r2.yaml's
contradiction rules); none exists, so no band is written and --band is refused.

THE BAND COMES FROM THE CHECKED ENERGY BASIS (CHECK-1, B2), at the supply range's low end with U3's 6.0 A bracket: the
BAND table below is written from the filed basis (fnd/l3plane cd8720a1, checked by the energy stream's CHECK-5), which gives
no band there for any lid. Every mechanical figure is asserted in v2/docs/records/a1mech/README.md.

Usage: python3 od_l3_4.py --option adopt|reject --words "<the owner's words>" --date YYYY-MM-DD [--check] [--registry PATH]
       [--push-n N] [--slope-deg N]   (adopt)
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cond as C  # noqa: E402

E = C.E
ROW = "L3-OD4"
# The band, written from the checked energy basis at the supply range's low end with U3's 6.0 A bracket (case WE60):
# none exists for any lid on either pass line (ENERGY-BASIS.md section 1, "Band at WE60 (either line)", asserted below;
# energy_basis.out 6). So adopt states the open kit's stability and no plane band, and M1 stays judged on SC-37's
# reference plane. A band text given with --band is refused while the basis gives none.
BASIS = "v2/docs/records/l3plane/ENERGY-BASIS.md"
BAND_ROW = "| Band at WE60 (either line) | none | none | none |"
BAND = {"qmx-out": None, "qmx-outside": None, "tablet-out": None}
MECH = {    # the open kit's tipping on its stay, a1mech README section 5 (static, the lid at 100 degrees, feet-inboard bound,
            # the swept case's lightest base, level ground), interim until T-A1-3 measures the feet
    "qmx-out": {"slope": 1, "mech": "**C on 1.2**", "push": "6.1 N at its far edge", "at": "a press normal to the lid tablet's screen at its far edge", "limit": 6.1},
    "qmx-outside": {"slope": 1, "mech": "**C on 1.2**", "push": "6.1 N at its far edge", "at": "a press normal to the lid tablet's screen at its far edge", "limit": 6.1},
    "tablet-out": {"slope": 3, "mech": "B stands on 3.6 degrees at 100", "push": "above 11.7 N (B)", "at": "a horizontal backward push at the QMX set's controls", "limit": 11.7},
    "both-kept": {"slope": 4, "mech": "A on 4.8", "push": "(13.7 and 10.8 N in A)", "at": "a press normal to the lid tablet's screen at its far edge, the lower of its two figures (10.8 N, against 12.8 N at the QMX set's controls)", "limit": 10.8},
}


def deg(n):
    return "%s degree%s" % (n, "" if str(n) == "1" else "s")


def build(a, raw, d):
    op = a["option"]
    C.runtime_first(d, ROW)
    dec = C.require(d, ROW, ["L3-OD1:approve|reject", "L3-OD3:*"])
    two = dec["L3-OD1"][0] == "approve"
    if two and "L3-OD2" not in dec: E.refuse("%s needs L3-OD2 decided first (it applies with row L3-OD1 approved)" % ROW)
    C.hold(a, ROW)
    lid = dec["L3-OD2"][0] if two else None
    M = MECH.get(lid) if lid else None
    if M: E.assert_in("v2/docs/records/a1mech/README.md", ["a lid stay at 100 degrees", M["mech"], M["push"]])
    arr = {"2s2p": "the 2S2P array", "1s4p": "the 1S4P array", "keep": "the array of REQ-016's kept window"}[dec["L3-OD3"][0]]
    if op == "adopt":
        band = BAND.get(lid)
        push = a["extra"].get("push-n")
        if a["extra"].get("band"):
            E.refuse("the checked basis gives no band at U3's 6.0 A bracket; a band text is not taken from the command line")
        if not push or not push.replace(".", "", 1).isdigit():
            E.refuse("adopt needs --push-n, the operator push the open kit must stand, from the owner's answer (a chosen "
                     "design target, D-26)")
        slope = a["extra"].get("slope-deg")
        if slope is None:
            if not M: E.refuse("adopt needs --slope-deg for this lid: no mechanical figure is filed for %s"
                               % ("the lid without a lid pack (row L3-OD1 rejected)" if not lid else lid))
            slope = M["slope"]
        elif not str(slope).replace(".", "", 1).isdigit(): E.refuse("--slope-deg is not a number of degrees")
        at = M["at"] if M else "a press normal to the lid tablet's screen at its far edge"
        cfg = "the lid pack and lid items fitted" if two else "the lid items fitted"
        if band is None:
            E.assert_in(BASIS, [BAND_ROW])
            where = ("no plane band: none exists at the supply range's low end with U3's 6.0 A bracket (" + BASIS +
                     " section 1, energy_basis.out 6), so M1 stays judged on SC-37's reference plane")
        else:
            where = "the array at %s" % band
        if M:
            cand = (("FAIL: the studied lid tips at %s N on level ground, at or under the target's %s N (%s)" if float(push) >= M["limit"]
                     else "INCONCLUSIVE: the studied lid stands %s N on level ground, above the target's %s N, and no result "
                     "is filed for the push on %s (%s)") % ((M["limit"], push, "v2/docs/records/a1mech/README.md section 5")
                                                           if float(push) >= M["limit"] else
                                                           (M["limit"], push, deg(slope), "v2/docs/records/a1mech/README.md section 5")))
        else:
            cand = ("INCONCLUSIVE: no mechanical result is filed for the lid without a lid pack (row L3-OD1 rejected), on "
                    "level ground or on the slope")
        ruling = ("Row L3-OD4 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: M1's deployment conditions for the "
                  "%s and %s are %s, and the open kit, %s, on ground sloping at most %s toward the hinge and standing a static "
                  "operator push of %s N (%s), a chosen design target and not a standard; a proposed narrower operating "
                  "condition the owner approves here, restated when the case's feet are measured (T-A1-3). Feasibility item "
                  "FI-05 records the studied candidate's status (D-26)."
                  % ("%s lid" % lid if lid else "lid without a lid pack", arr, where, cfg, deg(slope), push, at))
        raw, rid = C.add_ruling(raw, d, ROW, "adopt", "M1's deployment conditions adopted (row L3-OD4)", ruling,
                                a["words"], a["date"])
        if band is None:
            note = "M1's deployment condition (%s, row L3-OD4, %s): %s." % (rid, a["date"], where)
            E.screen(note, "REQ-072's note")
            raw = E.replace_entry(raw, "REQ-072", lambda b: C.add_ruling_ref(E.append_folded(b, "notes", note), rid), "records")
        nid = E.next_id(d, "REQ", ("records",))
        st = ("With the lid open at 100 degrees on its stay and %s, the kit standing on its feet on a rigid flat surface "
              "sloping up to %s toward the hinge side does not tip under a static operator push of up to %s N applied as %s "
              "(a chosen design target, not a standard): the open kit's deployment condition of M1 (%s)."
              % (cfg, deg(slope), push, at, rid))
        acc = ("Desk: the stability calculation of v2/cad/lid_pack_a1.py, with the case's feet as measured by the targeted "
               "check T-A1-3, the lid at 100 degrees, the base contents at the swept case's lightest and the surface at %s "
               "toward the hinge, keeps the open kit's centre of mass inside its support under the %s N static push applied "
               "as %s; the matching mechanical result is cited before any modelled pass (D-26). Prototype: the open kit on a "
               "rigid surface tilted %s toward the hinge, the lid on its stay, does not tip under a %s N static push applied "
               "as %s, held for the time the test plan sets."
               % (deg(slope), push, at, deg(slope), push, at))
        why = ("The owner's ruling %s (row L3-OD4) makes the open kit's stability a condition of mission M1, whose need "
               "NEED-05 is in prototype 1's core." % rid)
        for x in (st, acc, why): E.screen(x, nid)
        entry = ("  - id: %s\n    kind: requirement\n    parent: NEED-06\n    statement: >-\n%s    acceptance: >-\n%s"
                 "    allocated_to: [case, kit, procedure]\n    verification_method: [CALCULATION, PROTOTYPE_MEASUREMENT]\n"
                 "    verification_phase: PLACED_BOARD\n    final_phase: PROTOTYPE\n    prototype_1: core\n"
                 "    prototype_1_basis: NAMED\n    prototype_1_why: >-\n%s    satisfied_by:\n      rules: []\n      decisions: []\n"
                 "    rule_coverage: NONE\n    rulings: [%s]\n    status: DEFINED\n    evidence_result: NOT_JUDGED\n"
                 "    release_effect: BLOCKER\n"
                 "    source: [\"owner ruling %s\", \"v2/docs/records/a1mech/README.md section 5\", \"v2/cad/lid_pack_a1.py\"]\n"
                 "    source_check: VERIFIED\n" % (nid, E.fold(st, 6), E.fold(acc, 6), E.fold(why, 6), rid, rid))
        raw = E.insert_after_entry(raw, "REQ-072", entry, "records")
        raw, fid = C.feasibility_item(raw, "FI-05", [rid, "D-26"], candidate=cand, after=nid, blocks=[nid])
        exp = {("owner_rulings", rid, "added"), ("records", "REQ-072", "changed"), ("records", nid, "added"),
               ("records", fid, "added")}
    else:
        if two and "L3-OD2" not in dec: E.refuse("%s needs L3-OD2 decided first" % ROW)
        ruling = ("Row L3-OD4 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: no deployment condition is stated "
                  "for M1; its claim stays on SC-37's reference plane (40 degrees, facing south).")
        raw, rid = C.add_ruling(raw, d, ROW, "reject", "No M1 deployment condition (row L3-OD4)", ruling, a["words"], a["date"])
        raw = E.replace_entry(raw, "REQ-072", lambda b: C.add_ruling_ref(E.append_folded(b, "notes",
            "No deployment condition is stated (%s, row L3-OD4, %s): the acceptance is judged on SC-37's reference plane "
            "alone." % (rid, a["date"])), rid), "records")
        exp = {("owner_rulings", rid, "added"), ("records", "REQ-072", "changed")}
    raw, _ = C.close_m02_if_done(raw, rid)
    return raw, exp


if __name__ == "__main__":
    sys.exit(C.run("od_l3_4", build, ("adopt", "reject"), sys.argv[1:]))
