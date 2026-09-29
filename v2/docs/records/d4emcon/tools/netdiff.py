#!/usr/bin/env python3
"""Stream d4emcon (MESHSAT-1357): part-by-part and net-by-net difference of two KiCad netlists, read with
tx_inhibit.parse_netlist (the RF-002 instrument's own reader). Reads only; prints to stdout.

usage: netdiff.py <v2/ecad/tools> <old.net> <new.net>"""
import sys
sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode=True
import tx_inhibit
a=tx_inhibit.parse_netlist(sys.argv[2]); b=tx_inhibit.parse_netlist(sys.argv[3])
ca, cb = a["comps"], b["comps"]
for r in sorted(set(cb)-set(ca)): print("ADD part", r, (cb[r].get("value") or "")[:110])
for r in sorted(set(ca)-set(cb)): print("DEL part", r, (ca[r].get("value") or "")[:110])
for r in sorted(set(ca)&set(cb)):
    if ca[r].get("value")!=cb[r].get("value"): print("CHG part", r, repr((ca[r].get("value") or "")[:80]), "->", repr((cb[r].get("value") or "")[:80]))
na, nb = a["nets"], b["nets"]
for n in sorted(set(nb)-set(na)): print("ADD net", n, sorted((x[0],x[1]) for x in nb[n]))
for n in sorted(set(na)-set(nb)): print("DEL net", n, sorted((x[0],x[1]) for x in na[n]))
for n in sorted(set(na)&set(nb)):
    sa=set((x[0],x[1]) for x in na[n]); sb=set((x[0],x[1]) for x in nb[n])
    if sa!=sb: print("CHG net", n, "+", sorted(sb-sa), "-", sorted(sa-sb))
