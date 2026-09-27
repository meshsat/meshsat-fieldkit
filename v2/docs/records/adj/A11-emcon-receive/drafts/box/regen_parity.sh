#!/usr/bin/env bash
# Box job for A11-emcon-receive: regenerate the A, B and D schematics from the generators at HEAD in my own clone,
# export their netlists with kicad-cli, and compare them net by net (net name -> set of ref.pin) against the
# committed netlists. Writes only under /root/r2/A11-emcon-receive/.
set -uo pipefail
R=/root/r2/A11-emcon-receive; W=$R/regen; mkdir -p $W; cd $R/repo/v2/ecad
for spec in "a pcb-a-power-a23 pcb-a-power" "b pcb-b-compute-b19 pcb-b-compute" "d pcb-d-aprs-d9 pcb-d-aprs"; do
  set -- $spec; L=$1; D=$2; N=$3
  mkdir -p $W/$D; cp $D/fp-lib-table $W/$D/ 2>/dev/null; cp $D/$N.kicad_pro $W/$D/ 2>/dev/null
  ( cd $D && PHASE=regen python3 ../tools/gen_sch_$L.py $W/$D/$N.kicad_sch $N ) > $W/$D/gen.log 2>&1; echo "gen $L exit $?" >> $W/summary.txt
  kicad-cli sch export netlist --format kicadsexpr -o $W/$D/$N.net $W/$D/$N.kicad_sch > $W/$D/net.log 2>&1; echo "net $L exit $?" >> $W/summary.txt
done
python3 - <<'PY' >> $W/summary.txt
import re
def load(p):
    t=open(p,encoding="utf-8").read(); nets={}
    for part in t.split('(net (code "')[1:]:
        name=re.match(r'(\d+)"\) \(name "([^"]*)"\)',part).group(2).lstrip("/")
        nets[name]=frozenset("%s.%s"%(r,p) for r,p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)',part))
    return nets
R="/root/r2/A11-emcon-receive"
for D,N in (("pcb-a-power-a23","pcb-a-power"),("pcb-b-compute-b19","pcb-b-compute"),("pcb-d-aprs-d9","pcb-d-aprs")):
    try:
        a=load("%s/repo/v2/ecad/%s/out/%s.net"%(R,D,N)); b=load("%s/regen/%s/%s.net"%(R,D,N))
    except Exception as e:
        print(D,"PARITY ERROR",e); continue
    # compare by connectivity (the set of node sets), and by name for the named nets
    ca=set(a.values()); cb=set(b.values())
    named=[k for k in a if not k.startswith(("unconnected-","Net-("))]
    diff=[k for k in named if a.get(k)!=b.get(k)]
    print(D,"nets committed %d regen %d; connectivity identical: %s; named nets differing: %d %s"%(len(a),len(b),ca==cb,len(diff),diff[:10]))
PY
echo DONE >> $W/summary.txt
