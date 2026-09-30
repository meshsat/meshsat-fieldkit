#!/usr/bin/env python3
"""vbus20_range.py: board A's charge bus VBUS20 at the charger U3's input, under load and temperature, term by term from the
design as generated and the makers' own pages (stream l3plane, MESHSAT-1357, 30 September 2026).

PROTOTYPE DESIGN, desk arithmetic: nothing is built, powered or measured. Every figure printed carries its basis: MAKER
(document and page, read by this script from the PDF's text layer), NETLIST (board A's committed netlist), or INFERRED (a
figure no maker states; the reason is printed beside it).

Why. The energy model turns U3's input current limit into power at energy_two_pack.py's V_BUS20 = 20.7 V. Stream s120
(records/s120/vbus20_bound.py) printed the front end's DC band as 19.08 to 20.96 V, its TCR term an assumption (100 ppm/K
over 65 K). The owner asked for the applicable range established from the design: VREF over temperature, the regulation
under load and line, R6's and R7's actual parts and their TCR from the makers' sheets, the kit's internal temperature,
and the drops between the regulation point and U3.

What it reads (each checked; the script refuses, exit 3, if a fact it rests on is not what it expects):
  * board A's committed netlist v2/ecad/pcb-a-power-a23/out/pcb-a-power.net (the file s120 read): R6, R7 and their nets,
    U2's FB pin, R11 (FE_OUT to VBUS20), R16 (VBUS20 to CH_ACN) and U3's VBUS pin;
  * R6's and R7's purchase codes: v2/ecad/tools/lcsc_fill.py's MAP, applied as that script applies it (first key whose
    value regex matches the netlist value and whose footprint substring is in the footprint), since the netlist carries no
    code for either; corroborated by the released A24 BOM row;
  * the makers' sheets: YAGEO RC_L series V.12 (filed, v2/vendor/passives/yageo-rc-l-series-v12.pdf, pages 2 and 5) for
    R6 RC0603FR-07240KL; UNI-ROYAL thick film chip resistors V.3 (HELD BACK, v2/vendor/passives/held/, pages 2 and 6; read
    only when present with its pinned sha256) for R7 0603WAF1002T5E; TI SNVSAI1D (LM5176, v2/vendor/ti/lm5176-datasheet.pdf,
    pages 5 to 7);
  * the kit's temperatures: v2/ecad/tools/pcb_envelope.yaml (the in-use ambient, the worst inside air, the rise in
    PS-IDLE-SPEC with the lid open) and the reference day's T2m (the 40/0 DRcalc file of the energy model);
  * stream s120's printed band (records/s120/vbus20_bound.out section 2), for comparison.

Second issue (30 September 2026, after the independent check CHECK-1 of 6a283b25, minors 1, 2, 3, 5 and 10): the range is
called what it is, a STEADY-STATE range, and the soft start, the transients and the ground offset are named; two brackets are
added beside it, the divider's own rise on board A (an assumption, stated) and the resistors' endurance limits (a bound at
test stress); U3's input current is labelled (its 6.1 A minimum is INFERRED: SLUSE66A prints only the maximum, and its front
page's +-2.5 %); and the as-generated entry's 50 mA margin is named.
Run from the repository root:  python3 v2/docs/records/l3plane/vbus20_range.py > v2/docs/records/l3plane/vbus20_range.out
Deterministic (pdftotext's text layer of pinned files). Exit 3: an input is missing, changed or not what is expected."""
import ast
import csv
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import netlist_sexp as N  # noqa: E402
import yaml  # noqa: E402

NET_A = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"
LCSC_FILL = "v2/ecad/tools/lcsc_fill.py"
BOM_A24 = "v2/release/revA/boards/meshsat-pcb-a-revA-A24/pcb-a-power-bom.csv"
READING = "v2/docs/parts/readings/lcsc-2026-09-27.json"
YAGEO = ("v2/vendor/passives/yageo-rc-l-series-v12.pdf", "e7dbabb0611925227ccfc429c14c8833a7b1f2c755684444124446f20b22a229")
UNIROYAL = ("v2/vendor/passives/held/uniroyal-series-11cd644d.pdf", "11cd644d5d8a34a6d12775afb80bf58d8fc11f0c3b700dbd0f7a59942ceaa5ef")
LM5176 = "v2/vendor/ti/lm5176-datasheet.pdf"
ENVELOPE = "v2/ecad/tools/pcb_envelope.yaml"
ANCHOR = "v2/docs/records/a1solar/inputs/pvgis-leiden-daily-profile-2005-2020.json"
S120_OUT = "v2/docs/records/s120/vbus20_bound.out"
BQ25731 = "v2/vendor/ti/bq25731-datasheet.pdf"
BOARD_RISE_K = 20.0                    # ASSUMPTION (CHECK-1 minor 2): the divider's own rise over the inside air on board A,
                                       # which no layout establishes; printed as a bracket beside the range, not in it

R6_TOP, R7_BOT = 240e3, 10e3           # checked against the netlist's values below
T_REF = 25.0                           # the makers' TCR reference, read below: UNI-ROYAL p.6 and YAGEO p.8, "t1 = +25 C"
I_U3_MAX = 6.3                         # U3's IIN_HOST 6.2 A nominal plus the 100 mA SLUSE66A 9.6.22 p.80 adds for the maximum
                                       # (energy_two_pack.py PAR u3_iin_draft_a, read below)


def refuse(msg):
    sys.stderr.write("vbus20_range: %s; refusing\n" % msg)
    sys.exit(3)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


SYMBOL_FONT = {0xF057: "Ω", 0xF0B1: "±", 0xF0B0: "°"}   # the symbol font's private-use code points in UNI-ROYAL's text layer


def page(rel, n):
    return subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), os.path.join(TOP, rel), "-"],
                          capture_output=True, text=True, check=True).stdout.translate(SYMBOL_FONT)


def need(text, pattern, what):
    m = re.search(pattern, text, re.M)
    if not m:
        refuse("%s not found" % what)
    return m


def lcsc_map():
    tree = ast.parse(open(os.path.join(TOP, LCSC_FILL), encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MAP" for t in node.targets):
            return ast.literal_eval(node.value)
    refuse("lcsc_fill.py's MAP not found")


def code_for(mp, value, footprint):
    for (vre, fsub), code in mp.items():
        if re.match(vre, value) and fsub in footprint:
            return code
    return None


def band(vref, tol, tcr6, tcr7, dt, ibias, reg, life6=0.0, life7=0.0):
    """(low, high) of VOUT = VREF (1 + R6 / R7) at the regulation point: tolerance and TCR taken in opposite directions on
    the two resistors (the makers give each a limit, not a tracking figure, and the two are different makers' parts),
    IBIAS(FB) through R6 both ways, and the error amplifier's finite gain both ways; life6 and life7 add each resistor's
    endurance limit as a fraction of its value, in the same opposite directions."""
    d6, d7 = tol + tcr6 * dt + life6, tol + tcr7 * dt + life7
    r_lo = 1 + R6_TOP * (1 - d6) / (R7_BOT * (1 + d7))
    r_hi = 1 + R6_TOP * (1 + d6) / (R7_BOT * (1 - d7))
    return vref[0] * r_lo - ibias * R6_TOP * (1 + d6) - reg, vref[2] * r_hi + ibias * R6_TOP * (1 + d6) + reg


def compute():
    out = {}
    a = N.load(os.path.join(TOP, NET_A))
    comp, pins = a["components"], a["pins"]

    def nets(ref):
        return {p: v["net"] for p, v in pins[ref].items()}
    f = []
    ok = (comp["R6"]["value"] == "240k 1%" and sorted(nets("R6").values()) == ["FE_FB", "VBUS20"]
          and comp["R7"]["value"] == "10k 1%" and sorted(nets("R7").values()) == ["FE_FB", "GND"]
          and nets("U2").get("11") == "FE_FB")
    f.append(("the FB divider", ok, "R6 %s on %s, R7 %s on %s, U2 (%s) pin 11 on %s" % (
        comp["R6"]["value"], sorted(nets("R6").values()), comp["R7"]["value"], sorted(nets("R7").values()),
        comp["U2"]["value"].split(" ")[0], nets("U2").get("11"))))
    ok = nets("R11") == {"1": "FE_OUT", "2": "VBUS20"} and comp["R11"]["value"].startswith("10mOhm")
    f.append(("R11, the front end's ISNS shunt", ok, "%s, pin 1 %s, pin 2 %s: the divider's R6 is on VBUS20, the shunt's far side"
              % (comp["R11"]["value"], nets("R11")["1"], nets("R11")["2"])))
    ok = nets("R16") == {"1": "VBUS20", "2": "CH_ACN"} and nets("U3").get("1") == "VBUS20"
    f.append(("U3's input", ok, "R16 %s from %s to %s; U3 (%s) pin 1 VBUS on %s" % (
        comp["R16"]["value"], nets("R16")["1"], nets("R16")["2"], comp["U3"]["value"].split(" ")[0], nets("U3").get("1"))))
    codes6 = comp["R6"].get("fields", {}).get("LCSC"), comp["R7"].get("fields", {}).get("LCSC")
    f.append(("no purchase code in the netlist", codes6 == (None, None), "R6 %s, R7 %s" % codes6))
    if not all(x[1] for x in f):
        refuse("a netlist fact does not hold: %s" % [x[0] for x in f if not x[1]])
    out["netlist"] = (NET_A, sha(os.path.join(TOP, NET_A))[:16], f)

    # identities
    mp = lcsc_map()
    c6 = code_for(mp, comp["R6"]["value"], comp["R6"]["footprint"])
    c7 = code_for(mp, comp["R7"]["value"], comp["R7"]["footprint"])
    bom = {}
    for row in csv.reader(open(os.path.join(TOP, BOM_A24), encoding="utf-8")):
        for ref in (row[1].split(",") if len(row) > 3 else []):
            bom[ref.strip()] = (row[0], row[3])
    rd = {x["code"]: x for x in json.load(open(os.path.join(TOP, READING), encoding="utf-8"))["rows"]}
    if (c6, c7) != ("C137765", "C25804") or bom.get("R6", (None, None))[1] != c6 or bom.get("R7", (None, None))[1] != c7:
        refuse("R6 and R7's codes are not C137765 and C25804 by lcsc_fill.py and the A24 BOM")
    r7_read = rd.get(c7)
    if not r7_read or r7_read.get("model") != "0603WAF1002T5E":
        refuse("the LCSC reading of C25804 is not UNI-ROYAL 0603WAF1002T5E")
    out["ident"] = (c6, c7, bom["R6"], bom["R7"], r7_read)

    # YAGEO RC_L V.12, R6
    if sha(os.path.join(TOP, YAGEO[0])) != YAGEO[1]:
        refuse("the YAGEO RC_L sheet is not the pinned file")
    p2, p5 = page(YAGEO[0], 2), page(YAGEO[0], 5)
    need(p2, r"F = ± 1\.0%", "YAGEO p.2 tolerance code F")
    need(p2, r"R = Paper taping reel", "YAGEO p.2 packaging code R")
    need(p2, r"07 = 7 inch dia\. Reel & Standard power", "YAGEO p.2 code 07")
    need(p2, r"\(4\) TEMPERATURE COEFFICIENT OF RESISTANCE", "YAGEO p.2 TCR field")
    lines = p5.split("\n")
    i_p = next(i for i, l in enumerate(lines) if "1/10 W" in l and "75V" in l)          # RC0603's power row
    i_lab = next(i for i, l in enumerate(lines) if i > i_p and l.startswith("RC0603"))
    i_prev = max(i for i, l in enumerate(lines) if i < i_p and ("1/8W" in l or "1/16 W" in l))   # RC0402's last row
    i_first = next(i for i, l in enumerate(lines) if i > i_prev and "5% (E24)" in l)
    blk = [l for l in lines[i_first:i_lab + 3] if l.strip()]
    tcr_line = [l for l in blk if "10Ω<R≦10MΩ" in l]
    if not tcr_line or "± 100ppm°C" not in " ".join(blk) or not any("1% (E24/E96)" in l for l in blk):
        refuse("YAGEO p.5 Table 2's RC0603 1 % row not read")
    p8 = page(YAGEO[0], 8)
    need(p8, r"At \+25/\u201355°C and \+25/\+125°C", "YAGEO p.8 the TCR test temperatures")
    need(p8, r"t1=\+25 °C or specified room temperature", "YAGEO p.8 the TCR reference")
    tcr6 = 100e-6
    need(p8, r"Life/", "YAGEO p.8 the Life/Endurance row")
    need(p8, r"At 70± 2°C for 1,000 hours", "YAGEO p.8 the endurance test")
    need(p8, r"± \(1%\+50mΩ\) for B/D/F tol", "YAGEO p.8 the endurance limit for 1 % parts")
    life6 = 0.01 + 0.050 / R6_TOP
    out["yageo"] = (YAGEO[0], YAGEO[1][:16], [l.strip() for l in blk])
    # UNI-ROYAL, R7 (held back)
    up = os.path.join(TOP, UNIROYAL[0])
    if os.path.exists(up):
        if sha(up) != UNIROYAL[1]:
            refuse("the held UNI-ROYAL sheet is present but not the pinned file")
        u2, u6 = page(UNIROYAL[0], 2), page(UNIROYAL[0], 6)
        need(u2, r"WA=1/10W", "UNI-ROYAL p.2 power code WA")
        need(u2, r"F=±1%", "UNI-ROYAL p.2 tolerance code F")
        m = need(u6, r"0603：[\s\S]*?>10Ω: ±100PPM/℃", "UNI-ROYAL p.6 0603 TCR row")
        need(u6, r"t1: \+25°C or specified room temperature", "UNI-ROYAL p.6 TCR reference")
        u7 = page(UNIROYAL[0], 7)
        need(u7, r"Load life", "UNI-ROYAL p.7 the load life row")
        need(u7, r"70℃±2℃ ambient", "UNI-ROYAL p.7 the load life test")
        need(u7, r"±0\.5%,±1%\s*:\s*±\(1\.0%\+0\.05Ω\)", "UNI-ROYAL p.7 the 1 % limit")
        rows = re.findall(r"1Ω≤R≤10Ω: ±200PPM/°C|>10Ω: ±100PPM/℃", m.group(0))
        if rows != ["1Ω≤R≤10Ω: ±200PPM/°C", ">10Ω: ±100PPM/℃"]:
            refuse("UNI-ROYAL p.6's 0603 rows not the two expected")
        out["uniroyal"] = (UNIROYAL[0], UNIROYAL[1][:16], "p.6 rows read for 0603: %s; %s; reference t1 +25 C" % tuple(rows))
    else:
        out["uniroyal"] = (UNIROYAL[0], UNIROYAL[1][:16], "NOT PRESENT here (held back): not re-read; the LCSC reading's "
                           "'Temperature Coefficient %s' is used" % r7_read["params"].get("Temperature Coefficient"))
    tcr7 = 100e-6
    life7 = 0.01 + 0.05 / R7_BOT
    out["life"] = (life6, life7)

    # TI SNVSAI1D
    t5, t6, t7 = page(LM5176, 5), page(LM5176, 6), page(LM5176, 7)
    need(t6, r"Minimum and maximum limits apply over the \u201340°C to 125°C junction\s*\n?\s*temperature|Minimum and maximum limits apply over the \u201340°C to 125°C junction temperature",
         "SNVSAI1D p.6 the limits' temperature range")
    m = need(t6, r"VREF\s+Feedback reference voltage\s+FB = COMP\s+(0\.\d+)\s+(0\.\d+)\s+(0\.\d+)\s+V", "SNVSAI1D p.6 VREF")
    vref = tuple(float(x) for x in m.groups())
    gm = float(need(t6, r"gmEA\s+Error amplifier gm\s+([\d.]+)\s+mS", "SNVSAI1D p.6 gmEA").group(1)) * 1e-3
    rout = float(need(t6, r"ROUT\s+Amplifier output resistance\s+([\d.]+)\s+M[\u03a9\u2126]", "SNVSAI1D p.6 ROUT").group(1)) * 1e6
    ibias = float(need(t6, r"IBIAS\(FB\)\s+Feedback pin input bias current\s+FB in regulation\s+([\d.]+)\s+nA", "SNVSAI1D p.6 IBIAS(FB)").group(1)) * 1e-9
    vcc_max = float(need(t6, r"VVCC\(VIN\)\s+Regulation voltage\s+VBIAS = 0 V, VCC open\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s+V", "SNVSAI1D p.6 VCC").group(1))
    vsns = tuple(float(x) for x in need(t7, r"VSNS\s+Average current loop regulation target\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "SNVSAI1D p.7 VSNS").groups())
    need(t5, r"TJ\s+Operating temperature\(2\)\s+\u201340\s+125", "SNVSAI1D p.5 TJ")
    for n in (9, 10, 11, 12):   # the typical characteristics: no plot of the reference against temperature
        tn = page(LM5176, n).replace("Submit Document Feedback", "")
        if re.search(r"(?i)reference|vref|feedback", tn):
            refuse("SNVSAI1D p.%d names the reference; the no-curve reading must be re-read" % n)
    iss = tuple(float(x) for x in need(t6, r"ISS\s+Soft-start pullup current\s+VSS = 0 V\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+\S*A",
                                        "SNVSAI1D p.6 ISS").groups())
    t11 = page(LM5176, 11)
    for fig in ("Figure 6-15. Load Step (Boost)", "Figure 6-16. Load Step (Buck-Boost)", "Figure 6-17. Load Step (Buck)",
                "Figure 6-18. Line Transient"):
        if fig not in t11:
            refuse("SNVSAI1D p.11 %s not found" % fig)
    divs = sorted(set(re.findall(r"(\d+ [\u00b5m]s)/div", t11)))
    out["ti"] = dict(vref=vref, gm=gm, rout=rout, ibias=ibias, vcc_max=vcc_max, vsns=vsns, iss=iss, divs=divs)
    b1 = page(BQ25731, 1)
    need(b1, r"±2\.5% Input current regulation", "SLUSE66A p.1 input current accuracy")
    b80 = page(BQ25731, 80)
    need(b80, r"Additional 100-mA \(10-mΩ sense", "SLUSE66A p.80 the 100 mA for the maximum")

    # temperatures
    env = yaml.safe_load(open(os.path.join(TOP, ENVELOPE), encoding="utf-8"))
    amb = env["ambient_c"]["in_use"]
    worst_in = env["worst_inside_air_c"]
    rise = env["inside_air_bounds_k"]["ps_idle_spec_lid_open"]
    dj = json.load(open(os.path.join(TOP, ANCHOR), encoding="utf-8"))
    t2m = [r["T2m"] for r in dj["outputs"]["daily_profile"] if r["month"] == 9]
    rise_lo = min(rise["independent"] + rise["design_record"])
    rise_hi = max(rise["independent"] + rise["design_record"])
    cases = [("the envelope, any in-use condition", amb["min"], max(worst_in["lid_open"], worst_in["lid_closed"]),
              "in-use ambient minimum %s C (the divider at the air before any warm-up, INFERRED) to the worst inside air in use "
              "%s C (lid closed; pcb_envelope.yaml worst_inside_air_c, itself INFERRED)" % (amb["min"], worst_in["lid_closed"])),
             ("M1 on the reference day", min(t2m) + rise_lo, max(t2m) + rise_hi,
              "the reference day's air %.2f to %.2f C (the 40/0 DRcalc T2m) plus PS-IDLE-SPEC's lid-open inside-air rise %.2f to "
              "%.2f K (pcb_envelope.yaml inside_air_bounds_k, both bounds; INFERRED, nothing measured)" % (min(t2m), max(t2m), rise_lo, rise_hi))]
    out["temps"] = cases

    # regulation error from the amplifier's finite DC gain (INFERRED from typical figures)
    a_dc = gm * rout
    reg = vcc_max / a_dc * (1 + R6_TOP / R7_BOT)
    out["reg"] = (a_dc, reg)
    ss_c = [comp[r]["value"] for r, pp in pins.items() if r != "U2" and any(v["net"] == "FE_SS" for v in pp.values())]
    if ss_c != ["4.7u"]:
        refuse("FE_SS is not one 4.7u capacitor")
    out["ss"] = (4.7e-6 * vref[1] / iss[2] * 1e6, 4.7e-6 * vref[1] / iss[0] * 1e6)

    # the bands
    rows = []
    for name, tmin, tmax, why in cases:
        dt = max(abs(tmin - T_REF), abs(tmax - T_REF))
        lo, hi = band(vref, 0.01, tcr6, tcr7, dt, ibias, reg)
        rows.append((name, tmin, tmax, dt, lo, hi, why))
    out["bands"] = rows
    out["nominal"] = vref[1] * (1 + R6_TOP / R7_BOT)
    out["printed_only"] = band(vref, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0)
    env = rows[0]
    dt_rise = max(abs(env[1] - T_REF), abs(env[2] + BOARD_RISE_K - T_REF))
    out["brackets"] = [
        ("the envelope with the divider %.0f K above the inside air (an ASSUMPTION: no layout)" % BOARD_RISE_K, dt_rise,
         band(vref, 0.01, tcr6, tcr7, dt_rise, ibias, reg)),
        ("the envelope with both resistors at their endurance limits (MAKER test limits, a bound)", env[3],
         band(vref, 0.01, tcr6, tcr7, env[3], ibias, reg, life6, life7)),
        ("both brackets together", dt_rise, band(vref, 0.01, tcr6, tcr7, dt_rise, ibias, reg, life6, life7))]
    # term by term at the envelope's temperature
    dt = rows[0][3]
    nom = out["nominal"]
    terms = []
    lo, hi = band(vref, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    terms.append(("VREF 0.788 / 0.800 / 0.812 V over TJ -40 to 125 C", lo - nom, hi - nom, "MAKER SNVSAI1D 6.5 p.6",
                  "part to part AND temperature: TI prints one band for both, and its typical characteristics (pp.9 to 12, read) plot no reference, so a unit may sit at either end at any temperature"))
    lo2, hi2 = band((0.8, 0.8, 0.8), 0.01, 0.0, 0.0, 0.0, 0.0, 0.0)
    terms.append(("R6 and R7 at 1 %, opposite directions", lo2 - nom, hi2 - nom, "MAKER YAGEO p.2 code F, UNI-ROYAL p.2 code F; NETLIST values",
                  "part to part: a fixed offset per unit"))
    lo3, hi3 = band((0.8, 0.8, 0.8), 0.0, tcr6, tcr7, dt, 0.0, 0.0)
    terms.append(("R6 and R7 TCR 100 ppm/K each over %.1f K from +25 C, opposite directions" % dt, lo3 - nom, hi3 - nom,
                  "MAKER YAGEO p.5 Table 2, UNI-ROYAL p.6; the direction INFERRED (no tracking figure)", "temperature: drifts with the divider's temperature"))
    terms.append(("IBIAS(FB) at most 25 nA through R6, either direction", -ibias * R6_TOP, ibias * R6_TOP, "MAKER SNVSAI1D p.6 (maximum; direction not stated)",
                  "part to part and temperature (a maximum over the range)"))
    terms.append(("the error amplifier's finite DC gain, COMP anywhere up to VCC's %.2f V maximum" % vcc_max, -reg, reg,
                  "INFERRED: gm %.2f mS x ROUT %.0f MOhm = %.0f (TYPICAL figures, p.6; TI prints no minimum)" % (gm * 1e3, rout / 1e6, a_dc),
                  "load and line: COMP moves with the current the loop asks for and with VIN; TI specifies no load or line regulation"))
    out["terms"] = terms
    # the front end's current limit against U3's input current
    tp_i = None
    tp = open(os.path.join(TOP, "v2/docs/records/a1elec/energy_two_pack.py"), encoding="utf-8").read()
    m = re.search(r'"u3_iin_draft_a": \(([\d.]+),', tp)
    m2 = re.search(r'"fe_r11_draft_mohm": \(([\d.]+),', tp)
    if not (m and m2):
        refuse("energy_two_pack.py's U3 limit or drafted R11 not found")
    tp_i, r11_draft = float(m.group(1)), float(m2.group(1)) * 1e-3
    r11_gen = 0.010
    out["cc"] = dict(gen=tuple(v * 1e-3 / r11_gen for v in vsns), draft=tuple(v * 1e-3 / r11_draft for v in vsns),
                     r11_draft=r11_draft, u3_nom=tp_i, u3_max=tp_i + 0.1)
    s120 = open(os.path.join(TOP, S120_OUT), encoding="utf-8").read()
    m = need(s120, r"(\d+\.\d{3}) to (\d+\.\d{3}) V\s+<- the DC band", "s120's DC band")
    out["s120"] = (float(m.group(1)), float(m.group(2)))
    return out


def main():
    o = compute()
    P = print
    P("VBUS20 AT U3'S INPUT, UNDER LOAD AND TEMPERATURE, FROM THE DESIGN AS GENERATED (vbus20_range.py second issue, stream")
    P("l3plane, MESHSAT-1357). PROTOTYPE DESIGN: desk arithmetic, nothing built, powered or measured. Basis per figure: MAKER (document,")
    P("page, read from its text layer here), NETLIST, or INFERRED (reason given).")
    P("")
    net, s16, facts = o["netlist"]
    P("1. THE CIRCUIT (NETLIST %s, sha256/16 %s)" % (net, s16))
    for name, ok, det in facts:
        P("   %-4s %-34s %s" % ("PASS" if ok else "FAIL", name, det))
    P("   So U2 regulates VBUS20 itself (R6's pin on VBUS20): R11's drop (FE_OUT to VBUS20) is INSIDE the loop and does not")
    P("   lower VBUS20. U3's VBUS pin and R16 sit on the same net; the copper between R6's tap and R16's pin carries U3's input")
    P("   current, and its resistance is a layout quantity.")
    P("")
    c6, c7, b6, b7, rd = o["ident"]
    P("2. R6 AND R7, THE PARTS")
    P("   the netlist carries no purchase code for either (fact 4); lcsc_fill.py's MAP (applied as that script applies it) gives")
    P("   R6 '240k 1%%' 0603 -> %s and R7 '10k 1%%' 0603 -> %s; the released A24 BOM rows read R6 %s and R7 %s (agree)" % (c6, c7, b6, b7))
    P("   R6 %s: YAGEO RC0603FR-07240KL (lcsc_fill.py's own comment; decoded on YAGEO p.2: F = 1 %%, R = paper reel, 07 = 7 inch" % c6)
    P("      reel and standard power, TCR 'based on spec'), %s sha256/16 %s, p.5 Table 2, RC0603 rows as read:" % (o["yageo"][0], o["yageo"][1]))
    for l in o["yageo"][2]:
        P("        | %s" % " ".join(l.split()))
    P("      -> RC0603, 1 %, 10 Ohm < R <= 10 MOhm: 100 ppm/K from +25 C (MAKER, YAGEO RC_L V.12 p.5 Table 2; p.8 t1 = +25 C)")
    P("   R7 %s: %s %s (LCSC reading %s: '%s', '%s'); decoded on UNI-ROYAL p.2: WA = 1/10 W, F = 1 %%" % (
        c7, rd["brand"], rd["model"], READING.split("/")[-1], rd["params"].get("Tolerance"), rd["params"].get("Temperature Coefficient")))
    P("      %s sha256/16 %s: %s" % o["uniroyal"])
    P("      -> 0603, R > 10 Ohm: 100 ppm/K from +25 C (MAKER, UNI-ROYAL V.3 p.6; the sheet is held back, not in the tree)")
    P("")
    ti = o["ti"]
    P("3. THE CONTROLLER (MAKER, TI SNVSAI1D, read here)")
    P("   VREF %.3f / %.3f / %.3f V at FB = COMP, limits over TJ -40 to 125 C (6.5 p.6; TJ -40 to 125 C recommended, 6.3 p.5)" % ti["vref"])
    P("   IBIAS(FB) %.0f nA maximum, FB in regulation (p.6); gmEA %.2f mS and ROUT %.0f MOhm, both TYPICAL only (p.6);" % (
        ti["ibias"] * 1e9, ti["gm"] * 1e3, ti["rout"] / 1e6))
    P("   VCC %.2f V maximum (p.6), the ceiling of COMP; no load or line regulation is specified anywhere in the sheet's tables" % ti["vcc_max"])
    P("   VSNS, the front end's own constant-current loop: %.0f / %.0f / %.0f mV (p.7)" % ti["vsns"])
    P("")
    P("4. THE KIT'S TEMPERATURE AT THE DIVIDER (the resistors' TCR runs from +25 C)")
    for name, tmin, tmax, dt, lo, hi, why in o["bands"]:
        P("   %-36s %+6.1f to %+6.1f C, the largest distance from +25 C %.1f K" % (name, tmin, tmax, dt))
        P("      %s" % why)
    P("   Board A's own local rise over the inside air near the divider is not established (no current layout): INFERRED zero.")
    P("")
    P("5. THE TERMS AT THE REGULATION POINT (R6's tap), the envelope's temperature, against the nominal %.3f V" % o["nominal"])
    P("   %-78s %8s %8s   %s" % ("term", "low, V", "high, V", "basis; kind"))
    for name, lo, hi, basis, kind in o["terms"]:
        P("   %-78s %+8.3f %+8.3f   %s; %s" % (name, lo, hi, basis, kind))
    a_dc, reg = o["reg"]
    P("")
    P("6. THE STEADY-STATE RANGE (min, nominal, max) at the regulation point, all terms together (tolerance and TCR opposite on")
    P("   R6 and R7)")
    P("   the printed figures alone (VREF and 1 %%): %.3f to %.3f V" % o["printed_only"])
    for name, tmin, tmax, dt, lo, hi, why in o["bands"]:
        P("   %-36s min %.3f V, nominal %.3f V, max %.3f V" % (name, lo, o["nominal"], hi))
    P("   stream s120's band (65 K of TCR assumed, no amplifier term): %.3f to %.3f V" % o["s120"])
    P("   BRACKETS beside the range (not in it):")
    for name, dt, (lo, hi) in o["brackets"]:
        P("   %-86s min %.3f V, max %.3f V (%.1f K)" % (name, lo, hi, dt))
    P("   The endurance limits (YAGEO p.8: +-(1 % + 50 mOhm) after 1000 h at 70 C at rated voltage; UNI-ROYAL p.7: +-(1.0 % +")
    P("   0.05 Ohm) after 1000 h at 70 C) are test limits at far more stress than the divider sees (about %.0f uA): a bound, not an" % (
        o["nominal"] / (R6_TOP + R7_BOT) * 1e6))
    P("   expectation. The divider's rise is an assumption until board A is laid out; it warms the hot end only (at the cold end the")
    P("   board starts unpowered at the air), which is why it adds %.1f K and not its full %.0f K to the envelope's %.1f K." % (
        o["brackets"][0][1] - o["bands"][0][3], BOARD_RISE_K, o["bands"][0][3]))
    P("   Not steady state, and outside the range: the soft start (C7 4.7 uF on FE_SS, NETLIST, charged at ISS %.2f / %.0f / %.2f uA" % o["ti"]["iss"])
    P("   to the %.1f V reference, SNVSAI1D p.6: %.2f to %.2f s after each enable); load steps and line transients (TI Figures 6-15" % (
        o["ti"]["vref"][1], o["ss"][0], o["ss"][1]))
    P("   to 6-18, p.11, plotted at %s per division); neither moves an hourly energy balance. Not established: the ground offset" % " and ".join(o["ti"]["divs"]))
    P("   between R7's return and U2's AGND, a layout term like the copper to R16.")
    P("")
    cc = o["cc"]
    P("7. UNDER LOAD: U3'S INPUT CURRENT AGAINST THE FRONT END'S CURRENT LIMIT, AND THE COPPER")
    P("   U3's IIN_HOST %.1f A nominal, %.1f A maximum (energy_two_pack.py PAR u3_iin_draft_a; SLUSE66A 9.6.22 p.80, which gives" % (cc["u3_nom"], cc["u3_max"]))
    P("   only the maximum). Its MINIMUM is not printed for the 10 mOhm sense: the energy records take 6.1 A (INFERRED, the maximum's")
    P("   100 mA mirrored) with 6.0 A as a bracket; SLUSE66A's front page (p.1) states +-2.5 % input current regulation, which")
    P("   gives %.3f A at the %.1f A setting, inside that bracket." % (cc["u3_nom"] * 0.975, cc["u3_nom"]))
    P("   As generated, R11 10 mOhm: the front end's constant-current loop holds %.2f / %.2f / %.2f A (VSNS over R11, MAKER p.7 with" % cc["gen"])
    P("   NETLIST R11): below U3's %.1f A, so at U3's full input current THE BUS IS NOT IN VOLTAGE REGULATION as generated: the" % cc["u3_nom"])
    P("   front end limits its current and VBUS20 falls below the band until the charger's input loops settle (energy_two_pack")
    P("   entry E1 is that regime, U3 held at 4.15 A, whose 4.25 A maximum sits only 50 mA under the front end's 4.30 A minimum,")
    P("   and R11 also carries the VBUS20 currents that do not pass R16: U2's BIAS, R197, the divider; not quantified, and they")
    P("   can only make E1 worse). Every Option A(i) figure uses entry E2, the DRAFTED re-rate R11 %.1f mOhm" % (cc["r11_draft"] * 1e3))
    P("   (a1elec TOPOLOGY.md 7; not in the generator): %.2f / %.2f / %.2f A, above U3's %.1f A maximum, so the bus stays in" % (cc["draft"] + (cc["u3_max"],)))
    P("   voltage regulation and the range above applies at the regulation point.")
    P("   The copper from R6's tap to R16's pin: NOT ESTABLISHED (board A's routed file is of 15 September, A32, and predates the")
    P("   netlist read here). Each 1 mOhm of it lowers U3's input by %.1f mV at %.1f A (0.03 %% of the bus), load-proportional." % (cc["u3_max"], cc["u3_max"]))
    P("   The resistors' long-term drift is not in the range: it is the endurance bracket of section 6.")
    P("")
    P("8. THE KINDS: part to part (a fixed offset per unit): the resistors' 1 % and, as far as TI says anything, VREF's band;")
    P("   temperature: the resistors' TCR (and any part of VREF's band TI does not separate); load and line: the amplifier's finite")
    P("   gain and the copper to R16. The first two dominate: VREF %.1f %% and the ratio's 1 %% pair about %.1f %%; TCR at most %.1f %%." % (
        (ti["vref"][1] - ti["vref"][0]) / ti["vref"][1] * 100, (o["terms"][1][2] - o["terms"][1][1]) / 2 / o["nominal"] * 100,
        (o["terms"][2][2] - o["terms"][2][1]) / 2 / o["nominal"] * 100))
    P("")
    P("END. Desk figures on the makers' pages and the committed netlist; nothing is measured.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
