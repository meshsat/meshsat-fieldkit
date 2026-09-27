#!/usr/bin/env bash
# stream w4c pass 2: apply the six files and the drafts (integration steps 1 to 5 of drafts/w4c/README.md) in throwaway
# clones of main 91894cd7 and of main 62f26a44, validate the registry, render the trace page, check the diagrams manifest
# and run the tests that read the touched files. Box scratch only (/root/w4c); never /root/gitlab.
set -uo pipefail
W=/root/w4c
F=$W/files
NAMES=$(cat $W/test-names.txt)
for tag in 91894cd7 62f26a44; do
  T=$W/t-$tag; rm -rf $T
  git clone -q $W/main $T || exit 3
  cd $T
  if [ $tag = 62f26a44 ]; then git fetch -q $W/main62.bundle refs/heads/main || exit 4; fi
  git checkout -q $tag || exit 5
  echo "=== $tag: $(git log --oneline -1 | cut -c1-80)"
  tar xf $F/w4c-files.tar -C $T
  python3 $F/apply_registry.py $T --dry-run > $W/t-$tag-apply-dry.diff 2>&1; tail -1 $W/t-$tag-apply-dry.diff | cut -c1-300
  python3 $F/apply_registry.py $T | cut -c1-400
  python3 $F/patch_docs.py $T --dry-run > $W/t-$tag-patch-dry.diff 2>&1; tail -1 $W/t-$tag-patch-dry.diff | cut -c1-200
  python3 $F/patch_docs.py $T > $W/t-$tag-patch.log 2>&1; cat $W/t-$tag-patch.log | cut -c1-200
  # step 4: the vendor filing
  cp $F/ultrachip-uc8253c-a0.6.pdf v2/vendor/pdi/
  python3 - "$F/sources-w4c.yaml" <<'PY'
import sys, yaml
src = open(sys.argv[1]).read()
entry = "".join(l for l in src.splitlines(True) if not l.startswith("#")).strip("\n") + "\n"
p = "v2/vendor/SOURCES.yaml"; t = open(p).read()
if "id: epd-driver-uc8253c" not in t:
    assert t.count("\nowed:\n") == 1
    t = t.replace("\nowed:\n", "\n" + entry + "\nowed:\n"); open(p, "w").write(t)
yaml.safe_load(open(p)); print("SOURCES.yaml: epd-driver-uc8253c filed")
PY
  # idempotency: a second run of both scripts changes nothing
  git add -A >/dev/null; python3 $F/apply_registry.py $T | cut -c1-160; python3 $F/patch_docs.py $T | cut -c1-120
  git diff --quiet && echo "second run: no change" || echo "second run CHANGED FILES"
  (cd v2/ecad/tools && python3 rules_lib.py requirements 2>&1 | tail -2 && python3 rules_render.py --requirements 2>&1 | tail -2)
  python3 v2/docs/diagrams/tools/build.py --check 2>&1 | tail -7
  git add -A >/dev/null; git -c user.name=w4c-scratch -c user.email=scratch@invalid commit -q -m "scratch: w4c applied (throwaway, never pushed)"
  git diff $tag HEAD --stat | tail -25
  git diff $tag HEAD > $W/t-$tag-applied.diff
  (python3 v2/ecad/tools/tests/run.py $NAMES > $W/t-$tag-tests.log 2>&1); echo "tests exit $?"
  grep -E "^tests: [0-9]+ passed" $W/t-$tag-tests.log; grep -E "FAIL|ERROR" $W/t-$tag-tests.log | head -20
  git status --short | head -10
done
echo T-RUN-DONE
