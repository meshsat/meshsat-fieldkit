#!/usr/bin/env python3
"""check_dd7_netlist.py: DD-7's board A side read back from a regenerated board A netlist (task L4-E11, MESHSAT-1357, round 10,
4 October 2026; record l8p's round 3 findings L8P-F04 and L8P-F05).

Usage:  check_dd7_netlist.py NETLIST

NETLIST is a KiCad export form E netlist of board A: the box's `kicad-cli sch export netlist`, or record l8p's gen_netlist.py run on
a scratch copy of gen_sch_a.py with the drafts applied in L4-E9's order (the tests do the second). Every pin of every part
apply_gen_sch_a_dd7.py draws is read against the draft's map, each value against its prefix, and the circuit's properties that a
single pin row does not show:
  LOOP  the return DOCK_EN_RET reaches J_DOCK, RT1, Q44's drain and U48's SENSE1 and nothing else (no load under 1 MOhm on it);
        DOCK_EN_OUT reaches J_DOCK, RT1 and R109 alone; U48's SENSE2 sits on R109 / R144's tap;
  TRIG  U48's RESET1 is DD7_T, pulled up only from DD7_LP (R250), which is U48's RESET2; Q50's gate is DD7_T;
  HOLD  Q51 from VBAT to DD7_K, R253 from DD7_K to ground, R84 and D26 (cathode on DD7_H) into DD7_H, C241 and R85 to ground,
        U47's SENSE1 on DD7_H and its CTS1 on C248;
  REL   U47's RESET1 and RESET2 both on DD7_N; the CELL+ divider's foot DD7_REF reaches ground only through Q52 to DD7_N;
  INH   Q47 from DD7_N to SYS_INH_D, gate DD7_LP; Q49 from VBAT to CH_BATDRV, gate SYS_INH_P; Q48 and R256 from CELL+ to DD7_N;
        every gate on DD7_LP is one of Q47, Q48 and Q52;
  RST   Q44 on DOCK_EN_RET, gate DD7_G; Q45 and Q46 pull DD7_G, gates FE_RUN and DD7_N.
Exit 0: DRAWN; 4: FAIL (each failure printed); 3: NOT DRAWN (U47 absent). Nothing is written."""
import hashlib
import re
import sys

# the draft's own map: (ref, value prefix, {pin: net})
MAP = [
    ("Q44", "2N7002", {"1": "DD7_G", "2": "GND", "3": "DOCK_EN_RET"}),
    ("R106", "1M", {"1": "VIN_RAW", "2": "DD7_G"}),
    ("D25", "BZT52C12", {"1": "DD7_G", "2": "GND"}),
    ("Q45", "2N7002", {"1": "FE_RUN", "2": "GND", "3": "DD7_G"}),
    ("Q46", "2N7002", {"1": "DD7_N", "2": "GND", "3": "DD7_G"}),
    ("R233", "100k", {"1": "VBAT", "2": "DD7_VC"}),
    ("D27", "BZT52C12", {"1": "DD7_VC", "2": "GND"}),
    ("U48", "TPS37A010122", {"1": "VBAT", "2": "DOCK_EN_RET", "3": "DD7_OS", "4": "DD7_T", "5": "DD7_LP", "10": "GND", "11": "GND"}),
    ("R109", "562k 0.1%", {"1": "DOCK_EN_OUT", "2": "DD7_OS"}),
    ("R144", "422k 0.1%", {"1": "DD7_OS", "2": "GND"}),
    ("R249", "100k", {"1": "DD7_VC", "2": "DD7_LP"}),
    ("R250", "1M", {"1": "DD7_LP", "2": "DD7_T"}),
    ("Q50", "2N7002", {"1": "DD7_T", "2": "GND", "3": "DD7_AD"}),
    ("R251", "100k", {"1": "VBAT", "2": "DD7_AG"}),
    ("R252", "200k", {"1": "DD7_AG", "2": "DD7_AD"}),
    ("Q51", "AO3401A", {"1": "DD7_AG", "2": "VBAT", "3": "DD7_K"}),
    ("R253", "10k", {"1": "DD7_K", "2": "GND"}),
    ("R84", "56R", {"1": "DD7_K", "2": "DD7_KA"}),
    ("D26", "1N4148W", {"1": "DD7_H", "2": "DD7_KA"}),
    ("C241", "1u 100V", {"1": "DD7_H", "2": "GND"}),
    ("R85", "1.2M", {"1": "DD7_H", "2": "GND"}),
    ("U47", "TPS37A010122", {"1": "VBAT", "2": "DD7_H", "3": "DD7_CS", "4": "DD7_N", "5": "DD7_N", "7": "DD7_CTS", "10": "GND", "11": "GND"}),
    ("C248", "3.9n", {"1": "DD7_CTS", "2": "GND"}),
    ("R107", "464k", {"1": "CELL+", "2": "DD7_CS"}),
    ("R108", "100k", {"1": "DD7_CS", "2": "DD7_REF"}),
    ("Q52", "2N7002", {"1": "DD7_LP", "2": "DD7_N", "3": "DD7_REF"}),
    ("R254", "1M", {"1": "DD7_VC", "2": "DD7_REF"}),
    ("R255", "1M", {"1": "DD7_VC", "2": "DD7_N"}),
    ("Q47", "2N7002", {"1": "DD7_LP", "2": "DD7_N", "3": "SYS_INH_D"}),
    ("R82", "100k", {"1": "VBAT", "2": "SYS_INH_P"}),
    ("R83", "200k", {"1": "SYS_INH_P", "2": "SYS_INH_D"}),
    ("Q49", "AO3401A", {"1": "SYS_INH_P", "2": "VBAT", "3": "CH_BATDRV"}),
    ("Q48", "2N7002", {"1": "DD7_LP", "2": "DD7_N", "3": "DD7_BL"}),
    ("R256", "4.7k", {"1": "CELL+", "2": "DD7_BL"}),
    ("TP1", "DD7_H", {"1": "DD7_H"}),
    ("TP2", "DD7_N", {"1": "DD7_N"}),
]
# nets whose whole membership the circuit fixes (a part added on one is a change to the circuit, not a detail)
EXCLUSIVE = {
    "DOCK_EN_RET": {"J_DOCK", "RT1", "Q44", "U48"},
    "DOCK_EN_OUT": {"J_DOCK", "RT1", "R109"},
    "DD7_OS": {"U48", "R109", "R144"},
    "DD7_T": {"U48", "R250", "Q50"},
    "DD7_LP": {"U48", "R249", "R250", "Q47", "Q48", "Q52"},
    "DD7_H": {"D26", "C241", "R85", "U47", "TP1"},
    "DD7_N": {"U47", "Q46", "Q47", "Q48", "Q52", "R255", "TP2"},
    "DD7_REF": {"R108", "Q52", "R254"},
    "DD7_K": {"Q51", "R253", "R84"},
    "SYS_INH_D": {"Q47", "R83"},
    "SYS_INH_P": {"R82", "R83", "Q49"},
    "DD7_BL": {"Q48", "R256"},
}


def sexp(text):
    tok = re.compile(r'\(|\)|"((?:[^"\\]|\\.)*)"|([^\s()"]+)')
    stack, cur = [], []
    for m in tok.finditer(text):
        t = m.group(0)
        if t == "(":
            stack.append(cur); cur = []
        elif t == ")":
            done = cur; cur = stack.pop() if stack else []; cur.append(done)
        elif m.group(1) is not None:
            cur.append(m.group(1).replace('\\"', '"'))
        else:
            cur.append(m.group(2))
    return cur


def kv(node, key):
    for x in node[1:] if isinstance(node, list) else []:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def read_netlist(raw):
    tree = sexp(raw.decode("utf-8", "replace"))
    root = tree[0] if tree and isinstance(tree[0], list) else tree
    comps, pins = {}, {}
    for sec in (root[1:] if isinstance(root, list) else []):
        if not (isinstance(sec, list) and sec):
            continue
        if sec[0] == "components":
            for c in sec[1:]:
                if isinstance(c, list) and c and c[0] == "comp":
                    ref, val = kv(c, "ref"), kv(c, "value")
                    if ref and len(ref) > 1:
                        comps[ref[1]] = val[1] if val and len(val) > 1 else ""
        elif sec[0] == "nets":
            for n in sec[1:]:
                if not (isinstance(n, list) and n and n[0] == "net"):
                    continue
                name = str((kv(n, "name") or [None, ""])[1]).lstrip("/")
                for x in n[1:]:
                    if isinstance(x, list) and x and x[0] == "node":
                        r, p = kv(x, "ref"), kv(x, "pin")
                        if r and p and len(r) > 1 and len(p) > 1:
                            pins.setdefault(r[1], {})[p[1]] = name
    on = {}
    for r, d in pins.items():
        for p, n in d.items():
            on.setdefault(n, set()).add(r)
    return comps, pins, on


def judge(raw):
    comps, pins, on = read_netlist(raw)
    if "U47" not in comps:
        return "NOT DRAWN", ["U47 is absent: the draft is not applied"]
    bad = []
    for ref, pre, want in MAP:
        if ref not in comps:
            bad.append("%s is absent" % ref)
            continue
        if not comps[ref].startswith(pre):
            bad.append("%s's value %r does not start with %r" % (ref, comps[ref][:40], pre))
        got = pins.get(ref, {})
        for p, n in want.items():
            if got.get(p) != n:
                bad.append("%s.%s on %r, wanted %s" % (ref, p, got.get(p), n))
        extra = sorted(set(got) - set(want))
        if extra and ref not in ("U47", "U48"):
            bad.append("%s carries pins %s the draft does not draw" % (ref, extra))
    for ref in ("U47", "U48"):
        for p in ("6", "8", "9") + (("7",) if ref == "U48" else ()):
            if pins.get(ref, {}).get(p) not in (None, "NC"):
                bad.append("%s.%s on %r, wanted open (its delay pin unused)" % (ref, p, pins[ref][p]))
    for net, members in EXCLUSIVE.items():
        if on.get(net, set()) != members:
            bad.append("%s reaches %s, wanted %s" % (net, sorted(on.get(net, set())), sorted(members)))
    gates_lp = sorted(r for r, d in pins.items() if r.startswith("Q") and d.get("1") == "DD7_LP")
    if gates_lp != ["Q47", "Q48", "Q52"]:
        bad.append("the gates on DD7_LP are %s, wanted Q47, Q48 and Q52" % gates_lp)
    return ("FAIL", bad) if bad else ("DRAWN", [])


def main(argv):
    if len(argv) != 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0].strip() + "\n")
        return 2
    raw = open(argv[0], "rb").read()
    v, why = judge(raw)
    print("board A netlist sha256 %s" % hashlib.sha256(raw).hexdigest()[:16])
    for w in why:
        print("  %s" % w)
    print("DD-7 on board A (L4-E11 round 10): %s" % v)
    return {"DRAWN": 0, "FAIL": 4, "NOT DRAWN": 3}[v]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
