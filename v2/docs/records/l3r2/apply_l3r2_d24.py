#!/usr/bin/env python3
"""Record the owner's addendum on the power path and the decision package (30 September 2026) as owner ruling D-24
(MESHSAT-1357, layer 3's second issue, round 3b). Applied once: a second run refuses. The pattern of apply_l3r2_d23.py.

The addendum reached this work through the coordinating session and is filed, as quoted there, in
v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md (its fourth section); every quote below is asserted in that file
before anything is written. The ruling changes no record: it is the source the pages cite for stating every result that
depends on board A's front end in three cases (the circuit as drawn, the resistor-only proposal, a hypothetical corrected
power path), for labelling energy available only through the last as hypothetical, for tracking the corrections as
engineering tasks, and for recommending no option as feasible on its idealised energy balance alone.

Usage: python3 apply_l3r2_d24.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3edit as E  # noqa: E402

INSTR = "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md"
QUOTES = [
    "Update decision 1's premise. The reported findings make this a power-path correction, potentially involving "
    "components, sensing, layout and thermal design. Stop presenting the 6.2 mOhm substitution as a sufficient solution. "
    "Keep findings provisional until independently checked, and distinguish: the circuit as drawn; the resistor-only "
    "proposal; any hypothetical corrected power path used for feasibility calculations.",
    "Correct the energy claims ... Where a supportable power envelope is not established, label the result conditional or "
    "inconclusive. Preserve useful hypothetical calculations, but state the required circuit corrections prominently. Do "
    "not count energy available only through an inadequate power path as demonstrated capability.",
    "Finish the concise decision package. Keep the existing six-row owner table. Show each option's checked figures, "
    "limitations, required changes and remaining uncertainties, with links to evidence. Retain the weather-coverage "
    "choices and quantified capacity/fit comparisons. Do not recommend an option as feasible solely because its idealised "
    "energy balance passes.",
    "Close requirements without confusing them with implementation. Complete only the bounded feasibility work necessary "
    "for informed requirements decisions. Full circuit correction, layout and bench testing belong to subsequent layers.",
    "Bring me decisions only when the proposed remedy changes mission requirements, functions, deployment conditions, "
    "enclosure constraints or approved resources.",
    "Component selection and Kelvin routing are engineering tasks.",
]
RID = "D-24"
TITLE = "the owner's addendum on the power path and the decision package of layer 3 (30 September 2026)"
RULING = ("The owner's addendum of 30 September 2026 to the third round of layer 3's second issue, as quoted in " + INSTR +
          " (its one elision is the quoting session's, marked). In his words: " + " ".join("\"%s\"" % q for q in QUOTES))
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
    if not any(r["id"] == "D-23" for r in d["owner_rulings"]): E.refuse("D-23 is not in the registry: run apply_l3r2_d23.py first")
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
        print("apply_l3r2_d24: REFUSED: %s" % e)
        return 2
    print("owner_rulings  %s     added" % RID)
    print("apply_l3r2_d24: 1 entry, validator 0 errors, %d warnings%s" % (len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r2_d24: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
