#!/usr/bin/env python3
"""Placement distance screen for the fabric's long runs (read-only; MESHSAT-1357 stream FAB, 26 Sep 2026).

Usage: lengths.py <board.kicad_pcb>
Manhattan distance between FOOTPRINT ORIGINS on the given board. It is a screen, not a length: pads, escapes,
detours and layer changes are not in it, and routed length is usually longer. It says which runs are long enough
to need a channel budget, nothing more.
"""
import re, sys, hashlib
t = open(sys.argv[1]).read()
pos = {}
i = 0
while True:
    i = t.find('(footprint "', i)
    if i < 0:
        break
    j = t.find('(property "Reference" "', i)
    ref = t[j + 23:t.find('"', j + 23)]
    a = re.search(r'\(at ([-\d.]+) ([-\d.]+)', t[i:i + 600])
    pos[ref] = (float(a.group(1)), float(a.group(2)))
    i += 10
def d(a, b):
    return abs(pos[a][0] - pos[b][0]) + abs(pos[a][1] - pos[b][1])
segs = []
for s in (1, 2, 3):
    cm = {1: 'U30B', 2: 'U31B', 3: 'U32B'}[s]; ca = {1: 'U30A', 2: 'U31A', 3: 'U32A'}[s]
    sw = 'U%d01' % s
    segs += [('PCIe up, slot %d' % s, [cm, sw]), ('PCIe to NVMe, slot %d' % s, [sw, 'J_M2N%d' % s]),
             ('PCIe to card, slot %d' % s, [sw, 'J_M2C%d' % s]),
             ('USB home, slot %d to bank %d hub' % (s, s), [cm, 'U%d09' % s, 'U%d02' % s])]
    f = {1: 3, 2: 1, 3: 2}[s]
    segs.append(('USB failover, slot %d USB3-1 to bank %d hub' % (s, f), [cm, 'U%d09' % f, 'U%d02' % f]))
    segs.append(('Ethernet, slot %d to KSZ9897R' % s, [ca, 'U1']))
segs += [('HDMI, slot 1 to J_HDMI', ['U30B', 'U3', 'U4', 'J_HDMI']), ('HDMI, slot 2 to J_HDMI', ['U31B', 'U3', 'U4', 'J_HDMI']),
         ('HDMI, slot 3 to J_HDMI', ['U32B', 'U4', 'J_HDMI']), ('LimeSDR, bank 1 hub to J_LIME', ['U102', 'J_LIME'])]
print('board sha256', hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest())
for name, chain in segs:
    L = sum(d(a, b) for a, b in zip(chain, chain[1:]))
    print('%-45s %-32s %6.1f mm' % (name, ' > '.join(chain), L))
