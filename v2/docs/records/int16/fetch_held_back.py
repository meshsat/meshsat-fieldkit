#!/usr/bin/env python3
"""fetch_held_back.py: fetch PANJIT's SS2020FL series sheet, held back from the public tree since integration set 15
(MESHSAT-1357, 29 September 2026). Its page 4 reads "Reproducing and modifying information of the document is prohibited
without permission"; under the owner's rule of 27 September 2026 the session decides by each file's terms, conservatively,
so the sheet is not published (v2/vendor/sources.txt, its line). This script downloads it from the maker's address into
v2/vendor/power/held/ (ignored), checks the sha256 recorded in v2/vendor/SOURCES.yaml, and refuses a file that differs.
It is never run by a test or a gate. Usage: fetch_held_back.py [--out DIR] (default v2/vendor/power/held/)."""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [("panjit-ss2020fl-series.pdf", "https://www.panjit.com.tw/upload/datasheet/SS2020FL_SERIES.pdf",
         "92544a833cdaa6e17d9192a05ec84bbc8ec797c4cb5fa51c4250f158f2c534fe")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "v2", "vendor", "power", "held"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    bad = 0
    for name, url, want in DOCS:
        dst = os.path.join(a.out, name)
        if os.path.exists(dst) and hashlib.sha256(open(dst, "rb").read()).hexdigest() == want:
            print("present  %s" % name); continue
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        got = hashlib.sha256(data).hexdigest()
        if got != want:
            print("REFUSED  %s: sha256 %s, the record pins %s" % (name, got[:16], want[:16])); bad += 1; continue
        open(dst, "wb").write(data)
        print("fetched  %s" % name)
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
