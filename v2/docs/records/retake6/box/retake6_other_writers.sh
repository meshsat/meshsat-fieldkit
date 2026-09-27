#!/usr/bin/env bash
# retake6, step 4 (MESHSAT-1357): the two writers the driver does not run and whose tool or inputs set 6 changed.
#   reliability.py (REL-001), per board, with the arguments gate_sweep.sh gives it (`--ecad <ecad> --board <letter>`),
#     run in the board's phase directory with VERDICT_DIR=<phase>/out as the driver runs its writers, and the reading
#     copied to <phase>/routed/ as gate_sweep.sh and the driver's --routed copy theirs;
#   claims_check.py (ENV-002), from v2/ecad, so it writes v2/ecad/out (the set-level folder rules_status reads).
# Nothing else is run. A writer that fails to write is reported and the others still run.
set -u
D=/root/retake6; C=$D/rtk; E=$C/v2/ecad; T=$E/tools
export PYTHONDONTWRITEBYTECODE=1
L=$D/other-writers.log; : > $L
echo "HEAD $(git -C $C rev-parse HEAD)  start $(date -u +%FT%TZ)" >> $L
echo "tools dir dirty lines: $(git -C $C status --porcelain -- v2/ecad/tools | wc -l)" >> $L
python3 - "$T" > $D/phase-dirs.txt <<'PY'
import sys, os
sys.path.insert(0, sys.argv[1])
import rules_status as S
m = S.manifest()
for L in m["boards"]:
    print(L, os.path.relpath(S._phase_dir(L, m), os.path.dirname(sys.argv[1])))
PY
cat $D/phase-dirs.txt >> $L
while read LET PD; do
  P=$E/$PD
  echo "--- reliability board $LET in $PD" >> $L
  B=$(sha256sum $P/routed/reliability.verdict.json 2>/dev/null | cut -c1-16)
  ( cd $P && VERDICT_DIR=$P/out timeout 600 python3 $T/reliability.py --ecad "$E" --board $LET >> $L 2>&1; echo "exit $?" >> $L )
  if [ -s $P/out/reliability.verdict.json ] && [ $P/out/reliability.verdict.json -nt $D/phase-dirs.txt ]; then
    cp $P/out/reliability.verdict.json $P/routed/reliability.verdict.json
    echo "copied to $PD/routed/ (was $B, is $(sha256sum $P/routed/reliability.verdict.json | cut -c1-16))" >> $L
  else
    echo "NO READING WRITTEN for board $LET: nothing copied" >> $L
  fi
done < $D/phase-dirs.txt
echo "--- claims_check from v2/ecad" >> $L
( cd $E && timeout 600 python3 tools/claims_check.py >> $L 2>&1; echo "exit $?" >> $L )
ls -la --time-style=full-iso $E/out/claims_check.verdict.json >> $L
echo "end $(date -u +%FT%TZ)" >> $L
git -C $C status --short > $D/other-writers-status-after.txt
date -u +%FT%TZ > $D/done-other
