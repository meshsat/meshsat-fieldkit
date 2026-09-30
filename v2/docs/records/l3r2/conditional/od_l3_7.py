#!/usr/bin/env python3
"""Row L3-OD7 of OWNER-DECISIONS-L3.md: M1's runtime requirement. PREPARED, NOT APPLIED. No prerequisite; answered
before rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6, whose scripts refuse until it is (D-27, cond.runtime_first). HELD by the
owner's addendum (D-27) until the bounded runtime and battery comparison of stream l3batt is filed with its accepted
check: the script refuses to write the tree's registry while l3r2.yaml's `runtime_comparison` is not filed (a copy is
not held). Structure only: the figures are the comparison's, and nothing here states one.

D-27, the owner: "Evaluate alternatives before asking me to sacrifice functions or accept restrictive deployment
conditions." As relayed: "He also said to preserve HF and the tablet functionality."

  --option 72-required                   72 hours required, as REQ-072 states it; the figure becomes the owner's in place
                                         of the session's SC-21 (REQ-072's statement names the ruling)
  --option 48-required-72-desired        48 hours required, 72 hours desired, HF and the tablet kept: REQ-072's statement
                                         and acceptance restated to 48 hours, the 72 hours desired and the rows' figures
                                         (for 72 hours) noted as restated from the comparison (closure item L3-C56)
  --option 72-required-battery-upgrade   72 hours required with an upgraded battery arrangement, HF and the tablet kept:
                                         REQ-072's statement names the ruling; the arrangement and the rows that depend
                                         on the store are restated from the comparison (L3-C56)

Usage: python3 od_l3_7.py --option <option> --words "<the owner's words>" --date YYYY-MM-DD [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cond as C  # noqa: E402

E = C.E
ROW = "L3-OD7"
OPTIONS = ("72-required", "48-required-72-desired", "72-required-battery-upgrade")
PAGE = "v2/docs/handover/layer3/OWNER-DECISIONS-L3.md"
OLD_ST = "for M1's 72 hours (SC-21)"
OLD_ACC = ("ends the 72 hours above the graceful shutdown threshold", "the kit runs PS-IDLE-SPEC for 72 hours from a full pack")
RULING = {
    "72-required": ("Row L3-OD7 of %s decided: M1's runtime is 72 hours required, as REQ-072 states it; the figure is the "
                    "owner's own setting in place of the session's SC-21, which D-20 had preserved with M1's specified "
                    "duration." % PAGE),
    "48-required-72-desired": ("Row L3-OD7 of %s decided: M1's runtime is 48 hours required, with 72 hours desired; HF "
                               "and the tablet are kept (D-27). REQ-072 is restated to 48 hours, and the rows whose "
                               "prepared restatements state 72 hours are restated from the runtime comparison before they "
                               "are applied." % PAGE),
    "72-required-battery-upgrade": ("Row L3-OD7 of %s decided: M1's runtime is 72 hours required, with an upgraded battery "
                                    "arrangement; HF and the tablet are kept (D-27). The arrangement is the runtime "
                                    "comparison's, and the rows that depend on the store are restated from it before they "
                                    "are applied." % PAGE),
}


def build(a, raw, d):
    C.require(d, ROW, [])
    C.hold(a, ROW)
    op = a["option"]
    recs = {r["id"]: r for r in d["records"]}
    sc = next((c for c in d.get("session_choices") or [] if c["id"] == "SC-21"), None)
    if sc is None or "72 hours" not in " ".join(str(sc.get("taken")).split()):
        E.refuse("SC-21 does not take M1's 72 hours: the provenance this row states is not the registry's")
    st = " ".join(recs["REQ-072"]["statement"].split())
    if st.count(OLD_ST) != 1: E.refuse("REQ-072's statement does not carry %r once" % OLD_ST)
    raw, rid = C.add_ruling(raw, d, ROW, op, "M1's runtime answered, %s (row L3-OD7)" % op, RULING[op], a["words"], a["date"])
    stamp = "%s (row L3-OD7, %s)" % (rid, a["date"])
    if op == "48-required-72-desired":
        acc = " ".join(recs["REQ-072"]["acceptance"].split())
        for o in OLD_ACC:
            if acc.count(o) != 1: E.refuse("REQ-072's acceptance does not carry %r once" % o)
        acc = acc.replace(OLD_ACC[0], OLD_ACC[0].replace("72", "48")).replace(OLD_ACC[1], OLD_ACC[1].replace("72", "48"))
        raw = C.restate(raw, "REQ-072", stamp, statement=st.replace(
            OLD_ST, "for 48 hours, M1's required duration (owner ruling %s on row L3-OD7, in place of SC-21's 72 hours; 72 "
                    "hours desired)" % rid), acceptance=acc)
        note = ("Row L3-OD7 (%s): 48 hours required and 72 hours desired, HF and the tablet kept (D-27); the 72 hours are a "
                "design objective beside the requirement, not its pass line. This record's evidence and the prepared "
                "restatements of rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 are for 72 hours and are restated from the runtime "
                "comparison (l3r2.yaml runtime_comparison, closure item L3-C56); until then its FAIL reads for 72 hours." % stamp)
    else:
        raw = C.restate(raw, "REQ-072", stamp, statement=st.replace(
            OLD_ST, "for M1's 72 hours (owner ruling %s on row L3-OD7, in place of SC-21)" % rid))
        note = ("Row L3-OD7 (%s): 72 hours required, the owner's own setting, which replaces the session's SC-21 (D-20 had "
                "preserved M1's specified duration without setting the figure)." % stamp)
        if op == "72-required-battery-upgrade":
            note += (" With an upgraded battery arrangement, HF and the tablet kept (D-27): the arrangement is the runtime "
                     "comparison's, and rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 are restated from it (l3r2.yaml "
                     "runtime_comparison, closure item L3-C56).")
    E.screen(note, "REQ-072's note")
    raw = E.replace_entry(raw, "REQ-072", lambda b: C.add_ruling_ref(E.append_folded(b, "notes", note), rid))
    return raw, {("owner_rulings", rid, "added"), ("records", "REQ-072", "changed")}


if __name__ == "__main__":
    sys.exit(C.run("od_l3_7", build, OPTIONS, sys.argv[1:]))
