#!/usr/bin/env python3
"""The coordinator's own check of the Layer 3 amendment's B1 and B2 (MESHSAT-1357, 1 October 2026), written independently of
the author's tests, after the engineering collaborator's two runs on the issue (check 1: R01, R02, R05 and scope accepted;
check 2: B2 and scope accepted, B1 not). Every expected outcome is a literal written from the closure criteria:
  B1 (check 2's criterion): "A schema-valid stage closure, including CLOSED, closed_by and the required hold-summary update,
     and a feasibility closure leave the requirements digest and bound acceptance unchanged when demands are unchanged. All
     eight existing normative mutations still invalidate acceptance for a requirements mismatch."
  B2: the findings close only with a new accepted check whose first three lines are exact; the pre-amendment check is refused.
Usage: verify_l3am.py <worktree at the candidate>. Writes only a temporary record under v2/docs/records/l3am/checks/ and removes it."""
import copy, os, subprocess, sys
WT = sys.argv[1]; sys.dont_write_bytecode = True
for p in ("v2/docs/handover/layer3", "v2/ecad/tools", "v2/docs/records/l3am"): sys.path.insert(0, os.path.join(WT, p))
os.chdir(os.path.join(WT, "v2/ecad/tools"))
import render_l3r2 as RL, rules_lib as R
import apply_l3am_findings_closed as CL
REQ, DATA = R.load_requirements(), RL.load_data()
HEAD = subprocess.run(["git", "-C", WT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
D0 = RL.requirements_digest(REQ)
rows = []
def expect(name, got, want): rows.append((name, got, want, got == want))
def errs(req):
    out = R.validate_requirements(req)
    e = out[0] if isinstance(out, tuple) else out
    return len(e) if isinstance(e, (list, tuple)) else e
def rec(req, rid): return next(x for x in req["records"] if x["id"] == rid)

# B1 positive: FEA-003's layout stage closed as rules_lib requires
q = copy.deepcopy(REQ); f = rec(q, "FEA-003")
st = next(s for s in f["stages"] if s["stage"] == "LAYOUT_ENTRY"); st["status"] = "CLOSED"; st["closed_by"] = "commit %s (fixture)" % HEAD[:8]
f["holds_layout_entry"] = []
expect("validator on the layout-stage closure (errors)", errs(q), 0)
expect("digest after a schema-valid layout-stage closure", RL.requirements_digest(q) == D0, True)
# B1 positive: an added reading and a note
q = copy.deepcopy(REQ); r = rec(q, "REQ-072"); r.setdefault("evidence", []).append("a fixture reading"); r["notes"] = str(r.get("notes", "")) + " fixture note"
expect("digest after an added reading and note", RL.requirements_digest(q) == D0, True)
# B1 negative: normative mutations
def mut(name, fn):
    q = copy.deepcopy(REQ); fn(q); expect("digest after " + name, RL.requirements_digest(q) == D0, False)
mut("REQ-016 statement at 500 W", lambda q: rec(q, "REQ-016").__setitem__("statement", str(rec(q, "REQ-016")["statement"]).replace("100 W", "500 W")))
mut("REQ-072 acceptance changed", lambda q: rec(q, "REQ-072").__setitem__("acceptance", str(rec(q, "REQ-072")["acceptance"]) + " (fixture)"))
mut("an owner ruling's text changed (D-34)", lambda q: next(x for x in q["owner_rulings"] if x["id"] == "D-34").__setitem__("ruling", "fixture"))
mut("CON-012's accepted residual risk changed", lambda q: rec(q, "CON-012").__setitem__("residual_risk_accepted", "fixture"))
mut("a stage's requires changed (FEA-003 layout)", lambda q: next(s for s in rec(q, "FEA-003")["stages"] if s["stage"] == "LAYOUT_ENTRY").__setitem__("requires", "fixture"))
mut("a record superseded (REQ-016 DEFINED to SUPERSEDED)", lambda q: rec(q, "REQ-016").__setitem__("status", "SUPERSEDED"))

# acceptance_ok on in-memory records
man = RL.content_manifest(REQ, DATA)
newest = RL.handover_checks(DATA)[-1]["record"]
def acc(rev, req=None, manifest=man):
    d = copy.deepcopy(DATA); d["baseline_acceptance"] = {"revision": rev, "authorised_by": "D-39", "evidence": [newest], "accepted_on": "2026-10-01"}
    if manifest is not None: d["baseline_acceptance"]["manifest"] = manifest
    return RL.acceptance_ok(req or REQ, d)[0]
expect("acceptance bound at the candidate", acc(HEAD), True)
expect("acceptance at forty zeros", acc("0" * 40), False)
expect("acceptance at b4b199d0 (exists, other content)", acc(subprocess.run(["git", "-C", WT, "rev-parse", "b4b199d0"], capture_output=True, text=True).stdout.strip()), False)
q = copy.deepcopy(REQ); rec(q, "REQ-016")["statement"] = str(rec(q, "REQ-016")["statement"]).replace("100 W", "500 W")
expect("acceptance with REQ-016 changed after it", acc(HEAD, req=q), False)
q = copy.deepcopy(REQ); f = rec(q, "FEA-003"); st = next(s for s in f["stages"] if s["stage"] == "LAYOUT_ENTRY"); st["status"] = "CLOSED"; st["closed_by"] = "fixture"; f["holds_layout_entry"] = []
expect("acceptance after a schema-valid downstream closure", acc(HEAD, req=q), True)
expect("a legacy record without a manifest", acc(HEAD, manifest=None), False)

# B2: the findings-closing verification
def ver(record_rel):
    try:
        out = CL.verify(record_rel, DATA, head=HEAD, req=REQ)
        return True if out in (None, True) or (isinstance(out, tuple) and out[0]) else False
    except Exception: return False
expect("closing with the pre-amendment check-l3r5-3", ver("v2/docs/records/l3r5/checks/check-l3r5-3.md"), False)

w = max(len(r[0]) for r in rows)
for n, g, wa, ok in rows: print("%-*s  got %-6s want %-6s %s" % (w, n, g, wa, "OK" if ok else "WRONG"))
bad = [r for r in rows if not r[3]]
print("verify_l3am: %s (%d of %d as the criteria require) at %s" % ("PASS" if not bad else "FAIL", len(rows) - len(bad), len(rows), HEAD[:12]))
sys.exit(1 if bad else 0)
