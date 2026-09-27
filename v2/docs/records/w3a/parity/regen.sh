#!/usr/bin/env bash
# w3a: regenerate board A's schematic phase with main's chain (full.sh's schematic steps), once for main and once for the candidate
set -uo pipefail
B=/root/w3a
for side in "$@"; do
  D=$B/$side/v2/ecad/pcb-a-power-a23
  cd "$D" || exit 2
  T=../tools; CFG=$T/boards/a.json
  export PHASE="${PHASE:-$(python3 -c "import json;print(json.load(open('$CFG')).get('phase') or '')")}"   # a caller's own value wins, as in full.sh
  GENV="$(python3 -c "import json,os; d=json.load(open('$CFG')).get('gen_env') or {}; print(' '.join('%s=%s' % (k, v) for k, v in d.items() if not os.environ.get(k)))")"
  echo "== $side PHASE=$PHASE GENV=$GENV"
  ( cd ..; find meshsat.pretty -type f -exec sha256sum {} + | sort -k2 > /root/w3a/$side-pretty-before.sha )
  mkdir -p out
  # the committed outputs, kept for comparison
  mkdir -p /root/w3a/$side-committed; cp -p out/pcb-a-power.net out/pcb-a-power-intent.json out/pcb-a-power.net.prov.json pcb-a-power.kicad_sch /root/w3a/$side-committed/
  for f in $(python3 -c "import json;v=json.load(open('$CFG')).get('footprint_generator') or [];print(' '.join(v if isinstance(v,list) else [v]))"); do
    python3 $T/$f ../meshsat.pretty > out/gen_fp.log 2>&1 || echo "FPGEN FAIL $f"
  done
  ( cd ..; find meshsat.pretty -type f -exec sha256sum {} + | sort -k2 > /root/w3a/$side-pretty-after.sha )
  env $GENV python3 $T/gen_sch_a.py pcb-a-power.kicad_sch pcb-a-power > out/gen_sch.log 2>&1; echo "gen_sch exit $?"; grep -E 'wrote|single-pin nets|intent:' out/gen_sch.log | cut -c1-200
  rm -f out/pcb-a-power.net
  $T/build_sch.sh . pcb-a-power > out/build_sch.log 2>&1; echo "build_sch exit $?"; grep -E 'ERC|netlist' out/build_sch.log
  rm -f out/pcb-a-power-erc.status out/erc_gate.verdict.json
  python3 $T/erc_gate.py . pcb-a-power --run > out/erc_gate.log 2>&1; echo "erc_gate exit $?"; tail -4 out/erc_gate.log | cut -c1-300
  python3 $T/power_path.py out/pcb-a-power.net > out/power_path.log 2>&1; echo "power_path exit $?"; grep -E '^power_path:' out/power_path.log | tail -8 | cut -c1-300
  python3 $T/sch_prov.py read out/pcb-a-power.net > out/sch_prov_read.log 2>&1; echo "sch_prov read exit $?"; head -5 out/sch_prov_read.log | cut -c1-200
done
