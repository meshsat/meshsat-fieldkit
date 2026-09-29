#!/usr/bin/env python3
"""scan_vendor.py: which held PDFs print each part number board C's identities name (MESHSAT-1357, stream
w5identc round 3, 29 September 2026). Reads the text layer of every PDF under v2/vendor once (pdftotext -layout, the
tool's reader), searches each part number by part_identities.names_part (letter case aside, alphanumeric boundaries),
and for each hit the pages that print it. Writes readings/vendor-scan-unresolved.json. Pages without a text layer are
not read. Usage: scan_vendor.py [--out PATH]"""
import glob, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "v2", "ecad", "tools"))
import part_identities as PI   # noqa: E402
sys.path.insert(0, HERE)
from verdict import opt        # noqa: E402

EXTRA = ["MC-09-530-Q", "FH34SRJ-24S-0.5SH", "5636ADKB", "M2044SD3A01", "ABM8-272", "GRM188R61E475KE11",
         "0603B103K500NT", "0402CG150J500NT", "CS03W5F470LT5E", "ATNR4010100MT", "BAT54W", "GZ1608D601TF",
         "19-217/GHC-YR1S2/6T", "BH254VS-26P", "U-174/U", "1282.5004"]


def main(argv):
    out = opt(argv, "--out") or os.path.join(HERE, "readings", "vendor-scan-unresolved.json")
    # a FIXED list, independent of the table's states (round 4's check, minor 3: the list was the table's UNRESOLVED
    # part numbers, so the reading changed when a selection resolved): every part number stream w5ident's board C
    # identities and this stream's DECISIONS name, and EXTRA
    import build_table as B
    carried = json.load(open(os.path.join(HERE, "w5ident-board-c-identities.json")))
    mpns = sorted({x["identity"]["mpn"] for x in carried["board_c"] if x["identity"].get("mpn")}
                  | {d["mpn"] for d in B.DECISIONS.values() if d.get("mpn")} | set(EXTRA))
    pdfs = sorted(glob.glob(os.path.join(REPO, "v2", "vendor", "**", "*.pdf"), recursive=True))
    hits = {m: [] for m in mpns}
    unread = []
    for p in pdfs:
        r = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True, timeout=300)
        if r.returncode != 0 or not r.stdout.strip(): unread.append(os.path.relpath(p, REPO)); continue
        for m in mpns:
            if PI.names_part(r.stdout, m)[0]:
                hits[m].append(dict(document=os.path.relpath(p, REPO), sha256=PI.sha256(p), pages=PI.find_pages(p, m, limit=3)))
    doc = dict(what="every PDF under v2/vendor read by its text layer for each part number stream w5ident's board C identities and this stream's DECISIONS name, and a few named in the values (a fixed list, so the reading replays while the vendor tree does not change)",
               pdfs_read=len(pdfs) - len(unread), pdfs_without_text=unread, part_numbers=hits)
    json.dump(doc, open(out, "w"), indent=1, sort_keys=True)
    print("scan_vendor: %d PDFs read, %d without a text layer, %d part numbers, %d with a hit" % (len(pdfs) - len(unread), len(unread), len(mpns), sum(1 for v in hits.values() if v)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
