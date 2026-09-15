#!/usr/bin/env python3
"""Cut the one-sheet schematic PDF along its A3 cell grid into a multi-page A3 PDF (MESHSAT-862, 15 September 2026).

Usage: sch_pages.py <schematic.kicad_sch> <sheet.pdf> <pages.pdf>
The sheet's paper size (`(paper "User" W H)`, written by schlayout.py as cols x 419.1 by rows x 297.18 mm) gives the grid; mutool
cuts the sheet into that many tiles; the tiles that carry ink (a page frame is ink, an empty cell has none) are kept in reading order.
A sheet that is not a grid (an A0 or a single cell) is copied as one page."""
import os, re, subprocess, sys, tempfile

CELL_W, CELL_H = 330 * 1.27, 234 * 1.27


def main():
    sch, sheet, out = sys.argv[1:4]
    m = re.search(r'\(paper "User" ([\d.]+) ([\d.]+)\)', open(sch).read())
    cols = rows = 1
    if m:
        W, H = float(m.group(1)), float(m.group(2))
        if abs(W / CELL_W - round(W / CELL_W)) < 0.01 and abs(H / CELL_H - round(H / CELL_H)) < 0.01: cols, rows = int(round(W / CELL_W)), int(round(H / CELL_H))
    if cols * rows == 1:
        subprocess.run(["cp", sheet, out], check=True); print("sch_pages: one page"); return
    tmp = tempfile.mkdtemp(prefix="schpages")
    tiles = os.path.join(tmp, "tiles.pdf")
    subprocess.run(["mutool", "poster", "-x", str(cols), "-y", str(rows), sheet, tiles], check=True)
    subprocess.run(["pdftoppm", "-r", "6", "-gray", "-png", tiles, os.path.join(tmp, "t")], check=True)
    keep = []
    pngs = sorted(f for f in os.listdir(tmp) if f.startswith("t") and f.endswith(".png"))
    from PIL import Image
    for i, f in enumerate(pngs):
        im = Image.open(os.path.join(tmp, f)).convert("L"); px = list(im.getdata()); ink = sum(1 for v in px if v < 200) / max(1, len(px))
        if ink > 0.0005: keep.append(i + 1)
    subprocess.run(["mutool", "merge", "-o", out, tiles, ",".join(str(k) for k in keep)], check=True)
    print("sch_pages: %d x %d cells, %d pages kept of %d tiles" % (cols, rows, len(keep), len(pngs)))


if __name__ == "__main__": main()
