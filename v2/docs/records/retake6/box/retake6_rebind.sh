#!/usr/bin/env bash
# retake6, step 5 continued (MESHSAT-1357): rebind CON-010 and REQ-044 to the re-rendered CURRENT-EVIDENCE.md, render
# again, run the checks, and ask claims_check what it reads on the final documents WITHOUT writing in the tree.
set -u
D=/root/retake6; C=$D/rtk; E=$C/v2/ecad; O=$D/rebind; mkdir -p $O
export PYTHONDONTWRITEBYTECODE=1
cd $C || exit 2
echo "HEAD $(git rev-parse HEAD)  start $(date -u +%FT%TZ)" > $O/run.txt
sha256sum v2/docs/CURRENT-EVIDENCE.md v2/docs/REQUIREMENTS-TRACE.md v2/ecad/tools/pcb_requirements.yaml > $O/sha-before.txt
python3 $D/apply_rebind_current_evidence.py > $O/rebind.log 2>&1; echo "rebind exit $?" >> $O/run.txt
python3 $D/apply_rebind_current_evidence.py > $O/rebind-second.log 2>&1; echo "rebind second run exit $? (1 expected: refused)" >> $O/run.txt
cd $E
for i in 1 2; do
  python3 tools/rules_render.py > $O/render-$i.log 2>&1; echo "render-$i exit $?: $(grep -c 'wrote' $O/render-$i.log) page(s) written" >> $O/run.txt
  python3 tools/decisions_render.py > $O/decisions-render-$i.log 2>&1; echo "decisions_render-$i exit $?" >> $O/run.txt
done
python3 tools/rules_render.py --check > $O/check.log 2>&1; echo "rules_render --check exit $?: $(tail -n 1 $O/check.log)" >> $O/run.txt
python3 tools/rules_render.py --requirements --check > $O/check-req.log 2>&1; echo "rules_render --requirements --check exit $?: $(tail -n 1 $O/check-req.log)" >> $O/run.txt
python3 tools/decisions_render.py --check > $O/check-dec.log 2>&1; echo "decisions_render --check exit $?" >> $O/run.txt
( cd tools && python3 rules_lib.py > $O/rules_lib.log 2>&1; echo "rules_lib exit $?: $(tail -n 1 $O/rules_lib.log)" >> $O/run.txt
  python3 rules_lib.py requirements > $O/rules_lib-req.log 2>&1; echo "rules_lib requirements exit $?: $(tail -n 1 $O/rules_lib-req.log)" >> $O/run.txt )
mkdir -p $O/claims-scratch
( VERDICT_DIR=$O/claims-scratch python3 tools/claims_check.py > $O/claims-final.log 2>&1; echo "claims_check (scratch verdict dir, final documents) exit $?: $(head -n 1 $O/claims-final.log)" >> $O/run.txt )
sha256sum ../docs/CURRENT-EVIDENCE.md ../docs/REQUIREMENTS-TRACE.md tools/pcb_requirements.yaml > $O/sha-after.txt
git -C $C status --short > $O/status-after.txt
echo "end $(date -u +%FT%TZ)" >> $O/run.txt
date -u +%FT%TZ > $D/done-rebind
