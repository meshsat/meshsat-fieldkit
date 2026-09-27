#!/usr/bin/env bash
# H2 exports and regeneration on the KiCad box, only under /root/h2 (MESHSAT-1357)
set -u
H=/root/h2
C=763bccdf25026cb8b3f28f7a57b68ae7ac784d5d
mkdir -p $H && cd $H
[ -d repo ] || git clone -q /root/chk-w4c/main repo
git -C repo fetch -q $H/h2.bundle "fnd/h2:refs/heads/fnd-h2"
git -C repo cat-file -t $C
rm -rf src rg && mkdir -p src rg
git -C repo archive --format=tar $C | tar xf - -C src
git -C repo archive --format=tar $C | tar xf - -C rg
export PYTHONDONTWRITEBYTECODE=1
cd $H/src && date -u +%FT%TZ > $H/exports.start
python3 v2/ecad/tools/handover_exports.py exports --out $H/ex-out --commit $C --letters a,b,d,e > $H/exports.log 2>&1; echo "exports exit $?" >> $H/exports.log
cd $H/rg && python3 v2/ecad/tools/handover_exports.py regen --out $H/rg-out --letters a,b,c,d,e,p > $H/regen.log 2>&1; echo "regen exit $?" >> $H/regen.log
date -u +%FT%TZ > $H/done
