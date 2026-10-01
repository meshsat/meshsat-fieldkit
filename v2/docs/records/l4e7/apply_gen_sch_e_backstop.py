#!/usr/bin/env python3
"""apply_gen_sch_e_backstop.py: DRAFT for board E's generator owner (task L4-E7R, MESHSAT-1357, 1 October 2026; third round
of 2 October 2026 after checks/astra-check-l4e7r-2.md). NOT APPLIED to the tree by L4-E7; its author ran it only on scratch
copies (the tests also write scratch copies).

The control decision of L4E7-CONTROL-DECISION.md, approach C: a hardware 100 W backstop under the LT8705A's input-current
limit, its bound on printed limits and two named assumptions with their break-evens, SWEN off by default, and the solar
entry's protection against the disturbances derived from the approved test plan. It edits the
text apply_gen_sch_e_hold.py and apply_gen_sch_e_input_limit.py leave, so it applies AFTER both and refuses a generator that
does not carry them. What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else:
  - R60 to R64 (new): five Vishay Dale WSL2512R0700FEA (70 mOhm, 1 %, 75 ppm/K from -55 to +155 C; LCSC C2076144) in parallel,
    14 mOhm, from PV_P to the new net TRK_VS: the sense bank, ahead of everything on the entry but F2, R8, TP5 and U18's VIN+;
  - U18 (new): TI INA169NA/3K (LCSC C44322), VIN+ on PV_P, VIN- and V+ on TRK_VS with C66, its output current into R65 16.9k
    and R66 8.25k (LCSC C705798; 25.15k together, against the 25 kOhm of its gain row, SBOS181F p.6; the trip's highest sense
    voltage at the 50 mV the rejection rows are printed at), C70 1 nF across R66 (LCSC C1588: a
    discharge's charge cannot lift INB past its 7 V rating);
  - U19 (new): TI TPS3701DDCR (LCSC C132788): INB on R66 (the trip), INA on R67 110k over R68 9.53k from TRK_VS (the monitor of
    U18's supply), OUTA and OUTB together on TRK_MR, VDD from TRK_LDO33 with C67;
  - U20 (new): TI TPS3808G33DBVR (LCSC C43698): VDD and SENSE on TRK_LDO33 with C68, MR on TRK_MR, CT to VDD through R69 100k
    (the fixed reset delay, 180 ms at least, SBVS050N p.7), RESET on the new net TRK_SWEN;
  - U5's SWEN (pin 36) from TRK_INTVCC to TRK_SWEN, with R70 8.06k from TRK_LDO33 and R71 6.04k to GND (LCSC C728595): off
    by default, SWEN cannot reach its threshold below about 2.66 V on TRK_LDO33, above every sensing part's least supply;
  - R59 (RSENSE1) and U5's CSPIN (pin 33) move from PV_P to TRK_VS; CSNIN (pin 32) and VIN (pin 34) stay on TRK_VIN; nothing in
    series with either pin (8705af p.30); C71 to C74 (new), four 10 uF 50 V ceramics (the value text and land of C13 and C14) on
    TRK_VS at R59's pad, so a fast edge reaches R59 only through C13 to C15's share (U5's 0.3 V sense rating, 8705af p.2);
  - the surge correction: C11 and C12 become Panasonic EEHZA1H330XP (33 uF 50 V, the same 6.3 x 7.7 mm land; LCSC C178637), C69
    a third, all on TRK_VS with D4 (moved from PV_P), so D4 clamps at up to 45.4 V under 50 V parts and the pulse reaches R59
    only through the ceramics' share; R14 (SHDN's divider top) moves to TRK_VS;
  - R16, RIMON_IN: 23.2k to 30k 0.1 % 25 ppm/K (RT0603BRD0730KL, LCSC C723585), the regulation coordinated under the trip;
  - the declarations: PV_P's loads are the bank; TRK_VS a series segment of PV_P from the bank to R59; the tracker section's list.

It is not the whole change: the layout owes the bank's Kelvin taps to U18 and R59's to U5 (board E's layout constraints), the
regeneration and its gates, and the input capacitance's ripple and damping check with the new bulk (99 uF in place of 200 uF);
the requirement records that name "the 35 V bulk capacitors" and "the 225 uF on PV_P" see the new values (their owners restate
them). After any application the record's and l4e5's pins of the netlist refuse by design. R10 (L4-E5) is not touched.

Usage:  apply_gen_sch_e_backstop.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, the hold or input
limit draft is not applied yet, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_backstop"
BULK = '"33u 50V Panasonic EEHZA1H330XP hybrid polymer (7.7 mm)", "CPOL63", {"1": "TRK_VS", "2": "GND"}, "C178637")'
BLOCK = (
    '# L4-E7R (MESHSAT-1357, v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md): THE 100 W BACKSTOP. R60 to R64 (five WSL2512 70 mOhm\n'
    '# in parallel, 14 mOhm) carry the stage\'s input from PV_P to TRK_VS ahead of RSENSE1; U18 (INA169, SBOS181F) reads them, its\n'
    '# output current into R65 + R66 (25.15k, beside the 25 kOhm of its gain row); U19 (TPS3701, SBVS240C) trips on R66 at INB\n'
    '# and watches TRK_VS at INA\n'
    '# (R67, R68); its outputs drive U20\'s MR (TPS3808G33, SBVS050N), which holds RESET low at least 180 ms after any trip (CT to\n'
    '# VDD through R69) and whenever TRK_LDO33 is under its threshold; RESET holds U5\'s SWEN (pin 36) low, R70 over R71 set it\n'
    '# when released, and R71 holds it low with no supply (SWEN under its threshold below 2.66 V on TRK_LDO33). C71 to C74 on\n'
    '# TRK_VS at R59\'s pad take a fast edge ahead of RSENSE1; nothing is in series with CSPIN or CSNIN (8705af p.30).\n'
    'for _bk in range(5): r("R6%d" % _bk, "70mOhm 1% 2512 (backstop sense bank, WSL2512R0700FEA)", "PV_P", "TRK_VS", "RS2512", "C2076144")\n'
    'ic("U18", 5, "INA169NA/3K high-side current-shunt monitor, current output (SOT-23-5: 1 OUT, 2 GND, 3 VIN+, 4 VIN-, 5 V+)", "SOT235", '
    '{"1": "TRK_ISO", "2": "GND", "3": "PV_P", "4": "TRK_VS", "5": "TRK_VS"}, "C44322")\n'
    'c("C66", "100n", "TRK_VS", "GND", "C", "C14663", bypass=("U18", "5"))\n'
    'r("R65", "16.9k 0.1% 25ppm (U18 load, 25.15k with R66)", "TRK_ISO", "TRK_BKS", "R", "C861156"); '
    'r("R66", "8.25k 0.1% 25ppm (the trip: 400 mV at 48.5 mV sense)", "TRK_BKS", "GND", "R", "C705798"); '
    'c("C70", "1n", "TRK_BKS", "GND", "C", "C1588")\n'
    'r("R67", "110k 0.1% 25ppm (TRK_VS monitor top)", "TRK_VS", "TRK_UVS", "R", "C326736"); '
    'r("R68", "9.53k 0.1% 25ppm (TRK_VS monitor bottom)", "TRK_UVS", "GND", "R", "C705800")\n'
    'ic("U19", 6, "TPS3701DDCR window comparator: INB the 100 W trip, INA the TRK_VS monitor (SOT-23-6: 1 OUTA, 2 GND, 3 INA, 4 INB, '
    '5 VDD, 6 OUTB)", "TSOT6", {"1": "TRK_MR", "2": "GND", "3": "TRK_UVS", "4": "TRK_BKS", "5": "TRK_LDO33", "6": "TRK_MR"}, "C132788")\n'
    'c("C67", "100n", "TRK_LDO33", "GND", "C", "C14663", bypass=("U19", "5"))\n'
    'ic("U20", 6, "TPS3808G33DBVR supervisor: the off-time after a trip, the default-off on TRK_LDO33 (SOT-23-6: 1 RESET, 2 GND, 3 MR, '
    '4 CT, 5 SENSE, 6 VDD)", "SOT236", {"1": "TRK_SWEN", "2": "GND", "3": "TRK_MR", "4": "TRK_CT", "5": "TRK_LDO33", "6": "TRK_LDO33"}, "C43698")\n'
    'c("C68", "100n", "TRK_LDO33", "GND", "C", "C14663", bypass=("U20", "6")); '
    'r("R69", "100k 0.1% 25ppm (CT to VDD: the fixed reset delay)", "TRK_CT", "TRK_LDO33", "R", "C122538")\n'
    'r("R70", "8.06k 0.1% 25ppm (SWEN supply guard top)", "TRK_LDO33", "TRK_SWEN", "R", "C861587"); '
    'r("R71", "6.04k 0.1% 25ppm (SWEN pull-down, the guard bottom)", "TRK_SWEN", "GND", "R", "C728595")\n'
    'for _ca in range(4): c("C7%d" % (_ca + 1), "10u 50V", "TRK_VS", "GND", "C10u50")   # L4-E7R: ahead of RSENSE1 at its pad\n')
EDITS = [
    ('r("R59", "15mOhm 1% 2512 (RSENSE1: input-current sense, HoJLR2512-3W-15mR-1%)", "PV_P", "TRK_VIN", "RS2512", "C2903494")',
     'r("R59", "15mOhm 1% 2512 (RSENSE1: input-current sense, HoJLR2512-3W-15mR-1%)", "TRK_VS", "TRK_VIN", "RS2512", "C2903494")   '
     '# L4-E7R: behind the sense bank\n' + BLOCK.rstrip("\n")),
    ('"32": "TRK_VIN", "33": "PV_P", "34": "TRK_VIN", "35": "TRK_INTVCC", "36": "TRK_INTVCC"',
     '"32": "TRK_VIN", "33": "TRK_VS", "34": "TRK_VIN", "35": "TRK_INTVCC", "36": "TRK_SWEN"'),
    ('"100u 35V Panasonic EEHZK1V101XP hybrid polymer (7.7 mm)", "CPOL63", {"1": "TRK_VIN", "2": "GND"}, "C454360")   # L4-E7: behind RSENSE1 (R59)',
     BULK + '   # L4-E7R: 50 V (the surge correction), behind the sense bank, ahead of R59\n'
     'part("C69", "Device", "C_Polarized", ' + BULK),
    ('"SMCJ28A (panel surge: 28 V standoff, conducting from 31.1 V, below the 35 V bulk capacitors; unidirectional, cathode on PV_P)", "TVS", {"1": "PV_P", "2": "GND"}, "C224047")',
     '"SMCJ28A (panel surge: 28 V standoff, clamping at up to 45.4 V at its rated 10/1000 us pulse, under the 50 V bulk; '
     'unidirectional, cathode on TRK_VS)", "TVS", {"1": "TRK_VS", "2": "GND"}, "C224047")   # L4-E7R: behind the sense bank'),
    ('r("R14", "100k 1%", "PV_P", "TRK_SHDN")',
     'r("R14", "100k 1%", "TRK_VS", "TRK_SHDN")'),
    ('r("R16", "23.2k 0.1% 25ppm (RIMON_IN: input-current limit 3.47 A with R59)", "TRK_IMONI", "GND", "R", "C861244"); ',
     'r("R16", "30k 0.1% 25ppm (RIMON_IN: input-current limit 2.68 A with R59, under the backstop)", "TRK_IMONI", "GND", "R", "C723585"); '),
    ('loads={"F2" if _pvn == "PV_IN" else "R59": 5.68}',
     'loads=({"F2": 5.68} if _pvn == "PV_IN" else {"R6%d" % _bk: 5.68 / 5 for _bk in range(5)})'),
    ('# L4-E7: TRK_VIN, the tracker\'s input behind RSENSE1 (R59), is a series segment of PV_P at its voltage, carried by M1 (Q3).\n',
     '# L4-E7R: TRK_VS, between the sense bank (R60 to R64) and RSENSE1 (R59), is a series segment of PV_P at its voltage.\n'
     '_intent.rail("TRK_VS", _intent.rail_volts("PV_P"), 5.68, 6.25, ["R60", "R61", "R62", "R63", "R64"], loads={"R59": 5.68},\n'
     '             v_work=25.0, v_max=25.0, converted=False, series_of="PV_P", note="the panel current past the sense bank, into "\n'
     '             "RSENSE1 (R59); D4, the 50 V bulk, C71 to C74 and U18\'s supply sit on it (L4-E7R)")\n'
     '# L4-E7: TRK_VIN, the tracker\'s input behind RSENSE1 (R59), is a series segment of PV_P at its voltage, carried by M1 (Q3).\n'),
    ('"R14", "R15", "R16", "R17", "R59", "C65", "C24"',
     '"R14", "R15", "R16", "R17", "R59", "C65", "R60", "R61", "R62", "R63", "R64", "U18", "C66", "R65", "R66", "R67", "R68", "U19", '
     '"C67", "U20", "C68", "R69", "R70", "R71", "C69", "C70", "C71", "C72", "C73", "C74", "C24"'),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if 'r("R59", ' not in text:
        refuse("apply_gen_sch_e_input_limit.py is not applied (no R59): the old text occurs 0 times, not once")
    if 'r("R8", "102k 0.1% 25ppm' not in text:
        refuse("apply_gen_sch_e_hold.py is not applied (R8 is not the RT part the bound counts): the old text occurs 0 times, not once")
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
