#!/usr/bin/env python3
"""apply_gen_sch_e_entry.py: DRAFT for board E's generator owner (task L4-E11, MESHSAT-1357, fix round of 2 October 2026). NOT
APPLIED to the tree by L4-E11; its author ran it only on scratch copies (the tests write scratch copies).

Why (blocker B1 of the focused check cx30, l4e11_power.out section 3): REQ-015's 9 V is taken at the kit's plug (SESSION, the
first round). The drawn LM5069 enables all its functions only with VIN at POREN, 9.0 V at most (SNVS452G p.5), and its VIN is
DC_P behind the LM74700 ideal diode, at most 9.00 V less 13 mV from a 9.00 V plug before any current flows: no divider makes it
start, and VIN is its current-sense reference, so it cannot be supplied from elsewhere. The TPS48110-Q1 (TI SLUSEE5E, held
back; VS 3.5 to 80 V, 100 V absolute, EN/UVLO and OV at 1.16 to 1.2 V) replaces it: on by 8.44 V and off by 7.95 V of DC_P at
the most, off above 41.22 V, a breaker at 6.36 to 7.14 A after 0.25 to 0.49 ms (TI's loaded row; the in-service maximum from
a 9.00 V plug is 5.98 A with the final round's knee; F1's 80 C column 7.3 A), a short-circuit trip at 10.36 to 13.87 A on the
sense filtered by RISCP x CSCP (about 3 us) and then 5 us, gate-slew inrush of 0.38 to 1.22 A. It limits no power, so the pass
FET carries a start into a resistive fault on its own chart: with the filter and the delays in the scan the drawn CSD19532Q5B
reaches 3.08 of its derated Figure 10, the CSD19536KTT (D2PAK, Figure 4-10) 0.70, by a conservative whole-pulse reading, and
0.74 in a start into a hard short (section 3c). R19
becomes 4.5 mOhm so the breaker sits at TI's characterised 30.6 mV point (RSET 100 Ohm, RIWRN 39.7 k); L2 becomes the
SRF1260-1R0Y, whose 7.51 A carries the breaker's highest current at 98.2 C against its 105 C.

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else: U6's comment and call; R19's and Q7's calls; L4-E9's R20 to
R23 line (UVLO 59.0k over 10.0k at 1 %, OV 332k over 10.0k at 0.1 %); the C5, R24, R25 line (C5 the 22 nF C0G timer, R24 the
39.7k 0.1 % RIWRN, R25 unchanged) with the new parts R80 to R86 and C122 to C125; L2's value text; the footprint map (DGX19,
D2PAK, XT60F); _VEH_T and _VEH_P (the breaker's 7.14 A); the vehicle entry's schematic section; J_DCIN (round 9, 4 October 2026:
record l9stk's DD-3) from the JST VH to the Amass XT60-F (C98734; V1.2: 30 A rated, 60 A instantaneous, -20 to 120 C), the gender
opposite J_BATT's XT60-M, as D-06 (section 6) selected; its nets unchanged. The board's narrative comments and
the intent notes that still name the LM5069 are E11-01's to restate with the regeneration.

FOOTPRINTS OWED (E11-01): DGX19 names meshsat:TI_DGX0019A_VSSOP-19_3x5.1mm_P0.5mm, which does not exist yet (TI's DGX0019A
drawing, SLUSEE5E section 12; pin 16 absent, the symbol's pin 16 a no-connect); D2PAK names KiCad's TO-263-2, whose pads are to
be checked against TI's KTT drawing (1 gate, 2 the drain tab, 3 source) by kisch's map check.

ORDER: apply it AFTER L4-E9's apply_gen_sch_e_hotswap.py (its old texts are that draft's results), and INSTEAD of
apply_gen_sch_e_timer.py (the LM5069's timer): each refuses once the other has run.

Usage:  apply_gen_sch_e_entry.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_entry"
EDITS = [
    ('# LM5069 (ti/ti-lm5069.pdf, VSSOP-10: 1 SENSE 2 VIN 3 UVLO 4 OVLO 5 GND 6 TIMER 7 PWR 8 PGD 9 OUT 10 GATE); the -2 variant restarts after a fault; sense resistor 10 mOhm, pass FET 60 V\n'
     'ic("U6", 10, "LM5069MM-2 hot-swap controller: 9 V on, 41.4 V off, current and power limit", "VSSOP10", {"1": "HS_S", "2": "DC_P", "3": "HS_UVLO", "4": "HS_OVLO", "5": "GND_V", "6": "HS_TIMER", "7": "HS_PWR", "8": "DCIN_PGD", "9": "DC_HS", "10": "HS_GATE"}, "C111822")',
     '# L4-E11 (MESHSAT-1357, fix round, U-04 B1): the LM5069 cannot start from a 9.00 V plug (POREN 9.0 V at most at its VIN, which is also its sense\n'
     '# reference). TPS48110-Q1 (TI SLUSEE5E; DGX VSSOP-19, pin 16 absent: 1 EN/UVLO 2 OV 3 INP 4 FLT_T 5 FLT_I 6 GND 7 IMON 8 IWRN 9 TMR 10 DIODE 11 NC\n'
     '# 12 BST 13 SRC 14 PD 15 PU 17 CS- 18 CS+ 19 ISCP 20 VS): a breaker with a timed overcurrent and a fast short-circuit trip, gate-slew inrush; every\n'
     '# figure is in v2/docs/records/l4e11/l4e11_power.out section 3c. DCIN_PGD is now its fault flag (FLT_I and FLT_T, low on a fault).\n'
     'ic("U6", 20, "TPS48110AQDGXRQ1 high-side driver with protection (entry): on by 8.44 V, off above 41.22 V, breaker 6.36 to 7.14 A, short circuit 10.36 to 13.87 A, auto-retry", "DGX19", '
     '{"1": "HS_UVLO", "2": "HS_OVLO", "3": "HS_INP", "4": "DCIN_PGD", "5": "DCIN_PGD", "6": "GND_V", "7": "GND_V", "8": "HS_IWRN", "9": "HS_TIMER", "10": "GND_V", "11": "NC", '
     '"12": "HS_BST", "13": "DC_HS", "14": "HS_GATE", "15": "HS_PU", "16": "NC", "17": "HS_S", "18": "HS_CSP", "19": "HS_ISCP", "20": "HS_VS"}, "C17556513")'),
    ('r("R19", "10mOhm 1% 2512 (hot-swap sense)", "DC_P", "HS_S", "RS2512"); nfet("Q7", "CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6), hot-swap pass", "HS_GATE", "HS_S", "DC_HS", lcsc="C473333")',
     'r("R19", "4.5mOhm 1% 2512 3W 50ppm (entry sense: 30.6 mV at the breaker, L4-E11)", "DC_P", "HS_S", "RS2512", lcsc="C2985708"); '
     'part("Q7", "Connector_Generic", "Conn_01x03", "CSD19536KTT 100 V N-FET (2.4 mOhm at VGS 10 V, D2PAK; its Figure 4-10 carries a start into a resistive fault, L4-E11), entry pass: 1 G, 2 D tab, 3 S", "D2PAK", '
     '{"1": "HS_GATE", "2": "HS_S", "3": "DC_HS"}, "C2687963")'),
    ('# L4-E9 (MESHSAT-1357, D-02 and D-07): the OVLO clear of CS101 at 36 V (R22 and R23 at 0.1 %) and the power limit at 5 mV or more at 43.18 V.\n'
     'r("R20", "100k 1%", "DC_P", "HS_UVLO"); r("R21", "38.3k 1% (UVLO: 9 V)", "HS_UVLO", "GND_V"); r("R22", "100k 0.1%", "DC_P", "HS_OVLO"); r("R23", "6.42k 0.1% (OVLO: 41.4 V)", "HS_OVLO", "GND_V")',
     '# L4-E11 (MESHSAT-1357, fix round): UVLO on by 8.44 V and off by 7.95 V of DC_P at the most (9.00 V at the plug gives DC_P 8.43 V at 5.98 A, hot);\n'
     '# OV off above 39.60 to 41.22 V (over CS101\'s 38.83 V, under D10\'s 42.4 V at -20 C); INP high from 7.23 V and 18.4 V at the 64.5 V clamp; TI\'s VS filter.\n'
     'r("R20", "59.0k 1%", "DC_P", "HS_UVLO"); r("R21", "10.0k 1% (UVLO: on by 8.44 V, L4-E11)", "HS_UVLO", "GND_V"); r("R22", "332k 0.1%", "DC_P", "HS_OVLO"); r("R23", "10.0k 0.1% (OV: off above 41.22 V, L4-E11)", "HS_OVLO", "GND_V")\n'
     'r("R84", "100k 1%", "DC_P", "HS_INP"); r("R85", "39k 1% (INP: high from 7.23 V)", "HS_INP", "GND_V"); r("R86", "100R 1% (VS filter, SLUSEE5E 9.5)", "DC_P", "HS_VS"); c("C124", "100n 100V", "HS_VS", "GND_V", "C0805")'),
    ('c("C5", "100n (TIMER)", "HS_TIMER", "GND_V"); r("R24", "22k 1% (PWR: power limit, 5.06 mV at 43.18 V at its low corner)", "HS_PWR", "GND_V"); r("R25", "10k", "DCIN_PGD", "+3V3_E6")',
     'c("C5", "22n C0G 5% 50V 1206 (CTMR: 0.25 to 0.49 ms, retry 0.5 s, L4-E11)", "HS_TIMER", "GND_V", "C10u50", lcsc="C97929"); '
     'r("R24", "39.7k 0.1% (RIWRN: breaker 6.36 to 7.14 A with R19, L4-E11)", "HS_IWRN", "GND_V", lcsc="C861872"); r("R25", "10k", "DCIN_PGD", "+3V3_E6")\n'
     'r("R80", "100R 0.1% (RSET)", "DC_P", "HS_CSP"); r("R81", "3.01k 1% (RISCP: short circuit 10.36 to 13.87 A, filtered)", "DC_P", "HS_ISCP"); c("C125", "1n C0G 100V (CSCP, SLUSEE5E 9.5)", "HS_ISCP", "HS_S")\n'
     'r("R82", "36.5k 1% (R1: gate slew)", "HS_PU", "HS_GATE"); r("R83", "10R 1% (R2: damping)", "HS_GATE", "HS_SLEW"); c("C122", "10n C0G 5% 100V 1206 (C1: gate slew, 17.3 to 24.7 V/ms)", "HS_SLEW", "GND_V", "C10u50", lcsc="C184799")\n'
     'c("C123", "1u 25V X7R (CBST: over Qg and 10 x C1, SLUSEE5E Equation 4)", "HS_BST", "DC_HS")'),
    ('"Bourns SRF1260-1R5Y dual-winding choke, common-mode connection (each winding carries the line current: 6.89 A Irms and 9.15 A Isat in the series column, 1.5 uH per winding)',
     '"Bourns SRF1260-1R0Y dual-winding choke, common-mode connection (each winding carries the line current: 7.51 A Irms and 11.8 A Isat in the series column, 1.0 uH per winding; L4-E11: the breaker\'s 7.14 A)'),
    ('           "DFN6S": "meshsat:Sensirion_DFN-6-1EP_2.44x2.44mm_P0.8mm_EP1.25x1.7mm"})',
     '           "DFN6S": "meshsat:Sensirion_DFN-6-1EP_2.44x2.44mm_P0.8mm_EP1.25x1.7mm",\n'
     '           "DGX19": "meshsat:TI_DGX0019A_VSSOP-19_3x5.1mm_P0.5mm", "D2PAK": "Package_TO_SOT_SMD:TO-263-2",\n'
     '           "XT60F": "Connector_AMASS:AMASS_XT60-F_1x02_P7.20mm_Vertical"})   # L4-E11: the entry\'s U6 (land owed) and Q7; J_DCIN (round 9)'),
    ('part("J_DCIN", "Connector_Generic", "Conn_01x02", "JST-VH socket, 10 A: vehicle and shore DC in 9 to 36 V (lead from the D38999 wall receptacle DC pair): + -", "VH2", {"1": "DC_IN", "2": "GND_V"}, "C274411")',
     '# L4-E11 (MESHSAT-1357, D-06 and round 9, DD-3 of record l9stk): J_DCIN leaves the JST VH (10 A at AWG 16, 7 A at AWG 18, 105 C) for\n'
     '# an Amass XT60-F (V1.2: 30 A rated, 60 A instantaneous, -20 to 120 C, 12 AWG), the gender opposite J_BATT\'s XT60-M so the pack lead\n'
     '# cannot mate it; the inside lead ends in an XT60-M. Pad 1 is the + contact, read against KiCad\'s AMASS land at regeneration.\n'
     'part("J_DCIN", "Connector_Generic", "Conn_01x02", "Amass XT60-F, 30 A: vehicle and shore DC in 9 to 36 V (the inside lead from the D38999 wall receptacle DC pair, on an XT60-M): 1 +, 2 -", "XT60F", {"1": "DC_IN", "2": "GND_V"}, "C98734")'),
    ('_VEH_T, _VEH_P = 6.15, 6.15',
     '_VEH_T, _VEH_P = 7.14, 7.14   # L4-E11: the TPS48110 breaker\'s highest current with R19 4.5 mOhm (was the LM5069\'s 6.15 A)'),
    ('"U6", "R19", "Q7", "R20", "R21", "R22", "R23", "C5", "R24", "R25", "Q8"',
     '"U6", "R19", "Q7", "R20", "R21", "R22", "R23", "R84", "R85", "R86", "C124", "C5", "R24", "R25", "R80", "R81", "C125", "R82", "R83", "C122", "C123", "Q8"'),
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


# NOT RELEASED: task L4-E11 drafts this value for board E's generator owner and never applies it. Writing the repository's
# own gen_sch_e.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an
# accepted check of L4-E11 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written
# (the tests do, on scratch copies).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_e.py")
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
