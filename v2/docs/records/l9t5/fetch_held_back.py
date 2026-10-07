#!/usr/bin/env python3
"""Fetch the makers' sheets record l9t5 reads for A1's detector survey and does not file (Layer 9, task T5 round 2, MESHSAT-1357,
4 October 2026).

Four RF power detector data sheets, held back from the public tree as the project holds its TI sheets (no redistribution grant was
read): ADI's ADL5902 (Rev. B), ADL5513 (Rev. B) and LTC5582 (Rev. D), which analog.com did not answer from the runner, so they are
taken from the Internet Archive's copies of the maker's own URLs (served gzip-compressed for two of them, decompressed here), and
TI's LMH2110 (SNWS022D) from ti.com. They land in v2/vendor/adi/held/ and v2/vendor/ti/held/, which .gitignore excludes, and are
checked by sha256; nothing here is committed but this script. l9t5_a1.py reads the printed rows from them and refuses without them.

Usage (repository root):  python3 v2/docs/records/l9t5/fetch_held_back.py      exit 0: present and checked; 3: a mismatch."""
import gzip
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
AR = "https://web.archive.org/web/%sid_/https://www.analog.com/media/en/technical-documentation/data-sheets/%s.pdf"
SHEETS = [
    ("v2/vendor/adi/held/adi-adl5902-revb.pdf", AR % ("20261001031856", "adl5902"),
     "f79f5a6b04e30e9eb2181f7cf85780cc896e6a9441279b2923068c050cea0545"),
    ("v2/vendor/adi/held/adi-adl5513-revb.pdf", AR % ("20260617032159", "adl5513"),
     "e51b849b75f81beda037e5895470c732cef42213e9fadba2a838a8d817866f19"),
    ("v2/vendor/adi/held/adi-ltc5582-revd.pdf", AR % ("20250806014757", "ltc5582"),
     "cf1382cf45de07bb995dbaeb2940d9af694f25e4482b4b41410c32f583fd1f78"),
    ("v2/vendor/ti/held/ti-lmh2110-snws022d.pdf", "https://www.ti.com/lit/ds/symlink/lmh2110.pdf",
     "b504ef25b74ca6f6a70badc4ce276a0d18cf7d5a098452357f235f1a85a7c6b2"),
]


def main():
    bad = 0
    for rel, url, want in SHEETS:
        path = os.path.join(REPO, rel)
        if not os.path.isfile(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=120).read()
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            tmp = path + ".part"
            open(tmp, "wb").write(data)
            os.replace(tmp, path)
        got = hashlib.sha256(open(path, "rb").read()).hexdigest()
        ok = got == want
        bad += not ok
        print("%s %s %s" % ("OK      " if ok else "MISMATCH", got[:16], rel))
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
