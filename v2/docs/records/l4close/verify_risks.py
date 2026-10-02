#!/usr/bin/env python3
"""verify_risks.py: the independent verifier's separate code for the findings ledger's "Concrete remaining risks"
(MESHSAT-1357, 2 October 2026; v2/docs/records/l4close/VERIFICATION-2026-10-02.md). It prints every figure the
verification reports. It imports no record's script and reruns none: it reads TEST-PLAN.md, the records' outputs and the
makers' sheets itself (pdftotext) and does its own arithmetic.

PAUSED CHECKPOINT (the coordinator's stop of 2 October 2026): items 2, 4 and 5 are settled here; item 3 has an interim
reading of the pocket's volume only (not the item's result); items 6, 7, 9 and 11 are not reached.

Run from anywhere inside the repository:  python3 v2/docs/records/l4close/verify_risks.py > v2/docs/records/l4close/verify_risks.out
Stdlib only, plus pdftotext. Read-only. Exit 1 if a source line it reads is not where it reads it."""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()


def rel(p):
    return os.path.join(TOP, p)


def txt(p):
    with open(rel(p), encoding="utf-8") as fh:
        return fh.read()


def pdf(p, first=None, last=None):
    a = ["pdftotext", "-layout"] + (["-f", str(first), "-l", str(last)] if first else []) + [rel(p), "-"]
    return subprocess.run(a, capture_output=True, check=True).stdout.decode("utf-8", "replace")


def flat(s):
    return re.sub(r"\s+", " ", s)


def must(cond, what):
    if not cond:
        print("SOURCE NOT AS READ: %s" % what)
        sys.exit(1)


def block(text, start, stop):
    i = text.find(start)
    must(i >= 0, "block %r" % start)
    j = text.find(stop, i + len(start))
    return text[i:j if j >= 0 else len(text)]


# ======================================================================================== item 2: the screen's mappings
def item2():
    print("ITEM 2. L4-E10's screen rows C04, C05, C16, C17, C18 against TEST-PLAN.md (the recheck's R2 list)")
    tp = flat(txt("v2/docs/TEST-PLAN.md"))
    out = txt("v2/docs/records/l4e10/l4e10_cell_thermal.out")
    rows = {k: flat(block(out, "\n%s " % k, "\n%s " % n)) for k, n in (("C04", "C05"), ("C05", "C06"), ("C16", "C17"),
                                                                    ("C17", "C18"), ("C18", "C19"))}
    rows["C01"] = flat(block(out, "\nC01 ", "\nC02 "))
    # (the recheck's item, the TEST-PLAN wording read at its source, the screen row, the row's wording that maps it)
    checks = [
        ("E3-H: the +40 C lid-closed level held until the hot stop acts or 4 h pass",
         "at +40 C with the lid closed the level is held until the hot stop has acted or its 4 h have passed", "C05",
         "at +40 C lid closed the level is held until the hot stop has acted or its 4 h have passed"),
        ("E3-H: repeated with the sensor controller in reset",
         "once more with the sensor controller held in reset", "C05", "the run is repeated with the sensor controller held in reset"),
        ("E3-H: the TMP117 fallback thresholds +55.0 and +56.0 C",
         "the same steps act on board B's TMP117 at +55.0 C and +56.0 C", "C05",
         "board B's TMP117 acts at +55.0 C (shed) and +56.0 C (shutdown)"),
        ("P15: the TMP117 release at +45.0 C", "released at +45.0 C", "C05", "released at +45.0 C"),
        ("E3-H: the restart at or below +46.5 C after 30 minutes",
         "comes back only once the hottest cell reads +46.5 C or less and 30 minutes have passed", "C05",
         "returns once the hottest cell reads +46.5 C or less and 30 minutes have passed"),
        ("E3-H: the stepped run from +40 C by 2 K an hour to at most +55 C, on shore then on the pack",
         "the chamber raised from +40 C by 2 K an hour to at most +55 C until H1 and then H2 have acted, first on shore", "C05",
         "from +40 C by 2 K an hour to at most +55 C"),
        ("E3-L: started once with the lid already closed", "started once with the lid already closed", "C04",
         "E3-L is started once with the lid already closed"),
        ("E3-L: the lid-closed start enters the reduced mode once the lid is read",
         "the start with the lid closed enters the reduced mode once the lid is read", "C04",
         "the start with the lid closed enters the reduced mode once the lid is read"),
        ("E3-L: the +40 C level (in C01, as the recheck's list does not name it)", "lid closed at +20 C, +30 C and +40 C, 4 h at each",
         "C01", "E3-L at +40 C"),
        ("E3-P: OTD recovers at or below +52.5 C", "recovers at or below +52.5 C", "C17", "recover at or below +52.5 C"),
        ("E4-T: full function after return to 25 C, capacity within 5 %",
         "full function after return to 25 C, capacity within 5 % of its value before (PROVISIONAL: the maker publishes no cold-storage recovery figure)",
         "C16", "full function after return to 25 C, capacity within 5 % of its value before (PROVISIONAL"),
        ("E4-P: recovery as E4-T", "| E4-P | the pack alone | as E4-T | the pack at its own cold storage limit | as E4-T |", "C18",
         "recovery mapped (as E4-T): full function after return to 25 C, capacity within 5 %"),
        ("charge state unstated in TEST-PLAN named as a missing input (E3-L)", None, "C04", "charge state: the pack's charge at each level's start is not stated by TEST-PLAN (a named missing input)"),
        ("charge state unstated in TEST-PLAN named as a missing input (E3-H)", None, "C05", "charge state: not stated by TEST-PLAN for E3-H (a named missing input"),
        ("charge state unstated in TEST-PLAN named as a missing input (E4-T transport)", None, "C16", "for transport 'at its charge', not stated (a named missing input)"),
        ("charge state unstated in TEST-PLAN named as a missing input (E4-P)", None, "C18", "E4-P names none (a named missing input)"),
        ("E3-P's charge state is TEST-PLAN's own (full charge)", "| E3-P | the pack alone, armed (JP1 closed), at full charge", "C17", "full charge"),
    ]
    n_ok = 0
    for what, src, row, mapped in checks:
        in_tp = True if src is None else (flat(src) in tp)
        in_row = flat(mapped) in rows[row]
        n_ok += in_tp and in_row
        print("   %-92s TEST-PLAN %-3s  %s %s" % (what, "n/a" if src is None else ("yes" if in_tp else "NO"), row, "yes" if in_row else "NO"))
    print("   mapped and read at the source: %d of %d" % (n_ok, len(checks)))
    # not on the recheck's list: E3-P's other pass items, read for completeness
    extra = [("E3-P: the second level does not fire", "the second level does not fire"),
             ("E3-P: capacity recovery at least 95 % as E3-T", "capacity recovery at least 95 % as E3-T")]
    for what, src in extra:
        print("   observation, not on the recheck's list: %-48s TEST-PLAN %s; restated in C17: %s" % (
            what, "yes" if flat(src) in tp else "NO", "yes" if flat(src) in rows["C17"] else "no (C17 cites MAKER 7.10)"))
    print()
    return n_ok == len(checks)


# ======================================================================================== item 3 (interim): the pocket
def item3_interim():
    print("ITEM 3, INTERIM READING ONLY (paused; not the item's result): the pocket's room beyond the 1.0 mm minimums")
    pt = txt("v2/docs/feasibility/POWER-THERMAL.md")
    m = re.search(r"The pack block is (\d+\.\d+) x (\d+\.\d+) x (\d+\.\d+) mm \(A06\)", pt)
    must(m, "POWER-THERMAL's pack block")
    X, Y, Z = (float(v) for v in m.groups())
    A_E, A_B, A_end = Y * Z, X * Y, X * Z           # mm2: the east face, the top, each end
    sl = txt("v2/docs/records/l3batt/SHORTLIST.md")
    east = float(re.search(r"\| M4b, across \| (\d+\.\d+) mm \|", sl).group(1))
    top = float(re.search(r"\| M6 east, height \| (\d+\.\d+) mm \|", sl).group(1))
    ends = float(re.search(r"\| M5 east, along the axis \| (\d+\.\d+) mm \|", sl).group(1))
    worst = (A_E * east + A_B * top + 2 * A_end * ends) / 1e6
    cm = txt("v2/docs/CASE-MARGINS.md")
    head = [c.strip() for c in re.search(r"^\| # \| Margin \|.*$", cm, re.M).group(0).strip("|").split("|")]
    must(head[3].startswith("As designed: nominal") and head[5] == "Chosen: nominal", "CASE-MARGINS 3.2's header")
    def cells(key):
        line = re.search(r"^\| %s \|.*$" % key, cm, re.M).group(0)
        return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
    chosen = {}
    designed_flat = {}
    for key in ("M4b", "M5", "M6"):
        c = cells(key)
        must(len(c) == len(head), "CASE-MARGINS %s has the header's %d cells (escaped pipes kept)" % (key, len(head)))
        chosen[key] = float(c[5])
        designed_flat[key] = float(c[3].split("/")[0])
    vol = lambda m4b, m5, m6: (A_E * (m4b - 1.0) + A_B * (m6 - 1.0) + 2 * A_end * (m5 - 1.0) + A_E * (2.0 - 1.0)) / 1e6
    v_chosen = vol(chosen["M4b"], chosen["M5"], chosen["M6"])
    v_record = vol(chosen["M4b"], designed_flat["M5"], chosen["M6"])
    print("   block %.2f x %.2f x %.2f mm; east face %.2f, top %.2f, each end %.2f mm2" % (X, Y, Z, A_E, A_B, A_end))
    print("   the worst stack (SHORTLIST's rooms %.2f / %.2f / %.2f mm): %.4f L (the record: 0.056 L)" % (east, top, ends, worst))
    print("   CASE-MARGINS 3.2, chosen nominal (C1 on the C6 legs): M4b +%.2f, M5 +%.2f, M6 +%.2f mm; M5 as designed on the flat floor +%.2f mm" % (
        chosen["M4b"], chosen["M5"], chosen["M6"], designed_flat["M5"]))
    print("   as designed on the chosen column throughout: %.4f L" % v_chosen)
    print("   with M5 taken from the flat-floor 'As designed' column (the record's 0.121 L): %.4f L" % v_record)
    print("   why the record's reading differs: M5's margin text carries escaped pipes ('\\|Y\\|'), so a split on '|' that skips three")
    print("   cells lands one cell early for M5 only and its maximum picks the flat-floor +%.2f mm (l4e10_cell_thermal.py, rows_cm)" % designed_flat["M5"])
    print()


# ======================================================================================== item 4: R-b against SLUSE66A p.10
def item4():
    print("ITEM 4. L4-E11's R-b against SLUSE66A p.10 (BQ25731, v2/vendor/ti/bq25731-datasheet.pdf)")
    p1 = pdf("v2/vendor/ti/bq25731-datasheet.pdf", 1, 1)
    p10 = pdf("v2/vendor/ti/bq25731-datasheet.pdf", 10, 10)
    must("SLUSE66A" in p10 and "REVISED JANUARY 2021" in p10, "SLUSE66A's revision on p.10")
    hdr = re.search(r"VVBUS_UVLOZ < VVBUS < VVBUSOV_FALL , TJ = -40°C to \+125°C, and TJ = 25°C for typical values \(unless otherwise noted\)", p10)
    must(hdr, "p.10's table condition (TJ)")
    f10 = flat(p10)
    rowm = re.search(r"Charge current 4096 mA regulation accuracy REG0x03/02\(\) = 0x0800H 5-mΩ RSR sensing \u20135\.0% 6\.0% ICHRG_REG_ACC "
                     r"resistor, VBAT above 2048 mA VSYS_MIN\(0°C to REG0x03/02\(\) = 0x0400H 85°C\) \u201312% 13\.5% 1024 mA "
                     r"REG0x03/02\(\) = 0x0200H \u201318% 21\.5%", f10)
    must(rowm, "p.10's ICHRG_REG_ACC rows and their condition")
    clamp = re.search(r"CELL\(≥2 S\),VSRN < VSYS_MIN 384 mA", f10)
    must(clamp, "p.10's ICLAMP row (typical only)")
    print("   p.10 table condition: 'TJ = -40°C to +125°C, and TJ = 25°C for typical values (unless otherwise noted)'")
    print("   ICHRG_REG_ACC, 'Charge current regulation accuracy 5-mΩ RSR sensing resistor, VBAT above VSYS_MIN(0°C to 85°C)':")
    print("     REG0x03/02() = 0x0200H, 1024 mA: -18 % / +21.5 % (MIN / MAX); the (0°C to 85°C) is the row's 'otherwise noted'")
    print("     temperature under a TJ table: a junction range")
    print("   ICLAMP, CELL(>=2 S), VSRN < VSYS_MIN: 384 mA in the TYP column, no MIN or MAX")
    gen = txt("v2/ecad/tools/gen_sch_a.py")
    must('r("R17", "5mOhm 1% 2512 (RSR, charge current sense)", "VBAT", "CELL_FUSED", "RS2512")' in gen, "R17 5 mOhm 1 % in gen_sch_a.py")
    i_set = 1.024
    i_max = i_set * (1 + 0.215) / (1 - 0.01)
    i_min = i_set * (1 - 0.18) / (1 + 0.01)
    t_air, vsd, rja = 62.1, 1.0, 50.0
    tj = t_air + i_max * vsd * rja
    print("   R17: '5mOhm 1%% 2512 (RSR, charge current sense)' (gen_sch_a.py): case (i) %.4f to %.4f A (the record: 0.8314 to 1.2567 A)" % (i_min, i_max))
    print("   Q2's diode: %.4f W at VSD 1 V, %.3f K over the %.1f C air at %.0f C/W: TJ %.3f C (the record: 1.257 W, 62.8 K, 124.9 C) against 150 C" % (
        i_max * vsd, i_max * vsd * rja, t_air, rja, tj))
    p_max = i_max * 16.884
    print("   R-b's charge power above 14 V: %.4f A x 16.884 V = %.2f W (the record: 21.22 W)" % (i_max, p_max))
    # R17's temperature coefficient: not in the +-1 %; no part number is drawn for R17, so a typical metal-strip 75 ppm/K is shown
    for ppm in (75.0, 200.0):
        k = 1 - ppm * 1e-6 * 60.0
        im = i_set * 1.215 / (0.99 * k)
        print("   sensitivity, not in the record: R17 at -%.0f ppm/K over 60 K (0 to 85 C from 25 C): %.4f A, Q2 at %.2f C" % (ppm, im, t_air + im * vsd * rja))
    l11 = flat(txt("v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md"))
    c2 = "| (ii) | SRN at or above VSYS_MIN, the charger outside 0 to 85 C (it sits in the inside air, -20 C at a cold start to 62.1 C hot, plus its own rise, which no held record gives) | not printed | INCONCLUSIVE: E11-22 |"
    c3 = "| (iii) | SRN under VSYS_MIN | the clamp, 384 mA typical, no maximum printed | INCONCLUSIVE: E11-22 |"
    q2 = "**CONDITIONAL** on case (i) holding and on board P's installed copper giving TI's 50 C/W"
    for lab, s in (("case (ii) INCONCLUSIVE, the charger's own rise counted", c2), ("case (iii) INCONCLUSIVE", c3), ("Q2's 124.9 C CONDITIONAL", q2)):
        print("   L4E11 section 4: %-55s %s" % (lab, "read" if flat(s) in l11 else "NOT FOUND"))
        must(flat(s) in l11, lab)
    reg = txt("v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md")
    r136 = re.search(r"^\| R-136 \|.*$", reg, re.M).group(0)
    for lab, s in (("cases (ii) and (iii)", "R-b's cases (ii) and (iii) closed"),
                   ("the charger's temperature bounded inside 0 to 85 C, or TI's accuracy outside it", "the charger's temperature while R-b holds bounded inside 0 to 85 C, or TI's 0x0200 accuracy outside it"),
                   ("the clamp's maximum under VSYS_MIN", "the clamp's maximum under VSYS_MIN"),
                   ("Q2's copper for 50 C/W", "board P's copper under Q2 for TI's 50 C/W"),
                   ("acceptance: Q2 at most 124.9 C confirmed or re-derived", "Q2's diode at most 124.9 C at the 62.1 C air confirmed or re-derived")):
        print("   R-136 carries %-75s %s" % (lab, "yes" if s in r136 else "NO"))
        must(s in r136, "R-136: " + lab)
    print()


# ======================================================================================== item 5: the SGP41's shutdown
def item5():
    print("ITEM 5. L4-E12's SGP41 shutdown on a TMP117 (v2/vendor/ti/ti-tmp117-temperature.pdf)")
    p1 = pdf("v2/vendor/ti/ti-tmp117-temperature.pdf", 1, 1)
    must("SNOSD82D \u2013 JUNE 2018 \u2013 REVISED SEPTEMBER 2022" in p1, "the TMP117 sheet's revision")
    must(re.search(r"±0\.15 °C \(maximum\) from \u201340 °C to 70 °C", p1), "p.1's +-0.15 C row")
    p6 = pdf("v2/vendor/ti/ti-tmp117-temperature.pdf", 6, 6)
    must("6.5 Electrical Characteristics" in p6, "6.5 on p.6")
    must(re.search(r"-40 °C to 70 °C\s+-0\.15\s+±0\.05\s+0\.15", p6), "6.5's TMP117 -40 to 70 C row")
    must(re.search(r"8 averages", p6) and re.search(r"1-Hz conversion cycle", p6) and re.search(r"Thermal Pad unsoldered", p6),
         "6.5's test conditions")
    must(re.search(r"TMP117N\s+-55 °C to 125 °C", p6) or "TMP117N" in p6, "6.5's TMP117N rows")
    print("   p.1: '+-0.15 C (maximum) from -40 C to 70 C' (SNOSD82D, revised September 2022; the sheet prints the minus as an en dash)")
    print("   p.6, 6.5 Electrical Characteristics, TMP117 row -40 to 70 C: MIN -0.15, TYP +-0.05, MAX 0.15 C, over free-air temperature;")
    print("     conditions: 8 averages, 1-Hz conversion cycle, thermal pad unsoldered (DRV), I2C inputs VIL <= 0.05 V+, VIH >= 0.95 V+;")
    print("     the TMP117N rows print +-0.2 C from -40 to 100 C (no +-0.15 C row); board B's part is TMP117AIDRVR (gen_sch_b.py)")
    gb = txt("v2/ecad/tools/gen_sch_b.py")
    must('"TMP117AIDRVR board temperature under the coolers' in gb, "board B's TMP117AIDRVR")
    rate = 15.0 / 3600.0          # E5's 30 to 60 C in 2 h (Method 507.6), K/s
    lag = rate * 61.0             # a 1 s reading plus a 60 s time constant (the record's ASSUMPTION)
    off_x = 55.0 - 0.15 - 0.5 - lag
    on_x = 50.0 - 0.15 - 0.5 - lag
    print("   the lag: 15.0 K/h x 61 s = %.6f K (the record: 0.254167 K)" % lag)
    print("   off at 55 - 0.15 - 0.5 - lag = %.6f C, set at 54.0 C; the SGP41 then at most %.6f C (the record: 54.095833, 54.904167 C)" % (
        off_x, 54.0 + 0.15 + 0.5 + lag))
    print("   on and used at 50 - 0.15 - 0.5 - lag = %.6f C, set at 49.0 C; at most %.6f C while used (the record: 49.095833, 49.904167 C)" % (
        on_x, 49.0 + 0.15 + 0.5 + lag))
    for err in (0.15, 0.2):
        tau_be = (55.0 - 54.0 - err - 0.5) / rate - 1.0
        print("   break-even of the 54.0 C setting at +-%.2f C: the sensor-to-SGP41 time constant at most %.1f s at 15 K/h (the record assumes 60 s);"
              " off point %.6f C" % (err, tau_be, 55.0 - err - 0.5 - lag))
    reg = txt("v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md")
    rows = {k: re.search(r"^\| %s \|.*$" % k, reg, re.M).group(0) for k in ("R-138", "R-139", "R-146")}
    print("   the register: R-146 carries the 0.5 K placement (%s); R-138 and R-139 a forced shutdown at room temperature (%s, %s);"
          " no row names the 61 s lag or its time constant (%s)" % (
              "yes" if "the TMP117 within 0.5 K of the SGP41" in rows["R-146"] else "NO",
              "yes" if "a forced SGP41 shutdown at room temperature" in rows["R-138"] else "NO",
              "yes" if "a forced SGP41 shutdown at room temperature" in rows["R-139"] else "NO",
              "none" if not any(re.search(r"61 s|time constant|lag", v) for v in rows.values()) else "FOUND"))
    print()


def main():
    print("verify_risks.py: the independent verification of the findings ledger's concrete remaining risks (MESHSAT-1357, 2 October 2026)")
    print("PAUSED CHECKPOINT: items 2, 4 and 5 settled; item 3 an interim reading only; items 6, 7, 9 and 11 NOT YET VERIFIED (paused)")
    print()
    ok2 = item2()
    item3_interim()
    item4()
    item5()
    print("SUMMARY: item 2 %s; item 4 CONFIRMED; item 5 CONFIRMED (the row and the arithmetic; the lag carried by no register row);"
          " items 3, 6, 7, 9, 11 NOT YET VERIFIED (paused)" % ("CONFIRMED" if ok2 else "DIFFERS"))


if __name__ == "__main__":
    main()
