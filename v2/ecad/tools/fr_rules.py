#!/usr/bin/env python3
"""fr_rules: write a Freerouting rules file (the format the router itself writes and reads with -dr) with an autoroute_settings block.

The capability probe of 6 Sep 2026 showed that this is the lever Freerouting 1.9.0 actually honours: via_costs 200 against the default 50 cut
D7's vias from 130 to 98 (25 percent) for 13 percent more length, while -us, -is, -oit and -mp changed nothing on a board that completes.
Keys: via_costs, plane_via_costs, start_ripup_costs (integers), preferred (a list of per-layer directions in DSN layer order: h, v or -, where
'-' keeps the layer active with no preference), inactive (layers routed on no wire), fanout/autoroute/postroute on|off.
Usage: fr_rules.py <board.dsn> <out.rules> [--via-costs 50] [--plane-via-costs 5] [--ripup 100] [--preferred h,v,h,v] [--inactive In1.Cu,In4.Cu]
       [--fanout off] [--autoroute on] [--postroute on] [--name PCB]"""
import sys, re

def arg(name, default=None): return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

dsn, out = sys.argv[1], sys.argv[2]
text = open(dsn, errors="replace").read()
m = re.search(r"\(structure(.*?)\(boundary", text, re.S)
layers = re.findall(r"\(layer (\S+)\s*\(type", m.group(1) if m else text)
if not layers: layers = sorted(set(re.findall(r"\(layer ([A-Za-z0-9_.]+)", text)))
pref = (arg("--preferred") or "").split(",") if arg("--preferred") else []
inactive = set((arg("--inactive") or "").split(",")) - {""}
name = arg("--name") or re.search(r"\(pcb\s+(\S+)", text).group(1).strip('"') if re.search(r"\(pcb\s+(\S+)", text) else "PCB"
# --only a,b,c (6 Sep 2026 11:40): emit only these items of the block (fanout, autoroute, postroute, vias, via_costs, plane_via_costs, start_ripup_costs, start_pass_no, layer_rules);
# the isolation of what in a "default" block makes the router lose the design's clearances on B15 (42 hard violations with the full block, 0 without any block)
ONLY = set((arg("--only") or "fanout,autoroute,postroute,vias,via_costs,plane_via_costs,start_ripup_costs,start_pass_no,layer_rules").split(","))
items = [("fanout", "(fanout %s)" % arg("--fanout", "off")), ("autoroute", "(autoroute %s)" % arg("--autoroute", "on")), ("postroute", "(postroute %s)" % arg("--postroute", "on")), ("vias", "(vias on)"),
         ("via_costs", "(via_costs %s)" % arg("--via-costs", "50")), ("plane_via_costs", "(plane_via_costs %s)" % arg("--plane-via-costs", "5")), ("start_ripup_costs", "(start_ripup_costs %s)" % arg("--ripup", "100")), ("start_pass_no", "(start_pass_no 1)")]
lines = ["(rules PCB %s" % name, "  (snap_angle fortyfive_degree)", "  (autoroute_settings " + " ".join(t for k, t in items if k in ONLY)]
if "layer_rules" not in ONLY: layers = []
for i, L in enumerate(layers):
    d = pref[i] if i < len(pref) else "-"
    direction = "horizontal" if d == "h" else "vertical" if d == "v" else None
    active = "off" if L in inactive else "on"
    if direction: lines.append("    (layer_rule %s (active %s) (preferred_direction %s) (preferred_direction_trace_costs 1.0) (against_preferred_direction_trace_costs 2.5))" % (L, active, direction))
    else: lines.append("    (layer_rule %s (active %s) (preferred_direction horizontal) (preferred_direction_trace_costs 1.0) (against_preferred_direction_trace_costs 1.0))" % (L, active))
lines += ["  )", ")"]
open(out, "w").write("\n".join(lines) + "\n")
print("fr_rules: %s layers %s only %s via_costs %s plane_via_costs %s ripup %s preferred %s inactive %s -> %s" % (name, layers, sorted(ONLY), arg("--via-costs", "50"), arg("--plane-via-costs", "5"), arg("--ripup", "100"), pref or "none", sorted(inactive) or "none", out))
