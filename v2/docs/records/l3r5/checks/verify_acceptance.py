#!/usr/bin/env python3
"""The coordinator's check that layer 3's acceptance guards keep their protections (MESHSAT-1357, 30 September 2026;
restated 1 October 2026 for the binding of the layer 3 amendment, L3-R04, and the review findings' closure), written
independently of the author's tests. Each scenario's EXPECTED outcome is written below as a literal, derived from the
agreed closure criteria (the owner's: the gate's five conditions, an independent check accepting the handover, D-39 a
conditional authorisation, and "Record final baseline acceptance against the verified revision after those gates pass;
the ruling itself is not evidence that they passed"; since 1 October 2026 also: the acceptance binds the reviewed
content, and the independent review's findings are closed by an accepted amendment check before the baseline is
accepted again), never computed by the helper under test. A refusal is read with its reason, so a scenario cannot pass
on a refusal for another cause.

What changed on 1 October 2026: S2 states a record without a content manifest (filed before the binding) and expects
DRAFTED, as the amendment's check asked (astra-check-l3am-1, its minor on this script); the scenarios that test another
criterion carry a manifest of the verified revision, so they do not read DRAFTED for want of one; S4 names the Astra
recheck by its record, not by position; S9 to S12 and A4 to A5 are the binding's and the findings' scenarios.
Usage: verify_acceptance.py <worktree> (a clean checkout with its evidence installed, HEAD holding the tree's content).
It writes nothing in the tree."""
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
RECHECK = "v2/docs/records/l3r5/checks/astra-check-l3r5-2.md"
PRE_AMENDMENT = "b4b199d0ceee6d7a632b85090fbf3bf95a602758"  # the revision accepted on 30 September 2026
MAN, why = RL.manifest_at(HEAD)
if MAN is None: sys.exit("verify_acceptance: HEAD %s holds no manifest: %s" % (HEAD[:12], why))
LEGACY = {"revision": HEAD, "authorised_by": "D-39", "evidence": [NEWEST], "accepted_on": "2026-10-01"}
ACC = dict(LEGACY, manifest=MAN)


def level(req, data):
    return RL.status_level(req, RL.decided(req, data), data, H3)[0]


def with_(data=None, req=None, **kw):
    d = copy.deepcopy(data or DATA); r = copy.deepcopy(req or REQ); d.update(kw); return r, d


rows = []
def expect(name, got, want):
    rows.append((name, got, want, got == want))

# S1 D-39 filed, no acceptance record -> not VALIDATED
r1, d1 = with_(baseline_acceptance=None); expect("S1 D-39 alone, no acceptance record", level(r1, d1), "DRAFTED")
# S2 a record without a content manifest (filed before the binding of 1 October 2026), every other criterion holding
r2, d2 = with_(baseline_acceptance=dict(LEGACY)); expect("S2 a record without a manifest binds no content", level(r2, d2), "DRAFTED")
# S2b the record with the manifest of the verified revision, every criterion holding -> VALIDATED
r2b, d2b = with_(baseline_acceptance=dict(ACC)); expect("S2b all criteria hold and the bound record is filed", level(r2b, d2b), "VALIDATED")
# S3 the record without the authorising ruling -> not VALIDATED
r3, d3 = with_(baseline_acceptance=dict(ACC)); r3["owner_rulings"] = [x for x in r3["owner_rulings"] if x["id"] != "D-39"]
expect("S3 the record but no D-39", level(r3, d3) == "VALIDATED", False)
# S4 a newer check that does not accept, filed after the accepted one -> not VALIDATED
r4, d4 = with_(baseline_acceptance=dict(ACC))
rc_entry = next(c for c in DATA["independent_check"] if c["record"] == RECHECK)
d4["independent_check"] = d4["independent_check"] + [dict(rc_entry)]
d4["baseline_acceptance"]["evidence"] = [NEWEST, RECHECK]
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
# S9 a demand changed after the acceptance (REQ-072's acceptance text) -> not VALIDATED (the binding, L3-R04)
r9, d9 = with_(baseline_acceptance=dict(ACC)); x9 = next(x for x in r9["records"] if x["id"] == "REQ-072")
x9["acceptance"] = str(x9.get("acceptance")) + " (changed after the acceptance)"
expect("S9 a demand changed after the acceptance", level(r9, d9) == "VALIDATED", False)
# S10 closure progress only (one stage of FEA-001 closed; stage status and closure evidence are not demands) -> VALIDATED
r10, d10 = with_(baseline_acceptance=dict(ACC)); x10 = next(x for x in r10["records"] if x["id"] == "FEA-001")
st = next(s for s in x10["stages"] if str(s.get("status")) == "OPEN"); st["status"] = "CLOSED"; st["closed_by"] = "a fixture closure"
expect("S10 closure progress only, the demand unchanged", level(r10, d10), "VALIDATED")
# S11 the record at the pre-amendment revision with that revision's own manifest -> not VALIDATED (it holds other content)
m11, _w = RL.manifest_at(PRE_AMENDMENT)
r11, d11 = with_(baseline_acceptance=dict(LEGACY, revision=PRE_AMENDMENT, manifest=m11))
expect("S11 the pre-amendment revision's own manifest", level(r11, d11) == "VALIDATED", False)
# S12 the pre-amendment revision named with the manifest of the content the tree holds -> not VALIDATED (it does not hold it)
r12, d12 = with_(baseline_acceptance=dict(ACC, revision=PRE_AMENDMENT))
expect("S12 a manifest the named revision does not hold", level(r12, d12) == "VALIDATED", False)

# The acceptance script, --check on copies of l3r2.yaml (it writes nothing with --check). A record is filed in the tree
# (at b4b199d0, or the acceptance at the amendment's revision once filed), so every run supersedes it.
ACCEPT = os.path.join(WT, "v2/docs/records/l3r5/apply_l3r5_accept.py")
raw = open(os.path.join(WT, "v2/docs/handover/layer3/l3r2.yaml"), encoding="utf-8").read()
lines = raw.split("\n")


def run_accept(text, evidence, revision=HEAD):
    d = tempfile.mkdtemp(prefix="acc-"); p = os.path.join(d, "l3r2.yaml"); open(p, "w", encoding="utf-8").write(text)
    r = subprocess.run([sys.executable, ACCEPT, "--data", p, "--revision", revision, "--evidence"] + evidence +
                       ["--supersede", "--check"], capture_output=True, text=True, cwd=WT)
    return r.returncode, (r.stdout + r.stderr).strip().split("\n")[-1]


def refused_for(name, rc_out, reason):
    rc, out = rc_out
    expect(name, (rc, reason in out), (2, True)); said[name] = out


said = {}
# A1 the tree's state, every criterion holding -> the record may be filed
rc, out = run_accept(raw, [NEWEST]); expect("A1 accept script, every criterion holding", rc, 0); said["A1"] = out
# A2 a newer check that does not accept, filed after the newest -> refused for that reason
k = next(i for i, l in enumerate(lines) if l.lstrip().startswith("- {record: %s," % NEWEST))
rec_line = next(l for l in lines if l.lstrip().startswith("- {record: %s," % RECHECK))
raw2 = "\n".join(lines[:k + 1] + [rec_line] + lines[k + 1:])
assert yaml.safe_load(raw2)["independent_check"][-1]["record"] == RECHECK
refused_for("A2 accept script, newest check not accepted", run_accept(raw2, [NEWEST, RECHECK]), "is not ACCEPTED")
# A3 a closure criterion unmet (the definition re-issue not filed, the gate's third condition) -> refused for that reason
dr_line = next(l for l in lines if l.startswith("definition_reissue:"))
raw3 = raw.replace(dr_line, "definition_reissue: null", 1)
assert yaml.safe_load(raw3)["definition_reissue"] is None
refused_for("A3 accept script, a gate condition unmet", run_accept(raw3, [NEWEST]), "NOT MET")
# A4 the independent review's findings not CLOSED -> refused for that reason
rf_line = next(l for l in lines if l.startswith("review_findings: {"))
head_, sep, _t = rf_line.partition(", state: ")
assert sep
raw4 = raw.replace(rf_line, head_ + ", state: OPEN}", 1)
assert yaml.safe_load(raw4)["review_findings"]["state"] == "OPEN"
refused_for("A4 accept script, review findings open", run_accept(raw4, [NEWEST]), "are OPEN")
# A5 the pre-amendment revision -> refused: the check that closed the findings read a later revision (B2)
refused_for("A5 accept script, the pre-amendment revision", run_accept(raw, [NEWEST], PRE_AMENDMENT), "does not verify")

w = max(len(r[0]) for r in rows)
for name, got, want, ok in rows: print("%-*s  got %-14s want %-14s %s" % (w, name, got, want, "OK" if ok else "WRONG"))
for n, o in said.items(): print("%s said: %s" % (n.split(" ")[0], o[:170]))
bad = [r for r in rows if not r[3]]
print("verify_acceptance: %s (%d of %d as the criteria require)" % ("PASS" if not bad else "FAIL", len(rows) - len(bad), len(rows)))
sys.exit(1 if bad else 0)
