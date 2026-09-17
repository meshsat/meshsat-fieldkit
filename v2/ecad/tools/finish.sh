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
STUB_ENV="$(cfg x stub_env)"; DCL="$(cfg x direct_close_layers)"; DCB="$(cfg x direct_close_budget_s)"   # A gives the stub router a wider window and a higher node cap; nothing else does
CONT="$(python3 -c "import json,sys; c=json.load(open(sys.argv[1])).get('finish',{}).get('cont_route'); print('' if not c else '%d %d %d' % (c['max_opens'], c['passes'], c['timeout_s']))" "$CFG")"
TAG="$(echo "$PHASE" | tr 'A-Z' 'a-z')"; FLAG="out/$TAG-clean.txt"; DELIV="meshsat-pcb-$L-revA-$PHASE"
. "$T/guarded.sh"; F_T0=$(date +%s)
# what a finish costs, said at every exit (15 September 2026, red team round four L2): the wall seconds and the DRC
# calls and seconds since this finish began, read from the per-call lines drc.sh appends to out/drc-costs.jsonl
costs () { python3 - "$F_T0" <<'PY' 2>/dev/null || true
import json, sys, time, os
t0 = int(sys.argv[1]); n = 0; secs = 0
for l in open("out/drc-costs.jsonl") if os.path.exists("out/drc-costs.jsonl") else []:
    try: r = json.loads(l)
    except ValueError: continue
    if r.get("t", 0) >= t0: n += 1; secs += r.get("seconds", 0)
print("finish: %d s wall, %d DRC call(s), %d s in DRC" % (int(time.time()) - t0, n, secs))
PY
}
cd "$E/$PROJ" || { echo "finish: no project directory $E/$PROJ"; exit 2; }
rm -f "$FLAG" out/par-score.txt out/contracts.log   # a stale clean flag must never finish a board (register class 6)
# A stop names a log; print its tail with it. The clones exited before their own grep on a crash too, so this
# is not a regression they had and we lost, but the evidence lives on a rented box that is destroyed when its
# last job is fetched, and a message naming a file nobody will ever read is not evidence (11 September 2026).
stop () { echo "$PHASE $1"; [ -n "${2:-}" ] && [ -s "${2:-}" ] && { echo "--- tail of $2"; tail -12 "$2"; }; echo open > "$FLAG"; costs; echo "FINISH-$PHASE-DONE"; exit 1; }

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
# The count it is handed, taken here because here is the only place the board is still the router's own: the
# stub stage must not leave it more open than it found it (13 September 2026, A25 went in at 13 and out at 80).
# THE ONE GUARD (15 September 2026, red team round four H2): every copper-editing pass from here on runs under
# `guarded` (tools/guarded.sh): snapshot, run, DRC, compare hard AND unrouted against the board the pass was HANDED,
# keep or restore, one verdict JSON per pass. The stub stage used to carry two hand-rolled guards (hard alone, then the
# open count after A25 went in at 13 and out at 80) and restored `par-routed`, the RAW router board, which is older than
# the board it was handed; the guard restores its own snapshot.
stub_stage () {
  # A time limit on the search, not on a wait: a fine grid over a big window is the difference between closing a
  # connection and not (A24, 12 September 2026: the 0.1 mm grid refused both of its last two, the 0.05 mm grid with
  # a six-fold window closed both), and it is also the difference between ten minutes and an afternoon. A cut run
  # leaves the board as it was, which is the same outcome as a run that closes nothing, so the finish goes on.
  env STUB_LAYERS=$STUB_L STUB_GRID=0.1 $STUB_ENV timeout "${STUB_TIMEOUT_S:-$(cfg x stub_timeout_s)}" nice -n 10 python3 -u $T/stub_router.py $N.kicad_pcb out/$N-drc.json > out/$N-stub.log 2>&1; SR=$?
  [ "$SR" -eq 124 ] && echo "stub router: cut at its time limit, the board is as it was"
  [ "$SR" -eq 0 ] || [ "$SR" -eq 124 ] || stop "stub router CRASHED, exit $SR (out/$N-stub.log)" "out/$N-stub.log"
  grep -E 'closed|FAILED|stub_router|Error' out/$N-stub.log | head -12
  # the refill before the check, so a legal closing via is not read against a stale fill
  python3 - "$N" <<'PY' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled after the stub router')
PY
  $T/drc.sh $N.kicad_pcb out/$N-drc.json
  python3 $T/hardset.py out/$N-drc.json post --score out/par-score.txt --label 'after stub router' --board $N.kicad_pcb | grep -v '^hardset:'
  [ -s out/par-score.txt ] || stop "no DRC score after the stub router (hardset refused)"
  read H < out/par-score.txt
  if [ "$H" -ne 0 ]; then
    # a closure the DRC finds in a hard violation comes off; the rest stay; the guard around this stage then
    # judges what is left against the board it was handed
    python3 $T/stub_accept.py out/$N-guard-stub.kicad_pcb $N.kicad_pcb out/$N-drc.json 2>&1 | grep stub_accept
    python3 - "$N" <<'PY' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b)
PY
    $T/drc.sh $N.kicad_pcb out/$N-drc.json
    H=$(python3 $T/hardset.py out/$N-drc.json post --score out/par-score.txt --label 'after stub_accept' --board $N.kicad_pcb >/dev/null; cat out/par-score.txt)
    echo "after stub_accept: hard $H"
  fi
}
guarded stub stub_stage
python3 $T/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | tail -1
# 5a2. A TRACK SHORTER THAN THE PROCESS CAN DRAW IS AN ISLAND, NOT A CONDUCTOR (16 September 2026, board E11).
# Its re-finish came back hard 0, unrouted 1, and the one open connection was a GND track 0.0002 mm long beside
# U13 pad 2: two tenths of a micrometre of copper that no fabricator draws, which KiCad's connectivity is right
# to call a piece of the net that reaches nothing. `cleanup_dangling` cannot see it because its first line skips
# every net that owns a zone, which is correct for its own job and is exactly why this class survives on plane
# nets. Guarded like every other pass: a dot that touches two items is a bridge and is kept, and the removal is
# refused outright if the unconnected count rises.
guarded dots python3 $T/dot_prune.py $N.kicad_pcb
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
# 15 September 2026 (A34): a locked stitch via the fill has abandoned can be dead only AFTER rail_prune has taken the
# router's parallel copper off the rail (before it, a router track still ended on the via and removing it opened a
# connection: "stitch_prune hurt, reverting"), so the pass runs twice, here and again after rail_prune.
prune_stitch() { guarded stitch_prune python3 $T/stitch_prune.py $N.kicad_pcb; }
if [ -n "$(cfg x stitch_prune)" ]; then prune_stitch; fi
# 4c. the closure the router stopped short of, proposed as geometry and judged by the DRC (12 September 2026).
# The stub router searches a 0.1 mm raster in which every cell beside a target pad is inside somebody's
# clearance; the segment that closes the gap ends ON that pad, where the pad's own clearance does not apply to
# its own net. A24: /CELL+ closed as a straight 9.59 mm locked track, hard 0, opens 3 to 2, after the stub
# router had refused it. Declared per board, with the number, like every other pass that lays copper here.
if [ -n "$(cfg x direct_close)" ] || [ -n "$(cfg x direct_close_max)" ]; then
  # `python3 -u`, and the exit status read: on A26 this tool SEGFAULTED after 1,812 lines of output and the
  # finish showed not one of them, because a buffered stdout dies with the process and a pipeline hides
  # the exit code. A stage that crashes has to say so (14 September 2026).
  # THE BUDGET IS A DECLARATION, NOT A LITERAL (16 September 2026). Board A's re-finish spent its whole
  # 1,800 seconds on five of thirteen open pairs and stopped mid-shape: each candidate costs a DRC, and a
  # 240 by 160 six-layer board's DRC is seven seconds, so a board with a dozen opens needs more than half an
  # hour or it reports "the budget ran out" for the ones it never reached. `direct_close_budget_s` in
  # boards/<letter>.json, with the board's own number and its reason.
  GUARD_QUIET=1 guarded direct_close python3 -u $T/direct_close.py $N.kicad_pcb out/$N-drc.json --max="$(cfg x direct_close_max)" ${DCL:+--layers=$DCL} ${DCB:+--budget-s=$DCB}
  grep -a direct_close out/guard-direct_close.log | tail -12
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
# 15 September 2026 (MESHSAT-862): the router's own copper on a rail the rail's copper already carries comes off
# before the refill and the judgements (rail_prune.py, declared per board): Freerouting never sees a pour, so it
# lays a 0.5 mm inner track in parallel with a band and the solver takes a share of the rail through it.
if [ -n "$(cfg x rail_prune)" ]; then python3 $T/rail_prune.py $N.kicad_pcb 2>&1 | grep -E 'rail_prune|Traceback|Error'; fi
if [ -n "$(cfg x rail_prune)" ] && [ -n "$(cfg x stitch_prune)" ]; then $T/drc.sh $N.kicad_pcb out/$N-drc.json; prune_stitch; fi   # the second pass, on copper the rail prune has just changed
# 6a. THE TRACKS THAT ARE TOO THIN FOR WHAT THEY CARRY (rule PI-001, 16 September 2026). `widen_net.py` was
# written this morning for board A's mezzanine 5 V, which the router laid at its class width for 63.9 mm at
# 1.0 A, and NOTHING RAN IT: it sat in the tools directory with its own tests passing while the rule it was
# written for went on failing on two boards. The same shape as bypass_place.py, which existed for a day before
# any chain called it. It is declared per board (`widen` in boards/<letter>.json, a list of {net, to, steps,
# layers}), it runs AFTER rail_prune so the router copper the rail does not need is already off, and it is
# guarded like every other copper-editing pass on top of its own trial-and-revert.
if [ -n "$(python3 -c "import json,sys; print(len(json.load(open(sys.argv[1])).get('finish',{}).get('widen') or []))" "$CFG")" ] \
   && [ "$(python3 -c "import json,sys; print(len(json.load(open(sys.argv[1])).get('finish',{}).get('widen') or []))" "$CFG")" != "0" ]; then
  python3 -c "
import json,sys
for w in json.load(open(sys.argv[1])).get('finish',{}).get('widen') or []:
    print('%s\t%s\t%s\t%s' % (w['net'], w.get('to',''), ','.join(w.get('steps',[]) if isinstance(w.get('steps'),list) else [str(w.get('steps',''))]).strip(','), ','.join(w.get('layers',[]))))" "$CFG" |
  while IFS=$'\t' read -r WNET WTO WSTEPS WLAYERS; do
    [ -n "$WNET" ] || continue
    GUARD_QUIET=1 guarded "widen-$(echo "$WNET" | tr -d '/+')" python3 -u $T/widen_net.py $N.kicad_pcb "$WNET" \
      ${WTO:+--to} ${WTO:+$WTO} ${WSTEPS:+--steps} ${WSTEPS:+$WSTEPS} ${WLAYERS:+--layers} ${WLAYERS:+$WLAYERS}
  done
fi
# 6. a ground via beside every signal via (owner ruling 15 September 2026 20:15 CEST, rule 2): after every stage that lays
# or removes copper and before the final refill and the routed-board gate, which judges the vias it placed like any other
# copper. The tool keeps its vias only if neither the hard nor the unrouted count rose against the board it was handed.
# Declared per board (`return_via` in boards/<letter>.json), and the gate that follows refuses a board with a signal via
# left without one whether or not the stage ran, so a board that turns it off still has to pass.
if [ -n "$(cfg x return_via)" ]; then
  GUARD_QUIET=1 guarded return_via python3 -u $T/return_via.py $N.kicad_pcb
  grep -a return_via out/guard-return_via.log | head -8
fi
# 13 September 2026 (MESHSAT-862): REFILL BEFORE ANYTHING JUDGES THE COPPER, and this is not a tidy-up.
# The only refill in this script was after the stub router, and between it and the judgements below run
# `stub_accept` (which removes closure copper), `stitch_prune` and its revert (which COPIES BACK a board that
# was never filled), `direct_close` and `quality_pass` (which merged 108 segments out of A26 and 146 out of
# C11). Every one of those changes what a pour can fill, so the gate and `dc_drop` were reading a fill from
# several steps ago. Measured on E8: the finish read `CELL_F pour F.Cu 122 mm2` and refused the rail at a
# conductor ratio of 1.04, and the same board refilled reads **163 mm2 and the rail MET**. A verdict off a
# stale fill is not a verdict about this board.
python3 -c "import pcbnew, sys; b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled before the gate and the rail checks')" $N 2>&1 | grep -vE 'Debug|leak'
$T/drc.sh $N.kicad_pcb out/$N-drc.json
python3 $T/hardset.py out/$N-drc.json post --flag "$FLAG" --label 'routed-board gate' --board $N.kicad_pcb | sed 's/^hardset:/routed-board DRC:/'
python3 -c "import json; d=json.load(open('out/$N-drc.json')); [print('  OPEN', ' ~ '.join(i['description'][:50] for i in u['items'])) for u in d.get('unconnected_items', [])[:6]]"
# ONE RUN, ONE DECISION. It ran twice, once to print and once to decide, which is the pattern stage 0
# removed from every board gate and left here (red team round three L2). On B that is two passes over the
# pruned list for one boolean, and worse, two runs can disagree.
# ASKED ON EVERY BOARD, not only where the prune stage runs (16 September 2026). Five boards carried RTE-002
# INCONCLUSIVE because this gate was never even called on them, and its answer for a board that prunes nothing
# is a PASS with the declaration as its reason. The guard stays on the STOP, which is the part that is about
# board B: a pruned pad the router never reached is a refusal, and there is no such pad where none was pruned.
python3 $T/pruned_gate.py $N.kicad_pcb out/$N-pruned.txt > out/pruned_gate.log 2>&1; PRC=$?
grep -E 'pruned_gate' out/pruned_gate.log | tail -6
# THE LIST TRAVELS WITH THE BOARD (16 September 2026). escape_prune writes it in the ROUTE tree, the board is
# committed without it, and every later reading of that board then has no way to ask whether a pruned pad was
# reached: RTE-002 read "no pruned_gate verdict for this board" on five boards for that reason alone. It is
# this morning's DRC-report lesson in a second place, an artefact that decides a rule belongs beside the board.
mkdir -p routed && cp out/$N-pruned.txt routed/$N-pruned.txt 2>/dev/null || true
# THE PLACEMENT'S EVIDENCE TRAVELS WITH THE BOARD TOO (16 September 2026, the same lesson a third time).
# PLC-001 asks whether the placement was legal BEFORE anything was routed, and that question can only be
# answered on the placed board: `full.sh` measures it (the placed-board DRC, `hardset --label placed`, and
# `place_audit`) and writes the verdicts in the ROUTE tree's out/, which nobody keeps. Three boards read
# "no hardset-placed verdict for this board" and a fourth read one from three days ago, all of them about
# boards whose placement WAS measured, in a directory that was thrown away with the tree. The two verdicts
# are 2 kB and they are the only record that the expensive stage ran on a legal board.
# AND THE CARRY IS PROVED, NOT ASSUMED (17 September 2026). Copying those three files moved a verdict about
# one board into a directory holding another, with nothing but the shared tree tying them together, which is
# the attribution defect of this week in its smallest form. A route lays copper and moves no part, and that
# is checkable: `carry_placed.py` compares every footprint's position, orientation and side between the
# placed snapshot and the board being cut, carries the three verdicts with both shas recorded when none
# moved, and refuses when one did, because then this board's placement was never measured.
if [ -s "out/$N-placed.kicad_pcb" ]; then
  # NON-FATAL BY CONSTRUCTION. This stage carries EVIDENCE and changes no copper, so it must never be able to
  # end a finish that a five-hour route paid for: its refusal is the honest answer (the placement was not
  # measured for this board) and the readiness computation already treats an absent verdict as inconclusive.
  # The pipeline runs under pipefail, so the status is taken and discarded deliberately rather than by luck.
  python3 $T/carry_placed.py "out/$N-placed.kicad_pcb" "$N.kicad_pcb" out routed 2>&1 | head -6 || true
else
  echo "carry_placed: no placed snapshot in this tree, so the placement's evidence is not carried (PLC-001 stays unmeasured for this board)"
fi
[ "$PRC" -ne 1 ] || stop "PRUNED PAD NOT REACHED by the router"

# every gate below runs ONCE and its exit code is its verdict; the reason comes from its verdict JSON
# RULE VIA-001: every via against the board's own minimum diameter and drill, and the vias in pads counted for
# the order paperwork. It runs on the routed board because that is when every via exists: the escapes, the
# fanout, the router's own, the stitching, the grid and whatever the closers added.
python3 $T/via_audit.py $N.kicad_pcb > out/via_audit.log 2>&1; VA=$?; grep -E 'via_audit:|FAIL|via in pad' out/via_audit.log | head -6
[ "$VA" -eq 1 ] && stop "a via is below the board's own minimum (rule VIA-001, out/via_audit.log)" out/via_audit.log
python3 $T/check_pcb_$L.py $N.kicad_pcb > out/gate-$N.log 2>&1; GATE=$?; grep -E "$GGREP" out/gate-$N.log | tail -14
[ "$GATE" -eq 0 ] || stop "GATE $(python3 $T/verdict.py read out/check_pcb_$L.verdict.json 2>&1 | tail -1) on the routed board" "out/gate-$N.log"
# THE INTENT RULES BLOCK THROUGH THEIR OWN VERDICTS (16 September 2026). The board gate used to count them in
# its own failure list, which blocked correctly and attributed wrongly: one composite verdict fails every rule
# it is mapped to, so board D's single open item, one signal via short of a ground via, failed the MECHANICAL
# rule on six boards. The gate reports them now and these five decide, so the finish stops in exactly the same
# places it did and the readiness names the rule that actually failed.
# RULE TRN-001 BLOCKS THE DELIVERABLE (16 September 2026). Every conductor that leaves the enclosure is
# followed from its connector to a clamp; the netlist is where that is decided, and this is the last gate
# before a board is cut. The pre-route chain reports it and does not stop for it, because a route cannot
# change it and owner decision 31 is open.
if [ -s out/$N.net ]; then
  python3 $T/port_protect.py out/$N.net > out/port_protect-finish.log 2>&1; PPF=$?
  grep -aE 'port_protect:|FAIL' out/port_protect-finish.log | head -6
  [ "$PPF" -eq 1 ] && stop "PORTS a conductor leaves the case and meets a chip with nothing between (rule TRN-001)" "out/port_protect-finish.log"
  # RULE SCH-004 BLOCKS THE DELIVERABLE FOR THE SAME REASON (17 September 2026): a line whose assertion inhibits
  # a hazard has to hold its safe state with this board's own copper, it is decided on the netlist, and a board
  # that reaches a deliverable without its pull-down would ship an inhibit that depends on a cable being there.
  # The pre-route chain runs it too, and a board cut by a re-finish never goes through that chain.
  python3 $T/safe_lines.py out/$N.net > out/safe_lines-finish.log 2>&1; SLF=$?
  grep -aE 'safe_lines:|FAIL' out/safe_lines-finish.log | head -6
  [ "$SLF" -eq 1 ] && stop "SAFETY a declared safety line does not hold its safe state on this board (rule SCH-004)" "out/safe_lines-finish.log"
fi
for _iv in intent_return_path intent_return_via intent_decoupling intent_rails intent_other; do
  [ -f "out/$_iv.verdict.json" ] || continue
  python3 $T/verdict.py read "out/$_iv.verdict.json" > out/intent-verdict.txt 2>&1 || \
    stop "INTENT $(tail -1 out/intent-verdict.txt)" "out/gate-$N.log"
done
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
CLEAN=$(cat "$FLAG" 2>/dev/null || echo missing); [ "$CLEAN" = clean ] || { echo "$PHASE NOT CLEAN, not finishing"; costs; echo "FINISH-$PHASE-DONE"; exit 1; }
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
costs
echo "FINISH-$PHASE-DONE"
