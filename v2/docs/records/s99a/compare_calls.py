#!/usr/bin/env python3
"""Parsed comparison of board A's generator against a base commit (stream s99a, item 6).

Reads v2/ecad/tools/gen_sch_a.py at BASE (git show) and in the worktree, parses both with ast, and compares every
module-level statement: a call statement is keyed by its function name and first literal argument (a reference or a
net), anything else by its kind and target; repeated keys are numbered in order. Comments are not statements, so a
comment-only change is invisible here by design; the diff shows those. Prints the added, removed and changed keys and,
for a changed call, which positional or keyword arguments differ. Writes nothing.
"""
import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
GEN = "v2/ecad/tools/gen_sch_a.py"
BASE = sys.argv[1] if len(sys.argv) > 1 else "36e10781"


def _name(f):
    if isinstance(f, ast.Name): return f.id
    if isinstance(f, ast.Attribute): return _name(f.value) + "." + f.attr
    return type(f).__name__


def _first(call):
    if call.args and isinstance(call.args[0], ast.Constant): return str(call.args[0].value)
    return ""


def _stmts(body, out, prefix=""):
    for st in body:
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call):
            c = st.value; out.append((prefix + "%s(%s)" % (_name(c.func), _first(c)), c))
        elif isinstance(st, (ast.For, ast.If, ast.With, ast.Try)):
            out.append((prefix + "%s[%d]" % (type(st).__name__, len(out)), st))
        elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            tg = st.targets[0] if isinstance(st, ast.Assign) else st.target
            out.append((prefix + "assign %s" % ast.unparse(tg), st))
        elif isinstance(st, (ast.FunctionDef, ast.ClassDef)):
            out.append((prefix + "def %s" % st.name, st))
        else:
            out.append((prefix + type(st).__name__, st))


def table(src):
    raw = []; _stmts(ast.parse(src).body, raw)
    seen = {}; out = {}
    for k, node in raw:
        k0 = k.split("[")[0] if k.startswith(("For[", "If[", "With[", "Try[")) else k
        if k0 != k:   # control statements keyed by their header text, not their position
            node_head = ast.unparse(node).split("\n")[0][:120]
            k0 = "%s %s" % (type(node).__name__, node_head)
        n = seen.get(k0, 0); seen[k0] = n + 1
        out["%s #%d" % (k0, n)] = node
    return out


def _argdiff(a, b):
    diffs = []
    if isinstance(a, ast.Call) and isinstance(b, ast.Call):
        for i in range(max(len(a.args), len(b.args))):
            x = ast.unparse(a.args[i]) if i < len(a.args) else None
            y = ast.unparse(b.args[i]) if i < len(b.args) else None
            if x != y: diffs.append("arg%d: %s -> %s" % (i, (x or "")[:90], (y or "")[:90]))
        ka = {k.arg: ast.unparse(k.value) for k in a.keywords}; kb = {k.arg: ast.unparse(k.value) for k in b.keywords}
        for k in sorted(set(ka) | set(kb)):
            if ka.get(k) != kb.get(k):
                diffs.append("%s: %s -> %s" % (k, (ka.get(k) or "(absent)")[:90], (kb.get(k) or "(absent)")[:90]))
    return diffs or ["(statement text differs)"]


def main():
    old = subprocess.run(["git", "-C", str(ROOT), "show", "%s:%s" % (BASE, GEN)], capture_output=True, text=True, check=True).stdout
    new = (ROOT / GEN).read_text()
    ta, tb = table(old), table(new)
    added = [k for k in tb if k not in ta]; removed = [k for k in ta if k not in tb]
    changed = [k for k in ta if k in tb and ast.dump(ta[k]) != ast.dump(tb[k])]
    print("base %s: %d statements; worktree: %d statements" % (BASE, len(ta), len(tb)))
    print("ADDED %d" % len(added)); [print("  + " + k) for k in added]
    print("REMOVED %d" % len(removed)); [print("  - " + k) for k in removed]
    print("CHANGED %d" % len(changed))
    for k in changed:
        print("  ~ " + k)
        for d in _argdiff(ta[k], tb[k]): print("      " + d)


if __name__ == "__main__":
    main()
