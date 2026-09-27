# Review A, layer 2 (concept of operations): the brief for the fresh reviewer

To be filed as `v2/docs/reviews/2026-09-27-review-A-layer2-brief.md` with the commit it pins. MESHSAT-1357.
Prototype design: nothing has been built, ordered, powered or deployed.

**This is an AI review, and it is labelled so in its record.** It is not a qualified review, it replaces none of the
qualified reviews the records require (D-09: R-BAT, R-SEC, and those still to be approved), and it establishes no
circuit's correctness. Its job is to find what a careful engineer taking over the concept of operations would find
missing, contradictory or unsupported.

**Who.** One reviewer who wrote none of the layer's documents and did not assemble the handover (not the layer-2
closer, not the integrator). No conversation history: the repository at the pinned commit and the documents below.

**What, at one pinned commit:**
- `v2/docs/CONOPS.md` (all of it);
- `v2/docs/OPERATING-ENVELOPE.md` and `v2/ecad/tools/pcb_envelope.yaml`;
- `v2/docs/PANEL.md` sections 1, 3, 5, 8, 9 and 10 (the operator-facing behaviour);
- `v2/docs/TEST-PLAN.md` section 1 and the envelope rows (E1 to E10, M1 to M7, section 6), with their Purpose and
  Verifies columns.

**Against:**
1. The owner's execution prompt, `v2/docs/reviews/2026-09-27-handover-execution-prompt.md`, section 2 (what COMPLETE
   means) and the layer-2 row of section 3: normal, degraded, startup, charging, shutdown, storage, service and fault
   scenarios; the operating envelope; simultaneous modes; the explicit behaviour of the retained core functions
   (CONOPS section 2a); product decisions settled under existing authority.
2. `v2/docs/ARCH-PCB-B-IOHA.md` sections 4, 7, 10, 13 and 15 (which module can host which bank: does the reduced mode
   of CONOPS section 4c hold its bearers and the SOS path?).
3. `v2/docs/feasibility/EMCON.md` section 5a (L_max and F1 to F9: are they carried into CONOPS 4b.1 and M4 without
   loss?).
4. `v2/docs/feasibility/POWER-THERMAL.md` sections 4, 6, 7 and 9 (are CONOPS 4a, 5 and 6 and OPERATING-ENVELOPE 3 and 4
   consistent with it; are C1 to C4 and K1 to K5 carried with what the operator sees?).
5. The requirements registry's owner rulings and session choices (`v2/ecad/tools/pcb_requirements.yaml`): is every
   owner ruling quoted as the owner's and every session choice marked as the session's, with its reversal?

**Questions the record must answer, each with file and line:**
- Is every mode entered and left on something the kit can actually sense or the operator can do?
- Does any core function lose its path in a mode without the document saying so?
- Is every number either sourced, marked INFERRED with its arithmetic, a stated session choice, or TBD with its effect?
- Is any requirement lowered, any function dropped, any protection weakened or any scope narrowed to close an item?
- Does any feasibility bound that includes failure stand as settled where a layer-2 decision depends on it? (The
  documents claim the enclosure conductance does not decide any layer-2 item: check that claim.)
- Is anything stated as done, tested, qualified or working that is not?

**Record:** findings numbered, each BLOCKING or MINOR, with file:line and the fix asked; the pinned commit; the reviewer's
identity as an AI reviewer; the label "AI review". The layer is marked baselined at that commit in
`v2/docs/handover/LAYER-STATUS.md` only after every BLOCKING finding is answered in the documents.

## Pass 2 (added 27 September 2026, after the first pass, `v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27.md`)

The second pass is held at the integrating commit by one fresh reviewer who wrote none of the layer's documents and
did not hold the first pass (so that the first pass's framing is checked, not inherited), with the same scope, the
same sources and the same label (AI review). It reads the first pass's record, then checks each finding's answer
below against the documents and the sources, and then the whole scope again for anything the answers broke. It is not
told which answers the closer thinks are strongest. Where each finding is answered:

| Finding | Answered in |
|---|---|
| B1 (the heat stage's losses; the shutdown source) | CONOPS 4 (Heat stage and Shutdown rows), 4c (the heat stage, as generated; graceful shutdown), 4f (two heat-stage columns), 7a; SC-L2-02, SC-L2-10. Sources: Quectel RM520N series HD v1.1 section 3.2; TI SLUSE66A 9.6.8, 9.6.10, Table 9-8; `gen_sch_a.py` line 708 |
| B2 (a lid-closed start-up) | CONOPS 4 (Startup and Reduced rows), 4c (the start-up paragraph), 7a; TEST-PLAN E3-L and section 4; SC-L2-17 |
| B3 (M1 and the night) | CONOPS 3 (M1), 6, 7 (D-06 row), 7a; SC-L2-05; `drafts/LAYER-STATUS-layer2.md`; handoffs 3.8 |
| B4 (E3-L's pass line) | TEST-PLAN E3-L (E3-A's whole pass line with the lid closed; an SGP41 above +55 C fails) |
| B5 (REQ-052 not restated down) | CONOPS 4c (the heat stage's required set; BANK-R1 and the finding), 4 (Heat stage row), 4f, 7, 7a; TEST-PLAN E3-L; OPERATING-ENVELOPE 3, 4, 8; SC-L2-18; `drafts/gen_sch_b.BANK-R1.patch`; handoffs 3.6 (REQ-052 kept) and 13 |
| B6 (ASSEMBLY step 10) | CONOPS 4d step 1; TEST-PLAN T-H3; `drafts/ASSEMBLY.step10-and-lamp-test.patch`; handoffs 14 |
| B7 (the cold end) | CONOPS M5, 4c (the cold end and its table), 4a (the warm-up's power), 7a; OPERATING-ENVELOPE 4; `pcb_envelope.yaml` carve-out and `cold_end`; TEST-PLAN E4; SC-L2-11; `pwr_red2.out` COLD block |
| m1 | CONOPS 5 (the APRS duty row) |
| m2 | `pwr_red2.py` and `.out` (PS-EMCON's aged-60 % runtime); CONOPS 4a |
| m3 | CONOPS 4 (Reduced row, Guarantee), 4c (the reduced mode) |
| m4 | CONOPS 4 (Heat stage row, Exit), 4c ("There is no stage after this one") |
| m5 | CONOPS 4 (Transport and Storage rows), 4c (preparing for storage or transport), 7a; TEST-PLAN section 1 states; SC-L2-03 |
| m6 | `drafts/LAYER-STATUS-layer2.md` (CFL-017 with its compact question) |
| m7 | CONOPS 4c (the D-02b paragraph); handoffs 3.6 (CON-012); `drafts/LAYER-STATUS-layer2.md` |
| m8 | handoffs 1 and 8 (the part_temps patch in the same commit) |
| m9 | CONOPS M5, 4 (Degraded row), 4c (recovery targets); TEST-PLAN section 4; SC-L2-09 |
| m10 | TEST-PLAN E4 (UTC +1.0 C, UTD -9.0 C) |
| m11 | handoffs 1 and 12 (records filed in the integrating commit): an acceptance item until then |
| m12 | handoffs 1, 3.2 to 3.5 (SC-12, S-43, CFL-017, round 8's bindings); CONOPS "on main since `53a98a71`" wording |

## Pass 3 (added 27 September 2026 by the targeted fixer c23, after the second pass, the same record)

The next pass is held the same way (one fresh reviewer who held neither earlier pass nor the documents). Where the two
blocking findings of the second pass are answered:

| Finding | Answered in |
|---|---|
| P2-B1 (D-02b's row carries the session's choices without saying so) | CONOPS section 7, row D-02b: "with choices taken by the session under the owner's standing rule of 26 September 2026 (section 7a), which are not part of the ruling", and "restated by the session" before the two consequences |
| P2-B2 (nothing protects the pack once the heat stage fails on an input) | CONOPS section 4 (a new Hot stop row, and the Heat stage row's Exit and Guarantee), 4c (the hot stop: the two steps, the thresholds against the battery packet's error budget, the controller and the signal path from the netlists, HOT-R1, firmware or hardware, the destructive backstops named, the open design question of a non-destructive hardware stage, and what it costs, with its firing inside the envelope OPEN under FEA-004 and REQ-052 predicted to fail at +40 C on any supply at the worst corner), 4e (three rows), 4f (Pack safety), M2, 7a (three rows); TEST-PLAN E3-H (the expected action and the abort at a cell surface of +59 C for every E3-A, E3-L and E3-H run; E3-L's pass line unchanged); OPERATING-ENVELOPE sections 3 and 4; `pcb_envelope.yaml` `hot_end.hot_stop`; `drafts/hotstop_bounds.py` and `.out`; the registry side in fnd/hc3 (REQ-077 under NEED-13, SC-49 and SC-50, S-57 and S-58 on main a8652172) |

