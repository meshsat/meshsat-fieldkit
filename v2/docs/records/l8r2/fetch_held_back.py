#!/usr/bin/env python3
"""Fetch the maker's sheet this record reads and may not file by its terms (Layer 8 record l8r2, MESHSAT-1357, 3 October 2026).

TI's TPS4811-Q1 data sheet (SLUSEE5E), the controller of item 2's series cut-off, is held back by TI's IMPORTANT NOTICE as record
l4e11 holds it (the same URL and sha256 as v2/docs/records/l4e11/fetch_held_back.py). It lands in v2/vendor/ti/held/, which
.gitignore excludes, and is checked by sha256; nothing here is committed but this script.

Round 4 (3 October 2026, L9P-F02's focused check): four pages of Sanyo Denki's San Ace general catalogue C1152B001 '25.10, served
one page at a time by the maker's own catalogue viewer at publish.sanyodenki.com (the product page of 9WPA0412P6G001 links it):
p.362 the 9WPA type (the 100 % and 25 % PWM rows, "When control terminal is open, speed is the same as at 100% duty cycle", the
airflow and static pressure curves at 100, 50 and 25 % and the PWM duty to speed example), p.616 the motor protection (the locked
rotor current cut-off and restart), p.623 the PWM control (the input signal example, the duty to speed curve), p.633 the cautions
("current several times the rated current may flow" at power-on). No redistribution grant was readable (the maker's conditions of
use page answered HTTP 403 on 3 October 2026), so they are held back: they land in v2/vendor/fans/held/, which .gitignore excludes.

Usage (repository root):  python3 v2/docs/records/l8r2/fetch_held_back.py      exit 0: present and checked; 3: a mismatch."""
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
SHEETS = [
    ("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "https://www.ti.com/lit/ds/symlink/tps4811-q1.pdf",
     "3cfe41fef1407b85abaaee1e27a95ac3cf2cb1bdf218209b8578a835c4c9497f"),
    ("v2/vendor/fans/held/sanyo-denki-san-ace-c1152b001-2510-p0362.pdf", "https://publish.sanyodenki.com/library/books/San_Ace_E/book/pdf/0362.pdf",
     "7e5e2e7b1fe7e92fd0d1a63eb5e365fdca85be56559c7f6ee2353a10c4d072b9"),
    ("v2/vendor/fans/held/sanyo-denki-san-ace-c1152b001-2510-p0616.pdf", "https://publish.sanyodenki.com/library/books/San_Ace_E/book/pdf/0616.pdf",
     "5a7dbdd94339d81b574e4218bf2f73ae7deb1daf1883a46d9c4e24ffc34578ee"),
    ("v2/vendor/fans/held/sanyo-denki-san-ace-c1152b001-2510-p0623.pdf", "https://publish.sanyodenki.com/library/books/San_Ace_E/book/pdf/0623.pdf",
     "cd8112da11bc536f1054609d6afee0e43850d00cbfa657624ad49c29d0697c3f"),
    ("v2/vendor/fans/held/sanyo-denki-san-ace-c1152b001-2510-p0633.pdf", "https://publish.sanyodenki.com/library/books/San_Ace_E/book/pdf/0633.pdf",
     "17e067067bfe798f1ed6371c32df81c050bd5edaf82242b433a23e4d5ff989af"),
]


def main():
    bad = 0
    for rel, url, want in SHEETS:
        path = os.path.join(REPO, rel)
        if not os.path.isfile(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=90).read()
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
