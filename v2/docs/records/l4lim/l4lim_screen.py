#!/usr/bin/env python3
"""l4lim_screen.py: Layer 4 task L4A-101 (MESHSAT-1357, 7 October 2026), the limiter window screen before L4A-56 and L4A-57 (the
challenge W127's finding 3 on the AI-scope register's method M-A for RE-6 and RE-7). PROTOTYPE DESIGN: nothing in this kit has been
built, bought, powered or measured; no figure printed here is a measurement. A SCREEN, not an acceptance: it closes no cx46 item.

M-A, as registered: a current limiter with a PRINTED limit and a PRINTED response at each supervisor LDO's input, so that the LDO's
dissipation is bounded by the constant power at the limiter's printed maximum (a bound for every waveform under it). This script
states the limiter's WINDOW on printed limits against the four rows W127 named, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256 (record l9t5's output and pages, the makers' sheets, three of them held back);
  2. the window's edges, parsed (never typed) from record l9t5's T10 output at its fitted revision V and its 14.0k set point;
  3. the candidates' printed rows (page and row of each maker's sheet), and the parts considered and not taken, with why;
  4. row 1: the window against the rows the design must serve (IOHA row 7), and the local capacitance a limited frame would need
     against the capacitance a latch-off limiter can start into;
  5. row 2: the LDO output short;
  6. row 3: the limiter's own dissipation while limiting, and its restart waveform;
  7. row 4: T10-A3's headroom with the limiter's resistance in place of the 0.3 ohm sense;
  8. the line for L4A-56: GO with a candidate part, or CHANGE-METHOD naming the alternative, with why; the predicates.
Run from the repository root:  python3 v2/docs/records/l4lim/l4lim_screen.py  (l4lim_screen.out is its output, regenerated with
_bin/regen_out.py). It imports record l9t5's T10 and drafts modules for the AP2112 and TCAN334 rows and the supply path, exactly as
T10 reads them, and reproduces T10-A3's printed figure before substituting anything. Labels: PRINTED (a maker's limit or tested
row), TYPICAL, DECLARED, MODEL, ASSUMPTION, SESSION, INFERRED."""
import hashlib
import importlib.util
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(ROOT, "v2", "docs", "records", "l9t5"))
import l9t5_t10 as T  # noqa: E402  (record l9t5's T10: the AP2112, TCAN334 and H743 rows, the 14.0k set point)
D = T.D

T10_OUT = "v2/docs/records/l9t5/l9t5_t10.out"
DOCS = {"ioha": "v2/docs/ARCH-PCB-B-IOHA.md", "rem": "v2/docs/records/l4close/REMAINING-ENGINEERING.md",
        "t10py": "v2/docs/records/l9t5/l9t5_t10.py", "drafts": "v2/docs/records/l9t5/l9t5_drafts.py",
        "gndret": "v2/docs/records/l8r2/l8r2_gndret.out"}
SHEETS = {"ap2112": ("v2/vendor/diodes/diodes-ap2112-ldo.pdf", False), "tcan": ("v2/vendor/ti/ti-tcan334-can-fd-transceiver.pdf", False),
          "tps2553": ("v2/vendor/ti/held/ti-tps2553-slvs841f.pdf", True), "ap2265": ("v2/vendor/diodes/held/diodes-ap22652-53-ds41186.pdf", True),
          "tps25200": ("v2/vendor/ti/held/ti-tps25200-slvscj0f.pdf", True), "tps2596": ("v2/vendor/power/tps2596.pdf", False)}
FETCH = "v2/docs/records/l4lim/fetch_held_back.py"
REL = "v2/docs/records/l4lim"
# W34's rule (Q-41 item 1), carried here by W159 on W157's finding F3 (7 October 2026, the composition of fnd/l4hod with fnd/l4lim): a
# generator never runs pdftotext; every maker's text this screen reads is the committed (or, for a held-back sheet, the held) text the
# re-take takes: python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l4lim
PDFTEXT = {
    "v2/vendor/diodes/diodes-ap2112-ldo.pdf": [["-layout"]],
    "v2/vendor/diodes/held/diodes-ap22652-53-ds41186.pdf": [["-layout"]],
    "v2/vendor/power/tps2596.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps25200-slvscj0f.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps2553-slvs841f.pdf": [["-layout"]],
    "v2/vendor/ti/ti-tcan334-can-fd-transceiver.pdf": [["-layout"]],
}
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PT)

# the session's choices (SESSION under the owner's standing rule of 26 September 2026), each printed with its reason
R_TOL = 0.01          # the limit resistor at 1 % (the makers' recommended range is stated for 1 % parts; a 0.1 % part only narrows the band)
BITRATE = 500e3       # FW-B21's least bit rate (record l9t5 10d and 10i (4)): the longest bit, so the longest limited interval
FRAME_BITS = 135      # record l9t5's frame model (T10 FRAME_BITS): a classic 8-byte frame at its most stuffing, every bit counted dominant
R_COMPANION = 49.9    # kOhm: the one limit resistor at which BOTH candidates print a tested row over temperature (SLVS841F 7.5, DS41186 p.5)
E96 = (100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130, 133, 137, 140, 143, 147, 150, 154, 158, 162, 165, 169, 174, 178, 182,
       187, 191, 196, 200, 205, 210, 215, 221, 226, 232, 237, 243, 249, 255, 261, 267, 274, 280, 287, 294, 301, 309, 316, 324, 332, 340,
       348, 357, 365, 374, 383, 392, 402, 412, 422, 432, 442, 453, 464, 475, 487, 499, 511, 523, 536, 549, 562, 576, 590, 604, 619, 634,
       649, 665, 681, 698, 715, 732, 750, 768, 787, 806, 825, 845, 866, 887, 909, 931, 953, 976)
EN_DASH = chr(0x2013)


def refuse(msg):
    sys.stderr.write("l4lim_screen: REFUSED: %s\n" % msg)
    sys.exit(2)


def sha(relpath, n=16):
    return hashlib.sha256(open(os.path.join(ROOT, relpath), "rb").read()).hexdigest()[:n]


def text(relpath):
    return open(os.path.join(ROOT, relpath), encoding="utf-8").read()


_PDF = {}


def pdf(key):
    """The sheet's text with its page breaks (pdftotext writes a form feed between pages), so every reading carries its page."""
    if key not in _PDF:
        path, held = SHEETS[key]
        if not os.path.isfile(os.path.join(ROOT, path)):
            refuse("%s is not present%s" % (path, " (held back: run %s)" % FETCH if held else ""))
        _PDF[key] = PT.pdf_text(ROOT, path, ["-layout"], PDFTEXT, REL)
    return _PDF[key]


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


def page(t, m):
    return t[:m.start()].count("\f") + 1


def line(t, m):
    return t[:m.start()].count("\n") + 1


def edges():
    """Record l9t5's T10 output, parsed: every figure with the line it is printed on (the output is pinned in section 1)."""
    t = text(T10_OUT)
    E = {}

    def get(key, pat, what, n=1, flags=re.M):
        m = need(t, pat, what, flags)
        E[key] = (float(m.group(n)), line(t, m))
        return m
    get("air", r"THE JUNCTION TEMPERATURE at L4-E12's inside air, ([\d.]+) C", "the inside air (section 4)")
    get("mcu125", r"its junction reaches 125 C at ([\d.]+) A", "the H743's 125 C current (section 4)")
    get("theta", r"SOT25 junction to ambient (\d+) C/W, no heat sink \(p\.3\)", "the AP2112K's junction to ambient (section 7)")
    m = need(t, r"R602 14\.0k, ([\d.]+) V\s*\n\s*nominal, ([\d.]+) to ([\d.]+) V; the drop at its worst corner ([\d.]+) V, ([\d.]+) K/A",
             "the 14.0k set point and its corner (10i)")
    for k, g in (("nom14", 1), ("lo14", 2), ("hi14", 3), ("drop", 4), ("kpa", 5)):
        E[k] = (float(m.group(g)), line(t, m))
    get("foldback", r"foldback short current (\d+) mA \(TYPICAL\)", "the foldback's typical (section 7)")
    need(t, r"the foldback \(the output short's behaviour\) acts in no row", "T10's sentence on the foldback (section 8)")
    E["foldback_none"] = (1.0, line(t, need(t, r"the foldback \(the output short's behaviour\) acts in no row", "the foldback sentence")))
    m = need(t, r"against U601's (\d+) A \(PRINTED\) and the VH's (\d+) A", "U601's and the lead's ratings (section 9 (2))")
    E["u601"], E["vh"] = (float(m.group(1)), line(t, m)), (float(m.group(2)), line(t, m))
    get("share", r"the two transceivers at FW-B21's share \(10d\): ([\d.]+) A each", "the transceivers' share average (10c)")
    get("f1", r"\(f1\) one fabric faulted.*?: ([\d.]+) A, junction", "row (f1) (section 8)", flags=re.S)
    get("f2", r"\(f2\) both fabrics faulted, both transceivers driving into their faults: ([\d.]+) A", "row (f2) (section 8)")
    get("both_v", r"rev V: held ([\d.]+) A, [\d.]+ C \(OVER 150 C\)", "both fabrics held, rev V (10e)")
    get("bab_v", r"^\s+babbling \(nothing ends it\)\s+V\s+([\d.]+) A", "the babbling row's composition, rev V (10i)")
    get("vos0", r"105 C VOS0 limit from ([\d.]+) A \(MODEL\)", "HO-E's VOS0 current (10j (c))")
    m = need(t, r"each LDO's input at ([\d.]+) A, the sense\s*\n\s*resistor's drop counted: at least ([\d.]+) V against ([\d.]+) V: holds",
             "T10-A3 at the trip's average maximum (10j (d))")
    for k, g in (("a3_i", 1), ("a3_at", 2), ("a3_need", 3)):
        E[k] = (float(m.group(g)), line(t, m))
    m = need(t, r"Every served state is under the trip's least [\d.]+ A \(the largest\s*\n\s*([\d.]+) A\): none trips", "the served rows (10j (e))")
    E["s1"] = (float(m.group(1)), line(t, m))
    blk = t[m.end():m.end() + 2000]
    rows = re.findall(r"^\s{9}(\S.*?)\s{2,}([\d.]+) A\s+LDO ([\d.]+) C\s*$", blk, re.M)
    if len(rows) != 10 or abs(max(float(r[1]) for r in rows) - E["s1"][0]) > 1e-9:
        refuse("10j (e)'s ten served rows no longer read with their largest as the printed one")
    E["served_rows"] = [(lab.strip(), float(i)) for lab, i, _tj in rows]
    held = {}
    for m in re.finditer(r"^\s+(B\d[ab]?)\s+(V|Y)\s+([\d.]+) A\s+([\d.]+) C", t, re.M):
        held.setdefault((m.group(1), m.group(2)), (float(m.group(3)), line(t, m)))
    if len(held) != 16:
        refuse("10e's held rows no longer read as eight faults on two revisions")
    E["held"] = held
    m = need(t, r"B4\s+CANH to a 3\.3 V or 5 V net.*?\n\s+I_f ([\d.]+) A", "B4's I_f (10e)", re.S)
    E["if_b4"] = (float(m.group(1)), line(t, m))
    m = need(t, r"B5\s+CANL to a 3\.3 V or 5 V net.*?\n\s+I_f ([\d.]+) A, ASSUMED: IOS\(DOM\)'s 200 mA", "B5's I_f (10e)", re.S)
    E["if_b5"] = (float(m.group(1)), line(t, m))
    return E


def ioha():
    t = text(DOCS["ioha"])
    m7 = need(t, r"^\| 7 \| One CAN fabric breaks or a transceiver fails dominant \| n/a \| (quorum continues on the other fabric) \|", "IOHA row 7")
    m3 = need(t, r"^\| 3 \| One I/O supervisor dies or is unpowered \| n/a[^|]*\| (the other two are a majority and ownership is unaffected) \|", "IOHA row 3")
    m8 = need(t, r"^\| 8 \| Both CAN fabrics break \| n/a \| (no controller can form a majority;[^|]*?) \|", "IOHA row 8")
    ma7 = need(t, r"^\| A7 \| Heartbeat fabric break \| (cut fabric A, then fabric B, one at a time) \|", "IOHA test A7")
    return dict(row7=(m7.group(1), line(t, m7)), row3=(m3.group(1), line(t, m3)), row8=(m8.group(1).strip(), line(t, m8)),
                a7=(ma7.group(1), line(t, ma7)))


def sheets():
    """The makers' printed rows, each with its page: the two candidates, the LDO's packages, the transceiver's two rows."""
    S = {}
    t = pdf("tps2553")
    need(t, r"SLVS841F", "the TPS255x sheet's number")
    S["ti_doc"] = "TI SLVS841F (TPS2552, TPS2553, TPS2552-1, TPS2553-1; November 2008, revised August 2016)"
    m = need(t, r"RILIM = 49\.9 kΩ\s*\n\s*connected to GND\s+\S40°C ≤TJ ≤125°C\s+(\d+)\s+(\d+)\s+(\d+)", "IOS at 49.9 kOhm over TJ")
    S["ti_49"] = (tuple(float(x) / 1000 for x in m.groups()), page(t, m))
    m = need(t, r"RILIM = 210 kΩ\s+(\d+)\s+(\d+)\s+(\d+)", "IOS at 210 kOhm")
    S["ti_210"] = (tuple(float(x) / 1000 for x in m.groups()), page(t, m))
    eq = {}
    for k in ("max", "nom", "min"):
        m = need(t, r"(\d+)V\s*\n\s*IOS%s \(mA\) =\s*\n\s*RILIM([\d.]+)kW" % k, "the IOS%s equation" % k)
        eq[k] = (float(m.group(1)), float(m.group(2)))
    S["ti_eq"] = (eq, page(t, m))
    m = need(t, r"(\d+) kΩ ≤ RILIM ≤ (\d+) kΩ\.\s+\(1\)", "the equations' range")
    S["ti_rrange"] = (float(m.group(1)), float(m.group(2)))
    m = need(t, r"DBV package, \S40°C ≤TJ ≤125°C\s+(\d+)", "rDS(on) DBV over TJ")
    S["ti_ron"] = (float(m.group(1)) / 1000, page(t, m))
    m = need(t, r"FAULT assertion or de-assertion due to overcurrent condition\s+(\d+)\s+([\d.]+)\s+(\d+)\s+ms", "the overcurrent deglitch")
    S["ti_tlatch"] = (tuple(float(x) / 1000 for x in m.groups()), page(t, m))
    m = need(t, r"the TPS255x-1 limits the current to IOS until the overload condition is removed or the internal deglitch time\s*\nis reached "
             r"and the device is latched off\.", "the latch-off sentence (9.3.1)")
    S["ti_latch_p"] = page(t, m)
    m = need(t, r"The device remains\s*\noff until power is cycled or the device enable is toggled\.", "the latch's exit (9.3.1)")
    S["ti_exit_p"] = page(t, m)
    m = need(t, r"The deglitch circuitry delays entering and\s+leaving fault conditions\.", "the deglitch description (9.3.3)")
    S["ti_deg_p"] = page(t, m)
    m = need(t, r"RθJA\s+Junction-to-ambient thermal resistance\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "RthJA (7.4)")
    S["ti_rja"] = ((float(m.group(3)), float(m.group(4))), page(t, m))
    m = need(t, r"VIN\s+Input voltage, IN\s+([\d.]+)\s+([\d.]+)\s+V", "VIN (7.3)")
    S["ti_vin"] = (float(m.group(1)), float(m.group(2)))
    m = need(t, r"toff\s+Turnoff time\s+CL = 1 µF, RL = 100 Ω, \(see Figure 20\)\s+(\d+)\s+ms", "toff")
    S["ti_toff"] = (float(m.group(1)) / 1000, page(t, m))
    m = need(t, r"first thermal sensor turns off the power switch when the die temperature\s*\nexceeds (\d+)°C \(minimum\) and the part is in current limit",
             "the thermal sensor in current limit (9.3.6)")
    S["ti_otsd1"] = (float(m.group(1)), page(t, m))
    m = need(t, r"Reverse-voltage comparator trip point\s*\n\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "the reverse-voltage trip")
    S["ti_rv"] = (tuple(float(x) / 1000 for x in m.groups()), page(t, m))
    m = need(t, r"Time from reverse-voltage condition\s*\n\s+VIN = 5 V\s+(\d+)\s+(\d+)\s+(\d+)\s+ms\s*\n\s+to MOSFET turn off", "the reverse-voltage time")
    S["ti_rvt"] = tuple(float(x) / 1000 for x in m.groups())
    m = need(t, r"Fast Overcurrent Response - (\d+) µs \(Typical\)", "the overcurrent response (typical)")
    S["ti_tios"] = float(m.group(1))

    t = pdf("ap2265")
    need(t, r"Document number: DS41186 Rev\. 5 - 2", "the AP2265x sheet's number")
    S["ap_doc"] = "Diodes DS41186 Rev. 5 - 2 (AP22652, AP22653, AP22652A, AP22653A; March 2026)"
    m = need(t, r"RLIM = 49\.9k\S\s*\n\s*-40°C ≤ TA ≤ \+85°C\s+(\d+)\s+(\d+)\s+(\d+)", "ILIMIT at 49.9 kOhm over TA")
    S["ap_49"] = (tuple(float(x) / 1000 for x in m.groups()), page(t, m))
    m = need(t, r"RLIM = 210k\S\s+TA = \+25°C\s+(\d+)\s+(\d+)\s+(\d+)", "ILIMIT at 210 kOhm (25 C)")
    S["ap_210"] = (tuple(float(x) / 1000 for x in m.groups()), page(t, m))
    m = need(t, r"ILIMIT_Min\[mA\] = (\d+)/R\[k\S\]([\d.]+)\s+ILIMIT_Typ\[mA\] = (\d+)/R\[k\S\]([\d.]+)\s+ILIMIT_Max\[mA\] = (\d+)/R\[k\S\]([\d.]+)",
             "the best-fit equations")
    S["ap_eq"] = ({"min": (float(m.group(1)), float(m.group(2))), "nom": (float(m.group(3)), float(m.group(4))),
                   "max": (float(m.group(5)), float(m.group(6)))}, page(t, m))
    m = need(t, r"SOT26 \(Type A1\)\s*\n\s*-40°C ≤ TA ≤ \+85°C\s+\S\s+\S\s+(\d+)", "RDS(ON) SOT26 over TA")
    S["ap_ron"] = (float(m.group(1)) / 1000, page(t, m))
    m = need(t, r"tBLANK\s+FAULT Blanking Time\s+(\d+)\s+(\d+)\s+(\d+)\s+ms", "tBLANK")
    S["ap_tlatch"] = (tuple(float(x) / 1000 for x in m.groups()), page(t, m))
    m = need(t, r"For AP22652A/53A, when an overcurrent condition is detected, the devices will limit the current until the overload condition is "
             r"removed or the internal\s*\ndeglitch time \(6ms typical\) is reached, and AP22652A/53A will be turned off\. The AP22652A/53A will remain "
             r"latched off until power is cycled or the\s*\ndevice enable is toggled\.", "the latch-off paragraph")
    S["ap_latch_p"] = page(t, m)
    m = need(t, r"High-K\s+SOT26\s*\n\s*(\d+)°C/W", "theta JA SOT26 (high-K)")
    S["ap_rja"] = (float(m.group(1)), page(t, m))
    m = need(t, r"VIN\s+Input Voltage\s+(\d+)\s+([\d.]+)\s+V", "VIN")
    S["ap_vin"] = (float(m.group(1)), float(m.group(2)))
    m = need(t, r"Once the die temperature rises to approximately \+(\d+)°C, the thermal protection", "the thermal protection (approximately)")
    S["ap_otp"] = (float(m.group(1)), page(t, m))

    t = pdf("tps25200")
    need(t, r"SLVSCJ0F", "the TPS25200 sheet's number")
    m = need(t, r"The TPS25200 devices limit the current to IOS until the overload condition is removed or\s*\n.*?the device begins to thermal cycle",
             "the TPS25200's overload behaviour", re.S)
    S["t252_p"] = page(t, m)
    t = pdf("tps2596")
    need(t, r"SLVSET8A", "the TPS2596 sheet's number")
    m = need(t, r"exits current limiting when the load current falls below ILIM", "the TPS2596's current limit exit")
    S["t2596_p"] = page(t, m)
    m = need(t, r"TSD\s+TJ Rising\s+(\d+)", "the TPS2596's TSD row")
    S["t2596_tsd"] = (float(m.group(1)), page(t, m))
    need(t, r"Latch-off", "the TPS2596's latch-off variants (on TSD)")

    t = pdf("ap2112")
    m = need(t, r"SOT25\s+(\d+)\s*\n\s*θJA\s+Thermal Resistance \(Junction to Ambient\)\(No Heatsink\)\s+SO-8\s+(\d+)\s+°C/W\s*\n\s*SOT89-5\s+(\d+)",
             "the AP2112's three junction-to-ambient rows")
    S["ldo_pkgs"] = ({"SOT25 (AP2112K)": float(m.group(1)), "SO-8 (AP2112M)": float(m.group(2)), "SOT89-5 (AP2112R5)": float(m.group(3))}, page(t, m))
    for code in ("AP2112K-3.3TRG1", "AP2112M-3.3TRG1", "AP2112R5-3.3TRG1"):
        need(t, re.escape(code), "the order code %s" % code)
    t = pdf("tcan")
    m = need(t, r"VCC\s+Supply voltage\s+(\d+(?:\.\d+)?)\s+([\d.]+)\s+V", "the TCAN334's supply range (5.3)")
    S["vcc"] = ((float(m.group(1)), float(m.group(2))), page(t, m))
    m = need(t, r"The CAN protocol allows a maximum of (eleven) successive dominant bits \(on TXD\) for the\s*\n\s*worst case", "note 1's eleven bits")
    S["run_bits"] = (11, page(t, m))
    return S


def band_eq(eq, r_k, tol):
    """The current limit's band on a maker's equations, the resistor at its tolerance (MODEL on PRINTED equations)."""
    (cmin, emin), (cmax, emax) = eq["min"], eq["max"]
    return cmin / (r_k * (1 + tol)) ** emin / 1000.0, cmax / (r_k * (1 - tol)) ** emax / 1000.0


def band_row(row, eq, tol):
    """A tested row at its nominal resistor, the resistor's tolerance applied through the equations' exponents (MODEL on PRINTED)."""
    return row[0] * (1 + tol) ** -eq["min"][1], row[2] * (1 - tol) ** -eq["max"][1]


def best_r(eq, rrange, i_hi, i_floor):
    """The E96 value whose band reaches highest while its maximum stays at or under i_hi (the most a limit under i_hi can serve)."""
    best = None
    for dec in (10.0, 100.0):
        for v in E96:
            r = v * dec / 100.0
            if not (rrange[0] <= r <= rrange[1]):
                continue
            lo, hi = band_eq(eq, r, R_TOL)
            if hi <= i_hi and lo >= i_floor and (best is None or lo > best[1]):
                best = (r, lo, hi)
    return best


def need_at(P, i):
    """T10-A3's requirement at a current, exactly as T10 writes it (the dropout INFERRED between its printed points)."""
    d = P["drop"][10] + (P["drop"][300] - P["drop"][10]) * (i - 0.01) / 0.29 if i <= 0.3 else P["drop"][300] + (P["drop"][600] - P["drop"][300]) * (i - 0.3) / 0.3
    return 3.3 * (P["vout_hi"] + P["load"] * i) + d


def main():
    out = []
    w = out.append
    E, IO, S = edges(), ioha(), sheets()
    P, DP, G = T.figures(), D.figures(), D.gndret()
    lo14, nom14, hi14 = T.CHK.vout_band(T.R601, T.R602_SET)
    r_sup = G["rhot"] + 2 * DP["vh_r"][1]
    fixed = lo14 - D.RAIL_BUDGET * nom14 - G["shift_drawn_ub"]

    def avail(i_self, i_lead, r_ser):
        return fixed - i_lead * r_sup - r_ser * i_self
    air, tj = E["air"][0], T.TJ_GOAL
    drop = hi14 - 3.3 * P["vout_lo"]
    i125 = lambda theta: (tj - air) / (theta * drop)                       # noqa: E731  the LDO's 125 C current at the corner (MODEL)
    tj_at = lambda theta, i: air + theta * drop * i                        # noqa: E731
    rs_old = 0.3 * 1.01
    a3_repro = (need_at(P, E["a3_i"][0]), avail(E["a3_i"][0], 3 * E["a3_i"][0], rs_old))
    if abs(a3_repro[0] - E["a3_need"][0]) > 5e-5 or abs(a3_repro[1] - E["a3_at"][0]) > 5e-5 or abs(drop - E["drop"][0]) > 5e-5 \
            or abs(P["theta_ldo"] - E["theta"][0]) > 1e-9 or abs(air - P["air"]) > 1e-9:
        refuse("T10-A3, the corner or the LDO's rows no longer reproduce from record l9t5's modules as its output prints them")
    v_floor = S["vcc"][0][0]                                               # the transceiver's least supply (PRINTED)
    v_ldo_lo = 3.3 * P["vout_lo"]                                          # the LDO's least output (PRINTED band)
    dv = v_ldo_lo - v_floor
    t_bit = 1.0 / BITRATE
    s_v = {k[0]: v[0] for k, v in E["held"].items() if k[1] == "V"}
    dom = P["can_dom_hi"]
    peak_v = {b: s_v[b] - E["share"][0] + dom for b in ("B1", "B2", "B3", "B4", "B5")}   # held, the healthy fabric's transceiver dominant too

    w("l4lim_screen: Layer 4 task L4A-101, the limiter window screen before L4A-56 and L4A-57 (W127's finding 3; MESHSAT-1357)")
    w("prototype design; nothing built, bought, powered or measured; nothing applied to the tree; a SCREEN, not an acceptance: it closes no")
    w("cx46 item, accepts nothing and moves no state (cx46 CORRECTIONS NOT CLOSED and Layer 4's DESK gate NOT PASSED stand)")
    w("")
    w("1. INPUTS, pinned by sha256")
    for p in [T10_OUT] + list(DOCS.values()) + [v[0] for v in SHEETS.values()] + [FETCH]:
        w("   %s %s%s" % (sha(p), p, "  (held back; %s)" % FETCH if any(p == v[0] and v[1] for v in SHEETS.values()) else ""))
    for rel_, h_, held_ in PT.inputs(ROOT, PDFTEXT):   # the makers' texts read through pdftext.py (W159, W157-F3)
        if h_ is None:
            refuse("%s is not taken: python3 v2/docs/records/_lib/retake_pdf_text.py %s" % (rel_, REL))
        w("   %s %s%s" % (h_[:16], rel_, "  (held back with its sheet)" if held_ else ""))
    w("   not read: ADI's MAX4995A (latch-off, 50 to 600 mA class): analog.com refused this host and the Internet Archive answered")
    w("   'Temporarily Offline' on 7 October 2026; nothing is claimed from it")
    w("")
    w("2. THE WINDOW'S EDGES, from record l9t5's T10 output (%s, parsed; line numbers of that file), revision V (fitted, L9T5-D7), 14.0k" % T10_OUT)
    w("   the corner: inside air %.2f C (line %d); the pre-regulator %.4f to %.4f V, the LDO's least output %.4f V, so its drop %.4f V and" % (
        air, E["air"][1], lo14, hi14, v_ldo_lo, drop))
    w("     %.1f K/A on the AP2112K's %.0f C/W (line %d; PRINTED, no heat sink, DS39724 p.3); criterion %.0f C for every sustained state (SESSION," % (
        P["theta_ldo"] * drop, P["theta_ldo"], E["kpa"][1], tj))
    w("     the owner's part 22), %.0f C the absolute maximum, never an operating target" % P["tj_ldo"])
    w("   UPPER EDGE, the LDO's 125 C current at the corner, I125 = (%.0f - %.2f) / (theta x %.4f V) (MODEL on PRINTED theta):" % (tj, air, drop))
    pk = S["ldo_pkgs"]
    for name, th in pk[0].items():
        w("     %-20s theta %5.1f C/W  I125 %.4f A" % (name, th, i125(th)))
    w("     (the three are DS39724's own rows, p.%d, 'No Heatsink'; the board is not printed: realising any of them on board B's copper is a" % pk[1])
    w("     Layer 10 means, as T10 already says of the 184 C/W)")
    w("   LOWER EDGES, the currents the design must serve (each regulator's total: controller, auxiliaries, both transceivers):")
    w("     S1 the largest SUSTAINED served state (an average over FW-B21's window): %.4f A, line %d (MODEL; '%s')" % (
        E["s1"][0], E["s1"][1], max(E["served_rows"], key=lambda r: r[1])[0]))
    w("     S2 the normal-service PEAK, both transceivers dominant at once (a frame on each fabric): %.4f A, line %d (MODEL: 10i's" % (E["bab_v"][0], E["bab_v"][1]))
    w("        babbling row has exactly this composition, the bounded controller, the circuit's auxiliaries and both transceivers at the")
    w("        %.0f mA dominant row, PRINTED; in normal traffic it lasts bit times, not a sustained state)" % (dom * 1000))
    w("     S3 IOHA row 7's fault rows, held (the faulted transceiver dominant into the fault, the other at its share), rev V (10e):")
    for b in ("B1", "B2", "B3", "B4", "B5", "B6", "B7a", "B7b"):
        w("        %-4s %.4f A, line %d" % (b, s_v[b], E["held"][(b, "V")][1]))
    w("        and the brief's (f1) %.4f A (line %d; round 4's controller figure, rev Y at 144 MHz: a cover, larger than rev V's B1)" % (E["f1"][0], E["f1"][1]))
    w("     S3' the same rows with the healthy fabric's transceiver dominant in the same bit (MODEL: held - %.4f A share + %.3f A dominant):" % (
        E["share"][0], dom))
    for b in ("B1", "B2", "B3", "B4", "B5"):
        w("        %-4s %.4f A" % (b, peak_v[b]))
    s3p = max(peak_v.values())
    w("        largest %.4f A (B5: I_f 0.200 A ASSUMED by T10, IOS(DOM)'s printed 200 mA, line %d); row 7 '%s' (IOHA line %d) makes" % (
        s3p, E["if_b5"][1], IO["row7"][0], IO["row7"][1]))
    w("        the healthy fabric's frames part of the served state, so S3' is the row's instantaneous peak")
    w("     S4 IOHA row 8 (both fabrics faulted, survive, 'nothing moves'): (f2) %.4f A (line %d); rev V held %.4f A (line %d)" % (
        E["f2"][0], E["f2"][1], E["both_v"][0], E["both_v"][1]))
    w("     HO-E for reference: VOS0's 105 C limit from %.4f A (line %d), %.1f %% over S1's %.4f A: no current limit both serves S1 and holds it" % (
        E["vos0"][0], E["vos0"][1], 100 * (E["vos0"][0] / E["s1"][0] - 1), E["s1"][0]))
    w("        (W127 finding 2; HO-E is its own comparison, L4A-59)")
    w("")
    ti_eq, ap_eq = S["ti_eq"][0], S["ap_eq"][0]
    w("3. THE CANDIDATES: integrated current-limited switches with a PRINTED limit near 0.2 to 0.6 A and a PRINTED fault timer with latch-off")
    w("   C1 %s" % S["ti_doc"])
    w("      TPS2553-1 (latch-off, active-high EN; TPS2552-1 the active-low twin), SOT-23-6 (DBV) or WSON-6 (DRV); VIN %.1f to %.1f V (7.3)" % S["ti_vin"])
    w("      IOS PRINTED rows (7.5, p.%d): RILIM 49.9 kOhm, -40 C <= TJ <= 125 C: %.3f / %.3f / %.3f A; RILIM 210 kOhm: %.3f / %.3f / %.3f A" % (
        S["ti_49"][1], *S["ti_49"][0], *S["ti_210"][0]))
    w("      the maker's equations (9.5.1, p.%d; include temperature and process, not the resistor): IOSmin = %.0f / R^%.3f, IOSmax = %.0f / R^%.2f mA," % (
        S["ti_eq"][1], ti_eq["min"][0], ti_eq["min"][1], ti_eq["max"][0], ti_eq["max"][1]))
    w("        R in kOhm, %.0f to %.0f kOhm" % S["ti_rrange"])
    w("      rDS(on) DBV at most %.3f ohm, -40 C <= TJ <= 125 C (p.%d); RthJA DBV %.1f, DRV %.1f C/W (7.4, p.%d)" % (
        S["ti_ron"][0], S["ti_ron"][1], S["ti_rja"][0][0], S["ti_rja"][0][1], S["ti_rja"][1]))
    w("      FAULT TIMER: the overcurrent deglitch %.0f / %.1f / %.0f ms (min / typ / max, PRINTED, p.%d); LATCH-OFF: '...limits the current to" % (
        S["ti_tlatch"][0][0] * 1e3, S["ti_tlatch"][0][1] * 1e3, S["ti_tlatch"][0][2] * 1e3, S["ti_tlatch"][1]))
    w("        IOS until the overload condition is removed or the internal deglitch time is reached and the device is latched off' (9.3.1,")
    w("        p.%d); off 'until power is cycled or the device enable is toggled' (p.%d); turnoff time at most %.0f ms (p.%d)" % (
        S["ti_latch_p"], S["ti_exit_p"], S["ti_toff"][0] * 1e3, S["ti_toff"][1]))
    w("      NOT PRINTED: whether the deglitch restarts when an overload clears for a moment; the sheet says only 'The deglitch circuitry")
    w("        delays entering and leaving fault conditions' (9.3.3, p.%d). The response is %.0f us TYPICAL only" % (S["ti_deg_p"], S["ti_tios"]))
    w("   C2 %s" % S["ap_doc"])
    w("      AP22653A (latch-off, active-high EN; AP22652A active-low), SOT26 or W-DFN2020-6; VIN %.1f to %.1f V" % S["ap_vin"])
    w("      ILIMIT PRINTED rows (p.%d): RLIM 49.9 kOhm, -40 C <= TA <= +85 C: %.3f / %.3f / %.3f A; RLIM 210 kOhm at TA 25 C only: %.3f / %.3f / %.3f A" % (
        S["ap_49"][1], *S["ap_49"][0], *S["ap_210"][0]))
    w("      the maker's best-fit equations (p.%d; temperature and process, not the resistor): ILIMIT_Min = %.0f / R^%.3f, ILIMIT_Max = %.0f / R^%.3f mA" % (
        S["ap_eq"][1], ap_eq["min"][0], ap_eq["min"][1], ap_eq["max"][0], ap_eq["max"][1]))
    w("      RDS(ON) SOT26 at most %.3f ohm, -40 C <= TA <= +85 C (p.%d); theta JA SOT26 %.0f C/W on a JEDEC high-K board (p.%d)" % (
        S["ap_ron"][0], S["ap_ron"][1], S["ap_rja"][0], S["ap_rja"][1]))
    w("      FAULT TIMER: tBLANK %.0f / %.0f / %.0f ms (PRINTED, p.%d); LATCH-OFF: the A versions are 'turned off' when 'the internal deglitch time" % (
        S["ap_tlatch"][0][0] * 1e3, S["ap_tlatch"][0][1] * 1e3, S["ap_tlatch"][0][2] * 1e3, S["ap_tlatch"][1]))
    w("        (6ms typical) is reached' and 'remain latched off until power is cycled or the device enable is toggled' (p.%d); that this" % S["ap_latch_p"])
    w("        deglitch is the tBLANK row is INFERRED (the row names the FAULT flag); its restart on a momentary clearing is NOT PRINTED")
    w("   considered and not taken:")
    w("      TI TPS2596 (SLVSET8A, in the tree): its latch-off variants latch only at thermal shutdown (TSD %.0f C, p.%d, a TYPICAL figure)" % S["t2596_tsd"])
    w("        and it 'exits current limiting when the load current falls below ILIM' (p.%d): no printed fault timer" % S["t2596_p"])
    w("      TI TPS25200 (SLVSCJ0F): constant current until 'the device begins to thermal cycle' (p.%d): no latch-off, a periodic waveform" % S["t252_p"])
    w("      ADI MAX4995A: not read (section 1)")
    w("")

    # ---------------------------------------------------------------------------------------------------------------- row 1
    I184 = i125(P["theta_ldo"])
    cands = {"C1 TPS2553-1": dict(eq=ti_eq, rr=S["ti_rrange"], row=S["ti_49"][0], tl=S["ti_tlatch"][0], ron=S["ti_ron"][0], rja=S["ti_rja"][0][0]),
             "C2 AP22653A": dict(eq=ap_eq, rr=(10.0, 210.0), row=S["ap_49"][0], tl=S["ap_tlatch"][0], ron=S["ap_ron"][0], rja=S["ap_rja"][0])}
    w("4. ROW 1: THE WINDOW AGAINST THE ROWS THE DESIGN MUST SERVE (IOHA row 7, line %d: '%s')" % (IO["row7"][1], IO["row7"][0]))
    w("   W1, no served state limited: IOSmin >= the served peak and IOSmax <= I125. W2, served peaks limited and bridged by local capacitance:")
    w("   IOSmin >= S1, IOSmax <= I125, the bridging capacitance <= what the latch-off limiter can start into, AND a latch timer that restarts")
    w("   between limited intervals (printed by neither candidate: W2 can never be shown on printed limits)")
    w("   (a) M-A as registered: the limiter ahead of the AP2112K (SOT25, %.0f C/W): I125 %.4f A" % (P["theta_ldo"], I184))
    need_ratio = I184 / E["bab_v"][0]
    w("     W1 against S2 alone needs IOSmax / IOSmin <= %.4f / %.4f = %.3f (a +-%.1f %% band); against S3' (%.4f A) the edges cross: CLOSED" % (
        I184, E["bab_v"][0], need_ratio, 100 * (need_ratio - 1) / (need_ratio + 1), s3p))
    r184 = {}
    for name, c in cands.items():
        b = best_r(c["eq"], c["rr"], I184, E["s1"][0])
        r184[name] = b
        w("     %s: the highest band under I125 at an E96 resistor (1 %%): %.1f kOhm, IOS %.4f to %.4f A (ratio %.3f; MODEL on the maker's equations)" % (
            name, b[0], b[1], b[2], b[2] / b[1]))
    w("     so W1 is CLOSED at %.0f C/W for both candidates: normal service (S2) and every row-7 fault above IOSmin would be limited" % P["theta_ldo"])
    w("     W2, the capacitance (MODEL): a limited interval t at a peak I needs C = (I - IOSmin) x t / dV on the supervisor's 3.3 V rail, dV =")
    w("       the LDO's least output %.4f V less the TCAN334's least supply %.1f V (PRINTED, SLLSEQ7F 5.3, p.%d) = %.4f V; the latch-off limiter" % (
        v_ldo_lo, v_floor, S["vcc"][1], dv))
    w("       starts into at most C = (IOSmin - S1) x t_latch(min) / %.4f V (the rail charged at its least limit while the supervisor draws S1;" % (3.3 * P["vout_hi"]))
    w("       the soft start not credited)")
    w("       intervals: a frame on record l9t5's frame model, %d bit-times at %.0f kbit/s (FW-B21's least rate) = %.0f us (ASSUMPTION, T10's);" % (
        FRAME_BITS, BITRATE / 1e3, FRAME_BITS * t_bit * 1e6))
    w("       a run of %d successive dominant bits on TXD, TI's printed protocol worst case (SLLSEQ7F 5.7 note 1, p.%d) = %.0f us; a held TXD" % (
        S["run_bits"][0], S["run_bits"][1], S["run_bits"][0] * t_bit * 1e6))
    w("       ended by the driver time-out, %.1f ms (PRINTED maximum)" % P["can_dto"][2])
    rowsW2 = [("S2 normal frames, both transceivers dominant", E["bab_v"][0], FRAME_BITS * t_bit),
              ("B3 frames (the bus still works), S3'", peak_v["B3"], FRAME_BITS * t_bit),
              ("B4 frames (the bus still works), S3'", peak_v["B4"], FRAME_BITS * t_bit),
              ("B1/B2 error runs (bits read wrong), S3'", max(peak_v["B1"], peak_v["B2"]), S["run_bits"][0] * t_bit),
              ("B5 error runs (bits read wrong), S3'", peak_v["B5"], S["run_bits"][0] * t_bit),
              ("B7a a held TXD into the healthy bus, held", s_v["B7a"], P["can_dto"][2] / 1000.0)]
    w2 = {}
    for name, c in cands.items():
        r, lo, hi = r184[name]
        c_start = (lo - E["s1"][0]) * c["tl"][0] / (3.3 * P["vout_hi"])
        w("     %s at %.1f kOhm (IOSmin %.4f A, latch at least %.0f ms): it can start into at most %.1f uF" % (name, r, lo, c["tl"][0] * 1e3, c_start * 1e6))
        worst = 0.0
        for lab, i, t_ in rowsW2:
            cb = max(0.0, (i - lo) * t_ / dv)
            worst = max(worst, cb)
            w("       %-46s %.4f A for %7.1f us: bridging %6.1f uF  %s" % (lab, i, t_ * 1e6, cb * 1e6,
                                                                       "fits" if cb <= c_start else "OVER the start limit"))
        w2[name] = (c_start, worst)
    w("     so on the record's own frame model W2 conflicts for both candidates (B4's limited frame needs more capacitance than the latch-off")
    w("     limiter can start into), and on any interval model it rests on a latch timer whose restart is not printed: M-A at %.0f C/W has NO" % P["theta_ldo"])
    w("     WINDOW ON PRINTED LIMITS for the rows the design must serve")
    w("   (b) THE THERMAL-HEADROOM COMPANION: the limit raised over every served peak, the LDO's junction-to-ambient lowered to hold it")
    comp = {}
    for name, c in cands.items():
        lo, hi = band_row(c["row"], c["eq"], R_TOL)
        th_need = (tj - air) / (drop * hi)
        comp[name] = (lo, hi, th_need)
        w("     %s at %.1f kOhm: the PRINTED row %.3f to %.3f A with the resistor's 1 %% through the exponents: IOS %.4f to %.4f A (MODEL);" % (
            name, R_COMPANION, c["row"][0], c["row"][2], lo, hi))
        w("       IOSmin over S3' by %+.4f A, over S1 by %+.4f A: W1 holds on the served side; the LDO must hold 125 C at %.4f A: theta at most %.1f C/W" % (
            lo - s3p, lo - E["s1"][0], hi, th_need))
        elo, ehi = band_eq(c["eq"], R_COMPANION, R_TOL)
        w("       (the tested row governs; the maker's design equation at %.1f kOhm reads %.4f to %.4f A with the 1 %%, theta at most %.1f C/W if taken)" % (
            R_COMPANION, elo, ehi, (tj - air) / (drop * ehi)))
        for nm, th in pk[0].items():
            w("       %-20s %.1f C/W: junction %.1f C at %.4f A  %s" % (nm, th, tj_at(th, hi), hi, "holds" if tj_at(th, hi) <= tj else "FAILS"))
    w("     so no AP2112 package holds the companion's maximum: the companion is a different regulator part with a PRINTED junction-to-ambient")
    w("     at most %.1f C/W (C1) or %.1f C/W (C2) at this corner, rated at least the limiter's maximum (section 8)" % (
        comp["C1 TPS2553-1"][2], comp["C2 AP22653A"][2]))
    w("     no capacitance is needed to bridge a served frame (none is limited); the latch-off limiter starts into at most %.0f uF (C1, 5 ms)" % (
        (comp["C1 TPS2553-1"][0] - E["s1"][0]) * cands["C1 TPS2553-1"]["tl"][0] / (3.3 * P["vout_hi"]) * 1e6))
    w("     or %.0f uF (C2, 2 ms) on the rail, the decoupling's ceiling (MODEL)" % (
        (comp["C2 AP22653A"][0] - E["s1"][0]) * cands["C2 AP22653A"]["tl"][0] / (3.3 * P["vout_hi"]) * 1e6))
    lo1, hi1, _ = comp["C1 TPS2553-1"]
    w("     row 8 (S4, survive only): (f2) %.4f A and rev V's %.4f A against IOS %.4f to %.4f A: may be limited (no service is owed; IOHA" % (
        E["f2"][0], E["both_v"][0], lo1, hi1))
    w("       line %d: '%s');" % (IO["row8"][1], IO["row8"][0]))
    w("       a limiter that latches leaves its supervisor off until EN or power is cycled: the home assignment holds either way; the")
    w("       recovery after the repair is a restart (the peers' EN, section 6)")
    w("     what the companion gives up: its IOSmin (%.4f A) is over the H743's own 125 C current %.3f A (line %d), so a firmware fault outside" % (
        lo1, E["mcu125"][0], E["mcu125"][1]))
    w("       FW-B20 can still take the controller past its rating (T10 10h (3): a systematic firmware defect, not a protective mechanism); M-A")
    w("       at 184 C/W (IOSmax %.4f A) would have held it, had it a window; HO-E (VOS0 from %.4f A) is under every IOSmin either way (L4A-59)" % (
        r184["C1 TPS2553-1"][2], E["vos0"][0]))
    w("")

    # ---------------------------------------------------------------------------------------------------------------- row 2
    w("5. ROW 2: THE LDO OUTPUT SHORT (AP2112 'foldback short current %.0f mA (TYPICAL)', T10 line %d; 'acts in no row', line %d)" % (
        E["foldback"][0], E["foldback"][1], E["foldback_none"][1]))
    e_c1 = hi14 * hi1 * cands["C1 TPS2553-1"]["tl"][2]
    e_c2 = hi14 * comp["C2 AP22653A"][1] * cands["C2 AP22653A"]["tl"][2]
    w("   (i) the short draws the limiter's own limit through the LDO (the LDO fully on): the limiter limits and latches off within its")
    w("       PRINTED timer: the event's energy")
    w("       at most %.4f V x %.4f A x %.0f ms = %.1f mJ (C1 companion) or %.1f mJ (C2, 20 ms); with M-A at 184 C/W, %.1f mJ (C1 at %.1f kOhm)" % (
        hi14, hi1, cands["C1 TPS2553-1"]["tl"][2] * 1e3, e_c1 * 1e3, e_c2 * 1e3, hi14 * r184["C1 TPS2553-1"][2] * cands["C1 TPS2553-1"]["tl"][2] * 1e3, r184["C1 TPS2553-1"][0]))
    w("       (MODEL, the whole input across whichever part holds the drop); BOUNDED on printed limits")
    p_fb = hi14 * P["ishort"]
    w("   (ii) the LDO holds its own short current under the limiter's limit (the AP2112's foldback %.0f mA is TYPICAL, no maximum printed; a" % (P["ishort"] * 1e3))
    w("       companion part's own limit and foldback are likewise its own): the limiter does not act; the LDO holds the")
    w("       whole input at its own short current for as long as the short lasts (%.3f W at the typical, %.1f C at 184 C/W: a TYPICAL reading," % (
        p_fb, air + P["theta_ldo"] * p_fb))
    w("       never a bound). EXCLUDED from the LDO-junction criterion, with the reason (SESSION): a supervisor on a shorted rail is already")
    w("       lost, which IOHA row 3 (line %d) carries: '%s'; the containment that row needs is held on PRINTED" % (IO["row3"][1], IO["row3"][0]))
    w("       limits whatever the LDO does: +5V_IOC and the other two branches see at most IOSmax from it, and an LDO that fails shorted")
    w("       input to output becomes case (i), which latches. The bounded-interval disconnection of a dead branch is the peers' vote on its")
    w("       limiter's EN (L4A-54's M-B vote outputs; turnoff at most %.0f ms PRINTED): a finding for L4A-54 and L4A-56, not a printed timer" % (
        S["ti_toff"][0] * 1e3))
    w("   result: a PRINTED fault timer with latch-off on both candidates (C1 %.0f to %.0f ms, C2 %.0f to %.0f ms); the sub-case under the" % (
        S["ti_tlatch"][0][0] * 1e3, S["ti_tlatch"][0][2] * 1e3, S["ap_tlatch"][0][0] * 1e3, S["ap_tlatch"][0][2] * 1e3))
    w("   limit is excluded with its reason, not bounded")
    w("")

    # ---------------------------------------------------------------------------------------------------------------- row 3
    w("6. ROW 3: THE LIMITER'S OWN DISSIPATION WHILE LIMITING, AND ITS RESTART WAVEFORM")
    for name, c in cands.items():
        lo, hi, _th = comp[name]
        p_on = s3p ** 2 * c["ron"]
        w("   %s companion: in service at S3' %.4f A, %.1f mW (rDS(on) %.3f ohm PRINTED): junction %.1f C at %.1f C/W (MODEL); limiting into a" % (
            name, s3p, p_on * 1e3, c["ron"], air + c["rja"] * p_on, c["rja"]))
        w("     shorted output at most %.4f V x %.4f A = %.3f W for at most %.0f ms (the timer's PRINTED maximum), %.1f mJ; its junction in that" % (
            hi14, hi, hi14 * hi, c["tl"][2] * 1e3, hi14 * hi * c["tl"][2] * 1e3))
        w("     time is NOT computed (no transient thermal impedance printed): surviving it is the part's stated function (both sheets: short")
        w("     circuits), backed by its own thermal protection")
    w("   C1's thermal sensor in current limit acts from %.0f C (minimum, 9.3.6, p.%d); C2's at approximately %.0f C (p.%d, no limit printed)" % (
        S["ti_otsd1"][0], S["ti_otsd1"][1], S["ap_otp"][0], S["ap_otp"][1]))
    w("   RESTART: the latch-off versions do not restart by themselves (C1 p.%d, C2 p.%d): no periodic waveform of their own. Two exceptions:" % (
        S["ti_exit_p"], S["ap_latch_p"]))
    w("     a hard short at the limiter's own output may thermal-cycle it inside the timer (whether the deglitch completes across a thermal")
    w("     cycle is NOT PRINTED): a periodic waveform in the limiter alone, its current at most IOSmax (PRINTED), so the containment holds and")
    w("     the LDO is not in that path; and a restart the peers command through EN (L4A-54, L4A-58) must bound its own rate: at most one")
    w("     attempt per T_r keeps the average at most %.1f mJ / T_r (%.1f mW at 10 s)" % (e_c1 * 1e3, e_c1 / 10 * 1e3))
    rv = S["ti_rv"][0]
    w("   the reverse-voltage latch (C1: VOUT - VIN %.0f to %.0f mV held %.0f to %.0f ms, PRINTED, p.%d) needs the LDO's input capacitance to" % (
        rv[0] * 1e3, rv[2] * 1e3, S["ti_rvt"][0] * 1e3, S["ti_rvt"][2] * 1e3, S["ti_rv"][1]))
    w("     stay above a falling +5V_IOC for 3 ms against the supervisor's own draw (10 uF at 10 mA falls 1 V a ms): not a credible trip in")
    w("     service (MODEL); at power-down it latches nothing that a power cycle does not clear")
    w("")

    # ---------------------------------------------------------------------------------------------------------------- row 4
    w("7. ROW 4: T10-A3'S HEADROOM WITH THE LIMITER'S RESISTANCE IN PLACE OF THE 0.3 OHM SENSE (the supply path exactly as T10 computes it:")
    w("   the pre-regulator's least %.4f V, the rail's %.0f %% budget, the lead and contacts %.5f ohm at the total current, the return's shift %.4f V)" % (
        lo14, 100 * D.RAIL_BUDGET, r_sup, G["shift_drawn_ub"]))
    w("   reproduced first: at %.4f A with 0.3 ohm at +1 %%: %.4f V against %.4f V (T10 line %d prints %.4f against %.4f): EQUAL" % (
        E["a3_i"][0], a3_repro[1], a3_repro[0], E["a3_at"][1], E["a3_at"][0], E["a3_need"][0]))
    a3 = {}
    for name, c in cands.items():
        at = avail(E["a3_i"][0], 3 * E["a3_i"][0], c["ron"])
        a3[name] = at - a3_repro[0]
        w("   (a) %s's %.3f ohm at T10's point, %.4f A on all three: %.4f V against %.4f V: %+.4f V, %s" % (
            name, c["ron"], E["a3_i"][0], at, a3_repro[0], at - a3_repro[0], "holds" if at >= a3_repro[0] else "FAILS"))
    c = cands["C1 TPS2553-1"]
    w("   (b) at each design's largest sustained current, IOSmax on all three (the AP2112's dropout rows, INFERRED between 300 and 600 mA as T10):")
    rb = {}
    for lab, i in (("M-A at 184 C/W, C1 at %.1f kOhm" % r184["C1 TPS2553-1"][0], r184["C1 TPS2553-1"][2]), ("companion, C1 at 49.9 kOhm", hi1)):
        at, nd = avail(i, 3 * i, c["ron"]), need_at(P, i)
        rb[lab] = (at, nd)
        w("       %-34s %.4f A: %.4f V against %.4f V: %+.4f V, %s" % (lab, i, at, nd, at - nd, "holds" if at >= nd else "FAILS on the AP2112's rows"))
    at_c, nd_c = rb["companion, C1 at 49.9 kOhm"]
    vout_part = 3.3 * (P["vout_hi"] + P["load"] * hi1)
    w("       so the companion regulator's PRINTED dropout at %.4f A must be at most %.4f - %.4f = %.4f V (with the AP2112's output band and" % (
        hi1, at_c, vout_part, at_c - vout_part))
    w("       load regulation; its own rows replace them)")
    at_o = avail(E["s1"][0], hi1 + 2 * E["s1"][0], c["ron"])
    w("   (c) the other two while one sits at the companion's IOSmax: lead %.4f A, each other LDO at S1 %.4f A: %.4f V against %.4f V: %+.4f V, %s" % (
        hi1 + 2 * E["s1"][0], E["s1"][0], at_o, need_at(P, E["s1"][0]), at_o - need_at(P, E["s1"][0]),
        "holds" if at_o >= need_at(P, E["s1"][0]) else "FAILS"))
    w("   (d) the connected path upstream: three limiters at their maximum draw %.4f A from U601 and the lead's pin 1, against U601's %.0f A and" % (
        3 * hi1, E["u601"][0]))
    w("       the VH's %.0f A (PRINTED, T10 line %d): %s; a shorted branch takes at most IOSmax from them, so the other two keep their supply" % (
        E["vh"][0], E["u601"][1], "holds" if 3 * hi1 <= E["u601"][0] else "FAILS"))
    at_p = avail(s3p, 3 * s3p, c["ron"])
    w("   (e) S3' on all three in one bit (error flags overlap): %.4f V against %.4f V on the AP2112's rows: %+.4f V (a bit-time peak; the LDO's" % (
        at_p, need_at(P, s3p), at_p - need_at(P, s3p)))
    w("       input capacitance carries it; shown, not judged)")
    w("")

    # ---------------------------------------------------------------------------------------------------------------- the line
    go = any(r184[n][1] >= s3p for n in cands)
    w("8. THE LINE FOR L4A-56")
    if go:
        w("   GO: a candidate serves every row on printed limits at 184 C/W")
    else:
        w("   CHANGE-METHOD: M-A as registered (a limiter ahead of the AP2112K at %.0f C/W) has no window on printed limits: its 125 C current" % P["theta_ldo"])
        w("   %.4f A sits %.1f %% over normal service's own peak (S2 %.4f A) and under row 7's (S3' %.4f A); serving them through limiting needs" % (
            I184, 100 * (I184 / E["bab_v"][0] - 1), E["bab_v"][0], s3p))
        w("   more capacitance than the latch-off limiter can start into and a latch timer neither maker prints. TAKE THE THERMAL-HEADROOM")
        w("   COMPANION (SESSION, W135-1): C1, TI TPS2553-1 (SLVS841F; DBV), RILIM 49.9 kOhm, IOS %.3f to %.3f A, latch-off after %.0f to %.0f ms," % (
            lo1, hi1, S["ti_tlatch"][0][0] * 1e3, S["ti_tlatch"][0][2] * 1e3))
        w("   at each supervisor LDO's input, AND a regulator part in place of the AP2112K with, PRINTED: junction-to-ambient at most %.1f C/W at" % comp["C1 TPS2553-1"][2])
        w("   the 14.0k corner, rated output and current limit at least %.3f A, dropout at %.3f A at most %.3f V, input to at least %.2f V." % (
            hi1, hi1, at_c - vout_part, hi14))
        w("   Second source: C2, Diodes AP22653A (DS41186), RLIM 49.9 kOhm, IOS %.3f to %.3f A, theta at most %.1f C/W, latch after %.0f to %.0f ms" % (
            comp["C2 AP22653A"][0], comp["C2 AP22653A"][1], comp["C2 AP22653A"][2], S["ap_tlatch"][0][0] * 1e3, S["ap_tlatch"][0][2] * 1e3))
        w("   WHY the companion and not K1: it keeps the drafted structure (pre-regulator, a private LDO a supervisor, CON-004's own branch) and")
        w("   its acceptance (T10-A2, T10-A3) and adds one SOT-23-6 and a resistor a supervisor; no served row is limited, so nothing rests on a")
        w("   timer's unprinted restart, the protocol or the firmware. K1 (a buck a supervisor, U25's AP63203) is the FALLBACK if no regulator")
        w("   with those printed figures fits board B's pockets: it was set aside for area and switching ripple on VDD and VDDA, not because it")
        w("   failed (T10 section 8). To reverse W135-1: take K1, or a limiter class that prints a band of +-%.1f %% at 0.29 A (none of the four" % (
            100 * (need_ratio - 1) / (need_ratio + 1)))
        w("   sheets read does)")
    w("")
    pred = {}
    pred["T10-A3's printed figure reproduces from record l9t5's modules before the limiter's resistance replaces the sense"] = True
    pred["no candidate's band fits under the AP2112K's 125 C current with its minimum at row 7's peak (W1 closed at 184 C/W)"] = not go
    pred["W2 at 184 C/W: a row-7 frame needs more bridging capacitance than the latch-off limiter starts into, for both candidates"] = all(
        w2[n][1] > w2[n][0] for n in cands)
    pred["both candidates print a fault timer (minimum and maximum) and a latch-off that only EN or power clears"] = all(
        cands[n]["tl"][0] > 0 and cands[n]["tl"][2] > cands[n]["tl"][0] for n in cands)
    pred["at 49.9 kOhm both candidates' minimum is over every served peak (S3') and no AP2112 package holds 125 C at their maximum"] = all(
        comp[n][0] > s3p and all(tj_at(th, comp[n][1]) > tj for th in pk[0].values()) for n in cands)
    pred["the limiter's resistance in place of the 0.3 ohm sense keeps T10-A3 at T10's own point"] = all(v >= 0 for v in a3.values())
    pred["three companion limiters at their maximum stay inside U601's and the lead's printed ratings"] = 3 * hi1 <= min(E["u601"][0], E["vh"][0])
    pred["the AP2112's typical foldback is under every IOSmin, so the output short under the limit is excluded with a reason, not bounded"] = (
        P["ishort"] < min(r184[n][1] for n in cands))
    w("9. THE PREDICATES")
    for k, v in pred.items():
        w("   %-122s %s" % (k, "yes" if v else "NO"))
    w("")
    w("l4lim_screen: done")
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(pred.values()) else 4


if __name__ == "__main__":
    sys.exit(main())
