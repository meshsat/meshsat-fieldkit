#!/usr/bin/env python3
"""fetch_held_back.py: fetch the maker's document record l9stk read but did not file (MESHSAT-1357, 4 October 2026).

TI's application report SLVA673A, "Robust Hot Swap Design" (November 2014, revised; 10 pages), the calculation basis of the
protection design in L9-STACKUPS.md section 15 (the owner's instruction of 4 October 2026). It carries TI's IMPORTANT NOTICE and
no grant to redistribute, so it is held back from the public tree under the owner's rule of 27 September 2026: this script
downloads it into the ignored v2/vendor/ti/held/ folder, checks the sha256 l9stk_protection.py pins, and refuses to keep a file
that differs (TI serves the current revision, so a later fetch may differ: the refusal says so). It is never run by a test.
Usage: fetch_held_back.py [--root DIR]   (default: this repository's root)"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [
    ("v2/vendor/ti/held/ti-slva673a.pdf", "https://www.ti.com/lit/an/slva673a/slva673a.pdf",
     "ea1604c5c8ed02acd29a412e7d235e7b9330a61b134809fcfaa1c43bbe78676b"),
]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args(argv)
    bad = 0
    for rel, url, want in DOCS:
        dest = os.path.join(a.root, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.isfile(dest) and hashlib.sha256(open(dest, "rb").read()).hexdigest() == want:
            print("held, unchanged: %s" % rel)
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        got = hashlib.sha256(data).hexdigest()
        if got != want:
            print("REFUSED: %s fetched with sha256 %s, not the pinned %s (the maker may serve a newer revision)" % (rel, got, want))
            bad += 1
            continue
        open(dest, "wb").write(data)
        print("fetched: %s" % rel)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
