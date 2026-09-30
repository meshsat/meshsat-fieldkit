#!/usr/bin/env python3
"""Text-level editing helpers for the requirements registry (layer 3's second issue, L3-R2, MESHSAT-1357, 30 September
2026).

The registry is edited as text so that its comments, its folding and every entry this work does not touch stay byte for
byte (the idiom of `v2/docs/records/int7/apply_check1_answers.py`). Every edit locates its target by id and by its own
text, never by a line number, so a script built on this module runs on any integration set that carries the ids it
names. Every script that uses it re-parses the result, compares the parsed registry with the parsed original entry by
entry, and keeps `rules_lib.py requirements` at 0 errors.

Nothing here writes a file: `commit(path, old_raw, new_raw)` does, and only after the caller's checks pass.
"""
import os
import re
import subprocess
import sys
import textwrap

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))


def top():
    return subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True,
                          check=True).stdout.decode().strip()


TOP = top()
TOOLS = os.path.join(TOP, "v2/ecad/tools")
REGISTRY = os.path.join(TOOLS, "pcb_requirements.yaml")
sys.path.insert(0, TOOLS)
import claims_check as _cc  # noqa: E402

WIDTH = 120
DASHES = ("\u2013", "\u2014")


class Refused(Exception):
    pass


def refuse(msg):
    raise Refused(msg)


def screen(text, what):
    """No dash character and no claim word of claims_check.py in any text this work adds to the registry."""
    for d in DASHES:
        if d in text: refuse("%s carries a dash character" % what)
    hit = _cc.CLAIM.search(text)
    if hit: refuse("%s carries the claim word %r" % (what, hit.group(0)))


def fold(text, indent, width=WIDTH):
    body = " ".join(str(text).split())
    return "".join(" " * indent + l + "\n"
                   for l in textwrap.wrap(body, width - indent, break_on_hyphens=False, break_long_words=False))


def unfold(lines):
    return " ".join(l.strip() for l in lines if l.strip())


# ---------------------------------------------------------------------------------------------- entries and fields
def _section_bounds(raw, section):
    k = "\n%s:\n" % section
    if raw.count(k) != 1: refuse("top-level %s: occurs %d times" % (section, raw.count(k)))
    s = raw.index(k) + len(k)
    m = re.compile(r"\n(?=[^\s#])").search(raw, s)
    return s, (m.start() + 1 if m else len(raw))


def entry_span(raw, eid, section=None):
    """(start, end) of the list entry `  - id: <eid>` (a record, a ruling, a choice or an item): from its first line to
    the line before the next entry or the next top-level line. With `section`, only that top-level list is searched.
    Refuses unless the id occurs exactly once where it is searched."""
    key = "\n  - id: %s\n" % eid
    lo, hi = _section_bounds(raw, section) if section else (1, len(raw))
    n = raw.count(key, lo - 1, hi)
    if n != 1: refuse("entry %s occurs %d times in %s" % (eid, n, section or "the registry"))
    s = raw.index(key, lo - 1, hi) + 1
    ends = []
    j = raw.find("\n  - id: ", s + 5)
    if j > 0: ends.append(j + 1)
    m = re.compile(r"\n(?=[^\s#])").search(raw, s + 5)
    if m: ends.append(m.start() + 1)
    e = min(ends) if ends else len(raw)
    # blank or comment lines closing the entry belong to what follows it
    lines = raw[s:e].split("\n")
    k = len(lines)
    while k > 1 and (not lines[k - 1].strip() or lines[k - 1].lstrip().startswith("#")):
        k -= 1
    return s, s + len("\n".join(lines[:k])) + 1


def section_end(raw, section):
    """The offset of the line after the last entry of the top-level list `section:` (where a new entry is added)."""
    k = "\n%s:\n" % section
    if raw.count(k) != 1: refuse("top-level %s: occurs %d times" % (section, raw.count(k)))
    s = raw.index(k) + len(k)
    m = re.compile(r"\n(?=[^\s#])").search(raw, s)
    e = m.start() + 1 if m else len(raw)
    lines = raw[s:e].split("\n")
    k2 = len(lines)
    while k2 > 1 and (not lines[k2 - 1].strip() or lines[k2 - 1].lstrip().startswith("#")):
        k2 -= 1
    return s + len("\n".join(lines[:k2])) + 1


def _field_lines(block, field):
    lines = block.split("\n")
    idx = [i for i, l in enumerate(lines) if re.match(r"^    %s:( |$)" % re.escape(field), l)]
    if len(idx) > 1: refuse("field %s occurs %d times in one entry" % (field, len(idx)))
    if not idx: return lines, None, None
    a = idx[0]
    b = a + 1
    while b < len(lines) and lines[b].startswith("      "):
        b += 1
    return lines, a, b


def field_text(block, field):
    """The field's folded text (for `>-` scalars) or its raw value line."""
    lines, a, b = _field_lines(block, field)
    if a is None: return None
    head = lines[a].split(":", 1)[1].strip()
    if head in (">-", ">", "|", "|-"): return unfold(lines[a + 1:b])
    return head


def set_folded(block, field, text, after=None):
    """Write `field: >-` with `text` folded; an absent field is inserted after the field `after`."""
    lines, a, b = _field_lines(block, field)
    new = ("    %s: >-\n" % field + fold(text, 6)).rstrip("\n").split("\n")
    if a is None:
        if after is None: refuse("field %s is absent and no anchor was given" % field)
        _, a2, b2 = _field_lines(block, after)
        if a2 is None: refuse("anchor field %s is absent" % after)
        return "\n".join(lines[:b2] + new + lines[b2:])
    return "\n".join(lines[:a] + new + lines[b:])


def append_folded(block, field, sentence, after=None):
    old = field_text(block, field)
    if old is not None and sentence.strip() in old: refuse("field %s already carries the sentence %r" % (field, sentence[:60]))
    return set_folded(block, field, (old + " " if old else "") + sentence, after=after)


def set_flow(block, field, items):
    lines, a, b = _field_lines(block, field)
    if a is None: refuse("field %s is absent" % field)
    line = "    %s: [%s]" % (field, ", ".join(items)) if items else "    %s: []" % field
    return "\n".join(lines[:a] + [line] + lines[b:])


def flow_items(block, field):
    t = field_text(block, field)
    if t is None: return None
    m = re.match(r"^\[(.*)\]$", t)
    if not m: refuse("field %s is not a flow list: %r" % (field, t[:60]))
    return [x.strip() for x in m.group(1).split(",") if x.strip()]


def add_list_entry(block, field, text):
    """Append a `- >-` item to the block list `field` (the evidence list's form: items at six spaces, text at ten)."""
    lines, a, b = _field_lines(block, field)
    if a is None: refuse("list field %s is absent" % field)
    new = ("      - >-\n" + fold(text, 10)).rstrip("\n").split("\n")
    return "\n".join(lines[:b] + new + lines[b:])


def set_top_scalar(raw, key, value_line):
    """Replace `key: ...` (one line, top level)."""
    pat = re.compile(r"^%s: .*$" % re.escape(key), re.M)
    if len(pat.findall(raw)) != 1: refuse("top-level %s occurs %d times" % (key, len(pat.findall(raw))))
    return pat.sub(lambda m: "%s: %s" % (key, value_line), raw, count=1)


def replace_entry(raw, eid, fn, section=None):
    s, e = entry_span(raw, eid, section)
    block = raw[s:e].rstrip("\n")
    new = fn(block)
    if new == block: refuse("the edit of %s changed nothing" % eid)
    return raw[:s] + new + "\n" + raw[e:]


def remove_entry(raw, eid, section=None):
    s, e = entry_span(raw, eid, section)
    return raw[:s] + raw[e:], raw[s:e]


def insert_at_section_end(raw, section, entry_text):
    p = section_end(raw, section)
    return raw[:p] + entry_text.rstrip("\n") + "\n" + raw[p:]


def insert_after_entry(raw, eid, entry_text, section=None):
    s, e = entry_span(raw, eid, section)
    return raw[:e] + entry_text.rstrip("\n") + "\n" + raw[e:]


# ---------------------------------------------------------------------------------------------- checks
def parse(raw):
    import yaml
    return yaml.safe_load(raw)


def validate(raw, citing=None):
    """rules_lib.validate_requirements on the text (written to a temporary copy beside nothing: the parsed object is
    passed in, with the tree's own needs document, rules, decisions and interfaces)."""
    import rules_lib as R
    req = parse(raw)
    errs, warns = R.validate_requirements(req, root=TOP, citing=citing if citing is not None else ())
    return errs, warns


def entries(d):
    out = {}
    for sec in ("owner_rulings", "session_choices", "open_items", "closed_items", "records"):
        for x in d.get(sec) or []:
            out[(sec, x["id"])] = x
    return out


def diff_entries(before, after):
    """[(section, id, kind)] with kind added, removed or changed, comparing parsed entries."""
    b, a = entries(before), entries(after)
    out = []
    for k in sorted(set(b) | set(a)):
        if k not in b: out.append((k[0], k[1], "added"))
        elif k not in a: out.append((k[0], k[1], "removed"))
        elif b[k] != a[k]: out.append((k[0], k[1], "changed"))
    return out


def changed_fields(before, after, sec, eid):
    b, a = entries(before).get((sec, eid)) or {}, entries(after).get((sec, eid)) or {}
    return sorted(k for k in set(b) | set(a) if b.get(k) != a.get(k))


def next_id(d, prefix, sections):
    nums = []
    for sec in sections:
        for x in d.get(sec) or []:
            m = re.match(r"^%s-(\d+)$" % re.escape(prefix), str(x["id"]))
            if m: nums.append(int(m.group(1)))
    return "%s-%0*d" % (prefix, 2 if prefix in ("D", "SC") else 3, (max(nums) + 1) if nums else 1)


def git(*args):
    return subprocess.run(["git", "-C", TOP] + list(args), capture_output=True)


def sha16(path):
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def read(rel):
    p = os.path.join(TOP, rel)
    if not os.path.exists(p): refuse("%s is not in this tree" % rel)
    return open(p, encoding="utf-8").read()


def assert_in(rel, needles):
    """Refuse unless every needle is in the file: a registry clause about a document is written only on this read."""
    t = " ".join(" ".join(l.lstrip("> ") for l in read(rel).split("\n")).split())   # blockquote markers dropped
    for n in needles:
        if " ".join(n.split()) not in t: refuse("%s does not carry %r" % (rel, n[:80]))
    return sha16(os.path.join(TOP, rel))


def commit_text(path, old_raw, new_raw):
    cur = open(path, encoding="utf-8").read()
    if cur != old_raw: refuse("%s changed while this script ran" % path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_raw)
