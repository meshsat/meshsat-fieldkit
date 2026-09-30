#!/usr/bin/env python3
"""Row L3-OD6 of OWNER-DECISIONS-L3.md: M1's weather basis, a quantified choice. PREPARED, NOT APPLIED. HELD by the
owner's instruction of 30 September 2026 (D-23: the row's recommendation and figures wait on the checked energy basis;
"An average-day benchmark may be an option; do not select it automatically because the current design passes it"): the
script refuses to write the tree's registry while l3r2.yaml's `energy_basis` is not filed (a copy is not held).

The owner's words of D-22: "Define 'adverse.' A model based on a September average day does not establish performance
across unspecified adverse weather." REQ-072 states M1 on SC-37's reference mean day today. The row's options:

  --option mean-day   the average-day benchmark: M1 stays judged on SC-37's reference mean day, and REQ-072's notes state
                      the benchmark's limitations (one site and one month's mean day repeated; a mean day is not a cloudy
                      day; no share of real weather stated), so that nobody reads it as a statement about real weather.
                      With --stat "<sentence>" --stat-evidence PATH, a sentence of the checked basis (asserted in that file)
                      is added as informative.
  --option coverage   a historical-coverage target: M1 must also hold in at least --share N percent of the 72-hour
                      windows of September's actual weather at SC-37's site and plane. N must be one of the targets of
                      the row's quantified table in l3r2.yaml (`quantified.rows`), with its figures filled from the checked
                      basis; a held (empty) target is refused. REQ-072's statement and acceptance gain one marked sentence
                      each (od_l3_1.py carries them over if row L3-OD1 is applied after). Where the table says the target
                      does not fit the case, an open conflict (the next free CFL id, a core BLOCKER) records it with the
                      figures; otherwise REQ-072's notes carry them. Refused while row L3-OD4 stands answered adopt: its
                      band comes from mean-day grids, and no band exists for a coverage target.
Both options cite the ruling in SC-37's sources. Every figure written is asserted in the evidence file the table names.

Usage: python3 od_l3_6.py --option mean-day|coverage --words "<the owner's words>" --date YYYY-MM-DD [--share N]
       [--stat "<sentence>" --stat-evidence PATH] [--table PATH] [--check] [--registry PATH]
--table PATH reads the quantified targets from a fixture (a copy of the registry only: the tests and dryrun.py).
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
FIGS = ("usable_wh", "nominal_wh", "mass_kg", "volume_l", "fits", "evidence")


def targets(a):
    """The row's quantified targets: l3r2.yaml's, or a fixture given with --table on a copy of the registry."""
    import yaml
    tp = a["extra"].get("table")
    if tp:
        if os.path.abspath(a["registry"]) == os.path.abspath(E.REGISTRY):
            E.refuse("--table is a fixture for a copy of the registry; the tree's registry reads l3r2.yaml")
        data = yaml.safe_load(open(tp, encoding="utf-8"))
    else:
        data = C.l3data()
    if "rows" in data: return data["rows"]
    row = next(x for x in data["decisions"] if x["id"] == ROW)
    return row["quantified"]["rows"]


def evidence_text(path):
    p = path if os.path.isabs(path) else os.path.join(E.TOP, path)
    if not os.path.isfile(p): E.refuse("the evidence %s is not in this tree" % path)
    return " ".join(open(p, encoding="utf-8").read().split())


def figures(t):
    """The target's figures, each asserted in its evidence file."""
    miss = [k for k in FIGS if t.get(k) in (None, "")]
    if miss: E.refuse("the target %s is HELD: its %s are not filled from the checked energy basis" % (t.get("id"), ", ".join(miss)))
    if str(t["fits"]).upper() not in ("YES", "NO"): E.refuse("the target %s: fits is %r, not YES or NO" % (t["id"], t["fits"]))
    text = evidence_text(t["evidence"])
    for k in ("usable_wh", "nominal_wh", "mass_kg", "volume_l"):
        if str(t[k]) not in text: E.refuse("%s does not carry %s's %s %s" % (t["evidence"], t["id"], k, t[k]))
    return t


def sc37(raw, rid):
    return E.replace_entry(raw, "SC-37", lambda b: E.set_flow(b, "source", E.flow_items(b, "source") +
                                                             ['"owner ruling %s"' % rid]), "session_choices")


def build(a, raw, d):
    op = a["option"]
    dec = C.require(d, ROW, [])
    C.hold(a, ROW)
    sc = next(c for c in d["session_choices"] if c["id"] == "SC-37")
    if "4.0 kWh/m2 a day" not in " ".join(str(sc["taken"]).split()): E.refuse("SC-37 does not state 4.0 kWh/m2 a day")
    recs = {r["id"]: r for r in d["records"]}
    if op == "mean-day":
        ruling = ("Row L3-OD6 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: the average-day benchmark. Mission "
                  "M1 is judged on SC-37's reference mean day (the September mean day at Leiden on the 40 degree south "
                  "plane, 4.0 kWh/m2), with the benchmark's limitations stated in REQ-072: %s. M1 keeps its setting and "
                  "carries no season." % LIMITS)
        raw, rid = C.add_ruling(raw, d, ROW, op, "M1's weather basis: the average-day benchmark (row L3-OD6)", ruling,
                                a["words"], a["date"])
        note = ("M1's weather basis (%s, row L3-OD6, %s): the average-day benchmark. REQ-072 is judged on SC-37's reference "
                "mean day: %s. It is a design benchmark, not a promise that the kit runs 72 hours in real September "
                "weather." % (rid, a["date"], LIMITS))
        stat, sev = a["extra"].get("stat"), a["extra"].get("stat-evidence")
        if stat or sev:
            if not (stat and sev): E.refuse("--stat and --stat-evidence go together")
            if " ".join(stat.split()) not in evidence_text(sev): E.refuse("%s does not carry the sentence given" % sev)
            note += " Informative, from the checked energy basis (%s): %s" % (sev, " ".join(stat.split()))
        E.screen(note, "REQ-072's note")
        raw = E.replace_entry(raw, "REQ-072", lambda b: C.add_ruling_ref(E.append_folded(b, "notes", note), rid), "records")
        exp = {("owner_rulings", rid, "added"), ("records", "REQ-072", "changed")}
    else:
        if dec.get("L3-OD4", ("",))[0] == "adopt":
            E.refuse("row L3-OD4 stands answered adopt: its band comes from mean-day grids and no band exists for a "
                     "coverage target; row L3-OD4 is answered again first")
        s = str(a["extra"].get("share") or "")
        if not s.isdigit() or not 1 <= int(s) <= 100:
            E.refuse("coverage needs --share N, the owner's share of windows as a whole percent from 1 to 100")
        n = int(s)
        t = next((x for x in targets(a) if str(x.get("share")) == str(n)), None)
        if t is None: E.refuse("the quantified table has no target of %d percent: the checked basis gives no figures for it" % n)
        t = figures(t)
        worst = ("the lowest 72-hour irradiation of the record" if n == 100 else
                 "the %s percentile of 72-hour irradiation over those windows" % C.ordinal(100 - n))
        ruling = ("Row L3-OD6 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: a historical-coverage target. "
                  "Mission M1 must also hold in at least %d percent of %s, each started from a full, aged store; SC-37's "
                  "reference day stays the design day of REQ-072's mean-day calculation." % (n, WINDOWS))
        raw, rid = C.add_ruling(raw, d, ROW, op, "M1's weather basis: at least %d percent of September's windows (row L3-OD6)" % n,
                                ruling, a["words"], a["date"])
        stamp = "%s (row L3-OD6, %s)" % (rid, a["date"])
        st_add = ("%s, %s): M1 also holds in at least %d percent of %s, each started from a full, aged store."
                  % (C.OD6_MARK, rid, n, WINDOWS))
        acc_add = ("%s, %s): desk, the calculation above, run hour by hour over each of those windows, meets its pass line "
                   "in at least %d percent of them; prototype, the 72-hour run is repeated with the array emulator following "
                   "the hourly irradiance of the window at %s." % (C.OD6_MARK, rid, n, worst))
        r072 = recs["REQ-072"]
        raw = C.restate(raw, "REQ-072", stamp,
                        statement=" ".join(str(r072["statement"]).split()) + " " + st_add,
                        acceptance=" ".join(str(r072["acceptance"]).split()) + " " + acc_add)
        raw = E.replace_entry(raw, "REQ-072", lambda b: C.add_ruling_ref(b, rid), "records")
        exp = {("owner_rulings", rid, "added"), ("records", "REQ-072", "changed")}
        need = ("on the checked energy basis it needs %s Wh usable, %s Wh nominal, %s kg and %s litres of store (%s)"
                % (t["usable_wh"], t["nominal_wh"], t["mass_kg"], t["volume_l"], t["evidence"]))
        if str(t["fits"]).upper() == "NO":
            # a repository path is a source; a fixture outside the tree (the tests, dryrun.py) is named in the text only
            src = ['"owner ruling %s"' % rid] + ([] if os.path.isabs(t["evidence"]) else ['"%s"' % t["evidence"]])
            cid = E.next_id(E.parse(raw), "CFL", ("records",))
            st = ("REQ-072's historical coverage (%s: M1 in at least %d percent of September's 72-hour windows) cannot be "
                  "met inside the case, the Peli 1450 of the current moulding: %s, which the case does not hold."
                  % (rid, n, need))
            acc = ("One of: an owner ruling that changes the coverage target, M1's duration or operating state, or the "
                   "store, functions or enclosure the kit carries, after which REQ-072 is judged again; until then "
                   "REQ-072 reads FAIL and layer 3 is not complete.")
            for x in (st, acc): E.screen(x, cid)
            entry = ("  - id: %s\n    kind: conflict\n    parent: NEED-05\n    statement: >-\n%s    acceptance: >-\n%s"
                     "    allocated_to: [kit, procedure]\n    verification_method: [MANUAL_REVIEW]\n    verification_phase: SCHEMATIC\n"
                     "    prototype_1: core\n    prototype_1_basis: NEED_DEFAULT\n    satisfied_by:\n      rules: []\n      decisions: []\n"
                     "    rule_coverage: NONE\n    rulings: [%s, D-20, D-21, D-22, D-23]\n    status: CONFLICT_OPEN\n    evidence_result: FAIL\n"
                     "    evidence_phase: SCHEMATIC\n    release_effect: BLOCKER\n"
                     "    source: [%s]\n"
                     "    source_check: VERIFIED\n" % (cid, E.fold(st, 6), E.fold(acc, 6), rid, ", ".join(src)))
            raw = E.insert_after_entry(raw, "REQ-072", entry, "records")
            exp |= {("records", cid, "added")}
        else:
            note = "M1's historical coverage (%s): %s, which fits the case." % (stamp, need)
            E.screen(note, "REQ-072's note")
            raw = E.replace_entry(raw, "REQ-072", lambda b: E.append_folded(b, "notes", note), "records")
    raw = sc37(raw, rid)
    exp |= {("session_choices", "SC-37", "changed")}
    return raw, exp


if __name__ == "__main__":
    sys.exit(C.run("od_l3_6", build, ("mean-day", "coverage"), sys.argv[1:]))
