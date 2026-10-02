#!/usr/bin/env python3
"""l4e13_panel.py: layer 4 task L4-E13 (MESHSAT-1357, 2 October 2026): U-03, a solar panel whose MAKER's document bounds its
open-circuit voltage at the coldest operating temperature inside REQ-016's window.

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured. No generator, registry, Layer 3 file or
other record is edited. For each candidate panel (the present one, SunPower's SPR-E-Flex-100, and at most two more) this
script reads the maker's printed rows from the pinned document and prints:
  - the open-circuit voltage at REQ-024's coldest in-use temperature (-20 C) at the top of the maker's printed band, with
    the maker's coefficient, against REQ-016's 25 V; a band the maker does not print is not invented (NOT BOUNDED);
  - the panel against the input hold of board E's stage (L4-E7's selected settings: 17.593 V nominal, 16.970 / 18.221 V
    with EA3 at its typical gain, 16.420 / 18.813 V the widest conditioned band): whether the hold lies inside the curve at
    the design day's noon over the printed band, the maximum-power voltage over the day, and the energy into the stage on
    SC-37's mean September day at every hold corner, with and without the drafted input-current limit;
  - the power into the stage against REQ-016's 100 W, the hot short-circuit current against the entry's 10 A, and the
    panel's portable class from its own document;
  - the window against the printed bands: the widest spread of open-circuit voltage (top over bottom of a band) a panel of
    each candidate's curve shape can have and still be both bounded at 25 V and held at the conditioned upper corner;
  - A1 and A2 (the replay's own meanday and least, unchanged) on each candidate's trace;
  - the decision on U-03 by a stated predicate, and the downstream item.

The model is the energy record's, not a new one: l4e_replay.main() runs here with its locals captured and must print
l4e_replay.out byte for byte; this script's trace must equal the replay's trace hour for hour on the SunPower panel, its
day sums must equal the replay's section 12 and L4-E7's section 5 at every hold printed there, and A1 and A2 on the SunPower
trace at L4-E7's nominal hold and limit must equal L4-E7's printed rows (exit 4 otherwise).

Evidence classes: MAKER (a maker's document, page named), MAKER-PAGE (a maker's web page, transcribed and filed), RECORD (a
committed output read by pattern), MODELED (the energy record's model), INFERRED (arithmetic on the above with a stated
step), ASSUMPTION (a figure no document gives), SESSION (a reading or choice this record takes, with its reason).

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
    "l4e7_out": ("v2/docs/records/l4e7/l4e7_stage_settings.out", "66fb58ef99fe7e816ed6f5bfe0abbd33a0c7f081641db4dbb8cca91278a331d1"),
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
}

# The few figures and readings this record sets itself (each named where it is used)
G_STC = 1000.0        # SESSION: the bound puts STC irradiance on cells still at the ambient (a cold, clear sunrise before the
                      # cells warm); with no irradiance the cells sit at the ambient, and less irradiance only lowers Voc
G_EDGE = 1250.0       # SESSION, a sensitivity only: an irradiance 25 % above STC (edge of cloud), on the fit's log term (INFERRED)
T_ISC_HOT = 70.0      # a1solar's convention for the hot short-circuit current (array_calc.T_HOT): cells at +70 C, 1000 W/m2
K_CLAUSE = 1.25       # SunPower 524958 Rev F 3.0's multiplier of Isc and Voc for component ratings (the one such clause held)
DAY_FRACTION = 0.05   # SESSION: the day's maximum-power voltage band is read over the hours with at least 5 % of the peak irradiance
ENTRY_A = 10.0        # REQ-016's acceptance: F2 and J_SOLAR rated 10 A
PORTABLE_KG = 2.5     # SESSION: "portable" is a flexible or folding class at or under 2.5 kg (the 100 Wp class weighs about 2 kg;
                      # the registry carries no owner ruling on a panel's class or mass)
# a panel-class word beside "panel" or "array" in one sentence (a bare "blanket" also means "blanket approval", D-26)
PANEL_CLASS = re.compile(r"(?i)\b(foldable|folding|flexible|semi-rigid|blanket)\b[^.]{0,60}\b(panel|array)s?\b|"
                         r"\b(panel|array)s?\b[^.]{0,60}\b(foldable|folding|flexible|semi-rigid|blanket)\b")
CLASSES = ("MAKER", "MAKER-PAGE", "RECORD", "MODELED", "INFERRED", "ASSUMPTION", "SESSION")


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
        if c["band"] is None:
            c["bound"], c["readings"], c["bounded"] = None, [], False
        else:
            top = c["band"][1]
            rd = [("band top %.4f x rated, the coefficient relative to the unit's Voc" % top, AC.voc_at(scaled(c, top, True), R["t_cold"]))]
            if c.get("beta_voc_abs") is not None:
                rd.append(("band top %.4f x rated, the sheet's absolute coefficient" % top, AC.voc_at(scaled(c, top, False), R["t_cold"])))
            else:
                rd.append(("band top %.4f x rated, the coefficient's change taken on the rated Voc" % top,
                           c["voc"] * top + abs(c["beta_rel"]) * c["voc"] * (25.0 - R["t_cold"])))
            if c is spr:
                rt = spr["band_records"][1]
                rd.append(("the records' reading, rated x %.2f, the absolute coefficient (L4-ENERGY O-1)" % rt,
                           AC.voc_at(scaled(c, rt, False), R["t_cold"])))
            c["readings"] = rd
            c["bound"] = max(v for _l, v in rd)
            c["bounded"] = c["bound"] <= R["v_oc"] + 1e-9
            c["edge"] = voc_model(AC.Diode(scaled(c, top, True)), G_EDGE, R["t_cold"])
            if abs(voc_model(AC.Diode(scaled(c, top, True)), G_STC, R["t_cold"]) - rd[0][1]) > 1e-6:
                refuse(4, "%s: the fit's Voc at STC irradiance and -20 C is not the coefficient's" % c["name"])
        c["k_bound"] = R["v_oc"] / c["voc_cold_nom"]           # the largest factor on the rated Voc that stays at 25 V
        c["tol_needed_up"] = c["k_bound"] - 1.0
        c["edge_nom"] = voc_model(c["fit"], G_EDGE, R["t_cold"])
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
        c["tol_needed_down"] = 1.0 - c["k_reach_cond"]
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
    # ---------------------------------------------------------------- the decision
    R["qualifying"] = [c["key"] for c in cands if c["qualifies"]]
    R["bounded_any"] = [c["key"] for c in cands if c["bounded"]]
    R["decision"] = "DOWNSTREAM" if R["qualifying"] else "OPEN"
    for c in cands:
        c["acc_ceiling"] = c["k_bound"] * c["voc"]               # a unit's Voc at STC at or under this is bounded at -20 C
        c["acc_floor"] = c["k_reach_cond"] * c["voc"]            # and at or over this reaches the conditioned upper corner at noon
    return R


# ====================================================================================== the printed record
def render(R):
    o = []
    P = o.append
    cands = {c["key"]: c for c in R["cands"]}
    spr, bgv, sbx = cands["SPR"], cands["BGV"], cands["SBX"]
    P("L4-E13 (MESHSAT-1357): U-03, A PANEL WHOSE MAKER'S DOCUMENT BOUNDS ITS OPEN-CIRCUIT VOLTAGE AT THE COLDEST OPERATING")
    P("TEMPERATURE INSIDE REQ-016'S WINDOW. Prototype design, desk arithmetic: nothing bought, built, powered or measured.")
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
    P("")
    P("1. THE REQUIREMENT AND THE TEMPERATURE")
    P("   REQ-016 (v2/ecad/tools/pcb_requirements.yaml), verbatim: \"%s\"" % R["req016"])
    P("   read: at most %.0f V open circuit at the panel's coldest operating temperature; held at %.1f V; at most %.0f W into the stage;"
      % (R["v_oc"], R["v_hold_req"], R["p_win"]))
    P("   its acceptance: F2 and J_SOLAR rated %.0f A. A series diode or a clamp in place of the panel's own open circuit: %s"
      % (R["entry_a"], "admitted by the text" if R["series_admitted"] else "NOT admitted (the statement constrains the panel's own open circuit; D4 is judged apart under TRN-001)"))
    P("   the coldest operating temperature: %.0f C, REQ-024's in-use minimum (%s to +%s C ambient; pcb_envelope.yaml in_use agrees);"
      % (R["t_cold"], R["req024_range"][0], R["req024_range"][1]))
    P("   the records settle REQ-016's reading at the kit's use boundary (L4-ENERGY-ARCHITECTURE.md, 'What stays INCONCLUSIVE'); the")
    P("   panels' own -40 C ratings are printed for information only.")
    P("   SESSION (the assumption the brief asks to state): with no irradiance the cells sit at the ambient; the bound puts STC")
    P("   irradiance (%.0f W/m2) on cells still at %.0f C, a cold clear sunrise before the cells warm. Less irradiance only lowers Voc;"
      % (G_STC, R["t_cold"]))
    P("   an edge-of-cloud %.0f W/m2 is printed beside it as a sensitivity (the fit's log term, INFERRED), not as part of the bound."
      % G_EDGE)
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
        P("     the model's fit (a1solar's single-diode model, imported and pinned): %s" % c["fit_note"])
    P("")
    P("3. THE BOUND: Voc AT %.0f C AT THE TOP OF THE MAKER'S BAND, WITH ITS COEFFICIENT, AGAINST %.0f V" % (R["t_cold"], R["v_oc"]))
    for c in (spr, bgv, sbx):
        P("   %s: rated Voc at %.0f C %.3f V (the typical row; %.3f V at -40 C, information)" % (
            c["name"], R["t_cold"], c["voc_cold_nom"], c["voc_m40_nom"]))
        if c["band"] is None:
            P("     NOT BOUNDED: the maker prints no open-circuit band, so no maximum exists on its document; the rated row leaves")
            P("     %.3f V (%.2f %%) to 25 V: the band's top could be at most %.2f %% above the rated Voc" % (
                R["v_oc"] - c["voc_cold_nom"], 100 * (R["v_oc"] - c["voc_cold_nom"]) / R["v_oc"], 100 * c["tol_needed_up"]))
        else:
            for lab, v in c["readings"]:
                P("     %-92s %.3f V" % (lab, v))
            P("     the bound (the largest reading) %.3f V: %s (margin %+.3f V); at %.0f W/m2 (sensitivity) %.3f V" % (
                c["bound"], "BOUNDED at or under 25 V" if c["bounded"] else "NOT BOUNDED: the maker's own band reaches past 25 V",
                R["v_oc"] - c["bound"], G_EDGE, c["edge"]))
            P("     the largest band top the rated row allows: %.2f %% above rated (the band printed: %+.2f / %+.2f %%)" % (
                100 * c["tol_needed_up"], 100 * (c["band"][0] - 1), 100 * (c["band"][1] - 1)))
    P("")
    P("4. THE HOLD: board E's input regulation (L4-E7, selected, drafted and not applied; RECORD l4e7_stage_settings.out)")
    P("   nominal %.3f V; EA3 at its typical gain %.3f / %.3f V; the widest conditioned band (EA3 at half, the drifts) %.3f / %.3f V"
      % (R["hold_typ"][1], R["hold_typ"][0], R["hold_typ"][2], R["hold_cond"][0], R["hold_cond"][1]))
    P("   the drafted input-current limit %.4f A (its lowest %.4f A at the nominal hold), taken flat; the 5 m lead %.4f Ohm (ESTIMATE)"
      % (R["i_set"], R["i_low"], R["rl"]))
    P("   SC-37's mean September day: noon is hour %d (%.1f W/m2, air %.2f C, cells %.2f C at NOCT %.0f C); the day's band is read over"
      % (R["h_noon"], R["g_noon"], R["ta_noon"], R["tc_noon"], R["noct_inf"]))
    P("   hours %d to %d (at least %.0f %% of the peak, SESSION). SESSION predicate: the hold lies inside the curve when the panel's"
      % (R["day_h"][0], R["day_h"][1], 100 * DAY_FRACTION))
    P("   open circuit at noon exceeds the hold corner, at every point of the printed band (a necessary condition: at the corner the")
    P("   stage takes nothing); the energy below says how much it takes. The band's voltages are scaled together with the rated")
    P("   currents kept (ASSUMPTION); the Voc coefficient as a fraction of each unit's Voc (SESSION, a1solar's coef()).")
    for c in (spr, bgv, sbx):
        P("   %s:" % c["name"])
        for v in c["variants"]:
            P("     %-12s Voc at STC %.3f V, Vmp at STC %.3f V; at noon Voc %.3f V, Vmp %.3f V; Vmp over the day %.3f to %.3f V" % (
                v["lab"], v["voc_stc"], v["vmp_stc"], v["voc_noon"], v["vmp_noon"], v["vmp_day"][0], v["vmp_day"][1]))
            P("     %-12s the hold inside the curve at noon: %s" % ("", "; ".join(
                "%.3f V %s" % (vh, "yes" if v["reach"][vh] else "NO") for vh in sorted(v["reach"]))))
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
        P("     as drawn the stage would take up to %.1f W (%s %.0f W); with the drafted limit at most %.1f W here (L4-E7 bounds the limit"
          % (c["p_drawn_max"], "over" if c["p_drawn_max"] > R["p_win"] else "under", R["p_win"], c["p_lim_max"]))
        P("     at 96.25 W to 25 V, CONDITIONAL on five unprinted values): the 100 W rests on the drafted limit, as for every candidate")
        P("     hot short circuit (+%.0f C cells, 1000 W/m2, the band's top) %.2f A against the entry's %.0f A; x %.2f (SunPower's rating"
          % (T_ISC_HOT, c["isc_hot"], R["entry_a"], K_CLAUSE))
        P("     clause, a1solar's convention) %.2f A: %s" % (c["isc_hot_clause"],
                                                          "inside %.0f A" % R["entry_a"] if c["isc_hot_clause"] <= R["entry_a"] else "OVER the entry's %.0f A" % R["entry_a"]))
    P("")
    P("6. PORTABLE CLASS (the makers' documents); SESSION: portable is a flexible or folding class at or under %.1f kg" % PORTABLE_KG)
    for c in (spr, bgv, sbx):
        P("   %-60s %s; %s; %.2f kg; operating %s" % (c["name"], c["class"], c["size"], c["mass"],
                                                       "%.1f to %.1f C" % c["t_range"] if c["t_range"] else "not printed"))
    P("   BougeRV's page limits operation to %.1f to %.1f C: the kit's -20 C is its own lower limit, and its upper limit sits under the" % bgv["t_range"])
    P("   cells' temperature in full sun at the envelope's +%.0f C ambient (%.1f C at 1000 W/m2 by the NOCT model at %.0f C, INFERRED)" % (
        R["t_hot_amb"], R["t_hot_amb"] + (R["noct_inf"] - 20.0) / 800.0 * 1000.0, R["noct_inf"]))
    P("")
    P("7. THE WINDOW AGAINST THE PRINTED BANDS (the gap, INFERRED on the model)")
    P("   A band's spread is its top over its bottom (as factors on the rated Voc). A panel of a given curve shape is bounded at 25 V")
    P("   only while its band top is at most k_bound (25 V over its rated Voc at %.0f C) and is held only while its band bottom is at least"
      % R["t_cold"])
    P("   k_reach (the hold's upper corner over its rated Voc at noon; the fit's Voc scales exactly with the voltages, checked). Both")
    P("   hold for some rating only while the spread is at most W = k_bound / k_reach.")
    for c in (spr, bgv, sbx):
        P("   %-60s k_bound %.4f; k_reach %.4f (%.3f V) / %.4f (%.3f V); W %.4f / %.4f (symmetric +-%.2f / +-%.2f %%); printed spread %s" % (
            c["name"], c["k_bound"], c["k_reach_cond"], R["hold_cond"][1], c["k_reach_typ"], R["hold_typ"][2], c["w_cond"], c["w_typ"],
            100 * (c["w_cond"] - 1) / (c["w_cond"] + 1), 100 * (c["w_typ"] - 1) / (c["w_typ"] + 1),
            "%.4f: %s" % (c["band_ratio"], "fits W" if c["band_ratio"] <= c["w_cond"] else "WIDER than W, no rating of this shape and band fits both")
            if c["band_ratio"] else "none printed"))
    P("   For the rated rows as they stand, the band a maker would have to print: SunPower %+.2f / %+.2f %%, Solbian SX 156 %+.2f / %+.2f %%"
      % (100 * spr["tol_needed_up"], -100 * spr["tol_needed_down"], 100 * sbx["tol_needed_up"], -100 * sbx["tol_needed_down"]))
    P("   (the top from the bound, the bottom from the conditioned upper corner's reach; the coefficient relative).")
    if bgv["k_reach_cond"] > 1.0:
        P("   BougeRV's rated row sits under its own reach floor (k_reach %.4f > 1): its rating, not only its band, is too low for the"
          % bgv["k_reach_cond"])
        P("   hold's upper corner.")
    P("")
    P("8. THE ENERGY CONSEQUENCE: A1 AND A2 ON EACH TRACE (the replay's meanday and least, unchanged; CORRECTED, WE, TYP; the service")
    P("   ledger; pairs 06 / 18 UTC). The 100 W screening stimulus gives %.1f Wh a day; the SunPower nominal trace %.1f Wh." % (
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
    P("   and sha256, none filed)")
    for r_ in R["screen"]["rows"]:
        P("   %s, %s: %s (sha256 %s); %s" % (r_["maker"], r_["model"], r_["why_not"], r_["sha256"][:16], r_["url"]))
    P("   in the tree already: %s" % R["screen"]["in_the_tree_already"])
    P("")
    P("10. THE DECISION ON U-03 (SESSION, by the predicate: bounded at or under 25 V by the maker's printed band AND the hold inside")
    P("    the curve at the conditioned upper corner over that band; portable)")
    for c in (spr, bgv, sbx):
        P("   %-60s bounded %s; hold %s; portable %s -> %s" % (
            c["name"], "yes" if c["bounded"] else "NO", "yes" if c["reach_cond_upper"] else "NO", "yes" if c["portable"] else "NO",
            "QUALIFIES" if c["qualifies"] else "does not qualify"))
    P("   on EA3's typical band (upper corner %.3f V) instead of the conditioned one: %s" % (R["hold_typ"][2], "; ".join(
        "%s %s" % (c["key"], "qualifies" if c["qualifies_typ"] else "does not qualify") for c in (spr, bgv, sbx))))
    if R["decision"] == "DOWNSTREAM":
        P("   U-03 becomes a downstream purchase item: %s" % ", ".join(R["qualifying"]))
    else:
        P("   NO CANDIDATE QUALIFIES. U-03 stays an unresolved choice; it decides the solar source, not the topology (REQ-016's window,")
        P("   the stage and its hold stay). REQ-016 need not change, so no owner question is raised.")
        P("   The exact gap: no maker's document read prints an open-circuit band narrow enough for this window. SunPower's band (10 %")
        P("   of measured) reaches %.3f V at %.0f C; BougeRV's (-5 / +10 %%) is bounded at %.3f V but its curve sits under the hold"
          % (spr["bound"], R["t_cold"], bgv["bound"]))
        P("   (its rated Voc at noon %.3f V against the conditioned upper corner %.3f V); Solbian prints none. The window admits a spread"
          % (bgv["voc_noon_nom"], R["hold_cond"][1]))
        wl, wh = min(c["w_cond"] for c in (spr, bgv, sbx)), max(c["w_cond"] for c in (spr, bgv, sbx))
        P("   of at most %.4f to %.4f (the shapes above), a symmetric band of about +-%.1f to +-%.1f %%; the rated rows of the two panels"
          % (wl, wh, 100 * (wl - 1) / (wl + 1), 100 * (wh - 1) / (wh + 1)))
        P("   that match the hold need a band top of at most %+.2f %% (SunPower) and %+.2f %% (Solbian)." % (
            100 * spr["tol_needed_up"], 100 * sbx["tol_needed_up"]))
        P("   The next bounded action: (1) the makers' written open-circuit band for the two hold-matched panels, asked by the drafts in")
        P("   clarification/ (the owner sends them; the session contacts no outside party); (2) failing a written band, O-1's own")
        P("   alternative closure, a controlled unit at Layer 6: the unit bought (the owner's money) is accepted only when its Voc,")
        P("   measured at a known cell temperature and irradiance and corrected to STC with its expanded uncertainty U, lies inside")
        for c in (spr, sbx):
            P("     %-28s %.3f V + U to %.3f V - U (its coefficient's own uncertainty inside U)" % (c["name"], c["acc_floor"], c["acc_ceiling"]))
        P("   (the floor is the hold's necessary condition: a unit there gives the stage nothing at the conditioned upper corner at noon;")
        P("   the unit's own trace, rerun, decides its energy)")
        P("   A series diode or a clamp is not a substitute (section 1).")
    P("   THE DOWNSTREAM ITEM (Layer 6, component selection; the purchase is the owner's): PANEL-ACC. Accept the bought panel when")
    P("   the maker's document of the bought revision, filed with its sha256, bounds Voc at %.0f C at or under %.0f V by section 3's rule"
      % (R["t_cold"], R["v_oc"]))
    P("   and its band keeps the hold inside the curve by section 4's rule, or, failing a printed band, when the unit itself passes the")
    P("   window above; then rerun its trace through the replay's section 12 and L4-E7's section 5 (A1 and A2), and re-read the")
    P("   entry's %.0f A for its hot short circuit." % R["entry_a"])
    P("")
    P("11. EVIDENCE CLASSES: MAKER (SunPower's sheet and guide, Solbian's sheet), MAKER-PAGE (BougeRV's page, transcribed), RECORD")
    P("    (the replay's and L4-E7's outputs), MODELED (the energy record's single-diode model and day), INFERRED (the window ratios,")
    P("    the cell temperature at the hot end, the edge-of-cloud term), ASSUMPTION (a band's voltages scaled with its currents kept;")
    P("    BougeRV's rows taken as STC), SESSION (the temperature reading, the 10 % sentence's reading, the coefficient as a fraction,")
    P("    the hold predicate and the day's 5 % hours, the conditioned band as the judged band).")
    return "\n".join(o) + "\n"


def main():
    R = compute()
    sys.stdout.write(render(R))
    return 0


if __name__ == "__main__":
    sys.exit(main())
