#!/usr/bin/env python3
"""fetch_held_back.py: fetch the maker's document task L4-E9 read but did not file (MESHSAT-1357, 2 October 2026).

Littelfuse's datasheet "MINI Series Blade Fuses - Rated 58V" (the 0997 series, revised 11/18/2025) gives F1's DC voltage
rating, interrupting rating, time-current rows and derating table. It carries the maker's copyright and a disclaimer and no
grant to redistribute, so it is held back from the public tree under the owner's rule of 27 September 2026, as the a1solar,
s117, w5identc and l4e7 records hold theirs: this script downloads it from the Internet Archive's snapshot of the maker's own
address (the maker's site refuses this runner; inputs/ia-littelfuse-997-mini58v-20251210045250.json) into the ignored
v2/vendor/power/held/ folder, checks the sha256 l4e9_power_path.py pins, and refuses to keep a file that differs. It is
never run by a test.
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
