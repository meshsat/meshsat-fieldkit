#!/usr/bin/env python3
"""The SOURCES.yaml entries of the two sheets stream d8dec31 filed (MESHSAT-1357, 28 September 2026; the fresh check's
item M9). The integrator runs it on v2/vendor/SOURCES.yaml, its file.

The two files are in v2/vendor/ with their sources.txt lines since bcc6f41d; this appends a `documents_filed_d8dec31`
block at the end of SOURCES.yaml in the shape of documents_filed_hc1 and documents_filed_hc3 (outside `parts:`, because
no parts entry names the fitted codes C534330 and C3685740 yet; that entry is the parts stream's and is said to be owed).
It checks each file is in the tree with the sha256 written here, asserts the marker is absent, asserts the new text
differs, re-parses the file, and refuses a second run.

Usage: apply_sources_d31.py <tree root> [--check]
"""
import hashlib, os, sys

import yaml

MARK = "documents_filed_d8dec31:"
FILES = {
    "v2/vendor/infineon/infineon-bsc039n06ns-rev2.4-c534330.pdf": "8d95c1da9c78b3afb037e1f80c3bea1ed0f874f689e3a0c96d926dafe6a437b9",
    "v2/vendor/ti/ti-tps37-snvsbj1e.pdf": "d6aed9d98fbf7f16f4dea2d6edf7c889e5fd3fa862f4072da656fb3fe7cef545",
}
BLOCK = '''
# ADDED 28 SEPTEMBER 2026 (MESHSAT-1357, the review of decision 31, worktree fnd/d8dec31). Outside `parts:` because no
# parts entry names the fitted codes yet (C534330, board E's Q1, Q4 and Q6; C3685740, board A's U34): those entries are
# the parts stream's and are owed. Part documents, read for the review's ledger (v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md
# section 8) and filed so the ledger's rows can be reproduced.
documents_filed_d8dec31:
  - for_entry: null
    role: "the ratings of board E's Q1, the N-FET the LM74700-Q1 ideal-diode controller U3 drives on the vehicle entry (also Q4 and Q6 of the panel tracker), read for finding E-F1 of the review of decision 31: VDS 60 V, 100 percent avalanche tested, EAS 50 mJ; session filing of 27 September 2026 under the owner's standing rule"
    path: "v2/vendor/infineon/infineon-bsc039n06ns-rev2.4-c534330.pdf"
    doc_id: "Infineon BSC039N06NS OptiMOS 5 Power-Transistor, 60 V, Final Data Sheet"
    revision: "Rev.2.4, 2020-02-03 (13 pages, with a text layer; Infineon's own site serves a scan with no text layer)"
    url: "https://datasheet.lcsc.com/datasheet/pdf/8e4886fa29da7cb0f19c73d556cca14b.pdf?productCode=C534330 (LCSC's copy of the maker's sheet, the pdfUrl of LCSC's product record for C534330; infineon.com was not tried by name because its file ids are not guessable)"
    fetched: "2026-09-27T21:49:31Z, curl from the runner, 1,344,705 bytes, 13 pages"
    sha256_of_the_file_read: "8d95c1da9c78b3afb037e1f80c3bea1ed0f874f689e3a0c96d926dafe6a437b9"
    filing_note: "the fitted code C534330 is gen_sch_e.py's for Q1, Q4 and Q6 (value text 'BSC039N06NS 60 V ...'); whether LCSC's C534330 is this exact part and package (PG-TDSON-8) is the parts stream's condition 1 check, not done here"
    status: VERIFIED
    matches_fitted: "the value text names the part; the code's match to the part and package is not certified here"
  - for_entry: null
    role: "the absolute maximum ratings of board A's U34 (TPS37A010122DSKR, the front end's 65 V over- and under-voltage supervisor on VIN_RAW), read for the ledger of the review of decision 31: VDD, VSENSE, VRESET -0.3 to 70 V (7.1, p.6); session filing of 27 September 2026 under the owner's standing rule"
    path: "v2/vendor/ti/ti-tps37-snvsbj1e.pdf"
    doc_id: "TI TPS37 Wide VIN 65 V Dual Channel Overvoltage and Undervoltage (OV and UV) Detector with Programmable Sense and Reset Delay Function, datasheet"
    revision: "SNVSBJ1E, October 2020, revised August 2023 (Rev. E, 44 pages)"
    url: "https://www.ti.com/lit/ds/symlink/tps37.pdf"
    fetched: "2026-09-27T21:49:20Z, curl from the runner, 3,124,179 bytes, 44 pages; the same bytes gen_sch_a.py:754 cites by sha256 d6aed9d9 from stream r4a's draft copy"
    sha256_of_the_file_read: "d6aed9d98fbf7f16f4dea2d6edf7c889e5fd3fa862f4072da656fb3fe7cef545"
    filing_note: "the fitted code C3685740 is gen_sch_a.py's for U34 (line 798); the code's match to the -DSKR suffix and the WSON-10 package is the parts stream's condition 1 check, not done here"
    status: VERIFIED
    matches_fitted: "the value text names the part; the code's match to the part and package is not certified here"
'''


def main(argv):
    if not argv: print(__doc__); return 2
    root, dry = os.path.abspath(argv[0]), "--check" in argv
    p = os.path.join(root, "v2", "vendor", "SOURCES.yaml")
    old = open(p, encoding="utf-8").read()
    if MARK in old: raise SystemExit("apply_sources_d31: already applied (its block is in the file)")
    for rel, want in FILES.items():
        fp = os.path.join(root, rel)
        if not os.path.exists(fp): raise SystemExit("apply_sources_d31: %s is not in the tree; merge the branch first" % rel)
        have = hashlib.sha256(open(fp, "rb").read()).hexdigest()
        assert have == want, "%s is %s here and this entry says %s" % (rel, have[:16], want[:16])
    new = old.rstrip("\n") + "\n" + BLOCK
    assert new != old
    d0, d1 = yaml.safe_load(old), yaml.safe_load(new)
    assert set(d1) == set(d0) | {"documents_filed_d8dec31"} and len(d1["documents_filed_d8dec31"]) == 2
    assert {x["path"] for x in d1["documents_filed_d8dec31"]} == set(FILES)
    assert all(d1[k] == d0[k] for k in d0), "another block of SOURCES.yaml moved"
    if not dry:
        with open(p, "w", encoding="utf-8") as f: f.write(new)
        yaml.safe_load(open(p, encoding="utf-8"))
    print("apply_sources_d31: documents_filed_d8dec31 with 2 entries%s" % (" (checked, not written)" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
