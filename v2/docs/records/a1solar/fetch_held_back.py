#!/usr/bin/env python3
"""fetch_held_back.py: fetch the makers' documents this stream read but did not file (stream a1solar, MESHSAT-1357).

SunPower's datasheet 523809 Rev D (a distributor's re-branded issue with no terms) and its flexible modules' Safety and
Installation Instructions 524958 Rev F and Rev A (distributors' copies reading "All rights reserved") are held back from
the public tree under the owner's rule of 27 September 2026 (v2/vendor/sources.txt, each line's publication note). This
script downloads each from the address recorded there into v2/vendor/solar/held/ (ignored by .gitignore), checks the
sha256 the stream read, and refuses to keep a file that differs. It is never run by a test or a gate; array_calc.py does
not read the files (it quotes their figures) and only refuses one that is present but not the pinned file.
Usage: fetch_held_back.py [--out DIR]   (default: v2/vendor/solar/held/ under this repository's root)"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [
    ("sunpower-spr-e-flex-100-datasheet-523809-revd.pdf",
     "https://cdn.autosolar.es/pdf/fichas-tecnicas/SPR-E-Flex-100-SUNPOWER.pdf",
     "da06e5e2d9bca625f54a756105e009950a2352e4764868853cb26921372ff605"),
    ("sunpower-flex-safety-installation-524958-revf.pdf",
     "https://www.solarrun.com.au/wp-content/uploads/2021/06/mn-sunpower-flex-modules-safety-installation-guide-na.pdf",
     "b8ebdfb7019a399accd75e564a4a764eed565f7066dfd25b131fe65365ec6dd9"),
    ("sunpower-flex-safety-installation-524958-reva.pdf",
     "https://unboundsolar.sfo3.digitaloceanspaces.com/app/uploads/media/2019/12/08172255/"
     "sunpower-spr-e-flex-100-flexible-100-watt-module-solar-panel-installation-manual-1538113011.9433670.pdf",
     "74e09944eac53e737082957be82549a46e9e0ddbea42bb9931751335314b8369"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "v2", "vendor", "solar", "held"))
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
