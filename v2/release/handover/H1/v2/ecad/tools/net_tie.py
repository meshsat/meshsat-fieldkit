#!/usr/bin/env python3
"""USBLC6-2SC6 is a flow-through part: pins 1/6 and 3/4 are joined inside the package. Declare them as net-tie pad groups (text patch: the Python API has no setter). Usage: net_tie.py <board>"""
import sys, re
p = sys.argv[1]; s = open(p).read(); n = 0
def patch(m):
    global n
    blk = m.group(0)
    if "net_tie_pad_groups" in blk or '"USBLC6' not in blk: return blk
    new, k = re.subn(r'(\n(\t+)\(attr smd\))', r'\1\n\2(net_tie_pad_groups "1,6" "3,4")', blk, count=1)
    n += k
    return new
# footprint blocks start with "\n\t(footprint " and end before the next "\n\t(footprint " / "\n\t(gr_" / "\n\t(segment" etc.
out = re.sub(r'\n\t\(footprint .*?(?=\n\t\((?:footprint|gr_|segment|via|zone|arc)\b)', patch, s, flags=re.S)
open(p, "w").write(out); print("net_tie: %d USBLC6 footprints marked" % n)
