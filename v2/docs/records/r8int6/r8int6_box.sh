#!/usr/bin/env bash
# r8int6 on the KiCad box, only under /root/r8int6: clone /root/gitlab read-only, fetch the integration bundle, archive
# the head, regenerate boards A, B, C, D, E and P with main's chain (handover_exports.py regen) and compare with the
# committed files. Usage: r8int6_box.sh regen <commit> <bundle>
set -u
H=/root/r8int6; mode=$1; C=$2; BUN=$3
cd $H
[ -d repo ] || git clone -q /root/gitlab/products/meshsat/meshsat-fieldkit repo
git -C repo fetch -q "$BUN" "fnd/r8int6:refs/heads/r8int6-$(basename $BUN .bundle)"
git -C repo cat-file -t $C
export PYTHONDONTWRITEBYTECODE=1
if [ "$mode" = regen ]; then
  rm -rf rg-$C rg-out-$C && mkdir -p rg-$C
  git -C repo archive --format=tar $C | tar xf - -C rg-$C
  cd rg-$C && python3 v2/ecad/tools/handover_exports.py regen --out $H/rg-out-$C --letters a,b,c,d,e,p > $H/regen-$C.log 2>&1
  echo "regen exit $?" >> $H/regen-$C.log
fi
date -u +%FT%TZ > $H/done-$mode-$C
