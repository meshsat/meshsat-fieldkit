#!/usr/bin/env python3
"""apply_fw_a16.py: DRAFT for the coordinator (layer 4 task L4-E5, MESHSAT-1357, 1 October 2026). NOT APPLIED to the tree by
L4-E5; its author ran it only on scratch copies with --check (and --write on a copy, for the test).

What it changes in v2/docs/HW-FW-CONTRACT.md, and nothing else (L4E5-SOURCE-CONTROL.md, l4e5_source_control.out):
  - FW-A16 restated: IIN_HOST a constant 4.70 A ceiling (L4-E4's setting, provisional with it), rewritten after every adapter
    removal; EN_EXTILIM kept 1b; VINDPM as before; a stale or missing VIN_MON changes no setting; VIN_MON and the charger's
    input ADC as a diagnostic that falls back to the previous rule only when the hardware line is seen to fail;
  - FW-A18 added after FW-A17: the hardware line on U3's ILIM_HIZ pin (OWED, not drawn) and the tracker's raised ceiling;
  - FW-E04: VIN_MON reported for FW-A16's diagnostic, not as a control input;
  - V-A06 to V-A10 added after V-A05 (steady state, the crossover, transients, startup and the knee, telemetry faults);
  - section 3.1's heading to FW-A18; FW-C01's step 5 names A18; a change-record row.

Usage:  apply_fw_a16.py TARGET [--check | --write]     (default --check: nothing is written)
Guards: every anchor is found exactly once by its first cell or its exact text; every new row has its table's cell count; a
second application refuses (FW-A18 is a row, or the restated FW-A16 is there); the result, with the edits taken back out, is
the input line for line; no dash character. Exit 0: checked (or written); 3: refused."""
import sys

HEAD_OLD = "### 3.1 Board A: power controller, charger, monitors and enables (FW-A01 to FW-A17)"
HEAD_NEW = "### 3.1 Board A: power controller, charger, monitors and enables (FW-A01 to FW-A18)"
C01_OLD = "5. the charger (FW-A01 to A03, A16, A17);"
C01_NEW = "5. the charger (FW-A01 to A03, A16, A17, A18);"
E04_OLD = "| Report both over USB at 1 s for FW-A16 | FW-A16 |"
E04_NEW = ("| Report both over USB at 1 s; VIN_MON feeds FW-A16's diagnostic (f) only, never a control setting (L4-E5): a late or "
           "missing report changes no charger setting | FW-A16 |")
FW_A16 = ("| FW-A16 | BQ25731 `A:U3` IIN_HOST (REG 0x0F/0E; SLUSE66A p.80 annotates its reset 2000h in the heading and 4100h in the "
          "figure, Table 9-50's reset bits read 0x20, 3.2 A in the 5 mOhm terms of POR; the one-time reset after every adapter removal "
          "is 3.25 A, p.26 and p.80) and InputVoltage (REG 0x0B/0A); "
          "ChargeOption2 EN_EXTILIM (REG0x32 bit 7, reset 1b, p.63), so U3's input limit is the lower of IIN_HOST and the ILIM_HIZ "
          "pin (p.6; 9.3.6, p.26), the pin following VIN_RAW in hardware (FW-A18, OWED); FE_PGOOD on `A:U27.20` IO1_7 (R13 100 k "
          "to +3V3) and CHRG_OK on `A:U27.13` IO1_0, both raising EXP_INT (`A:U27.1`); board E's VIN_MON = 0.0909 x VIN_RAW "
          "(`E:R40` 100 k over R41 10 k, `E:U10.39` GPIO27 ADC1), reported over USB (FW-E04) | (a) Hold IIN_HOST at 4.70 A "
          "(code 94, 0x5E00; RSNS_RAC = 0b first, FW-A01; L4-E4's setting, provisional with it) and never write a higher value: the "
          "VIN_RAW dependence is FW-A18's pin, not firmware. (b) At POR the register holds its power-on value, at most 3.25 A of "
          "board current at RSNS_RAC = 1b on either annotation (INFERRED), recorded raw with RSNS_RAC by V-A09; after FW-A01 write "
          "4.70 A. After every adapter removal U3 resets IIN_HOST once to 3.25 A; on CHRG_OK or FE_PGOOD falling (EXP_INT) write "
          "4.70 A while the adapter is absent (9.3.6 allows the write under battery only and does not reset it again at the next "
          "plug-in); until written the reset applies, under the pin. (c) Once FE_PGOOD is high, "
          "write VINDPM to about 18.5 V. (d) Keep EN_EXTILIM = 1b: every ChargeOption2 write is read-modify-write keeping REG0x32 "
          "bit 7, read back at every service. (e) A missing or stale VIN_MON (older than 3 s) changes no setting. (f) Diagnostic "
          "only: with VIN_MON fresh and the charger's input ADC (ADCIIN, 9.6.9; EN_ADC_IIN set) above FW-A18's band at that "
          "VIN_RAW by more than 0.3 A in three readings in a row, report FW-A18 failed and fall back to the previous rule: IIN_HOST "
          "at or below 0.80 x 4.80 A x 0.93 x VIN_RAW / 20.7 V and at most 4.70 A, the 9 V figure 1.55 A while VIN_MON is stale | "
          "the vehicle entry's LM5069 limits at 4.85 to 6.15 A and its fault timer runs 3.1 to 8.2 ms, a solar deficit empties "
          "VIN_RAW in 1 to 10 ms, and FW-E04's 1 s cannot act inside either; no drawn line tells the tracker from a vehicle on "
          "VIN_RAW (`records/l4e5/L4E5-SOURCE-CONTROL.md`) | V-A06 to V-A10; FW-A15 item 10 | FIRMWARE; FW-A18 OWED |")
FW_A18 = ("| FW-A18 | OWED (L4-E5, not drawn): `A:U3` pin 6 ILIM_HIZ (CHG_ILIM) driven from VIN_RAW on board A in place of R19 and "
          "R20's fixed divider from REGN, Q6's HIZ pull-down (CHG_INHIBIT) kept: at and above 9.0 V, V(ILIM_HIZ) = 1.000 V + "
          "0.0690 V/V x VIN_RAW (U3's input 0.17252 A/V x VIN_RAW at R16 10 mOhm, SLUSE66A p.6: V = 1 V + 40 x IDPM x RAC), "
          "inside +-1 % plus the pin's own error; below 9.0 V a knee: the pin at 1.0 V (no current) at 8.750 V, falling to 0.4 V "
          "(HIZ entry, p.17 VHIZ_HIGH and p.6) at 8.508 V and rising to 0.8 V (HIZ exit, VHIZ_LO) at 8.669 V nominal, so with the "
          "network at +-0.5 % U3 is certainly in HIZ below 8.466 V, above the restart guard's highest 8.31 V, and certainly "
          "converting above 8.713 V; on board E the tracker's ceiling "
          "raised (`E:R10` 232 k, about 28.3 to 30.2 V, TRK_OUT's 25 V parts re-rated) so the line admits REQ-016's window | "
          "Never write EN_EXTILIM = 0b; drive CHG_INHIBIT only as FW-A14 says; nothing else (the line is hardware) | U3's VINDPM "
          "watches the regulated VBUS20, so only a line on VIN_RAW itself acts at the charger's loop speed, for every source and "
          "without telling them apart (`records/l4e5/`) | V-A06 to V-A10 | OWED |")
V_A06 = ("| V-A06 | FW-A16, A18 | steady state: a stiff supply on VIN_RAW at 9, 12, 24, 27, 28 and 36 V with U3 asking more than "
         "its limit: U3's input current by a reference meter inside the line's band (0.17252 A/V x VIN_RAW, +-1 % and the pin's "
         "own error), and the front end's input current at most 4.80 A at 9 V |")
V_A07 = ("| V-A07 | FW-A18 | the crossover: VIN_RAW stepped from 26.0 to 28.5 V in 0.1 V steps on a stiff supply: U3's input "
         "current at most 4.817 A x 10 mOhm / R16 measured four-wire (the pin's error at most 0.071 A there), or R11 re-chosen "
         "by L4-E4's rule (`records/l4e5/` section 7) |")
V_A08 = ("| V-A08 | FW-A16, A18 | transients, recorded apart from steady state: the vehicle supply stepped 24 to 12 V, 36 to 9 V "
         "and 12 to 24 V, plugged and unplugged, and a panel simulator stepped from 100 W into the stage to 50, 30 and 10 W and "
         "back, each under U3's full demand: the LM5069's TIMER never reaches 3.76 V, VIN_RAW never falls below 8.41 V (the guard's "
         "highest 8.31 V plus 0.1 V), "
         "FE_PGOOD never drops; the peak and settling time of U3's input current recorded |")
V_A09 = ("| V-A09 | FW-A16, A18 | startup and the knee, with no host and U3 asked for full charge, VIN_RAW swept quasi-statically "
         "(10 mV steps, each held 1 s) from 9.5 V down to 8.35 V and back up: U3 converting at every VIN_RAW above 8.713 V and in "
         "HIZ at every VIN_RAW below 8.466 V; the HIZ entry on the falling sweep (the pin falling to 0.4 V, SLUSE66A p.17 VHIZ_HIGH "
         "and p.6) recorded against 8.508 V predicted (8.466 to 8.551 V with the network's +-0.5 %), the HIZ exit on the rising "
         "sweep (the pin rising to 0.8 V, VHIZ_LO) against 8.669 V (8.626 to 8.713 V), the pin's 1.0 V zero-current target (p.6) "
         "against 8.750 V (8.706 to 8.794 V), each with the pin's voltage; U3's input current at most the line's band from 8.854 V "
         "up (the pin inside the printed 1.15 to 4 V range, p.10) and recorded below it, at least 1.068 A at 9.0 V; then shore at "
         "9, 12 and 24 V. With the host: raw IIN_HOST (REG0x0F/0E) and ChargeOption1's RSNS_RAC recorded at POR before FW-A01 and "
         "after it, the POR value kept apart from the one-time 3.25 A reset after an adapter removal (p.80 annotates 2000h and "
         "4100h), then 4.70 A after the first service and after every removal |")
V_A10 = ("| V-A10 | FW-A16, E04 | telemetry fault injection, every kit-bus write logged, U3 asked more than its limit: (1) on shore "
         "at 12 V and on the panel simulator at 50 W, the sensor controller's reports stopped for 30 s (U10 held in reset at TP12, "
         "or its USB lead out) and resumed, and (2) absent from boot: no write to IIN_HOST, ChargeOption2 or InputVoltage, "
         "IIN_HOST reads 4.70 A throughout and U3's input current stays inside the line's band; (3) a laboratory supply of at "
         "least 10 A on VIN_RAW at 12 V in place of the entry, FW-A18 made to fail by lifting the pin above 4.0 V through a fitted "
         "test link, VIN_MON fresh, for at most 10 s: two readings above 2.623 A of board current (the band's 2.323 A plus 0.3 A) "
         "do not trigger the fallback and the third in a row does; after it IIN_HOST is the line at the reported VIN_RAW rounded down, "
         "2.05 A at 12 V, and the failure is reported; then VIN_MON stopped: IIN_HOST written to 1.55 A once the last report is "
         "older than 3 s; no write above 4.70 A at any point of (1) to (3) |")
LOG = ("| 1 (L4-E5) | 1 October 2026 | By layer 4 task L4-E5 (MESHSAT-1357, `records/l4e5/`): FW-A16 restated (IIN_HOST a "
       "constant 4.70 A ceiling, the VIN_RAW dependence moved to hardware), FW-A18 added (OWED), FW-E04's VIN_MON made "
       "diagnostic, V-A06 to V-A10 added |")
NEW_ROWS = (FW_A18, V_A06, V_A07, V_A08, V_A09, V_A10, LOG)


def refuse(msg):
    sys.stderr.write("apply_fw_a16: %s; refusing\n" % msg)
    sys.exit(3)


def cells(line):
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return None
    return [c.strip() for c in s[1:-1].split("|")]


def patched(t):
    lines = t.split("\n")
    first = [(i, cells(l)) for i, l in enumerate(lines)]
    if any(c and c[0] == "FW-A18" for _, c in first) or FW_A16 in lines:
        refuse("already applied (FW-A18 is a row, or FW-A16 is restated)")
    idx = {}
    for key in ("FW-A16", "FW-A17", "V-A05"):
        hits = [i for i, c in first if c and c[0] == key]
        if len(hits) != 1:
            refuse("%s occurs %d times, not once" % (key, len(hits)))
        idx[key] = hits[0]
    n_fw = len(first[idx["FW-A16"]][1])
    for row in (FW_A16, FW_A18):
        if len(cells(row)) != n_fw:
            refuse("a new contract row does not have FW-A16's %d cells" % n_fw)
    for row in (V_A06, V_A07, V_A08, V_A09, V_A10):
        if len(cells(row)) != len(first[idx["V-A05"]][1]):
            refuse("a new verification row does not have V-A05's cells")
    for what, old in (("section 3.1's heading", HEAD_OLD), ("FW-C01's step 5", C01_OLD), ("FW-E04's obligation", E04_OLD)):
        if t.count(old) != 1:
            refuse("%s occurs %d times, not once" % (what, t.count(old)))
    k = len(lines) - 1
    while k >= 0 and not lines[k].strip():
        k -= 1
    last = cells(lines[k])
    if not last or not last[0].startswith("1 (S-117)"):
        refuse("the change record's last row is not as read")
    if len(cells(LOG)) != len(last):
        refuse("the change-record row does not have the table's cells")
    old16 = lines[idx["FW-A16"]]
    new = list(lines)
    new.insert(k + 1, LOG)
    new.insert(idx["V-A05"] + 1, V_A10)
    new.insert(idx["V-A05"] + 1, V_A09)
    new.insert(idx["V-A05"] + 1, V_A08)
    new.insert(idx["V-A05"] + 1, V_A07)
    new.insert(idx["V-A05"] + 1, V_A06)
    new.insert(idx["FW-A17"] + 1, FW_A18)
    new[idx["FW-A16"]] = FW_A16
    out = "\n".join(new).replace(HEAD_OLD, HEAD_NEW).replace(C01_OLD, C01_NEW).replace(E04_OLD, E04_NEW)
    if "\u2014" in out or "\u2013" in out:
        refuse("a dash character")
    back = [l for l in out.replace(HEAD_NEW, HEAD_OLD).replace(C01_NEW, C01_OLD).replace(E04_NEW, E04_OLD).split("\n") if l not in NEW_ROWS]
    back = [old16 if l == FW_A16 else l for l in back]
    if "\n".join(back) != t:
        refuse("something beyond the edits moved")
    if out == t:
        refuse("the result does not differ")
    return out


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__)
        return 2
    target = args[0]
    t = open(target, encoding="utf-8").read()
    out = patched(t)
    if "--write" in flags:
        open(target, "w", encoding="utf-8").write(out)
        print("WRITTEN %s (+%d lines)" % (target, out.count("\n") - t.count("\n")))
    else:
        print("CHECK OK %s: FW-A16 restated, FW-A18, V-A06 to V-A10, heading, FW-C01, FW-E04 and the change record; nothing written" % target)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
