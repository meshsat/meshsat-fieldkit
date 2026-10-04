#!/usr/bin/env python3
"""check_l9t5_netlist.py: what the regenerated netlists of boards A and B must show for record l9t5's I-03 drafts (Layer 9, task T5,
MESHSAT-1357, 4 October 2026): the three supervisors' 5 V on board A's own TPS62933 U601, over its own JST-VH lead J_5V_IOC, into
board B's three AP2112K LDOs U40, U50 and U60. It PARSES the netlists (record l8p's s-expression reader, never a grep) and judges:

  board A  BUCK  U601 pins 2 EN on RAIL_EN, 3 VIN on VBAT, 4 GND, 5 SW IOCB_SW, 6 BST IOCB_BST, 7 SS IOCB_SS, 8 FB IOCB_FB;
                 L601 from IOCB_SW to +5V_IOC; C601 BST to SW; C602 SS to GND; C603 and C604 VBAT to GND; C605 and C606 +5V_IOC to
                 GND; R601 +5V_IOC to IOCB_FB over R602 IOCB_FB to GND (the top and the bottom read from the netlist's topology)
           LEAD  J_5V_IOC pin 1 +5V_IOC, pin 2 GND; nothing on +5V_IOC but L601, C605, C606, R601 and J_5V_IOC
           EN    U601's enable is RAIL_EN, the enable of U12 (board A's +3V3 buck): U12 pin 2 and U601 pin 2 on one net, R42 from
                 DEV_EN to +3V3 (the device rail's enable pulled up to U12's rail), U7 pin 1 on DEV_EN; so +5V_DEV can be up only
                 while +3V3 is, that is while RAIL_EN is high, and then U601 is enabled (the condition of record l9t5 out 5)
           DEV   U7's device rail keeps its shunt and lead: J_5V_DEV pin 1 on +5V_DEV; no U601, L601 or J_5V_IOC node on +5V_DEV
           DIV   the divider's values are 56.2k over 10.7k (0.1 percent), the TPS62933's output then 5.002 V nominal
  board B  LDO   U40, U50 and U60 pin 1 (VIN) on +5V_IOC; their EN pull-ups R66, R78 and R90 from +5V_IOC; their input capacitors
                 C400, C420 and C440 from +5V_IOC to GND; none of the three LDOs' VIN on +5V_DEV
           LEAD  J_5V_IOC pin 1 +5V_IOC, pin 2 GND; D900 (SMBJ5.0A, cathode pin 1) on +5V_IOC; C900 +5V_IOC to GND; nothing else on +5V_IOC
                 but the parts above
  BOTH     the lead's two ends carry the same nets pin for pin, on the same land (VH2)
Each board reads DRAWN (every property holds), NOT DRAWN (U601 on A, or J_5V_IOC on B, is absent: today's state) or FAIL.
Nothing has been built or measured: the statements are about netlists.

Usage:  check_l9t5_netlist.py [a=path.net] [b=path.net]      (default: the committed netlists of the tree)
Exit 0 when every board given reads DRAWN (and the lead pair holds when both are given), 4 otherwise, 2 on a usage error."""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(REPO, "v2", "docs", "records", "l8p"))
import check_l8p_netlist as L8P  # noqa: E402  (its read_netlist: an s-expression reader)

COMMITTED = {"a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "b": "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net"}
IOC = "+5V_IOC"
VFB = (0.784, 0.800, 0.816)           # V, TPS62933 VFB over TJ -40 to 150 C (TI SLUSEA4D 8.5): read by l9t5_drafts.py, held here as its check
LDOS = (("U40", "R66", "C400"), ("U50", "R78", "C420"), ("U60", "R90", "C440"))


def read(raw):
    return L8P.read_netlist(raw)


def pin(nl, ref, p):
    return nl["pins"].get(ref, {}).get(p)


def rows(nl, want):
    return ["%s.%s on %r, wanted %s" % (r, p, pin(nl, r, p), n) for r, p, n in want if pin(nl, r, p) != n]


def two(nl, ref):
    return sorted(set(nl["pins"].get(ref, {}).values()))


def members(nl, net):
    return sorted("%s.%s" % (r, p) for r, d in nl["pins"].items() for p, n in d.items() if n == net)


def value(nl, ref):
    return nl["comps"].get(ref, {}).get("value", "")


def kohm(v):
    t = v.split()[0].lower()
    return float(t[:-1]) * 1e3 if t.endswith("k") else float(t)


def divider(nl):
    """(top ohms, bottom ohms, top ref, bottom ref) read from the topology: the top joins +5V_IOC to IOCB_FB, the bottom IOCB_FB to GND."""
    top = [r for r in ("R601", "R602") if two(nl, r) == sorted([IOC, "IOCB_FB"])]
    bot = [r for r in ("R601", "R602") if two(nl, r) == sorted(["GND", "IOCB_FB"])]
    if len(top) != 1 or len(bot) != 1:
        return None
    return kohm(value(nl, top[0])), kohm(value(nl, bot[0])), top[0], bot[0]


def vout_band(top, bot, tol=0.001, tcr=25e-6, dt=65.0, ifb=0.15e-6):
    """the buck's output from the divider, every term one way: VFB's printed band, the resistors' tolerance and TCR over dt, the FB
    leakage through the top resistor either way (its sign is not printed; the s99a method for U41: 4.872 to 5.133 V)."""
    e = tol + tcr * dt
    lo = VFB[0] * (1 + top * (1 - e) / (bot * (1 + e))) - ifb * top * (1 - e)
    hi = VFB[2] * (1 + top * (1 + e) / (bot * (1 - e))) + ifb * top * (1 + e)
    return lo, VFB[1] * (1 + top / bot), hi


def checks_a(nl):
    if "U601" not in nl["pins"]:
        return {"BUCK": ("NOT DRAWN", ["U601 absent"])}
    res = {}
    why = rows(nl, [("U601", "2", "RAIL_EN"), ("U601", "3", "VBAT"), ("U601", "4", "GND"), ("U601", "5", "IOCB_SW"), ("U601", "6", "IOCB_BST"),
                    ("U601", "7", "IOCB_SS"), ("U601", "8", "IOCB_FB")])
    for ref, nets in (("L601", ["IOCB_SW", IOC]), ("C601", ["IOCB_BST", "IOCB_SW"]), ("C602", ["GND", "IOCB_SS"]), ("C603", ["GND", "VBAT"]),
                      ("C604", ["GND", "VBAT"]), ("C605", [IOC, "GND"]), ("C606", [IOC, "GND"])):
        if two(nl, ref) != sorted(nets):
            why.append("%s on %s, wanted %s" % (ref, two(nl, ref), sorted(nets)))
    d = divider(nl)
    if d is None:
        why.append("R601 and R602 are not a divider from %s over IOCB_FB to GND" % IOC)
    res["BUCK"] = ("FAIL" if why else "DRAWN", why)
    why = rows(nl, [("J_5V_IOC", "1", IOC), ("J_5V_IOC", "2", "GND")])
    extra = [m for m in members(nl, IOC) if m.split(".")[0] not in ("L601", "C605", "C606", "R601", "R602", "J_5V_IOC")]
    if extra:
        why.append("%s also carries %s" % (IOC, ", ".join(extra)))
    res["LEAD"] = ("FAIL" if why else "DRAWN", why)
    why = rows(nl, [("U12", "2", "RAIL_EN"), ("U7", "1", "DEV_EN")])
    if two(nl, "R42") != sorted(["DEV_EN", "+3V3"]):
        why.append("R42 on %s, wanted DEV_EN to +3V3" % two(nl, "R42"))
    if pin(nl, "U601", "2") != pin(nl, "U12", "2"):
        why.append("U601's enable %r is not U12's %r" % (pin(nl, "U601", "2"), pin(nl, "U12", "2")))
    res["EN"] = ("FAIL" if why else "DRAWN", why)
    why = rows(nl, [("J_5V_DEV", "1", "+5V_DEV"), ("J_5V_DEV", "2", "GND")])
    bad = [m for m in members(nl, "+5V_DEV") if m.split(".")[0] in ("U601", "L601", "J_5V_IOC", "R601", "C605", "C606")]
    if bad:
        why.append("+5V_DEV carries %s" % ", ".join(bad))
    res["DEV"] = ("FAIL" if why else "DRAWN", why)
    why = []
    if d is None:
        why.append("no divider to read")
    else:
        lo, nom, hi = vout_band(d[0], d[1])
        if not (value(nl, d[2]).startswith("56.2k 0.1%") and value(nl, d[3]).startswith("10.7k 0.1%")):
            why.append("the divider is %s over %s, wanted 56.2k 0.1%% over 10.7k 0.1%%" % (value(nl, d[2]), value(nl, d[3])))
        if not (4.8 < lo and hi < 5.2):
            why.append("the output band %.3f to %.3f V leaves 4.8 to 5.2 V" % (lo, hi))
    res["DIV"] = ("FAIL" if why else "DRAWN", why)
    return res


def checks_b(nl):
    if "J_5V_IOC" not in nl["pins"]:
        return {"LDO": ("NOT DRAWN", ["J_5V_IOC absent"])}
    res = {}
    want = []
    for u, rr, cc in LDOS:
        want.append((u, "1", IOC))
    why = rows(nl, want)
    for u, rr, cc in LDOS:
        en = pin(nl, u, "3")
        if two(nl, rr) != sorted([IOC, en or "?"]):
            why.append("%s on %s, wanted %s to %s" % (rr, two(nl, rr), IOC, en))
        if two(nl, cc) != sorted([IOC, "GND"]):
            why.append("%s on %s, wanted %s to GND" % (cc, two(nl, cc), IOC))
    on_dev = [u for u, _r, _c in LDOS if pin(nl, u, "1") == "+5V_DEV"]
    if on_dev:
        why.append("%s still on +5V_DEV" % ", ".join(on_dev))
    res["LDO"] = ("FAIL" if why else "DRAWN", why)
    why = rows(nl, [("J_5V_IOC", "1", IOC), ("J_5V_IOC", "2", "GND"), ("D900", "1", IOC), ("D900", "2", "GND")])
    if two(nl, "C900") != sorted([IOC, "GND"]):
        why.append("C900 on %s" % two(nl, "C900"))
    allowed = {"J_5V_IOC", "D900", "C900"} | {x for t in LDOS for x in t}
    extra = [m for m in members(nl, IOC) if m.split(".")[0] not in allowed]
    if extra:
        why.append("%s also carries %s" % (IOC, ", ".join(extra)))
    res["LEAD"] = ("FAIL" if why else "DRAWN", why)
    return res


def check_pair(a, b):
    why = []
    for p in ("1", "2"):
        if pin(a, "J_5V_IOC", p) != pin(b, "J_5V_IOC", p):
            why.append("pin %s: A %r, B %r" % (p, pin(a, "J_5V_IOC", p), pin(b, "J_5V_IOC", p)))
    fa, fb = a["comps"].get("J_5V_IOC", {}).get("footprint", ""), b["comps"].get("J_5V_IOC", {}).get("footprint", "")
    if not fa or fa != fb:
        why.append("the lands differ: A %r, B %r" % (fa, fb))
    return ("FAIL" if why else "DRAWN"), why


def judge(letter, nl):
    res = {"a": checks_a, "b": checks_b}[letter](nl)
    lines = ["%s %-4s %s%s" % (letter.upper(), k, v, (": " + "; ".join(why[:3])) if why else "") for k, (v, why) in res.items()]
    vs = [v for v, _w in res.values()]
    worst = "DRAWN" if all(v == "DRAWN" for v in vs) else ("FAIL" if "FAIL" in vs else "NOT DRAWN")
    return worst, lines


def run(paths, repo=REPO, out=sys.stdout, label=None):
    verdicts, nls = {}, {}
    for letter in ("a", "b"):
        if letter not in paths:
            continue
        raw = open(paths[letter], "rb").read()
        name = label(letter) if label else os.path.relpath(paths[letter], repo)
        out.write("%s sha256 %s\n" % (name, hashlib.sha256(raw).hexdigest()[:16]))
        nls[letter] = read(raw)
        v, lines = judge(letter, nls[letter])
        verdicts[letter] = v
        for l in lines:
            out.write("  %s\n" % l)
    if set(nls) == {"a", "b"} and all(v == "DRAWN" for v in verdicts.values()):
        v, why = check_pair(nls["a"], nls["b"])
        verdicts["pair"] = v
        out.write("  PAIR %s%s\n" % (v, (": " + "; ".join(why[:3])) if why else ""))
    vs = list(verdicts.values())
    kit = "DRAWN" if vs and all(v == "DRAWN" for v in vs) else ("FAIL" if "FAIL" in vs else "NOT DRAWN")
    out.write("record l9t5's supervisors' buck and lead on the netlists: %s\n" % kit)
    return kit, verdicts


def main(argv):
    paths = {}
    for a in argv:
        if len(a) > 2 and a[0] in "ab" and a[1] == "=":
            paths[a[0]] = a[2:]
        else:
            sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
            return 2
    kit, _v = run(paths or {k: os.path.join(REPO, v) for k, v in COMMITTED.items()})
    return 0 if kit == "DRAWN" else 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
