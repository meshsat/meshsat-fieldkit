#!/usr/bin/env bash
# REGENERATE.md section 6 with the one referenced citation restored by section 1a's fetch (only under /root/h2/ec)
set -u
V=H2; Z=/root/h2/ec
rm -rf $Z && mkdir -p $Z && cd $Z && unzip -q /root/h2/$V.zip && cd $V
HO="$PWD"; export PYTHONDONTWRITEBYTECODE=1
REF=62f26a44
fetch() { for p in "$@"; do
  b=$(awk -F'\t' -v p="$p" '$1==p{print $2}' REFERENCED-SOURCES.tsv)
  [ -n "$b" ] || { echo "NOT LISTED $p"; continue; }
  mkdir -p "$(dirname "$p")"
  curl -fsSL -o "$p" "https://raw.githubusercontent.com/meshsat/meshsat-fieldkit/$REF/$p" || { echo "FETCH FAILED $p"; continue; }
  got=$( (printf 'blob %s\0' "$(stat -c%s "$p")"; cat "$p") | sha1sum | cut -d' ' -f1)
  [ "$got" = "$b" ] && echo "OK $p" || echo "DIFFERS $p"
done; }
fetch v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf
cd "$HO/v2/ecad/tools"
VERDICT_DIR="$HO/../verdicts" python3 energy_chain.py --ecad ..
echo "energy_chain exit $?"
for b in a b e e5 p; do python3 -c "import json,sys; j=json.load(open(sys.argv[1])); print(sys.argv[1].split('/')[-1], j.get('verdict'), j.get('counts'))" "$HO/../verdicts/energy_chain_$b.verdict.json"; done
