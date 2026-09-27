#!/usr/bin/env bash
# The suite on a CODE-ONLY archive: tools, cad and the two READMEs, no release/, no boards, no appendix, no .git.
# 15 September 2026 (red team round four H3): the pack sent to reviewers failed seven rules for missing artefacts and
# the Skip path written for that host had a NameError. Every rule that reads an artefact skips with `harness.need`
# now, and this script is how that stays true: run it before a pack goes out. Exit status is the suite's.
set -uo pipefail
R=$(cd "$(dirname "$0")/../../../.." && pwd); D=$(mktemp -d)
mkdir -p "$D/v2/ecad" && cp -r "$R/v2/ecad/tools" "$D/v2/ecad/" && cp -r "$R/v2/cad" "$D/v2/" 2>/dev/null; cp "$R/README.md" "$D/"; cp "$R/v2/README.md" "$D/v2/" 2>/dev/null
find "$D" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
cd "$D/v2/ecad" && python3 tools/tests/run.py 2>&1 | grep -E "FAIL|SKIP|passed" | grep -v " PASS$"; RC=${PIPESTATUS[0]}
echo "code-only checkout at $D (delete it when read)"; exit $RC
