accepted: yes
tip: 63897fc31c4bb80426c4434d9b4e883c31aa74ed

# CHECK-3 of fnd/l3batt: the lid tablet's USB-C service budget (stream l3batt, MESHSAT-1357)

**An AI check, not a qualified review, and not the author.** 30 September 2026, 15:21 CEST.
- **The branch** is `fnd/l3batt`, tip `63897fc3` (confirmed), one commit on CHECK-2's `83577a13`: 7 files, 858
  insertions, 4 deletions.
- **The clone.** A `--no-local --single-branch` clone (`_scratch/chk-l3batt3`, removed after the check), with
  `int18-evidence-1f34bf92.tar` extracted and the l3batt worktree's ignored vendor files copied in. `git status` stayed
  clean throughout.
- **Method.** Every energy figure was recomputed on the checker's own two-pack balance (`../chk-energy/indep_balance.py`
  with an hourly added load at VBAT, driven by `indep_tablet.py` and `indep_tablet2.py` in this folder; no record script
  imported). The straps, the shunt and the idle draw were read from board A's netlist and the makers' pages directly.

## Files verified at the tip (working tree equal to the blob)

```
c1c7c4156935bfa85bbd98f5f345be9b8a893618abebe5648cddccc42ad4d23a  .gitignore
e84f3a45f57355cf1695c6ad8d286c8ae307e8509e6c007743ab2b9171874d8c  v2/docs/records/l3batt/COMPARISON.md
9b0cbdf3d3932250ac215f41ca1f67523889421cf76384a38cac3de335b7fc8d  v2/docs/records/l3batt/TABLET-BUDGET.md
f45c2489418b767dcd85123b074d02b2725079657a62c6b6d0ddd2d1834360f2  v2/docs/records/l3batt/fetch_held_back.py
d71429a9bd6d60a51662f1a4826db398c629cb3675b8c6668e3aba1fb60a8194  v2/docs/records/l3batt/tablet.out
ea4b95416122d9ecd368e40337c35a7f902ad131f3fdd829eaee5a2ceab3690d  v2/docs/records/l3batt/tablet.py
0d5ef5559fc72d27addeebc60d88a8e66a5f66c13a2f555a196571d8cec470f3  v2/vendor/sources.txt
```

Read beside them (unchanged by the commit):

```
6c40250c47195ebb7b2ae1388e284dc7f2fba9f2e683f654a47c98444290e8c5  v2/ecad/pcb-a-power-a23/out/pcb-a-power.net
60276c7a0e2a138ae3fcd68be7bd6f0c2e01e78ea60fb33ad0fb1b6874d89cd8  v2/vendor/ti/ti-tps25740.pdf
98191bec36d43771affa3e1540f6e1737347c19a1602747ffb4327509550a820  v2/vendor/ti/lm5176-datasheet.pdf
cb747de812f6685995917335ec78c663fbf1cee0942db9a3e5b1c375147a601a  v2/vendor/battery/ti-csd18510q5b.pdf
87d9c1ee590597638c57aa97c384c217af9eb36044a2db39e27194a88047fc13  v2/docs/records/l3batt/runtime.out
e35e62483b67fbe71bf89b819f6be46173ce708a8a62c683905d55a37ad4c218  v2/docs/records/l3batt/load_trace.out
9da1e3e99762403f7ae341d3be91c4d9e0286fa90f6f7e3d86c4913c758a19fd  v2/docs/records/l3batt/lid_21700.out
f5a40178566ca410f5a91423730697deeb598edc949ed50f9df5ae054b800fa5  v2/vendor/tablet/held/samsung-galaxy-tab-active5-spec-sheet.pdf (ignored)
59f0c2807fb5b24d43d418e45f684c0394123cf0cda921a61f030a78c5056d73  v2/vendor/tablet/held/zebra-et40-et45-spec-sheet-en-us.pdf (ignored)
```

## Blocking items

None. Every figure of the page reproduces on the checker's own balance within 0.2 Wh, the double counting is
excluded, the budget is labelled a PROPOSAL, and no row takes the 45 W or drops the charging.

## Minors

1. **New finding, board A as drawn: the outlet's OCP shunt R138 is 10 mOhm, twice TI's recommended 5 mOhm, so the
   trip sits at 1.92 to 2.26 A.** The strap change alone does not give an outlet that delivers 18 W on every PDO.
   - **Netlist.** R138 "10mOhm 1% 2512 (ISNS)" runs from PD_SW (U18 pin 19 ISNS, pin 23 GDNS, Q27's source) to PD_VBUS
     (U18 pin 21 VBUS, J_USBC_OUT pin 1). The trip is sensed as V(ISNS) minus V(VBUS) across it.
   - **The maker.** In SLVSDG8B 8.3.8.2 (p.31): "Following the recommended implementation of a 5 mOhm sense resistor,
     when the device is configured to deliver 3 A (via HIPWR pin), the OCP threshold lies between 3.8 A and 4.5 A". VI(TRIP)
     is 19.2 to 22.6 mV in the electrical table. At 10 mOhm that is **1.92 to 2.26 A**.
   - **The proposed 18 W setting** (Table 5 p.29: PSEL direct to GND, PCTRL low, HIPWR high) advertises 5 V 3.0 A,
     9 V 2.0 A and 15 V 1.2 A.
     - The 5 V 3.0 A PDO (also the 15 W offered to a non-PD Type-C sink) lies above the trip.
     - The 9 V 2.0 A PDO sits above the trip's low end, 1.92 A.
     - Only the 15 V 1.2 A PDO is inside it.
     - The alternative in `tablet.out` 2 (PCTRL to an expander line, 36 W with PCTRL high) has 9 V 3.0 A and
       15 V 2.4 A, both above the trip.
   - **As drawn**, the 45 W straps advertise 3.0 A at 5, 9 and 15 V against the same 1.92 to 2.26 A trip. The page's
     wording "advertise ... 45 W peak" is correct, but the outlet as drawn cannot deliver it. **No record in the tree names
     R138's trip** (searched `v2/docs` for R138 and the trip figures). File it as a board A finding.
   - **The maker's own inconsistency.** The electrical table labels its 29 to 34 mV row "HIPWR = DVDD (5 A enabled)".
     That contradicts Tables 4 and 5 and 8.3.6, where HIPWR to DVDD gives 3 A. Under that label the trip would be 2.9 to
     3.4 A at 10 mOhm, still no margin at a 3.0 A PDO. Either reading leads to the same correction.
   - **Correction.** Add R138 to the proposal's electrical corrections (TI's 5 mOhm puts the trip at 3.8 to 4.5 A, above
     every PDO of both settings). Or state that the 18 W peak is deliverable only on the 15 V contract. The energy figures
     are unaffected: the model charges the kit side at its bound, and a lower deliverable power only lowers the tablet's
     draw.
2. **"A ceiling the strapped board and the window enforce without a meter"** (TABLET-BUDGET.md line 62, `tablet.out`
   2) is stronger than the circuit.
   - The 18 W cap is a USB PD advertisement that a compliant sink obeys.
   - The hardware bound at the 15 V contract is the OCP trip: 1.92 to 2.26 A, 28.8 to 33.9 W.
   - Suggested wording: "held for a compliant sink; the OCP trip bounds a non-compliant one".
   - The measurement column should also say that E_OUT is read with an inline USB-C meter at verification. The kit
     cannot meter it: six INA226 (U8 to U11, U14, U17), none on the outlet, as the page's "No meter" bullet already says.
3. **WAB is used unexpanded on the page** (lines 98, 106, 107 and 134).
   - **The tree's expansion:** "the worst array build, not a weather case" (`l3plane/ENERGY-BASIS.md` line 314,
     `handover/layer3/OWNER-DECISIONS-L3.md` line 77).
   - **"The weather-adverse build" appears nowhere in the committed tree.** I searched TABLET-BUDGET.md, tablet.py,
     tablet.out, COMPARISON.md and the commit message. The only "adverse" is the function name `R40.adverse()` at
     tablet.py line 327.
   - If the covering note or the owner message calls WAB the weather-adverse build, that is a naming error: WAB is an
     installation and component case on the same mean day. Correct it there and expand WAB once on the page.
4. **"up to 22 % lost in the tablet's own charger"** (line 62, `tablet.out` 2). The 22.4 % is 36 / 29.41 minus 1, the
   overhead over the battery's energy. As a share of the 36 Wh delivered, the loss allowed is 18.3 % (a charger efficiency
   down to 0.817). Reword the sentence to one of the two meanings.
5. **"the class's largest battery (29.41 Wh)".** Zebra's p.3 also lists an "Optional hot swappable 3400 mAh 7.6 V
   (25.84 Wh) secondary battery, for use with expansion back accessory".
   - With it an ET4x holds 55.25 Wh, which 36 Wh a day does not refill.
   - Say "the largest primary battery", or name the secondary battery as outside the budget.
6. **`fetch_held_back.py` places the tablet sheets relative to `--out`** (`../../tablet/held/` joined to it).
   - At the default this is `v2/vendor/tablet/held/`, which is correct.
   - With any other `--out`, the sheets land two levels above the chosen folder.
   - Give the tablet sheets their own default, or document the behaviour in the usage line.

## What holds

- **(1) No double counting.**
  - `pwr_budget.out`'s PS-IDLE-SPEC section has 39 shares summing to 42.82 W. None names a tablet, USB-C, outlet, PDO,
    U18 or U19 (checker's own parse).
  - `load_trace.out` gives the tablet no row (CHECK-1).
  - Every tablet figure is added on top of the 42.8 W, including the converter's draw when enabled.
- **The idle draw, 1.09 / 1.44 W (INFERRED), reproduced from the makers' terms.**
  - LM5176 p.6: 2 / 4 mA at 14.4 V = 0.029 / 0.058 W.
  - CSD18510Q5B p.3: Qg 58 / 75 nC at 4.5 V and 118 / 153 nC at 10 V, interpolated to 89.1 / 115.4 nC at VCC 7.35 V.
    4 x Qg x 206 kHz (R78 40.2k) x 14.4 V = 1.057 / 1.370 W.
  - TPS25740A p.8: 1 / 3 mA at 5 V over 0.90 = 0.006 / 0.017 W.
  - Sum: 1.09 / 1.44 W.
  - Forced CCM is R135 100k on MODE. The four FETs are Q21, Q22, Q25 and Q26.
  - Excluding the ripple and core losses is stated. With no sink, VBUS is off and the stage sits at 5 V with two FETs
    switching (0.53 / 0.69 W on the same terms), so 1.44 W is conservative for those hours.
- **(2) The straps, read on the netlist and Table 5.**
  - U18 pins: HIPWR (pin 5) and PSEL (pin 12) on PD_DVDD, EN9V (pin 8) on GND, PCTRL (pin 14) on PD_VAUX.
  - **As drawn:** 5, 9 and 15 V (Table 2, EN9V low with HIPWR direct) at 3 A (Table 5, PSEL direct to DVDD, PCTRL high).
    That is 45 W advertised.
  - **Proposed:** PSEL and PCTRL to GND give P(SEL) 36 W (Table 3), halved to 18 W (Equation 2): 5 V 3.0 A, 9 V 2.0 A,
    15 V 1.2 A.
  - PSEL is latched after reset and PCTRL is read dynamically (8.3.6), as the page's spare-line remark assumes.
  - PD_EN = U26 pin 11 = PD_SW_EN (pin 12) AND OUTLET_OK (pin 13), so the window is a software rule on an existing line.
- **The makers' tablet figures and terms.**
  - Zebra p.3: "6100 mAh 3.87 V ... (23.61 Wh)" and "7600 mAh 3.87 V ... (29.41 Wh)". The sheet reads "(c)2025 Zebra
    Technologies Corp. and/or its affiliates. 10/13/2025".
  - Samsung p.2: "Li-Po 5,050mAh, removable", with footnote "Rated (minimum) capacity is 4,900mAh". Its notice reads
    "(c) 2024 Samsung Electronics America, Inc. All rights reserved.". 5,050 x 3.85 V = 19.4 Wh.
  - Both files' sha256 and sizes (3273073 and 169804 bytes) equal the `sources.txt` lines and `fetch_held_back.py`'s
    pins.
- **The 0.930 efficiency.**
  - I viewed LM5176 Figure 6-2 (p.9) myself. At 1.5 A the VIN 24 V curve reads about 94.5 to 95 % and the VIN 12 V curve
    about 98 %, in line with `tablet.out` 3's 94.5 and 97.9.
  - Taking the declared 0.93 below both readings is the conservative choice. 36 / 0.930 = 38.71 Wh a day, and
    18 / 0.930 = 19.35 W peak at VBAT.
- **(3) Schedules: the daylight reason is confirmed from my own trace.** NOM TYP 72 h W13 at 4S11.79P, start 06, second
  day:
  - The node reads 104, 121, 121, 121, 121, 121, 121, 102, 60 and 16 W from 08 to 17 UTC, level at 09 to 14.
  - The packs reach at most base 212.6 of 218.4 Wh and lid 358.3 of 372.3 Wh.
  - They never fill, so both daylight windows fall inside the level hours and read alike.
- **(4) The options table** reproduces cell by cell (below). This includes the pack counts at 58 to 67 Wh a pack: A 2
  packs NOM to WE and 3 at WE90; B 2 packs at NOM, 3 to 4 at NOM90 and WE, 5 at WE90.
  - The masses follow from 0.435 kg a pack: 0.87, 1.3, 1.74 and 2.2 kg. The 0.435 kg is from NH2054HD34 sheet 3.6.1,
    "Approximately 0.97lbs. (0.435Kg)", held sha `5be44725`.
- **(5) Wording.** The 72 h provenance holds:
  - SC-L2-05 at `de59686e` (a commit), then SC-21.
  - D-20's "with their specified duration" (REQUIREMENTS-TRACE.md line 245).
  - D-21's "Preserve the approved 72-hour mission" (OWNER-INSTRUCTION-2026-09-30.md line 24).
  - WAB is kept as a sensitivity with no owner ruling claimed.
  - Option B's recommendation reads "feasible on the model only with its store: about 190 Wh ... or about 260 Wh with HF
    listening, with the corrected path and the outlet correction". Minor 1 adds R138 to that correction.
  - Option A is "relief of about one pack, not a cure". Battery-only and solar-assisted figures are kept apart.
- **(6) Hygiene.**
  - **Reruns:** `tablet.py` (3 s), `runtime.py` (59 s), `load_trace.py` and `lid_21700.py` all exit 0, and each
    output is byte identical to the committed one.
  - **Held files:** no held file is committed (`git ls-files v2/vendor/tablet v2/vendor/battery/held` is empty), and
    `.gitignore` adds `v2/vendor/tablet/held/`.
  - **Untouched paths:** nothing under `v2/ecad` or `v2/docs/handover` changed, and `pcb_requirements.yaml` is
    untouched.
  - **Added lines:** none carries U+2012 to U+2015 or U+2212 (the only hyphens are table rules, code and list bullets).
    None carries a host name, home path, scratch path or address.
  - **The commit:** authored by the owner, with no trailer.
  - **The l3batt worktree:** at `63897fc3`, `git status` clean, no `__pycache__` or `.pyc` anywhere under `v2`.
    Its ignored files beyond the archive are only the held vendor sheets and IBIS models.

## Figures beside theirs

| Item | Theirs | Checker |
|---|---|---|
| Idle draw, enabled, no load | 1.09 / 1.44 W | 1.092 / 1.445 W |
| Energy at VBAT a day, window / peak | 38.7 Wh / 19.4 W | 38.71 Wh / 19.35 W |
| ANY a day (converter on all day) | 73.4 Wh (idle 1.445 W) | 73.27 Wh (idle 1.44 W) |
| Schedules, NOM TYP, 48 h: none / W13 / W10 / W19 / ANY | +68.1 / +68.1 / +68.1 / +107.2 / +139.7 | +68.1 / +68.1 / +68.1 / +107.2 / +139.5 |
| Schedules, NOM TYP, 72 h: none / W13 / W10 / W19 / ANY | +68.1 / +88.0 / +88.0 / +130.9 / +197.4 | +68.1 / +88.0 / +88.0 / +130.9 / +197.2 |
| Option A, 48 h W13 TYP: NOM / NOM90 / WE / WE90 | +68.1 / +114.7 / +116.0 / +164.3 | +68.1 / +114.7 / +116.0 / +164.3 |
| Option A, WAB range | +94.8 to +193.1 | +94.8 (NOM) to +193.1 (WE90) |
| Option B, 72 h W13 TYP: NOM / NOM90 / WE / WE90 | +88.0 / +186.8 / +189.9 / +286.1 | +88.0 / +186.7 / +189.9 / +286.0 |
| Option B, WAB range | +146.5 to +342.5 | +146.4 (NOM) to +342.5 (WE90) |
| HF listening, A: NOM / NOM90 / WE / WE90 | +105.1 / +156.3 / +158.4 / +206.0 | +105.1 / +156.3 / +158.4 / +206.0 |
| HF listening, B: NOM / NOM90 / WE / WE90 | +153.2 / +255.3 / +260.2 / +354.6 | +153.2 / +255.3 / +260.1 / +354.5 |
| Present store with W13, unserved: 48 h NOM / WE; 72 h NOM / WE | 102.2 / 104.6; 165.7 / 169.2 | 102.2 / 104.6; 165.7 / 169.2, stops h 23/11 |
| A's 48 h store run to 72 h, short: NOM to WE90 | 15.3 to 113.4, stops h 48 and 57 to 60 | 15.2 (NOM), 65.7 (NOM90), 66.5 (WE), 113.3 (WE90); stops h 48 and 58 to 60 |
| As drawn, unserved: 48 h / 72 h | 302.7 / 566.6 | 302.7 / 566.7, stops h 23/11 |
| As drawn, least store: 48 h / 72 h | at least +328 / +614 | +328.1 (4S19.39P) / +614.5 (4S28.46P) |
| Battery only, present store, window in the run | 11.81 / 4.34 h | 11.81 / 4.34 h (their store form); 11.85 / 4.35 h (my cells) |
| Battery only, A NOM / A WE store | 13.40 / 4.99; 14.52 / 5.46 h | the same in their form; 13.68 / 5.11 and 14.97 / 5.64 h with the store as added cells |
| Battery only, B NOM / B WE store | 13.86 / 5.19; 16.24 / 6.17 h | the same in their form; 14.22 / 5.33 and 16.96 / 6.46 h as cells |
| Daylight rule worth, 72 h | 43 to 109 Wh | 42.9 to 109.2 Wh |
| A saves against B, TYP: NOM / NOM90 / WE / WE90 | 20; 72 to 122 Wh | 19.9 / 72.0 / 73.9 / 121.7 Wh |
| R138's OCP trip (HIPWR 3 A) | not stated | 1.92 to 2.26 A (19.2 to 22.6 mV over 10 mOhm) |

The battery-only rows differ only in form. `tablet.out` 7 takes the options' added store as an external store: the
13.23 C Wh counted at +20 C, and x 0.4124 at -10 C (stated there as INFERRED). My rows count the same cells in the lid
pack at each temperature, so theirs are the lower, conservative figures.
