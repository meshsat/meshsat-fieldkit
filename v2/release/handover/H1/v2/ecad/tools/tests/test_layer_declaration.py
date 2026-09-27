#!/usr/bin/env python3
"""A board's copper layer count is a declaration, and no gate may carry it as a literal (MESHSAT-862,
16 September 2026).

Twice a measurement came back whose ONLY failure was the gate describing the previous decision: board A's
four-layer experiment on 12 September read "netlist_board 2004 of 2004, check_pcb_a 510 of 511, the one failure
being the gate asserting six layers", and board C's six-layer measurement on 16 September carried the same
shape. Under the P0 ruling of 11 September every board's layer count is open and will be measured both ways, so
a literal in a gate means a layer experiment is a source edit, and a source edit in an experiment tree is the
12 September trap (an experiment needs its own ECAD directory, not its own tools).

`boardtable.py` already existed for this and every gate imported it without using it: the import was added and
the literal was left, which is the shape worth catching, because the file then LOOKS fixed."""
import os, re, json

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LETTERS = ("a", "b", "c", "d", "e", "p")
LIT = re.compile(r"GetCopperLayerCount\(\)\s*==\s*\d")


def t_no_board_gate_carries_a_copper_layer_literal():
    for L in LETTERS:
        s = open(os.path.join(TOOLS, "check_pcb_%s.py" % L), encoding="utf-8").read()
        m = LIT.search(s)
        assert not m, "check_pcb_%s.py asserts its layer count as a literal: %r" % (L, m.group(0))


def t_every_board_gate_reads_the_declaration_it_imports():
    for L in LETTERS:
        s = open(os.path.join(TOOLS, "check_pcb_%s.py" % L), encoding="utf-8").read()
        assert "import boardtable as _bt" in s, "check_pcb_%s.py does not import the board table" % L
        assert '_bt.value("%s", "copper_layers"' % L in s, \
            "check_pcb_%s.py imports the board table and does not read its layer count from it" % L


def t_every_board_declares_the_count_its_gate_asks_for():
    for L in LETTERS:
        d = json.load(open(os.path.join(TOOLS, "boards", "%s.json" % L), encoding="utf-8"))
        n = d.get("copper_layers")
        assert isinstance(n, int) and n in (2, 4, 6), "board %s declares copper_layers %r" % (L, n)
        assert (d.get("_copper_layers_why") or "").strip(), \
            "board %s declares a layer count with no reason beside it" % L
