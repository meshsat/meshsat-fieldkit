#!/usr/bin/env bash
# Usage: build_pcb.sh <board-dir> <board-name>   (runs DRC, gerbers, drill, 1:1 PDF, renders)
set -euo pipefail
D="$1"; N="$2"; cd "$D"; mkdir -p out
# 10 September 2026 (round-two red teams, report 1 P1): this ran the DRC with --exit-code-violations inside `cmd && clean ||
# violations`, so EVERY non-zero status read as "the board is dirty" (5 means violations; anything else is a tool failure) and
# a failed export left the previous out/$N-drc.json in place for finish_board.sh to read. One contract now, in drc.sh: the
# report is an output, and hardset.py says what it means.
../tools/drc.sh "$N.kicad_pcb" "out/$N-drc.json"
python3 ../tools/hardset.py "out/$N-drc.json" post --label "DRC" | head -2
kicad-cli pcb drc --severity-all --format report -o "out/$N-drc.rpt" "$N.kicad_pcb" >/dev/null
rm -rf out/gerbers; mkdir -p out/gerbers
CU=$(python3 -c "import pcbnew; b=pcbnew.LoadBoard('$N.kicad_pcb'); n=b.GetCopperLayerCount(); print(','.join(['F.Cu']+['In%d.Cu'%i for i in range(1,n-1)]+['B.Cu']))" 2>/dev/null | tail -1)
echo "gerber copper layers: $CU"
kicad-cli pcb export gerbers --layers $CU,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask --no-x2 --use-drill-file-origin -o out/gerbers/ "$N.kicad_pcb" >/dev/null
kicad-cli pcb export drill --format excellon --excellon-units mm --excellon-zeros-format decimal --drill-origin absolute --generate-map --map-format gerberx2 -o out/gerbers/ "$N.kicad_pcb" >/dev/null
(cd out/gerbers && rm -f "../$N-gerbers.zip" && zip -q "../$N-gerbers.zip" ./*)
kicad-cli pcb export pdf --layers Edge.Cuts,F.Silkscreen,User.Drawings,F.Courtyard --mode-single --drill-shape-opt 2 -o "out/$N-1to1-top.pdf" "$N.kicad_pcb" >/dev/null
kicad-cli pcb export pdf --layers Edge.Cuts,B.Silkscreen --mode-single --mirror --drill-shape-opt 2 -o "out/$N-1to1-bottom-mirrored.pdf" "$N.kicad_pcb" >/dev/null
kicad-cli pcb export svg --layers Edge.Cuts,F.Silkscreen,User.Drawings --page-size-mode 2 --exclude-drawing-sheet -o "out/$N-top.svg" "$N.kicad_pcb" >/dev/null
kicad-cli pcb render --side top --width 1800 --height 1300 --zoom 1.0 --background opaque -o "out/$N-render-top.png" "$N.kicad_pcb" >/dev/null 2>&1 || echo "render top failed"
kicad-cli pcb render --side bottom --width 1800 --height 1300 --zoom 1.0 --background opaque -o "out/$N-render-bottom.png" "$N.kicad_pcb" >/dev/null 2>&1 || echo "render bottom failed"
ls -la out | sed 's/^/  /'
