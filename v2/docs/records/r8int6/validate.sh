#!/bin/bash
# validators for the r8int6 integration, run from v2/ecad/tools of the worktree
cd $SP/wt/r8int6/v2/ecad/tools || exit 2
echo "--- rules_lib"; python3 rules_lib.py 2>&1 | tail -3
echo "--- rules_lib requirements"; python3 rules_lib.py requirements 2>&1 | grep -v "out/rule-audit is not" | tail -8
echo "--- rules_render --check"; python3 rules_render.py --check 2>&1 | tail -6
echo "--- rules_render --requirements --check"; python3 rules_render.py --requirements --check 2>&1 | tail -2
echo "--- decisions_render --check"; python3 decisions_render.py --check 2>&1 | tail -2; echo "rc=$?"
