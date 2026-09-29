# GAUGE: the lid pack's gauge under Option A(i) (stream a1elec, MESHSAT-1357)

29 September 2026. **Prototype design, AI review: no gauge is programmed, no pack is built, nothing is measured.**
Every figure below is printed by `gauge_scale.py` (beside this page; output `gauge_scale.out`), which parses TI's
manual itself, or is quoted from a maker's document held under `v2/vendor/` with its section and page.

## 1. The problem, as the outside review put it and as TI's manual prints it

The lid module is 4S12P of the ruled Samsung INR18650-35E. At the specification minimum (3,350 mAh, spec 3.1 and 7.2)
it holds **40,200 mAh and 57,888 cWh** (40.2 Ah x 14.40 V); at the Technical Report's typical 3.45 Ah, 41,400 mAh and
59,616 cWh. TI's BQ4050 technical reference manual, **SLUUAQ3A** (April 2016, revised October 2022,
`v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf`, sha256 `525d16b2...`), types both design-capacity words as I2 with a
maximum of **32,767** (14.13.5.1 and 14.13.5.2, page 180; Table 14-1 rows 0x444d and 0x444f, page 191). Both lid
figures are above it.

The manual's scale field does not resolve it. SpecificationInfo() IPScale reads "Not supported by the gas gauge / MUST
be set to 0, 0, 0, 0" in 13.27 (page 107) and lists working scales of 10E0 to 10E3 in 14.14.1.5 (page 184). A flag
whose own manual contradicts itself is not a basis, and even if it worked it would scale only what the gauge
*reports*, not the data-flash words it *compares against*. **This record does not use IPScale: it is written 0, as
13.27 requires** (the Specification Information word stays TI's 0x0031).

## 2. The options, and the one taken

| option | what it is | against it | verdict |
|---|---|---|---|
| **(a) BQ4050 on board PL with a current-scale calibration of k = 2** | the lid's board is board P as generated; its gauge is calibrated so that its internal unit is 2 mA (section 3) and every word in a current, charge, energy or power unit is written in that unit | rests on the firmware having no hidden current constant (section 6, Q-TI-A1); the host must hold k | **TAKEN** (authority SESSION) |
| (b) split the lid into two 4S6P modules, each under an unmodified board P | no scaling: each gauge carries the base's own words (20,100 mAh, 28,944 cWh, section 8a of the energy record) | two lid packs in parallel behind one lid path are two separately protected packs in parallel again, the problem TOPOLOGY.md exists to solve; a third board P, a third gauge address, more harness across the hinge | fallback if (a) is refuted |
| (c) another gauge: TI BQ34Z100-G1 (held, `v2/vendor/power/bq34z100-g1.pdf`, SLUSBZ5D) | TI documents scaled units for it outright (7.3.1.6 and 7.3.1.8, pages 15 and 16: "if PackConfiguration [SCALED] is set then the units have been scaled through the calibration process. The actual scale is not set in the device and SCALED is just an indicator flag") | it is a gauge only: no FET drive, no AFE protection, so board PL would be a new board with a separate primary protector; its Design Capacity is also I2 to 32,767 (its data-flash table, SLUSBZ5D, row "Design Capacity 0 32767 1000 mAh"), so it scales the same way | second fallback |
| (d) write 32,767 as the design capacity | the gauge would report a pack 18.5 percent smaller than it is, RSOC and FCC wrong | picks the number that fits, not the pack | rejected |

**Decision (authority SESSION, 29 September 2026; reason: (a) keeps one board design and one protection circuit for
both packs and needs no new part, and the scaling it uses is the calibration TI's own EVM procedure performs; reverse
by taking (b) or (c) if TI's answer to Q-TI-A1 or the bench test of section 7 refutes it).**

## 3. The scaling, against TI's documents

1. **What sets the gauge's current unit.** SLUUBF9 (bq4050EVM guide) 3.3.3: current is calibrated by applying a known
   current and entering its value in *Applied Current*; the firmware computes CC Gain and Capacity Gain (SLUUAQ3A Table
   14-1 rows 0x4006 and 0x400a, page 185: CC Gain F4, 0.1 to 4.0, default 3.58422; Capacity Gain F4, 29,800 to
   1,190,000, default 1,069,035.256). The gauge has no other knowledge of amperes: its "mA" is whatever that calibration
   defines.
2. **The k = 2 calibration.** Apply a known true current through board PL's R10 and enter HALF of it (apply -4,000 mA,
   enter -2,000). The firmware's unit is then 2 mA, its "mAh" 2 mAh, and its cWh and cW follow because energy is its
   voltage (unscaled) times its current. The two gains keep TI's ratio (298,261.6, `gauge_scale.out` section 2).
3. **Why it fits.** At k = 2 the design capacity is written **20,100** and **28,944** (61.3 and 88.3 percent of 32,767);
   at the typical 3.45 Ah, 20,700 and 29,808. k = 2 is the smallest integer that fits both. The I2 current range then
   spans -65.5 to +65.5 A true, above board PL's 25 A blade, so no current the path can carry is clipped.
4. **The consequence TI's sibling manual states and this record enforces.** Scaling by calibration changes no firmware
   behaviour (SLUSBZ5D's "the actual scale is not set in the device"), so **every data-flash word whose unit is a current,
   a charge, an energy or a power must be written in the internal unit, or it acts at twice its intended value.**
   `gauge_scale.py` parses Table 14-1 (pages 185 to 197) and finds **63** such words (mA, mAh, cWh, cW and the CEDV
   Electronics Load in steps of 3 uA); it refuses to print if any of them lacks a stated true value, and checks each
   written value against its row's minimum and maximum. All 63 are inside their ranges.
5. **What is not scaled.** The other 322 rows: millivolts (COV, CUV, charge voltages, Design Voltage 14,400 mV),
   temperatures, times, counts and bit fields, written as the base's image writes them
   (`review-packets/battery/PRIMARY-CONFIGURATION.md` section 2). The coulomb counter's own deadband is in 116 nV steps
   of the shunt voltage (row 0x43c7), not a current. **The AFE's hardware thresholds (AOLD, ASCC, ASCD) are voltages
   across the real shunt** (SLUSC67B 6.31, 6.32; SLUUAQ3A 2.6) and are set on R10's true 2 mOhm: the same codes as board P's,
   because board PL is board P and its path limits are the same.

## 4. The exact data-flash values (the lid's golden image, the words that differ from the base's)

Full table with addresses, TI defaults, true values, written values and each reason: `gauge_scale.out` section 3.
The protection and capacity words, true value / **written value** (unit of the written value: 2 mA, 2 mAh or 2 cWh):

| word (TRM section; Table 14-1 row, page) | base 4S6P image | lid true | lid **written** |
|---|---|---|---|
| Design Capacity mAh (14.13.5.1; 0x444d, p.191) | 20,100 mAh | 40,200 mAh | **20,100** |
| Design Capacity cWh (14.13.5.2; 0x444f, p.191) | 28,944 cWh | 57,888 cWh | **28,944** |
| Learned Full Charge Capacity, initial (0x4100, p.191) | = design | 40,200 mAh | **20,100** |
| OCC1 Threshold (14.9.3; 0x4497, p.187), delay 2 s | 5,000 mA | 10,000 mA | **5,000** |
| OCC2 Threshold (0x449a, p.187) | TI default | 12,000 mA | **6,000** |
| OCD1 Threshold (14.9.6; 0x44a0, p.187), delay 2 s | -20,000 mA | -20,000 mA | **-10,000** |
| OCD2 Threshold (14.9.7; 0x44a3, p.188), delay 1 s | -24,000 mA | -24,000 mA | **-12,000** |
| CHGC Threshold (0x44e9, p.189) | TI default | 1,000 mA | **500** |
| Pre-Charging Current (0x455c, p.190) | 1,000 mA | 4,200 mA | **2,100** |
| Standard and Rec Temp charge currents (0x4546 to 0x454a, 0x4556 to 0x455a, p.190) | per image | 8,000 mA | **4,000** |
| Low and High Temp charge currents (0x453e to 0x4542, 0x454e to 0x4552, p.190) | per image | 4,000 mA | **2,000** |
| Charge Term Taper Current (0x456c, p.191) | per image | 800 mA | **400** |
| Dsg / Chg Current Threshold, Quit Current (0x4586 to 0x458a, p.191) | TI | 100 / 50 / 10 mA | **50 / 25 / 5** |
| Remaining AH / WH Cap. Alarm (0x4443, 0x4445, p.195) | TI | 4,020 mAh / 5,789 cWh | **2,010 / 2,895** |

Everything else of the lid's image is the base's image word for word (FET Options 0x3D, DA Configuration 0x17 for 4
cells, COV 4,250 mV, CUV 2,500 mV, the temperature windows of `THERMAL-COORDINATION.md`, HWDF with 10 s, SBS
Configuration BCAST = 0, Shutdown Voltage 2,000 mV and the rest of `PRIMARY-CONFIGURATION.md` section 2), plus three
lid-only words: **SMBus Address** (12.1, page 73) left at 0x16 because the lid gauge has its own bus (TOPOLOGY.md
section 5); **Manufacturer Info Block A** (Table 14-1 from 0x4041, page 194) carrying the ASCII marker `IPSCALE2`;
and the **CEDV profile**, fitted with TI's CEDV tool on this pack's own discharge logs taken under the k = 2
calibration, so its coefficients are in the internal unit by construction (a commissioning step, not a desk value).

## 5. What the host must scale

The host (board E's sensor controller, FW-E01 and its lid twin) multiplies by **k = 2** every value it reads in mA,
mAh, 10 mWh or cW: Current(), AverageCurrent(), RemainingCapacity(), FullChargeCapacity(), DesignCapacity(),
ChargingCurrent(), the Lifetimes records and the PF Status current. It does not scale voltages, cell voltages,
temperatures, RelativeStateOfCharge(), MaxError() or the times (RunTimeToEmpty() and the like are ratios the gauge
forms in its own consistent units). It never writes AtRate() (not in the kit's contract); if it ever does, it writes
half the true value. **ChargingCurrent() times 2 is the most the host may write to U3B's ChargeCurrent** (CHARGER.md),
and the host refuses the lid gauge's currents and capacities until it has read `IPSCALE2` from Manufacturer Info.

## 6. What the documents do not settle (drafted for TI, not sent)

- **Q-TI-A1.** "Does the BQ4050 firmware (SLUUAQ3A, Revised October 2022) apply any fixed current or charge threshold
  that is not a data-flash word of Table 14-1, for example for SLEEP entry, 0-V charging, FET-state detection or
  permanent-fail checks? A pack calibrated so that the gauge's unit is 2 mA would see such a constant act at twice its
  value." If one exists, its effect is judged; if it is safety-relevant and cannot be compensated, option (b) or (c).
- **Q-TI-A2.** "Which of 13.27 and 14.14.1.5 describes IPScale correctly for the BQ4050?" (Informative only: the design
  does not use it.)
- **The CC Gain relation.** The manual does not state how CC Gain relates to the sense resistance, so the gain a k = 2
  calibration writes on 2 mOhm is not computed here; it must read back inside 0.1 to 4.0 (row 0x4006). If it would fall
  outside, k = 2 cannot be calibrated on 2 mOhm and R10 changes on board PL (a generator item, then re-checked).

## 7. What the bench must show before the lid pack is trusted (TEST-PLAN rows to add)

1. After the k = 2 calibration: CC Gain and Capacity Gain read back inside their rows; Current() reads half the true
   current within the gauge's accuracy at +1.0, +8.0 and -15.0 A true.
2. OCC1 opens the charge FET at 10.0 A true (5,000 internal) within 2 s and not at 8.0 A; OCD1 at 20 A true within 2 s;
   the AFE short-circuit trips at the same true currents as board P's.
3. A full CEDV learning cycle: FullChargeCapacity() settles at or under 20,700 internal (41,400 mAh true), and
   RemainingCapacity() times 2 matches a reference coulomb count within the stated error.
4. Every word of section 4 and of the base image written, reset, read back and compared, JP1 closed only afterwards
   (the base's commissioning order, `FUSE-INTERPRETATION.md` section 5).

## 8. Balancing and sensing on a 12P block (unchanged hardware, stated consequences)

Board PL's balancing is the gauge's internal 9.75 mA path (SLUSC67B 6.10, the value section 8a of the energy record
uses): moving 1 percent of a 12P group (402 mAh) takes about 41 h, four times the base's 3P figure. The block must be
built from matched cells at one voltage (the pack-build step of section 8a). Four thermistors on TS1 to TS4, one per
series group, and U2's own NTC, all on the lid block: the error term "sensed cell to hottest cell" is judged on a
block of 48 cells with five sensors, a bench item (`THERMAL-COORDINATION.md` section 3, TEST-PLAN P14).
