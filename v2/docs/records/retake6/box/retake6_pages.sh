#!/usr/bin/env bash
# retake6, step 5 (MESHSAT-1357): rules_status three times, rules_render, decisions_render, then the checks.
# Usage: retake6_pages.sh <label>   logs go to /root/retake6/pages-<label>/
set -u
D=/root/retake6; C=$D/rtk; E=$C/v2/ecad; LAB=${1:?label}; O=$D/pages-$LAB; mkdir -p $O
export PYTHONDONTWRITEBYTECODE=1
cd $E || exit 2
echo "HEAD $(git -C $C rev-parse HEAD)  start $(date -u +%FT%TZ)" > $O/run.txt
for i in 1 2 3; do
  s=$(date +%s); python3 tools/rules_status.py > $O/status-$i.log 2>&1; rc=$?
  echo "status-$i exit $rc in $(( $(date +%s) - s )) s: $(tail -n 1 $O/status-$i.log)" >> $O/run.txt
  sha256sum out/rule-audit/*.json out/rules_status.verdict.json out/rules_complete.verdict.json 2>/dev/null > $O/audit-sha-$i.txt
done
s=$(date +%s); python3 tools/rules_render.py > $O/render-1.log 2>&1; echo "render-1 exit $? in $(( $(date +%s) - s )) s" >> $O/run.txt
s=$(date +%s); python3 tools/decisions_render.py > $O/decisions-render.log 2>&1; echo "decisions_render exit $? in $(( $(date +%s) - s )) s" >> $O/run.txt
git -C $C status --short > $O/status-after-render-1.txt
s=$(date +%s); python3 tools/rules_render.py > $O/render-2.log 2>&1; echo "render-2 exit $? in $(( $(date +%s) - s )) s" >> $O/run.txt
git -C $C status --short > $O/status-after-render-2.txt
( cd $C && git diff --stat > $O/diffstat-after-render-2.txt )
python3 tools/rules_render.py --check > $O/check.log 2>&1; echo "rules_render --check exit $?: $(tail -n 1 $O/check.log)" >> $O/run.txt
python3 tools/rules_render.py --requirements --check > $O/check-req.log 2>&1; echo "rules_render --requirements --check exit $?: $(tail -n 1 $O/check-req.log)" >> $O/run.txt
python3 tools/decisions_render.py --check > $O/check-dec.log 2>&1; echo "decisions_render --check exit $?: $(tail -n 1 $O/check-dec.log)" >> $O/run.txt
( cd tools && python3 rules_lib.py > $O/rules_lib.log 2>&1; echo "rules_lib exit $?: $(tail -n 1 $O/rules_lib.log)" >> $O/run.txt
  python3 rules_lib.py requirements > $O/rules_lib-req.log 2>&1; echo "rules_lib requirements exit $?: $(tail -n 1 $O/rules_lib-req.log)" >> $O/run.txt )
sed -n 6p ../docs/CURRENT-EVIDENCE.md >> $O/run.txt
sha256sum ../docs/CURRENT-EVIDENCE.md >> $O/run.txt
echo "end $(date -u +%FT%TZ)" >> $O/run.txt
date -u +%FT%TZ > $D/done-pages-$LAB
