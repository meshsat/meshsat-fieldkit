#!/usr/bin/env python3
"""fetch_held_back.py: fetch the makers' documents stream w5identc reads and does not file (MESHSAT-1357, 29 September 2026).

Uniroyal's thick film chip resistor specification (the maker's sheet, as LCSC's datasheet server hosts it) carries
"Uniroyal Electronics Global Co., Ltd. , all rights reserved" and grants no redistribution, so under the owner's rule of
27 September 2026 (third-party files: decide by each file's terms, conservatively; the precedent is stream s117's
Nexperia sheet) it is held back from the public tree: v2/vendor/passives/held/ is ignored, v2/vendor/sources.txt
records the address and the sha256, and this script downloads it there, checks that sha256, and refuses to keep a file
that differs. part_identities.py check reads it where it is fetched and reads UNREAD where it is not.
Usage: fetch_held_back.py [--out DIR]   (default: v2/vendor/passives/held/ under this repository's root)"""
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "v2", "ecad", "tools"))
from verdict import opt  # noqa: E402

DOCS = [
    ("uniroyal-series-11cd644d.pdf",
     "https://datasheet.lcsc.com/datasheet/pdf/0a975aaa49b7c97f38a963127be4a823.pdf?productCode=C25469",
     "11cd644d5d8a34a6d12775afb80bf58d8fc11f0c3b700dbd0f7a59942ceaa5ef"),
]


def main(argv):
    out = opt(argv, "--out") or os.path.join(ROOT, "v2", "vendor", "passives", "held")
    os.makedirs(out, exist_ok=True)
    bad = 0
    for name, url, want in DOCS:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        got = hashlib.sha256(data).hexdigest()
        if got != want:
            sys.stderr.write("fetch_held_back: %s differs from the pinned file (%s); not kept\n" % (name, got[:16]))
            bad += 1
            continue
        with open(os.path.join(out, name), "wb") as f:
            f.write(data)
        print("fetch_held_back: %s %d bytes, sha256 matches" % (name, len(data)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
