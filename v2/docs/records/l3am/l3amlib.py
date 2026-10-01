#!/usr/bin/env python3
"""Shared helpers of the layer 3 amendment's apply scripts (MESHSAT-1357, 1 October 2026; v2/docs/records/l3am/).

Every script edits text, locates each target by its own words or id (never by a line number), asserts each replaced text
occurs exactly once, re-parses the result and compares it with the parsed original: only the named keys, entries and
fields may differ. Nothing is written until every check passes, and then through l3edit.commit_text, which refuses a file
that changed while the script ran. No dash character (U+2013, U+2014) and no claim word of claims_check.py is written.
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2"))
import l3edit as E  # noqa: E402

TOP = E.TOP
DATA = os.path.join(TOP, "v2/docs/handover/layer3/l3r2.yaml")
REGISTRY = E.REGISTRY
REVIEW = "v2/docs/records/l3am/REVIEW-AS-RECEIVED.md"
DISPOSITIONS = "v2/docs/records/l3am/DISPOSITIONS.md"
RELAYED_ON = "2026-10-01"
RELAYED_ON_TEXT = "1 October 2026"
# The amendment's base (main when the amendment branched) and the files whose bytes its check reviews, besides the
# content the acceptance's manifest binds (the requirements, the owner brief, the change record, l3r2.yaml's policy): the
# code and the claims a check of the amendment reads. Views rendered or restated from these (the three pages, the trace,
# LAYER-STATUS.md, DEFINITION-STATUS.md) are not listed: their renderers' checks bind them to their inputs.
BASE = "b45d1705c816b5f9bc6bf9d14f4409545047ebd6"
AMENDMENT_FILES = (
    "v2/docs/handover/layer3/render_l3r2.py",
    "v2/docs/records/l3r5/apply_l3r5_accept.py",
    "v2/docs/records/l3am/l3amlib.py",
    "v2/docs/records/l3am/apply_l3am_findings.py",
    "v2/docs/records/l3am/apply_l3am_r01.py",
    "v2/docs/records/l3am/apply_l3am_r02.py",
    "v2/docs/records/l3am/apply_l3am_r05.py",
    "v2/docs/records/l3am/apply_layer_status_l3am.py",
    "v2/docs/records/l3am/apply_l3am_findings_closed.py",
    "v2/docs/records/l3am/DISPOSITIONS.md",
    "v2/docs/records/l3am/REVIEW-AS-RECEIVED.md",
    "v2/ecad/tools/tests/test_l3am.py",
    "v2/ecad/tools/tests/l3amfix.py",
)
Refused = E.Refused
refuse = E.refuse


def once(text, old, new, what):
    n = text.count(old)
    if n != 1: refuse("%s: %d occurrences of %r, one expected" % (what, n, old[:80]))
    return text.replace(old, new)


def insert_before_line(raw, prefix, block, what):
    """Insert `block` (whole lines) before the one line that starts with `prefix`."""
    lines = raw.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(hits) != 1: refuse("%s: %d lines start with %r, one expected" % (what, len(hits), prefix))
    return "\n".join(lines[:hits[0]] + block.rstrip("\n").split("\n") + lines[hits[0]:])


def insert_after_line(raw, prefix, block, what):
    """Insert `block` (whole lines) after the one line that starts with `prefix`."""
    lines = raw.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(hits) != 1: refuse("%s: %d lines start with %r, one expected" % (what, len(hits), prefix))
    return "\n".join(lines[:hits[0] + 1] + block.rstrip("\n").split("\n") + lines[hits[0] + 1:])


def only_keys_changed(old_raw, new_raw, keys, what="l3r2.yaml"):
    """Refuse unless the parsed YAML differs in the top-level `keys` alone ({key: 'added' or 'changed'})."""
    a, b = E.parse(old_raw), E.parse(new_raw)
    got = {}
    for k in set(a) | set(b):
        if k not in a: got[k] = "added"
        elif k not in b: got[k] = "removed"
        elif a[k] != b[k]: got[k] = "changed"
    if got != keys: refuse("%s: the keys changed are %s, not %s" % (what, sorted(got.items()), sorted(keys.items())))
    return a, b


def only_fields_changed(old_raw, new_raw, want, what="the registry"):
    """Refuse unless the registry's parsed entries differ exactly as `want`: {(section, id): [fields] or 'added'}."""
    a, b = E.parse(old_raw), E.parse(new_raw)
    got = {}
    for sec, eid, kind in E.diff_entries(a, b):
        got[(sec, eid)] = "added" if kind == "added" else (kind if kind == "removed" else E.changed_fields(a, b, sec, eid))
    if got != want: refuse("%s: the entries changed are %s, not %s" % (what, sorted(got.items()), sorted(want.items())))
    top = {k for k in set(a) | set(b) if k not in ("owner_rulings", "session_choices", "open_items", "closed_items", "records")
           and a.get(k) != b.get(k)}
    if top: refuse("%s: top-level keys changed: %s" % (what, sorted(top)))
    return a, b


def screen(text, what):
    E.screen(text, what)


def validate_registry(raw):
    errs, _w = E.validate(raw)
    if errs: refuse("the registry does not validate (%d errors): %s" % (len(errs), "; ".join(errs[:3])))


def write(path, old, new):
    E.commit_text(path, old, new)
    print("  written %s" % os.path.relpath(path, TOP))
