#!/usr/bin/env bash
# to_box.sh <name>: this branch as a bundle on the rented box, cloned under /root/d6dec/<name> at its tip.
# The clone comes from the box's /root/r8int6/repo (it holds 73ae2f21) plus the bundle; nothing is fetched INTO that
# repository, so no other stream's clone sees this branch. Run from anywhere; no cd.
set -eu
W=${WORKTREES:-$HOME/worktrees/meshsat-fieldkit}/d6dec
B=${BOX_BIN:-${WORKTREES:-$HOME/worktrees/meshsat-fieldkit}/_bin}
S=${SCRATCH:-${TMPDIR:-/tmp}/d6dec-to-box}/bx
N=$1; mkdir -p "$S"
H=$(git -C $W rev-parse HEAD)
git -C $W bundle create "$S/d6dec-$N.bundle" 73ae2f21..fnd/d6dec >/dev/null 2>&1
git -C $W bundle verify "$S/d6dec-$N.bundle" >/dev/null 2>&1
$B/bxs.sh "mkdir -p /root/d6dec/bundles"
$B/bxcp.sh to "$S/d6dec-$N.bundle" /root/d6dec/bundles/
$B/bxs.sh "set -e; rm -rf /root/d6dec/$N; git clone -q --no-checkout /root/r8int6/repo /root/d6dec/$N; git -C /root/d6dec/$N fetch -q /root/d6dec/bundles/d6dec-$N.bundle fnd/d6dec:refs/heads/d6dec; git -C /root/d6dec/$N checkout -q $H; git -C /root/d6dec/$N log --oneline -1; git -C /root/d6dec/$N status --short | head -3"
echo "box clone /root/d6dec/$N at $H"
