#!/usr/bin/env python3
"""fetch_held_back_fet.py: fetch the makers' sheets record l4e11's round FET read but did not file (task L4A-70, MESHSAT-1357,
7 October 2026).

The round searched P-channel MOSFET sheets that print a Ciss or QG(tot) maximum (l4e11_fet.py, page L4E11-ROUND-FET.md). Thirteen sheets
are new to the tree: five Vishay automotive sheets (SQJA37EP, SQJQ131EL, SQS407ENW, SQS415ENW, SQS401EN), fetched from vishay.com, and
eight Infineon sheets of its 2023 P-channel selection guide's -30 V row (BSC030P03NS3 G, BSC060P03NS3E G, BSC084P03NS3 G, BSZ086P03NS3 G,
BSZ120P03NS3 G, BSZ180P03NS3 G, IPD042P03L3 G, BSO301SP H), fetched from infineon.com's product pages. Each carries its maker's copyright and no grant to redistribute (Vishay's legal disclaimer,
document 91000; Infineon's important notice), so they are held back from the public tree as the tree's other Vishay and Infineon
sheets are (v2/vendor/power/held/, gitignored): this script downloads each into that folder, checks the sha256 l4e11_fet.py pins, and
refuses to keep a file that differs (a maker may serve a later revision at the same address: the refusal says so). The other held
sheets the round reads (TI SLUSE65A, Nexperia BUK6Y10-30P and PXP9R1-30QL, AOS AONS21357, Vishay SQJ403EP and SQJ407EP) are fetched by
fetch_held_back.py beside this script. It is never run by a test.

Usage: fetch_held_back_fet.py [--root DIR] [--only TEXT]   (default: this repository's root, every document)"""
import argparse
import hashlib
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
IFX = "https://www.infineon.com/assets/row/public/documents/24/49/"
DOCS = [
    ("v2/vendor/power/held/vishay-sqja37ep-75171-revb.pdf", "https://www.vishay.com/docs/75171/sqja37ep.pdf",
     "6a723edefaa97d2049c9746296b3d74eba826a2f6f5bdd1325892c2bd03f5668"),
    ("v2/vendor/power/held/vishay-sqjq131el-77936-reva.pdf", "https://www.vishay.com/docs/77936/sqjq131el.pdf",
     "d5dd14f0499cbfb3f6287b0d6adca930e7fb10cdc882e90a579afa74eeabbbeb"),
    ("v2/vendor/power/held/vishay-sqs407enw-76627-reva.pdf", "https://www.vishay.com/docs/76627/sqs407enw.pdf",
     "1970576e979a94559427babe70aac12d0817db1b43cfe6fda23f8ed3b91ef378"),
    ("v2/vendor/power/held/vishay-sqs415enw-77427-revc.pdf", "https://www.vishay.com/docs/77427/sqs415enw.pdf",
     "3d777ff9639c8c9efd8b4f2b98c0feb00289da487d20e4f5d4323dd4a797731b"),
    ("v2/vendor/power/held/vishay-sqs401en-65529-revd.pdf", "https://www.vishay.com/docs/65529/sqs401en.pdf",
     "385fae910ca444d9d219eeeebe52b11e94d5c3e66e303f1c432e6004c4fafa6f"),
    ("v2/vendor/power/held/infineon-ipd042p03l3-g-rev2.2-2014-05-16.pdf", IFX + "infineon-ipd042p03l3-g-datasheet-en.pdf",
     "8dbb10cfa21baa671bc6b86e8718bc2c40606504fca7d24e8a21ac11a8d414d1"),
    ("v2/vendor/power/held/infineon-bso301sp-h-rev1.32-2010-05-12.pdf", IFX + "infineon-bso301sp-h-datasheet-en.pdf",
     "f391eea4f0ea21cb1c2970fc544a1a5fdd7ea8b4fae35e3b2193c1a4f49044dc"),
    ("v2/vendor/power/held/infineon-bsc030p03ns3-g-rev2.1-2009-11-16.pdf", IFX + "infineon-bsc030p03ns3-g-datasheet-en.pdf",
     "a9786bf2b5f65b25742d95d5f4f5c4c76f758bf3f8f8e5b9076c9e97c6edda19"),
    ("v2/vendor/power/held/infineon-bsc060p03ns3e-g-rev2.1-2009-11-16.pdf", IFX + "infineon-bsc060p03ns3e-g-datasheet-en.pdf",
     "64c17f6d22bac04897fb583456f3b560cc7a65bd0c0d05af5beb23c9296e9112"),
    ("v2/vendor/power/held/infineon-bsc084p03ns3-g-rev2.1-2009-11-16.pdf", IFX + "infineon-bsc084p03ns3-g-datasheet-en.pdf",
     "78b0ee06750492feaac517b0a1b358d8898b9780025e5cda927b65c67bb40060"),
    ("v2/vendor/power/held/infineon-bsz086p03ns3-g-rev2.4-2019-12-03.pdf", IFX + "infineon-bsz086p03ns3-g-datasheet-en.pdf",
     "1e67b3366caacf20bf990e5238cd3b7d963a1276d6f97b69f79a658513f2a6a2"),
    ("v2/vendor/power/held/infineon-bsz120p03ns3-g-rev2.1-2009-11-16.pdf", IFX + "infineon-bsz120p03ns3-g-datasheet-en.pdf",
     "d6798434aec2a3771b568795bbf0ce29700d4033aee8196b3987326e17259015"),
    ("v2/vendor/power/held/infineon-bsz180p03ns3-g-rev2.1-2009-11-16.pdf", IFX + "infineon-bsz180p03ns3-g-datasheet-en.pdf",
     "c7882d545da9f2f1f114e34f61113e23946ce32014a03394189058eff9f41a25"),
]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--only", default="")
    a = ap.parse_args(argv)
    bad = 0
    for rel, url, want in DOCS:
        if a.only and a.only not in rel:
            continue
        dest = os.path.join(a.root, rel)
        if os.path.isfile(dest) and hashlib.sha256(open(dest, "rb").read()).hexdigest() == want:
            print("held  %s" % rel)
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        got = hashlib.sha256(data).hexdigest()
        if got != want:
            print("REFUSED %s: sha256 %s, not the %s this record read (the maker may serve a later revision)" % (rel, got[:16], want[:16]))
            bad += 1
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "wb").write(data)
        print("fetched %s" % rel)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
