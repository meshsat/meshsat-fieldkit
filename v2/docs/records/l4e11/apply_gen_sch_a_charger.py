#!/usr/bin/env python3
"""apply_gen_sch_a_charger.py: DRAFT for board A's generator owner (task L4-E11, MESHSAT-1357, the U-04 question for the
consolidation of 2 October 2026). NOT APPLIED to the tree by L4-E11; its author ran it only on scratch copies (the tests write
scratch copies).

Why (L4E11-SOURCE-ONLY-AND-ENTRY.md section 12, l4e11_power.out sections 12 to 14): the drawn BQ25731 has no battery FET, so
VSYS with no battery current (D1) and with the charge inhibited (D3) rest on statements TI does not print. TI's BQ25730
(SLUSE65A, February 2021, revised January 2024) is the same 32-pin land with pin 21 as BATDRV, the gate drive of a P-channel
battery FET between VSYS and the charge sense resistor; its table prints VSYS_MIN's regulation (12.3 V, at least 12.054 V, TJ
-40 to 125 C) and the system voltage with the charge disabled (VSRN + 150 mV within 2 %), and every row the settings of L4-E4
to L4-E8 rest on is the BQ25731's row. The session selected it (SESSION, section 14).

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else:
  U3      BQ25731RSNR (C2871872) becomes BQ25730RSNR (C5219071); pin 21 goes from NC to CH_BATDRV; its section comment.
  Q39     added: AOS AONS21357 (C404364), 30 V P-channel, source on VBAT (VSYS), drain on CH_BATQ, gate on CH_BATDRV, on the
          five-pad land the charger's FETs use (pads 1 to 3 source, 4 gate, 5 drain); the land's fit to AOS's DFN 5x6 drawing is
          the parts stream's to confirm.
  R17     the 5 mOhm RSR moves from VBAT to CH_BATQ (to CELL_FUSED), and R149 (SRP's 10 Ohm) from VBAT to CH_BATQ, as TI's
          Figure 9-1 draws the battery FET between VSYS and RSR.
  C236    added: Panasonic EEHZK1V181P (C242139) on VBAT, VSYS's effective capacitance by design (SLUSE65A 9.1: 50 uF), with its
          land key CPOL8 (KiCad's CP_Elec_8x10).
  intent  CH_BATQ declared a segment of the pack path (source R17, load Q39, 10 A typical, 18 A peak); VBAT's source becomes Q39,
          fed from CH_BATQ; the charger's sheet group names Q39 and C236.
The designators Q39 and C236 are free in gen_sch_a.py as pinned by l4e11_power.py; if another draft takes them first, renumber.

ORDER: independent of apply_gen_sch_a_guard.py (either order). It withdraws E11-24's register row (the bank is not drawn).
Firmware rules come with it (E11-28): EN_OOA 0 at boot, ChargeCurrent written for any charge, the watchdog serviced, the
battery FET's registers left at their power-on values.

Usage:  apply_gen_sch_a_charger.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_a_charger"
_Q39 = ("# L4-E11 (MESHSAT-1357, the U-04 question for the consolidation, 2 October 2026): THE BQ25730's BATTERY FET. BATDRV (pin 21)\n"
        "# pulls the gate 10 V below VSYS to turn it fully on and shorts it to VSYS to turn it off (SLUSE65A pin table p.5); it runs\n"
        "# in linear mode to hold VSYS at VSYS_MIN under a depleted or absent pack and as an ideal diode in supplement mode (8.4.1.1,\n"
        "# p.38). TI asks a P-channel part of 20 V or more for 1 to 4 cells with Ciss under 5 nF (9.2.2, p.92): AONS21357, 30 V,\n"
        "# VGS +-25 V, 7.8 mOhm at most at -10 V (10.7 at 125 C), Ciss 2.83 nF typical (AOS Rev 2.1). Its installed thermal path is\n"
        "# E11-29's bar; the docking inrush through its body diode is E11-30.\n"
        "nfet(\"Q39\", \"AONS21357 30 V P-FET (the BQ25730's battery FET: S on VSYS, D toward RSR)\", \"CH_BATDRV\", \"CH_BATQ\", \"VBAT\", lcsc=\"C404364\")")
_BATQ = ('\n# L4-E11 (the U-04 question for the consolidation): CH_BATQ, the copper between the BQ25730\'s battery FET Q39 and the RSR\n'
         '# shunt R17. The pack current crosses it in both directions, charge and discharge, so it is declared a segment of the pack\n'
         '# path as CELL_FUSED is, with the same 10 A typical and 18 A peak.\n'
         '_intent.rail("CH_BATQ", 14.4, 10.0, 18.0, "R17", v_work=16.8, converted=False, series_of="CELL+", loads={"Q39": 10.0},\n'
         '             note="L4-E11: the node between the battery FET Q39 (drain) and the RSR shunt R17, SRP through R149; the pack\'s charge "\n'
         '                  "and discharge current, 10.0 A typical and 18.0 A peak, counted once as a segment of CELL+")')
EDITS = [
    ("# --- charger BQ25731 (bq25731-datasheet.pdf, QFN-32 RSN; no BATFET, so the system sits on VSYS and the pack on the far side of RSR, SLUSE66A Figure 10-1): 4S from VBUS20 at up to 8 A, I2C 0x6B on the kit bus,",
     "# --- charger BQ25730 (SLUSE65A, held back; QFN-32 RSN; an NVDC charger: the system on VSYS, the battery FET Q39 and RSR between it and the pack, SLUSE65A Figure 9-1; L4-E11): 4S from VBUS20 at up to 8 A, I2C 0x6B on the kit bus,"),
    ('ic("U3", 33, "BQ25731RSNR 1 to 5 cell buck-boost charger, 4S from the 20 V bus, I2C 0x6B", "QFN32_04", {',
     'ic("U3", 33, "BQ25730RSNR 1 to 5 cell NVDC buck-boost charger (battery FET Q39), 4S from the 20 V bus, I2C 0x6B", "QFN32_04", {'),
    ('"21": "NC", "22": "VBAT"', '"21": "CH_BATDRV", "22": "VBAT"'),
    ('"33": "GND"}, "C2871872")', '"33": "GND"}, "C5219071")'),
    ('("Q10", "CH_HIDRV2", "VBAT", "CH_SW2", "CSD17577Q5A 30 V N-FET")): nfet(_qr, _v, _g, _d, _s)',
     '("Q10", "CH_HIDRV2", "VBAT", "CH_SW2", "CSD17577Q5A 30 V N-FET")): nfet(_qr, _v, _g, _d, _s)\n' + _Q39),
    ('r("R17", "5mOhm 1% 2512 (RSR, charge current sense)", "VBAT", "CELL_FUSED", "RS2512")',
     'r("R17", "5mOhm 1% 2512 (RSR, charge current sense)", "CH_BATQ", "CELL_FUSED", "RS2512")'),
    ('r("R149", "10R", "VBAT", "CH_SRP_F")            # the same on SRP, so the pair sees one filter and not a half; SRP is the system side, VSYS (S-04, 26 Sep 2026)',
     'r("R149", "10R", "CH_BATQ", "CH_SRP_F")         # the same on SRP, so the pair sees one filter and not a half; SRP is the battery FET\'s side of RSR (L4-E11, SLUSE65A Figure 9-1)'),
    ('for k in range(3): c("C%d" % (23 + k), "22u 25V 1210", "VBAT", "GND", "C1210")   # the charger\'s VSYS capacitors, at Q10\'s drain (S-04, 26 Sep 2026)',
     'for k in range(3): c("C%d" % (23 + k), "22u 25V 1210", "VBAT", "GND", "C1210")   # the charger\'s VSYS capacitors, at Q10\'s drain (S-04, 26 Sep 2026)\n'
     'c("C236", "180u 35V Panasonic EEHZK1V181P hybrid polymer (10.2 mm)", "VBAT", "GND", "CPOL8", lcsc="C242139")   # VSYS\'s 50 uF effective by design (SLUSE65A 9.1; L4-E11 D5)'),
    ('"CPOL63": "Capacitor_SMD:CP_Elec_6.3x7.7", "CPOL10": "Capacitor_SMD:CP_Elec_10x10",',
     '"CPOL63": "Capacitor_SMD:CP_Elec_6.3x7.7", "CPOL10": "Capacitor_SMD:CP_Elec_10x10", "CPOL8": "Capacitor_SMD:CP_Elec_8x10",'),
    ('("CHARGER BQ25731: 4S FROM THE 20 V BUS, SYSTEM ON VSYS (VBAT), PACK BEYOND RSR, I2C 0x6B", ["U3", "Q7", "Q8", "Q9", "Q10", "L2", "R16", "R17", "C16",',
     '("CHARGER BQ25730: 4S FROM THE 20 V BUS, SYSTEM ON VSYS (VBAT), BATTERY FET Q39 AND RSR TO THE PACK, I2C 0x6B", ["U3", "Q7", "Q8", "Q9", "Q10", "L2", "R16", "R17", "Q39", "C236", "C16",'),
    ('_intent.rail("VBAT", 14.4, 10.0, 18.0, "R17", always_on=True, v_work=16.8, converted=False, fed_from="CELL_FUSED",',
     '_intent.rail("VBAT", 14.4, 10.0, 18.0, "Q39", always_on=True, v_work=16.8, converted=False, fed_from="CH_BATQ",'),
    ('"10.0 A typical and 18.0 A peak, and is counted once as a segment of CELL+")',
     '"10.0 A typical and 18.0 A peak, and is counted once as a segment of CELL+")' + _BATQ),
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
