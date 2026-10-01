#!/usr/bin/env python3
"""l4e10_cell_thermal.py: layer 4 task L4-E10 (MESHSAT-1357, 2 October 2026). FEA-008: the cell and thermal design of the
battery path against REQ-046 and the temperature requirements, mode by mode (LO-01a to LO-01h of
v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md section 2.5, DR-06).

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured. No generator, registry, Layer 3 file or
other record is edited. Every figure carries its class: MAKER (a maker's specification, clause named), MODELED (the tree's
power and thermal model, records/rv-pwr/pwr_budget.py and records/hc2/pwr_red2.py, imported unchanged), INFERRED (the
method is stated), ASSUMPTION (a figure no held document gives, named where it is used), CONDITIONAL (a result that holds
only on a stated condition).

Order of the work, as the owner's refinement of 2 October 2026 asks: section 2 is a FEASIBILITY SCREEN of every required
charging, discharging, transport and storage condition (ambient, duration, configuration, the maker's limit, the power
available for thermal control, the gap, and a physically credible route or the reason one is rejected); thermal measures
are quantified only where the screen finds a credible route (section 3); the cells are compared alongside (section 4); the
decision per row, and where no option qualifies the exact conflict and at most three options for the owner (section 5).

Section 0 proves, before any figure is used (exit 4 otherwise):
  0a pwr_budget.py, re-run in a child with a scratch JSON path, prints pwr_budget.out and writes pwr_budget.json byte for byte;
  0b pwr_red2.py and 0c hotstop_bounds.py, re-run in children, reproduce their committed outputs byte for byte;
  0d pwr_red2.py imported here (its stdout captured) prints pwr_red2.out byte for byte, so its heat() and state tables are
     the ones that printed the record; pwr_budget.py and hotstop_bounds.py are imported (their main() is guarded).
Inputs are pinned by sha256 (exit 2 if a file differs). Held documents (v2/vendor/battery/held/, ignored by git) are
fetched by fetch_held_back.py beside this file.

Run from the repository root:  python3 v2/docs/records/l4e10/l4e10_cell_thermal.py > v2/docs/records/l4e10/l4e10_cell_thermal.out
Needs pdftotext and PyYAML. A few seconds. Exit 2: a pinned file differs or is missing; 3: an input cannot be parsed;
4: a reproduction or a predicate failed."""
import ast
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
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()

PB_PY = "v2/docs/records/rv-pwr/pwr_budget.py"
PB_OUT = "v2/docs/records/rv-pwr/pwr_budget.out"
PB_JSON = "v2/docs/records/rv-pwr/pwr_budget.json"
RED2_PY = "v2/docs/records/hc2/pwr_red2.py"
RED2_OUT = "v2/docs/records/hc2/pwr_red2.out"
HOT_PY = "v2/docs/records/hc2/hotstop_bounds.py"
HOT_OUT = "v2/docs/records/hc2/hotstop_bounds.out"
W4_PY = "v2/docs/records/w4/w4-scratch-thermal.py"
L3R2 = "v2/docs/handover/layer3/l3r2.yaml"
REG = "v2/ecad/tools/pcb_requirements.yaml"
ENV_Y = "v2/ecad/tools/pcb_envelope.yaml"
TP = "v2/docs/TEST-PLAN.md"
PT = "v2/docs/feasibility/POWER-THERMAL.md"
APPX = "v2/docs/MESHSAT-709-geometry-appendix.md"
CM = "v2/docs/CASE-MARGINS.md"
SL = "v2/docs/records/l3batt/SHORTLIST.md"
TC = "v2/docs/review-packets/battery/THERMAL-COORDINATION.md"
S35E11 = "v2/vendor/battery/samsung-35e-orbtronic.pdf"
S35E10 = "v2/vendor/battery/samsung-35e-akkuzentrum.pdf"
S30Q6 = "v2/vendor/battery/held/samsung-inr18650-30q6-v1.0-2020.pdf"
S30Q = "v2/vendor/battery/held/samsung-inr18650-30q-v1.0-2015.pdf"
S30QD = "v2/vendor/battery/held/samsung-inr18650-30q6-draft-v0.1-2024.pdf"
LGHG2 = "v2/vendor/battery/held/lg-inr18650hg2-rev0-2014.pdf"
MP28A = "v2/vendor/battery/molicel-inr18650-p28a-v1.pdf"
EATON = "v2/vendor/battery/eaton-scf9550-elx1135.pdf"
BQ77207 = "v2/vendor/battery/ti-bq77207.pdf"
BQ4050 = "v2/vendor/battery/ti-bq4050.pdf"
TRM = "v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf"
HEATER = "v2/vendor/battery/heater/rs-pro-245-556-heater-mat-sheet.pdf"
TOPWELL = "v2/docs/records/l4e10/inputs/topwell-hl18650v-page-2026-10-01.json"
PRICES = "v2/docs/records/l4e10/inputs/prices-2026-10-01.json"
PINS = {
    CM: "55244f94aace54ca09d98c100b9830cba75c70a4774c3ba375a14903fcaf6376",
    APPX: "852736b661a805e36305ca6c2c91ebb76794e883a2ccd75dc3274c25d65212f1",
    TP: "42a3dff33442c86089a2c6c9dee841e8e2c8b9cbc1222a4adc311902b3c316f7",
    PT: "ad3ba27cef9e0f684f28ce81815afa86d44c4114b9bc10ff474308d875ba5788",
    L3R2: "ee2efadf269994ce90830989714d3d48fecf0868b673e9f43e44b25b48fb091c",
    HOT_OUT: "5f03619f7bf5c476e57f90ef17e161989ceac6e9b0df8b40b25d60ed5dfdf825",
    HOT_PY: "ed8f8c6b4c3bed083883439ccfb9fc1a96bb4c3864fc4dc3bc3f934beb1dcf8f",
    RED2_OUT: "835910e807d588c481951dc879e030b55d893453bd124872b9310a99bed46db6",
    RED2_PY: "5790bc7e444bebc4b6b7b6616c4641dfe602185631992d19aeb223eb51e9feec",
    SL: "6a943a1fb0d47edf1977e39b0c1801f9319abdb8087015ccbea3a1c4a784e28c",
    PRICES: "86b28732d45dedb6dfd690382107b6a8bbbd0b194dd94d8336b2f71e865f12da",
    TOPWELL: "7d62d6be4368e92f5444a22c9978e32261ec761b695125edbc8124bb06e489f3",
    PB_JSON: "5a616902d2ddab82f25d34ab55d848d06011fb6fbe48c147221d6b442783e462",
    PB_OUT: "58e40cf604804cc9d70c7fbeb1012be4552563fcc8ae7ef6755003c33acb902f",
    PB_PY: "469d0820b046ef6ff5aceadf422b4166de3d6a02bc50fa5b0c3644704f0f9556",
    W4_PY: "6c83da5f7e3e4f0f5393bfe0f609ba02c423adbadfa3661a245d0a9b778e65c3",
    TC: "0d4d60f03260f004cd7af9d738e41bbdb5f5a1d4818fa33775328d0d264d41ec",
    ENV_Y: "35cf43a2b7098a76abb4919685ece4d6e352331628f5f242c1492d9fcbbf2864",
    REG: "b624ac495650a3592c45a37610375fb05bf7b775042cf3de7ec8979bc46a6e50",
    EATON: "3ecc2424acfa1753c2aec0b62d5706d4f25b7a08e731795c0d84d59938a3158e",
    HEATER: "5c0e331bc0051078cc373f87ed904a2fffaeb26dc1bffd0d79e54c524667fe7f",
    LGHG2: "b135f906d383a964ac7d4585d66acc762145aa739c20d7bfc60269d32d7857e9",
    S30Q: "a8f0918fb31e90b8f9a7c29acfb0854effc1ca3b3711d10d7fa972e211763464",
    S30QD: "931243bb08500750f2a20b72e985cc8896a465a375f383d9fe41d0d8429bd9c4",
    S30Q6: "652b3b98380428a112f147b830490e0da2aeec5b62eba04f1b6583ee963a61e1",
    MP28A: "05db826b40db2106639eb137047ecce6d8e6a1efb57fd57e70dfc01318d471d1",
    S35E10: "d2a7c686941c1f4237240ee140127e6828f6d590170cf5a7f30d945d1aab50a1",
    S35E11: "5ec577b952b9dc5106593a4e4c3a6e8cea64f6f72b8faaf1bb512155c29dc516",
    BQ77207: "45c1c99e2d303be8bcf1a2b1eea8275f657c7c80170bda7c2778042a688295cb",
    TRM: "525d16b2bdee44e5b587ccf6800b9967bc524772d0b5a20937957ea2e738b7ad",
    BQ4050: "2664e33fe6d6ebed3a0f58153d8ba8ce66cb84f07741f6708ae11a224f443f5e",
}

# The few figures this record sets itself (ASSUMPTION; each is used in one place and its effect is printed):
K_PAD = 1.0          # W/mK, a gap filler between the pack's east face and the east wall (no maker's sheet held; low end)
T_MAT = 0.0015       # m, the RS PRO heater mat's thickness (its sheet states none)
K_MAT = 0.2          # W/mK, the mat's silicone (its sheet states none)
COP = (0.5, 1.0)     # a thermoelectric cooler's coefficient of performance near these lifts (no module's sheet held)
HOT_RISE = 30.0      # K, the cooler's hot side at most this far above the ambient it rejects to
K_INS = 0.02         # W/mK, an aerogel-class insulating blanket (no maker's sheet held), only to size the layer section 2 rejects
CLASSES = ("MAKER", "MODELED", "INFERRED", "ASSUMPTION", "CONDITIONAL")


def refuse(code, msg):
    sys.stderr.write("l4e10_cell_thermal: %s; refusing\n" % msg)
    sys.exit(code)


def path(rel):
    return os.path.join(TOP, rel)


def sha(rel):
    p = path(rel)
    if not os.path.exists(p):
        refuse(2, "%s is missing (held documents: fetch_held_back.py)" % rel)
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def text(rel):
    return open(path(rel), encoding="utf-8").read()


_PDF = {}


def pdf(rel):
    if rel not in _PDF:
        r = subprocess.run(["pdftotext", "-layout", path(rel), "-"], capture_output=True)
        if r.returncode != 0:
            refuse(3, "pdftotext failed on %s" % rel)
        _PDF[rel] = r.stdout.decode("utf-8", "replace")
    return _PDF[rel]


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse(3, "%s not found" % what)
    return m


def load(name, rel, quiet=False):
    sp = importlib.util.spec_from_file_location(name, path(rel))
    m = importlib.util.module_from_spec(sp)
    buf = io.StringIO()
    if quiet:
        with contextlib.redirect_stdout(buf):
            sp.loader.exec_module(m)
    else:
        sp.loader.exec_module(m)
    return m, buf.getvalue()


def ast_consts(rel, names):
    tree = ast.parse(text(rel))
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            n = node.targets[0].id
            if n in names:
                out[n] = ast.literal_eval(node.value)
    missing = [n for n in names if n not in out]
    if missing:
        refuse(3, "%s lacks %s" % (rel, missing))
    return out


def f1(x):
    return "%.1f" % x


def f2(x):
    return "%.2f" % x


def floor1(x):
    return math.floor(x * 10.0 + 1e-9) / 10.0


def nums(s):
    return [float(v) for v in re.findall(r"[-+]?\d+(?:\.\d+)?", s.replace("~", " ~ "))]


# ------------------------------------------------------------------------------------------------ the maker sheets
def read_sheets():
    S = {}
    t = pdf(S35E11)
    S["35E_11"] = {
        "doc": "Samsung SDI INR18650-35E Ver. 1.1 (9 July 2015), %s" % S35E11,
        "c_min": float(need(t, r"Min (\d),(\d{3})mAh", "35E Ver. 1.1 3.1").group(1)) + float(need(t, r"Min (\d),(\d{3})mAh", "35E 3.1").group(2)) / 1000.0,
        "charge": tuple(map(float, need(t, r"3\.12 Operating Temperature\s+Charge : (\d+) to (\d+)°C", "35E 3.12 charge").groups())),
        "discharge": tuple(map(float, need(t, r"Discharge : (-?\d+) to (\d+)°C", "35E 3.12 discharge").groups())),
        "basis": need(t, r"\((Cell Surface Temperature)\)", "35E 3.12 basis").group(1).lower(),
        "st_1y": tuple(map(float, need(t, r"1 year :\s+(-?\d+)~(\d+)°C", "35E 3.13 1 year").groups())),
        "st_3m": tuple(map(float, need(t, r"3 months : (-?\d+)~(\d+)°C", "35E 3.13 3 months").groups())),
        "st_1m": tuple(map(float, need(t, r"1 month : (-?\d+)~(\d+)°C", "35E 3.13 1 month").groups())),
        "soc": need(t, r"ex-factory status \((30% of charge)\)", "35E 3.13 note").group(1),
        "i_cont": float(need(t, r"(\d),(\d{3})mA \(for continuous discharge\)", "35E 3.8").group(1)) * 1000 + float(need(t, r"(\d),(\d{3})mA \(for continuous discharge\)", "35E 3.8").group(2)),
        "dims": (float(need(t, r"Diameter: Max\. Φ (\d+\.\d+) mm", "35E 3.11 diameter").group(1)), float(need(t, r"Height : Max\. (\d+\.\d+) mm", "35E 3.11 height").group(1))),
        "cold10": need(t, r"Relative Capacity\s+(\d+)%\s+(\d+)%\s+(\d+)%", "35E 7.5").groups(),
        "car": bool(re.search(r"Don't leave, charge or use the battery in a car or similar place where inside of temperature may be\s+over 60°C", t)),
        "store60": bool(re.search(r"Store the battery at temperature below 60°C", t)),
    }
    S["35E_11"]["i_cont"] /= 1000.0
    m = need(t, r"Capacity after (\d+)cycles\.\s+Capacity ≥ ([\d,]+)mAh \((\d+)% of Standard Capacity\)", "35E 7.9")
    S["35E_11"]["cycle"] = "%s %% (%s mAh) after %s cycles, charge %s mA, discharge %s mA" % (m.group(3), m.group(2), m.group(1),
        need(t, r"\(charge current ([\d,]+)mA\)", "35E 7.9 charge").group(1), need(t, r"\(discharge current ([\d,]+)mA\)", "35E 7.9 discharge").group(1))
    t = pdf(S35E10)
    S["35E_10"] = {
        "doc": "Samsung SDI INR18650-35E Version No. 1.0, %s" % S35E10,
        "charge": tuple(map(float, need(t, r"Charge\s+: (\d+) to (\d+)°C \(Ambient\)", "35E V1.0 3.15 charge").groups())),
        "discharge": tuple(map(float, need(t, r"Discharge : (-?\d+) to (\d+)°C \(Ambient\)", "35E V1.0 3.15 discharge").groups())),
        "basis": "ambient",
        "st_1y": tuple(map(float, need(t, r"1 year :\s+(-?\d+)~(\d+)°C", "35E V1.0 3.16 1 year").groups())),
        "st_3m": tuple(map(float, need(t, r"3 months : (-?\d+)~(\d+)°C", "35E V1.0 3.16 3 months").groups())),
        "st_1m": tuple(map(float, need(t, r"1 month : (-?\d+)~(\d+)°C", "35E V1.0 3.16 1 month").groups())),
    }
    t = pdf(S30Q6)
    m = need(t, r"Min\. (\d),(\d{3})mAh", "30Q6 3.1")
    S["30Q6"] = {
        "doc": "Samsung SDI INR18650-30Q Version No. V1.0 (date of application 2020/01/17; the 30Q6 production code), %s" % S30Q6,
        "date": need(t, r"Date of Application \(YY/MM/DD\)\s+: (\d{4}/\d{2}/\d{2})", "30Q6 date").group(1),
        "c_min": float(m.group(1)) + float(m.group(2)) / 1000.0,
        "amb_charge": tuple(map(float, need(t, r"3\.14 Operating temperature\s+Charge : (\d+) to (\d+)℃", "30Q6 3.14 charge").groups())),
        "amb_discharge": tuple(map(float, need(t, r"\(Ambient\)\s+Discharge: (-?\d+) to (\d+)℃", "30Q6 3.14 discharge").groups())),
        "surf_charge": tuple(map(float, need(t, r"Charge : (\d+) to (\d+)℃\s*\n\s+\(recommended recharge release", "30Q6 3.15 charge").groups())),
        "surf_discharge": tuple(map(float, need(t, r"Discharge: (-?\d+) to (\d+)℃\s*\n\s+\(Cell Surface temperature\)", "30Q6 3.15 discharge").groups())),
        "release": float(need(t, r"must re-discharge release < (\d+)℃", "30Q6 release").group(1)),
        "st_1y": tuple(map(float, need(t, r"1 year\s+(-?\d+)~(\d+)℃", "30Q6 3.16 1 year").groups())),
        "st_3m": tuple(map(float, need(t, r"3 months\s+(-?\d+)~(\d+)℃", "30Q6 3.16 3 months").groups())),
        "st_1m": tuple(map(float, need(t, r"1 month\s+(-?\d+)~(\d+)℃", "30Q6 3.16 1 month").groups())),
        "soc": need(t, r"ex-factory status \((30% of charge)\)", "30Q6 note 3").group(1),
        "i_cont": float(need(t, r"3\.8 Max\. continuous discharge\s+(\d+)A\(Without temperature cut\)", "30Q6 3.8").group(1)),
        "dims": (float(need(t, r"Diameter : Max\. (\d+\.\d+) mm", "30Q6 diameter").group(1)), float(need(t, r"Height : Max\. (\d+\.\d+) mm", "30Q6 height").group(1))),
        "cold": need(t, r"23°C\s+-20℃\s+-10℃\s+0℃\s+23℃\s+60℃\s*\n\s+Relative Capacity\s+(\d+)%\s+(\d+)%\s+(\d+)%\s+(\d+)%\s+(\d+)%", "30Q6 7.6").groups(),
        "cutoff": float(need(t, r"3\.9 Discharge cut-off voltage\s+(\d\.\d)V", "30Q6 3.9").group(1)),
        "v_chg": float(need(t, r"3\.5 Standard charge\s+CCCV, [\d.]+A, (\d\.\d+)V", "30Q6 3.5").group(1)),
    }
    m = need(t, r"Capacity ≥ ([\d,]+)mAh @ after (\d+)cycles\s*\n\s*\((\d+)% of the standard capacity @ RT\)\s*\n\s*3\.10 Cycle life\s*\n\s+- Charge : (\d+)A, [^\n]*\n\s+- Discharge: (\d+)A", "30Q6 3.10")
    S["30Q6"]["cycle"] = "%s %% (%s mAh) after %s cycles, charge %s A, discharge %s A" % (m.group(3), m.group(1), m.group(2), m.group(4), m.group(5))
    t = pdf(S30Q)
    S["30Q_2015"] = {
        "doc": "Samsung SDI INR18650-30Q Version No. 1.0 (February 2015), %s" % S30Q,
        "surf_discharge": tuple(map(float, need(t, r"Discharge: (-?\d+) to (\d+)℃", "30Q 2015 3.11").groups())),
        "st_1y5": tuple(map(float, need(t, r"1\.5 year\s+(-?\d+)~(\d+)℃", "30Q 2015 3.12 1.5 year").groups())),
        "st_1m": tuple(map(float, need(t, r"1 month\s+(-?\d+)~(\d+)℃", "30Q 2015 3.12 1 month").groups())),
        "soc": need(t, r"ex-factory status \((40±5% SOC), 25℃\)", "30Q 2015 note").group(1),
        "car": bool(re.search(r"in a car or similar place where inside of temperature may be\s*\n?\s*over 60℃", t)),
        "store60": bool(re.search(r"Store the battery at temperature below 60℃", t)),
    }
    t = pdf(S30QD)
    S["30Q6_draft"] = {
        "doc": "Samsung SDI INR18650-30Q Draft V0.1 (date of application 2024/01/23, a customer draft), %s" % S30QD,
        "amb_discharge": tuple(map(float, need(t, r"\(Ambient\)\s+Discharge: (-?\d+) to (\d+)℃", "30Q6 draft 3.14").groups())),
        "st_1m": tuple(map(float, need(t, r"1 month\s+(-?\d+)~(\d+)℃", "30Q6 draft 1 month").groups())),
    }
    t = pdf(LGHG2)
    S["HG2"] = {
        "doc": "LG Chem INR18650HG2 product specification BCY-PS-HG2-Rev0 (13 October 2014), %s" % LGHG2,
        "discharge_2_9": tuple(map(float, need(t, r"Discharge\s+(-?\d+) ~ (\d+)℃", "HG2 2.9").groups())),
        "discharge_5_1": tuple(map(float, need(t, r"Battery must be discharged at operating temperature range (-?\d+) ~ (\d+)℃", "HG2 5.1").groups())),
        "st_1m": tuple(map(float, need(t, r"1 month\s+(-?\d+) ?~ ?(\d+)℃", "HG2 2.10 1 month").groups())),
        "st_1y": tuple(map(float, need(t, r"1 year\s+(-?\d+) ?~ ?(\d+)℃", "HG2 2.10 1 year").groups())),
    }
    t = pdf(MP28A)
    S["P28A"] = {
        "doc": "E-One Moli Energy MOLICEL INR-18650-P28A product data sheet, %s" % MP28A,
        "charge": tuple(map(float, need(t, r"Charge\s+(\d+)°C to (\d+)°C", "P28A charge").groups())),
        "discharge": tuple(map(float, need(t, r"Discharge\s+(-\d+)°C to (\d+)°C", "P28A discharge").groups())),
        "c_min": float(need(t, r"Minimum\s+(\d{4}) mAh", "P28A minimum").group(1)) / 1000.0,
        "ambient": "Ambient" in t,
        "storage": bool(re.search(r"[Ss]torage", t)),
    }
    j = json.load(open(path(TOPWELL), encoding="utf-8"))
    sp = j["specification_table_verbatim"]
    S["HL18650V"] = {
        "doc": "Yichun Topwell Power HL18650V product page (a maker's page, not a specification), reading %s" % TOPWELL,
        "c_min": float(need(sp, r"Min\. (\d{4})mAh", "HL18650V min").group(1)) / 1000.0,
        "dims": tuple(map(float, need(sp, r"Dimensions (\d+\.\d+)\*(\d+\.\d+)mm max", "HL18650V dims").groups())),
        "discharge": tuple(map(float, need(sp, r"Discharge: (-\d+)~(\d+)℃", "HL18650V discharge").groups())),
        "charge": tuple(map(float, need(sp, r"Charge: (-\d+) ~(\d+)℃", "HL18650V charge").groups())),
        "st_12m": tuple(map(float, need(sp, r"Storage Temperature Range (-?\d+)~(\d+)℃ 0 - 12 months", "HL18650V 12 months").groups())),
        "st_6m": tuple(map(float, need(sp, r"(-?\d+)~(\d+)℃ 0 - 6 months", "HL18650V 6 months").groups())),
        "st_3m": tuple(map(float, need(sp, r"(-?\d+)~(\d+)℃ 0 - 3 months", "HL18650V 3 months").groups())),
        "st_30d": tuple(map(float, need(sp, r"(-?\d+)~(\d+) ℃ Within 30 days", "HL18650V 30 days").groups())),
        "i_cont": float(need(sp, r"Max Continuous Discharge Current (\d+)A", "HL18650V current").group(1)),
        "cutoff": float(need(sp, r"Discharge Cut-off Voltage (\d\.\d+)V", "HL18650V cut-off").group(1)),
        "v_chg": float(need(sp, r"Charge Cut-off Voltage (\d\.\d+)V", "HL18650V charge V").group(1)),
        "company": j["company_named_on_page"], "url": j["url"], "page_sha": j["sha256"],
        "cycle": need(sp, r"Cycle Life (≥\d+ times \(25 ℃，0\.5 C / 1C \))", "HL18650V cycle").group(1).replace("≥", "at least ").replace(" ℃，", " C, ").replace("( ", "(").replace(" )", ")"),
    }
    t = pdf(EATON)
    S["F2"] = {
        "doc": "Eaton SCF9550 ELX1135 (effective January 2022), %s" % EATON,
        "operating": tuple(map(float, need(t, r"Operating temperature: (-\d+) °C to \+(\d+) °C", "F2 operating").groups())),
        "storage": tuple(map(float, need(t, r"Storage temperature: (-\d+) °C to \+(\d+) °C", "F2 storage").groups())),
        "storage_line": need(t, r"(Storage temperature: .*)", "F2 storage line").group(1).strip(),
        "hi_test": need(t, r"High temperature: (\+\d+ °C @ \d+ hours)", "F2 high temperature").group(1),
        "lo_test": need(t, r"Low temperature: (-\d+ °C @ \d+ hours)", "F2 low temperature").group(1),
    }
    t = pdf(BQ77207)
    ot = {}
    for m in re.finditer(r"^\s+(BQ77207\d\d)\s+(?:[\d.]+|N/A)\s+(?:\d+s|N/A)\s+(\d+)\s+(Enabled|Disabled)", t, re.M):
        ot[m.group(1)] = float(m.group(2))
    if "BQ7720700" not in ot:
        refuse(3, "BQ77207 OT table not found")
    rows = {}
    for m in re.finditer(r"^\s+(BQ77207\d\d)\s+\u201340°C to 110°C\s+12-Pin WSON\s+DSS\s+([\d.]+)\s+([\d.]+)\s+(\d+s)\s+([\d.]+|Disabled)", t, re.M):
        rows[m.group(1)] = {"ovp": float(m.group(2)), "ovd": m.group(4), "uvp": m.group(5) if m.group(5) == "Disabled" else "%s V" % m.group(5)}
    for name in rows:
        rows[name]["ot"] = ot[name]
        mm = re.search(r"^\s+%s\s+[^\n]*?(Active High 6V)" % name, t, re.M)
        rows[name]["drive"] = "active high 6 V" if mm else None
    if rows.get("BQ7720704", {}).get("drive") is None and re.search(r"COUT = Open\s*\n\s*Drain Active Pulldown,", t):
        rows["BQ7720704"]["drive"] = "open-drain active pulldown (DOUT active high 6 V)"
    if any(v["drive"] is None for v in rows.values()) or len(rows) != len(ot):
        refuse(3, "BQ77207 variant table not read whole")
    S["U2"] = {"doc": "TI BQ77207 (SLUSEG7D), %s" % BQ77207, "ot": ot, "rows": rows}
    t = pdf(HEATER)
    S["mat"] = {"power": float(need(t, r"Power Rating\s+(\d+\.\d+)W", "mat power").group(1)),
                "size": need(t, r"Rectangular Mat Size\s+(\d+mm x \d+mm)", "mat size").group(1),
                "thickness_stated": bool(re.search(r"[Tt]hickness", t))}
    return S


# ------------------------------------------------------------------------------------------------ the computation
def compute():
    for rel in list(PINS):
        got = sha(rel)
        if got != PINS[rel]:
            refuse(2, "%s is not the pinned file (%s)" % (rel, got[:16]))
    R = {"pins": dict(PINS)}
    # ======================================================== 0: the reproductions
    outs = {rel: open(path(rel), "rb").read() for rel in (PB_OUT, PB_JSON, RED2_OUT, HOT_OUT)}
    with tempfile.TemporaryDirectory() as td:
        jp = os.path.join(td, "pwr_budget.json")
        ch = subprocess.run([sys.executable, "-B", path(PB_PY), jp], cwd=os.path.dirname(path(PB_PY)), capture_output=True)
        R["r0a"] = ch.returncode == 0 and ch.stdout == outs[PB_OUT] and open(jp, "rb").read() == outs[PB_JSON]
    ch = subprocess.run([sys.executable, "-B", path(RED2_PY)], cwd=os.path.dirname(path(RED2_PY)), capture_output=True)
    R["r0b"] = ch.returncode == 0 and ch.stdout == outs[RED2_OUT]
    ch = subprocess.run([sys.executable, "-B", path(HOT_PY)], cwd=os.path.dirname(path(HOT_PY)), capture_output=True)
    R["r0c"] = ch.returncode == 0 and ch.stdout == outs[HOT_OUT]
    old_argv = sys.argv
    sys.argv = [path(RED2_PY)]
    try:
        red2, printed = load("pwr_red2_for_l4e10", RED2_PY, quiet=True)
    finally:
        sys.argv = old_argv
    R["r0d"] = printed.encode("utf-8") == outs[RED2_OUT]
    if not (R["r0a"] and R["r0b"] and R["r0c"] and R["r0d"]):
        refuse(4, "a reproduction failed (0a %s, 0b %s, 0c %s, 0d %s)" % (R["r0a"], R["r0b"], R["r0c"], R["r0d"]))
    pb = red2.pb
    hot, _ = load("hotstop_bounds_for_l4e10", HOT_PY)
    w4 = ast_consts(W4_PY, ["H_OUT_WALL", "H_OUT_FLOOR", "T_OVER_K_WALL", "H_IN_FANS", "H_IN_STILL"])
    import yaml
    l3 = yaml.safe_load(text(L3R2))
    reg = yaml.safe_load(text(REG))
    env = yaml.safe_load(text(ENV_Y))["ambient_c"]
    rulings = {r["id"]: r for r in reg["owner_rulings"]}
    recs = {r["id"]: r for r in reg.get("records", []) if isinstance(r, dict) and "id" in r} if isinstance(reg.get("records"), list) else {}
    R["modes"] = {m["id"]: m for m in l3["cell_modes"]}
    R["provenance_binds"] = l3["cell_provenance"]["binds"]
    R["d06"] = rulings["D-06"]["ruling"]
    R["d02a"] = rulings["D-02a"]["ruling"]
    R["d29_has_extremes_clause"] = "the extremes apply without cells" in rulings["D-29"]["ruling"]
    R["env"] = env
    S = read_sheets()
    R["S"] = S
    # TEST-PLAN levels and durations (read, not typed)
    tp = text(TP)
    R["tp"] = {
        "E3-S": tuple(map(float, need(tp, r"\*\*E3-S\*\* storage (\d+) hours at \+(\d+) C", "E3-S").groups())),
        "E3-O": tuple(map(float, need(tp, r"\*\*E3-O\*\* operation (\d+) hours at \+(\d+) C", "E3-O").groups())),
        "E4-S": tuple(map(float, need(tp, r"\*\*E4-S\*\* storage (\d+) hours at (-\d+) C", "E4-S").groups())),
        "E4-O": tuple(map(float, need(tp, r"\*\*E4-O\*\* operation (\d+) hours at (-\d+) C", "E4-O").groups())),
        "E5": tuple(map(float, need(tp, r"\| E5 \| 507, humidity: (\d+) cycles of (\d+) hours at (\d+) percent relative humidity, (\d+) to (\d+) C", "E5").groups())),
        "E3-T": float(need(tp, r"\| E3-T \|.*?a chamber set to \+(\d+) C", "E3-T").group(1)),
        "E3-A": float(need(tp, r"\| E3-A \|.*?\| \+(\d+) C for 4 h on the pack", "E3-A").group(1)),
        "E3-L": need(tp, r"\| E3-L \|.*?\| (lid closed at \+20 C, \+30 C and \+40 C, 4 h at each)", "E3-L").group(1),
        "E5-A": need(tp, r"\| E5-A \|.*?(10 cycles of 24 hours at 95 percent relative humidity, the cycle of E5 with its upper level at the use envelope's \+40 C)", "E5-A").group(1),
        "E4-T": need(tp, r"\| E4-T \|.*?\| (the lowest storage temperature of the governing cell specification, 24 h)", "E4-T").group(1),
        "E5_dwell_stated": bool(re.search(r"E5 \|[^\n]*dwell of \d+ h", tp)),
    }
    # The pack block and the record's pack and enclosure figures
    pt = text(PT)
    dims = tuple(float(v) / 1000.0 for v in need(pt, r"The pack block is (\d+\.\d+) x (\d+\.\d+) x (\d+\.\d+) mm \(A06\)", "pack block").groups())
    X, Y, Z = dims
    A_blk = 2 * (X * Y + X * Z + Y * Z)
    if abs(A_blk - pb.A_BLK) > 1e-12:
        refuse(4, "the pack block's area is not pwr_budget's A_BLK")
    c_lo, c_hi = map(float, need(pt, r"the 12 cells hold (\d+) to (\d+) J/K", "cells' heat capacity").groups())
    ap = text(APPX)
    k_lo, k_hi = map(float, need(ap, r"goes into about (\d+) to (\d+) kJ/K of thermal mass", "32.53 thermal mass").groups())
    R["blk"] = {"X": X, "Y": Y, "Z": Z, "A": A_blk, "h": (pb.G_BLK[0] / A_blk, pb.G_BLK[1] / A_blk), "C": (c_lo, c_hi)}
    R["C_kit"] = (k_lo * 1000.0, k_hi * 1000.0)
    cmt = text(CM)
    m4b = nums(need(cmt, r"^\| M4b \|(.*)$", "CASE-MARGINS M4b").group(1).split("|", 3)[3])
    R["m4b_gap_max_mm"] = max(m4b)
    R["m4b_gap_min_mm"] = min(v for v in m4b if v > 7.0)
    slt = text(SL)
    room = {}
    for key, pat in (("axis", r"\| M5 east, along the axis \| (\d+\.\d+) mm \|"), ("across", r"\| M4b, across \| (\d+\.\d+) mm \|"),
                     ("height", r"\| M6 east, height \| (\d+\.\d+) mm \|")):
        room[key] = float(need(slt, pat, "SHORTLIST room " + key).group(1))
    R["room"] = room
    R["price_35e"] = float(need(slt, r"Battery Junction: USD (\d+\.\d+) a cell", "SHORTLIST 35E price").group(1))
    pr = json.load(open(path(PRICES), encoding="utf-8"))["readings"]
    R["price_30q"] = float(need(pr[0]["verbatim"], r"Sale price \$(\d+\.\d+)", "30Q price").group(1))
    R["price_30q_stock"] = "In stock" in pr[0]["verbatim"]
    R["price_hl"] = float(need(pr[1]["verbatim"], r"US\$(\d+\.\d+) 10-4,999 Pieces", "HL18650V price").group(1))
    R["price_src"] = [(p["cell"], p["seller"], p["fetched_utc"], p["sha256"][:16]) for p in pr]
    tc = text(TC)
    R["ladder"] = {k: float(need(tc, pat, k).group(1)) for k, pat in (
        ("OTC", r"\| OTC Threshold / Recovery \(14\.9\.12\) \| [\d.]+ / [\d.]+ C \| \*\*(\d+\.\d) /"),
        ("OTD", r"\| OTD Threshold / Recovery \(14\.9\.13\) \| [\d.]+ / [\d.]+ C \| \*\*(\d+\.\d) /"),
        ("UTC", r"\| UTC Threshold / Recovery \(14\.9\.15\) \| [\d.]+ / [\d.]+ C \| \*\*(\d+\.\d) /"),
        ("UTD", r"\| UTD Threshold / Recovery \(14\.9\.16\) \| -[\d.]+ C \(recovery not stated\) \| \*\*(-\d+\.\d) /"),
        ("SOT", r"U1 SOT \(3\.6, 14\.10\.5\) \| TS1 to TS4, max \| (\d+\.\d) C, 5 s"))}
    R["ladder"]["UTD_rec"] = float(need(tc, r"\| UTD Threshold / Recovery \(14\.9\.16\) \| -[\d.]+ C \(recovery not stated\) \| \*\*-[\d.]+ / (-[\d.]+) C\*\*", "UTD's recovery").group(1))
    R["ladder"]["U2_trip_lo"] = float(need(tc, r"BQ7720700 OT, fixed 70 C .*?\| (\d+\.\d) to (\d+\.\d) C at the network", "U2 trip").group(1))
    R["hot"] = {"budget": hot.BUDGET_K, "C1": hot.C1_CELL_C, "H1": hot.H1_C, "H2": hot.H2_C, "OTD": hot.OTD_C, "release": hot.RELEASE_C,
                "terms": dict(hot.BUDGET_TERMS_K),
                "C1_air": float(need(pt, r"when the inside air reaches \+(\d+) C\s+\(the SGP41's recommended maximum\)", "C1's air trigger").group(1))}
    R["trm_shutdown"] = need(pdf(TRM), r"(In SHUTDOWN mode, the device turns off the FETs after FET Off Time)", "SLUUAQ3A 5.4.2").group(1)
    t11 = pdf(S35E11)
    m = need(t11, r"Capacity after storage for (\d+)days at (\d+)°C after the Standard charged", "35E 7.10")
    m2 = need(t11, r"Capacity recovery\(after the storage\) ≥ ([\d,]+)mAh \((\d+)% of Standard Discharge Capacity\)", "35E 7.10 recovery")
    R["full_storage"] = {"days": float(m.group(1)), "t": float(m.group(2)), "mah": m2.group(1), "pct": float(m2.group(2))}
    seq = need(tp, r"\| \+(\d+) C for (\d) h on the pack, then shore applied for (\d) h; and \+(\d+) C for (\d) h with three loaded modules on shore", "E3-A's sequence").groups()
    p13 = need(tp, r"\| P13 \|[^|]*\| the block at \+(\d+) C: (\d+) A for (\d+) s; the block at the pack's hot limit: (\d+) A for (\d) h", "P13").groups()
    e3h = need(tp, r"the chamber raised from \+(\d+) C by (\d) K an hour to at most \+(\d+) C", "E3-H's stepped run").groups()
    e3p = need(tp, r"\| E3-P \| the pack alone, armed \(JP1 closed\), at full charge[^|]*\| \+(\d+) C set point, \+-(\d) K, (\d+) h; then discharged at (\d) A from", "E3-P").groups()
    R["tpx"] = {"abort": float(need(tp, r"if any cell surface reaches \+(\d+) C on the reference thermocouples", "the +59 C abort").group(1)),
                "sgp41": float(need(tp, r"the inside air at or under the SGP41's \+(\d+) C", "E3-L's SGP41 line").group(1)),
                "e3l_levels": tuple(float(v) for v in re.findall(r"\+(\d+) C", R["tp"]["E3-L"])),
                "e3a": tuple(float(v) for v in seq), "p13_kd": tuple(float(v) for v in p13[:3]), "p13_a": float(p13[3]), "p13_h": float(p13[4]),
                "e3h": tuple(float(v) for v in e3h), "e3p": tuple(float(v) for v in e3p),
                "e4p": bool(re.search(r"\| E4-P \| the pack alone \| as E4-T \|", tp)),
                "bank_r1": need(tp, r"(On board B as generated the stage criteria fail at any level where the heat stage is entered[^(]*)", "BANK-R1's failure").group(1)}
    R["heat_reg"] = red2.HEAT_REG[1]

    # ======================================================== 1: the collisions restated from their sources
    G, G32, GB = pb.G, pb.G_3253, pb.G_BLK

    def heat_red(ov):
        _, q, p = red2.heat(ov, "plan")
        return q, p

    qR, pR = heat_red(red2.SURVR)
    fR, _, _ = red2.heat(red2.SURVR, "plan")
    qS, pS = heat_red(red2.SURV)
    f = pb.state_full("IDLESPEC", "plan")
    qI, pI = f["pb"] - f["outside"], pb.pack_i2r(f["pb"])
    R["heat"] = {"SURVR": (qR, pR), "SURV": (qS, pS), "IDLESPEC": (qI, pI), "w_idlespec": round(f["pb"], 2)}
    lim = S["35E_11"]
    t_use = float(env["in_use"]["max"])
    t_cold = float(env["in_use"]["min"])
    a = {}
    a["air_closed_W4"] = t_use + (qR + pR) / G["closed_fans"][0]
    a["air_open_W4"] = t_use + (qR + pR) / G["open_fans"][0]
    a["air_open_3253"] = t_use + (qR + pR) / G32["open_fans"][0]
    a["air_closed_3253"] = t_use + (qR + pR) / G32["closed_fans"][0]
    a["cell_closed_W4_pack"] = pb.cell_temp(t_use, qR, pR, G["closed_fans"][0], GB[0])
    a["cell_closed_3253_pack"] = pb.cell_temp(t_use, qR, pR, G32["closed_fans"][0], sum(GB) / 2)
    R["a"] = a
    e3o_h, e3o_t = R["tp"]["E3-O"]
    rises_open = [(q + p) / g for (q, p) in ((qR, pR), (qS, pS)) for g in (G["open_fans"][0], G["open_fans"][1], G32["open_fans"][0], G32["open_fans"][1])]
    R["d"] = {"amb": e3o_t, "hours": e3o_h, "rise_lo": min(rises_open), "rise_hi": max(rises_open),
              "air_lo": e3o_t + min(rises_open), "air_hi": e3o_t + max(rises_open),
              "cell_hi_pack": pb.cell_temp(e3o_t, qR, pR, G["open_fans"][0], GB[0])}
    n5, h5, rh5, lo5, hi5 = R["tp"]["E5"]
    R["e"] = {"cycles": n5, "hours": h5, "rh": rh5, "lo": lo5, "amb": hi5, "air_lo": hi5 + min(rises_open), "air_hi": hi5 + max(rises_open)}
    e3s_h, e3s_t = R["tp"]["E3-S"]
    e4s_h, e4s_t = R["tp"]["E4-S"]
    R["f"] = {"amb": e3s_t, "hours": e3s_h}
    R["g"] = {"amb": e4s_t, "hours": e4s_h}
    rb = (qI + pI) / G32["open_fans"][1]
    R["b"] = {"rise_air": rb, "air": t_cold + rb, "cell": pb.cell_temp(t_cold, qI, pI, G32["open_fans"][1], GB[1])}
    pbj = json.loads(outs[PB_JSON])
    typ_chg = [r for r in pbj["thermal"]["ceilings"]["PS-TYP, lid open, fans"] if r[0].startswith("cells, charge")][0]
    r2j = json.loads(outs[RED2_OUT])
    surv_chg = r2j["states"]["PS-SURV (slot 2 alone)"]["open_fans"]["ambient_ceilings_C"]["cells charge 45 C"]["W4_worst_to_best"]
    R["c"] = {"reach_lo": typ_chg[2], "reach_hi": surv_chg[1]}
    gaps = {
        "LO-01a": a["air_closed_W4"] - lim["discharge"][1],
        "LO-01d": (R["d"]["air_lo"] - lim["discharge"][1], R["d"]["air_hi"] - lim["discharge"][1]),
        "LO-01e": R["e"]["air_lo"] - lim["discharge"][1],
        "LO-01f": e3s_t - lim["st_1m"][1],
        "LO-01g": (lim["st_1m"][0] - e4s_t, S["35E_10"]["st_1m"][0] - e4s_t),
        "LO-01h": (S["35E_10"]["st_3m"][0] - R["env"]["storage_3_months"]["min"], R["env"]["storage_1_year"]["max"] - S["35E_10"]["st_1y"][1]),
    }
    R["gaps"] = gaps
    # agreement with Layer 3's table (l3r2.yaml cell_modes: req_c and limit_c)
    agree = {}
    for k, mine in (("LO-01a", floor1(a["air_closed_W4"])), ("LO-01d", floor1(R["d"]["air_hi"])), ("LO-01e", round(R["e"]["air_lo"], 2)),
                    ("LO-01f", e3s_t), ("LO-01g", e4s_t)):
        md = R["modes"][k]
        agree[k] = (md["req_c"], mine, abs(md["req_c"] - mine) < 1e-9, md["limit_c"], lim["discharge"][1] if k in ("LO-01a", "LO-01d", "LO-01e") else (lim["st_1m"][1] if k == "LO-01f" else lim["st_1m"][0]))
    agree["LO-01h"] = (R["modes"]["LO-01h"]["req_c"], R["env"]["storage_3_months"]["min"], R["modes"]["LO-01h"]["req_c"] == R["env"]["storage_3_months"]["min"],
                       R["modes"]["LO-01h"]["limit_c"], S["35E_10"]["st_3m"][0])
    R["agree"] = agree
    if not all(v[2] for v in agree.values()) or not all(abs(v[3] - v[4]) < 1e-9 for v in agree.values()):
        refuse(4, "the restated collisions do not reproduce Layer 3's table: %s" % agree)

    # ======================================================== 3 (computed before the screen prints it): thermal figures
    # 3a: LO-01a's thresholds, lid closed and lid open (fans on), on the pack and on shore, PLAN heat of the heat stage.
    gblk = GB[0]
    tpx = R["tpx"]
    eta_fe = min(pb.ETA_FE)
    path_loss = fR["pb"] / (pb.ETA_CHG * eta_fe) - fR["pb"]          # the front end's and charger's loss on the loads on shore
    R["shore_heat"] = qR + path_loss
    rd_hi = R["hot"]["terms"]["thermistor interchangeability"]        # the only published term that can read HIGH at steady state
    crit = []   # (criterion, supply, kind, limit C, required conductance W/K)
    for sup in ("pack", "shore"):
        heat = qR + pR if sup == "pack" else qR + path_loss
        own = pR / gblk if sup == "pack" else 0.0
        for name, lim_c, kind in (("cell rating (+60 C)", lim["discharge"][1], "cell"), ("the +59 C abort (FEA-008 LO-01a)", tpx["abort"], "cell"),
                                  ("H1 not acting (reading under +%.1f C, no sensor allowance)" % R["hot"]["H1"], R["hot"]["H1"], "cell"),
                                  ("H1 not acting with the %.2f K reading-high term" % rd_hi, R["hot"]["H1"] - rd_hi, "cell"),
                                  ("SGP41 inside air at most +%.0f C" % tpx["sgp41"], tpx["sgp41"], "air"),
                                  ("F2 at the inside air at most +%.0f C" % S["F2"]["operating"][1], S["F2"]["operating"][1], "air")):
            room_k = lim_c - t_use - (own if kind == "cell" else 0.0)
            crit.append((name, sup, kind, lim_c, heat / room_k))
    R["crit"] = crit
    gov = max(crit, key=lambda c: c[4])
    gov_noerr = max((c for c in crit if "reading-high" not in c[0]), key=lambda c: c[4])
    R["gov"] = {"all": gov, "no_sensor_term": gov_noerr,
                "fea008_pack": [c for c in crit if c[1] == "pack" and c[0].startswith("the +59")][0][4],
                "rating_pack": [c for c in crit if c[1] == "pack" and c[0].startswith("cell rating")][0][4],
                "rating_shore": [c for c in crit if c[1] == "shore" and c[0].startswith("cell rating")][0][4]}
    gstar = {"cell limit": {"pack": R["gov"]["rating_pack"], "input": [c for c in crit if c[1] == "shore" and c[0].startswith("cell rating")][0][4]}}
    R["gstar"] = gstar
    # lid open at the bound's lowest conductance: the cells on the pack and the air on shore (E3-A, E5-A)
    R["open_worst"] = {"cell_pack": pb.cell_temp(t_use, qR, pR, G["open_fans"][0], gblk), "air_shore": t_use + (qR + path_loss) / G["open_fans"][0],
                       "air_pack": t_use + (qR + pR) / G["open_fans"][0], "g_gov": gov[4]}
    # 3b: the pocket coupling measure (east face to the east wall through a gap filler, the base to the floor through the
    # heater mat; the other four faces left to the inside air at the record's film), two-node model.
    A_E, A_B = Y * Z, X * Y
    A_in = A_blk - A_E - A_B
    tk = w4["T_OVER_K_WALL"]
    t_pad = R["m4b_gap_max_mm"] / 1000.0

    def g_east(h_out):
        return 1.0 / (t_pad / (K_PAD * A_E) + tk / A_E + 1.0 / (h_out * A_E))

    def g_base(h_out):
        return 1.0 / (T_MAT / (K_MAT * A_B) + tk / A_B + 1.0 / (h_out * A_B))

    def dg_encl(h_in, h_wall, h_floor):
        u_w = 1.0 / (1.0 / h_in + tk + 1.0 / h_wall)
        u_f = 1.0 / (1.0 / h_in + tk + 1.0 / h_floor)
        return A_E * u_w + A_B * u_f

    hb_lo, hb_hi = R["blk"]["h"]
    worst = {"g_in": hb_hi * A_in, "g_amb": g_east(w4["H_OUT_WALL"][0]) + g_base(w4["H_OUT_FLOOR"][0]),
             "dg": dg_encl(w4["H_IN_FANS"][0], w4["H_OUT_WALL"][0], w4["H_OUT_FLOOR"][0])}
    best = {"g_in": hb_lo * A_in, "g_amb": g_east(w4["H_OUT_WALL"][1]) + g_base(w4["H_OUT_FLOOR"][1]),
            "dg": dg_encl(w4["H_IN_FANS"][1], w4["H_OUT_WALL"][1], w4["H_OUT_FLOOR"][1])}
    for d in (worst, best):
        d["f"] = d["g_in"] / (d["g_in"] + d["g_amb"])
    R["pad_sens"] = (1.0 / (t_pad / (3.0 * A_E) + tk / A_E + 1.0 / (w4["H_OUT_WALL"][0] * A_E))) - g_east(w4["H_OUT_WALL"][0])

    def two_node(t0, q, p, g_encl, g_in, g_amb, p_h=0.0):
        """Inside air and cells (C): air couples to ambient by g_encl and to the pack by g_in; the pack to ambient by g_amb."""
        pc = p + p_h
        det = (g_encl + g_in) * (g_in + g_amb) - g_in * g_in
        air = (q * (g_in + g_amb) + g_in * pc) / det
        cell = ((g_encl + g_in) * pc + g_in * q) / det
        return t0 + air, t0 + cell

    R["two_node"] = two_node
    R["Gb"], R["G32b"], R["Gblk"] = pb.G, pb.G_3253, pb.G_BLK
    meas = {}
    meas["a_pack_worst"] = two_node(t_use, qR, pR, G["closed_fans"][0] - worst["dg"], worst["g_in"], worst["g_amb"])
    meas["a_pack_best"] = two_node(t_use, qR, pR, G["closed_fans"][0] - best["dg"], best["g_in"], best["g_amb"])
    meas["a_input_worst"] = two_node(t_use, qR + path_loss, 0.0, G["closed_fans"][0] - worst["dg"], worst["g_in"], worst["g_amb"])
    meas["a_base_pack"] = two_node(t_use, qR, pR, G["closed_fans"][0], gblk, 0.0)
    meas["d_worst"] = two_node(e3o_t, qR, pR, G["open_fans"][0] - worst["dg"], worst["g_in"], worst["g_amb"])
    meas["d_best"] = two_node(e3o_t, qS, pS, G32["open_fans"][1] - best["dg"], best["g_in"], best["g_amb"])
    meas["e_best"] = two_node(hi5, qS, 0.0, G32["open_fans"][1] - best["dg"], best["g_in"], best["g_amb"])
    meas["d_f_needed"] = ((lim["discharge"][1] - e3o_t) / R["d"]["rise_hi"], (lim["discharge"][1] - e3o_t) / R["d"]["rise_lo"],
                          (R["hot"]["H1"] - e3o_t) / R["d"]["rise_hi"], (R["hot"]["H1"] - e3o_t) / R["d"]["rise_lo"])
    f_need = meas["d_f_needed"][0]
    ins = []
    for ga in (worst["g_amb"], best["g_amb"]):
        g_in_max = f_need / (1.0 - f_need) * ga
        r_add = 1.0 / g_in_max - 1.0 / (hb_lo * A_in)
        ins.append(r_add * A_in * K_INS * 1000.0)
    meas["ins_mm"] = (min(ins), max(ins))
    meas["two_node_matches_record"] = abs(meas["a_base_pack"][1] - a["cell_closed_W4_pack"]) < 1e-9
    # the fallback against every criterion of the complete pass line (lid closed, the bound's lowest conductance)
    fb_cell, fb_air = meas["a_pack_worst"][1], meas["a_pack_worst"][0]
    meas["fallback_vs"] = [("cell rating", fb_cell, lim["discharge"][1]), ("the +59 C abort", fb_cell, tpx["abort"]),
                           ("H1 reading", fb_cell, R["hot"]["H1"]), ("SGP41 air", fb_air, tpx["sgp41"]), ("F2 at the air", fb_air, S["F2"]["operating"][1])]
    R["meas"] = meas
    R["worst"], R["best"] = worst, best
    R["areas"] = (A_E, A_B, A_in)
    # 3c: the cold end with the measure (LO-01b), PS-IDLE-SPEC on the pack, lid open, at -20 C, highest conductances
    gc = G32["open_fans"][1]
    p_mat_cells = S["mat"]["power"]                         # MAKER: 7.5 W at 12 V into the block
    p_mat_air = R["heat_reg"] - p_mat_cells                 # the regulator's loss, into the inside air (POWER-THERMAL 7.1)
    R["mat_split"] = (p_mat_cells, p_mat_air)
    cold_base = two_node(t_cold, qI, pI, gc, GB[1], 0.0)
    corners = [(gi, ga) for gi in (worst["g_in"], best["g_in"]) for ga in (worst["g_amb"], best["g_amb"])]
    cold_meas = min((two_node(t_cold, qI, pI, gc - best["dg"], gi, ga) for gi, ga in corners), key=lambda t: t[1])
    if abs(cold_meas[1] - two_node(t_cold, qI, pI, gc - best["dg"], best["g_in"], best["g_amb"])[1]) > 1e-12:
        refuse(4, "the coldest corner of the coupled block is not the one the heater duty is sized on")
    cold_meas_w4 = two_node(t_cold, qI, pI, G["open_fans"][1] - best["dg"], best["g_in"], best["g_amb"])
    target = R["ladder"]["UTD"] + 1.0     # 1 K above the gauge's UTD reading, so the stop does not act (INFERRED margin)
    ge, gi_, ga_ = gc - best["dg"], best["g_in"], best["g_amb"]
    det = (ge + gi_) * (gi_ + ga_) - gi_ ** 2
    # the mat's cell share x and its regulator loss k*x into the air: cell rise = ((ge+gi)(p+x) + gi(q+k x))/det = target - t0
    k_loss = p_mat_air / p_mat_cells
    x = ((target - t_cold) * det - (ge + gi_) * pI - gi_ * qI) / ((ge + gi_) + gi_ * k_loss)
    p_h = max(0.0, x)
    R["cold"] = {"base": cold_base, "meas": cold_meas, "meas_w4": cold_meas_w4, "target": target, "p_h": p_h,
                 "p_h_batt": p_h * R["heat_reg"] / p_mat_cells, "w": R["heat"]["w_idlespec"]}
    # 3d: charging at the cold end on an input: the mat's 7.5 W into the block, its regulator's loss into the air, the pack idle
    R["cchg"] = {"base": two_node(t_cold, qI + p_mat_air, 0.0, gc, GB[1], 0.0, p_mat_cells),
                 "meas": min((two_node(t_cold, qI + p_mat_air, 0.0, gc - best["dg"], gi, ga, p_mat_cells) for gi, ga in corners), key=lambda t: t[1]),
                 "floor": R["ladder"]["UTC"]}
    R["cchg"]["hold"] = float(need(text(TC), r"panel and bridge hold on charge below \+(\d) C", "the panel's charge hold").group(1))
    # 3e: hold times, one node (the kit) and two nodes (the kit and the cells)
    taus_pack = (R["blk"]["C"][0] / GB[1], R["blk"]["C"][1] / GB[0])
    taus_pack_meas = (R["blk"]["C"][0] / (worst["g_in"] + worst["g_amb"]), R["blk"]["C"][1] / (best["g_in"] + best["g_amb"]))
    gcs = G["closed_still"]
    taus_kit = (R["C_kit"][0] / gcs[1], R["C_kit"][1] / gcs[0])
    st_env = R["env"]
    step_hot = e3s_t - st_env["storage_3_months"]["min"]       # the most favourable start: the storage envelope's far edge
    step_cold = st_env["storage_3_months"]["max"] - e4s_t
    slow = {"C_tot": R["C_kit"][1], "C_p": R["blk"]["C"][1], "G_e": gcs[0], "G_b": GB[0]}   # the slowest corner

    def step2(t, C_tot, C_p, G_e, G_b):
        """Two-node step response: the fraction of an ambient step still unreached by the cells after t seconds."""
        C_k = C_tot - C_p
        a11, a12, a21, a22 = -(G_e + G_b) / C_k, G_b / C_k, G_b / C_p, -G_b / C_p
        tr, dt = a11 + a22, a11 * a22 - a12 * a21
        l1 = (tr + math.sqrt(tr * tr - 4 * dt)) / 2.0
        l2 = (tr - math.sqrt(tr * tr - 4 * dt)) / 2.0
        # x' = A x, x(0) = (1, 1) (both nodes one step from ambient); solve x(t) = v1 e^{l1 t} k1 + v2 e^{l2 t} k2 with eigenvectors v = (a12, l - a11)
        v1, v2 = (a12, l1 - a11), (a12, l2 - a11)
        detv = v1[0] * v2[1] - v2[0] * v1[1]
        k1 = (1.0 * v2[1] - v2[0] * 1.0) / detv
        k2 = (v1[0] * 1.0 - 1.0 * v1[1]) / detv
        return k1 * v1[1] * math.exp(l1 * t) + k2 * v2[1] * math.exp(l2 * t)

    R["step2"] = step2
    resid2_hot = step_hot * step2(e3s_h * 3600.0, **slow)
    resid2_cold = step_cold * step2(e4s_h * 3600.0, **slow)
    R["hold"] = {"tau_pack_s": taus_pack, "tau_pack_meas_s": taus_pack_meas, "tau_kit_s": taus_kit,
                 "resid_hot": step_hot * math.exp(-e3s_h * 3600.0 / taus_kit[1]), "resid_cold": step_cold * math.exp(-e4s_h * 3600.0 / taus_kit[1]),
                 "resid2_hot": resid2_hot, "resid2_cold": resid2_cold, "slow": slow,
                 "step_hot": step_hot, "step_cold": step_cold,
                 "e_kit_hot_Wh": tuple(g * gaps["LO-01f"] * e3s_h for g in gcs), "e_kit_cold_Wh": tuple(g * gaps["LO-01g"][0] * e4s_h for g in gcs),
                 "pack_Wh_nom": 12 * lim["c_min"] * pb.V_NOM, "e3o_s": e3o_h * 3600.0}
    # 3f: the passive storage routes bounded: how far the cells' own coupling must fall for 24 h of hold (two-node, slowest kit)
    def gb_max(step_k, allow_k, hours):
        """The largest pack-to-air conductance for which the cells move at most allow_k of a step_k ambient step in hours."""
        moved = lambda g: step_k * (1.0 - step2(hours * 3600.0, slow["C_tot"], slow["C_p"], slow["G_e"], g))
        if moved(GB[0]) <= allow_k:
            return GB[0]
        lo_, hi_ = 1e-7, GB[0]
        for _ in range(200):
            mid = (lo_ + hi_) / 2.0
            if moved(mid) > allow_k:
                hi_ = mid
            else:
                lo_ = mid
        return lo_

    passive = {}
    for key, t_amb, t_lim, start, hours in (("LO-01f", e3s_t, lim["st_1m"][1], st_env["storage_3_months"]["min"], e3s_h),
                                           ("LO-01g", e4s_t, lim["st_1m"][0], st_env["storage_3_months"]["max"], e4s_h)):
        step_k = abs(t_amb - start)
        allow = abs(t_lim - start)          # how far the cells may move from the start before they reach the limit
        g = gb_max(step_k, allow, hours)
        r_ins = R["blk"]["A"] / g - 1.0 / hb_lo
        passive[key] = {"step": step_k, "allow": allow, "g_max": g, "ins_mm": r_ins * K_INS * 1000.0,
                        "now_reached": step_k * (1.0 - step2(hours * 3600.0, slow["C_tot"], slow["C_p"], slow["G_e"], GB[0]))}
    R["passive"] = passive
    # 3g: LO-01g, the -33 C storage margin (E4-S, 24 h), in three cases: (i) a warm pack kept inside its limits, (ii) a pack
    # already cold-soaked before any heater starts, (iii) heating lost or its energy spent. One calculation boundary: from
    # the source's terminals; the mat's 7.5 W into the block, the regulator's loss into the air node, the gauge's own draw.
    gser = (1.0 / (1.0 / GB[0] + 1.0 / gcs[0]), 1.0 / (1.0 / GB[1] + 1.0 / gcs[1]))
    corners_c = {"slow": {"C_tot": R["C_kit"][1], "C_p": R["blk"]["C"][1], "G_e": gcs[0], "G_b": GB[0]},
                 "fast": {"C_tot": R["C_kit"][0], "C_p": R["blk"]["C"][0], "G_e": gcs[1], "G_b": GB[1]}}

    def free(t, xk0, xp0, C_tot, C_p, G_e, G_b):
        """Two nodes, no heat input: the cells' deviation from ambient after t seconds, from deviations xk0 (kit) and xp0 (cells)."""
        C_k = C_tot - C_p
        a11, a12, a21, a22 = -(G_e + G_b) / C_k, G_b / C_k, G_b / C_p, -G_b / C_p
        tr, dt = a11 + a22, a11 * a22 - a12 * a21
        l1 = (tr + math.sqrt(tr * tr - 4 * dt)) / 2.0
        l2 = (tr - math.sqrt(tr * tr - 4 * dt)) / 2.0
        v1, v2 = (a12, l1 - a11), (a12, l2 - a11)
        detv = v1[0] * v2[1] - v2[0] * v1[1]
        k1 = (xk0 * v2[1] - v2[0] * xp0) / detv
        k2 = (v1[0] * xp0 - xk0 * v1[1]) / detv
        return k1 * v1[1] * math.exp(l1 * t) + k2 * v2[1] * math.exp(l2 * t)

    def t_reach(target_dev, xk0, xp0, prm):
        """Seconds until the cells' deviation falls to target_dev (bisection; the response falls monotonically here)."""
        lo_, hi_ = 0.0, 7 * 86400.0
        if free(hi_, xk0, xp0, **prm) > target_dev:
            return float("inf")
        for _ in range(200):
            mid = (lo_ + hi_) / 2.0
            if free(mid, xk0, xp0, **prm) > target_dev:
                lo_ = mid
            else:
                hi_ = mid
        return hi_

    def hold(d, prm, k):
        """Steady hold of the cells d K above ambient by a mat in the block whose regulator loses k of the mat's power into
        the air: returns (mat W into the cells, W at the source's terminals, the air's deviation)."""
        gb_, ge_ = prm["G_b"], prm["G_e"]
        a_ = gb_ * (1 + k) * d / (ge_ + gb_ * (1 + k))
        pm = gb_ * (d - a_)
        return pm, pm * (1 + k), a_

    k_reg = p_mat_air / p_mat_cells
    budget_cold = float(need(text(TC), r"\| \*\*Sum of the published terms\*\* \| \| \*\*[\d.]+ K\*\* \| \*\*[\d.]+ K\*\* \| \*\*[\d.]+ K\*\* \| \*\*([\d.]+) K\*\* \|", "the cold-side budget").group(1))
    i_norm_ua = float(need(pdf(BQ4050), r"INORMAL\s+NORMAL mode\s+CHG on\. DSG on, no Flash write\s+(\d+)\s+µA", "the gauge's NORMAL current").group(1))
    p_gauge = i_norm_ua * 1e-6 * pb.V_NOM * 4
    soc_store = float(need(lim["soc"], r"(\d+)%", "the stored charge").group(1)) / 100.0
    age = float(need(text(REG), r"an aged pack, (\d+) percent of the cells'\s+specification minimum capacity", "SC-23's aged basis").group(1)) / 100.0
    t_start = float(need(t11, r"conducted at temperature (\d+)±3°C", "the sheet's standard temperature").group(1))
    sh = {"i_norm_ua": i_norm_ua, "g_series": gser, "k_reg": k_reg, "budget_cold": budget_cold, "p_gauge": p_gauge, "soc_store": soc_store, "age": age,
          "reserve": pb.RESERVE, "cold_f": (pb.COLD_LO, 1.0), "t_start": t_start, "shutdown_fets_off": R["trm_shutdown"]}
    # setpoints: the pack-fed heater discharges the cells, so the discharge floor's UTD reading plus the published cold-side
    # budget (gradient and ADC terms TBD); a separately fed heater keeps the storage floor, its thermostat's tolerance TBD
    sh["set_pack"] = R["ladder"]["UTD"] + budget_cold
    sh["set_prim"] = lim["st_1m"][0]
    rows3 = {}
    air_devs = []
    for cname, prm in sorted(corners_c.items()):
        d_pack = sh["set_pack"] - e4s_t
        d_prim = sh["set_prim"] - e4s_t
        pm_pack, pt_pack, air_pack = hold(d_pack, prm, k_reg)
        pt_pack += p_gauge
        pm_prim, pt_prim_direct, air_prim = hold(d_prim, prm, 0.0)
        _, pt_prim_reg, _ = hold(d_prim, prm, k_reg)
        air_devs.append(air_prim)
        per_k = hold(1.0, prm, 0.0)[1] * e4s_h                  # Wh over the exposure per K of setpoint margin, direct
        # the cool-down credit from the sheet's standard temperature (ASSUMPTION: E4-S's starting state is not stated)
        x0 = t_start - e4s_t
        tc_pack = t_reach(d_pack, x0, x0, prm)
        tc_prim = t_reach(d_prim, x0, x0, prm)
        # (iii): heating lost at the steady hold; time until the cells pass the storage floor
        t_lost_pack = t_reach(d_prim, air_pack, d_pack, prm)
        rows3[cname] = {"pm_pack": pm_pack, "pt_pack": pt_pack, "pm_prim": pm_prim, "pt_prim_direct": pt_prim_direct, "pt_prim_reg": pt_prim_reg,
                        "Wh_pack": pt_pack * e4s_h, "Wh_prim_direct": pt_prim_direct * e4s_h, "Wh_prim_reg": pt_prim_reg * e4s_h, "Wh_per_K": per_k,
                        "tc_pack_h": tc_pack / 3600.0, "tc_prim_h": tc_prim / 3600.0, "t_lost_pack_h": t_lost_pack / 3600.0}
    sh["rows"] = rows3
    sh["air_dev"] = (min(air_devs), max(air_devs))
    # (i), fed by the pack at its stored charge: usable energy (aged, the reserve kept, the cold factor at the setpoint unknown
    # between MAKER 7.5's 1C point and 1.0), the duration it buys, and the reserve after the exposure without any cool-down credit
    e_use = tuple(12 * lim["c_min"] * pb.V_NOM * age * (soc_store - pb.RESERVE) * cf for cf in sh["cold_f"])
    sh["e_use_stored"] = e_use
    sh["dur_h"] = {"slow, cold factor 1.0": e_use[1] / rows3["slow"]["pt_pack"], "fast, 1C factor": e_use[0] / rows3["fast"]["pt_pack"]}
    sh["dur_h_range"] = (e_use[0] / rows3["fast"]["pt_pack"], e_use[1] / rows3["slow"]["pt_pack"])
    sh["reserve_after_Wh"] = (e_use[0] - rows3["fast"]["Wh_pack"], e_use[1] - rows3["slow"]["Wh_pack"])
    e_full = tuple(12 * lim["c_min"] * pb.V_NOM * age * (1.0 - pb.RESERVE) * cf for cf in sh["cold_f"])
    sh["dur_full_h_range"] = (e_full[0] / rows3["fast"]["pt_pack"], e_full[1] / rows3["slow"]["pt_pack"])
    sh["warm_per_K_Wh"] = (R["blk"]["C"][0] / 3600.0, R["blk"]["C"][1] / 3600.0)
    R["selfheat"] = sh
    # 3h: E5's cycle and added insulation or thermal storage (TEST-PLAN states the cycle's limits, not its profile)
    lo5_, hi5_ = R["e"]["lo"], R["e"]["amb"]
    e5 = {"mean_max": (lim["discharge"][1] - R["d"]["rise_hi"], lim["discharge"][1] - R["d"]["rise_lo"])}
    mean_sym, amp = (lo5_ + hi5_) / 2.0, (hi5_ - lo5_) / 2.0
    w_ = 2.0 * math.pi / (R["e"]["hours"] * 3600.0)
    room_sym = lim["discharge"][1] - mean_sym - R["d"]["rise_lo"]
    e5["sym"] = {"mean": mean_sym, "amp": amp, "room_best": room_sym, "feasible_worst": lim["discharge"][1] - mean_sym - R["d"]["rise_hi"] > 0}
    if room_sym > 0:
        att = room_sym / amp
        tau = math.sqrt(1.0 / att ** 2 - 1.0) / w_ if att < 1 else 0.0
        e5["sym"]["tau_s"] = tau
        g_need = (R["blk"]["C"][0] / tau, R["blk"]["C"][1] / tau)
        e5["sym"]["ins_mm"] = tuple((R["blk"]["A"] / g - 1.0 / hb_lo) * K_INS * 1000.0 for g in g_need)
        e5["sym"]["c_need_kJ"] = (tau * GB[0] / 1000.0, tau * GB[1] / 1000.0)
    R["e5"] = e5
    # 3i: powered cooling: the cold-side load, a COP range (ASSUMPTION, no module's sheet held) and the heat-rejection balance
    cool = {}
    for key, airs, t_hold, gpair in (("E3-O", (R["d"]["air_lo"], R["d"]["air_hi"]), R["hot"]["H1"], (GB[0], GB[1])),
                                     ("E5", (R["e"]["air_lo"], R["e"]["air_hi"]), R["hot"]["H1"], (GB[0], GB[1])),
                                     ("E3-S", (e3s_t, e3s_t), lim["st_1m"][1] - R["hot"]["budget"], gser)):
        qc = (gpair[0] * (airs[0] - t_hold), gpair[1] * (airs[1] - t_hold))
        row = {"t_hold": t_hold, "qc": qc}
        row["qh"] = {cop: (qc[0] * (1 + 1.0 / cop), qc[1] * (1 + 1.0 / cop)) for cop in COP}
        # rejected through the pack's own skin path (the coupling measure's), hot side at most HOT_RISE above ambient
        row["g_out_need"] = {cop: (row["qh"][cop][0] / HOT_RISE, row["qh"][cop][1] / HOT_RISE) for cop in COP}
        # rejected into the inside air: the loop converges only if G_b (1 + 1/COP) < G_enclosure
        genc = gcs[0] if key == "E3-S" else G["open_fans"][0]
        row["loop_ok_worst"] = {cop: gpair[1] * (1 + 1.0 / cop) < genc for cop in COP}
        if key == "E3-S":
            row["Wh"] = {cop: (qc[0] / cop * e3s_h, qc[1] / cop * e3s_h) for cop in COP}
        cool[key] = row
    cool["skin"] = (worst["g_amb"], best["g_amb"])
    R["cool"] = cool
    # 3j: PWR-F12, an 18 A key-down of 60 s from a cell at C1's +55 C trigger (the cells' adiabatic rise)
    i_cell = pb.I_PEAK / 3.0
    q_kd = [12 * i_cell ** 2 * r * 60.0 for r in (pb.R_CELL["lo"], pb.R_CELL["hi"])]
    kd = (q_kd[0] / R["blk"]["C"][1], q_kd[1] / R["blk"]["C"][0])
    R["kd"] = {"i_cell": i_cell, "rise": kd, "from": R["hot"]["C1"], "to": (R["hot"]["C1"] + kd[0], R["hot"]["C1"] + kd[1])}
    # 3k: P13's hour at 10 A: the cells' own I2R, steady over the block's film and adiabatic over the hour
    i13 = tpx["p13_a"] / 3.0
    q13 = (12 * i13 ** 2 * pb.R_CELL["lo"], 12 * i13 ** 2 * pb.R_CELL["hi"])
    R["p13"] = {"i_cell": i13, "w": q13, "steady": (q13[0] / GB[1], q13[1] / GB[0]),
                "adiabatic": (q13[0] * tpx["p13_h"] * 3600.0 / R["blk"]["C"][1], q13[1] * tpx["p13_h"] * 3600.0 / R["blk"]["C"][0])}
    # 3l: E3-A's and E3-L's other levels, the stage the controls select and the cells at the bound's worst corner
    lev = {}
    q2, p2 = heat_red(red2.RED2)
    for t0 in tpx["e3l_levels"]:
        air_r = t0 + (q2 + p2) / G["closed_fans"][0]
        cell_r = pb.cell_temp(t0, q2, p2, G["closed_fans"][0], gblk)
        if air_r < R["hot"]["C1_air"] and cell_r < R["hot"]["C1"]:
            lev[t0] = ("the reduced mode", air_r, cell_r)
        else:
            lev[t0] = ("the heat stage (C1 acted)", t0 + (qR + pR) / G["closed_fans"][0], pb.cell_temp(t0, qR, pR, G["closed_fans"][0], gblk))
    R["e3l_levels"] = lev

    # ======================================================== 4: the cells alongside
    def usable(c_min, age=0.8, f_t=1.0):
        old = pb.C_MIN
        pb.C_MIN = c_min
        try:
            e, _, _ = pb.usable(f["pb"], 3, age, f_t, pb.R_CELL["plan"])
        finally:
            pb.C_MIN = old
        return e
    w = f["pb"]
    base_dims = (lim["dims"][1], lim["dims"][0])
    cand = {}
    for key, c_min, dims_c, i_cont in (("35E", lim["c_min"], (lim["dims"][1], lim["dims"][0]), lim["i_cont"]),
                                       ("30Q6", S["30Q6"]["c_min"], (S["30Q6"]["dims"][1], S["30Q6"]["dims"][0]), S["30Q6"]["i_cont"]),
                                       ("HL18650V", S["HL18650V"]["c_min"], (S["HL18650V"]["dims"][1], S["HL18650V"]["dims"][0]), S["HL18650V"]["i_cont"])):
        L_, D_ = dims_c
        grow = (2 * (L_ - base_dims[0]), 3 * (D_ - base_dims[1]), 2 * (D_ - base_dims[1]))
        e = usable(c_min)
        cand[key] = {"c_min": c_min, "wh_nom": 12 * c_min * pb.V_NOM, "usable_wh": e, "hours": e / w,
                     "i_cont": i_cont, "i_need": i_cell, "grow_mm": grow,
                     "fits": grow[0] <= room["axis"] and grow[1] <= room["across"] and grow[2] <= room["height"]}
    cand["35E"]["cold_f"] = pb.COLD_LO
    cand["30Q6"]["cold_f"] = float(S["30Q6"]["cold"][1]) / float(S["30Q6"]["cold"][3])
    cand["HL18650V"]["cold_f"] = None
    for k in cand:
        cf = cand[k]["cold_f"]
        cand[k]["cold_wh"] = usable(cand[k]["c_min"], 0.8, cf) if cf is not None else None
    R["cand"] = cand
    floors = {"35E Ver. 1.1": lim["st_1m"][0], "35E Version 1.0": S["35E_10"]["st_1m"][0], "30Q6 (2020)": S["30Q6"]["st_1m"][0],
              "30Q (2015)": S["30Q_2015"]["st_1m"][0], "HG2": S["HG2"]["st_1m"][0]}
    tops = {"35E Ver. 1.1": lim["st_1m"][1], "35E Version 1.0": S["35E_10"]["st_1m"][1], "30Q6 (2020)": S["30Q6"]["st_1m"][1],
            "30Q (2015)": S["30Q_2015"]["st_1m"][1], "HG2": S["HG2"]["st_1m"][1]}
    R["maker_floor"] = min(floors.values())
    R["maker_floor_by"] = sorted(k for k, v in floors.items() if v == R["maker_floor"])
    R["maker_top"] = max(tops.values())
    R["w_idlespec"] = w
    R["dr01"] = need(text(REG), r"48 to 72 hours", "REQ-072's objective").group(0)
    # the modes each candidate's documented limits meet (MAKER for 35E and 30Q6; the HL18650V's page is not a specification)
    s6 = S["30Q6"]
    hl = S["HL18650V"]
    cell_a_pack = a["cell_closed_W4_pack"]
    meets = {
        "35E": {"LO-01a": cell_a_pack <= lim["discharge"][1], "LO-01d": R["d"]["cell_hi_pack"] <= lim["discharge"][1],
                "LO-01e": R["e"]["air_lo"] <= lim["st_1m"][1], "LO-01f": e3s_t <= lim["st_1m"][1], "LO-01g": e4s_t >= lim["st_1m"][0],
                "LO-01h": lim["st_3m"][0] <= st_env["storage_3_months"]["min"] and lim["st_3m"][1] >= st_env["storage_3_months"]["max"]
                and lim["st_1y"][1] >= st_env["storage_1_year"]["max"]},
        "30Q6": {"LO-01a": cell_a_pack <= s6["surf_discharge"][1] and a["air_closed_W4"] <= s6["amb_discharge"][1],
                 "LO-01d": R["d"]["cell_hi_pack"] <= s6["surf_discharge"][1] and R["d"]["air_hi"] <= s6["amb_discharge"][1],
                 "LO-01e": R["e"]["air_lo"] <= s6["st_1m"][1] and R["e"]["air_lo"] <= s6["amb_discharge"][1],
                 "LO-01f": e3s_t <= s6["st_1m"][1], "LO-01g": e4s_t >= s6["st_1m"][0],
                 "LO-01h": s6["st_3m"][0] <= st_env["storage_3_months"]["min"] and s6["st_3m"][1] >= st_env["storage_3_months"]["max"]
                 and s6["st_1y"][1] >= st_env["storage_1_year"]["max"]},
        "HL18650V": {"LO-01a": cell_a_pack <= hl["discharge"][1], "LO-01d": R["d"]["cell_hi_pack"] <= hl["discharge"][1],
                     "LO-01e": R["e"]["air_hi"] <= hl["st_30d"][1], "LO-01f": e3s_t <= hl["st_30d"][1], "LO-01g": e4s_t >= hl["st_3m"][0],
                     "LO-01h": hl["st_6m"][0] <= st_env["storage_3_months"]["min"] and hl["st_6m"][1] >= st_env["storage_3_months"]["max"]
                     and hl["st_12m"][1] >= st_env["storage_1_year"]["max"]},
    }
    # the 30Q6 under the other reading of its ambient clause (the kit's outside ambient, not the inside air): surface only
    meets["30Q6_outside_ambient"] = {"LO-01a": cell_a_pack <= s6["surf_discharge"][1] and t_use <= s6["amb_discharge"][1],
                                     "LO-01d": R["d"]["cell_hi_pack"] <= s6["surf_discharge"][1] and e3o_t <= s6["amb_discharge"][1]}
    R["meets"] = meets
    # F2 and U2 against each hot or cold level (board P sits beside the block in the pocket: at the inside air or the cells)
    F2 = S["F2"]
    R["f2"] = {"LO-01a": a["air_closed_W4"] > F2["operating"][1], "LO-01d": R["d"]["air_lo"] > F2["operating"][1],
               "LO-01e": R["e"]["air_lo"] > F2["operating"][1], "LO-01f": e3s_t > F2["operating"][1], "LO-01g": e4s_t < F2["operating"][0],
               "storage_env": (st_env["storage_3_months"]["min"] < F2["storage"][0], st_env["storage_3_months"]["max"] > F2["storage"][1])}
    R["u2"] = {"trip_lo": R["ladder"]["U2_trip_lo"], "LO-01f": e3s_t >= R["ladder"]["U2_trip_lo"], "LO-01d": R["d"]["air_hi"] >= R["ladder"]["U2_trip_lo"],
               "variants": dict(sorted(S["U2"]["ot"].items()))}

    # ======================================================== 5: decisions (FEA-008 stays an engineering obligation; see R4 of check 1)
    gv = R["gov"]["all"]
    sh, e5, cool, pas = R["selfheat"], R["e5"], R["cool"], R["passive"]
    dec = {}
    dec["LO-01a"] = {"decision": "CONDITIONAL", "evidence": ["MAKER", "MODELED", "INFERRED", "ASSUMPTION"], "bounded": True, "cell_change": None,
                     "routes": [{"route": "the enclosure's measured conductance", "status": "CONDITIONAL",
                                 "basis": "the complete pass line holds on the model from %.3f W/K (%s, on %s), lid open and lid closed with fans" % (gv[4], gv[0], gv[1]),
                                 "missing": "T-H1's reading in both lid states"},
                                {"route": "the pocket coupling measure", "status": "CONDITIONAL",
                                 "basis": "lowers the cells only (the +60 C rating and the +59 C abort); the air criteria (SGP41, F2) stay the enclosure's",
                                 "missing": "the film and filler figures, board B's underside"}],
                     "acceptance": "E3-A and E3-L with the pack fitted at +40 C, first on the pack, then on shore: every cell at or under +60 C and the +59 C abort, H1 not acting, the inside air at or under the SGP41's +55 C, F2's body at or under +60 C, the stage's bearers passing traffic (REQ-052), C1 to C3 and K2 at their triggers, no permanent protection action",
                     "gap": "T-H1 reading at least %.3f W/K in each lid state, BANK-R1 in board B's generator, F2's body (P13), the gauge's ADC and gradient terms (P14); HIGH heat is not covered" % gv[4]}
    dec["LO-01b"] = {"decision": "NO_COLLISION", "evidence": ["MAKER", "MODELED"], "bounded": True, "cell_change": None, "routes": [],
                     "acceptance": "E4-O with the pack fitted: every cell at or above -10 C once warm", "gap": "none"}
    dec["LO-01c"] = {"decision": "NO_COLLISION", "evidence": ["MAKER", "MODELED"], "bounded": True, "cell_change": None, "routes": [],
                     "acceptance": "E3-A's T3, T4 and OTC lines; E4-O's charge floor and the panel's hold", "gap": "none"}
    cell_route = lambda rows, extra="": {"route": "a cell whose maker's sheet covers the level, with the protection and control redesign as its entry cost (section 4)",
                                         "status": "INCONCLUSIVE", "basis": rows,
                                         "missing": "a maker's signed specification covering the level (none held; the HL18650V's page is not one)%s, F2's replacement, U2 and the hot-stop thresholds re-derived" % extra}
    dec["LO-01d"] = {"decision": "OPEN", "evidence": ["MAKER", "MODELED", "INFERRED", "ASSUMPTION"], "bounded": True,
                     "cell_change": {"candidate": "30Q6 or HL18650V class", "taken": False, "owner_approval_required": True},
                     "routes": [{"route": "thermal design without added power (fans, spreading, insulation, the coupling)", "status": "REJECTED",
                                 "basis": "the cells may sit 5 K over +55 C against a 6.63 to 19.22 K rise; insulation needs %.1f to %.1f mm against at most 2.66 mm; with the coupling the cells pass H1's reading at every corner, so the hot stop stops every module (E3-O's 'no shutdown')" % R["meas"]["ins_mm"],
                                 "missing": "none"},
                                {"route": "powered cooling of the pack on the input", "status": "INCONCLUSIVE",
                                 "basis": "cold-side load %.2f to %.2f W; with its heat sent out through the pack's skin path it needs %.3f to %.3f W/K at COP 1.0 against %.3f to %.3f W/K" % (cool["E3-O"]["qc"] + cool["E3-O"]["g_out_need"][1.0] + cool["skin"]),
                                 "missing": "a cooler's maker sheet (load against lift, COP), the input's spare power during E3-O, the volume, a sealed path out of the case for the worst corner"},
                                cell_route("the 30Q6's surface rating (80 C) covers the cells, its ambient line (60 C) does not unless read as the outside air; the HL18650V's page reaches 85 C", ", or Samsung's reading of the 30Q6's ambient clause")],
                     "acceptance": "E3-O with the pack fitted: every cell inside its limit for the 4 h, no shutdown, recovery to specification",
                     "gap": "a thermoelectric module's maker sheet sized at the cold-side load, the input's spare power during E3-O, the volume and a sealed path out of the case; F2's answer from Eaton. Next: size one module class from a maker's sheet against 3i's loads"}
    dec["LO-01e"] = {"decision": "OPEN", "evidence": ["MAKER", "MODELED", "INFERRED", "ASSUMPTION"], "bounded": True,
                     "cell_change": {"candidate": "HL18650V class", "taken": False, "owner_approval_required": True},
                     "routes": [{"route": "added insulation or thermal storage over E5's cycle", "status": "INCONCLUSIVE",
                                 "basis": "possible only where the cycle's mean ambient is under %.2f to %.2f C; for a symmetric 30 to 60 C cycle (ASSUMPTION) none at the worst corner, and at the best a %.2f h time constant, %.1f to %.1f mm of insulation or %.1f to %.1f kJ/K of added heat capacity, against at most 2.66 mm of room" % (e5["mean_max"] + (e5["sym"]["tau_s"] / 3600.0,) + (min(e5["sym"]["ins_mm"]), max(e5["sym"]["ins_mm"])) + e5["sym"]["c_need_kJ"]),
                                 "missing": "E5's profile (TEST-PLAN states its limits, not its dwell and ramps)"},
                                {"route": "powered cooling on the input", "status": "INCONCLUSIVE",
                                 "basis": "cold-side load %.2f to %.2f W" % cool["E5"]["qc"], "missing": "as LO-01d's cooling route"},
                                cell_route("the HL18650V's page stores to 80 C within 30 days; no Samsung or LG sheet held passes +60 C in storage")],
                     "acceptance": "E5 with the pack fitted: every cell inside its limit through the dwells and the pack recovering its capacity",
                     "gap": "E5's dwell and ramp profile (TEST-PLAN's owner), then as LO-01d. Next: the profile stated, 3h recomputed on it"}
    dec["LO-01f"] = {"decision": "OPEN", "evidence": ["MAKER", "MODELED", "INFERRED", "ASSUMPTION"], "bounded": True,
                     "cell_change": {"candidate": "HL18650V class", "taken": False, "owner_approval_required": True},
                     "routes": [{"route": "passive insulation or thermal storage (no power in storage)", "status": "REJECTED",
                                 "basis": "24 h of hold from the most favourable start needs the pack's coupling under %.4f W/K, %.1f mm at k 0.02, against at most 2.66 mm in D-06's pocket" % (pas["LO-01f"]["g_max"], pas["LO-01f"]["ins_mm"]),
                                 "missing": "none within D-06's pocket"},
                                {"route": "powered cooling from a separate source in storage", "status": "INCONCLUSIVE",
                                 "basis": "cold-side load %.2f to %.2f W, %.0f to %.0f Wh of input over 24 h at COP 1.0 to 0.5; the pack is in shutdown (its FETs off)" % (cool["E3-S"]["qc"] + (cool["E3-S"]["Wh"][1.0][0], cool["E3-S"]["Wh"][0.5][1])),
                                 "missing": "the source and cooler sheets, a sealed path out of the case, the volume"},
                                cell_route("the HL18650V's page stores to 80 C within 30 days; U2's 70 C trip window (62.7 to 77.5 C) permits a destructive trip at +71 C")],
                     "acceptance": "E3-S with the pack fitted: every cell inside its governing sheet's storage limit for the 24 h at the stored charge (a cell whose sheet covers +71 C, or the cells held under +60 C), the pack recovering its capacity",
                     "gap": "a separate source and cooler sized at 3i's E3-S load with a sealed path out, or a cell covering +71 C with the redesign; F2's answer. Next: as LO-01d's, with a storage source"}
    dec["LO-01g"] = {"decision": "OPEN", "evidence": ["MAKER", "MODELED", "INFERRED", "ASSUMPTION"], "bounded": True,
                     "cell_change": {"candidate": "HL18650V class", "taken": False, "owner_approval_required": True},
                     "routes": [{"route": "passive insulation or thermal storage", "status": "REJECTED",
                                 "basis": "needs the pack's coupling under %.4f W/K, %.1f mm at k 0.02, against at most 2.66 mm" % (pas["LO-01g"]["g_max"], pas["LO-01g"]["ins_mm"]),
                                 "missing": "none within D-06's pocket"},
                                {"route": "a heater fed by the pack itself, keeping a warm pack (case i)", "status": "REJECTED",
                                 "basis": "it discharges the cells, so it holds %.2f C; in REQ-025's stored state the gauge's shutdown turns its FETs off (SLUUAQ3A 5.4.2), and the stored charge buys %.1f to %.1f h of the %.0f h; with the gauge awake and a full charge %.1f to %.1f h, a change of REQ-025's stored state outside this task's authority" % ((sh["set_pack"],) + sh["dur_h_range"] + (e4s_h,) + sh["dur_full_h_range"]),
                                 "missing": "none within REQ-025"},
                                {"route": "a heater fed by a separate primary source, keeping a warm pack at the storage floor (case i; the CANDIDATE)", "status": "INCONCLUSIVE",
                                 "basis": "%.1f to %.1f Wh into the cells for the %.0f h at the floor itself, driven direct, plus %.2f to %.2f Wh per K of margin; a cold-soaked pack (case ii) is not recovered, and a lost heater (case iii) is past the floor at once" % (sh["rows"]["slow"]["Wh_prim_direct"], sh["rows"]["fast"]["Wh_prim_direct"], e4s_h, sh["rows"]["slow"]["Wh_per_K"], sh["rows"]["fast"]["Wh_per_K"]),
                                 "missing": "the source's usable energy at -33 C, the thermostat's tolerance, the in-pack gradient, a place in the case, its transport classification (D-04)"},
                                cell_route("the HL18650V's page stores from -40 C; the 2015 30Q sheet stops at -30 C")],
                     "acceptance": "E4-S with the pack fitted: every cell inside its storage row for the 24 h (or a cell whose sheet covers -33 C), the pack recovering its capacity",
                     "gap": "a primary source's usable energy at -33 C (at least 3g's demand plus margin and reserve), the thermostat's tolerance, the in-pack gradient, a place in the case, its transport classification, F2 at about -30 C (Eaton). Next: read one lithium primary maker's sheet at -33 C and size it against 3g"}
    dec["LO-01h"] = {"decision": "CONDITIONAL", "evidence": ["MAKER"], "bounded": True, "cell_change": None,
                     "routes": [{"route": "procurement", "status": "CONDITIONAL", "basis": "Ver. 1.1 covers both rows", "missing": "the lot's revision"}],
                     "acceptance": "the bought lot's sheet covers -20 C for three months and +25 C for a year (BAT-F09); E4-T at the governing floor",
                     "gap": "the purchase record"}
    R["dec"] = dec
    # an owner decision is forced only where every route of a row is rejected on bounded evidence
    R["forced_rows"] = sorted(k for k, d in dec.items() if d["decision"] == "OPEN" and d["routes"] and all(r["status"] == "REJECTED" for r in d["routes"]))
    R["owner_decision_required"] = bool(R["forced_rows"])
    R["classes"] = CLASSES
    return R


# ------------------------------------------------------------------------------------------------ the rendering
def render(R):
    S, a, d, e, hot, L = R["S"], R["a"], R["d"], R["e"], R["hot"], []
    lim = S["35E_11"]
    w = L.append
    w("l4e10_cell_thermal: layer 4 task L4-E10 (MESHSAT-1357), FEA-008: the cell and thermal design of the battery path")
    w("PROTOTYPE DESIGN, desk arithmetic; nothing bought, built, powered or measured. Classes: MAKER, MODELED, INFERRED, ASSUMPTION, CONDITIONAL.")
    w("")
    w("== 0. Reproductions and pins")
    w("0a pwr_budget.py re-run (child, scratch JSON): pwr_budget.out and pwr_budget.json byte for byte: %s" % R["r0a"])
    w("0b pwr_red2.py re-run (child): pwr_red2.out byte for byte: %s" % R["r0b"])
    w("0c hotstop_bounds.py re-run (child): hotstop_bounds.out byte for byte: %s" % R["r0c"])
    w("0d pwr_red2.py imported here prints pwr_red2.out byte for byte: %s (its heat() and state tables are the record's)" % R["r0d"])
    for rel in sorted(R["pins"]):
        w("   pin %s %s" % (R["pins"][rel], rel))
    w("")
    w("== 1. The collisions restated from their sources (Layer 3's table reproduced, then the cells on the pack)")
    w("Governing cell limits (MAKER, %s): charge %.0f to %.0f C, discharge %.0f to %.0f C at the %s; storage 1 month %.0f to %.0f C,"
      % (lim["doc"], lim["charge"][0], lim["charge"][1], lim["discharge"][0], lim["discharge"][1], lim["basis"], lim["st_1m"][0], lim["st_1m"][1]))
    w("   3 months %.0f to %.0f C, 1 year %.0f to %.0f C, each at the ex-factory %s; the handling list: 'Don't leave, charge or use the battery in a car"
      % (lim["st_3m"][0], lim["st_3m"][1], lim["st_1y"][0], lim["st_1y"][1], lim["soc"]))
    w("   or similar place where inside of temperature may be over 60°C' (%s) and 'Store the battery at temperature below 60°C' (%s)." % (lim["car"], lim["store60"]))
    s10 = S["35E_10"]
    w("Version 1.0 (MAKER, %s): charge %.0f to %.0f C and discharge %.0f to %.0f C (ambient); storage 1 year %.0f to %.0f C, 3 months %.0f to %.0f C, 1 month %.0f to %.0f C."
      % (s10["doc"], s10["charge"][0], s10["charge"][1], s10["discharge"][0], s10["discharge"][1], s10["st_1y"][0], s10["st_1y"][1], s10["st_3m"][0],
         s10["st_3m"][1], s10["st_1m"][0], s10["st_1m"][1]))
    qR, pR = R["heat"]["SURVR"]
    qS, pS = R["heat"]["SURV"]
    w("Heat inside (MODELED, PLAN): the heat stage after BANK-R1 (PS-SURV-R) %.2f W plus the cells' I2R %.3f W on the pack; as generated (PS-SURV) %.2f W plus %.3f W."
      % (qR, pR, qS, pS))
    w("")
    w("LO-01a  in use, the envelope's +%.0f C, battery-powered, the heat stage (in-use: operate to specification; acceptance E3-A, E3-L)" % R["env"]["in_use"]["max"])
    w("   inside air (MODELED): lid closed %.2f C on the independent bound's lowest conductance, lid open %.2f C; on 32.53's %.2f C closed, %.2f C open"
      % (a["air_closed_W4"], a["air_open_W4"], a["air_closed_3253"], a["air_open_3253"]))
    w("   Layer 3's +62.1 C reproduced (rounded down): %s; gap against +60 C: %.2f K (on the inside air)" % (R["agree"]["LO-01a"][2], R["gaps"]["LO-01a"]))
    w("   on the pack the cells sit above that air by their own I2R (MODELED, pwr_budget.cell_temp, the block's lowest film): %.2f C, gap %.2f K;"
      % (a["cell_closed_W4_pack"], a["cell_closed_W4_pack"] - lim["discharge"][1]))
    w("   on 32.53's lid-closed conductance %.2f C (no collision). Against the hot stop's first step (H1 at a reading of +%.1f C): %.2f K over on the bound."
      % (a["cell_closed_3253_pack"], hot["H1"], a["cell_closed_W4_pack"] - hot["H1"]))
    w("LO-01b  in use, the envelope's %.0f C once warm: inside air %.2f C on the highest conductance (rise %.2f K, PS-IDLE-SPEC lid open); cells %.2f C: above the %.0f C floor by %.2f K (no collision)"
      % (R["env"]["in_use"]["min"], R["b"]["air"], R["b"]["rise_air"], R["b"]["cell"], lim["discharge"][0], R["b"]["cell"] - lim["discharge"][0]))
    w("LO-01c  charging in use: the 0 to 45 C window is reached at ambients of %.1f to +%.1f C by state on the independent bound (MODELED, the records' ceilings); the charge is held off outside it (no collision)"
      % (R["c"]["reach_lo"], R["c"]["reach_hi"]))
    w("LO-01d  D-02a's +%.0f C operating margin, %.0f h (E3-O; qualification margin: no damage and recovery to specification, no shutdown)" % (d["amb"], d["hours"]))
    w("   inside air in the heat stage lid open, both configurations (MODELED): %.2f to %.2f C; gap %.2f to %.2f K (Layer 3: 1.6 to 14.2 K; %s); on the pack at the worst corner %.2f C"
      % (d["air_lo"], d["air_hi"], R["gaps"]["LO-01d"][0], R["gaps"]["LO-01d"][1], R["agree"]["LO-01d"][2], d["cell_hi_pack"]))
    w("LO-01e  E5: %.0f cycles of %.0f h at %.0f %% RH, %.0f to %.0f C, on an input with the kit logging (qualification margin, SC-03): the pack idle at the inside air,"
      % (e["cycles"], e["hours"], e["rh"], e["lo"], e["amb"]))
    w("   %.2f to %.2f C (MODELED); gap at least %.2f K (Layer 3: at least 6.63 K; %s); the dwell's length at +%.0f C stated in TEST-PLAN: %s"
      % (e["air_lo"], e["air_hi"], R["gaps"]["LO-01e"], R["agree"]["LO-01e"][2], e["amb"], "yes" if R["tp"]["E5_dwell_stated"] else "no"))
    w("LO-01f  D-02a's +%.0f C storage, %.0f h (E3-S), stored kit, pack fitted, every input unplugged: cells at the ambient; gap %.0f K (Layer 3: 11 K; %s)"
      % (R["f"]["amb"], R["f"]["hours"], R["gaps"]["LO-01f"], R["agree"]["LO-01f"][2]))
    w("LO-01g  D-02a's %.0f C storage, %.0f h (E4-S): gap %.0f K on Ver. 1.1, %.0f K on Version 1.0 (Layer 3: 13 K; 33 K; %s)"
      % (R["g"]["amb"], R["g"]["hours"], R["gaps"]["LO-01g"][0], R["gaps"]["LO-01g"][1], R["agree"]["LO-01g"][2]))
    w("LO-01h  storage inside the envelope (%.0f to +%.0f C three months, %.0f to +%.0f C a year): none on Ver. 1.1; on Version 1.0 %.0f K at the cold end and %.0f K at the one-year top (%s)"
      % (R["env"]["storage_3_months"]["min"], R["env"]["storage_3_months"]["max"], R["env"]["storage_1_year"]["min"], R["env"]["storage_1_year"]["max"],
         R["gaps"]["LO-01h"][0], R["gaps"]["LO-01h"][1], R["agree"]["LO-01h"][2]))
    w("   Lid open at the same corner (1.22 W/K): the cells on the pack reach %.2f C and, on shore, the inside air %.2f C (the front end's loss counted): past +60 C as well (3a)."
      % (R["open_worst"]["cell_pack"], R["open_worst"]["air_shore"]))
    w("In-use (the envelope, operate to specification): LO-01a, LO-01b, LO-01c, LO-01h. Qualification margins (D-02a, SC-03; no damage and recovery): LO-01d, LO-01e, LO-01f, LO-01g.")
    w("")
    # ---------------------------------------------------------------- 2: the feasibility screen
    H = R["hold"]
    w("== 2. THE FEASIBILITY SCREEN: every required charging, discharging, transport and storage condition (the owner's refinement of 2 October 2026)")
    w("Each row: ambient, duration, configuration and charge state (TEST-PLAN), the governing MAKER limit, the power for thermal control, the gap, the approaches judged, the result.")
    w("A rejection is kept only where physics or a bounded figure gives it; a route with a missing input is INCONCLUSIVE, with the input named.")
    rows = screen_rows(R)
    for r in rows:
        w("%s %s" % (r["id"], r["cond"]))
        w("   ambient %s; duration %s; configuration %s" % (r["amb"], r["dur"], r["cfg"]))
        w("   limit: %s" % r["limit"])
        w("   power for thermal control: %s" % r["power"])
        w("   gap: %s" % r["gap"])
        for ap in r["approaches"]:
            w("   - %s" % ap)
        w("   SCREEN: %s" % r["result"])
    R["screen"] = rows
    w("")
    # ---------------------------------------------------------------- 3: the thermal routes, bounded
    m, wo, be = R["meas"], R["worst"], R["best"]
    A_E, A_B, A_in = R["areas"]
    w("== 3. The thermal routes, bounded")
    w("3a LO-01a: the thresholds (MODELED, PS-SURV-R at PLAN heat, +%.0f C; on shore the front end's and charger's loss on the loads adds %.3f W; the block's lowest film)."
      % (R["env"]["in_use"]["max"], R["shore_heat"] - R["heat"]["SURVR"][0]))
    w("   The conductance from which each criterion holds (W/K), the same in either lid state:")
    for c in R["crit"]:
        w("   %-62s on the %-5s %.4f" % (c[0], c[1], c[4]))
    gv, gn = R["gov"]["all"], R["gov"]["no_sensor_term"]
    w("   The cell rating alone: %.4f W/K on the pack. FEA-008's own LO-01a criterion (the +59 C abort): %.4f W/K. The complete E3-A and E3-L pass line: %.4f W/K (%s, on %s)."
      % (R["gov"]["rating_pack"], R["gov"]["fea008_pack"], gv[4], gv[0], gv[1]))
    w("   T-H1 must read at least %.3f W/K with the fans, lid closed AND lid open (the heat stage runs in both). The record's bounds: independent %.2f to %.2f (closed) and %.2f to %.2f W/K (open);"
      % (gv[4], R["Gb"]["closed_fans"][0], R["Gb"]["closed_fans"][1], R["Gb"]["open_fans"][0], R["Gb"]["open_fans"][1]))
    w("   appendix 32.53 %.1f to %.1f (closed) and %.1f to %.1f W/K (open). Lid open at the bound's lowest %.2f W/K the cells on the pack reach %.2f C and the air on shore %.2f C: past +60 C as well."
      % (R["G32b"]["closed_fans"][0], R["G32b"]["closed_fans"][1], R["G32b"]["open_fans"][0], R["G32b"]["open_fans"][1], R["Gb"]["open_fans"][0], R["open_worst"]["cell_pack"], R["open_worst"]["air_shore"]))
    w("   Dependencies that fail today and stay visible: %s (TEST-PLAN E3-L); F2's body (P13, PWR-F12); the gauge's ADC and gradient terms (P14, not in the thresholds above); HIGH heat (not covered)."
      % R["tpx"]["bank_r1"].strip())
    w("3b The pocket coupling measure: the block's east face (%.5f m2) against the east wall through a gap filler of the pocket's widest gap (%.2f mm, CASE-MARGINS M4b; k %.1f W/mK, ASSUMPTION),"
      % (A_E, R["m4b_gap_max_mm"], K_PAD))
    w("   its base (%.5f m2) on the floor through the heater mat (%.1f mm, k %.1f W/mK, ASSUMPTION; the mat's sheet states neither: %s); the other four faces (%.5f m2) in the inside air at %.1f to %.1f W/m2K."
      % (A_B, T_MAT * 1000.0, K_MAT, not R["S"]["mat"]["thickness_stated"], A_in, R["blk"]["h"][0], R["blk"]["h"][1]))
    w("   Coupling to ambient %.4f (worst) to %.4f W/K (best), to the inside air %.4f (worst) to %.4f W/K (best): f = %.3f to %.3f; the enclosure loses %.4f to %.4f W/K of skin (counted); a 3 W/mK filler adds %.4f W/K."
      % (wo["g_amb"], be["g_amb"], wo["g_in"], be["g_in"], wo["f"], be["f"], wo["dg"], be["dg"], R["pad_sens"]))
    w("   LO-01a lid closed at the bound's lowest: cells %.2f C without it (two-node reproduces pwr_budget: %s), %.2f C (worst) to %.2f C (best) with it; on shore %.2f C. Against the complete pass line:"
      % (R["a"]["cell_closed_W4_pack"], m["two_node_matches_record"], m["a_pack_worst"][1], m["a_pack_best"][1], m["a_input_worst"][1]))
    for name, v, lim_c in m["fallback_vs"]:
        w("      %-14s %.2f C against %.2f C: %s" % (name, v, lim_c, "holds" if v <= lim_c else "fails by %.2f K" % (v - lim_c)))
    w("   So the measure closes the cell criteria only; the air criteria are the enclosure's (3a). It is a fallback for the cells, never a substitute for T-H1's conductance.")
    w("   Placement: the block's top lies about %.2f mm under board B's underside (SHORTLIST's %.2f mm of room plus the 1.0 mm minimum, CASE-MARGINS M6), which has no local model (POWER-THERMAL.md 9.2)."
      % (R["room"]["height"] + 1.0, R["room"]["height"]))
    c = R["cold"]
    w("3c The cold end the measure touches (LO-01b; PS-IDLE-SPEC on the pack, lid open, %.0f C, the highest conductance): cells %.2f C without it, %.2f C with it (%.2f C on W4's highest);"
      % (R["env"]["in_use"]["min"], c["base"][1], c["meas"][1], c["meas_w4"][1]))
    w("   holding %.1f C (1 K over UTD's %.1f C reading, INFERRED) takes %.2f W into the cells, %.2f W from the battery with the mat's regulator (%.1f %% of PS-IDLE-SPEC's %.2f W; firmware owner)."
      % (c["target"], R["ladder"]["UTD"], c["p_h"], c["p_h_batt"], 100.0 * c["p_h_batt"] / c["w"], c["w"]))
    cc = R["cchg"]
    w("3d Charging at the cold end: the mat puts %.1f W into the block (MAKER, RS PRO 245-556 at 12 V) and its regulator %.1f W into the air (POWER-THERMAL.md 7.1); at %.0f C on input power, the pack idle,"
      % (R["mat_split"][0], R["mat_split"][1], R["env"]["in_use"]["min"]))
    w("   the cells reach %.2f C (record's model) and %.2f C (with the coupling): over UTC's %.1f C and the panel's +%.0f C hold (MODELED)." % (cc["base"][1], cc["meas"][1], cc["floor"], cc["hold"]))
    sl = H["slow"]
    w("3e Storage hold times (INFERRED): the cells' own time constant in the pocket %.0f to %.0f s; the closed, stopped kit %.2f to %.2f h (32.53's %.0f to %.0f kJ/K over the lid-closed still-air bound)."
      % (H["tau_pack_s"][0], H["tau_pack_s"][1], H["tau_kit_s"][0] / 3600.0, H["tau_kit_s"][1] / 3600.0, R["C_kit"][0] / 1000.0, R["C_kit"][1] / 1000.0))
    w("   After %.0f h from the most favourable start (steps of %.0f K and %.0f K) the cells lag the ambient by %.2f K (hot) and %.2f K (cold) as one node, %.3f K and %.3f K as two nodes"
      % (R["f"]["hours"], H["step_hot"], H["step_cold"], H["resid_hot"], H["resid_cold"], H["resid2_hot"], H["resid2_cold"]))
    w("   (the kit's %.0f J/K beside the cells' %.0f J/K, %.2f W/K to ambient, %.4f W/K to the cells). Heating the whole kit at the -20 C floor for 24 h would take %.0f to %.0f Wh (the first issue's figure);"
      % (sl["C_tot"] - sl["C_p"], sl["C_p"], sl["G_e"], sl["G_b"], H["e_kit_cold_Wh"][0], H["e_kit_cold_Wh"][1]))
    w("   heating only the pack is 3g.")
    pas = R["passive"]
    for k in ("LO-01f", "LO-01g"):
        pv = pas[k]
        w("3f %s passive: to keep the cells within %.0f K of the start for 24 h against a %.0f K step (two nodes, the slowest kit), the pack's coupling must fall under %.4f W/K from %.4f:"
          % (k, pv["allow"], pv["step"], pv["g_max"], R["Gblk"][0]))
        w("   %.1f mm of insulation at k %.2f W/mK (ASSUMPTION) round the block, against 0.77 to 2.66 mm of room in D-06's pocket: REJECTED within the pocket (today the cells move %.2f K)."
          % (pv["ins_mm"], K_INS, pv["now_reached"]))
    sh = R["selfheat"]
    rs, rf = sh["rows"]["slow"], sh["rows"]["fast"]
    w("3g LO-01g, the %.0f C storage margin (E4-S, %.0f h), in three cases. Ambient and cell temperatures are kept apart; the pack's discharge window (-10 to +60 C, 3.12) governs" % (R["g"]["amb"], R["g"]["hours"]))
    w("   whenever the pack feeds a heater, the storage rows only when it does not. One boundary: the source's terminals; the mat's 7.5 W into the block, its regulator's %.3f of that into the air," % sh["k_reg"])
    w("   the gauge's NORMAL draw (%.0f uA typical, MAKER SLUSC67B 6.5: %.4f W) when the pack feeds it. Slow and fast corners: %.4f and %.4f W/K in series (pack, air, case)." % (sh["i_norm_ua"], sh["p_gauge"], sh["g_series"][0], sh["g_series"][1]))
    w("   WITHDRAWN as a feasibility basis: the comparison of 38.1 to 106.1 Wh with the pack's nominal %.1f Wh. It is a nominal comparison; the usable-energy comparison below replaces it." % R["hold"]["pack_Wh_nom"])
    w("   (i) A warm pack kept inside its limits for the exposure.")
    w("      Fed by the pack: the heater discharges the cells, so the setpoint is UTD's %.1f C reading plus the published cold-side budget %.2f K = %.2f C (the gradient and ADC terms TBD)."
      % (R["ladder"]["UTD"], sh["budget_cold"], sh["set_pack"]))
    w("      Hold: %.2f to %.2f W into the cells, %.2f to %.2f W at the pack's terminals, %.1f to %.1f Wh for %.0f h with no cool-down credit."
      % (rs["pm_pack"], rf["pm_pack"], rs["pt_pack"], rf["pt_pack"], rs["Wh_pack"], rf["Wh_pack"], R["g"]["hours"]))
    w("      Usable at the stored charge: %.0f %% (Ver. 1.1 3.13) less the %.0f %% reserve, aged to %.0f %% (SC-23), times the cold factor at the setpoint, unknown between MAKER 7.5's %.2f (1C, -10 C) and 1.0:"
      % (100 * sh["soc_store"], 100 * sh["reserve"], 100 * sh["age"], sh["cold_f"][0]))
    w("      %.1f to %.1f Wh, so the heat lasts %.1f to %.1f h of the %.0f h, a reserve of %.1f to %.1f Wh after the exposure; from a full charge %.1f to %.1f h."
      % (sh["e_use_stored"] + sh["dur_h_range"] + (R["g"]["hours"],) + sh["reserve_after_Wh"] + sh["dur_full_h_range"]))
    w("      And in the stored state the gauge is in shutdown: '%s' (MAKER, SLUUAQ3A 5.4.2), so the pack-fed heater has no protected path unless the gauge stays awake." % sh["shutdown_fets_off"])
    w("      Scope: not available at REQ-025's stored state (its shutdown and its 30 %% charge); with the gauge awake and a full charge, %.1f to %.1f h, so 24 h only at the low-demand, high-cold-factor end." % sh["dur_full_h_range"])
    w("      Fed by a separate primary source (the pack stays in its storage row and in shutdown): setpoint the -20 C floor plus the thermostat's tolerance and the in-pack gradient (both TBD):")
    w("      %.2f to %.2f W into the cells at the floor itself, %.1f to %.1f Wh for %.0f h driven direct (%.1f to %.1f Wh through the 12 V regulator), plus %.2f to %.2f Wh per K of margin."
      % (rs["pm_prim"], rf["pm_prim"], rs["Wh_prim_direct"], rf["Wh_prim_direct"], R["g"]["hours"], rs["Wh_prim_reg"], rf["Wh_prim_reg"], rs["Wh_per_K"], rf["Wh_per_K"]))
    w("      Start and control: a thermostat on the block, independent of the gauge and the kit (both off), arms with the stored state and closes at its setpoint; the source must deliver at -33 C.")
    w("      Its usable energy at -33 C, the thermostat's tolerance, the gradient, a place in the case and its transport classification (D-04) are NAMED UNKNOWNS: its duration is not computed.")
    w("      Cool-down credit (ASSUMPTION: E4-S's starting state is not stated; from the sheet's %.0f C standard temperature): %.2f to %.2f h before the pack reaches %.2f C, %.2f to %.2f h before -20 C."
      % (sh["t_start"], rf["tc_pack_h"], rs["tc_pack_h"], sh["set_pack"], rf["tc_prim_h"], rs["tc_prim_h"]))
    w("      Recovery: E4-O follows E4-S (%.0f h at %.0f C); a pack held at the -20 C floor is below the -10 C discharge floor, so E4-O starts from shore or vehicle input or after" % (R["tp"]["E4-O"][0], R["tp"]["E4-O"][1]))
    w("      warming, as TEST-PLAN and D-02d already allow; a pack held at -8.14 C could start from itself.")
    w("   (ii) A pack already cold-soaked before any heater starts: below -20 C it has already left its storage row and no heater undoes that; between -20 and -10 C the pack may not")
    w("      discharge (3.12) and the gauge holds its discharge FET off below UTD (recovery %.1f C), so only a separate source can rewarm it: %.3f to %.3f Wh into the cells per K, plus the losses." % (R["ladder"]["UTD_rec"], sh["warm_per_K_Wh"][0], sh["warm_per_K_Wh"][1]))
    w("      Its scope if the unknowns land: E4-S's %.0f h at -33 C from a warm stored kit, the source supplying at least %.1f to %.1f Wh at -33 C plus %.2f to %.2f Wh per K of margin and its own reserve."
      % (R["g"]["hours"], rs["Wh_prim_direct"], rf["Wh_prim_direct"], rs["Wh_per_K"], rf["Wh_per_K"]))
    w("      F2 sits at about the inside air (%.1f to %.1f C at the hold), below its %.0f C operating floor: Eaton's answer, or the heated zone extended to board P (a Layer 7 item)."
      % (R["g"]["amb"] + sh["air_dev"][0], R["g"]["amb"] + sh["air_dev"][1], S["F2"]["operating"][0]))
    w("   (iii) Heating lost, or its energy spent, at the pack-fed hold: the cells pass the -20 C floor %.2f to %.2f h later (two nodes, from the heated steady state); a separately fed" % (rf["t_lost_pack_h"], rs["t_lost_pack_h"]))
    w("      hold at the floor itself passes it at once, so its margin must cover the source's depletion as well. Neither the gauge (in shutdown) nor the kit records the event (a named item).")
    e5 = R["e5"]
    w("3h E5's cycle: TEST-PLAN states %.0f cycles of %.0f h between %.0f and %.0f C and no dwell or ramp. Any passive network passes the cycle's mean, so the pack's surroundings average"
      % (R["e"]["cycles"], R["e"]["hours"], R["e"]["lo"], R["e"]["amb"]))
    w("   the mean ambient plus the rise: storage can help only if the mean ambient is under %.2f C (worst rise) to %.2f C (best). For a symmetric cycle (mean %.0f C, %.0f K amplitude, ASSUMPTION):"
      % (e5["mean_max"][0], e5["mean_max"][1], e5["sym"]["mean"], e5["sym"]["amp"]))
    w("   possible at the worst corner: %s; at the best a %.2f h time constant, regeneration in the cool half included, so %.1f to %.1f mm of insulation or %.1f to %.1f kJ/K of added heat capacity,"
      % ("yes" if e5["sym"]["feasible_worst"] else "no", e5["sym"]["tau_s"] / 3600.0, min(e5["sym"]["ins_mm"]), max(e5["sym"]["ins_mm"]), e5["sym"]["c_need_kJ"][0], e5["sym"]["c_need_kJ"][1]))
    w("   against 0.77 to 2.66 mm and a full pocket: INCONCLUSIVE until the profile is stated; for the symmetric profile, not within D-06's pocket.")
    co = R["cool"]
    w("3i Powered cooling (a thermoelectric stage; COP %s ASSUMPTION; hot side at most %.0f K over the ambient it rejects to):" % (" to ".join("%.1f" % v for v in COP), HOT_RISE))
    for k in ("E3-O", "E5", "E3-S"):
        r = co[k]
        w("   %-5s hold %.2f C: cold-side load %.2f to %.2f W; through a path out of the case it needs %.3f to %.3f W/K (COP 1.0) or %.3f to %.3f W/K (COP 0.5); into the inside air the loop closes at the worst corner: %s"
          % ((k, r["t_hold"]) + r["qc"] + r["g_out_need"][1.0] + r["g_out_need"][0.5] + (", ".join("COP %.1f %s" % (cp, "yes" if ok else "no") for cp, ok in sorted(r["loop_ok_worst"].items())),)))
    w("   The pack's own skin path (3b) is %.3f to %.3f W/K: enough only at E3-O's best corner. E3-S has no input: %.0f to %.0f Wh over 24 h from a separate source."
      % (co["skin"] + (co["E3-S"]["Wh"][1.0][0], co["E3-S"]["Wh"][0.5][1])))
    w("   INCONCLUSIVE, the inputs missing: a cooler's maker sheet, the input's spare power (L4-E4's 4.70 A limit less the kit's load, not derived here), the volume, a sealed path out of the case.")
    kd, p13 = R["kd"], R["p13"]
    w("3j PWR-F12's key-down: %.0f A for %.0f s (%.1f A a cell) from C1's +%.0f C warms the cells %.2f to %.2f K adiabatically (MODELED), to %.2f to %.2f C, inside +60 C."
      % (R["tpx"]["p13_kd"][1], R["tpx"]["p13_kd"][2], kd["i_cell"], kd["from"], kd["rise"][0], kd["rise"][1], kd["to"][0], kd["to"][1]))
    w("3k P13's hour at %.0f A (%.2f A a cell): the cells' own %.2f to %.2f W, a steady rise of %.1f to %.1f K over the block's film and %.1f to %.1f K adiabatic over the hour (MODELED):"
      % ((R["tpx"]["p13_a"], p13["i_cell"]) + p13["w"] + p13["steady"] + p13["adiabatic"]))
    w("   'the block at the pack's hot limit' holds the cells inside +60 C only if the limit is set at the cell surface and the chamber runs that much cooler (a definition item for P13's owner).")
    lev = R["e3l_levels"]
    w("3l E3-L's levels at the bound's lowest lid-closed conductance (MODELED): " + "; ".join("+%.0f C: %s, air %.2f C, cells %.2f C" % (t, v[0], v[1], v[2]) for t, v in sorted(lev.items())))
    w("")
    # ---------------------------------------------------------------- 4: cells alongside
    w("== 4. The cells, alongside the thermal measures (at most three solutions, each inside D-06's single 4S3P in the east pocket)")
    s6, s15, hl, hg, mp = S["30Q6"], S["30Q_2015"], S["HL18650V"], S["HG2"], S["P28A"]
    cand = R["cand"]
    w("S1 Samsung INR18650-35E as ruled (MAKER, Ver. 1.1): the limits of section 1; min %.2f Ah, %.1f Wh nominal; %.0f A continuous; USD %.2f a cell (l3batt reading)."
      % (lim["c_min"], cand["35E"]["wh_nom"], lim["i_cont"], R["price_35e"]))
    w("S2 Samsung INR18650-30Q, current revision (MAKER, %s): ambient charge %.0f to %.0f C, discharge %.0f to %.0f C; cell surface charge %.0f to %.0f C,"
      % (s6["doc"], s6["amb_charge"][0], s6["amb_charge"][1], s6["amb_discharge"][0], s6["amb_discharge"][1], s6["surf_charge"][0], s6["surf_charge"][1]))
    w("   discharge %.0f to %.0f C ('must re-discharge release < %.0f C'); storage 1 year %.0f to %.0f C, 3 months %.0f to %.0f C, 1 month %.0f to %.0f C at %s;"
      % (s6["surf_discharge"][0], s6["surf_discharge"][1], s6["release"], s6["st_1y"][0], s6["st_1y"][1], s6["st_3m"][0], s6["st_3m"][1], s6["st_1m"][0], s6["st_1m"][1], s6["soc"]))
    w("   min %.2f Ah, %.1f Wh nominal; %.0f A continuous; cut-off %.1f V; charge to %.2f V; -10 C %s %% of its 23 C capacity at 10 A; USD %.2f (18650 Battery Store, in stock %s)."
      % (s6["c_min"], cand["30Q6"]["wh_nom"], s6["i_cont"], s6["cutoff"], s6["v_chg"], s6["cold"][1], R["price_30q"], R["price_30q_stock"]))
    w("   Its 2015 Version 1.0 (MAKER, %s): surface discharge to %.0f C, storage 1.5 years %.0f to %.0f C, 1 month %.0f to %.0f C at %s, and the same car clause (%s) and 'below 60' storage (%s);"
      % (s15["doc"], s15["surf_discharge"][1], s15["st_1y5"][0], s15["st_1y5"][1], s15["st_1m"][0], s15["st_1m"][1], s15["soc"], s15["car"], s15["store60"]))
    w("   the 2024 customer draft (%s) keeps the ambient discharge to %.0f C and storage to %.0f C (read; no figure taken from a draft)."
      % (S["30Q6_draft"]["doc"], S["30Q6_draft"]["amb_discharge"][1], S["30Q6_draft"]["st_1m"][1]))
    w("S3 a wide-temperature 18650, the HL18650V (%s; %s, page sha256 %s): discharge %.0f to %.0f C, charge %.0f to %.0f C (reduced rates below +10 C),"
      % (hl["company"], hl["doc"], hl["page_sha"][:16], hl["discharge"][0], hl["discharge"][1], hl["charge"][0], hl["charge"][1]))
    w("   storage %.0f to %.0f C 12 months, %.0f to %.0f C 6 months, %.0f to %.0f C 3 months, %.0f to %.0f C within 30 days; no state of charge, no basis (ambient or surface), no recovery figure;"
      % (hl["st_12m"][0], hl["st_12m"][1], hl["st_6m"][0], hl["st_6m"][1], hl["st_3m"][0], hl["st_3m"][1], hl["st_30d"][0], hl["st_30d"][1]))
    w("   min %.2f Ah, %.1f Wh nominal; %.0f A continuous; cut-off %.2f V; charge to %.1f V; USD %.2f (a marketplace seller, not the maker; 10 to 4,999 pieces). Its figures are INFERRED (a page, not a specification)."
      % (hl["c_min"], cand["HL18650V"]["wh_nom"], hl["i_cont"], hl["cutoff"], hl["v_chg"], R["price_hl"]))
    w("Read and set aside: LG INR18650HG2 (MAKER, %s): discharge %.0f to %.0f C in 2.9 but %.0f to %.0f C in its own 5.1 cautions, storage 1 month %.0f to %.0f C, 1 year %.0f to %.0f C"
      % (hg["doc"], hg["discharge_2_9"][0], hg["discharge_2_9"][1], hg["discharge_5_1"][0], hg["discharge_5_1"][1], hg["st_1m"][0], hg["st_1m"][1], hg["st_1y"][0], hg["st_1y"][1]))
    w("   (its own text limits it to +60 C, and the one-year row fails LO-01h); Molicel INR-18650-P28A (MAKER, %s): ambient charge %.0f to %.0f C, discharge %.0f to %.0f C, no storage clause (%s), min %.2f Ah."
      % (mp["doc"], mp["charge"][0], mp["charge"][1], mp["discharge"][0], mp["discharge"][1], not mp["storage"], mp["c_min"]))
    w("Energy at the kit's conditions (MODELED, pwr_budget.usable at PS-IDLE-SPEC %.2f W, +20 C, aged to 80 %%, the 35E's rate table for all three, INFERRED for S2 and S3):" % R["w_idlespec"])
    for k in ("35E", "30Q6", "HL18650V"):
        cd = cand[k]
        w("   %-9s %.1f Wh usable, %.2f h battery-only (%+.1f %% against S1); REQ-072's objective is %s (DR-01 stays FAIL for all three)"
          % (k, cd["usable_wh"], cd["hours"], 100.0 * (cd["usable_wh"] / cand["35E"]["usable_wh"] - 1.0), R["dr01"]))
    w("Cold, -10 C (aged 80 %%, the sheet's own cold point as a lower bound at the kit's current): 35E %.1f Wh (factor %.2f, 1C), 30Q6 %.1f Wh (factor %.2f, 10 A), HL18650V not stated at -10 C."
      % (cand["35E"]["cold_wh"], cand["35E"]["cold_f"], cand["30Q6"]["cold_wh"], cand["30Q6"]["cold_f"]))
    w("Cycle terms: 35E %s (MAKER 7.9); 30Q6 %s (MAKER 3.10; harsher conditions, not comparable); HL18650V %s (INFERRED, page)."
      % (lim["cycle"], s6["cycle"], hl["cycle"]))
    w("Current against PS-ALLTX (18 A on the pack, %.1f A a cell for 60 s): S1 %.0f A, S2 %.0f A, S3 %.0f A continuous a cell: all carry it (MAKER; S3 INFERRED)."
      % (cand["35E"]["i_need"], cand["35E"]["i_cont"], cand["30Q6"]["i_cont"], cand["HL18650V"]["i_cont"]))
    w("Fit in the east pocket (INFERRED, the ruled block 2 cells along the axis, 3 across, 2 high; room at the worst less the 1.0 mm minimum: axis %.2f, across %.2f, height %.2f mm):"
      % (R["room"]["axis"], R["room"]["across"], R["room"]["height"]))
    for k in ("35E", "30Q6", "HL18650V"):
        g = cand[k]["grow_mm"]
        w("   %-9s growth %+.2f / %+.2f / %+.2f mm: fits %s" % (k, g[0], g[1], g[2], cand[k]["fits"]))
    w("The documented limits against each row (True = the row's level is inside the cell's own limits):")
    for k in ("35E", "30Q6", "HL18650V"):
        w("   %-9s %s" % (k, "  ".join("%s %s" % (r[3:], R["meets"][k][r]) for r in ("LO-01a", "LO-01d", "LO-01e", "LO-01f", "LO-01g", "LO-01h"))))
    w("   30Q6 read with its ambient as the kit's outside air (a reading Samsung's sheet does not state): a %s, d %s" % (R["meets"]["30Q6_outside_ambient"]["LO-01a"], R["meets"]["30Q6_outside_ambient"]["LO-01d"]))
    w("Protection and charger changes: all three are 4.2 V a cell (the BQ25731's 16.8 V unchanged); S2 and S3 need the gauge's chemistry data for a new cell (BQ4050 image);")
    w("   S2's ambient discharge limit is the 35E's +60 C, so the ladder (OTC %.1f, OTD %.1f, UTC %.1f, UTD %.1f C) and the hot stop stay as they are unless Samsung reads its ambient as the outside air;"
      % (R["ladder"]["OTC"], R["ladder"]["OTD"], R["ladder"]["UTC"], R["ladder"]["UTD"]))
    u2 = S["U2"]
    w("   The protection and control redesign is the entry cost of any cell used above +60 C (S2 under the outside-air reading, S3): keeping H1 and H2 at their 35E-derived readings still stops")
    w("   every module in the hot margins; U2's variants are not drop-ins (MAKER, SLUSEG7D p.3): %s;" % "; ".join(
        "%s OT %.0f C, OVP %.3f V, UVP %s, OV delay %s, COUT %s" % (k, v["ot"], v["ovp"], v["uvp"], v["ovd"], v["drive"]) for k, v in sorted(u2["rows"].items())))
    w("   so the hot ladder (C1, H1, H2, OTD, SOT, U2's OT and its voltage thresholds, the PTC) and F2's replacement must be re-specified together, with their tolerance, nuisance-trip and")
    w("   permanent-trip bounds recomputed for storage and for powered operation. This record does not specify that redesign: it is the cost of entry of S2's and S3's hot rows.")
    w("Thermal-control burden: S1 none beyond the design (C1, the hot stop, the mat on input power; the coupling only for the cells, below T-H1's threshold); S2 the same; S3 the same.")
    w("   Evidence outstanding: S1 T-H1, E3-A, E3-L, E3-H, the lot's revision; S2 those plus Samsung's reading of its ambient clause and the redesign; S3 the maker's signed specification")
    w("   (none found), the maker's identity behind the marketplace listings, the redesign, the gauge data.")
    w("Assessed, not held (the collaborator's reading in check 1, not read by this record): a Saft MP174565 xtd prismatic cell (preliminary sheet, October 2014): as 4S1P only 58.4 Wh, and 8 A")
    w("   continuous with 16 A pulses against the pack's 18 A: not a substitute inside D-06; another form factor or chemistry would need its own energy, current, fit, charger and protection work.")
    w("")
    w("4b The bounded shortlist (the owner's refinement of 2 October 2026, item 4): at most three approaches, the pack and enclosure constraints kept unless named.")
    for line in shortlist_lines(R):
        w("   " + line)
    w("")
    # ---------------------------------------------------------------- 5: decisions, the remaining gap, and why no owner decision is forced
    w("== 5. The decision per row, what is closable and conditional, and the remaining feasibility gap")
    for k in sorted(R["dec"]):
        dd = R["dec"][k]
        w("%s %s (evidence %s)" % (k, dd["decision"], "+".join(dd["evidence"])))
        w("   acceptance, complete: %s" % dd["acceptance"])
        for rt in dd["routes"]:
            w("   route %s: %s. %s. Missing: %s" % (rt["status"], rt["route"], rt["basis"], rt["missing"]))
        w("   gap: %s" % dd["gap"])
    w("Closable now: none. No collision: LO-01b, LO-01c. Conditional: LO-01a (T-H1 at least %.3f W/K in each lid state, and its failing dependencies), LO-01h (the lot's revision)."
      % R["gov"]["all"][4])
    w("Open engineering obligations: LO-01d, LO-01e, LO-01f, LO-01g, each with at least one route INCONCLUSIVE on named inputs (above); none has every route rejected.")
    w("SELECTION: A1 (4b), the 35E as ruled with local thermal management; no cell change and no spend now. S2 is not recommended (it moves no margin row on its own sheet, misses"
      " LO-01h's year at its 23 C and costs %.1f %% of the energy)." % (-100.0 * (R["cand"]["30Q6"]["usable_wh"] / R["cand"]["35E"]["usable_wh"] - 1.0)))
    w("OWNER DECISION: none is forced (rows with every route rejected: %s). A1 changes no approved constraint; A2, A3 and a pack-fed heater would (D-06's cell or pocket, REQ-025's"
      % (", ".join(R["forced_rows"]) or "none"))
    w("   stored state), and none of them is needed while A1's routes stand; A1's purchases are the owner's spend only when made. A missing cell rating is a component limitation plus")
    w("   missing feasibility evidence, not a contradiction between owner requirements (D-29, D-36, cell_provenance). FEA-008 stays open as the session's engineering obligation.")
    w("Possible later changes (none proposed now; each would be the owner's only once every route of a row within the requirements is shown unavailable on bounded evidence):")
    for line in later_lines(R):
        w("   " + line)
    w("")
    # ---------------------------------------------------------------- 6: the battery path's other thermal items
    F2 = S["F2"]
    w("== 6. The battery path's other thermal items (PWR-F12, F2 and the protection temperatures)")
    w("F2 (MAKER, %s): operating %.0f to +%.0f C; '%s'; endurance lines '%s' and '%s' (test conditions, not a rating)."
      % (F2["doc"], F2["operating"][0], F2["operating"][1], F2["storage_line"], F2["hi_test"], F2["lo_test"]))
    w("   Board P sits beside the block, so F2 is at about the inside air or the cells (INFERRED): past its operating range at LO-01a's worst corner %s (%.2f C), LO-01d %s, LO-01e %s, LO-01f %s,"
      % (R["f2"]["LO-01a"], R["a"]["air_closed_W4"], R["f2"]["LO-01d"], R["f2"]["LO-01e"], R["f2"]["LO-01f"]))
    w("   LO-01g %s; its storage line, if it covers a mounted part, also misses the storage envelope (cold %s, hot %s): Eaton (clarification/eaton-scf9550.txt, extending Q-E2)."
      % (R["f2"]["LO-01g"], R["f2"]["storage_env"][0], R["f2"]["storage_env"][1]))
    w("   F2's own 0.32 to 0.81 W at 18 A is unpublished in rise, so its margin after a key-down from +55 C stays PWR-F12's (P13). The coupling changes neither the key-down nor F2's air.")
    w("U2 (BQ7720700): its fixed %.0f C over-temperature trips somewhere in %.1f to 77.5 C at the network, so at the +%.0f C storage margin a destructive trip of a fitted pack is permitted (%s), not certain."
      % (S["U2"]["ot"]["BQ7720700"], R["u2"]["trip_lo"], R["f"]["amb"], R["u2"]["LO-01f"]))
    w("The gauge's thresholds stay inside REQ-046's windows (OTC %.1f, OTD %.1f, UTC %.1f, UTD %.1f C; THERMAL-COORDINATION.md section 5): this record moves none. With the coupling the block"
      % (R["ladder"]["OTC"], R["ladder"]["OTD"], R["ladder"]["UTC"], R["ladder"]["UTD"]))
    w("   gains a gradient (wall side cooler, the side under board B hotter), so the thermistors go on the hottest cells and P14's gradient term is re-measured (INFERRED).")
    w("")
    w("== 7. Downstream items (owner by layer; acceptance)")
    for line in downstream_lines(R):
        w(line)
    w("")
    w("== 8. Predicates")
    pr = predicates(R)
    for k in sorted(pr):
        w("%s: %s" % (k, pr[k]))
    if not all(pr.values()):
        refuse(4, "a predicate failed: %s" % [k for k, v in pr.items() if not v])
    return L


def screen_rows(R):
    S, a, d, e = R["S"], R["a"], R["d"], R["e"]
    lim = S["35E_11"]
    H, G2, hot, tp, tpx = R["hold"], R["gaps"], R["hot"], R["tp"], R["tpx"]
    env, gv, ow, sh, pas, co, fs = R["env"], R["gov"]["all"], R["open_worst"], R["selfheat"], R["passive"], R["cool"], R["full_storage"]
    fans = "fans and heat spreading cannot cool the cells below a hotter ambient"
    rows = [
        {"id": "C01", "lo": "LO-01a", "cond": "discharge in use at the hot edge, on the pack, lid closed (E3-L at +%.0f C)" % tpx["e3l_levels"][-1], "zero_power": False,
         "amb": "+%.0f C (REQ-024)" % env["in_use"]["max"], "dur": "4 h at the level (E3-L)", "cfg": "deployed closed-lid, the heat stage, pack fitted, discharging",
         "limit": "discharge -10 to %.0f C at the cell surface (35E Ver. 1.1 3.12); the +%.0f C abort" % (lim["discharge"][1], tpx["abort"]), "power": "the pack",
         "gap": "%.2f K at the bound's worst corner (%.2f C); none on 32.53's conductance (%.2f C)" % (a["cell_closed_W4_pack"] - lim["discharge"][1], a["cell_closed_W4_pack"], a["cell_closed_3253_pack"]),
         "approaches": ["the heat is the kit's own, so moving it out works: the enclosure's conductance decides (3a: %.3f W/K for the complete pass line)" % gv[4],
                        "the coupling to the skin (3b) lowers the cells only; the inside air's criteria stay the enclosure's",
                        "a path to the face plate: the block sits on the floor under board B and the plate above it, and the plate, the air's main exit, runs near that air (INFERRED from 32.53's split): no gain",
                        "a lower heat stage: its 23 W carries REQ-052's required set"],
         "result": "CREDIBLE, CONDITIONAL on T-H1 (3a)"},
        {"id": "C02", "lo": "LO-01a", "cond": "on shore at the hot edge, the pack idle at the inside air (E3-L's second half, E3-A's 2 h on shore, E5-A)", "zero_power": False,
         "amb": "+%.0f C" % env["in_use"]["max"], "dur": "E3-A %.0f h on the pack then %.0f h on shore; E5-A %s" % (tpx["e3a"][1], tpx["e3a"][2], tp["E5-A"]),
         "cfg": "deployed, lid open (E3-A, E5-A) or closed (E3-L), pack fitted, idle",
         "limit": "+%.0f C, the idle pack's limit as REQ-046's note and REQ-077 read it" % lim["discharge"][1], "power": "the input",
         "gap": "lid closed %.2f K; lid open at the bound's lowest the air on shore reaches %.2f C and the cells on the pack %.2f C" % (a["air_closed_W4"] - lim["discharge"][1], ow["air_shore"], ow["cell_pack"]),
         "approaches": ["as C01, with the front end's loss on shore counted (3a)"], "result": "CREDIBLE, CONDITIONAL on T-H1 (3a), both lid states"},
        {"id": "C03", "lo": "LO-01a", "cond": "E3-A's +%.0f C point, %.0f h, three loaded modules on shore (D-02b's charge point)" % (tpx["e3a"][3], tpx["e3a"][4]), "zero_power": False,
         "amb": "+%.0f C" % tpx["e3a"][3], "dur": "%.0f h" % tpx["e3a"][4], "cfg": "deployed, lid open, on shore, the stage C1 selects",
         "limit": "+%.0f C; no charge start above T3 %.0f C" % (lim["discharge"][1], 42.0), "power": "the input",
         "gap": "none for the cells: C1 sheds on measured temperatures; whether a charge starts is recorded (the charge ceiling of three loaded modules lies below +25 C, LO-01c)",
         "approaches": ["none needed"], "result": "NO GAP (recorded, not judged on charging)"},
        {"id": "C04", "lo": "LO-01a", "cond": "E3-L's lower levels (%s)" % ", ".join("+%.0f C" % t for t in tpx["e3l_levels"][:-1]), "zero_power": False,
         "amb": ", ".join("+%.0f C" % t for t in tpx["e3l_levels"][:-1]), "dur": "4 h each, on the pack then on shore", "cfg": "deployed closed-lid, the reduced mode or its heat stage",
         "limit": "+%.0f C; the SGP41's +%.0f C air" % (lim["discharge"][1], tpx["sgp41"]), "power": "the pack, then the input",
         "gap": "none at the bound's worst corner: " + "; ".join("+%.0f C %s, cells %.2f C" % (t, v[0], v[2]) for t, v in sorted(R["e3l_levels"].items()) if t < tpx["e3l_levels"][-1]),
         "approaches": ["none needed"], "result": "NO GAP"},
        {"id": "C05", "lo": "LO-01a", "cond": "E3-H's stepped run beyond the envelope (a protection test)", "zero_power": False,
         "amb": "from +%.0f C by %.0f K an hour to at most +%.0f C" % tpx["e3h"], "dur": "until H1 and then H2 have acted", "cfg": "lid closed, the heat stage, pack fitted, on shore then on the pack",
         "limit": "no cell at +%.0f C before H1 and H2 act; no permanent protection" % tpx["abort"], "power": "the input, then the pack",
         "gap": "none for the cells: past H2 the kit's heat stops and the cells approach the chamber's at most +%.0f C (quasi-static at 2 K an hour against time constants of hours, INFERRED); whether H2 is reached depends on the minimum load's heat, not modelled (P15 forces it)" % tpx["e3h"][2],
         "approaches": ["the hot stop itself"], "result": "NO GAP for the cells; a step not reached reads NOT_VERIFIED (TEST-PLAN)"},
        {"id": "C06", "lo": "LO-01b", "cond": "discharge in use at the cold edge, once warm (E4-O)", "zero_power": False,
         "amb": "%.0f C" % env["in_use"]["min"], "dur": "%.0f h" % tp["E4-O"][0], "cfg": "deployed, pack fitted, heater active, started warm or on an input",
         "limit": "discharge floor %.0f C" % lim["discharge"][0], "power": "the pack, or the input",
         "gap": "none: cells %.2f C on the highest conductance" % R["b"]["cell"], "approaches": ["none needed"], "result": "NO GAP"},
        {"id": "C07", "lo": None, "cond": "a start from a pack cold-soaked below about -10 C", "zero_power": False,
         "amb": "below about -10 C at the cells", "dur": "the start", "cfg": "pack fitted", "limit": "discharge floor %.0f C" % lim["discharge"][0],
         "power": "shore or vehicle input, or warming", "gap": "out of scope by the owner's D-02d", "approaches": ["no requirement: D-02d"], "result": "NOT REQUIRED (D-02d)"},
        {"id": "C08", "lo": "LO-01c", "cond": "charging in use, hot", "zero_power": False,
         "amb": "-20 to +40 C", "dur": "a mission", "cfg": "deployed, pack fitted, charging", "limit": "charge %.0f to %.0f C at the cell surface; T3 42 C" % lim["charge"],
         "power": "the input", "gap": "none by requirement: held off outside the window (reached at %.1f to +%.1f C ambient)" % (R["c"]["reach_lo"], R["c"]["reach_hi"]),
         "approaches": ["none needed; D-02b's accepted consequence"], "result": "NO GAP"},
        {"id": "C09", "lo": "LO-01c", "cond": "charging in use, cold (the mat before charge, REQ-046)", "zero_power": False,
         "amb": "%.0f C" % env["in_use"]["min"], "dur": "the warm-up, then the charge", "cfg": "deployed, pack fitted, on an input",
         "limit": "charge from %.0f C; UTC %.1f C, the panel's +%.0f C hold" % (lim["charge"][0], R["ladder"]["UTC"], R["cchg"]["hold"]),
         "power": "the input (the mat %.1f W into the cells, %.1f W regulator loss into the air)" % R["mat_split"],
         "gap": "the mat lifts the idle cells to %.2f C" % R["cchg"]["base"][1],
         "approaches": ["powered heating with a source present and the existing hold-then-warm start; its use is on the input"], "result": "CREDIBLE: the existing mat (3d)"},
        {"id": "C10", "lo": "LO-01d", "cond": "D-02a's +%.0f C operating margin (E3-O)" % d["amb"], "zero_power": False,
         "amb": "+%.0f C" % d["amb"], "dur": "%.0f h" % d["hours"], "cfg": "deployed, monitor and radios on, on shore or vehicle input, pack fitted (FEA-008)",
         "limit": "+%.0f C (surface and the idle pack); H1 at a reading of +%.1f C; E3-O's 'no shutdown'" % (lim["discharge"][1], hot["H1"]), "power": "the input",
         "gap": "%.2f to %.2f K" % G2["LO-01d"],
         "approaches": [fans + "; the cells may sit %.0f K over +%.0f C against a %.2f to %.2f K rise" % (lim["discharge"][1] - d["amb"], d["amb"], d["rise_lo"], d["rise_hi"]),
                        "insulation: no hold over %.0f s (time constant %.0f to %.0f s), and in steady state %.1f to %.1f mm at k %.2f W/mK against 0.77 to 2.66 mm: rejected" % (H["e3o_s"], H["tau_pack_s"][0], H["tau_pack_s"][1], R["meas"]["ins_mm"][0], R["meas"]["ins_mm"][1], K_INS),
                        "the coupling: the cells pass H1's reading at every corner (%.2f C at the best): the hot stop stops every module: rejected" % R["meas"]["d_best"][1],
                        "powered cooling on the input: cold side %.2f to %.2f W; INCONCLUSIVE (3i)" % co["E3-O"]["qc"],
                        "a cell route with its protection redesign: INCONCLUSIVE (section 4)"],
         "result": "OPEN: passive design rejected; cooling and a cell INCONCLUSIVE on named inputs"},
        {"id": "C11", "lo": "LO-01e", "cond": "E5's humid cycle (SC-03 margin)", "zero_power": False,
         "amb": "%.0f to %.0f C at %.0f %% RH" % (e["lo"], e["amb"], e["rh"]), "dur": "%.0f cycles of %.0f h (dwell and ramps not stated)" % (e["cycles"], e["hours"]),
         "cfg": "deployed, logging, on shore or vehicle input, pack fitted (FEA-008)", "limit": "+%.0f C" % lim["discharge"][1], "power": "the input",
         "gap": "at least %.2f K at the +%.0f C dwell" % (G2["LO-01e"], e["amb"]),
         "approaches": [fans, "insulation or thermal storage over the cycle: INCONCLUSIVE on the profile (3h)",
                        "powered cooling: cold side %.2f to %.2f W; INCONCLUSIVE (3i)" % co["E5"]["qc"], "a cell route: INCONCLUSIVE (section 4)"],
         "result": "OPEN: every route INCONCLUSIVE on named inputs"},
        {"id": "C12", "lo": "LO-01f", "cond": "D-02a's +%.0f C storage margin (E3-S)" % R["f"]["amb"], "zero_power": True,
         "amb": "+%.0f C" % R["f"]["amb"], "dur": "%.0f h" % R["f"]["hours"], "cfg": "stored: closed, latched, every input unplugged, pack fitted at %s in its gauge's shutdown (REQ-025, SC-19)" % lim["soc"],
         "limit": "storage 1 month %.0f to %.0f C at %s (35E Ver. 1.1 3.13)" % (lim["st_1m"][0], lim["st_1m"][1], lim["soc"]),
         "power": "zero from the inputs and the stored pack (its FETs off); a separate source only if one is added",
         "gap": "%.0f K: the ambient alone exceeds the limit" % G2["LO-01f"],
         "approaches": ["fans and spreading: no power and no colder sink",
                        "passive insulation or storage for the 24 h: %.1f mm needed against 2.66 mm (3f): rejected within D-06's pocket" % pas["LO-01f"]["ins_mm"],
                        "powered cooling from a separate source: %.0f to %.0f Wh over 24 h; INCONCLUSIVE (3i)" % (co["E3-S"]["Wh"][1.0][0], co["E3-S"]["Wh"][0.5][1]),
                        "a cell route: INCONCLUSIVE (section 4)"],
         "result": "OPEN: zero-power design rejected; cooling and a cell INCONCLUSIVE"},
        {"id": "C13", "lo": "LO-01g", "cond": "D-02a's %.0f C storage margin (E4-S)" % R["g"]["amb"], "zero_power": True,
         "amb": "%.0f C" % R["g"]["amb"], "dur": "%.0f h" % R["g"]["hours"], "cfg": "stored, as C12",
         "limit": "storage floor %.0f C (Ver. 1.1); %.0f C (Version 1.0); discharge floor %.0f C" % (lim["st_1m"][0], S["35E_10"]["st_1m"][0], lim["discharge"][0]),
         "power": "zero from the inputs and the stored pack; a separate primary source only if one is added",
         "gap": "%.0f K (Ver. 1.1); %.0f K (Version 1.0)" % G2["LO-01g"],
         "approaches": ["passive insulation or storage: %.1f mm needed (3f): rejected within D-06's pocket" % pas["LO-01g"]["ins_mm"],
                        "a heater fed by the pack (case i): the discharge window applies, its FETs are off in shutdown, and the stored charge buys %.1f to %.1f h of the 24 h (3g): rejected within REQ-025" % sh["dur_h_range"],
                        "a heater fed by a separate primary source at the storage floor (case i): %.1f to %.1f Wh direct plus %.2f to %.2f Wh per K of margin (3g); INCONCLUSIVE on named unknowns" % (sh["rows"]["slow"]["Wh_prim_direct"], sh["rows"]["fast"]["Wh_prim_direct"], sh["rows"]["slow"]["Wh_per_K"], sh["rows"]["fast"]["Wh_per_K"]),
                        "a pack already cold-soaked (case ii): not recovered by any heater below -20 C; the pack cannot feed one below -10 C",
                        "heating lost (case iii): past the floor %.2f to %.2f h after a pack-fed hold, at once for a hold at the floor (3g)" % (sh["rows"]["fast"]["t_lost_pack_h"], sh["rows"]["slow"]["t_lost_pack_h"]),
                        "a cell route: INCONCLUSIVE (section 4)"],
         "result": "OPEN: a separately fed heater INCONCLUSIVE on named unknowns"},
        {"id": "C14", "lo": "LO-01h", "cond": "storage inside the envelope", "zero_power": True,
         "amb": "%.0f to +%.0f C; %.0f to +%.0f C" % (env["storage_3_months"]["min"], env["storage_3_months"]["max"], env["storage_1_year"]["min"], env["storage_1_year"]["max"]),
         "dur": "three months; a year", "cfg": "stored, as C12", "limit": "Ver. 1.1: 3 months %.0f to %.0f C, 1 year %.0f to %.0f C at %s" % (lim["st_3m"] + lim["st_1y"] + (lim["soc"],)),
         "power": "zero", "gap": "none on Ver. 1.1; %.0f K and %.0f K on Version 1.0" % G2["LO-01h"],
         "approaches": ["procurement of a lot governed by Ver. 1.1 (BAT-F09)"], "result": "CREDIBLE: procurement (no thermal measure)"},
        {"id": "C15", "lo": None, "cond": "E3-T, the stored and transport soaks at the cells' own limit (REQ-074)", "zero_power": True,
         "amb": "+%.0f C set point, +-2 K" % tp["E3-T"], "dur": "24 h", "cfg": "closed, latched, kit off, pack fitted in shutdown; at the ex-factory state (storage) and at its charge (transport)",
         "limit": "storage 1 month to %.0f C at %s (3.13); at full charge, the maker's %.0f days at %.0f C with at least %s mAh (%.0f %%) recovered (MAKER 7.10)" % (lim["st_1m"][1], lim["soc"], fs["days"], fs["t"], fs["mah"], fs["pct"]),
         "power": "zero", "gap": "none: the set point's top tolerance reaches the limit, not past it", "approaches": ["none needed"], "result": "NO GAP"},
        {"id": "C16", "lo": None, "cond": "E4-T, the stored and transport cold soak", "zero_power": True,
         "amb": tp["E4-T"], "dur": "24 h", "cfg": "closed, latched, kit off, pack fitted in shutdown",
         "limit": "storage floor %.0f C (Ver. 1.1) at %s; F2's operating floor %.0f C" % (lim["st_1m"][0], lim["soc"], S["F2"]["operating"][0]),
         "power": "zero", "gap": "none for the cells at the ex-factory state; F2's storage line (-10 C) open with Eaton", "approaches": ["none needed"], "result": "NO GAP for the cells"},
        {"id": "C17", "lo": None, "cond": "E3-P, the pack alone, armed, at full charge, then discharged from +%.0f C" % tpx["e3p"][0], "zero_power": False,
         "amb": "+%.0f C set point, +-%.0f K" % (tpx["e3p"][0], tpx["e3p"][1]), "dur": "%.0f h, then a %.0f A discharge until the gauge stops it" % (tpx["e3p"][2], tpx["e3p"][3]),
         "cfg": "the pack alone, JP1 closed, full charge",
         "limit": "at full charge the maker's %.0f days at %.0f C (MAKER 7.10); discharge to %.0f C; F2 %.0f C" % (fs["days"], fs["t"], lim["discharge"][1], S["F2"]["operating"][1]),
         "power": "the pack (the test load)",
         "gap": "none by construction: the soak sits at the limits; the discharge starts at or above OTD's %.1f C reading, so the gauge refuses it within its delay (the pass line)" % R["ladder"]["OTD"],
         "approaches": ["none needed"], "result": "NO GAP (a protection test at the limits)"},
        {"id": "C18", "lo": None, "cond": "E4-P, the pack alone at its cold storage limit", "zero_power": True,
         "amb": "as E4-T (%s)" % tp["E4-T"], "dur": "24 h", "cfg": "the pack alone (%s)" % ("as E4-T" if tpx["e4p"] else "not stated"),
         "limit": "storage floor %.0f C at %s; no cold-storage recovery figure published (PROVISIONAL pass line)" % (lim["st_1m"][0], lim["soc"]),
         "power": "zero", "gap": "none for the cells at the ex-factory state; another charge state is not in the sheet", "approaches": ["none needed"], "result": "NO GAP at the ex-factory state"},
        {"id": "C19", "lo": None, "cond": "P13, F2 at temperature: %.0f A for %.0f s from +%.0f C, and %.0f A for %.0f h at the pack's hot limit" % (tpx["p13_kd"][1], tpx["p13_kd"][2], tpx["p13_kd"][0], tpx["p13_a"], tpx["p13_h"]), "zero_power": False,
         "amb": "+%.0f C block; the pack's hot limit" % tpx["p13_kd"][0], "dur": "%.0f s; %.0f h" % (tpx["p13_kd"][2], tpx["p13_h"]), "cfg": "a block on the bench, a thermocouple on F2's body",
         "limit": "+%.0f C at the cells and at F2's body" % lim["discharge"][1], "power": "the test load",
         "gap": "the key-down: none for the cells (%.2f to %.2f C); the hour: the cells' own %.2f to %.2f W rise them %.1f to %.1f K over the block's air, so 'at the hot limit' must mean the cell surface (3k)" % (R["kd"]["to"] + R["p13"]["w"] + R["p13"]["steady"]),
         "approaches": ["a definition item for P13's owner; F2's body is the measurement"], "result": "NO GAP for the cells if the limit is held at the cell surface; F2 open"},
    ]
    return rows


def shortlist_lines(R):
    c, sh, pas = R["cand"], R["selfheat"], R["passive"]
    return [
        "A1 the 35E as ruled with local thermal management (SELECTED): the enclosure's conductance for LO-01a (3a), the coupling for the cells only (3b), a heater fed by a",
        "   separate primary source for LO-01g (3g), powered cooling for the hot margins (3i). Constraints kept: D-06's pack and pocket, the sealed case, REQ-025's stored state.",
        "   Adds parts (a primary source, a thermostat, a cooler) whose purchase is the owner's spend at purchase time; research needs none. Energy unchanged (%.1f Wh usable)." % c["35E"]["usable_wh"],
        "A2 a compatible alternative cell in D-06's 4S3P (S2, S3 of section 4) with the protection and control redesign: changes the cell D-06 names, so its spend and D-06's",
        "   parenthesis are the owner's (cell_provenance); %.1f %% to %.1f %% less usable energy; S2 moves no margin row, S3 rests on a page." % (
            -100.0 * (c["30Q6"]["usable_wh"] / c["35E"]["usable_wh"] - 1.0), -100.0 * (c["HL18650V"]["usable_wh"] / c["35E"]["usable_wh"] - 1.0)),
        "A3 another thermal arrangement, an insulated pack enclosure for the storage margins: %.1f to %.1f mm at k %.2f W/mK (3f) cannot sit in D-06's shrink-wrapped pocket, so it" % (
            pas["LO-01f"]["ins_mm"], pas["LO-01g"]["ins_mm"], K_INS),
        "   changes an approved constraint (D-06's pack in the east pocket); not selected while A1's routes stand. A heater fed by the pack would change REQ-025's stored state likewise.",
    ]


def later_lines(R):
    c = R["cand"]
    return [
        "A. (a requirement change) the four margin levels shown with the pack out of the exposure, as REQ-074 and REQ-051's deviations already run them: no spend, no energy lost;",
        "   the kit not claimed at those levels with its own pack. Reserved to the owner by D-29; not proposed, because routes remain open.",
        "B. (a resource change) a wide-temperature 18650 inside D-06's 4S3P: its maker's signed specification (the request is drafted), the protection and control redesign (section 4),",
        "   about USD %.2f a pack of 12 cells, %.1f Wh nominal against %.1f (%.1f %% less usable), D-06's 'about 145 Wh' restated: spend and D-06 need the owner's approval (cell_provenance)."
        % (12 * R["price_hl"], c["HL18650V"]["wh_nom"], c["35E"]["wh_nom"], -100.0 * (c["HL18650V"]["usable_wh"] / c["35E"]["usable_wh"] - 1.0)),
        "C. (the existing state) FEA-008 open as the session's engineering obligation, a release gate on those rows; no ruling is needed for it.",
    ]


def downstream_lines(R):
    gv = R["gov"]["all"]
    return [
        "Session (layer 4, this obligation): the routes left INCONCLUSIVE: E5's profile (TEST-PLAN's owner), the primary-source self-heating parts for LO-01g, a cooler's sheet, the",
        "   input's spare power, Samsung's reading of the 30Q6's ambient clause and the HL18650V's specification (drafts in clarification/). Acceptance: each route bounded or rejected.",
        "Layer 6 (components): the 35E lot's specification revision on the purchase record (Ver. 1.1; BAT-F09) closes LO-01h; F2's storage line and operation above +60 C (Eaton, Q-E2 extended);",
        "   for any cell route, the protection and control redesign of section 4. Acceptance: the documents filed and read, the redesign's bounds computed.",
        "Layer 7 (mechanical): the coupling (3b) for the cells only if T-H1 reads under %.3f W/K with the fans; a primary source's place for LO-01g if that route is pursued. Acceptance: E3-L, E4-S." % gv[4],
        "Layer 8 (generator owners): none now; under a cell route, gen_sch_p.py (U2, F2) and pcb_pack_protection.yaml re-derived. Acceptance: the protection suite.",
        "Layer 9 (pre-layout analysis): board P's place against the block (F2 at the air passes +60 C at LO-01a's worst corner) and the thermistors on the hottest cells. Acceptance: P13, P14.",
        "Prototype bench: T-H1 in both lid states with the dummy pack block (at least %.3f W/K for the complete pass line); E3-A, E3-L, E3-H with a thermocouple on every cell; E4-O; P13" % gv[4],
        "   at the cell surface; P14; P15. Acceptance: each run's TEST-PLAN pass line; the thresholds of 3a replaced by the measured conductance.",
        "Firmware owner: only with the coupling, the mat's thermostat on battery at the cold end (3c); with a self-heating store, a thermostat independent of the gauge (3g).",
        "Board B's owner: BANK-R1 in gen_sch_b.py, without which E3-L's stage criteria fail at every level that enters the heat stage.",
        "Owner: no decision is asked now (section 5).",
    ]


def predicates(R):
    dec, modes = R["dec"], R["modes"]
    p = {}
    p["P1 every LO row has a decision"] = sorted(dec) == sorted(modes)
    p["P2 a closed or no-collision row rests on MAKER or bounded MODELED evidence only"] = all(
        set(d["evidence"]) <= {"MAKER", "MODELED"} and d["bounded"] for d in dec.values() if d["decision"] in ("CLOSED", "NO_COLLISION"))
    p["P3 no cell change is taken"] = all(d["cell_change"] is None or (d["cell_change"]["taken"] is False and d["cell_change"]["owner_approval_required"]) for d in dec.values())
    p["P4 the screen covers every LO row"] = set(r["lo"] for r in R["screen"] if r["lo"]) == set(modes)
    p["P5 zero-power rows name their power and credit no unpowered active means"] = all(r["power"].startswith("zero") for r in R["screen"] if r["zero_power"])
    p["P6 storage margins: the hold time is shorter than the exposure"] = R["hold"]["tau_kit_s"][1] * 3 < R["f"]["hours"] * 3600.0
    p["P7 an owner decision is recorded only where every route of a row is rejected"] = R["owner_decision_required"] == bool(R["forced_rows"])
    p["P8 the collisions reproduce Layer 3's table"] = all(v[2] for v in R["agree"].values())
    p["P9 every decision is a known kind"] = all(d["decision"] in ("CLOSED", "CONDITIONAL", "NO_COLLISION", "OPEN") for d in dec.values())
    p["P10 every open row has a route not rejected"] = all(any(r["status"] != "REJECTED" for r in d["routes"]) for d in dec.values() if d["decision"] == "OPEN")
    p["P11 LO-01a's complete threshold is at least FEA-008's and the rating's"] = R["gov"]["all"][4] >= R["gov"]["fea008_pack"] >= R["gov"]["rating_pack"]
    p["P12 the screen maps every TEST-PLAN exposure of sections 6 and 7 it covers"] = all(any(t in (r["cond"] + r["dur"]) for r in R["screen"]) for t in ("E3-A", "E3-L", "E3-H", "E3-O", "E3-S", "E3-T", "E3-P", "E4-O", "E4-S", "E4-T", "E4-P", "E5", "P13"))
    return p


def main():
    R = compute()
    sys.stdout.write("\n".join(render(R)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
