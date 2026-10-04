#!/usr/bin/env python3
"""Fetch the maker's sheet this record reads and does not file (Layer 8 record l8p, MESHSAT-1357, 4 October 2026).

TI's OPA187 data sheet (SBOS807E), the amplifier record l8p draws as C-1c's comparator (U102), is held back by TI's IMPORTANT
NOTICE as records l4e11 and l8r2 hold their TI sheets. It lands in v2/vendor/ti/held/, which .gitignore excludes, and is checked
by sha256; nothing here is committed but this script. l8p_drafts.py reads the offset over temperature from it and refuses
without it.

Usage (repository root):  python3 v2/docs/records/l8p/fetch_held_back.py      exit 0: present and checked; 3: a mismatch."""
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
SHEETS = [
    ("v2/vendor/ti/held/ti-opa187-sbos807e.pdf", "https://www.ti.com/lit/ds/symlink/opa187.pdf",
     "62bd7b52851715978aa52511ad946b1d725850b4d2e8672a901627ed65585c32"),
]


def main():
    bad = 0
    for rel, url, want in SHEETS:
        path = os.path.join(REPO, rel)
        if not os.path.isfile(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=90).read()
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
