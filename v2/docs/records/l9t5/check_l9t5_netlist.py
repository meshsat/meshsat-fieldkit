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

ROUND 3 (record l8r2's finding L8R2-F35): decl(letter, intent, basis) holds the DECLARATIONS a patched generator writes into its
intent to their basis, which the caller computes from record l9t5's case script (never typed here): on board B the device lead's
peak is the lead's own current on C-DEV rev 1 with the draft, rounded up to 0.1 mA, and +5V_IOC's peak is the supervisors' HIGH at
constant power at that rail's least load voltage, rounded up; on board A +5V_DEV's peak is that lead plus the wall port's limit
(stream s99's construction) and +5V_IOC's the same figure, with this board's 0.5 share of the rail's 2 percent. A typed figure that
differs from its basis reads FAIL (round 2's drafts declared 6.0 A and 1.38 A).

Usage:  check_l9t5_netlist.py [a=path.net] [b=path.net]      (default: the committed netlists of the tree)
Exit 0 when every board given reads DRAWN (and the lead pair holds when both are given), 4 otherwise, 2 on a usage error."""
import hashlib
import math
import os
import re
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
# the divider a board A netlist must carry and the band its set point must stay in: I-03's draft (U601 at 5 V, as U41) and, with
# task T10's pre-regulator draft composed after it, R602 at 13.3 k (round 4; record l9t5's l9t5_t10.py)
DIVS = {"i03": (("56.2k 0.1%", "10.7k 0.1%"), (4.8, 5.2)), "t10": (("56.2k 0.1%", "13.3k 0.1%"), (4.05, 4.31)),
        # P0 round (Slot A, 5 October 2026, SESSION L9T5-D9): Slot C's set point delta iocset composed after iocpre, R602 14.0 k. The
        # band's floor 3.87 V: the least output that kept T10-A3 at 0.4512 A (SESSION L9T5-D8) with the return as drawn and no sense
        # resistor (3.6652 V + 2 % of 4.01 V + three LDOs' 0.4512 A on 42.52 mOhm + 0.0681 V = 3.871 V); after cx45 L9T5-D8 is
        # superseded by T10-A3 at the rail trip's maximum with the sense resistor's drop (a floor of about 3.78 V): the stricter 3.87 V
        # is kept, never lowered; its ceiling 4.18 V: the top that keeps the babbling supervisor's LDO at 125 C on revision V without
        # the containment (l9t5_connected.out section 10)
        "t10s": (("56.2k 0.1%", "14.0k 0.1%"), (3.87, 4.18))}


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


def mode_of(nl):
    """P0 round (V6-m1, 5 October 2026): the divider mode read from the netlist itself. R602 at T10's 13.3 k means record l9t5's iocpre
    draft is composed, and the check reads T10's band; any other value is judged against I-03's own (so a wrong value still FAILS)."""
    v = (nl.get("comps", {}).get("R602", {}).get("value", "") or "").split()
    for mode in ("t10", "t10s"):           # t10s: Slot C's iocset delta composed after iocpre (R602 14.0 k, SESSION L9T5-D9)
        if v and v[0] == DIVS[mode][0][1].split()[0]:
            return mode
    return "i03"


def checks_a(nl, div="auto"):
    if div == "auto":
        div = mode_of(nl)
    (want_top, want_bot), (v_lo, v_hi) = DIVS[div]
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
        if not (value(nl, d[2]).startswith(want_top) and value(nl, d[3]).startswith(want_bot)):
            why.append("the divider is %s over %s, wanted %s over %s" % (value(nl, d[2]), value(nl, d[3]), want_top, want_bot))
        if not (v_lo < lo and hi < v_hi):
            why.append("the output band %.3f to %.3f V leaves %s to %s V" % (lo, hi, v_lo, v_hi))
    res["DIV"] = ("FAIL" if why else "DRAWN", why)
    return res


def _guard_adds():
    """the designators record l9t5's containment delta (apply_gen_sch_b_iocguard.py, Slot C's T10 round 6) adds, read with ast from its
    ADDS expression (evaluated on literals only)"""
    import ast as _ast
    p = os.path.join(HERE, "apply_gen_sch_b_iocguard.py")
    if not os.path.isfile(p):
        return set()
    for node in _ast.parse(open(p, encoding="utf-8").read()).body:
        if isinstance(node, _ast.Assign) and any(isinstance(x, _ast.Name) and x.id == "ADDS" for x in node.targets):
            return set(eval(compile(_ast.Expression(node.value), p, "eval"), {"__builtins__": {"tuple": tuple, "range": range}}))
    return set()


def ldo_in(nl, u):
    """the LDO's input net: +5V_IOC as I-03 draws it, or behind its rail trip's sense resistor (the containment delta, L9T5-F25)"""
    n = pin(nl, u, "1")
    return n if n and re.fullmatch(r"IOC\w*_LDO_IN", n) else None


def checks_b(nl):
    if "J_5V_IOC" not in nl["pins"]:
        return {"LDO": ("NOT DRAWN", ["J_5V_IOC absent"])}
    res = {}
    guard = all(ldo_in(nl, u) for u, _r, _c in LDOS)      # P0 round after cx45 (L9T5-F25): the containment delta composed
    why = []
    for u, rr, cc in LDOS:
        en = pin(nl, u, "3")
        vin = ldo_in(nl, u) if guard else IOC
        if not guard and pin(nl, u, "1") != IOC:
            why.append("%s.1 on %r, wanted %s" % (u, pin(nl, u, "1"), IOC))
        if guard:
            # the sense resistor alone joins the LDO's input to +5V_IOC
            rs = [r for r in nl["pins"] if r.startswith("R") and two(nl, r) == sorted([IOC, vin])]
            if len(rs) != 1:
                why.append("%s's input %s is joined to %s by %s, wanted one sense resistor" % (u, vin, IOC, rs or "nothing"))
        if two(nl, rr) != sorted([IOC, en or "?"]):
            why.append("%s on %s, wanted %s to %s" % (rr, two(nl, rr), IOC, en))
        if two(nl, cc) != sorted([vin, "GND"]):
            why.append("%s on %s, wanted %s to GND" % (cc, two(nl, cc), vin))
    on_dev = [u for u, _r, _c in LDOS if pin(nl, u, "1") == "+5V_DEV"]
    if on_dev:
        why.append("%s still on +5V_DEV" % ", ".join(on_dev))
    res["LDO"] = ("FAIL" if why else "DRAWN", why)
    why = rows(nl, [("J_5V_IOC", "1", IOC), ("J_5V_IOC", "2", "GND"), ("D900", "1", IOC), ("D900", "2", "GND")])
    if two(nl, "C900") != sorted([IOC, "GND"]):
        why.append("C900 on %s" % two(nl, "C900"))
    allowed = {"J_5V_IOC", "D900", "C900"} | {x for t in LDOS for x in t} | (_guard_adds() if guard else set())
    extra = [m for m in members(nl, IOC) if m.split(".")[0] not in allowed]
    if extra:
        why.append("%s also carries %s" % (IOC, ", ".join(extra)))
    res["LEAD"] = ("FAIL" if why else "DRAWN", why)
    return res


def ceil4(x):
    """a figure rounded UP to 0.1 mA: a declaration is never under its basis."""
    return math.ceil(x * 1e4 - 1e-7) / 1e4


def rails_of(intent):
    return {k.lstrip("/"): v for k, v in (intent.get("rails") or {}).items()}


def decl(letter, intent, basis):
    """(verdict, why) for the declarations; basis = {"dev_lead": A, "ioc": A, "wall": A}, computed by the caller."""
    r = rails_of(intent)
    ioc, dev = r.get("+5V_IOC"), r.get("+5V_DEV") or {}
    if not ioc:
        return "NOT DRAWN", ["+5V_IOC is not declared"]
    why = []
    want_ioc, want_lead = ceil4(basis["ioc"]), ceil4(basis["dev_lead"])

    def peak(x):
        return float(x.get("amps_peak") or 0)
    if abs(peak(ioc) - want_ioc) > 1e-9:
        why.append("+5V_IOC declares a %.4f A peak; its basis gives %.4f A (%.6f A rounded up)" % (peak(ioc), want_ioc, basis["ioc"]))
    if abs(float(ioc.get("amps_typ") or 0) - 0.36) > 1e-9:
        why.append("+5V_IOC declares %.2f A typical, wanted 0.36" % float(ioc.get("amps_typ") or 0))
    if letter == "a":
        want = round(want_lead + basis["wall"], 4)
        if abs(peak(dev) - want) > 1e-9:
            why.append("+5V_DEV declares a %.4f A peak; board B's lead %.4f A plus the wall port's %.4f A is %.4f A" % (peak(dev), want_lead, basis["wall"], want))
        if (ioc.get("source"), ioc.get("switch"), ioc.get("fed_from")) != ("L601", "U601", "VBAT"):
            why.append("+5V_IOC's source, switch and feed are %r" % ((ioc.get("source"), ioc.get("switch"), ioc.get("fed_from")),))
        if abs(float(ioc.get("share") or 0) - 0.005) > 1e-12:
            why.append("+5V_IOC's share of its budget on board A is %r, wanted 0.005 (board B's is 0.015 of the 0.02)" % ioc.get("share"))
        if ioc.get("loads") != {"J_5V_IOC": 0.36}:
            why.append("+5V_IOC's loads are %r, wanted the typical allocation at J_5V_IOC" % ioc.get("loads"))
    else:
        if abs(peak(dev) - want_lead) > 1e-9:
            why.append("+5V_DEV (the device lead) declares a %.4f A peak; its basis gives %.4f A (%.6f A rounded up)" % (peak(dev), want_lead, basis["dev_lead"]))
        left = sorted(u for u, _r, _c in LDOS if u in (dev.get("loads") or {}))
        if left:
            why.append("+5V_DEV still allocates %s" % ", ".join(left))
        if ioc.get("source") != "J_5V_IOC" or sorted(ioc.get("loads") or {}) != sorted(u for u, _r, _c in LDOS):
            why.append("+5V_IOC's source and loads are %r, %r" % (ioc.get("source"), sorted(ioc.get("loads") or {})))
        if abs(float(ioc.get("share") or 0) - 0.015) > 1e-12:
            why.append("+5V_IOC's share on board B is %r, wanted 0.015" % ioc.get("share"))
        for n in ("+3V3_IOCA", "+3V3_IOCB", "+3V3_IOCC"):
            if (r.get(n) or {}).get("fed_from") != "+5V_IOC":
                why.append("%s is fed from %r" % (n, (r.get(n) or {}).get("fed_from")))
        src = (r.get("GND") or {}).get("source")
        if "J_5V_IOC" not in (src if isinstance(src, list) else [src]):
            why.append("GND does not name J_5V_IOC a source")
    return ("FAIL" if why else "DRAWN"), why


RETURN_SOCKETS = ("J_GR1", "J_GR2", "J_GR3")     # record l8r2's round 8 draft: three XT60 sockets, both contacts on GND, on each board


def return_drawn(nl):
    """(verdict, why): record l8r2's dedicated ground return between boards A and B as this netlist carries it. DRAWN: the three
    sockets each with pins 1 and 2 on GND; NOT DRAWN: none present; FAIL: some present or a contact off GND. Round 4: record
    l9t5's connected-path row reads which return figures apply from this, never from a typed flag."""
    have = [j for j in RETURN_SOCKETS if j in nl["pins"]]
    if not have:
        return "NOT DRAWN", ["no return socket"]
    why = ["%s absent" % j for j in RETURN_SOCKETS if j not in nl["pins"]]
    why += ["%s.%s on %r, wanted GND" % (j, p_, pin(nl, j, p_)) for j in have for p_ in ("1", "2") if pin(nl, j, p_) != "GND"]
    return ("FAIL" if why else "DRAWN"), why


def check_pair(a, b):
    why = []
    for p in ("1", "2"):
        if pin(a, "J_5V_IOC", p) != pin(b, "J_5V_IOC", p):
            why.append("pin %s: A %r, B %r" % (p, pin(a, "J_5V_IOC", p), pin(b, "J_5V_IOC", p)))
    fa, fb = a["comps"].get("J_5V_IOC", {}).get("footprint", ""), b["comps"].get("J_5V_IOC", {}).get("footprint", "")
    if not fa or fa != fb:
        why.append("the lands differ: A %r, B %r" % (fa, fb))
    return ("FAIL" if why else "DRAWN"), why


def judge(letter, nl, div="auto"):
    res = checks_a(nl, div) if letter == "a" else checks_b(nl)
    lines = ["%s %-4s %s%s" % (letter.upper(), k, v, (": " + "; ".join(why[:3])) if why else "") for k, (v, why) in res.items()]
    vs = [v for v, _w in res.values()]
    worst = "DRAWN" if all(v == "DRAWN" for v in vs) else ("FAIL" if "FAIL" in vs else "NOT DRAWN")
    return worst, lines


def run(paths, repo=REPO, out=sys.stdout, label=None, div="auto"):
    verdicts, nls = {}, {}
    for letter in ("a", "b"):
        if letter not in paths:
            continue
        raw = open(paths[letter], "rb").read()
        name = label(letter) if label else os.path.relpath(paths[letter], repo)
        out.write("%s sha256 %s\n" % (name, hashlib.sha256(raw).hexdigest()[:16]))
        nls[letter] = read(raw)
        v, lines = judge(letter, nls[letter], div)
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
