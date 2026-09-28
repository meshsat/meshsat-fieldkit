#!/usr/bin/env python3
"""DRAFT for the integrator (stream w5si, second pass, 27 September 2026, MESHSAT-1357, layers 8 and 9): board B's RF
switch ports declared and classed as the RF lines they are, and the basis of BOB corrected. It replaces the first
pass's draft of the same name, which is filed as recovered under ../recovery/pass1-drafts/ with the suffix
.superseded-do-not-run: that draft deleted four USB pair-class patterns from gen_pcb_b3.py (see _pyedit.py).

FOUND BY THE SI-001 READING (edge_length.py with tools/pcb_edge_rates.yaml) on the committed netlist
pcb-b-compute-b19/out/pcb-b-compute.net (sha256/16 8b78c59754a6a0c7) at c23c5e76:
  1. boards/b.json declares `SW?_IN` and `SW?_O?` as CLOCKED_DIGITAL, "a voter input" and "a voter output". Every net
     those patterns match is a port of an RF switch: SWA_IN, SWB_IN (the SKY13351-378LF's common port, U82 and U83
     pin 5) and SWA_O1, SWA_O2, SWB_O1, SWB_O2 (its two throws, pins 1 and 3). No voter net carries those names.
  2. gen_pcb_b3.py's PATTERNS puts those six ports and the card RF lines (W?*_CARD) in the USB pair class instead of
     the RF class the same file defines for single-ended 50 ohm lines, and no pattern covers GNSS_RF_IN.
  3. boards/b.json declares `BOB` as CLOCKED_DIGITAL, "the break-before-make timing node of the same logic". The only
     net of that name is the common node of the wall Ethernet port's line-side (Bob Smith) termination
     (gen_sch_b.py: MCT3 and MCT4 through R9 and R10, 75 ohm, to BOB; C33, 1 nF 2 kV, from BOB to GND). The
     break-before-make nets are BBM*.

WHAT IT CHANGES, each a session decision under the owner's standing rule of 26 September 2026 (authority: SESSION):
  W5SI-D1  boards/b.json: `SW?_IN` and `SW?_O?` become HIGH_SPEED_DIGITAL, the class this table gives its other RF
           lines (*_ANT, *_RF_IN, W?A_CARD), with a basis that names the parts. gen_pcb_b3.py PATTERNS:
           ("SW?_O*", "USB"), ("SW?_IN", "USB") and ("W?*_CARD", "USB") become "RF", and ("GNSS_RF_IN", "RF") is added
           after ("*_ANT", "RF"). Why: they are single-ended 50 ohm RF lines. Reverse: restore the two entries and the
           three classes, and remove the added pattern.
  W5SI-D2  (REPLACED in the second pass) boards/b.json: `BOB` KEEPS ITS CLASS, CLOCKED_DIGITAL, and only its basis is
           corrected. The first pass moved it to LOW_SPEED_OR_DC, the class return_via.py and ref_change.py skip: that
           hid from both return rules the one node of the board whose whole purpose is to carry a return current (the
           cable's common-mode current). None of the four signal classes asks the right question of it: the three
           that are judged ask for an adjacent reference plane, and the maker's guidance for the line side of the
           magnetics is the opposite (Microchip DS00004151A 6.5: no signal ground under the magnetics, the connector
           and the area between). So the class is left as committed, which keeps the net judged and visible, its basis
           says so, and the class that fits is PROPOSED to the integrator in
           v2/docs/records/w5si/F-BOB-common-mode-termination.md. Reverse: restore the basis.

HOW IT CHANGES THEM: on the parsed structure, never on a stretch of text.
  * boards/b.json is read with json, the three entries are found by their pattern (each exactly once) and held to the
    class and basis this draft expects, the new table is written as the repository writes board tables
    (json.dumps(indent=1, ensure_ascii=False) and a newline), read back, and compared with the old one: every key
    unchanged but signal_classes, and in it every entry unchanged but the three.
  * gen_pcb_b3.py is parsed with ast, the ONE module-level assignment to PATTERNS is located, the class constant of
    each of the three tuples is replaced at the position the parser gives, the new tuple is inserted at the end of
    ("*_ANT", "RF"), and a comment goes on a line of its own above the statement. The file is parsed again and the
    evaluated PATTERNS must be the old list with exactly those changes: every other entry there, unchanged, in the
    same order (40 entries become 41). Every other statement of the module must be unchanged.
Both files are checked before either is written. A second run is refused.

Applied by the integrator on the integrated tree (after set 6), from anywhere:
    python3 v2/docs/records/w5si/apply/apply_board_b_declarations.py [--root <tree>] [--dry-run]
The effect on SI-001: none on the counts at the declared phase (the ports are covered by the interface record
RF-LINES whatever their class; BOB by CABLE-SIDE-TERMINATION). The net classes take effect at board B's next layout
generation.
"""
import os, sys, json, ast

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _pyedit as PE
import _apply as AP          # since 28 September 2026 (stream w5si2, the drafts check's M4): preconditions, and a sentence for a refusal

ROOT = AP.root_of(HERE) if "--root" not in sys.argv or sys.argv.index("--root") + 1 < len(sys.argv) else os.path.abspath(".")
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
TABLE = os.path.join(TOOLS, "boards", "b.json")
GEN = os.path.join(TOOLS, "gen_pcb_b3.py")

STAMP = "27 September 2026, stream w5si"
ENTRIES = {
    "SW?_IN": ({"class": "CLOCKED_DIGITAL", "basis": "a voter input"},
               {"class": "HIGH_SPEED_DIGITAL",
                "basis": "the common RF port of the SKY13351-378LF antenna changeovers U82 and U83 (pin 5), behind a "
                         "22 pF DC block: radio frequency, a single-ended 50 ohm line (" + STAMP + ", W5SI-D1: the "
                         "entry read 'a voter input' and no voter net carries this name)"}),
    "SW?_O?": ({"class": "CLOCKED_DIGITAL", "basis": "a voter output"},
               {"class": "HIGH_SPEED_DIGITAL",
                "basis": "the two RF throws of the SKY13351-378LF antenna changeovers U82 and U83 (pins 1 and 3), each "
                         "behind a 22 pF DC block to a card's U.FL: radio frequency, a single-ended 50 ohm line (" + STAMP +
                         ", W5SI-D1: the entry read 'a voter output' and no voter net carries this name)"}),
    "BOB": ({"class": "CLOCKED_DIGITAL", "basis": "the break-before-make timing node of the same logic"},
            {"class": "CLOCKED_DIGITAL",
             "basis": "the common node of the wall Ethernet port's line-side (Bob Smith) termination: the magnetics' "
                      "cable-side centre taps MCT3 and MCT4 through R9 and R10, 75 ohm, to this node, and C33, 1 nF "
                      "2 kV, from it to GND. It carries the cable's common-mode current and is NOT a clocked bus: no "
                      "class of this table asks the right question of it, and it is held in this one only so that the "
                      "return rules keep judging it until the class proposed in "
                      "v2/docs/records/w5si/F-BOB-common-mode-termination.md is ruled (" + STAMP + ", W5SI-D2 as "
                      "replaced: the entry read 'the break-before-make timing node', which is BBM*)"}),
}
CHANGED = {("SW?_O*", "USB"): ("SW?_O*", "RF"), ("SW?_IN", "USB"): ("SW?_IN", "RF"), ("W?*_CARD", "USB"): ("W?*_CARD", "RF")}
ADDED = [(("GNSS_RF_IN", "RF"), ("*_ANT", "RF"))]
COMMENT = ("# RF (" + STAMP + ", W5SI-D1): the SKY13351 switch ports (SW?_O*, SW?_IN), the card RF lines (W?*_CARD) and the\n"
           "# LG290P's RF input (GNSS_RF_IN) are single-ended 50 ohm lines and take the RF class; until that day the first\n"
           "# three sat in the USB pair class and GNSS_RF_IN in none.\n")


def new_table(text):
    """(new text, what changed) for boards/b.json, or an AssertionError."""
    old = json.loads(text)
    assert json.dumps(old, indent=1, ensure_ascii=False) + "\n" == text, \
        "boards/b.json is not written as the repository writes board tables, so rewriting it would change more than three entries"
    new = json.loads(text)
    done = 0
    for pat, (was, now) in ENTRIES.items():
        hits = [e for e in new["signal_classes"] if e.get("pattern") == pat]
        assert len(hits) == 1, "%d entries carry the pattern %s, expected one" % (len(hits), pat)
        e = hits[0]
        if e.get("basis") == now["basis"] and e.get("class") == now["class"]: done += 1; continue
        assert e.get("class") == was["class"] and e.get("basis") == was["basis"], \
            "the entry %s is not as this draft read it (class %r, basis %r): re-read it" % (pat, e.get("class"), e.get("basis"))
        e["class"], e["basis"] = now["class"], now["basis"]
    assert done == 0, "already applied" if done == len(ENTRIES) else "applied in part: %d of %d entries" % (done, len(ENTRIES))
    out = json.dumps(new, indent=1, ensure_ascii=False) + "\n"
    assert out != text
    back = json.loads(out)
    # every key unchanged but signal_classes, and in it every entry unchanged but the three
    why = PE.same_except(old, back, changed={"signal_classes": back["signal_classes"]})
    assert why is None, why
    assert len(back["signal_classes"]) == len(old["signal_classes"])
    for a, b in zip(old["signal_classes"], back["signal_classes"]):
        if a["pattern"] in ENTRIES:
            assert b == dict(a, **ENTRIES[a["pattern"]][1]), (a, b)
        else:
            assert a == b, "an entry that was not to change changed: %r" % (a,)
    return out


def new_generator(src):
    """The new text of gen_pcb_b3.py, or an AssertionError."""
    tree = PE.parse(src)
    stmt = PE.assignment(tree, "PATTERNS")
    assert isinstance(stmt.value, ast.List), "PATTERNS is not a list literal"
    old = [tuple(x) for x in ast.literal_eval(stmt.value)]
    assert len(set(old)) == len(old), "PATTERNS carries an entry twice"
    assert ADDED[0][0] not in old and not any(v in old for v in CHANGED.values()), "already applied"
    classes = ast.literal_eval(PE.assignment(tree, "CLASSES").value)
    assert "RF" in classes, "gen_pcb_b3.py defines no RF net class"
    edits = [(PE.line_start(src, stmt), PE.line_start(src, stmt), COMMENT)]
    seen = set()
    for el in stmt.value.elts:
        assert isinstance(el, ast.Tuple) and len(el.elts) == 2, "an entry of PATTERNS is not a pair"
        key = tuple(ast.literal_eval(el))
        if key in CHANGED:
            a, b = PE.span(src, el.elts[1])
            edits.append((a, b, json.dumps(CHANGED[key][1])))
            seen.add(key)
        for new, after in ADDED:
            if key == after:
                end = PE.span(src, el)[1]
                edits.append((end, end, ", (%s, %s)" % (json.dumps(new[0]), json.dumps(new[1]))))
                seen.add(new)
    assert seen == set(CHANGED) | {a[0] for a in ADDED}, "not every entry to change was found: %s" % sorted(set(CHANGED) - seen)
    out = PE.apply(src, edits)
    assert out != src
    tree2 = PE.parse(out)
    new = [tuple(x) for x in ast.literal_eval(PE.assignment(tree2, "PATTERNS").value)]
    why = PE.same_except(old, new, changed=CHANGED, added=ADDED)
    assert why is None, why
    assert len(new) == len(old) + len(ADDED), (len(old), len(new))
    # every entry it had before is there but the three whose class moved, and nothing else was lost
    assert not [e for e in old if e not in new and e not in CHANGED], [e for e in old if e not in new and e not in CHANGED]
    # and no other statement of the module moved
    rest = lambda t: [ast.dump(n) for n in t.body if not (isinstance(n, ast.Assign) and len(n.targets) == 1
                                                          and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "PATTERNS")]
    assert rest(tree) == rest(tree2), "a statement other than PATTERNS changed"
    return out, old, new


def main():
    # this draft needs nothing of the stream's tools: what it needs is the two files it changes, as it read them
    AP.need_files(ROOT, ["v2/ecad/tools/boards/b.json", "v2/ecad/tools/gen_pcb_b3.py"], "this draft changes it")
    t = open(TABLE, encoding="utf-8").read()
    g = open(GEN, encoding="utf-8").read()
    t2 = new_table(t)
    g2, old, new = new_generator(g)
    owed = ("\n  OWED after this draft: re-take board B's readings that read boards/b.json (it is a configuration input of every "
            "reading that declares it) with retake_gate.sh; the net classes take effect at board B's next layout generation")
    if "--dry-run" in sys.argv:
        print("dry run, nothing written: boards/b.json 3 entries; gen_pcb_b3.py PATTERNS %d entries become %d%s" % (len(old), len(new), owed))
        return 0
    AP.write(TABLE, t2)
    AP.write(GEN, g2)
    # read both back from the disk
    json.loads(open(TABLE, encoding="utf-8").read())
    back = [tuple(x) for x in ast.literal_eval(PE.assignment(PE.parse(open(GEN, encoding="utf-8").read()), "PATTERNS").value)]
    assert back == new
    print("board B: SW?_IN and SW?_O? declared RF and BOB's basis corrected (its class kept); gen_pcb_b3.py PATTERNS "
          "%d entries become %d: the switch ports and the card RF lines in class RF, GNSS_RF_IN added%s" % (len(old), len(new), owed))
    return 0


if __name__ == "__main__":
    AP.run(main)
