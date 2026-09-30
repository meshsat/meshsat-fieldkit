#!/usr/bin/env python3
"""Row L3-OD4 of OWNER-DECISIONS-L3.md: M1's deployment conditions for the lid chosen in row L3-OD2 and the array chosen
in row L3-OD3. PREPARED, NOT APPLIED. Held by the owner's review of 30 September 2026 (D-22) and his addendum (D-24) until
the checked energy basis and the checked power path are filed (both are, since round 3c; a copy is never held).

  --option adopt   requires row L3-OD6 answered mean-day first (the band is a mean-day grid's, so it follows the owner's
                   weather answer and never precedes it, D-23), row L3-OD1 approved, row L3-OD2 decided and row L3-OD3
                   answered 2s2p: the only array a plane
                   grid has been run for (v2/docs/records/l3plane/plane_grid.out ran 400 Wp in 2S2P into 200 W; a band for
                   1S4P or for REQ-016 kept needs its own grid, so the script refuses those answers). It is refused while
                   row L3-OD6 stands answered coverage: the grid runs SC-37's mean day on each plane, and no band
                   exists for a coverage target. REQ-072 gains a note that no plane band exists (the BAND table),
                   and a new requirement (the next free REQ id, parent NEED-06, prototype 1
                   core by the ruling) states the open kit's stability: the ground slope toward the hinge a1mech gives for
                   the chosen lid, and the operator push the owner sets.
  --option reject  requires rows L3-OD1 to L3-OD3 decided: no deployment condition; REQ-072 gains a note.
Row L3-OD2 answered both-kept (a 4S9P lid, M1 not met): adopt is refused, reject stands.

THE BAND COMES FROM THE CHECKED ENERGY BASIS (CHECK-1, B2), at the supply range's low end with U3's 6.0 A bracket: the
BAND table below is written from the filed basis (fnd/l3plane cd8720a1, checked by the energy stream's CHECK-5), which gives
no band there for any lid, so adopt states the open kit's stability with no plane band; --band is refused. The operator
push is the owner's: --push-n N, from his answer. Every other figure is asserted in v2/docs/records/a1mech/README.md.

Usage: python3 od_l3_4.py --option adopt|reject --words "<the owner's words>" --date YYYY-MM-DD [--check] [--registry PATH]
       [--push-n N]   (adopt)
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
MECH = {    # the open kit's tipping on its stay, a1mech README section 5 (interim, until T-A1-3 measures the feet)
    "qmx-out": {"slope": 1, "mech": "**C on 1.2**", "push": "6.1 N at its far edge", "at": "a press normal to the lid tablet's screen at its far edge"},
    "qmx-outside": {"slope": 1, "mech": "**C on 1.2**", "push": "6.1 N at its far edge", "at": "a press normal to the lid tablet's screen at its far edge"},
    "tablet-out": {"slope": 3, "mech": "B stands on 3.6 degrees at 100", "push": "above 11.7 N (B)", "at": "a backward push at the QMX set's controls"},
}


def deg(n):
    return "%d degree%s" % (n, "" if n == 1 else "s")


def build(a, raw, d):
    op = a["option"]
    if op == "adopt":
        # the band is a mean-day grid's, so it follows the owner's weather answer and never precedes it: an undecided
        # row L3-OD6 refuses adopt (CHECK-2 of L3-R2, B1; D-23)
        dec = C.require(d, ROW, ["L3-OD1:approve", "L3-OD2:*", "L3-OD3:2s2p", "L3-OD6:mean-day"])
    else:
        dec = C.require(d, ROW, ["L3-OD1:approve", "L3-OD2:*", "L3-OD3:*"])
    C.hold(a, ROW)
    lid = dec["L3-OD2"][0]
    if lid == "both-kept" and op == "adopt":
        E.refuse("row L3-OD2 is answered both-kept: M1 is not met with a 4S9P lid, so no deployment band is adopted for it")
    M = MECH.get(lid)
    if M: E.assert_in("v2/docs/records/a1mech/README.md", ["a lid stay at 100 degrees", M["mech"], M["push"]])
    if op == "adopt":
        band = BAND.get(lid)
        push = a["extra"].get("push-n")
        if a["extra"].get("band"):
            E.refuse("the checked basis gives no band at U3's 6.0 A bracket; a band text is not taken from the command line")
        if not push or not push.replace(".", "", 1).isdigit():
            E.refuse("adopt needs --push-n, the operator push the open kit must stand, from the owner's answer")
        if band is None:
            E.assert_in(BASIS, [BAND_ROW])
            where = ("no plane band: none exists at the supply range's low end with U3's 6.0 A bracket (" + BASIS +
                     " section 1, energy_basis.out 6), so M1 stays judged on SC-37's reference plane")
        else:
            where = "the array at %s" % band
        ruling = ("Row L3-OD4 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: M1's deployment conditions for the "
                  "%s lid and the 2S2P array are %s, and the open kit, its lid pack and lid items fitted, on ground sloping "
                  "at most %s toward the hinge and standing an operator push of %s N; a proposed narrower operating "
                  "condition the owner approves here, restated when the case's feet are measured (T-A1-3)."
                  % (lid, where, deg(M["slope"]), push))
        raw, rid = C.add_ruling(raw, d, ROW, "adopt", "M1's deployment conditions adopted (row L3-OD4)", ruling,
                                a["words"], a["date"])
        if band is None:
            note = "M1's deployment condition (%s, row L3-OD4, %s): %s." % (rid, a["date"], where)
            E.screen(note, "REQ-072's note")
            raw = E.replace_entry(raw, "REQ-072", lambda b: C.add_ruling_ref(E.append_folded(b, "notes", note), rid), "records")
        else:
            add = ("M1's deployment condition (%s): the array faces %s. The desk calculation above holds on every grid plane "
                   "of that band, each on its own reference-day profile (v2/docs/records/l3plane/plane_grid.py), and the "
                   "prototype run is repeated with the array emulator following the band's least-energy grid plane." % (rid, band))
            E.screen(add, "REQ-072's added acceptance")
            raw = E.replace_entry(raw, "REQ-072", lambda b: C.add_ruling_ref(E.append_folded(b, "acceptance", add), rid), "records")
            raw = E.replace_entry(raw, "REQ-072", lambda b: E.append_folded(b, "history",
                "The deployment condition added to the acceptance by %s (row L3-OD4, %s)." % (rid, a["date"]), after="source_check"),
                "records")
        nid = E.next_id(d, "REQ", ("records",))
        st = ("With the lid open as the kit is deployed and the lid pack and lid items fitted, the kit stands without "
              "tipping on ground sloping up to %s toward the hinge side, and under an operator push of up to %s N at any "
              "lid item an operator works (%s among them): the open kit's deployment condition of M1 (%s)."
              % (deg(M["slope"]), push, M["at"], rid))
        acc = ("Desk: the stability calculation of v2/cad/lid_pack_a1.py, with the case's feet as measured by the targeted "
               "check T-A1-3, keeps the open kit's centre of mass inside its support at %s toward the hinge at every lid "
               "opening the deployment allows, with the %s N push applied at each lid item. Prototype: the open kit on a "
               "surface tilted %s toward the hinge does not tip under a %s N push at each lid item."
               % (deg(M["slope"]), push, deg(M["slope"]), push))
        why = ("The owner's ruling %s (row L3-OD4) makes the open kit's stability a condition of mission M1, whose need "
               "NEED-05 is in prototype 1's core, and the lid pack it carries joins the core under row L3-OD1." % rid)
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
        exp = {("owner_rulings", rid, "added"), ("records", "REQ-072", "changed"), ("records", nid, "added")}
    else:
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
