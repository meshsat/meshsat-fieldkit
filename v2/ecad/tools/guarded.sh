#!/usr/bin/env bash
# guarded <label> <command...>  (source this file; needs N, T and a project cwd with out/)
#
# ONE keep-or-revert guard for every copper-editing pass after the router (15 September 2026, red team round four H2).
# There were five hand-rolled copies of snapshot, run, DRC, compare, restore, with three different comparison rules,
# and the difference between two of those rules was the A25 phase (the stub stage went in at 13 opens and out at 80
# while the first guard, which compared hard alone, passed it). The rule here is the one every copy should have had:
# compare hard AND unrouted against the board the pass was HANDED, never against zero, and restore on either rising.
# One verdict JSON per guarded pass carries both counts, the seconds and whether the board was kept.
#
#   GUARD_MODE   pre or post (hardset's verb: a pre-route board is not judged on its opens); default post
#   GUARD_QUIET  1 to keep the command's own output out of the log (it always goes to out/guard-<label>.log)
guarded () {
  local LBL="$1"; shift
  local MODE="${GUARD_MODE:-post}" T0=$SECONDS BH BU AH AU KEPT
  cp "$N.kicad_pcb" "out/$N-guard-$LBL.kicad_pcb"
  "$T/drc.sh" "$N.kicad_pcb" "out/$N-drc.json" >/dev/null 2>&1
  python3 "$T/hardset.py" "out/$N-drc.json" "$MODE" --counts "out/guard-$LBL-before.txt" --label "before $LBL" >/dev/null 2>&1 || true
  read BH BU < "out/guard-$LBL-before.txt" 2>/dev/null || { BH=999; BU=999; }
  # the command runs in THIS shell (no pipe): a `stop` inside it ends the finish the way it always did, and the
  # guard's own status is its exit status; the output is teed to out/guard-<label>.log through a process substitution
  local RC
  if [ "${GUARD_QUIET:-0}" = 1 ]; then "$@" > "out/guard-$LBL.log" 2>&1; RC=$?
  else "$@" > >(tee "out/guard-$LBL.log") 2>&1; RC=$?; wait 2>/dev/null; fi
  "$T/drc.sh" "$N.kicad_pcb" "out/$N-drc.json" >/dev/null 2>&1
  python3 "$T/hardset.py" "out/$N-drc.json" "$MODE" --counts "out/guard-$LBL-after.txt" --label "after $LBL" >/dev/null 2>&1 || true
  read AH AU < "out/guard-$LBL-after.txt" 2>/dev/null || { AH=999; AU=999; }
  if [ "$AH" -gt "$BH" ] || [ "$AU" -gt "$BU" ]; then
    KEPT=0; echo "$LBL HURT (hard $BH -> $AH, unrouted $BU -> $AU): the board is restored as it was handed in"
    cp "out/$N-guard-$LBL.kicad_pcb" "$N.kicad_pcb"; "$T/drc.sh" "$N.kicad_pcb" "out/$N-drc.json" >/dev/null 2>&1
  else
    KEPT=1; echo "$LBL kept (hard $BH -> $AH, unrouted $BU -> $AU, exit $RC, $((SECONDS - T0)) s)"
  fi
  python3 - "$LBL" "$BH" "$BU" "$AH" "$AU" "$KEPT" "$RC" "$((SECONDS - T0))" "$T" <<'PY' >/dev/null 2>&1 || true
import sys, os
sys.path.insert(0, sys.argv[9]); import verdict
l, bh, bu, ah, au, kept, rc, secs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8])
verdict.write("guard-" + l, verdict.PASS if kept else verdict.FAIL,
              counts={"hard_before": bh, "unrouted_before": bu, "hard_after": ah, "unrouted_after": au, "kept": kept, "exit": rc, "seconds": secs},
              denominator=1, evidence=[] if kept else ["restored: hard %d -> %d, unrouted %d -> %d" % (bh, ah, bu, au)],
              note="kept only if neither count rose against the board it was handed", out_dir="out")
PY
  return $((1 - KEPT))
}
