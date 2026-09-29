#!/usr/bin/env python3
"""Stream rf2walk3 (MESHSAT-1357): a DRAFT follow-up to apply_b_chk12.py for board B's generator, answering the re-check of set
12's minor 2 (`_scratch/chk-set12/CHECK-2.md`). It runs on gen_sch_b.py as fnd/int13 carries it at dd7230a7 (CHK12-B applied);
NOT applied by this stream. The integrator applies it with CHK12-B's regeneration of board B (one regeneration for both) and
reads it back with tools/readback_chk12.py, which now also checks these loads. Taken by the session under the owner's standing
rule of 26 September 2026; reversible by reverting the lines it writes.

THE ITEM. CHK12-B's M5 note says each module rail "level-shifts against it (Q{s}01 to Q{s}05 and their pull-ups)". Q{s}01 is not
a level shifter: it is the BC857 that buffers the module's LED_nPWR, its emitter on +3V3_CM{s} (pin 2), feeding the red power LED
through R{s}50 (1 k) (set 12's netlist: Q101 pins 1 Q1B, 2 +3V3_CM1, 3 Q1C; R150 from Q1C to LED_PWR_A1); and R{s}48 (1 k) feeds
the green ACT LED from the rail into the module's LED_nACT. Neither is in the rail's loads, which name U parts only.
THE CHANGE. The note says what Q{s}01 and R{s}48 do, and the loads name them at 3.3 mA each: the rail over 1 k with no LED drop
taken, an upper bound that needs no LED sheet (the forward drop only lowers it). Slot 3's loads then sum to 0.121 A against the
rail's 0.20 A peak.

READ-BACK (after regeneration): tools/readback_chk12.py --tools v2/ecad/tools --board-dir v2/ecad/pcb-b-compute-b19/out: its
check "+3V3_CM{s} loads name Q{s}01 and R{s}48" (added by this stream) must PASS with the rest. No RF-002 row moves.

The script asserts its anchor is present exactly once, that the new text differs, re-parses the file with ast, and refuses a
second run (the marker CHK12-LED already present).

usage: apply_b_chk12_led.py <worktree root> [--dry-run]"""
import ast, os, sys

MARK = "CHK12-LED"
A = '''                 loads=dict([("U3%dA" % (_s - 1), 0.10)] + [(_u, 0.001) for _u in _cm_gates]),
                 note="slot %d's module-supplied 3.3 V. This board decouples it, level-shifts against it (Q%d01 to Q%d05 and "
                      "their pull-ups) and runs from it the slot's EMCON gates U%d12 to U%d15 (round 8, EMCON L3)%s; 1 mA a "
                      "gate" % (_s, _s, _s, _s, _s, {2: ", U220 (SD-EMC-1r8) and U554 (D4E-B B-5)",
                                                     3: " and the E22's gates and buffers U544 to U553 (D4E-B B-3)"}.get(_s, "")))
'''
B = '''                 # CHK12-LED (stream rf2walk3, the re-check of set 12, minor 2): Q{s}01 is the BC857 buffering LED_nPWR into the
                 # red power LED through R{s}50 (1 k), its emitter on this rail, and R{s}48 (1 k) feeds the green ACT LED from it;
                 # each at most 3.3 mA (the rail over 1 k, no LED drop taken).
                 loads=dict([("U3%dA" % (_s - 1), 0.10)] + [(_u, 0.001) for _u in _cm_gates]
                            + [("Q%d01" % _s, 0.0033), ("R%d48" % _s, 0.0033)]),
                 note="slot %d's module-supplied 3.3 V. This board decouples it, level-shifts against it (Q%d02 to Q%d05 and "
                      "their pull-ups), runs the power LED from it through the BC857 buffer Q%d01 and R%d50 (1 k) and the ACT "
                      "LED through R%d48 (1 k), at most 3.3 mA each, and runs from it the slot's EMCON gates U%d12 to U%d15 "
                      "(round 8, EMCON L3)%s; 1 mA a gate" % (_s, _s, _s, _s, _s, _s, _s, _s,
                                                              {2: ", U220 (SD-EMC-1r8) and U554 (D4E-B B-5)",
                                                               3: " and the E22's gates and buffers U544 to U553 (D4E-B B-3)"}.get(_s, "")))
'''


def main(argv):
    if not argv or len(argv) > 2:
        print(__doc__); return 2
    dry = "--dry-run" in argv[1:]
    p = os.path.join(argv[0], "v2/ecad/tools/gen_sch_b.py")
    old = open(p, encoding="utf-8").read()
    if MARK in old:
        print("refused: %s is already in %s (a second run)" % (MARK, p)); return 1
    if "CHK12-B" not in old:
        print("refused: %s does not carry CHK12-B (apply_b_chk12.py), which this follows" % p); return 1
    n = old.count(A)
    if n != 1:
        print("refused: anchor found %d times, not once" % n); return 1
    new = old.replace(A, B)
    assert new != old and MARK in new
    ast.parse(new)
    if dry:
        print("dry run: the anchor found once, the result parses; %+d lines" % (new.count("\n") - old.count("\n"))); return 0
    open(p, "w", encoding="utf-8").write(new)
    ast.parse(open(p, encoding="utf-8").read())
    print("applied CHK12-LED to %s; regenerate board B with CHK12-B's regeneration, then tools/readback_chk12.py" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
