#!/usr/bin/env python3
"""The three shapes of moving a declared entry, on the three REAL board tables as apply_port_declarations.py corrects
them, in a scratch tree, never in the tree (MESHSAT-1357, worker d8dec31, 28 September 2026; the fresh check's item B1,
open item S-88). It reads TRN-001 with VERDICT_DIR set, on copies of the corrected tables, and asserts each shape reads
what the reviewed set demands:

  baseline      the corrected declaration and the reviewed set agree: PASS, the counts as the review states them
  moved-ground  an external entry re-pointed at ground pins (board A's J_DOCK shape): FAIL, the reviewed pin named
  removed       an external entry deleted from both lists: INCONCLUSIVE, named UNCOVERED and REVIEWED
  reclassified  an external entry moved into internal_ports with a reason (the checker's counter-example, J_USBW on A):
                INCONCLUSIVE, named RECLASSIFIED, and the same pins counted; before this change it read PASS of 38
  narrowed      an entry narrowed by `pins` with the rest declared internal: INCONCLUSIVE for the pins that left
  zero          every external entry gone and the zero given its reason: INCONCLUSIVE, not PASS
  reconciled    the reclassification carried into the reviewed set with its reason and its review: PASS again

It restores each table after every case. Usage: regress_reclassify.py <scratch tree root with the corrected tables>
"""
import json, os, subprocess, sys

NETLIST = {"a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "d": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net",
           "e": "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"}
# the entry each board's case moves: an external entry with more than one live pin where the board has one
MOVE = {"a": "J_USBW", "d": "J_HS1", "e": "J_POD"}
WANT_PASS = {"a": 42, "d": 21, "e": 13}
WHY = "said to stay inside the case now, the lead having moved to a harness under the plate"


def run(root, letter, vd):
    os.makedirs(vd, exist_ok=True)
    r = subprocess.run([sys.executable, os.path.join(root, "v2", "ecad", "tools", "port_protect.py"), os.path.join(root, NETLIST[letter])],
                       cwd=os.path.join(root, "v2", "ecad"), capture_output=True, text=True, timeout=300,
                       env=dict(os.environ, VERDICT_DIR=vd))
    v = json.load(open(os.path.join(vd, "port_protect_%s.verdict.json" % letter)))
    return r.returncode, r.stdout + r.stderr, v


def main(root):
    root = os.path.abspath(root)
    tools = os.path.join(root, "v2", "ecad", "tools")
    reviews_p = os.path.join(tools, "pcb_port_reviews.json")
    scratch = os.path.join(root, "_regress_verdicts")
    failed = 0
    for letter in ("a", "d", "e"):
        tp = os.path.join(tools, "boards", "%s.json" % letter)
        orig = open(tp, encoding="utf-8").read()
        rev_orig = open(reviews_p, encoding="utf-8").read()
        t0 = json.loads(orig)
        assert "internal_ports" in t0, "board %s's table is not the corrected one (apply_port_declarations.py first)" % letter
        ref = MOVE[letter]
        ext = [e for e in t0["external_ports"] if e["ref"] == ref]
        assert ext, (letter, ref)

        def case(name, table, want_rc, words, reviews=None):
            nonlocal failed
            open(tp, "w", encoding="utf-8").write(json.dumps(table, indent=1, ensure_ascii=False) + "\n")
            if reviews is not None: open(reviews_p, "w", encoding="utf-8").write(json.dumps(reviews, indent=1, ensure_ascii=False) + "\n")
            try:
                rc, out, v = run(root, letter, os.path.join(scratch, letter, name))
            finally:
                open(tp, "w", encoding="utf-8").write(orig); open(reviews_p, "w", encoding="utf-8").write(rev_orig)
            missing = [w for w in words if w not in out]
            ok = rc == want_rc and not missing
            failed += 0 if ok else 1
            c = v.get("counts") or {}
            print("%s board %s %-12s rc=%d want %d verdict %s of %s ports %s ext_pins %s reviewed %s disagreements %s%s"
                  % ("ok  " if ok else "FAIL", letter.upper(), name, rc, want_rc, v.get("verdict"), v.get("denominator"),
                     c.get("ports"), c.get("declared_external_pins"), c.get("reviewed_pins"), c.get("review_disagreements"),
                     ("  MISSING: " + " | ".join(missing)) if missing else ""))
            for line in out.splitlines():
                if any(k in line for k in ("RECLASSIFIED", "REVIEWED ", "NOT REVIEWED", "UNCOVERED", "names no conductor", "verdict:")):
                    print("      " + line.strip()[:200])
            return v

        # baseline
        v = case("baseline", t0, 0, ["the reviewed set holds"])
        assert v["verdict"] == "PASS" and v["denominator"] == WANT_PASS[letter], (letter, v["verdict"], v["denominator"])
        # moved onto ground pins: the entry's pins are re-pointed at the connector's ground pin(s) via an explicit list
        # of a pin that is ground on this netlist (board A: J_DOCK-style; here the entry's own ground pin)
        _bn, by_ref, _v = __import__("port_protect").netlist(os.path.join(root, NETLIST[letter]))
        gnd = [p for p, n in sorted(by_ref[ref]) if not __import__("port_protect").carries_conductor(n)]
        live = [p for p, n in sorted(by_ref[ref]) if __import__("port_protect").carries_conductor(n)]
        if gnd:
            t1 = json.loads(orig)
            for e in t1["external_ports"]:
                if e["ref"] == ref: e["pins"] = gnd[:1]
            case("moved-ground", t1, 1, ["%s.%s is on" % (ref, gnd[0]), "names no conductor", "REVIEWED %s.%s" % (ref, live[0]),
                                        "UNCOVERED %s.%s" % (ref, live[0])])
        else:
            print("      board %s: %s has no ground pin, the moved-ground shape is the fixture test's" % (letter.upper(), ref))
        # removed from both lists
        t2 = json.loads(orig); t2["external_ports"] = [e for e in t2["external_ports"] if e["ref"] != ref]
        case("removed", t2, 3, ["UNCOVERED %s.%s" % (ref, live[0]), "REVIEWED %s.%s" % (ref, live[0])])
        # reclassified into internal_ports with a reason (the checker's counter-example)
        t3 = json.loads(orig); t3["external_ports"] = [e for e in t3["external_ports"] if e["ref"] != ref]
        t3["internal_ports"] = t3["internal_ports"] + [{"ref": ref, "why": WHY}]
        v3 = case("reclassified", t3, 3, ["RECLASSIFIED %s.%s" % (ref, live[0])])
        assert v3["counts"]["review_disagreements"] == len(live), v3["counts"]
        # narrowed by pins, the rest internal
        if len(live) > 1:
            t4 = json.loads(orig)
            for e in t4["external_ports"]:
                if e["ref"] == ref: e["pins"] = live[:1]
            t4["internal_ports"] = t4["internal_ports"] + [{"ref": ref, "pins": live[1:], "why": WHY}]
            case("narrowed", t4, 3, ["RECLASSIFIED %s.%s" % (ref, live[1])])
        # the declared zero
        t5 = json.loads(orig); t5["external_ports"] = []; t5["_external_ports_why"] = "every conductor of this board ends inside the sealed case now, the reason written here"
        t5["internal_ports"] = t5["internal_ports"] + [{"ref": e["ref"], "why": WHY} for e in t0["external_ports"]]
        case("zero", t5, 3, ["RECLASSIFIED %s.%s" % (ref, live[0]), "this board declares no external port, and the reviewed set holds"])
        # reconciled: the reviewed set carries the change with its reason and its review
        rv = json.loads(rev_orig)
        rec = rv["boards"][letter]
        moved = rec["external"].pop(ref)
        rec["changes"] = rec["changes"] + [{"entry": "%s.%s" % (ref, p), "was": "external", "now": "internal", "on": "2026-09-28",
                                            "review": rec["review"], "why": "a regression fixture: the lead is said to have moved under the plate, and the review is named so the change can be audited"}
                                           for p in moved]
        case("reconciled", t3, 0, ["the reviewed set holds %d external pin(s)" % (sum(len(x) for x in rec["external"].values()))], reviews=rv)
    print("regress_reclassify: %d case(s) failed" % failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.abspath(sys.argv[1]), "v2", "ecad", "tools"))
    sys.exit(main(sys.argv[1]))
