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
cfg () { python3 -c "import json,sys; d=json.load(open(sys.argv[1])).get('finish',{}); v=d.get(sys.argv[2]); print('' if v is None else (','.join(v) if isinstance(v,list) else ('1' if v is True else ('' if v is False else v))))" "$CFG" "$2"; }
N="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['name'])" "$CFG")"
STUB_L="$(cfg x stub_layers)"; POUR="$(cfg x pour_nets)"; PAIRM="$(cfg x pair_match)"
AUDIT="$(cfg x pair_audit_nets)"; PFIX="$(cfg x post_fix)"; PRUNED="$(cfg x pruned_gate)"; GGREP="$(cfg x gate_grep)"
STUB_ENV="$(cfg x stub_env)"   # A gives the stub router a wider window and a higher node cap; nothing else does
CONT="$(python3 -c "import json,sys; c=json.load(open(sys.argv[1])).get('finish',{}).get('cont_route'); print('' if not c else '%d %d %d' % (c['max_opens'], c['passes'], c['timeout_s']))" "$CFG")"
TAG="$(echo "$PHASE" | tr 'A-Z' 'a-z')"; FLAG="out/$TAG-clean.txt"; DELIV="meshsat-pcb-$L-revA-$PHASE"
cd "$E/$PROJ" || { echo "finish: no project directory $E/$PROJ"; exit 2; }
rm -f "$FLAG" out/par-score.txt out/contracts.log   # a stale clean flag must never finish a board (register class 6)
stop () { echo "$PHASE $1"; echo open > "$FLAG"; echo "FINISH-$PHASE-DONE"; exit 1; }

# A wait with a deadline: if the producer crashes or the marker is never written this job used to be immortal.
W=0; while ! grep -q PARALLEL-DONE "$LOG" 2>/dev/null; do sleep 30; W=$((W + 30));
  if [ "$W" -ge "${FINISH_WAIT_S:-21600}" ]; then echo "finish: no PARALLEL-DONE in $LOG after ${W} s; refusing"; exit 1; fi
done
grep -E 'attempt|WINNER' "$LOG"
$T/drc.sh $N.kicad_pcb out/$N-drc.json
cp $N.kicad_pcb out/$N-par-routed.kicad_pcb

# --- the order, and it is the whole reason this file exists ---
# 1. the router's knot (two nets' tracks tangled at one spot, 20 to 25 shorts) goes before anything else
python3 $T/unknot.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep unknot && python3 $T/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup
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
  if [ "$UN" -gt 0 ] && [ "$UN" -le "$1" ]; then $T/cont_route.sh "$PWD" $N "$2" "$3" 2>&1 | grep -E 'cont:'; $T/drc.sh $N.kicad_pcb out/$N-drc.json; fi
fi
# 4. ONLY NOW the stub router, on a board that is clean and whose pours are filled
env STUB_LAYERS=$STUB_L STUB_GRID=0.1 $STUB_ENV nice -n 10 python3 $T/stub_router.py $N.kicad_pcb out/$N-drc.json > out/$N-stub.log 2>&1 || stop "stub router CRASHED, exit $? (out/$N-stub.log)"
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
bash $T/quality_pass.sh "$PWD" $N > out/$N-quality-run.log 2>&1 || echo "quality_pass.sh exited $? (out/$N-quality-run.log)"; grep -E "quality:|Traceback" out/$N-quality-run.log | tail -6
python3 $T/silk_fix_all.py $N.kicad_pcb $L 2>&1 | grep -vE 'Debug|leak' | tail -2

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
[ -n "$PRUNED" ] && { python3 $T/pruned_gate.py $N.kicad_pcb out/$N-pruned.txt 2>&1 | grep -E 'pruned_gate' | tail -6; python3 $T/pruned_gate.py $N.kicad_pcb out/$N-pruned.txt >/dev/null 2>&1 || stop "PRUNED PAD NOT REACHED by the router"; }

# every gate below runs ONCE and its exit code is its verdict; the reason comes from its verdict JSON
python3 $T/check_pcb_$L.py $N.kicad_pcb > out/gate-$N.log 2>&1; GATE=$?; grep -E "$GGREP" out/gate-$N.log | tail -14
[ "$GATE" -eq 0 ] || stop "GATE $(python3 $T/verdict.py read out/check_pcb_$L.verdict.json 2>&1 | tail -1) on the routed board"
python3 $T/dc_drop.py $N.kicad_pcb --json out/$N-dc_drop.json > out/$N-dc_drop.log 2>&1; DC=$?; grep -E 'dc_drop' out/$N-dc_drop.log | tail -14
[ "$DC" -eq 0 ] || stop "DC DROP $(python3 $T/verdict.py read out/dc_drop.verdict.json 2>&1 | tail -1)"
python3 $T/stackup_write.py $N.kicad_pcb 2>&1 | tail -1
python3 $T/impedance_check.py $N.kicad_pcb --json out/$N-impedance.json > out/$N-impedance.log 2>&1; IM=$?; grep -E 'impedance' out/$N-impedance.log | tail -14
[ "$IM" -eq 0 ] || stop "IMPEDANCE $(python3 $T/verdict.py read out/impedance_check.verdict.json 2>&1 | tail -1)"
python3 $T/netlist_board.py $N.kicad_pcb out/$N.net > out/netlist_board.log 2>&1; NB=$?; tail -2 out/netlist_board.log
[ "$NB" -eq 0 ] || stop "BOARD DOES NOT MATCH ITS NETLIST $(python3 $T/verdict.py read out/netlist_board.verdict.json 2>&1 | tail -1)"
python3 $T/check_contracts.py .. > out/contracts.log 2>&1; grep -E 'FAIL|MISSING' out/contracts.log | head -12
grep -q 'ALL CONTRACTS PASS' out/contracts.log && echo 'contracts: ALL PASS' || stop "CONTRACTS FAILED (out/contracts.log)"
CLEAN=$(cat "$FLAG" 2>/dev/null || echo missing); [ "$CLEAN" = clean ] || { echo "$PHASE NOT CLEAN, not finishing"; echo "FINISH-$PHASE-DONE"; exit 1; }
cd "$E"; ./tools/finish_board.sh "$PROJ" "$N" "$PFIX" "$DELIV" 2>&1 | tail -16
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "$PHASE: finish_board REFUSED the deliverable"; echo "FINISH-$PHASE-DONE"; exit 1; }
echo "FINISH-$PHASE-DONE"
