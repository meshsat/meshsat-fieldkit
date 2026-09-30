#!/usr/bin/env python3
"""fetch_held_back.py: fetch the battery makers' documents stream l3batt read but did not file (MESHSAT-1357, 30 September
2026). Held back from the public tree by their terms, a session decision under the owner's rule of 27 September 2026
(v2/vendor/sources.txt, each line's publication note): Samsung SDI's INR21700-50E cell specification reads "SAMSUNG SDI
Confidential Proprietary" on every page; Inspired Energy's NH2054HD34 specification states the information "should not,
in whole or in part, be reproduced"; LG's INR21700M50LT specification is a customer copy that "should only be used for
engineer study and pre-discussion". This script downloads each from the address recorded there into
v2/vendor/battery/held/ (ignored), checks the sha256 the stream read, and refuses to keep a file that differs.
Usage: fetch_held_back.py [--out DIR]   (default: v2/vendor/battery/held/ under this repository's root)"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [
    ("samsung-inr21700-50e-v1.0.pdf",
     "https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/INR21700_2D00_50E-Cell-Specification_5F00_V1.0_5F00_180711.pdf",
     "f2feac1fe964b66db438d42c42d1b3713137a0c5ddc13334d54a4b794a889ec3"),
    ("lg-inr21700-m50lt-2020-08-27.pdf",
     "https://www.dnkpower.com/wp-content/uploads/2022/07/LG-INR21700_M50LT_-CELL-SPECIFICATION.pdf",
     "1408ad2c1be0c92b168588224474e8d8ae5873395ac639ee7938d8d3efa9ea0b"),
    ("inspired-energy-nh2054hd34-v1.8.pdf",
     "https://inspired-energy.com/images/product_data_sheets/NH2054HD34_spec_v1.8.pdf",
     "5be4472514b5557bc529d0b258a8117bd4f930b7880c2ebbb04a62ced448b9b3"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "v2", "vendor", "battery", "held"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    bad = 0
    for name, url, want in DOCS:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        got = hashlib.sha256(data).hexdigest()
        if got != want:
            sys.stderr.write("fetch_held_back: %s differs from the pinned file (%s); not kept\n" % (name, got[:16]))
            bad += 1
            continue
        with open(os.path.join(a.out, name), "wb") as f:
            f.write(data)
        print("fetch_held_back: %s %d bytes, sha256 matches" % (name, len(data)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
