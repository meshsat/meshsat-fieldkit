#!/usr/bin/env bash
# Usage: build_e2.sh <ecad dir> <deliverable dirname> : PCB-E2 RF JUNCTION (bare board, no schematic): generate, DRC, gerbers,
# renders, 1:1 prints, then the deliverable folder with an empty CPL (no assembly) and the footprint library.
set -uo pipefail
cd "$1/pcb-e5-block"; N=pcb-e5-block; REL="$(cd ../..; pwd)/release/${MESHSAT_FK_REV:-revA}"; D="$REL/boards/$2"
python3 ../tools/gen_pcb_e5.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | tail -2
# OWNER RULING 7 (12 September 2026): the two-layer boards are ordered at 2 oz, which is what the prose
# has always claimed. full.sh writes the stackup into every board it builds and E5 does not go through
# full.sh, so its board carried none and the order notes' copper weight rested on nothing.
python3 ../tools/stackup_write.py $N.kicad_pcb 2>&1 | tail -1
../tools/build_pcb.sh . $N 2>&1 | grep -E '^DRC|copper'
grep -E '^\[' out/$N-drc.rpt | sed 's/:.*//' | sort | uniq -c | sort -rn
rm -rf "$D"; mkdir -p "$D"; echo "Designator,Mid X,Mid Y,Layer,Rotation" > "$D/$N-cpl.csv"
cp out/$N-gerbers.zip out/$N-drc.rpt out/$N-render-top.png out/$N-render-bottom.png out/$N-1to1-top.pdf out/$N-1to1-bottom-mirrored.pdf $N.kicad_pcb $N.kicad_pro "$D"/
cp -r ../meshsat.pretty "$D"/; unzip -l out/$N-gerbers.zip | tail -1; echo "deliverables: $D ($(ls "$D" | wc -l) items)"; echo BUILD-E5-DONE
