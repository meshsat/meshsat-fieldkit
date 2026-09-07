#!/usr/bin/env bash
# Usage: finish_board.sh <dir> <name> <postfix script or -> <deliverable dirname> : post-route fixes, DRC + fab files, JLC BOM/CPL + LCSC fill, deliverables copy
# The deliverable folder lands in v2/release/${MESHSAT_FK_REV:-revA}/boards/<dirname> of the meshsat-fieldkit repo (derived from this script's location).
set -euo pipefail   # 8 Sep 2026 (MESHSAT-862): -e too; the 6 Sep deliverable lost its gerber zip to a silent cp
TOOLS="$(cd "$(dirname "$0")" && pwd)"; RELEASE="$(dirname "$(dirname "$TOOLS")")/release/${MESHSAT_FK_REV:-revA}"
cd "$1"; N="$2"; PF="$3"; D="$RELEASE/boards/$4"; mkdir -p "$RELEASE/boards"
python3 - "$N" <<'PY' || exit 2
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1] + ".kicad_pcb"); pads = sum(1 for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode() > 0)
tracks = sum(1 for t in b.GetTracks()); fps = len(list(b.GetFootprints()))
if pads > 20 and tracks == 0: print("finish_board: %d footprints, %d connected pads and no tracks: this board was never placed and routed, refusing to finish it" % (fps, pads)); sys.exit(2)
print("finish_board: %d footprints, %d connected pads, %d tracks" % (fps, pads, tracks))
PY
if [ "$PF" != "-" ]; then NO_GAPS=1 python3 ../tools/$PF $N.kicad_pcb out/$N-drc.json > out/$N-postfix.log 2>&1 || { echo "post-fix $PF failed (out/$N-postfix.log)"; exit 2; }; grep -vE 'Debug|memory leak' out/$N-postfix.log | tail -3; fi
python3 ../tools/net_tie.py $N.kicad_pcb
../tools/build_pcb.sh . $N > out/$N-build_pcb.log 2>&1 || { echo "build_pcb.sh failed (out/$N-build_pcb.log)"; tail -5 out/$N-build_pcb.log; exit 2; }; grep -E '^DRC|gerber copper' out/$N-build_pcb.log
../tools/export_jlc.sh . $N > out/$N-export_jlc.log 2>&1 || { echo "export_jlc.sh failed (out/$N-export_jlc.log)"; exit 2; }; grep JLC out/$N-export_jlc.log
if python3 ../tools/lcsc_fill.py out/jlc/$N-bom.csv; then echo OK > out/jlc/$N-bom.status; else echo "BLANK not allow-listed (lcsc-allow.txt)" > out/jlc/$N-bom.status; fi; echo "BOM status: $(cat out/jlc/$N-bom.status)"   # make_handoff.py refuses an order set on a non-OK status
[ -f out/jlc/README-fab.custom ] && cp out/jlc/README-fab.custom out/jlc/README-fab.txt || true
grep -E '^\\[' out/$N-drc.rpt | sed 's/:.*//' | sort | uniq -c | sort -rn || true
python3 ../tools/hardset.py out/$N-drc.json post --label 'deliverable DRC' --examples 4
python3 -c "import json; d=json.load(open('out/$N-drc.json')); print('unrouted:', len(d.get('unconnected_items', []))); [print('   ', ' / '.join(i.get('description', '')[:70] for i in v.get('items', []))) for v in d.get('unconnected_items', [])]"
rm -rf "$D"; mkdir -p "$D"
cp out/$N-gerbers.zip out/jlc/$N-bom.csv out/jlc/$N-cpl.csv out/jlc/README-fab.txt out/$N-drc.rpt out/$N-schematic.pdf out/$N-bom.csv out/$N-render-top.png out/$N-render-bottom.png out/$N-1to1-top.pdf out/$N-1to1-bottom-mirrored.pdf $N.kicad_pcb $N.kicad_sch $N.kicad_pro out/jlc/$N-bom.status "$D"/
cp -r ../meshsat.pretty "$D"/; echo "deliverables: $D ($(ls "$D" | wc -l) items)"
# 8 Sep 2026 (MESHSAT-862): the deliverable is read back (every item, the gerber zip against the copper layer count, BOM and CPL form); a FAIL removes the folder
CU=$(python3 -c "import pcbnew; print(pcbnew.LoadBoard('$N.kicad_pcb').GetCopperLayerCount())" 2>/dev/null | tail -1)
python3 ../tools/verify_deliverable.py "$D" $N "$CU" || { echo "finish_board: deliverable REFUSED, folder removed"; rm -rf "$D"; exit 3; }
