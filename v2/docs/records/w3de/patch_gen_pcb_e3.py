#!/usr/bin/env python3
"""DRAFT for board E's layout owner (v2/ecad/tools/gen_pcb_e3.py): the placement knock-ons of w3de's schematic changes
(27 September 2026, MESHSAT-1357). gen_pcb_e3.py refuses a part it cannot place ("unplaced: ..."), so E's next
placement needs these before it runs; none of it changes the committed E layout, which predates the netlist anyway.

  1. S-47: the net class pattern ("TRK_LSENSE", "PWR") names a net that no longer exists; the new sense node TRK_CS
     carries the bottom switches' current to R5 and takes the power class in its place (the maker: "Minimize inductance
     from the sources of M2 and M3 to RSENSE by making the trace short and wide", 8705af p.36).
  2. S-47's smaller item: the two new controller capacitors C63 (GATEVCC, pin 15) and C64 (VIN, pin 34) join the TRKS
     region beside C19 and C20; their seats at the pins are DEC-001's (the bypass entries declare them).
  3. EQ-16: the two 12 AWG pads P_VR (VIN_RAW) and P_VN (GND) need FIXED positions under E5's two new wire holes. Those
     holes are placed by E5's owner against board A's J_VR and J_VN pins (layer 7), so this draft does NOT invent the
     coordinates: it leaves a marked line that stops the placement ("unplaced: P_VN, P_VR") until they are chosen.

Usage: patch_gen_pcb_e3.py <tree root holding v2/ecad>   (asserted old text)"""
import os, sys
p = os.path.join(sys.argv[1], "v2", "ecad", "tools", "gen_pcb_e3.py")
s = open(p, encoding="utf-8").read(); o = s
EDITS = [
    ('("TRK_SW*", "SW"), ("TRK_LSENSE", "PWR"), ("+5V_E6", "PWR")',
     '("TRK_SW*", "SW"), ("TRK_CS", "PWR"), ("+5V_E6", "PWR")'),
    ('''("TRKS",   (39.5, -95.5, 56, -80), ["C19", "C20", "C21",''',
     '''("TRKS",   (39.5, -95.5, 56, -80), ["C19", "C20", "C63", "C64", "C21",'''),
]
for old, new in EDITS:
    if s.count(old) != 1: raise SystemExit("patch_gen_pcb_e3: the old text is not there exactly once: %r" % old[:90])
    s = s.replace(old, new)
# 3. a marker for the two pads, deliberately without coordinates
marker = ("\n# EQ-16 (w3de, 27 September 2026): P_VR (VIN_RAW) and P_VN (GND), board E's 12 AWG pads to the dock block's VIN_RAW\n"
          "# power pins, are NOT in FIXED yet: their places follow E5's two new wire holes, which E5's owner lays against board\n"
          "# A's J_VR1-4 and J_VN1-4 (layer 7). Until they are added here the placement stops with 'unplaced: P_VN, P_VR'.\n")
anchor = "FIXED = {"
if s.count(anchor) != 1: raise SystemExit("patch_gen_pcb_e3: FIXED is not defined exactly once")
s = s.replace(anchor, marker.lstrip("\n") + anchor)
assert s != o
compile(s, p, "exec")
open(p, "w", encoding="utf-8").write(s); print("patch_gen_pcb_e3: %s edited, %d hunks and the P_VR/P_VN marker" % (p, len(EDITS)))
