accepted: yes

# Layer 4, L4-E4, B2: Claude's verification of the outlet bench's hold windows (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 1 October 2026. Scope: the one blocker the engineering collaborator's targeted recheck left open
(`astra-check-l4e4-2.md`, run 20261001T033707Z-1842303 on `b9d01448`, which accepted B1 and the three minors of the first
check `astra-check-l4e4-1.md`): the bench's 15 V hold window reached 16.3 V, past the fast overvoltage minimum, so a gate
edge inside the accepted window could come from the overvoltage path rather than the current comparator. The fix is commit
`1352560c`; Astra did not examine it (its two runs on this issue are spent).

- **The maker's rows, read by the coordinator** from `v2/vendor/ti/ti-tps25740.pdf` (SLVSDG8B, p.8, section 7.5, the
  TPS25740A rows; U18 is the TPS25740ARGER in `gen_sch_a.py`): V(FOVP) minimum 5.8 / 10.1 / 16.2 V and V(SOVP) minimum
  5.5 / 10.0 / 16.3 V for the 5 / 9 / 15 V contracts; V(SUVP) maximum 3.8 / 7.1 / 12.2 V. Page 31 states that a fast OVP
  disables GDNG.
- **The windows at `1352560c`:** upper bound min(V(FOVP) min, V(SOVP) min), lower bound max(V(SUVP) max, V(VBUS_FTH) max
  3.9 V), VBUS strictly inside: 3.9 < VBUS < 5.5 V, 7.1 < VBUS < 10.0 V, 12.2 < VBUS < 16.2 V. These are the rows' values;
  only the 15 V upper bound moved (16.3 to 16.2 V, the fast OVP minimum being the smaller there).
- **The test:** `t_outlet_bench_isolates_u18` derives each bound from the rows, refuses 16.25 V and the old 16.3 V at 15 V,
  accepts 16.15 V and refuses each boundary value; `test_l4e4` run by the coordinator: 12 passed, 0 failed, 0 skipped.
- **Reproduction:** `l4e4_limits.py` re-run by the coordinator: its output equal to the committed `l4e4_limits.out`;
  `r11_dep.out` reproduced byte for byte (its section 0a).

Result: B2 closed. What stays open is what the page states: C-7 (U3's input-current minimum rests on the INFERRED 0.1 A),
which VI(TRIP) row board A's strapping selects (the bench decides, by the measured differential threshold in a valid
run), R11's real temperature, the J_USBC_OUT contact rating and C-8. The values are drafts for board A's generator owner:
nothing is implemented, built or measured.
