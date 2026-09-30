#!/usr/bin/env python3
"""Row L3-OD1 of OWNER-DECISIONS-L3.md: Option A(i)'s store for mission M1. PREPARED, NOT APPLIED. HELD by the owner's
review of 30 September 2026 (D-22) until the corrected, independently checked energy comparison is filed: the script
refuses to write the tree's registry while l3r2.yaml's `energy_basis` is not filed (a copy is not held).

This row fixes the STORE only. The solar input (its stage, its array, REQ-016's window and the array REQ-072 names) is row
L3-OD3's alone, so the two rows can never leave two rulings on the array standing (CHECK-1, B1).

  --option approve   D-06 is superseded (reversed_by the new ruling, which keeps D-06's runtime statement per pack) and
                     every record citing D-06 cites the new ruling; REQ-014 and REQ-075 are restated per pack, the lid's
                     parallel count left to row L3-OD2 by a marked phrase od_l3_2.py replaces; REQ-072 is restated to two
                     packs, its array left to row L3-OD3 by a marked phrase od_l3_3.py replaces, its claim held across
                     the charge bus's supply range and every load-holding limit at its minimum (the energy basis), and
                     its graceful shutdown given a floor of 3.00 V a cell; CFL-006's acceptance and resolution become
                     per pack. If row L3-OD6 was answered `coverage` first, its marked sentence in REQ-072's statement
                     and acceptance is carried over into the restated texts (cond.od6_tail).
  --option reject    D-06's one pack stands; an open conflict (the next free CFL id) records REQ-072 against it, a core
                     BLOCKER reading FAIL on its own sources; M-02 gains the owner's answer.

Usage: python3 od_l3_1.py --option approve|reject --words "<the owner's words>" --date YYYY-MM-DD [--check] [--registry PATH]
The figures the new texts quote are asserted in the records they come from before anything is written (cond.py).
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cond as C  # noqa: E402

E = C.E
ROW = "L3-OD1"
LID_AH = "2.68 Ah times the lid pack's parallel count (row L3-OD2)"
LID_A = "1.02 A times the lid pack's parallel count (row L3-OD2)"
LID_BLOCK = "a lid block whose parallel count row L3-OD2 sets"
ARRAY = "the kit's array (row L3-OD3)"
BASIS = "v2/docs/records/l3plane/ENERGY-BASIS.md"

ASSERT = {
    "v2/docs/records/energy/ENERGY-RECONCILIATION.md": ["D-06's one 4S3P: 9.1 W, whatever the panel or window",
                                                        "the base pockets' 4S6P", "the 3.00 V line"],
    "v2/docs/records/a1elec/TOPOLOGY.md": ["base 4S6P (both base pockets"],
    "v2/docs/records/a1mech/README.md": ["the west RF entry is re-planned before the west block is taken"],
}


def approve(a, raw, d):
    for rel, n in ASSERT.items(): E.assert_in(rel, n)
    C.require(d, ROW, [])
    C.hold(a, ROW)
    r072 = next(r for r in d["records"] if r["id"] == "REQ-072")
    st6, acc6 = C.od6_tail(r072["statement"]), C.od6_tail(r072["acceptance"])   # row L3-OD6 coverage, if applied
    ruling = ("Row L3-OD1 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md approved: the kit's energy store for mission M1 is "
              "two separately protected packs of the Samsung INR18650-35E, a base pack of 4S6P across the two base pockets "
              "under board P (the west RF entry re-planned before the west block is taken) and a lid pack under its own "
              "protection board whose parallel count row L3-OD2 sets, each with its own charger path and gauge. The second "
              "pack leaves D-01's deferred list and joins prototype 1's core, and approving it takes one approved lid "
              "function out of the lid, which row L3-OD2 decides with the place its function takes. Where a requirement "
              "says 'the pack', it applies to each pack unless it names one. D-06's runtime statement is kept for both "
              "packs together and for each pack alone: battery-only hours in an idle and a typical mode at +20 C for aged "
              "packs, missions longer than the packs relying on vehicle or solar input. The solar input is row L3-OD3's. "
              "It authorises no purchase. It supersedes D-06.")
    raw, rid = C.add_ruling(raw, d, ROW, "approve", "Option A(i)'s store adopted for M1 (row L3-OD1)", ruling,
                            a["words"], a["date"])
    stamp = "%s (row L3-OD1, %s)" % (rid, a["date"])
    raw = E.replace_entry(raw, "D-06", lambda b: C.set_line(b, "reversed_by", rid, after="title"), "owner_rulings")
    raw, touched = C.swap_ruling(raw, d, "D-06", rid)

    raw = C.restate(raw, "REQ-014", stamp,
        statement=("The kit runs from its internal packs, the base pack and the lid pack (%s), and its battery-only "
                   "runtime is stated in hours in an idle and a typical mode (PS-IDLE-SPEC and PS-TYP) at +20 C for aged "
                   "packs, for both packs together and for each pack alone; missions longer than the packs rely on "
                   "vehicle or solar input." % rid),
        acceptance=("The stated hours for PS-IDLE-SPEC and PS-TYP at +20 C are computed for aged packs, each at 80 percent "
                    "of the cells' specification minimum capacity, 2.68 Ah a cell (SC-23): 16.08 Ah for the base pack's 6P "
                    "block and " + LID_AH + " for the lid pack; then measured on the prototype and scaled to that "
                    "capacity; no published runtime exceeds the scaled measurement, and a pack is replaced once its "
                    "gauge's learned full-charge capacity falls below its capacity so stated."))
    raw = E.replace_entry(raw, "REQ-014", lambda b: E.append_folded(b, "provisional",
        "These are the one 4S3P pack's figures of D-06, which %s supersedes; the two packs' figures are computed again at "
        "layer 4." % rid), "records")
    raw = C.restate(raw, "REQ-075", stamp,
        statement=("Each pack is charged at no more than 1,020 mA per cell of its parallel block, the cell maker's charge "
                   "current for cycle life: 6.12 A for the base pack's 6P block and " + LID_A + " for the lid pack (%s)." % rid),
        acceptance=("Desk: each charger's ChargeCurrent setting and each pack gauge's charging current in its golden "
                    "image are at most that pack's limit (Samsung INR18650-35E Ver. 1.1, clause 3.5; SC-40); prototype: "
                    "the charge current measured at each pack in constant-current charge is at most its limit."))
    raw = C.restate(raw, "REQ-072", stamp,
        statement=("For mission M1 (CONOPS section 3), the kit's two packs (%s) plus the solar input keep the kit running "
                   "in PS-IDLE-SPEC for M1's 72 hours (SC-21, preserved by D-20 and approved by D-21) on the reference day "
                   "of SC-37, starting from full, aged packs (REQ-014)." % rid + st6),
        acceptance=("Desk: a calculation from the PS-IDLE-SPEC load of POWER-THERMAL.md section 4, the aged packs of "
                    "REQ-014, each at its own cell temperature, and the energy the input path delivers into the kit from "
                    + ARRAY + " on the reference day (4.0 kWh/m2 on the optimally inclined plane, SC-37), with the charge "
                    "bus anywhere in its supply range and every limit that must hold a load at its minimum (" + BASIS +
                    ", D-22), serves the load at every hour of the 72 without the kit reaching its graceful shutdown, the "
                    "graceful shutdown set at a cell voltage of 3.00 V or more; repeated with the loads and the stages' "
                    "efficiencies measured at bring-up. Prototype: the kit runs PS-IDLE-SPEC for 72 hours from full packs "
                    "on its solar input, fed by an array emulator following the reference day's profile, without "
                    "reaching its graceful shutdown." + acc6))
    raw = E.replace_entry(raw, "REQ-072", lambda b: E.append_folded(C.add_ruling_ref(C.add_ruling_ref(b, "D-21"), "D-22"),
        "notes", "Restated by %s: the single pack's pass line 'ends the 72 hours above the graceful shutdown threshold' "
        "becomes 'serves the load at every hour of the 72 without the kit reaching its graceful shutdown' for two packs, "
        "with a floor of 3.00 V a cell under the graceful shutdown (the line of v2/docs/records/energy/"
        "ENERGY-RECONCILIATION.md), so that a lower line cannot ease the requirement." % stamp), "records")
    raw = E.replace_entry(raw, "CFL-006", lambda b: E.set_folded(E.set_folded(b, "acceptance",
        "For each pack of %s: one named cell and one parallel count, with the cell's own sheet in v2/vendor/battery/, used "
        "by the energy chain, the protection table, the runtime and the enclosure." % rid), "resolved_by",
        "%s, superseding D-06: two packs of the Samsung INR18650-35E, a base 4S6P block and %s; the cell's sheet is held in "
        "v2/vendor/battery/." % (rid, LID_BLOCK)), "records")
    raw = E.replace_entry(raw, "CFL-006", lambda b: E.append_folded(b, "history",
        "Acceptance and resolution restated per pack by %s; they read 'One named cell and one parallel count ...' and "
        "'D-06: one 4S3P block ...'." % stamp, after="source_check"), "records")
    exp = {("owner_rulings", rid, "added"), ("owner_rulings", "D-06", "changed")} | \
          {("records", r, "changed") for r in set(touched) | {"REQ-014", "REQ-075", "REQ-072", "CFL-006"}}
    raw, _ = C.close_m02_if_done(raw, rid)
    return raw, exp


def reject(a, raw, d):
    C.require(d, ROW, [])
    C.hold(a, ROW)
    E.assert_in("v2/docs/records/energy/ENERGY-RECONCILIATION.md", ["D-06's one 4S3P: 9.1 W, whatever the panel or window"])
    ruling = ("Row L3-OD1 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md not approved: D-06's one 4S3P pack stands, and "
              "Option A(i)'s store is not adopted. REQ-072 keeps reading FAIL; the conflict with D-06 is recorded as an "
              "open conflict and layer 3 stays open until the owner authorises a change to M1, to the approved functions "
              "or to the store.")
    raw, rid = C.add_ruling(raw, d, ROW, "reject", "Option A(i) not adopted; D-06 stands (row L3-OD1)", ruling,
                            a["words"], a["date"])
    cid = E.next_id(d, "CFL", ("records",))
    st = ("REQ-072 (M1: 72 hours in PS-IDLE-SPEC on pack and solar, preserved by D-20 and approved by D-21) cannot be met "
          "on D-06's one 4S3P pack, which the owner kept on %s (%s): the pack allows at most 9.1 W for M1 against "
          "PS-IDLE-SPEC's 42.8 W (v2/docs/records/energy/ENERGY-RECONCILIATION.md section 9d)." % (a["date"], rid))
    acc = ("One of: an owner ruling that changes the store, M1's duration or operating state, or the functions the kit "
           "carries, after which REQ-072 is judged again; until then REQ-072 reads FAIL and layer 3 is not complete.")
    for t in (st, acc): E.screen(t, cid)
    entry = ("  - id: %s\n    kind: conflict\n    parent: NEED-05\n    statement: >-\n%s    acceptance: >-\n%s"
             "    allocated_to: [kit, p, procedure]\n    verification_method: [MANUAL_REVIEW]\n    verification_phase: SCHEMATIC\n"
             "    prototype_1: core\n    prototype_1_basis: NEED_DEFAULT\n    satisfied_by:\n      rules: []\n      decisions: []\n"
             "    rule_coverage: NONE\n    rulings: [D-06, %s, D-20, D-21]\n    status: CONFLICT_OPEN\n    evidence_result: FAIL\n"
             "    evidence_phase: SCHEMATIC\n    release_effect: BLOCKER\n"
             "    source: [\"owner ruling %s\", \"owner ruling D-20\", \"v2/docs/records/energy/ENERGY-RECONCILIATION.md section 9\"]\n"
             "    source_check: VERIFIED\n" % (cid, E.fold(st, 6), E.fold(acc, 6), rid, rid))
    raw = E.insert_after_entry(raw, "REQ-072", entry, "records")
    raw = E.replace_entry(raw, "M-02", lambda b: E.append_folded(b, "title",
        "The owner answered row L3-OD1 on %s (%s): D-06's one pack stands; %s records the conflict." % (a["date"], rid, cid)),
        "open_items")
    return raw, {("owner_rulings", rid, "added"), ("records", cid, "added"), ("open_items", "M-02", "changed")}


def build(a, raw, d):
    return (approve if a["option"] == "approve" else reject)(a, raw, d)


if __name__ == "__main__":
    sys.exit(C.run("od_l3_1", build, ("approve", "reject"), sys.argv[1:]))
