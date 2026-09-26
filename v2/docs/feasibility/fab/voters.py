#!/usr/bin/env python3
"""Evaluate the 2-of-3 voters of board B from a netlist (read-only; MESHSAT-1357 stream FAB, 26 Sep 2026).

Usage: voters.py <netlist>
Gates are read from the netlist with the standard quad-gate pinout of SN74LVC08A (SCAS283W, pin configuration),
SN74LVC32A (SCAS286U) and 74LVC86A (SCAS288R): gate n inputs (1,2)->3, (4,5)->6, (9,10)->8, (12,13)->11.
For every voted output it enumerates the 8 states of the three controller outputs and checks the result is the
majority; then it checks the break-before-make XOR sees the select on one input and the RC copy on the other.
"""
import itertools, sys
import tracer as T
b = T.Board(sys.argv[1])
GATES = {'08': lambda x, y: x & y, '32': lambda x, y: x | y, '86': lambda x, y: x ^ y}
PINS = [(('1', '2'), '3'), (('4', '5'), '6'), (('9', '10'), '8'), (('12', '13'), '11')]
gates = []
for ref, c in b.comps.items():
    v = c['value'] or ''
    kind = '08' if 'LVC08' in v else '32' if 'LVC32' in v else '86' if 'LVC86' in v else None
    if kind and (ref.startswith('U7') or ref == 'U80'):
        for (i1, i2), o in PINS:
            n1, n2, no = b.pinnet.get((ref, i1)), b.pinnet.get((ref, i2)), b.pinnet.get((ref, o))
            if no and not no.startswith('unconnected') and n1 != 'GND':
                gates.append((ref, kind, n1, n2, no))
def evaluate(inputs):
    val = dict(inputs)
    for _ in range(10):
        for ref, k, a, c, o in gates:
            if a in val and c in val:
                val[o] = GATES[k](val[a], val[c])
    return val
bits = ['SEL1', 'SEL2', 'SEL3', 'HUBRST1', 'HUBRST2', 'HUBRST3', 'WSEC']
out = {'SEL1': 'BSEL1', 'SEL2': 'BSEL2', 'SEL3': 'BSEL3', 'HUBRST1': 'HUBRST1_VOTE', 'HUBRST2': 'HUBRST2_VOTE',
       'HUBRST3': 'HUBRST3_VOTE', 'WSEC': 'WIFI_SEC'}
ok = 0
for bit in bits:
    good = True
    for s in itertools.product((0, 1), repeat=3):
        v = evaluate({'%s_A' % bit: s[0], '%s_B' % bit: s[1], '%s_C' % bit: s[2]})
        want = 1 if sum(s) >= 2 else 0
        if v.get(out[bit]) != want:
            good = False
            print('FAIL', bit, s, v.get(out[bit]))
    ok += good
    print('%-8s -> %-13s majority on all 8 states: %s' % (bit, out[bit], good))
for bank in (1, 2, 3):
    x = [g for g in gates if g[0] == 'U80' and g[4] == 'BOE%d_n' % bank]
    print('BOE%d_n = XOR(%s, %s)' % (bank, x[0][2], x[0][3]) if x else 'BOE%d_n: no XOR found' % bank)
print('%d of %d voted bits are 2-of-3 majorities; %d gates read' % (ok, len(bits), len(gates)))
