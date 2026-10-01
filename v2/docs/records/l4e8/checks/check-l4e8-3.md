accepted: yes

# Layer 4, L4-E8: Claude's verification of the conservative bound and the cold-envelope loop (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 1 October 2026. The collaborator's check (`astra-check-l4e8-1.md`, on `5ff06474`) and its targeted recheck
(`astra-check-l4e8-2.md`, on `cc95fe1f`) did not accept the bank. The second failure on the same issue changed the method:
the sampled search was replaced by a conservative analytic bound over fully independent components. The fix is `a282c8b7`,
and this check verifies it. Both collaborator runs on the issue are spent.

- **The bound's construction, read in `ripple_dense.py`.**
  - Each branch's impedance over a frequency bin is a rectangle (`branch_rect`). The real part is the ballast plus the ESR
    interval. The reactance runs from its minimum at the bin's lower edge, the smallest L and the smallest C, to its maximum
    at the upper edge, the largest L and the largest C, because it rises in each.
  - The image of a convex polygon under 1/z (`inv_hull`) is bounded by arcs of circles through the origin, of radius 1/(2d).
    The arcs are sampled so every chord's sagitta is at most the tolerance, and the samples' hull is grown by that sagitta,
    which encloses the image.
  - Independent branches add as exact Minkowski sums of convex polygons (`mink`). A target can's share of the current is
    bounded below in its denominator by branch and bound over its own rectangle (`kmin_bb`, `tmax_bb`).
  - Taking each harmonic's worst parts separately can only overstate. The L11 and L16 / C190 cells keep one physical part
    consistent across harmonics, and each cell still takes its own worst.
  - Coincident harmonics add as magnitudes. The tail above the 120th harmonic is bounded.
- **The primitives, tested by the coordinator with its own random cases** (seed 777, not the script's or the tests'):
  - `mink` against the brute-force hull of pairwise sums: 300 random convex pairs, no true sum vertex outside the computed
    sum.
  - `inv_hull` on 300 random branch-shaped rectangles: none of 60,000 random image points outside the enclosure.
- **Run by the coordinator at `a282c8b7`:** `ripple_dense.py` re-run, its output equal to the committed
  `ripple_dense.out` byte for byte. `test_l4e8` with `test_public_hygiene`: 23 passed, 0 failed, 0 skipped. That includes
  the tests' own brute-force samples against the bound, with seeds of their own.
- **The result, read from the output.** The six drawn EEHZK1V331P cans each sit behind a 45 mOhm ballast (C2903491). The
  bound's worst can is 2.4096 A at R11 8 mOhm (7.262 A), against the rule's 2.7745 A, a margin of 0.365 A. At R11 7 mOhm
  (8.300 A) it is 2.7661 A against 2.7709 A. Below 38 mOhm a feasible configuration exceeds the limit, so the ballast is
  necessary. Cc2 goes from 680 pF to 3.3 nF (C1613): across the cold ESR envelope, 0 to 300 mOhm per can, the worst PM is
  61.4 degrees and the worst GM 15.8 dB (14.4 dB on the widened band). The drawn 680 pF reads GM 5.0 dB there. The ballast and
  Cc2 go in only with L4-E6's R12 12 mOhm (PM 46.3 degrees on the drawn R12).

Result: accepted. **B-4 closes at R11 8 mOhm on a conservative bound.** The 7 mOhm fallback (needed only if bench V-A07
fails) stays **CONDITIONAL**: its 0.005 A margin is thinner than any allowance for the operating points, VIN on 26 points
and VBAT in 0.05 V steps, which are sampled rather than bounded. At 8 mOhm the 0.365 A margin covers that sampling.

Carried as conditions and downstream obligations:
- the lifetime, CONDITIONAL on the can's measured temperature rise (bench 7b.8 item 4);
- the cold ESR envelope, the sheet's -40 C limit applied down to -20 C (INFERRED), confirmed by the bank's ESR envelope at
  -20 C over service life;
- C190 and C191's regions (ASSUMPTION, no maker data held);
- the restart ring of 16.13 A over endurance, to L4-E6's saturation-aware C-5 sweep;
- the symmetric-placement rule replaced by the bound (it no longer needs matching);
- the ballast's surface temperature at the bench.

Energy term for REQ-072's owner: an upper sum of 2.09 W at the worst corner (0.0093 W in the nominal-parts illustration),
not to be double-counted with measured efficiency.
