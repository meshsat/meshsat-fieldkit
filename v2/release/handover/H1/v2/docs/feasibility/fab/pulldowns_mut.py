#!/usr/bin/env python3
"""Mutation set for pulldowns.py (read-only on its input; MESHSAT-1357 stream FAB, 26 Sep 2026).

Usage: pulldowns_mut.py <candidate netlist> <out dir>
Writes three netlists into <out dir> (never into the repository): fixed.net (R480 to R500, R15 and R16 at 10k, the
FAB-04 remedy), mut_r500_100k.net (WSEC_C's pull-down left at 100k) and mut_r498_gone.net (WSEC_A's pull-down under
another designator). pulldowns.py must read FAIL 0, 1 and 1 on them.
"""
import re, sys
src, out = sys.argv[1], sys.argv[2]
t = open(src, encoding='utf-8').read()


def setval(t, ref, val):
    pat = re.compile(r'(\(comp \(ref "%s"\)\s*\(value ")([^"]*)(")' % ref)
    t2, n = pat.subn(lambda m: m.group(1) + val + m.group(3), t)
    assert n == 1, (ref, n)
    return t2


fixed = t
for r in ['R%d' % k for k in range(480, 501)] + ['R15', 'R16']:
    fixed = setval(fixed, r, '10k')
assert fixed != t
open(out + '/fixed.net', 'w').write(fixed)
open(out + '/mut_r500_100k.net', 'w').write(setval(fixed, 'R500', '100k'))
gone = fixed.replace('(ref "R498")', '(ref "R998")')
assert gone != fixed
open(out + '/mut_r498_gone.net', 'w').write(gone)
