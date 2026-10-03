#!/usr/bin/env python3
"""apply_gen_sch_a_vbus20ov.py: DRAFT for board A's generator owner (Layer 8 record l8r2, item 2, R-48 / S-111, MESHSAT-1357,
3 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies.

The defect (S-111, R-48; records/s120 section 8): with U2's high-side Q2 shorted, VBUS20 follows VIN_RAW less Q5's body diode (35.2 V
at 36 V in, 41.7 V at board E's lockout); with R6 open or FB shorted U2 drives the bus with nothing on board A to bound it. Either
passes U3's absolute 32 V (VBUS, ACP, ACN) and, while the charger still switches, Q7's 30 V; no clamp and no exemption.

The selection (the record, section 2): an SMCJ22A on VBUS20 is REJECTED on the printed data: its breakdown (24.4 to 26.9 V at 1 mA)
lies under voltages the sources hold steadily below board E's breaker trip (6.364 A): the solar tracker's drafted ceiling 28.28 to
30.15 V and a 24 V vehicle charging at 27 to 29 V would push amperes through it continuously, tens of watts against its
steady-state rating, and it would also take current from a Q2 short with the vehicle on. The SELECTED correction is an independent
over-voltage cut-off that removes VBUS20's energy in both faults: a TPS48110-Q1 U45 (the controller L4-E11 selected for board E's
entry, TI SLUSEE5E) driving a CSD19532Q5B Q41 (board A's own 100 V FET and land) in series with board A's VIN_RAW at its entry,
its OV pin on VBUS20 through R241 200k over R242 10.0k (0.1 %): cut at 24.25 to 25.31 V (V(OVR) 1.16 to 1.20 V, the OV leakage
included), back at 23.00 to 23.84 V (V(OVF) 1.10 to 1.13 V); turn-off 2.6 to 4 us (tPD(OV_OFF)). The cut is above the bus's in-
service bound 23.40 V (s120, INFERRED) and under U3's recommended 26 V and ACOV's 26.0 V; after the cut the bus reaches at most
25.9 V with Q2 shorted and 26.5 V with FB open (U2 pumping VIN_RAW's 32 uF down to U34's 8.08 V UV, and L1's energy: INFERRED), 5.5
V under U3's absolute 32 V. Cutting VIN_RAW at board A removes the vehicle AND the solar source, so U34's bleed, which the UV of the
cut engages, only ever drains capacitors. Overcurrent, short-circuit and remote temperature are not used (IWRN, TMR, IMON and DIODE to
GND, ISCP to CS-; SLUSEE5E Table 5-1); EN/UVLO on VIN_RAW_IN through R239 33.2k over R240 10.0k (on by 4.93 to 5.26 V, under U34's
8.08 V UV); INP through R243 100k over R244 39k (high from 7.23 V, L4-E11's divider); VS through R245 100 R with C244 100 nF 100 V;
the gate slewed by R246 36.5k, R247 10 R and C245 10 nF C0G (L4-E11's network, 17.3 to 24.7 V/ms); BST C246 1 uF 25 V.

What it changes in v2/ecad/tools/gen_sch_a.py: the footprint table gains DGX19 (meshsat:TI_DGX0019A_VSSOP-19_3x5.1mm_P0.5mm, the land
L4-E11's E11-01 owes); the dock's J_VR1 to J_VR4 move to the new net VIN_RAW_IN and the cut-off's block follows the J_VN loop;
VIN_RAW's declaration takes Q41 as its source and switch (it was always on: this board now switches it) and VIN_RAW_IN is declared
with the dock pins as its source; a section lists the parts. Composed after board A's power drafts and l8gnd's, before d8dec31's
mainpb (l8r2_drafts.out). Owed: the DGX-19 land, Q41's SOA under board E's retries (Layer 9), IF-AE-DOCK's alias VIN_RAW_IN /
VIN_RAW (Layer 5) and s120's VBUS20 membership re-read (R241 is a new member).

Usage:  apply_gen_sch_a_vbus20ov.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_vbus20ov"
GEN = "gen_sch_a.py"
ADDS = ("U45", "Q41", "R239", "R240", "R241", "R242", "R243", "R244", "R245", "R246", "R247", "C244", "C245", "C246")
NETS = ("VIN_RAW_IN", "VCO_UVLO", "VCO_OV", "VCO_INP", "VCO_VS", "VCO_GATE", "VCO_PU", "VCO_SLEW", "VCO_BST")

_BLOCK = (
    "# --- S-111 / R-48, drafted by Layer 8 record l8r2 (MESHSAT-1357, 3 October 2026): VBUS20's OVER-VOLTAGE CUT-OFF IN VIN_RAW. A shorted Q2\n"
    "# puts VIN_RAW on VBUS20 and an open FB lets U2 drive it, past U3's absolute 32 V. U45 (TPS48110-Q1, TI SLUSEE5E) turns Q41 off within\n"
    "# 2.6 to 4 us once VBUS20 passes 24.25 to 25.31 V (OV on R241 200k / R242 10.0k, 0.1 %), removing the vehicle AND the solar source from\n"
    "# this board; it closes again under 23.00 to 23.84 V. Over-current, short circuit and remote temperature unused (IWRN, TMR, IMON, DIODE to\n"
    "# GND, ISCP to CS-; SLUSEE5E Table 5-1). An SMCJ22A on VBUS20 was rejected: sources hold the bus in its breakdown under board E's breaker\n"
    "# trip (the record l8r2, section 2). Gate slew, BST and VS filter as L4-E11's entry on board E.\n"
    'ic("U45", 20, "TPS48110AQDGXRQ1 VBUS20 over-voltage cut-off in VIN_RAW: off above 24.25 to 25.31 V of VBUS20, on by 5.26 V of VIN_RAW_IN", "DGX19", '
    '{"1": "VCO_UVLO", "2": "VCO_OV", "3": "VCO_INP", "4": "NC", "5": "NC", "6": "GND", "7": "GND", "8": "GND", "9": "GND", "10": "GND", "11": "NC", '
    '"12": "VCO_BST", "13": "VIN_RAW", "14": "VCO_GATE", "15": "VCO_PU", "16": "NC", "17": "VCO_VS", "18": "VCO_VS", "19": "VCO_VS", "20": "VCO_VS"}, "C17556513")\n'
    'nfet("Q41", "CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6): the VBUS20 cut-off in VIN_RAW", "VCO_GATE", "VIN_RAW_IN", "VIN_RAW", lcsc="C473333")\n'
    'r("R239", "33.2k 1%", "VIN_RAW_IN", "VCO_UVLO"); r("R240", "10.0k 1% (EN: on by 4.93 to 5.26 V)", "VCO_UVLO", "GND", lcsc="C25804")\n'
    'r("R241", "200k 0.1%", "VBUS20", "VCO_OV"); r("R242", "10.0k 0.1% (OV: VBUS20 over 24.25 to 25.31 V)", "VCO_OV", "GND")\n'
    'r("R243", "100k 1%", "VIN_RAW_IN", "VCO_INP", lcsc="C25803"); r("R244", "39k 1% (INP: high from 7.23 V)", "VCO_INP", "GND")\n'
    'r("R245", "100R 1% (VS filter, SLUSEE5E 9.5)", "VIN_RAW_IN", "VCO_VS", lcsc="C22775"); c("C244", "100n 100V", "VCO_VS", "GND", "C10u", lcsc="C106243")\n'
    'r("R246", "36.5k 1% (R1: gate slew)", "VCO_PU", "VCO_GATE"); r("R247", "10R 1% (R2: damping)", "VCO_GATE", "VCO_SLEW")\n'
    'c("C245", "10n C0G 5% 100V 1206 (C1: gate slew)", "VCO_SLEW", "GND", "Capacitor_SMD:C_1206_3216Metric", lcsc="C184799"); c("C246", "1u 25V X7R (CBST: over Qg and 10 x C1, SLUSEE5E Equation 4)", "VCO_BST", "VIN_RAW")\n'
    '_intent.rail("VIN_RAW_IN", 12.0, _VIN_RAW_A, _VIN_RAW_A, ["J_VR1", "J_VR2", "J_VR3", "J_VR4"], loads={"Q41": _VIN_RAW_A}, budget=0.02, share=0.015, v_work=36.0, converted=False,\n'
    '             always_on=True, always_on_why="shore, vehicle and panel input arriving over the dock behind board E\'s entry; this board switches it only through Q41, downstream",\n'
    '             note="VIN_RAW as it arrives on the dock pins J_VR1 to J_VR4, ahead of the VBUS20 cut-off Q41 (S-111, record l8r2); the alias of board E\'s VIN_RAW")\n'
    '_intent.node("VCO_OV", 2.9, "U45\'s OV pin on VBUS20 through 200k / 10.0k: 2.86 V at a 60 V bus, under the pin\'s 20 V absolute maximum (SLUSEE5E 6.1)")\n'
    '_intent.node("VCO_UVLO", 15.0, "U45\'s EN/UVLO pin on VIN_RAW_IN through 33.2k / 10.0k: 14.9 V at the 64.5 V clamp, under 20 V (SLUSEE5E 6.1)")\n'
    '_intent.node("VCO_INP", 18.2, "U45\'s INP pin on VIN_RAW_IN through 100k / 39k: 18.1 V at the 64.5 V clamp, under 20 V (SLUSEE5E 6.1)")\n'
    '_intent.node("VCO_GATE", 64.5 + 13.0, "Q41\'s gate: up to the charge pump\'s 13 V over VIN_RAW (SLUSEE5E V(BST - SRC) turn-off 13 V maximum)", rides_on="VIN_RAW", bias_v=13.0)\n'
    '_intent.node("VCO_BST", 64.5 + 13.0, "U45\'s BST, at most 13 V over its SRC VIN_RAW (SLUSEE5E)", rides_on="VIN_RAW", bias_v=13.0)\n')

EDITS = [
    ('"L6060": "Inductor_SMD:L_Coilcraft_XAL6060-XXX", "L6030"',
     '"L6060": "Inductor_SMD:L_Coilcraft_XAL6060-XXX", "DGX19": "meshsat:TI_DGX0019A_VSSOP-19_3x5.1mm_P0.5mm", "L6030"'),
    ('    part("J_VR%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, VIN_RAW (Mill-Max 0858 class, dock block; EQ-16)", "MMPIN", {"1": "VIN_RAW"})\n'
     '    part("J_VN%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, VIN_RAW return (Mill-Max 0858 class, dock block; EQ-16)", "MMPIN", {"1": "GND"})\n',
     '    part("J_VR%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, VIN_RAW_IN (Mill-Max 0858 class, dock block; EQ-16; ahead of the cut-off Q41)", "MMPIN", {"1": "VIN_RAW_IN"})\n'
     '    part("J_VN%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, VIN_RAW return (Mill-Max 0858 class, dock block; EQ-16)", "MMPIN", {"1": "GND"})\n' + _BLOCK),
    ('_intent.rail("VIN_RAW", 12.0, _VIN_RAW_A, _VIN_RAW_A, ["J_VR1", "J_VR2", "J_VR3", "J_VR4"], loads=',
     '_intent.rail("VIN_RAW", 12.0, _VIN_RAW_A, _VIN_RAW_A, "Q41", loads='),
    ('             always_on=True, always_on_why="shore and vehicle input arriving over the dock behind board E\'s own 10 A blade and ideal diode; this board does not switch it, it consumes it", note=',
     '             switch="Q41", enable_net="VCO_GATE", note="SWITCHED since record l8r2 (S-111): Q41 cuts it when VBUS20 passes 24.25 to 25.31 V. " '),
    ("_listed = {r for _, refs in SECTIONS for r in refs}\n",
     'SECTIONS.append(("VBUS20 OVER-VOLTAGE CUT-OFF IN VIN_RAW (S-111): TPS48110 U45 AND Q41", ["U45", "Q41", "R239", "R240", "R241", "R242", "R243", "R244", "R245", "R246", "R247", "C244", "C245", "C246"]))   # Layer 8 record l8r2\n'
     "_listed = {r for _, refs in SECTIONS for r in refs}\n"),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def in_use(text, ref):
    return re.search(r'(?:part|ic|r|c|tp|nfet|vh2|synth|q|esd|efuse)\(\s*"%s"' % re.escape(ref), text) is not None


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


# NOT RELEASED: record l8r2 drafts this change for the board's generator owner and never applies it. Writing the repository's own
# generator is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check of
# this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", GEN)
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/" + GEN, "b/" + GEN, n=0))
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
