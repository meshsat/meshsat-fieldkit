#!/usr/bin/env python3
"""File the layer 3 requirements baseline's acceptance as its own record: l3r2.yaml's `baseline_acceptance` (MESHSAT-1357,
layer 3 round 5, prepared 30 September 2026; bound to the reviewed content on 1 October 2026, finding L3-R04 of the
independent review the owner relayed, v2/docs/records/l3am/). The owner's clarification quoted in ruling D-39: "Record
final baseline acceptance against the verified revision after those gates pass; the ruling itself is not evidence that
they passed." So D-39 authorises and this record accepts: the renderer reads the status level VALIDATED only with both
(render_l3r2.acceptance_ok). Run by the coordinator after the promoted revision's clean-clone check and box suite pass,
never before.

  apply_l3r5_accept.py --revision <40-hex sha> --evidence <path> [<path> ...] [--date YYYY-MM-DD] [--supersede]
                       [--check] [--data PATH]

The record carries a content manifest (render_l3r2.content_manifest): the sha256 of the requirements baseline (the needs
and every record's baseline fields), of the owner brief OWNER-INSTRUCTION-2026-09-30.md, of the governing definition
change record DEFINITION-CHANGE-RECORD-L3.md, and of the acceptance policy (l3r2.yaml without baseline_acceptance and
baseline_acceptance_history). The manifest is computed from the files as the revision holds them (git show) and must
equal the content as the tree holds it now: the revision accepted is the content reviewed, and the renderer re-checks both
every time it reads the status level.

Refuses: a record already filed, unless --supersede (then the filed record is kept byte for byte, as parsed, at the end
of `baseline_acceptance_history` and the new one replaces it; --supersede with nothing filed is refused); no ruling
deciding `layer3_baseline`; any of the gate's five conditions NOT MET on the data given; the independent review's findings
still OPEN in l3r2.yaml's `review_findings`; a revision that is not a full 40-hex commit of this repository; a revision
whose files do not hold the content the tree holds now (the manifest differs); an evidence path this tree does not hold;
evidence that does not list the newest independent check of l3r2.yaml, or a newest check that is not ACCEPTED. It writes
baseline_acceptance (and, with --supersede, baseline_acceptance_history) and nothing else, reads the record back through
render_l3r2.acceptance_ok, and the pages are re-rendered after it (render_l3r2.py); the layer status follows through its
own script.
"""
import datetime
import json
import os
import re
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2"))
import l3edit as E  # noqa: E402

DATA = os.path.join(E.TOP, "v2/docs/handover/layer3/l3r2.yaml")
NULL = "baseline_acceptance: null\n"
HIST = "baseline_acceptance_history:"


def opt(argv, name):
    return argv[argv.index(name) + 1] if name in argv else None


def evidence_args(argv):
    if "--evidence" not in argv: return []
    out = []
    for a in argv[argv.index("--evidence") + 1:]:
        if a.startswith("--"): break
        out.append(a)
    return out


def flow(obj):
    """A one-line YAML flow mapping that reads back as `obj` (json is YAML's flow subset)."""
    return json.dumps(obj, ensure_ascii=False, separators=(", ", ": "), default=str)


def build(raw, revision, evidence, date, supersede=False, full=None):
    d = yaml.safe_load(raw)
    filed = d.get("baseline_acceptance")
    if filed and not supersede:
        E.refuse("baseline_acceptance is already filed: this script has run (--supersede keeps it as history and files anew)")
    if supersede and not filed: E.refuse("--supersede: no baseline_acceptance is filed, so there is nothing to supersede")
    lines = [l for l in raw.split("\n") if l.startswith("baseline_acceptance:")]
    if len(lines) != 1: E.refuse("l3r2.yaml does not hold one line baseline_acceptance")
    if not supersede and raw.count(NULL) != 1: E.refuse("l3r2.yaml does not hold one line %r" % NULL.strip())
    sys.path.insert(0, os.path.join(E.TOP, "v2", "docs", "handover", "layer3"))
    sys.path.insert(0, os.path.join(E.TOP, "v2", "ecad", "tools"))
    import render_l3r2 as RL  # noqa: E402
    import rules_lib as R  # noqa: E402
    full = full or R.load_requirements()
    rid = [r["id"] for r in full["owner_rulings"] if str(r.get("decides")) == "layer3_baseline"]
    if len(rid) != 1: E.refuse("no single ruling decides the layer 3 baseline: run apply_l3r5_d39.py first")
    if not re.fullmatch(r"[0-9a-f]{40}", revision or ""): E.refuse("--revision %r is not a full 40-hex sha" % revision)
    r = subprocess.run(["git", "-C", E.TOP, "cat-file", "-e", revision + "^{commit}"], capture_output=True)
    if r.returncode != 0: E.refuse("%s is not a commit of this repository" % revision)
    if not evidence: E.refuse("no --evidence named")
    for p in evidence:
        if os.path.isabs(p) or ".." in p.split("/") or not os.path.isfile(os.path.join(E.TOP, p)):
            E.refuse("%s is not a file this tree holds (a path relative to the repository)" % p)
    chks = d.get("independent_check") or []
    if not chks or str(chks[-1].get("verdict")).upper() != "ACCEPTED":
        E.refuse("the newest independent check in l3r2.yaml is not ACCEPTED")
    if str(chks[-1]["record"]) not in evidence: E.refuse("--evidence does not list the newest independent check %s" % chks[-1]["record"])
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date): E.refuse("--date %r is not YYYY-MM-DD" % date)
    # every closure criterion, not only the independent check: the gate's five conditions read on the data given (the
    # coordinator's acceptance-guard check of 30 September 2026 found the record could be filed with the definition
    # re-issue unfiled, the third condition NOT MET; the status level stayed DRAFTED, but no acceptance record may exist
    # while a criterion is unmet)
    unmet = [x[0] for x in RL.gate(full, RL.decided(full, d), d, RL.load_h3()) if not x[1]]
    if unmet: E.refuse("the gate reads NOT MET on %s: %s" % ("; ".join(unmet), "no acceptance while a closure criterion is unmet"))
    rf = d.get("review_findings") or {}
    if str(rf.get("state") or "").upper() == "OPEN":
        E.refuse("the independent review's findings (%s) are OPEN in l3r2.yaml's review_findings: the amendment is checked "
                 "and its findings closed before the baseline is accepted again" % ", ".join(rf.get("findings") or []))
    # the binding (L3-R04): the revision holds the content the tree holds now, and the record names that content
    at, why = RL.manifest_at(revision)
    if at is None: E.refuse("the revision %s does not hold the reviewed content: %s" % (revision[:12], why))
    now = RL.content_manifest(full, d)
    diff = RL.manifest_differs(at, now)
    if diff: E.refuse("the revision %s does not hold the content the tree holds now (%s): accept the revision that "
                      "holds it" % (revision[:12], ", ".join(diff)))
    rec = {"revision": revision, "authorised_by": rid[0], "evidence": list(evidence), "accepted_on": date, "manifest": now}
    new = raw.replace(lines[0] + "\n", "baseline_acceptance: %s\n" % flow(rec), 1)
    hist_before = d.get("baseline_acceptance_history") or []
    if supersede:
        hl = [l for l in new.split("\n") if l.startswith(HIST)]
        item = "  - %s\n" % flow(filed)
        if not hl:
            k = new.index("\nbaseline_acceptance: ") + 1
            k = new.index("\n", k) + 1
            new = new[:k] + HIST + "\n" + item + new[k:]
        else:
            if len(hl) != 1 or hl[0] != HIST: E.refuse("l3r2.yaml's %s is not one block list" % HIST)
            k = new.index(HIST + "\n") + len(HIST) + 1
            while new.startswith("  - ", k): k = new.index("\n", k) + 1
            new = new[:k] + item + new[k:]
    back = yaml.safe_load(new)
    if back.get("baseline_acceptance") != rec: E.refuse("the written record does not read back as given")
    if (back.get("baseline_acceptance_history") or []) != (hist_before + ([filed] if supersede else [])):
        E.refuse("the history does not read back as the filed record appended")
    keep = ("baseline_acceptance", "baseline_acceptance_history")
    if {k: v for k, v in back.items() if k not in keep} != {k: v for k, v in d.items() if k not in keep}:
        E.refuse("something other than baseline_acceptance and its history changed")
    ok, why = RL.acceptance_ok(full, back)
    if not ok: E.refuse("the written record does not validate: %s" % why)
    return new


def main(argv):
    path = opt(argv, "--data") or DATA
    old = open(path, encoding="utf-8").read()
    date = opt(argv, "--date") or datetime.date.today().isoformat()
    sup = "--supersede" in argv
    try:
        new = build(old, opt(argv, "--revision"), evidence_args(argv), date, supersede=sup)
    except E.Refused as e:
        print("apply_l3r5_accept: REFUSED: %s" % e)
        return 2
    print("l3r2.yaml  baseline_acceptance  filed (revision %s, %d evidence path(s), %s, content manifest of 4 entries)%s" % (
        opt(argv, "--revision"), len(evidence_args(argv)), date, "; the record it supersedes kept as history" if sup else ""))
    if "--check" in argv:
        print("apply_l3r5_accept: check only, nothing written"); return 0
    E.commit_text(path, old, new)
    print("apply_l3r5_accept: written %s; next: render_l3r2.py, then the layer status" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
