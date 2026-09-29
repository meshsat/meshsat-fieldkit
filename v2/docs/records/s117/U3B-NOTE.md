# U3B: a drafted note for Option A(i)'s electrical record (stream s117, second issue, MESHSAT-1357)

29 September 2026. **DRAFT ONLY, for the writer of `v2/docs/records/a1elec/` (TOPOLOGY.md 3b, CHARGER.md 2) and the
energy record's writer: nothing in `records/a1elec`, `records/a1int` or `records/energy` is edited by this stream.** AI
engineering work, desk arithmetic on the makers' documents; nothing is built or measured. Every figure is
`efficiency.out` (sections 4, 5 and 7) beside this file, SLUSE66A Equations 6 to 22 (printed pages 86 to 88) with R16B
and R17B counted and the inductor's core loss excluded.

## What the draft carries and what it gives

U3B as drafted: a second BQ25731 from VBAT (the model's 14.5 V node) into the lid pack, R16B and R17B 5 mOhm
(RSNS_RAC = 1b), IIN_HOST 8.0 A, L2B XAL1010-332ME with 169 k on IADPT (the 3.3 uH row, 800 kHz), and Q7B to Q10B
CSD18510Q5B. Between two 4S packs the lid sits below VBAT (buck), above it (boost) or beside it (buck-boost, all four FETs
switching; the maker gives no threshold, 9.3.10 p.27).

| | buck, lid 13.0 V | boost, lid 15.5 V | buck-boost (a bound) | REGN, buck / buck-boost, typical (maxima) |
|---|---|---|---|---|
| drafted (CSD18510Q5B x 4, 800 kHz) | 0.896 (0.866 to 0.930) | 0.891 (0.856 to 0.929) | 0.802 (0.734 to 0.869) | 120 / 240 mA (177 / 354) |
| (a) CSD17578Q5A x 4, the drafted 800 kHz row | 0.975 (0.966 to 0.980) | 0.976 (0.968 to 0.982) | 0.961 (0.947 to 0.971) | 16.5 / 33.0 mA (25.0 / 49.9) |
| (b) the 400 kHz row, Q7B and Q9B CSD17578Q5A, Q8B and Q10B CSD17577Q5A | 0.981 (0.976 to 0.985) | 0.982 (0.977 to 0.985) | 0.974 (0.966 to 0.980) | 10.5 / 21.0 mA (16.3 / 32.6) |

TI's reading first, the makers' maxima and the most favourable reading in brackets, at the model's peak hour (55.3 W from
VBAT, lid charge 3.69 A). REGN: VREGN_REG is specified for 0 to 60 mA and IREGN_LIM is 50 mA minimum (8.5, p.11).

1. **The drafted FETs cannot be driven.** REGN would be asked 120 mA in buck mode at 800 kHz and 240 mA in buck-boost,
   against a 50 mA minimum limit; S-117's finding F1 (S-118 on the tree checked) names U3B for this.
2. **The 0.975 of `energy_two_pack.py` (`eta_u3b`) is not supported with the drafted FETs**: 0.80 to 0.90 by TI's method
   at the peak hour, depending on the mode. F2 (S-119 on the tree checked) carries it for the energy record's writer.
3. **Two ways to carry U3B, both with the parts U3 takes under decision 57:**
   - (a) keeps the drafted row (3.3 uH, 169 k, the 800 kHz compensation, 5 mOhm sense, 8.0 A input; Table 9-1, printed
     page 26, gives 10 A for the 3.3 uH row at RSNS_RAC = 1b) with CSD17578Q5A in all four positions. REGN sits at 49.9
     mA against 50 mA at the maxima in buck-boost at 920 kHz: no margin.
   - (b) takes U3's row (4.7 uH XAL1010-472ME, 191 k on IADPT, Table 9-5's 400 kHz compensation, PWM_FREQ at its power-on
     400 kHz) with a 10 mOhm input sense (RSNS_RAC = 0b), so IIN_HOST clamps at 6.35 A (9.3.5, p.25; Table 9-1 has no 4.7
     uH row at 5 mOhm, so an 8 A setting would sit outside the maker's table), with the fast part where each leg
     hard-switches (Q7B in buck, Q9B in boost) and the low-resistance part on the synchronous side. REGN keeps a margin of
     17 mA or more in every mode, and the losses are lower. The model's busiest U3B hour draws 55.3 W, 3.8 A from VBAT,
     well under 6.35 A; whether any case of the reconciliation needs more than 6.35 A into U3B is the writer's to check.
   Either way one land (XAL1010) and one FET pair serve U3 and U3B.
4. **Carry into the energy model** (the worst mode at the peak hour, TI's reading, until the lid's mode per hour is
   modelled): drafted 0.802; (a) 0.961; (b) 0.974. Buck mode alone: 0.896, 0.975, 0.981.
5. **A correction to CHARGER.md's item M8**: it says no Coilcraft XAL6030 or XAL6060 sheet is held;
   `v2/vendor/coilcraft/coilcraft-xal60xx-series.pdf` (Documents 887-1 to 887-4) holds both.

The FETs' datasheets are held back by their makers' terms and pinned by sha256 in `v2/vendor/sources.txt`
(`fetch_held_back.py` beside this note fetches them).
