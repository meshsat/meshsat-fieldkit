#!/usr/bin/env python3
"""Record the owner's reviewer's review of the layer 3 decision brief (30 September 2026) as owner ruling D-26
(MESHSAT-1357, layer 3 round 5). Applied once: a second run refuses. The pattern of v2/docs/records/l3r2/apply_l3r2_d25.py.

The review reached this work through the coordinating session and is filed, as quoted there, in
v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md (its section on the review); every quote below is asserted in that
file before anything is written. The ruling changes no record: it is the source the pages and the prepared restatements
cite for the separation of the owner's requirement target from the studied candidate's compliance, for the acceptance
definitions of rows L3-OD1, L3-OD3, L3-OD4 and L3-OD5, and for the three status levels.

Usage: python3 apply_l3r5_d26.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "l3r2"))
import l3edit as E  # noqa: E402

INSTR = "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md"
QUOTES = [
    'Separate owner-selected requirements from candidate compliance. A combination can be a valid target and have '
    'a FAIL or INCONCLUSIVE implementation. Retain rejection of genuinely contradictory requirements and all '
    'release gates. Verify that recording HF retention plus WAB does not fabricate a PASS or silently change the '
    'requirement.',
    'Define the criterion at the kit loads: the specified service continues for 72 hours within voltage, power '
    'and pack limits. Combined stored Wh alone is insufficient. Reference exact initial state, load profile, '
    'panel orientation, installation, cutoff and power-path case. State whether a single exact orientation is the '
    'benchmark when no deployment band is established.',
    'Supply the selected cell/pack limits and a mode-specific environment table. Distinguish battery-fitted '
    "operation from cell-free qualification/storage. Owner acceptance must cover the operational consequence. 'No "
    "cost' should not conceal reduced claimed capability.",
    'A 10 N requirement can be proposed as a chosen design target. Specify application point, force '
    'direction/duration, slope, support surface, lid angle and load configuration. Cite the matching mechanical '
    'result before calling the candidate a modelled PASS.',
    'Approve topology separately from electrical compliance. Pin the panel revision and datasheet; distinguish '
    'available array power, controlled converter input power, cold open-circuit exposure, short-circuit/fault '
    'currents and string versus combined-feed protection. Provide the rating derivation or an explicit '
    'engineering obligation rather than treating owner approval as verification.',
    'Requirements drafted / decisions recorded: the intended product and its acceptance criteria are explicit. '
    'Requirements baseline validated and accepted: the chosen constraints have a credible feasibility basis, the '
    'identified gaps are resolved to the agreed review scope, and the owner has accepted the baseline. Design and '
    'hardware compliant: later circuit, layout and physical evidence demonstrate those requirements.',
]
RID = "D-26"
TITLE = "the owner's reviewer's review of the layer 3 decision brief (30 September 2026)"
RULING = ("The review of the layer 3 decision brief MESHSAT-L3-OWNER-DECISIONS-2026-09-30.md (sha256/16 ca4a9dcfa2e076ff) by "
          "the owner's reviewer, relayed as the owner's and quoted in " + INSTR + "; its verdict CONDITIONAL for individual "
          "owner choices and BLOCKED for blanket approval or a claim that the revised layer 3 baseline is fully validated. "
          "In the review's words: " + " ".join("\"%s\"" % q for q in QUOTES[:5]) + " Its sixth passage defines the three "
          "status levels, quoted in the same file (requirements drafted and decisions recorded; the requirements baseline "
          "validated and accepted; the design and hardware shown by later layers' evidence).")
ENTRY = '''  - id: {rid}
    authority: OWNER
    ruled_on: "2026-09-30"
    title: "{title}"
    ruling: >-
{ruling}    source: ["owner ruling {rid}", "{instr}"]
'''


def build(raw):
    d = E.parse(raw)
    if any(r.get("title") == TITLE for r in d["owner_rulings"]): E.refuse("the review is already recorded: this script has run")
    if not any(r["id"] == "D-25" for r in d["owner_rulings"]): E.refuse("D-25 is not in the registry: run ../l3r2/apply_l3r2_d25.py first")
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
        print("apply_l3r5_d26: REFUSED: %s" % e)
        return 2
    print("owner_rulings  %s     added" % RID)
    print("apply_l3r5_d26: 1 entry, validator 0 errors, %d warnings%s" % (len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r5_d26: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
