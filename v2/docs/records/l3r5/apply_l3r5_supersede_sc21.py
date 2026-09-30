#!/usr/bin/env python3
"""Mark session choice SC-21 (M1's 72 hours, the session's choice of 27 September 2026 under the standing rule) superseded
in place by the owner's clarification D-28, applied to row L3-OD7 as D-32 (MESHSAT-1357, layer 3 round 5's fix round,
30 September 2026; the engineering collaborator's closure check astra-check-l3r5-1, B2: the registry's SC-21 still read
"this choice GOVERNS M1's duration"). The row stays as history: `taken` is unchanged, one dated sentence closes `why`, and
three fields are added (superseded_on, superseded_by, superseded_why), which the pages print as the mark. Nothing else
in the registry changes. Applied once: a second run refuses.

Usage: python3 apply_l3r5_supersede_sc21.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "l3r2"))
import l3edit as E  # noqa: E402

CID = "SC-21"
ON = "2026-09-30"
BY = "D-28 (applied as D-32)"
TAKEN = "72 hours on the PS-IDLE-SPEC energy basis (42.8 W)"
WHY = ("The owner's clarification D-28 of 30 September 2026, applied to row L3-OD7 as D-32: M1's runtime is a design "
       "objective of 48 to 72 hours under REQ-072's stated operating profile (obligation OBJECTIVE), not a mandatory "
       "minimum, and 72 hours is not elevated into one. The owner's own setting replaces this choice, as its reverse "
       "clause says; the 72 hours it took no longer govern M1's duration. The row is kept as history: L-02 stays closed, "
       "its value now the owner's.")
SENTENCE = ("Superseded on 30 September 2026 by the owner's clarification D-28, applied as D-32: M1's runtime is a design "
            "objective of 48 to 72 hours under REQ-072's stated operating profile, not a mandatory minimum; this choice no "
            "longer governs M1's duration and is kept as history (L-02 stays closed, its value now the owner's).")


def build(raw):
    d = E.parse(raw)
    sc = next((c for c in d["session_choices"] if c["id"] == CID), None)
    if sc is None: E.refuse("%s is not in the registry" % CID)
    if sc.get("superseded_by") is not None or sc.get("superseded_on") is not None:
        E.refuse("%s is already marked superseded: this script has run" % CID)
    if not any(r["id"] == "D-32" and str(r.get("decides")) == "L3-OD7:objective-48-72" for r in d["owner_rulings"]):
        E.refuse("D-32 does not decide row L3-OD7 objective-48-72: run apply_l3r5_closure.py first")
    if TAKEN not in " ".join(str(sc.get("taken")).split()): E.refuse("%s does not read %r" % (CID, TAKEN))
    for t in (WHY, SENTENCE): E.screen(t, CID)

    def f(block):
        block = E.append_folded(block, "why", SENTENCE)
        lines = block.split("\n")
        idx = [i for i, l in enumerate(lines) if l.startswith("    closes:")]
        if len(idx) != 1: E.refuse("%s has no single closes line" % CID)
        add = ['    superseded_on: "%s"' % ON, '    superseded_by: "%s"' % BY] + \
            ("    superseded_why: >-\n" + E.fold(WHY, 6)).rstrip("\n").split("\n")
        return "\n".join(lines[:idx[0] + 1] + add + lines[idx[0] + 1:])
    return E.replace_entry(raw, CID, f, "session_choices")


def main(argv):
    path = argv[argv.index("--registry") + 1] if "--registry" in argv else E.REGISTRY
    old = open(path, encoding="utf-8").read()
    try:
        new = build(old)
        got = set(E.diff_entries(E.parse(old), E.parse(new)))
        if got != {("session_choices", CID, "changed")}: E.refuse("the entries changed are not the list: %s" % sorted(got))
        fields = E.changed_fields(E.parse(old), E.parse(new), "session_choices", CID)
        if fields != ["superseded_by", "superseded_on", "superseded_why", "why"]: E.refuse("the fields changed are %s" % fields)
        sc = next(c for c in E.parse(new)["session_choices"] if c["id"] == CID)
        if TAKEN not in " ".join(str(sc["taken"]).split()) or sc.get("closes") != ["L-02"]: E.refuse("taken or closes changed")
        errs, warns = E.validate(new)
        if errs: E.refuse("the result does not validate: %s" % "; ".join(errs[:5]))
    except E.Refused as e:
        print("apply_l3r5_supersede_sc21: REFUSED: %s" % e)
        return 2
    print("session_choices  %s     changed (superseded_on, superseded_by, superseded_why, why)" % CID)
    print("apply_l3r5_supersede_sc21: 1 entry, validator 0 errors, %d warnings%s" % (
        len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r5_supersede_sc21: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
