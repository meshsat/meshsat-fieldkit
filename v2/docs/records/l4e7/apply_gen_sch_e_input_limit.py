#!/usr/bin/env python3
"""apply_gen_sch_e_input_limit.py: DRAFT for board E's generator owner (task L4-E7, MESHSAT-1357, 1 October 2026). NOT
APPLIED to the tree by L4-E7; its author ran it only on scratch copies with --check (the tests also write scratch copies).

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else: the LT8705A's input-current limit (8705af p.31, Figure 11)
made real. As drawn, U5's CSPIN, CSNIN and VIN all sit on PV_P (the sense tied off, p.12) and IMON_IN has R16 10k alone, so
no input limit acts. After it:
  - R59 (new), RSENSE1: 15 mOhm, Milliohm HoJLR2512-3W-15mR-1%, LCSC C2903494, from PV_P to the new net TRK_VIN; CSPIN (pin
    33) stays on PV_P and CSNIN (pin 32) moves to TRK_VIN, Kelvin at R59's pads (no series resistance, p.30);
  - TRK_VIN takes the converter side, as Figure 1 (p.13) draws it: U5's VIN (pin 34) and its C64, the bulk C11 to C15 and
    M1's drain (Q3 pins 5 to 8), so R59 carries the smoothed input current; PV_P keeps F2, D4, R8 (the hold), R14 and TP5;
  - R16, RIMON_IN: 23.2k 0.1 % 25 ppm/K, YAGEO RT0603BRD0723K2L, LCSC C861244 (the setting 1.208 V / (1 mmho x 15 mOhm x
    23.2k) = 3.4713 A), and C65 (new), CIMON_IN: 100 nF X7R 0603, LCSC C14663, above p.31's minimum and at its 0.1 uF end;
  - the declarations: PV_P's load is R59, and TRK_VIN is declared a series segment of PV_P at PV_P's own voltage (read with
    intent.rail_volts), carried by Q3; the tracker section lists R59 and C65.

It is not the whole change: the layout owes R59's Kelvin taps and placement (v2/docs/layout-constraints/E.md), and the
regeneration's gates; the requirement records that name the 225 uF "on PV_P" now see it behind R59 (their owners restate
them). After any application l4e5's and this record's pins of the netlist refuse by design. R10 (L4-E5) is not touched.

Usage:  apply_gen_sch_e_input_limit.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_input_limit"
EDITS = [
    ('{"1": "PV_P", "2": "GND"}, "C454360")',
     '{"1": "TRK_VIN", "2": "GND"}, "C454360")   # L4-E7: behind RSENSE1 (R59)'),
    ('c("C13", "10u 50V", "PV_P", "GND", "C10u50"); c("C14", "10u 50V", "PV_P", "GND", "C10u50"); c("C15", "4.7u 50V", "PV_P", "GND", "C10u50")',
     'c("C13", "10u 50V", "TRK_VIN", "GND", "C10u50"); c("C14", "10u 50V", "TRK_VIN", "GND", "C10u50"); c("C15", "4.7u 50V", "TRK_VIN", "GND", "C10u50")\n'
     '# L4-E7 (MESHSAT-1357, v2/docs/records/l4e7/L4E7-STAGE-SETTINGS.md): RSENSE1 of the LT8705A\'s input-current limit (8705af p.31,\n'
     '# Figure 11), from PV_P to TRK_VIN; CSPIN (U5 pin 33) and CSNIN (pin 32) Kelvin at its pads, nothing in series (p.30).\n'
     'r("R59", "15mOhm 1% 2512 (RSENSE1: input-current sense, HoJLR2512-3W-15mR-1%)", "PV_P", "TRK_VIN", "RS2512", "C2903494")'),
    ('"32": "PV_P", "33": "PV_P", "34": "PV_P"',
     '"32": "TRK_VIN", "33": "PV_P", "34": "TRK_VIN"'),
    ('"4": "TRK_TG1", "5": "PV_P", "6": "PV_P", "7": "PV_P", "8": "PV_P"}, "C148250")',
     '"4": "TRK_TG1", "5": "TRK_VIN", "6": "TRK_VIN", "7": "TRK_VIN", "8": "TRK_VIN"}, "C148250")'),
    ('c("C64", "100n", "PV_P", "GND", "C", "C14663", bypass=("U5", "34"))',
     'c("C64", "100n", "TRK_VIN", "GND", "C", "C14663", bypass=("U5", "34"))'),
    ('r("R16", "10k", "TRK_IMONI", "GND"); r("R17", "10k", "TRK_IMONO", "GND")',
     'r("R16", "23.2k 0.1% 25ppm (RIMON_IN: input-current limit 3.47 A with R59)", "TRK_IMONI", "GND", "R", "C861244"); '
     'c("C65", "100n (CIMON_IN)", "TRK_IMONI", "GND", "C", "C14663"); r("R17", "10k", "TRK_IMONO", "GND")   # L4-E7'),
    ('loads={"F2" if _pvn == "PV_IN" else "U5": 5.68}',
     'loads={"F2" if _pvn == "PV_IN" else "R59": 5.68}'),
    ('# S-09 / A03 / F-IN-01, 26 September 2026: D4 is a unidirectional SMCJ28A (Littelfuse, LCSC C224047) and had GND on\n',
     '# L4-E7: TRK_VIN, the tracker\'s input behind RSENSE1 (R59), is a series segment of PV_P at its voltage, carried by M1 (Q3).\n'
     '_intent.rail("TRK_VIN", _intent.rail_volts("PV_P"), 5.68, 6.25, "R59", loads={"Q3": 5.68}, v_work=25.0, v_max=25.0,\n'
     '             converted=False, series_of="PV_P", note="the LT8705A\'s input behind RSENSE1 (R59): the bulk C11 to C15, C64, "\n'
     '             "U5\'s VIN and CSNIN, and M1\'s drain; the input-current limit holds its average (L4-E7)")\n'
     '# S-09 / A03 / F-IN-01, 26 September 2026: D4 is a unidirectional SMCJ28A (Littelfuse, LCSC C224047) and had GND on\n'),
    ('"R14", "R15", "R16", "R17", "C24"',
     '"R14", "R15", "R16", "R17", "R59", "C65", "C24"'),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
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


# NOT RELEASED: task L4-E7 drafts these values for board E's generator owner and never applies them. Writing the
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
