#!/bin/bash
# copy main's gitignored evidence into the r8int6 worktree, by main's ignored-file list only, never over a tracked file
set -e
M=/home/claude-runner/gitlab/products/meshsat/meshsat-fieldkit
SP=$SP
W=$SP/wt/r8int6
L=$SP/r8int6/ignored-$(date +%H%M%S).lst
git -C $M ls-files -o -i --exclude-standard -- v2 \
  | grep -v -E '(^|/)(\.pytest_cache|__pycache__)/|CLAUDE\.md$|claude-design-prompt|ORDER-SESSION-PROMPT' > $L.all
git -C $W ls-files > $SP/r8int6/wt_tracked.lst
grep -v -x -F -f $SP/r8int6/wt_tracked.lst $L.all > $L || true
echo "main ignored: $(wc -l < $L.all); tracked in worktree (skipped): $(( $(wc -l < $L.all) - $(wc -l < $L) )); to copy: $(wc -l < $L)"
rsync -a --checksum --files-from=$L $M/ $W/
echo "copied; list $L"
