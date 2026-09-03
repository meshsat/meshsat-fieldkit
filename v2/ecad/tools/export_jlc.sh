#!/usr/bin/env bash
# Usage: export_jlc.sh <dir> <name> : JLCPCB assembly files (BOM + CPL) next to the Gerber zip, plus a fab README
set -euo pipefail
D="$1"; N="$2"; cd "$D"; mkdir -p out/jlc
kicad-cli pcb export pos --format csv --units mm --use-drill-file-origin --side both --smd-only -o out/jlc/pos-smd.csv "$N.kicad_pcb" >/dev/null
kicad-cli pcb export pos --format csv --units mm --use-drill-file-origin --side both -o out/jlc/pos-all.csv "$N.kicad_pcb" >/dev/null
python3 - "$N" <<'PY'
import csv, sys, re
N = sys.argv[1]
# CPL: KiCad pos csv -> JLC (Designator, Mid X, Mid Y, Layer, Rotation)
rows = list(csv.DictReader(open("out/jlc/pos-all.csv")))
with open("out/jlc/%s-cpl.csv" % N, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for r in rows:
        if r["Ref"].startswith(("H", "S_", "TP")): continue        # holes, slots, test points: nothing to place
        w.writerow([r["Ref"], "%smm" % r["PosX"], "%smm" % r["PosY"], "Top" if r["Side"] == "top" else "Bottom", r["Rot"]])
# BOM: schematic BOM csv (grouped) -> JLC (Comment, Designator, Footprint, LCSC Part #)
rows = list(csv.DictReader(open("out/%s-bom.csv" % N)))
with open("out/jlc/%s-bom.csv" % N, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
    for r in rows:
        refs = [x for x in r["Reference"].split(",") if not x.startswith(("H", "S_", "TP", "#"))]
        if not refs: continue
        w.writerow([r["Value"], ",".join(refs), r["Footprint"].split(":")[-1], r.get("LCSC", "")])
print("JLC BOM + CPL written to out/jlc/")
PY
cat > out/jlc/README-fab.txt <<'TXT'
MeshSat field-kit carrier PCB-B COMPUTE Rev A - JLCPCB order notes (generated)
- Gerbers + drill: out/pcb-b-compute-gerbers.zip (KiCad 9, Protel extensions, Excellon mm)
- Board: 245 x 170 mm, 4 layers, 1.6 mm FR-4, JLC04161H-7628 stackup, 1 oz outer copper, ENIG, matte black soldermask, white silkscreen
- Impedance control: USB 2.0 differential pairs (nets USB_*_P/N) designed at 0.2 mm / 0.15 mm on outer layers; ask JLC to tune for 90 ohm differential on the 7628 stackup
- Assembly: SMD + THT, top and bottom (J_AB1 is on the bottom). BOM: pcb-b-compute-bom.csv, CPL: pcb-b-compute-cpl.csv
- LCSC part numbers: only the certain ones are filled; the rest must be matched in the JLC parts library at order time
- Not assembled by JLC (fit at the bench): the COTS modules, the RockBLOCK bracket, cable ties, the display
TXT
ls -la out/jlc | awk '{print $5, $9}'
