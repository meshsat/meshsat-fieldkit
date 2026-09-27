# W2 runtime draft: 4S3P against 4S4P (MESHSAT-1357, round 2)

**Status: PROVISIONAL.** Owner condition 2: the runtime stays provisional until it is computed per configuration (done
here) **and** W1's power states, duty cycles and the pack decision are fixed (not done). Nothing has been built; every
figure is a model over datasheet numbers, declarations and named assumptions. Do not quote a number from this page
without its power state, temperature and age.

Round 2 of 25 September 2026, worktree `fnd/w2` at `82dd1e4d`. Power states and loads: `w2-power.md` sections 4 and 5,
which adopt adjudication A05's table (`scratchpad/adj/A05-modes-and-runtime-basis/`). Model:
`drafts/_scratch/budget_r2.py` (scratch, stdlib, under a second), which reproduces A05's independent model to 0.01 W and
0.01 h. Circuit defects that change what the pack can deliver: `w2-findings.md`.

## 1. The published figures, compared like with like

**32.52's 50 W and 200 W are battery-side** (appendix:2846). The listed loads sum to 45.0 W typical (18 + 6 + 3 + 3 +
3 + 0.5 + 0.5 + 1 + 1.5 + 6 + 2.5) and 178 W peak (36 + 10 + 10 + 10 + 3 + 6.5 + 5 + 12 + 75 + 8 + 2.5); a flat 12 %
gives 50.4 W and 199 W, the stated "about 50 W" and "about 200 W". **The 290 W is not**: 199 + 90 = 289, so the 90 W of
outlets was added after the allowance (A05). None of the three is a measurement or a per-rail calculation.

**V2-SPEC.md:23's figures come from 32.49 (appendix:2775), ruled for a one-CM5 device set** before the three-module
cluster of 32.50 item 15 (appendix:2800, "about 25 W more typical draw ... one BB-2590 from 8 to 9 hours to 5 to 6").
Round 1's headline set the 8 to 9.5 h against PS-TYP (60 W); that compared different states and is **withdrawn**. The
like-for-like table, at +20 C (inside the cell sheet's standard condition of 23 +- 3 C, section 6.1, so the temperature
factor is 1.00):

| published figure | source | today's counterpart (A05) | battery W | 4S3P new / EOL80 | 4S4P new / EOL80 |
|---|---|---|---|---|---|
| 8 to 9.5 h "typical (29 W: monitor on, radios idle, APRS beacons)" | V2-SPEC.md:23, 32.49 | **PS-IDLE-SPEC** (its words) | 32.4 | **4.2 / 3.4 h** | **5.6 / 4.5 h** |
| (same, by wattage alone) | | PS-IDLE (monitor dimmed, no beacons) | 29.4 | 4.6 / 3.7 h | 6.2 / 5.0 h |
| 5 to 6 h "with the three-CM5 cluster busy" | V2-SPEC.md:23, appendix:2800, 2846 | **PS-TYP** | 60.1 | **2.2 / 1.8 h** | **3.0 / 2.4 h** |
| 11 to 13.5 h "dimmed" (20 W) | V2-SPEC.md:23, 32.49 | no three-module counterpart; nearest by words PS-IDLE | 29.4 | 4.6 / 3.7 h | 6.2 / 5.0 h |
| peak "about 150 W with everything transmitting" | V2-SPEC.md:23, 32.49 | superseded by 32.52; PS-ALLTX | 227.0 | 0.5 / 0.4 h (energy only) | 0.7 / 0.6 h |
| "about 4 h" | plan section 1, CONOPS.md:186-187 (200 Wh / 50 W) | withdrawn: 200 Wh is 4S4P only and 50 W is PS-TYP | 60.1 | 2.2 / 1.8 h | 3.0 / 2.4 h |

**Reading:** on V2-SPEC's own words, typical use gives **4.2 h (4S3P) or 5.6 h (4S4P) on a new pack at +20 C, 3.4 h or
4.5 h at 80 % end of life**, against the published 8 to 9.5 h; the busy cluster gives 2.2 h or 3.0 h against 5 to 6 h.
Neither pack supports either published figure. Two cross-checks: the record's own runtimes divide the BB-2590's nominal
250 to 300 Wh by a battery-side power with no derating (50 W x 5 to 6 h = 250 to 300 Wh; 29 W x 8 to 9.5 h = 232 to
276 Wh), and the "bare" figure here (nominal energy over battery W, no rate, sag, reserve or age) is 4.5 h and 6.0 h for
PS-IDLE-SPEC: the gap is the pack (145 or 193 Wh against 250 to 300), not the model's deratings. And 12.2 of PS-IDLE's
29.4 W and 29.7 of PS-TYP's 60.1 W rest on TBD loads (w2-power.md section 5), so both rows can move several watts
either way.

## 2. The model and every assumption in it

Runtime = usable energy / battery-side power, with
usable energy = N_cells x C_min x f_rate(I_cell) x V_avg(I_cell) x f_T x f_age x (1 - reserve).

| # | assumption | value | basis | status |
|---|---|---|---|---|
| A1 | cell capacity | C_min = 3.35 Ah (standard, 0.2C, 2.65 V cut-off, 23 C) | samsung-35e-orbtronic.pdf Ver. 1.1, 3.1 and 7.2 | VERIFIED; the typical 3.45 Ah (samsung-35e-conrad.pdf) would add 3 % |
| A2 | rate factor | 100 % at 0.68 A, 97 % at 3.4 A, 95 % at 6.8 A, 92 % at 8 A per cell, linear between | 7.8 | VERIFIED points, INFERRED interpolation |
| A3 | average discharge voltage | 3.60 V minus I_cell x 0.05 Ohm | 3.60 V nominal (3.3); 0.05 Ohm DC INFERRED from the 35 mOhm AC maximum (7.4) | INFERRED |
| A4 | end of discharge | the cell's 2.65 V cut-off (3.9); the gauge's 2.50 V trip adds under 2 %, not counted | 3.9; pcb_pack_protection.yaml | VERIFIED |
| A5 | shutdown reserve | 5 % | assumption, to be set by W5 | INFERRED |
| A6 | temperature factor | **1.00 at +20 C** (inside the 23 +- 3 C standard condition, 6.1; cells of a running kit sit warmer, and 7.5 gives 97 % at both 23 C and 40 C). **Cold: TBD between 0.41 and 1.00** wherever the cell temperature is unknown; 0.41 is the sheet's only cold point (40 % at -10 C against 97 % at 23 C, 1C discharge), and there is no point between -10 C and 23 C. Below a -10 C cell surface the gauge opens discharge: no runtime from the pack at all (F-PK-01) | 6.1, 7.5; pcb_pack_protection.yaml | VERIFIED points; the cold factor is a bracket, not an estimate |
| A7 | cell temperature | inside air = ambient + 10 K (one module) or + 16 K (three), plus self-heating: at -20 C ambient about -10 C (one module) to -4 C (three) | OPERATING-ENVELOPE.md section 3, appendix 32.53; TEST-PLAN E3 measures it | INFERRED |
| A8 | ageing | end of life at 80 % of initial capacity (design point, needs a requirement); the sheet's own floor is 60 % after 500 cycles | 7.9: "Capacity >= 2,010mAh (60% of Standard Capacity)" | 80 % ASSUMPTION; 60 % VERIFIED |
| A9 | conversion | per rail, the generators' datasheet floors (LM5176 0.93, AP64500 0.90, TPS62933 0.88, 3.3 V and 1.x V bucks 0.88 / 0.85, LDO Vout/Vin), cascaded where the tree cascades | gen_sch_a.py:45-62, gen_sch_b.py:50-63, gen_sch_e.py:21-31 | VERIFIED as declarations; floors, not measurements |
| A10 | distribution loss | 20 mOhm from cells to VBAT, I2R | blades, FETs and shunt VERIFIED; about 9 mOhm of lead, contacts and copper INFERRED | mixed |
| A11 | loads and states | w2-power.md sections 4 and 5 (A05's PS table) | W1 owns duty cycles | PROVISIONAL |
| A12 | pack balance and gauge | cells matched, the gauge's capacity equals A1 to A8 | no pack built | INFERRED |

## 3. Energy per configuration

| configuration | cells | energy at C_min x 3.6 V | at the typical capacity | cells-only mass | cell sheet held |
|---|---|---|---|---|---|
| 4S3P INR18650-35E | 12 | **144.7 Wh** | 149.0 Wh (3.45 Ah) | 600 g max | yes |
| 4S4P INR18650-35E | 16 | **193.0 Wh** | 198.7 Wh | 800 g max | yes |
| 4S3P 21700 at 5 Ah (appendix 32.62, appendix:3062; V2-SPEC.md:20) | 12 | 216 Wh (nominal, TBD) | TBD | TBD | **no** (TBD) |

"About 200 Wh" (gen_sch_p.py:7, V2-SPEC.md:20, pcb_pack_protection.yaml:24) is 4S4P of the 18650 cell. 32.62's 216 Wh
4S3P is the 21700 option; `pcb_energy_chain.yaml` now says so (sourced correction in this worktree).

## 4. Runtime per power state (hours), PROVISIONAL

Battery-side power from w2-power.md section 5. "+20 C" is the cell sheet's standard condition (A6). "Cold" is -20 C
ambient with the kit running, heater off: a **bracket**, factor 0.41 to 1.00 (A6), and zero if the cell surface falls
below -10 C.

| state | battery W | config | cell A | +20 C new | +20 C EOL80 | +20 C at 60 % (500 cycles) | cold new (TBD bracket) | cold EOL80 (TBD bracket) |
|---|---|---|---|---|---|---|---|---|
| PS-IDLE | 29.4 | 4S3P | 0.68 | 4.6 | 3.7 | 2.8 | 1.9 to 4.6 | 1.5 to 3.7 |
| | | 4S4P | 0.51 | 6.2 | 5.0 | 3.7 | 2.5 to 6.2 | 2.0 to 5.0 |
| PS-IDLE-SPEC | 32.4 | 4S3P | 0.75 | **4.2** | **3.4** | 2.5 | 1.7 to 4.2 | 1.4 to 3.4 |
| | | 4S4P | 0.56 | **5.6** | **4.5** | 3.4 | 2.3 to 5.6 | 1.8 to 4.5 |
| PS-TYP | 60.1 | 4S3P | 1.39 | **2.2** | **1.8** | 1.3 | 0.9 to 2.2 | 0.7 to 1.8 |
| | | 4S4P | 1.04 | **3.0** | **2.4** | 1.8 | 1.2 to 3.0 | 1.0 to 2.4 |
| PS-RED (one module) | 19.7 | 4S3P | 0.46 | 6.9 | 5.5 | 4.2 | 2.8 to 6.9 | 2.3 to 5.5 |
| | | 4S4P | 0.34 | 9.2 | 7.4 | 5.5 | 3.8 to 9.2 | 3.0 to 7.4 |
| PS-RED-b (cluster idle) | 25.4 | 4S3P | 0.59 | 5.4 | 4.3 | 3.2 | 2.2 to 5.4 | 1.8 to 4.3 |
| | | 4S4P | 0.44 | 7.2 | 5.7 | 4.3 | 2.9 to 7.2 | 2.4 to 5.7 |
| PS-EMCON (as generated) | 47.6 | 4S3P | 1.10 | 2.8 | 2.3 | 1.7 | 1.2 to 2.8 | 0.9 to 2.3 |
| | | 4S4P | 0.83 | 3.8 | 3.0 | 2.3 | 1.6 to 3.8 | 1.3 to 3.0 |
| PS-EMCON-L (D-05 variant) | 52.5 | 4S3P | 1.22 | 2.6 | 2.0 | 1.5 | 1.0 to 2.6 | 0.8 to 2.0 |
| | | 4S4P | 0.91 | 3.4 | 2.7 | 2.1 | 1.4 to 3.4 | 1.1 to 2.7 |
| PS-ALLTX (energy only) | 227.0 | 4S3P | 5.25 | 0.5 | 0.4 | 0.3 | 0.2 to 0.5 | 0.2 to 0.4 |
| | | 4S4P | 3.94 | 0.7 | 0.6 | 0.4 | 0.3 to 0.7 | 0.2 to 0.6 |
| PS-ALLTX-OUT (protection trips first, F-PR-03) | 316.4 | 4S3P | 7.33 | 0.4 | 0.3 | 0.2 | 0.2 to 0.4 | 0.1 to 0.3 |
| | | 4S4P | 5.49 | 0.5 | 0.4 | 0.3 | 0.2 to 0.5 | 0.2 to 0.4 |
| PS-BUSY | TBD | both | | TBD (needs duty cycles) | | | | |

Reading the table:
- PS-IDLE-SPEC and PS-TYP are the two rows to set a requirement against (section 10), each at end of life.
- The cold columns are not estimates. With one module the cells may sit near -10 C (A7), where 0.41 is the documented
  point at 1C and the gauge's limit is at hand; with three modules they may sit near -4 C, where no document gives a
  factor. A bench test at 0 C and -10 C at 0.1 to 0.3C, or the maker's full cold-rate curve (not held), replaces the
  bracket.
- Above +35 C ambient the envelope runs the reduced state; the three-module inside air (about +56 C) is 4 K from the
  60 C discharge limit and above the 45 C charge limit (OPERATING-ENVELOPE.md section 3).
- PS-ALLTX rows are energy arithmetic only: whether the pack can deliver them is F-PR-03.

## 5. Cold operation and the heater

| case | battery W | 4S3P new | 4S4P new |
|---|---|---|---|
| PS-TYP + heater (10.8 W at 14.4 V), cells cold | 71.0 | 0.8 to 1.9 h (TBD bracket) | 1.0 to 2.5 h |
| PS-RED + heater, cells cold | 30.6 | 1.8 to 4.5 h | 2.4 to 6.0 h |

Below a -10 C cell surface the gauge opens the discharge FET (pcb_pack_protection.yaml `DISCHARGE_TEMPERATURE_WINDOW`)
and the heater runs from that same pack, so a cold-soaked kit cannot start without shore power (F-PK-01; the envelope's
carve-out at OPERATING-ENVELOPE.md:96-97 covers charge and discharge limits, not the start). The heater's 10.8 W is its
7.5 W / 12 V rating scaled resistively to 14.4 V (F-PR-06), which applies only after F-SQ-06's OVLO fix; as drawn the
heater eFuse is locked out above about 13 V.

## 6. Off and in storage (pack connected)

| drain | basis | 4S3P from full | 4S3P from 30 % | 4S4P from full | 4S4P from 30 % |
|---|---|---|---|---|---|
| 0.17 W | F-BP-01 alone (VERIFIED topology, INFERRED clamp voltage) | 34 days | **10 days** | 45 days | **14 days** |
| 0.37 W | F-BP-01 plus board E always-on at an unsourced 0.2 W floor | 15.5 days | 4.6 days | 20.6 days | 6.2 days |
| 1.87 W | F-BP-01 plus board E at its 1.7 W declaration | 3.1 days | 0.9 days | 4.1 days | 1.2 days |

The envelope declares storage "for up to three months ... at the pack's ex-factory 30 percent charge"
(OPERATING-ENVELOPE.md:103-104) without saying whether the pack is connected. **With the pack connected it does not
hold, on F-BP-01 alone.** It holds with the pack disconnected or in a gauge ship state (F-BP-02).

## 7. Charge time (after F-CH-01; with a host running unless stated)

Constant-current phase to about 80 % (INFERRED share); the constant-voltage tail is TBD (the sheet's standard charge,
0.5C to a 0.02C cut-off, takes 4 h in total, 3.6). Currents from w2-power.md section 7, with the loads on CELL+ as
wired (F-CH-03).

| source and state | pack current | 4S3P to about 80 % | 4S4P to about 80 % |
|---|---|---|---|
| shore, PS-CHG (MAIN on, host running, slots off, 10.7 W) | 4.0 A (design) | 2.0 h | 2.7 h |
| shore, PS-TYP | about 2.4 A | 3.3 h | 4.4 h |
| 12 V vehicle, PS-CHG | about 2.8 A | 2.8 h | 3.8 h |
| 12 V vehicle, PS-TYP | negative (the pack discharges about 0.6 A) | never | never |
| 9 V vehicle, PS-CHG | about 1.9 A | 4.2 h | 5.5 h |
| any input, **MAIN off, no host** (256 mA default less the PS-OFF drain; A02, INFERRED, bench owed) | 0.13 to 0.23 A | 35 to 64 h | 47 to 85 h |

There is no "kit off" full-rate charge: the charger's only host is the panel controller, which needs MAIN (F-CH-02).
Round 1's "shore, kit off, 4.0 A" row assumed a host that does not exist with MAIN off; it is replaced by the PS-CHG
row, which costs 10.7 W.

## 8. How the pack size moves the architecture and the mechanics

| aspect | 4S3P 18650 | 4S4P 18650 | what moves |
|---|---|---|---|
| energy (minimum) | 144.7 Wh | 193.0 Wh | runtime scales with it (section 4) |
| cell mass | 600 g max | 800 g max | +200 g; the mass budget is W4's |
| cell block, 3 wide x 2 high (18.55 x 65.25 mm max cells, 3.11) | 55.7 x 37.1 x 130.5 mm (12 sites) | 55.7 x 37.1 x 195.8 mm (18 sites, 16 used) | pocket length |
| **fit** | 32.62 put a 4S pack in the 58 x 240 x 48 mm east pocket; **W4 reports the 4S pack under board B sits between 0.5 mm clear and 0.6 mm interference, and that pack_4s.py's cells and BMS overlap** (adjudication A06 open) | **W4 reports that no 4S4P 18650 block fits either pocket** (A06 open) | the pack options that physically exist are W4's and A06's to settle before the owner is asked |
| heater mat 50 x 150 mm | covers the 130.5 mm block | covers 150 of 195.8 mm | 4S4P leaves a quarter of the block unheated |
| per-cell current at PS-ALLTX (15.8 A at 14.4 V; 18.9 A at 12 V) | 5.3 to 6.3 A of 8 A | 3.9 to 4.7 A | 4S4P gives peak headroom; the gauge thresholds are set for parallel_min = 3 (pcb_pack_protection.yaml) and would rise for a declared 4S4P |
| charge at the 4 A design current | 0.40C, 1.33 A per cell: above the 1,020 mA cycle-life current (3.5) | 0.30C, 1.0 A per cell: at it | 4S3P ages faster at the same setting, or charges at 3 A |
| pack I2R heat at PS-ALLTX (AC resistance, a lower bound; DC is higher, TBD) | 47 mOhm: 11.6 W | 35 mOhm: 8.7 W | into a sealed pocket beside the heater mat |
| board changes | none on A to E: the node is 4S either way | same | the choice is a board P and mechanical decision |
| a second pack | needs its own gauge and a paralleling scheme; E has one XT60 and one SMBus header (F-CH-04) | n/a | |

## 9. Sensitivities and what fixes the number

- Loads with no document behind them: 12.2 W of PS-IDLE and 29.7 W of PS-TYP (the WiFi cards, LimeSDR, NVMe drives,
  fans, KSZ9897R, camera, the monitor below full brightness, and the 5G, LoRa and RockBLOCK duties). Each W6 datasheet
  narrows a row.
- Duty cycles are the biggest unknown for PS-TYP, PS-EMCON and PS-BUSY (transmit averages, SDR use, display brightness,
  beacon interval): W1.
- The conversion floors are deliberately low; if every converter ran 3 points better, PS-TYP falls from 60.1 to about
  58 W.
- Capacity: +3 % at the typical 3.45 Ah; reserve 5 %; end of life 80 % is an assumption (at 60 % every new-pack figure
  scales by 0.6).
- Temperature: two datasheet points only (section 4).

## 10. Owner decision this feeds (candidate, plan first batch item 2)

**Runtime target and pack size.** Evidence: sections 1, 4, 7 and 8. The requirement is set against named states at end
of life; the pack is then the largest option W4 proves fits.

| option | PS-IDLE-SPEC new / EOL80 | PS-TYP new / EOL80 | fit (W4, A06 open) | other consequences |
|---|---|---|---|---|
| (a) 4S3P 18650, 144.7 Wh | 4.2 / 3.4 h | 2.2 / 1.8 h | 32.62's pocket; W4: 0.5 mm clear to 0.6 mm interference under B | charges above the cycle-life current at 4 A; no peak headroom at low charge |
| (b) 4S4P 18650, 193.0 Wh | 5.6 / 4.5 h | 3.0 / 2.4 h | W4: fits neither pocket | peak headroom; +200 g; not an option until a fit is proven |
| (c) 4S3P 21700, about 216 Wh at 5 Ah | about 1.5 x (a) (INFERRED from nominal energy) | about 1.5 x (a) | TBD | no cell sheet held (W6 to source); protection thresholds re-derived |
| (d) a second pack in the other pocket | about 2 x (a) (TBD, depends on what fits there) | same | TBD | paralleling design, a second gauge link (F-CH-04) |
| (e) meet the target by state | PS-RED 6.9 / 5.5 h (4S3P) | n/a | any | the product states which functions run for how long |

Recommendation: ask the owner for the runtime target as "PS-IDLE-SPEC and PS-TYP at end of life" (hours each), after W4
and A06 say which of (a) to (d) physically exist. If the target exceeds what (a) gives, (c) is the next candidate to
source before (b) is revived. This stays PROVISIONAL until W1's states and duty cycles exist.
