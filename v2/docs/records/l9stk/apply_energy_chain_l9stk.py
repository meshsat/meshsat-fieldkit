#!/usr/bin/env python3
"""apply_energy_chain_l9stk.py: a text correction of v2/ecad/tools/pcb_energy_chain.yaml for the integrator (record l9stk, the
copper question, MESHSAT-1357; revised 4 October 2026 after the check COPPER: NOT CONFIRMED). NOT APPLIED to the tree by this
record; its author ran it only on scratch copies.

It REPLACES record l8r2's draft apply_energy_chain_e1oz.py (round 3, item 6), whose 12.26 and 2.76 mm a face rated each face
alone at an even split and left out L4-E11's 20 A on the shore input. Run it INSTEAD of l8r2's draft; if l8r2's was already
run, this one finds l8r2's texts and replaces them in turn.

What it writes (ratings, interrupting figures, every other stage and line unchanged, so energy_chain.py's coordination checks
read the same numbers):
  the conductor texts of DOCK_ENTRY, SHORE_INPUT and BOARD_A_NODE: a band's two outer faces and its adjacent return rated as
      one conductor (record l9stk's l9stk_copper.out), the widths at 1 oz and at 2 oz, the outer weight the owner's open
      decision (L9STK CU); BOARD_A_NODE no longer names an In2 plane board A does not have;
  the 25 A blade's citation in PACK_CELLS, PACK_LEAD, DOCK_ENTRY, DOCK_BLOCK, BOARD_A_NODE and BOARD_A_CONVERTERS: the Keystone
      3568 takes the Littelfuse MINI 297 or 997, so the regular ATOF sheet and its 1000 A2s give way to the MINI 297 sheet, its
      625 A2s (a nominal melting figure, no clearing guarantee) and PACK_CELLS' cold resistance 2.36 mOhm and note.

What a run checks: the decision register carries record l9stk's board A and board E decisions, each ruled at 1 oz outer as the
design input (titles carrying "(L9STK A)" and "(L9STK E)"), so the correction follows the decisions; for each edit exactly one
of its accepted old texts occurs once, or, once every new text is present and no old one is, the file is already corrected and
the run writes nothing and exits 0; the result re-parses as YAML; every stage reads back identical to the original but the
fields stated, the conductors keep their ratings and carry their widths, and no 25 A blade cites the ATOF sheet; after a write
the file is read back and parsed again.

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

# this record's texts (the revision of 4 October 2026: a band's two faces and its adjacent return rated as one conductor)
_DOCK_WHAT = ("board E's pack path on both outer faces, a band's faces and its adjacent return rated as one conductor, no inner "
              "layer counted (record l9stk section 14): 38.79 mm a band a face between through-hole ends and 39.14 mm at a one-face "
              "land at 1 oz, 19.39 and 19.57 mm at 2 oz; the outer weight is the owner's open decision (L9STK CU)")
_DOCK_BASIS = ("gen_pcb_e3.py power copper; " + OUT + " sections 2 to 5: the blades' 25 A at 10 K, decision 35's model on the "
               "combined section; dc_drop measures the copper itself on the routed board")
_SHORE_WHAT = ("board E's input bands on both outer faces, a band's faces and its adjacent return rated as one conductor (record "
               "l9stk section 14): J_DCIN to L2 and GND_V at L4-E11's 20 A, 25.78 to 26.02 mm a band a face at 1 oz and 12.89 to "
               "13.01 mm at 2 oz; the outer weight is the owner's open decision (L9STK CU)")
_SHORE_BASIS = ("gen_pcb_e3.py; " + OUT + " sections 2 to 5: decision 35's model at 10 K on the combined section; "
                "records/l4e11/l4e11_power.out section 6 (D-06) selects at least 20 A continuous from J_DCIN to F1 to the clamps")
_NODE_WHAT = ("board A's pack path on both outer faces, a band's faces and its adjacent return rated as one conductor, no inner "
              "layer counted (record l9stk section 14): 38.79 mm a band a face between through-hole ends and 39.14 mm at R17 and "
              "the battery FET pair at 1 oz, 19.39 and 19.57 mm at 2 oz; the outer weight is the owner's open decision (L9STK CU)")
_NODE_BASIS = ("gen_pcb_a3.py power copper; " + OUT + " sections 2 to 5: the blades' 25 A at 10 K, decision 35's model on the "
               "combined section; dc_drop measures the copper itself on the routed board")

NEW = {"DOCK_ENTRY": (_DOCK_WHAT, _DOCK_BASIS, "25.0"), "SHORE_INPUT": (_SHORE_WHAT, _SHORE_BASIS, "10.0"),
       "BOARD_A_NODE": (_NODE_WHAT, _NODE_BASIS, "25.0")}
WIDTHS = {"DOCK_ENTRY": ("38.79", "39.14", "19.39", "19.57"), "SHORE_INPUT": ("25.78", "26.02", "12.89", "13.01"),
          "BOARD_A_NODE": ("38.79", "39.14", "19.39", "19.57")}

# the 25 A blades' citation: the holder takes the MINI 297 or 997, not the regular ATO (the check's minor)
_MINI = "v2/vendor/keystone/littelfuse-297-ficcorp.pdf"
_MINI_BASIS = (_MINI + ", Ratings table and Time-Current Characteristics: 0297025, 1000 A interrupting at 32 VDC, 625 A2s a "
               "nominal melting figure and no clearing I2t printed; the Keystone 3568 takes the Littelfuse MINI 297 or 997, "
               "v2/vendor/keystone/M65p42.pdf")
_MINI_WHAT = "25 A MINI blade fuse, Littelfuse 0297025.WXNV (silver terminals, -40 to +125 C), in a Keystone 3568 holder"
_ATO = "v2/vendor/battery/littelfuse-287-atof.pdf"
BLADES = [
    ("PACK_CELLS",
     '   protection: {ref: F1, kind: fuse, what: "25 A ATOF blade fuse in a Keystone 3568 holder", rating_a: 25.0,\n'
     '                interrupting_a: 1000.0, i2t_a2s: 1000.0, cold_resistance_mohm: 2.52,\n'
     '                basis: "' + _ATO + ', Ratings table and Specifications"}\n',
     '   protection: {ref: F1, kind: fuse, what: "' + _MINI_WHAT + '", rating_a: 25.0,\n'
     '                interrupting_a: 1000.0, i2t_a2s: 625.0, cold_resistance_mohm: 2.36,\n'
     '                basis: "' + _MINI_BASIS + '"}\n',
     {"what": _MINI_WHAT, "i2t_a2s": 625.0, "cold_resistance_mohm": 2.36, "basis": _MINI_BASIS}),
    ("PACK_LEAD",
     '   protection: {ref: F1, what: "the pack\'s own 25 A blade, upstream", rating_a: 25.0, interrupting_a: 1000.0,\n'
     '                i2t_a2s: 1000.0, basis: "' + _ATO + '"}\n',
     '   protection: {ref: F1, what: "the pack\'s own 25 A MINI blade, upstream", rating_a: 25.0, interrupting_a: 1000.0,\n'
     '                i2t_a2s: 625.0, basis: "' + _MINI_BASIS + '"}\n',
     {"what": "the pack's own 25 A MINI blade, upstream", "i2t_a2s": 625.0, "basis": _MINI_BASIS}),
    ("DOCK_ENTRY",
     '   protection: {ref: F3, kind: fuse, what: "25 A ATOF blade fuse (Keystone 3568 holder)", rating_a: 25.0,\n'
     '                interrupting_a: 1000.0, i2t_a2s: 1000.0,\n'
     '                basis: "' + _ATO + '"}\n',
     '   protection: {ref: F3, kind: fuse, what: "' + _MINI_WHAT + '", rating_a: 25.0,\n'
     '                interrupting_a: 1000.0, i2t_a2s: 625.0,\n'
     '                basis: "' + _MINI_BASIS + '"}\n',
     {"what": _MINI_WHAT, "i2t_a2s": 625.0, "basis": _MINI_BASIS}),
    ("DOCK_BLOCK",
     '   protection: {ref: F3, what: "board E\'s 25 A blade, upstream", rating_a: 25.0, interrupting_a: 1000.0,\n'
     '                i2t_a2s: 1000.0, basis: "' + _ATO + '"}\n',
     '   protection: {ref: F3, what: "board E\'s 25 A MINI blade, upstream", rating_a: 25.0, interrupting_a: 1000.0,\n'
     '                i2t_a2s: 625.0, basis: "' + _MINI_BASIS + '"}\n',
     {"what": "board E's 25 A MINI blade, upstream", "i2t_a2s": 625.0, "basis": _MINI_BASIS}),
    ("BOARD_A_NODE",
     '   protection: {ref: F1, kind: fuse, what: "25 A ATOF blade fuse (Keystone 3568 holder): pack node to VBAT", rating_a: 25.0,\n'
     '                interrupting_a: 1000.0, i2t_a2s: 1000.0,\n'
     '                basis: "' + _ATO + '"}\n',
     '   protection: {ref: F1, kind: fuse, what: "' + _MINI_WHAT + ': pack node to VBAT", rating_a: 25.0,\n'
     '                interrupting_a: 1000.0, i2t_a2s: 625.0,\n'
     '                basis: "' + _MINI_BASIS + '"}\n',
     {"what": _MINI_WHAT + ": pack node to VBAT", "i2t_a2s": 625.0, "basis": _MINI_BASIS}),
    ("BOARD_A_CONVERTERS",
     '   protection: {ref: F1, what: "the board\'s own 25 A blade, upstream at the pack node", rating_a: 25.0,\n'
     '                interrupting_a: 1000.0, i2t_a2s: 1000.0,\n'
     '                basis: "' + _ATO + '"}\n',
     '   protection: {ref: F1, what: "the board\'s own 25 A MINI blade, upstream at the pack node", rating_a: 25.0,\n'
     '                interrupting_a: 1000.0, i2t_a2s: 625.0,\n'
     '                basis: "' + _MINI_BASIS + '"}\n',
     {"what": "the board's own 25 A MINI blade, upstream at the pack node", "i2t_a2s": 625.0, "basis": _MINI_BASIS}),
]
_NOTE_OLD = ('   note: "at the high end of the fault range the melting time from I2t is 1000/480^2 = 4.3 ms, and at the low\n'
             '     end 17 ms; the interrupting rating is 1000 A at 32 VDC against a pack that cannot exceed 16.8 V"\n')
_NOTE_TEXT = ("at the high end of the fault range the nominal melting time from the MINI's 625 A2s is 625/480^2 = 2.7 ms, and at "
              "the low end 10.9 ms; a nominal melting I2t is no clearing guarantee (no clearing I2t is printed); the interrupting "
              "rating is 1000 A at 32 VDC against a pack that cannot exceed 16.8 V")
_NOTE_NEW = '   note: "%s"\n' % _NOTE_TEXT


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
    """[(stage id, [accepted old texts], new text, {path: value} the stage reads back with)]"""
    l8 = l8r2_texts()
    out = []
    for sid, tree in (("DOCK_ENTRY", _DOCK_TREE), ("SHORE_INPUT", _SHORE_TREE), ("BOARD_A_NODE", _NODE_TREE)):
        what, basis, rating = NEW[sid]
        olds = [tree] + ([l8[sid]] if sid in l8 else [])
        out.append((sid, olds, _cond(what, rating, basis), {("conductor", "what"): what, ("conductor", "basis"): basis}))
    for sid, old_t, new_t, fields in BLADES:
        out.append((sid, [old_t], new_t, {("protection", k): v for k, v in fields.items()}))
    out.append(("PACK_CELLS", [_NOTE_OLD], _NOTE_NEW, {("note",): _NOTE_TEXT}))
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
    if all(text.count(n) == 1 for _s, _o, n, _f in E) and not any(text.count(o) for _s, olds, _n, _f in E for o in olds):
        return text, True
    new = text
    for sid, olds, rep, _f in E:
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
    want = {}
    for sid, _o, _n, fields in E:
        want.setdefault(sid, {}).update(fields)
    for sa, sb in zip(a["stages"], b["stages"]):
        exp = copy.deepcopy(sa)
        for path, v in want.get(sa.get("id"), {}).items():
            node = exp
            for k in path[:-1]:
                node = node[k]
            node[path[-1]] = v
        if sb != exp:
            refuse("%s does not read back as the old stage with only its stated fields corrected" % sa.get("id"))
        if sa.get("id") in WIDTHS:
            if float(sb["conductor"]["rating_a"]) != float(sa["conductor"]["rating_a"]):
                refuse("%s's rating moved" % sa["id"])
            if not all(w in sb["conductor"]["what"] for w in WIDTHS[sa["id"]]):
                refuse("%s does not carry its widths" % sa["id"])
        if "287-atof" in str(sb.get("protection", {}).get("basis", "")) and float(sb["protection"].get("rating_a") or 0) == 25.0:
            refuse("%s still cites the ATOF sheet for a 25 A MINI blade" % sa["id"])
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
        print("%s: ALREADY CORRECTED, nothing to write" % NAME)
        return 0
    if not write:
        print("%s: CHECK OK, %d edit(s), nothing written" % (NAME, len(edits())))
        return 0
    open(chain, "w", encoding="utf-8").write(new)
    back = open(chain, encoding="utf-8").read()
    if back != new:
        refuse("the written file does not read back as the corrected text")
    stages(back)
    print("%s: WRITTEN, %d edit(s)" % (NAME, len(edits())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
