#!/usr/bin/env bash
# The registration's trial on the rented box (p3bind, MESHSAT-1357, 27 September 2026): apply_rule_and_coverage.py in a
# THROWAWAY clone at one commit, then what the integrator would do after it (validate, the re-take in place on every
# board, the render), how rules_status reads rule DOC-003 on each board, and the full suite in that state.
# Usage (on the box): trial.sh <commit> <bundle> <ref in bundle>      writes /root/p3bind/trial-<commit>.log
set -u
C=$1; BUN=$2; REF=$3
D=/root/p3bind/apply-$C; LOG=/root/p3bind/trial-$C.log
export PYTHONDONTWRITEBYTECODE=1
{
rm -rf $D && git clone -q /root/r8int6/repo $D && cd $D && git fetch -q "$BUN" "$REF:refs/heads/p3bind-trial-$C" \
  && git checkout -q $C && tar xf /root/r8int6/evidence-head.tar -C $D || { echo "CLONE FAILED"; exit 3; }
echo "== HEAD"; git log --oneline -1 | cut -c1-100
echo "== apply"; python3 v2/docs/records/p3bind/apply_rule_and_coverage.py; echo "exit $?"
echo "== apply, a second time"; python3 v2/docs/records/p3bind/apply_rule_and_coverage.py; echo "exit $?"
cd v2/ecad/tools
echo "== validate"; python3 rules_lib.py validate | tail -1
echo "== the re-take's plan"
python3 retake_schematic_phase.py --plan --verdict-dir /root/p3bind/vd-$C | grep "DOC-003\|constraints_bound\|^plan"
echo "== the re-take in place, every board"
python3 retake_schematic_phase.py --run --in-place --routed 2>&1 | grep "^board\|^retake_schematic_phase:" | cut -c1-400
echo "== render"; python3 rules_render.py 2>&1 | tail -1; python3 rules_render.py --check 2>&1 | tail -1
echo "== rule DOC-003 on every board, as rules_status reads it"
python3 - <<'PY'
import json, sys
sys.path.insert(0, ".")
import rules_status as S
for L in S.manifest()["boards"]:
    st = S.board_status(L)
    rows = st["rows"] if isinstance(st, dict) and "rows" in st else st
    for r in rows:
        if r.get("rule") == "DOC-003":
            print("%-3s %s %s %s | %s | %s" % (L, r.get("result"), r.get("evidence_class"), r.get("evidence_cause"),
                                                r.get("why"), r.get("evidence_why")))
PY
echo "== the pages and files that differ from the commit"; git -C $D status --short
echo "== the full suite in this state"
timeout 7200 python3 tests/run.py > /root/p3bind/trial-$C-suite.log 2>&1; echo "EXIT $?"
grep "^tests:" /root/p3bind/trial-$C-suite.log | grep -v "PASS$" | cut -c1-400
echo "== status after the suite"; git -C $D status --short
} > $LOG 2>&1
date -u +%FT%TZ > /root/p3bind/done-trial-$C
