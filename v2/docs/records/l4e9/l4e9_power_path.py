#!/usr/bin/env python3
"""l4e9_power_path.py: layer 4 task L4-E9 (MESHSAT-1357, 1 October 2026). The connected power architecture and Layer 4's
closure gate for it: the executable reconciliation of every interface between the blocks of the selected architecture
(A1, the owner's D-06 single 4S3P; A2 recorded as a proposal), with the simultaneous-operation, startup and fault traces
that are computed here and the closure gate's predicate.

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured. No generator, registry, rendered page,
Layer 3 file, pcb_interfaces.yaml, HW-FW-CONTRACT.md or other record is edited. Every figure is READ, never retyped:
  - from the generators (gen_sch_a.py, gen_sch_e.py, gen_sch_p.py) by their syntax tree: the rail declarations and the
    part value texts;
  - from board A's committed netlist (the VBAT capacitors, U17's sense nets);
  - from the records' committed outputs (L4-E4 to L4-E8, the energy replay, s120, the power budget, the load trace) by a
    pattern on the line that prints the figure;
  - from the makers' documents by pdftotext on the cited page;
  - from pcb_pack_protection.yaml, pcb_envelope.yaml, pcb_interfaces.yaml and HW-FW-CONTRACT.md by their text.
Each input is pinned by sha256 (exit 2 otherwise). L4-E8's record is read from the tree if it is there and otherwise from
the accepted commit L4E8_COMMIT on fnd/l4e8 (the coordinator's check 3); the bytes are pinned either way. L4-E7R (the 100 W
control decision on board E and the solar entry's surge protection, in its fix round on fnd/l4e7) is not read: its rows are
PENDING.

The few figures this record sets itself are named where they are used (the copper constants of the F1 bound, the
capacitance retained under bias in the pack-open bound, the back-feed diode's drop taken as zero). Evidence classes, from
strongest to weakest: MAKER, NETLIST (and the generator's declarations), MODELED, INFERRED, CONDITIONAL (a calculated result
resting on an unwarranted assumption or an open measurement), ASSUMPTION (a figure no document gives), PENDING (waits on a
record not yet landed). A row's class is its weakest check's.

Run from the repository root:  python3 v2/docs/records/l4e9/l4e9_power_path.py > v2/docs/records/l4e9/l4e9_power_path.out
Needs pdftotext and PyYAML. A few seconds. Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed;
4: a predicate failed (a check's arithmetic, the gate's rule, the register's or the handover's form)."""
import ast
import hashlib
import math
import os
import re
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
L4E8_COMMIT = "3c8f7a1fe0995b1d37f03fcace44544c6c17dcbe"     # fnd/l4e8, the coordinator's check 3 (accepted), figures as a282c8b7
L4E7R = ("PENDING: L4-E7R's CS101 follow-up, the backstop's trip under TEST-PLAN M2 (an INB filter or a ripple-shunt capacitor ahead "
         "of the sense bank, on the same topology; fnd/l4e7 after its closing check 42fe879f)")

PINS = {
    "gen_a": ("v2/ecad/tools/gen_sch_a.py", "6a136feec6c9cf4e2011ed8c45a1f2e0adc3e263718c355b4b909872ee5d3c4b"),
    "gen_e": ("v2/ecad/tools/gen_sch_e.py", "f846e138cb53a8c63247efb3ad7b5cc44a68cb73e71699c65fd53b63c01af186"),
    "gen_p": ("v2/ecad/tools/gen_sch_p.py", "740817ada5c8e14af8c8e001b775e09cbae94d6a03ad462ee2e1c1755bc935a3"),
    "net_a": ("v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "6c40250c47195ebb7b2ae1388e284dc7f2fba9f2e683f654a47c98444290e8c5"),
    "l4e4": ("v2/docs/records/l4e4/l4e4_limits.out", "f68bf6951a6361caf6c41db14d86d735f9e3e9736723984ef61234aa10a80694"),
    "l4e5": ("v2/docs/records/l4e5/l4e5_source_control.out", "f9c98ec5c43ada0e1a5a033a794c98b45f110ffcb0a67ff8c81a31fede134e71"),
    "l4e6": ("v2/docs/records/l4e6/l4e6_fault_handling.out", "4f7cefb270f326d1956a7c5b1e11c8901e4f21a0ff3feb4fcb6d66fb78728c66"),
    "l4e8": ("v2/docs/records/l4e8/ripple_dense.out", "3b751989b8b70345469f2fdc14640fe041415b7333d669b205d2c675b046ab84"),
    "replay": ("v2/docs/records/l4e/l4e_replay.out", "59c6eeab16da98f8ddf16880ddcdc1d2a2c910f4256be9b69aade49dd4d2726d"),
    "s120": ("v2/docs/records/s120/vbus20_bound.out", "35c3e2e30fc637e0321daa1111e02aba84ab94fe789c59466e1f12c61470f823"),
    "budget": ("v2/docs/records/rv-pwr/pwr_budget.out", "58e40cf604804cc9d70c7fbeb1012be4552563fcc8ae7ef6755003c33acb902f"),
    "trace": ("v2/docs/records/l3batt/load_trace.out", "e35e62483b67fbe71bf89b819f6be46173ce708a8a62c683905d55a37ad4c218"),
    "packprot": ("v2/ecad/tools/pcb_pack_protection.yaml", "ab1dbc3f3f69aa4687a4fa9745c0cbdc96d0521146dc5d3f84698656e33c484b"),
    "envelope": ("v2/ecad/tools/pcb_envelope.yaml", "35cf43a2b7098a76abb4919685ece4d6e352331628f5f242c1492d9fcbbf2864"),
    "hwfw": ("v2/docs/HW-FW-CONTRACT.md", "1c211e467d81b8b70546bc4435c65d4bd2dcd0d2fc3606714a746b4d8d0ac1fa"),
    "ifaces": ("v2/ecad/tools/pcb_interfaces.yaml", "9ec50ccfae3b70a0b27c1f32fdf0461eadd99012cfe8954409bc2573771680c0"),
    "lm5176": ("v2/vendor/ti/lm5176-datasheet.pdf", "98191bec36d43771affa3e1540f6e1737347c19a1602747ffb4327509550a820"),
    "lm74700": ("v2/vendor/ti/ti-lm74700-q1.pdf", "e16b3a8c0023201fafa5825436f5f2dd6f885b92b84e65602b3f50d741c58b6f"),
    "csd19532": ("v2/vendor/power/ti-csd19532q5b-n-fet.pdf", "353ce937cff0b719e730010829720d25c2ece3637ed92fb7ad8cc370438559d1"),
    "bsc039": ("v2/vendor/infineon/infineon-bsc039n06ns-rev2.4-c534330.pdf", "8d95c1da9c78b3afb037e1f80c3bea1ed0f874f689e3a0c96d926dafe6a437b9"),
    "smcj": ("v2/vendor/power/littelfuse-smcj-series-tvs.pdf", "6e610db955ed876306999009c62b242f7de9bb05e2cd9717288a96586a5093ea"),
    "tps2596": ("v2/vendor/power/tps2596.pdf", "66f6bae4494f7bfe7dfdc314e508f0291d9ca1e87265cca9b6fdfeaa5cb19fe9"),
    "lm5069": ("v2/vendor/ti/ti-lm5069.pdf", "d60d8106a6e8113900ff8b9576dd959942fa7169742baf0beeb30684d4d64681"),
    "ina226": ("v2/vendor/ti/ti-ina226.pdf", "c9b67f886d4a5241a5e070723f7b61867409eeb27eed768b9cdd9cb17e03ca2d"),
    "bq25731": ("v2/vendor/ti/bq25731-datasheet.pdf", "3e5e927fdf63cf6a2397630987c58e947ebc80d5a1cfc93fb1fb58d98bb58973"),
    "fuse297": ("v2/vendor/keystone/littelfuse-297-ficcorp.pdf", "98a7e99bc5bbdf2abc9f329de5b779ea97fc78a3ba9aa8d8fecc0ec5b9c3a778"),
    "vh": ("v2/vendor/connectors/jst-vh-catalogue.pdf", "d51e669c597988b20c0963daf5bef7356cbd2104c1f867e9107c6fa6cd2b899c"),
    "millmax": ("v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf", "8ef40cd98d95c653ce506a1af457656b287a475342684ac110cf594f923782d6"),
    "xt60": ("v2/vendor/battery/amass-xt60-spec-tme.pdf", "c2cbb5962c1f37da89e76e505c75184dd07e84eec3a6fe5f24569dafc6f6b9e9"),
    "dec31": ("v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md", "094817023210d1b09d92e62716ba550d0fb5b11affc75fe18986bfc6ebae3609"),
    "fuse997": ("v2/vendor/power/held/littelfuse-997-mini58v-rev2025-11-18.pdf", "437b1fd2c8cb3ef16107ec14d096b31ef3c3cb83893325234e880deb7540393e"),
    "keystone": ("v2/vendor/keystone/M65p42.pdf", "caa141ea51ac68cf80ab6e14ad2075fcfc76206451f4bfe45330005c0deaf395"),
    "l4e7r": ("v2/docs/records/l4e7/l4e7_stage_settings.out", "7edcc52a88874a53a911736b989b51626cf7a380750f5d072a6bf8dcd0150969"),
    "l4e10": ("v2/docs/records/l4e10/l4e10_cell_thermal.out", "ce2d11f11eecfceef696eac1d6cda66d448cdfb3703d2fc69062e3a1a3f2aeac"),
}
# Read from the tree when the tree's file is the pinned one, else from the named commit: L4-E7R's selected solution (fnd/l4e7,
# the coordinator's closing check 42fe879f confirmed its figures) and L4-E10's final record (fnd/l4e10, closing check 573c8b8f)
FROM_COMMIT = {"l4e7r": "237cd9be", "l4e10": "79b2f568"}
FROM_LABEL = {"l4e7r": "fnd/l4e7, the selected solution", "l4e10": "fnd/l4e10, final, closing check 573c8b8f"}
FROM_L4E8 = {"l4e8"}       # read from L4E8_COMMIT when the path is not in the tree

# The few figures this record sets itself (each an input, named where it is used)
CU_RHO_20C = 0.01724      # ASSUMPTION: standard annealed copper, ohm mm2 / m at 20 C (a physical constant; no document held)
CU_ALPHA = 0.00393        # ASSUMPTION: copper's temperature coefficient, 1 / K (the constant r11dep's C-1 uses)
AWG18_MM2 = 0.823         # ASSUMPTION: the cross-section of an 18 AWG conductor, mm2 (the gauge's definition)
T_COLD = -20.0            # REQ-024's use boundary (D-02a), C: the cold copper gives the larger prospective current
BIAS_KEEP = 0.2           # ASSUMPTION: the fraction of a ceramic's nominal capacitance kept under DC bias (the review of
                          # decision 31's 'a fifth'); the pack-open bound states the fraction it actually needs
VF_BACKFEED = 0.0         # the body diode's drop on the back-feed path taken as zero: the larger DC_P, an upper bound
L2_TOL = 0.20             # Coilcraft XAL family inductance tolerance (+-20 %), as r11dep carries it for L1
# Read from the CSD19532Q5B sheet's figures by eye (INFERRED from the figure; SLPS414B p.6), named here as this record's inputs:
CSD_RDS_NORM_150C = 1.95   # Figure 8, normalized RDS(on) at TC 150 C, VGS 10 V (typical curve): the junction bound uses it
CSD_SOA_10MS_36V_A = 3.0   # Figure 10, the 10 ms single-pulse line at VDS 36 V, TC 25 C, RthetaJC 0.8 C/W max
SOA_TC_HOT = 100.0         # ASSUMPTION: Q7's case at most 100 C in the hot swap's fault; the line derated by (150 - TC) / 125
R23_NEW_K = 6.42           # SESSION: E192's 6.42k, the OVLO resolution (ii) for CS101 at a 36 V source, with R22 100k, both 0.1 %
PWRLIM_SPREAD = 31.0 / 25.0  # LM5069 PWRLIM-1 row 19 / 25 / 31 mV carried as the power limit's spread (INFERRED scaling)


_C_TEXT = {}     # the pinned text inputs of the last compute(), for part A's readers


def refuse(code, msg):
    sys.stderr.write("l4e9_power_path: %s; refusing\n" % msg)
    sys.exit(code)


def raw(key):
    rel, _ = PINS[key]
    p = os.path.join(TOP, rel)
    if key in FROM_COMMIT:
        if os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() == PINS[key][1]:
            return open(p, "rb").read(), "tree"      # the selected solution's file already in the tree
        r = subprocess.run(["git", "show", "%s:%s" % (FROM_COMMIT[key], rel)], cwd=TOP, capture_output=True)
        if r.returncode != 0:
            refuse(3, "%s is not at %s" % (rel, FROM_COMMIT[key]))
        return r.stdout, "commit %s" % FROM_COMMIT[key]
    if os.path.exists(p):
        return open(p, "rb").read(), "tree"
    if key in FROM_L4E8:
        r = subprocess.run(["git", "show", "%s:%s" % (L4E8_COMMIT, rel)], cwd=TOP, capture_output=True)
        if r.returncode != 0:
            refuse(3, "%s is neither in the tree nor at %s" % (rel, L4E8_COMMIT[:12]))
        return r.stdout, "commit %s" % L4E8_COMMIT[:12]
    refuse(3, "%s is missing" % rel)


def load_inputs():
    B, where = {}, {}
    for key, (rel, want) in PINS.items():
        b, w = raw(key)
        h = hashlib.sha256(b).hexdigest()
        if want is not None and h != want:
            refuse(2, "%s is not the pinned file (%s)" % (rel, h[:16]))
        B[key], where[key] = b, (w, h)
    return B, where


def pdf_text(key, first=None, last=None):
    rel = PINS[key][0]
    cmd = ["pdftotext", "-layout"]
    if first:
        cmd += ["-f", str(first), "-l", str(last or first)]
    r = subprocess.run(cmd + [os.path.join(TOP, rel), "-"], capture_output=True)
    if r.returncode != 0:
        refuse(3, "pdftotext failed on %s" % rel)
    return r.stdout.decode("utf-8", "replace")


def need(text, pat, what, flags=re.M):
    m = re.search(pat, text, flags)
    if not m:
        refuse(3, "%s not found" % what)
    return m


def f(m, i=1):
    return float(m.group(i))


# ------------------------------------------------------------------------------------------ the generators' declarations
class Gen:
    """A generator read by its syntax tree: module-level constants, the _intent.rail() declarations (also those inside a
    for loop over constant tuples) and the part value texts (part, r, c, ic, nfet; and the part a helper function draws)."""
    FUNCS = {"part": 3, "r": 1, "c": 1, "ic": 2, "nfet": 1}

    def __init__(self, text):
        self.tree = ast.parse(text)
        self.env, self.rails, self.values, self.helpers = {}, {}, {}, {}
        self._walk(self.tree.body, {})

    def ev(self, n, env):
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.Name):
            if n.id in env:
                return env[n.id]
            if n.id in self.env:
                return self.env[n.id]
            raise ValueError(n.id)
        if isinstance(n, ast.Tuple):
            return tuple(self.ev(e, env) for e in n.elts)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -self.ev(n.operand, env)
        if isinstance(n, ast.BinOp):
            a, b = self.ev(n.left, env), self.ev(n.right, env)
            ops = {ast.Add: lambda: a + b, ast.Sub: lambda: a - b, ast.Mult: lambda: a * b, ast.Div: lambda: a / b,
                   ast.Mod: lambda: a % b}
            return ops[type(n.op)]()
        if isinstance(n, ast.IfExp):
            raise ValueError("ifexp")
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("round", "min", "max"):
            args = [self.ev(a, env) for a in n.args]
            return {"round": round, "min": min, "max": max}[n.func.id](*args)
        raise ValueError(type(n).__name__)

    def _call(self, call, env):
        fn = call.func
        if isinstance(fn, ast.Attribute) and fn.attr == "rail" and isinstance(fn.value, ast.Name) and fn.value.id == "_intent":
            try:
                name = self.ev(call.args[0], env)
            except (ValueError, KeyError, TypeError):
                return
            vals = []
            for a in call.args[1:4]:
                try:
                    vals.append(self.ev(a, env))
                except (ValueError, KeyError, TypeError):
                    vals.append(None)
            kw = {}
            for k in call.keywords:
                if k.arg in ("v_work", "v_max", "efficiency"):
                    try:
                        kw[k.arg] = self.ev(k.value, env)
                    except (ValueError, KeyError, TypeError):
                        kw[k.arg] = None
            self.rails.setdefault(name, {"volts": vals[0], "typ": vals[1], "peak": vals[2], **kw})
        elif call.args and isinstance(call.args[0], ast.Constant) and (
                (isinstance(fn, ast.Name) and fn.id in self.FUNCS) or (isinstance(fn, ast.Attribute) and fn.attr == "tvs")):
            i = self.FUNCS[fn.id] if isinstance(fn, ast.Name) else 1
            if len(call.args) > i and isinstance(call.args[i], ast.Constant):
                self.values.setdefault(call.args[0].value, call.args[i].value)

    def _walk(self, body, env):
        for st in body:
            if isinstance(st, ast.Assign) and not env:
                for tgt in st.targets:
                    try:
                        v = self.ev(st.value, env)
                    except (ValueError, KeyError, TypeError, ZeroDivisionError):
                        continue
                    if isinstance(tgt, ast.Name):
                        self.env[tgt.id] = v
                    elif isinstance(tgt, ast.Tuple) and isinstance(v, tuple) and len(v) == len(tgt.elts):
                        for t, x in zip(tgt.elts, v):
                            if isinstance(t, ast.Name):
                                self.env[t.id] = x
            elif isinstance(st, ast.FunctionDef):
                for n in ast.walk(st):
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "part" and len(n.args) > 3 \
                            and isinstance(n.args[0], ast.Name) and isinstance(n.args[3], ast.Constant):
                        self.helpers.setdefault(st.name, []).append((n.args[0].id, n.args[3].value))
            elif isinstance(st, ast.For) and isinstance(st.target, (ast.Name, ast.Tuple)):
                try:
                    seq = self.ev(st.iter, env)
                except (ValueError, KeyError, TypeError):
                    seq = None
                if seq is None:
                    continue
                for item in seq:
                    e2 = dict(env)
                    if isinstance(st.target, ast.Name):
                        e2[st.target.id] = item
                    else:
                        for t, x in zip(st.target.elts, item):
                            e2[t.id] = x
                    for n in st.body:
                        for c in ast.walk(n):
                            if isinstance(c, ast.Call):
                                self._call(c, e2)
            for n in ([st] if isinstance(st, (ast.Expr,)) else []):
                for c in ast.walk(n):
                    if isinstance(c, ast.Call):
                        self._call(c, env)

    def rail(self, name):
        if name not in self.rails:
            refuse(3, "rail %s not declared" % name)
        return self.rails[name]

    def value(self, ref):
        if ref not in self.values:
            refuse(3, "part %s not found" % ref)
        return self.values[ref]


def amps_in(text, what):
    m = re.search(r"(\d+(?:\.\d+)?)\s*A\b", text)
    if not m:
        refuse(3, "no current in %s's value '%s'" % (what, text))
    return float(m.group(1))


def volts_in(text, what):
    m = re.search(r"(\d+(?:\.\d+)?)\s*V\b", text)
    if not m:
        refuse(3, "no voltage in %s's value '%s'" % (what, text))
    return float(m.group(1))


def cap_uf(v):
    m = re.match(r"\s*(\d+(?:\.\d+)?)\s*([pnu])", v)
    if not m:
        return None
    return float(m.group(1)) * {"p": 1e-6, "n": 1e-3, "u": 1.0}[m.group(2)]


# ------------------------------------------------------------------------------------------------------- the checks
ORDER = {"MAKER": 0, "NETLIST": 0, "MODELED": 1, "INFERRED": 2, "CONDITIONAL": 3, "ASSUMPTION": 4, "PENDING": 5}


class Chk:
    """One comparison across an interface: a (what is asked) against b (what is available or rated), with the relation
    that must hold, the evidence class of its weakest figure and the scope: 'selected' (the selected architecture, the
    Layer 4 decisions applied) or 'drawn' (the committed netlist, shown where a defect is found and resolved)."""

    def __init__(self, what, a, rel, b, unit, cls, src, scope="selected"):
        self.what, self.a, self.rel, self.b, self.unit, self.cls, self.src, self.scope = what, a, rel, b, unit, cls, src, scope
        if cls == "PENDING" or a is None or b is None:
            self.met = None
        else:
            self.met = {"<=": a <= b, "<": a < b, ">=": a >= b, ">": a > b}[rel]
        if cls not in ORDER:
            refuse(4, "unknown class %s" % cls)

    def line(self):
        if self.met is None:
            v = "PENDING" if self.cls == "PENDING" else "OPEN"
        else:
            v = "MEETS" if self.met else "NOT MET"
        ab = "%s %s %s %s" % (fmt(self.a), self.rel, fmt(self.b), self.unit) if self.met is not None else "(%s)" % self.unit
        tag = " [as drawn]" if self.scope == "drawn" else ""
        return "%s: %s: %s; %s (%s)%s" % (v, self.what, ab, self.cls, self.src, tag)


def fmt(x):
    if isinstance(x, float):
        s = ("%.4f" % x).rstrip("0").rstrip(".")
        return s
    return str(x)


def row_status(r):
    sel = [c for c in r["checks"] if c.scope == "selected"]
    worst = max((ORDER[c.cls] for c in sel), default=0)
    cls = [k for k, v in ORDER.items() if v == worst][0] if worst else "MAKER"
    if worst == ORDER["NETLIST"]:
        cls = "MAKER/NETLIST"
    if any(c.met is None and c.cls == "PENDING" for c in sel):
        st = "PENDING"
    elif any(c.met is False for c in sel):
        st = "NOT MET"
    elif worst >= ORDER["CONDITIONAL"]:
        st = "CONDITIONAL"
    else:
        st = "MEETS"
    return cls, st


# --------------------------------------------------------------------------------------------------------- the compute
def compute():
    B, where = load_inputs()
    T = {k: B[k].decode("utf-8", "replace") for k in B if not PINS[k][0].endswith(".pdf")}
    _C_TEXT.clear()
    _C_TEXT.update(T)
    F = {}

    # ===================================================================================== 1: the makers' rows
    t = pdf_text("lm5176", 5)
    F["u2_vin_abs"] = f(need(t, r"VIN, EN/UVLO, VISNS, VOSNS, ISNS\(\+\), ISNS\(.\)\s+.0\.3\s+(\d+)", "LM5176 VIN absolute maximum"))
    t = pdf_text("lm74700", 5)
    F["ld_ca_abs"] = f(need(t, r"CATHODE to ANODE\s+.5\s+(\d+)", "LM74700-Q1 CATHODE to ANODE absolute"))
    F["ld_anode_abs"] = f(need(t, r"ANODE to GND\s+.65\s+(\d+)", "LM74700-Q1 ANODE absolute"))
    F["ld_ac_rec"] = f(need(t, r"ANODE to CATHODE\s+.(\d+)", "LM74700-Q1 ANODE to CATHODE recommended minimum"))
    t = pdf_text("csd19532", 1)
    F["csd19532_vds"] = f(need(t, r"Drain-to-Source Voltage\s+(\d+)", "CSD19532Q5B VDS"))
    t = pdf_text("bsc039", 1)
    F["bsc039_vds"] = f(need(t, r"VDS\s+(\d+)\s+V", "BSC039N06NS VDS"))
    t = pdf_text("smcj")
    for part in ("SMCJ18A", "SMCJ22A", "SMCJ28A", "SMCJ40A"):
        m = need(t, r"%s\s+\S+\s+\S+\s+\S+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+\d+\s+([\d.]+)\s+([\d.]+)" % part, part + " row")
        F[part] = {"vr": f(m, 1), "vbr_min": f(m, 2), "vbr_max": f(m, 3), "vc": f(m, 4), "ipp": f(m, 5)}
    t = pdf_text("tps2596")
    F["tps2596_abs"] = f(need(t, r"Maximum Input Voltage Range\s+.0\.3\s+(\d+)\s+V", "TPS2596 VIN absolute"))
    t = pdf_text("lm5069")
    F["lm5069_vin_abs"] = f(need(t, r"VIN to GND \(3\)\s+.0\.3\s+(\d+)", "LM5069 VIN absolute"))
    m = need(t, r"VCL\s+Threshold voltage\s+VIN-SENSE voltage\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+mV", "LM5069 VCL")
    F["vcl"] = (f(m, 1), f(m, 2), f(m, 3))
    t = pdf_text("ina226")
    F["ina_abs"] = f(need(t, r"VVBUS\s+.0\.3\s+(\d+)\s+V", "INA226 VBUS absolute"))
    F["ina_cm_op"] = f(need(t, r"0 V . VIN\+ . (\d+) V", "INA226 CMRR common-mode condition"))
    F["ina_fs_mv"] = f(need(t, r"Full-scale range = ([\d.]+)mV", "INA226 shunt full scale"))
    t = pdf_text("bq25731", 8)
    F["u3_abs"] = f(need(t, r"SRN, SRP, ACN, ACP, VBUS, VSYS\s+.0\.3\s+(\d+)", "BQ25731 VBUS and VSYS absolute"))
    t = pdf_text("bq25731", 14)
    m = need(t, r"VSYSOVP_RISE\s+rising threshold to\s+\S+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "BQ25731 SYSOVP")
    F["sysovp"] = (f(m, 1), f(m, 2), f(m, 3))
    t = pdf_text("fuse297")
    F["f297_v"] = f(need(t, r"Voltage Rating:\s+(\d+)\s*VDC", "297 voltage rating"))
    F["f297_i"] = f(need(t, r"Interrupting Rating:[\s\x07]+(\d+)A @", "297 interrupting rating"))
    t = pdf_text("vh", 1)
    F["vh_16"] = f(need(t, r"Current rating:\s+(\d+) A", "VH rating"))
    need(t, r"AWG #16 with the standard type header", "VH AWG 16 condition")
    F["vh_18"] = f(need(t, r"^\s+(\d+)A\s+AC/DC", "VH AWG 18 shrouded rating"))
    need(t, r"AWG #18 with the shrouded type header", "VH AWG 18 condition")
    t = subprocess.run(["pdftotext", os.path.join(TOP, PINS["millmax"][0]), "-"], capture_output=True).stdout.decode()
    F["millmax_a"] = f(need(t, r"carrying (\d+) amps continuous current", "Mill-Max continuous current"))
    t = pdf_text("xt60")
    F["xt60_a"] = f(need(t, r"额定电流\s+(\d+)A", "XT60 rated current"))

    # ===================================================================================== 2: the generators
    gA, gE, gP = Gen(T["gen_a"]), Gen(T["gen_e"]), Gen(T["gen_p"])
    F["vbat"] = gA.rail("VBAT")
    F["vin_raw_a"] = gA.rail("VIN_RAW")
    F["vbus20"] = gA.rail("VBUS20")
    F["pa"] = gA.rail("+13V8_PA")
    F["hf"] = gA.rail("+12V_HF")
    F["poe"] = gA.rail("+54V_POE")
    F["pd"] = gA.rail("PD_VBUS")
    F["vmon"] = gA.rail("VMON")
    F["vheat"] = gA.rail("VHEAT")
    F["s2"] = gA.rail("+5V_S2")
    F["dev"] = gA.rail("+5V_DEV")
    F["a_f1"] = amps_in(gA.value("F1"), "A F1")
    F["a_d1"] = gA.value("D1")
    F["a_d2"] = gA.value("D2")
    F["vin_raw_e"] = gE.rail("VIN_RAW")
    F["pv"] = gE.rail("PV_P")
    F["trk"] = gE.rail("TRK_OUT")
    F["cell_f"] = gE.rail("CELL_F")
    F["veh_t"] = gE.env["_VEH_T"]
    F["e_f1"] = gE.value("F1")
    F["e_f2"] = gE.value("F2")
    F["e_d10"], F["e_d1"], F["e_d2"], F["e_d4"] = gE.value("D10"), gE.value("D1"), gE.value("D2"), gE.value("D4")
    F["e_q7"] = gE.value("Q7")
    F["e_r19"] = gE.value("R19")
    F["e_r21"], F["e_r23"] = gE.value("R21"), gE.value("R23")
    F["e_r10"] = gE.value("R10")
    F["e_jdcin"], F["e_jsolar"] = gE.value("J_DCIN"), gE.value("J_SOLAR")
    F["e_l2"] = gE.value("L2")
    idl = dict(gE.helpers.get("ideal_diode", []))
    if "qref" not in idl:
        refuse(3, "board E's ideal_diode helper draws no FET")
    F["e_q1"] = idl["qref"]
    F["p_pack"] = gP.rail("PACK_P")
    F["p_f1"], F["p_f2"] = gP.value("F1"), gP.value("F2")
    for k in ("e_q1", "e_q7"):
        if not re.search(r"\b(\d+) V\b", F[k]):
            refuse(3, "%s's value states no voltage" % k)
    F["e_q1_v"] = volts_in(F["e_q1"], "E Q1")
    F["e_q7_v"] = volts_in(F["e_q7"], "E Q7")
    if "BSC039N06NS" not in F["e_q1"] or "CSD19532Q5B" not in F["e_q7"]:
        refuse(3, "board E's Q1 and Q7 are not the parts the makers' rows were read for")

    # board A's netlist: VBAT's capacitors and U17's sense nets
    na = T["net_a"]
    m = need(na, r'\(net \(code "\d+"\) \(name "/?VBAT"\)', "VBAT net")
    blk = na[m.start(): na.find("(net (code", m.start() + 5)]
    caps = sorted(set(r for r, _ in re.findall(r'\(node \(ref "(C\d+)"\) \(pin "(\d+)"\)', blk)), key=lambda s: int(s[1:]))
    tot = 0.0
    for c in caps:
        mv = need(na, r'\(comp \(ref "%s"\)\s*\(value "([^"]+)"\)' % c, c + " value")
        u = cap_uf(mv.group(1))
        tot += u or 0.0
    F["vbat_caps"] = (len(caps), tot)
    F["vbat_d1_on_net"] = '(ref "D1")' in blk
    u17 = {}
    for net in ("POE_OUT", "+54V_POE"):
        mm = re.search(r'\(net \(code "\d+"\) \(name "/?%s"\)' % re.escape(net), na)
        if not mm:
            refuse(3, "net %s" % net)
        b2 = na[mm.start(): na.find("(net (code", mm.start() + 5)]
        u17[net] = re.findall(r'\(node \(ref "U17"\) \(pin "(\d+)"\)', b2)
    F["u17_nets"] = u17

    # ===================================================================================== 3: the records' figures
    t = T["l4e4"]
    m = need(t, r"declared\s+0\.93 x 0\.93: ([\d.]+) W, at least ([\d.]+) A: setting ([\d.]+) A \(minimum ([\d.]+) A, maximum ([\d.]+) A, through R11 ([\d.]+) A\)", "L4-E4 setting line")
    F["win_w"], F["win_need"], F["iin_host"], F["u3_min"], F["u3_max_board"], F["r11_need"] = (f(m, i) for i in range(1, 7))
    F["u3_max_u3"] = f(need(t, r"U3's own maximum ([\d.]+) A", "U3's own maximum"))
    m = need(t, r"HoJLR2512-3W-8mR-1%\s+C2904240 stock\s+\d+: band ([\d.]+) / ([\d.]+) / ([\d.]+) A", "8 mOhm band")
    F["r11_8"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(t, r"HoJLR2512-3W-7mR-1%\s+C2904239 stock\s+\d+: band ([\d.]+) / ([\d.]+) / ([\d.]+) A", "7 mOhm band")
    F["r11_7"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(t, r"^\s+62\.1 C\s+[\d.]+\.\.[\d.]+\s+([\d.]+) A, margin \+([\d.]+) A\s+([\d.]+) A, margin \+([\d.]+) A\s+([\d.]+) A, margin \+([\d.]+) A", "62.1 C margins")
    F["r11_min_62_alone"], F["r11_min_62_full"], F["r11_margin_62_full"] = f(m, 1), f(m, 5), f(m, 6)
    m = need(t, r"TRIP WINDOW at 5 mOhm: ([\d.]+) to ([\d.]+) A", "R138 trip window")
    F["trip"] = (f(m, 1), f(m, 2))
    F["recept_a"] = f(need(t, r"Bulgin PXP4043/C \(CASE-MARGINS.md\): (\d+) A", "receptacle rating"))
    F["q27_a"] = f(need(t, r"Q27 CSD18510Q5B .*?: (\d+) A continuous", "Q27 rating"))
    m = need(t, r"the stage ahead \(U19, R81 10 mOhm.*?: ([\d.]+) / ([\d.]+) / ([\d.]+) A", "U19 limit")
    F["u19_lim"] = (f(m, 1), f(m, 2), f(m, 3))
    F["pdo_a"] = f(need(t, r"Largest PDO current ([\d.]+) A", "PDO current"))

    t = T["l4e5"]
    h3 = {}
    for v in ("9.0", "12.0", "24.0", "36.0"):
        m = need(t, r"^\s+%s V \|.*\| ([\d.]+) A \| ([\d.]+) A \(\s*([\d.]+) %%\)\s*$" % re.escape(v), "H3 row %s V" % v)
        h3[float(v)] = (f(m, 1), f(m, 2), f(m, 3))
    F["h3"] = h3
    m = need(t, r"certainly in HIZ below ([\d.]+) V of VIN_RAW", "HIZ certain")
    F["hiz_below"] = f(m)
    F["hiz_out_above"] = f(need(t, r"out of HIZ \(with EN_HIZ = 0,\s+REG0x35 bit 7, reset 0b, p\.64; p\.27\) above ([\d.]+) V", "HIZ out"))
    F["pin_reg_from"] = f(need(t, r"VIN_RAW ([\d.]+) V at the band's top", "regulation from"))
    F["u3_at_9"] = f(need(t, r"At the 9 V floor U3 still gets at least ([\d.]+) A", "U3 at 9 V"))
    m = need(t, r"so E96 232 k: ceiling ([\d.]+) / ([\d.]+) / ([\d.]+) V", "raised ceiling")
    F["trk_ceiling"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(t, r"as drawn\s+([\d.]+) / ([\d.]+) / ([\d.]+) V: FBOUT", "drawn ceiling")
    F["trk_drawn"] = (f(m, 1), f(m, 2), f(m, 3))
    F["c26_pct"] = f(need(t, r"C26 10u 25V at (\d+) % of its 25 V", "C26 stress"))
    F["c24_pct"] = f(need(t, r"C24 39u 35V Panasonic 35SVPF39M polymer at (\d+) % of its 35 V", "C24 stress"))
    m = need(t, r"UV falling ([\d.]+) / ([\d.]+) / ([\d.]+) V", "restart guard")
    F["latch"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(t, r"LM5069 limits at ([\d.]+) to ([\d.]+) A \(([\d.]+) A with R19's 1 %\)", "entry limit")
    F["entry_lim"], F["entry_basis"] = (f(m, 1), f(m, 2)), f(m, 3)
    m = need(t, r"fault timeout of ([\d.]+) / ([\d.]+) / ([\d.]+) ms", "fault timer")
    F["timer_ms"] = (f(m, 1), f(m, 2), f(m, 3))
    F["vin_uf"] = f(need(t, r"VIN_RAW and TRK_OUT hold ([\d.]+) uF nominal", "VIN_RAW capacitance"))
    m = need(t, r"86\.5 W at VBUS20: VIN_RAW ([\d.]+) V nominal \(([\d.]+) V to ([\d.]+) V\)", "solar settle")
    F["settle_865"] = (f(m, 1), f(m, 2), f(m, 3))
    F["eff_floor_9v"] = f(need(t, r"it reaches 4\.80 A only if the front end's efficiency at 9 V falls to ([\d.]+)", "9 V efficiency floor"))
    m = need(t, r"at most ([\d.]+) A in\s+board current, ([\d.]+) A through R11", "pin path")
    F["pin_path"] = f(m, 2)
    F["pin_err_allow"] = f(need(t, r"pin's error at 10 mOhm is at most ([\d.]+) A in that band", "V-A07 allowance"))
    ms = list(re.finditer(r"H3\s+taken\s+([\d.]+) to\s+([\d.]+) Wh a day, given up\s+([\d.]+) to\s+([\d.]+) Wh; A2 unserved ([\d.]+) to ([\d.]+) Wh \(48 h\), ([\d.]+) to ([\d.]+) Wh \(72 h\)", t))
    if len(ms) != 2:
        refuse(3, "H3's two energy rows")
    F["h3_cand_given"] = (f(ms[1], 3), f(ms[1], 4))
    F["h3_cand_a2"] = (f(ms[1], 5), f(ms[1], 6), f(ms[1], 7), f(ms[1], 8))
    F["fwa16"] = tuple(float(x) for x in need(t, r"its own figures ([\d.]+) / ([\d.]+) / ([\d.]+) A at 9 / 12 / 24 V", "FW-A16 figures").groups())

    t = T["l4e6"]
    m = need(t, r"HoJLR2512-3W-12mR-1%\s+C2904242: peak ([\d.]+) / ([\d.]+) / ([\d.]+) A, valley ([\d.]+) / ([\d.]+) / ([\d.]+) A; service \+([\d.]+)", "R12 row")
    F["r12_peak"], F["r12_valley"], F["r12_service"] = (f(m, 1), f(m, 2), f(m, 3)), (f(m, 4), f(m, 5), f(m, 6)), f(m, 7)
    F["svc_peak"] = f(need(t, r"H3's highest boost peak ([\d.]+) A", "service peak"))
    sec = t[t.find("R11 8 mOhm, 7.262 A:\n      9.0 V"):]
    m = need(sec, r"9\.0 V \(boost, set by the cycle-by-cycle limit\): L1 ([\d.]+) A average.*?output ([\d.]+) A", "9 V closure", re.S)
    F["fe_in_9v"], F["fe_out_9v"] = f(m, 1), f(m, 2)
    m = need(sec, r"15\.1 V \(boost, set by the average limit\): L1 ([\d.]+) A average", "15.1 V closure")
    F["fe_in_151"] = f(m)
    m = need(sec, r"B-1: the peak bound over 9 to 36 V ([\d.]+) A \(at ([\d.]+) V\), ([\d.]+) % of the typical ([\d.]+) A", "B-1")
    F["l1_peak"], F["l1_pct"], F["l1_isat"] = f(m, 1), f(m, 3), f(m, 4)
    F["l1_need"] = f(need(sec, r"Isat there is at least [\d.]+ % of its 25 C value, ([\d.]+) A", "C-5 need"))
    F["l1_qual"] = f(need(sec, r"the qualifying temperature is (\d+) C", "qualifying temperature"))
    F["fet_tj"] = f(need(sec, r"B-2: every FET at most (\d+) C: MET on the ASSUMED RthetaJA", "B-2"))
    F["avg_from"] = f(need(sec, r"above ([\d.]+) V the average limit, not the peak limit, sets the fault current", "average limit onset"))
    F["vbus_max_r11"] = f(need(t, r"VBUS20 at ([\d.]+) V, efficiency ([\d.]+) DECLARED", "r11_dep bus"))
    F["eta_fe"] = f(need(t, r"VBUS20 at [\d.]+ V, efficiency ([\d.]+) DECLARED", "front end efficiency"))

    t = T["l4e7r"]      # L4-E7R's selected solution, (C) at R66 8.25k and RIMON_IN 30k
    need(t, r"the selected solution is \(C\) at R66 8\.25k and RIMON_IN 30k", "L4-E7R's selected solution")
    m = need(t, r"regulation at RIMON_IN 30k, ([\d.]+) A nominal and ([\d.]+) A at its highest on the\s+hold's corners \(([\d.]+) W at the nominal hold, ([\d.]+) W at most there\)", "L4-E7R's regulation")
    F["reg"], F["reg_w"] = (f(m, 1), f(m, 2)), (f(m, 3), f(m, 4))
    m = need(t, r"the backstop's static bound, ([\d.]+) W \(CONDITIONAL on G_CM and the VIN\+ bias, break-evens\s+above\), with the regulation's own 25 V corner at ([\d.]+) W", "the static bound")
    F["static_bound"], F["reg_corner"] = f(m, 1), f(m, 2)
    F["isc_hot_tol"] = f(need(t, r"is ([\d.]+) A\s+with the sheet's power tolerance \(still under J_SOLAR's nearest stated [\d.]+ A\)", "the hot short circuit with tolerance"))
    m = need(t, r"against ([\d.]+) to ([\d.]+) A at 25 V, at commissioning", "the backstop's trip window")
    F["bs_trip"] = (f(m, 1), f(m, 2))
    F["bs_allow_ms"] = f(need(t, r"at most 10 J in any 0\.1 s for a response up to ([\d.]+) ms", "the dynamic allowance"))
    F["swen_v"] = f(need(t, r"Below ([\d.]+) V on\s+TRK_LDO33 SWEN cannot reach", "SWEN off by default"))
    F["u5_diff"] = f(need(t, r"U5's sense differential, the rating that bounded the second round: at most ([\d.]+) V", "U5's differential"))
    F["u5_diff_lim"] = f(need(t, r"CS114, against ([\d.]+) V \(8705af p\.2\)", "U5's differential limit"))
    m = need(t, r"THE ENERGY: on SC-37's day ([\d.]+) / ([\d.]+) / ([\d.]+) Wh at the lower, nominal and upper hold corners", "L4-E7R's energy")
    F["e7r_day"] = (f(m, 1), f(m, 2), f(m, 3))
    F["e7r_bright"] = f(need(t, r"on the\s+bright day ([\d.]+) Wh \(\d+ h bound\)", "the bright day"))
    m = need(t, r"costs ([\d.]+) Wh on SC-37's day and\s+([\d.]+) Wh on the bright day", "the bank's conduction")
    F["bank_wh"] = (f(m, 1), f(m, 2))
    F["cs101_bank_a"] = f(need(t, r"the injected current crosses the bank, ([\d.]+) A rms at most", "CS101 through the bank"))
    F["cs101_pv"] = f(need(t, r"under CS101 the input reaches ([\d.]+) V at most", "CS101 at the panel input"))
    F["trk_vs_max"] = f(need(t, r"TRK_VS ([\d.]+) V against the bulk's 50 V", "TRK_VS at its worst"))
    m = need(t, r"PV_P ([\d.]+) V against U18's VIN\+ and V\+ (\d+) V", "PV_P at its worst")
    F["pv_p_max"], F["u18_vin"] = f(m, 1), f(m, 2)
    F["backstop_edits"] = int(need(t, r"apply_gen_sch_e_backstop\.py, (\d+) edit\(s\)", "the backstop draft").group(1))
    m = need(t, r"EA3 at its typical 90 V/V:\s+([\d.]+) / ([\d.]+) / ([\d.]+) V", "hold band")
    F["hold"] = (f(m, 1), f(m, 2), f(m, 3))
    m = re.search(r"(16\.41\d+) .*?(18\.81\d+)", t)
    if not m:
        refuse(3, "the conditioned hold envelope")
    F["hold_cond"] = (f(m, 1), f(m, 2))
    F["u5_tj"] = f(need(t, r"TJ estimated about ([\d.]+) C \(INFERRED\)", "U5 junction"))
    m = need(t, r"NEW nominal \(hold 17\.593 V, limit 3\.471 A\), A1: ([\d.]+) Wh a day; first interruption h (\d+)/(\d+); unserved ([\d.]+) / ([\d.]+) at 48 h, ([\d.]+) / ([\d.]+) at 72 h; least addition \+([\d.]+) / \+([\d.]+) Wh", "A1 nominal")
    F["a1_cand"] = tuple(f(m, i) for i in range(1, 10))
    m = need(t, r"NEW nominal \(hold 17\.593 V, limit 3\.471 A\), A2: ([\d.]+) Wh a day; first interruption h (\d+)/(\d+); unserved ([\d.]+) / ([\d.]+) at 48 h, ([\d.]+) / ([\d.]+) at 72 h; least addition \+([\d.]+) / \+([\d.]+) Wh", "A2 nominal")
    F["a2_cand"] = tuple(f(m, i) for i in range(1, 10))

    t = T["l4e8"]
    m = need(t, r"R11 8 mOhm, 7\.262 A: every can at most ([\d.]+) A against ([\d.]+) A \(meets\)", "bank 8 mOhm")
    F["can8"] = (f(m, 1), f(m, 2))
    m = need(t, r"R11 7 mOhm, 8\.300 A: every can at most ([\d.]+) A against ([\d.]+) A \(meets\)", "bank 7 mOhm")
    F["can7"] = (f(m, 1), f(m, 2))
    need(t, r"CHOSEN: six EEHZK1V331P as drawn, each in series with a 45 mOhm 1 % 2512 ballast, Milliohm HoJLR2512-3W-45mR-1%, LCSC C2903491", "ballast")
    F["ballast_w"] = f(need(t, r"Upper\s+sum at the bound's worst corner ([\d.]+) W", "ballast energy term"))
    F["ballast_nom_w"] = f(need(t, r"fch 400 kHz: ([\d.]+) W\s+\(not a measurement\)\. Not to be counted twice once a measured converter efficiency includes it", "the ballast at nominal parts"))
    need(t, r"CHOSEN: Cc2 3\.3n \(C1613", "Cc2")

    t = T["replay"]
    m = need(t, r"A1 D-06's 4S3P: usable ([\d.]+) Wh at \+20 C, ([\d.]+) Wh at -10 C: ([\d.]+) h and ([\d.]+) h", "A1 battery-only")
    F["a1_bat"] = tuple(f(m, i) for i in range(1, 5))
    m = need(t, r"A2 base 4S6P \+ lid 4S9P: usable ([\d.]+) Wh at \+20 C, ([\d.]+) Wh at -10 C: ([\d.]+) h and ([\d.]+) h", "A2 battery-only")
    F["a2_bat"] = tuple(f(m, i) for i in range(1, 5))
    m = need(t, r"against 48 h: A1 short by ([\d.]+) h .*?, A2 short by ([\d.]+) h .*?; against 72 h: A1 ([\d.]+) h .*?,\n\s+A2 ([\d.]+) h", "shortfalls", re.S)
    F["short"] = tuple(f(m, i) for i in range(1, 5))
    m = need(t, r"A1   CORRECTED, HYPOTHETICAL, WE\s+48 h TYP: pack \S+;\s+\+([\d.]+) Wh", "A1 screening 48 h")
    m2 = need(t, r"A1   CORRECTED, HYPOTHETICAL, WE\s+72 h TYP: pack \S+;\s+\+([\d.]+) Wh", "A1 screening 72 h")
    F["a1_scr_add"] = (f(m), f(m2))
    m = need(t, r"A2   CORRECTED, HYPOTHETICAL, WE\s+48 h TYP: lid \S+;\s+\+([\d.]+) Wh", "A2 screening 48 h")
    m2 = need(t, r"A2   CORRECTED, HYPOTHETICAL, WE\s+72 h TYP: lid \S+;\s+\+([\d.]+) Wh", "A2 screening 72 h")
    F["a2_scr_add"] = (f(m), f(m2))
    blk = t[t.find("A1 D-06's 4S3P             CORRECTED, HYPOTHETICAL, WE"):]
    m = need(blk, r"TYP from 06 UTC: first interruption h\s+(\d+) \((\d+) UTC\); unserved\s+([\d.]+) Wh at 48 h,\s+([\d.]+) Wh at 72 h", "A1 screening 06")
    m2 = need(blk, r"TYP from 18 UTC: first interruption h\s+(\d+) \((\d+) UTC\); unserved\s+([\d.]+) Wh at 48 h,\s+([\d.]+) Wh at 72 h", "A1 screening 18")
    F["a1_scr"] = (f(m, 1), f(m2, 1), f(m, 3), f(m2, 3), f(m, 4), f(m2, 4))
    blk = t[t.find("A2 base 4S6P + lid 4S9P    CORRECTED, HYPOTHETICAL, WE"):]
    m = need(blk, r"TYP from 06 UTC: first interruption h\s+(\d+) \((\d+) UTC\); unserved\s+([\d.]+) Wh at 48 h,\s+([\d.]+) Wh at 72 h", "A2 screening 06")
    m2 = need(blk, r"TYP from 18 UTC: first interruption h\s+(\d+) \((\d+) UTC\); unserved\s+([\d.]+) Wh at 48 h,\s+([\d.]+) Wh at 72 h", "A2 screening 18")
    F["a2_scr"] = (f(m, 1), f(m2, 1), f(m, 3), f(m2, 3), f(m, 4), f(m2, 4))
    m = need(t, r"CORRECTED, O-2 nominal\s+A2 48 h ([\d.]+) W, 72 h ([\d.]+) W; A1 48 h ([\d.]+) W, 72 h ([\d.]+) W", "steady loads")
    F["steady"] = tuple(f(m, i) for i in range(1, 5))
    F["bus_low"] = f(need(t, r"CORRECTED  HYPOTHETICAL, ENERGY-BASIS 6c's WE: bus ([\d.]+) V", "lowest bus"))
    F["eta_u3"] = f(need(t, r"U3's limit [\d.]+ A, U3 ([\d.]+),", "U3 efficiency"))
    F["cand_voc_cold"] = f(need(t, r"the NOMINAL open circuit is ([\d.]+) V there", "candidate cold Voc"))
    F["cand_isc_hot"] = f(need(t, r"its hot short-circuit current about ([\d.]+) A", "candidate hot Isc"))
    F["cand_day"] = f(need(t, r"nominal hold\s+17\.593 V, limit nominal\s+([\d.]+) Wh", "candidate day"))

    t = T["l4e10"]      # L4-E10's final record (FEA-008 not closed; the recommendation and the conditioned corner)
    need(t, r"Closable now: none\.", "FEA-008 not closed")
    need(t, r"route CONDITIONAL: \(II\) RECOMMENDED: a wide-temperature 18650 \(the HL18650V class\)", "L4-E10's recommendation")
    F["th1"] = f(need(t, r"T-H1 must read at least ([\d.]+) W/K with the fans, lid closed AND lid open", "T-H1's floor"))
    m = need(t, r"at this corner the uncooled air settles at ([\d.]+) C in E3-O and tends to ([\d.]+) C in E5's 60 C dwell, at or past the \+(\d+) C", "the conditioned corner")
    F["corner_air"], F["parts_hot"] = (f(m, 1), f(m, 2)), f(m, 3)
    F["e3o_amb"] = f(need(t, r"ambient \+(\d+) C; duration 4 h; configuration deployed, monitor and radios on", "E3-O's ambient"))
    m = need(t, r"35E\s+([\d.]+) Wh usable, ([\d.]+) h battery-only", "the 35E's usable energy")
    m2 = need(t, r"HL18650V\s+([\d.]+) Wh usable, ([\d.]+) h battery-only \((-[\d.]+) % against S1\)", "the HL18650V's usable energy")
    F["cell_usable"], F["cell_hours"], F["cell_less_pct"] = (f(m, 1), f(m2, 1)), (f(m, 2), f(m2, 2)), -f(m2, 3)
    m = need(t, r"([\d.]+) Wh nominal against ([\d.]+)", "the nominal energy")
    F["cell_nom"] = (f(m, 2), f(m, 1))
    F["corner_heat"] = (F["corner_air"][0] - F["e3o_amb"]) * F["th1"]
    m = need(t, r"LO-01e ([\d.]+) C: ([\d.]+), ([\d.]+) and ([\d.]+) K;", "LO-01e's margins")
    F["lo01e"] = (f(m, 1), f(m, 2), f(m, 3), f(m, 4))
    F["cell_usd"] = f(need(t, r"USD ([\d.]+) \(a marketplace seller, not the maker", "the cell's price"))

    t = T["s120"]
    m = need(t, r"with 100 ppm/K over 65 K \(INFERRED\).*?\s+([\d.]+) to ([\d.]+) V\s+<- the DC band", "VBUS20 DC band")
    F["vbus_band"] = (f(m, 1), f(m, 2))
    F["vbus_bound"] = f(need(t, r"BOUND, INFERRED\s+([\d.]+) V", "VBUS20 bound"))
    m = need(t, r"opens its pass FET at OVLO ([\d.]+) / ([\d.]+) / ([\d.]+) V \(OVLOTH ([\d.]+) / ([\d.]+) / ([\d.]+) V", "OVLO")
    F["ovlo"] = (f(m, 1), f(m, 2), f(m, 3))
    th = (f(m, 4), f(m, 5), f(m, 6))
    r22 = float(re.match(r"([\d.]+)k", Gen(T["gen_e"]).value("R22")).group(1))
    # the selected band: R23 at E192's 6.42k with R22 and R23 both 0.1 % (SESSION, part A's CS101 finding; register R-94)
    F["ovlo_sel"] = (th[0] * (1 + r22 * 0.999 / (R23_NEW_K * 1.001)), th[1] * (1 + r22 / R23_NEW_K), th[2] * (1 + r22 * 1.001 / (R23_NEW_K * 0.999)))
    F["chg_v_max"] = f(need(t, r"ChargeVoltage 16\.8 V \+ 0\.5 % = ([\d.]+) V", "ChargeVoltage maximum"))
    F["batovp"] = f(need(t, r"BATOVP at most 105 % = ([\d.]+) V", "BATOVP"))
    F["u3_rec_vbus"] = f(need(t, r"U3 VBUS, ACP, ACN \((\d+) V recommended", "U3 recommended"))
    F["acov_min"] = f(need(t, r"U3 ACOV rising minimum \(([\d.]+) V", "ACOV"))

    t = T["budget"]
    m = need(t, r"^PS-IDLE-SPEC load\s+([\d.]+) \| battery\s+([\d.]+) /\s+([\d.]+) /\s+([\d.]+)", "IDLE-SPEC")
    F["idle"] = (f(m, 2), f(m, 3), f(m, 4))
    m = need(t, r"^PS-ALLTX\s+load\s+([\d.]+) \| battery\s+([\d.]+) /\s+([\d.]+) /\s+([\d.]+)", "ALLTX")
    F["alltx"] = (f(m, 2), f(m, 3), f(m, 4))
    m = need(t, r'^PS-IDLE-SPEC \{"battery_W_plan": [\d.]+, .*?"I_plan": \{"16\.8": ([\d.]+), "14\.4": ([\d.]+), "12\.0": ([\d.]+), "10\.0": ([\d.]+)\}', "IDLE-SPEC currents")
    F["idle_i"] = tuple(f(m, i) for i in range(1, 5))
    m = need(t, r'^PA keyed alone over PS-IDLE-SPEC, PA at 113 W \{"battery_W_plan": ([\d.]+), .*?"I_plan": \{"16\.8": ([\d.]+), "14\.4": ([\d.]+), "12\.0": ([\d.]+), "10\.0": ([\d.]+)\}', "PA keyed 113 W")
    F["pa113"] = tuple(f(m, i) for i in range(1, 6))
    m = need(t, r'^PS-TYP plus USB-C \{"battery_W_plan": ([\d.]+), "battery_W_high": ([\d.]+), "outside_W": ([\d.]+), .*?"I_plan": \{"16\.8": ([\d.]+), "14\.4": ([\d.]+)', "TYP plus USB-C")
    F["typ_usbc"] = tuple(f(m, i) for i in range(1, 6))
    m = need(t, r'^PS-TYP plus PoE \{"battery_W_plan": ([\d.]+), "battery_W_high": ([\d.]+), "outside_W": ([\d.]+)', "TYP plus PoE")
    F["typ_poe"] = tuple(f(m, i) for i in range(1, 4))
    m = need(t, r'^ALLTX plan \{"battery_W": ([\d.]+), "vbat_W": ([\d.]+), "V_vbat_at_18A": ([\d.]+), "V_stack_at_18A": ([\d.]+)', "D-11 basis")
    F["alltx_18a_stack"] = f(m, 4)
    line = need(t, r'^ALLTX plan \{.*$', "D-11 line").group(0)
    F["alltx_rest_need"] = max(float(x) for x in re.findall(r'"V_rest_pack": ([\d.]+)', line))
    F["alltx_20a_stack"] = f(need(line, r'"V_stack_at_I": \{[^}]*"20\.0": ([\d.]+)', "the 20 A stack"))
    F["d11_floor"] = f(need(T["hwfw"], r"SoC floors ([\d.]+) V and ([\d.]+) V rest", "D-11 floors"))
    F["pa_floor"] = f(need(T["hwfw"], r"SoC floors [\d.]+ V and ([\d.]+) V rest", "PA floor"))
    t = T["trace"]
    m = need(t, r"PLAN by tier, W:\s+S ([\d.]+), R ([\d.]+), D ([\d.]+), T ([\d.]+)", "tiers")
    F["undoc_w"] = f(m, 4)

    yaml.safe_load(T["packprot"])        # it parses (a malformed file refuses here)
    txt = T["packprot"]
    F["pp_cont"] = f(need(txt, r"declared_continuous_a: ([\d.]+)", "declared continuous"))
    F["pp_peak"] = f(need(txt, r"declared_peak_a: ([\d.]+)", "declared peak"))
    m = need(txt, r"prospective_fault_a: \{low: ([\d.]+), high: ([\d.]+)\}", "prospective fault")
    F["pp_fault"] = (f(m, 1), f(m, 2))
    F["ocd1"] = (f(need(txt, r"threshold: \{value: (20\.0), unit: A, per: pack, delay_s: (2\.0)\}", "OCD1")), 2.0)
    F["occ"] = f(need(txt, r"threshold: \{value: (5\.0), unit: A, per: pack, delay_s: 2\.0\}", "OCC"))
    F["scd"] = f(need(txt, r"threshold: \{value: (60\.0), unit: A, per: pack, delay_s: 0\.0002\}", "SCD"))
    F["cuv"] = f(need(txt, r"threshold: \{value: (2\.50), unit: V, per: cell", "CUV"))
    F["cov"] = f(need(txt, r"threshold: \{value: (4\.25), unit: V, per: cell", "COV"))
    F["cell_chg_ma"] = f(need(txt, r"max_charge_current_ma:\s+\{value: (\d+)", "cell charge maximum"))
    F["cell_dis_ma"] = f(need(txt, r"max_continuous_discharge_ma: \{value: (\d+)", "cell discharge maximum"))
    env = T["envelope"]
    m = need(env, r"worst_inside_air_c: \{lid_open: ([\d.]+), lid_closed: ([\d.]+)", "worst inside air")
    F["air"] = (f(m, 1), f(m, 2))
    hw = T["hwfw"]
    F["chg_set"] = f(need(hw, r"ChargeCurrent at most ([\d.]+) A \(the nearest code at or below\)", "FW-A02"))
    F["ina_fs_contract"] = f(need(hw, r"full scale (81\.92) mV over the shunt", "FW-A09 full scale"))
    m = need(T["dec31"], r"moves DC_F ([\d.]+) V at 8 kV and ([\d.]+) V at 15 kV", "E-F1's bound")
    F["ef1_dv"] = (f(m, 1), f(m, 2))
    m = need(T["dec31"], r"moves it 0\.06 V at\s+8 kV and ([\d.]+) V at 15 kV", "VIN_RAW's discharge bound")
    F["vinraw_esd_dv"] = f(m)
    ifc = T["ifaces"]
    m = need(ifc, r"Lapp OLFLEX ROBUST 210 (\d+) x ([\d.]+) or Alpha Wire 25064, (\d+) m", "the external DC cable")
    F["cable_mm2"], F["cable_m"] = f(m, 2), f(m, 3)
    m = need(ifc, r'harness: "inside: (\d+) AWG, (\d+) mm, VH crimp at E', "the inside DC lead")
    F["lead_awg"], F["lead_mm"] = f(m, 1), f(m, 2)
    m = need(ifc, r"([\d.]+) A per pin with four sharing,\s+([\d.]+) A with one open", "pack pins")
    F["pack_pin_share"] = (f(m, 1), f(m, 2))
    return F, where


# ----------------------------------------------------------------------------------------------- the derived figures
def derived(F):
    D = {}
    vrev = F["vin_raw_e"]["v_work"]                                   # REQ-015's 36 V as board E declares VIN_RAW's work voltage
    D["vrev"] = vrev
    D["dcp_backfeed"] = F["trk_ceiling"][2] - VF_BACKFEED              # TRK_OUT's raised ceiling, through U4/Q2, L2 and Q7's body diode
    D["dcp_backfeed_drawn"] = F["trk_drawn"][2] - VF_BACKFEED
    D["q1_rev"] = D["dcp_backfeed"] + vrev
    D["q1_rev_drawn"] = D["dcp_backfeed_drawn"] + vrev
    # F1's bound: the kit's own cable (the external pair and the inside lead), copper alone, at REQ-024's cold end
    r20 = 2 * F["cable_m"] * CU_RHO_20C / F["cable_mm2"] + 2 * (F["lead_mm"] / 1000.0) * CU_RHO_20C / AWG18_MM2
    rc = r20 * (1 + CU_ALPHA * (T_COLD - 20.0))
    D["f1_v"] = F["ovlo_sel"][2]       # the highest steady input the selected entry admits (R23 6.42k, 0.1 %)
    D["f1_r20"], D["f1_rcold"] = r20, rc
    D["f1_ipf"] = D["f1_v"] / rc
    # the front end's VIN_RAW current at the onset of the average limit (L4-E6's boundary), the largest over 9 to 36 V
    D["vin_fault"] = F["r11_8"][2] * F["vbus_max_r11"] / (F["eta_fe"] * F["avg_from"])
    D["vin_fault_7"] = F["r11_7"][2] * F["vbus_max_r11"] / (F["eta_fe"] * F["avg_from"])
    # solar at the window: the tracker's output current at H3's lowest settle point
    D["trk_out_w"] = 100.0 * F["trk"]["efficiency"]
    D["trk_i_settle"] = D["trk_out_w"] / F["settle_865"][1]
    # U3's delivered power at VBAT
    D["vbat_avail_min"] = F["u3_min"] * F["bus_low"] * F["eta_u3"]
    D["vbat_avail_max"] = F["u3_max_board"] * F["vbus_band"][1] * F["eta_u3"]
    D["vbat_win"] = F["win_w"] * F["eta_u3"]
    D["vbat_at_9"] = (F["u3_at_9"] * F["bus_low"] * F["eta_u3"], F["h3"][9.0][0] * F["vbus_band"][1] * F["eta_u3"])
    D["vbat_at_12"] = F["h3"][12.0][0] * F["vbus_band"][1] * F["eta_u3"]
    D["vbat_at_24"] = F["h3"][24.0][0] * F["vbus_band"][1] * F["eta_u3"]
    D["entry_9v_vbat"] = F["entry_lim"][0] * 9.0 * F["eta_fe"] * F["eta_u3"]
    # the pack opening while charging: L2's energy at the converter's stop (SYSOVP maximum) into VBAT's capacitance
    l2 = 4.7e-6 * (1 + L2_TOL)
    p_in = F["u3_max_board"] * F["vbus_band"][1]
    i_out = p_in / F["batovp"]
    fsw_min = 340e3                                              # SLUSE66A 8.5 FSW at the 400 kHz setting, its minimum (FW-A17, V-A05)
    lmin = 4.7e-6 * (1 - L2_TOL)
    d = F["batovp"] / F["vbus_band"][1]
    ripple = (F["vbus_band"][1] - F["batovp"]) * d / (lmin * fsw_min)
    i_pk = i_out + ripple / 2.0
    e = 0.5 * l2 * i_pk ** 2
    n, cnom = F["vbat_caps"]
    ceff = cnom * BIAS_KEEP * 1e-6
    v0 = F["sysovp"][2]
    D["pack_open"] = {"i_pk": i_pk, "e_mj": e * 1e3, "c_nom_uf": cnom, "n": n, "c_eff_uf": ceff * 1e6,
                      "v_end": math.sqrt(v0 ** 2 + 2 * e / ceff), "c_need_uf": 2 * e / (F["tps2596_abs"] ** 2 - v0 ** 2) * 1e6}
    D["pack_open"]["keep_need"] = D["pack_open"]["c_need_uf"] / cnom
    # HF-F02's resolution: the PoE stage's input current at the pack's lowest stack (CUV), the shunt that keeps the INA226 in range
    vlow = 4 * F["cuv"]
    i_in = F["poe"]["peak"] * F["poe"]["volts"] / (F["poe"]["efficiency"] * vlow)
    D["poe_in"] = i_in
    D["poe_shunt_max_mohm"] = F["ina_fs_mv"] / i_in
    D["poe_shunt_mv"] = 5.0 * i_in     # R227 5 mOhm (part A)
    D["vbat_low"] = vlow
    return D


# ------------------------------------------------------------------------------------------- part A: Q1, F1 and U17
def partA(F, D, T):
    """The three datasheet-backed proposals. Every figure is read from the makers' sheets (pinned) or the records'
    outputs, except the constants named at the top (figure readings and two assumptions)."""
    A = {}
    flat = lambda t: re.sub(r"\s+", " ", t)
    # ---- the makers' rows
    c1 = flat(subprocess.run(["pdftotext", "-f", "1", "-l", "1", os.path.join(TOP, PINS["csd19532"][0]), "-"], capture_output=True).stdout.decode())
    m = need(c1, r"Gate-to-Source Voltage ±(\d+) V", "CSD19532Q5B VGS")
    A["vgs_max"] = f(m)
    m = need(c1, r"Continuous Drain Current (\d+) Pulsed Drain Current\(2\) (\d+) Power Dissipation\(1\) ([\d.]+)", "CSD19532Q5B ID, IDM, PD")
    A["id_cont"], A["idm"], A["pd"] = f(m, 1), f(m, 2), f(m, 3)
    A["tj_max"] = f(need(c1, r"Storage Temperature Range .55 to (\d+)", "CSD19532Q5B TJ"))
    A["eas"] = f(need(c1, r"ID = 74 A, L = 0\.1 mH, RG = 25 [\u2126\u03a9] (\d+) mJ", "CSD19532Q5B EAS"))
    c3 = pdf_text("csd19532", 3)
    m = need(c3, r"VGS\(th\)\s+Gate-to-Source Threshold Voltage\s+VDS = VGS, ID = 250 μA\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "CSD19532Q5B Vth")
    A["vth"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(c3, r"VGS = 10 V, ID = 17 A\s+([\d.]+)\s+([\d.]+)\s+m[\u2126\u03a9]", "CSD19532Q5B RDS(on) at 10 V")
    A["rds10"] = (f(m, 1), f(m, 2))
    m = need(c3, r"ISD = 17 A, VGS = 0 V\s+([\d.]+)\s+([\d.]+)\s+V", "CSD19532Q5B VSD")
    A["vsd_max"] = f(m, 2)
    A["rja"] = f(need(c3, r"Junction-to-Ambient Thermal Resistance \(1\) \(2\)\s+(\d+)", "CSD19532Q5B RthetaJA max"))
    m = need(c3, r"Gate Charge Total \(10 V\)\s+([\d.]+)\s+([\d.]+)\s+nC", "CSD19532Q5B Qg")
    A["qg_max"] = f(m, 2)
    l7 = pdf_text("lm74700")
    m = need(l7, r"Charge pump turn on voltage\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "LM74700 charge pump on")
    A["cp_on_min"] = f(m, 1)
    m = need(l7, r"Charge pump turn off voltage\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "LM74700 charge pump off")
    A["cp_off_max"] = f(m, 3)
    A["gate_src_min_ma"] = f(need(l7, r"Peak source current\s+(\d+)\s+\d+\s+mA", "LM74700 peak gate source current"))
    m = need(l7, r"ENTDLY\s+V\(VCAP\) > V\(VCAP UVLOR\)\s+(\d+)\s+(\d+)\s+µs", "LM74700 ENTDLY")
    A["entdly_max_us"] = f(m, 2)
    m = need(l7, r"tReverse delay\s+([\d.]+)\s+([\d.]+)\s+µs", "LM74700 reverse turn-off")
    A["trev_max_us"] = f(m, 2)
    need(l7, r"MOSFET with 15-V minimum VGS should be selected", "LM74700 VGS guidance")
    A["gate_rec"] = 15.0
    need(l7, r"gate threshold voltage Vth of 2-V to 2\.5-V", "LM74700 Vth guidance")
    A["vth_rec_max"] = 2.5
    need(l7, r"\(20 mV / ILoad\(Nominal\)\) ≤ RDS\(ON\) ≤ \( 50 mV / ILoad\(Nominal\)\)", "LM74700 RDS guidance")
    A["rds_guide_mv"] = (20.0, 50.0)
    l69 = pdf_text("lm5069")
    m = need(l69, r"PWRLIM-1\s+Power limit sense voltage\s+SENSE-OUT = 48 V, RPWR = 150 k[\u2126\u03a9]\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM5069 PWRLIM-1")
    A["pwrlim"] = (f(m, 1), f(m, 2), f(m, 3))
    need(l69, r"R PWR\s+1\.30 u 10 5 u R SNS \(PLIM 1\.18mV u", "LM5069 Equation 9")
    A["eq9"] = (1.30e5, 1.18e-3)
    m = need(l69, r"VCB\s+Threshold voltage\s+VIN to SENSE\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM5069 VCB")
    A["vcb_max"] = f(m, 3)
    A["tcb_max"] = f(need(l69, r"tCB\s+Response time\s+[\d.]+\s+([\d.]+)\s+µs", "LM5069 tCB"))
    A["ovlo_del_us"] = f(need(l69, r"OVLODEL\s+OVLO delay\s+Delay to GATE low\s+(\d+)", "LM5069 OVLO delay"), 1) if re.search(r"OVLODEL\s+OVLO delay\s+Delay to GATE low\s+(\d+)", l69) else \
        f(need(l69, r"Delay to GATE high\s+\d+\s+µs\s+OVLODEL\s+OVLO delay\s+Delay to GATE low\s+(\d+)", "LM5069 OVLO delay"))
    A["restart_duty"] = f(need(l69, r"DCFAULT\s+Fault restart duty cycle\s+LM5069-2 only\s+([\d.]+)%", "LM5069 restart duty")) / 100.0
    gE = Gen(T["gen_e"])
    A["rpwr"] = float(re.match(r"([\d.]+)k", gE.value("R24")).group(1)) * 1e3
    A["rs"] = float(re.match(r"([\d.]+)mOhm", gE.value("R19")).group(1)) * 1e-3
    fz = pdf_text("fuse997")
    A["f_v"] = f(need(fz, r"Voltage Rating:\s+(\d+) V DC", "0997 voltage rating"))
    A["f_int"] = f(need(fz, r"Interrupting Rating:\s+(\d+) A @ 58 V DC", "0997 interrupting rating"))
    need(fz, r"Same blade size and pitch as", "0997 blade size")
    m = need(fz, r"0997010_\s+10\s+1\s+(\d+)\s+([\d.]+)\s+(\d+)", "0997 10 A row")
    A["f_r_cold_mohm"], A["f_i2t"] = f(m, 2), f(m, 3)
    amb = [float(x) for x in re.findall(r"(-?\d+) °C", need(fz, r"(-40 °C\s+-20 °C\s+0 °C\s+20 °C\s+40 °C\s+60 °C\s+80 °C\s+100 °C)", "0997 derating columns").group(1))]
    row = [float(x) for x in need(fz, r"\n\s+10A\s+((?:[\d.]+\s+){7}[\d.]+)", "0997 10 A derating row").group(1).split()]
    A["f_amb"], A["f_der"] = amb, row
    tc = {}
    for pct in (110, 135, 200, 350, 600):
        mm = re.search(r"^\s*%d\s+(\d+(?:\.\d+)?(?: \d{3})?)\s*/\s*(\d+(?:\.\d+)?|-)\s*$" % pct, fz, re.M)
        if not mm:
            refuse(3, "0997 time-current row %d %%" % pct)
        tc[pct] = (float(mm.group(1).replace(" ", "")), None if mm.group(2) == "-" else float(mm.group(2)))
    A["f_tc"] = tc
    ks = flat(subprocess.run(["pdftotext", "-raw", os.path.join(TOP, PINS["keystone"][0]), "-"], capture_output=True).stdout.decode())
    need(ks, r"CAT\. NO\. 3568", "Keystone 3568")
    need(ks, r"For Littelfuse Mini 297 or 997 series/Bussmann ATM series or equivalent", "Keystone MINI holder text")
    ina = pdf_text("ina226")
    m = need(ina, r"Shunt offset voltage, RTI\(2\)\s+±([\d.]+)\s+±([\d.]+)\s+μV", "INA226 VOS")
    A["ina_vos_uv"] = f(m, 2)
    m = need(ina, r"Shunt voltage gain error\s+([\d.]+)%\s+([\d.]+)%", "INA226 gain error")
    A["ina_gain"] = f(m, 2) / 100.0
    need(ina, r"the bus voltage can be present with the supply\s+voltage off", "INA226 supply independence")
    need(ina, r"0\.00512", "INA226 Equation 1")
    A["ina_cal_k"] = 0.00512
    tv = flat(subprocess.run(["pdftotext", "-raw", os.path.join(TOP, PINS["smcj"][0]), "-"], capture_output=True).stdout.decode())
    m = need(tv, r"VBR @ TJ ?= VBR ?@25°C x \(1\+αT x \(TJ - 25\)\) \(αT:Temperature Coefficient, typical value is ([\d.]+)%\)", "SMCJ VBR temperature coefficient")
    A["tvs_alpha"] = f(m) / 100.0
    m = need(pdf_text("lm5176"), r"VCS\(BUCK\)\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM5176 VCS(BUCK)")
    A["vcs_buck_max"] = f(m, 3) * 1e-3
    # ---- the records' figures used here
    s120 = T["s120"]
    m = need(s120, r"boost mode, peak limit \((\d+) \+ ([\d.]+)\) mV", "LM5176 VCS(BOOST) maximum and the CS offset")
    A["vcs_boost_max"], A["cs_off"] = f(m, 1) * 1e-3, f(m, 2) * 1e-3
    A["poe_rcs"] = float(need(T["gen_a"], r'isns="20m", rcs="(\d+)m", bias="VBAT"', "U16's CS resistor").group(1)) * 1e-3
    l8 = T["l4e8"]
    m = need(l8, r"THE BALLAST \(MAKER, the HoJLR2512 sheet p\.2\): (\d+) W, derated from (\d+) C to zero at (\d+) C", "HoJLR2512 rating")
    A["hojlr"] = (f(m, 1), f(m, 2), f(m, 3))
    m = need(T["l4e4"], r"CHOSEN: R138 5 mOhm, HoJLR2512-3W-5mR-1%, LCSC (C\d+) \(Milliohm.*?\n.*?p\.2 TCR \+-(\d+) ppm/K", "R138's part and TCR", re.S)
    A["r5_lcsc"], A["r5_tcr"] = m.group(1), f(m, 2) * 1e-6
    A["r5_span_k"] = f(need(T["l4e4"], r"-20 C to the ASSUMED 100 C \((\d+) K from 25 C\)", "the shunt's temperature span"))
    r7 = T["l4e7r"]
    m = need(r7, r"curve 2 \(sources of (\d+) V or below\): 126 dBuV, ([\d.]+)\s+V rms", "CS101 curve 2")
    A["cs101_src_v"], A["cs101_vrms"] = f(m, 1), f(m, 2)
    m = need(T["s120"], r"OVLO ([\d.]+) / ([\d.]+) / ([\d.]+) V \(OVLOTH ([\d.]+) / ([\d.]+) / ([\d.]+) V", "the OVLO band and its threshold")
    A["ovloth"] = (f(m, 4), f(m, 5), f(m, 6))
    gE2 = Gen(T["gen_e"])
    A["r22_k"] = float(re.match(r"([\d.]+)k", gE2.value("R22")).group(1))
    A["r23_k"] = float(re.match(r"([\d.]+)k", gE2.value("R23")).group(1))
    A["cs114_ma"] = f(need(r7, r"curve 4's 103 dBuA \((\d+) mA rms", "CS114 curve 4"))

    # ---- Q1
    i_hi = F["entry_lim"][1]
    A["q1_p"] = i_hi ** 2 * A["rds10"][1] * 1e-3 * CSD_RDS_NORM_150C
    A["q1_tj"] = F["air"][1] + A["q1_p"] * A["rja"]
    t_on = A["entdly_max_us"] * 1e-6 + A["qg_max"] * 1e-9 / (A["gate_src_min_ma"] * 1e-3)
    A["q1_inrush_s"], A["q1_inrush_mj"] = t_on, i_hi * A["vsd_max"] * t_on * 1e3
    A["q1_rev"] = D["q1_rev"]
    A["cs101_pk"] = A["cs101_vrms"] * math.sqrt(2)
    A["cs101_top"] = D["vrev"] + A["cs101_pk"]
    A["cs101_top_src"] = A["cs101_src_v"] + A["cs101_pk"]
    ovlo = lambda th, r23, lo, tol=0.01: th * (1 + A["r22_k"] * (1 - tol if lo else 1 + tol) / (r23 * (1 + tol if lo else 1 - tol)))
    A["ovlo_check"] = (ovlo(A["ovloth"][0], A["r23_k"], True), ovlo(A["ovloth"][2], A["r23_k"], False))
    sm = F["SMCJ40A"]["vbr_min"]
    A["r23_win"] = (A["r22_k"] * 1.01 / (0.99 * (sm / A["ovloth"][2] - 1)), A["r22_k"] * 0.99 / (1.01 * (A["cs101_top"] / A["ovloth"][0] - 1)))
    A["r23_e192"] = R23_NEW_K
    A["ovlo_e192"] = (ovlo(A["ovloth"][0], A["r23_e192"], True), ovlo(A["ovloth"][2], A["r23_e192"], False))
    A["ovlo_new"] = (ovlo(A["ovloth"][0], A["r23_e192"], True, 0.001), ovlo(A["ovloth"][2], A["r23_e192"], False, 0.001))
    A["d10_cold_vbr"] = sm * (1 + A["tvs_alpha"] * (T_COLD - 25.0))
    A["cs114_pk"] = A["cs114_ma"] * 1e-3 * math.sqrt(2) / (2 * math.pi * 10e3 * 1e-6)
    A["m7_vds"] = D["vrev"] + F["ef1_dv"][1]
    sm40 = F["SMCJ40A"]
    A["cap_neg_vds"] = D["vrev"] + sm40["vc"]
    A["cap_dcp_ld_limit"] = F["ld_ca_abs"] - sm40["vc"]
    A["cap_dcp_q1_limit"] = F["csd19532_vds"] - sm40["vc"]
    A["cap_energy_mj"] = 0.5 * F["vin_uf"] * 1e-6 * D["vrev"] ** 2 * 1e3
    plim = lambda vds: A["rpwr"] / (A["eq9"][0] * A["rs"]) + A["eq9"][1] * vds / A["rs"]
    A["plim36"], A["plim_ovlo"] = plim(D["vrev"]), plim(F["ovlo_sel"][2])
    A["plim_hi"] = A["plim_ovlo"] * PWRLIM_SPREAD
    A["soa_36_w"] = CSD_SOA_10MS_36V_A * D["vrev"]
    A["soa_hot_w"] = A["soa_36_w"] * (A["tj_max"] - SOA_TC_HOT) / (A["tj_max"] - 25.0)
    A["cb_a"] = A["vcb_max"] * 1e-3 / A["rs"]
    A["dcp_short_s"] = A["f_i2t"] / D["f1_ipf"] ** 2
    inom = F["h3"][9.0][1]
    A["rds_guide"] = (A["rds_guide_mv"][0] / inom, A["rds_guide_mv"][1] / inom)
    A["rds_at_tj"] = A["rds10"][0] * (1 + (CSD_RDS_NORM_150C - 1) * (A["q1_tj"] - 25.0) / 125.0)
    # ---- F1
    A["f1_ipf_by_v"] = [(v, v / D["f1_rcold"]) for v in (9.0, 12.0, 24.0, D["vrev"], D["f1_v"])]
    col = [x for x in A["f_amb"] if x >= F["air"][1]][0]
    A["f_col"], A["f_allow"] = col, A["f_der"][A["f_amb"].index(col)]
    A["f_startup_i2t"] = i_hi ** 2 * F["timer_ms"][2] * 1e-3
    r_hot = D["f1_r20"] * (1 + CU_ALPHA * (F["air"][1] - 20.0))
    A["f_min_fault_9v"] = 9.0 / r_hot
    # ---- U17 at the PoE stage's input on 5 mOhm (R227)
    rsh = 0.005
    A["u17_rsh"] = rsh
    A["u17_in_norm"] = D["poe_in"]
    A["u17_mv_norm"] = D["poe_in"] * rsh * 1.01 * 1e3
    A["u17_fault_a"] = (A["vcs_boost_max"] + A["cs_off"]) / (A["poe_rcs"] * 0.99)
    A["u17_mv_fault"] = A["u17_fault_a"] * rsh * 1.01 * 1e3
    A["u17_p_fault"] = A["u17_fault_a"] ** 2 * rsh * 1.01
    A["u17_buck_valley_a"] = (A["vcs_buck_max"] + A["cs_off"]) / (A["poe_rcs"] * 0.99)
    A["hojlr_avail"] = A["hojlr"][0] if F["air"][1] <= A["hojlr"][1] else A["hojlr"][0] * (A["hojlr"][2] - F["air"][1]) / (A["hojlr"][2] - A["hojlr"][1])
    A["u17_fs_a"] = F["ina_fs_mv"] * 1e-3 / rsh
    A["u17_lsb"] = A["u17_fs_a"] / 32768.0
    A["u17_cal"] = A["ina_cal_k"] / (A["u17_lsb"] * rsh)
    A["u17_err_pct"] = (A["ina_gain"] + 0.01 + A["r5_tcr"] * A["r5_span_k"]) * 100.0
    A["u17_off_ma"] = A["ina_vos_uv"] * 1e-6 / rsh * 1e3
    return A


def partA_lines(F, D, A):
    L = []
    p = L.append
    p("11. PART A: Q1, F1 AND U17 AS DATASHEET-BACKED PROPOSALS (the applicable conditions, not only the headline rating)")
    p("   Q1, board E's vehicle-entry ideal-diode FET: TI CSD19532Q5B (SLPS414B, byte-identical to ti.com on 2 October 2026), LCSC C473333")
    p("     maker's rows: VDS %s V, VGS +-%s V, ID %s A (1 in2 2 oz), IDM %s A, EAS %s mJ, TJ to %s C; RDS(on) at VGS 10 V %s / %s mOhm;"
      % (fmt(F["csd19532_vds"]), fmt(A["vgs_max"]), fmt(A["id_cont"]), fmt(A["idm"]), fmt(A["eas"]), fmt(A["tj_max"]), fmt(A["rds10"][0]), fmt(A["rds10"][1])))
    p("       Vth %s / %s / %s V; VSD at most %s V; Qg at most %s nC; RthetaJA at most %s C/W (1 in2 2 oz; board E's copper an ASSUMPTION)"
      % (fmt(A["vth"][0]), fmt(A["vth"][1]), fmt(A["vth"][2]), fmt(A["vsd_max"]), fmt(A["qg_max"]), fmt(A["rja"])))
    p("     normal: %s A (the entry's highest) at RDS(on) %s mOhm x %s (Figure 8 at 150 C, read) = %s W; TJ at most %s C in %s C air "
      "(MEETS against %s C; INFERRED)" % (fmt(F["entry_lim"][1]), fmt(A["rds10"][1]), fmt(CSD_RDS_NORM_150C), fmt(round(A["q1_p"], 3)), fmt(round(A["q1_tj"], 1)), fmt(F["air"][1]), fmt(A["tj_max"])))
    p("       ID %s A against %s A: MEETS (MAKER); at hot plug the body diode carries the hot swap's limited current for at most "
      "%s ms (ENTDLY %s us plus Qg %s nC at the controller's %s mA): %s mJ (INFERRED)"
      % (fmt(F["entry_lim"][1]), fmt(A["id_cont"]), fmt(round(A["q1_inrush_s"] * 1e3, 3)), fmt(A["entdly_max_us"]), fmt(A["qg_max"]), fmt(A["gate_src_min_ma"]), fmt(round(A["q1_inrush_mj"], 3))))
    p("       SOA: Q1 runs fully enhanced or off (the ideal diode regulates only a 20 mV forward drop): no linear dwell to judge")
    p("     reverse (REQ-015, -%s V with DC_P back-fed from the raised tracker ceiling through Q7's body diode): VDS %s V against %s V: MEETS (INFERRED);"
      % (fmt(D["vrev"]), fmt(A["q1_rev"]), fmt(F["csd19532_vds"])))
    p("       the LM74700-Q1's cathode to anode %s V against %s V recommended and %s V absolute, its ANODE -%s V against -%s V: MEETS (MAKER)"
      % (fmt(A["q1_rev"]), fmt(F["ld_ac_rec"]), fmt(F["ld_ca_abs"]), fmt(D["vrev"]), fmt(F["ld_anode_abs"])))
    p("       the body diodes: Q1's reverse-biased (it blocks); Q7's forward at DC_P's own milliamps (the back-feed); D10 off (%s V under its %s V"
      % (fmt(D["vrev"]), fmt(F["SMCJ40A"]["vbr_min"])))
    p("       breakdown); D1 reverse-biased (cathode on DC_P); the input capacitor of E-F1 at -%s V on its 100 V rating" % fmt(D["vrev"]))
    p("     transients (TEST-PLAN M2 CS101, M3 CS114 and M7 at decision 34's level, as L4-E7R derived them for the solar entry; no surge level is")
    p("       ruled, D-16 and CHO-003): CS101 curve 2, %s V rms, %s V peak: Q1 conducts forward and blocks at most %s V when the controller opens it"
      % (fmt(A["cs101_vrms"]), fmt(round(A["cs101_pk"], 3)), fmt(round(2 * A["cs101_pk"], 2))))
    p("       in %s us; at the range's top the input reaches %s V, past the OVLO's %s V minimum: the hot swap may switch off under M2 (an upset"
      % (fmt(A["trev_max_us"]), fmt(round(A["cs101_top"], 2)), fmt(F["ovlo"][0])))
    p("       against M2's line at a 36 V source, not a rating); at curve 2's own boundary, a %s V source, the top is %s V, %s V under it: MEETS."
      % (fmt(A["cs101_src_v"]), fmt(round(A["cs101_top_src"], 2)), fmt(round(F["ovlo"][0] - A["cs101_top_src"], 2))))
    p("       TEST-PLAN M2 states no source voltage, so the finding is a defect at REQ-015's top with two resolutions on the same topology: (i) M2 at")
    p("       the source's nominal, stated by TEST-PLAN's owner; (ii) the OVLO moved so its minimum clears %s V and its maximum stays under D10's %s V breakdown"
      % (fmt(round(A["cs101_top"], 2)), fmt(F["SMCJ40A"]["vbr_min"])))
    p("       minimum: R23 from %s k down to %s k with R22 %s k at 1 %% (the band re-derived: %s to %s V for R23 %s k, as s120 prints); no E96"
      % (fmt(round(A["r23_win"][1], 3)), fmt(round(A["r23_win"][0], 3)), fmt(A["r22_k"]), fmt(round(A["ovlo_check"][0], 2)), fmt(round(A["ovlo_check"][1], 2)), fmt(A["r23_k"])))
    p("       value lies inside; E192's %s k at 1 %% gives %s to %s V (%s V and %s V of margin); with R22 and R23 both 0.1 %%: %s to %s V, %s V over the"
      % (fmt(A["r23_e192"]), fmt(round(A["ovlo_e192"][0], 2)), fmt(round(A["ovlo_e192"][1], 2)), fmt(round(A["ovlo_e192"][0] - A["cs101_top"], 2)),
         fmt(round(F["SMCJ40A"]["vbr_min"] - A["ovlo_e192"][1], 2)), fmt(round(A["ovlo_new"][0], 2)), fmt(round(A["ovlo_new"][1], 2)),
         fmt(round(A["ovlo_new"][0] - A["cs101_top"], 2))))
    p("       CS101 peak and %s V under D10's breakdown minimum at 25 C. D10's breakdown falls %s %%/K (typical): %s V at -20 C, under the present"
      % (fmt(round(F["SMCJ40A"]["vbr_min"] - A["ovlo_new"][1], 2)), fmt(A["tvs_alpha"] * 100), fmt(round(A["d10_cold_vbr"], 2))))
    p("       OVLO maximum already, so steady inputs above it reach D10 when cold; REQ-015 admits steady inputs to 40 V, under it: MEETS for REQ-015's")
    p("       inputs. SESSION: (ii) at 0.1 % selected (it removes the finding whatever M2's source voltage; register R-94); (i) not taken (a test")
    p("       condition is not changed to fit the design); CS114 curve 4, %s mA rms into E-F1's 1 uF at 10 kHz: at most %s V peak, Q1 blocks"
      % (fmt(A["cs114_ma"]), fmt(round(A["cs114_pk"], 2))))
    p("       at most %s V; M7 with E-F1's capacitor: DC_F moves %s V, so Q1 stands off at most %s V: MEETS (INFERRED)"
      % (fmt(round(2 * A["cs114_pk"], 2)), fmt(F["ef1_dv"][1]), fmt(round(A["m7_vds"], 2))))
    p("       the capability scenario (D10 at its rated pulse, not a requirement): negative, Q1 at %s V with DC_P at %s V, past %s V by %s V; the"
      % (fmt(A["cap_neg_vds"]), fmt(D["vrev"]), fmt(F["csd19532_vds"]), fmt(round(A["cap_neg_vds"] - F["csd19532_vds"], 2))))
    p("       avalanche energy on the bus behind it at most %s mJ against EAS %s mJ; the LM74700-Q1's %s V is passed once DC_P exceeds %s V, and"
      % (fmt(round(A["cap_energy_mj"], 1)), fmt(A["eas"]), fmt(F["ld_ca_abs"]), fmt(A["cap_dcp_ld_limit"])))
    p("       Q1's once DC_P exceeds %s V: NOT MET, outside every requirement (D-16; DECISION-31 recorded it); positive: the controller's ANODE at"
      % fmt(A["cap_dcp_q1_limit"]))
    p("       %s V against %s V (E-N2)" % (fmt(F["SMCJ40A"]["vc"]), fmt(F["ld_anode_abs"])))
    p("     faults: an output short behind the hot swap: Q7 limits at %s to %s A with its power limit %s W at 36 V and %s W at the OVLO maximum (Equation 9,"
      % (fmt(F["entry_lim"][0]), fmt(F["entry_lim"][1]), fmt(round(A["plim36"], 2)), fmt(round(A["plim_ovlo"], 2))))
    p("       R24 %s Ohm, R19 %s Ohm; %s W with PWRLIM-1's spread) for at most %s ms, then restarts at %s %% duty; Q7's 10 ms SOA at 36 V %s W at TC 25 C,"
      % (fmt(A["rpwr"]), fmt(A["rs"]), fmt(round(A["plim_hi"], 2)), fmt(F["timer_ms"][2]), fmt(A["restart_duty"] * 100), fmt(round(A["soa_36_w"], 1))))
    p("       %s W at a %s C case (Figure 10, read; INFERRED): MEETS; Q1 carries at most %s A, and %s A for at most %s us at the circuit breaker: MEETS"
      % (fmt(round(A["soa_hot_w"], 1)), fmt(SOA_TC_HOT), fmt(F["entry_lim"][1]), fmt(round(A["cb_a"], 1)), fmt(A["tcb_max"])))
    p("       a short at DC_P, ahead of the hot swap (a single fault): only F1 limits, at most %s A for about %s ms (the 10 A part's I2t over it) against"
      % (fmt(round(D["f1_ipf"], 1)), fmt(round(A["dcp_short_s"] * 1e3, 3))))
    p("       IDM %s A for 100 us: no figure shows Q1 holds it; F1 clears it inside its interrupting rating (outside every requirement, ASM-001)" % fmt(A["idm"]))
    p("     gate drive and land: VGS %s to %s V (the charge pump's window) against +-%s V: MEETS; TI's guidance asks a VGS rating of %s V: MEETS;"
      % (fmt(A["cp_on_min"]), fmt(A["cp_off_max"]), fmt(A["vgs_max"]), fmt(A["gate_rec"])))
    p("       its Vth at most %s V against TI's recommended %s V: NOT MET as a recommendation (the drawn BSC039N06NS's 3.3 V also misses it;"
      % (fmt(A["vth"][2]), fmt(A["vth_rec_max"])))
    p("       effect: turn-on time and light-load regulation, bench R-80); RDS(on) %s mOhm typical at about %s C against TI's %s to %s mOhm at"
      % (fmt(round(A["rds_at_tj"], 2)), fmt(round(A["q1_tj"], 0)), fmt(round(A["rds_guide"][0], 2)), fmt(round(A["rds_guide"][1], 2))))
    p("       H3's %s A: MEETS (typical, INFERRED); TI recommends FETs to 60 V with this controller; the 100 V part is a deliberate departure (SESSION)"
      % fmt(F["h3"][9.0][1]))
    p("       whose reason, the controller's own pins, is checked above; the land is Q7's PowerPAK SO-8 / 5x6 SON for the same part")
    p("   F1, board E's vehicle-entry fuse: Littelfuse 0997010.WXN, MINI 58 V (the sheet revised 11/18/2025, held back; fetch_held_back.py)")
    p("     DC voltage rating %s V DC against the selected OVLO maximum %s V (R23 6.42k, 0.1 %%): MEETS (MAKER, a DC rating); interrupting %s A at 58 V DC against %s A: MEETS"
      % (fmt(A["f_v"]), fmt(round(D["f1_v"], 2)), fmt(A["f_int"]), fmt(round(D["f1_ipf"], 1))))
    p("     the prospective current by voltage (the kit's cable and lead, copper at -20 C, the source stiff: REQ-015 states no source impedance, so")
    p("       a vehicle battery and its wiring only lower it): %s" % "; ".join("%s V %s A" % (fmt(round(v, 2)), fmt(round(i, 1))) for v, i in A["f1_ipf_by_v"]))
    p("     no nuisance opening: the sheet's derating table (%s C columns) at the next column above %s C inside air, %s C: %s A against the entry's %s A: MEETS"
      % ("/".join(fmt(x) for x in A["f_amb"]), fmt(F["air"][1]), fmt(A["f_col"]), fmt(A["f_allow"]), fmt(F["entry_lim"][1])))
    p("       (the project's rule: the next higher column, never interpolated); 110 %% of rating opens no sooner than %s s; the hot swap's start-up"
      % fmt(A["f_tc"][110][0]))
    p("       at %s A for at most %s ms is %s A2s against the part's typical %s A2s (melting before arcing): MEETS (INFERRED)"
      % (fmt(F["entry_lim"][1]), fmt(F["timer_ms"][2]), fmt(round(A["f_startup_i2t"], 3)), fmt(A["f_i2t"])))
    p("     against what it protects: the time-current rows %s; the lowest stiff-source fault at 9 V with the copper at %s C is %s A, %s times"
      % ("; ".join("%d %% %s / %s s" % (k, fmt(v[0]), fmt(v[1]) if v[1] is not None else "-") for k, v in sorted(A["f_tc"].items())), fmt(F["air"][1]), fmt(round(A["f_min_fault_9v"], 1)), fmt(round(A["f_min_fault_9v"] / 10.0, 1))))
    p("       the rating, inside the 600 %% row (at most %s s); a fault between 13.5 and 20 A (a single upstream fault on a weak source) may take up to"
      % fmt(A["f_tc"][600][1]))
    p("       %s s, over J_DCIN's stated VH rating (7 A at AWG 18 shrouded, 10 A at AWG 16): the fuse protects the lead, not the contact, in that band" % fmt(A["f_tc"][135][1]))
    p("       (a residual of a single fault, ASM-001; R-29's lead change narrows it); Q1 against the stiff-source bound: above")
    p("     the holder: Keystone M65 p.42 names the 3568 'For Littelfuse Mini 297 or 997 series'; the sheet gives the same blade size and pitch:")
    p("       MEETS; the 58 V part's rejection feature works only in a 58 V keyed holder, so the 3568 also takes a 32 V MINI: the BOM, label and")
    p("       ASSEMBLY.md name the 0997 (R-18)")
    p("   U17, board A's PoE monitor: the INA226 (SBOS547C, byte-identical to ti.com on 2 October 2026) moved to R227, %s mOhm in the PoE stage's VBAT input"
      % fmt(A["u17_rsh"] * 1e3))
    p("     as drawn: IN+ and IN- at %s V against %s V absolute: NOT MET (HF-F02)" % (fmt(F["poe"]["volts"]), fmt(F["ina_abs"])))
    p("     common mode: VBAT at most %s V regulated, %s V at SYSOVP, %s V at the pack-open bound, %s V at D1's rated pulse, against %s V (CMRR row and"
      % (fmt(F["chg_v_max"]), fmt(F["sysovp"][2]), fmt(round(D["pack_open"]["v_end"], 3)), fmt(F["SMCJ18A"]["vc"]), fmt(F["ina_cm_op"])))
    p("       bus range) and %s V absolute: MEETS (MAKER); VBUS on POE_VIN likewise" % fmt(F["ina_abs"]))
    p("     differential: the stage's input at its 0.6 A at a %s V stack, %s A, %s mV; at its fault bound, U16's boost peak limit (%s + %s) mV over"
      % (fmt(D["vbat_low"]), fmt(round(A["u17_in_norm"], 3)), fmt(round(A["u17_mv_norm"], 2)), fmt(A["vcs_boost_max"] * 1e3), fmt(A["cs_off"] * 1e3)))
    p("       R72's %s mOhm at -1 %%, %s A, %s mV: both inside the %s mV full scale: MEETS (INFERRED); R227 then dissipates %s W against %s W at %s C"
      % (fmt(A["poe_rcs"] * 1e3), fmt(round(A["u17_fault_a"], 2)), fmt(round(A["u17_mv_fault"], 2)), fmt(F["ina_fs_mv"]), fmt(round(A["u17_p_fault"], 3)), fmt(round(A["hojlr_avail"], 2)), fmt(F["air"][1])))
    p("       (HoJLR2512: %s W derated from %s C to zero at %s C): MEETS" % (fmt(A["hojlr"][0]), fmt(A["hojlr"][1]), fmt(A["hojlr"][2])))
    p("       R227 is the part L4-E4 chose for R138, HoJLR2512-3W-5mR-1%%, LCSC %s (Milliohm; +-1 %%, TCR +-%s ppm/K, MAKER as L4-E4 read it)"
      % (A["r5_lcsc"], fmt(round(A["r5_tcr"] * 1e6))))
    p("     a PoE fault (an overload or a short on +54V_POE): U16 is a four-switch buck-boost; with its output pulled under its input it runs in buck")
    p("       operation, where the high-side current's valley is held at VCS(BUCK) %s mV maximum over R72 (%s A at -1 %%) and the input current is the"
      % (fmt(A["vcs_buck_max"] * 1e3), fmt(round(A["u17_buck_valley_a"], 2))))
    p("       inductor's times the duty: under the boost bound above (INFERRED, SNVSAI1D 7.3.1 and 7.3.5); a port's own fault is board B's TPS23861's")
    p("     U16's own input: its VIN and BIAS move with U17 to POE_VIN, at most %s V under VBAT at the fault bound; its UVLO and BIAS window are"
      % fmt(round(A["u17_mv_fault"] * 1e-3, 3)))
    p("       read against VBAT less that drop (the helper refuses a BIAS rail other than the input without a blocking diode, so both move)")
    p("     startup: the sheet: 'the bus voltage can be present with the supply voltage off, and reciprocally': MEETS (MAKER)")
    p("     a load dump: the vehicle reaches VBAT only through the front end and the charger, so VBAT's own bounds above hold: MEETS")
    p("     accuracy: VOS %s uV, %s mA; gain %s %% with R227's 1 %% and %s ppm/K over %s K (L4-E4's span): %s %% plus %s mA (INFERRED)"
      % (fmt(A["ina_vos_uv"]), fmt(round(A["u17_off_ma"], 2)), fmt(A["ina_gain"] * 100), fmt(round(A["r5_tcr"] * 1e6)), fmt(A["r5_span_k"]),
         fmt(round(A["u17_err_pct"], 3)), fmt(round(A["u17_off_ma"], 2))))
    p("     for the firmware (FW-A09): the readings are the PoE stage's INPUT current and VBAT; full scale %s A, Current_LSB %s mA, CAL %s"
      % (fmt(round(A["u17_fs_a"], 3)), fmt(round(A["u17_lsb"] * 1e3, 3)), fmt(round(A["u17_cal"], 1))))
    p("       (0.00512 over Current_LSB x R); the PoE output power is inferred as the input power times the stage's efficiency (0.88, undocumented)")
    return L


# ------------------------------------------------------------------------------------------------------- the rows
def rows(F, D, A):
    R = []
    sm40, sm28, sm18 = F["SMCJ40A"], F["SMCJ28A"], F["SMCJ18A"]
    pv = F["pv"]
    R.append({
        "id": "IF-01", "title": "the panel to board E's solar entry (J_SOLAR, F2, the sense bank, D4, C71 to C74, PV_IN, PV_P and TRK_VS)",
        "a": "the panel (SPR-E-Flex-100 candidate, O-1, source compliance INCONCLUSIVE)", "b": "board E, PV_IN, PV_P and TRK_VS (L4-E7R's corrected entry)",
        "v": "panel: open circuit at most %s V at -20 C (REQ-016, gen PV_P v_max); candidate %s V nominal at -20 C; held at %s V nominal | entry: D4 %s standoff %s V on TRK_VS; under CS101 the input at most %s V; TRK_VS at most %s V and PV_P %s V at the capability scenario"
             % (fmt(pv["v_max"]), fmt(F["cand_voc_cold"]), fmt(F["hold"][1]), "SMCJ28A", fmt(sm28["vr"]), fmt(F["cs101_pv"]), fmt(F["trk_vs_max"]), fmt(F["pv_p_max"])),
        "i": "panel hot short circuit %s A with the sheet's power tolerance (L4-E7R; %s A nominal sheet) | F2 %s A blade, J_SOLAR VH (%s A at AWG 16, standard header; %s A at AWG 18, shrouded only; the lead is AWG 18 on a standard header: no stated rating); under CS101 %s A rms crosses the sense bank"
             % (fmt(F["isc_hot_tol"]), fmt(F["cand_isc_hot"]), fmt(amps_in(F["e_f2"], "F2")), fmt(F["vh_16"]), fmt(F["vh_18"]), fmt(F["cs101_bank_a"])),
        "loss": "the 5 m lead about 0.0465 Ohm (the replay's ESTIMATE); the sense bank %s Wh on SC-37's day, %s Wh on the bright day (L4-E7R)" % (fmt(F["bank_wh"][0]), fmt(F["bank_wh"][1])),
        "therm": "the entry at the worst inside air %s C (envelope, lid closed); the bulk cans' heating under CS101's bounding case CONDITIONAL (M2 records it)" % fmt(F["air"][1]),
        "prot_a": "none (a bare panel)", "prot_b": "F2; D4 one-way clamp on TRK_VS; the 50 V bulk and C71 to C74 on TRK_VS; C70 across R66 (L4-E7R, drafted in apply_gen_sch_e_backstop.py)",
        "settled": "l4e (O-1), L4-E7R at 237cd9be (closing check 42fe879f)", "checks": [
            Chk("the candidate's nominal cold open circuit within REQ-016's 25 V", F["cand_voc_cold"], "<=", pv["v_max"], "V", "CONDITIONAL", "replay out 12; source compliance needs a supported maximum (O-1)"),
            Chk("D4's standoff above the window's 25 V", pv["v_max"], "<=", sm28["vr"], "V", "MAKER", "Littelfuse SMCJ row"),
            Chk("the panel's hot short circuit with the sheet's power tolerance inside F2", F["isc_hot_tol"], "<=", amps_in(F["e_f2"], "F2"), "A", "INFERRED", "L4-E7R out; gen F2"),
            Chk("the panel's hot short circuit with tolerance inside J_SOLAR's nearest stated VH rating (AWG 18, shrouded header)", F["isc_hot_tol"], "<=", F["vh_18"], "A", "ASSUMPTION", "JST VH catalogue p.1; the fitted standard header with AWG 18 is not rated"),
            Chk("D4 does not conduct under CS101 (the input's peak under its standoff)", F["cs101_pv"], "<", sm28["vr"], "V", "MODELED", "L4-E7R out (lumped model)"),
            Chk("TRK_VS at the capability scenario under the bulk's and the ceramics' 50 V", F["trk_vs_max"], "<=", 50.0, "V", "MODELED", "L4-E7R out (capability, not a requirement)"),
            Chk("PV_P at the capability scenario under U18's VIN+ %s V" % fmt(F["u18_vin"]), F["pv_p_max"], "<=", F["u18_vin"], "V", "MODELED", "L4-E7R out"),
            Chk("U5's sense differential under the approved disturbances and the capability scenario", F["u5_diff"], "<=", F["u5_diff_lim"], "V", "CONDITIONAL", "L4-E7R out: the lumped model, layout, M3, M7, bench 7b.18"),
            Chk("the backstop does not trip under TEST-PLAN M2 (CS101's injected current across the sense bank; 'no upset')", None, "<=", None, "the follow-up", "PENDING", L4E7R),
        ]})
    R.append({
        "id": "IF-02", "title": "PV_P to the LT8705A stage U5 (the hold, the regulation and the backstop on SWEN) to TRK_OUT",
        "a": "PV_P and TRK_VS (behind the sense bank, L4-E7R)", "b": "TRK_OUT",
        "v": "in: hold %s / %s / %s V (EA3 typical), %s to %s V conditioned (L4-E7), at most %s V; SWEN off by default below %s V on TRK_LDO33 | out: ceiling %s / %s / %s V (L4-E5, R10 232 k; as drawn %s / %s / %s V)"
             % (fmt(F["hold"][0]), fmt(F["hold"][1]), fmt(F["hold"][2]), fmt(F["hold_cond"][0]), fmt(F["hold_cond"][1]), fmt(pv["v_max"]), fmt(F["swen_v"]),
                fmt(F["trk_ceiling"][0]), fmt(F["trk_ceiling"][1]), fmt(F["trk_ceiling"][2]), fmt(F["trk_drawn"][0]), fmt(F["trk_drawn"][1]), fmt(F["trk_drawn"][2])),
        "i": "the regulation (RIMON_IN 30k) %s A nominal, %s A at its highest on the hold's corners (%s W and %s W in); the backstop trips at %s to %s A at 25 V; the static bound %s W, the regulation's own 25 V corner %s W | out at the window %s W (stage %s DECLARED), a ceiling: the stage takes at most %s W in at the hold"
             % (fmt(F["reg"][0]), fmt(F["reg"][1]), fmt(F["reg_w"][0]), fmt(F["reg_w"][1]), fmt(F["bs_trip"][0]), fmt(F["bs_trip"][1]), fmt(F["static_bound"]), fmt(F["reg_corner"]),
                fmt(D["trk_out_w"]), fmt(F["trk"]["efficiency"]), fmt(F["reg_w"][1])),
        "loss": "stage %s DECLARED (C-8, undocumented)" % fmt(F["trk"]["efficiency"]),
        "therm": "U5 junction about %s C (INFERRED) in %s C air against the I grade's 125 C" % (fmt(F["u5_tj"]), fmt(F["air"][1])),
        "prot_a": "the regulation (IMON_IN at RIMON_IN 30k); the backstop on SWEN (the sense bank, U18 INA169, U19 TPS3701, U20 TPS3808), its response inside %s ms for 10 J in any 0.1 s" % fmt(F["bs_allow_ms"]),
        "prot_b": "U4/Q2 ideal diode blocks the bus",
        "settled": "l4e7 (hold, grade), l4e5 (ceiling), L4-E7R at 237cd9be (closing check 42fe879f)", "checks": [
            Chk("the stage's input power at the 25 V corner, the backstop's static bound, against REQ-016's 100 W", F["static_bound"], "<=", 100.0, "W", "CONDITIONAL", "L4-E7R out: CONDITIONAL on G_CM and U18's VIN+ bias (break-evens printed there)"),
            Chk("the regulation's own 25 V corner against REQ-016's 100 W", F["reg_corner"], "<=", 100.0, "W", "INFERRED", "L4-E7R out"),
            Chk("the regulation's highest current under the backstop's lowest trip (no trip in normal operation)", F["reg"][1], "<", F["bs_trip"][0], "A", "CONDITIONAL", "L4-E7R out: the regulation's unprinted values inside the joint assumptions, else a hiccup"),
            Chk("the response from a step over the trip inside %s ms (10 J in any 0.1 s; the 0.1 s interpretation is layer 8's; bench 7b.16)" % fmt(F["bs_allow_ms"]), None, "<=", None, "an interpretation and a bench row", "CONDITIONAL", "L4-E7R out, check (b)"),
            Chk("U5's junction inside the I grade's 125 C", F["u5_tj"], "<=", 125.0, "C", "INFERRED", "l4e7 out 3"),
            Chk("the backstop's trip under TEST-PLAN M2 (CS101), the open material defect of the closing check", None, "<=", None, "the follow-up", "PENDING", L4E7R),
        ]})
    R.append({
        "id": "IF-03", "title": "TRK_OUT through U4/Q2 (ideal diode) onto VIN_RAW",
        "a": "TRK_OUT (C24, C25 35 V polymer; C26, C27 10u 25 V)", "b": "VIN_RAW (board E)",
        "v": "TRK_OUT at most %s V (raised ceiling) | VIN_RAW up to the vehicle's OVLO maximum %s V with TRK_OUT at 0 (R23 6.42k at 0.1 %%; %s V as drawn)" % (fmt(F["trk_ceiling"][2]), fmt(round(F["ovlo_sel"][2], 2)), fmt(F["ovlo"][2])),
        "i": "asked: at the window %s W out, at H3's lowest settle point (%s V) %s A | available: the declared _TRK_A %s A" % (fmt(D["trk_out_w"]), fmt(F["settle_865"][1]), fmt(round(D["trk_i_settle"], 3)), fmt(F["trk"]["typ"])),
        "loss": "Q2's RDS(on) (milliohms)", "therm": "inside air %s C" % fmt(F["air"][1]),
        "prot_a": "the stage's own limit", "prot_b": "U4 blocks VIN_RAW into TRK_OUT",
        "settled": "l4e5 (ceiling, C26/C27), this record (reverse)", "checks": [
            Chk("C26 and C27 (10u 25 V) at the raised ceiling", F["c26_pct"], "<=", 100.0, "% of rating", "NETLIST", "l4e5 out 3", scope="drawn"),
            Chk("C26 and C27 re-rated to a 50 V part (the drawn C13's 10u 50V) at the raised ceiling", F["trk_ceiling"][2], "<=", 50.0, "V", "NETLIST", "the owed re-rate, register R-14"),
            Chk("C24 and C25 (35 V polymer) at the raised ceiling, for the derating gate", F["c24_pct"], "<=", 100.0, "% of rating", "NETLIST", "l4e5 out 3"),
            Chk("Q2 (BSC039N06NS, 60 V) blocking the vehicle bus at its OVLO maximum with TRK_OUT at 0", round(F["ovlo_sel"][2], 2), "<=", F["bsc039_vds"], "V", "MAKER", "this record out 11 (R23 6.42k); Infineon p.1"),
            Chk("U4 (LM74700-Q1) cathode to anode at the OVLO maximum", round(F["ovlo_sel"][2], 2), "<=", F["ld_ca_abs"], "V", "MAKER", "TI SNOSD17G 6.1"),
        ]})
    R.append({
        "id": "IF-04", "title": "the vehicle and shore input to board E's entry (J_DCIN, F1, D10, U3/Q1 LM74700 ideal diode) to DC_P",
        "a": "a vehicle or shore supply, 9 to 36 V (REQ-015), reversed or at an over-voltage to 40 V", "b": "board E, DC_F and DC_P",
        "v": "9 to %s V in service, CS101's %s V peak on it under M2; reversed to -%s V | OVLO %s / %s / %s V selected (R23 6.42k, R22 100k, both 0.1 %%; %s / %s / %s V as drawn); D10 SMCJ40CA breakdown %s V minimum either way at 25 C, %s V at -20 C (typical coefficient)"
             % (fmt(D["vrev"]), fmt(round(A["cs101_pk"], 2)), fmt(D["vrev"]), fmt(round(F["ovlo_sel"][0], 2)), fmt(round(F["ovlo_sel"][1], 2)), fmt(round(F["ovlo_sel"][2], 2)),
                fmt(F["ovlo"][0]), fmt(F["ovlo"][1]), fmt(F["ovlo"][2]), fmt(sm40["vbr_min"]), fmt(round(A["d10_cold_vbr"], 2))),
        "i": "asked: the entry limits at %s to %s A (LM5069, R19 10 mOhm, VCL %s / %s / %s mV); a stiff source's fault at most %s A (the kit's cable at -20 C) | available: F1 Littelfuse 0997010.WXN 10 A (%s A at its %s C column), %s A at 58 V DC; Q1 CSD19532Q5B %s A; J_DCIN VH, the lead AWG %d (no stated rating at it)"
             % (fmt(F["entry_lim"][0]), fmt(F["entry_lim"][1]), fmt(F["vcl"][0]), fmt(F["vcl"][1]), fmt(F["vcl"][2]), fmt(round(D["f1_ipf"], 1)), fmt(A["f_allow"]), fmt(A["f_col"]), fmt(A["f_int"]), fmt(A["id_cont"]), int(F["lead_awg"])),
        "loss": "F1, Q1, R19, Q7 and L2 in series (about 0.2 V, the generator's note); Q1 at most %s W" % fmt(round(A["q1_p"], 3)),
        "therm": "R19 and Q7 at 6.15 A continuous, 32 K rise (gen_sch_e.py); Q1's junction at most %s C in %s C air (INFERRED)" % (fmt(round(A["q1_tj"], 1)), fmt(F["air"][1])),
        "prot_a": "the supply's own", "prot_b": "F1 (0997 blade); D10 (two-way, at the entry); U3/Q1 reverse block (CSD19532Q5B); D1 at DC_P; the LM5069 (UVLO 9 V, OVLO, current limit and its timer)",
        "settled": "d8dec31 (E-F1, E-F2), this record (part A: Q1, F1 and the OVLO), l4e5", "checks": [
            Chk("D10 does not conduct up to the selected OVLO maximum (25 C)", round(F["ovlo_sel"][2], 2), "<", sm40["vbr_min"], "V", "MAKER", "this record out 11; Littelfuse SMCJ40A row"),
            Chk("D10 does not conduct at REQ-015's 40 V at -20 C (the breakdown's typical coefficient)", 40.0, "<", round(A["d10_cold_vbr"], 2), "V", "INFERRED", "Littelfuse SMCJ sheet p.1, VBR at TJ"),
            Chk("D10 does not conduct on a reversed 36 V input (two-way part)", D["vrev"], "<", sm40["vbr_min"], "V", "MAKER", "Littelfuse SMCJ40CA row"),
            Chk("Q1 in reverse, DC_P back-fed from the drawn tracker ceiling (Q1 BSC039N06NS)", D["q1_rev_drawn"], "<=", F["bsc039_vds"], "V", "INFERRED", "l4e5 out 2, Q7's body diode; Infineon p.1", scope="drawn"),
            Chk("Q1 in reverse with L4-E5's raised ceiling, Q1 as drawn (BSC039N06NS)", D["q1_rev"], "<=", F["bsc039_vds"], "V", "INFERRED", "l4e5 ceiling; Infineon p.1", scope="drawn"),
            Chk("Q1 in reverse with the raised ceiling, Q1 the CSD19532Q5B (part A; register R-17)", D["q1_rev"], "<=", F["csd19532_vds"], "V", "INFERRED", "TI CSD19532Q5B p.1"),
            Chk("U3 (LM74700-Q1) cathode to anode in that reverse", D["q1_rev"], "<=", F["ld_ac_rec"], "V", "MAKER", "TI SNOSD17G 6.3, recommended; 75 V absolute"),
            Chk("Q1's junction at the entry's highest limit", round(A["q1_tj"], 1), "<=", A["tj_max"], "C", "INFERRED", "part A (Figure 8; RthetaJA on 1 in2 2 oz)"),
            Chk("F1's voltage rating (Littelfuse 297, the series the holder takes) against the highest steady input the drawn entry admits", F["ovlo"][2], "<=", F["f297_v"], "V", "MAKER", "Littelfuse 297 sheet; s120 OVLO", scope="drawn"),
            Chk("F1 (0997010.WXN) DC voltage rating against the selected OVLO maximum", round(D["f1_v"], 2), "<=", A["f_v"], "V", "MAKER", "Littelfuse 0997 sheet (held back), DC rating"),
            Chk("F1's interrupting rating against the kit cable's prospective current at -20 C from a stiff source", round(D["f1_ipf"], 1), "<=", A["f_int"], "A", "MAKER", "Littelfuse 0997 sheet; this record out 7"),
            Chk("F1 at its derating table's next higher column above the inside air (%s C), against the entry's highest limit" % fmt(A["f_col"]), F["entry_lim"][1], "<=", A["f_allow"], "A", "MAKER", "Littelfuse 0997 derating table, never interpolated"),
            Chk("the entry's limit inside F1 (10 A blade)", F["entry_lim"][1], "<=", amps_in(F["e_f1"], "F1"), "A", "MAKER", "LM5069 VCL / R19; gen F1"),
            Chk("the entry's limit inside J_DCIN's nearest stated VH rating (AWG 18, shrouded header)", F["entry_lim"][1], "<=", F["vh_18"], "A", "ASSUMPTION", "JST VH catalogue p.1; the fitted header and gauge are not rated"),
            Chk("the negative discharge at the ruled level (15 kV) with E-F1's 1 uF input capacitor: DC_F's rise against D10's breakdown", F["ef1_dv"][1], "<", sm40["vbr_min"], "V", "INFERRED", "DECISION-31 6.3 (d8dec31 apply_gen_sch_e_cin.py, register R-16)"),
            Chk("CS101 (M2) at REQ-015's 36 V: the input's peak under the drawn OVLO minimum", round(A["cs101_top"], 2), "<", F["ovlo"][0], "V", "INFERRED", "part A (L4-E7R's CS101 level)", scope="drawn"),
            Chk("CS101 (M2) at REQ-015's 36 V: the input's peak under the selected OVLO minimum (R23 6.42k, 0.1 %; register R-94)", round(A["cs101_top"], 2), "<", round(F["ovlo_sel"][0], 2), "V", "INFERRED", "part A"),
        ]})
    R.append({
        "id": "IF-05", "title": "DC_P through the hot swap U6/Q7 (LM5069) and the choke L2 to VIN_RAW",
        "a": "DC_P", "b": "VIN_RAW (board E)",
        "v": "DC_P up to D1's clamping %s V at %s A | LM5069 VIN %s V absolute; Q7 %s V" % (fmt(sm40["vc"]), fmt(sm40["ipp"]), fmt(F["lm5069_vin_abs"]), fmt(F["e_q7_v"])),
        "i": "asked: the limit %s to %s A, fault timer %s / %s / %s ms then off and retry (-2) | available: L2 %s" % (fmt(F["entry_lim"][0]), fmt(F["entry_lim"][1]), fmt(F["timer_ms"][0]), fmt(F["timer_ms"][1]), fmt(F["timer_ms"][2]), "6.89 A Irms, 9.15 A Isat (its value text)"),
        "loss": "R19 0.38 W at 6.15 A", "therm": "inside air %s C" % fmt(F["air"][1]),
        "prot_a": "D1 SMCJ40A at DC_P", "prot_b": "D2 SMCJ40A on VIN_RAW",
        "settled": "gen_sch_e.py (F-IN-02), l4e5", "checks": [
            Chk("the LM5069's VIN at D1's clamping voltage", sm40["vc"], "<=", F["lm5069_vin_abs"], "V", "MAKER", "TI SNVS452G 7.1"),
            Chk("Q7 at D1's clamping voltage", sm40["vc"], "<=", F["e_q7_v"], "V", "MAKER", "TI CSD19532Q5B p.1"),
            Chk("the entry's limit inside L2's Irms (its value text)", F["entry_lim"][1], "<=", 6.89, "A", "NETLIST", "gen_sch_e.py L2"),
        ]})
    R.append({
        "id": "IF-06", "title": "VIN_RAW over the dock (board E, E5, board A J_VR1 to J_VR4)",
        "a": "VIN_RAW (board E)", "b": "VIN_RAW (board A, U2's input)",
        "v": "solar: H3's knee (HIZ certain below %s V, out of HIZ above %s V, regulation from %s V) to the ceiling %s V; vehicle 9 to %s V; OVLO maximum %s V | U2 VIN %s V absolute"
             % (fmt(F["hiz_below"]), fmt(F["hiz_out_above"]), fmt(F["pin_reg_from"]), fmt(F["trk_ceiling"][2]), fmt(D["vrev"]), fmt(round(F["ovlo_sel"][2], 2)), fmt(F["u2_vin_abs"])),
        "i": "in service at most %s A (H3, 9 V vehicle); at the window %s A from the tracker; the front end's fault current at most %s A (R11 8 mOhm, R12 12 mOhm; %s A at 7 mOhm) | declared %s A; four Mill-Max pins at %s A each"
             % (fmt(F["h3"][9.0][1]), fmt(round(D["trk_i_settle"], 2)), fmt(round(D["vin_fault"], 3)), fmt(round(D["vin_fault_7"], 3)), fmt(F["vin_raw_a"]["typ"]), fmt(F["millmax_a"])),
        "loss": "the dock's contacts and 12 AWG wires (IF-AE-DOCK)", "therm": "about 6 K rise of the pins at 14.10 A (IF-AE-DOCK, INFERRED)",
        "prot_a": "the entry (IF-04, IF-05); D2 on board E", "prot_b": "D2 SMCJ40A on board A; U34's restart guard",
        "settled": "l4e5, l4e6, IF-AE-DOCK, DECISION-31 (A-N1)", "checks": [
            Chk("the highest steady VIN_RAW (the selected OVLO maximum) inside U2's absolute rating", round(F["ovlo_sel"][2], 2), "<=", F["u2_vin_abs"], "V", "MAKER", "this record out 11; TI SNVSAI1D 6.1"),
            Chk("the front end's fault current at the onset of its average limit inside the declared VIN_RAW current", D["vin_fault"], "<=", F["vin_raw_a"]["typ"], "A", "INFERRED", "l4e6 out 5 (R11 band, 20.887 V, 0.93, %s V)" % fmt(F["avg_from"])),
            Chk("one Mill-Max pin with one of four open at that fault current", D["vin_fault"] / 3.0, "<=", F["millmax_a"], "A", "INFERRED", "Mill-Max p.28 (the 0850 to 0853 sibling figure)"),
            Chk("the clamp D2 at its rated pulse against U2's 60 V (no surge level is ruled, D-16; at the ruled discharge the bus's capacitance holds it to 0.11 V)", sm40["vc"], "<=", F["u2_vin_abs"], "V", "MAKER", "DECISION-31 A-N1, S-111: a recorded residual outside the requirements", scope="drawn"),
        ]})
    r11_8 = F["r11_8"]
    R.append({
        "id": "IF-07", "title": "VIN_RAW through the front end U2 (LM5176), R11 and R12, to VBUS20",
        "a": "VIN_RAW (board A)", "b": "VBUS20",
        "v": "in %s to %s V | out %s to %s V DC band, %s V bound (the typical-only OVP)" % (fmt(F["hiz_below"]), fmt(round(F["ovlo_sel"][2], 2)), fmt(F["vbus_band"][0]), fmt(F["vbus_band"][1]), fmt(F["vbus_bound"])),
        "i": "asked in service %s A through R11 (U3 at %s A, %s A board current, plus 0.079 A) | R11 8 mOhm stacked minimum %s A at 62.1 C with C-1's taps; highest permitted %s A; R12 peak limit %s / %s / %s A"
             % (fmt(F["r11_need"]), fmt(F["iin_host"]), fmt(F["u3_max_board"]), fmt(F["r11_min_62_full"]), fmt(r11_8[2]), fmt(F["r12_peak"][0]), fmt(F["r12_peak"][1]), fmt(F["r12_peak"][2])),
        "loss": "front end %s DECLARED (C-8)" % fmt(F["eta_fe"]),
        "therm": "FETs at most %s C on the ASSUMED 50 C/W (C-3); L1 at most %s C (qualifying), its Isat there INCONCLUSIVE (C-5)" % (fmt(F["fet_tj"]), fmt(F["l1_qual"])),
        "prot_a": "U34 restart guard (UV %s / %s / %s V falling); the clamp D2" % (fmt(F["latch"][0]), fmt(F["latch"][1]), fmt(F["latch"][2])),
        "prot_b": "the average limit (R11), the cycle-by-cycle limit (R12), no hiccup; OVP on FB; no clamp on VBUS20 (S-111)",
        "settled": "l4e4, l4e5, l4e6, r11dep, s120", "checks": [
            Chk("R11's stacked minimum (8 mOhm, C-1's full taps, 62.1 C) above what U3 and the other loads ask", F["r11_need"], "<=", F["r11_min_62_full"], "A", "CONDITIONAL", "l4e4 out 2; U3's minimum rests on C-7"),
            Chk("the pin path's highest current (26.50 to 27.24 V on a stiff source) through R11 8 mOhm alone at 62.1 C", F["pin_path"], "<=", F["r11_min_62_alone"], "A", "INFERRED", "l4e5 out 7; l4e4 out 2"),
            Chk("the pin path with C-1's full tap allowance: holds only if bench V-A07 reads the pin's error at most %s A, else R11 7 mOhm (the bank and R12 serve both)" % fmt(F["pin_err_allow"]), None, "<=", None, "a measurement", "CONDITIONAL", "l4e5 out 7; l4e6 out 7; l4e8 check 3"),
            Chk("the in-service boost peak under the peak limit's minimum (R12 12 mOhm)", F["svc_peak"], "<", F["r12_peak"][0], "A", "INFERRED", "l4e6 out 5"),
            Chk("L1's peak bound at 90 % of its typical Isat at 25 C", F["l1_peak"], "<=", 0.9 * F["l1_isat"], "A", "MAKER", "l4e6 out 5; Coilcraft p.1"),
            Chk("L1's Isat at %s C at least %s A, so its peak bound stays at 90 %% of it (C-5: Coilcraft's derating or the L-versus-current sweep)" % (fmt(F["l1_qual"]), fmt(F["l1_need"])), None, "<=", None, "a maker figure or a measurement", "CONDITIONAL", "l4e6 out 5"),
            Chk("every FET's junction at the highest permitted current on the ASSUMED 50 C/W", F["fet_tj"], "<=", 150.0, "C", "CONDITIONAL", "l4e6 out 5: C-3"),
            Chk("U2's VIN at the highest steady input", round(F["ovlo_sel"][2], 2), "<=", F["u2_vin_abs"], "V", "MAKER", "TI SNVSAI1D 6.1"),
        ]})
    R.append({
        "id": "IF-08", "title": "VBUS20's bulk bank (six EEHZK1V331P, each behind a 45 mOhm ballast; Cc2 3.3 nF)",
        "a": "the front end's output and U3's input pulses", "b": "the six cans",
        "v": "VBUS20 at most %s V | the cans' 35 V" % fmt(F["vbus_bound"]),
        "i": "every can at most %s A (R11 8 mOhm, 7.262 A); %s A at 7 mOhm | the rule's %s A; %s A at 7 mOhm" % (fmt(F["can8"][0]), fmt(F["can7"][0]), fmt(F["can8"][1]), fmt(F["can7"][1])),
        "loss": "the ballasts at most %s W at the bound's worst corner, %s W at L4-E8's nominal illustration: an operating-point term carried in the energy and thermal budgets (out 8), never added again once a measured efficiency includes it" % (fmt(F["ballast_w"]), fmt(F["ballast_nom_w"])),
        "therm": "the can's rise is a bench reading (lifetime CONDITIONAL); the cold ESR envelope INFERRED; the ballasts' heat at most %s K on the inside air at T-H1's floor (out 8)" % fmt(round(F["ballast_w"] / F["th1"], 2)), "prot_a": "R12's peak limit and R11's average limit", "prot_b": "the ballasts",
        "settled": "l4e8 (accepted, check 3)", "checks": [
            Chk("every can at R11 8 mOhm (a conservative bound)", F["can8"][0], "<=", F["can8"][1], "A", "INFERRED", "l4e8 out 6"),
            Chk("every can at R11 7 mOhm (only if V-A07 fails; VIN and VBAT sampled)", F["can7"][0], "<=", F["can7"][1], "A", "CONDITIONAL", "l4e8 out 6; check 3"),
            Chk("the cans' voltage at the bus's bound", F["vbus_bound"], "<=", 35.0, "V", "INFERRED", "s120 out 8"),
            Chk("the cans' lifetime at their measured temperature rise (bench 7b.8 item 4); the cold ESR envelope at -20 C over life", None, "<=", None, "a measurement", "CONDITIONAL", "l4e8 out 6b; check 3"),
        ]})
    R.append({
        "id": "IF-09", "title": "VBUS20 through R16 and the charger U3 (BQ25731) to VBAT, the system node",
        "a": "VBUS20", "b": "VBAT (VSYS) and the pack's charge",
        "v": "VBUS20 %s to %s V, bound %s V | U3 VBUS and VSYS %s V absolute, VBUS %s V recommended; VBAT %s to %s V; SYSOVP %s / %s / %s V"
             % (fmt(F["vbus_band"][0]), fmt(F["vbus_band"][1]), fmt(F["vbus_bound"]), fmt(F["u3_abs"]), fmt(F["u3_rec_vbus"]), fmt(D["vbat_low"]), fmt(F["chg_v_max"]), fmt(F["sysovp"][0]), fmt(F["sysovp"][1]), fmt(F["sysovp"][2])),
        "i": "IIN_HOST %s A, minimum %s A, maximum %s A board current; the window needs %s A at %s V | delivered at VBAT %s to %s W; ChargeCurrent at most %s A"
             % (fmt(F["iin_host"]), fmt(F["u3_min"]), fmt(F["u3_max_board"]), fmt(F["win_need"]), fmt(F["bus_low"]), fmt(round(D["vbat_avail_min"], 1)), fmt(round(D["vbat_avail_max"], 1)), fmt(F["chg_set"])),
        "loss": "U3 %s (INFERRED)" % fmt(F["eta_u3"]), "therm": "the charger's own; inside air %s C" % fmt(F["air"][1]),
        "prot_a": "the H3 line on ILIM_HIZ (hardware), IIN_HOST, VINDPM about 18.5 V, ACOV", "prot_b": "BATOVP %s V, SYSOVP; the pack's OCC %s A" % (fmt(F["batovp"]), fmt(F["occ"])),
        "settled": "l4e4, l4e5, s120, FW-A02", "checks": [
            Chk("U3's minimum covers the window at the lowest bus (C-7: the 0.1 A is INFERRED)", F["win_need"], "<=", F["u3_min"], "A", "CONDITIONAL", "l4e4 out 1"),
            Chk("U3's VBUS at the bus's bound", F["vbus_bound"], "<=", F["u3_abs"], "V", "INFERRED", "s120 out 9; TI SLUSE66A p.8"),
            Chk("ACOV not reached at the bus's bound", F["vbus_bound"], "<", F["acov_min"], "V", "INFERRED", "s120 out 9"),
            Chk("ChargeCurrent inside REQ-075's 3.06 A", F["chg_set"], "<=", 3.06, "A", "NETLIST", "FW-A02"),
            Chk("ChargeCurrent inside the pack's OCC", F["chg_set"], "<", F["occ"], "A", "NETLIST", "pcb_pack_protection.yaml"),
            Chk("the charge per cell inside the cell maker's maximum charge current", F["chg_set"] / 3.0 * 1000.0, "<=", F["cell_chg_ma"], "mA", "MAKER", "Samsung 35E 3.7"),
        ]})
    R.append({
        "id": "IF-10", "title": "VBAT and the pack (board A F1 and R17, the dock's pack pins, board E F3, the XT60 lead, board P's chain)",
        "a": "VBAT (the kit's loads and U3)", "b": "the 4S3P pack (D-06) and board P",
        "v": "%s V (the gauge's CUV %s V a cell) to %s V; BATOVP %s V | D1 SMCJ18A standoff %s V, breakdown %s V minimum; the pack FETs 30 V"
             % (fmt(D["vbat_low"]), fmt(F["cuv"]), fmt(F["chg_v_max"]), fmt(F["batovp"]), fmt(sm18["vr"]), fmt(sm18["vbr_min"])),
        "i": "declared %s A continuous, %s A peak; PS-IDLE-SPEC %s / %s / %s / %s A at 16.8 / 14.4 / 12.0 / 10.0 V; the PA keyed at 113 W %s A at 10.0 V; PS-ALLTX's 18 A at a %s V stack (D-11); charge %s A | OCD1 %s A for %s s, SCD %s A; the pins %s / %s A; XT60 %s A"
             % (fmt(F["pp_cont"]), fmt(F["pp_peak"]), *[fmt(x) for x in F["idle_i"]], fmt(F["pa113"][4]), fmt(F["alltx_18a_stack"]), fmt(F["chg_set"]), fmt(F["ocd1"][0]), fmt(F["ocd1"][1]), fmt(F["scd"]),
                fmt(F["pack_pin_share"][0]), fmt(F["pack_pin_share"][1]), fmt(F["xt60_a"])),
        "loss": "R17, F1, the pins, F3, the lead, the pack's FETs and F2 (POWER-THERMAL 7.3's 22.5 mOhm)", "therm": "the cells' windows 0 to 45 C charge, -10 to 60 C discharge (REQ-046); FEA-008 not closed (L4-E10: approach (II) recommended, CONDITIONAL)",
        "prot_a": "D1 SMCJ18A on VBAT; A F1 25 A", "prot_b": "BQ4050 (COV %s V, CUV %s V, OCC, OCD1, SCD, temperatures); BQ7720700; F1 25 A; F2 SCF9550 30 A" % (fmt(F["cov"]), fmt(F["cuv"])),
        "settled": "pcb_pack_protection.yaml, POWER-THERMAL 7, FEA-004 (PWR-F12), L4-E10 (FEA-008, final at 79b2f568)", "checks": [
            Chk("D1's standoff above VBAT's regulated maximum", F["chg_v_max"], "<=", sm18["vr"], "V", "MAKER", "Littelfuse SMCJ18A row; s120 out 7"),
            Chk("D1 not conducting at the SYSOVP maximum", F["sysovp"][2], "<=", sm18["vbr_min"], "V", "MAKER", "TI SLUSE66A p.14; Littelfuse"),
            Chk("the PA keyed alone at 113 W from the %s V rest floor, at a 10.0 V stack, inside the declared peak" % fmt(F["pa_floor"]), F["pa113"][4], "<=", F["pp_peak"], "A", "MODELED", "pwr_budget.out; FW-A05"),
            Chk("PS-ALLTX held under the 18 A peak through a 60 s key-down: the rest voltage it needs at the worst cell resistance under D-11's floor", F["alltx_rest_need"], "<=", F["d11_floor"], "V", "MODELED", "pwr_budget.out D-11 line; FW-A05's floor (PROVISIONAL thresholds)"),
            Chk("OCD1 (%s A for %s s) reached only below a %s V stack, under the 18 A point's %s V" % (fmt(F["ocd1"][0]), fmt(F["ocd1"][1]), fmt(F["alltx_20a_stack"]), fmt(F["alltx_18a_stack"])), F["alltx_20a_stack"], "<", F["alltx_18a_stack"], "V", "MODELED", "pwr_budget.out D-11 line"),
            Chk("the chain's short-time rating at 18 A for 60 s with F2 near +60 C (PWR-F12)", None, "<=", None, "a rating", "CONDITIONAL", "FEA-004: re-declaration and Eaton's answer or the bench owed"),
            Chk("the peak per pack pin with one of four open", F["pack_pin_share"][1], "<=", F["millmax_a"], "A", "MAKER", "IF-AE-DOCK; Mill-Max p.28"),
            Chk("the peak inside the XT60's rating", F["pp_peak"], "<=", F["xt60_a"], "A", "MAKER", "Amass XT60 sheet"),
            Chk("the cells' temperature design against REQ-046 with the pack fitted (FEA-008, DR-06): L4-E10 recommends a wide-temperature 18650 in D-06's 4S3P, CONDITIONAL on its signed specification and the owner's approval (D-06 to about %s Wh nominal)" % fmt(F["cell_nom"][1]),
                None, "<=", None, "a design and the owner's two items", "CONDITIONAL", "L4-E10 out 5 (closing check 573c8b8f): FEA-008 not closed; LO-01a CONDITIONAL on T-H1 at least %s W/K, LO-01d to g OPEN; unresolved choice U-01" % fmt(F["th1"])),
        ]})
    R.append({
        "id": "IF-11", "title": "VBAT to the load converters (slot rails, device rail, logic, monitor, heater; board E's always-on on CELL_F)",
        "a": "VBAT", "b": "the 39 loads of PS-IDLE-SPEC and the PS-ALLTX set",
        "v": "%s to %s V | the converters assumed to run to %s V (SHORTLIST.md 2, not shown)" % (fmt(D["vbat_low"]), fmt(F["chg_v_max"]), fmt(D["vbat_low"])),
        "i": "asked: PS-IDLE-SPEC %s / %s / %s W; PS-ALLTX %s / %s / %s W (low / plan / high at the pack terminals); %s W of PS-IDLE-SPEC has no document | available: each converter's own rating (pwr_budget.py)"
             % (fmt(F["idle"][0]), fmt(F["idle"][1]), fmt(F["idle"][2]), fmt(F["alltx"][0]), fmt(F["alltx"][1]), fmt(F["alltx"][2]), fmt(F["undoc_w"])),
        "loss": "the converters' makers' floors (pwr_budget.py)",
        "therm": "the heat per state, POWER-THERMAL 9 (conductance unmeasured, FEA-004); at L4-E10's conditioned corner the inside air %.2f C (E3-O) and %.2f C (E5), plus at most %s K from L4-E8's ballasts" % (F["corner_air"][0], F["corner_air"][1], fmt(round(F["ballast_w"] / F["th1"], 2))),
        "prot_a": "the eFuses (monitor %s A peak declared, heater) and the stages' limits" % fmt(F["vmon"]["peak"]), "prot_b": "each converter's own",
        "settled": "pwr_budget.out, load_trace.out, POWER-THERMAL", "checks": [
            Chk("the profile's %s W with no document measured or bounded by a maker" % fmt(F["undoc_w"]), None, "<=", None, "a measurement", "ASSUMPTION", "load_trace.out; replay out 13"),
            Chk("the inside air at L4-E10's conditioned corner (T-H1 at %s W/K, E5's +60 C dwell) under the +%s C parts (SA868, AW7915-AED, LimeSDR, Xenarc; MESHSAT-1478)" % (fmt(F["th1"]), fmt(F["parts_hot"])),
                F["corner_air"][1], "<=", F["parts_hot"], "C", "CONDITIONAL", "L4-E10 out 3o (MODELED at the enclosure's floor; E3-O %.2f C); unresolved choice U-02" % F["corner_air"][0]),
            Chk("every load converter runs to the 3.00 V line (10.0 V stack)", None, "<=", None, "a record", "ASSUMPTION", "SHORTLIST.md 2: no record"),
            Chk("TPS2596 eFuses (U21, U22) on VBAT at the SYSOVP maximum", F["sysovp"][2], "<=", F["tps2596_abs"], "V", "MAKER", "TI TPS2596 7.1"),
        ]})
    pd = F["pd"]
    R.append({
        "id": "IF-12", "title": "VBAT to the USB-C outlet (U19 LM5176, Q27, R138, J_USBC_OUT; U18 TPS25740A), the tablet's optional charge",
        "a": "VBAT", "b": "the outlet's sink (a tablet), 5, 9 and 15 V at 3 A",
        "v": "VBAT %s to %s V into U19 | 5 / 9 / %s V contracts, each held inside the maker's window (L4-E4 bench (a))" % (fmt(D["vbat_low"]), fmt(F["chg_v_max"]), fmt(pd["volts"])),
        "i": "asked: %s A each PDO; with PS-TYP %s W plan (%s W at the outlet), %s A at 14.4 V | available: R138 5 mOhm trip %s to %s A; U19's own limit %s to %s A; the Bulgin receptacle %s A; Q27 %s A; J_USBC_OUT no rating held"
             % (fmt(F["pdo_a"]), fmt(F["typ_usbc"][0]), fmt(F["typ_usbc"][2]), fmt(F["typ_usbc"][4]), fmt(F["trip"][0]), fmt(F["trip"][1]), fmt(F["u19_lim"][0]), fmt(F["u19_lim"][2]), fmt(F["recept_a"]), fmt(F["q27_a"])),
        "loss": "U19 0.93 DECLARED", "therm": "inside air %s C" % fmt(F["air"][1]),
        "prot_a": "OUTLET_OK interlock (off while the PA keys, CON-019); C2's shed at 9.0 A", "prot_b": "U18's OCP over R138 (15 us); fast and slow OVP",
        "settled": "l4e4 (R138, bench a and b)", "checks": [
            Chk("every PDO below the trip window's minimum (the 3 A row; bench (a) decides the row)", F["pdo_a"], "<", F["trip"][0], "A", "CONDITIONAL", "l4e4 out 3: VI(TRIP)'s label"),
            Chk("the trip maximum inside the receptacle", F["trip"][1], "<=", F["recept_a"], "A", "MAKER", "l4e4 out 3; Bulgin"),
            Chk("the trip maximum inside Q27", F["trip"][1], "<=", F["q27_a"], "A", "MAKER", "TI SLPS632"),
            Chk("J_USBC_OUT's VBUS pin with a maker's rating at or above the trip maximum (a 2.54 mm pin, no part number)", None, "<=", None, "a rating", "ASSUMPTION", "l4e4: INCONCLUSIVE; register R-30 (Layer 6)"),
            Chk("PS-TYP with the outlet inside the declared continuous pack current at 14.4 V", F["typ_usbc"][4], "<=", F["pp_cont"], "A", "MODELED", "pwr_budget.out"),
        ]})
    poe = F["poe"]
    R.append({
        "id": "IF-13", "title": "VBAT through R227 to the PoE stage (U16 LM5176 boost, R71, +54V_POE, J_54V to board B) and its monitor U17",
        "a": "VBAT", "b": "+54V_POE at %s A peak (REQ-017)" % fmt(poe["peak"]),
        "v": "VBAT %s to %s V regulated, %s V at the pack-open bound, %s V at D1's rated pulse, into R227 and U16 (POE_VIN at most %s V under VBAT) | %s V; U17 (INA226) IN+ on VBAT, IN- and VBUS on POE_VIN (part A; as drawn on POE_OUT and +54V_POE, pins %s and %s); INA226 %s V absolute, %s V common mode"
             % (fmt(D["vbat_low"]), fmt(F["chg_v_max"]), fmt(round(D["pack_open"]["v_end"], 3)), fmt(F["SMCJ18A"]["vc"]), fmt(round(A["u17_mv_fault"] * 1e-3, 3)), fmt(poe["volts"]),
                "/".join(F["u17_nets"]["POE_OUT"]) or "none", "/".join(F["u17_nets"]["+54V_POE"]) or "none", fmt(F["ina_abs"]), fmt(F["ina_cm_op"])),
        "i": "asked: %s / %s A at 54 V, the stage's input at a %s V stack %s A (%s mV over R227), at its fault bound %s A (%s mV); PS-TYP plus PoE %s W plan (%s W outside) | available: R227 5 mOhm %s W (%s W at %s C); the INA226's %s mV full scale (%s A); U16's limits"
             % (fmt(poe["typ"]), fmt(poe["peak"]), fmt(D["vbat_low"]), fmt(round(D["poe_in"], 3)), fmt(round(A["u17_mv_norm"], 2)), fmt(round(A["u17_fault_a"], 2)), fmt(round(A["u17_mv_fault"], 2)),
                fmt(F["typ_poe"][0]), fmt(F["typ_poe"][2]), fmt(A["hojlr"][0]), fmt(round(A["hojlr_avail"], 2)), fmt(F["air"][1]), fmt(F["ina_fs_mv"]), fmt(round(A["u17_fs_a"], 3))),
        "loss": "U16 %s (the generator's figure outside the maker's plots); R227 at most %s W at the stage's peak input" % (fmt(poe["efficiency"]), fmt(round(D["poe_in"] ** 2 * 0.005 * 1.01, 4))),
        "therm": "inside air %s C" % fmt(F["air"][1]),
        "prot_a": "OUTLET_OK interlock", "prot_b": "U16's average limit (R71) and cycle limit (R72); board B's TPS23861 port limit",
        "settled": "HW-FW-CONTRACT HF-F02 (S-60), this record (part A, apply_gen_sch_a_u17.py)", "checks": [
            Chk("U17's inputs at the rail (HF-F02)", poe["volts"], "<=", F["ina_abs"], "V", "MAKER", "TI SBOS547 5.1", scope="drawn"),
            Chk("U17's common mode on VBAT at its highest bound (the pack-open bound, above SYSOVP's maximum)", round(max(F["sysovp"][2], D["pack_open"]["v_end"]), 3), "<=", F["ina_cm_op"], "V", "MAKER", "TI SBOS547 CMRR condition and bus range"),
            Chk("U17's common mode at D1's rated pulse on VBAT", F["SMCJ18A"]["vc"], "<=", F["ina_cm_op"], "V", "MAKER", "Littelfuse SMCJ18A row; TI SBOS547"),
            Chk("R227's drop at the stage's peak input at the lowest stack inside the full scale", round(A["u17_mv_norm"], 2), "<=", F["ina_fs_mv"], "mV", "INFERRED", "the declared 0.6 A at 54 V over 0.88; R227 at +1 %"),
            Chk("R227's drop at the stage's fault bound (U16's boost peak limit over R72) inside the full scale", round(A["u17_mv_fault"], 2), "<=", F["ina_fs_mv"], "mV", "INFERRED", "part A; SNVSAI1D VCS(BOOST)"),
            Chk("R227's dissipation at that bound inside its derated rating", round(A["u17_p_fault"], 3), "<=", round(A["hojlr_avail"], 2), "W", "MAKER", "HoJLR2512 p.2 (through L4-E8)"),
        ]})
    pa = F["pa"]
    R.append({
        "id": "IF-14", "title": "VBAT to the PA rail (+13V8_PA, J_PA) with the PA keyed",
        "a": "VBAT", "b": "the RA30H1317M1 PA, %s V" % fmt(pa["volts"]),
        "v": "VBAT %s to %s V into U13 | %s V; PA_EN gated by EMCON and TX_INHIBIT_n" % (fmt(D["vbat_low"]), fmt(F["chg_v_max"]), fmt(pa["volts"])),
        "i": "asked: the drain 5.4 to 8.2 A, not characterised (F-PR-02); PS-IDLE-SPEC plus the PA at 113 W %s W, %s A at 10.0 V | available: declared %s / %s A, the stage's average loop 7.2 to 9.5 A"
             % (fmt(F["pa113"][0]), fmt(F["pa113"][4]), fmt(pa["typ"]), fmt(pa["peak"])),
        "loss": "U13 %s" % fmt(pa["efficiency"]), "therm": "key-down at most 60 s, flange gates +75 C and +85 C (D-11, PROVISIONAL)",
        "prot_a": "the K rules (FW-A05), the outlets dropped by OUTLET_OK", "prot_b": "the stage's limit",
        "settled": "POWER-THERMAL 7.2, FEA-004", "checks": [
            Chk("the PA keyed alone at 113 W within the pack's declared peak at the 10.0 V stack", F["pa113"][4], "<=", F["pp_peak"], "A", "MODELED", "pwr_budget.out"),
            Chk("the PA's drain current against the rail's declared peak (F-PR-02, not characterised)", 8.2, "<=", 9.5, "A", "ASSUMPTION", "POWER-THERMAL 7.3: the stage's loop band"),
        ]})
    return R


# ------------------------------------------------------------------------------------------------------- the gate
GATE = [
    {"n": 1, "criterion": "one architecture selected, its mandatory functions with a defensible feasibility basis",
     "rows": ["IF-02", "IF-04", "IF-07", "IF-09", "IF-10", "IF-11", "IF-12", "IF-13"], "choices": ["U-01", "U-02", "U-03"], "verdict": "CONDITIONAL",
     "constraint": "the solar function's 100 W bound is CONDITIONAL on G_CM and U18's VIN+ bias (L4-E7R) and its source on O-1 (U-03); PS-ALLTX's chain "
                   "at 18 A for 60 s (PWR-F12) is an open obligation; the battery path's thermal design (FEA-008, U-01) and the electronics' inside air at "
                   "the enclosure's floor (MESHSAT-1478, U-02) are unresolved choices",
     "overturn": "possibly: U-01 and U-02 could change D-06's pack or the sealed case's thermal design; the rest resolves by a value, a part or a "
                 "measurement on the same topology"},
    {"n": 2, "criterion": "material power-path defects have engineering resolutions and bounded supporting calculations",
     "rows": ["IF-01", "IF-02", "IF-04", "IF-13"], "choices": [], "verdict": "CONDITIONAL",
     "constraint": "one material defect is open, D-01: under TEST-PLAN M2 (CS101) the injected current crosses the solar entry's sense bank and the "
                   "backstop trips, stopping solar charging against M2's 'no upset' line; the fix, an INB filter or a ripple-shunt capacitor ahead of "
                   "the bank on the same topology, is L4-E7R's bounded follow-up (PENDING)",
     "overturn": "no: a filter or a capacitor on the same topology"},
    {"n": 3, "criterion": "remaining assumptions explicit, with their impact and verification method",
     "rows": [], "choices": [], "verdict": "PASS", "constraint": "", "overturn": ""},
    {"n": 4, "criterion": "downstream implementation changes, layout constraints and tests have named owners and acceptance criteria",
     "rows": [], "choices": [], "verdict": "PASS", "constraint": "", "overturn": ""},
    {"n": 5, "criterion": "no unresolved uncertainty could overturn the selected architecture while described as routine later testing",
     "rows": ["IF-01", "IF-10", "IF-11"], "choices": ["U-01", "U-02", "U-03"], "verdict": "CONDITIONAL",
     "constraint": "three unresolved choices could overturn it and are named as such, not as later testing: U-01 (FEA-008's cell), U-02 "
                   "(MESHSAT-1478, the inside air against the +70 C parts), U-03 (O-1, a panel with a supported cold open circuit); an owner and an "
                   "acceptance criterion do not close them",
     "overturn": "yes for U-01 and U-02 (D-06's pack, the sealed case's thermal design); U-03 decides the solar source, not the topology"},
]

# The unresolved choices that could overturn the architecture (category b). An owner and an acceptance criterion close an
# assignment, never one of these: each stays open, and keeps every criterion that names it from PASS, until its evidence lands.
CHOICES = [
    {"id": "U-01", "title": "FEA-008: the battery path's cell and thermal design (L4-E10, final)",
     "constraint": "LO-01d to LO-01g (E3-O, E5, E3-S, E4-S with the pack fitted) have no route that holds on held evidence; LO-01a holds only with "
                   "T-H1 at least 1.666 W/K in both lid states",
     "settles": "the HL18650V's signed specification confirming storage at +71 C and -33 C at the stored charge and the +80 C idle limit, then L4-E10's "
                "margins re-run (1.06 K under H1 and 0.97 K under U2's INFERRED trip at LO-01e); T-H1 measured in both lid states",
     "alternatives": "(II) a wide-temperature 18650 in D-06's 4S3P (recommended, CONDITIONAL); (I) the 35E with powered cooling (INCONCLUSIVE: up to "
                     "35 W into the sealed case); (III) latent storage and a primary-fed heater (rejected at LO-01d to f; added energy storage under D-06); "
                     "a requirement change (the owner's, D-29)",
     "owner": "(1) send the drafted request for the specification; (2) once it confirms, approve the cell change (D-06's about 145 Wh to about 121 Wh "
              "nominal, REQ-046 and REQ-077 restated with the cell, about USD 42 a pack); if declined, LO-01d to g stay a release gate",
     "overturns": "D-06's pack energy (16.4 % less usable) and the pack's protection settings; the power path's topology stays",
     "rows": ["IF-10"]},
    {"id": "U-02", "title": "MESHSAT-1478: the inside air at the enclosure's floor against the +70 C parts",
     "constraint": "at T-H1's 1.666 W/K floor the uncooled inside air is 70.00 C in E3-O and tends to 75.00 C in E5's +60 C dwell (L4-E10, MODELED), "
                   "plus up to 1.25 K from L4-E8's ballasts, at or past the +70 C ratings of the SA868, the AW7915-AED cards, the LimeSDR and the Xenarc",
     "settles": "T-H1 measured in both lid states and the parts' temperatures in E3-O and E5 on the prototype, or a thermal design whose modelled inside "
                "air stays under +70 C at those levels",
     "alternatives": "an enclosure conductance above LO-01a's floor (the plate, the fans, the case); parts rated past +70 C; D-02a's +55 C margin and E5 "
                     "restated (the owner's, D-29); a reduced mode at those levels",
     "owner": "none yet: an architecture-level thermal question for the kit's thermal owner (MESHSAT-1478); a requirement change would be the owner's",
     "overturns": "the sealed case's thermal design (no vent, the ruling of 7 September 2026) or D-02a's margin; not the power path's topology",
     "rows": ["IF-11"]},
    {"id": "U-03", "title": "O-1: a solar panel with a supported maximum open circuit inside REQ-016's window",
     "constraint": "REQ-016 admits a panel only with an open circuit at or below 25 V at -20 C; the candidate's nominal sheet gives 24.05 V and no "
                   "supported maximum (source compliance INCONCLUSIVE)",
     "settles": "a panel maker's stated maximum, or a measured lot, at -20 C at or under 25 V",
     "alternatives": "the SPR-E-Flex-100 with the maker's tolerance; another panel inside the window; REQ-016's window restated (the owner's)",
     "owner": "none until a panel is pinned",
     "overturns": "which panel the mandatory solar function uses; the stage and the window stay",
     "rows": ["IF-01"]},
]

# The material power-path defects (criterion 2), open or resolved this round.
DEFECTS = [
    {"id": "D-01", "title": "the solar backstop trips under TEST-PLAN M2 (CS101)", "state": "OPEN",
     "constraint": "CS101's injected current, up to 1.91 A rms at 1 kHz and above, crosses the sense bank; its peaks over the trip less the operating "
                   "current stop the stage for td (at least 180 ms) each time, so solar charging stops for the test, against M2's 'no upset' line",
     "options": "an INB filter (the coordinator's estimate: a corner near 180 Hz, crossing the trip in about 0.2 ms on a step, inside the 3.783 ms "
                "allowance) or a ripple-shunt capacitor ahead of the bank (its charge bounded by C V squared in check (b), surge-rated)",
     "resolution": "L4-E7R's bounded follow-up on fnd/l4e7 (PENDING)", "rows": ["IF-01", "IF-02"]},
    {"id": "D-02", "title": "the vehicle entry's hot swap opens under TEST-PLAN M2 (CS101) at REQ-015's 36 V", "state": "RESOLVED (draft owed)",
     "constraint": "36 V plus CS101's 2.83 V peak reaches 38.83 V, past the drawn OVLO minimum 37.78 V",
     "options": "R22 100k and R23 6.42k, both 0.1 %: OVLO 39.71 / 41.44 / 43.18 V (selected, SESSION); M2 at the source's nominal (not taken)",
     "resolution": "register R-94 (MISSING DRAFT)", "rows": ["IF-04"]},
    {"id": "D-03", "title": "Q1 over its rating on a reversed input with the raised ceiling", "state": "RESOLVED (drafted)",
     "constraint": "66.15 V across the drawn 60 V BSC039N06NS", "options": "the CSD19532Q5B (100 V)",
     "resolution": "register R-17, apply_gen_sch_e_q1.py", "rows": ["IF-04"]},
    {"id": "D-04", "title": "F1 cannot interrupt at the entry's highest steady input", "state": "RESOLVED (drafted)",
     "constraint": "the drawn 32 V DC MINI against 43.18 V", "options": "the Littelfuse 0997010.WXN (58 V DC, 1000 A at 58 V DC)",
     "resolution": "register R-18, apply_gen_sch_e_f1.py", "rows": ["IF-04"]},
    {"id": "D-05", "title": "U17 on the 54 V rail (HF-F02)", "state": "RESOLVED (drafted)",
     "constraint": "54 V on the INA226's IN+ and IN- against its 40 V absolute", "options": "U17 on R227, 5 mOhm in the PoE stage's input",
     "resolution": "register R-06, apply_gen_sch_a_u17.py", "rows": ["IF-13"]},
]
OWNERS = ["Layer 4 coordinator", "Layer 5 interfaces", "Layer 6 components", "Layer 7 mechanical", "Layer 8 board A generator owner",
          "Layer 8 board E generator owner", "Layer 8 board P generator owner", "Layer 9 pre-layout analysis", "prototype bench",
          "firmware owner", "TEST-PLAN owner", "Layer 8 board B generator owner"]


def gate_violations(gate, st):
    """The criteria marked PASS that rest on a row not reading MEETS, or on an ASSUMPTION, CONDITIONAL or PENDING row; and
    the criteria naming a row the reconciliation does not print. The closure gate's rule, held by test_l4e9.py too."""
    bad = []
    for g in gate:
        for rid in g["rows"]:
            if rid not in st:
                bad.append((g["n"], "unknown row %s" % rid))
        if g["verdict"] == "PASS":
            for rid in g["rows"]:
                cls, s = st.get(rid, ("PENDING", "PENDING"))
                if s != "MEETS" or cls in ("ASSUMPTION", "CONDITIONAL", "PENDING"):
                    bad.append((g["n"], "%s reads %s, %s" % (rid, s, cls)))
        elif not g["constraint"] or not g["overturn"]:
            bad.append((g["n"], "a criterion not PASS names no constraint or no overturn answer"))
    if sorted(g["n"] for g in gate) != [1, 2, 3, 4, 5]:
        bad.append((0, "the gate does not cover the five criteria"))
    ids = {c["id"] for c in CHOICES}
    for g in gate:
        for cid in g.get("choices", []):
            if cid not in ids:
                bad.append((g["n"], "unknown choice %s" % cid))
            elif g["verdict"] == "PASS":
                bad.append((g["n"], "PASS while the unresolved choice %s stands" % cid))
        if g["n"] == 2 and g["verdict"] == "PASS" and any(d["state"] == "OPEN" for d in DEFECTS):
            bad.append((2, "PASS while a material defect is open"))
    for c in CHOICES:
        if not all(c.get(k) for k in ("constraint", "settles", "alternatives", "owner", "overturns", "rows")):
            bad.append((0, "choice %s lacks a field" % c["id"]))
    return bad


def md_table(text, header_start):
    """The rows of the first markdown table whose header line starts with header_start."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith(header_start):
            out = []
            for l2 in lines[i + 2:]:
                if not l2.startswith("|"):
                    break
                out.append([c.strip() for c in l2.strip().strip("|").split("|")])
            return out
    return []


def main():
    F, where = compute()
    D = derived(F)
    A = partA(F, D, _C_TEXT)
    R = rows(F, D, A)
    st = {r["id"]: row_status(r) for r in R}
    for r in R:
        for k in ("v", "i"):
            if r[k].count(" | ") != 1 or not all(x.strip() for x in r[k].split(" | ")):
                refuse(4, "%s's %s does not give both sides" % (r["id"], k))
        if not r["settled"] or not r["checks"] or not r["a"] or not r["b"]:
            refuse(4, "%s has no settling record, check or side" % r["id"])
    out = []
    p = out.append
    p("L4-E9: THE CONNECTED POWER ARCHITECTURE AND LAYER 4'S CLOSURE GATE (MESHSAT-1357, 1 October 2026; round 2, 2 October 2026). Prototype")
    p("design, desk arithmetic:")
    p("nothing is bought, built, powered or measured. Every figure is read from a generator, a committed netlist, a record's committed")
    p("output or a maker's document, each pinned by sha256; the few this record sets itself are named. Classes: MAKER, NETLIST, MODELED,")
    p("INFERRED, CONDITIONAL, ASSUMPTION, PENDING.")
    p("")
    p("0. INPUTS (sha256/16, where read)")
    for key, (rel, _) in PINS.items():
        w, h = where[key]
        p("   %-9s %s  %s%s" % (key, h[:16], rel, "" if w == "tree" else "  (" + w + (", fnd/l4e8 accepted)" if key in FROM_L4E8 else ", " + FROM_LABEL[key] + ")")))
    p("   pending: %s" % L4E7R)
    p("   this record's own figures: copper %s ohm mm2/m at 20 C and %s /K, 18 AWG %s mm2 (ASSUMPTION, constants); the cold end %s C (REQ-024);"
      % (fmt(CU_RHO_20C), fmt(CU_ALPHA), fmt(AWG18_MM2), fmt(T_COLD)))
    p("     capacitance kept under bias %s (ASSUMPTION; the bound states the fraction it needs); the back-feed diode's drop %s V (an upper bound);"
      % (fmt(BIAS_KEEP), fmt(VF_BACKFEED)))
    p("     the charger's L2 +-%s %% (Coilcraft XAL family)" % fmt(L2_TOL * 100))
    p("")
    p("1. THE MAKERS' ROWS (pdftotext, the page cited)")
    p("   LM5176 (SNVSAI1D 6.1): VIN, VISNS %s V absolute. LM74700-Q1 (SNOSD17G 6.1, 6.3): CATHODE to ANODE %s V absolute, ANODE to"
      % (fmt(F["u2_vin_abs"]), fmt(F["ld_ca_abs"])))
    p("     CATHODE -%s V recommended, ANODE %s V. CSD19532Q5B %s V; BSC039N06NS %s V. LM5069 (SNVS452G 7.1, 7.5): VIN %s V absolute, VCL %s / %s / %s mV."
      % (fmt(F["ld_ac_rec"]), fmt(F["ld_anode_abs"]), fmt(F["csd19532_vds"]), fmt(F["bsc039_vds"]), fmt(F["lm5069_vin_abs"]), fmt(F["vcl"][0]), fmt(F["vcl"][1]), fmt(F["vcl"][2])))
    for part in ("SMCJ18A", "SMCJ22A", "SMCJ28A", "SMCJ40A"):
        q = F[part]
        p("   Littelfuse %s: VR %s V, VBR %s to %s V at 1 mA, VC %s V at %s A" % (part, fmt(q["vr"]), fmt(q["vbr_min"]), fmt(q["vbr_max"]), fmt(q["vc"]), fmt(q["ipp"])))
    p("   TPS2596 (7.1): VIN %s V absolute. INA226 (SBOS547 5.1): VBUS, IN+ and IN- %s V absolute; common mode %s V (CMRR row); full scale %s mV."
      % (fmt(F["tps2596_abs"]), fmt(F["ina_abs"]), fmt(F["ina_cm_op"]), fmt(F["ina_fs_mv"])))
    p("   BQ25731 (SLUSE66A p.8, p.14): VBUS, VSYS %s V absolute; SYSOVP %s / %s / %s V. Littelfuse 297 MINI: %s V DC, %s A interrupting."
      % (fmt(F["u3_abs"]), fmt(F["sysovp"][0]), fmt(F["sysovp"][1]), fmt(F["sysovp"][2]), fmt(F["f297_v"]), fmt(F["f297_i"])))
    p("   JST VH p.1: %s A at AWG 16 with the standard header; %s A at AWG 18 with the shrouded header only. Mill-Max p.28: %s A continuous (0850 to"
      % (fmt(F["vh_16"]), fmt(F["vh_18"]), fmt(F["millmax_a"])))
    p("     0853, the 0858's sibling figure). Amass XT60: %s A rated." % fmt(F["xt60_a"]))
    p("")
    p("2. THE GENERATORS' DECLARATIONS (syntax tree)")
    for k, nm in (("vbat", "A VBAT"), ("vin_raw_a", "A VIN_RAW"), ("vbus20", "A VBUS20"), ("pa", "A +13V8_PA"), ("hf", "A +12V_HF"), ("poe", "A +54V_POE"),
                  ("pd", "A PD_VBUS"), ("vmon", "A VMON"), ("vheat", "A VHEAT"), ("vin_raw_e", "E VIN_RAW"), ("pv", "E PV_P"), ("trk", "E TRK_OUT"),
                  ("cell_f", "E CELL_F"), ("p_pack", "P PACK_P")):
        r = F[k]
        extra = "".join(", %s %s" % (kk, fmt(r[kk])) for kk in ("v_work", "v_max", "efficiency") if r.get(kk) is not None)
        p("   %-11s %s V, %s A typical, %s A peak%s" % (nm, fmt(r["volts"]), fmt(r["typ"]), fmt(r["peak"]), extra))
    p("   parts: A F1 '%s'; A D1 '%s'; A D2 '%s'" % (F["a_f1"], F["a_d1"][:40], F["a_d2"][:40]))
    p("     E F1 '%s'; E F2 '%s'; E D10 '%s'" % (F["e_f1"], F["e_f2"], F["e_d10"][:40]))
    p("     E Q1 (ideal_diode) '%s'; E Q7 '%s'" % (F["e_q1"][:44], F["e_q7"][:44]))
    p("     E R19 '%s'; R21 '%s'; R23 '%s'; R10 '%s'" % (F["e_r19"][:30], F["e_r21"], F["e_r23"], F["e_r10"]))
    p("     P F1 '%s'; P F2 '%s'" % (F["p_f1"][:44], F["p_f2"][:44]))
    p("   board A's netlist: VBAT carries %d capacitors, %s uF nominal; D1 on VBAT: %s; U17's pins on POE_OUT %s and on +54V_POE %s"
      % (F["vbat_caps"][0], fmt(round(F["vbat_caps"][1], 2)), "yes" if F["vbat_d1_on_net"] else "no", F["u17_nets"]["POE_OUT"], F["u17_nets"]["+54V_POE"]))
    p("")
    p("3. THE RECORDS' FIGURES (each read from the line that prints it)")
    p("   L4-E4: the window %s W at VBUS20 needs %s A; IIN_HOST %s A (minimum %s A, maximum %s A board current, %s A through R11); U3's own %s A"
      % (fmt(F["win_w"]), fmt(F["win_need"]), fmt(F["iin_host"]), fmt(F["u3_min"]), fmt(F["u3_max_board"]), fmt(F["r11_need"]), fmt(F["u3_max_u3"])))
    p("     R11 8 mOhm band %s / %s / %s A, 7 mOhm %s / %s / %s A; at 62.1 C with C-1's taps %s A (+%s A); R138 trip %s to %s A; U19 %s / %s / %s A"
      % (*[fmt(x) for x in F["r11_8"]], *[fmt(x) for x in F["r11_7"]], fmt(F["r11_min_62_full"]), fmt(F["r11_margin_62_full"]), fmt(F["trip"][0]), fmt(F["trip"][1]), *[fmt(x) for x in F["u19_lim"]]))
    p("   L4-E5 (H3): U3 effective maximum and the front end's input maximum at 9 / 12 / 24 / 36 V: %s"
      % "; ".join("%s A, %s A (%s %%)" % (fmt(F["h3"][v][0]), fmt(F["h3"][v][1]), fmt(F["h3"][v][2])) for v in (9.0, 12.0, 24.0, 36.0)))
    p("     HIZ certain below %s V, out of HIZ above %s V, regulation by the pin from %s V; U3 at least %s A at 9.0 V; ceiling %s / %s / %s V (drawn %s / %s / %s V)"
      % (fmt(F["hiz_below"]), fmt(F["hiz_out_above"]), fmt(F["pin_reg_from"]), fmt(F["u3_at_9"]), *[fmt(x) for x in F["trk_ceiling"]], *[fmt(x) for x in F["trk_drawn"]]))
    p("     the entry %s to %s A (basis %s A), timer %s / %s / %s ms; restart guard %s / %s / %s V; pin path %s A (V-A07 %s A); FE input under 4.80 A while the 9 V efficiency is at least %s"
      % (fmt(F["entry_lim"][0]), fmt(F["entry_lim"][1]), fmt(F["entry_basis"]), *[fmt(x) for x in F["timer_ms"]], *[fmt(x) for x in F["latch"]], fmt(F["pin_path"]), fmt(F["pin_err_allow"]), fmt(F["eff_floor_9v"])))
    p("     on the candidate panel H3 gives up %s to %s Wh a day; A2 unserved %s to %s Wh (48 h), %s to %s Wh (72 h)"
      % (fmt(F["h3_cand_given"][0]), fmt(F["h3_cand_given"][1]), *[fmt(x) for x in F["h3_cand_a2"]]))
    p("   L4-E6: R12 12 mOhm peak %s / %s / %s A; service peak %s A; 9 V: L1 %s A average, output %s A; 15.1 V L1 %s A; average limit above %s V;"
      % (*[fmt(x) for x in F["r12_peak"]], fmt(F["svc_peak"]), fmt(F["fe_in_9v"]), fmt(F["fe_out_9v"]), fmt(F["fe_in_151"]), fmt(F["avg_from"])))
    p("     L1 peak bound %s A (%s %% of %s A), Isat needed %s A at %s C; FETs at most %s C; the bus %s V, efficiency %s"
      % (fmt(F["l1_peak"]), fmt(F["l1_pct"]), fmt(F["l1_isat"]), fmt(F["l1_need"]), fmt(F["l1_qual"]), fmt(F["fet_tj"]), fmt(F["vbus_max_r11"]), fmt(F["eta_fe"])))
    p("   L4-E7R (237cd9be): the regulation %s A nominal, %s A highest (%s / %s W in at the hold); the backstop trips at %s to %s A at 25 V; static bound"
      % (fmt(F["reg"][0]), fmt(F["reg"][1]), fmt(F["reg_w"][0]), fmt(F["reg_w"][1]), fmt(F["bs_trip"][0]), fmt(F["bs_trip"][1])))
    p("     %s W (CONDITIONAL), the regulation's 25 V corner %s W; %s ms allowance; SWEN off below %s V; U5's differential %s V; the hot short circuit %s A;"
      % (fmt(F["static_bound"]), fmt(F["reg_corner"]), fmt(F["bs_allow_ms"]), fmt(F["swen_v"]), fmt(F["u5_diff"]), fmt(F["isc_hot_tol"])))
    p("     energy %s / %s / %s Wh (SC-37), %s Wh (bright day); the bank %s / %s Wh; CS101 puts %s A rms across the bank; hold %s / %s / %s V, conditioned"
      % (*[fmt(x) for x in F["e7r_day"]], fmt(F["e7r_bright"]), fmt(F["bank_wh"][0]), fmt(F["bank_wh"][1]), fmt(F["cs101_bank_a"]), *[fmt(x) for x in F["hold"]]))
    p("     %s to %s V; U5 about %s C" % (fmt(F["hold_cond"][0]), fmt(F["hold_cond"][1]), fmt(F["u5_tj"])))
    p("   L4-E10 (79b2f568): FEA-008 not closed; (II) recommended, CONDITIONAL; T-H1 at least %s W/K; the conditioned corner's air %.2f C (E3-O), %.2f C (E5),"
      % (fmt(F["th1"]), F["corner_air"][0], F["corner_air"][1]))
    p("     the +%s C parts; usable %s Wh (35E) and %s Wh (HL18650V, %s %% less), %s Wh nominal against %s; the kit's heat at E3-O's corner %s W (INFERRED)"
      % (fmt(F["parts_hot"]), fmt(F["cell_usable"][0]), fmt(F["cell_usable"][1]), fmt(F["cell_less_pct"]), fmt(F["cell_nom"][1]), fmt(F["cell_nom"][0]), fmt(round(F["corner_heat"], 2))))
    p("     LO-01e under (II): the cells %s C, %s K under the page's limit, %s K under the re-derived H1 and %s K under U2's INFERRED trip;"
      % (fmt(F["lo01e"][0]), fmt(F["lo01e"][1]), fmt(F["lo01e"][2]), fmt(F["lo01e"][3])))
    p("     USD %s a cell, so about USD %s a 4S3P pack of 12 (a marketplace price)" % (fmt(F["cell_usd"]), fmt(round(F["cell_usd"] * 12))))
    p("   L4-E8: every can at most %s A against %s A (8 mOhm), %s against %s A (7 mOhm); ballasts at most %s W (%s W at the nominal illustration)"
      % (fmt(F["can8"][0]), fmt(F["can8"][1]), fmt(F["can7"][0]), fmt(F["can7"][1]), fmt(F["ballast_w"]), fmt(F["ballast_nom_w"])))
    p("   s120: VBUS20 %s to %s V, bound %s V; OVLO %s / %s / %s V; ChargeVoltage at most %s V; BATOVP %s V; ACOV %s V minimum"
      % (fmt(F["vbus_band"][0]), fmt(F["vbus_band"][1]), fmt(F["vbus_bound"]), *[fmt(x) for x in F["ovlo"]], fmt(F["chg_v_max"]), fmt(F["batovp"]), fmt(F["acov_min"])))
    p("     the selected OVLO (R23 6.42k, R22 100k, both 0.1 %%): %s / %s / %s V (this record, part A)" % tuple(fmt(round(x, 2)) for x in F["ovlo_sel"]))
    p("   the budget: PS-IDLE-SPEC %s / %s / %s W; PS-ALLTX %s / %s / %s W; the PA keyed alone at 113 W %s W, %s A at 10.0 V; PS-TYP plus USB-C %s W"
      % (*[fmt(x) for x in F["idle"]], *[fmt(x) for x in F["alltx"]], fmt(F["pa113"][0]), fmt(F["pa113"][4]), fmt(F["typ_usbc"][0])))
    p("   the pack: %s A continuous, %s A peak; prospective %s to %s A; OCD1 %s A for %s s; OCC %s A; SCD %s A; COV %s V, CUV %s V; inside air %s / %s C (lid open / closed)"
      % (fmt(F["pp_cont"]), fmt(F["pp_peak"]), fmt(F["pp_fault"][0]), fmt(F["pp_fault"][1]), fmt(F["ocd1"][0]), fmt(F["ocd1"][1]), fmt(F["occ"]), fmt(F["scd"]), fmt(F["cov"]), fmt(F["cuv"]), fmt(F["air"][0]), fmt(F["air"][1])))
    p("")
    p("4. THE INTERFACE ROWS (the selected architecture: A1, with L4-E4 to L4-E8 applied and this record's changes; 'as drawn' checks show a defect")
    p("   the selected design resolves). Each row: both sides' ranges, the currents at the modes, losses, thermal, protection, the record that settles it.")
    for r in R:
        cls, s = st[r["id"]]
        p("   %s  %s  [%s, %s]" % (r["id"], r["title"], s, cls))
        p("     sides: %s | %s" % (r["a"], r["b"]))
        p("     voltage: %s" % r["v"])
        p("     current: %s" % r["i"])
        p("     losses: %s; thermal: %s" % (r["loss"], r["therm"]))
        p("     protection: %s | %s" % (r["prot_a"], r["prot_b"]))
        p("     settled by: %s" % r["settled"])
        for c in r["checks"]:
            p("       - " + c.line())
    counts = {}
    for r in R:
        counts[st[r["id"]][1]] = counts.get(st[r["id"]][1], 0) + 1
    p("   rows: %d; %s" % (len(R), ", ".join("%s %d" % (k, counts[k]) for k in sorted(counts))))
    p("")
    p("5. SIMULTANEOUS OPERATION (solar at the window, a vehicle at 24 V, the full load, charging)")
    p("   the front end's input is the H3 line's at VIN_RAW whatever the sources share: at 24 V at most %s A, %s %% of the entry's basis; the tracker's"
      % (fmt(F["h3"][24.0][1]), fmt(F["h3"][24.0][2])))
    p("   ceiling (%s V minimum) is above 24 V, so the panel carries the bus first and the vehicle supplies only what the panel does not give"
      % fmt(F["trk_ceiling"][0]))
    p("   delivered at VBAT: %s to %s W (U3 between its minimum at the lowest bus and its board-current maximum at the bus's top, U3 %s)"
      % (fmt(round(D["vbat_avail_min"], 1)), fmt(round(D["vbat_avail_max"], 1)), fmt(F["eta_u3"])))
    for nm, w in (("PS-IDLE-SPEC plan", F["idle"][1]), ("PS-TYP plus USB-C plan", F["typ_usbc"][0]), ("the PA keyed alone at 113 W, plan", F["pa113"][0]), ("PS-ALLTX plan", F["alltx"][1]), ("PS-ALLTX high", F["alltx"][2])):
        short = w - D["vbat_avail_min"]
        if short <= 0:
            p("   %-34s %6s W: carried by the sources, up to %s W left to charge (at most %s A ChargeCurrent)" % (nm, fmt(w), fmt(round(-short, 1)), fmt(F["chg_set"])))
        else:
            p("   %-34s %6s W: the pack supplies at least %s W, %s A at a 14.4 V stack; no charge" % (nm, fmt(w), fmt(round(short, 1)), fmt(round(short / 14.4, 2))))
    p("   no stage is pushed past its limit: the entry stays under its minimum limit (H3), R11 carries at most %s A, every can at most %s A, the pack's"
      % (fmt(F["r11_need"]), fmt(F["can8"][0])))
    p("   current falls by what the sources give (PS-ALLTX's floors of D-11 hold as on the pack alone), and the outlets drop while the PA keys")
    p("   per source at VBAT (U3 %s, VBUS20 %s V top, %s V lowest): vehicle at 9 V %s to %s W (the entry itself bounds 9 V at %s W); at 12 V up to %s W; at 24 V up to %s W"
      % (fmt(F["eta_u3"]), fmt(F["vbus_band"][1]), fmt(F["bus_low"]), fmt(round(D["vbat_at_9"][0], 1)), fmt(round(D["vbat_at_9"][1], 1)), fmt(round(D["entry_9v_vbat"], 1)), fmt(round(D["vbat_at_12"], 1)), fmt(round(D["vbat_at_24"], 1))))
    p("   so at the 9 V floor the vehicle runs PS-IDLE-SPEC (%s W) with the pack supplementing, and charges only while the kit draws under %s W"
      % (fmt(F["idle"][1]), fmt(round(D["vbat_at_9"][0], 1))))
    p("")
    p("6. STARTUP")
    p("   source arriving: the LM5069 starts at 9 V (UVLO, R21 '%s'), its timer bounds inrush; U3 is in HIZ below %s V and out above %s V; the H3 line"
      % (F["e_r21"], fmt(F["hiz_below"]), fmt(F["hiz_out_above"])))
    p("     bounds U3 from its first cycle with no host; the panel: the stage's own UVLO and soft start, the hold at %s V; SWEN stays off while"
      % fmt(F["hold"][1]))
    p("     TRK_LDO33 is under %s V, whatever the ramp (L4-E7R), and each backstop trip restarts through the soft start" % fmt(F["swen_v"]))
    p("   source leaving: VBAT is the system node with no battery FET, so the pack carries the loads without a break; IIN_HOST resets to 3.25 A")
    p("     and firmware writes %s A again (FW-A16 restated); VIN_RAW falls through the restart guard (%s V at the highest) and the front end stops" % (fmt(F["iin_host"]), fmt(F["latch"][2])))
    p("   dead pack (CUV opened the discharge FET): a source runs the loads through U3 at the pack's voltage while the charge clamps at 384 mA")
    p("     below VSYS_MIN; CONDITIONAL on TI's answer Q-TI-3 and O-CHG-2 (CHARGER-STATE-SEQUENCE.md); board E's always-on comes up on CELL_F from VBAT")
    p("")
    p("7. FAULTS, TRACED ACROSS THE STAGES")
    p("   reversed vehicle input (REQ-015): DC_P is back-fed from VIN_RAW through Q7's body diode (L4-E5's finding), so Q1 holds DC_P plus the")
    p("     reversed input: %s V with the drawn ceiling, %s V with L4-E5's raised ceiling, against BSC039N06NS %s V; a CSD19532Q5B (%s V) holds it,"
      % (fmt(D["q1_rev_drawn"]), fmt(D["q1_rev"]), fmt(F["bsc039_vds"]), fmt(F["csd19532_vds"])))
    p("     and U3's cathode to anode stays under its %s V recommended and %s V absolute" % (fmt(F["ld_ac_rec"]), fmt(F["ld_ca_abs"])))
    p("   a short behind F1: F1 must interrupt at up to %s V (the selected OVLO maximum); the kit's cable (%s m of %s mm2 a way) and lead (%s mm of AWG %d)"
      % (fmt(round(D["f1_v"], 2)), fmt(F["cable_m"]), fmt(F["cable_mm2"]), fmt(F["lead_mm"]), int(F["lead_awg"])))
    p("     give %s Ohm at 20 C and %s Ohm at %s C, so a stiff source drives at most %s A (copper alone); the drawn 297 is rated %s V DC: NOT MET"
      % (fmt(round(D["f1_r20"], 5)), fmt(round(D["f1_rcold"], 5)), fmt(T_COLD), fmt(round(D["f1_ipf"], 1)), fmt(F["f297_v"])))
    p("     as drawn; the selected 0997010.WXN is rated %s V DC and %s A at 58 V DC: MEETS (part A, section 11)" % (fmt(A["f_v"]), fmt(A["f_int"])))
    p("   VBUS20 shorted: the front end holds the output at %s A at 9 V (R12) and %s A above %s V (R11 8 mOhm); VIN_RAW then carries at most %s A;"
      % (fmt(F["fe_out_9v"]), fmt(F["r11_8"][2]), fmt(F["avg_from"]), fmt(round(D["vin_fault"], 3))))
    p("     the vehicle entry limits at %s to %s A and opens after %s to %s ms; the panel's stage regulates at %s A at most and its backstop trips"
      % (fmt(F["entry_lim"][0]), fmt(F["entry_lim"][1]), fmt(F["timer_ms"][0]), fmt(F["timer_ms"][2]), fmt(F["reg"][1])))
    p("     at %s A at most (SWEN, inside %s ms); the restart guard cycles the front end" % (fmt(F["bs_trip"][1]), fmt(F["bs_allow_ms"])))
    p("   VBAT shorted: the pack's SCD (%s A in 0.2 ms), OCD2, the 25 A blades and F2 against %s to %s A prospective; U3 at its input limit"
      % (fmt(F["scd"]), fmt(F["pp_fault"][0]), fmt(F["pp_fault"][1])))
    po = D["pack_open"]
    p("   the pack's charge FET opening mid-charge (a designed event, REQ-046): VBAT is held at ChargeVoltage (%s V at most), BATOVP stops switching"
      % fmt(F["chg_v_max"]))
    p("     at %s V, SYSOVP at %s V; L2's energy at the stop, %s mJ (peak %s A, L +20 %%), into VBAT's %d capacitors (%s uF nominal, %s uF kept at %s)"
      % (fmt(F["batovp"]), fmt(F["sysovp"][2]), fmt(round(po["e_mj"], 4)), fmt(round(po["i_pk"], 3)), po["n"], fmt(round(po["c_nom_uf"], 2)), fmt(round(po["c_eff_uf"], 2)), fmt(BIAS_KEEP)))
    p("     ends at %s V from the SYSOVP maximum, under the TPS2596's %s V; %s uF would do (%s of the nominal)"
      % (fmt(round(po["v_end"], 3)), fmt(F["tps2596_abs"]), fmt(round(po["c_need_uf"], 2)), fmt(round(po["keep_need"], 4))))
    p("   U2 failed (Q2 short or FB open) and U3 lost: outside every requirement (ASM-001); s120 section 11 and S-111 carry the residual and the")
    p("     options (an SMCJ22A on VBUS20: VR %s V over the %s V band; an independent over-voltage trip)" % (fmt(F["SMCJ22A"]["vr"]), fmt(F["vbus_band"][1])))
    p("   PoE monitor (HF-F02): U17's inputs at %s V against the INA226's %s V absolute: NOT MET as drawn; on R227, 5 mOhm in the stage's input"
      % (fmt(poe_v(F)), fmt(F["ina_abs"])))
    p("     (part A): %s A at a %s V stack, %s mV; %s A at the stage's fault bound, %s mV, against %s mV full scale; common mode at most %s V"
      % (fmt(round(D["poe_in"], 3)), fmt(D["vbat_low"]), fmt(round(A["u17_mv_norm"], 2)), fmt(round(A["u17_fault_a"], 2)), fmt(round(A["u17_mv_fault"], 2)), fmt(F["ina_fs_mv"]),
         fmt(round(max(F["sysovp"][2], D["pack_open"]["v_end"]), 3))))
    p("   the solar entry (L4-E7R): CS101 keeps the input at %s V under D4's %s V standoff; the capability scenario holds TRK_VS at %s V and PV_P at %s V;"
      % (fmt(F["cs101_pv"]), fmt(F["SMCJ28A"]["vr"]), fmt(F["trk_vs_max"]), fmt(F["pv_p_max"])))
    p("     a reversed panel conducts through D4 (DECISION-31 E-N1); the LT8705A's single faults are layer 8's list; the backstop's trip under CS101:")
    p("     %s" % L4E7R)
    p("   the vehicle entry under CS101 (M2) at REQ-015's 36 V: %s V against the drawn OVLO minimum %s V (NOT MET as drawn), the selected %s V: MEETS"
      % (fmt(round(A["cs101_top"], 2)), fmt(F["ovlo"][0]), fmt(round(F["ovlo_sel"][0], 2))))
    p("")
    p("8. THE ENDURANCE STATEMENT (A1 selected; A2 a proposal; DR-01)")
    a1b, a2b, sh = F["a1_bat"], F["a2_bat"], F["short"]
    p("   battery only: A1 %s Wh usable at +20 C, %s Wh at -10 C: %s h and %s h (short of 48 h by %s h, of 72 h by %s h); A2 %s h and %s h"
      % (fmt(a1b[0]), fmt(a1b[1]), fmt(a1b[2]), fmt(a1b[3]), fmt(sh[0]), fmt(sh[2]), fmt(a2b[2]), fmt(a2b[3])))
    c1, c2 = F["a1_cand"], F["a2_cand"]
    p("   solar-assisted on the candidate panel (nominal sheet, source compliance INCONCLUSIVE; L4-E7's settings, %s Wh a day): A1 first interruption"
      % fmt(c1[0]))
    p("     h %d / %d (06 / 18 UTC starts); unserved %s / %s Wh at 48 h, %s / %s Wh at 72 h; least storage to add +%s / +%s Wh"
      % (int(c1[1]), int(c1[2]), *[fmt(x) for x in c1[3:9]]))
    p("     A2: h %d / %d; unserved %s / %s and %s / %s Wh; +%s / +%s Wh; steady load carried A1 %s W, A2 %s / %s W (48 / 72 h)"
      % (int(c2[1]), int(c2[2]), *[fmt(x) for x in c2[3:9]], fmt(F["steady"][2]), fmt(F["steady"][0]), fmt(F["steady"][1])))
    s1, s2 = F["a1_scr"], F["a2_scr"]
    p("   the 100 W screening stimulus (a conditional comparison): A1 h %d / %d, unserved %s / %s and %s / %s Wh, +%s / +%s Wh; A2 h %d / %d, +%s / +%s Wh"
      % (int(s1[0]), int(s1[1]), fmt(s1[2]), fmt(s1[3]), fmt(s1[4]), fmt(s1[5]), fmt(F["a1_scr_add"][0]), fmt(F["a1_scr_add"][1]), int(s2[0]), int(s2[1]), fmt(F["a2_scr_add"][0]), fmt(F["a2_scr_add"][1])))
    p("   what moves these: H3 gives up %s to %s Wh a day on the candidate's trace; the ballasts at most %s W at the bound's worst corner; C-8"
      % (fmt(F["h3_cand_given"][0]), fmt(F["h3_cand_given"][1]), fmt(F["ballast_w"])))
    dd = F["a1_cand"][0] - F["e7r_day"][1]
    p("   the selected solar control (L4-E7R): the day's energy %s / %s / %s Wh on SC-37 (lower / nominal / upper hold corner) and %s Wh on the"
      % (*[fmt(x) for x in F["e7r_day"]], fmt(F["e7r_bright"])))
    p("     bright day; the solar rows above are at L4-E7's %s Wh nominal and the replay is not re-run here: at the nominal hold the unserved energy"
      % fmt(F["a1_cand"][0]))
    p("     grows by at most %s Wh a day, %s Wh at 48 h and %s Wh at 72 h (INFERRED: harvest lost can at most add to it); the sense bank's %s Wh a day"
      % (fmt(round(dd, 1)), fmt(round(2 * dd, 1)), fmt(round(3 * dd, 1)), fmt(F["bank_wh"][0])))
    p("     is carried beside it (L4-E7R prints it apart from the day's energy; if the day's figure already holds it, this counts it twice, the")
    p("     conservative side)")
    p("   L4-E8's ballasts in the budgets: at most %s W while U3 runs at the bound's worst corner, %s W at L4-E8's nominal illustration; a loss on"
      % (fmt(F["ballast_w"]), fmt(F["ballast_nom_w"])))
    p("     the charge path only (battery-only endurance does not carry it: U3 is idle), outside the DECLARED efficiencies (C-8), and dropped once a")
    p("     measured efficiency with the ballasts fitted includes it (R-51). Thermal: at most %s W more into the sealed case, %s K on the inside air"
      % (fmt(F["ballast_w"]), fmt(round(F["ballast_w"] / F["th1"], 2))))
    p("     at T-H1's %s W/K floor (INFERRED: the same conductance), on top of L4-E10's conditioned corner (%s / %s C; about %s W of the kit's heat at"
      % (fmt(F["th1"]), "%.2f" % F["corner_air"][0], "%.2f" % F["corner_air"][1], fmt(round(F["corner_heat"], 1))))
    p("     E3-O, which predates the ballasts): it narrows U-02 (MESHSAT-1478)")
    p("   the cell under L4-E10's recommendation (U-01, CONDITIONAL on the signed specification and the owner's approval; not taken here): usable")
    p("     %s Wh against the 35E's %s Wh (%s %% less), %s h against %s h battery-only at PS-IDLE-SPEC (L4-E10's own basis); D-06's about 145 Wh becomes"
      % (fmt(F["cell_usable"][1]), fmt(F["cell_usable"][0]), fmt(F["cell_less_pct"]), fmt(F["cell_hours"][1]), fmt(F["cell_hours"][0])))
    p("     about %s Wh nominal; every storage shortfall above grows by at most the usable energy lost, %s Wh (INFERRED)"
      % (fmt(F["cell_nom"][1]), fmt(round(F["cell_usable"][0] - F["cell_usable"][1], 1))))
    p("   the objective of 48 to 72 h is unmet by A1 on every trace (DR-01); no mandatory function is reduced to narrow it")
    p("")
    p("9. THE CLOSURE GATE (a criterion reads PASS only on rows that read MEETS; ASSUMPTION, CONDITIONAL and PENDING rows cannot carry a PASS)")
    bad = gate_violations(GATE, st)
    for g in GATE:
        p("   %d. %s: %s; rows %s%s" % (g["n"], g["criterion"], g["verdict"], ", ".join("%s %s" % (r, st[r][1]) for r in g["rows"]) or "none (the registers)",
                                    "; choices " + ", ".join(g["choices"]) if g.get("choices") else ""))
        if g["constraint"]:
            p("      constraint: %s" % g["constraint"])
            p("      could it overturn the architecture: %s" % g["overturn"])
    if bad:
        refuse(4, "the gate's rule fails: %s" % bad)
    closed = all(g["verdict"] == "PASS" for g in GATE)
    p("   Layer 4's power architecture closes: %s" % ("YES" if closed else "NO, criteria %s are not PASS" % ", ".join(str(g["n"]) for g in GATE if g["verdict"] != "PASS")))
    p("   MATERIAL POWER-PATH DEFECTS (criterion 2): %d, %d open" % (len(DEFECTS), sum(1 for d in DEFECTS if d["state"] == "OPEN")))
    for d in DEFECTS:
        p("     %s %s [%s]; rows %s" % (d["id"], d["title"], d["state"], ", ".join("%s %s" % (r, st[r][1]) for r in d["rows"])))
        p("        the constraint: %s" % d["constraint"])
        p("        the options: %s; resolution: %s" % (d["options"], d["resolution"]))
    p("   (b) UNRESOLVED CHOICES THAT COULD OVERTURN THE ARCHITECTURE: %d (no owner or acceptance criterion closes one; each keeps every" % len(CHOICES))
    p("       criterion that names it from PASS until its evidence lands)")
    for c in CHOICES:
        p("     %s %s; rows %s" % (c["id"], c["title"], ", ".join("%s %s" % (r, st[r][1]) for r in c["rows"])))
        for k, lab in (("constraint", "the exact constraint"), ("settles", "the evidence that settles it"), ("alternatives", "the alternatives"),
                       ("owner", "the owner's items"), ("overturns", "what it could overturn")):
            p("        %s: %s" % (lab, c[k]))
    p("   (a) DOWNSTREAM IMPLEMENTATION AND VERIFICATION TASKS: the register of section 10; an owner and an acceptance criterion close the")
    p("       ASSIGNMENT, not the item: each stays OWED, DRAFTED, MISSING DRAFT or PENDING until its acceptance is met on the built prototype")
    p("")
    p("10. THE REGISTERS (this folder's DOWNSTREAM-REGISTER.md and LAYER5-HANDOVER.md, read and checked)")
    reg_text = open(os.path.join(HERE, "DOWNSTREAM-REGISTER.md"), encoding="utf-8").read() if os.path.exists(os.path.join(HERE, "DOWNSTREAM-REGISTER.md")) else ""
    reg = md_table(reg_text, "| ID | Kind |")
    by_owner, by_kind = {}, {}
    for r in reg:
        if len(r) < 8 or r[4] not in OWNERS or not r[5]:
            refuse(4, "register row %s has no named owner or acceptance" % (r[0] if r else "?"))
        by_owner[r[4]] = by_owner.get(r[4], 0) + 1
        by_kind[r[1]] = by_kind.get(r[1], 0) + 1
    p("   register: %d items; by owner: %s" % (len(reg), "; ".join("%s %d" % (o, by_owner[o]) for o in OWNERS if o in by_owner)))
    p("     by kind: %s" % "; ".join("%s %d" % (k, by_kind[k]) for k in sorted(by_kind)))
    by_state = {}
    for r in reg:
        if r[1] == "IMPLEMENTATION":
            by_state[r[6]] = by_state.get(r[6], 0) + 1
    p("     implementation changes by state: %s" % "; ".join("%s %d" % (k, by_state[k]) for k in sorted(by_state)))
    h_text = open(os.path.join(HERE, "LAYER5-HANDOVER.md"), encoding="utf-8").read() if os.path.exists(os.path.join(HERE, "LAYER5-HANDOVER.md")) else ""
    ho = md_table(h_text, "| ID | Target |")
    for r in ho:
        for rid in re.findall(r"IF-\d\d", r[3] if len(r) > 3 else ""):
            if rid not in st:
                refuse(4, "handover %s names an unknown row %s" % (r[0], rid))
    p("   Layer 5 handover: %d interface entries drafted (pcb_interfaces.yaml and HW-FW-CONTRACT.md, drafts only)" % len(ho))
    p("")
    for ln in partA_lines(F, D, A):
        p(ln)
    p("")
    p("END. Desk arithmetic on read figures; nothing is measured.")
    return "\n".join(out) + "\n", F, D, R, st


def poe_v(F):
    return F["poe"]["volts"]


if __name__ == "__main__":
    text, *_ = main()
    sys.stdout.write(text)
