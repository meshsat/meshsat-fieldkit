# Secondary over-temperature on board P: decision and netlist change

MeshSat field kit V2, MESHSAT-1357, review stream BAT, 26 September 2026 (second cycle). Prototype design: no board of this
set has been built, and nothing here has been measured on hardware. This is not electrical sign-off; it is the session's
decision and the evidence behind it, prepared for the qualified battery-and-protection review (D-09, see `REVIEW-REQUEST.md`).

**Decision (taken by the session under the owner's standing rule of 26 September 2026):** the BQ7720700's over-temperature
function is restored. Its TS pin gets its own Semitec 103AT-2 thermistor on a separate socket (J_TS2), through a 270 ohm
series resistor (R34) with an 18 kohm resistor from TS to VSS (R33). The fixed 10 kohm that held TS at a 25 C reading is
withdrawn. The +71 C storage margin of D-02a is reconciled for the pack at its cells' own limit instead of being bought
by disabling the protection. The circuit change is in `v2/ecad/tools/gen_sch_p.py` (candidate, generator identity
`4ce12f9caae757d0`), regenerated on the KiCad box and diffed (section 6), and held by a fixture test (section 7).

**Second cycle (the checker's blocking item on BAT-F01).** The first cycle sized the shunt at 22 kohm and claimed it sat
"17.8 percent under the lowest UT resistance at its -2 percent accuracy". That reading was wrong: in SLUSEG7D 6.5 RUT_ACC
(+-2 %) is titled "UT Detection External Resistance Accuracy", the tolerance that footnote (1) *assumes* for the external
part, and the chip's own UT accuracy is TUT_ACC, +-5 C. Moved by TUT_ACC's +5 C at the 103AT's slope, the 26.7 kohm
threshold can sit as low as about 21.5 kohm, and the 22 kohm network's open-NTC ceiling (about 22.4 kohm at +1 % and
-40 C) is above that: the margin was about -4 %, not +17.8 %, so the "indifferent to UT" claim did not hold. The first
cycle also applied TOT_ACC's +-5 C on the OT side and ignored the matching TUT_ACC on the UT side. This cycle treats both
the same way (section 4) and re-dimensions the network to 270 ohm / 18 kohm, whose ceiling is 15.0 % under the
conservative UT figure (13.8 % if the slope of TI's own two warmest UT thresholds is used instead, section 4). The first-cycle numbers are kept below for the record, marked withdrawn.

## 1. The question

The review of 26 September (`v2/docs/reviews/2026-09-26-foundation-progress-review.md:51-53`) found that the BQ77207's
temperature input had been held by a fixed resistor to avoid a secondary over-temperature trip during a +71 C storage
qualification margin, and that "a qualification target is not, by itself, a technical justification for disabling a
protective function". The design at main `1f614233` does exactly that: `gen_sch_p.py` at `1f614233`, lines 363 to 387,
`r("R33", "10k", "TS_SEC", "GND")`, with the reasoning of round-4 decision RP-17 (the morning fix-up): the 70 C trip drives
COUT, COUT fires the chemical fuse F2, and TEST-PLAN E3 stores the kit at +71 C and operates it at +55 C, where D-02a asks it
to survive and recover.

## 2. Evidence (every item VERIFIED by reading the document named)

| # | Fact | Source |
|---|---|---|
| E1 | The BQ7720700 has a fixed 70 C over-temperature threshold; OV 4.325 V, UV 2.25 V, open wire enabled, latch disabled, active-high 6 V outputs. | SLUSEG7D Rev. D (May 2026), section 4, Device Comparison Table (`v2/vendor/battery/ti-bq77207.pdf`, sha256 45c1c99e...) |
| E2 | Over-temperature, open wire and oscillator faults drive BOTH COUT and DOUT; over-voltage drives COUT only; under-voltage DOUT only. | SLUSEG7D Table 7-1 and 7.1 |
| E3 | OT detection: TS ratiometric on an internal pull-up RTC 19.4 to 20.6 kohm; ROT_EXT_NTC 2195 ohm for 70 C; TOT_ACC "OT Detection Accuracy (NTC)" -5 to +5 C; tOT_DELAY 4 s; no capacitor above 200 pF on TS. | SLUSEG7D 6.5, 6.6, 7.3.3 |
| E4 | An under-temperature detection exists in the silicon and drives both outputs: TUT "UT Detection Threshold" -30 to 0 C; RUT_EXT_NTC 111.1, 68.9, 42.2, 26.7 kohm; **TUT_ACC "UT Detection Accuracy (NTC)" -5 to +5 C**, the chip's UT accuracy; RUT_ACC "UT Detection External Resistance Accuracy" -2 to +2 %. Footnote (1), on both TOT_ACC and TUT_ACC: "Assured by design. This accuracy assumes the external resistance is within ±2% of the R_OT_EXT values for the corresponding temperature threshold." The Device Comparison Table has no UT column for any variant, and the custom BQ77207xy option list offers none. | SLUSEG7D 6.5 (page 7), 7.1, section 4 |
| E5 | TI's pin FMA for the BQ77207: TS open-circuited gives "No OT detection" (class B); TS shorted to ground gives "Automatic OT detection"; TS shorted to supply is class A (device damage), "No OT detection". | SFFS317A Rev. A (April 2022), Tables 4-2, 4-3, 4-5 (`v2/vendor/battery/ti-sffs317a-bq77207-fusa.pdf`, sha256 fe429cf9...) |
| E6 | "This protector is most commonly used as a secondary protector meant to flow up a FUSE." (sic: read "blow"); and, on an active-low output, "At the moment no current released versions of this device have that capability." | TI E2E thread 1421182, TI engineer's answer of 2024-10-04 (`v2/vendor/battery/ti-e2e-1421182-bq77207-application.html`, sha256 2038e7af...) |
| E7 | Samsung INR18650-35E, Ver. 1.1: operating (cell surface) charge 0 to 45 C, discharge -10 to 60 C; storage 1 year -20 to 25 C, 3 months -20 to 45 C, 1 month -20 to 60 C, at ex-factory 30 % charge. | `v2/vendor/battery/samsung-35e-orbtronic.pdf` (sha256 5ec577b9...), sections 3.12 and 3.13 |
| E8 | Samsung INR18650-35E, Version No. 1.0 (date of application 2016/04/11): operating (ambient) charge 0 to 45 C, discharge -10 to 60 C; storage 1 year 0 to 23 C, 3 months 0 to 45 C, 1 month 0 to 60 C; note: "Discharge OTP (over temp. protection) should not be over 60'C of the cell surface temperature. Protection set should be based on the location of the cell surface with the highest temp increase part of the battery pack." | `v2/vendor/battery/samsung-35e-akkuzentrum.pdf` (sha256 d2a7c686...), sections 3.15 and 3.16 and their notes |
| E9 | TEST-PLAN E3: "storage 24 hours at +71 C closed, then operation 4 hours at +55 C deployed", pass line includes "pack under 60 C". | `v2/docs/TEST-PLAN.md:18` |
| E10 | D-02a: +55 C operation, +71 C storage and -33 C storage are qualification margins; the pass line at the margin is survive and recover. | `v2/docs/CONOPS.md:389` (D-02a row); `v2/docs/OPERATING-ENVELOPE.md:18-19` |
| E11 | The primary's discharge over-temperature is planned at 60 C and charge at 45 C at the cell surface. | `v2/ecad/tools/pcb_pack_protection.yaml:142-158` |
| E12 | Semitec 103AT-2: R25 10.0 kohm +-1 %, B25/85 3435 K +-1 %, 2.228 kohm at 70 C, 27.28 kohm at 0 C, 17.96 kohm at 10 C, 67.77 kohm at -20 C, 111.3 kohm at -30 C. | `v2/vendor/battery/semitec-at-p12-13.pdf` (sha256 389dc527...), resistance table and specifications |
| E13 | R33 and R34 as bought: UNI-ROYAL 0603WAF1802T5E (18 kohm) and 0603WAF2700T5E (270 ohm), "±1% ±100ppm/℃", JLC basic parts C25810 and C22966. | JLC parts API, 26 September 2026 13:25 UTC (`evidence/jlc-queries-bat.json`) |

What the evidence settles:

1. **A pack held at +71 C is outside its cells' rating whatever board P does.** Both Samsung revisions cap storage at +60 C
   for one month (E7, E8) and discharge at +60 C (E7, E8). TEST-PLAN E3's own pass line already says "pack under 60 C" (E9),
   which a 24 h soak at +71 C cannot meet. The margin, not the protection, is what is inconsistent for the pack.
2. **The +55 C operating margin is also outside the cells' rating for the pack inside the case.** With the ruled internal
   rise of +10 K (one module, D-02b) the air round the pack is about +65 C, above the cells' 60 C discharge limit (E7). The
   primary stops discharge at 60 C (E11); the cells are still beyond their rating.
3. **The protective function does what TI and Samsung intend.** Samsung's note (E8) puts discharge over-temperature
   protection at no more than 60 C at the hottest cell surface: that is the primary's OTD at 60 C (E11), and it is why
   both levels' sensors go on the hottest cells. It does not ask for a trip above 60 C. The secondary's trip sits above
   the primary's as the independent backstop for a failed or misconfigured primary, which is TI's stated use of this part,
   with the fuse as its actuator (E6); a pack that reaches it has already passed the point Samsung sets for protection,
   so retiring it is the intended outcome.
4. **Under-temperature is not stated for the BQ7720700**, and TI's own FMA (E5) treats an open TS (the coldest possible
   reading) as "No OT detection" rather than as a UT fault, which is only consistent with UT not being active. That is an
   inference, not a statement, so the circuit is made indifferent to it (section 4), **at the chip's own UT accuracy,
   TUT_ACC** (E4), not at the external-resistance tolerance RUT_ACC.

## 3. Options considered

| Option | What it does | Verdict |
|---|---|---|
| A. Keep TS on a fixed 10 kohm (main `1f614233`) | No secondary over-temperature at all; OT rests on the gauge's firmware (OTC/OTD, which by the TRM default take no FET action, see `PRIMARY-CONFIGURATION.md`) and the PTC at 110 to 133 C at the FET element. | **Rejected.** It disables a protective function to meet a margin the pack's cells cannot meet anyway (section 2, point 1). |
| B. Bare NTC on TS, TI Figure 8-1 | OT at 70.5 C nominal (103AT on 2195 ohm). If UT were enabled on the 00700, an open NTC or cold storage below the UT threshold (anywhere from about +5 C to -30 C with TUT_ACC) would fire the fuse. | Sound and TI's own arrangement; its only residual is the unstated UT (E4), which TI's FMA (E5) suggests is absent. Kept as the documented simplification if TI confirms UT disabled (section 9). |
| C1. NTC with 200 ohm in series and 22 kohm from TS to VSS (first cycle) | OT at 69.8 C nominal; network ceiling about 22.4 kohm (NTC open, +1 %, -40 C). | **Withdrawn in the second cycle.** The ceiling is above the lowest UT resistance the chip may apply at TUT_ACC (21.5 kohm conservative, 21.9 kohm by the footnote's own reading): an unplugged lead on an armed pack could fire F2 if UT is enabled. |
| **C. NTC with R34 270 ohm in series and R33 18 kohm from TS to VSS (taken)** | OT at 69.97 C nominal; the network never exceeds 18.3 kohm, 15.0 % under the conservative UT figure, so no cold reading and no open lead can look like UT whatever the silicon carries. | **Taken.** Restores the function, stays within the pin's use, and removes the one unknown without a measurement. Costs about 1 C per side of trip accuracy against the bare NTC (section 4). |
| D. A variant with a higher OT | 00701 and 00702 (80 C) and 00704 (83 C) have a 4.275 V OV (+-50 mV over temperature), which can trip at 4.225 V, below a 4.25 V primary COV, and would blow the fuse on a normal overcharge event handled by the primary; 00704 also has an open-drain COUT. 00705 (75 C) has open wire disabled and UV 2.5 V, equal to the primary's CUV. | **Rejected** (SLUSEG7D section 4; the OV reasoning is round-4 RP-03). |
| E. A custom BQ77207xy | Any listed OT from 62 to 83 C, OV and UV to order. | Not orderable ("For future options, contact TI"). |
| F. Route OT so it cannot fire the fuse (for example fuse drive gated by "COUT and not DOUT") | OT and open wire would only hold the FETs through DOUT. | **Rejected.** It also removes open wire from the fuse, puts OT on the same FETs the primary uses (so a welded FET defeats both levels), and adds logic, for a storage case that the cells already rule out. |
| G. Reconcile the margin for the pack | The pack is stored and operated within its cells' limits in qualification; the kit without the pack keeps the +71 C / +55 C / -33 C margins. | **Taken with C** (section 5). |

## 4. The circuit taken, and its numbers

```
U2 pin 12 (TS) ──┬── R34 270R ── J_TS2.1 ── 103AT-2 (off board, on the hottest cell) ── J_TS2.2 ── VSS (GND)
                 ├── R33 18k ── VSS
                 └── TP15 (TS_SEC)
```

Computed by `candidate/ts_network.py` from the Semitec table (E12), SLUSEG7D 6.5 (E3, E4) and the resistors' data (E13);
output in `candidate/ts_network.out`. INFERRED (arithmetic on published figures), not measured.

**The accuracy model, the same for OT and UT.** The chip compares the external resistance with a threshold. Its own error,
expressed as a resistance, is taken from the +-5 C of TOT_ACC or TUT_ACC at the 103AT's slope at that threshold (0.0297 per
C at 70 C, 0.0432 per C at 0.5 C). Footnote (1) can be read two ways, and both are carried:
- **reading A** (the footnote's words): the +-5 C already includes an external resistance within +-2 %, so the chip's own
  share is the +-5 C less 2 %;
- **reading B** (conservative): the +-5 C is the chip's alone.
The network's own tolerance (NTC R25 and B +-1 % each; R33 and R34 +-1 % and 100 ppm/C) is added on top. Every margin
quoted as a single number is reading B, the worse one for both the OT window and the UT ceiling.

| Quantity | Bare 103AT (option B) | 200R / 22k (C1, withdrawn) | **270R / 18k (C, taken)** |
|---|---|---|---|
| OT trip, nominal (network = 2195 ohm) | 70.5 C | 69.84 C | **69.97 C** |
| Slope of ln(R) at the trip, relative to a bare NTC | 1.000 | 0.826 | **0.783** |
| Network tolerance at the trip | -2.5 % to +2.6 % (NTC alone) | -2.30 % to +2.34 % | **-2.26 % to +2.30 %** |
| OT window, reading A | 65.4 to 75.8 C | 63.8 to 76.1 C | **63.6 to 76.6 C** |
| OT window, reading B | 64.7 to 76.5 C | 63.0 to 76.9 C | **62.7 to 77.5 C** |
| Highest resistance TS can see (NTC open, shunt at +1 % and -40 C) | infinite | 22,364 ohm | **18,298 ohm** |
| Lowest UT resistance the chip may apply (26.7 kohm moved by TUT_ACC +5 C) | 21,946 ohm (A), 21,516 ohm (B) | the same | the same |
| Ceiling below that UT resistance, reading B (A) | none: every UT threshold is reachable | **-3.9 % (-1.9 %): overlaps** | **15.0 % (16.6 %)** |
| NTC connected, coldest (-50 C) | 329.5 kohm | 20,624 ohm | 17,068 ohm |
| NTC shorted | OT, fuse (fail-safe) | 198 ohm: OT, fuse | 266 ohm: OT, fuse (fail-safe) |
| NTC open (lead out) | UT if enabled (fuse), else silent | reads as about 5 C | reads as about 10 C: silent |
| R34 shorted / R33 open | n/a | trip 67.0 C / 73.7 C | trip 66.1 C / 75.0 C |
| TS fraction of the internal reference, 25 C / NTC open | 0.333 / 1.0 | 0.258 / 0.524 | 0.246 / 0.474 |

**The UT floor, cross-checked on TI's own thresholds (third cycle).** The floor above moves 26.7 kohm by TUT_ACC's +5 C at
the 103AT's slope at 0.5 C (0.0432 per C). TI's two warmest UT thresholds, 42.2 kohm at -10 C and 26.7 kohm at 0 C (E4),
give a chord slope of 0.0458 per C, which belongs at about -5 C. Applied unchanged over 0 to +5 C it puts the floor at
21,238 ohm and the ceiling 13.8 % under it; a B-parameter fit through the same two thresholds (3290 K), evaluated at +5 C,
gives 21,502 ohm and 14.9 %, within 0.1 % of reading B (`candidate/ts_network.out`, "CROSS-CHECK"). The most conservative
of the three views is therefore 13.8 %, and every view clears the fixture's 10 % `MARGIN` (section 7), which is what the
network was sized to.

For the record, the first cycle's "17.8 percent" was 26.7 kohm less RUT_ACC's 2 % (26.17 kohm) against 22.22 kohm (the shunt
at +1 %); that compares the network with the tolerance of the external resistor, not with the chip's threshold. It was also
the distance by which the threshold sat above the cap; the cap sat 15.1 % below the threshold. Both figures are withdrawn.

**Why these values.** The options, reading B (`ts_network.out`):

| Rs / Rp | trip | slope | window | ceiling | under the lowest UT |
|---|---|---|---|---|---|
| 200 / 22,000 | 69.84 C | 0.826 | 63.0 to 76.9 C | 22,364 ohm | -3.9 % (withdrawn) |
| 240 / 20,000 | 70.04 C | 0.804 | 62.9 to 77.4 C | 20,331 ohm | +5.5 % |
| **270 / 18,000** | **69.97 C** | **0.783** | **62.7 to 77.5 C** | **18,298 ohm** | **+15.0 %** |
| 330 / 15,000 | 69.80 C | 0.744 | 62.2 to 77.7 C | 15,248 ohm | +29.1 % |

18 kohm is the largest E24 value (20 kohm gives 5.5 %) that keeps the ceiling at least 10 % under the conservative UT figure (the fixture's
`MARGIN`, section 7); a smaller shunt buys more UT margin at the cost of slope, which widens the OT window downward toward
the primary's 60 C. 270 ohm then puts the nominal trip at 69.97 C. Both are JLC basic parts (E13).

The window against the other thresholds (cell surface):

```
 45 C   primary OTC (charge stop, recoverable)            pcb_pack_protection.yaml
 60 C   primary OTD (discharge stop, recoverable) = Samsung discharge limit and 1-month storage limit
 62.7-77.5  secondary OT, reading B (63.6-76.6 reading A) -> COUT -> F2 open (permanent) and DOUT -> Q2 off
 65 C   primary SOT permanent fail (TRM default 650 x 0.1 C, enabled by the image)   SLUUAQ3A 14.10.5
110-133 PTC element RT1 beside the FETs -> PTC permanent fail            gen_sch_p.py:228-244
```

The gap between the primary's 60 C and the secondary's lowest trip is about 2.7 K (reading B) or 3.6 K (reading A). A pack
kept inside its cells' rating does not reach the secondary; a pack that reaches it has left every temperature Samsung
rates (E7, E8), and a permanent disconnect for inspection is the intended outcome.

**The sensor.** The secondary has its own 103AT-2 on its own two-way socket, J_TS2 (JST B2B-PH-K-S-GW, C5251182), so an
unplugged J_TS blinds only the gauge and an unplugged J_TS2 only the second level. It is taped to the cell expected
hottest (E8's note). Which cell that is depends on the pack's thermal layout (D-06: shrink-wrapped 4S3P in the east pocket
under board B): **TBD**, owner the pack build; effect: a sensor on a cooler cell delays the secondary by the gradient.

**What the network costs, stated plainly.**
- About 1 C per side of trip accuracy against the bare NTC (slope 0.783): 62.7 to 77.5 C instead of 64.7 to 76.5 C
  (reading B).
- An open 103AT-2 is not detected by U2 (it reads as about 10 C). The bare NTC behaves the same way if UT is disabled,
  which is what TI's FMA says for an open TS (E5). It is found by the commissioning and service check below.
- The NTC lead runs in the cell block beside the tap wires: a TS wire chafed onto a cell tab exceeds the TS pin's 1.5 V
  absolute maximum (SLUSEG7D 6.1) and is FMA class A (E5). Insulation and routing of all five thermistor leads is a
  pack-build item.

**Commissioning and service check (added to O-9).** The TS input cannot be biased continuously: with no fault the whole
device draws 2 uA typical and 3.5 uA maximum (SLUSEG7D 6.5, ICC), far less than a steady bias through the 20 kohm pull-up
RTC into about 6.5 kohm would take, so the bias is pulsed or very small (INFERRED; its timing is not published and is
added to Q-TI-1). A multimeter's DC reading on TP15 may therefore sit near zero whatever is plugged. Two methods:
- **Resistance, before the cells are connected** (commissioning step 1, U2 unpowered): TP15 (TS_SEC) to TP8 (PACK_N,
  joined to VSS through the 2 mOhm shunt R10; the board has no GND test point). With J_TS2 plugged the reading is R33 in
  parallel with R34 and the NTC: about 6.5 kohm at 25 C (5.1 kohm at 35 C, 8.2 kohm at 15 C); unplugged it is R33 alone,
  about 18.0 kohm (17.8 to 18.2 kohm). The ratio is the check, because the unpowered TS pin may load the reading a little.
- **Scope, cells connected** (commissioning step 4 and every service check): TP15 against TP8, triggered on the bias
  pulse. At about 25 C the pulse top is 0.246 of the input's internal reference with J_TS2 plugged and 0.474 unplugged
  (ratiometric on RTC; `ts_network.out`); equal readings mean the NTC is not connected. On an imaged pack this is the only
  method: unplugging J_CELL to measure resistance risks a 2LVL permanent fail when the taps are reconnected
  (`FUSE-INTERPRETATION.md` section 5, step 4).

Then read TP11 (FUSE_G) low, which proves COUT inactive, before JP1 is closed. Because R33 caps the network 15.0 % under the lowest UT resistance at
TUT_ACC (reading B), unplugging J_TS2 on an armed pack does not open F2 even if the BQ7720700 carries UT. The procedure
still unplugs J_TS2 only with JP1 open, because that margin rests on a conservative reading of a data sheet that does not
state UT for this variant at all (Q-TI-1).

## 5. The margin, reconciled for the pack (proposed TEST-PLAN text; owner of TEST-PLAN.md applies it)

Taken by the session under the owner's standing rule of 26 September 2026, because it follows from the cells' rating and
changes no product ruling: D-02a's margins stay for the kit; the pack's margins are its cells' limits. The proposed
TEST-PLAN rows are handed to that file's owner with this stream's integration notes (not part of the packet). In short:

| Test | Kit | Pack |
|---|---|---|
| E3 storage | +71 C, 24 h, closed, **pack removed** (stored separately inside its envelope) | its own check at a **+58 C set point for 24 h**, armed (JP1 closed), in a chamber holding +-2 K or better, with a reference thermometer on the hottest cell, so no cell exceeds Samsung's +60 C one-month storage limit: pass = F2 intact, full function, capacity recovery logged |
| E3 operation | +55 C, 4 h, on shore or vehicle input with the pack removed (or a bench supply on the pack lead) | its own check at its **60 C discharge limit** (cell surface): the gauge stops discharge and recovers; the secondary does not fire |
| E4 storage | -33 C, 24 h, **pack removed** | its own check at the **lowest storage temperature of the governing cell specification** (-20 C in Ver. 1.1, 0 C in the 2016 Version 1.0; which revision governs the purchased lot is TBD, owner the pack purchase) |
| E4 operation | -20 C with the pack heater (unchanged) | unchanged |

The storage soak's set point is 58 C so that a chamber at the edge of its +-2 K tolerance still keeps the cells at or
under their 60 C rating, which leaves 2.7 K to the secondary's lowest trip (reading B) even then. The discharge check
brings the cells to 60 C by their own heating, where the primary's OTD must stop discharge; a cell surface reading above
60 C during E3-P is itself a fail of that check, so the secondary firing there would be a finding, not a nuisance. The kit's
electronics keep the full margin; the pack is never asked to survive a temperature its maker does not rate. The same
reconciliation removes the round-4 residual that the chemical fuse F2 would sit above its +60 C operating rating at E3 (see
`FUSE-INTERPRETATION.md`).

## 6. The netlist change (VERIFIED on the KiCad box)

Box run: vast.ai 52646493, KiCad 9.0.9, `/root/rv/bat/run`, 2026-09-26T13:32:48Z to 13:33:16Z, driver
`evidence/regeneration/bat_box.sh` (unchanged from the first cycle), inputs `git archive 1f614233 v2/ecad v2/vendor/battery
v2/docs` plus the overlay `v2/ecad/tools/gen_sch_p.py` (sha256 `e111e10a...fd7a`). Its log, environment, parity and change
records, gate verdicts and output hashes are in `evidence/regeneration/`; the regenerated board P files are in `candidate/`
(their sha256 in `evidence/regeneration/sha256.txt`). The first cycle's run (12:39:57Z to 12:40:25Z, the 200R / 22k
network) is kept in the session's record. `/root/rv/bat` was removed from the box afterwards.

**Parity first.** Main `1f614233`'s own generator, regenerated on the box, reproduces the committed board P files in
`v2/ecad/pcb-p-pack-p2/`: schematic PARITY, netlist PARITY_AFTER_NOISE, BOM PARITY, ERC PARITY_AFTER_NOISE, intent
PARITY_AFTER_NOISE (`evidence/regeneration/parity_*.json`, `v2/ecad/tools/regen_compare.py`). So the difference below is the
generator change and nothing else.

**Every difference, main regenerated against the candidate** (`candidate/netlist-diff-vs-main.txt`, from
`evidence/regeneration/netdiff.py`; regen_compare reads DIFFERENT, as expected, `evidence/regeneration/change_*.json`):

| Difference | Finding |
|---|---|
| + J_TS2, JST-PH 1x2 (`Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical`), LCSC C5251182; pin 1 TS_SEC_J, pin 2 GND | BAT-F01 |
| + R34, 270R 0603, LCSC C22966; TS_SEC to TS_SEC_J | BAT-F01 |
| + TP15 on TS_SEC | BAT-F01 (commissioning check) |
| ~ R33 value 10k to 18k and LCSC blank to C25810 (same nets TS_SEC and GND) | BAT-F01 |
| ~ U2 value text: "... open wire, TS on a fixed 10k ..." to "... open wire / OT 70 C on its own 103AT-2 (J_TS2) ..." | BAT-F01 |
| new net TS_SEC_J (R34.2, J_TS2.1); TS_SEC gains R34.1 and TP15.1; GND gains J_TS2.2 | BAT-F01 |

**Against the first cycle's candidate** (`candidate/netlist-diff-vs-first-cycle.txt`): R33 22k to 18k (LCSC blank to
C25810), R34 200R to 270R (C8218 to C22966); no part, pin or net otherwise.

Components 82 to 85. No other part, pin or net changed. Comment-only edits in the same file: the docstring, the U2 block
(the accuracy model above), the F2 temperature interpretation (BAT-F03), the F1 identity note (BAT-F04), the Q5 bench
condition. New generator sha256 `e111e10a...fd7a`, identity `4ce12f9caae757d0` (equal to `sch_prov.generator_sha('p')` in
the worktree and to the candidate netlist's sidecar); main's was `d66ae0a1...3714`.

**Gates, base (main regenerated) against new** (`evidence/regeneration/gates-base/`, `gates-new/`):

| Gate | Base | New |
|---|---|---|
| gen_sch_p.py, build_sch.sh | exit 0, 82 parts, 50 nets, 2 A3 pages | exit 0, 85 parts, 51 nets, 2 A3 pages; no single-pin net |
| ERC (erc_gate) | PASS, 120 warnings, 0 errors | PASS, 123 warnings, 0 errors; the three added are `lib_symbol_issues` on TP15, R34 and J_TS2, the same library-table warning every symbol carries on the box |
| TRN-001 port_protect | PASS | PASS (unchanged) |
| SCH-005 pin_map_lands | PASS, 81 judged | PASS, 84 judged, 0 failures |
| CMP-001 derate | PASS, 6 judged | PASS, 6 judged (unchanged) |
| power_path | PASS | PASS (unchanged) |
| BAT-001 pack_protection | 1 finding: the yaml still declares no second protector (O-4) | same text (the yaml is not this stream's file) |
| check_contracts | INCONCLUSIVE (boards A and B absent from the archive) | same |
| check_contracts_p (the contracts that name board P: the pack leads' polarity against board E's XT60, and F1) | PASS, 4 of 4 | PASS, 4 of 4 (`gates-new/check_contracts_p.verdict.json`); the SMBus lead J_SMB is not covered by any contract rule and is read by hand in `PROTECTION-ARCHITECTURE.md` section 9 |
| energy_chain | FAIL 7 of 98, all outside board P's change | same |
| lcsc_fill, on the box | FAIL, 34 rows, 5 blank over allowance | FAIL, 37 rows, the same 5; the box archive did not carry `v2/release/revA/order/JLC-CERTIFIED.tsv` |
| lcsc_fill, re-run on the runner with the certified table and the project allow-list (`evidence/regeneration/lcsc_fill-runner/`) | FAIL, 34 rows, F1 the one blank over allowance (O-3, pre-existing) | FAIL, 37 rows, the same single blank (F1); R33 C25810, R34 C22966, J_TS2 C5251182 filled |

Rendered schematic, page 2, "SECOND-LEVEL PROTECTOR BQ77207": U2 pin 12 (TS) on TS_SEC to R34 270R to TS_SEC_J and J_TS2 pin
1, R33 18k from TS_SEC to GND, J_TS2 pin 2 to GND (`candidate/pcb-p-pack-schematic.pdf`, read as an image at 110 dpi on the
runner).

## 7. The fixture that holds it (checker item: code change without a fixture)

`v2/ecad/tools/tests/test_pack_secondary_ts.py` (new) states the property on connectivity, parsed and never grepped: the
netlist through `regen_compare.parse_net`, the generator through `ast`. U2 pin 12 must reach an off-board two-way socket to
VSS through one series resistor; the shunt from TS to VSS must be at most 18 kohm nominal, and 18 kohm at +1 % and
100 ppm/C down to -40 C must sit at least 10 % under the lowest UT resistance at TUT_ACC (derived in the test from 26.7
kohm and the 103AT table, not typed in; the taken network clears it by 15.0 %, and by 13.8 % on the most conservative view of
section 4, so the 10 % holds on every view); the nominal trip must be within 1.5 C of 70 C; no capacitor on TS. Fixtures: the
taken network PASSES; a fixed resistor alone, the first cycle's 22k shunt, a bare socket with no cap, an on-board sensor, a
capacitor on TS and a 1 kohm series resistor each FAIL. The generator in the tree and the netlist its own generator wrote
(`sch_prov`) are judged too.

Recorded runs (`evidence/regeneration/test-pack-secondary-ts-runs.txt`):

| Artefact | Result |
|---|---|
| main `1f614233` `gen_sch_p.py` (by ast) | **FAIL**: "TS does not reach an off-board thermistor socket through a series resistor" |
| main `1f614233` committed netlist `pcb-p-pack-p2/out/pcb-p-pack.net` | **FAIL**, the same |
| first-cycle candidate netlist (200R / 22k) | **FAIL**: "the shunt from TS to GND is 22000 ohm, above the 18000 ohm cap ... 22364 ohm ... 21516 ohm" |
| candidate `gen_sch_p.py` | **PASS** |
| candidate netlist regenerated on the box | **PASS** |
| the suite with main's `gen_sch_p.py` swapped into a copy of the tools | 8 passed, **1 failed** (`t_the_generator_in_this_tree_holds_the_property`), 1 skipped (no netlist in the copy) |
| `test_pack_secondary_ts` in this worktree | 10 passed, 0 failed, 0 skipped |
| the full suite in this worktree (second cycle, and again in the third after the vendor filing: the same counts both times, the tree's own files unchanged by the run; the logs are in the session's record) | 1422 passed, 0 failed, 70 skipped; the first cycle's worktree run was 1412 / 0 / 70, so the ten new tests account for the difference; main on this host is 1422 / 0 / 60, the ten extra skips being evidence a fresh worktree does not carry (rule audit, routeflow journal, readiness evidence, certification run) |

## 8. What this changes for other owners (none is written by this stream)

- `v2/ecad/pcb-p-pack-p2/` (integrator): take the candidate schematic, netlist, intent and provenance from `candidate/`
  (byte-identical to the box outputs; sha256 in `evidence/regeneration/sha256.txt`). Once they are committed, the fixture
  judges the committed netlist instead of the packet's copy.
- `gen_pcb_p3.py` (placement owner): J_TS2, R34 and TP15 are not placed; region SEC (`gen_pcb_p3.py:140`) lists R33 and
  its comment at lines 77 and 106 still says R33 holds TS at a fixed 10 kohm. Place R34 and R33 at U2 pin 12, J_TS2 at the
  board edge by J_TS, TP15 in TPS2 away from TP14 (TS_SEC is harmless to bridge: at most about 1.5 V). Board P's 4-layer
  regeneration (O-11) is where this lands.
- `pcb_pack_protection.yaml` (BAT-001 owner, O-4): the second level now has over-temperature at 70 C (window 62.7 to 77.5
  C, reading B) through its own NTC; `secondary_protection.present: true`; add U2, F2, Q3, Q5, RT1, JP1, R33, R34, J_TS2.
- `TEST-PLAN.md` (owner): E3 and E4 reconciled for the pack (section 5).
- Certification (`JLC-CERTIFIED.tsv`): rows J_TS2, R33 (new value), R34 are not certified yet (the same state as the other
  round-4 rows, O-3).

## 9. How this is reversed, and what would change it

- **If TI states that UT is disabled on the BQ7720700** (question Q-TI-1 in `REVIEW-REQUEST.md`), R33 and R34 can go and
  the bare NTC (option B) recovers the narrower window (64.7 to 76.5 C, reading B); the commissioning check stays. The
  fixture's cap would then be restated for a bare socket, on a fixture, with TI's answer cited.
- **If TI states the UT accuracy another way** (for example that TUT_ACC already includes RUT_ACC, reading A), the margin
  rises from 15.0 % to 16.6 % (on the 103AT's slope); nothing changes.
- **If the thermal test shows the hottest cell above about 63 C inside the use envelope** (40 C ambient plus the ruled
  rise), the envelope, not the protector, is wrong for the pack: the D-02b carve-outs are what move.
- **If the qualified reviewer prefers the fixed resistor**, the reason must be a technical one about this pack; the margin
  reason is withdrawn (section 2).
