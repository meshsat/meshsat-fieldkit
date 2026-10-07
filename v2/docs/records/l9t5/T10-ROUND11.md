**ROUND 11 (T10; row (b)'s corrections on W157's focused check L4A-62, Q-182; 7 October 2026, W159, branch `fnd/l4hod`, the one writer after W151): DONE: fnd/l4small (77866143) and fnd/l4lim (aa6704b2) merged into fnd/l4hod in W157's order, so fnd/l4hod is row (b)'s composite for set 33; F1 (the blocker) corrected: rowb's FW-B20 states L9T5-D11's words and applies before or after apply_l4small_revx.py with one page; F2 the limiter's band restated on TI's Equation 1 (0.4702 to 0.5878 A) and carried through every row that used 0.5704 A; F3, F4, F5, F8 corrected; F6 read on RM0433; F7 drafted (the peers' hold-off); F9 to F11 stated. NOT DONE: no independent check of this round (Q-183, the targeted recheck of F1 with F2's restatement, is next); nothing applied to the tree; E-17, W146-F10 and HO-E stay open. NEXT: Q-183. Nothing in this kit has been built, bought, powered or measured; nothing here closes a cx46 item.**

# T10 round 11: row (b)'s corrections after its focused check

- **Author:** W159 (Claude), MESHSAT-1357, 7 October 2026 from 10:57 CEST (times from `date`, Europe/Amsterdam). Branch `fnd/l4hod`,
  base `e51c1bd9` (W151's round 10), then `925a1efd` (fnd/l4small merged) and `f83879dc` (fnd/l4lim merged).
- **Failure cases read against:** W157's report (`_runs/claude/w157chkrowb/REPORT-FULL-AS-RECEIVED.md`, an AI review): row (b) NOT
  SUPPORTED AS COMPOSED on one clerical blocker F1; RE-5 and HO-C SUPPORTED; RE-6 and RE-7 SUPPORTED AS CONDITIONAL (E-17); HO-D
  SUPPORTED AS CONDITIONAL (W146-F10); findings F2 to F8 should fix, F9 to F11 notes. No verdict is upgraded here: this round is a
  correction, and the verdicts are the recheck's (Q-183).
- **Case rows:** C-DEV rev 2's T10 figures as record l9t5 carries them (14.0k corner, 76.25 C inside air, revision V). F9's figures are
  for the coordinator's revision of C-DEV; this round keeps working on the current row.

## 1. The findings and what this round did

| Id | W157's class | What was wrong | Correction | Evidence |
|---|---|---|---|---|
| F1 | blocks | `apply_hw_fw_contract_rowb.py` anchored FW-B20 on t10's text before `apply_l4small_revx.py`, so after revx it refused, and without revx it wrote "revision X held until its own qualification, V-B20" (L9T5-D11 removes that route) | FW-B20 now states L9T5-D11's words ("revision X NOT ADMITTED, record l9t5 SESSION L9T5-D11"); the anchor takes either form t10's script writes (revx-edited first, before revx second): SESSION W159-D1 | `test_l9t5_rowb.t_rowb_and_revx_apply_in_either_order_with_one_page`: revx then t10, canq, rowb, and t10, canq, rowb then revx, give one page; each script refuses a second run; the admission words are absent and a mutant carrying them is caught |
| F2 | should fix | the limiter's upper edge taken as 0.5704 A (the 7.5 row's 565 mA through the exponent), where TI's own procedure (SLVS841F 10.2.1.2.3 and Table 2: Equation 1 at the 1 % resistor's bounds) gives 0.5878 A | the band is the ENVELOPE of both readings, 0.4702 to 0.5878 A (`l4reg_compare.py` `band_env`, `l9t5_t10.py` 11a, `l4hod.py`): SESSION W159-D2; carried into the junction, T10-A3, E-17's pass limit, HO-D's pass band, V-B23 and every contract row (section 2) | `l9t5_t10.out` 11a (c), (d), (e), (g), (h); `l4reg_compare.out` section 2; `l4hod.out` section 7; `test_l9t5_rowb`, `test_l4reg`, `test_l4hod` re-solve the edge from the printed constants |
| F3 | should fix | fnd/l4lim in the composition: `pdftext.FETCH` lacked l4lim's fetch script; `test_l4lim.py` reached pdftotext through `l4lim_screen.pdf()` | `l4lim_screen.py` reads its six sheets through `_lib/pdftext.py` (a literal PDFTEXT table, the two new held texts taken, its output pins the texts); FETCH lists l4lim for the TPS2553 sheet and for the TPS25200 and AP22652/53 sheets | `l4lim_screen.out` regenerated (its figures unchanged); `test_pdftext_input`, `test_l4lim` |
| F4 | should fix | "HO-E unchanged by the limiter" understated L4REG-F7: the rail trip's controller-protection role (each controller's average under its own 125 C current) is not held by the limiter | restated in T10 11a (h) and (j), the connected record's item 17, rowb's FW-B20 and the ledger script's row ("WEAKENED by row (b) ... moves to HO-E"), and in record l4reg's W138-2 authority row | `l9t5_t10.out` 11a (h), (j) line 674; `l9t5_connected.out` 11a (d) |
| F5 | should fix | 42 SESSION decisions without the explicit fields; W138-2's removal of a protection without its reason written out; L9T5-D11's text citing the removed rail trip | each page gains a table of the fields (`T10-ROUND6.md` W137-D1 to D9, `T10-CANQ.md` W139-D1 to D12, `T10-ROUND9.md` W143-D1 to D10, `L4REG.md` W138-2 to W138-7, `L4LIM-SCREEN.md` W135-1 to 6: 43, W138-7 being the one W157's count missed); W138-2's and W137-D2's protection removals written out; L9T5-D11's decision and reversed_by restated on the selected stage (`apply_l4small_revx.py`) | the five pages' last section; `test_l4small` |
| F6 | should fix | HO-D's one-test-per-transient rule rested on backup-register retention through a brown-out, RM0433 unread | read: a BOR reset is a system reset (RM0433 Rev 8 p.329) and the backup registers are not reset by a system reset (p.1919), so a survivor reset by BOR keeps the record; the backup domain is reset when VSW leaves its range (p.333) and board B ties each VBAT to its supervisor's +3V3_IOCx, so a dip under the power-down threshold may clear it: an ASSUMPTION bounded by V-B25 (each survivor's 3.3 V over VBOR2's 2.37 V, above DS12110's highest falling PDR 1.68 V), with DBP set before each write and clear, tamper erase off and no BDRST at boot (ES0392 2.2.20's workaround not taken) | `l4hod.out` section 7 (the quotes read from the committed page texts), `L4HOD.md` section 3 |
| F7 | should fix | an output short drawing under IOSmin is never limited, and the restart rule retried every 10 s for the mission | DRAFTED HOLD-OFF in FW-B22: after 3 consecutive failed restarts both peers keep their restart votes (the limiter's EN low, the target unpowered) and retry once every 600 s; SESSION W159-D3; IOHA row 22 and V-B23 carry it | `l9t5_t10.out` 11a (f) (iii): powered 80 % of the mission without it, 1.33 % in the hold-off; three mutations FAIL (no hold-off, retries at the restart period, a hold-off one peer's vote holds); `test_l9t5_rowb.t_the_hold_off_bounds_a_short_under_iosmin` |
| F8 | should fix | W151-F1 (no change-list rows for the four drafts) and W151-F3 (canq's and HO-E's contract scripts both demanded t10's change record as the last row) | `apply_l4e9_changelist_rowb.py` (a TEXT DRAFT, not applied): R-247 to R-250 after R-245 and before R-236 in L4-E9's own change list (122 changes), with six order constraints; `apply_hw_fw_contract_canq.py` takes t10's or HO-E's change record as the last row, so t10, hoe, canq, rowb apply in that order | `test_l9t5_rowb.t_the_change_list_rows_for_the_four_drafts`, `t_canq_applies_after_hoe_and_rowb_after_both` (a stand-in for HO-E's rows) |
| F9 | note | C-DEV lacks row (b)'s +0.0073 A (TIM3 and an ADC in FW-B20's enabled set) and +0.0041 A (the drafts' rail additions) | stated for the coordinator's revision of C-DEV; this round works on rev 2 with the two figures as a LABELLED SCENARIO (the window +0.0349 A on the composed candidate) | `l9t5_connected.out` 11a (b) |
| F10 | note | the limiter's own die during the hourly test (about 1.54 W for at most 10 ms) is not bounded on printed figures | added to V-B25: no FAULT EARLY on a healthy part at 76 C air, a FAULT EARLY read as the safe outcome it is | rowb's V-B25 |
| F11 | note | T10 11a (d) printed IOUT where it meant I_IN; W139-D10's timer behaviour is not described by TI's sheet | (d) reads "(VIN - VOUT) x I_IN + VOUT x IGND" (the bound is unchanged: P falls as VOUT rises, so VOUT_min is the worst); W139-D10's authority row states that no single-fault row depends on the timer | `l9t5_t10.out` 11a (d); `T10-CANQ.md` last section |

## 2. The figures on the envelope (every one a MODEL on PRINTED rows; the earlier column is history)

| Figure | At 0.5704 A (W138, W146, W151) | At 0.5878 A (W159) | Where |
|---|---|---|---|
| the limiter's band, RILIM 49.9 kOhm 1 % | 0.4702 to 0.5704 A | 0.4702 to 0.5878 A | `l9t5_t10.out` 11a (c) |
| the TPS73733DCQRM3's junction at constant maximum dissipation, IGND = 0, printed 76.0 C/W | 113.8 C | 115.0 C (margin 10.0 K) | 11a (d), K2 |
| the IGND 125 C admits | 45.2 mA | 40.6 mA | 11a (d) |
| E-17's pass limit (the theta that holds 125 C at IOSmax, IGND = 0) | 98.6 C/W | 95.7 C/W | 11a (d), (e) |
| E-17's latched transient | 2.348 W, 36.2 K, Zth(10 ms) 15.4 C/W | 2.420 W, 35.0 K, Zth(10 ms) 14.5 C/W | 11a (e) |
| T10-A3 at IOSmax on all three | +0.0087 V (1 A row), +0.1161 V (INFERRED) | +0.0041 V, +0.1072 V | 11a (g) (4), K6 |
| three limiters' maxima against U601's 3 A | 1.7111 A | 1.7634 A | K7 |
| the window over the largest served state | 0.0463 A | 0.0462 A (the least moves by 0.05 mA on the envelope) | 11a (g) (1), K1 |
| the window on the composed candidate | +0.0349 A | +0.0349 A | `l9t5_connected.out` 11a |
| HO-D: a healthy limiter reads | 0.4345 to 0.6140 A (a healthy part at 0.5878 A would read up to 0.6326 A and fail) | 0.4345 to 0.6326 A | `l4hod.out` section 7, J4 |
| HO-D: a PASS admits | 0.4023 to 0.6620 A, the regulator at 119.9 C or less | 0.4023 to 0.6819 A, at 121.2 C or less (under the 0.7399 A that reads 125 C) | J4 |
| HO-D's margins | B up to 78.4 mA, ADC error +-83 mV | B up to 58.5 mA, ADC error +-64 mV | `l4hod.out` section 7 |
| the latched energy at IOSmax | 23.5 mJ | 24.2 mJ | 11a (f), K4 |

The selection W138-1 stands on the envelope (the legacy TPS73733 and the AP2112K still fail; `l4reg_compare.out`). W135's screen
(`l4lim_screen.out`) keeps its own rule's 0.570 A: it is the CHANGE-METHOD screen whose line does not depend on the edge (its
requirement on the regulator, at most 98.6 C/W at 0.570 A, becomes 95.7 C/W at 0.5878 A, and the selected part's printed 76.0 C/W
meets both), so it is left as W135 computed it; the current band is record l4reg's `band_env` (SESSION W159-D4).

## 3. SESSION decisions of this round

Each under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026; ruled_by W159 (Claude), MESHSAT-1357;
ruled_on 2026-10-07; reversed_by none (the way back is the last column).

| Id | Decision | authority | authority_why | To reverse |
|---|---|---|---|---|
| W159-D1 | rowb's FW-B20 states L9T5-D11's words and is anchored on either form of t10's FW-B20 (revx-edited first) | SESSION | a clerical correction of a contract draft's anchor and words: no part, net, figure or verdict changes; anchoring on revx's form alone would fix the order (revx before t10) and leave rowb refused on a tree where t10 ran first, so one option stands | anchor on the revx form only and require revx before t10 in set 33's order |
| W159-D2 | the limiter's band is the envelope of the tested row through the exponents and TI's Equation 1 at the 1 % resistor's bounds: the lower least, the larger most | SESSION | TI's own procedure (10.2.1.2.3, Table 2) calculates the threshold limits from the equations at the resistor's bounds and says the equations include temperature and process; the 7.5 row's 565 mA is narrower; the larger maximum is the conservative one for the junction and E-17, and HO-D's band must admit it or it fails a healthy part; no requirement, class, purchase or claim changes; one option stands (taking the narrower row is picking the number that passes) | a TI statement that the 7.5 row bounds the system-level threshold with a 1 % resistor (none read), then every figure of section 2 back |
| W159-D3 | the peers' hold-off: after 3 consecutive failed restarts of one supervisor both peers keep its restart votes and retry once every 600 s, a rejoin clearing the count | SESSION | it bounds the time a regulator is powered into a short under IOSmin (80 % to 1.33 %) without lowering a service: two of three serve throughout, a single latch still restarts in 5.603 s, and only a cause lasting over three restarts returns up to 600 s later; the hold needs both peers' votes (canen's 2-of-2), so one faulty peer cannot hold a healthy supervisor off; one option stands after the judge (each mutation FAILS) | a regulator printing its short-circuit current with a maximum under IOSmin (then the limiter latches the short), or another N and retry with 11a (f) (iii)'s judge re-run |
| W159-D4 | the composition merges in W157's order (l4hod, l4small, l4lim; both branches not written again); W135's screen keeps its own band (section 2); the AP22652/53 sheet staged from fnd/l4lim's worktree (held back, its sha256 checked by `fetch_held_back.py`) | SESSION | clerical: two clean merges and the held sheet the fetch script names; no figure of the screen's verdict depends on the edge | re-compose in another order (the two merges touch no common file) |

## 4. What stays open (unchanged in kind by this round)

- **E-17** (the receiving company's measurement; nothing sent): first-article board B or a six-layer coupon, three sites; each regulator's
  junction at the limiter's printed maximum 0.5878 A with 4.1174 V input, by psi-JT 8.6 C/W, 76.25 C still air; pass limit 125 C (95.7
  C/W at IGND = 0); the latched transient's Zth(10 ms) at most 14.5 C/W or W151-1's exclusion kept. RE-6 and RE-7 stay CONDITIONAL on it.
- **W146-F10** (HO-D's supply dip at the test's load step): PROVISIONAL; V-B25's pass limits unchanged.
- **F6's assumption:** the step record's retention under a dip below the power-down threshold, bounded by V-B25 and the firmware
  conditions above; a check, not a closure.
- **HO-E** (L4A-59, its check L4A-100, fnd/l4hoe): now carries the rail trip's controller-protection role; `apply_gen_sch_b_vcoremon.py`
  on fnd/l4hoe has no change-list row either (HO-E's task).
- **Row (b)'s verdict:** the targeted recheck Q-183. cx46 stays CORRECTIONS NOT CLOSED, Layer 4's DESK gate NOT PASSED.

## 5. Reproduce

From the repository root, in dependency order through `_bin/regen_out.py <worktree> <script> <output>`: `l9t5/l9t5_t10.py`,
`l4reg/l4reg_compare.py`, `l9t5/l9t5_canq.py`, `l9t5/l9t5_canmb.py`, `l4canen/l4canen.py`, `l4hod/l4hod.py`, `l8r2/l8r2_dist.py`,
`l9t5/l9t5_connected.py`, `l4lim/l4lim_screen.py` (held sheets: the fetch scripts of records l4reg, l4canen and l4lim; the texts:
`python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l4hod` and `.../l4lim`). Apply drafts, never on the tree: the
contract order t10, (hoe,) canq, rowb, with revx before or after; `apply_l4e9_changelist_rowb.py --check`. Tests: `env -C
v2/ecad/tools python3 tests/run.py test_l9t5_rowb.` and the modules listed in the round's commit.

The constitution was read and is acknowledged (sections 3 to 6 and 8): each correction is checked against its own failure case, the
one design change (the hold-off) has a judge whose mutations fail, no verdict is upgraded, and the recheck is the next step.
