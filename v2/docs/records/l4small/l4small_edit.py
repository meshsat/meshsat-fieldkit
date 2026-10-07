#!/usr/bin/env python3
"""l4small_edit.py: the one edit engine of stream l4small's apply scripts (MESHSAT-1357, worker W133, branch fnd/l4small,
7 October 2026). Not run by itself: each `apply_l4small_<name>.py` beside its record imports it and names its edits.

Why an engine: set 32 (fnd/int32, be07863b..4c8196a0) changes most of the files these edits touch, so the edits are applied by the
integrator on the integrated tree (set 33), never merged as file contents. Every edit is asserted, not assumed:
  E1 each old text occurs exactly once in its file, and the new text differs from it;
  E2 a second run is refused: when every new text is present the script says "already applied", and when any one is present
     before the run it says "partly applied" (exit 3, nothing written);
  E3 an edit keeps the file's line count (no line moves, so every line citation of the file still points at the same line),
     unless the script names it as an append at the end of the file, or marks it GROW (an insertion only, in a test module that
     no line citation reads);
  E4 an edit marked KEEP removes no character of the old text (an insertion only: the earlier words stay as labelled history,
     the house rule of record l9t5's pages since W9, test_w9l9t5);
  E5 the result re-parses: a .py file with ast, a .yaml file with yaml.safe_load, and in a .md file every changed table row keeps
     its number of cells;
  E6 nothing is written unless every file of the script passes E1 to E5 (all or nothing), and each written file reads back as the
     patched text.
Usage (through an apply script):  apply_l4small_<name>.py [ROOT] [--check | --write]
  ROOT: a repository root (default: the tree the script sits in); default --check: nothing is written, the diff is printed.
Exit 0: checked or written; 2: usage; 3: refused (E1 to E6), nothing written."""
import ast
import difflib
import hashlib
import os
import sys


class Refused(Exception):
    pass


GROW = "grow"   # an edit's keep value for a file no line citation reads (a test module): an insertion that may add lines


def _cells(line):
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return None
    return s.replace("\\|", "").count("|")


def _insertion_only(old, new):
    sm = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    return all(tag in ("equal", "insert") for tag, *_r in sm.get_opcodes())


def _reparse(rel, before, after):
    if rel.endswith(".py"):
        ast.parse(after)
    elif rel.endswith((".yaml", ".yml")):
        import yaml
        yaml.safe_load(after)
    elif rel.endswith(".md"):
        b, a = before.splitlines(), after.splitlines()
        for i, (x, y) in enumerate(zip(b, a)):
            if x != y and _cells(x) is not None and _cells(x) != _cells(y):
                raise Refused("%s line %d: a table row changed its number of cells" % (rel, i + 1))


def plan(root, edits, appends=(), extra=None):
    """edits: [(rel, old, new, keep)]; appends: [(rel, text)]; extra(texts) may return more (rel, old, new, keep) edits computed
    from the patched texts (a digest rebind). Returns {rel: (before, after)} or raises Refused."""
    rels = []
    for e in list(edits) + [(a[0],) for a in appends]:
        if e[0] not in rels:
            rels.append(e[0])
    texts = {}
    for rel in rels:
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            raise Refused("%s is not in %s" % (rel, root))
        texts[rel] = open(p, encoding="utf-8").read()
    present = [rel for rel, _o, n, _k in edits if n in texts[rel]] + [rel for rel, t in appends if t in texts[rel]]
    if present and len(present) == len(edits) + len(appends):
        raise Refused("already applied: every new text is present (a second run is refused)")
    if present:
        raise Refused("partly applied: a new text is already present in %s (nothing written)" % sorted(set(present)))
    after = dict(texts)
    for rel, o, n, keep in edits:
        if o == n:
            raise Refused("%s: an edit's new text equals its old text" % rel)
        if after[rel].count(o) != 1:
            raise Refused("%s: the old text occurs %d times, once expected: %r" % (rel, after[rel].count(o), o[:90]))
        if n.count("\n") != o.count("\n") and keep != GROW:
            raise Refused("%s: an edit changes the line count: %r" % (rel, o[:90]))
        if keep and not _insertion_only(o, n):
            raise Refused("%s: an edit marked KEEP removes text: %r" % (rel, o[:90]))
        after[rel] = after[rel].replace(o, n)
        if after[rel].count(n) != 1:
            raise Refused("%s: the new text does not occur exactly once after the edit: %r" % (rel, n[:90]))
    for rel, t in appends:
        if t in after[rel]:
            raise Refused("%s: the appended text is already there" % rel)
        if not after[rel].endswith("\n") or not t.startswith("\n") or not t.endswith("\n"):
            raise Refused("%s: an append must start a new paragraph and end with a newline" % rel)
        after[rel] = after[rel] + t
    if extra is not None:
        more = extra(texts, after)
        for rel, o, n, keep in more:
            if rel not in texts:
                p = os.path.join(root, rel)
                if not os.path.isfile(p):
                    raise Refused("%s is not in %s" % (rel, root))
                texts[rel] = after[rel] = open(p, encoding="utf-8").read()
            if o == n or after[rel].count(o) != 1 or n in after[rel] or n.count("\n") != o.count("\n"):
                raise Refused("%s: a computed edit does not hold E1 to E3: %r" % (rel, o[:90]))
            after[rel] = after[rel].replace(o, n)
    for rel in texts:
        if after[rel] == texts[rel]:
            raise Refused("%s: nothing changes" % rel)
        _reparse(rel, texts[rel], after[rel])
    return {rel: (texts[rel], after[rel]) for rel in texts}


def sha16(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def main(name, here, edits, appends=(), extra=None, argv=None):
    argv = sys.argv[1:] if argv is None else argv
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) > 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write("usage: %s.py [ROOT] [--check | --write]\n" % name)
        return 2
    root = os.path.abspath(args[0]) if args else os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here))))
    write = flags == ["--write"]
    try:
        if callable(edits):   # edits computed from the tree they apply to (a line number read at apply time)
            edits = edits(root)
        res = plan(root, edits, appends, extra)
    except (Refused, SyntaxError, ValueError) as ex:
        sys.stderr.write("%s: REFUSED: %s\n" % (name, ex))
        return 3
    except Exception as ex:   # a yaml error and the like: refused, never half-written
        sys.stderr.write("%s: REFUSED: %s: %s\n" % (name, type(ex).__name__, ex))
        return 3
    for rel, (b, a) in res.items():
        sys.stdout.writelines(difflib.unified_diff(b.splitlines(True), a.splitlines(True), "a/" + rel, "b/" + rel, n=0))
    if not write:
        print("%s: CHECK OK, %d edit(s) and %d append(s) on %d file(s), nothing written" % (name, len(edits), len(appends), len(res)))
        return 0
    for rel, (_b, a) in res.items():
        p = os.path.join(root, rel)
        tmp = p + ".l4small.tmp"
        open(tmp, "w", encoding="utf-8").write(a)
        os.replace(tmp, p)
        if open(p, encoding="utf-8").read() != a:
            sys.stderr.write("%s: REFUSED: %s does not read back as the patched text\n" % (name, rel))
            return 3
    print("%s: WRITTEN, %d edit(s) and %d append(s) on %d file(s)" % (name, len(edits), len(appends), len(res)))
    return 0
