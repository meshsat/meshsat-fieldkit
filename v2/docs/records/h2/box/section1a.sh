#!/usr/bin/env bash
# REGENERATE.md section 1a as H2 states it (only under /root/h2/ra2)
set -u
V=H2; Z=/root/h2/ra2
rm -rf $Z && mkdir -p $Z && cd $Z && unzip -q /root/h2/$V.zip && cd $V
export PYTHONDONTWRITEBYTECODE=1
REF=62f26a44
fetch() { for p in "$@"; do
  b=$(awk -F'\t' -v p="$p" '$1==p{print $2}' REFERENCED-SOURCES.tsv)
  [ -n "$b" ] || { echo "NOT LISTED $p"; continue; }
  mkdir -p "$(dirname "$p")"
  curl -fsSL -o "$p" "https://raw.githubusercontent.com/meshsat/meshsat-fieldkit/$REF/$p" || { echo "FETCH FAILED $p"; continue; }
  got=$( (printf 'blob %s\0' "$(stat -c%s "$p")"; cat "$p") | sha1sum | cut -d' ' -f1)
  [ "$got" = "$b" ] && echo "OK $p" || echo "DIFFERS $p"
done; }
fetch $(cd v2/ecad && python3 tools/rules_lib.py requirements 2>&1 | awk '/^ERROR/' | grep -o 'v2/vendor/[^ ,]*' | sort -u)
fetch $(python3 v2/docs/review-packets/battery/evidence/check_manifest.py | awk '$1=="MISSING"{print $2}')
fetch v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf
echo "--- after"
python3 v2/docs/review-packets/battery/evidence/check_manifest.py | tail -2
(cd v2/ecad && python3 tools/rules_lib.py requirements | tail -1)
python3 v2/ecad/tools/rules_render.py --requirements --check
du -sh v2/vendor
