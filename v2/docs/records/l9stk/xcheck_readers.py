#!/usr/bin/env python3
"""Record l9stk, a cross-check for its readers (MESHSAT-1357, round 3, 4 October 2026): what L4-E11's round 9 and record l8p read
from this record's protection output and page, at the commit they read it and in this tree.

L4-E11's round 9 reads l9stk_protection.out and L9-STACKUPS.md FROM THEIR COMMIT by sha256 (R9_COMMITS and R9_GIT in
v2/docs/records/l4e11/l4e11_power.py) and applies patterns to them; record l8p reads copies of section 15, the output and the
script's constants made at a commit (its inputs/). Neither is touched by a regeneration here, and neither notices one. This
script answers the question a regeneration raises: of what they read, what reads differently in this tree's files?

It edits nothing and pins nothing. The patterns are PARSED out of the readers' sources with ast (never retyped here): every
need(o9, ...) and need(p9, ...) of L4-E11's fix19_round, the two patterns of its loop over the pair and the three, record
l8p's VALUES table, the phrases of its section 2 loop and the patterns of its budget(). Each is applied to the bytes at the
reader's commit (git show, the sha256 checked where the reader pins one) and to this tree's file, as the reader applies it
(L4-E11 collapses white space in the page; l8p matches phrases with any white space between words).

Run from the repository root: python3 v2/docs/records/l9stk/xcheck_readers.py
Exit 0: every pattern matches both and reads the same; 1: at least one differs or no longer matches (each is printed).
Desk tooling on committed files; nothing here is measured. Stdlib and git; no network, no date.
"""
import ast
import hashlib
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.dont_write_bytecode = True
L4E11 = "v2/docs/records/l4e11/l4e11_power.py"
L8P = "v2/docs/records/l8p/l8p_drafts.py"
L8P_CHK = "v2/docs/records/l8p/check_l8p_netlist.py"
OUT = "v2/docs/records/l9stk/l9stk_protection.out"
PAGE = "v2/docs/records/l9stk/L9-STACKUPS.md"
PROT = "v2/docs/records/l9stk/l9stk_protection.py"


def stop(msg):
    sys.stderr.write("xcheck_readers: REFUSED: %s\n" % msg)
    sys.exit(2)


def tree(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


def at(commit, p, want=None):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, p)], capture_output=True)
    if r.returncode != 0:
        stop("%s is not in this repository at %s" % (p, commit[:8]))
    if want is not None and hashlib.sha256(r.stdout).hexdigest() != want:
        stop("%s at %s is not the file its reader pins" % (p, commit[:8]))
    return r.stdout.decode("utf-8")


def flat(t):
    return " ".join(t.split())


def literal(node, env=None):
    """A pattern expression as its reader writes it: a literal, or a literal formatted with the names in env."""
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError):
        if env is None:
            return None
        try:
            return eval(compile(ast.Expression(node), "<pattern>", "eval"), {"__builtins__": {}}, dict(env))
        except Exception:
            return None


def l4e11_reads(src=None):
    """(input key, pattern, what) for every pattern L4-E11's fix19_round applies to o9 (the output) and p9 (the page); src is
    L4-E11's source (the tree's when None; a test passes a fixture)."""
    t = ast.parse(tree(L4E11) if src is None else src)
    consts, fn = {}, None
    for n in t.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("R9_COMMITS", "R9_GIT"):
            consts[n.targets[0].id] = ast.literal_eval(n.value)
        if isinstance(n, ast.FunctionDef) and n.name == "fix19_round":
            fn = n
    if fn is None or set(consts) != {"R9_COMMITS", "R9_GIT"}:
        stop("L4-E11's fix19_round, R9_COMMITS or R9_GIT did not read")
    reads = []

    def take(call, env=None):
        if isinstance(call.func, ast.Name) and call.func.id == "need" and len(call.args) >= 2 and isinstance(call.args[0], ast.Name) and call.args[0].id in ("o9", "p9"):
            pat = literal(call.args[1], env)
            what = literal(call.args[2], env) if len(call.args) > 2 else ""
            if pat is None:
                return False
            reads.append((call.args[0].id, pat, what or ""))
            return True
        return None
    unread = 0
    loops = [n for n in ast.walk(fn) if isinstance(n, ast.For)]
    in_loop = set()
    for lp in loops:
        vals = literal(lp.iter)
        calls = [c for c in ast.walk(lp) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == "need"
                 and c.args and isinstance(c.args[0], ast.Name) and c.args[0].id in ("o9", "p9")]
        if not calls:
            continue
        for c in calls:
            in_loop.add(id(c))
        if vals is None or not isinstance(lp.target, ast.Tuple):
            unread += len(calls)
            continue
        for v in vals:
            env = {e.id: x for e, x in zip(lp.target.elts, v)}
            for c in calls:
                if take(c, env) is False:
                    unread += 1
    for c in ast.walk(fn):
        if isinstance(c, ast.Call) and id(c) not in in_loop:
            if take(c) is False:
                unread += 1
    return consts, reads, unread


def l8p_reads():
    """(input key, pattern, what) for record l8p: its VALUES table, the phrases of its section 2 loop, its budget()'s patterns
    and the constants it checks. Its copies' commit is read from its INPUT_FILES names."""
    sp = importlib.util.spec_from_file_location("l8p_check_for_xcheck", os.path.join(ROOT, L8P_CHK))
    chk = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(chk)
    reads = [(key, chk.phrase_rx(pat), "%s %s" % (ref, src)) for _b, ref, _pre, src, pat, key in chk.VALUES]
    t = ast.parse(tree(L8P))
    files, unread = None, 0
    for n in t.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "INPUT_FILES":
            files = ast.literal_eval(n.value)
    if not files:
        stop("record l8p's INPUT_FILES did not read")
    for n in ast.walk(t):
        if isinstance(n, ast.For) and isinstance(n.target, ast.Tuple) and [getattr(e, "id", None) for e in n.target.elts] == ["pat", "what"]:
            vals = literal(n.iter)
            if vals is None:
                unread += 1
                continue
            reads += [("page", chk.phrase_rx(p), w) for p, w in vals]
        if isinstance(n, ast.FunctionDef) and n.name == "budget":
            for c in ast.walk(n):
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == "need" and c.args and isinstance(c.args[0], ast.Name) and c.args[0].id == "page":
                    pat = literal(c.args[1], {"N": r"([0-9.]+)"})
                    if pat is None:
                        unread += 1
                    else:
                        reads.append(("page", pat, literal(c.args[2]) or ""))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "search" and len(n.args) == 2 \
                and isinstance(n.args[1], ast.Subscript) and isinstance(n.args[1].value, ast.Name) and n.args[1].value.id == "texts":
            key, pat = literal(n.args[1].slice), literal(n.args[0])
            if key == "constants" and pat is not None:
                reads.append(("constants", pat, "the script's constants"))
    m = re.search(r"-([0-9a-f]{8})\.", files["out"])
    if not m:
        stop("record l8p's copies do not name their commit")
    return m.group(1), reads, unread


def compare(pat, old, new, flags):
    a, b = re.search(pat, old, flags), re.search(pat, new, flags)
    if a is None:
        return "NOT MATCHED AT THE READER'S COMMIT", None, None
    if b is None:
        return "NO LONGER MATCHES", a.group(0), None
    if a.group(0) == b.group(0):
        return "same", a.group(0), b.group(0)
    if a.groups() == b.groups() and a.groups():
        return "TEXT DIFFERS, FIGURES SAME", a.group(0), b.group(0)
    return "DIFFERS", a.group(0), b.group(0)


def main():
    bad, lines = 0, []
    p = lines.append
    consts, reads, unread = l4e11_reads()
    cm = consts["R9_COMMITS"]["l9stk"]
    old = {"o9": at(cm, OUT, consts["R9_GIT"]["l9stk_out"][2]), "p9": flat(at(cm, PAGE, consts["R9_GIT"]["l9stk_page"][2]))}
    new = {"o9": tree(OUT), "p9": flat(tree(PAGE))}
    p("xcheck_readers: what this record's readers read, at their commit and in this tree (record l9stk, MESHSAT-1357)")
    p("")
    p("1. L4-E11 ROUND 9 (l4e11_power.py fix19_round): %d patterns on l9stk_protection.out and L9-STACKUPS.md at %s" % (len(reads), cm[:8]))
    if unread:
        p("   %d pattern(s) could not be parsed out of L4-E11's source: NOT CHECKED" % unread)
        bad += unread
    same = 0
    for key, pat, what in reads:
        verdict, a, b = compare(pat, old[key], new[key], 0)
        if verdict == "same":
            same += 1
            continue
        bad += 1
        p("   %s, %s (%s): %s" % ("the output" if key == "o9" else "the page", what, pat[:70], verdict))
        p("      at %s: %s" % (cm[:8], a))
        p("      in the tree: %s" % b)
    p("   %d of %d read the same text (so the same figures) in this tree's files" % (same, len(reads)))
    p("")
    c8, reads8, unread8 = l8p_reads()
    page_old = at(c8, PAGE)
    old8 = {"page": page_old[page_old.index("## 15. "):], "out": at(c8, OUT), "constants": at(c8, PROT)}
    page_new = tree(PAGE)
    new8 = {"page": page_new[page_new.index("## 15. "):], "out": tree(OUT), "constants": tree(PROT)}
    p("2. RECORD l8p (l8p_drafts.py, check_l8p_netlist.py): %d patterns on section 15, the output and the script's constants at %s" % (len(reads8), c8))
    if unread8:
        p("   %d pattern(s) could not be parsed out of record l8p's source: NOT CHECKED" % unread8)
        bad += unread8
    same = 0
    for key, pat, what in reads8:
        verdict, a, b = compare(pat, old8[key], new8[key], re.M)
        if verdict == "same" or (verdict == "DIFFERS" and flat(a) == flat(b)):
            same += 1
            continue
        bad += 1
        p("   %s, %s: %s" % (key, what, verdict))
        p("      at %s: %s" % (c8, a))
        p("      in the tree: %s" % b)
    p("   %d of %d read the same text in this tree's files" % (same, len(reads8)))
    p("")
    p("RESULT: %s" % ("every pattern reads the same in this tree as at its reader's commit" if not bad else "%d pattern(s) differ, no longer match or were not checked" % bad))
    sys.stdout.write("\n".join(lines) + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
