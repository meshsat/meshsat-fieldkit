#!/usr/bin/env python3
"""The pair_router package imports on a host with pcbnew, proved here without one: every name a module uses at MODULE
level is defined in that module or in a module it imports, in import order. The first split put the timed wrappers
past the geometry anchor and the package raised NameError on the box (A36's pre-route, 15 September 2026 21:55 CEST)
while the runner's suite, which cannot import pcbnew, stayed green."""
import os, ast, builtins, re
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(TOOLS, "pair_router")


def _defs(tree):
    local = set()
    for n in tree.body:
        for x in ast.walk(n):
            if isinstance(x, (ast.FunctionDef, ast.ClassDef)): local.add(x.name)
            elif isinstance(x, ast.Name) and isinstance(x.ctx, ast.Store): local.add(x.id)
            elif isinstance(x, ast.alias): local.add((x.asname or x.name).split(".")[0])
            elif isinstance(x, ast.arg): local.add(x.arg)
            elif isinstance(x, ast.ExceptHandler) and x.name: local.add(x.name)
    return local


def _module_level_loads(tree):
    used = set()
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)): continue   # a function body resolves at call time
        for x in ast.walk(n):
            if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load): used.add(x.id)
    return used


def t_every_module_level_name_in_the_package_resolves_in_import_order():
    trees = {m: ast.parse(open(os.path.join(PKG, m + ".py")).read()) for m in ("config", "occupancy", "search", "geometry")}
    imports = {m: [a.module.lstrip(".") for n in trees[m].body if isinstance(n, ast.ImportFrom) and n.level == 1 for a in [n]] for m in trees}
    # a `from .x import name` inside the module body (not a star import) counts through _defs' aliases; star imports bring the whole module
    bad = []
    for m, t in trees.items():
        visible = set(dir(builtins)) | {"__file__", "__name__", "__doc__"} | _defs(t)
        for dep in imports[m]: visible |= _defs(trees[dep])
        used = _module_level_loads(t)
        # comprehension variables are stores inside expressions the walker sees as loads too; they are in _defs by the Store visit
        missing = sorted(u for u in used if u not in visible)
        if missing: bad.append("%s.py uses %s at module level and no module it imports defines them" % (m, missing))
    assert not bad, "\n".join(bad)


def t_the_entry_file_reexports_the_whole_package_in_dependency_order():
    src = open(os.path.join(TOOLS, "pair_preroute.py"), errors="replace").read()
    order = [m for m in re.findall(r"^from pair_router\.(\w+) import \*", src, re.M)]
    assert order == ["config", "occupancy", "search", "geometry"], order
