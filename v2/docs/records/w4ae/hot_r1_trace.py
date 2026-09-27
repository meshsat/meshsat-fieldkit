#!/usr/bin/env python3
"""HOT-R1 and the hot stop's H2, traced on the committed netlists (MESHSAT-1357, stream w4ae, 27 September 2026).

WHAT IT ANSWERS. REQ-077's desk acceptance asks that "the committed netlists carry a path from the pack gauge's cell
temperatures to the control that removes the kit's load which needs no compute module" (HOT-R1, SC-50). This script
walks that path hop by hop on the six boards' committed netlists and the three cross-board contracts that join them
(v2/ecad/tools/pcb_interfaces.yaml IF-AE-DOCK, IF-AB-RIBBON, IF-BC-PANEL), and prints each hop with every other node on
the conductor. Each hop is an assertion: a missing one stops the walk and the script exits 1, naming it. It reads
netlists and one YAML file and writes nothing.

THE CHAIN (what the walk must find):
  detect   E U10 (the sensor controller, the gauge's SMBus host on J_SMB) pin 30 = GPIO19 drives a 2N7002's gate, which
           has a resistor to ground; the transistor's source is GND and its drain is on J_BLK pin 12.
  dock     IF-AE-DOCK pin 12: E J_BLK.12 to A J_DOCK.12.
  read     A J_DOCK.12 lands on U27 (PCA9555) pin 18 (P15) and has a resistor to +3V3, U27's own VCC (U27.24).
  alert    U27 pin 1 (INT) is EXP_INT: A J_AB1.13, IF-AB-RIBBON pin 13, B J_AB1.13 to B J_PANEL.6, IF-BC-PANEL pin 6,
           C J_PANEL.6 to C U3 pin 36 = GPIO24 (the panel controller).
  bus      U27's SDA (pin 23) and SCL (pin 22): A J_AB1.11/12, B, J_PANEL.4/5, C U3 pins 2/3 = GPIO0/1.
  act      C U3 pin 30 = GPIO19 is PI_KILL: C J_PANEL.25, IF-BC-PANEL pin 25, B J_PANEL.25 to B J_AB1.10, IF-AB-RIBBON
           pin 10, A J_AB1.10 to Q1's gate (pin 1), which has a resistor to ground; Q1's source is GND and its drain is
           KILL, U1 (LTC2954) pin 8, with a resistor to +3V3; U1 pin 6 is RAIL_EN, which enables U12 (A's +3V3 buck).
  power    what keeps the path alive with no compute module: E U10 on +3V3_E6 from U13 on +5V_E6 from U12, whose EN
           (pin 2) is on CELL_F (the pack); A U27 on +3V3 from U12 (EN RAIL_EN, the LTC2954); C U3 on C's +3V3 from U5,
           whose input is C's +5V = J_PANEL.1/2 = B PANEL_5V behind B F1 from B's +5V_DEV on J_5V_DEV.1, IF-AB-POWER to
           A J_5V_DEV.1 = A +5V_DEV, whose converter U7 is enabled by DEV_EN (U27 P07 with a pull-up resistor).
RP2040 QFN-56 pin numbers are from the RP2040 datasheet 1.4.1, Figure 3 (v2/vendor/rp2040/rpi-rp2040-datasheet.pdf,
printed p.11): pin 2 GPIO0, 3 GPIO1, 30 GPIO19, 36 GPIO24.

Usage: hot_r1_trace.py <tree root holding v2/>      Exit 0: every hop found; 1: a hop is missing (named)."""
import os, re, sys

try:
    import yaml
except ImportError:
    yaml = None

BOARDS = {"a": "pcb-a-power-a23/out/pcb-a-power.net", "b": "pcb-b-compute-b19/out/pcb-b-compute.net",
          "c": "pcb-c-display-c8/out/pcb-c-display.net", "e": "pcb-e1-dock-e7/out/pcb-e1-dock.net"}
RP2040_GPIO = {2: "GPIO0", 3: "GPIO1", 30: "GPIO19", 36: "GPIO24"}


def _tokens(s):
    return re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', s)


def _parse(s):
    toks = _tokens(s); pos = 0
    def rd():
        nonlocal pos
        t = toks[pos]; pos += 1
        if t == "(":
            out = []
            while toks[pos] != ")": out.append(rd())
            pos += 1; return out
        return t[1:-1] if t.startswith('"') else t
    return rd()


def _find(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


class Net:
    """One board's netlist: pin -> net, net -> pins, ref -> value."""
    def __init__(self, path):
        root = _parse(open(path, encoding="utf-8").read())
        self.value, self.pin, self.nets = {}, {}, {}
        for c in _find(_find(root, "components")[0], "comp"):
            ref = _find(c, "ref")[0][1]; v = _find(c, "value")
            self.value[ref] = v[0][1] if v else ""
        for n in _find(_find(root, "nets")[0], "net"):
            name = _find(n, "name")[0][1].lstrip("/")
            pins = set()
            for nd in _find(n, "node"):
                r = _find(nd, "ref")[0][1]; p = _find(nd, "pin")[0][1]
                pins.add((r, p)); self.pin["%s.%s" % (r, p)] = name
            self.nets[name] = pins

    def net(self, rp):
        return self.pin.get(rp)

    def on(self, rp):
        return sorted("%s.%s" % x for x in self.nets.get(self.net(rp), ()))

    def two_terminal_to(self, net, other):
        """Resistors joining `net` to `other` (by name or a predicate)."""
        out = []
        for r, p in self.nets.get(net, ()):
            if not re.match(r"^R\d", r): continue
            q = "2" if p == "1" else "1"
            o = self.pin.get("%s.%s" % (r, q))
            if (other(o) if callable(other) else o == other): out.append("%s (%s, to %s)" % (r, self.value.get(r, "?"), o))
        return out


class Walk:
    def __init__(self, root):
        self.root = root
        ecad = os.path.join(root, "v2", "ecad")
        self.b = {k: Net(os.path.join(ecad, v)) for k, v in BOARDS.items()}
        self.lines, self.bad = [], []
        self.ifc = {}
        if yaml:
            y = yaml.safe_load(open(os.path.join(ecad, "tools", "pcb_interfaces.yaml"), encoding="utf-8"))
            def walk(x):
                if isinstance(x, dict):
                    for k, v in x.items():
                        if isinstance(k, str) and k.startswith("IF-") and isinstance(v, dict): self.ifc[k] = v
                        walk(v)
                elif isinstance(x, list):
                    for v in x: walk(v)
            walk(y)

    def ok(self, cond, text):
        self.lines.append(("  ok   " if cond else "  MISSING ") + text)
        if not cond: self.bad.append(text)
        return cond

    def hop(self, board, rp, want_net=None):
        n = self.b[board].net(rp)
        good = n is not None and (want_net is None or n == want_net)
        self.ok(good, "%s %s is on %s%s; the conductor carries %s" % (board.upper(), rp, n,
                "" if want_net is None or n == want_net else " (expected %s)" % want_net,
                ", ".join(self.b[board].on(rp)) if n else "-"))
        return n

    def same(self, board, rp, net, why):
        n = self.b[board].net(rp)
        return self.ok(n == net and n is not None, "%s %s is on %s too (%s)" % (board.upper(), rp, n, why))

    def contract(self, ifid, pin, a_board, a_rp, b_board, b_rp):
        """The contract's pin map names this pin, and the two ends' nets agree with it (aliases allowed)."""
        n1, n2 = self.b[a_board].net(a_rp), self.b[b_board].net(b_rp)
        c = self.ifc.get(ifid) or {}
        declared = (c.get("pins") or {}).get(pin) if c else None
        alias = {n for pair in (c.get("aliases") or []) for n in pair[:2] if isinstance(pair, list)} if c else set()
        names = {str(declared)} | (alias if str(declared) in alias else set())
        good = n1 is not None and n2 is not None and (not c or n1 in names or n2 in names)
        self.ok(good, "%s pin %s: %s %s (%s) mates %s %s (%s); the contract names %s%s" % (
            ifid, pin, a_board.upper(), a_rp, n1, b_board.upper(), b_rp, n2, declared,
            "" if c else " (pcb_interfaces.yaml not read: PyYAML absent)"))

    def run(self):
        E, A, B, C = (self.b[k] for k in "eabc")
        self.lines.append("detect (board E)")
        g = self.hop("e", "U10.30")
        self.ok(g is not None and not g.startswith("unconnected"), "U10 pin 30 (%s) drives a net, not a no-connect" % RP2040_GPIO[30])
        qs = sorted(r for r, p in E.nets.get(g, ()) if re.match(r"^Q\d", r) and p == "1")
        self.ok(bool(qs), "a transistor's gate (pin 1) on %s: %s" % (g, ", ".join(qs) or "none"))
        q = qs[0] if qs else None
        if q:
            self.ok(E.value.get(q, "").startswith("2N7002"), "%s is a 2N7002 (%s)" % (q, E.value.get(q)))
            self.same("e", q + ".2", "GND", "the source on ground: an open drain")
            self.ok(bool(E.two_terminal_to(g, "GND")), "the gate held off by a resistor to GND: %s" % (", ".join(E.two_terminal_to(g, "GND")) or "none"))
            d = self.hop("e", q + ".3")
            self.same("e", "J_BLK.12", d, "the drain is on the dock's contact 12")
            self.ok(not E.two_terminal_to(d, lambda o: bool(o) and o.startswith("+")), "board E puts no pull-up on the line (open drain only): %s" % (", ".join(E.two_terminal_to(d, lambda o: bool(o) and o.startswith("+"))) or "none"))
        self.lines.append("dock")
        self.contract("IF-AE-DOCK", 12, "e", "J_BLK.12", "a", "J_DOCK.12")
        self.lines.append("read (board A)")
        s = self.hop("a", "J_DOCK.12")
        self.same("a", "U27.18", s, "U27 P15, an input")
        self.ok(A.value.get("U27", "").startswith("PCA9555"), "U27 is a PCA9555 (%s)" % A.value.get("U27"))
        vcc = A.net("U27.24")
        pu = A.two_terminal_to(s, vcc)
        self.ok(bool(pu), "the line's pull-up goes to U27's own VCC (%s): %s" % (vcc, ", ".join(pu) or "none"))
        self.lines.append("alert: U27's INT to the panel controller")
        i = self.hop("a", "U27.1", "EXP_INT")
        self.same("a", "J_AB1.13", i, "out on the A to B ribbon")
        self.contract("IF-AB-RIBBON", 13, "a", "J_AB1.13", "b", "J_AB1.13")
        ib = self.hop("b", "J_AB1.13")
        self.same("b", "J_PANEL.6", ib, "on to the panel ribbon")
        self.contract("IF-BC-PANEL", 6, "b", "J_PANEL.6", "c", "J_PANEL.6")
        ic = self.hop("c", "J_PANEL.6")
        self.same("c", "U3.36", ic, "the panel controller's %s" % RP2040_GPIO[36])
        self.lines.append("bus: the panel controller reads U27")
        for upin, apin, ppin, cpin in (("23", "11", 4, "2"), ("22", "12", 5, "3")):
            n = self.hop("a", "U27." + upin)
            self.same("a", "J_AB1." + apin, n, "U27's %s on the ribbon" % n)
            self.contract("IF-AB-RIBBON", int(apin), "a", "J_AB1." + apin, "b", "J_AB1." + apin)
            nb = B.net("J_AB1." + apin)
            self.same("b", "J_PANEL.%d" % ppin, nb, "the same conductor on board B")
            self.contract("IF-BC-PANEL", ppin, "b", "J_PANEL.%d" % ppin, "c", "J_PANEL.%d" % ppin)
            self.same("c", "U3." + cpin, C.net("J_PANEL.%d" % ppin), "the panel controller's %s" % RP2040_GPIO[int(cpin)])
        self.lines.append("act: PI_KILL back to board A")
        k = self.hop("c", "U3.30")
        self.ok(k == "PI_KILL", "the panel controller's %s is PI_KILL (%s)" % (RP2040_GPIO[30], k))
        self.same("c", "J_PANEL.25", k, "out on the panel ribbon")
        self.contract("IF-BC-PANEL", 25, "c", "J_PANEL.25", "b", "J_PANEL.25")
        kb = self.hop("b", "J_PANEL.25")
        self.same("b", "J_AB1.10", kb, "on to the A to B ribbon")
        self.contract("IF-AB-RIBBON", 10, "b", "J_AB1.10", "a", "J_AB1.10")
        ka = self.hop("a", "J_AB1.10")
        self.same("a", "Q1.1", ka, "Q1's gate")
        self.ok(bool(A.two_terminal_to(ka, "GND")), "PI_KILL held low on board A: %s" % (", ".join(A.two_terminal_to(ka, "GND")) or "none"))
        self.same("a", "Q1.2", "GND", "Q1's source")
        kl = self.hop("a", "Q1.3")
        self.same("a", "U1.8", kl, "the LTC2954's KILL (%s)" % A.value.get("U1", "?")[:28])
        self.ok(bool(A.two_terminal_to(kl, "+3V3")), "KILL held high: %s" % (", ".join(A.two_terminal_to(kl, "+3V3")) or "none"))
        en = self.hop("a", "U1.6")
        self.same("a", "U12.2", en, "the +3V3 buck's EN (%s)" % A.value.get("U12", "?")[:30])
        self.lines.append("power: no compute module in the path")
        self.same("e", "U10.1", "+3V3_E6", "the sensor controller's IOVDD")
        self.same("e", "U13.5", "+3V3_E6", "its LDO's output")
        self.same("e", "U13.1", "+5V_E6", "the LDO's input")
        self.same("e", "U12.1", "+5V_E6", "the AP63205's output (FB)")
        self.same("e", "U12.2", "CELL_F", "the AP63205's EN on the pack node: on whenever a pack is fitted")
        self.same("a", "U27.24", "+3V3", "U27's VCC")
        self.ok(A.value.get("U12", "").startswith("TPS62933"), "A U12 (the +3V3 buck whose EN is RAIL_EN) is %s" % A.value.get("U12", "?")[:40])
        self.same("c", "U3.1", "+3V3", "the panel controller's IOVDD")
        self.same("c", "U5.5", "+3V3", "C's LDO output")
        cin = C.net("U5.1")
        self.same("c", "J_PANEL.1", cin, "C's LDO input is the panel ribbon's supply")
        self.contract("IF-BC-PANEL", 1, "c", "J_PANEL.1", "b", "J_PANEL.1")
        pb = B.net("J_PANEL.1")
        self.ok(pb is not None and B.net("F1.2") == pb, "B's panel supply %s is behind F1 (%s)" % (pb, B.value.get("F1", "?")[:34]))
        f1 = B.net("F1.1")
        self.same("b", "J_5V_DEV.1", f1, "F1 is fed from B's J_5V_DEV")
        self.ok(A.net("J_5V_DEV.1") == "+5V_DEV", "IF-AB-POWER J_5V_DEV pin 1 (1 = the rail on both ends): A %s, B %s" % (A.net("J_5V_DEV.1"), f1))
        self.same("a", "U7.12", "+5V_DEV", "the LM5176 stage U7 makes +5V_DEV")
        de = self.hop("a", "U7.1")
        self.same("a", "U27.11", de, "U7's EN is U27 P07")
        self.ok(bool(A.two_terminal_to(de, "+3V3")), "DEV_EN pulled up, so +5V_DEV starts with +3V3: %s" % (", ".join(A.two_terminal_to(de, "+3V3")) or "none"))
        cm5 = [x for x in ("U30A", "U30B", "U31A", "U31B", "U32A", "U32B") if x in B.value]
        touched = set()
        for n in (ib, B.net("J_AB1.11"), B.net("J_AB1.12"), kb, pb, f1):
            touched |= {r for r, p in B.nets.get(n, ())}
        self.ok(not (set(cm5) & touched), "no compute module part (%s) is on any board B conductor of the path" % ", ".join(cm5))
        return not self.bad


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    w = Walk(sys.argv[1]); good = w.run()
    print("\n".join(w.lines))
    print("RESULT: %s" % ("EVERY HOP FOUND" if good else "%d HOP(S) MISSING: %s" % (len(w.bad), "; ".join(w.bad[:3]))))
    sys.exit(0 if good else 1)
