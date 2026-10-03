#!/usr/bin/env python3
"""fetch_held_back.py: fetch the makers' documents the Layer 6 record l6pwr reads but does not file (MESHSAT-1357, 3 October 2026).

The Layer 4 records (L4-E7, L4-E10 and L4-E11) read these sheets and held them back from the public tree under the owner's rule of
27 September 2026 (TI's IMPORTANT NOTICE grants use only for development of an application using TI's products and prohibits other
reproduction; Nexperia's and Diodes' sheets read "All rights reserved" with no grant; Saft's forbids reproduction without its
authorization; Vishay's WSL revision of 23 November 2023 is LCSC's copy, held with the same caution as the L4-E7 record). This
record binds its identities to the SAME files by the SAME sha256 pins, so a reader who runs this script reads what the record read.
It downloads each into its ignored held/ folder, checks the sha256, and refuses to keep a file that differs (TI serves the current
revision, so a later fetch may differ: the refusal says so, and the record's page citations then belong to the pinned revision). It
is never run by a test. Usage: fetch_held_back.py [--root DIR] [--only SUBSTRING]   (default root: this repository's root)"""
import argparse
import hashlib
import os
import ssl
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [
    # the charger and its battery FETs (L4-E11 sections 14 to 16)
    ("v2/vendor/ti/held/ti-bq25730-sluse65a.pdf", "https://www.ti.com/lit/ds/symlink/bq25730.pdf",
     "e41ef289ce1de377d7b92bce609177d924e149099d9c4424d88f6b21ad57153f"),
    ("v2/vendor/nexperia/held/nexperia-buk6y10-30p-2020-04-17.pdf", "https://assets.nexperia.com/documents/data-sheet/BUK6Y10-30P.pdf",
     "ba928dfe6a85134423562bd378bdfafafb26d857ba08b50560ce5aacb956da40"),
    # the dock's VSYS eFuse and its output clamp (L4-E11 16e, 17a)
    ("v2/vendor/ti/held/ti-tps1663-slvset9g.pdf", "https://www.ti.com/lit/ds/symlink/tps1663.pdf",
     "8f91a0db2daf2da35abd335420ff9f8b4ac9a99c93dac93e215e0a75e9a866fe"),
    ("v2/vendor/power/held/diodes-b520c-b560c-ds13012-rev18-2.pdf", "https://www.diodes.com/assets/Datasheets/ds13012.pdf",
     "1b1de94df0a7729f4a69a885edd54213594acdce3cd6d4fa072961431ddf71ff"),
    # the vehicle entry's breaker and pass FET (L4-E11 3c), the same breaker as the solar guard's U21 (L4-E7)
    ("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "https://www.ti.com/lit/ds/symlink/tps4811-q1.pdf",
     "3cfe41fef1407b85abaaee1e27a95ac3cf2cb1bdf218209b8578a835c4c9497f"),
    ("v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf", "https://www.ti.com/lit/ds/symlink/csd19536ktt.pdf",
     "19e1a9660fac8577743f40acc2cdc791539afd5232bbc1fc350e15fec735d78d"),
    # the backstop's monitor and comparator (L4-E7R)
    ("v2/vendor/ti/held/ti-ina169-sbos181f.pdf", "https://www.ti.com/lit/ds/symlink/ina169.pdf",
     "dbb74b6cdc5431353f17b044b7d762df1f2f9049d03d2d1611a53058e570d62c"),
    ("v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf", "https://www.ti.com/lit/ds/symlink/tps3701.pdf",
     "27c94a6c3a243bf539e98942d26f0bd9ed979c5775c12cf86b7c1a8c3d7d9560"),
    # the sense bank's maker sheet at the revision L4-E7 read (the tree files an older revision of the same document)
    ("v2/vendor/passives/held/vishay-wsl-30100-2023-11-23.pdf",
     "https://datasheet.lcsc.com/datasheet/pdf/548f4c1b2301e9c8a8b168347d5344c1.pdf?productCode=C844695",
     "1b5c68910aa562a0dcce11ec572b4dd1febe63cfb90d20f3eaf5f9c7e01b59ac"),
    # the pack's labelled PROPOSAL (L4-E10 section 15); Saft's portal omits its intermediate certificate, the sha256 decides
    ("v2/vendor/battery/held/saft-mp176065xtd-31109-2-0625.pdf",
     "https://saft4u.saft.com/en/download_file/58d1fabc-9a46-4c07-8df1-0a00d3a1e7a9/English",
     "8ca0a3e09997a4a30567a4313cf83c2b6cf165543baf424e0ff788d5a8d27f8e"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    bad = 0
    for rel, url, want in DOCS:
        if a.only and a.only not in rel:
            continue
        path = os.path.join(a.root, rel)
        if os.path.exists(path) and hashlib.sha256(open(path, "rb").read()).hexdigest() == want:
            print("fetch_held_back: %s already present, sha256 matches" % rel)
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        ctx = ssl._create_unverified_context() if "saft4u.saft.com" in url else None
        try:
            data = urllib.request.urlopen(req, timeout=120, context=ctx).read()
        except Exception as e:
            sys.stderr.write("fetch_held_back: %s not fetched (%s)\n" % (rel, e))
            bad += 1
            continue
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
