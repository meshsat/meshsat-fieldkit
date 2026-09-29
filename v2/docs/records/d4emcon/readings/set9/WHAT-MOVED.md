# What moved between set 6 and set 9 on the EMCON paths (stream d4emcon, 29 September 2026)

Read on the committed netlists of main `c5f93464` (merged into `fnd/d4emcon` as `fe501d26`) against those of
`73ae2f21` (the set 6 line this stream's first readings were taken on). Tools: `tools/netdiff.py`,
`tools/path_walk.py`, `tools/walk_report.py`, `tools/fault_levels.py`; nothing here needed KiCad.

| Board | set 6 sha256/16 | set 9 sha256/16 | What changed (`netdiff-*.txt`) | Effect on an EMCON path |
|---|---|---|---|---|
| A | `0a2b59087bcc2678` | `599ee964a9c23d6e` | S-99's D8 split (decision 55): U41 (TPS62933, 5.0 V) with L13, R217, R218, C227 to C232 makes `+5V_D8IN` from VBAT, enabled by `RAIL_EN` (U41 pin 2); the eFuse U23 now feeds `+5V_D8` from `+5V_D8IN` instead of `+5V_DEV`. U23, U32 and U39's value text and R186 and R209's value text carry corrected current-limit labels (resistor values unchanged: R209 is still 4.7 k 1 percent) | none on a path. No net of any of the 27 declared paths changed: `TX_INHIBIT_n`, `EMCON_HW`, `PA_EN`/`PA_UVLO`, `HF_EN`/`HF_UVLO`, `+3V3_EMCON`, U35 to U40, R102, R145 are byte-identical in nodes. `RAIL_EN` is the kit's main on/off (U1, LTC2954) and enables board A's +3V3 buck U12, the EMCON gates' eFuse U39 and now U41 together, so `+5V_D8` (board D's supply) now falls with board A's +3V3 and `+3V3_EMCON` when the kit is switched off; that is the unpowered state, in which every inhibit is asserted by its pull-downs (RF-002's named state). |
| B | `028997a6c5e8810f` | `21a1f74a3ec1ae28` | the `source` and `date` header lines only (S-98's regeneration); no part, value or net differs | none |
| C | `3fddbb3edcd4248a` | `3fddbb3edcd4248a` | unchanged | none |
| D | `7a2c0ac2190b141a` | `7a2c0ac2190b141a` | unchanged | none on D's netlist; its `+5V_D8` input now comes from U41 on board A (above) |
| E | `56adc9746d61c4e0` | `56adc9746d61c4e0` | unchanged | none (board E carries no transmitter and no EMCON line: `path_walk.py` finds no hop on E) |
| P | `760ac6f74d62d194` | `760ac6f74d62d194` | unchanged | none |

Result of the re-run: `set9/paths-set9.txt` (27 declared paths, every hop holds), `set9/walk/walk-full.txt` (RF-002's
walk: A FAIL 0 PASS 3 UNDECIDED 2; B FAIL 0 PASS 9 UNDECIDED 8; C FAIL 0 PASS 3; D FAIL 0 PASS 3 UNDECIDED 1; E and P
PASS 1) and `set9/fault/fault-levels-set9.txt` are byte-identical to the set 6 readings under `readings/` apart from the
two netlist hashes in their headers. So every statement this stream's set 6 readings support stands on set 9.

The one consequence of the D8 split for EMCON's open items: board D's L4 residual (EMCON.md section 3, a fall of
`+3V3_D8` through the 0 to 1.65 V band faster than `+5V_TX` decays, bench E-11) is unchanged in kind, because board D's
netlist is unchanged; the source that sets how fast `+5V_D8` itself falls at switch-off is now U41 rather than the
`+5V_DEV` stage. Nothing on a path depends on it: with `+5V_D8` falling, U21 (TPS22810) on board D removes `+5V_TX`
by the same EN/UVLO divider on `+3V3_D8` as before.
