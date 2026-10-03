#!/usr/bin/env python3
"""apply_gen_sch_b_fans12.py: DRAFT for board B's generator owner (Layer 8 record l8r2, item 1, MESHSAT-1357, 3 October 2026). NOT
APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).

The defect (E11-40, R-190, Layer 7's F-L7-02): board B's J_FAN1 to J_FAN3 carry the slot rail +5V_Sn at 5.1 V, and the cooler fan
Layer 7 selected (Sanyo Denki 9WPA0412P6G001, record l7pwr at 2087060b: 12 V, operating range 10.8 to 13.2 V, 0.17 A, 2.0 W, pulse
sensor and PWM; the PWM input level, the pulse output's type and the starting current NOT READ) needs 10.8 to 13.2 V.

What it draws, per slot s (designators in the 700 block, 700 + 30 (s - 1) + k, registered in SLOT_EXTRA[s] as _cx() does):
  U7x1  TPS61089 boost (TI SLVSD38C) from +5V_Sn to CFANs_12V at 11.51 to 12.43 V (R7x3 88.7k over R7x4 10k on VREF 1.188 to
        1.236 V); 498 kHz (R7x1 301k, Equation 3); peak current limit 7.3 to 8.9 A (R7x2 127k, the printed row); L7x1 4.7 uH
        XAL6060-472ME (Isat 11 A, board A's own part); COMP R7x5 23.7k with C7x8 47 nF (Equations 17 and 18 at an effective 33 uF,
        an ASSUMPTION; 10 kHz crossover, 5 to 15 kHz over 66 to 22 uF), C6 open (Equation 19 under 10 pF); VCC C7x2 4.7 uF ("more than 1.0 uF"); BOOT C7x1 100 nF; input C7x3 10 uF 25 V 1210 and C7x4 100 nF at VIN;
        output C7x5 to C7x7 3 x 22 uF 25 V 1210 (TI: "three 22-uF ceramic output capacitors work for most applications"); EN on
        +5V_Sn (EN absolute maximum 7 V), so an empty or unpowered slot's fan is dark, as the slot rail is.
  U7x2  TPS259631 eFuse (board B's efuse() helper, TI SLVSET8A) from CFANs_12V to CFANs_V: current limit 0.448 to 0.538 A
        (R7x6 1.87k by Equation 7, the tolerance interpolated between the printed 909 Ohm and 3.83 k rows: INFERRED), so a shorted
        fan lead takes 0.54 A at most and the boost's inductor and body diode never carry the slot rail's limit; OVLO 100k over
        10k cuts the fan at 12.64 to 13.67 V (VOVLO(R) 1.17 to 1.22 V, 1 % parts) against the boost's own OVP 12.7 to 13.6 V; EN
        pulled to +5V_Sn through R7x10 100k (SLVSET8A note 2: under 6 V, 100 k or more); FLT pulled to +3V3_DEV (R7x7).
  Q7x1  the tach stage, board B's level() helper: a 2N7002 with its gate on the module's +3V3_CMs, source on FAN_TACHOs (R7x11 10k
        to +3V3_CMs, beside the module's own pull-up), drain on the fan's pulse lead CFANs_TACH: whatever the fan's pulse output
        is (NOT READ), the module's pin never sees more than its own rail, and an open collector reads as it did.
  Q7x2  the PWM stage, the same bidirectional 2N7002: gate +3V3_CMs, source FAN_PWMs (R51 10k to +3V3_CMs, kept), drain the
        fan's PWM lead CFANs_PWM with R7x12 10k to +5V_Sn. Non-inverting; the module's Fan_PWM released (at boot, in reset) leaves
        CFANs_PWM high, the four-wire convention's full speed (INFERRED, the maker's level NOT READ).
  J_FANs  pin 1 CFANs_V (12 V), 2 GND, 3 CFANs_TACH, 4 CFANs_PWM; the JST-SH land and code unchanged.
ROUND 3 (record l9pwr's L9P-F02, 3 October 2026): at full speed the step-up takes 0.47 A of the slot rail (2.0 W of fan over 0.85,
an ASSUMPTION, at 5.0 V), which put slots 1 and 3 at 5.010 A at HIGH against their AP64500's 5 A and the slot rail's declared loads
at 5.121 A against its declared 5.0 A peak, over intent.rail's 2 % allowance, so the generator would have refused itself. The
modules drive the coolers' Fan_PWM at no more than 70 % duty (a firmware rule, the record's section 1 text for HW-FW-CONTRACT), so
the fan takes at most 1.4 W (the linear bound: a fan's input rises at least as fast as its duty, the fan laws) and the slot rail's
load row for the fan moves from J_FANs 0.1 A to the boost U7x1 at 0.33 A (1.4 W over 0.85 at 5.0 V; the slot's declared loads
4.981 A). Full speed (0.47 A) comes only with Fan_PWM released, when the module's PCIE_PWR_EN is low and the card socket's supply
is off by hardware (S{s}A_EN = EMCON_HW AND PCIE_PWR_EN{s}). The rails CFANs_12V and CFANs_V and the nodes CFANs_SW, CFANs_BOOT, CFANs_VCC, CFANs_FSW,
CFANs_TACH and CFANs_PWM are declared to the intent; the VIN and VCC capacitors are declared with their class and TI's clause.

What it changes in v2/ecad/tools/gen_sch_b.py, and nothing else: the footprint table gains QFN11 beside SH4; the fan's row in
_SLOT_LOADS; the J_FAN line of the slot loop becomes the block above (R51 kept on FAN_PWMs). No other draft targets gen_sch_b.py
but record l8gnd's GND-002 draft (R-195) and this record's F03 and F04 drafts, whose anchors are elsewhere (l8r2_drafts.out).

Usage:  apply_gen_sch_b_fans12.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or
net is in use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_fans12"
ADDS = tuple("%s%d" % (p, 700 + 30 * (s - 1) + k) for s in (1, 2, 3) for p, ks in
             (("U", (1, 2)), ("L", (1,)), ("Q", (1, 2)), ("R", range(1, 13)), ("C", range(1, 11))) for k in ks)
NETS = tuple("CFAN%d_%s" % (s, t) for s in (1, 2, 3) for t in ("12V", "V", "TACH", "PWM", "SW", "BOOT", "VCC", "FSW", "FB", "COMP", "ILIM", "EN", "FLT"))

_OLD_FP = '"SH4": "Connector_JST:JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical",'
_NEW_FP = ('"SH4": "Connector_JST:JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical", '
           '"QFN11": "Package_DFN_QFN:Texas_VQFN-RNR0011A-11",   # l8r2: the coolers\' TPS61089 (the land board A drew at A17, b8cef471)')

_OLD_LOAD = '    "J_FAN%d" % s: 0.1,              # the slot\'s IP68 cooler fan\n'
_NEW_LOAD = ('    "U%d" % (701 + 30 * (s - 1)): 0.33,   # l8r2 (E11-40): the cooler fan\'s 12 V step-up, 1.4 W of fan over 0.85 '
             '(ASSUMPTION) at 5.0 V, at the modules\' 70 % Fan_PWM maximum (round 3, L9P-F02; 0.47 A at full speed only with '
             'Fan_PWM released, the card socket\'s supply then off)\n')

_OLD_FAN = ('    part("J_FAN%d" % s, "Connector_Generic", "Conn_01x04", "IP68 cooler fan of S%d (JST-SH 1.0): 5V GND TACHO PWM" % s, '
            '"SH4", {"1": n5, "2": "GND", "3": "FAN_TACHO%d" % s, "4": "FAN_PWM%d" % s, "MP": "NC"}, "C160390"); '
            'r(R(51), "10k", "FAN_PWM%d" % s, cm33)')

_NEW_FAN = '''    # E11-40 (R-190, Layer 7's F-L7-02), drafted by Layer 8 record l8r2 (MESHSAT-1357, 3 October 2026): THE COOLER FAN NEEDS 12 V.
    # The selected Sanyo Denki 9WPA0412P6G001 (record l7pwr at 2087060b) prints 12 V, 10.8 to 13.2 V, 0.17 A, 2.0 W, a pulse
    # sensor and a PWM input; this rail is 5.1 V. A per-slot step-up keeps the fan with its slot (dark with an empty slot),
    # needs no harness, no contract and no board A change; selected over one 12 V feed from board A (the record, section 1).
    # ROUND 3 (record l9pwr's L9P-F02): the module drives Fan_PWM at no more than 70 % duty, which holds this slot's declared
    # loads under its 5.0 A and slots 1 and 3 under their AP64500's 5 A at HIGH; full speed only with Fan_PWM released, when
    # the card socket's supply is off (S{s}A_EN = EMCON_HW AND PCIE_PWR_EN{s}). One 12 V feed from board A would make one converter
    # common to the three modules' coolers, a shared element ASM-002 does not name (the record, section 1).
    _fb = 700 + 30 * (s - 1); _fU = lambda k: "U%d" % (_fb + k); _fL = lambda k: "L%d" % (_fb + k)
    _fQ = lambda k: "Q%d" % (_fb + k); _fR = lambda k: "R%d" % (_fb + k); _fC = lambda k: "C%d" % (_fb + k)
    f12, fv, fsw = "CFAN%d_12V" % s, "CFAN%d_V" % s, "CFAN%d_SW" % s
    # U7x1 TPS61089 (TI SLVSD38C): 1 FSW, 2 VCC, 3 FB, 4 COMP, 5 GND, 6 VOUT, 7 EN, 8 ILIM, 9 VIN, 10 BOOT, 11 SW (Table 6-1).
    ic(_fU(1), 11, "TPS61089 boost 12.0 V: S%d's cooler fan (11.51 to 12.43 V, 498 kHz, ILIM 7.3 to 8.9 A)" % s, "QFN11",
       {"1": "CFAN%d_FSW" % s, "2": "CFAN%d_VCC" % s, "3": "CFAN%d_FB" % s, "4": "CFAN%d_COMP" % s, "5": "GND", "6": f12, "7": n5,
        "8": "CFAN%d_ILIM" % s, "9": n5, "10": "CFAN%d_BOOT" % s, "11": fsw}, "C165129")
    part(_fL(1), "Device", "L", "4.7uH XAL6060-472ME (Isat 11 A)", "L6060", {"1": n5, "2": fsw})
    r(_fR(1), "301k 1% (FSW: 498 kHz)", "CFAN%d_FSW" % s, fsw, "R", "C2933194"); r(_fR(2), "127k 1% (ILIM 7.3 to 8.9 A)", "CFAN%d_ILIM" % s, "GND")
    r(_fR(3), "88.7k 1%", f12, "CFAN%d_FB" % s); r(_fR(4), "10k 1%", "CFAN%d_FB" % s, "GND")   # 1.212 V x (1 + 88.7 / 10) = 11.96 V
    r(_fR(5), "23.7k 1%", "CFAN%d_COMP" % s, "CFAN%d_COMPC" % s); c(_fC(8), "47n", "CFAN%d_COMPC" % s, "GND", "C", "C1622")
    c(_fC(1), "100n", "CFAN%d_BOOT" % s, fsw); c(_fC(2), "4.7u", "CFAN%d_VCC" % s, "GND", "C10u", "C354262")   # CC0805KKX7R8BB475, X7R 25 V 0805
    c(_fC(3), "10u 25V 1210", n5, "GND", "C1210", "C2918497"); c(_fC(4), "100n", n5, "GND")
    for _k in (5, 6, 7): c(_fC(_k), "22u 25V 1210", f12, "GND", "C1210", "C2918511")
    _intent.bypass(_fC(4), _fU(1), "9", n5, cls="D", basis="TI SLVSD38C (TPS61089) 9.2.2.6 p.16: 'A 0.1-uF ceramic bypass capacitor is "
                   "recommended as close as possible to the VIN pin'")
    _intent.bypass(_fC(2), _fU(1), "2", "CFAN%d_VCC" % s, cls="L", basis="TI SLVSD38C (TPS61089) Table 6-1 and 9.2.2.6: VCC 'Output of the "
                   "internal regulator. A ceramic capacitor of more than 1.0 uF is required'", value_floor="1u")
    # U7x2 TPS259631 eFuse (board B's helper): the fan lead's short is limited at 0.448 to 0.538 A (R 1.87k, Equation 7; the
    # tolerance interpolated between SLVSET8A's printed rows, INFERRED); its OVLO (100k / 10k) cuts the fan at 12.64 to 13.67 V.
    efuse(_fU(2), f12, fv, "CFAN%d_EN" % s, "CFAN%d_FLT" % s, [_fC(9), _fR(6), _fR(7), _fR(8), _fR(9), _fC(10)], "1.87k 1% (ILM: 0.49 A)")
    r(_fR(10), "100k", "CFAN%d_EN" % s, n5)   # SLVSET8A note 2: EN pulled to a supply under 6 V through 100 k or more
    # The control lines cross a 2N7002 stage each, so the module's pins never see the fan's own levels (NOT READ). The PWM stage
    # is non-inverting: the module's duty, at most 70 % (round 3), reaches the fan as it is; released, the fan runs full.
    level(_fQ(1), _fR(11), "CFAN%d_TACH" % s, "FAN_TACHO%d" % s, cm33)
    nfet(_fQ(2), cm33, "FAN_PWM%d" % s, "CFAN%d_PWM" % s); r(_fR(12), "10k", "CFAN%d_PWM" % s, n5)
    part("J_FAN%d" % s, "Connector_Generic", "Conn_01x04", "IP68 cooler fan of S%d, Sanyo Denki 9WPA0412P6G001 (JST-SH 1.0): 12V GND TACH PWM" % s,
         "SH4", {"1": fv, "2": "GND", "3": "CFAN%d_TACH" % s, "4": "CFAN%d_PWM" % s, "MP": "NC"}, "C160390"); r(R(51), "10k", "FAN_PWM%d" % s, cm33)
    for _ref in [_fU(1), _fU(2), _fL(1), _fQ(1), _fQ(2)] + [_fR(k) for k in range(1, 13)] + [_fC(k) for k in range(1, 11)]:
        SLOT_EXTRA[s].add(_ref)
    _intent.rail(f12, 12.0, 0.17, 0.54, _fU(1), loads={_fU(2): 0.17}, converted=True, efficiency=0.85, fed_from=n5, switch=_fU(1),
                 source_ic="U%d is a TPS61089 boost: its VOUT pin is the power path (the synchronous rectifier is internal)" % (_fb + 1),
                 v_work=12.43, note="S%d's cooler fan rail: 11.51 to 12.43 V regulated (VREF 1.188 to 1.236 V, 1 %% divider); "
                 "0.17 A the fan's rated current at full speed (Fan_PWM released), at most 0.117 A at the modules' 70 %% Fan_PWM "
                 "maximum (the linear bound, round 3); 0.54 A the eFuse's highest limit; efficiency 0.85 an ASSUMPTION" % s)
    _intent.rail(fv, 12.0, 0.17, 0.54, _fU(2), loads={"J_FAN%d" % s: 0.17}, series_of=f12, converted=False, v_work=12.43,
                 source_ic="U%d is a TPS2596 eFuse: its OUT pin IS the power path" % (_fb + 2),
                 note="S%d's cooler fan supply behind the eFuse U%d (0.448 to 0.538 A, OVLO 12.64 to 13.67 V), out at J_FAN%d pin 1" % (s, _fb + 2, s))
    _intent.node(fsw, 13.6, "S%d's cooler boost switching node: it swings to CFAN%d_12V, at most the TPS61089's OVP 13.6 V (SLVSD38C)" % (s, s), v_min=-1.0)
    _intent.node("CFAN%d_BOOT" % s, 13.6 + 7.0, "the TPS61089's bootstrap riding on %s (BOOT absolute maximum SW + 7 V, SLVSD38C 7.1)" % fsw,
                 rides_on=fsw, bias_v=7.0)
    _intent.node("CFAN%d_VCC" % s, 7.0, "the TPS61089's internal regulator output (VCC, absolute maximum 7 V, SLVSD38C 7.1)")
    _intent.node("CFAN%d_FSW" % s, 13.6, "the TPS61089's FSW pin, joined to %s through 301 k" % fsw)
    _intent.node("CFAN%d_TACH" % s, 13.67, "the fan's pulse lead at J_FAN%d pin 3, the tach stage's drain: its level NOT READ, bounded by the fan's "
                 "supply (the eFuse's OVLO maximum 13.67 V)" % s)
    _intent.node("CFAN%d_PWM" % s, 13.67, "the fan's PWM lead at J_FAN%d pin 4, the PWM stage's drain, pulled to +5V_S%d by 10 k; the fan's own "
                 "pull-up NOT READ, bounded by its supply" % (s, s))'''

EDITS = [(_OLD_FP, _NEW_FP), (_OLD_LOAD, _NEW_LOAD), (_OLD_FAN, _NEW_FAN)]


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
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once" % new.count(old))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: record l8r2 drafts this change for board B's generator owner and never applies it. Writing the repository's own
# gen_sch_b.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_b.py")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_b.py", "b/gen_sch_b.py", n=0))
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
