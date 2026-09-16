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
# THE NAME COMES FROM THE BOARD TABLE, AND E5 HAS NONE. Board E5 is a bare contact interposer: it is generated
# by gen_pcb_e5.py from board A's own board file, it has no schematic, no netlist and no routed copper, so it
# has never needed a chain and never got a boards/e5.json. The sweep stopped there with "no board .kicad_pcb"
# and every one of its twenty applicable rule-board pairs stayed INCONCLUSIVE for a reason that was about this
# script rather than about the board. The registry's own applicability data already carries the answer, so the
# fall-back reads it there rather than inventing a board table that would claim a chain this board does not
# have (16 September 2026).
N=$(python3 - "$T" "$L" <<'PYNAME'
import json, os, sys
tools, letter = sys.argv[1], sys.argv[2]
p = os.path.join(tools, "boards", "%s.json" % letter)
if os.path.exists(p):
    print(json.load(open(p, encoding="utf-8"))["name"]); raise SystemExit(0)
sys.path.insert(0, tools)
import rules_lib   # the facts file is the registry's, and rules_lib is its only reader
b = rules_lib.board_facts().get(letter) or {}
name = b.get("project")
if not name:
    sys.stderr.write("gate_sweep: no board table and no project in the facts for %s\n" % letter); raise SystemExit(2)
print(name)
PYNAME
)
P=$E/$PD
[ -f "$P/$N.kicad_pcb" ] || { echo "gate_sweep: no board $P/$N.kicad_pcb"; exit 2; }
S=$P/out/sweep
rm -rf $S; mkdir -p $S/out
# A GATE THIS SWEEP MEANS TO RUN AND CANNOT MUST LEAVE NO VERDICT (16 September 2026). The sweep copies the
# verdicts it produced into <phase>/routed/, and a gate that did not run this time left the PREVIOUS run's
# answer sitting there, taken on the same board, so the freshness check could not see it either. Board E's
# order-code rule read FAIL for exactly that reason, from a sweep in another tree. The verdicts of the gates
# below are removed first: absence is INCONCLUSIVE, which is the honest reading of "this sweep did not judge
# it", and every other producer's evidence in that directory is left alone.
for _g in hardset-routed-board-gate check_pcb_$L check_zone_nets intent_checks intent_rails intent_decoupling \
          intent_return_path intent_return_via dc_drop dc_density impedance_check netlist_board class_floor \
          return_via return_stitch via_audit via_annular fab_limits via_current ref_change thermal spacing \
          edge_length derate clock_check port_protect place_audit check_contracts check_contracts_$L lcsc_fill \
          energy_chain; do
  rm -f "$P/routed/$_g.verdict.json"
done
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
# board E5 had no gate at all until 16 September 2026, and six boards had one: the sweep runs whichever exists
if [ -f $T/check_pcb_$L.py ]; then run "board gate"        python3 $T/check_pcb_$L.py $N.kicad_pcb
else echo "--- board gate"; echo "gate_sweep: there is no check_pcb_$L.py, so nothing asserts a number about this board"; fi
run "zone nets"         python3 $T/check_zone_nets.py $N.kicad_pcb
run "intent"            python3 $T/intent_checks.py $N.kicad_pcb
run "dc drop"           python3 $T/dc_drop.py $N.kicad_pcb
run "impedance"         python3 $T/impedance_check.py $N.kicad_pcb
run "netlist vs board"  python3 $T/netlist_board.py $N.kicad_pcb out/$N.net
run "class floor"       python3 $T/class_floor.py $N.kicad_pcb
run "return vias"       python3 $T/return_via.py $N.kicad_pcb --check
# The SECOND tool of two rules that need both to agree (16 September 2026). place_audit predicts which escape
# fans will collide, which the DRC on a placed board cannot say; lcsc_fill refuses a BOM line with no order
# code, which asking the fabricator about a code cannot say because there is no code to ask about.
run "via table"         python3 $T/via_audit.py $N.kicad_pcb
run "fabricator limits" python3 $T/fab_limits.py $N.kicad_pcb
run "via current"        python3 $T/via_current.py $N.kicad_pcb
run "reference change"   python3 $T/ref_change.py $N.kicad_pcb --check
run "thermal"            python3 $T/thermal.py $N.kicad_pcb
run "hv spacing"         python3 $T/spacing.py $N.kicad_pcb
run "electrical length"  python3 $T/edge_length.py $N.kicad_pcb
# These two read the NETLIST this sweep rebuilt, not the board: a part's rating against the rail it sits on,
# and every crystal's load network. Both are schematic properties, so they are true of the board whether or not
# it has been routed.
[ -s out/$N.net ] && run "derating" python3 $T/derate.py out/$N.net
[ -s out/$N.net ] && run "crystals" python3 $T/clock_check.py out/$N.net
[ -s out/$N.net ] && run "exposed ports" python3 $T/port_protect.py out/$N.net
run "placement predictor" python3 $T/place_audit.py $N.kicad_pcb
# THE CROSS-BOARD CONTRACTS, which nothing was re-judging (16 September 2026). SCH-003 and RF-002 read
# INCONCLUSIVE on all seven boards for one reason: their evidence was taken under an older rule set and no
# sweep produced a new one. The contracts need the OTHER boards' netlists, and this tree already has them: the
# sweep driver copies every sibling's `out/*.net` in before it starts, and this board's own netlist was rebuilt
# above. It is read-only by construction, like everything else here: check_contracts.py opens netlists and
# writes a verdict.
run "cross-board contracts" python3 $T/check_contracts.py "$E"
# THE STORED-ENERGY CHAIN (rules BAT-002 and PWR-003, 16 September 2026). It is a property of the SET rather
# than of one board, like the contracts above: the chain runs from the pack through four boards, and a stage
# is checked against the netlist of the board it claims to be on. Every board's evidence carries the verdict,
# because every board the chain crosses is judged by it.
run "energy chain" python3 $T/energy_chain.py --ecad "$E"
# The order-code gate reads a BOM THAT ALREADY EXISTS and never makes one. Exporting it here would turn this
# sweep into a producer of a fabrication artefact, which the execution-paths floor refuses and is right to:
# read-only is this tool's whole property, and a producer that writes only into its own copy is still a
# producer. Where the deliverable folder holds a BOM, it is judged; where it does not, the rule stays
# INCONCLUSIVE, which is the honest reading of "nobody has exported one".
# AND IT READS THE FOLDER OF THE PHASE THIS BOARD DECLARES, not the first one a glob returns (16 September
# 2026). `ls <boards>/*-E*/...  | head -1` returns meshsat-pcb-e-revA-E4, the folder cut on 4 September, so
# board E's order codes were being judged against a bill of materials eleven days and five phases old: eleven
# blank codes that the board being built does not have. Every board has three or four folders, so every board
# was reading its oldest. A folder for a phase the tree is not cutting is not evidence about the board, in
# either direction, so where the declared phase has no folder the rule stays INCONCLUSIVE and says why.
_PHASE=$(python3 -c "import json,sys;print((json.load(open(sys.argv[1])).get('phase') or '').upper())" "$T/boards/$L.json" 2>/dev/null)
_BOM=""
if [ -n "$_PHASE" ]; then _BOM=$(ls "$E/../release/revA/boards/"*"-$_PHASE"/$N-bom.csv 2>/dev/null | head -1); fi
if [ -n "$_BOM" ]; then run "order codes" python3 $T/lcsc_fill.py "$_BOM"
elif [ -n "$_PHASE" ]; then echo "--- order codes"; echo "gate_sweep: no deliverable folder for $N at its declared phase $_PHASE (the folders that exist are for earlier phases), so the order-code rule is not judged here"
else echo "--- order codes"; echo "gate_sweep: $L declares no phase, so there is no folder to judge"; fi
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
# THE DRC REPORT TRAVELS WITH THE BOARD TOO (16 September 2026). Board E's routed/ held a DRC report saying
# zero unconnected items, written by the E9 deliverable's finish on 13 September, beside a board this sweep
# measures at one. The report is the artefact a person opens to see WHICH connection is open, and it was
# describing a different board; the verdict beside it was right the whole time, which is how it survived.
cp out/$N-drc.json $P/routed/ 2>/dev/null
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
