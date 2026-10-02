#!/usr/bin/env python3
"""fetch_held_back.py: fetch the maker's document task L4-E12 read but did not file (MESHSAT-1478 under MESHSAT-1357,
2 October 2026).

Texas Instruments' TLV755P data sheet (the sheet LCSC links for C404027, the TLV75533PDBVR on boards C, D and E) gives the
regulator's junction-to-ambient resistance in SOT-23-5 (DBV) and its absolute maximum junction temperature, which the
screen of l4e12_thermal.py reads. It is held back from the public tree by its IMPORTANT NOTICE, read conservatively (the
owner's rule of 27 September 2026), as the s117 record holds TI's FET sheets: this script downloads it from the address
grade-sources.yaml already records into the ignored v2/vendor/ti/held/ folder, checks the sha256 l4e12_thermal.py pins, and
refuses to keep a file that differs. It is never run by a test.
Usage: fetch_held_back.py [--root DIR]   (default: this repository's root)"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [
    ("v2/vendor/ti/held/ti-tlv755p-c404027.pdf",
     "https://datasheet.lcsc.com/datasheet/pdf/107eeb995f1c91f292b91a59221db472.pdf?productCode=C404027",
     "44ac688d7e51f85259134abcffeed6cd1ae61234dfd2b6dea2b0607d8ad0d015"),
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
        data = urllib.request.urlopen(req, timeout=60).read()
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
