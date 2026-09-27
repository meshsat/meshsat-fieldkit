#!/bin/bash
# r8int6: stream w4c onto the integration worktree, in the stream's integration order (its six files, the registry, the
# documents, the vendor sheet), the registry and document drafts in their r8int6 re-derivations. Idempotent.
# Usage: apply_w4c_r8int6.sh <worktree root> <stream worktree root>
set -e
W=$1; S=$2; K=$(dirname "$(readlink -f "$0")")
E=v2/ecad; T=$E/tools; C=$E/pcb-c-display-c8
for f in $T/gen_sch_c.py $T/boards/c.json $C/pcb-c-display.kicad_sch $C/out/pcb-c-display.net \
         $C/out/pcb-c-display-intent.json $C/out/pcb-c-display.net.prov.json; do cp "$S/$f" "$W/$f"; done
python3 "$K/derive_w4c_r8int6.py" "$K"
python3 "$K/apply_registry_r8int6.py" "$W"
python3 "$K/patch_docs_r8int6.py" "$W"
python3 "$K/fixes_w4c_r8int6.py" "$W"
