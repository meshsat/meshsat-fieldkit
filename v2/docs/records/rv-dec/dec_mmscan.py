#!/usr/bin/env python3
"""Decision 42: scan every PDF under v2/vendor/ for a millimetre or mil placement figure next to a capacitor clause.
A hit = a window of three consecutive text lines of one page that mentions capacitor/decoupl/bypass AND carries
'<number> mm' or '<number> mil' AND a placement word (within, close, place, from, distance, away). Prints file, page,
the window. It is a SCREEN for the reader: every hit is then read in its page; a miss is not proof of absence in a
figure drawn as an image. Usage: dec_mmscan.py <vendor dir>"""
import os, re, subprocess, sys
CAP = re.compile(r"capacit|decoupl|bypass", re.I)
NUM = re.compile(r"\b\d+(\.\d+)?\s?(mm|mils?)\b", re.I)
PLACE = re.compile(r"within|close|place|distance|away|from the", re.I)
root = sys.argv[1]; nfiles = 0; hits = 0
for dp, _, fs in os.walk(root):
    for f in sorted(fs):
        if not f.lower().endswith(".pdf"): continue
        p = os.path.join(dp, f); nfiles += 1
        try:
            txt = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True, timeout=120).stdout
        except Exception as e:
            print("UNREADABLE", p, e); continue
        for pg, page in enumerate(txt.split("\f"), 1):
            L = page.splitlines()
            for i in range(len(L)):
                w = " ".join(x.strip() for x in L[i:i + 3])
                if CAP.search(w) and NUM.search(L[i]) and PLACE.search(w):
                    hits += 1; print("%s p.%d: %s" % (os.path.relpath(p, root), pg, re.sub(r"\s+", " ", w)[:260]))
print("files scanned:", nfiles, "hits:", hits, file=sys.stderr)
