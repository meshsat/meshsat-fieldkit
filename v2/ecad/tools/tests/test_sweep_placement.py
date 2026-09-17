#!/usr/bin/env python3
"""The sweep judges the placement rule on the pre-route board, never on the routed one (18 September 2026).

Sweeps 24 to 27 ran `place_audit` on whatever board the phase directory holds, which for a cut board is the
ROUTED board: the router had covered escapes and the closers pruned dangling ones, so the predictor read 19
collisions on B21 where its placed board read 10, and the sweep's fetch wrote that over the carried reading.
Each phase directory now carries its proved pre-route snapshot (`routed/<stem>-preroute.kicad_pcb`), the sweep
runs the predictor on it in its own out dir, and `carry_placed` proves the snapshot's footprints are the routed
board's before the verdict is written as this board's."""
import os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ECAD = os.path.dirname(TOOLS)


def _src(name):
    return open(os.path.join(TOOLS, name), encoding="utf-8").read()


def t_the_sweep_runs_the_predictor_on_the_pre_route_snapshot_and_carries_it():
    s = _src("gate_sweep.sh")
    i = s.find('routed/$N-preroute.kicad_pcb')
    assert i > 0, "gate_sweep.sh does not look for the pre-route snapshot beside the board"
    blk = s[i:i + 900]
    assert "place_audit.py out/pre/$N-preroute.kicad_pcb" in blk, "the predictor is not run on the snapshot"
    assert "carry_placed.py out/pre/$N-preroute.kicad_pcb $N.kicad_pcb" in blk, \
        "the snapshot's reading is not proved to belong to the routed board before it is carried"
    assert "--verdicts place_audit" in blk, "carry_placed would carry more than the placement reading from the snapshot's out dir"
    assert re.search(r"else\s*\n\s*run \"placement predictor\" python3 \$T/place_audit.py \$N.kicad_pcb", blk), \
        "with no snapshot the predictor must still run on the board (and decline it if routed)"


def t_every_cut_board_directory_carries_its_pre_route_snapshot():
    """A board whose phase directory holds a routed board and no snapshot cannot have PLC-001 judged by a sweep."""
    missing = []
    for d in sorted(os.listdir(ECAD)):
        p = os.path.join(ECAD, d)
        if not (d.startswith("pcb-") and os.path.isdir(p) and re.search(r"-[a-z]+\d+$", d)): continue
        boards = [f for f in os.listdir(p) if f.endswith(".kicad_pcb")]
        if len(boards) != 1: continue
        stem = boards[0][:-len(".kicad_pcb")]
        if not os.path.exists(os.path.join(p, "routed", stem + "-preroute.kicad_pcb")): missing.append(d)
    assert not missing, "these phase directories hold a board and no pre-route snapshot: %s" % missing
