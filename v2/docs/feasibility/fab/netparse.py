#!/usr/bin/env python3
"""Read-only KiCad 9 s-expression netlist reader for the FAILOVER-FABRIC map (MESHSAT-1357, 26 Sep 2026).

parse(path) -> (comps, nets, pinnet)
  comps:  ref -> {value, footprint, part, lcsc}
  nets:   net name (leading '/' stripped) -> list of (ref, pin, pinfunction, pintype)
  pinnet: (ref, pin) -> net name
No fitted constant, no write: it only reads the file it is given.
"""
import re, sys, hashlib


def _blocks(t, head):
    out, i = [], 0
    while True:
        i = t.find(head, i)
        if i < 0:
            return out
        d, j = 0, i
        while j < len(t):
            c = t[j]
            if c == '"':
                j += 1
                while t[j] != '"':
                    if t[j] == '\\':
                        j += 1
                    j += 1
            elif c == '(':
                d += 1
            elif c == ')':
                d -= 1
                if d == 0:
                    break
            j += 1
        out.append(t[i:j + 1])
        i = j + 1


def parse(path):
    t = open(path, encoding='utf-8').read()
    comps, nets, pinnet = {}, {}, {}
    ci = t.find('(components')
    ni = t.find('(nets')
    for b in _blocks(t[ci:ni], '(comp (ref'):
        ref = re.search(r'\(ref "([^"]+)"\)', b).group(1)
        v = re.search(r'\(value "((?:[^"\\]|\\.)*)"\)', b)
        f = re.search(r'\(footprint "([^"]*)"\)', b)
        fields = dict(re.findall(r'\(field \(name "([^"]+)"\) "((?:[^"\\]|\\.)*)"\)', b))
        lib = re.search(r'\(libsource \(lib "([^"]*)"\) \(part "([^"]*)"\)', b)
        comps[ref] = {'value': v.group(1) if v else None, 'footprint': f.group(1) if f else None,
                      'part': (lib.group(1) + ':' + lib.group(2)) if lib else None, 'lcsc': fields.get('LCSC')}
    for b in _blocks(t[ni:], '(net (code'):
        name = re.search(r'\(name "((?:[^"\\]|\\.)*)"\)', b).group(1)
        if name.startswith('/'):
            name = name[1:]
        nodes = []
        for nb in re.findall(r'\(node [^\n]*\)', b):
            ref = re.search(r'\(ref "([^"]+)"\)', nb).group(1)
            pin = re.search(r'\(pin "([^"]+)"\)', nb).group(1)
            pf = re.search(r'\(pinfunction "([^"]*)"\)', nb)
            pt = re.search(r'\(pintype "([^"]*)"\)', nb)
            nodes.append((ref, pin, pf.group(1) if pf else '', pt.group(1) if pt else ''))
            pinnet[(ref, pin)] = name
        nets[name] = nodes
    return comps, nets, pinnet


def sha256(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


if __name__ == '__main__':
    c, n, p = parse(sys.argv[1])
    print(sha256(sys.argv[1]), len(c), 'parts', len(n), 'nets')
