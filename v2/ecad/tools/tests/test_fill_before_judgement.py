#!/usr/bin/env python3
"""Every judgement of the copper runs on a board whose zones were just filled (MESHSAT-862, 13 Sep 2026).

`finish.sh` refilled once, after the stub router. Between that and the judgements, four stages change copper:
`stub_accept` removes closures, `stitch_prune` removes vias and its revert COPIES BACK a board that was never
filled, `direct_close` lays track, and `quality_pass` merges segments (108 out of A26, 146 out of C11). A pour
fills differently after every one of them, so the routed-board gate and `dc_drop` were reading a fill from
several steps earlier.

Measured on E8: the finish read `CELL_F pour F.Cu 122 mm2` and refused the rail for a conductor at ratio 1.04;
the same board refilled reads 163 mm2 and the rail MET. That is the whole finding: a verdict off a stale fill
is not a verdict about the board being cut.
"""
import os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIN = open(os.path.join(TOOLS, "finish.sh")).read()


def _pos(needle):
    i = FIN.find(needle)
    assert i >= 0, "finish.sh no longer contains %r" % needle
    return i


def t_the_board_is_refilled_after_the_last_stage_that_changes_copper():
    fill = [m.start() for m in re.finditer(r"ZONE_FILLER", FIN)]
    assert len(fill) >= 2, "only one refill in the finish: the stages after it change copper"
    assert max(fill) > _pos("quality_pass.sh"), "the last refill runs before the quality pass, which merges segments"


def t_the_refill_comes_before_the_routed_board_gate():
    assert max(m.start() for m in re.finditer(r"ZONE_FILLER", FIN)) < _pos("--label 'routed-board gate'")


def t_the_refill_comes_before_dc_drop_and_the_board_gate():
    last = max(m.start() for m in re.finditer(r"ZONE_FILLER", FIN))
    assert last < _pos("dc_drop.py $N.kicad_pcb"), "dc_drop reads a fill older than the copper it judges"
    assert last < _pos("check_pcb_$L.py $N.kicad_pcb"), "the board gate reads a fill older than the copper it judges"


def t_the_stub_router_refill_is_still_there():
    assert "zones refilled after the stub router" in FIN, "the closing via would be read against a stale fill again"
