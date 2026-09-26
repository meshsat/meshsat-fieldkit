# The BQ4050 data-flash settings this protection depends on (golden image requirements)

MeshSat field kit V2, MESHSAT-1357, review stream BAT, 26 September 2026. Prototype design: no pack is built, no gauge
is programmed, and no golden image exists yet (open item O-10 of the round-4 board P record). This page is the
requirement list the golden image must meet, with TI's stated default beside each value, so the reviewer can see which
protections exist only if the image is right.

Source for every default: TI BQ4050 Technical Reference Manual, SLUUAQ3A (April 2016, revised October 2022),
`v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf`, sha256 `525d16b2bdee44e5b587ccf6800b9967bc524772d0b5a20937957ea2e738b7ad`
(fetched from ti.com on 26 September 2026; filed in this review by stream PKT, see `MANIFEST.md`). Section and page
numbers below are the TRM's. Required values come from the cell specification (`v2/vendor/battery/samsung-35e-orbtronic.pdf`,
Ver. 1.1, and its Pack Design Guideline on page 14), `v2/ecad/tools/pcb_pack_protection.yaml` (the planned thresholds)
and this packet's architecture. Every "required" value is a design requirement, NOT_YET_TESTED.

## 1. What TI's defaults do (finding BAT-F05)

**As shipped, TI's image holds both FETs off.** Manufacturing Status Init defaults to 0x0000 (14.3.1, page 134; Table
14-1 row 0x4340, page 187; its bit text agrees, FET_EN "0 = Disabled (default)"), and ManufacturingStatus() is re-loaded
from it at every reset or seal (11.1). With FET_EN = 0 the gauge disables charge (4.12, the first condition of the
charge-disable table, "ManufacturingStatus()[FET_EN] = 0 OR") and discharge (4.12, "ManufacturingStatus()[FET_EN] = 0,
OR"); the FETs then move only on the manufacturing-test toggles (13.1.11 to 13.1.13). PF_EN and FUSE_EN are 0 as well, so
the gauge takes no permanent-fail or fuse action (3.1, 13.1.16, 13.1.18). **A pack on TI's image is inert**: it neither
delivers nor accepts current. That is safe and useless, and it is not the hazard.

**The hazard is a partial image**: FET control switched on (FET_EN = 1, by the MAC FET Control command 0x0022 at
commissioning, 13.1.14, or by an image that writes Mfg Status Init and little else) with TI's other defaults. That pack
would:

1. **Let the secondary blow F2 on an overcharge the primary should have handled.** COV defaults to 4300 mV in all four
   temperature ranges (14.9.2); the BQ7720700 can trip as low as 4.275 V (4.325 V less its 50 mV accuracy over temperature,
   SLUSEG7D 6.5). A cell between 4.275 and 4.30 V would open the chemical fuse before the gauge opened the charge FET.
2. **Trip on the kit's normal load.** OCD1 defaults to -6000 mA for 6 s and OCD2 to -8000 mA for 3 s (14.9.6, 14.9.7);
   the pack's declared continuous current is 10 A and peak 18 A (`pcb_energy_chain.yaml`, PACK_CELLS).
3. **Charge up to 55 C.** OTC defaults to 55.0 C (14.9.12); the cells allow charge to 45 C (Samsung 3.12).
4. **Take no FET action on over-temperature at all.** FET Options[OTFET] is 0 in every statement of the default, "No FET
   action for overtemperature condition (default)", and so are CHGIN and CHGSU (14.2.1.1). OTC, OTD and OTF then only
   raise flags (2.8 to 2.10); only UTC and UTD open a FET unconditionally (2.11, 2.12).
5. **Never enter permanent fail and never drive FUSE.** PF_EN and FUSE_EN are 0 (14.3.1), and "All permanent failure
   checks, except for IFC and DFW, are disabled until ManufacturingStatus()[PF] is set" (3.1). The Enabled PF words
   would not rescue it: their headers and Table 14-1 say 0x00, while their own bit texts mark most checks enabled
   (section 1a); Permanent Fail Fuse A to D are 0x00 in every statement (14.2.2.1 to 14.2.2.4).
6. **Give up on a fuse blow before Eaton's maximum opening time.** Fuse Blow Timeout defaults to 30 s (14.2.2.6); the
   SCF9550 heater opens the fuse within 60 s maximum at its operating voltage (ELX1135 page 2).
7. **Never precharge a deep-discharged pack.** FET Options[PCHG_COMM] defaults to 0, "PCHG FET" (14.2.1.1); board P has
   no precharge FET (U1 pin 30 PCHG is NC, `gen_sch_p.py:165-167`), so precharge must use the charge FET (PCHG_COMM = 1).
8. **Treat the 4S pack as three cells.** DA Configuration defaults to 0x12 (14.2.1.14, page 124; Table 14-1 row 0x457B,
   page 187), whose CC1,CC0 = 1,0 is "3 cell (default)"; "1,1 = 4 cell" must be written.
9. **Read one cell thermistor as a FET temperature and possibly ignore two.** Temperature Mode defaults to 0x4, "TS2 Mode
   ... 1 = FET temp (default)" (14.2.1.13), so TS2 would feed the FET over-temperature rather than the cell windows.
   Temperature Enable is 0x6 in the header and Table 14-1, which enables TS1 and TS2 only, while its bit text marks TS3 and
   TS4 enabled by default (section 1a).
10. **Shut down below the cell maker's BMS shut-down voltage.** Shutdown Voltage defaults to 1750 mV per cell (14.5.2.1,
    page 141); Samsung's Pack Design Guideline gives "BMS Shut Down Voltage 2.00V" (Ver. 1.1, page 14).

## 1a. Where the manual states a default two ways (finding BAT-F13)

**Method.** `evidence/trm_defaults_check.py` reads the whole of chapter 14 (14.2 to 14.14) from the TRM's text layer and
asks three questions mechanically: (A) does each parameter row's default equal its row in Table 14-1 (350 compared);
(B) do the "(default)" marks of a bit-field word's own bit texts equal its header default (83 words, 28 of them with at
least one mark); (C) do those marks equal Table 14-1. Its output, `evidence/trm_defaults_check.out`, lists every
disagreement, every row it could not parse or match, and the five multi-row tables it does not compare by name. The
protection rows it could not match by name (OCD1 Delay, CHGV Recovery, VIMR Delay, CFET and DFET Delay, 2LVL, OPNCELL
Delay) were compared by hand against Table 14-1 and agree.

**Correction of the second cycle.** That cycle compared 92 rows (A only) and read the bit texts by eye, and reported
that the bit texts added only Temperature Enable. That was wrong: the checker of the third cycle found FET Options,
Protection Configuration and Enabled PF A, C and D, and the mechanical sweep adds Enabled PF B, LED Configuration,
Initial Battery Mode, the ZVCHG Exit Threshold and five permanent-fail thresholds. The complete list:

| Word (TRM section, page) | Section header | Table 14-1 | What the bit texts mark "(default)" | Effect on this pack | Settled by (section 2) |
|---|---|---|---|---|---|
| FET Options (14.2.1.1, p.116) | 0x20 | 0x20 (0x4407, p.187) | CHGFET "0 = FET active (default)", so bit 5 = 0: 0x00 over the marked bits | whether the gauge opens the charge FET at valid termination | written 0x3D (CHGFET = 1) |
| LED Configuration (14.2.1.6, p.118) | 0x0D0 | 0x00d0 (0x442e) | LEDC1,LEDC0 "0,0 ... (default)" against bits 7 and 6 set | none: board P has no LED display (LEDCNTLA to C not connected, DISP to VSS through R15, `gen_sch_p.py:167, 223`) | LED_EN = 0 in Mfg Status Init |
| Temperature Enable (14.2.1.12, p.123) | 0x6 | 0x06 (0x4579) | TS3 and TS4 "1 = Enable ... (default)": 0x1E | whether TS3 and TS4 are read at all | written 0x1E |
| Protection Configuration (14.2.4.1, p.128-129) | 0x00 | 0x0 (0x447c, p.186) | CUV_RECOV_CHG and SUV_MODE "1 = Enabled (default)": 0x03 | whether CUV recovers without a charger (2.2); whether the SUV check runs with the FETs off at wake (3.2.1) | written 0x03 |
| Enabled Protections B (14.2.4.3, p.129) | 0xFF | 0x3f (0x447e) | every defined bit enabled; reserved bits 7 and 6 unmarked | reserved bits only | written 0x3F; reserved bits Q-TI-6 |
| Enabled Protections C (14.2.4.4, p.130) | 0xFF | 0xd5 (0x447f) | HWDF "1 = Enabled (default)": 0xD7 over the defined bits | host watchdog on or off (2.13) | written 0xD7 |
| Enabled Protections D (14.2.4.5, p.131) | 0xFF | 0x0f (0x4480) | every defined bit enabled; reserved bits 7 to 4 unmarked | reserved bits only | written 0x0F; reserved bits Q-TI-6 |
| Enabled PF A (14.2.5.1, p.131-132) | 0x00 | 0x0 (0x44f5) | the text contradicts itself and its own diagram: "OTF (Bit 6)" and "PF_OTCE (Bit 4)" enabled, then "SOT (Bit 4)" disabled; "RSVD (Bits 3-2)" beside SOCD (Bit 3) and SOCC (Bit 2) | which safety permanent fails latch | written 0x53 by the diagram's bit positions (SOTF 6, SOT 4, SOCD 3, SOCC 2, SOV 1, SUV 0), which PFAlert() (13.1.34, p.85) and Permanent Fail Fuse A (14.2.2.1) share |
| Enabled PF B (14.2.5.2, p.132) | 0x00 | 0x0 (0x44f6) | VIMA and VIMR enabled: 0x18 | the cell-imbalance permanent fails | written 0x00 until Q-P3 |
| Enabled PF C (14.2.5.3, p.132-133) | 0x00 | 0x0 (0x44f7) | 2LVL, AFEC, AFER, FUSE, DFET and CFETF enabled: 0x7B (PTC unmarked) | which hardware permanent fails latch | written 0xFB |
| Enabled PF D (14.2.5.4, p.133) | 0x00 | 0x0 (0x44f8) | TS1 to TS4 and OPNCELL enabled: 0xF2 | the open-thermistor permanent fails | written 0xF0 |
| ZVCHG Exit Threshold (14.2.7, p.134) | 0x0000 mV, maximum 0xFFFF | 2200 mV, maximum 8000 (0x4583, p.187) | n/a (not a bit field) | how long 0-V charging through the charge FET lasts once PCHG_COMM = 1 (4.9) | "Over-discharged cells" below; Q-TI-7 |
| Open Thermistor FET Delta and Cell Delta (14.10.7.3, 14.10.7.4, p.164) | 1500 (0.1 C), with minimum 0 and maximum -400 | 200 (0.1 C), minimum -400, maximum 1500 (0x450e, 0x4510, p.189) | n/a | 3.20: the check trips only when the TS reading is at or below the threshold (223.2 K, -50 C) and the internal temperature is more than the delta above that reading; at 150.0 C the board would have to be 150 K warmer than an open thermistor's reading, which does not happen in service; at 20.0 C an open thermistor trips on any board more than 20 K warmer than its reading | written 200 (20.0 C) |
| VIMR Delta Threshold (14.10.8.3, p.165) | 200 mV | 500 mV (0x4516) | n/a | the at-rest imbalance permanent fail | acts only if PF B is enabled (Q-P3); written as the fresh device reports (commissioning step 2a) |
| VIMA Delta Threshold and Delay (14.10.9.3, 14.10.9.4, p.165) | 300 mV, 5 s | 200 mV, 2 s (0x451f, 0x4521) | n/a | the active imbalance permanent fail | as VIMR |
| AFER Delay Period (14.10.13.2, p.166) | 5 s | 2 s (0x452c) | n/a | the AFE register permanent fail's counter decrement period | written as the fresh device reports (step 2a); Q-TI-6 |
| Initial Battery Mode (14.14.1.4, p.183) | 0x0081 | 0x0081 (0x4449, p.195) | CHGM "1 = Disable ... broadcasts ... (default)" and ICC "0 = Function not supported (default)": 0x4000 over the marked bits | broadcasts to a smart charger, of which this bus has none | none while SBS Configuration[BCAST] = 0, which is written |

Two label slips that change no value: the row of 14.2.2.6 Fuse Blow Timeout is named "Min Blow Fuse Voltage" (default 30),
and the row of 14.2.3.2 Init Charge Set is named "Init Discharge Set" (default 175). ManufacturingStatus() (13.1.39,
page 94) labels BBR_EN "(Bit 8)" where its diagram and 14.3.1 put it at bit 7.

**Rule, taken by the session under the owner's standing rule of 26 September 2026: no requirement rests on a TI default.**
Every word of section 2 is written with the value stated there, including the words whose required value equals every
statement of TI's default. Where the manual gives two values and neither is the protective one (the VIMR, VIMA and AFER
rows), the image carries the value a fresh device reports: its full data flash is read and archived before anything is
written (`FUSE-INTERPRETATION.md` section 5, step 2a), which also records, for every row above, which default TI
actually ships. Q-TI-6 asks TI the same question in writing.

## 2. Required settings

Every row is written explicitly by the golden image and compared on the commissioning read-back. Currents assume
R10 = 2 mOhm (`gen_sch_p.py:209`). "All agree" means the section header, Table 14-1 and the bit text (where it marks a
default) give the same value.

| Setting (TRM section) | TI default | Required | Why |
|---|---|---|---|
| Manufacturing Status Init (14.3.1; 11.1; 13.1.14 to 13.1.18) | 0x0000, all agree (FET_EN, PF_EN, FUSE_EN, GAUGE_EN, BBR_EN "0 ... (default)") | **0x01F8**: FUSE_EN, BBR_EN, PF_EN, LF_EN, FET_EN, GAUGE_EN = 1; LED_EN = 0 | FET_EN enables FET control at all (4.12); PF_EN the permanent fails (3.1); FUSE_EN the gauge's fuse action (13.1.18); GAUGE_EN gauging; BBR_EN the black-box record of the events before a permanent fail (3.1 item 5); LF_EN lifetime data; no LED display. The gauge takes a new Mfg Status Init only at a reset or seal (11.1), so the read-back compares ManufacturingStatus() (13.1.39) after a reset, not only the data flash |
| COV Threshold, all four ranges (14.9.2) | 4300 mV | 4250 mV | cell charge voltage 4.20 V (Samsung 3.2); must stay below the secondary's lowest trip, 4.275 V. How close the gauge's own measurement comes is a reviewer question (Q-P2). |
| COV Recovery (14.9.2) | 3900 mV | 4100 mV | the pack guideline's re-charge voltage (`pcb_pack_protection.yaml:54`) |
| COV Delay | 2 s | 2 s | |
| CUV Threshold / Delay / Recovery (14.9.1) | 2500 mV / 2 s / 3000 mV | 2500 mV / 4 s / 3000 mV | guideline 2.50 V terminate (`pcb_pack_protection.yaml:55`); the secondary holds DSG at 2.25 V below it |
| Protection Configuration (14.2.4.1) | **stated two ways**: 0x00 (header, Table 14-1) against 0x03 (bit text) | **0x03**: CUV_RECOV_CHG = 1, SUV_MODE = 1 | CUV_RECOV_CHG: after a CUV trip, discharge stays off until the cells are above CUV Recovery **and** charging is detected (2.2, recovery condition 2), so a pack left at CUV is not cycled back into discharge by relaxation alone; this is the "recoverable at 3.00 V with charge" of `PROTECTION-ARCHITECTURE.md` section 7. SUV_MODE: the SUV check runs when the gauge wakes from shutdown, with both FETs off for SUV:Delay, "to prevent an applied charge voltage from masking a copper deposition condition" (3.2.1). Taken by the session (TI's own bit-text default, and the protective choice of each pair) |
| Enabled Protections A (14.2.4.2) | 0xFF, all agree | 0xFF | every recoverable protection of the word on (AOLDL, OCD2, OCD1, OCC2, OCC1, COV, CUV), RSVD_ONE "programmed to 1" |
| Enabled Protections B (14.2.4.3) | 0xFF (header) against 0x3f (Table 14-1); the defined bits agree | **0x3F**: OTD, OTC, ASCDL, RSVD_ONE, ASCCL, ASCC; reserved bits 7 and 6 at 0 as Table 14-1 | the reserved-bit value is question Q-TI-6 |
| Enabled Protections C [HWDF] and HWD Delay (2.13, 14.2.4.4, 14.9.17) | **stated two ways**: 0xFF with HWDF "1 = Enabled (default)" (page 130); 0xd5, HWDF = 0, in Table 14-1 row 0x447F (page 186). HWD Delay 10 s in both (14.9.17, page 159; row 0x44CE, page 188) | **0xD7** (Table 14-1's 0xd5 with bit 1 HWDF = 1; CHGC, OC, CTO, PTO and OTF as there, Q-P3; reserved bits 5 and 3 at 0 as there, Q-TI-6) and HWD Delay = 10 s | the gauge's SMBus master is board E's always-on sensor controller; see the HWD paragraph below |
| Enabled Protections D (14.2.4.5) | 0xFF (header) against 0x0f (Table 14-1); the defined bits agree | **0x0F**: UTD, UTC, PCHGV, CHGV; reserved bits 7 to 4 at 0 as Table 14-1 | the reserved-bit value is question Q-TI-6 |
| OCC1 (14.9.3) | 6000 mA, 6 s | 5000 mA, 2 s | three cells at 2.0 A maximum charge = 6 A (Samsung 3.7); the host's charge setting is 3.0 A (board A FW-A02) |
| OCD1 (14.9.6) | -6000 mA, 6 s | -20000 mA, 2 s | continuous 3 x 8 A = 24 A (Samsung 3.8); declared 10 A typical, 18 A peak |
| OCD2 (14.9.7) | -8000 mA, 3 s | -24000 mA, 1 s (TBD by the reviewer) | the yaml's 30 A / 20 ms function cannot be firmware OCD2, whose delay is in whole seconds; it belongs to the AFE's AOLD below |
| AOLD threshold and delay (14.9.9, 2.6.1) | 0xF4 | 30 A class, 20 ms (the yaml's PACK_OVER_CURRENT_DISCHARGE_2), at the nearest AFE step | hardware protection, independent of the firmware loop |
| ASCD1/2 threshold and delay (14.9.11, SLUSC67B 6.31, 6.32) | 0x77 | about 55.6 or 66.7 A (RSNS = 1 steps of 22.2 mV over 2 mOhm) at about 183 to 244 us | the yaml's 60 A / 200 us falls between steps; the delay is also a FET safe-operating-area question (`FUSE-INTERPRETATION.md` section 4, BAT-F07) |
| ASCC (14.9.10) | 0x77 | set for the charge-direction short at the charger's worst case | |
| AFE Protection Control (14.2.6.1) | 0x70, all agree (RSNS "0 = 0.5 x AFE Protection Thresholds (default)") | RSTRIM 0x7 as TI instructs; RSNS as the AOLD and ASCD rows need (RSNS = 1 for the steps quoted) | the AFE thresholds above assume the RSNS it names |
| OTC Threshold / Recovery (14.9.12) | 55.0 / 50.0 C | 45.0 / 40.0 C | Samsung charge limit 45 C (3.12) |
| OTD Threshold / Recovery (14.9.13) | 60.0 / 55.0 C | 60.0 / 55.0 C | Samsung discharge limit 60 C and its note that discharge OTP should not exceed 60 C at the hottest cell (2016 Version 1.0, note 2) |
| UTC (14.9.15) | 0.0 C, recovery 5.0 C | 0.0 C, recovery 5.0 C | Samsung charge floor 0 C |
| UTD (14.9.16) | 0.0 C | -10.0 C | Samsung discharge floor -10 C; the kit's cold behaviour is D-02d |
| FET Options (14.2.1.1) | **stated two ways**: 0x20 (header, Table 14-1), which sets CHGFET, against CHGFET "0 = FET active (default)" in the bit text | **0x3D**: PACK_FUSE 0, SLEEPCHG 0, CHGFET 1, CHGIN 1, CHGSU 1, OTFET 1, PCHG_COMM 1 | OTFET: temperature protections must open a FET; CHGIN/CHGSU: the charge temperature ranges act on the FET, because the charger has no thermistor input (`CHARGER-STATE-SEQUENCE.md`); CHGFET: the gauge ends charge at termination with no host; PCHG_COMM: no PCHG FET on this board; PACK_FUSE 0: F2 is on the cell side, so the stack voltage decides (3.1 note) |
| SBS Configuration (14.2.1.3) | 0x20, all agree | 0x20: BCAST = 0, BLT 2 s | the pack's SMBus has one master (board E's sensor controller) and no smart charger; no broadcasts. With BCAST = 0 Initial Battery Mode's CHGM conflict (section 1a) has nothing to act on |
| Power Config (14.2.1.4) | 0x00 (header, Table 14-1; the bit text marks no default) | 0x00: AUTO_SHIP_EN = 0 | an automatic shutdown after a quiet SLEEP would drop the kit's supply; storage shutdown is commanded (MAC 0x0010, `PROTECTION-ARCHITECTURE.md` section 4) |
| Balancing Configuration (14.2.1.15) | 0x01, all agree | 0x01 (CB = 1) | balancing on; its effect on the second level's open-wire detection is Q-P1 |
| Shutdown Voltage (14.5.2.1) | 1750 mV | 2000 mV | Samsung's Pack Design Guideline, "BMS Shut Down Voltage 2.00V" (Ver. 1.1 page 14; `pcb_pack_protection.yaml:51-65` quotes the same guideline) |
| Min Blow Fuse Voltage (14.2.2.5) | 3500 mV | 10500 mV | the SCF9550-30-05 heater's rated operating range starts at 10.5 V (ELX1135 page 2); FET failures bypass the check (3.1 item 8). Whether an unrated attempt below 10.5 V is better than none is question Q-P4 |
| Fuse Blow Timeout (14.2.2.6) | 30 s | at least 60 s (120 s proposed) | Eaton: heater opens the fuse within 60 s maximum (ELX1135 page 2); Q3 carries 1.3 to 3.5 A meanwhile (about 0.5 W, `gen_sch_p.py` fuse drive comment) |
| Enabled PF A (14.2.5.1) | **stated two ways** (section 1a) | **0x53**: SUV, SOV, SOT, SOTF; SOCC and SOCD 0 until the reviewer answers Q-P3 | SOV default 4500 mV and SOT 65.0 C sit above the recoverable levels; SOT at 65 C duplicates the secondary's window on an independent sensor; SUV per "Over-discharged cells" below |
| SUV Threshold / Delay (14.10.1) | 2200 mV / 5 s | **1000 mV** / 5 s | Samsung: "Under 1.0V voltage, do not charge the cell" (Ver. 1.1 Pack Design Guideline, page 14; the 2016 Version 1.0, Pack Design Guideline 1.1.7, page 19: "Do not charge the battery under 1.0V voltage") |
| Enabled PF B (14.2.5.2) | **stated two ways** (section 1a) | **0x00** until Q-P3 | the imbalance thresholds are themselves stated two ways; a permanent fail on an unreviewed threshold scraps a pack without covering a hazard the per-cell COV, CUV, the second level and SUV leave open. Taken by the session as the interim value |
| Enabled PF C (14.2.5.3) | **stated two ways** (section 1a) | **0xFB**: PTC, 2LVL, AFEC, AFER, FUSE, DFET, CFETF (bit 2 reserved, 0) | 2LVL records the secondary's COUT on the FUSE pin (3.16); PTC records the hardware PTC trip (3.15) |
| Enabled PF D (14.2.5.4) | **stated two ways** (section 1a) | **0xF0**: TS1 to TS4 open thermistor; OPNCELL 0 until Q-P3 | four cell thermistors on J_TS (`gen_sch_p.py:221`) |
| Open Thermistor Threshold / Delay / FET Delta / Cell Delta (14.10.7) | 2232 (0.1 K) / 5 s agree; the deltas **stated two ways**, 1500 against 200 (0.1 C) | 2232 / 5 s / 200 / 200 | at a delta of 1500 the open-thermistor permanent fail this page enables could not act in service (3.20, section 1a) |
| Permanent Fail Fuse A to D (14.2.2.1 to 14.2.2.4) | 0x00, all agree | at least SOV, SOT, PTC, CFETF, DFETF; the rest per the reviewer; **never SUV** | which permanent failures blow F2 rather than only opening the FETs. An SUV pack is below the heater's rated 10.5 V (4 x 1.0 V) and is already disabled by the FETs |
| Temperature Enable (14.2.1.12) and Temperature Mode (14.2.1.13) | Enable **stated two ways** (0x6 against 0x1E); Mode 0x4, all agree (TS2 a FET temperature) | **Temperature Enable = 0x1E** (TS1 to TS4, internal sensor off) and **Temperature Mode = 0x00** (all four CELL temperature); DA Configuration[CTEMP] = 0 (maximum of the four) | one thermistor per series group (`gen_sch_p.py:210-221`) |
| DA Configuration (14.2.1.14; 2.6, 5.2) | 0x12, all agree: SLEEP 1, NR 0 (removable), CC 1,0 = 3 cell | **0x17**: CC1,CC0 = 1,1 (4 cell), NR = 1 (embedded), SLEEP = 1 as TI's default; IN_SYSTEM_SLEEP, EMSHUT_EN, CTEMP, FTEMP = 0 | PRES is held low on board P by R14 (`gen_sch_p.py:223`), so it never makes the transition a removable pack's latch recovery waits for |
| ZVCHG Exit Threshold (14.2.7) | **stated two ways**: 0x0000 mV against 2200 mV | TBD by Q-TI-7; interim **0 mV** | see "Over-discharged cells" below |
| Charge Term Taper Current, SOC flag config (4.6, 4.7) | per image | set so TC is raised at termination and cleared at a recharge threshold | with CHGFET = 1 this is the host-free termination (`CHARGER-STATE-SEQUENCE.md`) |
| VIMR, VIMA thresholds, AFER Delay Period (14.10.8, 14.10.9, 14.10.13) | **stated two ways** (section 1a) | as the fresh device reports (commissioning step 2a) | no protective side in either reading; VIMR and VIMA act only if Q-P3 enables PF B |

**Over-discharged cells, taken by the session under the owner's standing rule of 26 September 2026.** Samsung's guideline
is plain: "Under 1.0V voltage, do not charge the cell", with pre-charging for cells between 1.0 and 3.0 V (Ver. 1.1, page 14).
PCHG_COMM = 1, which this board needs to precharge at all, also brings 0-V charging: "If [PCHG_COMM] = 1, the gauge enables
the hardware 0-V charging circuit automatically when the battery stack voltage is below the minimum operation voltage of
the device" (4.9), and the gauge leaves that mode at the ZVCHG Exit Threshold, which the manual states as 0 or 2200 mV
(section 1a). A 4S stack below the device's 2.2 V supply minimum (SLUSC67B 6.3) has at least one cell under 0.55 V. The
requirement is therefore stated as the cell maker states it, and enforced by the check TI provides for it: Enabled PF A[SUV]
= 1 at 1000 mV, with Protection Configuration[SUV_MODE] = 1, so a pack that wakes with any cell at or below 1.0 V is
disabled permanently with its FETs held off during the check (3.2, 3.2.1), and SUV never maps to the fuse. What is not
known is whether the hardware 0-V circuit can conduct before the woken firmware has made that check, and what exit value
disables 0-V charging on this part: question Q-TI-7 to TI and a bench item (a 4S string simulator at 0.9 V per cell with a
charger on PACK must see no charge current, O-9). Until TI answers, the image writes ZVCHG Exit Threshold = 0 mV, the
reading of 14.2.7's one sentence ("Voltage() threshold where the gauge will exit ZVCHG mode") that ends the mode soonest
(INFERRED).

**HWD, taken by the session under the owner's standing rule of 26 September 2026.** The gauge's host watchdog disables
charging when no valid SMBus transaction arrives for HWD:Delay (2.13). Whether it is on out of the box is not settled by
TI's own manual: 14.2.4.4 says enabled, Table 14-1 says disabled (section 1a). The requirement is therefore an explicit
write, HWDF = 1 and HWD Delay = 10 s, and the behaviour the rest of this packet describes (`CHARGER-STATE-SEQUENCE.md` S9,
`PROTECTION-ARCHITECTURE.md` section 5) holds only once that write is read back at commissioning. The gauge's SMBus master
is the RP2040 sensor controller on board E, which runs from the pack node whenever the pack is connected
(`gen_sch_e.py:111-126`, U12's EN tied to CELL_F; J_SMB to GPIO 2 and 3 at `gen_sch_e.py:501-508`). Enabling HWD ties
charging to that controller being alive; leaving it off would let a charger keep charging while nothing reads the gauge.
Neither changes cell safety, which is the gauge's own; enabled is the more conservative. Reverse it if the sensor
controller's availability proves lower than the charge path needs.

## 3. Which protections exist without the image

| Protection | Needs the image? | Evidence |
|---|---|---|
| Any FET action by the gauge (charge or discharge, every firmware and AFE protection below) | **Yes**: FET_EN = 1 in Mfg Status Init; TI's 0x0000 holds both FETs off | 4.12, 14.3.1, 11.1 |
| BQ7720700 OV, UV, open wire, OT, oscillator (second level) | **No** | fixed in the part (SLUSEG7D section 4) |
| PTC element RT1 opening the FETs | **No**: "a hardware controlled feature", "also works in SHUTDOWN mode" | SLUUAQ3A 3.15 |
| PTC recorded as permanent fail and driving FUSE | Yes (PF_EN, FUSE_EN, Enabled PF C, PF Fuse C) | 3.1, 14.2.5.3, 14.2.2.3 |
| AFE short circuit and overload (ASCD, ASCC, AOLD) | Partly: they run in the AFE, at default thresholds unless written | 2.6 |
| Gauge COV, CUV, OCC, OCD, temperature windows | Yes (FET_EN, values and OTFET) | section 1 above |
| Gauge FUSE output, for any cause | Yes (PF_EN, FUSE_EN, PF Fuse words) | 3.1, 13.1.18, 14.2.2 |
| F1 25 A blade, D1 terminal clamp, C11/C12 | No | passive |

Consequence for commissioning: **a pack on TI's shipped image is inert**, JP1 closed or not: both FETs are held off
(FET_EN = 0), so it can neither deliver nor accept current, and the PTC's and the AFE's FET actions have nothing to act
on. What still acts is the second level (which, once JP1 is closed, opens F2 on OV, open wire, OT or an oscillator fault)
and F1. The unsafe state is the **partial image** of section 1, FET control on with TI's thresholds, above all its
3-cell count (item 8), which makes every cell protection of the gauge wrong for this 4S pack. The order "fresh device read
and archived, image written, reset, every word of section 2 and ManufacturingStatus() read back, then JP1 closed" is
therefore a safety step, not a convenience (`FUSE-INTERPRETATION.md` section 5).
