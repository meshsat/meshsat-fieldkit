### 22b. The sources into CELL+ with the breaker off and the inhibit held (each labelled)

| Source | Figure | Label and document |
|---|---|---|
| the LM5069's internal 1 MOhm, SENSE to OUT | 16.8 uA at BRK_VIN 16.8 V (29.2 uA at the 29.2 V clamp) | MAKER value (TI SNVS452G 7.5 note 1, as record l8p reads it); its tolerance is not printed |
| the three battery FETs Q39, Q40, Q42 | 3 uA at 25 C, **30 uA at Tj 125 C** (1 and 10 uA each, VDS -30 V) | MAKER, printed maxima: Nexperia BUK6Y10-30P (17 April 2020) Table 7 p.6. Over 125 C nothing is printed; on the sheet's own two rows' slope E-1's 150 C would read 53.3 uA for the three (INFERRED, information only) |
| the breaker pair Q101, Q102 (CSD18510Q5B) | 2 uA at 25 C; **69.8 uA at the 76.25 C air, 388.0 uA at the held 101.0 C case** | 25 C: MAKER (TI SLPS632, March 2017, p.3: IDSS 1 uA at VGS 0 V, VDS 32 V, TA 25 C, its only row). Hot: **ASSUMPTION**, record l8p's L8P-F06 (OPEN; `fnd/l8p2` at `69156072`, 12j, copied to `inputs/l8p-section12j-f06-69156072.md`): a doubling every 10 K |

**The hot bound on C-PROT rev 1** (the pack at 16.8 V, the battery FETs on their printed 125 C row, the breaker pair at its held
case): 16.8 + 30 + 388.0 = **434.8 uA** (116.6 uA at the air; 447.2 uA with BRK_VIN at the clamp; 458.2 uA with the battery FETs at
150 C, INFERRED).

