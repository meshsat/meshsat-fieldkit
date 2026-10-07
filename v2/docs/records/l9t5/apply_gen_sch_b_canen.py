#!/usr/bin/env python3
"""apply_gen_sch_b_canen.py: DRAFT for board B's generator owner (Layer 9 record l9t5, task T10 round 9; Layer 4 task L4A-54's
correction by W143 on W139's finding W139-F2; record l4canen reads it; MESHSAT-1357, 7 October 2026). NOT APPLIED to the tree by this
record, like every draft of L4-E9's change list (None is APPLIED); its author ran it only on scratch copies. It applies after BOTH
apply_gen_sch_b_canmb.py (W137, the peers' observation and vote) and W138's apply_gen_sch_b_regstage.py (record l4reg, fnd/l4reg
86dbcdff: the TPS2553-1 limiter whose EN this draft drives), in either order of those two, and refuses a target without either.

Why (W139's T10-CANQ.md section 6 and finding W139-F2): a supervisor latched off by its TPS2553-1 (row 8's held states lie inside the
limiter's band; "latched off ... until EN or power is cycled", W138 quoting SLVS841F 9.3.1 and 9.3.3) has nothing driving its EN, so
only a kit power cycle (RAIL_EN) brings it back: the recovery proof is NOT met for that state. The route (W139's, drawn here): the two
peers restart a latched supervisor by a 2-of-2 vote on its limiter's EN, each deciding on its own observation and needing no fabric,
so that a single faulty peer can never hold a healthy supervisor off, as the SHDN votes of canmb.
  1. THE VOTE (six outputs, two per controller): each controller drives two restart votes on pins 59 and 60 (PD12, PD13, GPIO), one
     on the next controller and one on the one after. Each target's two votes enter an SN74LVC1G08 (U586, U587, U588) supplied from the
     NEXT controller's 3.3 V through 100 Ohm (R615, R635, R655), so the gate is alive while its target is latched and dark, and a short
     of its 100 nF (C947, C957, C967) loads that rail with tens of milliamperes only; each vote input is held low by 10 kOhm (R616 and
     R617, R636 and R637, R656 and R657) while its voter is in reset or dark.
  2. THE DELAY AND THE SWITCH: the gate's output reaches an AO3400A's gate (Q586, Q587, Q588; JLCPCB C20917, board B's Q212 part)
     through 100 kOhm 1 % (R618, R638, R658) into 4.7 uF (C948, C958, C968) with 1 MOhm 1 % to ground (R619, R639, R659), so a test pulse
     of 4 ms leaves the gate far under the FET's printed threshold while a restart vote held 2 s turns it fully on; the FET pulls the
     target's IOC{t}_LIM_EN low through 470 Ohm 1 % (R660, R662, R664), which bounds the current to a few milliamperes if the EN pull-up
     ever shorts.
  3. THE PULL-UP: W138's EN pull-up R602, R622, R642 becomes 10 kOhm 1 % (was 100 kOhm), so that the FET's off-state leakage, printed only
     to 55 C, cannot pull EN under the TPS2553's 1.1 V high threshold at board B's 76.25 C air (record l4canen section 5).
  4. THE READ-BACK: each controller reads its own restart gate's output on pin 61 (PD14, an input) through 10 kOhm (R661, R663, R665),
     so the in-service test (FW-B22 restated, record l9t5 l9t5_canmb.out section 7) sees every latent fault of the vote path that could
     let one peer act alone, without ever switching a supervisor off.
The firmware rule (DRAFTED in apply_hw_fw_contract_canq.py): a controller asserts its restart vote on a peer for 2 s when it has
captured no edge on either of that peer's TXDs and received no state frame of it on either fabric for 2 s, at most once in 10 s per
peer; never on a message received over a fabric. CON-004's fabrics, the transceivers, canmb's observation and SHDN votes and W138's
limiter and regulator are otherwise untouched; no part is removed.
Designators added: U586 to U588, Q586 to Q588, C947, C948, C957, C958, C967, C968, R615 to R619, R635 to R639, R655 to R659, R660 to
R665 (33 parts); changed: R602, R622, R642 (100 kOhm to 10 kOhm 1 %); the controllers' pins 59, 60 and 61.
Usage:  apply_gen_sch_b_canen.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (already applied, canmb or regstage absent, an old text missing, a designator or a pin in
use, or the repository's own generator named before RELEASE-T10.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_canen"
BOARD = "b"
ADDS = (tuple("U%d" % (586 + k) for k in range(3)) + tuple("Q%d" % (586 + k) for k in range(3))
        + tuple("C%d" % (947 + 10 * k + n) for k in range(3) for n in (0, 1))
        + tuple("R%d" % (615 + 20 * k + n) for k in range(3) for n in range(5)) + tuple("R%d" % (660 + n) for n in range(6)))
REMOVES = ()
CHANGED = tuple("R%d" % (602 + 20 * k) for k in range(3))
# the pin plan, read by record l4canen (never typed there): LQFP-100 pin -> (port, use, which peer: 1 the next, 2 the one after, 0 itself)
RST_PINS = {59: ("PD12", "vote", 1), 60: ("PD13", "vote", 2), 61: ("PD14", "readback", 0)}
R_SUP, R_VPD, R_RC, C_RC, R_PD, R_DRAIN, R_RB, R_ENPU = "100R 1%", "10k", "100k 1%", "4.7u", "1M 1%", "470R 1%", "10k", "10k 1%"
GATE, GATE_LCSC, FET, FET_LCSC = "SN74LVC1G08DBVR", "C7666", "AO3400A", "C20917"

_OLD_MAP = '              57: "IOC%s_CAN1_VOTE%s" % ("ABC"[(_k + 2) % 3], _tag), 58: "IOC%s_CAN2_VOTE%s" % ("ABC"[(_k + 2) % 3], _tag)})\n'
_NEW_MAP = ('              57: "IOC%s_CAN1_VOTE%s" % ("ABC"[(_k + 2) % 3], _tag), 58: "IOC%s_CAN2_VOTE%s" % ("ABC"[(_k + 2) % 3], _tag),\n'
            '              # T10 ROUND 9 (records l9t5 and l4canen, W143; apply_gen_sch_b_canen.py, NOT APPLIED): the latched supervisor\'s EN route.\n'
            '              # PD12 and PD13 (pins 59 and 60, GPIO outputs) are this controller\'s restart votes on the next controller and the one\n'
            '              # after (2 of 2 with the other peer); PD14 (pin 61, an input) reads this controller\'s own restart gate through 10 kOhm\n'
            '              59: "IOC%s_RSTV%s" % ("ABC"[(_k + 1) % 3], _tag), 60: "IOC%s_RSTV%s" % ("ABC"[(_k + 2) % 3], _tag), 61: "IOC%s_RSTRB" % _tag})\n')
_OLD_EN = '    r(_GR(2), "100k", "+5V_IOC", "IOC%s_LIM_EN" % _tag)   # the limiter\'s EN pulled up (SLVS841F 7.3: EN 0 to 6.5 V)\n'
_NEW_EN = (
    "    # T10 ROUND 9 (records l9t5 and l4canen, W143; apply_gen_sch_b_canen.py, a DRAFT, NOT APPLIED): THE LATCHED SUPERVISOR'S EN ROUTE\n"
    "    # (W139-F2). The other two controllers restart this one by a 2-of-2 vote on its limiter's EN: an SN74LVC1G08 supplied from the NEXT\n"
    "    # controller's rail through 100 Ohm (alive while this one is latched and dark), its inputs the two peers' restart votes, each held\n"
    "    # low by 10 kOhm; its output through 100 kOhm into 4.7 uF (1 MOhm to ground) turns on an AO3400A that pulls EN low through 470 Ohm.\n"
    "    # One peer alone can never pull EN (the AND), so no single faulty peer holds this controller off; a 4 ms test pulse stays far under\n"
    "    # the FET's threshold behind the RC, so the in-service test never switches a supervisor off; pin 61 reads the gate's output. EN's\n"
    "    # pull-up is 10 kOhm so that the FET's leakage, printed only to 55 C, cannot pull EN under 1.1 V (SLVS841F 7.3). Record l4canen reads\n"
    "    # every level, the recovery interval and the route's own faults on the makers' printed figures\n"
    '    r(_GR(2), "10k 1%", "+5V_IOC", "IOC%s_LIM_EN" % _tag)   # the limiter\'s EN pulled up (SLVS841F 7.3: EN 0 to 6.5 V); 10 kOhm since round 9\n'
    '    _pa, _pb = "ABC"[(_k + 1) % 3], "ABC"[(_k + 2) % 3]   # the next controller and the one after: this controller\'s two peers\n'
    '    _env, _rsy, _rsg, _rsd = ("IOC%s_%s" % (_tag, _n) for _n in ("ENVCC", "RSTY", "RSTG", "RSTD"))\n'
    '    _rva, _rvb = "IOC%s_RSTV%s" % (_tag, _pa), "IOC%s_RSTV%s" % (_tag, _pb)\n'
    '    r(_GR(15), "100R 1%", "+3V3_IOC%s" % _pa, _env)   # the restart gate\'s supply, from the next controller\'s rail\n'
    '    lvc1g08("U%d" % (586 + _k), _rva, _rvb, _rsy, _env, "C%d" % (947 + 10 * _k), "controller %s\'s restart, the 2-of-2 vote of controllers %s and %s on its limiter\'s EN (records l9t5, l4canen)" % (_tag, _pa, _pb))\n'
    '    r(_GR(16), "10k", _rva, "GND"); r(_GR(17), "10k", _rvb, "GND")   # each restart vote low while its voter is in reset or dark\n'
    '    r(_GR(18), "100k 1%", _rsy, _rsg); c("C%d" % (948 + 10 * _k), "4.7u", _rsg, "GND", "C10u"); r(_GR(19), "1M 1%", _rsg, "GND")   # the RC: a 4 ms test pulse never reaches the threshold\n'
    '    part("Q%d" % (586 + _k), "Transistor_FET", "AO3400A", "AO3400A: controller %s\'s restart, pulls its limiter\'s EN low while both peers vote (records l9t5, l4canen)" % _tag, "SOT23",\n'
    '         {"1": _rsg, "2": "GND", "3": _rsd}, "C20917")   # 1 G 2 S 3 D (board B\'s Q212 part)\n'
    '    r("R%d" % (660 + 2 * _k), "470R 1%", _rsd, "IOC%s_LIM_EN" % _tag)   # bounds the current if the EN pull-up shorts\n'
    '    r("R%d" % (661 + 2 * _k), "10k", _rsy, "IOC%s_RSTRB" % _tag)   # this controller reads its own restart gate\'s output\n')
EDITS = [(_OLD_MAP, _NEW_MAP), (_OLD_EN, _NEW_EN)]
PLANNED = tuple(RST_PINS)


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if "_RSTV%s" in text or "_RSTRB" in text:
        refuse("the change is already applied")
    if text.count(_OLD_MAP) != 1 or "_CAN1_OBS%s" not in text:
        refuse("record l9t5's canmb draft (apply_gen_sch_b_canmb.py, after iocguard) is not in the target: apply it first")
    if text.count(_OLD_EN) != 1 or "TPS2553-1" not in text:
        refuse("W138's regstage draft (apply_gen_sch_b_regstage.py, record l4reg, fnd/l4reg 86dbcdff) is not in the target: apply it first")
    for ref in ADDS:
        if re.search(r'"%s"' % ref, text):
            refuse("%s is already drawn as a literal designator" % ref)
    if not re.search(r"_GR = lambda n, _k=_k: \"R%d\" % \(600 \+ 20 \* _k \+ n\)", text) or "def lvc1g08(" not in text:
        refuse("the controllers' resistor numbering (_GR(n) = R600 + 20k + n) or the SN74LVC1G08 helper is not the one this draft was written against")
    blk = text[text.index("    m.update({14: \"IOC%s_RST_n\" % _tag"):text.index(_OLD_MAP)]
    taken = [p for p in PLANNED if re.search(r"(?<![\d.])%d: " % p, blk)]
    if taken:
        refuse("pin(s) %s are already on the controllers' map" % taken)
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once: %r" % (new.count(old), old[:60]))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: record l9t5 drafts this change for the generator's owner and never applies it. Writing the repository's own generator
# is refused until RELEASE-T10.md beside this script reads "released: yes" on its first line and names an accepted check of task T10
# ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (record l4canen's script does).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_%s.py" % BOARD)
RELEASE = os.path.join(HERE, "RELEASE-T10.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE-T10.md; record l9t5's T10 drafts wait on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE-T10.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE-T10.md names no single check")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_%s.py" % BOARD, "b/gen_sch_%s.py" % BOARD, n=0))
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
