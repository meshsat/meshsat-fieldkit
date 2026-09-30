#!/usr/bin/env bash
# int7: bring the box re-take's pack back and install it in the int7 worktree (tracked readings by patch, ignored
# readings by tar), then report. Run on the runner. Usage: int7_install_pack.sh
set -eu
W=${WORKTREES:-$HOME/worktrees/meshsat-fieldkit}/int7
SP=${SCRATCH:-${TMPDIR:-/tmp}/int7-install}/box
L=$SP/pack; rm -rf $L; mkdir -p $L
B=${BOX_BIN:-${WORKTREES:-$HOME/worktrees/meshsat-fieldkit}/_bin}; $B/bxs.sh "tar cf /root/int7/pack.tar -C /root/int7 pack" && $B/bxcp.sh from /root/int7/pack.tar $SP/ && tar xf $SP/pack.tar -C $SP/
test -d $L || { echo "pack not fetched"; exit 2; }
( env -C $L sha256sum -c SHA256SUMS )
test "$(git -C $W rev-parse --short HEAD)" = "a4b157f0" || { echo "int7 is not at a4b157f0"; exit 3; }
# the rendered pages of the first pass are discarded first (they are re-rendered after the install)
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
