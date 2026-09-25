#!/usr/bin/env python3
"""Write the JLC stackup into a board file (MESHSAT-862, 8 Sep 2026): the six-layer B16 and the four-layer boards carried no dielectric or
epsilon entry at all, so the 90 and 100 ohm order notes were unconnected to any geometry in the project and no impedance could be read back.
Numbers from JLCPCB's impedance page, transcribed into v2/vendor/fabricator/jlcpcb-impedance-stackups-2026-09-16.md
on 16 September 2026 (they had been in this comment alone, citing a reading of 8 September with no file behind it): JLC04161H-7628 (4 layers, 1.6 mm): Cu 0.035, prepreg 7628 0.2104 Dk 4.4, Cu 0.0152,
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
    # Dk 4.5 AND NOT 4.6 on a two-layer board (16 September 2026). The fabricator's own capability document
    # states its FR-4 dielectric constants per build, and for a 2-layer board it says 4.5
    # (v2/vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md, the FR-4 dielectric constants row). The 4.6
    # here came from its impedance page on 8 September, which is a different page about the multilayer cores.
    # Neither two-layer board carries an impedance target today, so nothing computed moves; the number matches
    # its source now, which is the point of having one.
    "2L": [("F.Cu", 0.035), ("core", "FR4 core", 1.51, 4.5), ("B.Cu", 0.035)],
    # OWNER RULING 12 September 2026, decision 7: P and E5 are ordered at 2 oz, which is what their prose has
    # always claimed and what the order set must now say. 2 oz is 0.070 mm of copper against 1 oz's 0.035, and
    # it is the reason the ruling went this way: P's FUSED band measured 193.5 A/mm2 at 1 oz against IPC-2221's
    # 82.7, and doubling the copper halves the density on a board that carries the whole pack current. dc_drop
    # and every current-density check judge against the stackup, so this entry is what makes the ruling real
    # rather than a sentence in a document.
    "2L-2oz": [("F.Cu", 0.070), ("core", "FR4 core", 1.44, 4.5), ("B.Cu", 0.070)],
    # AUTHORITY: OWNER RULING 25 September 2026, decision 28 (appendix 32.365; pcb_decisions.yaml n 28, authority
    # OWNER, ruled_on 2026-09-25): board P goes to four layers at 2 oz outer copper. This table is on the never-auto
    # floor (reserved.json, class "layer count and stackup"), and this row is added under that ruling alone; no
    # other row was changed with it (26 September 2026, MESHSAT-1357).
    # SOURCE: JLCPCB's JLC04162H-7628, the default ("No requirement") at 4 layers, 1.6 mm, 2 oz outer, 0.5 oz inner,
    # read 25 September 2026 from jlcpcb.com/impedance with its 2 oz outer selector and from the order form, and
    # transcribed in v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md. Layer sum 1.6562 mm, the fabricator's own
    # compressionThickness for the code. The dielectric constants are the impedance calculator's for this code
    # (7628 prepreg 4.4, 1.1 mm core 4.38); the impedance page prints one core figure, 4.6, which is what the older
    # multilayer rows above carry. Board P carries no impedance target, so no computed number depends on the core
    # figure. Inner copper 0.5 oz is the fabricator's default for this selector; 1 oz and 2 oz inner codes exist
    # (JLC041621-*, JLC041622-*) and choosing one is an engineering decision that has not been taken.
    # A four-layer board written with no name still gets the 1 oz four-layer row from write(), so board P's chain
    # has to name this row.
    "JLC04162H-7628": [("F.Cu", 0.070), ("pp", "FR4 prepreg 7628", 0.2104, 4.4), ("In1.Cu", 0.0152), ("core", "FR4 core", 1.065, 4.38), ("In2.Cu", 0.0152), ("pp", "FR4 prepreg 7628", 0.2104, 4.4), ("B.Cu", 0.070)],
    # AUTHORITY: OWNER RULING 25 September 2026, decision 43 (appendix 32.365; pcb_decisions.yaml n 43, authority
    # OWNER, ruled_on 2026-09-25): board B is regenerated and routed ONCE on eight layers on a rented box, as a
    # measurement. That run is EXPERIMENTAL, and this row is the stackup record the measurement needs. It
    # authorises no board B layout and no order: feasibility is not authorisation (owner condition 7 of
    # 25 September 2026), and the eight-layer price goes to the owner before any order. Added under that ruling
    # alone; no other row was changed with it (26 September 2026, MESHSAT-1357).
    # SOURCE: JLCPCB's JLC08161H-2116, the order form's default ("No requirement", the same layer table as the
    # code's own entry) at 8 layers, 1.6 mm, 1 oz outer, 0.5 oz inner, read 25 September 2026 from
    # cart.jlcpcb.com/quote with "Specify Stackup: Yes" (jlcpcb.com/impedance has no eight-layer section), and
    # transcribed in v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md. Layer sum 1.5996 mm, the fabricator's own
    # compressionThickness for the code. Dielectric constants from the impedance calculator for this code (2116
    # prepreg 4.16, 1080 prepreg 3.91, 0.3 mm core 4.41); the impedance page's single core figure is 4.6, and which
    # of the two the fabricator designs to is the open question to JLCPCB (adjudication A10; about 2 percent of a
    # stripline's impedance, INFERRED, not computed).
    # TWO PLIES, ONE DIELECTRIC: the fabricator lists two 1080 plies (0.0764 mm each, Dk 3.91) between L3 and L4 and
    # again between L5 and L6. KiCad holds one dielectric per copper gap (a second ply is a sublayer, which block()
    # does not write and stackup_read does not read), so each pair is written as one prepreg of 0.1528 mm at the
    # plies' common Dk: the same distance and the same constant impedance_check.geometry() takes between those
    # copper layers either way. tests/test_stackup_write.py holds each row to the transcription layer by layer.
    "JLC08161H-2116": [("F.Cu", 0.035), ("pp", "FR4 prepreg 2116", 0.1164, 4.16), ("In1.Cu", 0.0152), ("core", "FR4 core", 0.3, 4.41), ("In2.Cu", 0.0152),
                       ("pp", "FR4 prepreg 1080 x 2", 0.1528, 3.91), ("In3.Cu", 0.0152), ("core", "FR4 core", 0.3, 4.41), ("In4.Cu", 0.0152),
                       ("pp", "FR4 prepreg 1080 x 2", 0.1528, 3.91), ("In5.Cu", 0.0152), ("core", "FR4 core", 0.3, 4.41), ("In6.Cu", 0.0152),
                       ("pp", "FR4 prepreg 2116", 0.1164, 4.16), ("B.Cu", 0.035)],
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
