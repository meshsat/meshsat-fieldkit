#!/usr/bin/env python3
"""fetch_held_back.py: fetch the makers' documents task L4-E11 read but did not file (MESHSAT-1357, 2 October 2026).

Littelfuse's "MINI Series Blade Fuses - Rated 58V" (the 0997 series, revised 11/18/2025; the sheet L4-E9 fetched, provenance
copied in inputs/ia-littelfuse-997-mini58v-20251210045250.json) gives F1's time-current rows, derating table and cold
resistance. Murata's reference sheets for GRM3195C1H104GA05 and GRM3195C1H683JA05 (as of Jun.11,2026;
inputs/murata-reference-sheets-2026-10-02.json) give the timer capacitors' rated values, Table A and the endurance and damp
heat rows. The fix round (2 October 2026) adds three TI sheets: the TPS4811-Q1 (SLUSEE5E, the selected entry controller), the
CSD19536KTT (SLPS540C, its pass FET and Figure 4-10) and the TPS1663 (SLVSET9G, the rejected eFuse), held back by TI's
IMPORTANT NOTICE as stream s117 held its FET sheets. The dependency round (2 October 2026) adds Diodes Incorporated's B520C to
B560C sheet (DS13012 Rev. 18-2, the hold-up bank's diode). The consolidation round (2 October 2026) adds TI's BQ25730 (SLUSE65A,
February 2021, revised January 2024, 111 pages) and AOS's AONS21357 (Rev 2.1, November 2023, the first battery FET). The fix round (2 October 2026)
adds Vishay's SQJ403EP (document 67109, S15-2089 Rev. A, 31 August 2015) and Nexperia's BUK6Y10-30P (product data sheet of 17
April 2020, the selected battery FETs Q39 and Q40). The fix round for the review of the provisional fixes (2 October 2026) adds two
sheets read in the search for a P-channel part printing RDS(on) at a low gate drive hot (section 16a): Vishay's SQJ407EP (document
62806, S22-0224 Rev. B, 7 March 2022) and Nexperia's PXP9R1-30QL (product data sheet of 5 January 2021). The fans' feed round (3 October 2026, section 18) adds the mixers' 12 V rail
candidates: ADI's LTC3115-1 (Rev. E; analog.com refuses this host, so the archive's copy of the maker's file), TI's TPS55340
(SLVSBD4E) and TPS63070 (SLVSC58B). The specimens' round (3 October 2026, section 17d) adds TI's "Semiconductor and IC Package
Thermal Metrics" (TI serves SPRA953D, revised March 2024, at the SPRA953C address) and Nexperia's AN11158 (Rev. 7.0). Round 9 (4 October 2026,
section 19) adds Shenzhen Milliohm's (moolee) HoLLR2512 alloy shunt specification (Ho-A0, revised 2022-01-06), the fitted R19's maker sheet
(its power curve and the 5 s short-time overload), served by LCSC. All nineteen carry their makers' copyright and no grant to redistribute, so they
are held back from the public tree under the owner's rule of 27 September 2026: this script downloads each into an ignored
held/ folder, checks the sha256 l4e11_power.py pins, and refuses to keep a file that differs (Murata generates its sheets on
request, and TI serves the current revision, so a later fetch may differ: the refusal says so). It is never run by a test.
Usage: fetch_held_back.py [--root DIR] [--only TEXT]   (default: this repository's root, every document)"""
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
    ("v2/vendor/passives/held/murata-grm3195c1h104ga05-01a-2026-06-11.pdf",
     "https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM3195C1H104GA05-01A.pdf",
     "4457e5ec41c25d29a47f9201bd903f0f4abf98c7566d84a81aae7028e2d7a188"),
    ("v2/vendor/passives/held/murata-grm3195c1h683ja05-01a-2026-06-11.pdf",
     "https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM3195C1H683JA05-01A.pdf",
     "89cfedda1a8d61d5cf5371ab274a8c033e2bd9157d959ddd27d4e8963a934fde"),
    ("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "https://www.ti.com/lit/ds/symlink/tps4811-q1.pdf",
     "3cfe41fef1407b85abaaee1e27a95ac3cf2cb1bdf218209b8578a835c4c9497f"),
    ("v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf", "https://www.ti.com/lit/ds/symlink/csd19536ktt.pdf",
     "19e1a9660fac8577743f40acc2cdc791539afd5232bbc1fc350e15fec735d78d"),
    ("v2/vendor/ti/held/ti-tps1663-slvset9g.pdf", "https://www.ti.com/lit/ds/symlink/tps1663.pdf",
     "8f91a0db2daf2da35abd335420ff9f8b4ac9a99c93dac93e215e0a75e9a866fe"),
    ("v2/vendor/power/held/diodes-b520c-b560c-ds13012-rev18-2.pdf", "https://www.diodes.com/assets/Datasheets/ds13012.pdf",
     "1b1de94df0a7729f4a69a885edd54213594acdce3cd6d4fa072961431ddf71ff"),
    ("v2/vendor/ti/held/ti-bq25730-sluse65a.pdf", "https://www.ti.com/lit/ds/symlink/bq25730.pdf",
     "e41ef289ce1de377d7b92bce609177d924e149099d9c4424d88f6b21ad57153f"),
    ("v2/vendor/power/held/aos-aons21357-rev2.1-2023-11.pdf", "https://www.aosmd.com/res/datasheets/AONS21357.pdf",
     "1a6460e7c63596ca7d48fe1660ee3a3ee48c33d6e345ef41d7c94c21cd7642d9"),
    ("v2/vendor/power/held/vishay-sqj403ep-67109-reva.pdf", "https://www.vishay.com/docs/67109/sqj403ep.pdf",
     "6005efe139fc94e3e855c2beeef8fcaaa5dc71d3c4a6e82f8e8ce82c5506961c"),
    ("v2/vendor/nexperia/held/nexperia-buk6y10-30p-2020-04-17.pdf", "https://assets.nexperia.com/documents/data-sheet/BUK6Y10-30P.pdf",
     "ba928dfe6a85134423562bd378bdfafafb26d857ba08b50560ce5aacb956da40"),
    ("v2/vendor/power/held/vishay-sqj407ep-62806-revb.pdf", "https://www.vishay.com/docs/62806/sqj407ep.pdf",
     "1c1038b032b5bf378878473ba170cdbbd640ce1597fbb9c23be20adeaea663e8"),
    ("v2/vendor/nexperia/held/nexperia-pxp9r1-30ql.pdf", "https://assets.nexperia.com/documents/data-sheet/PXP9R1-30QL.pdf",
     "88a7b67bfcec9ba7dbf4619be60cfaa883f61b7c9a93a19affc3a5278d91513f"),
    ("v2/vendor/power/held/adi-ltc3115-1-rev-e.pdf",
     "http://web.archive.org/web/2026id_/https://www.analog.com/media/en/technical-documentation/data-sheets/LTC3115-1.pdf",
     "bbcd4991d9b86c100cf8da775a358740b3c524325d18251d56ec6e40a2014a03"),
    ("v2/vendor/ti/held/ti-tps55340-slvsbd4e.pdf", "https://www.ti.com/lit/ds/symlink/tps55340.pdf",
     "e579aa4fcb549eab29e889f7f6dcbd0fd88cac2647082c65f102e411c3f666ca"),
    ("v2/vendor/ti/held/ti-tps63070-slvsc58b.pdf", "https://www.ti.com/lit/ds/symlink/tps63070.pdf",
     "a88ef66f3493156ff6e7da0849de0e0e1068647f2553d08c1844d4a90c5c65ef"),
    ("v2/vendor/ti/held/ti-spra953c-thermal-metrics.pdf", "https://www.ti.com/lit/an/spra953c/spra953c.pdf",
     "8ab81b5a351132ae8ab049d984e7cc72f1eb3dd3e4d9d8e063be6fcd841080a9"),
    ("v2/vendor/nexperia/held/nexperia-an11158-rev7.pdf", "https://assets.nexperia.com/documents/application-note/AN11158.pdf",
     "9e3211549d0bcd774b265d0598588b3b221b13b9c528b7374445fd0f21d47aec"),
    ("v2/vendor/passives/held/moolee-hollr2512-ho-a0-2022-01-06.pdf",
     "https://datasheet.lcsc.com/datasheet/pdf/a6c04b348627a06d1c2e9d73fb46c6ff.pdf?productCode=C2985708",
     "5dac9ede82062791abe6128aa7cad87c1422993820fbd21efa33dbea2ce04005"),
    # record l8p's row (c) script (l8p_rowc.py): ROHM's GMR100 HJ sheet its PDFTEXT declares, also fetched by
    # l8p/fetch_held_back_rowc.py; listed here and not in l8p/fetch_held_back.py, whose digest l8p_drafts.out pins (the coordinator,
    # set 33's integration, 7 October 2026: the extraction helper's FETCH map reads this script's list)
    ("v2/vendor/passives/held/rohm-gmr100hj-rev006e-2026-03-05.pdf",
     "https://fscdn.rohm.com/en/products/databook/datasheet/passive/resistor/chip_resistor/gmr100-e.pdf",
     "3b5ac7258851583c154cc33c7ec7b8be4768702f633402ab72341c42ca525266"),
    # record l4e11's round FET (l4e11_fet.py): the text sheets its PDFTEXT declares, also fetched by fetch_held_back_fet.py (the
    # coordinator, set 33's integration, 7 October 2026: the extraction helper's FETCH map reads this script's list)
    ("v2/vendor/power/held/vishay-sqja37ep-75171-revb.pdf",
     "https://www.vishay.com/docs/75171/sqja37ep.pdf",
     "6a723edefaa97d2049c9746296b3d74eba826a2f6f5bdd1325892c2bd03f5668"),
    ("v2/vendor/power/held/vishay-sqjq131el-77936-reva.pdf",
     "https://www.vishay.com/docs/77936/sqjq131el.pdf",
     "d5dd14f0499cbfb3f6287b0d6adca930e7fb10cdc882e90a579afa74eeabbbeb"),
    ("v2/vendor/power/held/vishay-sqs407enw-76627-reva.pdf",
     "https://www.vishay.com/docs/76627/sqs407enw.pdf",
     "1970576e979a94559427babe70aac12d0817db1b43cfe6fda23f8ed3b91ef378"),
    ("v2/vendor/power/held/vishay-sqs415enw-77427-revc.pdf",
     "https://www.vishay.com/docs/77427/sqs415enw.pdf",
     "3d777ff9639c8c9efd8b4f2b98c0feb00289da487d20e4f5d4323dd4a797731b"),
    ("v2/vendor/power/held/vishay-sqs401en-65529-revd.pdf",
     "https://www.vishay.com/docs/65529/sqs401en.pdf",
     "385fae910ca444d9d219eeeebe52b11e94d5c3e66e303f1c432e6004c4fafa6f"),
    ("v2/vendor/power/held/infineon-ipd042p03l3-g-rev2.2-2014-05-16.pdf",
     "https://www.infineon.com/assets/row/public/documents/24/49/infineon-ipd042p03l3-g-datasheet-en.pdf",
     "8dbb10cfa21baa671bc6b86e8718bc2c40606504fca7d24e8a21ac11a8d414d1"),
    ("v2/vendor/power/held/infineon-bso301sp-h-rev1.32-2010-05-12.pdf",
     "https://www.infineon.com/assets/row/public/documents/24/49/infineon-bso301sp-h-datasheet-en.pdf",
     "f391eea4f0ea21cb1c2970fc544a1a5fdd7ea8b4fae35e3b2193c1a4f49044dc"),
    ("v2/vendor/power/held/infineon-bsz086p03ns3-g-rev2.4-2019-12-03.pdf",
     "https://www.infineon.com/assets/row/public/documents/24/49/infineon-bsz086p03ns3-g-datasheet-en.pdf",
     "1e67b3366caacf20bf990e5238cd3b7d963a1276d6f97b69f79a658513f2a6a2"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--only", default="", help="fetch only the documents whose path contains this text")
    a = ap.parse_args()
    bad = 0
    for rel, url, want in DOCS:
        if a.only and a.only not in rel:
            continue
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
