#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3, restated for layer 3's second issue (L3-R2, MESHSAT-1357, 30 September 2026).

Three edits to v2/docs/handover/LAYER-STATUS.md, each located by its own text (never a line number), each asserted to
occur exactly once before it is made:

  1. the page head's "**At H3**" paragraph gains one sentence: layer 3 is reopened for the current target (L3-R2);
  2. the section "## Layer 3. Requirements" is restated: L3-R2's state, the completion gate of D-21 with each
     condition's state at this writing (the live state is REQUIREMENTS-L3-R2.md section 2), what the session closed, the
     feasibility finding F-01, whose each remaining item is; the section's text as it stood (the states at H2 and H3)
     is kept word for word under "### History: layer 3 at H2 and H3 (kept as written)";
  3. Appendix A.3's INTEGRATOR LINE gains an L3-R2 step at its end.

Nothing else on the page changes: the script compares the result with the page, outside the three places, byte for
byte. No dash character is written. A second run is refused.

Usage: python3 apply_layer_status_l3.py [--check]
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l3edit as E  # noqa: E402

PAGE = os.path.join(E.TOP, "v2/docs/handover/LAYER-STATUS.md")
MARK = "L3-R2 (30 September 2026"
HEAD_OLD = ("**At H3** the section \"Status at handover H3\" is the current status. It is short: H3's design is H2's, so it "
            "states\nwhat H3 changes and leaves the H2 section's rows for layers 4 to 9 and its layout-entry table as the "
            "status they are.")
HEAD_ADD = (" **After H3 (30 September 2026) layer 3 is reopened for the current target configuration, L3-R2, IN_PROGRESS**:"
            " its own section below states it, with the pages of `v2/docs/handover/layer3/`; the H3 section keeps the status"
            " H3 carried.")
SEC_START = "## Layer 3. Requirements\n\n"
SEC_END = "\n---\n\n## Layer 4. System architecture\n"
ILINE_ANCHOR = "> **INTEGRATOR LINE, layer 3:**"

NEW_SECTION = """## Layer 3. Requirements

**Now (30 September 2026): IN_PROGRESS, reopened for the current target configuration (L3-R2).** Layer 3 was COMPLETE at H3 on the requirements H3 accepted (the registry BASELINED at `a54b793b`; `v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md`). Since H3 the owner preserved M1 and REQ-072 (D-20, 28 September 2026); the energy reconciliation showed that D-06's one pack cannot carry M1 and that the architecture meeting it on the model changes the store, the lid and the solar input (Option A(i)); the owner's instruction of 30 September 2026 (owner ruling D-21) asks layer 3 to be finished for the current target before layer 4 advances; and his review of the draft decision table the same day (owner ruling D-22) holds rows L3-OD1, L3-OD2 and L3-OD4 until a corrected, independently checked energy comparison arrives. Both are filed in `v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md`. Layer 4 does not advance on the changed target until this layer completes. The second issue is under `v2/docs/handover/layer3/`: `REQUIREMENTS-L3-R2.md` (the consolidated, versioned specification, generated from the registry by `render_l3r2.py`), `L3-RECONCILIATION.md` (the target, every proposal since H3 with its status, requirement against implementation, the closure list) and `OWNER-DECISIONS-L3.md` (the five rows the owner decides and the combinations the evidence covers). The H3 release is preserved and unchanged.

**The completion gate (D-21).** The states below are this writing's; the live state is `REQUIREMENTS-L3-R2.md` section 2, rendered from the registry and the files `l3r2.yaml` names.

| Condition | At this writing | What closes it |
|---|---|---|
| The target is unambiguous | NOT MET | the owner's rows L3-OD1 to L3-OD4 (Option A(i)'s store; where the displaced lid item goes and whether its function stays; the solar input; M1's deployment conditions) decided on a combination the evidence covers, each applied by its prepared script under `v2/docs/records/l3r2/conditional/`, on the checked energy basis (open item S-127) |
| The requirement-changing owner decisions are resolved | NOT MET | the five rows L3-OD1 to L3-OD5; rows L3-OD1, L3-OD2 and L3-OD4 are held by D-22 until the energy basis is filed |
| Contradictions and requirement-level TBDs are closed | NOT MET | CFL-017 (row L3-OD5); the CONOPS and PRODUCT-BRIEF passages the decided rows change, re-issued through their layers or by a change record the owner approves (L3-C26). CFL-016 is closed: S-122 closed on integration set 15 and CFL-016 reads PASS. No record reads TBD, and every TBD, owed or open mention is classified (`L3-RECONCILIATION.md` (d)) |
| An independent check accepts the handover | NOT MET | the first check (`v2/docs/records/l3r2/checks/check-l3r2-1.md`) reads accepted: no; its findings are answered in round 2, and a further check by a checker who wrote none of L3-R2 is owed (L3-C27) |

**What the session closed (30 September 2026, `v2/docs/records/l3r2/`).** D-21 and D-22 recorded; S-114 closed (the reconciliation filed and REQ-072 re-read on it), its closing evidence qualified by the model's 20.7 V bus; the energy basis every M1 figure waits on opened as S-127, which REQ-072 waits on; M-02 and S-53 restated to the decisions they now wait on; CFL-006 re-read (its FAIL is the pack enclosure's, a layer 7 item, S-27); CFL-002's stale TBD sentence corrected; seven acceptances made measurable from their own statements with no limit added or removed (REQ-008, REQ-012, REQ-029, REQ-054, REQ-057, REQ-068, CHO-003). The rows are made coherent: row L3-OD1 fixes the store only, row L3-OD3 alone fixes the array, and the scripts and the gate refuse a combination the evidence does not cover. Every open item is classified by layer, and every item no record waits on carries its disposition (acceptance item 3.15).

**Feasibility finding F-01, for the owner.** The two-pack results were computed on the energy model's most favourable charge bus (20.7 V, above the bus's nominal 20.000 V and its stated band of 19.080 to 20.960 V); at lower bus voltages, and with U3's 6.0 A bracket, the margins fall, the tablet-out lid's the most. Which lid option meets M1 across the kit's supply range, and on which planes, is stated only from the checked energy basis (S-127); until then no energy figure on the L3 pages is the design's (`L3-RECONCILIATION.md` (a)).

**Whose each remaining item is.** The owner: rows L3-OD1 to L3-OD5 (`OWNER-DECISIONS-L3.md`), rows 1, 2 and 4 after the energy basis. Stream l3plane and an independent checker: the energy basis and its check (S-127, L3-C31), and the relocation facts row L3-OD2 needs. The session: the rows' figures and recommendations restated from the checked basis; the CONOPS and product brief passages the decisions change, prepared for the owner's approval (L3-C26); the re-take of the analyses on the adopted architecture at layer 4 (S-53). The integrator: the scripts and renders on the integration set (L3-C28). A checker: the independent check of L3-R2 (L3-C27).

### History: layer 3 at H2 and H3 (kept as written)

"""
ILINE_ADD = (" **L3-R2 (30 September 2026, branch `fnd/l3r2` on integration set 15's line `4012429e`):** status now IN_PROGRESS,"
             " reopened for the current target configuration on the owner's instruction D-21; rows L3-OD1, L3-OD2 and L3-OD4"
             " held by his review D-22. The session's closures applied by `v2/docs/records/l3r2/apply_l3r2_session.py` (D-21"
             " and D-22 recorded; S-114 closed; the energy basis opened as S-127; M-02 and S-53 restated; CFL-006 re-read;"
             " CFL-002 corrected; seven acceptances made measurable); the five owner rows prepared as"
             " `v2/docs/records/l3r2/conditional/od_l3_1.py` to `od_l3_5.py`, not applied, coherent by construction; the"
             " handover `v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md`, generated from the registry; the completion gate and"
             " the closure list in `v2/docs/handover/layer3/L3-RECONCILIATION.md` (d); finding F-01 reported to the owner;"
             " the first independent check (`v2/docs/records/l3r2/checks/check-l3r2-1.md`, accepted: no) answered. The"
             " registry's `baseline_state` keeps naming `a54b793b` until an independent check of L3-R2 accepts the issue."
             " Owner: the integrator as registry writer; the owner for rows L3-OD1 to L3-OD5.")


def build(t):
    if MARK in t: E.refuse("the page already carries L3-R2: this script has run")
    reg = E.parse(open(E.REGISTRY, encoding="utf-8").read())
    if not any(c["id"] == "S-122" for c in reg["closed_items"]): E.refuse("S-122 is not closed: the section says CFL-016 is closed")
    if not any(r["id"] == "D-22" for r in reg["owner_rulings"]): E.refuse("D-22 is not in the registry: run apply_l3r2_session.py first")
    for txt in (HEAD_ADD, NEW_SECTION, ILINE_ADD):
        for dch in E.DASHES:
            if dch in txt: E.refuse("an added text carries a dash character")
    if t.count(HEAD_OLD) != 1: E.refuse("the head's At H3 paragraph is not the text restated")
    t = t.replace(HEAD_OLD, HEAD_OLD + HEAD_ADD, 1)
    if t.count(SEC_START) != 1 or t.count(SEC_END) != 1: E.refuse("the layer 3 section's bounds are not unique")
    a = t.index(SEC_START)
    b = t.index(SEC_END, a)
    old_body = t[a + len(SEC_START):b]
    if not old_body.startswith("**After H2: COMPLETE**"): E.refuse("the layer 3 section does not open as expected")
    t = t[:a] + NEW_SECTION + old_body + t[b:]
    if t.count(ILINE_ANCHOR) != 1: E.refuse("appendix A.3's integrator line is not unique")
    i = t.index(ILINE_ANCHOR)
    j = t.index("\n", i)
    t = t[:j] + ILINE_ADD + t[j:]
    return t, old_body


def main(argv):
    try:
        old = open(PAGE, encoding="utf-8").read()
        new, old_body = build(old)
        if old_body not in new: E.refuse("the section's old text is not kept word for word")
        # outside the three places nothing changed
        rest_old = old.replace(old_body, "")
        rest_new = new.replace(NEW_SECTION, SEC_START).replace(HEAD_ADD, "").replace(ILINE_ADD, "").replace(old_body, "")
        if rest_old != rest_new: E.refuse("the page changed outside the three places")
    except E.Refused as e:
        print("apply_layer_status_l3: REFUSED: %s" % e)
        return 2
    print("apply_layer_status_l3: head sentence, layer 3 section (%d characters kept as history), integrator line%s"
          % (len(old_body), " (check only)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(PAGE, old, new)
        print("apply_layer_status_l3: written v2/docs/handover/LAYER-STATUS.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
