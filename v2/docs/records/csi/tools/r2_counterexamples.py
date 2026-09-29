#!/usr/bin/env python3
"""The re-check's R2-B1 counterexamples on board C's committed edge_allow entries, under a given edge_length.py (stream
csi, 29 September 2026). Each case keeps every citation true (the rows are real lines of the cited files, at their
sha256/16), so only the method of tying max_mm to its reference lengths can refuse it. Run it with the tools of the
round 2 tool (6605f3f6) and of this round: the first holds every case, the second refuses every one.
Usage: r2_counterexamples.py <tools dir> [<repository root>]"""
import hashlib, os, sys

tools = os.path.abspath(sys.argv[1])
repo = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.abspath(os.path.join(tools, "..", "..", ".."))
sys.path.insert(0, tools)
import edge_length as E
import json

allow = {e["pattern"]: e for e in json.load(open(os.path.join(tools, "boards", "c.json"), encoding="utf-8"))["edge_allow"]}
tpd = E.worst_delay("c")[0]
LST = "v2/docs/records/csi/readings/minimal-layout-lengths.txt"
OTHER = "v2/docs/records/csi/readings/si001-c-decl.txt"          # a second document with a "<token> <x> mm" line
s16 = lambda p: hashlib.sha256(open(os.path.join(repo, p), "rb").read()).hexdigest()[:16]
row = lambda doc, q, where: {"document": doc, "sha256_16": s16(doc), "where": where, "quote": q}
xr, sc = allow["XOUT_R"], allow["QSPI_SCLK"]
tpd_row = next(c for c in xr["checked"] if "t_pd" in c["quote"])
cases = [
    ("XOUT_R with SWCLK's row of the same listing, max_mm 20.1 (its own limit 2.1)",
     dict(xr, max_mm=20.1, checked=xr["checked"] + [row(LST, "SWCLK 25.92 mm", "the line of the net SWCLK")])),
    ("XOUT_R with an unrelated \"extent 572.0 mm\" of another document, max_mm 445",
     dict(xr, max_mm=445.0, checked=xr["checked"] + [row(OTHER, "extent 572.0 mm", "the reading's first line")])),
    ("QSPI_SCLK on QSPI_SD1's row, max_mm 13.1 (the first round's own error)",
     dict(sc, max_mm=13.1, checked=[row(LST, "QSPI_SD1 16.85 mm", "the line of the net QSPI_SD1"), tpd_row])),
]
print("== the %s edge_length.py, board C's committed entries, board C's slowest delay %.3f ps/mm" % (
    "tree's" if os.path.abspath(tools).startswith(repo + os.sep) else "given", tpd))
for words, e in cases:
    why = E.allow_refusal(e, tpd) or E._quotes_hold(e, repo)
    print("  %-8s %s%s" % ("REFUSED" if why else "HELD", words, (": " + why) if why else ""))
# THE FOURTH CASE, rows from two documents: no second file of the tree quotes XOUT's length, so it is made in a scratch
# repository: XOUT_R's own length row from one file and its delay row from another, both true of their files; only the
# citations of the rows are held there (the entry's own document is the tree's, asked above)
import tempfile
tmp = tempfile.mkdtemp(prefix="csi-r2-")
for name, text in (("a.txt", "   XOUT          2.76 mm\n"), ("b.txt", "   reference t_pd 5.572 ps/mm\n")):
    os.makedirs(os.path.join(tmp, "v2", "fix"), exist_ok=True)
    open(os.path.join(tmp, "v2", "fix", name), "w").write(text)
two = [{"document": "v2/fix/a.txt", "sha256_16": hashlib.sha256(open(os.path.join(tmp, "v2/fix/a.txt"), "rb").read()).hexdigest()[:16],
        "where": "the line", "quote": "XOUT 2.76 mm"},
       {"document": "v2/fix/b.txt", "sha256_16": hashlib.sha256(open(os.path.join(tmp, "v2/fix/b.txt"), "rb").read()).hexdigest()[:16],
        "where": "the line", "quote": "reference t_pd 5.572 ps/mm"}]
e = dict(xr, checked=two)
why = E.allow_refusal(e, tpd) or E._quotes_hold({"checked": two}, tmp)
print("  %-8s %s%s" % ("REFUSED" if why else "HELD", "XOUT_R's length row and delay row from two documents",
                       (": " + why) if why else ""))
