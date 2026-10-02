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
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a predicate this record rests on failed."""
import hashlib
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
}
INPUTS = ["lcsc-C907944-2026-10-02.json", "lcsc-C3847777-2026-10-02.json", "lcsc-C363929-2026-10-02.json",
          "lcsc-C3873338-2026-10-02.json", "jlc-search-c0g-150nf-2026-10-02.json", "murata-reference-sheets-2026-10-02.json",
          "ia-littelfuse-997-mini58v-20251210045250.json",
          "lcsc-C17556513-2026-10-02.json", "lcsc-C2687963-2026-10-02.json", "lcsc-C2985708-2026-10-02.json", "lcsc-C7084461-2026-10-02.json",
          "lcsc-C861872-2026-10-02.json", "lcsc-C97929-2026-10-02.json", "lcsc-C184799-2026-10-02.json", "lcsc-C23107-2026-10-02.json"]
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
SEL_CABLE_M = 3.0            # SESSION (D-06): the DC pair's run from the NATO plug to the kit's plug, at least
SEL_MM2 = AWG14_MM2          # SESSION (D-06): the class of core that fits a MIL-DTL-38999 size 12 crimp barrel
CONT_CLASS_A = 20.0          # SESSION (D-06): every element of the vehicle entry's interconnect rated at least this, continuous
R21_NEW_K = 42.2             # SESSION (U-04, finding U4-F2): E96 value; the rising UVLO's maximum under REQ-015's 9 V
PLUG_V = 9.0                 # REQ-015's floor, taken at the kit's plug (SESSION, the most demanding reading)
RULE_PRECHARGE_A = 1.0       # SESSION (U-04 rule R-b): ChargeCurrent while the pack may be held at its cutoff, at most
RULE_SRN_V = 14.0            # SESSION (U-04 rule R-b): the charger's own SRN reading under which R-b holds without the gauge's report
STEP_N = 40000               # the start integration's voltage steps (deterministic)
CAP_STACK_PARTS = 2          # SESSION (D-09): a timer capacitor of at most two parts in parallel
# ---- the fix round's own figures (2 October 2026, the focused check cx30's B1 to B5)
T_OUT_HOT = 40.0             # C, REQ-024's +40 C ambient for the outside cable (REQUIREMENT; sun loading not counted, named)
LOOP_CEIL = 0.05             # SESSION (D-06): the interconnect loop's resistance ceiling over the selected nominal at 20 C
HOLDER_R = 0.0010            # ohm, F1's holder (two clips): the 3568 prints nothing (ASSUMPTION)
BOARD_R = 0.0050             # ohm, board E's and board A's copper and the dock's VIN_RAW pins in the loop (ASSUMPTION)
FET_HOT = 1.8                # a MOSFET's RDS(on) at the hot end over its 25 C maximum (ASSUMPTION, for TJ up to about 125 C)
PIN_ERR = 0.200              # A, the ILIM_HIZ pin's error at R16 10 mOhm (INFERRED by L4-E5 from TI's 0.4 A at 5 mOhm)
NET_TOL = 0.01               # the knee network's error on the pin voltage (ASSUMPTION, L4-E5's 1 %)
KNEE_IT = 1.89               # A board current, SESSION (B3): the corrected H3's flat target, the functional state's need rounded up
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
        t = m.group(0)
        st = re.search(r"stroke:(rgb\([^)]*\))", t)
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
              "alpha", "lm5176", "srf1260", "yageo", "fuse997", "mur104", "mur683", "bq25798", "lm74700", "tps4811", "csd19536", "tps1663"):
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
    r20, r21, tol = f(m, 1) * 1e3, f(m, 3) * 1e3, f(m, 2) / 100.0

    def uvlo(r21x):
        rise = (uv[0] * (1 + r20 * (1 - tol) / (r21x * (1 + tol))), uv[1] * (1 + r20 / r21x), uv[2] * (1 + r20 * (1 + tol) / (r21x * (1 - tol))))
        fall = (rise[0] - hy[2] * r20 * (1 + tol), rise[1] - hy[1] * r20, rise[2] - hy[0] * r20 * (1 - tol))
        return rise, fall
    E["uv_rows"], E["hy_rows"] = uv, hy
    E["uvlo_drawn"] = uvlo(r21)
    E["uvlo_new"] = uvlo(R21_NEW_K * 1e3)
    E["r21"] = (r21, R21_NEW_K * 1e3)
    E["r20"] = r20
    if not E["uvlo_new"][0][2] < PLUG_V:
        refuse(4, "R21 %.1fk does not put the UVLO's maximum under %s V" % (R21_NEW_K, PLUG_V))
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
        t = m.group(0)
        st = re.search(r"stroke:(rgb\([^)]*\))", t)
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


def fault_scan(lines, vin, s, c, ioc, isc, toc, derate):
    """A start into a resistive fault Rf under gate-slew inrush and a circuit breaker (no power limit): the output follows the
    gate at the slew s (V/s), the FET carries c x s plus Vout / Rf with VIN - Vout across it, and it is turned off when the
    current reaches the short-circuit threshold or stays over the overcurrent threshold for the timer. Every point of the pulse
    is held against the line for the WHOLE pulse's duration (a conservative reading of a single-pulse chart: no thermal
    impedance superposition). Returns the worst ratio of current to the derated line, its Rf and its duration."""
    worst = (0.0, None, None)
    for k in range(241):
        rf = 10 ** (-1.0 + 4.0 * k / 240)
        i0 = c * s
        v_oc = max(0.0, (ioc - i0) * rf)
        v_sc = max(0.0, (isc - i0) * rf)
        v_end = min(vin, v_sc, (v_oc + s * toc) if v_oc < vin else vin)
        dur = max(v_end / s, 1e-6)
        r = 0.0
        for j in range(121):
            v = v_end * j / 120
            vds = vin - v
            if vds < 2.2:
                continue
            r = max(r, (i0 + v / rf) / (derate * soa_t(lines, vds, dur)))
        if r > worst[0]:
            worst = (r, rf, dur)
    return worst


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
    N["uvlo_drawn"] = uvlo(E["r21"][0])
    N["uvlo_withdrawn"] = uvlo(42.2e3)
    # ---- the kit's own series resistance, hot and cold (each element's class named in the output)
    rho_hot_out = CU_RHO_20 * (1 + CU_ALPHA * (T_OUT_HOT - 20.0))
    sel_r20 = (2 * SEL_CABLE_M + 2 * LEAD_M) * CU_RHO_20 / SEL_MM2
    N["loop_nom20"] = sel_r20
    N["loop_floor20"] = D["r_floor"] / (1 + CU_ALPHA * (T_COLD - 20.0))
    N["loop_ceil20"] = sel_r20 * (1 + LOOP_CEIL)
    out_share = SEL_CABLE_M / (SEL_CABLE_M + LEAD_M)
    N["cable_hot"] = N["loop_ceil20"] * (out_share * (1 + CU_ALPHA * (T_OUT_HOT - 20.0)) + (1 - out_share) * (1 + CU_ALPHA * (F["air_hot"] - 20.0)))
    N["c12_r"] = D["c12_mv"] * 1e-3 / D["c12"]
    xt = flat(pdf_pages("xt60", True)[0])
    N["xt60_r"] = f(need(xt, r"接触电阻 ([\d.]+)mΩ", "XT60 contact resistance")) * 1e-3
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
    N["func"] = tuple(x + N["heater_w"] for x in surv)
    N["surv"] = surv
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
    N["toc"] = (N["t48_tmr_v"][0] * c_lo / N["t48_tmr_i"][2], N["t48_tmr_v"][1] * en["ctmr"] / N["t48_tmr_i"][1], N["t48_tmr_v"][2] * c_hi / N["t48_tmr_i"][0])
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
    N["r_plug_dcp"] = [("the interconnect loop at its ceiling (%s m outside at %s C, %s m inside at %s C)" % (fmt(2 * SEL_CABLE_M, 1), fmt(T_OUT_HOT, 0), fmt(2 * LEAD_M, 1), fmt(F["air_hot"], 1)), N["cable_hot"], "SESSION ceiling, INFERRED"),
                       ("the D38999 size 12 pair (%s mV at %s A each)" % (fmt(D["c12_mv"], 0), fmt(D["c12"], 0)), 2 * N["c12_r"], "MAKER"),
                       ("the NATO plug's pair, taken as a size 12 contact each", 2 * N["c12_r"], "ASSUMPTION"),
                       ("J_DCIN of the XT60 class, two contacts", 2 * N["xt60_r"], "MAKER"),
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
    N["eta_break"] = E["eta_fe"] * N["i9"] / N["ioc"][0]
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
        lo_pw = lambda vv: (min(band(target(vv))[0], E["iin_min"]) + E["oth"]) * E["vb_low"] / E["eta_fe"]
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
    N["imax_all"] = max(e["i_max"] for e in env.values())
    if not N["imax_all"] < N["ioc"][0] or not N["ioc"][2] <= F["f_hot_a"]:
        refuse(4, "the breaker's band does not sit between the in-service maximum and F1's hot column")
    if not (N["uv_rise"][2] < N["dcp_noload"] and N["uv_fall"][2] < N["dcp9"] and N["top_margin"] > 0 and N["guard_margin"] >= 0.1):
        refuse(4, "an entry or knee threshold does not clear the 9.00 V plug's operating point")
    # ---- the owner-question caps with the losses (B3): F1's columns at a 9.00 V plug, the auxiliary loads taken off
    def cap(ia, rr):
        vr = PLUG_V - ia * rr
        return vr, (vr * ia * E["eta_fe"] - E["oth"] * E["vb_top"]) * E["eta_u3"]
    N["r_cold"] = (D["r_floor"] + 4 * N["c12_r"] + 2 * N["xt60_r"] + E["f1_rcold"] + HOLDER_R + N["q1_rds"] + rs_lo + N["q7_rds"]
                   + N["l2_dcr"] * (1 + CU_ALPHA * (T_COLD - 20.0)) + BOARD_R)
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
        worst = max((fault_scan(lines, D["vmax"], s, c, N["ioc"][2], N["isc"][2], N["toc"][2], T9["derate"]) + (s, c))
                    for s in (N["slew"][0], N["slew"][2]) for c in (N["c_load"][0], N["c_load"][2]))
        start = max(c * s / (T9["derate"] * soa_t(lines, D["vmax"], D["vmax"] / s)) for s in (N["slew"][0], N["slew"][2]) for c in (N["c_load"][0], N["c_load"][2]))
        scan.append((fet, worst, start))
    N["scan"] = scan
    N["hard_short_us"] = N["t48_tsc"][1] + 3.0 * en["riscp"] * en["cscp"]
    if not scan[1][1][0] < 1.0 or not scan[1][2] < 1.0:
        refuse(4, "the selected FET's fault start is not under its derated chart")
    # ---- B5: R-b's register value and its actual-current bound; the dead pack's charge
    bq = flat("".join(pdf_pages("bq25731", True)))
    m = need(bq, r"REG0x03/02\(\) = 0x0200H \S(\d+)% ([\d.]+)%", "the 0x0200 accuracy row")
    N["rb_err"] = (f(m, 1) / 100.0, f(m, 2) / 100.0)
    need(bq, r"With 5-m. sense resistor, the charger provides charge current range of 0 A to 16\.256 A, with a 128-mA step resolution", "the 5 mOhm LSB")
    need(bq, r"5-m. RSR sensing", "the accuracy rows' sense resistor")
    need(bq, r"VBAT above", "the accuracy rows' condition")
    N["rb_set"] = 1.024
    N["rb_max"] = N["rb_set"] * (1 + N["rb_err"][1]) / (1 - 0.01)
    N["rb_min"] = N["rb_set"] * (1 - N["rb_err"][0]) / (1 + 0.01)
    N["q2_w"] = N["rb_max"] * P["vsd_max"]
    N["q2_rise"] = N["q2_w"] * P["rja"]
    N["q2_tj"] = F["air_hot"] + N["q2_rise"]
    N["dead_charge_w"] = N["rb_max"] * RULE_SRN_V
    need(bq, r"Upon POR, ChargeCurrent\(\) is 0 A", "ChargeCurrent at POR")
    # ---- B4: the weak-source envelope as monotone intervals, its energies, and the elements' obligations
    tc = D["tc"]
    rating = D["rating"]
    edges = [rating * tc[1][0], rating * tc[2][0], rating * tc[3][0], rating * tc[4][0]]
    N["intervals"] = [(None, edges[0], None), (edges[0], edges[1], tc[1][2]), (edges[1], edges[2], tc[2][2]), (edges[2], edges[3], tc[3][2]), (edges[3], D["sel_ipf"], tc[4][2])]
    N["i2t_top"] = [(lo, hi, t, (hi ** 2 * t) if t else None) for lo, hi, t in N["intervals"]]
    s_cm2 = SEL_MM2 / 100.0
    N["adiab"] = [(lo, hi, t, hi * hi * t * CU_RHO_20 * 1e-4 / (s_cm2 ** 2 * CU_CV)) for lo, hi, t in N["intervals"][2:]]
    N["contact_eq"] = [(lo, hi, t, hi * hi * t / D["c12"] ** 2) for lo, hi, t in N["intervals"][1:4]]
    m = need(fz, r"Note: The typical I2t is an average value calculated from the breaking capacity tests by using the melting time before the arcing occurs\.", "the I2t note")
    N["f1_melt"] = E["f1_i2t"]
    return N


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
    p("     ChargeCurrent with the 5 mOhm RSR: 128 mA steps, 0 A at POR (9.6); REG0x03/02 = 0x0200 (1024 mA) regulates within -%s %% to +%s %%, a row printed for VBAT above VSYS_MIN (8.5, p.10) (MAKER)"
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
    p("       at R-b's %s A (below): at most %s W, %s K, so TJ %s C at the %s C inside air against %s C (MEETS, INFERRED)"
      % (fmt(N["rb_max"], 3), fmt(N["q2_w"], 3), fmt(N["q2_rise"], 1), fmt(N["q2_tj"], 1), fmt(F["air_hot"], 1), fmt(P["tj_max"], 0)))
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
    p("       ChargeCurrent crosses Q2's diode, so rule R-b holds ChargeCurrent() at 0x0200 (1024 mA set) or less (SESSION) while the charger's own SRN")
    p("       reading is under %s V or the gauge reports XDSG or PRECHARGE: at most %s A actual (+%s %% and R17 at -1 %%), at least %s A (MAKER row, INFERRED);"
      % (fmt(RULE_SRN_V, 1), fmt(N["rb_max"], 4), fmt(N["rb_err"][1] * 100, 1), fmt(N["rb_min"], 4)))
    p("       without the gauge's report it covers a cell up to %s V under the stack's average (%s V a cell at the threshold) (INFERRED); below VSYS_MIN the"
      % (fmt(P["rb_imbalance"], 2), fmt(P["rb_stack"] / P["cells"], 2)))
    p("       clamp is the limit TI states and its maximum is not printed: the setting's %s A is taken as the bound there too (CONDITIONAL; E11-06 measures it)" % fmt(N["rb_max"], 3))
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
    p("        the charge; no bit is set, so N2 does not arise here")
    p("     in S2 and S4 the CHG_INHIBIT line (HIZ, 9.3.8) and SHORE_INHIBIT each remove the kit's only supply: neither is ever a charge hold (rule R-a)")
    p("")
    p("3. U-04, THE ENTRY AT A 9.00 V PLUG, THE KIT'S OWN LOSSES AND THE SOURCE ENVELOPE (the focused check's B1 and B3)")
    p("   3a. the drawn LM5069 against a 9.00 V plug (finding U4-F2, corrected in the fix round)")
    p("     UVLOTH %s / %s / %s V, UVLOHYS %s / %s / %s uA (SNVS452G p.%d); Equations 38 to 40 (p.24): the falling threshold is UVLOTH x (1 + R20/R21),"
      % (tuple(fmt(x, 2) for x in E["uv_rows"]) + tuple(fmt(x * 1e6, 0) for x in E["hy_rows"]) + (E["uvlo_page"],)))
    p("       the rising one that plus UVLOHYS x R20 (MAKER); the first round put the hysteresis on the falling edge, so its numbers and its R21 draft were wrong")
    for lab, (rise, fall) in (("as drawn (R20 %sk, R21 %sk, 1 %%)" % (fmt(E["r20"] / 1e3, 0), fmt(E["r21"][0] / 1e3, 1)), N["uvlo_drawn"]), ("the withdrawn first-round draft (R21 42.2k)", N["uvlo_withdrawn"])):
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
    p("       the breaker's delay %s / %s / %s ms (CTMR with the GRM3195 family's rows, an ASSUMPTION for this part), retry %s s (INFERRED)"
      % (fmt(N["toc"][0] * 1e3, 3), fmt(N["toc"][1] * 1e3, 3), fmt(N["toc"][2] * 1e3, 3), fmt(N["tretry"], 2)))
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
    p("     A START INTO A RESISTIVE FAULT (Rf 0.1 to 1000 Ohm on VIN_RAW at %s V; the breaker at its slowest: overcurrent %s A for %s ms, short circuit %s A; both"
      % (fmt(D["vmax"], 2), fmt(N["ioc"][2], 2), fmt(N["toc"][2] * 1e3, 3), fmt(N["isc"][2], 2)))
    p("       slew and capacitance corners; every point held against the chart for the whole pulse, conservative, no thermal-impedance superposition) (INFERRED):")
    for fet, (r, rf, dur, s, c), start in N["scan"]:
        p("       %-24s worst %s of the derated chart at Rf %s Ohm, %s ms (slew %s V/ms, %s uF); the start itself %s: %s"
          % (fet, fmt(r, 3), fmt(rf, 2), fmt(dur * 1e3, 3), fmt(s / 1e3, 2), fmt(c * 1e6, 1), fmt(start, 3), "MEETS" if r < 1.0 and start < 1.0 else "NOT MET"))
    p("       a hard short at the start reaches the short-circuit threshold inside the 100 us line; in service the breaker opens within %s us (tSC with CSCP's"
      % fmt(N["hard_short_us"] * 1e6, 1))
    p("       filter): the peak before it is set by the loop's inductance, which no document gives (L4-E9's open item, carried) (CONDITIONAL)")
    p("   3d. the kit's series resistance from the plug, at the hot end (the low side of the envelope and the in-service maximum):")
    for n, x, cl in N["r_plug_dcp"] + N["r_dcp_vin"]:
        p("     %-104s %s mOhm (%s)" % (n, fmt(x * 1e3, 3), cl))
    p("     the plug to DC_P %s mOhm, DC_P to VIN_RAW %s mOhm, %s mOhm in all (INFERRED); the first round's model (%s mOhm at 20 C) left out the hot values and the contacts"
      % (fmt(N["r1_hot"] * 1e3, 2), fmt(N["r2_hot"] * 1e3, 2), fmt(N["r_hot"] * 1e3, 2), fmt(E["r_plug"]["selected"] * 1e3, 3)))
    p("   3e. the in-service maximum at a 9.00 V plug (the corrected knee's high band, VBUS20 at %s V, the front end at %s, the losses hot) (INFERRED):"
      % (fmt(E["vb_top"], 2), fmt(E["eta_fe"], 2)))
    p("     VIN_RAW %s V, %s A from the plug, DC_P %s V; against the selected entry:" % (fmt(N["vin9"], 3), fmt(N["i9"], 3), fmt(N["dcp9"], 3)))
    p("       UVLO: its highest rise %s V against DC_P at %s V or more before any current flows (MEETS); its highest fall %s V against DC_P %s V in service (MEETS)"
      % (fmt(N["uv_rise"][2], 2), fmt(N["dcp_noload"], 3), fmt(N["uv_fall"][2], 2), fmt(N["dcp9"], 2)))
    p("       overcurrent: %s A at its lowest against %s A, %s %% in hand; the front end's efficiency at 8.1 V must be %s or more (C-8, CONDITIONAL)"
      % (fmt(N["ioc"][0], 3), fmt(N["i9"], 3), fmt(N["ioc_margin"] * 100, 1), fmt(N["eta_break"], 3)))
    p("       F1: the breaker's highest %s A against its %s C column %s A (MEETS, MAKER); L2 at %s A: %s K over the %s C air, %s C under its 105 C (MEETS, MAKER)"
      % (fmt(N["ioc"][2], 3), fmt(F["f_col"], 0), fmt(F["f_hot_a"], 1), fmt(N["ioc"][2], 2), fmt(N["l2_rise"], 1), fmt(F["air_hot"], 1), fmt(F["air_hot"] + N["l2_rise"], 1)))
    p("       Q7 at %s A: %s W (INFERRED); the highest in-service current over 9 to 36 V is the 9 V one, %s A (INFERRED)" % (fmt(N["ioc"][2], 2), fmt(N["q7_w"], 3), fmt(N["imax_all"], 3)))
    p("   3f. THE CORRECTED KNEE (SESSION, specification for L4-E5's undrawn network) AND THE RESTART GUARD (draft apply_gen_sch_a_guard.py):")
    p("     flat target %s A of board current (the pin at %s V) from VIN_RAW %s V up to %s V, where L4-E5's line (%s A/V) takes over; below %s V L4-E5's knee slope"
      % (fmt(KNEE_IT, 2), fmt(1 + 0.4 * KNEE_IT, 3), fmt(KNEE_TOP, 2), fmt(N["v_join"], 3), fmt(E["slope"] / 0.4, 6), fmt(KNEE_TOP, 2)))
    p("       (%s V/V at the pin): zero at %s V, HIZ entry %s V, exit %s V; with L4-E5's +-%s %% the knee's top is at most %s V, %s V under the 9 V plug's VIN_RAW,"
      % (fmt(N["knee_slope"], 3), fmt(N["v_zero"], 3), fmt(N["v_hiz_in"], 3), fmt(N["v_hiz_out"], 3), fmt(N["knee_tol"] * 100, 2), fmt(N["top_max"], 3), fmt(N["top_margin"], 3)))
    p("       and HIZ is certain below %s V (SESSION, INFERRED); the functional need sets the target at %s A or more (3g)" % (fmt(N["hiz_certain"], 3), fmt(N["it_need"], 4)))
    p("     the guard (U34, board A): R14 %sk over R15 %sk as drawn falls at %s / %s / %s V; R14 %sk: falls at %s / %s / %s V and rises at %s / %s / %s V (SNVSBJ1E, INFERRED)"
      % ((fmt(N["guard_r"][0] / 1e3, 0), fmt(N["guard_r"][1] / 1e3, 0)) + tuple(fmt(x, 3) for x in N["guard_drawn"][0]) + (fmt(GUARD_R14_K, 1),)
         + tuple(fmt(x, 3) for x in N["guard_new"][0]) + tuple(fmt(x, 3) for x in N["guard_new"][1])))
    p("       %s V under the knee's certain HIZ (L4-E5's rule: 0.1 V or more; MEETS); at its lowest fall the running levels scale to FE_VZ %s V, FE_RUN %s V"
      % (fmt(N["guard_margin"], 3), fmt(N["guard_levels"][0], 2), fmt(N["guard_levels"][1], 2)))
    p("       (Q36 and Q37 need %s V at most) and EN %s V (VEN(OP) %s V at most): MEETS (INFERRED: the network is resistive under the zener's knee)"
      % (fmt(N["guard_levels"][2], 1), fmt(N["guard_levels"][3], 2), fmt(N["ven_op"], 2)))
    p("   3g. THE FUNCTIONAL WARM-UP AT A 9.00 V PLUG (B3): REQ-024's start with the pack cold-soaked (both FETs open), REQ-046's heater before any charge, the charge")
    p("     held and the charger carrying the kit (REQ-077), done by the bridge on one module: PS-SURV, slot 2 alone (hc2 pwr_red2.out: %s / %s / %s W) with the heater"
      % tuple(fmt(x, 2) for x in N["surv"]))
    p("     (%s W, its overlay on PS-IDLE-SPEC): %s / %s / %s W at VBAT (RECORD; SESSION: the least state that performs the sequence)" % ((fmt(N["heater_w"], 2),) + tuple(fmt(x, 2) for x in N["func"])))
    p("     at 9.00 V at the plug, hot: %s to %s W delivered (3h): the plan figure is carried at every corner (MEETS); its hi corner (%s W) is not, by %s W: there"
      % (fmt(N["env"][9.0]["w_lo"], 2), fmt(N["env"][9.0]["w_hi"], 2), fmt(N["func"][2], 2), fmt(N["func"][2] - N["env"][9.0]["w_hi"], 2)))
    p("       rule R-c's shed applies (the heater cycled or the module's radios held; CONDITIONAL on the measured state, E11-06) (INFERRED)")
    p("   3h. THE SOURCE ENVELOPE AT THE PLUG (the low side with the losses hot and VBUS20 at %s V, the high side with no loss and %s V; U3 %s) (INFERRED):"
      % (fmt(E["vb_low"], 3), fmt(E["vb_top"], 2), fmt(E["eta_u3"], 4)))
    p("   plug | VIN_RAW at the low side | U3 board current, A | at VBAT, W | L4-E9 at VIN_RAW (no loss) (INFERRED)")
    for v in (9.0, 12.0, 24.0, 36.0):
        e = N["env"][v]
        l9 = {9.0: "%s to %s W" % (fmt(E["l9"]["min9"], 1), fmt(E["l9"]["max9"], 1)), 12.0: "up to %s W" % fmt(E["l9"]["max12"], 1), 24.0: "up to %s W" % fmt(E["l9"]["max24"], 1), 36.0: "(the window)"}[v]
        p("     %5s V | %s V | %s to %s | %s to %s | %s" % (fmt(v, 1), fmt(e["vin_lo"], 3), fmt(e["board_lo"], 3), fmt(e["board_hi"], 3), fmt(e["w_lo"], 2), fmt(e["w_hi"], 2), l9))
    p("   the states at their plan figure against it:")
    for name, (lo, plan, hi) in list(E["states"].items()) + [("the functional warm-up", N["func"])]:
        key = name if name != "the functional warm-up" else "the functional warm-up (one module and the heater)"
        cl = " | ".join("%s V: %s" % (fmt(v, 0), N["cls"][(key, v)]) for v in (9.0, 12.0, 24.0, 36.0))
        p("     %-32s %s W | %s (RECORD, INFERRED)" % (name, fmt(plan, 2), cl))
    p("   a dead pack's charge on top: at most %s A x %s V = %s W under R-b (section 2), taken only from what DPM leaves after the system (9.3.17): it never" % (fmt(N["rb_max"], 3), fmt(RULE_SRN_V, 1), fmt(N["dead_charge_w"], 2)))
    p("     pushes the kit out of the envelope (INFERRED; the first round's 4.22 W took the typical 384 mA as a bound and is withdrawn)")
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
    p("   a mandatory requirement naming a load state for source-only operation: %s (section 1); the functional warm-up of 3g is carried at its plan figure" % ("yes" if F["owner_question"] else "none"))
    p("   what the source path itself admits at a 9.00 V plug, the kit's losses included and VBUS20's other loads taken off (INFERRED; the first round's")
    p("     %s / %s / %s W left the losses out):" % (fmt(F["cap9_hot_w"], 1), fmt(F["cap9_cold_w"], 1), fmt(F["cap9_15a_hot_w"], 1)))
    for lab, ia, rr, vr, w in N["caps"]:
        p("     %-46s %s mOhm: VIN_RAW %s V, %s W at VBAT (MAKER, INFERRED)" % (lab, fmt(rr * 1e3, 2), fmt(vr, 3), fmt(w, 2)))
    p("     (the check's reference, 115.511 mOhm with no auxiliary load: " + ", ".join("%s A %s W" % (fmt(ia, 1), fmt(w, 2)) for ia, w in N["check_ref"]) + ")")
    p("   these are the path's ceilings with the electronics set to use all of them; the breaker's band and the knee's spread keep the least delivered")
    p("     figure lower (3h: %s W at 9 V) (INFERRED). REQ-015 states no source current capability: every figure takes the source as holding its voltage (named)" % fmt(N["env"][9.0]["w_lo"], 2))
    p("   so NO owner question is forced: no approved requirement names a load REQ-015's 9 V must carry beyond the functional sequence, which 3c to 3g carry at its")
    p("     plan figure; PS-TYP %s W and the CONOPS cold warm-up %s W exceed every 9 V ceiling above, a design envelope and not a requirement conflict (INFERRED)"
      % (fmt(E["states"]["PS-TYP"][1], 2), fmt(E["states"]["the cold warm-up (CONOPS 4c)"][1], 2)))
    p("")
    p("6. D-06, F1'S WEAK-SOURCE BAND AND THE INTERCONNECT")
    p("   0997010.WXN time-current (MAKER, held sheet p.3): " + "; ".join("%s %%: %s to %s s" % (fmt(pct * 100, 0), fmt(tmin, 2), "-" if tmax is None else fmt(tmax, 2)) for pct, tmin, tmax in D["tc"]))
    p("   the envelope a source can leave, read monotone (a larger current clears no later than a smaller one; INFERRED), with each interval's top I2t:")
    for lo, hi, tt, i2t in N["i2t_top"]:
        if tt is None:
            p("     up to %s A: no maximum time printed: carried with no time limit" % fmt(hi, 1))
        elif hi == D["sel_ipf"]:
            p("     from %s A up to the declared prospective %s A: at most %s s by the 600 %% row, which bounds the energy only by %s A2s; F1's total clearing"
              % (fmt(lo, 1), fmt(hi, 1), fmt(tt, 2), fmt(i2t, 0)))
            p("       I2t at 58 V DC is not printed (the sheet's %s A2s is a typical melting figure from its breaking tests), so above %s A the elements are judged"
              % (fmt(N["f1_melt"], 0), fmt(lo, 0)))
            p("       against F1's total clearing I2t once filed (R-115, E11-16) (MAKER, INFERRED)")
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
        p("     %s A for %s s: %s K%s (INFERRED)" % (fmt(hi, 1), fmt(tt, 2), fmt(dt, 2), "; the monotone bound only, F1's clearing I2t decides it" if hi == D["sel_ipf"] else ""))
    p("   and against the size 12 contact's %s A, which Amphenol prints as a crimp-contact test current (p.%d), not an installed rating: the same I2t as %s"
      % (fmt(D["c12"], 0), D["d38999_p"], "; ".join("%s A for %s s = %s s at %s A" % (fmt(hi, 0), fmt(tt, 2), fmt(e, 3), fmt(D["c12"], 0)) for lo, hi, tt, e in N["contact_eq"][1:])))
    p("     (INFERRED; the contact's installed continuous rating and its short-time limit are not printed: E11-10 and E11-16)")
    p("   THE INTERCONNECT BY ITS RESISTANCE (SESSION; the minor on A11-1: a larger or purer conductor raises a stiff fault, so the check rests on a measured floor,")
    p("     not on copper constants): the loop from the plug's pins to J_DCIN, both conductors and the inside lead, at least %s mOhm at 20 C (the floor's %s mOhm"
      % (fmt(N["loop_floor20"] * 1e3, 2), fmt(D["r_floor"] * 1e3, 2)))
    p("     at %s C) and at most %s mOhm at 20 C (the selected %s mOhm plus %s %%, the 9 V envelope's basis), measured four-wire on every assembly and"
      % (fmt(T_COLD, 0), fmt(N["loop_ceil20"] * 1e3, 2), fmt(N["loop_nom20"] * 1e3, 2), fmt(LOOP_CEIL * 100, 0)))
    p("     replacement (E11-11); 3.0 m of AWG 14 with the 0.5 m lead is one construction inside it (INFERRED)")
    p("   THE STIFF SOURCE AGAIN (copper alone at %s C, the source's own resistance zero, A-12; at the OVLO maximum %s V):" % (fmt(T_COLD, 0), fmt(D["vmax"], 2)))
    for lab, rr, ipf in D["stiff"]:
        p("     %-48s %s ohm, %s A against %s A: %s (INFERRED)" % (lab, fmt(rr, 5), fmt(ipf, 1), fmt(D["interrupt_a"], 0), "MEETS" if ipf <= D["interrupt_a"] else "NOT MET"))
    p("   so a heavier interconnect needs a resistance floor: at least %s ohm of copper loop at %s C, which AWG 14 gives from %s m of cable"
      % (fmt(D["r_floor"], 5), fmt(T_COLD, 0), fmt(D["min_len_14"], 2)))
    p("     with the 0.5 m lead; SESSION: the DC pair's run at least %s m (%s A); a shorter or heavier lead needs a fuse with a larger interrupting"
      % (fmt(SEL_CABLE_M, 1), fmt(D["sel_ipf"], 1)))
    p("     rating at 58 V DC, of which no sheet is held (named)")
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
    p("END. Desk arithmetic; nothing is measured. Drafts: apply_gen_sch_e_entry.py (the entry, 3c), apply_gen_sch_a_guard.py (R14, 3f),")
    p("apply_gen_sch_e_timer.py (C5 and C121, the alternative while the LM5069 stays); the first round's apply_gen_sch_e_uvlo.py is withdrawn; the")
    p("knee is a specification (3f); the interface and firmware texts are drafts for Layer 5 in the record. Software tests establish this record's")
    p("own behaviour only.")
    return "\n".join(out) + "\n"




def downstream(R):
    E, D, T9, N = R["E"], R["D"], R["T9"], R["N"]
    return [
    ("E11-01", "IMPLEMENTATION", "Layer 8 board E generator owner", "apply_gen_sch_e_entry.py applied after L4-E9's apply_gen_sch_e_hotswap.py, instead of apply_gen_sch_e_timer.py: U6 TPS48110AQDGXRQ1, Q7 CSD19536KTT, R19 4.5 mOhm, L2 SRF1260-1R0Y and the network of section 3c; the DGX-19 land added to meshsat.pretty from TI's DGX0019A drawing and the D2PAK land checked against TI's KTT drawing; _VEH_T restated to the breaker's %s A; the regenerated netlist reads every value of 3c" % fmt(N["ioc"][2], 2)),
    ("E11-02", "IMPLEMENTATION", "Layer 8 board A generator owner", "apply_gen_sch_a_guard.py applied together with the corrected knee (E11-09): R14 %sk (C23107); U34's fall recomputed from the fitted parts reads %s to %s V" % (fmt(GUARD_R14_K, 1), fmt(N["guard_new"][0][0], 2), fmt(N["guard_new"][0][2], 2))),
    ("E11-03", "INTERFACE", "Layer 5 interfaces", "FW-C08, FW-A14 and PANEL.md section 10 restated as the record's section 7a (rule R-a's state table: every charge hold by the CHRG_INHIBIT bit or ChargeCurrent 0, never by the CHG_INHIBIT line or SHORE_INHIBIT, and neither line asserted while the pack cannot discharge); DCIN_PGD restated as the entry's fault flag (FLT_I and FLT_T, low on a fault); REQ-046's hold still clears above 3 C"),
    ("E11-04", "FIRMWARE", "firmware owner", "rules R-a to R-d implemented (section 7a): R-a's state table; R-b's ChargeCurrent() at 0x0200 or less while U3's SRN reading is under %s V or the gauge reports XDSG or PRECHARGE; R-c's shed to the envelope at the measured input and the VSYS_UVP recovery; R-d; checked on the bench (E11-06)" % fmt(RULE_SRN_V, 1)),
    ("E11-05", "EVIDENCE", "Layer 6 components", "TI's answers filed: Q-TI-3 restated as N2 for state S2 (VSYS's regulation with CHRG_INHIBIT = 1 while the pack can take charge but cannot discharge, under a 5 A load step) and N1, and Q-TI-2; U-04's N1 to N3 re-judged on them"),
    ("E11-06", "TEST", "prototype bench", "R-85 extended: at 9.00 V at the kit's plug with the interconnect at its resistance ceiling, and at 12 and 24 V: the functional warm-up of section 3g with the pack cold-soaked (S4), at a warm CUV (S2, the charge held by the bit: VSYS stays up) and absent; the entry starts and does not trip (the front end's input under %s A); VSYS's step response; Q2's case at R-b's current; the latch recovery by a re-plug" % fmt(N["ioc"][0], 2)),
    ("E11-07", "ANALYSIS", "Layer 9 pre-layout analysis", "VSYS's effective capacitance at 16.884 V from the makers' DC-bias curves at least 50 uF (SLUSE66A 10.1), else a polymer capacitor added (TI prefers POSCAP)"),
    ("E11-08", "EVIDENCE", "Layer 9 pre-layout analysis", "every load converter's and the controllers' minimum input read from their sheets against 10.0 V (A-14, R-49) and against 8.0 V for a pack at its Shutdown Voltage"),
    ("E11-09", "ANALYSIS", "Layer 4 coordinator", "L4-E5's undrawn H3 network drawn to section 3f's specification (flat %s A from VIN_RAW %s V to %s V, the knee slope kept, zero %s V, HIZ certain below %s V) with E11-02's guard; L4-E5's low-light settle and the solar line re-run on it" % (fmt(KNEE_IT, 2), fmt(KNEE_TOP, 2), fmt(N["v_join"], 3), fmt(N["v_zero"], 3), fmt(N["hiz_certain"], 3))),
    ("E11-10", "IMPLEMENTATION", "Layer 7 mechanical", "the DC receptacle and plug on MIL-DTL-38999 size 12 contacts (shell 17, insert 17-6: DC and solar pairs on four contacts, two unassigned between power and return; or 13-26 with the solar pair on rated contacts elsewhere), with the insert's installed continuous rating of at least 20 A at the case's air from the maker's derating, or a measured rise at 20 A, filed; the plate cut-out checked against CASE-MARGINS 3.3"),
    ("E11-11", "IMPLEMENTATION", "Layer 7 mechanical", "the DC interconnect specified by its loop resistance, plug pins to J_DCIN with the inside lead: at least %s mOhm and at most %s mOhm at 20 C, measured four-wire on every assembly and every replacement; cores with a maker's rating of at least 20 A each; the NATO plug with a maker's rating of at least 20 A; the sheets filed" % (fmt(N["loop_floor20"] * 1e3, 2), fmt(N["loop_ceil20"] * 1e3, 2))),
    ("E11-12", "IMPLEMENTATION", "Layer 7 mechanical", "the inside lead (a maker's rating of at least 20 A) and J_DCIN as a board connector rated at least 20 A (XT60 class, gender opposite J_BATT's, so the pack lead cannot mate it) or soldered lands; board E's generator names the part"),
    ("E11-13", "IMPLEMENTATION", "Layer 8 board E generator owner", "F1's holder: a MINI 297/997 holder whose maker prints a current rating of at least 20 A (the 3568 prints none); its sheet filed"),
    ("E11-14", "LAYOUT", "Layer 9 pre-layout analysis", "board E's copper from J_DCIN through F1 to D10, C4 and Q1 sized for 20 A continuous at the rise this project judges at, and Q7's D2PAK land with its copper"),
    ("E11-15", "IMPLEMENTATION", "Layer 8 board E generator owner", "pcb_energy_chain.yaml SHORE_INPUT restated with L4-E9's R-95: conductor %s A, the breaker's %s A, protects the interconnect, the prospective high %s A; the energy chain gate reads it" % (fmt(CONT_CLASS_A, 0), fmt(N["ioc"][2], 2), fmt(D["sel_ipf"], 1))),
    ("E11-16", "EVIDENCE", "Layer 6 components", "the size 12 contact's, the board connector's and the cable's short-time withstand against the monotone envelope (35 A for 5 s, 60 A for 0.5 s) and F1's total clearing I2t at 58 V DC from 60 A to %s A (Littelfuse, R-115) against each of them, filed" % fmt(D["sel_ipf"], 1)),
    ("E11-17", "TEST", "prototype bench", "R-118 for the selected entry at 43 V: the start inside %s ms with the inrush at most %s A, a start into a resistive fault near %s Ohm and a hard short, the breaker opening at %s to %s A, Q7 unharmed; with the LM5069 kept instead, D-09's rows (the fault time inside %s to %s ms, the start inside %s ms)" % (fmt(N["t_start"] * 1e3, 2), fmt(N["inrush"][2], 2), fmt(N["scan"][1][1][1], 1), fmt(N["isc"][0], 2), fmt(N["isc"][2], 2), fmt(T9["sel"]["tmin"] * 1e3, 3), fmt(T9["sel"]["tmax"] * 1e3, 3), fmt(T9["start_max"] * 1e3, 3))),
    ("E11-18", "DOCUMENT", "CONOPS owner", "the source-only statement in CONOPS (section 7b's text): with no usable pack the kit runs within the source envelope at the plug; a pack below about 2.4 V a cell holds VSYS under the converters' floor while it precharges; a brown-out on the source alone may latch the charger off until the source is re-plugged"),
    ("E11-19", "ANALYSIS", "Layer 4 coordinator", "L4-E9's entry findings that rest on the LM5069 (IF-05's hot short, D-07's power limit, R-118, the start's I2t) re-judged for the selected entry, with section 3c's figures"),
    ("E11-20", "EVIDENCE", "Layer 9 pre-layout analysis", "the loop inductance from the source to Q7, so the hot-short peak before the breaker opens (within %s us) is bounded, with L4-E9's open item" % fmt(N["hard_short_us"] * 1e6, 1)),
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
