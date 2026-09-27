#!/usr/bin/env python3
"""Stream w4b (27 September 2026): run check_pcb_b.py's EMCON block (from its "THE HARDWARE EMCON LINE IS ONLY READ" comment
to the FAB-01 comment) on a NETLIST instead of a placed board, so the draft edits of apply_check_pcb_b_w4b.py can be read on
the candidate before board B has a placement. The block reads only bynet, bypad and byval, which a placed board builds from
its pads' nets and values; here they are built from the netlist's nodes (net names without their leading '/', as the gate
strips them). Usage: emcon_block_harness.py <check_pcb_b.py> <pcb-b-compute.net>. Prints each PASS/FAIL line and a count;
exit 1 if any FAIL. It is a reading aid for the draft, not the gate: the gate runs on the placed board."""
import sys, re, os, textwrap
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(sys.argv[1]))))
import tx_inhibit as T


def main(a):
    src = open(a[0], encoding="utf-8").read().split("\n")
    i0 = next(i for i, l in enumerate(src) if "THE HARDWARE EMCON LINE IS ONLY READ ON THIS BOARD" in l)
    i1 = next(i for i, l in enumerate(src) if "# FAB-01 (MESHSAT-1357 round 8; FAILOVER" in l)
    block = textwrap.dedent("\n".join(src[i0:i1]))
    nl = T.parse_netlist(a[1])
    bynet, bypad = {}, {}
    for net, nodes in nl["nets"].items():
        nm = net.lstrip("/")
        for ref, pin, _fn in nodes:
            bynet.setdefault(nm, set()).add(ref); bypad.setdefault(nm, set()).add((ref, pin))
    byval = {r: c.get("value", "") for r, c in nl["comps"].items()}
    res = []
    def check(c, m):
        print(("PASS " if c else "FAIL ") + m[:400]); res.append(bool(c))
    ns = dict(bynet=bynet, bypad=bypad, byval=byval, check=check)
    exec(compile(block, "check_pcb_b EMCON block", "exec"), ns)
    print("block: %d checks, %d FAIL" % (len(res), res.count(False)))
    return 1 if False in res else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
