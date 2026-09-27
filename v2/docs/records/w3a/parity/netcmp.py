#!/usr/bin/env python3
"""Independent KiCad netlist comparison (w3a, 27 Sep 2026): its own s-expression reader, no project module.
Compares every component (value, footprint, every field) and every net (name and its (ref, pin) set; class)."""
import sys, re, json

def tokens(s):
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in '()': yield c; i += 1
        elif c.isspace(): i += 1
        elif c == '"':
            j = i + 1; buf = []
            while s[j] != '"':
                if s[j] == '\\': buf.append(s[j+1]); j += 2
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

def find(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]

def val(node, key):
    f = find(node, key)
    return f[0][1] if f and len(f[0]) > 1 else None

def read(path):
    tree = parse(open(path, encoding='utf-8').read())
    comps, nets = {}, {}
    for comp in find(find(tree, 'components')[0], 'comp'):
        ref = val(comp, 'ref')
        d = {'value': val(comp, 'value'), 'footprint': val(comp, 'footprint')}
        for fs in find(comp, 'fields'):
            for f in find(fs, 'field'):
                nm = val(f, 'name'); v = [x for x in f[1:] if not isinstance(x, list)]
                d['field:' + str(nm)] = v[0] if v else ''
        lib = find(comp, 'libsource')
        if lib: d['lib'] = (val(lib[0], 'lib'), val(lib[0], 'part'))
        comps[ref] = d
    for net in find(find(tree, 'nets')[0], 'net'):
        name = val(net, 'name')
        pins = frozenset((val(n, 'ref'), val(n, 'pin')) for n in find(net, 'node'))
        nets[name] = {'pins': pins, 'class': val(net, 'class')}
    return comps, nets

def compare(a, b):
    ca, na = read(a); cb, nb = read(b)
    out = {'components_only_a': sorted(set(ca) - set(cb)), 'components_only_b': sorted(set(cb) - set(ca)),
           'components_changed': {}, 'nets_only_a': {}, 'nets_only_b': {}, 'nets_changed': {}}
    for r in sorted(set(ca) & set(cb)):
        diff = {k: (ca[r].get(k), cb[r].get(k)) for k in set(ca[r]) | set(cb[r]) if ca[r].get(k) != cb[r].get(k)}
        if diff: out['components_changed'][r] = diff
    # nets compared by NAME and, independently, by pin set
    for n in sorted(set(na) - set(nb)): out['nets_only_a'][n] = sorted(na[n]['pins'])
    for n in sorted(set(nb) - set(na)): out['nets_only_b'][n] = sorted(nb[n]['pins'])
    for n in sorted(set(na) & set(nb)):
        if na[n]['pins'] != nb[n]['pins'] or na[n]['class'] != nb[n]['class']:
            out['nets_changed'][n] = {'removed': sorted(na[n]['pins'] - nb[n]['pins']), 'added': sorted(nb[n]['pins'] - na[n]['pins']),
                                      'class': (na[n]['class'], nb[n]['class'])}
    # pin -> net maps, the other direction: every pin of every component, which net it is on
    pa = {p: n for n, d in na.items() for p in d['pins']}; pb = {p: n for n, d in nb.items() for p in d['pins']}
    out['pins_moved'] = sorted((p, pa.get(p), pb.get(p)) for p in set(pa) | set(pb) if pa.get(p) != pb.get(p))
    out['counts'] = {'a': [len(ca), len(na), len(pa)], 'b': [len(cb), len(nb), len(pb)]}
    return out

if __name__ == '__main__':
    r = compare(sys.argv[1], sys.argv[2])
    print(json.dumps(r, indent=1, default=list))
