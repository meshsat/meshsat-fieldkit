#!/usr/bin/env bash
# Continuation route (A21, 5 Sep 2026): when the parallel attempts leave a few connections open, run Freerouting once more on the routed board
# (its tracks stay as normal wires, the router reroutes what is incomplete and may rip up the rest), then keep the result only if it is better.
# Usage: cont_route.sh <project dir> <name> <passes> [timeout s]; prints "cont: ..." lines; the board is replaced only when unrouted drops and hard stays 0.
set -uo pipefail
cd "$1"; N="$2"; P="${3:-80}"; T="${4:-900}"; W=$PWD/out/cont; mkdir -p "$W"   # absolute: the kill below must match only this directory's router (7 Sep 2026: a relative pattern killed four parallel continuations at once)
cp "$N.kicad_pcb" "$W/$N-before.kicad_pcb"; cp "$N.kicad_pcb" "$W/$N.kicad_pcb"; cp "$N.kicad_pro" "$W/$N.kicad_pro"
# 7 Sep 2026 (B16 chunks): the same plane and power-layer treatment as route_one.sh, or a continuation re-routes every plane pin as a wire
python3 - "$W/$N.kicad_pcb" "$W/$N.dsn" "${FR_PLANE_NETS:-}" "${FR_POWER_LAYERS:-}" <<'PYX'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); keep_nets = set(x for x in sys.argv[3].split(",") if x); keep_layers = set(sys.argv[4].split()); kept = 0
for z in list(b.Zones()):
    if not z.GetIsRuleArea() and z.GetNetname() in keep_nets and any(b.GetLayerName(l) in keep_layers for l in z.GetLayerSet().Seq()): kept += 1; continue
    if not z.GetIsRuleArea() and not z.GetZoneName().startswith(("VOUT island", "inductor tap")): b.Remove(z)
if keep_nets: print("cont: planes kept in the DSN:", kept, "zone(s) of", sorted(keep_nets), "on", sorted(keep_layers))
tmp = sys.argv[2].replace(".dsn", "-noplanes.kicad_pcb"); pcbnew.SaveBoard(tmp, b)
b2 = pcbnew.LoadBoard(tmp); print("cont: DSN export", pcbnew.ExportSpecctraDSN(b2, sys.argv[2]))
PYX
if [ -n "${FR_POWER_LAYERS:-}" ]; then python3 - "$W/$N.dsn" $FR_POWER_LAYERS <<'PYPL'
import re, sys
fn = sys.argv[1]; layers = sys.argv[2:]; s = open(fn).read(); n1 = 0
for lay in layers:
    s, k = re.subn(r"(\(layer %s\s*\(type )signal(\))" % re.escape(lay), r"\1power\2", s); n1 += k
out = []; i = 0; n2 = 0
while True:
    j = s.find("(wire_keepout", i)
    if j < 0: out.append(s[i:]); break
    depth = 0; k = j
    while k < len(s):
        if s[k] == "(": depth += 1
        elif s[k] == ")":
            depth -= 1
            if depth == 0: break
        k += 1
    block = s[j:k + 1]
    if any(("(polygon %s" % lay) in block for lay in layers): out.append(s[i:j]); n2 += 1
    else: out.append(s[i:k + 1])
    i = k + 1
open(fn, "w").write("".join(out)); print("cont: power layers in the DSN:", ", ".join(layers), "(%d layer types changed, %d wire keep-outs dropped)" % (n1, n2))
PYPL
fi
JAR=$HOME/bin/freerouting-1.9.0.jar
timeout "$T" xvfb-run -a java -jar "$JAR" -de "$W/$N.dsn" -do "$W/$N.ses" -mp "$P" -mt ${FR_THREADS:-2} -oit ${FR_OIT:-2} -dct 0 > "$W/fr.log" 2>&1 || echo "cont: freerouting exit $?"
pkill -9 -f "^java .*$W/$N\.dsn" 2>/dev/null || true
[ -s "$W/$N.ses" ] || { echo "cont: no session, board kept"; exit 0; }
python3 - "$W/$N.kicad_pcb" "$W/$N.ses" <<'PYX'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); print("cont: SES import", pcbnew.ImportSpecctraSES(b, sys.argv[2])); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b)
PYX
score() { kicad-cli pcb drc --severity-all --format json -o "$W/drc-$2.json" "$1" >/dev/null 2>&1; python3 - "$W/drc-$2.json" <<'PYX'
import json, collections, sys
d = json.load(open(sys.argv[1])); c = collections.Counter(v['type'] for v in d['violations'])
print(sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'hole_to_hole', 'copper_edge_clearance')), len(d.get('unconnected_items', [])))
PYX
}
read H0 U0 < <(score "$W/$N-before.kicad_pcb" before); read H1 U1 < <(score "$W/$N.kicad_pcb" after)
echo "cont: before hard $H0 unrouted $U0, after hard $H1 unrouted $U1"
if [ "$H1" -eq 0 ] && [ "$U1" -lt "$U0" ]; then cp "$W/$N.kicad_pcb" "$N.kicad_pcb"; echo "cont: board replaced (unrouted $U0 -> $U1)"; else echo "cont: board kept"; fi
