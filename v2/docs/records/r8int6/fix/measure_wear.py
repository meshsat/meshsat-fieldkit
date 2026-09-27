#!/usr/bin/env python3
"""Where does WEAR match in a component's value: the whole text, the identity, or only the description?

Worker set6fix, MESHSAT-1357, 27 September 2026. READ ONLY: it reads the netlists `reliability.judge()` reads
(found with the tool's own `netlist_for` and the registry's `board_facts`) and the committed
`pcb_reliability.yaml`, and prints a table. It writes no verdict and nothing under `v2/ecad`.

A value in this project's netlists is written `<part identity and its properties>: <what it does in this
circuit>`. Three readings of a value are compared for every part:

  whole   WEAR searched in the whole value, which is what the tool did before the change
  first   WEAR searched before the FIRST colon followed by white space, wherever it stands
  ident   WEAR searched in `reliability.identity(value)`, the changed tool's own function: before the first
          colon followed by white space that stands outside every bracket

Usage: measure_wear.py <tools dir> --old <dir holding the unfixed reliability.py>
  The unfixed tool is `git show a76a246e:v2/ecad/tools/reliability.py`, written to a directory outside the tree.
  Both tools are then asked for their own answer on every board with every path given, so "before" and "after"
  are the tools' answers and the table beside them is this script's reading of why.
"""
import os, re, sys, fnmatch, hashlib, importlib.util


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def first_colon(v):
    m = re.search(r":\s", v or "")
    return (v or "")[:m.start()] if m else (v or "")


def sha16(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def main(argv):
    tools = os.path.abspath(argv[0])
    sys.path.insert(0, tools)
    import yaml
    import rules_lib as R
    new = load(os.path.join(tools, "reliability.py"), "rel_new")
    old = load(os.path.join(argv[argv.index("--old") + 1], "reliability.py"), "rel_old")
    assert not hasattr(old, "identity"), "the tool given as --old already carries the change"
    assert old.WEAR.pattern == new.WEAR.pattern and old.NOT_WEAR_PREFIX == new.NOT_WEAR_PREFIX, \
        "the word list or the prefix list moved, which this change does not do"
    WEAR, NOT = new.WEAR, new.NOT_WEAR_PREFIX
    ecad = os.path.dirname(tools)
    vendor = os.path.normpath(os.path.join(ecad, "..", "vendor"))
    rel = os.path.join(tools, "pcb_reliability.yaml")
    sheet = yaml.safe_load(open(rel, encoding="utf-8"))
    facts = R.board_facts()
    print("WEAR pattern    : %s" % WEAR.pattern)
    print("NOT_WEAR_PREFIX : %s (unchanged)" % (NOT,))
    print("tool before     : reliability.py sha16 %s (git show a76a246e:v2/ecad/tools/reliability.py)" % sha16(old.__file__))
    print("tool after      : reliability.py sha16 %s" % sha16(new.__file__))
    print("declared list   : pcb_reliability.yaml sha16 %s (not changed by this work)" % sha16(rel))
    print()
    keys = ("parts", "colon", "colon_in_bracket", "whole", "first", "ident", "desc_only", "excluded_prefix")
    total = dict.fromkeys(keys, 0); total["covered_before"] = total["covered_after"] = 0
    total["fails_before"] = total["fails_after"] = 0
    moved, summary = [], []
    for letter in sorted(sheet.get("boards") or {}):
        stem = (facts.get(letter) or {}).get("project")
        net = new.netlist_for(stem, ecad) if stem else None
        if not net:
            print("== board %s: no netlist in this tree (%s), so neither tool compares anything\n" % (letter.upper(), stem))
            continue
        txt = open(net, encoding="utf-8", errors="replace").read()
        parts = {r: v for r, v in re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt)}
        classes = (sheet["boards"][letter] or {}).get("classes") or []
        n = dict.fromkeys(keys, 0); n["parts"] = len(parts)
        n["colon"] = sum(1 for v in parts.values() if re.search(r":\s", v or ""))
        n["colon_in_bracket"] = sum(1 for v in parts.values() if first_colon(v) != new.identity(v))
        rows, sets = [], dict(whole=set(), first=set(), ident=set())
        for r, v in sorted(parts.items()):
            w = bool(WEAR.search(v or ""))
            f = bool(WEAR.search(first_colon(v)))
            i = bool(WEAR.search(new.identity(v)))
            if not w: continue
            pre = R.ref_prefix(r)
            if pre in NOT:
                n["excluded_prefix"] += 1
                rows.append((r, pre, w, f, i, "excluded by its prefix, before and after", v)); continue
            if w: sets["whole"].add(r)
            if f: sets["first"].add(r)
            if i: sets["ident"].add(r)
            n["whole"] += w; n["first"] += f; n["ident"] += i; n["desc_only"] += (w and not i)
            hit = [c.get("name") for c in classes if any(fnmatch.fnmatchcase(r, p) for p in (c.get("refs") or []))]
            rows.append((r, pre, w, f, i, "class: " + (", ".join(hit) if hit else "NONE"), v))
        print("== board %s  %s  sha16 %s" % (letter.upper(), os.path.relpath(net, ecad), sha16(net)))
        print("   parts %d; values with a colon and white space %d, of which the first stands inside a bracket %d"
              % (n["parts"], n["colon"], n["colon_in_bracket"]))
        print("   wear set: whole value %d, before the first colon %d, identity %d; wear word in the description only %d; "
              "excluded by prefix %d" % (n["whole"], n["first"], n["ident"], n["desc_only"], n["excluded_prefix"]))
        print("   %-12s %-12s %-5s %-5s %-5s %s" % ("ref", "prefix", "whole", "first", "ident", "class, then the value"))
        for r, pre, w, f, i, cl, v in rows:
            print("   %-12s %-12s %-5s %-5s %-5s %s" % (r, pre, "yes" if w else "-", "yes" if f else "-",
                                                       "yes" if i else "-", cl))
            print("   %-12s value: %s" % ("", v))
        before = old.judge(rel, ecad, letter, vendor)[letter]
        after = new.judge(rel, ecad, letter, vendor)[letter]
        print("   tool before: covered %d, fails %d" % (before["covered"], len(before["fails"])))
        for x in before["fails"]: print("     before FAIL %s" % x)
        print("   tool after : covered %d, fails %d, set aside as description only: %s"
              % (after["covered"], len(after["fails"]), ", ".join(after["prose_only"]) or "none"))
        for x in after["fails"]: print("     after  FAIL %s" % x)
        for x in after["notes"]: print("     after  note %s" % x)
        assert sorted(sets["whole"] - sets["ident"]) == after["prose_only"], "the table and the tool disagree"
        for r in sorted(sets["whole"] - sets["ident"]): moved.append((letter.upper(), r, "leaves", parts[r]))
        for r in sorted(sets["ident"] - sets["whole"]): moved.append((letter.upper(), r, "enters", parts[r]))
        summary.append((letter.upper(), len(sets["whole"]), len(sets["ident"]), before["covered"], len(before["fails"]),
                        after["covered"], len(after["fails"]), sorted(sets["first"] ^ sets["ident"])))
        for k in keys: total[k] += n[k]
        total["covered_before"] += before["covered"]; total["covered_after"] += after["covered"]
        total["fails_before"] += len(before["fails"]); total["fails_after"] += len(after["fails"])
        print()
    print("== SUMMARY")
    print("   %-5s %-11s %-11s %-15s %-13s %-14s %-12s %s" % ("board", "wear before", "wear after", "covered before",
          "fails before", "covered after", "fails after", "first-colon and identity readings differ on"))
    for b, wb, wa, cb, fb, ca, fa, diff in summary:
        print("   %-5s %-11d %-11d %-15d %-13d %-14d %-12d %s" % (b, wb, wa, cb, fb, ca, fa, ", ".join(diff) or "none"))
    print("   set: parts %(parts)d; values with a colon %(colon)d, first colon inside a bracket %(colon_in_bracket)d; "
          "wear set whole value %(whole)d, identity %(ident)d; excluded by prefix %(excluded_prefix)d" % total)
    print("   covered, summed over the boards (the committed test asks for at least 100): before %(covered_before)d "
          "with %(fails_before)d refusal(s), after %(covered_after)d with %(fails_after)d refusal(s)" % total)
    print()
    print("== PARTS WHOSE MEMBERSHIP CHANGES: %d" % len(moved))
    for b, r, how, v in moved:
        print("   %s %-6s %s the wear set" % (b, r, how))
        print("      value: %s" % v)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
