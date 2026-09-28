#!/usr/bin/env python3
"""Editing a Python source file through its PARSED STRUCTURE (stream w5si, 27 September 2026, MESHSAT-1357).

WHY THIS EXISTS. The first draft of this stream's change to gen_pcb_b3.py replaced a PREFIX of the one long line that
holds PATTERNS with a text ending in a '#' comment. The rest of the line became comment text, four USB pair-class
patterns vanished (40 entries to 37), the file still parsed and the draft's own check (the new text differs from the
old) still passed. The independent check of 27 September 2026 found it. A text replacement cannot see what it deletes.

WHAT THIS DOES INSTEAD, for every apply script of this stream that edits Python:
  * the file is parsed with `ast` and the node to change is LOCATED in the tree (a module-level assignment by its
    name, an element of its list, a value of its dict by key);
  * the change is made on WHOLE NODES, at the byte positions the parser gives for them, so nothing outside the node is
    touched; several edits are applied from the last to the first so that no position moves under an edit;
  * the result is parsed again, and the caller compares the evaluated structure before and after: every entry it had
    before is there, plus exactly the intended changes. `same_except` is that comparison for a list and for a dict.
"""
import ast


def parse(src):
    return ast.parse(src)


def assignment(tree, name):
    """The value node of the ONE module-level `name = ...`; an AssertionError if there is none or more than one."""
    hits = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
            and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name]
    assert len(hits) == 1, "%d module-level assignment(s) to %s, expected one" % (len(hits), name)
    return hits[0]


def _starts(src):
    """Byte offset of each line's start in the UTF-8 text (ast columns are UTF-8 byte columns)."""
    out, n = [], 0
    for line in src.encode("utf-8").split(b"\n"):
        out.append(n); n += len(line) + 1
    return out


def span(src, node):
    """(start, end) of a node as byte offsets into the UTF-8 text."""
    st = _starts(src)
    return st[node.lineno - 1] + node.col_offset, st[node.end_lineno - 1] + node.end_col_offset


def text_of(src, node):
    a, b = span(src, node)
    return src.encode("utf-8")[a:b].decode("utf-8")


def line_start(src, node):
    """Byte offset of the start of the line a node begins on (to put a whole comment line above a statement)."""
    return _starts(src)[node.lineno - 1]


def apply(src, edits):
    """The text with every (start, end, new text) applied, positions being byte offsets into the ORIGINAL text. Edits
    may not overlap. An insertion is an edit with start == end."""
    raw = src.encode("utf-8")
    last = len(raw) + 1
    for a, b, new in sorted(edits, key=lambda e: (e[0], e[1]), reverse=True):
        assert 0 <= a <= b <= len(raw) and b <= last, "edits overlap or fall outside the text: %r" % ((a, b, new[:40]),)
        raw = raw[:a] + new.encode("utf-8") + raw[b:]
        last = a
    return raw.decode("utf-8")


def same_except(before, after, changed=None, added=None):
    """None, or what differs beyond the intended changes.
    For two LISTS: `changed` maps an entry of `before` to the entry that replaces it in place, `added` is a list of
    (entry, the entry of `before` it follows). Every other entry must be there, unchanged and in the same order.
    For two DICTS: `changed` maps a key to its new value; every other key must be there with the same value, and no
    key may be added or lost."""
    changed, added = dict(changed or {}), list(added or [])
    if isinstance(before, dict):
        if set(before) != set(after): return "keys differ: lost %s, gained %s" % (sorted(set(before) - set(after)), sorted(set(after) - set(before)))
        for k in before:
            want = changed[k] if k in changed else before[k]
            if after[k] != want: return "the value of %r is not the intended one" % (k,)
        return None
    want = []
    for e in before:
        want.append(changed.get(e, e))
        for new, after_e in added:
            if after_e == e: want.append(new)
    for k in changed:
        if k not in before: return "the entry to change, %r, is not in the list" % (k,)
    for new, after_e in added:
        if after_e not in before: return "the entry to add after, %r, is not in the list" % (after_e,)
    if list(after) != want:
        lost = [e for e in want if e not in after]; gained = [e for e in after if e not in want]
        return "the list is not the old one with the intended changes: %d entries before, %d intended, %d after; lost %s, gained %s" % (
            len(before), len(want), len(after), lost, gained)
    return None
