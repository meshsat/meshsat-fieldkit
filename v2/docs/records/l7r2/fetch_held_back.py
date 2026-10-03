#!/usr/bin/env python3
"""fetch_held_back.py: fetch the makers' documents record l7r2 read and did not file (MESHSAT-1357, Layer 7 round 2, 3 October 2026).

Each carries its maker's copyright or reserved-rights notice, read conservatively (the owner's rule of 27 September 2026), so the tree
carries only their transcription (inputs/makers-drawings-r2-2026-10-03.md, each figure with its document's sha256). This script fetches
them into this record's held/ folder (to be ignored: the record's finding F-R2-11 drafts the .gitignore line), checks each sha256, and
refuses to keep a file that differs. It is never run by a test.
Usage: fetch_held_back.py [--root DIR]"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = [
    ("glenair-233-330.pdf", "https://www.glenair.com/superseal/superseal-rj45-cat-5e-6a-ip67-open-face-rated/pdf/233-330.pdf",
     "05280f3e6eff592b3ed9b450e24008ed8c06563a9ef797000a6458b14c0061d7"),
    ("bulgin-px0888.pdf", "https://web.archive.org/web/20230702120446id_/https://www.bulgin.com/pdf/pdf.php?sku=PX0888",
     "e190b66fe9fe17e24c7632581c80cf235cf2e7c6c0fe266a8c6ae3b3a7b461f2"),
    ("radiall-r125172001.pdf", "https://radiall-files.s3.amazonaws.com/tds/coaxialconnectors/R125172001%20R.pdf",
     "c94b970c9079cad54da38a7fd73439d197890cd8ddc453b054ec6c824f7a6cae"),
    ("jst-ring-r-type.pdf", "https://www.jst-mfg.com/product/pdf/eng/eRING1.pdf",
     "807b12bd15d35d9e931d23c10cc4e5c99c608ea4347d3870d9b6ce6852898d71"),
    ("jst-ph.pdf", "https://www.jst-mfg.com/product/pdf/eng/ePH.pdf",
     "447624f4f2f7d37c58c1eaa7ee314ad757fe7aff48f6186491ef6f69fbc00b96"),
    ("jst-sh.pdf", "https://www.jst-mfg.com/product/pdf/eng/eSH.pdf",
     "ea3071ca5ee5a6069eba534fa39a10f34c9fb742ee42135a69ab4156bfa0f5de"),
    ("amphenol-rjfield-catalog.pdf", "https://www.amphenolpcd.com/wp-content/uploads/2023/06/rj_field_catalog.pdf",
     "917b95d5bee65d6638612c458207e88cc0b13b712e47954900501d0715df6f71"),
]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default=os.path.join(HERE, "held")); a = ap.parse_args()
    os.makedirs(a.root, exist_ok=True); bad = 0
    for name, url, want in DOCS:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
        got = hashlib.sha256(data).hexdigest()
        if got != want:
            sys.stderr.write("fetch_held_back: %s differs from the transcribed file (%s); not kept\n" % (name, got[:16])); bad += 1; continue
        open(os.path.join(a.root, name), "wb").write(data)
        print("fetch_held_back: %s %d bytes, sha256 matches" % (name, len(data)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
