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
# THE AUTHORITATIVE GATE, AFTER THE LAST MUTATION (10 September 2026; round-two red teams, report 1 P1). The routed board's
# clean flag is written by the finish BEFORE this script runs, and this script then changes the board: the post-fix, and
# net_tie.py above. Until now the DRC that followed those changes was printed with --label, which returns 0 whatever it counts,
# so a regression introduced by the last mutation could be packaged and promoted. The board is gated here, on the fifteen types
# and on unrouted, and the deliverable is built from the file that passed.
python3 ../tools/hardset.py out/$N-drc.json post --label 'deliverable DRC' --examples 4 --gate out/$N-deliverable-gate.txt --counts out/$N-deliverable-counts.txt
read GH GU < out/$N-deliverable-counts.txt
python3 -c "import json; d=json.load(open('out/$N-drc.json')); [print('   unrouted:', ' / '.join(i.get('description', '')[:70] for i in v.get('items', []))) for v in d.get('unconnected_items', [])]"
# A QUOTE-ONLY deliverable is the project's own idiom for a held board (make_handoff.py accepts `<folder>-quote` and stamps
# QUOTE ONLY in the notes and the index; B16's was exported from a placed, unrouted board for the JLCPCB cart). It is exempt
# by its name rather than by a flag, and it says so; FINISH_ALLOW_DIRTY=1 is the deliberate override for anything else.
case "$4" in *-quote) QUOTE=1;; *) QUOTE=0;; esac
[ "$QUOTE" = 1 ] && echo "finish_board: QUOTE ONLY deliverable, the hard and unrouted gate does not apply ($GH hard, $GU unrouted)"
if [ "$QUOTE" != 1 ] && [ "${FINISH_ALLOW_DIRTY:-0}" != 1 ] && { [ "$GH" -ne 0 ] || [ "$GU" -ne 0 ]; }; then
  echo "finish_board: REFUSED after the last board change: $GH hard, $GU unrouted. Nothing is staged and the previous deliverable is untouched."
  echo "finish_board: (the routed board was judged before the post-fix and net_tie; this is the board the deliverable would have carried)"
  exit 4
fi
# The sha256 of the exact board the deliverable is built from, carried into the folder so a reader can tie the two together.
sha256sum $N.kicad_pcb | awk '{print $1}' > out/$N-board.sha256; echo "finish_board: gated clean, board sha256 $(cut -c1-16 out/$N-board.sha256)" 
# 10 September 2026 (report 1, item 3): the deliverable is built in a staging folder and PROMOTED only after the read-back passes.
# It used to remove the existing folder first and rebuild in place, so a refused rebuild destroyed the deliverable that was there.
STAGE="$D.staging.$$"; rm -rf "$STAGE"; mkdir -p "$STAGE"
# 8 Sep 2026 15:35: out/jlc/$N-bom.csv and out/$N-bom.csv share a basename, so this cp refused the second ("will not overwrite just-created") and returned 1;
# under set -e that ended the script here, which is why no deliverable since this morning carried meshsat.pretty and why verify_deliverable.py below never ran.
# The deliverable keeps the JLC-form BOM under the plain name (what make_handoff.py and the gate read) and the generator's full BOM beside it.
cp out/$N-gerbers.zip out/jlc/$N-bom.csv out/jlc/$N-cpl.csv out/jlc/README-fab.txt out/$N-drc.rpt out/$N-schematic.pdf out/$N-render-top.png out/$N-render-bottom.png out/$N-1to1-top.pdf out/$N-1to1-bottom-mirrored.pdf $N.kicad_pcb $N.kicad_sch $N.kicad_pro out/jlc/$N-bom.status "$STAGE"/
[ -f out/$N-bom.csv ] && cp out/$N-bom.csv "$STAGE"/$N-bom-full.csv || true
cp out/$N-board.sha256 "$STAGE"/
cp -r ../meshsat.pretty "$STAGE"/; echo "deliverables staged: $STAGE ($(ls "$STAGE" | wc -l) items)"
# 8 Sep 2026 (MESHSAT-862): the deliverable is read back (every item, the gerber zip against the copper layer count, BOM and CPL form); a FAIL removes the folder
CU=$(python3 -c "import pcbnew; print(pcbnew.LoadBoard('$N.kicad_pcb').GetCopperLayerCount())" 2>/dev/null | tail -1)
python3 ../tools/verify_deliverable.py "$STAGE" $N "$CU" || { echo "finish_board: deliverable REFUSED, staging folder removed, the previous deliverable is untouched"; rm -rf "$STAGE"; exit 3; }
rm -rf "$D.prev"; [ -d "$D" ] && mv "$D" "$D.prev"; mv "$STAGE" "$D"; rm -rf "$D.prev"   # promoted only after the read-back passed
echo "deliverables: $D ($(ls "$D" | wc -l) items)"
