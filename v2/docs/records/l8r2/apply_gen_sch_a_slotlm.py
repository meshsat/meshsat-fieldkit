#!/usr/bin/env python3
"""apply_gen_sch_a_slotlm.py: DRAFT for board A's generator owner (Layer 8 record l8r2, round 4, L9P-F02's focused check,
MESHSAT-1357, 3 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write
scratch copies).

The defect (record l9pwr's L9P-F02 and this record's section 1s): slots 1 and 3 run on board A's AP64500 U4 and U6, a 5 A buck
in one SO-8EP package (Diodes DS41979 Rev 5-2: theta-JA 45 C/W on a four-layer 2 oz board, recommended junction at most +125 C,
thermal shutdown +160 C). With the coolers' 12 V step-up on the slot rail (apply_gen_sch_b_fans12.py) the slot's envelope (every
load at HIGH, the cooler at its 2.75 W bound at the step-up's 12.43 V top over the step-up's 0.80, round 5) is 5.223 A at 5.1 V
and 5.487 A at the AP64500's least output with the rail's whole drop budget, over its 5 A; round 3's 70 % Fan_PWM maximum held
the slot under 5 A only at the nominal voltage, only while the module's firmware drives the line, and not with the PWM lead open
(the fan's maker: "When control terminal is open, speed is the same as at 100% duty cycle"). Without any cooler the slot's other
loads at HIGH and the least voltage, 4.779 A, are past the maker's typical derating at C1's +50 C inside air (Figure 24 at 500
kHz ends at 48.4 C); the drawn 68 k RT sets 1.47 MHz (DS41979 Eq. 7), where the switching loss is higher still.

The correction: slots 1 and 3 take the stage slot 2 and the device rail carry since F-PR-04 (26 September 2026): an LM5176
four-switch stage with four CSD19532Q5B, an XAL1010-682ME, a 6 mOhm WSL2512 ISNS shunt (its average current loop limits at 43
to 57 mV, 7.096 A at its least), BIAS on VBAT, slot 2's compensation, slope capacitor, bulk (three EEHZK1E151XP) and output
ceramics, its VIN pin's own 0.1 uF. Per slot, designators in board A's free 500 block (500 + k on slot 1, 530 + k on slot 3):
  U501 / U531       LM5176PWPR (the slot's controller; U4 and U6, the AP64500s, are retired)
  Q501..Q504 / Q531..Q534   the buck-side high and low FETs, the boost-side low and high FETs (Q501 / Q531 is VBAT's entry)
  L501 / L531       6.8 uH XAL1010-682ME
  R501..R512 / R531..R542   FB 53.6k over 10k (5.088 V, as slot 2), RT 40.2k, COMP Rc1, ISNS 6 mOhm, CS 5 mOhm, PGOOD, MODE,
                    the CS and ISNS filters' 100 R pairs
  C501..C519 / C531..C549   SLOPE 470p, COMP 100n and 1n, SS, VCC 4.7u, BOOT1 and BOOT2, CIN 2 x 10u, COUT 3 x 22u 25 V,
                    the CS and ISNS filters' 1n, three 150 uF hybrid polymer, BIAS 100n, VIN 100n
  D501, D502 / D531, D532   BAT46W bootstrap diodes
Kept: U8 and U10 (the INA226 monitors, 0x40 and 0x44, now across the 6 mOhm ISNS shunts R505 and R535: their calibration is a
firmware item, as F-PR-04 noted for slot 2's U9), R30 and R38 (the SLOT_EN pull-downs, the values and roles unchanged), the
nets S1_OUT, S1_FB, S1_RT, S1_COMP, S1_COMPC and their S3 twins (the same roles). Retired: U4, U6, L3, L5, C28 to C33, C40 to
C45, C112, C114, R28, R29, R31, R36, R37, R39, R45, R47, R129, R131 and the nets S1_SW, S1_BOOT, S3_SW, S3_BOOT.

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else:
  1. the two buck5() calls become the two stages (the lm5176() helper as slot 2 calls it), each followed by its SLOT_EN pull-down
     and its INA226, as slot 2's R34 and U9 follow its stage;
  2. VBAT's loads: "U4": 2.0 and "U6": 2.0 become the stages' entries Q501 and Q531 at 2.22 A each (the S-98 method of Q28's
     2.22 A: the declared peak x 5.1 V over 0.90 x 14.4 V, 5.63 x 5.1 / 12.96 = 2.216);
  3. the slot rails' declaration: the shunts R505 and R535, the switches U501 and U531, the peak 5.63 A on slots 1 and 3 at both
     ends of the lead (board B's half is apply_gen_sch_b_fans12.py), and the note;
  4. the two slot sections of SECTIONS name the stages' parts;
  5. where record l8r2's pack return (apply_gen_sch_a_packrtn.py) is already applied, GND's loads "U4": 2.0 and "U6": 2.0 become
     the stages' CS shunts R506 and R536 at 2.22 A, through which such a stage's input current returns (the draft's own rule for
     R170, R177, R56, R122); packrtn applied after this draft writes the same text (both orders give one generator).
The peak, 5.63 A (round 5, the collaborator's B2; slot 2's figure, so the three identical leads declare one): the slot's envelope,
every load at HIGH (record l9pwr's 23.197 W before the cooler on S1 in PS-BUSY and PS-ALLTX) with the cooler at its 2.75 W bound
at the step-up's 12.43 V top over the step-up's 0.80 (3.4375 W), at the stage's least output (VREF 0.788 V on the 1 % divider,
4.928 V) less the rail's whole 2 % drop budget (4.829 V): 5.515 A.

Order: after L4-E11's charger draft, whose anchor names VBAT's "U4": 2.0 (L4-E9's order already has it: 3a, then 3g, then this
record's drafts, then d8dec31's mainpb); release with apply_gen_sch_b_fans12.py (board B's half of the slot rails' peak).
Usage:  apply_gen_sch_a_slotlm.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or
net is in use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_slotlm"
BASE = {"1": 500, "3": 530}
ADDS = tuple("%s%d" % (p, BASE[s] + k) for s in ("1", "3") for p, ks in
             (("U", (1,)), ("Q", range(1, 5)), ("L", (1,)), ("D", (1, 2)), ("R", range(1, 13)), ("C", range(1, 20))) for k in ks)
RETIRED = ("U4", "U6", "L3", "L5", "C28", "C29", "C30", "C31", "C32", "C33", "C40", "C41", "C42", "C43", "C44", "C45", "C112",
           "C114", "R28", "R29", "R31", "R36", "R37", "R39", "R45", "R47", "R129", "R131")
NETS = tuple("S%s_%s" % (s, t) for s in ("1", "3") for t in ("SW1", "SW2", "HDRV1", "HDRV2", "LDRV1", "LDRV2", "BOOT1", "BOOT2", "VCC",
                                                           "CS", "CSF", "CSGF", "ISNS_P", "ISNS_N", "MODE", "SLOPE", "SS", "PGOOD"))
PEAK = 5.63
ENTRY = 2.22


def stage(s):
    b = BASE[s]; R = lambda k: '"R%d"' % (b + k); C = lambda k: '"C%d"' % (b + k); Q = lambda k: '"Q%d"' % (b + k)
    ina, a1, addr, en, pd = {"1": ("U8", "GND", "0x40", "SLOT_EN1", "R30"), "3": ("U10", "+3V3", "0x44", "SLOT_EN3", "R38")}[s]
    refs = ", ".join([Q(1), Q(2), Q(3), Q(4), R(1), R(2), R(3), C(1), R(4), C(2), C(3), C(4), C(5), C(6), C(7), R(5), R(6), R(7),
                      "None", "None", C(8), C(9), C(10), C(11), C(12), R(8)])
    return (
        'lm5176("S%s", "U%d", "VBAT", "+5V_S%s", "%s", "53.6k", "L%d", "6.8uH XAL1010-682ME (Isat 21.8 A)", '
        '"CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6)", "C473333",\n'
        '       [%s],\n'
        '       cs_filter=(%s, %s, %s), isns_filter=(%s, %s, %s), isns="6m", isns_lcsc="C843882",\n'
        '       cout="22u 25V 1210", cout_lcsc="C2918511", cslope=("470p", "C27694"), boot_diodes=("D%d", "D%d"), en_div=False,\n'
        '       bias="VBAT", comp=(("2.2k", "C4190"), ("100n", "C14663"), ("1n", "C1588")), bulk=(%s, %s, %s), bulk_part="E151", bias_cap=%s,\n'
        '       vin_cap=(%s, "100n", "C14663"))   # record l8r2 round 4 (L9P-F02): slot 2\'s stage (F-PR-04) for slot %s; its loop and bulk ripple re-run for this slot\'s remote capacitance is owed (the record, section 1s)\n'
        'r("%s", "100k", "%s", "GND")   # a slot with no controller line stays off (as the AP64500 stage had it; kept by record l8r2 round 4)\n'
        'ic("%s", 10, "INA226 rail monitor +5V_S%s", "VSSOP10", {"1": "%s", "2": "GND", "3": "INA_ALERT", "4": "SDA", "5": "SCL", "6": "+3V3", '
        '"7": "GND", "8": "+5V_S%s", "9": "+5V_S%s", "10": "S%s_OUT"}, "C49851")   # %s, across the 6 mOhm ISNS shunt R%d (was the AP64500\'s 5 mOhm R%s: a calibration change, a firmware item)\n'
        % (s, b + 1, s, en, b + 1, refs, R(9), R(10), C(13), R(11), R(12), C(14), b + 1, b + 2, C(15), C(16), C(17), C(18), C(19), s,
           pd, en, ina, s, a1, s, s, s, addr, b + 5, {"1": "31", "3": "39"}[s]))


def section(s):
    b = BASE[s]
    ina, pd, addr = {"1": ("U8", "R30", "0x40"), "3": ("U10", "R38", "0x44")}[s]
    refs = (["U%d" % (b + 1)] + ["Q%d" % (b + k) for k in range(1, 5)] + ["L%d" % (b + 1)] + ["R%d" % (b + k) for k in range(1, 13)]
            + ["C%d" % (b + k) for k in range(1, 20)] + ["D%d" % (b + 1), "D%d" % (b + 2), pd, ina, "J_5V_S%s" % s])
    return '            ("SLOT RAIL S%s: LM5176 5.1 V (7.1 A MINIMUM LIMIT) + INA226 %s", [%s]),   # record l8r2 round 4 (L9P-F02)\n' % (
        s, addr, ", ".join('"%s"' % x for x in refs))


_OLD_S1 = ('buck5("1", "U4", "SLOT_EN1", "+5V_S1", ["L3", "C28", "C29", "C30", "C31", "C32", "C33", "R28", "R29", "R30", "R31", "R45", '
           '"R129", "C112"], "U8", "GND", "GND")        # 0x40\n')
_OLD_S3 = ('buck5("3", "U6", "SLOT_EN3", "+5V_S3", ["L5", "C40", "C41", "C42", "C43", "C44", "C45", "R36", "R37", "R38", "R39", "R47", '
           '"R131", "C114"], "U10", "+3V3", "GND")      # 0x44\n')
_NEW_S = ('# L9P-F02, RECORD l8r2 ROUNDS 4 AND 5 (MESHSAT-1357, 3 and 4 October 2026; v2/docs/records/l8r2/ section 1s): SLOTS 1 AND 3\n'
          '# LEAVE THE AP64500 AS SLOT 2 DID UNDER F-PR-04. With the coolers\' 12 V step-up on the slot rail (board B, E11-40) a slot\'s\n'
          '# envelope reads 5.223 A at HIGH at 5.1 V and 5.487 A at the AP64500\'s least output with the rail\'s 2 % drop; a duty maximum\n'
          '# on Fan_PWM held 5 A only at the nominal voltage and only while the firmware drives the line (the fan runs at full speed with\n'
          '# its PWM lead open, San Ace catalogue C1152B001 p.362). Without the cooler the slot\'s other loads at HIGH and the least\n'
          '# voltage (4.779 A) are past the maker\'s typical derating at the normal mode\'s +50 C inside air (Figure 24 at 500 kHz), and the\n'
          '# 68 k RT sets 1.47 MHz (DS41979 Eq. 7), where the switching loss is higher still. The bigger converter is this board\'s own\n'
          '# LM5176 stage, slot 2\'s parts and values: its average loop limits at 7.096 A at least (43 mV over 6 mOhm at +1 %), over the\n'
          '# slot\'s 5.515 A envelope at its own least output (4.829 V at the load) and its 6.534 A with the cooler starting through its\n'
          '# eFuse\'s highest limit (an assumed bound, CONDITIONAL). Designators in the free 500 block.\n'
          + stage("1") + stage("3"))
_OLD_VBAT = '"U4": 2.0, "Q28": 2.22, "U6": 2.0,'
_NEW_VBAT = '"Q%d": %.2f, "Q28": 2.22, "Q%d": %.2f,' % (BASE["1"] + 1, ENTRY, BASE["3"] + 1, ENTRY)
_OLD_SH = 'for _n, _sh in (("1", "R31"), ("2", "R35"), ("3", "R39")):\n'
_NEW_SH = 'for _n, _sh in (("1", "R%d"), ("2", "R35"), ("3", "R%d")):   # record l8r2 round 4: slots 1 and 3 on LM5176 stages, their ISNS shunts\n' % (
    BASE["1"] + 5, BASE["3"] + 5)
_OLD_RAIL = ('    _intent.rail("+5V_S%s" % _n, 5.1, 4.2 if _n == "2" else 2.5, 5.63 if _n == "2" else 5.0, _sh, loads={"J_5V_S%s" % _n: '
             '5.63 if _n == "2" else 5.0}, budget=0.02, share=0.005, fed_from="VBAT",\n'
             '                 switch={"1": "U4", "2": "U5", "3": "U6"}[_n], efficiency=0.90,\n')
_NEW_RAIL = ('    _intent.rail("+5V_S%%s" %% _n, 5.1, 4.2 if _n == "2" else 2.5, %.2f, _sh, loads={"J_5V_S%%s" %% _n: %.2f}, budget=0.02, '
             'share=0.005, fed_from="VBAT",   # record l8r2 round 5: one peak on the three identical slot leads\n'
             '                 switch={"1": "U%d", "2": "U5", "3": "U%d"}[_n], efficiency=0.90,\n' % (PEAK, PEAK, BASE["1"] + 1, BASE["3"] + 1))
_OLD_NOTE = ('                       "one CM5 slot with its cooler fan; 5 A peak at the module, the AP64500\'s rating (DS41979 p.1); the rail "\n'
             '                       "net starts at the INA226 shunt. This board\'s share of the 2 percent is 0.5 point, measured 0.07"))\n')
_NEW_NOTE = ('                       "one CM5 slot with its cooler fan on its 12 V step-up (record l8r2, E11-40); an LM5176 stage since record l8r2 "\n'
             '                       "round 4 (L9P-F02, slot 2\'s F-PR-04 stage): %.2f A peak, slot 2\'s, over the slot\'s envelope (every load at "\n'
             '                       "HIGH, the cooler at its 2.75 W bound over 0.80) at the stage\'s least output less the 2 percent drop, 5.515 A "\n'
             '                       "(round 5), declared at both ends of the lead; the loop\'s least "\n'
             '                       "7.096 A (VSNS 43 mV over the 6 mOhm ISNS shunt at +1 percent). The rail net starts at the INA226 shunt. "\n'
             '                       "This board\'s share of the 2 percent is 0.5 point, measured 0.07 on the AP64500 stage\'s copper (owed again)"))\n' % PEAK)
_OLD_SEC1 = ('            ("SLOT RAIL S1: AP64500 5.1 V + INA226 0x40", ["U4", "L3", "C28", "C29", "C30", "C31", "C32", "C33", "R28", "R29", '
             '"R30", "R31", "R45", "R129", "C112", "U8", "J_5V_S1"]),\n')
_OLD_SEC3 = ('            ("SLOT RAIL S3: AP64500 5.1 V + INA226 0x44", ["U6", "L5", "C40", "C41", "C42", "C43", "C44", "C45", "R36", "R37", '
             '"R38", "R39", "R47", "R131", "C114", "U10", "J_5V_S3"]),\n')
# record l8r2's pack return, when applied first: the ground ends of the two slot stages are their CS shunts
_OLD_GND = '"U4": 2.0, "R170": 2.22, "U6": 2.0,'
_NEW_GND = '"R%d": %.2f, "R170": 2.22, "R%d": %.2f,' % (BASE["1"] + 6, ENTRY, BASE["3"] + 6, ENTRY)

EDITS = [(_OLD_S1 + _OLD_S3, _NEW_S), (_OLD_VBAT, _NEW_VBAT), (_OLD_SH, _NEW_SH), (_OLD_RAIL, _NEW_RAIL), (_OLD_NOTE, _NEW_NOTE),
         (_OLD_SEC1, section("1")), (_OLD_SEC3, section("3"))]
OPTIONAL = [(_OLD_GND, _NEW_GND)]   # applied when present (the pack return drafted first), never required


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def in_use(text, ref):
    return re.search(r'"%s"' % re.escape(ref), text) is not None


def patched(text):
    for ref in ADDS:
        if in_use(text, ref):
            refuse("designator %s is already in use in the target" % ref)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), text):
            refuse("net %s already exists in the target" % net)
    if "def lm5176(" not in text:
        refuse("the target has no lm5176() helper")
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once" % new.count(old))
        new = new.replace(old, rep)
    for old, rep in OPTIONAL:
        if new.count(old) > 1:
            refuse("the pack return's slot entries occur %d times" % new.count(old))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    left = [r for r in RETIRED if re.search(r'(?<![\w])"%s"' % r, "\n".join(l.split("#")[0] for l in new.splitlines()))]
    if left:
        refuse("retired designators still named outside comments: %s" % left)
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: record l8r2 drafts this change for board A's generator owner and never applies it. Writing the repository's own
# gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; l8r2's drafts wait on an accepted check")
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
