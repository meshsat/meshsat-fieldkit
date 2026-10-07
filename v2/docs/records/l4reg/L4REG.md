**Status (7 October 2026, 06:24 CEST): DONE: Layer 4 task L4A-56 as re-scoped by W135's CHANGE-METHOD: three approaches compared on printed figures (A the TPS2553-1 limiter with a replacement regulator; B K1, a buck per supervisor; C the regulator's own limit), A selected (SESSION W138-1: TI TPS2553-1 at RILIM 49.9 kOhm with TI TPS73733DCQRM3), its draft `apply_gen_sch_b_regstage.py` composed after record l9t5's iocguard and with W137's canmb in either order, read by pin and value, eight mutations failing, three refusals; the acceptance judge with five failing mutations; the tests (test_l4reg: "tests: 8 passed, 0 failed, 0 skipped"; test_pdftext_input: "tests: 19 passed, 0 failed, 0 skipped"; test_l9t5 with test_applier_state: "tests: 62 passed, 0 failed, 0 skipped"). NOT DONE: no independent check; nothing applied; L4A-57's, L4A-58's and L4A-61's own work; nothing physical. NEXT: the coordinator's reading, then one focused independent check of the selection (constitution section 6).**

# Record l4reg: the supervisors' regulator stage (Layer 4 task L4A-56, re-scoped by W135's CHANGE-METHOD; RE-6 and RE-7)

- **Author:** W138 (Claude), MESHSAT-1357, 7 October 2026 from 05:46 CEST (times from `date`, Europe/Amsterdam). Branch `fnd/l4reg`
  from `fnd/int32` `06d064ffa58a1211139d0f1d8e7b536675a67948`.
- **Why:** W135's screen (record l4lim, `fnd/l4lim` `aa6704b2`, copied verbatim to `inputs/`) read CHANGE-METHOD for L4A-56: a
  limiter ahead of the AP2112K has no window on printed limits (its 125 C current at the corner, 0.3056 A, sits under row 7's served
  peak 0.4240 A). It recommended (SESSION W135-1) the TPS2553-1 at 49.9 kOhm with a replacement regulator of printed junction-to-ambient
  at most 98.6 C/W, at least 0.57 A and a dropout that keeps T10-A3, with K1 as the fallback. Constitution section 4: an unresolved
  design choice compares at most three materially different approaches and selects within authority. Row (b)'s regulator half is
  Layer 4's critical path (the register, `_runs/l4ai/REGISTER.draft.md`, rows L4A-56 to L4A-59 and L4A-101; W127's check 1a).
- **Framing:** prototype design. Nothing has been built, bought, powered or measured. Every junction figure is a MODEL on printed
  thermal resistances, never a measured temperature. This record closes no cx46 item and moves no state: cx46 CORRECTIONS NOT CLOSED
  and Layer 4's DESK gate NOT PASSED stand; RE-6 and RE-7 stay NOT CLOSED until an independent check reads this selection.
- **Evidence:** `l4reg_compare.py` prints `l4reg_compare.out` (regenerated with `_bin/regen_out.py`; cited OUT section). It imports
  record l9t5's T10 and drafts modules for the rows, the supply path and the compositions, reads every maker's figure from the
  committed or held texts through `v2/docs/records/_lib/pdftext.py`, and reproduces record l9t5's corner and T10-A3 and W135's figures
  before using them. Its test is `v2/ecad/tools/tests/test_l4reg.py`.
- **Labels:** PRINTED (a maker's limit or tested row), TYPICAL, DESCRIBED (the maker's prose, no limit), DECLARED, MODEL, INFERRED,
  ASSUMPTION, SESSION. A TYPICAL figure is never used as a limit (the judge refuses one at J0 and FAILS, OUT 8).

## 1. The rows every approach is judged on (OUT 2)

At record l9t5's corner: revision V (fitted, L9T5-D7), R602 14.0 k (L9T5-D9), 76.25 C inside air, the pre-regulator 3.9063 to 4.1174 V,
the LDO's worst drop 0.8669 V. Criterion: 125 C for every sustained state, 150 C the absolute maximum, never an operating target.

| Row | Current a regulator | Source |
|---|---|---|
| S1, the largest sustained served state | 0.1855 A | T10 10j (e), MODEL |
| S2, both transceivers dominant (normal service's peak) | 0.2839 A | T10 10i, MODEL |
| (f1), one fabric faulted on the TCAN334's 180 mA PRINTED row | 0.3726 A | T10 section 8, MODEL |
| S3', IOHA row 7 with the healthy fabric's bit (largest, B5) | 0.4240 A | T10 10e and W135-3, MODEL |
| (f2) and rev V held, row 8 (survive only) | 0.5491 and 0.5639 A | T10 section 8 and 10e, MODEL |
| HO-E: the H743 at its 105 C VOS0 limit; its own 125 C | 0.1936 A; 0.328 A | T10 10j (c) and section 4, MODEL |

## 2. The three approaches (OUT 4 to 7)

| Row | A: TPS2553-1 at 49.9 kOhm + TPS73733DCQRM3 | B: K1, an AP63203 per supervisor | C: the regulator's own limit, no limiter |
|---|---|---|---|
| Window, served rows | none limited: IOSmin 0.4702 A over S3' by +0.0462 A, over (f1) by +0.0976 A | none limited (no limit under 2.5 A) | none limited |
| Row 8 | (f2) and 0.5639 A inside the band 0.4702 to 0.5704 A: may latch off after 5 to 10 ms (the outcome row 8 accepts; recovery by EN or power) | unlimited | unlimited |
| Regulator junction, 76.25 C air, PRINTED theta | 113.8 C at the limiter's maximum 0.5704 A (76.0 C/W, SBVS067W 5.4, new silicon DCQ); holds to 98.6 C/W | no printed bound: on-resistance and efficiency TYPICAL only (93.2 C on the DECLARED 0.88, not a bound) | 221.2 C (DCQ), 170.5 C (DRB) at its printed 2.2 A maximum: FAILS |
| Output short | (i) latched within 10 ms PRINTED, at most 23.5 mJ; (ii) a hard short under IOSmin excluded (SESSION W138-3, W135-2 carried); the part prints "Output short-circuit duration: Indefinite" | hiccup 2 ms on, 16 ms off, DESCRIBED only; 2.5 to 3.1 A at the switch from the shared rail, no per-branch limit | foldback TYPICAL only, no timer: unbounded |
| T10-A3 | +0.1161 V at 0.5704 A on all three (3.6082 V against 3.4921 V; the dropout INFERRED linear from 250 mV at 1 A) | input 3.7579 V at most, under the AP63203's recommended 3.8 V: FAILS at 14.0 k (R602 back to 10.7 k needed) | as A's regulator |
| Area a supervisor (MODEL on package outlines) | +49.7 mm2 against the tree, +24.6 mm2 against round 6's drafted state; 3.1 % of the 1624 mm2 pocket | +23.5 mm2 (+35.5 with A's limiter) | +37.8 mm2 |
| Board A | unchanged (R602 14.0 k kept) | R602 10.7 k: iocpre and iocset withdrawn, L9T5-D9 reversed | unchanged |
| HO-E | not covered: IOSmin is over VOS0's 0.1936 A and the H743's 0.328 A; the served 0.1855 A against 0.1936 A is a 4.4 % band no limiter reaches, which A neither narrows nor widens (L4A-59) | not covered | not covered |
| Verdict | HOLDS on its rows (the judge, OUT 8) | NOT SUPPORTED ON PRINTED FIGURES; the fallback | FAILS; not taken |

**Within A, the regulators read** (OUT 4, each at the limiter's maximum from the corner):

| Part | C/W PRINTED | Junction | Dropout at 0.5704 A (INFERRED) | T10-A3 margin | Verdict |
|---|---|---|---|---|---|
| AP2112K-3.3 (SOT25), as drawn | 184.0 | 167.2 C | 0.3802 V | -0.1404 V | FAILS |
| TPS73733DCQRM3 (SOT-223, new silicon only) | 76.0 | 113.8 C | 0.1426 V | +0.1161 V | selected |
| TPS73733DCQR (no M3: legacy silicon may ship) | 76.0 | 113.8 C | 0.2852 V | -0.0760 V | FAILS |
| TPS73701DRBRM3 (VSON-8, adjustable, 0.1 % divider) | 49.4 | 100.7 C | 0.1426 V | +0.1095 V | the alternate |
| TLV75733PDYDR (SOT-23-5 DYD) | 92.5 | 122.0 C | 0.2852 V | -0.0265 V | FAILS |
| TLV75733PDRVR (WSON-6) | 100.2 | 125.8 C | 0.2709 V | -0.0122 V | FAILS |
| TPS7A3701DRVR (WSON-6, adjustable) | 67.2 | 109.5 C | 0.1141 V | +0.1545 V | a second alternate |

The M3 suffix decides it: TI's Table 8-1 (SBVS067W p.29) reads "M3 is a suffix designator for devices that only use the latest
manufacturing flow (CSO: RFB). Devices without this suffix can ship with the legacy silicon (CSO: DLN) or the new silicon"; the legacy
silicon's 500 mV and +-3 % fail T10-A3 at the limit, the new silicon's 250 mV and +-1.5 % hold it.

## 3. The selection

**SESSION W138-1: approach A, TI TPS2553-1 (SOT-23-6, latch-off) at RILIM 49.9 kOhm 1 % with TI TPS73733DCQRM3 (SOT-223-6, new
silicon only) at each supervisor, in place of round 6's rail trip.**

- **authority:** SESSION, under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026.
- **authority_why:** an engineering selection among approaches on printed figures inside the drafted circuit. No requirement, protected
  class, case row, purchase or publication changes, and one option stands after the reading: B and C fail on printed figures.
- **ruled_by:** W138 (Claude), MESHSAT-1357. **ruled_on:** 7 October 2026. **reversed_by:** none.
- **To reverse:** the alternate within A (TPS73701DRBRM3 with a 0.1 % divider, or TPS7A3701DRVR), or B with R602 back to 10.7 k, or
  W135's second-source limiter (Diodes AP22653A, record l4lim).
- **End condition:** the method ends if E-17's coupon (or the first article) reads the regulator's junction-to-ambient over 98.6 C/W
  at a U40, U50 or U60 site in still air at 76.25 C; or V-T10-DROP (extended, L4REG-F2) reads its output outside 3.0 to 3.6 V between
  VOUT + VDO and VOUT + 0.5 V at up to 0.5704 A; or two negative independent checks of this selection.

The other SESSION decisions, each with its reason and reversal:

| Id | Decision | Why | To reverse |
|---|---|---|---|
| W138-2 | round 6's rail trip (R600, U46, C941, C942 and their siblings) removed; its INA169s' places take the limiters | the register's M-A replaces it (W127's cost reading); in series with the limiter its 0.3 ohm costs T10-A3 at the limit (3.4354 V against 3.4921 V, MODEL); cx46 withdrew its response and its sustained bound | keep iocguard's rail trip (drop edits 1 and 2 of the draft) and restate T10-A3 |
| W138-3 | W135-2's exclusion carried: a fault on the supervisor's own 3.3 V that draws under IOSmin (a hard short in foldback, or a partial short out of regulation) is excluded from the regulator-junction criterion | that supervisor is lost (IOHA row 3); the other two keep their supply (each branch at most IOSmax, PRINTED); the TPS737 prints "Output short-circuit duration: Indefinite" (SBVS067W 5.1) | a regulator printing its short-circuit current with a maximum under IOSmin, or the peers' EN made a hardware timer |
| W138-4 | the LDO's EN pulled up from its own input (R66, R78, R90 from IOC_LDO_IN, was +5V_IOC) | the TPS737 prints EN high from 1.7 V to VIN (5.6); the bench jumper still holds it off | R66 back to +5V_IOC (EN then over VIN by the limiter's drop) |
| W138-5 | no new designator: the limiters take U45, U55, U65, RILIM R601, R621, R641, the EN pull-ups R602, R622, R642, the IN capacitors C940, C950, C960 | composes with W137's canmb with no designator shared (canmb adds R611 to R654, reuses U47, U48 and C944, C946) | fresh designators in a free range |
| W138-6 | the draft lives beside iocguard in record l9t5, release-guarded by RELEASE-T10.md | it edits iocguard's lines, as canmb does; L4-E9's change list addresses the T10 drafts there | move it to record l4reg with its own release file |
| W138-7 | `_lib/pdftext.py`'s FETCH gains the four held TI sheets for record l4reg | test_pdftext_input's W37 map requires a fetch route for every declared held sheet | drop the declarations with the sheets |

## 4. The draft (OUT 9)

`v2/docs/records/l9t5/apply_gen_sch_b_regstage.py`, a successor of iocguard; **None is APPLIED** (release-guarded by RELEASE-T10.md).
Six edits on board B's generator: U40, U50, U60 become TPS73733DCQRM3 (SOT-223-6: 1 IN, 2 OUT, 3 GND, 4 NR open, 5 EN, 6 GND tab); R66,
R78, R90 from the LDO's input; the rail trip's eight parts a supervisor replaced by the limiter (IN on +5V_IOC, OUT on IOC_LDO_IN, EN on
IOC_LIM_EN through 100 kOhm to +5V_IOC, ILIM through 49.9 kOhm 1 % to GND, FAULT open) and its 100 nF; the bypass and decoupling-class
entries; +5V_IOC's load allocations on U45, U55, U65; the rail's source text.

- Composed in L4-E9's order after iocbuck, iocpre, canshdn, iocset and iocguard (17 drafts): every step OK; the generator ran to its
  end; read by pin and value: **DRAWN**. The state before it (iocguard's rail trip): FAIL.
- Mutations, each FAIL: the limiter bypassed; the LDO's IN and OUT exchanged; the LDO's EN on ground; the limiter's EN on ground;
  RILIM's ground end on the EN pull-up's rail; RILIM at 102 kOhm (W135's band under the AP2112K); the AP2112K back on U40; U40
  ordered without M3.
- With W137's canmb (its checkpoint `31de4bbc`, copied to `inputs/`): DRAWN in either order, the two netlists identical. **Shared:**
  no designator, no signal net, no controller pin; both attach parts to the rails +5V_IOC, +3V3_IOCA, +3V3_IOCB, +3V3_IOCC and GND.
- Refused: a generator without iocguard; a second application; the tree's own generator (NOT RELEASED).
- Record l9t5's own I-03 check reads LDO FAIL on this composition (it expects round 6's sense resistor): L4REG-F1.

## 5. Round 1 (7 October 2026): L4A-56 as re-scoped

| Deliverable | Document acceptance | Supported design | Implementation | Physical qualification |
|---|---|---|---|---|
| The stage (W138-1) | read by its author only | HOLDS on printed figures on its rows (J1 to J7, OUT 8); T10-A3 on an INFERRED dropout; the regulator's theta on JEDEC copper | the draft composed, read and mutated; not applied | E-17 (the site's theta, pass at most 98.6 C/W), V-T10-DROP extended (L4REG-F2) |

What it offers once independently checked: RE-7's peak-current containment (a constant-power bound on the regulator at the limiter's
printed maximum, for every waveform under the limit with the output in regulation, cx46's periodic countermodel included) and RE-6's
response replaced by a printed limit with a printed latch timer (the limiter's response itself, 2 us, is TYPICAL only and is not used:
the bound is the DC limit; the regulator's ground current, 880 uA TYPICAL at 1 A with no maximum printed, is outside it: 3.6 mW,
0.28 K on the printed theta, MODEL on a TYPICAL, against the 11.2 K margin). It does not close, and leaves open: HO-D (the limiter's latent loss of its limit, L4A-58), HO-E (L4A-59),
the realisation of the printed theta on board B's copper (E-17), the band between VOUT + VDO and VOUT + 0.5 V (V-T10-DROP), the
propagation into T10's rows and Layer 5's FW-B20 to FW-B22 and V-B20 to V-B23 (L4A-61), and the given-up average bound on the
controller's own current (L4REG-F7). L4A-57's acceptance can read the judge's J2 on the printed steady theta (W135's finding for it).

## 6. Findings for other authors (OUT 10)

- **L4REG-F1** (Slot A, record l9t5's `check_l9t5_netlist.py`): its board B LDO entry reads round 6's sense resistor, EN on pin 3 and R66
  from +5V_IOC; with this delta the limiter joins the LDO's input to +5V_IOC, EN is pin 5, R66 runs from IOC_LDO_IN: to restate when taken.
- **L4REG-F2** (Layer 5 V rows and the receiving company, V-T10-DROP extended): the TPS73733DCQRM3's output between VOUT + VDO and
  VOUT + 0.5 V at 0.01 to 0.5704 A and -40 to 125 C TJ, its start-up into the controller in reset (foldback, 6.3.2) and its power-up
  overshoot with EN from its input (6.3.3): specimen three first-article board B supervisors, pass limit 3.0 to 3.6 V.
- **L4REG-F3** (L4A-54, L4A-58): each limiter's EN (IOC_LIM_EN) is the node for the peers' restart of a latched supervisor and the
  in-service over-limit test; FAULT is open for L4A-58; a restart bounds its own rate (W135 row 3).
- **L4REG-F4** (Layer 6 and Layer 12): order codes owed for the TPS2553-1 (DBV, latch-off) and TPS73733DCQRM3; the M3 suffix is the
  identity row; the reel label's CSO RFB is read at incoming inspection.
- **L4REG-F5** (Layer 10): the land id `Package_TO_SOT_SMD:SOT-223-6` is this draft's ASSUMPTION (kisch's land check runs only where
  KiCad is); the printed 76.0 C/W assumes JEDEC 2s2p copper with a 3 x 2 via array under the tab.
- **L4REG-F6** (Layer 10, `gen_pcb_b3.py`): the controller pockets' region lists carry no part of any P0 draft yet.
- **L4REG-F7** (L4A-59, HO-E): round 6's rail trip held each controller's average at 0.2183 to 0.2452 A, under its 125 C current 0.328 A
  (PROVISIONAL); with it removed no hardware bounds a firmware outside FW-B20: H-2's watchdog proof should cover every state outside
  FW-B20, not VOS0 alone.
- **L4REG-F8** (the coordinator): when record l4lim is merged its fetch script lists the TPS2553 sheet too, and pdftext.FETCH's entry
  becomes ("l4lim", "l4reg").
- **L4REG-F9** (the coordinator, L4-E9's change list): `apply_gen_sch_b_regstage.py` needs its row on board B after record l9t5's
  iocguard (and W137's canmb, either order); the register's rows L4A-56 and L4A-57 read this record's selection.

## 7. What this record does not do

It runs no independent check and applies nothing. It does not compute either part's junction during a latched event (no transient
thermal impedance is printed), the K1 buck's loss on printed figures (none is printed), the switching ripple of K1, or the limiter's
response time (TYPICAL only). It does not settle the realisation of the regulator's printed theta on board B's copper (E-17), the band
under VOUT + 0.5 V (V-T10-DROP), or the HO-D test. The register and the ledger are the coordinator's to restate.

## 8. Reproduce

```
python3 v2/docs/records/l4reg/fetch_held_back.py                       # the four held TI sheets, checked by sha256
python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l4reg   # their texts, held back with them
python3 v2/docs/records/l4reg/l4reg_compare.py                         # prints l4reg_compare.out (about 15 s)
env -C v2/ecad/tools python3 tests/run.py test_l4reg
```

The constitution was read and is acknowledged (sections 3 to 6 and 8): the design choice compared at most three materially different
approaches, the selection is within authority, every limit is a printed one, and the failing mutations exercise the failure cases.
