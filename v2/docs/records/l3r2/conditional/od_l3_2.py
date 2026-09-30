#!/usr/bin/env python3
"""Row L3-OD2 of OWNER-DECISIONS-L3.md: which approved lid item leaves the lid for the lid pack, where it goes, and whether
its function stays in the kit. PREPARED, NOT APPLIED. Requires row L3-OD1 approved. HELD by the owner's review of 30
September 2026 (D-22) until the checked energy comparison is filed; the option that carries the QMX outside the case also
waits on the relocation facts. A held answer is never written into the tree's registry (a copy is not held).

Row L3-OD7 (M1's runtime) is answered first (D-27, cond.runtime_first): this script refuses while it is unanswered,
and after an answer other than 72-required, because its restatement states M1's 72 hours; it is then restated from
the runtime comparison before it is applied.

The owner's words of D-22: "moving equipment out of the lid must not silently remove its function from the kit". Each
option says where the displaced item goes and what happens to its function, in its ruling and in the records it restates.

  --option qmx-out      the QMX HF set leaves the kit and HF leaves with it, the owner's explicit decision to remove an
                        approved function: REQ-002 and REQ-067 are restated with no HF in the kit (their old statements
                        kept as SPD records), REQ-068 loses its QMX clause, CON-007 gains a note; the lid keeps an 8 inch
                        tablet bracket (REQ-011 narrowed from 8 to 10 inch) beside a 4S15P lid pack.
  --option qmx-outside  the QMX HF set leaves the lid and is carried outside the case, its HF function kept in the kit
                        through a sealed lead across the case wall (HELD on the relocation facts: l3r2.yaml's
                        `relocation_facts`); REQ-002 keeps its HF bearer with a note naming the set's place; the lid keeps
                        an 8 inch tablet bracket (REQ-011 narrowed) beside a 4S15P lid pack.
  --option tablet-out   the tablet bracket leaves the lid; holding the tablet in the lid leaves the kit, and the tablet's
                        use with the kit stays (carried outside the case, served by the kit's WiFi and the USB-C outlet of
                        REQ-017, which D-01 defers from prototype 1's acceptance); REQ-011 is restated (its old statement
                        kept as an SPD record); the QMX stays in its lid tray beside a 4S14P lid pack.
  --option both-kept    both approved lid items stay (the QMX in its lid tray, the tablet bracket), and the lid carries a
                        4S9P pack (a1mech DECISION-A1.md option 3); no function leaves the kit. The target is valid;
                        the records find the studied 4S9P lid NOT MET on the reference day, as every case of the energy
                        basis's first issue does (reproduced by its check), so feasibility item FI-04 records it (a
                        feasibility record, a core BLOCKER reading FAIL, D-26).
Every option writes the lid's count into REQ-014, REQ-075 and CFL-006. With row L3-OD6 decided, the lid must carry its
answer's store in its build case by row L3-OD6's filled table; otherwise feasibility item FI-02 records the valid target
the studied candidate does not meet (both-kept has FI-04). Row L3-OD1 rejected: this row does not apply (every option sets
a lid pack, which contradicts the kept one-pack store), and the script refuses. --table PATH reads that table from a fixture on a copy of the registry.

Where each option leaves a function (the relocation facts, fact CF-04 of l3r2.yaml): no location in the kit is
established for either displaced item, so qmx-out removes HF from the kit and tablet-out removes the bracket's function
(a tablet held in the lid); qmx-outside stays held until a record establishes the QMX's place and its sealed lead.

Usage: python3 od_l3_2.py --option qmx-out|qmx-outside|tablet-out|both-kept --words "<the owner's words>" --date YYYY-MM-DD
       [--table PATH] [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cond as C  # noqa: E402
import od_l3_1 as O1  # noqa: E402

E = C.E
ROW = "L3-OD2"
COUNT = {"qmx-out": 15, "qmx-outside": 15, "tablet-out": 14, "both-kept": 9}
CHECK = "v2/docs/records/l3r2/checks/energy-basis-check-1/CHECK-1.md"
ASSERT = {
    "v2/docs/records/a1int/RECONCILE.md": ["4S14P, the tablet out (B, 56 places; 4S20P)", "4S15P, the QMX out (C, 61 places after the mechanical check; 4S21P)"],
    "v2/docs/records/a1mech/DECISION-A1.md": ["Keep an 8 inch tablet bracket; HF leaves the lid.", "Keep HF; the tablet bracket leaves the lid."],
    "v2/docs/records/a1mech/README.md": ["outside the case it would need a lead through the back wall, which\n   the ruled connector plate does not carry"],
}
ASSERT_BOTH = {
    "v2/docs/records/a1mech/DECISION-A1.md": ["Keep both; 4S9P in the lid, 4S15P in all."],
    "v2/docs/records/a1int/RECONCILE.md": ["NOT MET at 400, 650 and 1000 Wp", "4S9P, both lid functions kept | NOT MET"],
    CHECK: ["4S9P NOM; WE; WA; GEN | NOT MET"],
}
RULINGS = {
    "qmx-out": ("Row L3-OD2 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: the QMX HF set (appendix 32.50 item 16a) "
                "leaves the kit and its HF function leaves with it, the owner's explicit decision to remove an approved "
                "function; the kit carries no HF transmitter. The lid carries an 8 inch tablet bracket (item 16d, narrowed "
                "from 8 to 10 inch) beside a lid pack of 4S15P.",
                "The QMX HF set and its HF function leave the kit; the lid pack is 4S15P (row L3-OD2)"),
    "qmx-outside": ("Row L3-OD2 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: the QMX HF set (appendix 32.50 item "
                    "16a) leaves the lid and is carried outside the case, its HF function kept in the kit through a sealed "
                    "lead across the case wall, placed as l3r2.yaml's relocation facts state. The lid carries an 8 inch "
                    "tablet bracket (item 16d, narrowed from 8 to 10 inch) beside a lid pack of 4S15P.",
                    "The QMX HF set carried outside the case, HF kept; the lid pack is 4S15P (row L3-OD2)"),
    "tablet-out": ("Row L3-OD2 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: the tablet bracket (appendix 32.50 "
                   "item 16d) leaves the lid, and holding the tablet in the lid leaves the kit; the tablet's use with the "
                   "kit stays, carried outside the case and served by the kit's WiFi and the USB-C outlet of REQ-017, which "
                   "D-01 defers from prototype 1's acceptance. The lid carries the QMX HF set in its lid tray (item 16a) "
                   "beside a lid pack of 4S14P.",
                   "The tablet bracket leaves the lid, the tablet's use kept; the lid pack is 4S14P (row L3-OD2)"),
    "both-kept": ("Row L3-OD2 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: both approved lid items stay, the "
                  "QMX HF set in its lid tray (appendix 32.50 item 16a) and the tablet bracket (item 16d), beside a lid pack "
                  "of 4S9P (4S15P in all with the base pack). No function leaves the kit. The target is valid; the studied "
                  "4S9P lid does not meet M1 on the records, and feasibility item FI-04 records that (D-26).",
                  "Both lid items kept; the lid pack is 4S9P, feasibility item FI-04 (row L3-OD2)"),
}


def build(a, raw, d):
    for rel, n in ASSERT.items(): E.assert_in(rel, n)
    rt = C.runtime_first(d, ROW)
    dec0 = C.decided(d)
    if dec0.get("L3-OD1", ("",))[0] == "reject":
        E.refuse("row L3-OD2 does not apply: row L3-OD1 is rejected (%s), which keeps D-06's one pack, and every option of "
                 "this row sets a lid pack; the two requirements cannot both hold (l3r2.yaml's contradiction rules, D-26)"
                 % dec0["L3-OD1"][1])
    C.require(d, ROW, ["L3-OD1:approve"])
    op = a["option"]
    if op == "qmx-out" and rt["hf"] == "listening":
        E.refuse("row L3-OD2's qmx-out takes the HF set out of the kit, and row L3-OD7 (%s) sets its receiver listening "
                 "through M1: the two requirements cannot both hold (l3r2.yaml's contradiction rules, D-27)" % rt["rid"])
    if op == "both-kept":
        for rel, n in ASSERT_BOTH.items(): E.assert_in(rel, n)
    C.hold(a, ROW, C.row_holds(ROW) + (["relocation_facts"] if op == "qmx-outside" else []))
    recs = {r["id"]: r for r in d["records"]}
    n = COUNT[op]
    ruling, title = RULINGS[op]
    external = op == "both-kept" and rt["external"] != "no"
    if external:     # D-27: both kept is the owner's stated wish; with the external store its candidate is FI-07's
        ruling = ruling.replace("the studied 4S9P lid does not meet M1 on the records, and feasibility item FI-04 records that (D-26).",
                                "the studied 4S9P lid alone does not meet M1 on the records; with the external battery "
                                "arrangement %s authorises on row L3-OD7 the candidate is feasibility item FI-07's, "
                                "CONDITIONAL on its size (D-26, D-27)." % rt["rid"])
        title = title.replace("feasibility item FI-04", "the external store of row L3-OD7 (FI-07)")
        if "FI-07" not in ruling or "FI-07" not in title: E.refuse("the both-kept ruling does not name FI-07")
    raw, rid = C.add_ruling(raw, d, ROW, op, title, ruling, a["words"], a["date"])
    stamp = "%s (row L3-OD2, %s)" % (rid, a["date"])
    exp = {("owner_rulings", rid, "added")}

    # the lid's count into the per-pack records of row L3-OD1
    raw = E.replace_entry(raw, "REQ-014", lambda b: C.add_ruling_ref(C.replace_in_field(b, "acceptance", O1.LID_AH,
        "%.2f Ah for its %dP block" % (2.68 * n, n)), rid), "records")
    raw = E.replace_entry(raw, "REQ-075", lambda b: C.add_ruling_ref(C.replace_in_field(b, "statement", O1.LID_A,
        "%.2f A for its %dP block" % (1.02 * n, n)), rid), "records")
    raw = E.replace_entry(raw, "CFL-006", lambda b: C.add_ruling_ref(C.replace_in_field(b, "resolved_by", O1.LID_BLOCK,
        "a lid 4S%dP block (%s)" % (n, rid)), rid), "records")
    exp |= {("records", r, "changed") for r in ("REQ-014", "REQ-075", "CFL-006")}

    spd = E.next_id(d, "SPD", ("records",))
    if op in ("qmx-out", "qmx-outside"):
        raw = C.restate(raw, "REQ-011", stamp,
            statement="A bracket in the lid holds an 8 inch rugged tablet beside the lid pack (%s), fed by the USB-C outlet and the kit's WiFi." % rid)
        raw = E.replace_entry(raw, "REQ-011", lambda b: C.add_ruling_ref(b, rid), "records")
        exp |= {("records", "REQ-011", "changed")}
    if op == "qmx-out":
        old002, old067 = recs["REQ-002"], recs["REQ-067"]
        raw = C.restate(raw, "REQ-002", stamp,
            statement=("The kit also carries VHF voice and the kit-to-kit WiFi link as a messaging bearer that needs no "
                       "access point; it carries no HF bearer (%s)." % rid),
            acceptance=("In the functional check: a VHF voice exchange over a headset is heard by an external receiver, and "
                        "messages pass over the WiFi link to a second kit with no access point."))
        raw = C.restate(raw, "REQ-067", stamp,
            statement="The kit carries no HF transmitter (%s); an HF set operated beside the kit is outside it." % rid,
            acceptance="Inspection: the kit's bill of materials, its case template and its lid layout carry no HF transmitter.")
        for r in ("REQ-002", "REQ-067"):
            raw = E.replace_entry(raw, r, lambda b: C.add_ruling_ref(b, rid), "records")
        spd2 = "SPD-%03d" % (int(spd.split("-")[1]) + 1)
        raw = E.insert_after_entry(raw, "REQ-002", C.superseded_entry(spd, old002,
            "REQ-002 restated by %s (row L3-OD2, the QMX and HF out of the kit): the kit carries no HF bearer." % rid, rid), "records")
        raw = E.insert_after_entry(raw, "REQ-067", C.superseded_entry(spd2, old067,
            "REQ-067 restated by %s (row L3-OD2, the QMX and HF out of the kit): the kit carries no HF transmitter." % rid, rid), "records")
        def r068(b):
            b2 = C.replace_in_field(b, "statement", "(the QMX HF unit, the LimeSDR's transmit path,", "(the LimeSDR's transmit path,")
            if "the QMX HF unit, " in (E.field_text(b2, "acceptance") or ""):
                b2 = C.replace_in_field(b2, "acceptance", "(the QMX HF unit, the LimeSDR's", "(the LimeSDR's")
            b2 = E.append_folded(b2, "history", "The QMX HF unit removed from its list by %s." % stamp, after="source_check")
            return C.add_ruling_ref(b2, rid)
        raw = E.replace_entry(raw, "REQ-068", r068, "records")
        raw = E.replace_entry(raw, "CON-007", lambda b: E.append_folded(b, "notes",
            "Under %s the kit carries no QMX; this constraint binds only while board A draws the HF rail." % rid,
            after="source_check"), "records")
        exp |= {("records", r, "changed") for r in ("REQ-002", "REQ-067", "REQ-068", "CON-007")}
        exp |= {("records", spd, "added"), ("records", spd2, "added")}
    elif op == "qmx-outside":
        raw = E.replace_entry(raw, "REQ-002", lambda b: C.add_ruling_ref(E.append_folded(b, "notes",
            "Under %s the QMX HF set is carried outside the case and reaches the kit through a sealed lead across the case "
            "wall (l3r2.yaml's relocation facts); the HF bearer stays in the kit." % stamp, after="source_check"), rid), "records")
        exp |= {("records", "REQ-002", "changed")}
    elif op == "both-kept" and not external:
        raw, fid = C.feasibility_item(raw, "FI-04", [rid, "D-20", "D-21", "D-26"])
        exp |= {("records", fid, "added")}
    elif op == "both-kept":
        raw = E.replace_entry(raw, "REQ-072", lambda b: C.add_ruling_ref(E.append_folded(b, "notes",
            "Row L3-OD2 (%s): both lid items kept on a 4S9P lid, the owner's stated wish (D-27); with the external battery "
            "arrangement of row L3-OD7 (%s) the candidate is feasibility item FI-07's." % (stamp, rt["rid"])), rid), "records")
        exp |= {("records", "REQ-072", "changed")}
    else:
        old011 = recs["REQ-011"]
        raw = C.restate(raw, "REQ-011", stamp,
            statement=("An 8 to 10 inch rugged tablet used with the kit is carried outside the case and fed by the USB-C "
                       "outlet and the kit's WiFi; the lid carries no tablet bracket (%s)." % rid),
            acceptance=("A tablet model is named; in the functional check the tablet charges from the USB-C outlet and joins "
                        "the kit's WiFi; the case template and the lid module's drawings carry no tablet bracket."))
        raw = E.replace_entry(raw, "REQ-011", lambda b: C.add_ruling_ref(b, rid), "records")
        raw = E.insert_after_entry(raw, "REQ-011", C.superseded_entry(spd, old011,
            "REQ-011 restated by %s (row L3-OD2, the tablet out): the tablet is carried outside the case." % rid, rid), "records")
        exp |= {("records", "REQ-011", "changed"), ("records", spd, "added")}
    # row L3-OD6's weather basis against this lid (CHECK-2 of L3-R2, B2; D-26): a valid target the studied candidate
    # does not meet records feasibility item FI-02, unless a feasibility record already carries the weather answer
    ans = C.od6_answer(E.parse(raw))
    if ans and op != "both-kept":
        o6, share6, build6, rid6 = ans
        rows, fixture = C.od6_rows(a)
        t6 = C.od6_row(rows, o6, share6, build6)
        if not fixture: C.od6_verify(t6)
        if C.LID[op] not in t6["fits"] and not C.fea_citing(E.parse(raw), rid6):
            n_text = "SC-37's mean day" if o6 == "mean-day" else "at least %s percent of September's 72-hour windows" % share6
            raw, fid = C.weather_feasibility(raw, rid6, op, t6, n_text, extra_rulings=(rid,))
            exp |= {("records", fid, "added")}
    raw, _ = C.close_m02_if_done(raw, rid)
    return raw, exp


if __name__ == "__main__":
    sys.exit(C.run("od_l3_2", build, ("qmx-out", "qmx-outside", "tablet-out", "both-kept"), sys.argv[1:]))
