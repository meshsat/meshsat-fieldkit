#!/usr/bin/env bash
# One board's pre-route chain on an ISOLATED copy of the tools, so a measurement is not disturbed by whatever else
# is running against the box clone (12 September 2026, MESHSAT-862).
#
# Two defects made this necessary in one night. A `git checkout origin/main -- v2/ecad/tools` while another chain
# was mid-run gave that chain a mixed tree, and the GitHub mirror this box pulls from lags GitLab by up to five
# minutes per sync, so every one-line fix cost a mirror round trip before it could be measured. The runner pushes
# the tools straight here instead:
#
#   rsync -a --delete --exclude __pycache__ --exclude 'out/' --exclude '*.pyc' \
#         v2/ecad/tools v2/ecad/meshsat.pretty root@<box>:/root/isotools/
#   ssh <box> 'bash /root/iso_chain.sh a pcb-a-power-a23 full_a22.sh'
#
# The commit still happens in git, because the record is the repository; this is the measuring instrument, not
# the source of truth. $1 = a tag for the run, $2 = the phase directory, $3 = the chain script.
set -uo pipefail
TAG="$1"; P0="$2"; CH="$3"; R=/root/gitlab/products/meshsat/meshsat-fieldkit; T=/root/local-$TAG/ecad
[ -d /root/isotools/tools ] || { echo "ISO-CHAIN-DONE $TAG NO-TOOLS (rsync them first)"; exit 1; }
rm -rf /root/local-$TAG; mkdir -p $T
cp -a /root/isotools/tools $T/tools
cp -a /root/isotools/meshsat.pretty $T/meshsat.pretty
rsync -a --exclude out/ $R/v2/ecad/$P0/ $T/$P0/
cd $T/$P0 || exit 1
timeout 7200 bash ../tools/$CH "$PWD" > /root/local_$TAG.pre.log 2>&1
echo "chain exit $? | $TAG | $(grep -a 'pairs laid,' /root/local_$TAG.pre.log | tail -1 | cut -c1-120)"
grep -a -E "^pair_preroute: (LAID|FAIL|NEAR|DIVE|TRIM|TWIST|UNMERGE|ENTRY|STUBS) |^pair_preroute:       " /root/local_$TAG.pre.log | sed 's/pair_preroute: //' | cut -c1-170
grep -a -E "PREROUTE-DONE" /root/local_$TAG.pre.log | tail -1
echo "ISO-CHAIN-DONE $TAG"
