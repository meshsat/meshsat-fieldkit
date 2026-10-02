#!/usr/bin/env python3
"""l4e11_power.py: layer 4 task L4-E11 (MESHSAT-1357, 2 October 2026). Three items the connected power architecture (L4-E9)
left open, resolved as engineering choices with their bounds:

  U-04  source-only and dead-pack operation (the kit on a vehicle or shore source with the pack absent, at or below its
        protection cutoff, or with its FETs open);
  D-06  the vehicle-entry interconnect in F1's long-time band from a weak source;
  D-09  the hot swap's fault time against its own start into VIN_RAW (added by the coordinator on 2 October 2026).

The fix round (2 October 2026) answers the collaborator's focused check (checks/astra-check-l4e11-1.md): the LM5069's UVLO by
SNVS452G Equations 38 to 40 and its POREN at the IC from a 9.00 V plug, so the entry is replaced (B1); the charge holds as a
state table of charge and discharge permission (B2); the source envelope with the kit's own losses and a functional warm-up
(B3); the weak-source envelope as monotone intervals and the interconnect specified by its resistance (B4); R-b's register
value and its actual-current bound (B5).

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured. No generator, registry, interface or
Layer 3 file is edited here; the circuit changes are the release-guarded drafts beside this file. Every printed figure
carries its class: MAKER (a maker's row, page named), CATALOGUE (a filed distributor reading), NETLIST (the committed
netlists or generators), REQUIREMENT (the registry's text), RECORD (another record's committed output, its own class
kept where it states one), INFERRED (method stated), CONDITIONAL (a calculated result on an unwarranted assumption or an
open measurement), ASSUMPTION (a figure no document gives), SESSION (a choice this record takes, with its reason).

Inputs are pinned by sha256 (PINS); L4-E9's output and hot-swap draft are read from its commit (GIT_PINS), never retyped.
Run from the repository root:  python3 v2/docs/records/l4e11/l4e11_power.py > v2/docs/records/l4e11/l4e11_power.out
Needs pdftotext and pdftocairo (poppler), PyYAML, git, and the held documents (fetch_held_back.py beside this file).
The consolidation round (2 October 2026, the owner's instructions of 11:25 and 12:00) evaluates TI's BQ25730 against board A's
circuit (its pins, the settings L4-E4 to L4-E8 drafted, startup and protection in each mode, the affected budgets with the battery
FET it adds), compares it with the drawn arrangement and with any other implementation a maker's sheet supports, selects one and
classifies U-04 (sections 12 to 14). The fix round (2 October 2026) answers the consolidation review cx36 (set 27, NOT YET): board
E's auxiliary domain moved to a VSYS feed over the dock (B1), the start bounded by the input clamp, the retries and a bench
acceptance, and the battery FET re-selected on its maker's printed maxima at BATDRV's least drive, a pair of Nexperia BUK6Y10-30P
(B2), with the charger minors (section 15).
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a predicate this record rests on failed."""
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REC = "v2/docs/records/l4e11"

PINS = {
    "reqs": ("v2/ecad/tools/pcb_requirements.yaml", "b624ac495650a3592c45a37610375fb05bf7b775042cf3de7ec8979bc46a6e50"),
    "rules": ("v2/ecad/tools/pcb_rules.yaml", "14ea032a7fdd86ac877a51ec7bdc804d95c1c639ddbca4035338da5a09d8b83f"),
    "testplan": ("v2/docs/TEST-PLAN.md", "42a3dff33442c86089a2c6c9dee841e8e2c8b9cbc1222a4adc311902b3c316f7"),
    "hwfw": ("v2/docs/HW-FW-CONTRACT.md", "1c211e467d81b8b70546bc4435c65d4bd2dcd0d2fc3606714a746b4d8d0ac1fa"),
    "panel": ("v2/docs/PANEL.md", "b396d028b41e880d7768cb1062111984b8800ee2333d29fcf4ba6b882b82c2e4"),
    "assembly": ("v2/docs/ASSEMBLY.md", "942d562edd128759c52ee976f7255862f7a2ef78b5fd76af0a2e223f328e64cd"),
    "gen_a": ("v2/ecad/tools/gen_sch_a.py", "6a136feec6c9cf4e2011ed8c45a1f2e0adc3e263718c355b4b909872ee5d3c4b"),
    "gen_e": ("v2/ecad/tools/gen_sch_e.py", "f846e138cb53a8c63247efb3ad7b5cc44a68cb73e71699c65fd53b63c01af186"),
    "gen_p": ("v2/ecad/tools/gen_sch_p.py", "740817ada5c8e14af8c8e001b775e09cbae94d6a03ad462ee2e1c1755bc935a3"),
    "net_a": ("v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "6c40250c47195ebb7b2ae1388e284dc7f2fba9f2e683f654a47c98444290e8c5"),
    "net_e": ("v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net", "2ed95a0e8069ebf8ad31f4567a14015e863182a83b6de7b3b13218488d8316d4"),
    "packprot": ("v2/ecad/tools/pcb_pack_protection.yaml", "ab1dbc3f3f69aa4687a4fa9745c0cbdc96d0521146dc5d3f84698656e33c484b"),
    "primcfg": ("v2/docs/review-packets/battery/PRIMARY-CONFIGURATION.md", "6726f23778f48e1017d29fffe923c4b07b9e196d4636e3e90432774d9f922aac"),
    "chain": ("v2/ecad/tools/pcb_energy_chain.yaml", "a09ca0293afd1f7c553cbffb5b95bc33ae58688a4c20b8de65ec47c15d45996c"),
    "l4e5": ("v2/docs/records/l4e5/l4e5_source_control.out", "f9c98ec5c43ada0e1a5a033a794c98b45f110ffcb0a67ff8c81a31fede134e71"),
    "budget": ("v2/docs/records/rv-pwr/pwr_budget.out", "58e40cf604804cc9d70c7fbeb1012be4552563fcc8ae7ef6755003c33acb902f"),
    "red2": ("v2/docs/records/hc2/pwr_red2.out", "835910e807d588c481951dc879e030b55d893453bd124872b9310a99bed46db6"),
    "ecss": ("v2/vendor/standards/ecss-q-st-30-11c-rev2-2021-06-23.md", "576256819950c4432b48769e5f642ee5bfb0eed4f025c03fb9727de7dbeabeea"),
    "bq25731": ("v2/vendor/ti/bq25731-datasheet.pdf", "3e5e927fdf63cf6a2397630987c58e947ebc80d5a1cfc93fb1fb58d98bb58973"),
    "sluuaq3a": ("v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf", "525d16b2bdee44e5b587ccf6800b9967bc524772d0b5a20937957ea2e738b7ad"),
    "csd17570": ("v2/vendor/battery/ti-csd17570q5b.pdf", "596555c33dce1fcac6de3b6ecc3eeb443f202382b3e2091fd6e1c27d129f2436"),
    "cell": ("v2/vendor/battery/samsung-35e-orbtronic.pdf", "5ec577b952b9dc5106593a4e4c3a6e8cea64f6f72b8faaf1bb512155c29dc516"),
    "lm5069": ("v2/vendor/ti/ti-lm5069.pdf", "d60d8106a6e8113900ff8b9576dd959942fa7169742baf0beeb30684d4d64681"),
    "csd19532": ("v2/vendor/power/ti-csd19532q5b-n-fet.pdf", "353ce937cff0b719e730010829720d25c2ece3637ed92fb7ad8cc370438559d1"),
    "d38999": ("v2/vendor/d38999/amphenol-d38999-iii-federal.pdf", "13a19268ba5939d9e4df5a20f9db84bb72e86525b82f0586c85696e42c126a2b"),
    "vh": ("v2/vendor/connectors/jst-vh-catalogue.pdf", "d51e669c597988b20c0963daf5bef7356cbd2104c1f867e9107c6fa6cd2b899c"),
    "xt60": ("v2/vendor/battery/amass-xt60-spec-tme.pdf", "c2cbb5962c1f37da89e76e505c75184dd07e84eec3a6fe5f24569dafc6f6b9e9"),
    "keystone": ("v2/vendor/keystone/M65p42.pdf", "caa141ea51ac68cf80ab6e14ad2075fcfc76206451f4bfe45330005c0deaf395"),
    "lapp": ("v2/vendor/d38999/cables/lapp-olflex-robust-210-product-information.pdf", "535cc7900e32bed34ea2dcb277708650bb90e06eb39f41d7dfb4ced4660ec2ba"),
    "alpha": ("v2/vendor/d38999/cables/alpha-25064-spec.pdf", "232d6661444a7e3a75819a61d57df4a83735353c4c8ea3ac204450a59e77d300"),
    "lm5176": ("v2/vendor/ti/lm5176-datasheet.pdf", "98191bec36d43771affa3e1540f6e1737347c19a1602747ffb4327509550a820"),
    "bq25798": ("v2/vendor/power/bq25798.pdf", "631d541679512116b5cf7ade0516000e78bc95f060b8b958e726c1b6eb74c27f"),
    "srf1260": ("v2/vendor/power/bourns-srf1260-common-mode-choke.pdf", "93b2dc7565d07e727adb658843b52ec227a2c05f1ee21e117d7057d03ba1aea6"),
    "yageo": ("v2/vendor/passives/yageo-cc-series.pdf", "61a606825ab314ea318cfb5362848a62fdffb851efa9818d642e9a541c56a648"),
    "fuse997": ("v2/vendor/power/held/littelfuse-997-mini58v-rev2025-11-18.pdf", "437b1fd2c8cb3ef16107ec14d096b31ef3c3cb83893325234e880deb7540393e"),
    "mur104": ("v2/vendor/passives/held/murata-grm3195c1h104ga05-01a-2026-06-11.pdf", "4457e5ec41c25d29a47f9201bd903f0f4abf98c7566d84a81aae7028e2d7a188"),
    "mur683": ("v2/vendor/passives/held/murata-grm3195c1h683ja05-01a-2026-06-11.pdf", "89cfedda1a8d61d5cf5371ab274a8c033e2bd9157d959ddd27d4e8963a934fde"),
    "lm74700": ("v2/vendor/ti/ti-lm74700-q1.pdf", "e16b3a8c0023201fafa5825436f5f2dd6f885b92b84e65602b3f50d741c58b6f"),
    "tps4811": ("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "3cfe41fef1407b85abaaee1e27a95ac3cf2cb1bdf218209b8578a835c4c9497f"),
    "csd19536": ("v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf", "19e1a9660fac8577743f40acc2cdc791539afd5232bbc1fc350e15fec735d78d"),
    "tps1663": ("v2/vendor/ti/held/ti-tps1663-slvset9g.pdf", "8f91a0db2daf2da35abd335420ff9f8b4ac9a99c93dac93e215e0a75e9a866fe"),
    "red2_py": ("v2/docs/records/hc2/pwr_red2.py", "5790bc7e444bebc4b6b7b6616c4641dfe602185631992d19aeb223eb51e9feec"),
    "budget_py": ("v2/docs/records/rv-pwr/pwr_budget.py", "469d0820b046ef6ff5aceadf422b4166de3d6a02bc50fa5b0c3644704f0f9556"),
    "loopdesign": ("v2/docs/records/l4e8/inputs/recovered/loop_design-r4a-fixup-A-1024.py", "fe0d946bc020d4b68c3a4e417b4c2e7dfd98eeabd2352ff849de4ef0d781d7da"),
    "zk": ("v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf", "5455014606c0b676ca1df345f1969ee1b056403b8ee424bb29245115facda389"),
    "b540c": ("v2/vendor/power/held/diodes-b520c-b560c-ds13012-rev18-2.pdf", "1b1de94df0a7729f4a69a885edd54213594acdce3cd6d4fa072961431ddf71ff"),
    "yageo_rc": ("v2/vendor/passives/yageo-rc-l-series-v12.pdf", "e7dbabb0611925227ccfc429c14c8833a7b1f2c755684444124446f20b22a229"),
    "e2e_por": ("v2/vendor/ti/ti-e2e-1316778-bq25731-chargecurrent-por.html", "96c511cf238d00182bcd82c5e7bdce3d25571c49cbd77f6b57a9171159f0d8c4"),
    "bq25730": ("v2/vendor/ti/held/ti-bq25730-sluse65a.pdf", "e41ef289ce1de377d7b92bce609177d924e149099d9c4424d88f6b21ad57153f"),
    "aons21357": ("v2/vendor/power/held/aos-aons21357-rev2.1-2023-11.pdf", "1a6460e7c63596ca7d48fe1660ee3a3ee48c33d6e345ef41d7c94c21cd7642d9"),
    "bq4050": ("v2/vendor/battery/ti-bq4050.pdf", "2664e33fe6d6ebed3a0f58153d8ba8ce66cb84f07741f6708ae11a224f443f5e"),
    "bq25792": ("v2/vendor/power/bq25792.pdf", "cc451e71123d24d4580bf867fcda0f000b5cf343622b5101f693137ac7be0c15"),
    "sqj403": ("v2/vendor/power/held/vishay-sqj403ep-67109-reva.pdf", "6005efe139fc94e3e855c2beeef8fcaaa5dc71d3c4a6e82f8e8ce82c5506961c"),
    "buk6y10": ("v2/vendor/nexperia/held/nexperia-buk6y10-30p-2020-04-17.pdf", "ba928dfe6a85134423562bd378bdfafafb26d857ba08b50560ce5aacb956da40"),
    "ap63200": ("v2/vendor/diodes/diodes-ap63200-series-buck.pdf", "ef99daa3789d835bc025dfcb4c605c5c2e6d3e7223e86d40b33e6b497ea5a722"),
    "smcj": ("v2/vendor/power/littelfuse-smcj-series-tvs.pdf", "6e610db955ed876306999009c62b242f7de9bb05e2cd9717288a96586a5093ea"),
    "dock_py": ("v2/docs/records/w3de/dock_contacts.py", "acd932cbb9e31f8f0fd4563fc97d7ece21e0ce531e133040afb911da3c513b41"),
    "msmf": ("v2/vendor/power/bourns-mf-msmf-pptc.pdf", "a84b990157dd1d755b5c7a413156ddf8792a3a95cff56f09a95d10754e9e49ed"),
    "arch": ("v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md", "0978b101bb4fc5721e217642338fcd3d3f3be5f37dcf7a88cfa9221118cffb6f"),
}
INPUTS = ["lcsc-C907944-2026-10-02.json", "lcsc-C3847777-2026-10-02.json", "lcsc-C363929-2026-10-02.json",
          "lcsc-C3873338-2026-10-02.json", "jlc-search-c0g-150nf-2026-10-02.json", "murata-reference-sheets-2026-10-02.json",
          "ia-littelfuse-997-mini58v-20251210045250.json",
          "lcsc-C17556513-2026-10-02.json", "lcsc-C2687963-2026-10-02.json", "lcsc-C2985708-2026-10-02.json", "lcsc-C7084461-2026-10-02.json",
          "lcsc-C861872-2026-10-02.json", "lcsc-C97929-2026-10-02.json", "lcsc-C184799-2026-10-02.json", "lcsc-C23107-2026-10-02.json",
          "lcsc-C242138-2026-10-02.json", "lcsc-C242139-2026-10-02.json", "lcsc-C72264-2026-10-02.json", "lcsc-C137025-2026-10-02.json"]
CONS_INPUTS = ["lcsc-C5219071-2026-10-02.json", "lcsc-C2871872-2026-10-02.json", "lcsc-C404364-2026-10-02.json",
               "lcsc-C242138-price-2026-10-02.json", "lcsc-C242139-price-2026-10-02.json", "lcsc-C72264-price-2026-10-02.json",
               "lcsc-C137025-price-2026-10-02.json"]          # the consolidation round's catalogue readings (with prices)
FIX_INPUTS = ["lcsc-C3278350-2026-10-02.json", "lcsc-C3289491-2026-10-02.json"]   # the fix round's FET candidates (with prices)
INPUTS = INPUTS + CONS_INPUTS + FIX_INPUTS + ["nexperia-buk6y10-30p-figure-readings-2026-10-02.json"]
L4E9_COMMIT = "3c09b3daaa48d0a9f16b833b949d7d9ab8ecd496"
GIT_PINS = {
    "l4e9": ("v2/docs/records/l4e9/l4e9_power_path.out", "07d8fb6e828cb15b5589f13983a76bde97c9048ab46ea193c528a28d59a7bbd3"),
    "l4e9_hotswap": ("v2/docs/records/l4e9/apply_gen_sch_e_hotswap.py", "ed228968916764468fada2e8317a908216d5a1e835d81bccb156952ab8397cbb"),
}

# ---- the figures this record sets itself (each named where it is used)
CU_RHO_20 = 0.01724          # ohm mm2 / m, annealed copper at 20 C (ASSUMPTION, a constant, as L4-E9)
CU_ALPHA = 0.00393           # 1/K (ASSUMPTION, a constant, as L4-E9)
CU_CV = 3.45                 # J / (cm3 K), copper's volumetric heat capacity (ASSUMPTION, a constant)
T_COLD = -20.0               # C, REQ-024's cold end, as L4-E9 takes it
AWG14_MM2, AWG12_MM2, AWG16_MM2, AWG18_MM2 = 2.081, 3.309, 1.309, 0.823   # nominal AWG cross-sections (ASSUMPTION, constants)
LEAD_M = 0.5                 # the inside lead, a way (L4-E9's 500 mm, read below for the drawn lead's gauge)
SEL_CABLE_M = 3.05           # SESSION (D-06, final round): the DC pair's run, a construction inside the measured window below
SEL_MM2 = AWG14_MM2          # SESSION (D-06): the class of core that fits a MIL-DTL-38999 size 12 crimp barrel
CONT_CLASS_A = 20.0          # SESSION (D-06): every element of the vehicle entry's interconnect rated at least this, continuous
PLUG_V = 9.0                 # REQ-015's floor, taken at the kit's plug (SESSION, the most demanding reading)
RULE_SRN_V = 14.0            # SESSION (U-04 rule R-b): the charger's own SRN reading under which R-b holds without the gauge's report
STEP_N = 40000               # the start integration's voltage steps (deterministic)
CAP_STACK_PARTS = 2          # SESSION (D-09): a timer capacitor of at most two parts in parallel
# ---- the fix round's own figures (2 October 2026, the focused check cx30's B1 to B5)
T_OUT_HOT = 40.0             # C, REQ-024's +40 C ambient for the outside cable (REQUIREMENT; sun loading not counted, named)
I_PF_TARGET = 900.0          # A, SESSION (D-06, final round): the specified worst stiff-source current, 10 % under F1's 1000 A
U_MEAS = 0.02                # SESSION (D-06): the loop measurement's instrument and fixture uncertainty, of reading
DT_MEAS = 2.0                # K, SESSION (D-06): the conductor temperature's uncertainty when the loop is measured
LOOP_CEIL20 = 0.066          # ohm, SESSION (D-06): the measured loop's actual ceiling at 20 C (copper, the D38999 pair, J_DCIN)
T_RESP = 1.0e-3             # s, ASSUMPTION (dependency round): the time the charger could take to restore VSYS after a step, no battery
K_COLD_HYB = 0.90            # ASSUMPTION: a hybrid polymer can's capacitance at -20 C over its 20 C value (the ZK sheet prints none)
VF_COLD_ADD = 0.10           # V, ASSUMPTION: a Schottky's forward drop at -20 C over its 25 C maximum
BANK_N = 4                   # SESSION (dependency round): the hold-up bank's cans (EEHZK1E471P)
R_CH = 330.0                 # ohm, SESSION: the hold-up bank's charge resistor (RC2512 1 W)
S2_ETA = 0.90                # ASSUMPTION: the slot rail's efficiency (gen_sch_a.py declares 0.90 for +5V_DEV and none for +5V_S2)
SHED_OFF = ("two mixer fans", "QMX USB and HDMI 5 V", "Geiger module", "5G RM520N-GL")   # SESSION (B3): held in the warm-up
HOLDER_R = 0.0010            # ohm, F1's holder (two clips): the 3568 prints nothing (ASSUMPTION)
BOARD_R = 0.0050             # ohm, board E's and board A's copper and the dock's VIN_RAW pins in the loop (ASSUMPTION)
FET_HOT = 1.8                # a MOSFET's RDS(on) at the hot end over its 25 C maximum (ASSUMPTION, for TJ up to about 125 C)
FIX_KNEE_IT, FIX_RLOOP = 1.89, 0.141525   # the fix round's knee and loop (RECORD: checks/astra-check-l4e11-2.md reproduces them)
PIN_ERR = 0.200              # A, the ILIM_HIZ pin's error at R16 10 mOhm (INFERRED by L4-E5 from TI's 0.4 A at 5 mOhm)
NET_TOL = 0.01               # the knee network's error on the pin voltage (ASSUMPTION, L4-E5's 1 %)
KNEE_IT = 1.82               # A board current, SESSION (final round): the flat target, between the warm-up's need and the trip
KNEE_TOP = 7.95              # V of VIN_RAW, SESSION (B3): where the flat target begins to fall; L4-E5's knee slope kept
GUARD_R14_K = 76.8           # kOhm, SESSION (B3): board A R14, the restart guard under the corrected knee
ENTRY = dict(rsns=4.5e-3, rsns_tcr=50e-6, prec=0.001, drift=2 * 50e-6 * 50.0, rset=100.0, riwrn=39.7e3, riscp=3010.0, ctmr=22e-9,
             r1=36.5e3, c1=10e-9, r2=10.0, cbst=1e-6, uv_top=59.0e3, uv_bot=10.0e3, ov_top=332e3, ov_bot=10.0e3,
             inp_top=100e3, inp_bot=39e3, rvs=100.0, cvs=100e-9, cscp=1e-9)   # SESSION (B1): the selected entry's values


def refuse(code, msg):
    sys.stderr.write("l4e11_power: %s; refusing\n" % msg)
    sys.exit(code)


def sha_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def read(key):
    rel, want = PINS[key]
    path = os.path.join(TOP, rel)
    if not os.path.isfile(path):
        refuse(2, "%s is not here (%s)" % (rel, "fetch_held_back.py" if "/held/" in rel else "the tree"))
    if sha_file(path) != want:
        refuse(2, "%s is not the pinned file" % rel)
    return path


def text(key):
    return open(read(key), encoding="utf-8").read()


def git_text(key):
    rel, want = GIT_PINS[key]
    r = subprocess.run(["git", "-C", TOP, "show", "%s:%s" % (L4E9_COMMIT, rel)], capture_output=True)
    if r.returncode != 0:
        refuse(2, "L4-E9's commit %s is not in this repository" % L4E9_COMMIT[:8])
    if hashlib.sha256(r.stdout).hexdigest() != want:
        refuse(2, "%s at %s is not the pinned file" % (rel, L4E9_COMMIT[:8]))
    return r.stdout.decode("utf-8")


_PDF = {}


def pdf_pages(key, layout=False):
    k = (key, layout)
    if k not in _PDF:
        a = ["pdftotext"] + (["-layout"] if layout else []) + [read(key), "-"]
        r = subprocess.run(a, capture_output=True)
        if r.returncode != 0:
            refuse(3, "pdftotext could not read %s" % PINS[key][0])
        _PDF[k] = r.stdout.decode("utf-8", "replace").split("\f")
    return _PDF[k]


def flat(t):
    return " ".join(t.split())


def find(key, pat, what, layout=False, flags=0):
    """The first page (1-based) whose text matches; the match. Flat text unless layout is asked."""
    for i, t in enumerate(pdf_pages(key, layout)):
        m = re.search(pat, t if layout else flat(t), flags)
        if m:
            return i + 1, m
    refuse(3, "%s not found in %s" % (what, PINS[key][0]))


def need(t, pat, what, flags=0):
    m = re.search(pat, t, flags)
    if not m:
        refuse(3, "%s not found" % what)
    return m


def f(m, i=1):
    return float(m.group(i).replace(",", ""))


def fmt(x, nd=3):
    s = ("%." + str(nd) + "f") % x
    return s.rstrip("0").rstrip(".") if "." in s else s


def netlist_nodes(t, name):
    m = re.search(r'\(net \(code "?\d+"?\) \(name "/?%s"\)(.*?)\n\s*\(net ' % re.escape(name), t, re.S)
    if not m:
        refuse(3, "net %s not in the netlist" % name)
    return re.findall(r'\(node \(ref "?([^" )]+)"?\) \(pin "?([^" )]+)"?', m.group(1))


def netlist_value(t, ref):
    m = re.search(r'\(comp \(ref "?%s"?\)\s*\(value "([^"]*)"' % re.escape(ref), t)
    if not m:
        refuse(3, "%s not in the netlist" % ref)
    return m.group(1)


def soa_lines():
    """CSD19532Q5B Figure 10 (SLPS414B p.6) read from the sheet's vector drawing, L4-E9's method (its soa_lines(), the
    same frame, legend and consistency checks), so the 10 ms, 1 ms and DC lines are TI's own coordinates."""
    pdf = read("csd19532")
    svg = subprocess.run(["pdftocairo", "-svg", "-f", "6", "-l", "6", pdf, "-"], capture_output=True).stdout.decode("utf-8", "replace")
    tr = "matrix(0.097966,0,0,-0.097966,64.4,445.1)"
    paths = []
    for m in re.finditer(r"<path[^>]*>", svg):
        # poppler 22 writes the stroke as a style property and "rgb(0%,0%,0%)", "matrix(a,b,...)"; poppler 24 writes a stroke
        # attribute and puts a space after each comma: the reader takes both, the path coordinates being the same
        t = re.sub(r",\s+", ",", m.group(0))
        st = re.search(r'stroke(?::|=")(rgb\([^)]*\))', t)
        if tr not in t or not st:
            continue
        pts = [(float(a), float(b)) for a, b in re.findall(r"[ML] ([-\d.]+) ([-\d.]+)", re.search(r' d="([^"]*)"', t).group(1))]
        paths.append((st.group(1), pts))
    frames = [p for c, p in paths if c == "rgb(0%,0%,0%)" and len(p) == 5 and p[0] == p[-1]]
    if not frames:
        refuse(3, "Figure 10's frame")
    fr = max(frames, key=lambda q: (max(a for a, _ in q) - min(a for a, _ in q)) * (max(b for _, b in q) - min(b for _, b in q)))
    x0, x1 = min(q[0] for q in fr), max(q[0] for q in fr)
    y0, y1 = min(q[1] for q in fr), max(q[1] for q in fr)
    lv = lambda x: -1.0 + 4.0 * (x - x0) / (x1 - x0)
    li = lambda y: -1.0 + 5.0 * (y - y0) / (y1 - y0)
    idm = [p for c, p in paths if c == "rgb(0%,0%,0%)" and len(p) == 3]
    if not idm or abs(10 ** li(idm[0][0][1]) - 400.0) > 4.0 or abs(10 ** lv(idm[0][1][0]) - 100.0) > 1.0:
        refuse(3, "Figure 10's IDM and 100 V boundary")
    txt = pdf_pages("csd19532", True)[5]
    rows = [re.findall(r"(10us|100us|1ms|10ms|DC)\b", ln) for ln in txt.splitlines() if re.search(r"\b(10us|100us)\b", ln)]
    if len(rows) != 2:
        refuse(3, "Figure 10's legend")
    legend = sorted(((p[0][1], p[0][0], c) for c, p in paths if len(p) == 2 and p[0][1] == p[1][1] and c != "rgb(0%,0%,0%)"
                     and 100 < p[1][0] - p[0][0] < 150 and p[0][1] > 1200), key=lambda q: (-q[0], q[1]))
    labels = rows[0] + rows[1]
    if len(legend) < len(labels):
        refuse(3, "Figure 10's legend segments")
    out = {}
    for lab, (_y, _x, col) in zip(labels, legend):
        cands = [p for c, p in paths if c == col and len(p) >= 3 and abs(10 ** lv(p[-1][0]) - 100.0) < 1.0]
        if len(cands) != 1:
            refuse(3, "Figure 10's %s line" % lab)
        out[lab] = [(lv(x), li(y)) for x, y in cands[0]]
    return out


def soa_at(line, vds):
    lx = math.log10(vds)
    for (xa, ya), (xb, yb) in zip(line, line[1:]):
        if xa <= lx <= xb:
            return 10 ** (ya + (yb - ya) * (lx - xa) / (xb - xa))
    refuse(3, "Figure 10 has no segment at %s V" % vds)


# ============================================================================================ the computation
def compute():
    R = {}
    T = {k: text(k) for k in ("reqs", "rules", "testplan", "hwfw", "panel", "assembly", "gen_a", "gen_e", "gen_p", "net_a",
                              "net_e", "packprot", "primcfg", "chain", "l4e5", "budget", "red2", "ecss")}
    for k in ("bq25731", "sluuaq3a", "csd17570", "cell", "lm5069", "csd19532", "d38999", "vh", "xt60", "keystone", "lapp",
              "alpha", "lm5176", "srf1260", "yageo", "fuse997", "mur104", "mur683", "bq25798", "lm74700", "tps4811", "csd19536", "tps1663",
              "bq25730", "aons21357", "bq4050", "bq25792", "sqj403", "buk6y10", "ap63200", "smcj", "dock_py", "arch", "msmf"):
        read(k)
    L9 = git_text("l4e9")
    R["inputs"] = [(k, PINS[k][0], sha_file(os.path.join(TOP, PINS[k][0]))) for k in PINS]
    R["git_inputs"] = [(k, "%s:%s" % (L4E9_COMMIT[:8], GIT_PINS[k][0]), GIT_PINS[k][1]) for k in GIT_PINS]
    R["filed"] = []
    for name in INPUTS:
        p = os.path.join(TOP, REC, "inputs", name)
        if not os.path.isfile(p):
            refuse(2, "inputs/%s is not filed" % name)
        R["filed"].append((name, sha_file(p)))
    J = {n: json.load(open(os.path.join(TOP, REC, "inputs", n), encoding="utf-8")) for n in INPUTS}

    # ------------------------------------------------------------------ 1. what the requirements demand (quoted)
    reg = yaml.safe_load(T["reqs"])
    recs = {r["id"]: r for r in reg["records"] if "id" in r}
    q = lambda s: flat(str(s))
    R["req015"] = (q(recs["REQ-015"]["statement"]), q(recs["REQ-015"]["acceptance"]))
    R["req014_clause"] = need(q(recs["REQ-014"]["statement"]), r"missions longer than the pack rely on vehicle or solar input \(D-06\)", "REQ-014's input clause").group(0)
    R["req024_clause"] = need(q(recs["REQ-024"]["statement"]), r"a pack cold-soaked below about -10 C at the cells is not started from \(shore or vehicle power, or warming, first; D-02d\)", "REQ-024's D-02d clause").group(0)
    R["req046"] = q(recs["REQ-046"]["statement"])
    R["req046_hold"] = need(q(recs["REQ-046"]["acceptance"]), r"the bridge's own hold clears above 3 C \(PANEL\.md section 10\)", "REQ-046's hold").group(0)
    R["req077_clause"] = need(q(recs["REQ-077"]["acceptance"]), r"the charge held by the charger's CHRG_INHIBIT with the charger still carrying the kit on shore", "REQ-077's shore clause").group(0)
    R["req072_obl"] = recs["REQ-072"].get("obligation")
    R["req072_clause"] = need(q(recs["REQ-072"]["acceptance"]), r"after a permitted pack cutoff the remaining supply carries the loads, D-26", "REQ-072's cutoff clause").group(0)
    R["e4o"] = need(flat(T["testplan"]), r"started warm or from shore or vehicle input \(D-02d: a cold start from the pack below about -10 C cell temperature is out of scope; inside the envelope, so an acceptance test\)", "TEST-PLAN E4-O's start").group(0)
    names_state = lambda s: bool(re.search(r"\bPS-[A-Z]", s))
    ob = lambda rid: recs[rid].get("obligation") or "MANDATORY"
    R["req_rows"] = [
        ("REQ-015", ob("REQ-015"), "9 to 36 V, where measured not stated", names_state(" ".join(R["req015"])), "operates and charges; the pack's state not named"),
        ("REQ-014", ob("REQ-014"), "none", False, "missions longer than the pack rely on vehicle or solar input"),
        ("REQ-024 (D-02d)", ob("REQ-024"), "shore or vehicle (9 to 36 V by REQ-015)", names_state(R["req024_clause"]), "a cold-soaked pack: both FETs open below -9 C, the kit started on the source"),
        ("REQ-046", ob("REQ-046"), "none", names_state(R["req046"]), "below 0 C the pack warmed by its heater before charge; the bridge's hold clears above 3 C"),
        ("REQ-077", ob("REQ-077"), "on shore", names_state(R["req077_clause"]), "the charge held by CHRG_INHIBIT while the charger carries the kit (a pack present)"),
        ("REQ-072", ob("REQ-072"), "solar", True, "after a permitted pack cutoff the remaining supply carries the loads (PS-IDLE-SPEC is the objective's profile)"),
    ]
    R["no_mandatory_state"] = not any(st for rid, ob, v, st, _ in R["req_rows"] if ob != "OBJECTIVE")
    if not R["no_mandatory_state"]:
        refuse(4, "a mandatory requirement names a load state for source-only operation; this record's reading is wrong")

    # ------------------------------------------------------------------ 2. the charger with no usable pack (SLUSE66A)
    B = {}
    B["nobatfet"] = find("bq25731", r"No battery MOSFET for saving cost", "no battery MOSFET")[0]
    B["powerup"] = find("bq25731", r"Power up sequence when the charger is powered up from VBUS:.*?Converter powers up\.", "9.3.1", flags=re.S)[0]
    B["fig104"] = find("bq25731", r"2-cell without battery.*?Figure 10-4\. Power Up From 20 V.*?Figure 10-5\. Power Up From 5 V", "Figures 10-4 and 10-5", flags=re.S)[0]
    p, m = find("bq25731", r"When CHRG_OK goes HIGH, the system is powered from adapter through the charger\. When adapter is removed, the system is connected to battery\.", "section 11")
    B["sec11"], B["sec11_text"] = p, m.group(0)
    p, m = find("bq25731", r"CHRG_OK is an active HIGH open drain indicator\. It indicates the charger is in normal operation when the following conditions are valid: (.*?) 9\.3\.5", "9.3.4")
    B["chrgok"], B["chrgok_text"] = p, flat(m.group(1).replace("\u2022", " "))
    if re.search(r"batter", B["chrgok_text"], re.I):
        refuse(4, "CHRG_OK's conditions name the battery")
    p, m = find("bq25731", r"the charger decreases the charge current to provide priority to the system load\..*?If the system load keeps increasing after the charge current drops down to zero, the system voltage starts to drop\. As the system voltage drops below the battery voltage, the battery will discharge to supplement the heavy system load\.", "9.3.17", flags=re.S)
    B["dpm"] = p
    p, m = find("bq25731", r"4S\s+75%\s+([\d.]+) V\s+([\d.]+) V\s+([\d.]+) V\s+([\d.]+) V", "Table 9-2's 4S row", layout=True)
    B["t92"], B["cv4s"], B["sysovp4s"], B["vsysmin4s"] = p, f(m, 1), f(m, 2), f(m, 3)
    p, m = find("bq25731", r"CELL\(≥2 S\),VSRN < VSYS_MIN\s+(\d+)\s+mA", "ICLAMP", layout=True)
    B["iclamp_p"], B["iclamp"] = p, f(m) / 1000.0
    p, m = find("bq25731", r"BATOVP rising condition is triggered: if charge is enabled \(charge current is not 0A\) converter should shut down with both HS MOSFET and LS MOSFET turned off; if charge is disabled the converter should keep operating without disturbance", "9.3.21.5")
    B["batovp"] = p
    p, m = find("bq25731", r"the charger can enter HIZ mode \(converter shuts off\) when ILIM_HIZ pin voltage is below ([\d.]+) V", "9.3.8")
    B["hiz_p"], B["hiz_v"] = p, f(m)
    p, m = find("bq25731", r"when VSYS is lower than ([\d.]+) V, there is 2-ms deglitch time, the IIN_DPM is set to 0\.5 A by the charger itself\. After 2-ms deglitch time, the charger should shut down and latched off\.", "9.3.21.8")
    B["uvp_p"], B["uvp_v"] = p, f(m)
    p, m = find("bq25731", r"Overall (\d+)-.F effective capacitance on VSYS net is necessary \(POSCAP is preferred\)", "10.1")
    B["csys_p"], B["csys_uf"] = p, f(m)
    p, m = find("bq25731", r"0b: Enable Charge <default at POR>\s+1b: Inhibit Charge", "CHRG_INHIBIT", flags=re.S)
    B["inhibit_p"] = p
    p, m = find("bq25731", r"host terminates charge by setting CHRG_INHIBIT bit to 1b, or setting ChargeCurrent\(\) to zero", "9.4.1")
    B["term_p"] = p
    p, m = find("bq25731", r"Auto Wakeup Enable When this bit is HIGH, if the battery is below VSYS_MIN , the device should automatically enable (\d+)-mA charging current for (\d+) mins\.(.*?)0b: Disable <default at POR>", "AUTO_WAKEUP_EN")
    if len(m.group(3)) > 400:
        refuse(3, "AUTO_WAKEUP_EN's default is not on its own row")
    B["wake_p"], B["wake_ma"], B["wake_min"] = p, f(m, 1), f(m, 2)
    R["B"] = B
    # the netlists' facts behind it
    ga = T["gen_a"]
    m = need(ga, r'r\("R26", "([\d.]+)k 1% \(CELL_BATPRESZ: 4S, (\d+) percent of VDDA\)", "CH_VDDA", "CH_CELL", lcsc="C\d+"\); r\("R27", "([\d.]+)k 1%"', "the cell-count strap")
    R["strap"] = (f(m, 1), f(m, 3), 100.0 * f(m, 3) / (f(m, 1) + f(m, 3)))
    need(ga, r'r\("R17", "5mOhm 1% 2512 \(RSR, charge current sense\)", "VBAT", "CELL_FUSED", "RS2512"\)', "R17 between VSYS and the pack")
    need(ga, r'part\("Q6", "Transistor_FET", "2N7002", "2N7002: CHG_INHIBIT high = ILIM_HIZ low = charger in HiZ", "SOT23", \{"1": "CHG_INHIBIT", "2": "GND", "3": "CHG_ILIM"\}\)', "Q6 on ILIM_HIZ")
    ge = T["gen_e"]
    need(ge, r'part\("Q8", "Transistor_FET", "2N7002", "2N7002: SHORE_INHIBIT high pulls UVLO low = input off \(1 G, 2 S, 3 D\)", "SOT23", \{"1": "SHORE_INHIBIT", "2": "GND_V", "3": "HS_UVLO"\}\)', "Q8 on the hot swap's UVLO")
    gp = T["gen_p"]
    need(gp, r'27: "PACK_F", 28: "DSG_G", 29: "GND", 30: "NC", 31: "CHG_G"', "board P's gauge with PCHG not connected")
    need(gp, r'pfet5\("Q2", "CSD17570Q5B 30 V N-FET, discharge switch", "DSG_G", "SW", "PACK_P"', "Q2 the discharge FET")
    need(gp, r'r\("R7", "1k", "PACK_P", "VCC_F"\)', "the gauge's VCC from the pack terminal")
    R["fwc08"] = need(flat(T["hwfw"]), r"\| FW-C08 \| (.*?) \| (Boot low; assert on the bridge's request when the pack reads below 0 C and clear above 3 C, or when the operator sets \"no charge\") \|", "FW-C08").group(2)
    R["fwa14"] = need(flat(T["hwfw"]), r"\| FW-A14 \| (CHG_INHIBIT .*?) \| (Held low \(charger enabled\) at power-up; asserted only by firmware) \|", "FW-A14").group(2)
    R["panel10"] = need(flat(T["panel"]), r"high = the shore and vehicle inputs are held off at the front end, so nothing charges\.", "PANEL.md section 10").group(0)
    R["panel10_cold"] = need(flat(T["panel"]), r"The bridge asks the controller to assert it when the pack temperature \(.*?\) is below 0 C, when the operator sets \"no charge\", and clears it with hysteresis \(charge again above 3 C\)\.", "PANEL.md's cold hold").group(0)
    # the pack (SLUUAQ3A, the pack's own tables)
    P = {}
    P["cuv_p"] = find("sluuaq3a", r"2\.2 Cell Undervoltage Protection.*?Trip Min cell voltage1\.\.4 ≤ CUV:Threshold for CUV:Delay duration SafetyAlert\(\)\[CUV\] = 0 SafetyStatus\(\)\[CUV\] = 1 BatteryStatus\(\)\[FD\] = 1,\[TDA\] = 0 OperationStatus\(\)\[XDSG\] = 1 Condition 1", "2.2 CUV trip", flags=re.S)[0]
    P["xdsg_p"] = find("sluuaq3a", r"SafetyStatus\(\)\[OCD1\] or \[OCD2\] or \[CUV\] or \[CUVC\] or \[AOLD\] or \[AOLDL\] or \[ASCD\] or \[ASCDL\] or \[UTD\] = 1", "4.12 XDSG")[0]
    P["xchg_p"] = find("sluuaq3a", r"SafetyStatus\(\)\[UTC\] = 1 OR", "4.12 XCHG")[0]
    P["pchg_p"] = find("sluuaq3a", r"Depending on the FET Options\[PCHG_COMM\] settings, the external precharge FET or CHG FET can be used in PRECHARGE mode", "4.9")[0]
    P["pchgbit_p"] = find("sluuaq3a", r"PCHG_COMM \(Bit 0\): Precharge FET selection 1 = CHG FET 0 = PCHG FET \(default\)", "14.2.1.1")[0]
    pc = flat(T["primcfg"])
    need(pc, r"\*\*0x3D\*\*: PACK_FUSE 0, SLEEPCHG 0, CHGFET 1, CHGIN 1, CHGSU 1, OTFET 1, PCHG_COMM 1", "the image's FET Options")
    P["shutdown_mv"] = f(need(pc, r"\| Shutdown Voltage \(14\.5\.2\.1\) \| 1750 mV \| (\d+) mV \|", "the image's Shutdown Voltage"))
    pp = yaml.safe_load(T["packprot"])
    fn = {x["id"]: x for x in pp["functions"]}
    P["cuv"] = float(fn["CELL_UNDER_VOLTAGE"]["threshold"]["value"])
    P["cuv_rec"] = float(re.search(r"([\d.]+) V", fn["CELL_UNDER_VOLTAGE"]["threshold"]["recovery"]).group(1))
    P["utd"] = float(fn["DISCHARGE_TEMPERATURE_WINDOW"]["threshold"]["low"])
    P["utc"] = float(fn["CHARGE_TEMPERATURE_WINDOW"]["threshold"]["low"])
    P["pre_a"] = float(fn["PRECHARGE_WINDOW"]["threshold"]["current_a"])
    P["pre_hi"] = float(fn["PRECHARGE_WINDOW"]["threshold"]["high"])
    P["cells"] = 4
    # Q2's body diode (CSD17570Q5B, SLPS...: page 3 rows)
    p, m = find("csd17570", r"VSD\s+Diode Forward Voltage\s+ISD = (\d+) A, VGS = 0 V\s+([\d.]+)\s+([\d.]+)\s+V", "Q2's VSD", layout=True)
    P["vsd_p"], P["vsd_i"], P["vsd_max"] = p, f(m, 1), f(m, 3)
    p, m = find("csd17570", r"RθJA\s+Junction-to-Ambient Thermal Resistance \(1\) \(2\)\s+(\d+)", "Q2's RthetaJA", layout=True)
    P["rja_p"], P["rja"] = p, f(m)
    p, m = find("csd17570", r"Operating Junction and.{0,600}?[\u2013-]55 to (\d+)\s*°C", "Q2's TJ", layout=True, flags=re.S)
    P["tj_max"] = f(m)
    P["q2"] = [(i, i * P["vsd_max"], i * P["vsd_max"] * P["rja"]) for i in (B["iclamp"], 3.0)]
    # the cell maker's precharge rows
    p, m = find("cell", r"Pre-charging voltage range\*+\s+(1\.0)V ~ (3\.0)V", "the precharge window", layout=True)
    P["cell_p"], P["pre_win"] = p, (f(m, 1), f(m, 2))
    m = find("cell", r"Current range of Pre-charging\s+(0\.1)C ~ (0\.5)C", "the precharge current range", layout=True)[1]
    P["pre_c"] = (f(m, 1), f(m, 2))
    m = find("cell", r"Charge : 0\.5C\(([\d,]+)mA\)", "the cell's C", layout=True)[1]
    P["c_a"] = f(m) / 1000.0 / 0.5
    P["clamp_c"] = B["iclamp"] / 3.0 / P["c_a"]
    P["cc_c"] = 3.0 / 3.0 / P["c_a"]
    # VSYS with the pack at its cutoff, and below it
    P["vsys_cuv"] = (P["cells"] * P["cuv"], P["cells"] * P["cuv"] + P["vsd_max"])
    P["vsys_shut"] = (P["cells"] * P["shutdown_mv"] / 1000.0, P["cells"] * P["shutdown_mv"] / 1000.0 + P["vsd_max"])
    P["release_stack"] = B["vsysmin4s"] - P["vsd_max"]            # SRN reaches VSYS_MIN with the stack this far up (worst VSD)
    P["window"] = (P["release_stack"] / P["cells"], P["cuv_rec"])
    P["rb_stack"] = RULE_SRN_V - P["vsd_max"]                    # with SRN at R-b's threshold the stack is at least this
    P["rb_imbalance"] = P["rb_stack"] / P["cells"] - P["cuv_rec"]   # a cell this far under the average is still covered
    R["P"] = P
    R["cv_max"] = f(need(L9, r"ChargeVoltage at most ([\d.]+) V", "the written ChargeVoltage's maximum"))

    # ------------------------------------------------------------------ 3. the source envelope at VIN_RAW and at the plug
    l5 = T["l4e5"]
    rows = {}
    for m in re.finditer(r"^\s+([\d.]+) V \|\s+([\d.]+) A\s+\|.*?\|\s+([\d.]+) V \| ([\d.]+) / ([\d.]+) A \| ([\d.]+) A \| ([\d.]+) A", l5, re.M):
        rows[float(m.group(1))] = dict(line=f(m, 2), pin_lo=f(m, 4), pin_hi=f(m, 5), hmax=f(m, 6), fe=f(m, 7))
    if sorted(rows) != [9.0, 12.0, 24.0, 36.0]:
        refuse(3, "L4-E5's envelope table")
    E = {"rows": rows}
    E["floor_min"] = f(need(l5, r"At the 9 V floor U3 still gets at least ([\d.]+) A", "L4-E5's floor minimum"))
    E["slope"] = f(need(l5, r"Its line: 1\.000 V \+ ([\d.]+) V/V x VIN_RAW at R16 10 mOhm", "L4-E5's line"))
    E["k0"] = f(need(l5, r"zero-current target, the pin at 1\.0 V .*?: VIN_RAW ([\d.]+) V \(", "the knee's zero"))
    E["hiz_lo"] = f(need(l5, r"So U3 is certainly in HIZ below ([\d.]+) V of VIN_RAW", "the HIZ entry"))
    E["oth"] = f(need(l5, r"VBUS20's other loads ([\d.]+) A\)", "VBUS20's other loads"))
    E["vb_nom"] = f(need(l5, r"VBUS20 nominal ([\d.]+) V", "VBUS20 nominal"))
    E["eta_fe"] = f(need(l5, r"the front end at ([\d.]+) and\s+VBUS20", "the front end's efficiency"))
    m = need(L9, r"per source at VBAT \(U3 ([\d.]+), VBUS20 ([\d.]+) V top, ([\d.]+) V lowest\): vehicle at 9 V ([\d.]+) to ([\d.]+) W \(the entry itself bounds 9 V at ([\d.]+) W\); at 12 V up to ([\d.]+) W; at 24 V up to ([\d.]+) W", "L4-E9's per-source line")
    E["eta_u3"], E["vb_top"], E["vb_low"] = f(m, 1), f(m, 2), f(m, 3)
    E["l9"] = dict(min9=f(m, 4), max9=f(m, 5), entry9=f(m, 6), max12=f(m, 7), max24=f(m, 8))
    m = need(L9, r"IIN_HOST ([\d.]+) A \(minimum ([\d.]+) A, maximum ([\d.]+) A board current", "IIN_HOST's band")
    E["iin_min"], E["iin_max"] = f(m, 2), f(m, 3)
    m = need(L9, r"the entry ([\d.]+) to ([\d.]+) A \(basis", "the entry's limit")
    E["entry"] = (f(m, 1), f(m, 2))
    E["r16_tol"] = f(need(ga, r'r\("R16", "10mOhm (\d+)% 2512', "R16's tolerance")) / 100.0
    env = {}
    for v in (9.0, 12.0, 24.0, 36.0):
        lo = (E["floor_min"] if v == 9.0 else rows[v]["pin_lo"]) / (1 + E["r16_tol"])
        lo = min(lo, E["iin_min"])
        hi = rows[v]["hmax"]
        env[v] = dict(board_lo=lo, board_hi=hi, w_lo=lo * E["vb_low"] * E["eta_u3"], w_hi=hi * E["vb_top"] * E["eta_u3"])
    E["env"] = env
    E["entry9_w"] = E["entry"][0] * 9.0 * E["eta_fe"] * E["eta_u3"]
    # the load states (the budget's battery-terminal figures, taken at VBAT)
    bu = T["budget"]
    st = {}
    for name in ("PS-RED", "PS-IDLE-SPEC", "PS-TYP"):
        m = need(bu, r"^%s\s+load\s+[\d.]+ \| battery\s+([\d.]+) /\s+([\d.]+) /\s+([\d.]+)" % re.escape(name), name, re.M)
        st[name] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(bu, r"PS-RED plus the heater \(cold overlay\), lid closed \{\"battery_W_plan\": ([\d.]+)", "PS-RED with the heater")
    st["PS-RED with the heater"] = (None, f(m), None)
    rd = T["red2"]
    m = need(rd, r'"PS-IDLE-SPEC, link cards held off, heater on": \{\s+"battery_W_plan": ([\d.]+)', "the cold idle with heater")
    st["PS-IDLE-SPEC cold, heater on"] = (None, f(m), None)
    m = need(rd, r'"warm-up: PS-TYP, link cards and SDR held off, heater on, three modules loaded": \{\s+"battery_W_plan": ([\d.]+)', "the cold warm-up")
    st["the cold warm-up (CONOPS 4c)"] = (None, f(m), None)
    E["states"] = st
    cls = {}
    for name, (lo, plan, hi) in st.items():
        for v in (9.0, 12.0, 24.0, 36.0):
            e = env[v]
            cls[(name, v)] = "carried at every corner" if plan <= e["w_lo"] else ("only above the line's minimum" if plan <= e["w_hi"] else "not carried")
    E["cls"] = cls
    # the dead pack's charge share inside the envelope
    E["dead_charge_w"] = B["iclamp"] * P["vsys_cuv"][1]
    # the entry's UVLO band (U4-F2)
    l69 = flat("".join(pdf_pages("lm5069", True)))
    m = need(l69, r"UVLOTH UVLO threshold ([\d.]+) ([\d.]+) ([\d.]+) V UVLOHYS UVLO hysteresis current UVLO = 1 V (\d+) (\d+) (\d+) µA", "LM5069 UVLO rows")
    uv = (f(m, 1), f(m, 2), f(m, 3)); hy = (f(m, 4) * 1e-6, f(m, 5) * 1e-6, f(m, 6) * 1e-6)
    E["uvlo_page"] = find("lm5069", r"UVLOTH\s+UVLO threshold", "the UVLO row", layout=True)[0]
    m = need(ge, r'r\("R20", "(\d+)k (\d+)%", "DC_P", "HS_UVLO"\); r\("R21", "([\d.]+)k (\d+)% \(UVLO: 9 V\)", "HS_UVLO", "GND_V"\)', "R20 and R21")
    E["uv_rows"], E["hy_rows"] = uv, hy
    E["r20"], E["r21"] = f(m, 1) * 1e3, f(m, 3) * 1e3            # the corrected thresholds (Equations 38 to 40) are entry_round's
    # the 9 V at the kit's plug (U4-F3): the kit's own series resistance
    m = need(L9, r"the kit's cable \(([\d.]+) m of ([\d.]+) mm2 a way\) and lead \((\d+) mm of AWG (\d+)\)\s+give ([\d.]+) Ohm at 20 C and ([\d.]+) Ohm at -20 C, so a stiff source drives at most ([\d.]+) A", "L4-E9's cable", re.S)
    E["cable_drawn"] = dict(m=f(m, 1), mm2=f(m, 2), lead_mm=f(m, 3), awg=int(m.group(4)), r20=f(m, 5), rcold=f(m, 6), ipf=f(m, 7))
    srf = flat(pdf_pages("srf1260", True)[0])
    m = need(srf, r"SRF1260-1R5Y 1\.5 ±30 ([\d.]+) ([\d.]+) ([\d.]+) 6 ±30 ([\d.]+) ([\d.]+) ([\d.]+)", "SRF1260-1R5Y's row")
    E["l2_dcr"] = f(m, 4)
    c19 = flat(pdf_pages("csd19532", True)[2])
    m = need(c19, r"VGS = 10 V, ID = 17 A ([\d.]+) ([\d.]+) m", "CSD19532Q5B RDS(on)")
    E["q_rds"] = f(m, 2) * 1e-3
    fz = flat("".join(pdf_pages("fuse997", True)))
    m = need(fz, r"0997010_ 10 (\d+) (\d+) ([\d.]+) (\d+)", "the 0997 10 A ratings row")
    E["f1_test_mm2"], E["f1_rcold"], E["f1_i2t"] = f(m, 1), f(m, 3) * 1e-3, f(m, 4)
    E["r_e"] = E["l2_dcr"] + 0.010 * (1 + 0.01) + 2 * E["q_rds"] + E["f1_rcold"]
    sel_r20 = (2 * SEL_CABLE_M + 2 * LEAD_M) * CU_RHO_20 / SEL_MM2
    E["r_plug"] = {"drawn": E["cable_drawn"]["r20"] + E["r_e"], "selected": sel_r20 + E["r_e"]}

    def line_board(v):                                     # H3's nominal target (L4-E5): the line from 9 V, the knee below
        if v >= 9.0:
            return E["slope"] / (40 * 0.010) * v
        if v <= E["k0"]:
            return 0.0
        return E["slope"] / (40 * 0.010) * 9.0 * (v - E["k0"]) / (9.0 - E["k0"])

    def fe_in(board, v):
        return (board + E["oth"]) * E["vb_nom"] / (E["eta_fe"] * v)
    plug = {}
    for k, rr in E["r_plug"].items():
        lo, hi = E["k0"], PLUG_V
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if PLUG_V - mid > fe_in(line_board(mid), mid) * rr:
                lo = mid
            else:
                hi = mid
        v = 0.5 * (lo + hi)
        b = line_board(v)
        plug[k] = dict(r=rr, vin=v, board=b, w=b * E["vb_nom"] * E["eta_u3"], knee_top=PLUG_V - rows[9.0]["fe"] * rr)
    E["plug"] = plug
    E["line9_nom_w"] = line_board(9.0) * E["vb_nom"] * E["eta_u3"]
    R["E"] = E

    # ------------------------------------------------------------------ 4. the comparison's own figures
    C = {}
    C["pack_peak"] = f(need(ga, r'_intent\.rail\("VBAT", [\d.]+, [\d.]+, ([\d.]+), "R17"', "VBAT's declared peak"))
    C["batfet_w_per_mohm_18a"] = C["pack_peak"] ** 2 * 1e-3
    C["idle_a"] = st["PS-IDLE-SPEC"][1] / 14.4
    C["batfet_w_per_mohm_idle"] = C["idle_a"] ** 2 * 1e-3
    C["pre_i_01c"] = P["pre_c"][0] * P["c_a"] * 3
    C["pre_r_01c"] = (B["cv4s"] - P["vsys_shut"][0]) / C["pre_i_01c"]
    C["pre_w_01c"] = (B["cv4s"] - P["vsys_shut"][0]) * C["pre_i_01c"]
    C["pre_r_clamp"] = (B["cv4s"] - P["vsys_shut"][0]) / B["iclamp"]
    C["pre_w_clamp"] = (B["cv4s"] - P["vsys_shut"][0]) * B["iclamp"]
    C["pre_w_cuv_01c"] = (B["cv4s"] - P["vsys_cuv"][0]) ** 2 / C["pre_r_01c"]
    C["nvdc_p"] = find("bq25798", r"It uses NVDC power path management, regulating the system not dropping below a configurable minimum system voltage\.", "BQ25798's NVDC")[0]
    p_, m = find("bq25798", r"RMS discharge current \(continuously\)\s+(\d+)\s+A", "BQ25798's battery FET RMS", layout=True)
    C["bq98_rms"], C["bq98_p"] = f(m), p_
    C["bq98_pk"] = f(find("bq25798", r"Peak discharge current \(upto 1 sec\)\s+(\d+)\s+A", "BQ25798's battery FET peak", layout=True)[1])
    R["C"] = C

    # ------------------------------------------------------------------ 5. the owner-question test (U-04)
    F = {}
    m = need(fz, r"10A 10 10 ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)", "the 0997 10 A derating row")
    F["der"] = dict(zip((-40, -20, 0, 20, 40, 60, 80, 100), (10.0, 10.0, f(m, 1), f(m, 2), f(m, 3), f(m, 4), f(m, 5), f(m, 6))))
    F["air_hot"] = f(need(L9, r"inside air ([\d.]+) / ([\d.]+) C \(lid open / closed\)", "the hottest inside air"), 2)
    col = [c for c in sorted(F["der"]) if c >= F["air_hot"]][0]
    F["f_col"], F["f_hot_a"] = col, F["der"][col]
    F["cap9_hot_w"] = F["f_hot_a"] * 9.0 * E["eta_fe"] * E["eta_u3"]
    F["cap9_cold_w"] = F["der"][0] * 9.0 * E["eta_fe"] * E["eta_u3"]
    F["cap9_interconnect_w"] = CONT_CLASS_A * 9.0 * E["eta_fe"] * E["eta_u3"]
    m = need(fz, r"15A 15 15 (\d+) (\d+) (\d+) (\d+) (\d+) ([\d.]+)", "the 0997 15 A derating row")
    F["der15_hot"] = f(m, 5)
    F["cap9_15a_hot_w"] = F["der15_hot"] * 9.0 * E["eta_fe"] * E["eta_u3"]
    F["over_hot"] = [(n, pl) for n, (lo, pl, hi) in st.items() if pl > F["cap9_hot_w"] and "cold" not in n and "warm-up" not in n]
    F["cold_over"] = [(n, pl) for n, (lo, pl, hi) in st.items() if ("cold" in n or "warm-up" in n) and pl > F["cap9_cold_w"]]
    named_loads = [(rid, st_) for rid, ob, v, st_, _ in R["req_rows"] if ob != "OBJECTIVE" and st_]
    F["owner_question"] = bool(named_loads)
    R["F"] = F

    # ------------------------------------------------------------------ 6. D-06: the weak-source band and the interconnect
    D = {}
    m = need(fz, r"110 360 000 / - 135 ([\d.]+) / (\d+) 200 ([\d.]+) / (\d+) 350 ([\d.]+) / ([\d.]+) 600 ([\d.]+) / ([\d.]+)", "the 0997's time-current rows")
    D["tc"] = [(1.10, 360000.0, None), (1.35, f(m, 1), f(m, 2)), (2.00, f(m, 3), f(m, 4)), (3.50, f(m, 5), f(m, 6)), (6.00, f(m, 7), f(m, 8))]
    D["rating"] = 10.0
    D["band"] = [(D["rating"] * pct, tmax) for pct, _tmin, tmax in D["tc"][1:]]
    D["cont_need"] = D["rating"] * D["tc"][1][0]                       # under 135 % no maximum time is printed
    D["interrupt_v"], D["interrupt_a"] = 58.0, 1000.0
    need(fz, r"Voltage Rating: 58 V DC Interrupting Rating: 1000 A @ 58 V DC", "the 0997's ratings")
    dz = flat("".join(pdf_pages("d38999", True)))
    dz = dz[need(dz, r"CONTACT RATING FOR TV III, HD, JT II, LJT I, SJT", "the D38999 contact table").start():]
    m = need(dz, r" 16 (\d+) (\d+) (\d+) \d+ \d+", "size 16")
    D["c16"], D["c16_mv"] = f(m, 1), f(m, 3)
    m = need(dz, r" 12 (\d+) (\d+) (\d+) \d+ \d+", "size 12")
    D["c12"], D["c12_mv"] = f(m, 1), f(m, 3)
    D["d38999_p"] = find("d38999", r"CONTACT RATING FOR TV III, HD, JT II, LJT I, SJT", "the contact table")[0]
    p, m = find("d38999", r"Series III TV\s+13-4\s+13-8\s+13-26\s+13-32 HD\s+13-35", "the shell 13 arrangements", layout=True)
    D["ins13_p"] = p
    p, m = find("d38999", r"Series III TV\s+17-2\s+17-6\s+17-8", "the shell 17 arrangements", layout=True)
    D["ins17_p"] = p
    asm = flat(T["assembly"])
    need(asm, r"Glenair D38999/26FC4SN plug \(shell 13, insert 13-4, four M39029/56-352 size 16 socket contacts", "the drawn DC plug")
    need(asm, r"Lapp OLFLEX ROBUST 210 4 x 1\.0 \(article 0021917, 6\.6 mm, TPE, outdoor\), or Alpha Wire 25064 \(18 AWG 4C, TPU, 6\.58 mm\); 2 m", "the drawn DC lead")
    vh = find("vh", r"Current rating: (\d+) A", "the VH rating", layout=True)
    D["vh"] = f(vh[1])
    need(flat(pdf_pages("vh", True)[0]), r"When using AWG #16 with the standard type header", "the VH condition")
    D["vh_max_awg"] = int(need(flat(pdf_pages("vh", True)[0]), r"Conductor size/ AWG #(\d+) to AWG #(\d+)", "the VH conductor range").group(2))
    xt = flat(pdf_pages("xt60", True)[0])
    D["xt60"], D["xt60_inst"] = f(need(xt, r"额定电流 (\d+)A", "XT60 rated")), f(need(xt, r"瞬时电流 (\d+)A", "XT60 instantaneous"))
    D["xt60_awg"] = int(need(xt, r"推荐线规 (\d+)AWG", "XT60 wire").group(1))
    ks = flat(subprocess.run(["pdftotext", read("keystone"), "-"], capture_output=True).stdout.decode("utf-8", "replace"))
    m = need(ks, r"CAT\. NO\. 3568 HORIZONTAL FUSE ENTRY ® For Littelfuse Mini 297 or 997 series/Bussmann ATM series or equivalent SPECIFICATIONS Contacts: \.012 \(\.30\) Brass Insulator: Nylon 6/6, UL Rated 94V-0 UL Temperature Rating: (.*?)\(-50°C to\+145°C\)", "the 3568 entry")
    D["holder_rating_printed"] = bool(re.search(r"Current Rating", m.group(0)))
    D["keystone_ratings"] = sorted(set(int(x) for x in re.findall(r"UL Current Rating: (\d+) Amps", ks)))
    for k in ("lapp", "alpha"):
        t = flat("".join(pdf_pages(k, True)))
        if re.search(r"(current[- ]carrying|ampacity|rated current|current rating)", t, re.I):
            refuse(4, "%s prints a current rating; this record says it does not" % PINS[k][0])
    D["cable_rating_printed"] = False
    ch = yaml.safe_load(T["chain"])
    si = [x for x in ch["stages"] if x["id"] == "SHORE_INPUT"][0]
    D["band_board_a"] = float(si["conductor"]["rating_a"])
    D["drawn"] = [("J_DCIN's VH contact (the lead AWG %d)" % E["cable_drawn"]["awg"], None, "VH prints %s A at AWG 16 with the standard header and 7 A at AWG 18 with the shrouded one; the drawn lead is AWG %d on the standard header: none stated" % (fmt(D["vh"]), E["cable_drawn"]["awg"]), "MAKER"),
                  ("the D38999 size 16 contact, insert 13-4", D["c16"], "Amphenol's test current", "MAKER"),
                  ("F1's holder, Keystone 3568", None, "the page prints a UL current rating for other MINI clips and holders (%s A) and none for the 3568" % ", ".join(str(x) for x in D["keystone_ratings"]), "MAKER"),
                  ("the DC lead, Lapp OLFLEX ROBUST 210 4 x 1.0 or Alpha Wire 25064", None, "no current rating printed in either sheet", "MAKER"),
                  ("the inside lead, %d mm of AWG %d" % (E["cable_drawn"]["lead_mm"], E["cable_drawn"]["awg"]), None, "no part and no rating", "NETLIST"),
                  ("board E's input bands at 2 oz", D["band_board_a"], "pcb_energy_chain.yaml SHORE_INPUT", "RECORD")]
    D["drawn_met"] = all(r is not None and r >= D["cont_need"] for _n, r, _s, _c in D["drawn"])
    D["selected"] = [("receptacle and plug contacts", "MIL-DTL-38999 size 12 (insert 17-6, or 13-26 with the solar pair on rated contacts elsewhere)", D["c12"], "Amphenol test current, MAKER"),
                     ("J_DCIN, the board connector", "a %d A class (Amass XT60 family, gender opposite J_BATT's), or soldered lead lands" % D["xt60"], D["xt60"], "Amass V1.2: %d A rated, %d A instantaneous, %d AWG recommended, MAKER" % (D["xt60"], D["xt60_inst"], D["xt60_awg"])),
                     ("F1's holder", "a MINI 297/997 holder whose maker prints at least %d A" % CONT_CLASS_A, None, "the 3568 prints none: Layer 7/8 picks"),
                     ("the DC lead and the inside lead", "cores of %.3f mm2 (AWG 14) whose maker states at least %d A continuous each" % (SEL_MM2, CONT_CLASS_A), None, "no held sheet: an acceptance for Layer 7"),
                     ("board E's copper J_DCIN to F1 to the clamps", "at least %d A continuous" % CONT_CLASS_A, None, "a layout constraint (Layer 9)")]
    # the stiff source again (copper alone at the cold end; the source's own resistance zero, A-12)
    vmax = f(need(L9, r"the selected OVLO \(R23 6\.42k, R22 100k, both 0\.1 %\): ([\d.]+) / ([\d.]+) / ([\d.]+) V", "the OVLO maximum"), 3)
    D["vmax"] = vmax
    rho_c = CU_RHO_20 * (1 + CU_ALPHA * (T_COLD - 20.0))
    cd = E["cable_drawn"]
    drawn_r = (2 * cd["m"] / cd["mm2"] + 2 * cd["lead_mm"] / 1000.0 / AWG18_MM2) * rho_c
    D["stiff"] = [("as drawn: %s m of %s mm2 and %d mm of AWG 18 (L4-E9)" % (fmt(cd["m"]), fmt(cd["mm2"]), cd["lead_mm"]), drawn_r, vmax / drawn_r)]
    for lab, cm, mm2 in (("AWG 14, 2.0 m cable, 0.5 m lead", 2.0, AWG14_MM2), ("AWG 14, %s m cable, 0.5 m lead (SELECTED)" % fmt(SEL_CABLE_M), SEL_CABLE_M, AWG14_MM2),
                         ("AWG 12, %s m cable, 0.5 m lead" % fmt(SEL_CABLE_M), SEL_CABLE_M, AWG12_MM2)):
        rr = (2 * cm + 2 * LEAD_M) * rho_c / mm2
        D["stiff"].append((lab, rr, vmax / rr))
    if abs(D["stiff"][0][2] - cd["ipf"]) > 0.6:
        refuse(4, "the drawn stiff-source current does not reproduce L4-E9's %s A" % cd["ipf"])
    D["r_floor"] = vmax / D["interrupt_a"]
    D["min_len_14"] = (D["r_floor"] * AWG14_MM2 / rho_c - 2 * LEAD_M) / 2.0
    D["sel_ipf"] = D["stiff"][2][2]
    if not D["sel_ipf"] <= D["interrupt_a"]:
        refuse(4, "the selected interconnect's stiff-source current passes F1's interrupting rating")
    rho_hot = CU_RHO_20 * (1 + CU_ALPHA * (F["air_hot"] - 20.0))
    D["min_fault_9v"] = 9.0 / ((2 * SEL_CABLE_M + 2 * LEAD_M) * rho_hot / SEL_MM2)
    D["min_fault_9v_x"] = D["min_fault_9v"] / D["rating"]
    # the short-time points: adiabatic rise of a 2.081 mm2 core, and the contact's I2t at its rated current
    s_cm2 = SEL_MM2 / 100.0
    D["adiabatic"] = [(i, t, i * i * t * CU_RHO_20 * 1e-4 / (s_cm2 ** 2 * CU_CV)) for i, t in D["band"][1:]]
    D["contact_eq_s"] = [(i, t, i * i * t / D["c12"] ** 2) for i, t in D["band"][1:]]
    D["sel_ok"] = D["c12"] >= CONT_CLASS_A >= D["band"][1][0] >= D["cont_need"] and D["xt60"] >= CONT_CLASS_A
    R["D"] = D

    # ------------------------------------------------------------------ 7. D-09: the fault timer against the start
    T9 = {}
    m = need(l69, r"VTMRH Upper threshold ([\d.]+) ([\d.]+) ([\d.]+) V", "VTMRH")
    T9["vtmrh"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(l69, r"Fault detection current (\d+) (\d+) (\d+) µA", "ITIMER")
    T9["itimer"] = (f(m, 1) * 1e-6, f(m, 2) * 1e-6, f(m, 3) * 1e-6)
    m = need(l69, r"VCL Threshold voltage VIN-SENSE voltage ([\d.]+) ([\d.]+) ([\d.]+) mV", "VCL")
    T9["vcl"] = (f(m, 1) * 1e-3, f(m, 2) * 1e-3, f(m, 3) * 1e-3)
    need(l69, r"TI recommends setting the minimum fault time \(tflt\) to be greater than the start time \(tstart\) by adding an additional margin of 50% of the fault time", "TI's 50 % margin")
    T9["eq12_p"] = find("lm5069", r"9\.2\.1\.2\.4 Set Fault Timer", "9.2.1.2.4")[0]
    m = need(l69, r"R PWR 1\.30 u 10 5 u R SNS \(PLIM 1\.18mV u", "Equation 9")
    T9["k9"], T9["v9"] = 1.30e5, 1.18e-3
    m = need(L9, r"the power limit with R24 22 k: ([\d.]+) W nominal, ([\d.]+) W at its corners, ([\d.]+) W with TI's 1\.3 margin, ([\d.]+) A at ([\d.]+) V", "L4-E9's power limit")
    T9["plim_nom_l9"], T9["pulse_a"] = f(m, 1), f(m, 4)
    T9["rpwr"] = 22e3
    T9["rs"] = 0.010
    T9["rs_tol"] = f(need(ge, r'r\("R19", "10mOhm (\d+)% 2512 \(hot-swap sense\)"', "R19")) / 100.0
    plim = lambda rpwr, rs, vds: rpwr / (T9["k9"] * rs) + T9["v9"] * vds / rs
    T9["plim_nom"] = plim(T9["rpwr"], T9["rs"], vmax)
    if abs(T9["plim_nom"] - T9["plim_nom_l9"]) > 0.01:
        refuse(4, "Equation 9 does not reproduce L4-E9's %s W" % T9["plim_nom_l9"])
    m = need(L9, r"Equation 19 derates by ([\d.]+)", "L4-E9's derating")
    T9["derate"] = f(m)
    T9["tc_case"] = f(need(L9, r"Q7's case at most ([\d.]+) C", "Q7's case"))
    # the capacitance the start charges: DC_HS and VIN_RAW on board E, VIN_RAW and the guard's two filters on board A
    na, ne = T["net_a"], T["net_e"]
    caps = []
    for net, t_, b in (("DC_HS", ne, "E"), ("VIN_RAW", ne, "E"), ("VIN_RAW", na, "A"), ("FE_VINP", na, "A"), ("FE_GVDD", na, "A")):
        for ref, _pin in netlist_nodes(t_, net):
            if ref.startswith("C"):
                mv = re.match(r"([\d.]+)u", netlist_value(t_, ref))
                if mv:
                    caps.append((b, ref, net, float(mv.group(1))))
    T9["caps"] = caps
    T9["c_uf"] = sum(x[3] for x in caps)
    # the resistive load during the start (each path bounded by its resistor alone to ground): LED1 behind R27, R40, R14, R200
    loads = []
    for t_, b, ref in ((ne, "E", "R27"), (ne, "E", "R40"), (na, "A", "R14"), (na, "A", "R200")):
        nodes = netlist_nodes(t_, "VIN_RAW")
        if (ref, "1") not in nodes and (ref, "2") not in nodes:
            refuse(3, "%s is not on VIN_RAW" % ref)
        loads.append((b, ref, float(re.match(r"([\d.]+)k", netlist_value(t_, ref)).group(1)) * 1e3))
    T9["loads"] = loads
    T9["g_load"] = sum(1.0 / r for _b, _r, r in loads)
    m = find("lm5176", r"IQ\s+VIN shutdown current\s+VEN/UVLO = 0 V\s+([\d.]+)\s+(\d+)\s+µA", "LM5176 shutdown", layout=True)[1]
    T9["u2_sd"] = f(m, 2) * 1e-6
    # the front end's enable: U34's release delay (gen_sch_a.py's derivation from SNVSBJ1E)
    m = need(flat(ga), r"C212\W+100 nF on CTR2 holds the release (\d+) / (\d+) / (\d+) ms", "U34's release delay")
    T9["ctr2_ms"] = (f(m, 1), f(m, 2), f(m, 3))
    # the X7R rows L4-E9 stacked (Yageo V.26) for the start's capacitors
    ya = flat("".join(pdf_pages("yageo", True)))
    need(ya, r"K = ± 10%", "Yageo K")
    T9["x7r"] = (0.10, f(need(ya, r"\(temperature characteristic/coefficient\): ± (\d+)%", "X7R temperature")) / 100.0,
                 f(need(ya, r"Endurance IEC 60384-.*?X7R: ± (\d+)%", "X7R endurance")) / 100.0)
    hi_f = (1 + T9["x7r"][0]) * (1 + T9["x7r"][1]) * (1 + T9["x7r"][2])

    def t_start(c_f, rpwr, rs, ilim, margin, g):
        n, dv, t, v = STEP_N, vmax / STEP_N, 0.0, 0.0
        for _ in range(n):
            vm = v + 0.5 * dv
            vds = vmax - vm
            i = min(plim(rpwr, rs, vds) / margin / vds, ilim)
            il = vm * g + (T9["u2_sd"] if g else 0.0)
            if i <= il:
                refuse(4, "the start stalls at %.2f V" % vm)
            t += c_f * dv / (i - il)
            v += dv
        return t
    T9["eq12_nom"] = T9["c_uf"] * 1e-6 / 2 * (vmax ** 2 / T9["plim_nom"] + T9["plim_nom"] / (T9["vcl"][1] / T9["rs"]) ** 2)
    T9["start_nom"] = t_start(T9["c_uf"] * 1e-6, T9["rpwr"], T9["rs"], T9["vcl"][1] / T9["rs"], 1.0, T9["g_load"])
    rs_hi = T9["rs"] * (1 + T9["rs_tol"])
    T9["start_max"] = t_start(T9["c_uf"] * 1e-6 * hi_f, T9["rpwr"] * 0.99, rs_hi, T9["vcl"][0] / rs_hi, 1.3, T9["g_load"])
    T9["start_max_noload"] = t_start(T9["c_uf"] * 1e-6 * hi_f, T9["rpwr"] * 0.99, rs_hi, T9["vcl"][0] / rs_hi, 1.3, 0.0)
    m = need(L9, r"takes ([\d.]+) ms at nominal values and ([\d.]+) ms with the capacitors at the printed rows' top", "L4-E9's start", re.S)
    T9["start_l9"] = (f(m, 1) * 1e-3, f(m, 2) * 1e-3)
    T9["need"] = 1.5 * T9["start_max"]
    T9["ctr2_over_start"] = T9["ctr2_ms"][0] * 1e-3 / T9["start_max"]
    # Figure 10 at the OVLO maximum (TI's vector drawing), TI's power law between 1 and 10 ms carried past 10 ms
    lines = soa_lines()
    i10, i1, idc = soa_at(lines["10ms"], vmax), soa_at(lines["1ms"], vmax), soa_at(lines["DC"], vmax)
    T9["i10"], T9["i1"], T9["idc"] = i10, i1, idc
    T9["m"] = math.log(i1 / i10) / math.log(10.0)
    soa = lambda t, mexp=None: i10 * (10e-3 / t) ** (T9["m"] if mexp is None else mexp) * T9["derate"]
    T9["t_soa_max"] = 10e-3 * (i10 * T9["derate"] / T9["pulse_a"]) ** (1.0 / T9["m"])
    # the Murata C0G rows (both reference sheets) and the catalogue readings
    mur = {}
    for k in ("mur104", "mur683"):
        tx = flat("".join(pdf_pages(k, True)))
        m = need(tx, r"(GRM3195C1H\d{3}[GJ]A05)_\(3216M\(1206\), C0G\(EIA\), ([\d.]+)(μF|pF), DC (\d+)V\)", "the Murata part line")
        val = f(m, 2) * (1e-6 if m.group(3) == "μF" else 1e-12)
        mm = need(tx, r"0\+/-(\d+) ppm/℃ 25 to 125℃ 25℃ DC (\d+)V [\d.]+(?:μF|pF) \+/-(\d+)% -55 to 125℃", "the rated values")
        ta = need(tx, r"Table A Capacitance Change between at Reference Temp\. and at each Temp\. \(%\) -55℃ -30℃ -10℃ Char\. Max\. Min\. Max\. Min\. Max\. Min\. 5C ([\d.]+) -([\d.]+)", "Table A")
        en = need(tx, r"Endurance Visual examination No defects or abnormalities\. Mounting method Solder the capacitor on the test substrate Capacitance Change Within \+/-(\d+)%", "the endurance row")
        dh = need(tx, r"Damp heat, steady state Visual examination No defects or abnormalities\. Mounting method Solder the capacitor on the test substrate Capacitance Change Within \+/-([\d.]+)%", "the damp heat row")
        mur[m.group(1)] = dict(c=val, v=f(m, 4), ppm=f(mm, 1) * 1e-6, tol=f(mm, 3) / 100.0, ta_up=f(ta, 1) / 100.0, ta_dn=f(ta, 2) / 100.0,
                               endur=f(en) / 100.0, damp=f(dh) / 100.0, page=find(k, r"Endurance\s+Visual examination", "endurance page", layout=True)[0])
    T9["mur"] = mur
    lc = {J[n]["code"]: J[n] for n in INPUTS if n.startswith("lcsc-")}
    code_of = {lc[c]["model"][:-1]: c for c in lc}
    for pn in mur:
        if pn not in code_of or lc[code_of[pn]]["stock"] < 1000:
            refuse(4, "%s has no filed LCSC reading with stock" % pn)
    T9["search150"] = (J["jlc-search-c0g-150nf-2026-10-02.json"]["count"], J["jlc-search-c0g-150nf-2026-10-02.json"]["stocked_count"])
    temp_up = max(next(iter(mur.values()))["ta_up"], 0.0)
    temp_dn = max(next(iter(mur.values()))["ta_dn"], 100.0 * next(iter(mur.values()))["ppm"])

    def env_of(parts, extra):
        lo = sum(mur[p]["c"] * (1 - mur[p]["tol"]) for p in parts) * (1 - temp_dn) * (1 - extra)
        hi = sum(mur[p]["c"] * (1 + mur[p]["tol"]) for p in parts) * (1 + temp_up) * (1 + extra)
        return lo, hi
    pA, pB = sorted(mur, key=lambda p: -mur[p]["c"])           # the 100 nF G part and the 68 nF J part
    cand = [("one %s" % pA, [pA]), ("one %s" % pB, [pB]), ("two %s" % pA, [pA, pA]), ("two %s" % pB, [pB, pB]), ("%s with %s" % (pA, pB), [pA, pB])]
    rows9 = []
    for lab, parts in cand:
        endur = max(mur[p]["endur"] for p in parts)
        lo, hi = env_of(parts, endur)
        tmin = lo * T9["vtmrh"][0] / T9["itimer"][2]
        tmax = hi * T9["vtmrh"][2] / T9["itimer"][0]
        rows9.append(dict(lab=lab, parts=parts, c=sum(mur[p]["c"] for p in parts), lo=lo, hi=hi, tmin=tmin, tmax=tmax,
                          start_ok=tmin >= T9["need"], soa=soa(tmax), soa_ok=soa(tmax) >= T9["pulse_a"]))
    T9["cands"] = rows9
    sel = [r for r in rows9 if r["start_ok"] and r["soa_ok"] and len(r["parts"]) <= CAP_STACK_PARTS]
    if [r["lab"] for r in sel] != ["%s with %s" % (pA, pB)]:
        refuse(4, "the stocked C0G sets meeting both ends are %s, not the one this record selects" % [r["lab"] for r in sel])
    S = sel[0]
    T9["sel"] = S
    T9["sel_codes"] = (code_of[pA], code_of[pB])
    T9["sel_nom_ms"] = S["c"] * T9["vtmrh"][1] / T9["itimer"][1]
    T9["sel_extrap"] = S["tmax"] / 10e-3 - 1.0
    T9["sel_soa_m05"] = soa(S["tmax"], 0.5)
    lo, hi = env_of(S["parts"], max(mur[p]["damp"] for p in S["parts"]))
    T9["damp"] = (lo * T9["vtmrh"][0] / T9["itimer"][2], hi * T9["vtmrh"][2] / T9["itimer"][0])
    T9["damp_soa"] = soa(T9["damp"][1])
    T9["typ_basis"] = (T9["sel_nom_ms"], 1.5 * T9["start_nom"])
    T9["c5_l9"] = (100e-9 * (1 - 0.10) * (1 - 0.15) * (1 - 0.15) * T9["vtmrh"][0] / T9["itimer"][2],
                   100e-9 * hi_f * T9["vtmrh"][2] / T9["itimer"][0])
    T9["f1_i2t_start"] = E["entry"][1] ** 2 * S["tmax"]
    T9["dc_hot"] = idc * T9["derate"]
    R["T9"] = T9
    R["N"] = entry_round(R, T, L9)
    R["G"] = dependency_round(R, T)
    R["H"] = consolidation_round(R, T)
    T["arch"] = text("arch")
    R["K"] = fix_round(R, T)
    R["L"] = fix16_round(R, T)
    R["M"] = fix17_round(R, T)
    return R


# ============================================================================================ the fix round (2 October 2026)
def soa_lines_ktt():
    """CSD19536KTT Figure 4-10 (SLPS540C p.6) read from the sheet's vector drawing by L4-E9's method (soa_lines above): the
    plot's own frame and transform, its legend order from the page text, and two anchors checked (the 400 A IDM line and the
    100 V boundary), so the 100 us, 1 ms, 10 ms and DC lines are TI's own coordinates. The plot spans 0.1 to 1000 V and A."""
    pdf = read("csd19536")
    svg = subprocess.run(["pdftocairo", "-svg", "-f", "6", "-l", "6", pdf, "-"], capture_output=True).stdout.decode("utf-8", "replace")
    tr = "matrix(0.0972764,0,0,-0.09741,67.961,231.544)"
    paths = []
    for m in re.finditer(r"<path[^>]*>", svg):
        # poppler 22 writes the stroke as a style property and "rgb(0%,0%,0%)", "matrix(a,b,...)"; poppler 24 writes a stroke
        # attribute and puts a space after each comma: the reader takes both, the path coordinates being the same
        t = re.sub(r",\s+", ",", m.group(0))
        st = re.search(r'stroke(?::|=")(rgb\([^)]*\))', t)
        if tr not in t or not st:
            continue
        pts = [(float(a), float(b)) for a, b in re.findall(r"[ML] ([-\d.]+) ([-\d.]+)", re.search(r' d="([^"]*)"', t).group(1))]
        paths.append((st.group(1), pts))
    frames = [p for c, p in paths if c == "rgb(0%,0%,0%)" and len(p) == 5 and p[0] == p[-1]]
    if not frames:
        refuse(3, "Figure 4-10's frame")
    fr = max(frames, key=lambda q: (max(a for a, _ in q) - min(a for a, _ in q)) * (max(b for _, b in q) - min(b for _, b in q)))
    x0, x1 = min(q[0] for q in fr), max(q[0] for q in fr)
    y0, y1 = min(q[1] for q in fr), max(q[1] for q in fr)
    lv = lambda x: -1.0 + 4.0 * (x - x0) / (x1 - x0)
    li = lambda y: -1.0 + 4.0 * (y - y0) / (y1 - y0)
    txt = flat(pdf_pages("csd19536", True)[5])
    if not re.search(r"DC 1 ms 10 ms 100 .s", txt):
        refuse(3, "Figure 4-10's legend text")
    labels = ["DC", "1ms", "10ms", "100us"]                           # the legend's two rows, left to right, top to bottom
    legend = sorted(((p[0][1], p[0][0], c) for c, p in paths if len(p) == 2 and p[0][1] == p[1][1] and c != "rgb(0%,0%,0%)"
                     and 10 ** lv(p[1][0]) < 2.0 and 10 ** li(p[0][1]) < 0.5), key=lambda q: (-q[0], q[1]))
    if len(legend) != 4:
        refuse(3, "Figure 4-10's legend segments")
    out = {}
    for lab, (_y, _x, col) in zip(labels, legend):
        cands = [p for c, p in paths if c == col and len(p) >= 2 and abs(10 ** lv(p[-1][0]) - 100.0) < 1.0]
        if len(cands) != 1:
            refuse(3, "Figure 4-10's %s line" % lab)
        out[lab] = [(lv(x), li(y)) for x, y in cands[0]]
    tops = [10 ** max(y for _x, y in v) for k, v in out.items() if k != "DC"]
    if any(abs(t - 400.0) > 4.0 for t in tops):
        refuse(3, "Figure 4-10's IDM line")
    return out


def soa_t(lines, vds, t):
    """The line's current at vds for a pulse of t s: log-log between the printed lines in time; under the shortest line its
    value (a longer pulse's, so lower); past 10 ms the power law of the last two lines carried (L4-E9's method)."""
    ts = sorted(lines)
    val = lambda k: soa_at(lines[k], vds) if math.log10(vds) >= lines[k][0][0] else 10 ** lines[k][0][1]
    if t <= ts[0]:
        return val(ts[0])
    for a, b in zip(ts, ts[1:]):
        if a <= t <= b:
            ia, ib = val(a), val(b)
            return 10 ** (math.log10(ia) + (math.log10(ib) - math.log10(ia)) * (math.log10(t) - math.log10(a)) / (math.log10(b) - math.log10(a)))
    ia, ib = val(ts[-2]), val(ts[-1])
    return ib * (ts[-1] / t) ** (math.log10(ia / ib) / math.log10(ts[-1] / ts[-2]))


def fault_scan(lines, vin, s, c, ioc, isc, toc, tau, tsc, derate):
    """A start into a resistive fault Rf under gate-slew inrush and a circuit breaker (no power limit). The output follows the
    gate at the slew s (V/s): the FET carries c x s plus Vout / Rf with VIN - Vout across it until Vout reaches VIN (then it is
    fully on and VIN / Rf flows at a small VDS). The breaker acts on two paths: the overcurrent comparator, whose delay toc
    (TI's row, loaded) runs while the current stays over ioc; the short-circuit comparator, which sees the sense voltage through
    the RISCP x CSCP filter (first order, time constant tau) and then turns the FET off within tsc (TI's loaded propagation).
    The current keeps following its trajectory through every delay. Every point of the pulse is held against the chart for the
    WHOLE pulse's duration (conservative: no thermal-impedance superposition). Returns the worst ratio of current to the derated
    line, its Rf, its duration and which path ended it."""
    worst = (0.0, None, None, None)
    for k in range(241):
        rf = 10 ** (-1.0 + 4.0 * k / 240)
        i0, a, tf, iend = c * s, s / rf, vin / s, vin / rf
        t_oc = None
        if i0 >= ioc:
            t0 = 0.0
        elif i0 + a * tf >= ioc:
            t0 = (ioc - i0) / a
        else:
            t0 = None
        if t0 is not None and (t0 + toc <= tf or iend >= ioc):
            t_oc = t0 + toc
        filt = lambda x: i0 * (1 - math.exp(-x / tau)) + a * (x - tau * (1 - math.exp(-x / tau)))
        ftf, t1 = filt(tf), None
        if ftf >= isc:
            lo_, hi_ = 0.0, tf
            for _ in range(80):
                mid = 0.5 * (lo_ + hi_)
                lo_, hi_ = (lo_, mid) if filt(mid) >= isc else (mid, hi_)
            t1 = hi_
        elif iend > isc:
            t1 = tf + tau * math.log((iend - ftf) / (iend - isc))
        t_sc = None if t1 is None else t1 + tsc
        ends = [(x, how) for x, how in ((t_oc, "the overcurrent delay"), (t_sc, "the short-circuit trip")) if x is not None]
        t_off, how = min(ends) if ends else (None, "the start completes")
        t_end = tf if t_off is None or t_off >= tf else t_off
        if t_off is not None and t_off >= tf:
            how = "the start completes, then %s" % how
        r = 0.0
        for jj in range(121):
            x = t_end * jj / 120
            vds = vin - s * x
            if vds < 2.2:
                continue
            r = max(r, (i0 + a * x) / (derate * soa_t(lines, vds, t_end)))
        if r > worst[0]:
            worst = (r, rf, t_end, how)
    return worst


def start_into_short(lines, vin, a_g, isc, tau, tsc, derate):
    """A start into a hard short: VDS stays at VIN and the drain current follows the gate at a_g (A/s, the transconductance
    times the gate slew) from the threshold; the filtered sense reaches isc, then tsc. Returns the peak, the pulse and the ratio
    to the derated chart at that pulse."""
    g = lambda x: a_g * (x - tau * (1 - math.exp(-x / tau)))
    lo_, hi_ = 0.0, isc / a_g + 10 * tau
    for _ in range(80):
        mid = 0.5 * (lo_ + hi_)
        lo_, hi_ = (lo_, mid) if g(mid) >= isc else (mid, hi_)
    tp = hi_ + tsc
    ip = a_g * tp
    return ip, tp, ip / (derate * soa_t(lines, vin, tp))


def red2_model():
    """hc2's pwr_red2.py with rv-pwr's pwr_budget.py, both pinned, imported as hc2 imports them: its own printing discarded."""
    read("red2_py")
    read("budget_py")
    import contextlib
    import importlib.util
    import io
    spec = importlib.util.spec_from_file_location("pwr_red2_for_l4e11", os.path.join(TOP, PINS["red2_py"][0]))
    mod = importlib.util.module_from_spec(spec)
    argv = sys.argv
    sys.argv = [os.path.join(TOP, PINS["red2_py"][0]), os.path.join(TOP, PINS["budget_py"][0])]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod


def entry_round(R, T, L9):
    """B1 to B5 of the focused check (cx30, 2 October 2026): the entry at a 9.00 V plug, the source envelope with the kit's own
    losses, the weak-source envelope as monotone intervals, the charge bounds. Every figure carries its class."""
    B, P, E, D, F, T9 = R["B"], R["P"], R["E"], R["D"], R["F"], R["T9"]
    N = {}
    l69 = flat("".join(pdf_pages("lm5069", True)))
    ge, ga = T["gen_e"], T["gen_a"]
    # ---- B1: the drawn LM5069 at a 9.00 V plug (SNVS452G)
    m = need(l69, r"PORIT VIN increasing ([\d.]+) ([\d.]+) V VIN to trigger insertion timer Power-On reset threshold at POREN VIN increasing ([\d.]+) ([\d.]+) V VIN to enable all functions POREN-HYS POREN hysteresis VIN decreasing (\d+) mV", "PORIT and POREN")
    N["porit"], N["poren"], N["poren_hys"] = (f(m, 1), f(m, 2)), (f(m, 3), f(m, 4)), f(m, 5) * 1e-3
    N["vin_range"] = (f(need(l69, r"Wide operating range: (\d+) V to (\d+) V", "the operating range"), 1), 80.0)
    need(l69, r"VCL Threshold voltage VIN-SENSE voltage", "VIN as the sense reference")
    need(ge, r'ic\("U6", 10, "LM5069MM-2 hot-swap controller: [^"]*", "VSSOP10", \{"1": "HS_S", "2": "DC_P"', "U6's VIN on DC_P")
    lm7 = flat("".join(pdf_pages("lm74700", True)))
    m = need(lm7, r"V\(AK REG\) Regulated Forward V\(AK\) Threshold (\d+) (\d+) (\d+) mV", "LM74700 V(AK REG)")
    N["vak"] = (f(m, 1) * 1e-3, f(m, 2) * 1e-3, f(m, 3) * 1e-3)
    N["vin_ic_max"] = PLUG_V - N["vak"][0]                       # before the hot swap conducts, nothing larger than this reaches VIN
    N["poren_met"] = N["vin_ic_max"] >= N["poren"][1]
    # the UVLO by Equations 38 to 40: falling UVLOTH (1 + R20/R21); rising that plus UVLOHYS x R20
    uv, hy, r20 = E["uv_rows"], E["hy_rows"], E["r20"]
    def uvlo(r21x, tol=0.01):
        fall = (uv[0] * (1 + r20 * (1 - tol) / (r21x * (1 + tol))), uv[1] * (1 + r20 / r21x), uv[2] * (1 + r20 * (1 + tol) / (r21x * (1 - tol))))
        rise = (fall[0] + hy[0] * r20 * (1 - tol), fall[1] + hy[1] * r20, fall[2] + hy[2] * r20 * (1 + tol))
        return rise, fall
    need(l69, r"VUVH = 2\.5V \+ \[R1 x \(2\.5V \+ 21 .A\)\]", "Equation 38")
    N["uvlo_drawn"] = uvlo(E["r21"])
    N["uvlo_withdrawn"] = uvlo(42.2e3)
    # ---- the kit's own series resistance, hot and cold (each element's class named in the output)
    cold_f = 1 + CU_ALPHA * (T_COLD - 20.0)
    N["c12_r"] = D["c12_mv"] * 1e-3 / D["c12"]
    xt = flat(pdf_pages("xt60", True)[0])
    N["xt60_r"] = f(need(xt, r"接触电阻 ([\d.]+)mΩ", "XT60 contact resistance")) * 1e-3
    N["loop_floor20"] = D["vmax"] / (I_PF_TARGET * cold_f)          # the loop's actual floor at 20 C (copper and contacts)
    N["loop_floor_cold"] = N["loop_floor20"] * cold_f
    N["i_pf_spec"] = D["vmax"] / N["loop_floor_cold"]
    N["u_meas"] = U_MEAS + CU_ALPHA * DT_MEAS
    N["acc"] = (N["loop_floor20"] * (1 + N["u_meas"]), LOOP_CEIL20 / (1 + N["u_meas"]))   # the measured value's acceptance window
    N["loop_ceil20"] = LOOP_CEIL20
    N["cu_nom20"] = (2 * SEL_CABLE_M + 2 * LEAD_M) * CU_RHO_20 / SEL_MM2
    N["contacts_max"] = 2 * N["c12_r"] + 2 * N["xt60_r"]
    N["constr"] = (N["cu_nom20"], N["cu_nom20"] + N["contacts_max"])
    if not (N["acc"][0] < N["constr"][0] and N["constr"][1] < N["acc"][1]):
        refuse(4, "the selected construction does not sit inside the measured window")
    N["min_len_floor"] = (N["loop_floor20"] * SEL_MM2 / CU_RHO_20 - 2 * LEAD_M) / 2.0
    out_share = SEL_CABLE_M / (SEL_CABLE_M + LEAD_M)
    N["hot_f"] = out_share * (1 + CU_ALPHA * (T_OUT_HOT - 20.0)) + (1 - out_share) * (1 + CU_ALPHA * (F["air_hot"] - 20.0))
    N["cable_hot"] = N["loop_ceil20"] * N["hot_f"]
    fz = flat("".join(pdf_pages("fuse997", True)))
    m = need(fz, r"0997010_ 10 1 (\d+) ([\d.]+) (\d+)", "the 0997010 drop")
    N["f1_hot"] = f(m, 1) * 1e-3 / 10.0
    N["q1_rds"] = f(need(ge, r'"BSC039N06NS 60 V ([\d.]+) mOhm N-FET', "Q1's RDS(on)")) * 1e-3
    kt = flat("".join(pdf_pages("csd19536", True)))
    m = need(kt, r"VGS = 10V, ID = 100A ([\d.]+) ([\d.]+)", "CSD19536KTT RDS(on)")
    N["q7_rds"] = f(m, 2) * 1e-3
    m = need(kt, r"Qg Gate charge total \(10V\) (\d+) (\d+) nC", "CSD19536KTT Qg")
    N["q7_qg"] = f(m, 2) * 1e-9
    N["q7_tj"] = f(need(kt, r"Operating Junction, \S55 to (\d+) \S?C", "CSD19536KTT TJ"))
    srf = flat(pdf_pages("srf1260", True)[0])
    m = need(srf, r"SRF1260-1R0Y 1\.0 ±30 ([\d.]+) ([\d.]+) ([\d.]+) 4 ±30 ([\d.]+) ([\d.]+) ([\d.]+)", "SRF1260-1R0Y's row")
    N["l2_dcr"], N["l2_irms"] = f(m, 4), f(m, 5)
    # ---- the candidates' rows (held TI sheets)
    t63 = flat("".join(pdf_pages("tps1663", True)))
    N["t63_range"] = (f(need(t63, r"Operating voltage: ([\d.]+)V to (\d+)V", "TPS1663 range"), 1), f(need(t63, r"Operating voltage: ([\d.]+)V to (\d+)V", "TPS1663 range"), 2))
    N["t63_abs"] = f(need(t63, r"Absolute maximum: (\d+)V", "TPS1663 absolute"))
    m = need(t63, r"R\(ILIM\) = 3k\S*\s+V\(IN\) \S V\(OUT\) = 1V ([\d.]+) ([\d.]+) ([\d.]+) A", "TPS1663 at 3k")
    N["t63_ilim"] = (f(m, 1), f(m, 2), f(m, 3))
    t48 = flat("".join(pdf_pages("tps4811", True)))
    rows = lambda pat, what, n=3: tuple(f(need(t48, pat, what), i) for i in range(1, n + 1))
    N["t48_vs"] = rows(r"V\(VS\) Operating input voltage ([\d.]+) ([\d.]+) V", "VS range", 2)
    N["t48_abs"] = f(need(t48, r"3\.5V to 80V input range \((\d+)V absolute maximum\)", "TPS4811 absolute"))
    N["t48_por"] = rows(r"V\(VS_PORR\) VS POR threshold, rising ([\d.]+) ([\d.]+) ([\d.]+) V", "VS POR")
    N["t48_uvr"] = rows(r"V\(UVLOR\) UVLO threshold voltage, rising ([\d.]+) ([\d.]+) ([\d.]+) V", "UVLOR")
    N["t48_uvf"] = rows(r"V\(UVLOF\) UVLO threshold voltage, falling ([\d.]+) ([\d.]+) ([\d.]+) V", "UVLOF")
    N["t48_enleak"] = f(need(t48, r"I\(EN/UVLO\) Enable input leakage current V\(EN/UVLO\) = 12V (\d+) (\d+) nA", "EN leakage"), 2) * 1e-9
    N["t48_ovr"] = rows(r"V\(OVR\) Overvoltage threshold input, ris[Ii]ng ([\d.]+) ([\d.]+) ([\d.]+) V", "OVR")
    N["t48_ovf"] = rows(r"V\(OVF\) Overvoltage threshold input, falling ([\d.]+) ([\d.]+) ([\d.]+) V", "OVF")
    N["t48_ovleak"] = f(need(t48, r"I\(OV\) OV Input leakage current 0V < V\(OV\) < 5V (\d+) (\d+) nA", "OV leakage"), 2) * 1e-9
    N["t48_cp_on"] = rows(r"Charge Pump Turn ON voltage ([\d.]+) ([\d.]+) ([\d.]+) V", "charge pump on")
    N["t48_cp_off"] = rows(r"Charge Pump Turn OFF voltage ([\d.]+) ([\d.]+) ([\d.]+) V", "charge pump off")
    m = need(t48, r"RSET = 100 ., RIWRN = 39\.7k. ([\d.]+) ([\d.]+) ([\d.]+) mV", "the OCP row at 39.7k")
    N["t48_wrn"] = (f(m, 1) * 1e-3, f(m, 2) * 1e-3, f(m, 3) * 1e-3)
    N["t48_iscp"] = tuple(x * 1e-6 for x in rows(r"I\(ISCP\) SCP Input Bias current ([\d.]+) ([\d.]+) ([\d.]+) .A", "ISCP bias"))
    need(t48, r"\u2212 464", "Equation 11's offset")
    N["t48_tmr_i"] = tuple(x * 1e-6 for x in rows(r"I\(TMR_SRC_CB\) TMR source current ([\d.]+) ([\d.]+) ([\d.]+) .A", "TMR source"))
    N["t48_tmr_v"] = rows(r"V\(TMR_OC\) ([\d.]+) ([\d.]+) ([\d.]+) V", "TMR threshold")
    m = need(t48, r"tSC Short-circuit protection propagation \S+ \S \S+ \S V\(SNS_SCP\) to PD \S, (\d+) (\d+) \Ss Delay CL = 47nF, TPS48110\SQ1 Only", "tSC of the TPS48110")
    N["t48_tsc"] = (f(m, 1) * 1e-6, f(m, 2) * 1e-6)
    m = need(t48, r"Over current protection delay (\d+) (\d+) \Ss = 47nF, CTMR = 0nF tOC .{0,80}?Over current protection delay (\d+) \Ss = 47nF, CTMR = 22nF", "tOC's rows")
    N["t48_toc0"], N["t48_toc22"] = (f(m, 1) * 1e-6, f(m, 2) * 1e-6), f(m, 3) * 1e-6
    need(t48, r"0\.63 \u00d7 V BST \u2212 SRC \u00d7 CLOAD", "Equation 3")
    need(t48, r"tRETRY = 22\.7 \u00d7 106 \u00d7 CTMR", "Equation 9")
    need(t48, r"After 32 charging, discharging cycles", "the auto-retry count")
    N["t48_inp_h"] = f(need(t48, r"V\(INP_H\) ([\d.]+) ([\d.]+) V", "INP high"), 2)
    N["t48_pin_abs"] = f(need(t48, r"Input Pins OV, EN/UVLO, INP, INP_G, FLT_I , FLT_T to GND \S1 (\d+)", "the input pins' maximum"))
    need(t48, r"TI recommends RVS value around 100\u03a9", "TI's VS filter")
    need(t48, r"add filter capacitor of 1nF \(CSCP\)", "TI's CSCP")
    need(t48, r"External VS to GND 22 nF Capacitor BST to SRC 0\.1 .F", "the external capacitors")
    # ---- the in-service current at a 9.00 V plug, the knee and the functional state (B3)
    st = E["states"]
    rd = T["red2"]
    m = need(rd, r'"PS-SURV \(slot 2 alone\)": \{\s+"battery_W_lo": ([\d.]+),\s+"battery_W_plan": ([\d.]+),\s+"battery_W_hi": ([\d.]+)', "PS-SURV slot 2 alone")
    surv = (f(m, 1), f(m, 2), f(m, 3))
    m1 = need(rd, r'"PS-IDLE-SPEC, link cards held off": \{\s+"battery_W_plan": ([\d.]+)', "the idle without the heater")
    N["heater_w"] = st["PS-IDLE-SPEC cold, heater on"][1] - f(m1)
    N["surv"] = surv
    M2 = red2_model()
    pbm = M2.pb
    if [round(pbm.state_full("RED", s_, M2.SURV)["pb"], 2) for s_ in ("lo", "plan", "hi")] != list(surv):
        refuse(4, "the budget model does not reproduce pwr_red2.out's PS-SURV")
    shed = dict(M2.SURV)
    names = {nm for (nm, _nd, _v, _s) in pbm.LOADS}
    for k_ in SHED_OFF:
        if k_ not in names:
            refuse(3, "the budget has no load %r" % k_)
        shed[k_] = pbm.OFF
    heat_ov = {**shed, M2.HEATER: M2.HEAT_REG}
    N["shed_held"] = [(k_, tuple(M2.SURV[k_][:3]) if k_ in M2.SURV else tuple(next(v for (nm, _nd, v, _s) in pbm.LOADS if nm == k_)["RED"][:3])) for k_ in SHED_OFF]
    N["shed"] = tuple(pbm.state_full("RED", s_, shed)["pb"] for s_ in ("lo", "plan", "hi"))
    N["func"] = tuple(pbm.state_full("RED", s_, heat_ov)["pb"] for s_ in ("lo", "plan", "hi"))
    fh = pbm.state_full("RED", "plan", heat_ov)
    N["func_heat_in"] = fh["pb"] - fh["outside"] + pbm.pack_i2r(fh["pb"])
    N["g_cold"] = tuple(pbm.G_3253["open_fans"])
    N["air_m20"] = (-20.0 + N["func_heat_in"] / N["g_cold"][1], -20.0 + N["func_heat_in"] / N["g_cold"][0])
    l5 = T["l4e5"]
    N["knee_slope"] = f(need(l5, r"The knee's slope at the pin is ([\d.]+) V/V", "the knee's slope"))
    m = need(l5, r"zero-current target, the pin at 1\.0 V .*?: VIN_RAW ([\d.]+) V \(([\d.]+) to ([\d.]+) V\)", "the knee's zero band")
    N["knee_tol"] = (f(m, 3) - f(m, 2)) / 2.0 / f(m, 1)
    gain = 40 * 0.010                                             # V/A at the pin with R16 10 mOhm (SLUSE66A p.6, RECORD L4-E5)
    def band(it):                                                 # U3's board current at a pin target it (INFERRED, L4-E5's components)
        pin = 1.0 + gain * it
        return ((it - PIN_ERR - NET_TOL * pin / gain) / (1 + E["r16_tol"]), (it + PIN_ERR + NET_TOL * pin / gain) / (1 - E["r16_tol"]))
    N["band"] = band
    need_lo = N["func"][1] / (E["vb_low"] * E["eta_u3"])
    N["it_need"] = (need_lo * (1 + E["r16_tol"]) + PIN_ERR + NET_TOL / gain) / (1 - NET_TOL)
    if KNEE_IT < N["it_need"]:
        refuse(4, "the knee's flat target %s A is under the functional state's need %s A" % (KNEE_IT, N["it_need"]))
    N["it_band"] = band(KNEE_IT)
    line = lambda v: E["slope"] / gain * v
    N["v_join"] = KNEE_IT / (E["slope"] / gain)
    def target(v):                                                # the corrected H3 shape: the line above v_join, flat to KNEE_TOP, the knee below
        if v >= N["v_join"]:
            return line(v)
        if v >= KNEE_TOP:
            return KNEE_IT
        return max(0.0, KNEE_IT - (KNEE_TOP - v) * N["knee_slope"] / gain)
    N["target"] = target
    N["v_zero"] = KNEE_TOP - KNEE_IT * gain / N["knee_slope"]
    N["v_hiz_in"] = N["v_zero"] - (1.0 - 0.4) / N["knee_slope"]
    N["v_hiz_out"] = N["v_zero"] - (1.0 - 0.8) / N["knee_slope"]
    N["hiz_certain"] = N["v_hiz_in"] * (1 - N["knee_tol"])
    N["top_max"] = KNEE_TOP * (1 + N["knee_tol"])
    # ---- the selected entry's settings (SESSION, ENTRY): thresholds and bands
    en = ENTRY
    rs_lo = en["rsns"] * (1 - 0.01) * (1 + en["rsns_tcr"] * (T_COLD - 25.0))
    rs_hi = en["rsns"] * (1 + 0.01) * (1 + en["rsns_tcr"] * (75.0 - 25.0))
    N["rs"] = (rs_lo, rs_hi)
    w0 = N["t48_wrn"][0] * (1 - 2 * en["prec"] - en["drift"]); w2 = N["t48_wrn"][2] * (1 + 2 * en["prec"] + en["drift"])
    N["ioc"] = (w0 / rs_hi, N["t48_wrn"][1] / en["rsns"], w2 / rs_lo)
    N["isc"] = (N["t48_iscp"][0] * (en["riscp"] * 0.99 + 464.0) / rs_hi, N["t48_iscp"][1] * (en["riscp"] + 464.0) / en["rsns"],
                N["t48_iscp"][2] * (en["riscp"] * 1.01 + 464.0) / rs_lo)
    mur = T9["mur"]
    any_m = next(iter(mur.values()))
    c_lo = en["ctmr"] * (1 - 0.05) * (1 - any_m["endur"]) * (1 - any_m["ta_dn"])
    c_hi = en["ctmr"] * (1 + 0.05) * (1 + any_m["endur"]) * (1 + any_m["ta_up"])
    if abs(en["ctmr"] - 22e-9) > 1e-12:
        refuse(4, "CTMR is not TI's characterised 22 nF")
    N["toc_eq7"] = (N["t48_tmr_v"][0] * c_lo / N["t48_tmr_i"][2], N["t48_tmr_v"][1] * en["ctmr"] / N["t48_tmr_i"][1], N["t48_tmr_v"][2] * c_hi / N["t48_tmr_i"][0])
    N["toc_k"] = N["t48_toc22"] / N["toc_eq7"][1]             # TI's loaded row over Equation 7 at the same capacitor
    N["toc"] = (N["toc_eq7"][0], N["t48_toc22"], max(N["toc_eq7"][2] * N["toc_k"], N["toc_eq7"][2] + N["t48_toc22"] - N["toc_eq7"][1]))
    N["tau"] = (en["riscp"] * 0.99 * en["cscp"] * 0.95 * (1 - any_m["endur"]) * (1 - any_m["ta_dn"]), en["riscp"] * en["cscp"],
                en["riscp"] * 1.01 * en["cscp"] * 1.05 * (1 + any_m["endur"]) * (1 + any_m["ta_up"]))
    N["q7_ceq"] = N["q7_qg"] / 12.0                               # Q7's gate charge as a capacitor at the 12 V drive
    N["filt_14"] = -N["tau"][1] * math.log(1 - N["isc"][2] / 14.0)   # the check's example: a 14 A step against the highest threshold
    N["tretry"] = 22.7e6 * en["ctmr"]
    def div(top, bot, th, leak, tol=0.01):
        lo = th[0] * (1 + top * (1 - tol) / (bot * (1 + tol)))
        nom = th[1] * (1 + top / bot)
        hi = th[2] * (1 + top * (1 + tol) / (bot * (1 - tol))) + leak * top * (1 + tol)
        return lo, nom, hi
    N["uv_rise"] = div(en["uv_top"], en["uv_bot"], N["t48_uvr"], N["t48_enleak"])
    N["uv_fall"] = div(en["uv_top"], en["uv_bot"], N["t48_uvf"], N["t48_enleak"])
    N["ov_rise"] = div(en["ov_top"], en["ov_bot"], N["t48_ovr"], N["t48_ovleak"], en["prec"])
    N["ov_fall"] = div(en["ov_top"], en["ov_bot"], N["t48_ovf"], N["t48_ovleak"], en["prec"])
    N["cs101_peak"] = 36.0 + f(need(L9, r"9 to 36 V in service, CS101's ([\d.]+) V peak on it under M2", "CS101's peak"))
    m = need(L9, r"D10 SMCJ40CA breakdown ([\d.]+) V minimum either way at 25 C, ([\d.]+) V at -20 C", "D10's breakdown")
    N["d10"] = (f(m, 1), f(m, 2))
    N["inp_ratio"] = (en["inp_bot"] * 0.99 / (en["inp_top"] * 1.01 + en["inp_bot"] * 0.99), en["inp_bot"] * 1.01 / (en["inp_top"] * 0.99 + en["inp_bot"] * 1.01))
    N["inp_on_at"] = N["t48_inp_h"] / N["inp_ratio"][0]
    N["clamp"] = 64.5
    N["pins_at_clamp"] = (N["clamp"] * N["inp_ratio"][1], N["clamp"] * en["uv_bot"] / (en["uv_top"] + en["uv_bot"]), N["clamp"] * en["ov_bot"] / (en["ov_top"] + en["ov_bot"]))
    vbst = (N["t48_cp_on"][0], N["t48_cp_off"][2])
    c1_lo = en["c1"] * 0.95 * (1 - any_m["endur"]) * (1 - any_m["ta_dn"]); c1_hi = en["c1"] * 1.05 * (1 + any_m["endur"]) * (1 + any_m["ta_up"])
    N["slew"] = (0.63 * vbst[0] / (en["r1"] * 1.01 * c1_hi), 0.63 * 12.0 / (en["r1"] * en["c1"]), 0.63 * vbst[1] / (en["r1"] * 0.99 * c1_lo))
    hi_f = (1 + T9["x7r"][0]) * (1 + T9["x7r"][1]) * (1 + T9["x7r"][2])
    lo_f = (1 - T9["x7r"][0]) * (1 - T9["x7r"][1]) * (1 - T9["x7r"][2])
    N["c_load"] = (T9["c_uf"] * 1e-6 * lo_f, T9["c_uf"] * 1e-6, T9["c_uf"] * 1e-6 * hi_f)
    N["inrush"] = (N["c_load"][0] * N["slew"][0], N["c_load"][1] * N["slew"][1], N["c_load"][2] * N["slew"][2])
    N["t_start"] = D["vmax"] / N["slew"][0]
    N["cbst_need"] = N["q7_qg"] / 1.0 + 10 * c1_hi
    # ---- the series resistance from the plug, hot (the in-service maximum) and its elements
    N["r_l2_hot"] = N["l2_dcr"] * (1 + CU_ALPHA * (F["air_hot"] + 40.0 * (N["ioc"][2] / N["l2_irms"]) ** 2 - 20.0))
    N["r_plug_dcp"] = [("the measured loop at its actual ceiling %s mOhm at 20 C (the cable, the D38999 pair, the inside lead, J_DCIN), %s m outside at %s C and %s m inside at %s C"
                        % (fmt(LOOP_CEIL20 * 1e3, 1), fmt(2 * SEL_CABLE_M, 1), fmt(T_OUT_HOT, 0), fmt(2 * LEAD_M, 1), fmt(F["air_hot"], 1)), N["cable_hot"], "SESSION ceiling, INFERRED"),
                       ("the NATO plug's pair, taken as a size 12 contact each (%s mV at %s A)" % (fmt(D["c12_mv"], 0), fmt(D["c12"], 0)), 2 * N["c12_r"], "ASSUMPTION"),
                       ("F1 at its rated current (typical drop)", N["f1_hot"], "MAKER"),
                       ("F1's holder, two clips", HOLDER_R, "ASSUMPTION"),
                       ("Q1 (BSC039N06NS) hot", N["q1_rds"] * FET_HOT, "NETLIST x ASSUMPTION")]
    N["r_dcp_vin"] = [("R19 4.5 mOhm at +1 %% and %s ppm/K at 75 C" % fmt(en["rsns_tcr"] * 1e6, 0), rs_hi, "CATALOGUE"),
                      ("Q7 (CSD19536KTT) hot", N["q7_rds"] * FET_HOT, "MAKER x ASSUMPTION"),
                      ("L2 (SRF1260-1R0Y series DCR) at the air plus its rise at the breaker's maximum", N["r_l2_hot"], "MAKER, INFERRED"),
                      ("board E's and board A's copper and the dock's VIN_RAW pins", BOARD_R, "ASSUMPTION")]
    N["r1_hot"] = sum(x for _n, x, _c in N["r_plug_dcp"])
    N["r2_hot"] = sum(x for _n, x, _c in N["r_dcp_vin"])
    N["r_hot"] = N["r1_hot"] + N["r2_hot"]
    pw_hi = lambda it: (band(it)[1] + E["oth"]) * E["vb_top"] / E["eta_fe"]
    def settle(vplug, rr, fe_power):                               # VIN_RAW where the plug, the resistance and a constant input power meet
        disc = vplug ** 2 - 4 * rr * fe_power(vplug)
        if disc <= 0:
            return None
        v = (vplug + math.sqrt(disc)) / 2.0
        for _ in range(60):
            disc = vplug ** 2 - 4 * rr * fe_power(v)
            v = (vplug + math.sqrt(max(disc, 0.0))) / 2.0
        return v
    N["vin9"] = settle(PLUG_V, N["r_hot"], lambda v: pw_hi(target(v)))
    N["i9"] = (PLUG_V - N["vin9"]) / N["r_hot"]
    N["dcp9"] = PLUG_V - N["i9"] * N["r1_hot"]
    N["ioc_margin"] = N["ioc"][0] / N["i9"] - 1.0
    N["pout9"] = (band(target(N["vin9"]))[1] + E["oth"]) * E["vb_top"]
    N["eta_floor"] = N["pout9"] / (N["ioc"][0] * (PLUG_V - N["ioc"][0] * N["r_hot"]))
    N["i_at_eta"] = lambda eta: (PLUG_V - math.sqrt(PLUG_V ** 2 - 4 * N["r_hot"] * N["pout9"] / eta)) / (2 * N["r_hot"])
    if abs(N["i_at_eta"](N["eta_floor"]) - N["ioc"][0]) > 1e-9 or abs(N["i_at_eta"](E["eta_fe"]) - N["i9"]) > 1e-6:
        refuse(4, "the coupled efficiency floor does not reproduce the trip and the operating point")
    N["fix_pout"] = (band(FIX_KNEE_IT)[1] + E["oth"]) * E["vb_top"]
    N["fix_eta"] = N["fix_pout"] / (N["ioc"][0] * (PLUG_V - N["ioc"][0] * FIX_RLOOP))
    N["fix_i"] = (PLUG_V - math.sqrt(PLUG_V ** 2 - 4 * FIX_RLOOP * N["fix_pout"] / round(N["fix_eta"], 6))) / (2 * FIX_RLOOP)
    i_tr = N["ioc"][0]
    N["board_at_trip"] = E["eta_fe"] * i_tr * (PLUG_V - i_tr * N["r_hot"]) / E["vb_top"] - E["oth"]
    N["board_excess"] = N["board_at_trip"] - band(target(N["vin9"]))[1]
    N["r19_f1"] = w2 / (F["f_hot_a"] * 0.99 * (1 + en["rsns_tcr"] * (T_COLD - 25.0)))
    N["trip_min_r19_f1"] = w0 / (N["r19_f1"] * 1.01 * (1 + en["rsns_tcr"] * (75.0 - 25.0)))
    N["top_margin"] = N["vin9"] - N["top_max"]
    N["dcp_noload"] = PLUG_V - N["vak"][2]
    N["l2_rise"] = 40.0 * (N["ioc"][2] / N["l2_irms"]) ** 2
    N["q7_w"] = N["ioc"][2] ** 2 * N["q7_rds"] * FET_HOT
    # the guard (board A U34) under the new knee
    m = need(ga, r"both channels at VIT ([\d.]+) V \(([\d.]+) to ([\d.]+)\) with (\d+) percent hysteresis", "U34's VIT")
    vit = (f(m, 2), f(m, 1), f(m, 3)); hys = f(m, 4) / 100.0
    r15 = f(need(ga, r'r\("R15", "(\d+)k 1%", "FE_UVS", "GND"', "R15")) * 1e3
    r14d = f(need(ga, r'r\("R14", "(\d+)k 1%", "VIN_RAW", "FE_UVS"', "R14")) * 1e3
    def guard(r14):
        fall = (vit[0] * (1 + r14 * 0.99 / (r15 * 1.01)), vit[1] * (1 + r14 / r15), vit[2] * (1 + r14 * 1.01 / (r15 * 0.99)))
        return fall, tuple(x * (1 + hys) for x in fall)
    N["guard_drawn"], N["guard_new"] = guard(r14d), guard(GUARD_R14_K * 1e3)
    N["guard_r"] = (r14d, r15)
    N["guard_margin"] = N["hiz_certain"] - N["guard_new"][0][2]
    gaf = flat(ga.replace("#", " "))
    m = need(gaf, r"Running at the lowest UV fall: FE_VZ ([\d.]+) V, FE_RUN ([\d.]+) V \(Q36 and Q37's VGS\(th\) is ([\d.]+) V at most\), EN ([\d.]+) V", "the guard's running levels")
    k = N["guard_new"][0][0] / N["guard_drawn"][0][0]
    N["guard_levels"] = (f(m, 1) * k, f(m, 2) * k, f(m, 3), f(m, 4) * k)
    N["ven_op"] = f(need(gaf, r"VEN\(OP\) ([\d.]+) to ([\d.]+) V\)", "U2's VEN(OP)"), 2)
    # ---- the envelope at the plug with the losses (B3): low side hot, high side with no loss
    env = {}
    for v in (9.0, 12.0, 24.0, 36.0):
        lo_pw = lambda vv: (min(band(target(vv))[0], E["iin_min"]) + E["oth"]) * E["vb_low"] / E["eta_fe"]   # noqa: E731
        vr = settle(v, N["r_hot"], lo_pw)
        blo = min(band(target(vr))[0], E["iin_min"])
        bhi = min(band(target(v))[1], E["iin_max"])
        vmx = settle(v, N["r_hot"], lambda vv: (min(band(target(vv))[1], E["iin_max"]) + E["oth"]) * E["vb_top"] / E["eta_fe"])
        imx = (min(band(target(vmx))[1], E["iin_max"]) + E["oth"]) * E["vb_top"] / E["eta_fe"] / vmx
        env[v] = dict(vin_lo=vr, board_lo=blo, board_hi=bhi, w_lo=blo * E["vb_low"] * E["eta_u3"], w_hi=bhi * E["vb_top"] * E["eta_u3"], i_max=imx, vin_imax=vmx)
    N["env"] = env
    N["cls"] = {}
    for name, (lo, plan, hi) in list(st.items()) + [("the functional warm-up (one module and the heater)", N["func"])]:
        for v in env:
            e = env[v]
            N["cls"][(name, v)] = "carried at every corner" if plan <= e["w_lo"] else ("only above the minimum" if plan <= e["w_hi"] else "not carried")
    N["func_ok"] = (N["func"][1] <= env[9.0]["w_lo"], N["func"][2] <= env[9.0]["w_hi"])
    e9 = env[9.0]
    N["phases"] = []
    for lab, ld in (("P0 start: the bridge boots on slot 2 (PS-SURV)", surv), ("P1 shed: PS-SURV with %s held" % ", ".join(SHED_OFF), N["shed"]),
                    ("P2 warm-up: P1 with the regulated mat on", N["func"])):
        N["phases"].append((lab, ld, [("carried at every corner" if x <= e9["w_lo"] else ("only above the minimum" if x <= e9["w_hi"] else "not carried")) for x in ld]))
    N["surplus"] = (e9["w_lo"] - N["shed"][1], e9["w_lo"] - N["shed"][2])
    N["shed_room"] = e9["w_lo"] - N["heater_w"]
    N["func_margin"] = e9["w_lo"] - N["func"][1]
    N["imax_all"] = max(e["i_max"] for e in env.values())
    if not N["imax_all"] < N["ioc"][0] or not N["ioc"][2] <= F["f_hot_a"]:
        refuse(4, "the breaker's band does not sit between the in-service maximum and F1's hot column")
    if not (N["uv_rise"][2] < N["dcp_noload"] and N["uv_fall"][2] < N["dcp9"] and N["top_margin"] > 0 and N["guard_margin"] >= 0.1):
        refuse(4, "an entry or knee threshold does not clear the 9.00 V plug's operating point")
    # ---- the owner-question caps with the losses (B3): F1's columns at a 9.00 V plug, the auxiliary loads taken off
    def cap(ia, rr):
        vr = PLUG_V - ia * rr
        return vr, (vr * ia * E["eta_fe"] - E["oth"] * E["vb_top"]) * E["eta_u3"]
    N["r_cold"] = (N["loop_floor_cold"] + 2 * N["c12_r"] + E["f1_rcold"] + HOLDER_R + N["q1_rds"] + rs_lo + N["q7_rds"]
                   + N["l2_dcr"] * cold_f + BOARD_R)
    N["caps"] = [("F1's %s C column, %s A, the losses hot" % (fmt(F["f_col"], 0), fmt(F["f_hot_a"], 1)), F["f_hot_a"], N["r_hot"]) + cap(F["f_hot_a"], N["r_hot"]),
                 ("F1's 0 C column, %s A, the losses cold" % fmt(F["der"][0], 1), F["der"][0], N["r_cold"]) + cap(F["der"][0], N["r_cold"]),
                 ("a 15 A MINI's %s C column, %s A, the losses hot" % (fmt(F["f_col"], 0), fmt(F["der15_hot"], 0)), F["der15_hot"], N["r_hot"]) + cap(F["der15_hot"], N["r_hot"])]
    N["check_ref"] = [(ia, (PLUG_V - ia * 0.115511) * ia * E["eta_fe"] * E["eta_u3"]) for ia in (F["f_hot_a"], F["der"][0], F["der15_hot"])]
    # ---- the smaller fuse, with the tolerances shown (minor)
    m = need(fz, r"7\.5A 7\.5 ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)", "the 0997 7.5 A derating row")
    N["f75_hot"] = f(m, 6)
    vcl = T9["vcl"]
    N["f75_lm"] = N["f75_hot"] * (vcl[0] / vcl[2]) * (0.99 / 1.01)
    N["f75_tps"] = N["f75_hot"] * (w0 / w2) * (rs_lo / rs_hi)
    # ---- SOA: a start into a resistive fault under the breaker (no power limit), both FETs, the conservative whole-pulse reading
    kl = soa_lines_ktt()
    N["ktt_lines"] = kl
    k_lines = {1e-4: kl["100us"], 1e-3: kl["1ms"], 1e-2: kl["10ms"]}
    q_lines = soa_lines()
    d_lines = {1e-5: q_lines["10us"], 1e-4: q_lines["100us"], 1e-3: q_lines["1ms"], 1e-2: q_lines["10ms"]}
    N["ktt_at"] = {k: soa_at(v, D["vmax"]) for k, v in kl.items() if k != "DC"}
    scan = []
    for fet, lines in (("CSD19532Q5B (as drawn)", d_lines), ("CSD19536KTT (selected)", k_lines)):
        worst = max((fault_scan(lines, D["vmax"], s, c, N["ioc"][2], N["isc"][2], N["toc"][2], N["tau"][2], N["t48_tsc"][1], T9["derate"]) + (s, c))
                    for s in (N["slew"][0], N["slew"][2]) for c in (N["c_load"][0], N["c_load"][2]))
        start = max(c * s / (T9["derate"] * soa_t(lines, D["vmax"], D["vmax"] / s)) for s in (N["slew"][0], N["slew"][2]) for c in (N["c_load"][0], N["c_load"][2]))
        scan.append((fet, worst, start))
    N["scan"] = scan
    N["gfs"] = f(need(kt, r"gfs Transconductance VDS = 10V, ID = 100A (\d+) S", "CSD19536KTT gfs"))
    N["idm"] = f(need(kt, r"IDM Pulsed Drain Current\(1\) (\d+) A", "CSD19536KTT IDM"))
    N["a_g"] = N["gfs"] * N["slew"][2]
    N["hs_start"] = start_into_short(k_lines, D["vmax"], N["a_g"], N["isc"][2], N["tau"][2], N["t48_tsc"][1], T9["derate"])
    N["t_d"] = N["tau"][2] + N["t48_tsc"][1]                       # a ramp's filter lag bound plus the loaded propagation
    N["i_allow"] = N["idm"] * T9["derate"]
    N["v_on_max"] = N["ov_rise"][2]
    N["l_min"] = N["v_on_max"] * N["t_d"] / (N["i_allow"] - N["isc"][2])
    if not scan[1][1][0] < 1.0 or not scan[1][2] < 1.0 or not N["hs_start"][2] < 1.0:
        refuse(4, "the selected FET's fault start is not under its derated chart")
    # ---- B5: R-b's register value and its actual-current bound; the dead pack's charge
    bq = flat("".join(pdf_pages("bq25731", True)))
    m = need(bq, r"REG0x03/02\(\) = 0x0200H \S(\d+)% ([\d.]+)%", "the 0x0200 accuracy row")
    N["rb_err"] = (f(m, 1) / 100.0, f(m, 2) / 100.0)
    need(bq, r"With 5-m. sense resistor, the charger provides charge current range of 0 A to 16\.256 A, with a 128-mA step resolution", "the 5 mOhm LSB")
    need(bq, r"5-m. RSR sensing", "the accuracy rows' sense resistor")
    m = need(bq, r"resistor, VBAT above 2048 mA VSYS_MIN\((\d+)°C to REG0x03/02\(\) = 0x0400H (\d+)°C\)", "the accuracy rows' condition")
    N["rb_temp"] = (f(m, 1), f(m, 2))
    N["rb_set"] = 1.024
    N["rb_max"] = N["rb_set"] * (1 + N["rb_err"][1]) / (1 - 0.01)
    N["rb_min"] = N["rb_set"] * (1 - N["rb_err"][0]) / (1 + 0.01)
    N["q2_w"] = N["rb_max"] * P["vsd_max"]
    N["q2_rise"] = N["q2_w"] * P["rja"]
    N["q2_tj"] = F["air_hot"] + N["q2_rise"]
    N["dead_charge_w"] = N["rb_max"] * RULE_SRN_V
    N["dead_charge_w_max"] = N["rb_max"] * R["cv_max"]
    need(bq, r"Upon POR, ChargeCurrent\(\) is 0 A", "ChargeCurrent at POR")
    # ---- B4: the weak-source envelope as monotone intervals, its energies, and the elements' obligations
    tc = D["tc"]
    rating = D["rating"]
    edges = [rating * tc[1][0], rating * tc[2][0], rating * tc[3][0], rating * tc[4][0]]
    N["intervals"] = [(None, edges[0], None), (edges[0], edges[1], tc[1][2]), (edges[1], edges[2], tc[2][2]), (edges[2], edges[3], tc[3][2]), (edges[3], N["i_pf_spec"], tc[4][2])]
    N["i2t_top"] = [(lo, hi, t, (hi ** 2 * t) if t else None) for lo, hi, t in N["intervals"]]
    s_cm2 = SEL_MM2 / 100.0
    N["adiab"] = [(lo, hi, t, hi * hi * t * CU_RHO_20 * 1e-4 / (s_cm2 ** 2 * CU_CV)) for lo, hi, t in N["intervals"][2:]]
    N["contact_eq"] = [(lo, hi, t, hi * hi * t / D["c12"] ** 2) for lo, hi, t in N["intervals"][1:4]]
    m = need(fz, r"Note: The typical I2t is an average value calculated from the breaking capacity tests by using the melting time before the arcing occurs\.", "the I2t note")
    N["f1_melt"] = E["f1_i2t"]
    N["sel_ipf_cold"] = D["vmax"] / ((N["constr"][0]) * cold_f)
    return N


# ============================================================================================ the dependency round (2 October 2026)
def dependency_round(R, T):
    """The owner's instruction of 2 October 2026 (the coordinator's dependency round): each missing specification apart, the
    claim it affects, what a maker's answer and what a bench sample could establish; and the bounded fallback for VSYS's
    hold-up with no battery (E11-07, VSYS's capacitance first), sized so it does not lean on the charger's transient response."""
    B, P, E, F, N = R["B"], R["P"], R["E"], R["F"], R["N"]
    G = {}
    ga = T["gen_a"]
    # ---- the charger's regulation rows and the POR answer
    bq9 = flat(pdf_pages("bq25731", True)[8])
    need(bq9, r"REG0x05/04\(\) = 0x41A0H \S0\.5% 0\.5%", "the 16.8 V ChargeVoltage accuracy row")
    need(bq9, r"VBAT_REG_ACC regulation accuracy REG0x05/04\(\) = 0x5208H \(0°C to 85°C\)", "the ChargeVoltage rows' temperature condition")
    G["cv_acc"] = 0.005
    G["cv_min"] = B["cv4s"] * (1 - G["cv_acc"])
    G["v_floor"] = B["vsysmin4s"]
    G["heat_en_v"] = f(need(ga, r"it starts at about ([\d.]+) V \(VEN_RISE", "the heater buck's enable divider"))
    for st_ in ("SLOT_EN2", "DEV_EN", "PA_EN", "HF_EN", "POE_EN", "PD_EN"):
        need(ga, r'lm5176\("\w+", "U\d+", "VBAT", "[^"]+", "%s"' % st_, "the VBAT stage enabled by %s" % st_)
    e2e = re.sub(r"<[^>]+>", " ", open(read("e2e_por"), encoding="utf-8", errors="replace").read())
    e2e = flat(e2e)
    G["por_ma"] = f(need(e2e, r"Looks like there is a mistake in the description\. The POR value is indeed (\d+)mA", "TI's E2E answer on the POR value"))
    need(flat("".join(pdf_pages("bq25731", True))), r"Upon POR, ChargeCurrent\(\) is 0 A", "the register description's POR text")
    # ---- the kit's declared load steps (r4a's loop design, recovered by L4-E8; session targets, INFERRED there)
    ld = text("loopdesign")
    eff = lambda net: f(need(ga, r'_intent\.rail\("%s",(?:(?!_intent\.rail\().){0,600}?efficiency=([\d.]+)' % re.escape(net), "%s's declared efficiency" % net, re.S))
    steps = []
    m = need(ld, r"# S2: VBAT 10 to 16\.8 V -> ([\d.]+) V .*?29\.5 W; step (\d+) A \(a 5G burst, INFERRED\)", "the S2 step", re.S)
    steps.append(("S2 slot rail (+5V_S2, a 5G burst)", f(m, 2), f(m, 1), S2_ETA, "ASSUMPTION (+5V_DEV's declared 0.90)"))
    m2 = need(ld, r"35 W; step (\d+) A\.", "the SD step")
    steps.append(("SD device rail (+5V_DEV)", f(m2, 1), f(m, 1), eff("+5V_DEV"), "NETLIST"))
    m = need(ld, r"# PA: VBAT -> ([\d.]+) V .*?step ([\d.]+) A \(key-up of a 30 W carrier at 40 percent\)", "the PA step", re.S)
    steps.append(("PA rail (+13V8_PA, a 30 W carrier keyed)", f(m, 2), f(m, 1), eff("+13V8_PA"), "NETLIST"))
    m = need(ld, r"# HF: VBAT -> ([\d.]+) V .*?24 W; step (\d+) A\.", "the HF step", re.S)
    steps.append(("HF rail (+12V_HF)", f(m, 2), f(m, 1), eff("+12V_HF"), "NETLIST"))
    m = need(ld, r"# POE: VBAT -> ([\d.]+) V .*?step ([\d.]+) A\.", "the PoE step", re.S)
    steps.append(("PoE rail (+54V_POE)", f(m, 2), f(m, 1), eff("+54V_POE"), "NETLIST"))
    m = need(ld, r"45 W at 15 V, 15 W at 5 V; step (\d+) A\.", "the PD step")
    steps.append(("USB-C PD outlet at 15 V (PD_VPWR)", f(m, 1), 15.0, eff("PD_VPWR"), "NETLIST"))
    heat = f(need(text("red2_py"), r'HEAT_REG = same\(([\d.]+), "S"\)', "the regulated mat"))
    G["steps"] = [(nm, i, v, eta, i * v / eta, cl) for nm, i, v, eta, cl in steps] + [("the pack heater mat, regulated (on)", None, None, None, heat, "RECORD")]
    base = N["shed"][1]
    env36, env9 = N["env"][36.0]["w_lo"], N["env"][9.0]["w_lo"]
    G["admit"] = [(nm, dp, base + dp <= env36) for nm, _i, _v, _e, dp, _c in G["steps"]]
    adm = [(nm, dp) for nm, dp, ok in G["admit"] if ok]
    G["worst"] = max(adm, key=lambda x: x[1])
    # ---- the hybrid polymer parts (Panasonic ZK sheet), the diode (Diodes DS13012), the resistor (Yageo RC_L V.12)
    z1, z2 = flat(pdf_pages("zk", True)[0]), flat(pdf_pages("zk", True)[1])
    m = need(z2, r"470\s+10\.0\s+10\.2\s+10\.5\s+G\s+(\d+)\s+(\d+)\s+([\d.]+)\s+EEHZK1E471P", "the ZK 471P row")
    G["c471"], G["esr471"] = 470e-6, f(m, 2) * 1e-3
    m = need(z2, r"180\s+8\.0\s+10\.2\s+10\.5\s+F\s+(\d+)\s+(\d+)\s+([\d.]+)\s+EEHZK1V181P", "the ZK 181P row")
    G["c181"], G["esr181"] = 180e-6, f(m, 2) * 1e-3
    G["zk_tol"] = f(need(z1, r"Capacitance tolerance\s+±(\d+) %", "the ZK tolerance")) / 100.0
    G["zk_end"] = f(need(z1, r"\+125 ℃ ± 2 ℃, 4000 h, apply the rated ripple current without exceeding the rated voltage\. Capacitance change Within ±(\d+)% of the initial value", "the ZK endurance row")) / 100.0
    need(z1, r"I ≦ 0\.01 CV \(μA\)", "the ZK leakage row")
    G["zk_leak"] = 0.01 * 470 * 25 * 1e-6
    need(z1, r"Characteristics dependencies in frequency and low temperature are as small as polymer type", "the ZK low-temperature sentence")
    G["k_eff"] = (1 - G["zk_tol"]) * (1 - G["zk_end"]) * K_COLD_HYB
    dz = flat("".join(pdf_pages("b540c", True)))
    m = need(dz, r"B520C, B530C, B540C \S ([\d.]+) ([\d.]+) Forward Voltage Drop VF", "B540C VF")
    G["vf25"] = f(m, 2)
    need(dz, r"IF = 5\.0A, TA = \+25°C", "B540C VF condition")
    G["io"] = f(need(dz, r"Average Rectified Output Current IO ([\d.]+)", "B540C IO"))
    G["vf"] = G["vf25"] + VF_COLD_ADD
    yr = flat("".join(pdf_pages("yageo_rc", True)))
    need(yr, r"Each type rated power at 70", "RC_L rated at 70 C")
    G["p_rc2512"] = f(need(yr, r"RC2512=(\d)W, 2W", "RC2512's rating"))
    # ---- the hold-up arithmetic (no battery, the charger delivering only its pre-step power for T_RESP)
    G["c_can_eff"] = G["c471"] * G["k_eff"]
    G["c_bank_eff"] = BANK_N * G["c_can_eff"]
    G["v1b"] = G["cv_min"] - BANK_N * G["zk_leak"] * R_CH
    v2b = G["v_floor"] + G["vf"]
    G["v2b"] = v2b
    per = 0.5 * (G["v1b"] ** 2 - v2b ** 2) - G["vf"] * (G["v1b"] - v2b)          # J per farad delivered into VSYS
    G["e_bank"] = G["c_bank_eff"] * per
    G["c_dir_eff"] = G["c181"] * G["k_eff"]
    G["e_dir"] = 0.5 * G["c_dir_eff"] * (G["cv_min"] ** 2 - G["v_floor"] ** 2)
    G["e_tot"] = G["e_bank"] + G["e_dir"]
    G["hold"] = [(nm, dp, G["e_tot"] / dp, ok) for nm, dp, ok in G["admit"]]
    G["worst_hold"] = G["e_tot"] / G["worst"][1]
    G["cans_for"] = [(t, max(0, math.ceil((G["worst"][1] * t - G["e_dir"]) / (G["c_can_eff"] * per)))) for t in (0.25e-3, 0.5e-3, 1e-3, 2e-3, 5e-3)]
    G["i_step_floor"] = G["worst"][1] / G["v_floor"]
    # ---- inrush and placement
    G["i_ch_pk"] = R["cv_max"] / R_CH
    G["p_ch_pk"] = R["cv_max"] ** 2 / R_CH
    G["c_bank_max"] = BANK_N * G["c471"] * (1 + G["zk_tol"])
    G["tau_ch"] = R_CH * G["c_bank_max"]
    G["e_ch"] = 0.5 * G["c_bank_max"] * R["cv_max"] ** 2
    na = T["net_a"]
    def nom_uf(net):
        s = 0.0
        for ref, _p in netlist_nodes(na, net):
            if ref.startswith("C"):
                v = netlist_value(na, ref)
                mm = re.match(r"([\d.]+)(u|n)", v)
                if mm:
                    s += float(mm.group(1)) * (1.0 if mm.group(2) == "u" else 1e-3)
        return s * 1e-6
    G["c_ceramic_nom"] = nom_uf("VBAT") + nom_uf("CELL_FUSED")
    G["c_pack_side_max"] = G["c_ceramic_nom"] * 1.1 + G["c181"] * (1 + G["zk_tol"])
    pc = flat(T["primcfg"])
    m = need(pc, r"about ([\d.]+) or ([\d.]+) A \(RSNS = 1 steps of 22\.2 mV over 2 mOhm\) at about (\d+) to (\d+) us", "the image's ASCD")
    G["ascd_a"], G["ascd_us"] = f(m, 1), f(m, 3) * 1e-6
    M2 = red2_model()
    G["r_loop"] = 4 * M2.pb.R_CELL["lo"] / 3 + M2.pb.R_DIST
    G["i_conn_pk"] = 4 * 4.2 / G["r_loop"]
    G["tau_conn"] = G["r_loop"] * G["c_pack_side_max"]
    G["t_over_ascd"] = G["tau_conn"] * math.log(G["i_conn_pk"] / G["ascd_a"])
    G["t_to_1v6"] = G["c_pack_side_max"] * 1.6 / 0.5
    # ---- the 9 V plug and the warm-CUV state
    s2 = [dp for nm, _i, _v, _e, dp, _c in G["steps"] if nm.startswith("S2")][0]
    G["s9_deficit"] = base + s2 - env9
    G["s9_time"] = G["e_tot"] / G["s9_deficit"] if G["s9_deficit"] > 0 else None
    G["s2_vsys"] = P["vsys_cuv"]
    # ---- the dependency rows' figures
    G["q2_i_lim"] = (P["tj_max"] - F["air_hot"]) / (P["vsd_max"] * P["rja"])
    G["clamp_x"] = N["rb_max"] / B["iclamp"]
    G["gfs_x"] = 1.0 / N["hs_start"][2]
    G["por_w"] = G["por_ma"] * 1e-3 * P["vsd_max"]
    return G


def dep_rows(R):
    """The dependency table: one row per specification the record leaves to a maker (TI for every row but N4), with what a
    maker's answer and what a bench sample can establish. The figures are this record's; the record's table repeats the rows."""
    B, P, N, G = R["B"], R["P"], R["N"], R["G"]
    return [
        dict(id="D1", name="N1a, VSYS's DC regulation with no battery",
             missing="no row gives VSYS's regulation with no battery current: VBAT_REG_ACC +-%s %% holds for a charge voltage at 0 to 85 C (p.9); section 11 (p.92) says the system is powered through the charger; Figures 10-4 and 10-5 (p.89) are typical power-up curves of a 2-cell system without battery" % fmt(G["cv_acc"] * 100, 1),
             claim="section 2's row 'absent, or both FETs open: VSYS at ChargeVoltage' and every S4 figure of 3g and 3h (U-04 in S4 at all)",
             maker="that the voltage loop holds VSYS at ChargeVoltage with no battery current, with the +-%s %% row applying: production-wide if TI states it as a limit" % fmt(G["cv_acc"] * 100, 1),
             bench="that one unit enters and holds the mode at the conditions tried; the mode is a design behaviour, and VSYS needs only %s V against ChargeVoltage's floor %s V, a %s V margin that is large against any plausible unit spread once the mode is shown (an engineering margin)" % (fmt(G["v_floor"], 1), fmt(G["cv_min"], 3), fmt(G["cv_min"] - G["v_floor"], 3)),
             cannot="that every unit and silicon revision enters the mode, or the accuracy below 0 C, where the +-%s %% row stops" % fmt(G["cv_acc"] * 100, 1),
             method="pack absent, P1's load and the envelope's maximum on VSYS, VBUS20 from 19.1 to 21 V, VSYS on a calibrated meter at -20, 25 and 62 C ambient",
             negative="arrangement (A) does not run S4: (B), a charger with a battery FET that regulates VSYS by design (an architecture change; five records reopen)"),
        dict(id="D2", name="N1b, VSYS's load-step response with no battery",
             missing="no load-transient figure or limit for the system output (Figure 10-17, p.91, is the OTG output's)",
             claim="S4 operation through the kit's load steps (3g, R-c): the declared steps of section 10, up to %s W" % fmt(G["worst"][1], 2),
             maker="a characterised deviation and recovery, or a minimum loop bandwidth; production-wide only if TI states a limit",
             bench="one unit's deviation and recovery at the steps tried; with the bank sized for %s ms, a measured recovery of %s ms or less is a five-fold margin, large against a loop's plausible spread (L, C and gain tolerances): an engineering margin" % (fmt(T_RESP * 1e3, 1), fmt(T_RESP * 1e3 / 5, 1)),
             cannot="a recovery time bounded for every unit",
             method="pack absent, an electronic load stepping VSYS by each declared step with a 1 us edge, VSYS and the inductor current on a scope, at the three ambients",
             negative="the bank of section 10 carries the step for %s ms with no help from the charger; a longer recovery needs more cans (%s for 2 ms) or (B)" % (fmt(G["worst_hold"] * 1e3, 3), [n for t, n in G["cans_for"] if abs(t - 2e-3) < 1e-9][0])),
        dict(id="D3", name="N2 (Q-TI-3), VSYS with CHRG_INHIBIT = 1 or ChargeCurrent 0 and no battery current",
             missing="9.4.1 (p.35) lets the host end a charge by CHRG_INHIBIT or ChargeCurrent 0; 9.3.21.5 (p.34) keeps the converter operating with charge disabled only in the BATOVP paragraph; nothing states what VSYS does in either state with no battery current",
             claim="R-a's S2 row and REQ-077's hold in every state (section 4): the charger still carrying the kit while the charge is held",
             maker="the control mode with charge inhibited, production-wide (a design behaviour)",
             bench="one unit's mode with the bit set and with ChargeCurrent 0, pack absent and in S2: a deterministic logic behaviour, so one sample is strong evidence for that silicon revision",
             cannot="that no later revision changes the mode, nor how a temperature-dependent comparator moves it",
             method="the pack emulated in S2 (a supply behind a diode), the bit set and cleared under P1's load, VSYS and the switch node recorded",
             negative="REQ-077's hold cannot use the bit with this charger; ChargeCurrent 0 is tried; if both fail, (B) or a requirement change to REQ-077's acceptance (the owner's)"),
        dict(id="D4", name="N3 (Q-TI-2), whether the charger charges before any host write",
             missing="9.6.3 says the charge starts when the host writes ChargeCurrent(); the register's reset value encodes 256 mA and its description says 0 A at POR. TI's expert on E2E thread 1316778 (held) answers: the POR value is %s mA, the description is in error; 9.6.3 is not addressed" % fmt(G["por_ma"], 0),
             claim="section 2's ChargeCurrent at POR (corrected in this round), R-a's persistence after a charger POR, CONOPS's hostless %s mA" % fmt(G["por_ma"], 0),
             maker="a datasheet erratum: production-wide (a forum answer is TI's word but not a revised document)",
             bench="one unit's SRP-SRN current after POR with no host: a logic behaviour, strong for that revision",
             cannot="other revisions",
             method="no host, the pack at 3.6 V a cell, the SRP-SRN current read for 200 s after POR",
             negative="a hostless charge at %s mA is safe (inside the gauge's window; Q2's diode %s W); no hostless charge leaves a hostless kit's dead pack uncharged: a stated limitation, no change" % (fmt(G["por_ma"], 0), fmt(G["por_w"], 3))),
        dict(id="D5", name="N4, VSYS's effective capacitance at 16.884 V against TI's 50 uF",
             missing="TI states %s uF effective necessary (10.1, p.83); the fitted MLCCs' capacitance at 16.9 V of DC bias is not printed in the held Yageo CC sheet (a capacitor maker's item, not TI's)" % fmt(B["csys_uf"], 0),
             claim="N1's premise (stable regulation) and E11-07",
             maker="the capacitor makers' DC-bias curves: typical per part number, not limits",
             bench="one board's VSYS capacitance at 16.8 V of bias: a sample",
             cannot="lot-to-lot spread",
             method="an LCR meter with DC bias on the populated node, or each part number on a bias fixture",
             negative="none needed: one EEHZK1V181P on VSYS gives %s uF at its stacked worst, with no DC-bias dependence, over %s uF by design" % (fmt(G["c_dir_eff"] * 1e6, 2), fmt(B["csys_uf"], 0))),
        dict(id="D6", name="Q-TI-7, 0-V charging before the gauge's SUV check",
             missing="SLUUAQ3A 4.9: with PCHG_COMM = 1 the hardware 0-V charging circuit is enabled below the minimum operation voltage; nothing states its timing against the SUV check of 3.2.1",
             claim="R-d (the image keeps PCHG_COMM 1 and the SUV check): no cell below 1.0 V charged (Samsung)",
             maker="the gauge's sequence, production-wide",
             bench="one gauge with a cell simulator: a logic sequence, strong for that firmware and revision",
             cannot="other firmware revisions",
             method="a cell simulator at 0.8 V a cell, the charger enabled, the stack current logged from the gauge's wake",
             negative="ZVCHG Exit Threshold set to stop 0-V charging, or a precharge FET (arrangement (C)'s part) with PCHG_COMM 0"),
        dict(id="D7", name="the clamp's maximum under VSYS_MIN",
             missing="8.5 (p.10) prints the clamp under VSYS_MIN, %s mA, as typical only" % fmt(B["iclamp"] * 1000, 0),
             claim="R-b's case (iii) and Q2's diode below VSYS_MIN (section 4)",
             maker="a maximum, production-wide",
             bench="one unit's clamp current; Q2 reaches %s C only at %s A on its %s C/W, %s times the typical clamp, so a sample near typical is a large engineering margin" % (fmt(P["tj_max"], 0), fmt(G["q2_i_lim"], 3), fmt(P["rja"], 0), fmt(G["q2_i_lim"] / B["iclamp"], 2)),
             cannot="a maximum for every unit",
             method="SRN held at 11 V by a sink, ChargeCurrent 0x0200, the current read at -20, 25 and 62 C",
             negative="a maximum over %s A: Q2's copper improved, or arrangement (C)" % fmt(G["q2_i_lim"], 3)),
        dict(id="D8", name="ChargeCurrent's accuracy at 0x0200 outside 0 to 85 C, and under 0x0200",
             missing="p.10's rows hold for VBAT above VSYS_MIN at %s to %s C; no accuracy outside that range, nor for any setting under 0x0200" % (fmt(N["rb_temp"][0], 0), fmt(N["rb_temp"][1], 0)),
             claim="R-b's case (ii) and Q2's %s C (section 4, CONDITIONAL)" % fmt(N["q2_tj"], 1),
             maker="limits outside the range, production-wide",
             bench="one unit at -20 and 62 C ambient: a sample; Q2's limit %s A is %s times R-b's %s A, so a sample within about 1.3 A is an engineering margin" % (fmt(G["q2_i_lim"], 3), fmt(G["q2_i_lim"] / N["rb_max"], 2), fmt(N["rb_max"], 4)),
             cannot="production limits",
             method="as D7 with SRN at 13 V",
             negative="the charger's temperature bounded inside the row by layout (E11-22), or Q2's copper improved"),
        dict(id="D9", name="the TPS48110-Q1's overcurrent delay at CTMR 22 nF",
             missing="SLUSEE5E p.10 prints %s us typical only" % fmt(N["t48_toc22"] * 1e6, 0),
             claim="V-A08's %s ms (the nuisance margin) and the fault scan's %s ms (A11-11)" % (fmt(N["toc"][0] * 1e3, 3), fmt(N["toc"][2] * 1e3, 3)),
             maker="a minimum and a maximum over temperature, production-wide",
             bench="one unit's delay: a sample; the scan's worst fault ends on the short-circuit trip (3c), so the delay's maximum does not decide it; its minimum sets V-A08",
             cannot="the spread across units",
             method="a current step over the threshold at three temperatures, the sense step to PD timed",
             negative="V-A08's allowance re-derived on TI's minimum, or CTMR raised"),
        dict(id="D10", name="the CSD19536KTT's transconductance bound",
             missing="SLPS540C p.3 prints gfs %s S typical only" % fmt(N["gfs"], 0),
             claim="the start into a hard short (3c, %s of the derated chart)" % fmt(N["hs_start"][2], 3),
             maker="a maximum, or the transfer curve's spread",
             bench="one unit's transfer curve; the headroom (%s times) is not large against a plausible transconductance spread, so a sample is no margin" % fmt(G["gfs_x"], 3),
             cannot="a bound across units",
             method="a pulsed transfer curve at VDS 10 V, 10 to 100 A",
             negative="a slower gate slew for the start (C1 larger) or a power-limiting controller"),
    ]


def render_dependency(R, p):
    G, N, E, P, B = R["G"], R["N"], R["E"], R["P"], R["B"]
    p("9. THE DEPENDENCY ROUND: EACH MISSING SPECIFICATION, THE CLAIM IT DECIDES, WHO CAN SETTLE IT (2 October 2026)")
    p("   the held answer on the POR value: TI's expert on E2E thread 1316778: \"The POR value is indeed %smA\" (the register description's 0 A is in error) (MAKER, forum)" % fmt(G["por_ma"], 0))
    for r in dep_rows(R):
        p("   %s %s (MAKER, INFERRED)" % (r["id"], r["name"]))
        for k, lab in (("missing", "missing"), ("claim", "the claim"), ("maker", "a maker's answer would establish"), ("bench", "a bench sample could establish"),
                       ("cannot", "a bench sample cannot establish"), ("method", "the bench method"), ("negative", "if the answer is negative")):
            p("     %s: %s" % (lab, r[k]))
    p("")
    p("10. THE BOUNDED FALLBACK (E11-07, VSYS's capacitance first): A HOLD-UP THAT DOES NOT LEAN ON THE CHARGER'S TRANSIENT RESPONSE")
    p("   the criterion: with no battery (S4) VSYS sits at ChargeVoltage, at least %s V (16.8 V less TI's %s %%, p.9, MAKER), and must stay above VSYS_MIN %s V"
      % (fmt(G["cv_min"], 3), fmt(G["cv_acc"] * 100, 1), fmt(G["v_floor"], 1)))
    p("     through a step while the charger delivers only its pre-step power for %s ms (ASSUMPTION: the time the charger could take to respond;" % fmt(T_RESP * 1e3, 1))
    p("     D2's bench reading turns it into a margin); the VBAT stages' EN/UVLO pins are driven by logic (the slot, device, PA, HF, PoE and PD stages)")
    p("     and the heater buck's divider starts it at about %s V, so no VSYS divider sets a line above VSYS_MIN; A-14's assumed 10.0 V converter floor" % fmt(G["heat_en_v"], 1))
    p("     is under it too (NETLIST, INFERRED)")
    p("   the kit's declared steps (r4a's loop design, INFERRED there; efficiencies from gen_sch_a.py; the mat from hc2) at VSYS, and whether R-c's envelope")
    p("     admits each on top of P1's plan %s W at the widest source (36 V, %s W) (INFERRED):" % (fmt(N["shed"][1], 2), fmt(N["env"][36.0]["w_lo"], 2)))
    for nm, i, v, eta, dp, cl in G["steps"]:
        adm = [ok for n2, d2, ok in G["admit"] if n2 == nm][0]
        hold = [h for n2, d2, h, ok in G["hold"] if n2 == nm][0]
        src = ("%s A at %s V over %s (%s)" % (fmt(i, 1), fmt(v, 2), fmt(eta, 2), cl)) if i is not None else "%s W (%s)" % (fmt(dp, 2), cl)
        p("     %-44s %s: %s W at VSYS; %s; the fallback holds it %s ms (INFERRED)" % (nm, src, fmt(dp, 2), "admitted in S4" if adm else "not admitted in S4 (R-c holds it)", fmt(hold * 1e3, 3)))
    p("   the worst admitted step: %s, %s W, %s A at the floor (INFERRED)" % (G["worst"][0], fmt(G["worst"][1], 2), fmt(G["i_step_floor"], 3)))
    p("   THE FALLBACK (SESSION; a register row, E11-24, never applied):")
    p("     a direct can on VSYS: one Panasonic EEHZK1V181P (180 uF 35 V, F size 8.0 x 10.2 mm, ESR %s mOhm; LCSC C242139); and a hold-up bank: %d x EEHZK1E471P"
      % (fmt(G["esr181"] * 1e3, 0), BANK_N))
    p("     (470 uF 25 V, G size 10.0 x 10.2 mm, ESR %s mOhm; C242138), charged from VSYS through R_CH %s Ohm (Yageo RC2512FK-07330RL, %s W at 70 C, C137025) and"
      % (fmt(G["esr471"] * 1e3, 0), fmt(R_CH, 0), fmt(G["p_rc2512"], 0)))
    p("     discharging into VSYS through D_H, a Diodes B540C-13-F (40 V, %s A, VF at most %s V at 5 A and 25 C; C72264) (MAKER, CATALOGUE)" % (fmt(G["io"], 1), fmt(G["vf25"], 2)))
    p("   the capacitance's derating (Panasonic ZK sheet): +-%s %% tolerance, endurance within +-%s %%, no DC-bias dependence (an aluminium hybrid polymer part, its class),"
      % (fmt(G["zk_tol"] * 100, 0), fmt(G["zk_end"] * 100, 0)))
    p("     the low-temperature change not printed (\"as small as polymer type\"): %s at -20 C (ASSUMPTION); so %s of nominal at the stacked worst (MAKER, ASSUMPTION)"
      % (fmt(K_COLD_HYB, 2), fmt(G["k_eff"], 3)))
    p("   the bank: %s uF effective; it sits at %s V (the leakage, 0.01 CV uA a can, across R_CH) and gives into VSYS down to %s V (VSYS_MIN plus D_H's"
      % (fmt(G["c_bank_eff"] * 1e6, 1), fmt(G["v1b"], 3), fmt(G["v2b"], 2)))
    p("     %s V: its 25 C maximum plus %s V at -20 C, ASSUMPTION): %s mJ net of the diode; the direct can %s uF effective from %s to %s V: %s mJ;"
      % (fmt(G["vf"], 2), fmt(VF_COLD_ADD, 2), fmt(G["e_bank"] * 1e3, 2), fmt(G["c_dir_eff"] * 1e6, 2), fmt(G["cv_min"], 3), fmt(G["v_floor"], 1), fmt(G["e_dir"] * 1e3, 2)))
    p("     %s mJ in all, the MLCCs not counted (N4) (INFERRED)" % fmt(G["e_tot"] * 1e3, 2))
    p("   against the worst admitted step: %s ms of hold, over the %s ms assumed (MEETS, CONDITIONAL on T_RESP); the least cans for a hold of: %s (INFERRED)"
      % (fmt(G["worst_hold"] * 1e3, 3), fmt(T_RESP * 1e3, 1), ", ".join("%s ms %d" % (fmt(t * 1e3, 2), n) for t, n in G["cans_for"])))
    p("   size: four G cans (10.3 mm square lands, 10.5 mm tall at most), one F can, an SMC diode and a 2512: about 5.5 cm2 of board A (INFERRED)")
    p("   placement: board A, on VBAT (the charger's VSYS); board P is behind the pack's FETs, which are open in S4, so it cannot hold VSYS there (NETLIST, INFERRED);")
    p("     the height and the zone are Layer 9's (L4-E8 placed six G cans on board A's VBUS20, so the class fits the board) (INFERRED)")
    p("   inrush, the entry and F1: the bank charges through R_CH at %s mA at most, %s W at most against the resistor's %s W at 70 C (the inside air %s C), with"
      % (fmt(G["i_ch_pk"] * 1e3, 1), fmt(G["p_ch_pk"], 3), fmt(G["p_rc2512"], 0), fmt(R["F"]["air_hot"], 1)))
    p("     a time constant of %s s and %s J per full charge; the direct can charges with VSYS under the charger's own start (0.5 A until 1.6 V, 3 min allowed,"
      % (fmt(G["tau_ch"], 3), fmt(G["e_ch"], 3)))
    p("     9.3.21.8; %s ms to 1.6 V at that current); the entry's start ends before U34 releases the front end (79 ms at least), so neither the entry's"
      % fmt(G["t_to_1v6"] * 1e3, 2))
    p("     inrush nor F1's I2t changes (MEETS, INFERRED)")
    p("   inrush from the pack (S1 from cold, VSYS discharged, the discharge FET switching at once): the direct can and the MLCCs (%s uF nominal, %s uF at"
      % (fmt(G["c_ceramic_nom"] * 1e6, 1), fmt(G["c_pack_side_max"] * 1e6, 1)))
    p("     most) through the pack's least loop %s mOhm (four cells at %s mOhm over three, and pwr_budget's distribution): %s A peak, over the image's ASCD"
      % (fmt(G["r_loop"] * 1e3, 2), fmt(0.035 * 1e3, 0), fmt(G["i_conn_pk"], 1)))
    p("     %s A for %s us against its %s us delay (MEETS, INFERRED); the bank behind R_CH adds %s mA, so it cannot trip ASCD (INFERRED)"
      % (fmt(G["ascd_a"], 1), fmt(G["t_over_ascd"] * 1e6, 1), fmt(G["ascd_us"] * 1e6, 0), fmt(G["i_ch_pk"] * 1e3, 1)))
    p("   what it does not do (INFERRED):")
    p("     a step beyond the source's headroom is a deficit, not a transient: at a 9.00 V plug the slot rail's step on P1's plan leaves %s W short, which the"
      % fmt(G["s9_deficit"], 2))
    p("       fallback only delays by %s ms; R-c's measured headroom must therefore count the largest uncontrolled step of the loads P1 keeps (E11-06 measures P1's peaks)"
      % fmt(G["s9_time"] * 1e3, 2))
    p("     in S2 (a warm CUV) VSYS is the stack plus Q2's diode, %s to %s V, at A-14's assumed 10.0 V floor: no droop is left to hold, so S2 still rests on"
      % (fmt(G["s2_vsys"][0], 1), fmt(G["s2_vsys"][1], 1)))
    p("       the charger's response (D2 for S2) and on the converters' real minimum inputs (E11-08)")
    p("     it settles neither D1 (the steady mode) nor D3 (the inhibited mode): no capacitance answers what the converter regulates")
    p("")
    p("11. WHAT CHANGES FOR U-04'S CLASSIFICATION (INFERRED)")
    p("   made independent of TI by the fallback: D2 for every admitted step in S4 within the bank's %s ms (with D2's bench margin), and D5 (VSYS's" % fmt(G["worst_hold"] * 1e3, 3))
    p("     effective capacitance) by the direct can (INFERRED)")
    p("   still depending on TI: D1 (S4 at all), D3 (REQ-077's hold and R-a's S2), D4 (low consequence), D6 (the image's 0-V charging), D7 and D8 (R-b's")
    p("     cases (iii) and (ii)); and on the entry's makers: D9 and D10")
    p("   negative answers with a remedy inside arrangement (A): D4, D5, D6, D7, D8, D9, D10; with none: D1 and D3, whose negative answers return (B)")
    p("   so U-04 STAYS AN ARCHITECTURE-LEVEL CHOICE: the fallback narrows the architecture's dependence on TI from four statements (D1, D2, D3, D5) to two")
    p("     (D1, D3), but those two decide whether arrangement (A) can run on a source with no usable pack and hold a charge while carried, and no part,")
    p("     rule or capacitance inside (A) answers them; one bench sample can show the mode on that silicon revision, not a production-wide behaviour")
    p("")


# ============================================================================================ the consolidation round
EC_SKIP = re.compile(r"Copyright|Submit Document|Product Folder|SLUSE6|www\.ti\.com|^\s*BQ2573\d\s*$|Electrical Characteristics|"
                     r"VVBUS_UVLOZ <|PARAMETER|Timing Requirements|MIN\s+NOM\s+MAX")
EC_SYM = re.compile(r"^\s{0,4}([A-Z][A-Za-z0-9_]{2,})(?:\s|$)")
# the electrical rows L4-E4 to L4-E8, this record and the charger's drawn parts rest on (ChargeVoltage, the input limit and the
# ILIM_HIZ line, VINDPM, REGN, the protections, the converter's current limits, HIZ, the cell strap, PROCHOT and PSYS)
EC_RESTS_ON = ("VBAT_REG_ACC", "VIREG_CHG_RNG", "IIIN_DPM_REG_ACC", "VIREG_DPM_RNG_ILIM", "IIIN_DPM_REG_ACC_ILIM", "VDPM_REG_ACC",
               "VREGN_REG", "VVBUSOV_RISE", "VVBUSOV_FALL", "VACOC_FLOOR", "VACOC_CEILING", "VSYSOVP_RISE", "VSYSOVP_FALL",
               "VBATOVP_RISE", "VBATOVP_FALL", "VOCP_lim_ACX", "VOCP_lim_Q2", "VOCP_lim_SYSSHRT_ACX", "VOCP_lim_SYSSHRT_Q2",
               "TSHUT_RISE", "VHIZ_", "VCELL_4S", "VCELL_BATPRESZ_FALL", "IDCHG_TH1", "IDCHG_TH2", "VPSYS_ACC", "VIADPT_ACC",
               "IIBAT_CHG_ACC", "VVBUS_CONVEN", "VVBAT_UVLOZ")
# the rows whose numbers differ between the sheets, by kind: the script refuses a sheet in which any other row differs
EC_CHANGED = {"VSYS_UVLOZ": "changed", "VSYS_UVLO": "changed", "IDCHG_DEG1": "a typical figure reprinted",
              "ICHRG_REG_ACC": "the condition text and the 1S row's 3.6 V written as VSYS_MIN; the precharge rows follow",
              "IREGN_LIM": "a footnote marker", "VVBUS_OTG_OV": "a heading's text", "VINDEP_CMP_HYS": "a footnote marker",
              "ILEAK_COMP2": "a section number"}


def pin_table(key):
    t = "\f".join(pdf_pages(key, True))
    i = t.find("Pin Functions")
    seg = t[i:t.find("Specifications", i)]
    d = {}
    for m in re.finditer(r"^\s{0,6}([A-Z][A-Z0-9_/]+)\s+(\d{1,2})\s+(PWR|I/O|I|O|GND|NA)\b", seg, re.M):
        d[int(m.group(2))] = m.group(1)
    if sorted(d) != list(range(1, 33)):
        refuse(3, "%s's pin table" % PINS[key][0])
    return d


def ec_blocks(key, head):
    t = "\f".join(pdf_pages(key, True))
    i = t.find(head, t.find(head) + 1)
    j = t.find("Typical Characteristics", i)
    if i < 0 or j < 0:
        refuse(3, "%s's electrical characteristics" % PINS[key][0])
    out, cur = {}, "(head)"
    out[cur] = []
    for ln in t[i:j].split("\n"):
        if EC_SKIP.search(ln):
            continue
        m = EC_SYM.match(ln)
        if m and "_" in m.group(1):
            cur = m.group(1)
            out.setdefault(cur, [])
            out[cur].append([])
        elif not out[cur]:
            out[cur].append([])
        out[cur][-1] += re.findall(r"-?\d+(?:\.\d+)?%?", ln.replace("\u2013", "-"))
    return out


def z_ja_aons():
    """AONS21357 Figure 14 (Rev 2.1 p.5), the single-pulse power junction-to-ambient on the maker's 1 in2 2 oz board at TA 25 C
    (Note H), read from the sheet's vector drawing: the plot's own frame (1E-05 to 1000 s, 1 to 10000 W, log axes) and its one
    curve (a cubic path whose segment ends are the curve's points). ZthJA(t) = (150 - 25) / P(t), checked against the table's
    'Maximum Junction-to-Ambient, t <= 10 s' 25 C/W."""
    pdf = read("aons21357")
    svg = subprocess.run(["pdftocairo", "-svg", "-f", "5", "-l", "5", pdf, "-"], capture_output=True).stdout.decode("utf-8", "replace")
    paths = []
    for m in re.finditer(r"<path[^>]*>", svg):
        t = re.sub(r",\s+", ",", m.group(0))
        d = re.search(r' d="([^"]*)"', t)
        w = re.search(r'stroke-width(?::|=")([\d.]+)', t)
        if d and w and "matrix(0.998658,0,0,-0.998658,0,840.955329)" in t:
            paths.append((float(w.group(1)), d.group(1)))
    frames = []
    for w, d in paths:
        pts = [(float(a), float(b)) for a, b in re.findall(r"[ML] ([-\d.]+) ([-\d.]+)", d)]
        if len(pts) == 5 and "C" not in d and pts[0] == pts[-1] and 340 < max(x for x, _ in pts) - min(x for x, _ in pts) < 360 \
                and 400 < min(y for _, y in pts) < 450:
            frames.append(pts)
    if len(frames) != 1:
        refuse(3, "Figure 14's frame")
    x0, x1 = min(x for x, _ in frames[0]), max(x for x, _ in frames[0])
    y0, y1 = min(y for _, y in frames[0]), max(y for _, y in frames[0])
    def inside(d):                                            # the curve's segment ends inside the frame's power span
        ys = sorted(float(nums.split()[-1]) for _c, nums in re.findall(r"([MC])((?: [-\d.]+)+)", d))
        return bool(ys) and y0 <= ys[len(ys) // 2] <= y1
    curves = [d for w, d in paths if w > 1.5 and d.count("C ") > 100 and inside(d)]
    if len(curves) != 1:
        refuse(3, "Figure 14's curve")
    pts = []
    for cmd, nums in re.findall(r"([MC])((?: [-\d.]+)+)", curves[0]):
        v = [float(x) for x in nums.split()]
        pts.append((-5.0 + 8.0 * (v[-2] - x0) / (x1 - x0), 4.0 * (v[-1] - y0) / (y1 - y0)))
    pts = [p for p in pts if p[0] >= -5.0]
    if any(b[0] <= a[0] for a, b in zip(pts, pts[1:])):
        refuse(3, "Figure 14's curve is not monotone in time")

    def p_of(t):
        lt = math.log10(t)
        for (a, b), (c, e) in zip(pts, pts[1:]):
            if a <= lt <= c:
                return 10 ** (b + (e - b) * (lt - a) / (c - a))
        refuse(3, "Figure 14 has no point at %s s" % t)
    return (lambda t: 125.0 / p_of(t)), (10 ** pts[0][0], 10 ** pts[-1][0])


def consolidation_round(R, T):
    """The owner's instructions of 2 October 2026 11:25 (compare at most three credible approaches, prefer adequate margin and
    fewer interacting controls, quantify power, heat, space, cost and endurance, select the best-supported route) and 12:00
    (the charger: the implementation that supports the battery-present, battery-absent and charging-inhibited modes; TI's
    BQ25730 evaluated against its datasheet and board A's circuit: interfaces, settings, startup, protection, budgets)."""
    B, P, E, F, N, G, C = R["B"], R["P"], R["E"], R["F"], R["N"], R["G"], R["C"]
    ga = T["gen_a"]
    gaf = re.sub(r"\n#\s*", " ", ga)
    H = {}
    # ---- the sheet itself
    p_, m = find("bq25730", r"(SLUSE65A) . FEBRUARY 2021 . REVISED JANUARY 2024", "the BQ25730's literature number")
    H["lit"], H["pages"] = m.group(1), sum(1 for t in pdf_pages("bq25730") if t.strip())
    H["feat_p"] = find("bq25730", r"Power path control through battery MOSFET implementing independent system voltage instant-?\s?on with no battery or depleted battery", "p.1's power path")[0]
    # ---- the pins against U3's netlist
    p31, p30 = pin_table("bq25731"), pin_table("bq25730")
    H["pins_diff"] = [(k, p31[k], p30[k]) for k in range(1, 33) if p31[k] != p30[k]]
    if H["pins_diff"] != [(21, "NC", "BATDRV")]:
        refuse(4, "the two pin tables differ elsewhere than pin 21")
    m = need(ga, r'ic\("U3", 33, "BQ25731RSNR[^"]*", "QFN32_04", \{(.*?)\}, "(C\d+)"\)', "U3's call", re.S)
    u3 = dict(re.findall(r'"(\d+)": "([^"]+)"', m.group(1)))
    H["u3_code"] = m.group(2)
    if u3.get("21") != "NC" or u3.get("22") != "VBAT" or u3.get("18") != "CH_CELL" or u3.get("6") != "CHG_ILIM":
        refuse(4, "U3's pins 6, 18, 21 and 22 are not as this round reads them")
    H["u3"] = u3
    H["batdrv_p"] = find("bq25730", r"P-channel battery FET \(BATFET\) gate driver output\. It is shorted to VSYS to turn off the BATFET\. It goes 10 V below VSYS to fully turn on BATFET\. BATFET is in linear mode to regulate VSYS at minimum system voltage when battery is depleted\. BATFET is fully on during fast charge and works as an ideal-diode in supplement mode\.", "the BATDRV pin")[0]
    H["vsys_pin_p"] = find("bq25730", r"The system voltage regulation maximum limit is programmed in ChargeVoltage register plus 150 mV and regulation minimum limit is programmed in VSYS_MIN register\.", "the VSYS pin")[0]
    p_, m = find("bq25730", r"When CELL_BATPRESZ pin is pulled down to GND \(because of battery removal\) at the beginning of startup process, VSYS_MIN = ([\d.]+) V and SYS_OVP = (\d+) V and Maximum charge voltage \(REG0x05/04\)\) follow 1 cell default setting ([\d.]+) V\.", "8.3.7")
    H["rm_p"], H["rm"] = p_, (f(m, 1), f(m, 2), f(m, 3))
    need(ga, r'r\("R148", "10R", "CELL_FUSED", "CH_SRN_F"\)', "R148 on the pack side")
    need(ga, r'r\("R149", "10R", "VBAT", "CH_SRP_F"\)', "R149 on VSYS")
    # ---- the electrical rows, sheet against sheet
    b31 = ec_blocks("bq25731", "8.5 Electrical Characteristics(BQ25731)")
    b30 = ec_blocks("bq25730", "7.5 Electrical Characteristics(BQ25730)")
    H["ec_n31"] = len([k for k in b31 if k != "(head)"])
    H["ec_added"] = [k for k in b30 if k not in b31]
    H["ec_gone"] = [k for k in b31 if k not in b30]
    H["ec_same"] = [k for k in b31 if k in b30 and b31[k] == b30[k] and k != "(head)"]
    H["ec_diff"] = [k for k in b31 if k in b30 and b31[k] != b30[k]]
    if sorted(H["ec_diff"]) != sorted(EC_CHANGED):
        refuse(4, "the electrical rows differ elsewhere than this round reads: %s" % sorted(set(H["ec_diff"]) ^ set(EC_CHANGED)))
    miss = [k for k in EC_RESTS_ON if k not in H["ec_same"]]
    if miss:
        refuse(4, "a row the drafted settings rest on differs: %s" % miss)
    pc31 = [x for x in b31["ICHRG_REG_ACC"][0] if x.endswith("%")]
    pc30 = [x for x in b30["ICHRG_REG_ACC"][0] if x.endswith("%")]
    if pc30[:len(pc31)] != pc31:
        refuse(4, "ChargeCurrent's accuracy rows differ")
    H["ichg_pct"] = pc31
    if b30["IREGN_LIM"][0][:len(b31["IREGN_LIM"][0])] != b31["IREGN_LIM"][0]:
        refuse(4, "the REGN rows differ")
    fs = lambda b: any(b["VINDEP_CMP_HYS"][0][i:i + 3] == ["340", "400", "460"] for i in range(len(b["VINDEP_CMP_HYS"][0])))
    if not (fs(b31) and fs(b30)):
        refuse(4, "the 400 kHz switching row differs")
    H["uvlo31"] = (b31["VSYS_UVLOZ"][0][:3], b31["VSYS_UVLO"][0][:3])
    H["uvlo30"] = (b30["VSYS_UVLOZ"][0][:3], [x for x in b30["VSYS_UVLO"][0] if "." in x][:3])
    H["idchg"] = ([x for x in b31["IDCHG_DEG1"][0] if x.startswith("24.")][0], [x for x in b30["IDCHG_DEG1"][0] if x.startswith("24.")][0])
    # ---- the registers that change
    H["ichg_por"] = find("bq25730", r"8\.6\.2 ChargeCurrent Register \(I2C address = 03/02h\) \[reset = (\w+)h\]", "ChargeCurrent's reset")[1].group(1)
    H["ichg_por_p"] = find("bq25730", r"8\.6\.2 ChargeCurrent Register \(I2C address = 03/02h\) \[reset = (\w+)h\]", "ChargeCurrent's reset")[0]
    H["wd_p"] = find("bq25730", r"except ChargeCurrent\(\) resets to 0 A \.", "the watchdog's reset")[0]
    find("bq25730", r"New non-zero charge current value has to be written to ChargeCurrent\(\) register to resume charging after watchdog timer expires\.", "the watchdog's resume")
    H["wd_s"] = f(find("bq25730", r"Watchdog timeout period, REG0x01\[6:5\]=11\s+(\d+)\s+(\d+)\s+(\d+)\s+s", "the watchdog's period", layout=True)[1], 2)
    H["vmin_reg_p"] = find("bq25730", r"Upon POR, the VSYS_MIN register is 3\.6 V for 1 S, 6\.6V for 2 S and 9\.2 V for 3 S, and 12\.3 V for 4 S, and 15\.4 V for 5S\.", "VSYS_MIN's POR")[0]
    regs = {}
    for name, pat in (("EN_LDO", r"2 EN_LDO R/W (\d)b LDO Mode Enable"), ("EN_OOA", r"2 EN_OOA R/W (\d)b Out-of-Audio Enable"),
                      ("CHRG_INHIBIT", r"0 CHRG_INHIBIT R/W (\d)b Charge Inhibit"), ("EN_PORT_CTRL", r"2 EN_PORT_CTRL R/W (\d)b Enable BATFET control"),
                      ("BATFET_ENZ", r"7 BATFET_ENZ R/W (\d)b Turn off BATFET under battery only mode\."),
                      ("BATFETOFF_HIZ", r"1 BATFETOFF_HIZ R/W (\d)b Control BATFET on/off during charger HIZ mode\. 0b: BATFET on during charger HIZ mode <default at POR>")):
        p_, m = find("bq25730", pat, name)
        regs[name] = (int(m.group(1)), p_)
    if (regs["EN_LDO"][0], regs["EN_PORT_CTRL"][0], regs["BATFET_ENZ"][0], regs["BATFETOFF_HIZ"][0], regs["CHRG_INHIBIT"][0]) != (1, 1, 0, 0, 0):
        refuse(4, "a BATFET or charge register's reset is not as this round reads it")
    H["regs"] = regs
    H["devid"] = find("bq25730", r"Device ID \(DeviceAddress\) Register \(I2C address = 2Fh\) \[reset = (\w+)h\]", "the device ID")[1].group(1)
    H["devid31"] = find("bq25731", r"Device ID \(DeviceAddress\) Register \(I2C address = 2Fh\) \[reset = (\w+)h\]", "BQ25731's device ID")[1].group(1)
    # ---- the three modes: the statements that bound VSYS
    H["nvdc_p"] = find("bq25730", r"The device employs Narrow VDC architecture \(NVDC\) with BATFET separating the system from the battery\. The minimum system voltage is set by VSYS_MIN register REG0x0D/0C\(\)\. Even with a depleted battery, the system is regulated above the minimum system voltage\. When the battery is below minimum system voltage setting, the BATFET operates in linear mode \(LDO mode\), and the system is regulated at VSYS_MIN register value\. As the battery voltage rises above the minimum system voltage, system voltage is regulated 150 mV above battery voltage when BATFET is turned off \(no charging or no supplement current\)\. When in charging or in supplement mode, the voltage difference between the system and battery is the VDS of the BATFET and the BATFET is fully on\.", "8.4.1.1")[0]
    p_, m = find("bq25730", r"REG0x05/04\(\) = 0x41A0H \(16\.800 V\)\s+150 mV\s+.\s*(\d)%\s+(\d)%", "VSYSMAX_ACC at 16.8 V", layout=True)
    H["smax_p"], H["smax_acc"] = p_, (f(m, 1) / 100.0, f(m, 2) / 100.0)
    find("bq25730", r"VSYSMAX_ACC\s+REG0x05/04\(\) = 0x5208H \(21\.000 V\)\s*\n\s+\(charge disabled and\s*\n\s+OOA disabled\)", "VSYSMAX_ACC's condition", layout=True)
    p_, m = find("bq25730", r"(\d+\.\d+)\s+V\s*\n\s*REG0x0D/0C\(\) = 0x7B00H\s*\n\s*(.)(\d)%\s+(.)(\d)%", "VSYS_MIN_REG_ACC at 12.3 V", layout=True)
    H["smin_p"], H["smin"], H["smin_lo"] = p_, f(m, 1), f(m, 3) / 100.0
    H["smin_max_printed"] = ("-" if m.group(4) in "\u2013-" else "+") + m.group(5)
    if m.group(2) not in "\u2013-":
        refuse(3, "VSYS_MIN_REG_ACC's minimum is not negative")
    find("bq25730", r"VSYS_MIN_REG_ACC\s+Accuracy \(VBAT\s+REG0x0D/0C\(\) = 0x9A00H\s*\n\s+below REG0x0D/0C\(\)", "VSYS_MIN_REG_ACC's condition", layout=True)
    m = find("bq25730", r"VVBUS_UVLOZ < VVBUS < VVBUSOV_FALL , TJ = (-\d+)°C to \+(\d+)°C", "the electrical table's temperature", layout=True)[1]
    H["ec_tj"] = (f(m, 1), f(m, 2))
    p_, m = find("bq25730", r"REG0x03/02\(\) = 0x0080H\s+(\d+)\s+mA\s*\n\s*setting \(0°C to 85°C\)\s+≥2S\s+.(\d+\.\d)%\s+(\d+\.\d)%", "the 256 mA precharge row", layout=True)
    H["pre_p"], H["pre256"] = p_, (f(m, 1) / 1000.0, f(m, 2) / 100.0, f(m, 3) / 100.0)
    m = find("bq25730", r"REG0x03/02\(\) = 0x00C0H\s+(\d+)\s+mA\s*\n.*?≥2S\s+.(\d+\.\d)%\s+(\d+\.\d)%", "the 384 mA precharge row", layout=True, flags=re.S)[1]
    H["pre384"] = (f(m, 1) / 1000.0, f(m, 2) / 100.0, f(m, 3) / 100.0)
    H["inhibit_p"] = regs["CHRG_INHIBIT"][1]
    # the bounds (INFERRED from the rows above; the pack's window from the image)
    H["floor"] = H["smin"] * (1 - H["smin_lo"])
    H["smin_hi"] = H["smin"] * (1 + H["smin_lo"])                 # ASSUMPTION: the MAX column's "-2 %" read as +2 %
    H["vsys_top"] = (R["cv_max"] + 0.150) * (1 + H["smax_acc"][1])
    H["vsys_inh_cuv"] = max(H["floor"], (P["vsys_cuv"][0] + 0.150) * (1 - H["smax_acc"][0]))
    H["margin_floor"] = H["floor"] - 10.0
    # ---- startup in each mode
    H["bat_only_p"] = find("bq25730", r"If only battery is present and the voltage is above VVBAT_UVLOZ , charger wakes up and the BATFET is turned on and connecting the battery to system\.", "8.3.1, battery only")[0]
    m = find("bq25730", r"VVBAT_UVLOZ\s+VSRN rising\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "VVBAT_UVLOZ", layout=True)[1]
    H["vbat_uvloz"] = (f(m, 1), f(m, 3))
    H["pu_p"] = find("bq25730", r"Battery CELL configuration is read at CELL_BATPRESZ pin voltage and compared to VDDA to determine cell configuration\. Corresponding the default value of ChargeVoltage register \(REG0x05/04\(\)\), ChargeCurrent register \(Reg0x03/02\), VSYS_MIN register \(Reg0x0D/0C\) and SYSOVP threshold are loaded\. Converter powers up\.", "8.3.1, from VBUS")[0]
    find("bq25730", r"This protection is mainly defined to protect converter from system short circuit under both startup and steady state process\.", "8.3.21.8")
    p_, m = find("bq25730", r"than ([\d.]+) V \(configurable through VSYS_UVP register bits\), there is (\d)-ms deglitch time, the IIN_DPM is clamped to ([\d.]+) A by the charger itself\. If hiccup mode is enabled with VSYS_UVP_NO_HICCUP = 0b, after 2-ms deglitch time, the charger should shut down for (\d+) ms\.The charger will restart for (\d+) ms if VSYS is still lower than [\d.]+ V, the charger should shut down again\. This hiccup mode will be tried continuously, if the charger restart failed for (\d) times in (\d+) second, the charger will be latched off\.", "VSYS_UVP and hiccup")
    H["uvp_p"], H["uvp"] = p_, dict(v=f(m, 1), deg=f(m, 2) * 1e-3, iin=f(m, 3), off=f(m, 4) * 1e-3, on=f(m, 5) * 1e-3, n=int(m.group(6)), win=f(m, 7))
    na = T["net_a"]

    def nom_uf(net):
        s = 0.0
        for ref, _p in netlist_nodes(na, net):
            if ref.startswith("C"):
                mm = re.match(r"([\d.]+)(u|n)", netlist_value(na, ref))
                if mm:
                    s += float(mm.group(1)) * (1.0 if mm.group(2) == "u" else 1e-3)
        return s * 1e-6
    H["c_vsys_nom"] = nom_uf("VBAT")
    H["c_vsys_max"] = H["c_vsys_nom"] * 1.1 + G["c181"] * (1 + G["zk_tol"])
    H["t_2v4"] = H["c_vsys_max"] * H["uvp"]["v"] / H["uvp"]["iin"]
    H["hiccups"] = 0 if H["t_2v4"] <= H["uvp"]["deg"] else (1 if H["t_2v4"] <= H["uvp"]["on"] else None)
    if H["hiccups"] is None:
        refuse(4, "VSYS's capacitance cannot reach VSYS_UVP's threshold inside the restart window")
    H["start_bound"] = H["hiccups"] * H["uvp"]["off"] + H["t_2v4"]
    # ---- the rest of the BATFET's place in the circuit (TI's guidance and the gate drive)
    p_, m = find("bq25730", r"P-channel MOSFETs is used for battery charging BATFET\. The gate drivers are internally integrated into the IC with 10 V of gate drive voltage\. (\d+) V or higher voltage rating MOSFETs are preferred for 1- to 4-cell battery application, 30 V or higher voltage rating MOSFETs are preferred for 5-cell battery application, the Ciss of P-channel MOSFET should be chosen less than (\d) nF\.", "the BATFET's selection")
    H["bf_p"], H["bf_v"], H["bf_ciss"] = p_, f(m, 1), f(m, 2) * 1e-9
    m = find("bq25730", r"VBATDRV_ON\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s+V", "VBATDRV_ON", layout=True)
    H["drv_p"], H["drv"] = m[0], (f(m[1], 1), f(m[1], 2), f(m[1], 3))
    H["drv_diode_mv"] = f(find("bq25730", r"VBATDRV_DIODE\s+on BATFET during\s+(\d+)\s+mV", "VBATDRV_DIODE", layout=True)[1])
    m = find("bq25730", r"RBATDRV_ON\s+sourcing 10 µA\s+(\d)\s+(\d)\s+(\d)\s+kΩ", "RBATDRV_ON", layout=True)[1]
    H["rdrv"] = (f(m, 1) * 1e3, f(m, 3) * 1e3)
    H["csys_p"], H["csys_uf"] = find("bq25730", r"Overall (\d+)-.F effective capacitance on VSYS net is necessary \(POSCAP is preferred\)", "9.1")[0], \
        f(find("bq25730", r"Overall (\d+)-.F effective capacitance on VSYS net is necessary \(POSCAP is preferred\)", "9.1")[1])
    H["pk_p"] = find("bq25730", r"When battery is depleted in which VBAT is lower than VSYS_MIN setting or battery is removed, host need to set EN_PKPWR_VSYS=1b to enable peak power mode triggered by system voltage undershoot\.", "8.3.19")[0]
    H["f922_p"] = find("bq25730", r"Figure 9-22\. Peak Power Mode VSYS Trigger", "Figure 9-22")[0]
    find("bq25730", r"ISYS = 1 to 6 A ICHG = 0 A", "Figure 9-22's conditions")
    H["depl_p"] = find("bq25730", r"Typically the battery depletion threshold should be greater than the VSYS_MIN so that the battery capacity can be fully utilized for maximum battery run time\.", "10")[0]
    H["batoc_p"] = find("bq25730", r"BATFET status is not impacted if need to supplement power to system\.", "8.3.21.6")[0]
    H["hiz_v"] = f(find("bq25730", r"the charger can enter HIZ mode \(converter shuts off\) when ILIM_HIZ pin voltage is below ([\d.]+) V", "8.3.8")[1])
    m = find("bq25730", r"7\.3 Recommended Operating Conditions \(continued\).*?Junction temperature range, TJ\s+(\S+)\s+(\d+)", "the recommended TJ", layout=True, flags=re.S)[1]
    H["tj_rec"] = (f(m, 1) if m.group(1)[0].isdigit() else -float(m.group(1)[1:]), f(m, 2))
    # ---- the battery FET Q39: AOS AONS21357 (Rev 2.1, November 2023), held
    aos = lambda pat, what, fl=0: find("aons21357", pat, what, layout=True, flags=fl)
    H["q_rev"] = find("aons21357", r"Rev\.(\d\.\d): November 2023", "the AOS revision")[1].group(1)
    Q = {}
    Q["vds"] = f(aos(r"Drain-Source Voltage\s+VDS\s+-(\d+)", "VDS")[1])
    Q["vgs"] = f(aos(r"Gate-Source Voltage\s+VGS\s+±(\d+)", "VGS")[1])
    Q["idm"] = f(aos(r"Pulsed Drain Current\s+IDM\s+-(\d+)", "IDM")[1])
    m = aos(r"t ≤ 10s\s+(\d+)\s+(\d+)\s+°C/W", "RthJA 10 s")[1]
    Q["rja10"] = f(m, 2)
    m = aos(r"Steady-State\s+(\d+)\s+(\d+)\s+°C/W", "RthJA steady")[1]
    Q["rja_ss"] = f(m, 2)
    m = aos(r"VGS=-10V, ID=-20A\s+([\d.]+)\s+([\d.]+)\s*\n.*?TJ=125°C\s+([\d.]+)\s+([\d.]+)", "RDS(on)", re.S)[1]
    Q["rds25"], Q["rds125"] = f(m, 2) * 1e-3, f(m, 4) * 1e-3
    Q["ciss"] = f(aos(r"Ciss\s+Input Capacitance\s+(\d+)\s+pF", "Ciss")[1]) * 1e-12
    m = aos(r"IS=-1A, VGS=0V\s+-([\d.]+)\s+-(\d)\s+V", "VSD")[1]
    Q["vsd"] = f(m, 2)
    Q["is"] = f(aos(r"IS\s+Maximum Body-Diode Continuous Current G\s+-(\d+)", "IS")[1])
    find("aons21357", r"H\. These tests are performed with the device mounted on 1 in2 FR-4 board with 2oz\. Copper, in a still air environment with TA=25°C\.", "Note H")
    find("aons21357", r"Figure 14: Single Pulse Power Rating Junction-to-Ambient \(Note H\)", "Figure 14")
    Q["fig9_p"] = find("aons21357", r"Figure 9: Maximum Forward Biased Safe Operating Area \(Note F\)", "Figure 9")[0]
    find("aons21357", r"F\. These curves are based on the junction-to-case thermal impedance which is measured with the device mounted to a large heatsink, assuming a maximum junction temperature of TJ\(MAX\)=150°C\. The SOA curve provides a single pulse rating\.", "Note F")
    zja, Q["z_span"] = z_ja_aons()
    Q["z10"] = zja(10.0)
    if abs(Q["z10"] - Q["rja10"]) > 0.02 * Q["rja10"]:
        refuse(3, "Figure 14 does not read the table's 10 s junction-to-ambient figure")
    air = F["air_hot"]
    Q["vgs_use"] = H["drv"][2] / Q["vgs"]
    Q["vds_use"] = B["sysovp4s"] / Q["vds"]
    # loss on battery at the profile states (the budget's battery-terminal watts at 14.4 V), RDS(on) at its 125 C maximum
    Q["prof"] = []
    for name in ("PS-IDLE-SPEC", "PS-TYP"):
        i_ = E["states"][name][1] / 14.4
        Q["prof"].append((name, i_, i_ ** 2 * Q["rds125"], i_ ** 2 * Q["rds125"] / (i_ * 14.4)))
    # the pack's own currents through Q39 (fully on), from the inside air and from 10 A held
    pf = yaml.safe_load(T["packprot"])
    fn = {x["id"]: x for x in pf["functions"]}
    th = lambda k: (float(fn[k]["threshold"]["value"]), float(fn[k]["threshold"]["delay_s"]))
    ocd1, aold = th("PACK_OVER_CURRENT_DISCHARGE"), th("PACK_OVER_CURRENT_DISCHARGE_2")
    m = need(flat(T["primcfg"]), r"\| OCD2 \(14\.9\.7\) \| -8000 mA, 3 s \| -(\d+) mA, (\d) s", "the image's OCD2")
    ocd2 = (f(m, 1) / 1000.0, f(m, 2))
    Q["i_cont"], Q["i_peak"] = 10.0, C["pack_peak"]
    p10 = Q["i_cont"] ** 2 * Q["rds125"]
    Q["tj_10a_60s"] = air + p10 * zja(60.0)
    Q["tj_10a_ss"] = air + p10 * Q["rja_ss"]
    p18 = Q["i_peak"] ** 2 * Q["rds125"]
    Q["p18"] = p18

    def t_lim(p_add, base):
        lo, hi = math.log10(Q["z_span"][0]) + 1e-6, math.log10(Q["z_span"][1]) - 1e-6
        if base + p_add * zja(10 ** hi) <= 150.0:
            return None
        if base + p_add * zja(10 ** lo) > 150.0:
            return 0.0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if base + p_add * zja(10 ** mid) <= 150.0:
                lo = mid
            else:
                hi = mid
        return 10 ** lo
    Q["t18_air"] = t_lim(p18, air)
    Q["t18_hot"] = t_lim(p18 - p10, Q["tj_10a_ss"])
    Q["prot"] = []
    for lab, (i_, t_) in (("the gauge's OCD1", ocd1), ("the image's OCD2", ocd2), ("the AFE's AOLD", aold), ("the image's ASCD", (G["ascd_a"], 244e-6))):
        p_ = i_ ** 2 * Q["rds125"]
        Q["prot"].append((lab, i_, t_, i_ * Q["rds125"], air + p_ * zja(t_), Q["tj_10a_ss"] + (p_ - p10) * zja(t_)))
    Q["rja_need_20"] = (150.0 - air) / (ocd1[0] ** 2 * Q["rds125"])
    Q["rja_need_18"] = (150.0 - air) / p18
    Q["ocd1"] = ocd1
    # the docking inrush through Q39's body diode (the dependency round's pack-loop model: the discharge FET at once, no drop credited)
    Q["c_behind"] = H["c_vsys_max"]
    Q["tau"] = G["r_loop"] * Q["c_behind"]
    Q["i_dock"] = G["i_conn_pk"]
    Q["t_over_idm"] = Q["tau"] * math.log(Q["i_dock"] / Q["idm"]) if Q["i_dock"] > Q["idm"] else 0.0
    Q["q_dock"] = Q["c_behind"] * 4 * 4.2
    m = find("bq4050", r"VDSG from 0% to 35% VDSG\(ON\)\(TYP\).*?(\d+)\s+(\d+)\s*\n", "the gauge's DSG rise time", layout=True, flags=re.S)
    Q["dsg_rise"] = (m[0], f(m[1], 1) * 1e-6, f(m[1], 2) * 1e-6)
    # the LDO-mode precharge (VSYS at VSYS_MIN, the pack under it): Q39 linear
    i_pre = H["pre256"][0] * (1 + H["pre256"][2])
    i_pre3 = H["pre384"][0] * (1 + H["pre384"][2])
    Q["i_pre"], Q["i_pre3"] = i_pre, i_pre3
    Q["ldo_floor"] = H["smin_hi"] - (150.0 - air) / (Q["rja_ss"] * i_pre)
    Q["ldo_floor3"] = H["smin_hi"] - (150.0 - air) / (Q["rja_ss"] * i_pre3)
    Q["tj_ldo_cuv"] = air + (H["smin_hi"] - P["vsys_cuv"][0]) * i_pre * Q["rja_ss"]
    Q["tj_ldo_shut"] = air + (H["smin_hi"] - P["vsys_shut"][0]) * i_pre * Q["rja_ss"]
    Q["q2_pre"] = (i_pre * P["vsd_max"], air + i_pre * P["vsd_max"] * P["rja"])
    H["Q"] = Q
    # ---- the inductor in supplement mode (S-117's bound with Q39's drop at OCD1's 20 A)
    m = need(gaf, r"the front end's ([\d.]+) A at ([\d.]+) V into a pack at its ([\d.]+) V CUV puts ([\d.]+) A through this inductor", "S-117's inductor bound")
    s117 = (f(m, 1), f(m, 2), f(m, 3), f(m, 4))
    H["l_s117"] = s117
    H["l_pk117"] = f(need(gaf, r"peaks at ([\d.]+) A worst at that bound", "S-117's peak"))
    H["l_isat"] = f(need(gaf, r"The XAL1010-472ME \(4\.7 uH, Isat ([\d.]+) A", "the XAL1010's Isat"))
    H["l_vsys"] = s117[2] - ocd1[0] * Q["rds125"]
    H["l_i"] = s117[0] * s117[1] / H["l_vsys"]
    H["l_pk"] = H["l_pk117"] * H["l_i"] / (s117[0] * s117[1] / s117[2])
    # ---- the second NVDC sheet held and the other held candidates (B2)
    m = find("bq25792", r"RMS discharge current \(continuously\)\s+(\d+)\s+A", "BQ25792's battery FET RMS", layout=True)
    H["bq92"] = (f(m[1]), f(find("bq25792", r"Peak discharge current \(upto 1 sec\)\s+(\d+)\s+A", "BQ25792's peak", layout=True)[1]), m[0])
    H["lm747_p"] = find("lm74700", r"Low IQ Reverse Battery Protection Ideal Diode Controller", "the LM74700-Q1's title")[0]
    # ---- the parts' catalogue readings (LCSC, 2 October 2026) and the comparison's cost
    J = {n: json.load(open(os.path.join(TOP, REC, "inputs", n), encoding="utf-8")) for n in CONS_INPUTS}

    def price(n):
        lad = J[n]["price_usd"]
        k = "10" if "10" in lad else sorted(lad, key=lambda s: int(s))[0]
        return int(k), float(lad[k])
    H["cat"] = {J[n]["model"]: (J[n]["code"], J[n]["stock"], price(n)) for n in CONS_INPUTS}
    cA = H["cat"]["BQ25731RSNR"][2][1] + BANK_N * H["cat"]["EEHZK1E471P"][2][1] + H["cat"]["B540C-13-F"][2][1] \
        + H["cat"]["RC2512FK-07330RL"][2][1] + H["cat"]["EEHZK1V181P"][2][1]
    cB = H["cat"]["BQ25730RSNR"][2][1] + H["cat"]["AONS21357"][2][1] + H["cat"]["EEHZK1V181P"][2][1]
    H["cost"] = (cA, cB)
    # E11-24's bank and direct can at (B1)'s floor: charged to it less the bank's leakage across R_CH, giving into VSYS down to
    # A-14's 10.0 V plus D_H's drop, for the worst admitted step: what the bank would still buy under (B1)
    v1 = H["floor"] - BANK_N * G["zk_leak"] * R_CH
    v2 = 10.0 + G["vf"]
    e = G["c_bank_eff"] * (0.5 * (v1 ** 2 - v2 ** 2) - G["vf"] * (v1 - v2)) + 0.5 * G["c_dir_eff"] * (H["floor"] ** 2 - 10.0 ** 2)
    H["bank_b1"] = e / G["worst"][1]
    return H


def cons_rows(R):
    """D1 to D10 under each option: (row, (A), (B1)). The figures are this record's; section 13 prints them."""
    H, Q, G = R["H"], R["H"]["Q"], R["G"]
    return [
        ("D1", "OPEN (TI): no row bounds VSYS with no battery current", "REMOVED: VSYS_MIN_REG_ACC %s V, at least %s V at TJ %s to %s C (p.%d), with p.%d's LDO mode and p.%d's instant-on" % (fmt(H["smin"], 2), fmt(H["floor"], 3), fmt(H["ec_tj"][0], 0), fmt(H["ec_tj"][1], 0), H["smin_p"], H["nvdc_p"], H["feat_p"])),
        ("D2", "bank E11-24: %s ms against T_RESP %s ms (ASSUMPTION)" % (fmt(G["worst_hold"] * 1e3, 3), fmt(T_RESP * 1e3, 1)), "OPEN (no transient limit; Figure 9-22, p.%d, a typical waveform at 4 ms a division): a bench test against the converters' floor with R-c's step rule as the fallback" % H["f922_p"]),
        ("D3", "OPEN (TI): no statement of VSYS with charge inhibited and no battery current", "REMOVED: VSYSMAX_ACC, VSRN + 150 mV within +-%s %% with charge disabled (p.%d), the BATFET off with no charge or supplement current (p.%d)" % (fmt(H["smax_acc"][1] * 100, 0), H["smax_p"], H["nvdc_p"])),
        ("D4", "E2E answer (forum): 256 mA at POR", "REMOVED: ChargeCurrent's reset printed %sh, 0 A (p.%d); the watchdog returns it to 0 A (p.%d)" % (H["ichg_por"], H["ichg_por_p"], H["wd_p"])),
        ("D5", "the direct EEHZK1V181P (by design)", "the same can (TI's %s uF, p.%d)" % (fmt(H["csys_uf"], 0), H["csys_p"])),
        ("D6", "OPEN (the gauge's 0-V sequence)", "OPEN, unchanged (the gauge's)"),
        ("D7", "OPEN: the clamp typical only", "REMOVED inside 0 to 85 C: IPRECHRG_REG_ACC %s mA within +-%s %% (p.%d)" % (fmt(H["pre256"][0] * 1e3, 0), fmt(H["pre256"][2] * 100, 0), H["pre_p"])),
        ("D8", "OPEN (0x0200 outside 0 to 85 C)", "OPEN, the same row"),
        ("D9", "OPEN (the entry's delay)", "OPEN, unchanged (board E)"),
        ("D10", "OPEN (the entry's transconductance)", "OPEN, unchanged (board E)"),
    ]


def render_consolidation(R, p):
    H, Q, G, B, P, F, C, E = R["H"], R["H"]["Q"], R["G"], R["B"], R["P"], R["F"], R["C"], R["E"]
    air = F["air_hot"]
    p("12. THE U-04 QUESTION FOR THE CONSOLIDATION: TI'S BQ25730 AGAINST BOARD A'S CIRCUIT (2 October 2026)")
    p("   the owner's instructions of 2 October 2026: 11:25, compare at most three credible approaches, prefer adequate margin and fewer interacting")
    p("     controls, quantify power, heat, space, cost and endurance, select the best-supported route, retain the work done unless the change affects it;")
    p("     12:00, the charger that supports the battery-present, battery-absent and charging-inhibited modes, the BQ25730 against TI's sheet and")
    p("     board A's circuit: interfaces, settings, startup, protection and the affected budgets (REQUIREMENT, the owner's)")
    p("   the sheet: TI BQ25730, %s (February 2021, revised January 2024), %d pages, held back under TI's terms (fetch_held_back.py); p.%d: \"Power path"
      % (H["lit"], H["pages"], H["feat_p"]))
    p("     control through battery MOSFET implementing independent system voltage instant-on with no battery or depleted battery\" (MAKER)")
    p("   12a. THE PINS AGAINST U3'S NETLIST (gen_sch_a.py, U3 %s)" % H["u3_code"])
    p("     the two pin tables (SLUSE66A and SLUSE65A, pp.5 to 7) name 31 of 32 pins alike; the one difference: pin %d, %s on the BQ25731 (\"must be"
      % (H["pins_diff"][0][0], H["pins_diff"][0][1]))
    p("       floating\", U3 draws it NC) and %s on the BQ25730, the P-channel BATFET's gate drive, \"shorted to VSYS to turn off ... 10 V below VSYS"
      % H["pins_diff"][0][2])
    p("       to fully turn on\" (p.%d) (MAKER, NETLIST)" % H["batdrv_p"])
    p("     added: Q39, a P-channel FET, source on VBAT (pin 22, VSYS), drain on a new node CH_BATQ, gate on CH_BATDRV (pin 21); R17 (the 5 mOhm RSR)")
    p("       moves to CH_BATQ to CELL_FUSED and R149 (SRP's 10 Ohm) to CH_BATQ, as TI's Figure 9-1 draws the BATFET between VSYS and RSR (SESSION)")
    p("     same pin, new function: VSYS (22) becomes a regulated output, \"maximum limit ... ChargeVoltage register plus 150 mV and regulation minimum")
    p("       limit ... VSYS_MIN register\" (p.%d); SRP (20) reads the BATFET's side of RSR; every other pin keeps its net and function (MAKER, NETLIST)" % H["vsys_pin_p"])
    p("     CELL_BATPRESZ (18) keeps the 4S strap (%s percent of VDDA): pulled low it would load VSYS_MIN %s V, SYSOVP %s V and ChargeVoltage %s V"
      % (fmt(R["strap"][2], 2), fmt(H["rm"][0], 1), fmt(H["rm"][1], 0), fmt(H["rm"][2], 1)))
    p("       (p.%d), so battery presence is never wired to it (SESSION, MAKER)" % H["rm_p"])
    p("   12b. THE SETTINGS L4-E4 TO L4-E8 DRAFTED, SHEET AGAINST SHEET (the electrical tables of SLUSE66A 8.5 and SLUSE65A 7.5, read row by row)")
    p("     %d of the BQ25731's %d row blocks are identical in the BQ25730's table; the rows the drafted settings rest on are among them (MAKER, INFERRED):"
      % (len(H["ec_same"]), H["ec_n31"]))
    p("       %s" % ", ".join(EC_RESTS_ON[:10]))
    p("       %s" % ", ".join(EC_RESTS_ON[10:20]))
    p("       %s; ChargeCurrent's accuracy %s, the 400 kHz row and REGN's limit the same (MAKER)" % (", ".join(EC_RESTS_ON[20:]), " / ".join(H["ichg_pct"])))
    p("     rows whose numbers differ: VSYS_UVLOZ %s V to %s V and VSYS_UVLO %s V to %s V (changed); IDCHG_TH2's typical %s A reprinted %s A;"
      % ("/".join(H["uvlo31"][0]), "/".join(H["uvlo30"][0]), "/".join(H["uvlo31"][1]), "/".join(H["uvlo30"][1]), H["idchg"][0], H["idchg"][1]))
    p("       %d more differ only in text (a condition, a heading, footnote markers, a section number); rows added: %s (MAKER)"
      % (len(H["ec_diff"]) - 3, ", ".join(sorted(set(H["ec_added"])))))
    p("     so these carry over unchanged (RECORD, INFERRED): ChargeVoltage 16.8 V written at most %s V; IIN_HOST 4.70 A with RSNS_RAC 0 and EN_EXTILIM 1"
      % fmt(R["cv_max"], 3))
    p("       (L4-E4, L4-E5); the ILIM_HIZ line and its knee (L4-E5, section 3f's %s A); VINDPM; SYSOVP %s V, BATOVP, ACOV, ACOC, the converter's"
      % (fmt(KNEE_IT, 2), fmt(B["sysovp4s"], 1)))
    p("       OCP rows; HIZ under %s V; PROCHOT and PSYS (R23, R24); the 400 kHz row with R219 191k, the compensation and L2 (S-117); Q7 to Q10 on"
      % fmt(H["hiz_v"], 1))
    p("       REGN; R11 and R12 and L4-E8's bank with its ballasts, which sit on VBUS20 ahead of the charger's input and see the same input current")
    p("     registers that change (MAKER): ChargeCurrent resets to %sh, 0 A, where the BQ25731's resets to 0080h (p.%d); the watchdog (%s s at POR)"
      % (H["ichg_por"], H["ichg_por_p"], fmt(H["wd_s"], 0)))
    p("       returns it to 0 A and a non-zero write resumes the charge (p.%d); VSYS_MIN becomes a register, 12.3 V at POR for 4S (p.%d); EN_LDO %d,"
      % (H["wd_p"], H["vmin_reg_p"], H["regs"]["EN_LDO"][0]))
    p("       EN_PORT_CTRL %d, BATFET_ENZ %d and BATFETOFF_HIZ %d at POR (pp.%d, %d, %d): the BATFET driven, on in HIZ; EN_OOA %d at POR (p.%d); the device"
      % (H["regs"]["EN_PORT_CTRL"][0], H["regs"]["BATFET_ENZ"][0], H["regs"]["BATFETOFF_HIZ"][0], H["regs"]["EN_LDO"][1], H["regs"]["EN_PORT_CTRL"][1],
         H["regs"]["BATFETOFF_HIZ"][1], H["regs"]["EN_OOA"][0], H["regs"]["EN_OOA"][1]))
    p("       ID reads %sh, not %sh; I2C address 6Bh the same (MAKER)" % (H["devid"], H["devid31"]))
    p("   12c. THE THREE MODES: THE STATEMENT THAT BOUNDS VSYS IN EACH (the acceptance)")
    p("     the table's conditions: TJ %s to %s C unless a row says otherwise (p.9); the two VSYS rows hold \"OOA disabled\", and EN_OOA is %d at POR,"
      % (fmt(H["ec_tj"][0], 0), fmt(H["ec_tj"][1], 0), H["regs"]["EN_OOA"][0]))
    p("       so the firmware writes EN_OOA 0 at boot for the printed accuracy to apply (SESSION; before that the modes are stated, their accuracy not) (MAKER)")
    p("     (1) battery present, the source on: p.%d, \"system voltage is regulated 150 mV above battery voltage when BATFET is turned off\", the BATFET"
      % H["nvdc_p"])
    p("       fully on while charging or supplementing, VSYS_MIN the floor; VSYS from %s V (the floor), or, with the source overloaded, the pack less"
      % fmt(H["floor"], 3))
    p("       Q39's drop as it supplements (%s V at the CUV stack and OCD1's %s A, 12e, as (A)'s pack sits on VSYS less R17's drop),"
      % (fmt(H["l_vsys"], 3), fmt(Q["ocd1"][0], 0)))
    p("       to %s V (the pack at ChargeVoltage's %s V plus 150 mV, +%s %%, p.%d): BOUNDED (MAKER, INFERRED)" % (fmt(H["vsys_top"], 3), fmt(R["cv_max"], 3), fmt(H["smax_acc"][1] * 100, 0), H["smax_p"]))
    p("       startup: from VBUS the registers, the cell count from CELL_BATPRESZ, then \"Converter powers up\" (p.%d); with only the battery, above"
      % H["pu_p"])
    p("       VVBAT_UVLOZ (%s to %s V on SRN), \"charger wakes up and the BATFET is turned on\" (p.%d); no charge until ChargeCurrent is written (p.%d) (MAKER)"
      % (fmt(H["vbat_uvloz"][0], 2), fmt(H["vbat_uvloz"][1], 2), H["bat_only_p"], H["ichg_por_p"]))
    p("     (2) battery absent (or both of the pack's FETs open), the source on: p.%d's instant-on; p.%d, below VSYS_MIN \"the BATFET operates in linear"
      % (H["feat_p"], H["nvdc_p"]))
    p("       mode (LDO mode), and the system is regulated at VSYS_MIN\"; VSYS_MIN_REG_ACC %s V, minimum -%s %% (p.%d): at least %s V at TJ %s to %s C;"
      % (fmt(H["smin"], 2), fmt(H["smin_lo"] * 100, 0), H["smin_p"], fmt(H["floor"], 3), fmt(H["ec_tj"][0], 0), fmt(H["ec_tj"][1], 0)))
    p("       at most %s V by the VSYS pin's maximum limit and VSYSMAX_ACC (p.%d, p.%d): BOUNDED (MAKER, INFERRED)" % (fmt(H["vsys_top"], 3), H["vsys_pin_p"], H["smax_p"]))
    p("       the exact gap: VSYS_MIN_REG_ACC prints %s %% in its maximum column as well (p.%d), so the row's upper side is not printed; no claim here rests on it"
      % (H["smin_max_printed"], H["smin_p"]))
    p("       (the floor decides every claim); where a figure needs it, %s V is taken (+%s %%, ASSUMPTION) (MAKER)" % (fmt(H["smin_hi"], 3), fmt(H["smin_lo"] * 100, 0)))
    p("       startup: the same power-up from VBUS (p.%d); VSYS_UVP clamps the input to %s A while VSYS is under %s V and, after %s ms, shuts the"
      % (H["pu_p"], fmt(H["uvp"]["iin"], 1), fmt(H["uvp"]["v"], 1), fmt(H["uvp"]["deg"] * 1e3, 0)))
    p("       converter for %s ms and retries for %s ms, latching after %d failures in %s s (p.%d) (MAKER); VSYS's capacitance at most %s uF (the VBAT net's"
      % (fmt(H["uvp"]["off"] * 1e3, 0), fmt(H["uvp"]["on"] * 1e3, 0), H["uvp"]["n"], fmt(H["uvp"]["win"], 0), H["uvp_p"], fmt(H["c_vsys_max"] * 1e6, 1)))
    p("       %s uF of ceramics plus 10 %%, and the direct can at +%s %%); WITHDRAWN by the fix round: the %s A is the input clamp, not a delivered"
      % (fmt(H["c_vsys_nom"] * 1e6, 1), fmt(G["zk_tol"] * 100, 0), fmt(H["uvp"]["iin"], 1)))
    p("       current, so no start time follows from it; the start is bounded in 15b (INFERRED)")
    p("     (3) battery present, charging inhibited: CHRG_INHIBIT 1 inhibits the charge (p.%d); VSYSMAX_ACC with charge disabled: VSRN + 150 mV within"
      % H["inhibit_p"])
    p("       +-%s %% (p.%d), the BATFET off, so no battery current unless the load exceeds the source (supplement, p.%d); with the pack at its CUV stack VSYS"
      % (fmt(H["smax_acc"][1] * 100, 0), H["smax_p"], H["batdrv_p"]))
    p("       is at least %s V: BOUNDED (MAKER, INFERRED); startup as (1), the bit at 0 by POR, written from the hold flag (section 14)" % fmt(H["vsys_inh_cuv"], 3))
    p("     so each mode has the maker's printed bound on VSYS (D1 and D3 removed); the margin from the floor to A-14's assumed 10.0 V converter floor:")
    p("       %s V, which a load step in S2 or S4 must not use up (D2, no transient limit printed) (INFERRED)" % fmt(H["margin_floor"], 3))
    p("   12d. PROTECTION (MAKER)")
    p("     the input, system and battery over-voltage, input over-current, converter OCP and thermal rows are the same (12b); VSYS_UVP moves to %s V with"
      % fmt(H["uvp"]["v"], 1))
    p("       hiccup (12c); BATOC stops the converter and \"BATFET status is not impacted if need to supplement power to system\" (p.%d); in HIZ the BATFET"
      % H["batoc_p"])
    p("       stays on (BATFETOFF_HIZ %d), so CHG_INHIBIT's HIZ leaves the kit on the pack exactly as with the BQ25731 (R-a's rule on the line holds);"
      % H["regs"]["BATFETOFF_HIZ"][0])
    p("       BATFET_ENZ would force the BATFET off on battery and the kit would run through its body diode: never written (SESSION)")
    p("     for a pack below VSYS_MIN with the source overloaded, TI's peak power mode on VSYS undershoot is the one meant \"when ... battery is removed\"")
    p("       (p.%d); Figure 9-22 (p.%d) draws that mode (1 to 6 A on VSYS at VSYS_MIN 12.3 V, ICHG 0 A) at a scale that resolves no transient (MAKER)"
      % (H["pk_p"], H["f922_p"]))
    p("   12e. THE AFFECTED BUDGETS")
    p("     the inductor L2: with the pack at CUV supplementing at the gauge's OCD1 %s A, VSYS is %s V (Q39's drop), so S-117's %s A at %s V becomes %s A"
      % (fmt(Q["ocd1"][0], 0), fmt(H["l_vsys"], 3), fmt(H["l_s117"][3], 1), fmt(H["l_s117"][2], 1), fmt(H["l_i"], 3)))
    p("       and its worst peak %s A against Isat %s A (S-117: %s A): re-derived, %s %% up (INFERRED)"
      % (fmt(H["l_pk"], 2), fmt(H["l_isat"], 1), fmt(H["l_pk117"], 1), fmt((H["l_i"] / (H["l_s117"][0] * H["l_s117"][1] / H["l_s117"][2]) - 1) * 100, 2)))
    p("     L4-E8's bank, its ballasts, R11 and R12: on VBUS20, ahead of R16; the charger's input current and switching are the same rows: unchanged (INFERRED)")
    p("     the battery FET Q39 as first selected (SUPERSEDED by 15c: its -10 V rows do not bound BATDRV's 8.5 V drive): AOS AONS21357, %s V,"
      % fmt(Q["vds"], 0))
    p("       VGS +-%s V, RDS(on) at -10 V at most %s mOhm at 25 C and %s mOhm at 125 C, Ciss %s nF"
      % (fmt(Q["vgs"], 0), fmt(Q["rds25"] * 1e3, 1), fmt(Q["rds125"] * 1e3, 1), fmt(Q["ciss"] * 1e9, 2)))
    p("       typical, IDM %s A, IS %s A, RthJA %s C/W at 10 s and %s C/W steady on a 1 in2 2 oz board (Rev %s, pp.1 and 2) (MAKER); LCSC %s, stock %d (CATALOGUE)"
      % (fmt(Q["idm"], 0), fmt(Q["is"], 0), fmt(Q["rja10"], 0), fmt(Q["rja_ss"], 0), H["q_rev"], H["cat"]["AONS21357"][0], H["cat"]["AONS21357"][1]))
    p("       TI's selection (p.%d): P-channel, %s V or more for 1 to 4 cells, Ciss under %s nF: %s nF typical, %s %% of it (no maximum printed); VDS at"
      % (H["bf_p"], fmt(H["bf_v"], 0), fmt(H["bf_ciss"] * 1e9, 0), fmt(Q["ciss"] * 1e9, 2), fmt(Q["ciss"] / H["bf_ciss"] * 100, 1)))
    p("       SYSOVP %s V is %s %% of %s V; BATDRV's %s V at most is %s %% of VGS's rating (MAKER, INFERRED)"
      % (fmt(B["sysovp4s"], 1), fmt(Q["vds_use"] * 100, 1), fmt(Q["vds"], 0), fmt(H["drv"][2], 1), fmt(Q["vgs_use"] * 100, 1)))
    p("     the SOA: Figure 9 (p.%d) is junction-to-case on a large heatsink at TC 25 C (Note F, a single pulse), so on board A's copper the"
      % Q["fig9_p"])
    p("       junction-to-ambient single-pulse rating of Figure 14 decides; every protection current below sits at VDS under %s V, in Figure 9's RDS(on) region"
      % fmt(max(v for _l, _i, _t, v, _a, _h in Q["prot"]) + 0.005, 2))
    p("       and under IDM %s A (the docking inrush is not: below), and the LDO precharge's DC point (under 5 V at %s mA) is judged on RthJA (MAKER, INFERRED)"
      % (fmt(Q["idm"], 0), fmt(Q["i_pre"] * 1e3, 0)))
    p("     Figure 14 (Rev %s p.5, junction to ambient, single pulse, TA 25 C, Note H) read from the sheet's drawing: ZthJA(10 s) %s C/W against the"
      % (H["q_rev"], fmt(Q["z10"], 3)))
    p("       table's %s (MAKER, read); RDS(on) at its 125 C maximum above 125 C (ASSUMPTION); from the inside air %s C (L4-E9, RECORD):" % (fmt(Q["rja10"], 0), fmt(air, 1)))
    for name, i_, w, fr in Q["prof"]:
        p("       on battery at %s, %s A: %s W in Q39, %s %% of the pack's output, the endurance it costs (INFERRED)" % (name, fmt(i_, 3), fmt(w, 4), fmt(fr * 100, 3)))
    p("       10 A for 60 s: TJ %s C (MEETS); 10 A held: %s C at the steady %s C/W (MEETS) (INFERRED)" % (fmt(Q["tj_10a_60s"], 1), fmt(Q["tj_10a_ss"], 1), fmt(Q["rja_ss"], 0)))
    p("       the pack's %s A peak (%s W): from the air for at most %s s; after 10 A held, for at most %s s (INFERRED)"
      % (fmt(Q["i_peak"], 0), fmt(Q["p18"], 3), fmt(Q["t18_air"], 2), fmt(Q["t18_hot"], 3)))
    for lab, i_, t_, vds, tj_air, tj_hot in Q["prot"]:
        dur = ("%s s" % fmt(t_, 2)) if t_ >= 0.1 else (("%s ms" % fmt(t_ * 1e3, 1)) if t_ >= 1e-3 else ("%s us" % fmt(t_ * 1e6, 0)))
        p("       %s, %s A for %s (VDS %s V, deep in the SOA's RDS(on) region): TJ %s C from the air, %s C after 10 A held: %s (INFERRED)"
          % (lab, fmt(i_, 1), dur, fmt(vds, 3), fmt(tj_air, 1), fmt(tj_hot, 1), "MEETS" if tj_hot <= 150.0 else "NOT MET"))
    p("       so the sheet's own board does not carry the pack's protection envelope: below OCD1's %s A the gauge never trips, and %s A held needs an"
      % (fmt(Q["ocd1"][0], 0), fmt(Q["ocd1"][0], 0)))
    p("       installed RthJA of at most %s C/W (%s C/W for %s A held), against the sheet's %s: a Layer 9 bar (E11-29, CONDITIONAL); the fallback is the"
      % (fmt(Q["rja_need_20"], 2), fmt(Q["rja_need_18"], 2), fmt(Q["i_peak"], 0), fmt(Q["rja_ss"], 0)))
    p("       gauge's OCD1 set to what the installed path carries, or the bridge shedding on PROCHOT's IDCHG (INFERRED)")
    p("     the docking inrush (S1 from cold, the dependency round's pack loop, the discharge FET at once, no diode drop credited): %s A peak through"
      % fmt(Q["i_dock"], 1))
    p("       Q39's body diode into VSYS's %s uF at most, over IDM's %s A for %s us (time constant %s us): the sheet prints no body-diode pulse rating, only"
      % (fmt(Q["c_behind"] * 1e6, 1), fmt(Q["idm"], 0), fmt(Q["t_over_idm"] * 1e6, 1), fmt(Q["tau"] * 1e6, 1)))
    p("       IS %s A continuous: the exact gap (E11-30); the gauge's DSG drive rises in %s to %s us typical to maximum (bq4050 p.%d), with no minimum, so"
      % (fmt(Q["is"], 0), fmt(Q["dsg_rise"][1] * 1e6, 0), fmt(Q["dsg_rise"][2] * 1e6, 0), Q["dsg_rise"][0]))
    p("       it bounds nothing (MAKER, INFERRED); the same peak passes R17, F1 and the pack's FETs in arrangement (A)")
    p("     the precharge in LDO mode (a pack under VSYS_MIN with the source on): ChargeCurrent 0x0080, %s mA within +-%s %% at 0 to 85 C (p.%d), at"
      % (fmt(H["pre256"][0] * 1e3, 0), fmt(H["pre256"][2] * 100, 0), H["pre_p"]))
    p("       most %s mA; Q39 drops VSYS_MIN's %s V to the pack: TJ %s C at the CUV stack (%s V) and %s C at the Shutdown Voltage's %s V; TJ reaches"
      % (fmt(Q["i_pre"] * 1e3, 1), fmt(H["smin_hi"], 3), fmt(Q["tj_ldo_cuv"], 1), fmt(P["vsys_cuv"][0], 1), fmt(Q["tj_ldo_shut"], 1), fmt(P["vsys_shut"][0], 1)))
    p("       150 C at %s V; at 0x00C0 (%s mA at most) already at %s V, so R-b' takes 0x0080 and no charge under %s V on SRN (SESSION, INFERRED, the"
      % (fmt(Q["ldo_floor"], 3), fmt(Q["i_pre3"] * 1e3, 0), fmt(Q["ldo_floor3"], 3), fmt(math.ceil(Q["ldo_floor"] * 10) / 10, 1)))
    p("       steady %s C/W on the sheet's board, CONDITIONAL on E11-29); Q2's diode then carries %s W, TJ %s C (INFERRED)"
      % (fmt(Q["rja_ss"], 0), fmt(Q["q2_pre"][0], 3), fmt(Q["q2_pre"][1], 1)))
    p("     TI's own note: \"Typically the battery depletion threshold should be greater than the VSYS_MIN\" (p.%d); the pack's CUV (%s V) is under it,"
      % (H["depl_p"], fmt(P["vsys_cuv"][0], 1)))
    p("       so LDO-mode precharge is a normal state after a deep discharge, budgeted above (MAKER, INFERRED)")
    p("")
    p("13. THREE APPROACHES COMPARED (each complete; INFERRED unless marked)")
    p("   (A) the drawn BQ25731 with E11-24's hold-up; (B1) TI's BQ25730 with Q39, as 12; (B2) one other implementation whose maker's sheet states the")
    p("     property that removes D1 and D3: NONE FOUND. Looked at, held: the BQ25798 and BQ25792 (NVDC, both statements, but an integrated BATFET of")
    p("     %s A RMS and %s A for 1 s, BQ25798 p.%d, BQ25792 p.%d, under the pack's %s A); the LM74700-Q1 (p.%d, an ideal-diode controller: it blocks"
      % (fmt(C["bq98_rms"], 0), fmt(C["bq98_pk"], 0), C["bq98_p"], H["bq92"][2], fmt(C["pack_peak"], 0), H["lm747_p"]))
    p("     reverse current and regulates no node); the LT8705A (a buck-boost regulator with no battery FET); the TPS2595, TPS2596 and TPS1663 (eFuses).")
    p("     TI's external-FET NVDC parts other than the BQ25730 are its family and architecture, not a different implementation (MAKER, INFERRED)")
    p("   row | (A) | (B1)")
    for rid, a, b in cons_rows(R):
        p("     %s | %s | %s (MAKER, INFERRED)" % (rid, a, b))
    p("   carried over unchanged in (B1): every L4-E4 to L4-E8 figure on VBUS20 and the input (IIN_HOST 4.70 A, RSNS_RAC, EN_EXTILIM, the ILIM_HIZ line")
    p("     and knee, VINDPM, R11 8 mOhm, R12 12 mOhm, C147, L4-E8's six cans and 45 mOhm ballasts), ChargeVoltage, SYSOVP, BATOVP, ACOV, the converter's")
    p("     parts (Q7 to Q10, L2's part, R219, the compensation), R16, R17's value, R-b's case (i) (the 0x0200 row is the same), section 3 (RECORD, MAKER)")
    p("   re-derived in (B1): VSYS's range per mode (12c); L2's supplement current (%s A, 12e); the start (VSYS_UVP, 12c); ChargeCurrent's POR and"
      % fmt(H["l_i"], 3))
    p("     watchdog (R-a's persistence); R-b' under VSYS_MIN; Q39's loss, thermal bar and inrush; VSYS's capacitance split (CELL_FUSED's 104 uF now")
    p("     behind Q39); E11-24's bank withdrawn (12c's floor is %s V, where four cans would hold %s ms; the bank leaned on T_RESP) (INFERRED)"
      % (fmt(H["floor"], 3), fmt(H["bank_b1"] * 1e3, 3)))
    p("   power and heat into the case on battery: (A) none added; (B1) Q39 %s W at PS-IDLE-SPEC and %s W at PS-TYP, %s W at 10 A (INFERRED)"
      % (fmt(Q["prof"][0][2], 4), fmt(Q["prof"][1][2], 4), fmt(10.0 ** 2 * Q["rds125"], 3)))
    p("   endurance on battery: (A) none lost; (B1) %s %% at PS-IDLE-SPEC, %s %% at PS-TYP (INFERRED)" % (fmt(Q["prof"][0][3] * 100, 3), fmt(Q["prof"][1][3] * 100, 3)))
    p("   area on board A: (A) the bank and the direct can, about 5.5 cm2 (section 10); (B1) Q39's 5 x 6 mm land and the direct can, about 1 cm2 of parts,")
    p("     with Q39's copper sized by E11-29's bar (at least the sheet's 1 in2 of 2 oz copper, on any layer) (INFERRED)")
    p("   part cost at LCSC's 10-piece price (CATALOGUE, 2 October 2026): (A) %s USD (BQ25731, four EEHZK1E471P, B540C, RC2512, EEHZK1V181P); (B1) %s USD"
      % (fmt(H["cost"][0], 4), fmt(H["cost"][1], 4)))
    p("     (BQ25730, AONS21357, EEHZK1V181P): %s USD less; stock: BQ25731 %d, BQ25730 %d at LCSC (a supply item, E11-32) (CATALOGUE)"
      % (fmt(H["cost"][0] - H["cost"][1], 4), H["cat"]["BQ25731RSNR"][1], H["cat"]["BQ25730RSNR"][1]))
    p("   interacting controls: (A) four run-time rules, two of them tied to the gauge's FET state (R-a's S4 exception, R-b), R-c, the hold's flag, and the")
    p("     bank's reliance on T_RESP; (B1) three run-time rules (R-a with no exception, R-b' tied to the gauge, R-c), the flag, and two boot writes")
    p("     (EN_OOA 0, ChargeCurrent with the watchdog); the BATFET's registers stay at POR (SESSION, INFERRED)")
    p("")
    p("14. THE SELECTION, THE DRAFT AND U-04'S CLASS")
    p("   SELECTED (SESSION): (B1), TI's BQ25730 in U3's land with Q39 (the fix round, 15c: Q39 and Q40, two BUK6Y10-30P; 15a: board E on VSYS).")
    p("     Why: it is the only option whose maker prints a bound on VSYS in all three modes")
    p("     (12c), removing D1, D3 and D4 and bounding D7 inside 0 to 85 C, where (A) leaves D1 and D3 to TI and holds D2 with compensating parts on an")
    p("     assumed 1 ms; every setting L4-E4 to L4-E8 drafted rests on rows the two sheets print alike (12b); it costs less and removes the bank; its")
    p("     costs are named and bounded: Q39's thermal bar (E11-29), the docking pulse (E11-30), %s %% of the pack's output at PS-IDLE-SPEC, and"
      % fmt(Q["prof"][0][3] * 100, 3))
    p("     the BQ25730's stock (E11-32). No protected line changes and no money beyond parts (reserved.json names no schematic part) (SESSION)")
    p("   the draft: apply_gen_sch_a_charger.py (release-guarded, never applied here): U3 BQ25730RSNR (%s), pin 21 CH_BATDRV, Q39 AONS21357 (%s) between"
      % (H["cat"]["BQ25730RSNR"][0], H["cat"]["AONS21357"][0]))
    p("     VBAT and CH_BATQ, R17 and R149 moved to CH_BATQ, C236 EEHZK1V181P (C242139) on VBAT, CH_BATQ declared a segment of the pack path (SESSION)")
    p("   what it changes downstream: E11-27 to E11-32 added; E11-24 withdrawn and E11-05 not needed once E11-27 is applied; E11-22's case (iii) bounded")
    p("     inside 0 to 85 C; Q-TI-11's D1 and Q-TI-3's addendum fall away (D2's question stays); R-a's S4 exception withdrawn; section 3 unchanged (INFERRED)")
    p("   U-04's claims still open with (B1): D2 (S2 and S4 load steps against the %s V margin: bench E11-31, fallback R-c's step rule); Q39's thermal"
      % fmt(H["margin_floor"], 3))
    p("     bar (E11-29) and docking pulse (E11-30); D6, D8 (R-b's case (ii)); REQ-015 at 9.00 V at the plug as section 3g (E11-06, E11-09, E11-23); and")
    p("     on board E D9 and D10 (INFERRED)")
    p("   U-04 BY THE OWNER'S EXIT DEFINITION: A DOWNSTREAM QUALIFICATION TEST WITH BOUNDED EVIDENCE AND A WORKABLE FALLBACK, once E11-27 is applied:")
    p("     the three modes rest on the maker's printed rows; each open claim has a test or analysis that bounds it and a fallback that needs no new")
    p("     architecture (R-c's step rule; OCD1 set to the installed path; a slower DSG turn-on on board P). On the drawn board (A) it stays the")
    p("     architecture-level choice of section 11 (INFERRED)")
    p("")

# ============================================================================================ the fix round (cx36's B1, B2)
TJ_LIM_175 = 150.0       # C, SESSION (fix round): the junction limit for a part rated 175 C (25 K under its rating)
FIX_HELD_ACC = 1.0e-3    # A, SESSION (fix round): the held state's pack current acceptance on the bench (E11-31)
FIX_DOCK_CONTACTS = 1    # SESSION (fix round): 813 contacts carrying VSYS to board E (pin 1); seven stay ground
FIX_OCD1_HELD = True     # the sustained worst: just under the gauge's OCD1, which never trips below its threshold


def fet_bound(r10_25, r10_hot, t_hot, r45_25, vg, tj, r10_mid=None, t_mid=None):
    """An upper bound on a P-channel FET's RDS(on) at |VGS| = vg and junction tj from the maker's printed maxima only:
    the chord between the printed maxima at -4.5 V and -10 V (25 C) bounds the value at vg (each unit's RDS(on) is convex and
    falling in |VGS|, and so is their pointwise maximum: INFERRED), and the chord between the printed -10 V maxima bracketing
    tj bounds the temperature factor (convex rising in TJ: INFERRED); the gate ratio is taken from 25 C, where the threshold
    sits highest (it falls with temperature, so the hot ratio is no larger: INFERRED). Refuses a tj above the last printed row."""
    if tj > t_hot + 1e-9:
        refuse(4, "no printed RDS(on) maximum at %s C" % tj)
    kg = (r10_25 + (r45_25 - r10_25) * (10.0 - vg) / (10.0 - 4.5)) / r10_25
    if r10_mid is not None and tj >= t_mid:
        r10 = r10_mid + (r10_hot - r10_mid) * (tj - t_mid) / (t_hot - t_mid)
    else:
        r10 = r10_25 + (r10_hot - r10_25) * (tj - 25.0) / (t_hot - 25.0)
    return kg, r10 * kg


def fix_round(R, T):
    """The consolidation review cx36 (filed in set 27: records/l4close/checks/astra-check-l4close-1.md), read NOT YET. B1: board
    E's auxiliary domain sits on CELL_F, on the pack side of R17, so with Q39 off it still drains the pack and with the pack
    absent nothing feeds it; the 502.3 ms start rested on a 0.5 A input ceiling read as a delivered current. B2: Q39's thermal
    acceptance used RDS(on) at -10 V where BATDRV may give 8.5 V. And the charger minors (E1)."""
    H, Q0, G, B, P, E, F, C = R["H"], R["H"]["Q"], R["G"], R["B"], R["P"], R["E"], R["F"], R["C"]
    K = {}
    ge, ga = T["gen_e"], T["gen_a"]
    # ---- B1: board E's auxiliary domain as drawn (NETLIST)
    need(ge, r'ic\("U12", 6, "AP63205WU-7[^"]*", "TSOT6", \{"1": "\+5V_E6", "2": "CELL_F", "3": "CELL_F"', "U12 on CELL_F")
    need(ge, r'c\("C31", "10u 25V 1210", "CELL_F", "GND", "C1210"\)', "C31 on CELL_F")
    need(ge, r'ph\("J_FAN%s" % n, 3, "mixer fan %s under the plate \(12 V class fan on the pack node, low-side PWM, tachometer\)" % n, \{"1": "CELL_F"', "the fans on CELL_F")
    m = need(ge, r'_intent\.rail\("CELL_F", 14\.4, 10\.0, 18\.0, "F3".*?loads=\{"P_CP": ([\d.]+), "U12": ([\d.]+), "J_FAN1": ([\d.]+), "J_FAN2": ([\d.]+)\}', "CELL_F's loads", re.S)
    K["aux"] = dict(U12=f(m, 2), J_FAN1=f(m, 3), J_FAN2=f(m, 4))
    K["aux_a"] = sum(K["aux"].values())
    m = need(ge, r'r\("R42", "(\d+)k 1%", "CELL_F", "CELL_MON"\); r\("R43", "(\d+)k 1% \(ADC2: 0\.18 x pack\)", "CELL_MON", "GND"\)', "the pack monitor divider")
    K["div_r"] = (f(m, 1) + f(m, 2)) * 1e3
    K["i_div"] = R["cv_max"] / (K["div_r"] * 0.99)
    need(ge, r'part\("J_BLK", "Connector_Generic", "Conn_01x12", "[^"]*", "POGO_T6",\s+\{"1": "GND", "2": "GND"', "J_BLK pin 1 on GND")
    need(ga, r'part\("J_DOCK", "Connector_Generic", "Conn_01x12", "[^"]*", "POGO12",\s+\{"1": "GND", "2": "GND"', "J_DOCK pin 1 on GND")
    need(ge, r'"U12 is an AP63205 whose EN pin is tied to CELL_F, the pack node it runs from', "U12's EN on CELL_F")
    # the AP63205's input range (Diodes DS41326, held) and the SMCJ18A's leakage (Littelfuse SMC series, held)
    K["ap_vin"] = find("ap63200", r"VIN (\d+\.\d)V to (\d+)V", "the AP63205's input range")[1]
    K["ap_vin"] = (f(K["ap_vin"], 1), f(K["ap_vin"], 2))
    m = find("smcj", r"SMCJ18A\s+SMCJ18CA\s+\S+\s+\S+\s+(18\.0)\s+([\d.]+)\s+([\d.]+)\s+1\s+([\d.]+)\s+([\d.]+)\s+(\d+)", "SMCJ18A's row", layout=True)[1]
    K["d3_ir_ua"] = f(m, 6)
    # the dock's 813 contacts (w3de's model, pinned): the supply contact and the ground return with one contact fewer
    sp = importlib.util.spec_from_file_location("dock_contacts_pinned", read("dock_py"))
    dc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(dc)
    K["c813_max"] = dc.PD_MAX
    K["aux_share"] = K["aux_a"] / FIX_DOCK_CONTACTS / dc.PD_MAX
    K["aux_rise"] = dc.rise_813(K["aux_a"] / FIX_DOCK_CONTACTS)
    ret = []
    for n813 in (8, 8 - FIX_DOCK_CONTACTS):
        for opened in (0, 1):
            g_mm = dc.MM_RMAX / 8 + dc.R_POUR + dc.R_12AWG / 2
            n = n813 - opened
            g813 = dc.R_813_PATH / n
            i8 = (dc.I_VIN + dc.I_PACK_P) * (g_mm / (g_mm + g813)) / n
            ret.append((n813, opened, i8, 100 * i8 / dc.PD_MAX, dc.AIR["envelope 51 C"] + dc.rise_813(i8), dc.AIR["margin 65 C"] + dc.rise_813(i8)))
    K["ret"] = ret
    # the held state: the pack current with the charge inhibited and the source carrying the kit
    K["held_dv"] = R["cv_max"] - (R["cv_max"] + 0.150) * (1 - H["smax_acc"][0])     # VSYS may sit this far under VSRN
    K["held_bounded_a"] = K["i_div"] + K["d3_ir_ua"] * 1e-6
    # ---- the piecewise acceptance (the review's minor and E1)
    K["lo_v"] = H["smin"] * 0.98                       # VBAT_VSYS_MIN_RISE at least 98 %: below it, LDO mode
    K["hi_v"] = H["smin"] * 1.02                       # at most 102 %: above it, the battery-tracking mode
    m = find("bq25730", r"VBAT_VSYS_MIN_RISE\s+as percentage of 0x0D/0C\(\)\s+(\d+)%\s+(\d+)%\s+(\d+)%", "VBAT_VSYS_MIN_RISE", layout=True)[1]
    if (f(m, 1), f(m, 3)) != (98.0, 102.0):
        refuse(4, "VBAT_VSYS_MIN_RISE is not 98 to 102 %")
    K["track_floor_at_lo"] = (K["lo_v"] + 0.150) * (1 - H["smax_acc"][0])
    K["inh_floor"] = min(H["floor"], K["track_floor_at_lo"])
    K["review_case"] = (10.0 + 0.150) * (1 + H["smax_acc"][1])
    # ---- the start (VSYS_UVP), bounded where held evidence bounds it
    u = H["uvp"]
    K["uvlo30"] = [float(x) for x in H["uvlo30"][0]]
    K["e_start"] = 0.5 * H["c_vsys_max"] * K["uvlo30"][2] ** 2
    K["p_in_cap"] = u["iin"] * E["vb_top"]
    na = T["net_a"]
    rs = []
    for ref, _p in netlist_nodes(na, "VBAT"):
        if ref.startswith("R") and ref not in ("R17", "R149"):
            mm = re.match(r"([\d.]+)k", netlist_value(na, ref))
            if mm:
                rs.append((ref, float(mm.group(1)) * 1e3))
    K["start_rs"] = rs
    K["i_res_start"] = K["uvlo30"][2] * sum(1.0 / r for _r, r in rs)
    K["t_latch"] = u["deg"] + (u["n"] - 1) * (u["off"] + u["on"])
    K["por_p"] = find("bq25730", r"5 ms after either VBUS or VBAT becomes valid, the charger resets all the registers to the default state\.", "8.3.1's reset")[0]
    # ---- B2: three battery-FET options on one basis (MAKER rows; the bound of fet_bound)
    vg = H["drv"][0]
    air = {"route": None, "l4e9": F["air_hot"]}
    m = need(T["arch"], r"\| K9 \| E3-O, D-02a's \+55 C AMBIENT margin: the heat stage, every radio C1 leaves on \| open \| [\d.]+ \| \+55\.0 C \| \+(\d+) C \(U-02\)", "the consolidation's +70 C line")
    air["route"] = f(m)
    K["air"] = air
    zja, span = z_ja_aons()
    zss = Q0["rja_ss"]
    z = lambda t: min(1.0, zja(t) / zss)                # the board's transient shape, AOS Figure 14 over its steady 55 C/W
    K["z"] = {t: z(t) for t in (2.44e-4, 0.02, 1.0, 60.0)}
    vs = flat(pdf_pages("sqj403", True)[1])
    m = need(vs, r"VGS = -10 V ID = -10 A - ([\d.]+) ([\d.]+) VGS = -10 V ID = -10 A, TJ = 125 °C - - ([\d.]+) Drain-Source On-State Resistance a RDS\(on\)\s*\S?\s*VGS = -10 V ID = -10 A, TJ = 175 °C - - ([\d.]+) VGS = -4\.5 V ID = -7 A - [\d.]+ ([\d.]+)", "SQJ403EP's RDS(on) rows")
    sq = dict(r10_25=f(m, 2) * 1e3, r10_mid=f(m, 3) * 1e3, t_mid=125.0, r10_hot=f(m, 4) * 1e3, t_hot=175.0, r45_25=f(m, 5) * 1e3)
    sq["ciss_max"] = f(need(vs, r"Input Capacitance Ciss - (\d+) (\d+)", "SQJ403EP's Ciss"), 2) * 1e-12
    sq["ism"] = f(need(vs, r"Pulsed Current a ISM - - -(\d+)", "SQJ403EP's ISM"))
    v1 = flat(pdf_pages("sqj403", True)[0])
    sq["idm"] = f(need(v1, r"Pulsed Drain Current b IDM -(\d+)", "SQJ403EP's IDM"))
    sq["vgs"] = f(need(v1, r"Gate-Source Voltage VGS ± (\d+)", "SQJ403EP's VGS"))
    sq["rja"] = f(need(v1, r"Junction-to-Ambient PCB Mount c RthJA (\d+)", "SQJ403EP's RthJA"))
    sq["tj"] = f(need(v1, r"TJ, Tstg -55 to \+(\d+)", "SQJ403EP's TJ"))
    sq["rev"] = need(v1, r"(S15-2089-Rev\. A, 31-Aug-15)", "SQJ403EP's revision").group(1)
    nx = "\n".join(pdf_pages("buk6y10", True))
    m = need(nx, r"VGS = -10 V; ID = -13\.5 A; Tj = 25 °C\s+-\s+(\d+)\s+(\d+)\s+mΩ\s*\n\s+resistance\s+VGS = -10 V; ID = -13\.5 A; Tj = (\d+) °C\s+-\s+(\d+)\s+(\d+)\s+mΩ\s*\n\s+VGS = -4\.5 V; ID = -8\.5 A; Tj = 25 °C\s+-\s+(\d+)\s+(\d+)", "BUK6Y10-30P's RDSon rows")
    nxp = dict(r10_25=f(m, 2), t_hot=f(m, 3), r10_hot=f(m, 5), r45_25=f(m, 7))
    nxp["ciss"] = f(need(nx, r"Ciss\s+input capacitance\s+VDS = -15 V; f = 1 MHz; VGS = 0 V;\s+-\s+(\d+)\s+-", "BUK6Y10-30P's Ciss")) * 1e-12
    nxp["idm"] = f(need(nx, r"IDM\s+peak drain current\s+single pulse; tp ≤ 10 µs; Tmb = 25 °C\s+-\s+-(\d+)", "BUK6Y10-30P's IDM"))
    nxp["ism"] = f(need(nx, r"ISM\s+peak source current\s+single pulse; tp ≤ (\d+) µs; Tmb = 25 °C\s+-\s+-(\d+)", "BUK6Y10-30P's ISM"), 2)
    nxp["ism_tp"] = f(need(nx, r"ISM\s+peak source current\s+single pulse; tp ≤ (\d+) µs", "BUK6Y10-30P's ISM width")) * 1e-6
    nxp["vgs"] = f(need(nx, r"VGS\s+gate-source voltage\s+\[1\]\s+-(\d+)\s+(\d+)\s+V", "BUK6Y10-30P's VGS"))
    nxp["tj"] = f(need(nx, r"Tj\s+junction temperature\s+-55\s+(\d+)", "BUK6Y10-30P's Tj"))
    nxp["rthmb"] = f(need(nx, r"Rth\(j-mb\)\s+thermal resistance from\s+-\s+([\d.]+)\s+([\d.]+)", "BUK6Y10-30P's Rth(j-mb)"), 2)
    nxp["date"] = need(nx, r"(17 April 2020)\s+Product data sheet", "BUK6Y10-30P's date").group(1)
    aos = dict(r10_25=Q0["rds25"] * 1e3, r10_hot=Q0["rds125"] * 1e3, t_hot=125.0,
               r45_25=f(find("aons21357", r"VGS=-4\.5V, ID=-20A\s+([\d.]+)\s+([\d.]+)\s+mΩ", "AONS21357's -4.5 V row", layout=True)[1], 2))
    cands = [
        dict(key="a", lab="(Q-a) AOS AONS21357, one", n=1, tjlim=aos["t_hot"], rdef=aos, ciss=Q0["ciss"], ciss_kind="typical",
             pulse=Q0["idm"], pulse_kind="IDM only; no body-diode pulse rating", rboard=Q0["rja_ss"], vgs=Q0["vgs"], vds=Q0["vds"], tjr=150.0),
        dict(key="b", lab="(Q-b) Vishay SQJ403EP, one", n=1, tjlim=TJ_LIM_175, rdef=sq, ciss=sq["ciss_max"], ciss_kind="maximum",
             pulse=sq["ism"], pulse_kind="ISM (300 us test pulse)", rboard=sq["rja"], vgs=sq["vgs"], vds=30.0, tjr=sq["tj"]),
        dict(key="c", lab="(Q-c) Nexperia BUK6Y10-30P, two in parallel", n=2, tjlim=TJ_LIM_175, rdef=nxp, ciss=2 * nxp["ciss"], ciss_kind="typical, two",
             pulse=nxp["ism"], pulse_kind="ISM, tp at most 10 us, each", rboard=None, vgs=nxp["vgs"], vds=30.0, tjr=nxp["tj"]),
    ]
    ocd1 = Q0["ocd1"]
    ocd2 = [(i_, t_) for lab, i_, t_, _v, _a, _h in Q0["prot"] if lab == "the image's OCD2"][0]
    aold = [(i_, t_) for lab, i_, t_, _v, _a, _h in Q0["prot"] if lab == "the AFE's AOLD"][0]
    ascd = [(i_, t_) for lab, i_, t_, _v, _a, _h in Q0["prot"] if lab == "the image's ASCD"][0]
    for cd in cands:
        rd = cd["rdef"]
        kg, rb = fet_bound(rd["r10_25"], rd["r10_hot"], rd["t_hot"], rd["r45_25"], vg, cd["tjlim"], rd.get("r10_mid"), rd.get("t_mid"))
        cd["kg"], cd["rb"] = kg, rb * 1e-3                              # ohm, per FET, at the junction limit and 8.5 V
        n = cd["n"]
        pw = lambda i: (i / n) ** 2 * cd["rb"]                          # per FET: the even split bounds each FET's power
        cd["p"] = dict(p10=pw(10.0), p18=pw(Q0["i_peak"]), p20=pw(ocd1[0]), p24=pw(ocd2[0]), p30=pw(aold[0]), pscd=pw(ascd[0]))
        bud = {}
        for a_lab, ta in air.items():
            b = cd["tjlim"] - ta
            lim = {
                "10 A held": b / cd["p"]["p10"],
                "18 A for 60 s after 10 A held": b / (cd["p"]["p10"] + (cd["p"]["p18"] - cd["p"]["p10"]) * z(60.0)),
                "20 A held (under OCD1)": b / cd["p"]["p20"],
                "OCD2 24 A for 1 s after 20 A held": b / (cd["p"]["p20"] + (cd["p"]["p24"] - cd["p"]["p20"]) * z(1.0)),
                "AOLD 30 A for 20 ms after 20 A held": b / (cd["p"]["p20"] + (cd["p"]["p30"] - cd["p"]["p20"]) * z(0.02)),
                "ASCD 55.6 A for 244 us after 20 A held": b / (cd["p"]["p20"] + (cd["p"]["pscd"] - cd["p"]["p20"]) * z(2.44e-4)),
            }
            bud[a_lab] = lim
        cd["bars"] = bud
        cd["bar"] = {a: min(v.values()) for a, v in bud.items()}
        cd["bind"] = {a: min(v, key=v.get) for a, v in bud.items()}
        cd["board_ok"] = (cd["rboard"] is not None and cd["rboard"] <= cd["bar"]["route"])
        cd["ciss_ok"] = cd["ciss"] < H["bf_ciss"]
        cd["dock_peak"] = Q0["i_dock"]
        cd["dock_ok_cold"] = Q0["i_dock"] <= cd["pulse"] * n if cd["key"] != "a" else False
    K["cands"] = cands
    sel = cands[2]
    K["sel"] = sel
    # the selected pair's docking pulse: the ISM rectangle against the decaying pulse, all of it in one FET at 25 C, and from the
    # route's inside air with ISM derated linearly to the 175 C rating (ASSUMPTION A11-22), the largest share one FET may take
    i2t_pulse = Q0["i_dock"] ** 2 * Q0["tau"] / 2.0
    i2t_rect = nxp["ism"] ** 2 * nxp["ism_tp"]
    der = (nxp["tj"] - air["route"]) / (nxp["tj"] - 25.0)
    K["dock"] = dict(i2t_pulse=i2t_pulse, i2t_rect=i2t_rect, der=der, ism_hot=nxp["ism"] * der,
                     s_max=min(1.0, math.sqrt(i2t_rect * der / i2t_pulse), nxp["ism"] * der / Q0["i_dock"]))
    # the LDO-mode precharge with R17's tolerance, all of it in one FET of the pair (linear-mode sharing not assumed)
    r17_tol = 0.01
    K["i_pre"] = H["pre256"][0] * (1 + H["pre256"][2]) / (1 - r17_tol)
    K["ldo_floor"] = H["smin_hi"] - (sel["tjlim"] - air["route"]) / (sel["bar"]["route"] * K["i_pre"])
    K["rb_floor"] = max(math.ceil(K["ldo_floor"] * 10) / 10.0, P["cells"] * P["pre_win"][0])
    K["q2_pre"] = (K["i_pre"] * P["vsd_max"], air["route"] + K["i_pre"] * P["vsd_max"] * P["rja"])
    # the inductor in supplement mode and VSYS's supplement floor with the pair and R17
    r17 = 0.005 * (1 + r17_tol)
    K["vsys_sup"] = P["vsys_cuv"][0] - ocd1[0] * (r17 + sel["rb"] / sel["n"])
    K["l_i"] = H["l_s117"][0] * H["l_s117"][1] / K["vsys_sup"]
    K["l_pk"] = H["l_pk117"] * K["l_i"] / (H["l_s117"][0] * H["l_s117"][1] / H["l_s117"][2])
    K["prof"] = [(nm, i_, i_ ** 2 * sel["rb"] / sel["n"], i_ * sel["rb"] / sel["n"] / 14.4) for nm, i_, _w, _f in Q0["prof"]]
    K["turn_tau"] = (H["rdrv"][1] * sel["ciss"])
    J = {n: json.load(open(os.path.join(TOP, REC, "inputs", n), encoding="utf-8")) for n in FIX_INPUTS}
    K["cat"] = {J[n]["model"]: (J[n]["code"], J[n]["stock"], float(J[n]["price_usd"]["10"])) for n in FIX_INPUTS}
    return K


def render_fix(R, p):
    K, H, Q0, P, F = R["K"], R["H"], R["H"]["Q"], R["P"], R["F"]
    sel = K["sel"]
    p("15. THE FIX ROUND FOR THE CONSOLIDATION REVIEW (cx36, read NOT YET on set 27's 8fbb68b6: its B1, B2 and the charger minors)")
    p("   15a. B1: BOARD E'S AUXILIARY DOMAIN ON A SOURCE-CAPABLE FEED")
    p("     as drawn (NETLIST): U12 (the AP63205, its VIN and EN), C31 and both mixer fans (J_FAN1, J_FAN2, D7, D8) sit on CELL_F, the pack node")
    p("       before board A's R17 and the battery FET; CELL_F declares them at %s A (U12 %s, fans %s and %s); the counterexample holds: with"
      % (fmt(K["aux_a"], 2), fmt(K["aux"]["U12"], 2), fmt(K["aux"]["J_FAN1"], 2), fmt(K["aux"]["J_FAN2"], 2)))
    p("       the charge inhibited the battery FET is off (p.%d) and they still drain the pack, and with the pack absent nothing feeds them (NETLIST, MAKER)"
      % H["nvdc_p"])
    p("     the feed (SESSION): from VSYS alone, over the dock: board A's J_DOCK pin 1 from GND to VBAT (VSYS), board E's J_BLK pin 1 to a new net")
    p("       VSYS_E, and U12's VIN and EN, C31, the fans' supply pins and D7 and D8 on VSYS_E; CELL_F keeps the pack path to board A, D3, C1 and")
    p("       the pack monitor (R42 and R43). Why VSYS and no OR: VSYS exists whenever the pack or a source does (the battery FET on with the")
    p("       battery alone, p.%d, and its body diode under any fault of the drive), and a diode or ideal-diode OR with CELL_F would take the pack"
      % H["bat_only_p"])
    p("       whenever VSYS sits under it, which the +-%s %% row allows in the held state (INFERRED)" % fmt(H["smax_acc"][0] * 100, 0))
    p("     the contact: one 813 on pin 1, %s A declared, %s %% of its %s A, %s K by w3de's assumed I2 rise; the seven 813 ground contacts left carry,"
      % (fmt(K["aux_a"], 2), fmt(K["aux_share"] * 100, 1), fmt(K["c813_max"], 1), fmt(K["aux_rise"], 2)))
    p("       at the 32.1 A coincidence with every Mill-Max pin at 20 mOhm (w3de's model, pinned):")
    for n813, opened, i8, pct, t51, t65 in K["ret"]:
        p("       %d x 813 ground%s: %s A each, %s %% of 3.5 A, %s C at the 51 C air and %s C at the margin's 65 C (INFERRED, w3de's ASSUMPTIONS)"
          % (n813, ", one open" if opened else "", fmt(i8, 3), fmt(pct, 1), fmt(t51, 1), fmt(t65, 1)))
    p("       so taking one ground contact moves W3DE-DOCK-R1's residual by one contact's step and keeps the 51 C envelope under 85 C with one open;")
    p("       a second supply contact would leave six, %s C with one open at 51 C: one contact is taken (SESSION); losing it unpowers board E's"
      % fmt(dock_six_open(K), 1))
    p("       controller, which board A reads on HOT-R1 as the detector lost (IF-AE-DOCK hot_r1), a detected state (INFERRED)")
    p("     VSYS_E's range: the supplement floor %s V to %s V (15d); the AP63205 takes %s to %s V (Diodes DS41326 p.1); the fans, rated as 12 V class"
      % (fmt(K["vsys_sup"], 3), fmt(H["vsys_top"], 3), fmt(K["ap_vin"][0], 1), fmt(K["ap_vin"][1], 0)))
    p("       on CELL_F's 16.884 V, now see up to %s V: their maximum supply voltage is owed (E11-35) (MAKER, INFERRED)" % fmt(H["vsys_top"], 3))
    p("     the held state (the charge inhibited, an adequate source, the pack present): the battery FET off with no charging or supplement current")
    p("       (p.%d); board E on VSYS_E from the source; what the pack still feeds, by element (MAKER, NETLIST, INFERRED):" % H["nvdc_p"])
    p("       the pack monitor R42 + R43 (%s kOhm at -1 %%): %s mA at %s V, intended (the controller's own pack reading)"
      % (fmt(K["div_r"] / 1e3, 0), fmt(K["i_div"] * 1e3, 4), fmt(R["cv_max"], 3)))
    p("       D3, SMCJ18A: IR at most %s uA at 18 V and 25 C (Littelfuse SMC series, held); its hot leakage is not printed" % fmt(K["d3_ir_ua"], 0))
    p("       the battery FETs' body diodes: VSYSMAX_ACC's -%s %% lets VSYS sit up to %s V under the pack at %s V, a forward bias at which the sheets"
      % (fmt(H["smax_acc"][0] * 100, 0), fmt(K["held_dv"], 3), fmt(R["cv_max"], 3)))
    p("       print no current (VSD only at 80 A): not bounded on held evidence; and the charger's SRN pin, whose leakage row prints a mismatch only")
    p("     so no kit load is fed from the pack while the source carries it; the bounded drains total %s mA, and the bench reads the held pack"
      % fmt(K["held_bounded_a"] * 1e3, 4))
    p("       current at most %s mA (E11-31's acceptance; board E's aux drew about 0.5 to 1.5 W from the pack before) (SESSION, CONDITIONAL)" % fmt(FIX_HELD_ACC * 1e3, 1))
    p("     the source-only sequence (the pack absent or both its FETs open): the source and the entry (3c); the front end to VBUS20; U3's POR (p.%d),"
      % K["por_p"])
    p("       ChargeCurrent 0 A; the converter up; VSYS through VSYS_UVP's start (15b) to VSYS_MIN; board A's always-on and board E's U12 on VSYS_E;")
    p("       E's controller up and driving HOT-R1; firmware: EN_OOA 0, IIN_HOST 4.70 A, CHRG_INHIBIT from the hold flag (INFERRED, MAKER)")
    p("     the held sequence: the flag set writes CHRG_INHIBIT 1; the battery FET turns off as the charge stops (p.%d); VSYS moves to VSRN + 150 mV;"
      % H["nvdc_p"])
    p("       nothing on either board moves; the flag cleared writes 0 and ChargeCurrent by R-b' (INFERRED)")
    p("   15b. THE START, BOUNDED WHERE THE HELD SHEETS BOUND IT (the 502.3 ms of 12c withdrawn: 0.5 A is an input ceiling, not a delivered current)")
    p("     the input limits (MAKER, p.%d): under %s V of VSYS (VSYS_UVLO; rising %s/%s/%s V, p.13) the input is clamped to %s A, at most %s W from VBUS20's"
      % (H["uvp_p"], fmt(H["uvp"]["v"], 1), fmt(K["uvlo30"][0], 2), fmt(K["uvlo30"][1], 1), fmt(K["uvlo30"][2], 2), fmt(H["uvp"]["iin"], 1), fmt(K["p_in_cap"], 2)))
    p("       %s V top; the sheet prints no minimum delivered current below that voltage (MAKER)" % fmt(R["E"]["vb_top"], 2))
    p("     the loads below %s V: the converters on VSYS held off by their enables or their UVLOs (the LM5176 stages by logic, U12 on board E under"
      % fmt(K["uvlo30"][2], 2))
    p("       its %s V start, the heater buck by its divider); the resistors on VBAT (%s): at most %s mA at %s V; the ICs' currents under UVLO are not"
      % (fmt(K["ap_vin"][0], 1), ", ".join("%s %s k" % (r_, fmt(v / 1e3, 0)) for r_, v in K["start_rs"]), fmt(K["i_res_start"] * 1e3, 4), fmt(K["uvlo30"][2], 2)))
    p("       all held (NETLIST, INFERRED); the energy to bring VSYS's %s uF to %s V: %s mJ (INFERRED)"
      % (fmt(H["c_vsys_max"] * 1e6, 1), fmt(K["uvlo30"][2], 2), fmt(K["e_start"] * 1e3, 3)))
    p("     the retries (MAKER): each failed start shuts the converter for %s ms and retries for %s ms; the %dth failure inside %s s latches it, at"
      % (fmt(H["uvp"]["off"] * 1e3, 0), fmt(H["uvp"]["on"] * 1e3, 0), H["uvp"]["n"], fmt(H["uvp"]["win"], 0)))
    p("       most %s s after the first window (INFERRED); with no pack only a POR clears it (VBUS re-plugged: \"5 ms after either VBUS or VBAT becomes"
      % fmt(K["t_latch"], 3))
    p("       valid, the charger resets all the registers\", p.%d), with a pack the host does (it runs on the pack through the battery FET) (MAKER)" % K["por_p"])
    p("     so on held evidence the start ends in VSYS_MIN or in a latch within %s s, never undefined; whether the first window succeeds is not"
      % fmt(K["t_latch"], 3))
    p("       bounded (no minimum delivered current): BENCH E11-31, acceptance: from cold, at VBUS20 %s and %s V, with VSYS's maximum capacitance and the"
      % (fmt(R["E"]["vb_low"], 2), fmt(R["E"]["vb_top"], 2)))
    p("       declared always-on loads (board E on VSYS_E), at -20, 25 and %s C, VSYS reaches %s V with Fault VSYS_UVP clear; the hiccup's %s/%s ms and"
      % (fmt(F["air_hot"], 1), fmt(H["floor"], 3), fmt(H["uvp"]["off"] * 1e3, 0), fmt(H["uvp"]["on"] * 1e3, 0)))
    p("       the latch shown on a shorted VSYS and cleared by a re-plug (SESSION)")
    p("   15c. B2: THE BATTERY FET, THREE OPTIONS ON ONE BASIS (the drive BATDRV gives at its least, %s V, p.17; RDS(on) from the makers' printed"
      % fmt(H["drv"][0], 1))
    p("     [SUPERSEDED IN PART by section 16: fet_bound's figure is an allowance, not a bound; AOS's shape, the Ciss reading and the docking I2t")
    p("     are replaced; the selection of the pair stands] (SESSION)")
    p("     maxima only, bounded by fet_bound: the gate chord between -4.5 and -10 V, the temperature chord between the printed -10 V rows) (MAKER, INFERRED)")
    p("     the inside air: the consolidation's +%s C mixed-air line for the parts that must work in the heat stage (L4-POWER-ARCHITECTURE K9, E3-O"
      % fmt(K["air"]["route"], 0))
    p("       at +55 C ambient; K3 at +40 C), reconciled with L4-E9's %s C, which it covers; the board's transient shape from AOS Figure 14 over its"
      % fmt(K["air"]["l4e9"], 1))
    p("       steady %s C/W for every option: z(244 us) %s, z(20 ms) %s, z(1 s) %s, z(60 s) %s (ASSUMPTION A11-21 for the other packages) (MAKER, read)"
      % (fmt(Q0["rja_ss"], 0), fmt(K["z"][2.44e-4], 5), fmt(K["z"][0.02], 4), fmt(K["z"][1.0], 4), fmt(K["z"][60.0], 4)))
    p("     the events, each from a hot state, per FET (the even split bounds each FET's power for any split of the RDS(on) spread): 10 A held; 18 A")
    p("       for 60 s after 10 A held (PWR-F12's service); 20 A held, under the gauge's OCD1, which never trips below it; from it OCD2's 24 A for 1 s,")
    p("       the AFE's AOLD 30 A for 20 ms and the image's ASCD 55.6 A for 244 us; the bar is the installed junction-to-air resistance per FET at")
    p("       which every event keeps TJ at the limit or under (INFERRED)")
    for cd in K["cands"]:
        rd = cd["rdef"]
        p("     %s (MAKER, INFERRED):" % cd["lab"])
        p("       printed maxima: %s mOhm at -10 V and 25 C, %s mOhm at -10 V and %s C, %s mOhm at -4.5 V and 25 C; the bound at %s V and the junction"
          % (fmt(rd["r10_25"], 1), fmt(rd["r10_hot"], 1), fmt(rd["t_hot"], 0), fmt(rd["r45_25"], 1), fmt(H["drv"][0], 1)))
        p("         limit %s C (the sheet's last printed temperature or 25 K under a 175 C rating): gate factor %s, %s mOhm per FET"
          % (fmt(cd["tjlim"], 0), fmt(cd["kg"], 4), fmt(cd["rb"] * 1e3, 3)))
        p("       Ciss %s nF (%s) against TI's %s nF: %s; VGS +-%s V against BATDRV's %s V; VDS %s V against SYSOVP's %s V"
          % (fmt(cd["ciss"] * 1e9, 2), cd["ciss_kind"], fmt(H["bf_ciss"] * 1e9, 0), "MEETS" if cd["ciss_ok"] else "NOT MET", fmt(cd["vgs"], 0),
             fmt(H["drv"][2], 1), fmt(cd["vds"], 0), fmt(R["B"]["sysovp4s"], 1)))
        for a_lab, ta in (("route", K["air"]["route"]), ("l4e9", K["air"]["l4e9"])):
            p("       the bar at %s C air: %s C/W per FET, set by %s" % (fmt(ta, 1), fmt(cd["bar"][a_lab], 2), cd["bind"][a_lab]))
        p("       the maker's reference board: %s; the docking pulse, %s A peak: %s A %s (MAKER, INFERRED)"
          % (("%s C/W, %s" % (fmt(cd["rboard"], 0), "inside the bar" if cd["board_ok"] else "over the bar")) if cd["rboard"] is not None else "none printed (LFPAK56, a junction-to-mounting-base %s K/W)" % fmt(rd["rthmb"], 1),
             fmt(Q0["i_dock"], 1), fmt(cd["pulse"], 0), cd["pulse_kind"]))
    d = K["dock"]
    p("   SELECTED (SESSION): %s, Q39 and Q40 (LCSC %s, %d in stock, %s USD each at 10). Why: the only option inside TI's Ciss (%s nF typical"
      % (sel["lab"][6:], K["cat"]["BUK6Y10-30PX"][0], K["cat"]["BUK6Y10-30PX"][1], fmt(K["cat"]["BUK6Y10-30PX"][2], 4), fmt(sel["ciss"] * 1e9, 2)))
    p("     for the two) with a bar of the order a board pour gives: %s C/W per FET at +%s C air, %s of AOS's 1 in2 figure for the same 5 x 6 mm class,"
      % (fmt(sel["bar"]["route"], 2), fmt(K["air"]["route"], 0), fmt(sel["bar"]["route"] / Q0["rja_ss"], 3)))
    p("       where (Q-a) needs %s C/W (%s of its maker's board) and (Q-b) %s C/W (%s of its maker's), which a pour does not give one part; a printed RDS(on)"
      % (fmt(K["cands"][0]["bar"]["route"], 2), fmt(K["cands"][0]["bar"]["route"] / K["cands"][0]["rboard"], 3),
         fmt(K["cands"][1]["bar"]["route"], 2), fmt(K["cands"][1]["bar"]["route"] / K["cands"][1]["rboard"], 3)))
    p("     maximum to 175 C, a 175 C rating, and a printed body-diode pulse rating (ISM %s A each) over the docking pulse; a third FET would put"
      % fmt(sel["rdef"]["ism"], 0))
    p("     Ciss at %s nF typical, over TI's %s nF (SESSION, INFERRED)" % (fmt(3 * sel["rdef"]["ciss"] * 1e9, 2), fmt(R["H"]["bf_ciss"] * 1e9, 0)))
    p("     its envelope at the bar, +%s C air: TJ at most %s C for every event of 15c; 18 A for 60 s after 10 A held: %s C (INFERRED, CONDITIONAL on E11-29)"
      % (fmt(K["air"]["route"], 0), fmt(sel["tjlim"], 0), fmt(sel_tj_18(K), 1)))
    p("     the docking pulse: all of it in one FET at 25 C: %s A against ISM %s A and %s A2s against the ISM rectangle's %s A2s (MEETS); from the"
      % (fmt(Q0["i_dock"], 1), fmt(sel["rdef"]["ism"], 0), fmt(d["i2t_pulse"], 4), fmt(d["i2t_rect"], 4)))
    p("       +%s C air, ISM derated linearly to the 175 C rating (x%s, ASSUMPTION A11-22): %s A and %s A2s, met for a share of at most %s in one FET;"
      % (fmt(K["air"]["route"], 0), fmt(d["der"], 4), fmt(d["ism_hot"], 1), fmt(d["i2t_rect"] * d["der"], 4), fmt(d["s_max"], 3)))
    p("       the split of two body diodes is not printed: E11-30 (the bench pulse on the pair, or a layout matching the two paths) (INFERRED)")
    p("     the drive: BATDRV's %s kOhm at most into %s nF: a %s us time constant (MAKER, INFERRED)" % (fmt(H["rdrv"][1] / 1e3, 0), fmt(sel["ciss"] * 1e9, 2), fmt(K["turn_tau"] * 1e6, 2)))
    p("     the precharge in LDO mode with R17's 1 %%: %s A at most (0.256 x 1.30 / 0.99, the review's minor), all of it in one FET (linear-mode sharing"
      % fmt(K["i_pre"], 5))
    p("       not assumed): TJ reaches %s C at the bar and +%s C air with SRN at %s V, so R-b' allows no charge under %s V on SRN (the cells' 1.0 V a"
      % (fmt(sel["tjlim"], 0), fmt(K["air"]["route"], 0), fmt(K["ldo_floor"], 3), fmt(K["rb_floor"], 1)))
    p("       cell floor is %s V); Q2's diode then %s W, TJ %s C (SESSION, INFERRED; R17's drift with temperature not held)"
      % (fmt(P["cells"] * P["pre_win"][0], 1), fmt(K["q2_pre"][0], 4), fmt(K["q2_pre"][1], 1)))
    for nm, i_, w, fr in K["prof"]:
        p("     on battery at %s, %s A: %s W in the pair, %s %% of the pack's output (INFERRED)" % (nm, fmt(i_, 3), fmt(w, 4), fmt(fr * 100, 3)))
    p("     L2 with the pair: VSYS in supplement %s V (CELL_FUSED's 10.0 V less R17 and the pair at OCD1's 20 A), %s A, peak %s A against Isat %s A (INFERRED)"
      % (fmt(K["vsys_sup"], 3), fmt(K["l_i"], 3), fmt(K["l_pk"], 2), fmt(H["l_isat"], 1)))
    p("   15d. THE CHARGER MINORS (E1)")
    p("     the inhibited acceptance, piecewise (VBAT_VSYS_MIN_RISE 98 to 102 %% of VSYS_MIN, p.14): SRN under %s V: LDO mode, VSYS at least %s V;"
      % (fmt(K["lo_v"], 3), fmt(H["floor"], 3)))
    p("       SRN over %s V: VSRN + 150 mV within +-%s %%; between, either, so at least %s V; the review's case, SRN at 10 V, is the LDO region, and"
      % (fmt(K["hi_v"], 3), fmt(H["smax_acc"][0] * 100, 0), fmt(K["inh_floor"], 3)))
    p("       (10 + 0.15) x 1.02 = %s V belongs to no region (MAKER, INFERRED)" % fmt(K["review_case"], 3))
    p("     the upper side in the LDO region, %s V, is an assumed reading of TI's malformed maximum column (A11-18), not a printed limit (MAKER)"
      % fmt(H["smin_hi"], 3))
    p("     every floor above holds with adequate input power; with the source overloaded VSYS follows the pack through the battery FETs and R17:")
    p("       %s V at CELL_FUSED's 10.0 V and OCD1's 20 A; with no pack and an overloaded source there is no floor, R-c sheds (INFERRED)" % fmt(K["vsys_sup"], 3))
    p("     EN_OOA resets to %d (p.%d): the printed accuracy covers VSYS only after the firmware writes 0; the pre-firmware start has no printed accuracy"
      % (H["regs"]["EN_OOA"][0], H["regs"]["EN_OOA"][1]))
    p("       (E11-31 records it) (MAKER)")
    p("     the text that still says \"no battery FET\" in L4-E9's record and the system node's label are drafted for their owner (E11-34) (INFERRED)")
    p("")


def dock_six_open(K):
    """The 51 C figure with six 813 ground contacts and one of them open (a second supply contact), from w3de's model."""
    sp = importlib.util.spec_from_file_location("dock_contacts_pinned6", read("dock_py"))
    dc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(dc)
    g_mm = dc.MM_RMAX / 8 + dc.R_POUR + dc.R_12AWG / 2
    n = 5
    i8 = (dc.I_VIN + dc.I_PACK_P) * (g_mm / (g_mm + dc.R_813_PATH / n)) / n
    return dc.AIR["envelope 51 C"] + dc.rise_813(i8)


def sel_tj_18(K):
    sel, z60 = K["sel"], K["z"][60.0]
    r = sel["bar"]["route"]
    return K["air"]["route"] + r * (sel["p"]["p10"] + (sel["p"]["p18"] - sel["p"]["p10"]) * z60)

# ============================================================================================ the review of the provisional fixes (L4-F02, L4-F03)
F16_RA = 21.136e-3      # ohm per FET, SESSION: the RDS(on) ALLOWANCE at BATDRV's least 8.5 V and the 150 C limit the design is sized to;
                        # section 15c's figure, no longer called a bound (no sheet prints a maximum there); confirmed by E11-36 or reversed
F16_RA_ALT = 25.0e-3    # ohm, the sheet's largest printed maximum (-4.5 V, 25 C): the sensitivity printed beside the allowance
F16_TJ_HELD = 140.0     # C, SESSION: the held fault's (20 A under OCD1) junction ceiling, 10 K under the limit kept for the pulses from it
F16_READ = "nexperia-buk6y10-30p-figure-readings-2026-10-02.json"
F16_RILIM_K = 11.0      # kOhm 0.1 %, SESSION: the eFuse's ILIM resistor
F16_RILIM_TOL = 0.001
F16_CDVDT = 22e-9       # F, SESSION: the eFuse's dVdT capacitor (TI's characterised 22 nF row)
F16_CDVDT_TOL = 0.10
F16_OVL = (5.0, 14.4)   # the review's counterexample: 5 A drawn from 14.4 V (2.88 Ohm) on VSYS_E
F16_SPREAD = 2.0        # w3de's assumed 2:1 spread of a contact's static resistance (dock_contacts.py)


def zjmb_table(J):
    """BUK6Y10-30P Fig. 4 (the duty-cycle 0.01 curve, above any single pulse), read on the rendered page (inputs/F16_READ), scaled so
    its plateau is Table 6's maximum Rth(j-mb); log-log interpolation; below the first point it is held at the first point's value
    (Z rises with the pulse, so this bounds it from above)."""
    pts, top = [], 0.0
    for t, z in J["fig4"]["points_s_kw"]:
        top = max(top, float(z))                      # Z never falls with a longer pulse: the reading's dips past the plateau are not used
        pts.append((float(t), top))
    return pts


def zjmb_at(pts, scale, rmax, t):
    if t <= pts[0][0]:
        return pts[0][1] * scale
    if t >= pts[-1][0]:
        return rmax
    for (t0, z0), (t1, z1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            fr = (math.log(t) - math.log(t0)) / (math.log(t1) - math.log(t0))
            return min(rmax, scale * math.exp(math.log(z0) + fr * (math.log(z1) - math.log(z0))))
    return rmax


def dock_rise(zf, i0, tau, vsd, is_t, k, dt=0.2e-6, span=300e-6):
    """The junction rise of ONE FET carrying the whole docking pulse i0 exp(-t/tau) through its body diode (no sharing assumed),
    P = k VF(i) i with VF(i) at most max(VSD, VSD i / IS_test): VF is concave in i through the origin, so VF(i)/i does not rise with
    i above the printed point (INFERRED); k scales the printed 25 C point for a hot junction. Superposition on zf. Returns the
    largest rise, the energy and the peak power."""
    n = int(span / dt)
    P = []
    for j in range(n):
        i = i0 * math.exp(-j * dt / tau)
        P.append(k * max(vsd, vsd * i / is_t) * i)
    zg = [zf((j + 1) * dt) for j in range(n)]
    dP = [P[0]] + [P[j] - P[j - 1] for j in range(1, n)]
    best, t_best = 0.0, 0.0
    for m in range(n):
        s = 0.0
        for j in range(m + 1):
            s += dP[j] * zg[m - j]
        if s > best:
            best, t_best = s, (m + 1) * dt
    return best, sum(P) * dt, P[0], t_best


def fix16_round(R, T):
    """The review of the provisional fixes (2 October 2026): L4-F02 keeps B2 open (RDS(on) at 8.5 V inferred, the transient shape
    borrowed from AOS, Ciss typical against TI's 5 nF, the docking pulse converted into an I2t the sheet does not print) and
    L4-F03 finds the dock's new VSYS contact without branch protection."""
    H, Q0, K = R["H"], R["H"]["Q"], R["K"]
    sel = K["sel"]
    nxp = sel["rdef"]
    L = {}
    J = json.load(open(os.path.join(TOP, REC, "inputs", F16_READ), encoding="utf-8"))
    if J["sha256"] != PINS["buk6y10"][1]:
        refuse(4, "the figure readings name another BUK6Y10-30P sheet")
    nx = "\n".join(pdf_pages("buk6y10", True))
    L["rthmb"] = nxp["rthmb"]
    m = need(nx, r"VSD\s+source-drain voltage\s+IS = -(\d+) A; VGS = 0 V; Tj = 25 °C\s+-\s+-([\d.]+)\s+-([\d.]+)\s+V", "BUK6Y10-30P's VSD")
    L["vsd_is"], L["vsd_max"] = f(m, 1), f(m, 3)
    m = need(nx, r"IS\s+source current\s+Tmb = 25 °C\s+-\s+-(\d+)\s+A", "BUK6Y10-30P's IS")
    L["is_dc"] = f(m)
    need(nx, r"Fig\. 4\.\s+Transient thermal impedance from junction to mounting base as a function of pulse duration", "Fig. 4")
    need(nx, r"Fig\. 12\. Input, output and reverse transfer capacitances", "Fig. 12")
    pts = zjmb_table(J)
    L["plateau"] = float(J["fig4"]["plateau_kw"])
    if abs(max(z for _t, z in pts) - L["plateau"]) > 1e-9 or not all(a[1] <= b[1] + 1e-9 for a, b in zip(pts, pts[1:9])):
        refuse(4, "the Fig. 4 reading is not a rising curve with the stated plateau")
    L["zscale"] = L["rthmb"] / L["plateau"]
    zf = lambda t: zjmb_at(pts, L["zscale"], L["rthmb"], t)
    L["zf"] = zf
    L["z"] = {t: zf(t) for t in (2.44e-4, 0.02, 1.0, 60.0)}
    # ---- objection 1: what the sheet prints, and the allowance
    L["r10_hot"], L["r45_25"], L["r10_25"] = nxp["r10_hot"] * 1e-3, nxp["r45_25"] * 1e-3, nxp["r10_25"] * 1e-3
    L["ra"] = F16_RA
    if abs(F16_RA - sel["rb"]) > 1e-6:
        refuse(4, "the allowance is not section 15c's figure")
    # ---- objection 2: the events on the device's own Zth(j-mb) and the installed pair's self and mutual impedance
    ocd1 = Q0["ocd1"]
    ocd2 = [(i_, t_) for lab, i_, t_, _v, _a, _h in Q0["prot"] if lab == "the image's OCD2"][0]
    aold = [(i_, t_) for lab, i_, t_, _v, _a, _h in Q0["prot"] if lab == "the AFE's AOLD"][0]
    ascd = [(i_, t_) for lab, i_, t_, _v, _a, _h in Q0["prot"] if lab == "the image's ASCD"][0]
    air = K["air"]["route"]

    def plan(ra, zsum=None):
        pb = lambda i: (i / 2.0) ** 2 * ra                     # per FET: the even split bounds each FET's power (section 15c)
        if zsum is None:
            zsum = (F16_TJ_HELD - air) / pb(ocd1[0])            # (Zself + Zmut) steady: 20 A held reaches the held ceiling
        pre10 = air + pb(10.0) * zsum
        tj18 = pre10 + (pb(Q0["i_peak"]) - pb(10.0)) * zsum     # no transient credit at 60 s
        ev = []
        for lab, (i_, t_) in (("OCD2 %s A for %s s" % (fmt(ocd2[0], 0), fmt(ocd2[1], 0)), ocd2), ("AOLD %s A for %s ms" % (fmt(aold[0], 0), fmt(aold[1] * 1e3, 0)), aold),
                              ("ASCD %s A for %s us" % (fmt(ascd[0], 1), fmt(ascd[1] * 1e6, 0)), ascd)):
            dp = pb(i_) - pb(ocd1[0])
            allow = (150.0 - F16_TJ_HELD) / dp
            ev.append((lab, i_, t_, pb(i_), allow, zf(t_), allow - zf(t_)))
        return dict(pb10=pb(10.0), pb18=pb(Q0["i_peak"]), pb20=pb(ocd1[0]), zsum=zsum, pre10=pre10, tj18=tj18, ev=ev,
                    tj20=air + pb(ocd1[0]) * zsum,
                    pre_ldo=(150.0 - air) / zsum / K["i_pre"])
    L["plan"] = plan(F16_RA)
    L["plan_alt"] = plan(F16_RA_ALT)
    L["plan_miss"] = plan(F16_RA_ALT, L["plan"]["zsum"])       # parts at 25 mOhm on a board built to the allowance's sum
    L["ldo_floor16"] = H["smin_hi"] - L["plan"]["pre_ldo"]
    # ---- objection 3: Ciss
    L["ciss_t"] = nxp["ciss"]
    L["ciss_0"] = float(J["fig12"]["ciss_typ_pf_at_vds_minus_0v1"]) * 1e-12
    m = find("bq25730", r"RBATDRV_OFF\s+10 µA current from\s+([\d.]+)\s+([\d.]+)\s+kΩ", "RBATDRV_OFF", layout=True)
    L["roff"] = (f(m[1], 1) * 1e3, f(m[1], 2) * 1e3)
    L["ciss_p"] = find("bq25730", r"the Ciss of\s+P-channel MOSFET should be chosen less than 5 nF\.", "TI's Ciss rule", layout=True)[0]
    L["tau_on"] = (H["rdrv"][1] * 2 * L["ciss_t"], H["rdrv"][1] * 2 * L["ciss_0"])
    L["tau_off"] = L["roff"][1] * 2 * L["ciss_0"]
    L["one_rja"] = (F16_TJ_HELD - air) / (ocd1[0] ** 2 * F16_RA)
    # ---- objection 4: the docking pulse, the whole of it in one FET, from the hot air
    L["dock_k1"] = dock_rise(zf, Q0["i_dock"], Q0["tau"], L["vsd_max"], L["vsd_is"], 1.0)
    L["k_max"] = (150.0 - air) / L["dock_k1"][0]
    L["vf_pk_bound"] = L["vsd_max"] * Q0["i_dock"] / L["vsd_is"]
    L["t_over_is"] = Q0["tau"] * math.log(Q0["i_dock"] / L["is_dc"])
    L["i_at_tp"] = Q0["i_dock"] * math.exp(-nxp["ism_tp"] / Q0["tau"])
    # ---- L4-F03: the branch protection for the dock's VSYS contact
    tp = "\n".join(pdf_pages("tps1663", True))
    m = need(tp, r"R\(ILIM\) = 30kΩ, V\(IN\) \u2013 V\(OUT\) = 1V\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+A", "I(OL) at 30 kOhm")
    r30 = (f(m, 1), f(m, 2), f(m, 3))
    m = need(tp, r"R\(ILIM\) = 9kΩ, V\(IN\) \u2013 V\(OUT\) = 1V\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+A", "I(OL) at 9 kOhm")
    r9 = (f(m, 1), f(m, 2), f(m, 3))
    need(tp, r"IOL = R 18", "Equation 6")
    m = need(tp, r"IN to OUT total ON resistance\s+(\d+)\s+([\d.]+)\s+(\d+)\s+mΩ", "RON over temperature")
    L["ron"] = (f(m, 1) * 1e-3, f(m, 2) * 1e-3, f(m, 3) * 1e-3)
    m = need(tp, r"tCL_PLIM\(dly\)\s+(\d+)\s+(\d+)\s+(\d+)\s+ms", "tCL_PLIM(dly)")
    L["tcl"] = (f(m, 1) * 1e-3, f(m, 3) * 1e-3)
    m = need(tp, r"t\(TSD_retry\)\s+Retry delay in TSD\s+MODE = GND\s+(\d+)\s+(\d+)\s+(\d+)\s+ms", "t(TSD_retry)")
    L["tretry"] = (f(m, 1) * 1e-3, f(m, 3) * 1e-3)
    m = need(tp, r"Soft short response\s+I\(FASTTRIP\) < I\(OUT\) < I\(SCP\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+µs", "the soft-short response")
    L["tsoft"] = f(m, 3) * 1e-6
    L["iscp"] = f(need(tp, r"I\(SCP\)\s+Short Circuit Protect current\s+(\d+)\s+A", "I(SCP)"))
    L["thot"] = f(need(tp, r"Hot-short response time\s+I\(OUT\) > I\(SCP\)\s+(\d+)\s+µs", "the hot-short response")) * 1e-6
    L["iq"] = f(need(tp, r"Enabled: V\(SHDN\) = 2V\s+([\d.]+)\s+([\d.]+)\s+mA", "IQ(ON)"), 2) * 1e-3
    m = need(tp, r"T\(J_REG\)\s+Thermal regulation set point\s+(\d+)\s+(\d+)\s+(\d+)", "T(J_REG)")
    L["tjreg"] = (f(m, 1), f(m, 3))
    need(tp, r"tdVdT = 20\.8 × 103 × V IN × C dVdT", "Equation 2")
    need(tp, r"auto-retries after a\s.*?delay of t\(TSD_retry\)", "Table 8-1, MODE to GND", re.S)
    need(tp, r"UL 2367 recognized", "UL 2367")
    L["ilim_typ"] = 18.0 / F16_RILIM_K
    rel = max(r9[2] / r9[1] - 1, r30[2] / r30[1] - 1, 1 - r9[0] / r9[1], 1 - r30[0] / r30[1])
    L["ilim_rel"] = rel
    L["ilim"] = (L["ilim_typ"] * (1 - rel) / (1 + F16_RILIM_TOL), L["ilim_typ"] * (1 + rel) / (1 - F16_RILIM_TOL))
    sp = importlib.util.spec_from_file_location("dock_contacts_pinned16", read("dock_py"))
    dc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(dc)
    L["c813"] = dc.PD_MAX
    L["r813"] = dc.R_813_PATH * 1e-3
    L["rise_lim"] = dc.rise_813(L["ilim"][1])
    L["t_lim"] = {k: a + L["rise_lim"] for k, a in dc.AIR.items()}
    L["duty"] = L["tcl"][1] / (L["tcl"][1] + L["tretry"][0])
    vt, it = F16_OVL[1], F16_OVL[0]
    L["ovl_r"] = vt / it
    L["ovl_p"] = (vt - L["ilim"][1] * L["ovl_r"]) * L["ilim"][1]
    L["c_e"] = 10e-6                                  # C31 10 uF 25 V 1210 (gen_sch_e.py; the only capacitor on VSYS_E)
    L["t_ramp"] = (20.8e3 * K["vsys_sup"] * F16_CDVDT * (1 - F16_CDVDT_TOL), 20.8e3 * H["vsys_top"] * F16_CDVDT * (1 + F16_CDVDT_TOL))
    L["i_inrush"] = L["c_e"] / (20.8e3 * F16_CDVDT * (1 - F16_CDVDT_TOL))
    # the 2 A MINI 58 V fuse (0997, held) and the PTC MF-MSMF150/24X (Bourns, held) on their printed rows
    fz = flat(text_pdf("fuse997"))
    m = need(fz, r"0997002_ 2 0\.5 (\d+) ([\d.]+) ([\d.]+)", "the 0997 2 A row")
    L["fuse_r"], L["fuse_i2t"] = f(m, 2) * 1e-3, f(m, 3)
    m = need(fz, r"110 360 000 / - 135 ([\d.]+) / (\d+) 200 ([\d.]+) / (\d+) 350 ([\d.]+) / ([\d.]+)", "the 0997 time-current rows")
    L["fuse_tc"] = dict(t135=f(m, 2), t200=f(m, 4), t350=f(m, 6))
    m = need(fz, r"2A 2\.0 2\.0 2\.0 1\.9 1\.7 (1\.6) (1\.4) 1\.3", "the 0997 2 A derating row")
    L["fuse_der"] = (f(m, 1), f(m, 2))
    pt = flat(text_pdf("msmf"))
    m = need(pt, r"MF-MSMF150/24X (\d+) (\d+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)", "MF-MSMF150/24X's row")
    L["ptc"] = dict(vmax=f(m, 1), imax=f(m, 2), ihold=f(m, 3), itrip=f(m, 4), r1max=f(m, 6))
    m = need(pt, r"MF-MSMF150/24X ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) MF", "MF-MSMF150/24X's derating")
    L["ptc_h"] = {-40: f(m, 1), 70: f(m, 8)}
    L["ptc_trip_cold"] = L["ptc"]["itrip"] * L["ptc_h"][-40] / L["ptc"]["ihold"]
    # the feed's drop at the supplement floor: the eFuse, the 813 path at w3de's 2:1 spread, and the ground return's shift
    i_g = K["ret"][3][2]
    L["drop"] = K["aux_a"] * (L["ron"][2] + L["r813"] * F16_SPREAD) + i_g * L["r813"]
    L["vsys_e_min"] = K["vsys_sup"] - L["drop"]
    L["vsys_e_start"] = H["floor"] - L["drop"]
    return L


def text_pdf(key):
    return "\n".join(pdf_pages(key, True))


def render_fix16(R, p):
    K, H, Q0, L = R["K"], R["H"], R["H"]["Q"], R["L"]
    sel, pl, pa = K["sel"], R["L"]["plan"], R["L"]["plan_alt"]
    air = K["air"]["route"]
    p("16. THE FIX ROUND FOR THE REVIEW OF THE PROVISIONAL FIXES (L4-F02 and L4-F03; a qualification gap, not a demonstrated failure)")
    p("   16a. L4-F02 OBJECTION 1: RDS(on) AT BATDRV'S LEAST DRIVE (BATDRV %s / %s / %s V, SLUSE65A p.17; the source on VSYS, so VGS is minus that)"
      % (fmt(H["drv"][0], 1), fmt(H["drv"][1], 0), fmt(H["drv"][2], 1)))
    p("     printed by the BUK6Y10-30P (17 April 2020, Table 7, p.6): at most %s mOhm at -10 V and 25 C, %s mOhm at -10 V and 175 C, %s mOhm at -4.5 V"
      % (fmt(L["r10_25"] * 1e3, 0), fmt(L["r10_hot"] * 1e3, 0), fmt(L["r45_25"] * 1e3, 0)))
    p("       and 25 C; no maximum at a gate drive under 10 V above 25 C, so no printed point bounds the operating point (-8.5 V, hot) (MAKER)")
    p("     the %s mOhm of 15c is WITHDRAWN AS A BOUND: it is kept as the ALLOWANCE each FET is sized to (SESSION), and E11-36 confirms it on"
      % fmt(L["ra"] * 1e3, 3))
    p("       parts (RDS(on) at -8.5 V and 150 C, at most %s mOhm) or reverses it; at the sheet's largest printed maximum, %s mOhm, every figure below"
      % (fmt(L["ra"] * 1e3, 3), fmt(F16_RA_ALT * 1e3, 0)))
    p("       scales by %s (printed beside it); parts at %s mOhm on a board built to the allowance would take 20 A held to %s C and the service to"
      % (fmt(F16_RA_ALT / L["ra"], 4), fmt(F16_RA_ALT * 1e3, 0), fmt(L["plan_miss"]["tj20"], 1)))
    p("       %s C, so E11-36 gates E11-29 (SESSION, CONDITIONAL)" % fmt(L["plan_miss"]["tj18"], 1))
    p("     searched: SQJ403EP (held), AONS21357 (held), SQJ407EP (Vishay 62806 Rev. B, filed held) and PXP9R1-30QL (Nexperia, 5 January 2021, filed")
    p("       held) print their hot maxima at -10 V only; no part read prints one at |VGS| of 8.5 V or less above 25 C (MAKER)")
    p("     STATUS: CONDITIONAL on E11-36 (the measurement, or Nexperia's maximum at the point, filed) (SESSION)")
    p("   16b. L4-F02 OBJECTION 2: THE DEVICE'S OWN TRANSIENT IMPEDANCE AND THE TWO FETS' COUPLING")
    p("     Fig. 4 (p.5), the duty-cycle 0.01 curve (above any single pulse), read on the rendered page (inputs/%s): its plateau %s K/W, scaled by"
      % (F16_READ, fmt(L["plateau"], 4)))
    p("       %s to Table 6's maximum Rth(j-mb) %s K/W: Zth(j-mb) %s K/W at 244 us, %s at 20 ms, %s at 1 s, %s at 60 s (MAKER, read; INFERRED scale)"
      % (fmt(L["zscale"], 4), fmt(L["rthmb"], 1), fmt(L["z"][2.44e-4], 4), fmt(L["z"][0.02], 4), fmt(L["z"][1.0], 4), fmt(L["z"][60.0], 4)))
    p("     AOS's Figure 14 shape is no longer used for these FETs. The installed path is stated as what a bench reads: each FET's self impedance")
    p("       Zself(t) (heat one, read its own junction) and the mutual Zmut(t) (heat one, read the other); then for any split of the pair's current")
    p("       TJ <= air + Pb x (Zself + Zmut)(t), Pb the even split's per-FET power at the allowance (it bounds each FET's power, 15c); Zself includes")
    p("       the device's own Zth(j-mb); the coupling is in the sum, not assumed away (INFERRED)")
    p("     the plan at the +%s C mixed air (SESSION): 20 A held under OCD1 reaches %s C at most (10 K under the 150 C limit kept for the pulses), so"
      % (fmt(air, 0), fmt(F16_TJ_HELD, 0)))
    p("       the installed (Zself + Zmut) at steady state at most %s K/W (%s at %s mOhm); per-FET power %s W at 10 A, %s W at 18 A, %s W at 20 A (INFERRED)"
      % (fmt(pl["zsum"], 2), fmt(pa["zsum"], 2), fmt(F16_RA_ALT * 1e3, 0), fmt(pl["pb10"], 4), fmt(pl["pb18"], 4), fmt(pl["pb20"], 4)))
    p("     THE SERVICE, 18 A FOR 60 S FROM THE HOT STATE (10 A held at the +%s C air, no board capacity credited, so 60 s counts as steady): TJ %s C,"
      % (fmt(air, 0), fmt(pl["tj18"], 1)))
    p("       from %s C at 10 A held, %s K under the limit; the 18 A for 60 s is kept and no protection is lowered (INFERRED, CONDITIONAL on E11-29, E11-36)"
      % (fmt(pl["pre10"], 1), fmt(150.0 - pl["tj18"], 1)))
    p("     the fault histories from the held 20 A (each a step from the %s C ceiling to the 150 C limit): the allowance on the installed sum at the" % fmt(F16_TJ_HELD, 0))
    p("       event's width, against the device's own Zth(j-mb) at that width (INFERRED):")
    for (lab, i_, t_, pb, allow, zd, room), alt in zip(pl["ev"], pa["ev"]):
        p("       %s: per FET %s W; (Zself + Zmut) at %s s at most %s K/W (%s at %s mOhm), the device alone %s K/W, so %s K/W for the board and the coupling"
          % (lab, fmt(pb, 3), fmt(t_, 6), fmt(allow, 3), fmt(alt[4], 3), fmt(F16_RA_ALT * 1e3, 0), fmt(zd, 4), fmt(room, 3)))
    p("     the LDO-mode precharge, one FET linear with %s A: under the plan's steady sum it stays at 150 C down to SRN %s V, so R-b' (no charge under"
      % (fmt(K["i_pre"], 5), fmt(L["ldo_floor16"], 3)))
    p("       %s V) keeps its margin (INFERRED)" % fmt(K["rb_floor"], 1))
    p("     STATUS: the analysis basis is the device's own and the coupling explicit; the qualification is CONDITIONAL on E11-29's measured Zself and")
    p("       Zmut at the five widths (SESSION)")
    p("   16c. L4-F02 OBJECTION 3: Ciss AGAINST TI'S 5 nF (SLUSE65A p.%d), FROM PRINTED DATA" % L["ciss_p"])
    p("     the BUK6Y10-30P prints Ciss as a typical only: %s nF at -15 V (Table 7), no maximum, no spread; Fig. 12 (typical) reads about %s nF at -0.1 V,"
      % (fmt(L["ciss_t"] * 1e9, 2), fmt(L["ciss_0"] * 1e9, 2)))
    p("       the battery FET's working point (on, or an ideal diode at 30 mV): the pair %s nF at -15 V and about %s nF near 0 V (MAKER, read)"
      % (fmt(2 * L["ciss_t"] * 1e9, 2), fmt(2 * L["ciss_0"] * 1e9, 2)))
    p("     TI states the drive, not the requirement behind 5 nF: RBATDRV_ON at most %s kOhm, RBATDRV_OFF at most %s kOhm; into the pair's typical"
      % (fmt(H["rdrv"][1] / 1e3, 0), fmt(L["roff"][1] / 1e3, 1)))
    p("       Ciss the turn-on time constant is %s us at -15 V and %s us near 0 V, the turn-off %s us; no printed limit to compare them with (MAKER, INFERRED)"
      % (fmt(L["tau_on"][0] * 1e6, 2), fmt(L["tau_on"][1] * 1e6, 2), fmt(L["tau_off"] * 1e6, 2)))
    p("     so the pair's 4.72 nF meets TI's figure only at the maker's test point and as a typical; near 0 V the typical curve is over it: NOT SHOWN")
    p("       on printed data (MAKER, INFERRED)")
    p("     the three approaches (at most three): (S1) the pair, kept: Ciss open (E11-37); (S2) one BUK6Y10-30P, Ciss about %s nF near 0 V (%s %% of 5 nF,"
      % (fmt(L["ciss_0"] * 1e9, 2), fmt(100 * L["ciss_0"] / H["bf_ciss"], 0)))
    p("       typical), but its installed junction-to-air at most %s K/W for 20 A held at the allowance, a path through the case rather than a board"
      % fmt(L["one_rja"], 2))
    p("       pour, with the docking pulse unchanged; (S3) a part whose sheet prints both: none found among the parts read (16a) (INFERRED)")
    p("     STATUS: OPEN; the pair stays selected (SESSION, it is the only arrangement whose heat a board can carry); E11-37: TI's statement of what")
    p("       5 nF bounds (Q-TI-17, drafted, not sent) or the bench's BATDRV behaviour with the pair, and an engineer's decision on (S1) or (S2) (SESSION)")
    p("   16d. L4-F02 OBJECTION 4: THE DOCKING PULSE (15c's reading of ISM's 320 A for 10 us as an I2t of 1.024 A2s is WITHDRAWN)")
    p("     the waveform: %s A peak, time constant %s us (the dependency round's pack loop, the discharge FET at once); it is over the continuous IS"
      % (fmt(Q0["i_dock"], 1), fmt(Q0["tau"] * 1e6, 1)))
    p("       %s A (Tmb 25 C) for %s us and still %s A when ISM's 10 us ends (MAKER, INFERRED)" % (fmt(L["is_dc"], 0), fmt(L["t_over_is"] * 1e6, 1), fmt(L["i_at_tp"], 1)))
    p("     no sharing is credited: the whole pulse in one FET (the sheet prints VSD's maximum, no minimum, so the split is not bounded) (SESSION)")
    p("     its junction from the +%s C air: P = VF x i with VF at most max(%s V, %s V x i / %s A), the printed 25 C maximum carried up by VF's"
      % (fmt(air, 0), fmt(L["vsd_max"], 1), fmt(L["vsd_max"], 1), fmt(L["vsd_is"], 0)))
    p("       concavity (%s V at the peak); superposed on Fig. 4 (scaled), the board below not added: a rise of %s K, TJ %s C, %s mJ, %s W at the peak (INFERRED)"
      % (fmt(L["vf_pk_bound"], 3), fmt(L["dock_k1"][0], 2), fmt(air + L["dock_k1"][0], 1), fmt(L["dock_k1"][1] * 1e3, 2), fmt(L["dock_k1"][2], 0)))
    p("       the largest rise comes at %s us: Fig. 4 is held at its first read point (12 us, %s K/W, %s %% of its steady value) below that width,"
      % (fmt(L["dock_k1"][3] * 1e6, 1), fmt(L["zf"](1.2e-5), 4), fmt(100 * L["zf"](1.2e-5) / L["rthmb"], 1)))
    p("       a bound and not a waveform; within 12 us the heat is still inside the package, so the board below cannot add to it (INFERRED)")
    p("     between ISM's 10 us and the continuous IS the sheet prints no rating but the junction limit, so the waveform past 10 us is judged on")
    p("       TJ alone, at 25 C as hot (INFERRED)")
    p("     what the sheet does not print: VF above %s A or at a hot junction (TJ stays under 150 C while VF is at most %s times that bound), and ISM"
      % (fmt(L["vsd_is"], 0), fmt(L["k_max"], 3)))
    p("       at a mounting base over 25 C (the pulse's %s A peak is %s %% of 320 A at 25 C) (MAKER, INFERRED)" % (fmt(Q0["i_dock"], 1), fmt(100 * Q0["i_dock"] / sel["rdef"]["ism"], 1)))
    p("     STATUS: CONDITIONAL on E11-30 (VF at the docking current from +70 C and ISM's amplitude at a hot mounting base, from Nexperia or the")
    p("       bench); the constraint that would remove both, a slower discharge-FET turn-on on board P, interacts with the pack's ASCD turn-off and")
    p("       belongs to board P's owner (E11-30) (SESSION)")
    p("   16e. L4-F03: THE DOCK'S VSYS CONTACT, ITS BRANCH PROTECTION")
    p("     the branch: VSYS (VBAT) on board A to J_DOCK pin 1, one Preci-Dip 813 (%s A operating maximum; 85 C with its music-wire spring), 24 AWG"
      % fmt(L["c813"], 1))
    p("       and board E's copper to VSYS_E; 1.0 A declared; the review's counterexample %s A from %s V (%s Ohm) is over the contact and under every"
      % (fmt(F16_OVL[0], 0), fmt(F16_OVL[1], 1), fmt(L["ovl_r"], 2)))
    p("       upstream threshold, in source-only and battery operation alike (RECORD, INFERRED)")
    p("     (F) a fuse, Littelfuse 0997 MINI 2 A 58 V (held, rev. 11/18/2025): %s mOhm cold, I2t %s A2s; 110 %% never opens (360000 s minimum), 135 %%"
      % (fmt(L["fuse_r"] * 1e3, 2), fmt(L["fuse_i2t"], 1)))
    p("       within %s s, 200 %% within %s s, 350 %% within %s s; load allowed %s A at 60 C and %s A at 80 C: from 3.5 A (175 %%) to 4 A it may carry for up to"
      % (fmt(L["fuse_tc"]["t135"], 0), fmt(L["fuse_tc"]["t200"], 0), fmt(L["fuse_tc"]["t350"], 1), fmt(L["fuse_der"][0], 1), fmt(L["fuse_der"][1], 1)))
    p("       %s s (the 135 %% row's maximum) over the contact's 3.5 A, and under 2.7 A it need never open: it does not protect the contact (MAKER, INFERRED)"
      % fmt(L["fuse_tc"]["t135"], 0))
    p("     (P) a PTC, Bourns MF-MSMF150/24X (held): Vmax %s V, Imax %s A, hold %s A and trip %s A at 23 C; hold %s A at 70 C, under the 1.0 A load;"
      % (fmt(L["ptc"]["vmax"], 0), fmt(L["ptc"]["imax"], 0), fmt(L["ptc"]["ihold"], 2), fmt(L["ptc"]["itrip"], 2), fmt(L["ptc_h"][70], 2)))
    p("       hold %s A at -40 C, so trip about %s A there, over 3.5 A; and its %s A interrupt is under the pack's prospective current (MAKER, INFERRED)"
      % (fmt(L["ptc_h"][-40], 2), fmt(L["ptc_trip_cold"], 2), fmt(L["ptc"]["imax"], 0)))
    p("     (E) an eFuse, TI TPS16630 (SLVSET9G, held; 60 V, 31 mOhm, UL 2367 recognized): I(OL) = 18 / R(ILIM) (Equation 6, p.20); with R(ILIM)")
    p("       %s kOhm %s %%, %s A typical and, at the wider of the printed rows' spreads (9 and 30 kOhm, +-%s %% over TJ -40 to 125 C), %s to %s A"
      % (fmt(F16_RILIM_K, 1), fmt(F16_RILIM_TOL * 100, 1), fmt(L["ilim_typ"], 4), fmt(L["ilim_rel"] * 100, 1), fmt(L["ilim"][0], 4), fmt(L["ilim"][1], 4)))
    p("       (MAKER, INFERRED between rows); RON at most %s mOhm over TJ; current limiting for at most %s ms, then auto-retry after %s to %s ms (MODE"
      % (fmt(L["ron"][2] * 1e3, 0), fmt(L["tcl"][1] * 1e3, 0), fmt(L["tretry"][0] * 1e3, 0), fmt(L["tretry"][1] * 1e3, 0)))
    p("       to GND, Table 8-1); thermal regulation %s to %s C; a soft short off within %s us, a hot short (over %s A typical) in %s us typical (MAKER)"
      % (fmt(L["tjreg"][0], 0), fmt(L["tjreg"][1], 0), fmt(L["tsoft"] * 1e6, 1), fmt(L["iscp"], 0), fmt(L["thot"] * 1e6, 0)))
    p("     SELECTED (SESSION): (E) on board A between VBAT and J_DOCK pin 1 (a new net VSYS_DOCK; drafted in apply_gen_sch_a_charger.py); in a")
    p("       sustained overload the contact, the 24 AWG and the copper downstream see at most %s A (%s %% of 3.5 A); by w3de's assumed I2 rise, %s C at the 51 C air and %s C at the"
      % (fmt(L["ilim"][1], 3), fmt(100 * L["ilim"][1] / L["c813"], 1), fmt(L["t_lim"]["envelope 51 C"], 1), fmt(L["t_lim"]["margin 65 C"], 1)))
    p("       65 C margin, under the spring's 85 C; the load's 1.0 A is %s %% of the least limit (INFERRED, ASSUMPTION w3de)" % fmt(100 * 1.0 / L["ilim"][0], 1))
    p("     the cases, source-only and battery alike (the eFuse limits whatever feeds VSYS): overload (the 2.88 Ohm counterexample) held at %s A at most,"
      % fmt(L["ilim"][1], 3))
    p("       %s W in the eFuse until its timer, then off for at least %s ms: a duty of at most %s; a short, applied while on or present at the"
      % (fmt(L["ovl_p"], 1), fmt(L["tretry"][0] * 1e3, 0), fmt(L["duty"], 3)))
    p("       start, and the retry: section 17a (the first version's soft-short figure, built on the typical 45 A, is WITHDRAWN);")
    p("       inrush with C(dVdT) %s nF +-%s %%: %s to %s ms ramps (Equation 2), %s mA into C31's %s uF; recovery: auto-retry, board A reads"
      % (fmt(F16_CDVDT * 1e9, 0), fmt(F16_CDVDT_TOL * 100, 0), fmt(L["t_ramp"][0] * 1e3, 2), fmt(L["t_ramp"][1] * 1e3, 2), fmt(L["i_inrush"] * 1e3, 1), fmt(L["c_e"] * 1e6, 0)))
    p("       HOT-R1 lost meanwhile; the eFuse draws at most %s mA from VSYS: on the source while one carries the kit, on the pack otherwise, an"
      % fmt(L["iq"] * 1e3, 1))
    p("       addition to the always-on load, never to the held pack's drain (MAKER, INFERRED)")
    p("     the drop at the supplement floor %s V with 1.0 A: the eFuse %s mOhm, the 813 path %s mOhm at w3de's 2:1 spread, and the return's shift"
      % (fmt(K["vsys_sup"], 3), fmt(L["ron"][2] * 1e3, 0), fmt(L["r813"] * F16_SPREAD * 1e3, 1)))
    p("       (%s A on an 813 ground contact with one open): %s V, so VSYS_E at least %s V (%s V at VSYS_MIN's start); the AP63205 takes %s V and up;"
      % (fmt(K["ret"][3][2], 3), fmt(L["drop"], 4), fmt(L["vsys_e_min"], 3), fmt(L["vsys_e_start"], 3), fmt(K["ap_vin"][0], 1)))
    p("       the fans' least operating voltage is owed with their maximum (E11-35) (INFERRED, ASSUMPTION w3de)")
    p("     the held-pack drain (15a corrected): %s mA is the QUANTIFIED SUBSET (the monitor and D3 at 25 C); D3's hot leakage and the body diodes'"
      % fmt(K["held_bounded_a"] * 1e3, 4))
    p("       current are not bounded on held evidence; the bench acceptance stays at most %s mA (E11-31) (SESSION, CONDITIONAL)" % fmt(FIX_HELD_ACC * 1e3, 1))
    p("     check_contracts.py, the interface draft's second target, is in this tree (v2/ecad/tools/check_contracts.py) and the alias edit applies")
    p("       to it; the alias is now VSYS_DOCK and VSYS_E (RECORD)")
    p("     STATUS: sustained-overload remedy drafted; fault qualification open (section 17a, E11-38) (SESSION)")
    p("")

# ============================================================================================ the second review (L4-CP01 to L4-CP03) and the specimens
F17_L_IN = 20e-9        # H, SESSION (a layout requirement): U42's IN within 20 nH of C236 and C23 to C25
F17_FAN_RUN = 0.1       # A, each fan running (CELL_F's declaration, now VSYS_E's)
F17_DOCK_MARGIN = 1.1   # SESSION: the pulse qualification's margin on the docking waveform's peak and time constant
F17_DOCK_N = (2000, 6, 10.0)   # SESSION: pulses per part (a lifetime allowance of 1000 docking events, twice), parts, seconds apart
F17_TMB = 75.0          # C, SESSION: the qualification's mounting base, 5 K over the +70 C mixed air


def fix17_round(R, T):
    """The second external review (of the 22:30 checkpoint): L4-CP01 (U42's fault envelope: TI's 45 A is typical, a limiter's steady
    setting is no instantaneous ceiling, and the start into a short times out at 1.5 s, not 202 ms), L4-CP02 (a junction temperature
    does not extend a printed pulse rating: the whole hot docking waveform needs an applicable basis) and L4-CP03 (the charger draft's
    text); and the specimens for the measurement rows."""
    H, K, L, G = R["H"], R["K"], R["L"], R["G"]
    M = {}
    tp = "\n".join(pdf_pages("tps1663", True))
    m = need(tp, r"Hot-short response time\s+I\(OUT\) > I\(SCP\)\s+(\d+)\s+µs", "the hot-short response")
    M["hot_typ_only"] = True
    need(tp, r"I\(FASTRIP\)\s+Fast-trip comparator threshold\s+2xI\(OL\)\s+A", "I(FASTTRIP), a typical only")
    need(tp, r"I\(SCP\)\s+Short Circuit Protect current\s+45\s+A", "I(SCP), a typical only")
    m = need(tp, r"t\(Treg_timeout\)\s+Thermal Regulation Timeout\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+s", "t(Treg_timeout)")
    M["treg"] = (f(m, 1), f(m, 3))
    need(tp, r"When the device is started with short-circuit on the output, the current begins to limit at I\(OL\)\.", "8.3.4.2.1")
    need(tp, r"The fast-trip circuit holds the internal FET off for only a few microseconds, after which the device\s+turns back on slowly, allowing the current-limit loop to regulate the output current to I\(OL\)\.", "8.3.4.2")
    need(tp, r"Using a Schottky diode across the output and GND to absorb negative spikes", "9.4.1")
    need(tp, r"IN, P_IN, OUT\s+0\.1\s+µF", "the 0.1 uF minimum at IN, P_IN and OUT")
    m = need(tp, r"IN, P_IN, OUT, UVLO, FLT, PGOOD\s+\u20130\.3\s+(\d+)", "the absolute maximum at IN and OUT")
    M["abs_in"] = f(m)
    # case 2, a short applied while on: the resistive bound (no inductance credited, the contact's own resistance taken as 0)
    sp = importlib.util.spec_from_file_location("dock_contacts_pinned17", read("dock_py"))
    dc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(dc)
    M["r_path_min"] = (dc.R_813_PATH - dc.PD_R) * 1e-3
    M["i_pk"] = H["vsys_top"] / (L["ron"][0] + M["r_path_min"])
    M["i2t_pk"] = M["i_pk"] ** 2 * L["tsoft"]
    M["fast_typ"] = 2.0 * L["ilim"][1]
    # the input spike (TI's Equation 14) at the bound, with C236's stacked effective capacitance and printed ESR next to U42
    M["c_in"], M["esr_in"] = G["c_dir_eff"], G["esr181"]
    M["v_in_pk"] = H["vsys_top"] + M["i_pk"] * (math.sqrt(F17_L_IN / M["c_in"]) + M["esr_in"])
    # case 3, a start into a short, and case 4, the retry: the duty and the contact's average heating
    M["duty_start"] = M["treg"][1] / (M["treg"][1] + L["tretry"][0])
    M["duty_ovl"] = L["duty"]
    M["rise_retry"] = dc.rise_813(L["ilim"][1]) * max(M["duty_start"], M["duty_ovl"])
    M["rise_steady"] = dc.rise_813(L["ilim"][1])
    # the fans' start against U42's least limit and VSYS_E's floor at that current
    i_u12 = K["aux"]["U12"]
    M["fan_simul"] = (L["ilim"][0] - i_u12) / 2.0
    M["fan_stag"] = L["ilim"][0] - i_u12 - F17_FAN_RUN
    i_g = K["ret"][3][2]
    M["vsys_e_lim"] = K["vsys_sup"] - (L["ilim"][0] * (L["ron"][2] + L["r813"] * F16_SPREAD) + i_g * L["r813"])
    # CP02: the docking waveform's qualification envelope
    Q0 = H["Q"]
    M["dock_q"] = (Q0["i_dock"] * F17_DOCK_MARGIN, Q0["tau"] * F17_DOCK_MARGIN)
    M["dock_q_t80"] = M["dock_q"][1] * math.log(M["dock_q"][0] / L["is_dc"])
    # CP03: the claims the charger draft must no longer write
    M["withdrawn"] = ("bounded at 21.1", "34.4 C/W", "split between their body diodes")
    return M


def render_fix17(R, p):
    K, H, L, M = R["K"], R["H"], R["L"], R["M"]
    Q0 = H["Q"]
    p("17. THE SECOND REVIEW (L4-CP01 TO L4-CP03, of the 22:30 checkpoint) AND THE EVIDENCE SPECIMENS")
    p("   17a. L4-CP01: U42'S FAULT ENVELOPE BY CASE (G = printed limit, I = inferred, T = typical only; SLVSET9G pp.8 to 10, 21, 22, 26, 30, 31)")
    p("     the setting: I(OL) %s to %s A at R(ILIM) %s kOhm (I: between the printed 9 and 30 kOhm rows, each G over TJ -40 to 125 C at VIN - VOUT"
      % (fmt(L["ilim"][0], 4), fmt(L["ilim"][1], 4), fmt(F16_RILIM_K, 1)))
    p("       1 V); a regulated, steady setting, NOT an instantaneous ceiling; the fast-trip threshold 2 x I(OL) and I(SCP) 45 A are T only (MAKER)")
    p("     (1) operating overload, I(OL) < I < I(FASTTRIP): held at the setting once the loop settles (the settling's peak is not printed); limiting for")
    p("       at most %s ms (G), then off %s to %s ms (G) and a retry; a duty of at most %s; the contact at most %s A steady, %s K by w3de's rise (I)"
      % (fmt(L["tcl"][1] * 1e3, 0), fmt(L["tretry"][0] * 1e3, 0), fmt(L["tretry"][1] * 1e3, 0), fmt(M["duty_ovl"], 3), fmt(L["ilim"][1], 3), fmt(M["rise_steady"], 2)))
    p("     (2) a short applied while on: the current rises from VSYS's local capacitance (C236 and C23 to C25, the source's impedance behind them)")
    p("       until the fast trip; turn-off %s to %s us under I(SCP) (G, from a threshold that is T), about 1 us over it (T); then the device turns back"
      % (fmt(2.2, 1), fmt(L["tsoft"] * 1e6, 1)))
    p("       on slowly into case (1) (p.21). Bound (I): at most %s A, VSYS's %s V over RON's printed least %s mOhm and the path's %s mOhm with the"
      % (fmt(M["i_pk"], 1), fmt(H["vsys_top"], 3), fmt(L["ron"][0] * 1e3, 0), fmt(M["r_path_min"] * 1e3, 1)))
    p("       contact at 0 and no inductance credited, for at most %s us: %s A2s (I, resting on the %s us row holding above I(SCP)); the 813 prints no"
      % (fmt(L["tsoft"] * 1e6, 1), fmt(M["i2t_pk"], 3), fmt(L["tsoft"] * 1e6, 1)))
    p("       pulse rating, so the contact, the 24 AWG and the clamp are left to the bench's qualification (E11-38), not bounded (MAKER, INFERRED)")
    p("     the pins: IN at most %s V by TI's Equation 14 at that bound with U42 within %s nH of C236 (%s uF effective, ESR %s mOhm printed) against"
      % (fmt(M["v_in_pk"], 1), fmt(F17_L_IN * 1e9, 0), fmt(M["c_in"] * 1e6, 1), fmt(M["esr_in"] * 1e3, 0)))
    p("       the absolute %s V (I; the 20 nH a layout requirement, SESSION); OUT's negative spike through the output loop's inductance clamped by a"
      % fmt(M["abs_in"], 0))
    p("       Schottky D23 at OUT (TI 9.4.1, 9.5.1); OUT's -0.3 V absolute minimum is not shown under a clamp at hundreds of amperes: left to the bench (E11-38,")
    p("       Q-TI-18) (MAKER, INFERRED)")
    p("     (3) a start into a pre-existing short: limited at I(OL) from the start, then thermal regulation at %s to %s C for %s to %s s (G), then off"
      % (fmt(L["tjreg"][0], 0), fmt(L["tjreg"][1], 0), fmt(M["treg"][0], 2), fmt(M["treg"][1], 1)))
    p("       (p.22); the setting's row is printed at VIN - VOUT 1 V, not at the %s V a short puts across U42: the current at that bias is left to the bench"
      % fmt(H["vsys_top"], 1))
    p("       (E11-38) (MAKER, INFERRED)")
    p("     (4) repeated retry into a persistent short: each cycle is case (3) for at most %s s and off at least %s ms (G): a duty of at most %s; the"
      % (fmt(M["treg"][1], 1), fmt(L["tretry"][0] * 1e3, 0), fmt(M["duty_start"], 3)))
    p("       contact's average heating at most %s K by w3de's rise, under the steady case's %s K; an intermittent short re-applied faster than the"
      % (fmt(M["rise_retry"], 2), fmt(M["rise_steady"], 2)))
    p("       retry is not bounded by the device's timers: its count is the bench's (E11-38) (INFERRED)")
    p("     the fans' start, against U42's least limit %s A with U12's %s A: both together at most %s A each, one at a time at most %s A (one other"
      % (fmt(L["ilim"][0], 3), fmt(K["aux"]["U12"], 1), fmt(M["fan_simul"], 4), fmt(M["fan_stag"], 4)))
    p("       running at %s A); VSYS_E at that current at least %s V at the supplement floor: the fans must start at or under it (E11-35, E11-39) (INFERRED)"
      % (fmt(F17_FAN_RUN, 1), fmt(M["vsys_e_lim"], 3)))
    p("     STATUS: sustained-overload remedy drafted; fault qualification open (E11-38); not evidence of a failure (SESSION)")
    p("   17b. L4-CP02: THE WHOLE HOT DOCKING WAVEFORM (a junction temperature does not extend ISM's printed 10 us at Tmb 25 C)")
    p("     the waveform to accept: %s A peak, time constant %s us, over IS's %s A for %s us, from a +%s C mounting base, once per docking event"
      % (fmt(Q0["i_dock"], 1), fmt(Q0["tau"] * 1e6, 1), fmt(L["is_dc"], 0), fmt(L["t_over_is"] * 1e6, 1), fmt(K["air"]["route"], 0)))
    p("     (D1) Nexperia's written acceptance of that waveform (Q-NXP-1, drafted, not sent): no circuit change; outside this project's control")
    p("     (D2) a defined pulse qualification on parts: %s A peak and %s us (x%s), mounting base %s C, %d pulses %s s apart on each of %d parts"
      % (fmt(M["dock_q"][0], 1), fmt(M["dock_q"][1] * 1e6, 1), fmt(F17_DOCK_MARGIN, 1), fmt(F17_TMB, 0), F17_DOCK_N[0], fmt(F17_DOCK_N[2], 0), F17_DOCK_N[1]))
    p("       (over IS for %s us); no circuit change; within its stated scope (a sample, not a production limit) (SESSION)" % fmt(M["dock_q_t80"] * 1e6, 1))
    p("     (D3) board P bounds the inrush (a slower discharge-FET turn-on or a precharge path): changes the pack's protection path, whose ASCD")
    p("       turn-off and normal charging must be re-shown; board P's owner, a draft for board P's generator (INFERRED)")
    p("     SELECTED (SESSION): (D2), with (D1) asked in parallel; (D3) only if (D2) fails, as E11-30 states; STATUS: CONDITIONAL on E11-30 (SESSION)")
    p("   17c. L4-CP03: apply_gen_sch_a_charger.py's text now writes the allowance, the 33.12 K/W self-plus-mutual target and no sharing credited;")
    p("     the three withdrawn statements are absent from the text it writes (tested) (RECORD)")
    p("")

# ============================================================================================ the output
def render(R):
    out = []
    p = out.append
    B, P, E, C, F, D, T9, N = R["B"], R["P"], R["E"], R["C"], R["F"], R["D"], R["T9"], R["N"]
    p("L4-E11: SOURCE-ONLY AND DEAD-PACK OPERATION (U-04), THE VEHICLE-ENTRY INTERCONNECT (D-06) AND THE HOT SWAP'S FAULT TIMER (D-09)")
    p("MESHSAT-1357, 2 October 2026. Prototype design, desk arithmetic: nothing is bought, built, powered or measured. Classes: MAKER,")
    p("CATALOGUE, NETLIST, REQUIREMENT, RECORD, INFERRED, CONDITIONAL, ASSUMPTION, SESSION.")
    p("")
    p("0. INPUTS (sha256/16)")
    for k, rel, s in R["inputs"]:
        p("   %-9s %s  %s" % (k, s[:16], rel))
    for k, rel, s in R["git_inputs"]:
        p("   %-9s %s  %s (L4-E9's commit, read with git show)" % (k, s[:16], rel))
    for name, s in R["filed"]:
        p("   filed     %s  %s/inputs/%s" % (s[:16], REC, name))
    p("   this record's own figures: copper %s ohm mm2/m at 20 C and %s /K, %s J/cm3K (ASSUMPTION, constants); AWG 14 %s mm2, AWG 12 %s mm2,"
      % (CU_RHO_20, CU_ALPHA, CU_CV, AWG14_MM2, AWG12_MM2))
    p("     AWG 18 %s mm2 (ASSUMPTION, constants); the cold end %s C (REQ-024); the SESSION choices are named where they are used" % (AWG18_MM2, fmt(T_COLD)))
    p("")
    p("1. U-04, WHAT THE REQUIREMENTS DEMAND OF SOURCE-ONLY OPERATION (quoted, not reinterpreted)")
    p("   REQ-015 statement: \"%s\" (REQUIREMENT)" % R["req015"][0])
    p("   REQ-015 acceptance: \"%s\" (REQUIREMENT)" % R["req015"][1])
    p("   REQ-014: \"%s\" (REQUIREMENT)" % R["req014_clause"])
    p("   REQ-024: \"%s\" (REQUIREMENT)" % R["req024_clause"])
    p("   TEST-PLAN E4-O (REQ-024's acceptance): \"%s\" (REQUIREMENT)" % R["e4o"])
    p("   REQ-046: \"%s\"; its acceptance: \"%s\" (REQUIREMENT)" % (R["req046"], R["req046_hold"]))
    p("   REQ-077 acceptance: \"%s\" (REQUIREMENT)" % R["req077_clause"])
    p("   REQ-072 (obligation %s): \"%s\" (REQUIREMENT)" % (R["req072_obl"], R["req072_clause"]))
    p("   requirement | obligation | source voltage named | names a load state | the source-only content")
    for rid, ob, v, st, what in R["req_rows"]:
        p("     %-16s | %-9s | %s | %s | %s (REQUIREMENT)" % (rid, ob, v, "yes" if st else "no", what))
    p("   So: no mandatory requirement names a load state (a PS- profile or a wattage) for the kit on a source alone, at any")
    p("     source voltage; REQ-015's \"runs the kit and charges the pack\" names neither the load nor the pack's state, and \"9 V\"")
    p("     is not tied to a measuring point. PS-IDLE-SPEC enters only through REQ-072, an objective. What the mandatory text does")
    p("     demand of a source alone: a start and a warm-up of a cold-soaked pack whose FETs are open (REQ-024, D-02d, REQ-046,")
    p("     E4-O), and the charger carrying the kit with its charge held (REQ-077, a pack present). (INFERRED from the quotes)")
    p("")
    p("2. U-04, THE CHARGER AND THE PACK WITH NO USABLE PACK")
    p("   BQ25731 (SLUSE66A), what the sheet states:")
    p("     no battery MOSFET (p.%d); from VBUS: registers, cell count, then \"Converter powers up.\" with no battery condition (9.3.1, p.%d) (MAKER)" % (B["nobatfet"], B["powerup"]))
    p("     power-up curves drawn \"2-cell without battery\", Figures 10-4 and 10-5 (p.%d) (MAKER)" % B["fig104"])
    p("     \"%s\" (11, p.%d) (MAKER)" % (B["sec11_text"], B["sec11"]))
    p("     CHRG_OK's conditions name VBUS and the faults, not the battery: \"%s\" (9.3.4, p.%d) (MAKER)" % (B["chrgok_text"], B["chrgok"]))
    p("     DPM: the charge falls first, then \"the system voltage starts to drop\" and the battery supplements (9.3.17, p.%d) (MAKER)" % B["dpm"])
    p("     4S defaults: ChargeVoltage %s V, SYSOVP %s V, VSYS_MIN %s V (Table 9-2, p.%d); below VSYS_MIN at SRN the charge is clamped at %s mA, a typical figure with no minimum or maximum printed (8.5, p.%d) (MAKER)"
      % (fmt(B["cv4s"]), fmt(B["sysovp4s"]), fmt(B["vsysmin4s"]), B["t92"], fmt(B["iclamp"] * 1000), B["iclamp_p"]))
    p("     in the BATOVP paragraph: with charge enabled the converter shuts down; \"if charge is disabled the converter should keep operating without disturbance\"")
    p("       (9.3.21.5, p.%d): a statement about a battery over-voltage event, not a specification of VSYS's regulation or transient response with no battery (N1, N2) (MAKER, context kept)" % B["batovp"])
    p("     HIZ: \"converter shuts off\" with ILIM_HIZ under %s V (9.3.8, p.%d) (MAKER)" % (fmt(B["hiz_v"]), B["hiz_p"]))
    p("     VSYS under %s V for 2 ms in steady state: \"shut down and latched off\" until a host write (9.3.21.8, p.%d) (MAKER)" % (fmt(B["uvp_v"]), B["uvp_p"]))
    p("     \"Overall %s-uF effective capacitance on VSYS net is necessary\" (10.1, p.%d); CHRG_INHIBIT \"1b: Inhibit Charge\" (p.%d); the host ends a charge by CHRG_INHIBIT or ChargeCurrent 0 (9.4.1, p.%d) (MAKER)"
      % (fmt(B["csys_uf"]), B["csys_p"], B["inhibit_p"], B["term_p"]))
    p("     AUTO_WAKEUP_EN, 0 at POR: with it set, a battery under VSYS_MIN gets %s mA for %s min with no further host write (p.%d) (MAKER); it needs a host write first, so it does not answer N3"
      % (fmt(B["wake_ma"]), fmt(B["wake_min"]), B["wake_p"]))
    p("     ChargeCurrent at POR: the register description says 0 A, its reset value encodes 256 mA, and TI's expert on E2E thread 1316778 (held) states %s mA,"
      % fmt(R["G"]["por_ma"], 0))
    p("       the description being in error (the dependency round, D4) (MAKER)")
    p("     ChargeCurrent with the 5 mOhm RSR: 128 mA steps; REG0x03/02 = 0x0200 (1024 mA) regulates within -%s %% to +%s %%, a row printed for VBAT above VSYS_MIN (8.5, p.10) (MAKER)"
      % (fmt(N["rb_err"][0] * 100, 0), fmt(N["rb_err"][1] * 100, 1)))
    p("   board A and E as generated: the strap R26 %sk over R27 %sk, %s %% of VDDA, so U3 never sees \"battery removal\"; R17 between VBAT"
      % (fmt(R["strap"][0], 1), fmt(R["strap"][1], 1), fmt(R["strap"][2], 1)))
    p("     (VSYS, every load) and CELL_FUSED (the pack); CHG_INHIBIT pulls ILIM_HIZ low through Q6 (HIZ); SHORE_INHIBIT pulls the hot")
    p("     swap's UVLO low through Q8 (the input off); board P's gauge PCHG pin not connected; R7 1 k from PACK_P to its VCC (NETLIST)")
    p("     FW-C08 as written: \"%s\" (RECORD, HW-FW-CONTRACT)" % R["fwc08"])
    p("     FW-A14 as written: \"%s\" (RECORD); PANEL.md 10: \"%s\" (RECORD)" % (R["fwa14"], R["panel10"]))
    p("   the pack (SLUUAQ3A and this tree's image):")
    p("     a CUV trip sets OperationStatus()[XDSG] only (2.2, p.%d): the discharge FET opens, the charge FET stays (MAKER)" % P["cuv_p"])
    p("     XDSG also on UTD, XCHG on UTC (4.12, p.%d); the image's UTD %s C and UTC %s C (pcb_pack_protection.yaml): below %s C both FETs are open (MAKER, RECORD)"
      % (P["xdsg_p"], fmt(P["utd"]), fmt(P["utc"]), fmt(P["utd"])))
    p("     precharge by the external FET or the CHG FET per PCHG_COMM (4.9, p.%d), default 0 = PCHG FET (14.2.1.1, p.%d); board P has no PCHG FET and"
      % (P["pchg_p"], P["pchgbit_p"]))
    p("     the image writes FET Options 0x3D, PCHG_COMM 1 (PRIMARY-CONFIGURATION.md); Shutdown Voltage %s mV; CUV %s V, recovery %s V; pre-charge %s A (MAKER, RECORD)"
      % (fmt(P["shutdown_mv"]), fmt(P["cuv"], 2), fmt(P["cuv_rec"], 2), fmt(P["pre_a"])))
    p("     Q2's body diode carries the charge while XDSG: VSD at most %s V at %s A, RthetaJA at most %s C/W on 1 in2 2 oz, TJ %s C (CSD17570Q5B p.%d) (MAKER)"
      % (fmt(P["vsd_max"]), fmt(P["vsd_i"]), fmt(P["rja"]), fmt(P["tj_max"]), P["vsd_p"]))
    for i, w, dt in P["q2"]:
        p("       at %s A: at most %s W, %s K over the air (INFERRED: VSD's row at %s A bounds it at less current; board P's copper an ASSUMPTION)"
          % (fmt(i, 3), fmt(w, 3), fmt(dt, 1), fmt(P["vsd_i"])))
    p("       at R-b's %s A (below): at most %s W, %s K, so TJ %s C at the %s C inside air against %s C (CONDITIONAL: on R-b's bound holding, below, and"
      % (fmt(N["rb_max"], 3), fmt(N["q2_w"], 3), fmt(N["q2_rise"], 1), fmt(N["q2_tj"], 1), fmt(F["air_hot"], 1), fmt(P["tj_max"], 0)))
    p("         on board P's installed copper giving TI's %s C/W, which TI states for its own 1 in2 2 oz board; INFERRED)" % fmt(P["rja"]))
    p("     the cell maker: pre-charge between %s and %s V a cell at %s to %s C, C = %s A (Samsung 35E p.%d) (MAKER); the charger's %s mA is %s C a cell,"
      % (fmt(P["pre_win"][0], 1), fmt(P["pre_win"][1], 1), fmt(P["pre_c"][0], 1), fmt(P["pre_c"][1], 1), fmt(P["c_a"], 2), P["cell_p"], fmt(B["iclamp"] * 1000), fmt(P["clamp_c"], 3)))
    p("       under the range (a lower current; the maker states no consequence), and a 3.0 A ChargeCurrent is %s C a cell, inside it (INFERRED)" % fmt(P["cc_c"], 3))
    p("   what follows, by pack state (INFERRED from the rows above, the drawn topology and the image):")
    p("     pack absent, or both FETs open (below %s C, SHUTDOWN, a permanent fail): no current through R17, so the voltage loop holds" % fmt(P["utd"]))
    p("       SRN, and VSYS with it, at ChargeVoltage (at most %s V written, s120); the kit is carried up to the input limit (11, 9.3.17) (INFERRED)" % fmt(R["cv_max"], 3))
    p("     pack at CUV, charge FET on: charge through Q2's diode; VSYS = stack + VSD, %s to %s V; %s mA while SRN is under %s V (CONDITIONAL on A-14's 10.0 V floor)"
      % (fmt(P["vsys_cuv"][0], 2), fmt(P["vsys_cuv"][1], 2), fmt(B["iclamp"] * 1000), fmt(B["vsysmin4s"], 1)))
    p("     a pack self-discharged to the Shutdown Voltage: VSYS %s to %s V while it precharges, under the converters' assumed 10.0 V floor (A-14): the loads wait (CONDITIONAL)"
      % (fmt(P["vsys_shut"][0], 2), fmt(P["vsys_shut"][1], 2)))
    p("     the clamp lifts at SRN %s V, a stack of %s V or more (%s V a cell) with VSD at its maximum, before CUV recovers at %s V a cell: in that window"
      % (fmt(B["vsysmin4s"], 1), fmt(P["release_stack"], 2), fmt(P["window"][0], 3), fmt(P["window"][1], 2)))
    p("       ChargeCurrent crosses Q2's diode, so rule R-b (SESSION) permits exactly two settings while the charger's own SRN reading is under %s V or the"
      % fmt(RULE_SRN_V, 1))
    p("       gauge reports XDSG or PRECHARGE: ChargeCurrent() 0x0000 (no charge) and 0x0200 (1024 mA set); no other value, because TI prints no accuracy")
    p("       for any setting under 0x0200 (MAKER, SESSION). The bounds by case (B5; the row's condition: 5 mOhm RSR, VBAT above VSYS_MIN, %s to %s C):"
      % (fmt(N["rb_temp"][0], 0), fmt(N["rb_temp"][1], 0)))
    p("       (i) SRN at or above VSYS_MIN and the charger inside %s to %s C: %s to %s A actual (-%s / +%s %%, R17 at +-1 %%) (MAKER row, INFERRED: BOUNDED)"
      % (fmt(N["rb_temp"][0], 0), fmt(N["rb_temp"][1], 0), fmt(N["rb_min"], 4), fmt(N["rb_max"], 4), fmt(N["rb_err"][0] * 100, 0), fmt(N["rb_err"][1] * 100, 1)))
    p("       (ii) SRN at or above VSYS_MIN with the charger outside %s to %s C: no accuracy printed: INCONCLUSIVE until the charger's temperature in this"
      % (fmt(N["rb_temp"][0], 0), fmt(N["rb_temp"][1], 0)))
    p("            state is bounded inside the row (it sits in the inside air, -20 C at a cold start to %s C hot, plus its own rise, which no held record gives)," % fmt(F["air_hot"], 1))
    p("            or TI states the accuracy outside it, or the bench measures the current at the inside air's ends (E11-22)")
    p("       (iii) SRN under VSYS_MIN: the clamp, %s mA typical with no maximum printed: INCONCLUSIVE until TI states a maximum or the bench measures it (E11-22)"
      % fmt(B["iclamp"] * 1000))
    p("       without the gauge's report the %s V threshold covers a cell up to %s V under the stack's average (%s V a cell) (INFERRED); R-b also holds above %s V"
      % (fmt(RULE_SRN_V, 1), fmt(P["rb_imbalance"], 2), fmt(P["rb_stack"] / P["cells"], 2), fmt(RULE_SRN_V, 1)))
    p("       while the gauge reports XDSG or PRECHARGE, so in case (i) the charge power is at most %s A x %s V = %s W (at the %s V threshold, %s W) (INFERRED)"
      % (fmt(N["rb_max"], 4), fmt(R["cv_max"], 3), fmt(N["dead_charge_w_max"], 2), fmt(RULE_SRN_V, 1), fmt(N["dead_charge_w"], 2)))
    p("     CHG_INHIBIT (HIZ) or SHORE_INHIBIT asserted while the pack cannot discharge: the converter is off, so VSYS has no source and the")
    p("       kit stops; the controllers die, the pull-downs release the line and the kit restarts: a loop (INFERRED: 9.3.8, the UVLO, the netlists)")
    p("     FW-C08 asserts SHORE_INHIBIT below 0 C: with a pack below %s C the source start REQ-024 requires is cut by the hold itself (finding U4-F1, INFERRED)" % fmt(P["utd"]))
    p("   NOT STATED in any held document (named, not inferred): N1 VSYS's regulation and transient response with no battery under the")
    p("     kit's load steps; N2 what the converter regulates with CHRG_INHIBIT = 1 or ChargeCurrent 0 and no battery current (Q-TI-3);")
    p("     N3 whether the charger charges before any host write (Q-TI-2); N4 VSYS's effective capacitance at %s V against TI's %s uF (RECORD, MAKER);"
      % (fmt(R["cv_max"], 3), fmt(B["csys_uf"])))
    p("     N5 every load converter's minimum input (A-14, R-49); N6 0-V charging before the gauge's SUV check (Q-TI-7)")
    p("   THE PACK'S STATES BY PERMISSION (B2; the gauge's own FETs, SLUUAQ3A 2.2 and 4.12) and how a charge hold is made in each (INFERRED):")
    p("     S1 charge on, discharge on: the pack and the source share the kit; a hold by the CHRG_INHIBIT bit or ChargeCurrent 0 (9.4.1) leaves the converter")
    p("        carrying the kit from the source (11): REQ-077 as written")
    p("     S2 charge on, discharge off (a warm CUV trip, or an OCD, AOLD or SCD latch): the source alone carries the kit and the pack can still take charge")
    p("        through Q2's diode, so the gauge does NOT hold the charge; a hold only by the bit or ChargeCurrent 0; whether VSYS stays regulated with charge")
    p("        inhibited while the pack cannot discharge is N2 (Q-TI-3): OPEN, the bench proves it (E11-06)")
    p("     S3 charge off, discharge on (between UTD %s C and UTC %s C; OTC; COV): the gauge holds the charge; a requested hold by the bit as in S1 (REQ-077)" % (fmt(P["utd"]), fmt(P["utc"])))
    p("     S4 charge off, discharge off (below %s C, SHUTDOWN, a permanent fail, or no pack): the source alone carries the kit and the gauge already holds" % fmt(P["utd"]))
    p("        the charge. THE ONE EXCEPTION: in S4 the bit is NOT set and ChargeCurrent() is not written 0, so N2 never arises where the source alone carries")
    p("        the kit with no charge possible; the hold is the gauge's own")
    p("     THE HOLD PERSISTS ACROSS STATES: it is a flag in the firmware, set and cleared only by its own condition (the cold hold above 3 C with hysteresis,")
    p("        the operator, REQ-077's hold), never by a state change; in S1, S2 and S3 the bit follows the flag; on leaving S4 (a FET closing, a pack fitted)")
    p("        the bit is written from the flag at once, and in the firmware's reaction time only the gauge's window acts, which keeps the cells inside their")
    p("        charge window; after a charger POR ChargeCurrent() is %s mA by TI's E2E answer (D4), so a charge at %s mA can begin before the firmware writes the"
      % (fmt(R["G"]["por_ma"], 0), fmt(R["G"]["por_ma"], 0)))
    p("        flag's bit: in that window too only the gauge's window acts, and %s mA is under R-b's bound (INFERRED)" % fmt(R["G"]["por_ma"], 0))
    p("     in S2 and S4 the CHG_INHIBIT line (HIZ, 9.3.8) and SHORE_INHIBIT each remove the kit's only supply: neither is ever a charge hold (rule R-a)")
    p("")
    p("3. U-04, THE ENTRY AT A 9.00 V PLUG, THE KIT'S OWN LOSSES AND THE SOURCE ENVELOPE (the focused check's B1 and B3)")
    p("   3a. the drawn LM5069 against a 9.00 V plug (finding U4-F2, corrected in the fix round)")
    p("     UVLOTH %s / %s / %s V, UVLOHYS %s / %s / %s uA (SNVS452G p.%d); Equations 38 to 40 (p.24): the falling threshold is UVLOTH x (1 + R20/R21),"
      % (tuple(fmt(x, 2) for x in E["uv_rows"]) + tuple(fmt(x * 1e6, 0) for x in E["hy_rows"]) + (E["uvlo_page"],)))
    p("       the rising one that plus UVLOHYS x R20 (MAKER); the first round put the hysteresis on the falling edge, so its numbers and its R21 draft were wrong")
    for lab, (rise, fall) in (("as drawn (R20 %sk, R21 %sk, 1 %%)" % (fmt(E["r20"] / 1e3, 0), fmt(E["r21"] / 1e3, 1)), N["uvlo_drawn"]), ("the withdrawn first-round draft (R21 42.2k)", N["uvlo_withdrawn"])):
        p("     %s: on at %s / %s / %s V rising, off at %s / %s / %s V falling: NOT MET at 9.00 V (INFERRED)" % ((lab,) + tuple(fmt(x, 2) for x in rise) + tuple(fmt(x, 2) for x in fall)))
    p("     POREN (all functions enabled, VIN increasing) %s typical, %s V maximum; PORIT %s / %s V; POREN's hysteresis %s mV typical; the operating range %s to %s V (SNVS452G p.1, p.5) (MAKER)"
      % (fmt(N["poren"][0], 1), fmt(N["poren"][1], 1), fmt(N["porit"][0], 1), fmt(N["porit"][1], 1), fmt(N["poren_hys"] * 1e3, 0), fmt(N["vin_range"][0], 0), fmt(N["vin_range"][1], 0)))
    p("     U6's VIN (pin 2) is DC_P behind the ideal diode (NETLIST); before the hot swap conducts, VIN is at most 9.00 V less the LM74700's regulated drop")
    p("       (%s / %s / %s mV, SNOSD17G) = %s V, under POREN's %s V maximum: no divider makes a 9.00 V plug start the LM5069 (NOT MET, INFERRED)"
      % (fmt(N["vak"][0] * 1e3, 0), fmt(N["vak"][1] * 1e3, 0), fmt(N["vak"][2] * 1e3, 0), fmt(N["vin_ic_max"], 3), fmt(N["poren"][1], 1)))
    p("     with the in-service current flowing DC_P falls further, to %s V at the 9.00 V plug's maximum (3e), under POREN less its %s mV typical hysteresis (INFERRED)"
      % (fmt(N["dcp9"], 2), fmt(N["poren_hys"] * 1e3, 0)))
    p("     the IC cannot be supplied from elsewhere: VIN is the current-sense reference (VCL is the VIN-SENSE voltage, p.5), so it sits at R19's top (MAKER, NETLIST)")
    p("   3b. what a replacement must do (INFERRED; the figures are 3d to 3e's):")
    p("     (1) operate and enable below its own supply at the in-service maximum from a 9.00 V plug, DC_P %s V hot; (2) act on overcurrent between" % fmt(N["dcp9"], 2))
    p("       the in-service maximum at 9 V (%s A) and F1's %s C column (%s A); (3) keep the pass FET inside its derated chart in every start, a start into a"
      % (fmt(N["i9"], 3), fmt(F["f_col"], 0), fmt(F["f_hot_a"], 1)))
    p("       resistive fault included; (4) lock out over-voltage above CS101's %s V peak and under D10's %s V breakdown at -20 C (L4-E9), with a 100 V rating"
      % (fmt(N["cs101_peak"], 2), fmt(N["d10"][1], 1)))
    p("     TPS1663 (SLVSET9G, held back): %s to %s V, %s V absolute; its highest limit (RILIM 3 k) %s / %s / %s A: under %s A, fails (2) (MAKER)"
      % (fmt(N["t63_range"][0], 1), fmt(N["t63_range"][1], 0), fmt(N["t63_abs"], 0), fmt(N["t63_ilim"][0], 2), fmt(N["t63_ilim"][1], 0), fmt(N["t63_ilim"][2], 2), fmt(N["i9"], 2)))
    p("     TPS4811-Q1 (SLUSEE5E, held back): VS %s to %s V, %s V absolute, VS POR %s / %s / %s V; EN/UVLO %s / %s / %s V rising and %s / %s / %s V falling,"
      % ((fmt(N["t48_vs"][0], 1), fmt(N["t48_vs"][1], 0), fmt(N["t48_abs"], 0)) + tuple(fmt(x, 2) for x in N["t48_por"]) + tuple(fmt(x, 2) for x in N["t48_uvr"]) + tuple(fmt(x, 2) for x in N["t48_uvf"])))
    p("       %s nA leakage at most; OV the same thresholds (TPS48110 only); OCP %s / %s / %s mV at RSET 100 Ohm and RIWRN 39.7 k; ISCP bias %s / %s / %s uA (Equation 11,"
      % ((fmt(N["t48_enleak"] * 1e9, 0),) + tuple(fmt(x * 1e3, 1) for x in N["t48_wrn"]) + tuple(fmt(x * 1e6, 1) for x in N["t48_iscp"])))
    p("       464 Ohm); TMR %s / %s / %s uA to %s / %s / %s V, retry 22.7e6 x CTMR after 32 cycles; short-circuit response %s / %s us (TPS48110); charge pump %s to %s V;"
      % (tuple(fmt(x * 1e6, 0) for x in N["t48_tmr_i"]) + tuple(fmt(x, 3) for x in N["t48_tmr_v"]) + (fmt(N["t48_tsc"][0] * 1e6, 0), fmt(N["t48_tsc"][1] * 1e6, 0), fmt(N["t48_cp_on"][0], 0), fmt(N["t48_cp_off"][2], 0))))
    p("       gate-slew inrush 0.63 x V(BST-SRC) x CLOAD / (R1 x C1) (Equation 3); input pins to %s V absolute; TI's 100 Ohm VS filter and 1 nF CSCP (MAKER)" % fmt(N["t48_pin_abs"], 0))
    p("       it meets (1), (2) and (4); it limits no power, so (3) rests on the pass FET (3c)")
    p("     a power-limiting controller that operates under 9 V: none among the held sheets (TI's power-limiting hot-swap family starts at 9 V or above); not drafted (named)")
    en = ENTRY
    p("   3c. SELECTED (SESSION; draft apply_gen_sch_e_entry.py): U6 TPS48110AQDGXRQ1 (LCSC C17556513), Q7 CSD19536KTT (C2687963, D2PAK), R19 %s mOhm 1 %% %s ppm/K"
      % (fmt(en["rsns"] * 1e3, 1), fmt(en["rsns_tcr"] * 1e6, 0)))
    p("     (C2985708), L2 SRF1260-1R0Y (C7084461); RSET %s Ohm and RIWRN %s k at 0.1 %% (C861872), RISCP %s k, CTMR %s nF C0G (C97929), R1 %s k, C1 %s nF C0G 100 V"
      % (fmt(en["rset"], 0), fmt(en["riwrn"] / 1e3, 1), fmt(en["riscp"] / 1e3, 2), fmt(en["ctmr"] * 1e9, 0), fmt(en["r1"] / 1e3, 1), fmt(en["c1"] * 1e9, 0)))
    p("     (C184799), R2 %s Ohm, CBST %s uF; UVLO %s k over %s k, OV %s k over %s k at 0.1 %%, INP %s k over %s k, RVS %s Ohm with %s nF, CSCP %s nF (SESSION, CATALOGUE)"
      % (fmt(en["r2"], 0), fmt(en["cbst"] * 1e6, 0), fmt(en["uv_top"] / 1e3, 1), fmt(en["uv_bot"] / 1e3, 1), fmt(en["ov_top"] / 1e3, 0), fmt(en["ov_bot"] / 1e3, 1),
         fmt(en["inp_top"] / 1e3, 0), fmt(en["inp_bot"] / 1e3, 0), fmt(en["rvs"], 0), fmt(en["cvs"] * 1e9, 0), fmt(en["cscp"] * 1e9, 0)))
    p("     UVLO: on at %s / %s / %s V, off at %s / %s / %s V of DC_P; OV: off above %s / %s / %s V, on again under %s / %s / %s V (INFERRED, the leakage included)"
      % (tuple(fmt(x, 2) for x in N["uv_rise"]) + tuple(fmt(x, 2) for x in N["uv_fall"]) + tuple(fmt(x, 2) for x in N["ov_rise"]) + tuple(fmt(x, 2) for x in N["ov_fall"])))
    p("     overcurrent %s / %s / %s A (the printed row, the 0.1 %% parts, %s %% of their drift, R19's tolerance and drift); short circuit %s / %s / %s A;"
      % (fmt(N["ioc"][0], 3), fmt(N["ioc"][1], 2), fmt(N["ioc"][2], 3), fmt(en["drift"] * 100, 1), fmt(N["isc"][0], 2), fmt(N["isc"][1], 2), fmt(N["isc"][2], 2)))
    p("     the breaker's delay (item 2 of the final round): Equation 7 gives %s / %s / %s ms (CTMR on the GRM3195 family's rows, an ASSUMPTION for this part);"
      % (fmt(N["toc_eq7"][0] * 1e3, 3), fmt(N["toc_eq7"][1] * 1e3, 3), fmt(N["toc_eq7"][2] * 1e3, 3)))
    p("       TI's loaded row prints %s us typical at CTMR 22 nF (and %s / %s us at 0 nF), from the sense crossing to PD at CL 47 nF (SLUSEE5E p.10, MAKER), so"
      % (fmt(N["t48_toc22"] * 1e6, 0), fmt(N["t48_toc0"][0] * 1e6, 0), fmt(N["t48_toc0"][1] * 1e6, 0)))
    p("       the delay is taken as %s ms at least (Equation 7's, the row's excess over it not counted), %s ms typical (the row) and %s ms at most (Equation 7's"
      % (fmt(N["toc"][0] * 1e3, 3), fmt(N["toc"][1] * 1e3, 3), fmt(N["toc"][2] * 1e3, 3)))
    p("       maximum scaled by the row's %s over Equation 7), retry %s s (INFERRED)" % (fmt(N["toc_k"], 3), fmt(N["tretry"], 2)))
    p("     the short-circuit path: the sense reaches the comparator through RISCP x CSCP, a first-order filter of %s / %s / %s us (RISCP 1 %%, CSCP C0G 5 %% on the"
      % (fmt(N["tau"][0] * 1e6, 2), fmt(N["tau"][1] * 1e6, 2), fmt(N["tau"][2] * 1e6, 2)))
    p("       GRM3195 rows, ASSUMPTION), then PD within %s / %s us (tSC at CL 47 nF; Q7's %s nC at 12 V is %s nF, under the test load, so the row covers Q7) (MAKER,"
      % (fmt(N["t48_tsc"][0] * 1e6, 0), fmt(N["t48_tsc"][1] * 1e6, 0), fmt(N["q7_qg"] * 1e9, 0), fmt(N["q7_ceq"] * 1e9, 2)))
    p("       INFERRED); the filter's delay depends on the overdrive: a 14 A step against the highest %s A takes %s us before tSC (the check's example), a ramp"
      % (fmt(N["isc"][2], 4), fmt(N["filt_14"] * 1e6, 2)))
    p("       lags by at most tau, so the threshold is where the trip begins and the peak current is where the trajectory has moved by the delay (INFERRED)")
    p("     INP high from DC_P %s V, under the UVLO's lowest rise; at the clamps' %s V the pins see INP %s V, EN/UVLO %s V, OV %s V, under %s V (INFERRED)"
      % (fmt(N["inp_on_at"], 2), fmt(N["clamp"], 1), fmt(N["pins_at_clamp"][0], 2), fmt(N["pins_at_clamp"][1], 2), fmt(N["pins_at_clamp"][2], 2), fmt(N["t48_pin_abs"], 0)))
    p("     the start: slew %s / %s / %s V/ms (Equation 3, V(BST-SRC) %s to %s V, R1 and C1 tolerances); inrush %s to %s A into %s to %s uF; at most %s ms to %s V;"
      % (fmt(N["slew"][0] / 1e3, 2), fmt(N["slew"][1] / 1e3, 2), fmt(N["slew"][2] / 1e3, 2), fmt(N["t48_cp_on"][0], 0), fmt(N["t48_cp_off"][2], 0),
         fmt(N["inrush"][0], 3), fmt(N["inrush"][2], 3), fmt(N["c_load"][0] * 1e6, 1), fmt(N["c_load"][2] * 1e6, 1), fmt(N["t_start"] * 1e3, 2), fmt(D["vmax"], 2)))
    p("       U34 holds the front end off for %s ms at least, so the start's load is the bias network (section 7); CBST %s uF against Equation 4's %s nF (INFERRED)"
      % (fmt(T9["ctr2_ms"][0], 0), fmt(en["cbst"] * 1e6, 0), fmt(N["cbst_need"] * 1e9, 0)))
    p("     Q7's chart: CSD19536KTT Figure 4-10 from TI's vector drawing (SLPS540C p.6, single pulse, TC 25 C): at %s V 100 us %s A, 1 ms %s A, 10 ms %s A (MAKER);"
      % (fmt(D["vmax"], 2), fmt(N["ktt_at"]["100us"], 1), fmt(N["ktt_at"]["1ms"], 2), fmt(N["ktt_at"]["10ms"], 3)))
    p("       derated by L4-E9's %s (a 150 C part at a %s C case; this part's TJ is %s C, so it is conservative) (RECORD, INFERRED)" % (fmt(T9["derate"], 4), fmt(T9["tc_case"], 1), fmt(N["q7_tj"], 0)))
    p("     A START INTO A RESISTIVE FAULT (Rf 0.1 to 1000 Ohm on VIN_RAW at %s V; the breaker at its slowest: overcurrent %s A for %s ms, the short-circuit"
      % (fmt(D["vmax"], 2), fmt(N["ioc"][2], 2), fmt(N["toc"][2] * 1e3, 3)))
    p("       sense filtered at tau %s us against %s A and then %s us; the current follows its trajectory through every delay; both slew and capacitance"
      % (fmt(N["tau"][2] * 1e6, 2), fmt(N["isc"][2], 2), fmt(N["t48_tsc"][1] * 1e6, 0)))
    p("       corners; every point held against the chart for the whole pulse, conservative, no thermal-impedance superposition) (INFERRED):")
    for fet, (r, rf, dur, how, s, c), start in N["scan"]:
        p("       %-24s worst %s of the derated chart at Rf %s Ohm, %s ms, ended by %s (slew %s V/ms, %s uF); the start itself %s: %s"
          % (fet, fmt(r, 3), fmt(rf, 2), fmt(dur * 1e3, 3), how, fmt(s / 1e3, 2), fmt(c * 1e6, 1), fmt(start, 3), "MEETS" if r < 1.0 and start < 1.0 else "NOT MET"))
    hp, ht, hr = N["hs_start"]
    p("     A START INTO A HARD SHORT: VDS stays at %s V and the current follows the gate at most %s A/us (gfs %s S, TI's typical at 100 A taken as the bound,"
      % (fmt(D["vmax"], 2), fmt(N["a_g"] * 1e-6, 2), fmt(N["gfs"], 0)))
    p("       times the highest slew); the filtered sense reaches %s A and PD follows: a peak of %s A after %s us, %s of the derated 100 us line (MEETS,"
      % (fmt(N["isc"][2], 2), fmt(hp, 1), fmt(ht * 1e6, 2), fmt(hr, 3)))
    p("       CONDITIONAL on the transconductance bound) (INFERRED)")
    p("     A HARD SHORT IN SERVICE (Q7 fully on): the current rises at VIN / L; the filter and PD add at most tau + tSC = %s us, so the peak is at most %s A"
      % (fmt(N["t_d"] * 1e6, 2), fmt(N["isc"][2], 2)))
    p("       plus VIN x %s us / L, and never more than VIN over the loop's resistance. Q7's IDM %s A derated by %s gives %s A; at the entry's highest on-voltage"
      % (fmt(N["t_d"] * 1e6, 2), fmt(N["idm"], 0), fmt(T9["derate"], 4), fmt(N["i_allow"], 1)))
    p("       (the OV rise's %s V) that holds for a loop inductance of %s uH or more from the source to the fault: the threshold is %s to %s A; the PEAK is set"
      % (fmt(N["v_on_max"], 2), fmt(N["l_min"] * 1e6, 2), fmt(N["isc"][0], 2), fmt(N["isc"][2], 2)))
    p("       by the inductance, which no document gives (L4-E9's open item, carried as E11-20 with this bound) (CONDITIONAL)")
    p("   3d. the kit's series resistance from the plug, at the hot end (the low side of the envelope and the in-service maximum):")
    for n, x, cl in N["r_plug_dcp"] + N["r_dcp_vin"]:
        p("     %-104s %s mOhm (%s)" % (n, fmt(x * 1e3, 3), cl))
    p("     the plug to DC_P %s mOhm, DC_P to VIN_RAW %s mOhm, %s mOhm in all (INFERRED); the first round's 20 C copper-only model gives %s mOhm for this"
      % (fmt(N["r1_hot"] * 1e3, 2), fmt(N["r2_hot"] * 1e3, 2), fmt(N["r_hot"] * 1e3, 2), fmt(E["r_plug"]["selected"] * 1e3, 3)))
    p("       construction: it left out the hot values and the contacts")
    p("   3e. the in-service maximum at a 9.00 V plug (the corrected knee's high band, VBUS20 at %s V, the front end at %s, the losses hot) (INFERRED):"
      % (fmt(E["vb_top"], 2), fmt(E["eta_fe"], 2)))
    p("     VIN_RAW %s V, %s A from the plug, DC_P %s V; against the selected entry:" % (fmt(N["vin9"], 3), fmt(N["i9"], 3), fmt(N["dcp9"], 3)))
    p("       UVLO: its highest rise %s V against DC_P at %s V or more before any current flows (MEETS); its highest fall %s V against DC_P %s V in service (MEETS)"
      % (fmt(N["uv_rise"][2], 2), fmt(N["dcp_noload"], 3), fmt(N["uv_fall"][2], 2), fmt(N["dcp9"], 2)))
    p("       overcurrent: %s A at its lowest against %s A, %s %% in hand (INFERRED). The efficiency floor (item 1 of the final round), with the current and"
      % (fmt(N["ioc"][0], 3), fmt(N["i9"], 3), fmt(N["ioc_margin"] * 100, 1)))
    p("         the voltage coupled: Pout / [Itrip x (9 - Itrip x Rloop)] = %s W / [%s A x (9 - %s A x %s mOhm)] = %s; the front end's efficiency at the"
      % (fmt(N["pout9"], 3), fmt(N["ioc"][0], 5), fmt(N["ioc"][0], 5), fmt(N["r_hot"] * 1e3, 3), fmt(N["eta_floor"], 6)))
    p("         operating point must be at least that (L4-E5 takes %s, undocumented: C-8) (CONDITIONAL); the same margin read as U3's board current: %s A over"
      % (fmt(E["eta_fe"], 2), fmt(N["board_excess"], 3)))
    p("         the knee's high band, against the pin's inferred +-%s A (INFERRED)" % fmt(PIN_ERR, 1))
    p("         the fix round's own point (knee %s A, loop %s mOhm, the check's reproduction) gives %s W and a floor of %s, and at that efficiency the equation"
      % (fmt(FIX_KNEE_IT, 2), fmt(FIX_RLOOP * 1e3, 3), fmt(N["fix_pout"], 3), fmt(N["fix_eta"], 6)))
    p("         returns %s A, the trip's lowest: the fix round's 0.906 scaled the current inversely with the efficiency at a fixed voltage and is withdrawn (INFERRED)"
      % fmt(N["fix_i"], 5))
    p("         judged: the static margin rests on three things no held document bounds (the front end's efficiency at 8.1 V, the pin's real band, and the")
    p("         input current's excursions in transients, which the breaker passes only for under %s ms); the component temperatures and losses are bounded"
      % fmt(N["toc"][0] * 1e3, 3))
    p("         (the hot case is the worst). R19 cannot buy more: its least value keeping the breaker's highest under F1's %s A is %s mOhm (no stocked part),"
      % (fmt(F["f_hot_a"], 1), fmt(N["r19_f1"] * 1e3, 3)))
    p("         which would move the lowest trip only to %s A. So the margin was moved on the other side: the knee's flat target %s A (3f) instead of the"
      % (fmt(N["trip_min_r19_f1"], 3), fmt(KNEE_IT, 2)))
    p("         fix round's 1.89 A; what closes it is E11-06's measurement of those three at a 9.00 V plug (SESSION, CONDITIONAL)")
    p("       F1: the breaker's highest %s A against its %s C column %s A (MEETS, MAKER); L2 at %s A: %s K over the %s C air, %s C under its 105 C (MEETS, MAKER)"
      % (fmt(N["ioc"][2], 3), fmt(F["f_col"], 0), fmt(F["f_hot_a"], 1), fmt(N["ioc"][2], 2), fmt(N["l2_rise"], 1), fmt(F["air_hot"], 1), fmt(F["air_hot"] + N["l2_rise"], 1)))
    p("       Q7 at %s A: %s W (INFERRED); the highest in-service current over 9 to 36 V is the 9 V one, %s A (INFERRED)" % (fmt(N["ioc"][2], 2), fmt(N["q7_w"], 3), fmt(N["imax_all"], 3)))
    p("   3f. THE CORRECTED KNEE (SESSION, specification for L4-E5's undrawn network) AND THE RESTART GUARD (draft apply_gen_sch_a_guard.py):")
    p("     flat target %s A of board current (the pin at %s V) from VIN_RAW %s V up to %s V, where L4-E5's line (%s A/V) takes over; below %s V L4-E5's knee slope"
      % (fmt(KNEE_IT, 2), fmt(1 + 0.4 * KNEE_IT, 3), fmt(KNEE_TOP, 2), fmt(N["v_join"], 3), fmt(E["slope"] / 0.4, 6), fmt(KNEE_TOP, 2)))
    p("       (%s V/V at the pin): zero at %s V, HIZ entry %s V, exit %s V; with L4-E5's +-%s %% the knee's top is at most %s V, %s V under the 9 V plug's VIN_RAW,"
      % (fmt(N["knee_slope"], 3), fmt(N["v_zero"], 3), fmt(N["v_hiz_in"], 3), fmt(N["v_hiz_out"], 3), fmt(N["knee_tol"] * 100, 2), fmt(N["top_max"], 3), fmt(N["top_margin"], 3)))
    p("       and HIZ is certain below %s V (SESSION, INFERRED); the warm-up's plan figure (3g) sets the target at %s A or more, and %s A leaves the rest of"
      % (fmt(N["hiz_certain"], 3), fmt(N["it_need"], 4), fmt(KNEE_IT, 2)))
    p("       the window to the breaker (3e) (SESSION)")
    p("     the guard (U34, board A): R14 %sk over R15 %sk as drawn falls at %s / %s / %s V; R14 %sk: falls at %s / %s / %s V and rises at %s / %s / %s V (SNVSBJ1E, INFERRED)"
      % ((fmt(N["guard_r"][0] / 1e3, 0), fmt(N["guard_r"][1] / 1e3, 0)) + tuple(fmt(x, 3) for x in N["guard_drawn"][0]) + (fmt(GUARD_R14_K, 1),)
         + tuple(fmt(x, 3) for x in N["guard_new"][0]) + tuple(fmt(x, 3) for x in N["guard_new"][1])))
    p("       %s V under the knee's certain HIZ (L4-E5's rule: 0.1 V or more; MEETS); at its lowest fall the running levels scale to FE_VZ %s V, FE_RUN %s V"
      % (fmt(N["guard_margin"], 3), fmt(N["guard_levels"][0], 2), fmt(N["guard_levels"][1], 2)))
    p("       (Q36 and Q37 need %s V at most) and EN %s V (VEN(OP) %s V at most): MEETS (INFERRED: the network is resistive under the zener's knee)"
      % (fmt(N["guard_levels"][2], 1), fmt(N["guard_levels"][3], 2), fmt(N["ven_op"], 2)))
    p("   3g. THE FUNCTIONAL WARM-UP AT A 9.00 V PLUG, AS A SHEDDING SEQUENCE (item 3 of the final round): REQ-024's start with the pack cold-soaked (both")
    p("     FETs open, S4), REQ-046's heater before any charge and the charge held while the charger carries the kit (REQ-077), done by the bridge on slot 2.")
    p("     The loads, battery-side, from hc2's pwr_red2.py and rv-pwr's pwr_budget.py run as hc2 runs them (pinned; RECORD, INFERRED); held in P1 (SESSION):")
    for k_, v_ in N["shed_held"]:
        p("       %-24s %s / %s / %s W at the load (RECORD)" % (k_, fmt(v_[0], 3), fmt(v_[1], 3), fmt(v_[2], 3)))
    p("     phase | lo / plan / hi W at VBAT | against 9.00 V at the plug, %s to %s W (3h)" % (fmt(N["env"][9.0]["w_lo"], 2), fmt(N["env"][9.0]["w_hi"], 2)))
    for lab, ld, cl in N["phases"]:
        p("       %-96s %s / %s / %s | %s (INFERRED)" % (lab, fmt(ld[0], 2), fmt(ld[1], 2), fmt(ld[2], 2), " / ".join(cl)))
    p("       P3 charge: the cells over 3 C, the cold hold cleared; the source's surplus over P1 goes to the charge by DPM: %s W at the plan figure, %s at"
      % (fmt(N["surplus"][0], 2), "none" if N["surplus"][1] <= 0 else fmt(N["surplus"][1], 2) + " W"))
    p("         the hi corner, whose P1 exceeds the source's least (INFERRED); the charge then within R-b's bounds (section 2)")
    p("     the mat runs on measured headroom (SESSION): on only while the source's measured headroom over the load is at least the mat's %s W, else it is"
      % fmt(N["heater_w"], 2))
    p("       cycled, so control is kept whenever P1 alone is carried; the warm-up completes on that rule while P1's load is at most %s W (the source's least"
      % fmt(N["shed_room"], 2))
    p("       %s W less the mat) (INFERRED)" % fmt(N["env"][9.0]["w_lo"], 2))
    p("     the result: at the plan figure every phase is carried at every source corner, the warm-up with %s W in hand; at the hi corner P1 (%s W) exceeds the"
      % (fmt(N["func_margin"], 2), fmt(N["shed"][2], 2)))
    p("       source's least, so neither control nor the warm-up is bounded there (NOT BOUNDED by held evidence: E11-06 measures P1)")
    p("     the thermal side: P2 puts %s W of heat inside; with hc2's lid-open conductance (%s to %s W/K, the fans on; P1 holds the mixer fans, so the air runs"
      % (fmt(N["func_heat_in"], 1), fmt(N["g_cold"][0], 1), fmt(N["g_cold"][1], 1)))
    p("       warmer than this) the inside air at -20 C ambient is %s to %s C, so the cells are warmed by the mat alone; the time from the cold soak to 3 C"
      % (fmt(N["air_m20"][0], 1), fmt(N["air_m20"][1], 1)))
    p("       needs the mat-to-cell coupling and the pack's loss to the air, which no held record gives (NOT BOUNDED: E11-23 measures it) (INFERRED)")
    p("     REQ-015 at 9.00 V at the plug: CONDITIONAL CANDIDATE, on E11-06 (P1's load, the front end's efficiency, the pin's band, the transients), E11-09")
    p("       (the knee drawn), E11-23 (the warm-up time), E11-05 (N1, and N2 for S2) and E11-22 (R-b's bounds); not closed (INFERRED)")
    p("   3h. THE SOURCE ENVELOPE AT THE PLUG (the low side with the losses hot and VBUS20 at %s V, the high side with no loss and %s V; U3 %s) (INFERRED):"
      % (fmt(E["vb_low"], 3), fmt(E["vb_top"], 2), fmt(E["eta_u3"], 4)))
    p("   plug | VIN_RAW at the low side | U3 board current, A | at VBAT, W | L4-E9 at VIN_RAW (no loss) (INFERRED)")
    for v in (9.0, 12.0, 24.0, 36.0):
        e = N["env"][v]
        l9 = {9.0: "%s to %s W" % (fmt(E["l9"]["min9"], 1), fmt(E["l9"]["max9"], 1)), 12.0: "up to %s W" % fmt(E["l9"]["max12"], 1), 24.0: "up to %s W" % fmt(E["l9"]["max24"], 1), 36.0: "(the window)"}[v]
        p("     %5s V | %s V | %s to %s | %s to %s | %s" % (fmt(v, 1), fmt(e["vin_lo"], 3), fmt(e["board_lo"], 3), fmt(e["board_hi"], 3), fmt(e["w_lo"], 2), fmt(e["w_hi"], 2), l9))
    p("   the states at their plan figure against it:")
    for name, (lo, plan, hi) in list(E["states"].items()) + [("the warm-up (P2)", N["func"])]:
        key = name if name != "the warm-up (P2)" else "the functional warm-up (one module and the heater)"
        cl = " | ".join("%s V: %s" % (fmt(v, 0), N["cls"][(key, v)]) for v in (9.0, 12.0, 24.0, 36.0))
        p("     %-32s %s W | %s (RECORD, INFERRED)" % (name, fmt(plan, 2), cl))
    p("   a dead pack's charge on top: at most %s A x %s V = %s W under R-b in case (i) (section 2; %s W at its %s V threshold), taken only from what DPM"
      % (fmt(N["rb_max"], 3), fmt(R["cv_max"], 3), fmt(N["dead_charge_w_max"], 2), fmt(N["dead_charge_w"], 2), fmt(RULE_SRN_V, 1)))
    p("     leaves after the system (9.3.17): it never pushes the kit out of the envelope (INFERRED; the first round's 4.22 W took the typical 384 mA as a bound)")
    p("   3i. the first round's finding U4-F3 as found (the DRAWN knee at the plug, the 20 C model): a 9.00 V plug settles VIN_RAW at %s V and gives %s W (selected"
      % (fmt(E["plug"]["selected"]["vin"], 3), fmt(E["plug"]["selected"]["w"], 1)))
    p("     interconnect) or %s V and %s W (drawn), against %s W at VIN_RAW 9 V: the drawn knee caps the plug's 9 V; 3f replaces it (INFERRED)"
      % (fmt(E["plug"]["drawn"]["vin"], 3), fmt(E["plug"]["drawn"]["w"], 1), fmt(E["line9_nom_w"], 1)))
    p("")
    p("4. U-04, THE COMPARISON'S OWN FIGURES")
    p("   (B) a battery FET in the pack path carries the pack's peak: %s W per mOhm at %s A, %s mW per mOhm at PS-IDLE-SPEC's %s A (INFERRED)"
      % (fmt(C["batfet_w_per_mohm_18a"], 3), fmt(C["pack_peak"]), fmt(C["batfet_w_per_mohm_idle"] * 1000, 1), fmt(C["idle_a"], 2)))
    p("     the one NVDC charger held, TI's BQ25798, states NVDC regulation (p.%d) but its integrated battery FET carries %s A RMS and %s A for 1 s (p.%d),"
      % (C["nvdc_p"], fmt(C["bq98_rms"]), fmt(C["bq98_pk"]), C["bq98_p"]))
    p("     under the pack's %s A peak (the declared VBAT peak, NETLIST): (B) needs an external-FET part whose sheet is not held (MAKER, INFERRED)" % fmt(C["pack_peak"]))
    p("   (C) a pre-charge resistor on board P from VSYS at %s V into a pack at the Shutdown Voltage (%s V): for the cell maker's 0.1 C (%s A for 3P)"
      % (fmt(B["cv4s"], 1), fmt(P["vsys_shut"][0], 1), fmt(C["pre_i_01c"], 2)))
    p("     %s ohm and %s W, %s W at CUV; for the charger's own %s mA, %s ohm and %s W (INFERRED)"
      % (fmt(C["pre_r_01c"], 2), fmt(C["pre_w_01c"], 2), fmt(C["pre_w_cuv_01c"], 2), fmt(B["iclamp"] * 1000), fmt(C["pre_r_clamp"], 1), fmt(C["pre_w_clamp"], 2)))
    p("")
    p("5. U-04, IS AN OWNER QUESTION FORCED?")
    p("   a mandatory requirement naming a load state for source-only operation: %s (section 1); the warm-up sequence of 3g is carried at its plan figure" % ("yes" if F["owner_question"] else "none"))
    p("   what the source path itself admits at a 9.00 V plug, the kit's losses included and VBUS20's other loads taken off (INFERRED; the first round's")
    p("     %s / %s / %s W left the losses out):" % (fmt(F["cap9_hot_w"], 1), fmt(F["cap9_cold_w"], 1), fmt(F["cap9_15a_hot_w"], 1)))
    for lab, ia, rr, vr, w in N["caps"]:
        p("     %-46s %s mOhm: VIN_RAW %s V, %s W at VBAT (MAKER, INFERRED)" % (lab, fmt(rr * 1e3, 2), fmt(vr, 3), fmt(w, 2)))
    p("     (the check's reference, 115.511 mOhm with no auxiliary load: " + ", ".join("%s A %s W" % (fmt(ia, 1), fmt(w, 2)) for ia, w in N["check_ref"]) + ")")
    p("   these are the path's ceilings with the electronics set to use all of them; the breaker's band and the knee's spread keep the least delivered")
    p("     figure lower (3h: %s W at 9 V) (INFERRED). REQ-015 states no source current capability: every figure takes the source as holding its voltage (named)" % fmt(N["env"][9.0]["w_lo"], 2))
    typ, cwu = E["states"]["PS-TYP"][1], E["states"]["the cold warm-up (CONOPS 4c)"][1]
    (_l0, _i0, _r0, _v0, c_hot), (_l1, _i1, _r1, _v1, c_cold), (_l2, _i2, _r2, _v2, c_15) = N["caps"]
    cmp_ = lambda x, c: "over" if x > c else "under"
    p("   so NO owner question is forced: no approved requirement names a load REQ-015's 9 V must carry beyond the functional sequence, which 3c to 3g carry at")
    p("     its plan figure (CONDITIONAL, 3g). Against the ceilings: PS-TYP %s W is %s F1's hot ceiling %s W and %s its cold %s W; the CONOPS cold warm-up"
      % (fmt(typ, 2), cmp_(typ, c_hot), fmt(c_hot, 2), cmp_(typ, c_cold), fmt(c_cold, 2)))
    p("     %s W (a cold state, so F1's cold column applies) is %s its cold ceiling %s W; a 15 A part's hot ceiling %s W is %s both. So the kit at 9 V with F1 as"
      % (fmt(cwu, 2), cmp_(cwu, c_cold), fmt(c_cold, 2), fmt(c_15, 2), "over" if c_15 >= max(typ, cwu) else "not over"))
    p("     fitted does not carry PS-TYP hot or the CONOPS warm-up cold: a design envelope stated, not a conflict with an approved requirement (INFERRED)")
    p("")
    p("6. D-06, F1'S WEAK-SOURCE BAND AND THE INTERCONNECT")
    p("   0997010.WXN time-current (MAKER, held sheet p.3): " + "; ".join("%s %%: %s to %s s" % (fmt(pct * 100, 0), fmt(tmin, 2), "-" if tmax is None else fmt(tmax, 2)) for pct, tmin, tmax in D["tc"]))
    p("   the envelope a source can leave, read monotone (a larger current clears no later than a smaller one; INFERRED), with each interval's top I2t:")
    for lo, hi, tt, i2t in N["i2t_top"]:
        if tt is None:
            p("     up to %s A: no maximum time printed: carried with no time limit" % fmt(hi, 1))
        elif hi == N["i_pf_spec"]:
            p("     from %s A up to the specified worst stiff-source current %s A (the loop's floor, below): at most %s s by the 600 %% row, which bounds the energy"
              % (fmt(lo, 1), fmt(hi, 1), fmt(tt, 2)))
            p("       only by %s A2s; F1's total clearing I2t at 58 V DC is not printed (the sheet's %s A2s is a typical melting figure from its breaking tests),"
              % (fmt(i2t, 0), fmt(N["f1_melt"], 0)))
            p("       so above %s A the elements are judged" % fmt(lo, 0))
            p("       against F1's total clearing I2t at %s A once filed (R-115, E11-16) (MAKER, INFERRED)" % fmt(hi, 0))
        else:
            p("     from %s A up to %s A: up to %s s, %s A2s at the interval's top" % (fmt(lo, 1), fmt(hi, 1), fmt(tt, 2), fmt(i2t, 0)))
    p("   the elements in that fault loop, as drawn:")
    for n, r, src, cls in D["drawn"]:
        p("     %-58s %s (%s; %s)" % (n, ("%s A" % fmt(r, 1)) if r is not None else "no rating", src, cls))
    p("   as drawn: NOT MET (every element needs at least %s A with no time limit; one is %s A, four state none) (INFERRED)" % (fmt(D["cont_need"], 1), fmt(D["c16"], 0)))
    p("   option (ii), a smaller fuse, with the tolerances shown: the 7.5 A MINI's %s C column is %s A; an LM5069 limit whose maximum is that has its minimum at"
      % (fmt(F["f_col"], 0), fmt(N["f75_hot"], 1)))
    p("     %s A (VCL %s over %s mV, R19 at +-1 %%), the selected breaker's at %s A: both under the in-service %s A at 9 V (and L4-E5's 4.629 A): rejected (INFERRED)"
      % (fmt(N["f75_lm"], 3), fmt(T9["vcl"][0] * 1e3, 1), fmt(T9["vcl"][2] * 1e3, 1), fmt(N["f75_tps"], 3), fmt(N["i9"], 3)))
    p("   SELECTED (SESSION): every element of the interconnect rated at least %s A continuous where installed, which covers the envelope to 20 A for"
      % fmt(CONT_CLASS_A, 0))
    p("     any time; above it, the short-time obligations below:")
    for n, cl, r, src in D["selected"]:
        p("     %-46s %s%s (%s) (SESSION)" % (n, cl, (" : %s A" % fmt(r, 0)) if r is not None else "", src))
    p("     D38999 contact table p.%d (MAKER); shell 13's Series III arrangements 13-4, 13-8, 13-26, 13-32, 13-35 (p.%d), shell 17's 17-2, 17-6, 17-8 (p.%d) (MAKER)"
      % (D["d38999_p"], D["ins13_p"], D["ins17_p"]))
    p("   the interval tops against a %s mm2 core, adiabatic (INFERRED: copper's resistivity and volumetric heat):" % fmt(SEL_MM2, 3))
    for lo, hi, tt, dt in N["adiab"]:
        p("     %s A for %s s: %s K%s (INFERRED)" % (fmt(hi, 1), fmt(tt, 2), fmt(dt, 2), "; the monotone bound only, F1's clearing I2t decides it" if hi == N["i_pf_spec"] else ""))
    p("   and against the size 12 contact's %s A, which Amphenol prints as a crimp-contact test current (p.%d), not an installed rating: the same I2t as %s"
      % (fmt(D["c12"], 0), D["d38999_p"], "; ".join("%s A for %s s = %s s at %s A" % (fmt(hi, 0), fmt(tt, 2), fmt(e, 3), fmt(D["c12"], 0)) for lo, hi, tt, e in N["contact_eq"][1:])))
    p("     (INFERRED; the contact's installed continuous rating and its short-time limit are not printed: E11-10 and E11-16)")
    p("   THE WITHSTAND OBLIGATIONS of every element the fault current passes (the receptacle and plug contacts, the NATO plug, the cable's and the inside lead's")
    p("     cores, J_DCIN, F1's holder, board E's copper to F1): each carries %s A continuous (which covers the envelope to %s A), %s A for %s s and"
      % (fmt(CONT_CLASS_A, 0), fmt(N["intervals"][1][1], 0), fmt(N["intervals"][2][1], 0), fmt(N["intervals"][2][2], 0)))
    p("     %s A for %s s, and from %s A to %s A has a short-time capability of at least F1's total clearing I2t at %s A and 58 V DC, which is not printed; until it is filed the only"
      % (fmt(N["intervals"][3][1], 0), fmt(N["intervals"][3][2], 1), fmt(N["intervals"][4][0], 0), fmt(N["i_pf_spec"], 0), fmt(N["i_pf_spec"], 0)))
    p("     bound is the 600 %% row's %s A2s, which no element's held data is shown to withstand (E11-16 files both sides) (MAKER, INFERRED)" % fmt(N["i2t_top"][4][3], 0))
    p("   THE INTERCONNECT BY ITS RESISTANCE (SESSION; final round): a larger or purer conductor raises a stiff fault, so the check rests on a measured floor,")
    p("     not on copper constants, and the floor is set so the worst case stays %s A, %s %% under F1's %s A, on L4-E9's %s V basis (kept: it is over"
      % (fmt(N["i_pf_spec"], 0), fmt((1 - N["i_pf_spec"] / D["interrupt_a"]) * 100, 0), fmt(D["interrupt_a"], 0), fmt(D["vmax"], 2)))
    p("     REQ-015's 40 V over-voltage test and the new entry's OV maximum %s V, which would give %s A on the same floor):"
      % (fmt(N["ov_rise"][2], 2), fmt(N["ov_rise"][2] / N["loop_floor_cold"], 1)))
    p("     the loop from the NATO plug's pins to J_DCIN's board pins (the cable, the D38999 pair, the inside lead, J_DCIN), its actual resistance at 20 C")
    p("       at least %s mOhm (%s mOhm at %s C) and at most %s mOhm (the 9 V envelope's basis, 3d) (SESSION, INFERRED)"
      % (fmt(N["loop_floor20"] * 1e3, 2), fmt(N["loop_floor_cold"] * 1e3, 2), fmt(T_COLD, 0), fmt(N["loop_ceil20"] * 1e3, 1)))
    p("     the acceptance, four-wire on every assembly and every replacement, with the instrument and fixture within %s %% of reading and the conductor's"
      % fmt(U_MEAS * 100, 0))
    p("       temperature known within %s K (%s %% with copper's coefficient), the reading corrected to 20 C: %s to %s mOhm (SESSION, INFERRED)"
      % (fmt(DT_MEAS, 0), fmt(N["u_meas"] * 100, 2), fmt(N["acc"][0] * 1e3, 2), fmt(N["acc"][1] * 1e3, 2)))
    p("     the selected construction: %s m of AWG 14 with the 0.5 m lead, copper %s mOhm at 20 C, with the D38999 pair and J_DCIN at most %s mOhm more:"
      % (fmt(SEL_CABLE_M, 2), fmt(N["cu_nom20"] * 1e3, 2), fmt(N["contacts_max"] * 1e3, 2)))
    p("       %s to %s mOhm, inside the window; copper alone reaches the floor from %s m (INFERRED); a reading outside the window is corrected by length"
      % (fmt(N["constr"][0] * 1e3, 2), fmt(N["constr"][1] * 1e3, 2), fmt(N["min_len_floor"], 2)))
    p("   THE STIFF SOURCE AGAIN (copper alone at %s C, the source's own resistance zero, A-12; at the OVLO maximum %s V):" % (fmt(T_COLD, 0), fmt(D["vmax"], 2)))
    for lab, rr, ipf in D["stiff"]:
        p("     %-48s %s ohm, %s A against %s A: %s (INFERRED)" % (lab, fmt(rr, 5), fmt(ipf, 1), fmt(D["interrupt_a"], 0), "MEETS" if ipf <= D["interrupt_a"] else "NOT MET"))
    p("   so a heavier interconnect needs a resistance floor: F1's 1000 A alone would need %s ohm at %s C (AWG 14 from %s m); the specified floor above"
      % (fmt(D["r_floor"], 5), fmt(T_COLD, 0), fmt(D["min_len_14"], 2)))
    p("     keeps %s A with the margin and the measurement's uncertainty; the selected construction's own figure is %s A; a shorter or heavier lead needs"
      % (fmt(N["i_pf_spec"], 0), fmt(N["sel_ipf_cold"], 1)))
    p("     a fuse with a larger interrupting rating at 58 V DC, of which no sheet is held (named) (INFERRED)")
    p("   F1's other checks with it: the selected breaker's highest %s A (the drawn LM5069's 6.15 A) against its %s C column %s A (MEETS, MAKER);"
      % (fmt(N["ioc"][2], 3), fmt(F["f_col"], 0), fmt(F["f_hot_a"], 1)))
    p("     the lowest stiff fault at 9 V with the copper at %s C, %s A, %s times the rating, inside the 600 %% row's 0.1 s (MEETS, INFERRED);"
      % (fmt(F["air_hot"], 1), fmt(D["min_fault_9v"], 1), fmt(D["min_fault_9v_x"], 2)))
    p("     the start's I2t: the LM5069's longest at its timer's maximum in section 7, the selected entry's inrush %s A for %s ms (MEETS, INFERRED)"
      % (fmt(N["inrush"][2], 2), fmt(N["t_start"] * 1e3, 2)))
    p("")
    p("7. D-09, THE HOT SWAP'S FAULT TIME AGAINST ITS START")
    p("   LM5069 (SNVS452G): VTMRH %s / %s / %s V, ITIMER %s / %s / %s uA, VCL %s / %s / %s mV; Equation 9 (1.30e5, 1.18 mV); TI's half-again margin (9.2.1.2.4, p.%d) (MAKER)"
      % (tuple(fmt(x, 2) for x in T9["vtmrh"]) + tuple(fmt(x * 1e6, 0) for x in T9["itimer"]) + tuple(fmt(x * 1e3, 1) for x in T9["vcl"]) + (T9["eq12_p"],)))
    p("   the power limit with R24 22k (L4-E9's draft) and R19 10 mOhm %s %%: %s W at %s V, falling with VDS (Equation 9) (MAKER, NETLIST; L4-E9 reads %s W)"
      % (fmt(T9["rs_tol"] * 100, 0), fmt(T9["plim_nom"], 3), fmt(D["vmax"], 2), fmt(T9["plim_nom_l9"], 2)))
    p("   what the start charges (NETLIST): " + ", ".join("%s %s %s uF on %s" % (b, ref, fmt(c, 1), net) for b, ref, net, c in T9["caps"]) + " = %s uF nominal" % fmt(T9["c_uf"], 1))
    p("     (L4-E9 counted 31 uF: C6 on DC_HS, and C207 and C210 behind D19 and R196, are added); the X7R rows stacked as L4-E9: K %s %%, %s %%, %s %% (Yageo V.26, MAKER; an ASSUMPTION for parts of other makers)"
      % (fmt(T9["x7r"][0] * 100, 0), fmt(T9["x7r"][1] * 100, 0), fmt(T9["x7r"][2] * 100, 0)))
    p("   the resistive load on VIN_RAW during the start, each path bounded by its resistor alone: " + ", ".join("%s %s %s k" % (b, r, fmt(x / 1e3, 1)) for b, r, x in T9["loads"])
      + ", %s mA at %s V, and U2's shutdown %s uA (MAKER LM5176 IQ) (NETLIST, INFERRED)" % (fmt(T9["g_load"] * D["vmax"] * 1e3, 1), fmt(D["vmax"], 2), fmt(T9["u2_sd"] * 1e6, 0)))
    p("   THE FRONT END'S OWN LOAD: U2 is held off by U34 until its release, %s / %s / %s ms after VIN_RAW passes the UV rise (gen_sch_a.py's"
      % tuple(fmt(x, 0) for x in T9["ctr2_ms"]))
    p("     derivation from SNVSBJ1E), %s times the start's maximum: the soft start never overlaps the hot swap's start, so its load during the"
      % fmt(T9["ctr2_over_start"], 1))
    p("     start is the bias network above (INFERRED, NETLIST)")
    p("   the start (TI's Equation 12 with the power limit following VDS, integrated; the load included) (INFERRED):")
    p("     nominal: %s ms (Equation 12 with the limit held at its %s V value: %s ms; L4-E9 %s ms on 31 uF) (INFERRED)"
      % (fmt(T9["start_nom"] * 1e3, 3), fmt(D["vmax"], 2), fmt(T9["eq12_nom"] * 1e3, 3), fmt(T9["start_l9"][0] * 1e3, 3)))
    p("     corners: the capacitors at the stacked top, R24 -1 %%, R19 +%s %%, the limit over TI's 1.3, VCL's minimum: %s ms (%s ms without the load; L4-E9 %s ms) (INFERRED)"
      % (fmt(T9["rs_tol"] * 100, 0), fmt(T9["start_max"] * 1e3, 3), fmt(T9["start_max_noload"] * 1e3, 3), fmt(T9["start_l9"][1] * 1e3, 3)))
    p("     TI's margin: the fault time's minimum at least %s ms (1.5 x the corner start) (INFERRED)" % fmt(T9["need"] * 1e3, 3))
    p("   C5 as drawn (100 nF K X7R, L4-E9's stack from the timer rows): %s to %s ms (L4-E9 2.035 to 11.871 ms from L4-E5's rounded times): NOT MET against %s ms (INFERRED)" % (fmt(T9["c5_l9"][0] * 1e3, 3), fmt(T9["c5_l9"][1] * 1e3, 3), fmt(T9["need"] * 1e3, 3)))
    p("   Q7's Figure 10 at %s V from TI's vector drawing: 10 ms %s A, 1 ms %s A, DC %s A at TC 25 C; m %s; derated to Q7's %s C case by %s (L4-E9) (MAKER, RECORD)"
      % (fmt(D["vmax"], 2), fmt(T9["i10"], 3), fmt(T9["i1"], 3), fmt(T9["idc"], 4), fmt(T9["m"], 4), fmt(T9["tc_case"], 1), fmt(T9["derate"], 4)))
    p("     the pulse %s A (the limit at its corners times TI's 1.3, L4-E9) fits the power law carried past 10 ms up to %s ms (CONDITIONAL on the law past 10 ms)"
      % (fmt(T9["pulse_a"], 3), fmt(T9["t_soa_max"] * 1e3, 2)))
    p("   no single C0G part of 150 nF is stocked: %d surface-mount 150 nF C0G or NP0 rows read, %d with stock (CATALOGUE, inputs/jlc-search-c0g-150nf)" % T9["search150"])
    p("   the stocked GRM3195 C0G parts read (Murata reference sheets, Jun.11,2026): " + "; ".join(
        "%s %s nF +-%s %%, %s V, 0+-%s ppm/K, Table A +%s/-%s %% at -55 C, endurance +-%s %%, damp heat +-%s %% (p.%d)"
        % (pn, fmt(v["c"] * 1e9, 0), fmt(v["tol"] * 100, 0), fmt(v["v"], 0), fmt(v["ppm"] * 1e6, 0), fmt(v["ta_up"] * 100, 2), fmt(v["ta_dn"] * 100, 2), fmt(v["endur"] * 100, 0), fmt(v["damp"] * 100, 1), v["page"])
        for pn, v in T9["mur"].items()) + " (MAKER)")
    p("   candidate | C nF | stacked C nF (tolerance, temperature, endurance) | fault time ms | start | Figure 10 at its maximum (CONDITIONAL)")
    for r in T9["cands"]:
        p("     %-42s | %s | %s to %s | %s to %s | %s | %s A against %s A: %s (INFERRED)"
          % (r["lab"], fmt(r["c"] * 1e9, 0), fmt(r["lo"] * 1e9, 2), fmt(r["hi"] * 1e9, 2), fmt(r["tmin"] * 1e3, 3), fmt(r["tmax"] * 1e3, 3),
             "MEETS" if r["start_ok"] else "NOT MET", fmt(r["soa"], 4), fmt(T9["pulse_a"], 3), "MEETS" if r["soa_ok"] else "NOT MET"))
    S = T9["sel"]
    p("   SELECTED (SESSION): C5 %s (LCSC %s) with C121 %s (LCSC %s), both 1206 C0G 50 V, on HS_TIMER: %s nF; fault time %s ms nominal, %s to %s ms stacked"
      % (S["parts"][0], T9["sel_codes"][0], S["parts"][1], T9["sel_codes"][1], fmt(S["c"] * 1e9, 0), fmt(T9["sel_nom_ms"] * 1e3, 3), fmt(S["tmin"] * 1e3, 3), fmt(S["tmax"] * 1e3, 3)))
    p("     start: %s ms against %s ms, %s ms in hand, so the margin holds while the start stays under %s ms (MEETS, INFERRED); Figure 10: %s A against %s A at %s ms, %s %% past the 10 ms line (MEETS, CONDITIONAL)"
      % (fmt(S["tmin"] * 1e3, 3), fmt(T9["need"] * 1e3, 3), fmt((S["tmin"] - T9["need"]) * 1e3, 3), fmt(S["tmin"] / 1.5 * 1e3, 3), fmt(S["soa"], 4), fmt(T9["pulse_a"], 3), fmt(S["tmax"] * 1e3, 3), fmt(T9["sel_extrap"] * 100, 1)))
    p("     sensitivities: a steeper law past 10 ms (m 0.5) gives %s A (MEETS); the damp-heat row stacked instead of endurance: %s to %s ms, %s A (MEETS) (INFERRED);"
      % (fmt(T9["sel_soa_m05"], 4), fmt(T9["damp"][0] * 1e3, 3), fmt(T9["damp"][1] * 1e3, 3), fmt(T9["damp_soa"], 4)))
    p("     TI's own basis (typical values, 1.5 x the typical start): %s ms against %s ms (MEETS, INFERRED); the DC line derated, %s A, is under the pulse:"
      % (fmt(T9["typ_basis"][0] * 1e3, 3), fmt(T9["typ_basis"][1] * 1e3, 3), fmt(T9["dc_hot"], 4)))
    p("     the pulse is bounded by the fault time, not by a steady rating (INFERRED); F1 during the longest start: %s A2s against %s A2s (MEETS)"
      % (fmt(T9["f1_i2t_start"], 3), fmt(E["f1_i2t"], 0)))
    p("   D-09 stands for the LM5069 as drawn: the selected entry of 3c removes the LM5069 and its timer, so apply_gen_sch_e_timer.py is the alternative to")
    p("     apply_gen_sch_e_entry.py while the LM5069 stays, and the two drafts refuse each other (SESSION)")
    p("")
    p("8. THE DOWNSTREAM ITEMS (each with one owner and an acceptance; L4E11-SOURCE-ONLY-AND-ENTRY.md section 8 is the same table)")
    for it in downstream(R):
        p("   %s | %s | %s | %s" % (it[0], it[1], it[2], it[3]))
    p("")
    render_dependency(R, p)
    render_consolidation(R, p)
    render_fix(R, p)
    render_fix16(R, p)
    render_fix17(R, p)
    p("END. Desk arithmetic; nothing is measured. Drafts: apply_gen_sch_e_entry.py (the entry, 3c), apply_gen_sch_a_guard.py (R14, 3f),")
    p("apply_gen_sch_e_timer.py (C5 and C121, the alternative while the LM5069 stays), apply_gen_sch_a_charger.py (the BQ25730, its two")
    p("battery FETs and the dock's VSYS contact, 14 and 15), apply_gen_sch_e_aux.py and apply_pcb_interfaces_dock.py (board E's VSYS feed, 15a); the")
    p("first round's apply_gen_sch_e_uvlo.py is withdrawn; the knee is a specification (3f); the interface and firmware texts are drafts for Layer 5")
    p("in the record. Software tests establish this record's own behaviour only.")
    return "\n".join(out) + "\n"




def downstream(R):
    E, D, T9, N = R["E"], R["D"], R["T9"], R["N"]
    return [
    ("E11-01", "IMPLEMENTATION", "Layer 8 board E generator owner", "apply_gen_sch_e_entry.py applied after L4-E9's apply_gen_sch_e_hotswap.py, instead of apply_gen_sch_e_timer.py: U6 TPS48110AQDGXRQ1, Q7 CSD19536KTT, R19 4.5 mOhm, L2 SRF1260-1R0Y and the network of section 3c; the DGX-19 land added to meshsat.pretty from TI's DGX0019A drawing and the D2PAK land checked against TI's KTT drawing; _VEH_T restated to the breaker's %s A; the regenerated netlist reads every value of 3c" % fmt(N["ioc"][2], 2)),
    ("E11-02", "IMPLEMENTATION", "Layer 8 board A generator owner", "apply_gen_sch_a_guard.py applied together with the corrected knee (E11-09): R14 %sk (C23107); U34's fall recomputed from the fitted parts reads %s to %s V" % (fmt(GUARD_R14_K, 1), fmt(N["guard_new"][0][0], 2), fmt(N["guard_new"][0][2], 2))),
    ("E11-03", "INTERFACE", "Layer 5 interfaces", "FW-C08, FW-A14 and PANEL.md section 10 restated as the record's section 7a (rule R-a's state table: every charge hold by the CHRG_INHIBIT bit or ChargeCurrent 0, never by the CHG_INHIBIT line or SHORE_INHIBIT, and neither line asserted while the pack cannot discharge); DCIN_PGD restated as the entry's fault flag (FLT_I and FLT_T, low on a fault); REQ-046's hold still clears above 3 C"),
    ("E11-04", "FIRMWARE", "firmware owner", "rules R-a to R-d implemented (section 7a): R-a's state table with its S4 exception and the hold's persistence across states; R-b's two settings (ChargeCurrent() 0x0000 or 0x0200, no other) while U3's SRN reading is under %s V or the gauge reports XDSG or PRECHARGE; R-c's shed to the envelope at the measured input and the VSYS_UVP recovery; R-d; checked on the bench (E11-06)" % fmt(RULE_SRN_V, 1)),
    ("E11-05", "EVIDENCE", "Layer 6 components", "TI's answers filed: Q-TI-3 restated as N2 for state S2 (VSYS's regulation with CHRG_INHIBIT = 1 while the pack can take charge but cannot discharge, under a 5 A load step) and N1, and Q-TI-2; U-04's N1 to N3 re-judged on them; not needed once E11-27 is applied (SLUSE65A prints the bounds, section 12)"),
    ("E11-06", "TEST", "prototype bench", "R-85 extended: at 9.00 V at the plug with the interconnect at its resistance ceiling, and at 12 and 24 V: the shedding sequence of section 3g (P0 to P3) with the pack cold-soaked (S4), at a warm CUV (S2, the charge held by the bit: VSYS stays up) and absent; P1's load measured at most %s W at VBAT; the front end's efficiency at the operating point at least %s; U3's board current at the knee's flat target inside its band; the entry's current over the kit's load steps and source changes above the breaker's lowest %s A for less than %s ms and its filtered short-circuit sense under %s A; VSYS's step response; Q2's case at R-b's current; the latch recovery by a re-plug" % (fmt(N["shed_room"], 2), fmt(N["eta_floor"], 4), fmt(N["ioc"][0], 2), fmt(N["toc"][0] * 1e3, 3), fmt(N["isc"][0], 2))),
    ("E11-07", "ANALYSIS", "Layer 9 pre-layout analysis", "VSYS's effective capacitance at 16.884 V from the makers' DC-bias curves at least 50 uF (SLUSE66A 10.1), or the direct EEHZK1V181P of E11-24, which gives it by design (TI prefers POSCAP)"),
    ("E11-08", "EVIDENCE", "Layer 9 pre-layout analysis", "every load converter's and the controllers' minimum input read from their sheets against 10.0 V (A-14, R-49) and against 8.0 V for a pack at its Shutdown Voltage"),
    ("E11-09", "ANALYSIS", "Layer 4 coordinator", "L4-E5's undrawn H3 network drawn to section 3f's specification (flat %s A from VIN_RAW %s V to %s V, the knee slope kept, zero %s V, HIZ certain below %s V) with E11-02's guard; L4-E5's low-light settle, the solar line and its V-A09 sweep re-run on it" % (fmt(KNEE_IT, 2), fmt(KNEE_TOP, 2), fmt(N["v_join"], 3), fmt(N["v_zero"], 3), fmt(N["hiz_certain"], 3))),
    ("E11-10", "IMPLEMENTATION", "Layer 7 mechanical", "the DC receptacle and plug on MIL-DTL-38999 size 12 contacts (shell 17, insert 17-6: DC and solar pairs on four contacts, two unassigned between power and return; or 13-26 with the solar pair on rated contacts elsewhere), with the insert's installed continuous rating of at least 20 A at the case's air from the maker's derating, or a measured rise at 20 A, filed; the plate cut-out checked against CASE-MARGINS 3.3"),
    ("E11-11", "IMPLEMENTATION", "Layer 7 mechanical", "the DC interconnect specified by its loop, from the NATO plug's pins to J_DCIN's board pins: its reading, four-wire with the instrument and fixture within %s %% of reading and the conductor's temperature known within %s K, corrected to 20 C, between %s and %s mOhm on every assembly and every replacement (the actual floor %s mOhm keeps a stiff source under %s A); cores and the NATO plug with a maker's rating of at least 20 A; the sheets filed" % (fmt(U_MEAS * 100, 0), fmt(DT_MEAS, 0), fmt(N["acc"][0] * 1e3, 2), fmt(N["acc"][1] * 1e3, 2), fmt(N["loop_floor20"] * 1e3, 2), fmt(N["i_pf_spec"], 0))),
    ("E11-12", "IMPLEMENTATION", "Layer 7 mechanical", "the inside lead (a maker's rating of at least 20 A) and J_DCIN as a board connector rated at least 20 A (XT60 class, gender opposite J_BATT's, so the pack lead cannot mate it) or soldered lands; board E's generator names the part"),
    ("E11-13", "IMPLEMENTATION", "Layer 8 board E generator owner", "F1's holder: a MINI 297/997 holder whose maker prints a current rating of at least 20 A (the 3568 prints none); its sheet filed"),
    ("E11-14", "LAYOUT", "Layer 9 pre-layout analysis", "board E's copper from J_DCIN through F1 to D10, C4 and Q1 sized for 20 A continuous at the rise this project judges at, and Q7's D2PAK land with its copper"),
    ("E11-15", "IMPLEMENTATION", "Layer 8 board E generator owner", "pcb_energy_chain.yaml SHORE_INPUT restated with L4-E9's R-95: conductor %s A, the breaker's %s A, protects the interconnect, the prospective high %s A (the specified floor's worst case); the energy chain gate reads it" % (fmt(CONT_CLASS_A, 0), fmt(N["ioc"][2], 2), fmt(N["i_pf_spec"], 0))),
    ("E11-16", "EVIDENCE", "Layer 6 components", "F1's total clearing I2t at %s A and 58 V DC from Littelfuse (R-115), and against it, and against the monotone envelope (35 A for 5 s, 60 A for 0.5 s), the short-time withstand of every element the fault passes: the size 12 contacts, the NATO plug, the cable's and the inside lead's cores, J_DCIN, F1's holder and board E's copper to F1; filed" % fmt(N["i_pf_spec"], 0)),
    ("E11-17", "TEST", "prototype bench", "R-118 for the selected entry at 43 V, the TRIP THRESHOLDS apart from the PEAK CURRENTS: the start inside %s ms with at most %s A; the breaker's thresholds on a slow ramp (overcurrent %s to %s A after %s to %s ms, short circuit %s to %s A on the filtered sense); the peaks recorded and held under the chart: a start into a resistive fault near %s Ohm, a start into a hard short (at most %s A), Q7 unharmed; with the LM5069 kept, D-09's rows (the fault time inside %s to %s ms, the start inside %s ms)" % (fmt(N["t_start"] * 1e3, 2), fmt(N["inrush"][2], 2), fmt(N["ioc"][0], 2), fmt(N["ioc"][2], 2), fmt(N["toc"][0] * 1e3, 3), fmt(N["toc"][2] * 1e3, 3), fmt(N["isc"][0], 2), fmt(N["isc"][2], 2), fmt(N["scan"][1][1][1], 1), fmt(N["hs_start"][0], 0), fmt(T9["sel"]["tmin"] * 1e3, 3), fmt(T9["sel"]["tmax"] * 1e3, 3), fmt(T9["start_max"] * 1e3, 3))),
    ("E11-18", "DOCUMENT", "CONOPS owner", "the source-only statement in CONOPS (section 7b's text): with no usable pack the kit runs within the source envelope at the plug; a pack below about 2.4 V a cell holds VSYS under the converters' floor while it precharges; a brown-out on the source alone may latch the charger off until the source is re-plugged"),
    ("E11-19", "ANALYSIS", "Layer 4 coordinator", "L4-E9's entry findings that rest on the LM5069 (IF-05's hot short, D-07's power limit, R-118, the start's I2t) re-judged for the selected entry, with section 3c's figures"),
    ("E11-20", "EVIDENCE", "Layer 9 pre-layout analysis", "a hard short in service: the loop inductance from the source to a fault on DC_HS or VIN_RAW at least %s uH, or the peak through Q7 measured at most %s A (Q7's IDM derated), the trip threshold (%s to %s A) being only where the turn-off begins; with L4-E9's open item" % (fmt(N["l_min"] * 1e6, 2), fmt(N["i_allow"], 0), fmt(N["isc"][0], 2), fmt(N["isc"][2], 2))),
    ("E11-21", "INTERFACE", "Layer 4 coordinator", "L4-E5's V-A08 and its source-change transient row restated as the record's section 7a draft: the entry's breaker never trips (its current over %s A for less than %s ms, its filtered short-circuit sense under %s A) and VIN_RAW never under %s V (the guard's highest fall plus 0.1 V), in place of the LM5069's 3.13 ms timer and 8.41 V" % (fmt(N["ioc"][0], 2), fmt(N["toc"][0] * 1e3, 3), fmt(N["isc"][0], 2), fmt(N["guard_new"][0][2] + 0.1, 2))),
    ("E11-22", "EVIDENCE", "Layer 6 components", "R-b's cases (ii) and (iii) closed: the charger's temperature while R-b holds bounded inside %s to %s C (Layer 9 thermal), or TI's 0x0200 accuracy outside it and the clamp's maximum under VSYS_MIN (Q-TI), or the bench's current at 0x0200 and under VSYS_MIN at the inside air's ends; board P's copper under Q2 for TI's %s C/W" % (fmt(N["rb_temp"][0], 0), fmt(N["rb_temp"][1], 0), fmt(R["P"]["rja"]))),
    ("E11-23", "TEST", "prototype bench", "TEST-PLAN E4-O at the plug: the kit cold-soaked at -20 C with the pack inside, started from 9.00 V at the plug through the interconnect at its ceiling; the shedding sequence of section 3g runs, the mat on measured headroom: the cells reach 3 C, the hold clears and the charge begins; the time recorded and accepted against CONOPS's warm-up"),
    ("E11-24", "IMPLEMENTATION", "Layer 8 board A generator owner", "the dependency round's fallback on VBAT (a register row, never applied by this record): one EEHZK1V181P direct (C242139) and a hold-up bank of %d EEHZK1E471P (C242138) charged through R_CH %s Ohm RC2512FK-07330RL (C137025) and discharging through D_H B540C-13-F (C72264); the regenerated netlist carries them; the bank's hold recomputed from the fitted parts reads at least %s ms for the worst admitted step (%s W); withdrawn once E11-27 is applied (section 14: B1 carries the direct can, and the bank is not drawn)" % (BANK_N, fmt(R_CH, 0), fmt(R["G"]["worst_hold"] * 1e3, 3), fmt(R["G"]["worst"][1], 2))),
    ("E11-25", "EVIDENCE", "Layer 6 components", "the clarification questions of clarification/TI-QUESTIONS.md (Q-TI-11 to Q-TI-14 and the addendum to Q-TI-3) sent by the owner and answered, each answer filed against its dependency row D1 to D10 and judged: a limit closes a row production-wide, a typical figure does not"),
    ("E11-26", "TEST", "prototype bench", "the bench methods of rows D1 to D10 run on one unit each, every reading filed as a sample with its uncertainty and conditions, never as a limit; D2's recovery at most %s ms against the bank's %s ms assumption gives the engineering margin the record names" % (fmt(T_RESP * 1e3 / 5, 1), fmt(T_RESP * 1e3, 1))),
    ("E11-27", "IMPLEMENTATION", "Layer 8 board A generator owner", "apply_gen_sch_a_charger.py applied (sections 14 and 15): U3 BQ25730RSNR (%s) with pin 21 on CH_BATDRV; Q39 and Q40, two Nexperia BUK6Y10-30PX (%s) in parallel, sources on VBAT, drains on CH_BATQ, gates on CH_BATDRV; R17 and R149 on CH_BATQ; C236 EEHZK1V181P (C242139) on VBAT; U42 TPS16630PWPR from VBAT to VSYS_DOCK with R221 %sk 0.1 %%, C237 %s nF, MODE to GND, C238 1 uF at IN, C239 0.1 uF at OUT and D23 B540C from GND to OUT, within 20 nH of C236, J_DOCK pin 1 on VSYS_DOCK for board E's VSYS_E (section 16e), the HTSSOP-20 land checked against TI's PWP0020 drawing; CH_BATQ declared a segment of the pack path; the LFPAK56 lands checked against Nexperia's SOT669 drawing, seated by R17 with matched paths; the regenerated netlist reads each" % (R["H"]["cat"]["BQ25730RSNR"][0], R["K"]["cat"]["BUK6Y10-30PX"][0], fmt(F16_RILIM_K, 1), fmt(F16_CDVDT * 1e9, 0))),
    ("E11-28", "FIRMWARE", "firmware owner", "the BQ25730's register rules (section 14): EN_OOA 0 at boot; ChargeCurrent written for any charge (0 A at POR and after the watchdog's %s s), the watchdog serviced or WDTMR_ADJ 00; VSYS_MIN, EN_LDO, EN_PORT_CTRL, BATFET_ENZ and BATFETOFF_HIZ never written from their power-on values; the device ID %sh checked; R-a's bit following the hold flag in every state (S4's exception withdrawn); R-b' under VSYS_MIN: 0x0080 only, and no charge under %s V on SRN (section 15c)" % (fmt(R["H"]["wd_s"], 0), R["H"]["devid"], fmt(R["K"]["rb_floor"], 1))),
    ("E11-29", "LAYOUT", "Layer 9 pre-layout analysis", "the pair's copper sized before layout to the target below, and measured on the specimen of section 17 (a coupon or the controlled first prototype; it blocks only the final release): the installed pair Q39 and Q40 (section 16b), each FET's self impedance and the mutual one, junction to air by the body diode's VSD method on that specimen, at the +%s C mixed air or referred to it: (Zself + Zmut) at most %s K/W steady and at 60 s, %s at 1 s, %s at 20 ms and %s K/W at 244 us (at the allowance of E11-36); the 18 A for 60 s and 10 A continuous kept, no protection lowered; the case-rise reading at 10 A alone does not close it" % (fmt(R["K"]["air"]["route"], 0), fmt(R["L"]["plan"]["zsum"], 2), fmt(R["L"]["plan"]["ev"][0][4], 3), fmt(R["L"]["plan"]["ev"][1][4], 3), fmt(R["L"]["plan"]["ev"][2][4], 3))),
    ("E11-30", "EVIDENCE", "Layer 6 components", "the WHOLE hot docking waveform accepted (sections 16d and 17b): %s A peak, time constant %s us, from a +%s C mounting base, once per docking event, taken whole in one FET's body diode; by the pulse qualification selected in 17b: %d parts, each %d pulses %s s apart at %s A peak and %s us (x%s), mounting base %s C, every part passing VSD at 80 A pulsed within +5 %% of its first reading, IDSS at -30 V and 25 C at most the printed 1 uA, RDS(on) at -10 V and 25 C within +5 %% and at most the printed 10 mOhm, IGSS at most the printed 100 nA; or Nexperia's written acceptance of the same waveform (Q-NXP-1); a sample result is not a production limit; on a failure board P's owner bounds the inrush (a slower discharge-FET turn-on or a precharge path, its normal charging and its ASCD turn-off re-shown)" % (fmt(R["H"]["Q"]["i_dock"], 1), fmt(R["H"]["Q"]["tau"] * 1e6, 1), fmt(R["K"]["air"]["route"], 0), F17_DOCK_N[1], F17_DOCK_N[0], fmt(F17_DOCK_N[2], 0), fmt(R["M"]["dock_q"][0], 1), fmt(R["M"]["dock_q"][1] * 1e6, 1), fmt(F17_DOCK_MARGIN, 1), fmt(F17_TMB, 0))),
    ("E11-31", "TEST", "prototype bench", "the three modes on the BQ25730 build (EN_OOA 0), piecewise (section 15d): pack absent, VSYS at least %s V; CHRG_INHIBIT 1 with SRN over %s V, VSRN plus 150 mV within 2 percent, under %s V at least %s V, between at least %s V; the held pack current at most %s mA with board E on VSYS_E; the start from cold at VBUS20 %s and %s V, VSYS's maximum capacitance and the always-on loads, at -20, 25 and %s C, with Fault VSYS_UVP clear, the hiccup and latch on a shorted VSYS and the re-plug; VSYS before EN_OOA's write recorded; VSYS's step response in S2 and S4 for each declared step against the converters' floor (D2, %s V of margin), the outlets held by R-c where a step uses more" % (fmt(R["H"]["floor"], 3), fmt(R["K"]["hi_v"], 3), fmt(R["K"]["lo_v"], 3), fmt(R["H"]["floor"], 3), fmt(R["K"]["inh_floor"], 3), fmt(FIX_HELD_ACC * 1e3, 1), fmt(R["E"]["vb_low"], 2), fmt(R["E"]["vb_top"], 2), fmt(R["F"]["air_hot"], 1), fmt(R["H"]["margin_floor"], 3))),
    ("E11-32", "EVIDENCE", "Layer 6 components", "the BQ25730RSNR's supply for the build quantity from an authorised source, filed (LCSC stock %d on 2 October 2026), and the two battery FETs' (BUK6Y10-30PX, LCSC stock %d)" % (R["H"]["cat"]["BQ25730RSNR"][1], R["K"]["cat"]["BUK6Y10-30PX"][1])),
    ("E11-33", "IMPLEMENTATION", "Layer 8 board E generator owner", "apply_gen_sch_e_aux.py applied with E11-27 (section 15a): J_BLK pin 1 on VSYS_E; U12's VIN and EN, C31, J_FAN1 and J_FAN2 pin 1 and D7 and D8 on VSYS_E; VSYS_E declared (source J_BLK, %s A: U12 %s, the fans %s each, always on); CELL_F's loads the pack path alone; E6_SW, E6_BST and the fans' switched returns re-declared to VSYS's %s V; the regenerated netlist and check_contracts read the dock's pin 1 as VSYS_DOCK and VSYS_E" % (fmt(R["K"]["aux_a"], 2), fmt(R["K"]["aux"]["U12"], 2), fmt(R["K"]["aux"]["J_FAN1"], 2), fmt(R["H"]["vsys_top"], 3))),
    ("E11-34", "INTERFACE", "Layer 4 coordinator", "apply_pcb_interfaces_dock.py applied (IF-AE-DOCK: pin 1 VSYS_DOCK and VSYS_E behind U42's eFuse, the alias, BAT-F06's charge_share replaced by the VSYS feed, the ground return with seven 813 contacts) and section 15e's texts for L4-E9's record: the IF rows of VBAT and the dock, the source-change rows, the two sentences that say no battery FET and the diagram's system-node label (%s to %s V)" % (fmt(R["K"]["vsys_sup"], 3), fmt(R["H"]["vsys_top"], 3))),
    ("E11-35", "EVIDENCE", "Layer 6 components", "the mixer fans' supply range from their maker: at least %s V at the top (VSYS_E's top; CELL_F reached %s V) and running at %s V or less at the bottom (VSYS_E's least with 1.0 A, section 16e), and their starting current, with U12's 0.8 A, under U42's least limit %s A; or a fan of that range named" % (fmt(R["H"]["vsys_top"], 3), fmt(R["cv_max"], 3), fmt(R["L"]["vsys_e_min"], 3), fmt(R["L"]["ilim"][0], 3))),
    ("E11-36", "EVIDENCE", "Layer 6 components", "the battery FETs' RDS(on) at VGS -8.5 V and a 150 C junction at most %s mOhm (the allowance of section 16a): Nexperia's maximum at that point filed, or a pulsed Kelvin reading on parts from the build lot in an oven at 150 C (a sample, not a production limit: only the maker's maximum closes it for every part); a reading over it reverses the allowance and E11-29 is re-sized before layout" % fmt(F16_RA * 1e3, 3)),
    ("E11-37", "EVIDENCE", "Layer 6 components", "TI's statement of what the BATFET's 5 nF bounds (Ciss at which VDS, or a gate charge; Q-TI-17, drafted in clarification/TI-QUESTIONS.md, not sent), or the bench's BATDRV behaviour with the pair at -20, 25 and 70 C: supplement entry, the ideal diode's 30 mV regulation without oscillation and LDO mode at VSYS_MIN within its printed band; on a negative answer the engineer chooses between the pair and one FET with a heat path through the case (section 16c)"),
    ("E11-38", "TEST", "prototype bench", "the dock's VSYS branch, the whole fault envelope (sections 16e and 17a), at -20, 25 and 70 C and at VSYS 9.688 and 17.375 V, ten times each: (a) U42's limit on a slow ramp at VIN - VOUT 1 V between %s and %s A, and recorded at 17 V; (b) an operating overload (2.88 Ohm, and a load just under 2 x I(OL)): settled at or under %s A within 1 ms, off within %s ms, retry after %s to %s ms; (c) a 10 mOhm short applied at board E's VSYS_E while on: the peak through J_DOCK pin 1 at most %s A and over %s A for at most %s us, U42's IN at most 60 V, OUT's least recorded against -0.3 V (Q-TI-18); (d) a start into that short: at most %s A after the first 100 us, off within %s s; (e) one hour of retry into it at 70 C: the 813's body at most 85 C; for every case the 813's resistance at 1 A four-wire within +10 %% of its first reading and at most 20 mOhm, the plunger free, the 24 AWG's insulation and D23 (VF at 5 A within +5 %%) unchanged; (f) both fans and U12 started together and one at a time at VSYS 9.688 V: no limiting (FLT high), VSYS_E at least %s V" % (fmt(R["L"]["ilim"][0], 3), fmt(R["L"]["ilim"][1], 3), fmt(R["L"]["ilim"][1], 3), fmt(R["L"]["tcl"][1] * 1e3, 0), fmt(R["L"]["tretry"][0] * 1e3, 0), fmt(R["L"]["tretry"][1] * 1e3, 0), fmt(R["M"]["i_pk"], 0), fmt(R["M"]["fast_typ"], 1), fmt(R["L"]["tsoft"] * 1e6, 1), fmt(R["L"]["ilim"][1], 3), fmt(R["M"]["treg"][1], 1), fmt(R["M"]["vsys_e_lim"], 3))),
    ("E11-39", "FIRMWARE", "firmware owner", "board E's mixer fans started one at a time, each with a PWM ramp, never both within 1 s and never while U12 starts (section 17a: one fan's start at most %s A beside U12 and the other fan running, under U42's least limit %s A)" % (fmt(R["M"]["fan_stag"], 4), fmt(R["L"]["ilim"][0], 3))),
]


def main():
    try:
        os.nice(10)
    except OSError:
        pass
    sys.stdout.write(render(compute()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
