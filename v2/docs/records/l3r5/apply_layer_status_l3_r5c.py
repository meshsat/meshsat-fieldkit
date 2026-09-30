#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3 after the fix round on the engineering collaborator's closure check (MESHSAT-1357, layer 3
round 5's fix round, 30 September 2026; astra-check-l3r5-1, B3): the definition re-issue is authorised by owner ruling
D-38 (his closure instructions), its acceptance the targeted independent review, so the page's closure paragraph, its
copy of the gate's third and fourth rows, its status level sentence and "Whose each remaining item is" no longer say the
re-issue waits on the owner's approving ruling; the re-stamp of the two definition documents is named as the
integrator's open obligation (L3-C63). Each replaced text is located by its own words and asserted to occur exactly
once; nothing else on the page changes. The third row's state is read from REQUIREMENTS-L3-R2.md's live gate, never
declared. No dash character is written. It refuses unless D-38 decides the re-issue and l3r2.yaml files it, and a second
run is refused.

Usage: python3 apply_layer_status_l3_r5c.py [--check] [--page PATH]   (--page: a copy of the page, for the tests)
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2"))
import l3edit as E  # noqa: E402
import yaml  # noqa: E402

PAGE = os.path.join(E.TOP, "v2/docs/handover/LAYER-STATUS.md")
DATA = os.path.join(E.TOP, "v2/docs/handover/layer3/l3r2.yaml")
SPEC = os.path.join(E.TOP, "v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md")
LIVE3 = "| Contradictions and requirement-level TBDs closed | MET |"
EDITS = [
    ("**No owner decision remains**; his approval of the definition re-issue (L3-C26) and his acceptance of the baseline "
     "follow the independent check of the closure.",
     "**No owner decision remains, and no owner approval**: the definition re-issue is authorised by his closure "
     "instructions D-38 (L3-C26 CLOSED), its acceptance the targeted independent review of the closure, which follows; once the closure "
     "criteria pass, the baseline is reported COMPLETE without a further review from him (D-38). The re-stamp of the two definition "
     "documents with the approved texts is the integrator's (L3-C63); until then the change record governs where a "
     "document differs from it."),
    ("| Contradictions and requirement-level TBDs are closed | NOT MET | CFL-017 is closed (D-29) and no record reads TBD; "
     "the definition re-issue is drafted (`handover/layer3/DEFINITION-REISSUE-DRAFT.md` and its change record) and waits on "
     "the owner's approving ruling (L3-C26) |",
     "| Contradictions and requirement-level TBDs are closed | MET | CFL-017 is closed (D-29) and no record reads TBD; the "
     "definition re-issue (`handover/layer3/DEFINITION-REISSUE-DRAFT.md` and its change record) is authorised by owner "
     "ruling D-38, his closure instructions, its acceptance the targeted independent review that follows (L3-C26 CLOSED); the "
     "re-stamp of both documents through layers 1 and 2 is L3-C63, the change record governing where a document differs "
     "until then |"),
    ("| An independent check accepts the handover | NOT MET | CHECK-5 of L3-R2 accepted the handover as prepared with the "
     "decisions pending; the decided issue, this closure, is checked again (L3-C27) |",
     "| An independent check accepts the handover | NOT MET | CHECK-5 of L3-R2 accepted the handover as prepared with the "
     "decisions pending; the engineering collaborator's closure check astra-check-l3r5-1 (`v2/docs/records/l3r5/checks/`) "
     "read NOT ACCEPTED with B1 to B3 and two minors, answered in round 5's fix round; the targeted recheck of the fixed "
     "closure is next (L3-C27) |"),
    ("\"Requirements baseline validated and accepted\" does not yet: the independent check of the closure, the owner's "
     "approval of the re-issue (L3-C26) and his acceptance of the baseline remain.",
     "\"Requirements baseline validated and accepted\" does not yet: the targeted independent check of the closure "
     "(L3-C27) remains, after which the baseline is reported COMPLETE once the closure criteria pass (D-38); the "
     "re-issue is authorised (L3-C26)."),
    ("The owner: no decision (D-29's test finds no contradiction between mandatory owner requirements); the approval of "
     "the definition re-issue's change record (L3-C26) and his acceptance of the baseline, after the independent check of "
     "the closure.",
     "The owner: no decision (D-29's test finds no contradiction between mandatory owner requirements) and no approval: "
     "the definition re-issue's change record is authorised by his closure instructions D-38 (L3-C26), its acceptance the "
     "targeted independent review; once the closure criteria pass, the baseline is reported COMPLETE without a further review from him (D-38)."),
    ("the CONOPS and product brief passages the decisions change, prepared for the owner's approval (L3-C26);",
     "the CONOPS and product brief passages the decisions change, generated and authorised (L3-C26);"),
    ("The integrator: the scripts and renders on the integration set (L3-C28).",
     "The integrator: the scripts and renders on the integration set (L3-C28), and the re-stamp of CONOPS.md and "
     "PRODUCT-BRIEF.md with the approved change record's texts through layers 1 and 2 (L3-C63)."),
]


def build(page):
    if EDITS[0][1] in page: E.refuse("the page already carries the fix round's texts: this script has run")
    data = yaml.safe_load(open(DATA, encoding="utf-8"))
    dr = data.get("definition_reissue")
    if not dr: E.refuse("l3r2.yaml's definition_reissue is not filed")
    req = E.parse(open(E.REGISTRY, encoding="utf-8").read())
    rul = next((r for r in req["owner_rulings"] if r["id"] == "D-38"), None)
    if rul is None or str(rul.get("decides")) != "definition_reissue" or str(dr.get("approved_by")) != "D-38":
        E.refuse("D-38 does not decide the re-issue, or definition_reissue names another ruling")
    if LIVE3 not in open(SPEC, encoding="utf-8").read():
        E.refuse("REQUIREMENTS-L3-R2.md's live gate does not read the third condition MET: the copy is not written")
    for old, new in EDITS:
        if page.count(old) != 1: E.refuse("the text %r is not on the page exactly once" % old[:70])
        for d in E.DASHES:
            if d in new: E.refuse("a written text carries a dash character")
        page = page.replace(old, new)
    return page


def main(argv):
    path = argv[argv.index("--page") + 1] if "--page" in argv else PAGE
    old = open(path, encoding="utf-8").read()
    try:
        new = build(old)
    except E.Refused as e:
        print("apply_layer_status_l3_r5c: REFUSED: %s" % e)
        return 2
    print("apply_layer_status_l3_r5c: %d text(s) replaced%s" % (len(EDITS), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_layer_status_l3_r5c: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
