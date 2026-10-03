#!/usr/bin/env python3
"""l4e13_panel.py: layer 4 task L4-E13 (MESHSAT-1357, 2 October 2026; second fix round after the recheck astra-check-l4e13-2):
U-03, a solar panel whose open-circuit voltage is bounded at the coldest operating temperature inside REQ-016's window, by its
MAKER's document (route 1) or by the measurement of ONE identified unit (route 2, PANEL-ACC), with the disturbance check
judged apart from the window as REQ-016 directs ("Protection is judged apart from the window, under rule TRN-001").

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured, and no physical unit is accepted. No
generator, registry, Layer 3 file or other record is edited. For each candidate panel (the present one, SunPower's
SPR-E-Flex-100, and at most two more) this script reads the maker's printed rows from the pinned document and prints:
  - THE WINDOW (normal operation, REQ-016's rated quantity): the makers' rated Voc row, defined at 1000 W/m2, moved to
    REQ-024's coldest in-use temperature (-20 C); route 1 reads each maker's printed band there, the coefficient both ways (a
    scenario and an extrapolation, neither warranted); a band the maker does not print is not invented (NOT BOUNDED); and the
    band a maker would have to warrant (the clarification drafts ask for it);
  - the panel against the input hold of board E's stage (L4-E7's selected settings: 17.593 V nominal, 16.970 / 18.221 V with
    EA3 at its typical gain, 16.420 / 18.813 V the widest conditioned band), the energy into the stage on SC-37's mean
    September day at every hold corner, the power against REQ-016's 100 W, the hot short-circuit current, and the panel's
    portable class from its own document;
  - ROUTE 2, PANEL-ACC: the measurements on one identified unit and their specification; A-1, the window, Vm20 + U_V at or
    under 25.000 V; A-2, the useful charging power measured at the noon corner on the conservative side, P - U_P strictly above
    the stage's own drive power over its efficiency, with the model's signs showing the offsets conservative; A-3, the entry,
    in three cases (normal operation under L4-E7's limit, a sustained input fault with the maker's 1.25 allowance, the
    enhancement transient during a fault as a downstream connector row); A-4, the 100 W on L4-E7's limit; demonstrated on a
    unit equal to the typical rows, with the window of measured values and A1 and A2 (the replay's own meanday and least);
  - THE DISTURBANCE CHECK: D4's standoff against a unit at A-1's ceiling under an irradiance burst on cold cells, bounded by
    junction physics (n_max = 2, a modelling assumption M3 verifies), with the coldest cells shown to be the worst case and the
    irradiance threshold below which A-1 implies it; no irradiance maximum is a decision input;
  - the classification of U-03 by a predicate that admits either route, and the downstream item.

The model is the energy record's, not a new one: l4e_replay.main() runs here with its locals captured and must print
l4e_replay.out byte for byte; this script's trace must equal the replay's trace hour for hour on the SunPower panel, its
day sums must equal the replay's section 12 and L4-E7's section 5 at every hold printed there, and A1 and A2 on the SunPower
trace at L4-E7's nominal hold and limit must equal L4-E7's printed rows (exit 4 otherwise).

Evidence classes: MAKER (a maker's document, page named), MAKER-PAGE (a maker's web page, transcribed and filed), RECORD (a
committed output read by pattern), LITERATURE (a quoted open-access paper, context only), MODELED (the energy record's model),
INFERRED (arithmetic on the above with a stated step), ASSUMPTION (a figure no document gives, physical constants included),
MODELLING_ASSUMPTION (n_max), COMPONENT_LIMITATION (a rating no held document prints), SESSION (a reading or choice this
record takes, with its reason).

Run from the repository root:  python3 v2/docs/records/l4e13/l4e13_panel.py > v2/docs/records/l4e13/l4e13_panel.out
Needs pdftotext and PyYAML (through the replay). About a minute and a half (most of it the replay). The held documents are
fetched by v2/docs/records/a1solar/fetch_held_back.py (SunPower) and v2/docs/records/l4e13/fetch_held_back.py (Solbian).
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction or a predicate failed."""
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
try:
    os.nice(10)                 # a shared host: stay behind interactive work
except OSError:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()

PINS = {
    "reqs": ("v2/ecad/tools/pcb_requirements.yaml", "b624ac495650a3592c45a37610375fb05bf7b775042cf3de7ec8979bc46a6e50"),
    "env": ("v2/ecad/tools/pcb_envelope.yaml", "35cf43a2b7098a76abb4919685ece4d6e352331628f5f242c1492d9fcbbf2864"),
    "replay_py": ("v2/docs/records/l4e/l4e_replay.py", "3de985e2e3e06453d2c9d576311c1f39935149ac1e9b7cff0431a40933bb8734"),
    "replay_out": ("v2/docs/records/l4e/l4e_replay.out", "59c6eeab16da98f8ddf16880ddcdc1d2a2c910f4256be9b69aade49dd4d2726d"),
    "l4e7_out": ("v2/docs/records/l4e7/l4e7_stage_settings.out", "8d5e8191e5938a7682349bcca2fc366642ee8704637ed98e2879312ace4215e3"),
    "array_calc": ("v2/docs/records/a1solar/array_calc.py", "fdeaf63f525f1d7f4ca54502083369cfd4f322a41207ff0a52582c27038fd1e4"),
    "spr_ds": ("v2/vendor/solar/held/sunpower-spr-e-flex-100-datasheet-523809-revd.pdf",
               "da06e5e2d9bca625f54a756105e009950a2352e4764868853cb26921372ff605"),
    "spr_guide": ("v2/vendor/solar/held/sunpower-flex-safety-installation-524958-revf.pdf",
                  "b8ebdfb7019a399accd75e564a4a764eed565f7066dfd25b131fe65365ec6dd9"),
    "sbx_ds": ("v2/vendor/solar/held/solbian-sx-series-datasheet-eng-2023-02.pdf",
               "da89757253556a9d807c6e0c6848f079fbd1d81c1f6422bd211cab7e33e1c12c"),
    "bgv_page": ("v2/vendor/solar/bougerv-sp001-100w-n-type-foldable-product-page-2026-10-02.md",
                 "fc9de44fa8149c70e166823ed591093bf971a44eafb7b833a74087f1aff8c658"),
    "screen": ("v2/docs/records/l4e13/inputs/screen-2026-10-02.json",
               "bdf17c68de48f8f85a1177bc8814f890224e310c42a0ffc3cc5c76eb0f1fcb5c"),
    "smcj": ("v2/vendor/power/littelfuse-smcj-series-tvs.pdf", "6e610db955ed876306999009c62b242f7de9bb05e2cd9717288a96586a5093ea"),
    "vh": ("v2/vendor/connectors/jst-vh-catalogue.pdf", "d51e669c597988b20c0963daf5bef7356cbd2104c1f867e9107c6fa6cd2b899c"),
    "enh": ("v2/vendor/solar/irradiance-enhancement-sources-2026-10-02.md",
            "e33b0a05c27f67635f7537ad6ba4b9b85623427e99550c4e9343c24bb91903a5"),
}

# The few figures and readings this record sets itself (each named where it is used)
G_STC = 1000.0        # STC irradiance, W/m2: the makers' rated Voc row is defined at it, and so is THE WINDOW (REQ-016's rated
                      # quantity: the open-circuit voltage at 1000 W/m2, moved to the coldest operating temperature, -20 C)
S0 = 1361.0           # ASSUMPTION (a physical constant): the total solar irradiance at one astronomical unit, W/m2
ECC = 0.0167          # ASSUMPTION (a physical constant): the eccentricity of the Earth's orbit; S0 / (1 - ECC)^2 is the
                      # extraterrestrial irradiance at perihelion, E0. CONTEXT only (and the base of A-3(c)'s design level):
                      # no irradiance maximum is an input to the window or to the disturbance check
N_MAX = 2.0           # MODELLING_ASSUMPTION: the ideality ceiling of a silicon junction (n = 1 for diffusion current, n = 2 for
                      # recombination in the depletion region; a module's n lies between them); M3's measured n must read at or
                      # under it, else the disturbance check is re-judged
N_SENS = 3.0          # a sensitivity row of the disturbance check only
T_ISC_HOT = 70.0      # a1solar's convention for the hot short-circuit current (array_calc.T_HOT): cells at +70 C, 1000 W/m2
# PANEL-ACC's measurement specification (SESSION: requirements on the Layer 6 measurement, not a claim about a laboratory;
# the laboratory states its own expanded uncertainties, k = 2, and each must be at or under these)
SPEC_UV = 0.10        # V: on each voltage: M2's Voc at -20 C (the cell temperature's own 1 K, about 0.06 V here, inside it)
                      # and A-2's voltage point
SPEC_TM = 1.0         # K: M2's cell temperature within -20 +- 1 C
SPEC_UA = 0.10        # M3's irradiance slope A25 = dVoc / d ln G at 25 C: a fraction of the slope (it gives the measured n)
SPEC_UI = 0.02        # a current reading (Isc at STC; A-2's current): a fraction of the reading
SPEC_UG = 0.02        # A-2's irradiance setting: a fraction of the setting (the lab sets at or under 520.7 W/m2 minus it)
SPEC_UTC = 1.0        # K: A-2's cell temperature (the lab sets at or above 35.65 C plus it)
K_CLAUSE = 1.25       # SunPower 524958 Rev F 3.0's multiplier of Isc and Voc for component ratings (the one such clause held)
DAY_FRACTION = 0.05   # SESSION: the day's maximum-power voltage band is read over the hours with at least 5 % of the peak irradiance
ENTRY_A = 10.0        # REQ-016's acceptance: F2 and J_SOLAR rated 10 A
PORTABLE_KG = 2.5     # SESSION: "portable" is a flexible or folding class at or under 2.5 kg (the 100 Wp class weighs about 2 kg;
                      # the registry carries no owner ruling on a panel's class or mass)
# a panel-class word beside "panel" or "array" in one sentence (a bare "blanket" also means "blanket approval", D-26)
PANEL_CLASS = re.compile(r"(?i)\b(foldable|folding|flexible|semi-rigid|blanket)\b[^.]{0,60}\b(panel|array)s?\b|"
                         r"\b(panel|array)s?\b[^.]{0,60}\b(foldable|folding|flexible|semi-rigid|blanket)\b")
CLASSES = ("MAKER", "MAKER-PAGE", "RECORD", "LITERATURE", "MODELED", "INFERRED", "ASSUMPTION", "MODELLING_ASSUMPTION",
           "COMPONENT_LIMITATION", "SESSION")


def classify(route1, route2):
    """U-03's classification (the check's B2): either route takes it downstream; only when neither stands is it open."""
    if route1:
        return "DOWNSTREAM PURCHASE (maker-bound)"
    if route2:
        return "CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC)"
    return "OPEN (architecture-level)"


def refuse(code, msg):
    sys.stderr.write("l4e13_panel: %s; refusing\n" % msg)
    sys.exit(code)


def sha_of(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def need(text, pat, what, flags=re.M):
    m = re.search(pat, text, flags)
    if not m:
        refuse(3, "%s not parsed" % what)
    return m


def pdf_page(rel, n):
    r = subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), os.path.join(TOP, rel), "-"], capture_output=True, text=True)
    if r.returncode != 0:
        refuse(3, "pdftotext could not read %s p.%d" % (rel, n))
    return r.stdout


def flat(s):
    return " ".join(s.split())


def load(name, rel):
    sp = importlib.util.spec_from_file_location(name, os.path.join(TOP, rel))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def run_main_captured(m):
    """Run m.main() with stdout captured and its locals taken at its return (CPython's profile hook), as L4-E4 and L4-E7 do."""
    cap = {}

    def prof(frame, event, _arg):
        if event == "return" and frame.f_code is m.main.__code__:
            cap.update(frame.f_locals)
    buf = io.StringIO()
    old = sys.getprofile()
    sys.setprofile(prof)
    try:
        with contextlib.redirect_stdout(buf):
            rc = m.main()
    finally:
        sys.setprofile(old)
    return rc, buf.getvalue(), cap


def fnum(s):
    return float(s.replace(",", "."))


# ====================================================================================== the makers' rows, read back
def read_sunpower():
    t = pdf_page(PINS["spr_ds"][0], 1)
    ft = flat(t)
    c = {"key": "SPR", "name": "SunPower SPR-E-Flex-100", "maker": "SunPower Corporation"}
    c["p"] = float(need(t, r"Nominal Power \(Pnom\)\s+(\d+) W", "SunPower Pnom").group(1))
    tol = need(t, r"Power Tolerance\s+\+(\d+)/[\u2013-](\d+)%", "SunPower power tolerance").groups()
    c["p_tol"] = (-float(tol[1]) / 100.0, float(tol[0]) / 100.0)
    c["vmp"] = float(need(t, r"Rated Voltage \(Vmpp\)\s+([\d.]+) V", "SunPower Vmpp").group(1))
    c["imp"] = float(need(t, r"Rated Current \(Impp\)\s+([\d.]+) A", "SunPower Impp").group(1))
    c["voc"] = float(need(t, r"Open-circuit voltage \(Voc\)\s+([\d.]+) V", "SunPower Voc").group(1))
    c["isc"] = float(need(t, r"Short-curcuit current \(Isc\)\s+([\d.]+) A", "SunPower Isc").group(1))
    c["beta_voc_abs"] = -1e-3 * float(need(t, r"Voltage Temp Coefficient\s+[\u2013-]([\d.]+) mV", "SunPower Voc coefficient").group(1))
    c["alpha_isc_abs"] = 1e-3 * float(need(t, r"Current Temp Coefficient\s+([\d.]+) mA", "SunPower Isc coefficient").group(1))
    c["gamma_p"] = -1e-2 * float(need(t, r"Power Temp Coeffiecient\s+[\u2013-]([\d.]+)%", "SunPower Pmax coefficient").group(1))
    c["cells"] = int(need(t, r"(\d+) Prime monocrystalline", "SunPower cells").group(1))
    c["mass"] = float(need(t, r"\((\d+(?:\.\d+)?) kg\)", "SunPower mass").group(1))
    c["size"] = "%s with the junction box, %s without" % (need(ft, r"(\d+ x \d+ x \d+ mm)", "SunPower size").group(1),
                                                          need(ft, r"with Jbox, (\d+ mm) w/o Jbox", "SunPower thickness").group(1))
    c["typical"] = "Typical Electrical Data" in ft
    c["stc"] = need(ft, r"at STC: (25\S*C, 1000 W/m\S* and AM 1\.5)", "SunPower STC line").group(1)
    g3 = flat(pdf_page(PINS["spr_guide"][0], 3))
    if "Table 1: Electrical Characteristics" not in g3 or "SPR-E-Flex-100" not in g3 or "Page | 2" not in g3:
        refuse(3, "SunPower's guide 524958 Rev F p.3 is not Table 1 as read")
    c["qual"] = need(g3, r"(Rated electrical characteristics are within (\d+)% of measured values at Standard Test Conditions of: "
                         r".*?spectrum\.)", "SunPower's 10 % sentence").group(1)
    c["qual_pct"] = float(need(c["qual"], r"within (\d+)%", "the qualification's percentage").group(1)) / 100.0
    g4 = flat(pdf_page(PINS["spr_guide"][0], 4))
    m = need(g4, r"[\u2010-]40\S* C to \+85\S* C", "SunPower operating range")
    c["t_range"] = (-40.0, 85.0) if m else None
    c["noct"] = None
    c["class"] = "semi-flexible laminate (flexing up to 30 degrees), carried flat; not folding"
    c["doc"] = ("v2/vendor/solar/held/sunpower-spr-e-flex-100-datasheet-523809-revd.pdf p.1 (Document 523809 Rev D, a distributor's "
                "issue of January 2023, 'Typical Electrical Data'); v2/vendor/solar/held/sunpower-flex-safety-installation-524958-revf.pdf "
                "Table 1 and its note (PDF p.3, printed p.2), 5.1 (PDF p.4)")
    c["evidence"] = "MAKER"
    return c


def read_solbian():
    t2 = pdf_page(PINS["sbx_ds"][0], 2)
    t1 = flat(pdf_page(PINS["sbx_ds"][0], 1))
    lines = t2.split("\n")
    head = [i for i, ln in enumerate(lines) if re.match(r"\s+SX 236\s{2,}SX 176 L", ln)]
    if len(head) != 1:
        refuse(3, "Solbian's SX table header not found once")
    cols = [x for x in re.split(r"\s{2,}", lines[head[0]].strip())]
    if "SX 156" not in cols:
        refuse(3, "Solbian's SX table has no SX 156 column")
    ci = cols.index("SX 156")
    rows = {}
    for ln in lines[head[0] + 1:]:
        parts = re.split(r"\s{2,}", ln.strip())
        if len(parts) == len(cols) + 1:
            rows[parts[0]] = parts[1:]
    def cell(label):
        if label not in rows:
            refuse(3, "Solbian's SX row %r not parsed" % label)
        return rows[label][ci]
    c = {"key": "SBX", "name": "Solbian SX 156", "maker": "Solbian Energie Alternative Srl"}
    c["p"] = fnum(cell("Maximum power [W]"))
    c["vmp"] = fnum(cell("Max power Voltage Vmp [V]"))
    c["imp"] = fnum(cell("Max power Current Imp [A]"))
    c["voc"] = fnum(cell("Open circuit voltage Voc [V]"))
    c["isc"] = fnum(cell("Short circuit current Isc [A]"))
    c["beta_voc"] = fnum(cell("Temp. coeff. Voc [%/°C]")) / 100.0
    c["alpha_isc"] = fnum(cell("Temp. coeff. Isc [%/°C]")) / 100.0
    c["gamma_p"] = fnum(cell("Temp. coeff. Pmax [%/°C]")) / 100.0
    noct = re.match(r"(\d+) ± (\d+)", cell("NOCT [°C]"))
    if not noct:
        refuse(3, "Solbian's NOCT not parsed")
    c["noct_row"] = (float(noct.group(1)), float(noct.group(2)))
    c["noct"] = c["noct_row"][0] + c["noct_row"][1]
    op = re.match(r"(-?\d+)/\+(\d+)", cell("Operating temperature [°C]"))
    c["t_range"] = (float(op.group(1)), float(op.group(2)))
    c["cells"] = int(re.search(r"\((\d+)\)", cell("Columns x Rows (cells n°)")).group(1))
    c["mass"] = fnum(cell("Weight [kg]"))
    c["size"] = "%s x %s x %s mm" % (cell("Length Y [mm]"), cell("Width X [mm]"), cell("Thickness [mm]"))
    m = need(t1, r"Positive power tolerance \((\d+)%, \+(\d+)%\)", "Solbian power tolerance")
    c["p_tol"] = (float(m.group(1)) / 100.0, float(m.group(2)) / 100.0)
    c["stc"] = need(flat(t2), r"\* (Values at STC = Standard Test Conditions: .*?cell temperature of 25 °C\.)", "Solbian STC note").group(1)
    c["iec_note"] = "Measurements carried out according to the Standard IEC 61215 requirements." in flat(t2) or \
        "Measurements carried out according to the Standard IEC 61215 requirements" in flat(t2)
    c["voc_tol_printed"] = bool(re.search(r"(?i)tolerance[^.]{0,40}(Voc|open circuit)|(Voc|open circuit)[^.]{0,40}toleran",
                                          flat(t1) + " " + flat(t2)))
    c["typical"] = False
    c["class"] = "flexible laminate under 2 mm (2.4 kg/m2, the sheet's p.1), carried flat or curved; not folding"
    c["doc"] = ("v2/vendor/solar/held/solbian-sx-series-datasheet-eng-2023-02.pdf p.2 (the SX table, the SX 156 column, and its STC "
                "note) and p.1 (the features list); created 7 February 2023")
    c["evidence"] = "MAKER"
    return c


def read_bougerv():
    t = open(os.path.join(TOP, PINS["bgv_page"][0]), encoding="utf-8").read()
    blk = need(t, r"```\n(.*?)```", "the BougeRV transcription block", re.S).group(1)
    row = {}
    for ln in blk.strip().split("\n"):
        k, _, v = ln.partition(": ")
        row[k.strip()] = v.strip()

    def tolv(k, unit):
        m = re.fullmatch(r"([\d.]+)%s\(([+-]\d+)%%,([+-]\d+)%%\)" % unit, row[k])
        if not m:
            refuse(3, "BougeRV row %r not parsed" % k)
        return float(m.group(1)), float(m.group(2)) / 100.0, float(m.group(3)) / 100.0
    c = {"key": "BGV", "name": "BougeRV 100W N-Type Fiberglass Foldable (SP001-BK-GRUSGA)", "maker": "BougeRV"}
    c["p"], lo_p, hi_p = tolv("Max Power (Pmax)", "W")
    c["p_tol"] = (lo_p, hi_p)
    c["vmp"], lo1, hi1 = tolv("Max. Power Voltage Vmp (V)", "V")
    c["imp"], _a, _b = tolv("Max. Power Current Imp (A)", "A")
    c["voc"], lo, hi = tolv("Open Circuit Voltage Voc (V)", "V")
    c["isc"], ilo, ihi = tolv("Short Circuit Current (Isc)", "A")
    if (lo, hi) != (lo1, hi1) or (lo, hi) != (ilo, ihi):
        refuse(3, "the BougeRV rows' bands differ")
    c["voc_band"] = (lo, hi)
    c["beta_voc"] = float(need(row["Temperature Coefficient Voc"], r"^(-[\d.]+)%/", "BougeRV Voc coefficient").group(1)) / 100.0
    c["alpha_isc"] = float(need(row["Temperature Coefficient Isc"], r"^\+([\d.]+)%/", "BougeRV Isc coefficient").group(1)) / 100.0
    c["gamma_p"] = float(need(row["Temperature Coefficient Pmax"], r"^(-[\d.]+)%/", "BougeRV Pmax coefficient").group(1)) / 100.0
    op = need(row["Operating Temperature Limits"], r"^(-?\d+)\S+ ~ \+(\d+)\S+$", "BougeRV operating limits")
    f2c = lambda f: (float(f) - 32.0) * 5.0 / 9.0
    c["t_range"] = (round(f2c(op.group(1)), 1), round(f2c(op.group(2)), 1))
    c["mass"] = round(float(need(row["Weight"], r"^([\d.]+) lbs$", "BougeRV weight").group(1)) * 0.45359237, 2)
    fold = [float(x) * 25.4 for x in need(row["Dimensions(Folded)"], r"^([\d.]+)\*([\d.]+)\*([\d.]+) inches$", "folded").groups()]
    unf = [float(x) * 25.4 for x in need(row["Dimensions(Unfolded)"], r"^([\d.]+)\*([\d.]+)\*([\d.]+) inches$", "unfolded").groups()]
    c["size"] = "%.0f x %.0f x %.0f mm open, %.0f x %.0f x %.0f mm folded" % tuple(unf + fold)
    c["fuse_row"] = row["Series Fuse Rating"]
    c["cells"] = None
    c["noct"] = None
    c["stc"] = None
    c["typical"] = False
    c["class"] = "folding (fiberglass), carried folded"
    c["doc"] = ("v2/vendor/solar/bougerv-sp001-100w-n-type-foldable-product-page-2026-10-02.md (the maker's product page, its "
                "'Product Specifications' table transcribed; the page's HTML sha256 ffc8cf99..., fetched 2026-10-02T04:28Z)")
    c["evidence"] = "MAKER-PAGE"
    return c


# ====================================================================================== the computation
def compute():
    for key, (rel, want) in PINS.items():
        p = os.path.join(TOP, rel)
        if not os.path.exists(p):
            refuse(2, "%s is missing%s" % (rel, " (fetch it: see this script's docstring)" if "/held/" in rel else ""))
        if sha_of(rel) != want:
            refuse(2, "%s is not the pinned file" % rel)
    R = {"notes": []}
    # ---------------------------------------------------------------- the requirement, the temperature
    reqs = open(os.path.join(TOP, PINS["reqs"][0]), encoding="utf-8").read()
    r016 = need(reqs, r"\n  - id: REQ-016\n(.*?)(?=\n  - id: )", "REQ-016", re.S).group(1)
    st016 = flat(need(r016, r"statement: >-\n(.*?)\n    acceptance:", "REQ-016's statement", re.S).group(1))
    acc016 = flat(need(r016, r"acceptance: >-\n(.*?)\n    allocated_to:", "REQ-016's acceptance", re.S).group(1))
    R["req016"] = st016
    R["v_oc"] = float(need(st016, r"an open-circuit voltage of at most ([\d.]+) V at the panel's coldest operating temperature",
                           "REQ-016's 25 V").group(1))
    R["v_hold_req"] = float(need(st016, r"held at ([\d.]+) V by the stage's input regulation", "REQ-016's hold").group(1))
    R["p_win"] = float(need(st016, r"at most ([\d.]+) W into the stage", "REQ-016's 100 W").group(1))
    R["entry_a"] = float(need(acc016, r"F2 and connector J_SOLAR are rated ([\d.]+) A", "REQ-016's entry rating").group(1))
    if R["entry_a"] != ENTRY_A:
        refuse(3, "REQ-016's entry rating is not %.0f A" % ENTRY_A)
    # does REQ-016 admit a series element or clamp in place of the panel's own open circuit? (read, not assumed)
    R["series_admitted"] = bool(re.search(r"(?i)series diode|blocking diode|unless|or a clamp|in place of the panel", st016))
    r024 = need(reqs, r"\n  - id: REQ-024\n(.*?)(?=\n  - id: )", "REQ-024", re.S).group(1)
    st024 = flat(need(r024, r"statement: >-\n(.*?)\n    acceptance:", "REQ-024's statement", re.S).group(1))
    R["req024_range"] = need(st024, r"operates at (-?\d+) to \+(\d+) C ambient", "REQ-024's range").groups()
    env = open(os.path.join(TOP, PINS["env"][0]), encoding="utf-8").read()
    m = need(env, r"in_use: \{min: (-?\d+), max: (\d+)\}", "the envelope's in-use range")
    R["t_cold"], R["t_hot_amb"] = float(m.group(1)), float(m.group(2))
    if (R["t_cold"], R["t_hot_amb"]) != tuple(float(x) for x in R["req024_range"]):
        refuse(3, "REQ-024 and pcb_envelope.yaml disagree on the in-use range")
    # owner rulings on the panel's class in the registry (read, not assumed)
    own = []
    for mm in re.finditer(r"\n  - id: (\S+)\n(.*?)(?=\n  - id: |\Z)", reqs, re.S):
        if "authority: OWNER" in mm.group(2) and PANEL_CLASS.search(flat(mm.group(2))):
            own.append(mm.group(1))
    R["owner_panel_rulings"] = own

    # ---------------------------------------------------------------- the stage's hold and limit (RECORD)
    o7 = open(os.path.join(TOP, PINS["l4e7_out"][0]), encoding="utf-8").read()
    typ = need(o7, r"EA3 at its typical 90 V/V:\s+([\d.]+) / ([\d.]+) / ([\d.]+) V", "L4-E7's typical band").groups()
    cond = need(o7, r"EA3 at half, soldering and life drifts:\s+([\d.]+) / ([\d.]+) V \(the widest conditioned band\)",
                "L4-E7's conditioned band").groups()
    R["hold_typ"] = tuple(float(x) for x in typ)
    R["hold_cond"] = (float(cond[0]), float(cond[1]))
    R["i_set"] = float(need(o7, r"ACHIEVED SETTING: .*? = ([\d.]+) A", "L4-E7's setting").group(1))
    lowm = need(o7, r"setting %s A, hold %.3f V: lowest ([\d.]+) A, above (\d+) W/m2" % (re.escape("%.4f" % R["i_set"]), R["hold_typ"][1]),
                "L4-E7's lowest limit at the nominal hold")
    R["i_low"], R["g_bind_spr"] = float(lowm.group(1)), float(lowm.group(2))
    l7e = {}
    for mm in re.finditer(r"^\s+(lower hold corner|nominal hold|upper hold corner|lower, EA3 at its floor|upper, EA3 at its floor|"
                          r"lower, EA3 floor, drifts|upper, EA3 floor, drifts)\s+([\d.]+) V\s+([\d.]+) \|", o7, re.M):
        l7e[round(float(mm.group(2)), 3)] = float(mm.group(3))
    if len(l7e) != 7:
        refuse(3, "L4-E7's section 5 energy rows not parsed")
    l7runs = {}
    for mm in re.finditer(r"NEW nominal \(hold ([\d.]+) V, limit ([\d.]+) A\), (A1|A2): ([\d.]+) Wh a day; first interruption h (\d+)/(\d+); "
                          r"unserved ([\d.]+) / ([\d.]+) at 48 h, ([\d.]+) / ([\d.]+) at 72 h; least addition \+([\d.]+) / \+([\d.]+) Wh", o7):
        l7runs[mm.group(3)] = mm.groups()
    if set(l7runs) != {"A1", "A2"}:
        refuse(3, "L4-E7's NEW nominal A1 and A2 rows not parsed")
    ro = open(os.path.join(TOP, PINS["replay_out"][0]), encoding="utf-8").read()
    leg = need(ro, r"the hold spans ([\d.]+) / ([\d.]+) / ([\d.]+) V", "the replay's legacy band").groups()
    R["hold_legacy"] = tuple(float(x) for x in leg)
    rl12 = {}
    for mm in re.finditer(r"^\s+(lower hold corner|nominal hold|upper hold corner)\s+([\d.]+) V, no input limit \(as drawn\)\s+([\d.]+) Wh", ro, re.M):
        rl12[round(float(mm.group(2)), 3)] = float(mm.group(3))
    R["e_mpp_spr_rec"] = float(need(ro, r"At the maximum-power point the day gives ([\d.]+) Wh \(PVGIS\)", "the replay's MPP day").group(1))
    R["stimulus"] = float(need(ro, r"([\d.]+) Wh at 100 W, clipped in \d+ hours", "the replay's 100 W stimulus").group(1))
    # the stage's own drive and quiescent power (L4-E7, INFERRED there) and the stage's declared efficiency (the replay):
    # below their quotient at its input the stage delivers no net charge, so "useful" power is strictly above it
    fx = need(o7, r"4\.2 mA: ([\d.]+) mA, ([\d.]+) W, TJ estimated", "L4-E7's stage drive power")
    R["p_fixed"], R["i_fixed_ma"] = float(fx.group(2)), float(fx.group(1))
    R["eta_stage"] = float(need(ro, r"stage ([\d.]+), front end", "the replay's stage efficiency").group(1))
    R["p_use"] = R["p_fixed"] / R["eta_stage"]
    # the irradiance envelope: the read source's enhancement on the extraterrestrial irradiance at perihelion
    enh = open(os.path.join(TOP, PINS["enh"][0]), encoding="utf-8").read()
    R["enh_quote"] = need(enh, r"(In cloud fields with enough optically thin area, such as altocumulus, forward escape alone can drive "
                               r"areas of irradiance enhancement of over (\d+) % of clear-sky irradiance\.)", "the enhancement quote").group(1)
    R["enh"] = float(need(R["enh_quote"], r"over (\d+) %", "the enhancement").group(1)) / 100.0
    R["cabauw_quote"] = need(enh, r"(A value of 10 W m-2 is based on 1 % of the typical order of magnitude for clear-sky irradiance "
                                  r"around noon for Cabauw\.)", "the Cabauw quote").group(1)
    R["e0_max"] = S0 / (1.0 - ECC) ** 2                       # CONTEXT only: no irradiance maximum is a decision input
    R["g_t"] = (1.0 + R["enh"]) * R["e0_max"]                 # SESSION design level of A-3(c), the double contingency, only
    alt = need(env, r"altitude_m:\n.*?in_use: \{min: (\d+), max: (\d+)\}", "the envelope's altitude", re.S)
    R["alt_max"] = float(alt.group(2))
    # THE DISTURBANCE CHECK's limits on PV_P (REQ-016: "Protection is judged apart from the window, under rule TRN-001")
    R["prot_quote"] = need(acc016, r"(Protection is judged apart from the window, under rule TRN-001)", "REQ-016's split").group(1)
    m = need(acc016, r"D4, an SMCJ28A, stands off ([\d.]+) V \(at most ([\d.]+) uA there", "REQ-016's D4 standoff")
    R["d4_vr"], R["d4_ir_ua"] = float(m.group(1)), float(m.group(2))
    R["cap_v"] = float(need(acc016, r"the ([\d.]+) V bulk capacitors C11 and C12", "REQ-016's bulk capacitors").group(1))
    sm1, sm2 = flat(pdf_page(PINS["smcj"][0], 1)), pdf_page(PINS["smcj"][0], 2)
    row = need(sm2, r"^\s*SMCJ28A\s+SMCJ28CA\s+\S+\s+\S+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)",
               "Littelfuse's SMCJ28A row").groups()
    R["d4_row"] = tuple(float(x) for x in row)            # VR, VBR min, VBR max, IT mA, VC, Ipp, IR uA
    if (R["d4_row"][0], R["d4_row"][6]) != (R["d4_vr"], R["d4_ir_ua"]):
        refuse(3, "REQ-016's D4 figures are not Littelfuse's SMCJ28A row")
    at = need(sm1, r"VBR @ TJ= VBR@25°C .*?x \(1\+αT x \(TJ - 25\)\) .*?\(αT:Temperature .*?Coefficient, typical value .*?is ([\d.]+)%\)",
              "Littelfuse's VBR temperature coefficient")
    R["d4_alpha_t"] = float(at.group(1)) / 100.0
    R["d4_vbr_cold"] = R["d4_row"][1] * (1.0 + R["d4_alpha_t"] * (R["t_cold"] - 25.0))
    # A-3(a): the stage's input current; the first-round limit's design floor's worst corner (stack C) is kept as the conservative
    # upper bound, above L4-E7R's backstop trip and regulation (read below)
    cw = need(o7, r"C\. the design floor .*?\n\s+the cold end worst ([\d.]+) W at ([\d.]+) V.*?\n\s+the hot end  worst ([\d.]+) W at ([\d.]+) V",
              "L4-E7's stack C corners", re.S).groups()
    R["i_norm_max"] = max(float(cw[0]) / float(cw[1]), float(cw[2]) / float(cw[3]))
    R["stack_c"] = tuple(float(x) for x in cw)
    # L4-E7R (accepted at checks 3 and 4): the regulation and the backstop that now hold the 100 W (section 10 of its output)
    f7 = flat(o7)
    r7 = {}
    for key, pat in (("reg", r"The LT8705A's own limit stays as the regulation, coordinated under the trip: RIMON_IN ([\d.]+k) \((C\d+)\), ([\d.]+) A"),
                     ("coord", r"stays at or under C's lowest trip with its parts aged, at every input voltage: ([\d.]+k), ([\d.]+) A at 25 V against ([\d.]+) A"),
                     ("joint", r"its highest under the joint assumptions \(([^)]*)\)"),
                     ("own", r"with the regulation's own 25 V corner at ([\d.]+) W"),
                     ("trip", r"the trip at most ([\d.]+) A at 25 V \(its sense voltage ([\d.]+) mV\), the static bound ([\d.]+) W, the margin"),
                     ("dec", r"normal operation: ([\d.]+) W at most, margin ([\d.]+) W, CONDITIONAL on G_CM \(break-even (\d+) %\) and the VIN\+ bias \((\d+) mA\)"),
                     ("resp", r"at most 10 J in any 0\.1 s for a response up to ([\d.]+) ms"),
                     ("energy", r"THE ENERGY: on SC-37's day ([\d.]+) / ([\d.]+) / ([\d.]+) Wh at the lower, nominal and upper hold corners \((\d+) / (\d+) / (\d+) h bound\)"),
                     ("crit", r"(L4-E7R's architecture criterion: MET, CONDITIONAL on the named items)")):
        r7[key] = need(f7, pat, "L4-E7R's %s" % key).groups()
    if r7["trip"][2] != r7["dec"][0]:
        refuse(3, "L4-E7R's static bound reads two ways")
    R["l4e7r"] = r7
    R["i_trip_max"], R["i_trip_min"] = float(r7["trip"][0]), float(r7["coord"][2])
    R["i_reg_nom"], R["i_reg_hi"] = float(r7["reg"][2]), float(r7["coord"][1])
    # A-3(b)/(c): the maker's own sizing allowance (SunPower 524958 Rev F, 3.0) and J_SOLAR's held catalogue rows
    g2 = flat(pdf_page(PINS["spr_guide"][0], 2))
    R["clause_quote"] = need(g2, r"(Under normal conditions, a photovoltaic module may experience conditions that produce more current "
                                 r"and/or voltage than reported at Standard Test Conditions\. Accordingly, the values of ISC and VOC marked "
                                 r"on the modules should be multiplied by a factor of 1\.25 when determining component voltage ratings, "
                                 r"conductor capacities, fuse sizes and size of controls connected to the module output\.)",
                             "SunPower's 1.25 clause").group(1)
    vh = flat(pdf_page(PINS["vh"][0], 1))
    R["vh_rating"] = need(vh, r"(Current rating: 10 A AC/DC)", "JST VH's current rating").group(1)
    R["vh_temp"] = need(vh, r"(Temperature range: \S+40℃ to \+105℃)", "JST VH's temperature range").group(1).replace("\u2011", "-")
    R["vh_overload"] = bool(re.search(r"(?i)overload|short.time|surge current", flat("".join(pdf_page(PINS["vh"][0], n) for n in range(1, 7)))))

    # ---------------------------------------------------------------- the model: the replay's main(), in-process
    RP = load("l4e_replay_for_l4e13", PINS["replay_py"][0])
    rc, text, LR = run_main_captured(RP)
    R["r0"] = rc == 0 and text.encode("utf-8") == open(os.path.join(TOP, PINS["replay_out"][0]), "rb").read()
    if not R["r0"]:
        refuse(4, "l4e_replay.main() does not print l4e_replay.out in-process")
    AC, BUD = LR["AC"], RP.BUD
    prof0, TA40, pr0, noct0, rl = LR["prof0"], LR["TA40"], LR["pr0"], LR["noct"], LR["rl"]
    meanday, least, gs, archs, win = LR["meanday"], LR["least"], LR["gs"], LR["archs"], LR["win_req016"]
    R["noct_inf"], R["rl"], R["pr0"] = noct0, rl, pr0
    hours = [h for h in range(24) if prof0[h] > 0.0]
    gpk = max(prof0)
    h_noon = prof0.index(gpk)
    R["h_noon"], R["g_noon"], R["ta_noon"] = h_noon, gpk, TA40[h_noon]
    R["tc_noon"] = AC.t_cell(TA40[h_noon], gpk, noct0)
    day_h = [h for h in hours if prof0[h] >= DAY_FRACTION * gpk]
    R["day_h"] = (min(day_h), max(day_h))

    def op_point(d, g, tc, v_hold, i_lim):
        """The replay's op_point with a flat limit: the FBIN hold while the panel gives less than the limit there, else the
        input-current limit with the voltage riding up the curve to where the panel gives it (8705af pp.29, 31)."""
        if g <= 0.0:
            return 0.0, 0.0, 0.0, False
        i_h = d.current(v_hold, g, tc, rl)
        if i_lim is None or i_h <= i_lim:
            return v_hold * i_h, v_hold, i_h, False
        lo, hi = v_hold, d.mpp(g, tc)[2]
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if d.current(mid, g, tc, rl) > i_lim:
                lo = mid
            else:
                hi = mid
        v = 0.5 * (lo + hi)
        return v * i_lim, v, i_lim, True

    def trace(d, v_hold, i_lim, wp, noct):
        """Hour by hour on SC-37's mean September day, by a1solar's and the replay's convention: PVGIS's maximum-power figure for
        wp (its 0.9417 carrying the angle, spectral and temperature losses) times the model's operating point over its own
        maximum-power point at the same irradiance and cell temperature."""
        out, nlim, zero = [], 0, 0
        for h in range(24):
            g, ta = prof0[h], TA40[h]
            if g <= 0.0:
                out.append(0.0)
                continue
            tc = AC.t_cell(ta, g, noct)
            pw, v_, i_, limited = op_point(d, g, tc, v_hold, i_lim)
            pm = AC.arr_mpp(d, 1, 1, g, tc)[0]
            st = BUD.panel_w(g, wp, pr0) * (pw / pm)
            if st > R["p_win"] + 1e-9:
                refuse(4, "a trace exceeds REQ-016's %.0f W at hour %d" % (R["p_win"], h))
            out.append(st)
            nlim += limited
            zero += (pw <= 0.0 and h in day_h)
        return out, nlim, zero

    # ---------------------------------------------------------------- the method checks (exit 4)
    dsp = LR["dsp"]
    for vh in (LR["v_lo"], LR["v_nom_hold"], LR["v_hi_hold"]):
        mine = trace(dsp, vh, None, 100.0, noct0)[0]
        theirs = LR["trace"](dsp, vh, None)[0]
        if mine != theirs:
            refuse(4, "this trace differs from the replay's at %.3f V" % vh)
    R["m1"] = []
    for vh in R["hold_legacy"]:
        s = round(sum(trace(dsp, vh, None, 100.0, noct0)[0]), 1)
        R["m1"].append((vh, s, rl12.get(round(vh, 3))))
        if rl12.get(round(vh, 3)) != s:
            refuse(4, "the SunPower day at %.3f V is %.1f Wh, the replay prints %s" % (vh, s, rl12.get(round(vh, 3))))
    R["m2"] = []
    for vh in R["hold_typ"] + R["hold_cond"]:
        s = round(sum(trace(dsp, vh, None, 100.0, noct0)[0]), 1)
        R["m2"].append((vh, s, l7e.get(round(vh, 3))))
        if l7e.get(round(vh, 3)) != s:
            refuse(4, "the SunPower day at %.3f V is %.1f Wh, L4-E7 prints %s" % (vh, s, l7e.get(round(vh, 3))))

    def a1a2(tr):
        out = {}
        for ak, _alab, n in archs:
            r_ = [meanday(ak, "WE", n, "TYP", h, win, collapse=False, gser=gs(tr), wp=100.0, ratio=1.0) for h in (48, 72)]
            x = [least(ak, "WE", "TYP", h, win, 1.0, 160.0, 34, collapse=False, gser=gs(tr), wp=100.0, ratio=1.0) for h in (48, 72)]
            kk = "el" if ak == "A2" else "eb"
            add = [(meanday(ak, "WE", x[i], "TYP", h, win, collapse=False, gser=gs(tr), wp=100.0, ratio=1.0)[kk] - r_[i][kk])
                   if x[i] is not None else None for i, h in enumerate((48, 72))]
            out[ak] = (r_[1]["stops"], r_[0]["uns"], r_[1]["uns"], add)
        return out
    tr_spr_nom = trace(dsp, R["hold_typ"][1], R["i_set"], 100.0, noct0)[0]
    chk = a1a2(tr_spr_nom)
    R["m3"] = []
    for ak in ("A1", "A2"):
        g7 = l7runs[ak]
        mine = ("%.1f" % sum(tr_spr_nom), "%d" % chk[ak][0][0], "%d" % chk[ak][0][1], "%.1f" % chk[ak][1][0], "%.1f" % chk[ak][1][1],
                "%.1f" % chk[ak][2][0], "%.1f" % chk[ak][2][1], "%.1f" % chk[ak][3][0], "%.1f" % chk[ak][3][1])
        R["m3"].append((ak, mine == tuple(g7[3:]), mine))
        if mine != tuple(g7[3:]):
            refuse(4, "A1/A2 on the SunPower trace differ from L4-E7's printed rows (%s: %s against %s)" % (ak, mine, g7[3:]))

    # ---------------------------------------------------------------- the candidates
    spr, sbx, bgv = read_sunpower(), read_solbian(), read_bougerv()
    cspr = AC.CAND["SPR100"]
    for k in ("p", "vmp", "imp", "voc", "isc", "beta_voc_abs", "alpha_isc_abs", "gamma_p"):
        if abs(spr[k] - cspr[k]) > 1e-12:
            refuse(3, "the SunPower sheet's %s reads %g, a1solar's CAND %g" % (k, spr[k], cspr[k]))
    q = spr["qual_pct"]
    # the bands of open-circuit voltage each maker prints, as factors on the rated value
    spr["band"] = (1.0 / (1.0 + q), 1.0 / (1.0 - q))          # SESSION: the sentence's own words, |rated - measured| <= 10 % of measured
    spr["band_records"] = (1.0 - q, 1.0 + q)                  # the reading the records took (L4-ENERGY O-1): rated x 1.10
    spr["band_src"] = "MAKER (guide 524958 Rev F, Table 1's note: '%s')" % spr["qual"]
    bgv["band"] = (1.0 + bgv["voc_band"][0], 1.0 + bgv["voc_band"][1])
    bgv["band_src"] = "MAKER-PAGE (the page's Voc row: '19.6V(-5%,+10%)')"
    sbx["band"] = None
    sbx["band_src"] = "none printed (MAKER: the sheet's only tolerance is 'Positive power tolerance (0%, +5%)', on Pmax)"
    spr["noct_used"], spr["noct_src"] = noct0, "INFERRED (none printed; the energy record's 47 C, Renogy's 45 +- 2 C at its upper end)"
    bgv["noct_used"], bgv["noct_src"] = noct0, "INFERRED (none printed; the energy record's 47 C)"
    sbx["noct_used"], sbx["noct_src"] = sbx["noct"], "MAKER (45 +- 2 C, the upper end)"
    if sbx["noct_used"] != noct0:
        refuse(3, "Solbian's NOCT upper end is not the energy record's 47 C")
    cands = [spr, bgv, sbx]

    def scaled(c, k, rel=True):
        """The panel at k times its rated voltages (Voc and Vmp), its rated currents kept (an ASSUMPTION: a band's voltages
        taken together); its Voc coefficient as a fraction of its own Voc (rel) or as the sheet's absolute figure."""
        d = {kk: c[kk] for kk in ("p", "vmp", "imp", "voc", "isc", "gamma_p") if kk in c}
        d["voc"], d["vmp"], d["p"] = c["voc"] * k, c["vmp"] * k, c["p"] * k
        for kk in ("beta_voc", "alpha_isc"):
            if c.get(kk) is not None:
                d[kk] = c[kk]
        if c.get("beta_voc_abs") is not None:
            d["beta_voc_abs"] = c["beta_voc_abs"] * (k if rel else 1.0)
        if c.get("alpha_isc_abs") is not None:
            d["alpha_isc_abs"] = c["alpha_isc_abs"]
        return d

    def voc_model(d, g, t):
        iph, i0, a = d.params(g, t)
        return a * math.log(iph / i0 + 1.0)

    for c in cands:
        c["fit"] = AC.Diode(scaled(c, 1.0))
        c["fit_note"] = c["fit"].fit_note
        # 3. the bound at the coldest in-use temperature
        c["beta_rel"] = AC.coef(scaled(c, 1.0), "beta_voc")[0]
        c["voc_cold_nom"] = AC.voc_at(scaled(c, 1.0), R["t_cold"])
        c["voc_m40_nom"] = AC.voc_at(scaled(c, 1.0), -40.0)
        # the module's diode ideality from the fit (INFERRED): n = A_ref / (Ns kT/q at 298.15 K); used only in the
        # disturbance check's sensitivity rows, never in the window
        c["n_fit"] = c["fit"].a_ref / (c["cells"] * 298.15 / AC.Q_OVER_K) if c.get("cells") else None
        if c["band"] is None:
            c["bound"], c["readings"], c["bounded"] = None, [], False
        else:
            top = c["band"][1]
            rd = [("SCENARIO, the band's top %.4f x rated with the coefficient relative to the unit's Voc" % top,
                   AC.voc_at(scaled(c, top, True), R["t_cold"]))]
            if c.get("beta_voc_abs") is not None:
                rd.append(("EXTRAPOLATION, the band's top %.4f x rated with the printed absolute coefficient" % top,
                           AC.voc_at(scaled(c, top, False), R["t_cold"])))
            else:
                rd.append(("EXTRAPOLATION, the band's top %.4f x rated, the coefficient's change taken on the rated Voc" % top,
                           c["voc"] * top + abs(c["beta_rel"]) * c["voc"] * (25.0 - R["t_cold"])))
            if c is spr:
                rt = spr["band_records"][1]
                rd.append(("the records' reading, rated x %.2f with the absolute coefficient (L4-ENERGY O-1)" % rt,
                           AC.voc_at(scaled(c, rt, False), R["t_cold"])))
            c["readings"] = rd
            if abs(voc_model(AC.Diode(scaled(c, top, True)), G_STC, R["t_cold"]) - rd[0][1]) > 1e-6:
                refuse(4, "%s: the fit's Voc at STC irradiance and -20 C is not the coefficient's" % c["name"])
            c["bound"] = max(v for _l, v in rd)          # THE WINDOW: the rated quantity, 1000 W/m2, moved to -20 C
            c["bounded"] = c["bound"] <= R["v_oc"] + 1e-9
        # the maker-bound route's window on the rated Voc at STC (what a maker's warranted band would have to stay inside):
        # the stricter of the coefficient's two readings at the band's top
        dv_rated = abs(c["beta_rel"]) * c["voc"] * (25.0 - R["t_cold"])
        c["k_bound"] = min(R["v_oc"] / c["voc_cold_nom"], (R["v_oc"] - dv_rated) / c["voc"])
        c["tol_needed_up"] = c["k_bound"] - 1.0
        # 4. the hold
        c["voc_noon_nom"] = voc_model(c["fit"], R["g_noon"], R["tc_noon"])
        ks = [("nominal", 1.0)] + ([] if c["band"] is None else [("band bottom", c["band"][0]), ("band top", c["band"][1])])
        c["variants"] = []
        for lab, k in ks:
            d = AC.Diode(scaled(c, k, True))
            if abs(voc_model(d, R["g_noon"], R["tc_noon"]) - k * c["voc_noon_nom"]) > 1e-6 * k * c["voc_noon_nom"]:
                refuse(4, "%s: the scaled panel's noon Voc is not linear in its scale" % c["name"])
            vm = [d.mpp(prof0[h], AC.t_cell(TA40[h], prof0[h], c["noct_used"]))[0] for h in day_h]
            v = {"lab": lab, "k": k, "d": d, "wp": c["p"] * k, "voc_stc": c["voc"] * k, "vmp_stc": c["vmp"] * k,
                 "voc_noon": voc_model(d, R["g_noon"], R["tc_noon"]), "vmp_day": (min(vm), max(vm)),
                 "vmp_noon": d.mpp(R["g_noon"], R["tc_noon"])[0]}
            v["reach"] = {vh: v["voc_noon"] > vh for vh in R["hold_typ"] + R["hold_cond"]}
            v["grid"] = []
            for vh in (R["hold_cond"][0], R["hold_typ"][0], R["hold_typ"][1], R["hold_typ"][2], R["hold_cond"][1]):
                row = [vh]
                for il in (None, R["i_set"], R["i_low"]):
                    tr, nl, zh = trace(d, vh, il, v["wp"], c["noct_used"])
                    row.append((sum(tr), nl, zh, tr))
                v["grid"].append(row)
            v["e_mpp"] = sum(BUD.panel_w(g, v["wp"], pr0) for g in prof0)
            c["variants"].append(v)
        c["reach_cond_upper"] = all(v["reach"][R["hold_cond"][1]] for v in c["variants"])
        c["reach_typ_upper"] = all(v["reach"][R["hold_typ"][2]] for v in c["variants"])
        # 5. power into the stage at the cold, bright corner and at STC, at the nominal hold (terminal, after the 5 m lead)
        pw = []
        for lab, k in ks:
            d = AC.Diode(scaled(c, k, True))
            for tl, tc in (("STC", 25.0), ("1000 W/m2, cells at -20 C", R["t_cold"])):
                drawn = R["hold_typ"][1] * d.current(R["hold_typ"][1], G_STC, tc, rl)
                lim = op_point(d, G_STC, tc, R["hold_typ"][1], R["i_set"])
                pw.append((lab, tl, drawn, lim[0], lim[1], d.mpp(G_STC, tc)[0] * d.current(d.mpp(G_STC, tc)[0], G_STC, tc)))
        c["power"] = pw
        c["p_drawn_max"] = max(x[2] for x in pw)
        c["p_lim_max"] = max(x[3] for x in pw)
        itop = 1.0 if c["band"] is None else c["band"][1]
        c["isc_hot"] = AC.isc_at(dict(scaled(c, 1.0), isc=c["isc"] * itop), T_ISC_HOT)
        c["isc_hot_clause"] = K_CLAUSE * c["isc_hot"]
        # 7. the window against the band: the widest band ratio (top over bottom) this curve shape can carry
        c["k_reach_cond"] = R["hold_cond"][1] / c["voc_noon_nom"]
        c["k_reach_typ"] = R["hold_typ"][2] / c["voc_noon_nom"]
        c["w_cond"] = c["k_bound"] / c["k_reach_cond"]
        c["w_typ"] = c["k_bound"] / c["k_reach_typ"]
        c["band_ratio"] = None if c["band"] is None else c["band"][1] / c["band"][0]
        c["k_reach_abs"] = None
        if c.get("beta_voc_abs") is not None:
            # the printed absolute coefficient, not scaled with the unit: the noon Voc is then not linear in k; solve it
            lo_k, hi_k = 0.5, 1.5
            for _ in range(80):
                mk = 0.5 * (lo_k + hi_k)
                if voc_model(AC.Diode(scaled(c, mk, False)), R["g_noon"], R["tc_noon"]) > R["hold_cond"][1]:
                    hi_k = mk
                else:
                    lo_k = mk
            c["k_reach_abs"] = 0.5 * (lo_k + hi_k)
        c["k_floor_maker"] = max(c["k_reach_cond"], c["k_reach_abs"] or 0.0)
        c["tol_needed_down"] = 1.0 - c["k_floor_maker"]
        # the predicate
        c["portable"] = c["mass"] <= PORTABLE_KG and ("flexible" in c["class"] or "folding" in c["class"])
        c["qualifies"] = bool(c["bounded"] and c["reach_cond_upper"] and c["portable"])
        c["qualifies_typ"] = bool(c["bounded"] and c["reach_typ_upper"] and c["portable"])     # the same on EA3's typical band
    R["cands"] = cands
    # 8. A1 and A2 on each candidate's traces: the nominal at the nominal hold and the limit nominal; the least-energy corner over
    # the printed band and the conditioned hold, the limit at its lowest
    R["runs"] = []
    for c in cands:
        vn = c["variants"][0]
        nom = vn["grid"][2][2][3]
        worst_v = min(c["variants"], key=lambda v: v["grid"][4][3][0])
        worst = worst_v["grid"][4][3][3]
        for lab, tr in (("nominal panel, nominal hold %.3f V, limit nominal %.4f A" % (R["hold_typ"][1], R["i_set"]), nom),
                        ("%s, conditioned upper corner %.3f V, limit at its lowest %.4f A" % (worst_v["lab"], R["hold_cond"][1], R["i_low"]), worst)):
            R["runs"].append((c["key"], lab, sum(tr), a1a2(tr), [round(x, 1) for x in tr]))
    # the screen of documents read
    R["screen"] = json.load(open(os.path.join(TOP, PINS["screen"][0]), encoding="utf-8"))
    for c in cands:
        c["maker_ceiling"] = c["k_bound"] * c["voc"]             # route 1: a warranted Voc at STC at or under this is bounded
        c["maker_floor"] = c["k_floor_maker"] * c["voc"]         # and at or over this reaches the conditioned upper corner at noon

    # ---------------------------------------------------------------- PANEL-ACC: route 2, one identified unit
    spec = {"u_v": SPEC_UV, "u_a": SPEC_UA, "u_i": SPEC_UI, "u_g": SPEC_UG, "u_tc": SPEC_UTC}
    R["spec"] = spec
    vh_c = R["hold_cond"][1]
    g_a2 = R["g_noon"] * (1.0 - spec["u_g"])          # A-2's corner, offset to the conservative side by the lab's settings
    t_a2 = R["tc_noon"] + spec["u_tc"]
    R["a2_corner"] = (g_a2, t_a2)

    def a2_measure(d):
        """A-2 as the laboratory measures it, here on the model (INFERRED): the current at the panel voltage vh_c + I R_lead
        (the 5 m lead's resistance), at g_a2 and t_a2; the stage's input P = vh_c x I; U_P from U_I and the voltage point's
        U_V through the local slope dI/dV; accepted on P - U_P strictly above the useful-power line."""
        i = d.current(vh_c, g_a2, t_a2, rl)
        h = 1e-4
        didv = (d.current(vh_c + h, g_a2, t_a2, rl) - d.current(vh_c - h, g_a2, t_a2, rl)) / (2.0 * h)
        p = vh_c * i
        up = vh_c * math.sqrt((spec["u_i"] * i) ** 2 + (didv * spec["u_v"]) ** 2)
        return {"i": i, "didv": didv, "p": p, "u_p": up, "p_low": p - up, "ok": p - up > R["p_use"]}

    def a2_signs(d):
        """At A-2's corner on the model: dI/dG, dI/dT at the fixed hold voltage, and the maximum-power voltage there."""
        dg, dt = 1.0, 0.01
        di_dg = (d.current(vh_c, g_a2 + dg, t_a2, rl) - d.current(vh_c, g_a2 - dg, t_a2, rl)) / (2.0 * dg)
        di_dt = (d.current(vh_c, g_a2, t_a2 + dt, rl) - d.current(vh_c, g_a2, t_a2 - dt, rl)) / (2.0 * dt)
        return {"di_dg": di_dg, "di_dt": di_dt, "vmp": d.mpp(g_a2, t_a2)[0], "vmp_noon": d.mpp(R["g_noon"], R["tc_noon"])[0]}

    def rated_unit(c, k=1.0):
        """A unit equal to c's typical rows at k times their voltages (INFERRED: the sheet's coefficient, the larger of its two
        readings, gives its -20 C Voc; the energy record's fit gives its curve; a real unit replaces each by its measurement)."""
        absb = abs(c["beta_voc_abs"]) if c.get("beta_voc_abs") is not None else None
        vm20 = c["voc"] * k * (1.0 + abs(c["beta_rel"]) * (25.0 - R["t_cold"]))
        if absb is not None:
            vm20 = max(vm20, c["voc"] * k + absb * (25.0 - R["t_cold"]))
        return {"v25": c["voc"] * k, "vm20": vm20, "isc": c["isc"], "d": AC.Diode(scaled(c, k, True)), "k": k,
                "a25": c["fit"].a_ref * k}

    def accept(c, unit):
        """PANEL-ACC's measured conditions on one unit: A-1 (the window), A-2 (useful charging, measured), A-3(a) and (b)."""
        a1 = unit["vm20"] + spec["u_v"]
        a2 = a2_measure(unit["d"])
        alpha = AC.coef(scaled(c, 1.0), "alpha_isc")[0]
        isc_hot = unit["isc"] * (1.0 + spec["u_i"]) * (1.0 + alpha * (T_ISC_HOT - 25.0))
        return {"a1": a1, "a1_ok": a1 <= R["v_oc"] + 1e-12, "a2": a2, "a2_ok": a2["ok"],
                "a3a": R["i_norm_max"], "a3a_ok": R["i_norm_max"] <= R["entry_a"],
                "isc_hot": isc_hot, "a3b": K_CLAUSE * isc_hot, "a3b_ok": K_CLAUSE * isc_hot <= R["entry_a"] + 1e-12,
                "a3c": isc_hot * R["g_t"] / G_STC}

    R["acc_cands"] = {}
    for c in cands:
        R["acc_cands"][c["key"]] = accept(c, rated_unit(c))
    unit_c = spr                                                # the identified unit's model: SunPower SPR-E-Flex-100 (SESSION)
    R["acc_unit"] = unit_c["key"]
    ru = rated_unit(unit_c)
    ra = R["acc_cands"][unit_c["key"]]
    R["a2_signs_rated"] = a2_signs(ru["d"])
    # the window for a unit of this shape: the scale k at A-1's ceiling and at A-2's floor (both by bisection)
    lo_k, hi_k = 0.80, 1.20
    for _ in range(80):
        mk = 0.5 * (lo_k + hi_k)
        if rated_unit(unit_c, mk)["vm20"] + spec["u_v"] <= R["v_oc"]:
            lo_k = mk
        else:
            hi_k = mk
    k_ceil = lo_k
    lo_k, hi_k = 0.80, 1.10
    for _ in range(80):
        mk = 0.5 * (lo_k + hi_k)
        if a2_measure(rated_unit(unit_c, mk)["d"])["p_low"] > R["p_use"]:
            hi_k = mk
        else:
            lo_k = mk
    k_floor = hi_k
    fu = rated_unit(unit_c, k_floor)
    fl = accept(unit_c, fu)
    R["a2_signs_floor"] = a2_signs(fu["d"])
    for sg in (R["a2_signs_rated"], R["a2_signs_floor"]):
        if not (sg["di_dg"] > 0.0 and sg["di_dt"] < 0.0 and sg["vmp"] < vh_c):
            refuse(4, "A-2's offsets are not conservative on the model at its corner")
    R["acc"] = {"k_ceil": k_ceil, "k_floor": k_floor, "v25_ceil": k_ceil * unit_c["voc"], "v25_floor": k_floor * unit_c["voc"],
                "vm20_ceil": rated_unit(unit_c, k_ceil)["vm20"], "rated": ra, "rated_unit": ru, "floor": fl,
                "feasible": k_floor < 1.0 <= k_ceil and ra["a1_ok"] and ra["a2_ok"] and ra["a3a_ok"] and ra["a3b_ok"]}
    # information: a laboratory without a cold chamber could extrapolate the cold point from M1 instead; the coefficient's
    # uncertainty that would leave the rated unit inside A-1 (Vm20 = (Voc25 + U_V)(1 + 45 K |beta| (1 + u)))
    R["acc"]["ub_extrap_max"] = ((R["v_oc"] - spec["u_v"]) / (ru["v25"] + spec["u_v"]) - 1.0) / (
        abs(unit_c["beta_rel"]) * (25.0 - R["t_cold"])) - 1.0
    # A-3(c), the double contingency: what a 20 A part would cover
    R["acc"]["g_20a"] = 20.0 / ra["isc_hot"] * G_STC
    # the energy of the rated unit and of the floor unit through the replay (A1, A2)
    R["acc_runs"] = []
    for lab, d, vh in (("the rated unit (the typical rows), the conditioned upper corner", ru["d"], vh_c),
                       ("the rated unit (the typical rows), the nominal hold", ru["d"], R["hold_typ"][1]),
                       ("the floor unit (A-2's lower bound on the line), the conditioned upper corner", fu["d"], vh_c)):
        tr, nl, zh = trace(d, vh, R["i_set"], d.c["p"], unit_c["noct_used"])
        R["acc_runs"].append((lab, vh, sum(tr), nl, zh, tr[R["h_noon"]], a1a2(tr), [round(x, 1) for x in tr]))
        if sum(tr) <= 0.0:
            refuse(4, "an accepted unit's trace gives no energy at %.3f V" % vh)

    # the rated unit's trace at the conditioned upper corner must be L4-E7's own row (its "NEW conditioned upper end")
    l7c = {}
    for mm in re.finditer(r"NEW conditioned upper end \(([\d.]+) V: [^)]*\), (A1|A2): ([\d.]+) Wh a day; first interruption h (\d+)/(\d+); "
                          r"unserved ([\d.]+) / ([\d.]+) at 48 h, ([\d.]+) / ([\d.]+) at 72 h; least addition \+([\d.]+) / \+([\d.]+) Wh", o7):
        l7c[mm.group(2)] = mm.groups()[2:]
    if set(l7c) != {"A1", "A2"}:
        refuse(3, "L4-E7's NEW conditioned upper end rows not parsed")
    r0_ = R["acc_runs"][0]
    R["m4"] = []
    for ak in ("A1", "A2"):
        st, u48, u72, add = r0_[6][ak]
        mine = ("%.1f" % r0_[2], "%d" % st[0], "%d" % st[1], "%.1f" % u48[0], "%.1f" % u48[1], "%.1f" % u72[0], "%.1f" % u72[1],
                "%.1f" % add[0], "%.1f" % add[1])
        R["m4"].append((ak, mine == tuple(l7c[ak]), mine))
        if mine != tuple(l7c[ak]):
            refuse(4, "the rated unit's corner trace differs from L4-E7's printed row (%s: %s against %s)" % (ak, mine, l7c[ak]))

    # L4-E7R moved the regulation to RIMON_IN 31.6k: the SunPower's highest model current on SC-37's day at the conditioned upper
    # corner and at the nominal hold, against the regulation's nominal and C's lowest trip (which rows of this record move)
    def i_day_max(vh):
        return max(dsp.current(vh, prof0[h], AC.t_cell(TA40[h], prof0[h], noct0), rl) for h in hours)
    R["corner_i"] = (i_day_max(vh_c), i_day_max(R["hold_typ"][1]))
    R["corner_unmoved"] = R["corner_i"][0] < min(R["i_reg_nom"], R["i_trip_min"])

    # ---------------------------------------------------------------- THE DISTURBANCE CHECK (protection, apart from the window)
    ns = spr["cells"]
    tk = R["t_cold"] + 273.15
    vt_cold, vt_25 = tk / AC.Q_OVER_K, 298.15 / AC.Q_OVER_K
    dv = R["d4_vr"] - R["v_oc"]               # from A-1's ceiling (Voc at -20 C, 1000 W/m2 at most 25.000 V) to D4's standoff
    rows = []
    for lab, n in (("n from the typical unit's fit (INFERRED)", spr["n_fit"]),
                   ("n_max = 2 (MODELLING_ASSUMPTION): the decision row", N_MAX),
                   ("n = 3 (a sensitivity)", N_SENS)):
        slope = n * ns * vt_cold
        g_thr = G_STC * math.exp(dv / slope)
        rows.append((lab, n, slope, g_thr, g_thr / R["e0_max"]))
    R["dist"] = {"ns": ns, "vt_cold": vt_cold, "vt_25": vt_25, "dv": dv, "rows": rows,
                 "dlog_dt_max": dv / tk,                                   # V/K: the log term's temperature slope at threshold
                 "beta_mag_min": min(abs(spr["beta_voc_abs"]), abs(spr["beta_rel"]) * spr["voc"]),
                 "n_meas_typ": ru["a25"] / (ns * vt_25), "n_meas_typ_upper": ru["a25"] * (1.0 + spec["u_a"]) / (ns * vt_25),
                 "clause_v_rated": K_CLAUSE * spr["voc"], "clause_v_ceil": K_CLAUSE * R["acc"]["v25_ceil"],
                 "enh_level": R["g_t"]}
    if not (R["dist"]["beta_mag_min"] > R["dist"]["dlog_dt_max"]):
        refuse(4, "the coldest cells would not be the worst case")
    R["dist"]["g_thr_dec"] = rows[1][3]
    R["dist"]["implied"] = R["dist"]["g_thr_dec"] > R["e0_max"]        # the threshold lies above every clear-sky irradiance

    # ---------------------------------------------------------------- the decision (B2): two routes
    R["qualifying"] = [c["key"] for c in cands if c["qualifies"]]
    R["bounded_any"] = [c["key"] for c in cands if c["bounded"]]
    R["route1"] = bool(R["qualifying"])
    R["route2"] = bool(R["acc"]["feasible"])
    R["decision"] = classify(R["route1"], R["route2"])
    return R


# ====================================================================================== the printed record
def render(R):
    o = []
    P = o.append
    cands = {c["key"]: c for c in R["cands"]}
    spr, bgv, sbx = cands["SPR"], cands["BGV"], cands["SBX"]
    A = R["acc"]
    ra, ru, spec = A["rated"], A["rated_unit"], R["spec"]
    P("L4-E13 (MESHSAT-1357): U-03, A PANEL WHOSE OPEN-CIRCUIT VOLTAGE IS BOUNDED AT THE COLDEST OPERATING TEMPERATURE INSIDE")
    P("REQ-016'S WINDOW, BY ITS MAKER'S DOCUMENT OR BY A CONTROLLED UNIT (PANEL-ACC), WITH THE DISTURBANCE CHECK JUDGED APART. Prototype")
    P("design, desk arithmetic: nothing bought, built, powered or measured; no physical unit is accepted.")
    P("")
    P("0. INPUTS AND REPRODUCTIONS")
    for key, (rel, want) in PINS.items():
        P("   %-10s %s  sha256 %s" % (key, rel, want[:16]))
    P("   l4e_replay.main() in-process, its locals captured, prints l4e_replay.out byte for byte: %s" % ("yes" if R["r0"] else "NO"))
    P("   this record's trace equals the replay's trace hour for hour on the SunPower panel at its three holds: yes")
    P("   the SunPower day (Wh, no limit) against the replay's section 12 (legacy band): %s" % "; ".join(
        "%.3f V %.1f = %.1f" % x for x in R["m1"]))
    P("   the SunPower day (Wh, no limit) against L4-E7's section 5 (the selected hold): %s" % "; ".join(
        "%.3f V %.1f = %.1f" % x for x in R["m2"]))
    for ak, ok, mine in R["m3"]:
        P("   %s on the SunPower trace at %.3f V and %.4f A equals L4-E7's NEW nominal row: %s (%s Wh a day; h %s/%s; %s / %s at 48 h, %s / %s at 72 h; +%s / +%s Wh)"
          % ((ak, R["hold_typ"][1], R["i_set"], "yes" if ok else "NO") + mine))
    for ak, ok, mine in R["m4"]:
        P("   %s on the rated unit at the conditioned upper corner %.3f V equals L4-E7's NEW conditioned upper end row: %s (%s Wh a day; h %s/%s; %s / %s at 48 h, %s / %s at 72 h; +%s / +%s Wh)"
          % ((ak, R["hold_cond"][1], "yes" if ok else "NO") + mine))
    P("")
    P("1. THE REQUIREMENT AND ITS THREE CHECKS")
    P("   REQ-016 (v2/ecad/tools/pcb_requirements.yaml), verbatim: \"%s\"" % R["req016"])
    P("   read: at most %.0f V open circuit at the panel's coldest operating temperature; held at %.1f V; at most %.0f W into the stage;"
      % (R["v_oc"], R["v_hold_req"], R["p_win"]))
    P("   its acceptance: F2 and J_SOLAR rated %.0f A; and \"%s\". A series diode or a clamp in place of the panel's own open"
      % (R["entry_a"], R["prot_quote"]))
    P("   circuit: %s" % ("admitted by the text" if R["series_admitted"] else "NOT admitted (the statement constrains the panel's own open circuit)"))
    P("   THE WINDOW (normal operation, REQ-016's rated quantity): the makers' rated Voc row is defined at %.0f W/m2 (SunPower 523809" % G_STC)
    P("   p.1: 'Typical Electrical Data at STC: %s'; Solbian's STC note and BougeRV's rows alike), moved to the coldest operating" % spr["stc"])
    P("   temperature, %.0f C, REQ-024's in-use minimum (%s to +%s C ambient; pcb_envelope.yaml in_use agrees). The records settle"
      % (R["t_cold"], R["req024_range"][0], R["req024_range"][1]))
    P("   REQ-016's reading there (L4-ENERGY-ARCHITECTURE.md, 'What stays INCONCLUSIVE'); the panels' -40 C ratings are information.")
    P("   No irradiance above %.0f W/m2 enters the window: the earlier G_MAX of %.1f W/m2 is WITHDRAWN as a decision input." % (
        G_STC, R["g_t"]))
    P("   THE DISTURBANCE CHECK (component limits during an irradiance burst on cold-soaked cells, seconds to minutes): judged apart")
    P("   from the window under TRN-001, against the lowest rating on PV_P (section 11); it needs no irradiance maximum.")
    P("   USEFUL POWER (A-2): the stage draws its own drive and quiescent power, %.1f mA, %.2f W at L4-E5's raised EXTVCC (L4-E7,"
      % (R["i_fixed_ma"], R["p_fixed"]))
    P("   INFERRED there), from its output; at its declared %.2f (the replay) the input must exceed %.2f / %.2f = %.6f W." % (
        R["eta_stage"], R["p_fixed"], R["eta_stage"], R["p_use"]))
    P("   CONTEXT, not a bound: E0 = %.0f W/m2 / (1 - %.4f)^2 = %.1f W/m2, the extraterrestrial irradiance at perihelion (physical"
      % (S0, ECC, R["e0_max"]))
    P("   constants); the read source (Mol and van Heerwaarden 2025, ACP 25, p.1, CC BY 4.0): \"%s\"" % R["enh_quote"])
    P("   and the clear-sky noon irradiance at Cabauw near 1000 W/m2 (Mol, Knap and van Heerwaarden 2023, p.8). The kit's in-use")
    P("   altitude reaches %.0f m (D-02c)." % R["alt_max"])
    P("   owner rulings in the registry naming a panel class (a class word beside 'panel' or 'array' in one sentence): %s"
      % (", ".join(R["owner_panel_rulings"]) or "none; a1solar SELECTION.md 1 (a session's criterion) prefers folding, semi-rigid or blanket for a carried kit"))
    P("")
    P("2. THE CANDIDATES, AS THEIR MAKERS PRINT THEM")
    for c in (spr, bgv, sbx):
        P("   %s (%s) [%s]" % (c["name"], c["maker"], c["evidence"]))
        P("     document: %s" % c["doc"])
        P("     Pmax %.0f W (power band %+.0f / %+.0f %%), Vmp %.2f V, Imp %.2f A, Voc %.2f V, Isc %.2f A" % (
            c["p"], 100 * c["p_tol"][0], 100 * c["p_tol"][1], c["vmp"], c["imp"], c["voc"], c["isc"]))
        if c.get("beta_voc_abs") is not None:
            P("     Voc coefficient %.1f mV/K as printed (%.4f %%/K of the rated Voc); Isc %+.1f mA/K; Pmax %.2f %%/K" % (
                1e3 * c["beta_voc_abs"], 100 * c["beta_rel"], 1e3 * c["alpha_isc_abs"], 100 * c["gamma_p"]))
        else:
            P("     Voc coefficient %.2f %%/K; Isc %+.3f %%/K; Pmax %.2f %%/K" % (100 * c["beta_voc"], 100 * c["alpha_isc"], 100 * c["gamma_p"]))
        P("     no limits are printed for any coefficient")
        P("     the open-circuit band: %s" % c["band_src"])
        P("     test conditions: %s; NOCT: %s; operating range %s" % (
            c["stc"] or "NOT STATED on the page (ASSUMPTION: the rows are STC values)",
            "%.0f +- %.0f C (MAKER)" % c["noct_row"] if c.get("noct_row") else "none printed",
            "%.1f to %.1f C" % c["t_range"] if c["t_range"] else "not printed"))
        if c is spr:
            P("     the sheet's heading over every row: 'Typical Electrical Data' (%s)" % ("yes" if c["typical"] else "no"))
        if c is bgv:
            P("     the page's Vmp x Imp is %.1f W against its %.0f W Pmax; its 'Series Fuse Rating' row prints no number ('%s')" % (
                c["vmp"] * c["imp"], c["p"], c["fuse_row"]))
        if c is sbx:
            P("     the STC note adds: 'Measurements carried out according to the Standard IEC 61215 requirements' (%s); a Voc tolerance"
              " printed anywhere on the sheet: %s" % ("yes" if c["iec_note"] else "no", "yes" if c["voc_tol_printed"] else "no"))
        P("     the model's fit (a1solar's single-diode model, imported and pinned): %s; its ideality n %s" % (
            c["fit_note"], "%.4f (INFERRED, from %d cells)" % (c["n_fit"], c["cells"]) if c["n_fit"] else "not derived (no cell count printed)"))
    P("")
    P("3. ROUTE 1, THE MAKER'S BAND IN THE WINDOW: Voc AT %.0f C AND %.0f W/m2 AT THE TOP OF THE PRINTED BAND, AGAINST %.0f V" % (
        R["t_cold"], G_STC, R["v_oc"]))
    P("   The readings are a SCENARIO and an EXTRAPOLATION of the printed rows: neither is a warranted maximum, since no maker prints a")
    P("   limit on its coefficient; the bound is the larger.")
    for c in (spr, bgv, sbx):
        P("   %s: rated Voc at %.0f C %.3f V (the typical row; %.3f V at -40 C, information)" % (
            c["name"], R["t_cold"], c["voc_cold_nom"], c["voc_m40_nom"]))
        if c["band"] is None:
            P("     NOT BOUNDED: the maker prints no open-circuit band, so no maximum exists on its document")
        else:
            for lab, v in c["readings"]:
                P("     %-100s %.3f V" % (lab, v))
            P("     the bound %.3f V: %s (margin %+.3f V)" % (
                c["bound"], "BOUNDED at or under 25 V" if c["bounded"] else "NOT BOUNDED: the maker's own band reaches past 25 V",
                R["v_oc"] - c["bound"]))
        P("     what a warranted band on Voc at STC would have to stay inside: %.4f to %.4f V" % (c["maker_floor"], c["maker_ceiling"]))
        P("     (top: 25 V at %.0f C by the stricter coefficient reading, %+.2f %% on the rated Voc; bottom: the conditioned upper corner %.3f V"
          % (R["t_cold"], 100 * c["tol_needed_up"], R["hold_cond"][1]))
        P("     reached at noon, %+.2f %%%s)" % (-100 * c["tol_needed_down"],
                                             "; the printed absolute coefficient gives the higher floor" if c["k_reach_abs"] and c["k_reach_abs"] > c["k_reach_cond"] else ""))
    P("")
    P("4. THE HOLD: board E's input regulation (L4-E7, selected, drafted and not applied; RECORD l4e7_stage_settings.out)")
    P("   nominal %.3f V; EA3 at its typical gain %.3f / %.3f V; the widest conditioned band (EA3 at half, the drifts) %.3f / %.3f V"
      % (R["hold_typ"][1], R["hold_typ"][0], R["hold_typ"][2], R["hold_cond"][0], R["hold_cond"][1]))
    P("   the drafted input-current limit %.4f A (its lowest %.4f A at the nominal hold), taken flat; the 5 m lead %.4f Ohm (ESTIMATE)"
      % (R["i_set"], R["i_low"], R["rl"]))
    P("   SC-37's mean September day: noon is hour %d (%.1f W/m2, air %.2f C, cells %.2f C at NOCT %.0f C); the day's band is read over"
      % (R["h_noon"], R["g_noon"], R["ta_noon"], R["tc_noon"], R["noct_inf"]))
    P("   hours %d to %d (at least %.0f %% of the peak, SESSION). The screen: the hold lies inside the curve when the panel's open"
      % (R["day_h"][0], R["day_h"][1], 100 * DAY_FRACTION))
    P("   circuit at noon exceeds the hold corner, over the printed band where one is printed and on the nominal model only where none")
    P("   is (a necessary condition: at the corner itself the stage takes nothing); the energy below says how much it takes. The band's")
    P("   voltages are scaled together with the rated currents kept (ASSUMPTION); the Voc coefficient as a fraction of each unit's Voc.")
    for c in (spr, bgv, sbx):
        P("   %s:" % c["name"])
        for v in c["variants"]:
            P("     %-12s Voc at STC %.3f V, Vmp at STC %.3f V; at noon Voc %.3f V, Vmp %.3f V; Vmp over the day %.3f to %.3f V" % (
                v["lab"], v["voc_stc"], v["vmp_stc"], v["voc_noon"], v["vmp_noon"], v["vmp_day"][0], v["vmp_day"][1]))
            P("     %-12s the hold inside the curve at noon: %s" % ("", "; ".join(
                "%.3f V %s" % (vh, "yes" if v["reach"][vh] else "NO") for vh in sorted(v["reach"]))))
        if c["band"] is None:
            P("     on the nominal model only (no band printed): inside the curve at the conditioned upper corner %s; at the typical one %s" % (
                "yes" if c["reach_cond_upper"] else "NO", "yes" if c["reach_typ_upper"] else "NO"))
        else:
            P("     inside the curve at the conditioned upper corner over the printed band: %s; at the typical upper corner: %s" % (
                "yes" if c["reach_cond_upper"] else "NO", "yes" if c["reach_typ_upper"] else "NO"))
    P("   ENERGY into the stage on SC-37's day (MODELED; Wh a day; [hours the limit binds, daylight hours with no input]); columns:")
    P("   no limit (as drawn) | the limit nominal %.4f A | the limit at its lowest %.4f A" % (R["i_set"], R["i_low"]))
    for c in (spr, bgv, sbx):
        for v in c["variants"]:
            P("   %s, %s (%.1f Wp; %.1f Wh a day at the maximum-power point, PVGIS):" % (c["name"], v["lab"], v["wp"], v["e_mpp"]))
            for row in v["grid"]:
                P("     hold %.3f V  %7.1f [%d, %d] | %7.1f [%d, %d] | %7.1f [%d, %d]" % (
                    row[0], row[1][0], row[1][1], row[1][2], row[2][0], row[2][1], row[2][2], row[3][0], row[3][1], row[3][2]))
    P("")
    P("5. THE POWER INTO THE STAGE AND THE ENTRY'S CURRENT (MODELED at the terminals after the lead; the nominal hold %.3f V)" % R["hold_typ"][1])
    for c in (spr, bgv, sbx):
        P("   %s:" % c["name"])
        for lab, tl, drawn, lim, vlim, pmpp in c["power"]:
            P("     %-12s %-27s as drawn %6.1f W | with the limit %6.1f W (at %.2f V) | the panel's maximum %6.1f W" % (
                lab, tl, drawn, lim, vlim, pmpp))
        P("     as drawn the stage would take up to %.1f W (%s %.0f W); with L4-E7's first-round limit at most %.1f W here; the 100 W rests"
          % (c["p_drawn_max"], "over" if c["p_drawn_max"] > R["p_win"] else "under", R["p_win"], c["p_lim_max"]))
        P("     on L4-E7R's regulation and backstop (A-4, section 10), as for every candidate")
        if c["band"] is None:
            P("     hot short circuit (+%.0f C cells, 1000 W/m2) %.2f A NOMINAL (no Isc band printed) against the entry's %.0f A; x %.2f, a factor"
              % (T_ISC_HOT, c["isc_hot"], R["entry_a"], K_CLAUSE))
            P("     transferred from SunPower's guide (a1solar's convention), not this maker's instruction: %.2f A: %s" % (
                c["isc_hot_clause"], "inside %.0f A" % R["entry_a"] if c["isc_hot_clause"] <= R["entry_a"] else "OVER the entry's %.0f A" % R["entry_a"]))
        else:
            P("     hot short circuit (+%.0f C cells, 1000 W/m2, the band's top) %.2f A against the entry's %.0f A; x %.2f (SunPower's rating"
              % (T_ISC_HOT, c["isc_hot"], R["entry_a"], K_CLAUSE))
            P("     clause, a1solar's convention%s) %.2f A: %s" % ("" if c is spr else "; transferred, not this maker's instruction",
                                                               c["isc_hot_clause"], "inside %.0f A" % R["entry_a"] if c["isc_hot_clause"] <= R["entry_a"] else "OVER the entry's %.0f A" % R["entry_a"]))
    P("")
    P("6. PORTABLE CLASS (the makers' documents); SESSION: portable is a flexible or folding class at or under %.1f kg" % PORTABLE_KG)
    for c in (spr, bgv, sbx):
        P("   %-60s %s; %s; %.2f kg; operating %s" % (c["name"], c["class"], c["size"], c["mass"],
                                                       "%.1f to %.1f C" % c["t_range"] if c["t_range"] else "not printed"))
    P("   BougeRV's page limits operation to %.1f to %.1f C: the kit's -20 C is its own lower limit, and its upper limit sits under the" % bgv["t_range"])
    P("   cells' temperature in full sun at the envelope's +%.0f C ambient (%.1f C at 1000 W/m2 by the NOCT model at %.0f C, INFERRED)" % (
        R["t_hot_amb"], R["t_hot_amb"] + (R["noct_inf"] - 20.0) / 800.0 * 1000.0, R["noct_inf"]))
    P("")
    P("7. THE WINDOW AGAINST A PRINTED BAND (route 1's gap, INFERRED on the model)")
    P("   A band's spread is its top over its bottom (as factors on the rated Voc). A panel of a given curve shape is bounded in the")
    P("   window only while its band top is at most k_bound (25 V over its rated Voc at %.0f C and %.0f W/m2) and is held only while its"
      % (R["t_cold"], G_STC))
    P("   band bottom is at least k_reach (the hold's upper corner over its rated Voc at noon; the fit's Voc scales exactly with the")
    P("   voltages, checked). Both hold for some rating only while the spread is at most W = k_bound / k_reach.")
    for c in (spr, bgv, sbx):
        P("   %-60s k_bound %.4f; k_reach %.4f (%.3f V) / %.4f (%.3f V); W %.4f / %.4f (symmetric +-%.2f / +-%.2f %%); printed spread %s" % (
            c["name"], c["k_bound"], c["k_reach_cond"], R["hold_cond"][1], c["k_reach_typ"], R["hold_typ"][2], c["w_cond"], c["w_typ"],
            100 * (c["w_cond"] - 1) / (c["w_cond"] + 1), 100 * (c["w_typ"] - 1) / (c["w_typ"] + 1),
            "%.4f: %s" % (c["band_ratio"], "fits W" if c["band_ratio"] <= c["w_cond"] else "WIDER than W, no rating of this shape and band fits both")
            if c["band_ratio"] else "none printed"))
    if bgv["k_reach_cond"] > 1.0:
        P("   BougeRV's rated row sits under its own reach floor (k_reach %.4f > 1): its rating, not only its band, is too low for the"
          % bgv["k_reach_cond"])
        P("   hold's upper corner.")
    P("")
    P("8. THE ENERGY CONSEQUENCE: A1 AND A2 ON EACH CANDIDATE'S TRACE (the replay's meanday and least, unchanged; CORRECTED, WE, TYP;")
    P("   the service ledger; pairs 06 / 18 UTC). The 100 W screening stimulus gives %.1f Wh a day; the SunPower nominal trace %.1f Wh." % (
        R["stimulus"], R["m2"][1][1]))
    for key, lab, tot, rr, tr in R["runs"]:
        for ak in ("A1", "A2"):
            st, u48, u72, add = rr[ak]
            P("   %s %s, %s: %.1f Wh a day; first interruption h %s; unserved %.1f / %.1f at 48 h, %.1f / %.1f at 72 h; least addition %s" % (
                key, lab, ak, tot, "/".join("-" if x is None else str(x) for x in st), u48[0], u48[1], u72[0], u72[1],
                " / ".join("-" if a is None else "+%.1f" % a for a in add) + " Wh"))
        P("     the trace (W, hours 0 to 23): %s" % " ".join("%.1f" % x for x in tr))
    P("")
    P("9. THE SCREEN: %d makers' documents read on 2 October 2026 and not taken (inputs/screen-2026-10-02.json; cited by address" % len(R["screen"]["rows"]))
    P("   and sha256, none filed). This is search history: it shows what was read, not that no other panel can qualify.")
    for r_ in R["screen"]["rows"]:
        P("   %s, %s: %s (sha256 %s); %s" % (r_["maker"], r_["model"], r_["why_not"], r_["sha256"][:16], r_["url"]))
    P("   in the tree already: %s" % R["screen"]["in_the_tree_already"])
    P("")
    P("10. ROUTE 2, PANEL-ACC: ONE IDENTIFIED UNIT, ACCEPTED BY ITS OWN MEASUREMENT (O-1's controlled unit)")
    P("   THE UNIT (SESSION): one SunPower SPR-E-Flex-100, recorded by serial number. The three typical rows under the same contract:")
    for c in (spr, bgv, sbx):
        a = R["acc_cands"][c["key"]]
        P("     %-60s A-1 %.3f V (%s); A-2 %.3f W lower bound (%s); A-3(b) %.2f A (%s); A-3(c) %.2f A" % (
            c["name"], a["a1"], "pass" if a["a1_ok"] else "FAIL", a["a2"]["p_low"], "pass" if a["a2_ok"] else "FAIL",
            a["a3b"], "pass" if a["a3b_ok"] else "FAIL", a["a3c"]))
    sa = R["acc_cands"]["SBX"]
    P("   Why SunPower: BougeRV's rated curve gives the stage nothing at the corner (A-2); Solbian's rated row passes A-1 with %.3f V"
      % (R["v_oc"] - sa["a1"]))
    P("   to spare against SunPower's %.3f V, and its hot short circuit is %.2f A before any allowance, where the 1.25 its own maker does"
      % (R["v_oc"] - ra["a1"], sa["isc_hot"]))
    P("   not print (SunPower's, transferred) puts it over 10 A; SunPower's 1.25 is its own instruction. It is the energy record's pinned panel.")
    P("   THE MEASUREMENTS ON THE UNIT (Layer 6; the owner's purchase and measurement):")
    P("     M1  the I-V curve at STC (25 C cells, 1000 W/m2): Isc, Voc25, Vmp, Imp")
    P("     M2  Voc at %.0f +- %.0f C cells and 1000 W/m2 (a cooled flash or a cold-chamber measurement): Vm20" % (R["t_cold"], SPEC_TM))
    P("     M3  Voc at 25 C at a second irradiance of at most 500 W/m2: the slope A25 = dVoc / d ln G, so n = A25 / (Ns kT/q at 298.15 K)")
    P("     A2m the current at A-2's corner (below)")
    P("     (M5, optional and not an acceptance row: Voc under an irradiance above 1000 W/m2 on the cold unit, for the disturbance check)")
    P("   THE MEASUREMENT SPECIFICATION (SESSION; the laboratory states its expanded uncertainties, k = 2, each at or under these):")
    P("     U_V %.2f V on each voltage (M2's cell temperature inside it); U_A %.0f %% of A25; U_I %.0f %% of a current; U_G %.0f %% of A-2's"
      % (spec["u_v"], 100 * spec["u_a"], 100 * spec["u_i"], 100 * spec["u_g"]))
    P("     irradiance setting; U_TC %.1f K on A-2's cell temperature" % spec["u_tc"])
    P("   THE ACCEPTANCE (on the unit's own measurements):")
    P("     A-1 THE WINDOW: Vm20 + U_V <= %.3f V (no slope, no extrapolation, no temperature scaling)" % R["v_oc"])
    P("     A-2 USEFUL CHARGING, MEASURED at SC-37's noon corner, offset to the conservative side: irradiance at or under %.1f W/m2"
      % R["g_noon"])
    P("         minus U_G (%.1f W/m2 at the specification), cells at or above %.2f C plus U_TC (%.2f C), the current I read at the panel"
      % (R["a2_corner"][0], R["tc_noon"], R["a2_corner"][1]))
    P("         voltage %.3f V + I x R_lead (the 5 m lead, %.4f Ohm, ESTIMATE as the record states it); P = %.3f V x I; accepted on"
      % (R["hold_cond"][1], R["rl"], R["hold_cond"][1]))
    P("         P - U_P strictly above %.6f W, U_P = %.3f V x sqrt((U_I I)^2 + (dI/dV U_V)^2) with dI/dV the measured local slope" % (
        R["p_use"], R["hold_cond"][1]))
    sg, sf = R["a2_signs_rated"], R["a2_signs_floor"]
    P("         why the offsets are conservative (the model's signs at the corner, the rated unit / the floor unit): dI/dG %+.5f / %+.5f A"
      % (sg["di_dg"], sf["di_dg"]))
    P("         per W/m2 (less light, less current); dI/dT %+.5f / %+.5f A/K (warmer cells, less current); the hold %.3f V lies above Vmp"
      % (sg["di_dt"], sf["di_dt"], R["hold_cond"][1]))
    P("         there, %.3f / %.3f V (%.3f / %.3f V at the unshifted noon)" % (sg["vmp"], sf["vmp"], sg["vmp_noon"], sf["vmp_noon"]))
    P("     A-3 THE ENTRY, THREE CASES:")
    r7 = R["l4e7r"]
    P("       (a) normal operation: the entry carries the stage's input current, independent of irradiance. L4-E7R (accepted, checks 3")
    P("           and 4) holds it two ways. The primary limit REGULATES it: the LT8705A at RIMON_IN %s (%s), %.4f A nominal, at"
      % (r7["reg"][0], r7["reg"][1], R["i_reg_nom"]))
    P("           most %.4f A at 25 V under the joint assumptions:" % R["i_reg_hi"])
    P("             %s" % r7["joint"][0])
    P("           The backstop does NOT limit: it turns the stage off (SWEN low) when the input current reaches its trip, at most")
    P("           %.4f A at 25 V (%.4f A at its lowest), so no steady entry current exceeds" % (R["i_trip_max"], R["i_trip_min"]))
    P("           %.4f A even if the regulation's unprinted values pass their assumptions (the overlap is then a hiccup); during a trip's"
      % R["i_trip_max"])
    P("           response (at most %s ms) the source's own current flows, at most A-3(b)'s. The bound kept here," % r7["resp"][0])
    P("           %.4f W / %.3f V = %.4f A" % (max(R["stack_c"][0], R["stack_c"][2]), R["stack_c"][1], R["i_norm_max"]))
    P("           (L4-E7's first-round stack C corner at RIMON_IN 23.2k, L4-E7 out 4), stays the conservative upper bound, above the")
    P("           backstop's %.4f A and the regulation's %.4f A, under %.0f A; CONDITIONAL with A-4" % (R["i_trip_max"], R["i_reg_hi"], R["entry_a"]))
    P("       (b) a sustained input fault (a short downstream of F2, D4 failing short for example): the panel's Isc for hours, hot cells")
    P("           +%.0f C, (1 + U_I), x %.2f, the maker's own sizing allowance, at or under %.0f A. SunPower 524958 Rev F prints it in" % (
        T_ISC_HOT, K_CLAUSE, R["entry_a"]))
    P("           section 3.0 (PDF p.2; the coordinator's direction named section 5.1, which holds the operating temperature), verbatim:")
    P("           \"%s\"" % R["clause_quote"])
    P("       (c) the enhancement transient during an existing input fault (a double contingency): F2 opening is the safe outcome; if")
    P("           F2 holds, J_SOLAR and the PV_IN conductors carry Isc_hot (1 + U_I) x G_T / 1000 for the event. G_T = %.1f W/m2 is a"
      % R["g_t"])
    P("           SESSION design level for this case only (the source's enhancement on E0; a design level, not a claimed maximum).")
    P("           J_SOLAR's held catalogue (JST VH, p.1) prints '%s' and '%s' and %s: COMPONENT_LIMITATION," % (
        R["vh_rating"], R["vh_temp"], "a short-time overload" if R["vh_overload"] else "no short-time overload"))
    P("           carried as PANEL-ACC row A-3(c): J_SOLAR and PV_IN rated at least that current at their maximum ambient, or a bench row")
    P("     A-4 the 100 W into the stage rests on two layers, as L4-E7R states them (accepted, checks 3 and 4): the primary limit, the")
    P("         LT8705A's regulation at RIMON_IN %s, its own 25 V corner %s W, CONDITIONAL on its unprinted values staying inside the"
      % (r7["reg"][0], r7["own"][0]))
    P("         joint assumptions above; and the backstop (approach C: the WSL2512 sense bank, the INA169, the TPS3701 and the TPS3808")
    P("         holding SWEN low, SWEN off by default, with the CS101 correction: the bulk ahead of the bank and the INB filter), its")
    P("         static bound %s W, margin %s W, CONDITIONAL on G_CM (break-even %s %%) and U18's VIN+ bias (break-even %s mA):"
      % (r7["dec"][0], r7["dec"][1], r7["dec"][2], r7["dec"][3]))
    P("         \"%s\" (L4-E7 out 10). Both are drafted, not applied; the unit's" % r7["crit"][0])
    P("         maximum at -20 C, 1000 W/m2 is %.1f W, over 100 W as drawn (section 5). Not a measured condition of the unit" % max(
        x[5] for x in spr["power"] if x[0] == "nominal"))
    P("   THE DEMONSTRATION ON A UNIT EQUAL TO THE TYPICAL ROWS (INFERRED: the sheet's coefficient, the larger of its two readings, gives")
    P("   Vm20; the energy record's fit gives the curve; a real unit replaces each by its measurement):")
    P("     Voc25 %.3f V, Vm20 %.4f V, Isc %.2f A" % (ru["v25"], ru["vm20"], ru["isc"]))
    P("     A-1 %.4f V: %s, margin %.4f V" % (ra["a1"], "PASS" if ra["a1_ok"] else "FAIL", R["v_oc"] - ra["a1"]))
    P("     A-2 I %.4f A, P %.4f W, dI/dV %.4f A/V, U_P %.4f W, lower bound %.4f W: %s (above %.6f W)" % (
        ra["a2"]["i"], ra["a2"]["p"], ra["a2"]["didv"], ra["a2"]["u_p"], ra["a2"]["p_low"], "PASS" if ra["a2_ok"] else "FAIL", R["p_use"]))
    P("     A-3 (a) %.4f A: %s; (b) %.4f A (%.4f A before the factor): %s; (c) %.4f A at G_T, over J_SOLAR's 10 A: a downstream row" % (
        ra["a3a"], "PASS" if ra["a3a_ok"] else "FAIL", ra["a3b"], ra["isc_hot"], "PASS" if ra["a3b_ok"] else "FAIL", ra["a3c"]))
    P("         a 20 A part would cover the double contingency up to %.0f W/m2, %.2f x E0" % (A["g_20a"], A["g_20a"] / R["e0_max"]))
    P("   THE WINDOW for a unit of this curve shape (the unit's own measurements decide; these are the specification's limits):")
    P("     Voc25 from %.3f V (A-2's floor: %.4f x rated) to %.3f V (A-1's ceiling: %.4f x rated); Vm20 at most %.3f V" % (
        A["v25_floor"], A["k_floor"], A["v25_ceil"], A["k_ceil"], A["vm20_ceil"]))
    P("     the rated %.3f V lies inside it: %s; the window is not empty: %s" % (
        spr["voc"], "yes" if A["k_floor"] < 1.0 <= A["k_ceil"] else "NO", "yes" if A["k_floor"] < A["k_ceil"] else "NO"))
    P("     information: a laboratory without a cold chamber could extrapolate Vm20 from M1 with a coefficient measured to within %.1f %%"
      % (100 * A["ub_extrap_max"]))
    P("     for the rated unit; the contract keeps M2 measured")
    P("   THE ENERGY (the replay's A1 and A2), computed at L4-E7's first-round limit %.4f A as section 0 reproduces it. L4-E7R's accepted"
      % R["i_set"])
    P("   regulation (RIMON_IN %s, %.4f A nominal) leaves the conditioned upper corner's rows unchanged: %s (the SunPower's highest"
      % (r7["reg"][0], R["i_reg_nom"], "yes" if R["corner_unmoved"] else "NO"))
    P("   current there on SC-37's day %.4f A, under the regulation's nominal and C's lowest trip %.4f A); it moves the nominal hold's"
      % (R["corner_i"][0], R["i_trip_min"]))
    P("   day to %s Wh (L4-E7 out 10, %s h bound; %s / %s Wh at the lower and upper corners) against the 350.0 Wh below (the panel's"
      % (r7["energy"][1], r7["energy"][4], r7["energy"][0], r7["energy"][2]))
    P("   highest current at the nominal hold %.4f A, over the regulation's nominal)" % R["corner_i"][1])
    for lab, vh, tot, nl, zh, noon_w, rr, tr in R["acc_runs"]:
        P("     %s (%.3f V): %.1f Wh a day; at noon %.2f W; [%d limited, %d daylight hours with no input]" % (lab, vh, tot, noon_w, nl, zh))
        for ak in ("A1", "A2"):
            st, u48, u72, add = rr[ak]
            P("       %s: first interruption h %s; unserved %.1f / %.1f at 48 h, %.1f / %.1f at 72 h; least addition %s" % (
                ak, "/".join("-" if x is None else str(x) for x in st), u48[0], u48[1], u72[0], u72[1],
                " / ".join("-" if a is None else "+%.1f" % a for a in add) + " Wh"))
        P("       the trace (W, hours 0 to 23): %s" % " ".join("%.1f" % x for x in tr))
    P("   (the floor unit's lower bound at A-2's corner is %.4f W, on the useful-power line; its trace's noon figure carries the" % (
        A["floor"]["a2"]["p_low"]))
    P("   replay's PVGIS convention, at the unshifted noon)")
    P("")
    D = R["dist"]
    P("11. THE DISTURBANCE CHECK: COMPONENT LIMITS DURING AN IRRADIANCE BURST ON COLD-SOAKED CELLS (TRN-001, apart from the window)")
    P("   THE LIMIT: the lowest rating on PV_P for a current-limited source held for minutes is D4's printed standoff, the SMCJ28A's")
    P("   VR %.1f V (at most %.0f uA there; Littelfuse SMCJ sheet p.2, the row VR %.1f / VBR %.2f to %.2f V at %.0f mA / VC %.1f V at %.1f A /"
      % (R["d4_vr"], R["d4_ir_ua"], R["d4_row"][0], R["d4_row"][1], R["d4_row"][2], R["d4_row"][3], R["d4_row"][4], R["d4_row"][5]))
    P("   IR %.0f uA). The sheet prints VBR(TJ) = VBR(25 C) x (1 + aT (TJ - 25)), aT typical %.1f %%/C (p.1): the cold VBR minimum at %.0f C"
      % (R["d4_row"][6], 100 * R["d4_alpha_t"], R["t_cold"]))
    P("   is %.2f V (a typical coefficient). C11 and C12's %.0f V lie above." % (R["d4_vbr_cold"], R["cap_v"]))
    P("   THE IRRADIANCE TERM, by junction physics, not by a measured slope: dVoc / d ln G <= n x Ns x kT/q, Ns %d (the sheet), T %.2f K"
      % (D["ns"], R["t_cold"] + 273.15))
    P("   (kT/q %.6f V); n_max = %.0f is a MODELLING_ASSUMPTION (the silicon junction's ideality ceiling: 1 for diffusion, 2 for" % (
        D["vt_cold"], N_MAX))
    P("   depletion-region recombination); M3's measured n = A25 / (Ns kT/q at 298.15 K, %.6f V) must read at or under %.0f with its"
      % (D["vt_25"], N_MAX))
    P("   uncertainty, else this check is re-judged (the typical unit's fit: n %.4f, %.4f with U_A)." % (D["n_meas_typ"], D["n_meas_typ_upper"]))
    P("   THE COLDEST CELLS ARE THE WORST CASE: d/dT [Voc(T, 1000) + n Ns kT/q ln(G / 1000)] = beta + n Ns k/q ln(G / 1000); up to the")
    P("   threshold below the second term is at most %.3f V / %.2f K = %.6f V/K, against the sheet's coefficient of at least %.4f V/K"
      % (D["dv"], R["t_cold"] + 273.15, D["dlog_dt_max"], D["beta_mag_min"]))
    P("   in magnitude (the smaller of its two readings): the derivative stays negative, so cells warmer than %.0f C give less." % R["t_cold"])
    P("   THE THRESHOLD: a unit at A-1's ceiling (Vm20 + U_V = %.3f V) reaches D4's %.1f V standoff at G = 1000 exp(%.3f V / (n Ns kT/q)):"
      % (R["v_oc"], R["d4_vr"], D["dv"]))
    for lab, n, slope, g_thr, mult in D["rows"]:
        P("     %-56s n %.4f: %.4f V per unit of ln G; %.0f W/m2, %.2f x E0" % (lab, n, slope, g_thr, mult))
    P("   RESULT: the disturbance check is implied by A-1 for every plane-of-array irradiance below %.0f W/m2 (n <= 2), %.2f x the"
      % (D["g_thr_dec"], D["g_thr_dec"] / R["e0_max"]))
    P("   extraterrestrial irradiance; no irradiance maximum is a decision input. ASSUMPTION: the plane-of-array irradiance stays below")
    P("   that threshold (the context of section 1 puts the read enhancement at %.1f W/m2 on E0). Its impact if it fails: D4 rises above"
      % D["enh_level"])
    P("   its standoff and conducts under %.0f mA until its VBR (%.2f V cold minimum), no damage below VBR. Its verification: none beyond"
      % (R["d4_row"][3], R["d4_vbr_cold"]))
    P("   M3's n check (M5 optional). Cross-check: SunPower's own allowance, 1.25 x Voc for component voltage ratings, is %.2f V on the"
      % D["clause_v_rated"])
    P("   rated row and %.2f V at the window's Voc25 ceiling, both under the %.1f V standoff." % (D["clause_v_ceil"], R["d4_vr"]))
    P("")
    P("12. THE DECISION ON U-03 (SESSION): TWO ROUTES")
    P("   Route 1, a maker-bound sheet: bounded in the window by the printed band AND the hold inside the curve at the conditioned upper")
    P("   corner over that band AND portable:")
    for c in (spr, bgv, sbx):
        P("     %-60s bounded %s; hold %s; portable %s -> %s" % (
            c["name"], "yes" if c["bounded"] else "NO", "yes" if c["reach_cond_upper"] else "NO", "yes" if c["portable"] else "NO",
            "QUALIFIES" if c["qualifies"] else "does not qualify"))
    P("     on EA3's typical band (upper corner %.3f V) instead: %s" % (R["hold_typ"][2], "; ".join(
        "%s %s" % (c["key"], "qualifies" if c["qualifies_typ"] else "does not qualify") for c in (spr, bgv, sbx))))
    P("   Route 2, a controlled unit: PANEL-ACC's contract (section 10) has a non-empty window that holds the identified panel's typical")
    P("   rows, with A-1, A-2, A-3(a) and A-3(b) met at the specification: %s" % ("yes" if R["route2"] else "NO"))
    P("   U-03: %s." % R["decision"])
    if R["decision"].startswith("CONDITIONAL"):
        P("   It is not an architecture-level choice: REQ-016's window, the stage, its hold and its 100 W control stay, and the panel is")
        P("   selected downstream by measurement. It is CONDITIONAL on: a bought unit passing A-1, A-2 and A-3(b) by its own measurement")
        P("   (M1 to M3 and A-2's reading at the specification); L4-E7R's regulation and backstop applied (A-3(a) and A-4, the backstop's")
        P("   %s W CONDITIONAL on G_CM and the VIN+ bias); A-3(c)'s connector and conductor rating at Layer 5/6; the disturbance check's"
          % R["l4e7r"]["dec"][0])
        P("   assumption (section 11) and M3's n;")
        P("   the unit's trace rerun (A1, A2). None of these can overturn the architecture: A-3(c) is a connector rating (REQ-016's 'rated")
        P("   10 A' is a minimum), and the rest decide a unit, not the topology.")
        P("   NO PHYSICAL UNIT IS ACCEPTED: none is bought or measured; the purchase and the measurement are the owner's actions (money).")
        P("   Route 1 stays open beside it: the drafts in clarification/ ask the two hold-matched makers for a warranted band (the owner")
        P("   sends them; the session contacts no outside party). REQ-016 need not change, so no owner question is raised.")
    P("   THE DOWNSTREAM ITEM, PANEL-ACC (Layer 6, component selection; the purchase is the owner's): accept the panel by route 1 (the")
    P("   bought revision's document, filed with its sha256, bounds its band in the window and keeps the hold inside the curve, sections")
    P("   3 and 4) or by route 2 (the identified unit passes A-1, A-2 and A-3(b) at the specification, section 10); in either case rerun")
    P("   its trace through the replay's section 12 and L4-E7's section 5 (A1 and A2), rate J_SOLAR and PV_IN for A-3(c), keep F2's and")
    P("   J_SOLAR's %.0f A minimum and the 100 W on L4-E7's limit (A-3(a), A-4), and check M3's n against the disturbance threshold." % R["entry_a"])
    P("")
    P("13. EVIDENCE CLASSES: MAKER (SunPower's sheet and guide, Solbian's sheet, Littelfuse's SMCJ sheet, JST's VH catalogue),")
    P("    MAKER-PAGE (BougeRV's page, transcribed), RECORD (the replay's and L4-E7's outputs, the stage's drive power), LITERATURE")
    P("    (the enhancement and the Cabauw quotations, CC BY 4.0, context only), MODELED (the energy record's single-diode model and day),")
    P("    INFERRED (the window ratios, the demonstration unit, A-2's signs, the cell temperature at the hot end), ASSUMPTION (S0 and the")
    P("    orbit's eccentricity as physical constants; a band's voltages scaled with its currents kept; BougeRV's rows taken as STC; the")
    P("    irradiance below the disturbance threshold), MODELLING_ASSUMPTION (n_max = 2), COMPONENT_LIMITATION (J_SOLAR prints no")
    P("    short-time overload), SESSION (the window's reading, the 10 % sentence's reading, the hold screen, the conditioned band,")
    P("    PANEL-ACC's unit, measurements and specification, the useful-power line, A-3(c)'s design level).")
    return "\n".join(o) + "\n"


def main():
    R = compute()
    sys.stdout.write(render(R))
    return 0


if __name__ == "__main__":
    sys.exit(main())
