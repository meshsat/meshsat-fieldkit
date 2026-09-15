#!/usr/bin/env bash
# gate_sweep.sh <ecad dir> <phase dir> <letter> [label]
#
# Re-judge one board under TODAY'S rule set, changing nothing (MESHSAT-862, 16 September 2026).
#
# The audit's largest single category of INCONCLUSIVE is not a missing check: it is evidence that exists and is
# older than the rule set it would be read under. A verdict written before the registry does not name the rule
# set it was taken under, so it is history rather than a decision, and the computed readiness says so. This
# sweep produces current evidence for a board that is already routed, without routing it again.
#
# READ-ONLY IS THE PROPERTY, and it is enforced by construction rather than by care: every gate runs in a COPY
# of the project under out/sweep/, and the board's sha256 is taken before and after and compared. Nothing here
# may fix, prune, stitch, close or fill anything. `return_via.py` runs with --check for exactly that reason:
# the same file is a judge and a fixer, and only the judge belongs in a sweep.
#
# The verdicts land in <phase dir>/routed/, which is committed: a board's evidence travels with the board,
# so the readiness can be recomputed on a host with no KiCad on it.
set -uo pipefail
E=${1:?ecad dir}; PD=${2:?phase dir}; L=${3:?letter}; LABEL=${4:-sweep}
T=$E/tools
N=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['name'])" $T/boards/$L.json)
P=$E/$PD
[ -f "$P/$N.kicad_pcb" ] || { echo "gate_sweep: no board $P/$N.kicad_pcb"; exit 2; }
S=$P/out/sweep
rm -rf $S; mkdir -p $S/out
BEFORE=$(sha256sum $P/$N.kicad_pcb | cut -c1-64)
cp $P/$N.kicad_pcb $P/$N.kicad_pro $S/ 2>/dev/null
[ -f $P/$N.kicad_prl ] && cp $P/$N.kicad_prl $S/
[ -f $P/$N.kicad_sch ] && cp $P/$N.kicad_sch $S/
for f in $P/erc-allow.txt $P/bypass-allow.txt $P/lcsc-allow.txt $P/pair-header-allow.txt $P/fp-lib-table; do [ -f $f ] && cp $f $S/; done
cd $S || exit 2

echo "gate_sweep: $L $PD $N  board ${BEFORE:0:16}  label $LABEL"
# The schematic is regenerated so the netlist and the intent file are OUTPUTS of this sweep and not files that
# happen to be there: netlist_board and intent_checks are only meaningful against the netlist this board claims.
PHASE=$LABEL python3 $T/gen_sch_$L.py $N.kicad_sch $N > out/gen_sch.log 2>&1 \
  && $T/build_sch.sh . $N > out/build_sch.log 2>&1 \
  || echo "gate_sweep: the schematic could not be rebuilt, netlist-dependent gates will be INCONCLUSIVE (see out/build_sch.log)"

$T/drc.sh $N.kicad_pcb out/$N-drc.json > out/drc.log 2>&1
python3 $T/hardset.py out/$N-drc.json post --label 'routed-board gate' 2>&1 | tail -2

run() { echo "--- $1"; shift; timeout 1800 "$@" 2>&1 | tail -3; }
run "board gate"        python3 $T/check_pcb_$L.py $N.kicad_pcb
run "zone nets"         python3 $T/check_zone_nets.py $N.kicad_pcb
run "intent"            python3 $T/intent_checks.py $N.kicad_pcb
run "dc drop"           python3 $T/dc_drop.py $N.kicad_pcb
run "impedance"         python3 $T/impedance_check.py $N.kicad_pcb
run "netlist vs board"  python3 $T/netlist_board.py $N.kicad_pcb out/$N.net
run "class floor"       python3 $T/class_floor.py $N.kicad_pcb
run "return vias"       python3 $T/return_via.py $N.kicad_pcb --check
# return_gaps.py is a REPORT and not a gate: it says where rule 1's uncovered millimetres are, which is what a
# person needs to fix them, while intent_checks item 1 is what decides. Its output is kept as a log beside the
# verdicts, never as evidence.
[ -f $T/return_gaps.py ] && timeout 900 python3 $T/return_gaps.py $N.kicad_pcb > out/return_gaps.log 2>&1

AFTER=$(sha256sum $N.kicad_pcb | cut -c1-64)
if [ "$BEFORE" != "$AFTER" ]; then
  echo "gate_sweep: REFUSED, a gate changed the board under a read-only sweep ($BEFORE -> $AFTER); no evidence written"
  exit 1
fi
mkdir -p $P/routed
cp out/*.verdict.json $P/routed/ 2>/dev/null
python3 - "$P/routed/sweep.json" "$BEFORE" "$LABEL" "$N" <<'PY'
import json, sys, subprocess, datetime
out, sha, label, name = sys.argv[1:5]
try: tools = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
except Exception: tools = ""
json.dump({"what": "a read-only re-judgement of this board under the rule set named in each verdict",
           "board": name, "board_sha256": sha, "label": label, "tools": tools,
           "taken": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "read_only": "the board sha256 was identical before and after; a sweep that changes a board writes nothing"},
          open(out, "w"), indent=1)
PY
echo "gate_sweep: $(ls $P/routed/*.verdict.json 2>/dev/null | wc -l) verdict(s) in $PD/routed, board unchanged"
echo "GATE-SWEEP-DONE $L $PD"
