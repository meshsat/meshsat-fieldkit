#!/usr/bin/env python3
"""Fetch the maker's sheet record l9t5's HO-E comparison (l9t5_hoe.py, Layer 4 task L4A-59) reads and does not file (MESHSAT-1357, W148,
7 October 2026).

TI's TPS3703 (SBVS249B, revised November 2020), the reset-loop hold stage l9t5_hoe.py compares and selects (SESSION W148-1), held back
from the public tree as the project holds its other TI sheets (no redistribution grant was read), fetched from ti.com. It lands in
v2/vendor/ti/held/, which .gitignore excludes, and is checked by sha256; nothing here is committed but this script. Then its text is
taken by v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l9t5 (l9t5_hoe.py declares the extraction).

WHY A FOLDER OF ITS OWN (SESSION W148-4, under the owner's standing rule of 26 September 2026): record l9t5's own fetch_held_back.py is
pinned by sha256 in l9t5_a1.py and l9t5_f01.py, whose outputs other records and pages pin; an entry there would move them all. This
folder holds only this script, so pdftext.FETCH names it for the TPS3703. To reverse: move the entry into l9t5's script in a set whose
dependency pass re-pins l9t5_a1.out and its dependants.

Usage (repository root):  python3 v2/docs/records/l9t5hoe/fetch_held_back.py      exit 0: present and checked; 3: a mismatch."""
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
SHEETS = [
    ("v2/vendor/ti/held/ti-tps3703-sbvs249b.pdf", "https://www.ti.com/lit/ds/symlink/tps3703.pdf",
     "cc65714774e50c97dca9a1bf094489b17350cc70fa16068880e108e320f8a6ea"),
]


def main():
    bad = 0
    for rel, url, want in SHEETS:
        path = os.path.join(REPO, rel)
        if not os.path.isfile(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=120).read()
            tmp = path + ".part"
            open(tmp, "wb").write(data)
            os.replace(tmp, path)
        got = hashlib.sha256(open(path, "rb").read()).hexdigest()
        ok = got == want
        bad += not ok
        print("%s %s %s" % ("OK      " if ok else "MISMATCH", got[:16], rel))
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
