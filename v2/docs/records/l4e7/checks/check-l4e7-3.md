accepted: yes

# Layer 4, L4-E7: Claude's verification of B1's fix and the recheck's residue (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 1 October 2026. The engineering collaborator's check of L4-E7 (`astra-check-l4e7-1.md`, run
20261001T140747Z-3274169 on `2d7e331e`) read NOT YET on B1: the 94.2k over 7.5k hold and its 16.3 V declaration changed
REQ-016's approved operating point. The coordinator agreed and directed the requirement-preserving hold; the fix is
`379ea32f`. The targeted recheck (`astra-check-l4e7-2.md`, run 20261001T144407Z-3391302 on `379ea32f`) read ACCEPT with one
nonblocking residue of M2; its fix is `6f9021c5`.

- **B1, read at the source.** REQ-016's statement says "the panel held at 17.6 V by the stage's input regulation"; owner
  ruling D-34 keeps REQ-016's approved window unchanged unless the owner rules otherwise. The hold draft
  (`apply_gen_sch_e_hold.py`) makes one edit: R8 and R9 keep 102k and 7.50k and become YAGEO RT0603BRD07102KL (C861068) and
  RT0603BRD077K5L (C728597), 0.1 % and 25 ppm/K; the panel entry keeps its declared 17.6 V. The 16.340 V hold is a proposal
  that would change REQ-016 and needs the owner's ruling (+25.0 Wh a day nominal on the design day); no draft carries it and
  `test_l4e7` holds that nothing depends on it.
- **B1's band, recomputed by the coordinator in separate code.** From 8705af p.4 (FBIN, E and I grades, 1.184 / 1.205 /
  1.226 V; the reference's line regulation at most 0.005 %/V; the FBIN bias 10 nA typical, out of the pin; EA3's gain 90 V/V
  typical), p.2 (VC from -0.3 to 2.2 V, so 1.5 V the largest excursion from the 1.2 V the rows are printed at), the YAGEO
  RT sheet's 0.1 % and 25 ppm/K, and the envelope's ends (-20 C and 62.1 C), on the replay's hold model (the line term at
  the 12 V reference iterated to its fixed point, EA3's allowance the excursion over its gain): **16.970441 / 17.593000 /
  18.220502 V**, equal to the script's and the recheck's figures.
- **M2's residue.** The script prints the EA2 break-evens to six decimals and the page states each with its stack: stack A
  25.026426 V/V cold and 24.924212 V/V hot; stack C's other terms (line x2, the drifts) 55.191656 and 54.709122 V/V; the
  bench acceptance stays at or above 65 V/V. The fix changed only those lines of the output.
- **Run by the coordinator at `6f9021c5`:** `l4e7_stage_settings.py` re-run, its output equal to the committed
  `l4e7_stage_settings.out` byte for byte (it reproduces `l4e_replay.out` and `l4e5_source_control.out` in child processes
  first); `test_l4e7` with `test_public_hygiene` 16 passed, 0 failed, 0 skipped.

Result: L4-E7 accepted as an engineering decision: U5 the LT8705AI; RSENSE1 15 mOhm (new R59) on the new net TRK_VIN;
RIMON_IN 23.2k, 3.4713 A, the 100 W corner at 96.2474 W cold and 96.2291 W hot under the printed limits; CIMON_IN 100 nF;
the hold kept at REQ-016's 17.6 V point with precision parts. Drafts only, refused against the repository's generator until
a `RELEASE.md` names an accepted check. Open and not closed here: EA2's gain, the line regulation while switching and at
temperature, RSENSE1's TCR below 25 C, EA3's gain and the FBIN bias (energy only), U5's junction (bench rows 7b.9 to
7b.13); R59's Kelvin taps and placement, the regeneration and its gates; the owner's ruling only if the 16.340 V proposal
is ever to be adopted.
