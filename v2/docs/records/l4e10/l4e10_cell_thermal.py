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
}

# The few figures this record sets itself (ASSUMPTION; each is used in one place and its effect is printed):
K_PAD = 1.0          # W/mK, a gap filler between the pack's east face and the east wall (no maker's sheet held; low end)
T_MAT = 0.0015       # m, the RS PRO heater mat's thickness (its sheet states none)
K_MAT = 0.2          # W/mK, the mat's silicone (its sheet states none)
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
    S["U2"] = {"doc": "TI BQ77207 (SLUSEG7D), %s" % BQ77207, "ot": ot}
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
    R["ladder"]["U2_trip_lo"] = float(need(tc, r"BQ7720700 OT, fixed 70 C .*?\| (\d+\.\d) to (\d+\.\d) C at the network", "U2 trip").group(1))
    R["hot"] = {"budget": hot.BUDGET_K, "C1": hot.C1_CELL_C, "H1": hot.H1_C, "H2": hot.H2_C, "OTD": hot.OTD_C, "release": hot.RELEASE_C}
    R["heat_reg"] = red2.HEAT_REG[1]

    # ======================================================== 1: the collisions restated from their sources
    G, G32, GB = pb.G, pb.G_3253, pb.G_BLK

    def heat_red(ov):
        _, q, p = red2.heat(ov, "plan")
        return q, p

    qR, pR = heat_red(red2.SURVR)
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
    # 3a: LO-01a's break-even lid-closed conductance (fans on), on the pack (worst block film) and on an input
    gblk = GB[0]
    gstar = {}
    for lab, lim_c in (("cell limit", lim["discharge"][1]), ("H1 reading", R["hot"]["H1"])):
        gstar[lab] = {"pack": (qR + pR) / (lim_c - t_use - pR / gblk), "input": qR / (lim_c - t_use)}
    R["gstar"] = gstar
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
    # sensitivity of the worst corner to the pad's assumed conductivity (1 to 3 W/mK)
    R["pad_sens"] = (1.0 / (t_pad / (3.0 * A_E) + tk / A_E + 1.0 / (w4["H_OUT_WALL"][0] * A_E))) - g_east(w4["H_OUT_WALL"][0])

    def two_node(t0, q, p, g_encl, g_in, g_amb, p_h=0.0):
        """Inside air and cells (C): air couples to ambient by g_encl and to the pack by g_in; the pack to ambient by g_amb."""
        pc = p + p_h
        det = (g_encl + g_in) * (g_in + g_amb) - g_in * g_in
        air = (q * (g_in + g_amb) + g_in * pc) / det
        cell = ((g_encl + g_in) * pc + g_in * q) / det
        return t0 + air, t0 + cell

    R["two_node"] = two_node
    meas = {}
    meas["a_pack_worst"] = two_node(t_use, qR, pR, G["closed_fans"][0] - worst["dg"], worst["g_in"], worst["g_amb"])
    meas["a_pack_best"] = two_node(t_use, qR, pR, G["closed_fans"][0] - best["dg"], best["g_in"], best["g_amb"])
    meas["a_input_worst"] = two_node(t_use, qR, 0.0, G["closed_fans"][0] - worst["dg"], worst["g_in"], worst["g_amb"])
    meas["a_base_pack"] = two_node(t_use, qR, pR, G["closed_fans"][0], gblk, 0.0)
    meas["d_worst"] = two_node(e3o_t, qR, pR, G["open_fans"][0] - worst["dg"], worst["g_in"], worst["g_amb"])
    meas["d_best"] = two_node(e3o_t, qS, pS, G32["open_fans"][1] - best["dg"], best["g_in"], best["g_amb"])
    meas["e_best"] = two_node(hi5, qS, 0.0, G32["open_fans"][1] - best["dg"], best["g_in"], best["g_amb"])
    # the f the +55 C margin would need (cells at the limit, and at H1's reading), against the best f the measure gives
    meas["d_f_needed"] = ((lim["discharge"][1] - e3o_t) / R["d"]["rise_hi"], (lim["discharge"][1] - e3o_t) / R["d"]["rise_lo"],
                          (R["hot"]["H1"] - e3o_t) / R["d"]["rise_hi"], (R["hot"]["H1"] - e3o_t) / R["d"]["rise_lo"])
    # the insulation the +55 C margin would need on the four inside faces to reach the f the +60 C limit asks at the worst corner
    f_need = meas["d_f_needed"][0]
    ins = []
    for ga in (worst["g_amb"], best["g_amb"]):
        g_in_max = f_need / (1.0 - f_need) * ga
        r_add = 1.0 / g_in_max - 1.0 / (hb_lo * A_in)
        ins.append(r_add * A_in * K_INS * 1000.0)
    meas["ins_mm"] = (min(ins), max(ins))
    meas["two_node_matches_record"] = abs(meas["a_base_pack"][1] - a["cell_closed_W4_pack"]) < 1e-9
    R["meas"] = meas
    R["worst"], R["best"] = worst, best
    R["areas"] = (A_E, A_B, A_in)
    # 3c: the cold end with the measure (LO-01b), PS-IDLE-SPEC on the pack, lid open, at -20 C, highest conductances
    gc = G32["open_fans"][1]
    cold_base = two_node(t_cold, qI, pI, gc, GB[1], 0.0)
    corners = [(gi, ga) for gi in (worst["g_in"], best["g_in"]) for ga in (worst["g_amb"], best["g_amb"])]
    cold_meas = min((two_node(t_cold, qI, pI, gc - best["dg"], gi, ga) for gi, ga in corners), key=lambda t: t[1])
    if abs(cold_meas[1] - two_node(t_cold, qI, pI, gc - best["dg"], best["g_in"], best["g_amb"])[1]) > 1e-12:
        refuse(4, "the coldest corner of the coupled block is not the one the heater duty is sized on")
    cold_meas_w4 = two_node(t_cold, qI, pI, G["open_fans"][1] - best["dg"], best["g_in"], best["g_amb"])
    target = R["ladder"]["UTD"] + 1.0     # 1 K above the gauge's UTD reading, so the stop does not act (INFERRED margin)
    det = (gc - best["dg"] + best["g_in"]) * (best["g_in"] + best["g_amb"]) - best["g_in"] ** 2
    p_h = max(0.0, ((target - t_cold) * det - best["g_in"] * qI) / (gc - best["dg"] + best["g_in"]) - pI)
    R["cold"] = {"base": cold_base, "meas": cold_meas, "meas_w4": cold_meas_w4, "target": target, "p_h": p_h,
                 "w": R["heat"]["w_idlespec"]}
    # 3d: charging at the cold end on an input: the regulated mat (pwr_red2's HEAT_REG) into the block, the pack idle
    pmat = R["heat_reg"]
    corners = [(gi, ga) for gi in (worst["g_in"], best["g_in"]) for ga in (worst["g_amb"], best["g_amb"])]
    R["cchg"] = {"base": two_node(t_cold, qI, 0.0, gc, GB[1], 0.0, pmat),
                 "meas": min((two_node(t_cold, qI, 0.0, gc - best["dg"], gi, ga, pmat) for gi, ga in corners), key=lambda t: t[1]),
                 "floor": R["ladder"]["UTC"], "hold": 3.0}
    hold_src = need(text(TC), r"panel and bridge hold on charge below \+(\d) C", "the panel's charge hold").group(1)
    R["cchg"]["hold"] = float(hold_src)
    # 3e: hold times
    taus_pack = (R["blk"]["C"][0] / GB[1], R["blk"]["C"][1] / GB[0])
    taus_pack_meas = (R["blk"]["C"][0] / (worst["g_in"] + worst["g_amb"]), R["blk"]["C"][1] / (best["g_in"] + best["g_amb"]))
    gcs = G["closed_still"]
    taus_kit = (R["C_kit"][0] / gcs[1], R["C_kit"][1] / gcs[0])
    day = 24 * 3600.0
    st_env = R["env"]
    step_hot = e3s_t - st_env["storage_3_months"]["min"]       # the most favourable start: the storage envelope's cold edge
    step_cold = st_env["storage_3_months"]["max"] - e4s_t
    R["hold"] = {"tau_pack_s": taus_pack, "tau_pack_meas_s": taus_pack_meas, "tau_kit_s": taus_kit,
                 "resid_hot": step_hot * math.exp(-e3s_h * 3600.0 / taus_kit[1]), "resid_cold": step_cold * math.exp(-e4s_h * 3600.0 / taus_kit[1]),
                 "step_hot": step_hot, "step_cold": step_cold,
                 "e_hold_hot_Wh": tuple(g * gaps["LO-01f"] * e3s_h for g in gcs), "e_hold_cold_Wh": tuple(g * gaps["LO-01g"][0] * e4s_h for g in gcs),
                 "pack_Wh_nom": 12 * lim["c_min"] * pb.V_NOM, "e3o_s": e3o_h * 3600.0}
    # 3f: PWR-F12, an 18 A key-down of 60 s from a cell at K2's +55 C gate (the cells' adiabatic rise)
    i_cell = pb.I_PEAK / 3.0
    q_kd = [12 * i_cell ** 2 * r * 60.0 for r in (pb.R_CELL["lo"], pb.R_CELL["hi"])]
    kd = (q_kd[0] / R["blk"]["C"][1], q_kd[1] / R["blk"]["C"][0])
    k2 = float(need(pt, r"K2 keeps it from keying above \+(\d+) C", "K2's flange gate").group(1))
    R["kd"] = {"i_cell": i_cell, "rise": kd, "from": R["hot"]["C1"], "to": (R["hot"]["C1"] + kd[0], R["hot"]["C1"] + kd[1]), "k2_flange": k2}

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

    # ======================================================== 5: decisions
    dec = {}
    dec["LO-01a"] = {"decision": "CONDITIONAL", "route": "thermal design and verification",
                     "evidence": ["MAKER", "MODELED", "INFERRED", "ASSUMPTION"], "bounded": True, "cell_change": None,
                     "basis": "no collision on appendix 32.53's conductance; at the independent bound's worst corner it closes once the measured lid-closed fan-on conductance is at least the break-even of section 3a, or, below it, with the pocket coupling measure of section 3b (MODELED on INFERRED film coefficients and two ASSUMPTION figures)",
                     "verify": "TEST-PLAN T-H1 (the dummy pack block's thermocouples, lid closed with fans), then E3-L and E3-H with the pack fitted at +40 C, a thermocouple on every cell"}
    dec["LO-01b"] = {"decision": "NO_COLLISION", "route": "none needed", "evidence": ["MAKER", "MODELED"], "bounded": True, "cell_change": None,
                     "basis": "the running rise keeps the cells above -10 C (section 1); if the coupling measure is ever fitted, the mat holds them at a duty of section 3c",
                     "verify": "E4-O with the pack fitted"}
    dec["LO-01c"] = {"decision": "NO_COLLISION", "route": "none needed", "evidence": ["MAKER", "MODELED"], "bounded": True, "cell_change": None,
                     "basis": "no requirement asks the kit to charge outside the window; it holds the charge off (REQ-046, D-02b); at the cold end the mat on input power brings the cells into the window (section 3d)",
                     "verify": "E3-A's T3 line and E4-O's charge floor"}
    for k in ("LO-01d", "LO-01e", "LO-01f", "LO-01g"):
        dec[k] = {"decision": "NOT_CLOSABLE", "route": "the owner's decision (section 5)", "evidence": ["MAKER", "MODELED", "INFERRED"], "bounded": True,
                  "cell_change": {"candidate": "HL18650V class", "taken": False, "owner_approval_required": True},
                  "basis": "no thermal design within the rulings (section 2) and no held maker's specification of an 18650 cell rates the level; board P's F2 is outside its own range there as well",
                  "verify": "the owner's decision first; then the named TEST-PLAN run with the pack fitted, or as REQ-051's deviation"}
    dec["LO-01h"] = {"decision": "CONDITIONAL", "route": "procurement", "evidence": ["MAKER"], "bounded": True, "cell_change": None,
                     "basis": "Ver. 1.1 rates storage at -20 C for three months and +25 C for a year; Version 1.0 does not; the cells bought must be shown to follow Ver. 1.1",
                     "verify": "Layer 6: the purchase record names the specification revision of the lot (BAT-F09); E4-T at the governing floor"}
    R["dec"] = dec
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
    w("In-use (the envelope, operate to specification): LO-01a, LO-01b, LO-01c, LO-01h. Qualification margins (D-02a, SC-03; no damage and recovery): LO-01d, LO-01e, LO-01f, LO-01g.")
    w("")
    # ---------------------------------------------------------------- 2: the feasibility screen
    H, G2 = R["hold"], R["gaps"]
    tk = H["tau_kit_s"]
    tp_ = H["tau_pack_s"]
    w("== 2. THE FEASIBILITY SCREEN: every required charging, discharging, transport and storage condition (the owner's refinement of 2 October 2026)")
    w("Columns: condition | ambient, duration, configuration (source) | the governing MAKER limit | power for thermal control | gap | approaches judged | screen result")
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
    w("Hold times behind the rejections (INFERRED): the cells' own time constant in the pocket %.0f to %.0f s (%.2f to %.2f h; 480 to 660 J/K over the block's film);"
      % (tp_[0], tp_[1], tp_[0] / 3600.0, tp_[1] / 3600.0))
    w("   the closed, stopped kit %.0f to %.0f s (%.2f to %.2f h; 32.53's %.0f to %.0f kJ/K over the lid-closed still-air bound); after %.0f h from the most favourable start"
      % (tk[0], tk[1], tk[0] / 3600.0, tk[1] / 3600.0, R["C_kit"][0] / 1000.0, R["C_kit"][1] / 1000.0, R["f"]["hours"]))
    w("   (the storage envelope's far edge, steps of %.0f K and %.0f K) the cells lag the margin's ambient by at most %.2f K (hot) and %.2f K (cold): no hold"
      % (H["step_hot"], H["step_cold"], H["resid_hot"], H["resid_cold"]))
    w("   holding the cells at the limit for the 24 h instead would take %.0f to %.0f Wh (hot) and %.0f to %.0f Wh (cold) of heat moved, against the pack's %.1f Wh nominal and no power available"
      % (H["e_hold_hot_Wh"][0], H["e_hold_hot_Wh"][1], H["e_hold_cold_Wh"][0], H["e_hold_cold_Wh"][1], H["pack_Wh_nom"]))
    w("")
    # ---------------------------------------------------------------- 3: thermal measures, only where credible
    gs = R["gstar"]
    wo, be = R["worst"], R["best"]
    m = R["meas"]
    A_E, A_B, A_in = R["areas"]
    w("== 3. Thermal measures, quantified only where the screen found a credible route (LO-01a; the cold end they touch)")
    w("3a LO-01a's break-even lid-closed conductance with fans (MODELED, PS-SURV-R at PLAN heat, +%.0f C): the cells stay at or under" % R["env"]["in_use"]["max"])
    w("   +%.0f C on the pack from %.3f W/K and on an input from %.3f W/K; under H1's +%.1f C reading from %.3f W/K and %.3f W/K."
      % (lim["discharge"][1], gs["cell limit"]["pack"], gs["cell limit"]["input"], hot["H1"], gs["H1 reading"]["pack"], gs["H1 reading"]["input"]))
    w("   The record's bounds: independent %.2f to %.2f W/K, appendix 32.53 %.2f to %.2f W/K. Above the break-even the row needs no measure; T-H1 decides which side holds."
      % (1.06, 2.49, 1.5, 2.0))
    w("3b The pocket coupling measure (the fallback if T-H1 reads below the break-even): the block's east face (%.5f m2) against the east wall through a gap filler of the"
      % A_E)
    w("   pocket's widest gap (%.2f mm, CASE-MARGINS M4b; k %.1f W/mK, ASSUMPTION), its base (%.5f m2) on the floor through the heater mat (%.1f mm, k %.1f W/mK, ASSUMPTION: the mat's sheet states neither: %s);"
      % (R["m4b_gap_max_mm"], K_PAD, A_B, T_MAT * 1000.0, K_MAT, not S["mat"]["thickness_stated"]))
    w("   the other four faces (%.5f m2) stay in the inside air at the record's %.1f to %.1f W/m2K (pwr_budget's G_BLK). Wall and outside films from W4's bound (INFERRED):" % (A_in, R["blk"]["h"][0], R["blk"]["h"][1]))
    w("   coupling to ambient %.4f (worst) to %.4f W/K (best), to the inside air %.4f (worst) to %.4f W/K (best), so the cells follow the inside air's rise by f = %.3f (worst) to %.3f (best);"
      % (wo["g_amb"], be["g_amb"], wo["g_in"], be["g_in"], wo["f"], be["f"]))
    w("   the area the pack takes from the walls and floor lowers the enclosure's conductance by %.4f to %.4f W/K (counted). A 3 W/mK filler adds only %.4f W/K at the worst corner."
      % (wo["dg"], be["dg"], R["pad_sens"]))
    w("   LO-01a at +%.0f C, lid closed, the bound's lowest conductance: without the measure the cells reach %.2f C on the pack (two-node model reproduces pwr_budget: %.2f C);"
      % (R["env"]["in_use"]["max"], R["a"]["cell_closed_W4_pack"], m["a_base_pack"][1]))
    w("   with it %.2f C (worst) to %.2f C (best) on the pack, %.2f C on an input: inside +%.0f C by %.2f K at the worst corner; under H1's +%.1f C reading only at the best."
      % (m["a_pack_worst"][1], m["a_pack_best"][1], m["a_input_worst"][1], lim["discharge"][1], lim["discharge"][1] - m["a_pack_worst"][1], hot["H1"]))
    w("   The inside air there moves from %.2f C to %.2f C: the area the pack takes from the case skin is outweighed by the path through the pack (every other part moves with it)."
      % (R["a"]["air_closed_W4"], m["a_pack_worst"][0]))
    w("   The same measure at the +%.0f C margin (E3-O): cells %.2f C (worst) to %.2f C (best); the margin would need f at most %.3f to %.3f for +%.0f C and %.3f to %.3f for H1: REJECTED (best f %.3f)."
      % (d["amb"], m["d_worst"][1], m["d_best"][1], m["d_f_needed"][0], m["d_f_needed"][1], lim["discharge"][1], m["d_f_needed"][2], m["d_f_needed"][3], be["f"]))
    w("   At E5's +%.0f C the pack on an input, best case: %.2f C, past the +%.0f C limit: REJECTED." % (e["amb"], m["e_best"][1], lim["discharge"][1]))
    w("   Time constant of the coupled pack %.0f to %.0f s (INFERRED): a key-down's heat leaves it about as slowly as now (section 6)." % R["hold"]["tau_pack_meas_s"])
    w("   Placement: the block's top lies about %.2f mm under board B's underside (SHORTLIST's %.2f mm of room plus the 1.0 mm minimum, CASE-MARGINS M6); the model takes that face at the"
      % (R["room"]["height"] + 1.0, R["room"]["height"]))
    w("   inside air, and board B's underside has no local model (POWER-THERMAL.md 9.2): a hotter underside raises f. T-H1's dummy block carries a thermocouple on that face (INFERRED).")
    c = R["cold"]
    w("3c The cold end the measure touches (LO-01b; PS-IDLE-SPEC on the pack, lid open, -%.0f C, the highest conductance): cells %.2f C without the measure, %.2f C with it (%.2f C on W4's highest);"
      % (-R["env"]["in_use"]["min"], c["base"][1], c["meas"][1], c["meas_w4"][1]))
    w("   holding them at %.1f C (1 K above the gauge's UTD reading of %.1f C, INFERRED margin) takes the mat at %.2f W average on battery, %.1f %% of PS-IDLE-SPEC's %.2f W (MODELED; firmware owner)."
      % (c["target"], R["ladder"]["UTD"], c["p_h"], 100.0 * c["p_h"] / c["w"], c["w"]))
    cc = R["cchg"]
    w("3d Charging at the cold end (REQ-046: warmed by the mat before charge; the input is the power): at -%.0f C with the regulated %.1f W mat on input power, the pack idle, the cells reach"
      % (-R["env"]["in_use"]["min"], R["heat_reg"]))
    w("   %.2f C (record's model) and %.2f C (with the coupling measure): above the gauge's UTC %.1f C and the panel's +%.0f C hold: CREDIBLE, no new part (MODELED)."
      % (cc["base"][1], cc["meas"][1], cc["floor"], cc["hold"]))
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
    w("   S3's hot levels need U2's over-temperature moved off %.0f C (released variants %s) and the gauge's SOT (%.1f C) moved, and a fuse for F2's place rated beyond %.0f to +%.0f C (none held)."
      % (S["U2"]["ot"]["BQ7720700"], ", ".join("%s %.0f C" % (k, v) for k, v in sorted(S["U2"]["ot"].items())), R["ladder"]["SOT"], S["F2"]["operating"][0], S["F2"]["operating"][1]))
    w("Thermal-control burden: S1 none beyond the design (C1, the hot stop, the mat on input power; the coupling measure only below T-H1's break-even); S2 the same; S3 the same, its storage")
    w("   levels resting on the cell's own rating with no power. Evidence outstanding: S1 T-H1, E3-L, E3-H, the lot's revision; S2 those plus Samsung's reading of its ambient clause;")
    w("   S3 the maker's signed specification (none found; the page links none), the maker's identity behind the marketplace listings, F2's replacement, U2's variant, the gauge data.")
    w("")
    # ---------------------------------------------------------------- 5: decisions and the conflict
    w("== 5. The decision per row, the selection, and the conflict for the owner")
    for k in sorted(R["dec"]):
        dd = R["dec"][k]
        w("%s %s (%s; evidence %s): %s. Verification: %s." % (k, dd["decision"], dd["route"], "+".join(dd["evidence"]), dd["basis"], dd["verify"]))
    w("SELECTION: S1, the 35E as ruled, is the simplest defensible solution: it meets every in-use row (LO-01a CONDITIONAL on T-H1, LO-01h on the lot's revision) with no spend.")
    w("   S2 is not recommended: on its own sheet it moves no margin row (its ambient discharge and storage stop at +60 C), it fails LO-01h's year at +%.0f C against its %.0f C, and it costs %.1f %% of the energy."
      % (R["env"]["storage_1_year"]["max"], s6["st_1y"][1], -100.0 * (cand["30Q6"]["usable_wh"] / cand["35E"]["usable_wh"] - 1.0)))
    w("   S3 is the only lead that reaches LO-01d to LO-01g, on a product page and only with a new fuse for F2's place; it cannot be selected on held evidence.")
    w("NO OPTION QUALIFIES for LO-01d, LO-01e, LO-01f and LO-01g, so the screen stops here (the owner's refinement, item 3). THE CONFLICT, exactly:")
    for line in conflict_lines(R):
        w("   " + line)
    w("Options for the owner's decision (at most three; nothing is taken; no money is spent):")
    for line in option_lines(R):
        w("   " + line)
    w("")
    # ---------------------------------------------------------------- 6: the battery path's other thermal items
    F2 = S["F2"]
    kd = R["kd"]
    w("== 6. The battery path's other thermal items (PWR-F12, F2 and the protection temperatures)")
    w("F2 (MAKER, %s): operating %.0f to +%.0f C; '%s'; endurance lines '%s' and '%s' (test conditions, not a rating)."
      % (F2["doc"], F2["operating"][0], F2["operating"][1], F2["storage_line"], F2["hi_test"], F2["lo_test"]))
    w("   Board P sits beside the block in the pocket, so F2 is at about the inside air or the cells (INFERRED). F2 is past its operating range at: LO-01a's worst corner %s (%.2f C),"
      % (R["f2"]["LO-01a"], a["air_closed_W4"]))
    w("   LO-01d %s, LO-01e %s, LO-01f %s, LO-01g %s. Its storage line, if it covers a mounted part, also misses the storage envelope (cold %s, hot %s): Eaton's answer (Q-E2, extended here)."
      % (R["f2"]["LO-01d"], R["f2"]["LO-01e"], R["f2"]["LO-01f"], R["f2"]["LO-01g"], R["f2"]["storage_env"][0], R["f2"]["storage_env"][1]))
    w("PWR-F12's key-down: 18 A for 60 s (%.1f A a cell) from a cell at C1's +%.0f C trigger warms the cells %.2f to %.2f K adiabatically (MODELED, R_CELL lo/hi over 480 to 660 J/K):"
      % (kd["i_cell"], kd["from"], kd["rise"][0], kd["rise"][1]))
    w("   to %.2f to %.2f C, inside +%.0f C; F2's own 0.32 to 0.81 W rise on top is unpublished, so its margin stays PWR-F12's (bench P13). The coupling measure changes neither figure."
      % (kd["to"][0], kd["to"][1], lim["discharge"][1]))
    w("U2 (BQ7720700): its fixed %.0f C over-temperature trips from %.1f C at the network, so at the +%.0f C storage margin (%s) and at the +%.0f C margin's worst air (%s) a fitted pack would blow F2 and be retired."
      % (S["U2"]["ot"]["BQ7720700"], R["u2"]["trip_lo"], R["f"]["amb"], R["u2"]["LO-01f"], d["amb"], R["u2"]["LO-01d"]))
    w("The gauge's thresholds stay inside REQ-046's windows (OTC %.1f, OTD %.1f, UTC %.1f, UTD %.1f C; THERMAL-COORDINATION.md section 5): this record moves none of them. With the coupling"
      % (R["ladder"]["OTC"], R["ladder"]["OTD"], R["ladder"]["UTC"], R["ladder"]["UTD"]))
    w("   measure the block gains a gradient (wall side cooler, the side under board B hotter), so the thermistors go on the hottest cells and P14's gradient term is re-measured (INFERRED).")
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
    H, G2, hot, tp = R["hold"], R["gaps"], R["hot"], R["tp"]
    env = R["env"]
    fans = "fans and heat spreading move heat from the cells to the case but cannot cool them below the ambient"
    rows = [
        {"id": "C01", "lo": "LO-01a", "cond": "discharge in use at the hot edge, on the pack (the heat stage, lid closed or open)", "zero_power": False,
         "amb": "+%.0f C (REQ-024)" % env["in_use"]["max"], "dur": "a mission (steady)", "cfg": "deployed, pack fitted, discharging (E3-A, E3-L)",
         "limit": "discharge %.0f to %.0f C at the cell surface (35E Ver. 1.1 3.12)" % lim["discharge"],
         "power": "the pack (the mat and fans draw on it)",
         "gap": "%.2f K on the pack at the bound's worst corner (%.2f C); none on 32.53's conductance (%.2f C)" % (a["cell_closed_W4_pack"] - lim["discharge"][1], a["cell_closed_W4_pack"], a["cell_closed_3253_pack"]),
         "approaches": ["the cells sit ABOVE the ambient by the kit's own heat, so moving that heat out works: credible",
                        "the enclosure's conductance itself decides it (break-even, section 3a): T-H1 measures it",
                        "fallback: couple the block to the case skin (section 3b), steady state, no hold time needed",
                        "a path to the face plate instead: rejected, the block sits on the floor under board B and the plate above it, and the plate is the inside air's main exit, so it runs near that air (INFERRED from 32.53's split)",
                        "a lower heat stage: rejected, its 23 W carries REQ-052's required set"],
         "result": "CREDIBLE: thermal design, CONDITIONAL on T-H1 (section 3)"},
        {"id": "C02", "lo": "LO-01a", "cond": "idle on an input at the hot edge (shore, vehicle or solar; the pack neither charging nor discharging), E5-A included", "zero_power": False,
         "amb": "+%.0f C" % env["in_use"]["max"], "dur": "a mission; E5-A %s" % tp["E5-A"], "cfg": "deployed, pack fitted, idle at the inside air",
         "limit": "+%.0f C, the idle pack's limit as REQ-046's note and REQ-077 read it (discharge and 1 month storage both +%.0f C)" % (lim["discharge"][1], lim["st_1m"][1]),
         "power": "the input",
         "gap": "%.2f K lid closed on the bound's worst corner (%.2f C air); lid open %.2f C (none)" % (a["air_closed_W4"] - lim["discharge"][1], a["air_closed_W4"], a["air_open_W4"]),
         "approaches": ["as C01; the hot stop (REQ-077) acts first where the air passes H1's reading: a FAIL of REQ-024 where it does, FEA-004's"],
         "result": "CREDIBLE: as C01"},
        {"id": "C03", "lo": "LO-01b", "cond": "discharge in use at the cold edge, once warm", "zero_power": False,
         "amb": "%.0f C" % env["in_use"]["min"], "dur": "a mission; E4-O %.0f h" % tp["E4-O"][0], "cfg": "deployed, pack fitted, discharging",
         "limit": "discharge floor %.0f C at the cell surface" % lim["discharge"][0], "power": "the pack",
         "gap": "none: cells %.2f C on the highest conductance" % R["b"]["cell"], "approaches": ["none needed"], "result": "NO GAP"},
        {"id": "C04", "lo": None, "cond": "a start from a pack cold-soaked below about -10 C", "zero_power": False,
         "amb": "below about -10 C at the cells", "dur": "the start", "cfg": "pack fitted",
         "limit": "discharge floor %.0f C" % lim["discharge"][0], "power": "shore or vehicle input, or warming",
         "gap": "out of scope by the owner's D-02d", "approaches": ["no requirement: D-02d"], "result": "NOT REQUIRED (D-02d)"},
        {"id": "C05", "lo": "LO-01c", "cond": "charging in use, hot", "zero_power": False,
         "amb": "-20 to +40 C", "dur": "a mission", "cfg": "deployed, pack fitted, charging",
         "limit": "charge %.0f to %.0f C at the cell surface; T3 %.0f C starts no charge" % (lim["charge"][0], lim["charge"][1], 42.0), "power": "the input",
         "gap": "none by requirement: the charge holds off outside the window (window reached at %.1f to +%.1f C ambient)" % (R["c"]["reach_lo"], R["c"]["reach_hi"]),
         "approaches": ["none needed; D-02b's accepted consequence"], "result": "NO GAP"},
        {"id": "C06", "lo": "LO-01c", "cond": "charging in use, cold (warmed by the mat before charge, REQ-046)", "zero_power": False,
         "amb": "%.0f C" % env["in_use"]["min"], "dur": "the warm-up, then the charge", "cfg": "deployed, pack fitted, on an input",
         "limit": "charge from %.0f C at the cell surface; the gauge's UTC %.1f C, the panel's +%.0f C hold" % (lim["charge"][0], R["ladder"]["UTC"], R["cchg"]["hold"]),
         "power": "the input (the mat's %.1f W regulated)" % R["heat_reg"],
         "gap": "the cells must rise from the inside air to +%.0f C; the mat lifts them to %.2f C" % (R["cchg"]["hold"], R["cchg"]["base"][1]),
         "approaches": ["powered heating on the input: an energy source exists in this condition, the start is the existing hold-then-warm sequence, its use is on the input"],
         "result": "CREDIBLE: the existing mat (section 3d)"},
        {"id": "C07", "lo": "LO-01d", "cond": "D-02a's +%.0f C operating margin (E3-O)" % d["amb"], "zero_power": False,
         "amb": "+%.0f C" % d["amb"], "dur": "%.0f h (E3-O)" % d["hours"], "cfg": "deployed, monitor and radios on, on shore or vehicle input, pack fitted (FEA-008)",
         "limit": "+%.0f C (discharge surface and the idle pack's limit); the hot stop's H1 at a reading of +%.1f C" % (lim["discharge"][1], hot["H1"]),
         "power": "the input",
         "gap": "%.2f to %.2f K" % G2["LO-01d"],
         "approaches": [fans + "; here the cells may sit at most %.0f K above it, against a %.2f to %.2f K inside-air rise" % (lim["discharge"][1] - d["amb"], d["rise_lo"], d["rise_hi"]),
                        "insulation: its time constant %.0f to %.0f s against %.0f s of exposure gives no hold, so it must work in the steady state: reaching the limit's f at the worst corner needs %.1f to %.1f mm at k %.2f W/mK (ASSUMPTION) on the four inside faces, against %.2f to %.2f mm of room (SHORTLIST's rows): rejected" % (H["tau_pack_s"][0], H["tau_pack_s"][1], H["e3o_s"], R["meas"]["ins_mm"][0], R["meas"]["ins_mm"][1], K_INS, min(R["room"].values()), max(v for k, v in R["room"].items() if k != "across")),
                        "coupling to the skin (section 3b): best f %.3f against the %.3f to %.3f the limit needs: rejected" % (R["best"]["f"], R["meas"]["d_f_needed"][0], R["meas"]["d_f_needed"][1]),
                        "active cooling on the input (a Peltier stage): rejected, no volume in the pocket and its hot side rejects into the sealed case at or above +%.0f C, raising the air further" % d["amb"],
                        "shedding to the hot stop keeps the cells safe but stops every module: fails E3-O's 'no shutdown'; with the coupling the cells still pass H1's reading at every corner (%.2f C at the best)" % R["meas"]["d_best"][1]],
         "result": "REJECTED for thermal design; a cell route only (section 4)"},
        {"id": "C08", "lo": "LO-01e", "cond": "E5's humid dwell (SC-03 margin)", "zero_power": False,
         "amb": "%.0f to %.0f C at %.0f %% RH" % (e["lo"], e["amb"], e["rh"]), "dur": "%.0f cycles of %.0f h (the dwell's length not stated)" % (e["cycles"], e["hours"]),
         "cfg": "deployed, logging, on shore or vehicle input, pack fitted (FEA-008)",
         "limit": "+%.0f C (discharge surface; storage 1 month)" % lim["discharge"][1], "power": "the input",
         "gap": "at least %.2f K: the chamber alone is at the limit" % G2["LO-01e"],
         "approaches": [fans + ", and the chamber is AT the cells' limit before the kit adds any heat",
                        "insulation or thermal storage: ten days of cycles against a %.0f to %.0f s time constant: no hold" % H["tau_pack_s"],
                        "active cooling: rejected as C07"],
         "result": "REJECTED for thermal design; a cell route only (section 4)"},
        {"id": "C09", "lo": "LO-01f", "cond": "D-02a's +%.0f C storage margin (E3-S)" % R["f"]["amb"], "zero_power": True,
         "amb": "+%.0f C" % R["f"]["amb"], "dur": "%.0f h" % R["f"]["hours"], "cfg": "stored: closed, latched, every input unplugged, pack fitted in its gauge's shutdown (REQ-025, SC-19)",
         "limit": "storage 1 month %.0f to %.0f C at %s (35E Ver. 1.1 3.13)" % (lim["st_1m"][0], lim["st_1m"][1], lim["soc"]),
         "power": "zero (no input; the pack may not be drawn in storage)",
         "gap": "%.0f K: the ambient alone exceeds the limit" % G2["LO-01f"],
         "approaches": ["fans, spreading, heating or cooling: no power in this condition",
                        "insulation or thermal storage: the kit settles within %.2f K of the ambient in %.0f h (time constant at most %.2f h)" % (H["resid_hot"], R["f"]["hours"], H["tau_kit_s"][1] / 3600.0)],
         "result": "REJECTED for thermal design: the ambient alone exceeds the cell's limit; only a cell whose maker's sheet covers the level"},
        {"id": "C10", "lo": "LO-01g", "cond": "D-02a's %.0f C storage margin (E4-S)" % R["g"]["amb"], "zero_power": True,
         "amb": "%.0f C" % R["g"]["amb"], "dur": "%.0f h" % R["g"]["hours"], "cfg": "stored, as C09",
         "limit": "storage floor %.0f C (Ver. 1.1); %.0f C (Version 1.0)" % (lim["st_1m"][0], S["35E_10"]["st_1m"][0]),
         "power": "zero",
         "gap": "%.0f K (Ver. 1.1); %.0f K (Version 1.0)" % G2["LO-01g"],
         "approaches": ["heating: no power; to hold %.0f C for the %.0f h would take %.0f to %.0f Wh, more than the pack's %.1f Wh" % (lim["st_1m"][0], R["g"]["hours"], H["e_hold_cold_Wh"][0], H["e_hold_cold_Wh"][1], H["pack_Wh_nom"]),
                        "insulation: settles within %.2f K in %.0f h" % (H["resid_cold"], R["g"]["hours"])],
         "result": "REJECTED for thermal design; only a cell whose maker's sheet covers the level"},
        {"id": "C11", "lo": "LO-01h", "cond": "storage inside the envelope", "zero_power": True,
         "amb": "%.0f to +%.0f C; %.0f to +%.0f C" % (env["storage_3_months"]["min"], env["storage_3_months"]["max"], env["storage_1_year"]["min"], env["storage_1_year"]["max"]),
         "dur": "three months; a year", "cfg": "stored, as C09",
         "limit": "Ver. 1.1: 3 months %.0f to %.0f C, 1 year %.0f to %.0f C" % (lim["st_3m"][0], lim["st_3m"][1], lim["st_1y"][0], lim["st_1y"][1]), "power": "zero",
         "gap": "none on Ver. 1.1; %.0f K and %.0f K on Version 1.0" % G2["LO-01h"],
         "approaches": ["procurement of a lot governed by Ver. 1.1 (BAT-F09)"], "result": "CREDIBLE: procurement (no thermal measure)"},
        {"id": "C12", "lo": None, "cond": "transport and stored soaks at the cells' own limits (REQ-074)", "zero_power": True,
         "amb": "E3-T +%.0f C set point; E4-T %s" % (tp["E3-T"], tp["E4-T"]), "dur": "24 h each", "cfg": "closed, latched, kit off, pack fitted in shutdown",
         "limit": "the governing sheet's storage limits", "power": "zero",
         "gap": "none: the levels are the limits by construction", "approaches": ["none needed"], "result": "NO GAP"},
        {"id": "C13", "lo": None, "cond": "a PA key-down at the hot edge (PWR-F12): 18 A for 60 s from C1's cell trigger", "zero_power": False,
         "amb": "any in use", "dur": "60 s", "cfg": "deployed, discharging at 18 A",
         "limit": "+%.0f C at the cell surface" % lim["discharge"][1], "power": "the pack",
         "gap": "none for the cells (to %.2f to %.2f C); F2's own margin unknown" % R["kd"]["to"], "approaches": ["the existing gates (K2, C4)"], "result": "NO GAP for the cells; F2 open (section 6)"},
    ]
    return rows


def conflict_lines(R):
    S, d, e = R["S"], R["d"], R["e"]
    lim = S["35E_11"]
    return [
        "Requirement side: D-02a's +%.0f C operation (%.0f h, E3-O), +%.0f C storage (%.0f h, E3-S) and %.0f C storage (%.0f h, E4-S), and SC-03's E5 dwell to +%.0f C (%.0f x %.0f h),"
        % (d["amb"], d["hours"], R["f"]["amb"], R["f"]["hours"], R["g"]["amb"], R["g"]["hours"], e["amb"], e["cycles"], e["hours"]),
        "   each with the pack fitted, as FEA-008's acceptance reads them (REQ-051, D-29: no cell exemption; the stored kit keeps its pack, REQ-025 and SC-19; no power in storage).",
        "Limit side: the cell maker's +%.0f C (discharge at the surface, storage for one month at %s) and %.0f C storage floor (35E Ver. 1.1 3.12, 3.13), and its 'Don't leave ... in a car or"
        % (lim["discharge"][1], lim["soc"], lim["st_1m"][0]),
        "   similar place where inside of temperature may be over 60°C'; every 18650 maker's specification held stops at +%.0f C in storage (the 30Q6 and the P28A at +60 C in ambient" % R["maker_top"],
        "   discharge, the HG2 at +60 C in its own cautions), and none rates storage below %.0f C (%s)." % (R["maker_floor"], ", ".join(R["maker_floor_by"])),
        "In which conditions: the four levels above; the ambient alone reaches or exceeds the limit in three of them (E3-S, E4-S, E5), and in E3-O the kit's own heat adds %.2f to %.2f K over +%.0f C."
        % (d["rise_lo"], d["rise_hi"], d["amb"]),
        "Bound with it: D-06 (one 4S3P 18650 pack of about 145 Wh in the east pocket), REQ-074 (the cells never past their own storage limits: for such exposure the pack comes out), and",
        "   board P's F2, whose operating range (%.0f to +%.0f C) every one of the four levels also leaves. The collision is between D-02a with SC-03 (as FEA-008 reads them) and D-06 with REQ-074."
        % (S["F2"]["operating"][0], S["F2"]["operating"][1]),
        "The one decision that resolves it: for these four levels, is the kit's margin to be shown with its pack fitted (which needs a cell and a fuse no held specification rates), or with the",
        "   pack removed and stored apart as REQ-074 already instructs and REQ-051's deviations already run (the reading D-29 reserves to the owner)?",
    ]


def option_lines(R):
    c = R["cand"]
    hl = R["S"]["HL18650V"]
    return [
        "A. Keep the 35E (D-06 as ruled) and decide that these four levels are shown with the pack out of the exposure, as REQ-074 and REQ-051's deviations already have it.",
        "   Consequence: no spend, no energy lost, no part changed; the kit is not claimed at those four levels with its own pack; FEA-008's rows d to g close by that decision,",
        "   a and h stay CONDITIONAL on their verification. Session's recommendation (not adopted; D-29 reserves the reading to the owner): A, because no held maker's specification of an",
        "   18650 lithium-ion cell rates the storage levels, the maker forbids the condition, and the alternative rests on a product page.",
        "B. Pursue a wide-temperature 18650 within D-06's 4S3P (the HL18650V class): first the maker's signed specification (a document request, drafted in clarification/, no money), then a",
        "   fuse for F2's place beyond %.0f to +%.0f C, U2's variant, the gauge data and UN 38.3 papers. Consequence: one pack of 12 cells at about USD %.2f each (USD %.2f, sample lot extra);"
        % (R["S"]["F2"]["operating"][0], R["S"]["F2"]["operating"][1], R["price_hl"], 12 * R["price_hl"]),
        "   energy %.1f Wh nominal against %.1f (%.1f %% less usable), so D-06's 'about 145 Wh' is restated and DR-01 widens (%.2f h against %.2f h at PS-IDLE-SPEC); closes d to g only if every"
        % (c["HL18650V"]["wh_nom"], c["35E"]["wh_nom"], -100.0 * (c["HL18650V"]["usable_wh"] / c["35E"]["usable_wh"] - 1.0), c["HL18650V"]["hours"], c["35E"]["hours"]),
        "   outstanding item lands; the owner's spend approval (cell_provenance) and his restatement of D-06's parenthesis are needed first.",
        "C. Keep FEA-008's rows d to g open as a release gate, no reading taken and no money spent, until a cell and a fuse with makers' specifications are found. Consequence: the power",
        "   architecture's closure criterion 1 stays failing on those four rows.",
    ]


def downstream_lines(R):
    gs = R["gstar"]
    return [
        "Layer 6 (components): the 35E lot's specification revision on the purchase record (Ver. 1.1; BAT-F09) closes LO-01h; F2's storage line and operation above +60 C to Eaton (Q-E2,",
        "   extended: the draft in clarification/); under option B only, the wide-temperature cell's specification, a fuse for F2's place, U2's variant. Acceptance: the documents filed and read.",
        "Layer 7 (mechanical): if T-H1 reads under %.3f W/K lid closed with fans, the block's east face and base coupled to the case skin (gap filler in M4b, the mat on the floor) and the"
        % gs["cell limit"]["pack"],
        "   hold-down (M4a, M5 OPEN) designed around it. Acceptance: E3-L with the pack fitted, every cell at or under +60 C at +40 C lid closed.",
        "Layer 8 (generator owners): none now; under option B, gen_sch_p.py (U2, F2) and pcb_pack_protection.yaml's thresholds re-derived for the new cell. Acceptance: the protection suite.",
        "Layer 9 (pre-layout analysis): board P's place against the block (F2 at the inside air passes +60 C at LO-01a's worst corner) and the thermistors on the hottest cells.",
        "   Acceptance: F2's body at or under +60 C in E3-A, E3-L and P13; P14's gradient term measured.",
        "Prototype bench: T-H1 with the dummy pack block (the lid-closed conductance against the break-even), E3-A, E3-L, E3-H with the pack fitted and a thermocouple on every cell, E4-O,",
        "   P13, P14. Acceptance: each run's pass line in TEST-PLAN; the break-even replaced by the measured conductance.",
        "Firmware owner: only if the coupling measure is fitted, the mat's thermostat on battery at the cold end (section 3c) with its consumption in the energy budget.",
        "Owner: the decision of section 5 (A, B or C); no spend is asked now.",
    ]


def predicates(R):
    dec, modes = R["dec"], R["modes"]
    p = {}
    p["P1 every LO row has a decision"] = sorted(dec) == sorted(modes)
    p["P2 a closed or no-collision row rests on MAKER or bounded MODELED evidence only"] = all(
        set(d["evidence"]) <= {"MAKER", "MODELED"} and d["bounded"] for d in dec.values() if d["decision"] in ("CLOSED", "NO_COLLISION"))
    p["P3 no cell change is taken"] = all(d["cell_change"] is None or (d["cell_change"]["taken"] is False and d["cell_change"]["owner_approval_required"]) for d in dec.values())
    p["P4 the screen covers every LO row"] = set(r["lo"] for r in R["screen"] if r["lo"]) == set(modes)
    p["P5 zero-power rows reject powered heating or cooling or need none"] = all(
        ("no power" in " ".join(r["approaches"]) or r["result"].startswith("NO GAP") or r["result"].startswith("CREDIBLE: procurement")) for r in R["screen"] if r["zero_power"])
    p["P6 storage margins: the hold time is shorter than the exposure"] = R["hold"]["tau_kit_s"][1] * 3 < R["f"]["hours"] * 3600.0
    p["P7 at most three owner options"] = sum(1 for l in option_lines(R) if re.match(r"^[A-Z]\. ", l)) <= 3
    p["P8 the collisions reproduce Layer 3's table"] = all(v[2] for v in R["agree"].values())
    p["P9 every decision is a known kind"] = all(d["decision"] in ("CLOSED", "CONDITIONAL", "NO_COLLISION", "NOT_CLOSABLE") for d in dec.values())
    return p


def main():
    R = compute()
    sys.stdout.write("\n".join(render(R)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
