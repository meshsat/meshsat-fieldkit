#!/usr/bin/env python3
"""A generator that uses a name before it imports it (MESHSAT-862, 13 September 2026).

`gen_pcb_a3.py` called `regionfit.record(..., stem=os.path.splitext(...))` at the region loop on line 171 and
imported `os` on line 422. It compiles: a NameError is a runtime event, and this one fires 250 lines before
the import that would have fixed it. **Board A's placement generator could not run at all**, so every attempt
to regenerate A blocked at `BLOCK placement generator exit 1` and the chain refused, correctly, while the
cause sat two words long in a line nobody read.

It is the same family as the five September footprint `%.2f`: a file that is syntactically perfect and dead at
the moment it matters. `python3 -W error -c compile(...)` does not catch it, which is what the chains use.

Scope, stated honestly: module-scope statements only. A name used inside a function body is bound by the time
that function runs, so those are not flagged, and an import nested in an `if` or a `try` binds from its own
line onward, which is how `escape_prune.py` legitimately imports `os` inside the branch that uses it.
"""
import ast, glob, os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def uses_before_import(path):
    src = open(path).read()
    tree = ast.parse(src)
    bound = {}
    def collect(stmts):
        for node in stmts:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): continue
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for a in node.names:
                    nm = (a.asname or a.name).split(".")[0]
                    if nm not in bound or node.lineno < bound[nm]: bound[nm] = node.lineno
            for f in ("body", "orelse", "finalbody"):
                collect(getattr(node, f, []) or [])
            for h in getattr(node, "handlers", []) or []: collect(h.body)
    collect(tree.body)
    bad = []
    def scan(stmts):
        for node in stmts:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): continue
            for n in ast.walk(node):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in bound and n.lineno < bound[n.id]:
                    bad.append("%s used on line %d, imported on line %d" % (n.id, n.lineno, bound[n.id]))
            for f in ("body", "orelse", "finalbody"):
                scan(getattr(node, f, []) or [])
            for h in getattr(node, "handlers", []) or []: scan(h.body)
    scan(tree.body)
    return sorted(set(bad))


def t_no_tool_uses_a_module_scope_name_before_it_imports_it():
    bad = []
    for f in sorted(glob.glob(os.path.join(TOOLS, "*.py"))):
        for b in uses_before_import(f):
            bad.append("%s: %s" % (os.path.basename(f), b))
    assert not bad, ("a NameError waiting at module scope:\n  " + "\n  ".join(bad))


def t_the_rule_catches_the_shape_it_was_written_for():
    """gen_pcb_a3.py as it stood: os used at the region loop, imported 250 lines later."""
    import tempfile
    src = "import sys\nx = os.path.join('a', 'b')\nimport json, os\n"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(src); p = fh.name
    try:
        b = uses_before_import(p)
        assert b and b[0].startswith("os used on line 2"), "the rule missed its own fixture: %s" % b
    finally:
        os.unlink(p)


def t_an_import_inside_the_branch_that_uses_it_is_not_flagged():
    """escape_prune.py imports os inside the `if not victims:` branch that uses it, on the line before."""
    import tempfile
    src = "import sys\nif sys.argv:\n    import os\n    y = os.path.join('a', 'b')\n"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(src); p = fh.name
    try:
        assert not uses_before_import(p), "a legitimate nested import was flagged"
    finally:
        os.unlink(p)
