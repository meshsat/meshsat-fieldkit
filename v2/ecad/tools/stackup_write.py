#!/usr/bin/env python3
"""Write the JLC stackup into a board file (MESHSAT-862, 8 Sep 2026): the six-layer B16 and the four-layer boards carried no dielectric or
epsilon entry at all, so the 90 and 100 ohm order notes were unconnected to any geometry in the project and no impedance could be read back.
Numbers from JLCPCB's impedance page (read 8 Sep 2026): JLC04161H-7628 (4 layers, 1.6 mm): Cu 0.035, prepreg 7628 0.2104 Dk 4.4, Cu 0.0152,
core 1.065 Dk 4.6, Cu 0.0152, prepreg 7628 0.2104, Cu 0.035.  JLC06161H-3313 (6 layers, 1.6 mm): Cu 0.035, prepreg 3313 0.0994 Dk 4.1,
Cu 0.0152, core 0.55 Dk 4.6, Cu 0.0152, prepreg 2116 0.1088 Dk 4.16, Cu 0.0152, core 0.55, Cu 0.0152, prepreg 3313 0.0994, Cu 0.035.
Two-layer boards: FR-4 core 1.6 (or the board thickness) Dk 4.6 under 1 oz.  The block is written as text into (setup ...) after pcbnew saved
the board, because the KiCad 9 Python API does not build a BOARD_STACKUP from scratch reliably; KiCad reads it as its own.

Usage: stackup_write.py <board.kicad_pcb> [JLC04161H-7628|JLC06161H-3313|2L] ; the name defaults from the copper layer count.  Prints the layers and the total."""
import sys, re

STACKS = {
    "JLC04161H-7628": [("F.Cu", 0.035), ("pp", "FR4 prepreg 7628", 0.2104, 4.4), ("In1.Cu", 0.0152), ("core", "FR4 core", 1.065, 4.6), ("In2.Cu", 0.0152), ("pp", "FR4 prepreg 7628", 0.2104, 4.4), ("B.Cu", 0.035)],
    "JLC06161H-3313": [("F.Cu", 0.035), ("pp", "FR4 prepreg 3313", 0.0994, 4.1), ("In1.Cu", 0.0152), ("core", "FR4 core", 0.55, 4.6), ("In2.Cu", 0.0152), ("pp", "FR4 prepreg 2116", 0.1088, 4.16),
                       ("In3.Cu", 0.0152), ("core", "FR4 core", 0.55, 4.6), ("In4.Cu", 0.0152), ("pp", "FR4 prepreg 3313", 0.0994, 4.1), ("B.Cu", 0.035)],
    "2L": [("F.Cu", 0.035), ("core", "FR4 core", 1.51, 4.6), ("B.Cu", 0.035)],
    # OWNER RULING 12 September 2026, decision 7: P and E5 are ordered at 2 oz, which is what their prose has
    # always claimed and what the order set must now say. 2 oz is 0.070 mm of copper against 1 oz's 0.035, and
    # it is the reason the ruling went this way: P's FUSED band measured 193.5 A/mm2 at 1 oz against IPC-2221's
    # 82.7, and doubling the copper halves the density on a board that carries the whole pack current. dc_drop
    # and every current-density check judge against the stackup, so this entry is what makes the ruling real
    # rather than a sentence in a document.
    "2L-2oz": [("F.Cu", 0.070), ("core", "FR4 core", 1.44, 4.6), ("B.Cu", 0.070)],
}
LOSS = 0.02

def block(name, thickness=None):
    st = STACKS[name]; lines = ["  (stackup"]
    lines.append('    (layer "F.SilkS" (type "Top Silk Screen"))')
    lines.append('    (layer "F.Paste" (type "Top Solder Paste"))')
    lines.append('    (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))')
    n = 0
    for it in st:
        if len(it) == 2:
            lines.append('    (layer "%s" (type "copper") (thickness %s))' % (it[0], it[1]))
        else:
            kind, mat, t, dk = it; n += 1
            lines.append('    (layer "dielectric %d" (type "%s") (thickness %s) (material "%s") (epsilon_r %s) (loss_tangent %s))' % (n, "prepreg" if kind == "pp" else "core", t, mat, dk, LOSS))
    lines.append('    (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))')
    lines.append('    (layer "B.Paste" (type "Bottom Solder Paste"))')
    lines.append('    (layer "B.SilkS" (type "Bottom Silk Screen"))')
    lines.append('    (copper_finish "ENIG")')
    lines.append('    (dielectric_constraints no)')
    lines.append("  )")
    return "\n".join(lines)

def total(name): return round(sum(it[1] if len(it) == 2 else it[2] for it in STACKS[name]), 4)

def write(path, name=None):
    s = open(path, encoding="utf-8").read()
    ncu = len(re.findall(r'^\s+\(\d+ "(?:F|B|In\d+)\.Cu" (?:signal|power|mixed|jumper)\)', s, re.M))
    if name is None: name = {4: "JLC04161H-7628", 6: "JLC06161H-3313"}.get(ncu, "2L-2oz")   # decision 7: two-layer boards are 2 oz
    want = [it[0] for it in STACKS[name] if len(it) == 2]
    if len(want) != ncu: raise SystemExit("stackup_write: %s has %d copper layers, board file lists %d" % (name, len(want), ncu))
    s2 = s; k = s.find("(stackup")   # drop an existing block by matching its parentheses (the regex to the first close cut a saved board in half, 8 Sep 2026)
    if k >= 0:
        depth = 0; e = k
        while e < len(s):
            if s[e] == "(": depth += 1
            elif s[e] == ")":
                depth -= 1
                if depth == 0: break
            e += 1
        j = s.rfind("\n", 0, k); s2 = s[:j + 1] + s[e + 1:].lstrip("\n")
    m = re.search(r"\n[ \t]+\(setup\n", s2)
    if not m: raise SystemExit("stackup_write: no (setup) block in %s" % path)
    s2 = s2[:m.end()] + block(name) + "\n" + s2[m.end():]
    open(path, "w", encoding="utf-8").write(s2)
    print("stackup_write: %s (%d copper layers, %s mm dielectric and copper) written into %s" % (name, ncu, total(name), path))
    return name

if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    write(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
