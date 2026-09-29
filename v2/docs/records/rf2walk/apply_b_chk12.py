#!/usr/bin/env python3
"""Stream rf2walk2 (MESHSAT-1357): DRAFT changes to board B's generator (v2/ecad/tools/gen_sch_b.py) answering the minor items
of the independent check of set 12 (`_scratch/chk-set12/CHECK.md`, minors 1, 2 and 5) that are stream d4emcon's remedies. NOT
applied by this stream: the integrator applies it, regenerates board B once on the KiCad box, and reads it back with
tools/readback_chk12.py. Every change is taken by the session under the owner's standing rule of 26 September 2026 and is
reversible by reverting the lines it writes. It runs on the generator as set 12 carries it (D4E-B applied).

M1  B-5's release level (the check's minor 1). R238 was 100 k: FULL_CARD_POWER_OFF# released rests on the RM520N-GL's own
    pull-down (Quectel HD v1.1 Table 9: "Pull down with a 100 kOhm resistor", no tolerance stated, so its tolerance is
    UNKNOWN), and 1.56 V falls under the 1.19 V VIH if that pull-down is under about 62 k. THE CHANGE: R238 49.9 k 1%, the code
    board B already carries for R297 (C23184). Held by U554: at most 3.545 V / 49.4 k = 72 uA, inside SCES308L's 100 uA row
    (VOL 0.1 V, under Quectel's 0.2 V VIL). Released: 3.135 V x 100 / (100 + 50.4) = 2.08 V at the nominal 100 k, and at or
    over 1.19 V for any module pull-down of 30.8 k or more (69 percent under nominal).
M2  B-4, U543 (the check's minor 2).
    (a) Between 1.65 V and U543's rising threshold (VIT 2.79 V +1.25 percent, VHYS at most 2.5 percent, SBVS050N: 2.90 V),
    U536 is inside its specified supply and may drive RB_IEN_DRV HIGH (EMCON released, request high), so U543 sank up to
    (2.90 - 0.40) / 2.178 k + 20 uA = 1.17 mA, over the 1 mA of its only VOL row (0.4 V). THE CHANGE: R532 2.7 k 1% (C13167):
    at most (2.90 - 0.40) / 2.673 k + 19.6 uA (the maker's divider at V_IN 5.3 V) = 0.955 mA, inside the row, so RB_IEN is at
    most 0.4 V whenever +3V3_DEV is under U543's threshold, not only in U536's 0 to 1.65 V band; and R527 20.0 k 1% (C4184),
    which keeps the released level: (2.4 V / 2.727 k + 2.457 V / 165.9 k - 5 uA) / (1 / 2.727 k + 1 / 165.9 k + 1 / 19.8 k) =
    2.10 V over the maker's 2.0 V (2.02 V had R527 stayed 15 k); asserted by EMCON at most 0.1 V + 19.6 uA x 2.727 k = 0.16 V;
    every rail lost (20.3 uA of stated leakage into 20.2 k parallel 165.9 k) 0.37 V, under the maker's 0.4 V.
    (b) A dip of +3V3_DEV under VIT held I_EN low for the dip plus td, 12 to 28 ms with CT open, and then released it while the
    request stayed high; Ground Control: "once I_EN has been driven low, the host application must wait for I_BTD to transition
    low before driving I_EN high again. Failure to follow this procedure may result in damage to the 9704 module" (hardware
    page, fetched 27 September 2026). No held document states how long the 9704 takes from I_EN low to I_BTD low, so no td can
    be shown long enough at desk. THE CHANGE: CT to VDD through R551 49.9 k 1% (SBVS050N: "a fixed 300ms typical delay time by
    tying CT to VDD; use a resistor from 40kOhm to 200kOhm"; td 180 to 420 ms, 6.6), as U221 already has with R297; at power-up
    this holds I_EN low for 180 ms or more after +3V3_DEV, which is the maker's own startup order (power first, then I_EN). THE
    BENCH ITEM, stated: E-04 measures the time from I_EN low to I_BTD low, idle and transmitting, over temperature; if it can
    exceed 180 ms, CT becomes a capacitor per SBVS050N's td equation (up to 10 s), or the panel firmware's brown-out rule holds
    RB_SW_IEN low until RB_STATUS reads low (PANEL.md), which only covers dips the panel controller sees.
M5  The intent notes (the check's minor 5). +3V3_CM2 now also feeds U554 (D4E-B B-5) and +3V3_CM3 the E22's gates and buffers
    U544 to U553 (B-3), where the rails' notes still say "nothing on the carrier draws from it beyond its own bypass network"
    (already stale at round 8: each slot's EMCON gates U{s}12 to U{s}15, and slot 2's U220, run from it; read on set 12's netlist);
    and +3V3_ZB's loads leave out R538's bleed (3.3 V / 4.653 k = 0.71 mA while the radios run) and the pull-ups R536 and R537
    (0.71 mA each while their open drain holds its line low). THE CHANGE: the loads and notes say so (1 mA per gate, the
    generous figure _3V3_LOADS uses for board B's single gates, whose ICC is at most 10 uA).

READ-BACK (after regeneration): tools/readback_chk12.py --tools v2/ecad/tools --board-dir v2/ecad/pcb-b-compute-b19/out
asserts R238 49.9k 1%, R532 2.7k 1%, R527 20.0k 1%, R551 49.9k 1% between +5V_DEV and U543 pin 4 (net RB_TD_CT), U543 pin 3
still open, and in the intent file each +3V3_CM{s}'s loads naming every logic part the netlist puts on it (U{s}12 to U{s}15,
slot 2's U220 and U554, slot 3's U544 to U553), +3V3_ZB's naming R536 to R538; the netlist otherwise must differ from set 12's only by R551 and the net RB_TD_CT (the integrator's comparator). Rows
moved: none of RF-002's (the parts sit on RB_IEN, 5G_PWROFF_n and rail notes, not on a path the walk judges); the record's
statements B-4 and B-5 become true over the whole band and for the module's unknown pull-down tolerance down to 30.8 k.

The script asserts every anchor is present exactly once, that the new text differs, re-parses the file with ast, and refuses a
second run (the marker CHK12-B already present).

usage: apply_b_chk12.py <worktree root> [--dry-run]"""
import ast, os, sys

MARK = "CHK12-B"
EDITS = []

# M1: R238 to 49.9 k 1%
A1 = ('        r(R(38), "100k 1%", "5G_PWROFF_n", a33, lcsc="C25803"); nfet(Q(7), "5G_OFF", "GND", "5G_PWROFF_n", '
      '"2N7002 expander -> FULL_CARD_POWER_OFF#")   # D4E-F2: 100 k so the held pin carries at most 36 uA (U554, SCES308L 100 uA row)\n')
EDITS.append((A1, '''        # CHK12-B M1 (stream rf2walk2, 29 September 2026, the check of set 12, minor 1): R238 49.9 k 1%, the code R297 already
        # carries. Held by U554 at most 72 uA (SCES308L's 100 uA row, VOL 0.1 V); released 2.08 V at the module's nominal
        # 100 k pull-down, whose tolerance Quectel does not state, and at or over the 1.19 V VIH down to a 30.8 k pull-down.
        r(R(38), "49.9k 1%", "5G_PWROFF_n", a33, lcsc="C23184"); nfet(Q(7), "5G_OFF", "GND", "5G_PWROFF_n", "2N7002 expander -> FULL_CARD_POWER_OFF#")
'''))
A1b = '''        # 10 k to 1 M) and U554, an SN74LVC2G07 on +3V3_CM2 (U220's rail), repeats it open-drain onto the pin, with R238 at 100 k:
        # at most 36 uA held, VOL 0.1 V (SCES308L 6.5, 100 uA row); released 1.56 V (module pull-down nominal, INFERRED). U554's
'''
EDITS.append((A1b, '''        # 10 k to 1 M) and U554, an SN74LVC2G07 on +3V3_CM2 (U220's rail), repeats it open-drain onto the pin, with R238 at 49.9 k
        # since CHK12-B M1 (100 k in D4E-B): at most 72 uA held, VOL 0.1 V (SCES308L 6.5, 100 uA row); released 2.08 V (module
        # pull-down nominal, its tolerance unstated: INFERRED). U554's
'''))

# M2: R532, R527, CT through R551
A2 = '''r("R532", "2.2k 1%", "RB_IEN_DRV", "RB_IEN", lcsc="C4190")
r("R527", "15k 1%", "RB_IEN", "GND", lcsc="C22809"); r("R528", "4.7k", "RB_SW_IEN", "GND")
ic("U543", 6, "TPS3808G30DBVR supervisor on +5V_DEV watching +3V3_DEV: holds the RockBLOCK's I_EN low below 2.79 V (L4 on U536, D4E-B)", "SOT236",
   {"1": "RB_IEN", "2": "GND", "3": "NC", "4": "NC", "5": "+3V3_DEV", "6": "+5V_DEV"}, "C189211")
'''
EDITS.append((A2, '''# CHK12-B M2 (stream rf2walk2, 29 September 2026, the check of set 12, minor 2). (a) Between 1.65 V and U543's rising threshold
# (2.90 V at most, SBVS050N VIT and VHYS) U536 may drive high while U543 holds RB_IEN: R532 2.7 k 1% keeps U543's sink at 0.955 mA
# at most, inside its 1 mA VOL row (0.4 V), so RB_IEN is low whenever +3V3_DEV is under the threshold; R527 20.0 k 1% keeps the
# released level at 2.10 V (over the maker's 2.0 V), asserted 0.16 V, every rail lost 0.37 V (under the maker's 0.4 V). (b) CT to
# VDD through R551 49.9 k 1%: td 180 to 420 ms (SBVS050N 6.6, 40 k to 200 k), so a dip holds I_EN low that long before release;
# Ground Control asks I_EN be driven high again only after I_BTD has gone low, and how long that takes is in no held document:
# bench E-04 measures it, and CT becomes a capacitor if it can exceed 180 ms. At power-up I_EN then waits 180 ms or more after
# +3V3_DEV, the maker's own startup order. Reverse: R532 2.2 k, R527 15 k 1%, U543 pin 4 open, R551 out.
r("R532", "2.7k 1%", "RB_IEN_DRV", "RB_IEN", lcsc="C13167")
r("R527", "20.0k 1%", "RB_IEN", "GND", lcsc="C4184"); r("R528", "4.7k", "RB_SW_IEN", "GND")
ic("U543", 6, "TPS3808G30DBVR supervisor on +5V_DEV watching +3V3_DEV: holds the RockBLOCK's I_EN low below 2.79 V and 180 to 420 ms after (L4 on U536, D4E-B, CHK12-B)", "SOT236",
   {"1": "RB_IEN", "2": "GND", "3": "NC", "4": "RB_TD_CT", "5": "+3V3_DEV", "6": "+5V_DEV"}, "C189211")
r("R551", "49.9k 1%", "+5V_DEV", "RB_TD_CT", lcsc="C23184")
'''))

# M5: the intent notes and loads
A5a = '''    _intent.rail("+3V3_CM%d" % _s, 3.3, 0.10, 0.20, "U3%dA" % (_s - 1), always_on=True, converted=False,
                 always_on_why="the module's OWN 3.3 V output on its receptacle: this board consumes it and cannot switch it",
                 source_ic="the module GENERATES this rail and hands it out on its receptacle: the pin IS the source",
                 loads={"U3%dA" % (_s - 1): 0.10},
                 note="slot %d's module-supplied 3.3 V. This board only decouples it and level-shifts against "
                      "it; nothing on the carrier draws from it beyond its own bypass network" % _s)
'''
EDITS.append((A5a, '''    # CHK12-B M5 (stream rf2walk2, the check of set 12, minor 5): the note "nothing on the carrier draws from it beyond its own
    # bypass network" was already stale at round 8, whose per-slot EMCON gates U{s}12 to U{s}15 (and slot 2's U220) run from the
    # module's own 3.3 V (EMCON L3); D4E-B added slot 2's U554 (B-5) and slot 3's E22 gates and buffers U544 to U553 (B-3). Read
    # from set 12's netlist. 1 mA a gate is the generous figure _3V3_LOADS uses for board B's single gates (ICC 10 uA at most).
    _cm_gates = ["U%d%02d" % (_s, _g) for _g in (12, 13, 14, 15)] + {2: ["U220", "U554"], 3: ["U%d" % _u for _u in range(544, 554)]}.get(_s, [])
    _intent.rail("+3V3_CM%d" % _s, 3.3, 0.10, 0.20, "U3%dA" % (_s - 1), always_on=True, converted=False,
                 always_on_why="the module's OWN 3.3 V output on its receptacle: this board consumes it and cannot switch it",
                 source_ic="the module GENERATES this rail and hands it out on its receptacle: the pin IS the source",
                 loads=dict([("U3%dA" % (_s - 1), 0.10)] + [(_u, 0.001) for _u in _cm_gates]),
                 note="slot %d's module-supplied 3.3 V. This board decouples it, level-shifts against it (Q%d01 to Q%d05 and "
                      "their pull-ups) and runs from it the slot's EMCON gates U%d12 to U%d15 (round 8, EMCON L3)%s; 1 mA a "
                      "gate" % (_s, _s, _s, _s, _s, {2: ", U220 (SD-EMC-1r8) and U554 (D4E-B B-5)",
                                                     3: " and the E22's gates and buffers U544 to U553 (D4E-B B-3)"}.get(_s, "")))
'''))
A5b = '''             loads={"U13": 0.04, "U14": 0.04, "J_ZBDBG1": 0.01, "J_ZBDBG2": 0.01},
             note="the two CC2652P radios behind their load switch, plus the two bench debug headers. 0.3 A "
                  "peak is both radios transmitting at once, which the fabric never asks for but the copper must carry")
'''
EDITS.append((A5b, '''             loads={"U13": 0.04, "U14": 0.04, "J_ZBDBG1": 0.01, "J_ZBDBG2": 0.01, "R538": 0.00071, "R536": 0.00071, "R537": 0.00071},
             note="the two CC2652P radios behind their load switch, plus the two bench debug headers, R538's bleed (0.71 mA) and "
                  "the RX pull-ups R536 and R537 (0.71 mA each while their open drain holds the line low; CHK12-B M5). 0.3 A "
                  "peak is both radios transmitting at once, which the fabric never asks for but the copper must carry")
'''))


def main(argv):
    if not argv or len(argv) > 2:
        print(__doc__); return 2
    dry = "--dry-run" in argv[1:]
    p = os.path.join(argv[0], "v2/ecad/tools/gen_sch_b.py")
    old = open(p, encoding="utf-8").read()
    if MARK in old:
        print("refused: %s is already in %s (a second run)" % (MARK, p)); return 1
    for a, _ in EDITS:
        n = old.count(a)
        if n != 1:
            print("refused: anchor found %d times, not once: %r" % (n, a[:100])); return 1
    new = old
    for a, b in EDITS:
        new = new.replace(a, b)
    assert new != old and MARK in new
    assert new.count('r("R551", "49.9k 1%", "+5V_DEV", "RB_TD_CT"') == 1 and new.count('"R532", "2.7k 1%"') == 1
    ast.parse(new)
    if dry:
        print("dry run: every anchor found once, the result parses; %d edits, %+d lines" % (len(EDITS), new.count("\n") - old.count("\n")))
        return 0
    open(p, "w", encoding="utf-8").write(new)
    ast.parse(open(p, encoding="utf-8").read())
    print("applied CHK12-B (M1, M2, M5) to %s; regenerate board B on the box, then tools/readback_chk12.py" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
