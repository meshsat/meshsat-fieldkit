# L4-E2: the energy architecture under REQ-016's retained 100 W window (layer 4, MESHSAT-1357)

**1 October 2026.** Branch `fnd/l4e`, from main `b45d1705` (the Layer 3 baseline accepted at `b4b199d0`, the fixed
input). **Prototype design:** nothing is bought, built, powered or measured. This page is the author's analysis, AI
arithmetic, not a qualified review and not the independent check. It edits no registry record, no Layer 3 record and
nothing in `v2/docs/handover/`. Every figure below is printed by `l4e_replay.py` into `l4e_replay.out` (its section
numbers are given as "out N") or quoted from a named record. The direction is the collaborator's L4-E1 assessment
(`ASTRA-L4E1.md`, filed here byte for byte), which the coordinator accepted. **Second issue, 1 October 2026:** it
answers the focused check `checks/astra-check-l4e2-1.md` (accepted: no; blockers B1 and B2, minor M1). Served and
unserved energy is now the replay's SERVICE LEDGER, counted from the traced load flows (B1); O-2 bounds V_in x I_in,max
at 100 W across the admitted loaded voltage (B2); M1's label is corrected; the Layer 3 headline is recomputed with the
ledger (last section). **Third issue, 1 October 2026:** it answers the recheck `checks/astra-check-l4e2-2.md` (accepted:
no; B2 again, the IMON_IN line regulation left out of a tolerance list picked by hand, and the sweep's lower end). O-2's
setting now comes from every row of the LT8705A's electrical characteristics that moves the limit, enumerated, read back
from the sheet and stacked worst case, and the replay refuses to print if any corner of the envelope exceeds 100 W.

**Labels.** MAKER (a maker's document, file and page); NETLIST; MODELED (the energy model); INFERRED (a stated method);
DECLARED or ESTIMATE (a figure no maker document gives for this circuit); HYPOTHETICAL (a corrected path not
implemented).

**The owner's fixed constraints** (the Current owner brief of `OWNER-INSTRUCTION-2026-09-30.md`): the store inside the
Peli 1450 and no external battery; battery and solar both required; HF and the tablet kept; 48 to 72 hours a design
objective under REQ-072's profile, not a minimum; optional tablet charging reduces endurance; every other approved
requirement unchanged, REQ-016 among them (D-34). No service is reduced on this page to make a candidate pass.

## In short

- **The model is accepted first.** `runtime.py` re-run reproduces the checked `runtime.out` byte for byte, and this
  harness reproduces its sections 1 to 3, `three_cases.out`'s AS DRAWN and DERATED rows at WE, and `energy_budget.out`'s
  single-pack rows (out 0). Only then is one input moved: the stage's input clip from P-03's 200 W to REQ-016's 100 W.
- **Neither architecture meets 48 hours** under the one assumption set, on either path. A2 on the hypothetical corrected
  path stops at 05 UTC of the first night (11 or 23 h), 270.1 / 286.3 Wh short at 48 h and 500.4 / 516.5 Wh at 72 h (06
  / 18 UTC starts); it needs **+278.8 Wh** (48 h) and **+515.8 Wh** (72 h) of usable storage more (out 3, 4). A1 stops 2
  or 13 h in and needs +654.8 and +873.1 Wh.
- **Service is counted from the traced load flows** (check B1). The model's own counter, the legacy model metric,
  credits each stopped hour's sun up to the load as served while it also charges the packs with it. The ledger counts
  that sun once, and its kit balance closes within 1e-6 Wh on every run (about 1e-12 Wh on those printed; out 5). The
  first interruptions and the least additions are unchanged; every unserved figure rises (A2 corrected, 72 h from 06
  UTC: 500.4 against the legacy 464.3 Wh).
- **No undocumented efficiency makes a pass.** With the three undocumented efficiencies set to 1.00 (U3, U3B and the lid
  path's losses retained), A2 still misses 48 h by 150.9 Wh (out 6).
- **Under REQ-016 the 200 W charge path is not needed.** The corrected path's 6.1 A cap never binds at 100 W; a U3
  setting of 4.65 A gives the same result (out 8). As drawn, A2 is 332.7 Wh short at 48 h against 270.1 corrected (06
  UTC): under the retained window the corrections are worth about 62.5 Wh at 48 h and 125.1 Wh at 72 h, not the about
  210.1 and 420.2 Wh the 200 W runs show at WE (out 3).
- **O-2 amended** (check B2, then the recheck's B2): a current limit bounds current, not power. The LT8705A's
  input-current limit is sized from every electrical-characteristics row that moves it, stacked worst case and rounded
  down: **3.548 A** nominal. A mechanical check of 106,496 corners (the loaded voltage from the hold's lower corner
  16.695 V to 25 V, both temperature ends, every tolerance at its limits) puts the worst at 25 V, 99.9984 W, a margin of
  0.0016 W; the replay refuses above 100 W (out 11). Its consequence is its own row in the table: in a limited hour the
  stage may take as little as 52.8 W, and A2 then needs +610.8 / +1167.3 Wh instead of +278.8 / +515.8 Wh.
- **Is REQ-016's window with a compliant panel represented by the SC-37 series? No.** The series in the tree is the 400
  Wp 2S2P array's (51.28 V cold), which REQ-016 does not admit, and no compliant panel's series is held. The 100 W
  results are therefore a conditional screening stimulus (out 7): they stand for a compliant source only if it delivers,
  every hour, at least the trace clipped at 100 W. That needs a pinned panel of at most 25 V open circuit at its
  coldest, its hourly power at the 17.6 V point on SC-37's day, at least 331 Wp at the trace's ratio, and the entry's 10
  A re-read for that array. A 100 Wp panel, REQ-016's own bench case (on the held panel's fit at 17.6 V), makes A2's 72
  h shortfall 1692.8 / 1919.0 Wh, not 500.4 / 516.5.
- **DR-01 stands** (last section): the Layer 3 corrected-path headline was computed at 200 W, and its unserved figures
  carry the same stopped-hour double count.

## The comparison (TYP; the corrected path unless named; each pair of figures is 06 UTC / 18 UTC start where it differs)

| | **A1: D-06's single 4S3P** | **A2: base 4S6P + separately protected lid 4S9P, both lid functions kept** |
|---|---|---|
| **Essential load and duty cycles** | PS-IDLE-SPEC, 42.8 W at the pack terminals over 39 loads (LOW 33.1, HIGH 82.8; 8.4 W with no document, the monitor 6.03 W of it; `load_trace.out`): monitor on, APRS beacons (the VHF PA's 1.07 W average, about 1.2 % duty, a placeholder; `energy_inputs.yaml`), the link card up and idle; HF available, not receiving (0.32 W; receiving +1.14 W, an additional use); the tablet not charged, the USB-C outlet off (REQ-072) | the same, plus the lid path's standby drain 0.025 W (1.8 Wh over 72 h, WE) |
| **Usable internal storage** (aged 80 %, 3.00 V and 5 %) | 107.9 Wh at +20 C, 44.5 Wh at -10 C (out 2) | 544.4 Wh at +20 C, 224.5 Wh at -10 C; 502.6 Wh at the solar runs' temperatures (base 218.4 at +20 C, lid 284.2 at 13.23 C; `runtime.out` 2) |
| **Solar contribution** (the stimulus: the 400 Wp trace clipped at 100 W; WE; 72 h from 06 UTC; out 5, 7) | 982.6 Wh a day into the stage, 827.1 Wh a day at the node (2481.4 Wh in 72 h), 200.1 Wh a day under the 1027.2 Wh the load asks; used: 1350.8 Wh straight to the load, 240.5 Wh stored, **854.4 Wh spilled** (the pack is full by midday) | the same sun; used: 1351.5 Wh straight to the load, 734.0 Wh stored, 326.1 Wh spilled (0.0 from 18 UTC). The window's ceiling with a 20 kWp array is 1016.8 Wh a day on WE's chain: at the declared efficiencies no array carries the day through it |
| **Conversion losses** (72 h from 06 UTC, WE; out 5) | stage and front end 398.3 Wh (2947.8 Wh into the stage, 2549.5 Wh at VBUS20: 0.93 x 0.93, DECLARED); U3 68.2 Wh (0.9733, INFERRED); charge side 35.7 Wh (13.8 Wh the 0.95, INFERRED; 21.9 Wh the model's full-store clamp, charge taken at the node that a full pack does not store). As drawn, a further 214.8 Wh at VBUS20 is refused by U3's 4.05 A cap (24 capped hours) | stage and front end 398.3 Wh; U3 68.2 Wh; charge side 69.8 Wh (the base's 0.95 15.9, U3B 0.963 and the lid loop 0.040 Ohm 19.8, the lid's 0.95 23.3, the clamp 10.8); discharge side 5.1 Wh (the lid path, V(AK) 29 mV and 0.045 Ohm, 0.1 Wh of it at the cutoff). As drawn, 214.8 Wh refused |
| **Peak power** | discharge: PS-ALLTX 203.8 W PLAN, 272.0 W HIGH; the PA keyed over PS-IDLE-SPEC 122.4 to 162.3 W PLAN, 12.4 to 16.6 A at 10 V (`pwr_budget.out` lines 9, 163, 164), all from the one pack (CELL+ declared 10 A typical, 18 A peak, `gen_sch_a.py`). Charge: at most 100 W into the stage, 86.5 W at VBUS20 on the declared efficiencies (out 8) | the same demand shared through the join; the lid's discharge path limits at 8.7 / 9.8 / 11.0 A (LM5069 VCL 48.5 / 55 / 61.5 mV over 5.6 mOhm, MAKER SNVS452G p.6; `TOPOLOGY.md`), so the base carries the rest, and after the lid's cutoff (hour 22 / 10 in the replay, out 5) the base alone. Charge as A1 |
| **Thermal limits** (FEA-008, per mode) | charge 0 to +45 C and discharge -10 to +60 C at the cell surface (MAKER, Samsung 35E Ver. 1.1, 3.12); the gauge's ladder starts a charge only between 1 and 42 C in its reading and turns discharge off at -9.0 C in its reading (-9.8 to -8.5 C true, no discharge below -9.8 C; `THERMAL-COORDINATION.md` 4), so REQ-072's -10 C battery-only case lies just past the ladder: a boundary figure, not an operating point. FEA-008's collisions stand: up to 2.1 K in hot use lid closed (LO-01a), 1.6 to 14.2 K at +55 C (LO-01d), at least 6.63 K in the humid dwell (LO-01e), 11 K at +71 C storage (LO-01f), 13 K at -33 C storage (LO-01g). No cell or thermal design closes them | the base as A1; the lid pack at 13.23 C in the model, inside the charge window. Its real temperature is INCONCLUSIVE (no thermal model): it lies 2.2 mm under the lid's skin, which faces the sky when closed (a1mech README 5), and its heater mat is not placed. The same FEA-008 collisions apply to both packs, the lid's unmodelled |
| **Mass** | 12 cells, 0.60 kg (50 g maximum, spec 3.10) | 60 cells, 3.0 kg. The lid pack adds 2.63 kg to the lid (cells 1.950 for all 39 places, 4S9P using 36; plate 0.248, cover 0.105, strip 0.077, wrap and glue 0.088, P2 0.080, harness 0.080 kg; ESTIMATE but the cells), the lid 4.53 kg in all; the base's second block 0.75 kg; so about 3.2 to 3.4 kg over A1 (`lid_pack_a1.out` 4). Far inside REQ-023's 45.4 kg (a1mech README 5) |
| **Volume** | one block 56.65 x 133.50 x 38.10 mm (0.288 L) in the east pocket, which holds it alone (`packfit_west.out`) | two such blocks (0.576 L) in the base pockets, with M4a (1.85), M5 (1.77) and the west block over C33 (3.99) OPEN and the west RF entry to re-plan (a1mech README 6); the lid module over 213.75 mm by up to 227.10 mm (INFERRED from its printed coordinates), 24.00 mm deep (40.06 mm under the nested layer), 39 places, 36 used (`lid_pack_a1.out` 2; its volume is not printed: INCONCLUSIVE) |
| **Battery-only runtime** against 48 to 72 h (out 2) | 2.52 h at +20 C, 1.04 h at -10 C: short by 45.5 h at 48 h and 69.5 h at 72 h | 12.71 h at +20 C, 5.24 h at -10 C: short by 35.3 h and 59.3 h |
| **Solar-assisted runtime** against 48 to 72 h (out 3) | CORRECTED, HYPOTHETICAL: first interruption at h 13 (19 UTC) / h 2 (20 UTC); full service 25 of 48 h and 37 of 72 h. AS DRAWN, upper bound: the same hours. AS DRAWN, lower bound (A-2's collapse): h 12 / 2 | CORRECTED, HYPOTHETICAL: first interruption at h 23 / 11, both 05 UTC; full service 41 / 40 of 48 h and 59 / 58 of 72 h. AS DRAWN, upper bound: h 23 / 11, 40 / 39 and 57 / 56 h. Lower bound: h 21 (03 UTC) / 11, 34 and 47 h |
| **The gap, Wh and hours** (the service ledger; out 3, 4, 5) | CORRECTED: 907.4 / 923.5 Wh unserved at 48 h, 1382.5 / 1398.6 at 72 h (23 and 35 hours without service); the least addition **+654.8 Wh** (48 h) and **+873.1 Wh** (72 h), one pack of 4S20.95P and 4S26.95P. AS DRAWN: 907.3 / 923.5 and 1382.4 / 1398.5 Wh (upper bound), +719.3 and +1002.2 Wh; 1068.3 and 1645.2 Wh (lower bound), +930.8 and +1366.0 Wh. WAB: +668.1 and +898.3 Wh | CORRECTED: **270.1 / 286.3 Wh** at 48 h, **500.4 / 516.5 Wh** at 72 h (7 to 8 and 13 to 14 hours without service); the least addition **+278.8 Wh** (48 h) and **+515.8 Wh** (72 h), a lid of 4S17.83P and 4S25.33P (781.4 and 1018.4 Wh in all). AS DRAWN: 332.7 / 348.9 and 625.5 / 641.7 Wh (upper bound), +341.6 and +641.0 Wh; 541.9 and 984.8 Wh (lower bound), +555.1 and +1008.0 Wh. WAB: +291.9 and +540.7 Wh |
| **Solar-assisted under O-2's conservative bound** (its own row, apart from the 100 W screening case; CORRECTED, WE, TYP, still on the stimulus; setting 3.548 A; out 11) | at the lower corner, 52.8 W into the stage in a limited hour (16.695 V x 3.162 A): first interruption h 13 / 2; 991.7 / 998.6 Wh unserved at 48 h, 1541.9 / 1548.8 at 72 h; least addition +995.0 / +1544.3 Wh. At the nominal hold, 62.4 W (17.593 V x 3.548 A): 907.4 / 923.5 and 1382.5 / 1398.6 Wh (the pack is night-limited), +908.8 / +1381.2 Wh | at the lower corner, 52.8 W: first interruption h 22 (04 UTC) / 11; 601.4 / 607.7 Wh unserved at 48 h, 1153.0 / 1159.4 at 72 h; least addition **+610.8 / +1167.3 Wh**. At the nominal hold, 62.4 W: 516.6 / 532.8 and 993.4 / 1009.6 Wh, +525.8 / +1008.0 Wh. Where a compliant panel lands between these and the 100 W case is its own curve (O-1) |
| **Owner rulings changed** (explicit proposals) | **None.** Closing its gap would need 4S21P to 4S27P in one pack: that changes D-06 (one 4S3P in the east pocket) and has no place in the case | **D-06 only** (proposal P-01: two separately protected packs, with DR-07's lid consequences). REQ-016 is kept; P-03's 200 W stage is not part of it. Closing its own gap would need a lid of about 4S18P to 4S25P, which the lid does not hold with both functions kept (39 places; SHORTLIST.md 3) |

**The assumption set** (out 1): SC-37's mean September day at Leiden, one plane 40/0, TYP (WAB a sensitivity), starts 06
and 18 UTC, full stores aged to 80 %, the 3.00 V line with the 5 % reserve, the base at +20 C and A2's lid at 13.23 C;
battery-only at +20 C and -10 C. The corrected path is ENERGY-BASIS 6c's WE (bus 19.146 V, U3's limit 6.1 A, U3 0.9733,
U3B 0.963, the three undocumented efficiencies at 0.93, 0.93 and 0.95, the lid loops' worse ends, V(AK) 29 mV, the
drain). AS DRAWN is `three_cases.py`'s DRAWN at WE: R11 10 mOhm (4.152 A to U3 at the stacked minimum), U3 at its
INFERRED 4.05 A minimum; its upper bound keeps the model's `min(available, cap)`, its lower bound is A-2's collapse.
A2's lid path is a1elec's draft (`TOPOLOGY.md`), on no generated board. A1 is charged at 1.02 A a cell
(`energy_inputs.yaml`); 1.32 A moves no figure (out 6). The pass line is COMB, as `runtime.py`. Served and unserved
energy is the service ledger's (out 5): a stopped hour serves nothing, and its sun goes to charge or spill once.

**Where a result could turn on a figure** (out 6, 8, 10). A2's least addition moves from +344.0 / +644.8 Wh (the three
efficiencies at 0.90) to +196.7 / +353.4 (0.97, 0.97, 0.98) and +131.4 / +223.4 Wh (the three set to 1.00, the other
losses retained): no value decides the verdict. U3 re-weighted over the 100 W day (0.9751) moves A2 by 1.4 to 2.9 Wh.
The steady load A2 carries through 48 / 72 h is 35.3 / 34.4 W on the corrected path and 33.5 / 32.3 W as drawn, against
the PLAN 42.8 W (A1: 8.8 W). **The objective stays unmet; the in-constraint options, each at its favourable end and none
established (out 10):** the lid pack held at +20 C (a bound, no heating energy counted; +43.5 Wh of store), a tenth lid
row (the check's 43-place bound), the high efficiency bracket. Together A2 still misses: 126.6 / 277.3 Wh unserved,
+116.0 / +271.9 Wh needed, or a load at or under 39.7 / 38.4 W. The load figures are a measurement question (the
undocumented 8.4 W), not a service reduction. What closes the gap otherwise changes a ruling: REQ-016's window (P-03,
which still leaves +79.6 / +116.2 Wh at WE, `runtime.out` 3), external storage (D-28), or a lid function out (D-33).
These are named, not proposed.

## The power-path corrections as architecture decisions

**The governing decision: size board A's solar charge path to REQ-016's window, not to P-03's 200 W.** Reason: at 100 W
into the stage the largest power at VBUS20 is 86.5 W at the declared efficiencies, 94.1 W at the 0.97 bracket and 100.0
W lossless (out 8). At the lowest bus of 19.146 V, U3's input minimum must cover 4.517, 4.914 and 5.223 A. The 50 mA
settings are then 4.65, 5.05 and 5.35 A, and the current through R11 is 4.829, 5.229 and 5.529 A with C-9's 0.079 A. A
4.65 A setting gives exactly the corrected path's result (out 8). The 6.2 mOhm and 6.2 A drafted for 200 W bring B-1 to
B-4 and C-6 with a 9.370 A highest permitted current, where the window needs 4.8 to 5.5 A through R11. The derated drawn
variant costs A2 83.1 Wh of service at 48 h against the window-sized path (369.4 against 286.3 Wh, each at the worse
start) and 83.4 Wh more storage (+362.2 against +278.8 Wh). The references are the makers' own: the BQ25731's
application circuit and its EVM (MAKER `v2/vendor/ti/bq25731-datasheet.pdf`, SLUSE66A p.83, 10.1 and Figure 10-1), the
LM5176's typical application (`v2/vendor/ti/lm5176-datasheet.pdf`, SNVSAI1D p.21, 8.2, 6 to 50 V in, 12 V at 6 A) and
the LT8705A's (`v2/vendor/power/lt8705a.pdf`, 8705af p.41, 12 V at 15 A from 7.5 to 55 V). None is a drop-in at the
kit's voltages; each item below says where the kit departs from them.

- **A-1, the front end limits below the charge design.** *Remedy:* one coordinated pair for the window: U3's IIN_HOST at
  the window-sized setting (4.65 A, or 5.05 A if the stage and front end reach the 0.97 bracket), and R11 chosen so that
  the LM5176's average-current limit (SNVSAI1D p.17, Equation 4; VSNS 43 / 50 / 57 mV, p.7) has a stacked minimum above
  that setting's maximum plus 0.079 A. Until the change, the drawn circuit runs at the derated 4.00 A (r11dep).
  *Reason:* it carries all the window gives, and nothing more. *Closure:* A-1's own: the stacked minimum of the fitted
  R11 at least U3's maximum plus the other loads; bench 7b.1 at -20, 25 and 62 C.
- **A-2, the bus collapses with a fixed IIN_HOST.** *Remedy:* a VIN_RAW-dependent IIN_HOST rule for every source
  (FW-A16's form; BQ25731 IIN_HOST, SLUSE66A p.80, and its clamp, 9.3.5 and Table 9-1, pp.25 and 26). *Reason:* in TI's
  Figure 10-1 the charger's VBUS is the source itself, so its own input regulation sees a sagging source. Board A's
  front end regulates VBUS20, so U3 cannot see the panel sag, and a firmware rule is the bound that remains. A2's lower
  bound under the collapse leaves 193.0 to 209.3 Wh (48 h) and 343.1 to 359.3 Wh (72 h) more unserved than its upper
  bound, by start (out 3). *Closure:* bench 7b.7: a source stepped below U3's demand, VIN_RAW settles above 12 V and
  FE_PGOOD never drops.
- **B-1, L1 past its typical Isat at 9 V.** *Remedy:* in service, the window-sized setting (4.65 A, or 5.05 A at the
  bracket) is at or under r11dep's 9 V schedule setting of 5.05 A, whose 5.18 A maximum puts L1's peak at 15.68 A, 89.6
  % of the typical Isat; so no separate schedule is needed at the declared figures, and A-2's rule carries it if one is.
  In a fault, L1 is rated for the window-sized path's highest permitted current, or that current is bounded (B-2).
  *Reason:* the solar entry runs at 15.1 V, so nothing at 9 V costs solar energy. A window-sized R11's fault current is
  INFERRED at about 6.66 to 7.21 A (the stacked band's max/min ratio 1.379 at 4.829 to 5.229 A), between the held 5.81 A
  (within) and the proposal's 9.37 A (over). *Closure:* B-1's own, recomputed at the chosen R11 with C-5's derating:
  peak at most 90 % of Isat at the part's temperature; bench 7b.5.
- **B-2, the FETs at the highest permitted current.** *Remedy:* enable the LM5176's hiccup mode (SNVSAI1D pp.17 and 20:
  shutdown after 128 consecutive cycle-by-cycle limits), and choose the FETs and copper for the window-sized fault
  current. *Reason:* the maker's own protection, and a fault current 23 to 29 % under the proposal's 9.37 A (INFERRED as
  above). *Closure:* TJ at most 150 C at the chosen highest permitted current at 9, 15.1 and 36 V in 62.1 C air, from
  board A's own thermal resistance or a measurement (7b.4).
- **B-3, the copper declarations.** *Remedy:* re-declare VBUS20, FE_OUT, VIN_RAW, _FE_A, _VIN_T and TRK_OUT at the
  window-sized path's currents, then regenerate. *Reason:* the declarations must follow the chosen currents. *Closure:*
  dc_drop, derate and the track-width gates PASS on the regenerated board.
- **B-4, VBUS20's bulk capacitors.** *Remedy:* re-run the generator's node analysis at the chosen fault current, and
  enlarge or rebalance the bank, or bound the fault (B-2's hiccup). *Reason:* r11dep's proportional scaling puts the
  worst can at about 2.85 to 3.09 A at 2:1 for 6.66 to 7.21 A (INFERRED), against 2.8 A a can (Panasonic p.2).
  *Closure:* every can at most 2.8 A over the ESR bands; bench 7b.8.
- **B-5, a fixed 6.2 A drops FW-A16's scaling.** *Remedy:* A-2's rule. With the window-sized path, no fixed setting is
  the design. *Closure:* 7b.7.
- **C-1, Kelvin taps on R11.** *Remedy:* Kelvin routing at layout (engineering), with the tap allowance recomputed for
  the chosen R11 from the same margin rule (0.29 mOhm at 25 C for 6.2 mOhm). *Closure:* kelvin_check at or under the
  recomputed allowance; bench 7b.3.
- **C-2, R11's order code.** *Remedy:* the chosen value's catalogue part, 1 %, 50 ppm/K or better, 3 W class
  (HoJLR2512's family). *Closure:* its sheet filed.
- **C-3, board A's thermal resistance for Q2 to Q5.** *Remedy:* a figure from the laid copper at the chosen currents.
  *Closure:* C-3's criteria recomputed at those currents, or a measurement.
- **C-4, C11 and C12's ripple rating.** *Remedy:* parts with a maker's ripple rating at 36 V in buck at the chosen
  current. *Closure:* the maker's figure filed (7b.8).
- **C-5, L1's Isat against temperature.** *Remedy:* file Coilcraft's derating. *Closure:* the derating read at the
  part's temperature and fed to B-1.
- **C-6, board E's 200 W stage, not designed.** *Remedy:* not designed. The stage stays in its drawn 100 W class (17.6 V
  point, F2 and J_SOLAR 10 A), with its input held to 100 W by O-2. *Reason:* the 200 W stage is P-03's, which is the
  owner's (REQ-016, D-34). With O-2 and A-2's rule, the front end's demand follows what the stage gives. *Closure:*
  O-2's; bench 7b.9 with the stage at its limit.
- **C-7, U3's input-current minimum.** *Remedy:* TI's figure or a bench reading. The window-sized setting carries the
  records' INFERRED 0.1 A margin. *Closure:* the reading at or above the setting less 0.1 A.
- **C-8, the three undocumented efficiencies.** *Remedy:* the makers' figures for these circuits, or measurements at
  bring-up of the stage (17.6 to 15.1 V), the front end (15.1 to 20 V) and the pack's charge efficiency. *Reason:* they
  size the gap (A2: +131.4 to +344.0 Wh at 48 h) and decide no verdict (out 6). *Closure:* measured values in the
  replay.
- **C-9, VBUS20's other loads.** *Remedy:* R11 is sized against 0.079 A (four FETs switching), so C-9 cannot move the
  choice. *Closure:* a bench reading of R11's current less R16's at U3's full draw.
- **R138, DR-03: the outlet's shunt trips below its 3 A contracts.** *Remedy:* TI's recommended 5 mOhm (MAKER
  `v2/vendor/ti/ti-tps25740.pdf`, SLVSDG8B 8.3.8.2 p.31: "the OCP threshold lies between 3.8 A and 4.5 A" at 3 A).
  *Reason:* the maker's reference, no custom part; at 10 mOhm the trip is 1.92 to 2.26 A (CHECK-3 of l3batt). The
  profile charges no tablet, so no figure here moves. *Closure:* the netlist carries 5 mOhm; the trip from VI(TRIP) 19.2
  to 22.6 mV lies above every PDO's current; a bench 3 A load on each PDO holds without a trip.
- **O-1, DR-04: the panel is not pinned.** *Remedy:* select and pin a panel that REQ-016 admits. The held RNG-100DB-H is
  outside it even alone (25.64 V at -20 C cells); a1solar ARRAY.md 5 admits the SunPower (24.05 V) and PowerFilm's 15 V
  model (24.86 V) at -20 C, and none at -40 C. *Reason:* the energy result needs a compliant source's own trace (next
  section). *Closure:* the sheet of the revision bought filed with its mark and sha256; its open-circuit voltage at its
  coldest operating temperature at most 25 V; its availability trace at the 17.6 V point computed by a1solar's method;
  O-3 to O-7 re-derived for it, the entry's 10 A included.
- **O-2, DR-04: the stage's input power is not controlled** (amended after check B2 and the recheck's B2). *Remedy:* the
  LT8705A's own input-current limit (MAKER 8705af p.31, "Current Limiting", Figure 11: IMON_IN = I x RSENSE1 x gm(A7) x
  RIMON_IN, regulated by EA2 at 1.208 V typical; as drawn CSPIN and CSNIN are tied to the input, pp.11 and 12), sized so
  that V_in x I_in,max stays at or under 100 W at every corner of the envelope. A current limit bounds current, not
  power: FBIN only lowers the current when the input falls below its set point (p.29), so while the current loop limits,
  the input rises along the panel's curve toward its open-circuit voltage. The 5.68 A first proposed is 113.6 W at a
  loaded 20 V and 142.0 W at 25 V. *The rows (out 11):* every parameter of the sheet's electrical characteristics (pp.3
  to 6) that names the mechanism or the hold is enumerated, read back from the pinned sheet by column, and classified.
  Those that move the limit and enter the stack: the IMON_IN reference 1.187 / 1.208 / 1.229 V over the full range
  (p.4); its line regulation, 0.005 %/V at most, either sign, from the 12 V it is printed at to the corner's voltage
  (p.4); the A7 gain 0.95 / 1 / 1.05 mmho at 25 C, 0.94 / 1.06 (E, I) and 0.93 / 1.07 (H, MP) over the full range (p.5;
  the netlist names no grade, so the widest); and, as an allowance, EA2's finite gain, 130 V/V typical, over VC's
  absolute maximum range -0.3 to 2.2 V around the references' VC = 1.2 V (p.5 and p.2; no minimum gain and no VC
  operating range are printed, so the TYP gain is taken as the bound, an ASSUMPTION): 11.54 mV. The two setting
  resistors are taken at 1 % each (an ASSUMPTION: no part is chosen). The pins' bias current moves nothing because the
  maker forbids series resistance on them (p.30); the common-mode, differential and IMON_IN output-current rows are
  conditions the design meets; the fault threshold and the SRVO flags do not move the limit. *The setting:* the ceiling
  at 25 V falls from the first issue's 3.622207 A to 3.619854 A with the line regulation, to 3.581345 A with every
  grade's A7 limits, and to 3.548056 A with the EA2 allowance; rounded down to the stated 1 mA, **3.548 A** (3.586 A if
  procurement fixed the E or I grade). *The envelope and the check:* the loaded voltage runs from the hold's
  tolerance-adjusted lower corner, **16.695 V** (R8 102k and R9 7.50k at 1 %, NETLIST; FBIN 1.182 V, every grade's
  minimum, p.4; its line regulation, the EA3 allowance of 16.67 mV and the FBIN bias against it), to REQ-016's 25 V
  open-circuit ceiling, at both temperature ends. The check reads the limit's rows from the sheet independently of the
  classification and evaluates 106,496 corners: the worst is 25 V with every term at its high end, **99.9984 W, a margin
  of 0.0016 W**; the replay refuses to print above 100 W (it does when the line regulation is dropped from the stack:
  100.0548 W). *Consequence, its own row in the table:* in a limited hour the stage takes between 52.8 W (16.695 V x
  3.162 A, the limit's lowest there) and 100 W; at the nominal hold and setting 62.4 W. Where in between is the admitted
  panel's own curve (INCONCLUSIVE until O-1); once O-1 pins a panel, its highest loaded voltage at the limit replaces 25
  V and lifts the setting. *Reason:* it is the maker's own function on the part already on board E, and its bound needs
  no efficiency. An output-current limit at the regulated 15.1 V bounds the input only through the stage's undocumented
  efficiency (C-8). A voltage-dependent limit would be custom circuitry, justified only if the pinned panel shows the
  conservative bound costs too much. Rating everything downstream for the uncontrolled ceiling of about 331 W
  (L3-FEASIBILITY 3b) is the larger change. *Closure:* the setting's derivation in `gen_sch_e.py` from the chosen
  resistors' own figures and the rows above, re-run through `l4e_replay.py`'s check. Then a bench sweep, not a single
  point: a PV emulator whose curves put the loaded voltage at the limit from the tolerance-adjusted lower hold corner,
  16.695 V, up to 25 V, at the load's maximum and at both temperature ends, reading V_in x I_in at or under 100 W at
  every point. The IMON_IN loop regulates a filtered current (CIMON_IN, p.31), so the steady-state record and the
  transient record are kept apart.

## What stays INCONCLUSIVE, and the evidence missing

- **The performance of a REQ-016-compliant panel.** Missing: a pinned compliant panel's sheet (O-1) and its hourly trace
  at the 17.6 V point. Every 100 W figure here rests on the non-compliant 400 Wp trace.
- **The as-drawn figures between their bounds.** Missing: bench row 7b.7 (A-2). The truth lies between the upper bound
  (`min(available, cap)`) and the collapse bound.
- **The three efficiencies (C-8) and U3's input-current minimum (C-7).** Missing: the makers' figures for these
  circuits, or measurements. They move the gap (out 6) but no verdict.
- **The 8.4 W of PS-IDLE-SPEC with no document.** Missing: the makers' figures or measured loads. A2's corrected path
  turns at 35.3 W (out 6).
- **The loads' converters down to the 12.0 V node.** Missing: a record that every load converter runs to the 3.00 V line
  (SHORTLIST.md 2). The usable-energy figures assume it, for both architectures.
- **The lid pack's temperature and the cells against FEA-008.** Missing: a thermal model or measurement of the lid pack,
  and a cell or thermal design for LO-01a to LO-01h. The 13.23 C basis is the model's.
- **The window-sized path's fault currents (B-1 to B-4).** Missing: `r11_dep.py`'s analysis at a chosen R11. The 6.66 to
  7.21 A and the bank's 2.85 to 3.09 A are INFERRED by scaling.
- **The lid module's volume and the base rows M4a, M5 and M6w.** Missing: a printed volume, and the mock-up that closes
  the OPEN rows (a1mech README 7).
- **The stage's input under O-2 between 52.8 W and 100 W, and the setting's two allowances.** Missing: the pinned
  panel's curve at the limit (O-1), the setting resistors' figures, a minimum gain for EA2 and EA3 and an operating
  range for VC (the sheet prints neither, so the allowances take the TYP gains and VC's absolute maximum range), and the
  bench sweep.
- **The entry's ratings for an array above about 150 Wp.** Missing: the compliant array's short-circuit current against
  F2 and J_SOLAR's 10 A (O-3 to O-7 re-derived).

## The next discriminating calculation, then the experiment

1. **Calculation: a REQ-016-compliant panel's own trace.** Pin a compliant panel (O-1) and compute its hourly power at
   the 17.6 V point on SC-37's day by a1solar's ratio method. Check its array's short-circuit current against the
   entry's 10 A (the records read an array above about 150 Wp of the 12 V class as re-rating it, `energy_budget.out` 4).
   Then re-run `l4e_replay.py` on that trace in place of the stimulus. *Why it discriminates:* the stimulus fills the
   window for eight hours a day, which at its ratio needs at least 331 Wp (to fill 08 to 15 UTC; out 7). On the held
   panel's fit at 17.6 V, 100 Wp makes A2's shortfall 954.1 / 1180.3 Wh at 48 h and 1692.8 / 1919.0 Wh at 72 h, 200 Wp
   490.4 / 527.4 and 918.8 / 955.8 Wh, and 400 Wp in 1S4P 276.4 / 292.0 and 512.3 / 527.8 Wh (06 / 18 UTC). *Closure:*
   both architectures' unserved energy and least additional storage on the compliant trace, after the same reproduction.
2. **Experiment: PS-IDLE-SPEC's undocumented loads.** 8.4 W of the 42.8 W has no document. At bring-up, or from the
   makers, those loads decide whether A2's corrected path reaches 48 h: it does on the model, on the stimulus, at 35.3 W
   or less. This measures the same profile; it reduces no service. *Closure:* the measured loads in the profile, the
   replay re-run.

## The Layer 3 finding, restated

- **What the baseline stated.** The accepted Layer 3 baseline (REQ-072's evidence; REQUIREMENTS-L3-R2 2.3) has A2's
  store stopping at 05 UTC of the first night: 266.7 / 494.7 Wh unserved at 48 / 72 h as drawn, and 102.2 / 165.7 Wh on
  the hypothetical corrected path (NOM).
- **On what array.** 400 Wp in 2S2P into a 200 W stage window (`runtime.out` line 28): proposal P-03. REQ-016, kept
  unchanged by D-34, admits at most 25 V open circuit, the panel held at 17.6 V and at most 100 W into the stage.
- **The same four figures by the service ledger, under the Layer 3 case's own inputs** (P-03's array, the 200 W clip;
  out 9; each the larger of the two starts, as `runtime.out` prints them): as drawn **301.2 / 547.4 Wh** against the
  published 266.7 / 494.7; corrected, NOM, **136.6 / 218.2 Wh** against the published 102.2 / 165.7. The published
  figures are understated by the stopped-hour double count; the original figures are preserved in Layer 3.
- **What the retained requirement gives** (out 9, the same model and rows, only the window moved to 100 W; the ledger).
  As drawn: 301.2 / 547.4 Wh, unchanged by the window, because the drawn charge path takes less than the window gives.
  Corrected, NOM: **277.2 / 499.3 Wh**; WE: 286.3 / 516.5 Wh. The first interruption is unchanged, at 05 UTC.
- **The corrected-path headline was optimistic twice over.** The window adds 140.6 Wh at 48 h and 281.1 Wh at 72 h
  (ledger, NOM: 136.6 / 218.2 at 200 W against 277.2 / 499.3 at 100 W); the double count hid another 34.4 / 52.5 Wh at
  200 W. Even the 100 W figures rest on the non-compliant trace, so a compliant panel's own trace is still owed.
- **DR-01 stands**, re-quantified here: A2 needs +278.8 / +515.8 Wh more (WE) where Layer 3 read +79.6 / +116.2 Wh (the
  least additions do not depend on the double count), and +610.8 / +1167.3 Wh at O-2's conservative lower corner.
