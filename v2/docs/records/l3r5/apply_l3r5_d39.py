#!/usr/bin/env python3
"""Record the owner's conditional closure authorisation for layer 3 as owner ruling D-39 (`decides: layer3_baseline`,
MESHSAT-1357, layer 3 round 5, 30 September 2026): three sentences of his closure instructions already filed (two of
D-38's paragraphs and the last paragraph of D-28's clarification) and his clarification of the same evening, "My
instruction authorizes closure once the agreed criteria pass. Record final baseline acceptance against the verified
revision after those gates pass; the ruling itself is not evidence that they passed." Applied once: a second run
refuses. It changes no requirement.

The ruling is a CONDITIONAL authorisation (the session's reading, labelled as such in the ruling and in the instruction
file): it is not evidence that any gate passed. The baseline's acceptance is a separate record, l3r2.yaml's
`baseline_acceptance`, filed by apply_l3r5_accept.py against the verified revision after the gates pass; the renderer
reads the status level VALIDATED only with both (render_l3r2.status_level). The four quotes are asserted in
v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md before anything is written.

Usage: python3 apply_l3r5_d39.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "l3r2"))
import l3edit as E  # noqa: E402

INSTR = "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md"
ACCEPT = "v2/docs/records/l3r5/apply_l3r5_accept.py"
QUOTES = ["Once the criteria pass, report 'Layer 3 requirements baseline: COMPLETE' and start Layer 4 architecture work immediately.",
          "When the closure criteria pass, integrate the baseline, update EXECUTION-PLAN.md and start Layer 4 immediately.",
          "If a genuine unresolved owner decision prevents closure, finish everything else and identify only the exact conflicting requirement and decision needed. Do not manufacture 100% completion, but do not keep us in review loops over an ordinary, explicitly accepted runtime trade-off.",
          "My instruction authorizes closure once the agreed criteria pass. Record final baseline acceptance against the verified revision after those gates pass; the ruling itself is not evidence that they passed."]
RID = "D-39"
TITLE = ("the owner's conditional closure authorisation: the layer 3 baseline reported COMPLETE once the agreed criteria "
         "pass, its acceptance recorded against the verified revision (30 September 2026)")
READING = ("The session's reading, not his words: D-39 is a CONDITIONAL authorisation. It authorises reporting 'Layer 3 "
           "requirements baseline: COMPLETE' and starting layer 4 once the agreed closure criteria pass; it is not evidence "
           "that any gate passed. The final baseline acceptance is a separate record, "
           "v2/docs/handover/layer3/l3r2.yaml's baseline_acceptance, filed against the verified revision after the gates "
           "pass by " + ACCEPT + "; until it is filed the requirements baseline reads DRAFTED, not VALIDATED.")
RULING = ("The owner's closure instructions of 30 September 2026 and his clarification of the same evening, relayed by the "
          "coordinating session and quoted in " + INSTR + "; the ruling that decides the layer 3 baseline's closure. It "
          "changes no requirement. In his words, from the instructions: \"" + QUOTES[0] + "\" \"" + QUOTES[1] + "\" \"" +
          QUOTES[2] + "\" And, clarifying them: \"" + QUOTES[3] + "\" " + READING)
ENTRY = '''  - id: {rid}
    authority: OWNER
    ruled_on: "2026-09-30"
    title: "{title}"
    decides: layer3_baseline
    words: >-
{words}    ruling: >-
{ruling}    source: ["owner ruling {rid}", "{instr}"]
'''


def build(raw):
    d = E.parse(raw)
    if any(r.get("title") == TITLE for r in d["owner_rulings"]): E.refuse("the authorisation is already recorded: this script has run")
    if any(str(r.get("decides")) == "layer3_baseline" for r in d["owner_rulings"]):
        E.refuse("a ruling already decides the layer 3 baseline")
    if not any(r["id"] == "D-38" and str(r.get("decides")) == "definition_reissue" for r in d["owner_rulings"]):
        E.refuse("D-38 does not decide the definition re-issue: run apply_l3r5_d38.py first")
    nid = E.next_id(d, "D", ("owner_rulings",))
    if nid != RID: E.refuse("the next free owner ruling is %s, not %s: the pages cite %s" % (nid, RID, RID))
    E.assert_in(INSTR, QUOTES + ['"%s"' % QUOTES[3]])
    E.assert_in(INSTR, ["as owner ruling D-39, the ruling that decides the layer 3 baseline's closure", "a CONDITIONAL authorisation"])
    for t in (TITLE, RULING): E.screen(t, RID)
    return E.insert_after_entry(raw, d["owner_rulings"][-1]["id"], ENTRY.format(
        rid=RID, title=TITLE, words=E.fold(" ".join(QUOTES), 6), ruling=E.fold(RULING, 6), instr=INSTR), "owner_rulings")


def main(argv):
    path = argv[argv.index("--registry") + 1] if "--registry" in argv else E.REGISTRY
    old = open(path, encoding="utf-8").read()
    try:
        new = build(old)
        got = set(E.diff_entries(E.parse(old), E.parse(new)))
        if got != {("owner_rulings", RID, "added")}: E.refuse("the entries changed are not the list: %s" % sorted(got))
        r = next(x for x in E.parse(new)["owner_rulings"] if x["id"] == RID)
        if str(r.get("decides")) != "layer3_baseline" or str(r.get("ruled_on")) != "2026-09-30" or r.get("authority") != "OWNER":
            E.refuse("the entry does not decide the layer 3 baseline as the owner's on 2026-09-30")
        errs, warns = E.validate(new)
        if errs: E.refuse("the result does not validate: %s" % "; ".join(errs[:5]))
    except E.Refused as e:
        print("apply_l3r5_d39: REFUSED: %s" % e)
        return 2
    print("owner_rulings  %s     added (decides layer3_baseline, a conditional authorisation)" % RID)
    print("apply_l3r5_d39: 1 entry, validator 0 errors, %d warnings%s" % (len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r5_d39: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
