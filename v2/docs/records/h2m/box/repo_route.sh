#!/usr/bin/env bash
# The H2 minor-findings editor's run of REGENERATE.md section 9's repository route (MESHSAT-1357, 27 September 2026):
# a repository built from an H2 extraction with handover_pack.py repo (the tool as committed on fnd/h2m), the
# referenced files of section 1a restored and committed, then board P's schematic-phase re-take. Run on the rented
# KiCad 9.0.9 box under /root/h2m (outside /tmp); the folder is deleted afterwards.
set -u
cd /root/h2m
export PYTHONDONTWRITEBYTECODE=1
echo "=== check and extract ($(date -u +%H:%M:%S))"
sha256sum -c H2.zip.sha256
rm -rf x && mkdir x && (cd x && unzip -q ../H2.zip)
python3 x/H2/v2/ecad/tools/handover_pack.py verify x/H2
echo "=== handover_pack.py repo, the committed tool ($(date -u +%H:%M:%S))"
python3 handover_pack.py repo H2.zip /root/h2m/rtk; echo "repo exit $?"
python3 handover_pack.py repo H2.zip /root/h2m/rtk2 >/dev/null; echo "second build: $(git -C /root/h2m/rtk rev-parse HEAD) $(git -C /root/h2m/rtk2 rev-parse HEAD)"
python3 handover_pack.py repo H2.zip /tmp/h2m-refused; echo "under /tmp: exit $?"
cd /root/h2m/rtk
echo "=== the validator and the trace check before any fetch ($(date -u +%H:%M:%S))"
(cd v2/ecad && python3 tools/rules_lib.py requirements 2>&1 | tail -n 1)
(cd v2/ecad && python3 tools/rules_lib.py requirements 2>&1 | grep -c "closed by\|closed_by\|closing commit" )
python3 v2/ecad/tools/rules_render.py --requirements --check 2>&1 | tail -n 2
echo "=== section 1a's fetch, REF as its code computes it ($(date -u +%H:%M:%S))"
REF=$(awk '/^commit timeline:/{t=1} t && /^$/{exit} t && $4=="public" && $5=="yes" && ($2" "$3)>=d {d=$2" "$3; r=$1} END{print r}' SOURCE.txt)
echo "REF=$REF"
fetch() { for p in "$@"; do
  b=$(awk -F'\t' -v p="$p" '$1==p{print $2}' REFERENCED-SOURCES.tsv)
  [ -n "$b" ] || { echo "NOT LISTED $p"; continue; }
  mkdir -p "$(dirname "$p")"
  curl -fsSL -o "$p" "https://raw.githubusercontent.com/meshsat/meshsat-fieldkit/$REF/$p" || { echo "FETCH FAILED $p"; continue; }
  got=$( (printf 'blob %s\0' "$(stat -c%s "$p")"; cat "$p") | sha1sum | cut -d' ' -f1)
  [ "$got" = "$b" ] && echo "OK $p" || echo "DIFFERS $p"
done; }
fetch $(cd v2/ecad && python3 tools/rules_lib.py requirements 2>&1 | awk '/^ERROR/' | grep -o 'v2/vendor/[^ ,]*' | sort -u) | sort | uniq -c | awk '{print $2}' | sort | uniq -c
fetch $(python3 v2/docs/review-packets/battery/evidence/check_manifest.py | awk '$1=="MISSING"{print $2}') | awk '{print $1}' | sort | uniq -c
fetch v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf
git -c user.name="handover snapshot" -c user.email=handover-snapshot@meshsat.invalid -c commit.gpgsign=false add -A -f
git -c user.name="handover snapshot" -c user.email=handover-snapshot@meshsat.invalid -c commit.gpgsign=false commit -q -m "the referenced files of REGENERATE.md section 1a, restored and checked by blob sha"
echo "commits: $(git rev-list --count HEAD); status: '$(git status --short | head -3)'"
(cd v2/ecad && python3 tools/rules_lib.py requirements 2>&1 | tail -n 1)
python3 v2/docs/review-packets/battery/evidence/check_manifest.py | tail -n 1
python3 v2/ecad/tools/rules_render.py --requirements --check 2>&1 | tail -n 1
echo "=== board P's re-take ($(date -u +%H:%M:%S))"
cd v2/ecad
python3 tools/retake_schematic_phase.py --plan --in-place --board p 2>&1 | tail -n 1
python3 tools/retake_schematic_phase.py --run --in-place --routed --board p --json > /root/h2m/retake-p.json 2> /root/h2m/retake-p.log
echo "retake exit $?"
python3 - <<'PY'
import json
j = json.load(open("/root/h2m/retake-p.json"))
print(json.dumps({k: v for k, v in j.items() if k not in ("steps", "boards")}, sort_keys=True)[:600])
rd = []
def walk(o):
    if isinstance(o, dict):
        if "readings" in o and isinstance(o["readings"], list): rd.extend(o["readings"])
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(j)
for r in rd:
    if isinstance(r, dict): print("  %s %s %s" % (r.get("verdict") or r.get("name"), r.get("result"), (r.get("summary") or "")[:90]))
    else: print("  %s" % r)
PY
for i in 1 2 3; do python3 tools/rules_status.py > /root/h2m/status-$i.log 2>&1; tail -n 1 /root/h2m/status-$i.log; done
python3 tools/rules_render.py 2>&1 | tail -n 1
python3 tools/rules_render.py --check 2>&1 | tail -n 3
sed -n 6p ../docs/CURRENT-EVIDENCE.md
grep -E "^\| P \| P4 \|" ../docs/CURRENT-EVIDENCE.md | cut -c1-240
python3 - <<'PY'
lines = open("../docs/CURRENT-EVIDENCE.md", encoding="utf-8").read().splitlines()
on = False
for ln in lines:
    if ln.startswith("| board | rule | reading now |"): on = True; continue
    if on:
        if ln.startswith("|---"): continue
        if not ln.startswith("|"): break
        c = [x.strip() for x in ln.strip("|").split("|")]
        if c[0] == "P": print("  P row: %s | %s | %s" % (c[1], c[2], c[4][:80]))
PY
echo "=== done ($(date -u +%H:%M:%S))"
