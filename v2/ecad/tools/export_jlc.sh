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
        refs = []   # 8 Sep 2026 (MESHSAT-862): kicad-cli writes `J_ANT?` for a reference without a number and compresses runs to `C49-C57`; JLC's parser wants neither (the deliverable read-back caught both in the shipped D8 BOM)
        for x in r["Reference"].split(","):
            x = x.strip().rstrip("?")
            m = re.match(r"^([A-Za-z_]+)(\d+)-\1?(\d+)$", x)
            refs += ["%s%d" % (m.group(1), k) for k in range(int(m.group(2)), int(m.group(3)) + 1)] if m else [x]
        refs = [x for x in refs if x and not x.startswith(("H", "S_", "TP", "#"))]
        if not refs: continue
        w.writerow([r["Value"], ",".join(refs), r["Footprint"].split(":")[-1], r.get("LCSC", "")])
print("JLC BOM + CPL written to out/jlc/")
PY
python3 - "$N" <<'PY'
import sys, csv, os, re, json, pcbnew
n = sys.argv[1]; b = pcbnew.LoadBoard(n + ".kicad_pcb"); bb = b.GetBoardEdgesBoundingBox(); ds = b.GetDesignSettings()
W, H, NL, T = bb.GetWidth() / 1e6, bb.GetHeight() / 1e6, b.GetCopperLayerCount(), ds.GetBoardThickness() / 1e6
title = b.GetTitleBlock().GetTitle() or n
top = bot = 0
if os.path.exists("out/jlc/%s-cpl.csv" % n):
    for r in csv.DictReader(open("out/jlc/%s-cpl.csv" % n)):
        if r.get("Layer", "").lower().startswith("t"): top += 1
        else: bot += 1
# 15 September 2026: the impedance line was written for any board with USB_*_P/N nets and said "0.2 mm / 0.15 mm"
# and "90 ohm" as constants. C declares its USB class with NO target (the RP2040 is full speed, appendix 32.79) and
# D's pairs are 0.30/0.20 since 8 September, so the note asked the fab to tune a board that needs no tuning and named
# a geometry two boards do not carry. The target comes from the intent file and the geometry from the project's class.
usb = False; _zt = None; _w = _g = None
try:
    _it = json.load(open("out/%s-intent.json" % n)); _zt = (_it.get("pair_classes") or {}).get("USB", {}).get("z_diff")
except Exception: _zt = None
try:
    _pro = json.load(open(n + ".kicad_pro")); _cls = [c for c in _pro.get("net_settings", {}).get("classes", []) if c.get("name") == "USB"]
    if _cls: _w, _g = _cls[0].get("track_width"), _cls[0].get("diff_pair_gap")
except Exception: pass
usb = bool(_zt) and any("USB_" in str(k) and str(k).endswith(("_P", "_N")) for k in b.GetNetInfo().NetsByName().keys())
# 13 September 2026. These two claims were CONSTANTS and both were wrong on a board in the tree. The stackup
# was named only for a four-layer board, so A24 and B16, which are on JLC06161H-3313, went out asking the fab
# to "tune for 90 ohm differential on the 7628 stackup", a stack they are not built on; and the copper weight
# was the literal "1 oz", which owner ruling 7 of 12 September contradicts for P and E5, both of which carry
# 0.070 mm in their own stackup block. Read both off the board instead: the note is then a measurement of the
# file the fab receives, and it cannot drift from a stackup decision again. The stackup itself is untouched
# and stays the owner's.
_st = open(n + ".kicad_pcb", errors="replace").read()
_cu = re.search(r'\(layer "F\.Cu" \(type "copper"\) \(thickness ([0-9.]+)\)', _st)
# A board file with no stackup block says nothing about its copper, and claiming "1 oz" for it is the same
# constant this change removes. `full.sh` writes a stackup into every board it generates, so this fallback
# fires only on a folder cut before 8 September 2026 (C7 is the one in the tree), and it says so plainly.
_oz = "%g oz" % round(float(_cu.group(1)) / 0.035) if _cu else "copper weight NOT DECLARED in the board file (ask before quoting)"
_pp = re.findall(r'\(material "FR4 prepreg ([0-9]+)"', _st)   # file order: the FIRST is the outer prepreg, which is what names the stack
stack = ("JLC%02d161H-%s stackup, " % (NL, _pp[0]) if _pp else "") if _cu else ("JLC04161H-7628 stackup, " if NL == 4 else "")
asm = "none (bare board)" if top + bot == 0 else ("top %d" % top + (", bottom %d" % bot if bot else ""))
lines = ["MeshSat field-kit carrier %s Rev A - JLCPCB order notes (generated from the board file)" % title.replace("MeshSat Field Kit carrier - ", ""),
         "- Gerbers + drill: out/%s-gerbers.zip (KiCad 9, Protel extensions, Excellon mm)" % n,
         "- Board: %.0f x %.0f mm, %d layers, %.1f mm FR-4, %s%s outer copper, ENIG, matte black soldermask, white silkscreen" % (W, H, NL, T, stack, _oz)]
if usb: lines.append("- Impedance control: USB 2.0 differential pairs (nets USB_*_P/N) designed at %s mm / %s mm on the outer layers; ask JLC to tune for %.0f ohm differential on the %s" % (("%g" % _w) if _w else "the class", ("%g" % _g) if _g else "the class", _zt, (stack.replace(" stackup, ", " stackup") or "stackup this board is built on"))
lines += ["- Assembly: %s. BOM: %s-bom.csv, CPL: %s-cpl.csv" % (asm, n, n) if top + bot else "- Assembly: none, bare board",
          "- LCSC part numbers: verified codes filled by tools/lcsc_fill.py; lines without a code are bench-fitted parts (see ORDER-NOTES.txt in the order folder)",
          "- Not assembled by JLC: the bench-fit list of the order folder's ORDER-NOTES.txt and docs/ASSEMBLY.md section 9"]
open("out/jlc/README-fab.txt", "w").write("\n".join(lines) + "\n"); print("README-fab:", lines[2])
PY
ls -la out/jlc | awk '{print $5, $9}'
