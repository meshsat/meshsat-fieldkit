#!/usr/bin/env python3
"""Design intent as data (MESHSAT-862 Stage C, 8 Sep 2026, appendix 32.64 W2). The schematic generators used to emit reference, symbol, value,
footprint and a pin-to-net map and nothing else, so no gate could ask "is this capacitor near the pin it bypasses", "does this rail's copper
carry its current" or "is this pair at its impedance". Each gen_sch_*.py now collects:
  bypass(cap_ref, part_ref, pin)            the pin a decoupling capacitor serves (through c(..., bypass=(part, pin)))
  rail(net, volts, amps_typ, amps_peak, source_ref, loads={ref: amps})   the currents a rail carries, from the record (appendix 32.55 for A22)
  pair_class(class_name, z_diff=None, z_se=None)   the impedance target of a net class (the class itself is assigned in the project file)
and writes out/<name>-intent.json beside the netlist. The gates read it with load(); a missing file is a FAIL there (fail closed), an empty
list is reported with its zero denominator ("bypass 0 of 0 checked"), never hidden."""
import json, os, sys, time

Z_DEFAULT = {"USB": {"z_diff": 90.0, "z_se": 50.0}, "DIFF100": {"z_diff": 100.0, "z_se": 50.0}, "PCIE": {"z_diff": 100.0}, "HDMI": {"z_diff": 100.0}, "RF": {"z_se": 50.0}}

_I = {"bypass": [], "rails": {}, "pair_classes": dict(Z_DEFAULT)}

def bypass(cap_ref, part_ref, pin, net=None):
    _I["bypass"].append({"cap": cap_ref, "part": part_ref, "pin": str(pin), "net": net})

def rail(net, volts, amps_typ, amps_peak, source, loads=None, note=""):
    _I["rails"][net] = {"volts": volts, "amps_typ": amps_typ, "amps_peak": amps_peak, "source": source, "loads": loads or {}, "note": note}

def pair_class(name, z_diff=None, z_se=None):
    _I["pair_classes"][name] = {k: v for k, v in (("z_diff", z_diff), ("z_se", z_se)) if v is not None}

def write(sch_path, project, parts=None):
    """Writes out/<project>-intent.json next to the schematic; the bypass entries are checked against the part list when given."""
    out = os.path.join(os.path.dirname(os.path.abspath(sch_path)), "out", project + "-intent.json"); os.makedirs(os.path.dirname(out), exist_ok=True)
    if parts is not None:
        refs = {p["ref"] for p in parts}; nets = {p["ref"]: p["nets"] for p in parts}
        for b in _I["bypass"]:
            if b["cap"] not in refs or b["part"] not in refs: raise SystemExit("intent: bypass %s -> %s.%s names a reference that is not in the schematic" % (b["cap"], b["part"], b["pin"]))
            if b["pin"] not in nets[b["part"]]: raise SystemExit("intent: bypass %s -> %s.%s: the part has no pin %s" % (b["cap"], b["part"], b["pin"], b["pin"]))
            if b["net"] is None: b["net"] = nets[b["part"]][b["pin"]]
            if b["net"] not in nets[b["cap"]].values(): raise SystemExit("intent: bypass %s -> %s.%s: the capacitor is not on that pin's net %s" % (b["cap"], b["part"], b["pin"], b["net"]))
        for net, r in _I["rails"].items():
            on_net = {p["ref"] for p in parts if net in p["nets"].values()}
            if not on_net: raise SystemExit("intent: rail %s is not a net of the schematic" % net)
            if r["source"] not in on_net: raise SystemExit("intent: rail %s names source %s, which is not on that net (refs on it: %s)" % (net, r["source"], sorted(on_net)[:8]))
            for ref in r["loads"]:
                if ref not in on_net: raise SystemExit("intent: rail %s names load %s, which is not on that net" % (net, ref))
    d = dict(board=project, written=time.strftime("%Y-%m-%d %H:%M"), **_I)
    json.dump(d, open(out, "w"), indent=1)
    print("intent: %s (%d bypass, %d rails, %d pair classes)" % (out, len(_I["bypass"]), len(_I["rails"]), len(_I["pair_classes"])))
    return out

def load(board_path):
    """The intent file for a board file (<dir>/out/<stem>-intent.json), or None."""
    stem = os.path.splitext(os.path.basename(board_path))[0]; p = os.path.join(os.path.dirname(os.path.abspath(board_path)), "out", stem + "-intent.json")
    if not os.path.exists(p): return None
    return json.load(open(p))
