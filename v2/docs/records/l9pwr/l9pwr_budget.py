#!/usr/bin/env python3
"""l9pwr_budget.py: Layer 9 item 9.1, the power budget brought to the current design with margins and sensitivities
(MESHSAT-1357, 3 October 2026). PROTOTYPE DESIGN, DESK ARITHMETIC: nothing in this kit has been built, powered or
measured, and no figure printed here is a measurement.

What it does. It imports record rv-pwr's model (v2/docs/records/rv-pwr/pwr_budget.py) UNCHANGED, pinned by sha256, and
rebuilds that model's load tree three times:
  RV       rv-pwr's tree as committed (the boards as generated at 1f614233); this script's own evaluator must reproduce
           rv-pwr's figures on it before anything else is printed (section 2);
  DRAWN    the generators as they are in this tree (gen_sch_a.py, gen_sch_b.py, gen_sch_e.py), so every change that is ON
           MAIN since 1f614233 and moves a power figure (section 1, rows M1 to M5);
  DRAFTED  DRAWN plus every release-guarded DRAFT of Layers 4 and 8 that moves a power figure (section 1, rows D1 to D5).
           A draft is modelled as a draft: it is printed DRAFTED, never as the built circuit, and nothing here applies it.
Every figure that enters is parsed from the file that carries it (a record's committed output, a generator, a draft, a
maker's document through pdftotext), each file pinned by sha256 in section 0; the script refuses to run when a figure is
not found where it is looked for. Each load keeps rv-pwr's tier (S a primary document gives it, R a document bounds it and
PLAN sits inside by a stated duty, D a generator declares it, T a placeholder) or carries the reason it has none.

Determinism: sums are math.fsum, printed figures are rounded at fixed places, the output carries no date, host or
absolute path; two runs give the same bytes (the output is regenerated only through _bin/regen_out.py).
Usage, from the repository root: python3 v2/docs/records/l9pwr/l9pwr_budget.py   (stdlib and pdftotext; about a second)
"""
import ast
import hashlib
import importlib.util
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))

PINS = {
    "rvpwr": "v2/docs/records/rv-pwr/pwr_budget.py",
    "rvpwr_out": "v2/docs/records/rv-pwr/pwr_budget.out",
    "hc2": "v2/docs/records/hc2/pwr_red2.py",
    "gen_a": "v2/ecad/tools/gen_sch_a.py",
    "gen_b": "v2/ecad/tools/gen_sch_b.py",
    "gen_e": "v2/ecad/tools/gen_sch_e.py",
    "pack": "v2/ecad/tools/pcb_pack_protection.yaml",
    "l4e9": "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md",
    "l4e11_out": "v2/docs/records/l4e11/l4e11_power.out",
    "l4e11_aux": "v2/docs/records/l4e11/apply_gen_sch_e_aux.py",
    "l4e11_chg": "v2/docs/records/l4e11/apply_gen_sch_a_charger.py",
    "l4e12_out": "v2/docs/records/l4e12/l4e12_thermal.out",
    "review": "v2/docs/records/l4close/REVIEW-PROVISIONAL-FIXES-AS-RECEIVED.md",
    "l7_out": "v2/docs/records/l7pwr/l7pwr_fans_th1.out",
    "l8r2_out": "v2/docs/records/l8r2/l8r2_drafts.out",
    "l8r2_fans": "v2/docs/records/l8r2/apply_gen_sch_b_fans12.py",
    "l8r2_pnl": "v2/docs/records/l8r2/apply_gen_sch_b_panel5v.py",
    "l8gnd_out": "v2/docs/records/l8gnd/l8gnd_drafts.out",
    "ap64500": "v2/vendor/diodes/diodes-ap64500.pdf",
    "ap632": "v2/vendor/diodes/diodes-ap63200-series-buck.pdf",
    "tps62933": "v2/vendor/ti/ti-tps62933.pdf",
    "ap2112": "v2/vendor/diodes/diodes-ap2112-ldo.pdf",
    "tlv755": "v2/vendor/power/ti-tlv755p-ldo.pdf",
    "lm5176": "v2/vendor/ti/lm5176-datasheet.pdf",
    "reqs": "v2/ecad/tools/pcb_requirements.yaml",
    "rules": "v2/ecad/tools/pcb_rules.yaml",
}

STATES = ["IDLE", "IDLESPEC", "TYP", "BUSY", "RED", "REDB", "EMCON", "ALLTX", "RED2", "SURV", "SURVR"]
SCEN = ("lo", "plan", "hi")


def die(msg):
    sys.stdout.write("l9pwr_budget: REFUSED, %s\n" % msg)
    sys.exit(3)


def path(key):
    return os.path.join(ROOT, PINS[key])


def text(key):
    p = path(key)
    if not os.path.isfile(p):
        die("%s (%s) is not in the tree" % (PINS[key], key))
    return open(p, encoding="utf-8").read()


def flat(t):
    return " ".join(t.split())


def sha16(key):
    return hashlib.sha256(open(path(key), "rb").read()).hexdigest()[:16]


_PDF = {}


def pdf(key, layout=False, last=None):
    k = (key, layout, last)
    if k not in _PDF:
        cmd = ["pdftotext"] + (["-layout"] if layout else []) + (["-l", str(last)] if last else []) + [path(key), "-"]
        try:
            r = subprocess.run(cmd, capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            die("pdftotext could not read %s (%s)" % (PINS[key], e))
        _PDF[k] = r.stdout.decode("utf-8", "replace")
    return _PDF[k]


def grab(t, pat, what, n=1, conv=float):
    m = re.search(pat, t)
    if not m:
        die("%s: the pattern for %s is not found" % (what, pat[:60]))
    g = m.groups()[:n] if n > 1 else (m.group(1),)
    out = tuple(conv(x) for x in g)
    return out if n > 1 else out[0]


def ohms(s):
    s = s.strip()
    m = re.match(r"^([\d.]+)\s*(m|R|k)?", s)
    v = float(m.group(1))
    return v / 1000.0 if m.group(2) == "m" else v * 1000.0 if m.group(2) == "k" else v


# ------------------------------------------------------------------------------------------------ the inputs, parsed
def load_rvpwr():
    sp = importlib.util.spec_from_file_location("l9pwr_rvpwr_model", path("rvpwr"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def hc2_states(pb):
    """record hc2's state compositions (PS-RED2, PS-SURV, PS-SURV-R, EMCON as generated since 458b2873), executed from
    pwr_red2.py's own statements with rv-pwr's model bound; the file prints at import, so only its definitions run."""
    tree = ast.parse(text("hc2"))
    want = {"CM5_ON", "FAN", "SW33", "SW10", "NV_IDLE", "RM_IDLE", "BEACONS", "RED2", "SURV", "SURVR", "EMCON_MAIN"}
    keep = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in ("slot", "hubs"):
            keep.append(node)
        elif isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) and t.id in want for t in node.targets):
            keep.append(node)
    ns = {"pb": pb, "up": pb.up, "same": pb.same, "OFF": pb.OFF}
    exec(compile(ast.Module(body=keep, type_ignores=[]), PINS["hc2"], "exec"), ns)
    for k in ("RED2", "SURV", "SURVR", "EMCON_MAIN"):
        if k not in ns:
            die("record hc2 no longer defines %s" % k)
    return ns


def gen_rails(key):
    """Every _intent.rail(...) of a generator: name -> (volts, typical A, peak A, switch, efficiency, fed_from), the
    calls inside a `for` loop evaluated once per loop value with the loop's simple assignments bound."""
    tree = ast.parse(text(key))
    rails = {}

    def ev(node, env):
        return eval(compile(ast.Expression(node), "<rail>", "eval"), {"__builtins__": {}}, dict(env))

    def take(call, env):
        try:
            args = [ev(a, env) for a in call.args[:4]]
        except Exception:
            return
        kw = {}
        for k in call.keywords:
            if k.arg in ("switch", "efficiency", "fed_from"):
                try:
                    kw[k.arg] = ev(k.value, env)
                except Exception:
                    kw[k.arg] = None
        if isinstance(args[0], str):
            rails[args[0]] = (args[1], args[2], args[3], kw.get("switch"), kw.get("efficiency"), kw.get("fed_from"))

    def is_rail(n):
        return (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute)
                and n.value.func.attr == "rail")

    def walk(body, env):
        for st in body:
            if is_rail(st):
                take(st.value, env)
            elif isinstance(st, ast.Assign) and env:
                try:
                    val = ev(st.value, env)
                except Exception:
                    continue
                t = st.targets[0]
                if isinstance(t, ast.Name):
                    env[t.id] = val
                elif isinstance(t, ast.Tuple) and isinstance(val, tuple) and len(val) == len(t.elts):
                    for e, v in zip(t.elts, val):
                        if isinstance(e, ast.Name):
                            env[e.id] = v
            elif isinstance(st, ast.For) and isinstance(st.target, (ast.Name, ast.Tuple)):
                try:
                    vals = ev(st.iter, env)
                except Exception:
                    continue
                for v in vals:
                    e2 = dict(env)
                    if isinstance(st.target, ast.Name):
                        e2[st.target.id] = v
                    else:
                        for e, x in zip(st.target.elts, v):
                            e2[e.id] = x
                    walk(st.body, e2)
    walk(tree.body, {})
    return rails


def gen_lm5176(key):
    """board A's LM5176 stages: tag -> (U ref, input net, output net, ISNS shunt in ohms)."""
    tree = ast.parse(text(key))
    default = None
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name == "lm5176":
            names = [a.arg for a in n.args.args]
            defs = n.args.defaults
            d = dict(zip(names[len(names) - len(defs):], defs))
            default = ast.literal_eval(d["isns"])
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "lm5176":
            a = [ast.literal_eval(x) for x in n.args[:4]]
            isns = default
            for k in n.keywords:
                if k.arg == "isns":
                    isns = ast.literal_eval(k.value)
            out[a[0]] = (a[1], a[2], a[3], ohms(isns))
    return out


def draft_rails(key):
    """the _intent.rail texts a draft would write into its generator (string literals inside the draft)."""
    t = text(key)
    out = {}
    for m in re.finditer(r'_intent\.rail\(\\?"([^"\\]+)\\?", ([\d.]+), ([\d.]+), ([\d.]+)', t.replace('\\"', '"')):
        out[m.group(1)] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))
    for m in re.finditer(r"_intent\.rail\((\w+), ([\d.]+), ([\d.]+), ([\d.]+), [^\n]*?efficiency=([\d.]+)", t):
        out["<%s>" % m.group(1)] = (float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)))
    return out


def parse_inputs(pb):
    F = {}
    # ---- the generators as they are in this tree (ON MAIN)
    ra, rb, re_ = gen_rails("gen_a"), gen_rails("gen_b"), gen_rails("gen_e")
    lm = gen_lm5176("gen_a")
    F["rails_a"], F["rails_b"], F["rails_e"], F["lm"] = ra, rb, re_, lm
    for need_ in ("+5V_S1", "+5V_S2", "+5V_S3", "+5V_DEV", "+5V_D8IN", "VHEAT", "+3V3", "+13V8_PA", "+12V_HF", "VMON"):
        if need_ not in ra:
            die("gen_sch_a.py declares no rail %s" % need_)
    for tag, rail in (("S2", "+5V_S2"), ("SD", "+5V_DEV"), ("PA", "+13V8_PA"), ("HF", "+12V_HF")):
        if tag not in lm or lm[tag][2] != rail:
            die("gen_sch_a.py: the LM5176 stage %s does not drive %s" % (tag, rail))
    F["s2_eff"], F["dev_eff"] = ra["+5V_S2"][4], ra["+5V_DEV"][4]
    F["d8_v"], F["d8_eff"], F["d8_sw"] = ra["+5V_D8IN"][0], ra["+5V_D8IN"][4], ra["+5V_D8IN"][3]
    F["heat_v"], F["heat_eff"], F["heat_sw"] = ra["VHEAT"][0], ra["VHEAT"][4], ra["VHEAT"][3]
    F["s2a_v"] = rb["+3V3_S2A"][0]
    F["shunt_tol"] = grab(flat(text("gen_a")), r'VSNS (\d+) mV\W+over the \d+ mOhm ISNS shunt at \+(\d+) percent', "the ISNS shunt tolerance", 2)[1] / 100.0
    F["mon_ilm"] = grab(text("gen_a"), r'efuse\("U21", "VBAT", "VMON".*?\(ILM: ([\d.]+) A\)', "U21's ILM")
    F["cellf_loads"] = None
    m = re.search(r'_intent\.rail\("CELL_F", .*?loads=(\{[^}]*\})', text("gen_e"), re.S)
    if not m:
        die("gen_sch_e.py: CELL_F's loads")
    F["cellf_loads"] = ast.literal_eval(m.group(1))
    # ---- the makers' documents
    F["ap64500_a"] = grab(pdf("ap64500", last=1), r"The AP64500 is a (\d+)A", "AP64500's rating")
    F["ap632_a"] = grab(pdf("ap632", last=1), r"is a (\d+)A, synchronous buck", "AP6320x's rating")
    F["tps62933_a"] = grab(flat(pdf("tps62933", last=1)), r"(\d)-A \(TPS62933 and", "TPS62933's rating")
    F["ap2112_a"] = grab(pdf("ap2112", last=1), r"guaranteed (\d+)mA \(min\.\)", "AP2112's rating") / 1000.0
    F["tlv755_a"] = grab(pdf("tlv755", last=1), r"TLV755P (\d+)mA", "TLV755P's rating") / 1000.0
    F["vsns"] = tuple(v / 1000.0 for v in grab(pdf("lm5176", layout=True), r"VSNS\s+Average current loop regulation target\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM5176 VSNS", 3))
    # ---- the pack contract
    pk = text("pack")
    F["i_cont"] = grab(pk, r"declared_continuous_a: ([\d.]+)", "the pack's continuous current")
    F["i_peak"] = grab(pk, r"declared_peak_a: ([\d.]+)", "the pack's peak current")
    F["i_ocd"] = grab(pk, r"PACK_OVER_CURRENT_DISCHARGE\n[^\n]*\n[^\n]*\n\s+threshold: \{value: ([\d.]+), unit: A", "OCD's threshold")
    F["cuv"] = grab(pk, r"CELL_UNDER_VOLTAGE\n[^\n]*\n[^\n]*\n\s+threshold: \{value: ([\d.]+), unit: V", "CUV's threshold")
    F["series"] = grab(pk, r"\n  series: (\d+)", "the series count", conv=int)
    # ---- rv-pwr's D-11 floors (constants inside its main())
    rv = text("rvpwr")
    F["floor"] = grab(rv, r"\n    FLOOR = ([\d.]+)", "rv-pwr's D-11 floor")
    F["pa_floor"] = grab(rv, r"\n    PA_FLOOR = ([\d.]+)", "rv-pwr's PA floor")
    # ---- L4-E9 (the consolidated architecture)
    n9 = flat(text("l4e9"))
    F["l4e9_modes"] = grab(n9, r"Modes: PS-IDLE-SPEC \(([\d.]+) W at the pack terminals\), PS-ALLTX \(([\d.]+) W plan, ([\d.]+) W high\) and the PA keyed alone at 113 W \(([\d.]+) W\)", "L4-E9's modes", 4)
    F["usable_wh"] = grab(n9, r"usable ([\d.]+) Wh at \+20 C", "the usable energy")
    F["vsys"] = grab(n9, r"the system node ([\d.]+) to ([\d.]+) V", "the system node", 2)
    F["iin_host"] = grab(n9, r"IIN_HOST ([\d.]+) A", "IIN_HOST")
    F["vbus20"] = grab(n9, r"VBUS20 ([\d.]+) to ([\d.]+) V", "VBUS20's band", 2)
    # ---- L4-E11 (the battery FETs, board E's auxiliary domain, the mixers' 12 V rail)
    t11 = flat(text("l4e11_out"))
    qc = t11[t11.index("(Q-c) Nexperia BUK6Y10-30P, two in parallel"):]
    F["fet_25c"] = grab(qc, r"printed maxima: ([\d.]+) mOhm at -10 V and 25 C", "the pair's 25 C maximum") / 1000.0
    F["fet_gate"], F["fet_bound"] = grab(qc, r"gate factor ([\d.]+), ([\d.]+) mOhm per FET", "the pair's bound", 2)
    F["fet_bound"] /= 1000.0
    F["fet_idle"] = grab(t11, r"on battery at PS-IDLE-SPEC, ([\d.]+) A: ([\d.]+) W in the pair", "the pair at PS-IDLE-SPEC", 2)
    F["fet_typ"] = grab(t11, r"on battery at PS-TYP, ([\d.]+) A: ([\d.]+) W in the pair", "the pair at PS-TYP", 2)
    s18 = t11[t11.index("18. THE FANS' FEED AFTER LAYER 7'S SELECTION"):]
    F["u22_eff_ta04"] = grab(s18, r"TA04b's efficiency at ([\d.]+) A reads about (\d+) percent", "TA04b", 2)
    F["u22_maxload"] = grab(s18, r"maximum load at 12 V out near ([\d.]+) V in about ([\d.]+) A", "U22's maximum load", 2)
    F["u22_ilim"] = grab(s18, r"inductor current limit ([\d.]+) / ([\d.]+) / ([\d.]+) A", "U22's inductor limit", 3)
    F["u22_out"] = grab(s18, r"the output ([\d.]+) V \(([\d.]+) to ([\d.]+) V at FB's limits", "U22's output", 3)
    F["u22_heat"] = grab(s18, r"heat into the case: ([\d.]+) W at full speed \(([\d.]+) W of fans at ([\d.]+)\)", "U22's heat", 3)
    F["vsyse_decl"] = grab(s18, r"U22's input ([\d.]+) A \(([\d.]+) W over ([\d.]+) at ([\d.]+) V, plus (\d+) mA quiescent\), with U12's ([\d.]+) A: ([\d.]+) A DECLARED", "VSYS_E's declaration", 7)
    F["vsyse_plan"] = grab(s18, r"at the plan's duty ([\d.]+) A", "VSYS_E at the plan's duty")
    F["u42"] = grab(s18, r"against U42's least limit ([\d.]+) A: ([\d.]+) %, ([\d.]+) A in hand", "U42's least limit", 3)
    F["vsyse_drop"] = grab(s18, r"the drop at the floor with ([\d.]+) A: ([\d.]+) V, VSYS_E ([\d.]+) V", "VSYS_E's drop", 3)
    dr = draft_rails("l4e11_aux")
    if "VSYS_E" not in dr or "+12V_FAN" not in dr:
        die("the draft apply_gen_sch_e_aux.py no longer writes VSYS_E and +12V_FAN")
    F["aux_rails"] = dr
    m = re.search(r'_intent\.rail\(\\?"\+12V_FAN\\?", [^\n]*?efficiency=([\d.]+)', text("l4e11_aux"))
    F["fan12_eff_draft"] = float(m.group(1)) if m else die("the +12V_FAN efficiency in the draft")
    if "BUK6Y10-30P" not in text("l4e11_chg") or "Q39" not in text("l4e11_chg"):
        die("the charger draft no longer carries the BUK6Y10-30P pair Q39, Q40")
    # ---- Layer 7's picks
    t7 = flat(text("l7_out"))
    F["mixer"] = grab(t7, r"mixers \(2, board E\): Sanyo Denki (\S+), [^;]*?, (\d+) V \(([\d.]+) to ([\d.]+) V\), ([\d.]+) A, ([\d.]+) W", "the mixer pick", 6, conv=str)
    F["cooler"] = grab(t7, r"coolers \(3, board B\): Sanyo Denki (\S+), [^;]*?, (\d+) V \(([\d.]+) to ([\d.]+) V\), ([\d.]+) A, ([\d.]+) W", "the cooler pick", 6, conv=str)
    F["l7_heat"] = grab(t7, r"the profile's five fans and their converters ([\d.]+) W against ([\d.]+) W", "L7's fan heat", 2)
    F["l7_stepup_loss"] = grab(t7, r"so ([\d.]+) W lost in it per running fan", "L7's step-up loss")
    # ---- record l8r2's drafts
    t8 = text("l8r2_out")
    F["su_eta"] = grab(t8, r"\n   eta\s+([\d.]+)\s+ASSUMPTION", "the step-up's efficiency")
    F["su_eta_lo"] = grab(t8, r"\n   eta_lo\s+([\d.]+)\s+ASSUMPTION", "the step-up's low efficiency")
    F["eta_slot"] = grab(t8, r"\n   eta_slot\s+([\d.]+)\s+ASSUMPTION", "l8r2's slot efficiency")
    F["su_efuse"] = grab(t8, r"eFuse ILM 1\.87 k: ([\d.]+) / ([\d.]+) / ([\d.]+) A", "the coolers' eFuse", 3)
    F["su_choice_a"] = grab(t8, r"choice \(a\), a step-up per slot \(SELECTED\): ([\d.]+) W on \+5V_Sn per slot at full speed, ([\d.]+) A at 5\.1 V .*? the three ([\d.]+) W at VBAT", "l8r2's choice (a)", 3)
    F["ron_lo"] = grab(t8, r"\n   ron_lo\s+([\d.]+)\s+MAKER", "the TPS2596 RON")
    F["pnl_efuse"] = grab(t8, r"with U901 \(ILM 604 Ohm\) ([\d.]+) / ([\d.]+) / ([\d.]+) A", "PANEL_5V's eFuse", 3)
    fr = draft_rails("l8r2_fans")
    if not any(k.startswith("<") and abs(v[0] - 12.0) < 1e-9 for k, v in fr.items()):
        die("the draft apply_gen_sch_b_fans12.py no longer writes the 12 V fan rail")
    F["fans12_rail"] = [v for k, v in sorted(fr.items()) if k.startswith("<") and len(v) == 4][0]
    if "U901" not in text("l8r2_pnl"):
        die("the draft apply_gen_sch_b_panel5v.py no longer carries U901")
    # ---- L4-E12 and the review (B4, B7, the fans' share, the heat stage)
    t12 = flat(text("l4e12_out"))
    F["b4"] = grab(t12, r"input ([\d.]+) W less stored ([\d.]+) W less exported ([\d.]+) W = ([\d.]+) W of heat, which is the profile's ([\d.]+) W at the battery node, the source path's ([\d.]+) W, the charge path's ([\d.]+) W and the charging cells' ([\d.]+) W", "L4-E12's B4", 8)
    F["b4_ballast"] = grab(t12, r"L4-E8's ballasts add ([\d.]+) W at their worst corner \(the margins' rule\): ([\d.]+) W", "the ballasts", 2)
    F["b7_run"] = grab(t12, r"PS-IDLE-SPEC on the pack \(([\d.]+) W at the pack, ([\d.]+) W into the case\)", "B7's run", 2)
    F["b7_stage"] = grab(t12, r"to the heat stage \(([\d.]+) W at the pack, ([\d.]+) W into the case", "B7's heat stage", 2)
    F["b7_g"] = grab(t12, r"G ([\d.]+) W/K reaches C1 at ([\d.]+) h and, unshed, the air ([\d.]+) C at ([\d.]+) h", "B7's constant-G check", 4)
    F["fans_share"] = grab(t12, r"PS-IDLE-SPEC \(the profile\) 4 fans: ([\d.]+) W at the pack of ([\d.]+) W", "L4-E12 8c", 2)
    F["fans_share_hs"] = grab(t12, r"the heat stage \(PS-SURV-R\) 2 fans: ([\d.]+) W at the pack of ([\d.]+) W", "L4-E12 8c heat stage", 2)
    rv_ = text("review")
    F["rev_b4"] = grab(rv_, r"P_input = \(([\d.]+) \+ ([\d.]+)\) / \(([\d.]+) . ([\d.]+)\) = ([\d.]+) W", "the review's B4 input", 5)
    F["rev_q"] = grab(rv_, r"Q_case = ([\d.]+) . ([\d.]+) = ([\d.]+) W", "the review's B4", 3)
    F["rev_b7"] = grab(rv_, r"At ([\d.]+) W case heat, ([\d.]+) W/K conductance, (\d+) kJ/K thermal mass and a \+(\d+) .C start, the closed-form model reaches \+(\d+) .C after \*\*([\d.]+) h\*\*", "the review's B7", 6)
    F["rev_b7u"] = grab(rv_, r"Without shedding it reaches \*\*([\d.]+) .C at ([\d.]+) h\*\*", "the review's unshed B7", 2)
    F["rev_ballast"] = grab(rv_, r"Adding the stated ([\d.]+) W ballast allowance gives \*\*([\d.]+) W\*\*", "the review's ballasts", 2)
    # ---- l8gnd: no power figure (read to state so)
    tg = flat(text("l8gnd_out"))
    F["l8gnd_head"] = tg[:160]
    # ---- the margin rules' own words
    rq, ru = flat(text("reqs")), flat(text("rules"))
    F["rule_cmp001"] = grab(ru, r"- id: CMP-001 .*? acceptance_criteria: > (For every part on a net whose nominal voltage exceeds 80 percent of the part's rating, and for every part in a current path above 1 A, a recorded comparison of the applied stress against the datasheet maximum, citing the datasheet page\.)", "CMP-001's acceptance", conv=str)
    F["rule_d11"] = grab(rq, r"(Set from the gauge's 20 A over-current trip with 10 percent margin and the cells' 60 C discharge window\.)", "D-11's margin rule", conv=str)
    return F


# ------------------------------------------------------------------------------------------------ the model
class Config:
    """a load tree: nodes (name -> [kind, parent, vout, param, note, status]), loads (name -> dict), the pack path."""

    def __init__(self, label, pb):
        self.label = label
        self.nodes = {n: [v[0], v[1], v[2], v[3], v[4], "RV"] for n, v in pb.NODES.items()}
        self.loads = []
        for (name, node, d, src) in pb.LOADS:
            self.loads.append({"name": name, "node": node, "d": dict(d), "src": src, "status": "RV"})
        self.r_path = pb.R_DIST
        self.r_parts = [("rv-pwr's R_DIST (W2's 20 mOhm with F2 at its 2.5 mOhm maximum)", pb.R_DIST, "RV")]
        self.fan_on = {}
        self.limits = {}
        self.heat_on = pb.HEAT_ON

    def load(self, name):
        for L in self.loads:
            if L["name"] == name:
                return L
        raise KeyError(name)

    def children(self, n):
        return [c for c, v in self.nodes.items() if v[1] == n]

    def pack_fed(self, n):
        p = self.nodes[n][1]
        while p is not None and self.nodes[p][0] == "series":
            p = self.nodes[p][1]
        return p == "VBAT"


def is_off(t):
    return t[0] == 0.0 and t[1] == 0.0 and t[2] == 0.0


def values(cfg, base, ov, idx):
    """load name -> watts at the load pins for state `base` with overrides `ov`, scenario index idx."""
    out = {}
    for L in cfg.loads:
        t = L["d"][base]
        if ov and L["name"] in ov:
            o = ov[L["name"]]
            if L["name"] in cfg.fan_on:
                t = o if is_off(o) else cfg.fan_on[L["name"]]
            else:
                t = o
        out[L["name"]] = t[idx]
    return out


def evaluate(cfg, vals, scen, vpack=None, vbatt=14.4, eff_over=None):
    """input power, output power, output current, efficiency and input voltage of every node; the VBAT total; the pack
    side (rv-pwr's battery_side at vbatt). eff_over: node -> efficiency, replacing the node's own."""
    pb = cfg.pb
    v = pb.VIN_OF[scen] if vpack is None else vpack
    at = {}
    for L in cfg.loads:
        at.setdefault(L["node"], []).append(vals[L["name"]])
    kids = {}
    for n, nv in cfg.nodes.items():
        if nv[1] is not None:
            kids.setdefault(nv[1], []).append(n)
    res = {}

    def walk(n):
        p_out = math.fsum(at.get(n, []) + [walk(c) for c in kids.get(n, [])])
        kind, parent, vout, param = cfg.nodes[n][:4]
        if kind == "root":
            res[n] = (p_out, p_out, p_out / v, 1.0, v)
            return p_out
        vin = v if cfg.pack_fed(n) else cfg.nodes[parent][2]
        if kind == "series":
            vo = v if cfg.pack_fed(n) else vout
            i = p_out / vo
            p_in = p_out + i * i * param
            res[n] = (p_in, p_out, i, (p_out / p_in) if p_in > 0 else 1.0, vin)
            return p_in
        if eff_over and n in eff_over:
            eta = eff_over[n]
        elif kind == "curve":
            eta = pb.eff_curve(param, vin, p_out / vout) if p_out > 0 else 1.0
        elif kind in ("fixed",):
            eta = param
        elif kind == "fixedq":
            eta = param[0]
        elif kind == "ldo":
            eta = vout / cfg.nodes[parent][2]
        else:
            eta = 1.0
        if p_out <= 0:
            p_in = 0.0
        elif kind == "fixedq":
            p_in = p_out / eta + param[1] * vin
        else:
            p_in = p_out / eta
        vo = v if kind == "pass" and cfg.pack_fed(n) and parent == "VBAT" else vout
        res[n] = (p_in, p_out, p_out / vo, eta, vin)
        return p_in
    p_vbat = walk("VBAT")
    pside = pb.battery_side(p_vbat, vbatt, cfg.r_path)
    return {"nodes": res, "p_vbat": p_vbat, "pb": pside, "p_load": math.fsum(vals.values())}


def shares(cfg, vals, ev):
    """battery-side watts per load: each load over the efficiency chain to VBAT, scaled to the pack side (rv-pwr's
    load_battery_share, on this evaluator)."""
    raw = []
    for L in cfg.loads:
        p = vals[L["name"]]
        if p <= 0:
            raw.append((L, 0.0))
            continue
        n, cum = L["node"], p
        while cfg.nodes[n][0] != "root":
            p_in, p_out = ev["nodes"][n][0], ev["nodes"][n][1]
            cum = cum * (p_in / p_out) if p_out > 0 else cum
            n = cfg.nodes[n][1]
        raw.append((L, cum))
    tot = math.fsum(c for _, c in raw)
    k = ev["pb"] / tot if tot else 1.0
    return [(L, c * k) for L, c in raw]


# ------------------------------------------------------------------------------------------------ the configurations
STEPS = []   # (id, status, short text) in the order they are applied


def build(pb, F, hc, upto):
    """the tree after applying the steps of section 1 up to and including `upto` (0: rv-pwr as committed)."""
    cfg = Config("step %d" % upto, pb)
    cfg.pb = pb
    rv_fan = {"cooler fan slot %d" % s: cfg.load("cooler fan slot %d" % s)["d"]["IDLE"] for s in (1, 2, 3)}
    rv_fan["two mixer fans"] = cfg.load("two mixer fans")["d"]["IDLE"]
    cfg.fan_on = dict(rv_fan)
    cfg.emcon_ov = {}
    # rv-pwr's limits (the parts as rv-pwr's notes name them)
    for n, nv in cfg.nodes.items():
        cfg.limits[n] = rv_limit(n, nv, F)
    if upto >= 1:   # M1: slot 2 and the device rail on LM5176 stages at the declared efficiency (458b2873, F-PR-04)
        for n, eff, tag in (("S2", F["s2_eff"], "S2"), ("DEV", F["dev_eff"], "SD")):
            u, _, _, rs = F["lm"][tag]
            cfg.nodes[n] = ["fixed", "VBAT", cfg.nodes[n][2], eff,
                            "%s, LM5176 stage %s (gen_sch_a.py), 5.1 V NOT PLOTTED (SNVSAI1D Fig. 6-2 is VOUT 12 V): the declared %.2f" % (cfg.nodes[n][4].split(",")[0], u, eff), "MAIN"]
            cfg.limits[n] = lm_limit(u, rs, F)
    if upto >= 2:   # M2: slot 2's card buck set to 3.456 V (O-17)
        cfg.nodes["S2A"][2] = F["s2a_v"]
        cfg.nodes["S2A"][5] = "MAIN"
    if upto >= 3:   # M3: board D on its own TPS62933 U41 from VBAT (S-99)
        cfg.nodes["D8IN"] = ["fixed", "VBAT", F["d8_v"], F["d8_eff"], "+5V_D8IN, TPS62933 %s from VBAT (S-99, gen_sch_a.py): the declared %.2f; a 5 V plot exists in SLUSEA4D and is not read here" % (F["d8_sw"], F["d8_eff"]), "MAIN"]
        cfg.load("board D (SA868 and logic)")["node"] = "D8IN"
        cfg.load("board D (SA868 and logic)")["status"] = "MAIN"
        cfg.limits["D8IN"] = ("TPS62933 %s" % F["d8_sw"], F["tps62933_a"], "out", "MAKER SLUSEA4D p.1 (3-A, TPS62933)", 1)
    if upto >= 4:   # M4: EMCON with both WiFi link cards unpowered (458b2873; record hc2)
        cfg.emcon_ov = dict(hc["EMCON_MAIN"])
    if upto >= 5:   # M5: board A's RSR shunt R17 in the discharge path (458b2873, S-04)
        cfg.r_path += pb.R_R17
        cfg.r_parts.append(("board A's R17, 5 mOhm (S-04)", pb.R_R17, "MAIN"))
        # the heater mat regulated to 12 V by U33 (F-PR-06; only the cold overlay uses it)
        cfg.nodes["HEAT"] = ["fixed", "VBAT", F["heat_v"], F["heat_eff"], "VHEAT, TPS62933 %s at the declared %.2f (F-PR-06)" % (F["heat_sw"], F["heat_eff"]), "MAIN"]
        cfg.heat_on = pb.same(F["heat_v"] ** 2 / pb.R_HEAT, "S")
        cfg.limits["HEAT"] = ("TPS62933 %s" % F["heat_sw"], F["tps62933_a"], "out", "MAKER SLUSEA4D p.1 (3-A, TPS62933)", 1)
    if upto >= 6:   # D1: the battery FET pair Q39, Q40 (L4-E11 15c, DRAFTED)
        r_pair = F["fet_bound"] / 2.0
        cfg.r_path += r_pair
        cfg.r_parts.append(("Q39 and Q40, BUK6Y10-30P in parallel at L4-E11's 150 C bound %.3f mOhm each (DRAFTED)" % (F["fet_bound"] * 1000), r_pair, "DRAFTED"))
    if upto >= 7:   # D2: board E's auxiliary domain on VSYS_E behind U42 (L4-E11 15a, DRAFTED)
        r_br = F["vsyse_drop"][1] / F["vsyse_drop"][0]
        cfg.nodes["VSYSE"] = ["series", "VBAT", 14.4, r_br, "VSYS_E over the dock's pin 1 behind U42 (L4-E11 15a, DRAFTED): %.4f Ohm from L4-E11's %.4f V at %.4f A" % (r_br, F["vsyse_drop"][1], F["vsyse_drop"][0]), "DRAFTED"]
        cfg.nodes["E5V"][1] = "VSYSE"
        cfg.nodes["E5V"][5] = "DRAFTED"
        cfg.limits["VSYSE"] = ("U42 TPS16630 (drafted)", F["u42"][0], "in_floor", "L4-E11 18b: U42's least limit, R228 11 kOhm (DRAFTED)", 1)
    if upto >= 8:   # D3: the mixers, Layer 7's pick on U22's 12.0 V rail (L4-E11 18a, DRAFTED; D-18 SESSION)
        eta = F["fan12_eff_draft"]
        iq = F["vsyse_decl"][4] / 1000.0
        cfg.nodes["FAN12"] = ["fixedq", "VSYSE", F["u22_out"][0], (eta, iq), "+12V_FAN, LTC3115-1 U22 on VSYS_E (L4-E11 18a, DRAFTED): %.2f (an ASSUMPTION of L4-E11) and %.0f mA quiescent at the input" % (eta, iq * 1000), "DRAFTED"]
        L = cfg.load("two mixer fans")
        hi = 2 * float(F["mixer"][5])
        new = pb.up(rv_fan["two mixer fans"][0], rv_fan["two mixer fans"][1], hi, "R")
        L["node"], L["status"] = "FAN12", "DRAFTED"
        L["src"] = "Layer 7's pick, two Sanyo Denki %s, %s V, %s A, %s W each at full speed (l7pwr, D-18 SESSION); LOW and PLAN keep rv-pwr's duty figures, the duty the controls set (R-150) being unset" % (F["mixer"][0], F["mixer"][1], F["mixer"][4], F["mixer"][5])
        L["d"] = {st: (pb.OFF if is_off(t) else new) for st, t in L["d"].items()}
        cfg.fan_on["two mixer fans"] = new
        cfg.limits["FAN12"] = ("LTC3115-1 U22 (drafted)", F["u22_maxload"][1], "out", "L4-E11 18a: about %.1f A at 12 V out near %.1f V in (G12, typical, read) (DRAFTED)" % (F["u22_maxload"][1], F["u22_maxload"][0]), 1)
    if upto >= 9:   # D4: the coolers, Layer 7's pick on a per-slot TPS61089 step-up (l8r2 item 1, DRAFTED)
        for s in (1, 2, 3):
            n = "S%dF" % s
            cfg.nodes[n] = ["fixed", "S%d" % s, F["fans12_rail"][0], F["su_eta"], "slot %d's cooler fan 12 V, a TPS61089 step-up from +5V_S%d (l8r2 item 1, DRAFTED): %.2f (an ASSUMPTION of l8r2)" % (s, s, F["su_eta"]), "DRAFTED"]
            L = cfg.load("cooler fan slot %d" % s)
            lo, pl = rv_fan[L["name"]][0], rv_fan[L["name"]][1]
            new = pb.up(lo, pl, float(F["cooler"][5]), "R")
            L["node"], L["status"] = n, "DRAFTED"
            L["src"] = "Layer 7's pick, Sanyo Denki %s, %s V, %s A, %s W at full speed (l7pwr, D-18 SESSION); LOW and PLAN keep rv-pwr's duty figures (the module's Fan_PWM sets the duty)" % (F["cooler"][0], F["cooler"][1], F["cooler"][4], F["cooler"][5])
            L["d"] = {st: (pb.OFF if is_off(t) else new) for st, t in L["d"].items()}
            cfg.fan_on[L["name"]] = new
            cfg.limits[n] = ("TPS61089 and its eFuse (drafted)", F["su_efuse"][0], "out", "l8r2 item 1: the fan eFuse's least limit at 12 V (ILM 1.87 k) (DRAFTED)", 1)
    if upto >= 10:  # D5: PANEL_5V behind the eFuse U901 (l8r2 item 3, DRAFTED)
        cfg.nodes["PNL"] = ["series", "DEV", cfg.nodes["DEV"][2], F["ron_lo"], "PANEL_5V behind U901, a TPS259631 (l8r2 item 3, DRAFTED): RON at most %.4f Ohm (SLVSET8A, the row l8r2 prints)" % F["ron_lo"], "DRAFTED"]
        L = cfg.load("panel board C")
        L["node"], L["status"] = "PNL", "DRAFTED"
        cfg.limits["PNL"] = ("TPS259631 U901 (drafted)", F["pnl_efuse"][0], "out", "l8r2 item 3: U901's least limit, ILM 604 Ohm (DRAFTED)", 1)
    return cfg


def rv_limit(n, nv, F):
    note = nv[4]
    count = 3 if re.search(r"\bthree\b", note) else 1
    for part, key, basis in (("AP64500", "ap64500_a", "MAKER DS41979 p.1"), ("AP63203", "ap632_a", "MAKER DS41326 p.1"),
                             ("AP63205", "ap632_a", "MAKER DS41326 p.1"), ("TPS62933", "tps62933_a", "MAKER SLUSEA4D p.1 (3-A, TPS62933)"),
                             ("AP2112K", "ap2112_a", "MAKER AP2112 p.1 (600 mA min.)"), ("TLV75533", "tlv755_a", "MAKER SBVS320D p.1")):
        if part in note:
            u = re.search(r"\b(U\d+(?:/U\d+)*)", note)
            return ("%s %s%s" % (part, u.group(1) if u else "", " (each of three)" if count == 3 else ""), F[key], "out", basis, count)
    m = re.search(r"LM5176 (U\d+)", note)
    if m and n in ("PA", "HF"):
        tag = {"PA": "PA", "HF": "HF"}[n]
        return lm_limit(m.group(1), F["lm"][tag][3], F)
    if n == "MON":
        return ("TPS259631 U21", F["mon_ilm"], "in_floor", "gen_sch_a.py: ILM %.1f A nominal (750R); the least limit is not printed there" % F["mon_ilm"], 1)
    return None


def lm_limit(u, rs, F):
    lim = F["vsns"][0] / (rs * (1 + F["shunt_tol"]))
    return ("LM5176 %s, average loop on %.0f mOhm" % (u, rs * 1000), lim, "out",
            "VSNS %.0f mV minimum (SNVSAI1D) over %.0f mOhm at +%.0f %% (gen_sch_a.py)" % (F["vsns"][0] * 1000, rs * 1000, F["shunt_tol"] * 100), 1)


def state_spec(cfg, hc, key):
    """(base state, overrides) of a state key."""
    if key == "RED2":
        return "RED", hc["RED2"]
    if key == "SURV":
        return "RED", hc["SURV"]
    if key == "SURVR":
        return "RED", hc["SURVR"]
    if key == "EMCON":
        return "EMCON", cfg.emcon_ov
    return key, {}


STATE_NAME = {"IDLE": "PS-IDLE", "IDLESPEC": "PS-IDLE-SPEC", "TYP": "PS-TYP", "BUSY": "PS-BUSY", "RED": "PS-RED (slot 3 alone)",
              "REDB": "PS-RED-b", "EMCON": "PS-EMCON", "ALLTX": "PS-ALLTX", "RED2": "PS-RED2 (slots 2 and 3)",
              "SURV": "PS-SURV (slot 2 alone)", "SURVR": "PS-SURV-R (the heat stage)"}


def run_state(cfg, hc, key, scen, extra=None, **kw):
    base, ov = state_spec(cfg, hc, key)
    ov = dict(ov)
    if extra:
        ov.update(extra)
    vals = values(cfg, base, ov, SCEN.index(scen))
    return vals, evaluate(cfg, vals, scen, **kw)


STEP_TEXT = [
    ("R0", "RV", "rv-pwr as committed: the boards as generated at 1f614233 (R_DIST 22.5 mOhm, AP64500 curves on every 5.1 V rail, board D on +5V_DEV, the representative fans)"),
    ("M1", "ON MAIN", "slot 2 and the device rail are LM5176 stages since 458b2873 (F-PR-04): their 5.1 V output is NOT PLOTTED, so the generator's declared efficiency replaces rv-pwr's AP64500 curve (rv-pwr's own rule for an unplotted point)"),
    ("M2", "ON MAIN", "slot 2's card buck is set to 3.456 V (O-17, gen_sch_b.py): the 5G module's watts unchanged, its buck's output current lower"),
    ("M3", "ON MAIN", "board D's 5 V comes from its own TPS62933 U41 on VBAT since S-99 (gen_sch_a.py +5V_D8IN), no longer through +5V_DEV"),
    ("M4", "ON MAIN", "EMCON removes both WiFi link cards' supplies since 458b2873 (record hc2's EMCON_MAIN)"),
    ("M5", "ON MAIN", "board A's 5 mOhm RSR shunt R17 is in the pack's discharge path since 458b2873 (S-04); the heater mat is regulated to 12.0 V by U33 since 458b2873 (F-PR-06, the cold overlay only)"),
    ("D1", "DRAFTED", "L4-E11 15c: the BQ25730's battery FET pair Q39, Q40 (BUK6Y10-30P in parallel) in the pack path, at L4-E11's 150 C RDS(on) bound (apply_gen_sch_a_charger.py, not applied)"),
    ("D2", "DRAFTED", "L4-E11 15a: board E's auxiliary domain (U12, the controller, the mixers) on VSYS_E over the dock's pin 1 behind the eFuse U42 (apply_gen_sch_e_aux.py, not applied)"),
    ("D3", "DRAFTED", "L4-E11 18a with Layer 7's D-18: the two mixers are Sanyo Denki 9WL0612P4H001 on U22's 12.0 V rail (LTC3115-1, 0.85 assumed, 16 mA quiescent) (apply_gen_sch_e_aux.py, not applied)"),
    ("D4", "DRAFTED", "l8r2 item 1 with Layer 7's D-18: the three coolers are Sanyo Denki 9WPA0412P6G001 on a per-slot TPS61089 step-up from +5V_Sn (0.85 assumed) (apply_gen_sch_b_fans12.py, not applied)"),
    ("D5", "DRAFTED", "l8r2 item 3: PANEL_5V behind the eFuse U901 (TPS259631), its RON in series with the panel (apply_gen_sch_b_panel5v.py, not applied)"),
]

NOT_MODELLED = [
    ("l8gnd (GND-002 and the HOT-R1 SLOT_EN hold)", "ground bonding and a logic hold: no load and no converter; nothing for the budget"),
    ("l8r2 item 2 (the VBUS20 over-voltage cut-off) and item 4 (J_QMX and J_CAM on the JST PH land)", "the charge path's protection and a connector land: no battery-side load"),
    ("l8r2's board D 3.3 V eFuse (apply_gen_sch_a_d8v3.py)", "a TPS259631 in series with board D's 0.06 A logic: under a milliwatt"),
    ("L4-E4, L4-E5, L4-E6, L4-E7, L4-E8, L4-E13 (the front end's limits, the source control, the fault handling, the solar stage, the VBUS20 bank, the panel)", "the source and charge path, not the battery-side loads; L4-E8's ballasts enter the charging balance (section 8, B4) as L4-E12 counts them"),
    ("L4-E9's U17 on R227 (the PoE stage's sense)", "5 mOhm in the PoE stage's input, which is off in every state; 1.8 mW at the outlet's 0.6 A, under the model's rounding"),
    ("L4-E10 (the cell and its thermal design) and L4-E12 (the electronics' thermal)", "the pack model and the heat: this record's pack-side watts are their input, not the other way round"),
    ("the rails' INA226 shunts (5 and 6 mOhm on the slot, device, PA and HF rails)", "not in rv-pwr's tree; their I2R is bounded in section 5 per state from the rails' own currents"),
    ("the BQ25730's own quiescent draw on battery", "no figure read in this record; a charger's battery-only quiescent is milliwatts against the states' tens of watts"),
    ("the USB-C outlet's tablet budget (an 18 W cap, a proposal) and source-only operation", "an outlet overlay and a source-side question (L4-E11 section 3); the system-node demand per state is printed for it in section 3"),
]


def ap64500_proxy(cfg, ev, n):
    """the AP64500 curve at the point an LM5176 5.1 V stage now runs (rv-pwr's model at 1f614233): the other end of
    M1's unplotted efficiency."""
    pb = cfg.pb
    p_in, p_out, i, eta, vin = ev["nodes"][n]
    return pb.eff_curve("AP64500_5V", vin, i) if p_out > 0 else 1.0


def compute():
    pb = load_rvpwr()
    F = parse_inputs(pb)
    hc = hc2_states(pb)
    R = {"pins": [(k, PINS[k], sha16(k)) for k in PINS], "F": F, "pred": {}}
    cfgs = [build(pb, F, hc, i) for i in range(len(STEP_TEXT))]
    RV, DRAWN, DRAFTED = cfgs[0], cfgs[5], cfgs[-1]
    R["cfgs"] = {"RV": RV, "DRAWN": DRAWN, "DRAFTED": DRAFTED}
    R["r_path"] = {k: (c.r_path, c.r_parts) for k, c in R["cfgs"].items()}

    # ---- 2. the model check: this evaluator on rv-pwr's tree against rv-pwr's own functions
    worst = 0.0
    for st in pb.STATES:
        for sc in SCEN:
            mine = run_state(RV, hc, st, sc)[1]["pb"]
            ref = pb.state_full(st, sc)["pb"]
            worst = max(worst, abs(mine - ref))
    for key in ("RED2", "SURV", "SURVR"):
        for sc in SCEN:
            mine = run_state(RV, hc, key, sc)[1]["pb"]
            ref = pb.state_full("RED", sc, state_spec(RV, hc, key)[1])["pb"]
            worst = max(worst, abs(mine - ref))
    R["check_worst"] = worst
    committed = {}
    for m in re.finditer(r"^(PS-[A-Za-z-]+)\s+load\s+([\d.]+) \| battery\s+([\d.]+) /\s+([\d.]+) /\s+([\d.]+)", text("rvpwr_out"), re.M):
        committed[m.group(1)] = tuple(float(x) for x in m.groups()[1:])
    R["committed"] = committed

    # ---- 3. totals
    tot = {}
    for cname, cfg in R["cfgs"].items():
        for st in STATES:
            row = {}
            for sc in SCEN:
                vals, ev = run_state(cfg, hc, st, sc)
                row[sc] = {"pb": ev["pb"], "vbat": ev["p_vbat"], "load": ev["p_load"],
                           "i14": pb.pack_current(ev["p_vbat"], 14.4, cfg.r_path)}
            vals, ev = run_state(cfg, hc, st, "plan")
            sh = shares(cfg, vals, ev)
            row["tiers"] = {t: math.fsum(c for L, c in sh if L["d"][state_spec(cfg, hc, st)[0]][3] == t and vals[L["name"]] > 0) for t in "SRDT"}
            row["drafted_share"] = math.fsum(c for L, c in sh if L["status"] == "DRAFTED")
            tot[(cname, st)] = row
    R["tot"] = tot

    # ---- 4. the waterfall, PLAN at the pack side
    wf = []
    for i, cfg in enumerate(cfgs):
        wf.append({st: run_state(cfg, hc, st, "plan")[1]["pb"] for st in STATES})
    R["wf"] = wf
    wf_hi = []
    for i, cfg in enumerate(cfgs):
        wf_hi.append({st: run_state(cfg, hc, st, "hi")[1]["pb"] for st in STATES})
    R["wf_hi"] = wf_hi

    # ---- 5. per state: loads, rails, converters against their limits (DRAWN and DRAFTED)
    per = {}
    margins = []
    for cname in ("DRAWN", "DRAFTED"):
        cfg = R["cfgs"][cname]
        for st in STATES:
            evs = {sc: run_state(cfg, hc, st, sc) for sc in SCEN}
            floor = run_state(cfg, hc, st, "hi", vpack=F["vsys"][0])[1]
            loads = []
            vals_p, ev_p = evs["plan"]
            sh = dict((L["name"], c) for L, c in shares(cfg, vals_p, ev_p))
            base = state_spec(cfg, hc, st)[0]
            for L in cfg.loads:
                v3 = tuple(evs[sc][0][L["name"]] for sc in SCEN)
                if v3 == (0.0, 0.0, 0.0):
                    continue
                ov = state_spec(cfg, hc, st)[1]
                tier = L["d"][base][3]
                if ov and L["name"] in ov and L["name"] not in cfg.fan_on:
                    tier = ov[L["name"]][3]
                loads.append((L["name"], L["node"], v3, sh[L["name"]], tier, L["status"]))
            rails = []
            for n, nv in cfg.nodes.items():
                r3 = tuple(evs[sc][1]["nodes"].get(n, (0, 0, 0, 1, 0)) for sc in SCEN)
                if r3[2][1] <= 0:
                    continue
                lim = cfg.limits.get(n)
                row = {"node": n, "kind": nv[0], "vout": nv[2], "status": nv[5], "note": nv[4],
                       "p_out": tuple(r[1] for r in r3), "i_out": tuple(r[2] for r in r3), "eta": r3[1][3],
                       "loss": r3[1][0] - r3[1][1], "lim": lim}
                if lim:
                    cnt = lim[4]
                    if lim[2] == "out":
                        i_pl, i_hi = r3[1][2] / cnt, r3[2][2] / cnt
                    else:
                        fl = floor["nodes"][n]
                        i_pl, i_hi = evs["plan"][1]["nodes"][n][0] / F["vsys"][0] / cnt, fl[0] / F["vsys"][0] / cnt
                    row["i_judged"] = (i_pl, i_hi)
                    row["margin"] = (lim[1] - i_pl, lim[1] - i_hi)
                    margins.append((cname, st, n, lim, i_pl, i_hi))
                rails.append(row)
            shunt = 0.0
            for n, rs in (("S1", 0.005), ("S2", 0.006), ("S3", 0.005), ("DEV", 0.006), ("PA", 0.006), ("HF", 0.010)):
                if n in evs["hi"][1]["nodes"]:
                    i = evs["hi"][1]["nodes"][n][2]
                    shunt += i * i * rs
            per[(cname, st)] = {"loads": loads, "rails": rails, "shunt_hi": shunt}
    R["per"] = per
    R["margins"] = margins

    # ---- 6. the pack current against the contract (I_CONT continuous to the gauge's CUV, I_PEAK)
    v_cuv = F["cuv"] * F["series"]
    R["v_stack"] = (16.8, 14.4, 12.0, v_cuv)
    rows = []
    overlay = [
        ("PS-TYP plus PoE", "TYP", {"PoE outlet (delivered outside)": pb.POE_ON}, "sustained"),
        ("PS-TYP plus USB-C", "TYP", {"USB-C outlet (delivered outside)": pb.PD_ON}, "sustained"),
        ("PS-TYP plus both outlets", "TYP", {"PoE outlet (delivered outside)": pb.POE_ON, "USB-C outlet (delivered outside)": pb.PD_ON}, "sustained"),
        ("PS-BUSY plus both outlets", "BUSY", {"PoE outlet (delivered outside)": pb.POE_ON, "USB-C outlet (delivered outside)": pb.PD_ON}, "sustained"),
        ("PA keyed alone over PS-IDLE-SPEC, PA at 75 W", "IDLESPEC", pb.PA_75, "key-down"),
        ("PA keyed alone over PS-IDLE-SPEC, PA at 113 W", "IDLESPEC", pb.PA_113, "key-down"),
        ("PA keyed alone over PS-TYP, PA at 75 W", "TYP", pb.PA_75, "key-down"),
        ("PA keyed alone over PS-TYP, PA at 113 W", "TYP", pb.PA_113, "key-down"),
        ("PS-TYP plus the heater (cold overlay)", "TYP", "HEAT", "sustained"),
        ("PS-RED plus the heater (cold overlay)", "RED", "HEAT", "sustained"),
    ]
    R["overlay"] = overlay
    for st in STATES:
        kind = "key-down" if st == "ALLTX" else "sustained"
        rows.append((STATE_NAME[st], st, None, kind))
    for lab, st, ov, kind in overlay:
        rows.append((lab, st, ov, kind))
    pc = []
    for lab, st, ov, kind in rows:
        r = {"label": lab, "kind": kind}
        for cname in ("RV", "DRAWN", "DRAFTED"):
            cfg = R["cfgs"][cname]
            ovx = {"pack heater mat (cold overlay)": cfg.heat_on} if ov == "HEAT" else ov
            for sc in ("plan", "hi"):
                ev = run_state(cfg, hc, st, sc, extra=ovx)[1]
                r[(cname, sc)] = {"pb": ev["pb"], "I": tuple(pb.pack_current(ev["p_vbat"], v, cfg.r_path) for v in R["v_stack"]),
                                  "V_cont": ev["p_vbat"] / F["i_cont"] + F["i_cont"] * cfg.r_path,
                                  "V_peak": ev["p_vbat"] / F["i_peak"] + F["i_peak"] * cfg.r_path}
        pc.append(r)
    R["pc"] = pc

    # ---- 7. D-11's floors on rv-pwr's method
    d11 = {}
    for cname in ("RV", "DRAWN", "DRAFTED"):
        cfg = R["cfgs"][cname]
        r_rv = pb.R_DIST + (pb.R_R17 if cname == "RV" else 0.0)    # RV: rv-pwr's main_pack_path_R17 record
        r = cfg.r_path if cname != "RV" else r_rv
        typ = {}
        for s in (1, 2, 3):
            typ["CM5 slot %d" % s] = cfg.load("CM5 slot %d" % s)["d"]["TYP"]
            typ["NVMe slot %d" % s] = cfg.load("NVMe slot %d" % s)["d"]["TYP"]
        typ["WiFi link card 2 (standby)"] = pb.OFF
        rows_ = {}
        for lab, st, ov, sc, fl in (("all-transmit basis: non-transmit typical, standby card off, high", "ALLTX", typ, "hi", F["floor"]),
                                    ("the same with the heater on", "ALLTX", {**typ, "pack heater mat (cold overlay)": "HEAT"}, "hi", F["floor"]),
                                    ("PA alone over PS-TYP, PA at 113 W, the rest at plan", "TYP", pb.PA_113, "plan", F["pa_floor"])):
            ovx = dict(ov)
            if ovx.get("pack heater mat (cold overlay)") == "HEAT":
                ovx["pack heater mat (cold overlay)"] = cfg.heat_on if cname != "RV" else pb.same(7.5 / 0.88, "S")
                if cname == "RV":
                    # rv-pwr's main_pack_path_R17 row: main's regulated heater at its declared 0.88, added at VBAT
                    ovx.pop("pack heater mat (cold overlay)")
            ev = run_state(cfg, hc, st, sc, extra=ovx)[1]
            pv = ev["p_vbat"] + (7.5 / 0.88 if (cname == "RV" and "heater" in lab) else 0.0)
            v_stack = pv / F["i_peak"] + F["i_peak"] * r
            rc = {k: v_stack + F["i_peak"] * F["series"] * rr / 3.0 for k, rr in pb.R_CELL.items()}
            rows_[lab] = {"vbat_W": pv, "floor": fl, "V_stack": v_stack, "V_rest": rc, "margin_hi": fl - rc["hi"],
                          "r_cell_max": (fl - v_stack) * 3.0 / (F["series"] * F["i_peak"])}
        d11[cname] = {"r": r, "rows": rows_}
    R["d11"] = d11
    R["d11_rv_record"] = pb  # for the record's own figures below
    # rv-pwr's committed main_pack_path_R17 margins, from its JSON output (read, not recomputed)
    rvj = text("rvpwr_out")
    R["rv_d11_main"] = grab(flat(rvj), r'"all-transmit basis: non-transmit typical, standby card off, high": \{"vbat_W": ([\d.]+), "floor_V": [\d.]+, "V_stack_at_18A": ([\d.]+), "V_rest_pack": \{"lo": [\d.]+, "plan": [\d.]+, "hi": ([\d.]+)\}, "margin_V_at_R_hi": ([\d.-]+)', "rv-pwr's main R17 D-11 row", 4)

    # ---- 8. the reconciliation with Layer 4
    rec = reconcile(pb, F, hc, R, cfgs)
    R["rec"] = rec

    # ---- 9. sensitivities
    R["sens"] = sensitivities(pb, F, hc, R)
    R["curves"] = curves(pb, F, hc, R)

    # ---- 10. findings and 11. predicates
    R["hc_emcon"] = list(hc["EMCON_MAIN"].keys())
    R["findings"] = findings(pb, F, R)
    R["classified"] = classify(pb, F, R)
    predicates(pb, F, R)
    return R


def t_to(q, g, c, dt):
    """hours for one node of heat capacity c (J/K) and conductance g (W/K), heated by q (W), to rise dt (K)."""
    x = 1.0 - dt * g / q
    return float("inf") if x <= 0 else -(c / g) * math.log(x) / 3600.0


def t_at(q, g, c, t0, h):
    return t0 + (q / g) * (1.0 - math.exp(-g * h * 3600.0 / c))


def reconcile(pb, F, hc, R, cfgs):
    rec = []
    tot = R["tot"]

    def pbp(c, st, sc="plan"):
        return tot[(c, st)][sc]["pb"]

    # R1 rv-pwr's figures as Layer 4 quotes them
    pa_idle = run_state(R["cfgs"]["RV"], hc, "IDLESPEC", "plan", extra=pb.PA_113)[1]["pb"]
    m = F["l4e9_modes"]
    ours = (pbp("RV", "IDLESPEC"), pbp("RV", "ALLTX"), pbp("RV", "ALLTX", "hi"), pa_idle)
    cur = {}
    for c in ("DRAWN", "DRAFTED"):
        cur[c] = (pbp(c, "IDLESPEC"), pbp(c, "ALLTX"), pbp(c, "ALLTX", "hi"),
                  run_state(R["cfgs"][c], hc, "IDLESPEC", "plan", extra=pb.PA_113)[1]["pb"])
    rec.append({"id": "R1", "what": "L4-E9's modes (1d): PS-IDLE-SPEC, PS-ALLTX plan and high, the PA keyed alone at 113 W over PS-IDLE-SPEC (W at the pack)",
                "theirs": m, "repro": tuple(round(x, 1) for x in ours), "equal": all(abs(round(a, 1) - b) < 1e-9 for a, b in zip(ours, m)),
                "cur": {c: tuple(round(x, 3) for x in v) for c, v in cur.items()},
                "why": "rv-pwr's figures, which L4-E9 quotes at 0.1 W; the current design moves them by the steps of section 4"})
    rec.append({"id": "R1b", "what": "the review's and L4-E12's profile (PS-IDLE-SPEC at the pack, W)", "theirs": (F["rev_b4"][0], F["b4"][4]),
                "repro": (round(ours[0], 5), round(ours[0], 3)), "equal": abs(round(ours[0], 5) - F["rev_b4"][0]) < 1e-9 and abs(round(ours[0], 3) - F["b4"][4]) < 1e-9,
                "cur": {c: (round(cur[c][0], 5),) for c in cur}, "why": "the same figure at five and three places"})

    # R2 B4, the charging heat as a balance (the review, L4-E12 12b)
    p0, into, efe, ech, pin_ = F["rev_b4"]
    chi = 12 * (pb.ICHG / 3) ** 2 * pb.R_CELL["plan"]
    eta = efe * ech

    def b4(p):
        pin = (p + into) / eta
        return pin, into - chi, pin - (into - chi), p / eta - p, into / eta - into

    r0 = b4(p0)
    rec.append({"id": "R2", "what": "B4: the charging heat with the profile running (W): input, stored, heat; the source path and the charge path",
                "theirs": (F["rev_q"][0], F["rev_q"][1], F["rev_q"][2], F["b4"][5], F["b4"][6]),
                "repro": (round(r0[0], 6), round(r0[1], 3), round(r0[2], 6), round(r0[3], 5), round(r0[4], 5)),
                "equal": abs(round(r0[0], 6) - F["rev_q"][0]) < 1e-9 and abs(round(r0[2], 6) - F["rev_q"][2]) < 1e-9 and abs(round(r0[3], 5) - F["b4"][5]) < 1e-9 and abs(round(r0[4], 5) - F["b4"][6]) < 1e-9 and abs(chi - F["b4"][7]) < 1e-9 and abs(pb.ICHG * 15.5 - into) < 1e-9 and abs(round(r0[2] + F["rev_ballast"][0], 6) - F["rev_ballast"][1]) < 1e-9 and abs(round(r0[2] + F["b4_ballast"][0], 3) - F["b4_ballast"][1]) < 1e-9 and abs(F["rev_ballast"][0] - F["b4_ballast"][0]) < 1e-9,
                "cur": {c: tuple(round(x, 4) for x in b4(cur[c][0])) + (round(b4(cur[c][0])[2] + F["b4_ballast"][0], 4),) for c in cur},
                "ballast": (F["rev_ballast"][0], F["rev_ballast"][1], round(r0[2] + F["rev_ballast"][0], 6), F["b4_ballast"][1], round(r0[2] + F["b4_ballast"][0], 3)),
                "why": "the profile moves by dP and the heat by dP / %.3f: dP itself plus the source path's %.4f per watt (section 4 gives dP step by step); on shore the profile is fed through the charger to VSYS and does not cross the pack path, so the pack-side figure the balance carries overstates it by the pack path's I2R (DRAFTED: %.4f W), the conservative side" % (eta, 1 / eta - 1, cur["DRAFTED"][0] - tot[("DRAFTED", "IDLESPEC")]["plan"]["vbat"])})

    # R3 B7, the battery-only run to C1 (the review, L4-E12 12c)
    q0, g, ckj, t0, t1, h0 = F["rev_b7"]
    c = ckj * 1000.0
    qr = p0 + pb.pack_i2r(p0)
    hr = t_to(q0, g, c, t1 - t0)
    tu = t_at(q0, g, c, t0, F["rev_b7u"][1])
    hr_unrounded = t_to(qr, g, c, t1 - t0)
    curb7 = {}
    for cn in cur:
        q = cur[cn][0] + pb.pack_i2r(cur[cn][0])
        run_h = F["usable_wh"] / cur[cn][0]
        curb7[cn] = (round(q, 3), round(t_to(q, g, c, t1 - t0), 5), round(t_at(q, g, c, t0, F["rev_b7u"][1]), 3), round(run_h, 3), round(t_at(q, g, c, t0, run_h), 3))
    rec.append({"id": "R3", "what": "B7: case heat (W), hours to C1's +50 C from +20 C at %.4f W/K and %.0f kJ/K, the air unshed at %.2f h (C)" % (g, ckj, F["rev_b7u"][1]),
                "theirs": (q0, h0, F["rev_b7u"][0]), "repro": (round(qr, 3), round(hr, 5), round(tu, 3)),
                "equal": abs(round(qr, 3) - q0) < 1e-9 and abs(round(hr, 5) - h0) < 1e-9 and abs(round(tu, 3) - F["rev_b7u"][0]) < 1e-9,
                "cur": curb7, "unrounded": (round(qr, 5), round(hr_unrounded, 5)),
                "why": "the case heat is the profile plus the cells' own I2R (rv-pwr's pack_i2r), %.5f W unrounded, which the review rounds to %.3f W; on the unrounded heat C1 comes at %.5f h, %.5f h earlier, the rounding and nothing else; with the current profile C1 comes earlier still; the last two figures are the energy-only run on L4-E10's %.1f Wh at the new profile and the unshed air at its end, consequences for item 9.2 and L4-E12, not this item's figures" % (qr, q0, hr_unrounded, hr - hr_unrounded, F["usable_wh"])})

    # R4 L4-E11's VSYS_E declaration
    d = F["vsyse_decl"]
    fans_full = 2 * float(F["mixer"][5])
    i_decl = fans_full / d[2] / d[3] + d[4] / 1000.0 + d[5]
    i_plan = pb.LOADS[[x[0] for x in pb.LOADS].index("two mixer fans")][2]["IDLESPEC"][1] / d[2] / d[3] + d[4] / 1000.0 + d[5]
    vsy = {}
    for st in ("IDLESPEC", "TYP", "SURVR"):
        rr = [r for r in R["per"][("DRAFTED", st)]["rails"] if r["node"] == "VSYSE"][0]
        e5 = [r for r in R["per"][("DRAFTED", st)]["rails"] if r["node"] == "E5V"][0]
        vsy[st] = (round(rr["i_out"][1], 4), round(rr["i_out"][2], 4), round(rr["i_judged"][1], 4))
    e5 = [r for r in R["per"][("DRAFTED", "IDLESPEC")]["rails"] if r["node"] == "E5V"][0]
    ev_e5 = run_state(R["cfgs"]["DRAFTED"], hc, "IDLESPEC", "plan")[1]["nodes"]["E5V"]
    rec.append({"id": "R4", "what": "L4-E11 18b: VSYS_E at the floor with both mixers at full speed, at the plan's duty, and against U42's least limit (A, %)",
                "theirs": (d[6], F["vsyse_plan"], F["u42"][1]), "repro": (round(i_decl, 4), round(i_plan, 4), round(100 * i_decl / F["u42"][0], 1)),
                "equal": abs(round(i_decl, 4) - d[6]) < 1e-9 and abs(round(i_plan, 4) - F["vsyse_plan"]) < 1e-9 and abs(round(100 * i_decl / F["u42"][0], 1) - F["u42"][1]) < 1e-9,
                "cur": vsy, "u12": (d[5], round(ev_e5[0] / 14.4, 4)),
                "why": "L4-E11's figure is a declaration: U12 at its declared %.1f A (its input at PS-IDLE-SPEC's board E loads is %.4f A at 14.4 V here), the fans at full speed at the floor's %.3f V; this record's per state figures are the branch at 14.4 V (PLAN), 16.8 V (HIGH) and VBAT's %.3f V floor with every load at HIGH" % (d[5], ev_e5[0] / 14.4, d[3], F["vsys"][0])})

    # R5 L4-E11's battery FET pair on battery
    rp = F["fet_bound"] / 2.0
    i1, i2 = m[0] / 14.4, R["committed"]["PS-TYP"][2] / 14.4
    curp = {st: (round(tot[("DRAFTED", st)]["plan"]["i14"], 4), round(tot[("DRAFTED", st)]["plan"]["i14"] ** 2 * rp, 4)) for st in ("IDLESPEC", "TYP")}
    rec.append({"id": "R5", "what": "L4-E11 15c: the pair's loss on battery at PS-IDLE-SPEC and PS-TYP (A, W)",
                "theirs": (F["fet_idle"][0], F["fet_idle"][1], F["fet_typ"][0], F["fet_typ"][1]),
                "repro": (round(i1, 3), round(i1 * i1 * rp, 4), round(i2, 3), round(i2 * i2 * rp, 4)),
                "equal": abs(round(i1, 3) - F["fet_idle"][0]) < 1e-9 and abs(round(i1 * i1 * rp, 4) - F["fet_idle"][1]) < 1e-9 and abs(round(i2, 3) - F["fet_typ"][0]) < 1e-9 and abs(round(i2 * i2 * rp, 4) - F["fet_typ"][1]) < 1e-9,
                "cur": curp,
                "why": "L4-E11 divides the profile's rounded %.1f W and %.1f W by 14.4 V; this record solves the pack current at 14.4 V with the whole pack path (R_DIST, R17, the pair) and the current design's profile" % (m[0], R["committed"]["PS-TYP"][2])})

    # R6 and R7 L4-E12's fans' share and its heat stage
    def fan_share(cn, st):
        cfg = R["cfgs"][cn]
        vals, ev = run_state(cfg, hc, st, "plan")
        return math.fsum(cc for L, cc in shares(cfg, vals, ev) if "fan" in L["name"])
    rec.append({"id": "R6", "what": "L4-E12 8c: the fans' battery-side watts in the profile and in the heat stage (W)",
                "theirs": (F["fans_share"][0], F["fans_share_hs"][0]), "repro": (round(fan_share("RV", "IDLESPEC"), 3), round(fan_share("RV", "SURVR"), 3)),
                "equal": abs(round(fan_share("RV", "IDLESPEC"), 3) - F["fans_share"][0]) < 1e-9 and abs(round(fan_share("RV", "SURVR"), 3) - F["fans_share_hs"][0]) < 1e-9,
                "cur": {cn: (round(fan_share(cn, "IDLESPEC"), 3), round(fan_share(cn, "SURVR"), 3)) for cn in cur},
                "why": "at PLAN the fans keep rv-pwr's duty figures; the drafted step-ups and U22 (0.85 each, U22's 16 mA) add their loss"})
    rec.append({"id": "R7", "what": "L4-E12 2a and 12c: the heat stage PS-SURV-R at the pack (W)", "theirs": (F["b7_stage"][0],),
                "repro": (round(pbp("RV", "SURVR"), 3),), "equal": abs(round(pbp("RV", "SURVR"), 3) - F["b7_stage"][0]) < 1e-9,
                "cur": {cn: (round(pbp(cn, "SURVR"), 3),) for cn in cur}, "why": "record hc2's state on rv-pwr's model; section 4 moves it"})

    # R8 Layer 7's fans and converters at full speed
    cf, mx = float(F["cooler"][5]), float(F["mixer"][5])
    own = 3 * cf + 2 * mx
    l7 = own + 3 * F["l7_stepup_loss"] + F["u22_heat"][0]
    mine = own + 3 * (cf / F["su_eta"] - cf) + (2 * mx / F["fan12_eff_draft"] - 2 * mx)
    rv_plan_fans = math.fsum(pb.LOADS[[x[0] for x in pb.LOADS].index(n)][2]["IDLESPEC"][1] for n in ("cooler fan slot 1", "cooler fan slot 2", "cooler fan slot 3", "two mixer fans"))
    rec.append({"id": "R8", "what": "Layer 7 section 3: the five fans and their converters at full speed against the plan's fan figures (W)",
                "theirs": F["l7_heat"], "repro": (round(l7, 2), round(rv_plan_fans, 3)), "equal": abs(round(l7, 2) - F["l7_heat"][0]) < 1e-9 and abs(round(rv_plan_fans, 3) - F["l7_heat"][1]) < 1e-9,
                "cur": {"this record, the converters' losses unrounded": (round(mine, 4),), "U22's quiescent at 14.4 V, in neither figure": (round(F["vsyse_decl"][4] / 1000.0 * 14.4, 4),)},
                "why": "Layer 7 rounds each step-up's loss to %.2f W (%.4f W at %.2f), %.4f W in all; U22's 16 mA quiescent is in L4-E11's input current and in this record's VSYS_E, not in either heat figure" % (F["l7_stepup_loss"], cf / F["su_eta"] - cf, F["su_eta"], mine - l7)})

    # R9 l8r2's choice (a)
    per_slot = cf / F["su_eta"]
    three = 3 * per_slot / F["eta_slot"]
    cfg = R["cfgs"]["DRAFTED"]
    vals, ev = run_state(cfg, hc, "IDLESPEC", "plan")
    v2 = dict(vals)
    for s in (1, 2, 3):
        v2["cooler fan slot %d" % s] = 0.0
    off = evaluate(cfg, v2, "plan")["p_vbat"]
    for s in (1, 2, 3):
        v2["cooler fan slot %d" % s] = cf
    full = evaluate(cfg, v2, "plan")["p_vbat"]
    rec.append({"id": "R9", "what": "l8r2 item 1, choice (a): per slot on +5V_Sn, its current at 5.1 V, the three at VBAT (W, A, W)",
                "theirs": F["su_choice_a"], "repro": (round(per_slot, 3), round(per_slot / 5.1, 3), round(three, 2)),
                "equal": abs(round(per_slot, 3) - F["su_choice_a"][0]) < 1e-9 and abs(round(per_slot / 5.1, 3) - F["su_choice_a"][1]) < 1e-9 and abs(round(three, 2) - F["su_choice_a"][2]) < 1e-9,
                "cur": {"this record: the three at full speed against the three off, PS-IDLE-SPEC, VBAT": (round(full - off, 4),)},
                "why": "l8r2 takes the slot converters at a flat %.2f; this record uses the slot rails' own converters (S1 and S3 on the AP64500 curve at their operating point, S2 at the declared %.2f)" % (F["eta_slot"], F["s2_eff"])})

    # R10 rv-pwr's D-11 margin on main's pack path (R17)
    d = R["d11"]["RV"]["rows"]["all-transmit basis: non-transmit typical, standby card off, high"]
    th = R["rv_d11_main"]
    rec.append({"id": "R10", "what": "rv-pwr's D-11 all-transmit basis on main's pack path with R17: VBAT W, the stack at 18 A, the rest voltage at R_cell high, the margin under 15.5 V",
                "theirs": th, "repro": (round(d["vbat_W"], 2), round(d["V_stack"], 2), round(d["V_rest"]["hi"], 2), round(d["margin_hi"], 2)),
                "equal": all(abs(a - b) < 1e-9 for a, b in zip((round(d["vbat_W"], 2), round(d["V_stack"], 2), round(d["V_rest"]["hi"], 2), round(d["margin_hi"], 2)), th)),
                "cur": {cn: (round(R["d11"][cn]["rows"]["all-transmit basis: non-transmit typical, standby card off, high"]["vbat_W"], 2),
                             round(R["d11"][cn]["rows"]["all-transmit basis: non-transmit typical, standby card off, high"]["V_stack"], 2),
                             round(R["d11"][cn]["rows"]["all-transmit basis: non-transmit typical, standby card off, high"]["V_rest"]["hi"], 2),
                             round(R["d11"][cn]["rows"]["all-transmit basis: non-transmit typical, standby card off, high"]["margin_hi"], 2)) for cn in cur},
                "why": "section 7: the drafted pair adds its resistance at 18 A, the fans at full speed (HIGH) their power"})
    return rec


def sensitivities(pb, F, hc, R):
    cfg = R["cfgs"]["DRAFTED"]
    f2 = grab(text("rvpwr"), r"fuse DCR ([\d.]+) to ([\d.]+) mOhm", "F2's DCR range", 2)
    r_lo = pb.R_W2 + f2[0] / 1000.0 + pb.R_R17 + F["fet_25c"] * F["fet_gate"] / 2.0
    out = {}
    for st in STATES:
        base, ov = state_spec(cfg, hc, st)
        vals = values(cfg, base, ov, 1)
        lo = values(cfg, base, ov, 0)
        hi = values(cfg, base, ov, 2)
        ev0 = evaluate(cfg, vals, "plan")
        h0 = ev0["pb"]
        rows = []
        for L in cfg.loads:
            n = L["name"]
            if lo[n] == hi[n]:
                continue
            a = dict(vals); a[n] = lo[n]
            b = dict(vals); b[n] = hi[n]
            wa, wb = evaluate(cfg, a, "plan")["pb"], evaluate(cfg, b, "plan")["pb"]
            rows.append(("load", n, wa, wb, "%s: %.3f to %.3f W at the pins (%s)" % (L["status"], lo[n], hi[n], L["d"][base][3] if not (ov and n in ov and n not in cfg.fan_on) else ov[n][3])))
        w12 = evaluate(cfg, vals, "plan", vpack=12.0, vbatt=12.0)["pb"]
        w168 = evaluate(cfg, vals, "plan", vpack=16.8, vbatt=16.8)["pb"]
        rows.append(("assumption", "the pack voltage", w12, w168, "12.0 to 16.8 V: the curves' input and the pack path's I2R"))
        prox = {n: ap64500_proxy(cfg, ev0, n) for n in ("S2", "DEV")}
        wp = evaluate(cfg, vals, "plan", eff_over=prox)["pb"]
        rows.append(("assumption", "S2 and DEV, the LM5176 5.1 V stages' efficiency", wp, h0, "the AP64500 curve at their point (S2 %.3f, DEV %.3f; rv-pwr's model) to the declared %.2f (NOT PLOTTED)" % (prox["S2"], prox["DEV"], F["s2_eff"])))
        if any(vals["cooler fan slot %d" % s] > 0 for s in (1, 2, 3)):
            w80 = evaluate(cfg, vals, "plan", eff_over={"S%dF" % s: F["su_eta_lo"] for s in (1, 2, 3)})["pb"]
            rows.append(("assumption", "the cooler step-ups' efficiency (l8r2)", h0, w80, "%.2f to %.2f (TI's low figure for the inductor's worst case, l8r2)" % (F["su_eta"], F["su_eta_lo"])))
        w93 = evaluate(cfg, vals, "plan", eff_over={"FAN12": F["u22_eff_ta04"][1] / 100.0})["pb"]
        rows.append(("assumption", "U22's efficiency (L4-E11)", w93, h0, "%.2f (TA04b, typical, read at %.2f A) to %.2f (L4-E11's assumption)" % (F["u22_eff_ta04"][1] / 100.0, F["u22_eff_ta04"][0], F["fan12_eff_draft"])))
        wr = pb.battery_side(ev0["p_vbat"], 14.4, r_lo)
        rows.append(("assumption", "the pack path's resistance", wr, h0, "%.2f to %.2f mOhm: F2 at %.1f to %.1f mOhm, the pair at 25 C (%.3f mOhm each at 8.5 V drive) to its 150 C bound" % (r_lo * 1000, cfg.r_path * 1000, f2[0], f2[1], F["fet_25c"] * F["fet_gate"] * 1000)))
        rows.sort(key=lambda r: (-abs(r[3] - r[2]), r[1]))
        out[st] = {"headline": h0, "top": rows[:5], "n": len(rows), "assumptions": [r for r in rows if r[0] == "assumption"]}
    return out


def curves(pb, F, hc, R):
    cfg = R["cfgs"]["DRAFTED"]
    vs = (12.0, 13.2, 14.4, 15.6, 16.8)
    head = {}
    for st in STATES:
        base, ov = state_spec(cfg, hc, st)
        vals = values(cfg, base, ov, 1)
        head[st] = tuple(evaluate(cfg, vals, "plan", vpack=v, vbatt=v)["pb"] for v in vs)
    eff = {}
    for st in ("IDLESPEC", "TYP", "BUSY", "ALLTX", "SURVR"):
        base, ov = state_spec(cfg, hc, st)
        vals = values(cfg, base, ov, 1)
        ev = evaluate(cfg, vals, "plan")
        rows = []
        for n, nv in cfg.nodes.items():
            if n not in ev["nodes"] or ev["nodes"][n][1] <= 0:
                continue
            i = ev["nodes"][n][2]
            if nv[0] == "curve":
                if cfg.pack_fed(n):
                    rows.append((n, nv[3], i, tuple(pb.eff_curve(nv[3], v, i) for v in vs), "pack-fed"))
                else:
                    rows.append((n, nv[3], i, (pb.eff_curve(nv[3], nv[2] if False else cfg.nodes[nv[1]][2], i),), "fed at %.3f V: NOT PLOTTED, rv-pwr's VIN 12 V curve" % cfg.nodes[nv[1]][2]))
            elif nv[0] in ("fixed", "fixedq"):
                e = nv[3] if nv[0] == "fixed" else nv[3][0]
                w0 = ev["pb"]
                w1 = evaluate(cfg, vals, "plan", eff_over={n: e - 0.01})["pb"]
                rows.append((n, "declared %.2f" % e, i, (w1 - w0,), "W at the pack per point below the declared figure"))
        eff[st] = rows
    return {"vs": vs, "head": head, "eff": eff}


def findings(pb, F, R):
    raw = {"conv": {}, "pack": [], "d11": []}
    for (cname, st, n, lim, i_pl, i_hi) in R["margins"]:
        if i_hi > lim[1] or i_pl > lim[1]:
            k = (cname, n)
            raw["conv"].setdefault(k, []).append((st, i_pl, i_hi, lim))
    for r in R["pc"]:
        lim = F["i_cont"] if r["kind"] == "sustained" else F["i_peak"]
        for cname in ("DRAWN", "DRAFTED"):
            pl, hi = r[(cname, "plan")]["I"][-1], r[(cname, "hi")]["I"][-1]
            if pl > lim or hi > lim:
                raw["pack"].append((cname, r["label"], r["kind"], lim, pl, hi, r[("RV", "plan")]["I"][-1], r[("RV", "hi")]["I"][-1]))
    for cname in ("RV", "DRAWN", "DRAFTED"):
        for lab, row in R["d11"][cname]["rows"].items():
            raw["d11"].append((cname, lab, row["floor"], row["V_rest"]["hi"], row["margin_hi"], row["r_cell_max"]))
    return raw


def predicates(pb, F, R):
    P = R["pred"]
    tot = R["tot"]
    P["this evaluator reproduces rv-pwr on its own tree within 1e-9 W"] = R["check_worst"] < 1e-9
    cm = R["committed"]
    P["rv-pwr's committed headline table equals this evaluator at 0.1 W"] = all(
        abs(round(tot[("RV", st)][sc]["pb"], 1) - cm[pb.STATE_NAME[st]][1 + i]) < 1e-9 for st in pb.STATES for i, sc in enumerate(SCEN))
    for r in R["rec"]:
        P["reconciliation %s: Layer 4's figure reproduced from its own inputs" % r["id"]] = bool(r["equal"])
    P["DRAFTED's PLAN is above DRAWN's in every state"] = all(tot[("DRAFTED", st)]["plan"]["pb"] > tot[("DRAWN", st)]["plan"]["pb"] for st in STATES)
    P["DRAWN's PLAN is above RV's in every state but PS-EMCON, where the link cards are unpowered"] = all(
        (tot[("DRAWN", st)]["plan"]["pb"] > tot[("RV", st)]["plan"]["pb"]) == (st != "EMCON") for st in STATES)
    P["the waterfall's last step is DRAFTED and its first RV, on every state"] = all(
        abs(R["wf"][-1][st] - tot[("DRAFTED", st)]["plan"]["pb"]) < 1e-9 and abs(R["wf"][0][st] - tot[("RV", st)]["plan"]["pb"]) < 1e-9 for st in STATES)
    d = {c: R["d11"][c]["rows"]["all-transmit basis: non-transmit typical, standby card off, high"]["margin_hi"] for c in ("RV", "DRAWN", "DRAFTED")}
    P["D-11's all-transmit floor holds on RV and DRAWN and fails on DRAFTED"] = d["RV"] > 0 and d["DRAWN"] > 0 and d["DRAFTED"] < 0
    P["D-11's PA-alone floor holds on every tree"] = all(R["d11"][c]["rows"]["PA alone over PS-TYP, PA at 113 W, the rest at plan"]["margin_hi"] > 0 for c in ("RV", "DRAWN", "DRAFTED"))
    over_plan = [m for m in R["margins"] if m[4] > m[3][1]]
    P["no converter is over its limit at PLAN in any state, DRAWN or DRAFTED"] = not over_plan
    P["every drafted node and row is labelled DRAFTED"] = all(v[5] == "DRAFTED" for n, v in R["cfgs"]["DRAFTED"].nodes.items() if n in ("VSYSE", "FAN12", "S1F", "S2F", "S3F", "PNL")) and all(
        L["status"] == "DRAFTED" for L in R["cfgs"]["DRAFTED"].loads if L["name"] in ("two mixer fans", "cooler fan slot 1", "cooler fan slot 2", "cooler fan slot 3", "panel board C"))
    ids = [x["id"] for x in R.get("classified", [])]
    P["every margin finding has a class among the instruction's three and an owner"] = all(
        x["class"] in ("DEMONSTRATED ANALYSIS DEFECT", "ASSUMPTION TO BOUND", "PHYSICAL QUESTION") and x["owner"] for x in R.get("classified", []))
    P["the findings are L9P-F01 to L9P-F06"] = ids == ["L9P-F01", "L9P-F02", "L9P-F03", "L9P-F04", "L9P-F05", "L9P-F06"]


def classify(pb, F, R):
    """the margin findings with their class under the owner's instruction of 2 October 2026 and their owner. Each is
    built from the computed figures; the class and the owner are this record's reading (SESSION)."""
    out = []
    raw = R["findings"]
    d = {c: R["d11"][c]["rows"]["all-transmit basis: non-transmit typical, standby card off, high"] for c in ("RV", "DRAWN", "DRAFTED")}
    if d["DRAFTED"]["margin_hi"] < 0:
        dv_pair = F["i_peak"] * F["fet_bound"] / 2.0
        dv_load = (d["DRAFTED"]["vbat_W"] - d["DRAWN"]["vbat_W"]) / F["i_peak"]
        out.append({
            "id": "L9P-F01", "class": "DEMONSTRATED ANALYSIS DEFECT", "new": "new",
            "subject": "D-11's all-transmit floor on the drafted design",
            "figure": ("the basis (all transmitters keyed, non-transmit loads typical, the standby card off, every other load at HIGH) needs a pack rest voltage of %.2f V at the worst cell resistance, %.2f V over the %.1f V floor; DRAWN %.2f V (%.2f V under it), rv-pwr on main %.2f V; "
                       "the drafted pair adds %.3f V at %.0f A (%.3f mOhm at L4-E11's 150 C bound) and the drafted fans and converters at HIGH %.3f V (%.2f W more at VBAT); the floor covers a cell resistance of at most %.4f Ohm, under rv-pwr's PLAN %.3f Ohm"
                       % (d["DRAFTED"]["V_rest"]["hi"], -d["DRAFTED"]["margin_hi"], F["floor"], d["DRAWN"]["V_rest"]["hi"], d["DRAWN"]["margin_hi"], d["RV"]["V_rest"]["hi"],
                          dv_pair, F["i_peak"], F["fet_bound"] / 2 * 1000, dv_load, d["DRAFTED"]["vbat_W"] - d["DRAWN"]["vbat_W"], d["DRAFTED"]["r_cell_max"], pb.R_CELL["plan"])),
            "rule": "D-11's floor, set from the gauge's 20 A over-current trip with 10 percent margin (18 A) and the cells' 60 C window (pcb_requirements.yaml, D-11)",
            "why": "the floor's own arithmetic, re-run on the drafts' own figures, does not hold: the drafts were written after the floor and none re-derived it; a desk result on maker figures and L4-E11's bound, not an assumption a measurement would settle",
            "action": "correct the threshold set: re-derive the floor on the drafted pack path and loads (at least %.2f V rest, %.3f V a cell, plus the stated margin), or cap the fans' duty during a key-down in FW-A05 and take the basis at that duty; either is a firmware threshold and its contract text" % (d["DRAFTED"]["V_rest"]["hi"], d["DRAFTED"]["V_rest"]["hi"] / F["series"]),
            "owner": "L4-E9 (C05: the key-down rules K1 to K5 and C4, FW-A05, the floors 15.5 and 12.4 V), with L4-E11 (the pair) and the fans' feeds (L4-E11 18a, l8r2 item 1); the contract text FW-A05 is Layer 5's"})
    conv = raw["conv"]
    s13 = [(c, n, v) for (c, n), v in sorted(conv.items()) if c == "DRAFTED" and n in ("S1", "S3")]
    if s13:
        worst = max(x[2] for _, _, v in s13 for x in v)
        drawn_hi = max(m[5] for m in R["margins"] if m[0] == "DRAWN" and m[2] in ("S1", "S3"))
        pl = max(x[1] for _, _, v in s13 for x in v)
        sts = sorted(set(STATE_NAME[x[0]] for _, _, v in s13 for x in v))
        out.append({
            "id": "L9P-F02", "class": "ASSUMPTION TO BOUND", "new": "new",
            "subject": "slots 1 and 3's AP64500 at HIGH with the drafted cooler step-ups",
            "figure": "%s at HIGH: %.3f A against the AP64500's %.0f A (DS41979 p.1), %.3f A over; at PLAN at most %.3f A; DRAWN at most %.3f A at HIGH (the representative 5 V fan); the step-up takes %.3f A of the slot rail at full speed" % (", ".join(sts), worst, F["ap64500_a"], worst - F["ap64500_a"], pl, drawn_hi, float(F["cooler"][5]) / F["su_eta"] / 5.1),
            "rule": "CMP-001: the applied stress against the datasheet maximum for every part in a current path above 1 A",
            "why": "HIGH stacks every maximum at once: the CM5 at board B's declared 1.6 A (Raspberry Pi publishes no maximum), the WiFi card at AsiaRF's 9.1 W, the NVMe at its maximum and the cooler at full speed; no document puts them together",
            "action": "bound it or design it out: l8r2's own alternative (b), one 12 V fan feed from board A over the bay harness, takes the cooler off the slot rail; or the module's Fan_PWM duty limited while the slot's INA226 reads above a set current; else a bench reading of the slot's peak with the module and card loaded (TEST-PLAN power rows)",
            "owner": "l8r2 (item 1, choice (a) against (b)), with board A's generator owner for the slot rails (I-03)"})
    for (c, n), v in sorted(conv.items()):
        if n == "DEV":
            if c != "DRAFTED":
                continue
            x = v[0]
            dr = [m for m in R["margins"] if m[0] == "DRAWN" and m[2] == "DEV" and m[1] == x[0]][0]
            out.append({
                "id": "L9P-F03", "class": "ASSUMPTION TO BOUND", "new": "carried (I-03)",
                "subject": "the device rail's LM5176 average loop in PS-ALLTX at HIGH",
                "figure": "%.3f A DRAFTED, %.3f A DRAWN, against the loop's least %.4f A (VSNS %.0f mV over %.0f mOhm at +%.0f %%); PLAN %.3f A" % (x[2], dr[5], x[3][1], F["vsns"][0] * 1000, F["lm"]["SD"][3] * 1000, F["shunt_tol"] * 100, x[1]),
                "rule": "CMP-001; the generator's own I-03 comparison (gen_sch_a.py: the conditional P-tier fails the loop minimum)",
                "why": "the PS-ALLTX currents of the device rail's loads are INCONCLUSIVE on held documents (cx1, I-03); HIGH takes each at its contract or maximum",
                "action": "I-03's bench reading of the device rail in PS-ALLTX, or the rail split W2 F-PR-04 named; the loop limits rather than damages (the rail droops)",
                "owner": "board A's generator owner under I-03, with the TEST-PLAN power rows"})
        if n == "PA" and c == "DRAFTED":
            x = v[0]
            out.append({
                "id": "L9P-F04", "class": "PHYSICAL QUESTION", "new": "carried (rv-pwr; F-PR-01)",
                "subject": "the PA rail's LM5176 average loop at the PA's 113 W bound",
                "figure": "%.3f A at HIGH (W2 F-PR-02's 113 W, INFERRED) against the loop's least %.4f A; PLAN %.3f A (75 W)" % (x[2], x[3][1], x[1]),
                "rule": "CMP-001; F-PR-01 (gen_sch_a.py) sets the loop above the 6.0 A declared peak so that the 8.2 A bound meets it and the rail droops",
                "why": "the drain current at 13.8 V is the RA30H1317M1's, which its sheet states at 12.5 V only; rv-pwr carries it as a bench item",
                "action": "specimen: one RA30H1317M1 on a heat sink at 13.8 V with the design's VGG (board D, 4.30 to 4.68 V) into 50 Ohm at 144 to 146 MHz; measure the drain current at 30 W out; accept at most %.2f A; on failure the rail limits and the PA gives less than 30 W (no damage), and the choice is a lower output setting or a 5 mOhm ISNS shunt within the JST-VH lead's 10 A" % x[3][1],
                "owner": "the TEST-PLAN power rows (the bench), with board A's F-PR-01 and POWER-THERMAL section 7.2's record"})
    sus = [p for p in raw["pack"] if p[0] == "DRAFTED" and p[2] == "sustained"]
    states_hi = [p for p in sus if p[4] <= p[3] < p[5]]
    states_pl = [p for p in sus if p[4] > p[3]]
    if states_hi:
        out.append({
            "id": "L9P-F05", "class": "ASSUMPTION TO BOUND", "new": "carried (rv-pwr 7.1), moved",
            "subject": "sustained states over the pack's continuous current at HIGH at the gauge's under-voltage",
            "figure": "; ".join("%s %.2f A at HIGH (rv-pwr %.2f), PLAN %.2f A" % (p[1], p[5], p[7], p[4]) for p in states_hi) + ", against %.0f A at %.1f V (the stack at %.2f V a cell)" % (F["i_cont"], F["cuv"] * F["series"], F["cuv"]),
            "rule": "the pack's declared continuous current (pcb_pack_protection.yaml, declared_continuous_a) at every stack voltage down to CUV",
            "why": "HIGH stacks maxima; PS-BUSY's PLAN stays under (its margin at 10.0 V %.2f A, rv-pwr's %.2f A)" % (F["i_cont"] - [p for p in R["pc"] if p["label"] == "PS-BUSY"][0][("DRAFTED", "plan")]["I"][-1], F["i_cont"] - [p for p in R["pc"] if p["label"] == "PS-BUSY"][0][("RV", "plan")]["I"][-1]),
            "action": "bounded by the control rv-pwr 9.3 took (the current trigger of the module shedding, read on the gauge's pack current); the trigger's setting is re-read on the drafted figures",
            "owner": "L4-E9 (C02 and C06: the shedding and the gauge's relay), POWER-THERMAL section 9.3's control"})
    if states_pl:
        out.append({
            "id": "L9P-F06", "class": "ASSUMPTION TO BOUND", "new": "carried (rv-pwr 7.1), moved",
            "subject": "the outlets over PS-TYP and PS-BUSY at PLAN",
            "figure": "; ".join("%s %.2f A at PLAN (rv-pwr %.2f)" % (p[1], p[4], p[6]) for p in states_pl) + " at %.1f V, against %.0f A" % (F["cuv"] * F["series"], F["i_cont"]),
            "rule": "the pack's declared continuous current, as L9P-F05",
            "why": "the outlets' contracts (PoE 32.4 W, USB-C 45 W) are what their stages may deliver; rv-pwr 7.1 found these rows over and took an outlet budget",
            "action": "bounded by rv-pwr 9.3's outlet budget (and the tablet's 18 W cap, a proposal); its numbers re-read on the drafted figures",
            "owner": "L4-E9 (C03, C04 and the tablet budget)"})
    return out


def render(R):
    F, pb = R["F"], R["cfgs"]["RV"].pb
    L = []
    w = L.append
    w("L9PWR (MESHSAT-1357): LAYER 9 ITEM 9.1, THE POWER BUDGET ON THE CURRENT DESIGN, WITH MARGINS AND SENSITIVITIES. Prototype design,")
    w("desk arithmetic: nothing built, powered or measured; no figure is a measurement. RV is record rv-pwr's model as committed (the boards as")
    w("generated at 1f614233); DRAWN the generators in this tree; DRAFTED is DRAWN plus the release-guarded drafts of Layers 4 and 8 that move a")
    w("power figure, none applied. Tiers as rv-pwr's: S a primary document gives PLAN; R a document bounds the load and PLAN sits inside it by a")
    w("stated duty; D a generator declares it; T a placeholder. LOW, PLAN and HIGH are rv-pwr's three values per load; HIGH puts every load at")
    w("its maximum at once (an upper bound, not a scenario). Watts at the pack side are rv-pwr's battery W (VBAT plus the pack path's I2R at 14.4 V).")
    w("")
    w("0. INPUTS (sha256/16)")
    for k, p, s in R["pins"]:
        w("   %-10s %s  sha256 %s" % (k, p, s))
    w("")
    w("1. WHAT DIFFERS FROM RV-PWR'S MODEL, AND HOW THIS BUDGET TAKES IT (applied in this order; section 4 prints each step's effect)")
    for sid, st, tx in STEP_TEXT:
        w("   %-3s %-8s %s" % (sid, st, tx))
    w("   the figures each step reads (parsed from the pinned files):")
    w("     M1 LM5176 stages: S2 %s, DEV %s (gen_sch_a.py lm5176 calls); declared efficiency %.2f and %.2f; ISNS %.0f and %.0f mOhm at +%.0f %%; VSNS %.0f / %.0f / %.0f mV (SNVSAI1D)"
      % (F["lm"]["S2"][0], F["lm"]["SD"][0], F["s2_eff"], F["dev_eff"], F["lm"]["S2"][3] * 1000, F["lm"]["SD"][3] * 1000, F["shunt_tol"] * 100, F["vsns"][0] * 1000, F["vsns"][1] * 1000, F["vsns"][2] * 1000))
    w("     M2 +3V3_S2A at %.3f V (gen_sch_b.py)" % F["s2a_v"])
    w("     M3 +5V_D8IN: %.1f V from %s at the declared %.2f (gen_sch_a.py); board D's row keeps rv-pwr's figures (D)" % (F["d8_v"], F["d8_sw"], F["d8_eff"]))
    w("     M4 EMCON's overrides from record hc2 (pwr_red2.py, EMCON_MAIN): %s" % ", ".join(sorted(R["hc_emcon"])))
    w("     M5 R17 %.1f mOhm (rv-pwr's R_R17); VHEAT %.1f V from %s at %.2f, the mat %.2f W at 12 V (rv-pwr's R_HEAT, the mat's sheet)" % (pb.R_R17 * 1000, F["heat_v"], F["heat_sw"], F["heat_eff"], F["heat_v"] ** 2 / pb.R_HEAT))
    w("     D1 BUK6Y10-30P: %.0f mOhm at -10 V and 25 C printed, gate factor %.4f at 8.5 V, %.3f mOhm per FET at the 150 C bound (L4-E11 15c): the pair %.3f mOhm" % (F["fet_25c"] * 1000, F["fet_gate"], F["fet_bound"] * 1000, F["fet_bound"] / 2 * 1000))
    w("     D2 VSYS_E: the draft declares %.2f A (apply_gen_sch_e_aux.py); L4-E11 18b: %.4f V at %.4f A, so %.4f Ohm in the branch; U42's least limit %.4f A" % (F["aux_rails"]["VSYS_E"][1], F["vsyse_drop"][1], F["vsyse_drop"][0], F["vsyse_drop"][1] / F["vsyse_drop"][0], F["u42"][0]))
    w("     D3 the mixer %s (Layer 7): %s V, %s to %s V, %s A, %s W each at full speed; U22 out %.3f V (%.3f to %.3f), the draft's efficiency %.2f, %.0f mA quiescent; G12 about %.1f A at 12 V out near %.1f V in"
      % (F["mixer"][0], F["mixer"][1], F["mixer"][2], F["mixer"][3], F["mixer"][4], F["mixer"][5], F["u22_out"][0], F["u22_out"][1], F["u22_out"][2], F["fan12_eff_draft"], F["vsyse_decl"][4], F["u22_maxload"][1], F["u22_maxload"][0]))
    w("     D4 the cooler %s (Layer 7): %s V, %s to %s V, %s A, %s W at full speed; the step-up's efficiency %.2f (low %.2f), its eFuse %.3f / %.3f / %.3f A (l8r2); the draft's 12 V rail %.1f V, %.2f A typical, %.2f A peak"
      % (F["cooler"][0], F["cooler"][1], F["cooler"][2], F["cooler"][3], F["cooler"][4], F["cooler"][5], F["su_eta"], F["su_eta_lo"], F["su_efuse"][0], F["su_efuse"][1], F["su_efuse"][2], F["fans12_rail"][0], F["fans12_rail"][1], F["fans12_rail"][2]))
    w("     D5 U901: RON at most %.4f Ohm, limit %.3f / %.3f / %.3f A (l8r2)" % (F["ron_lo"], F["pnl_efuse"][0], F["pnl_efuse"][1], F["pnl_efuse"][2]))
    w("   how the fans are taken (SESSION, under the owner's standing rule of 26 September 2026): HIGH is the picked fan's maker figure at full speed (S);")
    w("     LOW and PLAN keep rv-pwr's duty figures (tier R), because the duty the controls set (R-150) is unset and L4-E11 18b and Layer 7 carry the same")
    w("     PLAN; a draft converter's efficiency is the draft's own assumption, its range in section 9. Why: the alternative, PLAN at full speed, would")
    w("     replace an unset duty by its maximum and hide the duty's effect inside the headline instead of showing it as a sensitivity")
    w("   the pack path (ohms): " + "; ".join("%s %.4f %s" % (cn, R["r_path"][cn][0], "(" + ", ".join("%s %.4f" % (a.split(" (")[0], b) for a, b, s in R["r_path"][cn][1]) + ")") for cn in ("RV", "DRAWN", "DRAFTED")))
    w("   NOT MODELLED, each with its reason:")
    for a, b in NOT_MODELLED:
        w("     %s: %s" % (a, b))
    w("")
    w("2. THE MODEL CHECK: this script's evaluator on rv-pwr's own tree against rv-pwr's functions (state_full), every state and scenario and record")
    w("   hc2's three states: largest difference %.1e W (%s)" % (R["check_worst"], "within 1e-9 W" if R["check_worst"] < 1e-9 else "OVER 1e-9 W"))
    cm = R["committed"]
    ok = R["pred"]["rv-pwr's committed headline table equals this evaluator at 0.1 W"]
    w("   rv-pwr's committed output (pwr_budget.out, its first table at 0.1 W) against this evaluator rounded the same way: %s" % ("equal on all eight states" if ok else "DIFFERS"))
    w("")
    w("3. PACK-SIDE TOTALS PER STATE (W): LOW / PLAN / HIGH for RV, DRAWN and DRAFTED; at VBAT (the system node, PLAN); the pack current at 14.4 V")
    w("   (PLAN, DRAFTED); DRAFTED's PLAN by tier S / R / D / T at the pack side, and the share of it on DRAFTED rows")
    w("   %-28s %-25s %-25s %-25s %8s %7s %s" % ("state", "RV", "DRAWN", "DRAFTED", "VBAT", "I14.4", "tiers S / R / D / T, drafted"))
    for st in STATES:
        cells = []
        for cn in ("RV", "DRAWN", "DRAFTED"):
            t = R["tot"][(cn, st)]
            cells.append("%7.2f /%7.2f /%7.2f" % (t["lo"]["pb"], t["plan"]["pb"], t["hi"]["pb"]))
        t = R["tot"][("DRAFTED", st)]
        w("   %-28s %-25s %-25s %-25s %8.2f %7.3f %5.1f /%5.1f /%5.1f /%5.1f, %4.2f" % (STATE_NAME[st], cells[0], cells[1], cells[2], t["plan"]["vbat"], t["plan"]["i14"],
          t["tiers"]["S"], t["tiers"]["R"], t["tiers"]["D"], t["tiers"]["T"], t["drafted_share"]))
    w("")
    w("4. THE WATERFALL: each step of section 1 applied in turn, the pack side at PLAN and (second block) at HIGH, W; the delta of each step")
    for blk, wf in (("PLAN", R["wf"]), ("HIGH", R["wf_hi"])):
        w("   %s   %s" % (blk, " ".join("%9s" % k for k in STATES)))
        prev = None
        for i, (sid, stt, tx) in enumerate(STEP_TEXT):
            row = wf[i]
            w("   %-3s %-8s %s" % (sid, stt, " ".join("%9.3f" % row[k] for k in STATES)))
            if prev is not None:
                w("       delta    %s" % " ".join("%+9.3f" % (row[k] - prev[k]) for k in STATES))
            prev = row
        w("   DRAFTED against RV %s" % " ".join("%+9.3f" % (wf[-1][k] - wf[0][k]) for k in STATES))
    w("")
    w("5. PER STATE, DRAFTED: every load (LOW / PLAN / HIGH at its pins, its battery-side share at PLAN, tier, status), every rail (output W")
    w("   LOW / PLAN / HIGH, output A PLAN / HIGH, efficiency and loss at PLAN), and each converter against its limit (the current judged at PLAN /")
    w("   HIGH, the limit, the margin at HIGH; an input-side limit is judged at VBAT's %.3f V floor with every load at HIGH). DRAWN's margins follow" % F["vsys"][0])
    w("   where its converters differ. Status: RV rv-pwr's row unchanged, MAIN a change on main since 1f614233, DRAFTED a draft not applied.")
    for st in STATES:
        P = R["per"][("DRAFTED", st)]
        w("   == %s (pack side %.3f / %.3f / %.3f W)" % (STATE_NAME[st], R["tot"][("DRAFTED", st)]["lo"]["pb"], R["tot"][("DRAFTED", st)]["plan"]["pb"], R["tot"][("DRAFTED", st)]["hi"]["pb"]))
        for (n, node, v3, sh, tier, status) in P["loads"]:
            w("     load %-44s %-8s %7.3f %7.3f %7.3f  pack %7.3f  %s %s" % (n, node, v3[0], v3[1], v3[2], sh, tier, status))
        for r in P["rails"]:
            s = "     rail %-8s %-7s %6.3f V  out %7.3f %7.3f %7.3f W  %6.3f %6.3f A  eta %5.3f  loss %6.3f W  %s" % (
                r["node"], r["kind"], r["vout"], r["p_out"][0], r["p_out"][1], r["p_out"][2], r["i_out"][1], r["i_out"][2], r["eta"], r["loss"], r["status"])
            w(s)
            if r["lim"]:
                lim = r["lim"]
                verdict = "OVER at PLAN" if r["margin"][0] < 0 else "OVER at HIGH" if r["margin"][1] < 0 else "within"
                w("          limit %-44s %6.3f A (%s): judged %6.3f / %6.3f A, margin at HIGH %+7.3f A (%+6.1f %%): %s" % (
                    lim[0], lim[1], lim[2], r["i_judged"][0], r["i_judged"][1], r["margin"][1], 100 * r["margin"][1] / lim[1], verdict))
        Pd = R["per"][("DRAWN", st)]
        diff = []
        for r in Pd["rails"]:
            if r["lim"]:
                dr = [x for x in P["rails"] if x["node"] == r["node"]]
                if not dr or abs(dr[0]["margin"][1] - r["margin"][1]) > 5e-4:
                    diff.append("%s %+.3f A" % (r["node"], r["margin"][1]))
        w("     DRAWN's margins at HIGH that differ: %s" % (", ".join(diff) if diff else "none"))
        w("     the rails' INA226 shunts at HIGH (not in the tree): %.3f W in all" % P["shunt_hi"])
    w("")
    w("6. THE PACK CURRENT (A) at the stack voltages %s V (the last the gauge's CUV, %.2f V a cell x %d), PLAN and HIGH, RV / DRAWN / DRAFTED;" % (" / ".join("%.1f" % v for v in R["v_stack"]), F["cuv"], F["series"]))
    w("   against the declared continuous %.0f A (sustained rows) or the peak %.0f A (key-down rows, which D-11's floors govern, section 7); the stack" % (F["i_cont"], F["i_peak"]))
    w("   voltage below which the row passes the limit (DRAFTED, PLAN / HIGH)")
    for r in R["pc"]:
        lim = F["i_cont"] if r["kind"] == "sustained" else F["i_peak"]
        w("   %-50s %-9s" % (r["label"], r["kind"]))
        for cn in ("RV", "DRAWN", "DRAFTED"):
            a, b = r[(cn, "plan")], r[(cn, "hi")]
            w("      %-8s PLAN %s   HIGH %s" % (cn, " ".join("%6.2f" % x for x in a["I"]), " ".join("%6.2f" % x for x in b["I"])))
        key = "V_cont" if r["kind"] == "sustained" else "V_peak"
        a, b = r[("DRAFTED", "plan")], r[("DRAFTED", "hi")]
        w("      over %.0f A below %.2f V (PLAN) / %.2f V (HIGH): %s" % (lim, a[key], b[key], "PLAN over at %.1f V" % R["v_stack"][-1] if a["I"][-1] > lim else ("HIGH over at %.1f V" % R["v_stack"][-1] if b["I"][-1] > lim else "within to %.1f V" % R["v_stack"][-1])))
    w("")
    w("7. D-11's FLOORS ON RV-PWR'S METHOD (section 7.2 there): the stack voltage at %.0f A, the rest voltage at the cell resistances %s Ohm, the" % (F["i_peak"], " / ".join("%.3f" % v for v in pb.R_CELL.values())))
    w("   margin under the floor at the highest, and the largest cell resistance the floor covers. RV is rv-pwr's main pack path (R17 added, its")
    w("   record main_pack_path_R17); the heater row adds the regulated mat as rv-pwr does (rv-pwr: 7.5 W at its declared 0.88; DRAWN and DRAFTED: U33's %.2f)" % F["heat_eff"])
    for cn in ("RV", "DRAWN", "DRAFTED"):
        D = R["d11"][cn]
        w("   %s (pack path %.4f Ohm)" % (cn, D["r"]))
        for lab, row in D["rows"].items():
            w("      %-66s VBAT %7.2f W  stack %6.3f V  rest %s V  floor %.1f V  margin %+6.3f V  R_cell covered %.4f" % (
                lab, row["vbat_W"], row["V_stack"], " / ".join("%6.3f" % row["V_rest"][k] for k in ("lo", "plan", "hi")), row["floor"], row["margin_hi"], row["r_cell_max"]))
    w("")
    w("8. THE RECONCILIATION WITH LAYER 4 (each line: their figure, this script's reproduction from their inputs, EQUAL or not, the current")
    w("   design's figure, and the difference explained)")
    for r in R["rec"]:
        w("   %s %s" % (r["id"], r["what"]))
        w("      theirs %s; reproduced %s: %s" % (r["theirs"], r["repro"], "EQUAL" if r["equal"] else "NOT EQUAL"))
        for k, v in r["cur"].items():
            w("      %s: %s" % (k, v))
        if r.get("ballast"):
            w("      with L4-E8's %.2f W of ballasts: the review's %.6f, reproduced %.6f; L4-E12's %.3f, reproduced %.3f" % r["ballast"])
        if r.get("unrounded"):
            w("      unrounded: case heat %.5f W, C1 at %.5f h" % r["unrounded"])
        if r.get("u12"):
            w("      U12: declared %.1f A; its input in PS-IDLE-SPEC here %.4f A at 14.4 V" % r["u12"])
        w("      why: %s" % r["why"])
    w("   line by line for the profile (PS-IDLE-SPEC, PLAN, pack side): the steps of section 4, each with its delta: " + "; ".join(
        "%s %+.4f W" % (STEP_TEXT[i][0], R["wf"][i]["IDLESPEC"] - R["wf"][i - 1]["IDLESPEC"]) for i in range(1, len(STEP_TEXT))))
    w("")
    w("9. SENSITIVITIES (DRAFTED): for each state's headline (the pack side at PLAN, VIN 14.4 V), the five loads or assumptions that move it most, each")
    w("   moved alone over its LOW to HIGH (a load at its pins; an assumption over its stated range), the others at PLAN; the swing is W(HIGH) - W(LOW)")
    for st in STATES:
        S = R["sens"][st]
        w("   == %s, headline %.3f W (%d candidates)" % (STATE_NAME[st], S["headline"], S["n"]))
        for kind, n, wa, wb, how in S["top"]:
            w("      %-10s %-48s %8.3f to %8.3f W, swing %+8.3f W  %s" % (kind, n, wa, wb, wb - wa, how))
        w("      every assumption: " + "; ".join("%s %+.3f W" % (n, wb - wa) for kind, n, wa, wb, how in S["assumptions"]))
    C = R["curves"]
    w("   the headline against the pack's voltage (loads at PLAN; the curves' input and the pack path's I2R at that voltage), W at %s V:" % " / ".join("%.1f" % v for v in C["vs"]))
    for st in STATES:
        w("      %-28s %s" % (STATE_NAME[st], " ".join("%8.3f" % x for x in C["head"][st])))
    w("   the converters' efficiency at their PLAN current over the pack's %.1f to %.1f V (pack-fed curves), the 5.1 V-fed ones at rv-pwr's VIN 12 V" % (C["vs"][0], C["vs"][-1]))
    w("   curve (NOT PLOTTED at their input), and each declared figure's weight: W at the pack per point of efficiency below the declared figure")
    for st, rows in C["eff"].items():
        w("   == %s" % STATE_NAME[st])
        for n, how, i, vals, note in rows:
            w("      %-7s %-16s %6.3f A  %s  %s" % (n, how, i, " ".join("%6.4f" % x for x in vals), note))
    w("")
    w("10. MARGIN FINDINGS (the rules: CMP-001's acceptance, '%s'; the pack's declared continuous %.0f A and peak %.0f A, pcb_pack_protection.yaml;" % (F["rule_cmp001"], F["i_cont"], F["i_peak"]))
    w("    D-11: '%s' A limit acting by design is reported, not hidden.) Classes per the owner's instruction of 2 October 2026: a demonstrated" % F["rule_d11"])
    w("    defect is corrected by its owner; an assumption is bounded with evidence or designed out; a physical question gets a specimen, a")
    w("    measurement, an acceptance and the consequence of failure. The class and the owner are this record's reading (SESSION).")
    for x in R["classified"]:
        w("   %s  %s  (%s)  %s" % (x["id"], x["class"], x["new"], x["subject"]))
        w("      figure: %s" % x["figure"])
        w("      rule:   %s" % x["rule"])
        w("      why:    %s" % x["why"])
        w("      action: %s" % x["action"])
        w("      owner:  %s" % x["owner"])
    w("   within their rules (no finding): every other converter in every state; U42 on VSYS_E, U22, the coolers' eFuses and U901 (DRAFTED);")
    w("   D-11's PA-alone floor on every tree; the heater rows of section 7 are over the floor on every tree, which is why the rule holds the heater")
    w("   off during any key-down (rv-pwr 7.2), so they are not a finding")
    w("")
    w("11. PREDICATES")
    for k in sorted(R["pred"]):
        w("   %-118s %s" % (k, "yes" if R["pred"][k] else "NO"))
    w("")
    w("END. Desk arithmetic on the files pinned in section 0; nothing is measured, nothing is applied, and a software test of this script")
    w("establishes the arithmetic only.")
    return "\n".join(L) + "\n"


def main():
    R = compute()
    sys.stdout.write(render(R))


if __name__ == "__main__":
    main()
