#!/usr/bin/env python3
"""Fetch the maker's sheet this record reads and may not file by its terms (Layer 8 record l8r2, MESHSAT-1357, 3 October 2026).

TI's TPS4811-Q1 data sheet (SLUSEE5E), the controller of item 2's series cut-off, is held back by TI's IMPORTANT NOTICE as record
l4e11 holds it (the same URL and sha256 as v2/docs/records/l4e11/fetch_held_back.py). It lands in v2/vendor/ti/held/, which
.gitignore excludes, and is checked by sha256; nothing here is committed but this script.

Usage (repository root):  python3 v2/docs/records/l8r2/fetch_held_back.py      exit 0: present and checked; 3: a mismatch."""
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
SHEETS = [
    ("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "https://www.ti.com/lit/ds/symlink/tps4811-q1.pdf",
     "3cfe41fef1407b85abaaee1e27a95ac3cf2cb1bdf218209b8578a835c4c9497f"),
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
