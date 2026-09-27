#!/usr/bin/env python3
"""besc1_causes.py <analysis dir> <b21.net> <corrected.net> <out dir>: EXPERIMENTAL (Q-B-ESC-1). Joins the three
read-only readings of the trial's final boards (residue-<arm>.json from besc1_residue.py, passes-<arm>.json from
besc1_passes.py, viasite-<arm>.json from besc1_viasite.py) and the two netlists into one row per missing connection,
and assigns its cause by these rules, in this order (second version, 27 September 2026: the history column and the
via-site readings come from the second versions of besc1_passes.py and besc1_viasite.py; see their headers):

  keep-out        an end lies inside the confinement keep-out that dsn_confine.py writes over another region's core on
                  every routing layer (region "<other> core"): no router could close it in this trial;
  via site        an end is a pad for which the INPUT board (before any routing) already has no site for the router's
                  0.70 mm via reachable by a straight stub within 3 mm;
  escape at the pad  an end is a fine-pitch pad (U301, U302, U309, U310, U32B) that carried no escape on the input
                  board and carries no copper on the final board, and the FINAL board has no 0.70 mm site for it;
  congestion      every other connection.
Column open_in_observed_passes: after how many observed passes this connection was open, where OPEN means that no pad
of the final board's copper cluster at one end shares a copper cluster with any pad of the final board's cluster at
the other end (besc1_passes.py, second version; no cluster is singled out as the net's main one); open_after_passes
lists those passes. net_open_in_observed_passes counts the passes after which the net had two or more pad-bearing
clusters at all. Where a 0.70 mm site that a rule reads (the input board's for any end pad, the final board's for a
bare fine-pitch pad) is five grid points or fewer, the note gives it with its clearance: that row's cause turns on
micrometres, because the nearest grid site always clears by less than one grid step and a site that is only a few
points is one a slightly different model of the copper could remove.
Flag "pre-correction netlist": the net's pad set differs between B21's netlist and the corrected one, and the
connection's ends include a pad whose connection the correction changes. Notes name placement facts read off the board."""
import sys, os, re, json, csv

A, N21, NC, OUT = sys.argv[1:5]
FINE = ("U301", "U302", "U309", "U310", "U32B")


def parse(path):
    s = open(path).read(); i = s.find("(nets"); nets = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\n\s*\(net \(code|\Z)', s[i:], re.S):
        nets[m.group(1)] = sorted("%s.%s" % (n.group(1), n.group(2)) for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)))
    return nets


n21, ncor = parse(N21), parse(NC)
NOTES = {
    "C351.1": "C351 and C352 (the upstream pair's AC coupling) sit south-east of U301 at (205.4, 153.1 and 155.9), across the package from pins 123 and 124 on its north row: pin 124 to C351 is 25.3 mm and C351 to U32B.116 111.8 mm, against 99.4 mm from the pin to U32B.116 directly",
    "Y301.3": "the hub's 24 MHz crystal Y301 sits at (200.6, 154.1), its pads 22.1 and 24.3 mm from U302's XO and XI pins",
    "R347.1": "R347 sits on B.Cu under U302's north row; the crystal Y301 is 22 to 24 mm from the hub pins",
    "R347.2": "R347 sits on B.Cu under U302's north row; the crystal Y301 is 22 to 24 mm from the hub pins and C365 31 mm",
    "C364.1": "the crystal's load capacitor C364 sits at (237.5, 138.0), 28.3 mm from U302.62",
    "C365.1": "the crystal's load capacitor C365 sits at (240.6, 138.0), 30.8 mm from U302.61",
    "R317.1": "the switch's IREF resistor R317 sits at (229.6, 169.3), 41 mm from U301.86",
    "R342.1": "the hub's USB_R1 resistor R342 sits on B.Cu at (189.5, 135.6), under U301's north-west corner, 19 mm from U302.64",
    "C374.1": "C374 (+1V1_S3, the hub's rail) sits on B.Cu at (186.3, 132.6), under U301's north-row tip-via line, 22.9 mm from the hub's nearest supply pin",
    "C363.1": "C363 sits on B.Cu at (195.4, 132.4), under U301's north-row tip-via line",
    "U310.2": "the USB 2 host-select mux U310 at (194.4, 155.5) is about 114 mm from U32B.136",
    "U301.128": "U301.128 is the north row's last pad at the package's north-west corner, 99 mm from U32B.122",
    "U309.3": "U302's upstream SuperSpeed pins are on its north row; the bank mux U309 sits 34 mm south-west",
    "U309.4": "U302's upstream SuperSpeed pins are on its north row; the bank mux U309 sits 34 mm south-west",
    "U301.111": "B21 joins the switch's clock output U301.83 (east row) straight to its own clock input U301.111 (north row), defect A.3",
}


def end_label(x):
    it = x["item"]
    if it["kind"] == "pad":
        lay = it["layers"] if isinstance(it["layers"], str) else "+".join(it["layers"])
        return it["ref"], lay
    return "%s@(%.1f,%.1f)" % (it["kind"].replace(" ", "-"), x["at"][0], x["at"][1]), it.get("layer", "through")


for arm in ("a6", "a8"):
    res = json.load(open(os.path.join(A, "residue-%s.json" % arm)))
    pas = json.load(open(os.path.join(A, "passes-%s.json" % arm)))
    vs = json.load(open(os.path.join(A, "viasite-%s.json" % arm)))
    routed = [p for p in sorted(pas["totals"]) if p != "000"]
    assert pas["totals_equal_passes_csv"], arm
    hist = {}
    for h in pas["connections"]:
        hist.setdefault(h["net"], []).append(h)
    rows = []
    for net, v in sorted(res["nets"].items()):
        k = sum(1 for p in routed if net in pas["passes"][p])
        changed = n21.get(net, []) != ncor.get(net, [])
        for e in v["edges"]:
            ea, la = end_label(e["a"]); eb, lb = end_label(e["b"])
            regions = (e["a"]["region"], e["b"]["region"])
            pads = [x for x in (e["a"], e["b"]) if x["item"]["kind"] == "pad"]
            refs = [x["item"]["ref"] for x in pads]
            def site(ref, board, d):
                return (vs[board].get(ref, {}).get("via_%.2f" % d) or {}).get("nearest_site_mm")
            # this connection's own history (besc1_passes.py, second version), matched by net and edge order
            h = hist[net].pop(0)
            assert (h["end_a"], h["end_b"]) == ((e["a"]["item"].get("ref") if e["a"]["item"]["kind"] == "pad" else None),
                                                (e["b"]["item"].get("ref") if e["b"]["item"]["kind"] == "pad" else None)), (net, h)
            k_edge = len(h["open_after"])
            cause = None
            if any(r.endswith(" core") and not r.startswith("S3") for r in regions):
                cause = "keep-out"
            elif any(r in vs["input"] and site(r, "input", 0.70) is None for r in refs):
                cause = "via site"
            elif any(x["item"]["ref"].split(".")[0] in FINE and not x["item"]["escape_on_input_board"]
                     and not x["item"]["copper_on_pad_final"] and site(x["item"]["ref"], "final", 0.70) is None for x in pads):
                cause = "escape at the pad"
            else:
                cause = "congestion"
            flag = ""
            if changed:
                gone = set(n21.get(net, [])) - set(ncor.get(net, []))
                # the cluster pads on each side of this connection
                cl = v["pad_clusters"]
                touched = set(refs)
                for c in cl:
                    if set(c) & set(refs) or any(end in c for end in (ea, eb)):
                        touched |= set(c)
                if gone & touched:
                    flag = "pre-correction netlist (%s leave%s the net or change pin in the corrected netlist)" % (
                        ", ".join(sorted(gone & touched)), "s" if len(gone & touched) == 1 else "")
            note = "; ".join(NOTES[r] for r in refs if r in NOTES)
            # a rule-deciding 0.70 mm site that is only a handful of grid points (the input board's site for any end
            # pad decides "via site"; the final board's site for a bare fine-pitch pad decides "escape at the pad")
            for x in pads:
                r = x["item"]["ref"]
                boards = ["input"]
                if r.split(".")[0] in FINE and not x["item"]["escape_on_input_board"] and not x["item"]["copper_on_pad_final"]:
                    boards.append("final")
                for board in boards:
                    s7 = (vs[board].get(r, {}) or {}).get("via_0.70") or {}
                    nf = s7.get("nearest_foreign_to_via")
                    if s7.get("nearest_site_mm") is not None and s7.get("sites_found_up_to_25", 99) <= 5:
                        m = "the %s board's 0.70 mm site for %s, which a cause rule reads, is %d grid point(s) only, the nearest %.3f mm out at %s and %.3f mm from %s (%s), %d micrometres over the 0.127 mm clearance: this row's cause turns on micrometres" % (
                            board, r, s7["sites_found_up_to_25"], s7["nearest_site_mm"], tuple(s7["site_at"]), nf["mm"], nf["item"], nf["layer"], round((nf["mm"] - 0.127) * 1000))
                        note = (note + "; " if note else "") + m
            rows.append({"arm": arm, "net": net, "end_a": ea, "end_a_layer": la, "end_b": eb, "end_b_layer": lb,
                         "length_mm": e["length_mm"], "region_a": regions[0], "region_b": regions[1],
                         "open_in_observed_passes": "%d of %d" % (k_edge, len(routed)),
                         "open_after_passes": " ".join(str(int(p)) for p in h["open_after"]),
                         "net_open_in_observed_passes": "%d of %d" % (k, len(routed)),
                         "final_site_0.40_0.70_mm": " / ".join("%s:%s,%s" % (r, site(r, "final", 0.40), site(r, "final", 0.70)) for r in refs if r in vs["final"]),
                         "input_site_0.40_0.70_mm": " / ".join("%s:%s,%s" % (r, site(r, "input", 0.40), site(r, "input", 0.70)) for r in refs if r in vs["input"]),
                         "cause": cause, "flag": flag, "note": note})
    with open(os.path.join(OUT, "residue-%s.csv" % arm), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    from collections import Counter
    print(arm, len(rows), dict(Counter(r["cause"] for r in rows)), "flagged", sum(1 for r in rows if r["flag"]))
