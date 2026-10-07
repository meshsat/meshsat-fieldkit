#!/usr/bin/env python3
"""The one engine of record l4k's apply scripts (MESHSAT-1357, worker W131, branch fnd/l4k from main be07863b, 7 October 2026).

Record l4k re-reads the DESK-gate assessment's K table (K-01 to K-28) on main be07863b and resolves each standing contradiction
in its record. A file that set 32's lineage (fnd/int32) also changes, or a file whose sha256 a shared output pins, is never edited
on this branch: each change is an apply script beside this file, run by the integrator on set 33's integrated tree, so the edit
lands once, after set 32's own edits, and the outputs that pin the file are regenerated in set 33's chain.

Every apply script hands this engine a list of edits, (path relative to the repository root, OLD, NEW), applied in order. The
engine checks everything before it writes anything:
  - OLD occurs exactly once in its file (on the tree it patches) and NEW not at all: the edit is PENDING;
  - NEW occurs exactly once and OLD not at all: the edit is APPLIED;
  - any other state refuses (exit 2), as does a mix of PENDING and APPLIED edits (a partial state);
  - every edit is in place: NEW has as many line breaks and as many table bars as OLD, so no line of the file moves and no table
    row gains or loses a cell (citations by line number elsewhere stay true);
  - NEW differs from OLD and carries no em or en dash;
  - after all edits a Python file parses (ast) and every edited file decodes as UTF-8.
All APPLIED: exit 3, nothing written (a second run). With --check: exit 0 when the write would happen, nothing written.
Otherwise the files are written, read back (each NEW present once, each OLD gone) and their sha256 before and after printed.

Usage of every script: apply_l4k_<name>.py [--root <repository root>] [--check]
Exit 0 written (or would write, with --check); 2 refused, nothing written; 3 already applied, nothing written.
These are record-text edits: they establish no electrical or thermal property, close nothing and accept nothing."""
import argparse
import ast
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
DASHES = (chr(0x2013), chr(0x2014))   # the en dash and the em dash, by code point


def _refuse(msg):
    sys.stderr.write("REFUSED (nothing written): %s\n" % msg)
    sys.exit(2)


def plan(root, edits):
    """(texts after the edits, original texts, states) for the edits on the tree at root; refuses on any bad state."""
    orig, texts, states = {}, {}, []
    for rel, old, new in edits:
        if old == new:
            _refuse("%s: the new text equals the old" % rel)
        if new.count("\n") != old.count("\n"):
            _refuse("%s: the edit moves lines (%d line breaks for %d)" % (rel, new.count("\n"), old.count("\n")))
        if new.count("|") != old.count("|"):
            _refuse("%s: the edit changes a table's cell count" % rel)
        if any(d in new for d in DASHES):
            _refuse("%s: an em or en dash in the new text" % rel)
        if rel not in texts:
            p = os.path.join(root, rel)
            if not os.path.isfile(p):
                _refuse("%s is not in the tree at %s" % (rel, root))
            orig[rel] = open(p, "rb").read()
            texts[rel] = orig[rel].decode("utf-8")
        t = texts[rel]
        no, nn = t.count(old), t.count(new)
        if no == 1 and nn == 0:
            states.append("PENDING")
            texts[rel] = t.replace(old, new, 1)
        elif no == 0 and nn == 1:
            states.append("APPLIED")
        else:
            _refuse("%s: the old text occurs %d times and the new %d (one of them once, the other never, is required): %r"
                    % (rel, no, nn, old[:70]))
    if "PENDING" in states and "APPLIED" in states:
        _refuse("a partial state: %s" % ", ".join("%s %s" % (e[0], s) for e, s in zip(edits, states)))
    for rel, t in texts.items():
        if rel.endswith(".py"):
            try:
                ast.parse(t)
            except SyntaxError as e:
                _refuse("%s does not parse after the edits: %s" % (rel, e))
    return texts, orig, states


def run(title, edits, argv=None):
    ap = argparse.ArgumentParser(description=title)
    ap.add_argument("--root", default=REPO, help="the tree to patch (default: this file's repository)")
    ap.add_argument("--check", action="store_true", help="every check, nothing written")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    texts, orig, states = plan(root, edits)
    if all(s == "APPLIED" for s in states):
        print("%s: already applied (%d edits), nothing written" % (title, len(edits)))
        return 3
    if a.check:
        print("%s: --check: %d edits PENDING, each old text found once; would write %s" % (title, len(edits), ", ".join(sorted(texts))))
        return 0
    for rel, t in texts.items():
        p = os.path.join(root, rel)
        b = t.encode("utf-8")
        with open(p + ".l4k-tmp", "wb") as f:
            f.write(b)
        os.replace(p + ".l4k-tmp", p)
        back = open(p, "rb").read()
        if back != b:
            _refuse("%s did not read back as written" % rel)
        print("%s: %s sha256 %s -> %s" % (title, rel, hashlib.sha256(orig[rel]).hexdigest()[:16], hashlib.sha256(back).hexdigest()[:16]))
    for rel, old, new in edits:
        t = open(os.path.join(root, rel), encoding="utf-8").read()
        if t.count(new) != 1 or t.count(old) != 0:
            sys.stderr.write("written, but %s does not read back with the new text once: %r\n" % (rel, new[:70]))
            return 2
    print("%s: %d edits written" % (title, len(edits)))
    return 0
