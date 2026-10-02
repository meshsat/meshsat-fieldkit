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
margins and what stays conditional (section 5); the owner-question test (section 6); the downstream items (section 7); U-02 in
depth (section 8: the dependency round, the basis of the lines, the configuration, the fans' power, T-H1, a failed reading and
its fallbacks); the conservative lower bound and U-02's class (section 9); the heat-rejection approaches (section 10); the thermal
reconciliation of the owner's amendment (section 11); the fix round of the Layer 4 review, astra-check-l4close-1's B3, B4 and B7
(section 12: every required mode with its local limits and governing line, the charging heat as a balance, the battery-only run
coupled to C1, the bench points, and the addendum's outside capacity with a zero inside resistance and the three classes); the
predicates (section 13).

Revised twice on 2 October 2026: after the focused check (checks/astra-check-l4e12-1.md) and after the targeted recheck
(checks/astra-check-l4e12-2.md). Every judged limit names its rating category (recommended or operating, storage, absolute);
an absolute rating clears a part only as an exclusion screen, so survival or operation it alone covers stays INCONCLUSIVE; the
SGP41 is judged on Table 4's recommended conditions, and its in-envelope function is the owner's question (section 6).

Section 0 proves, before any figure is used (exit 4 otherwise): pwr_budget.py re-run in a child reproduces pwr_budget.out
and pwr_budget.json byte for byte; pwr_red2.py re-run in a child and imported here reproduces pwr_red2.out byte for byte;
v2/docs/parts/grade_check.py's build() is imported and run (it writes nothing) for the list of fitted parts. Inputs are
pinned by sha256 (exit 2 if a file differs or is missing). One held document (v2/vendor/ti/held/, ignored by git) is fetched
by fetch_held_back.py beside this file; it also fetches Rittal's page that section 11 cites (not an input: never read here).

Run from the repository root:  python3 v2/docs/records/l4e12/l4e12_thermal.py > v2/docs/records/l4e12/l4e12_thermal.out
Needs pdftotext and PyYAML. About fifteen seconds. Exit 2: a pinned file differs or is missing; 3: an input cannot be parsed;
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
import textwrap

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
TMP117_PDF = "v2/vendor/ti/ti-tmp117-temperature.pdf"
# the dependency round's inputs (2 October 2026): the records whose figures U-02's line carries, the profile's trace and its
# replay, Method 507.6's cycle as transcribed in the tree, and the T-H1 hardware list
L4E8_OUT = "v2/docs/records/l4e8/ripple_dense.out"
L4E10_OUT = "v2/docs/records/l4e10/l4e10_cell_thermal.out"
M507 = "v2/vendor/standards/mil-std-810h-method-507-6.md"
TRACE = "v2/docs/records/l3batt/load_trace.out"
REPLAY = "v2/docs/records/l4e/l4e_replay.out"
RTA = "v2/docs/reviews/READY-TO-ACT.md"
PINS = {
    L4E8_OUT: "3b751989b8b70345469f2fdc14640fe041415b7333d669b205d2c675b046ab84",
    L4E10_OUT: "0eb554285580b8f20f05440f2810300cf5c65e9b8b2ea93830474f0d83df2283",
    M507: "aab749c1b6d149c8dddedce99fcc0d505339723300df36a62a257b4ace380d80",
    TRACE: "e35e62483b67fbe71bf89b819f6be46173ce708a8a62c683905d55a37ad4c218",
    REPLAY: "59c6eeab16da98f8ddf16880ddcdc1d2a2c910f4256be9b69aade49dd4d2726d",
    RTA: "bdaf61a4991afb8ca1c45d0c1f71330dd8954e493af357503e01e350b8ed8fff",
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
    TMP117_PDF: "b33614678dd46e7997f813ccefb118796dcbcc97c9ba264806703ee453a3d555",
    TLV758_PDF: "4a86306d6734f1f4212e897c29787a93b56724c06adf87d926cc7b603a694d12",
    TPS62933_PDF: "16ec2eac43c7374eb9e7edd7df7bdb24de6862f695e1582c68716ced4820e5f6",
    TUSB2046_PDF: "d02d0b8af5cbdb1b8186f890efdb214cb8edc50d55b9df5eed0650933a08d3db",
    TUSB8041_PDF: "b715bce72e988310d18dbc8eb041a05b5f15e4a0b690843a873abdc373a1ad87",
    AW_PDF: "af1a93ef3b484a3da4354779f0b2a8a2537c94d71025eb68b82a4d4879f8e8db",
    XEN_PDF: "ba3b1474406fdaf5c7cfc87f80f691cf983f44b0e19f8757511df13f5d6241be",
}

# ------------------------------------------------------------------------------------------------ the figures this record sets
# The figures of other records this one carries; since set 26 each is read back from its pinned output in base() and checked:
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
# T-H1's uncertainty budget (ASSUMPTION, each a standard uncertainty k = 1 unless named; replaced by the bench's own):
TC_U_K = 0.2                 # a thermocouple channel after an isothermal comparison of all junctions before the run, offsets subtracted
MIX_U_K = 0.3                # the mixed air's spatial spread, as the standard deviation of the mean of the air channels
AMB_U_K = 0.3                # the ambient's drift over the averaging hour (a room, or a chamber's controller)
DRIFT_K_H = 0.1              # the steady-state criterion: the mixed air drifting at most 0.1 K/h over the last hour
P_U_REL = 0.007              # the heater power from the supply's V and I read on 0.5 % class meters
LEAD_U_REL = 0.005           # heat carried in or out by the heater and thermocouple leads
EPS_OUT = 0.85               # the outside surfaces' emissivity (W4's 0.85 to 0.9, the low end)
SIGMA = 5.670e-8             # W/m2K4
ROOM_C, SURF_DK = 22.0, 5.0  # the bench's room and the mean surface-to-air offset for the linearised radiation (INFERRED)
CHG_V = 15.5                 # the pack's voltage while charging in pwr_budget.charge_heat (p_into = ICHG x 15.5 V), the same boundary
# The heat-balance relationship of the owner's amendment of 2 October 2026 (item 1): Rittal's calculation basis for enclosure
# climate control, read on its public page (fetched 2026-10-02T12:39Z, HTTP 200, 2522 bytes); held back by its copyright and
# fetched by fetch_held_back.py, never pinned: only the relationship and the steel figure are cited, quoted here.
RITTAL_URL = "https://www.rittal.de/downloads/eBook/TSH/EN/Climate_control/pubData/SEO/Page_6.html"
RITTAL_SHA = "fd3a31d31c88adb4a3bd5b0d7b00bb32ae9bc30f752524971c1ca3a790ade9e8"
RITTAL_REL = "QS = A k \u0394T (watts)"
RITTAL_K_STEEL = 5.5         # W/m2K, "for sheet steel k = 5.5 W/m2K" (the page; A per IEC 890)
# The sensing allowances of the SGP41's own shutdown and of the hold's trigger window (ASSUMPTION, each printed where used):
READ_S, TAU_S = 1.0, 60.0    # a reading every second; a sensor's thermal time constant in the case's moving air
SGP_GRAD_K = 0.5             # a TMP117 on the SGP41's carrier to the SGP41, its own heating included (a placement rule, measured at the bench)
SGP_MARGIN_K = 0.5           # SESSION: the reference's steady reading this far under the power-on threshold, so that a restart takes a bounded time
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
        S[key] = {"v": conv(m), "doc": rel, "where": where, "quote": sq(m.group(quote_group))[:170], "pos": m.start(),
                  "full": sq(m.group(quote_group))}

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
    put("tmp117_acc", TMP117_PDF, r"±(0\.\d+) °C \(maximum\) from \u201340 °C to 100 °C", n(1), "TMP117 accuracy to 100 C")
    put("bme_t_acc", BME_PDF, r"AT\s+0 - 65 °C\s+±(\d\.\d)", n(1), "BME688 temperature accuracy")
    put("sgp_rec", SGP_PDF, r"Operating conditions\s+Relative humidity\s+0\s+90\s+% RH\s+Temperature\s+\u2212(\d+)\s+(\d+)\s+°C", lambda m: (-float(m.group(1)), float(m.group(2))), "SGP41 recommended operating (Table 4)")
    put("ap64500_tjop", AP64500_PDF, r"Operating Junction Temperature Range\s+-(\d+)\s+\+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "AP64500 recommended TJ")
    put("ap6320_tjrec", AP6320_PDF, r"should not\s+exceed the absolute maximum junction temperature of \+(\d+)°C", n(1), "AP6320x design junction ceiling")
    put("tlv758_tjrec", TLV758_PDF, r"TJ\s+Junction temperature\s+\u2013(\d+)\s+(\d+)\s+°C", lambda m: (-float(m.group(1)), float(m.group(2))), "TLV758P TJ recommended")
    put("tlv755_drv", TLV755_PDF, r"RθJA\s+Junction-to-ambient thermal resistance\s+\d+\.\d\s+\d+\.\d\s+(\d+\.\d)", n(1), "TLV755P DRV thetaJA")
    put("tlv755_absnote", TLV755_PDF, r"(Stresses beyond those listed under Absolute Maximum Ratings may cause permanent damage to the device\. These are stress ratings\s+only)", lambda m: True, "TLV755P abs note")
    put("pcm_absnote", PCM_PDF, r"(Stresses beyond those listed under Absolute Maximum Ratings may cause permanent damage to the device\. These are stress ratings\s+only, and functional operation of the device at these or any other conditions beyond those indicated under Recommended Operating\s+Conditions is not implied)", lambda m: True, "PCM2912A abs note")
    put("rm_recover", RM_PDF, r"(without any unrecoverable malfunction\.[\s\S]{0,260}?When the temperature returns to the normal operating temperature level, the\s+module will meet 3GPP specifications again)", lambda m: True, "RM520N recovery statement")
    put("tusb2046_th", TUSB2046_PDF, r"RθJA\s+Junction-to-ambient thermal resistance\s+(\d+\.\d)", n(1), "TUSB2046 thetaJA")
    put("lm5176_th", LM5176_PDF, r"RθJA\s+Junction-to-ambient thermal resistance\s+(\d+\.\d)\s+(\d+\.\d)", n(1, 2), "LM5176 thetaJA")
    put("bq25731_th", BQ25731_PDF, r"RθJA\s+Junction-to-ambient thermal resistance \(JEDEC\(1\)\)\s+(\d+\.\d)", n(1), "BQ25731 thetaJA")
    put("lvc2g07_ta", LVC2G07_PDF, r"TA\s+Operating free-air temperature\s+\u2013(\d+)\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "SN74LVC2G07 TA")
    put("lv1t08_ta", LV1T08_PDF, r"TA\s+Operating free-air temperature\s+\u2013(\d+)\s+(\d+)", lambda m: (-float(m.group(1)), float(m.group(2))), "SN74LV1T08 TA")
    put("csd77_th", CSD77_PDF, r"RθJA\s+Junction-to-Ambient Thermal Resistance \(1\) \(2\)\s+(\d+)", n(1), "CSD17577Q5A thetaJA")
    put("csd77_tj", CSD77_PDF, r"\u2013(\d+) to (\d+)\s+°C", lambda m: (-float(m.group(1)), float(m.group(2))), "CSD17577Q5A TJ")
    put("csd78_th", CSD78_PDF, r"RθJA\s+Junction-to-Ambient Thermal Resistance \(1\) \(2\)\s+(\d+)", n(1), "CSD17578Q5A thetaJA")
    put("csd78_tj", CSD78_PDF, r"\u2013(\d+) to (\d+)\s+°C", lambda m: (-float(m.group(1)), float(m.group(2))), "CSD17578Q5A TJ")
    put("tmp117_acc70", TMP117_PDF, r"±(0\.\d+) °C \(maximum\) from \u201340 °C to 70 °C", n(1), "TMP117 accuracy to 70 C")
    put("sgp_guar", SGP_PDF, r"(Gas Sensing Specifications as detailed in Table 1 are guarant\w+ only when the sensor is stored and operated under the\s+recommended conditions as specified in Table 4)",
        lambda m: True, "SGP41 2.3", 1)
    put("sgp_prolonged", SGP_PDF, r"(Prolonged exposure to conditions\s+outside these conditions may reduce sensor performance)", lambda m: True, "SGP41 2.3, exposure", 1)
    put("sgp_rec_st", SGP_PDF, r"Storage conditions\s+Relative humidity\s+0\s+80\s+% RH\s+Temperature\s+(\d+)\s+(\d+)\s+°C", n(1, 2), "SGP41 recommended storage (Table 4)")
    put("bme_gas_note", BME_PDF, r"(The sensors are electrically operable within this range\. Actual performance may vary\.)", lambda m: True, "BME688 note 1", 1)
    put("bme_iaq_test", BME_PDF, r"(Tested with 0\.6\u201390 ppm of EtOH at 5\u201340 °C)", lambda m: True, "BME688 note 5", 1)
    put("tps62933_tjrec", TPS62933_PDF, r"8\.3 Recommended Operating Conditions\s+Over the recommended operating junction temperature range of \u2013(\d+)°C to \+(\d+)°C",
        lambda m: (-float(m.group(1)), float(m.group(2))), "TPS62933 recommended TJ")
    put("mix_cfm_lo", SUNON_PDF, r"GF60151B9-1E000-AE9\s+12\s+32\s+0\.39\s+2300\s+(\d+\.\d)", n(1), "Sunon GF60151B9 flow")
    put("mix_cfm_hi", SUNON_PDF, r"GF60151B6-1E000-AE9\s+12\s+125\s+1\.50\s+4500\s+(\d+\.\d)", n(1), "Sunon GF60151B6 flow")
    put("mix_ip68", SUNON_PDF, r"(60x60x15 mm \(IP68\))", lambda m: True, "Sunon 60 mm IP68 heading", 1)
    put("fan_v1", SUNON_PDF, r"MF30060V1-10000-A99\s+5\s+112\s+(\d\.\d+)\s+9100\s+(\d\.\d)", n(1, 2), "Sunon MF30060V1 power and flow")
    put("tusb2046_ta", TUSB2046_PDF, r"7\.3 Recommended Operating Conditions[\s\S]{0,3000}?TA\s+Operating free-air temperature\s+°C\s+TUSB2046BI, TUSB2046I\s+\u2013(\d+)\s+(\d+)",
        lambda m: (-float(m.group(1)), float(m.group(2))), "TUSB2046I recommended TA")
    v = S["lime"]["v"]
    S["lime_st"] = dict(S["lime"], v=(v[2], v[3]))
    # the BME688's temperature accuracy sits in Table 10's Typ column (p.14), not its Max column: read from the layout
    pg = page_text(BME_PDF)
    i = S["bme_t_acc"]["pos"]
    line = pg[pg.rfind("\n", 0, i) + 1:pg.find("\n", i)]
    head = [h for h in pg[pg.rfind("\f", 0, i) + 1:i].split("\n") if re.search(r"Min\s+Typ\s+Max", h)]
    if not head:
        refuse(3, "BME688 Table 10's header not found")
    col = line.index("±")
    S["bme_t_typ"] = {"v": abs(col - head[-1].index("Typ")) < abs(col - head[-1].index("Max")), "doc": BME_PDF, "where": S["bme_t_acc"]["where"],
                      "quote": "Table 10, absolute accuracy temperature: +-0.5 C in the Typ column", "pos": i}
    pt = text(PT)
    m = need(pt, r"KSZ9897RTXI:\*\* (\d+\.\d) C/W on a 6-layer JESD51 board \(DS00002330D Note 6-3\) times (\d+\.\d+) W", "KSZ figure")
    S["ksz_th"] = {"v": (float(m.group(1)), float(m.group(2))), "doc": PT, "where": "section 9.2", "quote": sq(m.group(0))}
    m = need(pt, r"PI7C9X2G404SL:\*\* (\d+\.\d) C/W times (\d+\.\d+) to (\d+\.\d+) W gives \+\d+ to \+\d+ K, with a (\d+) C junction maximum", "PI7C figure")
    S["pi7c_th"] = {"v": (float(m.group(1)), float(m.group(4))), "doc": PT, "where": "section 9.2", "quote": sq(m.group(0))}
    return S


# ------------------------------------------------------------------------------------------------ the rating categories
# The category of each maker's statement the record judges by (SESSION reading of where the maker prints it; the headings of
# HEADS are checked on the page in base()). A category that starts with "absolute" is an exclusion screen only.
CAT = {
    "cm5_op": "operating", "rb_op": "operating", "lime": "operating", "lime_st": "storage", "aw_op": "operating", "aw_st": "storage",
    "rm_op": "operating", "rm_ext": "operating, extended (3GPP deviations allowed)", "rm_st": "storage", "xen_op": "operating",
    "xen_st": "storage", "sa_op": "operating", "g6k_op": "operating", "h5007": "operating", "hx": "operating", "atp19": "operating",
    "atp16": "operating", "nkk_mbn": "operating", "fb_op": "operating", "fb_st": "storage", "pdi_op": "operating",
    "pxpc_hi": "operating", "b4000": "operating", "cervoz_wide": "operating", "cervoz_std": "operating",
    "bme_gas": "operating (electrically operable; actual performance may vary)", "bme_st": "absolute (Table 11, storage)",
    "pcm_rec": "recommended", "pcm_bias": "absolute", "pcm_st": "absolute (storage)",
    "sgp_rec": "recommended (Table 4)", "sgp_rec_st": "recommended (Table 4, storage)", "sgp_op": "absolute (Table 5)",
    "sgp_st": "absolute (Table 5, short-term storage)",
    "ap64500_tjop": "recommended", "ap64500_tj": "absolute", "ap6320_tjrec": "recommended (the sheet's thermal-design limit)",
    "ap6320_tj": "absolute", "ap2112_tj": "absolute", "tps62933_tjrec": "recommended", "tps62933_tj": "absolute",
    "tlv755_tjrec": "recommended", "tlv755_tjabs": "absolute", "tlv758_tjrec": "recommended", "tlv758_tjabs": "absolute",
    "tusb8041_tj": "recommended", "tusb2046_ta": "recommended", "lvc2g07_ta": "recommended", "lv1t08_ta": "recommended",
    "csd77_tj": "absolute", "csd78_tj": "absolute",
    "pi7c_th": "absolute (a junction maximum whose category POWER-THERMAL 9.2 does not state; the conservative reading)",
}
_AMR = r"(?m)^\s*(?:\d+\.\d+\s+)?Absolute Maximum Ratings(?:\s*\(\d\))?(?:\s*\(continued\))?\s*$"
_RO = r"(?m)^\s*(?:\d+\.\d+\s+)?Recommended Operating Conditions(?:\s*\(\d\))?(?:\s*\(continued\))?\s*$"
_AMR_D, _RO_D = r"(?m)^Absolute Maximum Ratings", r"(?m)^Recommended Operating Conditions"
_SGP_RO, _SGP_AM = r"2\.3 Recommended Operating and Storage Conditions", r"2\.4 Absolute Minimum and Maximum Ratings"
HEADS = {   # key: (the heading its row is printed under, read before it on the same page; a competing heading that must not come between)
    "pcm_rec": (_RO, _AMR), "pcm_bias": (_AMR, _RO), "pcm_st": (_AMR, _RO), "tlv755_tjrec": (_RO, _AMR), "tlv755_tjabs": (_AMR, _RO),
    "tlv758_tjrec": (_RO, _AMR), "tlv758_tjabs": (_AMR, _RO), "tusb8041_tj": (_RO, _AMR), "lvc2g07_ta": (_RO, _AMR), "lv1t08_ta": (_RO, _AMR),
    "tps62933_tj": (_AMR, _RO), "ap64500_tjop": (_RO_D, _AMR_D), "ap64500_tj": (_AMR_D, _RO_D), "ap6320_tj": (_AMR_D, _RO_D),
    "ap2112_tj": (_AMR_D, _RO_D), "csd77_tj": (r"Absolute Maximum Ratings", _RO), "csd78_tj": (r"Absolute Maximum Ratings", _RO),
    "sgp_rec": (_SGP_RO, _SGP_AM), "sgp_rec_st": (_SGP_RO, _SGP_AM), "sgp_op": (_SGP_AM, _SGP_RO), "sgp_st": (_SGP_AM, _SGP_RO),
    "bme_st": (r"Table 11: Absolute maximum ratings", None),
}


def is_abs(cat):
    return bool(cat) and cat.startswith("absolute")


def heading_ok(S, key):
    """The heading a statement's category rests on is printed before it on the same page, with no competing heading between."""
    want, other = HEADS[key]
    t = page_text(S[key]["doc"])
    pos = S[key]["pos"]
    start = t.rfind("\f", 0, pos) + 1
    seg = t[start:pos]
    hits = [m.end() for m in re.finditer(want, seg)]
    if not hits:
        return False
    return not (other and re.search(other, seg[hits[-1]:]))


def hi_of(S, key):
    v = S[key]["v"]
    return v[1] if key == "lime" else v[-1]


# ------------------------------------------------------------------------------------------------ the parts read one by one
# Every bought module and every board part whose maker's range the screen's first pass finds within reach (section 3b).
# Each carries its state at E3-O and at E5 in two scenarios: "now", the design as it stands (the heat stage, C1's shedding
# the only control action, the radios on at both margins), and "route", the selected route (section 5: E3-O exactly as
# TEST-PLAN states it, radios on; E5 under the hold, radios off; the SGP41 off at both by its own shutdown). A state is
# "work" (powered and required to work during the exposure), "on" (powered, not required) or "off" (unpowered).
# op / st / abs / ext name statements of read_statements(); a part with neither op nor st has no maker's range held.
PARTS = [
    dict(k="CM5", label="Raspberry Pi CM5, slot 3 (running) and slots 1, 2 (off)", where="inside", now=("work", "work"), route=("work", "work"),
         op="cm5_op", dev=True, match=("Compute Module 5",)),
    dict(k="RB9704", label="Ground Control RockBLOCK 9704 SMA (board B J_RB9704)", where="inside", now=("work", "on"), route=("work", "off"),
         op="rb_op", dev=True, match=("RockBLOCK 9704",)),
    dict(k="LIME", label="LimeSDR Mini 2.4 (board B J_LIME; off by C1)", where="inside", now=("off", "off"), route=("off", "off"),
         op="lime", st="lime_st", dev=True, match=("LimeSDR",)),
    dict(k="AW7915", label="AsiaRF AW7915-AED, two (board B J_M2C1, J_M2C3; off by C1)", where="inside", now=("off", "off"), route=("off", "off"),
         op="aw_op", st="aw_st", dev=True, match=("AW7915",)),
    dict(k="RM520N", label="Quectel RM520N-GL (board B J_M2C2; off by C1 after BANK-R1)", where="inside", now=("off", "off"), route=("off", "off"),
         op="rm_op", st="rm_st", ext="rm_ext", dev=True, match=("RM520N",)),
    dict(k="XENARC", label="Xenarc 709GNK monitor (in the plate; off by C1)", where="face", now=("off", "off"), route=("off", "off"),
         op="xen_op", st="xen_st", dev=True, match=("Xenarc",)),
    dict(k="SA868", label="NiceRF SA868 (board D U2)", where="inside", now=("work", "on"), route=("work", "off"),
         op="sa_op", dev=True, match=("SA868",)),
    dict(k="PCM2912A", label="TI PCM2912A USB audio codec (board D U6, the APRS radio's audio)", where="inside", now=("work", "on"), route=("work", "off"),
         op="pcm_rec", abs_on="pcm_bias", abs_off="pcm_st", dev=False, match=("PCM2912A",)),
    dict(k="G6K", label="Omron G6K-2F-Y T/R relay (board D K1, in the radio's RF path)", where="inside", now=("work", "on"), route=("work", "off"),
         op="g6k_op", dev=False, match=("G6K",)),
    dict(k="SGP41", label="Sensirion SGP41 battery-bay gas sensor (board E U17)", where="inside", now=("on", "on"), route=("off", "off"), a=("off", "off"),
         op="sgp_rec", abs_on="sgp_op", abs_off="sgp_st", dev=True, match=("SGP41",)),
    dict(k="H5007NL", label="Pulse H5007NL Ethernet magnetics (board B T1, in circuit)", where="inside", now=("on", "on"), route=("on", "on"),
         op="h5007", dev=False, match=("H5007NL",)),
    dict(k="ATP19", label="C&K ATP19 MAIN pushbutton (board C SW_MAIN, in circuit)", where="face", now=("on", "on"), route=("on", "on"),
         op="atp19", dev=False, match=("ATP19",)),
    dict(k="ATP16", label="C&K ATP16 PI and TEST pushbuttons (board C, in circuit)", where="face", now=("on", "on"), route=("on", "on"),
         op="atp16", dev=False, match=("ATP16",)),
    dict(k="SOUNDER", label="Floyd Bell MC-09-530-Q sounder (board C BZ1; sounds only for SOS)", where="face", now=("off", "off"), route=("off", "off"),
         op="fb_op", st="fb_st", dev=False, match=("Floyd Bell",)),
    dict(k="EPAPER", label="PDi E2370KS0C1 e-paper (board C; refreshed on events)", where="face", now=("off", "off"), route=("off", "off"),
         op="pdi_op", dev=True, match=("E2370KS0C1",)),
    dict(k="PXP4043C", label="Bulgin PXP4043/C sealed USB-C (connector plate; the outlets are off)", where="wall", now=("off", "off"), route=("off", "off"),
         op="pxpc_hi", dev=False, match=("PXP4043/C",)),
    dict(k="NVME", label="NVMe 2242, slot 3 (not picked)", where="inside", now=("on", "on"), route=("on", "on"),
         op=None, dev=False, pick="cervoz_wide", match=()),
]
DEVICE_SET_NOTE = "CHO-001: the owner's device set of 6 September 2026 binds the pick (the owner brief)"


def govern(p, state, S):
    """The limit the corrected rule judges a part by (section 1j). lim: the highest statement that supports the state (a
    powered part, its recommended or operating range; an unpowered part, its storage range, or a range it may operate in,
    INFERRED to cover it unpowered); absv: the absolute rating for the state, an exclusion screen only."""
    out = {"lim": None, "basis": "no maker's range held", "key": None, "cat": None, "absv": None, "abs_key": None}
    if p.get("pick"):
        k = p["pick"]
        out.update(lim=S[k]["v"][1], basis="the pick's line, a wide grade (e.g. Cervoz -40 to +85 C)", key=k, cat=CAT[k])
        return out
    ak = p.get("abs_on") if state in ("work", "on") else p.get("abs_off")
    if ak:
        out.update(absv=hi_of(S, ak), abs_key=ak)
    cands = []
    if state in ("work", "on"):
        if p.get("op"):
            cands.append((hi_of(S, p["op"]), "powered", p["op"]))
    else:
        if p.get("st"):
            cands.append((hi_of(S, p["st"]), "unpowered", p["st"]))
        if p.get("op"):
            cands.append((hi_of(S, p["op"]), "unpowered, inside a range it may operate in (INFERRED to cover it unpowered)", p["op"]))
    if any(is_abs(CAT[c[2]]) for c in cands):
        refuse(4, "%s: an absolute rating offered as a supporting statement" % p["k"])
    if cands:
        lim, basis, key = max(cands, key=lambda c: c[0])
        out.update(lim=lim, basis=basis, key=key, cat=CAT[key])
    return out


def verdict(lim, lo, hi, state="work", absv=None):
    """lim: the statement that supports the state; absv: an absolute rating, an exclusion screen only. NOT REACHED: inside
    lim at the upper local bound; PLACEMENT: inside it only at the lower; REACHED: a part required to work past lim at the
    lower bound, or anything past its absolute rating (or past every statement held) at the lower bound; INCONCLUSIVE: past
    lim (or no lim held) and under the absolute rating at the upper bound (the screen cleared; operation or survival not
    stated by the maker), or no statement held at all."""
    if lim is not None:
        if lim >= hi - 1e-9:
            return "NOT REACHED"
        if lim >= lo - 1e-9:
            return "PLACEMENT"
        if state == "work":
            return "REACHED"
    if absv is None:
        return "INCONCLUSIVE" if lim is None else "REACHED"
    if absv >= hi - 1e-9:
        return "INCONCLUSIVE"
    if absv >= lo - 1e-9:
        return "PLACEMENT"
    return "REACHED"


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
    bad = [k for k in sorted(HEADS) if not heading_ok(S, k)]
    if bad or not S["bme_t_typ"]["v"]:
        refuse(3, "a rating's category is not where the record reads it: %s" % (", ".join(bad) or "the BME688's accuracy column"))
    R["heads"] = sorted(HEADS)
    R["env_store"] = (float(env["storage_3_months"]["min"]), float(env["storage_3_months"]["max"]))
    R["env_store_1y"] = (float(env["storage_1_year"]["min"]), float(env["storage_1_year"]["max"]))

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
    cmt = text(CM)
    geo_m = {"mid": tuple(float(x) / 1000.0 for x in need(cmt, r"\| Z 54\.5, mid-height \| \| (\d+\.\d+) x (\d+\.\d+) \|", "the base at mid-height").groups()),
             "shoulder": float(need(cmt, r"\| Z (101\.04), shoulder \|", "the shoulder").group(1)) / 1000.0,
             "tangent": float(need(cmt, r"\| Z (15\.32), fillet tangent \|", "the fillet tangent").group(1)) / 1000.0,
             "t_wall": float(need(cmt, r"\*\*(5\.34)\*\* on the end walls", "the wall thickness").group(1)) / 1000.0,
             "depth": float(need(cmt, r"\*\*(108\.97)\*\* \(#1321", "the base depth").group(1)) / 1000.0,
             "ceiling": tuple(float(x) / 1000.0 for x in need(cmt, r"\| Lid, flat ceiling \| \| (\d+\.\d+) x (\d+\.\d+) \(#736\)", "the lid ceiling").groups()),
             "parting": tuple(float(x) / 1000.0 for x in need(cmt, r"\| Lid, at the parting plane \| \| (\d+\.\d+) x (\d+\.\d+)", "the lid at the parting plane").groups()),
             "lid_depth": float(need(cmt, r"(45\.47) \(#712 to #736\)", "the lid depth").group(1)) / 1000.0,
             "floor": tuple(float(x) / 1000.0 for x in need(cmt, r"flat floor (\d+\.\d+) x (\d+\.\d+) \(#1321", "the flat floor").groups()),
             "feet": float(need(cmt, r"feet line at sheet y 227\.815 = Z -(\d+\.\d+)", "the feet").group(1))}
    A["geo_m"] = geo_m
    A["pack_wall_mm"] = need(text(CM), r"\| M4b \| Pack block's east face to the east wall \|[^\n]*?\| MET \| \+[\d.]+ \| \+([\d.]+) \|", "CASE-MARGINS M4b").group(1)
    A["req042"] = sq(recs["REQ-042"]["statement"])
    acc42 = sq(recs["REQ-042"]["acceptance"])
    A["req042_voc"] = need(acc42, r"(the SGP41's own clean-air baseline as its datasheet defines the VOC index)", "REQ-042's VOC level").group(1)
    A["req042_range"] = need(acc42, r"(a state outside a sensing part's published range is reported as not covered by that channel, never assumed)", "REQ-042's range clause").group(1)
    A["cfl002"] = sq(recs["CFL-002"]["acceptance"])
    A["req043"] = sq(recs["REQ-043"]["acceptance"])
    A["hold_ref"] = sq(need(cn, r"(board B's\s+TMP117 under the coolers, on the kit bus through the panel controller)", "the heat stage's reading").group(1))
    A["c1"] = sq(need(cn, r"\| (C1, module shedding \| inside air \+50 C or any cell \+55 C \| normal to the reduced mode; reached again in the reduced mode, to the heat stage; restores 5 K below)", "C1").group(1))
    # the cited records and documents, read (the dependency round): L4-E8's ballasts, L4-E10's floor and air, Method 507.6's
    # cycle as transcribed in the tree, T-H1's row and its hardware list, the profile's trace and its replay
    t8 = text(L4E8_OUT)
    A["l4e8_ballast"] = float(need(t8, r"Upper\s+sum at the bound's worst corner (\d\.\d+) W", "L4-E8's ballast sum").group(1))
    t10 = text(L4E10_OUT)
    A["l4e10_floor"] = float(need(t10, r"The complete E3-A and E3-L pass line: (\d\.\d+) W/K", "L4-E10's floor").group(1))
    A["l4e10_air"] = (float(need(t10, r"E3-O's air settles at (\d+\.\d+) C", "L4-E10's E3-O air").group(1)),
                      float(need(t10, r"tends to (\d+\.\d+) C in E5's 60 C dwell", "L4-E10's E5 air").group(1)))
    if abs(A["l4e8_ballast"] - L4E8_BALLAST_W) > 1e-9 or abs(A["l4e10_floor"] - L4E10_G_FLOOR) > 1e-9 or A["l4e10_air"] != L4E10_AIR:
        refuse(4, "a cited record's figure moved (L4-E8 %s, L4-E10 %s %s)" % (A["l4e8_ballast"], A["l4e10_floor"], A["l4e10_air"]))
    tm = text(M507)
    cyc = {int(h): float(c) for h, c in re.findall(r"(?m)^\| (\d{4}) \| (\d+) \|", tm)}
    if not (0 in cyc and 200 in cyc and 800 in cyc and 1600 in cyc):
        refuse(3, "Table 507.6-IX's rows not found")
    A["m507"] = {"lo": cyc[0], "hi": cyc[200], "ramp_h": (200 - 0) / 100.0, "dwell_h": (800 - 200) / 100.0, "down_h": (1600 - 800) / 100.0,
                 "checks": sq(need(tm, r"> (3\. Perform operational checks near the end of the fifth and tenth cycles\.)", "507.6 note 3").group(1))}
    if (A["m507"]["lo"], A["m507"]["hi"]) != (A["e5"][3], A["e5"][4]) or cyc[800] != cyc[200]:
        refuse(4, "TEST-PLAN E5's levels are not Table 507.6-IX's")
    A["th1_row"] = sq(need(tp, r"\| T-H1 \| the empty-case heat-balance test[^|]*\| (a current-moulding Peli 1450 with the 1450PF frame and a 3 mm aluminium plate blank; 20, 40 and 60 W of resistive heat on a dummy stack, the fans running and stopped, lid open and closed, thermocouples on the air, the plate, the walls and a dummy pack block)", "T-H1's row").group(1))
    A["th1_who"] = sq(need(tp, r"(it needs no\s+built kit, and its purchase is the owner's to authorise)", "T-H1's authorisation").group(1))
    rta = text(RTA)
    m = need(rta, r"three of (\d+\.\d) ohm at (\d+\.\d) V give (\d+\.\d) W each", "T-H1's stack heaters")
    A["rta_heater"] = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    A["rta_logger"] = sq(need(rta, r"(Pico Technology PicoLog TC-08, SKU PP222), (\d) thermocouple inputs", "T-H1's logger").group(0))
    A["rta_channels"] = sq(need(rta, r"(eight channels per run \(air 2, plate 2, walls 2, pack block 1, outside air 1\))", "T-H1's channels").group(1))
    A["rta_mixers"] = sq(need(rta, r"(Same Sky CFM-6025BG68, 12 V, the -22 variant \(tachometer and PWM\))", "T-H1's mixer fans").group(1))
    A["rta_who"] = sq(need(rta, r"(who runs the test and where \(the session cannot\))", "T-H1's missing authorisation").group(1))
    tr_ = text(TRACE)
    m = need(tr_, r"LOW (\d+\.\d) /\s+PLAN (\d+\.\d) / HIGH (\d+\.\d) W", "the profile's totals")
    A["trace_total"] = tuple(float(x) for x in m.groups())
    m = need(tr_, r"S (\d+\.\d), R (\d+\.\d), D (\d+\.\d), T (\d+\.\d)", "the profile's tiers")
    A["trace_tiers"] = dict(zip("SRDT", (float(x) for x in m.groups())))
    A["trace_fans"] = [(float(w_), tier, name) for w_, tier, name in re.findall(r"(?m)^\s+(\d+\.\d\d)\s+([SRDT])\s+(two mixer fans|cooler fan slot \d)", tr_)]
    rp = text(REPLAY)
    m = need(rp, r"PS-IDLE-SPEC (\d+\.\d) W at the pack terminals over its (\d+) loads \(REQ-072's objective_profile\)", "the replay's profile")
    A["replay_profile"] = (float(m.group(1)), int(m.group(2)))
    i13 = need(rp, r"13\. THE LOADS OF PS-IDLE-SPEC WITH NO DOCUMENT[^\n]*?(\d+\.\d+) W at the pack", "the replay's section 13")
    blk = rp[i13.start():rp.index("END.", i13.start())] if "END." in rp[i13.start():] else rp[i13.start():]
    A["replay_undoc"] = (float(i13.group(1)), [(float(w_), nm.strip()) for w_, nm in re.findall(r"(?m)^\s+(\d+\.\d\d) W  (\S[^\n]*)$", blk)])
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
    # B4 (astra-check-l4close-1): the heat while charging is a balance on the model's boundary: the input power less the power
    # stored in the cells and the power exported by the outlets (pwr_red2.heat(charging=True)'s terms: the loads' power through
    # the source path, the charge path's loss on the power into the pack, the charging cells' own I2R)
    def charge_balance(st_, ov_):
        f_ = pb.state_full(st_, "plan", ov_)
        p_into = pb.ICHG * CHG_V
        cells = 12 * (pb.ICHG / 3) ** 2 * pb.R_CELL["plan"]
        eta = pb.ETA_CHG * eta_fe
        p_in = (f_["pb"] + p_into) / eta
        stored, exported = p_into - cells, f_["outside"]
        parts = {"loads": f_["pb"] - exported, "supply": f_["pb"] / eta - f_["pb"], "charge": p_into / eta - p_into, "cells": cells}
        heat = p_in - stored - exported
        if abs(sum(parts.values()) - heat) > 1e-9 or abs(pb.charge_heat(f_["pb"], eta_fe) - parts["supply"] - parts["charge"]) > 1e-9:
            refuse(4, "the charging balance does not close on pwr_budget.charge_heat's terms")
        return {"p_in": p_in, "stored": stored, "exported": exported, "heat": heat, "parts": parts, "eta": eta, "p_into": p_into, "pb": f_["pb"]}
    chg_hs, chg_prof = charge_balance("RED", red2.SURVR), charge_balance("IDLESPEC", None)
    # E3-O's charge (2d) runs with the pack outside the case (the deviation): the charge path's loss only; the cells' I2R is outside
    charge_extra = chg_hs["heat"] - q_hs - chg_hs["parts"]["cells"]
    T = {"q_m_gen": q_m_gen, "q_hs": q_hs, "q_hs_pack": q_hs_pack, "q_hs_hi": q_hs_hi, "q_gen": q_gen, "q_m": q_m, "q_m_pack": q_m_pack, "q_m_hi": q_m_hi,
         "q_m45": q_m45, "g_floor": g_floor, "qb": qb, "charge_extra": charge_extra, "sgp55": sgp55, "t_use": t_use,
         "chg_hs": chg_hs, "chg_prof": chg_prof, "eta_fe": eta_fe}
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
    flr = [(tk + 1.0 / ho) / (1.0 / hi + tk + 1.0 / ho) for hi in hin for ho in hfl]
    T["f_plate"] = (min(fr), max(fr))
    T["f_wall"] = (min(wr), max(wr))
    T["f_floor"] = (min(flr), max(flr))
    T["w4_closed"] = (w4.conductance(True, False, "low")[0], w4.conductance(True, False, "high")[0])
    T["g_3253_closed"] = tuple(pb.G_3253["closed_fans"])
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
    R["w4"] = {"hin": tuple(hin), "hof": tuple(hof), "how": tuple(how), "hfl": tuple(hfl), "tk": tk, "hin_still": tuple(w4.H_IN_STILL), "a_side": tuple(w4.A_SIDE)}
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
            "locs": locs, "bounds": bounds, "shore": shore, "hold_ov": hold_ov, "gc": gc, "w4": w4}


# ------------------------------------------------------------------------------------------------ section 3: the screen
CTRL_PARTS = ("LM5176", "BQ25731")
PASS_PARTS = ("TPS259631", "TPS22810", "BSC028N06NS", "BSC039N06NS", "AO3400A", "AO3401A", "SI2300DS", "CSD17577", "CSD17578")
OFF_IN_MARGIN = ("LT8705A",)           # board E's solar stage: no solar input in E3-O or E5 (on shore or vehicle input)
WALL_PARTS = ("PXP4043/C", "PX0833", "MIL-DTL-38999")
NOT_FITTED = {"PX0833": "CASE-MARGINS.md refuses it for the 54 V PoE feed and for fit; the sealed RJ45 is a MIL-DTL-38999 shell 15 class part"}
MARGINS = ("E3-O", "E5")


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
    """The parts whose own dissipation the model gives (MODELED) with the maker's thetaJA, its recommended junction limit
    (the judged limit) and its absolute maximum (an exclusion screen only) (MAKER)."""
    S, pb = C["S"], C["pb"]
    L = node_losses(pb, ov)
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
    th755, abs755, rec755 = S["tlv755_th"]["v"][1], S["tlv755_tjabs"]["v"][1], S["tlv755_tjrec"]["v"][1]
    hubp = (loads["three TUSB8041 hubs VDD33"] + loads["three TUSB8041 hubs VDD 1.1 V"]) / 3.0
    D = {}

    def add(b, refs, part, p, p_src, th, th_key, rec, rec_key, absv, abs_key, rated="TJ", abs_cat=None):
        if rec_key and is_abs(CAT[rec_key]):
            refuse(4, "%s: an absolute junction rating offered as the judged limit" % part)
        for r_ in refs:
            D[(b, r_)] = {"part": part, "p": p, "p_src": p_src, "th": th, "th_key": th_key, "rec": rec, "rec_key": rec_key,
                          "rec_cat": CAT[rec_key] if rec_key else None, "abs": absv, "abs_key": abs_key,
                          "abs_cat": abs_cat or (CAT[abs_key] if abs_key else None), "rated": rated}
    a64 = (S["ap64500_th"]["v"][0], "ap64500_th", S["ap64500_tjop"]["v"][1], "ap64500_tjop", S["ap64500_tj"]["v"][0], "ap64500_tj")
    a63 = (S["ap6320_th"]["v"][0], "ap6320_th", S["ap6320_tjrec"]["v"][0], "ap6320_tjrec", S["ap6320_tj"]["v"][0], "ap6320_tj")
    a21 = (S["ap2112_th"]["v"][0], "ap2112_th", None, None, S["ap2112_tj"]["v"][0], "ap2112_tj")
    t62 = (S["tps62933_th"]["v"][0], "tps62933_th", S["tps62933_tjrec"]["v"][1], "tps62933_tjrec", S["tps62933_tj"]["v"][1], "tps62933_tj")
    t75 = (th755, "tlv755_th", rec755, "tlv755_tjrec", abs755, "tlv755_tjabs")
    add("A", ["U6"], "AP64500 (slot 3's 5.1 V)", L["S3"], "MODELED node S3", *a64, rated="TA")
    add("B", ["U304"], "AP64500 (slot 3's 3.3 V B)", L["S3B"], "MODELED node S3B", *a64, rated="TA")
    add("B", ["U25"], "AP63203 (+3V3_DEV)", L["D3V3"], "MODELED node D3V3", *a63, rated="TA")
    add("E", ["U12"], "AP63205 (+5V_E6)", L["E5V"], "MODELED node E5V", *a63, rated="TA")
    add("B", ["U27"], "AP2112K-2.5 (KSZ AVDDH)", L["KSZ2V5"], "MODELED node KSZ2V5", *a21, rated="TA")
    add("B", ["U40", "U50", "U60"], "AP2112K-3.3 (a supervisor's 3.3 V)", L["IOC"] / 3.0, "MODELED node IOC / 3", *a21, rated="TA")
    add("B", ["U26"], "TPS62933 (KSZ 1.2 V)", L["KSZ1V2"], "MODELED node KSZ1V2", *t62)
    add("A", ["U12"], "TPS62933 (board A 3.3 V)", L["A3V3"], "MODELED node A3V3", *t62)
    add("B", ["U106", "U206", "U306"], "TPS62933 (a hub core)", L["HUB1V1"] / 3.0, "MODELED node HUB1V1 / 3", *t62)
    add("B", ["U305"], "TPS62933 (slot 3's switch core)", L["S3C"], "MODELED node S3C", *t62)
    add("E", ["U13"], "TLV75533 DBV (+3V3_E6), at the model's plan", L["E3V3"], "MODELED node E3V3", *t75)
    add("C", ["U5"], "TLV75533 DBV (board C +3V3), at the declared typical", (5.0 - 3.3) * c_typ, "INFERRED from gen_sch_c's declared %.3f A" % c_typ, *t75)
    add("D", ["U1"], "TLV75533 DBV (+3V3_D8), at the declared typical", (5.0 - 3.3) * d_typ, "INFERRED from gen_sch_d's declared %.3f A" % d_typ, *t75)
    add("D", ["U17"], "TLV75801 DBV (+3V4_HUB)", d17, "gen_sch_d's own bound", S["tlv758_th"]["v"][0], "tlv758_th", S["tlv758_tjrec"]["v"][1], "tlv758_tjrec",
        S["tlv758_tjabs"]["v"][1], "tlv758_tjabs")
    add("B", ["U102", "U202", "U302"], "TUSB8041I (a hub)", hubp, "MODELED the three hubs / 3", S["tusb8041_th"]["v"][0], "tusb8041_th",
        S["tusb8041_tj"]["v"][1], "tusb8041_tj", None, None)
    add("D", ["U4"], "TUSB2046I (board D hub)", 3.44 * 0.040, "INFERRED from gen_sch_d's +3V4_HUB 0.040 A", S["tusb2046_th"]["v"][0], "tusb2046_th",
        None, None, 115.0, "the grade row's TJ", rated="TA", abs_cat="absolute (the grade row's clause: Absolute Maximum Ratings)")
    add("B", ["U1"], "KSZ9897RTXI", S["ksz_th"]["v"][1], "POWER-THERMAL 9.2", S["ksz_th"]["v"][0], "ksz_th", None, None, None, None, rated="TA")
    add("B", ["U301"], "PI7C9X2G404SL (slot 3)", loads["PCIe switch 3.3 V slot 3"] + loads["PCIe switch 1.0 V slot 3"], "MODELED slot 3's switch rails",
        S["pi7c_th"]["v"][0], "pi7c_th", None, None, S["pi7c_th"]["v"][1], "pi7c_th", rated="TA")
    decl = {"e": (e_typ, e_pk), "c": (c_typ, c_pk), "d": (d_typ, d_pk), "iout": S["tlv755_iout"]["v"][0] / 1000.0,
            "e_decl_p": (5.0 - 3.3) * e_typ, "c_decl_p": (5.0 - 3.3) * c_typ, "e_plan_p": L["E3V3"],
            "th755": th755, "tj755": abs755, "rec755": rec755, "drv755": S["tlv755_drv"]["v"][0]}
    return D, decl


def _bounds(where, L):
    if where == "inside":
        return L["mixed"], L["plume"]
    if where in ("face", "wall"):
        return L["plate"][0], L["mixed"]
    return L["amb"], L["amb"]


EC_CUE = re.compile(r"(?i)at operating temperature range|over operating|limits (?:apply|are specified)|guarant\w+ over|electrical characteristics"
                    r"|min/max values stated|from to ta|T[Jj] ?= ?[-\u2013]\s?40")
ROW_OVERRIDE = {"TUSB2046": "tusb2046_ta"}   # a held sheet's recommended row judged in place of a grade row's absolute one


def row_cat(r, part):
    """The rating category of a grade row, read from its clause and quote (SESSION rule, printed in 3b)."""
    s = r.get("source") or {}
    cl, q, cls = s.get("clause") or "", s.get("quote") or "", s.get("class") or ""
    if re.search(r"(?i)recommended", cl + " " + q):
        return "recommended"
    if EC_CUE.search(q):
        return "operating (the range the electrical characteristics hold over)"
    if re.search(r"(?i)absolute|maximum ratings|limiting values", cl):
        return "absolute (the clause names the maker's maximum ratings)"
    if re.search(r"(?i)storage", q) and re.search(r"(?i)junction|\bT ?J\b", q):
        return "absolute (a junction-and-storage row)"
    if re.search(r"Ptot", q):
        return "absolute (a power dissipation row)"
    if r.get("kind") == "TJ":
        return "absolute (a junction row whose table the quote does not name: the conservative reading)"
    if "CSD" in part and cls.startswith("LCSC parametric"):
        return "absolute (a distributor's figure for a TI power FET: the family's junction-and-storage row, as the held CSD17577Q5A sheet prints it)"
    if cls.startswith("LCSC parametric"):
        return "operating (a distributor's parametric figure)"
    return "operating"


def short_cat(cat):
    if not cat:
        return "-"
    if is_abs(cat):
        return "abs"
    if cat.startswith("recommended"):
        return "rec"
    if cat.startswith("storage"):
        return "stor"
    if "electrical characteristics" in cat:
        return "ec"
    if "distributor" in cat:
        return "dist"
    return "op"


def screen_rows(C, Lmap, Dmap, p2=None):
    """Every fitted line (grade_check), every module and every undeclared line: its limit, its local bounds, its own rise and
    its verdict per margin. Lmap and Dmap are per margin; p2, the parts read one by one, replaces the first pass's verdict."""
    S = C["S"]
    out = []
    for kind, code, r, lns, v, why in C["rows"]:
        part = (r.get("part") or "")
        boards = sorted(set(ln["board"] for ln in lns))
        refs = {b: sorted(set(x for ln in lns if ln["board"] == b for x in ln["refs"])) for b in boards}
        row = {"part": part, "code": code, "refs": refs, "kind": r.get("kind"), "max": r.get("max_c"), "where_gs": r.get("where", "inside"),
               "cat": row_cat(r, part)}
        for o_, key_ in ROW_OVERRIDE.items():
            if o_ in part:
                row.update(kind="TA", max=hi_of(S, key_), cat=CAT[key_], override=key_, abs_row=r.get("max_c"))
        pk = [p["k"] for p in PARTS if any(s in part for s in p["match"])]
        if pk:
            row["level2"] = pk[0]
        if r.get("not_a_component"):
            row["verdict"] = {m_: "NO PART" for m_ in MARGINS}
            out.append(row)
            continue
        if boards == ["P"]:
            row["verdict"] = {m_: "OUT OF SCOPE" for m_ in MARGINS}
            out.append(row)
            continue
        if "P" in refs:
            row["pack_refs_out"] = refs.pop("P")
        where = {"outside_face": "face", "plate": "face", "pack": "inside"}.get(row["where_gs"], row["where_gs"])
        if where == "outside":
            where = "wall" if any(w in part for w in WALL_PARTS) else "outside"
        row["where"] = where
        row["verdict"], row["temps"], row["rise"], row["rise_cls"] = {}, {}, {}, {}
        for mg in MARGINS:
            D = Dmap[mg]
            hits = [D[(b, x)] for b in refs for x in refs[b] if (b, x) in D]
            h = max(hits, key=lambda d: d["p"] * d["th"]) if hits else None
            rise, cls, lim = 0.0, "MAKER (an ambient rating: the part's own rise is inside it)", row["max"]
            tj_chk = None
            if row["kind"] == "TJ":
                if h:
                    rise, cls = h["p"] * h["th"], "MODELED %.3f W x MAKER %.1f C/W" % (h["p"], h["th"])
                elif any(c_ in part for c_ in CTRL_PARTS):
                    th = S["lm5176_th"]["v"][1] if "LM5176" in part else S["bq25731_th"]["v"][0]
                    rise, cls = CTRL_P_W * th, "ASSUMPTION (controller at %.2f W) x MAKER %.1f C/W" % (CTRL_P_W, th)
                elif any(c_ in part for c_ in PASS_PARTS):
                    rise, cls = PASS_P_W * PASS_THETA, "ASSUMPTION (pass element %.2f W at %.0f C/W)" % (PASS_P_W, PASS_THETA)
                elif any(c_ in part for c_ in OFF_IN_MARGIN):
                    rise, cls = 0.0, "INFERRED (no solar input in E3-O or E5: unpowered)"
                else:
                    rise, cls = SIG_P_W * SIG_THETA, "ASSUMPTION (signal or protection part %.2f W at %.0f C/W)" % (SIG_P_W, SIG_THETA)
            elif h:
                tj_chk = (h["p"] * h["th"], h["rec"], h["abs"])
            lo, hi = _bounds(where, Lmap[mg])
            lo, hi = lo + rise, hi + rise
            sup, absv = (None, lim) if is_abs(row["cat"]) else (lim, None)
            vd = verdict(sup, lo, hi, "work", absv)
            if tj_chk:
                jlo, jhi = lo + tj_chk[0], hi + tj_chk[0]
                if tj_chk[1] is not None and vd == "NOT REACHED":
                    vd = verdict(tj_chk[1], jlo, jhi)
                elif tj_chk[2] is not None and tj_chk[2] < jhi - 1e-9:
                    vd = verdict(None, jlo, jhi, "work", tj_chk[2])
            if vd == "INCONCLUSIVE" and absv is not None:
                row.setdefault("screen_k", {})[mg] = absv - hi
            if any(n_ in part for n_ in NOT_FITTED):
                vd = "NOT FITTED"
            row["temps"][mg], row["verdict"][mg], row["rise"][mg], row["rise_cls"][mg] = (lo, hi), vd, rise, cls
        if p2 and row.get("level2") in p2:
            row["verdict_l1"] = dict(row["verdict"])
            row["verdict"] = dict(p2[row["level2"]]["verdict"])
            row["cat_l2"] = dict(p2[row["level2"]]["cat"])
            row["lim_l2"] = dict(p2[row["level2"]]["lim"])
        out.append(row)
    for r, v, why in C["mods"]:
        part = r.get("part", "")
        row = {"part": part, "code": "", "refs": {"module": [r.get("maker", "")]}, "kind": r.get("kind"), "max": r.get("max_c"),
               "where_gs": r.get("where", "inside"), "module": True, "rise": {m_: 0.0 for m_ in MARGINS}, "rise_cls": {m_: "MAKER" for m_ in MARGINS},
               "cat": row_cat(r, part)}
        pk = [p["k"] for p in PARTS if any(s in part for s in p["match"])]
        if pk:
            row["level2"] = pk[0]
        where = {"outside_face": "face", "plate": "face", "pack": "pack"}.get(row["where_gs"], row["where_gs"])
        if "QMX" in part:
            where = "lid"
        if where == "outside":
            where = "wall" if any(w in part for w in WALL_PARTS) else "outside"
        row["where"] = where
        if where == "pack":
            row["verdict"] = {m_: "OUT OF SCOPE" for m_ in MARGINS}
            out.append(row)
            continue
        row["verdict"], row["temps"] = {}, {}
        for mg in MARGINS:
            lo, hi = _bounds(where, Lmap[mg])
            row["temps"][mg] = (lo, hi)
            sup, absv = (None, row["max"]) if is_abs(row["cat"]) else (row["max"], None)
            row["verdict"][mg] = "NOT FITTED" if any(n_ in part for n_ in NOT_FITTED) else verdict(sup, lo, hi, "work", absv)
            if row["verdict"][mg] == "INCONCLUSIVE" and absv is not None:
                row.setdefault("screen_k", {})[mg] = absv - hi
        if p2 and row.get("level2") in p2:
            row["verdict_l1"] = dict(row["verdict"])
            row["verdict"] = dict(p2[row["level2"]]["verdict"])
            row["cat_l2"] = dict(p2[row["level2"]]["cat"])
            row["lim_l2"] = dict(p2[row["level2"]]["lim"])
        out.append(row)
    for ln in C["undeclared"]:
        val = ln["value"]
        if "CSD17577" in val or "CSD17578" in val:
            key = "csd77" if "CSD17577" in val else "csd78"
            row = {"part": val.split(" ")[0], "kind": "TJ", "max": S[key + "_tj"]["v"][1], "cat": CAT[key + "_tj"] + " (%s, Absolute Maximum Ratings)" % S[key + "_tj"]["where"]}
            rise, cls = PASS_P_W * S[key + "_th"]["v"][0], "ASSUMPTION (pass element %.2f W) x MAKER %.0f C/W" % (PASS_P_W, S[key + "_th"]["v"][0])
        elif "SN74LVC2G07" in val:
            row, rise, cls = {"part": "SN74LVC2G07DBVR", "kind": "TA", "max": S["lvc2g07_ta"]["v"][1], "cat": CAT["lvc2g07_ta"]}, 0.0, "MAKER (an ambient rating)"
        elif "SN74LV1T08" in val:
            row, rise, cls = {"part": "SN74LV1T08DBVR", "kind": "TA", "max": S["lv1t08_ta"]["v"][1], "cat": CAT["lv1t08_ta"]}, 0.0, "MAKER (an ambient rating)"
        else:
            row, rise, cls = {"part": val[:40], "kind": None, "max": None, "cat": None}, 0.0, ""
        row.update({"code": ln["code"], "refs": {ln["board"]: ln["refs"]}, "where": "inside", "where_gs": "inside", "undeclared": True,
                    "rise": {m_: rise for m_ in MARGINS}, "rise_cls": {m_: cls for m_ in MARGINS}})
        row["verdict"], row["temps"] = {}, {}
        for mg in MARGINS:
            lo, hi = Lmap[mg]["mixed"] + rise, Lmap[mg]["plume"] + rise
            row["temps"][mg] = (lo, hi)
            sup, absv = (None, row["max"]) if is_abs(row["cat"]) else (row["max"], None)
            row["verdict"][mg] = verdict(sup, lo, hi, "work", absv)
            if row["verdict"][mg] == "INCONCLUSIVE" and absv is not None:
                row.setdefault("screen_k", {})[mg] = absv - hi
        out.append(row)
    return out


def parts_eval(C, Lmap, scen):
    """The parts read one by one in a scenario ('now', 'a' or 'route'): per margin, the part's state, its governing limit
    by the corrected rule, its local bounds and its verdict."""
    S = C["S"]
    out = []
    for p in PARTS:
        states = p.get(scen) or p["now"]
        row = {"k": p["k"], "label": p["label"], "where": p["where"], "dev": p.get("dev", False), "state": {}, "lim": {}, "basis": {},
               "key": {}, "cat": {}, "abs": {}, "abs_key": {}, "temps": {}, "verdict": {}, "gap": {}}
        for i, mg in enumerate(MARGINS):
            st = states[i]
            gv = govern(p, st, S)
            lim, absv = gv["lim"], gv["absv"]
            lo, hi = _bounds(p["where"], Lmap[mg])
            row["state"][mg], row["lim"][mg], row["basis"][mg], row["key"][mg] = st, lim, gv["basis"], gv["key"]
            row["cat"][mg], row["abs"][mg], row["abs_key"][mg] = gv["cat"], absv, gv["abs_key"]
            row["temps"][mg] = (lo, hi)
            row["verdict"][mg] = verdict(lim, lo, hi, st, absv)
            row["gap"][mg] = (None if lim is None else lo - lim, None if lim is None else hi - lim)
        out.append(row)
    return out


# ------------------------------------------------------------------------------------------------ sections 4 to 8
CANDIDATES = {   # approach (b): the wider-rated part for each colliding part, its maker's statement and who may pick it
    "RB9704": (None, "OWNER (CHO-001)", "no wider-rated Iridium IMT unit in any held document"),
    "SA868": (None, "OWNER (CHO-001)", "no VHF module rated past +70 C in any held document"),
    "LIME": (None, "OWNER (CHO-001)", "its maker's page offers the commercial grade only (0 to +70 C in use and in storage)"),
    "SGP41": ("bme_gas", "OWNER (CHO-001)", "Bosch BME688 (gas sensing electrically operable -40 to +85 C, performance may vary; storage -45 to +85 C, absolute), already on board E as U14; a second one takes I2C 0x77, which the outside pod's BME688 (32.54, deferred) then cannot use"),
    "EPAPER": (None, "OWNER (CHO-001)", "no e-paper rated past +60 C in any held document"),
    "ATP19": ("nkk_mbn", "SESSION", "NKK MBN sealed pushbutton (IP67, -30 to +85 C); its 12 mm bushing, terminals and cutout are owed"),
    "ATP16": ("nkk_mbn", "SESSION", "NKK MBN sealed pushbutton, as ATP19"),
    "H5007NL": ("hx", "SESSION", "the maker's HX (extended temperature) version, -40 to +85 C; pin compatibility not claimed"),
    "G6K": (None, "SESSION", "no signal relay rated past +70 C held; an +85 C part is a Layer 6 pick"),
    "PXP4043C": ("b4000", "SESSION", "the same maker's 4000 series sheet states -40 to +80 C for the series; the C-type's own sheet says +70 C"),
    "PCM2912A": (None, "SESSION", "its recommended range ends at +70 C; no wider-rated USB audio codec held"),
    "SOUNDER": ("fb_st", "SESSION", "no change: muted, its storage range reaches +85 C"),
    "NVME": ("cervoz_wide", "SESSION", "the pick: a wide grade (Cervoz -40 to +85 C), not the 0 to +70 C standard grade"),
}
HOLD_OFF = ("RB9704", "SA868", "PCM2912A", "G6K")   # the parts read one by one that the hold turns off (with LoRa, both E72, Geiger)
UNRATED = [   # the lines with no maker's range held: the evidence each owes, its owner, and whether it can overturn the architecture
    ("IP68 fans", "ARCHITECTURE", "Layer 6 (D-18's pick)", "they carry the inside film every conductance here assumes (fans on); a fan that stops at the margin takes the enclosure to W4's fans-off values (lid open 0.77 to 1.57 W/K) and every margin with it: a maker's operating range reaching the mixed air at the line"),
    ("CR2032 coin cell", "downstream", "Layer 6", "a lithium coin cell's maker's range at or over the mixed air at the line (a +80 C class cell exists in the market; none held)"),
    ("Keystone 3034 CR2032 holder", "downstream", "Layer 6", "the holder's sheet"),
    ("QRP Labs QMX", "downstream", "Layer 6, the owner's device set", "the unit's range at the ambient (it sits in the lid, outside the sealed volume with the lid open); an owner item only if its maker states less than the ambient"),
    ("sensor and receiver modules on headers", "downstream", "Layer 6", "each module's range (Geiger, lightning, DCF77, pod, camera); the Geiger is unpowered in the hold"),
    ("3 mm panel LEDs", "downstream", "Layer 6", "the LEDs' sheet, at the plate to the inside air"),
    ("U-174/U headset jack", "downstream", "Layer 6", "the jack's drawing"),
    ("2086581001", "downstream", "Layer 6", "J_HDMI's sheet"),
    ("2.54 mm pin header", "downstream", "Layer 6", "the headers' and jumper lands' sheet"),
    ("Keystone 3568 mini blade fuse holder", "downstream", "Layer 6", "the holders' sheet"),
    ("pre-charge pin", "downstream", "Layer 6", "the pin's sheet once named"),
]


def g_req(q, qb, lim, amb, margin=0.0):
    room = lim - amb - margin
    return None if room <= 0 else (q + qb) / room


def g_needs(parts, q_by, amb_by, qb, margin=0.0):
    """Per part, the conductance at which its supporting limit holds at the mixed air (the lower bound inside, the rear at
    the face and wall) at both margins (need). A part not required to work whose supporting limit the air cannot reach, but
    whose absolute rating it can, goes to screen: there the air clears only the exclusion screen and survival stays
    INCONCLUSIVE. Parts with neither cannot be routed by the air (opened)."""
    need, screen, opened = {}, {}, []
    for pr in parts:
        gs, scr = [], False
        for mg in MARGINS:
            lim, absv = pr["lim"][mg], pr["abs"][mg]
            g = None if lim is None else g_req(q_by[mg], qb, lim, amb_by[mg], margin)
            if g is None and pr["state"][mg] != "work" and absv is not None:
                g = g_req(q_by[mg], qb, absv, amb_by[mg], margin)
                scr = scr or g is not None
            if g is None:
                gs = None
                if lim is None and absv is None:
                    opened.append((pr["k"], "no maker's range held"))
                else:
                    opened.append((pr["k"], "its limit %.0f C (%s, %s) is at or under %s's ambient" % (
                        lim if lim is not None else absv, pr["cat"][mg] or CAT[pr["abs_key"][mg]], pr["basis"][mg], mg)))
                break
            gs.append(g)
        if gs is not None:
            (screen if scr else need)[pr["k"]] = {"E3-O": gs[0], "E5": gs[1]}
    return need, screen, opened


def g_line(parts, q_by, amb_by, qb, margin=0.0):
    need, screen, _o = g_needs(parts, q_by, amb_by, qb, margin)
    both = dict(need, **screen)
    return max(max(v.values()) for v in both.values())


def floor1(x):
    """Rounded down to 0.1 C (a threshold set on the safe side of its exact value)."""
    import math
    return math.floor(round(x * 10.0, 6)) / 10.0


# ------------------------------------------------------------------------------------------------ section 8: U-02 in depth
LOSS_ON_A = ("S1", "S2", "S3", "DEV", "A3V3", "PA", "HF", "POE", "PDO", "HEAT")   # board A's converters (gen_sch_a.py, the node notes)
LOSS_ON_E = ("E5V", "E3V3")


def place_of(name):
    """Where a load's heat sits, for T-H1's dummy heaters (INFERRED from the load's name and node)."""
    if "fan" in name:
        return "fans (the real fans, run from the bench supply)"
    if name == "panel board C" or name.startswith("Xenarc"):
        return "board C and the face"
    if name in ("board E controller and sensors", "Geiger module"):
        return "board E"
    if name == "board A logic":
        return "board A"
    if name.startswith("board D") or name.startswith("VHF PA"):
        return "board D and the PA"
    return "board B (slot 3, its switch, hubs, supervisors, the device rail)"


DEEP_OFF = ("KSZ9897R AVDDL+DVDDL 1.2 V", "KSZ9897R AVDDH 2.5 V", "KSZ9897R VDDIO 3.3 V", "NVMe slot 3", "PCIe switch 3.3 V slot 3",
            "PCIe switch 1.0 V slot 3", "LG290P GNSS")   # E5's deeper hold: loads the logging of E5 does not need (SESSION, CONDITIONAL)


def dependency(C, R, ap, gc_all, parts_c):
    """The dependency round of 2 October 2026 (the owner's point on U-02): the basis of the lines, the configuration they
    assume, the fans in the energy budget, T-H1 and what a failed reading changes."""
    import math
    T, A, S, pb, red2, w4 = C["T"], C["A"], C["S"], C["pb"], C["red2"], C["w4"]
    shore, hold_ov = C["shore"], C["hold_ov"]
    qb, e3o_t, e5_t = T["qb"], A["e3o_t"], A["e5"][4]
    c = ap["c"]
    need_by = c["trip"]["need_by"]
    dep = {}

    def comp(ov):
        saved = pb.with_overrides("RED", ov)
        try:
            sh, _pbat = pb.load_battery_share("RED", "plan")
            f = pb.state_full("RED", "plan")
        finally:
            pb.restore(saved)
        loss = node_losses(pb, ov)
        q_pack, q_case, _ = shore(ov)
        loads = sorted([(n_, p_, s_) for n_, p_, s_, _t in sh if p_ > 0], key=lambda x: -x[1])
        out = {"loads": loads, "p_load": f["p_load"], "loss": sum(loss.values()), "loss_by": loss, "dist": f["pb"] - f["p_vbat"],
               "pack": q_pack, "case": q_case, "front": q_case - q_pack}
        place = {}
        for n_, p_, _s in loads:
            place[place_of(n_)] = place.get(place_of(n_), 0.0) + p_
        for nd, v in loss.items():
            k = "board A" if nd in LOSS_ON_A else ("board E" if nd in LOSS_ON_E else "board B (slot 3, its switch, hubs, supervisors, the device rail)")
            place[k] = place.get(k, 0.0) + v
        place["board A"] = place.get("board A", 0.0) + out["dist"]
        place["the front end and the charger (boards E and A, on shore)"] = out["front"]
        out["place"] = place
        return out
    hs, hold = comp(red2.SURVR), comp(hold_ov)
    dep["hs"], dep["hold"] = hs, hold
    # 8a the basis of each line
    rows = {}
    for key, q, amb in (("E5, the hold", T["q_m"], e5_t), ("E3-O, the heat stage", T["q_hs"], e3o_t), ("E5, no hold", T["q_hs"], e5_t)):
        Q, dT = q + qb, need_by - amb
        rows[key] = {"q": q, "Q": Q, "amb": amb, "lim": need_by, "dT": dT, "G": Q / dT, "dGdW": 1.0 / dT, "dGdK": -Q / dT ** 2,
                     "w": ((Q - 1.0) / dT, (Q + 1.0) / dT), "k": (Q / (dT + 1.0), Q / (dT - 1.0))}
    dep["rows"] = rows
    hs_v = dict((n_, p_) for n_, p_, _s in hs["loads"])
    hold_v = dict((n_, p_) for n_, p_, _s in hold["loads"])
    dep["hold_action"] = sorted([(k, hs_v.get(k, 0.0), hold_v.get(k, 0.0)) for k in hold_ov if hs_v.get(k, 0.0) != hold_v.get(k, 0.0)],
                                key=lambda x: -(x[1] - x[2]))
    dep["setters"] = [(pr["k"], pr["state"]["E5"], pr["lim"]["E5"] if pr["lim"]["E5"] is not None else pr["abs"]["E5"],
                       pr["cat"]["E5"] or CAT[pr["abs_key"]["E5"]]) for pr in parts_c
                      if pr["k"] in gc_all and abs(gc_all[pr["k"]]["E5"] - c["gmax"]) < 1e-9]
    # 8b the configuration
    conf = {}
    for case in ("low", "high"):
        conf[case] = {"open_fans": w4.conductance(True, True, case), "open_still": w4.conductance(False, True, case),
                      "closed_fans": w4.conductance(True, False, case), "closed_still": w4.conductance(False, False, case)}
    dep["conf"] = conf
    dep["areas"] = {"face": w4.A_FACE, "side": tuple(w4.A_SIDE), "floor": tuple(w4.A_FLOOR)}
    dep["fans_running"] = {"E3-O": [(n_, p_) for n_, p_, _s in hs["loads"] if "fan" in n_],
                           "E5": [(n_, p_) for n_, p_, _s in hold["loads"] if "fan" in n_]}
    fans_pack_hold = sum(s_ for n_, p_, s_ in hold["loads"] if "fan" in n_)
    fans_pack_hs = sum(s_ for n_, p_, s_ in hs["loads"] if "fan" in n_)
    fans_case_hold = fans_pack_hold * hold["case"] / hold["pack"]
    fans_case_hs = fans_pack_hs * hs["case"] / hs["pack"]
    hin_s, hof = w4.H_IN_STILL, w4.H_OUT_FACE
    f_still = [hi_ / (hi_ + ho_) for hi_ in hin_s for ho_ in hof]
    still = T["w4_open_still"]
    q5s, q3s = T["q_m"] + qb - fans_case_hold, T["q_hs"] + qb - fans_case_hs
    dep["fans_off"] = {"fans_case_hold": fans_case_hold, "fans_case_hs": fans_case_hs, "still": still, "f_still": (min(f_still), max(f_still)),
                       "e5_air": (e5_t + q5s / still[1], e5_t + q5s / still[0]), "e3o_air": (e3o_t + q3s / still[1], e3o_t + q3s / still[0]),
                       "e5_plate_max": e5_t + max(f_still) * q5s / still[0], "e3o_plate_max": e3o_t + max(f_still) * q3s / still[0],
                       "g_needed_e5": q5s / (need_by - e5_t), "g_3253_still": pb.G_3253["open_still"][0]}
    # 8c the fans in the energy budget
    fp = []
    for label, st, ov in (("PS-IDLE-SPEC (the profile)", "IDLESPEC", None), ("PS-TYP", "TYP", None), ("PS-RED, lid closed", "RED", None),
                          ("the heat stage (PS-SURV-R)", "RED", red2.SURVR), ("E5's hold", "RED", hold_ov)):
        row = {"label": label}
        for scen in ("lo", "plan", "hi"):
            saved = pb.with_overrides(st, ov or {})
            try:
                sh, pbat = pb.load_battery_share(st, scen)
            finally:
                pb.restore(saved)
            fl = [(n_, p_, s_) for n_, p_, s_, _t in sh if "fan" in n_ and p_ > 0]
            row[scen] = {"load": sum(p_ for _n, p_, _s in fl), "pack": sum(s_ for _n, _p, s_ in fl), "state": pbat, "n": len(fl)}
        row["wh_day"] = 24.0 * row["plan"]["pack"]
        row["share"] = row["plan"]["pack"] / row["plan"]["state"]
        fp.append(row)
    dep["fan_power"] = fp
    fan_rows = [(n_, v) for n_, _nd, v, _s in pb.LOADS if "fan" in n_]

    def fan_ov(base_ov, st, idx):
        o = dict(base_ov or {})
        for n_, v in fan_rows:
            cur = o.get(n_, v[st])
            if cur[1] > 0:
                o[n_] = pb.same(v[st][idx] if v[st][1] > 0 else v["IDLESPEC"][idx], "R")
        return o
    q_hold_flo = shore(fan_ov(hold_ov, "RED", 0))[1]
    q_hold_fhi = shore(fan_ov(hold_ov, "RED", 2))[1]
    prof = pb.state_full("IDLESPEC", "plan")["pb"]
    prof_hi = pb.state_full("IDLESPEC", "plan", fan_ov(None, "IDLESPEC", 2))["pb"]
    dep["fan_sens"] = {"q_lo": q_hold_flo, "q_hi": q_hold_fhi, "g_lo": (q_hold_flo + qb) / (need_by - e5_t), "g_hi": (q_hold_fhi + qb) / (need_by - e5_t),
                       "prof": prof, "prof_hi": prof_hi, "runtime_factor": prof / prof_hi}
    # 8d T-H1
    kJ, gop = T["kJ"], T["w4_open"]
    taus = [k_ * 1000.0 / g_ / 3600.0 for k_ in kJ for g_ in gop]
    tau_line = max(kJ) * 1000.0 / c["gmax"] / 3600.0
    t_ss = (math.log(100.0) * min(taus), math.log(100.0) * max(taus))
    u_ss = DRIFT_K_H * tau_line
    u_dt = math.sqrt(2 * TC_U_K ** 2 + MIX_U_K ** 2 + AMB_U_K ** 2 + u_ss ** 2)
    ub = {}
    for dT in (10.0, 20.0):
        ur = math.sqrt((u_dt / dT) ** 2 + P_U_REL ** 2 + LEAD_U_REL ** 2)
        ub[dT] = {"u_rel": ur, "U_rel": 2.0 * ur, "pass": c["gmax"] / (1.0 - 2.0 * ur)}
    ph = A["rta_heater"][2]

    def hrad(t_c):
        return 4.0 * EPS_OUT * SIGMA * (t_c + 273.15 + SURF_DK) ** 3
    d_room, d_margin = hrad(ROOM_C) - hrad(310.0 - 273.15 - SURF_DK), hrad(e5_t) - hrad(310.0 - 273.15 - SURF_DK)

    def g_shift(case, dh):
        i = 0 if case == "low" else 1
        h_in = w4.H_IN_FANS[i]
        return (w4.A_SIDE[i] / (1.0 / h_in + w4.T_OVER_K_WALL + 1.0 / (w4.H_OUT_WALL[i] + dh))
                + w4.A_FLOOR[i] / (1.0 / h_in + w4.T_OVER_K_WALL + 1.0 / (w4.H_OUT_FLOOR[i] + dh))
                + w4.series(w4.A_FACE * h_in, w4.A_FACE * (w4.H_OUT_FACE[i] + dh)))
    rad = {case: g_shift(case, d_margin) / g_shift(case, d_room) for case in ("low", "high")}
    dep["th1"] = {"taus": (min(taus), max(taus)), "tau_line": tau_line, "t_ss": t_ss, "points": 8, "total_h": (8 * t_ss[0], 8 * t_ss[1]),
                  "u_ss": u_ss, "u_dt": u_dt, "ub": ub, "heater": A["rta_heater"], "powers": (ph, 2 * ph, 3 * ph),
                  "rise_line": (ph / c["gmax"], 2 * ph / c["gmax"]), "rad": rad, "h_room": hrad(ROOM_C), "h_margin": hrad(e5_t)}
    # 8e a failed reading and the fallbacks
    Q5, Q3 = T["q_m"] + qb, T["q_hs"] + qb
    f_lo, f_hi = T["f_plate"]
    gs = (T["cap"][0], 2.0, 1.9, c["g_e3o"], T["g_floor"], 1.5)
    dep["fail"] = [(g_, e3o_t + Q3 / g_, e5_t + Q5 / g_) for g_ in gs]
    fins = {}
    for case in ("low", "high"):
        i = 0 if case == "low" else 1
        walls = w4.conductance(True, True, case)[1]
        gi, go = w4.A_FACE * w4.H_IN_FANS[i], w4.A_FACE * w4.H_OUT_FACE[i]
        fins[case] = [(ki, ko, walls + w4.series(gi * ki, go * ko)) for ki, ko in ((1, 1), (1, 1.5), (1, 2), (1, 3), (2, 2), (3, 3))]
        fins[case + "_cap_out"] = walls + gi
    rr = {"out2": [], "both2": []}
    for case in ("low", "high"):
        g11 = dict(((a_, b_), g_) for a_, b_, g_ in fins[case])
        rr["out2"].append(g11[(1, 2)] / g11[(1, 1)])
        rr["both2"].append(g11[(2, 2)] / g11[(1, 1)])
    fins["ratio"] = {k: (min(v), max(v)) for k, v in rr.items()}
    fins["applied"] = {k: (c["g_e3o"] * v[0], c["g_e3o"] * v[1]) for k, v in fins["ratio"].items()}
    dep["fins"] = fins
    dep["cond"] = [(g_, (Q5 - (need_by - e5_t) * g_) / (1.0 - f_hi), (Q5 - (need_by - e5_t) * g_) / (1.0 - f_lo),
                    max(0.0, (Q3 - (need_by - e3o_t) * g_) / (1.0 - f_hi))) for g_ in (2.0, 1.9, c["g_e3o"])]
    deep_ov = dict(hold_ov)
    for n_ in DEEP_OFF:
        if n_ not in [x for x, _nd, _v, _s in pb.LOADS]:
            refuse(3, "the model has no load named %s" % n_)
        deep_ov[n_] = pb.OFF
    deep = comp(deep_ov)
    q_deep = deep["case"]
    dep["deep"] = {"q": q_deep, "shed": [(n_, hold_v.get(n_, 0.0)) for n_ in DEEP_OFF], "line": (q_deep + qb) / (need_by - e5_t),
                   "allow": [(g_, (need_by - e5_t) * g_ - qb) for g_ in gs]}
    conn80 = sorted(set(r_["part"] for r_ in R["screen"] if r_.get("max") == 80.0 and r_.get("where") == "inside"))
    d_hs, d_hold = T["d_hs"], T["d_hold"]
    dep["plate"] = {"f_hi": f_hi, "conn80": conn80,
                    "e5": (f_hi * Q5 / (need_by - e5_t), Q5 / (80.0 - e5_t - d_hold)),
                    "e3o": (f_hi * Q3 / (need_by - e3o_t), Q3 / (80.0 - e3o_t - d_hs), Q3 / (80.0 - e3o_t)),
                    "e5_deep": (f_hi * (q_deep + qb) / (need_by - e5_t), (q_deep + qb) / (80.0 - e5_t - d_hold))}
    dep["plate"]["e5_floor"] = max(dep["plate"]["e5"])
    dep["plate"]["e3o_floor"] = max(dep["plate"]["e3o"][:2])
    dep["plate"]["e3o_floor_out"] = max(dep["plate"]["e3o"][0], dep["plate"]["e3o"][2])
    dep["plate"]["e5_deep_floor"] = max(dep["plate"]["e5_deep"])
    return dep


# ------------------------------------------------------------------------------------------------ section 10: heat rejection
K_FIN = (2.0, 3.0)           # ASSUMPTION: the effective area multiplier of fins on the face's free strips (fixed fins under M3's
                             # space, or a clip-on exchanger when deployed); only a vendor's heat-sink datasheet or a bench point confirms it
K_CU = 390.0                 # W/mK, copper (textbook)
STRAP_L, STRAP_A = 0.20, 200e-6   # ASSUMPTION: a flexible copper braid from the plate's edge to the lid, 0.20 m long, 200 mm2
COUPLED = ("Xenarc 709GNK", "WiFi link card 1 (live)", "CM5 slot 1", "CM5 slot 2", "CM5 slot 3", "panel board C",
           "KSZ9897R AVDDL+DVDDL 1.2 V", "KSZ9897R AVDDH 2.5 V", "KSZ9897R VDDIO 3.3 V", "NVMe slot 1", "NVMe slot 2", "NVMe slot 3",
           "VHF PA 30 W")    # approach (b): the profile's loads that sit at or under the plate and can be led into it (INFERRED)


def two_node(amb_c, q_air, q_plate, cfg, geo, k_fin=1.0, a_free=0.0, lid=None, n=45):
    """The inside air and the plate as two nodes: the air takes q_air and loses it through the walls and the plate's inner face;
    the plate takes q_plate (heat led into it by conduction) and the air's share, and rejects through its outer face (fins of
    effective multiplier k_fin on a_free) and, with lid = (R_strap, A_skin, H), through a strap to an aluminium skin on the open
    lid's inside. Natural convection inside (the fans' flow at zero), the bound's coefficients. Returns the rises and flows."""
    ta = amb_c + 273.15
    ep, es, kpp, fo = cfg["eps_plate"], cfg["eps_shell"], cfg["k_pp"], cfg["f_open"]
    tk = geo["t_wall"] / kpp
    a, aw, awo = geo["a_plate"], geo["a_wall"], geo["a_wall_out"]

    def walls_theta(q):
        th_wo = _inv(lambda th: awo * (h_vert(th, geo["h_out"], ta + th / 2) + h_rad(es, 1.0, ta + th, ta)) * th, q, 0.0, 500.0, n)
        th_wi = th_wo + q * tk / (0.5 * (aw + awo))
        return th_wi + _inv(lambda d: aw * h_vert(d, geo["h_in"], ta + th_wi + d / 2) * d, q, 0.0, 500.0, n)

    def q_pi(th_a, th_p):
        d, tf = th_a - th_p, ta + 0.5 * (th_a + th_p)
        if d >= 0:
            return a * h_up(d, geo["l_plate"], tf) * d
        ra, k, _pr = _ra(-d, geo["l_plate"], tf)
        return a * 0.27 * ra ** 0.25 * k / geo["l_plate"] * d   # a warm plate over cooler air: a stable layer (eq 9.32)

    def q_po(th):
        return ((a - a_free) + a_free * k_fin) * (h_up(th, geo["l_plate"], ta + th / 2) + h_rad(ep, fo, ta + th, ta)) * th

    def q_lid(th_p):
        if not lid or th_p <= 0:
            return 0.0
        r_s, a_s, h_s = lid

        def h_skin(th):
            front = h_vert(th, h_s, ta + th / 2) + h_rad(ep, 1.0, ta + th, ta)
            back = 1.0 / (tk + 1.0 / (h_vert(th, h_s, ta + th / 2) + h_rad(es, 1.0, ta + th, ta)))
            return front + back
        th_s = _inv(lambda th: a_s * h_skin(th) * th - (th_p - th) / r_s, 0.0, 0.0, th_p, n)
        return (th_p - th_s) / r_s

    def air(th_p):
        qw = _inv(lambda qw_: qw_ + q_pi(walls_theta(qw_), th_p), q_air, 0.0, 300.0, n)
        return walls_theta(qw), qw
    th_p = _inv(lambda th: q_po(th) + q_lid(th) - q_pi(air(th)[0], th), q_plate, 0.0, 300.0, n)
    th_a, qw = air(th_p)
    return {"th_a": th_a, "th_p": th_p, "walls": qw, "plate_in": q_pi(th_a, th_p), "plate_out": q_po(th_p), "lid": q_lid(th_p)}


def heat_rejection(C, R):
    """Section 10: the profile at REQ-024's +40 C and charging on the design day, against three approaches inside the rulings."""
    T, A, pb, cb = C["T"], C["A"], C["pb"], R["cb"]
    geo, cons = cb["geo"], cb["cons"]
    f = pb.state_full("IDLESPEC", "plan")
    q_prof = f["pb"] + pb.pack_i2r(f["pb"])
    sh, _ = pb.load_battery_share("IDLESPEC", "plan")
    pins = dict((n_, p_) for n_, p_, _s, _t in sh)
    for n_ in COUPLED:
        if n_ not in pins:
            refuse(3, "the model has no load named %s" % n_)
    q_c = sum(pins[n_] for n_ in COUPLED)
    w4t = text(W4_PY)
    m_ = need(w4t, r"the monitor window (\d+\.\d+) x (\d+\.\d+) \(glass level with the plate\) and the e-paper lens (\d+\.\d+) x (\d+\.\d+)", "the face's windows")
    mon, epd = float(m_.group(1)) * float(m_.group(2)) / 1e6, float(m_.group(3)) * float(m_.group(4)) / 1e6
    a_free = geo["a_plate"] - mon - epd
    cmt = text(CM)
    m3 = need(cmt, r"\| M3 \| Space under the QMX tray[^\n]*?\| MET \| \+([\d.]+) \| \+([\d.]+) \| \+([\d.]+) \| \+([\d.]+) \|", "CASE-MARGINS M3")
    ext = need(cmt, r"\| Exterior \| (\d+) x (\d+) \|", "the exterior")
    lid_h = float(ext.group(2)) / 1000.0
    t3 = float(need(text(TP), r"no charge starts while the gauge reads above (\d+) C \(T3\)", "T3").group(1))
    day = need(text(REPLAY), r"over SC-37's hourly air \((\d+\.\d) to (\d+\.\d) C\)", "SC-37's air")
    day = (float(day.group(1)), float(day.group(2)))
    lim, t_use = ap_need_by(R), T["t_use"]
    r_strap = STRAP_L / (K_CU * STRAP_A)
    lid = (r_strap, geo["a_lid_top"], lid_h)
    need_g = q_prof / (lim - t_use)
    # B4: charging with the profile running on the design day: the balance (T["chg_prof"]) plus L4-E8's ballasts, the solar stage
    # running on SC-37's day (their worst corner, the margins' rule)
    q_chg = T["chg_prof"]["heat"] + T["qb"]
    need_ch = (q_chg / (t3 - day[0]), q_chg / (t3 - day[1]))
    rows = [("none: the bound", 0.0, 1.0, None), ("(a) fins on the free strips, k %.0f" % K_FIN[0], 0.0, K_FIN[0], None),
            ("(a) fins on the free strips, k %.0f" % K_FIN[1], 0.0, K_FIN[1], None), ("(b) the large loads led into the plate", q_c, 1.0, None),
            ("(b) with (a)'s fins, k %.0f" % K_FIN[1], q_c, K_FIN[1], None), ("(c) the open lid's skin on a strap", 0.0, 1.0, lid),
            ("(b) + (a) + (c): the best route", q_c, K_FIN[1], lid)]
    out = []
    for lbl, qc, kf, ld in rows:
        r_ = {"label": lbl, "q_c": qc, "k": kf}
        for key, amb in (("use", t_use), ("day_cold", day[0]), ("day_warm", day[1])):
            q_ = q_prof if key == "use" else q_chg
            o = two_node(amb, q_ - qc, qc, cons, geo, kf, a_free, ld)
            o["air"], o["plate"], o["g"] = amb + o["th_a"], amb + o["th_p"], q_ / o["th_a"]
            r_[key] = o
        out.append(r_)
    best = out[-1]
    # the heat the best route rejects with the air at the +70 C class at +40 C: a secant on the air's own share
    qa_lo, qa_hi = 0.5 * (q_prof - q_c), q_prof - q_c
    th_lo = two_node(t_use, qa_lo, q_c, cons, geo, K_FIN[1], a_free, lid)["th_a"]
    th_hi = best["use"]["th_a"]
    target = lim - t_use
    for _ in range(4):
        qa_x = qa_lo + (target - th_lo) * (qa_hi - qa_lo) / (th_hi - th_lo)
        th_x = two_node(t_use, qa_x, q_c, cons, geo, K_FIN[1], a_free, lid)["th_a"]
        qa_lo, th_lo, qa_hi, th_hi = qa_hi, th_hi, qa_x, th_x
    q_max_best = qa_x + q_c
    q_max_bare = enclosure_g(t_use, target, "open", cons, geo)["g"] * target
    fi = pb.state_full("IDLE", "plan")
    q_idle = fi["pb"] + pb.pack_i2r(fi["pb"])
    # the smallest experiment for this question: one lid-open, fans-on point at two heaters, about the profile's heat
    import math
    t1 = R["dep"]["th1"]
    ph = 2.0 * A["rta_heater"][2]

    def u_rel(dt):
        return 2.0 * math.sqrt((t1["u_dt"] / dt) ** 2 + P_U_REL ** 2 + LEAD_U_REL ** 2)

    def reading_for(tg):
        return _inv(lambda g_: g_ * (1.0 - u_rel(ph / g_)), tg, 0.3, 20.0)
    exp2 = [(lbl, tg, reading_for(tg), ph / reading_for(tg)) for lbl, tg in (
        ("the profile's +70 C class at +40 C (the consolidation's framing; section 11 reconciles it)", need_g),
        ("charging with the profile on the design day's cold end", q_chg / (t3 - day[0])),
        ("charging with the profile on the design day's warm end", q_chg / (t3 - day[1])))]
    return {"q_prof": q_prof, "q_chg": q_chg, "q_c": q_c, "coupled": [(n_, pins[n_]) for n_ in COUPLED], "a_free": a_free, "mon": mon, "epd": epd,
            "m3": tuple(float(x) for x in m3.groups()), "lid_h": lid_h, "r_strap": r_strap, "t3": t3, "day": day, "lim": lim,
            "need_g": need_g, "need_ch": need_ch, "rows": out, "q_max_best": q_max_best, "q_max_bare": q_max_bare,
            "short_w": q_prof - q_max_best, "short_g": need_g - best["use"]["g"], "short_w_bare": q_prof - q_max_bare,
            "reaches": best["use"]["air"] <= lim + 1e-9, "charges": best["day_warm"]["air"] <= t3 + 1e-9 and best["day_cold"]["air"] <= t3 + 1e-9,
            "short_ch": (q_chg / (t3 - day[0]) - best["day_cold"]["g"], q_chg / (t3 - day[1]) - best["day_warm"]["g"]),
            "q_idle": q_idle, "exp2": exp2, "exp_power": ph, "fin_mass": a_free * (1.5 / 8.0) * float(m3.group(4)) / 1000.0 * 2700.0,
            "skin_mass": geo["a_lid_top"] * 0.001 * 2700.0, "strap_mass": STRAP_L * STRAP_A * 8960.0}


def reconcile(C, R):
    """Section 11: the owner's amendment of 2 October 2026, item 1: what the bench heat is, the nodes and every limit with its
    reference, the translation from the bench to the operating ambient, the margin, what one point closes, the procedure."""
    import math
    T, A, S, pb, cb, hr, dep = C["T"], C["A"], C["S"], C["pb"], R["cb"], R["hr"], R["dep"]
    red2 = C["red2"]
    geo, cons = cb["geo"], cb["cons"]
    tp, cn = text(TP), text(CONOPS)
    import yaml
    reg = yaml.safe_load(text(REG))
    recs = {r["id"]: r for r in reg["records"] if isinstance(r, dict) and "id" in r}
    rul = {r["id"]: r for r in reg["owner_rulings"]}
    q = {}
    # 11a the heat, counted once
    f = pb.state_full("IDLESPEC", "plan")
    fans_prof = sum(p_ for n_, p_ in ((n_, v["IDLESPEC"][1]) for n_, _nd, v, _s in pb.LOADS) if "fan" in n_)
    q["prof"] = {"loads": f["p_load"], "fans": fans_prof, "conv": f["pb"] - f["p_load"], "i2r": pb.pack_i2r(f["pb"]), "total": hr["q_prof"]}
    hs = dep["hs"]
    fans_hs = sum(p_ for n_, p_, _s in hs["loads"] if "fan" in n_)
    q["hs"] = {"loads": hs["p_load"], "fans": fans_hs, "conv": hs["loss"] + hs["dist"], "front": hs["front"], "ballast": T["qb"],
               "total": T["q_hs"] + T["qb"]}
    q["charge"] = {"bal": T["chg_prof"], "qb": T["qb"], "total": hr["q_chg"], "extra": hr["q_chg"] - hr["q_prof"]}
    nom = float(need(text(L4E8_OUT), r"fch 400 kHz: (\d\.\d+) W", "L4-E8's nominal ballast sum").group(1))
    v_h, r_h = A["rta_heater"][1], A["rta_heater"][0]
    p_heater = v_h ** 2 / r_h
    q["bench"] = {"heater": p_heater, "two": 2.0 * p_heater, "ballast_nom": nom, "r": r_h,
                  "prof_heaters": hr["q_prof"] - fans_prof, "prof_v": math.sqrt((hr["q_prof"] - fans_prof) / 2.0 * r_h),
                  "hs_heaters": T["q_hs"] + T["qb"] - fans_hs, "hs_v": math.sqrt((T["q_hs"] + T["qb"] - fans_hs) * r_h)}
    # the heaters' spread per mode over the places the model puts the heat (the fans excluded: they are real on the bench)
    B_PLACE = "board B (slot 3, its switch, hubs, supervisors, the device rail)"

    def no_fans(place, extra):
        d_ = {k_: v_ for k_, v_ in place.items() if not k_.startswith("fans")}
        for k_, v_ in extra:
            d_[k_] = d_.get(k_, 0.0) + v_
        return d_
    cache = {}
    pb.node_power("VBAT", "IDLESPEC", "plan", cache)
    pl = {}
    for n_, _nd, v, _s in pb.LOADS:
        if v["IDLESPEC"][1] > 0:
            pl[place_of(n_)] = pl.get(place_of(n_), 0.0) + v["IDLESPEC"][1]
    for (node, _st, _sc), (pin, _i, eta) in cache.items():
        if pb.NODES[node][0] != "root":
            k_ = "board A" if node in LOSS_ON_A else ("board E" if node in LOSS_ON_E else B_PLACE)
            pl[k_] = pl.get(k_, 0.0) + pin - pin * eta
    pl["board A"] = pl.get("board A", 0.0) + f["pb"] - f["p_vbat"]
    fans_hold = sum(p_ for n_, p_, _s in dep["hold"]["loads"] if "fan" in n_)
    prof_sp = no_fans(pl, [("the pack (its own I2R)", q["prof"]["i2r"])])
    cb_ = T["chg_prof"]["parts"]
    chg_sp = no_fans(pl, [("the pack (its own I2R)", cb_["cells"]), ("the front end and the charger (boards E and A, on shore)", cb_["supply"] + cb_["charge"]),
                          ("board E", T["qb"])])
    q["settings"] = []
    f_hs_ = pb.state_full("RED", "plan", red2.SURVR)
    i_hs_ = pb.pack_i2r(f_hs_["pb"])
    hs_pack_sp = {k_: v_ for k_, v_ in hs["place"].items() if not k_.startswith("the front end")}
    q_hs_onpack = f_hs_["pb"] - f_hs_["outside"] + i_hs_ + T["qb"]
    for k_, Q_, fans_, sp in (("M2, M4, M6 (K1, K5, K9)", T["q_hs"] + T["qb"], fans_hs, no_fans(hs["place"], [("board A", T["qb"])])),
                              ("M1, M3", q_hs_onpack, fans_hs, no_fans(hs_pack_sp, [("board A", T["qb"]), ("the pack (its own I2R)", i_hs_)])),
                              ("M7 (K10)", T["q_m"] + T["qb"], fans_hold, no_fans(dep["hold"]["place"], [("board A", T["qb"])])),
                              ("M5 (K6)", hr["q_prof"], fans_prof, prof_sp), ("M8, M9 (K7, K8)", hr["q_chg"], fans_prof, chg_sp)):
        heaters = Q_ - fans_
        n_h = max(1, int(round(heaters / p_heater)))
        q["settings"].append({"k": k_, "Q": Q_, "fans": fans_, "heaters": heaters, "n": n_h, "v": math.sqrt(heaters / n_h * r_h),
                              "spread": sorted(sp.items(), key=lambda x: -x[1])})
    # 11b the texts every limit rests on
    lim = {}
    req024 = sq(recs["REQ-024"]["statement"])
    lim["req024_c1"] = need(req024, r"(on measured inside-air \(\+50 C\) and cell \(\+55 C\) temperatures the kit sheds to its reduced mode and then its heat stage \(C1\))", "REQ-024's C1 clause").group(1)
    lim["req024_env"] = need(req024, r"(The kit operates at -20 to \+40 C ambient)", "REQ-024's envelope").group(1)
    lim["req024_acc"] = need(sq(recs["REQ-024"]["acceptance"]), r"(part_temps\.py finds no part outside its range)", "REQ-024's acceptance").group(1)
    lim["req024_shade"] = need(req024, r"(the kit is operated shaded \(D-02e\))", "REQ-024's shade").group(1)
    lim["req052"] = need(sq(recs["REQ-052"]["acceptance"]), r"(every part inside its published range \(an SGP41 above \+55 C fails\))", "REQ-052's SGP41").group(1)
    lim["e3l_air"] = need(tp, r"(the inside air at or under the SGP41's \+55 C; an SGP41 above \+55 C fails E3-L)", "E3-L's inside air").group(1)
    lim["e3a_t3"] = need(tp, r"(\*\*no charge starts while the gauge reads above 42 C \(T3\))", "E3-A's T3").group(1).strip("*")
    lim["e3a_cells"] = need(tp, r"(every cell surface at most \+60 C throughout)", "E3-A's cells").group(1)
    lim["e3a_mode"] = sq(need(tp, r"\| E3-A \| (deployed, pack fitted, lid open, shaded; the kit in the mode its controls select)", "E3-A's mode").group(1))
    lim["req014"] = need(sq(recs["REQ-014"]["statement"]), r"(its battery-only runtime is stated in hours in an idle and a typical mode \(PS-IDLE-SPEC and PS-TYP\) at \+20 C)", "REQ-014").group(1)
    lim["d02a"], lim["d02b"], lim["d02e"] = A["d02a"], sq(rul["D-02b"]["ruling"]), sq(rul["D-02e"]["ruling"])
    lim["d02b_35"] = need(lim["d02b"], r"(above \+35 C ambient the kit runs one module)", "D-02b's consequence").group(1)
    lim["no505"] = not re.search(r"\b505\b", tp)
    nb = c_need = R["ap"]["c"]["trip"]["need_by"]
    t_use, e3o, e5 = T["t_use"], A["e3o_t"], A["e5"][4]
    qp, qh, qc = hr["q_prof"], q["hs"]["total"], hr["q_chg"]
    t3, day = hr["t3"], hr["day"]
    conds = [
        ("K1", "REQ-024 and E3-A at +40 C: C1's end state, the heat stage on shore with the ballasts; a SCREEN, not a closure line (12a)", qh, t_use, "the SGP41's Table 5 +55 C, an ABSOLUTE rating (REQ-052's and E3-L's fail line reads it): an exclusion screen, never the sensor's function", 55.0, "lid open"),
        ("K2", "the same, the SGP41 judged on its Table 4 +50 C (this record's corrected rule; the owner's CFL-002 open)", qh, t_use, "the SGP41's +50 C (Table 4)", S["sgp_rec"]["v"][1], "lid open"),
        ("K3", "the same, the +70 C class in the heat stage (the H5007NL, the ATP16, the PXP4043/C and the radios C1 leaves on) at the MIXED air; a component screen (the exhaust, the cells and the junctions are 12a's)", qh, t_use, "+70 C (the makers' sheets of section 4)", nb, "lid open"),
        ("K4", "the same, the module's intake", qh, t_use, "the module's +85 C (CM5 4.4)", S["cm5_op"]["v"][1], "lid open"),
        ("K5", "REQ-052 and E3-L at +40 C: the heat stage; a SCREEN (12a)", qh, t_use, "the SGP41's Table 5 +55 C (E3-L's fail line; ABSOLUTE, a screen)", 55.0, "lid closed"),
        ("K6", "REQ-014 at +20 C: the profile on the pack, not shed by C1", qp, 20.0, "C1's inside-air trigger +50 C (REQ-024)", 50.0, "lid open"),
        ("K7", "charging on SC-37's design day, the profile running, the balance of 12b (the source path, the charge path, the charging cells, the solar stage's ballasts), cold end", qc, day[0], "the gauge's charge start T3 42 C (E3-A; the idle cells at the air; the running charge's T4 with the cells' own rise is 12a's)", t3, "lid open"),
        ("K8", "the same, warm end", qc, day[1], "T3 42 C", t3, "lid open"),
        ("K9", "E3-O, D-02a's +55 C AMBIENT margin: the heat stage, every radio C1 leaves on", qh, e3o, "+70 C (U-02)", nb, "lid open"),
        ("K10", "E5's +60 C dwell under the hold", T["q_m"] + T["qb"], e5, "+70 C (U-02)", nb, "lid open"),
        ("X1", "the profile at +40 C (no requirement: C1 sheds it, REQ-024; D-02b runs one module above +35 C)", qp, t_use, "C1's +50 C", 50.0, "lid open"),
        ("X2", "the profile's +70 C class at +40 C (the consolidation's framing, no requirement)", qp, t_use, "+70 C", nb, "lid open"),
        ("X3", "the owner's conditional check: 42.4 W under a +55 C inside-air limit at +40 C", 2.0 * A["rta_heater"][2], t_use, "+55 C", 55.0, "lid open")]
    rc_conds = [(k_, lbl, Q_, amb, lim_txt, L_, lid, Q_ / (L_ - amb)) for k_, lbl, Q_, amb, lim_txt, L_, lid in conds]
    # 11c the translation from the bench's room to the operating ambient: the bound's model at the same rise
    trans = []
    for lbl, cfg in (("the bound", cons), ("the coefficients' other ends", cb["opt"]), ("the fans' flow 0.5 m/s", dict(cons, v=0.5)),
                     ("the stack's radiation", dict(cons, rad_in=True))):
        row = [lbl]
        for rise in (15.0, 30.0):
            g_room = enclosure_g(ROOM_C, rise, "open", cfg, geo)["g"]
            g_op = enclosure_g(t_use, rise, "open", cfg, geo)["g"]
            row.append((rise, g_room, g_op, g_op / g_room))
        trans.append(row)
    g_k1 = rc_conds[0][7]
    taus = (min(T["kJ"]) * 1000.0 / g_k1 / 3600.0, max(T["kJ"]) * 1000.0 / g_k1 / 3600.0)
    # the relationship QS = A k dT on this enclosure's own surfaces and films: k per path is the bound's heat over its area and
    # the rise, at +40 C and K1's rise (the plate's exposed face and the walls' outer skin; the floor adiabatic)
    rise_k1 = rc_conds[0][2] / g_k1
    area = geo["a_plate"] + geo["a_wall_out"]
    rit = {"area": area, "a_plate": geo["a_plate"], "a_wall": geo["a_wall_out"], "rise": rise_k1, "steel_g": RITTAL_K_STEEL * area,
           "k_need": g_k1 / area, "rows": []}
    for lbl, cfg in (("the bound", cons), ("the coefficients' other ends", cb["opt"])):
        e_ = enclosure_g(t_use, rise_k1, "open", cfg, geo)
        rit["rows"].append((lbl, e_["q"]["plate"] / (geo["a_plate"] * rise_k1), e_["q"]["walls"] / (geo["a_wall_out"] * rise_k1),
                            e_["g"] / area, e_["g"]))
    # the outside films' cap at the same point: any inside film (a 50 m/s flow), at both ends of the coefficients
    rit["cap"] = tuple(enclosure_g(t_use, rise_k1, "open", dict(cfg, v=50.0), geo)["g"] for cfg in (cons, cb["opt"]))
    rit["w4"], rit["s3253"] = T["w4_open"], T["g_3253_open"]
    e3a_h = float(need(tp, r"\| \+(\d+) C for (\d+) h on the pack, then shore applied for (\d+) h", "E3-A's levels").group(2))
    # 11d the margin: each condition's bench reading at its own heat (heaters plus the fans), with the expanded uncertainty
    t1 = dep["th1"]

    def u_rel(dt):
        return 2.0 * math.sqrt((t1["u_dt"] / dt) ** 2 + P_U_REL ** 2 + LEAD_U_REL ** 2)

    def reading_for(tg, p_):
        return _inv(lambda g_: g_ * (1.0 - u_rel(p_ / g_)), tg, 0.3, 20.0)
    marg = []
    for k_, lbl, Q_, amb, lim_txt, L_, lid, gneed in rc_conds:
        if k_.startswith("K"):
            rd = reading_for(gneed, Q_)
            marg.append((k_, Q_, gneed, rd, Q_ / rd, u_rel(Q_ / rd)))
    r509 = hr["exp2"][0]
    check509 = {"p": 2.0 * A["rta_heater"][2], "reading": r509[2], "rise": r509[3], "u": u_rel(r509[3]), "after": r509[2] * (1.0 - u_rel(r509[3])),
                "target": r509[1], "air40": t_use + 2.0 * A["rta_heater"][2] / r509[2]}
    # each point's duration at its pass line: tau = C / G with 32.53's upper thermal mass; within 1 % of the rise at ln(100) tau
    times = []
    for k_ in ("K1", "K5", "K10", "K6", "K7"):
        m_ = next(x for x in marg if x[0] == k_)
        tau = max(T["kJ"]) * 1000.0 / m_[3] / 3600.0
        times.append((k_, tau, math.log(100.0) * tau, 3.0 * tau))
    # B3's points take their own readings (12a); their durations are printed there
    return {"q": q, "lim": lim, "conds": rc_conds, "trans": trans, "taus": taus, "e3a_h": e3a_h, "marg": marg, "check509": check509,
            "rit": rit, "times": times, "t_bound": cb["exp"]["t_bound"], "kj_hi": max(T["kJ"])}


# ------------------------------------------------------------------------------------------------ section 12: the fix round
# The parts read one by one in the battery profile PS-IDLE-SPEC (pwr_budget's IDLESPEC loads: a part is powered where its load is
# over 0 W): every module powered but the LimeSDR (0 W), the outlets off; the e-paper refreshed on events, taken as working.
PROFILE_STATES = {"CM5": "work", "RB9704": "work", "LIME": "off", "AW7915": "work", "RM520N": "work", "XENARC": "work", "SA868": "work",
                  "PCM2912A": "work", "G6K": "work", "H5007NL": "on", "ATP19": "on", "ATP16": "on", "SOUNDER": "off", "EPAPER": "work",
                  "PXP4043C": "off", "NVME": "on"}
ROUTE_P85 = ("ATP16", "ATP19")      # the route's pushbuttons to an +85 C part (5b, the session's pick, NKK MBN)
OPTIONS = ("as ruled", "C", "A", "B")
_R_PACK = ("the cells' own rise in the pocket (the block's film 5 to 15 W/m2K, the lowest taken; L4-E10, U-01) and the gauge's reading "
           "error at H1 (records/hc2/hotstop_bounds.out; the thresholds PROVISIONAL, HOT-R1 owed on boards A and E, CONOPS 4c)")
_R_COMMON = ("the parts' local air in the built kit (T-H2), the junctions' modeled rise (THM-001), the 33 lines cleared only by an absolute "
             "rating (section 7), the fans' rating (D-18); CFL-002 is the owner's")
REMAIN = {   # the evidence each mode still needs, beyond its conductance (SESSION reading of the review's B3)
    "M1": "T-H1's lid-open point at this heat; " + _R_PACK + "; " + _R_COMMON,
    "M2": "T-H1's lid-open point at this heat; the idle cells at the air (no own heat) and the gauge's reading error at H1; " + _R_COMMON,
    "M3": "T-H1's lid-closed point at this heat; " + _R_PACK + "; " + _R_COMMON,
    "M4": "T-H1's lid-closed point at this heat; the idle cells at the air and the gauge's reading error at H1; " + _R_COMMON,
    "M5": ("T-H1's point at the profile's heat; " + _R_PACK + "; the battery-only run's transient (12c): on the bound C1 sheds the profile before "
           "its energy ends; " + _R_COMMON),
    "M6": ("the e-paper's unpowered range (PDi's storage statement, the clarification drafted; only its operating row is held); E3-O "
           "runs with the cells kept out (TEST-PLAN's deviation): the fitted pack at the margin is U-01's (BAT-F19, CFL-017); the "
           "unpowered SGP41's short-term storage duration (Sensirion); T-H1's lid-open point at the heat stage's heat; " + _R_COMMON),
    "M7": ("the e-paper's unpowered range as in M6, with no conductance meeting its operating row at E5's +60 C; the cells kept out "
           "(TEST-PLAN's deviation; U-01, BAT-F19); the parts the hold turns off on their operating rows read to cover them unpowered "
           "until their makers state storage; T-H1's point at the hold's heat; " + _R_COMMON),
    "M8": ("T-H1's point at the charging heat; the charging cells' rise over the air (U-01); the source path's efficiency (the model's "
           "0.95 front end taken for the solar stage, INFERRED); a charge started under T3 cycles on T4 once the cells pass it; " + _R_COMMON),
    "M9": "as M8, at the design day's warm end",
}


def per_mode(C, R):
    """Section 12a (astra-check-l4close-1 B3): every required mode with its heat balance, ambient and every correctly categorised
    LOCAL limit (the cells with their own rise, the control thresholds whose firing ends the mode, the parts at their local air with
    the cooler's exhaust, the junctions, the unpowered parts' storage rows); the governing line is the tightest; an absolute rating
    is an exclusion screen only and never a line; per CFL-002 option."""
    import math
    T, A, S, pb, red2 = C["T"], C["A"], C["S"], C["pb"], C["red2"]
    hr, dep = R["hr"], R["dep"]
    qb, t_use, gb = T["qb"], T["t_use"], pb.G_BLK[0]
    cn, tp, t10 = sq(text(CONOPS)), sq(text(TP)), text(L4E10_OUT)
    th = {}
    th["h1"] = float(need(cn, r"the hottest of the gauge's four cell thermistors at \+(\d+\.\d) C in two readings a second apart \(H1", "H1").group(1))
    m = need(cn, r"C1 \(inside air \+(\d+) C, or any cell \+(\d+) C on the gauge's thermistors\)", "C1's triggers")
    th["c1_air"], th["c1_cell"] = float(m.group(1)), float(m.group(2))
    th["t3"] = hr["t3"]
    th["t4"] = float(need(tp, r"a running charge stops once it reads above (\d+) C \(T4\)", "T4").group(1))
    th["otc"] = float(need(tp, r"held off by OTC whenever it reads (\d+\.\d) C or more", "OTC").group(1))
    m = need(t10, r"charge (\d+) to (\d+) C, discharge (-\d+) to (\d+) C at the cell surface temperature; storage 1 month (-\d+) to (\d+) C", "the 35E's rows")
    th["chg"], th["dis"], th["st1m"] = float(m.group(2)), float(m.group(4)), float(m.group(6))
    th["sgp4"], th["sgp5"], th["sgp_st5"], th["bme"] = S["sgp_rec"]["v"][1], S["sgp_op"]["v"][1], hi_of(S, "sgp_st"), hi_of(S, "bme_gas")
    th["other"] = 80.0
    f_hs = pb.state_full("RED", "plan", red2.SURVR)
    q_hsp, i_hs = f_hs["pb"] - f_hs["outside"], pb.pack_i2r(f_hs["pb"])
    f_p = pb.state_full("IDLESPEC", "plan")
    q_pp, i_p = f_p["pb"] - f_p["outside"], pb.pack_i2r(f_p["pb"])
    cbal = T["chg_prof"]
    ov_prof = {n_: v["IDLESPEC"] for n_, _nd, v, _s in pb.LOADS}
    D = {"hs": diss_table(C, red2.SURVR)[0], "hold": diss_table(C, C["hold_ov"])[0], "prof": diss_table(C, ov_prof)[0]}
    day = hr["day"]
    hs_heat = [("the heat stage at the pack", q_hsp), ("the source path (on shore)", T["q_hs"] - q_hsp), ("L4-E8's ballasts", qb)]
    modes = [
        dict(id="M1", label="REQ-024 and E3-A at +40 C, lid open, shaded: C1's end state, the heat stage on the pack (the required set, REQ-052)",
             amb=t_use, lid="open", heat=[("the heat stage at the pack", q_hsp), ("the cells' discharge I2R", i_hs), ("L4-E8's ballasts", qb)],
             pack=("dis", i_hs), D="hs", col=0, d=T["d_hs"], c1=False, env=True),
        dict(id="M2", label="the same on shore (E3-A's 2 h): the pack idle, no charge starting above T3",
             amb=t_use, lid="open", heat=hs_heat, pack=("idle", 0.0), D="hs", col=0, d=T["d_hs"], c1=False, env=True),
        dict(id="M3", label="REQ-024 and E3-L at +40 C, lid closed: the heat stage on the pack", amb=t_use, lid="closed",
             heat=[("the heat stage at the pack", q_hsp), ("the cells' discharge I2R", i_hs), ("L4-E8's ballasts", qb)], pack=("dis", i_hs), D="hs",
             col=0, d=T["d_hs"], c1=False, env=True),
        dict(id="M4", label="the same on shore, lid closed (E3-L's second half)", amb=t_use, lid="closed", heat=hs_heat, pack=("idle", 0.0), D="hs",
             col=0, d=T["d_hs"], c1=False, env=True),
        dict(id="M5", label="REQ-014 at +20 C: PS-IDLE-SPEC on the pack, battery-only, unshed by C1", amb=rc_amb(R, "K6"), lid="open",
             heat=[("the profile at the pack", q_pp), ("the cells' discharge I2R", i_p)], pack=("dis", i_p), D="prof", col=None, d=T["d_hold"],
             c1=True, env=True),
        dict(id="M6", label="E3-O at D-02a's +55 C margin, 4 h: the heat stage, every radio C1 leaves on, on shore, the cells kept out (TEST-PLAN's deviation)",
             amb=A["e3o_t"], lid="open", heat=hs_heat, pack=("out", 0.0), D="hs", col=0, d=T["d_hs"], c1=False, env=False),
        dict(id="M7", label="E5's +60 C dwell: the hold, logging, on shore, the cells kept out (TEST-PLAN's deviation)", amb=A["e5"][4], lid="open",
             heat=[("the hold at the pack", T["q_m_pack"]), ("the source path (on shore)", T["q_m"] - T["q_m_pack"]), ("L4-E8's ballasts", qb)],
             pack=("out", 0.0), D="hold", col=1, d=T["d_hold"], c1=False, env=False),
        dict(id="M8", label="charging on SC-37's design day, cold end: PS-IDLE-SPEC running, the solar stage charging the pack", amb=day[0], lid="open",
             heat=[("the profile at the battery node", cbal["parts"]["loads"]), ("the source path", cbal["parts"]["supply"]),
                   ("the charge path", cbal["parts"]["charge"]), ("the charging cells' I2R", cbal["parts"]["cells"]), ("L4-E8's ballasts", qb)],
             pack=("chg", cbal["parts"]["cells"]), D="prof", col=None, d=T["d_hold"], c1=True, env=True),
        dict(id="M9", label="the same, warm end", amb=day[1], lid="open", heat=None, pack=("chg", cbal["parts"]["cells"]), D="prof", col=None,
             d=T["d_hold"], c1=True, env=True)]
    modes[-1]["heat"] = modes[-2]["heat"]
    for m_ in modes:
        m_["Q"] = sum(v for _k, v in m_["heat"])

    def lines(m_, option, route):
        L, scr = [], []
        kind, p_ = m_["pack"]
        rise = p_ / gb
        if kind == "dis":
            L.append(("the cells: the hot stop H1 at a +%.1f C reading (CONOPS 4c; a hot stop inside the envelope ends the mode)" % th["h1"],
                      "CONTROL, ends the mode", th["h1"] - rise, "the cells' hot stop H1"))
            L.append(("the cells: the 35E's discharge to +%.0f C at the surface" % th["dis"], "MAKER operating", th["dis"] - rise, "the cells' discharge +%.0f C" % th["dis"]))
            if m_["c1"]:
                L.append(("the cells: C1's cell trigger +%.0f C (the profile unshed)" % th["c1_cell"], "CONTROL, sheds the profile", th["c1_cell"] - rise, "C1's cell trigger"))
        elif kind == "idle":
            L.append(("the cells idle at the air: the hot stop H1 at +%.1f C" % th["h1"], "CONTROL, ends the mode", th["h1"], "the idle cells' hot stop H1"))
            L.append(("the cells idle: E3-A's every cell surface at most +%.0f C (the 35E's one-month storage to +%.0f C)" % (th["st1m"], th["st1m"]),
                      "MAKER storage; E3-A's pass line", th["st1m"], "the idle cells' +%.0f C" % th["st1m"]))
        elif kind == "chg":
            L.append(("the cells idle at the air before the charge: T3's start at %.0f C" % th["t3"], "CONTROL, no charge starts", th["t3"], "T3's charge start"))
            L.append(("the cells charging: T4's stop above %.0f C" % th["t4"], "CONTROL, a running charge stops", th["t4"] - rise, "T4 on the charging cells"))
            L.append(("the cells charging: OTC at %.1f C" % th["otc"], "CONTROL, the charge held off", th["otc"] - rise, "OTC"))
            L.append(("the cells charging: the 35E's charge to +%.0f C at the surface" % th["chg"], "MAKER operating", th["chg"] - rise, "the cells' charge +%.0f C" % th["chg"]))
        if m_["c1"]:
            L.append(("the inside air: C1's trigger +%.0f C (CONOPS 4)" % th["c1_air"], "CONTROL, sheds the profile", th["c1_air"], "C1's air trigger"))
        if m_["env"] and option == "as ruled":
            L.append(("the SGP41's sensing at its bay air to Table 4's +%.0f C" % th["sgp4"], "MAKER recommended (Table 4)", th["sgp4"], "the SGP41's Table 4"))
        if m_["env"] and option == "A":
            L.append(("the BME688 in the SGP41's place: gas sensing electrically operable to +%.0f C" % th["bme"],
                      "MAKER operating (\"actual performance may vary\")", th["bme"], "the BME688's +%.0f C" % th["bme"]))
        if option in ("as ruled", "C") or not m_["env"]:
            scr.append(("the SGP41 unpowered above its 54.0 C reading (its protective shutdown): Table 5's short-term storage to +%.0f C" % th["sgp_st5"],
                        "ABSOLUTE: a screen, survival INCONCLUSIVE until Sensirion states it", th["sgp_st5"]))
        for p in PARTS:
            if p["k"] == "SGP41":
                continue
            st = PROFILE_STATES[p["k"]] if m_["col"] is None else (p.get("route") or p["now"])[m_["col"]]
            gv = govern(p, st, S)
            lim, cat = gv["lim"], gv["cat"]
            if route and p["k"] in ROUTE_P85:
                lim, cat = hi_of(S, "nkk_mbn"), CAT["nkk_mbn"] + " (the route's pick)"
            off = m_["d"] if p["where"] == "inside" else 0.0
            if route and p["where"] == "inside" and lim is not None and lim <= 70.0 + 1e-9:
                off = 0.0
            where = {"inside": "its local air%s" % (" (the exhaust, +%.2f K)" % off if off else ""), "face": "the face (at most the mixed air)",
                     "wall": "the wall (at most the mixed air)"}[p["where"]]
            if lim is not None:
                L.append(("%s, %s, at %s" % (p["k"], st, where), "%s%s" % (cat, ", INFERRED to cover it unpowered" if "INFERRED" in gv["basis"] else ""),
                          lim - off, "the %s's +%.0f C" % (p["k"], lim)))
            elif gv["absv"] is not None:
                scr.append(("%s, %s" % (p["k"], st), "ABSOLUTE: a screen", gv["absv"] - off))
        for (b, ref), dd in sorted(D[m_["D"]].items()):
            if dd["rec"] is None or (route and dd["part"].startswith("TLV75533")):
                continue
            L.append(("%s %s %s: its recommended junction +%.0f C, own rise %.1f K at the mixed air" % (dd["part"], b, ref, dd["rec"], dd["p"] * dd["th"]),
                      "MAKER recommended junction, MODELED rise", dd["rec"] - dd["p"] * dd["th"], "%s %s's junction" % (b, ref)))
        L.append(("every other fitted line, rated +%.0f C or more at its local air (section 3, P5)" % th["other"], "MAKER operating or recommended",
                  th["other"] - m_["d"], "every other line"))
        out = []
        for name, cat, tmax, short in L:
            room = tmax - m_["amb"]
            out.append({"name": name, "short": short, "cat": cat, "t": tmax, "g": m_["Q"] / room if room > 1e-9 else math.inf})
        out.sort(key=lambda x: -x["g"])
        return out, scr
    t1 = dep["th1"]

    def u_rel(dt):
        return 2.0 * math.sqrt((t1["u_dt"] / dt) ** 2 + P_U_REL ** 2 + LEAD_U_REL ** 2)

    def reading_for(tg, p_):
        # g (1 - U(rise)) rises and then falls as the rise shrinks: bisect below its peak; none if the peak is under the target
        f = lambda g_: g_ * (1.0 - u_rel(p_ / g_))
        gs = [0.3 + 0.05 * i for i in range(800)]
        g_pk = max(gs, key=f)
        if not math.isfinite(tg) or f(g_pk) < tg:
            return math.inf
        return _inv(f, tg, 0.3, g_pk)
    for m_ in modes:
        m_["by"] = {}
        for opt in OPTIONS:
            ln, scr = lines(m_, opt, True)
            gov = ln[0]
            stated = [x for x in ln if "INFERRED" not in x["cat"]][0]
            m_["by"][opt] = {"lines": ln, "screens": scr, "gov": gov, "read": reading_for(gov["g"], m_["Q"]), "stated": stated,
                             "read_stated": reading_for(stated["g"], m_["Q"])}
        ln, _ = lines(m_, "as ruled", False)
        m_["designed"] = {"lines": ln, "gov": ln[0]}
    # B4's figures: K7 and K8 (T3's start) on the model's boundary and with the solar stage's ballasts, with their bench readings
    b4 = {"rows": [], "eta_chg": pb.ETA_CHG, "ichg": pb.ICHG, "rise": (cbal["parts"]["cells"] / pb.G_BLK[1], cbal["parts"]["cells"] / pb.G_BLK[0])}
    for amb_ in day:
        for q_ in (cbal["heat"], hr["q_chg"]):
            g_ = q_ / (th["t3"] - amb_)
            b4["rows"].append((amb_, q_, g_, reading_for(g_, q_)))
    # the bench points (12d): one per heat and lid state; M6 shares M2's point (the same heat and lid), M9 shares M8's
    by_id = {m_["id"]: m_ for m_ in modes}
    points = []
    for ids in (("M2", "M6"), ("M1",), ("M4",), ("M3",), ("M7",), ("M5",), ("M8", "M9")):
        m0 = by_id[ids[0]]
        reads = []
        for i_ in ids:
            for opt in ("as ruled", "C"):
                b = by_id[i_]["by"][opt]
                reads.append((i_, opt, b["gov"]["short"], b["gov"]["g"], b["read"], b["stated"]["short"], b["stated"]["g"], b["read_stated"]))
        finite = [r_[4] for r_ in reads if math.isfinite(r_[4])] + [r_[7] for r_ in reads if math.isfinite(r_[7])]
        g_lo = min(finite)
        tau = max(T["kJ"]) * 1000.0 / g_lo / 3600.0
        points.append({"ids": ids, "Q": m0["Q"], "lid": m0["lid"], "reads": reads, "tau": tau, "steady": math.log(100.0) * tau, "fit": 3.0 * tau})
    return {"th": th, "modes": modes, "gb": gb, "b4": b4, "points": points, "rise_hi": [m_["pack"][1] / pb.G_BLK[1] for m_ in modes]}


def rc_amb(R, key):
    return [x for x in R["rc"]["conds"] if x[0] == key][0][3]


def battery_run(C, R):
    """Section 12c (astra-check-l4close-1 B7): the battery-only PS-IDLE-SPEC run from +20 C coupled to C1: the inside air on the
    enclosure model integrated in time (one node, C the kit's thermal mass), C1 moving the kit to the heat stage on the inside air's
    +50 C, the run ending on the usable energy; the hot stop on the cells checked throughout."""
    import math
    T, pb, red2, cb = C["T"], C["pb"], C["red2"], R["cb"]
    pm = R["pm"]
    th = pm["th"]
    amb = rc_amb(R, "K6")
    f_p = pb.state_full("IDLESPEC", "plan")
    f_hs = pb.state_full("RED", "plan", red2.SURVR)
    p1, p2 = f_p["pb"], f_hs["pb"]
    q1 = f_p["pb"] - f_p["outside"] + pb.pack_i2r(f_p["pb"])
    q2 = f_hs["pb"] - f_hs["outside"] + pb.pack_i2r(f_hs["pb"])
    r1, r2 = pb.pack_i2r(p1) / pm["gb"], pb.pack_i2r(p2) / pm["gb"]
    m_ = need(text(L4E10_OUT), r"35E 4S3P\s+[^\n]*?-> (\d+\.\d) Wh, (\d\.\d\d) h at \+20 C", "the 35E's usable energy at +20 C")
    e_use, h_energy = float(m_.group(1)), float(m_.group(2))
    t_energy = e_use / p1
    rise_c1 = th["c1_air"] - amb
    # the reviewer's check reproduced: a constant G, C 8 kJ/K
    def t_const(g, c_kj, q, theta):
        x = 1.0 - theta * g / q
        return None if x <= 0 else -c_kj * 1000.0 / g * math.log(x) / 3600.0
    rev = []
    for g in (0.6711, 0.7404):
        rev.append((g, t_const(g, 8.0, q1, rise_c1), amb + q1 / g * (1.0 - math.exp(-t_energy * 3600.0 * g / 8000.0))))
    # the enclosure model's own G(rise) (section 9's, lid open, still air outside, at +20 C), tabulated and integrated
    grid = [1.0 + 1.0 * i for i in range(0, 60)]
    qo = {}
    for lbl, cfg in (("the bound", cb["cons"]), ("the coefficients' other ends", cb["opt"])):
        qo[lbl] = [enclosure_g(amb, th_, "open", cfg, cb["geo"])["g"] * th_ for th_ in grid]

    def q_out(lbl, theta):
        if theta <= grid[0]:
            return qo[lbl][0] * theta / grid[0]
        for i in range(1, len(grid)):
            if theta <= grid[i]:
                f = (theta - grid[i - 1]) / (grid[i] - grid[i - 1])
                return qo[lbl][i - 1] + f * (qo[lbl][i] - qo[lbl][i - 1])
        return qo[lbl][-1] * theta / grid[-1]
    runs = []
    dt = 10.0
    for lbl in qo:
        for c_kj in T["kJ"]:
            c_ = c_kj * 1000.0
            theta, t, e, mode, t_c1, cell_max, air_max = 0.0, 0.0, 0.0, "profile", None, amb, amb
            while e < e_use * 3600.0:
                p_, q_, r_ = (p1, q1, r1) if mode == "profile" else (p2, q2, r2)
                theta += (q_ - q_out(lbl, theta)) / c_ * dt
                t += dt
                e += p_ * dt
                cell_max = max(cell_max, amb + theta + r_)
                air_max = max(air_max, amb + theta)
                if mode == "profile" and amb + theta >= th["c1_air"]:
                    mode, t_c1 = "heat stage", t
                if amb + theta + r_ >= th["h1"]:
                    break
            runs.append({"label": lbl, "c": c_kj, "t_c1": None if t_c1 is None else t_c1 / 3600.0, "t_end": t / 3600.0, "cell_max": cell_max,
                         "air_max": air_max, "hot_stop": amb + theta + r_ >= th["h1"], "e_profile": (t_c1 if t_c1 else t) * p1 / 3600.0})
    # the constant-G line at which the profile never reaches C1 (K6's line, the steady state at C1), and the one at which it reaches
    # C1 just as its energy ends (one node, C at each end of 32.53's range)
    g_never = q1 / rise_c1
    g_full = []
    for c_kj in T["kJ"]:
        g_full.append((c_kj, _inv(lambda g: -(amb + q1 / g * (1.0 - math.exp(-t_energy * 3600.0 * g / (c_kj * 1000.0)))), -th["c1_air"], 0.05, 5.0)))
    return {"amb": amb, "p1": p1, "p2": p2, "q1": q1, "q2": q2, "r1": r1, "r2": r2, "e_use": e_use, "h_energy": h_energy, "t_energy": t_energy,
            "rev": rev, "runs": runs, "g_never": g_never, "g_full": g_full, "rise_c1": rise_c1, "dt": dt}


def outside_cap(amb, rise, cfg, geo, lid_state, k_fin=1.0, a_free=0.0, skin=None, floor=False, n=50):
    """The outside surfaces' capacity (W/K) at a rise with the inside resistance at zero: every inner face at the inside air
    (the plate's 3 mm aluminium taken as isothermal); lid open, the plate's outer face (fins of multiplier k_fin on a_free) and,
    with skin = (R_strap, A_skin, H), the strap to the open lid's skin; lid closed, the enclosed layer, the lid's shell and its
    outside films; the walls through the PP shell; the floor only when credited (its feet over a support at the ambient)."""
    ta = amb + 273.15
    ep, es, kpp, fo = cfg["eps_plate"], cfg["eps_shell"], cfg["k_pp"], cfg["f_open"]
    tk = geo["t_wall"] / kpp
    a, aw, awo = geo["a_plate"], geo["a_wall"], geo["a_wall_out"]
    am = 0.5 * (aw + awo)
    q = {}
    th_wo = _inv(lambda th: awo * (h_vert(th, geo["h_out"], ta + th / 2) + h_rad(es, 1.0, ta + th, ta)) * th - (rise - th) * am / tk,
                 0.0, 0.0, rise, n)
    q["walls"] = (rise - th_wo) * am / tk
    if lid_state == "open":
        q["plate"] = ((a - a_free) + a_free * k_fin) * (h_up(rise, geo["l_plate"], ta + rise / 2) + h_rad(ep, fo, ta + rise, ta)) * rise
        if skin:
            r_s, a_s, h_s = skin

            def h_skin(th):
                front = h_vert(th, h_s, ta + th / 2) + h_rad(ep, 1.0, ta + th, ta)
                back = 1.0 / (tk + 1.0 / (h_vert(th, h_s, ta + th / 2) + h_rad(es, 1.0, ta + th, ta)))
                return front + back
            th_s = _inv(lambda th: a_s * h_skin(th) * th - (rise - th) / r_s, 0.0, 0.0, rise, n)
            q["lid skin"] = (rise - th_s) / r_s
    else:
        at, ask = geo["a_lid_top"], geo["a_lid_skirt"]
        e_gap = 1.0 / (1.0 / ep + 1.0 / es - 1.0)

        def total(qq):
            th_lo = _inv(lambda th: (at * (h_up(th, geo["l_lid"], ta + th / 2) + h_rad(es, 1.0, ta + th, ta))
                                     + ask * (h_vert(th, geo["lid_depth"], ta + th / 2) + h_rad(es, 1.0, ta + th, ta))) * th, qq, 0.0, 500.0, n)
            th_li = th_lo + qq * tk / (at + ask)
            tli = ta + th_li
            d_gap = _inv(lambda d: a * (h_gap(d, geo["gap"], tli + d / 2) + h_rad(e_gap, 1.0, tli + d, tli)) * d, qq, 0.0, 500.0, n)
            return th_li + d_gap
        q["plate, through the closed lid"] = _inv(total, rise, 0.0, 500.0, n)
    if floor:
        af = geo["a_floor"]
        e_fl = 1.0 / (1.0 / es + 1.0 / 0.9 - 1.0)
        th_fo = _inv(lambda th: af * (air_props(ta + th / 2)[0] / geo["feet"] + h_rad(e_fl, 1.0, ta + th, ta)) * th - (rise - th) * af / tk,
                     0.0, 0.0, rise, n)
        q["floor"] = (rise - th_fo) * af / tk
    return {"g": sum(q.values()) / rise, "q": q}


def caps(C, R):
    """Section 12e (the addendum to the fix round): every governing and stated line of 12a against the outside surfaces'
    capacity with a perfect inside film, bare and with the combined heat-rejection route (10b: R-170 fins, R-171 loads into the
    plate, R-172 the lid skin), at each mode's own ambient and rise; class (i) reachable bare, T-H1 decides; (ii) reachable only
    with the route, T-H1 with the route decides; (iii) over the capacity even with the route: no measurement passes it."""
    import math
    T, pb, red2 = C["T"], C["pb"], C["red2"]
    cb, hr, pm = R["cb"], R["hr"], R["pm"]
    geo, cons, opt = cb["geo"], cb["cons"], cb["opt"]
    skin = (hr["r_strap"], geo["a_lid_top"], hr["lid_h"])
    md = {m_["id"]: m_ for m_ in pm["modes"]}
    lines = []
    for m_ in pm["modes"]:
        seen = set()
        for opt_ in ("as ruled", "C"):
            b = m_["by"][opt_]
            for ln, tag in ((b["gov"], "governing, %s" % opt_), (b["stated"], "maker-stated, %s" % opt_)):
                key = (ln["short"], round(ln["t"], 6))
                if key in seen:
                    continue
                seen.add(key)
                lines.append({"mode": m_["id"], "lid": m_["lid"], "amb": m_["amb"], "Q": m_["Q"], "line": ln, "tag": tag})
        if m_["id"] in ("M8", "M9"):   # T3's start, K7 and K8
            t3l = [x for x in m_["by"]["C"]["lines"] if x["short"] == "T3's charge start"][0]
            lines.append({"mode": m_["id"], "lid": m_["lid"], "amb": m_["amb"], "Q": m_["Q"], "line": t3l, "tag": "the start line (K7, K8)"})
    for e in lines:
        rise = e["line"]["t"] - e["amb"]
        e["rise"] = rise
        if rise <= 1e-9:
            e.update(bare=(0.0, 0.0), route=(0.0, 0.0), cls="iii", short_g=math.inf, short_w=e["Q"], route_q={})
            continue
        bare = (outside_cap(e["amb"], rise, cons, geo, e["lid"]), outside_cap(e["amb"], rise, opt, geo, e["lid"], floor=True))
        if e["lid"] == "open":
            route = (outside_cap(e["amb"], rise, cons, geo, "open", K_FIN[0], hr["a_free"], skin),
                     outside_cap(e["amb"], rise, opt, geo, "open", K_FIN[1], hr["a_free"], skin, floor=True))
        else:
            route = bare   # the route acts with the lid open: closed, the fins sit in the enclosed layer and the skin faces the plate
        need = e["line"]["g"]
        e["bare"], e["route"] = (bare[0]["g"], bare[1]["g"]), (route[0]["g"], route[1]["g"])
        e["route_q"] = route[0]["q"]
        if need <= e["bare"][1] + 1e-12:
            e["cls"] = "i"
        elif need <= e["route"][1] + 1e-12:
            e["cls"] = "ii"
        else:
            e["cls"] = "iii"
        e["only_opt"] = (e["cls"] == "i" and need > e["bare"][0]) or (e["cls"] == "ii" and need > e["route"][0])
        e["short_g"] = need - e["route"][1] if e["cls"] == "iii" else 0.0
        e["short_w"] = e["Q"] - e["route"][1] * rise if e["cls"] == "iii" else 0.0
    # the options' figures: charging only in a shed state (the heat stage charging on the design day, its balance plus the ballasts)
    q_hs_chg = T["chg_hs"]["heat"] + T["qb"]
    t4l = {m_: [x for x in md[m_]["by"]["C"]["lines"] if x["short"] == "T4 on the charging cells"][0] for m_ in ("M8", "M9")}
    shed = []
    for mid in ("M8", "M9"):
        amb = md[mid]["amb"]
        rise = t4l[mid]["t"] - amb + (md[mid]["pack"][1] - T["chg_hs"]["parts"]["cells"]) / pm["gb"]
        need = q_hs_chg / rise
        shed.append({"mode": mid, "amb": amb, "Q": q_hs_chg, "rise": rise, "need": need,
                     "bare": outside_cap(amb, rise, cons, geo, "open")["g"], "bare_opt": outside_cap(amb, rise, opt, geo, "open", floor=True)["g"]})
    # the e-paper at the plate rather than at the mixed air: the plate's fraction of the rise on the bound (section 9) and W4's high end
    ep_ = {}
    for mid in ("M6", "M7"):
        m_ = md[mid]
        f_b = cb["E3-O" if mid == "M6" else "E5"]["open"]["f_plate"]
        lim_ep = [x for x in m_["by"]["C"]["lines"] if x["short"].startswith("the EPAPER")][0]["t"]
        room = lim_ep - m_["amb"]
        ep_[mid] = {"f": f_b, "f_hi": T["f_plate"][1], "need": (None if room <= 0 else f_b * m_["Q"] / room),
                    "need_hi": (None if room <= 0 else T["f_plate"][1] * m_["Q"] / room)}
    ceil_sgp = {}
    for mid in ("M3", "M4"):
        m_ = md[mid]
        ceil_sgp[mid] = tuple(_inv(lambda a_: a_ + m_["Q"] / outside_cap(a_, max(50.0 - a_, 0.05), cf, geo, "closed", floor=fl)["g"], 50.0, -20.0, 49.95)
                              for cf, fl in ((cons, False), (opt, True)))
    k1 = (outside_cap(T["t_use"], 15.0, cons, geo, "open")["g"], outside_cap(T["t_use"], 15.0, opt, geo, "open", floor=True)["g"])
    fin_add = ((K_FIN[0] - 1.0) * hr["a_free"], (K_FIN[1] - 1.0) * hr["a_free"])
    return {"ceil_sgp": ceil_sgp, "k1": k1, "fin_add": fin_add, "lines": lines, "shed": shed, "q_hs_chg": q_hs_chg, "epaper": ep_, "skin": skin,
            "check9": (outside_cap(A_e3o(C), cb["E3-O"]["rise"], cons, geo, "open")["g"], cb["E3-O"]["cap"],
                       outside_cap(C["A"]["e5"][4], cb["E5"]["rise"], cons, geo, "open")["g"], cb["E5"]["cap"])}


def md_cap(mid, R, opt, stated=False):
    m_ = [x for x in R["pm"]["modes"] if x["id"] == mid][0]
    return m_["by"][opt]["stated" if stated else "gov"]["g"]


def A_e3o(C):
    return C["A"]["e3o_t"]


def hr_q(R):
    return R["hr"]["q_prof"]


def t_use_(R):
    return R["T"]["t_use"]


def ap_need_by(R):
    return R["ap"]["c"]["trip"]["need_by"]


def conservative_bound(C, R, ap, dep):
    """Section 9: a first-principles conservative lower bound on the conductance in each lid state with the fans, against the
    lines and the session's fallback; U-02's class (CONFIRMS or DECIDES) and the smallest experiment."""
    import math
    T, A, w4 = C["T"], C["A"], C["w4"]
    gm = A["geo_m"]
    gap = [float(x) / 1000.0 for x in need(text(W4_PY), r"the (\d+\.\d+) to (\d+\.\d+) mm enclosed gap", "W4's lid gap").groups()]
    geo = {"a_plate": w4.A_FACE, "l_plate": w4.A_FACE / (2.0 * (0.3655 + 0.2495)),
           "a_wall": 2.0 * (gm["mid"][0] + gm["mid"][1]) * gm["shoulder"], "h_in": gm["shoulder"], "h_out": gm["depth"],
           "a_wall_out": 2.0 * (gm["mid"][0] + gm["mid"][1] + 4.0 * gm["t_wall"]) * gm["depth"], "feet": gm["feet"] / 1000.0,
           "l_floor": gm["floor"][0] * gm["floor"][1] / (2.0 * (gm["floor"][0] + gm["floor"][1])),
           "t_wall": gm["t_wall"], "l_flow": gm["mid"][0],
           "a_lid_top": gm["ceiling"][0] * gm["ceiling"][1], "l_lid": gm["ceiling"][0] * gm["ceiling"][1] / (2.0 * (gm["ceiling"][0] + gm["ceiling"][1])),
           "a_lid_skirt": 2.0 * (gm["parting"][0] + gm["parting"][1]) * gm["lid_depth"], "lid_depth": gm["lid_depth"],
           "gap": max(gap), "a_floor": gm["floor"][0] * gm["floor"][1]}
    cons = {"eps_plate": EPS_PLATE[0], "eps_shell": EPS_SHELL[0], "k_pp": K_PP[0], "f_open": F_OPEN[0], "v": 0.0, "rad_in": False}
    opt = {"eps_plate": EPS_PLATE[1], "eps_shell": EPS_SHELL[1], "k_pp": K_PP[1], "f_open": F_OPEN[1], "v": 0.0, "rad_in": False}
    c = ap["c"]
    marg = {"E5": (A["e5"][4], c["trip"]["need_by"] - A["e5"][4]), "E3-O": (A["e3o_t"], c["trip"]["need_by"] - A["e3o_t"])}
    cb = {"geo": geo, "cons": cons, "opt": opt, "gap": gap}
    for mg, (amb, rise) in marg.items():
        r_ = {"amb": amb, "rise": rise, "open": enclosure_g(amb, rise, "open", cons, geo), "open_opt": enclosure_g(amb, rise, "open", opt, geo),
              "closed": enclosure_g(amb, rise, "closed", cons, geo)}
        r_["v"] = [(v_, enclosure_g(amb, rise, "open", dict(cons, v=v_), geo)["g"]) for v_ in V_SENS]
        r_["rad"] = enclosure_g(amb, rise, "open", dict(cons, rad_in=True), geo)["g"]
        r_["rad_v"] = enclosure_g(amb, rise, "open", dict(cons, rad_in=True, v=0.5), geo)["g"]
        r_["floor"] = enclosure_g(amb, rise, "open", dict(cons, floor=True), geo)["g"]
        r_["cap"] = enclosure_g(amb, rise, "open", dict(cons, v=50.0), geo)["g"]
        r_["opt_all"] = enclosure_g(amb, rise, "open", dict(opt, floor=True, rad_in=True, v=1.0), geo)["g"]
        cb[mg] = r_
    cb["env_closed"] = enclosure_g(T["t_use"], 15.0, "closed", cons, geo)
    cb["env_open"] = enclosure_g(T["t_use"], 15.0, "open", cons, geo)
    # the floors the bound is compared with: section 8's (W4's plate fraction) and the same recomputed on the bound's own films
    qd, q5, q3 = dep["deep"]["q"] + T["qb"], T["q_m"] + T["qb"], T["q_hs"] + T["qb"]
    d5, d3 = T["d_hold"], T["d_hs"]
    fb5, fb3 = cb["E5"]["open"]["f_plate"], cb["E3-O"]["open"]["f_plate"]
    lim70, lim80, lim85 = c["trip"]["need_by"], 80.0, 85.0
    a5, a3 = marg["E5"][0], marg["E3-O"][0]
    fl = {
        "E5": {"section 8 (W4's plate fraction), F4 with F3": dep["plate"]["e5_deep_floor"],
               "the bound's plate fraction, F4 with F3, the +80 C connectors in the exhaust": max(fb5 * qd / (lim70 - a5), qd / (lim80 - a5 - d5)),
               "the same, the connectors out of the exhaust": max(fb5 * qd / (lim70 - a5), qd / (lim80 - a5)),
               "the same, the +80 C connectors replaced by +85 C parts (the module's +85 C binds)": max(fb5 * qd / (lim70 - a5), qd / (lim85 - a5))},
        "E3-O": {"section 8 (W4's plate fraction), F4": dep["plate"]["e3o_floor"],
                 "section 8, F4, the connectors out of the exhaust": dep["plate"]["e3o_floor_out"],
                 "the bound's plate fraction, F4, the +80 C connectors in the exhaust": max(fb3 * q3 / (lim70 - a3), q3 / (lim80 - a3 - d3)),
                 "the same, the connectors out of the exhaust": max(fb3 * q3 / (lim70 - a3), q3 / (lim80 - a3)),
                 "the same, the +80 C connectors replaced by +85 C parts (the module's +85 C binds)": max(fb3 * q3 / (lim70 - a3), q3 / (lim85 - a3))}}
    cb["floors"] = fl
    cb["lines"] = {"E5": c["gmax"], "E3-O": c["g_e3o"]}

    def settle(amb, q):
        r = _inv(lambda r_: enclosure_g(amb, r_, "open", cons, geo)["g"] * r_, q, 0.05, 400.0)
        e = enclosure_g(amb, r, "open", cons, geo)
        return {"rise": r, "air": amb + r, "plate": amb + e["f_plate"] * r, "g": e["g"]}
    ops = {"E5, the hold": (a5, q5, d5), "E5, the deeper hold (F3)": (a5, qd, d5), "E3-O, the heat stage": (a3, q3, d3)}
    cb["ops"] = {}
    for k_, (amb, q, dpl) in ops.items():
        o = settle(amb, q)
        o["checks"] = [("the +70 C class on the plate (F4)", o["plate"], lim70), ("the +80 C connectors in the exhaust", o["air"] + dpl, lim80),
                       ("the +80 C connectors out of it", o["air"], lim80), ("the module, +85 C at its intake (device set)", o["air"], lim85)]
        cb["ops"][k_] = o
    # with every session measure (F4, F3 in E5, the connectors to +85 C parts, the HX magnetics and the wider buttons) the
    # module's +85 C binds: the conductance it needs against the bound's at the same rise
    cb["bind"] = {}
    for k_, amb, q in (("E5 with F4 and F3", a5, qd), ("E3-O with F4", a3, q3)):
        need_g = q / (lim85 - amb)
        have = enclosure_g(amb, lim85 - amb, "open", cons, geo)["g"]
        cr = {"internal radiation credited": dict(cons, rad_in=True), "the floor credited": dict(cons, floor=True),
              "internal radiation and the floor credited": dict(cons, rad_in=True, floor=True)}
        credits = [(lbl, enclosure_g(amb, lim85 - amb, "open", cfg_, geo)["g"]) for lbl, cfg_ in cr.items()]
        gv = lambda v_: enclosure_g(amb, lim85 - amb, "open", dict(cons, v=v_), geo)["g"]
        v_need = _inv(gv, need_g, 0.0, 20.0) if need_g > have and gv(20.0) >= need_g else (0.0 if need_g <= have else None)
        gvr = lambda v_: enclosure_g(amb, lim85 - amb, "open", dict(cons, v=v_, rad_in=True, floor=True), geo)["g"]
        v_need_cr = _inv(gvr, need_g, 0.0, 20.0) if need_g > credits[-1][1] and gvr(20.0) >= need_g else (0.0 if need_g <= credits[-1][1] else None)
        cb["bind"][k_] = {"need": need_g, "have": have, "gap": need_g - have, "rise": lim85 - amb, "credits": credits, "v_need": v_need,
                          "v_need_cr": v_need_cr}
    # the lines need more than any inside film can give on the bound's outside: the cap with an unbounded inside film
    cb["cap"] = {mg: enclosure_g(marg[mg][0], marg[mg][1], "open", dict(cons, v=50.0), geo)["g"] for mg in marg}
    cb["air_at_bound"] = {"E5": a5 + q5 / cb["E5"]["open"]["g"], "E5_deep": a5 + qd / cb["E5"]["open"]["g"], "E3-O": a3 + q3 / cb["E3-O"]["open"]["g"]}
    best = {mg: max(cb[mg]["open"]["g"], 0.0) for mg in marg}
    cb["clears"] = {"E5": cb["bind"]["E5 with F4 and F3"]["gap"] <= 0, "E3-O": cb["bind"]["E3-O with F4"]["gap"] <= 0}
    cb["gap_w"] = {"E5": cb["bind"]["E5 with F4 and F3"]["gap"], "E3-O": cb["bind"]["E3-O with F4"]["gap"]}
    cb["gap_s8"] = {"E5": fl["E5"]["section 8 (W4's plate fraction), F4 with F3"] - best["E5"],
                    "E3-O": fl["E3-O"]["section 8 (W4's plate fraction), F4"] - best["E3-O"]}
    cb["klass"] = "CONFIRMS" if all(cb["clears"].values()) else "DECIDES"
    # W4's 1.22 W/K reconciled: W4's low case, then one assumption at a time replaced by the bound's
    hin, hof, how, hfl, tk = w4.H_IN_FANS[0], w4.H_OUT_FACE[0], w4.H_OUT_WALL[0], w4.H_OUT_FLOOR[0], w4.T_OVER_K_WALL
    e5o = cb["E5"]["open"]
    ta = marg["E5"][0] + 273.15
    # the bound's converged films, from its paths: back-calculate effective per-area conductances
    def w4lin(a_side, a_floor, h_in_, h_out_face, h_out_wall, h_floor, tk_):
        g_ = a_side / (1.0 / h_in_ + tk_ + 1.0 / h_out_wall) + w4.series(w4.A_FACE * h_in_, w4.A_FACE * h_out_face)
        if h_floor:
            g_ += a_floor / (1.0 / h_in_ + tk_ + 1.0 / h_floor)
        return g_
    # the bound's films at E5 (lid open), evaluated at its own solution
    th_a = marg["E5"][1]
    qp, qw = e5o["q"]["plate"], e5o["q"]["walls"]
    th_p = e5o["f_plate"] * th_a
    hin_b = qp / (w4.A_FACE * (th_a - th_p))
    hout_face_b = qp / (w4.A_FACE * th_p)
    a_w = geo["a_wall"]
    th_wo = _inv(lambda th: a_w * (h_vert(th, geo["h_out"], ta + th / 2) + h_rad(cons["eps_shell"], 1.0, ta + th, ta)) * th, qw, 0.0, 500.0)
    tk_b = geo["t_wall"] / cons["k_pp"]
    th_wi = th_wo + qw * tk_b / a_w
    hin_w = qw / (a_w * (th_a - th_wi))
    hout_w = qw / (a_w * th_wo)
    steps = [("W4's low case (lid open, fans)", w4lin(w4.A_SIDE[0], w4.A_FLOOR[0], hin, hof, how, hfl, tk))]
    steps.append(("the floor adiabatic (the case on its feet)", w4lin(w4.A_SIDE[0], w4.A_FLOOR[0], hin, hof, how, None, tk)))
    steps.append(("the walls' inner area to the plate (CASE-MARGINS)", w4lin(a_w, 0, hin, hof, how, None, tk)))
    steps.append(("the wall 5.34 mm of PP at 0.12 W/mK", w4lin(a_w, 0, hin, hof, how, None, tk_b)))
    steps.append(("the outer films at +60 C with the conservative emissivities and the lid's view", w4lin(a_w, 0, hin, hout_face_b, hout_w, None, tk_b)))
    steps.append(("the inside film: natural convection only, no fan flow and no internal radiation credited",
                  a_w / (1.0 / hin_w + tk_b + 1.0 / hout_w) + w4.series(w4.A_FACE * hin_b, w4.A_FACE * hout_face_b)))
    cb["recon"] = steps
    cb["films"] = {"hin_plate": hin_b, "hin_wall": hin_w, "hout_face": hout_face_b, "hout_wall": hout_w}
    # the smallest experiment: one lid-open, fans-on point at one heater's power; reading thresholds with the expanded uncertainty
    t1 = dep["th1"]
    ph = A["rta_heater"][2]

    def u_rel(dt):
        return 2.0 * math.sqrt((t1["u_dt"] / dt) ** 2 + P_U_REL ** 2 + LEAD_U_REL ** 2)

    def reading_for(target):
        return _inv(lambda g_: g_ * (1.0 - u_rel(ph / g_)), target, 0.3, 20.0)
    targets = [("E5's line, the design as stated (route (c))", c["gmax"]),
               ("E3-O with F4, the connectors in the exhaust (section 8)", fl["E3-O"]["section 8 (W4's plate fraction), F4"]),
               ("E3-O with F4, the connectors out of the exhaust (section 8)", fl["E3-O"]["section 8, F4, the connectors out of the exhaust"]),
               ("E5 with F4 and F3 (section 8)", fl["E5"]["section 8 (W4's plate fraction), F4 with F3"]),
               ("E3-O with every session measure (the module's +85 C binds)", cb["bind"]["E3-O with F4"]["need"]),
               ("E5 with every session measure (the module's +85 C binds)", cb["bind"]["E5 with F4 and F3"]["need"])]
    cb["exp"] = {"power": ph, "targets": [(lbl, tg, reading_for(tg), ph / reading_for(tg)) for lbl, tg in targets],
                 "tau_bound": max(T["kJ"]) * 1000.0 / best["E3-O"] / 3600.0, "tau_line": t1["tau_line"],
                 "rise_bound": ph / best["E5"]}
    cb["exp"]["t_bound"] = math.log(100.0) * cb["exp"]["tau_bound"]
    return cb


# ------------------------------------------------------------------------------------------------ section 9: the conservative bound
# Coefficients of the first-principles lower bound (the consolidation's question of 2 October 2026). Each range is a textbook one
# (INFERRED: no held sheet gives it); the bound takes the end that lowers the conductance, the other end is printed beside it.
EPS_PLATE = (0.70, 0.90)     # anodised aluminium (32.53: the plate is anodised), clear to black anodise, textbook emissivity tables
EPS_SHELL = (0.85, 0.95)     # pigmented polypropylene, textbook emissivity tables; Peli publishes none
EPS_BOARD = 0.85             # solder-masked boards facing the plate (textbook 0.85 to 0.95), for the internal radiation credit only
K_PP = (0.12, 0.22)          # W/mK, polypropylene copolymer, textbook polymer tables; Peli publishes none
F_OPEN = (0.70, 1.00)        # ASSUMPTION: the plate's view of the surroundings past the open lid (the lid taken as reradiating)
F_VIEW_IN = 0.5              # ASSUMPTION: the plate's view of the dissipating stack beneath it, for the internal radiation credit only
V_SENS = (0.2, 0.5, 1.0)     # m/s across the inner faces, the fans' forced flow as a sensitivity (no held placement or pick)
G_N = 9.81


def air_props(t_k):
    """Dry air at t_k: Sutherland's laws for the viscosity and the conductivity (White, Viscous Fluid Flow), the ideal gas,
    cp 1007 J/kgK. Returns k, nu, alpha, Pr, beta (INFERRED, textbook)."""
    mu = 1.716e-5 * (t_k / 273.15) ** 1.5 * (273.15 + 110.4) / (t_k + 110.4)
    k = 0.0241 * (t_k / 273.15) ** 1.5 * (273.15 + 194.0) / (t_k + 194.0)
    rho = P_ATM / (R_AIR * t_k)
    return k, mu / rho, k / (rho * CP_AIR), mu * CP_AIR / k, 1.0 / t_k


def _ra(dt, length, t_film):
    k, nu, al, pr, be = air_props(t_film)
    return G_N * be * abs(dt) * length ** 3 / (nu * al), k, pr


def h_up(dt, length, t_film):
    """A heated plate facing up, or a cooled one facing down: Nu = 0.54 Ra^(1/4) (Ra up to 1e7), 0.15 Ra^(1/3) above,
    L = A/P (McAdams; Lloyd and Moran; Incropera and DeWitt eqs 9.30 and 9.31)."""
    if dt <= 0:
        return 0.0
    ra, k, _pr = _ra(dt, length, t_film)
    nu_ = 0.54 * ra ** 0.25 if ra < 1e7 else 0.15 * ra ** (1.0 / 3.0)
    return nu_ * k / length


def h_vert(dt, length, t_film):
    """A vertical plate: Churchill and Chu, Nu = {0.825 + 0.387 Ra^(1/6) / [1 + (0.492/Pr)^(9/16)]^(8/27)}^2, L = height."""
    if dt <= 0:
        return 0.0
    ra, k, pr = _ra(dt, length, t_film)
    nu_ = (0.825 + 0.387 * ra ** (1.0 / 6.0) / (1.0 + (0.492 / pr) ** (9.0 / 16.0)) ** (8.0 / 27.0)) ** 2
    return nu_ * k / length


def h_gap(dt, gap, t_mean):
    """A horizontal air layer heated from below: Hollands et al. (1975), Nu = 1 + 1.44 [1 - 1708/Ra]+ + [(Ra/5830)^(1/3) - 1]+."""
    if dt <= 0:
        return air_props(t_mean)[0] / gap
    ra, k, _pr = _ra(dt, gap, t_mean)
    nu_ = 1.0 + 1.44 * max(0.0, 1.0 - 1708.0 / ra) + max(0.0, (ra / 5830.0) ** (1.0 / 3.0) - 1.0)
    return nu_ * k / gap


def h_forced(v, length, t_film):
    """Forced laminar flow along a flat plate, average: Nu = 0.664 Re^(1/2) Pr^(1/3) (Re under 5e5)."""
    k, nu, _al, pr, _be = air_props(t_film)
    return 0.664 * (v * length / nu) ** 0.5 * pr ** (1.0 / 3.0) * k / length


def h_rad(eps, view, t1_k, t2_k):
    return eps * view * SIGMA * (t1_k ** 2 + t2_k ** 2) * (t1_k + t2_k)


def _inv(fun, target, lo, hi, n=60):
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if fun(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def enclosure_g(amb_c, rise, lid, cfg, geo):
    """The inside air's conductance to the ambient at a stated air rise (K), lid 'open' or 'closed', from the plate and wall
    paths in parallel (the floor adiabatic unless cfg names a film). Each path is solved for its heat q at the rise."""
    ta = amb_c + 273.15
    ep, es, kpp, f_open = cfg["eps_plate"], cfg["eps_shell"], cfg["k_pp"], cfg["f_open"]
    tk = geo["t_wall"] / kpp

    def h_in(face, d, t_surf_k, t_air_k):
        tf = 0.5 * (t_surf_k + t_air_k)
        hn = h_up(d, geo["l_plate"], tf) if face == "plate" else h_vert(d, geo["h_in"], tf)
        hf = h_forced(cfg["v"], geo["l_flow"], tf) if cfg["v"] > 0 else 0.0
        h = (hn ** 3 + hf ** 3) ** (1.0 / 3.0)
        if face == "plate" and cfg["rad_in"]:
            h += h_rad(1.0 / (1.0 / EPS_BOARD + 1.0 / ep - 1.0), F_VIEW_IN, t_air_k, t_surf_k)
        return h

    def rise_inside(q, area, face, th_s):
        ts = ta + th_s
        return _inv(lambda d: area * h_in(face, d, ts, ts + d) * d, q, 0.0, 500.0)

    def plate_open(q):
        a = geo["a_plate"]
        th_p = _inv(lambda th: a * (h_up(th, geo["l_plate"], ta + th / 2) + h_rad(ep, f_open, ta + th, ta)) * th, q, 0.0, 500.0)
        return th_p + rise_inside(q, a, "plate", th_p)

    def plate_closed(q):
        a, at, ask = geo["a_plate"], geo["a_lid_top"], geo["a_lid_skirt"]
        th_lo = _inv(lambda th: (at * (h_up(th, geo["l_lid"], ta + th / 2) + h_rad(es, 1.0, ta + th, ta))
                                 + ask * (h_vert(th, geo["lid_depth"], ta + th / 2) + h_rad(es, 1.0, ta + th, ta))) * th, q, 0.0, 500.0)
        th_li = th_lo + q * tk / (at + ask)
        e_gap = 1.0 / (1.0 / ep + 1.0 / es - 1.0)
        tli = ta + th_li
        d_gap = _inv(lambda d: a * (h_gap(d, geo["gap"], tli + d / 2) + h_rad(e_gap, 1.0, tli + d, tli)) * d, q, 0.0, 500.0)
        th_p = th_li + d_gap
        return th_p + rise_inside(q, a, "plate", th_p)

    def walls(q):
        a, ao = geo["a_wall"], geo["a_wall_out"]
        th_wo = _inv(lambda th: ao * (h_vert(th, geo["h_out"], ta + th / 2) + h_rad(es, 1.0, ta + th, ta)) * th, q, 0.0, 500.0)
        th_wi = th_wo + q * tk / (0.5 * (a + ao))
        return th_wi + rise_inside(q, a, "wall", th_wi)

    def floor(q):
        a = geo["a_floor"]
        # under the floor: the feet's air gap to a support at the ambient, conduction across it and radiation (INFERRED)
        th_fo = _inv(lambda th: a * (air_props(ta + th / 2)[0] / geo["feet"] + h_rad(1.0 / (1.0 / es + 1.0 / 0.9 - 1.0), 1.0, ta + th, ta)) * th,
                     q, 0.0, 500.0)
        th_fi = th_fo + q * tk / a
        tfi = ta + th_fi
        # above it: the warmer air over a cooler floor, a stable layer, Nu = 0.27 Ra^(1/4) (Incropera and DeWitt eq 9.32)
        d_in = _inv(lambda d: a * (0.27 * _ra(d, geo["l_floor"], tfi + d / 2)[0] ** 0.25 * air_props(tfi + d / 2)[0] / geo["l_floor"]
                                   if d > 0 else 0.0) * d, q, 0.0, 500.0)
        return th_fi + d_in
    paths = {"plate": plate_open if lid == "open" else plate_closed, "walls": walls}
    if cfg.get("floor"):
        paths["floor"] = floor
    out = {}
    for name, fn in paths.items():
        out[name] = _inv(lambda q: fn(q), rise, 0.0, 2000.0)
    g = sum(out.values()) / rise
    plate_th = None
    if lid == "open":
        a = geo["a_plate"]
        q = out["plate"]
        plate_th = _inv(lambda th: a * (h_up(th, geo["l_plate"], ta + th / 2) + h_rad(ep, f_open, ta + th, ta)) * th, q, 0.0, 500.0)
    return {"g": g, "q": out, "f_plate": None if plate_th is None else plate_th / rise}


def compute():
    C = base()
    R, S, T, A, pb, red2 = C["R"], C["S"], C["T"], C["A"], C["pb"], C["red2"]
    locs, hold_ov = C["locs"], C["hold_ov"]
    e3o_t, e5_t, e5_lo, g_floor, qb = A["e3o_t"], A["e5"][4], A["e5"][3], T["g_floor"], T["qb"]
    amb = {"E3-O": e3o_t, "E5": e5_t}
    # ======================================================== 3: the design as it stands (the heat stage at T-H1's floor)
    D_hs, decl = diss_table(C, red2.SURVR)
    D_hold, _ = diss_table(C, hold_ov)
    R["decl"], R["diss_now"] = decl, D_hs
    Lnow = R["locs_now"]
    R["parts_now"] = parts_eval(C, Lnow, "now")
    R["screen"] = screen_rows(C, Lnow, {"E3-O": D_hs, "E5": D_hs}, {p_["k"]: p_ for p_ in R["parts_now"]})
    # ======================================================== 4: three complete approaches
    ap = {}
    # (a) the heat path and the enclosure, no new mode: the heat stage at both margins, the radios on at both, the SGP41 off
    pa_floor = parts_eval(C, Lnow, "a")
    q_a = {"E3-O": T["q_hs"], "E5": T["q_hs"]}
    ga, ga_scr, a_open = g_needs(pa_floor, q_a, amb, qb)
    ga_all = dict(ga, **ga_scr)
    gmax_a = max(max(v.values()) for v in ga_all.values())
    ga_e3o = max(v["E3-O"] for v in ga_all.values())
    ap["a"] = {"g": ga, "screen": ga_scr, "gmax": gmax_a, "g_e3o": ga_e3o, "open": a_open,
               "g_m": [g_line(pa_floor, q_a, amb, qb, mm) for mm in (1.0, 2.0)],
               "plate_floor_e5": Lnow["E5"]["plate"], "g_plate": T["f_plate"][1] * (T["q_hs"] + qb) / 10.0}
    # (c) the route: E3-O exactly as stated (the heat stage, radios on, no hold); E5 under the hold (radios off)
    L_c_floor = {"E3-O": locs(e3o_t, T["q_hs"], g_floor, T["d_hs"]), "E5": locs(e5_t, T["q_m"], g_floor, T["d_hold"])}
    pc_floor = parts_eval(C, L_c_floor, "route")
    q_c = {"E3-O": T["q_hs"], "E5": T["q_m"]}
    gc_, gc_scr, c_open = g_needs(pc_floor, q_c, amb, qb)
    gc_all = dict(gc_, **gc_scr)
    gmax_c = max(max(v.values()) for v in gc_all.values())
    gc_e3o = max(v["E3-O"] for v in gc_all.values())
    gc_e5 = max(v["E5"] for v in gc_all.values())
    L_c = {"E3-O": locs(e3o_t, T["q_hs"], gmax_c, T["d_hs"]), "E5": locs(e5_t, T["q_m"], gmax_c, T["d_hold"])}
    parts_c = parts_eval(C, L_c, "route")
    screen_c = screen_rows(C, L_c, {"E3-O": D_hs, "E5": D_hold}, {p_["k"]: p_ for p_ in parts_c})
    ap["c"] = {"g": gc_, "g_screen": gc_scr, "gmax": gmax_c, "g_e3o": gc_e3o, "g_e5": gc_e5, "open": c_open, "L": L_c, "parts": parts_c,
               "screen": screen_c, "g_m": [g_line(pc_floor, q_c, amb, qb, mm) for mm in (1.0, 2.0)],
               "g_cm45": (T["q_m45"] + qb) / 10.0, "g_hi": (T["q_m_hi"] + qb) / 10.0}
    # the hold's trigger window at the line: E3-O's steady mixed air (no hold there) against the point E5 needs the hold by
    e3o_mix = L_c["E3-O"]["mixed"]
    need_by = min(pr["lim"]["E5"] for pr in R["parts_now"] if pr["k"] in HOLD_OFF)
    tol = S["tmp117_acc"]["v"][0]
    rate = (e5_t - e5_lo) / A["m507"]["ramp_h"] / 3600.0
    lag = rate * (READ_S + TAU_S)
    width = need_by - e3o_mix
    e_allow = (width - 2.0 * tol - lag) / 2.0
    g_plume = (T["q_hs"] + qb) / ((need_by - e3o_t) - T["d_hs"] - 2.0 * tol - lag)
    ap["c"]["trip"] = {"e3o_mix": e3o_mix, "need_by": need_by, "width": width, "tol": tol, "lag": lag, "rate_k_h": rate * 3600.0,
                       "e_allow": e_allow, "plume_window": width - T["d_hs"] - 2.0 * tol - lag, "g_plume": g_plume,
                       "trip_mid": (e3o_mix + tol + need_by - tol - lag) / 2.0,
                       "env_mix": T["t_use"] + (T["q_hs"] + qb) / gmax_c,
                       "e5_hold_mix": L_c["E5"]["mixed"],
                       "widths": [(g_, (need_by - e3o_t) - (T["q_hs"] + qb) / g_) for g_ in (gmax_c, 2.5, gmax_a)]}
    # the SGP41 (B2, B3 of the recheck): its own shutdown and power-on on a reference with a printed maximum error, and the
    # one engineering route for its in-envelope function, a location whose own temperature keeps it inside Table 4
    import math
    err_ref = S["tmp117_acc70"]["v"][0]
    s_abs, s_rec = S["sgp_op"]["v"][1], S["sgp_rec"]["v"][1]
    t_off_x = s_abs - err_ref - SGP_GRAD_K - lag
    t_on_x = s_rec - err_ref - SGP_GRAD_K - lag
    t_off, t_on = floor1(t_off_x), floor1(t_on_x)
    loc_max = t_on - err_ref - SGP_MARGIN_K
    q_env = T["q_hs"] + qb
    t_use = T["t_use"]
    c1_trig = float(need(A["c1"], r"inside air \+(\d+) C", "C1's air trigger").group(1))
    c1_cap = c1_trig + tol + lag
    sg_locs = []
    for name, (flo, fhi) in (("the bay air where board E's U17 sits (as designed)", (1.0, 1.0)),
                             ("the east wall's inner skin in the pack pocket", T["f_wall"]),
                             ("the floor's inner skin under the pack", T["f_floor"])):
        sg_locs.append({"name": name, "f": (flo, fhi), "g_need": fhi * q_env / (loc_max - t_use),
                        "open_line": t_use + fhi * q_env / gmax_c,
                        "closed": [t_use + fhi * q_env / g_ for g_ in T["g_3253_closed"]],
                        "closed_w4": [t_use + fhi * q_env / g_ for g_ in T["w4_closed"]],
                        "c1": t_use + fhi * (c1_cap - t_use)})
    wall = sg_locs[1]
    fw = wall["f"][1]
    gw = wall["g_need"]
    g_closed_max = max(T["g_3253_closed"][1], T["w4_closed"][1])
    g_open_max = max(T["g_3253_open"][1], T["w4_open"][1])
    e3o_loc = e3o_t + fw * q_env / gw
    rec_h = tuple(k_ * 1000.0 / gw * math.log((e3o_loc - loc_max) / SGP_MARGIN_K) / 3600.0 for k_ in T["kJ"])
    stor_rec = S["sgp_rec_st"]["v"]
    st_env = R["env_store"]
    stop_closed = [loc_max - fw * q_env / g_ for g_ in T["g_3253_closed"]]
    stop_open = loc_max - fw * q_env / gmax_c
    stop_bind = all(a_ + q_env / g_ > c1_cap for a_, g_ in zip(stop_closed, T["g_3253_closed"])) and stop_open + q_env / gmax_c > c1_cap
    ap["sgp"] = {"err": err_ref, "grad": SGP_GRAD_K, "lag": lag, "t_off_x": t_off_x, "t_off": t_off, "t_on_x": t_on_x, "t_on": t_on,
                 "off_at": t_off + err_ref + SGP_GRAD_K + lag, "on_at": t_on + err_ref + SGP_GRAD_K + lag, "abs": s_abs, "rec": s_rec,
                 "m": SGP_MARGIN_K, "loc_max": loc_max, "q_env": q_env, "c1_trig": c1_trig, "c1_cap": c1_cap, "locs": sg_locs,
                 "g_closed_max": g_closed_max, "g_open_max": g_open_max, "held_closed": gw <= g_closed_max, "held_open": gw <= g_open_max,
                 "e3o_loc": e3o_loc, "rec_h": rec_h, "warm": st_env[1], "stor_rec": stor_rec, "st_env": st_env, "st_env_1y": R["env_store_1y"],
                 "stor_out": st_env[0] < stor_rec[0] or st_env[1] > stor_rec[1],
                 "marg": {mg: {"bay": L_c[mg]["mixed"], "skin": amb[mg] + fw * (L_c[mg]["mixed"] - amb[mg]), "plume": L_c[mg]["plume"]} for mg in MARGINS},
                 "stor_lim": S["sgp_st"]["v"][1], "stop_closed": stop_closed, "stop_open": stop_open, "stop_bind": stop_bind,
                 "env_air": T["t_use"] + q_env / gmax_c, "env_air_floor": T["in_env"],
                 "bme": {"gas": S["bme_gas"]["v"][1], "env": T["t_use"] + q_env / gmax_c, "e3o": L_c["E3-O"]["mixed"], "e5": L_c["E5"]["mixed"]}}
    # the two TLV75533 regulators the corrected rule finds past their recommended junction (B2)
    reg = {}
    for name, p_w, src in (("E U13 at the model's plan", decl["e_plan_p"], "MODELED"), ("E U13 at its rail's declared typical", decl["e_decl_p"], "INFERRED"),
                           ("C U5 at its rail's declared typical", decl["c_decl_p"], "INFERRED")):
        reg[name] = {"p": p_w, "src": src}
        for pkg, th in (("DBV", decl["th755"]), ("DRV", decl["drv755"])):
            reg[name][pkg] = {mg: L_c[mg]["mixed"] + p_w * th for mg in MARGINS}
    reg_imax_drv = (decl["rec755"] - L_c["E5"]["mixed"]) / decl["drv755"] / (5.0 - 3.3)
    ap["reg"] = {"rows": reg, "imax_drv": reg_imax_drv}
    # the fallback below the line (the hold in E5; the +70 C modules coupled to the plate)
    L_fb = locs(e5_t, T["q_m"], g_floor, T["d_hold"])
    ap["c"]["fallback"] = {"plate": L_fb["plate"], "mixed": L_fb["mixed"], "margin": 70.0 - L_fb["plate"][1],
                           "e3o_plate": Lnow["E3-O"]["plate"], "e3o_margin": 70.0 - Lnow["E3-O"]["plate"][1]}
    # (b) wider-rated parts
    bl = []
    for pr in R["parts_now"]:
        if pr["k"] not in CANDIDATES:
            continue
        key, who, note = CANDIDATES[pr["k"]]
        cand = None if key is None else (S[key]["v"][1] if key == "bme_gas" else S[key]["v"][-1])
        bl.append({"k": pr["k"], "who": who, "note": note, "cand": cand, "key": key,
                   "margin_e5": None if cand is None else cand - pr["temps"]["E5"][1]})
    ap["b"] = {"rows": bl}
    R["ap"] = ap
    # ======================================================== 5 and 6: routes per colliding part; the owner-question test
    route = {}
    vc = {p_["k"]: p_ for p_ in parts_c}
    va = {p_["k"]: p_ for p_ in pa_floor}
    collide = [k for k, p_ in ((p_["k"], p_) for p_ in R["parts_now"]) if any(v_ != "NOT REACHED" for v_ in p_["verdict"].values())]
    for k in collide:
        r_ = {"a": "CONDITIONAL" if k in ga else ("INCONCLUSIVE" if k in ga_scr or va[k]["lim"]["E5"] is None or k == "EPAPER" else "REJECTED")}
        cb = CANDIDATES.get(k)
        r_["b"] = "INCONCLUSIVE" if cb is None else ("OUTSIDE AUTHORITY" if cb[1].startswith("OWNER") else ("CLOSES" if cb[0] else "INCONCLUSIVE"))
        if k in gc_:
            r_["c"] = "CONDITIONAL"
        elif k in gc_scr or k == "EPAPER" or vc[k]["lim"]["E5"] is None:
            r_["c"] = "INCONCLUSIVE"
        else:
            r_["c"] = "REJECTED"
        r_["forced"] = all(x in ("REJECTED", "OUTSIDE AUTHORITY") for x in (r_["a"], r_["b"], r_["c"]))
        route[k] = r_
    R["route"] = route
    sgp = ap["sgp"]
    R["forced_margin"] = [k for k, r_ in route.items() if r_["forced"]]
    R["sgp_forced"] = (not sgp["held_closed"]) or sgp["stor_out"]
    R["forced"] = R["forced_margin"] + (["SGP41 in the envelope"] if R["sgp_forced"] else [])
    R["g2"] = {"g": 2.0, "e3o": e3o_t + q_env / 2.0, "e5": e5_t + (T["q_m"] + qb) / 2.0}
    R["dep"] = dep = dependency(C, R, ap, gc_all, parts_c)
    R["cb"] = conservative_bound(C, R, ap, dep)
    R["hr"] = heat_rejection(C, R)
    R["rc"] = reconcile(C, R)
    R["pm"] = per_mode(C, R)
    R["br"] = battery_run(C, R)
    R["cap"] = caps(C, R)
    # ======================================================== 8: the predicates
    p = {}
    p["P1 pwr_budget and pwr_red2 reproduced byte for byte before any figure"] = R["r0a"] and R["r0b"] and R["r0c"]
    p["P2 T-H1's floor and the inside air reproduce L4-E10's 1.6664 W/K, 70.00 and 75.00 C"] = T["agree_g"] and T["agree_air"]
    p["P3 the acceptance is read: survive and recover, the CM5 not shut down, the monitor and radios on, C1's shedding recorded, E5 logging"] = (
        "survive and recover" in A["e3o_pass"] and "no shutdown" in A["e3o_pass"] and A["e3o_config"].startswith("deployed with the monitor and radios on")
        and "C1's inside-air trigger" in A["controls"] and "logging" in A["e5_config"] and "survive and recover at the margin" in A["d02a"])
    scr = R["screen"]
    p["P4 every fitted line, module and undeclared line is screened"] = len(scr) == R["gc"]["rows"] + R["gc"]["mods"] + R["gc"]["undeclared"]
    lvl1 = [r_ for r_ in scr if any(v_ in ("REACHED", "PLACEMENT") for v_ in r_.get("verdict_l1", r_["verdict"]).values())]
    unread = [r_["part"] for r_ in lvl1 if "level2" not in r_ and not (r_["kind"] == "TA" and r_["max"] is not None and r_["max"] >= 80.0)
              and not r_["part"].startswith("TLV75533")]
    R["unread"] = unread
    p["P5 every line the first pass finds within reach is read one by one, rated to +80 C or more and over only in the exhaust, or the regulators of 5c"] = not unread
    p["P6 approach (a)'s line is over the low-case outer-film cap and under W4's high case"] = T["cap"][0] < gmax_a < T["w4_open"][1]
    p["P7 the route keeps E3-O as stated: every radio on (work) at E3-O, no hold there"] = all(
        dict((p_["k"], p_["route"][0]) for p_ in PARTS)[k] == "work" for k in ("RB9704", "SA868", "PCM2912A", "G6K")) and q_c["E3-O"] == T["q_hs"]
    p["P8 at the line every part routed by the air is inside its governing limit at the mixed air at both margins"] = all(
        pr["k"] not in gc_ or all(pr["temps"][mg][0] <= pr["lim"][mg] + 1e-9 for mg in MARGINS) for pr in parts_c)
    p["P9 the hold lowers the enclosure line: G_c under G_a"] = gmax_c < gmax_a
    p["P10 the owner question is raised only after the routes are assessed: for the SGP41 in the envelope, and for no part at the margins"] = (
        not R["forced_margin"] and R["sgp_forced"])

    def rating_rule_held():
        for rows_ in (R["screen"], screen_c):
            for r_ in rows_:
                if set(r_["verdict"].values()) <= {"NO PART", "OUT OF SCOPE", "NOT FITTED"} or "level2" in r_:
                    continue
                if r_.get("max") is not None and not r_.get("cat"):
                    return False
                if is_abs(r_.get("cat")) and "NOT REACHED" in r_["verdict"].values():
                    return False
        for parts_ in (R["parts_now"], parts_c, pa_floor):
            for pr in parts_:
                for mg in MARGINS:
                    if pr["key"][mg] is not None and (is_abs(CAT[pr["key"][mg]]) or not pr["cat"][mg]):
                        return False
                    if pr["abs_key"][mg] is not None and not is_abs(CAT[pr["abs_key"][mg]]):
                        return False
        for D_ in (D_hs, D_hold):
            for d in D_.values():
                if d["rec_key"] and is_abs(d["rec_cat"]):
                    return False
        return dict((p_["k"], p_) for p_ in PARTS)["SGP41"]["op"] == "sgp_rec" and is_abs(CAT["sgp_op"]) and len(R["heads"]) == len(HEADS)
    p["P11 every judged limit names its category and none is cleared on an absolute rating alone (the SGP41 on Table 4)"] = rating_rule_held()
    p["P12 the SGP41 is off before its local +55 C and its output is used only at or under Table 4's +50 C (printed error, gradient, lag, rounded down)"] = (
        sgp["off_at"] <= s_abs + 1e-9 and sgp["on_at"] <= s_rec + 1e-9 and t_off <= t_off_x and t_on <= t_on_x)
    p["P13 the hold's window exists at the line only with a calibrated reference (e_allow over 0) and not across the whole exhaust spread"] = (
        e_allow > 0 and ap["c"]["trip"]["plume_window"] < 0)
    p["P14 no location holds the SGP41 to Table 4 in the envelope: the coolest skin's line over every lid-closed conductance held, storage outside Table 4"] = (
        not sgp["held_closed"] and sgp["held_open"] and sgp["stor_out"] and sgp["stop_bind"])
    d = R["dep"]
    rw = d["rows"]
    p["P15 the lines' basis: Q over the room to +70 C gives 2.159, 1.806 and 2.709 W/K, and E5's heat is its loads, losses and shore loss summed"] = (
        abs(rw["E5, the hold"]["G"] - gmax_c) < 1e-9 and abs(rw["E3-O, the heat stage"]["G"] - gc_e3o) < 1e-9 and abs(rw["E5, no hold"]["G"] - gmax_a) < 1e-9
        and abs(d["hold"]["p_load"] + d["hold"]["loss"] + d["hold"]["dist"] + d["hold"]["front"] - T["q_m"]) < 1e-9
        and abs(sum(d["hold"]["place"].values()) - T["q_m"]) < 1e-9)
    p["P16 the fans' power is counted: rv-pwr's rows, load_trace's tier-R rows in the 42.8 W profile the replay carries, none among its W with no document"] = (
        len(d["fans_running"]["E5"]) == 2 and len(A["trace_fans"]) == 4 and all(t_ == "R" for _w, t_, _n in A["trace_fans"])
        and A["replay_profile"][0] == A["trace_total"][1] and not any("fan" in nm for _w, nm in A["replay_undoc"][1])
        and abs(sum(w_ for w_, _n in A["replay_undoc"][1]) - A["replay_undoc"][0]) < 0.011 and abs(d["fan_power"][0]["plan"]["state"] - A["trace_total"][1]) < 0.05)
    p["P17 T-H1's pass line lies over 2.159 W/K by its expanded uncertainty and every point reaches steady state in a stated time"] = (
        all(v_["pass"] > gmax_c for v_ in d["th1"]["ub"].values()) and 0 < d["th1"]["t_ss"][0] < d["th1"]["t_ss"][1])
    p["P18 the plate coupling holds E5 and E3-O below E3-O's line, and the deeper hold lowers E5's heat (the session's fallbacks)"] = (
        d["plate"]["e5_floor"] < gc_e3o and d["plate"]["e3o_floor"] < gc_e3o and d["deep"]["q"] < T["q_m"] and d["plate"]["e5_deep_floor"] < d["plate"]["e5_floor"])
    cb = R["cb"]
    p["P19 the conservative bound comes from held geometry at the coefficients' conservative ends, under W4's low case, and the reconciliation ends at it"] = (
        abs(cb["recon"][0][1] - T["w4_open"][0]) < 1e-9 and abs(cb["recon"][-1][1] - cb["E5"]["open"]["g"]) < 1e-6
        and cb["E5"]["open"]["g"] < cb["E5"]["open_opt"]["g"] < T["w4_open"][0] and cb["E3-O"]["open"]["g"] < cb["E3-O"]["open_opt"]["g"])
    p["P20 U-02's class follows from the bound: the lines over the bound with a 50 m/s inside flow, E3-O's gap positive with every session measure, so T-H1 decides"] = (
        cb["cap"]["E5"] < cb["lines"]["E5"] and cb["cap"]["E3-O"] < cb["lines"]["E3-O"] and cb["gap_w"]["E3-O"] > 0 and cb["gap_w"]["E5"] <= 0
        and cb["klass"] == "DECIDES")
    hr = R["hr"]
    p["P21 heat rejection on the bound: no approach reaches the profile at +40 C (the best short by a positive margin) nor charging on the design day; U-02 stays a closure condition"] = (
        not hr["reaches"] and not hr["charges"] and hr["short_w"] > 0 and hr["short_g"] > 0 and all(x > 0 for x in hr["short_ch"])
        and hr["rows"][-1]["use"]["g"] == max(r_["use"]["g"] for r_ in hr["rows"]) and hr["q_idle"] < hr["q_max_best"] < hr["q_prof"])
    rc = R["rc"]
    p["P22 the reconciliation: 1.509 W/K at 42.4 W is 1.447 W/K after its uncertainty, K1's screen (Table 5's +55 C, not a line) at LO-01a's floor with the ballasts (1.806 W/K), the room reading conservative, every heater spread summing to its setting, A k on the case's own films under steel's and the need, the need between the bound's cap and W4's high case"] = (
        abs(rc["check509"]["after"] - rc["check509"]["target"]) < 1e-6 and abs(rc["conds"][0][7] - T["g_floor_ballast"]) < 1e-9
        and all(x[3] >= 1.0 for row in rc["trans"] for x in row[1:]) and rc["conds"][10][7] > R["cb"]["cap"]["E5"]
        and rc["lim"]["no505"] and abs(rc["q"]["prof"]["loads"] + rc["q"]["prof"]["conv"] + rc["q"]["prof"]["i2r"] - rc["q"]["prof"]["total"]) < 1e-9
        and abs(rc["rit"]["rows"][0][4] - rc["trans"][0][1][2]) < 1e-6 and rc["rit"]["rows"][0][4] < rc["rit"]["steel_g"] < rc["conds"][0][7]
        and rc["rit"]["cap"][0] < rc["conds"][0][7] < rc["rit"]["w4"][1]
        and all(abs(sum(v_ for _k, v_ in s_["spread"]) - s_["heaters"]) < 1e-6 for s_ in rc["q"]["settings"]))
    pm, br = R["pm"], R["br"]
    md = {m_["id"]: m_ for m_ in pm["modes"]}
    p["P23 B3: no absolute rating is a line; the SGP41's sensing is Table 4's (as ruled), C moves the heat stage's line to the cells' hot stop, and every mode's governing line is its tightest local line"] = (
        all(all("ABSOLUTE" not in x["cat"] for x in m_["by"][o]["lines"]) for m_ in pm["modes"] for o in OPTIONS)
        and all(m_["by"][o]["gov"]["g"] == max(x["g"] for x in m_["by"][o]["lines"]) for m_ in pm["modes"] for o in OPTIONS)
        and all(md[i_]["by"]["as ruled"]["gov"]["short"] == "the SGP41's Table 4" for i_ in ("M1", "M2", "M3", "M4"))
        and all("hot stop H1" in md[i_]["by"]["C"]["gov"]["short"] for i_ in ("M1", "M2", "M3", "M4"))
        and abs(md["M2"]["by"]["as ruled"]["gov"]["g"] - R["rc"]["conds"][1][7]) < 1e-9 and abs(md["M5"]["by"]["C"]["gov"]["g"] - R["rc"]["conds"][5][7]) < 1e-9)
    cbal = R["T"]["chg_prof"]
    p["P24 B4: the charging heat is input less stored less exported, the reviewer's 50.044 W on the model's boundary, and K7 and K8 carry it with the ballasts"] = (
        abs(cbal["p_in"] - cbal["stored"] - cbal["exported"] - cbal["heat"]) < 1e-9 and abs(cbal["heat"] - 50.04367) < 5e-5
        and abs(R["hr"]["q_chg"] - cbal["heat"] - R["T"]["qb"]) < 1e-12 and abs(R["rc"]["conds"][6][2] - R["hr"]["q_chg"]) < 1e-12
        and abs(md["M8"]["Q"] - R["hr"]["q_chg"]) < 1e-9)
    p["P25 B7: the battery-only run reaches C1 before its energy ends on the bound at C 8 kJ/K, the reviewer's constant-G figures reproduced, no hot stop, 2.52 h energy-only"] = (
        br["runs"][0]["t_c1"] is not None and br["runs"][0]["t_c1"] < br["t_energy"] and abs(br["rev"][0][1] - 2.063) < 5e-3
        and abs(br["rev"][1][1] - 2.151) < 5e-3 and not any(r_["hot_stop"] for r_ in br["runs"]) and abs(br["t_energy"] - br["h_energy"]) < 5e-3)
    cp = R["cap"]
    cls3 = sorted(set((e["mode"], e["line"]["short"]) for e in cp["lines"] if e["cls"] == "iii"))
    p["P26 the addendum: every line classed against the outside capacity with a zero inside resistance (bare and with the route); class (iii) is E3-L lid closed as ruled and the e-paper at E3-O and E5, no other"] = (
        cls3 == [("M3", "the SGP41's Table 4"), ("M4", "the SGP41's Table 4"), ("M6", "the EPAPER's +60 C"), ("M7", "the EPAPER's +60 C")]
        and all(e["route"][0] >= e["bare"][0] - 1e-9 and e["route"][1] >= e["bare"][1] - 1e-9 for e in cp["lines"])
        and cp["check9"][0] > R["cb"]["cap"]["E3-O"] and cp["check9"][2] > R["cb"]["cap"]["E5"]
        and all(e["short_g"] > 0 for e in cp["lines"] if e["cls"] == "iii"))
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


def _counts(rows):
    cnt = {}
    for r_ in rows:
        for mg in MARGINS:
            cnt[(mg, r_["verdict"][mg])] = cnt.get((mg, r_["verdict"][mg]), 0) + 1
    return "; ".join("%s: %s" % (mg, ", ".join("%s %d" % (v_, cnt[(m_, v_)]) for (m_, v_) in sorted(cnt) if m_ == mg)) for mg in MARGINS)


def _parts_lines(w, S, parts):
    for pr in parts:
        w("   %-9s %s%s" % (pr["k"], pr["label"], "; device set (CHO-001)" if pr["dev"] else ""))
        for mg in MARGINS:
            key, lim = pr["key"][mg], pr["lim"][mg]
            src = "" if key is None else "%s %s \"%s\"" % (S[key]["doc"].split("/")[-1], S[key]["where"], S[key]["quote"][:60])
            lo, hi = pr["temps"][mg]
            g = pr["gap"][mg]
            if g[0] is None:
                gap = ""
            elif g[1] > 1e-9:
                gap = ", over by %s K" % _rng(max(g[0], 0.0), g[1])
            else:
                gap = ", %.2f K inside" % max(0.0, -g[1])
            w("     %-4s %-4s limit %-6s %s; %s; MAKER: %s" % (mg, pr["state"][mg], "none" if lim is None else "+%.0f" % lim,
                                                     pr["cat"][mg] or "no category", pr["basis"][mg], src))
            ak = pr["abs_key"][mg]
            w("          local %s C (%s), %s%s%s" % (_rng(lo, hi), "MODELED" if pr["where"] == "inside" else "INFERRED", pr["verdict"][mg], gap,
                                               "" if ak is None else "; %s +%.0f C (%s %s), an exclusion screen only" % (
                                                   CAT[ak], pr["abs"][mg], S[ak]["doc"].split("/")[-1], S[ak]["where"])))


def render(R):
    S, T, A, ap = R["S"], R["T"], R["A"], R["ap"]
    out = []
    w = out.append
    from math import exp as math_exp
    C_ = {"hin_still": tuple(R["w4"]["hin_still"]), "a_side": tuple(R["w4"]["a_side"]), "prof_pb": R["dep"]["fan_power"][0]["plan"]["state"]}
    import math
    math_log100 = math.log(100.0)

    def para(text_, first="   ", rest="   "):
        for ln in textwrap.wrap(text_, width=128, initial_indent=first, subsequent_indent=rest, break_on_hyphens=False):
            w(ln)
    a, c, tr, sg, rg = ap["a"], ap["c"], ap["c"]["trip"], ap["sgp"], ap["reg"]
    w("l4e12_thermal.py: layer 4 task L4-E12 (MESHSAT-1478 under MESHSAT-1357). The kit's electronics against the inside air at")
    w("D-02a's +55 C operating margin (E3-O) and E5's +60 C dwell in the sealed Peli 1450. Prototype design, desk arithmetic: nothing")
    w("is bought, built, powered or measured. Classes: MAKER, MODELED, INFERRED, ASSUMPTION, CONDITIONAL. Revised after the focused")
    w("check astra-check-l4e12-1 and the targeted recheck astra-check-l4e12-2 (the record's section 12 maps each item to its change);")
    w("section 8 is the dependency round of 2 October 2026 on U-02 (the record's section 13), section 9 the conservative bound (section 14),")
    w("section 10 the heat-rejection question (section 15), section 11 the thermal reconciliation (section 16), section 12 the fix round of")
    w("the Layer 4 review (B3, B4, B7; section 17).")
    w("")
    w("0 Reproductions and inputs")
    w("0a pwr_budget.py re-run in a child: pwr_budget.out and pwr_budget.json byte for byte: %s" % ("yes" if R["r0a"] else "NO"))
    w("0b pwr_red2.py re-run in a child: pwr_red2.out byte for byte: %s" % ("yes" if R["r0b"] else "NO"))
    w("0c pwr_red2.py imported here prints pwr_red2.out byte for byte (its heat() and states are the record's): %s" % ("yes" if R["r0c"] else "NO"))
    w("0d grade_check.build() (it writes nothing): %d fitted lines, %d modules, %d lines no grade row covers; its own in-use bar %d C" % (
        R["gc"]["rows"], R["gc"]["mods"], R["gc"]["undeclared"], R["gc"]["inside_bar"]))
    w("0e %d inputs pinned by sha256 (the list ends this output)" % len(R["pins"]))
    para("0f The rating categories (1j): the heading each of %d statements is printed under read before it on its page, with no competing "
         "heading between (%s): yes; the BME688's +-0.5 C read in Table 10's Typ column (%s): yes" % (
             len(R["heads"]), ", ".join(R["heads"]), S["bme_t_typ"]["where"]), first="")
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
    para("1i What it requires (INFERRED from 1a to 1h): at both margins the kit is to survive and recover; operation to specification is "
         "required only inside the envelope. E3-O runs four hours at +55 C deployed with the monitor and radios on; the one control action its "
         "arrangement records is C1's inside-air shedding of modules (1e), which takes the kit to the heat stage (1f). Nothing else may turn a "
         "radio off in E3-O: the radios C1 leaves on (Iridium, the LoRa mesh, APRS, both E72, GNSS) stay on for the four hours, and a further "
         "shedding would change E3-O's configuration (no authority: withdrawn from the first revision). E5 requires logging, not the radios "
         "(1d), so a step of the kit's controls that turns radios off may act in E5 and must not act in E3-O. The SGP41 is neither the monitor "
         "nor a radio and E3-O's row does not name it; its own protective shutdown is inside E3-O's stated configuration (SESSION reading, "
         "named for TEST-PLAN's owner). The lid-closed mode and EMCON (\"%s\") change the configuration and are not used. E3-O is taken to start "
         "from a kit stabilised at the chamber's +55 C, as L4-E10 took it; started straight from E3-S's +71 C soak, the radios would be past +70 C "
         "at power-on (a sequence item for TEST-PLAN's owner)." % A["emcon"], first="")
    para("1j Which limits apply (the corrected rule, SESSION). Every judged limit names its category, read where the maker prints it (0f). A "
         "powered part is judged on its recommended or operating range (the range a sheet's electrical characteristics hold over counts as "
         "operating), whether it must work in the exposure (the CM5, the logging chain, the fans, the radios in E3-O) or is merely powered. An "
         "absolute rating (Absolute Maximum Ratings, limiting values, a junction-and-storage row) is a stress rating only (PCM2912A %s: \"%s\") and "
         "clears a part only as an exclusion screen: past its supporting range (or with none held) and under its absolute rating a part is "
         "INCONCLUSIVE, operation or survival not stated, unless its maker states recovery (Quectel RM520N %s: \"%s\"). An unpowered part: its "
         "storage range where the maker states one outside its absolute table, else a range it may operate in (INFERRED to cover it unpowered); "
         "an absolute storage row is a screen, and a duration the maker does not state stays open. The SGP41 (section 2.3, %s): its gas "
         "sensing specifications hold only when it is stored and operated under Table 4's recommended conditions, operation %.0f to +%.0f C and "
         "storage %.0f to %.0f C; Table 5's %.0f to +%.0f C operating and %.0f to +%.0f C short-term storage are absolute (%s). A part through the "
         "plate or the wall: the plate to the inside air." % (
             S["pcm_absnote"]["where"], S["pcm_absnote"]["full"], S["rm_recover"]["where"], S["rm_recover"]["full"], S["sgp_guar"]["where"],
             S["sgp_rec"]["v"][0], S["sgp_rec"]["v"][1], S["sgp_rec_st"]["v"][0], S["sgp_rec_st"]["v"][1],
             S["sgp_op"]["v"][0], S["sgp_op"]["v"][1], S["sgp_st"]["v"][0], S["sgp_st"]["v"][1], S["sgp_op"]["where"]), first="")
    w("")
    w("2 The thermal state at the margins (MODELED unless marked)")
    w("2a The heat stage after BANK-R1 (PS-SURV-R) on shore, plan: %.3f W at the pack, %.3f W into the case with the front end's and" % (T["q_hs_pack"], T["q_hs"]))
    w("   charger's loss on the loads; as board B is generated (PS-SURV) %.3f W. HIGH: %.3f W (not covered, as L4-E10 and LO-01a)." % (T["q_gen"], T["q_hs_hi"]))
    w("2b T-H1's floor (LO-01a): the inside air at or under the SGP41's +%.0f C (MAKER, %s Table 5, an absolute rating; LO-01a's" % (
        T["sgp55"], S["sgp_op"]["where"]))
    w("   criterion reproduced as stated) at +%.0f C on shore: %.4f W/K; by the corrected rule the bay air at Table 4's +%.0f C needs" % (
        T["t_use"], T["g_floor"], S["sgp_rec"]["v"][1]))
    w("   %.3f W/K with the ballasts (a finding for LO-01a's owner and for E3-L's \"+55 C\" line; the record's downstream table);" % (
        (T["q_hs"] + T["qb"]) / (S["sgp_rec"]["v"][1] - T["t_use"])))
    w("   L4-E10's %.4f W/K, %.2f and %.2f C (read from %s) agree: %s (%.2f, %.2f C uncond.)" % (
        A["l4e10_floor"], A["l4e10_air"][0], A["l4e10_air"][1], L4E10_OUT.split("/")[-1], "yes" if T["agree_g"] and T["agree_air"] else "NO", *T["air_uncond"]))
    w("2c L4-E8's ballasts, %.2f W at the bound's worst corner (MODELED by L4-E8, read from %s): +%.3f K. The inside air" % (T["qb"], L4E8_OUT.split("/")[-1], T["ballast_k"]))
    w("   (mixed) at the floor:")
    w("   E3-O %.2f C, E5's dwell %.2f C (steady; a 4 h E3-O from a kit at +55 C reaches %.2f to %.2f C at 32.53's %.0f to %.0f kJ/K," % (
        T["air"]["E3-O"], T["air"]["E5"], T["e3o_4h"][1], T["e3o_4h"][0], T["kJ"][1], T["kJ"][0]))
    w("   so the steady air is the bound; E5's 6 h dwell reaches it). At HIGH heat E5's air would be %.1f C." % T["air_hi"])
    w("2d A charge running on shore (the pack outside, at room temperature, inside its window): +%.3f W, +%.2f K. E3-O states no" % (T["charge_extra"], T["charge_k"]))
    w("   charge state; the route below keeps E3-O as stated and counts no charge (TEST-PLAN's owner records the pack's state, 7).")
    w("2e Inside the envelope at the floor (+40 C, heat stage, ballasts): %.2f C, over the SGP41's +55 C line of E3-L (REQ-052);" % T["in_env"])
    w("   LO-01a's floor with the ballasts counted is %.4f W/K (a finding for L4-E9 and L4-E10, section 7)." % T["g_floor_ballast"])
    w("2f The plate and the walls (INFERRED from W4's film coefficients, inside %s, outside face %s, wall %s W/m2K, wall t/k %.3f):" % (
        "%g to %g" % tuple(R["w4"]["hin"]), "%g to %g" % tuple(R["w4"]["hof"]), "%g to %g" % tuple(R["w4"]["how"]), R["w4"]["tk"]))
    w("   the plate sits at the ambient plus %.3f to %.3f of the rise, a PP wall's inner face at %.3f to %.3f of it, the floor's" % (T["f_plate"] + T["f_wall"]))
    w("   inner face at %.3f to %.3f (outer film %g to %g W/m2K)." % (T["f_floor"] + tuple(R["w4"]["hfl"])))
    w("2g The enclosure (INFERRED, W4, a sensitivity estimate and not a model of the kit): lid open with fans %.2f (low case) to %.2f" % T["w4_open"])
    w("   W/K (high case); 32.53 gives %.1f to %.1f. With the inside film taken as infinite the outer films give %.2f W/K in the low" % (T["g_3253_open"] + (T["cap"][0],)))
    w("   case and %.2f W/K in the high case: a cap of the low case's coefficients and areas, not a universal bound. Low outer films" % T["cap"][1])
    w("   with W4's high inside film: %.2f W/K; high outer films with its low inside film: %.2f W/K. Lid closed with fans: W4 %.2f to" % (
        T["g_low_out_high_in"], T["g_high_out_low_in"], T["w4_closed"][0]))
    w("   %.2f W/K, 32.53 %.1f to %.1f W/K." % (T["w4_closed"][1], T["g_3253_closed"][0], T["g_3253_closed"][1]))
    w("2h The running module's cooler exhaust (MODELED): the representative 30 mm fan's %.1f CFM free-air (MAKER, Sunon %s) at %.0f %%" % (
        S["fan_cfm"]["v"][0], S["fan_cfm"]["where"], FLOW_SHARE * 100))
    w("   through the heatsink (ASSUMPTION), %.3f l/s: the CM5's 4.5 W and the fan's %.2f W lift the exhaust %.2f K over the mixed air in" % (T["vdot_l_s"], T["fan_w"], T["d_hs"]))
    w("   the heat stage, and the idle module's 2.0 W %.2f K in the hold. A part outside the exhaust sits at the mixed air." % T["d_hold"])
    w("2i The design as it stands (the heat stage at T-H1's floor, the ballasts on):")
    for mg in MARGINS:
        L = R["locs_now"][mg]
        w("   %-4s ambient %.1f C; mixed air %.2f C; in the exhaust %.2f C; plate %s C; PP wall's inner face %s C" % (
            mg, L["amb"], L["mixed"], L["plume"], _rng(*L["plate"]), _rng(*L["wall_in"])))
    w("")
    w("3 The feasibility screen of the design as it stands (the heat stage at T-H1's floor, the radios on at both margins), by 1j")
    w("3a The parts read one by one: per margin, its state (work: powered and required; on: powered; off), its limit by 1j with its")
    w("   category (MAKER, document and page) and its local bounds (inside, the mixed air .. the exhaust; face and wall, the plate ..")
    w("   the inside air). REACHED: a part required to work past its limit at the lower bound, or anything past its absolute rating;")
    w("   PLACEMENT: past it only at the upper bound; INCONCLUSIVE: past the supporting limit of a part not required to work (or no")
    w("   limit held) and under its absolute rating, the screen cleared and survival or operation not stated; NOT REACHED.")
    _parts_lines(w, S, R["parts_now"])
    w("3b Every fitted line on boards A to E (grade_check), every module and every line no grade row covers. Rating: the grade row's")
    w("   maker's range with its category (SESSION rule, read from the row's clause and quote: rec, recommended; ec, the range the")
    w("   electrical characteristics hold over; op, operating as printed; dist, a distributor's parametric figure; abs, an absolute")
    w("   rating: the clause names maximum ratings or limiting values, a junction-and-storage or power-dissipation row, a junction row")
    w("   whose table the quote does not name (the conservative reading), or a distributor's figure for a TI power FET, whose held")
    w("   sheets print it as the absolute junction-and-storage row; abs rows are exclusion screens: INCONCLUSIVE when cleared). Board")
    w("   D's TUSB2046I is judged on the held TI sheet's recommended TA (%s), its grade row's +115 C junction being its absolute row." % S["tusb2046_ta"]["where"])
    w("   Rise: the part's own over its local air (class named); local bounds with the rise. Board P and the cells are outside the")
    w("   chamber in E3-O and E5 (TEST-PLAN section 6): FEA-008's, not here. Lines read one by one carry 3a's verdict and category.")
    cc = {}
    for r_ in R["screen"]:
        if set(r_["verdict"].values()) <= {"NO PART", "OUT OF SCOPE", "NOT FITTED"}:
            continue
        sc = short_cat((r_.get("cat_l2") or {}).get("E5") or r_.get("cat"))
        cc[sc] = cc.get(sc, 0) + 1
    w("   categories of the screened lines: %s" % ", ".join("%s %d" % (k_, cc[k_]) for k_ in sorted(cc)))
    w("   %s" % _counts(R["screen"]))
    for r_ in sorted(R["screen"], key=lambda x: (x["verdict"]["E5"] != "REACHED", x["verdict"]["E5"] != "PLACEMENT", x["part"])):
        t3, t5 = r_.get("temps", {}).get("E3-O"), r_.get("temps", {}).get("E5")
        if "lim_l2" in r_:
            l5 = r_["lim_l2"]["E5"]
            rating = "none read" if l5 is None else "%s L2 %s" % (f1(l5), short_cat(r_["cat_l2"]["E5"]))
        else:
            rating = "none read" if r_["max"] is None else "%s %s %s" % (f1(r_["max"]), r_.get("kind") or "", short_cat(r_.get("cat")))
        rise = r_.get("rise", {}).get("E5", 0.0) if isinstance(r_.get("rise"), dict) else 0.0
        rcls = (r_.get("rise_cls", {}).get("E5") or "MAKER") if isinstance(r_.get("rise_cls"), dict) else "MAKER"
        tag = "level 2: %s" % r_["level2"] if "level2" in r_ else ("undeclared line" if r_.get("undeclared") else ("module" if r_.get("module") else ""))
        w("   %-34.34s | %-26.26s | %-14s | %-7s | +%5.1f K %-10.10s | E3-O %-11s %-12s | E5 %-11s %-12s | %s" % (
            r_["part"], _refs(r_["refs"]), rating, r_.get("where", r_.get("where_gs")), rise, rcls.split(" ")[0],
            "-" if t3 is None else _rng(*t3), r_["verdict"]["E3-O"], "-" if t5 is None else _rng(*t5), r_["verdict"]["E5"], tag))
    w("   NOT FITTED: the Bulgin PX0833 (CASE-MARGINS: \"%s\"); the sealed RJ45 is a MIL-DTL-38999 shell 15 class part." % A["px0833"])
    w("3c The junction figures (MODELED dissipation in the heat stage x MAKER thetaJA on its JEDEC board; local air the mixed air at E5):")
    seen = set()
    for (b, ref), d in sorted(R["diss_now"].items()):
        if d["part"] in seen:
            continue
        seen.add(d["part"])
        tj5 = R["locs_now"]["E5"]["mixed"] + d["p"] * d["th"]
        lim = ("%s %.0f C (%s)" % (d["rec_cat"], d["rec"], d["rec_key"])) if d["rec"] is not None else "its ambient rating (no recommended junction read)"
        absn = "" if d["abs"] is None else "; %s %.0f C (an exclusion screen)" % (d["abs_cat"].split(" (")[0], d["abs"])
        w("   %-48s %s %-5s %.3f W (%s) x %.1f C/W = +%.1f K; TJ %.1f C against %s%s" % (
            d["part"], b, ref, d["p"], d["p_src"], d["th"], d["p"] * d["th"], tj5, lim, absn))
    dc = R["decl"]
    w("3d FINDING, in the envelope as well (the generators' own declarations): board E's U13 is a TLV75533 in SOT-23-5 (DBV, %.1f C/W," % dc["th755"])
    w("   recommended junction +%.0f C, absolute +%.0f C, MAKER, TLV755P sheet, held back) on a rail declared at %.2f A typical and %.2f A" % (
        dc["rec755"], dc["tj755"], dc["e"][0], dc["e"][1]))
    w("   peak from 5.0 V: %.3f W, +%.1f K, past its recommended +%.0f C at any local air above %.1f C; the declared peak exceeds its %.0f mA" % (
        dc["e_decl_p"], dc["e_decl_p"] * dc["th755"], dc["rec755"], dc["rec755"] - dc["e_decl_p"] * dc["th755"], dc["iout"] * 1000))
    w("   output. Board C's U5 (the same part) is declared %.3f A typical and %.3f A peak, the peak past %.0f mA. Even at the model's plan" % (
        dc["c"][0], dc["c"][1], dc["iout"] * 1000))
    w("   load U13 passes its recommended junction at both margins (3c): the regulators are part of the route (5c).")
    w("")
    w("4 Three complete approaches for the parts that collide (the same margins, the same floor, the same ballasts, the plan heat)")
    w("   Common to all three (none can be done by the air, the physics of 4a): the SGP41's own shutdown at the margins and its")
    w("   in-envelope function (5d, the owner's question of 6); the MAIN, PI and TEST pushbuttons to a +85 C part; PDi's storage")
    w("   statement for the e-paper; board E's and board C's 3.3 V regulators (5c); the +70 C parts out of the running cooler's")
    w("   exhaust; the fans, the other lines with no range held and the lines cleared only by an absolute rating (7).")
    w("4a (a) THE HEAT PATH AND THE ENCLOSURE, no new mode: the heat stage at both margins, the radios on at both. Each part routed by")
    w("   the air needs (MODELED, E3-O / E5):")
    ga_all = dict(a["g"], **a["screen"])
    for k in sorted(ga_all, key=lambda k: -max(ga_all[k].values())):
        w("      %-9s %.3f / %.3f W/K%s" % (k, ga_all[k]["E3-O"], ga_all[k]["E5"], "  (its absolute rating's screen only: survival INCONCLUSIVE)" if k in a["screen"] else ""))
    w("   so the line is %.3f W/K (0 K margin), %.3f with 1 K and %.3f with 2 K; E3-O alone %.3f W/K. It lies over the low case's" % (
        a["gmax"], a["g_m"][0], a["g_m"][1], a["g_e3o"]))
    w("   outer-film cap (%.2f W/K) and under W4's high case (%.2f W/K finite inside film, %.2f infinite); 32.53 gives %.1f to %.1f." % (
        T["cap"][0], T["w4_open"][1], T["cap"][1], T["g_3253_open"][0], T["g_3253_open"][1]))
    w("   Not routed by the air (the air cannot be cooled below the ambient without a cooler, and a cooler in the sealed case returns")
    w("   its input to the air, L4-E10's corrected balance):")
    for k, why in a["open"]:
        w("      %-9s %s" % (k, why))
    w("   Coupling the +70 C modules to the plate instead: the plate at E5 is %s C at the floor; it needs %.3f W/K at the plate's" % (_rng(*a["plate_floor_e5"]), a["g_plate"]))
    w("   upper fraction, and the parts that cannot be coupled still need the line above. VERDICT: CONDITIONAL on T-H1 at or over")
    w("   %.3f W/K; not selected (0.55 W/K over (c)); it is what applies, with no hold, if T-H1 reads at or over it." % a["gmax"])
    w("4b (b) WIDER-RATED PARTS, the mode and the enclosure unchanged (the inside air %.2f C at E5, %.2f C in the exhaust):" % (
        R["locs_now"]["E5"]["mixed"], R["locs_now"]["E5"]["plume"]))
    for b_ in ap["b"]["rows"]:
        w("      %-9s %-17s %s%s" % (b_["k"], b_["who"], b_["note"], "" if b_["margin_e5"] is None else "; at E5 %.2f K inside the candidate's +%.0f C (MAKER)" % (b_["margin_e5"], b_["cand"])))
    w("   VERDICT: not selectable by the session (five device-set parts are the owner's, CHO-001, four with no candidate held).")
    w("4c (c) E3-O AS STATED, THE HOLD IN E5 ONLY: in E3-O the heat stage runs with every radio C1 leaves on (no hold); in E5 a step")
    w("   of the kit's controls beyond the heat stage holds the charge (as H1), idles the running module (no shutdown) and powers off")
    w("   board D (APRS), the PA rail, the RockBLOCK (RB_SW_EN), the LoRa module (LORA_ON), both E72 (ZB_ON) and the Geiger module")
    w("   (GEIGER_EN). H1's own actions, which it reuses (CONOPS 4c): \"%s\". Heat in E5 under it: %.3f W (MODELED," % (A["h1_actions"], T["q_m"]))
    w("   plan; %.3f W at the pack); as board B is generated, the 5G socket's supply dropped too, %.3f W. Each part routed by the" % (T["q_m_pack"], T["q_m_gen"]))
    w("   air needs (MODELED, E3-O with the heat stage / E5 with the hold):")
    gc_all = dict(c["g"], **c["g_screen"])
    for k in sorted(gc_all, key=lambda k: -max(gc_all[k].values())):
        w("      %-9s %.3f / %.3f W/K%s" % (k, gc_all[k]["E3-O"], gc_all[k]["E5"], "  (its absolute rating's screen only: survival INCONCLUSIVE)" if k in c["g_screen"] else ""))
    w("   so the line is G_c = %.3f W/K, set by E5 (E3-O alone %.3f W/K); %.3f with 1 K and %.3f with 2 K of margin; with the module" % (
        c["gmax"], c["g_e3o"], c["g_m"][0], c["g_m"][1]))
    w("   at its typical 4.5 W in the hold %.3f W/K; at HIGH heat %.3f W/K (not covered). Over the low case's cap by %.3f W/K, inside" % (
        c["g_cm45"], c["g_hi"], c["gmax"] - T["cap"][0]))
    w("   W4's range and under 32.53's: CONDITIONAL on T-H1. Not routed by the air:")
    for k, why in c["open"]:
        w("      %-9s %s" % (k, why))
    w("4d THE HOLD'S TRIGGER WINDOW at the line (it must not act in E3-O, and must act in E5 before the radios it turns off pass")
    w("   their +%.0f C): E3-O's steady mixed air with the radios on %.2f C; the mixed air by which E5 needs the hold %.2f C; window %.2f K." % (
        tr["need_by"], tr["e3o_mix"], tr["need_by"], tr["width"]))
    w("   Taken from it: the reference's error twice (board B's TMP117, +-%.1f C to 100 C, MAKER %s), E5's fastest rise %.1f K/h (the" % (
        tr["tol"], S["tmp117_acc"]["where"], tr["rate_k_h"]))
    w("   chamber's %d to %d C in %.0f h, Method 507.6 as L4-E10 transcribed it) times a %.0f s reading and response lag (ASSUMPTION):" % (
        R["A"]["e5"][3], R["A"]["e5"][4], R["A"]["m507"]["ramp_h"], READ_S + TAU_S))
    w("   %.6f K. What is left bounds the reference's offset to the air at the +70 C parts: at most +-%.6f K (INFERRED). The TMP117 is" % (
        tr["lag"], tr["e_allow"]))
    w("   a board sensor under the coolers: across the exhaust's 0 to %.2f K the window is %.2f K, so it DOES NOT EXIST unless the" % (
        R["T"]["d_hs"], tr["plume_window"]))
    w("   reference is placed in the mixed air near those parts or its offset is calibrated at T-H1 to +-%.6f K (CONDITIONAL); with the" % tr["e_allow"])
    w("   whole spread it would need %.3f W/K. The trigger then sits at the window's middle, %.2f C of mixed air plus the calibrated" % (
        tr["g_plume"], tr["trip_mid"]))
    w("   offset; restore 5 K under it after 30 minutes (PROVISIONAL). The window grows with the conductance: %s." % "; ".join(
        "%.2f K at %.3f W/K" % (wd, g_) for g_, wd in tr["widths"]))
    w("   Inside the envelope the air is %.2f C at the line, far under it. In E5 under the hold the mixed air settles at %.2f C." % (
        tr["env_mix"], tr["e5_hold_mix"]))
    fb = c["fallback"]
    w("4e If T-H1 reads under the line: the radio modules (RockBLOCK, board D) and the LimeSDR coupled to the plate hold E3-O at the")
    w("   plate's %s C at the floor (%.2f K inside +70 C at its upper fraction) and E5 under the hold at %s C (%.2f K) (INFERRED);" % (
        _rng(*fb["e3o_plate"]), fb["e3o_margin"], _rng(*fb["plate"]), fb["margin"]))
    w("   the SGP41 in the bay air (%.2f C in E5) is then past Table 5's +70 C short-term storage, an absolute rating (the owner's" % fb["mixed"])
    w("   question of 6 covers it).")
    w("4f Per colliding part, the three routes (CLOSES, CONDITIONAL, REJECTED, OUTSIDE AUTHORITY, INCONCLUSIVE):")
    for k, r_ in sorted(R["route"].items()):
        w("      %-9s (a) %-17s (b) %-17s (c) %-17s every route rejected: %s" % (k, r_["a"], r_["b"], r_["c"], "YES" if r_["forced"] else "no"))
    w("")
    w("5 The selection: (c), E3-O as stated and the hold in E5 only, at the line G_c = %.3f W/K, with the common items" % c["gmax"])
    w("5a The parts at the line (E3-O: the heat stage, radios on; E5: the hold), by 1j:")
    _parts_lines(w, S, c["parts"])
    w("5b Every fitted line, module and undeclared line at the line: %s" % _counts(c["screen"]))
    for r_ in sorted(c["screen"], key=lambda x: x["part"]):
        if any(v_ not in ("NOT REACHED", "OUT OF SCOPE", "NO PART", "NOT FITTED") for v_ in r_["verdict"].values()):
            w("   %-40.40s %-26.26s E3-O %-12s E5 %-12s%s" % (r_["part"], _refs(r_["refs"]), r_["verdict"]["E3-O"], r_["verdict"]["E5"],
                                                         "  (read in 5a)" if "level2" in r_ else ""))
    w("5c The two 3.3 V regulators at the line (recommended junction +%.0f C, MAKER; DBV %.1f C/W, DRV %.1f C/W, TLV755P p.4):" % (
        R["decl"]["rec755"], R["decl"]["th755"], R["decl"]["drv755"]))
    for name, row in rg["rows"].items():
        w("   %-38s %.3f W (%s): DBV E3-O %.1f C, E5 %.1f C; DRV E3-O %.1f C, E5 %.1f C" % (
            name, row["p"], row["src"], row["DBV"]["E3-O"], row["DBV"]["E5"], row["DRV"]["E3-O"], row["DRV"]["E5"]))
    w("   The DRV package holds U13 at the plan load and U5 at its declared typical; at U13's declared %.2f A neither package holds" % R["decl"]["e"][0])
    w("   (a DRV part takes at most %.3f A at E5's air): a buck, or the rail's load re-derived. Owed to boards E and C's owners." % rg["imax_drv"])
    wall, bay = sg["locs"][1], sg["locs"][0]
    para("5d THE SGP41 (board E U17). CHO-001 picks it for the battery bay (\"SGP41 in the battery bay (32.54)\"); REQ-042: \"%s\"; CFL-002's "
         "acceptance: \"%s\"." % (A["req042"], A["cfl002"]), first="")
    para("Its maker's conditions (1j): its gas specifications hold only when it is stored at %.0f to %.0f C and operated at %.0f to +%.0f C "
         "(section 2.3 and Table 4, %s), and \"%s\" (%s); Table 5's %.0f to +%.0f C operating and %.0f to +%.0f C short-term storage are absolute (%s)." % (
             sg["stor_rec"][0], sg["stor_rec"][1], S["sgp_rec"]["v"][0], sg["rec"], S["sgp_rec"]["where"], S["sgp_prolonged"]["quote"],
             S["sgp_prolonged"]["where"], S["sgp_op"]["v"][0], sg["abs"], S["sgp_st"]["v"][0], sg["stor_lim"], S["sgp_op"]["where"]))
    para("The reference: a TMP117 on the SGP41's carrier, +-%.2f C maximum from -40 to 70 C (MAKER, TMP117 %s); the BME688's +-0.5 C sits in Table "
         "10's Typ column (%s), not a bound, and is not used. The gradient to the SGP41 at most %.1f K with its own heating (ASSUMPTION, a placement rule "
         "measured at the bench); the lag %.6f K (E5's %.1f K/h, the fastest rise the record carries, times a %.0f s reading and response, "
         "ASSUMPTION)." % (sg["err"], S["tmp117_acc70"]["where"], S["bme_t_typ"]["where"], sg["grad"], sg["lag"], tr["rate_k_h"], READ_S + TAU_S))
    para("Power off at a reading of %.0f - %.2f - %.1f - %.6f = %.6f C, set at %.1f C (rounded down): the SGP41 is at most %.6f C when switched "
         "off, %.6f K under Table 5's +%.0f C. Power on and use of its output at a reading at or under %.0f - %.2f - %.1f - %.6f = %.6f C, set at "
         "%.1f C: at most %.6f C while its output is used. Between the two it stays powered, its output logged as outside Table 4 and not used "
         "for REQ-042; off at every start until the reading is at or under %.1f C." % (
             sg["abs"], sg["err"], sg["grad"], sg["lag"], sg["t_off_x"], sg["t_off"], sg["off_at"], sg["abs"] - sg["off_at"], sg["abs"],
             sg["rec"], sg["err"], sg["grad"], sg["lag"], sg["t_on_x"], sg["t_on"], sg["on_at"], sg["t_on"]))
    para("In the envelope (+%.0f C) its channel works only where the reference reads at or under %.1f C in every state, with %.1f K kept for a "
         "bounded restart: the location's own temperature at or under %.2f C. The binding state is the heat stage, %.3f W with the ballasts, lid "
         "open or closed (E3-L runs it at +40 C lid closed); C1 holds the other states' air at its +%.0f C on board B's TMP117 plus %.1f C and the "
         "lag, %.3f C. The locations that still sample the bay air (fraction of the air's rise from W4's films, INFERRED; local temperatures "
         "MODELED at +40 C):" % (T["t_use"], sg["t_on"], sg["m"], sg["loc_max"], sg["q_env"], sg["c1_trig"], tr["tol"], sg["c1_cap"]))
    w("      %-50s %-12s %-10s %-14s %-22s %s" % ("location", "fraction", "needs", "lid open, line", "lid closed, 32.53 2.0/1.5", "C1-held"))
    for lc in sg["locs"]:
        w("      %-50s %-12s %-10s %-14s %-22s %s" % (lc["name"], "%.3f-%.3f" % lc["f"], "%.3f W/K" % lc["g_need"], "%.2f C" % lc["open_line"],
                                                    "%.2f / %.2f C" % (lc["closed"][1], lc["closed"][0]), "%.2f C" % lc["c1"]))
    para("The coolest is the east wall's inner skin in the pack pocket (the pack keeps %s mm to that wall at the worst, CASE-MARGINS M4b; a carrier bonded to the "
         "skin, the SGP41 sampling the bay air through a diffusion port whose response is owed to the bench). It needs %.3f W/K with the lid open, "
         "inside W4's %.2f and under 32.53's %.1f; and the same %.3f W/K with the lid closed, over 32.53's %.1f to %.1f and over W4's high case %.2f: "
         "NOT HELD with the lid closed on any conductance the record carries. Where it holds: the C1-held states %.2f C (%.2f K to spare); a warm "
         "start from the envelope's +%.0f C storage (powered at once); recovery from E3-O's end (%.2f C at the skin at %.3f W/K) to a restart in "
         "%.2f to %.2f h at +40 C (32.53's %.0f to %.0f kJ/K)." % (
             A["pack_wall_mm"], wall["g_need"], T["w4_open"][1], T["g_3253_open"][0], wall["g_need"], T["g_3253_closed"][0], T["g_3253_closed"][1],
             T["w4_closed"][1], wall["c1"], sg["loc_max"] - wall["c1"], sg["warm"], sg["e3o_loc"], wall["g_need"], sg["rec_h"][0], sg["rec_h"][1],
             T["kJ"][0], T["kJ"][1]))
    para("Storage in the envelope: %.0f to +%.0f C for three months (%.0f to +%.0f C for a year, pcb_envelope.yaml) against Table 4's %.0f to %.0f C "
         "storage: an unpowered kit's inside sits at the ambient, so no location changes it." % (
             sg["st_env"][0], sg["st_env"][1], sg["st_env_1y"][0], sg["st_env_1y"][1], sg["stor_rec"][0], sg["stor_rec"][1]))
    para("At the margins it is off (E3-O starts from a kit at +55 C, so it is never powered there; in E5 it is off from %.1f C). At the line, in "
         "the bay air %.2f C (E3-O) and %.2f C (E5), at the skin %.2f and %.2f C, under Table 5's +%.0f C short-term storage, an absolute rating: "
         "INCONCLUSIVE, Sensirion's duration and recovery owed (drafted); in a cooler's exhaust it would pass it (%.2f C in E5), so it stays out of "
         "it. A supply switch and a bus of its own keep a live pin from feeding it (record, section 6)." % (
             sg["t_off"], sg["marg"]["E3-O"]["bay"], sg["marg"]["E5"]["bay"], sg["marg"]["E3-O"]["skin"], sg["marg"]["E5"]["skin"], sg["stor_lim"],
             sg["marg"]["E5"]["plume"]))
    para("RESULT: no location holds the SGP41 inside its maker's conditions in the envelope: not with the lid closed at the hot end (no "
         "conductance the record carries reaches %.3f W/K) and not in storage. CHO-001 binds the part: the owner's question (6b)." % wall["g_need"])
    para("5e What stays CONDITIONAL: T-H1 lid open with fans at or over %.3f W/K; the hold's reference calibrated to +-%.6f K or placed in the mixed "
         "air; the SGP41's shutdown at the margins (a TMP117 on its carrier within %.1f K, its switch and bus, Sensirion's duration) and, inside the "
         "envelope, the owner's answer (6b); the pushbuttons' pick; PDi's statement; the regulators; the +70 C parts out of the exhaust; the fans' "
         "rating, the other lines with no range held and the lines cleared only by an absolute rating (7d)." % (c["gmax"], tr["e_allow"], sg["grad"]),
         first="", rest="   ")
    w("")
    w("6 The owner-question test, after the engineering routes of 4 and 5 are assessed")
    w("6a At the margins, a part with every route rejected or outside authority on held evidence: %s." % (", ".join(R["forced_margin"]) or "none"))
    para("6b Inside the envelope: the SGP41 (5d), %s. The conflict is CFL-002's: CHO-001's SGP41 in the battery bay against REQ-042's VOC "
         "channel under D-02a's \"operate to specification inside the envelope\". The options:" % ("RAISED" if R["sgp_forced"] else "not raised"),
         first="")
    para("A  a BME688-class gas sensor in the bay in its place (Bosch: gas sensing %.0f to +%.0f C, %s, \"%s\"; its IAQ figures \"%s\", %s; "
         "storage %.0f to +%.0f C, an absolute rating, %s): powered with no shutdown across the envelope and both margins (bay air %.2f C at +40 C, "
         "%.2f and %.2f C at the line); REQ-042's VOC level set from the BME688's own baseline instead of \"%s\" (its acceptance restated); its "
         "performance over +40 C and after storage owed to Bosch or the bench; a second BME688 takes I2C 0x77 on board E, which the deferred "
         "outside pod's BME688 then cannot share." % (
             S["bme_gas"]["v"][0], S["bme_gas"]["v"][1], S["bme_gas"]["where"], S["bme_gas_note"]["quote"], S["bme_iaq_test"]["quote"],
             S["bme_iaq_test"]["where"], S["bme_st"]["v"][0], S["bme_st"]["v"][1], S["bme_st"]["where"], sg["bme"]["env"], sg["bme"]["e3o"],
             sg["bme"]["e5"], A["req042_voc"]), first="   ", rest="      ")
    para("B  the VOC channel dropped: REQ-042 restated to water on the floor and hydrogen (S-49's part); CHO-001's line and CFL-002 restated; U17 "
         "and its switch off board E.", first="   ", rest="      ")
    para("C  the SGP41 kept, its channel reported as not covered (REQ-042: \"%s\") while its reference reads over %.1f C (on the east wall's "
         "skin: lid closed above about +%.2f to +%.2f C ambient at 32.53's %.1f to %.1f W/K, lid open above about +%.2f C at the line) and after "
         "storage outside %.0f to %.0f C until Sensirion states otherwise: a restriction of the VOC channel inside the envelope, which D-02a does "
         "not grant today." % (A["req042_range"], sg["t_on"], sg["stop_closed"][0], sg["stop_closed"][1], T["g_3253_closed"][0],
                               T["g_3253_closed"][1], sg["stop_open"], sg["stor_rec"][0], sg["stor_rec"][1]), first="   ", rest="      ")
    para("The session's recommendation: A, the one option that keeps a powered VOC channel across the envelope and the margins with a part the kit "
         "already carries. The radios' route (5) does not depend on the answer.")
    para("6c Escalation is not limited to 6b. If T-H1 reads under %.3f W/K lid open, E5 fails for the +70 C class unless the plate coupling of 4e "
         "holds them (at %.3f W/K E3-O's mixed air is %.3f C, under +70 C, while E5's under the hold is %.3f C, over it); under %.3f W/K E3-O "
         "fails as well. Each case is assessed against the routes then left (the plate coupling's evidence, wider-rated parts) before any "
         "question; what would then go to the owner is a device-set re-pick (CHO-001) or a stated deviation of E3-O's configuration." % (
             c["gmax"], R["g2"]["g"], R["g2"]["e3o"], R["g2"]["e5"], c["g_e3o"]), first="")
    w("")
    w("7 Downstream (the record's section 9 carries each item's owner by layer and its acceptance)")
    w("7a T-H1 (prototype bench; Layer 7 designs for it): lid open with fans at or over %.3f W/K (E5 with the hold); %.3f W/K with no" % (c["gmax"], a["gmax"]))
    w("   hold; E3-O alone %.3f W/K (LO-01a's own floor %.4f W/K, %.4f W/K with L4-E8's ballasts, 2e); lid closed, the reading that" % (
        c["g_e3o"], T["g_floor"], T["g_floor_ballast"]))
    w("   decides option C's restriction (6b) and E3-L's inside air.")
    w("7b The hold (firmware owner, CONOPS 4 and HW-FW-CONTRACT's integrators, TEST-PLAN's owner); enables read in the generators:")
    for k_, v_ in sorted(A["enables"].items()):
        w("      %-13s %s" % (k_, v_))
    w("7c The lines with no range held, as evidence obligations:")
    for name, cls, owner, what in UNRATED:
        w("      %-38s %-12s %-28s %s" % (name, cls, owner, what))
    ab = [(min(r_["screen_k"].values()), r_["part"]) for r_ in c["screen"] if r_.get("screen_k")]
    para("7d The lines cleared only by an absolute rating (INCONCLUSIVE at the line, the exclusion screen cleared): %d; the least clearance "
         "%.1f K (%s). Each owes a maker's statement supporting operation (a recommended range, or the range its electrical characteristics hold "
         "over) or the parts discipline's derating rule (Layer 6): %s." % (len(ab), min(ab)[0], min(ab)[1], ", ".join(sorted(set(p_ for _k, p_ in ab)))),
         first="")
    w("")
    d = R["dep"]
    rw = d["rows"]
    w("8 U-02 IN DEPTH (the dependency round of 2 October 2026: the owner's question on the 2.159 W/K line, its configuration, the")
    w("  fans' power, T-H1, and what a failed reading changes)")
    para("8a THE BASIS OF THE LINES. Each line is the heat into the sealed case divided by the room between the ambient and the limit of "
         "the parts the air must hold, G = Q / (T_limit - T_ambient) (the mixed air at the limit, 0 K of margin):", first="")
    for key, r_ in rw.items():
        w("   %-22s Q %.3f W (%.3f W + the ballasts %.2f W) / (%.0f - %.0f) K = %.3f W/K; dG/dQ %.4f W/K per W, dG/dT_limit %.4f W/K per K" % (
            key, r_["Q"], r_["q"], T["qb"], r_["lim"], r_["amb"], r_["G"], r_["dGdW"], r_["dGdK"]))
        w("   %-22s +-1 W: %.3f to %.3f W/K; the limit +-1 K (or the ambient -+1 K): %.3f to %.3f W/K" % ("", r_["w"][0], r_["w"][1], r_["k"][0], r_["k"][1]))
    h = d["hold"]
    para("E5's heat under the hold, built up (MODELED, pwr_budget.py and pwr_red2.py as reproduced in 0, plan): %.3f W at the load pins, %.3f W "
         "lost in the converters, %.3f W in the distribution (fuses, FETs, shunt, leads): %.3f W at the pack; on shore the front end's and "
         "the charger's loss on it adds %.3f W: %.3f W into the case; L4-E8's ballasts add %.2f W at the bound's worst corner (MODELED by "
         "L4-E8, %s, read): %.3f W. The ambient %.0f C is E5's dwell (Table 507.6-IX, %.0f to %.0f C, the dwell from 0200 to 0800, %.0f h, "
         "transcribed in %s). The limit +%.0f C is the class the hold leaves in the air at E5 (each at its limit by 1j):" % (
             h["p_load"], h["loss"], h["dist"], h["pack"], h["front"], h["case"], T["qb"], L4E8_OUT.split("/")[-1], rw["E5, the hold"]["Q"],
             rw["E5, the hold"]["amb"], A["m507"]["lo"], A["m507"]["hi"], A["m507"]["dwell_h"], M507.split("/")[-1], rw["E5, the hold"]["lim"]))
    w("      %s" % "; ".join("%s %s +%.0f C (%s)" % (k_, st_, lim_, cat_) for k_, st_, lim_, cat_ in d["setters"]))
    para("The loads the hold changes, heat stage -> hold at the load pins (W): %s; into the case %.3f -> %.3f W. The loads of E5's hold, "
         "largest first (W at the load pins / at the pack): %s." % (
             ", ".join("%s %.3f -> %.3f" % a_ for a_ in d["hold_action"]), T["q_hs"], T["q_m"],
             "; ".join("%s %.3f / %.3f" % (n_, p_, s_) for n_, p_, s_ in h["loads"])))
    para("E3-O's 1.806 W/K: the heat stage's %.3f W into the case with every radio C1 leaves on, plus the ballasts, over E5's same +70 C limit "
         "from E3-O's +55 C (TEST-PLAN E3-O); it equals LO-01a's floor with the ballasts (%.4f W/K) only because both rooms are 15 K. The "
         "2.709 W/K: the heat stage's heat in E5 with no hold. Classes: the heat MODELED (the model's figures carry their own tiers: S sheet, "
         "R representative, D declared, T placeholder); the ballasts MODELED by L4-E8; the ambient and the limit MAKER and TEST-PLAN as read; "
         "the line itself MODELED, and CONDITIONAL as a requirement on T-H1." % (T["q_hs"], T["g_floor_ballast"]))
    para("8b THE CONFIGURATION IT ASSUMES. Lid open, deployed, on shore (TEST-PLAN E3-O and E5); every conductance here is W4's lid-open "
         "fans-on value or a T-H1 reading in that state. The fans of 32.53 item 2 (REQ-043): three cooler fans, one per CM5 cooler on its "
         "slot's fan header, and two mixer fans under the plate on board E's sensor controller, their speed set from the inside climate "
         "reading. In both margins three run: %s (W at the load pins; slots 1 and 2 and their coolers are off in the heat stage and the "
         "hold). D-18 is OPEN: no fan is picked. The model carries representatives (Sunon, %s): the cooler fan MF30060V2, 30 mm, %.2f W, "
         "%.1f CFM (MF30060V1 %.2f W, %.1f CFM), not IP68; the mixers GF60151B9 to B6, \"%s\", %.2f to %.2f W, %.1f to %.1f CFM. No held "
         "sheet gives a fan's operating temperature: REQ-043's acceptance asks for \"%s\", and the fans are 7c's ARCHITECTURE "
         "line. T-H1's hardware list names Same Sky's CFM-6025BG68 for the mixers (%s)." % (
             ", ".join("%s %.2f" % x for x in d["fans_running"]["E5"]), "catalogue extract " + S["fan_cfm"]["where"] + " and " + S["mix_cfm_lo"]["where"],
             0.36, S["fan_cfm"]["v"][0], S["fan_v1"]["v"][0], S["fan_v1"]["v"][1], S["mix_ip68"]["full"], 0.39, 1.50, S["mix_cfm_lo"]["v"][0],
             S["mix_cfm_hi"]["v"][0], need(A["req043"], r"(a published operating range covering -20 C to the inside-air bar part_temps\.py computes from pcb_envelope\.yaml)", "REQ-043's range").group(1),
             RTA.split("/")[-1] + " 5.2"), first="")
    cf = d["conf"]
    para("The heat path under the no-vent ruling (32.53 item 1): the 3 mm aluminium plate (%.4f m2) and the PP walls (%.4f to %.4f m2) "
         "and floor (%.4f to %.4f m2) only. W4's split, lid open with the fans (W/K, the walls and floor together / the plate): low case "
         "%.3f / %.3f, high case %.3f / %.3f; lid closed %.3f / %.3f and %.3f / %.3f. The mixers stir the air under the plate across the "
         "boards and onto the plate and the walls: the inside film W4 takes as %g to %g W/m2K with them and %g to %g W/m2K without. The "
         "hold's reference: today %s (CONOPS 4c), a board sensor in the coolers' air; 4d requires it in the mixed air by the +70 C parts or "
         "calibrated to +-%.6f K." % (
             d["areas"]["face"], d["areas"]["side"][0], d["areas"]["side"][1], d["areas"]["floor"][0], d["areas"]["floor"][1],
             cf["low"]["open_fans"][1], cf["low"]["open_fans"][2], cf["high"]["open_fans"][1], cf["high"]["open_fans"][2],
             cf["low"]["closed_fans"][1], cf["low"]["closed_fans"][2], cf["high"]["closed_fans"][1], cf["high"]["closed_fans"][2],
             R["w4"]["hin"][0], R["w4"]["hin"][1], C_["hin_still"][0], C_["hin_still"][1], A["hold_ref"], tr["e_allow"]), first="   ")
    fo = d["fans_off"]
    para("If the fans stop (W4 lid open, fans off: %.2f to %.2f W/K; 32.53 says about %.1f W/K still): the hold's heat less the fans' own "
         "%.2f W (into the case) puts E5's mixed air at %.2f to %.2f C (it needs %.3f W/K to stay at +70 C) and E3-O's at %.2f to %.2f C: the +70 C class "
         "is past its limit on W4's still values. One mixer of two stopping lies between the two states (no model). Parts coupled to the plate "
         "(8e, F4) stay at the plate: with the still film's plate fraction %.3f to %.3f, at most %.2f C (E5) and %.2f C (E3-O). The cooler "
         "fan of slot 3 stopping leaves the module to its own throttling (CM5 4.4: it \"reduces its clock speed to keep the SoC temperature "
         "below %.0f C\"), which E3-O's pass line allows (\"CM5 throttling logged but no shutdown\"). The controls act on the measured air "
         "whatever the cause (C1, the hold); a stopped fan is seen by its tachometer only where the picked fan has one." % (
             fo["still"][0], fo["still"][1], fo["g_3253_still"], fo["fans_case_hold"], fo["e5_air"][0], fo["e5_air"][1], fo["g_needed_e5"],
             fo["e3o_air"][0], fo["e3o_air"][1], fo["f_still"][0], fo["f_still"][1], fo["e5_plate_max"], fo["e3o_plate_max"],
             S["cm5_soc"]["v"][0]), first="   ")
    para("8c THE FANS IN THE ENERGY BUDGET. They are counted, not left in the undocumented share: pwr_budget.py carries \"cooler fan slot "
         "1..3\" in every state where its slot runs and \"two mixer fans\" in every state, tier R (representatives, D-18 open; the mixers' "
         "PWM duty TBD); load_trace.out lists them in the profile (%s; its tiers S %.1f, R %.1f, D %.1f, T %.1f W of %.1f W); the replay "
         "carries that profile (\"PS-IDLE-SPEC %.1f W at the pack terminals over its %d loads\", %s), and L4-E9's endurance the same "
         "42.8 W (l4e9_power_path.out at aa897e38, not pinned here: that output quotes this record). The %.2f W with no document are %s, "
         "no fan among them. Their heat is inside the case and inside every heat figure of 8a. Per mode (MODELED, battery side, plan; "
         "low..high at the load pins):" % (
             "; ".join("%s %.2f W %s" % (nm, w_, t_) for w_, t_, nm in A["trace_fans"]), A["trace_tiers"]["S"], A["trace_tiers"]["R"],
             A["trace_tiers"]["D"], A["trace_tiers"]["T"], A["trace_total"][1], A["replay_profile"][0], A["replay_profile"][1],
             REPLAY.split("/")[-1], A["replay_undoc"][0], ", ".join("%s %.2f W" % (nm, w_) for w_, nm in A["replay_undoc"][1])), first="")
    for fr in d["fan_power"]:
        w("      %-28s %d fans: %.3f W at the pack of %.3f W (%.1f %%), %.1f Wh a day; at the loads %.2f .. %.2f .. %.2f W" % (
            fr["label"], fr["plan"]["n"], fr["plan"]["pack"], fr["plan"]["state"], 100.0 * fr["share"], fr["wh_day"],
            fr["lo"]["load"], fr["plan"]["load"], fr["hi"]["load"]))
    fs = d["fan_sens"]
    para("The picked fans' power moves both budgets: at the representatives' low and high figures E5's hold carries %.3f to %.3f W into the "
         "case and its line is %.3f to %.3f W/K (0.100 W/K per W); the profile at the fans' high figures is %.3f W against %.3f W, so a "
         "runtime falls to %.3f of its value (MODELED). Register row drafted for L4-E9's downstream register (its owner inserts it): "
         "\"R-new | EVIDENCE | The five fans' power (D-18, REQ-043): the picked fans' maker's figures at the duty the controls set replace "
         "pwr_budget.py's representative rows; E5's line moves 0.100 W/K per W into the case and the profile by the fans' battery-side "
         "watts | L4-E12 8c | Layer 6 components with D-18 | a held sheet; T-H1 logs the fans' drawn power\"." % (
             fs["q_lo"], fs["q_hi"], fs["g_lo"], fs["g_hi"], fs["prof_hi"], fs["prof"], fs["runtime_factor"]), first="   ")
    t1 = d["th1"]
    para("8d T-H1: WHO AND HOW. TEST-PLAN section 8's row: \"%s\"; \"%s\". Hardware (%s 5.2): the Peli 1450 with the 1450PF frame and a "
         "3 mm plate blank, stack heaters of %.1f ohm at %.1f V giving %.1f W each, %s, \"%s\". No electronics are needed. Who: the "
         "prototype bench, as Layer 9's physical verification, once the owner authorises it (READY-TO-ACT lists what is missing: \"%s\"); a "
         "laboratory only for a chamber run at E5's +60 C (the owner's spend). The draft procedure is T-H1-PROCEDURE-DRAFT.md beside this "
         "record." % (A["th1_row"], A["th1_who"], RTA.split("/")[-1], t1["heater"][0], t1["heater"][1], t1["heater"][2], A["rta_logger"],
                      A["rta_mixers"], A["rta_who"]), first="")
    para("Method: the dummy heaters spread as the model spreads E5's hold (W, plan): %s, plus the ballasts' %.2f W on board A; one "
         "heater's %.1f W puts the line's %.1f K rise on the air (two: %.1f K). Points: two powers (%.1f and %.1f W), lid open and closed, "
         "fans on and off: %d points. Steady state: the time constant C/G is %.2f to %.2f h (32.53's %.0f to %.0f kJ/K, the kit's mass, an "
         "upper bound for an empty case, over W4's lid-open %.2f to %.2f W/K); within 1 %% of the rise after %.1f to %.1f h a point, %.0f to "
         "%.0f h in all; a point ends when the mixed air drifts at most %.1f K/h over an hour (ASSUMPTION)." % (
             "; ".join("%s %.2f" % (k_, v_) for k_, v_ in sorted(d["hold"]["place"].items(), key=lambda x: -x[1])), T["qb"],
             t1["heater"][2], t1["rise_line"][0], t1["rise_line"][1], t1["powers"][0], t1["powers"][1], t1["points"], t1["taus"][0],
             t1["taus"][1], T["kJ"][0], T["kJ"][1], T["w4_open"][0], T["w4_open"][1], t1["t_ss"][0], t1["t_ss"][1], t1["total_h"][0],
             t1["total_h"][1], DRIFT_K_H), first="   ")
    para("Uncertainty (ASSUMPTION, standard, k = 1): each thermocouple +-%.1f K after an isothermal comparison, the mixed air's spread "
         "+-%.1f K, the ambient's drift +-%.1f K, the steady-state residual %.3f K (the drift times the line's %.2f h), so the rise +-%.3f K; "
         "the power +-%.1f %%, the leads +-%.1f %%. Expanded (k = 2): %.1f %% at a 10 K rise and %.1f %% at 20 K. PASS LINE: the measured "
         "conductance, lid open with the fans, less its expanded uncertainty, at or over %.3f W/K, so a reading of at least %.3f W/K at a "
         "10 K rise (%.3f W/K at 20 K). A room reading under-reads the margin: the outside films' radiation is %.2f W/m2K at the room's "
         "%.0f C and %.2f W/m2K at E5's %.0f C, so on W4's films the margin's conductance is %.2f to %.2f times the room's (INFERRED, a "
         "credit the pass line does not take)." % (
             TC_U_K, MIX_U_K, AMB_U_K, t1["u_ss"], t1["tau_line"], t1["u_dt"], 100 * P_U_REL, 100 * LEAD_U_REL,
             100 * t1["ub"][10.0]["U_rel"], 100 * t1["ub"][20.0]["U_rel"], c["gmax"], t1["ub"][10.0]["pass"], t1["ub"][20.0]["pass"],
             t1["h_room"], ROOM_C, t1["h_margin"], A["e5"][4], t1["rad"]["high"], t1["rad"]["low"]), first="   ")
    para("8e A FAILED READING AND THE FALLBACKS. Mixed air at a lid-open, fans-on reading G (MODELED; E3-O the heat stage, E5 the hold):",
         first="")
    for g_, a3, a5 in d["fail"]:
        w("      G %.3f W/K: E3-O %.2f C (%s), E5 %.2f C (%s)" % (g_, a3, "holds" if a3 <= 70.0 + 1e-9 else "past +70 C",
                                                             a5, "holds" if a5 <= 70.0 + 1e-9 else "past +70 C"))
    para("A reading in (%.3f, %.3f) W/K: E3-O holds as stated, E5 under the hold passes +70 C for the class of 8a. A reading under %.3f W/K: "
         "E3-O passes it too. The fallbacks inside the rulings (no vent, the Peli 1450 kept), each with what it buys:" % (
             c["g_e3o"], c["gmax"], c["g_e3o"]), first="   ")
    fn = d["fins"]
    para("F1 FINS ON THE PLATE (no penetration; bonded or machined; INFERRED from W4's films, k the effective area multiplier): G for "
         "(inside k, outside k) = %s in the low case and %s in the high case; outside fins alone saturate at the inside film (%.3f and %.3f "
         "W/K with an endless outside area). Applied to a reading through W4's split, outside fins of twice the area multiply it by %.3f to "
         "%.3f and fins of twice the area on both faces by %.3f to %.3f: a reading of %.3f W/K would read %.3f to %.3f W/K (both faces). "
         "T-H1's plate and wall readings give the split the reading actually has. Feasibility: CONDITIONAL on "
         "the face's free area (the monitor, the e-paper, the switches) and the lid's clearance (CASE-MARGINS M3); the session's (Layer 7)." % (
             ", ".join("(%g, %g) %.3f" % x for x in fn["low"]), ", ".join("(%g, %g) %.3f" % x for x in fn["high"]), fn["low_cap_out"],
             fn["high_cap_out"], fn["ratio"]["out2"][0], fn["ratio"]["out2"][1], fn["ratio"]["both2"][0], fn["ratio"]["both2"][1], c["g_e3o"],
             fn["applied"]["both2"][0], fn["applied"]["both2"][1]), first="   ", rest="      ")
    para("F2 CONDUCTION FROM THE HOT BOARDS TO THE PLATE: heat Q_c led into the plate leaves the air's balance by Q_c (1 - f), f the plate's "
         "fraction, so E5 at +70 C needs Q_c = (Q - 10 G) / (1 - f): %s (W at f %.3f / %.3f). Board B carries %.2f W of the hold's heat "
         "(the module, its switch, the supervisors, the hubs). Feasibility: CONDITIONAL on a pad path from those parts to the plate (Layer "
         "7); the session's." % ("; ".join("G %.3f: %.2f / %.2f" % (g_, a_, b_) for g_, a_, b_, _e in d["cond"]), T["f_plate"][1],
                                  T["f_plate"][0], d["hold"]["place"]["board B (slot 3, its switch, hubs, supervisors, the device rail)"]),
         first="   ", rest="      ")
    dp = d["deep"]
    para("F3 SHEDDING IN E5 (E5 requires logging only): the heat a reading allows, 10 G - %.2f W: %s. A deeper hold that keeps the logging "
         "(the module idle on its own storage, board E's controller and sensors, the fans, the panel for the SOS, the supervisors and hubs "
         "on the logging path) and turns off %s takes E5's heat to %.3f W and its line to %.3f W/K. The session's (E5's stated "
         "configuration); CONDITIONAL on a supply switch for each (none read for the switch chip: a Layer 8 item) and on the logging path." % (
             T["qb"], "; ".join("G %.3f: %.2f W" % x for x in dp["allow"]), ", ".join("%s %.3f W" % x for x in dp["shed"]), dp["q"], dp["line"]),
         first="   ", rest="      ")
    pl = d["plate"]
    para("F4 THE PLATE COUPLING (4e): the RockBLOCK, board D (SA868, PCM2912A, G6K) and the LimeSDR on pads to the plate sit at the plate, "
         "at most the ambient plus %.3f of the rise: E5 holds them to %.3f W/K and E3-O to %.3f W/K. The parts left in the mixed air then set "
         "the floor: the +80 C connectors (%s) in the exhaust need %.3f W/K in E5 and %.3f W/K in E3-O (%.3f out of the exhaust); the H5007NL, "
         "the ATP16 and the PXP4043/C take section 6's wider parts or statements. So F4 holds E5 down to %.3f W/K and E3-O down to %.3f W/K "
         "(%.3f with the connectors out of the exhaust); with F3, E5 down to %.3f W/K. With the fans stopped the coupled parts stay at most "
         "%.2f C (8b). Feasibility: the pads' own rise and their mechanical path (Layer 7); the session's." % (
             pl["f_hi"], pl["e5"][0], pl["e3o"][0], ", ".join(pl["conn80"]), pl["e5"][1], pl["e3o"][1], pl["e3o"][2], pl["e5_floor"],
             pl["e3o_floor"], pl["e3o_floor_out"], pl["e5_deep_floor"], fo["e5_plate_max"]), first="   ", rest="      ")
    para("THE BEST FALLBACK: F4, the plate coupling, with F3 in E5: no owner ruling, no change to E3-O. What needs the owner: a reading under "
         "E3-O's F4 floor (%.3f W/K, or %.3f W/K with the connectors out of the exhaust) leaves a deviation of E3-O's configuration (the "
         "hold in E3-O) or a device-set re-pick (CHO-001); the SGP41 is 6b's question already." % (pl["e3o_floor"], pl["e3o_floor_out"]),
         first="   ")
    w("")
    cb = R["cb"]
    geo, gmm = cb["geo"], A["geo_m"]
    w("9 THE CONSERVATIVE LOWER BOUND, AND U-02'S CLASS (the consolidation's question of 2 October 2026: does T-H1 confirm a design")
    w("  the evidence already supports, or decide whether it can work?)")
    para("9a THE MODEL. The inside air to the ambient through two paths in parallel, each solved for its heat at a stated air rise: the "
         "plate (the inside film, the 3 mm aluminium, the outside films; lid closed, the enclosed layer to the lid and the lid's shell) "
         "and the walls (the inside film, the PP shell, the outside films); the floor adiabatic (the case on its feet, %.2f mm over a "
         "support whose temperature no document gives). Held geometry (CASE-MARGINS, Peli's drawing and STEP as read there; W4's plate "
         "outline): the plate %.4f m2 (L = A/P %.4f m); the walls %.4f m2 inside (the perimeter %.2f x %.2f mm at mid-height, floor to the "
         "shoulder at %.2f mm) and %.4f m2 outside (the outer perimeter over the base's %.2f mm), %.2f mm thick; lid closed, the flat "
         "ceiling %.4f m2, the skirt %.4f m2, the layer %.1f mm (W4's %.1f to %.1f); the floor %.4f m2. Correlations (textbook, INFERRED): "
         "a plate facing up hot or down cold, Nu = 0.54 Ra^(1/4) (0.15 Ra^(1/3) over 1e7), L = A/P; a vertical wall, Churchill and Chu, "
         "Nu = {0.825 + 0.387 Ra^(1/6)/[1 + (0.492/Pr)^(9/16)]^(8/27)}^2; the enclosed layer, Hollands et al., Nu = 1 + 1.44[1 - "
         "1708/Ra]+ + [(Ra/5830)^(1/3) - 1]+; radiation eps F sigma (T1^2 + T2^2)(T1 + T2) to surroundings at the ambient; air by "
         "Sutherland's laws. Coefficients, the end the bound takes first: the plate's emissivity %.2f (%.2f to %.2f, anodised), the "
         "shell's %.2f (%.2f to %.2f, pigmented PP), the PP's conductivity %.2f W/mK (%.2f to %.2f), the plate's view past the open "
         "lid %.2f (%.2f to %.2f, ASSUMPTION); still air at the margin's ambient (a chamber's circulation not credited); inside, natural "
         "convection only: the fans' flow and the stack's radiation to the plate are credited at zero (no held document places or picks "
         "the fans), each shown below as a credit." % (
             gmm["feet"], geo["a_plate"], geo["l_plate"], geo["a_wall"], gmm["mid"][0] * 1000, gmm["mid"][1] * 1000, gmm["shoulder"] * 1000,
             geo["a_wall_out"], gmm["depth"] * 1000, gmm["t_wall"] * 1000, geo["a_lid_top"], geo["a_lid_skirt"], geo["gap"] * 1000,
             cb["gap"][0] * 1000, cb["gap"][1] * 1000, geo["a_floor"], EPS_PLATE[0], EPS_PLATE[0], EPS_PLATE[1], EPS_SHELL[0], EPS_SHELL[0],
             EPS_SHELL[1], K_PP[0], K_PP[0], K_PP[1], F_OPEN[0], F_OPEN[0], F_OPEN[1]), first="")
    w("9b THE BOUND (W/K; lid open with the fans, their flow credited at zero; MODELED on INFERRED coefficients):")
    for mg in ("E5", "E3-O"):
        r_ = cb[mg]
        w("   %-5s %.0f C, the air %.0f K up: lid open %.3f (the other coefficient ends %.3f), lid closed %.3f; plate fraction %.3f" % (
            mg, r_["amb"], r_["rise"], r_["open"]["g"], r_["open_opt"]["g"], r_["closed"]["g"], r_["open"]["f_plate"]))
        w("         credits: the fans' flow 0.2 / 0.5 / 1.0 m/s %s; the stack's radiation %.3f, with 0.5 m/s %.3f; the floor %.3f; all the" % (
            " / ".join("%.3f" % g_ for _v, g_ in r_["v"]), r_["rad"], r_["rad_v"], r_["floor"]))
        w("         favourable ends with 1.0 m/s %.3f; a 50 m/s inside flow (a film near 45 W/m2K, not a zero inside resistance: 12e) %.3f" % (r_["opt_all"], r_["cap"]))
    w("   The envelope's +40 C, the air 15 K up: lid open %.3f, lid closed %.3f (LO-01a's and E3-L's state; U-01's, not this record's)." % (
        cb["env_open"]["g"], cb["env_closed"]["g"]))
    fl_ = cb["films"]
    w("   The bound's films at E5 (W/m2K): inside, the plate %.2f and the walls %.2f; outside, the face %.2f and the walls %.2f." % (
        fl_["hin_plate"], fl_["hin_wall"], fl_["hout_face"], fl_["hout_wall"]))
    para("9c W4'S 1.22 W/K RECONCILED. The budget's 1.22 to 2.85 W/K (lid open, fans) and 1.06 to 2.49 W/K (lid closed) are W4's lumped "
         "estimate (records/w4/w4-scratch-thermal.py, pwr_budget.py's G): fixed films, inside %g to %g W/m2K for \"low-velocity forced "
         "flow from the mixer and cooler fans, plus internal radiation\", outside %g to %g (the face), %g to %g (the walls), %g to %g "
         "(the floor) at about 310 K with emissivities 0.85 to 0.9, the base's walls %.4f to %.4f m2, PP at %.3f m2K/W. It is a "
         "sensitivity estimate, not a lower bound: its low end already assumes the fans' film. One assumption at a time, W4's low case "
         "to the bound (E5):" % (R["w4"]["hin"][0], R["w4"]["hin"][1], R["w4"]["hof"][0], R["w4"]["hof"][1], R["w4"]["how"][0], R["w4"]["how"][1],
                                  R["w4"]["hfl"][0], R["w4"]["hfl"][1], C_["a_side"][0], C_["a_side"][1], R["w4"]["tk"]), first="")
    for lbl, g_ in cb["recon"]:
        w("      %-100s %.3f W/K" % (lbl, g_))
    para("The decisive term is the inside film: W4's low case takes 10 W/m2K with the fans; natural convection gives %.2f to %.2f W/m2K, "
         "and no held document gives the fans' flow at the inner faces." % (fl_["hin_wall"], fl_["hin_plate"]))
    para("9d AGAINST THE LINES AND THE FALLBACK. The lines (%.3f W/K in E5, %.3f W/K in E3-O) lie over the bound with a 50 m/s inside "
         "flow (%.3f and %.3f W/K; CORRECTED in 12e: that flow's film is near 45 W/m2K, not a zero inside resistance, and the outside "
         "capacity proper at these rises is %.3f and %.3f W/K on the conservative ends, so E3-O's line lies under it and E5's over it, "
         "both under it at the optimistic ends). Section 8's floors (E5 %.3f W/K with F4 "
         "and F3; E3-O %.3f, or %.3f with the connectors out of the exhaust) lie over the bound by %.3f and %.3f W/K. Where the air "
         "settles on the bound (MODELED, lid open, its own rise):" % (
             cb["lines"]["E5"], cb["lines"]["E3-O"], cb["cap"]["E5"], cb["cap"]["E3-O"], R["cap"]["check9"][2], R["cap"]["check9"][0],
             cb["floors"]["E5"]["section 8 (W4's plate fraction), F4 with F3"],
             cb["floors"]["E3-O"]["section 8 (W4's plate fraction), F4"], cb["floors"]["E3-O"]["section 8, F4, the connectors out of the exhaust"],
             cb["gap_s8"]["E5"], cb["gap_s8"]["E3-O"]), first="")
    for k_, o in cb["ops"].items():
        para("%s: the air %.2f C (%.3f W/K at %.1f K), the plate %.2f C; %s." % (
            k_, o["air"], o["g"], o["rise"], o["plate"], "; ".join("%s %.2f C, %s" % (lbl, t_, "inside" if t_ <= lim + 1e-9 else "PAST +%.0f C" % lim)
                                                                 for lbl, t_, lim in o["checks"])), first="      ", rest="         ")
    for k_, b in cb["bind"].items():
        para("%s, with every session measure (F4, F3 in E5, the +80 C connectors to +85 C parts, the HX magnetics, the wider buttons): "
             "the module's +85 C binds, needing %.3f W/K at its %.0f K; the bound gives %.3f W/K: %s. Credits no held evidence bounds: %s; a "
             "forced flow across the inner faces %s." % (
                 k_, b["need"], b["rise"], b["have"], ("clears by %.3f W/K" % -b["gap"]) if b["gap"] <= 0 else ("GAP %.3f W/K" % b["gap"]),
                 "; ".join("%s %.3f" % x for x in b["credits"]),
                 "is not needed" if b["v_need"] == 0.0 else ("of %.2f m/s alone would close it" % b["v_need"] if b["v_need"] else "cannot close it")),
             first="   ")
    para("9e U-02'S CLASS: T-H1 %s. On held geometry and conservative coefficients the sealed case does not hold E3-O as stated: with "
         "every measure inside the session's authority the module's intake reaches %.2f C against its +85 C (a gap of %.3f W/K); E5 holds "
         "with them (%.3f W/K to spare). What could close the gap: the fans' flow at the inner faces (%.2f m/s, Layer 7's mixer placement) "
         "or the stack's radiation and the floor's support (with both credited the bound reads %.3f W/K), all of which T-H1 measures; leading the module's "
         "heat into the plate, which competes with F4 for the plate's outside (%.3f W/K at the bound's face film) and needs a finned "
         "plate the face's layout has not been shown to carry (Layer 7, unbounded); a deeper hold in E3-O (a deviation of E3-O's "
         "configuration) or a device-set re-pick (CHO-001), both the owner's. U-02 stays a closure condition of L4-E9's gate." % (
             "DECIDES" if cb["klass"] == "DECIDES" else "CONFIRMS", cb["ops"]["E3-O, the heat stage"]["air"], cb["gap_w"]["E3-O"],
             -cb["gap_w"]["E5"], cb["bind"]["E3-O with F4"]["v_need"] or 0.0, cb["bind"]["E3-O with F4"]["credits"][-1][1],
             geo["a_plate"] * fl_["hout_face"]), first="")
    ex = cb["exp"]
    para("9f THE SMALLEST EXPERIMENT THAT RESOLVES IT: one point of T-H1, lid open, the fans running at full duty (the two mixers and slot "
         "3's cooler fan, stand-ins until D-18), one heater's %.1f W spread as the hold spreads it (8d), at room temperature in still "
         "air; channels: the mixed air (four), the ambient (two), the plate's inner face, a wall's inner face (one logger). It runs to "
         "steady state, the mixed air drifting at most %.1f K/h over an hour: %.1f h at the line's conductance, up to %.1f h if the case "
         "is as poor as the bound (time constant %.2f h). G = P / rise; the readings that settle it, each the target plus its expanded "
         "uncertainty at that point's rise:" % (ex["power"], DRIFT_K_H, math_log100 * ex["tau_line"], ex["t_bound"], ex["tau_bound"]), first="")
    for lbl, tg, rd, rs in ex["targets"]:
        w("      a reading of at least %.3f W/K (%.1f K rise) meets %.3f W/K: %s" % (rd, rs, tg, lbl))
    para("ACCEPTANCE: at or over %.3f W/K the design holds as stated (route (c)); at or over %.3f W/K section 8's fallback holds; at or "
         "over %.3f W/K E3-O holds with every session measure, provided the measured plate fraction keeps the plate-coupled +70 C class "
         "inside (the plate fraction times %.3f W over the reading, at most %.0f K); under %.3f W/K E3-O as stated cannot hold on the "
         "session's means and the owner decides (a deviation of E3-O or a re-pick). The room reading is the conservative side of the "
         "margin's (8d). The full T-H1 (eight points) follows for the fans-off case, the lid-closed state and the fractions." % (
             ex["targets"][0][2], ex["targets"][1][2], ex["targets"][4][2], T["q_hs"] + T["qb"], c["trip"]["need_by"] - A["e3o_t"],
             ex["targets"][4][2]), first="   ")
    para("9g THE FANS' POWER (13.3 confirmed): counted in pwr_budget.py, the 42.8 W profile, its replay and L4-E9's endurance (2.0 W in "
         "the hold, 3.1 W in the profile), not among the 8.4 W with no document. The bound credits their flow at zero and still counts "
         "their heat inside the case: nothing in 8c changes.", first="")
    w("")
    hr = R["hr"]
    w("10 THE HEAT-REJECTION QUESTION (the consolidation, 2 October 2026: if T-H1 reads under what the approved profile needs, what")
    w("   change inside the rulings restores it at REQ-024's +40 C, and charging on the design day?)")
    para("10a THE NEED. The approved profile PS-IDLE-SPEC puts %.3f W into the case lid open (MODELED: its %.3f W at the pack plus the "
         "pack's own I2R; L4-E9's 43.4 W at a0212d9e). Its +70 C class at REQ-024's +%.0f C needs %.3f W/K; a charge starts only while "
         "the gauge reads at or under %.0f C (TEST-PLAN, T3), so on SC-37's design day (the air %.1f to %.1f C, the replay) charging "
         "with the profile running (%.3f W into the case, the balance of 12b) needs %.3f to %.3f W/K. The rulings: no vent or opening anywhere (32.53), the Peli 1450 at any cost, "
         "the face a 3 mm aluminium plate carrying the UI (32.40). Every figure below is on section 9's bound: the inside by natural "
         "convection only, the coefficients' conservative ends, still air; a two-node model, the inside air and the plate." % (
             hr["q_prof"], C_["prof_pb"], t_use_(R), hr["need_g"], hr["t3"], hr["day"][0], hr["day"][1], hr["q_chg"],
             hr["need_ch"][0], hr["need_ch"][1]), first="")
    para("10b THE THREE APPROACHES. (a) Fins on the face's free strips (the plate %.4f m2 less the monitor window %.4f m2 and the "
         "e-paper lens %.4f m2: %.4f m2), fixed under M3's space beneath the QMX tray (%.2f mm nominal, %.2f mm with the unstated allowances doubled) or a "
         "clip-on exchanger when deployed; effective area multiplier %.0f to %.0f (ASSUMPTION; a vendor's heat-sink datasheet gives the "
         "real one). (b) The large loads led into the plate by heat pipes, bars and gap pads, %.3f W at their pins (%s), so the plate "
         "rejects them at its own temperature and the air keeps the rest; with (a)'s fins. (c) The open lid as a second radiator: an "
         "aluminium skin on the lid's flat ceiling (%.4f m2, an upper bound: the QMX tray and the tablet bracket share it), %.3f m tall "
         "when open, on a copper braid from the plate's edge inside the seal line (%.2f m, %.0f mm2: %.2f K/W, ASSUMPTION; copper %.0f "
         "W/mK). At the profile's heat at +%.0f C and the charging heat (%.3f W, 12b) on the design day (MODELED on the bound):" % (
             R["cb"]["geo"]["a_plate"], hr["mon"], hr["epd"], hr["a_free"], hr["m3"][0], hr["m3"][3], K_FIN[0], K_FIN[1], hr["q_c"],
             ", ".join("%s %.3f" % x for x in hr["coupled"]), R["cb"]["geo"]["a_lid_top"], hr["lid_h"], STRAP_L, STRAP_A * 1e6, hr["r_strap"], K_CU,
             t_use_(R), hr["q_chg"]),
         first="")
    w("      %-40s | +%.0f C: air, plate, G      | design day %.1f C: air, G | %.1f C: air, G" % ("approach", t_use_(R), hr["day"][0], hr["day"][1]))
    for r_ in hr["rows"]:
        w("      %-40s | %6.2f C %6.2f C %6.3f W/K | %6.2f C %6.3f W/K      | %6.2f C %6.3f W/K" % (
            r_["label"], r_["use"]["air"], r_["use"]["plate"], r_["use"]["g"], r_["day_cold"]["air"], r_["day_cold"]["g"],
            r_["day_warm"]["air"], r_["day_warm"]["g"]))
    para("Needs: %.3f W/K at +%.0f C (the air at %.0f C); %.3f and %.3f W/K for charging (the air at %.0f C). The open lid's strap carries "
         "%.2f W at +%.0f C in the best route." % (hr["need_g"], t_use_(R), hr["lim"], hr["need_ch"][0], hr["need_ch"][1], hr["t3"],
                                                  hr["rows"][-1]["use"]["lid"], t_use_(R)), first="   ")
    para("10c CONSEQUENCES (all three passive: no power, no endurance change, the heat unchanged; costs TBD, no quote held). (a): about "
         "%.2f kg of 1.5 mm fins at an 8 mm pitch to the worst M3 height (ASSUMPTION), no inside space; the UI's strips between the "
         "monitor, the e-paper and the switches, the light guides kept clear; bonded fins keep the face a 3 mm plate (a SESSION reading), "
         "an extruded thicker face would change the ruling of 32.40 (the owner's); a clip-on exchanger needs stowage. (b): spreaders and "
         "pads under the plate in the 11.9 to 22.9 mm between board B's tall parts and the face parts (W4), their mass and cost TBD; the "
         "plate runs at %.2f C (%.2f C without fins): the face's touch temperature rises (no held limit: an evaluation owed), the e-paper's "
         "+60 C operation is passed without fins, the switches go to +85 C parts, and each led part sits at the plate plus its path's drop "
         "(the WiFi card's +70 C bounds that drop); all inside the seal. (c): about %.2f kg (a 1 mm skin %.2f kg, the braid %.2f kg), the "
         "braid's fatigue over the hinge's cycles, the lid tray's layout; inside the seal line, no penetration." % (
             hr["fin_mass"], hr["rows"][-1]["use"]["plate"], hr["rows"][3]["use"]["plate"], hr["skin_mass"] + hr["strap_mass"], hr["skin_mass"],
             hr["strap_mass"]), first="")
    para("10d THE SELECTION: NONE REACHES THE NEED ON BOUNDED EVIDENCE. The best route assembled from the three, (b) with (a)'s fins and "
         "(c), keeps the air at %.2f C at +%.0f C: it rejects %.3f W with the air at +%.0f C against the profile's %.3f W, SHORT BY %.3f W "
         "(%.3f W/K). Charging with the profile running stays out of reach: %.3f and %.3f W/K short on the design day's cold and warm ends. "
         "On the bound alone the case rejects %.3f W at +%.0f C (%.3f W short). What would carry the route over: the inside film the "
         "fans make (section 9: credited at zero), and the fins' and the path's real resistances; each is a measurement or a maker's "
         "datasheet, not held. The remaining options are the owner's: an ALTERNATIVE duty cycle at +%.0f C, labelled as such (PS-IDLE, "
         "the monitor dimmed and no beacon: %.3f W into the case, under the best route's %.3f W by %.3f W, and nothing fits on the bound "
         "alone), or a requirement change (the profile's ambient ceiling, or charging with the profile running on the design day)." % (
             hr["rows"][-1]["use"]["air"], t_use_(R), hr["q_max_best"], hr["lim"], hr["q_prof"], hr["short_w"], hr["short_g"],
             hr["short_ch"][0], hr["short_ch"][1], hr["q_max_bare"], t_use_(R), hr["short_w_bare"], t_use_(R), hr["q_idle"],
             hr["q_max_best"], hr["q_max_best"] - hr["q_idle"]), first="")
    para("10e U-02 by the owner's exit definition: a CLOSURE CONDITION, with its exact fact: the sealed case's conductance lid open with "
         "the fans, as T-H1 reads it (the fans' inside film is what no document bounds). The smallest experiment: one point of T-H1, lid "
         "open, the fans at full duty, two heaters (%.1f W, about the profile's heat) spread as the boards dissipate, room air, to steady "
         "state (section 9f's duration). The readings that settle it (each the target plus its expanded uncertainty):" % hr["exp_power"],
         first="")
    for lbl, tg, rd, rs in hr["exp2"]:
        w("      a reading of at least %.3f W/K (%.1f K rise) meets %.3f W/K: %s" % (rd, rs, tg, lbl))
    para("Under the first, the route of 10d applies with its kit on the same bench point, and an owner's choice of 10d's options if it "
         "still reads short. (These readings take the 42.4 W of two heaters for every line and are superseded: 11a and 12d read each "
         "mode at its own heat, the fans counted, and 12a names each mode's governing line.)", first="   ")
    w("")
    rc = R["rc"]
    qq, lm, ck = rc["q"], rc["lim"], rc["check509"]
    w("11 THE THERMAL RECONCILIATION (the owner's amendment of 2 October 2026, 14:20, item 1)")
    para("11a THE CLAIM, CHECKED. Section 10e's line read: a reading of at least %.3f W/K at %.1f W meets %.3f W/K. Its arithmetic: %.1f W / "
         "%.3f W/K = %.1f K at the bench; the expanded uncertainty at that rise is %.2f %% (k = 2), so the conductance after it is %.3f x "
         "(1 - %.4f) = %.3f W/K, which is the profile's %.3f W over the %.0f K from +%.0f C to the +70 C class. The owner's check is right "
         "that the same reading puts the air at %.1f C at +%.0f C. What it establishes is narrower than \"operation at +%.0f C\": the "
         "profile's own +70 C class at +%.0f C, a condition no requirement asks for, because at +%.0f C the kit does not run the profile: "
         "REQ-024: \"%s\"; D-02b: \"%s\". The 1.447 W/K is nonetheless the profile's own condition at REQ-014's +20 C (\"%s\"): there the "
         "profile runs unshed only while the inside air stays under C1's +50 C, %.3f W over 30 K." % (
             ck["reading"], ck["p"], ck["target"], ck["p"], ck["reading"], ck["rise"], 100.0 * ck["u"], ck["reading"], ck["u"], ck["after"],
             hr_q(R), 30.0, t_use_(R), ck["air40"], t_use_(R), t_use_(R), t_use_(R), t_use_(R), lm["req024_c1"], lm["d02b_35"], lm["req014"],
             hr_q(R)), first="")
    para("11b THE HEAT, COUNTED ONCE (MODELED, plan). The profile PS-IDLE-SPEC: %.3f W at the load pins (the five fans' own %.2f W among "
         "them: the three modules' coolers and the two mixers), %.3f W lost in the converters and the distribution, %.3f W in the pack's own resistance: %.3f W into the case. Not in it: "
         "L4-E8's ballasts (%.4f W at its nominal illustration, at most %.2f W at the bound's worst corner, and only while the solar stage "
         "runs), the solar entry's sense bank (solar current only), Q39's 0.0945 W with L4-E11's (B1) (L4-E9 at a0212d9e). Charging "
         "with the profile running on the design day (the balance of 12b, CORRECTED: the source path's loss on the profile's power was "
         "left out) adds %.3f W: %.3f W. The heat stage on shore: %.3f W at the pins (fans %.2f W: slot 3's cooler and the two mixers), %.3f W in "
         "the converters and the distribution, %.3f W in the front end and the charger, the ballasts %.2f W (counted at the worst corner, "
         "the margins' rule): %.3f W. The bench: READY-TO-ACT's heater is %.1f ohm at %.1f V, %.3f W of heat (all of its electrical power "
         "stays inside); two give %.3f W. The fans run from the bench supply, their measured draw is heat inside and is added to the "
         "heaters: P = the heaters + the fans, never the heaters alone (section 10e's 42.4 W left the fans out and is restated here). "
         "To stand for a mode the heaters are set to its heat less the fans' measured draw: the profile %.3f W (two heaters at %.2f V), "
         "the heat stage %.3f W (one heater at %.2f V); the fans' draw replaces their modeled share, so nothing is counted twice." % (
             qq["prof"]["loads"], qq["prof"]["fans"], qq["prof"]["conv"], qq["prof"]["i2r"], qq["prof"]["total"], qq["bench"]["ballast_nom"],
             T["qb"], qq["charge"]["extra"], qq["charge"]["total"], qq["hs"]["loads"], qq["hs"]["fans"], qq["hs"]["conv"], qq["hs"]["front"],
             qq["hs"]["ballast"], qq["hs"]["total"], A["rta_heater"][0], A["rta_heater"][1], qq["bench"]["heater"], qq["bench"]["two"],
             qq["bench"]["prof_heaters"], qq["bench"]["prof_v"], qq["bench"]["hs_heaters"], qq["bench"]["hs_v"]), first="")
    para("11c THE NODES AND THE LIMITS. The conductance is between two nodes: the mixed inside air (the mean of the air channels, the hold's "
         "reference placed in it, 4d) and the ambient air (shaded channels about 0.5 m from the case). The bench ambient is the room "
         "(+%.0f C taken); the operational ambient is REQ-024's \"%s\". The limits and their references: C1's inside-air trigger +50 C and "
         "cell trigger +55 C (REQ-024, CONOPS 4: \"%s\"), control triggers that shed, not damage limits; the SGP41's +55 C inside air "
         "(REQ-052: \"%s\"; TEST-PLAN E3-L: \"%s\"), resting on its Table 5 absolute row, and its +50 C under this record's corrected rule "
         "(Table 4, section 5d, the owner's CFL-002); the +70 C class (the makers' sheets, section 4: RockBLOCK 9704, SA868, G6K, PCM2912A, "
         "LimeSDR, H5007NL, ATP16, PXP4043/C; the AW7915's 0 to +70 C operating while the profile runs it); the module's +%.0f C (CM5 %s); "
         "the cells (E3-A: \"%s\"; \"%s\"). REQ-024's acceptance: \"%s\". D-02a's +55 C is an AMBIENT qualification margin, not an inside-air limit: \"%s\"" % (
             ROOM_C, lm["req024_env"], A["c1"], lm["req052"], lm["e3l_air"], S["cm5_op"]["v"][1], S["cm5_op"]["where"], lm["e3a_t3"],
             lm["e3a_cells"], lm["req024_acc"], lm["d02a"]), first="")
    w("   Each condition: requirement and mode, heat into the case, ambient, the limit at the node, and the conductance it needs (Q / room):")
    for k_, lbl, Q_, amb, lim_txt, L_, lid, gneed in rc["conds"]:
        para("%-4s %s; %s; %.3f W at +%.1f C; %s; needs %.3f W/K" % (k_, lbl, lid, Q_, amb, lim_txt, gneed), first="      ", rest="           ")
    para("CORRECTED in the fix round (12a, astra-check-l4close-1 B3): a +55 C inside-air line exists only as REQ-052's and E3-L's fail "
         "line, read from the SGP41's Table 5 ABSOLUTE row; it is an exclusion screen, not a functional limit, and K1 and K5 (%.3f W/K) are "
         "screens, not closure lines. The SGP41's sensing ends at Table 4's +%.0f C (K2, %.3f W/K at the heat stage on shore). Option C "
         "keeps the part, reports its channel not covered above a 49.0 C reading and switches it off at 54.0 C; it never keeps it powered "
         "on +55 C. The governing line of each required mode is the tightest correctly categorised local limit (12a): the cells, the parts "
         "at their local air with the cooler's exhaust, the junctions and the unpowered parts' storage rows. The owner's conditional "
         "%.2f W/K (X3) belongs to no requirement's mode." % (rc["conds"][0][7], S["sgp_rec"]["v"][1], rc["conds"][1][7], rc["conds"][-1][7]),
         first="   ")
    para("Part-level hot spots: limits on a part's junction or case, not on the air: the TLV75533 regulators' +%.0f C recommended junction "
         "(3c, 5c), the converters' junctions (3c), the module's SoC (its own throttle), the PA's flange on the plate (CONOPS's key-down window and C4, PWR-F15; not this section's K conditions), "
         "the parts in a cooler's exhaust (2h, +%.2f K) and the plate-mounted face parts (the plate's own temperature). T-H1's air reading "
         "bounds the parts rated by ambient that sit in the mixed air; it does not bound the junction-rated parts (their rise is modeled, "
         "THM-001 at +40 C, REQ-024's acceptance) or the parts in the exhaust (placement), which T-H2 measures on the built kit; the plate "
         "fraction it records bounds the face parts." % (R["decl"]["rec755"], T["d_hs"]), first="   ")
    rt = rc["rit"]
    para("11d THE RELATIONSHIP AND THE TRANSLATION. Rittal's calculation basis for enclosure climate control (%s, read 2 October 2026, "
         "sha256 %s, held back by its copyright and fetched by fetch_held_back.py) gives the steady balance \"%s\", A the effective "
         "heat-dissipating enclosure surface to IEC 890 and k the heat transfer coefficient, \"for sheet steel k = %.1f W/m2K\"; the "
         "largest rise follows as Qv / (A k). The conductance of this record is that product, G = A k = Q / rise. The steel figure is "
         "not this enclosure's: the Peli 1450 is a %.2f mm polypropylene shell with natural convection only inside (the fans' flow "
         "credited at zero) and an aluminium face plate lid open, so its k is derived from its own films and walls (section 9's bound). "
         "At +%.0f C and K1's rise of %.1f K, over the plate's exposed %.4f m2 and the walls' outer %.4f m2 (%.4f m2, the floor "
         "adiabatic):" % (RITTAL_URL, RITTAL_SHA, RITTAL_REL, RITTAL_K_STEEL, cb["geo"]["t_wall"] * 1000.0,
                         t_use_(R), rt["rise"], rt["a_plate"], rt["a_wall"], rt["area"]), first="")
    for lbl, kp, kw, kk, gg in rt["rows"]:
        w("      %-30s k plate %.2f, walls %.2f, whole %.2f W/m2K: A k = %.3f W/K" % (lbl, kp, kw, kk, gg))
    para("Sheet steel's %.1f W/m2K on the same area would read %.3f W/K; K1's %.3f W/K needs k = %.2f W/m2K over it, %.1f to %.1f times "
         "what the bound's films give. With a 50 m/s inside flow (a film near 45 W/m2K) A k reaches %.3f W/K (%.3f at the "
         "coefficients' other ends), still air and the floor adiabatic: K1's need lies %s. CORRECTED in 12e: that is not the outside "
         "capacity; with the inside resistance at zero it is %.3f W/K at K1's rise (%.3f at the optimistic ends with the floor), over "
         "K1's need, so no physics bars it and the measurement decides. The tree's other conductance evidence spans "
         "the need: W4's lumped estimate %.2f to %.2f W/K (fixed films with the fans, the floor counted), 32.53's %.1f to %.1f W/K. "
         "The bound under the need leaves feasibility unestablished, not refuted: the floor's support, the outside's real films and "
         "air movement, the fans' film and heat led into the plate past the air (section 10b) are what it does not credit, and only "
         "a measured G decides (T-H1). The translation from the bench to the operating ambient on the same model, the bench's +%.0f C "
         "against +%.0f C (G = Q / rise; radiation grows with the absolute temperatures, natural convection with the rise and falls "
         "slightly with the air's properties):" % (
             RITTAL_K_STEEL, rt["steel_g"], rc["conds"][0][7], rt["k_need"], rt["k_need"] / max(r_[3] for r_ in rt["rows"]),
             rt["k_need"] / min(r_[3] for r_ in rt["rows"]), rt["cap"][0], rt["cap"][1],
             ("over it at the conservative ends and under it, by %.3f W/K, at the other ends" % (rt["cap"][1] - rc["conds"][0][7])
              if rt["cap"][1] > rc["conds"][0][7] else "over it at both ends"), R["cap"]["k1"][0], R["cap"]["k1"][1], rt["w4"][0], rt["w4"][1], rt["s3253"][0],
             rt["s3253"][1], ROOM_C, t_use_(R)), first="   ")
    for row in rc["trans"]:
        w("      %-30s %s" % (row[0], "; ".join("rise %.0f K: %.3f -> %.3f W/K, x %.3f" % x for x in row[1:])))
    para("So the operating ambient's conductance is %.1f to %.1f %% above the room's at the same rise: the room reading is the conservative "
         "side and the translation's uncertainty is not material; the procedure tests at room, with an optional confirming point in a "
         "chamber at +%.0f C. (Section 8d's 1.15 to 1.20 was the outside films' radiation on W4's films alone; the inside film, convective, "
         "dominates the whole.) The same reading does not give the same rise at +%.0f C: the rise there is the bench's divided by that "
         "factor. The rise also differs with the heat: a reading at one heat bounds the same heat; another heat needs its own point "
         "(11f). The transient: E3-A holds +%.0f C for %.0f h; the case's time constant at %.3f W/K is %.2f to %.2f h (32.53's thermal mass), so the "
         "air reaches %.1f to %.1f %% of its steady rise and the steady state is the bound. The sun: REQ-024 \"%s\", D-02e: \"%s\"; "
         "TEST-PLAN holds no Method 505 row: no solar load enters the derivation, and full sun stays a later qualification item." % (
             100.0 * (min(x[3] for row in rc["trans"] for x in row[1:]) - 1.0), 100.0 * (max(x[3] for row in rc["trans"] for x in row[1:]) - 1.0),
             t_use_(R), t_use_(R), t_use_(R), rc["e3a_h"], rc["conds"][0][7], rc["taus"][0], rc["taus"][1],
             100.0 * (1.0 - math_exp(-rc["e3a_h"] / rc["taus"][1])), 100.0 * (1.0 - math_exp(-rc["e3a_h"] / rc["taus"][0])),
             lm["req024_shade"], lm["d02e"]), first="   ")
    para("11e THE MARGIN. Each condition's bench reading at its own heat (the heaters plus the fans), the target plus its expanded "
         "uncertainty at that rise (the budget of 8d); the room-to-operating credit of 11d is kept as margin, not taken:", first="")
    for k_, Q_, gneed, rd, rise_, ur in rc["marg"]:
        w("      %-4s at %.3f W: needs %.3f W/K; a reading of at least %.3f W/K (rise %.1f K, U %.1f %%)" % (k_, Q_, gneed, rd, rise_, 100.0 * ur))
    para("11f WHAT ONE POINT CLOSES, AND WHAT REMAINS (CORRECTED by 12a: a dummy-load mixed-air point closes only the conductance it "
         "measures, for its lid state, fan state, heat and heat placement; no mode's functionality). One passing point lid open, the fans "
         "on, at the heat stage's heat (the heaters at %.3f W plus the fans), reading at least %.3f W/K, meets the conductance SCREENS K1, "
         "K3, K4 and K9 at the mixed air; it does not close REQ-024, E3-A or E3-O, whose governing lines are 12a's. Screens met only by a "
         "further measured point: K5 (lid closed, the same heat, reading at least %.3f "
         "W/K lid closed), K6 (the profile's heat, REQ-014 at +20 C, at least %.3f), K7 and K8 (the profile with the charge, at least "
         "%.3f and %.3f, and the cells' own rise over the air, U-01's), K10 (the hold's heat in E5, at least %.3f). Open: K2 (the SGP41 on "
         "Table 4, the owner's CFL-002), the part-level hot spots (T-H2, THM-001), the fans' rating (D-18, REQ-043), full sun (D-02e, a later "
         "qualification item), the cells on the pack at +%.0f C (U-01, L4-E10)." % (
             qq["bench"]["hs_heaters"], rc["marg"][0][3], rc["marg"][4][3], rc["marg"][5][3], rc["marg"][6][3], rc["marg"][7][3],
             rc["marg"][9][3], t_use_(R)), first="")
    para("11g THE PROCEDURE (T-H1-PROCEDURE-DRAFT.md, revised): the points of 12d (one per mode's heat and lid state), each with its "
         "heaters (READY-TO-ACT's %.1f ohm, the nearest whole number of them) set to the mode's heat less the fans' measured draw (the "
         "model's draw shown here) and spread over the places in proportion (W, plan; the fans excluded, being real):" % qq["bench"]["r"], first="")
    short = {"board B (slot 3, its switch, hubs, supervisors, the device rail)": "board B", "the pack (its own I2R)": "the pack",
             "the front end and the charger (boards E and A, on shore)": "the front end and the charger"}
    for s_ in qq["settings"]:
        para("%-11s %.3f W: the heaters %.3f W (the fans %.3f W), %s at %.2f V%s; %s" % (
            s_["k"], s_["Q"], s_["heaters"], s_["fans"], "one" if s_["n"] == 1 else "two" if s_["n"] == 2 else str(s_["n"]), s_["v"],
            "" if s_["n"] == 1 else " each",
            "; ".join("%s %.3f" % (short.get(k_, k_), v_) for k_, v_ in s_["spread"])), first="      ", rest="                  ")
    para("Each point's readings and duration: 12d. A case as poor as the bound takes up to %.1f h a point (9f)." % rc["t_bound"], first="   ")
    para("The endpoint is steady state, the mixed air drifting at most %.1f "
         "K/h over an hour, or a first-order fit theta(t) = theta_ss + (theta_0 - theta_ss) exp(-t/tau) over at least three time constants "
         "with residuals at most 0.05 K RMS and tau within a factor 2 of C/G; theta_ss's fitted standard error joins the rise's "
         "uncertainty. Pass: the reading less its expanded uncertainty at or over the condition's need; fail: under it; inconclusive: the "
         "endpoint not met, or the supply or a fan's draw moving more than 1 %% or the ambient more than 1 K in the averaging hour (the "
         "point is repeated). Authorisation to perform it is the owner's; accepting its result goes through the coordinator's check against "
         "this section; no temperature requirement is relaxed to make a point pass." % DRIFT_K_H, first="   ")
    # ======================================================== 12: the fix round of the Layer 4 review
    pm, br = R["pm"], R["br"]
    th_ = pm["th"]
    w("")
    w("12 THE FIX ROUND OF THE LAYER 4 REVIEW (astra-check-l4close-1 at 8fbb68b6, the owner's one authorised review: B3, B4 and B7)")
    para("12a B3, THE SGP41 AND OPTION C, RESTATED. Sensirion's SGP41 sheet: Table 4, the recommended conditions, operation to +%.0f C "
         "and storage %.0f to %.0f C (%s; its gas sensing specifications hold only when the sensor is stored and operated under them, "
         "%s); Table 5, the absolute ratings, operation to +%.0f C and short-term storage to +%.0f C "
         "(%s; \"%s\"). Sensing is supported to +%.0f C only; the +%.0f C row is an exclusion screen and never stands in for the "
         "sensor's function. Option C of CFL-002 (section 6) keeps the part and reports its channel as not covered while its reference "
         "reads over 49.0 C and after storage outside %.0f to %.0f C until Sensirion states otherwise; it switches the sensor off at a 54.0 "
         "C reading, so it is never powered on the +%.0f C line, and unpowered its survival rests on Table 5's short-term storage row "
         "(absolute: INCONCLUSIVE until Sensirion, the clarification drafted). Section 11's K1 and K5 used the +%.0f C row as a line: "
         "withdrawn, they are screens (11c, 11f). Every required mode below: its heat balance, its ambient and every correctly "
         "categorised LOCAL limit (the cells at the air plus their own I2R over the pack block's lowest film, %.4f W/K; the control "
         "thresholds whose firing ends or sheds the mode; the parts at their local air, the cooler's exhaust included; the junctions; the "
         "unpowered parts' storage rows, or their operating rows read to cover them unpowered where no storage row is held), each "
         "with the mixed air it allows and the conductance it needs (Q / room); the governing line is the tightest; absolute ratings "
         "are listed as screens, never as lines. With the route's measures (5b, 5c: the +70 C parts out of the running cooler's "
         "exhaust, the two regulators changed, the pushbuttons to an +85 C part); MODELED on the plan heat." % (
             S["sgp_rec"]["v"][1], S["sgp_rec_st"]["v"][0], S["sgp_rec_st"]["v"][1], S["sgp_rec"]["where"], S["sgp_guar"]["where"],
             S["sgp_op"]["v"][1], hi_of(S, "sgp_st"), S["sgp_op"]["where"], S["sgp_abs"]["quote"][:90], S["sgp_rec"]["v"][1], S["sgp_op"]["v"][1],
             S["sgp_rec_st"]["v"][0], S["sgp_rec_st"]["v"][1], S["sgp_op"]["v"][1], S["sgp_op"]["v"][1], pm["gb"]), first="")
    for m_ in pm["modes"]:
        para("%s %s. Heat %.3f W (%s); +%.1f C; lid %s." % (m_["id"], m_["label"], m_["Q"], ", ".join("%s %.3f" % x for x in m_["heat"]),
                                                             m_["amb"], m_["lid"]), first="   ", rest="      ")
        ln = m_["by"]["as ruled"]["lines"]
        shown = [x for x in ln[:6]]
        for x in shown:
            para("%-6s W/K  the air to %6.2f C  %s [%s]" % ("inf" if x["g"] == float("inf") else "%.3f" % x["g"], x["t"], x["name"], x["cat"]),
                 first="      ", rest="                ")
        rest_ = [x for x in ln[6:]]
        if rest_:
            w("      every other line needs at most %.3f W/K" % rest_[0]["g"])
        scr = m_["by"]["as ruled"]["screens"] + [x for x in m_["by"]["C"]["screens"] if x not in m_["by"]["as ruled"]["screens"]]
        if scr:
            para("screens (absolute, never lines): %s" % "; ".join("%s (%s)" % (a_, b_) for a_, b_, _c in scr),
                 first="      ", rest="      ")
        govs, seen = [], {}
        for opt in OPTIONS:
            b = m_["by"][opt]
            g_ = b["gov"]
            txt_ = "%s, %s" % (g_["short"], "no conductance (the limit at or under the ambient)" if g_["g"] == float("inf") else
                               "%.3f W/K, %s" % (g_["g"], "no bench reading suffices (its rise is too small for the budget)"
                                                 if b["read"] == float("inf") else "a reading of at least %.3f W/K" % b["read"]))
            seen.setdefault(txt_, []).append(opt)
        for txt_, opts in seen.items():
            who = opts[0] if len(opts) == 1 else ("every option" if len(opts) == len(OPTIONS) else ", ".join(opts[:-1]) + " and " + opts[-1])
            govs.append("%s: %s" % (who, txt_))
        para("GOVERNING (the route's measures): %s." % "; ".join(govs), first="      ", rest="      ")
        b = m_["by"]["C"]
        if b["stated"] is not b["gov"]:
            para("Without the INFERRED reading (once the maker states the unpowered range at or over its operating top): %s (%s), %.3f W/K, a "
                 "reading of at least %.3f W/K." % (b["stated"]["short"], b["stated"]["cat"], b["stated"]["g"], b["read_stated"]), first="      ", rest="      ")
        dg = m_["designed"]["gov"]
        para("As designed (no route measure; the SGP41 as ruled): %s, %s." % (dg["short"], "no conductance" if dg["g"] == float("inf") else "%.3f W/K" % dg["g"]),
             first="      ", rest="      ")
        para("REMAINING: %s" % REMAIN[m_["id"]], first="      ", rest="      ")
    para("CFL-002, restated with C as defined: as ruled today (no option taken; REQ-042's VOC channel sensing across the envelope) the "
         "SGP41's Table 4 +%.0f C governs the heat stage at +40 C, %.3f W/K on the pack and %.3f W/K on shore (M1, M2, and lid closed M3, "
         "M4); under C the channel is reported not covered above its 49.0 C reading and the sensor is off from 54.0 C, so the governing "
         "line moves to the cells' hot stop H1, %.3f W/K on the pack and %.3f W/K on shore, with the unpowered SGP41's survival a "
         "screen until Sensirion states its short-term storage duration; under A (a BME688 in its place, operable to +%.0f C) and B "
         "(the channel dropped) the line is H1's as under C, A owing the BME688's gas performance above +40 C. C restricts REQ-042's "
         "channel inside the envelope, which D-02a does not grant today: CFL-002 stays the owner's." % (
             th_["sgp4"], pm["modes"][0]["by"]["as ruled"]["gov"]["g"], pm["modes"][1]["by"]["as ruled"]["gov"]["g"],
             pm["modes"][0]["by"]["C"]["gov"]["g"], pm["modes"][1]["by"]["C"]["gov"]["g"], th_["bme"]), first="   ")
    para("What a bench point closes. T-H1 is a dummy-load, mixed-air measurement: one passing point establishes the conductance "
         "between the mixed air and the ambient for its own configuration (lid state, fan state and supply, heat, heat placement, room "
         "air), and the temperature offsets it records. It closes no mode's functionality: the cells' rise in the pack, the parts' "
         "local air in the built kit, the junctions, the hot stop's thresholds and every functional check of E3-A, E3-L, E3-O and E5 "
         "stay with their own evidence (U-01, T-H2, THM-001, E3-H). Lid-closed and fans-off states need their own points; the room-to-"
         "operating translation of 11d is a model, not a validation of other fans, flow restrictions, lid states or heat placements.",
         first="   ")
    b4 = pm["b4"]
    cbal = T["chg_prof"]
    para("12b B4, THE CHARGING HEAT AS A BALANCE (CORRECTED: section 11 added only the charge increment to the battery profile's heat "
         "and left out the source path's loss on the profile's own power). On the model's boundary (pwr_budget: the charge path at %.2f "
         "x %.2f = %.3f, ICHG %.1f A into the pack at %.1f V): input %.3f W less stored %.3f W less exported %.3f W = %.3f W of heat, which "
         "is the profile's %.3f W at the battery node, the source path's %.5f W, the charge path's %.5f W and the charging cells' %.3f W; "
         "the reviewer's 50.04367 W reproduced. On SC-37's design day the charge comes through the solar stage, so L4-E8's ballasts add "
         "%.2f W at their worst corner (the margins' rule): %.3f W, used in sections 10, 11 and 12a. K7 and K8 (T3's start, the idle "
         "cells at the air), each with its bench reading:" % (
             b4["eta_chg"], T["eta_fe"], cbal["eta"], b4["ichg"], CHG_V, cbal["p_in"], cbal["stored"], cbal["exported"], cbal["heat"],
             cbal["parts"]["loads"], cbal["parts"]["supply"], cbal["parts"]["charge"], cbal["parts"]["cells"], T["qb"], R["hr"]["q_chg"]), first="")
    for amb_, q_, g_, rd_ in b4["rows"]:
        w("      +%.1f C at %.3f W: needs %.4f W/K, a reading of at least %.4f W/K" % (amb_, q_, g_, rd_))
    para("A running charge is governed by T4 on the charging cells, their own %.3f W over the block's film adding %.2f to %.2f K "
         "(12a, M8 and M9). Section 2d's charge in E3-O keeps the charge path's %.3f W only: the pack is outside the case there, its "
         "cells' I2R with it." % (cbal["parts"]["cells"], b4["rise"][0], b4["rise"][1], T["charge_extra"]), first="   ")
    para("12c B7, THE BATTERY-ONLY RUN COUPLED TO C1 (MODELED, energy-and-thermal). The run: PS-IDLE-SPEC on the pack (%.3f W at the "
         "pack, %.3f W into the case) from a kit soaked at +%.0f C, lid open, shaded, still air; C1 moves the kit to the reduced mode at "
         "the inside air's +%.0f C and, its trigger still holding at the next reading, to the heat stage (%.3f W at the pack, %.3f W into "
         "the case; CONOPS states no dwell between the two, the model takes none); the reduced mode's restore, 5 K under the trigger, "
         "is not reached; the run ends on the 35E's usable %.1f Wh at the profile's rate (the shed states' slightly larger usable "
         "energy, energy_budget's PS-SURV-R row, not credited); the cells quasi-steady over the air by their own I2R over the block's "
         "lowest film; one node, C the kit's %.0f to %.0f kJ/K (32.53). The reviewer's constant-G check reproduced (C %.0f kJ/K): %s." % (
             br["p1"], br["q1"], br["amb"], th_["c1_air"], br["p2"], br["q2"], br["e_use"], T["kJ"][0], T["kJ"][1], T["kJ"][0],
             "; ".join("G %.4f W/K reaches C1 at %.3f h and, unshed, the air %.2f C at %.2f h" % (g, t_, a_, br["t_energy"]) for g, t_, a_ in br["rev"])),
         first="")
    w("   The enclosure model's own G(rise) (section 9, lid open), integrated in %.0f s steps:" % br["dt"])
    for r_ in br["runs"]:
        w("      %-30s C %4.1f kJ/K: %s; the run %.2f h; the air at most %.2f C, the cells at most %.2f C (H1 at %.1f C %s)" % (
            r_["label"], r_["c"], "C1 at %.2f h, then the heat stage for %.2f h" % (r_["t_c1"], r_["t_end"] - r_["t_c1"]) if r_["t_c1"] else "C1 not reached",
            r_["t_end"], r_["air_max"], r_["cell_max"], th_["h1"], "REACHED" if r_["hot_stop"] else "not reached"))
    ts_ = [r_["t_c1"] for r_ in br["runs"] if r_["t_c1"]]
    te_ = [r_["t_end"] for r_ in br["runs"] if r_["t_c1"]]
    para("So, ENERGY-AND-THERMAL (MODELED, on the bound and its other ends): C1 sheds the profile from %.2f to %.2f h where it acts, "
         "and the runtime with the shed states is %.2f to %.2f h, of which %.2f to %.2f h unshed; where C1 does not act, the profile "
         "runs its %.2f h. The profile runs its whole energy unshed only from a constant %.3f W/K at C %.0f kJ/K (%.3f W/K at %.0f kJ/K), and for "
         "any duration from K6's %.3f W/K. ENERGY ONLY: %.2f h (%.1f Wh at %.1f W) stays labelled energy-only; it is not an established "
         "unshed PS-IDLE-SPEC endurance. No hot stop on the bound. The bench runs that would show it: on T-H1's bench, a transient point, "
         "the empty case soaked at room temperature, the heaters stepped to the profile's heat less the fans' draw (%.3f W) and, when the "
         "mixed air has risen %.0f K, to the heat stage's battery-only heat less the fans' draw (%.3f W), logged to the run's end: the "
         "time to C1 and the air after it (the empty case's thermal mass is under the kit's: the conservative side); then, on the built "
         "kit (Layer 9), a battery-only PS-IDLE-SPEC run from a 24 h soak at +%.0f C, lid open, shaded, still air, logging the inside air "
         "at the hold's reference, the four cell thermistors, the gauge's energy and every C1 transition to the graceful shutdown: the "
         "runtime with its shed states, and the cells under H1. Authorisation is the owner's, acceptance the coordinator's check." % (
             min(ts_), max(ts_), min(te_), max(te_), min(ts_), max(ts_), br["t_energy"], br["g_full"][0][1], br["g_full"][0][0],
             br["g_full"][1][1], br["g_full"][1][0], br["g_never"], br["t_energy"], br["e_use"], br["p1"], br["q1"] - qq["prof"]["fans"],
             br["rise_c1"], br["q2"] - qq["hs"]["fans"], br["amb"]), first="   ")
    para("12d THE BENCH POINTS (T-H1-PROCEDURE-DRAFT.md): one per heat and lid state, the fans on, each reading the conductance its "
         "configuration has and nothing else; each mode's governing reading as ruled and under C (12a), and where the governing line is "
         "an operating row read to cover an unpowered part, the maker-stated line beside it; the duration at the lowest reading (tau = "
         "C / G, C %.0f kJ/K; steady within 1 %% of the rise at ln(100) tau, then an hour averaged; a first-order fit needs three time "
         "constants):" % rc["kj_hi"], first="")
    for pt in pm["points"]:
        rd_txt = []
        for i_, opt, sh, g_, rd, sh2, g2, rd2 in pt["reads"]:
            s_ = "%s %s: %s %s" % (i_, opt, sh, "no conductance" if not math.isfinite(g_) else "%.3f W/K read at %s" % (
                g_, "none" if not math.isfinite(rd) else "%.3f" % rd))
            if sh2 != sh:
                s_ += " (stated: %s %.3f W/K read at %.3f)" % (sh2, g2, rd2)
            rd_txt.append(s_)
        para("%s at %.3f W, lid %s: %s; tau %.2f h, steady at %.1f h, the fit's three time constants %.1f h" % (
            " and ".join(pt["ids"]), pt["Q"], pt["lid"], "; ".join(rd_txt), pt["tau"], pt["steady"], pt["fit"]), first="      ", rest="         ")
    para("Then the fans-off case at M2's heat (no pass line: the failure case) and 12c's transient point. A point passes for a mode and "
         "option when its reading meets that line; it closes that conductance only.", first="   ")
    cp = R["cap"]
    para("12e THE OUTSIDE CAPACITY (the addendum to the fix round, the coordinator's question of 2 October 2026: which lines a reading "
         "can pass at all). The outside surfaces' capacity with the inside resistance at zero (every inner face at the inside air, the "
         "3 mm aluminium plate isothermal), at each line's own ambient and rise, still air: bare (the plate's outer face and the walls "
         "through the PP shell; lid closed, the enclosed layer, the lid's shell and its outside films; the floor credited only at the "
         "optimistic ends, its feet over a support at the ambient) and with the combined route of 10b (R-170, fins of multiplier %.0f at the "
         "conservative end and %.0f at the optimistic on the free strips' %.4f m2, adding %.4f to %.4f m2 of effective outside area; R-171, "
         "the large loads led into the plate, which adds nothing once the inner faces sit at the air; R-172, the open lid's skin, %.4f m2 "
         "on its %.2f K/W strap; the route acts with the lid open only, so lid closed it is the bare case). Conservative coefficient ends "
         "(the plate's emissivity %.2f, the shell's %.2f, PP at %.2f W/mK, the plate's view %.2f) and optimistic ends (%.2f, %.2f, %.2f, "
         "%.2f, the floor credited). CORRECTION: section 9's 'cap' (%.3f W/K at E5's rise, %.3f at E3-O's) is the bound with a 50 m/s "
         "inside flow, whose film is near 45 W/m2K; the capacity proper at those rises is %.3f and %.3f W/K on the conservative ends. "
         "Class (i): reachable bare, T-H1 decides; (ii): reachable only with the route fitted, T-H1 with the route decides; (iii): over "
         "the capacity even with the route and the optimistic ends, so no measurement can pass it: a contradiction between the rulings "
         "(no vent, the Peli 1450, the device set) and that mode's requirement, the owner's. Each class is read at the optimistic ends "
         "(what physics may allow); the class at the conservative ends is printed beside it." % (
             K_FIN[0], K_FIN[1], R["hr"]["a_free"], cp["fin_add"][0], cp["fin_add"][1], cp["skin"][1], cp["skin"][0],
             R["cb"]["cons"]["eps_plate"], R["cb"]["cons"]["eps_shell"], R["cb"]["cons"]["k_pp"], R["cb"]["cons"]["f_open"],
             R["cb"]["opt"]["eps_plate"], R["cb"]["opt"]["eps_shell"], R["cb"]["opt"]["k_pp"], R["cb"]["opt"]["f_open"],
             R["cb"]["cap"]["E5"], R["cb"]["cap"]["E3-O"], cp["check9"][2], cp["check9"][0]), first="")

    def cls_at(e, i):
        need = e["line"]["g"]
        if not math.isfinite(need):
            return "iii"
        return "i" if need <= e["bare"][i] + 1e-12 else ("ii" if need <= e["route"][i] + 1e-12 else "iii")
    for e in cp["lines"]:
        ln = e["line"]
        if not math.isfinite(ln["g"]):
            para("%s, lid %s, +%.1f C: %s (%s) at or under the ambient: no capacity at a zero rise; class (iii), the whole %.3f W short" % (
                e["mode"], e["lid"], e["amb"], ln["short"], e["tag"], e["Q"]), first="      ", rest="         ")
            continue
        para("%s, lid %s, +%.1f C, rise %.2f K: %s (%s) needs %.3f W/K; capacity bare %.3f / %.3f, with the route %.3f / %.3f W/K "
             "(conservative / optimistic): class (%s)%s%s" % (
                 e["mode"], e["lid"], e["amb"], e["rise"], ln["short"], e["tag"], ln["g"], e["bare"][0], e["bare"][1], e["route"][0], e["route"][1],
                 e["cls"], "" if cls_at(e, 0) == e["cls"] else ", (%s) at the conservative ends" % cls_at(e, 0),
                 "; SHORT by %.3f W/K, %.3f W, of the route's optimistic capacity" % (e["short_g"], e["short_w"]) if e["cls"] == "iii" else ""),
             first="      ", rest="         ")
    sh_ = cp["shed"]
    ep_ = cp["epaper"]
    para("The class (iii) lines and their options (none lowers a requirement silently; each names its owner): (1) E3-L at +40 C with "
         "the lid closed as ruled (M3 on the pack, M4 on shore): the SGP41's Table 4 +50 C lies over the closed case's capacity. "
         "Options: CFL-002's C, A or B (the owner's), which move the line to the cells' hot stop H1, %.3f and %.3f W/K, under the closed "
         "capacity's optimistic end and over its conservative one, so T-H1's lid-closed point decides; a closed-lid ceiling on REQ-042's "
         "VOC channel (a requirement change, the owner's: the bay air holds Table 4's +50 C lid closed only to an ambient of +%.1f to "
         "+%.1f C on the pack and +%.1f to +%.1f C on shore, conservative to optimistic); D-02b's closed-lid test at +40 C restated (a "
         "ruling change, the owner's); a closed-lid conduction path from the plate to the lid's inner face inside the seal (the "
         "session's to develop at Layer 7; not modelled here, so it closes nothing yet). (2) E3-O at +55 C (M6): the e-paper, unpowered, "
         "judged on its +60 C operating row read to cover it (INFERRED), lies over the route's capacity. Options: PDi's storage "
         "statement (the request is drafted in clarification/pervasive-displays-e2370ks0c1.txt; sending it is the owner's), with a range "
         "at or over +70 C the line becomes the +70 C class, %.3f W/K, class (i); the e-paper's own temperature at its window in the "
         "plate rather than the mixed air (the session's: a T-H1 channel at the window), at the bound's plate fraction %.3f it needs "
         "%.3f W/K and at W4's high fraction %.3f it needs %.3f W/K, both under the route's optimistic capacity, so the measured "
         "fraction decides; an e-paper with a held range at or over +70 C (CHO-001, the owner's); E3-O run with the e-paper's state as "
         "a recorded deviation (TEST-PLAN's owner). (3) E5's +60 C dwell (M7): the same e-paper at an ambient equal to its operating "
         "top: no capacity and no plate fraction carries it. Options: PDi's statement (then the LimeSDR's +70 C storage row, %.3f W/K, "
         "class (i) at the optimistic ends); a different e-paper (CHO-001, the owner's); E5 run with the e-paper out as a recorded "
         "deviation (TEST-PLAN's owner). Charging (M8, M9) is not class (iii); for scale, charging only in the heat stage (%.3f W into "
         "the case) would need %.3f and %.3f W/K at T4's line, class (i) at both ends, at the cost of the profile while charging (the "
         "48 to 72 h DESIGN OBJECTIVE, already NOT MET, would lose the profile's service during the charge: an owner's choice of "
         "duty cycle, not taken)." % (
             md_cap("M3", R, "C"), md_cap("M4", R, "C"), cp["ceil_sgp"]["M3"][0], cp["ceil_sgp"]["M3"][1], cp["ceil_sgp"]["M4"][0],
             cp["ceil_sgp"]["M4"][1], md_cap("M6", R, "C", stated=True), ep_["M6"]["f"], ep_["M6"]["need"], ep_["M6"]["f_hi"],
             ep_["M6"]["need_hi"], md_cap("M7", R, "C", stated=True), cp["q_hs_chg"], sh_[0]["need"], sh_[1]["need"]), first="   ")
    w("")
    w("13 Predicates")
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
