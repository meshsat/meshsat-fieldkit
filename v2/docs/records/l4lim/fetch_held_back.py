#!/usr/bin/env python3
"""Fetch the makers' sheets record l4lim reads for the limiter window screen (Layer 4 task L4A-101, MESHSAT-1357, 7 October 2026).

Three current-limited switch data sheets, held back from the public tree as the project holds its TI sheets (no redistribution
grant was read; Diodes' IMPORTANT NOTICE item 8 reads "Any unauthorized copying, modification, distribution ... is prohibited"):
TI's TPS2552/TPS2553/TPS2552-1/TPS2553-1 (SLVS841F) and TPS25200 (SLVSCJ0F) from ti.com, and Diodes' AP22652/AP22653/AP22652A/
AP22653A (DS41186 Rev. 5 - 2) from diodes.com, each the maker's own URL, fetched on 7 October 2026 with a plain GET. They land in
v2/vendor/ti/held/ and v2/vendor/diodes/held/, which .gitignore excludes, and are checked by sha256; nothing here is committed but
this script. l4lim_screen.py reads the printed rows from them and refuses without them. The fourth sheet the screen reads, TI's
TPS2596 (SLVSET8A), is already in the tree at v2/vendor/power/tps2596.pdf (byte-identical to ti.com's download of 7 October 2026).

Not fetched: ADI's MAX4995A (analog.com refused this host and the Internet Archive answered "Temporarily Offline" on 7 October
2026 at about 05:00 CEST); the screen claims nothing from it.

Usage (repository root):  python3 v2/docs/records/l4lim/fetch_held_back.py      exit 0: present and checked; 3: a mismatch."""
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
SHEETS = [
    ("v2/vendor/ti/held/ti-tps2553-slvs841f.pdf", "https://www.ti.com/lit/ds/symlink/tps2553.pdf",
     "88e453700cea2b263cdb5b44fce1e883e0f6d3b975457f879ac1423eeea42071"),
    ("v2/vendor/ti/held/ti-tps25200-slvscj0f.pdf", "https://www.ti.com/lit/ds/symlink/tps25200.pdf",
     "fafdb867c456a2b24ef4fe5908e7d6da75703c0f24a36f984864d1d2daf9cd4a"),
    ("v2/vendor/diodes/held/diodes-ap22652-53-ds41186.pdf", "https://www.diodes.com/assets/Datasheets/AP22652_53.pdf",
     "972b6c1b8673f7a154e721162c5f1c5bf5d562e6f369341bf73c53565e017b40"),
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
