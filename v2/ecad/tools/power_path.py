#!/usr/bin/env python3
"""EVERY SEGMENT OF A POWER PATH, ASKED OF THE DECLARATION ALONE (20 September 2026, rules PI-001 and PI-002).

Board A had SIXTEEN DC conductors declared as `node`s, and `intent.node()` says in its own first line that it
describes a net that is NOT a rail: `dc_drop` solves no potential on one, so neither power rule ever looked at
them. Two of the sixteen were measured on 20 September at 4.81 A and 6.26 A in conductors IPC-2221 rates at
0.40 A, one of them on the committed board, and the remaining eight turned out to include the whole 45 W
USB-C outlet, which sags 837 mV at 3 A. Every one of them was found BY HAND, by reading a generator.

This asks the question mechanically, and it needs no board: a NETLIST and the intent beside it are enough, so
it runs where KiCad is not.

THE TEST. A rail declares its source and its loads. A load part is where that rail's current LEAVES the net,
so whatever is on that part's OTHER pins is the next segment of the same path, and if the next segment is a
declared NODE rather than a rail, no power rule is looking at it. That is exactly the shape of every one of
tonight's ten: VBUS20's load R16 has CH_ACN on its other pad; the stage shunt R81 has PD_OUT on one side and
PD_VPWR on the other; Q27's drain is PD_VPWR and its source PD_SW.

WHAT IT MUST NOT FLAG, and each exclusion is a fact rather than a name:
  * a net the intent declares a RAIL already, including one declared `series_of` another;
  * a net declared at 0 V (a ground or a return: `dc_drop` cannot judge a return against a percentage of its
    own ~50 mV, which is why board P's PACK_N is still a node and says so);
  * a SWITCHING node, which has no DC potential to solve and is where a buck-boost's current is chopped; the
    intent marks these by declaring `v_min` below zero or by naming another net it `rides_on`;
  * a part with only ONE pin on any net of interest (a capacitor to ground, a test point): the current does
    not pass THROUGH it, so its other pin is not the next segment;
  * a part whose reference says it carries no power: a test point, a fiducial, a mounting hole.

IT WALKS ONE HOP, DELIBERATELY. A path of several nodes in a row gets its FIRST link flagged and no more,
because the walk starts from a declared RAIL and a node declares no loads to walk on from. Board A's USB-C
outlet is four conductors and this names the first: declare it and the next run names the second. That is a
fixed point worth having rather than a transitive closure written at two in the morning, and the run after
each declaration is what tells you whether you are at it.

It REPORTS and does not decide. The answer to a flagged net is a reading of the design, not a rewrite: some
are genuinely nodes (a gate driver's supply behind a resistor, a bootstrap top plate) and the declaration is
where a person writes down which. That is why this prints the evidence for each one, the rail it hangs off
and the part it passes through, rather than a count.

Usage: power_path.py <netlist.net> [--intent <path>] [--out-dir <dir>]
"""
import os, sys, json, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict as _v

NO_POWER = re.compile(r"^(TP|FID|H|MH|MK|LOGO|NT)\d*$")


def parse_netlist(path):
    """{net: [(ref, pin), ...]} and the set of references, from KiCad's s-expression netlist.

    READ IT BY LINE AND NOT BY BLOCK. KiCad 9 writes `(net (code "19") (name "/CH_ACN") (class "Default")`
    with the code QUOTED and a class field, and every node line carries `pinfunction` and `pintype` after the
    pin. The first version of this matched `(code \d+)` unquoted and a block ending in a fixed indent, and it
    parsed ZERO nets out of a 413-part netlist while reporting a clean pass, which is the shape this whole
    file exists to catch: a reading that answers nothing and says PASS. A line walk survives a field order
    change, and `main` refuses a netlist it parsed no nets from.
    """
    nets, refs, cur = {}, set(), None
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.search(r'\(comp \(ref "([^"]+)"\)', line)
        if m: refs.add(m.group(1)); continue
        m = re.search(r'\(net \(code "?\d+"?\) \(name "([^"]+)"\)', line)
        if m: cur = m.group(1).lstrip("/"); nets.setdefault(cur, []); continue
        m = re.search(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', line)
        if m and cur is not None: nets[cur].append((m.group(1), m.group(2)))
    return {k: v for k, v in nets.items() if v}, refs


def _is_switching(node):
    """A switching node has no DC potential to solve, and the intent already says so in two ways."""
    return float(node.get("v_min") or 0) < 0 or node.get("rides_on") is not None


def segments(intent, nets):
    """Every declared node that carries a declared rail's current through a load part."""
    rails, nodes = intent.get("rails") or {}, intent.get("nodes") or {}
    rail_names = {n.lstrip("/") for n in rails}
    # HOW MANY NETS A PART TOUCHES IS WHETHER CURRENT PASSES THROUGH IT (20 September 2026, the first version's
    # three false positives). A rail's loads include its controller, and the first version walked out of
    # `U15`'s other pins and reported the stage's own sense filter and its 7.6 V regulator output as segments
    # of a 0.30 A power path. A shunt has two nets, a switch FET has three (drain, source, gate) and a
    # twenty-eight pin controller has twenty-five: a part with more than three distinct nets does not hand its
    # rail current to an arbitrary pin, which is `intent.rail`'s own rule about naming an IC as a source said
    # the other way round. The test is the netlist's, not the reference designator's.
    part_nets, part_pads = {}, {}
    for netname, nodelist in nets.items():
        for ref, pin in nodelist:
            part_nets.setdefault(ref, set()).add(netname)
            part_pads.setdefault(ref, {}).setdefault(netname, set()).add(pin)

    def _control_pin(ref, netname):
        """A power transistor's GATE, told from its drain and source by the LAND and not by a name.

        A PowerPAK SO-8 has eight pads on three nets: the drain tab is pad 5 repeated four times, the source
        is pads 1, 2 and 3, and the GATE is the single pad 4. So on a part with more PADS than NETS, a net it
        touches with exactly one pad while touching another with several is its control pin, and a gate
        carries no rail current. A two-pad resistor has pads == nets, so the test does not apply to it and
        both of its terminals count, which is what makes `CH_ACN` through R16 a real finding and
        `CH_HIDRV1` through Q7 a false one.

        A three-pin SOT-23 FET has pads == nets and its gate is NOT excluded by this. That is deliberate and
        it is stated rather than hidden: such a part is almost never a declared rail's load, and inventing a
        pin-name test to cover it would be the guard-as-hypothesis shape this project keeps meeting.
        """
        pads = part_pads.get(ref, {})
        if sum(len(v) for v in pads.values()) <= len(pads): return False
        return len(pads.get(netname, ())) == 1 and any(len(v) > 1 for k, v in pads.items() if k != netname)
    out = []
    for rname, r in sorted(rails.items()):
        rn = rname.lstrip("/")
        # BOTH ENDS OF THE RAIL, because a path has a previous segment as well as a next one. The current
        # ENTERS at the source and LEAVES at the loads, so the conductor on the far side of either is the
        # same path: `FE_OUT` hangs off VBUS20's SOURCE shunt R11 and `CH_ACN` off its LOAD shunt R16, and a
        # walk that knew only loads found one of them.
        _src = r.get("source"); _src = _src if isinstance(_src, (list, tuple)) else [_src]
        ends = [(x, float(r.get("amps_typ") or 0)) for x in _src if x] + \
               [(k, float(v or 0)) for k, v in sorted((r.get("loads") or {}).items())]
        for load, amps in ends:
            # A LOAD DECLARED AT ZERO PASSES NO CURRENT, so nothing downstream of it is a power path. Board D
            # declares seven logic gates on +3V3_D8 at 0.00 A each and the first sweep walked out of all
            # fourteen of their pins.
            if amps <= 0: continue
            # the pins this part has on the rail, and the pins it has anywhere else
            on_rail = [p for ref, p in nets.get(rn, []) if ref == load]
            if not on_rail: continue
            if NO_POWER.match(load): continue
            for other, nodelist in sorted(nets.items()):
                if other == rn or other in rail_names: continue
                mine = [p for ref, p in nodelist if ref == load]
                if not mine: continue
                # AN UNDECLARED NET ON A POWER PATH IS THE WORSE CASE, NOT AN EXEMPT ONE (20 September 2026,
                # the first version skipped it and board E's six went on being invisible). `derate` reports
                # an undeclared net only where a RATED PART sits on it, so a bare conductor between two
                # shunts is seen by nothing at all. Board E's entire input side is in that state: `DC_IN`,
                # `DC_F`, `DC_HS`, `DC_P` carry the vehicle and shore entry at 8 A typical and 10 A peak and
                # not one of them is a rail or a node. Every net on the path between a rail's source and its
                # loads must be declared SOMEHOW, as the rail it is or as a node with its basis: a switching
                # node is a node and says why, which is what board A's five stages do. Undeclared is never
                # the right answer, so it is reported as its own kind rather than skipped.
                nd = nodes.get(other)
                kind = "node"
                if nd is None:
                    kind, nd = "undeclared", {}
                else:
                    if abs(float(nd.get("v_max") or 0)) < 1e-9 and abs(float(nd.get("v_min") or 0)) < 1e-9:
                        continue                             # a declared zero: a ground or a return
                    if _is_switching(nd): continue
                if len(nodelist) < 2: continue               # nothing passes through a one-pin net
                # WHAT A PASS-THROUGH PART IS, stated as two shapes and nothing else (20 September 2026,
                # narrowed after the first sweep reported a fan header's tachometer pin as a power path).
                # Current passes THROUGH a part in exactly two arrangements: a two-terminal part, which is a
                # shunt, an inductor, a fuse or a ferrite and has exactly TWO nets; or a power transistor,
                # which has MORE PADS THAN NETS because its drain and source are multi-pad lands, and whose
                # single-pad net is its gate. A three-pin CONNECTOR has three nets and one pad each, and its
                # pins 2 and 3 are a tachometer and a pulse output rather than the other end of pin 1; a
                # SOT-23 FET has the same shape and is excluded with it, which is stated rather than hidden
                # (such a part carries at most a couple of hundred milliamps anywhere on these boards).
                _pads = part_pads.get(load, {})
                _multi = sum(len(v) for v in _pads.values()) > len(_pads)
                if not (len(_pads) == 2 or (_multi and len(_pads) <= 3)): continue
                if _control_pin(load, other): continue         # a gate carries no rail current: see _control_pin
                out.append(dict(node=other, kind=kind, rail=rn, through=load, amps=float(amps or 0),
                                pins_on_rail=on_rail, pins_on_node=mine,
                                v_max=float(nd.get("v_max") or 0), basis=str(nd.get("basis") or "")[:120]))
    seen, uniq = set(), []
    for s in out:
        k = (s["node"], s["rail"], s["through"])
        if k in seen: continue
        seen.add(k); uniq.append(s)
    return uniq


def main(argv):
    if not argv: raise SystemExit(__doc__)
    net = argv[0]
    ip = _v.opt(argv, "--intent", None) or os.path.join(os.path.dirname(os.path.abspath(net)),
                                                        os.path.splitext(os.path.basename(net))[0] + "-intent.json")
    _od = _v.opt(argv, "--out-dir", None)
    _w = (lambda *a, **k: _v.write(*a, **dict(k, out_dir=_od))) if _od else _v.write
    if not os.path.exists(ip):
        return _w("power_path", _v.INCONCLUSIVE,
                  note="no intent file beside this netlist, so no rail declares a load to walk from",
                  missing_input="the intent declaration")
    intent = json.load(open(ip, encoding="utf-8"))
    nets, refs = parse_netlist(net)
    # A READING TAKEN FROM NOTHING IS NOT A PASS. The first parse read zero nets and reported a clean answer.
    if not nets:
        return _w("power_path", _v.INCONCLUSIVE,
                  note="no net was parsed out of %s, so nothing was asked of it" % os.path.basename(net),
                  missing_input="a readable netlist")
    rows = segments(intent, nets)
    for s in rows:
        print("power_path: %-14s carries %s's %.2f A through %s (pins %s on the rail, %s on it), %s"
              % (s["node"], s["rail"], s["amps"], s["through"], ",".join(s["pins_on_rail"]), ",".join(s["pins_on_node"]),
                 "NOT DECLARED AT ALL" if s["kind"] == "undeclared" else "declared a NODE at %.1f V" % s["v_max"]))
        if s["basis"]: print("              its basis: %s" % s["basis"])
    _un = sum(1 for r in rows if r["kind"] == "undeclared")
    print("power_path: %d net(s) carry a declared rail's current through one of its own source or load parts "
          "without being a rail: %d declared a node and %d NOT DECLARED AT ALL, of %d rail(s) and %d node(s)"
          % (len(rows), len(rows) - _un, _un, len(intent.get("rails") or {}), len(intent.get("nodes") or {})))
    return _w("power_path", _v.PASS, counts=dict(segments=len(rows), undeclared=_un,
                                                 rails=len(intent.get("rails") or {}),
                                                 nodes=len(intent.get("nodes") or {})),
              evidence=["%s (%s) carries %s's %.2f A through %s" % (s["node"], s["kind"], s["rail"], s["amps"], s["through"]) for s in rows],
              
              note=("every declared node that carries a declared rail's current through one of that rail's own "
                    "load parts: a candidate segment of a power path that no power rule is looking at. It "
                    "REPORTS: some of these are genuinely nodes and the declaration is where that is written "
                    "down, with its reason."))


if __name__ == "__main__":
    sys.exit(_v.guard("power_path", main, sys.argv[1:]))
