#!/usr/bin/env python3
"""l9pwr_budget.py: Layer 9 item 9.1, the power budget brought to the current design with margins and sensitivities
(MESHSAT-1357, 3 October 2026; round 2, 4 October 2026; round 3, 4 October 2026). PROTOTYPE DESIGN, DESK ARITHMETIC: nothing in
this kit has been built, powered or measured, and no figure printed here is a measurement.

Round 6 (4 October 2026 night, task T5 round 4): labels only. Section 7b, its two predicates and out 7's NEW line name the case row
C-ALLTX rev 3 (rev 2's definition, which rev 3 keeps; the recheck V3's blocker 5); no figure moves.
Round 4 (4 October 2026, task T5 on branch fnd/l9t5, case rows C-ALLTX rev 2 and C-DEV rev 1): two corrections. C1, the
state PS-ALLTX carries the standby WiFi card OFF in every scenario (REQ-018's acceptance and CONOPS 4a's PS-ALLTX row; rv-pwr's
state powered it at its placeholder, 1.0 W PLAN and 9.1 W HIGH, the challenge cx40's Q1), applied as the last step so that
every earlier step reads as before. Section 7b, the case row C-ALLTX rev 2 computed from the row's own text (every transmitter
at its HIGH figure, the monitor full, the fans running at full speed, the outlets, the heater and the standby card off, every
other load at its PS-ALLTX PLAN figure, the compute modules at their typical 4.5 W), with the pack-fed converters evaluated at
the VBAT the case itself sets (18 A at the need), beside the rows it replaces (the raw PS-ALLTX HIGH row and D-11's basis on
rv-pwr's typ_nontx, which keeps every non-transmit load but the compute modules and the NVMe at HIGH).

Round 3 (4 October 2026, the integration of set 29, branch fnd/l9r3): a tool correction, no figure moved. L4-E11's round 9
broke +12V_FAN's declaration over two source lines in apply_gen_sch_e_aux.py (finding L8P-F03 corrected: U22 named as the
source, with source_ic) and wrote a third battery FET, Q42, into apply_gen_sch_a_charger.py; a one-line pattern for the
rail's efficiency refused. Both drafts are now PARSED (ast on the draft's string constants and on the call they hold), the
battery FETs' designators and count are read from the charger draft and held equal to record l9stk's selection, and record
l9stk's protection output is read from this tree (the copy at 2c8b29fb named the automatic-retry LM5069-2; record l9stk
15.4b selects the latch-off -1, which the script now reads and prints).

Round 2 (4 October 2026, branch fnd/l9pwr2 from main 64cd25ee): the DRAFTED tree follows record l8r2 to its round 6 on
fnd/l8r3 at 89924e40 (slots 1 and 3 on board A's LM5176 stage, the coolers at full speed with no duty maximum and their row
at the envelope, board B's slot bucks at RT 200 k, the 5.1 V stages' dividers at 0.1 %), read from copies in inputs/ that
git show made, pinned by sha256 (inputs/SOURCES.txt), and record l9stk's section 15 (board P's breaker C-1 and the third
battery FET), read at round 2 from a copy at 2c8b29fb and since round 3 from this tree's l9stk_protection.out. The round 1 DRAFTED tree is rebuilt beside it so that every figure
another record took from round 1 (L4-E9 round 7, record l8r2) is reproduced from the same evaluator.

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

# W34 (Q-41 item 1, adopted in set 32): the makers' PDFs this script reads as text, each with its pdftotext options ([] is pdftotext's
# plain reading order). Each text is a verbatim input taken once on the runner by v2/docs/records/_lib/retake_pdf_text.py beside its
# PDF (a held-back sheet's text is held back with it, under held/); _lib/pdftext.py returns it byte for byte and refuses when it is
# absent, so this script never runs pdftotext; section 0 prints each text's sha256 after the pins.
# Re-take after a sheet changes: python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l9pwr
PDFTEXT = {
    "v2/vendor/diodes/diodes-ap2112-ldo.pdf": [["-l", "1"]],
    "v2/vendor/diodes/diodes-ap63200-series-buck.pdf": [["-l", "1"]],
    "v2/vendor/diodes/diodes-ap64500.pdf": [["-l", "1"]],
    "v2/vendor/power/ti-tlv755p-ldo.pdf": [["-l", "1"]],
    "v2/vendor/power/tps2596.pdf": [[]],
    "v2/vendor/ti/lm5176-datasheet.pdf": [["-layout"]],
    "v2/vendor/ti/ti-tps62933.pdf": [["-l", "1"]],
}
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PT)
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
    "l8r2_out": "v2/docs/records/l9pwr/inputs/l8r2-l8r2_drafts-89924e40.txt",
    "l8r2_fans": "v2/docs/records/l9pwr/inputs/l8r2-apply_gen_sch_b_fans12-89924e40.txt",
    "l8r2_pnl": "v2/docs/records/l8r2/apply_gen_sch_b_panel5v.py",
    "l8r2_slotlm": "v2/docs/records/l9pwr/inputs/l8r2-apply_gen_sch_a_slotlm-89924e40.txt",
    "l8r2_rt500": "v2/docs/records/l9pwr/inputs/l8r2-apply_gen_sch_b_rt500-89924e40.txt",
    "l8r2_fb01": "v2/docs/records/l9pwr/inputs/l8r2-apply_gen_sch_a_fb01-89924e40.txt",
    "l9stk_prot": "v2/docs/records/l9stk/l9stk_protection.out",
    "l4e9r7": "v2/docs/records/l9pwr/inputs/l4e9-l4e9_power_path-section30-3737df82.txt",
    "sources": "v2/docs/records/l9pwr/inputs/SOURCES.txt",
    "l8gnd_out": "v2/docs/records/l8gnd/l8gnd_drafts.out",
    "ap64500": "v2/vendor/diodes/diodes-ap64500.pdf",
    "ap632": "v2/vendor/diodes/diodes-ap63200-series-buck.pdf",
    "tps62933": "v2/vendor/ti/ti-tps62933.pdf",
    "ap2112": "v2/vendor/diodes/diodes-ap2112-ldo.pdf",
    "tlv755": "v2/vendor/power/ti-tlv755p-ldo.pdf",
    "lm5176": "v2/vendor/ti/lm5176-datasheet.pdf",
    "tps2596": "v2/vendor/power/tps2596.pdf",
    "reqs": "v2/ecad/tools/pcb_requirements.yaml",
    "rules": "v2/ecad/tools/pcb_rules.yaml",
}

# the copies in inputs/: key -> (branch, commit, the source path, the source's lines or None for the whole file)
ORIGIN = {
    "l8r2_out": ("fnd/l8r3", "89924e40", "v2/docs/records/l8r2/l8r2_drafts.out", None),
    "l8r2_fans": ("fnd/l8r3", "89924e40", "v2/docs/records/l8r2/apply_gen_sch_b_fans12.py", None),
    "l8r2_slotlm": ("fnd/l8r3", "89924e40", "v2/docs/records/l8r2/apply_gen_sch_a_slotlm.py", None),
    "l8r2_rt500": ("fnd/l8r3", "89924e40", "v2/docs/records/l8r2/apply_gen_sch_b_rt500.py", None),
    "l8r2_fb01": ("fnd/l8r3", "89924e40", "v2/docs/records/l8r2/apply_gen_sch_a_fb01.py", None),
    "l4e9r7": ("fnd/l4e9r7", "3737df82", "v2/docs/records/l4e9/l4e9_power_path.out", (2127, 2163)),
}

# read from this tree since round 3 (no copy): record l9stk is merged beside this record, and a copy of its output went stale
# (the copy at 2c8b29fb named the LM5069-2; l9stk 15.4b selects the -1). The order of regeneration is l9stk's three scripts
# (stackups, copper, protection), then this one.
IN_TREE = {"l9stk_prot": "record l9stk's protection output (section 15: board P's breaker C-1 and the third battery FET)"}

# the round 1 parser's lines that read a figure record l8r2 has since removed or superseded: set aside, not read
SET_ASIDE = [
    ("eta_slot", "l8r2's flat 0.90 for the slot converters (round 2's 7.84 W at VBAT): removed from l8r2's figures table at round 3, "
                 "the slots' own converters carry it (round 1's R9)"),
    ("l8r2's choice (a) line", "'choice (a), a step-up per slot (SELECTED): ... the three 7.56 W at VBAT': round 3's text, which quotes "
                               "this record's round 1 R9 back and was superseded by round 4's decision (2c.5); R9 now reproduces round 6"),
]

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
        cmd = (["-layout"] if layout else []) + (["-l", str(last)] if last else [])
        _PDF[k] = PT.pdf_text(ROOT, PINS[key], cmd, PDFTEXT, "v2/docs/records/l9pwr")
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


def gen_lm5176_divider(key):
    """board A's LM5176 stages: tag -> the FB divider's top resistor (the call's sixth argument), and the helper's default
    bottom resistor (rfb_val)."""
    tree = ast.parse(text(key))
    bottom, top = None, {}
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name == "lm5176":
            names = [a.arg for a in n.args.args] + [a.arg for a in n.args.kwonlyargs]
            defs = list(n.args.defaults)
            d = dict(zip([a.arg for a in n.args.args][len(n.args.args) - len(defs):], defs))
            d.update({a.arg: v for a, v in zip(n.args.kwonlyargs, n.args.kw_defaults) if v is not None})
            if "rfb_val" in d:
                bottom = ast.literal_eval(d["rfb_val"])
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "lm5176" and len(n.args) > 5:
            top[ast.literal_eval(n.args[0])] = ast.literal_eval(n.args[5])
    if bottom is None or not top:
        die("gen_sch_a.py: the lm5176 helper's divider")
    return top, bottom


def module_literals(key, names):
    """module-level NAME = <literal> assignments of a file (a draft read as text, never run)."""
    out = {}
    for n in ast.parse(text(key)).body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id in names:
            try:
                out[n.targets[0].id] = ast.literal_eval(n.value)
            except ValueError:
                pass
    for k in names:
        if k not in out:
            die("%s carries no literal %s" % (PINS[key], k))
    return out


def stage_window(vref, ibias, rtop, rbot, tol, drop):
    """an LM5176 stage's output window on its FB divider (VREF and the resistors at their limits, IBIAS(FB) through the top
    resistor), and the least voltage at the loads with the rail's whole drop budget."""
    vmin = vref[0] * (1.0 + rtop * (1.0 - tol) / (rbot * (1.0 + tol))) - ibias * rtop
    vmax = vref[2] * (1.0 + rtop * (1.0 + tol) / (rbot * (1.0 - tol))) + ibias * rtop
    return vmin, vmax, vmin * (1.0 - drop)


def draft_rails(key):
    """the _intent.rail texts a draft would write into its generator (string literals inside the draft)."""
    t = text(key)
    out = {}
    for m in re.finditer(r'_intent\.rail\(\\?"([^"\\]+)\\?", ([\d.]+), ([\d.]+), ([\d.]+)', t.replace('\\"', '"')):
        out[m.group(1)] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))
    for m in re.finditer(r"_intent\.rail\((\w+), ([\d.]+), ([\d.]+), ([\d.]+), [^\n]*?efficiency=([\d.]+)", t):
        out["<%s>" % m.group(1)] = (float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)))
    return out


def draft_rail_call(key, name):
    """One _intent.rail(...) call a draft would write into its generator, PARSED and never matched by a line pattern (round 3:
    L4-E11's round 9 broke +12V_FAN's declaration over two source lines when it corrected L8P-F03, and a one-line pattern for
    its efficiency no longer matched). The draft is read as text and parsed with ast (a draft is never run); the call's text
    is found in the draft's string constants and parsed with ast again; the result is the call's positional and keyword
    literals. Every copy of the call in the draft must agree."""
    head = '_intent.rail("%s"' % name
    found = []
    for node in ast.walk(ast.parse(text(key))):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        s, at = node.value, 0
        while True:
            at = s.find(head, at)
            if at < 0:
                break
            call, end = None, at
            while call is None:
                end = s.find(")", end + 1)
                if end < 0:
                    break
                try:
                    call = ast.parse(s[at:end + 1], mode="eval").body
                except SyntaxError:
                    continue
            if not isinstance(call, ast.Call):
                die("%s: the %s rail's declaration does not parse" % (PINS[key], name))
            try:
                pos = [ast.literal_eval(a) for a in call.args]
                kw = {k.arg: ast.literal_eval(k.value) for k in call.keywords}
            except ValueError:
                die("%s: the %s rail's declaration is not all literals" % (PINS[key], name))
            found.append(dict(pos=pos, kw=kw))
            at = end
    if not found:
        die("%s writes no _intent.rail for %s" % (PINS[key], name))
    if any(x != found[0] for x in found[1:]):
        die("%s writes %s's declaration more than once, differently" % (PINS[key], name))
    return found[0]


BAT_NETS = ("CH_BATDRV", "CH_BATQ", "VBAT")     # nfet's gate, drain and source for a battery FET


def draft_battery_fets(key):
    """The charger's battery FETs as L4-E11's draft writes them, PARSED (round 3; the same reading as record l9stk's
    battery_fets): every nfet(ref, part, gate, drain, source, ...) inside the draft's string constants, read with ast, a `for`
    over a literal tuple unrolled with its names bound; the battery FETs are the calls on CH_BATDRV, CH_BATQ and VBAT.
    Returns the designators in the draft's order and the part's text."""
    found = []

    def walk(stmts, env):
        for st in stmts:
            if isinstance(st, ast.For):
                try:
                    vals = ast.literal_eval(st.iter)
                except (ValueError, SyntaxError):
                    continue
                for v in vals:
                    e2 = dict(env)
                    if isinstance(st.target, ast.Name):
                        e2[st.target.id] = v
                    elif isinstance(st.target, ast.Tuple) and isinstance(v, tuple) and len(v) == len(st.target.elts):
                        e2.update({e.id: x for e, x in zip(st.target.elts, v) if isinstance(e, ast.Name)})
                    walk(st.body, e2)
            elif isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) and isinstance(st.value.func, ast.Name) \
                    and st.value.func.id == "nfet" and len(st.value.args) >= 5:
                try:
                    args = tuple(eval(compile(ast.Expression(x), "<nfet>", "eval"), {"__builtins__": {}}, dict(env)) for x in st.value.args[:5])
                except Exception:
                    continue
                if all(isinstance(x, str) for x in args) and args[2:5] == BAT_NETS:
                    found.append((args[0], args[1]))
    for node in ast.walk(ast.parse(text(key))):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str) and "nfet(" in node.value):
            continue
        try:
            body = ast.parse(node.value).body
        except SyntaxError:
            body = []
            for line in node.value.splitlines():
                try:
                    body += ast.parse(line.strip()).body
                except SyntaxError:
                    continue
        walk(body, {})
    refs, parts = tuple(r for r, _p in found), sorted({p for _r, p in found})
    if len(refs) < 2 or len(set(refs)) != len(refs) or len(parts) != 1 or "BUK6Y10-30P" not in parts[0] or refs[:2] != ("Q39", "Q40"):
        die("the charger draft no longer carries the BUK6Y10-30P battery FETs Q39, Q40 on CH_BATDRV, CH_BATQ and VBAT (read: %s)" % (", ".join(refs) or "none"))
    return refs, parts[0]


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
    F["ap2112_a"] = grab(pdf("ap2112", last=1), r"delivers a \w+ (\d+)mA \(min\.\)", "AP2112's rating") / 1000.0
    F["tlv755_a"] = grab(pdf("tlv755", last=1), r"TLV755P (\d+)mA", "TLV755P's rating") / 1000.0
    F["vsns"] = tuple(v / 1000.0 for v in grab(pdf("lm5176", layout=True), r"VSNS\s+Average current loop regulation target\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM5176 VSNS", 3))
    # ---- the pack contract
    pk = text("pack")
    F["i_cont"] = grab(pk, r"declared_continuous_a: ([\d.]+)", "the pack's continuous current")
    F["i_peak"] = grab(pk, r"declared_peak_a: ([\d.]+)", "the pack's peak current")
    F["i_ocd"] = grab(pk, r"PACK_OVER_CURRENT_DISCHARGE\n[^\n]*\n[^\n]*\n\s+threshold: \{value: ([\d.]+), unit: A", "OCD's threshold")
    F["cuv"] = grab(pk, r"CELL_UNDER_VOLTAGE\n[^\n]*\n[^\n]*\n\s+threshold: \{value: ([\d.]+), unit: V", "CUV's threshold")
    F["series"] = grab(pk, r"\n  series: (\d+)", "the series count", conv=int)
    F["topology"] = grab(pk, r'\n  topology: "([^"]+)"', "the pack's topology", conv=str)
    F["parallel"] = grab(pk, r"\n  parallel_min: (\d+)", "the parallel count", conv=int)
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
    fan12 = draft_rail_call("l4e11_aux", "+12V_FAN")
    if not isinstance(fan12["kw"].get("efficiency"), float):
        die("the +12V_FAN efficiency in the draft")
    F["fan12_eff_draft"] = fan12["kw"]["efficiency"]
    F["fan12_decl"] = fan12
    F["bat_refs"], F["bat_part"] = draft_battery_fets("l4e11_chg")      # round 3: Q39, Q40 and, since L4-E11's round 9, Q42
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
    if re.search(r"\n   eta_slot\s", t8):
        die("record l8r2's figures table carries eta_slot again; this round set its parser line aside")
    F["su_efuse"] = grab(t8, r"eFuse ILM 1\.87 k: ([\d.]+) / ([\d.]+) / ([\d.]+) A", "the coolers' eFuse", 3)
    F["ron_lo"] = grab(t8, r"\n   ron_lo\s+([\d.]+)\s+MAKER", "the TPS2596 RON")
    F["pnl_efuse"] = grab(t8, r"with U901 \(ILM 604 Ohm\) ([\d.]+) / ([\d.]+) / ([\d.]+) A", "PANEL_5V's eFuse", 3)
    fr = draft_rails("l8r2_fans")
    if not any(k.startswith("<") and abs(v[0] - 12.0) < 1e-9 for k, v in fr.items()):
        die("the draft apply_gen_sch_b_fans12.py no longer writes the 12 V fan rail")
    F["fans12_rail"] = [v for k, v in sorted(fr.items()) if k.startswith("<") and len(v) == 4][0]
    if "U901" not in text("l8r2_pnl"):
        die("the draft apply_gen_sch_b_panel5v.py no longer carries U901")
    # ---- record l8r2 rounds 4 to 6 (fnd/l8r3 at 89924e40): the coolers' envelope, slots 1 and 3 on LM5176, RT 200 k, 0.1 %
    # the coolers' eFuse window unrounded, l8r2's own method: TPS2596 Equation 7 at its ILM, the wider neighbouring row's tolerance
    rilm = grab(t8, r"\n   rilm_fan\s+([\d.]+)\s+BOUND", "the coolers' ILM")
    rows_ = ast.literal_eval(grab(t8, r"\n   ilim_rows\s+(\(\(.*?\)\))\s+MAKER", "the TPS2596 ILIM rows", conv=str))
    k7 = grab(pdf("tps2596"), r"RILM :\s+(\d+)\s+ILIM A ([\d.]+)", "TPS2596 Equation 7", 2)
    rows_ = sorted(rows_)
    nb = [x for x in rows_ if x[0] < rilm][-1:] + [x for x in rows_ if x[0] > rilm][:1]
    n7 = k7[0] / rilm + k7[1]
    F["su_efuse_x"] = (n7 * (1 - max((x[2] - x[1]) / x[2] for x in nb)), n7, n7 * (1 + max((x[3] - x[2]) / x[2] for x in nb)))
    if any(abs(round(a, 3) - b) > 1e-9 for a, b in zip(F["su_efuse_x"], F["su_efuse"])):
        die("the coolers' eFuse window does not round to l8r2's printed figures")
    # the step-up's highest output unrounded, l8r2's own method (VREF's highest on the 1 % divider's highest ratio, FB leakage)
    vr = grab(t8, r"\n   vref\s+\(([\d.]+), ([\d.]+), ([\d.]+)\)\s+MAKER", "the TPS61089 VREF", 3)
    ifb = grab(t8, r"\n   ifb\s+([\d.e-]+)\s+MAKER", "the TPS61089 FB leakage")
    r1_, r2_, rt_ = (grab(t8, r"\n   %s\s+([\d.]+)\s+BOUND" % k, "the step-up's divider %s" % k) for k in ("r1", "r2", "rtol"))
    F["su_vtop_x"] = vr[2] * (1 + r1_ * (1 + rt_) / (r2_ * (1 - rt_))) + ifb * r1_
    if abs(round(F["su_vtop_x"], 3) - grab(t8, r"output [\d.]+ / [\d.]+ / ([\d.]+) V \(VREF and the 1 % divider", "the step-up's output")) > 1e-9:
        die("the step-up's highest output does not round to l8r2's printed figure")
    F["fan_env"] = grab(t8, r"\n   fan_env\s+([\d.]+)\s+BOUND", "the cooler's envelope bound")
    F["start_bound"] = grab(t8, r"\n   start_bound\s+([\d.]+)\s+BOUND", "the cooler branch's bounded start")
    F["ap_eq7"] = grab(t8, r"\n   ap_eq7\s+(\d+)\s+MAKER", "DS41979 Eq. 7")
    F["su_vout"] = grab(t8, r"output ([\d.]+) / ([\d.]+) / ([\d.]+) V \(VREF and the 1 % divider", "the step-up's output", 3)
    F["l8_window"] = grab(t8, r"with both resistors at 0\.1 % and IBIAS\(FB\) 25 nA through 53\.6 k \(1\.34 mV\) ([\d.]+) to ([\d.]+) V", "l8r2's 5.1 V window", 2)
    F["l8_vload"] = grab(t8, r"the least load voltage with the 2 % drop ([\d.]+) V", "l8r2's least load voltage")
    F["l8_loop"] = grab(t8, r"the loop's least: VSNS 43 mV over 6 mOhm at \+1 %: ([\d.]+) A", "l8r2's loop least")
    F["l8_other"] = grab(t8, r"the slot's other loads at HIGH \(PS-BUSY\): ([\d.]+) W", "l8r2's slot loads before the cooler")
    F["l8_slot2"] = grab(t8, r"slot 2 \(its own HIGH, the cooler's bounded start\): ([\d.]+) A", "l8r2's slot 2 start")
    F["l8_peak_margin"] = grab(t8, r"\+([\d.]+) A at the declared ([\d.]+) A", "l8r2's margin at the declared peak", 2)
    F["l8_rows"] = [(m.group(1), m.group(2), tuple(float(m.group(i)) for i in range(3, 10))) for m in re.finditer(
        r"\n      (PS-[A-Za-z0-9-]+)\s+slot (\d)\s+([\d.]+) / ([\d.]+) A  start ([\d.]+) A  degraded ([\d.]+) A  \+([\d.]+) / \+([\d.]+) / \+([\d.]+) A", t8)]
    if len(F["l8_rows"]) < 10:
        die("record l8r2's section 2c.5 rows")
    m = re.search(r"the energy at PLAN, VBAT side \(the stages' declared 0\.90 against the AP64500's curve point, slots 1 and 3\): ([^\n]+)", t8)
    if not m:
        die("record l8r2's energy line")
    F["l8_energy"] = [(a, float(b)) for a, b in re.findall(r"(PS-[A-Za-z0-9-]+) \+([\d.]+) W", m.group(1))]
    tf = text("l8r2_fans")
    lit = module_literals("l8r2_fans", ("_OLD_LOAD", "_NEW_LOAD", "_NEW_PEAK"))
    F["fan_row_old"] = grab(lit["_OLD_LOAD"], r'"J_FAN%d" % s: ([\d.]+),', "the drawn fan row")
    F["fan_row"] = grab(lit["_NEW_LOAD"], r'\(701 \+ 30 \* \(s - 1\)\): ([\d.]+),', "the drafted fan row")
    F["fan_row_basis"] = grab(lit["_NEW_LOAD"], r"([\d.]+) W of fan over ([\d.]+) \(ASSUMPTION\) at ([\d.]+) V", "the fan row's basis", 3)
    F["slot_peak_b"] = grab(lit["_NEW_PEAK"], r'else 2\.5, ([\d.]+), "J_5V_S', "board B's slot peak")
    sl = module_literals("l8r2_slotlm", ("BASE", "PEAK", "ENTRY", "_OLD_S1", "_OLD_S3"))
    F["slot_base"], F["slot_peak"], F["slot_entry"] = sl["BASE"], sl["PEAK"], sl["ENTRY"]
    ts = text("l8r2_slotlm")
    F["slot_isns"] = ohms(grab(ts, r'isns="(\d+m)", isns_lcsc', "the slot stages' ISNS shunt", conv=str))
    blk = ts[ts.index("_NEW_RAIL = ("):]
    blk = blk[:blk.index("\n_OLD_NOTE")]
    F["slot_eff"] = grab(blk, r"efficiency=([\d.]+)", "the drafted slot rails' efficiency")
    for k in ("_OLD_S1", "_OLD_S3"):
        if sl[k] not in text("gen_a"):
            die("gen_sch_a.py no longer carries the AP64500 slot stage the draft replaces (%s)" % k)
    rl = module_literals("l8r2_rt500", ("_OLD_RT", "_NEW_RT"))
    F["rt_old"] = grab(rl["_OLD_RT"], r'"(\d+)k \(RT', "the drawn RT")
    F["rt_new"] = grab(rl["_NEW_RT"], r'"(\d+)k 1% \(RT', "the drafted RT")
    if rl["_OLD_RT"] not in text("gen_b"):
        die("gen_sch_b.py no longer draws buck33's RT as the draft expects")
    kw = module_literals("l8r2_fb01", ("KW",))["KW"]
    F["fb_tol"] = grab(kw, r'rfb_tol="([\d.]+)%"', "the drafted divider tolerance") / 100.0
    F["fb_tol_drawn"] = grab(module_literals("l8r2_fb01", ("_NEW_DEF",))["_NEW_DEF"], r'rfb_tol="([\d.]+)%"', "the helper's default tolerance") / 100.0
    top, bot = gen_lm5176_divider("gen_a")
    F["rfb"] = (ohms(top["S2"]), ohms(bot.split()[0]))
    if ohms(top["SD"]) != F["rfb"][0]:
        die("gen_sch_a.py: the device rail's divider differs from slot 2's")
    lmp = pdf("lm5176", layout=True)
    F["vref"] = grab(lmp, r"VREF\s+Feedback reference voltage\s+FB = COMP\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "LM5176 VREF", 3)
    F["ibias"] = grab(lmp, r"IBIAS\(FB\)\s+Feedback pin input bias current\s+FB in regulation\s+(\d+)\s+nA", "LM5176 IBIAS(FB)") * 1e-9
    ga = text("gen_a")
    F["drop_s"] = grab(ga, r'_intent\.rail\("\+5V_S%s" % _n, [^\n]*?budget=([\d.]+)', "the slot rails' drop budget")
    F["drop_dev"] = grab(ga, r'_intent\.rail\("\+5V_DEV", [^\n]*?budget=([\d.]+)', "the device rail's drop budget")
    # ---- record l9stk section 15 (this tree's output since round 3): board P's breaker C-1 and the third battery FET
    tk = flat(text("l9stk_prot"))
    F["brk_variant"] = grab(tk, r"SELECTED: the (-\d) \(([a-z-]+)\)", "the breaker's selected variant", 2, conv=str)
    F["brk_rs_pair"] = tuple(x / 1000.0 for x in grab(tk, r"sense RS: ([\d.]+) and ([\d.]+) mOhm in parallel = [\d.]+ mOhm", "the breaker's two sense resistors", 2))
    F["brk_rs"] = grab(tk, r"sense RS: [\d.]+ and [\d.]+ mOhm in parallel = ([\d.]+) mOhm", "the breaker's sense") / 1000.0
    F["brk_rs_win"] = tuple(x / 1000.0 for x in grab(tk, r"its window: ([\d.]+) to ([\d.]+) mOhm", "the sense's window", 2))
    F["brk_fets"] = grab(tk, r"FETs: (\d) x CSD18510Q5B \(40 V, VGS \+-20 V, ([\d.]+) mOhm at 10 V", "the breaker's FETs", 2)
    F["brk_fet_hot"] = grab(tk, r"held at ([\d.]+) A: ([\d.]+) W each at ([\d.]+) mOhm \(Figure 8's x([\d.]+) at 150 C\)", "the breaker's FETs hot", 4)
    F["bat_fets"] = grab(tk, r"\((\d) x BUK6Y10-30P, ([\d.]+) mOhm each at 150 C\)", "the battery FETs", 2)
    F["bat_three_w"] = grab(tk, r"three \(Zself \+ 2 Zmut\) ([\d.]+) W each", "the three FETs' loss")
    F["brk_sense_w"] = grab(tk, r"the breaker's sense \([\d.]+ and [\d.]+ mOhm\) ([\d.]+) W in [\d.]+ mOhm; ([\d.]+) W in [\d.]+ mOhm", "the sense's loss", 2)
    if abs(F["bat_fets"][1] / 1000.0 - F["fet_bound"]) > 1e-12:
        die("l9stk's battery FET bound differs from L4-E11's")
    # ---- L4-E9 round 7 (fnd/l4e9r7 at 3737df82, out 30): decision D-11's all-transmit floor re-derived on round 1's drafts
    t9r = flat(text("l4e9r7"))
    F["r7_drawn"] = grab(t9r, r"DRAWN \(the generators in set 28's tree\): ([\d.]+) W, path ([\d.]+) Ohm: stack ([\d.]+) V, needs ([\d.]+) V", "L4-E9 r7's drawn need", 4)
    F["r7_need"] = grab(t9r, r"DRAFTED \(DRAWN plus the release-guarded drafts that move a power figure\): ([\d.]+) W, path ([\d.]+) Ohm: stack ([\d.]+) V, needs ([\d.]+) V", "L4-E9 r7's drafted need", 4)
    F["r7_parts"] = grab(t9r, r"the pair 18 A x ([\d.]+) mOhm = ([\d.]+) V, and the other drafts at HIGH .*? ([\d.]+) W at VBAT = ([\d.]+) V", "L4-E9 r7's parts", 4)
    F["r7_floor"] = grab(t9r, r"RE-DERIVED on the drafted design: ([\d.]+) V rest \(([\d.]+) V a cell", "L4-E9 r7's floor", 2)
    F["r7_rule"] = grab(t9r, r"the least floor on the floor's own ([\d.]+) V step that leaves at least ([\d.]+) V over the need", "L4-E9 r7's rule", 2)
    F["r7_margin"] = grab(t9r, r"margin \+([\d.]+) V at R_cell 0\.06 Ohm, covering R_cell up to ([\d.]+) Ohm", "L4-E9 r7's margin", 2)
    F["r7_heater"] = grab(t9r, r"with the heater on the drafts need ([\d.]+) V", "L4-E9 r7's heater row")
    F["r7_pa"] = grab(t9r, r"the PA-alone floor 12\.4 V holds on the drafts \(([\d.]+) V needed", "L4-E9 r7's PA row")
    F["r7_window"] = grab(t9r, r"from the floor up to ChargeVoltage's ([\d.]+) V maximum", "ChargeVoltage's maximum")
    F["r7_modes"] = grab(t9r, r"DRAFTED: ([\d.]+) / ([\d.]+) / ([\d.]+) / ([\d.]+) W", "L4-E9 r7's restated modes", 4)
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
        self.lm51 = []                     # the LM5176 5.1 V stages (rv-pwr's tree has none)
        self.shunts = {"S1": 0.005, "S2": 0.006, "S3": 0.005, "DEV": 0.006, "PA": 0.006, "HF": 0.010}   # the rails' INA226 shunts
        self.window = None                 # the LM5176 5.1 V stages' output window: (least, highest, least at the loads)
        self.cooler = None
        self.state_fix = {}                # state -> overrides that correct the state's definition (C1)

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
        elif kind == "fixedsc":
            eta = param[1] if scen == "hi" else param[0]
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


def build(pb, F, hc, upto, cooler="env"):
    """the tree after applying the steps of section 1 up to and including `upto` (0: rv-pwr as committed). cooler="maker"
    rebuilds round 1's D4 (the cooler at its maker's 2.0 W at 12 V over the step-up's 0.85 at HIGH, l8r2's round 2 row), for the
    round 1 tree; "env" is round 6's (the envelope at HIGH over the step-up's low efficiency, the row 0.69 A)."""
    cfg = Config("step %d" % upto, pb)
    cfg.pb = pb
    cfg.cooler = cooler
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
            cfg.lm51.append(n)
        cfg.window = stage_window(F["vref"], F["ibias"], F["rfb"][0], F["rfb"][1], F["fb_tol_drawn"], F["drop_s"])
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
    if upto >= 9:   # D4: the coolers, Layer 7's pick on a per-slot TPS61089 step-up (l8r2 item 1 to round 6, DRAFTED)
        for s in (1, 2, 3):
            n = "S%dF" % s
            L = cfg.load("cooler fan slot %d" % s)
            lo, pl = rv_fan[L["name"]][0], rv_fan[L["name"]][1]
            if cooler == "maker":
                cfg.nodes[n] = ["fixed", "S%d" % s, F["fans12_rail"][0], F["su_eta"], "slot %d's cooler fan 12 V, a TPS61089 step-up from +5V_S%d (l8r2 item 1 at round 2, DRAFTED): %.2f (an ASSUMPTION of l8r2)" % (s, s, F["su_eta"]), "DRAFTED"]
                new = pb.up(lo, pl, float(F["cooler"][5]), "R")
                L["src"] = "Layer 7's pick, Sanyo Denki %s, %s V, %s A, %s W at full speed (l7pwr, D-18 SESSION); LOW and PLAN keep rv-pwr's duty figures (the module's Fan_PWM sets the duty)" % (F["cooler"][0], F["cooler"][1], F["cooler"][4], F["cooler"][5])
            else:
                cfg.nodes[n] = ["fixedsc", "S%d" % s, F["fans12_rail"][0], (F["su_eta"], F["su_eta_lo"]), "slot %d's cooler fan 12 V, a TPS61089 step-up from +5V_S%d (l8r2 round 6, DRAFTED): %.2f at LOW and PLAN (the draft's declared figure), %.2f at HIGH (the envelope's, the slot row %.2f A), both ASSUMPTIONS of l8r2" % (s, s, F["su_eta"], F["su_eta_lo"], F["fan_row"]), "DRAFTED"]
                new = pb.up(lo, pl, F["fan_env"], "R")
                L["src"] = ("Layer 7's pick, Sanyo Denki %s, %s V, %s A, %s W at full speed at 12 V (l7pwr, D-18 SESSION); HIGH is l8r2's envelope, %.2f W at the step-up's %.2f V top, any duty (BOUND, l8r2 round 5; C4-3 holds the chain to it), no Fan_PWM maximum; LOW and PLAN keep rv-pwr's duty figures (the module's Fan_PWM sets the duty, R-150 unset)"
                            % (F["cooler"][0], F["cooler"][1], F["cooler"][4], F["cooler"][5], F["fan_env"], F["su_vout"][2]))
            L["node"], L["status"] = n, "DRAFTED"
            L["d"] = {st: (pb.OFF if is_off(t) else new) for st, t in L["d"].items()}
            cfg.fan_on[L["name"]] = new
            cfg.limits[n] = ("TPS61089 and its eFuse (drafted)", F["su_efuse"][0], "out", "l8r2 item 1: the fan eFuse's least limit at 12 V (ILM 1.87 k) (DRAFTED)", 1)
    if upto >= 10:  # D5: PANEL_5V behind the eFuse U901 (l8r2 item 3, DRAFTED)
        cfg.nodes["PNL"] = ["series", "DEV", cfg.nodes["DEV"][2], F["ron_lo"], "PANEL_5V behind U901, a TPS259631 (l8r2 item 3, DRAFTED): RON at most %.4f Ohm (SLVSET8A, the row l8r2 prints)" % F["ron_lo"], "DRAFTED"]
        L = cfg.load("panel board C")
        L["node"], L["status"] = "PNL", "DRAFTED"
        cfg.limits["PNL"] = ("TPS259631 U901 (drafted)", F["pnl_efuse"][0], "out", "l8r2 item 3: U901's least limit, ILM 604 Ohm (DRAFTED)", 1)
    if upto >= 11:  # D6: slots 1 and 3 on board A's LM5176 stage (l8r2 rounds 4 to 6, DRAFTED)
        for s in ("1", "3"):
            n, u = "S" + s, "U%d" % (F["slot_base"][s] + 1)
            cfg.nodes[n] = ["fixed", "VBAT", cfg.nodes[n][2], F["slot_eff"],
                            "slot %s rail, LM5176 stage %s (apply_gen_sch_a_slotlm.py, DRAFTED; the AP64500 %s retired): 5.1 V NOT PLOTTED, the draft's declared %.2f" % (s, u, {"1": "U4", "3": "U6"}[s], F["slot_eff"]), "DRAFTED"]
            cfg.limits[n] = lm_limit(u, F["slot_isns"], F)
            cfg.shunts[n] = F["slot_isns"]
            cfg.lm51.append(n)
    if upto >= 12:  # D7: board B's six slot bucks at RT 200 k (l8r2 round 5, DRAFTED): the curves' own frequency; no figure moves
        for s in (1, 2, 3):
            for x in ("A", "B"):
                n = "S%d%s" % (s, x)
                cfg.nodes[n][4] += "; RT %.0f k drafted (apply_gen_sch_b_rt500.py): %.0f kHz, the curve's frequency" % (F["rt_new"], F["ap_eq7"] / F["rt_new"])
                cfg.nodes[n][5] = "DRAFTED"
    if upto >= 13:  # D8: the LM5176 5.1 V stages' dividers at 0.1 % (l8r2 round 6, DRAFTED): the window; no figure at 5.1 V moves
        cfg.window = stage_window(F["vref"], F["ibias"], F["rfb"][0], F["rfb"][1], F["fb_tol"], F["drop_s"])
        for n in cfg.lm51:
            cfg.nodes[n][4] += "; divider at %.1f %% (apply_gen_sch_a_fb01.py, DRAFTED)" % (F["fb_tol"] * 100)
            cfg.nodes[n][5] = "DRAFTED"
    if upto >= 14:  # D9: board P's breaker C-1, its sense and two FETs in the pack path (l9stk 15.4, DRAFTED)
        nf = int(F["brk_fets"][0])
        r_brk = F["brk_rs_win"][1] + F["brk_fet_hot"][2] / 1000.0 / nf
        cfg.r_parts.append(("board P's breaker C-1: the sense at its window's highest %.4f mOhm and %d x CSD18510Q5B at %.3f mOhm each (150 C) in parallel (l9stk 15.4, DRAFTED)"
                            % (F["brk_rs_win"][1] * 1000, nf, F["brk_fet_hot"][2]), r_brk, "DRAFTED"))
    if upto >= 15:  # D10: the third battery FET beside Q39 and Q40 (l9stk 15.5, DRAFTED)
        nb = int(F["bat_fets"][0])
        cfg.r_parts = [p for p in cfg.r_parts if not p[0].startswith("Q39 and Q40")]
        cfg.r_parts.append(("Q39, Q40 and a third BUK6Y10-30P in parallel at L4-E11's 150 C bound %.3f mOhm each (l9stk 15.5; L4-E11's round 9 drafts it as %s; DRAFTED)" % (F["bat_fets"][1], ", ".join(F["bat_refs"][2:]) or "none"),
                            F["bat_fets"][1] / 1000.0 / nb, "DRAFTED"))
    if upto >= 16:  # C1: PS-ALLTX's standby WiFi card off in every scenario (REQ-018, CONOPS 4a): the state's definition, CORRECTED
        cfg.state_fix["ALLTX"] = {STANDBY: pb.OFF}
    cfg.r_path = math.fsum(p[1] for p in cfg.r_parts)
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
    return key, dict(cfg.state_fix.get(key, {}))


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
    ("D1", "DRAFTED", "L4-E11 15c: the BQ25730's battery FET pair Q39, Q40 (BUK6Y10-30P in parallel) in the pack path, at L4-E11's 150 C RDS(on) bound (apply_gen_sch_a_charger.py, not applied; since L4-E11's round 9 the draft writes three, the third is step D10)"),
    ("D2", "DRAFTED", "L4-E11 15a: board E's auxiliary domain (U12, the controller, the mixers) on VSYS_E over the dock's pin 1 behind the eFuse U42 (apply_gen_sch_e_aux.py, not applied)"),
    ("D3", "DRAFTED", "L4-E11 18a with Layer 7's D-18: the two mixers are Sanyo Denki 9WL0612P4H001 on U22's 12.0 V rail (LTC3115-1, 0.85 assumed, 16 mA quiescent) (apply_gen_sch_e_aux.py, not applied)"),
    ("D4", "DRAFTED", "l8r2 item 1 to round 6 with Layer 7's D-18: the three coolers are Sanyo Denki 9WPA0412P6G001 on a per-slot TPS61089 step-up from +5V_Sn, at full speed with no Fan_PWM maximum; HIGH the envelope (2.75 W at 12.43 V over the step-up's 0.80, the slot row 0.69 A), PLAN at 0.85 (apply_gen_sch_b_fans12.py at 89924e40, not applied)"),
    ("D5", "DRAFTED", "l8r2 item 3: PANEL_5V behind the eFuse U901 (TPS259631), its RON in series with the panel (apply_gen_sch_b_panel5v.py, not applied)"),
    ("D6", "DRAFTED", "l8r2 rounds 4 to 6: slots 1 and 3 on board A's LM5176 stage (U501, U531 on 6 mOhm ISNS shunts, the AP64500s U4 and U6 retired), 5.1 V NOT PLOTTED, the draft's declared 0.90; the three slot leads at 6.6 A (apply_gen_sch_a_slotlm.py at 89924e40, not applied)"),
    ("D7", "DRAFTED", "l8r2 round 5: board B's six slot bucks at RT 200 k, 500 kHz, the frequency of the maker's curves rv-pwr uses (DRAWN's 68 k sets 1.47 MHz, where no curve is printed); no figure moves (apply_gen_sch_b_rt500.py at 89924e40, not applied)"),
    ("D8", "DRAFTED", "l8r2 round 6: the LM5176 5.1 V stages' dividers at 0.1 %, the window 5.0019 to 5.1744 V; no figure at the model's 5.1 V moves, the least load voltage sets the stages' margins (apply_gen_sch_a_fb01.py at 89924e40, not applied)"),
    ("D9", "DRAFTED", "l9stk 15.4: board P's breaker C-1 (an LM5069 in the variant l9stk 15.4b selects, printed below; its 2.6087 mOhm sense and two CSD18510Q5B) in the pack path from Q2's source to PACK_P (record l9stk in this tree, a desk design, not applied)"),
    ("D10", "DRAFTED", "l9stk 15.5 and L4-E11 round 9: a third BUK6Y10-30P in parallel with the battery FET pair Q39, Q40, written by L4-E11's charger draft under the designator printed below (apply_gen_sch_a_charger.py, not applied)"),
    ("C1", "CORRECTED", "PS-ALLTX carries the standby WiFi card OFF in every scenario, as REQ-018's acceptance and CONOPS 4a's PS-ALLTX row define the state (rv-pwr's state powered it at its placeholder, 1.0 W PLAN and 9.1 W HIGH; the challenge cx40's Q1): a correction of the state's definition, no drawing and no draft, applied last so every earlier step reads as before; DRAWN and round 1's tree keep rv-pwr's state"),
]

STANDBY = "WiFi link card 2 (standby)"

# C-ALLTX rev 3 (rev 2's definition, the coordinator's case row of 4 October 2026, 14:50 CEST, kept by rev 3 at 15:45; plan section 4a): the state REQ-018's acceptance, CONOPS 4a's
# PS-ALLTX row and D-11's basis define. Each load's figure is chosen by the row's text, never by its effect:
CASE_TX = (   # "every transmitter keyed at its HIGH figure": the loads whose PS-ALLTX figure in rv-pwr is a transmit figure
    "WiFi link card 1 (live)", "5G RM520N-GL", "LimeSDR Mini 2.4", "RockBLOCK 9704", "LoRa E22-900M30S",
    "board D (SA868 and logic)", "E72 x2 (Zigbee, Thread)", "VHF PA 30 W", "QMX HF")
CASE_FULL = ("Xenarc 709GNK",)                                              # "monitor full": its HIGH
CASE_FANS = ("cooler fan slot 1", "cooler fan slot 2", "cooler fan slot 3", "two mixer fans")   # "fans running": full speed
CASE_OFF = (STANDBY, "pack heater mat (cold overlay)", "PoE outlet (delivered outside)", "USB-C outlet (delivered outside)")
CASE_CM5 = 4.5            # W, "the compute modules at their typical 4.5 W" (the row's text; the CM5's 0.9 A typical at 5 V)
CASE_V_REST, CASE_I = 15.5, 18.0                                             # REQ-018's rest voltage; the service limit, indicated

NOT_MODELLED = [
    ("l8gnd (GND-002 and the HOT-R1 SLOT_EN hold)", "ground bonding and a logic hold: no load and no converter; nothing for the budget"),
    ("l8r2 item 2 (the VBUS20 over-voltage cut-off) and item 4 (J_QMX and J_CAM on the JST PH land)", "the charge path's protection and a connector land: no battery-side load"),
    ("l8r2's board D 3.3 V eFuse (apply_gen_sch_a_d8v3.py)", "a TPS259631 in series with board D's 0.06 A logic: under a milliwatt"),
    ("l8r2 rounds 3 to 6's pack return (apply_gen_sch_a_packrtn.py, apply_gen_sch_e_packrtn.py) and the energy chain's board E texts (apply_energy_chain_e1oz.py)", "the return path declared as a rail and copper texts: no load and no converter"),
    ("the slot leads' declared 6.6 A and VBAT's entries at 2.60 A (l8r2 round 6)", "declarations that the conductor checks read, not loads; printed beside the slot stages' currents in section 5b"),
    ("the slot stages' CS shunts (5 mOhm in each LM5176 stage's input) and the breaker's enable loop, its RC hold and PTC guard (l9stk C-1b)", "inside the stages' declared efficiency as for slot 2 and the device rail since M1; the enable loop's divider and inverters carry no figure read here, milliwatts against the states' tens of watts"),
    ("l9stk's copper decision (section 14) and its other protection items (the clamps, the retry, DD-4, DD-5)", "the pack path's band and its faults: no load in any state; the breaker's retry is a fault state"),
    ("L4-E4, L4-E5, L4-E6, L4-E7, L4-E8, L4-E13 (the front end's limits, the source control, the fault handling, the solar stage, the VBUS20 bank, the panel)", "the source and charge path, not the battery-side loads; L4-E8's ballasts enter the charging balance (section 8, B4) as L4-E12 counts them"),
    ("L4-E9's U17 on R227 (the PoE stage's sense)", "5 mOhm in the PoE stage's input, which is off in every state; 1.8 mW at the outlet's 0.6 A, under the model's rounding"),
    ("L4-E10 (the cell and its thermal design) and L4-E12 (the electronics' thermal)", "the pack model and the heat: this record's pack-side watts are their input, not the other way round"),
    ("the rails' INA226 shunts (5 and 6 mOhm on the slot, device, PA and HF rails; 6 mOhm on slots 1 and 3 with D6)", "not in rv-pwr's tree; their I2R is bounded in section 5 per state from the rails' own currents"),
    ("the BQ25730's own quiescent draw on battery", "no figure read in this record; a charger's battery-only quiescent is milliwatts against the states' tens of watts"),
    ("board E's CELL_F loads as drawn (U12 and the mixers, declared 1.0 A, before R17)", "the DRAWN tree passes them through R17 with the rest; at their PLAN current, about 0.2 A, that is under a milliwatt; DRAFTED moves them to VSYS_E (D2)"),
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
    R = {"pins": [(k, PINS[k], sha16(k)) for k in PINS] + [("pdftext", t, (h or "ABSENT")[:16]) for t, h, _held in PT.inputs(ROOT, PDFTEXT)], "F": F, "pred": {}, "hc": hc}
    cfgs = [build(pb, F, hc, i) for i in range(len(STEP_TEXT))]
    RV, DRAWN, DRAFTED = cfgs[0], cfgs[5], cfgs[-1]
    R1T = build(pb, F, hc, 10, cooler="maker")   # round 1's DRAFTED tree (38ef774c): D1 to D5 with l8r2's round 2 cooler
    R["cfgs"] = {"RV": RV, "DRAWN": DRAWN, "DRAFTED": DRAFTED, "DRAFTED-R1": R1T}
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
            for n, rs in sorted(cfg.shunts.items()):
                if n in evs["hi"][1]["nodes"]:
                    i = evs["hi"][1]["nodes"][n][2]
                    shunt += i * i * rs
            per[(cname, st)] = {"loads": loads, "rails": rails, "shunt_hi": shunt}
    R["per"] = per
    R["margins"] = margins

    # ---- 5b. the LM5176 5.1 V stages side by side (slots 1 to 3 and the device rail): the loop's least, the current at the model's
    # 5.1 V and at the least load voltage the window gives, and for the slots the cooler branch's bounded start and a degraded
    # cooler (record l8r2's bounds) on the slot's other loads at HIGH
    stg = {}
    for cname in ("DRAWN", "DRAFTED", "DRAFTED-R1"):
        cfg = R["cfgs"][cname]
        for st in STATES:
            ev_pl = run_state(cfg, hc, st, "plan")[1]["nodes"]
            ev_hi = run_state(cfg, hc, st, "hi")[1]["nodes"]
            for n in ("S1", "S2", "S3", "DEV"):
                if n not in ev_hi or ev_hi[n][1] <= 0:
                    continue
                lim = cfg.limits[n]
                row = {"lim": lim, "lm": n in cfg.lm51, "status": cfg.nodes[n][5],
                       "i_plan": ev_pl[n][2], "i_hi": ev_hi[n][2], "p_hi": ev_hi[n][1]}
                if n in cfg.lm51 and cfg.window:
                    row["v_least"] = cfg.window[0] * (1.0 - (F["drop_dev"] if n == "DEV" else F["drop_s"]))
                    row["i_least"] = ev_hi[n][1] / row["v_least"]
                fan = "S%sF" % n[1:] if n != "DEV" else None
                if fan and fan in ev_hi and cfg.cooler == "env" and cname != "DRAWN":
                    other = ev_hi[n][1] - ev_hi[fan][0]
                    row["other"] = other
                    if cfg.window and n in cfg.lm51:
                        vl = cfg.window[2]
                        row["start"] = other / vl + F["start_bound"]
                        row["degraded"] = other / vl + F["su_efuse_x"][0] * F["su_vtop_x"] / F["su_eta_lo"] / vl
                stg[(cname, st, n)] = row
    R["stages"] = stg

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
        for cname in ("RV", "DRAWN", "DRAFTED", "DRAFTED-R1"):
            cfg = R["cfgs"][cname]
            ovx = {"pack heater mat (cold overlay)": cfg.heat_on} if ov == "HEAT" else ov
            for sc in ("plan", "hi"):
                ev = run_state(cfg, hc, st, sc, extra=ovx)[1]
                r[(cname, sc)] = {"pb": ev["pb"], "I": tuple(pb.pack_current(ev["p_vbat"], v, cfg.r_path) for v in R["v_stack"]),
                                  "V_cont": ev["p_vbat"] / F["i_cont"] + F["i_cont"] * cfg.r_path,
                                  "V_peak": ev["p_vbat"] / F["i_peak"] + F["i_peak"] * cfg.r_path}
        pc.append(r)
    R["pc"] = pc

    # ---- 6b. the pack path's elements per state (DRAFTED): each element's I2R at the state's pack current at 14.4 V
    el = {}
    for st in STATES:
        for sc in ("plan", "hi"):
            i = tot[("DRAFTED", st)][sc]["i14"]
            i1 = tot[("DRAFTED-R1", st)][sc]["i14"]
            el[(st, sc)] = {"I": i, "I_r1": i1, "parts": [(a, b, s, i * i * b) for a, b, s in DRAFTED.r_parts],
                            "pair_r1": i1 * i1 * F["fet_bound"] / 2.0}
    R["elems"] = el

    # ---- 7. D-11's floors on rv-pwr's method
    d11 = {}
    for cname in ("RV", "DRAWN", "DRAFTED", "DRAFTED-R1"):
        d11[cname] = d11_rows(pb, F, hc, R["cfgs"][cname], cname)
    R["d11"] = d11
    # the same DRAFTED tree with the coolers at round 1's HIGH (the maker's 2.0 W at 12 V over 0.85): the floor's other end, should
    # l8r2's C4-3 read the coolers' steady input at the maker's figure
    R["d11_mk"] = d11_rows(pb, F, hc, build(pb, F, hc, len(STEP_TEXT) - 1, cooler="maker"), "DRAFTED-MK")
    BASIS = "all-transmit basis: non-transmit typical, standby card off, high"
    R["d11_steps"] = [(STEP_TEXT[i][0], d11_rows(pb, F, hc, c, "step")["rows"][BASIS]) for i, c in enumerate(cfgs) if i >= 5]
    step, over = F["r7_rule"]
    need = d11["DRAFTED"]["rows"][BASIS]["V_rest"]["hi"]
    need_mk = R["d11_mk"]["rows"][BASIS]["V_rest"]["hi"]
    R["floor_rule"] = {"need": need, "floor_r7": F["r7_floor"][0], "margin": F["r7_floor"][0] - need,
                       "need_mk": need_mk, "floor_req_mk": floor_by_rule(need_mk, step, over),
                       "floor_req": floor_by_rule(need, step, over), "step": step, "over": over,
                       "heater": d11["DRAFTED"]["rows"]["the same with the heater on"]["V_rest"]["hi"],
                       "pa": d11["DRAFTED"]["rows"]["PA alone over PS-TYP, PA at 113 W, the rest at plan"]["V_rest"]["hi"]}
    R["d11_rv_record"] = pb  # for the record's own figures below
    # ---- 7b. C-ALLTX rev 3 (rev 2's definition), the case row, from its text (round 4; relabelled in round 6)
    cv, crule = case_vals(DRAFTED)
    ca = {"rule": crule, "vals": cv}
    ca["new"] = case_row(pb, F, DRAFTED, cv)
    ca["new_rv"] = case_row(pb, F, DRAFTED, cv, at="rv")
    ca["drawn"] = case_row(pb, F, DRAWN, case_vals(DRAWN)[0])
    raw_vals, raw_ev = run_state(cfgs[-2], hc, "ALLTX", "hi")       # the raw PS-ALLTX HIGH row before C1 (DRAFTED to D10)
    ca["old_raw"] = {"p": raw_ev["p_vbat"], "standby": raw_vals[STANDBY], "need": raw_ev["p_vbat"] / CASE_I + CASE_I * (cfgs[-2].r_path + F["series"] * pb.R_CELL["hi"] / 3.0)}
    fix_vals, fix_ev = run_state(DRAFTED, hc, "ALLTX", "hi")
    ca["raw_fixed"] = {"p": fix_ev["p_vbat"], "standby": fix_vals[STANDBY], "need": fix_ev["p_vbat"] / CASE_I + CASE_I * (DRAFTED.r_path + F["series"] * pb.R_CELL["hi"] / 3.0)}
    ca["old_basis"] = d11["DRAFTED"]["rows"][BASIS]
    ca["basis_vals"] = run_state(DRAFTED, hc, "ALLTX", "hi", extra=d11_typ(DRAFTED, pb))[0]
    ca["basis_case"] = case_row(pb, F, DRAFTED, ca["basis_vals"])
    ca["cm5_8"] = case_row(pb, F, DRAFTED, case_vals(DRAFTED, cm5=8.0)[0])
    ca["fans_plan"] = case_row(pb, F, DRAFTED, case_vals(DRAFTED, fans_idx=1)[0])
    R["calltx"] = ca
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


def case_vals(cfg, cm5=None, fans_idx=2):
    """C-ALLTX rev 3's load figures (rev 2's definition), by the row's text: transmitters at HIGH, the monitor full, the fans running at full speed
    (HIGH; fans_idx=1 is the PLAN duty, a separately labelled sensitivity), the outlets, the heater and the standby card off, the
    compute modules at CASE_CM5 (cm5 replaces it in a sensitivity), every other load at its PS-ALLTX PLAN figure. Returns
    (values, rule per load)."""
    vals, rule = {}, {}
    for L in cfg.loads:
        n, t = L["name"], L["d"]["ALLTX"]
        if n in CASE_OFF:
            vals[n], rule[n] = 0.0, "off"
        elif n in CASE_TX:
            vals[n], rule[n] = t[2], "transmitter, HIGH"
        elif n in CASE_FULL:
            vals[n], rule[n] = t[2], "monitor full, HIGH"
        elif n in CASE_FANS:
            vals[n], rule[n] = t[fans_idx], "fans running, %s" % ("HIGH (full speed)" if fans_idx == 2 else "PLAN (duty)")
        elif n.startswith("CM5 slot"):
            vals[n], rule[n] = (CASE_CM5 if cm5 is None else cm5), "compute module, %s W" % ("typical %g" % CASE_CM5 if cm5 is None else "%g" % cm5)
        else:
            vals[n], rule[n] = t[1], "typical (PS-ALLTX PLAN)"
    return vals, rule


def case_row(pb, F, cfg, vals, i=CASE_I, v_rest=CASE_V_REST, at="case", r_cell=None, eff_over=None, r_extra=0.0):
    """the case's power at VBAT with each pack-fed converter at the VBAT the case sets (VBAT = P / I at the pack current i,
    solved by fixed point) or, at="rv", at rv-pwr's HIGH scenario voltage 16.8 V; the rest voltage needed at i; the allowance at
    v_rest and i; the deficit and its parts (load pins, conversion, path, cells). eff_over replaces converters' efficiencies and
    r_extra adds path resistance, for the sensitivities of record l9t5."""
    rc = pb.R_CELL["hi"] if r_cell is None else r_cell
    r_path = cfg.r_path + r_extra
    r_cells = F["series"] * rc / 3.0
    if at == "rv":
        ev, v = evaluate(cfg, vals, "hi", eff_over=eff_over), pb.VIN_OF["hi"]
    else:
        v = 14.4
        for _ in range(200):
            ev = evaluate(cfg, vals, "hi", vpack=v, eff_over=eff_over)
            v2 = ev["p_vbat"] / i
            if abs(v2 - v) < 1e-12:
                break
            v = v2
        else:
            die("the case row's VBAT did not settle")
    p = ev["p_vbat"]
    allow = i * (v_rest - i * (r_path + r_cells))
    conv = {n: x[0] - x[1] for n, x in ev["nodes"].items() if n != "VBAT" and x[0] > 0}
    return {"p": p, "load": ev["p_load"], "conv": p - ev["p_load"], "vbat": v, "i": i, "r_path": r_path, "r_cells": r_cells,
            "need": p / i + i * (r_path + r_cells), "allow": allow, "deficit": p - allow, "path_w": i * i * r_path,
            "cell_w": i * i * r_cells, "emf_w": i * v_rest, "nodes": ev["nodes"], "conv_by": conv, "r_cell": rc}


def floor_by_rule(need, step, over):
    """L4-E9 round 7's rule: the least floor on its own step that leaves at least `over` above the need."""
    return round(math.ceil(round((need + over) / step, 6)) * step, 6)


def d11_typ(cfg, pb):
    """rv-pwr's typ_nontx (its section 7.2): the compute modules and the NVMe at their PS-TYP figures, the standby card off; every
    other load stays at the scenario's figure (so at HIGH in D-11's basis)."""
    typ = {}
    for s in (1, 2, 3):
        typ["CM5 slot %d" % s] = cfg.load("CM5 slot %d" % s)["d"]["TYP"]
        typ["NVMe slot %d" % s] = cfg.load("NVMe slot %d" % s)["d"]["TYP"]
    typ[STANDBY] = pb.OFF
    return typ


def d11_rows(pb, F, hc, cfg, cname):
    """D-11's three rows on rv-pwr's method (section 7.2 there) for one tree."""
    r_rv = pb.R_DIST + (pb.R_R17 if cname == "RV" else 0.0)    # RV: rv-pwr's main_pack_path_R17 record
    r = cfg.r_path if cname != "RV" else r_rv
    typ = d11_typ(cfg, pb)
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
                      "r_cell_max": (fl - v_stack) * 3.0 / (F["series"] * F["i_peak"]), "r": r}
    return {"r": r, "rows": rows_}


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
    r3 = F["bat_fets"][1] / 1000.0 / F["bat_fets"][0]
    curp = {}
    for st in ("IDLESPEC", "TYP"):
        i_r1, i_d = tot[("DRAFTED-R1", st)]["plan"]["i14"], tot[("DRAFTED", st)]["plan"]["i14"]
        curp["%s, round 1 (the pair)" % st] = (round(i_r1, 4), round(i_r1 ** 2 * rp, 4))
        curp["%s, DRAFTED now (three FETs, D10)" % st] = (round(i_d, 4), round(i_d ** 2 * r3, 4))
    rec.append({"id": "R5", "what": "L4-E11 15c: the pair's loss on battery at PS-IDLE-SPEC and PS-TYP (A, W)",
                "theirs": (F["fet_idle"][0], F["fet_idle"][1], F["fet_typ"][0], F["fet_typ"][1]),
                "repro": (round(i1, 3), round(i1 * i1 * rp, 4), round(i2, 3), round(i2 * i2 * rp, 4)),
                "equal": abs(round(i1, 3) - F["fet_idle"][0]) < 1e-9 and abs(round(i1 * i1 * rp, 4) - F["fet_idle"][1]) < 1e-9 and abs(round(i2, 3) - F["fet_typ"][0]) < 1e-9 and abs(round(i2 * i2 * rp, 4) - F["fet_typ"][1]) < 1e-9,
                "cur": curp,
                "why": "L4-E11 divides the profile's rounded %.1f W and %.1f W by 14.4 V; this record solves the pack current at 14.4 V with the whole pack path (R_DIST, R17, the battery FETs, on DRAFTED board P's breaker) and the current design's profile; with l9stk's third FET (D10) the FETs' share of the current falls to a third each and their loss with it" % (m[0], R["committed"]["PS-TYP"][2])})

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
    env = 3 * F["fan_env"] / F["su_eta_lo"] + 2 * mx / F["fan12_eff_draft"]
    rec.append({"id": "R8", "what": "Layer 7 section 3: the five fans and their converters at full speed against the plan's fan figures (W)",
                "theirs": F["l7_heat"], "repro": (round(l7, 2), round(rv_plan_fans, 3)), "equal": abs(round(l7, 2) - F["l7_heat"][0]) < 1e-9 and abs(round(rv_plan_fans, 3) - F["l7_heat"][1]) < 1e-9,
                "cur": {"this record, the converters' losses unrounded, the coolers at the maker's 2.0 W (round 1's HIGH)": (round(mine, 4),),
                        "DRAFTED's HIGH now: the coolers at l8r2's envelope, %.2f W over %.2f each, the mixers as before" % (F["fan_env"], F["su_eta_lo"]): (round(env, 4),),
                        "U22's quiescent at 14.4 V, in neither figure": (round(F["vsyse_decl"][4] / 1000.0 * 14.4, 4),)},
                "why": "Layer 7 rounds each step-up's loss to %.2f W (%.4f W at %.2f), %.4f W in all; U22's 16 mA quiescent is in L4-E11's input current and in this record's VSYS_E, not in either heat figure" % (F["l7_stepup_loss"], cf / F["su_eta"] - cf, F["su_eta"], mine - l7)})

    # R9 record l8r2 round 6 (2c.5): slots 1 and 3 on the LM5176 stage, the steady envelope, the bounded start, a degraded cooler,
    # the 0.1 % window and the loop's least (round 1's R9, l8r2's choice (a) on a flat eta_slot, is set aside: section 1). l8r2
    # parsed this record's round 1 rails as printed (section 5: out W and eta at 3 places); its inputs are rebuilt here from
    # DRAFTED-R1 at that precision and its arithmetic re-run on them
    SN = {v.split(" (")[0]: k for k, v in STATE_NAME.items()}
    stg = R["stages"]
    r1t = R["cfgs"]["DRAFTED-R1"]
    loop = F["vsns"][0] / (F["slot_isns"] * (1 + F["shunt_tol"]))
    win = stage_window(F["vref"], F["ibias"], F["rfb"][0], F["rfb"][1], F["fb_tol"], F["drop_s"])
    vl = win[2]
    env_b = F["fan_env"] / F["su_eta_lo"]
    degr_b = F["su_efuse_x"][0] * F["su_vtop_x"] / F["su_eta_lo"]
    _pr = {}

    def printed(k):
        if k not in _pr:
            ev = {sc: run_state(r1t, hc, k, sc)[1]["nodes"] for sc in SCEN}
            _pr[k] = {n: {"out": tuple(round(ev[sc][n][1], 3) for sc in SCEN), "eta": round(ev["plan"][n][3], 3), "kind": r1t.nodes[n][0]}
                      for n in ev["hi"] if n in ev["plan"] and n in ev["lo"]}
        return _pr[k]

    def base_w(k, s):
        p = printed(k)
        return (p["S" + s]["out"][2] / 5.1) * 5.1 - p["S%sF" % s]["out"][2] / p["S%sF" % s]["eta"]
    rows_ok, worst_dev = True, 0.0
    for name, slot, th in F["l8_rows"]:
        b = base_w(SN[name], slot)
        mine9 = ((b + env_b) / 5.1, (b + env_b) / vl, b / vl + F["start_bound"], (b + degr_b) / vl)
        mine9 = tuple(round(x, 4) for x in mine9) + tuple(round(loop - x, 4) for x in mine9[1:])
        rows_ok = rows_ok and all(abs(a - c) < 1e-9 for a, c in zip(mine9, th))
        x = stg[("DRAFTED", SN[name], "S" + slot)]
        worst_dev = max(worst_dev, abs(x["i_least"] - th[1]), abs(x["start"] - th[2]), abs(x["degraded"] - th[3]))
    en_ok, en_mine, en_now = True, [], []
    for name, v in F["l8_energy"]:
        k = SN[name]
        p = printed(k)
        dw = math.fsum(p[n]["out"][1] * (1 / F["slot_eff"] - 1 / p[n]["eta"]) for n in ("S1", "S3") if p[n]["kind"] == "curve" and p[n]["out"][1] > 0)
        en_mine.append((name, round(dw, 3)))
        en_ok = en_ok and abs(round(dw, 3) - v) < 1e-9
        en_now.append((name, run_state(cfgs[11], hc, k, "plan")[1]["p_vbat"] - run_state(cfgs[10], hc, k, "plan")[1]["p_vbat"]))
    pb_ = printed("BUSY")
    other_r1 = base_w("BUSY", "1")
    s2_r1 = (pb_["S2"]["out"][2] - pb_["S2F"]["out"][2] / pb_["S2F"]["eta"]) / vl + F["start_bound"]
    repro9 = (round(other_r1, 3), round(win[0], 4), round(win[1], 4), round(vl, 4), round(loop, 6), round(s2_r1, 4), round(loop - F["slot_peak"], 4))
    theirs9 = (F["l8_other"], F["l8_window"][0], F["l8_window"][1], F["l8_vload"], F["l8_loop"], F["l8_slot2"], F["l8_peak_margin"][0])
    least = {}
    for col, key in (("steady at 5.1 V", None), ("steady at the least load voltage", "i_least"), ("bounded start", "start"), ("degraded cooler", "degraded")):
        least[col] = slot_least(R, key)
    busy = stg[("DRAFTED", "BUSY", "S1")]
    s2_now = max(stg[("DRAFTED", st, "S2")]["start"] for st in STATES if ("DRAFTED", st, "S2") in stg and "start" in stg[("DRAFTED", st, "S2")])
    rec.append({"id": "R9", "what": "l8r2 round 6 (2c.5): the slot's other loads at HIGH (PS-BUSY, W); the 0.1 %% window and its least load voltage (V); the loop's least (A); slot 2's bounded start (A); the margin at the declared %.1f A; every row of its per state table (A at 5.1 V, at the least voltage, start, degraded, the three margins) and its energy line" % F["slot_peak"],
                "theirs": theirs9, "repro": repro9,
                "equal": all(abs(a - b) < 1e-9 for a, b in zip(repro9, theirs9)) and rows_ok and en_ok,
                "cur": {"its %d per state rows, re-run on round 1's printed rails" % len(F["l8_rows"]): ("EQUAL" if rows_ok else "NOT EQUAL",),
                        "its energy line (D6's cost at VBAT at PLAN, W), re-run": tuple("%s %+.3f" % e for e in en_mine) + (("EQUAL",) if en_ok else ("NOT EQUAL",)),
                        "round 2's DRAFTED unrounded: the slot's other loads (PS-BUSY, W), slot 2's start (A), the largest difference from l8r2's rows (A)": (round(busy["other"], 4), round(s2_now, 4), round(worst_dev, 4)),
                        "round 2's DRAFTED unrounded: D6's cost at VBAT at PLAN (W)": tuple("%s %+.4f" % e for e in en_now),
                        "round 2's DRAFTED: the least margin over every state, slots 1 and 3 (A, state, rail)": tuple("%s %+.4f (%s, %s)" % (c, v[0], STATE_NAME[v[1]], v[2]) for c, v in least.items()),
                        "VBAT's entries at the declared peak (%.1f A x 5.1 V over %.2f x 14.4 V; declared %.2f A)" % (F["slot_peak"], F["slot_eff"], F["slot_entry"]): (round(F["slot_peak"] * 5.1 / (F["slot_eff"] * 14.4), 4),)},
                "why": "l8r2 took this record's round 1 rails as printed (3 places), so its rows carry that rounding; re-run on the same printed rails they are equal, and round 2's DRAFTED, which carries l8r2's own round 6 drafts (the cooler at its %.2f W envelope over %.2f, slots 1 and 3 on the LM5176 at %.2f), gives them unrounded within the difference printed; the window from the LM5176 sheet's VREF and IBIAS(FB), the divider %.1f k over %.0f k (gen_sch_a.py) at fb01's %.1f %% and the rails' %.0f %% drop" % (F["fan_env"], F["su_eta_lo"], F["slot_eff"], F["rfb"][0] / 1000, F["rfb"][1] / 1000, F["fb_tol"] * 100, F["drop_s"] * 100)})

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
    # R1c L4-E9 round 7's restated modes and R11 its D-17 floor, both on this record's round 1 tree (38ef774c)
    r1 = R["cfgs"]["DRAFTED-R1"]
    r1m = (pbp("DRAFTED-R1", "IDLESPEC"), pbp("DRAFTED-R1", "ALLTX"), pbp("DRAFTED-R1", "ALLTX", "hi"),
           run_state(r1, hc, "IDLESPEC", "plan", extra=pb.PA_113)[1]["pb"])
    rec.append({"id": "R1c", "what": "L4-E9 round 7 (out 30): the modes restated DRAFTED, PS-IDLE-SPEC, PS-ALLTX plan and high, the PA keyed alone at 113 W (W at the pack)",
                "theirs": F["r7_modes"], "repro": tuple(round(x, 3) for x in r1m),
                "equal": all(abs(round(a, 3) - b) < 1e-9 for a, b in zip(r1m, F["r7_modes"])),
                "cur": {"DRAFTED now": tuple(round(x, 3) for x in cur["DRAFTED"])},
                "why": "L4-E9 quotes this record's round 1 DRAFTED (rebuilt here as DRAFTED-R1: D1 to D5 with l8r2's round 2 cooler); round 2 moves them by D4's envelope at HIGH and D6 to D10"})
    B = "all-transmit basis: non-transmit typical, standby card off, high"
    dw, dr1 = R["d11"]["DRAWN"]["rows"], R["d11"]["DRAFTED-R1"]["rows"]

    def need_at_printed(row, r):
        """L4-E9's method: this record's printed VBAT watts (0.01 W) over 18 A, the path, the cells at R_cell high."""
        vs = round(row["vbat_W"], 2) / F["i_peak"] + F["i_peak"] * r
        return vs, vs + F["i_peak"] * F["series"] * pb.R_CELL["hi"] / 3.0
    s_dw, n_dw = need_at_printed(dw[B], R["d11"]["DRAWN"]["r"])
    s_r1, n_r1 = need_at_printed(dr1[B], R["d11"]["DRAFTED-R1"]["r"])
    n_ht = need_at_printed(dr1["the same with the heater on"], R["d11"]["DRAFTED-R1"]["r"])[1]
    n_pa = need_at_printed(dr1["PA alone over PS-TYP, PA at 113 W, the rest at plan"], R["d11"]["DRAFTED-R1"]["r"])[1]
    fl = floor_by_rule(n_r1, F["r7_rule"][0], F["r7_rule"][1])
    repro11 = (round(dw[B]["vbat_W"], 2), round(s_dw, 3), round(n_dw, 3), round(dr1[B]["vbat_W"], 2), round(R["d11"]["DRAFTED-R1"]["r"], 6), round(s_r1, 3), round(n_r1, 3),
               round(F["i_peak"] * F["fet_bound"] / 2, 4), round(round(dr1[B]["vbat_W"], 2) - round(dw[B]["vbat_W"], 2), 2),
               round((round(dr1[B]["vbat_W"], 2) - round(dw[B]["vbat_W"], 2)) / F["i_peak"], 4), round(n_ht, 3), round(n_pa, 3), fl, round(fl - n_r1, 3),
               round((fl - s_r1) * 3.0 / (F["series"] * F["i_peak"]), 4))
    theirs11 = (F["r7_drawn"][0], F["r7_drawn"][2], F["r7_drawn"][3], F["r7_need"][0], F["r7_need"][1], F["r7_need"][2], F["r7_need"][3],
                F["r7_parts"][1], F["r7_parts"][2], F["r7_parts"][3], F["r7_heater"], F["r7_pa"], F["r7_floor"][0], F["r7_margin"][0], F["r7_margin"][1])
    fr = R["floor_rule"]
    rec.append({"id": "R11", "what": "L4-E9 round 7's D-17 (out 30): DRAWN W at VBAT, stack, need; DRAFTED W, path, stack, need; the pair's V at 18 A, the other drafts' W and V; the heater row's and the PA row's need; the floor by its rule, its margin, the R_cell it covers",
                "theirs": theirs11, "repro": repro11,
                "equal": all(abs(a - b) < 1e-9 for a, b in zip(repro11, theirs11)),
                "cur": {"DRAFTED now, the all-transmit basis: VBAT W, path Ohm, stack V, the rest voltage needed at R_cell high": (round(R["d11"]["DRAFTED"]["rows"][B]["vbat_W"], 2), round(R["d11"]["DRAFTED"]["r"], 6), round(R["d11"]["DRAFTED"]["rows"][B]["V_stack"], 3), round(fr["need"], 3)),
                        "against round 7's %.1f V floor: the margin (V), and the floor its own rule gives now" % fr["floor_r7"]: (round(fr["margin"], 3), fr["floor_req"]),
                        "the heater row and the PA-alone row now (V)": (round(fr["heater"], 3), round(fr["pa"], 3))},
                "why": "L4-E9 took this record's round 1 watts as printed (0.01 W) and its own pack path; reproduced here on DRAFTED-R1 the same way. Round 2's need moves by the steps of section 7's ladder; the rule is L4-E9's (%s V step, at least %s V over the need)" % (F["r7_rule"][0], F["r7_rule"][1])})

    # R12 record l9stk section 15: the elements this budget adds to the pack path
    nf, rhot = F["brk_fets"][0], F["brk_fet_hot"][2]
    i_cl = F["brk_fet_hot"][0]
    ra, rb_ = F["brk_rs_pair"]
    rpar = ra * rb_ / (ra + rb_)
    repro12 = (round(rpar * 1000, 4), round(F["brk_fets"][1] * F["brk_fet_hot"][3], 3), round((i_cl / nf) ** 2 * rhot / 1000.0, 3),
               round((i_cl / F["bat_fets"][0]) ** 2 * F["bat_fets"][1] / 1000.0, 3),
               round(i_cl ** 2 * rpar * (rpar / ra), 2), round(i_cl ** 2 * rpar * (rpar / rb_), 2))
    theirs12 = (F["brk_rs"] * 1000, rhot, F["brk_fet_hot"][1], F["bat_three_w"], F["brk_sense_w"][0], F["brk_sense_w"][1])
    rd = R["cfgs"]["DRAFTED"]
    brk = [p for p in rd.r_parts if p[0].startswith("board P's breaker")][0][1]
    three = [p for p in rd.r_parts if p[0].startswith("Q39, Q40 and a third")][0][1]
    rec.append({"id": "R12", "what": "l9stk 15.4 and 15.5 at the breaker's largest limit %.2f A: the sense (mOhm), a breaker FET at 150 C (mOhm) and its loss (W), a battery FET's loss with three (W), the sense's loss in its 4 and 7.5 mOhm (W)" % i_cl,
                "theirs": theirs12, "repro": repro12, "equal": all(abs(a - b) < 1e-9 for a, b in zip(repro12, theirs12)),
                "cur": {"the pack path's change (mOhm): the breaker added (D9), the battery FETs from two to three (D10), the net": (round(brk * 1000, 4), round((three - F["fet_bound"] / 2) * 1000, 4), round((brk + three - F["fet_bound"] / 2) * 1000, 4)),
                        "the pack path, round 1 and now (Ohm)": (round(R["cfgs"]["DRAFTED-R1"].r_path, 6), round(rd.r_path, 6))},
                "why": "the breaker's sense at its window's highest and its FETs at the sheet's x1.8 at 150 C (l9stk's own bound), the battery FETs at L4-E11's 150 C bound: the conservative side for every limit this budget judges. The third FET is in parallel, so it lowers the path; with the breaker the net is within 0.01 mOhm of round 1's"})

    order = ["R1", "R1b", "R1c", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11", "R12"]
    return sorted(rec, key=lambda r: order.index(r["id"]))


def sensitivities(pb, F, hc, R):
    cfg = R["cfgs"]["DRAFTED"]
    f2 = grab(text("rvpwr"), r"fuse DCR ([\d.]+) to ([\d.]+) mOhm", "F2's DCR range", 2)
    nb, nf = F["bat_fets"][0], F["brk_fets"][0]
    r_lo = pb.R_W2 + f2[0] / 1000.0 + pb.R_R17 + F["fet_25c"] * F["fet_gate"] / nb + F["brk_rs_win"][0] + F["brk_fets"][1] / 1000.0 / nf
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
        prox = {n: ap64500_proxy(cfg, ev0, n) for n in cfg.lm51}
        wp = evaluate(cfg, vals, "plan", eff_over=prox)["pb"]
        rows.append(("assumption", "the LM5176 5.1 V stages' efficiency (%s)" % ", ".join(cfg.lm51), wp, h0, "the AP64500 curve at their point (%s; rv-pwr's model) to the declared %.2f (NOT PLOTTED)" % (", ".join("%s %.3f" % (n, prox[n]) for n in cfg.lm51), F["s2_eff"])))
        if any(vals["cooler fan slot %d" % s] > 0 for s in (1, 2, 3)):
            w80 = evaluate(cfg, vals, "plan", eff_over={"S%dF" % s: F["su_eta_lo"] for s in (1, 2, 3)})["pb"]
            rows.append(("assumption", "the cooler step-ups' efficiency (l8r2)", h0, w80, "%.2f to %.2f (TI's low figure for the inductor's worst case, l8r2)" % (F["su_eta"], F["su_eta_lo"])))
        w93 = evaluate(cfg, vals, "plan", eff_over={"FAN12": F["u22_eff_ta04"][1] / 100.0})["pb"]
        rows.append(("assumption", "U22's efficiency (L4-E11)", w93, h0, "%.2f (TA04b, typical, read at %.2f A) to %.2f (L4-E11's assumption)" % (F["u22_eff_ta04"][1] / 100.0, F["u22_eff_ta04"][0], F["fan12_eff_draft"])))
        wr = pb.battery_side(ev0["p_vbat"], 14.4, r_lo)
        rows.append(("assumption", "the pack path's resistance", wr, h0, "%.2f to %.2f mOhm: F2 at %.1f to %.1f mOhm, the %d battery FETs at 25 C (%.3f mOhm each at 8.5 V drive) to their 150 C bound, the breaker's sense over its window and its FETs at 25 C (%.2f mOhm) to 150 C" % (r_lo * 1000, cfg.r_path * 1000, f2[0], f2[1], nb, F["fet_25c"] * F["fet_gate"] * 1000, F["brk_fets"][1])))
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
            elif nv[0] in ("fixed", "fixedq", "fixedsc"):
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
                raw["pack"].append((cname, r["label"], r["kind"], lim, pl, hi, r[("RV", "plan")]["I"][-1], r[("RV", "hi")]["I"][-1],
                                    r[("DRAFTED-R1", "plan")]["I"][-1], r[("DRAFTED-R1", "hi")]["I"][-1]))
    for cname in ("RV", "DRAWN", "DRAFTED", "DRAFTED-R1"):
        for lab, row in R["d11"][cname]["rows"].items():
            raw["d11"].append((cname, lab, row["floor"], row["V_rest"]["hi"], row["margin_hi"], row["r_cell_max"]))
    return raw


BASIS = "all-transmit basis: non-transmit typical, standby card off, high"


def slot_least(R, key, cname="DRAFTED", rails=("S1", "S3")):
    """the least margin to the LM5176 loop over every state for the slot stages: (margin, state, rail)."""
    out = []
    for k, x in R["stages"].items():
        if k[0] != cname or k[2] not in rails or not x["lm"]:
            continue
        i = x["p_hi"] / 5.1 if key is None else x.get(key)
        if i is not None:
            out.append((x["lim"][1] - i, k[1], k[2]))
    return min(out)


def predicates(pb, F, R):
    P = R["pred"]
    tot = R["tot"]
    P["this evaluator reproduces rv-pwr on its own tree within 1e-9 W"] = R["check_worst"] < 1e-9
    cm = R["committed"]
    P["rv-pwr's committed headline table equals this evaluator at 0.1 W"] = all(
        abs(round(tot[("RV", st)][sc]["pb"], 1) - cm[pb.STATE_NAME[st]][1 + i]) < 1e-9 for st in pb.STATES for i, sc in enumerate(SCEN))
    for r in R["rec"]:
        P["reconciliation %s: the other record's figure reproduced from its own inputs" % r["id"]] = bool(r["equal"])
    P["DRAFTED's PLAN is above DRAWN's in every state"] = all(tot[("DRAFTED", st)]["plan"]["pb"] > tot[("DRAWN", st)]["plan"]["pb"] for st in STATES)
    P["DRAFTED's PLAN is above round 1's DRAFTED in every state but PS-SURV, where slots 1 and 3 are off, and PS-ALLTX, where C1 removes the standby card's 1.0 W"] = all(
        (tot[("DRAFTED", st)]["plan"]["pb"] > tot[("DRAFTED-R1", st)]["plan"]["pb"]) == (st not in ("SURV", "ALLTX")) for st in STATES)
    P["DRAWN's PLAN is above RV's in every state but PS-EMCON, where the link cards are unpowered"] = all(
        (tot[("DRAWN", st)]["plan"]["pb"] > tot[("RV", st)]["plan"]["pb"]) == (st != "EMCON") for st in STATES)
    P["the waterfall's last step is DRAFTED and its first RV, on every state"] = all(
        abs(R["wf"][-1][st] - tot[("DRAFTED", st)]["plan"]["pb"]) < 1e-9 and abs(R["wf"][0][st] - tot[("RV", st)]["plan"]["pb"]) < 1e-9 for st in STATES)
    d = {c: R["d11"][c]["rows"][BASIS]["margin_hi"] for c in ("RV", "DRAWN", "DRAFTED", "DRAFTED-R1")}
    P["D-11's all-transmit floor holds on RV and DRAWN and fails on DRAFTED"] = d["RV"] > 0 and d["DRAWN"] > 0 and d["DRAFTED"] < 0
    fl = F["r7_floor"][0]
    need = {c: R["d11"][c]["rows"][BASIS]["V_rest"]["hi"] for c in ("DRAFTED", "DRAFTED-R1")}
    P["L4-E9 round 7's all-transmit floor covers round 1's drafted basis and not this round's"] = need["DRAFTED-R1"] <= fl < need["DRAFTED"]
    P["D-11's PA-alone floor holds on every tree"] = all(R["d11"][c]["rows"]["PA alone over PS-TYP, PA at 113 W, the rest at plan"]["margin_hi"] > 0 for c in ("RV", "DRAWN", "DRAFTED", "DRAFTED-R1"))
    over_plan = [m for m in R["margins"] if m[4] > m[3][1]]
    P["no converter is over its limit at PLAN in any state, DRAWN or DRAFTED"] = not over_plan
    P["slots 1 and 3 are within their LM5176 loop on DRAFTED in every state: at HIGH at 5.1 V and at the least load voltage, in the bounded start and with a degraded cooler"] = all(
        slot_least(R, k)[0] > 0 for k in (None, "i_least", "start", "degraded"))
    dev = [m for m in R["margins"] if m[2] == "DEV" and m[1] == "ALLTX"]
    P["the device rail's LM5176 is over its loop at HIGH in PS-ALLTX on DRAWN and DRAFTED (L9P-F03)"] = sorted(m[0] for m in dev if m[5] > m[3][1]) == ["DRAFTED", "DRAWN"]
    P["the drafted fan row equals the envelope over the step-up's low efficiency at 5.0 V, to 0.01 A"] = abs(round(F["fan_row_basis"][0] / F["fan_row_basis"][1] / F["fan_row_basis"][2], 2) - F["fan_row"]) < 1e-9 and abs(F["fan_row_basis"][0] - F["fan_env"]) < 1e-9 and abs(F["fan_row_basis"][1] - F["su_eta_lo"]) < 1e-9
    ca = R["calltx"]
    P["C1: PS-ALLTX on DRAFTED carries the standby card at 0 W in every scenario, and DRAWN keeps rv-pwr's state"] = (
        all(run_state(R["cfgs"]["DRAFTED"], R["hc"], "ALLTX", sc)[0][STANDBY] == 0.0 for sc in SCEN)
        and run_state(R["cfgs"]["DRAWN"], R["hc"], "ALLTX", "hi")[0][STANDBY] > 0.0)
    P["C-ALLTX rev 3's row: every transmitter at its HIGH, the outlets, the heater and the standby card at 0 W, the compute modules at 4.5 W"] = (
        all(ca["vals"][n] == R["cfgs"]["DRAFTED"].load(n)["d"]["ALLTX"][2] for n in CASE_TX) and all(ca["vals"][n] == 0.0 for n in CASE_OFF)
        and all(ca["vals"]["CM5 slot %d" % k] == CASE_CM5 for k in (1, 2, 3)))
    P["C-ALLTX rev 3's row closes on itself: load pins, conversion, path and cells sum to the cell EMF at 18 A plus the deficit"] = abs(
        ca["new"]["load"] + ca["new"]["conv"] + ca["new"]["path_w"] + ca["new"]["cell_w"] - ca["new"]["emf_w"] - ca["new"]["deficit"]) < 1e-9
    P["L4-E11's charger draft writes the battery FETs record l9stk selected, the third beside Q39 and Q40 (D10)"] = (
        len(F["bat_refs"]) == int(F["bat_fets"][0]) and len(F["bat_refs"]) == 3)
    src = text("sources")
    P["every copy in inputs/ is pinned and named with its sha256 in SOURCES.txt"] = all(
        PINS[k].startswith("v2/docs/records/l9pwr/inputs/") and ("%s sha256 %s" % (os.path.basename(PINS[k]), hashlib.sha256(open(path(k), "rb").read()).hexdigest())) in src for k in ORIGIN)
    dn = R["cfgs"]["DRAFTED"]
    P["every drafted node and row is labelled DRAFTED"] = all(v[5] == "DRAFTED" for n, v in dn.nodes.items() if n in ("VSYSE", "FAN12", "S1F", "S2F", "S3F", "PNL", "S1", "S3")) and all(
        L["status"] == "DRAFTED" for L in dn.loads if L["name"] in ("two mixer fans", "cooler fan slot 1", "cooler fan slot 2", "cooler fan slot 3", "panel board C")) and all(
        s == "DRAFTED" for a, b, s in dn.r_parts if "breaker" in a or "BUK6Y10" in a)
    ids = [x["id"] for x in R.get("classified", [])]
    P["every margin finding has a class among the instruction's three and an owner"] = all(
        x["class"] in ("DEMONSTRATED ANALYSIS DEFECT", "ASSUMPTION TO BOUND", "PHYSICAL QUESTION") and x["owner"] for x in R.get("classified", []))
    P["the findings are L9P-F01 to L9P-F06"] = ids == ["L9P-F01", "L9P-F02", "L9P-F03", "L9P-F04", "L9P-F05", "L9P-F06"]


def classify(pb, F, R):
    """the margin findings with their class under the owner's instruction of 2 October 2026, their status in round 2 and their
    owner. Each is built from the computed figures; the class, the status and the owner are this record's reading (SESSION)."""
    out = []
    raw = R["findings"]
    d = {c: R["d11"][c]["rows"][BASIS] for c in ("RV", "DRAWN", "DRAFTED", "DRAFTED-R1")}
    fr = R["floor_rule"]
    ladder = dict(R["d11_steps"])
    nv = {k: v["V_rest"]["hi"] for k, v in ladder.items()}
    d_env = nv["D5"] - d["DRAFTED-R1"]["V_rest"]["hi"]
    parts = [("the coolers at l8r2's envelope at HIGH (D4: %.2f W at %.2f V over %.2f, against round 1's %.1f W over %.2f)" % (F["fan_env"], F["su_vout"][2], F["su_eta_lo"], float(F["cooler"][5]), F["su_eta"]), d_env),
             ("slots 1 and 3 on the LM5176 at the declared %.2f (D6)" % F["slot_eff"], nv["D6"] - nv["D5"]),
             ("board P's breaker (D9)", nv["D9"] - nv["D8"]), ("the third battery FET (D10)", nv["D10"] - nv["D9"])]
    rest = (fr["need"] - d["DRAFTED-R1"]["V_rest"]["hi"]) - math.fsum(p[1] for p in parts)
    # ROUND 5 (task T5 round 2, record l9t5, 4 October 2026): L9P-F01 is restated on the case row C-ALLTX rev 3 (REQ-018's acceptance
    # with CONOPS 4a's row, computed from its own text in out 7b). Its round 2 figure, 16.214 V, is decision D-11's basis as rv-pwr models
    # it and is kept below as a LABELLED SCENARIO; round 7's 16.1 V floor and the 16.4 V its rule gives are WITHDRAWN (the owner's
    # positions of 4 October 2026), so the finding is judged against REQ-018's 15.5 V only.
    nw = R["calltx"]["new"]
    case_holds = nw["need"] <= CASE_V_REST
    out.append({
        "id": "L9P-F01", "class": "DEMONSTRATED ANALYSIS DEFECT", "new": "carried (round 1), restated in round 5 on C-ALLTX rev 3",
        "status": ("OPEN on the case: C-ALLTX rev 3 needs %.4f V rest at %.0f A against REQ-018's %.1f V (record l9t5 bounds the printed uncertainties)"
                   % (nw["need"], CASE_I, CASE_V_REST)) if not case_holds else "CLOSED on the case: C-ALLTX rev 3 needs %.4f V" % nw["need"],
        "subject": "REQ-018's all-transmit case on the drafted design (D-17, the case row C-ALLTX rev 3); D-11's basis is a labelled scenario",
        "figure": ("THE CASE (C-ALLTX rev 3: REQ-018's acceptance with CONOPS 4a's row; every transmitter keyed at HIGH, the fans running, the outlets, the heater and the standby card off, every other load at typical; out 7b, each pack-fed converter at the case's VBAT %.3f V): "
                   "%.3f W at VBAT, a pack rest voltage of %.4f V needed at %.0f A and R_cell %.2f Ohm (an ASSUMPTION), %+.4f V against REQ-018's %.1f V. "
                   "LABELLED SCENARIO, NOT THE CASE: decision D-11's basis as rv-pwr models it (all transmitters keyed, the compute modules and the NVMe typical, the standby card off, every other load at HIGH, every converter at 16.8 V) needs %.3f V at the worst cell resistance on this round's drafts "
                   "(round 1's drafts %.3f V; DRAWN %.3f V); from round 1: %s; the rest %+.4f V; the coolers' envelope alone takes round 1's basis to %.3f V; with the coolers at the maker's %.1f W over %.2f, %.3f V. "
                   "WITHDRAWN (the owner's positions of 4 October 2026): L4-E9 round 7's %.1f V floor, the %.1f V its rule gives on these drafts, FAN_OK (rejected)"
                   % (nw["vbat"], nw["p"], nw["need"], CASE_I, nw["r_cell"], nw["need"] - CASE_V_REST, CASE_V_REST,
                      fr["need"], d["DRAFTED-R1"]["V_rest"]["hi"], d["DRAWN"]["V_rest"]["hi"], "; ".join("%s %+.4f V" % p for p in parts), rest, nv["D5"],
                      float(F["cooler"][5]), F["su_eta"], fr["need_mk"], fr["floor_r7"], fr["floor_req"])),
        "rule": "REQ-018's acceptance: PS-ALLTX supplied with every rail in regulation through a 60 s key-down begun at a pack rest voltage of 15.5 V or more, every cell at most +55 C (pcb_requirements.yaml); the case row C-ALLTX rev 3; D-11's service limit, 18 A indicated",
        "why": "the case computed from its own text needs more than REQ-018's rest voltage on this round's drafts; l8r2 round 6 declared the coolers' envelope (the slot row %.2f A) and moved slots 1 and 3 to the LM5176, and l9stk added board P's breaker and the third battery FET (together %+.4f V on the basis); a desk result on the drafts' own figures, not an assumption a measurement would settle" % (F["fan_row"], nv["D10"] - nv["D8"]),
        "action": ("close the deficit on the case, never on a scenario: record l9t5's A1 (the VHF PA held to its 30 W service by a closed VGG loop on board D), the selected direction, drafted and judged in record l9t5; "
                   "the coolers' share stays l8r2's envelope bound (C4-3: %.4f V per watt at VBAT); a Fan_PWM cap during a key-down is not available "
                   "(l8r2 round 4: the fan runs full whenever its PWM lead is not driven); the heater stays off while keyed (%.3f V needed with it on the basis)"
                   % (1.0 / F["i_peak"], fr["heater"])),
        "owner": "record l9t5 (A1, Layer 9's power author) with L4-E9 (D-17, R-28 and LH-12: FW-A05's all-transmit rule on the case), l8r2 (C4-3, the coolers' envelope) and Layer 5 (FW-A05's text)"})
    st13 = {k: slot_least(R, k) for k in (None, "i_least", "start", "degraded")}
    r1s = [m for m in R["stages"].items() if m[0][0] == "DRAFTED-R1" and m[0][2] in ("S1", "S3")]
    r1_worst = max(x["i_hi"] for k, x in r1s)
    r1_lim = r1s[0][1]["lim"][1]
    r1_over = sorted(set(k[1] for k, x in r1s if x["i_hi"] > x["lim"][1]), key=STATES.index)
    out.append({
        "id": "L9P-F02", "class": "ASSUMPTION TO BOUND", "new": "carried (round 1)",
        "status": "RESOLVED IN THE DRAFTS (l8r2 rounds 4 to 6), CONDITIONAL on l8r2's C4-1 to C4-6" if st13["start"][0] > 0 else "OPEN",
        "subject": "slots 1 and 3's converter at HIGH with the drafted coolers",
        "figure": ("round 1: the AP64500 at %.3f A against its %.0f A at HIGH (%s). Round 2: slots 1 and 3 on the LM5176 stage, the loop's least %.4f A (VSNS %.0f mV over %.0f mOhm at +%.0f %%); the least margins over every state: %s"
                   % (r1_worst, r1_lim, " and ".join(STATE_NAME[s] for s in r1_over), R["stages"][("DRAFTED", "BUSY", "S1")]["lim"][1],
                      F["vsns"][0] * 1000, F["slot_isns"] * 1000, F["shunt_tol"] * 100,
                      "; ".join("%s %+.4f A (%s, %s)" % (lab, v[0], STATE_NAME[v[1]], v[2]) for lab, v in (("steady at 5.1 V", st13[None]), ("steady at the least load voltage %.4f V" % R["cfgs"]["DRAFTED"].window[2], st13["i_least"]),
                                                                                          ("bounded start", st13["start"]), ("degraded cooler", st13["degraded"]))))),
        "rule": "CMP-001: the applied stress against the datasheet maximum for every part in a current path above 1 A",
        "why": "the LM5176's average loop limits rather than a rating being exceeded; the start and the degraded cooler are l8r2's bounds (the branch at 1.80 A as a 100 us average; the cooler's eFuse at its least 0.448 A at 12.43 V over 0.80), each CONDITIONAL on its bench row",
        "action": "none at the desk; l8r2's C4-1 (the stage over the envelopes, the 0.1 % window), C4-3 (the cooler chain in a loaded slot) and C4-6 (fit and copper) decide; the declared 6.6 A leads and VBAT's 2.60 A entries are the drafts' declarations",
        "owner": "l8r2 (C4-1 to C4-6) with board A's generator owner (slotlm, fb01) and board B's (fans12, rt500)"})
    conv = raw["conv"]
    stg = R["stages"]
    for (c, n), v in sorted(conv.items()):
        if n == "DEV":
            if c != "DRAFTED":
                continue
            x = [y for y in v if y[0] == "ALLTX"][0]
            dr = [m for m in R["margins"] if m[0] == "DRAWN" and m[2] == "DEV" and m[1] == x[0]][0]
            row = stg[("DRAFTED", "ALLTX", "DEV")]
            lv_over = [(STATE_NAME[k[1]], y["i_least"], y["lim"][1] - y["i_least"]) for k, y in sorted(stg.items(), key=lambda t: STATES.index(t[0][1]))
                       if k[0] == "DRAFTED" and k[2] == "DEV" and y["i_least"] > y["lim"][1] and k[1] != "ALLTX"]
            beside = "; ".join("%s %.4f A (%+.4f A)" % (s, stg[("DRAFTED", "ALLTX", s)]["i_hi"], stg[("DRAFTED", "ALLTX", s)]["lim"][1] - stg[("DRAFTED", "ALLTX", s)]["i_hi"]) for s in ("S1", "S2", "S3"))
            out.append({
                "id": "L9P-F03", "class": "ASSUMPTION TO BOUND", "new": "carried (I-03)", "status": "OPEN",
                "subject": "the device rail's LM5176 average loop in PS-ALLTX at HIGH, with the three slot stages beside it",
                "figure": ("%.3f A DRAFTED, %.3f A DRAWN, against the loop's least %.4f A (VSNS %.0f mV over %.0f mOhm at +%.0f %%), %+.4f A; PLAN %.3f A; at the least load voltage of fb01's window (%.4f V) %.3f A if every load draws constant power (%+.4f A), "
                           "and at that voltage also %s; beside it in PS-ALLTX at HIGH at 5.1 V the slot stages on the same loop: %s"
                           % (x[2], dr[5], x[3][1], F["vsns"][0] * 1000, F["lm"]["SD"][3] * 1000, F["shunt_tol"] * 100, x[3][1] - x[2], x[1], row["v_least"],
                              row["i_least"], row["lim"][1] - row["i_least"], "; ".join("%s at HIGH %.3f A (%+.4f A)" % t for t in lv_over) if lv_over else "no other state", beside)),
                "rule": "CMP-001; the generator's own I-03 comparison (gen_sch_a.py: the conditional P-tier fails the loop minimum)",
                "why": "the PS-ALLTX currents of the device rail's loads are INCONCLUSIVE on held documents (cx1, I-03); HIGH takes each at its contract or maximum; no draft of this round moves a device rail load, and the slot stages carry their own coolers",
                "action": "I-03's bench reading of the device rail in PS-ALLTX, or the rail split W2 F-PR-04 named; the loop limits rather than damages (the rail droops)",
                "owner": "board A's generator owner under I-03, with the TEST-PLAN power rows"})
        if n == "PA" and c == "DRAFTED":
            x = v[0]
            out.append({
                "id": "L9P-F04", "class": "PHYSICAL QUESTION", "new": "carried (rv-pwr; F-PR-01)", "status": "OPEN",
                "subject": "the PA rail's LM5176 average loop at the PA's 113 W bound",
                "figure": "%.3f A at HIGH (W2 F-PR-02's 113 W, INFERRED) against the loop's least %.4f A; PLAN %.3f A (75 W)" % (x[2], x[3][1], x[1]),
                "rule": "CMP-001; F-PR-01 (gen_sch_a.py) sets the loop above the 6.0 A declared peak so that the 8.2 A bound meets it and the rail droops",
                "why": "the drain current at 13.8 V is the RA30H1317M1's, which its sheet states at 12.5 V only; rv-pwr carries it as a bench item",
                "action": "specimen: one RA30H1317M1 on a heat sink at 13.8 V with the design's VGG (board D, 4.30 to 4.68 V) into 50 Ohm at 144 to 146 MHz; measure the drain current at 30 W out; accept at most %.2f A; on failure the rail limits and the PA gives less than 30 W (no damage), and the choice is a lower output setting or a 5 mOhm ISNS shunt within the JST-VH lead's 10 A" % x[3][1],
                "owner": "the TEST-PLAN power rows (the bench), with board A's F-PR-01 and POWER-THERMAL section 7.2's record"})
    sus = [p for p in raw["pack"] if p[0] == "DRAFTED" and p[2] == "sustained"]
    states_hi = [p for p in sus if p[4] <= p[3] < p[5]]
    states_pl = [p for p in sus if p[4] > p[3]]
    busy = [p for p in R["pc"] if p["label"] == "PS-BUSY"][0]
    if states_hi:
        out.append({
            "id": "L9P-F05", "class": "ASSUMPTION TO BOUND", "new": "carried (rv-pwr 7.1), moved", "status": "OPEN",
            "subject": "sustained states over the pack's continuous current at HIGH at the gauge's under-voltage",
            "figure": "; ".join("%s %.2f A at HIGH (round 1 %.2f, rv-pwr %.2f), PLAN %.2f A" % (p[1], p[5], p[9], p[7], p[4]) for p in states_hi) + ", against %.0f A at %.1f V (the stack at %.2f V a cell)" % (F["i_cont"], F["cuv"] * F["series"], F["cuv"]),
            "rule": "the pack's declared continuous current (pcb_pack_protection.yaml, declared_continuous_a) at every stack voltage down to CUV",
            "why": "HIGH stacks maxima, the coolers now at their envelope; PS-BUSY's PLAN stays under (its margin at 10.0 V %.2f A, round 1's %.2f A, rv-pwr's %.2f A)" % (
                F["i_cont"] - busy[("DRAFTED", "plan")]["I"][-1], F["i_cont"] - busy[("DRAFTED-R1", "plan")]["I"][-1], F["i_cont"] - busy[("RV", "plan")]["I"][-1]),
            "action": "bounded by the control rv-pwr 9.3 took (the current trigger of the module shedding, read on the gauge's pack current); the trigger's setting is re-read on the drafted figures",
            "owner": "L4-E9 (C02 and C06: the shedding and the gauge's relay), POWER-THERMAL section 9.3's control"})
    if states_pl:
        out.append({
            "id": "L9P-F06", "class": "ASSUMPTION TO BOUND", "new": "carried (rv-pwr 7.1), moved", "status": "OPEN",
            "subject": "the outlets over PS-TYP and PS-BUSY at PLAN",
            "figure": "; ".join("%s %.2f A at PLAN (round 1 %.2f, rv-pwr %.2f)" % (p[1], p[4], p[8], p[6]) for p in states_pl) + " at %.1f V, against %.0f A" % (F["cuv"] * F["series"], F["i_cont"]),
            "rule": "the pack's declared continuous current, as L9P-F05",
            "why": "the outlets' contracts (PoE 32.4 W, USB-C 45 W) are what their stages may deliver; rv-pwr 7.1 found these rows over and took an outlet budget",
            "action": "bounded by rv-pwr 9.3's outlet budget (and the tablet's 18 W cap, a proposal); its numbers re-read on the drafted figures",
            "owner": "L4-E9 (C03, C04 and the tablet budget)"})
    return out


def render(R):
    F, pb = R["F"], R["cfgs"]["RV"].pb
    L = []
    w = L.append
    w("L9PWR (MESHSAT-1357): LAYER 9 ITEM 9.1, THE POWER BUDGET ON THE CURRENT DESIGN, WITH MARGINS AND SENSITIVITIES (ROUND 2). Prototype design,")
    w("desk arithmetic: nothing built, powered or measured; no figure is a measurement. RV is record rv-pwr's model as committed (the boards as")
    w("generated at 1f614233); DRAWN the generators in this tree; DRAFTED is DRAWN plus the release-guarded drafts of Layers 4, 8 and 9 that move a")
    w("power figure, none applied; DRAFTED-R1 is round 1's DRAFTED tree (38ef774c) rebuilt on the same evaluator, the figures other records took")
    w("from round 1. Tiers as rv-pwr's: S a primary document gives PLAN; R a document bounds the load and PLAN sits inside it by a")
    w("stated duty; D a generator declares it; T a placeholder. LOW, PLAN and HIGH are rv-pwr's three values per load; HIGH puts every load at")
    w("its maximum at once (an upper bound, not a scenario). Watts at the pack side are rv-pwr's battery W (VBAT plus the pack path's I2R at 14.4 V).")
    w("")
    w("0. INPUTS (sha256/16)")
    for k, p, s in R["pins"]:
        w("   %-11s %s  sha256 %s" % (k, p, s))
    w("   the copies in inputs/ (inputs/SOURCES.txt), each read with git show from its author's branch, not merged:")
    for k, (br, cm, src, lines) in ORIGIN.items():
        w("     %-11s %s@%s on %s, %s" % (k, cm, src, br, "the whole file" if lines is None else "its lines %d to %d" % lines))
    for k, what in IN_TREE.items():
        w("   read from this tree since round 3, no copy: %s, %s" % (k, what))
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
    w("        round 6 (fans12 at 89924e40): HIGH the envelope %.2f W at the step-up's %.3f V top (its output %.3f / %.3f / %.3f V) over the step-up's %.2f, any duty, no Fan_PWM"
      % (F["fan_env"], F["su_vout"][2], F["su_vout"][0], F["su_vout"][1], F["su_vout"][2], F["su_eta_lo"]))
    w("        maximum; the slot row %.2f A (%.2f W of fan over %.2f at %.1f V; the drawn J_FAN row %.2f A); the 12 V rail %.2f A typical; board B's slot peak %.1f A; the branch's bounded start %.2f A (100 us average)"
      % (F["fan_row"], F["fan_row_basis"][0], F["fan_row_basis"][1], F["fan_row_basis"][2], F["fan_row_old"], F["fans12_rail"][1], F["slot_peak_b"], F["start_bound"]))
    w("     D5 U901: RON at most %.4f Ohm, limit %.3f / %.3f / %.3f A (l8r2)" % (F["ron_lo"], F["pnl_efuse"][0], F["pnl_efuse"][1], F["pnl_efuse"][2]))
    w("     D6 slots 1 and 3: LM5176 U%d and U%d (slotlm), ISNS %.0f mOhm, the rails' declared efficiency %.2f; the loop's least %.4f A; the slot leads' peak %.1f A, VBAT's entries Q%d, Q28, Q%d at %.2f A"
      % (F["slot_base"]["1"] + 1, F["slot_base"]["3"] + 1, F["slot_isns"] * 1000, F["slot_eff"], F["vsns"][0] / (F["slot_isns"] * (1 + F["shunt_tol"])), F["slot_peak"], F["slot_base"]["1"] + 1, F["slot_base"]["3"] + 1, F["slot_entry"]))
    w("     D7 board B's buck33 RT: %.0f k drawn, %.0f kHz by DS41979 Eq. 7 (RT[kOhm] = %.0f / fsw[kHz]); %.0f k drafted, %.0f kHz, the maker's curves' frequency"
      % (F["rt_old"], F["ap_eq7"] / F["rt_old"], F["ap_eq7"], F["rt_new"], F["ap_eq7"] / F["rt_new"]))
    wd = stage_window(F["vref"], F["ibias"], F["rfb"][0], F["rfb"][1], F["fb_tol_drawn"], F["drop_s"])
    wf_ = stage_window(F["vref"], F["ibias"], F["rfb"][0], F["rfb"][1], F["fb_tol"], F["drop_s"])
    w("     D8 the 5.1 V stages' divider %.1f k over %.0f k (gen_sch_a.py); VREF %.3f / %.3f / %.3f V and IBIAS(FB) at most %.0f nA (SNVSAI1D); the rails' drop budget %.0f %% (slots), %.0f %% (device rail):"
      % (F["rfb"][0] / 1000, F["rfb"][1] / 1000, F["vref"][0], F["vref"][1], F["vref"][2], F["ibias"] * 1e9, F["drop_s"] * 100, F["drop_dev"] * 100))
    w("        at %.1f %% (drawn) %.4f to %.4f V, the least at the loads %.4f V; at %.1f %% (fb01) %.4f to %.4f V, the least at the loads %.4f V"
      % (F["fb_tol_drawn"] * 100, wd[0], wd[1], wd[2], F["fb_tol"] * 100, wf_[0], wf_[1], wf_[2]))
    w("     D9 board P's breaker, the LM5069%s (%s, l9stk 15.4b): the sense %.1f and %.1f mOhm in parallel, %.4f mOhm nominal, its window %.4f to %.4f mOhm (taken at the highest); %d x CSD18510Q5B, %.2f mOhm at 10 V and 25 C, %.3f mOhm at 150 C (x%.1f), in parallel"
      % (F["brk_variant"][0], F["brk_variant"][1], F["brk_rs_pair"][0] * 1000, F["brk_rs_pair"][1] * 1000, F["brk_rs"] * 1000, F["brk_rs_win"][0] * 1000, F["brk_rs_win"][1] * 1000, F["brk_fets"][0], F["brk_fets"][1], F["brk_fet_hot"][2], F["brk_fet_hot"][3]))
    w("     D10 the battery FETs: %d x BUK6Y10-30P at %.3f mOhm each at 150 C (l9stk, L4-E11's bound): %.4f mOhm, against the pair's %.4f mOhm; L4-E11's charger draft writes %s"
      % (F["bat_fets"][0], F["bat_fets"][1], F["bat_fets"][1] / F["bat_fets"][0], F["fet_bound"] / 2 * 1000, ", ".join(F["bat_refs"])))
    w("   the round 1 parser's lines SET ASIDE in round 2 (the figure they read was removed or superseded by its record):")
    for a, b in SET_ASIDE:
        w("     %s: %s" % (a, b))
    w("   how the fans are taken (SESSION, under the owner's standing rule of 26 September 2026): HIGH is the picked fan's maker figure at full speed (S)")
    w("     for the mixers, and for the coolers since round 2 l8r2's envelope (%.2f W at the step-up's %.3f V top over its %.2f, the slot row %.2f A the draft" % (F["fan_env"], F["su_vout"][2], F["su_eta_lo"], F["fan_row"]))
    w("     declares; the maker prints only 12 V and free air); LOW and PLAN keep rv-pwr's duty figures (tier R), because the duty the controls set")
    w("     (R-150) is unset and L4-E11 18b and Layer 7 carry the same PLAN; a draft converter's efficiency is the draft's own assumption, its range in")
    w("     section 9. Why: the alternative, PLAN at full speed, would replace an unset duty by its maximum and hide the duty's effect inside the")
    w("     headline instead of showing it as a sensitivity; the coolers' HIGH is the bound the draft sizes its slot rows and leads on, so the budget's")
    w("     HIGH and the drafts' declarations agree (section 8, R9); the maker's 2.0 W is kept as the other end in section 7 (DRAFTED-MK)")
    w("   the pack: no difference. pcb_pack_protection.yaml declares '%s', %dS%dP; rv-pwr already models it (C_MIN %.2f Ah a cell, R_CELL %s Ohm" % (F["topology"], F["series"], F["parallel"], pb.C_MIN, " / ".join("%.3f" % v for v in pb.R_CELL.values())))
    w("     LOW / PLAN / HIGH); L4-E10's usable %.1f Wh enters only B7's consequence (section 8, R3), energy being item 9.2's" % F["usable_wh"])
    w("   the states: rv-pwr's eight and record hc2's three (CONOPS 4c: the reduced mode PS-RED2, slots 2 and 3; the heat stage PS-SURV as board B is")
    w("     generated and PS-SURV-R after BANK-R1); charging on shore is the B4 balance (section 8, R2); source-only operation and its entry current are")
    w("     L4-E11's (its section 3), not a pack-side figure; the system-node demand per state (VBAT, section 3) is what the charger must carry there")
    w("   the pack path (ohms):")
    for cn in ("RV", "DRAWN", "DRAFTED-R1", "DRAFTED"):
        w("     %-10s %.6f (%s)" % (cn, R["r_path"][cn][0], "; ".join("%s %.6f" % (a.split(" (")[0].split(":")[0], b) for a, b, s in R["r_path"][cn][1])))
    w("   NOT MODELLED, each with its reason:")
    for a, b in NOT_MODELLED:
        w("     %s: %s" % (a, b))
    w("")
    w("2. THE MODEL CHECK: this script's evaluator on rv-pwr's own tree against rv-pwr's functions (state_full), every state and scenario and record")
    w("   hc2's three states: largest difference %.9f W (%s; printed at 1e-9 W, below which a float sum's order may move it)" % (R["check_worst"], "within 1e-9 W" if R["check_worst"] < 1e-9 else "OVER 1e-9 W"))
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
    w("3b. DRAFTED BEFORE THIS ROUND AND AFTER: round 1's DRAFTED (DRAFTED-R1, 38ef774c, rebuilt here) against round 2's, the pack side LOW / PLAN / HIGH (W),")
    w("   the change at PLAN and at HIGH, and the pack current at 14.4 V at PLAN (A)")
    w("   %-28s %-25s %-25s %9s %9s %7s %7s" % ("state", "DRAFTED-R1", "DRAFTED", "dPLAN", "dHIGH", "I R1", "I now"))
    for st in STATES:
        a, b = R["tot"][("DRAFTED-R1", st)], R["tot"][("DRAFTED", st)]
        w("   %-28s %7.2f /%7.2f /%7.2f   %7.2f /%7.2f /%7.2f   %+9.3f %+9.3f %7.3f %7.3f" % (STATE_NAME[st], a["lo"]["pb"], a["plan"]["pb"], a["hi"]["pb"], b["lo"]["pb"], b["plan"]["pb"], b["hi"]["pb"],
          b["plan"]["pb"] - a["plan"]["pb"], b["hi"]["pb"] - a["hi"]["pb"], a["plan"]["i14"], b["plan"]["i14"]))
    w("   of dHIGH, the coolers' envelope over round 1's maker figure alone (section 4's D5 at HIGH less DRAFTED-R1's HIGH), W: " + "; ".join(
        "%s %+.3f" % (STATE_NAME[st].split(" (")[0], R["wf_hi"][10][st] - R["tot"][("DRAFTED-R1", st)]["hi"]["pb"]) for st in STATES))
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
    w("   HIGH, the limit, the margin at HIGH; an input-side limit is judged on the state's input power over VBAT's %.3f V floor, at HIGH with" % F["vsys"][0])
    w("   every load evaluated at that floor). DRAWN's margins follow"
      + " where its converters differ. Status: RV rv-pwr's row unchanged, MAIN a change on main since 1f614233, DRAFTED a draft not")
    w("   applied.")
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
    W5 = R["cfgs"]["DRAFTED"].window
    w("5b. THE LM5176 5.1 V STAGES SIDE BY SIDE (L9P-F02 and L9P-F03): slots 1 to 3 and the device rail, each against its average loop's least; the")
    w("   output current at PLAN and at HIGH at the model's 5.1 V; on DRAFTED at HIGH also at the least load voltage of fb01's window, %.4f V (every load" % W5[2])
    w("   behind a converter draws its power), and for the slots the cooler branch's bounded start (%.2f A, a 100 us average) and a degraded cooler" % F["start_bound"])
    w("   (%.5f A, the eFuse's least limit by l8r2's method, at %.2f V over %.2f) on the slot's other loads at HIGH (l8r2's bounds, CONDITIONAL on C4-3); the margins at HIGH; DRAWN and round 1" % (F["su_efuse_x"][0], F["su_vout"][2], F["su_eta_lo"]))
    w("   (DRAFTED-R1) at 5.1 V for comparison, slots 1 and 3 there on the AP64500's 5 A")
    for st in STATES:
        w("   == %s" % STATE_NAME[st])
        for n in ("S1", "S2", "S3", "DEV"):
            if ("DRAFTED", st, n) not in R["stages"]:
                continue
            x = R["stages"][("DRAFTED", st, n)]
            lim = x["lim"][1]
            s = "      %-4s %-34s %7.4f A  PLAN %6.3f  HIGH %6.3f (%+7.4f)" % (n, x["lim"][0], lim, x["i_plan"], x["i_hi"], lim - x["i_hi"])
            if "i_least" in x:
                s += "  least V %6.3f (%+7.4f)" % (x["i_least"], lim - x["i_least"])
            if "start" in x:
                s += "  start %6.3f (%+7.4f)  degraded %6.3f (%+7.4f)  other %7.3f W" % (x["start"], lim - x["start"], x["degraded"], lim - x["degraded"], x["other"])
            for cn in ("DRAWN", "DRAFTED-R1"):
                y = R["stages"].get((cn, st, n))
                if y:
                    s += "  %s %6.3f/%6.3f (%+.3f)" % ("DRAWN" if cn == "DRAWN" else "R1", y["i_hi"], y["lim"][1], y["lim"][1] - y["i_hi"])
            w(s)
    for lab, key in (("steady at 5.1 V", None), ("steady at the least load voltage", "i_least"), ("the bounded start", "start"), ("a degraded cooler", "degraded")):
        v = slot_least(R, key)
        w("   slots 1 and 3, the least margin over every state, %s: %+.4f A (%s, %s)" % (lab, v[0], STATE_NAME[v[1]], v[2]))
    w("")
    w("6. THE PACK CURRENT (A) at the stack voltages %s V (the last the gauge's CUV, %.2f V a cell x %d), PLAN and HIGH, RV / DRAWN / DRAFTED;" % (" / ".join("%.1f" % v for v in R["v_stack"]), F["cuv"], F["series"]))
    w("   against the declared continuous %.0f A (sustained rows) or the peak %.0f A (key-down rows, which D-11's floors govern, section 7); the stack" % (F["i_cont"], F["i_peak"]))
    w("   voltage below which the row passes the limit (DRAFTED, PLAN / HIGH)")
    for r in R["pc"]:
        lim = F["i_cont"] if r["kind"] == "sustained" else F["i_peak"]
        w("   %-50s %-9s" % (r["label"], r["kind"]))
        for cn in ("RV", "DRAWN", "DRAFTED-R1", "DRAFTED"):
            a, b = r[(cn, "plan")], r[(cn, "hi")]
            w("      %-10s PLAN %s   HIGH %s" % (cn, " ".join("%6.2f" % x for x in a["I"]), " ".join("%6.2f" % x for x in b["I"])))
        key = "V_cont" if r["kind"] == "sustained" else "V_peak"
        a, b = r[("DRAFTED", "plan")], r[("DRAFTED", "hi")]
        w("      over %.0f A below %.2f V (PLAN) / %.2f V (HIGH): %s" % (lim, a[key], b[key], "PLAN over at %.1f V" % R["v_stack"][-1] if a["I"][-1] > lim else ("HIGH over at %.1f V" % R["v_stack"][-1] if b["I"][-1] > lim else "within to %.1f V" % R["v_stack"][-1])))
    w("6b. THE PACK PATH'S ELEMENTS PER STATE (DRAFTED): the pack current at 14.4 V (PLAN / HIGH, A) and each element's I2R (PLAN / HIGH, W); round 1's")
    w("   battery FET pair at round 1's current beside the three FETs of D10; board P's breaker (D9) and the third FET (D10) are the elements this round adds")
    names = [a.split(" (")[0].split(":")[0] for a, b, s in R["cfgs"]["DRAFTED"].r_parts]
    w("   elements: " + "; ".join("%d %s %.6f Ohm" % (i + 1, n, b) for i, (n, (a, b, s)) in enumerate(zip(names, R["cfgs"]["DRAFTED"].r_parts))))
    for st in STATES:
        e0, e1 = R["elems"][(st, "plan")], R["elems"][(st, "hi")]
        w("   %-28s I %6.3f / %6.3f  %s  | round 1's pair %6.4f / %6.4f W at %6.3f / %6.3f A" % (
            STATE_NAME[st], e0["I"], e1["I"], "  ".join("%d %6.4f / %6.4f" % (i + 1, p0[3], p1[3]) for i, (p0, p1) in enumerate(zip(e0["parts"], e1["parts"]))),
            e0["pair_r1"], e1["pair_r1"], e0["I_r1"], e1["I_r1"]))
    w("")
    w("7. D-11's FLOORS ON RV-PWR'S METHOD (section 7.2 there): the stack voltage at %.0f A, the rest voltage at the cell resistances %s Ohm, the" % (F["i_peak"], " / ".join("%.3f" % v for v in pb.R_CELL.values())))
    w("   margin under the floor at the highest, and the largest cell resistance the floor covers. RV is rv-pwr's main pack path (R17 added, its")
    w("   record main_pack_path_R17); the heater row adds the regulated mat as rv-pwr does (rv-pwr: 7.5 W at its declared 0.88; DRAWN and DRAFTED: U33's %.2f)" % F["heat_eff"])
    for cn in ("RV", "DRAWN", "DRAFTED-R1", "DRAFTED"):
        D = R["d11"][cn]
        w("   %s (pack path %.6f Ohm)" % (cn, D["r"]))
        for lab, row in D["rows"].items():
            w("      %-66s VBAT %7.2f W  stack %6.3f V  rest %s V  floor %.1f V  margin %+6.3f V  R_cell covered %.4f" % (
                lab, row["vbat_W"], row["V_stack"], " / ".join("%6.3f" % row["V_rest"][k] for k in ("lo", "plan", "hi")), row["floor"], row["margin_hi"], row["r_cell_max"]))
    w("   the all-transmit basis step by step (each step of section 1 from DRAWN, the rest voltage needed at R_cell high and its change); DRAFTED-R1")
    w("   is round 1's D5 with l8r2's round 2 cooler, so D5's row less DRAFTED-R1's is the coolers' envelope at HIGH alone")
    prev = None
    for sid, row in R["d11_steps"]:
        w("      %-4s VBAT %7.2f W  path %.6f Ohm  stack %6.3f V  rest %6.3f V%s" % (sid, row["vbat_W"], row["r"], row["V_stack"], row["V_rest"]["hi"], "" if prev is None else "  %+7.4f V" % (row["V_rest"]["hi"] - prev)))
        prev = row["V_rest"]["hi"]
    r1 = R["d11"]["DRAFTED-R1"]["rows"][BASIS]
    w("      R1   VBAT %7.2f W  path %.6f Ohm  stack %6.3f V  rest %6.3f V  (D5 less R1: %+7.4f V)" % (r1["vbat_W"], r1["r"], r1["V_stack"], r1["V_rest"]["hi"], dict(R["d11_steps"])["D5"]["V_rest"]["hi"] - r1["V_rest"]["hi"]))
    fr = R["floor_rule"]
    w("   L4-E9 round 7's floor %.1f V rest (%.3f V a cell, D-17, from round 1's drafts): DRAFTED needs %.3f V, margin %+.3f V; round 7's rule (the least floor" % (fr["floor_r7"], F["r7_floor"][1], fr["need"], fr["margin"]))
    w("   on its %.1f V step with at least %.1f V over the need) gives %.1f V (%.3f V a cell) on this round's drafts; ChargeVoltage's %.3f V maximum leaves %.3f V of" % (fr["step"], fr["over"], fr["floor_req"], fr["floor_req"] / F["series"], F["r7_window"], F["r7_window"] - fr["floor_req"]))
    w("   rest voltage for all-transmit (round 7: %.3f V); the heater row needs %.3f V (the heater stays off while keyed); the PA-alone row %.3f V against %.1f V" % (F["r7_window"] - fr["floor_r7"], fr["heater"], fr["pa"], F["pa_floor"]))
    mk = R["d11_mk"]["rows"][BASIS]
    w("   the same DRAFTED tree with the coolers at round 1's HIGH (the maker's %.1f W at 12 V over %.2f), the other end should l8r2's C4-3 read the coolers" % (float(F["cooler"][5]), F["su_eta"]))
    w("   there: VBAT %.2f W, stack %.3f V, needs %.3f V (%+.3f V against %.1f V); round 7's rule gives %.1f V" % (mk["vbat_W"], mk["V_stack"], fr["need_mk"], fr["floor_r7"] - fr["need_mk"], fr["floor_r7"], fr["floor_req_mk"]))
    w("")
    ca = R["calltx"]
    nw, nr, ob, orw = ca["new"], ca["new_rv"], ca["old_basis"], ca["old_raw"]
    w("7b. C-ALLTX REV 3, THE CASE ROW (the coordinator's row of 4 October 2026, plan section 4a; rev 2's definition, which rev 3 keeps), FROM ITS TEXT, ON DRAFTED: every transmitter at")
    w("   its HIGH figure, the monitor full, the fans running at full speed, the outlets, the heater and the standby card off, every other load at its")
    w("   PS-ALLTX PLAN figure, the compute modules at their typical %.1f W; %.0f A from a %.1f V rest, R_cell %.3f Ohm (an ASSUMPTION; rv-pwr's high)" % (
        CASE_CM5, CASE_I, CASE_V_REST, nw["r_cell"]))
    w("   each load's figure and the rule that set it (W at its pins; HIGH and PLAN are its PS-ALLTX figures):")
    for ld in R["cfgs"]["DRAFTED"].loads:
        n = ld["name"]
        t = ld["d"]["ALLTX"]
        w("     %-46s %7.3f W  %-36s (PLAN %7.3f, HIGH %7.3f; D-11's basis %7.3f)" % (n, ca["vals"][n], ca["rule"][n], t[1], t[2], ca["basis_vals"][n]))
    w("   the converters at the case's VBAT %.3f V (each pack-fed converter's input; the loss in W, largest first):" % nw["vbat"])
    for n, x in sorted(nw["conv_by"].items(), key=lambda kv: -kv[1]):
        nd = nw["nodes"][n]
        w("     %-7s %7.3f W lost: in %8.3f W, out %8.3f W, efficiency %.4f at %6.3f V in  (%s)" % (n, x, nd[0], nd[1], nd[3], nd[4], R["cfgs"]["DRAFTED"].nodes[n][4][:90]))
    w("   THE ROW: load pins %.3f W + conversion %.3f W = %.3f W at VBAT (%.3f V at %.0f A); path %.6f Ohm, %.3f W; cells %.4f Ohm, %.3f W" % (
        nw["load"], nw["conv"], nw["p"], nw["vbat"], nw["i"], nw["r_path"], nw["path_w"], nw["r_cells"], nw["cell_w"]))
    w("     needs %.4f V rest at %.0f A; the allowance at %.1f V and %.0f A is %.3f W at VBAT (%.1f W of cell EMF less the cells' %.3f W and the path's %.3f W)" % (
        nw["need"], nw["i"], CASE_V_REST, nw["i"], nw["allow"], nw["emf_w"], nw["cell_w"], nw["path_w"]))
    w("     the deficit %+.3f W at VBAT, %+.4f V of rest voltage; with the converters at rv-pwr's 16.8 V instead: %.3f W, needs %.4f V, deficit %+.3f W" % (
        nw["deficit"], nw["need"] - CASE_V_REST, nr["p"], nr["need"], nr["deficit"]))
    w("   OLD AND NEW (the rows this one replaces as the case's figure, all on DRAFTED, R_cell %.3f Ohm):" % nw["r_cell"])
    w("     old, the raw PS-ALLTX HIGH row before C1 (every load at HIGH, the standby card at %.1f W, converters at 16.8 V): %.3f W, needs %.4f V" % (orw["standby"], orw["p"], orw["need"]))
    w("     the same row after C1 (the standby card %.1f W): %.3f W, needs %.4f V" % (ca["raw_fixed"]["standby"], ca["raw_fixed"]["p"], ca["raw_fixed"]["need"]))
    w("     old, D-11's basis on rv-pwr's typ_nontx (section 7: the compute modules and the NVMe at PS-TYP, the standby card off, every other load at")
    w("       HIGH, converters at 16.8 V): %.3f W, needs %.4f V; at the case's VBAT %.3f V: %.3f W, needs %.4f V" % (ob["vbat_W"], ob["V_rest"]["hi"], ca["basis_case"]["vbat"], ca["basis_case"]["p"], ca["basis_case"]["need"]))
    w("     NEW, C-ALLTX rev 3 from its text at the case's VBAT: %.3f W, needs %.4f V; the loads D-11's basis keeps at HIGH and the row's text takes at" % (nw["p"], nw["need"]))
    w("       typical: " + "; ".join("%s %.3f to %.3f W" % (n, ca["basis_vals"][n], ca["vals"][n]) for n in sorted(ca["vals"]) if abs(ca["basis_vals"][n] - ca["vals"][n]) > 1e-9 and not n.startswith("CM5")))
    w("     on DRAWN (the generators as they are, no draft): %.3f W, needs %.4f V" % (ca["drawn"]["p"], ca["drawn"]["need"]))
    w("   SENSITIVITIES (labelled scenarios, not the case): the compute modules at 8 W (the budget's HIGH; K4 holds no numerical ceiling): %.3f W," % ca["cm5_8"]["p"])
    w("     needs %.4f V; the fans at their PLAN duty: %.3f W, needs %.4f V" % (ca["cm5_8"]["need"], ca["fans_plan"]["p"], ca["fans_plan"]["need"]))
    w("")
    w("8. THE RECONCILIATION WITH LAYER 4 AND THE OTHER RECORDS (each line: their figure, this script's reproduction from their inputs, EQUAL or")
    w("   not, the current design's figure, and the difference explained; R9 is record l8r2's, R12 record l9stk's)")
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
        w("      status: %s" % x["status"])
        w("      figure: %s" % x["figure"])
        w("      rule:   %s" % x["rule"])
        w("      why:    %s" % x["why"])
        w("      action: %s" % x["action"])
        w("      owner:  %s" % x["owner"])
    w("   within their rules (no finding): every other converter in every state; U42 on VSYS_E, U22, the coolers' eFuses and U901 (DRAFTED);")
    w("   slots 1 and 3 on the LM5176 (section 5b); D-11's PA-alone floor on every tree; the heater rows of section 7 are over the floor on every")
    w("   tree, which is why the rule holds the heater off during any key-down (rv-pwr 7.2), so they are not a finding")
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
