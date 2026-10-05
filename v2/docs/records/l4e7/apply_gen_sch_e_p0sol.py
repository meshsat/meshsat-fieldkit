#!/usr/bin/env python3
"""apply_gen_sch_e_p0sol.py: DRAFT for board E's generator owner (task P0-7 of MESHSAT-1357, 5 October 2026: the solar stage's
D-10 and D-16 by circuit alternatives, L4E7-P0SOL.md). NOT APPLIED to the tree; its author ran it only on scratch copies (the tests
also write scratch copies).

Why (L4E7-P0SOL.md; l4e7_p0sol.out): RSENSE1 (R59) put the LT8705A's own input sense amplifier, whose pins are rated -0.3 to +0.3 V
absolute and -100 to +100 mV operating (8705af p.2 and p.5), in the path of two currents no part of the stage bounds on printed
figures: the charge a stiff source pushes into the capacitance behind it when it steps onto the port with the solar guard on
(D-10: -0.3021 V at the pins at the reference loop), and M1's pulsed input current at REQ-016's 25 V corner (D-16: the resistive
peak 0.1174 V). The selected alternative (C) takes U5's own sense out of both paths: CSPIN and CSNIN are tied to VIN, as the sheet
asks when the input sense is not in use (p.12, p.31), so their differential is zero by construction, and the input-current
regulation's sense becomes U23, a second INA169 (U18's part, TI SBOS181F) on the backstop's bank R60 to R64, whose current output
drives IMON_IN (TRK_IMONI) into RIMON_IN with CIMON_IN, where EA2 holds 1.208 V as before (8705af Figure 11). The regulation and the
100 W trip then read the same bank, so the bank's tolerance, drift and heating cancel between them. RIMON_IN R16 becomes 34.0k
(YAGEO RT0603BRD0734KL, C705770): the nominal setting 1.208 V / (1 mA/V x 14 mOhm x 34.0k) = 2.538 A, beside the drafted 2.5485 A.
INP's bottom resistor R97 becomes 24.9k (YAGEO RT0603BRD0724K9L, C136967), so INP stays at or under 18 V, 10 % under its 20 V
absolute maximum, for every PV_F up to 90 V, PV_F's own exclusion line (D-10's INP rows: 18.54 V and 18.29 V before); U21 then
turns on by 10.05 V at the most, under the hold's least 16.42 V.

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else: R59 and the net TRK_VIN removed (U5's VIN, CSPIN and CSNIN, M1's
drain, C13 to C15 and C64 on TRK_VS); U23 and its supply capacitor C79 (class D, the maker's clause) added; R16's value and code;
R97's value and code; TRK_VS's declaration (its load is now M1, Q3); the tracker section's part list; three comments made true.

It is not the whole change: U23 sits beside U18 on the bank's Kelvin pads (a layout obligation: both pairs from the bank's pad
centres, routed together); the regeneration and its gates on the box; the LCSC readings of C705770 and C136967 as single-part
records (the JLCPCB searches of 1 October 2026 filed under inputs/ carry their codes and stock).

ORDER: apply it AFTER this record's apply_gen_sch_e_input_limit.py, apply_gen_sch_e_backstop.py and apply_gen_sch_e_solar_guard.py
(it edits their texts and refuses a generator without them), so after L4-E9's hot swap and L4-E11's entry, which the solar guard
follows, and BEFORE L4-E11's aux draft and d8dec31's input capacitor (it names U23 and C79, neither of which a later draft takes:
the next free C at d8dec31's apply time stays the one it was).

Usage:  apply_gen_sch_e_p0sol.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a draft it follows
is not applied yet, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_p0sol"
R16_NEW = ("34.0k", "C705770")       # YAGEO RT0603BRD0734KL (JLCPCB search of 1 October 2026, inputs/jlc-search-rt0603brd07-30k-2026-10-01.json)
R97_NEW = ("24.9k", "C136967")       # YAGEO RT0603BRD0724K9L (the same search's main page, inputs/jlc-search-rt0603brd07-2026-10-01.json)
ADDS = ("U23", "C79")
REMOVES = ("R59",)
U23 = ('ic("U23", 5, "INA169NA/3K high-side current-shunt monitor, current output: the input-current regulation\'s sense on the bank, into '
       'U5\'s IMON_IN (SOT-23-5: 1 OUT, 2 GND, 3 VIN+, 4 VIN-, 5 V+)", "SOT235", {"1": "TRK_IMONI", "2": "GND", "3": "PV_P", "4": "TRK_VS", '
       '"5": "TRK_VS"}, "C44322")\n'
       'c("C79", "100n", "TRK_VS", "GND", "C", "C14663", bypass=("U23", "5"))\n')
EDITS = [
    # TRK_VS: behind the bank it is now the converter's input itself
    ('# L4-E7R: TRK_VS, between the sense bank (R60 to R64) and RSENSE1 (R59), is a series segment of PV_P at its voltage.\n'
     '_intent.rail("TRK_VS", _intent.rail_volts("PV_P"), 5.68, 6.25, ["R60", "R61", "R62", "R63", "R64"], loads={"R59": 5.68},\n'
     '             v_work=25.0, v_max=25.0, converted=False, series_of="PV_P", note="the panel current past the sense bank, into "\n'
     '             "RSENSE1 (R59); D4, C71 to C74 and U18\'s supply sit on it, the 50 V bulk ahead of the bank on PV_P (L4-E7R)")\n',
     '# L4-E7R, P0-7: TRK_VS, behind the sense bank (R60 to R64), is a series segment of PV_P at its voltage and, since P0-7, the\n'
     '# LT8705A\'s input itself (RSENSE1, R59, and TRK_VIN are gone): M1 (Q3) carries it.\n'
     '_intent.rail("TRK_VS", _intent.rail_volts("PV_P"), 5.68, 6.25, ["R60", "R61", "R62", "R63", "R64"], loads={"Q3": 5.68},\n'
     '             v_work=25.0, v_max=25.0, converted=False, series_of="PV_P", note="the panel current past the sense bank into the "\n'
     '             "converter: U5\'s VIN with CSPIN and CSNIN tied to it, M1\'s drain, C13 to C15, C64, C71 to C74, D4, U18\'s and U23\'s "\n'
     '             "supply; the 50 V bulk ahead of the bank on PV_P (L4-E7R, P0-7)")\n'),
    ('# L4-E7: TRK_VIN, the tracker\'s input behind RSENSE1 (R59), is a series segment of PV_P at its voltage, carried by M1 (Q3).\n'
     '_intent.rail("TRK_VIN", _intent.rail_volts("PV_P"), 5.68, 6.25, "R59", loads={"Q3": 5.68}, v_work=25.0, v_max=25.0,\n'
     '             converted=False, series_of="PV_P", note="the LT8705A\'s input behind RSENSE1 (R59): the bulk C11 to C15, C64, "\n'
     '             "U5\'s VIN and CSNIN, and M1\'s drain; the input-current limit holds its average (L4-E7)")\n',
     '# P0-7: TRK_VIN, the tracker\'s input behind RSENSE1, is gone with R59; U5\'s input is TRK_VS (above).\n'),
    ('c("C13", "10u 50V", "TRK_VIN", "GND", "C10u50"); c("C14", "10u 50V", "TRK_VIN", "GND", "C10u50"); c("C15", "4.7u 50V", "TRK_VIN", "GND", "C10u50")',
     'c("C13", "10u 50V", "TRK_VS", "GND", "C10u50"); c("C14", "10u 50V", "TRK_VS", "GND", "C10u50"); c("C15", "4.7u 50V", "TRK_VS", "GND", "C10u50")   # P0-7'),
    ('# L4-E7 (MESHSAT-1357, v2/docs/records/l4e7/L4E7-STAGE-SETTINGS.md): RSENSE1 of the LT8705A\'s input-current limit (8705af p.31,\n'
     '# Figure 11), from PV_P to TRK_VIN; CSPIN (U5 pin 33) and CSNIN (pin 32) Kelvin at its pads, nothing in series (p.30).\n'
     'r("R59", "15mOhm 1% 2512 (RSENSE1: input-current sense, HoJLR2512-3W-15mR-1%)", "TRK_VS", "TRK_VIN", "RS2512", "C2903494")   # L4-E7R: behind the sense bank\n',
     '# P0-7 (MESHSAT-1357, v2/docs/records/l4e7/L4E7-P0SOL.md): THE INPUT CURRENT IS SENSED ON THE BACKSTOP\'S BANK, NOT BY U5. RSENSE1\n'
     '# (R59) is gone and U5\'s input sense amplifier is not used: CSPIN (pin 33) and CSNIN (pin 32) are tied to VIN (pin 34) on TRK_VS,\n'
     '# as 8705af p.12 and p.31 ask when the input sense is not in use, so the pins\' differential is zero in every state (D-10, a stiff\n'
     '# source stepping onto the port with the guard on, put -0.3021 V on them; D-16, M1\'s pulsed current, took them out of their\n'
     '# +-100 mV range). U23, a second INA169 (U18\'s part, SBOS181F) on the bank\'s Kelvin pads, drives IMON_IN (TRK_IMONI): its output\n'
     '# current into RIMON_IN (R16) with CIMON_IN (C65) is the input current times 1 mA/V times the bank\'s 14 mOhm, and EA2 holds IMON_IN\n'
     '# at 1.208 V as before (8705af Figure 11). The regulation and the trip read the same bank.\n' + U23),
    ('"32": "TRK_VIN", "33": "TRK_VS", "34": "TRK_VIN"',
     '"32": "TRK_VS", "33": "TRK_VS", "34": "TRK_VS"'),
    ('"5": "TRK_VIN", "6": "TRK_VIN", "7": "TRK_VIN", "8": "TRK_VIN"}, "C148250")',
     '"5": "TRK_VS", "6": "TRK_VS", "7": "TRK_VS", "8": "TRK_VS"}, "C148250")'),
    ('c("C64", "100n", "TRK_VIN", "GND", "C", "C14663", bypass=("U5", "34"))',
     'c("C64", "100n", "TRK_VS", "GND", "C", "C14663", bypass=("U5", "34"))'),
    ('r("R16", "31.6k 0.1% 25ppm (RIMON_IN: input-current limit 2.55 A with R59, under the backstop)", "TRK_IMONI", "GND", "R", "C705766")',
     'r("R16", "%s 0.1%% 25ppm (RIMON_IN: input-current limit 2.54 A with U23 on the bank, under the backstop; P0-7)", "TRK_IMONI", "GND", "R", "%s")'
     % R16_NEW),
    ('"R16", "R17", "R59", "C65",',
     '"R16", "R17", "C65", "U23", "C79",'),
    ('r("R97", "28.0k 0.1% 25ppm (INP: high from 9.16 V, 10 % under 20 V to 81 V on PV_F; YAGEO RT0603BRD0728KL, LCSC code owed)", "PV_INP", "GND", "R")',
     'r("R97", "%s 0.1%% 25ppm (INP: high from 10.05 V, 10 %% under 20 V to 90 V on PV_F; YAGEO RT0603BRD0724K9L; P0-7)", "PV_INP", "GND", "R", "%s")'
     % R97_NEW),
    ('                 "10.1 \\"connect the bypass capacitors close to the device pins\\" (p.19); U18\'s V+ (pin 5) on TRK_VS"),\n',
     '                 "10.1 \\"connect the bypass capacitors close to the device pins\\" (p.19); U18\'s V+ (pin 5) on TRK_VS"),\n'
     '    # P0-7 (MESHSAT-1357, 5 October 2026): U23, the regulation\'s INA169 on the same bank, the same maker\'s clause\n'
     '    "C79": ("D", "TI INA139/INA169 SBOS181F, revised February 2017 (v2/vendor/ti/held/ti-ina169-sbos181f.pdf): 9 Power Supply "\n'
     '                 "Recommendations \\"TI recommends placing a 0.1-uF capacitor near the V+ pin on the INA139 or INA169\\" (p.18); "\n'
     '                 "10.1 \\"connect the bypass capacitors close to the device pins\\" (p.19); U23\'s V+ (pin 5) on TRK_VS"),\n'),
    ("TRK_VS at R59's pad take a fast edge ahead of RSENSE1; nothing is in series with CSPIN or CSNIN (8705af p.30).",
     "TRK_VS take a fast edge; since P0-7 U5's CSPIN and CSNIN are tied to its VIN there, nothing in series (8705af p.12, p.30)."),
    ('# L4-E7R: ahead of RSENSE1 at its pad; B6 round 2: the part whose curve the record bounds',
     '# L4-E7R, P0-7: on U5\'s input with C13 to C15; B6 round 2: the part whose curve the record bounds'),
]
# the texts of the drafts this one follows: the input limit's R59, the backstop's U18 and bank, the solar guard's R97
NEEDS = ('r("R59", "15mOhm 1% 2512 (RSENSE1', 'ic("U18", 5, "INA169NA/3K', 'r("R6%d" % _bk, "70mOhm 1% 2512 (backstop sense bank',
         'r("R97", "28.0k 0.1% 25ppm (INP')


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def first_args(text):
    """The first string argument of every call in the text (the references a generator creates by name), read with ast."""
    out = set()
    for n in ast.walk(ast.parse(text)):
        if isinstance(n, ast.Call) and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            out.add(n.args[0].value)
    return out


def patched(text):
    if all(text.count(rep) == 1 for _o, rep in EDITS):
        refuse("already applied (every new text is present)")
    for need_ in NEEDS:
        if need_ not in text:
            refuse("a draft this one follows is not applied (no %s)" % need_.split("(")[0])
    if any(a in first_args(text) for a in ADDS):
        refuse("a reference this draft adds (%s) is already drawn" % ", ".join(a for a in ADDS if a in first_args(text)))
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
    drawn = first_args(new)
    consts = {n.value for n in ast.walk(ast.parse(new)) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    if not all(a in drawn for a in ADDS) or any(r in drawn for r in REMOVES) or "TRK_VIN" in consts:
        refuse("the result does not draw U23 and C79 without R59 and the net TRK_VIN")
    return new


# NOT RELEASED: task P0-7 drafts these values for board E's generator owner and never applies them. Writing the repository's own
# gen_sch_e.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_e.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; P0-7's change waits on an accepted check")
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
