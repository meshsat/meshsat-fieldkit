#!/usr/bin/env python3
"""Run the NET section of a check_pcb_b.py against a KiCad netlist, without pcbnew (MESHSAT-1357 round 4, r4b fix-up,
26 September 2026).

Usage: check_pcb_b_emul.py <check_pcb_b.py> <netlist.net>

check_pcb_b.py builds `bynet` (net -> references) from a placed board's pads and then asserts the fabric nets.
A board that carries the round-4 parts does not exist yet (O-02: no placement run), so the review emulated that
section on netlists. This does the same with the gate's OWN SOURCE rather than a restatement of it: it parses the
given check_pcb_b.py with `ast`, takes every statement of the `if placed:` block from the one after the loop that
fills `bynet` up to the `import fnmatch` that starts the net-class section, and executes exactly those statements
with `bynet` and `bypad` (net -> (reference, pad)) built from the netlist's nodes and `check` recording each line.
Net names lose their leading '/', as the gate strips them from the board.
"""
import ast, os, sys, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from netdiff import parse_net   # the s-expression reader of W7's comparator, as the netlist diff uses it


def netlist_values(path):
    """reference -> value text, the netlist's (value ...) field, which is what pcbnew's GetValue() returns on a board
    (round 6, 26 September 2026: the gate judges a pull-down's size since R4T-F9)."""
    comps, _pins = parse_net(open(path).read())
    return {ref: c.get('value') for ref, c in comps.items()}


def netlist_maps(path):
    _comps, pins = parse_net(open(path).read())   # (ref, pin) -> net name, leading '/' already stripped
    bynet, bypad = {}, {}
    for (ref, pin), name in pins.items():
        bynet.setdefault(name, set()).add(ref); bypad.setdefault(name, set()).add((ref, pin))
    return bynet, bypad


def net_section(src):
    tree = ast.parse(src); lines = src.splitlines()
    blk = next(n for n in tree.body if isinstance(n, ast.If) and isinstance(n.test, ast.Name) and n.test.id == 'placed')
    body = blk.body
    start = next(i for i, n in enumerate(body) if isinstance(n, ast.For) and 'bynet' in ast.get_source_segment(src, n)) + 1
    end = next(i for i, n in enumerate(body) if isinstance(n, (ast.Import, ast.ImportFrom)) and 'fnmatch' in ast.get_source_segment(src, n))
    seg = '\n'.join(lines[body[start].lineno - 1: body[end - 1].end_lineno])
    return textwrap.dedent(seg), body[start].lineno, body[end - 1].end_lineno


def main(gate, net):
    src = open(gate).read()
    code, a, b = net_section(src)
    bynet, bypad = netlist_maps(net)
    res = []
    def check(c, m):
        res.append((bool(c), m)); print(('PASS ' if c else 'FAIL ') + m)
    exec(compile(code, '%s:%d-%d' % (gate, a, b), 'exec'), {'bynet': bynet, 'bypad': bypad, 'byval': netlist_values(net), 'check': check, 'sorted': sorted})
    fails = [m for c, m in res if not c]
    print('# %s lines %d-%d on %s: %d checks, %d FAIL' % (gate, a, b, net, len(res), len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:3]))
