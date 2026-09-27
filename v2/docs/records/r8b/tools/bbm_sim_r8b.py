#!/usr/bin/env python3
"""Board B's bank break-before-make, simulated from the NETLIST (MESHSAT-1357 round 8, stream b, pass 2).

Written for this round; no project tool. It reads a KiCad 9 netlist with its own reader, builds each bank's control plane
from the parts it finds there (not from the generator's comments), and runs an event-driven logic and RC simulation of
it. What it reads from the netlist:
  - every SN74LVC86A (quad XOR), SN74LVC32A (quad OR), 74LVC1G17 (Schmitt buffer), 74LVC1G157 (2:1 mux) and
    SN74LVC1G04 (inverter), by its value text, with the makers' pin tables (TI SCAS288R and SCAS286U Pin Functions,
    Diodes DS35124 Pin Assignments, Nexperia 74LVC1G157 Rev. 12 Table 3, TI SCES214AF Pin Functions);
  - every RC node: a net with exactly one resistor to a logic net and one capacitor to GND, read by a 74LVC1G17;
  - each bank's select and enable AT THE SWITCHES: the nets on TMUXHS4212 U{b}09 pins 9 (SEL) and 2 (OEn).
Stimulus nets are BSEL1..3 (the votes) and PG1..3 (the slots' power-good nodes); +3V3_DEV is 1 and GND is 0.

The parameters are the makers' ranges, drawn per part instance for each run (Monte Carlo) and pinned at corners:
  supply V 3.0 to 3.6 V; 74LVC1G17 VT+, VT- and hysteresis from Diodes DS35124 Rev 8-2 p.4 (the -40 to +125 C table:
  VT+ 1.50 to 2.00 V, VT- 0.80 to 1.33 V, hysteresis 0.32 to 1.00 V at VCC 3 V; 2.16 to 2.74, 1.21 to 1.95 and 0.50 to 1.20
  at 4.5 V; between 3.0 and 3.6 V the limits are interpolated linearly toward the 4.5 V row, INFERRED) and its input
  leakage +-5 uA through the RC's resistor; the driver's output level VCC - 0.1 V to VCC and 0 to 0.1 V (DS35124, SCAS288R:
  VOH/VOL at 100 uA); R 1 percent; C 10 percent (the order codes' tolerance) and X7R's +-15 percent over temperature;
  propagation delays at 3.3 V +-0.3 V, -40 to +125 C: SN74LVC86A 1.0 to 5.8 ns (SCAS288R 5.9), SN74LVC32A 1.0 to 5.0 ns
  (SCAS286U 5.9), 74LVC1G157 1.0 to 6.3 ns (Rev. 12 Table 8), 74LVC1G17 0.7 to 7.0 ns (DS35124 p.6), SN74LVC1G04 1.0 to
  4.2 ns (SCES214AF). Gates are transport delays (a pulse of any width is passed, which is the pessimistic choice for a
  hazard search). With --hazard, every 74LVC1G157 whose select changes while both data inputs are high also emits a
  0.1 to 2 ns low pulse (an AND-OR mux's static-1 hazard, which Nexperia's sheet neither promises nor excludes).

The property checked, for every move of the select at the switch pins: the enable at the same switch is HIGH (off) at the
move, with no enable transition from LEAD before the move to HOLD after it; LEAD and HOLD are reported per move, and a
move with the enable low, a LEAD under --lead-req (default 1 us, 100 times TS3USB221A's 10 ns OE disable time, SCDS277C
5.8, and the TMUXHS4212's 1 us SEL-to-OFF with a common-mode change, SLASEP7A 6.7) or a HOLD under --hold-req (default
40 us, 8 times the TMUXHS4212's 5 us SEL-to-ON with a common-mode change, SLASEP7A 6.7) is a violation. Liveness: after the last stimulus the bank
ends with the select equal to the vote and the enable low (all slots powered).

Usage: bbm_sim_r8b.py <netlist> [--runs N] [--seed S] [--hazard] [--json out.json] [--banks 1,2,3] [--lead-req s] [--hold-req s]"""
import heapq, json, math, random, re, sys

# ------------------------------------------------------------------ netlist reader (independent of the project's tools)
def parse(text):
    tok = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
    stack, cur = [], []
    for m in tok.finditer(text):
        t = m.group(0)
        if t == "(":
            stack.append(cur); cur = []
        elif t == ")":
            done = cur; cur = stack.pop(); cur.append(done)
        else:
            cur.append(t[1:-1].replace('\\"', '"').replace("\\\\", "\\") if t.startswith('"') else t)
    return cur[0]

def kids(node, name):
    return [c for c in node if isinstance(c, list) and c and c[0] == name]

def one(node, name, default=None):
    k = kids(node, name)
    return k[0][1] if k and len(k[0]) > 1 else default

def load(path):
    root = parse(open(path, encoding="utf-8").read())
    val, pins, nets = {}, {}, {}
    for comp in kids(kids(root, "components")[0], "comp"):
        val[one(comp, "ref")] = one(comp, "value") or ""
    for net in kids(kids(root, "nets")[0], "net"):
        name = one(net, "name").lstrip("/")
        for n in kids(net, "node"):
            pins.setdefault(one(n, "ref"), {})[one(n, "pin")] = name
            nets.setdefault(name, set()).add((one(n, "ref"), one(n, "pin")))
    return val, pins, nets

QUAD = [("1", "2", "3"), ("4", "5", "6"), ("9", "10", "8"), ("12", "13", "11")]   # (A, B, Y), SCAS288R / SCAS286U
def ohms(v):
    m = re.match(r"\s*([\d.]+)\s*([kKmM]?)", v); x = float(m.group(1))
    return x * {"": 1, "k": 1e3, "K": 1e3, "m": 1e6, "M": 1e6}[m.group(2)]
def farads(v):
    m = re.match(r"\s*([\d.]+)\s*([pnu])", v); return float(m.group(1)) * {"p": 1e-12, "n": 1e-9, "u": 1e-6}[m.group(2)]

def build(path):
    """Gates, RC nodes and Schmitt buffers of the whole netlist, by part type."""
    val, pins, nets = load(path)
    gates, schmitt = [], []
    for ref, v in val.items():
        p = pins.get(ref, {})
        if v.startswith("SN74LVC86A") or v.startswith("74LVC86A") or v.startswith("SN74LVC32A"):
            kind = "xor" if "86A" in v.split()[0] else "or"
            for a, b, y in QUAD:
                if p.get(y, "GND") in ("GND", "") or p.get(y, "").startswith("unconnected"): continue
                if p.get(a) == "GND" and p.get(b) == "GND": continue
                gates.append({"ref": ref + ":" + y, "kind": kind, "in": [p[a], p[b]], "out": p[y]})
        elif v.startswith("74LVC1G157"):
            gates.append({"ref": ref, "kind": "mux", "in": [p["6"], p["3"], p["1"]], "out": p["4"]})   # S, I0, I1
        elif v.startswith("SN74LVC1G04"):
            gates.append({"ref": ref, "kind": "inv", "in": [p["2"]], "out": p["4"]})
        elif v.startswith("74LVC1G17"):
            schmitt.append({"ref": ref, "in": p["2"], "out": p["4"]})
    # RC nodes: the Schmitt's input net carries one resistor to a logic net and one capacitor to GND
    rc = {}
    for s in schmitt:
        n = s["in"]; rs = [r for r, _ in nets.get(n, ()) if r.startswith("R")]; cs = [c for c, _ in nets.get(n, ()) if c.startswith("C")]
        if len(rs) == 1 and len(cs) == 1:
            r = rs[0]; drv = [x for k, x in pins[r].items() if x != n][0]
            c = cs[0]; other = [x for k, x in pins[c].items() if x != n][0]
            assert other == "GND", (c, other)
            rc[n] = {"R": ohms(val[r]), "C": farads(val[c]), "drv": drv, "rref": r, "cref": c}
    return val, pins, nets, gates, schmitt, rc

# ------------------------------------------------------------------ the makers' ranges
def lin(v, a3, a45): return a3 + (a45 - a3) * (v - 3.0) / 1.5
def tlimits(V):
    """74LVC1G17 limits at supply V (Diodes DS35124 Rev 8-2 p.5, -40 to +125 C): the MINIMA are the 3 V row's at every V (the
    lower, so shorter-time, side), the MAXIMA are interpolated linearly from the 3 V row toward the 4.5 V row (INFERRED); the
    hysteresis minimum is the 3 V row's 0.32 V at every V."""
    return {"tp": (1.50, lin(V, 2.00, 2.74)), "tm": (0.80, lin(V, 1.33, 1.95)), "h": (0.32, lin(V, 1.00, 1.20))}
def thresholds(V, rnd, corner=None):
    L = tlimits(V); (tpmin, tpmax), (tmmin, tmmax), (hmin, hmax) = L["tp"], L["tm"], L["h"]
    if corner == "narrow_low":    # the smallest hysteresis at the lowest thresholds
        tp = tpmin; return tp, max(tmmin, tp - hmin)
    if corner == "narrow_high":   # the smallest hysteresis at the highest thresholds
        tm = tmmax; return min(tpmax, tm + hmin), tm
    for _ in range(1000):
        tp = rnd.uniform(tpmin, tpmax); tm = rnd.uniform(tmmin, tmmax)
        if hmin <= tp - tm <= hmax: return tp, tm
    raise RuntimeError("no threshold pair")
TAU = {"R": (0.99, 1.01), "C": (0.90 * 0.85, 1.10 * 1.15)}      # 1 percent R; C 10 percent and X7R's +-15 percent
DRIVE = {"hi": (-0.15, 0.05), "lo": (-0.05, 0.15)}              # VOH = V - (0..0.1), VOL = 0..0.1, +-5 uA x 10 k

def bounds(tau1=(10e3 * 10e-9), taun=(10e3 * 100e-9), tau2=(10e3 * 100e-9), steps=13):
    """Analytic lower bounds, for ANY vote waveform, of the round-8 pass-2 cascade (see the record for the argument):
      HOLD >= tau2 x the D2 buffer's own hysteresis traversal (the MOV lock makes every move start from D2 = select);
      LEAD >= x1's return to its threshold after the last unlock, which follows either T2 of lock (case a) or ARM's
      re-arm, an up-traversal of ARM's own hysteresis (case b), with x1 driven to the select's rail throughout;
      ARM margin at a move: ARM cannot fall within this time of a move even if the vote returns at the move."""
    import itertools
    def grid(a, b): return [a + (b - a) * k / (steps - 1) for k in range(steps)]
    def pairs(L):
        """(VT+, VT-) over the limits, the hysteresis stepped from its minimum, so the narrowest band is always visited."""
        for tp in grid(*L["tp"]):
            for h in grid(*L["h"]):
                tm = tp - h
                if L["tm"][0] - 1e-9 <= tm <= L["tm"][1] + 1e-9: yield tp, tm
        for tm in grid(*L["tm"]):
            tp = tm + L["h"][0]
            if L["tp"][0] - 1e-9 <= tp <= L["tp"][1] + 1e-9: yield tp, tm
    t1 = [tau1 * TAU["R"][0] * TAU["C"][0], tau1 * TAU["R"][1] * TAU["C"][1]]
    tn = [taun * TAU["R"][0] * TAU["C"][0], taun * TAU["R"][1] * TAU["C"][1]]
    t2 = [tau2 * TAU["R"][0] * TAU["C"][0], tau2 * TAU["R"][1] * TAU["C"][1]]
    best = {"hold": (9, None), "lead_a": (9, None), "lead_b": (9, None), "up_n": (9, None), "arm_margin": (9, None)}
    def upd(k, v, why):
        if v < best[k][0]: best[k] = (v, why)
    for V in (3.0, 3.3, 3.6):
        L = tlimits(V)
        for tp, tm in pairs(L):
                for dh, dl in itertools.product(DRIVE["hi"], DRIVE["lo"]):
                    th, tl = V + dh, dl
                    up = math.log((th - tm) / (th - tp)); dn = math.log((tp - tl) / (tm - tl))
                    upd("up_n", min(up, dn), (V, tp, tm, th, tl))
                    # HOLD: D2 (tau2) traverses its band after every move
                    upd("hold", t2[0] * min(up, dn), (V, tp, tm, th, tl))
        # LEADs need x1's thresholds (one part) and the lock time (another part's traversal: take its minimum at this V)
    Hn = tn[0] * best["up_n"][0]; H2 = best["hold"][0]
    for V in (3.0, 3.3, 3.6):
        L = tlimits(V)
        for tp, tm in pairs(L):
                for dh, dl in itertools.product(DRIVE["hi"], DRIVE["lo"]):
                    th, tl = V + dh, dl
                    for ta in t1 + [(t1[0] + t1[1]) / 2]:
                        # case (a): locked T2 >= H2 from the threshold just crossed, then back to the other threshold
                        x_hi = th - (th - tp) * math.exp(-H2 / ta); la1 = ta * math.log((x_hi - tl) / (tm - tl))
                        x_lo = tl + (tm - tl) * math.exp(-H2 / ta); la0 = ta * math.log((th - x_lo) / (th - tp))
                        upd("lead_a", min(la1, la0), (V, tp, tm, th, tl, ta))
                        # case (b): locked for ARM's re-arm >= Hn from anywhere on the select's side, then to the threshold
                        x_b0 = tl + (tp - tl) * math.exp(-Hn / ta); lb0 = ta * math.log((th - x_b0) / (th - tp))
                        x_b1 = th - (th - tm) * math.exp(-Hn / ta); lb1 = ta * math.log((x_b1 - tl) / (tm - tl))
                        upd("lead_b", min(lb0, lb1), (V, tp, tm, th, tl, ta))
    # ARM margin: at a move ARM = 1 and xn has risen for the whole approach (>= min lead) from at least its VT-
    lead = min(best["lead_a"][0], best["lead_b"][0])
    for V in (3.0, 3.3, 3.6):
        L = tlimits(V)
        for tm in grid(*L["tm"]):
            for dh, dl in itertools.product(DRIVE["hi"], DRIVE["lo"]):
                th, tl = V + dh, dl
                for ta in tn:
                    x = th - (th - tm) * math.exp(-lead / ta)
                    upd("arm_margin", ta * math.log((x - tl) / (tm - tl)), (V, tm, th, tl, ta))
    # A SINGLE CHANGE FROM REST: every node starts at its rail (the drive target, offsets included) and crosses one threshold
    def rest(taus):
        lo, hi = 9.0, 0.0
        for V in (3.0, 3.3, 3.6):
            L = tlimits(V)
            for tp, tm in pairs(L):
                for dh, dl in itertools.product(DRIVE["hi"], DRIVE["lo"]):
                    th, tl = V + dh, dl
                    for ta in taus:
                        for t in (ta * math.log((th - tl) / (th - tp)), ta * math.log((th - tl) / (tm - tl))):
                            lo, hi = min(lo, t), max(hi, t)
        return lo, hi
    arm, sel, d2 = rest(tn), rest(t1), rest(t2)
    gate_max = (5.8 + 5.0 + 5.0 + 6.3) * 1e-9          # XOR, OR, OR, 74LVC1G157 at -40 to +125 C
    return {"single_change_from_rest": {"enable_off_after_vote_ns_max": gate_max * 1e9,
                                        "arm_after_vote_us": [arm[0] * 1e6, arm[1] * 1e6],
                                        "select_after_arm_us": [sel[0] * 1e6, sel[1] * 1e6],
                                        "select_after_vote_us": [(arm[0] + sel[0]) * 1e6, (arm[1] + sel[1]) * 1e6],
                                        "delayed_copy_after_select_us": [d2[0] * 1e6, d2[1] * 1e6]},
            "tau1_us": [x * 1e6 for x in t1], "taun_us": [x * 1e6 for x in tn], "tau2_us": [x * 1e6 for x in t2],
            "hysteresis_traversal_min_tau": best["up_n"][0], "hold_min_us": best["hold"][0] * 1e6,
            "lead_min_case_a_us": best["lead_a"][0] * 1e6, "lead_min_case_b_us": best["lead_b"][0] * 1e6,
            "arm_margin_min_us": best["arm_margin"][0] * 1e6,
            "worst": {k: v[1] for k, v in best.items()}}
DELAY = {"xor": (1.0e-9, 5.8e-9), "or": (1.0e-9, 5.0e-9), "mux": (1.0e-9, 6.3e-9), "inv": (1.0e-9, 4.2e-9), "st": (0.7e-9, 7.0e-9)}

class Sim:
    def __init__(self, model, rnd, V=None, hazard=False, corner=None, taucorner=None):
        self.val, self.pins, self.nets, self.gates, self.schmitt, self.rc = model
        self.rnd = rnd; self.V = V if V is not None else rnd.uniform(3.0, 3.6); self.hazard = hazard
        self.net = {"+3V3_DEV": 1, "GND": 0}
        self.readers = {}
        for g in self.gates:
            g["d"] = rnd.uniform(*DELAY[g["kind"]])
            for n in g["in"]: self.readers.setdefault(n, []).append(g)
        self.rcdrv = {}
        for n, r in self.rc.items():
            k = {"min": 0, "max": 1}.get(taucorner)
            rt = TAU["R"][k] if k is not None else rnd.uniform(*TAU["R"]); ct = TAU["C"][k] if k is not None else rnd.uniform(*TAU["C"])
            r["tau"] = r["R"] * rt * r["C"] * ct
            r["leak"] = rnd.uniform(-5e-6, 5e-6) * r["R"]
            r["voh"] = self.V - rnd.uniform(0.0, 0.1); r["vol"] = rnd.uniform(0.0, 0.1)
            r["x0"] = 0.0; r["t0"] = -1.0; r["tgt"] = r["vol"] + r["leak"]; r["ver"] = 0
            self.rcdrv.setdefault(r["drv"], []).append(n)
        self.st_of = {}
        for s in self.schmitt:
            s["tp"], s["tm"] = thresholds(self.V, rnd, corner)
            s["d"] = rnd.uniform(*DELAY["st"]); s["state"] = 0
            self.st_of[s["in"]] = s
            if s["in"] not in self.rc: self.readers.setdefault(s["in"], []).append(s)   # a Schmitt on a logic net
        self.q = []; self.seq = 0; self.t = 0.0; self.log = {}; self.times = []; self.init = {}
        self.watch = set()

    def push(self, t, kind, *a):
        self.seq += 1; heapq.heappush(self.q, (t, self.seq, kind, a))

    def x(self, n, t):
        r = self.rc[n]; return r["tgt"] + (r["x0"] - r["tgt"]) * math.exp(-(t - r["t0"]) / r["tau"])

    def retarget(self, n, t):
        r = self.rc[n]; r["x0"] = self.x(n, t); r["t0"] = t
        r["tgt"] = (r["voh"] if self.net.get(r["drv"], 0) else r["vol"]) + r["leak"]; r["ver"] += 1
        s = self.st_of.get(n)
        if s is None: return
        x0, tg = r["x0"], r["tgt"]
        if s["state"] == 0 and tg > s["tp"] and x0 < s["tp"]:
            tc = t + r["tau"] * math.log((x0 - tg) / (s["tp"] - tg)); self.push(tc, "cross", n, r["ver"])
        elif s["state"] == 1 and tg < s["tm"] and x0 > s["tm"]:
            tc = t + r["tau"] * math.log((x0 - tg) / (s["tm"] - tg)); self.push(tc, "cross", n, r["ver"])

    def evalg(self, g):
        v = [self.net.get(n, 0) for n in g["in"]]
        if g["kind"] == "xor": return v[0] ^ v[1]
        if g["kind"] == "or": return v[0] | v[1]
        if g["kind"] == "inv": return 1 - v[0]
        if g["kind"] == "mux": return v[2] if v[0] else v[1]

    def setnet(self, t, n, v):
        old = self.net.get(n, 0)
        if old == v: return
        self.net[n] = v; self.times.append(t)
        if n in self.watch: self.log.setdefault(n, []).append((t, v))
        for g in self.readers.get(n, []):
            if "kind" in g:
                if self.hazard and g["kind"] == "mux" and n == g["in"][0] and self.net.get(g["in"][1], 0) and self.net.get(g["in"][2], 0):
                    w = self.rnd.uniform(0.1e-9, 2e-9); self.push(t + g["d"], "set", g["out"], 0); self.push(t + g["d"] + w, "set", g["out"], 1)
                    continue
                self.push(t + g["d"], "set", g["out"], self.evalg(g))
            else:   # a Schmitt buffer on a logic net: a fast edge, it follows after its delay
                self.push(t + g["d"], "set", g["out"], v)
        for rn in self.rcdrv.get(n, []): self.retarget(rn, t)

    def run(self, stim, tend):
        for (t, n, v) in stim: self.push(t, "set", n, v)
        while self.q and self.q[0][0] <= tend:
            t, _, kind, a = heapq.heappop(self.q); self.t = t
            if kind == "set": self.setnet(t, a[0], a[1])
            elif kind == "cross":
                n, ver = a
                if ver != self.rc[n]["ver"]: continue
                s = self.st_of[n]; s["state"] = 1 - s["state"]; self.times.append(t)
                self.push(t + s["d"], "set", s["out"], s["state"])
                # the node keeps moving toward its target; no further crossing until the driver changes

def bank_nets(pins, b):
    mux = "U%d09" % b; usb = "U%d10" % b
    return pins[mux]["9"], pins[mux]["2"], pins[usb]["9"], pins[usb]["6"]

def settle(model, rnd, V, hazard, corner, taucorner, init):
    """A simulator settled at the initial stimulus (every node at its steady state), ready at t = 0."""
    sim = Sim(model, rnd, V, hazard, corner, taucorner)
    stim = [(-0.2, n, v) for n, v in init.items()]
    sim.run(stim, -0.1)
    for g in sim.gates: sim.push(-0.1, "set", g["out"], sim.evalg(g))
    sim.run([], 0.0)
    return sim

REQ = {"lead": 1e-6, "hold": 40e-6}
def judge(sim, b, sels, oes, a_final, pg_all):
    """Every select move at either switch against the enable at the same switch."""
    out = {"moves": 0, "min_lead": None, "min_hold": None, "violations": []}
    for sel, oe in zip(sels, oes):
        ev_s = sim.log.get(sel, []); ev_o = sim.log.get(oe, [])
        for (ts, vs) in ev_s:
            out["moves"] += 1
            before = [(t, v) for t, v in ev_o if t <= ts]; after = [(t, v) for t, v in ev_o if t > ts]
            level = before[-1][1] if before else sim.init.get(oe, 0)
            if level != 1:
                out["violations"].append("select %s moved at %.9f s with enable %s LOW (last edge %s)" % (sel, ts, oe, before[-1] if before else None)); continue
            lead = ts - before[-1][0] if before else float("inf")
            nxt = [t for t, v in after if v == 0]
            hold = (nxt[0] - ts) if nxt else float("inf")
            if lead < REQ["lead"] or hold < REQ["hold"]:
                out["violations"].append("select %s moved at %.9f s with the enable off only %.3f us before and %.3f us after (required %.1f and %.1f)" % (
                    sel, ts, lead * 1e6, hold * 1e6, REQ["lead"] * 1e6, REQ["hold"] * 1e6))
            out["min_lead"] = lead if out["min_lead"] is None else min(out["min_lead"], lead)
            out["min_hold"] = hold if out["min_hold"] is None else min(out["min_hold"], hold)
    # liveness: the select follows the final vote and, with every slot powered, the enable returns
    if pg_all:
        for sel, oe in zip(sels, oes):
            if sim.net.get(sel, 0) != a_final: out["violations"].append("liveness: %s ends at %d with the vote at %d" % (sel, sim.net.get(sel, 0), a_final))
            if sim.net.get(oe, 0) != 0: out["violations"].append("liveness: %s ends high with every slot powered" % oe)
    return out

def scenario(model, b, rnd, stim_a, hazard=False, V=None, corner=None, taucorner=None, pg=(1, 1, 1), pg_stim=(), tend=None):
    val, pins, nets, gates, schmitt, rc = model
    sel1, oe1, sel2, oe2 = bank_nets(pins, b)
    vote = "BSEL%d" % b
    init = {"BSEL1": 0, "BSEL2": 0, "BSEL3": 0, "PG1": pg[0], "PG2": pg[1], "PG3": pg[2]}
    a0 = stim_a[0][1] if stim_a and stim_a[0][0] < 0 else 0
    init[vote] = a0
    sim = settle(model, rnd, V, hazard, corner, taucorner, init)
    sim.watch = {sel1, oe1, sel2, oe2}; sim.log = {}; sim.times = []
    sim.init = {n: sim.net.get(n, 0) for n in sim.watch}
    st = [(t, vote, v) for t, v in stim_a if t >= 0] + list(pg_stim)
    last = max([t for t, _, _ in st] + [0.0])
    sim.run(st, (tend or (last + 0.03)))
    a_final = ([v for t, v in stim_a if t >= 0] or [a0])[-1]
    pg_all = all(pg) and not pg_stim
    return judge(sim, b, [sel1, sel2], [oe1, oe2], a_final, pg_all), sim

def event_times(sim):
    """Every instant something happened in a run, for the adversary to aim at."""
    return sorted(set(round(t, 12) for t in sim.times if t >= 0))

def main(a):
    if a and a[0] == "--bounds":
        b = bounds(); print(json.dumps(b, indent=1)); return 0
    path = a[0]
    runs = int(a[a.index("--runs") + 1]) if "--runs" in a else 300
    seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 1
    hazard = "--hazard" in a
    if "--lead-req" in a: REQ["lead"] = float(a[a.index("--lead-req") + 1])
    if "--hold-req" in a: REQ["hold"] = float(a[a.index("--hold-req") + 1])
    banks = [int(x) for x in (a[a.index("--banks") + 1].split(",") if "--banks" in a else ["1", "2", "3"])]
    model = build(path)
    val, pins, nets, gates, schmitt, rc = model
    rnd = random.Random(seed)
    rep = {"netlist": path, "hazard_model": hazard, "rc_nodes": {n: {k: r[k] for k in ("R", "C", "drv", "rref", "cref")} for n, r in rc.items()},
           "gates": len(gates), "schmitt": len(schmitt), "families": {}}
    for b in banks:
        sel1, oe1, sel2, oe2 = bank_nets(pins, b)
        rep.setdefault("switch_pins", {})[b] = {"TMUXHS4212 SEL": sel1, "TMUXHS4212 OEn": oe1, "TS3USB221A S": sel2, "TS3USB221A OE": oe2}
    fam = rep["families"]
    def acc(name, res):
        f = fam.setdefault(name, {"runs": 0, "moves": 0, "min_lead_us": None, "min_hold_us": None, "violations": 0, "examples": []})
        f["runs"] += 1; f["moves"] += res["moves"]
        for k, kk in (("min_lead", "min_lead_us"), ("min_hold", "min_hold_us")):
            if res[k] is not None and res[k] != float("inf"):
                f[kk] = res[k] * 1e6 if f[kk] is None else min(f[kk], res[k] * 1e6)
        f["violations"] += len(res["violations"])
        if res["violations"] and len(f["examples"]) < 6: f["examples"].append(res["violations"][0])
    corners = [(V, c, tc) for V in (3.0, 3.3, 3.6) for c in ("narrow_low", "narrow_high", None) for tc in ("min", "max", None)]
    for b in banks:
        # 1. single vote changes, both directions, at every corner
        for (V, c, tc) in corners:
            for up in (1, 0):
                stim = [(-1, 1 - up), (0.0, up)]
                res, _ = scenario(model, b, rnd, stim, hazard, V, c, tc); acc("1 single vote change (corners)", res)
        # 2. the checker's case: the vote returns r after it changed, r swept over 0 to 6 ms (1 us steps near the moves)
        for (V, c, tc) in corners[::3]:
            res0, sim0 = scenario(model, b, rnd, [(-1, 0), (0.0, 1)], hazard, V, c, tc)
            marks = event_times(sim0)
            grid = sorted(set([i * 20e-6 for i in range(300)] + [m + d for m in marks for d in (-2e-6, -1e-6, -1e-7, -1e-8, -1e-9, 0, 1e-9, 3e-9, 1e-8, 1e-7, 1e-6, 1e-5, 2e-5)]))
            for r in grid:
                if r <= 0: continue
                res, _ = scenario(model, b, rnd, [(-1, 0), (0.0, 1), (r, 0)], hazard, V, c, tc); acc("2 vote returns after r (checker's case)", res)
        # 3. an adversary that aims at the circuit's own instants, three levels deep
        for k in range(max(1, runs // 30)):
            V = rnd.choice([3.0, 3.3, 3.6, None]); c = rnd.choice(["narrow_low", "narrow_high", None]); tc = rnd.choice(["min", "max", None])
            seedk = rnd.random()
            stim = [(-1, 0), (0.0, 1)]
            for depth in range(3):
                res, simk = scenario(model, b, random.Random(seedk), stim, hazard, V, c, tc)
                acc("3 adversary aimed at the circuit's instants", res)
                marks = [m for m in event_times(simk) if m > stim[-1][0]]
                if not marks: break
                m = rnd.choice(marks); d = rnd.choice([-5e-9, -1e-9, 0.0, 5e-10, 1e-9, 2e-9, 3e-9, 5e-9, 7e-9, 1e-8, 1e-6, 3e-5])
                stim = stim + [(max(stim[-1][0] + 1e-12, m + d), 1 - stim[-1][1])]
        # 4. random vote waveforms: 1 to 30 toggles, gaps log-uniform over 1 ns to 3 ms, with and without power-good toggles
        for k in range(runs):
            t = 0.0; v = rnd.randint(0, 1); stim = [(-1, v)]
            for i in range(rnd.randint(1, 30)):
                t += 10 ** rnd.uniform(-9, math.log10(3e-3)); v = 1 - v; stim.append((t, v))
            pgs = ()
            if rnd.random() < 0.3:
                pgs = []; tp = 0.0; pv = {1: 1, 2: 1, 3: 1}
                for i in range(rnd.randint(1, 6)):
                    tp += 10 ** rnd.uniform(-8, math.log10(3e-3)); s = rnd.randint(1, 3); pv[s] = 1 - pv[s]; pgs.append((tp, "PG%d" % s, pv[s]))
                pgs.append((max(t, tp) + 1e-3, "PG1", 1)); pgs.append((max(t, tp) + 1e-3, "PG2", 1)); pgs.append((max(t, tp) + 1e-3, "PG3", 1))
            res, _ = scenario(model, b, rnd, stim, hazard, pg_stim=tuple(pgs))
            acc("4 random vote waveforms" + (" with power-good toggles" if pgs else ""), res)
    rep["totals"] = {"runs": sum(f["runs"] for f in fam.values()), "moves": sum(f["moves"] for f in fam.values()),
                     "violations": sum(f["violations"] for f in fam.values())}
    s = json.dumps(rep, indent=1, sort_keys=True, default=str)
    if "--json" in a: open(a[a.index("--json") + 1], "w").write(s + "\n")
    print("requirement: lead >= %.3f us, hold >= %.3f us" % (REQ["lead"] * 1e6, REQ["hold"] * 1e6))
    print("netlist %s: %d gates, %d Schmitt buffers, %d RC nodes; hazard model %s" % (path, len(gates), len(schmitt), len(rc), "ON" if hazard else "off"))
    for name, f in sorted(fam.items()):
        print("  %-48s runs %5d  select moves %6d  min lead %s us  min hold %s us  violations %d" % (
            name, f["runs"], f["moves"], "%.3f" % f["min_lead_us"] if f["min_lead_us"] is not None else "-",
            "%.3f" % f["min_hold_us"] if f["min_hold_us"] is not None else "-", f["violations"]))
        for e in f["examples"][:3]: print("      e.g. " + e)
    print("TOTAL runs %d, select moves %d, violations %d" % (rep["totals"]["runs"], rep["totals"]["moves"], rep["totals"]["violations"]))
    return 1 if rep["totals"]["violations"] else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
