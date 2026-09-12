#!/usr/bin/env bash
# The post-route finish, once, for every board (MESHSAT-862, 11 September 2026).
#
# There were fifteen finish_*.sh, 728 lines, clones of one another with a board name changed, and the drift between
# the clones was not cosmetic: FIVE OF THEM RAN THE STUB ROUTER BEFORE THE CLEAN-UP. The order established with B13
# on 5 September is clean up first, then the stub router, then a zone refill, then the check, and it has two written
# reasons: the stub router's closing via counts as a plane clearance violation when the fill is stale, so a legal
# closure is reverted; and `cleanup_dangling.py` running afterwards can remove the very via the closure used. The
# a22/a23/b19/c7/c8 family carries that order with the comment; d8/d9/e6/p1/p2 carry the opposite with no comment at
# all, and those are the boards whose deliverables shipped. This file has the documented order, once.
#
# Usage: finish.sh <ecad dir> <project dir name> <letter> <phase> <parallel log, relative to the project dir>
#   e.g. finish.sh /root/.../v2/ecad pcb-b-compute-b19 b B19 out/parallel-routeflow.log
# The per-board differences are `finish` in tools/boards/<letter>.json; everything else is the same for every board.
set -uo pipefail
E="$1"; PROJ="$2"; L="$3"; PHASE="$4"; LOG="$5"
T="$E/tools"; CFG="$T/boards/$L.json"
[ -s "$CFG" ] || { echo "finish: no board file $CFG"; exit 2; }
cfg () { python3 -c "
import json,sys
d = json.load(open(sys.argv[1])).get('finish', {}); k = sys.argv[2]
for _b in ('cont_route', 'direct_close'):
    if k.startswith(_b + '_'): d = d.get(_b) or {}; k = k[len(_b) + 1:]; break
v = d.get(k)
sep = ' ' if k == 'power_layers' else ','   # route_one.sh and cont_route.sh take layers space separated, nets comma separated
print('' if v is None else (sep.join(v) if isinstance(v, list) else ('1' if v is True else ('' if v is False else v))))" "$CFG" "$2"; }
N="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['name'])" "$CFG")"
STUB_L="$(cfg x stub_layers)"; POUR="$(cfg x pour_nets)"; PAIRM="$(cfg x pair_match)"
AUDIT="$(cfg x pair_audit_nets)"; PFIX="$(cfg x post_fix)"; PRUNED="$(cfg x pruned_gate)"; GGREP="$(cfg x gate_grep)"
STUB_ENV="$(cfg x stub_env)"; DCL="$(cfg x direct_close_layers)"   # A gives the stub router a wider window and a higher node cap; nothing else does
CONT="$(python3 -c "import json,sys; c=json.load(open(sys.argv[1])).get('finish',{}).get('cont_route'); print('' if not c else '%d %d %d' % (c['max_opens'], c['passes'], c['timeout_s']))" "$CFG")"
TAG="$(echo "$PHASE" | tr 'A-Z' 'a-z')"; FLAG="out/$TAG-clean.txt"; DELIV="meshsat-pcb-$L-revA-$PHASE"
cd "$E/$PROJ" || { echo "finish: no project directory $E/$PROJ"; exit 2; }
rm -f "$FLAG" out/par-score.txt out/contracts.log   # a stale clean flag must never finish a board (register class 6)
# A stop names a log; print its tail with it. The clones exited before their own grep on a crash too, so this
# is not a regression they had and we lost, but the evidence lives on a rented box that is destroyed when its
# last job is fetched, and a message naming a file nobody will ever read is not evidence (11 September 2026).
stop () { echo "$PHASE $1"; [ -n "${2:-}" ] && [ -s "${2:-}" ] && { echo "--- tail of $2"; tail -12 "$2"; }; echo open > "$FLAG"; echo "FINISH-$PHASE-DONE"; exit 1; }

# A wait with a deadline: if the producer crashes or the marker is never written this job used to be immortal.
W=0; while ! grep -q PARALLEL-DONE "$LOG" 2>/dev/null; do sleep 30; W=$((W + 30));
  if [ "$W" -ge "${FINISH_WAIT_S:-21600}" ]; then echo "finish: no PARALLEL-DONE in $LOG after ${W} s; refusing"; exit 1; fi
done
grep -E 'attempt|WINNER' "$LOG"
$T/drc.sh $N.kicad_pcb out/$N-drc.json
cp $N.kicad_pcb out/$N-par-routed.kicad_pcb

# --- the order, and it is the whole reason this file exists ---
# 1. the router's knot (two nets' tracks tangled at one spot, 20 to 25 shorts) goes before anything else
# `unknot | grep unknot && cleanup` made the clean-up conditional on the WORD unknot appearing, in the file
# whose whole point is that no driver branches on a gate's prose (red team round three L2). They are two
# steps; the clean-up runs either way.
python3 $T/unknot.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -E 'unknot' || true
python3 $T/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep -E 'cleanup' || true
$T/drc.sh $N.kicad_pcb out/$N-drc.json
# 2. a pad its own plane cannot reach gets a via in the pad, then the dogbone past its tip
python3 $T/zone_pad_via.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -v "^Debug" | tail -6; $T/drc.sh $N.kicad_pcb out/$N-drc.json
# 3. a pour island with no via of its net gets one (D9's front pour was 57 islands, eleven unstitched, one of 222 mm2)
python3 $T/pour_stitch.py $N.kicad_pcb --nets=$POUR 2>&1 | grep -vE "^Debug|leak" | tail -4; $T/drc.sh $N.kicad_pcb out/$N-drc.json
python3 $T/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | tail -1
cp $N.kicad_pcb out/$N-cleaned.kicad_pcb
$T/drc.sh $N.kicad_pcb out/$N-drc.json
# 3b. a handful of opens get ONE continuation pass of the router before the stub router (A21, 5 September 2026);
# cont_route.sh keeps the board only if it improves. Declared per board, and only A declares it.
if [ -n "$CONT" ]; then
  set -- $CONT
  UN=$(python3 -c "import json; print(len(json.load(open('out/$N-drc.json')).get('unconnected_items', [])))") || stop "no readable DRC JSON before the continuation pass"
  if [ "$UN" -gt 0 ] && [ "$UN" -le "$1" ]; then
    # The continuation exports its OWN DSN and has to be given the same plane treatment the route was given, or it
    # re-routes every plane pin as a wire (C: GND on In1, most of the board's connections). finish.sh passed none and
    # routeflow does not put it in the finish's environment either, so until 12 September 2026 every continuation on
    # every board ran that way. A caller's value still wins, which is how an arm measures the treatment.
    env FR_POWER_LAYERS="${FR_POWER_LAYERS:-$(cfg x cont_route_power_layers)}" FR_PLANE_NETS="${FR_PLANE_NETS:-$(cfg x cont_route_plane_nets)}" \
        $T/cont_route.sh "$PWD" $N "$2" "$3" 2>&1 | grep -E 'cont:'
    $T/drc.sh $N.kicad_pcb out/$N-drc.json
  fi
fi
# 4. ONLY NOW the stub router, on a board that is clean and whose pours are filled
# A time limit on the search, not on a wait: a fine grid over a big window is the difference between closing a
# connection and not (A24, 12 September 2026: the 0.1 mm grid refused both of its last two, the 0.05 mm grid with
# a six-fold window closed both), and it is also the difference between ten minutes and an afternoon. A cut run
# leaves the board as it was, which is the same outcome as a run that closes nothing, so the finish goes on.
env STUB_LAYERS=$STUB_L STUB_GRID=0.1 $STUB_ENV timeout "${STUB_TIMEOUT_S:-$(cfg x stub_timeout_s)}" nice -n 10 python3 $T/stub_router.py $N.kicad_pcb out/$N-drc.json > out/$N-stub.log 2>&1; SR=$?
[ "$SR" -eq 124 ] && echo "stub router: cut at its time limit, the board is as it was"
[ "$SR" -eq 0 ] || [ "$SR" -eq 124 ] || stop "stub router CRASHED, exit $SR (out/$N-stub.log)" "out/$N-stub.log"
grep -E 'closed|FAILED|stub_router|Error' out/$N-stub.log | head -12
# 5. the refill before the check, so a legal closing via is not read against a stale fill
python3 - "$N" <<'PY' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled after the stub router')
PY
$T/drc.sh $N.kicad_pcb out/$N-drc.json
python3 $T/hardset.py out/$N-drc.json post --score out/par-score.txt --label 'after stub router' | grep -v '^hardset:'
[ -s out/par-score.txt ] || stop "no DRC score after the stub router (hardset refused)"
read H < out/par-score.txt
if [ "$H" -ne 0 ]; then
  python3 $T/stub_accept.py out/$N-par-routed.kicad_pcb $N.kicad_pcb out/$N-drc.json 2>&1 | grep stub_accept
  $T/drc.sh $N.kicad_pcb out/$N-drc.json
  H=$(python3 $T/hardset.py out/$N-drc.json post --score out/par-score.txt --label 'after stub_accept' >/dev/null; cat out/par-score.txt)
  echo "after stub_accept: hard $H"
  [ "$H" -eq 0 ] || { echo 'stub router hurt: reverting'; cp out/$N-par-routed.kicad_pcb $N.kicad_pcb; }
fi
python3 $T/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | tail -1
# 5b. a locked stitch via the fill no longer covers is dead at its pour end: the router ran a track past it and
# the fill retreated by its clearance. cleanup_dangling leaves it because a via with a track on it is not
# dangling by its rule, and the board gate then refuses the board for it (P routed 0 hard and 0 unrouted and was
# refused for exactly one). Judged the way the stub router is: keep it only if nothing opened (11 Sep 2026).
# Declared per board and OFF everywhere today (`stitch_prune` in boards/<letter>.json). The tool is written and
# tested, and on 12 September it was measured finding SIXTEEN abandoned vias on board E of which NONE was dead:
# its abandonment test broke at the first zone whose fill missed the via, so a via connected on another layer
# read as abandoned. That is fixed and the same board now gives zero. But the tool has still never removed a via
# that needed removing, so its risk is proved and its value is not, and a pass that cuts copper out of a board
# bound for manufacture does not sit in the path on that balance. It goes back on for a board that presents the
# case, one board at a time, with the number that justified it.
if [ -n "$(cfg x stitch_prune)" ]; then
cp $N.kicad_pcb out/$N-prestitch.kicad_pcb
python3 $T/hardset.py out/$N-drc.json post --counts out/prune-before.txt --label 'before stitch_prune' >/dev/null
read BH BU < out/prune-before.txt
python3 $T/stitch_prune.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | head -4
$T/drc.sh $N.kicad_pcb out/$N-drc.json
python3 $T/hardset.py out/$N-drc.json post --counts out/prune-score.txt --label 'after stitch_prune' >/dev/null
read PH PU < out/prune-score.txt
# Judged against the board BEFORE it, never against zero. Written against zero, it blamed the pruner for an
# open the board already had: E reached the pruner at one open, the pruner changed nothing about that open, and
# the revert fired every time, so the pruner could never help a board that was not already clean
# (11 September 2026, found by reading the line beside "after stub router: hard 0 unrouted 1").
if [ "$PH" -gt "$BH" ] || [ "$PU" -gt "$BU" ]; then
  echo "stitch_prune hurt (hard $BH -> $PH, unrouted $BU -> $PU): reverting"; cp out/$N-prestitch.kicad_pcb $N.kicad_pcb; $T/drc.sh $N.kicad_pcb out/$N-drc.json
else
  echo "stitch_prune kept (hard $BH -> $PH, unrouted $BU -> $PU)"
fi
fi
# 4c. the closure the router stopped short of, proposed as geometry and judged by the DRC (12 September 2026).
# The stub router searches a 0.1 mm raster in which every cell beside a target pad is inside somebody's
# clearance; the segment that closes the gap ends ON that pad, where the pad's own clearance does not apply to
# its own net. A24: /CELL+ closed as a straight 9.59 mm locked track, hard 0, opens 3 to 2, after the stub
# router had refused it. Declared per board, with the number, like every other pass that lays copper here.
if [ -n "$(cfg x direct_close)" ] || [ -n "$(cfg x direct_close_max)" ]; then
  python3 $T/direct_close.py $N.kicad_pcb out/$N-drc.json --max="$(cfg x direct_close_max)" ${DCL:+--layers=$DCL} 2>&1 | grep -a direct_close | tail -12
  $T/drc.sh $N.kicad_pcb out/$N-drc.json
fi
bash $T/quality_pass.sh "$PWD" $N > out/$N-quality-run.log 2>&1 || echo "quality_pass.sh exited $? (out/$N-quality-run.log)"; grep -E "quality:|Traceback" out/$N-quality-run.log | tail -6
python3 $T/silk_fix_all.py $N.kicad_pcb $L "$PHASE" 2>&1 | grep -vE 'Debug|leak' | tail -3

# the pair gate (owner ruling 5 Sep 2026 17:00): a differential pair over 1 mm blocks the finish
if [ -n "$PAIRM" ]; then
  $T/pair_match.sh "$PWD" $N check_pcb_$L.py > out/pair-match.log 2>&1; PM=$?
  grep -E "pair_match|WARN|PASS|meander" out/pair-match.log | cut -c1-140
  if [ "$PM" -ne 0 ]; then
    mkdir -p out/audit; for pr in $(echo "$AUDIT" | tr ',' ' '); do python3 $T/pair_audit.py $N.kicad_pcb $pr out/audit/$pr.png 2>&1 | grep pair_audit; done
    stop "PAIRS NOT MATCHED, not finishing (audit images in out/audit)"
  fi
fi
$T/drc.sh $N.kicad_pcb out/$N-drc.json
python3 $T/hardset.py out/$N-drc.json post --flag "$FLAG" --label 'routed-board gate' | sed 's/^hardset:/routed-board DRC:/'
python3 -c "import json; d=json.load(open('out/$N-drc.json')); [print('  OPEN', ' ~ '.join(i['description'][:50] for i in u['items'])) for u in d.get('unconnected_items', [])[:6]]"
# ONE RUN, ONE DECISION. It ran twice, once to print and once to decide, which is the pattern stage 0
# removed from every board gate and left here (red team round three L2). On B that is two passes over the
# pruned list for one boolean, and worse, two runs can disagree.
if [ -n "$PRUNED" ]; then
  python3 $T/pruned_gate.py $N.kicad_pcb out/$N-pruned.txt > out/pruned_gate.log 2>&1; PRC=$?
  grep -E 'pruned_gate' out/pruned_gate.log | tail -6
  [ "$PRC" -eq 0 ] || stop "PRUNED PAD NOT REACHED by the router"
fi

# every gate below runs ONCE and its exit code is its verdict; the reason comes from its verdict JSON
python3 $T/check_pcb_$L.py $N.kicad_pcb > out/gate-$N.log 2>&1; GATE=$?; grep -E "$GGREP" out/gate-$N.log | tail -14
[ "$GATE" -eq 0 ] || stop "GATE $(python3 $T/verdict.py read out/check_pcb_$L.verdict.json 2>&1 | tail -1) on the routed board" "out/gate-$N.log"
python3 $T/dc_drop.py $N.kicad_pcb --json out/$N-dc_drop.json > out/$N-dc_drop.log 2>&1; DC=$?; grep -E 'dc_drop' out/$N-dc_drop.log | tail -14
[ "$DC" -eq 0 ] || stop "DC DROP $(python3 $T/verdict.py read out/dc_drop.verdict.json 2>&1 | tail -1)" "out/$N-dc_drop.log"
python3 $T/stackup_write.py $N.kicad_pcb 2>&1 | tail -1
python3 $T/impedance_check.py $N.kicad_pcb --json out/$N-impedance.json > out/$N-impedance.log 2>&1; IM=$?; grep -E 'impedance' out/$N-impedance.log | tail -14
[ "$IM" -eq 0 ] || stop "IMPEDANCE $(python3 $T/verdict.py read out/impedance_check.verdict.json 2>&1 | tail -1)" "out/$N-impedance.log"
python3 $T/netlist_board.py $N.kicad_pcb out/$N.net > out/netlist_board.log 2>&1; NB=$?; tail -2 out/netlist_board.log
[ "$NB" -eq 0 ] || stop "BOARD DOES NOT MATCH ITS NETLIST $(python3 $T/verdict.py read out/netlist_board.verdict.json 2>&1 | tail -1)" "out/netlist_board.log"
python3 $T/check_contracts.py .. > out/contracts.log 2>&1; CT=$?; grep -E 'FAIL|MISSING|absent from this tree' out/contracts.log | head -12
# exit 3 is INCONCLUSIVE: a board's netlist is not in this tree, so the cross-board contracts were judged
# against nothing. It still stops the finish, but it is not a verdict on the design and must not read as one.
[ "$CT" -eq 3 ] && stop "CONTRACTS NOT JUDGED: a board this set depends on has not been generated in this tree" "out/contracts.log"
[ "$CT" -eq 0 ] && echo 'contracts: ALL PASS' || stop "CONTRACTS FAILED (out/contracts.log)" "out/contracts.log"
CLEAN=$(cat "$FLAG" 2>/dev/null || echo missing); [ "$CLEAN" = clean ] || { echo "$PHASE NOT CLEAN, not finishing"; echo "FINISH-$PHASE-DONE"; exit 1; }
cd "$E"; ./tools/finish_board.sh "$PROJ" "$N" "$PFIX" "$DELIV" 2>&1 | tail -16
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "$PHASE: finish_board REFUSED the deliverable"; echo "FINISH-$PHASE-DONE"; exit 1; }

# A ROUTED BOARD THAT REACHED ITS GATE MUST LAND SOMEWHERE TRACKED BEFORE THIS SAYS DONE (red team round
# three M5). The lesson was written on 11 September, when four routed boards went with a destroyed rented
# box: "either the phase copies are tracked, or a route that reaches 0 hard is committed the same hour".
# It was written and no step did it, so it depended on somebody remembering within the hour. The board,
# its project file, its DRC report and its verdicts go beside the deliverable, which is tracked; the
# commit is still a person's or a driver's to make, and this at least puts the bytes where one can.
# NOT under release/: that is where fab artefacts live and the execution pin refused this file the moment
# it wrote there, correctly (the pin names which files may produce a gerber, a BOM, a CPL or an order set).
# A routed board and its verdicts are BOARD STATE, and the phase project directory is already tracked.
KEEP="$PROJ/routed"
mkdir -p "$KEEP" 2>/dev/null && {
  cp "$PROJ/$N.kicad_pcb" "$KEEP/" 2>/dev/null
  cp "$PROJ/$N.kicad_pro" "$KEEP/" 2>/dev/null
  cp "$PROJ/out/$N-drc.json" "$KEEP/" 2>/dev/null
  cp "$PROJ"/out/*.verdict.json "$KEEP/" 2>/dev/null
  echo "kept: the routed board and its verdicts are in $KEEP ($(ls "$KEEP" | wc -l) file(s)); commit them"
  echo "      (a board that exists only in a rented box's copy directory exists nowhere: 11 September)"
}
echo "FINISH-$PHASE-DONE"
