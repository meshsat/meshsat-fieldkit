#!/usr/bin/env python3
"""Record the owner's three corrections to round 3b (30 September 2026) as owner ruling D-25 (MESHSAT-1357, layer 3's
second issue). Applied once: a second run refuses. The pattern of apply_l3r2_d23.py and apply_l3r2_d24.py.

The corrections reached this work through the coordinating session and are filed, as quoted there, in
v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md (its fifth section); every quote below is asserted in that file
before anything is written. The ruling changes no record: it is the source the pages cite for Kelvin sensing as an
implementation requirement (the A32 layout tied to its revision), for the derated variant (a') of board A's front end, and
for the test every owner row meets (it names the requirement it changes and quantifies the consequence).

Usage: python3 apply_l3r2_d25.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3edit as E  # noqa: E402

INSTR = "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md"
QUOTES = [
    "Correct the Kelvin classification. The inspected A32 layout is historical evidence. It cannot establish a routing "
    "defect in the current board, which has no layout yet. Keep the A32 finding tied to that revision. Unless current "
    "schematic/netlist evidence independently establishes an error, record Kelvin sensing and the permitted shared "
    "resistance as implementation requirements with measurable verification criteria.",
    "Describe the 4.05 A proposal accurately. Reducing the charger's input-current limit addresses current-limit "
    "coordination. It does not establish that the other electrical defects are resolved or that the mission succeeds. Show "
    "its energy consequence as a clearly labelled derated variant; preserve the actual as-drawn case. Keep the "
    "independently checked 0.378 A comparison closed unless relevant inputs change.",
    "Restrict owner decisions to actual requirement changes. Charging below a source's available power is an engineering "
    "choice when approved requirements remain satisfied. Ask me only when the remedy changes an agreed mission condition, "
    "charging time, functionality, enclosure constraint or approved resources. Each such question must name the affected "
    "requirement and quantify the consequence. Component selection and sensing implementation remain engineering tasks.",
]
RID = "D-25"
TITLE = "the owner's corrections to round 3b of layer 3 (30 September 2026)"
RULING = ("The owner's corrections of 30 September 2026 to round 3b of layer 3's second issue, as quoted in " + INSTR +
          ". In his words: " + " ".join("\"%s\"" % q for q in QUOTES))
ENTRY = '''  - id: {rid}
    authority: OWNER
    ruled_on: "2026-09-30"
    title: "{title}"
    ruling: >-
{ruling}    source: ["owner ruling {rid}", "{instr}"]
'''


def build(raw):
    d = E.parse(raw)
    if any(r.get("title") == TITLE for r in d["owner_rulings"]): E.refuse("the corrections are already recorded: this script has run")
    if not any(r["id"] == "D-24" for r in d["owner_rulings"]): E.refuse("D-24 is not in the registry: run apply_l3r2_d24.py first")
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
        print("apply_l3r2_d25: REFUSED: %s" % e)
        return 2
    print("owner_rulings  %s     added" % RID)
    print("apply_l3r2_d25: 1 entry, validator 0 errors, %d warnings%s" % (len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r2_d25: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
