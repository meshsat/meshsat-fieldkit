#!/usr/bin/env python3
"""Each known-bad fixture put to the tool BEFORE the change and AFTER it (MESHSAT-1357, stream d6dec).

Usage (on the KiCad box): before_after.py <base tools dir> <new tools dir> <work dir> <out.json>
    base tools dir   v2/ecad/tools of a checkout at 73ae2f21, the set 6 candidate
    new tools dir    v2/ecad/tools of this branch
The fixtures are built once by the new tree's tests/decoupling_fixture.py, in <work dir>, and copied per run, so
both tools judge the same bytes. A fixture is DEFECTIVE when the ruling refuses it and ACCEPTABLE when it does not;
the table says what each tool answered, and whether the old tool's answer was the defect."""
import os, sys, json, shutil, subprocess, math

GATE = [  # scenario, what the ruling says, the defect the old gate shows
    ("g_unclassed", "FAIL", "an entry with no class is judged by its value string"),
    ("g_near", "PASS", None),
    ("g_far_blanket", "FAIL", "one line that names no capacitor allows every far one"),
    ("g_far_named", "PASS as a justified deviation", "an allowed capacitor is counted as a pass"),
    ("g_maker_cap", "FAIL", "an allowance passes the maker's own 5 mm"),
    ("g_value_bulk", "PASS", "a bare 10u is held to 3.0 mm whatever its class"),
    ("g_value_pin", "FAIL", "a value spelled 10u 25V 1210 is given 6.0 mm whatever its class"),
    ("g_farside_onesided", "FAIL", "a far-side capacitor on a one-sided board is judged by distance alone"),
    ("g_farside_past", "FAIL", "a far-side capacitor pays nothing for its vias"),
    ("g_farside_fan", "FAIL", "a far-side capacitor inside a fan is judged by distance alone"),
    ("g_shared_via", "PASS as a deviation", "any via of the net within 1.5 mm counts as the pad's own"),
]
PLACE = [
    ("p_window", "seated in the own-pin window", "the fan is closed to every capacitor"),
    ("p_converter", "seated inside its converter's fan", "a six-pin converter has no fan and the seat is measured to the centre"),
    ("p_farside", "seated on the other side", "the other side is never offered"),
    ("p_unclassed", "refused", "an entry with no class is seated at 3.0 mm"),
]


def run(cmd, cwd, env=None):
    e = dict(os.environ); e.pop("ESCAPE_SKIP", None); e["PYTHONDONTWRITEBYTECODE"] = "1"; e["VERDICT_DIR"] = os.path.join(cwd, "out")
    e.update(env or {})
    r = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True, timeout=900)
    return r.returncode, r.stdout + r.stderr


def main(a):
    base, new, work, out = a[0], a[1], a[2], a[3]
    fixture = os.path.join(new, "tests", "decoupling_fixture.py")
    rows = []
    for kind, table, tool in (("gate", GATE, "intent_checks.py"), ("placer", PLACE, "bypass_place.py")):
        for scen, ruled, defect in table:
            src = os.path.join(work, "src", scen); shutil.rmtree(src, ignore_errors=True); os.makedirs(src)
            rc, o = run([sys.executable, fixture, "build", scen, src], src)
            assert rc == 0, o[-600:]
            row = {"kind": kind, "scenario": scen, "ruling": ruled, "defect": defect}
            for label, tools in (("before", base), ("after", new)):
                d = os.path.join(work, label, scen); shutil.rmtree(d, ignore_errors=True); shutil.copytree(src, d)
                rc, o = run([sys.executable, os.path.join(tools, tool), os.path.join(d, "fix.kicad_pcb")], d)
                ans = {"exit": rc}
                if kind == "gate":
                    vp = os.path.join(d, "out", "intent_decoupling.verdict.json")
                    v = json.load(open(vp)) if os.path.exists(vp) else {}
                    ans.update({"verdict": v.get("verdict"), "counts": v.get("counts"),
                                "line": next((l for l in o.split("\n") if "bypass C1" in l), "")[:300]})
                else:
                    rc2, o2 = run([sys.executable, fixture, "read", os.path.join(d, "fix.kicad_pcb")], d)
                    st = json.loads(o2.strip().splitlines()[-1]) if rc2 == 0 else {}
                    c = st.get("C1") or {}
                    part = "U2" if scen.startswith("p_converter") else "U1"
                    pin = (st.get(part) or {}).get("pads", {}).get("3") or {}
                    rail = (c.get("pads") or {}).get("1") or {}
                    ans.update({"summary": next((l for l in o.split("\n") if " moved, " in l), "")[:200],
                                "line": next((l for l in o.split("\n") if "C1" in l and ("->" in l or "STUCK" in l or "REFUSED" in l)), "")[:300],
                                "C1": {"x": c.get("x"), "y": c.get("y"), "back": c.get("back"), "rot": c.get("rot")},
                                "rail_pad_to_pin_mm": round(math.hypot(rail.get("x", 0) - pin.get("x", 0), rail.get("y", 0) - pin.get("y", 0)), 3) if rail and pin else None})
                row[label] = ans
            rows.append(row)
    json.dump({"what": "each fixture before the change (tools at the base commit) and after it", "base_tools": base,
               "new_tools": new, "rows": rows}, open(out, "w"), indent=1)
    for r in rows:
        b, n = r["before"], r["after"]
        if r["kind"] == "gate":
            print("%-20s ruling %-32s before %-5s %s | after %-5s %s" % (r["scenario"], r["ruling"], b.get("verdict"), json.dumps(b.get("counts")), n.get("verdict"), json.dumps(n.get("counts"))))
        else:
            print("%-20s ruling %-32s before %s rail %s back %s | after %s rail %s back %s" % (r["scenario"], r["ruling"], (b.get("summary") or b.get("line"))[:60], b.get("rail_pad_to_pin_mm"), b["C1"].get("back"), (n.get("summary") or "")[:60], n.get("rail_pad_to_pin_mm"), n["C1"].get("back")))
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
