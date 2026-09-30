#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3 once the requirements baseline's acceptance is filed (MESHSAT-1357, 30 September 2026): the
layer reads COMPLETE, its gate's independent-check row MET on the filed checks (the engineering collaborator's two, not
accepted, and Claude's check 3, accepted, not a model review), the status level "requirements baseline validated and
accepted" holding on l3r2.yaml's `baseline_acceptance`, and the completion statuses naming the accepted revision. The
revision is read from `baseline_acceptance`, never typed; the fourth gate row's state is read from REQUIREMENTS-L3-R2.md's
live gate. Each replaced text is located by its own words and asserted to occur exactly once; nothing else changes. It
refuses unless `baseline_acceptance` is filed and authorised by D-39, and a second run is refused. No dash is written.

Usage: python3 v2/docs/records/l3r5/apply_layer_status_l3_accept.py (from the repository root)"""
import os, sys
import yaml
sys.dont_write_bytecode = True
PAGE = "v2/docs/handover/LAYER-STATUS.md"
DATA = "v2/docs/handover/layer3/l3r2.yaml"
SPEC = "v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md"


def refuse(m): print("apply_layer_status_l3_accept: REFUSED: %s" % m); sys.exit(1)


def main():
    if not os.path.exists(PAGE): refuse("run from the repository root")
    acc = yaml.safe_load(open(DATA, encoding="utf-8")).get("baseline_acceptance")
    if not acc: refuse("baseline_acceptance is not filed: the acceptance comes first")
    if str(acc.get("authorised_by")) != "D-39": refuse("baseline_acceptance is not authorised by D-39")
    rev = str(acc["revision"])[:8]
    if "| An independent check accepts the handover | MET |" not in open(SPEC, encoding="utf-8").read():
        refuse("the live gate does not read the independent check MET")
    old = open(PAGE, encoding="utf-8").read()
    if "validated and accepted at `%s`" % rev in old: refuse("the page already names the accepted revision: this script has run")
    row4_old_start = "| An independent check accepts the handover | NOT MET | CHECK-5 of L3-R2 accepted the handover as prepared with the decisions pending;"
    lines = old.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(row4_old_start)]
    if len(hits) != 1: refuse("%d fourth gate rows found, one expected" % len(hits))
    lines[hits[0]] = ("| An independent check accepts the handover | MET | the engineering collaborator's closure check "
                      "astra-check-l3r5-1 and its targeted recheck astra-check-l3r5-2 read NOT ACCEPTED, the recheck accepting "
                      "B1, B3 and M1; B2's final correction and D-22's trace are verified by Claude's check 3 (check-l3r5-3, "
                      "accepted: yes, at `a66c4e5b`; not a model review and not an Astra check; `v2/docs/records/l3r5/checks/`) |")
    new = "\n".join(lines)
    EDITS = [
        ("**Now (30 September 2026): IN_PROGRESS, reopened for the current target configuration (L3-R2).**",
         "**Now (30 September 2026): COMPLETE, the requirements baseline validated and accepted at `%s` (`baseline_acceptance` "
         "in `handover/layer3/l3r2.yaml`, authorised by D-39 once the gates passed).** Before that it was IN_PROGRESS, "
         "reopened for the current target configuration (L3-R2)." % rev),
        ("\"Requirements baseline validated and accepted\" does not yet: the targeted independent check of the closure (L3-C27) "
         "remains, after which the baseline is reported COMPLETE once the closure criteria pass (D-38); the re-issue is "
         "authorised (L3-C26).",
         "\"Requirements baseline validated and accepted\" holds: every gate condition is MET and the acceptance is filed "
         "against the verified revision `%s` after its clean-clone check and box suite passed (`baseline_acceptance`; D-39 is "
         "the owner's conditional authorisation, not itself evidence that a gate passed); the re-issue is authorised "
         "(L3-C26) and its re-stamp is L3-C63." % rev),
        ("The requirements baseline: drafted, decisions recorded, not yet validated and accepted.",
         "The requirements baseline: validated and accepted at `%s`." % rev),
    ]
    for a, b in EDITS:
        if new.count(a) != 1: refuse("%d occurrences of %r, one expected" % (new.count(a), a[:70]))
        new = new.replace(a, b)
    if any(c in new for c in ("\u2013", "\u2014")) and not any(c in old for c in ("\u2013", "\u2014")): refuse("a dash was written")
    if new == old: refuse("nothing changed")
    open(PAGE, "w", encoding="utf-8").write(new)
    print("apply_layer_status_l3_accept: layer 3 COMPLETE at %s; gate row 4 MET; status level validated and accepted" % rev)


if __name__ == "__main__":
    main()
