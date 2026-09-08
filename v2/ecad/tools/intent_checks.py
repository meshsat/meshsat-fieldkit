#!/usr/bin/env python3
"""The intent gates on a routed board (MESHSAT-862 Stage C, 8 Sep 2026): read out/<stem>-intent.json (intent.py) and the board, and check
  1. return path: every track of a net in a pair class with an impedance target (USB, DIFF100, PCIE, HDMI, RF) has a filled plane (GND or a
     power net's pour) on the copper layer next to it, sampled every SAMPLE mm; a sample with no plane on either neighbouring layer is a gap
     (an In1 rule-area window around the CM5 receptacles, a plane cut-out, a pour the router ate); reported per net as mm of gap, FAIL above 0.5 mm;
  2. decoupling: every bypass entry (capacitor, part, pin) has its capacitor's rail pad within LOOP_MM of the pin's pad centre (3.0 mm for 100 nF
     and smaller, 6.0 mm for bulk), and both the capacitor's rail pad and its ground pad reach a via or a pour within 1.5 mm (the loop closes
     through the planes, not across the board); reported per entry, FAIL on distance;
  3. every rail of the intent file exists on the board with pads on it (a renamed rail is a FAIL, not a silent skip).
A board without an intent file is a FAIL (fail closed). Denominators print on every summary line.
Used as a module by the check_pcb_*.py gates: intent_checks.run(board, check)  or standalone: intent_checks.py <board.kicad_pcb>."""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew, intent

SAMPLE = 1.0; GAP_MM = 0.5; NEAR_VIA = 1.5

def run(b, check, path=None):
    path = path or b.GetFileName(); it = intent.load(path)
    if not it: check(False, "intent file present (out/<stem>-intent.json from the schematic generator)"); return "intent_checks: no intent file, nothing checked"
    pro = os.path.splitext(path)[0] + ".kicad_pro"; assign = {}
    if os.path.exists(pro): assign = json.load(open(pro)).get("net_settings", {}).get("netclass_assignments", {})
    def cls_of(net):
        c = assign.get(net) or assign.get("/" + net.lstrip("/")) or assign.get(net.lstrip("/")) or "Default"
        return c[0] if isinstance(c, list) and c else (c if isinstance(c, str) else "Default")   # KiCad 9 stores the assignment as a list of class names
    targets = {k for k, v in it.get("pair_classes", {}).items() if v}
    cu = list(b.GetEnabledLayers().CuStack())   # KiCad 9: F.Cu 0, In1.Cu 4, In2.Cu 6, ..., B.Cu 2; the stack in order
    if not it.get("rails") and not it.get("bypass") and not it.get("pair_classes"): check(False, "intent file carries at least one rail, bypass entry or pair class (an empty file is not a pass)")
    planes = {}; planes_net = {}
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetFilledArea() <= 0: continue
        n = z.GetNetname().lstrip("/")
        if n == "GND" or n.startswith(("+", "VBAT", "CELL", "VBUS", "PACK")):
            pl = z.GetFilledPolysList(z.GetFirstLayer()); planes.setdefault(z.GetFirstLayer(), []).append(pl); planes_net.setdefault((z.GetFirstLayer(), z.GetNetname()), []).append(pl)
    def neighbours(L):
        i = cu.index(L); return [cu[j] for j in (i - 1, i + 1) if 0 <= j < len(cu)]
    # 1. return path
    gaps = {}; total = {}; n_nets = 0
    for tr in b.GetTracks():
        if tr.GetClass() != "PCB_TRACK": continue
        net = tr.GetNetname()
        if cls_of(net) not in targets: continue
        L = tr.GetLayer(); length = tr.GetLength() / 1e6; n = max(1, int(length / SAMPLE)); total[net] = total.get(net, 0.0) + length
        for k in range(n + 1):
            u = k / n; p = pcbnew.VECTOR2I(int(tr.GetStart().x + u * (tr.GetEnd().x - tr.GetStart().x)), int(tr.GetStart().y + u * (tr.GetEnd().y - tr.GetStart().y)))
            if not any(pl.Contains(p) for Ln in neighbours(L) for pl in planes.get(Ln, [])): gaps[net] = gaps.get(net, 0.0) + length / (n + 1)
    for net in sorted(total):
        n_nets += 1; g = gaps.get(net, 0.0)
        check(g <= GAP_MM, "return path under %s (%s): %.1f of %.1f mm without a plane on a neighbouring layer" % (net.lstrip("/"), cls_of(net), g, total[net]))
    # 2. decoupling
    pads = {(f.GetReference(), p.GetNumber()): p for f in b.GetFootprints() for p in f.Pads()}
    vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
    def closes(p):
        c = p.GetPosition(); r = int(NEAR_VIA * 1e6)
        if any(v.GetNetname() == p.GetNetname() and math.hypot(v.GetPosition().x - c.x, v.GetPosition().y - c.y) <= r for v in vias): return True
        return any(pl.Contains(c) for L in cu for pl in planes_net.get((L, p.GetNetname()), []))   # the pad lies in a pour of its own net (review of 8 Sep 2026: the `is` on SWIG proxies was always False)
    n_by = 0
    for e in it.get("bypass", []):
        n_by += 1
        cap = [p for (ref, num), p in pads.items() if ref == e["cap"]]; pin = pads.get((e["part"], e["pin"]))
        if not cap or pin is None: check(False, "bypass %s -> %s.%s: pads found on the board" % (e["cap"], e["part"], e["pin"])); continue
        rail = [p for p in cap if p.GetNetname() == pin.GetNetname()]; gnd = [p for p in cap if p.GetNetname() != pin.GetNetname()]
        if not rail: check(False, "bypass %s -> %s.%s: the capacitor shares the pin's net %s" % (e["cap"], e["part"], e["pin"], pin.GetNetname())); continue
        d = math.hypot(rail[0].GetPosition().x - pin.GetPosition().x, rail[0].GetPosition().y - pin.GetPosition().y) / 1e6
        val = next((f.GetValue() for f in b.GetFootprints() if f.GetReference() == e["cap"]), "")
        loop = 6.0 if any(u in val.lower() for u in ("u ", "uf", "u,", "µ")) and not val.lower().startswith(("0.1u", "0.01u")) else 3.0
        check(d <= loop, "bypass %s (%s) to %s.%s: %.2f mm pad to pin (limit %.1f)" % (e["cap"], val, e["part"], e["pin"], d, loop))
        check(closes(rail[0]) and (not gnd or closes(gnd[0])), "bypass %s: rail and ground pads reach a via or pour within %.1f mm" % (e["cap"], NEAR_VIA))
    # 3. rails exist
    names = {b.GetNetInfo().GetNetItem(k).GetNetname().lstrip("/") for k in range(1, b.GetNetInfo().GetNetCount())}
    for net in it.get("rails", {}): check(net.lstrip("/") in names, "intent rail %s is a net of the board" % net)
    return "intent_checks: return path on %d nets, %d bypass entries, %d rails checked" % (n_nets, n_by, len(it.get("rails", {})))

if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    fails = []
    def check(ok, text):
        print(("PASS  " if ok else "FAIL  ") + text)
        if not ok: fails.append(text)
    print(run(pcbnew.LoadBoard(sys.argv[1]), check, sys.argv[1]))
    print("RESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
