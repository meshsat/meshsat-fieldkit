#!/usr/bin/env python3
"""apply_energy_chain_l9stk.py: a text correction of v2/ecad/tools/pcb_energy_chain.yaml for the integrator (record l9stk, the
copper question, MESHSAT-1357, 4 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies.

It REPLACES record l8r2's draft apply_energy_chain_e1oz.py (round 3, item 6). That draft rewrote two board E conductors to 1 oz
with 12.26 mm on each of two faces for DOCK_ENTRY and 2.76 mm for SHORE_INPUT, both on an assumed even split; record l9stk's
l9stk_copper.out derives the split (section 3): an even split holds only between two through-hole ends, a band that ends at a
one-face part carries more on that part's face, and the shore input carries L4-E11's 20 A from J_DCIN to the clamps (its
section 6, D-06), not the fuse's 10 A alone. This draft writes the derived widths, and it also corrects BOARD_A_NODE, whose
text still names an In2 plane that record l9stk's board A decision does not have. Run it INSTEAD of l8r2's draft; if l8r2's
was already run, this one finds l8r2's texts and replaces them in turn.

The three conductors it writes (ratings, protective elements, every other stage and line unchanged, so energy_chain.py's
coordination checks read the same numbers; whether the copper as laid meets the widths is dc_drop's on the routed board):
  DOCK_ENTRY    board E's pack path, 1 oz on both faces: CELL+ 12.26 mm a face (through-hole ends), CELL_F 14.60 mm a face with
                a transfer field at P_CP, the return the same
  SHORE_INPUT   board E's input bands, 1 oz on both faces: 20 A to the clamps (8.15 mm a face between through-hole ends, 9.70 mm
                with a field), 10 A behind R19 (3.15 mm a face with a field, or 8.15 mm on one face)
  BOARD_A_NODE  board A's pack path, 1 oz on both faces, no inner layer counted: CELL+ 12.26 mm a face, CELL_FUSED and the VBAT
                trunk 14.60 mm a face with a field at R17 and at the battery FET pair, the return the same

What a run checks: the decision register carries record l9stk's board A and board E decisions, each ruled at 1 oz outer (titles
carrying "(L9STK A)" and "(L9STK E)"), so the correction follows the decisions and never comes before them; for each stage
exactly one of its accepted old texts occurs once (the tree's, or for DOCK_ENTRY and SHORE_INPUT l8r2's corrected one), or,
once every new text is present and no old one is, the file is already corrected: nothing is written and the run exits 0, so a
second run is a no-op; the result re-parses as YAML; every stage reads back identical to the original but the three conductors'
`what` and `basis`, which read back as written with their ratings unchanged and no "2 oz"; after a write the file is read back
and parsed again.

Usage:  apply_energy_chain_l9stk.py [--chain PATH] [--registry PATH] [--check | --write]
Exit 0: checked, written, or already corrected; 3: refused."""
import copy
import importlib.util
import os
import sys

import yaml

NAME = "apply_energy_chain_l9stk"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
CHAIN = os.path.join(REPO, "v2", "ecad", "tools", "pcb_energy_chain.yaml")
REGISTRY = os.path.join(REPO, "v2", "ecad", "tools", "pcb_decisions.yaml")
L8R2 = os.path.join(REPO, "v2", "docs", "records", "l8r2", "apply_energy_chain_e1oz.py")
MARKS = ("(L9STK A)", "(L9STK E)")
OUT = "records/l9stk/l9stk_copper.out"


def _cond(what, rating, basis):
    return '   conductor: {what: "%s", rating_a: %s,\n               basis: "%s"}\n' % (what, rating, basis)


# the tree's texts
_DOCK_TREE = ('   conductor: {what: "board E\'s 2 oz power bands to the dock block pads", rating_a: 25.0,\n'
              '               basis: "gen_pcb_e3.py bands; IPC-2221 at 2 oz"}\n')
_SHORE_TREE = '   conductor: {what: "board E\'s input bands at 2 oz", rating_a: 10.0, basis: "gen_pcb_e3.py"}\n'
_NODE_TREE = ('   conductor: {what: "board A\'s VBAT bands and In2 plane at 1 oz outer and 0.5 oz inner", rating_a: 25.0,\n'
              '               basis: "gen_pcb_a3.py power copper; dc_drop measures the copper itself on the routed board"}\n')

# this record's texts
_DOCK_WHAT = ("board E's pack path at 1 oz on both outer faces, no inner layer counted (record l9stk): CELL+ from J_BATT to F3 "
              "12.26 mm a face, CELL_F from F3 to P_CP 14.60 mm a face with a transfer field at P_CP, the return the same")
_DOCK_BASIS = ("gen_pcb_e3.py power copper; " + OUT + " sections 3 to 5: the blade's 25 A at 10 K (decision 35's model, "
               "track_current.width_for_current) with the faces' split derived from the band's resistance and its transfer "
               "barrels, at most 0.55 on a one-face part's face; dc_drop measures the copper itself on the routed board")
_SHORE_WHAT = ("board E's input bands at 1 oz on both outer faces (record l9stk): DC_IN, DC_F, DC_P and GND_V at L4-E11's 20 A "
               "to the clamps, 8.15 mm a face between through-hole ends and 9.70 mm with a transfer field; HS_S and DC_HS at "
               "F1's 10 A, 3.15 mm a face with a field or 8.15 mm on one face")
_SHORE_BASIS = ("gen_pcb_e3.py; " + OUT + " sections 3 to 5: decision 35's model at 10 K with the faces' split derived; "
                "records/l4e11/l4e11_power.out section 6 (D-06) selects at least 20 A continuous from J_DCIN to F1 to the clamps")
_NODE_WHAT = ("board A's pack path at 1 oz on both outer faces, no inner layer counted (record l9stk): CELL+ from the dock pins "
              "to F1 12.26 mm a face, CELL_FUSED and the VBAT trunk 14.60 mm a face with a transfer field at R17 and at the "
              "battery FET pair, the return the same")
_NODE_BASIS = ("gen_pcb_a3.py power copper; " + OUT + " sections 3 to 5: the blade's 25 A at 10 K (decision 35's model) with "
               "the faces' split derived, at most 0.55 on a one-face part's face; dc_drop measures the copper itself on the "
               "routed board")

NEW = {"DOCK_ENTRY": (_DOCK_WHAT, _DOCK_BASIS, "25.0"), "SHORE_INPUT": (_SHORE_WHAT, _SHORE_BASIS, "10.0"),
       "BOARD_A_NODE": (_NODE_WHAT, _NODE_BASIS, "25.0")}
WIDTHS = {"DOCK_ENTRY": ("12.26", "14.60"), "SHORE_INPUT": ("8.15", "9.70", "3.15"), "BOARD_A_NODE": ("12.26", "14.60")}


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def l8r2_texts():
    """{stage id: l8r2's corrected conductor text}, read from its draft when the tree carries it, else {}."""
    if not os.path.isfile(L8R2):
        return {}
    sp = importlib.util.spec_from_file_location("apply_energy_chain_e1oz_for_l9stk", L8R2)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return {sid: new for sid, _old, new, _w, _b in m.EDITS}


def edits():
    """[(stage id, [accepted old texts], new text, what, basis)]"""
    l8 = l8r2_texts()
    out = []
    for sid, tree in (("DOCK_ENTRY", _DOCK_TREE), ("SHORE_INPUT", _SHORE_TREE), ("BOARD_A_NODE", _NODE_TREE)):
        what, basis, rating = NEW[sid]
        olds = [tree] + ([l8[sid]] if sid in l8 else [])
        out.append((sid, olds, _cond(what, rating, basis), what, basis))
    return out


def decided(registry):
    d = yaml.safe_load(open(registry, encoding="utf-8"))
    for mark in MARKS:
        hits = [x for x in (d or {}).get("decisions") or [] if mark in str(x.get("title", ""))]
        if len(hits) != 1:
            refuse("the register carries %d decisions marked %s, not one: record l9stk's decisions are not integrated, and this "
                   "correction follows them" % (len(hits), mark))
        if str(hits[0].get("status")) != "ruled" or "1 oz outer" not in str(hits[0].get("title")):
            refuse("the decision marked %s is not ruled at 1 oz outer" % mark)


def stages(text):
    d = yaml.safe_load(text)
    if not isinstance(d, dict) or not isinstance(d.get("stages"), list):
        refuse("the chain does not parse to a mapping with a stages list")
    return d


def patched(text):
    """(new text, already corrected?)"""
    E = edits()
    if all(text.count(n) == 1 for _s, _o, n, _w, _b in E) and not any(text.count(o) for _s, olds, _n, _w, _b in E for o in olds):
        return text, True
    new = text
    for sid, olds, rep, _w, _b in E:
        if rep in olds:
            refuse("%s: an edit's new text equals an old text" % sid)
        found = [o for o in olds if new.count(o)]
        if len(found) != 1 or new.count(found[0]) != 1:
            refuse("%s: the accepted old texts occur %s times, not exactly one of them once" % (sid, [new.count(o) for o in olds]))
        if new.count(rep):
            refuse("%s: the new text is already present beside an old one" % sid)
        new = new.replace(found[0], rep)
    if new == text:
        refuse("the result does not differ")
    a, b = stages(text), stages(new)
    if {k: v for k, v in a.items() if k != "stages"} != {k: v for k, v in b.items() if k != "stages"}:
        refuse("a top-level entry other than the stages changed")
    if [s.get("id") for s in a["stages"]] != [s.get("id") for s in b["stages"]]:
        refuse("the stages' order or ids changed")
    want = {sid: (w, bs) for sid, _o, _n, w, bs in E}
    for sa, sb in zip(a["stages"], b["stages"]):
        if sa.get("id") in want:
            exp = copy.deepcopy(sa)
            exp["conductor"]["what"], exp["conductor"]["basis"] = want[sa["id"]]
            if sb != exp:
                refuse("%s does not read back as the old stage with its conductor's what and basis corrected" % sa["id"])
            if "2 oz" in str(sb["conductor"]) or float(sb["conductor"]["rating_a"]) != float(sa["conductor"]["rating_a"]):
                refuse("%s still names 2 oz or its rating moved" % sa["id"])
            if not all(w in sb["conductor"]["what"] for w in WIDTHS[sa["id"]]):
                refuse("%s does not carry its widths" % sa["id"])
        elif sb != sa:
            refuse("stage %s changed, and only DOCK_ENTRY's, SHORE_INPUT's and BOARD_A_NODE's conductors may" % sa.get("id"))
    return new, False


def main(argv):
    flags = [a for a in argv if a in ("--check", "--write")]
    chain = CHAIN if "--chain" not in argv else argv[argv.index("--chain") + 1]
    registry = REGISTRY if "--registry" not in argv else argv[argv.index("--registry") + 1]
    known = {"--check", "--write", "--chain", "--registry", chain, registry}
    if len(flags) > 1 or any(a not in known for a in argv):
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    write = flags == ["--write"]
    decided(registry)
    text = open(chain, encoding="utf-8").read()
    new, done = patched(text)
    if done:
        print("%s: ALREADY CORRECTED, nothing to write (DOCK_ENTRY, SHORE_INPUT, BOARD_A_NODE)" % NAME)
        return 0
    if not write:
        print("%s: CHECK OK, 3 edit(s), nothing written" % NAME)
        return 0
    open(chain, "w", encoding="utf-8").write(new)
    back = open(chain, encoding="utf-8").read()
    if back != new:
        refuse("the written file does not read back as the corrected text")
    stages(back)
    print("%s: WRITTEN, 3 edit(s)" % NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
