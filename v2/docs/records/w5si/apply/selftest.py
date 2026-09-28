#!/usr/bin/env python3
"""The self-test of this stream's apply scripts (stream w5si, second pass, 27 September 2026, MESHSAT-1357). Run by
hand; it builds its fixtures in a temporary directory and writes nowhere else.

It holds three things:
  1. THE DEFECT OF THE FIRST DRAFT IS CAUGHT. The first draft's text replacement is applied to a fixture generator as
     it was written (its old text was a PREFIX of the PATTERNS line and its new text ended in a '#' comment). The file
     still parses, the text still differs, and four entries are gone. _pyedit.same_except names them.
  2. THE NEW DRAFT CHANGES EXACTLY WHAT IT SAYS on the same fixture: every entry kept, three classes moved, one
     entry added, no other statement touched; and a second run is refused.
  3. EDITS ARE MADE AT BYTE POSITIONS, so a line that carries a character of more than one byte before the node is
     edited in the right place.

Usage: selftest.py        exit 1 on a failure
"""
import os, sys, ast, json, tempfile, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _pyedit as PE

GEN = '''# a fixture of gen_pcb_b3.py: the statements around PATTERNS, and PATTERNS on one long line and two short ones
CLASSES = {"USB": (0.127, 0.127), "RF": (0.18, 0.14),   # 50 Ω on the outer layers
           "PWR": (0.127, 0.4)}
PATTERNS = [("*_ANT", "RF"), ("USB*", "USB"), ("MUX*", "USB"), ("SW?_O*", "USB"), ("SW?_IN", "USB"), ("W?*_CARD", "USB"), ("GNSS_D*", "USB"), ("ZBA_D*", "USB"), ("ZBB_D*", "USB"), ("RB_D*", "USB"),
            ("PCIE*", "USB"),   # Ω: a character of two bytes ahead of the next entries
            ("+5V_*", "PWR"), ("GND", "PWR")]
PATTERNS += [("/" + pat, cls_) for pat, cls_ in PATTERNS if not pat.startswith("/")]
print(len(PATTERNS))
'''
# the first draft's replacement, as it was written (shortened to the fixture's entries)
G_OLD = '''PATTERNS = [("*_ANT", "RF"), ("USB*", "USB"), ("MUX*", "USB"), ("SW?_O*", "USB"), ("SW?_IN", "USB"), ("W?*_CARD", "USB"),'''
G_NEW = '''PATTERNS = [("*_ANT", "RF"), ("GNSS_RF_IN", "RF"), ("USB*", "USB"), ("MUX*", "USB"), ("SW?_O*", "RF"), ("SW?_IN", "RF"), ("W?*_CARD", "RF"),   # the RF switch ports are single-ended 50 ohm lines'''
TABLE = {"name": "pcb-b-compute", "signal_classes": [
    {"pattern": "SW?_IN", "class": "CLOCKED_DIGITAL", "basis": "a voter input"},
    {"pattern": "SW?_O?", "class": "CLOCKED_DIGITAL", "basis": "a voter output"},
    {"pattern": "BOB", "class": "CLOCKED_DIGITAL", "basis": "the break-before-make timing node of the same logic"},
    {"pattern": "BBM*", "class": "CLOCKED_DIGITAL", "basis": "a bank's break-before-make logic"}]}


def patterns(src):
    return [tuple(x) for x in ast.literal_eval(PE.assignment(PE.parse(src), "PATTERNS").value)]


def main():
    bad = []
    def check(ok, what):
        print("%s %s" % ("ok  " if ok else "FAIL", what))
        if not ok: bad.append(what)

    # 1. the first draft's defect
    old = patterns(GEN)
    assert GEN.count(G_OLD) == 1
    broken = GEN.replace(G_OLD, G_NEW)
    ast.parse(broken)                                   # it still parses
    check(broken != GEN and len(patterns(broken)) == len(old) - 3,
          "the first draft's replacement parses, differs, and takes %d entries to %d" % (len(old), len(patterns(broken))))
    import apply_board_b_declarations as B
    why = PE.same_except(old, patterns(broken), changed=B.CHANGED, added=B.ADDED)
    lost = [e for e in old if e not in patterns(broken) and e not in B.CHANGED]
    check(why is not None and sorted(lost) == sorted([("GNSS_D*", "USB"), ("ZBA_D*", "USB"), ("ZBB_D*", "USB"), ("RB_D*", "USB")]),
          "same_except refuses it and the four USB pair classes are named as lost: %s" % lost)

    # 2. the new draft on the same fixture, through its own entry point
    d = tempfile.mkdtemp(prefix="w5si-selftest-")
    tools = os.path.join(d, "v2", "ecad", "tools")
    os.makedirs(os.path.join(tools, "boards"))
    open(os.path.join(tools, "gen_pcb_b3.py"), "w", encoding="utf-8").write(GEN)
    open(os.path.join(tools, "boards", "b.json"), "w", encoding="utf-8").write(json.dumps(TABLE, indent=1, ensure_ascii=False) + "\n")
    run = lambda *a: subprocess.run([sys.executable, os.path.join(HERE, "apply_board_b_declarations.py"), "--root", d] + list(a),
                                    capture_output=True, text=True)
    r = run("--dry-run")
    check(r.returncode == 0 and open(os.path.join(tools, "gen_pcb_b3.py"), encoding="utf-8").read() == GEN, "a dry run writes nothing")
    r = run()
    new_src = open(os.path.join(tools, "gen_pcb_b3.py"), encoding="utf-8").read()
    new = patterns(new_src)
    check(r.returncode == 0 and len(new) == len(old) + 1, "the new draft takes %d entries to %d" % (len(old), len(new)))
    check(all(e in new for e in old if e not in B.CHANGED), "every entry that was not to change is still there")
    check(all(v in new for v in B.CHANGED.values()) and ("GNSS_RF_IN", "RF") in new and new.index(("GNSS_RF_IN", "RF")) == new.index(("*_ANT", "RF")) + 1,
          "the three classes moved and the new entry follows *_ANT")
    rest = lambda src: [ast.dump(n) for n in ast.parse(src).body if not (isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "PATTERNS")]
    check(rest(new_src) == rest(GEN), "no other statement changed")
    check("# Ω: a character of two bytes" in new_src and '("PCIE*", "USB"),   # Ω' in new_src, "the comment inside the list and the two-byte character are where they were")
    t = json.load(open(os.path.join(tools, "boards", "b.json"), encoding="utf-8"))
    ents = {e["pattern"]: e for e in t["signal_classes"]}
    check(ents["BOB"]["class"] == "CLOCKED_DIGITAL" and "Bob Smith" in ents["BOB"]["basis"] and ents["BBM*"] == TABLE["signal_classes"][3]
          and ents["SW?_IN"]["class"] == "HIGH_SPEED_DIGITAL", "the table: BOB keeps its class and gets its basis, the RF ports move, BBM* is untouched")
    r = run()
    check(r.returncode != 0 and "already applied" in r.stderr, "a second run is refused")

    # 3. byte positions
    src = 'A = ["Ω", ("x", "USB")]\n'
    el = PE.assignment(PE.parse(src), "A").value.elts[1].elts[1]
    a, b = PE.span(src, el)
    check(PE.apply(src, [(a, b, '"RF"')]) == 'A = ["Ω", ("x", "RF")]\n', "an edit after a two-byte character lands on its node")
    print("%d failure(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
