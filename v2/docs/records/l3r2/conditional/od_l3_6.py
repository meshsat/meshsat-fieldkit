#!/usr/bin/env python3
"""Row L3-OD6 of OWNER-DECISIONS-L3.md: M1's weather basis, a quantified choice. PREPARED, NOT APPLIED. HELD by the
owner's instruction of 30 September 2026 (D-23: the row's recommendation and figures wait on the checked energy basis;
"An average-day benchmark may be an option; do not select it automatically because the current design passes it"): the
script refuses to write the tree's registry while l3r2.yaml's energy_basis is not filed with an accepted check.

Row L3-OD7 (M1's runtime) is answered first (D-27, cond.runtime_first): this script refuses while it is unanswered,
and after an answer other than 72-required, because its restatement states M1's 72 hours; it is then restated from
the runtime comparison before it is applied.

The owner's words of D-22: "Define 'adverse.' A model based on a September average day does not establish performance
across unspecified adverse weather." REQ-072 states M1 on SC-37's reference mean day today. The owner's answer names the
option and the array build case (TYP or WAB, l3r2.yaml's quantified.builds):

  --option mean-day --build B               the average-day benchmark: M1 stays judged on SC-37's reference mean day;
                                            REQ-072's notes state the benchmark's limitations and the store it asks in
                                            build B, so that nobody reads it as a statement about real weather
  --option coverage --share N --build B     a historical-coverage target: M1 must also hold in at least N percent of the
                                            72-hour windows of September's actual weather at SC-37's site and plane; N
                                            is one of the table's targets (50, 80, 95); REQ-072's statement and
                                            acceptance gain one marked sentence each (od_l3_1.py carries them over)

Either way the answer's table row must be filled (a HELD row is refused), and for l3r2.yaml's own table every figure is
read again from the filed weather_basis.out by exact keys and compared (cond.od6_verify). The store must be carried by a
lid (CHECK-2 of L3-R2, B2): with row L3-OD2 decided, by its lid; without it, by at least one lid of the table. Otherwise
the answer is still a valid target (D-26) and a feasibility record holds REQ-072: FI-02 (the lid does not carry the mean
day's store in the build) or FI-03 (a coverage target no lid carries), a core BLOCKER reading FAIL; with row L3-OD2
answered both-kept, its own item FI-04 already holds REQ-072 and no second one is written. No answer here is refused for
the candidate's shortfall. SC-37 cites the ruling. The ruling
records `weather_share` and `weather_build`, which od_l3_2.py and the gate read.

Usage: python3 od_l3_6.py --option mean-day|coverage --build TYP|WAB [--share 50|80|95] --words "<the owner's words>"
       --date YYYY-MM-DD [--table PATH] [--check] [--registry PATH]
--table PATH reads the targets from a fixture (a copy of the registry only: the tests and dryrun.py).
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cond as C  # noqa: E402

E = C.E
ROW = "L3-OD6"
LIMITS = ("one site and one month's mean day, repeated for the 72 hours; a mean day is not a cloudy day, and no "
          "worse-weather case is established; it states no share of real September weather in which M1 holds")
WINDOWS = ("the 72-hour windows of September's actual weather at SC-37's site and plane (PVGIS-SARAH2 hourly "
           "irradiance on the 40 degree south plane at Leiden, 2005 to 2020, every window starting at 06 or 18 UTC on 1 "
           "to 27 September: 864 windows)")


def build(a, raw, d):
    op = a["option"]
    C.runtime_first(d, ROW)
    dec = C.require(d, ROW, [])
    C.hold(a, ROW)
    b = a["extra"].get("build")
    if b not in ("TYP", "WAB"): E.refuse("--build TYP or WAB, the array build case the owner names, is required")
    sc = next(c for c in d["session_choices"] if c["id"] == "SC-37")
    if "4.0 kWh/m2 a day" not in " ".join(str(sc["taken"]).split()): E.refuse("SC-37 does not state 4.0 kWh/m2 a day")
    n = None
    if op == "coverage":
        s = str(a["extra"].get("share") or "")
        if not s.isdigit() or not 1 <= int(s) <= 100:
            E.refuse("coverage needs --share N, one of the table's targets as a whole percent")
        n = int(s)
    rows, fixture = C.od6_rows(a)
    t = C.od6_row(rows, op, n, b)
    if not fixture: C.od6_verify(t)
    recs = {r["id"]: r for r in d["records"]}
    need = ("in the %s build it asks %s Wh usable, a lid block of %s, %s cells, %s Wh nominal, %s kg and %s / %s litres "
            "of cells (%s)" % (b, t["usable_wh"], t["lid_block"], t["cells"], t["nominal_wh"], t["mass_kg"], t["volume_cyl_l"],
                               t["volume_box_l"], t["evidence"]))
    extra = {"weather_share": n, "weather_build": b}
    if op == "mean-day":
        n_text = "SC-37's mean day"
        ruling = ("Row L3-OD6 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: the average-day benchmark, in the "
                  "%s array build case. Mission M1 is judged on SC-37's reference mean day (the September mean day at "
                  "Leiden on the 40 degree south plane, 4.0 kWh/m2), with the benchmark's limitations stated in REQ-072: "
                  "%s. M1 keeps its setting and carries no season." % (b, LIMITS))
        raw, rid = C.add_ruling(raw, d, ROW, op, "M1's weather basis: the average-day benchmark, %s (row L3-OD6)" % b, ruling,
                                a["words"], a["date"], extra)
        note = ("M1's weather basis (%s, row L3-OD6, %s): the average-day benchmark in the %s build. REQ-072 is judged on "
                "SC-37's reference mean day: %s. It is a design benchmark, not a promise that the kit runs 72 hours in real "
                "September weather. On the checked energy basis %s." % (rid, a["date"], b, LIMITS, need))
        E.screen(note, "REQ-072's note")
        raw = E.replace_entry(raw, "REQ-072", lambda blk: C.add_ruling_ref(E.append_folded(blk, "notes", note), rid), "records")
    else:
        n_text = "at least %d percent of September's 72-hour windows" % n
        worst = ("the lowest 72-hour irradiation of the record" if n == 100 else
                 "the %s percentile of 72-hour irradiation over those windows" % C.ordinal(100 - n))
        ruling = ("Row L3-OD6 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: a historical-coverage target, in "
                  "the %s array build case. Mission M1 must also hold in at least %d percent of %s, each started from a "
                  "full, aged store; SC-37's reference day stays the design day of REQ-072's mean-day calculation."
                  % (b, n, WINDOWS))
        raw, rid = C.add_ruling(raw, d, ROW, op, "M1's weather basis: at least %d percent of September's windows, %s (row L3-OD6)"
                                % (n, b), ruling, a["words"], a["date"], extra)
        stamp = "%s (row L3-OD6, %s)" % (rid, a["date"])
        st_add = ("%s, %s): M1 also holds in at least %d percent of %s, each started from a full, aged store, in the %s "
                  "array build case." % (C.OD6_MARK, rid, n, WINDOWS, b))
        acc_add = ("%s, %s): desk, the calculation above, run hour by hour over each of those windows in the %s build, "
                   "meets its pass line in at least %d percent of them; prototype, the 72-hour run is repeated with the "
                   "array emulator following the hourly irradiance of the window at %s." % (C.OD6_MARK, rid, b, n, worst))
        r072 = recs["REQ-072"]
        raw = C.restate(raw, "REQ-072", stamp,
                        statement=" ".join(str(r072["statement"]).split()) + " " + st_add,
                        acceptance=" ".join(str(r072["acceptance"]).split()) + " " + acc_add)
        note = "M1's historical coverage (%s): on the checked energy basis %s." % (stamp, need)
        E.screen(note, "REQ-072's note")
        raw = E.replace_entry(raw, "REQ-072", lambda blk: C.add_ruling_ref(E.append_folded(blk, "notes", note), rid), "records")
    exp = {("owner_rulings", rid, "added"), ("records", "REQ-072", "changed")}
    lid_opt = dec.get("L3-OD2", (None,))[0]
    lid = C.LID.get(lid_opt) if lid_opt else None
    if lid_opt != "both-kept" and ((lid and lid not in t["fits"]) or (not lid and not t["fits"])):
        raw, fid = C.weather_feasibility(raw, rid, lid_opt, t, n_text)
        exp |= {("records", fid, "added")}
    raw = E.replace_entry(raw, "SC-37", lambda blk: E.set_flow(blk, "source", E.flow_items(blk, "source") +
                                                              ['"owner ruling %s"' % rid]), "session_choices")
    exp |= {("session_choices", "SC-37", "changed")}
    return raw, exp


if __name__ == "__main__":
    sys.exit(C.run("od_l3_6", build, ("mean-day", "coverage"), sys.argv[1:]))
