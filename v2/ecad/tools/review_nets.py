#!/usr/bin/env python3
"""Netlist-level design review of a generated board: decoupling, floating control pins, ESD on USB pairs, I2C address map, connector mates.
Usage: review_nets.py <netlist.net> [<mate netlist.net>]"""
import sys, re, collections
def parse(s):
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', s)
    def rd(i):
        out = []
        while i < len(tok):
            t = tok[i]
            if t == "(": sub, i = rd(i + 1); out.append(sub)
            elif t == ")": return out, i + 1
            else: out.append(t); i += 1
        return out, i
    return rd(0)[0]
def uq(s): return s[1:-1] if s.startswith('"') else s
def kids(n, key): return [e for e in n if isinstance(e, list) and e and e[0] == key]
def load(path):
    nl = parse(open(path).read())[0]
    comps = {}
    for c in kids(kids(nl, "components")[0], "comp"):
        ref = uq(kids(c, "ref")[0][1]); val = uq(kids(c, "value")[0][1]); fp = uq(kids(c, "footprint")[0][1]) if kids(c, "footprint") else ""
        ls = kids(c, "libsource"); part = uq(kids(ls[0], "part")[0][1]) if ls else ""
        comps[ref] = dict(val=val, fp=fp, part=part)
    pinname = {}
    for lp in kids(kids(nl, "libparts")[0], "libpart"):
        key = (uq(kids(lp, "lib")[0][1]), uq(kids(lp, "part")[0][1]))
        for p in kids(kids(lp, "pins")[0], "pin") if kids(lp, "pins") else []:
            pinname[(key[1], uq(kids(p, "num")[0][1]))] = (uq(kids(p, "name")[0][1]), uq(kids(p, "type")[0][1]))
    nets = {}
    for n in kids(kids(nl, "nets")[0], "net"):
        name = uq(kids(n, "name")[0][1]); nets[name] = [(uq(kids(nd, "ref")[0][1]), uq(kids(nd, "pin")[0][1])) for nd in kids(n, "node")]
    return comps, pinname, nets
comps, pinname, nets = load(sys.argv[1])
byref = collections.defaultdict(dict)
for name, nodes in nets.items():
    for ref, pin in nodes: byref[ref][pin] = name
def pname(ref, pin): return pinname.get((comps[ref]["part"], pin), ("", ""))
print("== %s: %d parts, %d nets" % (sys.argv[1], len(comps), len(nets)))
issues = []
# 1. decoupling: every IC supply pin's net carries at least one capacitor
for ref, c in comps.items():
    if not ref.startswith("U"): continue
    for pin, net in byref[ref].items():
        nm, typ = pname(ref, pin)
        if typ == "power_in" or re.match(r"^(VDD|VCC|VIN|AVDD|DVDD|VDDA|VBAT|V\+|VS|VSYS|SYS|IN|PVIN|VBUS)\w*$", nm):
            caps = [r for r, p in nets.get(net, []) if r.startswith("C")]
            if not caps and net not in ("GND",): issues.append("DECOUPLING %s.%s (%s) on net %s has no capacitor" % (ref, pin, nm, net))
# 2. inputs with a single node (floating) on ICs, and control pins EN/CE/RST without a pull
for ref, c in comps.items():
    if not ref.startswith("U"): continue
    for pin, net in byref[ref].items():
        nm, typ = pname(ref, pin); nodes = nets.get(net, [])
        if net.startswith("unconnected-"): continue
        if len(nodes) == 1 and typ in ("input", "power_in"): issues.append("FLOATING %s.%s (%s, %s) alone on net %s" % (ref, pin, nm, typ, net))
        if re.match(r"^(EN|~?CE|~?RST|~?RESET|~?SHDN|MODE|BOOT0|NRST|~?PD|~?OE)\d*$", nm):
            rs = [r for r, p in nodes if r.startswith("R")]; ics = [r for r, p in nodes if r.startswith("U")]
            if not rs and len(nodes) <= 2 and not any(r.startswith("J") for r, p in nodes): issues.append("NOPULL %s.%s (%s) on net %s (%s)" % (ref, pin, nm, net, ",".join("%s.%s" % n for n in nodes)))
# 3. USB pairs: every net named USB_*_P/N must have an ESD part (USBLC6) on it
for net, nodes in nets.items():
    if re.match(r"^/?USB_\w+_(P|N|DP|DM)$", net) or net in ("/USB_DP", "/USB_DM"):
        if not any(comps[r]["val"].startswith("USBLC6") for r, p in nodes): issues.append("NOESD %s (%s)" % (net, ",".join("%s.%s" % n for n in nodes)))
# 4. I2C map: INA219 A0/A1, PCA9555 A0-2 -> addresses
addr = collections.defaultdict(list)
for ref, c in comps.items():
    if c["val"].startswith("INA219"):
        a0, a1 = byref[ref].get("7", "?"), byref[ref].get("8", "?")
        code = {"GND": 0, "+3V3": 1, "SDA": 2, "SCL": 3}
        try: addr[0x40 + code[a1] * 4 + code[a0]].append(ref)
        except KeyError: issues.append("I2C %s A0/A1 on %s/%s" % (ref, a0, a1))
    if c["val"].startswith("PCA9555"):
        bits = [1 if byref[ref].get(p) == "+3V3" else 0 for p in ("1", "2", "3")]
        addr[0x20 + bits[2] * 4 + bits[1] * 2 + bits[0]].append(ref)
    if c["val"].startswith("BQ27441"): addr[0x55].append(ref)
    if c["val"].startswith("BQ25601"): addr[0x6B].append(ref)
for a, refs in sorted(addr.items()):
    if len(refs) > 1: issues.append("I2C address 0x%02X used by %s" % (a, refs))
print("I2C map:", " ".join("0x%02X=%s" % (a, "/".join(r)) for a, r in sorted(addr.items())))
# 5. connector mate check (optional second netlist): same connector name on both sides must carry identical net names per pin
if len(sys.argv) > 2:
    comps2, pinname2, nets2 = load(sys.argv[2]); byref2 = collections.defaultdict(dict)
    for name, nodes in nets2.items():
        for ref, pin in nodes: byref2[ref][pin] = name
    for ref in set(byref) & set(byref2):
        if not ref.startswith("J_"): continue
        for pin in sorted(set(byref[ref]) | set(byref2[ref]), key=lambda p: int(p) if p.isdigit() else 0):
            a, b2 = byref[ref].get(pin, "-"), byref2[ref].get(pin, "-")
            print("  MATE %s pin %s: %s | %s" % (ref, pin, a, b2))
for i in issues: print("  " + i)
print("issues:", len(issues))
