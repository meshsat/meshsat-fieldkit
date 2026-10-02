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
RT57 = "v2/vendor/battery/pcm/rubitherm-rt57hc-2026-01-21.pdf"
RT55 = "v2/vendor/battery/pcm/rubitherm-rt55-2026-01-21.pdf"
LSH20 = "v2/vendor/battery/held/saft-lsh20-31015-2-0426.pdf"
LSH20HTS = "v2/vendor/battery/held/saft-lsh20hts-31057-2-0710.pdf"
LSHCURVES = "v2/docs/records/l4e10/inputs/saft-lsh20-curves-read-2026-10-01.json"
M507 = "v2/vendor/standards/mil-std-810h-method-507-6.md"
TRM = "v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf"
HEATER = "v2/vendor/battery/heater/rs-pro-245-556-heater-mat-sheet.pdf"
TOPWELL = "v2/docs/records/l4e10/inputs/topwell-hl18650v-page-2026-10-01.json"
PRICES = "v2/docs/records/l4e10/inputs/prices-2026-10-01.json"
BEYOND = "v2/docs/records/l4e10/inputs/cells-beyond-held-2026-10-02.json"
EB_PY = "v2/docs/records/energy/energy_budget.py"
EB_IN = "v2/docs/records/energy/energy_inputs.yaml"
REPLAY = "v2/docs/records/l4e/l4e_replay.out"
CSS = "v2/docs/review-packets/battery/CHARGER-STATE-SEQUENCE.md"
L4E9 = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
CL_TW = "v2/docs/records/l4e10/clarification/topwell-hl18650v.txt"
SAFT_MP = "v2/vendor/battery/held/saft-mp176065xtd-31109-2-0625.pdf"
PRICES2 = "v2/docs/records/l4e10/inputs/prices-2026-10-02.json"
L4E12 = "aab69775@v2/docs/records/l4e12/l4e12_thermal.out"     # U-02's record at its commit (fnd/l4e12, the consolidation)
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
    RT57: "74a5c20c8cc472d913b7e13865a12ee6aa18b1b065962d3d3527467fc7c2642b",
    RT55: "fac4909cd4a7f95d6743f31afa92b496163efb33b09b2211dad9c02032c882b2",
    LSH20: "79245e64a2c4abb79ad082568ade32357d27f103416dbe899256dfec322e3ecd",
    LSH20HTS: "5befce3a37ab89fad4826488793008f71d5c4ba4a36eacbfadd9dacfa5339d55",
    LSHCURVES: "cc5ad871143dda6c90b07f9ddf6334301dc4c1001bd80783dbf53d5a328a7a68",
    BEYOND: "40d68c77cec82869fe3d1fad9b4c1e8cb067e8ac577e6fd722b487db3660c1ec",
    EB_PY: "6a8ac4642bd2aaf35d5ad6b75c5004c24d3e11ed1ede09a4b7a1041cd103235c",
    EB_IN: "74a6e4ab0074648ed459cc62daf7000798ae6247cd5056e19cae5e4d56f55aed",
    REPLAY: "59c6eeab16da98f8ddf16880ddcdc1d2a2c910f4256be9b69aade49dd4d2726d",
    CSS: "44fdf9a022c49337d60eeefd15b7e7267fb5a4659449f7dc5c38153a9786548f",
    L4E9: "127807c1281baa035f00919fc3a36eeeaa36304a30a915281403e0f7f3186be5",
    SAFT_MP: "8ca0a3e09997a4a30567a4313cf83c2b6cf165543baf424e0ff788d5a8d27f8e",
    PRICES2: "eac0fc1807e7e4989801aa3448c13f4b2870de06f23cb1084059aae518b2c7f0",
    L4E12: "88d7b84179b407533bdf4a542c93487c1fa6ca8f95a742518f529517995f9637",
    CL_TW: "1ca762d83bbb58b2fa493970878970e173c23f91ce7d7bb4518dbc147a07e5e9",
    "v2/vendor/battery/held/toshiba-scib-brochure-2020.pdf": "acc8f192c54fb287f9ef66d5e26c440601fa795c87f46dba881dce747ef07df3",
    "v2/vendor/battery/held/ultraxel-hl18650t-flyer-2025.pdf": "f95db57fa9bef536a0abcab0a8a979db8593ebd528736c53590a35eb853f80c0",
    M507: "aab749c1b6d149c8dddedce99fcc0d505339723300df36a62a257b4ace380d80",
}

# The few figures this record sets itself (ASSUMPTION; each is used in one place and its effect is printed):
K_PAD = 1.0          # W/mK, a gap filler between the pack's east face and the east wall (no maker's sheet held; low end)
T_MAT = 0.0015       # m, the RS PRO heater mat's thickness (its sheet states none)
K_MAT = 0.2          # W/mK, the mat's silicone (its sheet states none)
COP = (0.5, 1.0)     # a thermoelectric cooler's coefficient of performance near these lifts (no module's sheet held)
HOT_RISE = 30.0      # K, the cooler's hot side at most this far above the ambient it rejects to
THERMO_TOL = 3.0     # K, a storage heater's thermostat tolerance (no part held)
GRAD_MEAN = 2.0      # K, the heated block's mean over its coldest cell, where the thermostat sits (the gradient is a bench item)
MARGIN_K = 2.0       # K, a design margin over the storage floor
RES_TYP = 0.20       # the primary cell's typical curves against an unpublished minimum (the maker's own caveat)
REPLACE_Y = 2.0      # years, the primary's replacement interval in the kit
K_INS = 0.02         # W/mK, an aerogel-class insulating blanket (no maker's sheet held), only to size the layer section 2 rejects
CLASSES = ("MAKER", "MODELED", "INFERRED", "ASSUMPTION", "CONDITIONAL")


def refuse(code, msg):
    sys.stderr.write("l4e10_cell_thermal: %s; refusing\n" % msg)
    sys.exit(code)


def path(rel):
    return os.path.join(TOP, rel)


def raw(rel):
    if "@" in rel:                       # a file read at its commit: "commit@path"
        c, r = rel.split("@", 1)
        ch = subprocess.run(["git", "show", "%s:%s" % (c, r)], cwd=TOP, capture_output=True)
        if ch.returncode != 0:
            refuse(2, "%s is not at %s" % (r, c))
        return ch.stdout
    p = path(rel)
    if not os.path.exists(p):
        refuse(2, "%s is missing (held documents: fetch_held_back.py)" % rel)
    return open(p, "rb").read()


def sha(rel):
    return hashlib.sha256(raw(rel)).hexdigest()


def text(rel):
    return raw(rel).decode("utf-8")


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


def md_cells(line):
    """The cells of a markdown table row, split on unescaped pipes only (a cell may carry '\\|')."""
    cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())]
    return cells[1:-1]


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
                "e3h_hold": need(tp, r"at \+40 C with the lid closed the level is held until the hot stop has acted or its (\d) h have passed; once more with the sensor controller held in reset", "E3-H's hold").group(1),
                "tmp117": tuple(float(v) for v in need(tp, r"the same steps act on board B's TMP117 at \+(\d+\.\d) C and \+(\d+\.\d) C", "E3-H's TMP117").groups()),
                "tmp117_rel": float(need(tp, r"released at \+(\d+\.\d) C", "TMP117 release").group(1)),
                "restart": tuple(float(v) for v in need(tp, r"comes back only once the hottest cell reads \+(\d+\.\d) C or less and (\d+) minutes have passed", "E3-H's restart").groups()),
                "e3l_start": need(tp, r"(started once with the lid already closed)", "E3-L's start").group(1),
                "e3l_lid": need(tp, r"(the start with the lid closed enters the reduced mode once the lid is read)", "E3-L's lid start").group(1),
                "e4t_return": need(tp, r"(full function after return to 25 C, capacity within 5 % of its value before \(PROVISIONAL: the maker publishes no cold-storage recovery figure\))", "E4-T's return").group(1),
                "otd_rec": float(need(tp, r"recovers at or below \+(\d+\.\d) C", "E3-P's OTD recovery").group(1)),
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
        # rejected into the inside air: the heat pumped out of the block returns to the air it came from, so the air gains only
        # the cooler's input Q_c/COP: G_e a = q + G_b (a - d)/COP, with a and d the air's and the hold's rise over the chamber
        fS = red2.heat(red2.SURV, "plan")[0]["pb"]
        qs_best = qS + (fS / (pb.ETA_CHG * min(pb.ETA_FE)) - fS)
        if key == "E3-S":
            cases = {"best": (0.0, gcs[1], GB[0]), "worst": (0.0, gcs[0], GB[1])}
            t_amb = e3s_t
        else:
            cases = {"best": (qs_best, G32["open_fans"][1], GB[0]), "worst": (R["shore_heat"], G["open_fans"][0], GB[1])}
            t_amb = e3o_t if key == "E3-O" else R["e"]["amb"]
        inside = {}
        for cname, (q_, ge_, gb_) in cases.items():
            d_ = t_hold - t_amb
            for cop in COP:
                if ge_ > gb_ / cop:
                    a_ = (q_ - gb_ * d_ / cop) / (ge_ - gb_ / cop)
                    qc_ = gb_ * (a_ - d_)
                    inside[(cname, cop)] = {"air": t_amb + a_, "qc": qc_, "p_in": qc_ / cop}
                else:
                    inside[(cname, cop)] = None
        row["inside"] = inside
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

    # ======================================================== 3m: part 2, the open rows' next bounded actions (final round)
    # the pocket's spare volume round the block beyond the 1.0 mm minimums: at the worst stack (SHORTLIST's rooms) and as designed
    # (CASE-MARGINS' largest printed gaps less the minimum), INFERRED; the west face is 2.0 mm from board A's edge
    rooms_w = {"east": room["across"], "top": room["height"], "ends": room["axis"]}
    rows_cm, rows_cm_old = {}, {}
    hdr = md_cells(need(cmt, r"^\| # \| Margin \|.*$", "CASE-MARGINS' table header").group(0))
    col = hdr.index("Chosen: nominal")
    for key in ("M4b", "M5", "M6"):
        line = need(cmt, r"^\| %s \|.*$" % key, "CASE-MARGINS " + key).group(0)
        cells = md_cells(line)
        if len(cells) != len(hdr):
            refuse(4, "CASE-MARGINS row %s has %d cells against the header's %d" % (key, len(cells), len(hdr)))
        rows_cm[key] = float(nums(cells[col])[0])
        # the earlier reading (fix round of 2 October 2026, the verifier's item 3): a plain split on every pipe, kept to show what moved
        rows_cm_old[key] = max(nums(line[len("| %s |" % key):].split("|", 3)[3]))
    R["rows_cm"], R["rows_cm_old"] = rows_cm, rows_cm_old
    A_E, A_B, A_end = Y * Z, X * Y, X * Z
    spare_worst = A_E * rooms_w["east"] / 1000.0 + A_B * rooms_w["top"] / 1000.0 + 2 * A_end * rooms_w["ends"] / 1000.0
    spare_design = (A_E * (rows_cm["M4b"] - 1.0) + A_B * (rows_cm["M6"] - 1.0) + 2 * A_end * (rows_cm["M5"] - 1.0) + A_E * (2.0 - 1.0)) / 1000.0
    R["spare_L"] = (spare_worst * 1000.0, spare_design * 1000.0)          # litres
    spare_old = (A_E * (rows_cm_old["M4b"] - 1.0) + A_B * (rows_cm_old["M6"] - 1.0) + 2 * A_end * (rows_cm_old["M5"] - 1.0) + A_E * (2.0 - 1.0)) / 1000.0
    R["spare_L_old"] = spare_old * 1000.0
    # the phase-change material (MAKER, Rubitherm RT57HC): melting area, capacity (latent and sensible over its range), density
    tr = pdf(RT57)
    pcm = {"melt": tuple(float(v) for v in need(tr, r"Melting area\s+(\d+) - (\d+) \[°C\]", "RT57HC melting").groups()),
           "cap": float(need(tr, r"Heat storage capacity ± 7,5%\s+(\d+)", "RT57HC capacity").group(1)) * 1000.0,
           "tol": 0.075, "cp": float(need(tr, r"Specific heat capacity\s+(\d+)", "RT57HC cp").group(1)) * 1000.0,
           "rho": float(need(tr, r"Density solid\s+~ (\d+),(\d+)", "RT57HC density").group(1)) + float(need(tr, r"Density solid\s+~ (\d+),(\d+)", "RT57HC density").group(2)) / 10.0}
    # favourable to the material: the whole capacity plus its tolerance as latent heat at the TOP of the melting area, the solid density,
    # no container, perfect contact with the cells
    pcm["L"], pcm["Tm"] = pcm["cap"] * (1 + pcm["tol"]), pcm["melt"][1]
    R["pcm"] = pcm

    def sim(chamber, hours, q, C_k, G_e, C_cells, G_b, m, T0k, T0p, dt=30.0):
        """Two nodes, explicit: the kit (air and structure) driven by the chamber and its own heat q; the block (cells and the PCM)
        by the kit through G_b. The block's enthalpy H is counted from the solid at Tm: below 0 sensible, 0 to m*L melting at Tm,
        above that sensible again. Returns the cells' peak temperature."""
        C_p = C_cells + m * pcm["cp"]
        Lm = m * pcm["L"]
        Tm = pcm["Tm"]
        H = (T0p - Tm) * C_p if T0p <= Tm else Lm + (T0p - Tm) * C_p
        Tk, t, end = T0k, 0.0, hours * 3600.0

        def temp(H_):
            return Tm + H_ / C_p if H_ < 0 else (Tm if H_ <= Lm else Tm + (H_ - Lm) / C_p)

        Tp = temp(H)
        peak = Tp
        while t < end:
            qb = G_b * (Tk - Tp)
            Tk += (q - G_e * (Tk - chamber(t)) - qb) * dt / C_k
            H += qb * dt
            Tp = temp(H)
            if Tp > peak:
                peak = Tp
            t += dt
        return peak

    def min_mass(run, limit, top=20.0):
        if run(0.0) <= limit:
            return 0.0
        if run(top) > limit:
            return None
        lo_, hi_ = 0.0, top
        for _ in range(28):
            mid = (lo_ + hi_) / 2.0
            if run(mid) > limit:
                lo_ = mid
            else:
                hi_ = mid
        return hi_

    # the profiles. E5: Method 507.6 Procedure II (transcribed), a 24 h conditioning at 23 C, then ten cycles 30-60-60-30-30 C
    m5 = text(M507)
    tab = [tuple(float(v) for v in mm) for mm in re.findall(r"^\| (\d{4}) \| (\d+) \|", m5, re.M)]
    cond_c = float(need(m5, r"Step 1\. .*?adjust the temperature to (\d+) ± 2 °C", "507.6 Step 1", re.M | re.S).group(1))
    knots = [(int(tt / 100) * 3600.0, temp) for tt, temp in tab]
    n_cyc = int(R["e"]["cycles"])

    def e5_chamber(t):
        t0 = 24 * 3600.0
        if t < t0:
            return cond_c
        tc = (t - t0) % (24 * 3600.0)
        for (ta, va), (tb, vb) in zip(knots, knots[1:]):
            if ta <= tc <= tb:
                return va + (vb - va) * (tc - ta) / (tb - ta)
        return knots[-1][1]

    cyc_mean = sum((tb - ta) * (va + vb) / 2.0 for (ta, va), (tb, vb) in zip(knots, knots[1:])) / (24 * 3600.0)
    R["e5_profile"] = {"knots": [(ta / 3600.0, va) for ta, va in knots], "cond": cond_c, "mean": cyc_mean, "cycles": n_cyc}
    # corners for the kit in operation, lid open with fans, on shore (the heat stage as the least heat, as Layer 3's rows take it)
    qS_shore = qS + (red2.heat(red2.SURV, "plan")[0]["pb"] / (pb.ETA_CHG * eta_fe) - red2.heat(red2.SURV, "plan")[0]["pb"])
    op = {"best": {"q": qS_shore, "G_e": G32["open_fans"][1], "C_k": R["C_kit"][1], "C_cells": R["blk"]["C"][1], "G_b": GB[0]},
          "worst": {"q": R["shore_heat"], "G_e": G["open_fans"][0], "C_k": R["C_kit"][0], "C_cells": R["blk"]["C"][0], "G_b": GB[1]}}
    lim60 = lim["discharge"][1]
    pcm_res = {}
    for cname, c_ in op.items():
        rise_ = c_["q"] / c_["G_e"]
        # E5: start of the conditioning with the kit at the conditioning temperature plus its rise
        s0 = cond_c + rise_
        run5 = lambda m, c_=c_, s0=s0: sim(e5_chamber, 24.0 * (n_cyc + 1), c_["q"], c_["C_k"], c_["G_e"], c_["C_cells"], c_["G_b"], m, s0, s0, dt=60.0)
        # E3-O: a kit stabilised at the chamber's +55 C with the kit off, then 4 h of operation
        run3 = lambda m, c_=c_: sim(lambda t: e3o_t, e3o_h, c_["q"], c_["C_k"], c_["G_e"], c_["C_cells"], c_["G_b"], m, e3o_t, e3o_t)
        pcm_res[cname] = {"e5_mean_air": cyc_mean + rise_, "e5_peak_none": run5(0.0), "e5_m": min_mass(run5, lim60),
                          "e3o_peak_none": run3(0.0), "e3o_m": min_mass(run3, lim60)}
    # E3-S, stored: no kit heat, lid closed and still, from the storage envelope's cold edge (the most favourable start)
    st0 = R["env"]["storage_3_months"]["min"]
    for cname, prm in (("best", corners_c["slow"]), ("worst", corners_c["fast"])):
        runs = lambda m, prm=prm: sim(lambda t: e3s_t, e3s_h, 0.0, prm["C_tot"] - prm["C_p"], prm["G_e"], prm["C_p"], prm["G_b"], m, st0, st0, dt=60.0)
        pcm_res[cname]["e3s_peak_none"] = runs(0.0)
        pcm_res[cname]["e3s_m"] = min_mass(runs, lim60)
    for cname in pcm_res:
        for k in ("e5_m", "e3o_m", "e3s_m"):
            mm_ = pcm_res[cname][k]
            pcm_res[cname][k.replace("_m", "_L")] = None if mm_ is None else mm_ / pcm["rho"]
    R["pcm_res"] = pcm_res
    # the complete E3-O pass: no hot stop, so the cells under H1's no-act limit, against a chamber already at +55 C
    R["h1_window"] = (e3o_t, R["hot"]["H1"] - R["hot"]["terms"]["thermistor interchangeability"])
    # 3o: the conditioned corner. LO-01a's complete pass needs the enclosure at R["gov"] W/K in each lid state (T-H1); every
    # approach carries that condition, so the hot margins are also read with the kit's conductance at that floor and every
    # other parameter at its worst (the same profiles: E3-O from a kit stabilised at +55 C, E5 on Method 507.6's cycle)
    wc = op["worst"]
    g_c = max(R["gov"]["all"][4], wc["G_e"])
    rise_c = wc["q"] / g_c
    s0c = cond_c + rise_c
    run5c = lambda m: sim(e5_chamber, 24.0 * (n_cyc + 1), wc["q"], wc["C_k"], g_c, wc["C_cells"], wc["G_b"], m, s0c, s0c, dt=60.0)
    run3c = lambda m: sim(lambda t: e3o_t, e3o_h, wc["q"], wc["C_k"], g_c, wc["C_cells"], wc["G_b"], m, e3o_t, e3o_t)
    condc = {"G_e": g_c, "rise": rise_c, "e3o_air_ss": e3o_t + rise_c, "e5_air_mean": cyc_mean + rise_c,
             "e3o_peak": run3c(0.0), "e5_peak": run5c(0.0), "e3o_m": min_mass(run3c, lim60), "e5_m": min_mass(run5c, lim60)}
    for k in ("e3o_m", "e5_m"):
        condc[k.replace("_m", "_L")] = None if condc[k] is None else condc[k] / pcm["rho"]
    # the 35E's cooler at this corner, into the sealed case, holding the cells at H1's reading (E3-O at +55 C, E5 at its 60 C dwell)
    condc["cool"] = {}
    for key, t_amb in (("E3-O", e3o_t), ("E5", R["e"]["amb"])):
        d_ = R["hot"]["H1"] - t_amb
        for cop in COP:
            gb_ = wc["G_b"]
            a_ = (wc["q"] - gb_ * d_ / cop) / (g_c - gb_ / cop)
            qc_ = gb_ * (a_ - d_)
            condc["cool"][(key, cop)] = {"air": t_amb + a_, "qc": qc_, "p_in": qc_ / cop}
    condc["g_best"] = op["best"]["G_e"]
    _cache3, _cache5 = {}, {}

    def run3g(g):
        if g not in _cache3:
            _cache3[g] = sim(lambda t: e3o_t, e3o_h, wc["q"], wc["C_k"], g, wc["C_cells"], wc["G_b"], 0.0, e3o_t, e3o_t)
        return _cache3[g]

    def run5g(g):
        if g not in _cache5:
            s0g = cond_c + wc["q"] / g
            _cache5[g] = sim(e5_chamber, 24.0 * (n_cyc + 1), wc["q"], wc["C_k"], g, wc["C_cells"], wc["G_b"], 0.0, s0g, s0g, dt=60.0)
        return _cache5[g]
    R["run3g"], R["run5g"] = run3g, run5g
    condc["air_unc"] = {"E3-O": e3o_t + rise_c, "E5": R["e"]["amb"] + rise_c}
    condc["lift"] = {k: v["air"] - condc["air_unc"][k[0]] for k, v in condc["cool"].items()}
    R["condc"] = condc
    # (a) LO-01g: one lithium primary cell from its maker's sheet (Saft LSH 20), driving the existing mat direct through a thermostat
    ts = pdf(LSH20)
    lsh = {"c_nom": float(need(ts, r"Nominal capacity \(under (\d+) mA, \+20°C, 2\.0 V cut-off\)\d?\s+(\d+) Ah", "LSH 20 capacity").group(2)),
           "c_nom_ma": float(need(ts, r"Nominal capacity \(under (\d+) mA", "LSH 20 capacity current").group(1)),
           "v_nom": float(need(ts, r"Nominal voltage \(at 2 mA, \+ 20°C\)\s+(\d\.\d) V", "LSH 20 voltage").group(1)),
           "i_cont": float(need(ts, r"Maximum recommended continuous current\d?\s+(\d\.\d) A", "LSH 20 current").group(1)),
           "t_op": tuple(float(v) for v in need(ts, r"Operating temperature range\d?\s+(-\d+)°C / \+(\d+)°C", "LSH 20 range").groups()),
           "d": float(need(ts, r"Diameter \(max\)\s+(\d+\.\d) mm", "LSH 20 diameter").group(1)),
           "h": float(need(ts, r"Height \(max\)\s+(\d+\.\d+) mm", "LSH 20 height").group(1)),
           "g": float(need(ts, r"Typical weight\s+(\d+) g", "LSH 20 mass").group(1)),
           "li": float(need(ts, r"Li metal content\s+approx\. (\d\.\d) g", "LSH 20 lithium").group(1)),
           "un": need(ts, r"Transport: (UN \d{4} and UN \d{4})", "LSH 20 transport").group(1),
           "self": need(ts, r"(less than 3%\s+per year of storage, at \+ 20°C, after 1\s+year)", "LSH 20 self-discharge").group(1).replace("\n", " "),
           "typical": bool(re.search(r"experimental averages and do not necessarily reflect the[\s\S]*?minimum values that may be observed", ts))}
    lsh["self_pct"] = float(need(lsh["self"], r"less than (\d+)%", "self-discharge").group(1)) / 100.0
    cr = json.load(open(path(LSHCURVES), encoding="utf-8"))

    def interp(curve, i_ma):
        (i1, y1), (i2, y2) = curve
        return y1 + (y2 - y1) * (math.log10(i_ma) - math.log10(i1)) / (math.log10(i2) - math.log10(i1))

    def cell_at(i_ma, temp):
        w_ = (temp - (-40.0)) / 20.0
        cap = interp(cr["capacity_Ah"]["-40"], i_ma) * (1 - w_) + interp(cr["capacity_Ah"]["-20"], i_ma) * w_
        v = interp(cr["voltage_V"]["-40"], i_ma) * (1 - w_) + interp(cr["voltage_V"]["-20"], i_ma) * w_
        return cap, v

    r_mat = 12.0 ** 2 / S["mat"]["power"]                      # the mat as a resistor: 12 V and 7.5 W (MAKER)
    allow = {"thermostat": THERMO_TOL, "gradient": GRAD_MEAN, "margin": MARGIN_K}
    a_tot = sum(allow.values())
    reserve = {"typical against minimum": RES_TYP, "self-discharge over the replacement interval": lsh["self_pct"] * REPLACE_Y}
    r_tot = sum(reserve.values())
    prim = {"r_mat": r_mat, "allow": allow, "allow_tot": a_tot, "reserve": reserve, "reserve_tot": r_tot, "configs": {}}
    for ns in (4, 5):
        for tname, temp in (("-40 C curve (lower)", -40.0), ("at the hold's air", e4s_t + sh["air_dev"][0])):
            i_ = 500.0
            for _ in range(60):
                cap, v = cell_at(i_, temp)
                i_ = ns * v / r_mat * 1000.0
            p_on = ns * v * i_ / 1000.0
            e_str = ns * v * cap
            row = {"i_ma": i_, "v": v, "cap": cap, "p_on": p_on, "e_string": e_str}
            for cname in ("slow", "fast"):
                gs_ = sh["g_series"][0 if cname == "slow" else 1]
                p_avg = gs_ * (sh["set_prim"] + a_tot - e4s_t)
                demand = p_avg * e4s_h
                need_e = demand / (1.0 - r_tot)
                m_str = max(1, math.ceil(need_e / e_str))
                row[cname] = {"p_avg": p_avg, "duty": p_avg / p_on, "demand": demand, "need": need_e, "strings": m_str,
                              "cells": m_str * ns, "kg": m_str * ns * lsh["g"] / 1000.0,
                              "L": m_str * ns * math.pi * (lsh["d"] / 20.0) ** 2 * (lsh["h"] / 10.0) / 1000.0,
                              "dur_h": m_str * e_str * (1.0 - r_tot) / p_avg, "reserve_Wh": m_str * e_str * (1.0 - r_tot) - demand,
                              "i_ok": i_ / 1000.0 / m_str <= lsh["i_cont"]}
            prim["configs"]["%dS, %s" % (ns, tname)] = row
    R["lsh"], R["prim"] = lsh, prim

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
    # cells beyond the held set (the owner's instruction of 2 October 2026), from the makers' own published lines (BEYOND)
    bj = json.load(open(path(BEYOND), encoding="utf-8"))
    rd = {r_["id"]: r_ for r_ in bj["readings"]}
    lwv = rd["APR18650M1B"]["verbatim"]
    lfp = {"v": float(need(lwv, r"Voltage (\d\.\d) V", "APR18650M1B voltage").group(1)),
           "c_min": float(need(lwv, r"Typical \(Min\) \d\.\d Ah \((\d\.\d+) Ah\)", "APR18650M1B min").group(1)),
           "wh": float(need(lwv, r"Energy @ 23°C (\d\.\d+) Wh", "APR18650M1B energy").group(1)),
           "dis": tuple(float(v) for v in need(lwv, r"Discharging .*?Temperature (-\d+)°C to (\d+)°C", "APR18650M1B discharge").groups()),
           "chg": tuple(float(v) for v in need(lwv, r"(\d+) ºC to (\d+) ºC Storage", "APR18650M1B charge").groups()),
           "st": tuple(float(v) for v in need(lwv, r"Storage Temperature (-\d+) ºC to (\d+) ºC", "APR18650M1B storage").groups()),
           "v_chg": float(need(lwv, r"Recommended Charge Voltage (\d\.\d) V", "APR18650M1B charge voltage").group(1)),
           "i_cont": float(need(lwv, r"Max\. Continuous Discharge Current (\d+)A", "APR18650M1B current").group(1)),
           "g": float(need(lwv, r"Mass (\d+\.\d) \+/-", "APR18650M1B mass").group(1))}
    lfp["pack_wh_nom"] = 12 * lfp["wh"]
    lfp["v4s"] = 4 * lfp["v"]
    lfp["meets"] = {"LO-01d": False, "LO-01e": False, "LO-01f": e3s_t <= lfp["st"][1], "LO-01g": e4s_t >= lfp["st"][0]}
    tsv = rd["SCiB"]["verbatim"]
    lto = {"low": float(need(tsv, r"as low as (-\d+)°C", "SCiB low").group(1)),
           "v": sorted(set(float(v) for v in re.findall(r"(\d\.\d)V", tsv))),
           "dims": need(tsv, r"Dimensions (W\d+ × D\d+ × H\d+mm)", "SCiB dims").group(1),
           "smallest_ah": float(need(tsv, r"Nominal Capacity (\d+\.\d)Ah", "SCiB capacity").group(1))}
    uxv = rd["HL18650T"]["verbatim"]
    ux = {"c_min": float(need(uxv, r"Min capacity \(0\.2C\) (\d+) mAh", "HL18650T min").group(1)) / 1000.0,
          "dis": tuple(float(v) for v in need(uxv, r"Discharge (-\d+)~(\d+)℃", "HL18650T discharge").groups()),
          "retain_claim": need(uxv, r"(Recovery capacity after 1000h 80℃ aging > \d+%)", "HL18650T claim").group(1),
          "chart": rd["HL18650T"]["chart_read"], "storage_rows": "Storage" in uxv}
    ux["pack_wh_nom"] = 12 * ux["c_min"] * pb.V_NOM
    ux["chart_pct"] = 100.0 * ux["chart"]["recovery_Ah"] / ux["chart"]["initial_Ah"]
    R["beyond"] = {"lfp": lfp, "lto": lto, "ux": ux, "src": [(r_["id"], r_["maker"], r_["class"], r_["sha256"][:16]) for r_ in bj["readings"]]}
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

    # ======================================================== 4d: one bounded comparison of three complete approaches (the owner's instruction of 2 October 2026)
    cc = R["condc"]
    hl = S["HL18650V"]
    twj = json.load(open(path(TOPWELL), encoding="utf-8"))
    w35 = float(need(pdf(S35E11), r"Cell Weight\s+(\d+) g max", "35E weight").group(1))
    whl = float(need(twj["specification_table_verbatim"], r"Weight Approx\. (\d+)g", "HL18650V weight").group(1))
    # (II)'s first-cut protection: the present ladder's offsets from the 35E's +60 C kept under the wide-temperature cell's idle
    # limit, the lower of its hot rows (storage within 30 days, +80 C); U2's lowest trip at the network taken the same distance
    # under each variant's nominal as the BQ7720700's (INFERRED: the network's tolerance analysis is not re-run here)
    lim2 = hl["st_30d"][1]
    off = {k: lim["discharge"][1] - R["hot"][k] for k in ("C1", "H1", "H2", "OTD")}
    lad2 = {k: lim2 - v for k, v in off.items()}
    h1n2 = lad2["H1"] - R["hot"]["terms"]["thermistor interchangeability"]
    u2_off = S["U2"]["ot"]["BQ7720700"] - R["ladder"]["U2_trip_lo"]
    u2lo = {k: v - u2_off for k, v in S["U2"]["ot"].items()}
    clear = max(cc["e3o_peak"], cc["e5_peak"], e3s_t)
    u2_pick = min((k for k, v in u2lo.items() if v > clear), key=lambda k: (S["U2"]["ot"][k], k))
    cell_a_c = pb.cell_temp(t_use, qR, pR, cc["G_e"], GB[0])
    m2 = {"LO-01a": {"peak": cell_a_c, "limit": hl["discharge"][1], "h1": h1n2},
          "LO-01d": {"peak": cc["e3o_peak"], "limit": lim2, "h1": h1n2, "u2": u2lo[u2_pick]},
          "LO-01e": {"peak": cc["e5_peak"], "limit": lim2, "h1": h1n2, "u2": u2lo[u2_pick]},
          "LO-01f": {"peak": e3s_t, "limit": lim2, "u2": u2lo[u2_pick]},
          "LO-01g": {"peak": e4s_t, "limit": hl["st_30d"][0]},
          "LO-01h": {"rows": (st_env["storage_3_months"]["min"] - hl["st_6m"][0], hl["st_6m"][1] - st_env["storage_3_months"]["max"],
                              hl["st_12m"][1] - st_env["storage_1_year"]["max"])}}
    for k, v in m2.items():
        if "limit" in v:
            v["m_limit"] = (v["peak"] - v["limit"]) if k == "LO-01g" else (v["limit"] - v["peak"])
        if "h1" in v:
            v["m_h1"] = v["h1"] - v["peak"]
        if "u2" in v:
            v["m_u2"] = v["u2"] - v["peak"]
    # at the bound's worst corner (the enclosure under LO-01a's line), E5's cells against (II)'s ladder: the dependency on T-H1
    m2_unc = {"e5_peak": R["pcm_res"]["worst"]["e5_peak_none"], "e3o_peak": R["pcm_res"]["worst"]["e3o_peak_none"]}
    # (I) at the conditioned corner: the 35E's cooler into the sealed case and its latent storage, and their effect on endurance
    usable35, w_ = R["cand"]["35E"]["usable_wh"], R["w_idlespec"]
    endu = lambda p_: usable35 / (w_ + p_)
    best_in = (cool["E3-O"]["inside"][("best", 1.0)]["p_in"], cool["E5"]["inside"][("best", 0.5)]["p_in"])
    cond_in = (cc["cool"][("E3-O", 1.0)]["p_in"], cc["cool"][("E5", 0.5)]["p_in"])
    cond_air = (cc["cool"][("E3-O", 1.0)]["air"], cc["cool"][("E5", 0.5)]["air"])
    i1 = {"best_in": best_in, "cond_in": cond_in, "cond_air": cond_air, "endu_best": (endu(best_in[1]), endu(best_in[0])),
          "endu_cond": (endu(cond_in[1]), endu(cond_in[0])), "endu_none": endu(0.0),
          "pcm_cond_L": (cc["e3o_L"], cc["e5_L"]), "e3s_Wh_best": (24 * cool["E3-S"]["inside"][("best", 1.0)]["p_in"], 24 * cool["E3-S"]["inside"][("best", 0.5)]["p_in"])}
    # (III)'s primary battery as added energy storage under D-06 (MAKER: Saft's nominal energy and its storage recommendation)
    ts_ = pdf(LSH20)
    lsh_e = float(need(ts_, r"Nominal energy\s+(\d+) Wh", "LSH 20 energy").group(1))
    lsh_st = float(need(ts_, r"\+(\d+)°C \(\+86°F\)", "LSH 20 storage").group(1))
    psel_ = R["prim"]["configs"]["5S, -40 C curve (lower)"]
    iii = {"wh_nom": (psel_["slow"]["cells"] * lsh_e, psel_["fast"]["cells"] * lsh_e), "li_g": (psel_["slow"]["cells"] * R["lsh"]["li"], psel_["fast"]["cells"] * R["lsh"]["li"]),
           "st_max": lsh_st, "st_env": st_env["storage_3_months"]["max"], "no_recharge": bool(re.search(r"Do not recharge", ts_)),
           "no_mix": bool(re.search(r"Do not mix new and used cells", ts_)), "stabilise": bool(re.search(r"after initial stabilisation", ts_)),
           "typ_basis": bool(re.search(r"Typical values relative to cells stored up to one year at \+ 30°C max", ts_))}
    iii["x_pack"] = (iii["wh_nom"][0] / R["cand"]["35E"]["wh_nom"], iii["wh_nom"][1] / R["cand"]["35E"]["wh_nom"])
    iii["stuck"] = {"p_on": psel_["p_on"], "settle": (e4s_t + psel_["p_on"] / sh["g_series"][0], e4s_t + psel_["p_on"] / sh["g_series"][1]),
                    "spent_h": (psel_["slow"]["strings"] * psel_["e_string"] / psel_["p_on"], psel_["fast"]["strings"] * psel_["e_string"] / psel_["p_on"])}
    iii["demand_Wh"] = (psel_["slow"]["demand"], psel_["fast"]["demand"])
    apr = {"I": {"name": "(I) the 35E as ruled with local thermal management",
                 "added": ["a cooler in the sealed case for E3-O and E5 (on the input)", "a cooler with its own energy store for E3-S (zero power from the pack)",
                           "a storage heater with its own energy store for E4-S (a primary battery, thermostat, isolation)"],
                 "rows": {"LO-01a": "CONDITIONAL (T-H1)", "LO-01b": "NO COLLISION", "LO-01c": "NO COLLISION",
                          "LO-01d": "INCONCLUSIVE: a cooler of %.2f to %.2f W lifting the air %.1f to %.1f K" % (cc["cool"][("E3-O", 1.0)]["p_in"], cc["cool"][("E3-O", 0.5)]["p_in"], cc["lift"][("E3-O", 1.0)], cc["lift"][("E3-O", 0.5)]),
                          "LO-01e": "INCONCLUSIVE: a cooler of %.2f to %.2f W lifting the air %.1f to %.1f K" % (cc["cool"][("E5", 1.0)]["p_in"], cc["cool"][("E5", 0.5)]["p_in"], cc["lift"][("E5", 1.0)], cc["lift"][("E5", 0.5)]),
                          "LO-01f": "NEEDS ADDED ENERGY STORAGE (D-06)", "LO-01g": "NEEDS ADDED ENERGY STORAGE (D-06)", "LO-01h": "CONDITIONAL (the lot)"},
                 "changes_constraint": ["D-06: a second energy store for E3-S and E4-S (one pack, internal storage)"]},
           "II": {"name": "(II) a wide-temperature 18650 (the HL18650V class) in D-06's 4S3P, with the protection and gauge re-derived",
                  "added": [],
                  "rows": {"LO-01a": "CONDITIONAL (T-H1)", "LO-01b": "NO COLLISION", "LO-01c": "NO COLLISION",
                           "LO-01d": "CONDITIONAL (T-H1, the signed specification)", "LO-01e": "CONDITIONAL (T-H1, the signed specification)",
                           "LO-01f": "CONDITIONAL (the signed specification)", "LO-01g": "CONDITIONAL (the signed specification)",
                           "LO-01h": "CONDITIONAL (the signed specification)"},
                  "changes_constraint": ["D-06's 'about 145 Wh' (%.1f Wh nominal)" % R["cand"]["HL18650V"]["wh_nom"], "the cell selection's spend (cell_provenance)",
                                         "the cell-derived numbers of REQ-046 (charge 0 to 45 C, discharge -10 to 60 C) and REQ-077 (the cell maker's +60 C), restated to the new cell's signed limits with the cell"]},
           "III": {"name": "(III) the 35E with auxiliary thermal energy (latent storage, a primary-fed storage heater)",
                   "added": ["a phase-change store round the block", "a primary battery with a thermostat and isolation"],
                   "rows": {"LO-01a": "CONDITIONAL (T-H1)", "LO-01b": "NO COLLISION", "LO-01c": "NO COLLISION",
                            "LO-01d": "REJECTED (H1's window)", "LO-01e": "REJECTED at the conditioned corner (no fit)",
                            "LO-01f": "REJECTED within the pocket", "LO-01g": "NEEDS ADDED ENERGY STORAGE (D-06)", "LO-01h": "CONDITIONAL (the lot)"},
                   "changes_constraint": ["D-06: a second energy store (the primary battery)"]}}
    for a_ in apr.values():
        a_["rejected"] = sorted(k for k, v in a_["rows"].items() if v.startswith("REJECTED"))
        a_["needs_d06"] = sorted(k for k, v in a_["rows"].items() if "D-06" in v)
        a_["qualifies"] = not a_["rejected"] and not a_["needs_d06"]
    qual = [k for k, a_ in apr.items() if a_["qualifies"]]
    rec = min(qual, key=lambda k: len(apr[k]["added"])) if qual else None
    R["cmp"] = {"lim2": lim2, "lad2": lad2, "h1n2": h1n2, "u2_off": u2_off, "u2lo": u2lo, "u2_pick": u2_pick, "clear": clear, "m2": m2, "m2_unc": m2_unc,
                "i1": i1, "iii": iii, "apr": apr, "rec": rec, "w35": w35, "whl": whl}

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
    cm_ = R["cmp"]

    def cell_route(row, extra=""):
        v = cm_["m2"][row]
        parts = ["the cells at %.2f C against the page's %+.0f C (%.2f K)" % (v["peak"], v["limit"], v["m_limit"])]
        if "m_h1" in v:
            parts.append("%.2f K under the re-derived H1's no-act limit %.2f C" % (v["m_h1"], v["h1"]))
        if "m_u2" in v:
            parts.append("%.2f K under %s's lowest trip %.1f C (INFERRED)" % (v["m_u2"], cm_["u2_pick"], v["u2"]))
        return {"route": "(II) RECOMMENDED: a wide-temperature 18650 (the HL18650V class) in D-06's 4S3P with the protection and gauge re-derived (4d)",
                "status": "CONDITIONAL", "basis": "at the conditioned corner " + "; ".join(parts) + extra,
                "missing": "the maker's signed specification confirming the page's rows at the stored charge (the request is drafted), the owner's approval of D-06's restated energy and the spend; F2 as every approach"}
    pr_, pcr, prm_ = R["pcm_res"], R["pcm"], R["prim"]
    psel = prm_["configs"]["5S, -40 C curve (lower)"]
    spare = R["spare_L"]
    room_txt = "%.3f to %.3f L of room round the block (INFERRED)" % spare
    dec["LO-01d"] = {"decision": "OPEN", "evidence": ["MAKER", "MODELED", "INFERRED", "ASSUMPTION"], "bounded": True,
                     "cell_change": {"candidate": "HL18650V class", "taken": False, "owner_approval_required": True},
                     "routes": [{"route": "thermal design without added power or storage (fans, spreading, the calculated insulation, the coupling)", "status": "REJECTED",
                                 "basis": "the cells may sit 5 K over +55 C against a 6.63 to 19.22 K rise; the calculated insulation needs %.1f to %.1f mm against at most 2.66 mm; with the coupling the cells pass H1's reading at every corner, so the hot stop stops every module (E3-O's 'no shutdown')" % R["meas"]["ins_mm"],
                                 "missing": "none for these arrangements"},
                                {"route": "(III) added latent storage (Rubitherm RT57HC, figures favourable to the material)", "status": "REJECTED",
                                 "basis": "for the cells under +60 C alone it needs %.3f kg (%.3f L) at the best corner, inside the %s, and %.3f kg (%.3f L) at the worst, outside it; the complete E3-O pass needs the cells under H1's no-act limit of %.2f C with the chamber at %.0f C, a %.2f K window against the material's %.0f to %.0f C melting area" % (pr_["best"]["e3o_m"], pr_["best"]["e3o_L"], room_txt, pr_["worst"]["e3o_m"], pr_["worst"]["e3o_L"], R["h1_window"][1], R["h1_window"][0], R["h1_window"][1] - R["h1_window"][0], pcr["melt"][0], pcr["melt"][1]),
                                 "missing": "none against the present hot-stop ladder"},
                                {"route": "(I) powered cooling of the pack on the input", "status": "INCONCLUSIVE",
                                 "basis": "into the sealed case the worst corner's air reaches %.1f to %.1f C (COP 1.0 to 0.5) (rejected there) and the conditioned corner's %.1f to %.1f C for %.2f to %.2f W (INCONCLUSIVE: the input's spare power, and the air lifted onto the +70 C parts); the best corner holds the cells for %.2f to %.2f W; out through the pack's skin path only at the best corner" % (cool["E3-O"]["inside"][("worst", 1.0)]["air"], cool["E3-O"]["inside"][("worst", 0.5)]["air"], R["condc"]["cool"][("E3-O", 1.0)]["air"], R["condc"]["cool"][("E3-O", 0.5)]["air"], R["condc"]["cool"][("E3-O", 1.0)]["p_in"], R["condc"]["cool"][("E3-O", 0.5)]["p_in"], cool["E3-O"]["inside"][("best", 1.0)]["p_in"], cool["E3-O"]["inside"][("best", 0.5)]["p_in"]),
                                 "missing": "a cooler's maker sheet (load against lift, COP), the input's spare power during E3-O, the volume in the 6.38 mm east gap, T-H1's conductance (which corner holds)"},
                                cell_route("LO-01d")],
                     "acceptance": "E3-O with the pack fitted: every cell inside its limit for the 4 h, no shutdown, recovery to specification",
                     "gap": "(II): the signed specification and T-H1; (I) stands only near the best corner, with a cooler's sheet; F2 (Eaton). Next: the owner sends the drafted request; T-H1"}
    dec["LO-01e"] = {"decision": "OPEN", "evidence": ["MAKER", "MODELED", "INFERRED", "ASSUMPTION"], "bounded": True,
                     "cell_change": {"candidate": "HL18650V class", "taken": False, "owner_approval_required": True},
                     "routes": [{"route": "(III) added latent storage over Method 507.6's aggravated cycle (RT57HC, favourable figures)", "status": "INCONCLUSIVE" if pr_["best"]["e5_L"] <= spare[1] else "REJECTED",
                                 "basis": "the air's cycle mean is %.2f C (best) to %.2f C (worst); the cells stay under +60 C through the conditioning and ten cycles with %.3f kg (%.3f L) at the best corner, against %s, and need %.3f kg (%.3f L) at the conditioned corner and %.2f kg (%.2f L) at the worst" % (pr_["best"]["e5_mean_air"], pr_["worst"]["e5_mean_air"], pr_["best"]["e5_m"], pr_["best"]["e5_L"], room_txt, R["condc"]["e5_m"], R["condc"]["e5_L"], pr_["worst"]["e5_m"], pr_["worst"]["e5_L"]),
                                 "missing": "the enclosure's conductance (which corner holds), the pocket's actual room at the built stack, the plan owner's confirmation that E5 is Procedure II of Method 507.6 (MIL-STD-810H)"},
                                {"route": "(I) powered cooling on the input", "status": "INCONCLUSIVE",
                                 "basis": "into the sealed case the worst corner's air reaches %.1f to %.1f C (COP 1.0 to 0.5) (rejected there) and the conditioned corner's %.1f to %.1f C for %.2f to %.2f W (INCONCLUSIVE: the input's spare power, and the air lifted onto the +70 C parts); the best corner holds the cells for %.2f to %.2f W" % (cool["E5"]["inside"][("worst", 1.0)]["air"], cool["E5"]["inside"][("worst", 0.5)]["air"], R["condc"]["cool"][("E5", 1.0)]["air"], R["condc"]["cool"][("E5", 0.5)]["air"], R["condc"]["cool"][("E5", 1.0)]["p_in"], R["condc"]["cool"][("E5", 0.5)]["p_in"], cool["E5"]["inside"][("best", 1.0)]["p_in"], cool["E5"]["inside"][("best", 0.5)]["p_in"]),
                                 "missing": "as LO-01d's cooling route"},
                                cell_route("LO-01e", "; at the bound's worst corner (the enclosure under LO-01a's line) %.2f C, over both, so it carries T-H1's condition" % cm_["m2_unc"]["e5_peak"])],
                     "acceptance": "E5 with the pack fitted: every cell inside its limit through the dwells and the pack recovering its capacity",
                     "gap": "(II): the signed specification and T-H1 (1.06 K under the re-derived H1 at the conditioned corner); the plan owner's confirmation of Method 507.6 Procedure II. Next: as LO-01d"}
    dec["LO-01f"] = {"decision": "OPEN", "evidence": ["MAKER", "MODELED", "INFERRED", "ASSUMPTION"], "bounded": True,
                     "cell_change": {"candidate": "HL18650V class", "taken": False, "owner_approval_required": True},
                     "routes": [{"route": "the calculated insulation (no power in storage)", "status": "REJECTED",
                                 "basis": "24 h of hold from the most favourable start needs the pack's coupling under %.4f W/K, %.1f mm at k 0.02 with the cells' own heat capacity, against at most 2.66 mm" % (pas["LO-01f"]["g_max"], pas["LO-01f"]["ins_mm"]),
                                 "missing": "none for this arrangement"},
                                {"route": "(III) added latent storage (RT57HC, favourable figures)", "status": "REJECTED",
                                 "basis": "the cells stay under +60 C for the 24 h with %.3f kg (%.3f L) at the best corner and %.3f kg (%.3f L) at the worst, both beyond the %s, from the storage envelope's cold edge" % (pr_["best"]["e3s_m"], pr_["best"]["e3s_L"], pr_["worst"]["e3s_m"], pr_["worst"]["e3s_L"], room_txt),
                                 "missing": "none within D-06's pocket"},
                                {"route": "(I) powered cooling from a second energy store in storage (added storage under D-06)", "status": "INCONCLUSIVE",
                                 "basis": "into the sealed case the best corner's air reaches %.1f to %.1f C for %.2f to %.2f W of input (%.0f to %.0f Wh over 24 h); the worst corner has no equilibrium at COP 0.5" % (cool["E3-S"]["inside"][("best", 1.0)]["air"], cool["E3-S"]["inside"][("best", 0.5)]["air"], cool["E3-S"]["inside"][("best", 1.0)]["p_in"], cool["E3-S"]["inside"][("best", 0.5)]["p_in"], 24 * cool["E3-S"]["inside"][("best", 1.0)]["p_in"], 24 * cool["E3-S"]["inside"][("best", 0.5)]["p_in"]),
                                 "missing": "the owner's ruling on a second energy store under D-06, the source and cooler sheets, the volume, the other parts' storage limits at that air"},
                                cell_route("LO-01f", "; the present BQ7720700 (lowest trip %.1f C) would permit a destructive trip at +71 C" % R["ladder"]["U2_trip_lo"])],
                     "acceptance": "E3-S with the pack fitted: every cell inside its governing sheet's storage limit for the 24 h at the stored charge (a cell whose sheet covers +71 C, or the cells held under +60 C), the pack recovering its capacity",
                     "gap": "(II): the signed specification at the stored charge, U2 moved to a variant whose lowest trip clears +71 C; F2. (I) and (III) need added energy storage or room the pocket lacks. Next: as LO-01d"}
    dec["LO-01g"] = {"decision": "OPEN", "evidence": ["MAKER", "MODELED", "INFERRED", "ASSUMPTION"], "bounded": True,
                     "cell_change": {"candidate": "HL18650V class", "taken": False, "owner_approval_required": True},
                     "routes": [{"route": "the calculated insulation", "status": "REJECTED",
                                 "basis": "needs the pack's coupling under %.4f W/K, %.1f mm at k 0.02, against at most 2.66 mm" % (pas["LO-01g"]["g_max"], pas["LO-01g"]["ins_mm"]),
                                 "missing": "none for this arrangement"},
                                {"route": "added latent storage freezing above the -20 C floor", "status": "INCONCLUSIVE",
                                 "basis": "no maker's sheet of a material freezing between -20 and -10 C is held",
                                 "missing": "such a sheet"},
                                {"route": "a heater fed by the pack itself (case i)", "status": "REJECTED",
                                 "basis": "it discharges the cells (setpoint %.2f C); in REQ-025's stored state the gauge's shutdown turns its FETs off (SLUUAQ3A 5.4.2), so it has no protected path; its durations (%.1f to %.1f h) are model sensitivities, not the basis" % ((sh["set_pack"],) + sh["dur_h_range"]),
                                 "missing": "none within REQ-025"},
                                {"route": "(III) a heater fed by a primary battery through the existing mat (case i; Saft LSH 20; ADDED ENERGY STORAGE, a proposal under D-06, not adopted)", "status": "INCONCLUSIVE",
                                 "basis": "5S strings driving the mat direct: %d to %d cells (%.1f to %.1f kg, %.2f to %.2f L of cells, %.0f to %.0f Wh nominal, %.1f to %.1f times the pack's), %.1f to %.1f h of hold with the %.0f %% reserve kept, against %s; the maker recommends storage at +%.0f C at most against the kit's +%.0f C envelope; F2 at about -30 C is a separate obstacle" % (psel["slow"]["cells"], psel["fast"]["cells"], psel["slow"]["kg"], psel["fast"]["kg"], psel["slow"]["L"], psel["fast"]["L"], cm_["iii"]["wh_nom"][0], cm_["iii"]["wh_nom"][1], cm_["iii"]["x_pack"][0], cm_["iii"]["x_pack"][1], psel["fast"]["dur_h"], psel["slow"]["dur_h"], 100 * prm_["reserve_tot"], room_txt, cm_["iii"]["st_max"], cm_["iii"]["st_env"]),
                                 "missing": "the owner's ruling on a second energy store under D-06 (one pack, internal storage), Saft's answer on storage above +30 C, a place in the case (Layer 7), a thermostat's sheet, the in-pack gradient, the minimum capacity at -33 C, the transport classification with the pack (D-04), F2 (Eaton)"},
                                cell_route("LO-01g", "; the cell itself holds no heater and needs no energy in storage")],
                     "acceptance": "E4-S with the pack fitted: every cell inside its storage row for the 24 h (or a cell whose sheet covers -33 C), the pack recovering its capacity",
                     "gap": "(II): the signed specification at the stored charge; F2 at -33 C. The fallback (III) is added energy storage (%.2f to %.2f L of primary cells outside the pocket) needing the owner's ruling under D-06. Next: as LO-01d; Eaton on F2" % (psel["slow"]["L"], psel["fast"]["L"])}
    dec["LO-01h"] = {"decision": "CONDITIONAL", "evidence": ["MAKER"], "bounded": True, "cell_change": None,
                     "routes": [{"route": "procurement", "status": "CONDITIONAL", "basis": "Ver. 1.1 covers both rows", "missing": "the lot's revision"}],
                     "acceptance": "the bought lot's sheet covers -20 C for three months and +25 C for a year (BAT-F09); E4-T at the governing floor",
                     "gap": "the purchase record"}
    R["dec"] = dec
    # an owner decision is forced only where every route of a row is rejected on bounded evidence
    R["forced_rows"] = sorted(k for k, d in dec.items() if d["decision"] == "OPEN" and d["routes"] and all(r["status"] == "REJECTED" for r in d["routes"]))
    R["owner_decision_required"] = bool(R["forced_rows"])
    R["classes"] = CLASSES
    R["u01"] = u01(R, pb)
    R["saft"] = saft_sheet()
    R["u01c"] = u01c(R, pb)
    R["u01_classes"] = ("MAKER", "MAKER-PAGE", "INFERRED", "ASSUMPTION", "SESSION")
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
    w("   So the measure meets the cell criteria on the pack only: on shore the cells reach %.2f C, past the +59 C abort, and the air %.2f C (check 2). The air criteria stay the" % (m["a_input_worst"][1], m["a_input_worst"][0]))
    w("   enclosure's (3a). It is a partial fallback for the cells, never a substitute for T-H1's conductance.")
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
        w("   %.1f mm of insulation at k %.2f W/mK (ASSUMPTION) round the block with the cells' own heat capacity, against 0.77 to 2.66 mm of room: that arrangement is rejected (today %.2f K); added storage is 3n."
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
    w("      At the fast corner the %.2f W into the cells exceeds the mat's own %.1f W at 12 V (MAKER): a further inability of the present mat to hold that setpoint." % (rf["pm_pack"], S["mat"]["power"]))
    w("      MODEL SENSITIVITY, not usable energy: %.0f %% of charge (Ver. 1.1 3.13) less the %.0f %% reserve, aged to %.0f %% (SC-23), at the nominal voltage, times a cold factor between %.2f and 1.0"
      % (100 * sh["soc_store"], 100 * sh["reserve"], 100 * sh["age"], sh["cold_f"][0]))
    w("      gives %.1f to %.1f Wh, %.1f to %.1f h of the %.0f h, a balance of %.1f to %.1f Wh; from a full charge %.1f to %.1f h. MAKER 7.5's point is a full standard charge, a 3 h"
      % (sh["e_use_stored"] + sh["dur_h_range"] + (R["g"]["hours"],) + sh["reserve_after_Wh"] + sh["dur_full_h_range"]))
    w("      temperature change and 3.4 A to 2.65 V; it does not give this regime. Missing: the terminal energy over the partial-charge voltage curve, the cutoff, the temperature history.")
    w("      The rejection does not rest on these figures: in the stored state the gauge is in shutdown, '%s' (MAKER, SLUUAQ3A 5.4.2), so the pack-fed heater" % sh["shutdown_fets_off"])
    w("      has no protected path unless the gauge stays awake, a change of REQ-025's stored state.")
    w("      Scope: not available at REQ-025's stored state (its shutdown); the durations above are sensitivities, not a basis either way.")
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
    w("3i Powered cooling (a thermoelectric stage; COP %s ASSUMPTION, no module's sheet held). Corrected balance (check 2): heat pumped out of the block into the inside air returns to"
      % " to ".join("%.1f" % v for v in COP))
    w("   the air it came from, so the air gains only the cooler's input Q_c/COP: G_e a = q + G_b (a - d)/COP, an equilibrium wherever G_e > G_b/COP.")
    for k in ("E3-O", "E5", "E3-S"):
        r = co[k]
        parts = []
        for (cname, cop), v in sorted(r["inside"].items()):
            parts.append("%s COP %.1f: %s" % (cname, cop, "no equilibrium" if v is None else "air %.1f C, load %.2f W, input %.2f W" % (v["air"], v["qc"], v["p_in"])))
        w("   %-5s hold %.2f C, into the inside air: %s" % (k, r["t_hold"], "; ".join(parts)))
    wa = [v["air"] for k in ("E3-O", "E5") for (c_, cp_), v in co[k]["inside"].items() if c_ == "worst" and v]
    bd = [(v["air"] - (R["d"]["air_lo"] if k == "E3-O" else R["e"]["air_lo"]), v["p_in"]) for k in ("E3-O", "E5") for (c_, cp_), v in co[k]["inside"].items() if c_ == "best" and v]
    R["cool_summary"] = {"worst_air": (min(wa), max(wa)), "best_dair": (min(b[0] for b in bd), max(b[0] for b in bd)), "best_pin": (min(b[1] for b in bd), max(b[1] for b in bd))}
    cs = R["cool_summary"]
    w("   So, into the sealed case: at the worst corners of E3-O and E5 the air reaches %.1f to %.1f C at COP 0.5 to 1.0, past every part limit of OPERATING-ENVELOPE.md section 2"
      % cs["worst_air"])
    w("   (F2 +60 C, the SGP41 +55 C); at their best corners the cells can be held for %.2f to %.2f W of input with the air %.2f to %.2f K above its uncooled value (which already passes F2"
      % (cs["best_pin"] + cs["best_dair"]))
    w("   and the SGP41 on its own).")
    for k in ("E3-O", "E5", "E3-S"):
        r = co[k]
        w("   %-5s with the air unchanged (heat sent out of the case): load %.2f to %.2f W; a path out needs %.3f to %.3f W/K (COP 1.0), %.3f to %.3f W/K (COP 0.5), hot side at most %.0f K over the chamber"
          % ((k,) + r["qc"] + r["g_out_need"][1.0] + r["g_out_need"][0.5] + (HOT_RISE,)))
    w("   The pack's own skin path (3b) is %.3f to %.3f W/K: enough only at E3-O's best corner. E3-S has no input: %.0f to %.0f Wh over 24 h from a separate source."
      % (co["skin"] + (co["E3-S"]["Wh"][1.0][0], co["E3-S"]["Wh"][0.5][1])))
    w("   Result: rejected into the sealed case at the worst corners for COP up to 1.0; at the best corners and for a higher COP INCONCLUSIVE, the inputs missing: a cooler's maker")
    w("   sheet (load against lift, COP), the input's spare power (L4-E4's 4.70 A limit less the kit's load, not derived here), the volume (a module and its spreader in a 6.38 mm gap).")
    kd, p13 = R["kd"], R["p13"]
    w("3j PWR-F12's key-down: %.0f A for %.0f s (%.1f A a cell) from C1's +%.0f C warms the cells %.2f to %.2f K adiabatically (MODELED), to %.2f to %.2f C, inside +60 C."
      % (R["tpx"]["p13_kd"][1], R["tpx"]["p13_kd"][2], kd["i_cell"], kd["from"], kd["rise"][0], kd["rise"][1], kd["to"][0], kd["to"][1]))
    w("3k P13's hour at %.0f A (%.2f A a cell): the cells' own %.2f to %.2f W, a steady rise of %.1f to %.1f K over the block's film and %.1f to %.1f K adiabatic over the hour (MODELED):"
      % ((R["tpx"]["p13_a"], p13["i_cell"]) + p13["w"] + p13["steady"] + p13["adiabatic"]))
    w("   'the block at the pack's hot limit' holds the cells inside +60 C only if the limit is set at the cell surface and the chamber runs that much cooler (a definition item for P13's owner).")
    lev = R["e3l_levels"]
    w("3l E3-L's levels at the bound's lowest lid-closed conductance (MODELED): " + "; ".join("+%.0f C: %s, air %.2f C, cells %.2f C" % (t, v[0], v[1], v[2]) for t, v in sorted(lev.items())))
    w("")
    # ---------------------------------------------------------------- 3n: part 2, the open rows' next bounded actions
    pr_, pcr, sp_ = R["pcm_res"], R["pcm"], R["spare_L"]
    w("3n The open rows' next bounded actions, from makers' documents and without a purchase (the final round).")
    w("   Room round the block beyond the 1.0 mm minimums (INFERRED, CASE-MARGINS and SHORTLIST): %.3f L at the worst stack, %.3f L as designed." % sp_)
    w("   Latent storage, MAKER (Rubitherm RT57HC, `v2/vendor/battery/pcm/`): melting area %.0f to %.0f C, %.0f kJ/kg +-%.1f %% (latent and sensible), cp %.0f J/kgK, %.1f kg/l solid."
      % (pcr["melt"][0], pcr["melt"][1], pcr["cap"] / 1000.0, 100 * pcr["tol"], pcr["cp"], pcr["rho"]))
    w("   Taken favourable to the material: %.0f kJ/kg all latent at the top of its melting area (%.0f C), the solid density, no container, perfect contact with the cells."
      % (pcr["L"] / 1000.0, pcr["Tm"]))
    ep = R["e5_profile"]
    w("   (b) E5: TEST-PLAN cites '507' with Procedure II's levels; MIL-STD-810H Method 507.6 (transcribed, `v2/vendor/standards/mil-std-810h-method-507-6.md`) gives a %.0f C conditioning"
      % ep["cond"])
    w("      for at least 24 h, then %d cycles of %s (h, C), RH 95 %%, then a return to %.0f C until stable; the cycle's mean is %.2f C. Which procedure E5 means is the plan owner's to confirm."
      % (ep["cycles"], ", ".join("%.0f h %.0f" % kv for kv in ep["knots"]), ep["cond"], ep["mean"]))
    for cname in ("best", "worst"):
        r_ = pr_[cname]
        w("      %-5s corner (the heat stage on shore, lid open): air mean %.2f C; without storage the cells peak at %.2f C; they stay under +60 C with %s"
          % (cname, r_["e5_mean_air"], r_["e5_peak_none"], "no storage" if r_["e5_m"] == 0 else ("more than 20 kg" if r_["e5_m"] is None else "%.3f kg (%.3f L)" % (r_["e5_m"], r_["e5_L"]))))
    if pr_["best"]["e5_L"] <= sp_[1]:
        w("      So: at the best corner a fit inside the designed room (%.3f L); at the worst no fit. INCONCLUSIVE on the conductance and the built room." % sp_[1])
    else:
        w("      So: no fit at any corner, the best corner's %.3f L over the designed room's %.3f L: rejected within the pocket on figures favourable to the material." % (pr_["best"]["e5_L"], sp_[1]))
    hw = R["h1_window"]
    w("   (c) LO-01d, E3-O's 4 h at +%.0f C from a kit stabilised at the chamber: without storage the cells peak at %.2f C (best) and %.2f C (worst); under +60 C with"
      % (R["d"]["amb"], pr_["best"]["e3o_peak_none"], pr_["worst"]["e3o_peak_none"]))
    w("      %.3f kg (%.3f L, inside the room) at the best corner and %.3f kg (%.3f L, outside it) at the worst. The complete pass ('no shutdown') needs the cells under H1's no-act"
      % (pr_["best"]["e3o_m"], pr_["best"]["e3o_L"], pr_["worst"]["e3o_m"], pr_["worst"]["e3o_L"]))
    w("      limit %.2f C with the chamber already at %.0f C: a %.2f K window against the material's %.0f to %.0f C melting area. Rejected against the present hot-stop ladder."
      % (hw[1], hw[0], hw[1] - hw[0], pcr["melt"][0], pcr["melt"][1]))
    w("   LO-01f, E3-S's 24 h at +%.0f C from the storage envelope's cold edge: under +60 C with %.3f kg (%.3f L) at the best corner and %.3f kg (%.3f L) at the worst: beyond the room."
      % (R["f"]["amb"], pr_["best"]["e3s_m"], pr_["best"]["e3s_L"], pr_["worst"]["e3s_m"], pr_["worst"]["e3s_L"]))
    w("   LO-01g: no maker's sheet of a material freezing between -20 and -10 C is held: INCONCLUSIVE.")
    w("   Each store's history (no fresh store is assumed): E3-O starts from the kit stabilised at +%.0f C with the material solid at the bottom of its melting area (favourable:"
      % R["d"]["amb"])
    w("      its partial melting below 55 C is not counted); E5's store is carried through the conditioning and all %d cycles in one run, refreezing only as the cycle's 30 C part"
      % R["e5_profile"]["cycles"])
    w("      allows; E3-S starts at the storage envelope's cold edge (favourable). Once the store is spent the cells follow the no-storage response: E3-O to %.2f to %.2f C, E5 to"
      % (pr_["best"]["e3o_peak_none"], pr_["worst"]["e3o_peak_none"]))
    w("      %.2f to %.2f C, E3-S to %.2f to %.2f C. Between required exposures the store resets only below 55 C, which each test's own return to ambient provides; a kit taken from"
      % (pr_["best"]["e5_peak_none"], pr_["worst"]["e5_peak_none"], pr_["best"]["e3s_peak_none"], pr_["worst"]["e3s_peak_none"]))
    w("      one hot exposure to the next without it starts with a spent store.")
    ls_, pm2 = R["lsh"], R["prim"]
    w("   (a) LO-01g's primary battery: ADDED ENERGY STORAGE, a proposal under D-06, bounded here and not adopted. MAKER (Saft LSH 20, Li-SOCl2, D size, Document 31015-2-0426,")
    w("      held back): %.0f Ah under %.0f mA at +20 C, %.1f V, at most %.1f A continuous,"
      % (ls_["c_nom"], ls_["c_nom_ma"], ls_["v_nom"], ls_["i_cont"]))
    w("      %.0f to +%.0f C, %.1f x %.2f mm, %.0f g, about %.1f g of lithium, %s, self-discharge '%s'. Its curves are typical, not minimum (the maker's own words: %s);"
      % (ls_["t_op"][0], ls_["t_op"][1], ls_["d"], ls_["h"], ls_["g"], ls_["li"], ls_["un"], re.sub(r"\s+", " ", ls_["self"]), ls_["typical"]))
    w("      read by eye (INFERRED, `inputs/saft-lsh20-curves-read-2026-10-01.json`) at -40 C and -20 C, interpolated in current and temperature.")
    w("      One boundary: the string drives the existing mat (%.1f ohm, MAKER 7.5 W at 12 V) through a thermostat, no regulator; the demand is the series path times the hold's rise." % pm2["r_mat"])
    w("      Setpoint: the -20 C floor plus %s = %.1f K (ASSUMPTION, no thermostat part held); reserve kept: %s = %.0f %% (ASSUMPTION)."
      % (" + ".join("%s %.1f K" % kv for kv in pm2["allow"].items()), pm2["allow_tot"], " + ".join("%s %.0f %%" % (k, 100 * v) for k, v in pm2["reserve"].items()), 100 * pm2["reserve_tot"]))
    for cfg, row in pm2["configs"].items():
        w("      %-30s %.0f mA on, %.3f V a cell, %.2f Ah, %.1f W on, %.1f Wh a string; slow corner: %.2f W average (duty %.2f), %d strings, %d cells, %.1f kg, %.2f L, %.1f h, balance %.1f Wh;"
          % (cfg, row["i_ma"], row["v"], row["cap"], row["p_on"], row["e_string"], row["slow"]["p_avg"], row["slow"]["duty"], row["slow"]["strings"], row["slow"]["cells"], row["slow"]["kg"], row["slow"]["L"], row["slow"]["dur_h"], row["slow"]["reserve_Wh"]))
        w("      %-30s fast corner: %.2f W average (duty %.2f%s), %d strings, %d cells, %.1f kg, %.2f L, %.1f h, balance %.1f Wh"
          % ("", row["fast"]["p_avg"], row["fast"]["duty"], ", above 1: the mat's on-power cannot carry it" if row["fast"]["duty"] > 1 else "", row["fast"]["strings"], row["fast"]["cells"], row["fast"]["kg"], row["fast"]["L"], row["fast"]["dur_h"], row["fast"]["reserve_Wh"]))
    psel = pm2["configs"]["5S, -40 C curve (lower)"]
    w("      Bound: 5S on the -40 C curve (4S's on-power falls under the fast corner's demand). %d to %d cells, %.1f to %.1f kg, %.2f to %.2f L of cells, %.1f to %.1f h with the reserve kept."
      % (psel["slow"]["cells"], psel["fast"]["cells"], psel["slow"]["kg"], psel["fast"]["kg"], psel["slow"]["L"], psel["fast"]["L"], psel["fast"]["dur_h"], psel["slow"]["dur_h"]))
    w("      Fit: the cells alone exceed the pocket's %.3f L, so they sit elsewhere in the case: Layer 7's free volume is the missing fact. F2 sits at about -30 C, below its -20 C floor:" % sp_[1])
    w("      a separate obstacle (Eaton, or the heated zone over board P). Sequence: the pack to its ex-factory charge and the gauge to shutdown (REQ-025); the storage heater armed; its")
    w("      thermostat on the coldest cell closes at the setpoint and connects the string to the mat, isolated from the kit's 12 V feed (a circuit item for the generator owners); the")
    w("      pack never discharges; disarmed at the end of storage. Scope: E4-S's 24 h at -33 C from a warm stored kit; not a cold start, not in use.")
    ii_ = R["cmp"]["iii"]
    w("      Against D-06: %d to %d cells hold %.0f to %.0f Wh nominal (MAKER, 47 Wh a cell), %.1f to %.1f times the pack's %.1f Wh, and %.0f to %.0f g of lithium: a second energy"
      % (psel["slow"]["cells"], psel["fast"]["cells"], ii_["wh_nom"][0], ii_["wh_nom"][1], ii_["x_pack"][0], ii_["x_pack"][1], R["cand"]["35E"]["wh_nom"], ii_["li_g"][0], ii_["li_g"][1]))
    w("      store beside D-06's one pack. Calling it a heater supply does not settle its compatibility with D-06 (one 4S3P pack, internal storage, no external battery): adopting it is the owner's.")
    w("      Bounded per measure (MAKER where quoted): output at the cold load from the typical curves above; startup: the pulse figures hold 'after initial stabilisation' (%s) and no"
      % ii_["stabilise"])
    w("      figure is given at -33 C after storage (missing); ageing: under 3 %% a year at +20 C, its typical values 'relative to cells stored up to one year at + 30°C max' (%s), the"
      % ii_["typ_basis"])
    w("      recommended storage at most +%.0f C against the kit's envelope to +%.0f C, E3-T's +58 C and E3-S's +71 C, so its energy after storage in the kit is unsupported (Saft's answer"
      % (ii_["st_max"], ii_["st_env"]))
    w("      missing); replacement as a set ('Do not mix new and used cells': %s) every %.0f years (ASSUMPTION); unintended charging: 'Do not recharge' (%s), so the string reaches the"
      % (ii_["no_mix"], REPLACE_Y, ii_["no_recharge"]))
    w("      mat only through a blocking path the kit's 12 V feed cannot back-drive (two series diodes, a circuit draft, no standard held); fit: outside the pocket (above).")
    w("      The three cases: (i) keeping a warm pack is its job; (ii) a pack already cold-soaked is rewarmed only from this store, 0.133 to 0.183 Wh per K (3g); (iii) lost control:")
    w("      with the store spent or the thermostat failed open the cells pass -20 C 0.30 to 1.09 h later (3g); failed closed, the mat runs at %.1f W, the cells settle at %.1f to %.1f C"
      % (ii_["stuck"]["p_on"], ii_["stuck"]["settle"][1], ii_["stuck"]["settle"][0]))
    w("      (inside their storage row) and the store is spent in %.1f to %.1f h." % ii_["stuck"]["spent_h"])
    cc_ = R["condc"]
    w("3o The conditioned corner. Every approach carries LO-01a's condition, T-H1 reading at least %.3f W/K in each lid state; with the kit's conductance at that floor and every"
      % cc_["G_e"])
    w("   other parameter at its worst (the heat stage on shore, the lowest heat capacities, the fastest block), on the same profiles as 3n: E3-O's air settles at %.2f C and the cells"
      % cc_["e3o_air_ss"])
    w("   peak at %.2f C in the 4 h; E5's air averages %.2f C over the cycle and the cells peak at %.2f C (MODELED)." % (cc_["e3o_peak"], cc_["e5_air_mean"], cc_["e5_peak"]))
    i1_ = R["cmp"]["i1"]
    w("   (I) at this corner: a cooler into the sealed case holding the cells at H1's reading takes %.2f to %.2f W (E3-O, COP 1.0 to 0.5) and %.2f to %.2f W (E5) and lifts the air to"
      % (cc_["cool"][("E3-O", 1.0)]["p_in"], cc_["cool"][("E3-O", 0.5)]["p_in"], cc_["cool"][("E5", 1.0)]["p_in"], cc_["cool"][("E5", 0.5)]["p_in"]))
    w("   %.1f to %.1f C, %.1f to %.1f K over the uncooled %.2f C (E3-O) and %.2f C (E5's 60 C dwell), onto and past the +70 C parts of OPERATING-ENVELOPE.md section 2 (the SA868,"
      % (min(v["air"] for v in cc_["cool"].values()), max(v["air"] for v in cc_["cool"].values()), min(cc_["lift"].values()), max(cc_["lift"].values()), cc_["air_unc"]["E3-O"], cc_["air_unc"]["E5"]))
    w("   the AW7915-AED cards, the LimeSDR, the Xenarc) and at COP 0.5 the CM5's +85 C: INCONCLUSIVE on the input's spare power and on that cost to other functions; latent storage")
    w("   needs %.3f L (E3-O) and %.3f L (E5) against at most %.3f L: rejected. Near the best corner (%.2f W/K with the other parameters favourable) %.2f to %.2f W of input holds the cells (3i)."
      % (cc_["e3o_L"], cc_["e5_L"], sp_[1], cc_["g_best"], i1_["best_in"][0], i1_["best_in"][1]))
    w("   Endurance, were the cooler fed by the pack (E3-O and E5 feed it from the input): %.2f h without it at PS-IDLE-SPEC, %.2f to %.2f h at the best corner's input, %.2f to %.2f h at"
      % (i1_["endu_none"], i1_["endu_best"][0], i1_["endu_best"][1], i1_["endu_cond"][0], i1_["endu_cond"][1]))
    w("   this corner's.")
    w("   Outside FEA-008 and common to every approach: at this corner the uncooled air settles at %.2f C in E3-O and tends to %.2f C in E5's 60 C dwell, at or past the +70 C"
      % (cc_["air_unc"]["E3-O"], cc_["air_unc"]["E5"]))
    w("   parts' limits (the SA868, the AW7915-AED cards, the LimeSDR, the Xenarc): a finding for the kit's thermal owner (section 7).")
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
    bd_ = R["beyond"]
    lf_, lt_, ux_ = bd_["lfp"], bd_["lto"], bd_["ux"]
    w("4c Cells beyond the held set (the owner's instruction of 2 October 2026; the makers' own published lines, `inputs/cells-beyond-held-2026-10-02.json`):")
    w("   LiFePO4, Lithium Werks APR18650M1B (MAKER product page; its data sheet sits behind a registration form): %.1f V, %.2f Ah minimum, %.2f Wh, discharge %.0f to %.0f C, charge"
      % (lf_["v"], lf_["c_min"], lf_["wh"], lf_["dis"][0], lf_["dis"][1]))
    w("   %.0f to %.0f C, storage %.0f to %.0f C (no duration), %.0f A continuous, %.1f g. As 4S3P: %.1f Wh nominal (%.0f %% against %.1f), %.1f V nominal with a %.1f V charge a cell,"
      % (lf_["chg"][0], lf_["chg"][1], lf_["st"][0], lf_["st"][1], lf_["i_cont"], lf_["g"], lf_["pack_wh_nom"], 100.0 * (lf_["pack_wh_nom"] / R["cand"]["35E"]["wh_nom"] - 1.0), R["cand"]["35E"]["wh_nom"], lf_["v4s"], lf_["v_chg"]))
    w("   so the charger's voltage, the gauge's chemistry and U2's thresholds all change; it covers LO-01g (%s) and no hot margin (LO-01d %s, LO-01e %s, LO-01f %s): set aside."
      % (lf_["meets"]["LO-01g"], lf_["meets"]["LO-01d"], lf_["meets"]["LO-01e"], lf_["meets"]["LO-01f"]))
    w("   Lithium titanate, Toshiba SCiB (MAKER brochure, held back): prismatic cells from %.1f Ah (%s), %s V, 'as low as %.0f°C': not an 18650, and 4S would sit near %.1f V;"
      % (lt_["smallest_ah"], lt_["dims"].replace(" × ", " x "), " and ".join("%.1f" % v for v in lt_["v"]), lt_["low"], 4 * max(lt_["v"])))
    w("   it leaves D-06's 4S3P of 18650 cells: set aside.")
    w("   Wide-temperature lithium ion, UltraXel HL18650T (MAKER flyer, images only, held back): %.0f mAh minimum, discharge %.0f to %.0f C, storage rows stated: %s; its text claims"
      % (1000 * ux_["c_min"], ux_["dis"][0], ux_["dis"][1], ux_["storage_rows"]))
    w("   '%s' while its own chart (read by eye) shows %.2f of %.2f Ah (%.0f %%) after 1120 h at 80 C and 4.1 V; %.1f Wh as 4S3P (%.0f %%): set aside, a second"
      % (ux_["retain_claim"], ux_["chart"]["recovery_Ah"], ux_["chart"]["initial_Ah"], ux_["chart_pct"], ux_["pack_wh_nom"], 100.0 * (ux_["pack_wh_nom"] / R["cand"]["35E"]["wh_nom"] - 1.0)))
    w("   maker's statement of the class's discharge range. No 18650 with a maker's signed specification covering +71 C and -33 C storage was found; the HL18650V's page (Yichun")
    w("   Topwell Power) carries the class's only stated storage rows.")
    w("")
    w("4d One bounded comparison of three complete approaches on the same profiles (the conditioned corner of 3o for the hot margins; E3-S, E4-S and the storage envelope as stated).")
    for line in comparison_lines(R):
        w(("   " + line) if line else "")
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
    w("Open engineering obligations: LO-01d, LO-01e, LO-01f, LO-01g, each with the recommended route (II) CONDITIONAL on named facts (above); none has every route rejected.")
    cm_ = R["cmp"]
    w("RECOMMENDATION (4d): %s, the least complex approach with a defensible basis: no row rejected, no added energy storage, no added subsystem. A recommendation, not taken:"
      % cm_["apr"][cm_["rec"]]["name"])
    w("   no cell change and no spend now. The 30Q6 is not recommended (it moves no margin row on its own sheet, misses LO-01h's year at its 23 C and costs %.1f %% of the energy)."
      % (-100.0 * (R["cand"]["30Q6"]["usable_wh"] / R["cand"]["35E"]["usable_wh"] - 1.0)))
    w("OWNER DECISION: none is forced (rows with every route rejected: %s). The recommendation needs the owner for two things outside the session's authority:"
      % (", ".join(R["forced_rows"]) or "none"))
    w("   (1) now: sending the drafted request for the signed specification to Yichun Topwell Power (clarification/topwell-hl18650v.txt), since the session contacts no outside party;")
    w("   (2) once that specification confirms the page's rows at the stored charge: approving the cell change inside D-06's 4S3P, which restates D-06's 'about 145 Wh' to about %.0f Wh"
      % R["cand"]["HL18650V"]["wh_nom"])
    w("   nominal (%.1f Wh usable, %.1f %% less) and, with the cell, the cell-derived numbers of REQ-046 (its windows) and REQ-077 (its +60 C) to the new cell's signed limits, and"
      % (R["cand"]["HL18650V"]["usable_wh"], -100.0 * (R["cand"]["HL18650V"]["usable_wh"] / R["cand"]["35E"]["usable_wh"] - 1.0)))
    w("   its spend (USD %.2f a cell at the marketplace price, about USD %.0f a pack). A missing cell rating is a component limitation plus" % (R["price_hl"], 12 * R["price_hl"]))
    w("   missing feasibility evidence, not a contradiction between owner requirements (D-29, D-36, cell_provenance).")
    w("CONSOLIDATED (section 10, 2 October 2026): the route resting on published makers' evidence is (II) with the Saft MP 176065 xtd as a 4S1P pack; the HL18650V")
    w("   stays its higher-energy alternative on a vendor answer; the owner's items there replace the two above for that route.")
    w("THE THERMAL ARCHITECTURE CRITERION (criterion 1, a defensible feasibility basis for every mandatory function): not met by this record. Every LO row now has a route that is")
    w("   not rejected, and LO-01d to LO-01g rest on a maker's product page until the signed specification arrives; FEA-008 stays open as the session's engineering obligation.")
    w("Possible later changes (none proposed now; each would be the owner's only once every route of a row within the requirements is shown unavailable on bounded evidence):")
    for line in later_lines(R):
        w("   " + line)
    w("5b The corrections of check 2 and what each changes (minor only where the decision and the acceptance margins stay as they were):")
    for line in correction_lines(R):
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
    w("The gauge's thresholds stay inside REQ-046's windows (OTC %.1f, OTD %.1f, UTC %.1f, UTD %.1f C; THERMAL-COORDINATION.md section 5): this record moves none; under (II) the windows and the ladder move with the cell (4d). With the coupling the block"
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
    w("")
    for line in u01_lines(R):
        w(line)
    w("")
    for line in u01c_lines(R):
        w(line)
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
         "approaches": ["as C01, with the front end's loss on shore counted (3a)", "charge state: the pack's charge at E3-A's start is not stated by TEST-PLAN (a named missing input)"],
         "result": "CREDIBLE, CONDITIONAL on T-H1 (3a), both lid states"},
        {"id": "C03", "lo": "LO-01a", "cond": "E3-A's +%.0f C point, %.0f h, three loaded modules on shore (D-02b's charge point)" % (tpx["e3a"][3], tpx["e3a"][4]), "zero_power": False,
         "amb": "+%.0f C" % tpx["e3a"][3], "dur": "%.0f h" % tpx["e3a"][4], "cfg": "deployed, lid open, on shore, the stage C1 selects",
         "limit": "+%.0f C; no charge start above T3 %.0f C" % (lim["discharge"][1], 42.0), "power": "the input",
         "gap": "none for the cells: C1 sheds on measured temperatures; whether a charge starts is recorded (the charge ceiling of three loaded modules lies below +25 C, LO-01c)",
         "approaches": ["none needed"], "result": "NO GAP (recorded, not judged on charging)"},
        {"id": "C04", "lo": "LO-01a", "cond": "E3-L's lower levels (%s)" % ", ".join("+%.0f C" % t for t in tpx["e3l_levels"][:-1]), "zero_power": False,
         "amb": ", ".join("+%.0f C" % t for t in tpx["e3l_levels"][:-1]), "dur": "4 h each, on the pack then on shore", "cfg": "deployed closed-lid, the reduced mode or its heat stage",
         "limit": "+%.0f C; the SGP41's +%.0f C air" % (lim["discharge"][1], tpx["sgp41"]), "power": "the pack, then the input",
         "gap": "none at the bound's worst corner: " + "; ".join("+%.0f C %s, cells %.2f C" % (t, v[0], v[2]) for t, v in sorted(R["e3l_levels"].items()) if t < tpx["e3l_levels"][-1]),
         "approaches": ["none needed",
                        "mapped: E3-L is %s, and %s; the levels' steady states above apply once the reduced mode runs (INFERRED: the start is shorter than the 4 h level)" % (tpx["e3l_start"], tpx["e3l_lid"]),
                        "charge state: the pack's charge at each level's start is not stated by TEST-PLAN (a named missing input)"],
         "result": "NO GAP"},
        {"id": "C05", "lo": "LO-01a", "cond": "E3-H's stepped run beyond the envelope (a protection test)", "zero_power": False,
         "amb": "from +%.0f C by %.0f K an hour to at most +%.0f C" % tpx["e3h"], "dur": "until H1 and then H2 have acted", "cfg": "lid closed, the heat stage, pack fitted, on shore then on the pack",
         "limit": "no cell at +%.0f C before H1 and H2 act; no permanent protection" % tpx["abort"], "power": "the input, then the pack",
         "gap": "none for the cells: past H2 the kit's heat stops and the cells approach the chamber's at most +%.0f C (quasi-static at 2 K an hour against time constants of hours, INFERRED); whether H2 is reached depends on the minimum load's heat, not modelled (P15 forces it)" % tpx["e3h"][2],
         "approaches": ["the hot stop itself",
                        "mapped: at +40 C lid closed the level is held until the hot stop has acted or its %s h have passed; the run is repeated with the sensor controller held in reset, when board B's TMP117 acts at +%.1f C (shed) and +%.1f C (shutdown), released at +%.1f C" % (tpx["e3h_hold"], tpx["tmp117"][0], tpx["tmp117"][1], tpx["tmp117_rel"]),
                        "restart: the heat stage's module returns once the hottest cell reads +%.1f C or less and %.0f minutes have passed; after H2 MAIN restarts it with no module raised above +%.1f C" % (tpx["restart"][0], tpx["restart"][1], tpx["restart"][0]),
                        "charge state: not stated by TEST-PLAN for E3-H (a named missing input; the thermal figures do not depend on it, the run's energy does)"],
         "result": "NO GAP for the cells; a step not reached reads NOT_VERIFIED (TEST-PLAN)"},
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
                        "added latent storage (3n): under +60 C it fits only at the best corner; the complete pass is rejected by the %.2f K window under H1 against a 3 K melting area" % (R["h1_window"][1] - R["h1_window"][0]),
                        "powered cooling on the input: cold side %.2f to %.2f W; rejected into the sealed case at the worst corner, INCONCLUSIVE at the conditioned corner (the air lifted onto the +70 C parts) and near the best (3i, 3o)" % co["E3-O"]["qc"],
                        "(II) a wide-temperature cell with the protection re-derived: CONDITIONAL, the cells %.2f K under the re-derived H1's no-act limit at the conditioned corner (4d)" % R["cmp"]["m2"]["LO-01d"]["m_h1"],
                        "charge state: the pack's charge in E3-O is not stated by TEST-PLAN (a named missing input)"],
         "result": "OPEN: (II) recommended, CONDITIONAL; passive design and latent storage rejected; cooling INCONCLUSIVE with its cost to other parts"},
        {"id": "C11", "lo": "LO-01e", "cond": "E5's humid cycle (SC-03 margin)", "zero_power": False,
         "amb": "%.0f to %.0f C at %.0f %% RH" % (e["lo"], e["amb"], e["rh"]), "dur": "%.0f cycles of %.0f h (Method 507.6 Procedure II, mapped in 3n)" % (e["cycles"], e["hours"]),
         "cfg": "deployed, logging, on shore or vehicle input, pack fitted (FEA-008)", "limit": "+%.0f C" % lim["discharge"][1], "power": "the input",
         "gap": "at least %.2f K at the +%.0f C dwell" % (G2["LO-01e"], e["amb"]),
         "approaches": [fans, "the profile mapped from Method 507.6 Procedure II (3n): a 23 C conditioning, ten 24 h cycles 30-60-60-30-30 C, a return to 23 C; operational checks near the ends of the fifth and tenth cycles",
                        ("added latent storage over that profile (3n, 3o): a fit at the best corner only, none at the conditioned and the worst: INCONCLUSIVE" if R["pcm_res"]["best"]["e5_L"] <= R["spare_L"][1]
                         else "added latent storage over that profile (3n, 3o): %.3f L at the best corner against the designed room's %.3f L, none at any corner: rejected within the pocket" % (R["pcm_res"]["best"]["e5_L"], R["spare_L"][1])),
                        "powered cooling: cold side %.2f to %.2f W; rejected into the sealed case at the worst corner, INCONCLUSIVE at the conditioned corner (the air lifted onto the +70 C parts) and near the best (3i, 3o)" % co["E5"]["qc"],
                        "(II) a wide-temperature cell: CONDITIONAL, the cells %.2f K under the re-derived H1's no-act limit at the conditioned corner (4d)" % R["cmp"]["m2"]["LO-01e"]["m_h1"],
                        "charge state: the pack's charge in E5 is not stated by TEST-PLAN (a named missing input)"],
         "result": "OPEN: (II) recommended, CONDITIONAL; latent storage rejected within the pocket (10a); cooling INCONCLUSIVE with its limits named"},
        {"id": "C12", "lo": "LO-01f", "cond": "D-02a's +%.0f C storage margin (E3-S)" % R["f"]["amb"], "zero_power": True,
         "amb": "+%.0f C" % R["f"]["amb"], "dur": "%.0f h" % R["f"]["hours"], "cfg": "stored: closed, latched, every input unplugged, pack fitted at %s in its gauge's shutdown (REQ-025, SC-19)" % lim["soc"],
         "limit": "storage 1 month %.0f to %.0f C at %s (35E Ver. 1.1 3.13)" % (lim["st_1m"][0], lim["st_1m"][1], lim["soc"]),
         "power": "zero from the inputs and the stored pack (its FETs off); a separate source only if one is added",
         "gap": "%.0f K: the ambient alone exceeds the limit" % G2["LO-01f"],
         "approaches": ["fans and spreading: no power and no colder sink",
                        "the calculated insulation for the 24 h: %.1f mm needed against 2.66 mm (3f): rejected" % pas["LO-01f"]["ins_mm"],
                        "added latent storage (3n): %.3f to %.3f L needed against the pocket's %.3f to %.3f L: rejected within the pocket" % (R["pcm_res"]["best"]["e3s_L"], R["pcm_res"]["worst"]["e3s_L"], R["spare_L"][0], R["spare_L"][1]),
                        "powered cooling from a second energy store: added storage under D-06, INCONCLUSIVE (3i)",
                        "(II) a wide-temperature cell: CONDITIONAL, %.2f K under the page's +%.0f C storage row, U2 moved to %s (4d)" % (R["cmp"]["m2"]["LO-01f"]["m_limit"], R["cmp"]["lim2"], R["cmp"]["u2_pick"])],
         "result": "OPEN: (II) recommended, CONDITIONAL; zero-power design and latent storage rejected within the pocket"},
        {"id": "C13", "lo": "LO-01g", "cond": "D-02a's %.0f C storage margin (E4-S)" % R["g"]["amb"], "zero_power": True,
         "amb": "%.0f C" % R["g"]["amb"], "dur": "%.0f h" % R["g"]["hours"], "cfg": "stored, as C12",
         "limit": "storage floor %.0f C (Ver. 1.1); %.0f C (Version 1.0); discharge floor %.0f C" % (lim["st_1m"][0], S["35E_10"]["st_1m"][0], lim["discharge"][0]),
         "power": "zero from the inputs and the stored pack; a separate primary source only if one is added",
         "gap": "%.0f K (Ver. 1.1); %.0f K (Version 1.0)" % G2["LO-01g"],
         "approaches": ["the calculated insulation: %.1f mm needed (3f): rejected" % pas["LO-01g"]["ins_mm"],
                        "added latent storage: no maker's sheet of a material freezing between -20 and -10 C is held: INCONCLUSIVE",
                        "a heater fed by the pack (case i): the discharge window applies and its FETs are off in shutdown (3g): rejected within REQ-025; its %.1f to %.1f h are model sensitivities, not the basis" % sh["dur_h_range"],
                        "a heater fed by a primary battery (case i), bounded in 3n: added energy storage under D-06, not adopted: INCONCLUSIVE",
                        "a pack already cold-soaked (case ii): not recovered by any heater below -20 C; the pack cannot feed one below -10 C",
                        "heating lost (case iii): past the floor %.2f to %.2f h after a pack-fed hold, at once for a hold at the floor (3g)" % (sh["rows"]["fast"]["t_lost_pack_h"], sh["rows"]["slow"]["t_lost_pack_h"]),
                        "(II) a wide-temperature cell: CONDITIONAL, %.2f K inside the page's %.0f C storage row, no heater and no store (4d)" % (R["cmp"]["m2"]["LO-01g"]["m_limit"], R["cmp"]["m2"]["LO-01g"]["limit"])],
         "result": "OPEN: (II) recommended, CONDITIONAL; the pack-fed heater rejected; the primary a proposal under D-06"},
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
         "power": "zero", "gap": "none for the cells at the ex-factory state; F2's storage line (-10 C) open with Eaton",
         "approaches": ["none needed", "recovery mapped: %s" % tpx["e4t_return"],
                        "charge state: the ex-factory state for storage; for transport 'at its charge', not stated (a named missing input)"],
         "result": "NO GAP for the cells"},
        {"id": "C17", "lo": None, "cond": "E3-P, the pack alone, armed, at full charge, then discharged from +%.0f C" % tpx["e3p"][0], "zero_power": False,
         "amb": "+%.0f C set point, +-%.0f K" % (tpx["e3p"][0], tpx["e3p"][1]), "dur": "%.0f h, then a %.0f A discharge until the gauge stops it" % (tpx["e3p"][2], tpx["e3p"][3]),
         "cfg": "the pack alone, JP1 closed, full charge",
         "limit": "at full charge the maker's %.0f days at %.0f C (MAKER 7.10); discharge to %.0f C; F2 %.0f C" % (fs["days"], fs["t"], lim["discharge"][1], S["F2"]["operating"][1]),
         "power": "the pack (the test load)",
         "gap": "none by construction: the soak sits at the limits; the pass line asks OTD (%.1f C in the reading) to stop the discharge before any cell exceeds +%.0f C and to recover at or below +%.1f C; whether it acts at once depends on the reading's error, so no immediate refusal is claimed" % (R["ladder"]["OTD"], lim["discharge"][1], tpx["otd_rec"]),
         "approaches": ["none needed"], "result": "NO GAP (a protection test at the limits)"},
        {"id": "C18", "lo": None, "cond": "E4-P, the pack alone at its cold storage limit", "zero_power": True,
         "amb": "as E4-T (%s)" % tp["E4-T"], "dur": "24 h", "cfg": "the pack alone (%s)" % ("as E4-T" if tpx["e4p"] else "not stated"),
         "limit": "storage floor %.0f C at %s; no cold-storage recovery figure published (PROVISIONAL pass line)" % (lim["st_1m"][0], lim["soc"]),
         "power": "zero", "gap": "none for the cells at the ex-factory state; another charge state is not in the sheet",
         "approaches": ["none needed", "recovery mapped (as E4-T): %s" % tpx["e4t_return"],
                        "charge state: E4-P names none (a named missing input); the sheet's storage rows hold at the ex-factory 30 %"],
         "result": "NO GAP at the ex-factory state"},
        {"id": "C19", "lo": None, "cond": "P13, F2 at temperature: %.0f A for %.0f s from +%.0f C, and %.0f A for %.0f h at the pack's hot limit" % (tpx["p13_kd"][1], tpx["p13_kd"][2], tpx["p13_kd"][0], tpx["p13_a"], tpx["p13_h"]), "zero_power": False,
         "amb": "+%.0f C block; the pack's hot limit" % tpx["p13_kd"][0], "dur": "%.0f s; %.0f h" % (tpx["p13_kd"][2], tpx["p13_h"]), "cfg": "a block on the bench, a thermocouple on F2's body",
         "limit": "+%.0f C at the cells and at F2's body" % lim["discharge"][1], "power": "the test load",
         "gap": "the key-down: none for the cells (%.2f to %.2f C); the hour: the cells' own %.2f to %.2f W rise them %.1f to %.1f K over the block's air, so 'at the hot limit' must mean the cell surface (3k)" % (R["kd"]["to"] + R["p13"]["w"] + R["p13"]["steady"]),
         "approaches": ["a definition item for P13's owner; F2's body is the measurement"], "result": "NO GAP for the cells if the limit is held at the cell surface; F2 open"},
    ]
    return rows


def comparison_lines(R):
    S, c, cm, cc = R["S"], R["cand"], R["cmp"], R["condc"]
    lim, hl, i1, ii, ap = S["35E_11"], S["HL18650V"], cm["i1"], cm["iii"], cm["apr"]
    pr_, sp_, ls_ = R["pcm_res"], R["spare_L"], R["lsh"]
    psel = R["prim"]["configs"]["5S, -40 C curve (lower)"]
    u2r = S["U2"]["rows"][cm["u2_pick"]]
    lad = cm["lad2"]
    pct = lambda k: -100.0 * (c[k]["usable_wh"] / c["35E"]["usable_wh"] - 1.0)
    L = []
    L += ["%s" % ap["I"]["name"],
          "   maker limits (MAKER, Ver. 1.1): discharge %.0f to %.0f C, charge %.0f to %.0f C, storage 1 month %.0f to %.0f C, 3 months %.0f to %.0f C, 1 year %.0f to %.0f C"
          % (lim["discharge"] + lim["charge"] + lim["st_1m"] + lim["st_3m"] + lim["st_1y"]),
          "   usable energy: %.1f Wh (%.2f h at PS-IDLE-SPEC); a cooler fed by the pack would leave %.2f to %.2f h at the best corner (3o)"
          % (c["35E"]["usable_wh"], c["35E"]["hours"], i1["endu_best"][0], i1["endu_best"][1]),
          "   thermal demand: E3-O and E5 %.2f to %.2f W of cooler input at the best corner and %.2f to %.2f W at the conditioned corner (the air then %.1f to %.1f C); E3-S %.0f to %.0f Wh over"
          % (i1["best_in"][0], i1["best_in"][1], i1["cond_in"][0], i1["cond_in"][1], i1["cond_air"][0], i1["cond_air"][1], i1["e3s_Wh_best"][0], i1["e3s_Wh_best"][1]),
          "   24 h from a second store (best corner; none at the worst for COP 0.5); E4-S %.1f to %.1f Wh of heat over 24 h from a second store (3n)" % ii["demand_Wh"],
          "   mass and volume: the cooler and its spreader (no sheet held), the E3-S store, the heater's %.1f to %.1f kg (%.2f to %.2f L) of primary cells outside the pocket"
          % (psel["slow"]["kg"], psel["fast"]["kg"], psel["slow"]["L"], psel["fast"]["L"]),
          "   maintenance: the primary cells replaced as a set every %.0f years (ASSUMPTION); the cooler's module and fan" % REPLACE_Y,
          "   implementation: a cooler stage with its control on the input, a storage-time store and cooler with their isolation, a primary string with a thermostat and blocking path,",
          "   Layer 7's volume for all of it",
          "   constraints changed: %s" % "; ".join(ap["I"]["changes_constraint"]),
          "   remaining: LO-01d and LO-01e rest on a cooler of up to 35 W lifting the inside air onto the +70 C parts (the input's spare power not derived); LO-01f and LO-01g need added energy storage",
          "",
          "%s" % ap["II"]["name"],
          "   maker limits (INFERRED: the HL18650V's page, not a specification): discharge %.0f to %.0f C, charge %.0f to %.0f C, storage 30 days %.0f to %.0f C, 3 months %.0f to %.0f C,"
          % (hl["discharge"] + hl["charge"] + hl["st_30d"] + hl["st_3m"]),
          "   6 months %.0f to %.0f C, 12 months %.0f to %.0f C (no state of charge stated)" % (hl["st_6m"] + hl["st_12m"]),
          "   usable energy: %.1f Wh (%.2f h), %.1f %% less than the 35E; %.1f Wh nominal against %.1f" % (c["HL18650V"]["usable_wh"], c["HL18650V"]["hours"], pct("HL18650V"), c["HL18650V"]["wh_nom"], c["35E"]["wh_nom"]),
          "   thermal demand: none added (the enclosure of LO-01a is common to all three; the existing mat stays for charging, the cell charging from -20 C at 0.1C to 4.1 V)",
          "   mass and volume: the same 18650 block; %.0f g a cell (page) against the 35E's %.0f g at most, %.0f g a pack less at most; %.2f mm longer against %.2f mm of room"
          % (cm["whl"], cm["w35"], 12 * (cm["w35"] - cm["whl"]), c["HL18650V"]["grow_mm"][0], R["room"]["axis"]),
          "   maintenance: the pack as today; cycles %s (page)" % hl["cycle"],
          "   implementation (first cut): the cell; U2 to %s (OT %.0f C, OVP %.3f V, UVP %s, drive %s, so F2's drive is re-drawn); the ladder under the idle limit %.0f C with today's"
          % (cm["u2_pick"], u2r["ot"], u2r["ovp"], u2r["uvp"], u2r["drive"], cm["lim2"]),
          "   offsets: C1 %.1f, H1 %.1f, H2 %.1f, OTD %.1f C (SOT, the PTC and the release with them); the gauge's chemistry data and its cold cutoffs; the charger's cold rows"
          % (lad["C1"], lad["H1"], lad["H2"], lad["OTD"]),
          "   constraints changed: %s" % "; ".join(ap["II"]["changes_constraint"]),
          "   remaining: the maker's signed specification (architecture level); U2's variant window at the network re-run (INFERRED here); T-H1 (common); F2 (common)",
          "",
          "%s" % ap["III"]["name"],
          "   maker limits: the 35E's; RT57HC melting area %.0f to %.0f C; Saft LSH 20 operating %.0f to +%.0f C, storage recommended at +%.0f C at most"
          % (R["pcm"]["melt"][0], R["pcm"]["melt"][1], ls_["t_op"][0], ls_["t_op"][1], ii["st_max"]),
          "   usable energy: the pack's %.1f Wh unchanged; the primary's typical %.2f Ah a cell at the cold load serves the heater only" % (c["35E"]["usable_wh"], psel["cap"]),
          "   thermal demand: none electrical for the store; the heater %.2f to %.2f W on average over the 24 h" % (psel["slow"]["p_avg"], psel["fast"]["p_avg"]),
          "   mass and volume: the store %.3f L (E3-O) and %.3f L (E5) at the conditioned corner, %.3f to %.3f L for E3-S, against at most %.3f L; the primary as (I)"
          % (cc["e3o_L"], cc["e5_L"], pr_["best"]["e3s_L"], pr_["worst"]["e3s_L"], sp_[1]),
          "   maintenance: the store none; the primary as (I)",
          "   implementation: a sealed container round the block; a primary string, thermostat and blocking path",
          "   constraints changed: %s" % "; ".join(ap["III"]["changes_constraint"]),
          "   remaining: LO-01d rejected (H1's window), LO-01e at the conditioned corner, LO-01f within the pocket; LO-01g needs added energy storage",
          "",
          "(II)'s hot limit: an idle pack on the input is read against the page's storage row within 30 days (+%.0f C), the lower of its hot rows (discharge to +%.0f C);"
          % (cm["lim2"], hl["discharge"][1]),
          "   E5's conditioning and ten cycles and E3-S's 24 h stay inside those 30 days. The ladder keeps today's offsets under that limit (a first cut, not a specification).",
          "Per row (the conditioned corner):"]
    for k in sorted(ap["I"]["rows"]):
        L.append("   %s  (I) %s | (II) %s | (III) %s" % (k, ap["I"]["rows"][k], ap["II"]["rows"][k], ap["III"]["rows"][k]))
    L.append("Added subsystems: (I) %d, (II) %d, (III) %d. Rows rejected: (I) %s, (II) %s, (III) %s. Rows needing added energy storage: (I) %s, (II) %s, (III) %s."
             % (len(ap["I"]["added"]), len(ap["II"]["added"]), len(ap["III"]["added"]),
                ", ".join(ap["I"]["rejected"]) or "none", ", ".join(ap["II"]["rejected"]) or "none", ", ".join(ap["III"]["rejected"]) or "none",
                ", ".join(ap["I"]["needs_d06"]) or "none", ", ".join(ap["II"]["needs_d06"]) or "none", ", ".join(ap["III"]["needs_d06"]) or "none"))
    m2 = cm["m2"]
    L += ["Recommended: (%s). Its margins at the conditioned corner (the cells' peak against the page's limit, the re-derived H1's no-act limit %.2f C, %s's lowest trip %.1f C):"
          % (cm["rec"], cm["h1n2"], cm["u2_pick"], cm["u2lo"][cm["u2_pick"]]),
          "   LO-01a %.2f C on the pack: %.2f K under %.0f C, %.2f K under H1; LO-01d %.2f C: %.2f, %.2f and %.2f K; LO-01e %.2f C: %.2f, %.2f and %.2f K;"
          % (m2["LO-01a"]["peak"], m2["LO-01a"]["m_limit"], m2["LO-01a"]["limit"], m2["LO-01a"]["m_h1"], m2["LO-01d"]["peak"], m2["LO-01d"]["m_limit"], m2["LO-01d"]["m_h1"], m2["LO-01d"]["m_u2"],
             m2["LO-01e"]["peak"], m2["LO-01e"]["m_limit"], m2["LO-01e"]["m_h1"], m2["LO-01e"]["m_u2"]),
          "   LO-01f %.0f C: %.2f K under %.0f C, %.2f K under U2; LO-01g %.0f C: %.2f K over %.0f C; LO-01h: %.0f, %.0f and %.0f K at the envelope's rows (the page's rows equal them)."
          % ((m2["LO-01f"]["peak"], m2["LO-01f"]["m_limit"], m2["LO-01f"]["limit"], m2["LO-01f"]["m_u2"], m2["LO-01g"]["peak"], m2["LO-01g"]["m_limit"], m2["LO-01g"]["limit"]) + m2["LO-01h"]["rows"]),
          "   U2's lowest trip is taken %.1f K under each variant's nominal, as the BQ7720700's %.0f C against its %.1f C at the network (INFERRED: the network's tolerance not re-run)."
          % (cm["u2_off"], S["U2"]["ot"]["BQ7720700"], R["ladder"]["U2_trip_lo"]),
          "   At the bound's worst corner (an enclosure under LO-01a's line) E5's cells reach %.2f C, over the re-derived H1 and U2's lowest trip, so (II) carries T-H1's condition as LO-01a does."
          % cm["m2_unc"]["e5_peak"],
          "   Architecture-level uncertainty (could overturn it): the signed specification not confirming storage at +71 C or -33 C at the stored charge, or the idle limit read lower than",
          "   +80 C; then that row falls back to (III), which needs the owner's ruling on added storage for LO-01g and has no in-pocket route for LO-01f. Downstream, not architectural:",
          "   U2's variant window re-run, the ladder's settings, the gauge's chemistry data, F2's replacement, T-H1's measured conductance."]
    return L


def correction_lines(R):
    cool, cc, pr_ = R["cool"], R["condc"], R["pcm_res"]
    wa = [v["air"] for (cn, cop), v in cool["E3-O"]["inside"].items() if cn == "worst" and v] + [v["air"] for (cn, cop), v in cool["E5"]["inside"].items() if cn == "worst" and v]
    ca = [v["air"] for v in cc["cool"].values()]
    return [
        "R3, powered cooling: was, into the inside air the loop did not close at the worst corner for COP 0.5 and closed for COP 1.0 (the extracted heat counted twice); now an equilibrium",
        "   exists for both, with the air at %.1f to %.1f C (worst) and %.1f to %.1f C (conditioned): the route is REJECTED into the sealed case at both corners and INCONCLUSIVE only near"
        % (min(wa), max(wa), min(ca), max(ca)),
        "   the best. E3-S's second store: 38 to 213 Wh with the heat sent out of the case (unchanged; a sealed path missing), %.0f to %.0f Wh into the sealed case at the best"
        % R["cmp"]["i1"]["e3s_Wh_best"],
        "   corner and no equilibrium at the worst for COP 0.5. Material: (I)'s hot rows now carry a cooler of up to 35 W that lifts the air onto the +70 C parts (3o, 4d).",
        "R3, passive storage: was, 'passive insulation or thermal storage' rejected with nothing missing; now the rejection covers the calculated insulation only (24.6 and 30.3 mm against",
        "   2.66 mm, unchanged) and added latent storage is bounded on its own (3n, 3o): new routes, REJECTED or INCONCLUSIVE as listed; each row's decision unchanged (OPEN).",
        "R3, usable energy: the pack-fed heater's 11.9 to 28.9 Wh and 1.3 to 8.6 h are model sensitivities; its rejection rests on the shutdown path alone: decision and margins unchanged, minor.",
        "R2, the mappings (C04, C05, C16, C17, C18): the lid-closed start, E3-H's hold and its repeat with the sensor controller in reset (TMP117 at +55.0 and +56.0 C, released at",
        "   +45.0 C), the restart at +46.5 C after 30 minutes, the return to 25 C with capacity within 5 %, and OTD's recovery at +52.5 C change no thermal figure: every row's result and",
        "   margin unchanged; the unstated charge states are named missing inputs: minor.",
        "E5's profile (R3's E5 item): was INCONCLUSIVE on a missing profile; now Method 507.6 Procedure II (mapped, its owner to confirm): latent storage %.3f L at the best corner"
        % pr_["best"]["e5_L"],
        "   (%.3f L), none at the conditioned (%.3f L) and worst (%.2f L) corners. Material for (III)." % (pr_["best"]["e5_L"], cc["e5_L"], pr_["worst"]["e5_L"]),
        "MINOR R1, the coupling on shore: the cells reach %.2f C, past the +59 C abort, the air %.2f C (was: the cell criteria met). The measure now serves the pack only; LO-01a's decision,"
        % (R["meas"]["a_input_worst"][1], R["meas"]["a_input_worst"][0]),
        "   CONDITIONAL on T-H1 at %.3f W/K, and its margins are unchanged: minor for the row." % R["gov"]["all"][4],
        "MINOR R2, C17: OTD must stop the discharge before any cell exceeds +60 C and recover at or below +52.5 C; no immediate refusal is claimed: NO GAP and OTD's 2.5 K under +60 C",
        "   unchanged: minor.",
        "MINOR R3, the fast corner's 8.20 W against the mat's 7.5 W: a further inability of the pack-fed heater, already rejected: minor.",
        "The owner's instruction of 2 October 2026 then changes the selection itself: with the corrected balance and the conditioned corner, (I)'s hot rows carry a cooler of up to",
        "   35 W and its storage rows need added energy storage; (II) is recommended (4d). The primary battery is a bounded proposal under D-06, no longer a sized adoption.",
    ]


def later_lines(R):
    c = R["cand"]
    return [
        "A. (a requirement change) the four margin levels shown with the pack out of the exposure, as REQ-074 and REQ-051's deviations already run them: no spend, no energy lost;",
        "   the kit not claimed at those levels with its own pack. Reserved to the owner by D-29; not proposed, because a route stands.",
        "B. (the recommendation's own owner step, section 5) the owner's approval of the cell change inside D-06's 4S3P once the signed specification confirms it: about USD %.2f a pack of 12 cells, %.1f Wh"
        % (12 * R["price_hl"], c["HL18650V"]["wh_nom"]),
        "   nominal against %.1f (%.1f %% less usable), D-06's 'about 145 Wh' restated (cell_provenance)." % (c["35E"]["wh_nom"], -100.0 * (c["HL18650V"]["usable_wh"] / c["35E"]["usable_wh"] - 1.0)),
        "C. (the fallback if the specification leaves LO-01g) (III)'s added energy store for the storage heater, a ruling on D-06's one pack; LO-01f has no in-pocket fallback (4d).",
    ]


def downstream_lines(R):
    gv, cm = R["gov"]["all"], R["cmp"]
    lad = cm["lad2"]
    return [
        "Session (layer 4, this obligation): with the signed specification in hand, re-derive (II)'s protection: U2's variant window at the network (%s first cut), the ladder (C1 %.1f,"
        % (cm["u2_pick"], lad["C1"]),
        "   H1 %.1f, H2 %.1f, OTD %.1f C first cut), SOT, the PTC, the release, the gauge's chemistry data and cold cutoffs; re-run 4d's margins on the specification's rows. Acceptance:"
        % (lad["H1"], lad["H2"], lad["OTD"]),
        "   each margin of 4d positive at the conditioned corner with the specification's limits.",
        "Layer 6 (components): the HL18650V's signed specification (the request is drafted; the session contacts no outside party), the maker's identity behind the listings, the lot;",
        "   F2's storage line and operation above +60 C and below -20 C (Eaton, Q-E2 extended) or another self-control protector. Acceptance: the documents filed and read.",
        "Layer 7 (mechanical): the coupling (3b) for the cells only if T-H1 reads under %.3f W/K with the fans; none for (II). Acceptance: E3-L, E4-S." % gv[4],
        "Layer 8 (generator owners): under (II), gen_sch_p.py (U2 to %s with its COUT drive, F2) and pcb_pack_protection.yaml re-derived. Acceptance: the protection suite." % cm["u2_pick"],
        "Layer 9 (pre-layout analysis): board P's place against the block (F2 at the air passes +60 C at LO-01a's worst corner) and the thermistors on the hottest cells. Acceptance: P13, P14.",
        "Prototype bench: T-H1 in both lid states with the dummy pack block (at least %.3f W/K for the complete pass line); E3-A, E3-L, E3-H, E3-O, E5 with a thermocouple on every cell;" % gv[4],
        "   E3-S, E4-S with the pack fitted; E4-O; P13 at the cell surface; P14; P15. Acceptance: each run's TEST-PLAN pass line; 3a's and 3o's corners replaced by the measured conductance.",
        "TEST-PLAN's owner: confirm that E5 is Method 507.6 Procedure II (3n); under (II), restate the cell-derived numbers (the +59 C abort, E3-P's +58 C, the +60 C pass lines) with the cell.",
        "Firmware owner: under (II), the gauge image with the new cell's data and the re-derived ladder; with the coupling, the mat's thermostat on battery at the cold end (3c).",
        "Board B's owner: BANK-R1 in gen_sch_b.py, without which E3-L's stage criteria fail at every level that enters the heat stage.",
        "The kit's thermal owner (layer 4, outside FEA-008): the +70 C parts against E3-O's and E5's inside air at the conditioned corner (%.2f and %.2f C, 3o), common to every approach."
        % (R["condc"]["air_unc"]["E3-O"], R["condc"]["air_unc"]["E5"]),
        "Owner: (1) send the drafted request to Yichun Topwell Power; (2) after the specification confirms the rows, approve D-06's restated energy and the spend (section 5).",
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
    cm = R["cmp"]
    p["P13 the comparison holds at most three approaches, each judged on every LO row"] = len(cm["apr"]) <= 3 and all(sorted(a["rows"]) == sorted(modes) for a in cm["apr"].values())
    p["P14 the recommended approach has no row rejected and none needing added energy storage, and the fewest added subsystems among such"] = cm["rec"] is not None and cm["apr"][cm["rec"]]["qualifies"] and all(
        len(cm["apr"][cm["rec"]]["added"]) <= len(a["added"]) for a in cm["apr"].values() if a["qualifies"])
    p["P15 U2's chosen variant's lowest trip clears every required level's peak"] = cm["u2lo"][cm["u2_pick"]] > cm["clear"]
    p["P16 the recommended margins are positive at the conditioned corner"] = all(v[k] > 0 for v in cm["m2"].values() for k in ("m_limit", "m_h1", "m_u2") if k in v)
    p["P17 the primary battery is a proposal, not adopted"] = all("not adopted" in r["route"] for d in dec.values() for r in d["routes"] if "primary battery" in r["route"])
    u = R["u01"]
    p["P18 U-01: every charge row's set current is within the page's band and the drawn limit"] = all(r["i_set"] <= min(r["i_page_pack"], u["i_draw"]) + 1e-12 for r in u["rows_chg"])
    p["P19 U-01: each drafted charge threshold sits inside its band's edge by today's margin"] = (u["draft"]["UTC"] > u["hp"]["bands"][0][0] and u["draft"]["T2"] > u["hp"]["bands"][1][0]
        and u["draft"]["T5"] > u["hp"]["bands"][2][0] and u["draft"]["OTC"] < u["hp"]["bands"][2][1])
    p["P20 U-01: the energy chain reproduces the replay's 35E figures before it is applied to the proposed cell"] = (round(u["e35"]["25"], 1) == u["rep"][0] and round(u["e35"]["m10"], 1) == u["rep"][1])
    p["P21 U-01: the idle-limit thresholds order E3-O's cells, E3-S, E5's cells and E5 with H1 idle"] = u["thr"]["e3o_cells"] < u["thr"]["e3s"] < u["thr"]["e5_cells"] < u["thr"]["e5_noact"]
    c = R["u01c"]
    verdicts = [d["charge"][0] for d in c["suit"].values()] + [v for d in c["suit"].values() for v, _ in d["discharge"] + d["storage"]]
    p["P22 U-01: every mode's verdict is one of the three"] = all(v in (SUIT_PUB, SUIT_VENDOR, UNSUIT) for v in verdicts)
    p["P23 U-01: the room is read in the chosen column and moved down"] = R["rows_cm"]["M5"] < R["rows_cm_old"]["M5"] and R["spare_L"][1] < R["spare_L_old"]
    p["P24 U-01: the 35E holds no hot row on the bound, LO-01a's complete pass and LO-01e lie over it for every cell"] = (
        not any(v for row in c["holds"]["35E"].values() for v in row.values())
        and all(not c["holds"][cell]["LO-01a"]["complete pass (the SGP41's air, common)"] for cell in c["holds"])
        and all(not v for cell in c["holds"] for v in c["holds"][cell]["LO-01e"].values()))
    p["P26 U-01: with the MP 176065 xtd LO-01d's cell limit and no-hot-stop line hold on the bound"] = (c["holds"]["MP 176065 xtd"]["LO-01d"]["cell limit"]
        and c["holds"]["MP 176065 xtd"]["LO-01d"]["no hot stop"])
    p["P25 U-01: the Saft cells' growth along the axis needs a thinner wrap than the 35E block's"] = 0 < c["fit"]["wrap_left"] < c["fit"]["wrap_35"]
    p["P12 the screen maps every TEST-PLAN exposure of sections 6 and 7 it covers"] = all(any(t in (r["cond"] + r["dur"]) for r in R["screen"]) for t in ("E3-A", "E3-L", "E3-H", "E3-O", "E3-S", "E3-T", "E3-P", "E4-O", "E4-S", "E4-T", "E4-P", "E5", "P13"))
    return p


# ------------------------------------------------------------------------------------------------ 9: U-01 by mode (2 October 2026)
def u01(R, pb):
    """The dependency round of 2 October 2026 (the owner: charging, discharging and storage limits established separately
    with their conditions; usable energy and charging constraints for the proposed cell). Nothing here is adopted."""
    S = R["S"]
    lim = S["35E_11"]
    tw = json.load(open(path(TOPWELL), encoding="utf-8"))
    t = tw["specification_table_verbatim"]
    hp = {}
    m = need(t, r"Nominal Capacity (\d+)mAh \(Min\. (\d+)mAh\) @0\.2C standard charge&discharge", "HL18650V capacity")
    hp["c_typ"], hp["c_min"] = float(m.group(1)) / 1000.0, float(m.group(2)) / 1000.0
    hp["std_chg"] = float(need(t, r"Standard Charge Current (\d\.\d+)A", "HL18650V standard charge").group(1))
    hp["max_chg"] = float(need(t, r"Max Continuous Charge Current (\d\.\d+)A", "HL18650V charge current").group(1))
    hp["max_dis"] = float(need(t, r"Max Continuous Discharge Current (\d+)A", "HL18650V discharge current").group(1))
    hp["v_chg"] = float(need(t, r"Charge Cut-off Voltage (\d\.\d+)V", "HL18650V charge voltage").group(1))
    hp["v_cut"] = float(need(t, r"Discharge Cut-off Voltage (\d\.\d+)V", "HL18650V end voltage").group(1))
    hp["method"] = need(t, r"Charge Method (CC/CV)", "HL18650V charge method").group(1)
    hp["ir"] = float(need(t, r"Internal Resistance ≤(\d+)mΩ", "HL18650V resistance").group(1))
    hp["g"] = float(need(t, r"Weight Approx\. (\d+)g", "HL18650V mass").group(1))
    hp["cycles"] = int(need(t, r"Cycle Life ≥(\d+) times", "HL18650V cycles").group(1))
    hp["chg_head"] = tuple(float(v) for v in need(t, r"Charge: (-\d+) ~(\d+)℃", "HL18650V charge headline").groups())
    g = need(t, r"Charge: -\d+ ~\d+℃ (-\d+) (-\d+)＜T≤", "HL18650V cold charge row")
    hp["garbled"] = (float(g.group(1)), float(g.group(2)))      # the row as printed: "-20 -10＜T≤0℃"
    hp["bands"] = [(float(a), float(b), float(c), float(v)) for a, b, c, v in
                   re.findall(r"(-?\d+)＜T[≤＜](-?\d+)℃: (\d\.\d)C to (\d\.\d)V", t)]
    hp["dis_head"] = tuple(float(v) for v in need(t, r"Discharge: (-\d+)~(\d+)℃", "HL18650V discharge headline").groups())
    hp["ends"] = [(float(a), float(b), float(v)) for a, b, v in re.findall(r"(-?\d+)[＜≤]T[≤＜](-?\d+)℃: (\d\.\d+)V", t)]
    hp["storage"] = [(float(a), float(b), (int(mo) * 30 if mo else int(dd)), ("%s months" % mo) if mo else ("within %s days" % dd))
                     for a, b, mo, dd in re.findall(r"(-\d+)~(\d+) ?℃ (?:0 - (\d+) months|Within (\d+) days)", t)]
    if [b[:2] for b in hp["bands"]] != [(-10.0, 0.0), (0.0, 10.0), (10.0, 60.0)] or len(hp["ends"]) != 3 or len(hp["storage"]) != 4:
        refuse(4, "the HL18650V page's rows did not read as expected: %s %s %s" % (hp["bands"], hp["ends"], hp["storage"]))
    hp["c_basis"] = hp["std_chg"] / 0.2
    if abs(hp["c_basis"] - hp["c_min"]) > 1e-9 or abs(hp["max_chg"] / 0.5 - hp["c_min"]) > 1e-9:
        refuse(4, "the page's C basis is not its minimum capacity")
    n_s, n_p = 4, 3
    # signed comparables (context only): Samsung's 30Q6 (2020) and 30Q (2015) specifications, Molicel's P28A data sheet
    s6t = pdf(S30Q6)
    cmp6 = {"cold": dict((float(k), float(v) / 100.0) for k, v in zip(
                re.search(r"23°C\s+(-20)℃\s+(-10)℃\s+(0)℃\s+(23)℃\s+(60)℃", s6t).groups(),
                need(s6t, r"Relative Capacity\s+(\d+)%\s+(\d+)%\s+(\d+)%\s+(\d+)%\s+(\d+)%", "30Q6 7.6").groups())),
            "full_storage": (int(need(s6t, r"Storage : (\d+) days \(@ (\d+)℃\)", "30Q6 3.11").group(1)), float(need(s6t, r"Storage : (\d+) days \(@ (\d+)℃\)", "30Q6 3.11").group(2)),
                             need(s6t, r"Capacity recovery\(after the storage\) ≥ ([\d,]+)mAh\s+\((\d+)% of the rated capacity", "30Q6 recovery").groups()),
            "release": need(s6t, r"\(must re-discharge release < (\d+)℃\)", "30Q6 release").group(1)}
    s15t = pdf(S30Q)
    cmp15 = {"rec": need(s15t, r"Recovery (\d+)% after storage", "30Q 2015 recovery").group(1)}
    mp = S["P28A"]
    mpt = pdf(MP28A)
    comps = {"30Q6": {"doc": S["30Q6"]["doc"], "kind": "MAKER, signed specification", "surf_dis": S["30Q6"]["surf_discharge"], "amb_chg": S["30Q6"]["amb_charge"],
                      "st_1m": S["30Q6"]["st_1m"], "soc": S["30Q6"]["soc"], "cold": cmp6["cold"], "full": cmp6["full_storage"], "release": cmp6["release"]},
             "30Q_2015": {"doc": S["30Q_2015"]["doc"], "kind": "MAKER, signed specification", "surf_dis": S["30Q_2015"]["surf_discharge"],
                          "st_1m": S["30Q_2015"]["st_1m"], "soc": S["30Q_2015"]["soc"], "rec": cmp15["rec"]},
             "P28A": {"doc": mp["doc"], "kind": "MAKER, a data sheet 'for reference only', not signed", "charge": mp["charge"], "discharge": mp["discharge"],
                      "ref_only": bool(re.search(r"for reference only", mpt))}}
    # what no signed comparable reaches: charge below 0 C, storage above +60 C, storage below -30 C
    signed_st_top = max(comps["30Q6"]["st_1m"][1], comps["30Q_2015"]["st_1m"][1])
    signed_st_floor = min(comps["30Q6"]["st_1m"][0], comps["30Q_2015"]["st_1m"][0])
    signed_chg_floor = min(comps["30Q6"]["amb_chg"][0], comps["P28A"]["charge"][0])
    beyond = {"charge below %.0f C" % signed_chg_floor: hp["bands"][0][0] < signed_chg_floor,
              "storage above %+.0f C" % signed_st_top: max(r[1] for r in hp["storage"]) > signed_st_top,
              "storage below %.0f C" % signed_st_floor: min(r[0] for r in hp["storage"]) < signed_st_floor}

    # ---- 2. charging constraints with the drawn charger (BQ25731) and the pack's gauge (BQ4050): drafts, never applied
    css = text(CSS)
    chg = {"strap_v": float(need(css, r"4S defaults \| ChargeVoltage (\d+\.\d+) V", "BQ25731 4S default").group(1)),
           "batovp_pct": float(need(css, r"BATOVP at (\d+) % of ChargeVoltage", "BQ25731 BATOVP").group(1)),
           "clamp": (float(need(css, r"below VSYS_MIN \((\d+\.\d) V for 4S\) charge current is clamped at (\d+) mA", "BQ25731 clamp").group(1)),
                     float(need(css, r"below VSYS_MIN \((\d+\.\d) V for 4S\) charge current is clamped at (\d+) mA", "BQ25731 clamp").group(2)) / 1000.0),
           "no_ts": bool(re.search(r"no cell temperature input", css)),
           "host_term": bool(re.search(r"host terminates charge by setting CHRG_INHIBIT", css))}
    tc = text(TC)
    lad = R["ladder"]
    lad_now = {"UTC": lad["UTC"], "UTC_rec": float(need(tc, r"1\.0 C, 2 s, recovery (\d+\.\d) C; T1 (\d+) C", "UTC recovery").group(1)),
               "T1": float(need(tc, r"1\.0 C, 2 s, recovery (\d+\.\d) C; T1 (\d+) C", "T1").group(2)),
               "T3": float(need(tc, r"charge inhibit at T3 .*?\| (\d+) C \(integer\)", "T3", re.M).group(1)),
               "T4": float(need(tc, r"charge suspend at T4 .*?\| (\d+) C \(integer\)", "T4", re.M).group(1)),
               "OTC": lad["OTC"], "L3": float(need(tc, r"panel and bridge hold on charge below \+(\d+) C", "L3 hold").group(1))}
    trm = pdf(TRM)
    taper_default = float(need(trm, r"Charge Term Taper Current\s+0\s+32767\s+(\d+)\s+mA", "Charge Term Taper Current").group(1))
    ranges_ok = all(re.search(r"14\.4\.1\.\d %s Temp" % k, trm) for k in ("T1", "T2", "T5", "T6", "T3", "T4"))
    floor_leg = hp["bands"][0][0]                     # the legible lower bound of the coldest charge row
    off_utc = lad_now["UTC"] - lim["charge"][0]       # today's UTC sits this far inside the 35E's 0 C
    draft = {"UTC": floor_leg + off_utc, "UTC_rec": floor_leg + off_utc + (lad_now["UTC_rec"] - lad_now["UTC"]),
             "T1": floor_leg + off_utc, "T2": hp["bands"][1][0] + off_utc, "T5": hp["bands"][2][0] + off_utc,
             "T3": lad_now["T3"], "T4": lad_now["T4"], "OTC": lad_now["OTC"],
             "L3": floor_leg + lad_now["L3"], "CUV": hp["v_cut"]}
    i_draw = pb.ICHG
    rows_chg = []
    for (lo, hi, crate, v), rng in zip(hp["bands"], ("Low Temp (T1 to T2)", "Standard Temp low (T2 to T5)", "Recommended and Standard Temp high (T5 to T3)")):
        i_pack = crate * hp["c_basis"] * n_p
        rows_chg.append({"band": (lo, hi), "range": rng, "crate": crate, "v_cell": v, "v_pack": v * n_s, "i_page_pack": i_pack,
                         "i_set": min(i_pack, i_draw), "batovp": v * n_s * chg["batovp_pct"] / 100.0})
    crate_drawn = i_draw / n_p / hp["c_basis"]
    # ---- 3. usable energy, not nameplate: the tree's energy chain (records/energy, the chain behind L4-E9's 107.9 Wh)
    sp = importlib.util.spec_from_file_location("energy_budget_l4e10", path(EB_PY))
    eb = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(eb)
    import yaml
    d_in = yaml.safe_load(open(path(EB_IN), encoding="utf-8"))
    pk = eb.Pack(d_in)
    p = float(d_in["model_states"]["PS-IDLE-SPEC"]["plan"])
    rp = need(text(REPLAY), r"A1 D-06's 4S3P: usable ([\d.]+) Wh at \+20 C, ([\d.]+) Wh at -10 C: ([\d.]+) h and ([\d.]+) h", "the replay's A1 line")
    rep = tuple(float(v) for v in rp.groups())
    cell_warm = R["b"]["cell"]
    e35 = {"25": pk.usable_wh(p, 25.0, pk.age80)[0], "m10": pk.usable_wh(p, -10.0, pk.age80)[0], "warm": pk.usable_wh(p, cell_warm, pk.age80)[0]}
    if round(e35["25"], 1) != rep[0] or round(e35["m10"], 1) != rep[1]:
        refuse(4, "the energy chain does not reproduce the replay's A1 line: %.2f and %.2f against %s" % (e35["25"], e35["m10"], rep[:2]))
    pkh = eb.Pack(d_in)
    pkh.c_min = hp["c_min"]
    e_hl25, k_hl = pkh.usable_wh(p, 25.0, pkh.age80)
    f35m10 = eb.interp(pk.temp, -10.0)
    c6 = comps["30Q6"]["cold"]
    f6_warm = c6[-10.0] + (c6[0.0] - c6[-10.0]) * (cell_warm - (-10.0)) / 10.0
    brackets = {"warm": (eb.interp(pk.temp, cell_warm), f6_warm), "cold": (f35m10, c6[-20.0])}
    e_hl = {"25": e_hl25, "warm": tuple(e_hl25 * f for f in brackets["warm"]), "cold": tuple(e_hl25 * f for f in brackets["cold"])}
    # the heater at the cold end: the 35E needs it only to stay above its discharge floor; the HL18650V's rows need none, and
    # a warm-up of a cold-soaked block toward its charge bands comes out of usable energy when the pack feeds it
    sh = R["selfheat"]
    c_hl = tuple(c * cm_w for c, cm_w in zip(R["blk"]["C"], (R["cmp"]["whl"] / R["cmp"]["w35"],) * 2))
    p_cells, p_loss = R["mat_split"]
    p_pack = R["heat_reg"]
    t_amb = float(R["env"]["in_use"]["min"])
    warm = {}
    for tgt_name, tgt in (("T1", draft["T1"]), ("T2", draft["T2"]), ("T5", draft["T5"])):
        for corner, (cc_, gg) in (("low", (c_hl[0], sh["g_series"][0])), ("high", (c_hl[1], sh["g_series"][1]))):
            dT = tgt - t_amb
            if dT * gg < p_cells:
                t_s = -(cc_ / gg) * math.log(1.0 - dT * gg / p_cells)
                warm[(tgt_name, corner)] = {"h": t_s / 3600.0, "wh": p_pack * t_s / 3600.0, "reach": True}
            else:
                warm[(tgt_name, corner)] = {"h": None, "wh": None, "reach": False, "ceiling": t_amb + p_cells / gg}
    h35 = {"p_coupled": R["cold"]["p_h_batt"], "wh_coupled": R["cold"]["p_h_batt"] * e35["m10"] / (p + R["cold"]["p_h_batt"])}
    objective = (48.0 * p, 72.0 * p)
    l9 = text(L4E9)
    l9m = need(l9, r"\*\*Under U-01's recommended cell\*\* \(CONDITIONAL, not taken\): usable ([\d.]+) Wh against the 35E's ([\d.]+) Wh \(([\d.]+) % less\), ([\d.]+) h\s+against ([\d.]+) h battery-only", "L4-E9's U-01 bullet", re.M)
    l9g = need(l9, r"storage shortfall above grows by at most ([\d.]+) Wh", "L4-E9's shortfall growth")
    l9_fig = {"usable": float(l9m.group(1)), "e35": float(l9m.group(2)), "pct": float(l9m.group(3)), "h": float(l9m.group(4)), "h35": float(l9m.group(5)),
              "grow": float(l9g.group(1))}
    # ---- 4. what the signed specification would change: thresholds from the conditioned corner (3o, 4d)
    cc = R["condc"]
    off_h1 = lim["discharge"][1] - R["hot"]["H1"] + R["hot"]["terms"]["thermistor interchangeability"]
    thr = {"e5_noact": cc["e5_peak"] + off_h1, "e5_cells": cc["e5_peak"], "e3o_noshut": cc["e3o_peak"] + off_h1, "e3s": R["f"]["amb"],
           "e3o_cells": cc["e3o_peak"], "floor": R["g"]["amb"], "crate": crate_drawn, "i_cell": R["kd"]["i_cell"], "graceful": d_in["pack"]["end_of_discharge"]["graceful"]["cell_v_under_load"],
           "per_100mah": e_hl25 / hp["c_min"] * 0.1}
    return {"hp": hp, "comps": comps, "beyond": beyond, "chg": chg, "lad_now": lad_now, "taper_default": taper_default, "ranges_ok": ranges_ok,
            "draft": draft, "rows_chg": rows_chg, "crate_drawn": crate_drawn, "i_draw": i_draw, "p": p, "rep": rep, "e35": e35, "e_hl": e_hl,
            "k_hl": k_hl, "brackets": brackets, "cell_warm": cell_warm, "c_hl": c_hl, "warm": warm, "h35": h35, "objective": objective,
            "l9": l9_fig, "thr": thr, "age": pk.age80, "n": (n_s, n_p), "p_pack_heat": p_pack, "p_cells_heat": p_cells, "t_amb": t_amb,
            "graceful": thr["graceful"], "cuv_now": d_in["pack"]["end_of_discharge"]["protection_cuv_v"]["value"],
            "draft_q": [int(n) for n in re.findall(r"^(\d+)\. ", text(CL_TW), re.M)]}


def u01_lines(R):
    u = R["u01"]
    hp, cm_, dr, ln = u["hp"], u["comps"], u["draft"], u["lad_now"]
    n_s, n_p = u["n"]
    L = []
    w = L.append
    w("== 9. U-01 BY MODE: the HL18650V class's limits established separately, the charging constraints, usable energy (the dependency round of 2 October 2026)")
    w("Classes here: MAKER (a maker's signed document or a maker's datasheet), MAKER-PAGE (a maker's product page: no signature, no test conditions), INFERRED")
    w("(computed, method stated), ASSUMPTION (a figure no held document gives), SESSION (a draft setting chosen here). No cell is adopted; every setting is a draft.")
    w("")
    w("9a The limits by mode (the HL18650V's own rows: Yichun Topwell Power's product page, MAKER-PAGE, `inputs/topwell-hl18650v-page-2026-10-01.json`):")
    b0, b1, b2 = hp["bands"]
    e0, e1, e2 = hp["ends"]
    rows = [
        ("CHARGE window", "%.0f to %.0f C" % hp["chg_head"], "basis (cell surface or ambient) not stated; no state of charge", "MAKER-PAGE (headline)",
         "the basis, and whether the window's low end holds at every state of charge"),
        ("CHARGE, coldest row", "%.1fC (%.2f A a cell) to %.1f V" % (b0[2], b0[2] * hp["c_basis"], b0[3]),
         "printed '%.0f %.0f<T<=%.0f C': legible from %.0f C; whether %.0f to %.0f C may charge is not legible" % (hp["garbled"][0], hp["garbled"][1], b0[1], b0[0], hp["garbled"][0], b0[0]),
         "MAKER-PAGE (row garbled)", "the band's lower edge, its current and voltage"),
        ("CHARGE, middle row", "%.1fC (%.2f A a cell) to %.1f V" % (b1[2], b1[2] * hp["c_basis"], b1[3]), "%.0f < T <= %.0f C; C taken on the %.2f Ah minimum (%.2f A = 0.2C)" % (b1[0], b1[1], hp["c_min"], hp["std_chg"]),
         "MAKER-PAGE", "the temperature basis"),
        ("CHARGE, warm row", "%.1fC (%.2f A a cell, the page's maximum continuous charge) to %.1f V" % (b2[2], hp["max_chg"], b2[3]), "%.0f < T < %.0f C; no derating toward the hot end stated" % (b2[0], b2[1]),
         "MAKER-PAGE", "any derating or time limit at 4.2 V above 45 C"),
        ("CHARGE method and end", "%s to %.1f V; termination current not stated; standard charge %.2f A" % (hp["method"], hp["v_chg"], hp["std_chg"]), "none stated", "MAKER-PAGE (termination absent)",
         "the termination current at 4.2 V and at 4.1 V"),
        ("DISCHARGE window", "%.0f to %.0f C" % hp["dis_head"], "basis not stated; no current stated with it", "MAKER-PAGE (headline)", "the basis, and the current at which the ends of the window hold"),
        ("DISCHARGE end voltage", "%.2f V (%.0f to %.0f C), %.2f V (%.0f to %.0f C), %.2f V (%.0f to %.0f C)" % (e0[2], e0[0], e0[1], e1[2], e1[0], e1[1], e2[2], e2[0], e2[1]),
         "by temperature; the current not stated", "MAKER-PAGE", "the current behind each end voltage"),
        ("DISCHARGE current", "%.0f A continuous; pulse not stated" % hp["max_dis"], "no temperature or duration stated", "MAKER-PAGE (pulse absent)",
         "the pulse current and duration; any derating with temperature"),
        ("DISCHARGE capacity", "%.2f Ah typical, %.2f Ah minimum at 0.2C" % (hp["c_typ"], hp["c_min"]), "temperature not stated (taken as the standard condition); none at the cold end", "MAKER-PAGE (cold capacity absent)",
         "the capacity at -20 and -40 C at 0.2C and 0.5C to the stated end voltages"),
        ("STORAGE", "; ".join("%.0f to %.0f C %s" % (a, b, lab) for a, b, _, lab in hp["storage"]), "state of charge, recovery and self-discharge not stated", "MAKER-PAGE",
         "the state of charge of each row, the recovery after it, the self-discharge rate"),
        ("REST at high charge, hot", "not stated", "the kit on an input in E3-O and E5 holds the pack up to its charge", "none (not on the page)",
         "the recovery after E5's ten cycles and E3-O's 4 h at the kit's state of charge"),
        ("OTHER", "internal resistance at most %.0f mOhm; about %.0f g; at least %d cycles (25 C, 0.5C / 1C), no end-of-life capacity" % (hp["ir"], hp["g"], hp["cycles"]), "the page's own figures, conditions as printed", "MAKER-PAGE",
         "the end-of-life capacity after the stated cycles"),
    ]
    for r in rows:
        w("   %-26s %s" % (r[0], r[1]))
        w("   %-26s condition: %s; class %s; the signed specification must confirm: %s" % ("", r[2], r[3], r[4]))
    w("   Comparable 18650s with makers' own sheets (context only, never a substitute for the HL18650V's figures):")
    c6, c15, c28 = cm_["30Q6"], cm_["30Q_2015"], cm_["P28A"]
    w("   - %s (%s): surface discharge %.0f to %.0f C (released under %s C), ambient charge %.0f to %.0f C, storage 1 month %.0f to %.0f C at %s;"
      % (c6["doc"].split(",")[0], c6["kind"], c6["surf_dis"][0], c6["surf_dis"][1], c6["release"], c6["amb_chg"][0], c6["amb_chg"][1], c6["st_1m"][0], c6["st_1m"][1], c6["soc"]))
    w("     capacity at 10 A: %s; full charge stored %d days at %.0f C, recovery at least %s mAh (%s %% of rated)."
      % (", ".join("%.0f %% at %.0f C" % (100 * v, k) for k, v in sorted(c6["cold"].items())), c6["full"][0], c6["full"][1], c6["full"][2][0], c6["full"][2][1]))
    w("   - %s (%s): surface discharge %.0f to %.0f C; storage 1 month %.0f to %.0f C at %s, recovery %s %%."
      % (c15["doc"].split(",")[0], c15["kind"], c15["surf_dis"][0], c15["surf_dis"][1], c15["st_1m"][0], c15["st_1m"][1], c15["soc"], c15["rec"]))
    w("   - %s (%s: %s): ambient charge %.0f to %.0f C, discharge %.0f to %.0f C; no storage clause."
      % (c28["doc"].split(",")[0], c28["kind"], c28["ref_only"], c28["charge"][0], c28["charge"][1], c28["discharge"][0], c28["discharge"][1]))
    w("   So signed sheets reach a surface discharge of +80 C, storage to -30 C and a cold discharge to -40 C; the page's rows beyond every comparable: %s."
      % ", ".join("%s (%s)" % (k, v) for k, v in u["beyond"].items()))
    w("   Those rows are the ones most exposed to a narrower signed figure.")
    w("")
    w("9b The charging constraints in D-06's 4S3P with the drawn charger and the pack's gauge (drafts, never applied):")
    ch = u["chg"]
    w("   The BQ25731 has no cell temperature input (%s) and ends a charge only on the host's word (%s); its 4S strap is %.3f V and BATOVP is %.0f %% of"
      % (ch["no_ts"], ch["host_term"], ch["strap_v"], ch["batovp_pct"]))
    w("   ChargeVoltage (MAKER, SLUSE66A via `review-packets/battery/CHARGER-STATE-SEQUENCE.md`). The windows are the gauge's: the BQ4050's ranges T1, T2, T5, T6, T3, T4 (%s)"
      % u["ranges_ok"])
    w("   set ChargingCurrent() and ChargingVoltage() per range and hold the charge FET off below UTC (MAKER, SLUUAQ3A 14.4, 2.11); the host relays them to the charger.")
    w("   Today: UTC %.1f C (recovery %.1f C), T1 %.0f C, T3 %.0f C, T4 %.0f C, OTC %.1f C, the kit's hold below %+.0f C (THERMAL-COORDINATION.md section 4)."
      % (ln["UTC"], ln["UTC_rec"], ln["T1"], ln["T3"], ln["T4"], ln["OTC"], ln["L3"]))
    w("   Draft for the HL18650V class (SESSION; each threshold kept today's %.1f K inside its band edge, as UTC sits inside the 35E's 0 C):" % (ln["UTC"] - 0.0))
    for r in u["rows_chg"]:
        w("   CH %-46s %.0f to %.0f C (page): %.1fC = %.2f A for the pack, set %.2f A; %.2f V a cell = %.2f V (BATOVP %.2f V)"
          % (r["range"], r["band"][0], r["band"][1], r["crate"], r["i_page_pack"], r["i_set"], r["v_cell"], r["v_pack"], r["batovp"]))
    w("   CH thresholds: UTC %.1f C (recovery %.1f C), T1 %.0f C, T2 %.0f C, T5 %.0f C; T3 %.0f C, T4 %.0f C and OTC %.1f C kept (SESSION: inside the page's +60 C, for cell"
      % (dr["UTC"], dr["UTC_rec"], dr["T1"], dr["T2"], dr["T5"], dr["T3"], dr["T4"], dr["OTC"]))
    w("      life; reversed by the signed charge rows); the kit's hold below %+.0f C; the gauge's CUV from %.2f V to %.2f V a cell (the page's end above 0 C; the"
      % (dr["L3"], u["cuv_now"], dr["CUV"]))
    w("      kit's graceful line at %.2f V under load acts first); the termination current: none on the page, TI's default %.0f mA kept (ASSUMPTION)."
      % (u["graceful"], u["taper_default"]))
    w("   The drawn %.1f A is %.3fC a cell, inside the page's 0.5C from %+.0f C; below it the gauge's range must lower the set current as above." % (u["i_draw"], u["crate_drawn"], u["rows_chg"][2]["band"][0]))
    w("   Below the cold charge limit no charge starts (UTC holds the charge FET; the host starts none). The mat (U22 on VBAT = VSYS) warms the block first:")
    w("   on battery it is a discharge load under the cells' discharge rows, so its energy comes out of usable energy (9c); with an input and the charge FET")
    w("   off it is fed through VSYS by the source, CONDITIONAL on U-04's VSYS regulation (L4-E11). The 35E cannot feed it below UTD's %.1f C reading" % R["ladder"]["UTD"])
    w("   (its discharge FET is off); the HL18650V's page lets the pack feed it down to %.0f C." % hp["dis_head"][0])
    w("")
    w("9c Usable energy, not nameplate (the tree's energy chain `records/energy/energy_budget.py`, the chain behind L4-E9's battery-only figure; PS-IDLE-SPEC %.1f W," % u["p"])
    w("   the run ending at the graceful line of %.2f V a cell under load, which acts before either cell's end voltage; ageing %.2f):" % (u["graceful"], u["age"]))
    e35, eh = u["e35"], u["e_hl"]
    w("   Ageing %.2f (ASSUMPTION for the HL18650V): REQ-014 and SC-23's replacement point, the basis of the 35E's figure, so the two compare; the page gives %d cycles"
      % (u["age"], hp["cycles"]))
    w("   and no end-of-life capacity, and its hot rest at high charge is unstated (the 30Q6's signed full-charge row loses up to 20 % in 30 days at 60 C).")
    w("   35E (D-06; the chain's inputs MAKER): %.1f Wh at +25 C (%.2f h), %.1f Wh with the cells at -10 C (%.2f h, the replay's %.1f / %.1f Wh reproduced), %.1f Wh at %.2f C"
      % (e35["25"], e35["25"] / u["p"], e35["m10"], e35["m10"] / u["p"], u["rep"][0], u["rep"][1], e35["warm"], u["cell_warm"]))
    w("      (LO-01b's cells at -20 C ambient with the kit's heat). Its heater: none at that corner; with the coupling fitted %.2f W from the pack (%.2f Wh over the run);"
      % (u["h35"]["p_coupled"], u["h35"]["wh_coupled"]))
    w("      a cold-soaked start is out of scope (D-02d): the pack cannot discharge below its floor.")
    w("   HL18650V (II): %.1f Wh at +25 C (%.2f h; the chain with its %.2f Ah minimum and the 35E's rate, mean-voltage and end-fraction curves, ASSUMPTION:"
      % (eh["25"], eh["25"] / u["p"], hp["c_min"]))
    w("      the page gives none), %.1f %% less than the 35E. At the cold end the page states no capacity; context brackets (ASSUMPTION): with the cells at %.2f C,"
      % (100 * (1 - eh["25"] / e35["25"]), u["cell_warm"]))
    w("      %.1f to %.1f Wh (factor %.3f, the 35E's own at that temperature on the chain's line, to %.3f, the 30Q6's signed points at 10 A); a cold start at -20 C,"
      % (eh["warm"][0], eh["warm"][1], u["brackets"]["warm"][0], u["brackets"]["warm"][1]))
    w("      %.1f to %.1f Wh (%.4f, the 35E's own -10 C point taken as a floor, to %.3f, the 30Q6's at -20 C)."
      % (eh["cold"][0], eh["cold"][1], u["brackets"]["cold"][0], u["brackets"]["cold"][1]))
    w("      Its heater: none required by its rows. A warm-up of a cold-soaked block from %.0f C, the mat %.1f W into the cells and %.1f W at the pack, block %.0f to %.0f J/K"
      % (u["t_amb"], u["p_cells_heat"], u["p_pack_heat"], u["c_hl"][0], u["c_hl"][1]))
    w("      (the 35E's scaled by mass, ASSUMPTION), series path %.4f / %.4f W/K, taken from the pack and so out of usable energy:"
      % R["selfheat"]["g_series"])
    for tg in ("T1", "T2", "T5"):
        lo_, hi_ = u["warm"][(tg, "low")], u["warm"][(tg, "high")]
        f = lambda x: ("%.2f h, %.1f Wh" % (x["h"], x["wh"])) if x["reach"] else ("not reached (the mat alone stops at %.1f C)" % x["ceiling"])
        w("      to %s (%+.0f C): %s at the low corner; %s at the high corner" % (tg, dr[tg], f(lo_), f(hi_)))
    w("   The objective (REQ-072, 48 to 72 h at %.1f W): %.0f to %.0f Wh; both packs stay far under it (DR-01 FAIL either way)." % ((u["p"],) + u["objective"]))
    l9 = u["l9"]
    w("   Where they enter: L4-E9 section 10's U-01 bullet reads %.1f Wh against %.1f Wh (%.1f %% less), %.2f h against %.2f h (this record's first chain), and every"
      % (l9["usable"], l9["e35"], l9["pct"], l9["h"], l9["h35"]))
    w("      shortfall growing by at most %.1f Wh; this chain gives %.1f Wh, %.1f Wh less than the 35E's %.1f Wh, the same growth. REQ-014 takes the aged figure;"
      % (l9["grow"], eh["25"], e35["25"] - eh["25"], e35["25"]))
    w("      REQ-046 the charge rows of 9b and the discharge window with its end voltages; REQ-077 the idle limit of 9d (+80 C on the page). None is applied.")
    w("")
    w("9d What the signed specification would change (each row: confirmed / a narrower figure and the threshold where the architecture moves / no answer):")
    th = u["thr"]
    w("   Idle hot limit (the 30-day storage row, +80 C): confirmed, 4d's margins stand. Narrower: under %.2f C H1 acts in E5's dwell at the conditioned corner (E5's"
      % th["e5_noact"])
    w("      acceptance does not require it idle; INFERRED); under %.2f C E5's cells pass the limit; under %.2f C E3-O loses 'no shutdown'; under %.2f C E3-S fails;"
      % (th["e5_cells"], th["e3o_noshut"], th["e3s"]))
    w("      under %.2f C E3-O's cells pass it." % th["e3o_cells"])
    w("      Fallback: E3-O and E5 to (I)'s cooler (8.18 to 35.21 W at the conditioned corner, INCONCLUSIVE); E3-S has no route within D-06's pocket: requirement change A")
    w("      (the owner's: the margins shown with the pack out of the exposure; no spend, the kit not claimed at that level with its own pack).")
    w("   Storage floor (the -40 C rows): confirmed to %.0f C or lower, LO-01g closes on the cell. Narrower than %.0f C: LO-01g falls back to (III)'s primary-fed heater"
      % (th["floor"], th["floor"]))
    w("      (added energy storage, 470 to 940 Wh, an owner's ruling under D-06) or requirement change A.")
    w("   State of charge of the storage rows: at or above REQ-025's stored charge (%s), no change; only below it, the stored charge is restated (REQ-025, the owner's)"
      % R["S"]["35E_11"]["soc"])
    w("      or the row falls back as above.")
    w("   Rest at high charge, hot: a loss within TEST-PLAN's recovery line, no change; beyond it, a High Temp range charging to 4.1 V a cell above T3 (SESSION lever,")
    w("      the stored energy lower in the hot) or L4-E12's hold of the charge; not architecture-level.")
    w("   Charge below 0 C: confirmed, the drafts of 9b; refused, T1 returns to +1 C and the mat comes first, as for the 35E today: no architecture effect.")
    w("   Charge current from +10 C: at or above %.3fC, the drawn %.1f A stands; under it the set current falls and the solar day's stored energy with it (L4-E9's replay)."
      % (th["crate"], u["i_draw"]))
    w("   Continuous discharge: at or above %.1f A a cell (PS-ALLTX's 18 A), no change; under it D-06's 4S3P cannot carry PS-ALLTX with this cell: back to (I)." % th["i_cell"])
    w("   End voltage: at or under the graceful %.2f V under load, no energy change; above it usable energy falls with the end fraction." % th["graceful"])
    w("   Minimum capacity: %.2f Wh of usable energy per 100 mAh a cell (INFERRED); not architecture-level (DR-01 already FAIL)." % th["per_100mah"])
    w("   Cold capacity, cycle life, basis: they move 9c's figures and the ageing allowance, not the architecture.")
    w("   No answer: every row stays CONDITIONAL, the owner's second item cannot proceed, and U-01 stays a release gate (the existing state, needing no ruling).")
    w("   The drafted request (`clarification/topwell-hl18650v.txt`, questions %s) gained 7 to 10 this round: the cold charge band and termination, the pulse"
      % ", ".join(str(q) for q in u["draft_q"]))
    w("      current, the cold capacity, the end-of-life capacity and self-discharge; 1, 2 and 6 already ask for the storage rows with their charge and recovery,")
    w("      the basis with the rest at high charge, and the gauge's data.")
    return L


# ------------------------------------------------------------------------------------------------ 10: U-01, the consolidation (2 October 2026)
SUIT_PUB, SUIT_VENDOR, UNSUIT = "SUITABLE ON PUBLISHED EVIDENCE", "SUITABLE ONLY WITH A VENDOR ANSWER", "UNSUITABLE ON PUBLISHED EVIDENCE"


def u01c(R, pb):
    """The owner's U-01 question of 2 October 2026: charge, discharge and storage suitability evaluated separately, usable
    energy, whether published makers' specifications suffice, and the exact missing fact. Nothing is adopted."""
    S, u = R["S"], R["u01"]
    lim = S["35E_11"]
    # ---- the conservative bound on the sealed case's conductance (U-02, L4-E12 at aab69775, read at its commit)
    t12 = text(L4E12)
    m5 = need(t12, r"E5\s+60 C, the air 10 K up: lid open (\d\.\d+) \(the other coefficient ends (\d\.\d+)\), lid closed (\d\.\d+)", "L4-E12 E5 bound")
    m3 = need(t12, r"E3-O\s+55 C, the air 15 K up: lid open (\d\.\d+) \(the other coefficient ends (\d\.\d+)\), lid closed (\d\.\d+)", "L4-E12 E3-O bound")
    me = need(t12, r"The envelope's \+40 C, the air 15 K up: lid open (\d\.\d+), lid closed (\d\.\d+)", "L4-E12 +40 C bound")
    bound = {"E5": tuple(float(v) for v in m5.groups()), "E3-O": tuple(float(v) for v in m3.groups()), "+40": tuple(float(v) for v in me.groups())}
    bands = [(float(a), float(r_), float(tg), lab.strip()) for a, r_, tg, lab in
             re.findall(r"a reading of at least (\d\.\d+) W/K \((\d+\.\d) K rise\) meets (\d\.\d+) W/K: (.+)", t12)]
    if len(bands) != 6:
        refuse(4, "L4-E12's acceptance bands did not read as six rows: %s" % bands)
    # ---- the conductance each row needs, per cell (lid open with the fans for E3-O and E5; LO-01a in both lid states)
    qR, pR = R["heat"]["SURVR"]
    gblk = pb.G_BLK[0]
    t_use = float(R["env"]["in_use"]["max"])
    hl = S["HL18650V"]
    sx = R["saft"]
    u2lo = R["cmp"]["u2lo"]["BQ7720704"]
    off_h1 = lim["discharge"][1] - R["hot"]["H1"] + R["hot"]["terms"]["thermistor interchangeability"]
    limits = {"35E": {"limit": lim["discharge"][1], "noact": lim["discharge"][1] - off_h1, "u2": None},
              "HL18650V": {"limit": hl["st_30d"][1], "noact": hl["st_30d"][1] - off_h1, "u2": u2lo},
              "MP 176065 xtd": {"limit": sx["st"][1], "noact": sx["st"][1] - off_h1, "u2": u2lo}}

    def g_for(runf, limit, lo=0.2, hi=6.0):
        if runf(hi) > limit:
            return None
        if runf(lo) <= limit:
            return lo
        for _ in range(26):
            mid = (lo + hi) / 2.0
            if runf(mid) > limit:
                lo = mid
            else:
                hi = mid
        return hi

    need_g = {}
    for cell, L_ in limits.items():
        rows = {}
        # LO-01a, steady on the pack at +40 C: the cells' own criterion, the binding protector, and the complete pass (the air's, common)
        g_cell = lambda tl: (qR + pR) / (tl - t_use - pR / gblk)
        rows["LO-01a"] = {"cell limit": g_cell(L_["limit"]), "no hot stop": g_cell(L_["noact"]),
                          "U2 at today's network": (g_cell(L_["u2"]) if L_["u2"] else None), "complete pass (the SGP41's air, common)": R["gov"]["all"][4]}
        for row, runf in (("LO-01d", R["run3g"]), ("LO-01e", R["run5g"])):
            rows[row] = {"cell limit": g_for(runf, L_["limit"]), "no hot stop": g_for(runf, L_["noact"]),
                         "U2 at today's network": (g_for(runf, L_["u2"]) if L_["u2"] else None)}
        need_g[cell] = rows
    peaks_bound = {"E3-O": R["run3g"](bound["E3-O"][0]), "E5": R["run5g"](bound["E5"][0])}
    row_bound = {"LO-01a": (bound["+40"][1], "+40 C lid closed"), "LO-01d": (bound["E3-O"][0], "E3-O lid open"), "LO-01e": (bound["E5"][0], "E5 lid open")}
    holds = {cell: {row: {k: (g is not None and g <= row_bound[row][0]) for k, g in crit.items()} for row, crit in rows.items()} for cell, rows in need_g.items()}
    lid_open_a = {cell: {k: (g is not None and g <= bound["+40"][0]) for k, g in rows["LO-01a"].items()} for cell, rows in need_g.items()}
    heat_I = sum(R["heat"]["IDLESPEC"])
    cold_bound = -20.0 + heat_I / bound["+40"][0]
    # the charge window at the bound: the highest ambient at which a running kit's cells sit under T3 (42 C) at PS-IDLE-SPEC
    chg_ceiling = R["u01"]["lad_now"]["T3"] - heat_I / bound["+40"][0]
    tau_kit_h = (R["C_kit"][1] / bound["E5"][2]) / 3600.0
    lag24 = math.exp(-24.0 / tau_kit_h)
    # ---- the candidates within the arrangement (a 4S pack in D-06's pocket, Li-ion at the 14.4 V class)
    room = R["room"]
    rc = R["rows_cm"]
    design_room = {"axis": 2 * (rc["M5"] - 1.0), "across": (rc["M4b"] - 1.0) + (2.0 - 1.0), "height": rc["M6"] - 1.0}
    base = (lim["dims"][1], lim["dims"][0])              # the 35E's length and diameter
    fitA = {"axis": 2 * sx["h"] - 2 * base[0], "across": sx["w"] - 3 * base[1], "height": 2 * sx["t"] - 2 * base[1]}
    fitB = {"axis": 2 * sx["w"] - 2 * base[0], "across": sx["h"] - 3 * base[1], "height": 2 * sx["t"] - 2 * base[1]}
    wrap_35 = R["blk"]["Y"] * 1000.0 - 2 * base[0] if R["blk"]["Y"] < 1 else R["blk"]["Y"] - 2 * base[0]
    wrap_left = (R["blk"]["Y"] * 1000.0 if R["blk"]["Y"] < 1 else R["blk"]["Y"]) + design_room["axis"] - 2 * sx["h"]
    fit = {"A": fitA, "B": fitB, "design_room": design_room, "worst_room": dict(room), "wrap_35": wrap_35, "wrap_left": wrap_left,
           "A_design": all(fitA[k] <= design_room[k] for k in fitA), "A_worst": all(fitA[k] <= room[k] for k in ("axis", "across", "height")),
           "B_design": all(fitB[k] <= design_room[k] for k in fitB)}
    # usable energy on the tree's chain: 4S1P at the sheet's typical capacity, and at an assumed minimum (the 35E's own minimum over typical)
    import yaml
    sp_ = importlib.util.spec_from_file_location("energy_budget_l4e10c", path(EB_PY))
    eb = importlib.util.module_from_spec(sp_)
    sp_.loader.exec_module(eb)
    d_in = yaml.safe_load(open(path(EB_IN), encoding="utf-8"))
    p = float(d_in["model_states"]["PS-IDLE-SPEC"]["plan"])
    pks = eb.Pack(d_in)
    typ_over = d_in["pack"]["capacity_min_ah"]["value"] / d_in["pack"]["capacity_typ_ah"]["value"]
    e_sx = {}
    for lab, c_ in (("typical", sx["c_typ"]), ("assumed minimum", sx["c_typ"] * typ_over)):
        pks.c_min = c_
        e_, k_ = pks.usable_wh(p, 25.0, pks.age80, n_p=1)
        e_sx[lab] = {"c": c_, "wh": e_, "h": e_ / p, "i_cell": k_["i_cell"]}
    i_alltx = pb.I_PEAK
    price = json.load(open(path(PRICES2), encoding="utf-8"))
    nz = float(need(price["verbatim"], r"\$ (\d+\.\d\d)", "Saft price").group(1))
    cands = [
        {"name": "Saft MP 176065 xtd (prismatic Li-ion, 4S1P)", "class": "MAKER datasheet (Doc. n 31109-2-0625, June 2025), held back",
         "rows": "every cell limit row: charge -30 to +85 C, discharge -40 to +85 C, storage allowable -40 to +85 C",
         "energy": "%.1f Wh nominal (typical); %.1f to %.1f Wh usable, %.2f to %.2f h" % (4 * sx["e_nom"], e_sx["assumed minimum"]["wh"], e_sx["typical"]["wh"], e_sx["assumed minimum"]["h"], e_sx["typical"]["h"]),
         "fit": "not as the 35E block is built: along the axis +%.2f mm against %.2f mm as designed; only with at most %.2f mm of wrap and spacers there (the 35E block uses %.2f mm)" % (fitA["axis"], design_room["axis"], wrap_left, wrap_35),
         "cost": "NZ$ %.2f a cell (a distributor's listing archived in January 2025), NZ$ %.2f for four" % (nz, 4 * nz),
         "downstream": "D-06 restated (the cell, 4S1P prismatic, about %.0f Wh nominal); REQ-046 and REQ-077's cell-derived numbers; U2 to the 83 C variant and the ladder under +85 C; the gauge's 1P data; a prismatic holder; the charger's 16.8 V and the CUV's 2.50 V unchanged" % (4 * sx["e_nom"])},
        {"name": "Yichun Topwell Power HL18650V (18650 Li-ion, 4S3P)", "class": "MAKER-PAGE (a product page)",
         "rows": "every row on the page, none on a specification", "energy": "121.0 Wh nominal; %.1f Wh usable, %.2f h" % (u["e_hl"]["25"], u["e_hl"]["25"] / p),
         "fit": "+0.50 mm along the axis against 0.77 mm at the worst stack", "cost": "USD %.2f a cell (a marketplace seller), about USD %.0f a pack" % (R["price_hl"], 12 * R["price_hl"]),
         "downstream": "D-06 restated (about 121 Wh); REQ-046 and REQ-077; U2, the ladder, the gauge's data and cold ranges (section 9)"},
        {"name": "Lithium Werks APR18650M1B (18650 LiFePO4, 4S3P)", "class": "MAKER product page",
         "rows": "LO-01g only (storage -40 to 70 C); not +71 C, not E3-O or E5 (discharge to 60 C)", "energy": "%.1f Wh nominal" % R["beyond"]["lfp"]["pack_wh_nom"],
         "fit": "the 18650 block", "cost": "not read", "downstream": "a 13.2 V class pack: the charger, the gauge and U2 changed (outside the 14.4 V class: a proposal, not a candidate)"},
    ]
    # ---- suitability by mode
    suit = {
        "35E": {"doc": "Samsung INR18650-35E Ver. 1.1 (MAKER, filed)",
                "charge": (SUIT_PUB, "LO-01c (REQ-046's 0 to 45 C at the surface, Ver. 1.1 3.12) and the cold charge (REQ-046: below 0 C the mat warms the pack first; C09, the cells to 12.44 C)"),
                "discharge": [(SUIT_PUB, "LO-01a (+40 C in use, D-02) and LO-01b (-20 C once warm, D-02d) against -10 to +60 C"),
                              (UNSUIT, "LO-01d (+55 C, D-02a, TEST-PLAN E3-O): the cells reach %.2f to %.2f C, over +60 C at every corner" % (R["pcm_res"]["best"]["e3o_peak_none"], R["pcm_res"]["worst"]["e3o_peak_none"]))],
                "storage": [(SUIT_PUB, "LO-01h (D-02, REQ-025: 3 months -20 to +45 C, a year -20 to +25 C) and E3-T's +58 C (1 month to 60 C at 30 %)"),
                            (UNSUIT, "LO-01f (+71 C, D-02a, E3-S), LO-01g (-33 C, D-02a, E4-S) and LO-01e (E5's dwell, SC-03: the idle pack %.2f C at the conditioned corner) against 1 month -20 to +60 C" % R["condc"]["e5_peak"])]},
        "HL18650V": {"doc": "Yichun Topwell Power's product page (MAKER-PAGE)",
                     "charge": (SUIT_VENDOR, "LO-01c and the cold charge: the page's rows, its coldest garbled, no termination (section 9a); the mat route serves the cold charge as for the 35E"),
                     "discharge": [(SUIT_VENDOR, "LO-01a, LO-01b, LO-01d: the page's -40 to +85 C, no basis, no pulse, no cold capacity")],
                     "storage": [(SUIT_VENDOR, "LO-01e, LO-01f, LO-01g, LO-01h: the page's rows, no state of charge and no recovery")]},
        "MP 176065 xtd": {"doc": "Saft MP 176065 xtd, Doc. n 31109-2-0625 (MAKER datasheet)",
                          "charge": (SUIT_PUB, "LO-01c (charge %.0f to +%.0f C, CC/CV %.1f V, %.1f A at most; the drawn %.1f A inside) and the cold charge by the mat (the sheet asks Saft only for charging under 0 C)" % (sx["chg"][0], sx["chg"][1], sx["v_chg"], sx["i_chg"], pb.ICHG)),
                          "discharge": [(SUIT_PUB, "LO-01a, LO-01b, LO-01d against %.0f to +%.0f C and %.0f A continuous (the kit's %.0f A)" % (sx["dis"][0], sx["dis"][1], sx["i_cont"], pb.I_CONT)),
                                        (SUIT_VENDOR, "PS-ALLTX's %.0f A for 60 s on one string: the sheet's %.0f A pulses state no duration" % (i_alltx, sx["i_pulse"]))],
                          "storage": [(SUIT_PUB, "LO-01e, LO-01f, LO-01g, LO-01h against the allowable %.0f to +%.0f C, which states no time or charge restriction (INFERRED: it covers 24 h at the stored charge); recommended +%.0f to +%.0f C" % (sx["st"][0], sx["st"][1], sx["st_rec"][0], sx["st_rec"][1]))]}}
    return {"bound": bound, "bands": bands, "limits": limits, "need": need_g, "peaks_bound": peaks_bound, "cold_bound": cold_bound,
            "chg_ceiling": chg_ceiling, "tau_kit_h": tau_kit_h, "lag24": lag24, "fit": fit, "e_sx": e_sx, "nz": nz, "cands": cands, "suit": suit,
            "i_alltx": i_alltx, "p": p, "design_room": design_room, "row_bound": row_bound, "holds": holds, "lid_open_a": lid_open_a}


def band_for(bands, g):
    """The acceptance band of L4-E12's one-point experiment whose target covers a need of g W/K (None if above every target)."""
    ok = [b for b in bands if b[2] >= g]
    return min(ok, key=lambda b: b[2]) if ok else None


def u01c_lines(R):
    c, u = R["u01c"], R["u01"]
    sx = R["saft"]
    L = []
    w = L.append
    w("== 10. U-01 CONSOLIDATED (the owner's question of 2 October 2026): suitability by mode, the conductance bound, published specifications, the missing fact")
    w("No cell is adopted; the adoption stays the owner's (D-06's cell and energy, the spend). Classes as section 9.")
    w("")
    rc, ro = R["rows_cm"], R["rows_cm_old"]
    w("10a The pocket's room, corrected (the independent verifier's item 3): CASE-MARGINS' rows are now split on unescaped pipes and read in the 'Chosen: nominal'")
    w("   column by its header. M4b %.2f, M5 %.2f, M6 %.2f mm (the earlier reading took M5 at %.2f mm, the superseded flat-floor figure, because its margin text"
      % (rc["M4b"], rc["M5"], rc["M6"], ro["M5"]))
    w("   carries escaped pipes). The room as designed moves from %.4f L to %.4f L; at the worst stack %.4f L, unchanged. What moved: E5's latent storage at the best"
      % (R["spare_L_old"], R["spare_L"][1], R["spare_L"][0]))
    w("   corner (%.3f L) no longer fits, so (III)'s E5 route is REJECTED within the pocket (it was INCONCLUSIVE, a marginal fit); every other fit and rejection"
      % R["pcm_res"]["best"]["e5_L"])
    w("   stands (E3-O's best corner %.3f L still inside; E3-S, E5's other corners and the primary cells still outside)." % R["pcm_res"]["best"]["e3o_L"])
    w("")
    w("10b Suitability by mode (per cell; the rows each mode serves, with their sources):")
    for cell, d in c["suit"].items():
        w("   %s (%s):" % (cell, d["doc"]))
        w("      CHARGE     %s: %s" % d["charge"])
        for v, why in d["discharge"]:
            w("      DISCHARGE  %s: %s" % (v, why))
        for v, why in d["storage"]:
            w("      STORAGE    %s: %s" % (v, why))
    w("   The cell limits are the cell's; whether the cells stay inside them in LO-01a, LO-01d and LO-01e is the enclosure's (10c).")
    w("")
    b = c["bound"]
    w("10c The conductance bound carried into the thermal routes (U-02, L4-E12 at aab69775, MODELED on INFERRED coefficients, the fans' flow credited at zero):")
    w("   E3-O: lid open %.3f W/K (the coefficients' other ends %.3f), lid closed %.3f; E5: lid open %.3f (%.3f), lid closed %.3f; +40 C: lid open %.3f, lid closed %.3f."
      % (b["E3-O"] + b["E5"] + b["+40"]))
    w("   T-H1's one-point acceptance (lid open, the fans on): " + "; ".join("%.3f W/K (target %.3f)" % (r_[0], r_[2]) for r_ in c["bands"]) + ".")
    w("   On the bound, at the conditioned corner's other parameters: E3-O's cells peak at %.2f C and E5's at %.2f C." % (c["peaks_bound"]["E3-O"], c["peaks_bound"]["E5"]))
    w("   The conductance each row needs (W/K; E3-O and E5 lid open with the fans, the corner's other parameters at their worst; LO-01a steady on the pack, judged")
    w("   on the lid-closed bound since E3-L runs lid closed). 'U2 at today's network' is the 83 C variant on today's thermistor network (INFERRED), a design choice that")
    w("   a re-derived network can move; the cell limit and the no-hot-stop line are the rows' own:")
    for cell, rows in c["need"].items():
        for row, crit in rows.items():
            parts = []
            for k, g in crit.items():
                if g is None and k == "U2 at today's network":
                    continue
                if g is None:
                    parts.append("%s: none suffices (over 6 W/K)" % k)
                    continue
                bnd = band_for(c["bands"], g)
                if c["holds"][cell][row][k]:
                    parts.append("%s %.3f, HOLDS on the bound" % (k, g))
                else:
                    parts.append("%s %.3f, %s" % (k, g, ("T-H1 to read at least %.3f" % bnd[0]) if bnd else "over every band of the one-point experiment"))
            w("   %-14s %-7s %s" % (cell, row, "; ".join(parts)))
    w("   LO-01a's readings are lid closed (E3-L): the one-point experiment is lid open, so the full T-H1 gives them (`l4e12/T-H1-PROCEDURE-DRAFT.md`).")
    w("   The bound per row: LO-01a %.3f (%s), LO-01d %.3f (%s), LO-01e %.3f (%s); LO-01a lid open on the bound %.3f W/K."
      % (c["row_bound"]["LO-01a"] + c["row_bound"]["LO-01d"] + c["row_bound"]["LO-01e"] + (c["bound"]["+40"][0],)))
    lo = c["lid_open_a"]
    w("   Lid open at +40 C on the bound: the cell limit holds for %s; the no-hot-stop line for %s."
      % (", ".join(k for k, v in lo.items() if v["cell limit"]) or "none", ", ".join(k for k, v in lo.items() if v["no hot stop"]) or "none"))
    w("   So, carried into the routes: LO-01a's complete pass (the SGP41's air, %.3f W/K) and LO-01e lie over the bound for every cell: T-H1 decides them."
      % R["gov"]["all"][4])
    w("   LO-01d holds on the bound only with the MP 176065 xtd (cell limit and no hot stop, with U2's network re-derived above the hot stop); the HL18650V needs")
    w("   %.3f W/K and the 35E %.3f W/K (cell limit), the 35E's no-hot-stop line none." % (c["need"]["HL18650V"]["LO-01d"]["cell limit"], c["need"]["35E"]["LO-01d"]["cell limit"]))
    w("   Rows that hold on the bound for every cell: LO-01b (the cells at about %+.0f C at -20 C ambient: warmer, not colder); LO-01c (the gauge holds charging off;"
      % c["cold_bound"])
    w("   a running kit at PS-IDLE-SPEC reaches T3's %.0f C window only below %+.1f C ambient on the bound, an energy consequence for L4-E9, not a cell limit; a"
      % (u["lad_now"]["T3"], c["chg_ceiling"]))
    w("   wide-temperature cell's charge rows would move that ceiling only with a re-derived T3);")
    w("   LO-01f, LO-01g and LO-01h (zero power: the kit's time constant rises to %.1f h and the cells still follow the ambient within %.3f of the step in 24 h, so"
      % (c["tau_kit_h"], c["lag24"]))
    w("   these rows are the cell's rating alone).")
    w("")
    w("10d Do published specifications suffice? Candidates within the arrangement (a 4S Li-ion pack at the 14.4 V class in D-06's pocket), at most three:")
    w("   Saft MP 176065 xtd (MAKER, %s): %.1f Ah typical at C/5 to %.1f V at +25 C, %.2f V, %.1f Wh; %.0f A continuous, %.0f A pulses (no duration); %.2f x %.1f x %.1f mm"
      % (sx["doc"], sx["c_typ"], sx["cut"], sx["v_nom"], sx["e_nom"], sx["i_cont"], sx["i_pulse"], sx["t"], sx["w"], sx["h"]))
    w("   (sleeved, the thickness at 100 %% charge and beginning of life, growing with temperature and life), %.0f g; charge %.0f to +%.0f C, discharge %.0f to +%.0f C,"
      % (sx["g"], sx["chg"][0], sx["chg"][1], sx["dis"][0], sx["dis"][1]))
    w("   storage recommended +%.0f to +%.0f C, allowable %.0f to +%.0f C; CC/CV to %.1f V at %.1f A at most (under 0 C 'consult Saft'). As 4S1P: %.2f V nominal, %.1f V full, %.1f V cut-off."
      % (sx["st_rec"] + sx["st"] + (sx["v_chg"], sx["i_chg"], 4 * sx["v_nom"], 4 * sx["v_chg"], 4 * sx["cut"])))
    f = c["fit"]
    w("   Fit in D-06's pocket (orientation A, two cells along the axis, two high): growth +%.2f / +%.2f / +%.2f mm (axis, across, height) against %.2f / %.2f / %.2f as designed"
      % (f["A"]["axis"], f["A"]["across"], f["A"]["height"], f["design_room"]["axis"], f["design_room"]["across"], f["design_room"]["height"]))
    w("      and %.2f / %.2f / %.2f at the worst stack. With the 35E block's own wrap it fits neither as designed (%s) nor at the worst stack (%s); orientation B (the"
      % (f["worst_room"]["axis"], f["worst_room"]["across"], f["worst_room"]["height"], f["A_design"], f["A_worst"]))
    w("      width along the axis) not as designed either (%s). Along the axis %.2f mm would remain for wrap and spacers where the 35E block uses %.2f mm (INFERRED from the"
      % (f["B_design"], f["wrap_left"], f["wrap_35"]))
    w("      block's 133.5 mm): the fit is CONDITIONAL on a wrap of at most that and on M5's chosen placement (CASE-MARGINS M5, OPEN: T4); failing it, the pocket")
    w("      changes and the candidate becomes a proposal for the owner (D-06's pocket).")
    es = c["e_sx"]
    w("   Usable energy (the tree's chain, 4S1P, PS-IDLE-SPEC %.1f W, aged 0.80, the 35E's curve shapes, ASSUMPTION): %.1f Wh at the typical %.2f Ah (%.2f h, %.2f A a cell),"
      % (c["p"], es["typical"]["wh"], es["typical"]["c"], es["typical"]["h"], es["typical"]["i_cell"]))
    w("      %.1f Wh at an assumed minimum of %.2f Ah (the 35E's minimum over typical; Saft publishes none); against the 35E's %.1f Wh and the HL18650V's %.1f Wh."
      % (es["assumed minimum"]["wh"], es["assumed minimum"]["c"], u["e35"]["25"], u["e_hl"]["25"]))
    for k, cd in enumerate(c["cands"], 1):
        w("   %d. %s [%s]" % (k, cd["name"], cd["class"]))
        w("      rows covered: %s" % cd["rows"])
        w("      energy: %s; fit: %s" % (cd["energy"], cd["fit"]))
        w("      cost: %s; downstream: %s" % (cd["cost"], cd["downstream"]))
    w("   Verdict: Saft's published datasheet covers every cell limit row (charge, discharge and storage) for the MP 176065 xtd; the HL18650V's need a vendor answer;")
    w("   the LiFePO4 cell fails the hot rows on its own page and leaves the 14.4 V class.")
    w("")
    w("10e The missing facts, each with its smallest resolution (no outside party is contacted; each experiment is the owner's purchase):")
    w("   Saft MP 176065 xtd route: (1) D-06's pocket (every row): whether four cells fit along the axis with at most %.2f mm of wrap and spacers as designed: a"
      % f["wrap_left"])
    w("      dimensional mock-up of four cells at the sheet's maximum dimensions in the pocket at the built stack (printed blocks; hours; no purchase); (2) LO-01a's")
    w("      mission states with PS-ALLTX: whether one cell carries %.0f A for 60 s at its temperature in use (PS-ALLTX on one"
      % c["i_alltx"])
    w("      string; the sheet's %.0f A pulses state no duration): Saft's statement (drafted: `clarification/saft-mp176065xtd.txt`), or a bench pulse of one cell at +25 C"
      % sx["i_pulse"])
    w("      and at the cold end with its surface temperature and voltage logged (one cell, NZ$ %.2f, and a 20 A load; a day); (3) the minimum capacity (the sheet" % c["nz"])
    w("      gives a typical one): measured on the lot at receipt.")
    w("   HL18650V route (LO-01f at +71 C, LO-01g at -33 C, both 24 h at the stored 30 %; LO-01e's rest at full charge; the page's +80 C idle row): the signed")
    w("      specification (the drafted request), or the smallest experiment: sample cells of the lot soaked 24 h at +71 C and 24 h at -33 C at")
    w("      the stored 30 % charge, and ten 507.6 cycles at full charge, each followed by a capacity measurement at 0.2C and +25 C against the cells' own before")
    w("      (about ten cells, USD %.2f, an oven, a -40 C freezer and a capacity tester; about 4 days for the soaks and 12 for the cycles): evidence for that lot," % (10 * R["price_hl"]))
    w("      not a production guarantee.")
    w("   Every route: T-H1 (U-02's experiment) for LO-01a's complete pass and for LO-01e, and for LO-01d unless the MP 176065 xtd is the cell; the cell moves the")
    w("      need, not the enclosure.")
    w("")
    w("10f U-01's class by the owner's exit definition: A SUPPORTED ROUTE EXISTS ON PUBLISHED MANUFACTURER EVIDENCE (the Saft MP 176065 xtd as a 4S1P pack in")
    w("   D-06's pocket, every cell limit row covered by its datasheet), ADOPTION PENDING the owner's approval (D-06's cell and energy, about %.0f Wh nominal, and the" % (4 * sx["e_nom"]))
    w("   spend). It is CONDITIONAL on two named facts with their smallest checks (the fit along the axis; the %.0f A peak's duration). With it LO-01d holds on the"
      % c["i_alltx"])
    w("   conservative bound (U2's network re-derived); LO-01a's complete pass and LO-01e rest on T-H1 for every cell. The HL18650V stays the higher-energy")
    w("   alternative (%.1f against %.1f Wh usable), resting on its vendor answer or a lot soak. Missing evidence is not shown to be impossible: each missing fact"
      % (u["e_hl"]["25"], c["e_sx"]["typical"]["wh"]))
    w("   has its check above.")
    return L


def saft_sheet():
    t = pdf(SAFT_MP)
    f = lambda pat, what: float(need(t, pat, what).group(1))
    rng = lambda lab: tuple(float(v) for v in need(t, r"%s\s+([-+]\d+)°C to \+(\d+)°C" % lab, "Saft " + lab).groups())
    return {"doc": "Doc. n %s" % need(t, r"Doc\. n° (\d+-\d+-\d+)", "Saft document number").group(1),
            "c_typ": f(r"Typical capacity \(at C/5 rate, \+25°C, 2\.5V cut-off\)1\s+(\d\.\d) Ah", "Saft capacity"),
            "v_nom": f(r"Nominal voltage\s+(\d\.\d+) V", "Saft voltage"), "e_nom": f(r"Nominal energy\s+(\d+\.\d) Wh", "Saft energy"),
            "i_cont": f(r"Continuous\s+(\d+) A \(~2C rate\)", "Saft continuous"), "i_pulse": f(r"Pulses\s+(\d+) A \(~4C rate\)", "Saft pulses"),
            "t": f(r"Thickness³\s+(\d+\.\d+) mm", "Saft thickness"), "w": f(r"Width\s+(\d+\.\d) mm", "Saft width"),
            "h": f(r"Height \(including terminals\)\s+(\d+\.\d) mm", "Saft height"), "g": f(r"Typical weight\s+(\d+) g", "Saft mass"),
            "cut": f(r"Typical cut-off voltage\s+(\d\.\d) V", "Saft cut-off"), "v_chg": f(r"Charging voltage\s+(\d\.\d) V", "Saft charge voltage"),
            "i_chg": f(r"Maximum continuous charge current4\s+(\d\.\d) A", "Saft charge current"),
            "chg": rng("Charge"), "dis": rng("Discharge"), "st_rec": rng("Recommended"), "st": rng("Allowable"),
            "proprietary": bool(re.search(r"Any duplication or reproduction without authorization of Saft is strictly prohibited", t)),
            "swell": bool(re.search(r"Can increase with temperature and during battery life", t))}


def main():
    R = compute()
    sys.stdout.write("\n".join(render(R)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
