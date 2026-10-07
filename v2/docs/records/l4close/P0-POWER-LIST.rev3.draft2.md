# P0: the power architecture's current blockers (revision 3, DRAFT 2: the state after cx46 and the disposition, refreshed to the candidate's commit 2a `bbba3e53`; 6 October 2026)

**Status: DRAFT for the coordinator**, the one writer of `v2/docs/records/l4close/P0-POWER-LIST.md`, who adopts it after reading it. **Base:
`bbba3e53e396d3fe0f8ddd2f38d0c169bcc99c45`**, the candidate's integration commit 2a on `fnd/p0pwr`. Written by the set 30 records-pack
worker on branch `fnd/recpack` from the first draft of this revision (branch fnd/int30rec at 7930ae68, written on `1c6d56f5`; not in this
branch's history, so cited as text only): every line citation re-pointed to `bbba3e53` and read there, the state column unchanged except
where a cited record now reads differently, each such change quoted with the commit that made it. The candidate branch has since merged
set 31 (`6fe398e9`); where that merge changes a statement below, it is named, with the line at `6fe398e9`. It keeps revision 2's twelve rows
(`v2/docs/records/l4close/P0-POWER-LIST.md:18-29`, 16:50 CEST) with their Id, Finding and Class as written there, cites each row's other
columns by line, and adds the column **State after cx46 and the disposition**, written from the candidate's records and the two checks as
received: cx45 on `06077cee` (`v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md`) and cx46 on `4d0ff8a2`
(`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md`), with the disposition commits classified in
`v2/docs/records/int30/RESULT.draft2.md` section 2. **No row is independently accepted. Nothing here accepts, closes or promotes anything.
Power-design closure: BLOCKED. Fabrication release: BLOCKED** (`v2/docs/records/l9t5/l9t5_connected.out:4`). Prototype framing: nothing is
built, bought, powered or measured. cx46 is the second negative on the method, which ends it (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:206`):
no disposition below has been read by an independent check.

**The state words.** REMAINING ENGINEERING: an unsupported correction or open design defect handed to the receiving company "with the
failed cases, attempted correction, unresolved fact or design decision, and affected provisional outputs" (the owner's part 24,
`v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:786`), never as a qualification-only item. CONDITIONAL: a check's "CONFIRMED AS
CONDITIONAL" or "CLOSED AS CONDITIONAL", with its conditions. CLOSED IN SCOPE: a cx46 item "CLOSED BY THE CORRECTION", closed only in the
scope cx46 states. EXTERNAL: the receiving company's validation scope (`v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md`).
Verdicts are quoted as given. `path:N` is line N at `bbba3e53`; a line at another revision is written `<sha>:path:N`.

| Id | Finding (revision 2) | Class (revision 2) | Revision 2's row | cx45 on `06077cee`, as given | cx46 on `4d0ff8a2`, as given | Disposition commit(s) | State after cx46 and the disposition |
|---|---|---|---|---|---|---|---|
| P0-1 | F01 / D-17 (L9P-F01): the all-transmit case is not supplied from the pass line | 1 (its overlap: 3) | `v2/docs/records/l4close/P0-POWER-LIST.md:18` | "P0-1: NOT CONFIRMED because the reference-loading disposition and complete tolerance claim need correction, although the service and dynamics are correctly PROVISIONAL." | "P0-1 NOT CONFIRMED: the steady-state MODEL band reproduces, but complete reference-loading coverage and conservative acceptance limits remain REMAINING ENGINEERING." Item 2 NOT CLOSED; item 3 CLOSED BY THE CORRECTION | `9cc6725d`, `1c6d56f5` | **REMAINING ENGINEERING** (the reference's loading through Q551's hold and release; the acceptance limits) with **F01 / D-17 PROVISIONAL** on B-PA1, B-PA2 and V-PA-REF; item 3 (the obsolete draft texts) **CLOSED IN SCOPE** |
| P0-2 | I-03 (L9P-F03) and the dedicated return L8R2-F31: V6-B1, V6-B2, V6-m1, V6-m8, V6-m12 | 1 | `v2/docs/records/l4close/P0-POWER-LIST.md:19` | "P0-2: NOT CONFIRMED because the return resistance is not demonstrated realisable on the current placement." | "P0-2 NOT CONFIRMED: the distributed return study improves the evidence, but actual socket geometry and the complete electrical bound remain REMAINING ENGINEERING." Item 4 NOT CLOSED | `9cc6725d`, `0b33a1f9` | **REMAINING ENGINEERING**: V6-B1 OPEN; the placement and solve are a STUDY on a stand-in land; V6-B2's vendor tasks PROVISIONAL, UNSENT |
| P0-3 | T10 (L9T5-F06) with the CAN fault rows F13, F16, F17; V6-B3, V6-m9, V6-m10 | 1 | `v2/docs/records/l4close/P0-POWER-LIST.md:20` | "P0-3: NOT CONFIRMED because CAN fault containment, thermal-envelope coverage and the final contract remain incomplete." | "P0-3 NOT CONFIRMED: independent hardware is drafted, but fault containment, response timing and sustained peak-temperature bounds remain REMAINING ENGINEERING." Items 5, 6, 7 and 8 NOT CLOSED | `6b768b1e` (merged by `9cf3982a`), `0b33a1f9` | **REMAINING ENGINEERING**: CON-004's quorum service OPEN, L9T5-F21 OPEN, FW-B22 PROVISIONAL, V-B23's response WITHDRAWN, the sustained thermal bound WITHDRAWN, rev X HELD; L9T5-F06 OPEN |
| P0-4 | eFuse settings EF-F01, EF-F02 and V6-m3 to m6 | 1 (m4: 2) | `v2/docs/records/l4close/P0-POWER-LIST.md:21` | "P0-4: CONFIRMED AS CONDITIONAL on connector thermal qualification and the RockBLOCK build condition." | "P0-4 CONFIRMED AS CONDITIONAL: connector thermal qualification, exact parts and the RockBLOCK pads-open build condition remain required." Item 16 CLOSED AS CONDITIONAL | none needed (`0b33a1f9` moved one digest line of `efuse_check.out`) | **CONDITIONAL**: the receptacle and harness contacts at the inside air (the supplier's measurement or a design alternative), the exact parts and values, the RockBLOCK pads OPEN as a build condition |
| P0-5 | the thermal guard C4 (L8P-F08 corrected in draft): V6-m7, V6-m2 | 1 | `v2/docs/records/l4close/P0-POWER-LIST.md:22` | "P0-5: NOT CONFIRMED because the guard correction has not been propagated through the connected calculation and common-path protection failures remain open." | "P0-5 NOT CONFIRMED: the second guard path improves single-fault coverage, but propagation, repeated thermal exposure and latent-fault coverage remain REMAINING ENGINEERING." Items 9 and 10 NOT CLOSED | `6b768b1e` (merged by `9cf3982a`), `0b33a1f9` | **REMAINING ENGINEERING**: C-PROT rev 1 for the guard PROVISIONAL; L8P-R9-F1 (the latent first failure, the retry heating with path 1 lost), L8P-R9-F2 (the allowance consumers unrestated) and L8P-R9-F3 OPEN; revision 2's SESSION L8P-D9 latent-fault tolerance WITHDRAWN |
| P0-6 | T7, the final composition (V6-m11) | 1 | `v2/docs/records/l4close/P0-POWER-LIST.md:23` | "P0-6: NOT CONFIRMED because successful composition does not establish complete protection coordination, preserved service or stable regenerated outputs." | "P0-6 NOT CONFIRMED: composition records and input digests are improved, but unsupported dependent claims remain REMAINING ENGINEERING." Items 13 and 17 NOT CLOSED; item 14 CLOSED AS CONDITIONAL; item 1 NOT CLOSED | `1a4d3706`, `9cc6725d`, `0b33a1f9`, `ac8efbca`, `7070f106`, `bbba3e53` | **REMAINING ENGINEERING** for the connected electrical verdict (seven open fault rows); stability **CONDITIONAL** (met for `4d0ff8a2` and for candidate 3, owed again on the integrated revision); item 1's inputs now in the tree (parts 23 to 25) and this list reconciled by this draft; L4-E9's change-list rows R-220 to R-245 APPLIED to the register, the page's table and the generator's data by `7070f106`, no drafted circuit change applied to a generator (`v2/docs/records/l4e9/l4e9_power_path.out:1310`: "117 changes; none APPLIED") |
| P0-7 | D-10 (B6 / L4-F01): a stiff source arriving with the solar guard already on; D-16: the input current sense out of its +-100 mV range at the 25 V corner | 2 | `v2/docs/records/l4close/P0-POWER-LIST.md:24` | "P0-7: NOT CONFIRMED because B2's connection and short-circuit guarantees do not stand, although D-16's correction and D-10's remaining-engineering classification are supported." | "P0-7 NOT CONFIRMED: D-10 remains explicit REMAINING ENGINEERING, while B2 has lost protection credit and baseline membership but still has inconsistent selection and owner-action wording." Items 11, 12 and 15 CLOSED BY THE CORRECTION; item 18 NOT CLOSED | `4d1d02de` (merged by `f973b646`), `7070f106` | D-10: **REMAINING ENGINEERING** E-1 (OPEN, an unresolved protection defect in the model); D-16: corrected in draft, its classification supported by cx45 (R-240 DRAFTED, not applied to a generator); since `7070f106` L4-E9's data reads "ADDRESSED IN DRAFTS: CORRECTED in draft by P0-7" (`v2/docs/records/l4e9/l4e9_power_path.out:615`); route B2: UNSELECTED and WITHDRAWN AS DRAFTED, items 11, 12 and 15 **CLOSED IN SCOPE**; item 18 addressed in text by `4d1d02de`, unchecked, with B2 wording left elsewhere (L4-E9's applied D-10 text read "an owner item" at `bbba3e53`, `v2/docs/records/l4e9/l4e9_power_path.py:4294`; cleared in L4-E9's files by `6fe398e9`) |
| P0-8 | E11-37, the charger's gate drive into three FETs | 2 | `v2/docs/records/l4close/P0-POWER-LIST.md:25` | not named | not named; finding 1: "P0-4, P0-8 and the four external-dependency rows retain their outstanding conditions; their presence supplies no closure evidence." | none (no commit after `4d0ff8a2` touches E11-37) | unchanged: **OPEN on a vendor fact** (Ciss against TI's 5 nF; Q-TI-17 drafted, UNSENT), bounded at the desk in L4-E11; **EXTERNAL** as TI's answer or the bench |
| U-01 | the cell (D-06's pocket): the ruled 35E unsuitable on its published evidence (LO-01d to g); the Saft MP 176065 xtd supported for the temperature windows only | 3 ARCH | `v2/docs/records/l4close/P0-POWER-LIST.md:26` | not named | finding 1, as P0-8 | none (the annex is unchanged after `4d0ff8a2`) | **EXTERNAL**, ARCHITECTURE-LEVEL, as the annex section 3 has it; the pack baseline unchanged; the Saft option a PROPOSAL |
| U-02 | the sealed case's heat rejection in each required mode | 3 ARCH | `v2/docs/records/l4close/P0-POWER-LIST.md:27` | not named | finding 1, as P0-8 | none | **EXTERNAL**, ARCHITECTURE-LEVEL, as the annex section 1 has it (T-H1); dependents PROVISIONAL |
| U-04 | the BQ25730 (B1) with the battery FET pair and board E on VSYS_E | 3 ARCH | `v2/docs/records/l4close/P0-POWER-LIST.md:28` | not named | finding 1, as P0-8 | none | **EXTERNAL**, ARCHITECTURE-LEVEL, as the annex section 2 has it (routes (R1) and (R2)); (B1)'s mode table, D2's margin and the held current PROVISIONAL |
| E11-29 | the three paralleled battery FETs' sharing: TP-E11-29 (DELTA-02's method, V2RG) | 3 (qualification, not ARCH) | `v2/docs/records/l4close/P0-POWER-LIST.md:29` | not named | finding 1, as P0-8 | none | **EXTERNAL**, a qualification, as the annex section 4 has it; TP-E11-29 NOT EXECUTABLE until its two preconditions; V2RG-B1 OPEN as the supplier's qualification item |

Sources of the two check columns: cx45's summary `v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md:10`; cx46's summary
`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:10`, its finding 1 `:81` and its items `:114-204`.

## Row notes (each state's evidence)

**P0-1.** cx46 item 2 "NOT CLOSED" (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:121-123`); item 3 "CLOSED BY THE
CORRECTION" (`:126-128`). The disposition (`9cc6725d`): Q551's held load on the reference, up to 4.4791 mA, and its release, about 30.5 ms,
REMAINING ENGINEERING "with the acceptance limits below" (`v2/docs/records/l9t5/l9t5_f01.out:103-108`); the MODEL band unchanged at 6.3518
to 6.9259 A and the PRINTED-rows band 6.3888 to 6.8945 A "NOT a bound on the cap" (`:132-134`); "AFTER cx46 ... F01 / D-17 and every
dependant ... stay PROVISIONAL; the reference's loading through Q551's hold and release and the acceptance limits are REMAINING ENGINEERING
for the receiving company, never a qualification-only item" (`:212-214`); cx44's finding 3 "STILL AN OPEN DESIGN DEFECT for the
reference's loading (cx46)" (`v2/docs/records/l9t5/L9T5-CASES.md:51`). C-ALLTX rev 3 at the cap: 15.1308 V, MODEL margin 0.3692 V
(`v2/docs/records/l9t5/l9t5_case.out:193`; `v2/docs/records/l9t5/L9T5-CASES.md:43`). The supplier's validation tasks, each PROVISIONAL
until read: B-PA1, "IDD at 30.0 W at most 6.351 A (the band's floor 6.3518 A rounded DOWN, cx46) less the measurement's own expanded
uncertainty" (`v2/docs/records/l9t5/l9t5_f01.out:226-227`); B-PA2, the dynamics and the release from Q551's hold (`:231-234`); V-PA-REF,
three TLV75801P at the drawn and the held load (`:235-239`). If B-PA1 fails, the ARRANGEMENT fails and routes R1 or R2 are taken
(`:215-219`). The connected output carries the row OPEN (`v2/docs/records/l9t5/l9t5_connected.out:334-335`, `:341-342`). Revision 2's
row reads the case at 15.1307 V (`v2/docs/records/l4close/P0-POWER-LIST.md:18`) where the records read 15.1308 V
(`v2/docs/records/l9t5/l9t5_f01.out:145`; `v2/docs/records/l9t5/l9t5_case.out:193`): the revision 3 list carries the records' figure. After
`6fe398e9`, L4-E9's data reads D-17 "OPEN (REMAINING ENGINEERING, RE-2): a correction DRAFTED and PROVISIONAL"
(`6fe398e9:v2/docs/records/l4e9/l4e9_power_path.out:621`); the state here is unchanged.

**P0-2.** cx46 item 4 "NOT CLOSED" (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:131-133`). The disposition
(`9cc6725d`, `0b33a1f9`): the XT60-M land stands in for the selected XT60-F (`v2/docs/records/l8r2/l8r2_dist.out:22-24`); "DISPOSITION OF
V6-B1 AFTER cx46 ...: OPEN, REMAINING ENGINEERING for the receiving company", its scope the selected female lands, the real source and
load sites, a justified distributed resistance with tolerance coverage and each LDO's own shift, with L8R2-F43 and L8R2-F44 (`:125-133`;
`v2/docs/records/l8r2/L8R2-KNOWN-DEFECTS.md:1087-1094`). V6-B2's indirect paths: vendor tasks (Hirose U.FL, Molex HDMI) UNSENT,
PROVISIONAL (`v2/docs/records/l9t5/l9t5_connected.out:343-345`).

**P0-3.** cx46 items 5 to 8 "NOT CLOSED" (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:136-153`). The disposition
(`6b768b1e`): "DISPOSITION (10j, after cx46): cx45's Q3 NOT CLOSED", OPEN or PROVISIONAL: CON-004's quorum service, FW-B22, L9T5-F21, the
response times, V-B23's response (WITHDRAWN), the sustained thermal bound (WITHDRAWN as a bound), T10-A3 at a peak; REMAINING ENGINEERING:
the peer-silence or diagnostic circuit with the recovery proof, the corrected rail-trip response and its network calculation, peak-current
containment or the periodic electrothermal solution, a rev X part's qualification, VOS0 under the trip
(`v2/docs/records/l9t5/l9t5_t10.out:662-667`). The countermodel: 127.54 C, "OVER 125 C" (`:620`). Rev X: HELD with no admission route
(`:645-647`; `v2/docs/records/l9t5/T10-ROUND5.md:51`). L9T5-F06 "STAYS OPEN" (`v2/docs/records/l9t5/l9t5_t10.out:670`). The rows F13 and
F16 read "A DRAFTED CORRECTION, DESK ACCEPTANCE MET BY ITS AUTHOR ON REV V, UNCHECKED" with "PROVISIONAL after cx46" (`:678-682`,
`:683-686`); the F17 row reads the same opening words without that qualifier (`:691`): a wording the coordinator may align with `:662-667`. The record's status line, since `ac8efbca`, reads T10 "STAYS OPEN, a DRAFTED
CANDIDATE, unchecked" and "L9T5-F13, F16 and F17 OPEN" (`v2/docs/records/l9t5/README.md:1`).

**P0-4.** cx46 item 16 "CLOSED AS CONDITIONAL" (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:191-193`). The
conditions as the record states them: EF-F01's and EF-F02's rows PROVISIONAL at the inside air until the supplier's measurement (the
receptacle or harness at the band's top current in a 76 C chamber) or a design alternative (`v2/docs/records/efuse/efuse_check.out:425-431`);
the RockBLOCK's charge pads OPEN, a build condition (`:432-434`); the label EF-L03 OPEN for Layer 6 (`:621`). No commit after `4d0ff8a2`
changed a figure of `efuse_check.out` (`v2/docs/records/int30/RESULT.draft2.md` section 2, row 10, and section 3: digest lines only).

**P0-5.** cx46 items 9 and 10 "NOT CLOSED" (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:156-163`). The
disposition (`6b768b1e`): "no single failure removes the trip AT ONCE. PROVISIONAL" (`v2/docs/records/l8p/l8p_c4.out:273-275`); with path
1 lost "the protection under those retries is NOT shown (cx46 10): the bounded retry-energy analysis is REMAINING ENGINEERING"
(`:285-286`); REMAINING ENGINEERING also "an AUTOMATIC diagnostic ... or a fault-tolerant redesign" (`:338-341`); the record's
"DISPOSITION (10c, after the recheck cx46 ...): V6-m7 and cx45's Q5 NOT CLOSED" (`:355-358`); `v2/docs/records/l8p/L8P-BREAKER.md:1398-1400`.
Propagation: L4-E11 section 28 executes both allowance cases on the intact circuit, "PROVISIONAL, not closed" (`v2/docs/records/l4e11/l4e11_power.out:2134-2138`).
Revision 2's "SESSION L8P-D9 tolerates the three as latent" (`v2/docs/records/l4close/P0-POWER-LIST.md:22`) is the passage cx46 finding
1 calls "withdrawn L8P-D9 latent-fault tolerance" (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:81`); the record reads "that label is WITHDRAWN: no requirement permits it" (`v2/docs/records/l8p/l8p_c4.out:200`); the
owner's part 24 superseded the latent-guard owner question (`v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:768`).

**P0-6.** cx46 items 13 and 17 "NOT CLOSED", item 14 "CLOSED AS CONDITIONAL", item 1 "NOT CLOSED"
(`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:176-183`, `:196-198`, `:116-118`). The connected output: seven
fault rows, all OPEN, and "THE CONNECTED ELECTRICAL VERDICT: REMAINING ENGINEERING" (`v2/docs/records/l9t5/l9t5_connected.out:319-340`);
the worst-case margin row "PROVISIONAL/OPEN" (`:314-316`). Stability: met for `4d0ff8a2`
(`v2/docs/records/l9t5/stability/RUN-4d0ff8a2-pass2.log:1-19`) and, since `ac8efbca`, for candidate 3 (its 18 outputs equal their
digests in `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt:4-21` at `bbba3e53`); owed again on the integrated revision, `bbba3e53`
carrying fourteen stale or forward pins that commit 2b moves (`v2/docs/records/int30/RESULT.draft2.md` section 3). Item 1: the owner's parts 23 to 25 are in the tree (the part table,
`v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:23-25`, merged by `1a4d3706`); this draft is the twelve rows' reconciliation. L4-E9's
change-list rows R-220 to R-239 and R-242 to R-245 were a draft (`v2/docs/records/l9t5/apply_l4e9_changelist_p0.py:8-16`); `7070f106`
applied them (`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:314-338`) and the draft now reads the applied tree ("APPLIED BEFORE",
`v2/docs/records/l9t5/apply_l4e9_changelist_p0.py:160`, `bbba3e53`). The connected output still reads "L4-E9's own output refuses at its
L4-E11 pin" (`v2/docs/records/l9t5/l9t5_connected.out:361-362`) while `bbba3e53` regenerated that output (`v2/docs/records/int30/RESULT.draft2.md`
section 5, item 5). After `6fe398e9`: set 31 adds R-246 to the change list and restates rows the draft's applied-state reader demands
verbatim, which is expected to refuse there (`v2/docs/records/int30/RESULT.draft2.md` section 5, item 9).

**P0-7.** cx46 items 11, 12, 15 "CLOSED BY THE CORRECTION" and item 18 "NOT CLOSED" (below). D-10: "an UNRESOLVED PROTECTION DEFECT in the
present model", the receiving company's remaining engineering item E-1, its failing cases F1 to F4, the unchanged requirements, the
correction routes open to a supplier, and S1 and S2 qualifying the correction afterwards (`v2/docs/records/l4e7/L4E7-P0SOL.md:99-127`;
`v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md:19-23`, `:85-92`). D-16: "Completed independently of E-1 ...: D-16's correction"
(`v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md:89-92`); its row R-240 DRAFTED, which since `7070f106` names D-10 "the receiving company's engineering item E-1 (its later validation step is S1" (`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:334`). Route B2:
"UNSELECTED and WITHDRAWN AS DRAFTED" with no owner item (`v2/docs/records/l4e7/B2-PRESENCE.md:4-6`, `:27-29`); the baseline has no B2
step (`:22-25`). Residual B2 wording is listed in `v2/docs/records/int30/RESULT.draft2.md`
section 5, item 1 (L4-E9's files cleared by `6fe398e9`: "UNSELECTED and WITHDRAWN AS DRAFTED, with no protection credit and no owner
item", `6fe398e9:v2/docs/records/l4e9/l4e9_power_path.out:600`, the data at `6fe398e9:v2/docs/records/l4e9/l4e9_power_path.py:4243-4244`); R-240's "item S1" for D-10 became E-1 in `7070f106` (item 2).

**P0-8.** Unchanged since revision 2: "E11-37 STAYS OPEN: no printed figure decides a three-device gate load against TI's 5 nF; Q-TI-17"
(`v2/docs/records/l4e11/l4e11_power.out:1527`); Ciss 7.08 nF typical, 1.42 times TI's 5 nF (`:1496`). No commit after `4d0ff8a2` changed
these lines (`v2/docs/records/int30/RESULT.draft2.md` section 2, row 8: L4-E11's changes are in its section 28; commit 2b moves two digest lines of that output).

**U-01, U-02, U-04 and E11-29**, as the annex has them (no commit after `4d0ff8a2` up to `6fe398e9` touches the annex):
- U-01, "ARCHITECTURE-LEVEL; D-06's pocket": three actions kept apart, a request for evidence (Saft, UNSENT), a limited experiment (the
  one-cell screen, a receiving-company task) and adoption of a 4S1P Saft pack (OW-3, "NOT requested"); the owner-approved pack baseline
  stands (`v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:81-99`).
- U-02, "ARCHITECTURE-LEVEL; T-H1": the per-mode lines M1 to M9 with their pass readings; T-H1 a receiving-company validation task; a
  measured failure shows "THAT arrangement failing", never by itself a requirements conflict; the outputs PROVISIONAL until it runs
  (`v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:21-60`).
- U-04, "ARCHITECTURE-LEVEL; E11-31 / R-161": routes (R1) TI's evaluation module and (R2) a controlled coupon, neither waiting on the
  whole-kit release; R-161's pass limits; (B1)'s mode table, D2's step margin and the held pack current PROVISIONAL
  (`v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:62-79`).
- E11-29, "a QUALIFICATION, kept apart from the architecture blockers": see the fixture facts below
  (`v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:101-109`).

## The three B2 items cx46 closed (as given; each closes the disposition it names, not B2's or D-10's engineering)

- Item 11, "Q6 cold-connection guarantee: CLOSED BY THE CORRECTION": "B2-PRESENCE.md:13-23,119-138 and l4e7_p0sol.out section 5e withdraw
  the guarantee, identify missing connector sequencing, bounce/remating and retained-BST proof, and remove protection credit. This closes
  the unsupported guarantee's disposition, not B2's engineering." (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:166-168`)
- Item 12, "Q6 presence-pair short and protection credit: CLOSED BY THE CORRECTION": "B2-PRESENCE.md:140-156 and l4e7_p0sol.out section
  5f include the pair-short circuit result and fault table. Protection credit is removed; baseline ORDER_E excludes B2. No claim that B2
  closes D-10 survives in those corrected disposition rows." (`:171-173`)
- Item 15, "D-10 retained as remaining engineering: CLOSED BY THE CORRECTION": "... Neither B2 nor S1 closes the defect. This disposition
  is correct; D-10 itself remains OPEN REMAINING ENGINEERING." (`:186-188`)

Item 18, "B2 uniformly unselected and withdrawn outside baseline: NOT CLOSED" (`:201-203`), is the one B2 item the disposition `4d1d02de`
answered in text after cx46; no check has read that answer. The line numbers cx46 cites inside `B2-PRESENCE.md` are those of `4d0ff8a2`;
`4d1d02de` rewrote the page (154 lines changed), so they no longer point at the same text.

## The fixture facts (E11-29)

- TP-E11-29 "is written and NOT EXECUTABLE until L4-E9 restates R-159 and a supplier agrees in writing to the fixture requirement: the net
  heat at each heating lead's joint at most 10 mW in every state (the supplier demonstrates it by three thermocouples or a reference
  coupon). Targets: Zw at most 37.59 K/W, R17 at most 0.294 K/W, the pours 0.1 mOhm." (`v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:103-105`)
- The specimen: the FET pair and Q42 on a coupon with the record's pours; route (R2)'s coupon can carry it; no bench secured; cost NOT
  QUOTED; the fallback if sharing fails, lower-resistance FETs or a fourth, "a design change inside UDC-1, not an architecture change"
  (`:105-109`).
- After `6fe398e9`: set 31 restates R-159 from E11-29's row, and its record keeps the procedure "still NOT EXECUTABLE until its
  quotation and check are re-taken against the restatement and a supplier agrees the fixture requirement"
  (`6fe398e9:v2/docs/records/l4e9/SET31-CHANGES.md:80-81`); the state here is unchanged.
- The procedure's own status: "NOT EXECUTABLE. Two things must happen first" (`v2/docs/test-procedures/TP-E11-29.md:19`); "V2RG-B1 stays
  OPEN as that supplier qualification item" (`:25`).
- Why it is a fixture requirement and not a desk design: the check V2RG found round 15's guard NOT CLOSED, "the second negative check of
  the lead treatment, so that design loop ENDED" (`v2/docs/records/l4e11/README.md:5`, `:11`).

## What this revision does not claim

No row moves to an accepted state. The CLOSED IN SCOPE entries close only what cx46 says they close. The REMAINING ENGINEERING rows are
handed over, not solved, and are not qualification-only items. The Layer 4 DESK gate is the coordinator's assessment
(the DESK gate evidence draft on fnd/int30rec at 7930ae68 is evidence for it); power-design closure and fabrication release stay BLOCKED.
Unchanged from revision 2, outside this list: the paused and preserved items and the decisions not reopened
(`v2/docs/records/l4close/P0-POWER-LIST.md:31-35`).
