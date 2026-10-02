#!/usr/bin/env python3
"""l4e11_power.py: layer 4 task L4-E11 (MESHSAT-1357, 2 October 2026). Three items the connected power architecture (L4-E9)
left open, resolved as engineering choices with their bounds:

  U-04  source-only and dead-pack operation (the kit on a vehicle or shore source with the pack absent, at or below its
        protection cutoff, or with its FETs open);
  D-06  the vehicle-entry interconnect in F1's long-time band from a weak source;
  D-09  the hot swap's fault time against its own start into VIN_RAW (added by the coordinator on 2 October 2026).

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
}
INPUTS = ["lcsc-C907944-2026-10-02.json", "lcsc-C3847777-2026-10-02.json", "lcsc-C363929-2026-10-02.json",
          "lcsc-C3873338-2026-10-02.json", "jlc-search-c0g-150nf-2026-10-02.json", "murata-reference-sheets-2026-10-02.json",
          "ia-littelfuse-997-mini58v-20251210045250.json"]
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
              "alpha", "lm5176", "srf1260", "yageo", "fuse997", "mur104", "mur683", "bq25798"):
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
    P["q2"] = [(i, i * P["vsd_max"], i * P["vsd_max"] * P["rja"]) for i in (B["iclamp"], RULE_PRECHARGE_A, 3.0)]
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
    return R


# ============================================================================================ the output
def render(R):
    out = []
    p = out.append
    B, P, E, C, F, D, T9 = R["B"], R["P"], R["E"], R["C"], R["F"], R["D"], R["T9"]
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
    p("     4S defaults: ChargeVoltage %s V, SYSOVP %s V, VSYS_MIN %s V (Table 9-2, p.%d); below VSYS_MIN at SRN the charge is clamped at %s mA (8.5, p.%d) (MAKER)"
      % (fmt(B["cv4s"]), fmt(B["sysovp4s"]), fmt(B["vsysmin4s"]), B["t92"], fmt(B["iclamp"] * 1000), B["iclamp_p"]))
    p("     with charge disabled \"the converter should keep operating without disturbance\" (9.3.21.5, BATOVP, p.%d) (MAKER)" % B["batovp"])
    p("     HIZ: \"converter shuts off\" with ILIM_HIZ under %s V (9.3.8, p.%d) (MAKER)" % (fmt(B["hiz_v"]), B["hiz_p"]))
    p("     VSYS under %s V for 2 ms in steady state: \"shut down and latched off\" until a host write (9.3.21.8, p.%d) (MAKER)" % (fmt(B["uvp_v"]), B["uvp_p"]))
    p("     \"Overall %s-uF effective capacitance on VSYS net is necessary\" (10.1, p.%d); CHRG_INHIBIT \"1b: Inhibit Charge\" (p.%d); the host ends a charge by CHRG_INHIBIT or ChargeCurrent 0 (9.4.1, p.%d) (MAKER)"
      % (fmt(B["csys_uf"]), B["csys_p"], B["inhibit_p"], B["term_p"]))
    p("     AUTO_WAKEUP_EN, 0 at POR: with it set, a battery under VSYS_MIN gets %s mA for %s min with no further host write (p.%d) (MAKER); it needs a host write first, so it does not answer N3"
      % (fmt(B["wake_ma"]), fmt(B["wake_min"]), B["wake_p"]))
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
    p("       ChargeCurrent crosses Q2's diode, so rule R-b caps it at %s A (SESSION; %s W at most, above) while the charger's own SRN reading is under %s V"
      % (fmt(RULE_PRECHARGE_A), fmt(RULE_PRECHARGE_A * P["vsd_max"]), fmt(RULE_SRN_V, 1)))
    p("       or the gauge reports XDSG or PRECHARGE: without the gauge's report it covers a cell up to %s V under the stack's average (%s V a cell at the threshold) (INFERRED)"
      % (fmt(P["rb_imbalance"], 2), fmt(P["rb_stack"] / P["cells"], 2)))
    p("     CHG_INHIBIT (HIZ) or SHORE_INHIBIT asserted while the pack cannot discharge: the converter is off, so VSYS has no source and the")
    p("       kit stops; the controllers die, the pull-downs release the line and the kit restarts: a loop (INFERRED: 9.3.8, the UVLO, the netlists)")
    p("     FW-C08 asserts SHORE_INHIBIT below 0 C: with a pack below %s C the source start REQ-024 requires is cut by the hold itself (finding U4-F1, INFERRED)" % fmt(P["utd"]))
    p("   NOT STATED in any held document (named, not inferred): N1 VSYS's regulation and transient response with no battery under the")
    p("     kit's load steps; N2 what the converter regulates with CHRG_INHIBIT = 1 or ChargeCurrent 0 and no battery current (Q-TI-3);")
    p("     N3 whether the charger charges before any host write (Q-TI-2); N4 VSYS's effective capacitance at %s V against TI's %s uF (RECORD, MAKER);"
      % (fmt(R["cv_max"], 3), fmt(B["csys_uf"])))
    p("     N5 every load converter's minimum input (A-14, R-49); N6 0-V charging before the gauge's SUV check (Q-TI-7)")
    p("")
    p("3. U-04, THE SOURCE ENVELOPE (what U3 delivers to VBAT with no pack; H3's line, L4-E5)")
    p("   method: U3's board current at the line's low target over R16 +%s %% (9 V: L4-E5's %s A floor) and IIN_HOST's minimum %s A, at"
      % (fmt(E["r16_tol"] * 100), fmt(E["floor_min"]), fmt(E["iin_min"])))
    p("     VBUS20's lowest %s V; the high side L4-E5's effective maximum at %s V; U3 %s (RECORD: L4-E5 and L4-E9, INFERRED)" % (fmt(E["vb_low"]), fmt(E["vb_top"]), fmt(E["eta_u3"], 4)))
    p("   VIN_RAW | U3 board current, A | at VBAT, W | L4-E9's figure")
    for v in (9.0, 12.0, 24.0, 36.0):
        e = E["env"][v]
        l9 = {9.0: "%s to %s W" % (fmt(E["l9"]["min9"], 1), fmt(E["l9"]["max9"], 1)), 12.0: "up to %s W" % fmt(E["l9"]["max12"], 1), 24.0: "up to %s W" % fmt(E["l9"]["max24"], 1), 36.0: "(the window)"}[v]
        p("     %5s V | %s to %s | %s to %s | %s (INFERRED)" % (fmt(v, 1), fmt(e["board_lo"]), fmt(e["board_hi"]), fmt(e["w_lo"], 1), fmt(e["w_hi"], 1), l9))
    p("   the entry's own bound at 9 V: %s A x 9 V x %s x %s = %s W (INFERRED)" % (fmt(E["entry"][0], 2), fmt(E["eta_fe"], 2), fmt(E["eta_u3"], 4), fmt(E["entry9_w"], 1)))
    p("   the load states (battery-terminal figures taken at VBAT; the pack path's loss neglected, a small overstatement) against it:")
    for name, (lo, plan, hi) in E["states"].items():
        cl = " | ".join("%s V: %s" % (fmt(v, 0), E["cls"][(name, v)]) for v in (9.0, 12.0, 24.0, 36.0))
        p("     %-32s %s W | %s (RECORD, INFERRED)" % (name, fmt(plan, 2), cl))
    p("   a dead pack's charge on top: at most %s A x %s V = %s W, which DPM gives up first (MAKER 9.3.17, INFERRED)" % (fmt(B["iclamp"]), fmt(P["vsys_cuv"][1], 1), fmt(E["dead_charge_w"], 2)))
    p("   THE ENTRY'S UVLO AGAINST 9 V (finding U4-F2): UVLOTH %s / %s / %s V, UVLOHYS %s / %s / %s uA (SNVS452G p.%d) (MAKER); R20 %sk, R21 %sk at 1 %% (NETLIST)"
      % (tuple(fmt(x, 2) for x in E["uv_rows"]) + tuple(fmt(x * 1e6, 0) for x in E["hy_rows"]) + (E["uvlo_page"], fmt(E["r20"] / 1e3, 0), fmt(E["r21"][0] / 1e3, 1))))
    for lab, (rise, fall) in (("as drawn (R21 %sk)" % fmt(E["r21"][0] / 1e3, 1), E["uvlo_drawn"]), ("SESSION R21 %sk 1 %%" % fmt(R21_NEW_K, 1), E["uvlo_new"])):
        p("     %s: on at %s / %s / %s V rising, off at %s / %s / %s V falling (INFERRED)" % ((lab,) + tuple(fmt(x, 2) for x in rise) + tuple(fmt(x, 2) for x in fall)))
    p("     as drawn a 9.00 V source turns the entry on only below the nominal corner: at %s V it never starts (NOT MET as drawn, INFERRED); with %sk the"
      % (fmt(E["uvlo_drawn"][0][2], 2), fmt(R21_NEW_K, 1)))
    p("     highest rising threshold is %s V, under 9.00 V by %s V with no current flowing (MEETS, INFERRED); the falling band stays under the knee" % (fmt(E["uvlo_new"][0][2], 2), fmt(PLUG_V - E["uvlo_new"][0][2], 2)))
    p("   WHERE THE 9 V IS MEASURED (finding U4-F3): REQ-015 names no point; H3's knee sits at VIN_RAW (zero at %s V, the line from 9.00 V). At" % fmt(E["k0"], 3))
    p("     the kit's plug the kit's own series resistance lies between: board E %s ohm (L2's series DCR %s, R19 +1 %%, Q1 and Q7 %s each at"
      % (fmt(E["r_e"], 4), fmt(E["l2_dcr"], 4), fmt(E["q_rds"], 4)))
    p("     their 25 C maximum, F1's typical cold %s) (MAKER, NETLIST; hot values higher, not counted) plus the cable and lead" % fmt(E["f1_rcold"], 5))
    for k in ("drawn", "selected"):
        pl = E["plug"][k]
        p("     %-8s interconnect %s ohm at 20 C: a 9.00 V plug settles VIN_RAW at %s V, U3 %s A, %s W at VBAT nominal (against %s W at VIN_RAW 9 V);"
          % (k, fmt(pl["r"], 4), fmt(pl["vin"], 3), fmt(pl["board"], 3), fmt(pl["w"], 1), fmt(E["line9_nom_w"], 1)))
        p("       the knee's top would have to sit at %s V of VIN_RAW to keep the line's 9 V current at the plug (INFERRED)" % fmt(pl["knee_top"], 3))
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
    p("   a mandatory requirement naming a load state for source-only operation: %s (section 1)" % ("yes" if F["owner_question"] else "none"))
    p("   the kit's own caps at 9 V: F1 0997010 at its %s C column %s A (the hottest air %s C): %s W at VBAT; at its 0 C column %s A: %s W; the"
      % (fmt(F["f_col"], 0), fmt(F["f_hot_a"], 1), fmt(F["air_hot"], 1), fmt(F["cap9_hot_w"], 1), fmt(F["der"][0], 1), fmt(F["cap9_cold_w"], 1)))
    p("     interconnect after D-06 at %s A: %s W; the entry's limit and H3's line are settings, not capabilities (MAKER, INFERRED)" % (fmt(CONT_CLASS_A, 0), fmt(F["cap9_interconnect_w"], 1)))
    p("   REQ-015 states no source current capability: every figure here takes the source as holding its voltage (named)")
    p("   against section 3's states at their plan figure: in the hottest air F1's 80 C column caps a 9 V source under %s (MAKER, INFERRED);"
      % (", ".join("%s %s W" % (n, fmt(pl, 1)) for n, pl in F["over_hot"]) or "none"))
    p("     the cold states against its 0 C column: %s over; a 15 A MINI 58 V (its 80 C column %s A) would admit %s W, with D-06's band"
      % (", ".join("%s %s W" % (n, fmt(pl, 1)) for n, pl in F["cold_over"]) or "none", fmt(F["der15_hot"], 0), fmt(F["cap9_15a_hot_w"], 1)))
    p("     re-rated to it: a part choice, not the source's capability (MAKER, INFERRED)")
    p("   so NO owner question is forced: no approved requirement names a load REQ-015's 9 V must carry, and where a part caps a named")
    p("     state at 9 V another part lifts it, so no arrangement-independent cap exists (INFERRED)")
    p("")
    p("6. D-06, F1'S WEAK-SOURCE BAND AND THE INTERCONNECT")
    p("   0997010.WXN time-current (MAKER, held sheet p.3): " + "; ".join("%s %%: %s to %s s" % (fmt(pct * 100, 0), fmt(tmin, 2), "-" if tmax is None else fmt(tmax, 2)) for pct, tmin, tmax in D["tc"]))
    p("   the band a source under 30 A can leave (INFERRED: no maximum time is printed under 135 %%): up to %s A with no stated limit; then" % fmt(D["cont_need"], 1))
    p("     " + "; ".join("from %s A at most %s s" % (fmt(i, 1), fmt(t, 2)) for i, t in D["band"]))
    p("   the elements in that fault loop, as drawn:")
    for n, r, src, cls in D["drawn"]:
        p("     %-58s %s (%s; %s)" % (n, ("%s A" % fmt(r, 1)) if r is not None else "no rating", src, cls))
    p("   as drawn: NOT MET (every element needs at least %s A with no time limit; one is %s A, four state none) (INFERRED)" % (fmt(D["cont_need"], 1), fmt(D["c16"], 0)))
    p("   SELECTED (SESSION): every element of the interconnect rated at least %s A continuous, which covers the band to 20 A for 600 s and"
      % fmt(CONT_CLASS_A, 0))
    p("     more with no time limit:")
    for n, cl, r, src in D["selected"]:
        p("     %-46s %s%s (%s) (SESSION)" % (n, cl, (" : %s A" % fmt(r, 0)) if r is not None else "", src))
    p("     D38999 contact table p.%d (MAKER); shell 13's Series III arrangements 13-4, 13-8, 13-26, 13-32, 13-35 (p.%d), shell 17's 17-2, 17-6, 17-8 (p.%d) (MAKER)"
      % (D["d38999_p"], D["ins13_p"], D["ins17_p"]))
    p("   the short-time points against a %s mm2 core, adiabatic (INFERRED: copper's resistivity and volumetric heat):" % fmt(SEL_MM2, 3))
    for i, t, dt in D["adiabatic"]:
        p("     %s A for %s s: %s K (INFERRED)" % (fmt(i, 1), fmt(t, 2), fmt(dt, 3)))
    p("   and against the size 12 contact's %s A: the same I2t as %s (INFERRED; its short-time limit is not printed, named)"
      % (fmt(D["c12"], 0), "; ".join("%s A for %s s = %s s at %s A" % (fmt(i, 0), fmt(t, 2), fmt(e, 3), fmt(D["c12"], 0)) for i, t, e in D["contact_eq_s"])))
    p("   THE STIFF SOURCE AGAIN (copper alone at %s C, the source's own resistance zero, A-12; at the OVLO maximum %s V):" % (fmt(T_COLD, 0), fmt(D["vmax"], 2)))
    for lab, rr, ipf in D["stiff"]:
        p("     %-48s %s ohm, %s A against %s A: %s (INFERRED)" % (lab, fmt(rr, 5), fmt(ipf, 1), fmt(D["interrupt_a"], 0), "MEETS" if ipf <= D["interrupt_a"] else "NOT MET"))
    p("   so a heavier interconnect needs a resistance floor: at least %s ohm of copper loop at %s C, which AWG 14 gives from %s m of cable"
      % (fmt(D["r_floor"], 5), fmt(T_COLD, 0), fmt(D["min_len_14"], 2)))
    p("     with the 0.5 m lead; SESSION: the DC pair's run at least %s m (%s A); a shorter or heavier lead needs a fuse with a larger interrupting"
      % (fmt(SEL_CABLE_M, 1), fmt(D["sel_ipf"], 1)))
    p("     rating at 58 V DC, of which no sheet is held (named)")
    p("   F1's other checks with it: 6.15 A against its %s C column %s A (MEETS, MAKER); the lowest stiff fault at 9 V with the copper at %s C,"
      % (fmt(F["f_col"], 0), fmt(F["f_hot_a"], 1), fmt(F["air_hot"], 1)))
    p("     %s A, %s times the rating, inside the 600 %% row's 0.1 s (MEETS, INFERRED); the start's I2t at the new timer's maximum below (MEETS)"
      % (fmt(D["min_fault_9v"], 1), fmt(D["min_fault_9v_x"], 2)))
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
    p("   SELECTED (SESSION): C5 %s (LCSC %s) with C5B %s (LCSC %s), both 1206 C0G 50 V, on HS_TIMER: %s nF; fault time %s ms nominal, %s to %s ms stacked"
      % (S["parts"][0], T9["sel_codes"][0], S["parts"][1], T9["sel_codes"][1], fmt(S["c"] * 1e9, 0), fmt(T9["sel_nom_ms"] * 1e3, 3), fmt(S["tmin"] * 1e3, 3), fmt(S["tmax"] * 1e3, 3)))
    p("     start: %s ms against %s ms, %s ms in hand, so the margin holds while the start stays under %s ms (MEETS, INFERRED); Figure 10: %s A against %s A at %s ms, %s %% past the 10 ms line (MEETS, CONDITIONAL)"
      % (fmt(S["tmin"] * 1e3, 3), fmt(T9["need"] * 1e3, 3), fmt((S["tmin"] - T9["need"]) * 1e3, 3), fmt(S["tmin"] / 1.5 * 1e3, 3), fmt(S["soa"], 4), fmt(T9["pulse_a"], 3), fmt(S["tmax"] * 1e3, 3), fmt(T9["sel_extrap"] * 100, 1)))
    p("     sensitivities: a steeper law past 10 ms (m 0.5) gives %s A (MEETS); the damp-heat row stacked instead of endurance: %s to %s ms, %s A (MEETS) (INFERRED);"
      % (fmt(T9["sel_soa_m05"], 4), fmt(T9["damp"][0] * 1e3, 3), fmt(T9["damp"][1] * 1e3, 3), fmt(T9["damp_soa"], 4)))
    p("     TI's own basis (typical values, 1.5 x the typical start): %s ms against %s ms (MEETS, INFERRED); the DC line derated, %s A, is under the pulse:"
      % (fmt(T9["typ_basis"][0] * 1e3, 3), fmt(T9["typ_basis"][1] * 1e3, 3), fmt(T9["dc_hot"], 4)))
    p("     the pulse is bounded by the fault time, not by a steady rating (INFERRED); F1 during the longest start: %s A2s against %s A2s (MEETS)"
      % (fmt(T9["f1_i2t_start"], 3), fmt(E["f1_i2t"], 0)))
    p("")
    p("8. THE DOWNSTREAM ITEMS (each with one owner and an acceptance; L4E11-SOURCE-ONLY-AND-ENTRY.md section 8 is the same table)")
    for it in downstream(R):
        p("   %s | %s | %s | %s" % (it[0], it[1], it[2], it[3]))
    p("")
    p("END. Desk arithmetic; nothing is measured. Drafts: apply_gen_sch_e_uvlo.py (R21), apply_gen_sch_e_timer.py (C5 and C5B); the")
    p("interface and firmware texts are drafts for Layer 5 in the record. Software tests establish this record's own behaviour only.")
    return "\n".join(out) + "\n"




def downstream(R):
    E, D, T9 = R["E"], R["D"], R["T9"]
    return [
    ("E11-01", "IMPLEMENTATION", "Layer 8 board E generator owner", "apply_gen_sch_e_uvlo.py applied after L4-E9's apply_gen_sch_e_hotswap.py: R21 %sk 1 %%, U6's label; the regenerated netlist carries R21 %sk and the UVLO band recomputed reads %s to %s V rising" % (fmt(R21_NEW_K, 1), fmt(R21_NEW_K, 1), fmt(E["uvlo_new"][0][0], 2), fmt(E["uvlo_new"][0][2], 2))),
    ("E11-02", "IMPLEMENTATION", "Layer 8 board E generator owner", "apply_gen_sch_e_timer.py: C5 GRM3195C1H104GA05D (C907944) and C5B GRM3195C1H683JA05D (C3847777) on HS_TIMER; the netlist carries both; the fault time recomputed from the fitted parts reads %s to %s ms" % (fmt(T9["sel"]["tmin"] * 1e3, 3), fmt(T9["sel"]["tmax"] * 1e3, 3))),
    ("E11-03", "INTERFACE", "Layer 5 interfaces", "FW-C08, FW-A14 and PANEL.md section 10 restated as this record's drafts (section 7a): the cold and no-charge holds act by the gauge's window and CHRG_INHIBIT, never by SHORE_INHIBIT or CHG_INHIBIT while the pack cannot discharge; REQ-046's hold still clears above 3 C"),
    ("E11-04", "FIRMWARE", "firmware owner", "rules R-a to R-d implemented (section 7a): ChargeCurrent at most %s A while U3's SRN reading is under %s V or the gauge reports XDSG or PRECHARGE; the source-only shed to the envelope at the measured VIN_RAW; the VSYS_UVP latch cleared by the host or by a source re-plug; checked on the bench (E11-06)" % (fmt(RULE_PRECHARGE_A, 1), fmt(RULE_SRN_V, 1))),
    ("E11-05", "EVIDENCE", "Layer 6 components", "TI's answers filed: Q-TI-3 restated (VSYS's regulation with no battery current possible, under a 5 A load step, and with CHRG_INHIBIT = 1) and Q-TI-2; U-04's N1 to N3 re-judged on them"),
    ("E11-06", "TEST", "prototype bench", "R-85 extended: at 9 V at the plug, 12 V and 24 V, with the pack absent, at CUV and cold-soaked (both FETs open): the kit boots and runs within the envelope; VSYS and its step response recorded; the 384 mA clamp; Q2's case at 1.0 A; the UVLO latch recovery by a re-plug"),
    ("E11-07", "ANALYSIS", "Layer 9 pre-layout analysis", "VSYS's effective capacitance at 16.884 V from the makers' DC-bias curves at least 50 uF (SLUSE66A 10.1), else a polymer capacitor added (TI prefers POSCAP)"),
    ("E11-08", "EVIDENCE", "Layer 9 pre-layout analysis", "every load converter's and the controllers' minimum input read from their sheets against 10.0 V (A-14, R-49) and against 8.0 V for a pack at its Shutdown Voltage"),
    ("E11-09", "ANALYSIS", "Layer 4 coordinator", "L4-E5's knee and restart guard re-derived for REQ-015's 9 V at the kit's plug with the kit's own series resistance (the knee's top at %s V drawn, %s V with D-06's interconnect); the 9 V envelope at the plug re-run at %s W or more" % (fmt(E["plug"]["drawn"]["knee_top"], 3), fmt(E["plug"]["selected"]["knee_top"], 3), fmt(E["env"][9.0]["w_lo"], 1))),
    ("E11-10", "IMPLEMENTATION", "Layer 7 mechanical", "the DC receptacle and plug on MIL-DTL-38999 size 12 contacts (shell 17, insert 17-6: DC and solar pairs on four contacts, two unassigned between power and return; or 13-26 with the solar pair on rated contacts elsewhere); the plate cut-out checked against CASE-MARGINS 3.3"),
    ("E11-11", "IMPLEMENTATION", "Layer 7 mechanical", "the DC lead: cores of 2.081 mm2 (AWG 14) with a maker's rating of at least 20 A each, the DC pair's run at least %s m (copper loop at least %s mOhm at -20 C with the inside lead), the NATO plug with a maker's rating of at least 20 A; the sheets filed" % (fmt(SEL_CABLE_M, 1), fmt(D["r_floor"] * 1e3, 2))),
    ("E11-12", "IMPLEMENTATION", "Layer 7 mechanical", "the inside lead (AWG 14, a maker's rating of at least 20 A) and J_DCIN as a board connector rated at least 20 A (XT60 class, gender opposite J_BATT's, so the pack lead cannot mate it) or soldered lands; board E's generator names the part"),
    ("E11-13", "IMPLEMENTATION", "Layer 8 board E generator owner", "F1's holder: a MINI 297/997 holder whose maker prints a current rating of at least 20 A (the 3568 prints none); its sheet filed"),
    ("E11-14", "LAYOUT", "Layer 9 pre-layout analysis", "board E's copper from J_DCIN through F1 to D10, C4 and Q1 sized for 20 A continuous at the rise this project judges at"),
    ("E11-15", "IMPLEMENTATION", "Layer 8 board E generator owner", "pcb_energy_chain.yaml SHORE_INPUT restated with L4-E9's R-95: conductor %s A, protects the interconnect, the prospective high the selected lead's %s A; the energy chain gate reads it" % (fmt(CONT_CLASS_A, 0), fmt(D["sel_ipf"], 1))),
    ("E11-16", "EVIDENCE", "Layer 6 components", "the size 12 contact's and the board connector's short-time data at 35 A for 0.5 s and 60 A for 0.1 s, or F1's total clearing I2t (R-115) against them, filed"),
    ("E11-17", "TEST", "prototype bench", "R-118 with the fitted C5 pair at 43 V: the fault time inside %s to %s ms and the start into VIN_RAW inside %s ms" % (fmt(T9["sel"]["tmin"] * 1e3, 3), fmt(T9["sel"]["tmax"] * 1e3, 3), fmt(T9["start_max"] * 1e3, 3))),
    ("E11-18", "DOCUMENT", "CONOPS owner", "the source-only statement in CONOPS (section 7b's text): with no usable pack the kit runs within the source envelope; a pack below about 2.4 V a cell holds VSYS under the converters' floor while it precharges; a brown-out on the source alone may latch the charger off until the source is re-plugged"),
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
