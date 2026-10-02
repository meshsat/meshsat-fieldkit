#!/usr/bin/env python3
"""apply_gen_sch_e_solar_guard.py: DRAFT for board E's generator owner (task L4-E7, MESHSAT-1357, 2 October 2026; the owner's
amendment of 2 October 2026, 14:20, item 3: the solar-fault remedies). NOT APPLIED to the tree by L4-E7; its author ran it only on
scratch copies (the tests also write scratch copies).

Why (L4E7-CONTROL-DECISION.md, "The solar-fault remedies"; l4e7_stage_settings.out section 10): the panel lead's derivation left
two open defects, D-10 and D-11 in L4-E9's register. A stiff 36 V source on the panel port (the kit's own declared source range)
drives the clamp D4 into continuous conduction, two orders of magnitude over its rating; a reversed panel conducts through D4
forward (DECISION-31's note E-N1). The selected remedies, one for each fault, both from parts already in the design:
  - for the 36 V source, U21, a TPS48110-Q1 (TI SLUSEE5E, held back) as an over-voltage cut-off on the high side in TI's own
    topology with the vehicle entry's network (L4-E11's apply_gen_sch_e_entry.py), its OV divider set between CS101's peak at the
    input and the clamp's least breakdown at the cold end, with one CSD19532Q5B (Q12); the clamp D4 becomes the SMCJ30A, the
    least held Littelfuse row that leaves the cut-off's aged band room (its LCSC code is owed: no catalogue reading is filed);
  - for the reversed panel, Q13, a CSD19532Q5B in the panel's return (J_SOLAR.2 becomes PV_RTN), its gate from PV_F through R101
    100k over R102 100k and clamped by D12 BZT52C12-7-F (Diodes DS18004): it blocks a reversal with its 100 V rating and no
    controller, and when on the path is linear;
  - D11 SMCJ40CA (the vehicle entry's D10 part) across the port, the clamp for the port when the cut-off is off, and C131 and
    C132, two 10 uF 100 V X7R 1210 on PV_F, which hold the high side to GND when Q13 is off and take the lead's current when the
    cut-off opens with the source already on (B6 of the consolidation review; THE GUARD ALREADY ON in section 10 of the .out);
  - B6's other changes: C133 and C134, two 10 uF 50 V ceramics on PV_P beside the bulk; U21's CSCP C126 330 pF (1 nF in L4-E11's
    network: the short-circuit trip's filter shorter, CS116's filtered sense still under the trip's least); INP's bottom resistor
    R97 30.0k (39k there: INP under its 20 V for PV_F up to 85 V; INP high from 8.80 V, under the stage's own enable).
What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else: J_SOLAR's pin 2; F2's pin 2 and the new parts after it; PV_P's
declaration (its source is now Q12, switched by U21 through PV_UVLO); the new rails PV_F, PV_SNS and PV_RTN; D4's value and code;
the panel tracker's schematic section.

It is not the whole change: U21's DGX-19 land is L4-E11's (E11-01, owed) and the gate, bootstrap and divider nets are declared as
nodes with the regeneration; the regeneration and its gates; D4's LCSC code. R10 (L4-E5) is not touched.

ORDER: apply it AFTER this record's apply_gen_sch_e_hold.py, apply_gen_sch_e_input_limit.py and apply_gen_sch_e_backstop.py,
L4-E9's apply_gen_sch_e_hotswap.py and L4-E11's apply_gen_sch_e_entry.py (it uses the DGX19 land name L4-E11 adds and the
text the backstop draft leaves): it refuses a generator without them.

Usage:  apply_gen_sch_e_solar_guard.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a draft it follows
is not applied yet, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_solar_guard"
OV_TOP_A, OV_TOP_B, OV_BOT = ("90.9k", "C728600"), ("95.3k", "C861605"), ("7.68k", "C375517")
BLOCK = (
    '# L4-E7, THE SOLAR-FAULT REMEDIES (MESHSAT-1357, v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md, "The solar-fault remedies"): a\n'
    '# stiff 36 V source on the panel port and a reversed panel were open defects (L4-E9\'s D-10 and D-11). D11 SMCJ40CA across the\n'
    '# port and C131, C132 on PV_F; U21, the TPS48110-Q1 over-voltage cut-off in TI\'s own topology with the vehicle entry\'s network\n'
    '# (L4-E11) but its OV divider (R98 + R99 over R100: off above 28.55 to 31.06 V aged, back under 27.07 V at the least, so a\n'
    '# panel inside the window is never locked out), R97 and C126 (B6: the source arriving with the cut-off on, C133 and C134 on\n'
    '# PV_P with it; THE GUARD ALREADY ON in the .out), R87 and Q12 from PV_F to PV_P; Q13 in the return (J_SOLAR.2 is PV_RTN), its\n'
    '# gate from PV_F through R101 over R102, clamped by D12: it blocks a reversed panel with its 100 V rating and no controller.\n'
    'part("D11", "Device", "D_TVS", "SMCJ40CA (bidirectional, Littelfuse SMCJ40 row: 40 V standoff and 44.4 V minimum breakdown each way, clamping 64.5 V at 23.3 A; the panel port\'s clamp, the cut-off\'s input when it is off)", "TVS", {"1": "PV_F", "2": "PV_RTN"}, "C80273")\n'
    'c("C131", "10u 100V X7R 1210 (panel port: holds PV_F to GND while Q13 is off; with C132 takes the lead\'s current when the cut-off opens)", "PV_F", "GND", "C1210")\n'
    'c("C132", "10u 100V X7R 1210 (panel port, with C131)", "PV_F", "GND", "C1210")\n'
    'ic("U21", 20, "TPS48110AQDGXRQ1 high-side driver with protection (panel port cut-off): on by 8.80 V, off above 28.55 to 31.06 V, back under 27.07 V at the least, auto-retry", "DGX19", '
    '{"1": "PV_UVLO", "2": "PV_OVLO", "3": "PV_INP", "4": "NC", "5": "NC", "6": "GND", "7": "GND", "8": "PV_IWRN", "9": "PV_TMR", "10": "GND", "11": "NC", '
    '"12": "PV_BST", "13": "PV_P", "14": "PV_GATE", "15": "PV_PU", "16": "NC", "17": "PV_SNS", "18": "PV_CSP", "19": "PV_ISCP", "20": "PV_VS"}, "C17556513")\n'
    'r("R87", "4.5mOhm 1% 2512 3W 50ppm (panel cut-off sense: its breaker at 6.36 to 7.14 A, over the panel\'s 6.8 A)", "PV_F", "PV_SNS", "RS2512", lcsc="C2985708")\n'
    'nfet("Q12", "CSD19532Q5B 100 V N-FET (4.9 mOhm at VGS 10 V, PowerPAK SO-8 / SON-8 5x6), panel cut-off pass", "PV_GATE", "PV_SNS", "PV_P", lcsc="C473333")\n'
    'r("R88", "100R 0.1% (RSET)", "PV_F", "PV_CSP"); r("R89", "3.01k 1% (RISCP)", "PV_F", "PV_ISCP"); c("C126", "330p C0G 100V (CSCP: the short-circuit filter, 0.93 to 1.05 us; SLUSEE5E 9.5 tunes it in the real system)", "PV_ISCP", "PV_SNS")\n'
    'r("R90", "36.5k 1% (R1: gate slew)", "PV_PU", "PV_GATE"); r("R91", "10R 1% (R2: damping)", "PV_GATE", "PV_SLEW"); c("C127", "10n C0G 5% 100V 1206 (C1: gate slew, 17.3 to 24.7 V/ms)", "PV_SLEW", "GND", "C10u50", lcsc="C184799")\n'
    'c("C128", "1u 25V X7R (CBST)", "PV_BST", "PV_P")\n'
    'c("C129", "22n C0G 5% 50V 1206 (CTMR)", "PV_TMR", "GND", "C10u50", lcsc="C97929"); r("R92", "39.7k 0.1% (RIWRN)", "PV_IWRN", "GND", lcsc="C861872")\n'
    'r("R93", "100R 1% (VS filter, SLUSEE5E 9.5)", "PV_F", "PV_VS"); c("C130", "100n 100V", "PV_VS", "GND", "C0805")\n'
    'r("R94", "59.0k 1%", "PV_F", "PV_UVLO"); r("R95", "10.0k 1% (UVLO: on by 8.44 V, under the stage\'s own enable)", "PV_UVLO", "GND")\n'
    'r("R96", "100k 1%", "PV_F", "PV_INP"); r("R97", "30.0k 1% (INP: high from 8.80 V, under 20 V to 85 V on PV_F)", "PV_INP", "GND")\n'
    + ('r("R98", "%s 0.1%% 25ppm (OV top)", "PV_F", "PV_OVM", "R", "%s"); r("R99", "%s 0.1%% 25ppm (OV top)", "PV_OVM", "PV_OVLO", "R", "%s"); '
       'r("R100", "%s 0.1%% 25ppm (OV bottom: off above 28.55 to 31.06 V, L4-E7)", "PV_OVLO", "GND", "R", "%s")\n'
       % (OV_TOP_A[0], OV_TOP_A[1], OV_TOP_B[0], OV_TOP_B[1], OV_BOT[0], OV_BOT[1])) +
    'nfet("Q13", "CSD19532Q5B 100 V N-FET, panel return switch: on with the panel\'s polarity, blocks a reversed panel", "PV_RG", "PV_RTN", "GND", lcsc="C473333")\n'
    'r("R101", "100k 1%", "PV_F", "PV_RG"); r("R102", "100k 1% (Q13: VGS at least 8.2 V at the hold\'s least)", "PV_RG", "GND")\n'
    'part("D12", "Device", "D_Zener", "BZT52C12-7-F zener, Q13\'s gate clamp (11.4 to 12.7 V, Diodes DS18004)", "SOD123", {"1": "PV_RG", "2": "GND"}, "C124196")\n'
    'c("C133", "10u 50V (PV_P, with C134 beside the bulk: the source arriving with the cut-off on)", "PV_P", "GND", "C10u50"); c("C134", "10u 50V", "PV_P", "GND", "C10u50")\n'
)
EDITS = [
    ('"VH2", {"1": "PV_IN", "2": "GND"}, "C274411")',
     '"VH2", {"1": "PV_IN", "2": "PV_RTN"}, "C274411")   # L4-E7: the return through Q13'),
    ('part("F2", "Device", "Fuse", "10 A mini blade (Keystone 3568 holder): panel input", "FUSE", {"1": "PV_IN", "2": "PV_P"})\n',
     'part("F2", "Device", "Fuse", "10 A mini blade (Keystone 3568 holder): panel input", "FUSE", {"1": "PV_IN", "2": "PV_F"})\n' + BLOCK),
    ('    _intent.rail(_pvn, 17.6, 5.68, 6.25, "J_SOLAR" if _pvn == "PV_IN" else "F2",',
     '    _intent.rail(_pvn, 17.6, 5.68, 6.25, "J_SOLAR" if _pvn == "PV_IN" else "Q12",'),
    ('                                    {"always_on": True,\n'
     '                                     "always_on_why": "a photovoltaic panel produces whenever there is light "\n'
     '                                     "on it and nothing on this board is between the connector and the fuse, "\n'
     '                                     "so there is no part whose enable pin could switch this rail. The "\n'
     '                                     "tracker downstream decides how much of it is drawn, not whether it is "\n'
     '                                     "present"}),\n',
     '                                    # L4-E7 (the solar-fault remedies): U21 switches PV_P through Q12, its enable the\n'
     '                                    # UVLO divider on PV_F; it is off below its UVLO and above the over-voltage cut-off\n'
     '                                    {"switch": "U21", "enable_net": "PV_UVLO"}),\n'),
    ('             "U5\'s VIN and CSNIN, and M1\'s drain; the input-current limit holds its average (L4-E7)")\n',
     '             "U5\'s VIN and CSNIN, and M1\'s drain; the input-current limit holds its average (L4-E7)")\n'
     '# L4-E7 (the solar-fault remedies): PV_F and PV_SNS, from F2 through R87 to Q12, are series segments of PV_P; PV_RTN, the\n'
     '# panel\'s return from J_SOLAR.2 through Q13 to GND, returns PV_P. v_max is D11\'s clamp at its rated current.\n'
     '_intent.rail("PV_F", _intent.rail_volts("PV_P"), 5.68, 6.25, "F2", loads={"R87": 5.68}, v_work=25.0, v_max=64.5, converted=False,\n'
     '             series_of="PV_P", note="the panel port behind F2: D11, C131, C132 and U21\'s supply and dividers on it (L4-E7)")\n'
     '_intent.rail("PV_SNS", _intent.rail_volts("PV_P"), 5.68, 6.25, "R87", loads={"Q12": 5.68}, v_work=25.0, v_max=64.5, converted=False,\n'
     '             series_of="PV_P", note="the cut-off\'s sense node between R87 and Q12 (L4-E7)")\n'
     '_intent.rail("PV_RTN", 0.1, 5.68, 6.25, "J_SOLAR", loads={"Q13": 5.68}, returns="PV_P", converted=False, v_max=64.5,\n'
     '             note="the panel\'s return from J_SOLAR.2 through Q13 to GND, about 0.07 V at the panel\'s short circuit; a reversed "\n'
     '                  "panel holds up to 25 V on it with Q13 off, D11\'s clamp on a ring (L4-E7)")\n'),
    ('part("D4", "Device", "D_Zener", "SMCJ28A (panel surge: 28 V standoff, clamping at up to 45.4 V at its rated 10/1000 us pulse, under the 50 V bulk; unidirectional, cathode on TRK_VS)", "TVS", {"1": "TRK_VS", "2": "GND"}, "C224047")',
     'part("D4", "Device", "D_Zener", "SMCJ30A (panel surge: 30 V standoff, over CS101\'s 27.82 V and the cut-off\'s band; clamping at up to 48.4 V at its rated 10/1000 us pulse, under the 50 V bulk; unidirectional, cathode on TRK_VS; LCSC code owed, L4-E7)", "TVS", {"1": "TRK_VS", "2": "GND"}, "")'),
    ('["J_SOLAR", "F2", "D4", ',
     '["J_SOLAR", "F2", "D11", "C131", "U21", "R87", "Q12", "R88", "R89", "C126", "R90", "R91", "C127", "C128", "C129", "R92", "R93", "C130", '
     '"R94", "R95", "R96", "R97", "R98", "R99", "R100", "Q13", "R101", "R102", "D12", "C132", "C133", "C134", "D4", '),
]
NEEDS = ('"DGX19": "meshsat:TI_DGX0019A_VSSOP-19_3x5.1mm_P0.5mm"', 'part("C69", ', '"36": "TRK_SWEN"')


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    for need_ in NEEDS:
        if need_ not in text:
            refuse("a draft this one follows is not applied (no %s)" % need_.split(":")[0])
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


# NOT RELEASED: task L4-E7 drafts these values for board E's generator owner and never applies them. Writing the repository's own
# gen_sch_e.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of L4-E7 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
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
