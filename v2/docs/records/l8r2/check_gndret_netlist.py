#!/usr/bin/env python3
"""check_gndret_netlist.py: what board B's regenerated netlist and intent must show for the return's declaration (Layer 8 record
l8r2, round 7, task T5b, MESHSAT-1357, 4 October 2026). Parsed, never grepped: the netlist with check_l8r2_netlist.py's reader,
the intent as JSON.

Usage:  check_gndret_netlist.py NETLIST INTENT.json
Exit 0: DRAWN; 4: NOT DRAWN or FAIL; 2: usage.

A LEAD is read from the netlist and the intent together, not from the declaration under test: a two-pin connector whose pin 1 is
on a declared rail that names this connector as its source and that no rail on this board feeds (an ARRIVING rail), and whose pin
2 is on GND. The return's declaration is DRAWN when
  R1 its sources are exactly the leads (a lead whose pin 2 is on GND and is not named is a return the copper rules never solve; a
     named connector that is no lead, for example a lead reversed in the netlist, is refused);
  R2 its typical and its peak are the sums of the arriving rails' typical and peak currents (a typed figure that differs is
     refused: the figure went stale twice that way);
  R3 every declared load has a pin on GND, and the PoE port's return is among them at the sense resistor, at +54V_POE's peak;
  R4 the loads sum to at most 1.02 times the peak (intent.rail's own rule, read back from what it wrote);
and it prints, for the capacity model, the board-to-board ground conductors the netlist carries: the leads' pin 2 and the ground
pins of the ribbon headers J_AB1 and J_AB2. NOT DRAWN is the committed state alone (10.0 A, 21.0 A, the four typed leads)."""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("l8r2_netlist_reader", os.path.join(HERE, "check_l8r2_netlist.py"))
_rd = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_rd)
read_netlist = _rd.read_netlist
RIBBONS = ("J_AB1", "J_AB2")
POE_RAIL, POE_SENSE = "+54V_POE", "R12"
TYPED = (10.0, 21.0, ["J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV"])


def rails_of(intent):
    return {k.lstrip("/"): v for k, v in (intent.get("rails") or {}).items()}


def arriving(intent):
    """{connector: rail} for every rail that enters the board at one connector and that no rail of this board feeds."""
    out = {}
    for name, r in sorted(rails_of(intent).items()):
        if name != "GND" and isinstance(r.get("source"), str) and r["source"].startswith("J_") \
                and not any(r.get(k) for k in ("fed_from", "series_of", "returns")):
            out.setdefault(r["source"], []).append(name)
    return out


def leads(nl, intent):
    """[(connector, rail)]: two-pin connectors with pin 1 on an arriving rail that names them and pin 2 on GND."""
    P = nl["pins"]; out = []
    for ref, rails in sorted(arriving(intent).items()):
        pins = P.get(ref, {})
        if sorted(pins) == ["1", "2"] and pins["2"] == "GND" and len(rails) == 1 and pins["1"] == rails[0]:
            out.append((ref, rails[0]))
    return out


def ground_conductors(nl):
    """the ribbon headers' pins on GND, per header"""
    P = nl["pins"]
    return {h: sorted((p for p, n in P.get(h, {}).items() if n == "GND"), key=int) for h in RIBBONS}


def judge(nl, intent):
    P = nl["pins"]; R = rails_of(intent); g = R.get("GND")
    if g is None:
        return "FAIL", ["the intent declares no GND rail"]
    src = list(g["source"]) if isinstance(g.get("source"), (list, tuple)) else [g.get("source")]
    typ, peak, loads = float(g.get("amps_typ") or 0), float(g.get("amps_peak") or 0), dict(g.get("loads") or {})
    L = leads(nl, intent); lead_refs = [r for r, _n in L]
    s_typ = round(sum(float(R[n].get("amps_typ") or 0) for _r, n in L), 4); s_peak = round(sum(float(R[n].get("amps_peak") or 0) for _r, n in L), 4)
    lines = ["leads read from the netlist and the intent: %s" % (", ".join("%s (%s)" % x for x in L) or "none"),
             "GND as declared: %.4f A typical, %.4f A peak, sources %s, %d loads summing %.4f A" % (typ, peak, ", ".join(src), len(loads), sum(loads.values())),
             "the leads' own declarations sum to %.4f A typical and %.4f A peak" % (s_typ, s_peak)]
    gc = ground_conductors(nl)
    lines.append("board-to-board ground conductors on the netlist: %d lead contacts (%s) and %d ribbon conductors (%s)"
                 % (len(L), ", ".join("%s.2" % r for r in lead_refs), sum(len(v) for v in gc.values()),
                    "; ".join("%s pins %s" % (h, ",".join(v)) for h, v in sorted(gc.items()))))
    if (typ, peak, src) == TYPED and sorted(src) != sorted(lead_refs):
        return "NOT DRAWN", lines + ["the return is the committed typed declaration (%.1f A, %.1f A, four leads)" % (typ, peak)]
    bad = []
    for s in src:
        if s not in lead_refs:
            bad.append("R1 %s is named a return lead and is none: pin 1 on %r, pin 2 on %r" % (s, P.get(s, {}).get("1"), P.get(s, {}).get("2")))
    for r in lead_refs:
        if r not in src:
            bad.append("R1 %s carries %s on pin 1 and GND on pin 2 and is not named a return lead" % (r, dict(L)[r]))
    if abs(typ - s_typ) > 1e-6 or abs(peak - s_peak) > 1e-6:
        bad.append("R2 the declared %.4f A typical and %.4f A peak are not the leads' sums %.4f A and %.4f A" % (typ, peak, s_typ, s_peak))
    off = sorted(k for k in loads if "GND" not in P.get(k, {}).values())
    if off:
        bad.append("R3 loads with no pin on GND: %s" % ", ".join(off))
    poe = float((R.get(POE_RAIL) or {}).get("amps_peak") or 0)
    if POE_RAIL in R and abs(loads.get(POE_SENSE, 0.0) - poe) > 1e-9:
        bad.append("R3 the PoE port's return at %s is %.3f A, not %s's %.3f A peak" % (POE_SENSE, loads.get(POE_SENSE, 0.0), POE_RAIL, poe))
    if sum(loads.values()) > 1.02 * peak:
        bad.append("R4 the loads sum to %.4f A, over 1.02 times the %.4f A peak" % (sum(loads.values()), peak))
    return ("FAIL", lines + bad) if bad else ("DRAWN", lines)


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0].strip() + "\n")
        return 2
    v, lines = judge(read_netlist(open(argv[0], "rb").read()), json.load(open(argv[1], encoding="utf-8")))
    for l in lines:
        print("  " + l)
    print("the return's declaration on board B: %s" % v)
    return 0 if v == "DRAWN" else 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
