"""The evidence behind the two `kind: tool` entries of v2/docs/evidence/COMPATIBILITY.md written by the second release
attempt of layers 1 to 3 (27 September 2026, MESHSAT-1357, fnd/rel2 from 953f5658).

Layer 3's finding R5 asked the requirements validator in rules_lib.py to refuse an SC- id no session choice defines.
rules_lib.py is in the code bundle of two writers whose readings are current on main: intent_checks.py (PWR-001 on
boards A, D and E, bundle 5aa3d5157698ae2a) and derate.py (CMP-001 on E5, bundle 4c4fc2aca3d8e542). Any edit of the
file changes both bundles, and rules_status would then read those readings TOOL_CHANGED. This script shows, from the
files themselves, that the edit cannot reach either writer, which is what a `kind: tool` entry has to answer for:

  1. the only file of each bundle that moved is rules_lib.py (every other file's sha256/16 is the reading's);
  2. rules_lib.py at the reading is the file at the named commit (its sha256/16 is the one the bundle recorded);
  3. with docstrings removed, the two versions' syntax trees differ only in the top-level definitions listed as
     changed and added, and none is removed;
  4. no file of either bundle other than rules_lib.py reaches any changed or added name through the module
     (an attribute of a name bound to rules_lib, or a `from rules_lib import` of it).

Usage (from the worktree root): tool_compat.py <commit holding the readings' rules_lib.py> <verdict> [<verdict> ...]
It prints one line per writer: tool, then, now, and the names, and exits non-zero if any step fails.
"""
import ast, hashlib, json, os, subprocess, sys

TOOLS = 'v2/ecad/tools'
sys.path.insert(0, TOOLS)
import verdict as V

commit, verdicts = sys.argv[1], sys.argv[2:]
sha16 = lambda b: hashlib.sha256(b).hexdigest()[:16]


def stripped(src):
    tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body \
           and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], 'value', None), ast.Constant) \
           and isinstance(n.body[0].value.value, str):
            n.body = n.body[1:] or [ast.Pass()]
    return tree


def top(tree):
    out = {}
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): names = [n.name]
        elif isinstance(n, ast.Assign): names = [t.id for t in n.targets if isinstance(t, ast.Name)]
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name): names = [n.target.id]
        elif isinstance(n, (ast.Import, ast.ImportFrom)): names = ['import:' + ast.dump(n)]
        else: names = ['stmt:' + ast.dump(n)]
        for k in names: out[k] = ast.dump(n)
    return out


def reached(path):
    """The names of rules_lib a module reaches: attributes of a name bound to it, and names imported from it."""
    tree = ast.parse(open(path, encoding='utf-8').read())
    alias, names = set(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == 'rules_lib': alias.add(a.asname or a.name)
        elif isinstance(n, ast.ImportFrom) and n.module == 'rules_lib':
            names |= {a.name for a in n.names}
    for n in ast.walk(tree):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in alias: names.add(n.attr)
    return names


then_src = subprocess.run(['git', 'show', '%s:%s/rules_lib.py' % (commit, TOOLS)], capture_output=True, check=True).stdout
now_src = open(os.path.join(TOOLS, 'rules_lib.py'), 'rb').read()
a, b = top(stripped(then_src)), top(stripped(now_src))
changed = sorted(k for k in a if k in b and a[k] != b[k]); added = sorted(k for k in b if k not in a)
removed = sorted(k for k in a if k not in b)
assert not removed, removed
assert all(not k.startswith(('stmt:', 'import:')) for k in changed + added), (changed, added)
ok = True
seen = {}
for vp in verdicts:
    d = json.load(open(vp)); cb = d['code_bundle']; w = d['writer']['file']
    if (w, cb['sha16']) in seen: continue
    cur = V.code_bundle(os.path.join(TOOLS, w), TOOLS)
    moved = sorted(f for f in set(cb['files']) | set(cur['files']) if cb['files'].get(f) != cur['files'].get(f))
    assert moved == ['rules_lib.py'], (w, moved)
    assert cb['files']['rules_lib.py'] == sha16(then_src), (w, 'the reading was not written with the file at %s' % commit)
    hit = {}
    for f in cur['files']:
        if f == 'rules_lib.py': continue
        r = reached(os.path.join(TOOLS, f)) & set(changed + added)
        if r: hit[f] = sorted(r)
    if hit: ok = False
    seen[(w, cb['sha16'])] = cur['sha16']
    print('%s then %s now %s; moved: rules_lib.py (%s -> %s); changed: %s; added: %s; reached by the bundle: %s'
          % (w, cb['sha16'], cur['sha16'], sha16(then_src), sha16(now_src), ', '.join(changed), ', '.join(added),
             hit or 'none'))
sys.exit(0 if ok else 1)
