#!/bin/bash
# r8int6: stream w4b onto the integration worktree, in the order the stream asked for (its files, the tool and test rows,
# the check_pcb_b block, the page drafts, then the registry), each draft in its r8int6 re-derivation where one exists.
# Idempotent: the copied files are the stream's; each script checks whether its change is already there.
# Usage: apply_w4b_r8int6.sh <worktree root> <stream worktree root>
set -e
W=$1; S=$2; K=$(dirname "$(readlink -f "$0")")
E=v2/ecad; T=$E/tools; B=$E/pcb-b-compute-b19
for f in $T/gen_sch_b.py $T/boards/b.json $B/pcb-b-compute.kicad_sch $B/out/pcb-b-compute.net \
         $B/out/pcb-b-compute-intent.json $B/out/pcb-b-compute.net.prov.json; do
  cp "$S/$f" "$W/$f"   # the stream's file; the fixes below re-apply the comment corrections on every run
done
grep -q "SN74LV1T08" "$W/$T/tx_inhibit.py"            || python3 "$K/tools/apply_tx_inhibit_w4b.py" "$W/$T/tx_inhibit.py"
grep -q "LV1T08\|lv1t08" "$W/$T/tests/test_tx_inhibit.py" || python3 "$K/tools/apply_tx_inhibit_tests_w4b.py" "$W/$T/tests/test_tx_inhibit.py"
grep -q "U536" "$W/$T/check_pcb_b.py"                 || python3 "$K/tools/apply_check_pcb_b_w4b.py" "$W/$T/check_pcb_b.py"
grep -q "## 4c. Stream w4b, board B" "$W/v2/docs/feasibility/EMCON.md" || python3 "$K/page_drafts_w4b_r8int6.py" "$W"
python3 "$K/fixes_w4b_r8int6.py" "$W"
# board B's sidecar: the generator's comments moved (fixes step 1), so its identity is re-stamped; the netlist does not move
( cd "$W/$T" && python3 -c "import sch_prov; sch_prov.write('../pcb-b-compute-b19/out/pcb-b-compute.net', 'b')" )
grep -q "(stream w4b). W4B-D1" "$W/$T/pcb_requirements.yaml" || python3 "$K/apply_registry_r8int6.py" "$W"
