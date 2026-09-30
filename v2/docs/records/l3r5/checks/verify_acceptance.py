#!/usr/bin/env python3
"""The coordinator's check that layer 3's acceptance guards keep their protections (MESHSAT-1357, 30 September 2026),
written independently of the author's tests. Each scenario's EXPECTED outcome is written below as a literal, derived
from the agreed closure criteria (the owner's: the gate's five conditions, an independent check accepting the
handover, D-39 a conditional authorisation, and "Record final baseline acceptance against the verified revision after
those gates pass; the ruling itself is not evidence that they passed"), never computed by the helper under test.
Usage: verify_acceptance.py <worktree> (a clean checkout with its evidence installed). It writes nothing in the tree."""
import copy, os, subprocess, sys, tempfile
WT = sys.argv[1]
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(WT, "v2/docs/handover/layer3")); sys.path.insert(0, os.path.join(WT, "v2/ecad/tools"))
os.chdir(os.path.join(WT, "v2/ecad/tools"))
import render_l3r2 as RL, rules_lib as R
import yaml
REQ, DATA, H3 = R.load_requirements(), RL.load_data(), RL.load_h3()
HEAD = subprocess.run(["git", "-C", WT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
NEWEST = DATA["independent_check"][-1]["record"]
ACC = {"revision": HEAD, "authorised_by": "D-39", "evidence": [NEWEST], "accepted_on": "2026-09-30"}


def level(req, data):
    return RL.status_level(req, RL.decided(req, data), data, H3)[0]


def with_(data=None, req=None, **kw):
    d = copy.deepcopy(data or DATA); r = copy.deepcopy(req or REQ); d.update(kw); return r, d


rows = []
def expect(name, got, want):
    rows.append((name, got, want, got == want))

# S1 the tree as it stands: D-39 filed, no acceptance record -> not VALIDATED
expect("S1 D-39 alone, no acceptance record", level(REQ, DATA), "DRAFTED")
# S2 the acceptance record against the verified revision, every criterion holding -> VALIDATED
r2, d2 = with_(baseline_acceptance=dict(ACC)); expect("S2 all criteria hold and the record is filed", level(r2, d2), "VALIDATED")
# S3 the record without the authorising ruling -> not VALIDATED
r3, d3 = with_(baseline_acceptance=dict(ACC)); r3["owner_rulings"] = [x for x in r3["owner_rulings"] if x["id"] != "D-39"]
expect("S3 the record but no D-39", level(r3, d3) == "VALIDATED", False)
# S4 a newer check that does not accept, filed after the accepted one -> not VALIDATED
r4, d4 = with_(baseline_acceptance=dict(ACC)); d4["independent_check"] = d4["independent_check"] + [
    {"record": "v2/docs/records/l3r5/checks/astra-check-l3r5-2.md", "sha16": DATA["independent_check"][-2]["sha16"], "verdict": "NOT_ACCEPTED"}]
d4["baseline_acceptance"]["evidence"] = [NEWEST, "v2/docs/records/l3r5/checks/astra-check-l3r5-2.md"]
expect("S4 the newest check not accepted", level(r4, d4) == "VALIDATED", False)
# S5 a decision row unsettled (its ruling removed) -> not VALIDATED
r5, d5 = with_(baseline_acceptance=dict(ACC)); r5["owner_rulings"] = [x for x in r5["owner_rulings"] if x["id"] != "D-35"]
expect("S5 row L3-OD4 unsettled", level(r5, d5) == "VALIDATED", False)
# S6 the definition re-issue not filed (the third condition unmet) -> not VALIDATED
r6, d6 = with_(baseline_acceptance=dict(ACC), definition_reissue=None)
expect("S6 the definition re-issue not filed", level(r6, d6) == "VALIDATED", False)
# S7 the record names evidence the tree does not hold -> not VALIDATED
r7, d7 = with_(baseline_acceptance=dict(ACC, evidence=[NEWEST, "v2/docs/records/no-such-file.md"]))
expect("S7 evidence not in the tree", level(r7, d7) == "VALIDATED", False)
# S8 the record not listing the newest (accepted) check -> not VALIDATED
r8, d8 = with_(baseline_acceptance=dict(ACC, evidence=["v2/docs/records/l3r5/checks/astra-check-l3r5-1.md"]))
expect("S8 evidence not listing the newest check", level(r8, d8) == "VALIDATED", False)

# The acceptance script, --check on copies of l3r2.yaml (it writes nothing with --check)
ACCEPT = os.path.join(WT, "v2/docs/records/l3r5/apply_l3r5_accept.py")
raw = open(os.path.join(WT, "v2/docs/handover/layer3/l3r2.yaml"), encoding="utf-8").read()


def run_accept(text, evidence):
    d = tempfile.mkdtemp(prefix="acc-"); p = os.path.join(d, "l3r2.yaml"); open(p, "w", encoding="utf-8").write(text)
    r = subprocess.run([sys.executable, ACCEPT, "--data", p, "--revision", HEAD, "--evidence"] + evidence + ["--check"],
                       capture_output=True, text=True, cwd=WT)
    return r.returncode, (r.stdout + r.stderr).strip().split("\n")[-1]

# A1 the tree's state, every criterion holding -> the record may be filed
rc, out = run_accept(raw, [NEWEST]); expect("A1 accept script, every criterion holding", rc, 0)
# A2 the newest check not accepted (the list cut at the Astra recheck) -> refused
lines = raw.split("\n"); k = next(i for i, l in enumerate(lines) if NEWEST in l and l.lstrip().startswith("- {record:"))
raw2 = "\n".join(lines[:k] + lines[k + 1:])
rc, out = run_accept(raw2, ["v2/docs/records/l3r5/checks/astra-check-l3r5-2.md"]); expect("A2 accept script, newest check not accepted", rc, 2)
# A3 a closure criterion unmet (the definition re-issue not filed, the gate's third condition) -> refused
y = yaml.safe_load(raw); dr_line = next(l for l in lines if l.startswith("definition_reissue:"))
raw3 = raw.replace(dr_line, "definition_reissue: null", 1)
assert yaml.safe_load(raw3)["definition_reissue"] is None
rc, out3 = run_accept(raw3, [NEWEST]); expect("A3 accept script, a gate condition unmet", rc, 2)

w = max(len(r[0]) for r in rows)
for name, got, want, ok in rows: print("%-*s  got %-10s want %-10s %s" % (w, name, got, want, "OK" if ok else "WRONG"))
print("A3 said: %s" % out3[:160])
bad = [r for r in rows if not r[3]]
print("verify_acceptance: %s (%d of %d as the criteria require)" % ("PASS" if not bad else "FAIL", len(rows) - len(bad), len(rows)))
sys.exit(1 if bad else 0)
