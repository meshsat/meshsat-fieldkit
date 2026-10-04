#!/usr/bin/env python3
"""apply_gen_sch_a_dd7.py: DRAFT for board A's generator owner (task L4-E11, MESHSAT-1357, round 9, 4 October 2026; record l9stk's
DD-7). NOT APPLIED to the tree by L4-E11; its author ran it only on scratch copies (the tests write scratch copies).

Why (L4E11-SOURCE-ONLY-AND-ENTRY.md section 19h, l4e11_power.out section 19h): record l9stk (branch fnd/l9stk at 0d72880b, 15.4b)
selects the latch-off LM5069-1 for board P's breaker. After a trip it stays off until its UVLO or its VIN cycles; on battery the kit
goes dark. When an input returns, the charger could push charge current through the latched breaker's body diodes (E-14). Board A
therefore opens the breaker's enable loop for a pulse when an input appears and the pack's terminal is dead: the second inverter on
board P pulls UVLO at once (C_U drains in 1.10 ms behind it), the latch resets, and when the loop closes the RC hold (0.110 to 0.907 s,
later while record l9stk's C-1c holds a hot pad) and the dv/dt start (at most 40.7 ms) restart the breaker, its timer re-enabled (under
0.3 V within 34.0 ms) long before. A later latch with the input still present gets no second pulse: the hardware charge inhibit
below holds the charge off the latched FET whenever the latch takes CELL+ dead (the checker's B-R2). Its reach (section 19h): a latch
while a source holds VSYS, and so CELL+ through the battery FETs, into a resistive fault never takes CELL+ dead, and the breaker's PGD
reads high with reverse current; that case stays OPEN for board P's gate state or a reverse-blocking element (route R1) or a hardware
charge-current cap on board A (route R2).

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else (after record l8p's apply_gen_sch_a_ptc.py, which draws the loop's two
nets DOCK_EN_OUT and DOCK_EN_RET and RT1 on this board):
  Q44     2N7002 (C8545), drain on DOCK_EN_RET, source GND: while on, it pulls the loop's return low, which opens the loop as an
          undocking does (record l9stk's C2: a short of the return to ground holds the breaker off, the fail-safe direction).
  R106    1M (C22935) from VIN_RAW to DD7_G, Q44's gate, and D25 BZT52C12-7-F (C124196) clamping it under 12.7 V: an input on the
          dock turns Q44 on.
  Q45     2N7002, gate FE_RUN (U34's two RESET outputs), drain DD7_G: the pulse ends when U34 releases the front end, 79 to 201 ms
          after VIN_RAW passes its UV threshold (CTR2's C212), so the pulse is time-limited by the existing supervisor.
  Q46     2N7002, gate DD7_ALIVE (CELL+ over R107 100k and R108 100k), drain DD7_G: while the pack's terminal is alive (the breaker
          on) no pulse forms, so an input arriving while the kit runs on its pack never drops the pack.
  Q47-Q49 THE HARDWARE CHARGE INHIBIT (the checker's B-R2 on record l9stk's recheck: a second latch with the input still present gets
          no second pulse): Q47 (2N7002, gate SYS_INH_G = DOCK_EN_OUT over R109 1M and R144 1M) turns Q49 (AO3401A, C15127) on through
          R82 100k and R83 200k, and Q49 holds CH_BATDRV, the battery FETs' gates, at VBAT, so Q39, Q40 and Q42 are off and no charge
          leaves VSYS for the pack; Q48 (2N7002, gate DD7_ALIVE) releases it once CELL+ is alive. The inhibit acts exactly while the
          enable loop is powered (the cells reach board P's breaker) and the pack's terminal is dead (the breaker off): no firmware;
          not set by a latch that leaves CELL+ held up from VSYS (its reach, section 19h).
  intent  DD7_G, DD7_ALIVE, SYS_INH_G, SYS_INH_D and SYS_INH_P declared as nodes; one schematic section for the thirteen parts and D25.
The designators Q44 to Q49, R82, R83, R106 to R109, R144 and D25 are free in gen_sch_a.py and disjoint from every board A draft composed
in L4-E9's order with record l8p's PTC draft (the resistors sit below every draft's reference, so d8dec31's next-free reference is
unchanged). It needs this record's charger draft (CH_BATDRV and the three battery FETs) and refuses a target without it.

ORDER: AFTER record l8p's apply_gen_sch_a_ptc.py (it refuses a target without DOCK_EN_RET), released with l8p's three drafts and this
record's charger draft; the charger-side hold until the restart is the firmware's (IF-7, E11-44).

Usage:  apply_gen_sch_a_dd7.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or net is in
use, record l8p's loop is not drawn, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_dd7"
ADDS = ("Q44", "Q45", "Q46", "R106", "R107", "R108", "D25", "Q47", "Q48", "Q49", "R82", "R83", "R109", "R144")
NETS = ("DD7_G", "DD7_ALIVE", "SYS_INH_G", "SYS_INH_D", "SYS_INH_P")
REQUIRES = ('part("RT1", "Device", "Thermistor_PTC"', '_intent.node("DOCK_EN_RET", ', '"4": "FE_RUN", "5": "FE_RUN"',
            'nfet(_qb, "BUK6Y10-30PX 30 V P-FET', '"21": "CH_BATDRV", "22": "VBAT"')

_ANCHOR_MAIN = ("# --- main power control LTC2954-1 (ltc2954.pdf): the panel MAIN button, EN to every converter's enable (RAIL_EN), "
                "INT = shutdown request, KILL from the panel controller through Q1\n")
_RESET = (
    '# L4-E11 ROUND 9 (MESHSAT-1357, 4 October 2026; record l9stk 15.4b, DD-7): THE PACK BREAKER\'S INPUT-RETURN RESET. Board P\'s breaker is\n'
    '# the latch-off LM5069-1: after a trip it stays off until its UVLO or VIN cycles. When an input appears on the dock while the pack\'s\n'
    '# terminal is dead, Q44 pulls the enable loop\'s return (DOCK_EN_RET) low, as an undocking opens the loop: board P\'s second inverter\n'
    '# pulls UVLO at once (C_U drains within 1.10 ms), the latch resets, and its timer falls under 0.3 V within 34.0 ms. The pulse\n'
    '# begins as VIN_RAW rises (R106 into Q44\'s gate, D25 clamping it) and ends when U34 releases FE_RUN, 79 to 201 ms after VIN_RAW\n'
    '# passes U34\'s UV threshold (Q45). Q46 holds the gate low while CELL+ is alive (the breaker on), so an input arriving while the kit\n'
    '# runs on its pack never opens the loop. When the loop closes the RC hold (0.110 to 0.907 s, later while C-1c holds a hot pad) and\n'
    '# the dv/dt start (at most 40.7 ms) restart the breaker. A Q44 shorted holds the breaker off (fail-safe, revealed at commissioning); a Q46 open lets an input\'s arrival\n'
    '# drop a live pack for the pulse and the restart (found by E11-45 b). The charge until the restart is held by the inhibit below; IF-7 reports.\n'
    'part("Q44", "Transistor_FET", "2N7002", "2N7002: DD7_G high = the breaker\'s enable loop opened at board A (1 G, 2 S, 3 D)", "SOT23", {"1": "DD7_G", "2": "GND", "3": "DOCK_EN_RET"}, "C8545")\n'
    'r("R106", "1M", "VIN_RAW", "DD7_G", lcsc="C22935"); part("D25", "Device", "D_Zener", "BZT52C12-7-F zener, the input-return reset\'s gate clamp", "SOD123", {"1": "DD7_G", "2": "GND"}, "C124196")\n'
    'part("Q45", "Transistor_FET", "2N7002", "2N7002: FE_RUN high = the input-return pulse ended (1 G, 2 S, 3 D)", "SOT23", {"1": "FE_RUN", "2": "GND", "3": "DD7_G"}, "C8545")\n'
    'part("Q46", "Transistor_FET", "2N7002", "2N7002: the pack\'s terminal alive = no input-return pulse (1 G, 2 S, 3 D)", "SOT23", {"1": "DD7_ALIVE", "2": "GND", "3": "DD7_G"}, "C8545")\n'
    'r("R107", "100k", "CELL+", "DD7_ALIVE", lcsc="C25803"); r("R108", "100k", "DD7_ALIVE", "GND", lcsc="C25803")   # CELL+ over two: 4.5 V at 9 V, 14.6 V at 29.2 V\n'
    '_intent.node("DD7_G", 12.7, "L4-E11 round 9 (DD-7): Q44\'s gate, VIN_RAW through R106 1M clamped by D25 (BZT52C12, 11.4 to 12.7 V, DS18004)")\n'
    '_intent.node("DD7_ALIVE", 14.6, "L4-E11 round 9 (DD-7): Q46\'s gate, CELL+ over R107 / R108 (half of it): 14.6 V at the SMCJ18A\'s 29.2 V clamp", v_work=8.4)\n'
    '# L4-E11 ROUND 9 (the checker\'s B-R2 of record l9stk\'s recheck): THE HARDWARE CHARGE INHIBIT. The input-return pulse restarts the\n'
    '# breaker once; a persistent fault latches it again with the input still present, and no second pulse comes. So, with no firmware,\n'
    '# charging is blocked whenever the enable loop is powered (DOCK_EN_OUT alive: the pack\'s cells reach board P\'s breaker, BRK_VIN)\n'
    '# while the pack\'s terminal is dead (CELL+ under Q48\'s threshold): the breaker is then off (latched, holding or starting), and a\n'
    '# charge could only pass its FET\'s body diodes. Q47 (gate DOCK_EN_OUT over R109 / R144, half of it) turns Q49 (AO3401A) on, which\n'
    '# holds the battery FETs\' gates CH_BATDRV at VBAT: Q39, Q40 and Q42 are off, their body diodes point from the pack to VSYS, so no\n'
    '# charge current can leave VSYS for the pack while the source keeps carrying the kit. BATDRV meanwhile sinks at most 11.5 V over its\n'
    '# 3 kOhm least RBATDRV_ON (SLUSE65A, at most 3.8 mA; Q-TI-17 asks TI). Q48 (gate DD7_ALIVE) releases it once CELL+ is alive. With\n'
    '# the loop unpowered (the gauge\'s FETs off, the pack absent or undocked) nothing is inhibited: a pack\'s wake and its precharge pass\n'
    '# the body diodes at the gauge\'s own current, as record l9stk states. Q49 shorted holds the battery FETs off (their body diodes carry\n'
    '# the discharge, and record l8p\'s PTC trips the breaker before their junctions pass 150 C); Q47 or Q49 open loses the inhibit (E11-45).\n'
    '# Its reach (L4-E11 19h): a latch while a source holds VSYS, and CELL+ through the battery FETs, into a resistive fault never takes\n'
    '# CELL+ dead, and the breaker\'s PGD reads high with reverse current: that case is OPEN (routes R1 on board P, R2 a charge cap here).\n'
    'r("R109", "1M", "DOCK_EN_OUT", "SYS_INH_G", lcsc="C22935"); r("R144", "1M", "SYS_INH_G", "GND", lcsc="C22935")   # the loop\'s 2 MOhm sense: half of DOCK_EN_OUT\n'
    'part("Q47", "Transistor_FET", "2N7002", "2N7002: the enable loop powered and the terminal dead = the charge inhibited (1 G, 2 S, 3 D)", "SOT23", {"1": "SYS_INH_G", "2": "GND", "3": "SYS_INH_D"}, "C8545")\n'
    'part("Q48", "Transistor_FET", "2N7002", "2N7002: the pack\'s terminal alive = the charge inhibit released (1 G, 2 S, 3 D)", "SOT23", {"1": "DD7_ALIVE", "2": "GND", "3": "SYS_INH_G"}, "C8545")\n'
    'r("R82", "100k 1%", "VBAT", "SYS_INH_P", lcsc="C25803"); r("R83", "200k 1%", "SYS_INH_P", "SYS_INH_D")   # Q49 VGS -VBAT/3: -4.0 V at 12.05 V, -9.7 V at the 29.2 V clamp\n'
    'part("Q49", "Transistor_FET", "AO3401A", "AO3401A P-FET: the charge inhibit, the battery FETs\' gates held at VBAT (1 G, 2 S, 3 D)", "SOT23", {"1": "SYS_INH_P", "2": "VBAT", "3": "CH_BATDRV"}, "C15127")\n'
    '_intent.node("SYS_INH_G", 14.6, "L4-E11 round 9 (B-R2): Q47\'s gate, DOCK_EN_OUT over R109 / R144 (half of it): 14.6 V at the loop\'s 29.2 V clamp")\n'
    '_intent.node("SYS_INH_D", 29.2, "L4-E11 round 9 (B-R2): Q47\'s drain, VBAT through R82 and R83 while Q47 is off: at most VBAT\'s 29.2 V clamp")\n'
    '_intent.node("SYS_INH_P", 29.2, "L4-E11 round 9 (B-R2): Q49\'s gate, VBAT through R82; two thirds of VBAT while Q47 holds R83 low")\n')

_ANCHOR_LISTED = "_listed = {r for _, refs in SECTIONS for r in refs}\n"
_SEC = ('SECTIONS.append(("THE PACK BREAKER\'S INPUT-RETURN RESET AND THE CHARGE INHIBIT (DD-7, L4-E11 ROUND 9): Q44 TO Q49", '
        '["Q44", "R106", "D25", "Q45", "Q46", "R107", "R108", "R109", "R144", "Q47", "Q48", "R82", "R83", "Q49"]))   # L4-E11 round 9\n')

EDITS = [
    (_ANCHOR_MAIN, _RESET + _ANCHOR_MAIN),
    (_ANCHOR_LISTED, _SEC + _ANCHOR_LISTED),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def code_only(text):
    return "\n".join(l.split("#")[0] for l in text.splitlines())


def patched(text):
    code = code_only(text)
    for req in REQUIRES:
        if req not in text:
            refuse("record l8p's enable loop or U34's FE_RUN is not drawn in the target (%r missing): apply l8p's PTC draft first" % req[:40])
    for ref in ADDS:
        if re.search(r'"%s"' % re.escape(ref), code):
            refuse("designator %s is already in use in the target" % ref)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), code):
            refuse("net %s already exists in the target" % net)
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once: %r" % (new.count(old), old[:70]))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: task L4-E11 drafts this change for board A's generator owner and never applies it. Writing the repository's own
# gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of L4-E11 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; L4-E11's values wait on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE.md names no single check")
    path = os.path.join(REPO, rec[0])
    if ".." in rec[0].split("/") or not os.path.isfile(path):
        refuse("NOT RELEASED: check %s is not in this tree" % rec[0])
    if open(path, encoding="utf-8").readline().rstrip("\n") != "accepted: yes":
        refuse("NOT RELEASED: check %s is not accepted" % rec[0])


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    if write and os.path.realpath(target) == os.path.realpath(TREE_GEN):
        released()
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_a.py", "b/gen_sch_a.py", n=0))
    if not write:
        print("%s: CHECK OK, %d edit(s), nothing written" % (NAME, len(EDITS)))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in EDITS):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("%s: WRITTEN, %d edit(s)" % (NAME, len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
