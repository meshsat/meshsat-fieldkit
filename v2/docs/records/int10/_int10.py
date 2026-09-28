"""Shared helpers of the integration set 9 apply scripts for S-99 (stream s99reg, MESHSAT-1357, 29 September 2026).

AI engineering work; prototype design, nothing built, ordered or measured. Not a script to run: the apply_*.py scripts
beside it import it.

Every script takes `--root <tree>` (default: the repository this file is in) and edits files under that root only. The
code it runs (these helpers, int7's span/fold/screen, claims_check) is always the repository's own. `write` refuses a
path whose real location is outside the real root or that is a symbolic link, so a dry run on an overlay of links
(v2/docs/records/int10/dryrun.py) can never write through to the tree it was built from.
"""
import ast, hashlib, os, re, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
CODE = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(CODE, "v2/docs/records/int7"))
import apply_check1_answers as A      # span, fold, block_at, screen (claims_check's CLAIM pattern and no dash)

REG = "v2/ecad/tools/pcb_requirements.yaml"


class Refused(SystemExit):
    pass


def refuse(name, msg):
    print("%s: REFUSED: %s" % (name, msg))
    raise Refused(2)


def root_of(argv):
    """The tree to edit: --root <dir>, or the repository this script is in."""
    if "--root" in argv:
        k = argv.index("--root")
        if k + 1 >= len(argv): raise SystemExit("--root needs a directory")
        return os.path.realpath(argv[k + 1])
    return os.path.realpath(CODE)


def rel(root, p): return os.path.join(root, p)


def read(root, p): return open(rel(root, p), encoding="utf-8").read()


def write(root, p, text):
    path = rel(root, p)
    real = os.path.realpath(path)
    if os.path.islink(path) or not real.startswith(os.path.realpath(root) + os.sep):
        raise SystemExit("write refused: %s resolves to %s, outside the root %s or through a link" % (p, real, root))
    open(path, "w", encoding="utf-8").write(text)


def sha16_text(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]


def one_space(t): return " ".join(t.split())


# ---------------------------------------------------------------- the registry's text forms (as int8 and int9 wrote them)
def add_waits(name, rec_text, rid, iid):
    """add `iid` to a record's waits_on list, or give it one (before its status line)"""
    m = re.search(r"(?m)^    waits_on: \[(.*)\]\n", rec_text)
    if m:
        have = [x.strip() for x in m.group(1).split(",") if x.strip()]
        if iid in have: refuse(name, "%s already waits on %s" % (rid, iid))
        return rec_text[:m.start()] + "    waits_on: [%s]\n" % ", ".join(have + [iid]) + rec_text[m.end():]
    s = re.search(r"(?m)^    status: ", rec_text)
    if not s: refuse(name, "%s has neither a waits_on nor a status line" % rid)
    return rec_text[:s.start()] + "    waits_on: [%s]\n" % iid + rec_text[s.start():]


def add_evidence(name, rec_text, rid, entry):
    """append one folded entry at the end of a record's evidence list"""
    m = re.search(r"(?m)^    evidence:\n", rec_text)
    if not m: refuse(name, "%s carries no evidence list" % rid)
    tail = rec_text[m.end():]
    k = re.search(r"(?m)^    [a-z_]+:", tail)
    end = m.end() + (k.start() if k else len(tail))
    return rec_text[:end] + "      - >-\n" + A.fold(entry, 10, 120) + rec_text[end:]


def rebind_line(name, rec_text, rid, path, was16, now16):
    """replace the one evidence_bound_to entry path@was16 by path@now16 (the prose of older entries keeps its sha)"""
    old = '      - "%s@%s"\n' % (path, was16)
    if rec_text.count(old) != 1: refuse(name, "%s: the binding %s@%s is not one list entry" % (rid, path, was16))
    return rec_text.replace(old, '      - "%s@%s"\n' % (path, now16), 1)


def bound_records(reg_obj, path):
    """{record id: sha16} for every record bound to `path` by evidence_bound_to"""
    out = {}
    for r in reg_obj["records"]:
        for b in r.get("evidence_bound_to") or []:
            if str(b).startswith(path + "@"): out[r["id"]] = str(b).split("@", 1)[1]
    return out


def compare_records(name, before, after, want):
    """every record unchanged but the fields `want` names ({id: set of fields}); the result never moves"""
    recs = {r["id"]: r for r in before["records"]}
    rb = {r["id"]: r for r in after["records"]}
    if list(recs) != list(rb): refuse(name, "the record list changed")
    for k in recs:
        d = {f for f in set(recs[k]) | set(rb[k]) if recs[k].get(f) != rb[k].get(f)}
        if d != set(want.get(k, set())): refuse(name, "record %s: fields changed %s, expected %s" % (k, sorted(d), sorted(want.get(k, set()))))
        if rb[k].get("evidence_result") != recs[k].get("evidence_result"): refuse(name, "%s's result moved" % k)


# ---------------------------------------------------------------- where a generator defines a part, a rail or a net
def _first_name(call):
    if not call.args: return None
    a = call.args[0]
    if isinstance(a, ast.Constant) and isinstance(a.value, str): return a.value
    if isinstance(a, ast.BinOp) and isinstance(a.op, ast.Mod) and isinstance(a.left, ast.Constant) and isinstance(a.left.value, str):
        return a.left.value
    return None


def _func(call):
    f = call.func
    return f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)


def calls(src, funcs, first):
    """[(lineno, end_lineno, node)] of the calls of any function in `funcs` whose first argument is `first` (a string
    constant, or the format string of `"J_5V_S%d" % n`)"""
    out = []
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Call) and _func(n) in funcs and _first_name(n) == first:
            out.append((n.lineno, n.end_lineno, n))
    return sorted(out, key=lambda x: x[0])


def one_call(name, src, funcs, first, where):
    c = calls(src, funcs, first)
    if len(c) != 1: refuse(name, "%s: %d calls of %s define %r, one expected" % (where, len(c), "/".join(funcs), first))
    return c[0]


def span_text(pairs):
    """'a-b' for a call on several lines, 'a' for one; several calls joined by ', ' in line order, adjacent ones merged"""
    rs = []
    for a, b in sorted(pairs):
        if rs and a <= rs[-1][1] + 1: rs[-1][1] = max(rs[-1][1], b)
        else: rs.append([a, b])
    return ", ".join(("%d" % a) if a == b else ("%d-%d" % (a, b)) for a, b in rs)


def const_strings(node):
    return {c.value for c in ast.walk(node) if isinstance(c, ast.Constant) and isinstance(c.value, str)}


def kw(call, key):
    for k in call.keywords:
        if k.arg == key: return k.value
    return None


def dict_key_line(dict_node, key):
    for k in dict_node.keys:
        if isinstance(k, ast.Constant) and k.value == key: return k.lineno
    return None
