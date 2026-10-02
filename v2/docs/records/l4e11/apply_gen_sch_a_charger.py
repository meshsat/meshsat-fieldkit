#!/usr/bin/env python3
"""apply_gen_sch_a_charger.py: DRAFT for board A's generator owner (task L4-E11, MESHSAT-1357, the U-04 question for the
consolidation of 2 October 2026 and its fix round for the consolidation review cx36). NOT APPLIED to the tree by L4-E11; its
author ran it only on scratch copies (the tests write scratch copies).

Why (L4E11-SOURCE-ONLY-AND-ENTRY.md sections 12 to 15, l4e11_power.out sections 12 to 15): the drawn BQ25731 has no battery FET,
so VSYS with no battery current (D1) and with the charge inhibited (D3) rest on statements TI does not print. TI's BQ25730
(SLUSE65A, February 2021, revised January 2024) is the same 32-pin land with pin 21 as BATDRV, the gate drive of a P-channel
battery FET between VSYS and the charge sense resistor; its table prints VSYS_MIN's regulation and the system voltage with the
charge disabled, and every row the settings of L4-E4 to L4-E8 rest on is the BQ25731's row. The fix round re-selects the battery
FET at BATDRV's least drive (8.5 V): two Nexperia BUK6Y10-30P in parallel (section 15c), sized to an RDS(on) allowance no printed
maximum covers (section 16a, E11-36), and moves
board E's auxiliary domain to VSYS over the dock's pin 1 (section 15a; board E's half is apply_gen_sch_e_aux.py).

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else:
  U3      BQ25731RSNR (C2871872) becomes BQ25730RSNR (C5219071); pin 21 goes from NC to CH_BATDRV; its section comment.
  Q39,Q40 added: Nexperia BUK6Y10-30PX (C3278350), 30 V P-channel, LFPAK56, in parallel: sources on VBAT (VSYS), drains on
          CH_BATQ, gates on CH_BATDRV (pads 1 to 3 source, 4 gate, 5 the mounting base, drain), with the land key LFPAK56 (KiCad's
          Package_TO_SOT_SMD:LFPAK56); the pad map read against Nexperia's SOT669 drawing is the parts stream's.
  R17     the 5 mOhm RSR moves from VBAT to CH_BATQ (to CELL_FUSED), and R149 (SRP's 10 Ohm) from VBAT to CH_BATQ, as TI's
          Figure 9-1 draws the battery FET between VSYS and RSR.
  C236    added: Panasonic EEHZK1V181P (C242139) on VBAT, VSYS's effective capacitance by design (SLUSE65A 9.1: 50 uF), with its
          land key CPOL8 (KiCad's CP_Elec_8x10).
  J_DOCK  pin 1 from GND to VSYS_DOCK: board E's auxiliary domain (U12, both mixer fans) fed from VSYS (board E's VSYS_E)
          through U42's eFuse (the review of the provisional fixes, L4-F03; section 16e).
  U42     added: TI TPS16630PWPR eFuse (SLVSET9G, held back), IN, P_IN and UVLO on VBAT, OUT on VSYS_DOCK, OVP and MODE to GND
          (OVP off; auto-retry), R228 11.0k 0.1 % on ILIM (I(OL) = 18 / R(ILIM): 1.47 to 1.80 A, a steady setting), C237 22 nF on
          dVdT, C238 1 uF at IN, C239 0.1 uF at OUT, D23 B540C-13-F (C72264) from GND to OUT, the land key SMC; SHDN, IMON,
          FLT and PGOOD open as TI allows; the land key HTSSOP20 (KiCad's HTSSOP-20-1EP, checked against TI's PWP0020 drawing
          by the parts stream); VBAT's declared loads gain U42's 1.0 A; VSYS_DOCK declared (source U42, J_DOCK's 1.0 A).
  intent  CH_BATQ declared a segment of the pack path (source R17, loads Q39 and Q40, 10 A typical, 18 A peak); VBAT's source
          becomes Q39 (the pair), fed from CH_BATQ; the charger's sheet group names Q39, Q40 and C236.
The designators Q39, Q40, C236 to C239, R228, D23 and U42 are free in gen_sch_a.py as pinned by l4e11_power.py; if another draft takes them first, renumber.

ORDER: independent of apply_gen_sch_a_guard.py (either order); apply with apply_gen_sch_e_aux.py (the dock's pin 1 on both
boards at once) and apply_pcb_interfaces_dock.py. It withdraws E11-24's register row (the bank is not drawn). Firmware rules come
with it (E11-28): EN_OOA 0 at boot, ChargeCurrent written for any charge, the watchdog serviced, the battery FET's registers
left at their power-on values.

Usage:  apply_gen_sch_a_charger.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_a_charger"
_PAIR = ("# L4-E11 (MESHSAT-1357, the U-04 question for the consolidation and its fix round, 2 October 2026): THE BQ25730's BATTERY\n"
         "# FETS. BATDRV (pin 21) pulls the gates 10 V below VSYS (8.5 V at least, SLUSE65A p.17) to turn them fully on and shorts\n"
         "# them to VSYS to turn them off (pin table p.5); they run in linear mode to hold VSYS at VSYS_MIN under a depleted or absent\n"
         "# pack and as an ideal diode in supplement mode (8.4.1.1, p.38). TI asks a P-channel part of 20 V or more for 1 to 4 cells\n"
         "# with Ciss under 5 nF (9.2.2, p.92). Two Nexperia BUK6Y10-30P (17 April 2020): 30 V, VGS +-20 V, 175 C, RDSon at most 10\n"
         "# mOhm at -10 V and 25 C, 16 at 175 C, 25 at -4.5 V; Ciss 2.36 nF typical each (4.72 for the two; near 0 V more, E11-37);\n"
         "# ISM 320 A each for 10 us at Tmb 25 C. No printed maximum covers BATDRV's 8.5 V hot: each is SIZED to an RDS(on) allowance of\n"
         "# 21.1 mOhm at 8.5 V and 150 C, which E11-36 confirms or reverses; the pair's installed self plus mutual junction-to-air\n"
         "# impedance is E11-29's target (33.12 K/W steady at +70 C air, with its 1 s, 20 ms and 244 us limits); the docking pulse is\n"
         "# taken whole in ONE body diode, no sharing credited, and its whole hot waveform is E11-30's (L4-E11 sections 16 and 17).\n"
         "# L4-E11 (the review of the provisional fixes, L4-F03, 2 October 2026): THE DOCK'S VSYS BRANCH. J_DOCK pin 1 carries VSYS to\n"
         "# board E's auxiliary domain over one Preci-Dip 813 (3.5 A operating maximum). U42 regulates a sustained overload to 1.47 to\n"
         "# 1.80 A (SLVSET9G p.8 rows over TJ -40 to 125 C at VIN - VOUT 1 V, inferred at R228 11.0k by Equation 6), a steady setting and\n"
         "# not an instantaneous ceiling; limits for at most 202 ms and retries after 500 to 800 ms (Table 8-1, MODE to GND); a start into\n"
         "# a short regulates its junction for up to 1.5 s; a short's first microseconds, the pins' spikes and the contact's pulse are\n"
         "# E11-38's (L4-E11 section 17a). C238 at IN and C239 at OUT are TI's 0.1 uF minimum (6.3); D23 is TI's Schottky at OUT for the\n"
         "# output loop's negative spike (9.4.1, 9.5.1); U42's IN sits within 20 nH of C236 and C23 to C25 (a layout requirement).\n"
         "ic(\"U42\", 21, \"TPS16630PWPR 60 V 6 A eFuse: the dock's VSYS branch to board E (I(OL) 18 / 11.0k)\", \"HTSSOP20\", {\"1\": \"VBAT\", \"2\": \"VBAT\", \"3\": \"VBAT\", \"4\": \"NC\", \"5\": \"NC\", \"6\": \"VBAT\", \"7\": \"VBAT\", \"8\": \"GND\", \"9\": \"GND\", \"10\": \"EF_DVDT\", \"11\": \"EF_ILIM\", \"12\": \"GND\", \"13\": \"NC\", \"14\": \"NC\", \"15\": \"NC\", \"16\": \"NC\", \"17\": \"NC\", \"18\": \"VSYS_DOCK\", \"19\": \"VSYS_DOCK\", \"20\": \"VSYS_DOCK\", \"21\": \"GND\"})\n"
         "r(\"R228\", \"11k 0.1%\", \"EF_ILIM\", \"GND\")    # U42's overload limit, 18 / 11.0 = 1.64 A typical\n"
         "c(\"C237\", \"22n 50V C0G\", \"EF_DVDT\", \"GND\")   # U42's output slew, TI's characterised 22 nF\n"
         "c(\"C238\", \"1u 50V X7R\", \"VBAT\", \"GND\")      # at U42's IN (TI 9.4.1: at least 1 uF where surges reach the input)\n"
         "c(\"C239\", \"100n 50V X7R\", \"VSYS_DOCK\", \"GND\")   # at U42's OUT (TI 6.3: 0.1 uF minimum at OUT)\n"
         "part(\"D23\", \"Device\", \"D_Schottky\", \"B540C-13-F 40 V 5 A Schottky, U42's output clamp (cathode on OUT)\", \"SMC\", {\"1\": \"VSYS_DOCK\", \"2\": \"GND\"}, \"C72264\")\n"
         "for _qb in (\"Q39\", \"Q40\"): nfet(_qb, \"BUK6Y10-30PX 30 V P-FET (the BQ25730's battery FET, one of two in parallel: S on VSYS, D toward RSR)\", \"CH_BATDRV\", \"CH_BATQ\", \"VBAT\", fp=\"LFPAK56\", lcsc=\"C3278350\")")
_BATQ = ('\n# L4-E11 (the U-04 question for the consolidation): CH_BATQ, the copper between the BQ25730\'s battery FETs Q39 and Q40 and the\n'
         '# RSR shunt R17. The pack current crosses it in both directions, charge and discharge, so it is declared a segment of the pack\n'
         '# path as CELL_FUSED is, with the same 10 A typical and 18 A peak.\n'
         '_intent.rail("CH_BATQ", 14.4, 10.0, 18.0, "R17", v_work=16.8, converted=False, series_of="CELL+", loads={"Q39": 5.0, "Q40": 5.0},\n'
         '             note="L4-E11: the node between the battery FETs Q39 and Q40 (drains) and the RSR shunt R17, SRP through R149; the "\n'
         '                  "pack\'s charge and discharge current, 10.0 A typical and 18.0 A peak, counted once as a segment of CELL+")\n'
         '_intent.rail("VSYS_DOCK", 14.4, 1.0, 1.0, "U42", always_on=True, v_work=17.4, converted=False, fed_from="VBAT",\n'
         '             always_on_why="VSYS through the eFuse U42, which opens only on its own overload, short or thermal fault and retries; nothing switches it",\n'
         '             loads={"J_DOCK": 1.0},\n'
         '             note="L4-E11 (L4-F03): U42\'s output to J_DOCK pin 1, board E\'s VSYS_E; limited to 1.47 to 1.80 A")')
EDITS = [
    ("# --- charger BQ25731 (bq25731-datasheet.pdf, QFN-32 RSN; no BATFET, so the system sits on VSYS and the pack on the far side of RSR, SLUSE66A Figure 10-1): 4S from VBUS20 at up to 8 A, I2C 0x6B on the kit bus,",
     "# --- charger BQ25730 (SLUSE65A, held back; QFN-32 RSN; an NVDC charger: the system on VSYS, the battery FETs Q39 and Q40 and RSR between it and the pack, SLUSE65A Figure 9-1; L4-E11): 4S from VBUS20 at up to 8 A, I2C 0x6B on the kit bus,"),
    ('ic("U3", 33, "BQ25731RSNR 1 to 5 cell buck-boost charger, 4S from the 20 V bus, I2C 0x6B", "QFN32_04", {',
     'ic("U3", 33, "BQ25730RSNR 1 to 5 cell NVDC buck-boost charger (battery FETs Q39 and Q40), 4S from the 20 V bus, I2C 0x6B", "QFN32_04", {'),
    ('"21": "NC", "22": "VBAT"', '"21": "CH_BATDRV", "22": "VBAT"'),
    ('"33": "GND"}, "C2871872")', '"33": "GND"}, "C5219071")'),
    ('("Q10", "CH_HIDRV2", "VBAT", "CH_SW2", "CSD17577Q5A 30 V N-FET")): nfet(_qr, _v, _g, _d, _s)',
     '("Q10", "CH_HIDRV2", "VBAT", "CH_SW2", "CSD17577Q5A 30 V N-FET")): nfet(_qr, _v, _g, _d, _s)\n' + _PAIR),
    ('r("R17", "5mOhm 1% 2512 (RSR, charge current sense)", "VBAT", "CELL_FUSED", "RS2512")',
     'r("R17", "5mOhm 1% 2512 (RSR, charge current sense)", "CH_BATQ", "CELL_FUSED", "RS2512")'),
    ('r("R149", "10R", "VBAT", "CH_SRP_F")            # the same on SRP, so the pair sees one filter and not a half; SRP is the system side, VSYS (S-04, 26 Sep 2026)',
     'r("R149", "10R", "CH_BATQ", "CH_SRP_F")         # the same on SRP, so the pair sees one filter and not a half; SRP is the battery FETs\' side of RSR (L4-E11, SLUSE65A Figure 9-1)'),
    ('for k in range(3): c("C%d" % (23 + k), "22u 25V 1210", "VBAT", "GND", "C1210")   # the charger\'s VSYS capacitors, at Q10\'s drain (S-04, 26 Sep 2026)',
     'for k in range(3): c("C%d" % (23 + k), "22u 25V 1210", "VBAT", "GND", "C1210")   # the charger\'s VSYS capacitors, at Q10\'s drain (S-04, 26 Sep 2026)\n'
     'c("C236", "180u 35V Panasonic EEHZK1V181P hybrid polymer (10.2 mm)", "VBAT", "GND", "CPOL8", lcsc="C242139")   # VSYS\'s 50 uF effective by design (SLUSE65A 9.1; L4-E11 D5)'),
    ('"CPOL63": "Capacitor_SMD:CP_Elec_6.3x7.7", "CPOL10": "Capacitor_SMD:CP_Elec_10x10",',
     '"CPOL63": "Capacitor_SMD:CP_Elec_6.3x7.7", "CPOL10": "Capacitor_SMD:CP_Elec_10x10", "CPOL8": "Capacitor_SMD:CP_Elec_8x10", "LFPAK56": "Package_TO_SOT_SMD:LFPAK56", "HTSSOP20": "Package_SO:HTSSOP-20-1EP_4.4x6.5mm_P0.65mm_EP3.4x6.5mm", "SMC": "Diode_SMD:D_SMC",'),
    ('("CHARGER BQ25731: 4S FROM THE 20 V BUS, SYSTEM ON VSYS (VBAT), PACK BEYOND RSR, I2C 0x6B", ["U3", "Q7", "Q8", "Q9", "Q10", "L2", "R16", "R17", "C16",',
     '("CHARGER BQ25730: 4S FROM THE 20 V BUS, SYSTEM ON VSYS (VBAT), BATTERY FETS Q39 AND Q40 AND RSR TO THE PACK, THE DOCK VSYS EFUSE U42, I2C 0x6B", ["U3", "Q7", "Q8", "Q9", "Q10", "L2", "R16", "R17", "Q39", "Q40", "C236", "U42", "R228", "C237", "C238", "C239", "D23", "C16",'),
    ('_intent.rail("VBAT", 14.4, 10.0, 18.0, "R17", always_on=True, v_work=16.8, converted=False, fed_from="CELL_FUSED",',
     '_intent.rail("VBAT", 14.4, 10.0, 18.0, "Q39", always_on=True, v_work=16.8, converted=False, fed_from="CH_BATQ",'),
    ('loads={"U4": 2.0, "Q28": 2.22,', 'loads={"U42": 1.0, "U4": 2.0, "Q28": 2.22,'),
    ('"10.0 A typical and 18.0 A peak, and is counted once as a segment of CELL+")',
     '"10.0 A typical and 18.0 A peak, and is counted once as a segment of CELL+")' + _BATQ),
    ('spring pins to the dock block (2x6, Preci-Dip 813-S1-012-10-016101, underside): 1-7 GND, 8 SHORE_INHIBIT,',
     'spring pins to the dock block (2x6, Preci-Dip 813-S1-012-10-016101, underside): 1 VSYS_DOCK (VBAT through the eFuse U42) to board E\'s VSYS_E, the auxiliary domain\'s feed (L4-E11), 2-7 GND, 8 SHORE_INHIBIT,'),
    ('The pack reaches it through the 25 A blade F1 and the RSR shunt R17, opened only by the pack\'s own BQ4050 FETs and the blade;',
     'The pack reaches it through the 25 A blade F1, the RSR shunt R17 and the battery FETs Q39 and Q40 (on with the battery alone, SLUSE65A p.27; their body diodes otherwise; L4-E11), opened only by the pack\'s own BQ4050 FETs and the blade;'),
    ('{"1": "GND", "2": "GND", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT", "9": "USB_E6_P", "10": "USB_E6_N", "11": "GND", "12": "DOCK_SPARE"})',
     '{"1": "VSYS_DOCK", "2": "GND", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT", "9": "USB_E6_P", "10": "USB_E6_N", "11": "GND", "12": "DOCK_SPARE"})'),
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


# NOT RELEASED: task L4-E11 drafts this change for board A's generator owner and never applies it. Writing the repository's
# own gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an
# accepted check of L4-E11 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written
# (the tests do, on scratch copies).
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
