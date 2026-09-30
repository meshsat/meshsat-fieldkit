# RESULT: AI review of the cx1 candidate (finding I-03, IF-AB-POWER), MESHSAT-1357

Independent checker, 28 September 2026 19:30 CEST. Candidate: commit b1c744db on fnd/cx1 (base 6b419b02), four
files under `v2/docs/records/cx1/`. Blind phase 1 (`PHASE1.md`, `phase1.py`, `phase1.out`) was on disk before any
candidate file was opened; the comparison is `CHECK.md`. All under
`<worktrees>/_scratch/chk-cx1/`. Prototype framing: nothing built, ordered or
measured; this is an AI review, not a qualified review.

- **acceptable as a record: yes** (as a filed analysis of I-03: its arithmetic reproduces byte for byte, every
  citation I opened is on the page it names, every bound is labelled a bound, nothing is lowered)
- **supports a change of declaration: no** (the candidate's conclusion, and no held document decides a mode figure;
  the checker adds that the sources DO support an interim alignment of the two ends, item B1 below)

## Blocking items (for I-03's closure, not for filing the record)

- **B1. The empty draft leaves board A's +5V_S2 at a figure the record itself shows to be stale.** A's 2.5 A typical
  and 5.0 A peak carry the AP64500-era note "5 A peak at the module" (gen_sch_a.py:104-113); slot 2's converter has
  been an LM5176 with a 7.17 A minimum loop since F-PR-04. Board B derives 4.157 A typical and 5.628 A coincident from
  the held maker pages (CM5 0.9 A, PDF p.16 and Table 9 p.28; Quectel 3.0 A v1.0 p.28 and 4 A v1.1 p.30) and the
  candidate reproduces both. The declared current is what `dc_drop` and `derate` judge board A's copper at
  (gen_sch_b.py:29-33), so leaving 2.5 A judges A's slot 2 copper 1.66 A low; understating is not the conservative
  side. Counter-example to "no number may be selected": one conductor cannot carry two declarations, and the end that
  derives its figure is the one to align to. The interim change the sources support, labelled as interim: A's +5V_S2
  typ 2.5 to 4.2, peak 5.0 to 5.63, load J_5V_S2 5.0 to 5.63, VBAT load Q28 2.0 to 2.22; B's +5V_S2 peak 5.0 to 5.63
  (B's own comment at gen_sch_b.py:78 derives 5.63 and its call at :79 declares 5.0). The mode figure stays
  INCONCLUSIVE and the note carries the 7.28 A all-peak bound against the 7.10 to 7.17 A loop minimum.
- **B2. The +5V_DEV converter-side inconsistency is computed but not called.** The candidate's 8.9 A bound (B 6.0 +
  D8 2.0 + wall 0.9) is right, and so is A's declared 6.9 A = 6.0 + 0.9 with the D8 mezzanine at ZERO. Nothing in the
  record makes D8 or the wall port non-coincident with B's peak (neither is an outlet the D-11 interlock drops; the
  candidate says so itself). The registry's own model already puts the rail's HIGH case at 7.8 A, inside the loop's
  band (POWER-THERMAL.md lines 709 and 1037), which the candidate did not cite. This is an engineering decision the
  record should have recommended (session authority): declare the coincident peak (7.9 A with D at its 1.0 A
  typical, 8.9 A at every limit) and record the loop's fold-back as the limiter, or write why they cannot coincide.
  Lead side: A's J_5V_DEV 3.2 to 3.8 (B's typical arriving) and A's typical 4.0 to 5.1 (3.8 + D's 1.0 + wall 0.3)
  are the same interim alignment as B1.

## Minor items

- M1. The registry's own PS-ALLTX model (`v2/docs/feasibility/POWER-THERMAL.md`: S1 4.65 A PLAN line 707, +5V_DEV
  5.89 / 7.8 A line 709, findings PWR-F01 to PWR-F03) is not cited anywhere in the candidate (0 mentions); a record on
  this finding should say whether it agrees with the record's existing mode figures (it does on S1 within 0.1 A).
- M2. PWR-F03 (POWER-THERMAL.md line 962): the KSZ9897R's maker figure 1.21 A at 1.2 V is VERIFIED above board B's
  0.5 / 0.8 A declaration, so the +5V_DEV load U26 0.15 A reads about 0.34 A at the maker's figure; the candidate's
  load table calls U26 "typical allocation, unverified" without this.
- M3. The copper model: 1.724e-8 ohm m and 1.31 mm2 are declared as model inputs, correctly; the tree's own constant
  `dc_drop.py:23` (1.72e-8) and the JST catalogue's 1.25 mm2 (p.2) would have been the held figures (5 percent apart).
- M4. The mode is named "PS-ALLTX-3LOADED"; the registry's name is PS-ALLTX (CONOPS section 5, S3 over S2, which
  already has three modules loaded). Use the registry's name.
- M5. Half of ANALYSIS.md is a verbatim copy of the .out (checked identical); the record is doubled for no gain.
- M6. The script pins nothing: it prints the input sha256 and does not compare with the job's expected values; a
  changed input is visible, not refused (shown by the perturbation test).
- M7. Board-B-side inconsistencies the candidate found and I confirm from the intent: the supervisor LDOs U40/U50/U60
  at 0.05 A each against their child rails +3V3_IOCx 0.12 / 0.25 A; the LoRa U21 at 0.6 A against Ebyte's 0.65 A TX;
  the +3V3_DEV comment "1.4 A" against the declared 1.2 A. Board B's owner.
- M8. The contract's `contact_rating: ... datasheet not held (TBD)` and ARCHITECTURE.md:1187 are stale: the JST VH
  catalogue is held (candidate and checker agree); the integrator owns that line.
- M9. My own phase 1 error, for the record: I wrote that the TPS23861 sheet is not held; it is
  (`v2/vendor/ti/tps23861-datasheet.pdf`, SLUSBX9I p.7). The candidate is right.

## Phase 1 figures beside the candidate's

| rail | figure | checker (phase 1) | candidate | note |
|---|---|---|---|---|
| all | A / B declarations | as parsed | identical | |
| +5V_S1 | mode current | 4.575 A (CM5 1.6 allowance, card 9.1 W) | 3.407 A planning mix (CM5 0.9, card 7 W); 6.229 A bound (CM5 2.5, card 9.1 W, child peaks) | registry model 4.65 A PLAN |
| +5V_S1 | limit | AP64500 5 A rating (DS41979 p.1); 6.8 A min peak limit (p.6) | 5 A rating | both cite p.1 |
| +5V_S2 | typical from sources | 4.157 A | 4.157470 A | agree |
| +5V_S2 | coincident | 5.628 A | 5.626523 / 5.627523 A | agree |
| +5V_S2 | worst bound | 6.382 A (CM5 1.6) | 7.281560 A (CM5 2.5, maker's B.3 p.36) | candidate better sourced |
| +5V_S2 | loop minimum | 7.167 A (nominal shunt) | 7.095710 A (+1 percent shunt) | both right; the candidate's is the bound |
| +5V_S2 | margin at the bound | +0.785 A | -0.185850 A | follows from the CM5 input |
| +5V_S3 | mode current | as S1 | card off (K4): 1.847 A mix, 4.201 A bound | candidate right |
| +5V_DEV | lead | A 3.2 vs B 3.8 typical | same | agree |
| +5V_DEV | converter typicals | 5.10 A | 4.6 / 5.3 A | A's parent map vs its child rails; both readings valid |
| +5V_DEV | converter peaks | 8.89 A | 8.9 A | agree |
| +5V_DEV | registry HIGH | 7.8 A over the 7.167 minimum (POWER-THERMAL 709) | not cited | |
| +54V_POE | mode | 0 A (interlock) | 0 A, leakage INCONCLUSIVE | agree |
| +54V_POE | limit | 2.150 A (R71 20 mOhm) | 2.128713 A with tolerance | agree |
| leads | 16 AWG pair, 300 mm | 4.128 mOhm (1.25 mm2, 1.72e-8) | 3.948 mOhm at 20 C, 4.569 at 60 C (1.31 mm2, 1.724e-8) | 5 percent apart, both labelled models |
| leads | four VH contacts at 10 mOhm max, 5.63 A | 225 mV, 4.4 percent of 5.1 V | 0.225 V inside its columns | agree; no lead share in the 2 percent budget (both) |
| verdicts | all five | INCONCLUSIVE | INCONCLUSIVE | agree on the mode figures; the checker supports an interim alignment (B1, B2) |

## What finding I-03 needs next

1. **Integrator (owner of pcb_interfaces.yaml) and board A's generator owner:** the interim alignment of B1 and B2
   as an `apply_` script under a records folder (A: +5V_S2 4.2 / 5.63, J_5V_S2 5.63, Q28 2.22; +5V_DEV J_5V_DEV 3.8,
   typ 5.1; a session decision on the +5V_DEV coincident peak, recorded with `authority: SESSION`), and the
   contract's currents rows and `contact_rating` re-written from the held catalogue. Board B's owner: +5V_S2 peak 5.63
   and the M7 items.
2. **Documents to fetch (the integrator, `v2/vendor/<maker>/` with a `sources.txt` line):** none decides the finding.
   The CM5 publishes no maximum (release 3, Table 9); Diodes plots no VIN 5 V curve for the AP64500 (DS41979 Fig. 4
   and 5 are 12 and 24 V); JST states no AWG 18 figure for the standard header. A JST enquiry text for the AWG 18 /
   B2P-VH rating can be prepared, not sent.
3. **Parts to pick, then declare (board B's owner):** the NVMe drive (the held Cervoz T405 gives a family bound,
   2.6 W active) and the cooler fan (IF-CM5-FAN, TBD).
4. **Bench measurements on the prototype (TEST-PLAN.md, the power tests; FW-A15 in POWER-THERMAL.md):** slot 2's
   rail current at J_5V_S2 with the module loaded and the 5G module transmitting at 24 dBm on a wired attenuator,
   averaged over the LM5176's soft-start time constant and at its peak; the same at J_5V_DEV with the LoRa and
   RockBLOCK bursts and the APRS exciter keyed; the card buck's input current at 5.1 V in and 3.456 V out at 3 A;
   the lead pair's drop end to end (which also reads the four contacts' real resistance against the 10 mOhm bound).
   These are the figures that turn INCONCLUSIVE into a verdict.

## What I ran, and its exact result lines

- `python3 phase1.py > phase1.out`: exit 0 (inputs pinned by sha256 in its first four lines).
- `env -C <worktrees>/cx1 python3 v2/docs/records/cx1/if_ab_power.py > rerun.out`:
  `rerun exit 0`; `cmp` with the filed output: `BYTE-FOR-BYTE IDENTICAL`; sha256 of both
  `e4a0397a63082be4802c20e6b1fce3314110bc3966d9deb8b9805fa3c82e1092`, 27262 bytes; `git status --short` in the
  worktree afterwards: empty.
- Perturbation in scratch (`pert/`, B's U31A 1.6 to 2.0): `changed copy exit 0`, `diff lines: 24`, the B input's
  sha256 line and every raw-sum row changed; the typed-in bound rows did not.
- Draft in scratch: as delivered `Refused: no sourced replacement currents; empty draft writes nothing.` exit 1, no
  marker; absent old text and duplicate old text: `AssertionError: ... old text must occur exactly once in original`;
  new equal to old: `AssertionError: Replacement must change nonempty old text`; broken syntax: `SyntaxError:
  unmatched ')'`, generator copy untouched; a valid entry: exit 0, one line changed, marker created; second run:
  `Refused: this draft has already been applied or attempted.` exit 1.
- Dash scan of the four files (U+2014, U+2013): none. `git show --stat b1c744db`: four files, 1112 insertions.
- Fifteen source rows opened at their pages with `pdftotext -layout` into `txt/`: all confirmed (CHECK.md section 2).

## What I could not check, and why

- Whether the LM5176's average loop would act on the 7.28 A bound: it depends on the burst duty and the soft-start
  capacitor's time constant, which no held document or tree page computes; a bench item.
- The AsiaRF "0721R" designation the candidate attributes to SOURCES.yaml (not looked up; immaterial to the figures).
- The 60 C copper temperature the candidate uses: it is the job's requested point, not a prediction; no thermal
  reading of the leads exists.
- No KiCad, no gate, no suite, nothing on the rented box: none was needed for this check and none was run.

---
Filing note (scrub, 30 September 2026, MESHSAT-1357): 2 paths in this check are written as neutral tokens (`<worktrees>`) under the owner's rule that public files carry no internal host names, user paths or addresses; `v2/docs/records/scrub/MAP.md` lists each by line and token class. No other byte of the check changed; the check as filed is in the repository's history at commit `8fec0733` and before.
