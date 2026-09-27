#!/bin/bash
# r8int6: commit one stream's integration as the owner, its message filled with the ids its scripts took and the base.
# Usage: commit_r8int6.sh <stream> <base short sha>
set -e
SP=$SP
R=$SP/r8int6; W=$SP/wt/r8int6; s=$1; BASE=$2
python3 $R/common/fill_msg_r8int6.py "$R/msg/$s.tmpl" "$R/kit/$s/ids_r8int6.json" "$BASE" "$R/msg/$s.txt"
cd "$W"
git add -A v2/ecad v2/docs v2/vendor
if git status --short | grep -v "^[MADR] "; then echo "commit_r8int6: unstaged or untracked files left"; exit 1; fi
SUBJ=$(head -1 "$R/msg/$s.txt")
git diff --cached | bash /home/claude-runner/gitlab/products/meshsat/scripts/pre-commit-check.sh meshsat-fieldkit --msg "$SUBJ" | tail -1
if git status --short | grep "^[MADR]" | grep -v -E "^[MADR]  v2/(ecad|docs|vendor)/"; then echo "commit_r8int6: staged outside v2"; exit 1; fi
git -c user.name="Kyriakos Papadopoulos" -c user.email="ncpjfuzl@mxmx.email" commit -q -F "$R/msg/$s.txt"
git log --oneline -1 | cat
$R/validate.sh 2>&1 | grep -E "error|out of date|current|rc="
