"""The requirements registry compared entry by entry across the re-baseline of layer 3 (27 September 2026, MESHSAT-1357,
branch fnd/l3rb). Run from the repository root; read-only; prints what rebaseline_difference.out holds.

Three steps, each a git revision of v2/ecad/tools/pcb_requirements.yaml, the last the working file:
  VERIFIED  3e4799eb  the file the narrow verification of the targeted fix read
                      (v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md)
  BASE      ef144760  main when the re-baseline started; its registry is the finalizer's 6b2a9965 (the reversal)
  FIX       a54b793b  S-80's wording fix and S-81 (v2/docs/records/l3rb/apply_fix.py)
  WORKING   the file on disk, written by v2/docs/records/l3rb/apply_baseline.py (the baseline commit's registry)

It compares every section (needs, owner_rulings, session_choices, open_items, closed_items, records and the top-level
keys) field by field, and the YAML comment lines, which a parse does not see, line by line. It asserts that BASE to FIX
changes only CON-010's newest evidence entry (and only its end), adds S-81 and changes header comment lines; that FIX to
WORKING changes only baseline_state and baseline_reviews, moves S-51, S-78 and S-80 from the open to the closed items
and changes comment lines; and that from VERIFIED to WORKING no record's kind, statement, acceptance, applicability,
allocation, verification, status, evidence_result or release effect differs.
"""
import difflib, subprocess, sys

import yaml

P = "v2/ecad/tools/pcb_requirements.yaml"
SECTIONS = ("needs", "owner_rulings", "session_choices", "open_items", "closed_items", "records")
PROTECTED = ("kind", "parent", "statement", "acceptance", "tbd_effect", "allocated_to", "verification_method",
             "verification_phase", "final_phase", "prototype_1", "prototype_1_basis", "prototype_1_choice",
             "status", "evidence_result", "release_effect")


def text_at(rev):
    if rev is None:
        return open(P, encoding="utf-8").read()
    return subprocess.run(["git", "show", "%s:%s" % (rev, P)], capture_output=True, text=True, check=True).stdout


def index(d):
    out = {}
    for s in SECTIONS:
        for e in d.get(s) or []:
            out[(s, e.get("id"))] = e
    return out


def comments(t):
    return [l for l in t.split("\n") if l.lstrip().startswith("#")]


def compare(a_rev, b_rev, label):
    ta, tb = text_at(a_rev), text_at(b_rev)
    da, db = yaml.safe_load(ta), yaml.safe_load(tb)
    ia, ib = index(da), index(db)
    res = {"top": [], "added": [], "removed": [], "changed": {}, "comments": []}
    for k in sorted(set(da) | set(db)):
        if k in SECTIONS: continue
        if da.get(k) != db.get(k): res["top"].append(k)
    for k in sorted(set(ia) | set(ib)):
        if k not in ia: res["added"].append(k)
        elif k not in ib: res["removed"].append(k)
        elif ia[k] != ib[k]:
            res["changed"][k] = sorted(f for f in set(ia[k]) | set(ib[k]) if ia[k].get(f) != ib[k].get(f))
    ca, cb = comments(ta), comments(tb)
    for op in difflib.ndiff(ca, cb):
        if op[:2] in ("- ", "+ "): res["comments"].append(op[:2].strip())
    print("== %s: %s -> %s" % (label, a_rev, b_rev or "WORKING"))
    print("top-level keys changed: %s" % (", ".join(res["top"]) or "none"))
    print("entries added: %s" % (", ".join("%s/%s" % k for k in res["added"]) or "none"))
    print("entries removed: %s" % (", ".join("%s/%s" % k for k in res["removed"]) or "none"))
    for k, fs in sorted(res["changed"].items()):
        print("entry changed: %s/%s fields %s" % (k[0], k[1], ", ".join(fs)))
    if not res["changed"]: print("entries changed: none")
    print("comment lines removed %d, added %d" % (res["comments"].count("-"), res["comments"].count("+")))
    return res, ia, ib


# BASE -> FIX
r, ia, ib = compare("ef144760", "a54b793b", "S-80's wording fix")
assert r["top"] == [] and r["removed"] == []
assert r["added"] == [("open_items", "S-81")], r["added"]
assert r["changed"] == {("records", "CON-010"): ["evidence"]}, r["changed"]
ea, eb = ia[("records", "CON-010")]["evidence"], ib[("records", "CON-010")]["evidence"]
assert ea[:-1] == eb[:-1] and len(ea) == len(eb), "an entry other than the newest changed"
stem = "so this constraint's own reasons are unchanged and it stays "
assert ea[-1].split(stem)[0] == eb[-1].split(stem)[0], "the newest entry changed before its end"
print("CON-010: only the newest evidence entry changed, and only after '%s'" % stem.strip())
print("  was: ...%s" % ea[-1].split(stem)[1])
print("  now: ...%s" % eb[-1].split(stem)[1])
assert "INCONCLUSIVE, on the file at 7a834fe55aea6ccd" in ea[-1].split(stem)[1]
assert eb[-1].split(stem)[1].startswith("FAIL on W3T-F1")
assert ib[("records", "CON-010")]["evidence_result"] == "FAIL"
assert ib[("records", "CON-010")]["evidence_bound_to"] == ia[("records", "CON-010")]["evidence_bound_to"]
fix_text = text_at("a54b793b")
assert "79963b3b's re-take of the reviewed attempt's own re-read of" in fix_text
print("header: the paragraph on the targeted fix names 79963b3b's re-take (present at a54b793b)")
print()

# FIX -> WORKING
r, ia, ib = compare("a54b793b", None, "the baseline")
assert sorted(r["top"]) == ["baseline_reviews", "baseline_state"], r["top"]
assert sorted(r["removed"]) == [("open_items", "S-51"), ("open_items", "S-78"), ("open_items", "S-80")], r["removed"]
assert sorted(r["added"]) == [("closed_items", "S-51"), ("closed_items", "S-78"), ("closed_items", "S-80")], r["added"]
assert r["changed"] == {}, r["changed"]
dw = yaml.safe_load(text_at(None))
print("baseline_state: %s" % dw["baseline_state"])
for x in dw["baseline_reviews"]: print("baseline_reviews: %s" % x)
for c in dw["closed_items"]:
    if c["id"] in ("S-51", "S-78", "S-80"): print("closed: %s by %s" % (c["id"], c["closed_by"]))
print()

# VERIFIED -> WORKING, the fields a baseline protects
dv, dw = yaml.safe_load(text_at("3e4799eb")), yaml.safe_load(text_at(None))
iv, iw = index(dv), index(dw)
bad = []
for k, e in iv.items():
    if k[0] != "records": continue
    for f in PROTECTED:
        if e.get(f) != iw.get(k, {}).get(f): bad.append("%s %s" % (k[1], f))
new = [k for k in iw if k[0] == "records" and k not in iv]
print("== protected fields: 3e4799eb -> WORKING")
print("records compared %d, records added %d, protected fields differing %d" % (
    sum(1 for k in iv if k[0] == "records"), len(new), len(bad)))
for b in bad: print("  " + b)
assert not bad and not new
print("session_choices equal: %s; owner_rulings equal: %s; needs equal: %s" % (
    dv["session_choices"] == dw["session_choices"], dv["owner_rulings"] == dw["owner_rulings"],
    dv["needs"] == dw["needs"]))
assert dv["session_choices"] == dw["session_choices"] and dv["owner_rulings"] == dw["owner_rulings"]
assert dv["needs"] == dw["needs"]
print("ALL ASSERTIONS HOLD")
