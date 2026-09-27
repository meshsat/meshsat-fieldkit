#!/usr/bin/env bash
# r8int6 on the KiCad box, only under /root/r8int6: the full suite at the integration head, in a clone of the box's
# /root/r8int6/repo (itself a read-only clone of /root/gitlab) with the head fetched from the bundle and the worktree's
# gitignored evidence unpacked. Usage: r8int6_suite.sh <commit> <bundle> <evidence tar>
set -u
H=/root/r8int6; C=$1; BUN=$2; TAR=$3
cd $H
git -C repo fetch -q "$BUN" "fnd/r8int6:refs/heads/r8int6-suite"
rm -rf suite && git clone -q repo suite && git -C suite checkout -q $C
tar xf "$TAR" -C suite
export PYTHONDONTWRITEBYTECODE=1
cd suite/v2/ecad/tools && timeout 7200 python3 tests/run.py > $H/suite-box.log 2>&1; echo "EXIT $?" >> $H/suite-box.log
git -C $H/suite status --short > $H/suite-box-status.txt
date -u +%FT%TZ > $H/done-suite-$C
