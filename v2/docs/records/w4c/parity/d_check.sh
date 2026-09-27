#!/usr/bin/env bash
# stream w4c pass 2: the diagrams' view of the ARCHITECTURE.md edit, read-only checks in the scratch clones (write nothing)
W=/root/w4c
for tag in 91894cd7 62f26a44; do
  T=$W/t-$tag; cd $T || exit 2
  echo "=== $tag, applied (HEAD $(git log --oneline -1 | cut -c1-40))"
  python3 v2/docs/diagrams/tools/extract_mermaid.py --check 2>&1 | tail -2
  python3 v2/docs/diagrams/tools/build.py --check 2>&1 | tail -12
  git checkout -q $tag
  echo "=== $tag, as committed"
  python3 v2/docs/diagrams/tools/extract_mermaid.py --check 2>&1 | tail -2
  python3 v2/docs/diagrams/tools/build.py --check 2>&1 | tail -12
  git checkout -q -
  git status --short | head -3
done
echo D-CHECK-DONE
