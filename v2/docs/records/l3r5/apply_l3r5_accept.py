#!/usr/bin/env python3
"""File the layer 3 requirements baseline's acceptance as its own record: l3r2.yaml's `baseline_acceptance` (MESHSAT-1357,
layer 3 round 5, prepared 30 September 2026). The owner's clarification quoted in ruling D-39: "Record final baseline
acceptance against the verified revision after those gates pass; the ruling itself is not evidence that they passed."
So D-39 authorises and this record accepts: the renderer reads the status level VALIDATED only with both
(render_l3r2.acceptance_ok). Run by the coordinator after the promoted revision's clean-clone check and box suite pass,
never before; applied once: a second run refuses.

  apply_l3r5_accept.py --revision <40-hex sha> --evidence <path> [<path> ...] [--date YYYY-MM-DD] [--check] [--data PATH]

Refuses: a second run (baseline_acceptance already filed); no ruling deciding `layer3_baseline`; a revision that is not
a full 40-hex commit of this repository; an evidence path this tree does not hold; evidence that does not list the newest
independent check of l3r2.yaml, or a newest check that is not ACCEPTED. It writes one line of l3r2.yaml and nothing
else; the pages are re-rendered after it (render_l3r2.py), and the layer status follows through its own script.
"""
import datetime
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


def opt(argv, name):
    return argv[argv.index(name) + 1] if name in argv else None


def evidence_args(argv):
    if "--evidence" not in argv: return []
    out = []
    for a in argv[argv.index("--evidence") + 1:]:
        if a.startswith("--"): break
        out.append(a)
    return out


def build(raw, revision, evidence, date):
    d = yaml.safe_load(raw)
    if d.get("baseline_acceptance"): E.refuse("baseline_acceptance is already filed: this script has run")
    if raw.count(NULL) != 1: E.refuse("l3r2.yaml does not hold one line %r" % NULL.strip())
    req = E.parse(open(E.REGISTRY, encoding="utf-8").read())
    rid = [r["id"] for r in req["owner_rulings"] if str(r.get("decides")) == "layer3_baseline"]
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
    line = "baseline_acceptance: {revision: %s, authorised_by: %s, evidence: [%s], accepted_on: \"%s\"}\n" % (
        revision, rid[0], ", ".join(evidence), date)
    new = raw.replace(NULL, line)
    back = yaml.safe_load(new)
    ba = back.get("baseline_acceptance") or {}
    if (ba.get("revision"), ba.get("authorised_by"), ba.get("evidence"), str(ba.get("accepted_on"))) != (revision, rid[0], evidence, date):
        E.refuse("the written record does not read back as given")
    if {k: v for k, v in back.items() if k != "baseline_acceptance"} != {k: v for k, v in d.items() if k != "baseline_acceptance"}:
        E.refuse("something other than baseline_acceptance changed")
    return new


def main(argv):
    path = opt(argv, "--data") or DATA
    old = open(path, encoding="utf-8").read()
    date = opt(argv, "--date") or datetime.date.today().isoformat()
    try:
        new = build(old, opt(argv, "--revision"), evidence_args(argv), date)
    except E.Refused as e:
        print("apply_l3r5_accept: REFUSED: %s" % e)
        return 2
    print("l3r2.yaml  baseline_acceptance  filed (revision %s, %d evidence path(s), %s)" % (opt(argv, "--revision"), len(evidence_args(argv)), date))
    if "--check" in argv:
        print("apply_l3r5_accept: check only, nothing written"); return 0
    E.commit_text(path, old, new)
    print("apply_l3r5_accept: written %s; next: render_l3r2.py, then the layer status" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
