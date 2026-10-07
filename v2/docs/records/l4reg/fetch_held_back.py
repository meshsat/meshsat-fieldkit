#!/usr/bin/env python3
"""Fetch the makers' sheets record l4reg reads for the supervisors' regulator stage (Layer 4 task L4A-56, re-scoped by W135's
CHANGE-METHOD; RE-6 and RE-7; MESHSAT-1357, 7 October 2026).

Four Texas Instruments data sheets, held back from the public tree as the project holds its TI sheets (no redistribution grant was
read): the TPS737 1 A LDO (SBVS067W, the selected regulator, TPS73733DCQRM3), the TLV757P 1 A LDO (SBVS322C, screened and not taken)
and the TPS7A37 1 A LDO (SBVS220B, the adjustable alternate), fetched by W138 on 7 October 2026 with a plain GET from the maker's own
URL; and the TPS2552/TPS2553/TPS2552-1/TPS2553-1 current-limited switch (SLVS841F), the limiter record l4lim selected (W135's
fetch on fnd/l4lim aa6704b2 lists the same sheet at the same sha256; this script lists it again so that this record reads it from
its own tree). They land in v2/vendor/ti/held/, which .gitignore excludes, and are checked by sha256; nothing here is committed but
this script. l4reg_compare.py reads their committed-elsewhere texts through v2/docs/records/_lib/pdftext.py (the held texts under
v2/vendor/ti/held/pdftext/, taken by v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l4reg) and refuses without them.

Usage (repository root):  python3 v2/docs/records/l4reg/fetch_held_back.py      exit 0: present and checked; 3: a mismatch."""
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
SHEETS = [
    ("v2/vendor/ti/held/ti-tps737-sbvs067w.pdf", "https://www.ti.com/lit/ds/symlink/tps737.pdf",
     "f706914950efed0b60423e9035b67c6dffbacd28091c452f24b7c0927bb3c851"),
    ("v2/vendor/ti/held/ti-tlv757p-sbvs322c.pdf", "https://www.ti.com/lit/ds/symlink/tlv757p.pdf",
     "9f5e9602ed9366124dfee01dd773ceafca6b54c5c22cf3a7999453432c5cefb9"),
    ("v2/vendor/ti/held/ti-tps7a37-sbvs220b.pdf", "https://www.ti.com/lit/ds/symlink/tps7a37.pdf",
     "e475d7120b96865b8647bb2d206e7e5565b62810e9fd728746188e08fa330012"),
    ("v2/vendor/ti/held/ti-tps2553-slvs841f.pdf", "https://www.ti.com/lit/ds/symlink/tps2553.pdf",
     "88e453700cea2b263cdb5b44fce1e883e0f6d3b975457f879ac1423eeea42071"),
]


def main():
    bad = 0
    for rel, url, want in SHEETS:
        path = os.path.join(REPO, rel)
        if not os.path.isfile(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=120).read()
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
