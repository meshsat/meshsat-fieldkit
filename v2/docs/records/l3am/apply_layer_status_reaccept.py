#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3 once the baseline is accepted again after the layer 3 amendment (MESHSAT-1357, 1 October
2026). The amendment's own status script (apply_layer_status_l3am.py) wrote "Layer 3 accepted baseline; independent
review findings open (L3-R01 to L3-R05)" and the status level "requirements drafted / decisions recorded", because the
acceptance at `b4b199d0` carries no content manifest. Once the amendment's check is filed, the findings are CLOSED and
the coordinator has accepted the baseline again (apply_l3r5_accept.py --supersede) at the promoted revision of set 19,
this script restates the three passages that state it and the gate table's check row, naming the revision the record in
l3r2.yaml names and the check that closed the findings (`review_findings.checked_by`, its reviewed revision read from
the record's third line); the open status stays on the page as what the layer read until the acceptance. The findings
were closed by the coordinator's check of the amendment, not by the reviewer, and the page
says so; "design compliance verified" and "fab-ready" still do not hold.

Refuses unless l3r2.yaml's review_findings is CLOSED, its baseline_acceptance validates (render_l3r2.acceptance_ok: a
content manifest the revision holds and the tree still holds) at a revision other than `b4b199d0`, and the record at
`b4b199d0` is kept in baseline_acceptance_history; a page that does not read the open status (the amendment's status
script not run) or that already reads the accepted-again status (a second run) is refused. Each replaced text is located
by its own words and asserted to occur once in layer 3's section; nothing outside it changes. No dash is written.

Usage: python3 v2/docs/records/l3am/apply_layer_status_reaccept.py [--check] [--page PATH]   (--page: a copy)"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3amlib as L  # noqa: E402

PAGE = os.path.join(L.TOP, "v2/docs/handover/LAYER-STATUS.md")
OPEN = "Layer 3 accepted baseline; independent review findings open (L3-R01 to L3-R05)"
PRE = "b4b199d0ceee6d7a632b85090fbf3bf95a602758"
AGAIN = "Layer 3 accepted baseline, accepted again at `%s` after the amendment; independent review findings dispositioned (L3-R01 to L3-R05)"
MARK = "Layer 3 accepted baseline, accepted again at `"
NOW_OPEN = "**Now (1 October 2026): %s.**" % OPEN


def accepted():
    """(revision, l3r2 data) of the acceptance at the amendment's revision, or a refusal."""
    sys.path.insert(0, os.path.join(L.TOP, "v2", "docs", "handover", "layer3"))
    sys.path.insert(0, os.path.join(L.TOP, "v2", "ecad", "tools"))
    import render_l3r2 as RL  # noqa: E402
    import rules_lib as R  # noqa: E402
    d = RL.load_data()
    rf = d.get("review_findings") or {}
    if str(rf.get("state")) != "CLOSED": L.refuse("l3r2.yaml's review_findings is not CLOSED")
    ba = d.get("baseline_acceptance") or {}
    rev = str(ba.get("revision") or "")
    if not ba.get("manifest"): L.refuse("l3r2.yaml's baseline_acceptance carries no content manifest: the baseline is not accepted again")
    if rev == PRE: L.refuse("the acceptance names the pre-amendment revision")
    ok, why = RL.acceptance_ok(R.load_requirements(), d)
    if not ok: L.refuse("the acceptance does not validate: %s" % why)
    if PRE not in [str(h.get("revision")) for h in d.get("baseline_acceptance_history") or []]:
        L.refuse("the record at b4b199d0 is not kept in baseline_acceptance_history")
    chk = str((d.get("review_findings") or {}).get("checked_by") or "")
    head = open(os.path.join(L.TOP, chk), encoding="utf-8").read().split("\n")[:3]
    if len(head) < 3 or not head[2].startswith("reviewed-revision: "): L.refuse("%s names no reviewed revision" % chk)
    return rev, chk, head[2].split(": ", 1)[1].strip()


def edits(rev, chk, rr):
    r8 = "`%s`" % rev[:8]
    status = AGAIN % rev[:8]
    name = os.path.basename(chk)[:-3] if chk.endswith(".md") else os.path.basename(chk)
    earlier = ""
    if name != "check-l3am-3":
        earlier = (" (it replaced check-l3am-3, which had verified the amendment at `cd231260` and no longer held once a test of "
                   "the amendment was corrected; a check holds only while the amendment's files are unchanged since its revision)")
    return [
        (NOW_OPEN, "**Now (1 October 2026): %s.** From the independent review until this acceptance the layer read \"%s\"."
         % (status, OPEN)),
        ("The amendment changes the requirements registry, and the acceptance at `b4b199d0` carries no content manifest, so "
         "it binds no content: the tree reads \"requirements drafted / decisions recorded\" until the baseline is accepted "
         "again at the amendment's revision, after the amendment's check and the gates pass (D-39 remains the owner's "
         "conditional authorisation; the coordinator runs `apply_l3r5_accept.py --supersede`, the record at `b4b199d0` kept "
         "as history).",
         "The amendment changed the requirements registry, and the acceptance at `b4b199d0` carried no content manifest, so "
         "it bound no content. The amendment was then checked (`%s`, Claude's verification at `%s`, not an Astra check "
         "and not the reviewer's%s; the collaborator's two checks of it read NOT ACCEPTED) and the findings closed; after set "
         "19's clean-clone check and box suite passed on %s "
         "(`v2/docs/records/int20/README.md`), the baseline was accepted again there under D-39 (`apply_l3r5_accept.py "
         "--supersede`, its content manifest binding the registry's normative content, the owner brief, the change record "
         "and l3r2.yaml's policy), the record at `b4b199d0` kept in `baseline_acceptance_history`. The reviewer has not "
         "re-read the amendment." % (chk, rr[:8], earlier, r8)),
        ("and does not hold for the amended registry: since the binding of 1 October 2026 (L3-R04) an acceptance holds only "
         "while its revision is a commit holding the content its manifest names and the tree still holds it, and the record "
         "at `b4b199d0` names none; the level reads \"requirements drafted / decisions recorded\" until the acceptance at "
         "the amendment's revision.",
         "and holds again for the amended registry at %s: since the binding of 1 October 2026 (L3-R04) an acceptance holds "
         "only while its revision is a commit holding the content its manifest names and the tree still holds it, and the "
         "record at %s names that content (the record at `b4b199d0` named none and is kept as history)." % (r8, r8)),
        ("The requirements baseline: accepted at `b4b199d0`; %s, the amended registry accepted again only after the "
         "amendment's check and the gates." % OPEN,
         "The requirements baseline: accepted again at %s, the amended registry with its content manifest (first accepted "
         "at `b4b199d0`); %s, closed by the coordinator's check of the amendment." % (r8, status)),
        ("(check-l3r5-3, accepted: yes, at `a66c4e5b`; not a model review and not an Astra check; "
         "`v2/docs/records/l3r5/checks/`) |",
         "(check-l3r5-3, accepted: yes, at `a66c4e5b`; not a model review and not an Astra check; "
         "`v2/docs/records/l3r5/checks/`); the amendment on the independent review: the collaborator's two checks read NOT "
         "ACCEPTED, Claude's verification accepts it (%s at `%s`, `v2/docs/records/l3am/checks/`) |" % (name, rr[:8])),
    ]


def build(old, rev, chk="v2/docs/records/l3am/checks/check-l3am-3.md", rr="cd2312604f6bb810176fc6ff7ed50281b67066b4"):
    if MARK in old: L.refuse("the page already reads %r: this script has run" % MARK)
    if NOW_OPEN not in old: L.refuse("the page does not read %r: apply_layer_status_l3am.py has not run" % NOW_OPEN)
    sec_a = old.index("## Layer 3. Requirements\n"); sec_b = old.index("\n### History: layer 3 at H2 and H3", sec_a)
    new = old
    for a, b in edits(rev, chk, rr):
        if old[sec_a:sec_b].count(a) != 1: L.refuse("%d occurrences in layer 3's section of %r, one expected" % (old[sec_a:sec_b].count(a), a[:70]))
        new = L.once(new, a, b, "LAYER-STATUS.md")
        L.screen(b, "LAYER-STATUS.md")
    na = new.index("## Layer 3. Requirements\n"); nb = new.index("\n### History: layer 3 at H2 and H3", na)
    if old[:sec_a] != new[:na] or old[sec_b:] != new[nb:]: L.refuse("the page changed outside layer 3's section")
    if NOW_OPEN in new: L.refuse("the open status is still stated as the current one")
    for c in ("\u2013", "\u2014"):
        if c in new and c not in old: L.refuse("a dash character was written")
    return new


def main(argv):
    path = argv[argv.index("--page") + 1] if "--page" in argv else PAGE
    old = open(path, encoding="utf-8").read()
    try:
        rev, chk, rr = accepted()
        new = build(old, rev, chk, rr)
    except L.Refused as e:
        print("apply_layer_status_reaccept: REFUSED: %s" % e); return 2
    print("apply_layer_status_reaccept: layer 3 reads %r; the status level, the completion status and the gate's check row "
          "restated%s" % (AGAIN % rev[:8], " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv: L.write(path, old, new)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
