#!/usr/bin/env python3
"""Fill row L3-OD7's table (l3r2.yaml `runtime_table`) from the filed, checked runtime comparison by exact keys (layer 3
round 5, MESHSAT-1357, 30 September 2026). The pattern of v2/docs/records/l3r2/fill_l3r2_from_basis.py.

It refuses unless l3r2.yaml's `runtime_comparison` names stream l3batt's record with its accepted check, every file byte
identical to the checked tip's (basis_binding.py), and unless runtime.out reads its two reproduction lines as yes. It
writes `runtime_table` and nothing else: the both-kept store (runtime.out 1 and 2), and for 48 and 72 hours and the
corrected path's cases NOM, WE and NOM90 the addition over the both-kept 4S9P lid in TYP and WAB (runtime.out 3), the
HF-receiving addition in TYP (section 3's sensitivity), the energy unserved and where the kit stops (section 2) and the
modelled historical coverage (section 4); the as-drawn circuit's shortfall beside them. Every figure is the text the output
prints (runtime_reader.py); the result is re-parsed and read back against the reader, and a second run is refused. The
row's prose is the session's, written from these figures and tested against them (test_l3r5.py).

Usage: python3 fill_l3r7_from_comparison.py [--check] [--data PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2", "conditional"))
import l3edit as E  # noqa: E402
import cond as C  # noqa: E402
import runtime_reader as RR  # noqa: E402

CASES = ("NOM", "WE", "NOM90")
PLACE = "    runtime_table: null\n"
NOTE = ("Filled by v2/docs/records/l3r5/fill_l3r7_from_comparison.py from runtime.out of the checked comparison (stream "
        "l3batt, fnd/l3batt 83577a13, CHECK-2) by exact keys and read back; od_l3_7.py reads the filed output again before "
        "it writes an answer. HF and the tablet kept (a1mech arrangement A). The additions are over the both-kept lid "
        "(4S9P), in usable Wh at the lid's 13.23 C on the COMB line with the kit never stopping; every figure with the sun "
        "rests on the corrected path (HYPOTHETICAL, CONDITIONAL on three efficiencies), the circuit as drawn failing.")


def table(text):
    b, s, sol, up, hf, cov = (RR.battery_only(text), RR.store_start(text), RR.solar(text), RR.upgrade(text),
                              RR.hf_listening(text), RR.coverage(text))
    if not RR.reproduced(text): raise RR.RuntimeFormatError("runtime.out does not read its reproduction lines as yes")
    store = {"usable_20": b["A35"]["usable_20"], "usable_m10": b["A35"]["usable_m10"], "hours_20": b["A35"]["hours_20"],
             "hours_m10": b["A35"]["hours_m10"], "d06_hours_20": b["D06"]["hours_20"], "nh1_hours_20": b["X-NH1"]["hours_20"],
             "nh2_hours_20": b["X-NH2"]["hours_20"], "start_total": s["total"], "start_base": s["base"], "start_lid": s["lid"],
             "drawn_48": "%s / %s" % (sol[("48", "DRAWN", "TYP")]["unserved"], sol[("48", "DRAWN", "WAB")]["unserved"]),
             "drawn_72": "%s / %s" % (sol[("72", "DRAWN", "TYP")]["unserved"], sol[("72", "DRAWN", "WAB")]["unserved"])}
    rows = []
    for h in ("48", "72"):
        for c in CASES:
            rows.append({"hours": h, "case": c, "typ_wh": up[(h, c, "TYP")]["wh"], "typ_cells": up[(h, c, "TYP")]["cells"],
                         "wab_wh": up[(h, c, "WAB")]["wh"], "wab_cells": up[(h, c, "WAB")]["cells"],
                         "listening_wh": hf[(h, c)]["wh"] if (h, c) in hf else None,
                         "typ_unserved": sol[(h, c, "TYP")]["unserved"], "wab_unserved": sol[(h, c, "WAB")]["unserved"],
                         "stops": sol[(h, c, "TYP")]["stops"], "coverage": cov[(h, c)][0]})
    return {"store": store, "rows": rows}


def q(v):
    return "null" if v is None else '"%s"' % v


def block(t):
    s = "    runtime_table:\n      note: >-\n%s      store: {%s}\n      rows:\n" % (
        E.fold(NOTE, 8), ", ".join("%s: %s" % (k, q(v)) for k, v in t["store"].items()))
    for r in t["rows"]:
        s += "        - {%s}\n" % ", ".join("%s: %s" % (k, q(v) if k not in ("case",) else v) for k, v in r.items())
    return s


def main(argv):
    path = argv[argv.index("--data") + 1] if "--data" in argv else C.L3DATA
    raw = open(path, encoding="utf-8").read()
    try:
        import yaml
        data = yaml.safe_load(raw)
        ok, why = C.basis_state(data, key="runtime_comparison")
        if not ok: E.refuse("the runtime comparison is not bound: %s" % why)
        out = next(o for o in data["runtime_comparison"]["outputs"] if str(o["path"]).endswith("runtime.out"))
        t = table(open(os.path.join(E.TOP, out["path"]), encoding="utf-8").read())
        row = next(d for d in data["decisions"] if d["id"] == "L3-OD7")
        if row.get("runtime_table") is not None:
            if row["runtime_table"].get("store") == t["store"] and row["runtime_table"].get("rows") == t["rows"]:
                print("fill_l3r7_from_comparison: REFUSED: row L3-OD7's table is filled and reads back equal; this script has run")
            else:
                print("fill_l3r7_from_comparison: REFUSED: row L3-OD7's table differs from the filed runtime.out")
            return 2
        if raw.count(PLACE) != 1: E.refuse("l3r2.yaml does not carry %r once" % PLACE.strip())
        new = raw.replace(PLACE, block(t))
        back = next(d for d in yaml.safe_load(new)["decisions"] if d["id"] == "L3-OD7")["runtime_table"]
        if back["store"] != t["store"] or back["rows"] != t["rows"]: E.refuse("the table does not read back equal")
    except (E.Refused, RR.RuntimeFormatError) as e:
        print("fill_l3r7_from_comparison: REFUSED: %s" % e)
        return 2
    print("fill_l3r7_from_comparison: %d rows and the store read back equal%s" % (len(t["rows"]), " (check only)" if "--check" in argv else ""))
    if "--check" not in argv:
        open(path, "w", encoding="utf-8").write(new)
        print("fill_l3r7_from_comparison: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
