#!/usr/bin/env bash
# Stream w4ae's integration order (MESHSAT-1357, 27 September 2026), as run in a scratch clone of main 62f26a44.
# Usage: integrate.sh <worktree holding fnd/w4ae's files> <tree to integrate into, a git checkout at the target commit>
# It never commits and never pushes; the integrator commits after reading every diff.
set -euo pipefail
WT=$(cd "$1" && pwd); T=$(cd "$2" && pwd)
export PYTHONDONTWRITEBYTECODE=1
# 1. w4ae's own files (the generators, the board tables, the regenerated A and E files, the filed maker's sheet)
for f in v2/ecad/tools/gen_sch_a.py v2/ecad/tools/gen_sch_e.py v2/ecad/tools/boards/a.json v2/ecad/tools/boards/e.json \
         v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_sch v2/ecad/pcb-a-power-a23/out/pcb-a-power.net \
         v2/ecad/pcb-a-power-a23/out/pcb-a-power.net.prov.json v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json \
         v2/ecad/pcb-e1-dock-e7/pcb-e1-dock.kicad_sch v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net \
         v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net.prov.json v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock-intent.json \
         v2/vendor/zhengxin/zhengxin-ss12-ss120-c51897884.pdf; do
  mkdir -p "$T/$(dirname "$f")"; cp "$WT/$f" "$T/$f"
done
# 2. the drafts filed as records (the registry binds records/w4ae/hot_r1_trace.py)
mkdir -p "$T/v2/docs/records/w4ae"; cp -r "$WT/drafts/w4ae/." "$T/v2/docs/records/w4ae/"
# 3. the registry: two session choices at the next free SC numbers, S-57 closed, S-76, REQ-077, twelve rebinds
python3 "$T/v2/docs/records/w4ae/apply_registry.py" "$T"
# 4. the pages other streams own (CONOPS, HW-FW-CONTRACT, PANEL, IF-AE-DOCK, vendor sources, grade sources, EQ-22)
python3 "$T/v2/docs/records/w4ae/edit_docs.py" "$T"
# 5. the registry follows the pages it binds (CONOPS's needs pin; readings bound to CONOPS, PANEL, grade-sources)
( cd "$T" && python3 v2/docs/records/w4ae/post_docs_registry.py "$T" )
# 6. validate and render
( cd "$T/v2/ecad" && python3 tools/rules_lib.py requirements )
( cd "$T" && python3 v2/ecad/tools/rules_render.py --requirements && python3 v2/ecad/tools/rules_render.py --requirements --check )
( cd "$T" && python3 v2/docs/records/w4ae/hot_r1_trace.py "$T" | tail -1 )
echo "integrate (w4ae): done; re-take A and E in a clean clone (retake_schematic_phase.py --in-place --routed) before rules_status/rules_render"
