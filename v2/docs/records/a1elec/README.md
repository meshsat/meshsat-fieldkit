# a1elec: Option A(i)'s electrical work package (MESHSAT-1357)

Stream a1elec, branch `fnd/a1elec` from integration set 10's line `13b5352b`, 29 September 2026. The owner's
instruction of that day: engineer Option A(i), 400 Wp into a 200 W solar stage and 4S18P of the ruled Samsung
INR18650-35E as the base pockets' 4S6P plus a lid module of 4S12P; M1 and REQ-072 unchanged; no purchase and no
requirement change authorised. **Prototype design: nothing built, ordered or measured. Every reading here is an AI's
(an AI review), not a qualified review. An analytical result is not physical verification or fabrication readiness;
REQ-072 stays FAIL until the design is drawn, reviewed and tested.**

## What it answers

**The outside review's point 1** (the aggregate model's one store, one temperature, one state of charge, one scaled
ceiling). `energy_two_pack.py` runs two stores with their own usable energy, cell temperature, state of charge, charge
ceiling, taper and lowest point, the lid path's losses and the entry into board A as a cap. It first proves that, with
the departures switched off, it IS the aggregate model (eight cases, largest difference 2.9e-13 Wh), so every
difference it prints comes from a named departure. On the September reference day with 400 Wp into a 200 W stage:
- **Meets M1 with the lid at 13.23 C**, the PVGIS mean day's minimum air (the lid is open in the full mode and outside
  the base's heat), from both starts; **lowest points 30.3 Wh in the base and 0.7 Wh in the lid, 31.1 Wh together**,
  against the aggregate's 91.0 Wh with every cell at +20 C. It meets down to a lid at **+9.6 C** (+7.0 C with 650 Wp,
  +5.5 C with 800 Wp), and with the base also at +15 C with 9.7 Wh left. The lid runs nearly empty at its lowest: its
  colder cells give less, and it is drained in proportion to its capacity.
- **Only with board A's entry re-rated.** As generated (U3's input held under the front end's 5.7 A) it does not meet
  at 13.23 C: it needs the lid at +17.4 C or 650 Wp. With the host contract FW-A16 as written it fails outright (53.9 W
  into the charger with the panel on VIN_RAW).
- Every fault case examined fails M1, as expected of a 72-hour mission on a one-pack remainder (TOPOLOGY.md 6).

**Hand check of the two stores** (energy_budget's chain, section 8c's method): the lid at 13.23 C holds 48 cells x 3.35
Ah x f_rate 1.000 (0.16 A a cell) x f_T 0.8674 (0.4124 + 23.23 / 30 x 0.5876) x V_mean 3.6244 V (clamped at the 0.2C
point) x f_dod 0.937 x 0.80 aged = **378.9 Wh**; the base at +20 C, 24 x 3.35 x 1.000 x 1.000 x 3.6244 x 0.937 x 0.80 =
**218.4 Wh**; both as `energy_two_pack.out` 3c prints them. The aggregate 4S18P at +20 C holds 655.3 Wh; the lid's
temperature alone takes 57.9 Wh of it.

**The outside review's point 2** (the BQ4050's 32,767 limit on the lid's 40,200 mAh and 57,888 cWh). `GAUGE.md`:
IPScale is not used (TI's manual contradicts itself on it); the lid's board PL runs the BQ4050 with a current-scale
calibration of k = 2 made by TI's own calibration procedure, the way TI's engineer answered for this part (E2E thread
854878: "the only way, ie fooling the gauge via calibration"; "all current related parameters will be cut in half") with
TI's application report SLUA760 as the method, and `gauge_scale.py` parses TI's data-flash table to find
all **63** words in a current, charge, energy or power unit, writes each at half its true value and checks its range.
What TI's documents do not settle is drafted as two questions for TI (not sent) and a bench list.

## Files

| file | what it is | kind |
|---|---|---|
| `TOPOLOGY.md` | the two-pack power path at VBAT: the base on U3 as generated; the lid on a second BQ25731 (U3B) from VBAT and an LM74700-Q1 ideal diode in series with an LM5069-2 limited at 8.7 to 11.0 A; what stops one pack charging the other; the join rule; every protection threshold per pack; the host's view (two SMBus segments, U3B behind a TCA9543A); ten fault cases; the drafts per generator; the geometric assumptions for fnd/a1mech | desk design, drafts |
| `GAUGE.md` | the lid gauge: the options, the k = 2 calibration against TI's documents, the exact words, what the host scales, the TI questions, the bench list | desk design, drafts |
| `CHARGER.md` | board A's charger and entry: the three entry cases, the drafted settings and parts (R16, IADPT, 800 kHz, IIN_HOST, L2, R11, U3B), the losses and the thermal load on board A | drafts |
| `energy_two_pack.py`, `.out` | the two-pack model (imports `records/energy/energy_budget.py` unchanged, pinned by sha256) | desk result |
| `gauge_scale.py`, `.out` | the lid gauge's 63 scaled words parsed from SLUUAQ3A Table 14-1 (needs `pdftotext`) | desk result |
| `inputs/pvgis-leiden-daily-profile-2005-2020.json` | PVGIS DRcalc mean-day profile with hourly T2m, byte-identical to the file `fnd/d4energy` filed at `71be4943` (sha256 `4d974567...`, the value `energy_inputs.yaml` names) | input |
| `apply_records_readme_row.py` | DRAFT for the integrator: this folder's row in `v2/docs/records/README.md` (tested on a copy: added once, refused a second run) | apply script, not executed |
| `LOG.md` | the running log | record |

Also filed by this stream, each with its line in `v2/vendor/ti/sources.txt` (URL, date, sha256), fetched on 29 September
2026: `v2/vendor/ti/ti-tca9543a.pdf` (TI SCPS206B), `v2/vendor/ti/ti-slua760-bq34z100-g1-high-capacity.pdf` (TI SLUA760)
and `v2/vendor/ti/ti-e2e-854878-bq4050-current-scaling.html` (TI E2E thread 854878).

## What is shown at desk, what is a draft, what is bench-only

**Shown at desk (on the record's model and the makers' documents):** the equivalence of the two-pack model to the
aggregate; M1 met on the reference day at the lid temperatures stated and the entry re-rated, not met as generated;
the allocation policies and the efficiency and resistance brackets all meet at the basis; the join current bounded at
11.0 A (1.83 A a base cell) by the LM5069's limit and at 2.5 A by the 0.20 V join rule; the 63 scaled gauge words inside
their ranges; the lid's prospective fault (630 A, the source's AC method) inside F1's 1000 A; the losses and the charging
peak's 19.0 W on board A.

**Drafts for a generator owner** (none applied): board A's U3B set, lid path, F_LA, J_LID, TCA9543A and interlock, and the
entry changes (R16 5 mOhm, the IADPT 169 k of O-24, 800 kHz, L2 XAL1010-332ME, R11 6.0 mOhm, VBUS20 re-declared);
board E's lid SMBus segment (J_SMB2, PRES2); the lid's golden image; the firmware contract's rows (FW-A02 lid row, FW-A16
revised, FW-E01's twin, the join rule); `pcb_pack_protection.yaml` and `pcb_energy_chain.yaml` lid sections (the
integrator's files: only described, no apply script written for them).

**Bench-only:** the k = 2 calibration's CC Gain read-back and the gauge's thresholds at their true currents; the CEDV
fit on the lid's own logs; U3 and U3B efficiencies at these points; the 800 kHz compensation; the allocation loop's
reaction; the LM5069's timer at the kit's peak; the ideal diode's reverse response on a harness short; the lid's cell
temperatures in the open lid; board A's temperatures at 19 W.

## Decisions taken (authority SESSION, 29 September 2026; each reversible as stated in its page)

1. A second BQ25731 (U3B) for the lid instead of sharing U3 (TOPOLOGY 3b). 2. The lid discharges through an ideal diode
in series with a current-limited switch, limit set by the base cells' charge rating, default on (3c). 3. The join rule,
0.20 V (3c). 4. The lid gauge on its own SMBus segment (5). 5. U3B behind a TCA9543A at 0x70 (5). 6. The lid gauge a
BQ4050 at a k = 2 calibration, IPScale unused (GAUGE 2). 7. Re-rate board A's entry rather than grow the array to 650 Wp
(CHARGER 1). 8. The lid's temperature basis: the September mean day's minimum air, 13.23 C (energy_two_pack.out 2).
9. Charge allocation in proportion to capacity; U3 ChargeCurrent 3.968 A, U3B 7.936 A.

## Open items, each with its next action

- **Board A's space and layout** for the new circuit (about 40 x 45 mm, ESTIMATE): board A's owner places it or moves it
  to a daughter board on VBAT (TOPOLOGY 9).
- **Board E's 200 W stage and REQ-016's 25 V**: board E's owner and the owner's ruling (CHARGER 2; energy record 9i).
- **A heater for the lid pack** and its supply: the mechanical stream and board A (TOPOLOGY 9).
- **TI's answers Q-TI-A1 and Q-TI-A2**: the owner sends them or authorises sending (GAUGE 6).
- **The qualified battery review (D-09)** of the whole two-pack design, including the double faults of TOPOLOGY 6.
- **The front end at 9.5 A**: the generator owner checks the LM5176 stage against its held datasheet (CHARGER 2).
- **POWER-THERMAL** re-run with board A at 19 W at the charging peak (CHARGER 3).
- **A three-GPIO check on board E's U10** for the lid SMBus segment, or the fallback address (TOPOLOGY 5).
- **Chronological weather**: every result is the mean day; a colder or duller spell than the mean is not examined here.
- **The lid's cold capacity**: the model's temperature factor is a lower bound at the lid's 0.16 A a cell (one cold
  point of the cell sheet at 3.4 A); a low-rate cold discharge curve of the 35E, from the maker or the bench, would
  replace it.
- **Transport**: the lid module is a second battery of 578.9 Wh nominal; its classification is REQ-069's and is not
  examined here (the energy record withdrew its own transport sentence).

## Reproducing

From the repository root, Python 3.11 with PyYAML, and `pdftotext` (poppler-utils) for the gauge table:

```
python3 v2/docs/records/a1elec/energy_two_pack.py > v2/docs/records/a1elec/energy_two_pack.out
python3 v2/docs/records/a1elec/gauge_scale.py     > v2/docs/records/a1elec/gauge_scale.out
git diff --exit-code v2/docs/records/a1elec/       # both outputs byte-identical to the committed ones
```

`energy_two_pack.py` refuses (exit 2 or 3) if `energy_inputs.yaml`, `energy_budget.py`, a file of the energy inputs'
pinned list or the daily profile changed, and exit 4 if the equivalence fails; `gauge_scale.py` refuses (exit 3) if the
TRM changed, exit 5 if a scaled word has no stated true value and exit 6 if a written value leaves its range. Both
outputs carry no date, host or absolute path; two runs were byte-identical.
