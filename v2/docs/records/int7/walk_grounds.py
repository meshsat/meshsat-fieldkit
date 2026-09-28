#!/usr/bin/env python3
"""Every ground RF-002's walk names for every row it leaves UNDECIDED, read from the walk itself (MESHSAT-1357, 28
September 2026; the method change after two fresh checks of the set 6 integration found CON-010's dependency items
incomplete, v2/docs/records/int7/CHECK.md finding B-1 and CHECK-2.md finding R-1: both times the items had been written
from a summary of the readings, and the readings carry one line per row where the walk's report carries every ground).

It runs tx_inhibit.judge IN MEMORY on the netlists the filed reading inhibit_chain_d records (by path, checked by
sha256/16), writes nothing in the tree unless --write is given (then only walk-grounds.txt beside this file), and gives
for each undecided row: its text, its boards, the parts its undecided grounds name (`refs`: every U or Q designator in
the report from its first UNDECIDED on) and the report itself, part by part. apply_check2_answers.py asserts that every
part of `refs` of every undecided row on a record's allocated boards is named in an open item the record waits on.

Usage, from anywhere: python3 walk_grounds.py [--write]"""
import hashlib, json, os, re, subprocess, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
E = os.path.join(TOP, "v2/ecad"); T = os.path.join(E, "tools")
READING = "pcb-d-aprs-d9/routed/inhibit_chain_d.verdict.json"


def sha16(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def rows():
    """[{text, boards, refs, parts}] for every row the walk reads UNDECIDED, with the netlists it read."""
    sys.path.insert(0, T)
    import tx_inhibit as tx
    r = json.load(open(os.path.join(E, READING), encoding="utf-8"))
    boards, nets = {}, {}
    for k, v in sorted(r["inputs"].items()):
        if not k.startswith("netlist_"): continue
        p = os.path.join(E, v["path"])
        if sha16(p) != v["sha256_16"]: raise SystemExit("walk_grounds: %s is %s, the reading recorded %s" % (v["path"], sha16(p), v["sha256_16"]))
        boards[k[-1].upper()] = tx.parse_netlist(p); nets[k[-1].upper()] = (v["path"], v["sha256_16"])
    out = []
    for x in tx.judge(boards):
        if x.get("absent") or x["ok"] is not None: continue
        d = x["detail"] or ""
        i = d.find("UNDECIDED")
        refs = sorted(set(re.findall(r"\b([UQ]\d+)\b", d[i:] if i >= 0 else "")), key=lambda s: (s[0], int(s[1:])))
        out.append({"text": x["text"], "boards": list(x["boards"]), "refs": refs, "parts": d.split("; ")})
    return out, nets, sha16(os.path.join(T, "tx_inhibit.py"))


def report():
    rs, nets, tool = rows()
    L = ["RF-002's walk: every row it reads UNDECIDED on the set 6 netlists, with every ground its own report names.",
         "Written by v2/docs/records/int7/walk_grounds.py from tx_inhibit.judge (tx_inhibit.py sha256/16 %s), in memory." % tool,
         "Prototype design: no board built or measured; a desk reading of netlists and of the makers' documents the walk cites.",
         "Netlists (as the filed reading inhibit_chain_d records them): " + "; ".join("%s %s %s" % (k, p, s) for k, (p, s) in sorted(nets.items())),
         "%d undecided row(s)." % len(rs), ""]
    for x in rs:
        L += ["ROW: %s" % x["text"], "  boards: %s" % ", ".join(x["boards"]), "  parts its undecided grounds name: %s" % ", ".join(x["refs"])]
        L += ["  - " + p for p in x["parts"]] + [""]
    return "\n".join(L)


if __name__ == "__main__":
    t = report()
    if "--write" in sys.argv[1:]:
        open(os.path.join(HERE, "walk-grounds.txt"), "w", encoding="utf-8").write(t)
        print("walk_grounds: wrote walk-grounds.txt (%d bytes)" % len(t.encode("utf-8")))
    else: print(t)
