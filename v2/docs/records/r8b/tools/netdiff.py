#!/usr/bin/env python3
"""Round-4 netlist difference, every line of it (MESHSAT-1357, 26 September 2026).

Usage: netdiff.py <committed.net> <regenerated.net> [out.json]

Reads both KiCad s-expression netlists with the parser of W7's comparator (drafts/scratch-parity/regen_compare.py,
parse_net, copied here so the file stands alone) and reports, in full and without caps:
  - components only in one side, and every changed value, footprint or LCSC field of a component in both;
  - every (reference, pin) whose net name differs, including pins that exist on one side only.
The pin view is the one a reviewer reads: 'U101.100 NVME1_RX_P -> NVME1_RX_SW_P' says what moved.
"""
import json, re, sys


def blocks(t, head):
    out, i = [], 0
    while True:
        i = t.find(head, i)
        if i < 0: return out
        d, j = 0, i
        while j < len(t):
            if t[j] == '(': d += 1
            elif t[j] == ')':
                d -= 1
                if d == 0: break
            j += 1
        out.append(t[i:j + 1]); i = j + 1


def parse_net(t):
    comps, pins = {}, {}
    for b in blocks(t, '(comp (ref'):
        ref = re.search(r'\(ref "([^"]+)"\)', b).group(1)
        v = re.search(r'\(value "((?:[^"\\]|\\.)*)"\)', b); f = re.search(r'\(footprint "([^"]*)"\)', b)
        fields = dict(re.findall(r'\(field \(name "([^"]+)"\) "((?:[^"\\]|\\.)*)"\)', b))
        lib = re.search(r'\(libsource \(lib "([^"]*)"\) \(part "([^"]*)"\)', b)
        comps[ref] = {'value': v.group(1) if v else None, 'footprint': f.group(1) if f else None,
                      'LCSC': fields.get('LCSC'), 'part': lib.group(2) if lib else None}
    i = t.find('(nets')
    for b in blocks(t[i + 5:], '(net (code'):
        name = re.search(r'\(name "((?:[^"\\]|\\.)*)"\)', b).group(1).lstrip('/')
        for nb in blocks(b, '(node (ref'):
            ref = re.search(r'\(ref "([^"]+)"\)', nb).group(1); pin = re.search(r'\(pin "([^"]+)"\)', nb).group(1)
            pins[(ref, pin)] = name
    return comps, pins


def main(a, b, out=None):
    ca, pa = parse_net(open(a).read()); cb, pb = parse_net(open(b).read())
    r = {'comps': [len(ca), len(cb)], 'pins': [len(pa), len(pb)],
         'comps_removed': sorted(set(ca) - set(cb)), 'comps_added': sorted(set(cb) - set(ca)), 'comps_changed': [], 'pins_changed': []}
    for k in sorted(set(ca) & set(cb)):
        d = {f: [ca[k][f], cb[k][f]] for f in ca[k] if ca[k][f] != cb[k][f]}
        if d: r['comps_changed'].append([k, d])
    for k in sorted(set(pa) | set(pb), key=lambda x: (x[0], x[1])):
        if pa.get(k) != pb.get(k):
            r['pins_changed'].append(['%s.%s' % k, pa.get(k), pb.get(k)])
    r['added_detail'] = {k: cb[k] for k in r['comps_added']}
    r['nets'] = [len(set(pa.values())), len(set(pb.values()))]
    r['nets_removed'] = sorted(set(pa.values()) - set(pb.values())); r['nets_added'] = sorted(set(pb.values()) - set(pa.values()))
    if out: json.dump(r, open(out, 'w'), indent=1)
    print('components %d -> %d (removed %d, added %d, changed %d); pins %d -> %d, %d pin(s) on a different net; nets %d -> %d'
          % (r['comps'][0], r['comps'][1], len(r['comps_removed']), len(r['comps_added']), len(r['comps_changed']),
             r['pins'][0], r['pins'][1], len(r['pins_changed']), r['nets'][0], r['nets'][1]))
    return r


if __name__ == '__main__':
    main(*sys.argv[1:4])
