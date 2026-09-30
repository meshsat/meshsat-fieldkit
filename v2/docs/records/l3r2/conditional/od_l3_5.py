#!/usr/bin/env python3
"""Row L3-OD5 of OWNER-DECISIONS-L3.md: CFL-017, D-02a's qualification margins against the cells' +60 C. PREPARED, NOT
APPLIED. No prerequisite.

  --option reading-c  the owner reads D-02a: its margins are the kit's without its cells, the cells held inside their
                      maker's limits. CFL-017 becomes CONFLICT_RESOLVED (NOT_JUDGED until its sources are read again),
                      REQ-051's closing clause is restated, both cite the new ruling.
  --option measure    CFL-017 stays open until the bounded enclosure heat experiment; a note
  --option cells      cells rated above +60 C are to be selected (D-06's cell reopened, money); CFL-017 stays open; a note

Usage: python3 od_l3_5.py --option reading-c|measure|cells --words "<the owner's words>" --date YYYY-MM-DD [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cond as C  # noqa: E402

E = C.E
ROW = "L3-OD5"
OLD_051 = ("and the kit with its own pack does not meet the +55 C, the +60 C humid and the storage levels (CFL-017, finding "
           "BAT-F19).")
RULING = {
    "reading-c": ("Row L3-OD5 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided, the owner's reading of D-02a: its "
                  "+55 C operating, +71 C and -33 C storage margins and TEST-PLAN E5's +60 C humid dwell are qualification "
                  "margins of the kit without its cells; the cells are held inside their maker's limits (REQ-046, REQ-074), "
                  "and no margin result is reported as the kit's with its pack."),
    "measure": ("Row L3-OD5 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: CFL-017 stays open until the bounded "
                "enclosure heat experiment (POWER-THERMAL.md section 10) is run on hardware."),
    "cells": ("Row L3-OD5 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: cells rated above +60 C are to be "
              "selected for the pack, which reopens D-06's cell and asks for money; CFL-017 stays open until the cell is "
              "chosen and its sheet is held."),
}


def build(a, raw, d):
    C.require(d, ROW, [])
    op = a["option"]
    recs = {r["id"]: r for r in d["records"]}
    if recs["CFL-017"]["status"] != "CONFLICT_OPEN": E.refuse("CFL-017 is not CONFLICT_OPEN")
    raw, rid = C.add_ruling(raw, d, ROW, op, "CFL-017 answered, %s (row L3-OD5)" % op, RULING[op], a["words"], a["date"])
    stamp = "%s (row L3-OD5, %s)" % (rid, a["date"])
    if op == "reading-c":
        if OLD_051 not in " ".join(recs["REQ-051"]["statement"].split()): E.refuse("REQ-051's closing clause is not the text restated")
        raw = C.restate(raw, "REQ-051", stamp, statement=" ".join(recs["REQ-051"]["statement"].split()).replace(
            OLD_051, "and by %s the margins are the kit's without its cells, the cells held inside their maker's limits "
                     "(REQ-046, REQ-074)." % rid))
        raw = E.replace_entry(raw, "REQ-051", lambda b: C.add_ruling_ref(b, rid))
        def f(b):
            b = C.set_line(b, "status", "CONFLICT_RESOLVED", after="choices")
            b = C.set_line(b, "evidence_result", "NOT_JUDGED", after="status")
            b = C.drop_field(b, "evidence_phase")
            b = E.set_folded(b, "resolved_by", "%s, the owner's reading of D-02a: its margins are the kit's without its cells, "
                             "the cells held inside their maker's limits (REQ-046, REQ-074)." % rid, after="status")
            b = C.add_ruling_ref(b, rid)
            return E.append_folded(b, "notes", "Resolved by %s; it reads NOT_JUDGED until REQ-051 and TEST-PLAN E3, E4 and "
                                   "E5 are read again against the reading." % stamp)
        raw = E.replace_entry(raw, "CFL-017", f)
        exp = {("owner_rulings", rid, "added"), ("records", "CFL-017", "changed"), ("records", "REQ-051", "changed")}
    else:
        raw = E.replace_entry(raw, "CFL-017", lambda b: C.add_ruling_ref(E.append_folded(b, "notes",
            "The owner answered row L3-OD5 on %s (%s, option %s): it stays open." % (a["date"], rid, op)), rid))
        exp = {("owner_rulings", rid, "added"), ("records", "CFL-017", "changed")}
    return raw, exp


if __name__ == "__main__":
    sys.exit(C.run("od_l3_5", build, ("reading-c", "measure", "cells"), sys.argv[1:]))
