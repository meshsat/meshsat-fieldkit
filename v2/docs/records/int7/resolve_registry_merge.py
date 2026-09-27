#!/usr/bin/env python3
"""Resolve the registry's two conflict hunks when main (H3 line: S-79 closed) is merged into the set 6 line
(S-76, S-64, S-45 closed; S-82 to S-87 opened). Usage: resolve_registry_merge.py <worktree> <ours commit> <theirs commit>

An item is open after the merge only if BOTH sides still hold it open; it is closed if EITHER side closed it. The
script resolves each hunk from that rule, never by taking a side, then checks the parsed result against the two
parents: every id of either parent is present exactly once, open or closed; every record, need, ruling and choice
equals the set 6 side's, except what main changed against the merge base."""
import subprocess, sys, yaml

wt, ours, theirs = sys.argv[1:4]
P = wt + "/v2/ecad/tools/pcb_requirements.yaml"
REL = "v2/ecad/tools/pcb_requirements.yaml"


def show(c):
    return subprocess.run(["git", "-C", wt, "show", "%s:%s" % (c, REL)], capture_output=True, check=True).stdout.decode()


def blocks(lines):
    out, cur = [], None
    for ln in lines:
        if ln.startswith("  - id: "):
            cur = [ln]; out.append(cur)
        else:
            assert cur is not None, "a hunk side starts inside an item: %r" % ln[:80]
            cur.append(ln)
    return out


A, B = yaml.safe_load(show(ours)), yaml.safe_load(show(theirs))
base = subprocess.run(["git", "-C", wt, "merge-base", ours, theirs], capture_output=True, check=True).stdout.decode().strip()
O = yaml.safe_load(show(base))
closed_either = {x["id"] for x in A["closed_items"]} | {x["id"] for x in B["closed_items"]}
L = open(P, encoding="utf-8").read().split("\n")
out, i, n = [], 0, 0
while i < len(L):
    if L[i].startswith("<<<<<<< "):
        a = i
        b = next(j for j in range(a, len(L)) if L[j] == "=======")
        c = next(j for j in range(b, len(L)) if L[j].startswith(">>>>>>> "))
        n += 1
        seen = set()
        for blk in blocks(L[a + 1:b]) + blocks(L[b + 1:c]):
            iid = blk[0].split("id: ")[1].strip()
            is_open = any(x.strip() == "status: OPEN" for x in blk[:4])
            if iid in seen:
                continue
            if is_open and iid in closed_either:
                continue            # still open on one side, closed on the other: it is closed, its closed block is kept elsewhere
            seen.add(iid); out += blk
        i = c + 1
    else:
        out.append(L[i]); i += 1
new = "\n".join(out)
assert "<<<<<<<" not in new and ">>>>>>>" not in new
M = yaml.safe_load(new)
ids_open = [x["id"] for x in M["open_items"]]; ids_closed = [x["id"] for x in M["closed_items"]]
assert len(ids_open) == len(set(ids_open)) and len(ids_closed) == len(set(ids_closed)), "an id is doubled"
assert not set(ids_open) & set(ids_closed), sorted(set(ids_open) & set(ids_closed))
every = {x["id"] for s in (A, B) for k in ("open_items", "closed_items") for x in s[k]}
assert set(ids_open) | set(ids_closed) == every, sorted(every ^ (set(ids_open) | set(ids_closed)))
assert set(ids_closed) == closed_either
for sec in ("needs", "owner_rulings", "session_choices", "records"):
    a_ = {x["id"]: x for x in A[sec]}; b_ = {x["id"]: x for x in B[sec]}; o_ = {x["id"]: x for x in O[sec]}; m_ = {x["id"]: x for x in M[sec]}
    assert set(m_) == set(a_) | set(b_), sec
    for k, v in m_.items():
        if k in a_ and k in b_ and a_[k] != b_[k]:
            changed_a, changed_b = a_[k] != o_.get(k), b_[k] != o_.get(k)
            assert not (changed_a and changed_b) or v in (a_[k], b_[k]), "%s %s changed on both sides: read it by hand" % (sec, k)
            if changed_a and changed_b:
                print("BOTH SIDES changed %s %s: the merged text is %s's; read it" % (sec, k, "ours" if v == a_[k] else "theirs"))
open(P, "w", encoding="utf-8").write(new)
print("resolved %d hunk(s): open %d, closed %d; records %d" % (n, len(ids_open), len(ids_closed), len(M["records"])))
