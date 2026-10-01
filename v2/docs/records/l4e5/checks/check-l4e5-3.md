accepted: yes

# Layer 4, L4-E5: Claude's verification of the recheck's two items (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 1 October 2026. Scope: the two acceptance statements the engineering collaborator's targeted recheck left open
(`astra-check-l4e5-2.md`, run 20261001T115956Z-2934193 on `03a52063`, which accepted the revised arithmetic, the fallback
coverage, the H3-specific 49.7 W conclusion and both minors of the first check `astra-check-l4e5-1.md`). The fix is commits
`037ea1c9`, `d57729bc` and `b2c54ca8`; Astra did not examine them (its two runs on this issue are spent).

- **B1, HIZ release is not guaranteed conversion.** Read by the coordinator in `v2/vendor/ti/bq25731-datasheet.pdf`
  (SLUSE66A): p.27, "In order to exit HIZ mode, ILIM_HIZ pin voltage has to be higher than 0.8 V and EN_HIZ bit has to be
  set to 0b"; p.17, VHIZ_LO 0.8 V rising and VHIZ_HIGH 0.4 V falling; p.10, the input-current regulation range by the pin
  (VIREG_DPM_RNG_ILIM) 1.15 to 4 V; p.64, EN_HIZ is REG0x35 bit 7, reset 0b. At `b2c54ca8` the page, FW-A18, V-A09 and the
  output say "out of HIZ above 8.713 V while EN_HIZ = 0b", assert regulation by the pin only from the 1.15 V point (VIN_RAW
  8.810 V nominal, 8.766 to 8.854 V; the coordinator recomputed it from the output's printed knee, about 2.48 V/V between
  8.669 and 8.700 V), and have V-A09 record switching and input current between HIZ release and that point without
  asserting conversion. The only remaining "converting" is the recheck table's quotation of the old wording.
- **B2, V-A10's boot case.** At `b2c54ca8` the case is split: (2i) normal initialization from POR permitted and verified,
  the raw IIN_HOST, ChargeOption1, ChargeOption2 and InputVoltage logged from POR, every write at or under 4.70 A; (2ii)
  after initialization no change caused by missing telemetry, FW-A16 (b)'s rewrite after an adapter removal excepted, every
  write at or under 4.70 A. It no longer contradicts the POR value or FW-A16's startup writes.
- **Reproduction and tests, run by the coordinator:** `l4e5_source_control.py` re-run, its output equal to the committed
  `l4e5_source_control.out`, `l4e4_limits.out` and `r11_dep.out` reproduced byte for byte in its section 0; `test_l4e5`
  17 passed, 0 failed, 0 skipped, `t_hiz_release_is_not_asserted_as_conversion` and `t_v_a10_boot_permits_initialization`
  among them.

Result: B1 and B2 closed; L4-E5 accepted as the source-control decision H3 (a hardware VIN_RAW line on U3's ILIM_HIZ pin with
a knee below 9 V, board E's tracker ceiling raised, firmware IIN_HOST constant at 4.70 A). It supports L4-E4's 4.70 A
setting for every register value; the pin path's possible 5.095 A through R11 between 26.50 and 27.24 V on a stiff source
stays open for bench V-A07 or R11 at 7 mOhm, which passes to the fault-handling task L4-E6. The circuit is undrawn: these
are decisions and drafts for the generator and firmware owners, nothing implemented, built or measured. What stays
INCONCLUSIVE is listed on the page.
