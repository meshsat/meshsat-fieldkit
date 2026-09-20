#!/bin/bash
# A CHAIN TREE WITHOUT THE VENDOR LIBRARY. 20 September 2026: the hub filled to 100 percent with 184 K free
# and four measurements died with `No space left on device`, which is the real reason the boxes have not
# been running in parallel; the cores were never the limit (load 6 of 96 threads, 106 GiB of memory free).
# An arm tree was a whole-repo copy at 810 MB, of which **636 MB is `v2/vendor`**, the 305-document library a
# CHAIN never opens; only a SWEEP does, and 31's own lesson is that a sweep carries the whole library or
# none of it, so this is for chains and routes alone. With one project directory instead of seven a tree is
# about 60 to 100 MB, so where one arm fitted, ten fit.
# Usage: stage_chain.sh <dest> <project dir>
set -u
D="$1"; PROJ="$2"
# SRC is the tree the boards and the sibling netlists come from and TOOLS the staged tools; both are box
# paths and both are arguments, because a driver that names one rented host is a claim about that host.
SRC="${3:-${STAGE_SRC:-/root/sweep32}}"; TOOLS="${4:-${STAGE_TOOLS:-/root/localtools}}"
rm -rf "$D"; mkdir -p "$D/v2/ecad" "$D/v2/release/revA/boards" "$D/v2/docs"
rsync -a "$SRC"/v2/ecad/tools/ "$D/v2/ecad/tools/" || exit 9
rsync -a --delete "$TOOLS"/ "$D/v2/ecad/tools/" || exit 9
rsync -a "$SRC"/v2/ecad/meshsat.pretty/ "$D/v2/ecad/meshsat.pretty/" || exit 9
rsync -a --exclude 'out/' ""$SRC"/v2/ecad/$PROJ/" "$D/v2/ecad/$PROJ/" || exit 9
for f in fp-lib-table; do [ -f ""$SRC"/v2/ecad/$f" ] && cp ""$SRC"/v2/ecad/$f" "$D/v2/ecad/$f"; done
# the sibling netlists, sidecars and intent files the contract gate needs (17 September: an isolated tree has
# one board in it and check_contracts needs six), which are kilobytes, not the boards
for p in "$SRC"/v2/ecad/pcb-*/; do n=$(basename "$p"); mkdir -p "$D/v2/ecad/$n/out"
  cp "$p"out/*.net "$p"out/*.net.prov.json "$p"out/*-intent.json "$D/v2/ecad/$n/out/" 2>/dev/null; done
rsync -a ""$SRC"/v2/ecad/$PROJ/out/" "$D/v2/ecad/$PROJ/out/" 2>/dev/null
du -sh "$D"
