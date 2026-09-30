#!/usr/bin/env python3
"""Record the owner's addendum to layer 3's round 5 (30 September 2026) as owner ruling D-27 (MESHSAT-1357). Applied
once: a second run refuses. The pattern of apply_l3r5_d26.py.

The addendum reached this work through the coordinating session and is filed, as quoted there, in
v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md (its section on the addendum); every quote below is asserted in
that file before anything is written. The ruling changes no record: it is the source the pages and the prepared scripts
cite for row L3-OD7 (M1's runtime requirement), which precedes rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6, and for holding
every question that would remove a function or narrow the deployment until that row is answered.

Usage: python3 apply_l3r5_d27.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "l3r2"))
import l3edit as E  # noqa: E402

INSTR = "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md"
QUOTES = [
    "Round 5 addendum from the owner (30 Sep 2026). The owner is questioning the 72-hour requirement:",
    "Evaluate alternatives before asking me to sacrifice functions or accept restrictive deployment conditions.",
    "He also said to preserve HF and the tablet functionality.",
]
RID = "D-27"
TITLE = "the owner's addendum to layer 3's round 5: M1's runtime questioned, alternatives before any sacrifice (30 September 2026)"
RULING = ("The owner's addendum of 30 September 2026, relayed by the coordinating session and quoted in " + INSTR + ": "
          "the owner is questioning the 72-hour requirement. In his words: \"" + QUOTES[1] + "\" As relayed: \"" + QUOTES[2] +
          "\" M1's runtime is a row he answers, L3-OD7, before rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6, which depend on it; "
          "no row asks him to remove a function or to accept a deployment condition before it is answered, and its "
          "figures come from a bounded runtime and battery comparison with its check. The 72 hours are the session's "
          "SC-21, which D-20 preserved with M1's specified duration.")
ENTRY = '''  - id: {rid}
    authority: OWNER
    ruled_on: "2026-09-30"
    title: "{title}"
    ruling: >-
{ruling}    source: ["owner ruling {rid}", "{instr}"]
'''


def build(raw):
    d = E.parse(raw)
    if any(r.get("title") == TITLE for r in d["owner_rulings"]): E.refuse("the addendum is already recorded: this script has run")
    if not any(r["id"] == "D-26" for r in d["owner_rulings"]): E.refuse("D-26 is not in the registry: run apply_l3r5_d26.py first")
    nid = E.next_id(d, "D", ("owner_rulings",))
    if nid != RID: E.refuse("the next free owner ruling is %s, not %s: the pages cite %s" % (nid, RID, RID))
    E.assert_in(INSTR, QUOTES)
    for t in (TITLE, RULING): E.screen(t, RID)
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
        print("apply_l3r5_d27: REFUSED: %s" % e)
        return 2
    print("owner_rulings  %s     added" % RID)
    print("apply_l3r5_d27: 1 entry, validator 0 errors, %d warnings%s" % (len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r5_d27: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
