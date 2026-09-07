#!/usr/bin/env bash
# dsn_export.sh <board.kicad_pcb> <out.dsn> "<plane nets csv>" "<power layers>": the DSN the route scripts make (zones off except the plane nets' zones
# on the power layers, those layers typed power and their board-wide wire keep-outs dropped), for a board that already carries locked tracks.
set -uo pipefail
B="$1"; D="$2"; PN="${3:-}"; PL="${4:-}"
python3 - "$B" "$D" "$PN" "$PL" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); keep_nets = set(x for x in sys.argv[3].split(",") if x); keep_layers = set(sys.argv[4].split()); kept = 0
for z in list(b.Zones()):
    if not z.GetIsRuleArea() and z.GetNetname() in keep_nets and any(b.GetLayerName(l) in keep_layers for l in z.GetLayerSet().Seq()): kept += 1; continue
    if not z.GetIsRuleArea() and not z.GetZoneName().startswith(("VOUT island", "inductor tap")): b.Remove(z)
tmp = sys.argv[2].replace(".dsn", "-noplanes.kicad_pcb"); pcbnew.SaveBoard(tmp, b)
b2 = pcbnew.LoadBoard(tmp); print("dsn_export: planes kept", kept, "DSN export:", pcbnew.ExportSpecctraDSN(b2, sys.argv[2]))
PY
if [ -n "$PL" ]; then python3 - "$D" $PL <<'PYPL'
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
open(fn, "w").write("".join(out)); print("dsn_export: power layers", ", ".join(layers), "(%d typed, %d keep-outs dropped)" % (n1, n2))
PYPL
fi
