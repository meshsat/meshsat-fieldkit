### 22c. V2's three corrections on one basis

**Need 1:** the bleed with the sources at their hot bound ends inside the hold's least value. **Need 2:** U47's RESET sink stays
within TI's recommended 5 mA (SNVSBJ1E 7.3, p.6; the absolute maximum is 10 mA, 7.1, p.6) in every state where it sinks, R256 at -1 %.

| | (a) text only: 6.8 kOhm, the hold as drawn | **(b) R256 back to 4.7 kOhm, the hold as drawn** | (c) 6.8 kOhm, the hold lengthened (C241 2.2 uF) |
|---|---|---|---|
| the hold, least to most | 1.341 to 5.82 s | 1.341 to 5.82 s | 2.585 to 12.8 s |
| the static limit (the latch reads dead) | 0.597 mA | **0.846 mA** | 0.597 mA |
| the bleed with no source (towards 0 V) | 1.228 s | 0.859 s | 1.228 s |
| the bleed at the air's 116.6 uA | 1.381 s | 0.934 s | 1.381 s |
| the bleed at the hot bound's 434.8 uA (with the loads credited) | 2.189 s (2.063 s) | **1.218 s** (1.181 s) | 2.189 s (2.063 s) |
| the same with the battery FETs at 150 C (INFERRED) | 2.312 s | 1.248 s | 2.312 s |
| the coupled limit: the sources under which the bleed ends inside the hold's least | 87.4 uA | **520.7 uA** | 498 uA |
| what that leaves the breaker pair | 40.6 uA | **473.9 uA** | 451.2 uA |
| on the ASSUMED doubling, the pair's case (held: 101.0 C) or the slowest doubling at the held case | 68.4 C; every 17.49 K | 103.9 C; every 9.63 K | 103.2 C; every 9.72 K |
| **need 1** | **FAILS** at the hot bound and at the air | holds, 0.123 s inside the hold, on the ASSUMED leakage | holds, 0.396 s inside the hold, on the ASSUMED leakage |
| RESET at the instant of setting (CELL+ at VSYS's 17.375 V) | 2.7 mA | 3.85 mA | 2.7 mA |
| RESET with the breaker restarted while the hold runs (the pack's 16.8 V) | 2.61 mA | 3.72 mA | 2.61 mA |
| RESET with CELL+ following VBAT at the charger's SYSOVP, 19.5 V | 3.02 mA | 4.32 mA | 3.02 mA |
| RESET with CELL+ at VBAT's 29.2 V clamp | 4.51 mA | 6.45 mA | 4.51 mA |
| CELL+ at which RESET reaches 5 mA | 32.45 V | 22.51 V | 32.45 V |
| **need 2** | holds in every state | holds in every state without a second fault (22d) | holds in every state |

**What (c) moves for the hold's readers** (20d, 20g, E-14 (c), E11-45 (h)): the hold's most 12.8 s, from 5.82 s (the battery FETs held
off that long after every set, a false set at a docking included); the arm completes 0.9116 of the way before the set, from 0.99519,
so the hold starts from 10.209 V; R84's pulse 1.186 mJ and D26's I2t 2.08e-05 A2s, from 0.539 mJ and 9.44e-06 A2s; a 2.2 uF 100 V
part whose DC bias is not read. With R85 at 2.4 MOhm instead, the hold's least is only 2.08 s (D26's leakage and C241's insulation
take more of it) and need 1 fails. **(c)'s reach:** with C241 at 3.3 uF the hold is 3.35 to 19.2 s and the coupled limit 557.6 uA (the
pair 510.8 uA, a case of 105 C on the ASSUMED doubling): wider than (b)'s by 36.9 uA, and never past its static 0.597 mA, where (b)'s
static room is 0.846 mA.

