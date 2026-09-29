#!/usr/bin/env python3
"""Set 10's AI check, blocking item B1 and minor item M9, answered (MESHSAT-1357, 29 September 2026). The U3 row of board A's
EMC sheet and open item S-117 said the BQ25731 starts at 400 kHz from its PWM_FREQ register default. TI's datasheet says the
charger reads its switching frequency and its inductance from the resistor on its IADPT pin before the converter starts
(SLUSE66A 9.3.11 and Table 9-4, printed page 27: 169 kOhm, 3 percent or better, for 3.3 uH at 800 kHz; 191 or 187 kOhm for
4.7 uH at 400 kHz), and board A's IADPT net carries only U3 pin 8 and TP19: no resistor, and not the 100 pF capacitor the pin
table asks for. That is round 4's finding O-24 (records/r4a/r4-open-items.md), never carried into the registry. This script
restates S-117 as a schematic-phase item on that circuit, drops its layout-stage disposition, makes REQ-015 (the input that
charges the pack) wait on it, restates the U3 row's basis, and names U23 on the U41 row's path to J_MEZZ_PWR1 (M9).
Asserts each old text once, re-parses both files, checks only the named fields moved, refuses a second run."""
import os, subprocess, sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
EMC = os.path.join(TOP, "v2/ecad/tools/pcb_emc.yaml")
TITLE = ("(set 10's AI check, blocking item B1; round 4's finding O-24, records/r4a/r4-open-items.md) Board A's charger U3 "
         "(BQ25731) reads its switching frequency and its inductance from the resistor on its IADPT pin before the converter starts "
         "(TI SLUSE66A 9.3.11 and Table 9-4, printed page 27: 169 kOhm, 3 percent or better, for 3.3 uH at 800 kHz; 191 or 187 kOhm "
         "for 4.7 uH at 400 kHz). Board A's IADPT net carries only U3 pin 8 and TP19: no resistor, and not the 100 pF capacitor the "
         "pin table asks for, so the frequency and inductance the drawn circuit starts with are not established. Its COMP1 and COMP2 "
         "networks are not those of the datasheet's compensation table for either frequency, and PWM_FREQ's power-on default (1b, "
         "400 kHz) is the frequency TI pairs with 4.7 uH, where board A fits 3.3 uH (L2). Closes when board A's writer draws the IADPT "
         "resistor and capacitor for the chosen inductor and frequency and the compensation networks from the datasheet's table, "
         "the firmware contract declares PWM_FREQ to match, and the EMC sheet's U3 row carries that frequency.")


def refuse(m):
    print("apply_s117_restate: REFUSED: %s" % m); sys.exit(2)


def main():
    t = open(REG, encoding="utf-8").read()
    if "blocking item B1; round 4's finding O-24" in t: refuse("already applied (a second run)")
    before = yaml.safe_load(t)
    i, j = A.span(t, "S-117")
    blk = t[i:j]
    a = blk.index("    title: >-\n"); b = blk.index("    disposition: LAYOUT_STAGE\n")
    c = blk.index("    disposition_why:"); rest = blk[c:]
    k = rest.find("\n  - id: "); k = len(rest) if k < 0 else k
    new_blk = blk[:a] + "    title: >-\n" + A.fold(TITLE, 6, 120) + "\n"
    new_blk = new_blk.rstrip("\n") + "\n"
    A.screen(TITLE, "S-117's title")
    t2 = t[:i] + new_blk + t[j:]
    # REQ-015 waits on S-117
    ri, rj = A.span(t2, "REQ-015")
    rb = t2[ri:rj]
    old_w = "    waits_on: [S-106, S-107, S-111]\n"
    if rb.count(old_w) != 1: refuse("REQ-015's waits_on is not as read")
    rb = rb.replace(old_w, "    waits_on: [S-106, S-107, S-111, S-117]\n")
    t2 = t2[:ri] + rb + t2[rj:]
    after = yaml.safe_load(t2)
    ib, ia = {x["id"]: x for x in before["open_items"]}, {x["id"]: x for x in after["open_items"]}
    if set(ia["S-117"]) != {"id", "class", "status", "title"}: refuse("S-117 keeps fields %s" % sorted(ia["S-117"]))
    for k2 in ib:
        if k2 != "S-117" and ib[k2] != ia[k2]: refuse("open item %s moved" % k2)
    rb_, ra_ = {r["id"]: r for r in before["records"]}, {r["id"]: r for r in after["records"]}
    for k2 in rb_:
        d = {f for f in set(rb_[k2]) | set(ra_[k2]) if rb_[k2].get(f) != ra_[k2].get(f)}
        if d and not (k2 == "REQ-015" and d == {"waits_on"}): refuse("%s moved in %s" % (k2, d))
    e = open(EMC, encoding="utf-8").read()
    a1 = [l for l in e.split("\n") if "ref: U3, part: BQ25731" in l]
    if len(a1) != 1: refuse("the U3 row is not found once")
    e2 = e.replace(a1[0], a1[0].replace("f_khz: 400,", "f_khz: 800,"))
    old_basis = [l for l in e2.split("\n") if "v2/vendor/ti/bq25731-datasheet.pdf (SLUSE66A), ChargeOption0 PWM_FREQ" in l]
    if len(old_basis) != 1: refuse("the U3 basis is not found once")
    new_basis = ('       basis: "v2/vendor/ti/bq25731-datasheet.pdf (SLUSE66A) 9.3.11 and Table 9-4, printed page 27: the charger reads its frequency and '
                 'inductance from the resistor on IADPT before it starts; 800 kHz is the frequency TI recommends for the fitted 3.3 uH (L2) with '
                 '169 kOhm, the design\'s intent. Board A\'s IADPT net carries no resistor and no 100 pF capacitor, so the frequency the drawn '
                 'circuit starts at is not established (open item S-117); PWM_FREQ\'s power-on default is 400 kHz; frequency dithering is '
                 'available and register-enabled, not declared"}')
    e2 = e2.replace(old_basis[0], new_basis)
    m9 = "Its output leaves board A on J_MEZZ_PWR1 to board D."
    if e2.count(m9) != 1: refuse("the U41 row's lead sentence is not found once")
    e2 = e2.replace(m9, "Its output reaches board A's J_MEZZ_PWR1, to board D, as +5V_D8 through the eFuse U23.")
    yaml.safe_load(e2)
    open(REG, "w", encoding="utf-8").write(t2)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    open(EMC, "w", encoding="utf-8").write(e2)
    print("apply_s117_restate: S-117 restated as a schematic item (REQ-015 waits on it); the U3 row at the design's 800 kHz with the missing IADPT resistor named; U41's path names U23")
    return 0


if __name__ == "__main__":
    sys.exit(main())
