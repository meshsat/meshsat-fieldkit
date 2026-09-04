#!/usr/bin/env bash
# Usage: finish_board.sh <dir> <name> <postfix script or -> <deliverable dirname> : post-route fixes, DRC + fab files, JLC BOM/CPL + LCSC fill, deliverables copy
# The deliverable folder lands in v2/release/${MESHSAT_FK_REV:-revA}/boards/<dirname> of the meshsat-fieldkit repo (derived from this script's location).
set -uo pipefail
TOOLS="$(cd "$(dirname "$0")" && pwd)"; RELEASE="$(dirname "$(dirname "$TOOLS")")/release/${MESHSAT_FK_REV:-revA}"
cd "$1"; N="$2"; PF="$3"; D="$RELEASE/boards/$4"; mkdir -p "$RELEASE/boards"
python3 - "$N" <<'PY' || exit 2
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1] + ".kicad_pcb"); pads = sum(1 for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode() > 0)
tracks = sum(1 for t in b.GetTracks()); fps = len(list(b.GetFootprints()))
if pads > 20 and tracks == 0: print("finish_board: %d footprints, %d connected pads and no tracks: this board was never placed and routed, refusing to finish it" % (fps, pads)); sys.exit(2)
print("finish_board: %d footprints, %d connected pads, %d tracks" % (fps, pads, tracks))
PY
if [ "$PF" != "-" ]; then NO_GAPS=1 python3 ../tools/$PF $N.kicad_pcb out/$N-drc.json 2>&1 | grep -vE 'Debug|memory leak' | tail -3; fi
python3 ../tools/net_tie.py $N.kicad_pcb
../tools/build_pcb.sh . $N 2>&1 | grep -E '^DRC'
../tools/export_jlc.sh . $N 2>&1 | grep JLC
python3 ../tools/lcsc_fill.py out/jlc/$N-bom.csv
[ -f out/jlc/README-fab.custom ] && cp out/jlc/README-fab.custom out/jlc/README-fab.txt
grep -E '^\[' out/$N-drc.rpt | sed 's/:.*//' | sort | uniq -c | sort -rn
python3 - "$N" <<'PY'
import json, sys
d = json.load(open('out/%s-drc.json' % sys.argv[1]))
print('unrouted:', len(d.get('unconnected_items', [])))
for v in d.get('unconnected_items', []): print('   ', ' / '.join(i.get('description', '')[:70] for i in v.get('items', [])))
for t in ('clearance', 'shorting_items', 'tracks_crossing', 'copper_edge_clearance', 'hole_clearance'):
    for v in [v for v in d['violations'] if v['type'] == t][:4]: print('  ', t, '|', ' / '.join(i.get('description', '')[:60] for i in v.get('items', [])))
PY
rm -rf "$D"; mkdir -p "$D"
cp out/$N-gerbers.zip out/jlc/$N-bom.csv out/jlc/$N-cpl.csv out/jlc/README-fab.txt out/$N-drc.rpt out/$N-schematic.pdf out/$N-bom.csv out/$N-render-top.png out/$N-render-bottom.png out/$N-1to1-top.pdf out/$N-1to1-bottom-mirrored.pdf $N.kicad_pcb $N.kicad_sch $N.kicad_pro "$D"/ 2>/dev/null
cp -r ../meshsat.pretty "$D"/ 2>/dev/null; echo "deliverables: $D ($(ls "$D" | wc -l) items)"
