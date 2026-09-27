#!/usr/bin/env python3
"""Trace a pin through series two-pin passives to its far-end pins (read-only; MESHSAT-1357 FAB stream).

A two-pin R, C, L, FB or 0-ohm link whose other pin is not on a ground or rail net is treated as SERIES and
followed; one whose other pin is on GND or a declared rail is recorded as a SHUNT on the net it hangs from.
Everything else on a net (ICs, connectors, test pads, transistors) is an endpoint. Rails are recognised by
name only: nets starting with '+' or equal to GND. That is a naming convention of this board's generator,
stated here so the reader knows the tracer relies on it.
"""
import re
import netparse

PASSIVE = re.compile(r'^(R|C|L|FB)\d+$')


def is_rail(net):
    return net == 'GND' or net.startswith('+') or net.startswith('GND')


class Board:
    def __init__(self, path):
        self.comps, self.nets, self.pinnet = netparse.parse(path)
        self.pf = {}
        for net, nodes in self.nets.items():
            for (r, pin, f, t) in nodes:
                self.pf[(r, pin)] = f
        self.pins_of = {}
        for (r, pin), net in self.pinnet.items():
            self.pins_of.setdefault(r, []).append(pin)

    def val(self, ref):
        v = self.comps.get(ref, {}).get('value') or ''
        return v

    def two_pin(self, ref):
        return PASSIVE.match(ref) and len(self.pins_of.get(ref, [])) == 2

    def other(self, ref, pin):
        ps = [p for p in self.pins_of[ref] if p != pin]
        return ps[0]

    def trace(self, ref, pin, maxhops=4):
        """Return (paths, shunts): paths = list of chains [(net, via_part_or_None)...] ending at an endpoint pin."""
        start = self.pinnet.get((ref, pin))
        out = []
        shunts = []
        seen = set([(ref, pin)])

        def walk(net, chain, hops):
            for (r, p, f, t) in self.nets[net]:
                if (r, p) in seen:
                    continue
                seen.add((r, p))
                if self.two_pin(r):
                    op = self.other(r, p)
                    onet = self.pinnet[(r, op)]
                    seen.add((r, op))
                    if is_rail(onet):
                        shunts.append((net, r, self.val(r), onet))
                        continue
                    if hops < maxhops:
                        walk(onet, chain + [(net, '%s(%s)' % (r, self.val(r)))], hops + 1)
                    else:
                        out.append(chain + [(net, None)] + [('...', r)])
                else:
                    out.append((chain + [(net, None)], (r, p, f)))
        if start is None:
            return [], []
        walk(start, [], 0)
        return out, shunts

    def fmt(self, ref, pin):
        paths, shunts = self.trace(ref, pin)
        s = []
        for p in paths:
            if isinstance(p, tuple):
                chain, (r, pp, f) = p
                txt = ' -> '.join((n if v is None else '%s -> %s' % (n, v)) for n, v in chain)
                s.append('%s => %s.%s %s' % (txt, r, pp, f))
            else:
                s.append(' -> '.join(str(x) for x in p))
        sh = ['%s: %s %s to %s' % x for x in shunts]
        return s, sh
