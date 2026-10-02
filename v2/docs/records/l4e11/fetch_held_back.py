#!/usr/bin/env python3
"""fetch_held_back.py: fetch the makers' documents task L4-E11 read but did not file (MESHSAT-1357, 2 October 2026).

Littelfuse's "MINI Series Blade Fuses - Rated 58V" (the 0997 series, revised 11/18/2025; the sheet L4-E9 fetched, provenance
copied in inputs/ia-littelfuse-997-mini58v-20251210045250.json) gives F1's time-current rows, derating table and cold
resistance. Murata's reference sheets for GRM3195C1H104GA05 and GRM3195C1H683JA05 (as of Jun.11,2026;
inputs/murata-reference-sheets-2026-10-02.json) give the timer capacitors' rated values, Table A and the endurance and damp
heat rows. The fix round (2 October 2026) adds three TI sheets: the TPS4811-Q1 (SLUSEE5E, the selected entry controller), the
CSD19536KTT (SLPS540C, its pass FET and Figure 4-10) and the TPS1663 (SLVSET9G, the rejected eFuse), held back by TI's
IMPORTANT NOTICE as stream s117 held its FET sheets. All six carry their makers' copyright and no grant to redistribute, so they
are held back from the public tree under the owner's rule of 27 September 2026: this script downloads each into an ignored
held/ folder, checks the sha256 l4e11_power.py pins, and refuses to keep a file that differs (Murata generates its sheets on
request, and TI serves the current revision, so a later fetch may differ: the refusal says so). It is never run by a test.
Usage: fetch_held_back.py [--root DIR]   (default: this repository's root)"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [
    ("v2/vendor/power/held/littelfuse-997-mini58v-rev2025-11-18.pdf",
     "http://web.archive.org/web/20251210045250id_/https://www.littelfuse.com/assetdocs/littelfuse-datasheet-997-mini58v"
     "?assetguid=838CC4AD-F429-4185-A8E8-CCC70CD2B713",
     "437b1fd2c8cb3ef16107ec14d096b31ef3c3cb83893325234e880deb7540393e"),
    ("v2/vendor/passives/held/murata-grm3195c1h104ga05-01a-2026-06-11.pdf",
     "https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM3195C1H104GA05-01A.pdf",
     "4457e5ec41c25d29a47f9201bd903f0f4abf98c7566d84a81aae7028e2d7a188"),
    ("v2/vendor/passives/held/murata-grm3195c1h683ja05-01a-2026-06-11.pdf",
     "https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM3195C1H683JA05-01A.pdf",
     "89cfedda1a8d61d5cf5371ab274a8c033e2bd9157d959ddd27d4e8963a934fde"),
    ("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "https://www.ti.com/lit/ds/symlink/tps4811-q1.pdf",
     "3cfe41fef1407b85abaaee1e27a95ac3cf2cb1bdf218209b8578a835c4c9497f"),
    ("v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf", "https://www.ti.com/lit/ds/symlink/csd19536ktt.pdf",
     "19e1a9660fac8577743f40acc2cdc791539afd5232bbc1fc350e15fec735d78d"),
    ("v2/vendor/ti/held/ti-tps1663-slvset9g.pdf", "https://www.ti.com/lit/ds/symlink/tps1663.pdf",
     "8f91a0db2daf2da35abd335420ff9f8b4ac9a99c93dac93e215e0a75e9a866fe"),
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
