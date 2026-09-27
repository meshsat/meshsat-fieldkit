#!/usr/bin/env python3
"""Draft for the owners of v2/vendor/sources.txt and v2/vendor/vendor-status.txt (stream w4dp, MESHSAT-1357, 27 September 2026).

WHY. w4dp files the maker's sheet of board D's D2 (LCSC C81598, SEMTECH ELECTRONICS LTD. 1N4148W, Rev 05, 20/09/2016) as
v2/vendor/power/st-semtech-1n4148w-c81598.pdf, the file LCSC serves for the code (sha256 54de8e40..., the same bytes
v2/docs/parts/grade-sources.yaml recorded at 2026-09-27T00:21:16Z). The folder `power` is already `current`, so the file
needs a provenance line in sources.txt and, as its neighbours have, a file line in vendor-status.txt; each goes after the
JSCJ 2N7002 line, the precedent for an LCSC-served maker's sheet in that folder. The PDF is AES-encrypted for copy
(print allowed); pdftotext reads it, as grade-sources.yaml's quote shows.

Usage: patch_vendor_index.py <tree root holding v2/>"""
import hashlib, os, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
V = os.path.join(ROOT, "v2", "vendor")
PDF = os.path.join(V, "power", "st-semtech-1n4148w-c81598.pdf")
if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != "54de8e4089bb8221cf6cf191ee3acc2bdb20c9933cf59e7b5de3ef4ee291ce3f":
    sys.exit("the filed sheet is not the one w4dp fetched")
EDITS = [
 (os.path.join(V, "sources.txt"),
  "power/jscj-2n7002-c8545.pdf   # https://datasheet.lcsc.com/datasheet/pdf/a141b8bd86b14475955ac8c4d3eea0a8.pdf?productCode=C8545 (LCSC's copy of the JSCJ sheet attached to the fitted code)\n",
  "power/st-semtech-1n4148w-c81598.pdf   # https://datasheet.lcsc.com/datasheet/pdf/8abd7fc00ebe41ffb03ad1383c10753b.pdf?productCode=C81598 (LCSC's copy of the SEMTECH ELECTRONICS LTD. 1N4148W sheet, Rev 05, 20/09/2016, attached to the fitted code; fetched 27 September 2026, sha256 54de8e40)\n"),
 (os.path.join(V, "vendor-status.txt"),
  "power/jscj-2n7002-c8545.pdf   current   # the JSCJ 2N7002 behind C8545, the logic N-FET on B, D and P\n",
  "power/st-semtech-1n4148w-c81598.pdf   current   # the SEMTECH ELECTRONICS 1N4148W behind C81598, board D's relay flyback D2\n"),
]
for path, anchor, line in EDITS:
    s = open(path, encoding="utf-8").read()
    if s.count(anchor) != 1: sys.exit("%s changed under this draft: its anchor is there %d times" % (path, s.count(anchor)))
    if line in s: sys.exit("%s already carries the line" % path)
    open(path, "w", encoding="utf-8").write(s.replace(anchor, anchor + line, 1))
    print("patched", path)
