"""The requirements registry's difference from the file layer 3's second release check read (27 September 2026,
MESHSAT-1357, the targeted fix of layers 1 and 3, branch fnd/h2).

The check (v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md) read v2/ecad/tools/pcb_requirements.yaml at
eb9f9030 (sha256/16 fb819e939f2895da). That branch was rebased onto main 391d8579 and 91894cd7 before it landed, and
set 5 had taken SC-51 to SC-57 and EQ-25 on main, so the reviewed SC-51 to SC-56 reached main as SC-58 to SC-63 and
EQ-25 as EQ-26. This script compares the reviewed file with the file at a commit (default HEAD), entry by entry, after
mapping those ids and removing the " as read at e3aedb25" the targeted fix appends to three gen_sch_b.py pointers
(the review's minor n1), and prints every entry that is added, removed or changed, and for each changed record the
fields that differ. It asserts what the registry header says: the renumbered choices carry the reviewed text, and no
record's statement, acceptance, applicability, allocation, verification or release effect differs.

Usage (from the repository root): python3 v2/docs/records/h2/registry_difference.py [commit]
"""
import hashlib, json, re, subprocess, sys

import yaml

P = "v2/ecad/tools/pcb_requirements.yaml"
REVIEWED = "eb9f9030"
AT = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
MAP = {"SC-%d" % o: "SC-%d" % (o + 7) for o in range(51, 57)}
MAP["EQ-25"] = "EQ-26"
KEEP = ("statement", "acceptance", "prototype_1", "prototype_1_basis", "prototype_1_choice", "allocated_to",
        "verification_method", "verification_phase", "final_phase", "release_effect", "kind", "parent", "status",
        "satisfied_by", "rule_coverage", "rulings", "choices", "waits_on", "tbd_effect", "provisional", "source")


def text(commit):
    return subprocess.run(["git", "show", "%s:%s" % (commit, P)], capture_output=True, text=True, check=True).stdout


def renumber(x):
    s = json.dumps(x, sort_keys=True, ensure_ascii=False)
    s = re.sub(r"\b(SC-5[1-6]|EQ-25)\b", lambda m: MAP[m.group(1)], s)
    return json.loads(s)


def unmark(x):
    s = json.dumps(x, sort_keys=True, ensure_ascii=False).replace(", as read at e3aedb25", "")
    return json.loads(s)


ta, tb = text(REVIEWED), text(AT)
print("reviewed %s sha256/16 %s; %s sha256/16 %s" % (REVIEWED, hashlib.sha256(ta.encode()).hexdigest()[:16], AT,
                                                     hashlib.sha256(tb.encode()).hexdigest()[:16]))
assert hashlib.sha256(ta.encode()).hexdigest()[:16] == "fb819e939f2895da"
a, b = yaml.safe_load(ta), yaml.safe_load(tb)
for k in sorted(set(a) | set(b)):
    if k in ("needs", "owner_rulings", "session_choices", "open_items", "closed_items", "records"): continue
    if a.get(k) != b.get(k): print("top-level %s: %r -> %r" % (k, a.get(k), b.get(k)))
print("needs: %s" % ("unchanged" if a["needs"] == b["needs"] else "CHANGED"))
assert a["needs"] == b["needs"]
bad = []
for sec in ("owner_rulings", "session_choices", "open_items", "closed_items", "records"):
    A = {x["id"]: x for x in a.get(sec) or []}
    B = {x["id"]: x for x in b.get(sec) or []}
    added = [k for k in B if k not in A]
    removed = [k for k in A if k not in B]
    print("%s: %d reviewed, %d at %s; added %s; removed %s" % (sec, len(A), len(B), AT, added or "none",
                                                            removed or "none"))
    for k in A:
        if k not in B or A[k] == B[k]: continue
        if sec == "session_choices" and k in MAP: continue      # the reviewed entry is MAP[k] here; k is set 5's
        ra, rb = renumber(A[k]), unmark(B[k])
        if ra == rb:
            print("  %s: renumbering only (%s)" % (k, ", ".join(sorted(set(re.findall(r"\b(?:SC-5[1-6]|EQ-25)\b",
                                                                                    json.dumps(A[k])))))))
            continue
        fields = sorted(f for f in set(ra) | set(rb) if ra.get(f) != rb.get(f))
        print("  %s: changed in %s" % (k, ", ".join(fields)))
        if sec == "records": bad += ["%s.%s" % (k, f) for f in fields if f in KEEP]
    if sec == "session_choices":
        for o in range(51, 57):
            x, y = dict(A["SC-%d" % o]), unmark(dict(B["SC-%d" % (o + 7)]))
            x.pop("id"); y.pop("id")
            same = renumber(x) == y
            print("  reviewed SC-%d is SC-%d here: %s; the id SC-%d here is set 5's entry" % (
                o, o + 7, "the same entry" if same else "DIFFERENT", o))
            assert same, o
print("record fields outside the readings that differ: %s" % (", ".join(bad) or "none"))
assert not bad, bad
