#!/usr/bin/env python3
"""Set 9's carried minor items taken in integration set 10 (MESHSAT-1357, 29 September 2026), before its re-take:
  M2   IF-AB-POWER's +5V_DEV row cited "gen_sch_a.py, the S-99 lines"; it now names the rail's line, read from the
       generator at run time (the `_intent.rail("+5V_DEV"` call), not typed.
  M10  board A's EMC sheet did not declare U3, the BQ25731 charger, and emc_sheet.py's switcher list did not know the part,
       so its completeness test could not see it. The part is added to the list and U3 to the sheet with its maker's
       frequency facts (SLUSE66A: PWM_FREQ 1b = 400 kHz is the power-on default, 0b = 800 kHz; 4.7 uH recommended at 400 kHz,
       2.2 uH at 800 kHz); board A fits 3.3 uH (L2) and no firmware setting is declared: open item S-117 records that.
  M11  the U41 row names the lead its output leaves on (J_MEZZ_PWR1) and the maker's frequency tolerance; the sheet's paths
       stop counting converters ("five LM5176" where seven are declared, "all five converters" where twelve are).
Asserts each old text once, re-parses every file, refuses a second run. Run from the repository root."""
import os, re, subprocess, sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
T = os.path.join(TOP, "v2/ecad/tools")


def refuse(m):
    print("apply_carried_minors_s9: REFUSED: %s" % m); sys.exit(2)


def once(t, a, b, what):
    if t.count(a) != 1: refuse("%s: old text found %d times" % (what, t.count(a)))
    t2 = t.replace(a, b)
    if t2 == t: refuse("%s: unchanged" % what)
    return t2


def main():
    gen = open(os.path.join(T, "gen_sch_a.py"), encoding="utf-8").read().split("\n")
    lines = [i + 1 for i, l in enumerate(gen) if l.startswith('_intent.rail("+5V_DEV"')]
    if len(lines) != 1: refuse("gen_sch_a.py has %d +5V_DEV rail calls" % len(lines))
    ln = lines[0]
    pi = os.path.join(T, "pcb_interfaces.yaml"); ti = open(pi, encoding="utf-8").read()
    if "(gen_sch_a.py:%d, the +5V_DEV rail" % ln in ti: refuse("already applied (a second run)")
    ti = once(ti, "(gen_sch_a.py, the S-99 lines)", "(gen_sch_a.py:%d, the +5V_DEV rail call, with S-99's comment block above it)" % ln, "M2")
    pe = os.path.join(T, "pcb_emc.yaml"); te = open(pe, encoding="utf-8").read()
    u41 = [l for l in te.split("\n") if "board A's netlist leaves U41 pin 1 unconnected." in l]
    if len(u41) != 1: refuse("the U41 row's basis is not found once")
    te = te.replace("board A's netlist leaves U41 pin 1 unconnected.",
                    "board A's netlist leaves U41 pin 1 unconnected; the maker gives the frequency's tolerance and spread in sections 8.5 and 9.3.10 (not a declared figure here). Its output leaves board A on J_MEZZ_PWR1 to board D.", 1)
    anchor = "    - {ref: U41, part: TPS62933,"
    if te.count(anchor) != 1: refuse("the U41 row is not found once")
    u3 = ('    - {ref: U3, part: BQ25731, what: "4S buck-boost charger, VBUS20 to the system node VBAT and the pack", f_khz: 400, edge_ns: null,\n'
          '       basis: "v2/vendor/ti/bq25731-datasheet.pdf (SLUSE66A), ChargeOption0 PWM_FREQ: 1b 400 kHz is the default at power-on, 0b 800 kHz; the maker recommends 4.7 uH at 400 kHz and 2.2 uH at 800 kHz, and board A fits 3.3 uH (L2, gen_sch_a.py); no firmware setting is declared (open item S-117); frequency dithering is available and register-enabled, not declared"}\n')
    te = te.replace(anchor, u3 + anchor, 1)
    te = once(te, '{from: "the five LM5176 switch nodes",', '{from: "the LM5176 switch nodes",', "M11 path")
    te = once(te, '"radiated emissions with all five converters loaded', '"radiated emissions with every converter above loaded', "M11 plan")
    pt = os.path.join(T, "emc_sheet.py"); tt = open(pt, encoding="utf-8").read()
    tt = once(tt, '"TPS56637", "LMR33640", "TPS23861")', '"TPS56637", "LMR33640", "TPS23861", "BQ25731")', "M10 tool")
    pr = os.path.join(T, "pcb_requirements.yaml"); tr = open(pr, encoding="utf-8").read()
    if "\n  - id: S-117\n" in tr: refuse("S-117 exists")
    item = ('  - id: S-117\n'
            '    class: SESSION\n'
            '    status: OPEN\n'
            '    title: >-\n'
            '      (set 9\'s AI check, minor item M10) Board A\'s charger U3 (BQ25731) switches at the frequency its PWM_FREQ bit\n'
            '      selects: 400 kHz at power-on, 800 kHz when firmware clears it (SLUSE66A, ChargeOption0). The maker recommends\n'
            '      4.7 uH at 400 kHz and 2.2 uH at 800 kHz; board A fits 3.3 uH (L2, XAL6030-332ME) and no firmware setting is\n'
            '      declared in HW-FW-CONTRACT.md. The inductor ripple current and the EMC sheet\'s frequency follow from the\n'
            '      choice. Closes when the setting is declared in the firmware contract and L2 is shown against the maker\'s\n'
            '      ripple guidance at that frequency (or changed by board A\'s writer), with the EMC row updated to match.\n'
            '    disposition: LAYOUT_STAGE\n'
            '    disposition_why: board A\'s charger design choice, decided with its firmware contract before board A\'s layout; no\n'
            '      schematic-phase record rests on the frequency.\n')
    i = tr.index("\nclosed_items:\n")
    tr2 = tr[:i + 1] + item + tr[i + 1:]
    for p, t, parse in ((pi, ti, yaml.safe_load), (pe, te, yaml.safe_load), (pr, tr2, yaml.safe_load)):
        parse(t)
    import ast; ast.parse(tt)
    for p, t in ((pi, ti), (pe, te), (pt, tt), (pr, tr2)):
        open(p, "w", encoding="utf-8").write(t)
    print("apply_carried_minors_s9: M2 at gen_sch_a.py:%d, M10 (U3 row, BQ25731 in the switcher list, S-117 opened), M11 applied" % ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
