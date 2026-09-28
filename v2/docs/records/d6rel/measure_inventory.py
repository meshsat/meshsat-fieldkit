#!/usr/bin/env python3
"""The inventory of REL-001 on the seven artefacts of the set 6 candidate, before and after the list of 28 September.

Worker d6rel, MESHSAT-1357, 28 September 2026. READ ONLY: it reads the tree's declared-phase netlists (board E5's
board file) through the repaired tool's own inventory, and two lists: the list of 16 September as it stood at
73ae2f21 (given with --old, written outside the tree) and the tree's own. It writes no verdict and nothing under
v2/ecad. No board has been built: these are readings of netlists and of a board file.

BEFORE = the population the repaired inventory finds, disposed against the OLD list's classes by their reference
patterns alone (the old list had no exclusions and no lands): what the old classes would have covered had the
inventory been the population. The old TOOL's own reading is a different number (its population was the twelve
words; v2/docs/records/r8int6/fix/wear-before-after.txt has it: 111 covered, 0 refused) and is quoted for contrast.
AFTER = the repaired tool's reading with the tree's list (`reliability.judge`).

Usage: measure_inventory.py <tools dir> --old <dir holding the old pcb_reliability.yaml>
"""
import os, sys, fnmatch, hashlib


def sha16(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def main(argv):
    tools = os.path.abspath(argv[0])
    sys.path.insert(0, tools)
    import yaml
    import reliability as REL, wear_inventory as WI, phase_artefacts as PA
    old_p = os.path.join(argv[argv.index("--old") + 1], "pcb_reliability.yaml")
    old = yaml.safe_load(open(old_p, encoding="utf-8"))
    new = yaml.safe_load(open(REL.REL, encoding="utf-8"))
    assert "inventory" not in old and "inventory" in new, "the old list is the one before the inventory"
    print("old list  : %s sha16 %s (git show 73ae2f21:v2/ecad/tools/pcb_reliability.yaml)" % (old_p, sha16(old_p)))
    print("new list  : %s sha16 %s" % (os.path.relpath(REL.REL, os.path.dirname(os.path.dirname(tools))), sha16(REL.REL)))
    print("tool      : reliability.py sha16 %s, wear_inventory.py sha16 %s"
          % (sha16(REL.__file__), sha16(WI.__file__)))
    print()
    after = REL.judge()
    summary = []
    for letter in PA.letters():
        kind, path = WI.artefact(letter)
        parts, raw = WI.read(kind, path)
        L = letter.upper()
        rel = os.path.relpath(path, os.path.dirname(tools))
        print("== board %s  %s %s  sha16 %s  %d part(s)" % (L, kind.replace("_", " "), rel, hashlib.sha256(raw).hexdigest()[:16], len(parts)))
        found = WI.candidates(parts, new["inventory"], (REL.WEAR, REL.NOT_WEAR_PREFIX, REL.identity))
        cand = found["candidates"]
        how = found["how"]
        print("   candidates %d: by reference class %d, by a mechanical land %d, by an undeclared land %d, by no land %d, "
              "by the word net %d, undeclared class %d" % (len(cand), how["reference_class"], how["land"], how["land_undeclared"],
                                                          how["no_land"], how["words"], how["undeclared_class"]))
        old_classes = ((old.get("boards") or {}).get(letter) or {}).get("classes") or []
        b_classed = b_refused = 0
        b_refused_refs = []
        for r in sorted(cand):
            hits = [c for c in old_classes if any(fnmatch.fnmatchcase(r, p) for p in (c.get("refs") or []))]
            if len(hits) == 1: b_classed += 1
            else: b_refused += 1; b_refused_refs.append(r)
        a = after[letter]
        print("   BEFORE (the old list's %d class(es) over the inventory): classed %d, excluded 0, refused %d"
              % (len(old_classes), b_classed, b_refused))
        print("   AFTER  (the new list's %d class(es) and %d exclusion(s)): classed %d, excluded %d, refused %d; result %s"
              % (a["classes"], a["exclusions"], a["covered"], a["excluded"], a["refused"], a["result"]))
        for x in a["excluded_by"]:
            print("      excluded %d: %s: %s" % (len(x["parts"]), ", ".join(x["parts"]), x["reason"]))
        for w in a["inconclusive"]: print("      owed: %s" % w[:200])
        if found["prose_only"]:
            print("   set aside, a wear word in the description only: %s" % ", ".join(found["prose_only"]))
        print("   refused BEFORE (%d): %s" % (b_refused, ", ".join(b_refused_refs) if b_refused_refs else "none"))
        print("   THE INVENTORY (ref, pins, land, disposition, value):")
        for row in a["inventory"]:
            print("     %-12s %3d  %-58s %s: %s" % (row["ref"], row["pins"], row["footprint"] or "(no land)",
                                                   row["disposition"] + (" " + str(row["by"])[:40] if row["disposition"] != "refused" else ""),
                                                   row["value"][:90]))
        summary.append((L, len(cand), b_classed, b_refused, a["covered"], a["excluded"], a["refused"], a["result"]))
        print()
    print("== SUMMARY  (candidates; BEFORE classed / refused; AFTER classed / excluded / refused; result)")
    for row in summary: print("   %-3s %4d   %4d / %4d   %4d / %4d / %4d   %s" % row)
    t = [sum(r[i] for r in summary) for i in range(1, 7)]
    print("   set %4d   %4d / %4d   %4d / %4d / %4d" % tuple(t))
    print("   the old TOOL's own reading of the same netlists (its population the twelve words): 111 covered, 0 refused "
          "(v2/docs/records/r8int6/fix/wear-before-after.txt, 27 September 2026)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
