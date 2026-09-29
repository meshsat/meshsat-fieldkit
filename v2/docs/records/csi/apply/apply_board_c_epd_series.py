#!/usr/bin/env python3
"""Board C's four e-paper lines take a series termination at the RP2040's pins (stream csi, MESHSAT-1357, 29 September
2026; session decision CSI-D3). A DRAFT for the owner of gen_sch_c.py, applied by the integrator; nothing is regenerated.

WHAT IT CHANGES
  tools/gen_sch_c.py  U3's pins 4 to 7 (GPIO2 to GPIO5) move to EPD_SCL_R, EPD_SDA_R, EPD_DC_R and EPD_CS_R, and four
                      27R resistors join each to its line: R53 EPD_SCL, R54 EPD_SDA, R55 EPD_DC, R56 EPD_CS. The lines keep
                      their names from the resistor to J_EPD, so every far-end record and every reader of J_EPD is unchanged.
  tools/boards/c.json four signal-class entries, EPD_SCL_R, EPD_SDA_R, EPD_DC_R and EPD_CS_R (CLOCKED_DIGITAL), ahead of
                      the glob EPD_*, which is LOW_SPEED_OR_DC and would otherwise take the new nets.
WHY 27R: the value the maker series-terminates this chip's own USB pins with (hardware design guide p. 12, "these I/Os do
require 27 Ω series termination resistors"), inside SI-001's 10 to 150 ohm screen, and a part this tree already codes
(lcsc_fill.py: 27R on R_0603, C25190). Raspberry Pi publishes no GPIO output impedance, so the value cannot be computed to
a match: it is INFERRED, and the edge at J_EPD is the bring-up measurement owed.

HOW IT BEHAVES: every anchor is asserted to occur exactly once; the preconditions are checked first and a failed one
refuses in one sentence with exit code 2 (a second run is one); the new generator is parsed (ast) and its U3 map and the
four resistor calls are read back from the parse; c.json is written in its own format (indent 1) and read back.
--dry-run writes nothing. --root <tree> runs on another tree (a scratch view).
After it: regenerate board C's schematic, netlist and intent on the box, then readback_board_c_epd_series.py on the new
netlist, then SI-001 re-taken (see the stream's README)."""
import ast, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
LINES = (("4", "EPD_SCL", "R53"), ("5", "EPD_SDA", "R54"), ("6", "EPD_DC", "R55"), ("7", "EPD_CS", "R56"))
OLD_U3 = '4: "EPD_SCL", 5: "EPD_SDA", 6: "EPD_DC", 7: "EPD_CS"'
NEW_U3 = '4: "EPD_SCL_R", 5: "EPD_SDA_R", 6: "EPD_DC_R", 7: "EPD_CS_R"'
ANCHOR = 'r("R2", "27R", "USB_DP_R", "USB_PNL_P"); r("R3", "27R", "USB_DM_R", "USB_PNL_N");'
ADD = ('# THE E-PAPER LINES ARE SERIES-TERMINATED AT THE CONTROLLER (stream csi, CSI-D3, 29 September 2026, taken under the\n'
       '# owner\'s standing rule of 26 September 2026). SI-001 found EPD_SCL, EPD_SDA, EPD_DC and EPD_CS layout-bound: the RP2040 publishes no\n'
       '# edge (no IBIS model, no minimum transition) and the lines run from the cluster to J_EPD. 27R at each pin, the value the maker\n'
       '# series-terminates this chip\'s USB pins with (hardware design guide p. 12); INFERRED for a GPIO pad, the edge at J_EPD is owed\n'
       '# at bring-up. Place each within a few millimetres of U3\'s pin (the layout generator\'s item). Reverse: delete the four lines\n'
       '# below and put U3 pins 4 to 7 back on EPD_SCL, EPD_SDA, EPD_DC and EPD_CS.\n'
       'r("R53", "27R", "EPD_SCL_R", "EPD_SCL"); r("R54", "27R", "EPD_SDA_R", "EPD_SDA"); r("R55", "27R", "EPD_DC_R", "EPD_DC"); r("R56", "27R", "EPD_CS_R", "EPD_CS")\n')
BASIS = {"EPD_SCL": "the e-paper's SPI clock", "EPD_SDA": "the e-paper's SPI data (the panel answers on it in a read)",
         "EPD_DC": "the e-paper's data and command select", "EPD_CS": "the e-paper's chip select"}


def refuse(why):
    print("apply_board_c_epd_series: refused: %s" % why); sys.exit(2)


def netlist_refs(path):
    """Every component reference of a KiCad netlist, parsed from its components section."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    return set(re.findall(r'\(comp \(ref "([^"]+)"\)', txt))


def u3_map(tree):
    """U3's pin map as the generator writes it: the dict literal of the synth("U3", ...) call, read from the parse."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "synth" and node.args and \
           isinstance(node.args[0], ast.Constant) and node.args[0].value == "U3":
            return ast.literal_eval(node.args[4])
    return None


def r_calls(tree):
    """{ref: (value, net a, net b)} of every r(...) call whose arguments are literals."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "r" and len(node.args) >= 4 and \
           all(isinstance(a, ast.Constant) for a in node.args[:4]):
            out[node.args[0].value] = tuple(a.value for a in node.args[1:4])
    return out


def main(argv):
    root = os.path.abspath(argv[argv.index("--root") + 1]) if "--root" in argv else ROOT
    dry = "--dry-run" in argv
    gen = os.path.join(root, "v2", "ecad", "tools", "gen_sch_c.py")
    tab = os.path.join(root, "v2", "ecad", "tools", "boards", "c.json")
    net = os.path.join(root, "v2", "ecad", "pcb-c-display-c8", "out", "pcb-c-display.net")
    for p in (gen, tab, net):
        if not os.path.isfile(p): refuse("%s is not in the tree at %s" % (os.path.relpath(p, root), root))
    src = open(gen, encoding="utf-8").read()
    tree = ast.parse(src)
    m = u3_map(tree)
    if m is None: refuse("gen_sch_c.py has no synth(\"U3\", ...) call to read U3's pins from")
    if m.get(7) == "EPD_CS_R" or any(r in r_calls(tree) for _p, _n, r in LINES):
        refuse("gen_sch_c.py already carries the series resistors (a second run)")
    for p, n, _r in LINES:
        if m.get(int(p)) != n: refuse("U3 pin %s is on %r, not %s" % (p, m.get(int(p)), n))
    for a in (OLD_U3, ANCHOR):
        if src.count(a) != 1: refuse("the anchor %r occurs %d times in gen_sch_c.py, not once" % (a[:50], src.count(a)))
    used = netlist_refs(net) | set(r_calls(tree))
    taken = [r for _p, _n, r in LINES if r in used]
    if taken: refuse("the references %s are taken on board C" % ", ".join(taken))
    raw = open(tab, encoding="utf-8").read()
    d = json.loads(raw)
    if json.dumps(d, indent=1, ensure_ascii=False) + "\n" != raw: refuse("boards/c.json is not in the format this writes")
    pats = [e.get("pattern") for e in d.get("signal_classes") or []]
    if any(n + "_R" in pats for _p, n, _r in LINES): refuse("boards/c.json already declares the new nets")
    for n in ("EPD_DC", "EPD_*"):
        if pats.count(n) != 1: refuse("boards/c.json declares %r %d times, not once" % (n, pats.count(n)))
    if not pats.index("EPD_DC") < pats.index("EPD_*"): refuse("EPD_DC is not declared ahead of EPD_*")

    new = src.replace(OLD_U3, NEW_U3).replace(ANCHOR, ANCHOR, 1)
    i = new.index(ANCHOR); j = new.index("\n", i) + 1
    new = new[:j] + ADD + new[j:]
    assert new != src
    t2 = ast.parse(new)
    m2, rc = u3_map(t2), r_calls(t2)
    for p, n, r in LINES:
        assert m2.get(int(p)) == n + "_R", (p, m2.get(int(p)))
        assert rc.get(r) == ("27R", n + "_R", n), (r, rc.get(r))
    ins = pats.index("EPD_DC") + 1
    for k, (_p, n, _r) in enumerate(LINES):
        d["signal_classes"].insert(ins + k, {"pattern": n + "_R", "class": "CLOCKED_DIGITAL", "basis": (
            "%s between the RP2040's pin and its 27R series termination, a few millimetres; the same edges as %s "
            "(29 September 2026, stream csi, CSI-D3)" % (BASIS[n], n))})
    out = json.dumps(d, indent=1, ensure_ascii=False) + "\n"
    assert out != raw
    if dry:
        print("apply_board_c_epd_series: dry run, nothing written: U3 pins 4 to 7 to the _R nets, R53 to R56 27R, four "
              "class entries ahead of EPD_*")
        return 0
    open(gen, "w", encoding="utf-8").write(new)
    open(tab, "w", encoding="utf-8").write(out)
    t3 = ast.parse(open(gen, encoding="utf-8").read())
    assert u3_map(t3).get(7) == "EPD_CS_R" and all(r in r_calls(t3) for _p, _n, r in LINES)
    back = [e["pattern"] for e in json.load(open(tab, encoding="utf-8"))["signal_classes"]]
    assert all(back.index(n + "_R") < back.index("EPD_*") for _p, n, _r in LINES)
    print("apply_board_c_epd_series: written: gen_sch_c.py (U3 pins 4 to 7, R53 to R56 27R) and boards/c.json (four "
          "class entries). Owed: board C regenerated on the box, readback_board_c_epd_series.py on the new netlist, the "
          "four resistors placed at U3's pins by gen_pcb_c3.py, SI-001 re-taken")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
