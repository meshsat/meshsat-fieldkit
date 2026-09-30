#!/usr/bin/env python3
"""Record the owner's closure instructions of 30 September 2026 (prepare the final package, apply the choices, generate
the affected CONOPS and product-brief passages, one targeted acceptance review, close and advance) as owner ruling D-38,
the ruling that decides the definition re-issue (`decides: definition_reissue`, closure item L3-C26). MESHSAT-1357, layer
3 round 5's fix round (the engineering collaborator's closure check astra-check-l3r5-1, B3). Applied once: a second run
refuses. It changes no requirement.

The instructions reached this work through the coordinating session from three of the owner's messages and are filed,
as quoted there, in v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md; the three quotes are asserted in that file
before anything is written. The session's reading, labelled as the session's, is in the ruling text and in that file.

Usage: python3 apply_l3r5_d38.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "l3r2"))
import l3edit as E  # noqa: E402

INSTR = "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md"
RECORD = "v2/docs/handover/layer3/DEFINITION-CHANGE-RECORD-L3.md"
QUOTES = ['Prepare the final package while those choices are pending. Complete all independent Layer 3 work and required integration steps. Once I answer, apply the choices, generate the concrete revised requirements and affected CONOPS/product-brief passages, and perform one targeted acceptance review. Fix actual blocking findings and verify their changes; backlog unrelated improvements.',
          "Close and advance. Integrate the completed package through the already authorised workflow. Update EXECUTION-PLAN.md with the baseline revision, closure evidence and downstream obligations. Once the criteria pass, report 'Layer 3 requirements baseline: COMPLETE' and start Layer 4 architecture work immediately. Prioritise the internal energy architecture and power-path corrections. Do not wait for another generic review from me or jump ahead to PCB layout.",
          'When the closure criteria pass, integrate the baseline, update EXECUTION-PLAN.md and start Layer 4 immediately.']
RID = "D-38"
TITLE = "the owner's closure instructions: prepare the package, apply the choices, one targeted acceptance review, close and advance (30 September 2026)"
READING = ("The session's reading, not his words: the owner instructed that the affected CONOPS and product-brief passages be "
           "generated from his choices and accepted by one targeted acceptance review, without a further review from him; the "
           "re-issue of exactly the passages his rulings D-32 to D-37 change (" + RECORD + " and its draft) is therefore "
           "authorised by this instruction, its acceptance is the targeted independent review of layer 3's closure (L3-C27), "
           "and it may contain no change beyond those rulings. The proposed texts reach CONOPS.md and PRODUCT-BRIEF.md by "
           "their re-stamp through layers 1 and 2, an open obligation of the integrator; until then, where either document "
           "differs from the change record, the change record governs.")
RULING = ("The owner's closure instructions of 30 September 2026, relayed by the coordinating session from three of his "
          "messages and quoted in " + INSTR + "; the ruling that decides the definition re-issue (closure item L3-C26). It "
          "changes no requirement. In his words: \"" + QUOTES[0] + "\" \"" + QUOTES[1] + "\" \"" + QUOTES[2] + "\" " + READING)
ENTRY = '''  - id: {rid}
    authority: OWNER
    ruled_on: "2026-09-30"
    title: "{title}"
    decides: definition_reissue
    words: >-
{words}    ruling: >-
{ruling}    source: ["owner ruling {rid}", "{instr}", "{record}"]
'''


def build(raw):
    d = E.parse(raw)
    if any(r.get("title") == TITLE for r in d["owner_rulings"]): E.refuse("the instructions are already recorded: this script has run")
    if any(str(r.get("decides")) == "definition_reissue" for r in d["owner_rulings"]):
        E.refuse("a ruling already decides the definition re-issue")
    if not any(r["id"] == "D-37" for r in d["owner_rulings"]): E.refuse("D-37 is not in the registry: run apply_l3r5_closure.py first")
    nid = E.next_id(d, "D", ("owner_rulings",))
    if nid != RID: E.refuse("the next free owner ruling is %s, not %s: the pages cite %s" % (nid, RID, RID))
    E.assert_in(INSTR, QUOTES)
    E.assert_in(INSTR, ["The registry records them as owner ruling D-38"])
    for t in (TITLE, RULING): E.screen(t, RID)
    return E.insert_after_entry(raw, d["owner_rulings"][-1]["id"], ENTRY.format(
        rid=RID, title=TITLE, words=E.fold(" ".join(QUOTES), 6), ruling=E.fold(RULING, 6), instr=INSTR, record=RECORD), "owner_rulings")


def main(argv):
    path = argv[argv.index("--registry") + 1] if "--registry" in argv else E.REGISTRY
    old = open(path, encoding="utf-8").read()
    try:
        new = build(old)
        got = set(E.diff_entries(E.parse(old), E.parse(new)))
        if got != {("owner_rulings", RID, "added")}: E.refuse("the entries changed are not the list: %s" % sorted(got))
        r = next(x for x in E.parse(new)["owner_rulings"] if x["id"] == RID)
        if str(r.get("decides")) != "definition_reissue" or str(r.get("ruled_on")) != "2026-09-30": E.refuse("the entry does not decide the re-issue on 2026-09-30")
        errs, warns = E.validate(new)
        if errs: E.refuse("the result does not validate: %s" % "; ".join(errs[:5]))
    except E.Refused as e:
        print("apply_l3r5_d38: REFUSED: %s" % e)
        return 2
    print("owner_rulings  %s     added (decides definition_reissue)" % RID)
    print("apply_l3r5_d38: 1 entry, validator 0 errors, %d warnings%s" % (len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r5_d38: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
