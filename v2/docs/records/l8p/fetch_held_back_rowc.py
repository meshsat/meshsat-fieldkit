#!/usr/bin/env python3
"""fetch_held_back_rowc.py: fetch the maker's sheet record l8p's round 10 (register row (c), L4A-66 and L4A-65; MESHSAT-1357, 7 October
2026) read but did not file
(round 11, 7 October 2026: TI's LM5066I sheet added, read for one comparison of L8P-BREAKER.md section 16).

The round reads R17's derating on ROHM's own sheet for the first time: GMR100 HJ series, Rev. GMR100J-IA-006E (5 March 2026), the
part GMR100HJAAFD5L00 that the parts stream's identity row names for board A's R17 (pcb_part_identities.yaml, DOCUMENT_OWED until
now). The sheet carries ROHM's copyright ("All rights reserved") and no grant to redistribute, so it is held back from the public
tree as the tree's other passives sheets are (v2/vendor/passives/held/, gitignored): this script downloads it into that folder,
checks the sha256 l8p_rowc.py pins, and refuses to keep a file that differs (ROHM may serve a later revision at the same address:
the refusal says so). The round's other held sheet, Nexperia's BUK6Y10-30P, is fetched by records/l4e11/fetch_held_back.py. It is
never run by a test.

Usage: fetch_held_back_rowc.py [--root DIR]   (default: this repository's root)"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [
    ("v2/vendor/passives/held/rohm-gmr100hj-rev006e-2026-03-05.pdf",
     "https://fscdn.rohm.com/en/products/databook/datasheet/passive/resistor/chip_resistor/gmr100-e.pdf",
     "3b5ac7258851583c154cc33c7ec7b8be4768702f633402ab72341c42ca525266"),
    # round 11 (L8P-R10-F1's approach (C), a controller with a tighter current-limit spread): TI's LM5066I, SNVS950C (July 2016),
    # read for its printed VCL row and its VIN range only; TI's sheets in this tree's held/ folder are kept back as the others are
    ("v2/vendor/ti/held/ti-lm5066i-snvs950c.pdf",
     "https://www.ti.com/lit/ds/symlink/lm5066i.pdf",
     "a759a5d04fe5b81577af575153fd528f0f03f147c892040eac6c51e400693628"),
]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args(argv)
    bad = 0
    for rel, url, want in DOCS:
        dest = os.path.join(a.root, rel)
        if os.path.isfile(dest) and hashlib.sha256(open(dest, "rb").read()).hexdigest() == want:
            print("held  %s" % rel)
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        got = hashlib.sha256(data).hexdigest()
        if got != want:
            print("REFUSED %s: sha256 %s, not the %s this record read (the maker may serve a later revision)" % (rel, got[:16], want[:16]))
            bad += 1
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").write(data)
        print("fetched %s" % rel)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
