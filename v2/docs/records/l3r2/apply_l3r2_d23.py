#!/usr/bin/env python3
"""Record the owner's instruction on the six-row decision table (30 September 2026) as owner ruling D-23 (MESHSAT-1357,
layer 3's second issue, third round). Applied once: a second run refuses.

The instruction reached this work through the coordinating session and is filed, as quoted there, in
v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md (its third section); every quote below is asserted in that file
before anything is written. The ruling changes no record: it is the source the pages cite for holding row L3-OD6's
recommendation and figures, for the table's form (options, recommendation, quantified consequences, dependencies, a plain
flag on an option that cannot meet the mission) and for carrying board A's current-limit resistor as two results.

Usage: python3 apply_l3r2_d23.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3edit as E  # noqa: E402

INSTR = "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md"
QUOTES = [
    "Changes to weather coverage, deployment restrictions, functionality or enclosure constraints remain proposals "
    "requiring my explicit decision. An average-day benchmark may be an option; do not select it automatically because the "
    "current design passes it.",
    "Make weather decision 6 a quantified choice ... Substantiate 'several times more energy' before recommending against "
    "an option.",
    "Update the existing six-row decision table with options, your recommendation, quantified consequences and "
    "dependencies. Put detailed calculations in the existing evidence package, linked from the table. Flag any option that "
    "cannot meet the stated mission plainly.",
    "Keep the current-limit resistor dependency explicit ... Distinguish performance of the held circuit from performance "
    "conditional on the proposed change. Track implementation and physical verification separately.",
]
RID = "D-23"
TITLE = "the owner's instruction on the six-row layer 3 decision table (30 September 2026)"
RULING = ("The owner's instruction of 30 September 2026 on the six-row decision table of layer 3's second issue, as quoted "
          "in " + INSTR + " (its two elisions are the quoting session's, marked). In his words: " +
          " ".join("\"%s\"" % q for q in QUOTES))
ENTRY = '''  - id: {rid}
    authority: OWNER
    ruled_on: "2026-09-30"
    title: "{title}"
    ruling: >-
{ruling}    source: ["owner ruling {rid}", "{instr}"]
'''


def build(raw):
    d = E.parse(raw)
    if any(r.get("title") == TITLE for r in d["owner_rulings"]): E.refuse("the instruction is already recorded: this script has run")
    if not any(r["id"] == "D-22" for r in d["owner_rulings"]): E.refuse("D-22 is not in the registry: run apply_l3r2_session.py first")
    nid = E.next_id(d, "D", ("owner_rulings",))
    if nid != RID: E.refuse("the next free owner ruling is %s, not %s: the pages cite %s" % (nid, RID, RID))
    E.assert_in(INSTR, QUOTES)
    for t in (TITLE, RULING): E.screen(t, "D-23")
    last = d["owner_rulings"][-1]["id"]
    return E.insert_after_entry(raw, last, ENTRY.format(rid=RID, title=TITLE, ruling=E.fold(RULING, 6), instr=INSTR),
                                "owner_rulings")


def main(argv):
    path = argv[argv.index("--registry") + 1] if "--registry" in argv else E.REGISTRY
    old = open(path, encoding="utf-8").read()
    try:
        new = build(old)
        before, after = E.parse(old), E.parse(new)
        got = set(E.diff_entries(before, after))
        if got != {("owner_rulings", RID, "added")}: E.refuse("the entries changed are not the list: %s" % sorted(got))
        for k in ("baseline_state", "needs_document_sha256", "sources_read_at"):
            if before.get(k) != after.get(k): E.refuse("%s moved" % k)
        errs, warns = E.validate(new)
        if errs: E.refuse("the result does not validate: %s" % "; ".join(errs[:5]))
    except E.Refused as e:
        print("apply_l3r2_d23: REFUSED: %s" % e)
        return 2
    print("owner_rulings  %s     added" % RID)
    print("apply_l3r2_d23: 1 entry, validator 0 errors, %d warnings%s" % (len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r2_d23: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
