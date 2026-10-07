#!/usr/bin/env python3
"""l4e11_fet.py: record l4e11, ROUND FET (Layer 4 AI-scope register tasks L4A-70 and L4A-71; MESHSAT-1357, 7 October 2026).

L4A-70 (HO-L, E11-37): search the makers' sheets for a battery-FET set whose gate load is under TI's 5 nF on PRINTED maxima (Ciss or
QG(tot)) and that meets E-1's 40.78 K/W bar at the breaker's held 23.93 A; if none does, (i)(a) stays CONDITIONAL on E-05 and the fallback
(ii) (the pair, Q42 removed) is drafted now (fallback/apply_gen_sch_a_fetpair.py, fallback/check_fetpair_netlist.py). L4A-71: the UDC-1 table that couples
HO-L, RE-10's M-A and E11-29, from the same figures. The page is L4E11-ROUND-FET.md; this script prints every figure the page quotes.

Inputs, all read from this tree (a record reads its inputs from its own tree):
  - E-1's case from record l9stk (l9stk_protection.out: 23.93 A held from 76.25 C, the band 9.16 K, R17's 2.86 W, the budget 64.59 K, the
    three's even split 45.88 K/W) and L9-STACKUPS.md (R17 designed apart: its coupling at most 1 K/W); R17's 5 mOhm from gen_sch_a.py;
  - L4-E11's round 11 (l4e11_power.out 21b: the worst-split bar 40.78 K/W, the allowance 21.136 mOhm; 16d: the docking pulse 242.9 A);
  - record l8p's breaker (L8P-BREAKER.md: "the breaker's held 23.93 A");
  - the makers' sheets, held back under v2/vendor/*/held/ (fetched by fetch_held_back.py and fetch_held_back_fet.py, checked by sha256
    here): TI SLUSE65A (BATDRV: pin table p.5, VBATDRV_ON and RBATDRV p.17, the 5 nF rule p.92) and the eighteen P-channel sheets of the
    search. Each printed row the screen uses is read back from the cited page's text (pdftotext -layout) when the sheet has a text
    layer; the five Infineon sheets of 16 November 2009 carry no usable text layer (their fonts map to no Unicode), so their rows are
    this record's reading of the rendered pages, filed in inputs/fet-search-readings-2026-10-07.json with each sheet's sha256.

Labels: MAKER (a printed figure, its class typ or max kept), INFERRED (arithmetic on printed figures by a stated rule), SESSION (a
choice this record makes, with its reason). A typical figure is never used as a limit: the screen refuses to read a limit from a row
that prints only a typical (GuardError), and the tests mutate a typical into a limit to show the refusal.

Usage:  python3 v2/docs/records/l4e11/l4e11_fet.py        (from anywhere; it locates the tree from its own path)
Exit 0: printed; 3: refused (an input missing, a sha256 that differs, a printed row not found on its cited page, a guard tripped)."""
import hashlib
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
READINGS = "v2/docs/records/l4e11/inputs/fet-search-readings-2026-10-07.json"

# ---------------------------------------------------------------- the held documents (path, sha256, how its rows are read)
DOCS = {
    "bq25730": ("v2/vendor/ti/held/ti-bq25730-sluse65a.pdf", "e41ef289ce1de377d7b92bce609177d924e149099d9c4424d88f6b21ad57153f", "text",
                "TI BQ25730 SLUSE65A (February 2021, revised January 2024)"),
    "buk6y10": ("v2/vendor/nexperia/held/nexperia-buk6y10-30p-2020-04-17.pdf", "ba928dfe6a85134423562bd378bdfafafb26d857ba08b50560ce5aacb956da40", "text",
                "Nexperia BUK6Y10-30P product data sheet, 17 April 2020"),
    "pxp9r1": ("v2/vendor/nexperia/held/nexperia-pxp9r1-30ql.pdf", "88a7b67bfcec9ba7dbf4619be60cfaa883f61b7c9a93a19affc3a5278d91513f", "text",
               "Nexperia PXP9R1-30QL product data sheet, 5 January 2021"),
    "aons21357": ("v2/vendor/power/held/aos-aons21357-rev2.1-2023-11.pdf", "1a6460e7c63596ca7d48fe1660ee3a3ee48c33d6e345ef41d7c94c21cd7642d9", "text",
                  "AOS AONS21357 Rev 2.1, November 2023"),
    "sqj403ep": ("v2/vendor/power/held/vishay-sqj403ep-67109-reva.pdf", "6005efe139fc94e3e855c2beeef8fcaaa5dc71d3c4a6e82f8e8ce82c5506961c", "text",
                 "Vishay SQJ403EP, document 67109, S15-2089 Rev. A, 31 August 2015"),
    "sqj407ep": ("v2/vendor/power/held/vishay-sqj407ep-62806-revb.pdf", "1c1038b032b5bf378878473ba170cdbbd640ce1597fbb9c23be20adeaea663e8", "text",
                 "Vishay SQJ407EP, document 62806, S22-0224 Rev. B, 7 March 2022"),
    "sqja37ep": ("v2/vendor/power/held/vishay-sqja37ep-75171-revb.pdf", "6a723edefaa97d2049c9746296b3d74eba826a2f6f5bdd1325892c2bd03f5668", "text",
                 "Vishay SQJA37EP, document 75171, S22-0224 Rev. B, 7 March 2022"),
    "sqjq131el": ("v2/vendor/power/held/vishay-sqjq131el-77936-reva.pdf", "d5dd14f0499cbfb3f6287b0d6adca930e7fb10cdc882e90a579afa74eeabbbeb", "text",
                  "Vishay SQJQ131EL, document 77936, S21-0235 Rev. A, 15 March 2021"),
    "sqs407enw": ("v2/vendor/power/held/vishay-sqs407enw-76627-reva.pdf", "1970576e979a94559427babe70aac12d0817db1b43cfe6fda23f8ed3b91ef378", "text",
                  "Vishay SQS407ENW, document 76627, S18-0633 Rev. A, 25 June 2018"),
    "sqs415enw": ("v2/vendor/power/held/vishay-sqs415enw-77427-revc.pdf", "3d777ff9639c8c9efd8b4f2b98c0feb00289da487d20e4f5d4323dd4a797731b", "text",
                  "Vishay SQS415ENW, document 77427, S19-1112 Rev. C, 18 December 2019"),
    "sqs401en": ("v2/vendor/power/held/vishay-sqs401en-65529-revd.pdf", "385fae910ca444d9d219eeeebe52b11e94d5c3e66e303f1c432e6004c4fafa6f", "text",
                 "Vishay SQS401EN, document 65529, S21-1246 Rev. D, 10 January 2022"),
    "bsz086": ("v2/vendor/power/held/infineon-bsz086p03ns3-g-rev2.4-2019-12-03.pdf", "1e67b3366caacf20bf990e5238cd3b7d963a1276d6f97b69f79a658513f2a6a2", "text",
               "Infineon BSZ086P03NS3 G final data sheet Rev. 2.4, 3 December 2019"),
    "ipd042": ("v2/vendor/power/held/infineon-ipd042p03l3-g-rev2.2-2014-05-16.pdf", "8dbb10cfa21baa671bc6b86e8718bc2c40606504fca7d24e8a21ac11a8d414d1", "text",
               "Infineon IPD042P03L3 G Rev. 2.2, 16 May 2014"),
    "bso301": ("v2/vendor/power/held/infineon-bso301sp-h-rev1.32-2010-05-12.pdf", "f391eea4f0ea21cb1c2970fc544a1a5fdd7ea8b4fae35e3b2193c1a4f49044dc", "text",
               "Infineon BSO301SP H Rev. 1.32, 12 May 2010"),
    "bsc030": ("v2/vendor/power/held/infineon-bsc030p03ns3-g-rev2.1-2009-11-16.pdf", "a9786bf2b5f65b25742d95d5f4f5c4c76f758bf3f8f8e5b9076c9e97c6edda19", "rendered",
               "Infineon BSC030P03NS3 G Rev. 2.1, 16 November 2009"),
    "bsc060": ("v2/vendor/power/held/infineon-bsc060p03ns3e-g-rev2.1-2009-11-16.pdf", "64c17f6d22bac04897fb583456f3b560cc7a65bd0c0d05af5beb23c9296e9112", "rendered",
               "Infineon BSC060P03NS3E G Rev. 2.1, 16 November 2009"),
    "bsc084": ("v2/vendor/power/held/infineon-bsc084p03ns3-g-rev2.1-2009-11-16.pdf", "78b0ee06750492feaac517b0a1b358d8898b9780025e5cda927b65c67bb40060", "rendered",
               "Infineon BSC084P03NS3 G Rev. 2.1, 16 November 2009"),
    "bsz120": ("v2/vendor/power/held/infineon-bsz120p03ns3-g-rev2.1-2009-11-16.pdf", "d6798434aec2a3771b568795bbf0ce29700d4033aee8196b3987326e17259015", "rendered",
               "Infineon BSZ120P03NS3 G Rev. 2.1, 16 November 2009"),
    "bsz180": ("v2/vendor/power/held/infineon-bsz180p03ns3-g-rev2.1-2009-11-16.pdf", "c7882d545da9f2f1f114e34f61113e23946ce32014a03394189058eff9f41a25", "rendered",
               "Infineon BSZ180P03NS3 G Rev. 2.1, 16 November 2009"),
}

# ---------------------------------------------------------------- the parts (MAKER rows; ohm, farad, coulomb, ampere, K/W, C)
# r10: RDS(on) maxima at -10 V by junction temperature; rlo: (|VGS|, the maximum at that drive and 25 C); ciss: (typ, max or None,
# |VDS| of the row); qg: (typ, max or None, |VGS| of the row); ism: the body diode's printed pulse rating (None: none printed);
# rth: (symbol, the printed maximum); chk: (page, tokens on one line) read back from a text sheet.
PARTS = [
    dict(part="BUK6Y10-30P", maker="Nexperia", doc="buk6y10", pkg="LFPAK56", vds=30, vgs=20, tj=175, rth=("Rth(j-mb)", 1.4),
         r10={25: 10e-3, 175: 16e-3}, rlo=(4.5, 25e-3), ciss=(2.36e-9, None, 15), qg=(42.5e-9, 64e-9, 10), ism=320.0, sel="(i)(a), the three drawn",
         chk=[(3, ("VDS", "-30")), (3, ("Tj", "junction temperature", "175")), (3, ("ISM", "-320")), (5, ("Rth(j-mb)", "1.4")),
              (6, ("Tj = 25", "10")), (6, ("Tj = 175", "16")), (6, ("VGS = -4.5 V", "25")), (6, ("QG(tot)", "42.5", "64")), (6, ("Ciss", "2360"))]),
    dict(part="PXP9R1-30QL", maker="Nexperia", doc="pxp9r1", pkg="MLPAK33", vds=30, vgs=20, tj=150, rth=("Rth(j-sp)", 2.5),
         r10={25: 9.1e-3, 150: 15.3e-3}, rlo=(4.5, 12.8e-3), ciss=(2.86e-9, None, 15), qg=(57e-9, 86e-9, 10), ism=None,
         sel="read in round 16a, restated",
         chk=[(3, ("Tj", "junction temperature", "150")), (5, ("Rth(j-sp)", "2.5")), (6, ("Tj = 25", "9.1")), (6, ("Tj = 150", "15.3")),
              (6, ("VGS = -4.5 V", "12.8")), (6, ("QG(tot)", "57", "86")), (6, ("Ciss", "2860"))]),
    dict(part="AONS21357", maker="AOS", doc="aons21357", pkg="DFN 5x6", vds=30, vgs=25, tj=150, rth=("RthJC", 2.6),
         r10={25: 7.8e-3, 125: 10.7e-3}, rlo=(4.5, 12.3e-3), ciss=(2.83e-9, None, 15), qg=(50e-9, 70e-9, 10), ism=None,
         sel="read in round 15c, restated",
         chk=[(1, ("TJ, TSTG", "150")), (1, ("Junction-to-Case", "2.6")), (2, ("VGS=-10V, ID=-20A", "7.8")), (2, ("TJ=125", "10.7")),
              (2, ("VGS=-4.5V", "12.3")), (2, ("Input Capacitance", "2830")), (2, ("Qg(10V)", "50", "70"))]),
    dict(part="SQJ403EP", maker="Vishay", doc="sqj403ep", pkg="PowerPAK SO-8L", vds=30, vgs=20, tj=175, rth=("RthJC", 2.2),
         r10={25: 8.5e-3, 125: 13.0e-3, 175: 15.0e-3}, rlo=(4.5, 20.0e-3), ciss=(3.4e-9, 4.5e-9, 15), qg=(73e-9, 109e-9, 10), ism=84.0,
         sel="read in round 15c, restated",
         chk=[(1, ("TJ, Tstg", "175")), (1, ("RthJC", "2.2")), (2, ("ID = -10 A", "0.0085")), (2, ("TJ = 125", "0.0130")),
              (2, ("TJ = 175", "0.0150")), (2, ("VGS = -4.5 V", "0.0200")), (2, ("Input Capacitance", "3400", "4500")),
              (2, ("VDS = -15 V, f = 1 MHz",)), (2, ("Total Gate Charge", "73", "109")), (2, ("ISM", "-84"))]),
    dict(part="SQJ407EP", maker="Vishay", doc="sqj407ep", pkg="PowerPAK SO-8L", vds=30, vgs=20, tj=175, rth=("RthJC", 2.2),
         r10={25: 4.4e-3, 125: 6.0e-3, 175: 6.8e-3}, rlo=(4.5, 7.1e-3), ciss=(8.2e-9, 10.7e-9, 25), qg=(169e-9, 260e-9, 10), ism=155.0,
         sel="read in round 16a, restated",
         chk=[(1, ("TJ, Tstg", "175")), (1, ("RthJC", "2.2")), (2, ("ID = -10 A", "0.0044")), (2, ("TJ = 125", "0.0060")),
              (2, ("TJ = 175", "0.0068")), (2, ("VGS = -4.5 V", "0.0071")), (2, ("Input capacitance", "8200", "10 700")),
              (2, ("VDS = -25 V, f = 1 MHz",)), (2, ("Total gate charge", "169", "260")), (2, ("ISM", "-155"))]),
    dict(part="SQJA37EP", maker="Vishay", doc="sqja37ep", pkg="PowerPAK SO-8L", vds=30, vgs=20, tj=175, rth=("RthJC", 3.3),
         r10={25: 9.2e-3, 125: 11.2e-3, 175: 12.2e-3}, rlo=(4.5, 14.6e-3), ciss=(3.62e-9, 4.9e-9, 25), qg=(65e-9, 100e-9, 10), ism=120.0,
         chk=[(1, ("TJ, Tstg", "175")), (1, ("RthJC", "3.3")), (2, ("ID = -6 A", "0.0092")), (2, ("TJ = 125", "0.0112")),
              (2, ("TJ = 175", "0.0122")), (2, ("VGS = -4.5 V", "0.0146")), (2, ("Input capacitance", "3620", "4900")),
              (2, ("VDS = -25 V, f = 1 MHz",)), (2, ("Total gate charge", "65", "100")), (2, ("ISM", "-120"))]),
    dict(part="SQJQ131EL", maker="Vishay", doc="sqjq131el", pkg="PowerPAK 8x8L", vds=30, vgs=20, tj=175, rth=("RthJC", 0.25),
         r10={25: 1.4e-3, 125: 1.9e-3, 175: 2.2e-3}, rlo=(4.5, 2.2e-3), ciss=(23.588e-9, 33.05e-9, 15), qg=(487e-9, 731e-9, 10), ism=1100.0,
         chk=[(1, ("TJ, Tstg", "175")), (1, ("RthJC", "0.25")), (2, ("ID = -10 A", "0.0014")), (2, ("TJ = 125", "0.0019")),
              (2, ("TJ = 175", "0.0022")), (2, ("VGS = -4.5 V", "0.0022")), (2, ("Input capacitance", "23 588", "33 050")),
              (2, ("VDS = 15 V, f = 1 MHz",)), (2, ("Total gate charge", "487", "731")), (2, ("ISM", "1100"))]),
    dict(part="SQS407ENW", maker="Vishay", doc="sqs407enw", pkg="PowerPAK 1212-8W", vds=30, vgs=20, tj=175, rth=("RthJC", 2.4),
         r10={25: 10.8e-3, 125: 15.0e-3, 175: 18.0e-3}, rlo=(4.5, 17.0e-3), ciss=(3.515e-9, 4.572e-9, 20), qg=(59e-9, 77e-9, 10), ism=64.0,
         chk=[(1, ("TJ, Tstg", "175")), (1, ("RthJC", "2.4")), (2, ("ID = -12 A", "0.0108")), (2, ("TJ = 125", "0.0150")),
              (2, ("TJ = 175", "0.0180")), (2, ("VGS = -4.5 V", "0.0170")), (2, ("Input capacitance", "3515", "4572")),
              (2, ("VDS = -20 V, f = 1 MHz",)), (2, ("Total gate charge", "59", "77")), (2, ("ISM", "-64"))]),
    dict(part="SQS415ENW", maker="Vishay", doc="sqs415enw", pkg="PowerPAK 1212-8W", vds=40, vgs=20, tj=175, rth=("RthJC", 2.4),
         r10={25: 16.1e-3, 125: 24.0e-3, 175: 27.0e-3}, rlo=(4.5, 23.0e-3), ciss=(3.71e-9, 4.825e-9, 25), qg=(63e-9, 82e-9, 10), ism=64.0,
         chk=[(1, ("TJ, Tstg", "175")), (1, ("RthJC", "2.4")), (2, ("ID = -12 A", "0.0161")), (2, ("TJ = 125", "0.0240")),
              (2, ("TJ = 175", "0.0270")), (2, ("VGS = -4.5 V", "0.0230")), (2, ("Input capacitance", "3710", "4825")),
              (2, ("VDS = -25 V, f = 1 MHz",)), (2, ("Total gate charge", "63", "82")), (2, ("ISM", "-64"))]),
    # SQS401EN prints QG(tot) at VGS -4.5 V only (its 21.2 nC maximum): no printed QG maximum at BATDRV's 10 V drive
    dict(part="SQS401EN", maker="Vishay", doc="sqs401en", pkg="PowerPAK 1212-8", vds=40, vgs=20, tj=175, rth=("RthJC", 2.4),
         r10={25: 29e-3, 125: 43e-3, 175: 51e-3}, rlo=(4.5, 47e-3), ciss=(1.565e-9, 1.875e-9, 20), qg=(17.7e-9, 21.2e-9, 4.5), ism=64.0,
         chk=[(1, ("TJ, Tstg", "175")), (1, ("RthJC", "2.4")), (2, ("ID = -12 A", "0.029")), (2, ("TJ = 125", "0.043")),
              (2, ("TJ = 175", "0.051")), (2, ("VGS = -4.5 V", "0.047")), (2, ("Input Capacitance", "1565", "1875")),
              (2, ("VDS = -20 V, f = 1 MHz",)), (2, ("Total Gate Charge", "17.7", "21.2")), (2, ("VGS = -4.5 V", "VDS = -20 V, ID = -9.3 A")),
              (2, ("ISM", "-64"))]),
    dict(part="BSZ086P03NS3 G", maker="Infineon", doc="bsz086", pkg="PQFN 3.3x3.3", vds=30, vgs=25, tj=150, rth=("RthJC", 1.8),
         r10={25: 8.6e-3}, rlo=(6.0, 13.4e-3), ciss=(3.19e-9, 4.785e-9, 15), qg=(43.2e-9, 57.5e-9, 10), ism=160.0,
         chk=[(3, ("Gate source voltage", "-25", "25")), (3, ("Operating and storage temperature", "150")), (3, ("RthJC", "1.8")),
              (4, ("6.5", "8.6", "VGS=-10 V")), (4, ("8.7", "13.4", "VGS=-6 V")), (4, ("Ciss", "3190", "4785", "VDS=-15 V")),
              (4, ("Gate charge total", "43.2", "57.5", "VDD=-15 V")), (5, ("Diode pulse current", "-160"))]),
    dict(part="IPD042P03L3 G", maker="Infineon", doc="ipd042", pkg="DPAK (TO-252)", vds=30, vgs=20, tj=175, rth=("RthJC", 1.0),
         r10={25: 4.2e-3}, rlo=(4.5, 6.8e-3), ciss=(9.29e-9, 12.4e-9, 15), qg=(131e-9, 175e-9, 10), ism=280.0,
         chk=[(1, ("VDS", "-30")), (1, ("T j, T stg", "175")), (1, ("V GS", "\u00b120")), (2, ("R thJC", "1.0")), (2, ("V GS=-4.5 V", "6.8")),
              (2, ("V GS=-10 V", "4.2")), (3, ("C iss", "9290", "12400")), (3, ("V DS=-15 V",)), (3, ("Gate charge total", "131", "175")),
              (3, ("V GS=0 to -10 V",)), (3, ("I S,pulse", "280"))]),
    # BSO301SP H prints a junction-to-soldering-point resistance (RthJS) and no junction-to-case figure
    dict(part="BSO301SP H", maker="Infineon", doc="bso301", pkg="SO-8", vds=30, vgs=20, tj=150, rth=("RthJS", 35.0),
         r10={25: 8.0e-3}, rlo=(4.5, 12e-3), ciss=(4.43e-9, 5.89e-9, 25), qg=(102e-9, 136e-9, 10), ism=60.0,
         chk=[(1, ("V DS", "-30")), (1, ("T j, T stg", "150")), (1, ("V GS", "\u00b120")), (2, ("R thJS", "35")), (2, ("V GS=-4.5 V", "12")),
              (2, ("V GS=-10 V", "8.0")), (3, ("C iss", "4430", "5890")), (3, ("V DS=-25 V",)), (3, ("Gate charge total", "-102", "-136")),
              (3, ("V GS=0 to -10 V",)), (3, ("I S,pulse", "-60"))]),
    dict(part="BSC030P03NS3 G", maker="Infineon", doc="bsc030", pkg="SuperSO8", vds=30, vgs=25, tj=150, rth=("RthJC", 1.0),
         r10={25: 3.0e-3}, rlo=(6.0, 4.6e-3), ciss=(10.5e-9, 14.0e-9, 15), qg=(140e-9, 186e-9, 10), ism=200.0, chk=[]),
    dict(part="BSC060P03NS3E G", maker="Infineon", doc="bsc060", pkg="SuperSO8", vds=30, vgs=25, tj=150, rth=("RthJC", 1.5),
         r10={25: 6.0e-3}, rlo=(6.0, 9.6e-3), ciss=(4.53e-9, 6.02e-9, 15), qg=(61e-9, 81e-9, 10), ism=200.0, chk=[]),
    dict(part="BSC084P03NS3 G", maker="Infineon", doc="bsc084", pkg="SuperSO8", vds=30, vgs=25, tj=150, rth=("RthJC", 1.8),
         r10={25: 8.4e-3}, rlo=(6.0, 14.0e-3), ciss=(3.19e-9, 4.785e-9, 15), qg=(43e-9, 58e-9, 10), ism=200.0, chk=[]),
    dict(part="BSZ120P03NS3 G", maker="Infineon", doc="bsz120", pkg="PQFN 3.3x3.3", vds=30, vgs=25, tj=150, rth=("RthJC", 2.4),
         r10={25: 12.0e-3}, rlo=(6.0, 20.0e-3), ciss=(2.24e-9, 3.36e-9, 15), qg=(30e-9, 45e-9, 10), ism=160.0, chk=[]),
    dict(part="BSZ180P03NS3 G", maker="Infineon", doc="bsz180", pkg="PQFN 3.3x3.3", vds=30, vgs=25, tj=150, rth=("RthJC", 3.1),
         r10={25: 18.0e-3}, rlo=(6.0, 30.0e-3), ciss=(1.48e-9, 2.22e-9, 15), qg=(20e-9, 30e-9, 10), ism=160.0, chk=[]),
]

TI_CISS = 5e-9          # SLUSE65A 9.2.2 (p.92): "the Ciss of P-channel MOSFET should be chosen less than 5 nF" (MAKER, no VDS stated)
TI_QG_V = 10.0          # the QG reading (SESSION): QG(tot)'s printed maximum at VGS -10 V against the charge 5 nF takes over 10 V
VDS_NEED = 29.2         # VBAT's SMCJ18A clamp with the cells' side near 0 V (L4E11-SOURCE-ONLY-AND-ENTRY.md 20g: VDS at most 29.2 V)
TLIM_BELOW = 25.0       # the record's convention: the junction limit 25 K under the rating (L4-E11 15c; 21b (i)(b))
SCREEN_N = 12           # the largest count screened (no set of more than 12 battery FETs fits one LFPAK pour; the class bound covers any n)


class Refused(Exception):
    pass


class GuardError(Exception):
    """A typical figure asked for as a limit."""


def fmt(x, n=2):
    return ("%%.%df" % n) % x


def path(rel):
    return os.path.join(ROOT, rel)


def read(rel):
    p = path(rel)
    if not os.path.isfile(p):
        raise Refused("missing input %s" % rel)
    return open(p, encoding="utf-8").read()


def sha(rel):
    return hashlib.sha256(open(path(rel), "rb").read()).hexdigest()


def need(text, pat, what):
    m = re.search(pat, text)
    if not m:
        raise Refused("%s not found" % what)
    return m


_PAGES = {}


def pages(key):
    if key not in _PAGES:
        rel, want, kind, _t = DOCS[key]
        if not os.path.isfile(path(rel)):
            raise Refused("held sheet %s absent (fetch_held_back.py / fetch_held_back_fet.py)" % rel)
        if sha(rel) != want:
            raise Refused("held sheet %s differs from the sha256 this record read" % rel)
        if kind != "text":
            _PAGES[key] = None
        else:
            r = subprocess.run(["pdftotext", "-layout", path(rel), "-"], capture_output=True)
            if r.returncode != 0:
                raise Refused("pdftotext refused %s" % rel)
            # a control character some makers' fonts map their thin spaces to is read as a space
            _PAGES[key] = [re.sub(r"[ \t]+", " ", re.sub(r"[\x00-\x08\x0b\x0e-\x1f]", " ", p)) for p in r.stdout.decode("utf-8", "replace").split("\f")]
    return _PAGES[key]


def on_page(key, page, tokens):
    """True when one line of the cited page carries every token (whitespace normalised)."""
    pg = pages(key)[page - 1]
    return any(all(t in line for t in tokens) for line in pg.splitlines())


def limit(row, what):
    """The printed maximum of a (typ, max, ...) row; a row that prints only a typical is never a limit."""
    if row[1] is None:
        raise GuardError("%s: the sheet prints a typical only (%s); a typical is never a limit" % (what, row[0]))
    return row[1]


# ---------------------------------------------------------------- inputs from the tree
def inputs():
    E = {}
    o9 = read("v2/docs/records/l9stk/l9stk_protection.out")
    m = need(o9, r"held at ([\d.]+) A from ([\d.]+) C, the band carrying the current \(([\d.]+) K", "E-1's case (l9stk)")
    E["i"], E["t0"], E["band"] = float(m.group(1)), float(m.group(2)), float(m.group(3))
    m = need(o9, r"and R17 dissipating ([\d.]+) W in place; the budget for the FETs and R17's coupling is ([\d.]+) K", "R17 and the budget (l9stk)")
    E["pr17_rec"], E["budget_rec"] = float(m.group(1)), float(m.group(2))
    m = need(o9, r"three \(Zself \+ 2 Zmut\)\s+([\d.]+) W each: FETs only ([\d.]+) K/W; R17 apart ([\d.]+) K/W", "the three's even split (l9stk)")
    E["even3_rec"] = float(m.group(3))
    m = need(o9, r"the pair \(Zself \+ Zmut\)\s+([\d.]+) W each: FETs only ([\d.]+) K/W; R17 apart ([\d.]+) K/W", "the pair's figure (l9stk)")
    E["pair_rec"] = float(m.group(3))
    st = re.sub(r"\s+", " ", read("v2/docs/records/l9stk/L9-STACKUPS.md"))
    E["r17c"] = float(need(st, r"Designed apart \(off the FETs' pour\), it is held to ([\d.]+) K/W", "R17's coupling (L9-STACKUPS.md)").group(1))
    ga = read("v2/ecad/tools/gen_sch_a.py")
    E["r17"] = float(need(ga, r'r\("R17", "(\d+)mOhm 1% 2512 \(RSR', "R17 (gen_sch_a.py)").group(1)) * 1e-3
    out = read("v2/docs/records/l4e11/l4e11_power.out")
    sec = need(out, r"(?s)21b\. THE THREE APPROACHES(.*?)21c\. ", "round 11's 21b (l4e11_power.out)").group(1)
    E["bar"] = float(need(sec, r"m    0: \(Zself \+ 2 Zmut\) at most ([\d.]+) K/W", "the worst-split bar").group(1))
    E["bar_pair"] = float(need(sec, r"its E-1 bar is record l9stk's \(Zself \+\s+Zmut\) at most ([\d.]+) K/W", "the pair's bar").group(1))
    E["ra"] = float(need(out, r"the allowance is section 15c's two-chord figure", "the allowance's origin") and
                    need(out, r"E-1 sized each FET at the even split, ([\d.]+) W at the RDS\(on\) allowance ([\d.]+) mOhm", "the allowance").group(2)) * 1e-3
    E["dock"] = float(need(out, r"the docking pulse, ([\d.]+) A peak: 320 A ISM", "the docking pulse (l4e11_power.out 16)").group(1))
    brk = read("v2/docs/records/l8p/L8P-BREAKER.md")
    E["held_brk"] = float(need(brk, r"at the breaker's held ([\d.]+) A", "the breaker's held current (L8P-BREAKER.md)").group(1))
    if abs(E["held_brk"] - E["i"]) > 1e-9:
        raise Refused("record l8p's held current and record l9stk's case differ")
    # TI's sheet: the pin, the drive and the rule
    E["ti_pin"] = on_page("bq25730", 5, ("P-channel battery FET (BATFET) gate driver output",))
    E["ti_drive"] = on_page("bq25730", 17, ("VBATDRV_ON", "8.5", "10", "11.5"))
    E["ti_ron"] = on_page("bq25730", 17, ("RBATDRV_ON", "3", "4", "6"))
    E["ti_rule"] = on_page("bq25730", 92, ("the Ciss of",)) and on_page("bq25730", 92, ("P-channel MOSFET should be chosen less than 5 nF.",))
    if not all((E["ti_pin"], E["ti_drive"], E["ti_ron"], E["ti_rule"])):
        raise Refused("TI's BATDRV rows are not where this record cites them (SLUSE65A pp.5, 17, 92)")
    E["vgs_drive"], E["vgs_drive_max"] = 8.5, 11.5
    return E


def check_rows():
    """Every printed row the screen uses, read back: text sheets by page, rendered sheets against the filed readings."""
    rd = json.loads(read(READINGS))
    lines = []
    for P in PARTS:
        rel, want, kind, title = DOCS[P["doc"]]
        pages(P["doc"])                                            # presence and sha256
        if kind == "text":
            bad = [(pg, t) for pg, t in P["chk"] if not on_page(P["doc"], pg, t)]
            if bad:
                raise Refused("%s: rows not on their cited pages: %s" % (P["part"], bad))
            lines.append("%s %s: %d rows read on the sheet's text layer" % (want[:16], rel, len(P["chk"])))
        else:
            r = rd["sheets"].get(P["doc"])
            if not r or r["sha256"] != want or r["part"] != P["part"]:
                raise Refused("%s: no filed reading for this sheet" % P["part"])
            got = r["rows"]
            exp = {"rds_10v_25c_max": P["r10"][25], "rds_lo_25c_max": P["rlo"][1], "rds_lo_vgs": P["rlo"][0], "ciss_typ": P["ciss"][0],
                   "ciss_max": P["ciss"][1], "ciss_vds": P["ciss"][2], "qg_typ": P["qg"][0], "qg_max": P["qg"][1], "is_pulse": P["ism"],
                   "rthjc_max": P["rth"][1], "tj_max": P["tj"], "vgs_max": P["vgs"], "vds": P["vds"]}
            diff = [k for k, v in exp.items() if k not in got or abs(got[k] - v) > 1e-15 + 1e-9 * abs(v)]
            if diff:
                raise Refused("%s: the table differs from the filed reading at %s" % (P["part"], diff))
            lines.append("%s %s: %d rows from the rendered pages %s (READING, %s)" % (want[:16], rel, len(exp), r["pages"], READINGS))
    return lines


# ---------------------------------------------------------------- the rules (INFERRED from printed rows; SESSION where named)
def chord(x, x1, y1, x2, y2):
    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)


def allowance(P, vgs=8.5):
    """L4-E11 15c's two chords on printed maxima: the gate ratio at 25 C between the low-drive and -10 V maxima, the temperature factor
    between the printed -10 V maxima bracketing the limit. None when no printed hot maximum reaches the limit."""
    tl = P["tj"] - TLIM_BELOW
    r10 = P["r10"]
    g = chord(vgs, P["rlo"][0], P["rlo"][1], 10.0, r10[25]) / r10[25]
    ts = sorted(r10)
    if tl in r10:
        hf = r10[tl] / r10[25]
    else:
        hi = [t for t in ts if t > tl]
        lo = [t for t in ts if t < tl]
        hf = chord(tl, lo[-1], r10[lo[-1]], hi[0], r10[hi[0]]) / r10[25] if hi else None
    return dict(tl=tl, g=g, hf=hf, ra=(r10[25] * g * hf if hf else None), rs=r10[25])


def budget(E, tl):
    return tl - E["t0"] - E["band"] - E["r17c"] * E["i"] ** 2 * E["r17"]


def f0(n):
    """The worst split's factor over the even split for n like FETs with no printed RDS(on) minimum (L4-E11 21a generalised):
    one FET at R / x and n - 1 at R, the hottest rise I^2 R Zself (x + m (n - 1)) / (x + n - 1)^2; its largest over x and m is at m = 0,
    x = n - 1: n^2 / (4 (n - 1)) for n >= 2 (9/8 for three, 1 for two), 1 for one."""
    return 1.0 if n <= 2 else n * n / (4.0 * (n - 1))


def bar(E, n, R, tl):
    """The installed per-FET (Zself + (n - 1) Zmut) at which the hottest junction is at most tl held at E-1's current, any split."""
    return budget(E, tl) * n * n / (E["i"] ** 2 * R * f0(n))


def i_hold(E, n, R, tl, z):
    """The held current at which the set's hottest junction reaches tl when each FET is installed at z (any split)."""
    return math.sqrt(budget(E, tl) * n * n / (z * R * f0(n)))


def n_gate(P):
    """The largest counts under TI's 5 nF on PRINTED maxima: by Ciss (the maker's own VDS) and by QG(tot) at -10 V (SESSION reading)."""
    try:
        c = limit(P["ciss"], P["part"] + " Ciss")
        nc = int(math.floor(TI_CISS / c * (1 - 1e-12)))
        while nc > 0 and nc * c >= TI_CISS:
            nc -= 1
    except GuardError:
        nc = None
    nq = None
    if P["qg"][1] is not None and abs(P["qg"][2] - TI_QG_V) < 1e-9:
        q = P["qg"][1]
        nq = int(math.floor(TI_CISS * TI_QG_V / q * (1 - 1e-12)))
        while nq > 0 and nq * q >= TI_CISS * TI_QG_V:
            nq -= 1
    return nc, nq


def screen(E, P):
    a = allowance(P)
    nc, nq = n_gate(P)
    S = dict(a=a, nc=nc, nq=nq, vds_ok=P["vds"] >= VDS_NEED, vgs_ok=P["vgs"] >= E["vgs_drive_max"])
    ns = [n for n in (nc, nq) if n]
    S["n"] = max(ns) if ns else 0
    R = a["ra"] if a["ra"] is not None else a["rs"]
    S["R_used"] = R
    S["R_basis"] = "ALLOWANCE (two chords on printed maxima)" if a["ra"] is not None else "SCREEN BOUND (the -10 V, 25 C maximum; no hot maximum printed)"
    S["bar"] = bar(E, S["n"], R, a["tl"]) if S["n"] else None
    S["G"] = S["n"] >= 1
    S["T"] = S["bar"] is not None and S["bar"] >= E["bar"] and a["ra"] is not None
    S["T_bound_fails"] = S["bar"] is not None and S["bar"] < E["bar"]   # fails even on the favourable bound
    S["H"] = S["T"]
    S["dock"] = P["ism"] is not None and P["ism"] >= E["dock"]
    S["rth_ok"] = S["bar"] is not None and P["rth"][1] < S["bar"]
    # the class figure: Ciss max x R against the n -> infinity limit of the joint condition
    c = P["ciss"][1]
    S["fom"] = c * R * 1e12 if c is not None else None                     # nF x mOhm
    S["fom_lim"] = class_limit(E, a["tl"])
    S["meets_all"] = S["G"] and S["T"] and S["H"] and S["vds_ok"] and S["vgs_ok"]
    return S


def class_limit(E, tl):
    """For n >= 2 like FETs: n Ciss < 5 nF and bar >= E-1's bar need Ciss_max R < 5 nF x 4 (n - 1) B / (bar I^2 n), which rises to
    20 B / (bar I^2) nF.Ohm as n grows: a part above it makes no set at any count (nF x mOhm)."""
    return TI_CISS * 1e9 * 4.0 * budget(E, tl) / (E["bar"] * E["i"] ** 2) * 1e3


def options(E):
    """The drawn and the record's options on the same basis (BUK6Y10-30P at the record's allowance)."""
    ra = E["ra"]
    buk = PARTS[0]
    out = []
    # the drawn three and the pair carry the records' printed bars (rounded inputs, reproduced within 0.1 % in compute()); one FET's is
    # computed on the same rule; about 2.87 nF near 0 V is round 16's reading of the sheet's Fig. 12 (typical)
    for name, n, b in (("(i)(a) three BUK6Y10-30P (drawn, SELECTED in round 11)", 3, E["bar"]), ("(ii) the pair, Q42 removed (the fallback)", 2, E["bar_pair"]),
                       ("(S2) one BUK6Y10-30P, a heat path through the case", 1, bar(E, 1, ra, 150.0))):
        o = dict(name=name, n=n, ciss_typ=n * buk["ciss"][0], ciss_0=n * 2.87e-9, qg_max=n * buk["qg"][1], bar=b,
                 ihold=i_hold(E, n, ra, 150.0, E["bar"]))
        try:
            limit(buk["ciss"], "BUK6Y10-30P Ciss")
            o["G"] = True
        except GuardError:
            o["G"] = None                                           # NOT SHOWN: no printed maximum
        o["QG_ok"] = o["qg_max"] < TI_CISS * TI_QG_V
        out.append(o)
    return out


def compute():
    E = inputs()
    rows = check_rows()
    # the record's own figures reproduced on this rule set
    e3 = budget(E, 150.0) / ((E["i"] / 3) ** 2 * E["ra"])
    if abs(e3 - E["even3_rec"]) > 0.001 * E["even3_rec"] + 0.03 or abs(bar(E, 3, E["ra"], 150.0) - E["bar"]) > 0.001 * E["bar"] + 0.03:
        raise Refused("the rule set does not reproduce record l9stk's even split or round 11's worst-split bar")
    if abs(bar(E, 2, E["ra"], 150.0) - E["pair_rec"]) > 0.001 * E["pair_rec"] + 0.02:
        raise Refused("the rule set does not reproduce the pair's 20.39 K/W")
    buk = allowance(PARTS[0])
    if abs(buk["ra"] - E["ra"]) > 5e-7:
        raise Refused("the two chords do not reproduce the record's 21.136 mOhm allowance")
    res = [(P, screen(E, P)) for P in PARTS]
    return dict(E=E, rows=rows, res=res, opts=options(E), e3=e3, buk=buk)


def gate_text(P, S):
    c = P["ciss"]
    ct = "Ciss %s nF typ, %s at -%g V" % (fmt(c[0] * 1e9, 3), ("%s nF MAX" % fmt(c[1] * 1e9, 3)) if c[1] is not None else "NO MAXIMUM PRINTED", c[2])
    q = P["qg"]
    qt = "QG(tot) %s nC typ, %s at -%g V" % (fmt(q[0] * 1e9, 1), ("%s nC MAX" % fmt(q[1] * 1e9, 1)) if q[1] is not None else "no maximum", q[2])
    return ct + "; " + qt


def report(R):
    E, res = R["E"], R["res"]
    o = []
    w = o.append
    w("L4-E11 ROUND FET: L4A-70 (a battery-FET set robust to Q-TI-17) and L4A-71 (row (c)'s selection gate), 7 October 2026")
    w("Desk engineering on printed figures; nothing bought, built, measured or sent. Labels: MAKER, INFERRED, SESSION, READING.")
    w("")
    w("1. INPUTS (read from this tree)")
    w("   E-1's case (record l9stk l9stk_protection.out): the hottest battery FET at most its limit held at %s A from %s C, the band %s K, R17 "
      "%s mOhm dissipating %s W (record %s W), its coupling at most %s K/W designed apart (L9-STACKUPS.md); the budget at 150 C %s K "
      "for the FETs and R17's coupling (record %s K)" % (fmt(E["i"]), fmt(E["t0"]), fmt(E["band"]), fmt(E["r17"] * 1e3, 0),
                                                           fmt(E["i"] ** 2 * E["r17"], 3), fmt(E["pr17_rec"]), fmt(E["r17c"], 1),
                                                           fmt(150 - E["t0"] - E["band"], 2), fmt(E["budget_rec"])))
    w("   the breaker's held %s A (record l8p L8P-BREAKER.md, the same current)" % fmt(E["held_brk"]))
    w("   E-1's worst-split bar %s K/W per FET for the three (l4e11_power.out 21b), the pair's %s K/W; the RDS(on) allowance %s mOhm at "
      "-8.5 V and 150 C (15c, E11-36); the docking pulse %s A peak taken whole in one body diode (16d, E11-30)"
      % (fmt(E["bar"]), fmt(E["bar_pair"]), fmt(E["ra"] * 1e3, 3), fmt(E["dock"], 1)))
    w("   TI SLUSE65A (MAKER): BATDRV is the 'P-channel battery FET (BATFET) gate driver output' (p.5); VBATDRV_ON 8.5 / 10 / 11.5 V, "
      "RBATDRV_ON 3 / 4 / 6 kOhm (p.17); 'the Ciss of P-channel MOSFET should be chosen less than 5 nF' (p.92), no VDS stated")
    w("   reproduced on this round's rules (INFERRED): the three's even split %s K/W (record %s), the worst split %s K/W (record %s), the pair "
      "%s K/W (record %s), BUK6Y10-30P's two chords %s mOhm (record %s): within 0.1 %%, the records' printed figures taken"
      % (fmt(R["e3"]), fmt(E["even3_rec"]), fmt(bar(E, 3, E["ra"], 150.0)), fmt(E["bar"]), fmt(bar(E, 2, E["ra"], 150.0)), fmt(E["pair_rec"]),
         fmt(R["buk"]["ra"] * 1e3, 3), fmt(E["ra"] * 1e3, 3)))
    w("   the held makers' sheets (sha256, path; each row read back):")
    for line in R["rows"]:
        w("     " + line)
    w("     %s %s: BATDRV pp.5, 17, 92" % (DOCS["bq25730"][1][:16], DOCS["bq25730"][0]))
    w("")
    w("2. THE SCREEN (SESSION: its scope and readings; INFERRED: its arithmetic)")
    w("   scope: P-channel, |VDS| at least %s V (VBAT's 29.2 V clamp with the cells' side near 0 V), |VGS| rating at least %s V (BATDRV's "
      "printed largest drive), like parts in parallel on one BATDRV node, 1 to %d of them; makers whose sheets print a Ciss or QG(tot) "
      "maximum read in full (seven Vishay automotive SQ parts and eight of the -30 V parts of Infineon's 2023 P-channel selection guide), "
      "with the record's three earlier parts (Nexperia, AOS) restated; an N-channel FET is outside the drive the design has (BATDRV pulls the gate 10 V BELOW VSYS, p.5)"
      % (fmt(30.0, 0), fmt(E["vgs_drive_max"], 1), SCREEN_N))
    w("   G, TI's 5 nF on PRINTED maxima: n x Ciss(max) under 5 nF at the maker's own VDS (near 0 V not bounded: Q-TI-17 (e)), or n x "
      "QG(tot)(max) at -10 V under 50 nC (the charge 5 nF takes over 10 V; a SESSION reading TI does not state, Q-TI-17 asks); a sheet "
      "that prints a typical only gives no G (a typical is never a limit)")
    w("   T, the 40.78 K/W bar: the set's own worst-split bar per FET, (Zself + (n - 1) Zmut) at most B n^2 / (I^2 R F0(n)) with F0 = "
      "n^2 / (4 (n - 1)) for n at least 3 and 1 for one or two (21a generalised), at least E-1's %s K/W" % fmt(E["bar"]))
    w("   H, the held %s A on printed figures: the bar is computed at E-1's current with R the ALLOWANCE at -8.5 V and the limit (25 K under "
      "the rating) by the two chords of 15c on printed maxima; a sheet with no printed hot maximum gives no allowance, and the screen "
      "then uses its -10 V, 25 C maximum, a bound under any hot -8.5 V figure, which can show a FAIL and never a PASS" % fmt(E["i"]))
    w("   D, information: the docking pulse %s A against the printed body-diode pulse rating, whole in one FET (E11-30's rule)" % fmt(E["dock"], 1))
    w("")
    w("3. THE CANDIDATES (MAKER rows; INFERRED figures; the best set each part allows under G)")
    for P, S in res:
        a = S["a"]
        w("   %s (%s, %s; %s; %s): VDS -%d V, VGS +-%d V, rated %d C so its limit %d C; %s %s K/W max" %
          (P["part"], P["maker"], P["pkg"], DOCS[P["doc"]][3], P.get("sel", "new in this round"), P["vds"], P["vgs"], P["tj"], a["tl"], P["rth"][0],
           fmt(P["rth"][1], 2)))
        hot = ", ".join("%s at %d C" % (fmt(v * 1e3, 1), t) for t, v in sorted(P["r10"].items()))
        w("     RDS(on) max at -10 V: %s mOhm; at -%g V and 25 C %s mOhm; gate ratio at -8.5 V %s; hot factor to %d C %s; R %s mOhm (%s)" %
          (hot, P["rlo"][0], fmt(P["rlo"][1] * 1e3, 1), fmt(a["g"], 4), a["tl"], fmt(a["hf"], 4) if a["hf"] else "NOT PRINTED",
           fmt(S["R_used"] * 1e3, 3), S["R_basis"]))
        w("     %s" % gate_text(P, S))
        nc = "NOT SHOWN (no printed maximum)" if S["nc"] is None else str(S["nc"])
        nq = "NOT SHOWN" if S["nq"] is None else str(S["nq"])
        w("     G: the largest count under 5 nF by Ciss max %s, by QG max at -10 V %s" % (nc, nq))
        if S["n"]:
            w("     T and H for %d: bar %s K/W against %s (%s); held at the 40.78 bar %s A against %s A; the device's own %s %s K/W" %
              (S["n"], fmt(S["bar"]), fmt(E["bar"]), "MEETS" if S["T"] else ("FAILS" if S["T_bound_fails"] else "NOT SHOWN"),
               fmt(i_hold(E, S["n"], S["R_used"], a["tl"], E["bar"])), fmt(E["i"]), P["rth"][0], fmt(P["rth"][1], 2)))
        else:
            w("     T and H: no count meets G on a printed maximum, so no set is formed")
        w("     D: %s; class figure Ciss(max) x R %s nF.mOhm against %s at any count; VERDICT: %s" %
          (("ISM %s A: %s" % (fmt(P["ism"], 0), "MEETS" if S["dock"] else "UNDER the pulse")) if P["ism"] is not None else "no body-diode pulse rating printed",
           fmt(S["fom"], 1) if S["fom"] is not None else "n/a (no Ciss maximum)", fmt(S["fom_lim"], 2), "MEETS ALL THREE" if S["meets_all"] else
           ("FAILS T" if S["G"] else "NO G ON PRINTED MAXIMA")))
    w("")
    w("4. THE CLASS BOUND (INFERRED)")
    w("   for n like FETs G (by Ciss) and T together need Ciss(max) x R under 5 nF x 4 (n - 1) B / (bar I^2 n), rising with n to %s nF.mOhm "
      "for a 175 C part (limit 150 C) and %s for a 150 C part (limit 125 C); by QG the same limit is %s nC.mOhm and %s"
      % (fmt(class_limit(E, 150.0), 2), fmt(class_limit(E, 125.0), 2), fmt(class_limit(E, 150.0) * TI_QG_V, 1), fmt(class_limit(E, 125.0) * TI_QG_V, 1)))
    form = [(S["fom"], P["part"], S) for P, S in res if P["ciss"][1] is not None and P["ciss"][1] < TI_CISS]
    lo = min(form, key=lambda x: x[0] - x[2]["fom_lim"])
    over = [P["part"] for P, S in res if P["ciss"][1] is not None and P["ciss"][1] >= TI_CISS]
    near = [(P["part"], S["fom"], S["fom_lim"]) for P, S in res if P["ciss"][1] is not None and P["ciss"][1] >= TI_CISS and S["fom"] < S["fom_lim"]]
    w("   every part read whose own Ciss maximum is under 5 nF sits above its limit (the nearest, %s, %s nF.mOhm on its %s against %s), so "
      "it makes no set at any count; the parts whose single Ciss maximum is at or over 5 nF (%s) make no set at all; the parts with no "
      "printed maximum give no G at any count; so no set of the parts read meets G and T together at ANY count, whatever the count's pour" %
      (lo[1], fmt(lo[0], 1), lo[2]["R_basis"].split(" (")[0].lower(), fmt(lo[2]["fom_lim"], 2), ", ".join(over)))
    for nm, fo, li in near:
        w("   %s alone sits under the limit on its favourable bound (%s against %s nF.mOhm; no hot maximum printed): the bound would not exclude "
          "a smaller die of its technology at a large count; its own die is over 5 nF" % (nm, fmt(fo, 1), fmt(li, 2)))
    w("")
    w("5. THE RECORD'S OPTIONS ON THE SAME BASIS (BUK6Y10-30P at the allowance %s mOhm)" % fmt(E["ra"] * 1e3, 3))
    for x in R["opts"]:
        w("   %s: Ciss %s nF typ at -15 V, about %s near 0 V (no maximum: G NOT SHOWN); QG(tot) max %s nC at -10 V against 50 (%s); bar %s K/W "
          "against %s (%s); held at the 40.78 bar %s A" % (x["name"], fmt(x["ciss_typ"] * 1e9, 2), fmt(x["ciss_0"] * 1e9, 2), fmt(x["qg_max"] * 1e9, 0),
                                                          "under" if x["QG_ok"] else "OVER", fmt(x["bar"]), fmt(E["bar"]),
                                                          "MEETS, CONDITIONAL on E11-29 and E11-36" if x["bar"] >= E["bar"] else "FAILS",
                                                          fmt(x["ihold"])))
    w("   GUARD: the pair's 4.72 nF is a TYPICAL at -15 V; read as a limit it would pass G; the screen refuses that reading (%s)" % guard_demo())
    w("")
    w("6. SELECTION (L4A-70; SESSION, on printed figures)")
    meets = [P["part"] for P, S in res if S["meets_all"]]
    w("   sets meeting G, T and H together: %s" % (", ".join(meets) if meets else "NONE among the %d parts read" % len(res)))
    w("   so (i)(a), the three BUK6Y10-30P, STAYS SELECTED and CONDITIONAL on E-05 (TI's answer to Q-TI-17 stated as a limit, or the bench of "
      "block E11-37), with E11-29 and E11-36 as before; E11-37 OPEN")
    w("   the fallback (ii), the pair with Q42 removed, is DRAFTED now: fallback/apply_gen_sch_a_fetpair.py (after the charger draft), read by "
      "fallback/check_fetpair_netlist.py; it is itself under 5 nF only on a TYPICAL at -15 V (CONDITIONAL on Q-TI-17 (e)) and needs the pair's "
      "%s K/W bar on the coupon (E11-29), so a negative E-05 moves the design to it without new engineering and leaves it conditional" % fmt(E["bar_pair"]))
    best = sorted([(P, S) for P, S in res if S["G"]], key=lambda ps: -ps[1]["bar"])
    w("   the best sets that meet G on printed maxima, each failing T by its bar: " +
      "; ".join("%d x %s %s K/W (%s)" % (S["n"], P["part"], fmt(S["bar"]), "allowance" if S["a"]["ra"] else "bound") for P, S in best[:4]))
    w("")
    w("7. THE UDC-1 TABLE (L4A-71; coupling HO-L, RE-10's M-A and E11-29)")
    for x in R["opts"]:
        w("   %s | FETs %d | R %s mOhm (allowance, E11-36) | gate load G NOT SHOWN (typ %s nF) | bar %s K/W | held at 40.78 %s A | HO-L: %s | "
          "M-A: %s | E11-29: %s" % (x["name"], x["n"], fmt(E["ra"] * 1e3, 3), fmt(x["ciss_typ"] * 1e9, 2), fmt(x["bar"]), fmt(x["ihold"]),
                                     "E-05" if x["n"] >= 2 else "E-05 (typical 57 %)",
                                     "holds 23.93 A at its bar, CONDITIONAL (E11-29, E11-36)" if x["bar"] >= E["bar"] else "holds 23.93 A only at %s K/W" % fmt(x["bar"]),
                                     ("the coupon at %s K/W" % fmt(x["bar"])) if x["n"] >= 2 else "a junction-to-air path at %s K/W (no pour coupon)" % fmt(x["bar"])))
    for P, S in best[:3]:
        w("   %d x %s | FETs %d | R %s mOhm (%s) | gate load G MEETS on printed maxima (at its own VDS) | bar %s K/W | held at 40.78 %s A | "
          "HO-L: Q-TI-17 (e) only | M-A: FAILS (bar) | E11-29: %s; D %s" %
          (S["n"], P["part"], S["n"], fmt(S["R_used"] * 1e3, 3), "allowance" if S["a"]["ra"] else "bound", fmt(S["bar"]),
           fmt(i_hold(E, S["n"], S["R_used"], S["a"]["tl"], E["bar"])),
           ("a pour bar %s K/W, tighter than the pair's %s" % (fmt(S["bar"]), fmt(E["bar_pair"]))) if S["n"] >= 2 else "a junction-to-air path at %s K/W, (S2)'s class" % fmt(S["bar"]),
           "MEETS" if S["dock"] else "FAILS (ISM %s A)" % fmt(P["ism"], 0)))
    w("   SESSION SELECTION: M-A first on (i)(a), CONDITIONAL on E-05, E11-29 and E11-36; M-B second, entered only on M-A's end condition "
      "(L4E11-ROUND-FET.md section 7, decision L4E11-FET-D2)")
    return "\n".join(o) + "\n"


def guard_demo():
    import copy
    p = copy.deepcopy(PARTS[0])
    try:
        limit(p["ciss"], "BUK6Y10-30P Ciss")
    except GuardError as e:
        return "GuardError: %s" % e
    raise Refused("the guard did not refuse a typical as a limit")


def main():
    try:
        R = compute()
        sys.stdout.write(report(R))
    except Refused as e:
        sys.stderr.write("l4e11_fet.py: REFUSED: %s\n" % e)
        return 3
    except GuardError as e:
        sys.stderr.write("l4e11_fet.py: GUARD: %s\n" % e)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
