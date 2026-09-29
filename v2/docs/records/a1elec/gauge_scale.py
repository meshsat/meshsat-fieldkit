#!/usr/bin/env python3
"""gauge_scale.py: the lid pack's BQ4050 data-flash words under a current-scale calibration (stream a1elec, MESHSAT-1357).

PROTOTYPE DESIGN, AI arithmetic: no gauge is programmed and no pack is built.

The problem (outside review, point 2). A 4S12P pack of the ruled Samsung INR18650-35E holds 12 x 3.35 Ah = 40,200 mAh
and 40.2 Ah x 14.4 V = 578.88 Wh = 57,888 cWh at the specification minimum; TI's BQ4050 technical reference manual,
SLUUAQ3A, types Design Capacity mAh and Design Capacity cWh as I2 with a maximum of 32,767 (14.13.5.1 and 14.13.5.2,
page 180; Table 14-1 rows 0x444d and 0x444f, page 191). SpecificationInfo()'s IPScale is described as "Not supported by
the gas gauge / MUST be set to 0, 0, 0, 0" in 13.27 (page 107) and as a working 10E0 to 10E3 scale in 14.14.1.5 (page
184): the flag is not a resolution.

The approach this script tabulates. The gauge's internal current unit is whatever its current calibration makes it:
SLUUBF9 3.3.3 (the BQ4050EVM guide) calibrates current by applying a known current and entering its value in mA; the
firmware then computes CC Gain and Capacity Gain (SLUUAQ3A Table 14-1 rows 0x4006 and 0x400a, page 185). Entering HALF
the applied current (k = 2) makes every current the firmware measures, integrates or compares read half the true
value: one internal "mA" is 2 mA and one internal "mAh" 2 mAh, and energy and power words follow. TI documents exactly
this for a sibling gauge, the BQ34Z100-G1 (SLUSBZ5D 7.3.1.6 and 7.3.1.8, pages 15 and 16: "the units have been scaled
through the calibration process. The actual scale is not set in the device"). It changes no firmware behaviour, so
EVERY data-flash word whose unit is a current, a charge, an energy or a power must be written in the internal unit,
or it acts at twice its intended value. This script PARSES Table 14-1 from the pinned manual (pdftotext's layout text),
finds every such word, requires a stated true value for each (it refuses, exit 5, if a word has none), writes the
internal value, and checks it against the row's minimum and maximum. Words in mV, degrees C, s or hex are not scaled,
and the AFE's hardware thresholds (AOLD, ASCC, ASCD) are voltages across the real shunt, set on R10's true 2 mOhm.

Run from the repository root (needs pdftotext from poppler-utils and python3):
  python3 v2/docs/records/a1elec/gauge_scale.py > v2/docs/records/a1elec/gauge_scale.out
Exit 3: the manual is missing or changed; exit 5: a scaled word without a stated true value; exit 6: a written value
outside its row's range."""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TRM = os.path.join(ROOT, "v2", "vendor", "battery", "ti-sluuaq3a-bq4050-trm.pdf")
TRM_SHA256 = "525d16b2bdee44e5b587ccf6800b9967bc524772d0b5a20937957ea2e738b7ad"   # the value PRIMARY-CONFIGURATION.md names
K = 2
SCALED_UNITS = {"mA", "mAh", "cWh", "cW", "mW", "mWh", "3 \u00b5A"}   # "3 uA" is a current in steps of 3 uA (CEDV Electronics Load)
MINUS = "–"        # the manual's minus sign in its text layer

# THE LID PACK'S TRUE VALUES, per Table 14-1 address. kind: P protection threshold; A absolute signal level (TI's
# default kept as the true value); S the pack's size; C the charge algorithm; R a record (read, never written by the
# image; the host multiplies it by k); I inert while its feature is off. base: the base pack's golden image where
# PRIMARY-CONFIGURATION.md states it. Every true value is a design requirement, NOT_YET_TESTED, authority SESSION.
TRUE = {
    "0x43c6": (4, "A", None, "deadband: TI's 3 mA rounded UP to the next internal step (4 mA true), the side that ignores noise"),
    "0x440d": (300, "I", None, "BTP init discharge set: BTP is not used by the kit (no pin to the host); TI's 150 mAh x 2 kept in proportion"),
    "0x440f": (350, "I", None, "BTP init charge set: as above"),
    "0x4497": (10000, "P", 5000, "OCC1: the lid's U3B ChargeCurrent 8.0 A plus 25 percent; 0.83 A a cell against the 35E's 2.0 A maximum (spec 3.7); delay 2 s as the base"),
    "0x449a": (12000, "P", None, "OCC2: 1.0 A a cell, under the cell's 2.0 A; TI's delay kept"),
    "0x449d": (-200, "A", None, "OCC recovery: TI's -200 mA as the true value"),
    "0x44a0": (-20000, "P", -20000, "OCD1: board PL's path is board P's (F1 25 A, Q1 and Q2 CSD17570Q5B, R10 2 mOhm), so the base's -20 A, 2 s; the cells would allow 12 x 8 A"),
    "0x44a3": (-24000, "P", -24000, "OCD2: as the base, -24 A, 1 s (TBD by the reviewer there as here)"),
    "0x44a6": (200, "A", None, "OCD recovery: TI's 200 mA as the true value"),
    "0x44cf": (2000, "A", None, "PTO charge threshold: TI's default as the true value (the precharge timeout's current)"),
    "0x44d1": (1800, "A", None, "PTO suspend threshold: TI's default as the true value"),
    "0x44d5": (2, "A", None, "PTO reset: TI's 2 mAh; written 1 (2 mAh true)"),
    "0x44d7": (8000, "C", None, "CTO charge threshold: the lid's charge current, so the charge timeout counts the lid's fast charge"),
    "0x44d9": (6000, "C", None, "CTO suspend threshold: 75 percent of the charge current"),
    "0x44dd": (2, "A", None, "CTO reset: TI's 2 mAh; written 1"),
    "0x44df": (3000, "S", None, "OC (over-charge) threshold: TI's 300 mAh on its 4400 mAh default is 6.8 percent; 3000 mAh is 7.5 percent of 40,200"),
    "0x44e1": (2, "A", None, "OC recovery: TI's 2 mAh; written 1"),
    "0x44e9": (1000, "P", None, "CHGC (charge above the requested current): 1.0 A true, 12.5 percent of the 8.0 A request"),
    "0x44ec": (200, "A", None, "CHGC recovery: TI's 100 mA doubled with the threshold"),
    "0x44ef": (500, "P", None, "PCHGC (precharge above request): 500 mA true, 12 percent of the 4.2 A precharge"),
    "0x44f2": (20, "A", None, "PCHGC recovery: TI's 10 mA as true, written 10 (20 mA true), the next step up"),
    "0x44ff": (16000, "I", None, "SOCC (permanent fail): 1.33 A a cell; inert while Enabled PF A[SOCC] = 0 (the base's image, until Q-P3)"),
    "0x4502": (-30000, "I", None, "SOCD (permanent fail): above OCD2; inert while Enabled PF A[SOCD] = 0 (until Q-P3)"),
    "0x4514": (10, "A", None, "VIMR check current: TI's 10 mA as true (acts only if PF B is enabled, Q-P3)"),
    "0x451d": (50, "A", None, "VIMA check current: TI's 50 mA as true (as above)"),
    "0x4522": (10, "A", None, "CFET OFF threshold: 10 mA true, the next step above TI's 5 mA, so a leaking twelve-string pack is not a false FET fail"),
    "0x4525": (-10, "A", None, "DFET OFF threshold: as CFET"),
    "0x4528": (10, "A", None, "FUSE threshold: 10 mA true, as CFET"),
    "0x453e": (4000, "C", None, "low temperature range (T1 to T2, 1 to 12 C) charge current, low voltage band: 0.33 A a cell"),
    "0x4540": (4000, "C", None, "low temperature range, medium band"),
    "0x4542": (4000, "C", None, "low temperature range, high band"),
    "0x4546": (8000, "C", None, "standard temperature range charge current, low band: the U3B setting, 0.67 A a cell"),
    "0x4548": (8000, "C", None, "standard temperature range, medium band"),
    "0x454a": (8000, "C", None, "standard temperature range, high band"),
    "0x454e": (4000, "C", None, "high temperature range (T3 to T4, 42 to 43 C), low band"),
    "0x4550": (4000, "C", None, "high temperature range, medium band"),
    "0x4552": (4000, "C", None, "high temperature range, high band"),
    "0x4556": (8000, "C", None, "recommended temperature range (T2 to T5 region per 4.2), low band"),
    "0x4558": (8000, "C", None, "recommended temperature range, medium band"),
    "0x455a": (8000, "C", None, "recommended temperature range, high band"),
    "0x455c": (4200, "C", None, "pre-charging current: 0.1C of 12 x 3.45 Ah = 4.14 A, rounded up to 4.2 A (the base's 1.0 A is 0.1C of 3P)"),
    "0x455e": (0, "C", None, "maintenance charging current: 0, no maintenance charge after termination (4.10); the host decides a recharge"),
    "0x456c": (800, "C", None, "charge term taper current: 0.02C of 40.2 Ah (TI's 250 mA is 0.057C of its 4400 mAh default); PROVISIONAL until the bench's termination test"),
    "0x4575": (8000, "I", None, "CCC current threshold: inert while Configuration[CCC] = 0 (4.x, the base's image does not enable it)"),
    "0x4586": (100, "A", None, "Dsg Current Threshold: TI's 100 mA as true"),
    "0x4588": (50, "A", None, "Chg Current Threshold: TI's 50 mA as true"),
    "0x458a": (10, "A", None, "Quit Current: TI's 10 mA as true"),
    "0x444d": (40200, "S", 20100, "Design Capacity mAh: 12 x 3,350 mAh at the specification minimum (the base's 4S6P writes 20,100 unscaled)"),
    "0x444f": (57888, "S", 28944, "Design Capacity cWh: 40.2 Ah x 14.40 V (Design Voltage 14400 mV, unscaled)"),
    "0x4100": (40200, "S", None, "Learned Full Charge Capacity, initial: the design capacity"),
    "0x4602": (10000, "C", None, "CEDV OverLoad Current: 10 A true (TI's 5000 mA on a 4.4 Ah default); the CEDV profile itself is fitted on logs taken under the scaled calibration, so its coefficients are in the internal unit by construction"),
    "0x4609": (1800, "S", None, "CEDV Near Full: TI's 200 mAh is 4.5 percent of 4400; 4.5 percent of 40,200"),
    "0x460b": (0, "S", None, "CEDV Reserve Capacity: 0, the kit's 5 percent reserve is the host's RSOC line (CONOPS 4c)"),
    "0x4607": (0, "A", None, "CEDV Electronics Load (steps of 3 uA): TI's 0 kept; if the bench measures board PL's unsensed draw it is entered at half its true steps"),
    "0x4475": (16000, "A", None, "Max Smoothing Current (U2): TI's 8000 mA doubled so that smoothing acts over the same share of the lid's range"),
    "0x441d": (10, "A", None, "Sleep Current: TI's 10 mA as true"),
    "0x4267": (0, "R", None, "PF Status Current: a record; the host multiplies it by k"),
    "0x4443": (4020, "S", None, "Remaining AH Capacity Alarm: 10 percent of design"),
    "0x4445": (5789, "S", None, "Remaining WH Capacity Alarm: 10 percent of design"),
    "0x4192": (0, "R", None, "Lifetimes Max Charge Current: a record; host x k"),
    "0x4194": (0, "R", None, "Lifetimes Max Discharge Current: a record; host x k"),
    "0x4196": (0, "R", None, "Lifetimes Max Avg Dsg Current: a record; host x k"),
    "0x4198": (0, "R", None, "Lifetimes Max Avg Dsg Power: a record; host x k"),
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def num(tok):
    tok = tok.replace(MINUS, "-")
    try:
        return float(tok) if "." in tok else int(tok)
    except ValueError:
        return None


def parse_table(text):
    """Rows of Table 14-1: (address, type, name, min, max, default, unit, context, pdf page)."""
    lines = text.split("\n")
    rows, page, in_table = [], 1, False
    for i, line in enumerate(lines):
        page += line.count("\f")
        if "Table 14-1. Data Flash Summary" in line:
            in_table = True
        if not in_table:
            continue
        toks = line.split()
        addr_i = [j for j, t in enumerate(toks) if t.startswith("0x4") and len(t) == 6]
        if not addr_i or len(toks) < addr_i[0] + 6:
            continue
        a = addr_i[0]
        if toks[-1] in ("\u00b5A", "nV") and num(toks[-2]) is not None and num(toks[-5]) is not None:
            # a unit printed as a step size, "3 \u00b5A" or "116 nV": one more token on the right
            toks = toks[:-2] + [toks[-2] + " " + toks[-1]]
        unit, dflt, mx, mn = toks[-1], toks[-2], toks[-3], toks[-4]
        if num(mn) is None or num(mx) is None:
            continue
        name = " ".join(toks[a + 2:-4])
        ctx = " ".join(toks[:a])
        for k in (i - 1, i + 1):
            if 0 <= k < len(lines) and "0x4" not in lines[k] and lines[k].strip() and "Table" not in lines[k]:
                ctx = (ctx + " | " + " ".join(lines[k].split())).strip(" |")
        rows.append((toks[a].lower(), toks[a + 1], name, num(mn), num(mx), num(dflt), unit, ctx, page))
    return rows


def written(true_v):
    """The internal value for a true value at k: exact when even, else rounded away from zero (the next internal
    step up in magnitude), which the TRUE table's reasons state where it matters."""
    q = abs(true_v) / K
    w = int(q) if q == int(q) else int(q) + 1
    return w if true_v >= 0 else -w


def main():
    if not os.path.exists(TRM) or sha(TRM) != TRM_SHA256:
        sys.stderr.write("gauge_scale: the BQ4050 TRM is missing or changed; refusing\n")
        return 3
    text = subprocess.run(["pdftotext", "-layout", TRM, "-"], check=True, capture_output=True).stdout.decode("utf-8", "replace")
    rows = parse_table(text)
    o = []
    P = o.append
    P("THE LID PACK'S BQ4050 WORDS UNDER A CURRENT-SCALE CALIBRATION OF k = %d (gauge_scale.py, stream a1elec, MESHSAT-1357)" % K)
    P("PROTOTYPE DESIGN; AI arithmetic; every true value a design requirement, NOT_YET_TESTED. Source: TI SLUUAQ3A (sha256 %s...)," % TRM_SHA256[:16])
    P("Table 14-1 as its text layer prints it; the page is the PDF page, which is the manual's printed page number.")
    P("")
    scaled = [r for r in rows if r[6] in SCALED_UNITS]
    P("1. WHY k: the two design-capacity rows and the pack")
    for r in rows:
        if r[0] in ("0x444d", "0x444f"):
            tv = TRUE[r[0]][0]
            P("   %s %-24s max %6d %-4s: the pack's %6d %s is %s its maximum; at k = %d it is written %6d (%.1f percent of the maximum)" % (
                r[0], r[2], r[4], r[6], tv, r[6], "ABOVE" if tv > r[4] else "within", K, written(tv), 100.0 * written(tv) / r[4]))
    P("   With the specification's typical 3.45 Ah a cell the pack is 41,400 mAh and 59,616 cWh: written 20,700 and 29,808 at k = 2.")
    P("   k = 2 is the smallest integer that fits both; the internal current range of an I2 word (-32,768 to 32,767) then spans")
    P("   -65.5 to +65.5 A true, above the pack path's 25 A blade, so no current the path can carry is clipped.")
    P("")
    P("2. THE CALIBRATION WORDS (written by the gauge's own current calibration, not by hand)")
    for r in rows:
        if r[0] in ("0x4006", "0x400a"):
            P("   %s %-16s type %s, range %s to %s, TI default %s (page %d)" % (r[0], r[2], r[1], r[3], r[4], r[5], r[8]))
    P("   Procedure (SLUUBF9 3.3.3, TI's EVM guide): apply a known current, enter its value in Applied Current. For k = 2 the")
    P("   value entered is half the applied true current (apply -4000 mA through the pack path, enter -2000). The firmware")
    P("   then computes both gains so that its unit is 2 mA; their ratio stays TI's (1069035.256 / 3.58422 = %.1f)." % (1069035.256 / 3.58422))
    P("   The manual does not state how CC Gain relates to the sense resistance, so its value after calibration is READ BACK")
    P("   at commissioning and must lie inside the row's range; that read-back is a bench item, not shown here.")
    P("")
    P("3. EVERY WORD IN A CURRENT, CHARGE, ENERGY OR POWER UNIT (%d rows parsed from Table 14-1)" % len(scaled))
    P("   %-7s %-4s %-30s %-5s %8s %8s %8s %8s %8s %-4s  %s" % ("address", "type", "name", "unit", "min", "max", "TI dflt", "true", "WRITTEN", "kind", "context and why"))
    missing, bad = [], []
    for r in scaled:
        if r[0] not in TRUE:
            missing.append(r)
            continue
        tv, kind, base, why = TRUE[r[0]]
        w = written(tv)
        if not (r[3] <= w <= r[4]):
            bad.append((r, w))
        P("   %-7s %-4s %-30s %-5s %8s %8s %8s %8d %8d %-4s  [%s, p.%d] %s%s" % (
            r[0], r[1], r[2][:30], r[6], r[3], r[4], r[5], tv, w, kind, r[7][:60], r[8], why,
            (" (base 4S6P image: %d)" % base) if base is not None else ""))
    extra = sorted(set(TRUE) - set(r[0] for r in scaled))
    P("")
    if missing:
        for r in missing:
            P("   NO TRUE VALUE STATED: %s %s %s" % (r[0], r[2], r[6]))
        sys.stdout.write("\n".join(o) + "\n")
        sys.stderr.write("gauge_scale: %d scaled word(s) without a stated true value; refusing\n" % len(missing))
        return 5
    if bad:
        for r, w in bad:
            P("   OUT OF RANGE: %s %s written %d against %s to %s" % (r[0], r[2], w, r[3], r[4]))
        sys.stdout.write("\n".join(o) + "\n")
        return 6
    P("   every scaled word has a stated true value and its written value lies inside its row's range; addresses in the")
    P("   true-value table that Table 14-1 does not list with a scaled unit: %s" % (", ".join(extra) if extra else "none"))
    P("")
    units = {}
    for r in rows:
        units[r[6]] = units.get(r[6], 0) + 1
    P("4. NOT SCALED (the other %d rows by unit): %s" % (len(rows) - len(scaled), ", ".join("%s %d" % (u, n) for u, n in sorted(units.items()) if u not in SCALED_UNITS)))
    P("   Voltages (COV, CUV, the charge voltages, Design Voltage 14400 mV), temperatures, times and bit fields are written as")
    P("   the base's image writes them. The AFE words (AOLD, ASCC, ASCD thresholds in AFE Protection Control and their codes)")
    P("   are voltages across the real shunt: set on R10's true 2 mOhm, as board P's, because board PL's path limits are board P's.")
    P("")
    P("5. WHAT THE HOST MUST SCALE (k = %d): every SBS or MAC value in mA, mAh, 10 mWh or cW: Current(), AverageCurrent()," % K)
    P("   RemainingCapacity(), FullChargeCapacity(), DesignCapacity(), ChargingCurrent(), MaxError is a percent (not scaled),")
    P("   RunTimeToEmpty and the other times are computed by the gauge from its own consistent units (not scaled), the")
    P("   Lifetimes and PF Status current records, and any value it writes (none in the kit's contract). ChargingCurrent()")
    P("   is multiplied by k BEFORE the host writes U3B's ChargeCurrent (FW-A02's lid row, CHARGER.md). Voltages, cell voltages,")
    P("   temperatures, RSOC and flags are not scaled. The marker: Manufacturer Info Block A (0x4041 onward, page 194) carries")
    P("   the ASCII text 'IPSCALE2' and the host refuses the lid gauge's currents and capacities until it has read it.")
    P("")
    P("END.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
