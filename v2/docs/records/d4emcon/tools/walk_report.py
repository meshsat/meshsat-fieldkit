#!/usr/bin/env python3
"""Stream d4emcon (MESHSAT-1357): RF-002's walk (tools/tx_inhibit.py) on a set of netlists, every result with its
whole detail, written to a directory the caller names. It writes no verdict and nothing in the tree's out/ folders:
tx_inhibit.judge() is read-only, and the output directory is an argument that must not lie under v2/ecad.

usage: walk_report.py --tools <v2/ecad/tools> --out <dir> <netlist.net>...
The board letter is read from the file name by boardtable.letter_for, as tx_inhibit.report() reads it."""
import hashlib, json, os, sys


def main(argv):
    tools, out, nets = None, None, []
    i = 0
    while i < len(argv):
        if argv[i] == "--tools": tools = argv[i + 1]; i += 2
        elif argv[i] == "--out": out = argv[i + 1]; i += 2
        else: nets.append(argv[i]); i += 1
    if not tools or not out or not nets:
        print(__doc__); return 2
    out = os.path.abspath(out)
    if "/v2/ecad/" in out + "/":
        print("refused: the output directory lies under v2/ecad"); return 2
    sys.path.insert(0, os.path.abspath(tools))
    sys.dont_write_bytecode = True
    import boardtable, tx_inhibit
    boards, shas = {}, {}
    for p in nets:
        l = (boardtable.letter_for(os.path.basename(p).replace(".net", ".kicad_pcb")) or "").upper()
        if not l:
            print("refused: no board letter for %s" % p); return 2
        boards[l] = tx_inhibit.parse_netlist(p)
        shas[l] = hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
    res = tx_inhibit.judge(boards)
    lab = {True: "PASS", False: "FAIL", None: "UNDECIDED"}
    os.makedirs(out, exist_ok=True)
    tool_sha = hashlib.sha256(open(os.path.join(tools, "tx_inhibit.py"), "rb").read()).hexdigest()[:16]
    lines = ["tx_inhibit.py sha256/16 %s" % tool_sha] + ["board %s netlist sha256/16 %s" % kv for kv in sorted(shas.items())]
    per = {}
    for r in res:
        l = "UNJUDGED" if r.get("absent") else lab[r["ok"]]
        lines.append("%s  %s  [%s]" % (l, r["text"], ",".join(r["boards"])))
        for part in (r["detail"] or "").split(" | "):
            if part: lines.append("      " + part)
        for b in r["boards"]:
            per.setdefault(b, {"PASS": 0, "FAIL": 0, "UNDECIDED": 0, "UNJUDGED": 0})[l] += 1
    lines.append("")
    for b in sorted(per):
        lines.append("board %s: FAIL %d, PASS %d, UNDECIDED %d, UNJUDGED %d" % (
            b, per[b]["FAIL"], per[b]["PASS"], per[b]["UNDECIDED"], per[b]["UNJUDGED"]))
    for k, nl in sorted(boards.items()):
        _got, stopped = tx_inhibit.reach(nl)
        for s in sorted(set(stopped)): lines.append("  %s: the walk stopped at %s (no pin map)" % (k, s))
    open(os.path.join(out, "walk-full.txt"), "w").write("\n".join(lines) + "\n")
    json.dump(dict(tool=tool_sha, netlists=shas, per_board=per,
                   results=[dict(label="UNJUDGED" if r.get("absent") else lab[r["ok"]], text=r["text"], detail=r["detail"],
                                 boards=r["boards"]) for r in res]),
              open(os.path.join(out, "walk-full.json"), "w"), indent=1, sort_keys=True)
    print("\n".join(lines[-(len(per) + 1 + 0):][:len(per) + 1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
