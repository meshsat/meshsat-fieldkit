#!/usr/bin/env python3
"""load_trace.py: PS-IDLE-SPEC's 42.8 W traced to its loads (stream l3batt, MESHSAT-1357, 30 September 2026; the owner's
instruction of that day: "Trace the load profile behind the quoted 42.8 W.").

It reads the committed power budget, records/rv-pwr/pwr_budget.out (the model feasibility/POWER-THERMAL.md section 4
quotes), and the load declarations in records/rv-pwr/pwr_budget.py for each load's stated source. It adds nothing: it
sums the battery-side shares, groups them by the budget's own tiers (S a primary document gives the number; R a primary
document bounds it and the figure sits inside by a stated duty; D a generator's declaration; T a placeholder with no
document), and names the HF and tablet related rows. Every figure is the budget's, at the pack terminals, PLAN.

Run from the repository root:  python3 v2/docs/records/l3batt/load_trace.py > v2/docs/records/l3batt/load_trace.out
Deterministic. Exit 3: an input cannot be parsed or the shares do not close to the stated total."""
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
OUT = "v2/docs/records/rv-pwr/pwr_budget.out"
PY = "v2/docs/records/rv-pwr/pwr_budget.py"


def refuse(msg):
    sys.stderr.write("load_trace: %s; refusing\n" % msg)
    sys.exit(3)


def main():
    t = open(os.path.join(TOP, OUT), encoding="utf-8").read()
    py = open(os.path.join(TOP, PY), encoding="utf-8").read()
    head = re.search(r"^PS-IDLE-SPEC load\s+([\d.]+) \| battery\s+([\d.]+) /\s+([\d.]+) /\s+([\d.]+) \| S\s+([\d.]+) R\s+([\d.]+) D\s+([\d.]+) T\s+([\d.]+)", t, re.M)
    if not head:
        refuse("the PS-IDLE-SPEC header")
    blk = t.split("== shares PS-IDLE-SPEC\n", 1)[1].split("\n==", 1)[0]
    rows = re.findall(r"^\s+(.+?)\s+load\s+([\d.]+)\s+battery\s+([\d.]+)\s+([SRDT])\s*$", blk, re.M)
    typ = t.split("== shares PS-TYP\n", 1)[1].split("\n==", 1)[0]
    qmx = re.search(r"^\s+QMX HF\s+load\s+([\d.]+)\s+battery\s+([\d.]+)\s+([SRDT])", typ, re.M)
    sys.path.insert(0, os.path.dirname(os.path.join(TOP, PY)))
    import pwr_budget as PB   # its loads register at import; its main() is behind __main__
    src = {name: source for name, _node, _d, source in PB.LOADS}
    total = sum(float(r[2]) for r in rows)
    if abs(total - float(head.group(3))) > 0.05 or not qmx:
        refuse("the shares do not close to %.1f W (%.2f)" % (float(head.group(3)), total))
    o = []
    P = o.append
    P("PS-IDLE-SPEC TRACED TO ITS LOADS (load_trace.py, stream l3batt, MESHSAT-1357), from %s" % OUT)
    P("")
    P("1. THE STATE: 'PS-IDLE as V2-SPEC.md line 23 words it: monitor on, APRS beacons; the idle state of the D-06 runtime")
    P("   requirement, with the kit-to-kit link card up and idle' (CONOPS 4a). At the loads %s W; at the pack terminals LOW %s /" % (head.group(1), head.group(2)))
    P("   PLAN %s / HIGH %s W (HIGH puts every load at its maximum at once: an upper bound, not a scenario); PLAN by tier, W:" % (head.group(3), head.group(4)))
    P("   S %s, R %s, D %s, T %s" % head.groups()[4:8])
    P("")
    P("2. THE %d LOADS, battery-side W at PLAN, largest first (tier; the budget's stated source, pwr_budget.py)" % len(rows))
    for name, ld, bt, tier in rows:
        s_ = src.get(name, "").strip()
        s_ = re.sub(r"\s+", " ", s_)[:160]
        P("   %6.2f  %s  %-44s %s" % (float(bt), tier, name, s_))
    P("   sum %.2f W (the stated %s W)" % (total, head.group(3)))
    P("")
    hf = [r for r in rows if "QMX" in r[0]]
    P("3. HF AND THE TABLET IN THIS STATE")
    for name, ld, bt, tier in hf:
        P("   HF: %s, %s W at the battery (%s); the QMX's own 12 V receiver is NOT powered in PS-IDLE-SPEC" % (name, bt, tier))
    P("   HF receiving is a PS-TYP load: 'QMX HF' %s W at the load, %s W at the battery (%s: %s)" % (
        qmx.group(1), qmx.group(2), qmx.group(3), re.sub(r"\s+", " ", src.get("QMX HF", ""))[:120]))
    P("   The tablet: no row. It runs on its own battery; the kit's USB-C PD outlet, the one path that could charge it, is off")
    P("   in every state (pwr_budget.py: 'The outlets are off in every state and switched on only by the section 7.1 variants';")
    P("   contract 15 V at 3 A, 45 W). The profile keeps both functions in the kit at these duties; it does not power HF reception")
    P("   or charge the tablet")
    P("")
    P("END. The budget's own figures, summed; nothing is measured.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
