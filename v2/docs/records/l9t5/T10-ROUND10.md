**ROUND 10 (T10; Layer 4 tasks L4A-57 and L4A-61, row (b) of the AI-scope register, 7 October 2026, W151, branch `fnd/l4hod` after W146's L4A-58): DONE: L4A-57 reads DONE AS CONDITIONAL on E-17 (the TPS73733DCQRM3's junction at constant maximum dissipation at the TPS2553-1's printed maximum 0.5704 A, 113.8 C on the printed 76.0 C/W, a bound for every waveform under the limit; the printed theta is TI's JEDEC best case, not a bound on board B's copper, so E-17 is named with its specimen, quantity and pass limits; W135's four screen rows held on the selected parts; the response on printed timing; the service window against C-DEV rev 2 with row (b)'s enabled set and the drafts' rail additions; the judge FAILS on a TYPICAL or a guideline used as a bound); L4A-61's propagation (the T10 rows restated in `l9t5_t10.out` 11a (j), the connected rows in `l9t5_connected.out` 11a, the dependents of the T10 output re-pinned in order, three apply scripts for the shared pages: the contract's FW-B20 to FW-B22, V-B20, V-B21, V-B23 and the new FW-B24 with V-B25, IOHA section 12's rows 21 to 24, the ledger's section 4). NOT DONE: no independent check (row (b)'s is L4A-62); nothing applied; E-17 and everything physical. NEXT: the coordinator's reading, then L4A-62.**

# T10 round 10: the selected regulator stage's acceptance and row (b)'s propagation

Record l9t5, task T10, MESHSAT-1357; Layer 4 tasks L4A-57 and L4A-61 (`_runs/l4ai/register.tsv`). Author W151 (Claude), the one writer of
`fnd/l4hod` after W146, from 09:31 CEST on 7 October 2026 (times from `date`, Europe/Amsterdam). Prototype design: nothing in this kit
has been built, bought, powered or measured, and no figure here is a measurement. Every junction is a MODEL on printed figures. Nothing
here closes a cx46 item or moves a state: cx46 CORRECTIONS NOT CLOSED and Layer 4's DESK gate NOT PASSED stand; RE-5 to RE-8 stay NOT
CLOSED until row (b)'s check (L4A-62) and, for RE-6 and RE-7, E-17.

Figures are printed by `l9t5_t10.py` into `l9t5_t10.out` section 11a (cited T10:line) and by `l9t5_connected.py` into
`l9t5_connected.out` section 11a (cited CON:line). Labels: PRINTED, TYPICAL, DESCRIBED (the maker's prose, no limit), GUIDELINE (a
maker's figure marked as such), DRAFTED, MODEL, INFERRED, ASSUMPTION, SESSION.

## 1. Why

Row (b) is drafted: CAN M-B (W137, W143), its quorum (W139), the regulator stage (W138: TPS2553-1 at 49.9 kOhm with TPS73733DCQRM3), the
latched supervisor's EN route (W143) and HO-D's in-service limiter test (W146). Before row (b)'s check two register tasks remained:
L4A-57 (RE-6 and RE-7's acceptance on the selected stage, "DONE AS CONDITIONAL on E-17 if Zth cannot be bounded at the desk") and
L4A-61 (the propagation: every claim of the ledger's section 4 that row (b) weakens restated or kept PROVISIONAL).

## 2. L4A-57: the sustained bound at constant maximum dissipation (T10:800-815)

After the limiter acts, everything the LDO's input takes is at most IOSmax 0.5704 A (TI SLVS841F 7.5, PRINTED 0.475 to 0.565 A over -40
to 125 C TJ at 49.9 kOhm, with RILIM's 1 % through the maker's equations' exponents, W135's rule). With its output in regulation the LDO
dissipates (VIN - VOUT) x IOUT + VOUT x IGND, at most (4.1174 - 3.2505) V x 0.5704 A = 0.4944 W plus 3.2505 V x IGND. The junction's
rise is the input power convolved with the network's unit-step rise, which for a passive conduction network climbs monotonically to its
steady theta; so for any waveform under that power the junction never exceeds the air plus theta x P (MODEL, a property of the network,
not a typical curve). cx46's countermodel (0.50 A for 0.40 s every 1.50 s) lies under IOSmax: inside the bound, or limited and latched
in a specimen whose limit is under 0.50 A.

| Quantity | Figure | Label and source |
|---|---|---|
| the junction at IGND = 0, the printed 76.0 C/W | 113.8 C (margin 11.2 K) | MODEL on PRINTED (SBVS067W 5.4, new silicon, DCQ) |
| the ground current IGND | 880 uA at 1 A | TYPICAL only, no maximum: never a bound |
| the IGND that 125 C admits | 45.2 mA (51 times the TYPICAL) | MODEL: the result stated as a function of IGND |
| the theta that holds 125 C at IOSmax (IGND = 0) | 98.6 C/W | MODEL (W135's and W138's figure reproduced) |
| the regulator's 125 C current on the printed theta | 0.7400 A | MODEL, over IOSmax by 0.1696 A |

## 3. The theta on board B's copper: not bounded at the desk, so E-17 (T10:816-836)

TI's own note on the metric (SPRA953D, held, sections 1.1 and 1.2): carrying a JEDEC theta to a system board is "a misapplication of
the RθJA thermal parameter", and the 2s2p board "gives a best case performance estimate". Board B is six layers with 0.5 oz inner
copper, and no P0 draft part is placed (L4REG-F6). The conduction screen (MODEL, a means, never evidence): RθJB 18.1 C/W PRINTED plus
In1's spreading alone into still air at an ASSUMED 5 or 10 W/m2 K gives 62.7 to 78.0 C/W; the controller's own 0.526 W adds 4.5 to
13.6 K at an ASSUMED 10 to 20 mm. On the worst row the LDO reads 128.4 C: the result rests on the tab's copper and the distance from its
controller, which only a laid-out board settles.

**E-17, named (the receiving company's measurement; nothing sent).** Specimen: the first-article board B (or a coupon of its six-layer
stack with the U40, U50 and U60 sites as Layer 10 lays them out, their controllers and limiters powered at their bounded state), three
sites. Quantity: each LDO's junction with its input current held at 0.5704 A, its input at 4.1174 V and its output in regulation, from
its case-top temperature by psi-JT 8.6 C/W (PRINTED), in still air at 76.25 C, its IGND read as input less output current. Pass limits:
the junction at most 125 C (RθJA(effective) at most 48.75 K over the measured power, 98.6 C/W at IGND = 0); for the latched transient,
the junction's rise in 10 ms of 2.348 W at most 36.2 K, Zth(10 ms) at most 15.4 C/W, which would remove W151-1's exclusion.

## 4. The response on printed timing and the output short (T10:837-852)

No response time is needed for the sustained bound: IOS is a DC limit and every state with the output in regulation is inside section 2
whatever its waveform. A demand over IOS is a fault (no served state reaches IOSmin): the limiter holds IOS and latches off at most
10 ms after it limits (the deglitch, PRINTED), then stays off until its EN toggles (the peers' route, at most once in 10 s). The limit's
onset tIOS (2 us) is TYPICAL only and is not used. V-B23's round 6 0.2 s stays WITHDRAWN; V-B23 is restated on the limiter.

**SESSION W151-1** (extending W138-3 and W135-2): the LDO's junction in a state whose output is out of regulation is excluded from the
125 C and 150 C criterion, both at or over IOS (latched within 10 ms, at most 23.5 mJ) and under IOSmin (a hard short in foldback, a
partial short). Why: that supervisor is lost (IOHA row 3); the containment of the other two holds on the limiter's printed IOSmax
whatever the LDO does (failing open it darkens its own supervisor; failing shorted IN to OUT it puts at most 4.1174 V on its own
supervisor's rail, read by its peers through FT pins rated to VDD + 3.6 V while powered; a peer dark at the same time is a double
condition, as W146-F9); the regulator prints its output short-circuit duration "Indefinite" (SBVS067W 5.1). authority SESSION (the
owner's standing rule of 26 September 2026 and ruling of 21 September 2026); authority_why: an engineering exclusion inside the drafted
circuit with its reason, no requirement, case row, purchase or publication changed; ruled_by W151; ruled_on 7 October 2026; reversed_by
none. To reverse: E-17's Zth(10 ms) limit read, or a regulator printing its short-circuit current with a maximum under IOSmin.

## 5. W135's four screen rows and the service window (T10:853-877, CON:374-378)

| Row | On the selected parts |
|---|---|
| (1) the bus-fault rows served | IOSmin 0.4702 A over the largest served 0.4239 A (S3', B5) by 0.0463 A; no served state limited, no bridging capacitance; row 8's 0.5491 and 0.5639 A may latch a supervisor off (row 8 accepts it; the peers restart it) |
| row (b)'s enabled set | TIM3 (canmb's captures) and an ADC (hodtest's reads) were in no bounded set: 0.0029 A by 10c's method plus the ADC's VDDA current, TYPICAL only, taken at three times (ASSUMPTION): at most 0.0073 A; the window 0.0390 A |
| the drafts' rail additions | canmb, canen and hodtest's own figures (their records'): at most 0.0041 A more; the window +0.0349 A on the composed candidate (CON:374-378) |
| (2) the output short | latched within 10 ms, or excluded with its reason (W151-1) |
| (3) the limiter's own dissipation | 24.3 mW at S3', 43.9 mW at IOSmax, 84.3 C on its printed 182.6 C/W; it holds 125 C to 1110 C/W, so no measurement decides it; no automatic restart; a latched event's average at most 2.35 mW at one restart in 10 s |
| (4) T10-A3 with 0.135 ohm at IOSmax on all three | 3.6082 V against 3.5995 V with the 1 A dropout row taken as the bound (+0.0087 V; the dropout rises with current, DESCRIBED) and against 3.4921 V on the INFERRED linear dropout (+0.1161 V); the other two +0.0409 V; U601 and the lead 1.7111 A against 3 A and 10 A |

## 6. The acceptance judge (T10:878-898)

K0 to K9, every limit PRINTED, HOLDS on the printed theta; five mutations each FAIL: a TYPICAL response time used as the response
bound (K0), the TYPICAL ground current used as its maximum (K0), Figure 7-9's guideline used as the site's theta (K0), the AP2112K's
184 C/W on the stage (K2), RILIM at 102 kOhm (K1). The stage reads DRAWN on board B composed with row (b)'s four drafts after round 6's
(1608 parts), and three netlist mutations FAIL (RILIM at 102 kOhm, the AP2112K back on U40, U40 without M3). **L4A-57: DONE AS
CONDITIONAL on E-17**; RE-6 and RE-7 read SUPPORTED ON PRINTED FIGURES, CONDITIONAL on E-17, PROVISIONAL until L4A-62.

## 7. L4A-61: what row (b) restates

- **The T10 rows** (T10:899-919): seventeen rows, each with the line of its old text, which is history from here on: T10-A2, T10-A3 and
  T10-A5; 10j (b)'s share limiter and rail trip (removed by canmb and regstage); V-B23's 0.2 s (stays WITHDRAWN); 10j (c)'s quorum rows
  and the NOT DRAFTED vote (drafted by canmb, canq and canen); 10j (d) and (e) (the limiter's maximum and the constant-dissipation
  bound); the qualification limits (superseded by E-17); VOS0 (unchanged, L4A-59); L9T5-F13, F16, F21, F25 and the babbling row.
- **The connected rows** (CON:364-410): the service window, the final figures and the worst-case margin row on the selected stage
  (+11.2 K, CONDITIONAL on E-17), section 11's rows 5, 6, 7 and 17 under row (b), each keeping cx46's state; finding W151-F1.
- **The re-pinned dependents** (regenerated through `_bin/regen_out.py` in dependency order, each diff read: pin lines only):
  `l4reg_compare.out`, `l9t5_canq.out`, `l9t5_canmb.out` (it pins canq's), `l4canen.out`, `l4hod.out` (it pins canen's),
  `l8r2_dist.out` (it pins `l9t5_connected.py`), `l9t5_connected.out`.
- **Layer 5, `apply_hw_fw_contract_rowb.py`** (after t10's and canq's): FW-B20 (the regulator and its limiter, the rail trip gone,
  TIM3 and an ADC in the enabled set, BOR level 2), FW-B21 (SHDN OR'd with the peers' 2-of-2 vote; W139's stop at the loss count kept),
  FW-B22's restart rule with the in-service test's exception (W143's DAR = 1 text with ES0392's workaround and the self-test kept word
  for word), V-B20 (E-17's site reading), V-B21, V-B23 (the limiter; the rail trip's 0.2 s WITHDRAWN); NEW FW-B24 (the peers' in-service
  test, record l4hod) and V-B25 (its bench rows). FW-B23 and V-B24 are left to HO-E's draft.
- **IOHA section 12, `apply_ioha_fmea_rowb.py`**: rows 21 to 24 (the babbler or GPIO jammer, a load over the limiter, a latent lost
  limit, the vote and test paths' latent faults) and a note naming their V rows; rows 1 to 20 word for word.
- **The ledger's section 4, `apply_remeng_rowb.py`**: a table after section 4's own restating six claims (the LDOs' sustained bound,
  CON-004's quorum, FW-B22, FW-B20 and the controller's survival, T10-A3, the connected final figures), each PROVISIONAL or CONDITIONAL,
  cited at the lines it finds when applied; section 4's own rows and every other section untouched; test_remeng holds on the result.

## 8. The four acceptance states (constitution section 2)

| Deliverable | Document acceptance | Supported design | Implementation | Physical qualification |
|---|---|---|---|---|
| L4A-57, the stage's acceptance | this page, its author only | SUPPORTED ON PRINTED FIGURES, CONDITIONAL on E-17 | the drafts composed, read and mutated; not applied | E-17; V-T10-DROP extended (L4REG-F2) |
| L4A-61, the propagation | this page, its author only | the rows restated, PROVISIONAL or CONDITIONAL | three apply scripts, run on scratch copies only | V-B20, V-B23, V-B25 |

## 9. Findings for other authors

- **W151-F1** (the coordinator, L4-E9's change list): canmb, regstage, canen and hodtest have no rows after iocguard on board B
  (L4REG-F9 for regstage); until they do, the connected candidate's composition is section 2's and T10 11a's the draft's.
- **W151-F2** (the coordinator, C-DEV): row (b)'s enabled set (TIM3, an ADC) and the drafts' rail additions raise a controller's rail by
  at most 0.0073 A and 0.0041 A (labelled scenarios); C-DEV rev 2's 0.1732 A a regulator (rev V) does not carry them. Inside the
  limiter's window (+0.0349 A); a revision of the row is the coordinator's.
- **W151-F3** (the coordinator, Layer 5): `apply_hw_fw_contract_canq.py` and HO-E's `apply_hw_fw_contract_hoe.py` (fnd/l4hoe) each refuse
  unless T10's change record is the page's last row, so as written they cannot both apply; one anchor needs restating before set 33.
  `apply_hw_fw_contract_rowb.py` takes either state and leaves FW-B23 and V-B24 to HO-E's draft.
- **W151-F4** (the ADC's analog supply, the receiving company): ST prints the ADC's VDDA consumption as TYPICAL only (DS12110 Table 184);
  the window takes three times it as an ASSUMPTION; V-B20 reads each supervisor's supply current with its enabled set.
- **W151-F5** (record l9t5, round 6's text): `l9t5_t10.out` 10j and section 11 still read the round 6 containment as written; section 11a
  (j) marks each row's old text as history. The stability digests (`stability/DIGESTS-cr3.txt`) predate this round (CO-14's condition
  is the coordinator's replay).
- **Not this round's** (named, untouched): `l4e7_p0sol.out` pins `l4e11_power.out` and `l4e7_stage_settings.py` at digests the tree no
  longer carries on this branch (the l4e7 KEY group, set 32's re-key on `fnd/int32`).

## 10. SESSION decisions of this round (under the owner's standing rule of 26 September 2026; authority SESSION, ruled_by W151, ruled_on 7 October 2026, reversed_by none)

| Id | Decision | authority_why | To reverse |
|---|---|---|---|
| W151-1 | the output out of regulation excluded from the LDO's junction criterion (section 4) | an exclusion with its reason inside the drafted circuit; nothing the owner reserves changes | E-17's Zth(10 ms) read, or a regulator printing its short-circuit maximum |
| W151-2 | section 11a appended after section 11 in both outputs, the old rows kept as history | every cited line of sections 1 to 11 keeps its number (the ledger, the round pages and the tests cite them) | fold 11a into 10j at the next set with every citation re-cited |
| W151-3 | the conduction screen's h, a and r ASSUMED (5 or 10 W/m2 K, 2 or 3 mm, 10 or 20 mm) and shown as a means | no layout exists to read them from; the screen bounds nothing and decides nothing | read them from Layer 10's layout |
| W151-4 | the ADC's VDDA current at three times ST's TYPICAL in the window | ST prints no maximum; the window keeps +0.0349 A with it | ST's maximum or V-B20's reading |
| W151-5 | the new contract rows numbered FW-B24 and V-B25 | FW-B23 and V-B24 are HO-E's on fnd/l4hoe | renumber with HO-E's at integration |

## 11. Tests

`v2/ecad/tools/tests/test_l9t5_rowb.py` (new): section 11a's figures re-solved from the printed values the outputs name, the judge's
mutants, the connected window, each apply script on scratch copies (once, refused twice, refused without its predecessors, re-parsed;
test_remeng's predicates on the applied ledger), the record's hygiene. `test_l9t5.py`: section 12's count 28 to 34 (six round 10
predicates). The totals as `run.py` printed them are in the round's final report and in the commit that carries this page.

## 12. Reproduce

From the repository root, the held sheets fetched (`v2/docs/records/l4reg/fetch_held_back.py`, `v2/docs/records/l4e11/fetch_held_back.py`
and the fetch scripts `pdftext.FETCH` names): `python3 v2/docs/records/l9t5/l9t5_t10.py` (about 30 s) and
`python3 v2/docs/records/l9t5/l9t5_connected.py` (about 20 s); outputs through `_bin/regen_out.py` in the order of section 7; tests:
`env -C v2/ecad/tools python3 tests/run.py test_l9t5_rowb.`

The constitution was read and is acknowledged (sections 3 to 6 and 8): the acceptance is on printed figures with every typical named
and refused as a bound, the missing site figure is a named measurement rather than a passed bound, and the propagation restates rather
than relabels.
