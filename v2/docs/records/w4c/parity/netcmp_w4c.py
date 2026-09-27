#!/usr/bin/env python3
"""Independent KiCad netlist comparison for stream w4c (27 Sep 2026): its own s-expression reader, no project module.
Every component (value, footprint, every field, library part) and every net (name, class, and each node as
(ref, pin, pinfunction, pintype)), in both directions, plus a check against an expected-change list."""
import sys, json

def tokens(s):
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in '()': yield c; i += 1
        elif c.isspace(): i += 1
        elif c == '"':
            j = i + 1; buf = []
            while s[j] != '"':
                if s[j] == '\\': buf.append(s[j + 1]); j += 2
                else: buf.append(s[j]); j += 1
            yield ('S', ''.join(buf)); i = j + 1
        else:
            j = i
            while j < n and not s[j].isspace() and s[j] not in '()': j += 1
            yield ('A', s[i:j]); i = j

def parse(s):
    st = [[]]
    for t in tokens(s):
        if t == '(': st.append([])
        elif t == ')': x = st.pop(); st[-1].append(x)
        else: st[-1].append(t[1])
    return st[0][0]

def find(node, key): return [x for x in node if isinstance(x, list) and x and x[0] == key]

def val(node, key):
    f = find(node, key)
    return f[0][1] if f and len(f[0]) > 1 else None

def read(path):
    tree = parse(open(path, encoding='utf-8').read())
    comps, nets = {}, {}
    for comp in find(find(tree, 'components')[0], 'comp'):
        d = {'value': val(comp, 'value'), 'footprint': val(comp, 'footprint')}
        for fs in find(comp, 'fields'):
            for f in find(fs, 'field'):
                v = [x for x in f[1:] if not isinstance(x, list)]
                d['field:' + str(val(f, 'name'))] = v[0] if v else ''
        lib = find(comp, 'libsource')
        if lib: d['lib'] = '%s:%s' % (val(lib[0], 'lib'), val(lib[0], 'part'))
        comps[val(comp, 'ref')] = d
    for net in find(find(tree, 'nets')[0], 'net'):
        nodes = frozenset((val(n, 'ref'), val(n, 'pin'), val(n, 'pinfunction'), val(n, 'pintype')) for n in find(net, 'node'))
        nets[val(net, 'name')] = {'nodes': nodes, 'class': val(net, 'class')}
    return comps, nets

def compare(a, b):
    ca, na = read(a); cb, nb = read(b)
    out = {'components_only_a': sorted(set(ca) - set(cb)), 'components_only_b': {r: cb[r] for r in sorted(set(cb) - set(ca))},
           'components_changed': {}, 'nets_only_a': sorted(set(na) - set(nb)), 'nets_only_b': sorted(set(nb) - set(na)), 'nets_changed': {}}
    for r in sorted(set(ca) & set(cb)):
        diff = {k: [ca[r].get(k), cb[r].get(k)] for k in sorted(set(ca[r]) | set(cb[r])) if ca[r].get(k) != cb[r].get(k)}
        if diff: out['components_changed'][r] = diff
    for n in sorted(set(na) & set(nb)):
        if na[n] != nb[n]:
            out['nets_changed'][n] = {'removed': sorted(na[n]['nodes'] - nb[n]['nodes']), 'added': sorted(nb[n]['nodes'] - na[n]['nodes']),
                                      'class': [na[n]['class'], nb[n]['class']]}
    pa = {x[:2]: (n, x[2:]) for n, d in na.items() for x in d['nodes']}; pb = {x[:2]: (n, x[2:]) for n, d in nb.items() for x in d['nodes']}
    out['pins_moved_or_retyped'] = sorted([list(p), pa.get(p), pb.get(p)] for p in set(pa) | set(pb) if pa.get(p) != pb.get(p))
    out['counts'] = {'a': [len(ca), len(na), len(pa)], 'b': [len(cb), len(nb), len(pb)]}
    return out

def against(r, exp):
    """Does the comparison equal the expected-change list exactly?"""
    got = {'components_only_a': r['components_only_a'], 'components_only_b': sorted(r['components_only_b']),
           'components_changed': {k: sorted(v) for k, v in r['components_changed'].items()},
           'nets_only_a': r['nets_only_a'], 'nets_only_b': r['nets_only_b'],
           'nets_changed': {k: sorted('%s.%s' % (x[0], x[1]) for x in v['added']) + sorted('-%s.%s' % (x[0], x[1]) for x in v['removed'])
                            for k, v in r['nets_changed'].items()}}
    return got == exp, got

if __name__ == '__main__':
    r = compare(sys.argv[1], sys.argv[2])
    if len(sys.argv) > 3:
        ok, got = against(r, json.load(open(sys.argv[3])))
        r['expected_change_list'] = {'file': sys.argv[3], 'result': 'MATCH' if ok else 'MISMATCH', 'observed': got}
    print(json.dumps(r, indent=1, default=list))
