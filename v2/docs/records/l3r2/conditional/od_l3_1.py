#!/usr/bin/env python3
"""Row L3-OD1 of OWNER-DECISIONS-L3.md: Option A(i)'s store for mission M1. PREPARED, NOT APPLIED. HELD by the owner's
review of 30 September 2026 (D-22) until the corrected, independently checked energy comparison is filed: the script
refuses to write the tree's registry while l3r2.yaml's `energy_basis` is not filed (a copy is not held).

Row L3-OD7 (M1's runtime) is answered first (D-27, cond.runtime_first): this script refuses while it is unanswered,
and after an answer other than 72-required, because its restatement states M1's 72 hours; it is then restated from
the runtime comparison before it is applied.

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
  --option reject    D-06's one pack stands as the store held; battery and solar stay mandatory and REQ-014, REQ-016 and
                     REQ-072 are unchanged. Rejecting the two-pack candidate leaves an open engineering problem, recorded
                     as feasibility item FI-01 (a feasibility record, a core BLOCKER reading FAIL, D-26); it blocks no
                     other row (row L3-OD2 then does not apply). M-02 gains the owner's answer.
  --pass-line kit-loads|each-pack   (approve; the owner's sub-choice 1b, D-26) REQ-072's pass line at the kit loads:
                     the four conditions of l3r2.yaml's acceptance definition 1b on the exact reference case of stream
                     l3feas (checked by its CHECK-2, l3r2.yaml feasibility_basis); each-pack holds the second condition
                     for each pack alone.

Usage: python3 od_l3_1.py --option approve|reject [--pass-line kit-loads|each-pack] --words "<the owner's words>"
       --date YYYY-MM-DD [--check] [--registry PATH]
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
FEAS = "v2/docs/records/l3feas/L3-FEASIBILITY.md"
FEAS_ASSERT = ["1. **STOP:** every hour of the 72 h serves the load, with each pack drawn only to its own line.",
               "hourly-step sensitivity, 4.2 Wh.", "the lid path under its 8.7 A minimum; the charge currents",
               "within U3's 3.968 A and U3B's 7.936 A and the cells' REQ-075 current.",
               "4. **Voltage:** the node stays at or above every load converter's minimum input with the base at 12.0 V.",
               "the lid pack at 13.23 C and the base pack at +20 C;", "ONE plane: 40 degrees of slope facing south"]
PASS_LINE = {
    "kit-loads": ("(2) the lowest store of the pack or packs still able to carry the kit stays above 4.2 Wh", "kit-loads"),
    "each-pack": ("(2) each pack's own lowest store stays above 4.2 Wh", "each-pack"),
}

ASSERT = {
    "v2/docs/records/energy/ENERGY-RECONCILIATION.md": ["D-06's one 4S3P: 9.1 W, whatever the panel or window",
                                                        "the base pockets' 4S6P", "the 3.00 V line"],
    "v2/docs/records/a1elec/TOPOLOGY.md": ["base 4S6P (both base pockets"],
    "v2/docs/records/a1mech/README.md": ["the west RF entry is re-planned before the west block is taken"],
}


def approve(a, raw, d):
    for rel, n in ASSERT.items(): E.assert_in(rel, n)
    E.assert_in(FEAS, FEAS_ASSERT)
    pl = a["extra"].get("pass-line")
    if pl not in PASS_LINE:
        E.refuse("approve needs --pass-line kit-loads or each-pack: the owner's sub-choice 1b, REQ-072's pass line at the "
                 "kit loads (D-26)")
    rt = C.runtime_first(d, ROW)
    C.require(d, ROW, [])
    C.hold(a, ROW)
    P = C.runtime_phrases(rt["rid"], rt["option"], rt["hf"], rt["external"], rt["tablet"])
    ext = "" if rt["external"] == "no" else " and the external battery arrangement row L3-OD7 authorises"
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
              "M1's pass line is at the kit loads (sub-choice 1b: %s, D-26). It authorises no purchase. It supersedes D-06."
              % ("the four conditions" if pl == "kit-loads" else "the four conditions, the second held by each pack alone"))
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
        statement=("For mission M1 (CONOPS section 3), the kit's two packs (%s)%s plus the solar input keep the kit running "
                   "in PS-IDLE-SPEC%s for %s on the reference day of SC-37, starting from full, aged packs (REQ-014)."
                   % (rid, P["store"], P["load"], P["duration"]) + st6),
        acceptance=("Desk, at the kit loads (the owner's sub-choice 1b, " + PASS_LINE[pl][1] + ", D-26): on the exact "
                    "reference case of " + FEAS + " section 2 (checked by CHECK-2 of stream l3feas): both packs" + ext + " full and "
                    "aged at the start (REQ-014), the base pack at +20 C and the lid pack at the reference day's lowest air, "
                    "13.23 C; the PS-IDLE-SPEC load of POWER-THERMAL.md section 4" + P["load"] + " at the pack terminals with the lid "
                    "path's standby drain, split between the packs by capacity; the energy the input path delivers into "
                    "the kit from " + ARRAY + " on the reference day (4.0 kWh/m2, SC-37) on ONE benchmark plane, 40 "
                    "degrees of slope facing south, the single exact orientation while no deployment band is established, "
                    "in the installation row L3-OD6 names; each pack's cutoff its graceful line (5 percent relative state "
                    "of charge, or its lowest cell at a cell voltage of 3.00 V or more under load), the kit's shutdown the "
                    "base pack at its line; the charge bus anywhere in its steady-state supply range as the energy basis "
                    "gives it (" + BASIS + " section 2) and every limit that must hold a load at its minimum (D-22), the "
                    "basis's brackets below that range stated beside the result; the power-path case named beside the "
                    "result. It passes only when all four hold: (1) every hour of the " + P["hours"] + " serves the load, each pack drawn "
                    "only to its own line; " + PASS_LINE[pl][0] + "; (3) every path stays within its limits every hour "
                    "(the lid path under its 8.7 A minimum; the charge currents within U3's 3.968 A, U3B's 7.936 A and the "
                    "cells' REQ-075 current); (4) the node stays at or above every load converter's minimum input with the "
                    "base pack at 12.0 V. After a permitted pack cutoff the remaining supply carries the loads; combined "
                    "stored energy alone is not the line. Repeated with the loads and the stages' efficiencies measured at "
                    "bring-up. Prototype: the kit runs PS-IDLE-SPEC" + P["load"] + " for " + P["hours"] + " hours from full packs on its solar input, fed "
                    "by an array emulator following the reference day's profile, with the four conditions read at the "
                    "kit loads." + acc6))
    raw = E.replace_entry(raw, "REQ-072", lambda b: E.append_folded(C.add_ruling_ref(C.add_ruling_ref(b, "D-21"), "D-22"),
        "notes", ("Restated by %s: the single pack's pass line 'ends the " + P["hours"] + " hours above the graceful shutdown "
        "threshold' becomes 'serves the load at every hour of the " + P["hours"] + " without the kit reaching its graceful "
        "shutdown' for two packs, "
        "with a floor of 3.00 V a cell under the graceful shutdown (the line of v2/docs/records/energy/"
        "ENERGY-RECONCILIATION.md), so that a lower line cannot ease the requirement.") % stamp), "records")
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
    C.runtime_first(d, ROW)
    C.require(d, ROW, [])
    C.hold(a, ROW)
    E.assert_in("v2/docs/records/energy/ENERGY-RECONCILIATION.md", ["D-06's one 4S3P: 9.1 W, whatever the panel or window"])
    ruling = ("Row L3-OD1 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md not approved: D-06's one 4S3P pack stands as the "
              "store held, and Option A(i)'s store is not adopted. Battery and solar stay mandatory for M1 (D-20); REQ-014, "
              "REQ-016 and REQ-072 are unchanged and REQ-072 keeps reading FAIL. Rejecting the two-pack candidate leaves "
              "the store that meets M1 an open engineering problem, recorded as feasibility item FI-01 (D-26); it blocks no "
              "other row, and row L3-OD2 does not apply.")
    raw, rid = C.add_ruling(raw, d, ROW, "reject", "Option A(i) not adopted; D-06 stands, the store an open problem (row L3-OD1)",
                            ruling, a["words"], a["date"])
    raw, fid = C.feasibility_item(raw, "FI-01", [rid, "D-06", "D-20", "D-26"])
    raw = E.replace_entry(raw, "M-02", lambda b: E.append_folded(b, "title",
        "The owner answered row L3-OD1 on %s (%s): D-06's one pack stands; %s records the open store problem (FI-01)."
        % (a["date"], rid, fid)), "open_items")
    exp = {("owner_rulings", rid, "added"), ("records", fid, "added"), ("open_items", "M-02", "changed")}
    raw, _ = C.close_m02_if_done(raw, rid)
    return raw, exp


def build(a, raw, d):
    return (approve if a["option"] == "approve" else reject)(a, raw, d)


if __name__ == "__main__":
    sys.exit(C.run("od_l3_1", build, ("approve", "reject"), sys.argv[1:]))
