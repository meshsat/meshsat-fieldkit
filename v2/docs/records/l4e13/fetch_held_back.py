#!/usr/bin/env python3
"""fetch_held_back.py: fetch the maker's document task L4-E13 read but did not file (MESHSAT-1357, 2 October 2026).

Solbian's SOLBIANFLEX SX series datasheet (English, created 7 February 2023, the maker's own site) gives the SX 156's
electrical rows, its nominal operating cell temperature and its temperature coefficients. It states no terms and grants no
redistribution, so it is held back from the public tree under the owner's rule of 27 September 2026 and the task's rule
(held back unless redistribution is clearly allowed), as the a1solar, l4e7 and l4e9 records hold theirs: this script
downloads it into the ignored v2/vendor/solar/held/ folder, checks the sha256 l4e13_panel.py pins, and refuses to keep a
file that differs. SunPower's two documents the record also reads are fetched by v2/docs/records/a1solar/fetch_held_back.py.
It is never run by a test.
Usage: fetch_held_back.py [--root DIR]   (default: this repository's root)"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [
    ("v2/vendor/solar/held/solbian-sx-series-datasheet-eng-2023-02.pdf",
     "https://www.solbian.eu/img/cms/PDF/ENG_SX_datasheet.pdf",
     "da89757253556a9d807c6e0c6848f079fbd1d81c1f6422bd211cab7e33e1c12c"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args()
    bad = 0
    for rel, url, want in DOCS:
        path = os.path.join(a.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=90).read()
        got = hashlib.sha256(data).hexdigest()
        if got != want:
            sys.stderr.write("fetch_held_back: %s differs from the pinned file (%s); not kept\n" % (rel, got[:16]))
            bad += 1
            continue
        with open(path, "wb") as f:
            f.write(data)
        print("fetch_held_back: %s %d bytes, sha256 matches" % (rel, len(data)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
