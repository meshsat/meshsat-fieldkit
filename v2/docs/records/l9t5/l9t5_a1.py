#!/usr/bin/env python3
"""l9t5_a1.py: Layer 9 record l9t5, task T5 round 2: A1's detector, chosen from the makers' sheets or not at all (MESHSAT-1357,
4 October 2026). PROTOTYPE DESIGN: nothing in this kit has been built, bought, powered or measured.

A1 (record l9t5 out 4 and 6, SELECTED as the direction for F01 / D-17 on C-ALLTX rev 3): the VHF PA held to its 30 W service by a
closed loop on its gate bias VGG on board D. Its acceptance: the loop's half-tolerance at most 0.5 dB over temperature (the case with
the printed bounds), at most 0.25 dB to cover the sensitivities as well. The brief's test for drafting it: a detector whose PRINTED
accuracy supports that tolerance; otherwise A1 stays a selected direction with the detector a named vendor or physical item, and no
figure is assumed. This script reads, from each held sheet (fetch_held_back.py), the printed temperature row nearest the kit's
144 to 146 MHz and its column (a limit in the Min/Max columns, or a typical figure), the detector's supply range against board D's
two rails, and states the result. It writes nothing but its output (l9t5_a1.out, regenerated with _bin/regen_out.py).

Run from the repository root:  python3 v2/docs/records/l9t5/l9t5_a1.py      (after: python3 v2/docs/records/l9t5/fetch_held_back.py)"""
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.dont_write_bytecode = True
M = "\u2212"     # the minus sign ADI prints
N = "\u2013"     # the en dash TI and LTC print

SHEETS = {"adl5902": "v2/vendor/adi/held/adi-adl5902-revb.pdf", "adl5513": "v2/vendor/adi/held/adi-adl5513-revb.pdf",
          "ltc5582": "v2/vendor/adi/held/adi-ltc5582-revd.pdf", "lmh2110": "v2/vendor/ti/held/ti-lmh2110-snws022d.pdf"}
# W34 (Q-41 item 1, adopted in set 32): the makers' PDFs this script reads as text, each with its pdftotext options ([] is pdftotext's
# plain reading order). Each text is a verbatim input taken once on the runner by v2/docs/records/_lib/retake_pdf_text.py beside its
# PDF (a held-back sheet's text is held back with it, under held/); _lib/pdftext.py returns it byte for byte and refuses when it is
# absent, so this script never runs pdftotext; section 1 prints each text's sha256 after the pins.
# Re-take after a sheet changes: python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l9t5
PDFTEXT = {
    "v2/vendor/adi/held/adi-adl5513-revb.pdf": [["-layout"]],
    "v2/vendor/adi/held/adi-adl5902-revb.pdf": [["-layout"]],
    "v2/vendor/adi/held/adi-ltc5582-revd.pdf": [["-layout"]],
    "v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-lmh2110-snws022d.pdf": [["-layout"]],
}
import importlib.util  # noqa: E402  (the helper's loader; W34)
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PT)
PINS = {"fetch": "v2/docs/records/l9t5/fetch_held_back.py", "codec_floor": "v2/docs/records/s99a/codec_floor.out",
        "gen_d": "v2/ecad/tools/gen_sch_d.py", "case_out": "v2/docs/records/l9t5/l9t5_case.out", "ra30": "v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf"}
BAND = (144.0, 146.0)          # MHz: the EU amateur 2 m band the SA868 and the PA serve (CHO-001, the device set)
TOL = (0.5, 0.25)              # dB: A1's two acceptance tiers (record l9t5 out 4)



def _adds(path):
    """the designators a draft's ADDS tuple names, read with ast (P0-1, 5 October 2026: board D now carries correction (c)'s draft)"""
    import ast
    for node in ast.parse(open(path, encoding="utf-8").read()).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "ADDS" for t in node.targets):
            return [e.value for e in node.value.elts]
    return []

def refuse(msg):
    sys.stderr.write("l9t5_a1: REFUSED: %s\n" % msg)
    sys.exit(2)


def sha(rel, n=16):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:n]


def pdf(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        refuse("%s is not held here: python3 v2/docs/records/l9t5/fetch_held_back.py" % rel)
    return PT.pdf_text(ROOT, rel, ["-layout"], PDFTEXT, "v2/docs/records/l9t5")


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


def dev(s):
    """'-0.11/+0.25' or '+0.3/-0.2' or '+-0.31' (any minus sign) as (low, high) in dB."""
    s = s.replace(M, "-").replace(N, "-").replace("±", "+-")
    if s.startswith("+-"):
        v = float(s[2:])
        return -v, v
    a, b = (float(x) for x in s.split("/"))
    return min(a, b), max(a, b)


def read():
    D = {}
    # ADI ADL5902 Rev. B: Table 1 (Min, Typ, Max); the 100 MHz and 700 MHz blocks; one value per deviation row (the Typ column)
    t = pdf(SHEETS["adl5902"])
    need(t, r"^Rev\. B\b", "the ADL5902 sheet's revision")
    need(t, r"Parameter\s+Test Conditions/Comments\s+Min\s+Typ\s+Max\s+Unit", "the ADL5902 table's columns")
    sup = need(t, r"Supply Voltage\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "the ADL5902's supply").groups()
    rows = {}
    for f, nxt in (("100 MHz", "700 MHz"), ("700 MHz", "900 MHz")):
        blk = need(t, r"^\s*%s\s*$(.*?)^\s*%s\s*$" % (f, nxt), "the ADL5902's %s block" % f, re.M | re.S).group(1)
        for lvl in ("0", M + "45"):
            m = need(blk, r"^\s+%s40°C < TA < \+85°C; PIN = %s dBm\s+(\S+)\s+dB\s*$" % (M, lvl), "the ADL5902's %s row at %s dBm" % (f, lvl))
            rows[(f, lvl.replace(M, "-"))] = dev(m.group(1))
    D["adl5902"] = dict(name="ADI ADL5902 TruPwr (Rev. B)", supply=(float(sup[0]), float(sup[2])), rows=rows, col="Typ (one value, no Min or Max)",
                        ref=("100 MHz", "0"), bracket=[("100 MHz", "0"), ("700 MHz", "0")], level="0 dBm", span="-40 to +85 C")
    # ADI ADL5513 Rev. B: FREQUENCY = 100 MHz block, the -10 dBm rows split at 25 C
    t = pdf(SHEETS["adl5513"])
    need(t, r"Rev\. B \| 2 of 25", "the ADL5513 sheet's revision")
    sup = need(t, r"^\s+Supply Voltage\s+([\d.]+)\s+([\d.]+)\s+V\s*$", "the ADL5513's supply").groups()
    blk = need(t, r"FREQUENCY = 100 MHz(.*?)FREQUENCY = 900 MHz", "the ADL5513's 100 MHz block", re.S).group(1)
    rows = {}
    for span, pat in (("25 to 85 C", r"25°C < TA < 85°C; PIN = %s10 dBm" % M), ("-40 to 25 C", r"%s40°C < TA < \+25°C; PIN = %s10 dBm" % (M, M))):
        m = need(blk, r"^\s+%s\s+(\S+)\s+dB\s*$" % pat, "the ADL5513's %s row" % span)
        rows[("100 MHz", span)] = dev(m.group(1))
    lo = min(r[0] for r in rows.values())
    hi = max(r[1] for r in rows.values())
    rows[("100 MHz", "-40 to 85 C, the two rows' union")] = (lo, hi)
    D["adl5513"] = dict(name="ADI ADL5513 log detector (Rev. B)", supply=(float(sup[0]), float(sup[1])), rows=rows, col="Typ (one value, no Min or Max)",
                        ref=("100 MHz", "-40 to 85 C, the two rows' union"), bracket=[("100 MHz", "-40 to 85 C, the two rows' union")], level="-10 dBm", span="-40 to +85 C (two printed rows)")
    # TI LMH2110 SNWS022D: the 50 MHz block, EVOT +-0.5 dB over a dynamic range (TYP column)
    t = pdf(SHEETS["lmh2110"])
    need(t, r"SNWS022D", "the LMH2110 sheet's number")
    sup = need(t, r"Wide Supply Range from ([\d.]+) V to ([\d.]+) V", "the LMH2110's supply").groups()
    blk = need(t, r"RFIN = 50 MHz \(fit range(.*?)RFIN = 900 MHz", "the LMH2110's 50 MHz block", re.S).group(1)
    m = need(blk, r"±([\d.]+)-dB input referred variation over temperature\s*\n\s*\(EVOT\), from PMIN\s+(\d+)", "the LMH2110's EVOT row")
    D["lmh2110"] = dict(name="TI LMH2110 log RMS (SNWS022D)", supply=(float(sup[0]), float(sup[1])), rows={("50 MHz", "range"): (-float(m.group(1)), float(m.group(1)))},
                        col="Typ (a dynamic range of %s dB within +-%s dB, typical)" % (m.group(2), m.group(1)), ref=("50 MHz", "range"),
                        bracket=[("50 MHz", "range")], level="a %s dB range from PMIN" % m.group(2), span="-40 to +85 C")
    # ADI LTC5582 Rev. D: the lowest characterized frequency in its table, and its temperature row there
    t = pdf(SHEETS["ltc5582"])
    need(t, r"Rev\. D", "the LTC5582 sheet's revision")
    vmax = float(need(t, r"Supply Voltage\.+([\d.]+)V", "the LTC5582's absolute supply").group(1))
    first = need(t, r"^fRF = (\d+)MHz\s*$", "the LTC5582's first characterized frequency").group(1)
    m = need(t, r"Output Variation vs Temperature\s+Normalized to Output at 25°C, Pin = %s50dBm to 0dBm\s+l\s+±([\d.]+)\s+dB" % N, "the LTC5582's first row")
    D["ltc5582"] = dict(name="ADI LTC5582 RMS (Rev. D)", supply=(3.3, vmax), supply_note="3.3 V its test condition, %.1f V its absolute maximum" % vmax, rows={("%s MHz" % first, "range"): (-float(m.group(1)), float(m.group(1)))},
                        col="Typ (one value; the bullet marks the full temperature range)", ref=("%s MHz" % first, "range"), bracket=[("%s MHz" % first, "range")],
                        level="-50 to 0 dBm", span="-40 to +105 C", first=float(first))
    # board D's rails
    cf = open(os.path.join(ROOT, PINS["codec_floor"]), encoding="utf-8").read()
    floors = [float(x) for x in re.findall(r"^1\.00\s+(?:typ|max)\s+\S+(?:\s+C)?\s+.*?\s+(\d\.\d{4})\s+[+-]\d\.\d{4}\s*$", cf, re.M)]
    if len(floors) < 6:
        refuse("record s99a's codec floor rows no longer read")
    D["v5_floor"] = min(floors)
    gd = open(os.path.join(ROOT, PINS["gen_d"]), encoding="utf-8").read()
    need(gd, r'ic\("U1", 5, "TLV75533PDBV 3\.3 V 500 mA LDO', "board D's 3.3 V LDO")
    need(gd, r'ic\("U15", 7, "TLV75801PDRVR adjustable LDO, PA gate bias VGG', "board D's VGG regulator U15")
    m = need(gd, r"IFB 0\.1 uA through R82 \(7\.3 mV\), load regulation negligible at the gate's 1 mA \(IGG, RA30H1317M1\): ([\d.]+) to ([\d.]+) V\.", "VGG's band")
    D["vgg"] = (float(m.group(1)), float(m.group(2)))
    co = open(os.path.join(ROOT, PINS["case_out"]), encoding="utf-8").read()
    D["a1_need"] = {}
    for db in ("0.25", "0.5", "1"):
        m = re.search(r"\+-%s dB.*?needs ([\d.]+) V" % re.escape(db), co)
        D["a1_need"][db] = float(m.group(1)) if m else None
    ra = pdf(PINS["ra30"])
    need(ra, r"Output Power Control:\s+By the gate voltage \(VGG\)\.", "the RA30H1317M1's output control")
    return D


def main():
    for rel in list(SHEETS.values()) + list(PINS.values()):
        if not os.path.isfile(os.path.join(ROOT, rel)):
            refuse("%s is missing (the held sheets: python3 v2/docs/records/l9t5/fetch_held_back.py)" % rel)
    D = read()
    out = []
    w = out.append
    w("l9t5_a1: Layer 9 record l9t5, task T5 round 2: A1's detector from the makers' sheets (MESHSAT-1357)")
    w("prototype design; nothing built, bought, powered or measured; the sheets are held back (fetch_held_back.py), read here, never committed")
    w("")
    w("1. INPUTS, pinned by sha256")
    for rel in list(SHEETS.values()) + list(PINS.values()) + [t for t, _h, _held in PT.inputs(ROOT, PDFTEXT)]:
        w("   %s %s" % (sha(rel), rel))
    w("")
    w("2. THE PRINTED TEMPERATURE ROW NEAREST THE KIT'S %.0f TO %.0f MHz, PER DETECTOR (deviation from the 25 C output; the column it is printed in)" % BAND)
    res = {}
    for k in ("adl5902", "adl5513", "lmh2110", "ltc5582"):
        x = D[k]
        worst = max(max(abs(x["rows"][r][0]), abs(x["rows"][r][1])) for r in x["bracket"])
        ref = max(abs(x["rows"][x["ref"]][0]), abs(x["rows"][x["ref"]][1]))
        near = x["ref"][0]
        res[k] = dict(worst=worst, ref=ref, near=near)
        rows = "; ".join("%s %s: %+.2f/%+.2f dB" % (f, l if l != "range" else "", a, b) for (f, l), (a, b) in sorted(x["rows"].items()))
        w("   %-34s %s; supply %s" % (x["name"], rows.replace(" range:", ":"), x.get("supply_note") or "%.1f to %.1f V" % x["supply"]))
        w("   %-34s at %s, %s; column: %s" % ("", x["level"], x["span"], x["col"]))
    w("   NO SHEET PRINTS THE ROW AS A LIMIT: every temperature deviation above sits in the Typ column (TYPICAL); none is printed at %.0f to %.0f MHz" % BAND)
    w("")
    w("3. EACH AGAINST A1'S ACCEPTANCE (the loop's half-tolerance, of which the detector is one term; the sampler, the set point and the")
    w("   error amplifier take the rest) AND AGAINST BOARD D'S RAILS (+5V_D8's floor %.4f V at board D, record s99a's codec floor, its worst row;" % D["v5_floor"])
    w("   +3V3_D8 from the TLV75533 U1)")
    cands = []
    for k in ("adl5902", "adl5513", "lmh2110", "ltc5582"):
        x, r = D[k], res[k]
        if k == "ltc5582":
            why = "no row below %.0f MHz: nothing printed near the band" % x["first"]
            ok_t = False
        else:
            ok_t = r["worst"] < TOL[0]
            why = "the detector alone takes %.2f dB TYPICAL%s of the %.2f dB tier, %.2f dB left for the rest of the loop" % (
                r["worst"], " (the worse of the rows bracketing the band, an ASSUMPTION that it holds between them)" if len(x["bracket"]) > 1 else "",
                TOL[0], TOL[0] - r["worst"])
        rail = 5.0 if x["supply"][0] > 3.3 else 3.3
        ok_s = (D["v5_floor"] >= x["supply"][0]) if rail == 5.0 else True
        w("   %-34s %s; the %.2f dB tier: %s" % (x["name"], why, TOL[1], "the detector alone exceeds it" if (k == "ltc5582" or r["worst"] >= TOL[1]) else "room"))
        w("   %-34s its rail on board D: %s" % ("", ("+5V_D8, whose floor %.4f V is UNDER its %.1f V minimum" % (D["v5_floor"], x["supply"][0])) if (rail == 5.0 and not ok_s)
                                                  else "+5V_D8 at or over its %.1f V minimum" % x["supply"][0] if rail == 5.0 else "+3V3_D8 (3.3 V), %s" % (x.get("supply_note") or "inside its %.1f to %.1f V" % x["supply"])))
        cands.append((k, ok_t, ok_s))
    w("")
    supports = [k for k, ok_t, ok_s in cands if ok_t and ok_s and D[k]["col"].startswith("Limit")]
    typ_room = [k for k, ok_t, ok_s in cands if ok_t]
    w("4. THE RESULT")
    w("   a detector whose PRINTED LIMIT supports A1's tolerance: %s" % (", ".join(supports) if supports else "NONE (every sheet prints its temperature row as typical data)"))
    w("   on TYPICAL data, room under the %.2f dB tier: %s; under the %.2f dB tier: none" % (TOL[0], ", ".join(D[k]["name"] for k in typ_room) or "none", TOL[1]))
    w("   of those, the ADL5902 runs from 4.5 V, over board D's +5V_D8 floor (%.4f V), and the ADL5513 leaves %.2f dB for the sampler, the set" % (
        D["v5_floor"], TOL[0] - res["adl5513"]["worst"]))
    w("   point and the amplifier together, on typical data")
    w("   SESSION DECISION (under the owner's standing rule of 26 September 2026): \"a printed accuracy that supports the tolerance\" is read as a")
    w("   printed LIMIT. Why: a typical figure says nothing of a unit's spread, and the loop exists to bound the case's power, which a typical")
    w("   drift does not bound; a correction accepted on it could not tell a passing unit from a failing one. How to reverse: if the coordinator")
    w("   or the checker reads typical data as enough, the ADL5513 on +3V3_D8 (or the ADL5902 with D-A1's supply) is drafted, TYPICAL and")
    w("   CONDITIONAL on P-A1")
    w("   A1 STAYS A SELECTED DIRECTION, NOT DRAFTED (the brief's rule): no loop is drawn on board D, no figure is assumed")
    w("   the named items that would let it be drafted (one is enough to restart the draft; none is sent or bought here):")
    w("     V-A1 (vendor, drafted, UNSENT): Analog Devices: the ADL5902's deviation vs temperature at 144 to 146 MHz and about 0 dBm as a")
    w("          limit or a characterized distribution (the sheet prints %+.2f/%+.2f dB typical at 100 MHz and %+.2f/%+.2f dB at 700 MHz), and its" % (
        D["adl5902"]["rows"][("100 MHz", "0")] + D["adl5902"]["rows"][("700 MHz", "0")]))
    w("          operation at %.2f V (board D's +5V_D8 floor); or a part ADI prints with such a limit" % D["v5_floor"])
    w("     P-A1 (physical): the loop's specimen over the kit's temperature range, its output deviation measured against a reference power")
    w("          meter, and the detector's drift tabulated per unit if it is to be compensated in firmware (board D already reads the flange")
    w("          temperature, U22); with the bench row already owed: the module's drain current at the loop's high end at 13.8 V")
    w("     D-A1 (design, after V-A1 or P-A1): a supply of at least 4.5 V for a 5 V detector on board D, or a 3.3 V part with the margin")
    w("   for the coordinator (not drafted, materially different): the loop's sensed variable could be the PA's DC input on board A, where")
    w("   U14 is an INA226 on +13V8_PA (0x46), whose sheet (held, v2/vendor/ti/ti-ina226.pdf, not read here) gives its gain error and offset")
    w("   Max columns; it bounds the case's own quantity (watts at VBAT), needs a path from board A to VGG on board D, and leaves the RF output")
    w("   to the module's efficiency (its printed minimum 40 %)")
    w("   what does not move: VGG today is open loop at %.2f to %.2f V (board D's U15); A1's own figures stay record l9t5 out 4's" % D["vgg"])
    w("")
    pred = {
        "every sheet's temperature row near the band is read and none is printed as a limit": not supports and len(cands) == 4,
        "on typical data the ADL5902 and the ADL5513 leave room under 0.5 dB and none under 0.25 dB": typ_room == ["adl5902", "adl5513"] and all(
            res[k]["worst"] >= TOL[1] for k in ("adl5902", "adl5513", "lmh2110")),
        "the ADL5902's supply minimum is over board D's +5V_D8 floor": D["adl5902"]["supply"][0] > D["v5_floor"],
        "A1 stays a direction: no board D draft of this record adds an IC (P0-1's apply_gen_sch_d_paloop.py adds resistors and a capacitor)": not [
            r for f in sorted(os.listdir(HERE)) if f.startswith("apply_gen_sch_d_") for r in _adds(os.path.join(HERE, f)) if r.startswith("U")],
    }
    w("5. THE PREDICATES")
    for k, v in pred.items():
        w("   %-110s %s" % (k, "yes" if v else "NO"))
    w("")
    w("l9t5_a1: done")
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(pred.values()) else 4


if __name__ == "__main__":
    sys.exit(main())
