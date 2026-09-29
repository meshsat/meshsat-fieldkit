#!/usr/bin/env python3
"""fetch_held_back.py: fetch the makers' documents stream s117 read but did not file (MESHSAT-1357, 29 September 2026).

TI's CSD17578Q5A (SLPS526, March 2015), CSD17577Q5A (SLPS516, August 2014), CSD17579Q5A (SLPS524) and CSD17581Q5A
(SLPS630) datasheets and Nexperia's PSMN4R0-30YLD (10 October 2013) are held back from the public tree under the owner's
rule of 27 September 2026: TI's IMPORTANT NOTICE grants use "only for development of an application that uses the TI
products described in the resource" and says "Other reproduction and display of these resources is prohibited", and
Nexperia's reads "All rights reserved" with no grant (v2/vendor/sources.txt, each line's publication note). This script
downloads each from the address recorded there into v2/vendor/ti/held/ or v2/vendor/nexperia/held/ (both ignored), checks the sha256 the stream read, and refuses to keep a file that
differs. It is never run by a test or a gate; efficiency.py does not read the files (it quotes their figures with pages).
Usage: fetch_held_back.py [--out DIR]   (default: v2/vendor/ti/held/ under this repository's root; the Nexperia file
lands in v2/vendor/nexperia/held/ beside it)"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [
    ("ti-csd17578q5a-slps526.pdf", "https://www.ti.com/lit/ds/symlink/csd17578q5a.pdf",
     "f1aad251830260a563a03e367f3db4c12112433fd8dde7b4ee179b22381b7834"),
    ("ti-csd17577q5a-slps516.pdf", "https://www.ti.com/lit/ds/symlink/csd17577q5a.pdf",
     "c8595fa806a99074f64592d5e36826f7b9c4b007b950344bc013316e7212348d"),
    ("ti-csd17579q5a-slps524.pdf", "https://www.ti.com/lit/ds/symlink/csd17579q5a.pdf",
     "05fea7ab5f6c3f1465c03d479dcd1ba6ea961f22bc043e36b0dcee0b0277055c"),
    ("ti-csd17581q5a-slps630.pdf", "https://www.ti.com/lit/ds/symlink/csd17581q5a.pdf",
     "99d50d881cedcc62d6629913c322968b6223b984fffbdfb4195521bd539123b6"),
    ("../../nexperia/held/nexperia-psmn4r0-30yld.pdf", "https://assets.nexperia.com/documents/data-sheet/PSMN4R0-30YLD.pdf",
     "ea964714683052c725692d58512b4f612d04f4aa00584be290180ed30823a704"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "v2", "vendor", "ti", "held"))
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
        dest = os.path.normpath(os.path.join(a.out, name))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        print("fetch_held_back: %s %d bytes, sha256 matches" % (name, len(data)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
