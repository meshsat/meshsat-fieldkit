"""Print every fail-safe state the RF-002 walk solves for TX_INHIBIT_n, with its level (read-only; stream w4c)."""
import sys, os
tree = sys.argv[1]
sys.path.insert(0, os.path.join(tree, "v2/ecad/tools"))
os.chdir(os.path.join(tree, "v2/ecad/tools"))
import tx_inhibit as T, boardtable as BT
paths = ["pcb-a-power-a23/out/pcb-a-power.net", "pcb-b-compute-b19/out/pcb-b-compute.net", "pcb-c-display-c8/out/pcb-c-display.net",
         "pcb-d-aprs-d9/out/pcb-d-aprs.net", "pcb-e1-dock-e7/out/pcb-e1-dock.net", "pcb-p-pack-p2/out/pcb-p-pack.net"]
boards = {}
for p in paths:
    l = (BT.letter_for(os.path.basename(p).replace(".net", ".kicad_pcb")) or "").upper()
    boards[l] = T.parse_netlist(os.path.join(tree, "v2/ecad", p))
seen = []
orig = T._fs_bound
def wrap(boards_, s, line, down, cut, src):
    r = orig(boards_, s, line, down, cut, src)
    frag = sorted({k for k, _n in line})
    seen.append((frag, sorted(down), sorted(cut), r.get("ok"), r.get("v"), (r.get("text") or "")[:260]))
    return r
T._fs_bound = wrap
res = T.fail_safe(boards, sys.argv[2] if len(sys.argv) > 2 else "TX_INHIBIT_n")
for frag, down, cut, ok, v, text in seen:
    cutn = ["%s-%s %s" % (T.MATES[i]["a"][0], T.MATES[i]["b"][0], T.MATES[i]["a"][1]) for i in cut]
    print("fragment %-8s down %-6s cut %-40s ok %-5s v %s" % (",".join(frag), ",".join(down) or "-", ";".join(cutn) or "-", ok, "%.3f" % v if v is not None else v))
print("fail:", res["fail"][:1]); print("undecided:", res["undecided"][:1])
