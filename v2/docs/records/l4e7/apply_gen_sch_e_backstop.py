#!/usr/bin/env python3
"""apply_gen_sch_e_backstop.py: DRAFT for board E's generator owner (task L4-E7R, MESHSAT-1357, 1 October 2026). NOT
APPLIED to the tree by L4-E7; its author ran it only on scratch copies (the tests also write scratch copies).

The control decision of L4E7-CONTROL-DECISION.md: a hardware 100 W backstop under the LT8705A's input-current limit. It
edits the text apply_gen_sch_e_input_limit.py leaves, so it applies AFTER that draft and refuses a generator that does not
carry it. What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else:
  - U18 (new): TI INA250A2PWR, LCSC C2859736, a current monitor with its own 2 mOhm shunt, 500 mV/A (SBOS511C p.3 pins,
    p.6 gain), in series ahead of RSENSE1: IN+ (pins 14 to 16) on PV_P, IN- (pins 1 to 3) on the new net TRK_VS; SH+ to
    VIN+ and SH- to VIN- unfiltered (p.3), REF to GND for unidirectional operation (p.15), VS from TRK_LDO33 with C66;
  - R59 (RSENSE1) moves from PV_P to TRK_VS, and U5's CSPIN (pin 33) with it, Kelvin at R59's pads; CSNIN (pin 32) and VIN
    (pin 34) stay on TRK_VIN, so U18 carries the stage's whole input but R8, R14, D4 and TP5;
  - R60 28k 0.1 % 25 ppm/K (YAGEO RT0603BRD0728KL, LCSC C705756) over R61 7.87k 0.1 % 25 ppm/K (RT0603BRD077K87L, LCSC
    C861565) divide U18's output into U19's INB;
  - U19 (new): TI TPS3701DDCR, LCSC C132788 (SBVS240C p.3): INB (pin 4) the divider, OUTB (pin 6) on the new net
    TRK_SWEN, INA (pin 3) tied to TRK_LDO33 so OUTA (pin 1, left open) never asserts, VDD from TRK_LDO33 with C67;
  - U5's SWEN (pin 36, QFN only, 8705af p.11) moves from TRK_INTVCC to TRK_SWEN, with R62 100k (LCSC C25803) from
    TRK_LDO33 and C68 1 uF to GND: OUTB low stops switching, and the restart passes the soft start (p.14, Figure 2);
  - R16, RIMON_IN: 23.2k to 26.1k 0.1 % 25 ppm/K (RT0603BRD0726K1L, LCSC C728586), the regulation coordinated below the
    backstop (1.208 V / (1 mmho x 15 mOhm x 26.1k) = 3.0856 A);
  - the declarations: PV_P's load is U18; TRK_VS is a series segment of PV_P at PV_P's voltage, from U18 to R59; TRK_ISP and
    TRK_ISN are nodes at the panel's 25 V; the tracker section lists the new parts; the footprint key TSSOP16.

It is not the whole change: the layout owes U18's placement in the panel current path and R59's Kelvin taps (the layout
constraints of board E), and the regeneration's gates; the record's and l4e5's pins of the netlist refuse by design after
any application. R10 (L4-E5) is not touched.

Usage:  apply_gen_sch_e_backstop.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, the input
limit draft is not applied yet, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_backstop"
BLOCK = (
    '# L4-E7R (MESHSAT-1357, v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md): THE 100 W BACKSTOP. U18 (INA250A2, its own 2 mOhm\n'
    '# shunt, 500 mV/A; SBOS511C p.3) carries the stage\'s input from PV_P to TRK_VS ahead of RSENSE1; SH+ to VIN+ and SH- to\n'
    '# VIN- unfiltered (p.3), REF to GND for unidirectional operation (p.15), VS from TRK_LDO33. R60 over R61 divide its output\n'
    '# into U19\'s INB (TPS3701, SBVS240C p.3); past the trip OUTB pulls SWEN (U5 pin 36) low and switching stops (8705af p.11);\n'
    '# R62 and C68 set the restart, which passes the soft start (p.14). INA tied to TRK_LDO33 keeps OUTA released, unused.\n'
    'FP.update({"TSSOP16": "Package_SO:TSSOP-16_4.4x5mm_P0.65mm"})\n'
    'ic("U18", 16, "INA250A2PWR current monitor, 2 mOhm integrated shunt, 500 mV/A (TSSOP-16: 1-3 IN-, 4 SH-, 5 VIN-, 6 8 11 GND, '
    '7 REF, 9 OUT, 10 VS, 12 VIN+, 13 SH+, 14-16 IN+)", "TSSOP16", {"1": "TRK_VS", "2": "TRK_VS", "3": "TRK_VS", "4": "TRK_ISN", '
    '"5": "TRK_ISN", "6": "GND", "7": "GND", "8": "GND", "9": "TRK_ISO", "10": "TRK_LDO33", "11": "GND", "12": "TRK_ISP", '
    '"13": "TRK_ISP", "14": "PV_P", "15": "PV_P", "16": "PV_P"}, "C2859736")\n'
    'c("C66", "100n", "TRK_LDO33", "GND", "C", "C14663", bypass=("U18", "10"))\n'
    'r("R60", "28k 0.1% 25ppm (backstop divider top)", "TRK_ISO", "TRK_BKS", "R", "C705756"); '
    'r("R61", "7.87k 0.1% 25ppm (backstop divider bottom)", "TRK_BKS", "GND", "R", "C861565")\n'
    'ic("U19", 6, "TPS3701DDCR window comparator, OUTB the 100 W backstop (SOT-23-6: 1 OUTA, 2 GND, 3 INA, 4 INB, 5 VDD, 6 OUTB)", '
    '"TSOT6", {"1": "NC", "2": "GND", "3": "TRK_LDO33", "4": "TRK_BKS", "5": "TRK_LDO33", "6": "TRK_SWEN"}, "C132788")\n'
    'c("C67", "100n", "TRK_LDO33", "GND", "C", "C14663", bypass=("U19", "5"))\n'
    'r("R62", "100k (SWEN pull-up)", "TRK_LDO33", "TRK_SWEN", "R", "C25803"); c("C68", "1u (SWEN restart delay)", "TRK_SWEN", "GND")\n'
    '_intent.node("TRK_ISP", 25.0, "U18\'s SH+ and VIN+ (pins 13 and 12): the integrated shunt\'s supply-side Kelvin, at PV_P\'s "\n'
    '             "voltage, at most the cold panel\'s 25 V open circuit (SBOS511C p.3; REQ-016)")\n'
    '_intent.node("TRK_ISN", 25.0, "U18\'s SH- and VIN- (pins 4 and 5): the integrated shunt\'s load-side Kelvin, at TRK_VS\'s "\n'
    '             "voltage, at most the cold panel\'s 25 V open circuit (SBOS511C p.3; REQ-016)")\n')
EDITS = [
    ('r("R59", "15mOhm 1% 2512 (RSENSE1: input-current sense, HoJLR2512-3W-15mR-1%)", "PV_P", "TRK_VIN", "RS2512", "C2903494")',
     'r("R59", "15mOhm 1% 2512 (RSENSE1: input-current sense, HoJLR2512-3W-15mR-1%)", "TRK_VS", "TRK_VIN", "RS2512", "C2903494")   '
     '# L4-E7R: behind U18\n' + BLOCK.rstrip("\n")),
    ('"32": "TRK_VIN", "33": "PV_P", "34": "TRK_VIN", "35": "TRK_INTVCC", "36": "TRK_INTVCC"',
     '"32": "TRK_VIN", "33": "TRK_VS", "34": "TRK_VIN", "35": "TRK_INTVCC", "36": "TRK_SWEN"'),
    ('r("R16", "23.2k 0.1% 25ppm (RIMON_IN: input-current limit 3.47 A with R59)", "TRK_IMONI", "GND", "R", "C861244"); ',
     'r("R16", "26.1k 0.1% 25ppm (RIMON_IN: input-current limit 3.09 A with R59, under the U18 backstop)", "TRK_IMONI", "GND", "R", "C728586"); '),
    ('loads={"F2" if _pvn == "PV_IN" else "R59": 5.68}',
     'loads={"F2" if _pvn == "PV_IN" else "U18": 5.68}'),
    ('# L4-E7: TRK_VIN, the tracker\'s input behind RSENSE1 (R59), is a series segment of PV_P at its voltage, carried by M1 (Q3).\n',
     '# L4-E7R: TRK_VS, between U18\'s shunt and RSENSE1 (R59), is a series segment of PV_P at its voltage.\n'
     '_intent.rail("TRK_VS", _intent.rail_volts("PV_P"), 5.68, 6.25, "U18", loads={"R59": 5.68}, v_work=25.0, v_max=25.0,\n'
     '             source_ic="the INA250A2\'s IN- pins 1 to 3 are its integrated shunt\'s load end, a power path rated 15 A "\n'
     '             "continuous from -40 to 85 C (SBOS511C p.5)",\n'
     '             converted=False, series_of="PV_P", note="the panel current past U18\'s 2 mOhm shunt, into RSENSE1 (R59) and "\n'
     '             "U5\'s CSPIN; the 100 W backstop measures it (L4-E7R)")\n'
     '# L4-E7: TRK_VIN, the tracker\'s input behind RSENSE1 (R59), is a series segment of PV_P at its voltage, carried by M1 (Q3).\n'),
    ('"R14", "R15", "R16", "R17", "R59", "C65", "C24"',
     '"R14", "R15", "R16", "R17", "R59", "C65", "U18", "U19", "R60", "R61", "R62", "C66", "C67", "C68", "C24"'),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if 'r("R59", ' not in text:
        refuse("apply_gen_sch_e_input_limit.py is not applied (no R59): the old text occurs 0 times, not once")
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


# NOT RELEASED: task L4-E7R drafts these values for board E's generator owner and never applies them. Writing the
# repository's own gen_sch_e.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and
# names an accepted check of L4-E7 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be
# written (the tests do, on scratch copies).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_e.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; L4-E7's values wait on an accepted check")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_e.py", "b/gen_sch_e.py", n=0))
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
