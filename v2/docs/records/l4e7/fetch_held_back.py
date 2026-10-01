#!/usr/bin/env python3
"""fetch_held_back.py: fetch the five makers' documents task L4-E7 read but did not file (MESHSAT-1357, 1 October 2026).

YAGEO's RT series product specification V.16 (May 06, 2025; the sheet LCSC links for C861244, C861068, C861589 and
C136968) gives the tolerance and TCR codes of RIMON_IN, R8 and R9. Infineon's BSC028N06NS data sheet Rev.2.1
(2013-01-18; LCSC's link for C148250) gives Q3's and Q5's gate charge for U5's junction estimate. Vishay Dale's WSL
sheet (Document Number 30100, Revision 23-Nov-2023; LCSC's link for C844695) is the RSENSE1 alternative the
qualification evaluates. TI's INA250 (SBOS511C, September 2023) and TPS3701 (SBVS240C, February 2019) are the control
decision's backstop. All five are held back from the public tree by the conservative reading of their terms (the owner's
rule of 27 September 2026), as the a1solar, s117 and w5identc records do: this script downloads each from the address
its catalogue reading in inputs/ records (TI's two from ti.com) into an ignored held/ folder, checks the sha256
l4e7_stage_settings.py pins, and refuses to keep a file that differs. It is never run by a test.
Usage: fetch_held_back.py [--root DIR]   (default: this repository's root)"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [
    ("v2/vendor/passives/held/yageo-rt-series-v16-2025-05-06.pdf",
     "https://datasheet.lcsc.com/datasheet/pdf/46d7760c582640714d605308a25a220a.pdf?productCode=C136968",
     "0a729d144519a7021c82a0ef242b064e467c70d44afcf9eabd6c7ffdc4b673a3"),
    ("v2/vendor/power/held/infineon-bsc028n06ns-rev2.1-c148250.pdf",
     "https://datasheet.lcsc.com/datasheet/pdf/0ee6668d612fe4d6661ddc31bcb9aa36.pdf?productCode=C148250",
     "2959653166e981f9de24cd9c141c44490ecc62acba5971ec8c0b263eca9708e0"),
    ("v2/vendor/passives/held/vishay-wsl-30100-2023-11-23.pdf",
     "https://datasheet.lcsc.com/datasheet/pdf/548f4c1b2301e9c8a8b168347d5344c1.pdf?productCode=C844695",
     "1b5c68910aa562a0dcce11ec572b4dd1febe63cfb90d20f3eaf5f9c7e01b59ac"),
    ("v2/vendor/ti/held/ti-ina250-sbos511c.pdf", "https://www.ti.com/lit/ds/symlink/ina250.pdf",
     "4690d49c0e10739b6dfc1da4d56bc2eeda8276d9b8816fb7b90db539c1eb0868"),
    ("v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf", "https://www.ti.com/lit/ds/symlink/tps3701.pdf",
     "27c94a6c3a243bf539e98942d26f0bd9ed979c5775c12cf86b7c1a8c3d7d9560"),
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
