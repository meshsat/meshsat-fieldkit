#!/usr/bin/env python3
"""l4e12_thermal.py: layer 4 task L4-E12 (MESHSAT-1478 under MESHSAT-1357, 2 October 2026). The kit's electronics against
the inside air at owner ruling D-02a's +55 C operating margin (TEST-PLAN E3-O) and E5's +60 C humid dwell, inside the sealed
Peli 1450 (no vent, appendix 32.53): U-02 of L4-E9's gate.

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured. No generator, registry, interface, Layer 3
file or other record is edited. Every figure carries its class: MAKER (a maker's document, page named), MODELED (the tree's
power and thermal model, records/rv-pwr/pwr_budget.py and records/hc2/pwr_red2.py, imported unchanged and reproduced
first, and W4's lumped film coefficients, records/w4/w4-scratch-thermal.py), INFERRED (the method is stated), ASSUMPTION (a
figure no held document gives, named where it is used), CONDITIONAL (a result that holds only on a stated condition).

Order of the work (the owner's rules of 1 and 2 October 2026): the acceptance read first and quoted (section 1); the
thermal state at the margins (section 2); a FEASIBILITY SCREEN of every fitted part on every board and of the bought modules
(section 3); at most three complete approaches compared for the parts that collide (section 4); the selection with its
margins and what stays conditional (section 5); the owner-question test (section 6); the downstream items (section 7); the
predicates (section 8).

Section 0 proves, before any figure is used (exit 4 otherwise): pwr_budget.py re-run in a child reproduces pwr_budget.out
and pwr_budget.json byte for byte; pwr_red2.py re-run in a child and imported here reproduces pwr_red2.out byte for byte;
v2/docs/parts/grade_check.py's build() is imported and run (it writes nothing) for the list of fitted parts. Inputs are
pinned by sha256 (exit 2 if a file differs or is missing). One held document (v2/vendor/ti/held/, ignored by git) is fetched
by fetch_held_back.py beside this file.

Run from the repository root:  python3 v2/docs/records/l4e12/l4e12_thermal.py > v2/docs/records/l4e12/l4e12_thermal.out
Needs pdftotext and PyYAML. A few seconds. Exit 2: a pinned file differs or is missing; 3: an input cannot be parsed;
4: a reproduction or a predicate failed."""
import contextlib
import hashlib
import html
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()

# ------------------------------------------------------------------------------------------------ the inputs
TP = "v2/docs/TEST-PLAN.md"
REG = "v2/ecad/tools/pcb_requirements.yaml"
CONOPS = "v2/docs/CONOPS.md"
PT = "v2/docs/feasibility/POWER-THERMAL.md"
CM = "v2/docs/CASE-MARGINS.md"
ENV_Y = "v2/ecad/tools/pcb_envelope.yaml"
APPX = "v2/docs/MESHSAT-709-geometry-appendix.md"
PB_PY = "v2/docs/records/rv-pwr/pwr_budget.py"
PB_OUT = "v2/docs/records/rv-pwr/pwr_budget.out"
PB_JSON = "v2/docs/records/rv-pwr/pwr_budget.json"
RED2_PY = "v2/docs/records/hc2/pwr_red2.py"
RED2_OUT = "v2/docs/records/hc2/pwr_red2.out"
W4_PY = "v2/docs/records/w4/w4-scratch-thermal.py"
GC_PY = "v2/docs/parts/grade_check.py"
GS_Y = "v2/docs/parts/grade-sources.yaml"
LCSC_FILL = "v2/ecad/tools/lcsc_fill.py"
CERT = "v2/release/revA/order/JLC-CERTIFIED.tsv"
NETS = ["v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net",
        "v2/ecad/pcb-c-display-c8/out/pcb-c-display.net", "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net",
        "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net", "v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net"]
GEN_B = "v2/ecad/tools/gen_sch_b.py"
GEN_C = "v2/ecad/tools/gen_sch_c.py"
GEN_D = "v2/ecad/tools/gen_sch_d.py"
GEN_E = "v2/ecad/tools/gen_sch_e.py"
# the makers' documents
CM5PDF = "v2/vendor/cm5/cm5-datasheet.pdf"
RB_HTML = "v2/vendor/rockblock/groundcontrol-docs-rockblock-9704-specification-20260927.html"
LIME_HTML = "v2/vendor/limesdr/myriadrf-limesdr-mini-2-0-page-20260925.html"
AW_PDF = "v2/vendor/wifi/asiarf-AW7915-AED_V1.pdf"
RM_PDF = "v2/vendor/quectel/quectel-rm520n-series-hardware-design-v1.1.pdf"
XEN_PDF = "v2/vendor/xenarc/xenarc-709gnk-product-manual-v2.pdf"
SA_PDF = "v2/vendor/nicerf/nicerf-sa868-datasheet-v1.3.pdf"
PCM_PDF = "v2/vendor/ti/ti-pcm2912a.pdf"
G6K_PDF = "v2/vendor/omron/omron-g6k-signal-relay.pdf"
SGP_PDF = "v2/vendor/sensirion/sgp41-datasheet.pdf"
BME_PDF = "v2/vendor/bosch/bosch-bme688.pdf"
H5007_PDF = "v2/vendor/pulse/pulse-h5007nl.pdf"
ATP19_PDF = "v2/vendor/switches/ck-atp19-series-datasheet.pdf"
ATP16_PDF = "v2/vendor/switches/ck-atp16-series-datasheet.pdf"
NKK_PDF = "v2/vendor/seals/nkk-ip-rated-switches-accessories.pdf"
FB_PDF = "v2/vendor/seals/floydbell-mc-09-530-q-spec.pdf"
PDI_PDF = "v2/vendor/pdi/pdi-e2370ks0c1-flyer.pdf"
PXPC_PDF = "v2/vendor/bulgin/bulgin-pxp4043c-usb-c-rear-panel.pdf"
B4000_PDF = "v2/vendor/bulgin/bulgin-4000-series-sealed-usb-c.pdf"
CERVOZ_PDF = "v2/vendor/storage/cervoz-m2-2242-nvme-titan.pdf"
SUNON_PDF = "v2/vendor/fans/sunon-dc-fan-catalogue-240A-pp18-40-extract.pdf"
AP64500_PDF = "v2/vendor/diodes/diodes-ap64500.pdf"
AP6320_PDF = "v2/vendor/diodes/diodes-ap63200-series-buck.pdf"
AP2112_PDF = "v2/vendor/diodes/diodes-ap2112-ldo.pdf"
TPS62933_PDF = "v2/vendor/ti/ti-tps62933.pdf"
TLV755_PDF = "v2/vendor/ti/held/ti-tlv755p-c404027.pdf"
TLV758_PDF = "v2/vendor/ti/ti-tlv758p.pdf"
TUSB8041_PDF = "v2/vendor/ti/ti-tusb8041.pdf"
TUSB2046_PDF = "v2/vendor/ti/ti-tusb2046b.pdf"
LM5176_PDF = "v2/vendor/ti/lm5176-datasheet.pdf"
BQ25731_PDF = "v2/vendor/ti/bq25731-datasheet.pdf"
LVC2G07_PDF = "v2/vendor/ti/ti-sn74lvc2g07.pdf"
LV1T08_PDF = "v2/vendor/ti/ti-sn74lv1t08.pdf"
CSD77_PDF = "v2/vendor/ti/held/ti-csd17577q5a-slps516.pdf"
CSD78_PDF = "v2/vendor/ti/held/ti-csd17578q5a-slps526.pdf"
PINS = {
    CM: "55244f94aace54ca09d98c100b9830cba75c70a4774c3ba375a14903fcaf6376",
    CONOPS: "6cb7b241cb84d7290caffa74df2622c64222dd66a2de66693e480e3a18e44281",
    APPX: "852736b661a805e36305ca6c2c91ebb76794e883a2ccd75dc3274c25d65212f1",
    TP: "42a3dff33442c86089a2c6c9dee841e8e2c8b9cbc1222a4adc311902b3c316f7",
    PT: "ad3ba27cef9e0f684f28ce81815afa86d44c4114b9bc10ff474308d875ba5788",
    GS_Y: "d9329f0c451aab09ee28c2c97e4549fa4c178405319f3429f40f88221753a4f5",
    GC_PY: "3569a5fa7f24ec60f7e0ee3d893f105c019f8a02034f401bd8d75a3d85014086",
    RED2_OUT: "835910e807d588c481951dc879e030b55d893453bd124872b9310a99bed46db6",
    RED2_PY: "5790bc7e444bebc4b6b7b6616c4641dfe602185631992d19aeb223eb51e9feec",
    PB_JSON: "5a616902d2ddab82f25d34ab55d848d06011fb6fbe48c147221d6b442783e462",
    PB_OUT: "58e40cf604804cc9d70c7fbeb1012be4552563fcc8ae7ef6755003c33acb902f",
    PB_PY: "469d0820b046ef6ff5aceadf422b4166de3d6a02bc50fa5b0c3644704f0f9556",
    W4_PY: "6c83da5f7e3e4f0f5393bfe0f609ba02c423adbadfa3661a245d0a9b778e65c3",
    'v2/ecad/pcb-a-power-a23/out/pcb-a-power.net': "6c40250c47195ebb7b2ae1388e284dc7f2fba9f2e683f654a47c98444290e8c5",
    'v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net': "3ef9b8c49a01b72834dece18a69e8637305d97bbf7342d765d28be596f0464d6",
    'v2/ecad/pcb-c-display-c8/out/pcb-c-display.net': "c9f7394594201045be328a07284328a7eef2c2f451e35e0828a98ac3e5510609",
    'v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net': "a2d48972d171aad19e943c6e77ae31c45d0d33ff3ac94100f02c6c8777bca001",
    'v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net': "2ed95a0e8069ebf8ad31f4567a14015e863182a83b6de7b3b13218488d8316d4",
    'v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net': "20c7b0795593d761f138e69ded1a92a5832e31cf89a1fec34008d1fda87c66b5",
    GEN_B: "3698cc04d8eaf75ba2104e6a246352ec12a092e107eee8ee554321fa95040cb8",
    GEN_C: "55ff8ede8851304963f571874c1f0554e05bcacc8c7f977c98f259e96d5a3f40",
    GEN_D: "54f17c8187d3bd195b2df6447a46c6bcaeb09209fe69bb3f61a7670a47585bbd",
    GEN_E: "f846e138cb53a8c63247efb3ad7b5cc44a68cb73e71699c65fd53b63c01af186",
    LCSC_FILL: "6888362e4a3295d0e1d595f65c03d5c13353d4785d7821c86e91f470a1cf6410",
    ENV_Y: "35cf43a2b7098a76abb4919685ece4d6e352331628f5f242c1492d9fcbbf2864",
    REG: "b624ac495650a3592c45a37610375fb05bf7b775042cf3de7ec8979bc46a6e50",
    CERT: "8200c1c6e7c2131ab213dcc8f871b8cb3f9977e9d35bcd0541da1b6617393fbf",
    BME_PDF: "fce73ae028a985b3265ce3dbc17ab5b7bea1ae31b7ea84c6698c7694083e2478",
    B4000_PDF: "bc353c794cafec7a6108fa6e8abdca3bc64d5e3f550d53c4741640e098365dea",
    PXPC_PDF: "cce556227a71f8956420e5deb3a72ed99d639d376ac75bd612d36d23fa6d1532",
    CM5PDF: "80070fefd8db6e8abc6e146c8b7b5fb318ba129cc1e28826936d547fde79c863",
    AP2112_PDF: "ef8d376f2ec356e29172eb9e053819a0ebdcc576dba7fc9ab0505c568427920f",
    AP6320_PDF: "ef99daa3789d835bc025dfcb4c605c5c2e6d3e7223e86d40b33e6b497ea5a722",
    AP64500_PDF: "d3bcdc7dd4ca44cb36ef893d3dbfabbd1742dfc736557777868f6ead5d0a98e8",
    SUNON_PDF: "fae7e21365939be5c3bbf156be3522b364037a637590f5079538d63456bca63b",
    LIME_HTML: "f1146105a3c09ebcf786d217fbf0053f8e6df3c5192efcf666e731281be4c4f1",
    SA_PDF: "938ef5ef5007df6bb8a3f2d2eb6878e3eac269e1f327c9a9164406b0f5152be1",
    G6K_PDF: "25d2046127b3ffa7e7a2047b7467c67587559e8e05111347260d5a892c0bec57",
    PDI_PDF: "266e2b62a3c88a08038e27c151982657a8395ef447e15549b5aebcaa2368333d",
    H5007_PDF: "76b85b47d0bd9f46cfca2281b5e5e31eba1e82f148ffda680472e5a1995c8d65",
    RM_PDF: "2bae882148b45172e009f88cbea08878f80e284dc6d44e93af5d67f6b9ed030a",
    RB_HTML: "30bad6e0074bea49bad4023b541c7d48c70e5d73e58281e7a9e3ab4d7bddcf84",
    FB_PDF: "d2dc7cd7959cdd076ef6941510c204058235744b2a87402f9746fe94daa8afc2",
    NKK_PDF: "1b5b8003ea7657807cac3880873f364fc09cea2c4d8bea4c60d47954b52ed60d",
    SGP_PDF: "331f35ed1f027a74ec79b302763f7adb920759bc055b3d2ada17822bb0005bec",
    CERVOZ_PDF: "30b3c59cd3332952f91eb825cd6bb9ebcbea3281fca4bd6a3277ddd03ce032b9",
    ATP16_PDF: "fce6061e05364e614da1d199b61cdfdc0a5ba50facb215690154710b824bdf11",
    ATP19_PDF: "ebf7ad2c6da083b2fd4805248819162cfc3cc8c4df5449901e921bc7621c2154",
    BQ25731_PDF: "3e5e927fdf63cf6a2397630987c58e947ebc80d5a1cfc93fb1fb58d98bb58973",
    CSD77_PDF: "c8595fa806a99074f64592d5e36826f7b9c4b007b950344bc013316e7212348d",
    CSD78_PDF: "f1aad251830260a563a03e367f3db4c12112433fd8dde7b4ee179b22381b7834",
    TLV755_PDF: "44ac688d7e51f85259134abcffeed6cd1ae61234dfd2b6dea2b0607d8ad0d015",
    LM5176_PDF: "98191bec36d43771affa3e1540f6e1737347c19a1602747ffb4327509550a820",
    PCM_PDF: "61d048c255190975933032c6ff712c6b780d8390cbc40821a54fd29b62adbf32",
    LV1T08_PDF: "cb0644caef3b0dedec65c793a2c19707208e377caf39a12098263fe237a49a94",
    LVC2G07_PDF: "71bbb2fc452e2949b332c030b004b094ba679ac8cce27123f806a0a6b1fde660",
    TLV758_PDF: "4a86306d6734f1f4212e897c29787a93b56724c06adf87d926cc7b603a694d12",
    TPS62933_PDF: "16ec2eac43c7374eb9e7edd7df7bdb24de6862f695e1582c68716ced4820e5f6",
    TUSB2046_PDF: "d02d0b8af5cbdb1b8186f890efdb214cb8edc50d55b9df5eed0650933a08d3db",
    TUSB8041_PDF: "b715bce72e988310d18dbc8eb041a05b5f15e4a0b690843a873abdc373a1ad87",
    AW_PDF: "af1a93ef3b484a3da4354779f0b2a8a2537c94d71025eb68b82a4d4879f8e8db",
    XEN_PDF: "ba3b1474406fdaf5c7cfc87f80f691cf983f44b0e19f8757511df13f5d6241be",
}

# ------------------------------------------------------------------------------------------------ the figures this record sets
# Cited from records not on this branch's base (read at their commits, carried as inputs and named where used):
L4E8_BALLAST_W = 2.09        # L4-E8's ballasts at the bound's worst corner, in the thermal budget once (L4-E9 IF-08 and A-20, fnd/l4e9)
L4E10_G_FLOOR = 1.6664       # L4-E10 section 4, LO-01a's governing line: the inside air at or under the SGP41's +55 C on shore (fnd/l4e10 79b2f568)
L4E10_AIR = (70.00, 75.00)   # L4-E10 section 4c: E3-O's air settles at 70.00 C, E5's dwell tends to 75.00 C at that floor
# ASSUMPTION (each used in one place, its effect printed):
FLOW_SHARE = 0.5             # the share of the representative cooler fan's free-air flow that passes a module's heatsink
CP_AIR = 1007.0              # J/kgK, air (textbook; INFERRED)
R_AIR = 287.05               # J/kgK, the gas constant of dry air (textbook; INFERRED)
P_ATM = 101325.0             # Pa
SIG_P_W, SIG_THETA = 0.02, 250.0     # a signal, logic or protection part in normal operation: at most 20 mW, at most 250 C/W
CTRL_P_W = 0.5                       # a controller driving external FETs: at most 0.5 W of its own (gate drive and bias)
PASS_P_W, PASS_THETA = 0.25, 60.0    # a pass element on a rail (eFuse, load switch, power FET): at most 0.25 W at 60 C/W
# The session's settings of the margin hold (SESSION, PROVISIONAL; section 5):
HOLD_TRIP_C, HOLD_RESTORE_C, HOLD_ALLOW_K = 64.0, 59.0, 2.0
CLASSES = ("MAKER", "MODELED", "INFERRED", "ASSUMPTION", "CONDITIONAL")


def refuse(code, msg):
    sys.stderr.write("l4e12_thermal: %s; refusing\n" % msg)
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


def page_text(rel):
    if rel.endswith(".pdf"):
        return pdf(rel)
    t = text(rel)
    if rel.endswith(".html"):
        t = re.sub(r"<script[\s\S]*?</script>", " ", t)
        t = re.sub(r"<[^>]+>", " ", t)
        t = html.unescape(t)
        t = re.sub(r"\s+", " ", t)
    return t


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse(3, "%s not found" % what)
    return m


def stmt(rel, pat, what):
    """A maker's statement read back from its document: (match, where) with the page for a PDF."""
    t = page_text(rel)
    m = need(t, pat, what)
    where = ("p.%d" % (t[:m.start()].count("\f") + 1)) if rel.endswith(".pdf") else "the page as served"
    return m, where


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


def f1(x):
    return "%.1f" % x


def f2(x):
    return "%.2f" % x


def sq(s):
    """One line, with the makers' dashes and minus signs written as a hyphen (the record's text carries no long dashes)."""
    return re.sub(r"\s+", " ", s).strip().replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")


# ------------------------------------------------------------------------------------------------ the makers' statements
def read_statements():
    """Every rating this record uses, read back from its document with its page (MAKER)."""
    S = {}

    def put(key, rel, pat, conv, what, quote_group=0):
        m, where = stmt(rel, pat, what)
        S[key] = {"v": conv(m), "doc": rel, "where": where, "quote": sq(m.group(quote_group))[:170]}

    n = lambda *g: (lambda m: tuple(float(m.group(i).replace("\u2212", "-").replace("\u2013", "-")) for i in g))
    put("cm5_op", CM5PDF, r"CM5.s overall operating temperature range is from (\S\d+)°C to \+(\d+)°C \(non-condensing\)", n(1, 2), "CM5 4.4")
    put("cm5_soc", CM5PDF, r"reduces its clock speed to keep the SoC temperature below\s+(\d+)°C", n(1), "CM5 throttling")
    put("rb_op", RB_HTML, r"Operating Temperature -(\d+)C to \+(\d+)C, <95% RH", lambda m: (-float(m.group(1)), float(m.group(2))), "RockBLOCK 9704 range")
    put("lime", LIME_HTML, r"Operating Temperature (\d+) °C to \+(\d+) °C Commercial-grade Storage Temperature (\d+) °C to \+(\d+) °C",
        n(1, 2, 3, 4), "LimeSDR range")
    put("aw_op", AW_PDF, r"Operating: (\d+)°C ~ \+(\d+)°C", n(1, 2), "AW7915 operating")
    put("aw_st", AW_PDF, r"Storage : -(\d+)°C ~ \+(\d+)°C", lambda m: (-float(m.group(1)), float(m.group(2))), "AW7915 storage")
    put("rm_op", RM_PDF, r"Operating temperature range: -(\d+) °C to \+(\d+) °C", lambda m: (-float(m.group(1)), float(m.group(2))), "RM520N operating")
    put("rm_ext", RM_PDF, r"Extended temperature range: -(\d+) °C to \+(\d+) °C", lambda m: (-float(m.group(1)), float(m.group(2))), "RM520N extended")
    put("rm_st", RM_PDF, r"Storage temperature range: -(\d+) °C to \+(\d+)°C", lambda m: (-float(m.group(1)), float(m.group(2))), "RM520N storage")
    put("xen_op", XEN_PDF, r"Operating Temperature: -4°F ~ 158°F \(-(\d+)°C ~ (\d+)°C\)", lambda m: (-float(m.group(1)), float(m.group(2))), "Xenarc operating")
    put("xen_st", XEN_PDF, r"Storage Temperature: -22°F ~ 176°F \(-(\d+)°C ~ (\d+)°C\)", lambda m: (-float(m.group(1)), float(m.group(2))), "Xenarc storage")
    put("sa_op", SA_PDF, r"Working Temperature range\s+-(\d+)\s+25\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "SA868 range")
    put("sa_rx", SA_PDF, r"RX current\s+(\d+)\s+mA", n(1), "SA868 RX current")
    put("pcm_rec", PCM_PDF, r"TA\s+Operating free-air temperature\s+\u2013(\d+)\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "PCM2912A TA")
    put("pcm_bias", PCM_PDF, r"Ambient temperature under bias\s+\u2013(\d+)\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "PCM2912A bias")
    put("pcm_st", PCM_PDF, r"Storage temperature, Tstg\s+\u2013(\d+)\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "PCM2912A storage")
    put("g6k_op", G6K_PDF, r"Ambient operating temperature\s+-(\d+) to (\d+)°C \(with no icing or condensation\)", lambda m: (-float(m.group(1)), float(m.group(2))), "G6K range")
    put("sgp_op", SGP_PDF, r"Operating temperature range\s+\u2212(\d+) to \+(\d+) °C", lambda m: (-float(m.group(1)), float(m.group(2))), "SGP41 operating (Table 5)")
    put("sgp_st", SGP_PDF, r"Short-term storage temperature range11\s+\u2212(\d+) to \+(\d+) °C", lambda m: (-float(m.group(1)), float(m.group(2))), "SGP41 short-term storage")
    put("sgp_abs", SGP_PDF, r"Stress levels beyond those listed in Table 5 may cause permanent damage to the device", lambda m: True, "SGP41 Table 5 heading")
    put("sgp_short", SGP_PDF, r"Short-term storage refers to temporary conditions during, e\.g\., transport", lambda m: True, "SGP41 note 11")
    put("bme_gas", BME_PDF, r"(-40)\s+(85)\s+°C\s+Operational range1", n(1, 2), "BME688 gas sensor range")
    put("bme_st", BME_PDF, r"Storage temperature\s+≤ 65% r\.H\.\s+-(\d+)\s+\+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "BME688 storage")
    put("h5007", H5007_PDF, r"Operating Temperature (\d+)°C to (\d+)°C", n(1, 2), "H5007NL range")
    put("hx", H5007_PDF, r"HX: Extended temperature version -(\d+)°C to \+(\d+)° C", lambda m: (-float(m.group(1)), float(m.group(2))), "HX range")
    put("atp19", ATP19_PDF, r"Operating Temperature\s+-(\d+)ºC to (\d+)ºC", lambda m: (-float(m.group(1)), float(m.group(2))), "ATP19 range")
    put("atp16", ATP16_PDF, r"OPERATING TEMPERATURE: -(\d+)˚C to \+(\d+)˚C", lambda m: (-float(m.group(1)), float(m.group(2))), "ATP16 range")
    put("nkk_mbn", NKK_PDF, r"MBN Series[\s\S]{0,400}?Operating temperature \u2013(\d+)°C ~ \+(\d+)°C", lambda m: (-float(m.group(1)), float(m.group(2))), "NKK MBN range")
    put("fb_op", FB_PDF, r"Operating Temperature\s+-(\d+)_C to \+(\d+)_C", lambda m: (-float(m.group(1)), float(m.group(2))), "sounder operating")
    put("fb_st", FB_PDF, r"Storage Temperature\s+-(\d+)_C to \+(\d+)_C", lambda m: (-float(m.group(1)), float(m.group(2))), "sounder storage")
    put("pdi_op", PDI_PDF, r"Operation Temperature\s+-(\d+)~(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "e-paper range")
    S["pdi_storage_stated"] = {"v": bool(re.search(r"(?i)storage", pdf(PDI_PDF))), "doc": PDI_PDF, "where": "the whole flyer", "quote": ""}
    put("pxpc_hi", PXPC_PDF, r"Max Operating Temperature:\s+\+(\d+)°C", n(1), "PXP4043/C maximum")
    put("b4000", B4000_PDF, r"Operating temperature\s+-(\d+)°C to \+(\d+)°C", lambda m: (-float(m.group(1)), float(m.group(2))), "4000 series range")
    put("cervoz_wide", CERVOZ_PDF, r"Wide Temperature Operating:\s+-(\d+)˚C~(\d+)˚C", lambda m: (-float(m.group(1)), float(m.group(2))), "Cervoz wide grade")
    put("cervoz_std", CERVOZ_PDF, r"Standard Temperature Operating:\s+(\d+)˚C~(\d+)˚C", n(1, 2), "Cervoz standard grade")
    put("fan_cfm", SUNON_PDF, r"MF30060V2-10000-A99\s+5\s+72\s+0\.36\s+7100\s+(\d+\.\d)", n(1), "Sunon MF30060V2 flow")
    put("ap64500_th", AP64500_PDF, r"θJA\s+Junction to Ambient\s+SO-8EP\s+(\d+)", n(1), "AP64500 thetaJA")
    put("ap64500_tj", AP64500_PDF, r"TJ\s+Junction Temperature\s+\+(\d+)", n(1), "AP64500 TJ absolute")
    put("ap6320_th", AP6320_PDF, r"θJA\s+Junction to Ambient\s+TSOT26\s+(\d+)", n(1), "AP6320x thetaJA")
    put("ap6320_tj", AP6320_PDF, r"TJ\s+Junction Temperature\s+\+(\d+)", n(1), "AP6320x TJ absolute")
    put("ap2112_th", AP2112_PDF, r"SOT25\s+(\d+)\s+θJA\s+Thermal Resistance \(Junction to Ambient\)", n(1), "AP2112 thetaJA")
    put("ap2112_tj", AP2112_PDF, r"Operating Junction Temperature Range\s+\+(\d+)", n(1), "AP2112 TJ absolute")
    put("tps62933_th", TPS62933_PDF, r"RθJA\s+Junction-to-ambient thermal resistance\s+(\d+\.\d)\s+N/A", n(1), "TPS62933 thetaJA")
    put("tps62933_tj", TPS62933_PDF, r"TJ\s+Operating junction temperature\(2\)\s+\u2013(\d+)\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "TPS62933 TJ")
    put("tlv755_th", TLV755_PDF, r"RθJA\s+Junction-to-ambient thermal resistance\s+(\d+\.\d)\s+(\d+\.\d)\s+(\d+\.\d)", n(1, 2, 3), "TLV755P thetaJA")
    put("tlv755_tjabs", TLV755_PDF, r"Operating junction temperature range, TJ\s+-(\d+)\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "TLV755P TJ absolute")
    put("tlv755_tjrec", TLV755_PDF, r"TJ\s+Junction temperature\s+\u2013(\d+)\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "TLV755P TJ recommended")
    put("tlv755_iout", TLV755_PDF, r"IOUT\s+Output current\s+0\s+(\d+)\s+mA", n(1), "TLV755P output current")
    put("tlv758_th", TLV758_PDF, r"RθJA\s+Junction-to-ambient thermal resistance\s+(\d+\.\d)\s+(\d+\.\d)", n(1, 2), "TLV758P thetaJA")
    put("tlv758_tjabs", TLV758_PDF, r"Operating junction, TJ\s+\u2013(\d+)\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "TLV758P TJ absolute")
    put("tusb8041_th", TUSB8041_PDF, r"RθJA\s+Junction-to-ambient thermal resistance \(2\)\s+(\d+)", n(1), "TUSB8041 thetaJA")
    put("tusb8041_tj", TUSB8041_PDF, r"TJ\s+Operating junction temperature\s+\u2013(\d+)\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "TUSB8041 TJ")
    put("tusb2046_th", TUSB2046_PDF, r"RθJA\s+Junction-to-ambient thermal resistance\s+(\d+\.\d)", n(1), "TUSB2046 thetaJA")
    put("lm5176_th", LM5176_PDF, r"RθJA\s+Junction-to-ambient thermal resistance\s+(\d+\.\d)\s+(\d+\.\d)", n(1, 2), "LM5176 thetaJA")
    put("bq25731_th", BQ25731_PDF, r"RθJA\s+Junction-to-ambient thermal resistance \(JEDEC\(1\)\)\s+(\d+\.\d)", n(1), "BQ25731 thetaJA")
    put("lvc2g07_ta", LVC2G07_PDF, r"TA\s+Operating free-air temperature\s+\u2013(\d+)\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "SN74LVC2G07 TA")
    put("lv1t08_ta", LV1T08_PDF, r"TA\s+Operating free-air temperature\s+\u2013(\d+)\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "SN74LV1T08 TA")
    put("csd77_th", CSD77_PDF, r"RθJA\s+Junction-to-Ambient Thermal Resistance \(1\) \(2\)\s+(\d+)", n(1), "CSD17577Q5A thetaJA")
    put("csd77_tj", CSD77_PDF, r"\u2013(\d+) to (\d+)\s+°C", lambda m: (-float(m.group(1)), float(m.group(2))), "CSD17577Q5A TJ")
    put("csd78_th", CSD78_PDF, r"RθJA\s+Junction-to-Ambient Thermal Resistance \(1\) \(2\)\s+(\d+)", n(1), "CSD17578Q5A thetaJA")
    put("csd78_tj", CSD78_PDF, r"\u2013(\d+) to (\d+)\s+°C", lambda m: (-float(m.group(1)), float(m.group(2))), "CSD17578Q5A TJ")
    pt = text(PT)
    m = need(pt, r"KSZ9897RTXI:\*\* (\d+\.\d) C/W on a 6-layer JESD51 board \(DS00002330D Note 6-3\) times (\d+\.\d+) W", "KSZ figure")
    S["ksz_th"] = {"v": (float(m.group(1)), float(m.group(2))), "doc": PT, "where": "section 9.2", "quote": sq(m.group(0))}
    m = need(pt, r"PI7C9X2G404SL:\*\* (\d+\.\d) C/W times (\d+\.\d+) to (\d+\.\d+) W gives \+\d+ to \+\d+ K, with a (\d+) C junction maximum", "PI7C figure")
    S["pi7c_th"] = {"v": (float(m.group(1)), float(m.group(4))), "doc": PT, "where": "section 9.2", "quote": sq(m.group(0))}
    return S


# ------------------------------------------------------------------------------------------------ the parts read one by one
# Every bought module and every board part whose maker's range the screen's first pass finds within reach (section 3b),
# with its state in the heat stage (CONOPS 4c, after BANK-R1) and in the margin hold this record proposes (section 5).
# op / st / abs / ext name statements of read_statements(); a part with neither op nor st has no maker's range held.
PARTS = [
    dict(k="CM5", label="Raspberry Pi CM5, slot 3 (running) and slots 1, 2 (off)", where="inside", hs="powered", hold="powered",
         op="cm5_op", dev=True, match=("Compute Module 5",)),
    dict(k="RB9704", label="Ground Control RockBLOCK 9704 SMA (board B J_RB9704)", where="inside", hs="powered", hold="unpowered",
         op="rb_op", dev=True, match=("RockBLOCK 9704",)),
    dict(k="LIME", label="LimeSDR Mini 2.4 (board B J_LIME)", where="inside", hs="unpowered", hold="unpowered",
         op="lime", st="lime", dev=True, match=("LimeSDR",)),
    dict(k="AW7915", label="AsiaRF AW7915-AED, two (board B J_M2C1, J_M2C3)", where="inside", hs="unpowered", hold="unpowered",
         op="aw_op", st="aw_st", dev=True, match=("AW7915",)),
    dict(k="RM520N", label="Quectel RM520N-GL (board B J_M2C2; off after BANK-R1)", where="inside", hs="unpowered", hold="unpowered",
         op="rm_op", st="rm_st", ext="rm_ext", dev=True, match=("RM520N",)),
    dict(k="XENARC", label="Xenarc 709GNK monitor (in the plate)", where="face", hs="unpowered", hold="unpowered",
         op="xen_op", st="xen_st", dev=True, match=("Xenarc",)),
    dict(k="SA868", label="NiceRF SA868 (board D U2)", where="inside", hs="powered", hold="unpowered",
         op="sa_op", dev=True, match=("SA868",)),
    dict(k="PCM2912A", label="TI PCM2912A USB audio codec (board D U6)", where="inside", hs="powered", hold="unpowered",
         op="pcm_rec", st="pcm_st", abs="pcm_bias", dev=False, match=("PCM2912A",)),
    dict(k="G6K", label="Omron G6K-2F-Y T/R relay (board D K1)", where="inside", hs="powered", hold="unpowered",
         op="g6k_op", dev=False, match=("G6K",)),
    dict(k="SGP41", label="Sensirion SGP41 battery-bay gas sensor (board E U17)", where="inside", hs="powered", hold="unpowered",
         op="sgp_op", st="sgp_st", abs="sgp_op", dev=True, match=("SGP41",)),
    dict(k="H5007NL", label="Pulse H5007NL Ethernet magnetics (board B T1)", where="inside", hs="powered", hold="powered",
         op="h5007", dev=False, match=("H5007NL",)),
    dict(k="ATP19", label="C&K ATP19 MAIN pushbutton (board C SW_MAIN)", where="face", hs="powered", hold="powered",
         op="atp19", dev=False, match=("ATP19",)),
    dict(k="ATP16", label="C&K ATP16 PI and TEST pushbuttons (board C)", where="face", hs="powered", hold="powered",
         op="atp16", dev=False, match=("ATP16",)),
    dict(k="SOUNDER", label="Floyd Bell MC-09-530-Q sounder (board C BZ1)", where="face", hs="event", hold="unpowered",
         op="fb_op", st="fb_st", dev=False, match=("Floyd Bell",)),
    dict(k="EPAPER", label="PDi E2370KS0C1 e-paper (board C)", where="face", hs="event", hold="unpowered",
         op="pdi_op", dev=True, match=("E2370KS0C1",)),
    dict(k="PXP4043C", label="Bulgin PXP4043/C sealed USB-C (connector plate)", where="wall", hs="unpowered", hold="unpowered",
         op="pxpc_hi", dev=False, match=("PXP4043/C",)),
    dict(k="NVME", label="NVMe 2242, slot 3 (not picked)", where="inside", hs="powered", hold="powered",
         op=None, dev=False, pick="cervoz_wide", match=()),
]
DEVICE_SET_NOTE = "CHO-001: the owner's device set of 6 September 2026 binds the pick (the owner brief)"


def govern(p, state, S):
    """The maker's widest statement of no damage that covers the part in this state (the rule of section 1)."""
    if state == "powered":
        for key, basis in (("abs", "absolute maximum"), ("ext", "extended range with recovery"), ("op", "operating range")):
            if p.get(key):
                v = S[p[key]]["v"]
                return v[-1] if key != "op" or p["op"] != "lime" else v[1], basis, p[key]
        return None, "no maker's range held", None
    if p.get("st"):
        v = S[p["st"]]["v"]
        hi = v[3] if p["st"] == "lime" else v[-1]
        return hi, ("short-term storage (absolute)" if p["st"] == "sgp_st" else "storage range"), p["st"]
    if p.get("op"):
        v = S[p["op"]]["v"]
        return (v[1] if p["op"] == "lime" else v[-1]), "operating range (the only statement held)", p["op"]
    return None, "no maker's range held", None


def verdict(lim, lo, hi):
    if lim is None:
        return "INCONCLUSIVE"
    if lim < lo - 1e-9:
        return "REACHED"
    if lim < hi - 1e-9:
        return "PLACEMENT"
    return "NOT REACHED"


# ------------------------------------------------------------------------------------------------ the computation
def base():
    for rel in list(PINS):
        got = sha(rel)
        if got != PINS[rel]:
            refuse(2, "%s is not the pinned file (%s)" % (rel, got[:16]))
    R = {"pins": dict(PINS)}
    # ======================================================== 0: the reproductions
    outs = {rel: open(path(rel), "rb").read() for rel in (PB_OUT, PB_JSON, RED2_OUT)}
    with tempfile.TemporaryDirectory() as td:
        jp = os.path.join(td, "pwr_budget.json")
        ch = subprocess.run([sys.executable, "-B", path(PB_PY), jp], cwd=os.path.dirname(path(PB_PY)), capture_output=True)
        R["r0a"] = ch.returncode == 0 and ch.stdout == outs[PB_OUT] and open(jp, "rb").read() == outs[PB_JSON]
    ch = subprocess.run([sys.executable, "-B", path(RED2_PY)], cwd=os.path.dirname(path(RED2_PY)), capture_output=True)
    R["r0b"] = ch.returncode == 0 and ch.stdout == outs[RED2_OUT]
    old_argv = sys.argv
    sys.argv = [path(RED2_PY)]
    try:
        red2, printed = load("pwr_red2_for_l4e12", RED2_PY, quiet=True)
    finally:
        sys.argv = old_argv
    R["r0c"] = printed.encode("utf-8") == outs[RED2_OUT]
    if not (R["r0a"] and R["r0b"] and R["r0c"]):
        refuse(4, "a reproduction failed (0a %s, 0b %s, 0c %s)" % (R["r0a"], R["r0b"], R["r0c"]))
    pb = red2.pb
    w4, _ = load("w4_for_l4e12", W4_PY)
    gc, _ = load("grade_check_for_l4e12", GC_PY)
    env_gc, inside_max_gc, rows, mods, undeclared = gc.build(TOP)
    R["gc"] = {"rows": len(rows), "mods": len(mods), "undeclared": len(undeclared), "inside_bar": inside_max_gc}
    import yaml
    reg = yaml.safe_load(text(REG))
    env = yaml.safe_load(text(ENV_Y))["ambient_c"]
    rulings = {r["id"]: r for r in reg["owner_rulings"]}
    choices = {r["id"]: r for r in reg["session_choices"]}
    recs = {r["id"]: r for r in reg["records"] if isinstance(r, dict) and "id" in r}
    S = read_statements()
    R["S"] = S

    # ======================================================== 1: the acceptance, read first
    tp = text(TP)
    cn = text(CONOPS)
    A = {}
    m = need(tp, r"then \*\*E3-O\*\* operation (\d+) hours at \+(\d+) C (deployed with the monitor and radios on, on shore or vehicle input), \*\*as a deviation with the cells kept out of the heat\*\*", "E3-O")
    A["e3o_h"], A["e3o_t"], A["e3o_config"] = float(m.group(1)), float(m.group(2)), m.group(3)
    A["e3o_pass"] = need(tp, r"\| (survive and recover \(D-02a\): no damage, no deformation, no lost data or keys, CM5 throttling logged but no shutdown, and the functional check passes once the kit is back inside the envelope with its pack refitted)", "E3's pass line").group(1)
    m = need(tp, r"\| E5 \| 507, humidity: (\d+) cycles of (\d+) hours at (\d+) percent relative humidity, (\d+) to (\d+) C, (deployed \(lid open; the case has \*\*no vent opening\*\*)", "E5")
    A["e5"] = tuple(float(m.group(i)) for i in range(1, 6))
    A["e5_config"] = need(tp, r"\| E5 \|[^\n]*?(on shore or vehicle input with the kit logging)", "E5's configuration").group(1)
    A["e5_pass"] = need(tp, r"\| E5 \|[^\n]*?\| (survive and recover \(D-02a, SC-03\): no condensation inside \(inside humidity log\), no corrosion, functional check passes) \|", "E5's pass line").group(1)
    A["controls"] = sq(need(tp, r"(the kit's controls read room-temperature cells, so of their temperature triggers only C1's inside-air trigger\s+sheds\s+modules)", "the deviation's controls").group(1))
    A["e3o_row6"] = sq(need(tp, r"\| E3-O \| (\*\*test deviation\*\*: deployed, monitor and radios on, on shore or vehicle input, the cells kept out of the heat \(the arrangement above\)) \| \+55 C, 4 h, after E3-S \|", "E3-O's row in section 6").group(1))
    A["deployed"] = sq(need(tp, r"(deployed \(open, antennas on, cables in, pack fitted, shaded, D-02e\))", "the deployed state").group(1))
    A["d02a"] = sq(rulings["D-02a"]["ruling"])
    A["d02b"] = sq(rulings["D-02b"]["ruling"])
    A["sc03"] = sq(choices["SC-03"]["taken"])
    A["req051_acc"] = sq(recs["REQ-051"]["acceptance"])
    A["cho001"] = sq(recs["CHO-001"]["statement"])
    A["heat_off"] = sq(need(cn, r"(after BANK-R1: slots 1 and 2, so bank 1 \(the SDR, the camera, the QMX, the wall port\), the 5G module \(its data is slot 2's\), both WiFi link cards, the monitor)", "the heat stage's off list").group(1))
    A["heat_on"] = sq(need(cn, r"(\*\*one module carrying the owner's D-02b example \(GNSS, the LoRa mesh, Iridium and APRS beacons\) with the SOS path, the required set \(REQ-052\)\.\*\*)", "the heat stage's set").group(1))
    A["h1_actions"] = sq(need(cn, r"(through board A's expanders on the kit bus it turns off the monitor, the pack heater, board D, PoE, the USB-C outlet, the wall port's VBUS and the PA and HF software holds; it holds the charge by the charger's own charge-inhibit bit)", "H1's actions").group(1))
    A["emcon"] = sq(need(cn, r"(radios dark \(owner ruling D-05\))", "EMCON's effect").group(1))
    gb, ge = text(GEN_B), text(GEN_E)
    A["enables"] = {
        "RB_SW_EN": sq(need(gb, r'(lvc1g08\("U503", "EMCON_HW", "RB_SW_EN", "RB_EN")', "the RockBLOCK's software enable").group(1)),
        "LORA_ON": sq(need(gb, r'(lvc1g08\("U504", "EMCON_HW", "LORA_ON", "E22_EN")', "the LoRa module's software enable").group(1)),
        "ZB_ON": sq(need(gb, r'(lvc1g08\("U505", "EMCON_HW", "ZB_ON", "E72_EN")', "the E72s' software enable").group(1)),
        "GEIGER_EN": sq(need(ge, r'(kisch\.tps22810\("U16", "\+5V_E6", "GEIGER_EN", "\+5V_GEIGER", "GEIGER_CT"\))', "the Geiger switch").group(1)),
        "SGP41 supply": sq(need(ge, r'(r\("R57", "4\.7R", "\+3V3_E6", "SGP_VDD", "R", "C23164"\))', "the SGP41's supply").group(1)),
        "U10 free pins": sq(need(ge, r'("30": "HOT_R1_G", "31": "NC", "32": "NC", "33": "\+3V3_E6", "34": "NC")', "U10's free GPIO20 to GPIO22").group(1)),
    }
    A["px0833"] = sq(need(text(CM), r"(The recommended PX0833 does not fit this plate)", "CASE-MARGINS' PX0833 refusal").group(1))
    A["c1"] = sq(need(cn, r"\| (C1, module shedding \| inside air \+50 C or any cell \+55 C \| normal to the reduced mode; reached again in the reduced mode, to the heat stage; restores 5 K below)", "C1").group(1))
    R["A"] = A

    # ======================================================== 2: the thermal state at the margins (MODELED)
    eta_fe = min(pb.ETA_FE)

    def shore(ov, scen="plan"):
        f = pb.state_full("RED", scen, ov)
        q = f["pb"] - f["outside"]
        return q, q + (f["pb"] / (pb.ETA_CHG * eta_fe) - f["pb"]), f["pb"]

    off = pb.OFF
    hold_ov = dict(red2.SURVR)
    hold_ov.update({"CM5 slot 3": pb.same(2.0, "S"), "board D (SA868 and logic)": off, "VHF PA 30 W": off, "RockBLOCK 9704": off,
                    "LoRa E22-900M30S": off, "E72 x2 (Zigbee, Thread)": off, "Geiger module": off})
    for k in hold_ov:
        if k not in [n_ for n_, _nd, _v, _s in pb.LOADS]:
            refuse(3, "the model has no load named %s" % k)
    q_hs_pack, q_hs, pb_hs = shore(red2.SURVR)
    q_hs_hi = shore(red2.SURVR, "hi")[1]
    q_gen = shore(red2.SURV)[1]
    q_m_pack, q_m, pb_m = shore(hold_ov)
    q_m_hi = shore(hold_ov, "hi")[1]
    hold_ov45 = dict(hold_ov)
    hold_ov45["CM5 slot 3"] = pb.up(2.0, 4.5, 4.5, "S")
    q_m45 = shore(hold_ov45)[1]
    hold_gen = dict(red2.SURV)   # as board B is generated: slot 2 alone; the 5G module's socket supply dropped as well
    hold_gen.update({"CM5 slot 2": pb.same(2.0, "S"), "board D (SA868 and logic)": off, "VHF PA 30 W": off, "RockBLOCK 9704": off,
                     "LoRa E22-900M30S": off, "E72 x2 (Zigbee, Thread)": off, "Geiger module": off, "5G RM520N-GL": off})
    q_m_gen = shore(hold_gen)[1]
    t_use = float(env["in_use"]["max"])
    sgp55 = S["sgp_op"]["v"][1]
    g_floor = q_hs / (sgp55 - t_use)
    qb = L4E8_BALLAST_W
    e3o_t = A["e3o_t"]
    e5_t = A["e5"][4]
    e5_lo = A["e5"][3]
    charge_extra = pb.charge_heat(pb_hs, eta_fe) - (q_hs - q_hs_pack)
    T = {"q_m_gen": q_m_gen, "q_hs": q_hs, "q_hs_pack": q_hs_pack, "q_hs_hi": q_hs_hi, "q_gen": q_gen, "q_m": q_m, "q_m_pack": q_m_pack, "q_m_hi": q_m_hi,
         "q_m45": q_m45, "g_floor": g_floor, "qb": qb, "charge_extra": charge_extra, "sgp55": sgp55, "t_use": t_use}
    T["agree_g"] = abs(g_floor - L4E10_G_FLOOR) < 5e-5
    T["air_uncond"] = (e3o_t + q_hs / g_floor, e5_t + q_hs / g_floor)
    T["agree_air"] = all(abs(a - b) < 5e-3 for a, b in zip(T["air_uncond"], L4E10_AIR))
    T["air"] = {"E3-O": e3o_t + (q_hs + qb) / g_floor, "E5": e5_t + (q_hs + qb) / g_floor}
    T["ballast_k"] = qb / g_floor
    T["charge_k"] = charge_extra / g_floor
    T["air_hi"] = e5_t + (q_hs_hi + qb) / g_floor
    T["in_env"] = t_use + (q_hs + qb) / g_floor
    T["g_floor_ballast"] = (q_hs + qb) / (sgp55 - t_use)
    # the enclosure from W4's lumped film coefficients (INFERRED): the plate and the walls between the air and the ambient
    hin, hof, how, hfl, tk = w4.H_IN_FANS, w4.H_OUT_FACE, w4.H_OUT_WALL, w4.H_OUT_FLOOR, w4.T_OVER_K_WALL
    fr = [(1.0 / ho) / (1.0 / hi + 1.0 / ho) for hi in hin for ho in hof]
    wr = [(tk + 1.0 / ho) / (1.0 / hi + tk + 1.0 / ho) for hi in hin for ho in how]
    T["f_plate"] = (min(fr), max(fr))
    T["f_wall"] = (min(wr), max(wr))
    T["w4_open"] = (w4.conductance(True, True, "low")[0], w4.conductance(True, True, "high")[0])
    T["w4_open_still"] = (w4.conductance(False, True, "low")[0], w4.conductance(False, True, "high")[0])

    def cap(i):
        """The lid-open, fans-on conductance with the inside film taken as infinite: the outer films alone (INFERRED)."""
        return (w4.A_SIDE[i] / (tk + 1.0 / how[i]) + w4.A_FLOOR[i] / (tk + 1.0 / hfl[i]) + w4.A_FACE * hof[i])

    def g_at(i_out, h_in):
        return (w4.A_SIDE[i_out] / (1.0 / h_in + tk + 1.0 / how[i_out]) + w4.A_FLOOR[i_out] / (1.0 / h_in + tk + 1.0 / hfl[i_out])
                + 1.0 / (1.0 / (w4.A_FACE * h_in) + 1.0 / (w4.A_FACE * hof[i_out])))
    T["cap"] = (cap(0), cap(1))
    T["g_low_out_high_in"] = g_at(0, hin[1])
    T["g_high_out_low_in"] = g_at(1, hin[0])
    T["g_3253_open"] = tuple(pb.G_3253["open_fans"])
    R["w4"] = {"hin": tuple(hin), "hof": tuple(hof), "how": tuple(how), "hfl": tuple(hfl), "tk": tk}
    # the running module's cooler exhaust over the mixed air (MODELED; FLOW_SHARE an ASSUMPTION)
    vdot = S["fan_cfm"]["v"][0] * 0.3048 ** 3 / 60.0 * FLOW_SHARE

    def plume(p_w, t_c):
        rho = P_ATM / (R_AIR * (t_c + 273.15))
        return p_w / (rho * CP_AIR * vdot)
    fan_w = [v for n_, _nd, v, _s in pb.LOADS if n_ == "cooler fan slot 3"][0]["RED"][1]
    T["fan_w"] = fan_w
    T["vdot_l_s"] = vdot * 1000.0
    T["d_hs"] = plume(4.5 + fan_w, T["air"]["E5"])
    T["d_hold"] = plume(2.0 + fan_w, e5_t + 10.0)
    T["e3o_h"] = A["e3o_h"]
    # E3-O as a 4 h transient from a kit stabilised at +55 C (appendix 32.53's 8 to 10 kJ/K): the steady air is the bound
    ap = text(APPX)
    k_lo, k_hi = map(float, need(ap, r"goes into about (\d+) to (\d+) kJ/K of thermal mass", "32.53 thermal mass").groups())
    import math
    T["e3o_4h"] = tuple(e3o_t + (q_hs + qb) / g_floor * (1.0 - math.exp(-A["e3o_h"] * 3600.0 * g_floor / (c * 1000.0))) for c in (k_lo, k_hi))
    T["kJ"] = (k_lo, k_hi)
    R["T"] = T

    def locs(amb, q, g, d):
        mixed = amb + (q + qb) / g
        rise = mixed - amb
        return {"amb": amb, "mixed": mixed, "plume": mixed + d, "plate": (amb + T["f_plate"][0] * rise, amb + T["f_plate"][1] * rise),
                "wall_in": (amb + T["f_wall"][0] * rise, amb + T["f_wall"][1] * rise)}

    def bounds(where, L, powered_dissipator=False):
        if where == "inside":
            return L["mixed"], L["plume"]
        if where in ("face", "wall"):
            return L["plate"][0], L["mixed"]
        return L["amb"], L["amb"]
    R["locs_now"] = {"E3-O": locs(e3o_t, q_hs, g_floor, T["d_hs"]), "E5": locs(e5_t, q_hs, g_floor, T["d_hs"])}
    return {"R": R, "pb": pb, "red2": red2, "S": S, "T": T, "A": A, "rows": rows, "mods": mods, "undeclared": undeclared,
            "locs": locs, "bounds": bounds, "shore": shore, "hold_ov": hold_ov, "gc": gc}


# ------------------------------------------------------------------------------------------------ section 3: the screen
CTRL_PARTS = ("LM5176", "BQ25731")
PASS_PARTS = ("TPS259631", "TPS22810", "BSC028N06NS", "BSC039N06NS", "AO3400A", "AO3401A", "SI2300DS", "CSD17577", "CSD17578")
OFF_IN_MARGIN = ("LT8705A",)           # board E's solar stage: no solar input in E3-O or E5 (on shore or vehicle input)
WALL_PARTS = ("PXP4043/C", "PX0833", "MIL-DTL-38999")
NOT_FITTED = {"PX0833": "CASE-MARGINS.md refuses it for the 54 V PoE feed and for fit; the sealed RJ45 is a MIL-DTL-38999 shell 15 class part"}


def node_losses(pb, ov, scen="plan"):
    saved = pb.with_overrides("RED", ov)
    try:
        cache = {}
        pb.node_power("VBAT", "RED", scen, cache)
    finally:
        pb.restore(saved)
    out = {}
    for (node, _st, _sc), (pin, _i, eta) in cache.items():
        kind = pb.NODES[node][0]
        out[node] = 0.0 if kind == "root" else pin - pin * eta
    return out


def diss_table(C, ov):
    """The parts whose own dissipation the model gives (MODELED) with the maker's thetaJA and junction limit (MAKER)."""
    S, pb = C["S"], C["pb"]
    L = node_losses(pb, ov)
    loads = {n_: v["RED"][1] for n_, _nd, v, _s in pb.LOADS}
    saved = pb.with_overrides("RED", ov)
    try:
        loads = {n_: v["RED"][1] for n_, _nd, v, _s in pb.LOADS}
    finally:
        pb.restore(saved)
    ge, gc_, gd = text(GEN_E), text(GEN_C), text(GEN_D)
    m = need(ge, r'_intent\.rail\("\+3V3_E6", 3\.3, (\d\.\d+), (\d\.\d+), "U13"', "+3V3_E6 declaration")
    e_typ, e_pk = float(m.group(1)), float(m.group(2))
    m = need(gc_, r"_P3V3_OWN = \((\d\.\d+), (\d\.\d+)\)\s+# the panel's logic loads", "board C +3V3 own")
    m2 = need(gc_, r"_EPD = \((\d\.\d+), (\d\.\d+)\)\s+# EPD_VCC", "board C EPD")
    c_typ, c_pk = float(m.group(1)) + float(m2.group(1)), float(m.group(2)) + float(m2.group(2))
    m = need(gd, r'_intent\.rail\("\+3V3_D8", 3\.3, (\d\.\d+), (\d\.\d+), "U1"', "+3V3_D8 declaration")
    d_typ, d_pk = float(m.group(1)), float(m.group(2))
    m = need(gd, r"U17 dissipates at most\s+#?\s*\((\d\.\d+) - (\d\.\d+)\) V x (\d+) mA = (\d+) mW", "board D U17")
    d17 = float(m.group(4)) / 1000.0
    th755 = S["tlv755_th"]["v"][1]
    tj755 = S["tlv755_tjabs"]["v"][1]
    hubp = (loads["three TUSB8041 hubs VDD33"] + loads["three TUSB8041 hubs VDD 1.1 V"]) / 3.0
    D = {}

    def add(b, refs, part, p, p_src, th, th_key, tj, tj_key, rated="TJ"):
        for r_ in refs:
            D[(b, r_)] = {"part": part, "p": p, "p_src": p_src, "th": th, "th_key": th_key, "tj": tj, "tj_key": tj_key, "rated": rated}
    add("A", ["U6"], "AP64500 (slot 3's 5.1 V)", L["S3"], "MODELED node S3", S["ap64500_th"]["v"][0], "ap64500_th", S["ap64500_tj"]["v"][0], "ap64500_tj", "TA")
    add("B", ["U304"], "AP64500 (slot 3's 3.3 V B)", L["S3B"], "MODELED node S3B", S["ap64500_th"]["v"][0], "ap64500_th", S["ap64500_tj"]["v"][0], "ap64500_tj", "TA")
    add("B", ["U25"], "AP63203 (+3V3_DEV)", L["D3V3"], "MODELED node D3V3", S["ap6320_th"]["v"][0], "ap6320_th", S["ap6320_tj"]["v"][0], "ap6320_tj", "TA")
    add("E", ["U12"], "AP63205 (+5V_E6)", L["E5V"], "MODELED node E5V", S["ap6320_th"]["v"][0], "ap6320_th", S["ap6320_tj"]["v"][0], "ap6320_tj", "TA")
    add("B", ["U27"], "AP2112K-2.5 (KSZ AVDDH)", L["KSZ2V5"], "MODELED node KSZ2V5", S["ap2112_th"]["v"][0], "ap2112_th", S["ap2112_tj"]["v"][0], "ap2112_tj", "TA")
    add("B", ["U40", "U50", "U60"], "AP2112K-3.3 (a supervisor's 3.3 V)", L["IOC"] / 3.0, "MODELED node IOC / 3", S["ap2112_th"]["v"][0], "ap2112_th", S["ap2112_tj"]["v"][0], "ap2112_tj", "TA")
    add("B", ["U26"], "TPS62933 (KSZ 1.2 V)", L["KSZ1V2"], "MODELED node KSZ1V2", S["tps62933_th"]["v"][0], "tps62933_th", S["tps62933_tj"]["v"][1], "tps62933_tj")
    add("A", ["U12"], "TPS62933 (board A 3.3 V)", L["A3V3"], "MODELED node A3V3", S["tps62933_th"]["v"][0], "tps62933_th", S["tps62933_tj"]["v"][1], "tps62933_tj")
    add("B", ["U106", "U206", "U306"], "TPS62933 (a hub core)", L["HUB1V1"] / 3.0, "MODELED node HUB1V1 / 3", S["tps62933_th"]["v"][0], "tps62933_th", S["tps62933_tj"]["v"][1], "tps62933_tj")
    add("B", ["U305"], "TPS62933 (slot 3's switch core)", L["S3C"], "MODELED node S3C", S["tps62933_th"]["v"][0], "tps62933_th", S["tps62933_tj"]["v"][1], "tps62933_tj")
    add("E", ["U13"], "TLV75533 DBV (+3V3_E6), at the model's plan", L["E3V3"], "MODELED node E3V3", th755, "tlv755_th", tj755, "tlv755_tjabs")
    add("C", ["U5"], "TLV75533 DBV (board C +3V3), at the declared typical", (5.0 - 3.3) * c_typ, "INFERRED from gen_sch_c's declared %.3f A" % c_typ, th755, "tlv755_th", tj755, "tlv755_tjabs")
    add("D", ["U1"], "TLV75533 DBV (+3V3_D8), at the declared typical", (5.0 - 3.3) * d_typ, "INFERRED from gen_sch_d's declared %.3f A" % d_typ, th755, "tlv755_th", tj755, "tlv755_tjabs")
    add("D", ["U17"], "TLV75801 DBV (+3V4_HUB)", d17, "gen_sch_d's own bound", S["tlv758_th"]["v"][0], "tlv758_th", S["tlv758_tjabs"]["v"][1], "tlv758_tjabs")
    add("B", ["U102", "U202", "U302"], "TUSB8041I (a hub)", hubp, "MODELED the three hubs / 3", S["tusb8041_th"]["v"][0], "tusb8041_th", S["tusb8041_tj"]["v"][1], "tusb8041_tj")
    add("D", ["U4"], "TUSB2046 (board D hub)", 3.44 * 0.040, "INFERRED from gen_sch_d's +3V4_HUB 0.040 A", S["tusb2046_th"]["v"][0], "tusb2046_th", 115.0, "grade-sources TJ row")
    add("B", ["U1"], "KSZ9897RTXI", S["ksz_th"]["v"][1], "POWER-THERMAL 9.2", S["ksz_th"]["v"][0], "ksz_th", None, None, "TA")
    add("B", ["U301"], "PI7C9X2G404SL (slot 3)", loads["PCIe switch 3.3 V slot 3"] + loads["PCIe switch 1.0 V slot 3"], "MODELED slot 3's switch rails", S["pi7c_th"]["v"][0], "pi7c_th", S["pi7c_th"]["v"][1], "pi7c_th", "TA")
    decl = {"e": (e_typ, e_pk), "c": (c_typ, c_pk), "d": (d_typ, d_pk), "iout": S["tlv755_iout"]["v"][0] / 1000.0,
            "e_decl_p": (5.0 - 3.3) * e_typ, "th755": th755, "tj755": tj755}
    return D, decl


def screen_rows(C, Lmap, D, scen_label, p2=None):
    """Every fitted line (grade_check), every module and every undeclared line: its limit, its local bounds, its rise and
    verdict for the scenario's locations Lmap = {'E3-O': locs, 'E5': locs}."""
    S = C["S"]
    out = []
    covered = set()
    for kind, code, r, lns, v, why in C["rows"]:
        part = (r.get("part") or "")
        boards = sorted(set(ln["board"] for ln in lns))
        refs = {b: sorted(set(x for ln in lns if ln["board"] == b for x in ln["refs"])) for b in boards}
        row = {"part": part, "code": code, "refs": refs, "kind": r.get("kind"), "max": r.get("max_c"), "where_gs": r.get("where", "inside")}
        pk = [p["k"] for p in PARTS if any(s in part for s in p["match"])]
        if pk:
            row["level2"] = pk[0]
        if r.get("not_a_component"):
            row["verdict"] = {"E3-O": "NO PART", "E5": "NO PART"}
            out.append(row)
            continue
        if boards == ["P"]:
            row["verdict"] = {"E3-O": "OUT OF SCOPE", "E5": "OUT OF SCOPE"}
            out.append(row)
            continue
        if "P" in refs:
            row["pack_refs_out"] = refs.pop("P")
            row["refs"] = refs
        where = {"outside_face": "face", "plate": "face", "pack": "inside"}.get(row["where_gs"], row["where_gs"])
        if where == "outside":
            where = "wall" if any(w in part for w in WALL_PARTS) else "outside"
        row["where"] = where
        rise, cls, rsrc = 0.0, "MAKER (an ambient rating: the part's own rise is inside it)", ""
        if row["kind"] == "TJ" or any(d in refs for d in []):
            hits = [D[(b, x)] for b in refs for x in refs[b] if (b, x) in D]
            if hits:
                h = max(hits, key=lambda d: d["p"] * d["th"])
                rise, cls, rsrc = h["p"] * h["th"], "MODELED dissipation x MAKER thetaJA", "%s: %.3f W x %.1f C/W" % (h["part"], h["p"], h["th"])
                if h["tj"] is not None and h["tj"] > (row["max"] or 0):
                    row["rec_max"], row["max"] = row["max"], h["tj"]
                    row["max_basis"] = "absolute maximum junction (%s)" % h["tj_key"]
            elif any(c_ in part for c_ in CTRL_PARTS):
                th = S["lm5176_th"]["v"][1] if "LM5176" in part else S["bq25731_th"]["v"][0]
                rise, cls, rsrc = CTRL_P_W * th, "ASSUMPTION (controller at %.2f W) x MAKER thetaJA" % CTRL_P_W, "%.2f W x %.1f C/W" % (CTRL_P_W, th)
            elif any(c_ in part for c_ in PASS_PARTS):
                rise, cls, rsrc = PASS_P_W * PASS_THETA, "ASSUMPTION (pass element %.2f W at %.0f C/W)" % (PASS_P_W, PASS_THETA), ""
            elif any(c_ in part for c_ in OFF_IN_MARGIN):
                rise, cls, rsrc = 0.0, "INFERRED (no solar input in E3-O or E5: unpowered)", ""
            else:
                rise, cls, rsrc = SIG_P_W * SIG_THETA, "ASSUMPTION (signal or protection part %.2f W at %.0f C/W)" % (SIG_P_W, SIG_THETA), ""
        else:
            hits = [D[(b, x)] for b in refs for x in refs[b] if (b, x) in D]
            if hits:
                h = max(hits, key=lambda d: d["p"] * d["th"])
                row["tj_info"] = {"rise": h["p"] * h["th"], "tj": h["tj"], "src": "%s: %.3f W x %.1f C/W" % (h["part"], h["p"], h["th"])}
        row.update({"rise": rise, "rise_cls": cls, "rise_src": rsrc})
        row["verdict"], row["temps"] = {}, {}
        for mg, L in Lmap.items():
            if where == "inside":
                lo, hi = L["mixed"], L["plume"]
            elif where in ("face", "wall"):
                lo, hi = L["plate"][0], L["mixed"]
            else:
                lo, hi = L["amb"], L["amb"]
            lo, hi = lo + rise, hi + rise
            row["temps"][mg] = (lo, hi)
            vd = verdict(row["max"], lo, hi)
            if "tj_info" in row and row["tj_info"]["tj"] is not None and vd == "NOT REACHED":
                vd = verdict(row["tj_info"]["tj"], lo + row["tj_info"]["rise"], hi + row["tj_info"]["rise"])
            row["verdict"][mg] = vd
        if any(n_ in part for n_ in NOT_FITTED):
            row["verdict"] = {k: "NOT FITTED" for k in row["verdict"]}
        if p2 and row.get("level2") in p2:
            row["verdict_l1"] = dict(row["verdict"])
            row["verdict"] = dict(p2[row["level2"]]["verdict"])
        out.append(row)
        covered.add(part)
    for r, v, why in C["mods"]:
        part = r.get("part", "")
        row = {"part": part, "code": "", "refs": {"module": [r.get("maker", "")]}, "kind": r.get("kind"), "max": r.get("max_c"),
               "where_gs": r.get("where", "inside"), "module": True}
        pk = [p["k"] for p in PARTS if any(s in part for s in p["match"])]
        if pk:
            row["level2"] = pk[0]
        where = {"outside_face": "face", "plate": "face", "pack": "pack"}.get(row["where_gs"], row["where_gs"])
        if "QMX" in part:
            where = "lid"
        if where == "outside":
            where = "wall" if any(w in part for w in WALL_PARTS) else "outside"
        row["where"] = where
        row["verdict"], row["temps"] = {}, {}
        if where == "pack":
            row["verdict"] = {"E3-O": "OUT OF SCOPE", "E5": "OUT OF SCOPE"}
            out.append(row)
            continue
        for mg, L in Lmap.items():
            if where == "inside":
                lo, hi = L["mixed"], L["plume"]
            elif where in ("face", "wall"):
                lo, hi = L["plate"][0], L["mixed"]
            else:
                lo, hi = L["amb"], L["amb"]
            row["temps"][mg] = (lo, hi)
            row["verdict"][mg] = verdict(row["max"], lo, hi)
        if any(n_ in part for n_ in NOT_FITTED):
            row["verdict"] = {k: "NOT FITTED" for k in row["verdict"]}
        if p2 and row.get("level2") in p2:
            row["verdict_l1"] = dict(row["verdict"])
            row["verdict"] = dict(p2[row["level2"]]["verdict"])
        out.append(row)
    for ln in C["undeclared"]:
        val = ln["value"]
        if "CSD17577" in val or "CSD17578" in val:
            key = "csd77" if "CSD17577" in val else "csd78"
            row = {"part": val.split(" ")[0], "kind": "TJ", "max": S[key + "_tj"]["v"][1], "src": key + "_tj"}
            rise, cls = PASS_P_W * S[key + "_th"]["v"][0], "ASSUMPTION (pass element %.2f W) x MAKER thetaJA %.0f C/W" % (PASS_P_W, S[key + "_th"]["v"][0])
        elif "SN74LVC2G07" in val:
            row = {"part": "SN74LVC2G07DBVR", "kind": "TA", "max": S["lvc2g07_ta"]["v"][1], "src": "lvc2g07_ta"}
            rise, cls = 0.0, "MAKER (an ambient rating)"
        elif "SN74LV1T08" in val:
            row = {"part": "SN74LV1T08DBVR", "kind": "TA", "max": S["lv1t08_ta"]["v"][1], "src": "lv1t08_ta"}
            rise, cls = 0.0, "MAKER (an ambient rating)"
        else:
            row = {"part": val[:40], "kind": None, "max": None, "src": None}
            rise, cls = 0.0, ""
        row.update({"code": ln["code"], "refs": {ln["board"]: ln["refs"]}, "where": "inside", "where_gs": "inside", "undeclared": True,
                    "rise": rise, "rise_cls": cls, "rise_src": ""})
        row["verdict"], row["temps"] = {}, {}
        for mg, L in Lmap.items():
            lo, hi = L["mixed"] + rise, L["plume"] + rise
            row["temps"][mg] = (lo, hi)
            row["verdict"][mg] = verdict(row["max"], lo, hi)
        out.append(row)
    return out


def parts_eval(C, Lmap, state_key):
    """The parts read one by one (PARTS) in a scenario: the governing limit for the part's state and the verdict."""
    S = C["S"]
    out = []
    for p in PARTS:
        st = p[state_key]
        lim, basis, key = govern(p, "powered" if st == "powered" else "unpowered", S)
        if p.get("pick"):
            lim, basis, key = S[p["pick"]]["v"][1], "the pick's line (a wide grade, e.g. Cervoz -40 to +85 C)", p["pick"]
        row = {"k": p["k"], "label": p["label"], "state": st, "lim": lim, "basis": basis, "key": key, "where": p["where"], "dev": p.get("dev", False)}
        row["temps"], row["verdict"], row["gap"] = {}, {}, {}
        for mg, L in Lmap.items():
            if p["where"] == "inside":
                lo, hi = L["mixed"], L["plume"]
            elif p["where"] in ("face", "wall"):
                lo, hi = L["plate"][0], L["mixed"]
            else:
                lo, hi = L["amb"], L["amb"]
            row["temps"][mg] = (lo, hi)
            row["verdict"][mg] = verdict(lim, lo, hi)
            row["gap"][mg] = (None if lim is None else lo - lim, None if lim is None else hi - lim)
        out.append(row)
    return out


# ------------------------------------------------------------------------------------------------ sections 4 to 8
CANDIDATES = {   # approach (b): the wider-rated part for each colliding part, its maker's statement and who may pick it
    "RB9704": (None, "OWNER (CHO-001)", "no wider-rated Iridium IMT unit in any held document"),
    "SA868": (None, "OWNER (CHO-001)", "no VHF module rated past +70 C in any held document"),
    "LIME": (None, "OWNER (CHO-001)", "its maker's page offers the commercial grade only (0 to +70 C in use and in storage)"),
    "SGP41": ("bme_gas", "OWNER (CHO-001)", "Bosch BME688 (gas sensing -40 to +85 C, storage -45 to +85 C), already on board E as U14; a second one takes I2C 0x77, which the outside pod's BME688 (32.54, deferred) then cannot use"),
    "EPAPER": (None, "OWNER (CHO-001)", "no e-paper rated past +60 C in any held document"),
    "ATP19": ("nkk_mbn", "SESSION", "NKK MBN sealed pushbutton (IP67, -30 to +85 C); its 12 mm bushing, terminals and cutout are owed"),
    "ATP16": ("nkk_mbn", "SESSION", "NKK MBN sealed pushbutton, as ATP19"),
    "H5007NL": ("hx", "SESSION", "the maker's HX (extended temperature) version, -40 to +85 C; pin compatibility not claimed"),
    "G6K": (None, "SESSION", "no signal relay rated past +70 C held; an +85 C part is a Layer 6 pick"),
    "PXP4043C": ("b4000", "SESSION", "the same maker's 4000 series sheet states -40 to +80 C for the series; the C-type's own sheet says +70 C"),
    "PCM2912A": ("pcm_bias", "SESSION", "no change: its absolute maximum ambient under bias is +125 C"),
    "SOUNDER": ("fb_st", "SESSION", "no change: muted, its storage range reaches +85 C"),
    "NVME": ("cervoz_wide", "SESSION", "the pick: a wide grade (Cervoz -40 to +85 C), not the 0 to +70 C standard grade"),
}


def g_req(q, qb, lim, amb, margin=0.0):
    room = lim - amb - margin
    return None if room <= 0 else (q + qb) / room


def compute():
    C = base()
    R, S, T, A, pb, red2 = C["R"], C["S"], C["T"], C["A"], C["pb"], C["red2"]
    locs, hold_ov = C["locs"], C["hold_ov"]
    e3o_t, e5_t, g_floor, qb = A["e3o_t"], A["e5"][4], T["g_floor"], T["qb"]
    # ======================================================== 3: the screen of the design as it stands (the heat stage at T-H1's floor)
    D_hs, decl = diss_table(C, red2.SURVR)
    R["decl"] = decl
    Lnow = R["locs_now"]
    R["parts_now"] = parts_eval(C, Lnow, "hs")
    R["screen"] = screen_rows(C, Lnow, D_hs, "now", {p_["k"]: p_ for p_ in R["parts_now"]})
    R["diss_now"] = D_hs
    # ======================================================== 4: three complete approaches
    ap = {}
    # (a) the heat path and the enclosure, the parts and the mode unchanged
    ga, a_open = {}, []
    for pr in R["parts_now"]:
        if pr["lim"] is None:
            a_open.append((pr["k"], "no maker's range held"))
            continue
        need_g = [g_req(T["q_hs"], qb, pr["lim"], amb) for amb in (e3o_t, e5_t)]
        if any(g is None for g in need_g):
            a_open.append((pr["k"], "its limit %.0f C is at or under the margin's ambient: the air cannot be cooled below it" % pr["lim"]))
        else:
            ga[pr["k"]] = max(need_g)
    gmax_a = max(ga.values())
    ga_e3o = max(g_req(T["q_hs"], qb, pr["lim"], e3o_t) for pr in R["parts_now"] if pr["k"] in ga)
    ap["a"] = {"g": ga, "gmax": gmax_a, "open": a_open, "g_e3o": ga_e3o,
               "g_m": [max(g_req(T["q_hs"], qb, R["parts_now"][[x["k"] for x in R["parts_now"]].index(k)]["lim"], e5_t, mm) or 0 for k in ga) for mm in (1.0, 2.0)],
               "plate_floor_e5": Lnow["E5"]["plate"], "g_plate": T["f_plate"][1] * (T["q_hs"] + qb) / 10.0}
    # (c) the margin hold: beyond the heat stage, on the inside air, it powers off what C1 left that is not needed to survive
    L_c_floor = {"E3-O": locs(e3o_t, T["q_m"], g_floor, T["d_hold"]), "E5": locs(e5_t, T["q_m"], g_floor, T["d_hold"])}
    parts_hold_floor = parts_eval(C, L_c_floor, "hold")
    gc_, c_open = {}, []
    for pr in parts_hold_floor:
        if pr["lim"] is None:
            c_open.append((pr["k"], "no maker's range held"))
            continue
        need_g = [g_req(T["q_m"], qb, pr["lim"], amb) for amb in (e3o_t, e5_t)]
        if any(g is None for g in need_g):
            c_open.append((pr["k"], "its limit %.0f C (%s) is at or under the margin's ambient" % (pr["lim"], pr["basis"])))
        else:
            gc_[pr["k"]] = max(need_g)
    gmax_c = max(gc_.values())
    L_c = {"E3-O": locs(e3o_t, T["q_m"], g_floor, T["d_hold"]), "E5": locs(e5_t, T["q_m"], gmax_c, T["d_hold"])}
    parts_c = parts_eval(C, L_c, "hold")
    D_hold, _ = diss_table(C, hold_ov)
    screen_c = screen_rows(C, L_c, D_hold, "hold", {p_["k"]: p_ for p_ in parts_c})
    ap["c"] = {"g": gc_, "gmax": gmax_c, "open": c_open, "L": L_c, "L_floor": L_c_floor, "parts": parts_c, "parts_floor": parts_hold_floor,
               "screen": screen_c,
               "g_m": [max(g_req(T["q_m"], qb, parts_hold_floor[[x["k"] for x in parts_hold_floor].index(k)]["lim"], e5_t, mm) or 0 for k in gc_) for mm in (1.0, 2.0)],
               "g_cm45": (T["q_m45"] + qb) / 10.0, "g_hi": (T["q_m_hi"] + qb) / 10.0}
    # the hold's trigger against the envelope: the heat stage's inside air at +40 C at T-H1's floor, the sensor in the exhaust
    env_tmp = T["in_env"] + T["d_hs"]
    ap["c"]["trip"] = {"env_tmp": env_tmp, "trip": HOLD_TRIP_C, "restore": HOLD_RESTORE_C, "allow": HOLD_ALLOW_K,
                       "never_in_env": HOLD_TRIP_C >= env_tmp + HOLD_ALLOW_K - 1e-9,
                       "before_trip_hi": HOLD_TRIP_C + T["d_hs"],
                       "stays": min(L_c["E3-O"]["mixed"], L_c["E5"]["mixed"], L_c_floor["E3-O"]["mixed"]) > HOLD_RESTORE_C,
                       "e5_low": A["e5"][3] + (T["q_hs"] + qb) / g_floor + T["d_hs"]}
    # the fallback at T-H1's floor: the hold, the +70 C modules coupled to the plate
    ap["c"]["fallback"] = {"plate": L_c_floor["E5"]["plate"], "mixed": L_c_floor["E5"]["mixed"],
                           "margin": 70.0 - L_c_floor["E5"]["plate"][1]}
    # (b) wider-rated parts, the mode and the enclosure unchanged
    bl = []
    for pr in R["parts_now"]:
        if pr["k"] not in CANDIDATES:
            continue
        key, who, note = CANDIDATES[pr["k"]]
        cand = None if key is None else S[key]["v"][-1] if key not in ("bme_gas",) else S[key]["v"][1]
        lo, hi = pr["temps"]["E5"]
        bl.append({"k": pr["k"], "who": who, "note": note, "cand": cand, "key": key,
                   "margin_e5": None if cand is None else cand - hi, "now": pr["verdict"]})
    ap["b"] = {"rows": bl}
    R["ap"] = ap
    # ======================================================== 5 and 6: the selection and the owner-question test
    route = {}
    vc = {p["k"]: p for p in parts_c}
    vn = {p["k"]: p for p in R["parts_now"]}
    collide = [k for k, p in vn.items() if any(v_ in ("REACHED", "PLACEMENT", "INCONCLUSIVE") for v_ in p["verdict"].values())]
    for k in collide:
        r_ = {}
        r_["a"] = "CONDITIONAL" if k in ga else "REJECTED"
        cb = CANDIDATES.get(k)
        if cb is None:
            r_["b"] = "INCONCLUSIVE"
        elif cb[1].startswith("OWNER"):
            r_["b"] = "OUTSIDE AUTHORITY"
        else:
            r_["b"] = "CLOSES" if cb[0] is not None else "INCONCLUSIVE"
        pc = vc[k]
        if pc["lim"] is None:
            r_["c"] = "INCONCLUSIVE"
        elif all(v_ == "NOT REACHED" for v_ in pc["verdict"].values()):
            r_["c"] = "CLOSES"
        elif all(v_ in ("NOT REACHED", "PLACEMENT") for v_ in pc["verdict"].values()):
            r_["c"] = "CONDITIONAL"
        elif k == "EPAPER":
            r_["c"] = "INCONCLUSIVE"
        else:
            r_["c"] = "REJECTED"
        r_["forced"] = all(x in ("REJECTED", "OUTSIDE AUTHORITY") for x in (r_["a"], r_["b"], r_["c"]))
        route[k] = r_
    R["route"] = route
    R["forced"] = [k for k, r_ in route.items() if r_["forced"]]
    # ======================================================== 8: the predicates
    p = {}
    p["P1 pwr_budget and pwr_red2 reproduced byte for byte before any figure"] = R["r0a"] and R["r0b"] and R["r0c"]
    p["P2 T-H1's floor and the inside air reproduce L4-E10's 1.6664 W/K, 70.00 and 75.00 C"] = T["agree_g"] and T["agree_air"]
    p["P3 the acceptance is read: survive and recover, the CM5 not shut down, C1's shedding recorded, E5 logging"] = (
        "survive and recover" in A["e3o_pass"] and "no shutdown" in A["e3o_pass"] and "C1's inside-air trigger" in A["controls"]
        and "logging" in A["e5_config"] and "survive and recover at the margin" in A["d02a"])
    scr = R["screen"]
    p["P4 every fitted line, module and undeclared line is screened"] = len(scr) == R["gc"]["rows"] + R["gc"]["mods"] + R["gc"]["undeclared"]
    lvl1 = [r_ for r_ in scr if any(v_ in ("REACHED", "PLACEMENT") for v_ in r_.get("verdict_l1", r_["verdict"]).values())]
    unread = [r_["part"] for r_ in lvl1 if "level2" not in r_ and not (r_["kind"] == "TA" and r_["max"] is not None and r_["max"] >= 80.0)]
    R["unread"] = unread
    p["P5 every part the first pass finds within reach is read one by one, or is rated to +80 C or more and over it only in the exhaust"] = not unread
    p["P6 approach (a) needs more conductance than the sealed case's outer films give at W4's low coefficients"] = gmax_a > T["cap"][0]
    p["P7 the hold never acts inside the envelope (its trigger over the heat stage's air at +40 C, the sensor in the exhaust, plus the allowance)"] = ap["c"]["trip"]["never_in_env"]
    p["P8 at the selected line every part routed by the air is inside its governing limit at the mixed air, E3-O at T-H1's floor"] = all(
        pr["lim"] is None or pr["k"] not in gc_ or (pr["temps"]["E5"][0] <= pr["lim"] + 1e-9 and pr["temps"]["E3-O"][0] <= pr["lim"] + 1e-9) for pr in parts_c)
    p["P9 the hold lowers the enclosure line: G_c under G_a"] = gmax_c < gmax_a
    p["P10 no part has every route rejected or outside authority on held evidence: no owner question is forced"] = not R["forced"]
    p["P11 every part read one by one has a governing statement or is named INCONCLUSIVE"] = all(
        (pr["lim"] is not None) or all(v_ == "INCONCLUSIVE" for v_ in pr["verdict"].values()) for pr in R["parts_now"])
    p["P12 the hold stays engaged once entered at both margins (the mixed air over its restore)"] = ap["c"]["trip"]["stays"]
    R["pred"] = p
    return R


# ------------------------------------------------------------------------------------------------ the rendering
def _refs(refs):
    out = []
    for b, xs in refs.items():
        if b == "module":
            out.append("module")
            continue
        out.append("%s %s%s" % (b, ", ".join(xs[:4]), " (+%d)" % (len(xs) - 4) if len(xs) > 4 else ""))
    return "; ".join(out)


def _rng(lo, hi):
    return "%s..%s" % (f1(lo), f1(hi))


def render(R):
    S, T, A, ap = R["S"], R["T"], R["A"], R["ap"]
    out = []
    w = out.append
    w("l4e12_thermal.py: layer 4 task L4-E12 (MESHSAT-1478 under MESHSAT-1357). The kit's electronics against the inside air at")
    w("D-02a's +55 C operating margin (E3-O) and E5's +60 C dwell in the sealed Peli 1450. Prototype design, desk arithmetic: nothing")
    w("is bought, built, powered or measured. Classes: MAKER, MODELED, INFERRED, ASSUMPTION, CONDITIONAL.")
    w("")
    w("0 Reproductions and inputs")
    w("0a pwr_budget.py re-run in a child: pwr_budget.out and pwr_budget.json byte for byte: %s" % ("yes" if R["r0a"] else "NO"))
    w("0b pwr_red2.py re-run in a child: pwr_red2.out byte for byte: %s" % ("yes" if R["r0b"] else "NO"))
    w("0c pwr_red2.py imported here prints pwr_red2.out byte for byte (its heat() and states are the record's): %s" % ("yes" if R["r0c"] else "NO"))
    w("0d grade_check.build() (it writes nothing): %d fitted lines, %d modules, %d lines no grade row covers; its own in-use bar %d C" % (
        R["gc"]["rows"], R["gc"]["mods"], R["gc"]["undeclared"], R["gc"]["inside_bar"]))
    w("0e %d inputs pinned by sha256 (the list ends this output)" % len(R["pins"]))
    w("")
    w("1 The acceptance, read first (quoted)")
    w("1a D-02a (owner ruling, 25 September 2026): \"%s\"" % A["d02a"])
    w("1b SC-03 (session choice under the owner's standing rule): \"%s\"" % A["sc03"])
    w("1c TEST-PLAN E3 (section 2): \"**E3-O** operation %d hours at +%d C %s, as a deviation with the cells kept out of the heat\"" % (
        A["e3o_h"], A["e3o_t"], A["e3o_config"]))
    w("   its pass line: \"%s\"" % A["e3o_pass"])
    w("   section 6: \"%s\"; the deployed state: \"%s\"" % (A["e3o_row6"], A["deployed"]))
    w("1d TEST-PLAN E5: %d cycles of %d h at %d %% RH, %d to %d C, \"deployed (lid open; the case has **no vent opening**\", \"%s\"" % (
        A["e5"][0], A["e5"][1], A["e5"][2], A["e5"][3], A["e5"][4], A["e5_config"]))
    w("   its pass line: \"%s\"" % A["e5_pass"])
    w("1e The deviation's arrangement (section 6, E3-O and E5): \"%s\"" % A["controls"])
    w("1f CONOPS 4: \"%s\"; the heat stage (after BANK-R1) runs %s; it turns off \"%s\"" % (A["c1"], A["heat_on"].strip("*"), A["heat_off"]))
    w("1g D-02b (owner ruling): \"%s\"" % A["d02b"])
    w("1h REQ-051's acceptance: \"%s\"" % A["req051_acc"])
    w("1i What it requires (INFERRED from 1a to 1h): at E3-O and E5 the kit is to survive and recover; operation to specification is")
    w("   required only inside the envelope. Required during the margin: E3-O's running module is not shut down (its throttling")
    w("   is logged), and E5's kit logs. The configuration is fixed by the rows: deployed, lid open, on shore or vehicle input,")
    w("   E3-O started with the monitor and radios on. The kit's own controls act during both runs and the rows record it")
    w("   (1e): C1 takes the kit to the heat stage on the inside air, which already turns off the monitor, both WiFi link cards,")
    w("   the 5G module and bank 1 (1f). The lid-closed reduced mode is not permitted (it changes the deployed configuration);")
    w("   EMCON is not permitted (\"%s\" contradicts E3-O's radios on). A further step of the kit's own controls beyond" % A["emcon"])
    w("   the envelope (section 5's hold) is permitted by the pass lines, which require no function during the margin but the")
    w("   running module; it is recorded as the session's reading and named for TEST-PLAN's owner (section 7).")
    w("1j Which ratings apply (SESSION, the rule this record judges by): a part powered during the margin, the maker's widest")
    w("   statement of no damage for an energised part (its absolute maximum where the sheet gives one, else a stated extended")
    w("   range with recovery, else its operating range); a part unpowered, its storage range, else its operating range (the only")
    w("   statement held covers it); no statement held: INCONCLUSIVE. A part straddling the plate or the wall is bounded by the")
    w("   plate (favourable) and the inside air (its rear). Operation to specification at the margin is not required (1a, 1h).")
    w("")
    w("2 The thermal state at the margins (MODELED unless marked)")
    w("2a The heat stage after BANK-R1 (PS-SURV-R) on shore, plan: %.3f W at the pack, %.3f W into the case with the front end's and" % (T["q_hs_pack"], T["q_hs"]))
    w("   charger's loss on the loads; as board B is generated (PS-SURV) %.3f W. HIGH: %.3f W (not covered, as L4-E10 and LO-01a)." % (T["q_gen"], T["q_hs_hi"]))
    w("2b T-H1's floor (LO-01a): the inside air at or under the SGP41's +%.0f C (MAKER, %s Table 5) at +%.0f C on shore: %.4f W/K;" % (
        T["sgp55"], S["sgp_op"]["where"], T["t_use"], T["g_floor"]))
    w("   L4-E10's printed 1.6664 W/K, 70.00 and 75.00 C agree: %s (%.2f, %.2f C uncond.)" % ("yes" if T["agree_g"] and T["agree_air"] else "NO", *T["air_uncond"]))
    w("2c L4-E8's ballasts, %.2f W at the bound's worst corner (cited, L4-E9 IF-08): +%.3f K. The inside air (mixed) at the floor:" % (T["qb"], T["ballast_k"]))
    w("   E3-O %.2f C, E5's dwell %.2f C (steady; a 4 h E3-O from a kit at +55 C reaches %.2f to %.2f C at 32.53's %.0f to %.0f kJ/K," % (
        T["air"]["E3-O"], T["air"]["E5"], T["e3o_4h"][1], T["e3o_4h"][0], T["kJ"][1], T["kJ"][0]))
    w("   so the steady air is the bound; E5's 6 h dwell reaches it). At HIGH heat E5's air would be %.1f C." % T["air_hi"])
    w("2d A charge running on shore (the pack outside, at room temperature, inside its window): +%.3f W, +%.2f K (sensitivity; the" % (T["charge_extra"], T["charge_k"]))
    w("   hold of section 5 holds the charge, as H1 does).")
    w("2e Inside the envelope at the floor (+40 C, heat stage, ballasts): %.2f C, over the SGP41's +55 C line of E3-L (REQ-052);" % T["in_env"])
    w("   LO-01a's floor with the ballasts counted is %.4f W/K (a finding for L4-E9 and L4-E10, section 7)." % T["g_floor_ballast"])
    w("2f The plate and the walls (INFERRED from W4's film coefficients, inside %s, outside face %s, wall %s W/m2K, wall t/k %.3f):" % (
        "%g to %g" % tuple(R["w4"]["hin"]), "%g to %g" % tuple(R["w4"]["hof"]), "%g to %g" % tuple(R["w4"]["how"]), R["w4"]["tk"]))
    w("   the plate sits at the ambient plus %.3f to %.3f of the rise, a PP wall's inner face at %.3f to %.3f of it." % (T["f_plate"] + T["f_wall"]))
    w("2g The enclosure (INFERRED, W4): lid open with fans %.2f to %.2f W/K (32.53: %.1f to %.1f); with the inside film taken as" % (T["w4_open"] + T["g_3253_open"]))
    w("   infinite the outer films alone give %.2f W/K (low coefficients) to %.2f W/K (high): the physical cap of the sealed case." % T["cap"])
    w("   Low outer films with W4's high inside film: %.2f W/K; high outer films with its low inside film: %.2f W/K." % (T["g_low_out_high_in"], T["g_high_out_low_in"]))
    w("2h The running module's cooler exhaust (MODELED): the representative 30 mm fan's %.1f CFM free-air (MAKER, Sunon %s) at %.0f %%" % (
        S["fan_cfm"]["v"][0], S["fan_cfm"]["where"], FLOW_SHARE * 100))
    w("   through the heatsink (ASSUMPTION), %.3f l/s: the CM5's 4.5 W and the fan's %.2f W lift the exhaust %.2f K over the mixed air in" % (T["vdot_l_s"], T["fan_w"], T["d_hs"]))
    w("   the heat stage, and the idle module's 2.0 W %.2f K in the hold. A part outside the exhaust sits at the mixed air." % T["d_hold"])
    w("2i The present design's locations (the heat stage at T-H1's floor, the ballasts on):")
    for mg in ("E3-O", "E5"):
        L = R["locs_now"][mg]
        w("   %-4s ambient %.1f C; mixed air %.2f C; in the exhaust %.2f C; plate %s C; PP wall's inner face %s C" % (
            mg, L["amb"], L["mixed"], L["plume"], _rng(*L["plate"]), _rng(*L["wall_in"])))
    w("")
    w("3 The feasibility screen of the design as it stands (the heat stage at T-H1's floor)")
    w("3a The parts read one by one: state in the heat stage; governing limit by 1j (MAKER, document and page); local bounds")
    w("   (MODELED/INFERRED: inside, mixed air .. exhaust; face and wall, plate .. inside air); verdict per margin. REACHED: past the")
    w("   limit at the favourable bound; PLACEMENT: past it only at the upper bound; NOT REACHED; INCONCLUSIVE: no range held.")
    for pr in R["parts_now"]:
        key = pr["key"]
        src = "" if key is None else "%s %s \"%s\"" % (S[key]["doc"].split("/")[-1], S[key]["where"], S[key]["quote"][:70])
        w("   %-9s %s; %s%s" % (pr["k"], pr["label"], pr["state"], "; device set (CHO-001)" if pr["dev"] else ""))
        w("             limit %s (%s) MAKER: %s" % ("none held" if pr["lim"] is None else "+%.0f C" % pr["lim"], pr["basis"], src))
        for mg in ("E3-O", "E5"):
            lo, hi = pr["temps"][mg]
            g = pr["gap"][mg]
            if g[0] is None:
                gap = ""
            elif g[1] > 0:
                gap = ", over by %s K" % _rng(max(g[0], 0.0), g[1])
            else:
                gap = ", %.2f K inside" % (-g[1])
            w("             %-4s local %s C (%s), %s%s" % (mg, _rng(lo, hi), "MODELED" if pr["where"] == "inside" else "INFERRED", pr["verdict"][mg], gap))
    w("3b Every fitted line on boards A to E (grade_check), every module and every line no grade row covers. Rating: the grade row's")
    w("   maker's range (MAKER); rise: the part's own over its local air for a junction rating (class named); E3-O and E5 local")
    w("   bounds with the rise. Board P and the cells are out of the heat in E3-O and E5 (TEST-PLAN section 6): FEA-008's, not here.")
    counts = {}
    for r_ in R["screen"]:
        for mg in ("E3-O", "E5"):
            counts[(mg, r_["verdict"][mg])] = counts.get((mg, r_["verdict"][mg]), 0) + 1
    for mg in ("E3-O", "E5"):
        w("   %s: %s" % (mg, ", ".join("%s %d" % (v_, counts[(m_, v_)]) for (m_, v_) in sorted(counts) if m_ == mg)))
    for r_ in sorted(R["screen"], key=lambda x: (x["verdict"]["E5"] != "REACHED", x["verdict"]["E5"] != "PLACEMENT", x["part"])):
        t3, t5 = r_.get("temps", {}).get("E3-O"), r_.get("temps", {}).get("E5")
        rating = "none read" if r_["max"] is None else "%s %s%s" % (f1(r_["max"]), r_.get("kind") or "", " abs (rec %s)" % f1(r_["rec_max"]) if r_.get("rec_max") else "")
        rise = r_.get("rise", 0.0)
        tag = "level 2: %s" % r_["level2"] if "level2" in r_ else ("undeclared line" if r_.get("undeclared") else ("module" if r_.get("module") else ""))
        w("   %-34.34s | %-26.26s | %-10s | %-7s | +%5.1f K %-10.10s | E3-O %-11s %-12s | E5 %-11s %-12s | %s" % (
            r_["part"], _refs(r_["refs"]), rating, r_.get("where", r_.get("where_gs")), rise, (r_.get("rise_cls") or "MAKER").split(" ")[0],
            "-" if t3 is None else _rng(*t3), r_["verdict"]["E3-O"], "-" if t5 is None else _rng(*t5), r_["verdict"]["E5"], tag))
    w("   NOT FITTED: the Bulgin PX0833 (CASE-MARGINS: \"%s\"); the sealed RJ45 is a MIL-DTL-38999 shell 15 class part." % A["px0833"])
    w("3c The junction figures (MODELED dissipation in the heat stage x MAKER thetaJA on its JEDEC board; local air the mixed air):")
    seen = set()
    for (b, ref), d in sorted(R["diss_now"].items()):
        if d["part"] in seen:
            continue
        seen.add(d["part"])
        tj5 = R["locs_now"]["E5"]["mixed"] + d["p"] * d["th"]
        w("   %-48s %s %-5s %.3f W (%s) x %.1f C/W = +%.1f K; TJ at E5's mixed air %.1f C against %s" % (
            d["part"], b, ref, d["p"], d["p_src"], d["th"], d["p"] * d["th"], tj5,
            "its ambient rating (TJ not read)" if d["tj"] is None else "%.0f C (%s)" % (d["tj"], d["tj_key"])))
    dc = R["decl"]
    w("3d FINDING outside U-02 (in the envelope, at the generators' own declarations): board E's U13 is a TLV75533 in SOT-23-5 (DBV,")
    w("   %.1f C/W, absolute junction +%.0f C, MAKER, TLV755P sheet, held back) on a rail declared at %.2f A typical and %.2f A peak from" % (dc["th755"], dc["tj755"], dc["e"][0], dc["e"][1]))
    w("   5.0 V: %.3f W, +%.1f K, past +%.0f C at any local air above %.1f C; the declared peak exceeds its %.0f mA output. Board C's U5" % (
        dc["e_decl_p"], dc["e_decl_p"] * dc["th755"], dc["tj755"], dc["tj755"] - dc["e_decl_p"] * dc["th755"], dc["iout"] * 1000))
    w("   (the same part) is declared %.3f A typical and %.3f A peak, the peak past %.0f mA. At the power model's plan load U13 holds" % (dc["c"][0], dc["c"][1], dc["iout"] * 1000))
    w("   (3c). Named for boards E and C's generator owners and Layer 9 (section 7); it does not change U-02.")
    w("")
    w("4 Three complete approaches for the parts that collide (the same margins, the same floor, the same ballasts)")
    a = ap["a"]
    w("4a (a) THE HEAT PATH AND THE ENCLOSURE, the parts and the mode unchanged. Each part routed by the air needs, at E5's dwell:")
    for k in sorted(a["g"], key=lambda k: -a["g"][k]):
        w("      %-9s %.3f W/K (MODELED)" % (k, a["g"][k]))
    w("   so the line is %.3f W/K (0 K margin), %.3f with 1 K and %.3f with 2 K (E3-O alone %.3f W/K), against the outer-film cap %.2f" % (
        a["gmax"], a["g_m"][0], a["g_m"][1], a["g_e3o"], T["cap"][0]))
    w("   (low) to %.2f W/K (high)" % T["cap"][1])
    w("   and W4's %.2f to %.2f W/K. Not routed by the air (physics: the air cannot be cooled below the ambient without a cooler," % T["w4_open"])
    w("   and a cooler in the sealed case returns its input to the air, L4-E10's corrected balance):")
    for k, why in a["open"]:
        w("      %-9s %s" % (k, why))
    w("   Coupling the +70 C modules to the plate instead: the plate at E5 is %s C at the floor, so it needs %.3f W/K at the" % (_rng(*a["plate_floor_e5"]), a["g_plate"]))
    w("   plate's upper fraction, and the parts that cannot be coupled (magnetics, relay, connectors) still need the line above.")
    w("   Cost: mechanical (inside fins, mixing) and a T-H1 line at the top of the bound. VERDICT: REJECTED as a design basis (beyond")
    w("   the cap at the low outer films and at W4's top; incomplete for the parts limited at or under the ambient).")
    w("4b (b) WIDER-RATED PARTS, the mode and the enclosure unchanged (the inside air %.2f C at E5, %.2f C in the exhaust):" % (
        R["locs_now"]["E5"]["mixed"], R["locs_now"]["E5"]["plume"]))
    for b_ in ap["b"]["rows"]:
        w("      %-9s %-17s %s%s" % (b_["k"], b_["who"], b_["note"], "" if b_["margin_e5"] is None else "; at E5 %.2f K inside the candidate's +%.0f C (MAKER)" % (b_["margin_e5"], b_["cand"])))
    w("   Cost: a re-pick of five device-set parts (CHO-001: the owner's) with no candidate held for four of them, and the session's")
    w("   picks. VERDICT: not selectable by the session (outside its authority for the device set; INCONCLUSIVE without candidates).")
    c = ap["c"]
    w("4c (c) THE MARGIN HOLD (a mode the acceptance permits, 1i): beyond the heat stage, on board B's TMP117 (C1's sensor), at +%.1f C" % HOLD_TRIP_C)
    w("   in two readings, the panel controller holds the charge (as H1), takes the running module to idle (no shutdown), and")
    w("   powers off board D (APRS: SA868, PCM2912A, K1, as H1 does), the PA rail (as H1), the RockBLOCK (RB_SW_EN), the LoRa")
    w("   module (LORA_ON), both E72 (ZB_ON), the Geiger module (GEIGER_EN) and the SGP41 (a switch owed on board E, section 5);")
    w("   no e-paper refresh and the sounder muted while it holds; restored at or under +%.1f C after 30 minutes. Existing enables," % HOLD_RESTORE_C)
    w("   firmware, except the SGP41's switch. Heat into the case on shore: %.3f W (MODELED, plan; %.3f W at the pack), against the heat" % (T["q_m"], T["q_m_pack"]))
    w("   stage's %.3f W. H1's own actions, which the hold reuses (CONOPS 4c): \"%s\"." % (T["q_hs"], A["h1_actions"]))
    w("   Each part routed by the air then needs, at E5's dwell:")
    for k in sorted(c["g"], key=lambda k: -c["g"][k]):
        w("      %-9s %.3f W/K (MODELED)" % (k, c["g"][k]))
    w("   so the line is G_c = %.3f W/K (0 K margin; %.3f with 1 K, %.3f with 2 K); with the module at its typical 4.5 W instead of" % (c["gmax"], c["g_m"][0], c["g_m"][1]))
    w("   idle %.3f W/K; at HIGH heat %.3f W/K (not covered). As board B is generated (slot 2 alone, the 5G socket's supply dropped" % (c["g_cm45"], c["g_hi"]))
    w("   too) the hold's heat is %.3f W (MODELED), so the same line covers it. E3-O closes at T-H1's floor (mixed air %.2f C)." % (
        T["q_m_gen"], c["L_floor"]["E3-O"]["mixed"]))
    w("   Not routed by the air:")
    for k, why in c["open"]:
        w("      %-9s %s" % (k, why))
    t_ = c["trip"]
    w("   The trigger (SESSION, PROVISIONAL): the heat stage's air at +40 C at the floor, read in the exhaust, is %.2f C; +%.1f K of" % (t_["env_tmp"], t_["allow"]))
    w("   allowance gives the +%.1f C trigger, so the hold never acts inside the envelope at or over the floor: %s. Before it acts the" % (t_["trip"], "yes" if t_["never_in_env"] else "NO"))
    w("   air is at most +%.1f C even in the exhaust. Once in it, the mixed air (%.2f, %.2f C) stays over the restore: %s. In E5's 30 C" % (
        t_["before_trip_hi"], c["L"]["E3-O"]["mixed"], c["L"]["E5"]["mixed"], "yes" if t_["stays"] else "NO"))
    w("   phase the heat stage reads at most %.2f C in the exhaust: no hold." % t_["e5_low"])
    fb = c["fallback"]
    w("   If T-H1 reads between the floor and G_c: the hold with the +70 C modules (LimeSDR, RockBLOCK, board D) coupled to the plate")
    w("   holds them at the plate's %s C at E5 (%.2f K inside +70 C at the upper fraction), the mixed air then %.2f C (INFERRED)." % (
        _rng(*fb["plate"]), fb["margin"], fb["mixed"]))
    w("   Cost: firmware on existing enables, one board E circuit item, the session's picks for the parts limited at or under the")
    w("   ambient, a T-H1 line %.0f %% over LO-01a's floor (%.3f W/K over the outer-film cap at W4's low coefficients). VERDICT:" % (
        100.0 * (c["gmax"] / T["g_floor"] - 1.0), c["gmax"] - T["cap"][0]))
    w("   SELECTED, CONDITIONAL (section 5).")
    w("4d Per colliding part, the three routes (CLOSES, CONDITIONAL, REJECTED, OUTSIDE AUTHORITY, INCONCLUSIVE):")
    for k, r_ in sorted(R["route"].items()):
        w("      %-9s (a) %-17s (b) %-17s (c) %-17s every route rejected: %s" % (k, r_["a"], r_["b"], r_["c"], "YES" if r_["forced"] else "no"))
    w("")
    w("5 The selection: (c), the margin hold, with the line on T-H1 and the session's picks")
    w("5a The parts at the selected line (E5 at G_c = %.3f W/K, E3-O at T-H1's floor), in the hold's states:" % c["gmax"])
    for pr in c["parts"]:
        mg5 = "" if pr["lim"] is None else "%+.2f/%+.2f" % (pr["lim"] - pr["temps"]["E5"][0], pr["lim"] - pr["temps"]["E5"][1])
        mg3 = "" if pr["lim"] is None else "%+.2f/%+.2f" % (pr["lim"] - pr["temps"]["E3-O"][0], pr["lim"] - pr["temps"]["E3-O"][1])
        w("   %-9s %-10s limit %-6s %-40s E3-O %-11s %-11s %-13s E5 %-11s %-11s %-13s (MAKER limit; MODELED air)" % (
            pr["k"], pr["state"], "none" if pr["lim"] is None else "+%.0f" % pr["lim"], pr["basis"][:40],
            _rng(*pr["temps"]["E3-O"]), pr["verdict"]["E3-O"], mg3, _rng(*pr["temps"]["E5"]), pr["verdict"]["E5"], mg5))
    w("   (margins in K to the lower / the upper bound of each span: inside, the mixed air / the exhaust; face and wall, the plate /")
    w("   the inside air)")
    cnt = {}
    for r_ in c["screen"]:
        for mg in ("E3-O", "E5"):
            cnt[(mg, r_["verdict"][mg])] = cnt.get((mg, r_["verdict"][mg]), 0) + 1
    w("5b Every fitted line, module and undeclared line at the selected line: %s" % "; ".join(
        "%s: %s" % (mg, ", ".join("%s %d" % (v_, cnt[(m_, v_)]) for (m_, v_) in sorted(cnt) if m_ == mg)) for mg in ("E3-O", "E5")))
    for r_ in sorted(c["screen"], key=lambda x: x["part"]):
        if any(v_ not in ("NOT REACHED", "OUT OF SCOPE", "NO PART", "NOT FITTED") for v_ in r_["verdict"].values()):
            w("   %-40.40s %-26.26s E3-O %-12s E5 %-12s%s" % (r_["part"], _refs(r_["refs"]), r_["verdict"]["E3-O"], r_["verdict"]["E5"],
                                                         "  (read in 5a)" if "level2" in r_ else ""))
    w("5c What stays CONDITIONAL: T-H1 lid open with fans at or over %.3f W/K (E5); the hold implemented and forced at room" % c["gmax"])
    w("   temperature; the SGP41 on its own switched supply and bus (board E, owed); the MAIN, PI and TEST pushbuttons picked to")
    w("   +85 C (NKK MBN class, owed); PDi's storage statement for the e-paper (drafted); the +70 C parts placed out of the running")
    w("   cooler's exhaust (Layer 9); the picks not yet made (fans, NVMe wide grade, coin cell, header modules) reaching at least the")
    w("   hold's air at E5 in their place (%.1f C in the exhaust); the parts with no range held (5b's INCONCLUSIVE lines)." % c["L"]["E5"]["plume"])
    w("")
    w("6 The owner-question test: a part with every route rejected or outside authority on held evidence: %s." % (", ".join(R["forced"]) or "none"))
    w("   The e-paper's (c) rests on a statement its maker has not published in a held document (a component limitation, not a")
    w("   requirements conflict); the conditional owner item is named in the record, not asked.")
    w("")
    w("7 Downstream (the record's section 7 carries each item's owner by layer and its acceptance)")
    w("7a T-H1 (prototype bench; Layer 7 designs for it): lid open with fans at or over %.3f W/K for E5 with the hold (LO-01a's own" % c["gmax"])
    w("   floor %.4f W/K, %.4f W/K once L4-E8's ballasts are counted, 2e); the plate and wall thermocouples give the fractions of 2f." % (T["g_floor"], T["g_floor_ballast"]))
    w("7b The hold (firmware owner, CONOPS 4 and HW-FW-CONTRACT's integrators, TEST-PLAN's owner): trigger +%.1f C, restore +%.1f C" % (HOLD_TRIP_C, HOLD_RESTORE_C))
    w("   after 30 minutes, on board B's TMP117; actions as 4c; enables read in the generators:")
    for k_, v_ in sorted(A["enables"].items()):
        w("      %-13s %s" % (k_, v_))
    w("7c Board E (its generator owner): the SGP41 on a switched supply and a bus of its own, so the hold can power it off without the")
    w("   live I2C bus feeding it through its pins; U10's free GPIO20 to GPIO22 serve (the line read above). Board C: the MAIN, PI and")
    w("   TEST pushbuttons (Layer 6 pick, Layer 7 cutouts). Board B: the H5007NL's HX version once its pinout is confirmed (Layer 6).")
    w("7d Layer 9: the parts limited at +70 C and the SGP41 out of the running cooler's exhaust (+%.2f K in the hold, 2h); the class" % T["d_hold"])
    w("   bounds of 3b replaced by laid-out figures. Boards E and C: U13 and U5 (3d).")
    w("7e The owner (outside contacts the session does not make): send the PDi clarification; the fallback evidence requests to")
    w("   Ground Control, NiceRF and Bulgin are drafted beside it.")
    w("")
    w("8 Predicates")
    for k, v in R["pred"].items():
        w("   %s: %s" % (k, "PASS" if v else "FAIL"))
    w("")
    w("Pinned inputs (sha256):")
    for rel in sorted(R["pins"]):
        w("   %s %s" % (R["pins"][rel], rel))
    return "\n".join(out) + "\n"


def main():
    R = compute()
    sys.stdout.write(render(R))
    if not all(R["pred"].values()):
        sys.exit(4)


if __name__ == "__main__":
    main()
