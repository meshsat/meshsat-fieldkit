#!/bin/bash
# r8int6: the evidence phase on the committed integration: main's gitignored evidence copied in by main's ignored-file
# list (never over a tracked file), claims_check re-taken from v2/ecad as a named deliberate re-take, rules_status three
# times, rules_render twice, then the audit's difference against main's. Logs in $R/logs.
set -e
SP=$SP
R=$SP/r8int6; W=$SP/wt/r8int6; L=$R/logs; mkdir -p $L
cd $W
if [ -n "$(git status --porcelain)" ]; then echo "evidence_r8int6: the tree is not clean"; git status --short | head; exit 1; fi
echo "HEAD $(git rev-parse HEAD)" > $L/evidence-head.txt
$R/copy_evidence.sh | tee $L/copy-evidence.log
( cd v2/ecad && python3 tools/claims_check.py > $L/claims_check-retake.log 2>&1; echo "claims_check exit $?" >> $L/claims_check-retake.log )
tail -3 $L/claims_check-retake.log
cd $W/v2/ecad/tools
for i in 1 2 3; do python3 rules_status.py > $L/status-$i.log 2>&1 || true; echo "status $i: $(grep -c '' $L/status-$i.log) lines"; done
for i in 1 2; do python3 rules_render.py > $L/render-$i.log 2>&1 || true; grep -v "^rules_render: wrote" $L/render-$i.log | tail -3; done
python3 $R/common/audit_diff_r8int6.py $R/audit-main $W/v2/ecad/out/rule-audit > $L/audit-diff.txt
tail -1 $L/audit-diff.txt
