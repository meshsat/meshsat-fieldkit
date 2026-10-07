#!/usr/bin/env python3
"""Fetch the makers' sheets record l4canen reads for the latched supervisor's EN route (Layer 4 task L4A-54's correction, round 9 of
record l9t5's T10, W143, MESHSAT-1357, 7 October 2026).

Two Texas Instruments data sheets, held back from the public tree as the project holds its TI sheets (no redistribution grant was
read): the TPS2552/TPS2553/TPS2552-1/TPS2553-1 current-limited switch (SLVS841F, the limiter whose EN the route drives) and the TPS737
1 A LDO (SBVS067W, the regulator behind it). W138's record l4reg (fnd/l4reg 86dbcdff) fetches the same two sheets from the same URLs at
the same sha256; this script lists them again so that this record reads them from its own tree (the convention W138 and W135 follow).
They land in v2/vendor/ti/held/, which .gitignore excludes, and are checked by sha256; nothing here is committed but this script.
l4canen.py reads their held texts through v2/docs/records/_lib/pdftext.py (under v2/vendor/ti/held/pdftext/, taken by
v2/docs/records/_lib/retake_pdf_text.py) and refuses without them.

Usage (repository root):  python3 v2/docs/records/l4canen/fetch_held_back.py      exit 0: present and checked; 3: a mismatch."""
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
SHEETS = [
    ("v2/vendor/ti/held/ti-tps2553-slvs841f.pdf", "https://www.ti.com/lit/ds/symlink/tps2553.pdf",
     "88e453700cea2b263cdb5b44fce1e883e0f6d3b975457f879ac1423eeea42071"),
    ("v2/vendor/ti/held/ti-tps737-sbvs067w.pdf", "https://www.ti.com/lit/ds/symlink/tps737.pdf",
     "f706914950efed0b60423e9035b67c6dffbacd28091c452f24b7c0927bb3c851"),
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
