#!/usr/bin/env bash
# retake6 (MESHSAT-1357): the full suite on the KiCad box at the re-take's own commit, as _bin/box_suite.sh runs it, with
# the evidence the pages were rendered from: the candidate's gitignored evidence and the re-take's ignored readings on top.
# Usage (on the box): retake6_suite.sh <commit> <bundle> <ref in bundle>
set -u
D=/root/retake6; C=$1; BUN=$2; REF=$3; S=$D/suite
git -C /root/r8int6/repo show-ref --verify -q refs/heads/retake6-suite-${C:0:8} || \
  git -C /root/r8int6/repo fetch -q "$BUN" "$REF:refs/heads/retake6-suite-${C:0:8}" || { echo "FETCH FAILED" > $D/suite-box.log; date -u +%FT%TZ > $D/done-suite; exit 3; }
rm -rf $S && git clone -q /root/r8int6/repo $S && git -C $S checkout -q $C || { echo "CHECKOUT FAILED" > $D/suite-box.log; date -u +%FT%TZ > $D/done-suite; exit 3; }
tar xf /root/r8int6/evidence-head.tar -C $S && tar xf $D/pack/ignored-readings.tar -C $S
export PYTHONDONTWRITEBYTECODE=1
# THE AUDIT IS CONVERGED FIRST (recipe item 6). The first run of this script did not: the clone held the candidate's
# audit from before the re-take (the tar of ignored readings leaves the audit's own outputs out), the suite's own
# render re-took it, and the suite's guard refused the run for changing rule-audit/rules_status.verdict.json
# (2015 passed, 1 failed, the guard; box/suite-attempt1/). rules_status three times and rules_render, as on main.
( cd $S/v2/ecad && for i in 1 2 3; do python3 tools/rules_status.py > $D/suite-converge-status-$i.log 2>&1; done
  python3 tools/rules_render.py > $D/suite-converge-render.log 2>&1; python3 tools/decisions_render.py >> $D/suite-converge-render.log 2>&1
  python3 tools/rules_render.py --check >> $D/suite-converge-render.log 2>&1 )
git -C $S status --short > $D/suite-box-status-before.txt
echo "start $(date -u +%FT%TZ)" > $D/suite-run.txt
( cd $S/v2/ecad/tools && timeout 7200 python3 tests/run.py > $D/suite-box.log 2>&1; echo "EXIT $?" >> $D/suite-box.log )
git -C $S rev-parse HEAD >> $D/suite-box.log
git -C $S status --short > $D/suite-box-status.txt
echo "end $(date -u +%FT%TZ)" >> $D/suite-run.txt
date -u +%FT%TZ > $D/done-suite
