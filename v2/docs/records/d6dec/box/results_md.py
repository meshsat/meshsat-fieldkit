#!/usr/bin/env python3
"""The box results of stream d6dec as Markdown, for README.md (29 September 2026).

Usage: results_md.py <run dir fetched from the box> [commit] [<parity run dir> <parity commit>]
Reads tests.log, escape_parity.json and dec001_read.json of one run_box.sh run and prints the three sections. The
DEC-001 table is labelled NOT EVIDENCE: it was read outside the tree, on a branch, by dec001_read.py."""
import sys, os, json, re

CAUSE_ORDER = ["declared, not on this board (the intent is newer than the placement)", "no ruled class",
               "past the class screen, no allowance names it", "past its maker's own distance",
               "far side refused (one-sided board)", "far side refused (inside a fan)",
               "far side refused (over a through-hole part)", "far side refused (maker names the same side)",
               "a pad reaches no via or pour within 1.5 mm", "the capacitor is not on the pin's net on this board", "other"]


def main(a):
    d = a[0]; commit = a[1] if len(a) > 1 else "?"; rn = os.path.basename(os.path.normpath(d))
    L = []
    t = open(os.path.join(d, "tests.log"), encoding="utf-8", errors="replace").read()
    tot = [l for l in t.splitlines() if re.match(r"^tests: \d+ passed", l)]
    fails = [l for l in t.splitlines() if re.search(r" FAIL( |$)", l) and l.startswith("tests: ")]
    skips = [l for l in t.splitlines() if re.search(r" SKIP( |$)", l) and l.startswith("tests: ")]
    L.append("### Tests on the KiCad box at %s (`box/run_box.sh`, 33 test files in one `run.py` call)\n" % commit)
    L.append("`%s`\n" % (tot[-1] if tot else "no summary line"))
    for l in fails: L.append("- FAIL: `%s`" % l[7:220])
    for l in skips: L.append("- SKIP: `%s`" % l[7:220])
    L.append("")
    pd = a[2] if len(a) > 3 else d; pc = a[3] if len(a) > 3 else commit; prn = os.path.basename(os.path.normpath(pd))
    ep = json.load(open(os.path.join(pd, "escape_parity.json")))
    L.append("### Escape parity at %s: 73ae2f21's escape.py against this branch's, six committed boards stripped of copper\n" % pc)
    L.append("| board | same copper | vias | tracks | pads with no escape | decoupling cost line |")
    L.append("|---|---|---|---|---|---|")
    for r in ep["rows"]:
        b, n = r["before"], r["after"]
        cost = [c for c in n["cost"] if "decoupling cost:" in c and "written" not in c]
        L.append("| %s (%s) | %s | %d / %d | %d / %d | %d / %d | %s |" % (
            r["board"].upper(), r["phase"], "yes" if r["same_copper"] else "**NO**", b["vias"], n["vias"], b["tracks"],
            n["tracks"], b["no_escape"], n["no_escape"], (cost[0][len("escape: decoupling cost: "):] if cost else "none")))
    L.append("\nBefore / after in each cell. The cost lines of the new pass (per part and cause) are in "
             "`box/%s/escape_parity.log`.\n" % prn)
    dr = json.load(open(os.path.join(d, "dec001_read.json")))
    L.append("### What DEC-001 reads on each committed candidate under the new rules (NOT EVIDENCE: read outside the tree)\n")
    L.append("Read by `box/dec001_read.py` at %s on the KiCad box: each phase folder copied whole to `/root/d6dec/%s/read/`, "
             "this branch's `intent_checks.py` run there. The boards are the committed candidates (A32, B21, C24, D12, "
             "E17, P4); the intents are the committed ones (A and B regenerated in set 8), so a declaration newer than "
             "its board's placement is read as not on the board. Nothing here is a reading the registry may count.\n" % (commit, rn))
    L.append("| board | verdict | declared | pass | justified | recorded | fail | no own ground via | far side | FAIL lines by cause |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in dr["rows"]:
        c = r.get("counts") or {}
        causes = "; ".join("%s %d" % (k, r["fail_by_cause"][k]) for k in CAUSE_ORDER if r["fail_by_cause"].get(k))
        decl = None
        for s in r.get("summary") or []:
            m = re.search(r"decoupling, (\d+) declared", s)
            if m: decl = int(m.group(1))
        L.append("| %s (%s, board %s, intent %s) | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["board"].upper(), r["phase"], r["board_sha256_16"], r["intent_sha256_16"], r.get("result"), decl,
            c.get("pass"), c.get("justified"), c.get("recorded"), c.get("fail"), c.get("no_own_via"), c.get("far_side"),
            causes or "none"))
    L.append("\nThe verdict's counts are the gate's lines, one per declared entry: `pass` is the lines that did not fail "
             "less the justified and recorded ones. Every FAIL and justified line is in `box/%s/dec001_read.json`. The "
             "gate's own summary line per board:\n" % rn)
    for r in dr["rows"]:
        for s in r.get("summary") or []:
            L.append("- %s: `%s`" % (r["board"].upper(), s[:400]))
    print("\n".join(L))


if __name__ == "__main__": main(sys.argv[1:])
