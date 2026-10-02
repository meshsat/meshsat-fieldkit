#!/usr/bin/env python3
"""fetch_held_back.py: fetch the cell specifications task L4-E10 read but did not file (MESHSAT-1357, 2 October 2026).

Samsung SDI's INR18650-30Q specifications (Version No. V1.0 of the 30Q6 production code, date of application 2020/01/17, a
German distributor's copy; Version No. 1.0 of February 2015 and the customer draft V0.1 of 2024/01/23, both posted to TI's
E2E forum) carry "SAMSUNG SDI Confidential Proprietary" on every page; LG Chem's INR18650HG2 product specification
(BCY-PS-HG2-Rev0, 13 October 2014) is a distributor's copy with no grant to reproduce it; Saft's LSH 20 sheets (Document
31015-2-0426 of April 2026 and the LSH 20 HTS sheet 31057-2-0710) carry "Photo credits: (c) Saft". Toshiba's SCiB brochure reads 'all rights reserved' and UltraXel's HL18650T flyer states no terms. Saft's MP 176065 xtd sheet forbids reproduction without Saft's authorization. All nine are held back from the
public tree by the conservative reading of their terms (the owner's rule of 27 September 2026), as the l3batt, a1solar and
l4e7 records do: this script downloads each from the address its line in v2/vendor/sources.txt records into the ignored
v2/vendor/battery/held/ folder, checks the sha256 l4e10_cell_thermal.py pins, and refuses to keep a file that differs.
It is never run by a test. Usage: fetch_held_back.py [--root DIR]   (default: this repository's root)"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DOCS = [
    ("v2/vendor/battery/held/samsung-inr18650-30q6-v1.0-2020.pdf",
     "https://www.joke-technology.com/media/pdf/c4/9a/9b/datenblatt_inr18650-30q6_cell_specification.pdf",
     "652b3b98380428a112f147b830490e0da2aeec5b62eba04f1b6583ee963a61e1"),
    ("v2/vendor/battery/held/samsung-inr18650-30q-v1.0-2015.pdf",
     "https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/INR18650_2D00_30Q_5F00_datasheet.PDF",
     "a8f0918fb31e90b8f9a7c29acfb0854effc1ca3b3711d10d7fa972e211763464"),
    ("v2/vendor/battery/held/samsung-inr18650-30q6-draft-v0.1-2024.pdf",
     "https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/INR18650_2D00_30Q6_2D00_SAMSUNG-Cell-Specification_5F00_Darfon_5F00_Draft_5F00_240123.pdf",
     "931243bb08500750f2a20b72e985cc8896a465a375f383d9fe41d0d8429bd9c4"),
    ("v2/vendor/battery/held/lg-inr18650hg2-rev0-2014.pdf",
     "https://files.batteryjunction.com/frontend/files/lg/datasheet/LG-HG2-18650-INR-Datasheet.pdf",
     "b135f906d383a964ac7d4585d66acc762145aa739c20d7bfc60269d32d7857e9"),
    # Saft's own portal serves these with an incomplete certificate chain (its DigiCert intermediate is not sent), so the fetch
    # skips the chain check and relies on the sha256 below; the LSH 20 HTS sheet was also byte-identical at a third-party mirror
    ("v2/vendor/battery/held/saft-lsh20-31015-2-0426.pdf",
     "https://saft4u.saft.com/en/download_file/8bdd6f76-c9c5-422e-95bd-a18e0a12d80f/English",
     "79245e64a2c4abb79ad082568ade32357d27f103416dbe899256dfec322e3ecd"),
    ("v2/vendor/battery/held/saft-lsh20hts-31057-2-0710.pdf",
     "https://saft4u.saft.com/en/download_file/eb00fd7f-30d7-4ad5-89e0-85f59f4f74d3/English",
     "5befce3a37ab89fad4826488793008f71d5c4ba4a36eacbfadd9dacfa5339d55"),
    # the cells read beyond the held set (the owner's instruction of 2 October 2026): Toshiba's SCiB brochure, UltraXel's HL18650T flyer
    ("v2/vendor/battery/held/toshiba-scib-brochure-2020.pdf",
     "https://www.global.toshiba/content/dam/toshiba/ww/outline/infrastructure/business-introduction/defense/pdf/BatterySCiB.pdf",
     "acc8f192c54fb287f9ef66d5e26c440601fa795c87f46dba881dce747ef07df3"),
    ("v2/vendor/battery/held/ultraxel-hl18650t-flyer-2025.pdf",
     "https://www.ultraxel.com/wp-content/uploads/2025/03/HL18650T-Ultraxel-Flyer-1.pdf",
     "f95db57fa9bef536a0abcab0a8a979db8593ebd528736c53590a35eb853f80c0"),
    # the consolidation of 2 October 2026: Saft's MP 176065 xtd datasheet from its own portal (the chain check skipped, the sha256 decides)
    ("v2/vendor/battery/held/saft-mp176065xtd-31109-2-0625.pdf",
     "https://saft4u.saft.com/en/download_file/58d1fabc-9a46-4c07-8df1-0a00d3a1e7a9/English",
     "8ca0a3e09997a4a30567a4313cf83c2b6cf165543baf424e0ff788d5a8d27f8e"),
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
        ctx = None
        if "saft4u.saft.com" in url:
            import ssl
            ctx = ssl._create_unverified_context()   # the server omits its intermediate certificate; the sha256 decides
        data = urllib.request.urlopen(req, timeout=60, context=ctx).read()
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
