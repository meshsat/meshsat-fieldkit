#!/usr/bin/env python3
"""lid_21700.py: how many 21700 cells the lid holds with HF and the tablet kept, counted by the tree's own lid generator
(stream l3batt, MESHSAT-1357, 30 September 2026).

It runs v2/cad/lid_pack_a1.py (stream a1mech's generator, unchanged on disk) with ONE edit made in memory: the cell's
maximum diameter, maximum length and maximum mass, taken from each maker's sheet. Every other input (the lid's room at
Peli's worst figures, the face parts, the QMX set, the 8 inch tablet bracket, the wrap, joints, plate, cover, P2) stays
as a1mech set it for the INR18650-35E. It first proves that the unedited source reproduces the committed record
v2/docs/records/a1mech/lid_pack_a1.out byte for byte, and refuses otherwise (exit 4).

What it is and is not. It is a count, INFERRED: the module's allowances were set for 18650 cells and are not re-derived
for 21700; nothing is designed and no module is proposed. The base pockets are not counted: the generator's base rows
carry the ruled 18650 block's figures, so they say nothing about a 21700 block.

Run from the repository root:  python3 v2/docs/records/l3batt/lid_21700.py > v2/docs/records/l3batt/lid_21700.out
Deterministic. Exit 3: the generator's constants line is not as read; 4: the reproduction failed."""
import io
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
GEN = "v2/cad/lid_pack_a1.py"
REC = "v2/docs/records/a1mech/lid_pack_a1.out"
LINE = "CELL_D, CELL_L, CELL_M = 18.55, 65.25, 0.050"
CELLS = [   # (key, label, diameter max, length max, mass max kg, source)
    ("P45B", "Molicel INR-21700-P45B", 21.55, 70.15, 0.070, "Version 1.2 p.1: 21.55 mm (Max), 70.15 mm (Max), 70 g (Max)"),
    ("50E", "Samsung SDI INR21700-50E", 21.25, 70.80, 0.0695, "V1.0 3.14 and 3.15: 69.5 g max, height max 70.80, top diameter max 21.25 (held back)"),
    ("M50LT", "LG INR21700M50LT", 21.44, 70.60, 0.0692, "2.12 and 3.2: 68.2 +- 1.0 g (TBD), diameter <= 21.44, height <= 70.60 (held back)"),
]


def run(src):
    ns = {"__name__": "lid_pack_a1_variant", "__file__": os.path.join(TOP, GEN)}
    exec(compile(src, os.path.join(TOP, GEN), "exec"), ns)
    buf = io.StringIO()
    ns["main"](buf)
    return buf.getvalue()


def main():
    src = open(os.path.join(TOP, GEN), encoding="utf-8").read()
    if src.count(LINE) != 1:
        sys.stderr.write("lid_21700: the generator's cell line is not as read; refusing\n")
        return 3
    base = run(src)
    rec = open(os.path.join(TOP, REC), encoding="utf-8").read()
    o = []
    P = o.append
    P("THE LID WITH HF AND THE TABLET KEPT, COUNTED FOR 21700 CELLS BY a1mech's GENERATOR (lid_21700.py, stream l3batt, MESHSAT-1357).")
    P("PROTOTYPE DESIGN: nothing built or fitted. A count, INFERRED: only the cell's maximum diameter, length and mass changed.")
    P("")
    P("0. REPRODUCTION: the unedited generator reproduces %s byte for byte: %s" % (REC, "yes" if base == rec else "NO"))
    if base != rec:
        sys.stdout.write("\n".join(o) + "\n")
        return 4
    P("")

    def arr(text, name):
        blk = text.split("   ARRANGEMENT %s:" % name, 1)[1].split("\n   ARRANGEMENT", 1)[0]
        c = re.search(r"cells: (\d+) \(layer 1 (\d+), layer 2 (\d+)\)", blk)
        u = re.search(r"=> (4S\d+P) \((\d+) cells used", blk)
        return int(c.group(1)), int(c.group(2)), int(c.group(3)), u.group(1), int(u.group(2))

    def mass(text):
        m = re.search(r"^   A: HF kept, 8 inch tablet kept: lid ([\d.]+) kg in all", text, re.M)
        d = re.search(r"module depth: one layer ([\d.]+), two layers ([\d.]+)", text)
        return float(m.group(1)), float(d.group(1)), float(d.group(2))
    P("1. ARRANGEMENT A (HF, the QMX set r2, and the 8 inch tablet bracket kept in the lid) and, for reference, B (HF kept, no tablet)")
    P("   %-28s %-40s %-26s %-26s %s" % ("cell", "its maximum figures", "A: places (layers), used", "B: places, used", "A's lid in all; module depth 1 / 2 layers"))
    a0, b0, m0 = arr(base, "A"), arr(base, "B"), mass(base)
    P("   %-28s %-40s %-26s %-26s %.2f kg; %.2f / %.2f mm" % ("Samsung SDI INR18650-35E", "18.55 x 65.25 mm, 50 g (a1mech)",
                                                            "%d (%d + %d), %s" % (a0[0], a0[1], a0[2], a0[3]), "%d, %s" % (b0[0], b0[3]), m0[0], m0[1], m0[2]))
    for key, lab, d, l, mk, srcn in CELLS:
        t = run(src.replace(LINE, "CELL_D, CELL_L, CELL_M = %s, %s, %s" % (d, l, mk)))
        a, b, mm = arr(t, "A"), arr(t, "B"), mass(t)
        P("   %-28s %-40s %-26s %-26s %.2f kg; %.2f / %.2f mm" % (lab, "%.2f x %.2f mm, %.1f g" % (d, l, mk * 1000),
                                                                "%d (%d + %d), %s" % (a[0], a[1], a[2], a[3]), "%d, %s" % (b[0], b[3]), mm[0], mm[1], mm[2]))
        P("     source: %s" % srcn)
    P("   The lid's room is 44.39 mm at Peli's worst figures (a1mech 1): a second layer of 21700 cells needs the module's two-layer")
    P("   depth, so most second-layer places are refused by the face rows; the count falls to the one-layer places, fewer per")
    P("   area than for 18650 cells (INFERRED from the generator's own output, printed above)")
    P("")
    P("END. A count by the tree's generator with the cell's size changed; the allowances are the 18650 module's.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
