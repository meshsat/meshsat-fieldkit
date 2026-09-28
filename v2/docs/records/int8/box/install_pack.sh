#!/usr/bin/env bash
# Bring a box re-take's pack back and install it in a worktree (tracked readings by patch, ignored readings by tar),
# then report (generalised from v2/docs/records/int7/box/int7_install_pack.sh). Run on the runner.
# Usage: install_pack.sh <worktree> <box dir name> <expected short sha of the worktree's HEAD> <local scratch dir>
set -eu
W=$1; N=$2; SHA=$3; SP=$4; BIN=$(dirname "$(readlink -f "$0")")
L=$SP/pack; rm -rf $L; mkdir -p $SP
$BIN/bxs.sh "tar cf /root/$N/pack.tar -C /root/$N pack" && $BIN/bxcp.sh from /root/$N/pack.tar $SP/ && tar xf $SP/pack.tar -C $SP/
test -d $L || { echo "pack not fetched"; exit 2; }
( env -C $L sha256sum -c SHA256SUMS )
test "$(git -C $W rev-parse --short=8 HEAD)" = "$SHA" || { echo "$W is not at $SHA"; exit 3; }
# the rendered pages are discarded first (they are re-rendered after the install)
git -C $W checkout -- v2/docs/CURRENT-EVIDENCE.md v2/docs/PCB-OPEN-PAIRS.md v2/docs/PCB-RULE-STATUS-*.md v2/docs/REQUIREMENTS-TRACE.md
echo "status before install: $(git -C $W status --short | wc -l) line(s)"
git -C $W apply --check $L/tracked.patch && git -C $W apply $L/tracked.patch
echo "tracked files changed by the patch: $(git -C $W diff --name-only | wc -l) (list: $(wc -l < $L/tracked-changed.lst))"
git -C $W diff --name-only | grep -v -E 'routed/.*\.verdict\.json$' | sed 's/^/  NOT A READING: /' || true
tar tf $L/ignored-readings.tar > $L/tar.lst
test "$(git -C $W ls-files -- $(cat $L/tar.lst) | wc -l)" = 0 || { echo "the tar holds tracked files"; exit 4; }
tar xf $L/ignored-readings.tar -C $W
echo "ignored readings installed: $(wc -l < $L/tar.lst)"
git -C $W status --short | grep -v '^ M v2/ecad/.*routed/' | head -5 || true
echo "install done $(date +%T)"
