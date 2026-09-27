# A05 adjudication: operating modes and the runtime basis (MESHSAT-1357)

**Status: PROVISIONAL (owner condition 2).** Written 25 September 2026 by adjudicator A05. Nothing in the kit has been
built or powered; every watt below is a datasheet figure, a generator declaration or a placeholder, and every hour is
arithmetic over those. No number here is a requirement.

Inputs read (main at `82dd1e4d`; W1 and W2 worktrees at the same base, untracked drafts):

| input | identity |
|---|---|
| `v2/docs/V2-SPEC.md` | main `82dd1e4d`, last changed `249481f1` |
| `v2/docs/MESHSAT-709-geometry-appendix.md` 32.49, 32.50, 32.52, 32.53, 32.62 | main `82dd1e4d` |
| `v2/docs/OPERATING-ENVELOPE.md`, `PANEL.md`, `TEST-PLAN.md` | main `82dd1e4d` |
| `v2/ecad/tools/gen_sch_a.py`, `gen_sch_b.py` | main `82dd1e4d` |
| Samsung INR18650-35E spec Ver. 1.1 (`v2/vendor/battery/samsung-35e-orbtronic.pdf`) | sha256 `5ec577b9...29dc516` |
| W1 `wt/w1/v2/docs/CONOPS.md` | sha256 `45829e74...` |
| W2 `wt/w2/drafts/w2-power.md`, `w2-runtime.md` | sha256 `63fd3103...`, `6c2d62c6...` |
| this adjudication's model | `model_a05.py` (sha256 `4b4fe69a...`), output `a05_results.json` (`c9622532...`), `a05_results.txt` |

## 1. Verdict

1. **The two mode sets describe different things.** W1's table (CONOPS.md:130-145) holds **14** operating modes
   (Transport to Service; the "13" in the question is one short), which are states of use. W2's M0 to M6
   (w2-power.md:143-153) are power states for a budget. W1's own simultaneity cases S1 to S5 (CONOPS.md:175-181)
   are the equivalent of W2's modes, not W1's 14 modes. The M-labels collide (W1 missions M1 to M5, W2 modes M1 to
   M6), so the adopted table renames W2's states **PS-...**; W1 keeps the final IDs (w2-power.md:253).
2. **32.52 item 3's 50 W and 200 W are battery-side** (VERIFIED arithmetic, appendix:2846): the listed loads sum to
   45.0 W and 178 W, and a 12 % allowance gives 50.4 W and 199 W (dividing by 0.88 gives 51.1 W and 202 W, which
   also rounds to "about"; either way the allowance is in the total). **The 290 W is not**: 199 + 90 = 289, so the
   90 W of outlets was added after the allowance (178 + 90 = 268; x 1.12 = 300). CONOPS.md:188-189 and :177 must
   stop calling this "not established".
3. **V2-SPEC.md:23's 29 W has two readings, and both beat W2's headline comparison.** Its number is appendix 32.49
   (:2775, "typical 29 W with the monitor on and radios idle; 20 W dimmed; 150 W with everything transmitting"),
   ruled for a **one-CM5** device set (32.49 item 1, :2757) before the three-module cluster of 32.50 item 15
   (:2800, "about 25 W more typical draw ... one BB-2590 from 8 to 9 hours to 5 to 6"). Its words, read on today's
   three-module kit, describe a not-busy kit: modules idle, monitor on, radios idle, APRS beacons. So:
   - the 8 to 9.5 h is compared against **PS-IDLE**, not PS-TYP. The challenger is right on this point and W2's
     headline (w2-runtime.md:83-85, M2 against 8 to 9.5 h) is withdrawn;
   - but W2's M1 is not "the same mode" as V2-SPEC's 29 W. The wattages match (29.4 W), the definitions do not:
     M1 has the monitor dimmed and sends no beacons. On V2-SPEC's own words the state is about **32.4 W**
     (monitor at 6 W, plus a 0.9 W beacon average placeholder), giving 4.2 h (4S3P) or 5.6 h (4S4P) new at +20 C;
   - V2-SPEC's "5 to 6 h with the three-CM5 cluster busy" is 32.52's typical (appendix:2846, "One BB-2590 gives 5
     to 6 hours typical") and maps to **PS-TYP** (W2 M2).
   - The record's own runtimes divide nominal pack energy by the battery-side figure with no derating: 50 W x 5 to
     6 h = 250 to 300 Wh, the BB-2590's 250 to 300 Wh (:2771); 29 W x 8 to 9.5 h = 232 to 276 Wh. The "bare"
     column of the model is the like-for-like check against them.
4. **W2's arithmetic reproduces exactly.** An independent re-implementation of W2's section 5 table and assumptions
   A1 to A10 (`model_a05.py`, built from the markdown table, not W2's scratch script) returns 29.4, 60.1, 19.7,
   52.5, 227.0 and 316.4 W and the same hours to 0.1 h.
5. **Two W2 state definitions do not match the design:**
   - **EMCON** (W2 M4, 52.5 W) keeps the LimeSDR, the QMX, the LoRa module, the RockBLOCK and the E72 radios
     powered. The generators gate all five in hardware: `gen_sch_b.py:725-728` (LIME_EN, RB_EN, E22_EN, E72_EN =
     EMCON_HW AND software) and `gen_sch_a.py:536` (HF_EN = EMCON_HW AND HF_SW_EN). As generated, EMCON is
     **47.6 W**. The 52.5 W is the "keep listening" option of W1 D-05, and it needs a design change.
   - **Reduced** has two source definitions: one module (OPERATING-ENVELOPE.md:100) against "monitor off, cluster
     idle" (32.53, appendix:2860). They are 19.7 W and 25.4 W. Nothing senses the lid (W1-F04), so the trigger is
     also open.
6. **+20 C is inside the cell's standard test condition.** The spec's condition is "23+-3 C" (section 6.1,
   extracted text line 137), so the 3,350 mAh minimum applies to a cell at +20 C. At +20 C ambient the cells of a
   running kit sit at about +30 to +36 C (W2 A7), where spec 7.5 gives 97 % at 1C, the same as at 23 C. On either
   reading the temperature factor is 1.00, and W2's "23 C" columns are the +20 C columns unchanged.
7. **CONOPS M1's "24 hours or more" has no source.** A search of V2-SPEC.md, OPERATING-ENVELOPE.md and the appendix
   for "24 h", "24 hours" and "day and night" finds no mission duration. The appendix hits are other things: a
   charger timer setting (:2320), a 24 h fog look in the seal bench check (:2493) and error counts (:571, :2521).
   TEST-PLAN's 24 h figures are storage soaks. The body of M1 already says TBD. The corrected title and text are in
   section 5. D-06 carries the same number (w1-decisions.md:212) and is corrected with it.

## 2. The adopted table: power states, their mapping, battery-side power and runtime at +20 C

All figures are PROVISIONAL. Battery W includes W2's per-path conversion floors and 20 mOhm of distribution I2R at
14.4 V. **S / D / T** split the battery watts by basis:
- **S**: a datasheet figure of the picked part, at a defined state.
- **D**: a generator declaration taken as the load (INFERRED).
- **T**: no document for the part, a 32.52 placeholder or a duty assumption. This share is **TBD**.

Runtime = usable energy / battery W.
- Cells: INR18650-35E, C_min 3.35 Ah (spec 3.1 and 7.2), rate factor from spec 7.8.
- Average voltage: 3.60 V minus I x 0.05 Ohm (INFERRED).
- Reserve: 5 % (INFERRED).
- Temperature factor 1.00 at +20 C.
- **BOL** is the spec minimum capacity new. **EOL80** is 80 % of it, an assumption that needs a requirement: the
  spec guarantees only 60 % after 500 cycles (7.9).

| ID (proposed) | definition | W2 | W1 S-case | W1 operating modes (CONOPS.md:132-145) | W1 missions | battery W | S / D / T W | 4S3P BOL h | 4S3P EOL80 h | 4S4P BOL h | 4S4P EOL80 h |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PS-OFF | pack connected, MAIN off: board E always-on, gauge, P clamp leak | M0 | none | Deploy; Shutdown (after); Transport if unpowered; Storage if the pack stays in | M2 (unpowered transit) | 0.37 to 1.87 (E always-on TBD) | not split | 3.1 to 15.5 days | 2.4 to 12.4 days | 4.1 to 20.6 days | 3.3 to 16.5 days |
| PS-IDLE | three CM5 idle (0.4 A), monitor dimmed (4 W placeholder; PANEL.md NIGHT is 20 % backlight, power TBD), radios receiving, SDR off, no transmit | M1 | S1 by definition (its "about 50 W" is 32.52's typical, see PS-TYP) | Normal (full), quiet periods | M1 night; M3 standby | **29.4** | 9.9 / 7.3 / 12.2 | 4.6 | 3.7 | 6.2 | 5.0 |
| PS-IDLE-SPEC | PS-IDLE as V2-SPEC.md:23 words it: monitor on (6 W), APRS beacons (0.9 W average, interval TBD) | M1 + 2 W + beacons | none | Normal (full) | M1 | **32.4** | 9.9 / 7.3 / 15.2 | 4.2 | 3.4 | 5.6 | 4.5 |
| PS-TYP | three CM5 at typical operation (0.9 A), monitor on, radios receiving with light traffic, SDR on, HF receiving; 32.52's "typical" re-derived | M2 | none (add one) | Normal (full) | M1 day; M3 linked | **60.1** | 20.8 / 9.2 / 29.7 | 2.2 | 1.8 | 3.0 | 2.4 |
| PS-BUSY | three modules loaded, 5G and WiFi link passing traffic, Iridium and LoRa sending | none | S2 | Normal (full) | M1, M3 | **TBD** (needs duty cycles; W2 has no state) | TBD | TBD | TBD | TBD | TBD |
| PS-RED | reduced, envelope definition: one module, monitor off, the other two slots and their cards off | M3 | S5 (its "about 30 W" is 32.53's lid-open, monitor-on one-module figure, not reduced) | Reduced (envelope); Degraded down to one module | M2 (lid closed); M5 (above +35 C) | **19.7** | 6.4 / 7.3 / 6.1 | 6.9 | 5.5 | 9.2 | 7.4 |
| PS-RED-b | reduced, 32.53 definition: cluster idle (three modules idle), monitor off | M1 with monitor 0 | S5 (alternative) | Reduced (32.53); Transport if powered (32.53: "the closed-lid transport mode is the reduced mode") | M2, M5 | **25.4** | 9.9 / 7.3 / 8.2 | 5.4 | 4.3 | 7.2 | 5.7 |
| PS-EMCON | EMCON as generated: PS-TYP with PA, HF, LimeSDR, RockBLOCK, LoRa, E72 rails gated off, 5G RF-off, cards idle behind W_DISABLE | M4 less gated loads | none | EMCON | M4 | **47.6** | 19.7 / 8.7 / 19.0 | 2.8 | 2.3 | 3.8 | 3.0 |
| PS-EMCON-L | EMCON "keep listening" (W1 D-05 option; needs a design change to the gates) | M4 as drafted | none | EMCON if D-05 so rules | M4 | **52.5** | 20.9 / 9.0 / 22.3 | 2.6 | 2.0 | 3.4 | 2.7 |
| PS-ALLTX | every transmitter keyed at once: three CM5 at declared stress, both cards and 5G at maximum, LoRa 1 W, RockBLOCK, QMX, 30 W PA, SDR, monitor full, fans; outlets off | M5 | S3 (W1 has outlets at minimum; W2 off) | Normal (full), key-down bursts | M1 (APRS key-down) | **227.0** | 110.4 / 43.5 / 68.2 | 0.5 (energy only) | 0.4 | 0.7 | 0.6 |
| PS-ALLTX-OUT | PS-ALLTX plus PoE 0.6 A at 54 V and USB-C PD 45 W | M6 | none | Normal (full) | M1 (lid tablet on the outlet) | **316.4** | 110.4 / 128.2 / 68.2 | 0.4 (protection trips first, F-PR-03) | 0.3 | 0.5 | 0.4 |

**Overlays.** These change a share of a state above rather than forming states of their own. None has a computed
number.

| overlay | W1 mode | effect on the table | status |
|---|---|---|---|
| Heater (cold) | Charging below 0 C, cold operation | +10.8 W at the battery (7.5 W at 12 V scaled to 14.4 V, W2 F-PR-06): PS-TYP 71.0 W, PS-RED 30.6 W. It never runs at +20 C, so it has no runtime here; W2 section 5 has the cold figures, and its 0.41 cold factor is a lower bound | PROVISIONAL |
| NIGHT, NVG | NVG | backlight 20 % or 5 % (PANEL.md:137-138); the monitor's power at partial backlight is in no document | TBD; the monitor row is at most 10 W (Xenarc manual v2, extracted text line 121, "Power Consumption: <= 10W") |
| Blackout | Blackout | backlight off, touch UI dark, LED rail open (PANEL.md:139): removes most of the monitor share | TBD |
| Charging | Charging | pack current reverses while the source covers the load (W2 section 7); a 12 V vehicle does not cover PS-TYP (W2 w2-power.md:239) | not adjudicated here |
| Transients | Startup, Shutdown, ZEROIZE | inrush and sequencing are W2 section 6 and rule PWR-002; not runtime states | TBD |
| Degraded | Degraded | between PS-RED and the pre-fault state, depending on what is lost | not computed |
| none | Service | bench supply; not a runtime state | n/a |

**How the legacy figures map to the table:**

| figure | source | what it describes | maps to | today's number (PROVISIONAL) |
|---|---|---|---|---|
| 29 W typical, 8 to 9.5 h | V2-SPEC.md:23 from appendix:2775 (32.49) | one-CM5 set, monitor on, radios idle; V2-SPEC adds "APRS beacons" | by words PS-IDLE-SPEC; by wattage alone PS-IDLE | 32.4 W: 4.2 / 5.6 h new |
| 20 W dimmed, 11 to 13.5 h | V2-SPEC.md:23, appendix:2775 | one-CM5 set, monitor dimmed | no three-module counterpart; nearest by words PS-IDLE | 29.4 W: 4.6 / 6.2 h new |
| 5 to 6 h, cluster busy | V2-SPEC.md:23, appendix:2800, :2846 | 32.52 typical with a BB-2590 | PS-TYP | 60.1 W: 2.2 / 3.0 h new |
| 150 W peak | V2-SPEC.md:23, appendix:2775 | one-CM5 set, everything transmitting | superseded by 32.52; PS-ALLTX | 227.0 W |
| about 50 W typical | appendix:2846 (32.52 item 3) | three CM5 at 6 W each, monitor 6 W, one WiFi card, 5G, SDR at 3 W each; battery-side with 12 % | PS-TYP | 60.1 W (W2: loads added after 7 Sep and cascaded paths at 16 to 23 %) |
| about 200 W peak | appendix:2846 | battery-side with 12 % | PS-ALLTX | 227.0 W |
| up to 290 W | appendix:2846 | 199 W plus 90 W outlets **without** the allowance | PS-ALLTX-OUT | 316.4 W |
| one CM5 about 30 W, three loaded about 50 W | appendix:2860 (32.53 thermal basis) | lid open, monitor on, radios idle | 30 W: the 32.49 one-module figure, **not** reduced; 50 W: PS-TYP | see rows |
| S1 "about 50 W" | CONOPS.md:177 | three idle modules, monitor on | PS-IDLE (definition); the 50 W is PS-TYP's | 29.4 to 32.4 W |
| S3 "about 200 W" | CONOPS.md:179 | every transmitter keyed, outlets at minimum | PS-ALLTX (outlets off); the outlets' minimum contract is TBD | 227.0 W plus the outlets' minimum |
| S5 "about 30 W" | CONOPS.md:181 | one module, monitor off | PS-RED or PS-RED-b | 19.7 or 25.4 W |
| "about 4 h" | CONOPS.md:186-187, plan section 1 | 200 Wh / 50 W | withdrawn: 200 Wh is 4S4P only (193.0 Wh at C_min, W2 section 3), and 50 W is PS-TYP | PS-TYP 4S4P: 3.0 h new, 2.4 h at EOL80 |

## 3. What the table rests on, and what it does not

- **Load figures spot-checked against the filed datasheets** (text extracted under `txt/`; sha256 prefixes in the
  model docstring's sense):

  | part | spec text | where |
  |---|---|---|
  | CM5 | idle 400 mA, operation 900 mA typical | cm5-datasheet Table 9, extracted lines 1494-1510 |
  | Xenarc 709GNK | "Power Consumption: <= 10W" | product manual v2, line 121 |
  | RockBLOCK 9704 | "60mW Idle, 1.4W Max" | datasheet, line 96 |
  | E22-900M30S | TX 650 mA, RX 14 mA | manual v1.20, lines 97-98 |
  | SA868 | RX 60 mA | v1.3, line 94 |
  | QMX | receive "as low as 80mA" | manual 1_04_004, line 101 |
  | RM520N-GL | idle 60 mA, RF-disabled 4.7 mA, LTE CA 1,512 mA | HD v1.1 Table 43, lines 4027-4066 |
  | PI7C9X2G404SL | 624.28 / 1,066.65 mW | line 5865 |
  | LG290P | 99 mA, 326.7 mW | HD v1.1, lines 561-567 |
  | TUSB8041 | 4 SS in U0: 49 mA at 3.3 V plus 778 mA at 1.1 V, about 1.0 W; 2 SS in U1/U2 about 0.5 W | SLLSEE4E 7.7, lines 744-766 |

  W2's 0.1 W per idle hub lies between the Suspend and HS-only rows, so it is tiered T.
- **The T share is large:** 12.2 of 29.4 W in PS-IDLE and 29.7 of 60.1 W in PS-TYP rest on parts with no power
  document or on duty assumptions. These are the AW7915 cards, the LimeSDR, the NVMe drives (no part), the slot and
  mixer fans, the KSZ9897R (datasheet filed, not read), the camera, the monitor below full brightness, and the 5G,
  LoRa and RockBLOCK duties in PS-TYP.
- **4S4P may not exist physically.** W4 reports that no 4S4P 18650 block fits either pocket, and that 4S3P sits
  between 0.5 mm clear and 0.6 mm interference under board B (digest XC "Pack size against geometry"). The 4S4P
  columns are arithmetic for a configuration whose fit is unproven.
- **PS-ALLTX and PS-ALLTX-OUT are energy arithmetic only.** Delivery is bound first by the gauge's 20 A / 2 s and
  the 25 A blades at low charge (W2 F-PR-03, w2-power.md:208-210).
- **Not modelled:** DC resistance growth at end of life, cell imbalance, gauge error beyond the 5 % reserve, and the
  21700 option (its sheet is not held).

## 4. Reproduction

`python3 model_a05.py a05_results.json` (stdlib only, runner-safe, under a second). The load values and tiers are
in the `L` table of the script, with one line per W2 row, and the tiers are this adjudicator's own. The
`check_32_52` block in `a05_results.json` holds the 32.52 and BB-2590 arithmetic of verdict items 2 and 3. W2's
scratch script (`wt/w2/drafts/_scratch/budget.py`) was run read-only for comparison and agrees to 0.1 W and 0.1 h.
No box was used.

## 5. Corrections for the integrator

The files named below are W1's and W2's drafts. This adjudication edits neither.

**W1, `v2/docs/CONOPS.md`:**
1. Line 57: `### M1. Remote site relay, 24 hours or more` becomes
   `### M1. Remote site relay on pack and solar (duration TBD)`.
2. Lines 67-69, the "must hold" clause: "the kit runs through a day and night cycle on its pack plus solar
   (NEED-05, duration **TBD** ...)" becomes:

   > the kit keeps running on its pack plus solar for the mission's duration (NEED-05). The duration is **TBD**: no
   > source in the tree states one, and the battery-only runtime per power state is PROVISIONAL (PS-TYP 2.2 h for
   > 4S3P or 3.0 h for 4S4P new at +20 C, adjudication A05). The solar yield is not in the record.

   The day and night narrative of the sequence may stay, because it describes use and sets no duration.
3. Line 177 (S1): replace "about 50 W" and its source cell. The new text is "PS-IDLE: 29.4 W at the battery (monitor
   dimmed), 32.4 W with the monitor on and beacons, PROVISIONAL". It adds the note "the 50 W of 32.52 item 3 is the
   typical state PS-TYP (60.1 W re-derived); the 29 W of V2-SPEC.md:23 is 32.49's one-module figure". Add a PS-TYP
   row between S1 and S2.
4. Line 179 (S3): "about 200 W" becomes "PS-ALLTX 227.0 W at the battery with the outlets off; the outlets' minimum
   contract is TBD".
5. Line 181 (S5): "about 30 W with one module (32.53 line 2860)" becomes "19.7 W (one module, envelope) or 25.4 W
   (cluster idle, 32.53); the definition is open". 32.53's 30 W is the lid-open, monitor-on figure.
6. Lines 185-191 (section 6): delete "whether the 50 W is at the battery or summed at the loads is not established"
   and state verdict item 2. Replace "about 4 hours" with the section 2 table.
7. Line 139 (EMCON row): add "battery-side about 47.6 W as generated (PS-EMCON), PROVISIONAL". The "keep listening"
   variant (52.5 W) exists only if D-05 rules so and the gates change.
8. Line 136 (Reduced row): name both power figures (19.7 and 25.4 W) beside the two definitions.
9. The mode table has 14 rows. Any count quoted elsewhere ("13 modes") is corrected to 14.

**W1, `drafts/w1-decisions.md`:**
1. Line 212: "M1's 24 h cycle as a separate energy-balance requirement with solar" becomes "M1's pack-plus-solar
   energy balance over a mission duration the owner sets (TBD), as a separate requirement".
2. Line 211: "mode S1" becomes a named PS state. Recommend that the owner sees PS-IDLE-SPEC (the V2-SPEC-worded
   state) and PS-TYP side by side, each at BOL and EOL80.

**W2, `drafts/w2-runtime.md` and `drafts/w2-power.md`:**
1. w2-runtime.md:83-85, the headline: compare like with like. V2-SPEC's 8 to 9.5 h at 29 W is set against PS-IDLE:
   29.4 W gives 4.6 h (4S3P) and 6.2 h (4S4P) new, and on V2-SPEC's own words 32.4 W gives 4.2 h and 5.6 h. V2-SPEC's
   5 to 6 h with the cluster busy is set against PS-TYP: 2.2 h and 3.0 h. Both published figures remain unsupported.
2. w2-power.md:151 and the M4 column: EMCON as generated gates LimeSDR, RockBLOCK, LoRa, E72 (`gen_sch_b.py:725-728`)
   and HF (`gen_sch_a.py:536`). This gives 47.6 W, not 52.5 W. Keep 52.5 W only as the labelled D-05
   "keep listening" variant.
3. w2-power.md:150 (M3): name the second definition (32.53, cluster idle, 25.4 W).
4. Rename M0 to M6 to the PS-IDs, or to W1's final IDs, everywhere: w2-power.md section 4 and 5, w2-runtime.md
   sections 4, 5 and 7, and the findings.
5. w2-runtime.md:64-68, the column headings: "23 C new" becomes "+20 C BOL (spec 6.1: standard condition 23+-3 C;
   cells at +20 C ambient run warmer)". The values are unchanged.
6. w2-runtime.md:160-166, the owner candidate: restate it on PS-IDLE-SPEC and PS-TYP at EOL80, and carry W4's
   pocket finding against option (b).

## 6. Remaining unknowns (each moves the table)

| unknown | effect |
|---|---|
| Duty cycles: beacon interval, 5G and WiFi traffic, SDR use, HF transfers | PS-BUSY does not exist; PS-TYP's T share; the beacon placeholder in PS-IDLE-SPEC |
| Power of the AW7915-AED, LimeSDR Mini 2.4, NVMe (no part), fans, camera, Geiger, KSZ9897R (datasheet filed, not read), and the Xenarc at 20 %, 5 % and 0 % backlight | T share: 12.2 W of PS-IDLE, 29.7 W of PS-TYP |
| End-of-life definition: 80 % is an assumption; the spec guarantees 60 % after 500 cycles | the EOL columns; at 60 % every BOL figure scales by 0.6 |
| Reserve (5 %), DC resistance (0.05 Ohm), average voltage | a few percent on every hour |
| Reduced mode: which definition, and what senses the lid | PS-RED 19.7 W against PS-RED-b 25.4 W |
| EMCON meaning (D-05) | PS-EMCON 47.6 W against PS-EMCON-L 52.5 W |
| Whether a 4S4P block fits (W4) | whether the 4S4P columns describe a buildable kit |
| The outlets' minimum contract while the PA keys | S3's figure above PS-ALLTX |
| Whether the kit is powered in transport | PS-OFF against PS-RED during M2 |
| Board E's always-on draw (0.2 to 1.7 W) | PS-OFF shelf time: 3.1 to 20.6 days from full |
