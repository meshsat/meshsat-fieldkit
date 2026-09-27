#!/usr/bin/env python3
"""The operating grade of every fitted active part and connector, against the adopted envelope (pre-PCB layer 6).

WHY IT EXISTS. `v2/ecad/tools/part_temps.py` compares thirteen declared parts with `pcb_envelope.yaml` and says of
itself that thirteen is a beginning and not a denominator. The layer 6 audit of 27 September 2026 asked for the grade
check "extended to every fitted active part and connector". This script is that extension, kept beside its page as a
record rather than as a rule: it writes `GRADE-CHECK.md` from the committed netlists, lcsc_fill.py's MAP, the
certification table and `grade-sources.yaml`, and it never writes an evidence file or a verdict JSON of the rule
registry (a gate run by hand writes the tree's evidence; this is not a gate).

WHAT IT JUDGES. Each BOM line whose first reference is a semiconductor (U, Q, D, LED), a crystal (Y), a transformer
(T), a relay (K), a fuse or holder (F), a coin-cell holder (BT), a switch (SW), a sounder (BZ) or a connector (J, P)
is joined to a row of `grade-sources.yaml` by its LCSC code (the netlist's, else lcsc_fill.py's, else the certified
table's, the order a finish fills blanks in), or by footprint and value for a line with none. Its range is set
against the envelope: the cold end against `ambient_c.in_use.min`; the hot end against the worst inside air
part_temps.py computes from the same file for a part `inside`, and against `ambient_c.in_use.max` for one on the face,
the plate, in the pack bay or outside. A row whose range is junction-only (kind TJ) is judged on the same numbers and
labelled, because its ambient margin needs the part's dissipation (layer 9). The qualification margins of the owner's
ruling D-02a (-33 C storage, +55 C operation, +71 C storage) are reported beside the verdict, never folded into it.

A line that no row covers is UNDECLARED and listed; a row without a range reads TBD. Nothing is assumed fine.

Usage: grade_check.py [--root DIR] [--write | --check]
  --write  (default) write GRADE-CHECK.md beside this file
  --check  exit 1 when GRADE-CHECK.md differs from what the tree now gives
"""
import argparse
import ast
import csv
import os
import re
import sys
from collections import OrderedDict, defaultdict

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BOARDS = OrderedDict([('A', 'pcb-a-power-a23/out/pcb-a-power.net'), ('B', 'pcb-b-compute-b19/out/pcb-b-compute.net'),
                      ('C', 'pcb-c-display-c8/out/pcb-c-display.net'), ('D', 'pcb-d-aprs-d9/out/pcb-d-aprs.net'),
                      ('E', 'pcb-e1-dock-e7/out/pcb-e1-dock.net'), ('P', 'pcb-p-pack-p2/out/pcb-p-pack.net')])
COMP = re.compile(r'\(comp \(ref "([^"]+)"\)\s*\(value "((?:[^"\\]|\\.)*)"\)\s*\(footprint "([^"]*)"\)(.*?)\(tstamps "[^"]*"\)\)',
                  re.S)
ACTIVE = ('U', 'Q', 'D', 'LED', 'Y', 'T', 'K', 'F', 'BT', 'SW', 'BZ', 'J', 'P')
PASSIVE = ('R', 'C', 'L', 'FB', 'RT', 'W_', 'PAD_W', 'JP', 'TP', 'H', 'S_', '#')


def _prefix(ref):
    return re.match(r'[A-Z_]+', ref).group(0)


def _is_active(ref):
    p = _prefix(ref)
    if p.startswith(PASSIVE) and not p.startswith(('SW', 'BT', 'BZ')):
        return False
    return p.startswith(ACTIVE)


def load_map(root):
    tree = ast.parse(open(os.path.join(root, 'v2/ecad/tools/lcsc_fill.py'), encoding='utf-8').read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == 'MAP' for t in node.targets):
            return ast.literal_eval(node.value)
    return {}


def bom_lines(root):
    MAP = load_map(root)
    cert = {}
    for r in csv.DictReader(open(os.path.join(root, 'v2/release/revA/order/JLC-CERTIFIED.tsv'), errors='replace'), delimiter='\t'):
        if r['verdict'] == 'CERTIFIED' and r['code']:
            cert.setdefault((r['comment'], r['fp']), r['code'])
    lines = defaultdict(list)
    for b, p in BOARDS.items():
        txt = open(os.path.join(root, 'v2/ecad', p), encoding='utf-8').read()
        for ref, val, fp, rest in COMP.findall(txt):
            if 'exclude_from_bom' in rest or ref.startswith(('H', 'S_', 'TP', '#')) or not _is_active(ref):
                continue
            m = re.search(r'\(property \(name "LCSC"\) \(value "([^"]*)"\)', rest)
            lines[(b, val.replace('\\"', '"'), fp.split(':')[-1])].append((ref, m.group(1) if m else ''))
    out = []
    for (b, val, fp), xs in sorted(lines.items()):
        codes = sorted(set(c for _, c in xs if c))
        code = codes[0] if codes else ''
        if not code:
            for (vre, fsub), c in MAP.items():
                if re.match(vre, val) and fsub in fp:
                    code = c
                    break
        if not code:
            code = cert.get((val, fp), '')
        out.append({'board': b, 'value': val, 'fp': fp, 'refs': sorted(r for r, _ in xs), 'code': code})
    return out


def inside_air_max(env):
    """The same arithmetic as v2/ecad/tools/part_temps.py:inside_air_max, read from the same file."""
    a = env['ambient_c']['in_use']
    rise = env['inside_air_rise_k']
    reduced = None
    for co in env['ambient_c']['carve_outs']:
        if 'above_c' in co and 'reduced mode' in str(co.get('what', '')):
            reduced = co['above_c']
    if reduced is None:
        return a['max'] + rise['three_modules_loaded_lid_open']
    return max(a['max'] + rise['one_module_lid_open'], reduced + rise['three_modules_loaded_lid_open'])


def verdict(row, env, inside_max):
    amb = env['ambient_c']['in_use']
    q = env['owner_rulings']['qualification_margins_c']
    lo, hi = row.get('min_c'), row.get('max_c')
    if row.get('not_a_component'):
        return 'NOT_A_COMPONENT', ''
    if lo is None and hi is None:
        return 'TBD', ''
    bar = inside_max if row.get('where', 'inside') == 'inside' else amb['max']
    out, lim = [], []
    if lo is None:
        lim.append('cold end not stated')
    elif lo > amb['min']:
        out.append('cold: rated from %s C, envelope %s C' % (lo, amb['min']))
    elif lo == amb['min']:
        lim.append('cold: at the %s C floor, no margin' % amb['min'])
    if hi is not None and hi < bar:
        out.append('hot: rated to %s C, bar %s C' % (hi, bar))
    elif hi is not None and hi == bar:
        lim.append('hot: at the %s C bar' % bar)
    margin = []
    if lo is not None and lo > q['storage_min']:
        margin.append('below %s C at the storage margin (survival rests on the storage rating)' % q['storage_min'])
    if hi is not None and row.get('where', 'inside') == 'inside' and hi < q['operating_max'] + env['inside_air_rise_k']['one_module_lid_open']:
        margin.append('under %s C inside air at the +%s C margin' % (q['operating_max'] + env['inside_air_rise_k']['one_module_lid_open'], q['operating_max']))
    if out and row.get('carve_out'):
        v = 'CARVE_OUT'
    elif out:
        v = 'OUTSIDE'
    elif lim and 'cold end not stated' in lim and len(lim) == 1:
        v = 'INSIDE_HOT_ONLY'
    elif lim:
        v = 'AT_LIMIT'
    else:
        v = 'INSIDE'
    if row.get('kind') == 'TJ' and v in ('INSIDE', 'AT_LIMIT', 'INSIDE_HOT_ONLY'):
        v += ' (TJ)'
    return v, '; '.join(out + lim + margin)


def _src(row):
    s = row.get('source') or {}
    bits = [s.get('class', '')]
    if s.get('document'):
        bits.append('`%s`' % s['document'])
    elif s.get('url'):
        bits.append('%s (sha256/16 `%s`, %s)' % (s['url'].split('?')[0], (s.get('sha256') or '')[:16], s.get('fetched_utc', '')))
    if s.get('clause'):
        bits.append(s['clause'])
    if s.get('quote'):
        bits.append('"%s"' % s['quote'][:160].replace('|', '/'))
    if s.get('note'):
        bits.append(s['note'])
    return ', '.join(b for b in bits if b)


def _range(row):
    lo, hi = row.get('min_c'), row.get('max_c')
    if lo is None and hi is None:
        return 'none read'
    return '%s to %s C %s' % ('?' if lo is None else lo, '?' if hi is None else hi, row.get('kind', ''))


def build(root):
    env = yaml.safe_load(open(os.path.join(root, 'v2/ecad/tools/pcb_envelope.yaml'), encoding='utf-8'))
    src = yaml.safe_load(open(os.path.join(HERE, 'grade-sources.yaml'), encoding='utf-8'))
    inside_max = inside_air_max(env)
    coded = {r['code']: r for r in src.get('coded') or []}
    uncoded = src.get('uncoded') or []
    lines = bom_lines(root)
    by_code, by_rule, undeclared = OrderedDict(), OrderedDict(), []
    for ln in lines:
        if ln['code'] and ln['code'] in coded:
            by_code.setdefault(ln['code'], []).append(ln)
            continue
        hit = None
        for i, u in enumerate(uncoded):
            m = u.get('match') or {}
            if m.get('fp') and m['fp'] not in ln['fp']:
                continue
            if m.get('value') and m['value'] not in ln['value']:
                continue
            hit = i
            break
        if hit is None:
            undeclared.append(ln)
        else:
            by_rule.setdefault(hit, []).append(ln)
    rows = []
    for code, lns in by_code.items():
        r = coded[code]
        v, why = verdict(r, env, inside_max)
        rows.append(('coded', code, r, lns, v, why))
    for i, lns in by_rule.items():
        r = uncoded[i]
        v, why = verdict(r, env, inside_max)
        rows.append(('uncoded', '', r, lns, v, why))
    mods = []
    for r in src.get('modules') or []:
        v, why = verdict(r, env, inside_max)
        mods.append((r, v, why))
    return env, inside_max, rows, mods, undeclared


def _refs(lns):
    per = defaultdict(list)
    for ln in lns:
        per[ln['board']] += ln['refs']
    out = []
    for b in per:
        refs = sorted(set(per[b]), key=lambda s: (re.sub(r'\d+', '', s), int(re.sub(r'\D', '', s) or 0)))
        out.append('%s %s' % (b, ', '.join(refs[:8]) + (' (+%d)' % (len(refs) - 8) if len(refs) > 8 else '')))
    return '; '.join(out)


def render(root):
    env, inside_max, rows, mods, undeclared = build(root)
    amb = env['ambient_c']['in_use']
    counts = defaultdict(int)
    for _, _, _, _, v, _ in rows:
        counts[v.split(' ')[0]] += 1
    mcounts = defaultdict(int)
    for _, v, _ in mods:
        mcounts[v.split(' ')[0]] += 1
    order = ['OUTSIDE', 'CARVE_OUT', 'AT_LIMIT', 'INSIDE_HOT_ONLY', 'TBD', 'INSIDE', 'NOT_A_COMPONENT']
    w = []
    w.append('# Grade check: every fitted active part and connector against the envelope\n')
    w.append('Generated by `v2/docs/parts/grade_check.py` from the committed netlists, `v2/ecad/tools/lcsc_fill.py`\'s MAP, '
             '`v2/release/revA/order/JLC-CERTIFIED.tsv`, `v2/ecad/tools/pcb_envelope.yaml` and `v2/docs/parts/grade-sources.yaml`. '
             'Do not edit by hand; edit the sources and run the script. Prototype design: nothing here has been built, powered '
             'or measured, and a range here is a maker\'s statement, not a test.\n')
    w.append('**Bars** (from `pcb_envelope.yaml`, decision 34 and the owner\'s D-02a): in use %s to %s C ambient; a part '
             '`inside` the case is judged against %s C of inside air (the arithmetic of `v2/ecad/tools/part_temps.py`: the '
             'reduced mode above +35 C gives the larger of %s + %s and 35 + %s); a part on the face, the plate, in the pack bay '
             'or outside against %s C. The qualification margins (-33 C storage, +55 C operation, +71 C storage) are '
             'reported in the last column and never change a verdict.\n'
             % (amb['min'], amb['max'], inside_max, amb['max'], env['inside_air_rise_k']['one_module_lid_open'],
                env['inside_air_rise_k']['three_modules_loaded_lid_open'], amb['max']))
    w.append('**Verdicts.** OUTSIDE: the maker\'s range does not cover the bar. CARVE_OUT: outside, and the envelope '
             'declares it. AT_LIMIT: the range ends exactly at a bar (no margin). INSIDE_HOT_ONLY: the sheet states a '
             'maximum and no operating minimum. TBD: no range read. (TJ): a junction-only rating, whose ambient margin '
             'needs the part\'s dissipation (layer 9).\n')
    w.append('**Board lines:** %s. **Modules, cells and wall parts:** %s. **Lines no row covers:** %d.\n'
             % (', '.join('%s %d' % (k, counts[k]) for k in order if counts.get(k)),
                ', '.join('%s %d' % (k, mcounts[k]) for k in order if mcounts.get(k)), len(undeclared)))
    for title, sel in (('Findings: OUTSIDE, CARVE_OUT, AT_LIMIT and TBD', lambda v: not v.startswith(('INSIDE', 'NOT_A'))),
                       ('INSIDE', lambda v: v.startswith('INSIDE')), ('Copper with no component', lambda v: v.startswith('NOT_A'))):
        sub = [x for x in rows if sel(x[4])]
        if not sub:
            continue
        w.append('\n## Board lines: %s (%d)\n' % (title, len(sub)))
        w.append('| Code | Part | Boards and references | Range | Where | Verdict | Why | Source |')
        w.append('|---|---|---|---|---|---|---|---|')
        for kind, code, r, lns, v, why in sorted(sub, key=lambda x: (order.index(x[4].split(' ')[0]), x[2].get('part', ''))):
            w.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (code or '-', (r.get('part') or '').replace('|', '/'),
                     _refs(lns), _range(r), r.get('where', 'inside'), v, why or '-', _src(r)))
    w.append('\n## Modules, cells and wall parts no netlist carries (%d)\n' % len(mods))
    w.append('| Part | Maker | Range | Where | Verdict | Why | Source |')
    w.append('|---|---|---|---|---|---|---|')
    for r, v, why in sorted(mods, key=lambda x: (order.index(x[1].split(' ')[0]), x[0].get('part', ''))):
        w.append('| %s | %s | %s | %s | %s | %s | %s |' % (r.get('part', ''), r.get('maker', ''), _range(r), r.get('where', 'inside'),
                 v, (why or '-') + ('; ' + r['carve_out'] if r.get('carve_out') else ''), _src(r) + ('; ' + r['note'] if r.get('note') else '')))
    if undeclared:
        w.append('\n## Lines no row covers (UNDECLARED, %d)\n' % len(undeclared))
        for ln in undeclared:
            w.append('- %s %s `%s` %s: %s' % (ln['board'], ', '.join(ln['refs']), ln['fp'], ln['code'] or '(no code)', ln['value'][:120]))
    return '\n'.join(w) + '\n'


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=DEFAULT_ROOT)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args(argv)
    text = render(a.root)
    path = os.path.join(HERE, 'GRADE-CHECK.md')
    if a.check:
        cur = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
        if cur != text:
            print('GRADE-CHECK.md is not what the tree gives; run grade_check.py --write')
            return 1
        print('GRADE-CHECK.md is current')
        return 0
    open(path, 'w', encoding='utf-8').write(text)
    print('wrote', path)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
