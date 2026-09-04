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
python3 - "$N" <<'PY'
import sys, csv, os, pcbnew
n = sys.argv[1]; b = pcbnew.LoadBoard(n + ".kicad_pcb"); bb = b.GetBoardEdgesBoundingBox(); ds = b.GetDesignSettings()
W, H, NL, T = bb.GetWidth() / 1e6, bb.GetHeight() / 1e6, b.GetCopperLayerCount(), ds.GetBoardThickness() / 1e6
title = b.GetTitleBlock().GetTitle() or n
top = bot = 0
if os.path.exists("out/jlc/%s-cpl.csv" % n):
    for r in csv.DictReader(open("out/jlc/%s-cpl.csv" % n)):
        if r.get("Layer", "").lower().startswith("t"): top += 1
        else: bot += 1
usb = any("USB_" in str(k) and str(k).endswith(("_P", "_N")) for k in b.GetNetInfo().NetsByName().keys())
stack = "JLC04161H-7628 stackup, " if NL == 4 else ""
asm = "none (bare board)" if top + bot == 0 else ("top %d" % top + (", bottom %d" % bot if bot else ""))
lines = ["MeshSat field-kit carrier %s Rev A - JLCPCB order notes (generated from the board file)" % title.replace("MeshSat Field Kit carrier - ", ""),
         "- Gerbers + drill: out/%s-gerbers.zip (KiCad 9, Protel extensions, Excellon mm)" % n,
         "- Board: %.0f x %.0f mm, %d layers, %.1f mm FR-4, %s1 oz outer copper, ENIG, matte black soldermask, white silkscreen" % (W, H, NL, T, stack)]
if usb: lines.append("- Impedance control: USB 2.0 differential pairs (nets USB_*_P/N) designed at 0.2 mm / 0.15 mm on the outer layers; ask JLC to tune for 90 ohm differential on the 7628 stackup")
lines += ["- Assembly: %s. BOM: %s-bom.csv, CPL: %s-cpl.csv" % (asm, n, n) if top + bot else "- Assembly: none, bare board",
          "- LCSC part numbers: verified codes filled by tools/lcsc_fill.py; lines without a code are bench-fitted parts (see ORDER-NOTES.txt in the order folder)",
          "- Not assembled by JLC: the bench-fit list of the order folder's ORDER-NOTES.txt and docs/ASSEMBLY.md section 9"]
open("out/jlc/README-fab.txt", "w").write("\n".join(lines) + "\n"); print("README-fab:", lines[2])
PY
ls -la out/jlc | awk '{print $5, $9}'
