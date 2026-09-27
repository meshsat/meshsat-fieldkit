#!/usr/bin/env python3
"""Is a board's list of SWITCHING nets complete? (rule ANA-001's second report, MESHSAT-862, 19 September 2026)

ANA-001 measures a sensitive node's clearance from the nearest SWITCHING copper, and which copper is switching
is read from `pcb_sensitive.yaml`'s `switch_nets` patterns for that board. So the rule's denominator is a
declaration, and `sensitive_nodes.py` already refuses the mirror image of the mistake: a SENSITIVE net that
carries a transistor or inductor pad is a power conductor and the declaration is about the wrong side of the
filter (18 September 2026). Nothing asks the other half. A net that IS switching copper and is not in the
list is not measured against, and the reading that comes back is a PASS taken against an incomplete list,
which is the same shape as a pass on a denominator of zero.

**It is a REPORT and it decides nothing.** Whether a given power node is "switching" for this rule is an
engineering judgement (a synchronous converter's midpoint certainly is; a hot-swap pass element that switches
once at power-up is arguable; a protection pair's common drain is arguable the other way), and a tool that
turned its own heuristic into a verdict would be asserting that judgement. What it does is put the candidates
in front of whoever writes the declaration, with the parts that make each one a candidate named.

THE PREDICATE, stated so it can be argued with, and RANKED because it knows more about one half than the
other. A net is switching-shaped when it carries the DRAIN or SOURCE pad of a transistor. It is **STRONG**
when an inductor's pad is on it too, which is the node between a switching device and its energy store and is
what this rule is about; it is **WEAK** when two different transistors' drain or source pads are on it and no
inductor is, which is the shape of a half bridge and also the shape of an open-drain logic bus, so it is
reported and ranked rather than asserted.

Three exclusions, each from evidence rather than from a name. A gate is excluded by its PIN FUNCTION, because
a gate drives the switching and is not the switching copper. The board's own POURED nets are excluded, because
a plane is a rail by construction and every converter's output pour carries the pad that feeds it. And a net
the INTENT declares as a rail, or as a node whose voltage is zero at both ends, is excluded, because a rail is
a rail and a return is a return: board E's GND_V carries a 2N7002's source and the return winding of a
common-mode choke, which reads exactly like a switch node and is the vehicle-side ground. A rule
that called a board's own reference switching copper would be unsatisfiable by construction, which is the
argument for that exclusion and not a convenience.

IT READS THE NETLIST, THE BOARD'S TEXT AND THE INTENT, never pcbnew, so it runs where KiCad is not: the
netlist gives the pads on each net with their pin function, the board file's zones give the poured nets and
the intent file gives the rails and the returns. The intent is optional and its absence is declared, because a
reading taken with less input never replaces one taken with more.

Usage: switch_list.py <netlist.net> [<board.kicad_pcb>] [<intent.json>] --board <letter> [--json]
"""
import os, re, sys, json, fnmatch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

SENS = os.path.join(HERE, "pcb_sensitive.yaml")


def nets_of(path):
    """{net name without its leading slash: [(ref, pin, pinfunction), ...]} from a KiCad netlist, as text."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    txt = txt[txt.find("(nets"):]
    out = {}
    for m in re.finditer(r'\(net\s+\(code\s+"?\d+"?\)\s+\(name\s+"([^"]*)"\)(.*?)(?=\(net\s+\(code|\Z)', txt, re.S):
        out[m.group(1).lstrip("/")] = re.findall(
            r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)(?:\s+\(pinfunction\s+"([^"]*)"\))?', m.group(2))
    return out


def poured(board_path):
    """The nets this board pours, read from the board file's zones. A plane is a rail by construction."""
    if not board_path or not os.path.exists(board_path): return set()
    txt = open(board_path, encoding="utf-8", errors="replace").read()
    return {m.group(1).lstrip("/") for m in
            re.finditer(r'\(zone\b(?:(?!\(zone\b).)*?\(net_name\s+"([^"]*)"', txt, re.S) if m.group(1)}


def declared_elsewhere(intent_path):
    """The nets the design's own intent already calls a rail or a return, and why each is excluded."""
    out = {}
    if not intent_path or not os.path.exists(intent_path): return out, False
    try:
        d = json.load(open(intent_path, encoding="utf-8"))
    except (OSError, ValueError):
        return out, False
    for n in (d.get("rails") or {}): out[n.lstrip("/")] = "the intent declares it a rail"
    for n, v in (d.get("nodes") or {}).items():
        if isinstance(v, dict) and v.get("v_max") == 0.0 and v.get("v_min") == 0.0:
            out[n.lstrip("/")] = "the intent declares it at 0 V, so it is a return"
    return out, True


def shaped(nets, planes, elsewhere):
    """Every switching-shaped net, with the parts that make it one and how strong the reading is."""
    out = []
    for n, nodes in sorted(nets.items()):
        if not n or n.upper() in ("GND", "GNDA", "GNDD") or n in planes or n in elsewhere: continue
        q = sorted({r for r, p, f in nodes if r[:1] == "Q" and r[1:2].isdigit() and (f or "").upper() != "G"})
        l = sorted({r for r, p, f in nodes if r[:1] == "L" and r[1:2].isdigit()})
        if q and l: out.append({"net": n, "transistors": q, "inductors": l, "rank": "STRONG"})
        elif len(q) >= 2: out.append({"net": n, "transistors": q, "inductors": l, "rank": "WEAK"})
    return out


def judge(netlist, board_path, letter, intent_path=None):
    import yaml
    b = ((yaml.safe_load(open(SENS, encoding="utf-8")) or {}).get("boards") or {}).get(letter) or {}
    pats = b.get("switch_nets")
    nets = nets_of(netlist)
    planes = poured(board_path)
    elsewhere, had_intent = declared_elsewhere(intent_path)
    cand = shaped(nets, planes, elsewhere)
    declared = sorted(n for n in nets if pats and any(fnmatch.fnmatchcase(n, p) for p in pats))
    undeclared = [c for c in cand if c["net"] not in declared]
    return dict(nets=len(nets), planes=sorted(planes), patterns=pats, declared=declared,
                shaped=cand, undeclared=undeclared, excluded=elsewhere, had_intent=had_intent,
                strong=[c for c in undeclared if c["rank"] == "STRONG"],
                declares_nothing=(pats is None),
                declared_zero=(pats == []), why=b.get("switch_nets_why"))


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    # a flag given no value is answered and never raised, and the next flag is never taken as a value
    letter = str(_v.opt(argv, "--board", "")).lower()
    netlist = args[0] if args else ""
    board = args[1] if len(args) > 1 else ""
    intent = args[2] if len(args) > 2 else ""
    if not netlist or not letter:
        print(__doc__.strip().splitlines()[-1]); return _v.INCONCLUSIVE
    r = judge(netlist, board, letter, intent)
    ev = ["%s %s: %s%s" % (c["rank"], c["net"], ",".join(c["transistors"]),
                           (" with " + ",".join(c["inductors"])) if c["inductors"] else "")
          for c in r["undeclared"]]
    print("switch_list: board %s, %d net(s), %d poured, %d named a rail or a return by the intent; the "
          "declaration matches %d; %d net(s) are switching shaped and %d of them are NOT in the list (%d strong)"
          % (letter.upper(), r["nets"], len(r["planes"]), len(r["excluded"]), len(r["declared"]),
             len(r["shaped"]), len(r["undeclared"]), len(r["strong"])))
    if not r["had_intent"]:
        print("  note no intent file was given, so no net could be excluded as a declared rail or return and "
              "the candidates below are the weaker reading")
    if r["declares_nothing"]:
        print("  note this board declares no switch_nets at all, so ANA-001 has no denominator here")
    elif r["declared_zero"]:
        print("  note this board declares that it has NO switching net%s" % (": " + " ".join(str(r["why"]).split())[:160] if r["why"] else ", with no reason beside it"))
    for e in ev: print("  CANDIDATE %s" % e)
    if "--json" in argv: print(json.dumps(r, indent=1))
    # A REPORT NEVER DECIDES A RULE (the 16 September rule for via_current's advisory half, and the reason
    # rail_crossings is declared beside via_current rather than in front of it). This writes an ADVISORY
    # verdict so the chain and the registry can read it, and ANA-001 stays sensitive_nodes' to decide.
    return _v.write("switch_list", _v.PASS if not r["undeclared"] else _v.FAIL,
                    counts={"nets": r["nets"], "poured": len(r["planes"]), "declared": len(r["declared"]),
                            "shaped": len(r["shaped"]), "undeclared": len(r["undeclared"]),
                            "strong": len(r["strong"]), "excluded_by_intent": len(r["excluded"])},
                    denominator=len(r["shaped"]), evidence=ev[:20], advisory=True,
                    missing_input=(None if r["had_intent"] else
                                   "no intent file, so no net could be excluded as a declared rail or return"),
                    inputs={"netlist": netlist, "board": board, "intent": intent, "declares": r["patterns"]},
                    note="a net carrying a transistor's drain or source pad with an inductor's pad, or two "
                         "transistors', and not matched by this board's own switch_nets patterns; a REPORT, "
                         "because whether such a node is switching for ANA-001 is a judgement and not a "
                         "measurement")


if __name__ == "__main__":
    sys.exit(_v.guard("switch_list", main, sys.argv[1:]))
