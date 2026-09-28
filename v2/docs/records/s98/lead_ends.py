#!/usr/bin/env python3
"""The two ends of the board A to board B power leads, read from the two intent files (stream s98, MESHSAT-1357,
28 September 2026; finding I-03, contract IF-AB-POWER, open item S-98).

DECLARATION CONSISTENCY ONLY. This reads what each board declares for the five leads and says whether the two ends
carry one figure per conductor. It is not an electrical adequacy check: it reads no converter limit, no lead rating and
no mode current, and it decides nothing about S-99 (the +5V_DEV converter-side coincidence). It writes nothing.

Per lead:
  +5V_S1, +5V_S2, +5V_S3   board A's rail typical and peak against board B's, and A's load on J_5V_Sx against A's peak
                           (the whole rail leaves on the lead)
  +5V_DEV                  the LEAD: A's apportionment to J_5V_DEV against B's typical arriving. The converter side
                           (A's peak against B's peak plus A's own branches) is printed and labelled S-99, never judged.
  +54V_POE                 A's rail typical and peak against B's

Usage: lead_ends.py [--a <A intent json>] [--b <B intent json>]   (defaults: the tree's committed files)
Exit 0 when the five leads AGREE, 1 otherwise. The inputs are named by sha256/16 on the first lines.
"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DEFAULT_A = os.path.join(ROOT, "v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json")
DEFAULT_B = os.path.join(ROOT, "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json")
TOL = 0.005


def opt(argv, k, d):
    return argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else d


def same(x, y):
    return x is not None and y is not None and abs(float(x) - float(y)) < TOL


def main(argv):
    pa, pb = opt(argv, "--a", DEFAULT_A), opt(argv, "--b", DEFAULT_B)
    out = []
    for tag, p in (("A", pa), ("B", pb)):
        b = open(p, "rb").read()
        out.append("lead_ends: %s intent %s sha256/16 %s" % (tag, os.path.relpath(p, ROOT) if p.startswith(ROOT) else p, hashlib.sha256(b).hexdigest()[:16]))
    A = json.load(open(pa, encoding="utf-8"))["rails"]; B = json.load(open(pb, encoding="utf-8"))["rails"]
    agree = 0; rows = []
    for net, lead in (("+5V_S1", "J_5V_S1"), ("+5V_S2", "J_5V_S2"), ("+5V_S3", "J_5V_S3")):
        a, b = A.get(net), B.get(net)
        if not a or not b: rows.append("%-9s MISSING at %s" % (net, "A" if not a else "B")); continue
        la = (a.get("loads") or {}).get(lead)
        ok = same(a["amps_typ"], b["amps_typ"]) and same(a["amps_peak"], b["amps_peak"]) and same(la, a["amps_peak"])
        agree += ok
        rows.append("%-9s %-8s A %.2f / %.2f A (load %s %s), B %.2f / %.2f A" % (net, "AGREE" if ok else "DISAGREE", a["amps_typ"], a["amps_peak"], lead, la, b["amps_typ"], b["amps_peak"]))
    a, b = A.get("+5V_DEV"), B.get("+5V_DEV")
    if a and b:
        la = (a.get("loads") or {}).get("J_5V_DEV")
        ok = same(la, b["amps_typ"]); agree += ok
        others = {k: v for k, v in (a.get("loads") or {}).items() if k != "J_5V_DEV"}
        rows.append("%-9s %-8s at the lead: A apportions %s A to J_5V_DEV, B declares %.2f A typical arriving; A's typical %.2f A = %s + %s"
                    % ("+5V_DEV", "AGREE" if ok else "DISAGREE", la, b["amps_typ"], a["amps_typ"], la, " + ".join("%s %.2f" % kv for kv in sorted(others.items()))))
        rows.append("%-9s S-99     converter side, NOT JUDGED HERE: A's peak %.2f A against B's peak %.2f A arriving plus A's other branches at their load figures (%.2f A); the coincident figures and the LM5176 average loop's limit are S-99's"
                    % ("", a["amps_peak"], b["amps_peak"], sum(others.values())))
    else:
        rows.append("+5V_DEV   MISSING")
    a, b = A.get("+54V_POE"), B.get("+54V_POE")
    if a and b:
        ok = same(a["amps_typ"], b["amps_typ"]) and same(a["amps_peak"], b["amps_peak"]); agree += ok
        rows.append("%-9s %-8s A %.2f / %.2f A (load J_54V %s), B %.2f / %.2f A" % ("+54V_POE", "AGREE" if ok else "DISAGREE", a["amps_typ"], a["amps_peak"], (a.get("loads") or {}).get("J_54V"), b["amps_typ"], b["amps_peak"]))
    else:
        rows.append("+54V_POE  MISSING")
    out += ["lead_ends: " + r for r in rows]
    out.append("lead_ends: %d of 5 leads AGREE (declaration consistency only; adequacy, the mode currents and S-99 are not judged here)" % agree)
    print("\n".join(out))
    return 0 if agree == 5 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
