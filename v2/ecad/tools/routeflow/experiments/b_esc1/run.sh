#!/usr/bin/env bash
# Q-B-ESC-1, the bounded escape trial of board B (v2/docs/B-FEASIBILITY.md section 7). EXPERIMENTAL: its outputs
# are labelled so in the journal, the run directory and every report; nothing here is a layout, a phase or a
# candidate, and nothing here authorises layout (the owner's condition 7 of 25 September 2026).
#
# Question: in slot 3 (U301, U302, U309, U310, U32A/U32B, J_M2N3, J_M2C3), is the failure to break out a layer
# capacity limit that two more routing layers remove, or a geometric limit that layer count does not change?
#
# Usage, from v2/ecad of a CLEAN clone at the commit to be recorded, on a rented KiCad 9 box:
#   BOX_USD_PER_H=<the box's rate> bash tools/routeflow/experiments/b_esc1/run.sh
# Env: T (trial dir, default out/routeflow/b-esc1, gitignored), PREPARE_ONLY=1 (stop before any router starts),
#      PASSES (20), JOB_TIMEOUT (9000 s), FIRST_PASS_MAX (5400 s), PLATEAU (3), BUDGET_H (6), BUDGET_USD (10),
#      FINAL_RESERVE_S (2700: wall time kept back for the final imports and DRC).
#
# The caps are enforced here, not described: route_part.sh's own timeout (JOB_TIMEOUT) and pass ceiling (PASSES);
# plateau_watch.py's plateau, first-pass and deadline kills; the deadline is the smaller of BUDGET_H hours and
# BUDGET_USD / BOX_USD_PER_H hours from this script's start, less FINAL_RESERVE_S. A missing rate refuses to start.
# Nothing is extended when a cap fires and no electrical rule is relaxed. Destroying the box is the operator's act
# after the files listed at the end are fetched and verified one by one.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ -d tools ] && [ -d pcb-b-compute-b19 ] || { echo "run from v2/ecad"; exit 2; }
T="${T:-out/routeflow/b-esc1}"; PASSES="${PASSES:-20}"; JOB_TIMEOUT="${JOB_TIMEOUT:-9000}"
FIRST_PASS_MAX="${FIRST_PASS_MAX:-5400}"; PLATEAU="${PLATEAU:-3}"; BUDGET_H="${BUDGET_H:-6}"; BUDGET_USD="${BUDGET_USD:-10}"
FINAL_RESERVE_S="${FINAL_RESERVE_S:-2700}"
INPUT=pcb-b-compute-b19/routed/pcb-b-compute-preroute.kicad_pcb
INPUT_SHA=62facf0952ff4c01cb0a47698ec6870b5fae0f0d9b836bf95db6c3c7bae166dd
N=pcb-b-compute
declare -A LAYERS=( [a6]="F.Cu In2.Cu In3.Cu B.Cu" [a8]="F.Cu In2.Cu In3.Cu In5.Cu In6.Cu B.Cu" )
say () { echo "$*" | tee -a "$T/JOURNAL.md"; }
stop () { say "STOP: $*"; exit 1; }

if [ "${PREPARE_ONLY:-0}" != 1 ]; then
  [ -n "${BOX_USD_PER_H:-}" ] || { echo "BOX_USD_PER_H is required: the credit cap cannot be enforced without the rate"; exit 2; }
fi
[ -z "$(git status --porcelain --untracked-files=no)" ] || { echo "the clone has tracked changes; the trial records a commit, so it runs on a clean one"; exit 2; }
[ ! -e "$T" ] || { echo "$T exists: a trial directory is never reused"; exit 2; }
for c in java xvfb-run kicad-cli python3; do command -v "$c" >/dev/null || { echo "missing $c"; exit 2; }; done
mkdir -p "$T/a6" "$T/a8"
START=$(date +%s)
CAP_S=$(python3 -c "import sys; h=float(sys.argv[1]); r=sys.argv[2]; u=float(sys.argv[3]); print(int(3600*min(h, u/float(r)) if r else 3600*h))" "$BUDGET_H" "${BOX_USD_PER_H:-}" "$BUDGET_USD")
ROUTE_DEADLINE=$((START + CAP_S - FINAL_RESERVE_S))
. tools/fr_jar.sh
JAR="$(fr_jar b_esc1)" || exit 2

# 0. provenance
{
  echo "# Q-B-ESC-1 journal (EXPERIMENTAL)"
  echo
  echo "Board B escape trial, v2/docs/B-FEASIBILITY.md section 7. EXPERIMENTAL: never a phase, a promotion or a layout candidate."
  echo
  echo "- start: $(date -u -Iseconds -d @$START)"
  echo "- commit: $(git rev-parse HEAD); tools tree: $(git rev-parse HEAD:v2/ecad/tools)"
  # the trial's own scripts by content, and whether the driver is tracked at that commit (integration, 26 Sep 2026:
  # the 25 Sep smoke run named a commit that did not contain these scripts, and nothing tied the two together)
  echo "- trial scripts sha256/16: $(cd "$HERE" && for f in *.sh *.py; do printf '%s %s; ' "$f" "$(sha256sum "$f" | cut -c1-16)"; done)"
  echo "- run.sh tracked at this commit: $(git ls-files --error-unmatch "$HERE/run.sh" >/dev/null 2>&1 && echo yes || echo NO)"
  echo "- jar: $(basename "$JAR") sha256/16 $(sha256sum "$JAR" | cut -c1-16); java: $(java -version 2>&1 | head -1)"
  echo "- kicad-cli: $(kicad-cli version 2>/dev/null | head -1); host: $(hostname); cores: $(nproc)"
  echo "- caps: passes $PASSES, job timeout $JOB_TIMEOUT s, first pass $FIRST_PASS_MAX s, plateau $PLATEAU, budget $BUDGET_H h / $BUDGET_USD USD at ${BOX_USD_PER_H:-unset} USD/h, cap $CAP_S s, route deadline $(date -u -Iseconds -d @$ROUTE_DEADLINE)"
  echo "- one job per arm: the router is deterministic (tests/test_driver_hygiene.py), so a repeat is the same number twice"
  echo
} > "$T/JOURNAL.md"

# 1. inputs, from the commit itself (the pre-route board is tracked, commit 8c691891)
git show "HEAD:v2/ecad/$INPUT" > "$T/a6/$N.kicad_pcb"
[ "$(sha256sum "$T/a6/$N.kicad_pcb" | cut -d' ' -f1)" = "$INPUT_SHA" ] || stop "input board sha differs from $INPUT_SHA"
for A in a6 a8; do cp pcb-b-compute-b19/$N.kicad_pro pcb-b-compute-b19/fp-lib-table "$T/$A/"; done
ln -sfn "$(pwd)/meshsat.pretty" "$T/meshsat.pretty"   # fp-lib-table names \${KIPRJMOD}/../meshsat.pretty
say "- input: $INPUT sha256 $INPUT_SHA; project file sha256 $(sha256sum pcb-b-compute-b19/$N.kicad_pro | cut -c1-16)"

# 2. the eight-layer arm, proved to differ in layer count only (read back from the saved file)
python3 "$HERE/make_arm8.py" "$T/a6/$N.kicad_pcb" "$T/a8/$N.kicad_pcb" "$T/arm8.json" 2>&1 | grep -v -E "Debug|leak" | tee -a "$T/JOURNAL.md"
[ "${PIPESTATUS[0]}" = 0 ] || stop "STOP-ARMS-DIFFER (make_arm8)"

# 3. the escape field must be identical in both arms: place_audit, with board B's own ESCAPE_SKIP
SKIP=$(python3 -c "import json; print(json.load(open('tools/boards/b.json'))['escape_env']['ESCAPE_SKIP'])") || stop "cannot read board B's ESCAPE_SKIP (tools/boards/b.json escape_env)"
say "- ESCAPE_SKIP (tools/boards/b.json escape_env): $SKIP"
for A in a6 a8; do
  ESCAPE_SKIP="$SKIP" VERDICT_DIR="$T/$A/pa" python3 tools/place_audit.py "$T/$A/$N.kicad_pcb" > "$T/$A/place_audit.txt" 2>&1
done
# 4. DSN and partition, board B's routeflow settings (plane net GND, power layers In1.Cu In4.Cu, default regions)
for A in a6 a8; do
  bash tools/dsn_export.sh "$T/$A/$N.kicad_pcb" "$T/$A/raw.dsn" "GND" "In1.Cu In4.Cu" > "$T/$A/dsn.log" 2>&1
  python3 tools/dsn_partition.py "$T/$A/$N.kicad_pcb" "$T/$A/raw.dsn" "$T/$A/part.dsn" "$T/$A/part.json" > "$T/$A/part.log" 2>&1
  [ -s "$T/$A/part.dsn" ] && [ -s "$T/$A/part.json" ] || stop "$A: no partitioned DSN (see $T/$A/dsn.log, part.log)"
done
python3 - "$T" <<'PY'
import json, sys, os
t = sys.argv[1]; diffs = []
pa = {a: json.load(open(os.path.join(t, a, "pa", "place_audit.verdict.json"))) for a in ("a6", "a8")}
for k in ("verdict", "counts", "evidence"):
    if pa["a6"].get(k) != pa["a8"].get(k): diffs.append("place_audit %s differs" % k)
pj = {a: json.load(open(os.path.join(t, a, "part.json"))) for a in ("a6", "a8")}
if pj["a6"]["groups"] != pj["a8"]["groups"]: diffs.append("partition groups differ")
m8 = json.load(open(os.path.join(t, "arm8.json")))
if not m8.get("agree"): diffs.append("make_arm8 disagreement")
out = {"label": "EXPERIMENTAL (Q-B-ESC-1)", "agree": not diffs, "differences": diffs,
       "place_audit_counts": pa["a6"].get("counts"), "s3_nets": len(pj["a6"]["groups"].get("S3", [])),
       "groups": {g: len(n) for g, n in pj["a6"]["groups"].items()}}
json.dump(out, open(os.path.join(t, "integrity.json"), "w"), indent=1)
print("integrity:", "arms agree" if not diffs else "STOP-ARMS-DIFFER " + "; ".join(diffs), out["groups"])
PY
python3 -c "import json,sys; sys.exit(0 if json.load(open('$T/integrity.json'))['agree'] else 1)" || stop "STOP-ARMS-DIFFER (integrity.json)"
say "- integrity: $(python3 -c "import json; d=json.load(open('$T/integrity.json')); print('groups', d['groups'], 'place_audit', d['place_audit_counts'])")"

# 5. the pass-0 reading of the decisive number on each arm's input
for A in a6 a8; do
  python3 "$HERE/count_open.py" "$T/$A/$N.kicad_pcb" "$T/$A/part.json" S3 --json "$T/$A/base.json" 2>&1 | grep -v -E "Debug|leak" | sed "s/^/- $A pass 0: /" | tee -a "$T/JOURNAL.md"
done
if [ "${PREPARE_ONLY:-0}" = 1 ]; then say "PREPARE_ONLY: stopped before any router started"; exit 0; fi

# 6. one S3 job per arm, confined to the S3 region on the arm's routing layers, each under its own watcher
declare -A JOB WAT
for A in a6 a8; do
  CONFINE=1 CONFINE_LAYERS="${LAYERS[$A]}" bash tools/route_part.sh "$T/$A/run" "$T/$A/part.dsn" S3 "$PASSES" "$JOB_TIMEOUT" "$T/$A/part.json" > "$T/$A/route.log" 2>&1 &
  JOB[$A]=$!
  python3 "$HERE/plateau_watch.py" --job-pid "${JOB[$A]}" --ses "$T/$A/run/S3/route.ses" --out "$T/$A/watch" \
    --count-cmd "python3 $HERE/count_open.py $T/$A/$N.kicad_pcb $T/$A/part.json S3 --ses {ses}" \
    --plateau "$PLATEAU" --first-pass-max "$FIRST_PASS_MAX" --deadline "$ROUTE_DEADLINE" --stop-file "$T/STOP" > "$T/$A/watch.log" 2>&1 &
  WAT[$A]=$!
  say "- $A: route_part pid ${JOB[$A]} on ${LAYERS[$A]}, watcher pid ${WAT[$A]}, start $(date -u -Iseconds)"
done
# A6 that cannot finish one pass inside FIRST_PASS_MAX means the tool cannot answer at this cap: stop the other arm too
while kill -0 "${WAT[a6]}" 2>/dev/null || kill -0 "${WAT[a8]}" 2>/dev/null; do
  if [ -f "$T/a6/watch/watch.json" ] && grep -q '"stop": "FIRST_PASS_TIMEOUT"' "$T/a6/watch/watch.json"; then touch "$T/STOP"; fi
  sleep 30
done
wait "${JOB[a6]}" "${JOB[a8]}" 2>/dev/null
for A in a6 a8; do say "- $A: $(tail -1 "$T/$A/watch.log")"; done

# 7. the final reading of each arm: import the last observed session with S3 locked, DRC, hard set, decisive count
for A in a6 a8; do
  LAST=$(ls "$T/$A/watch"/pass-*.ses 2>/dev/null | tail -1)
  [ -n "$LAST" ] || { say "- $A: no session to import"; continue; }
  python3 tools/ses_import_lock.py "$T/$A/$N.kicad_pcb" "$LAST" "$T/$A/part.json" S3 "$T/$A/s3.kicad_pcb" > "$T/$A/import.log" 2>&1 || { say "- $A: import failed (import.log)"; continue; }
  cp "$T/$A/$N.kicad_pro" "$T/$A/s3.kicad_pro"
  VERDICT_DIR="$T/$A/v" bash tools/drc.sh "$T/$A/s3.kicad_pcb" "$T/$A/s3-drc.json" > "$T/$A/drc.log" 2>&1 || { say "- $A: DRC failed as a tool (drc.log)"; continue; }
  VERDICT_DIR="$T/$A/v" python3 tools/hardset.py measure "$T/$A/s3-drc.json" post --label "b-esc1 $A EXPERIMENTAL" --board "$T/$A/s3.kicad_pcb" --counts "$T/$A/s3-counts.txt" > "$T/$A/hardset.log" 2>&1
  python3 "$HERE/count_open.py" "$T/$A/s3.kicad_pcb" "$T/$A/part.json" S3 --json "$T/$A/final.json" 2>&1 | grep -v -E "Debug|leak" | sed "s/^/- $A final: /" | tee -a "$T/JOURNAL.md"
  say "- $A hard set: $(cat "$T/$A/s3-counts.txt" 2>/dev/null) (H U, board-wide U includes every group the trial did not route)"
done

# 8. the outcome, by the table of the page, and the files to fetch
python3 "$HERE/judge.py" "$T" | tee -a "$T/JOURNAL.md"
say "- end: $(date -u -Iseconds); wall $(( $(date +%s) - START )) s"
say "- fetch, file by file, then destroy the box and read the instance list: JOURNAL.md integrity.json arm8.json outcome.json and, per arm, base.json final.json s3-counts.txt s3-drc.json place_audit.txt route.log watch.log watch/passes.csv watch/watch.json run/S3/fr.log"
exit 0
