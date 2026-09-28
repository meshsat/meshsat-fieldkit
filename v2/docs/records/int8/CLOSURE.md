# Integration set 7 (fnd/int8 at 7f6de345 onto main 6b419b02): closure record, DRAFT by the independent checker

An AI review's draft for the integrator to file as v2/docs/records/int8/CLOSURE.md; every count below was read from
git at 7f6de345 against main 6b419b02 (375 files, 128657 insertions, 2191 deletions, 82 commits). Nothing of the kit
has been built, ordered or measured; every verdict named is a desk reading of a prototype design.

## Circuit changes

None. No schematic generator (gen_sch_*.py), no .kicad_sch, no netlist (pcb-*/out/*.net) and no board file changed;
every board's declared phase and netlist sha on CURRENT-EVIDENCE.md is the same as at main (A32 0a2b59087bcc2678,
B21 028997a6c5e8810f, C24 3fddbb3edcd4248a, D12 7a2c0ac2190b141a, E17 56adc9746d61c4e0, P4 760ac6f74d62d194,
E5 686b29a734c55b9a). The one generator touched, gen_pcb_b3.py (5 lines), changes net-class PATTERNS only (below).

## Declaration changes

- Boards A, D and E (tools/boards/a.json +202, d.json +26, e.json +54): internal_ports named for every internal
  lead, and board A's 18 external entries (VIN_RAW's entry J_VR1 to J_VR4 among them) as decision 31's review
  corrected them; the reviewed set of external pins in tools/pcb_port_reviews.json (+120), a configuration input of
  port_protect.py, pinned in the holds (pcb_board_holds.yaml).
- Board B RF classes (gen_pcb_b3.py PATTERNS, stream w5si W5SI-D1): the SKY13351 switch ports SW?_O* and SW?_IN,
  the card RF lines W?*_CARD and GNSS_RF_IN take the RF class (single-ended 50 ohm); b.json (+10 -2) accordingly.
- Board C (c.json +20): the four EMCON copy nets declared LOW_SPEED_OR_DC on their content, checked against the
  netlist and the drivers' documents by the draft that wrote them; noted that this class is also the one the EMC
  return rules skip.
- The contract IF-AB-POWER's contact_rating (tools/pcb_interfaces.yaml) rewritten from the held JST VH catalogue:
  10 A per contact at AWG 16 on the standard header; the AWG 18 lead of J_54V carries no stated rating
  (INCONCLUSIVE). INT-001 was re-taken on every board for it.
- Layout constraint sheets (v2/docs/layout-constraints/A.md to P.md and README.md) bound to their inputs by
  constraints_bound.py (stream p3bind; rule DOC-003).

## Tool changes (v2/ecad/tools, 19 .py files, 7378 insertions, 243 deletions; 9 test files, 3589 insertions)

- port_protect.py (+330 net): refuses a declared port whose pins carry no supply or signal; reports every connector
  pin no entry covers; holds every declaration against the reviewed set (INCONCLUSIVE where no review enumerated the
  board's external pins, boards B and C); tests/test_port_protect.py (60 tests).
- reliability.py (+644 net) with wear_inventory.py (new, 272): the population is an inventory by reference class and
  land; a missing, unreadable or empty netlist reads INCONCLUSIVE; each board's declaration bound to its artefact by
  sha256 (written_against); CONFIG_INPUTS names the list and its thirty cited documents; pcb_reliability.yaml
  rewritten (+1164 net); tests/test_reliability.py and test_reliability_inventory.py.
- edge_length.py (+1048 net) with ibis_manifest.py, ibis_read.py, ibis_fetch.py (new): SI-001 reads a model only when
  the tracked manifest v2/vendor/ibis-manifest.yaml pins the file present, fails closed and says its state when the
  models are withheld, holds every Ramp cell to the model's own V-t table; pcb_edge_rates.yaml (+1136);
  tests/test_edge_length.py, test_ibis_models.py, test_pinned_models.py. Two fixes after the first suite:
  ibis_fetch.py reads its two flag values through verdict.opt (038037ed); edge_length.py's note no longer says a
  model is not in the tree when none is absent (05af085c).
- rules_status.py (+157 net): the manifest as a configuration input of edge_length.py and the pinned-state rule
  (PINNED_INPUTS, _pinned_state); CONFIG_INPUTS for reliability.py; rules_render.py's derived notices.
- constraints_bound.py (new, 885) with tests/test_constraints_bound.py (687).
- The tray's record tools: v2/cad/lid_tray_qmx_r2.py, _check.py, _drawing.py; tests/test_lid_tray_qmx_r2.py (315);
  test_frame_seat_inputs.py carries the r2 module.
- Apply scripts under v2/docs/records/int8/ (seven), each asserting its precondition, re-parsing what it writes and
  refusing a second run; the box helpers box_retake.sh and install_pack.sh (filed in 38fd7cc9).
- v2/docs/handover/pack.yaml classifies v2/docs/CODEX-WORKER.md in group EV.

## Registry changes (tools/pcb_requirements.yaml +732 net; pcb_decisions.yaml +280; pcb_rules_coverage.yaml)

- Opened: S-95 (the lid harness's crossing of the sealed face, EQ-31), S-96 (what the desk cannot close on the r2
  tray), S-97 (tx_inhibit.py's three-ground report cap, disposition TOOLING), S-98 (the interim alignment of the A to
  B power declarations, disposition DECLARATION), S-99 (the +5V_DEV coincident peak above the LM5176 average limit),
  S-100 to S-113 (decision 31's findings A-F2, X-C1, D-F1 to D-F4, E-F1 to E-F4, D-N1, A-N1, T-2, T-3),
  S-114 (the energy reconciliation of M1 under D-20).
- Closed: S-63 by SC-75 (the r2 lid tray); S-88 (H3-02) by TRN-001 PASS of 42 on board A against the reviewed set;
  S-89 (H3-01) by REL-001 re-taken on every board with the repaired tool (every board INCONCLUSIVE, held by named
  items), both landed by the re-take of aaed6daa and re-taken again in 9d89ffd3.
- Linked: FEA-007 (SC-75; waits on S-95, S-96, no longer S-63), REQ-021 (S-95), FEA-002 (S-92, S-93), REQ-018
  (S-99), REQ-072 and REQ-016 (S-114), REQ-007, REQ-009, REQ-015, REQ-017, REQ-029, REQ-041, REQ-058, CON-018,
  CHO-003 (S-100 to S-113 by finding); REQ-022, REQ-024, REQ-026, REQ-028, REQ-064 stop waiting on S-89 and cite it
  in history; CON-010 and REQ-044 rebound to the final page; REQ-005, CFL-014, CFL-016 rebound to CONOPS.md;
  CON-006, REQ-019, CFL-015 rebound to the case pages; CFL-016 to pcb_decisions.yaml.
- Extended: S-92 (both voltages of the SA_PTT_n divider; what bench E-01 does not measure), M-02 and L-07 (one
  sentence each on D-20 and D-19).
- Rulings: D-19 (the case test package, the buy route, staged) and D-20 (M1 and REQ-072 preserved, the budget
  reconciled), authority OWNER, 28 September 2026; session choice SC-75; decisions 48 to 54 (edge rates, w5si2) in
  pcb_decisions.yaml; REL-001's coverage entry with its evidence floor 2026-09-28T20:33:53+02:00; SI-001's coverage
  note; DOC-003 registered; needs_document_sha256 moved to the CONOPS.md that carries D-19 and D-20.
- No record's statement, acceptance, evidence_result, allocation or phase changed.

## Evidence refreshes

- The consolidated re-take of every schematic-phase reading on the KiCad box at 8b623c96 (commit aaed6daa: the
  driver retake_schematic_phase.py in place, reliability.py per board, claims_check; the makers' models present for
  SI-001; the tracked readings by patch, the ignored ones by tar).
- The second re-take at 05af085c after the two tool fixes (commit 9d89ffd3; 96 tracked routed/*.verdict.json changed
  against main); driver logs filed in 38fd7cc9 under records/int8/box/ (retake-2.log, retake-2-other-writers.log,
  retake-2-run.txt: HEAD 05af085c, retake exit 0, 19:14:50Z to 19:17:48Z).
- The pages rendered on it: 34 layout-entry reasons (A 6, B 8, C 4, D 6, E 3, P 5, E5 2), 83 CURRENT_CANDIDATE
  readings, no reading limited by an open item; the suite at 7f6de345 2171 passed, 0 failed, 3 skipped.

## Documents

- CONOPS.md (section 7 rows D-19 and D-20; section 3 M1's owner instruction), ASSEMBLY.md (the QMX tray r2 row,
  build steps 10 and 11, the lead table, the removal paragraph), CASE-MARGINS.md and CASE-FIT-UNCERTAINTIES.md (the
  r2 tray; M3 and M19 re-read from frame_seat.out), v2/BUILD.md, v2/README.md, v2/cad/README.md.
- handover/LAYER-STATUS.md (layer 7 reads the r2 tray; item (2) answered by SC-75), handover/ENGINEERING-QUESTIONS.md
  (EQ-24 answered, EQ-31 added, EQ-13's owner instruction row), handover/START-HERE.md, handover/pack.yaml.
- EXECUTION-PLAN.md (the checkpoints of 28 September 18:50 and 20:02, the Codex worker's usage and outcomes);
  OWNER-DECISIONS-OPEN.md; the generated pages CURRENT-EVIDENCE.md, REQUIREMENTS-TRACE.md, PCB-RULE-STATUS-*.md,
  PCB-GAP-REGISTER.md, PCB-GOLDEN-RULES.md, PCB-OPEN-PAIRS.md, PCB-ETA.md, PCB-RULE-COVERAGE.md,
  PCB-PROTOTYPE-UNKNOWNS.md; the layout-constraints sheets.
- reviews/DECISION-31-PROTECTION-TOPOLOGY.md (775 lines, AI review: 32 exposed conductors on boards A, D and E).
- The records: cx1 (the pilot's ANALYSIS.md, CORRECTION.md, two checks), d6rel, d8dec31 (52 files), p3bind, w5si
  and w5si2, w5tray, int8 (the three checks with their notes, seven apply scripts, the box logs), and the vendor
  filings (28 files: the Infineon and TI sheets, the QMX materials and standards transcriptions, the seven maker
  documents of the reliability list, the withheld IBIS lines in sources.txt and vendor-status.txt).
- The case release: v2/release/case-2026-09-27/lid-tray-qmx-r2/ (16 files with v2/cad).

## Carried minor items (the integrator's list after the fresh check, 28 September 2026)

| From | Item | Owner | Where it goes |
|---|---|---|---|
| set 7 check, 5 | S-88's and S-89's closing evidence name the first re-take's commit (aaed6daa) while the tree's readings are the second re-take's (9d89ffd3), identical in content | integrator | wording only; noted here |
| set 7 check, 6 | `apply_w5tray.py` writes six documents before the registry and does not roll back on a missing vendor file | the drafts' template (next stream's author) | a rollback or a pre-check in the template |
| d8dec31 check 2, N1 to N6 | the reviewed set's enforcement (pin the per-board map in the test or read the review's tables), a ref listed twice inflates the denominator, duplicate JSON keys, a review file that exists is the only check, the tests leave fixtures under /tmp, `make_pin_tables.py` on the committed shape | port_protect.py's owner (stream d8dec31's successor) | a tool item in the next set |
| d6rel check 2, 2 to 5 | the tests leave 108 fixtures per run; CONFIG_INPUTS must follow the list's citations by hand; no board reads PASS on REL-001 until REQ-028 rules a service life; REL-O-03's Amphenol M.2 documents and the series sheets' order-code rows | reliability.py's owner; the parts stream | a tool item and a parts item in the next set |
| w5si2 check, m2, m3, m7 | rehearse the merge again if int8 moves (done: it moved and merged); draft 6 writes the state it runs in (run with the models present: done); the board B draft applies without the stream (kept in order: done) | integrator | answered at integration |
| Codex check 1 of S-99 | ten findings for the S-99 author (the wall port's current-limit equation sign; a false PASS at 5.0 mOhm; the loop time constant; the LDO model; the burst and capacitor claim; S3's zero; POE's 7 mA; the thermal scenario; the draft's stale note; two arithmetic slips) | stream s99's author, then a Claude re-check | set 8 |
