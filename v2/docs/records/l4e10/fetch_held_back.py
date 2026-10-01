#!/usr/bin/env python3
"""fetch_held_back.py: fetch the four cell specifications task L4-E10 read but did not file (MESHSAT-1357, 2 October 2026).

Samsung SDI's INR18650-30Q specifications (Version No. V1.0 of the 30Q6 production code, date of application 2020/01/17, a
German distributor's copy; Version No. 1.0 of February 2015 and the customer draft V0.1 of 2024/01/23, both posted to TI's
E2E forum) carry "SAMSUNG SDI Confidential Proprietary" on every page; LG Chem's INR18650HG2 product specification
(BCY-PS-HG2-Rev0, 13 October 2014) is a distributor's copy with no grant to reproduce it. All four are held back from the
public tree by the conservative reading of their terms (the owner's rule of 27 September 2026), as the l3batt, a1solar and
l4e7 records do: this script downloads each from the address its line in v2/vendor/sources.txt records into the ignored
v2/vendor/battery/held/ folder, checks the sha256 l4e10_cell_thermal.py pins, and refuses to keep a file that differs.
It is never run by a test. Usage: fetch_held_back.py [--root DIR]   (default: this repository's root)"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [
    ("v2/vendor/battery/held/samsung-inr18650-30q6-v1.0-2020.pdf",
     "https://www.joke-technology.com/media/pdf/c4/9a/9b/datenblatt_inr18650-30q6_cell_specification.pdf",
     "652b3b98380428a112f147b830490e0da2aeec5b62eba04f1b6583ee963a61e1"),
    ("v2/vendor/battery/held/samsung-inr18650-30q-v1.0-2015.pdf",
     "https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/INR18650_2D00_30Q_5F00_datasheet.PDF",
     "a8f0918fb31e90b8f9a7c29acfb0854effc1ca3b3711d10d7fa972e211763464"),
    ("v2/vendor/battery/held/samsung-inr18650-30q6-draft-v0.1-2024.pdf",
     "https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/INR18650_2D00_30Q6_2D00_SAMSUNG-Cell-Specification_5F00_Darfon_5F00_Draft_5F00_240123.pdf",
     "931243bb08500750f2a20b72e985cc8896a465a375f383d9fe41d0d8429bd9c4"),
    ("v2/vendor/battery/held/lg-inr18650hg2-rev0-2014.pdf",
     "https://files.batteryjunction.com/frontend/files/lg/datasheet/LG-HG2-18650-INR-Datasheet.pdf",
     "b135f906d383a964ac7d4585d66acc762145aa739c20d7bfc60269d32d7857e9"),
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
