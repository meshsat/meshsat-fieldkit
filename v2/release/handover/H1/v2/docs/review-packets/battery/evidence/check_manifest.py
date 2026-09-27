#!/usr/bin/env python3
"""The battery review packet's release check (review stream BAT, MESHSAT-1357, 26 September 2026).

REVIEW-REQUEST.md section 5: the packet is not sent until every file MANIFEST.md lists, the packet's own files and the
documents it cites, is present in the tree at the listed path with the listed sha256. Several cited documents are filed
under v2/vendor/ by another stream of the same review (stream PKT); this script is how the owner or the integrator proves
they arrived, byte for byte, at the commit that is sent.

Run from anywhere inside the working tree: python3 v2/docs/review-packets/battery/evidence/check_manifest.py
Exit 0 when every row is present and matches; 1 otherwise, with each missing or differing row named.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKT = os.path.dirname(HERE)


def root():
    d = HERE
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, "v2", "vendor")):
            return d
        d = os.path.dirname(d)
    sys.exit("no v2/vendor above %s" % HERE)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    top = root()
    text = open(os.path.join(PKT, "MANIFEST.md"), encoding="utf-8").read()
    sections = re.split(r"^## ", text, flags=re.M)
    rows = []
    for sec in sections:
        title = sec.split("\n", 1)[0].strip()
        if title.startswith("Files of this packet"):
            base = PKT
        elif title.startswith("Documents cited"):
            base = top
        else:
            continue
        for m in re.finditer(r"^\| `([^`]+)` \|.*`([0-9a-f]{64})` \|", sec, flags=re.M):
            rows.append((title, m.group(1), os.path.join(base, m.group(1)), m.group(2)))
    bad = []
    for title, rel, path, want in rows:
        if not os.path.exists(path):
            bad.append("MISSING  %s  (%s)" % (rel, title))
        elif sha(path) != want:
            bad.append("DIFFERS  %s  (%s): %s, manifest %s" % (rel, title, sha(path), want))
    print("checked %d rows of MANIFEST.md against %s" % (len(rows), top))
    for b in bad:
        print(b)
    print("RELEASE CHECK %s" % ("PASS" if not bad and rows else "FAIL"))
    return 0 if not bad and rows else 1


if __name__ == "__main__":
    sys.exit(main())
