# Integration set 27 (MESHSAT-1357, 2 and 3 October 2026)

Promoted to main as `94971c8c` (`94971c8ce81a0276a22c4ff3c7594dc3deb46736`), gated by `_bin/suite_gate.py` on the box suite of that
exact commit: 3.12 pass 2554 passed, 0 failed, 92 skipped; 3.11 pass (test_l4e10, test_l4e12) 28 passed, 0 failed, 20 skipped;
216 of 216 modules ran; the tree unchanged after the suite (G1 to G6 PASS). The skips are the makers' held documents, which
the box does not carry by design. Runner checks before the suite: targeted modules 274 passed, 0 failed, 1 gated skip;
requirements 0 errors, rules 0 errors, 16 rendered pages current, verify_l3am 19 of 19, verify_acceptance 18 of 18.

What it carries: the response to the collaborator's review (B1 to B7) and its targeted recheck (NOT YET, filed as received),
and to the owner's four external reviews (filed as received in `records/l4close/`), each correction made in the record that
owns it and integrated by the consolidation (L4-E9 at `938e442a`); the classification of every open item (L4-E9 section 8f)
and the supplier task list (8g); the supplier handover's entry page (`v2/docs/handover/supplier/`); L4-E7's compute/render
split and its sentence-keyed lead scan. The coordinator's labelled check of the corrections after the recheck is
`records/l4close/checks/check-l4close-3.md` (not an Astra check; the recheck's NOT YET stands).

The design's decisions (L4-POWER-ARCHITECTURE.md section 6): the architecture candidate CONDITIONAL; power-design closure
BLOCKED; fabrication release BLOCKED; the engineer handoff READY TO START, provisional. Status headline: "Selected
power-architecture candidate. Known design defects and qualification gaps remain open. Changes are drafts, not an implemented
or qualified circuit. Power-design closure and fabrication release are blocked."

Integration traps met on the way (the session log has the detail): an output that prints another record's file digests made
the freeze loop (fixed at its root by L4-E7's sentence-keyed scan); regen_out's pin check refuses a pin a script reads at a
commit while the tree's file differs; a draft renumbered on a branch is disjoint only against the drafts in its base (the
board E collision C135 and C136, caught by the test at integration).
