#!/usr/bin/env python3
"""What the three circuit apply scripts of this stream share (MESHSAT-1357, worker d8dec31, 28 September 2026).

An apply script for a schematic generator edits TEXT, because the generators are text their owners read, and it
proves four things about its own edit: the old text was there exactly once, the new text differs, the file still
parses (ast), and the calls it added are in the syntax tree with the arguments it meant. A second run is refused by
a marker the first run writes into the file.

None of these scripts runs a generator: this host has no KiCad, and a generator's owner regenerates on the KiCad
host in the circuit round. What is tested here is the edit, on a copy.
"""
import ast, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netread


def sub_once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        raise SystemExit("%s: expected its old text exactly once, found %d time(s): %r" % (what, n, old[:110]))
    if old == new:
        raise SystemExit("%s: the new text is the old text" % what)
    return text.replace(old, new)


def string_constants(text):
    return {n.value for n in ast.walk(ast.parse(text)) if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def first_string_arguments(text):
    """The first positional argument of every call, where it is a string: the place a reference stands in c(), r(),
    part(), ic() and every helper built on them. A distributor's code is a string of the same shape (C382212) and is
    never a first argument, which is why the references are read here and not from every string of the file: the
    first version of next_free() read every string and answered C51897885, one above a distributor's code."""
    out = set()
    for n in ast.walk(ast.parse(text)):
        if isinstance(n, ast.Call) and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            out.add(n.args[0].value)
    return out


def next_free(prefix, netlist_path, gen_text, count=1):
    """The next `count` free references PREFIX<n>: above every one on the board's committed netlist and above every
    one the generator creates by name (the first argument of a call), read at apply time."""
    comps, _nets = netread.read(netlist_path)
    rx = re.compile(r"^%s(\d+)$" % re.escape(prefix))
    used = {int(m.group(1)) for m in map(rx.match, comps) if m}
    used |= {int(m.group(1)) for m in map(rx.match, first_string_arguments(gen_text)) if m}
    top = max(used) if used else 0
    if top > 999:
        raise SystemExit("next_free: the highest %s reference read is %s%d, which is no reference of these boards" % (prefix, prefix, top))
    return ["%s%d" % (prefix, top + 1 + k) for k in range(count)]


def calls(text, func):
    """[(positional string arguments, the call's source line)] of every call of `func` (a bare name or an attribute)."""
    out = []
    for n in ast.walk(ast.parse(text)):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            if name == func:
                out.append(([a.value for a in n.args if isinstance(a, ast.Constant)], n.lineno))
    return out


def first_args(text, func):
    return {a[0]: a for a, _l in calls(text, func) if a}


def finish(path, old_text, new_text, marker, dry, what):
    if marker not in new_text:
        raise SystemExit("%s: the edit does not carry its own marker" % what)
    if new_text == old_text:
        raise SystemExit("%s: nothing changed" % what)
    ast.parse(new_text)                       # the file still parses
    if not dry:
        with open(path, "w", encoding="utf-8") as f: f.write(new_text)
        ast.parse(open(path, encoding="utf-8").read())
    print("%s: %s, %d line(s) added%s" % (what, os.path.basename(path), new_text.count("\n") - old_text.count("\n"),
                                           " (checked, not written)" if dry else ""))


def refuse_second_run(text, marker, what):
    if marker in text:
        raise SystemExit("%s: already applied (its marker is in the file)" % what)
