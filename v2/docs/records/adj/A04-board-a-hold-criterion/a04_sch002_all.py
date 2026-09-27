#!/usr/bin/env python3
# A04: every SCH-002 disagreement on A32 (the verdict caps its evidence at 50), plus every VALUE and FOOTPRINT
# difference board-wide, and which of them touch an external-port net. Read-only; prints and writes one JSON.
import sys, json, re
sys.path.insert(0, sys.argv[1] + "/v2/ecad/tools")
import netlist_board as nb, pcbnew
out = sys.argv[4]
nl = nb.read_netlist(sys.argv[3])
b = pcbnew.LoadBoard(sys.argv[2])
fps = {f.GetReference(): f for f in b.GetFootprints()}
txt = open(sys.argv[3], encoding="utf-8").read()
vals = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "((?:[^"\\]|\\.)*)"\)', txt))
fpn = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "(?:[^"\\]|\\.)*"\)\s*\(footprint "([^"]*)"\)', txt))
EXT = {"VIN_RAW", "USB_WALL_P", "USB_WALL_N", "PD_VBUS", "PD_CC1", "PD_CC2"}
res = {"missing_on_board": [], "board_only_live": [], "pad_net": [], "value": [], "footprint": []}
for r in sorted(nl):
    if r not in fps: res["missing_on_board"].append({"ref": r, "netlist_nets": sorted(set(nl[r].values())),
                                                     "touches_external": bool(set(nl[r].values()) & EXT)})
for r in sorted(set(nl) & set(fps)):
    pads = {}
    for p in fps[r].Pads():
        n = p.GetNetname().lstrip("/")
        if n and not n.startswith("unconnected-"): pads.setdefault(p.GetNumber(), n)
    for pin, net in sorted(nl[r].items()):
        if net.startswith("unconnected-"): continue
        got = pads.get(pin)
        if got != net: res["pad_net"].append({"ref": r, "pin": pin, "netlist": net, "board": got,
                                             "touches_external": net in EXT or got in EXT})
    bv = fps[r].GetValue()
    if r in vals and bv != vals[r]: res["value"].append({"ref": r, "netlist": vals[r], "board": bv,
                                                         "touches_external": bool(set(nl[r].values()) & EXT)})
    bf = fps[r].GetFPIDAsString().split(":")[-1]
    if r in fpn and fpn[r].split(":")[-1] != bf: res["footprint"].append({"ref": r, "netlist": fpn[r], "board": bf})
for r in sorted(fps):
    if r in nl or r.startswith(nb.BENCH): continue
    live = sorted({p.GetNetname() for p in fps[r].Pads() if p.GetNetname()})
    if live: res["board_only_live"].append({"ref": r, "nets": live})
res["counts"] = {k: len(v) for k, v in res.items() if isinstance(v, list)}
res["sch002_equivalent_fail_count"] = len(res["missing_on_board"]) + len(res["pad_net"]) + len(res["board_only_live"])
res["any_touches_external"] = [x for k in ("missing_on_board", "pad_net", "value") for x in res[k] if x.get("touches_external")]
json.dump(res, open(out, "w"), indent=1)
print(json.dumps(res["counts"]), "sch002-equivalent", res["sch002_equivalent_fail_count"])
for x in res["pad_net"]: print("PADNET", x)
for x in res["value"]: print("VALUE", x)
for x in res["footprint"]: print("FOOTPRINT", x)
print("TOUCHES EXTERNAL:", res["any_touches_external"])
