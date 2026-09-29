# TOPOLOGY: two separately protected packs at the system node (Option A(i), stream a1elec, MESHSAT-1357)

29 September 2026. **Prototype design, AI review: nothing drawn in a generator, built, ordered or measured.** This
page is the electrical design the energy model (`energy_two_pack.py`) runs, written for the generators' owners as a
DRAFT. Figures marked `.out` are printed by that script (`energy_two_pack.out`, section named); makers' figures carry
their document, section and page; ESTIMATE marks arithmetic on stated assumptions. M1 and REQ-072 are unchanged;
REQ-072 stays FAIL until this is drawn, reviewed and tested. Nothing here is purchased or authorised.

## 1. The answer in brief

```
 base 4S6P (both base pockets, section 8 of the energy record)       lid 4S12P (lid module)
 board P  (BQ4050 U1, BQ7720700 U2 + U2B, F1 25 A, F2 SCF9550,       board PL = board P as generated, a second instance
           Q1/Q2 CSD17570Q5B, R10 2 mOhm)                                      (its own image: GAUGE.md, k = 2)
      |  CELL+ (dock pins, as today)                                     |  hinge harness: 2 x 12 AWG + SMBus lead
      F1 (board A, 25 A MINI) -- CELL_FUSED                              F_LA (board A, 15 A MINI) -- LID_IN
      |                                                                  |                                  \
      R17 5 mOhm (U3's RSR)                          LM74700-Q1 + CSD18510Q5B (ideal diode, blocks node->lid)  \
      |                                                                  |                                   R17B 5 mOhm (U3B's RSR)
 ==== VBAT, the system node (U3's VSYS; every converter) ====  <------  LM5069-2 + CSD18510Q5B, 5.6 mOhm     |
      ^                    |                                             (current limit 8.7 to 11.0 A; UVLO    U3B BQ25731 buck-boost
      |                    +--- VBUS of U3B (a second BQ25731) --------  enable, off while U3B runs)          (VBAT in, lid out)
 U3 BQ25731 (from VBUS20, as generated)
```

1. **The base pack stays exactly where S-04 put it**: the one BQ25731 **U3** charges it through **R17** (its RSR) and it
   discharges through R17 into VBAT. Nothing in that path changes (section 2).
2. **The lid pack has its own charger and its own one-way discharge path.** A second BQ25731, **U3B**, takes its input
   from VBAT and charges the lid through its own RSR **R17B**; the lid discharges into VBAT through an **LM74700-Q1 ideal
   diode in series with an LM5069-2 current-limited switch** (section 3).
3. **What stops one pack charging the other** (section 3c): base to lid is blocked in hardware (the ideal diode, and
   U3B's four-switch stage when off); lid to base happens only when the lid's voltage is above the base's, is limited in
   hardware to at most 11.0 A (1.83 A a base cell, under the cell's 2.0 A maximum charge), and is kept under 2.5 A in
   service by the host's join rule (0.20 V). The lid's discharge path is held off in hardware while U3B charges, so
   U3B's output can never flow back into the node through it (3b).
4. **The host sees two gauges on two separate SMBus segments** and **two chargers on the kit bus, U3B behind a
   TCA9543A switch** because both BQ25731 answer only at 0x6B (section 5).
5. **On the model**, this topology meets M1's September reference day with 400 Wp into a 200 W stage and board A's entry
   re-rated, with the lid at the mean day's minimum air (13.23 C) and down to a lid at **+9.6 C**; the lowest points are
   30.3 Wh in the base and 0.7 Wh in the lid (`.out` 3). With board A's entry as generated it does not (section 7).

## 2. The base pack: unchanged, with section 8's additions

The base is the 4S6P of `records/energy/ENERGY-RECONCILIATION.md` section 8: the east and west 4S3P blocks joined at
every series node under the one board P, with U2B on the west block's own taps, a fuse per string and per middle link,
two thermistors per block, ChargeCurrent at most 4.0 A and OCC1 5.0 A (section 8a's session settings, kept here). Its
path to the node is S-04's as `gen_sch_a.py` generates it: CELL+ over the dock, F1 (25 A MINI), CELL_FUSED, **R17**
(5 mOhm RSR, U3's SRN on CELL_FUSED through R148, SRP on VBAT through R149), VBAT. **No BATFET** (SLUSE66A Figure
10-1, as the generator's comment at U3 says), so the base pack is hard-wired to the system node: that fact shapes the
rest of this page.

## 3. The lid pack's path

### 3a. Protection and gauge: board PL

Board PL is **board P as `gen_sch_p.py` generates it**, a second instance in the lid module: BQ4050 U1 (gauge and
primary protection), BQ7720700 U2 (second level on its own taps, filters, supply and NTC), F1 25 A MINI, F2 Eaton
SCF9550-30-05, Q1/Q2 CSD17570Q5B, R10 2 mOhm, RT1 PTC, JP1, the same J_CELL, J_TS, J_TS2 and J_SMB. A 4S12P block is a
4S block to both levels; the parallel count changes only per-cell currents, which fall. What differs is data only: the
gauge's image at k = 2 (`GAUGE.md`). Its thresholds are in section 4.

### 3b. Charge: a second BQ25731 (U3B), and why one charger cannot serve both packs

**Why a second charger** (authority SESSION; reverse by a battery-selector design if a qualified review prefers one):
1. U3's charge loop regulates the current through ONE sense resistor, R17 (SLUSE66A 9.3.5, page 25: ChargeCurrent is
   the current through RSR). Two packs behind R17 are two packs in parallel: their split would be set by their open-circuit
   voltages and path resistances, not by the charger, exactly the aggregate model's hidden assumption.
2. The charger has no BATFET (Figure 10-1), so it cannot disconnect one pack to charge the other; a selector would need
   two bidirectional switch pairs and a control law of its own, and with the system on VSYS the higher pack would still
   feed the lower one through the selector's discharge side (section 3c).
3. A four-switch buck-boost that is off blocks both directions. SLUSE66A Table 9-3 (page 27) names the four switches;
   `gen_sch_a.py` places U3's N-FETs with Q7's drain on the input side (CH_ACN) and source on CH_SW1, and Q10's drain on
   the output (VBAT) and source on CH_SW2 (the `nfet` line after U3). Each high-side body diode therefore conducts only
   from its switching node toward its own terminal, and the low-side ones only from ground: with the stage off, neither
   terminal can drive current into the other. U3B, placed the same way, isolates the lid from the node except while it
   regulates.
4. U3B's own loops give the lid its own CC-CV charge (16.8 V, 4S strap as U3's R26/R27), its own current (ChargeCurrent
   through R17B) and its own input limit from the node (IIN_HOST through R16B).

**The parts** (drafts for board A's generator; the U3 set copied): U3B BQ25731RSNR; Q7B to Q10B CSD18510Q5B; **L2B
Coilcraft XAL1010-332ME** (3.3 uH, DCR 3.70 / 4.10 mOhm, Isat 27.4 A, Irms 18.2 A at a 20 C rise; held
`v2/vendor/power/coilcraft-xal1010.pdf`); **R16B 5 mOhm** (RAC; RSNS_RAC = 1b) and **R17B 5 mOhm** (RSR; RSNS_RSR = 1b),
2512; the IADPT resistor for 3.3 uH (169 k, SLUSE66A 9.3.11 and Table 9-4) so that Table 9-1 (page 26) allows 10 A of
input current; U3's filter set (R146 to R149, C121, C122) and input and VSYS capacitors copied; its VBUS pin on VBAT.

**Settings** (CHARGER.md has the figures): ChargeVoltage 16.8 V (the strap's 4S default); ChargeCurrent at most **7.936 A**
(62 x 128 mA) and never above the lid gauge's ChargingCurrent() x 2 (GAUGE.md); IIN_HOST **8.0 A** nominal from VBAT
(code 80: seven bits of 100 mA with RAC 5 mOhm, SLUSE66A 9.6.22 and Table 9-50, page 80; the register text adds 200 mA
for the maximum, 8.2 A); InputVoltage (VINDPM) at 12.0 V so that U3B backs off before it could pull the node below the
base's graceful line (a firmware choice, bounded by the charger's own VINDPM loop).

**The interlock: U3B charges only from outside energy, and never while the lid discharges.** U3B's ILIM_HIZ pin is
pulled below 0.4 V (HiZ, the converter off; above 0.8 V it runs; SLUSE66A pin table page 6 and 9.3.8, pages 26 and 27)
unless BOTH U3's CHRG_OK (open drain, R22 to +3V3: input present and no fault) AND the host's LID_CHG_EN (pulled down,
so a dead host leaves it low) are high: an SN74LVC1G00 NAND (held, `v2/vendor/ti/ti-sn74lvc1g00.pdf`) drives a 2N7002
from ILIM_HIZ_B to ground. With the kit on batteries alone U3's CHRG_OK is low and U3B cannot run, so **the base can
never charge the lid on battery**. The same two inputs into an SN74LVC1G08 AND (held, `ti-sn74lvc1g08.pdf`) drive a
second 2N7002 that pulls the LM5069's UVLO low (3c): **whenever U3B may run, the lid's discharge path is off.** Without
it, U3B's output would lift the lid's end of the harness (the charge current through the lead and the cells, about 0.3 V
at 8 A over the cells' 11.7 mOhm and the charge loop's 28 mOhm of `.out` section 0) above the node, and the ideal diode would return U3B's current into VBAT, a
circulating loop that also charges the base outside U3's control. The model never charges and discharges the lid in the
same hour, which this interlock makes true of the circuit. In daylight the host's
allocation loop (FW row in section 8) holds U3B's charge so that U3's reading of the base's current (ADCIBAT, 128 mA
steps) is not a discharge; a passing cloud lets the base feed U3B for the loop's reaction time, bounded by U3B's
IIN_HOST.

### 3c. Discharge: an ideal diode and a current-limited switch in series, and the join rule

**Parts** (drafts for board A): **U_LD LM74700-Q1** driving **Q_LD CSD18510Q5B** (40 V; RDS(on) 0.79 / 0.96 mOhm at
10 V, TI SLPS632 page 3) as an ideal diode, anode on LID_F (behind F_LA, the node U3B's R17B also feeds), cathode
toward VBAT; then **U_LS LM5069-2** (auto-retry;
SNVS452G, device table on page 3; operating 9 to 80 V, page 1) driving **Q_LS CSD18510Q5B** with **R_LS 5.6 mOhm** 2512
as its sense; the LM5069's input on the ideal diode's cathode side, its output on VBAT. The LM5069's 9 V floor is the
lid at 2.25 V a cell, the second level's under-voltage.

**What each blocks.**
- *Node to lid* (the base charging the lid): the LM74700-Q1 turns its FET off when V(AK) falls below its reverse
  threshold, **-17 / -11 / -2 mV** (SNOSD17G 6.5, page 6), and its fast response "(< 0.75 us)" (page 1); the FET's body
  diode points lid to node, so the reverse current meets a blocking junction. The LM5069's FET is on the node side and its
  body diode points node to lid, but it is in series with the blocked ideal diode. **Base to lid: blocked in hardware.**
- *Lid to node*: the ideal diode conducts with its regulated **13 / 20 / 29 mV** V(AK) (page 6) whenever the lid's
  terminal is above the node; the LM5069 limits the current at **VCL 48.5 / 55 / 61.5 mV** over 5.6 mOhm, **8.7 / 9.8 /
  11.0 A** (SNVS452G, page 6), and after its fault timer turns off and retries (the -2 variant). With the LM5069 off,
  its FET's body diode (node to lid) is in series with the ideal diode's (lid to node): **both directions are blocked**.

**Why the limit sits at 8.7 to 11.0 A.** The base pack is hard-wired to VBAT, so a lid whose voltage is above the base's
charges the base through this path. At the limit's maximum, 11.0 A into the base is 1.83 A a cell, **under the 35E's
2.0 A maximum charge current** (spec 3.7), whatever the voltage difference (`.out` 8). The lid's share of the kit's
10 A continuous (6.7 A at the capacity split) stays under the 8.7 A minimum. At the kit's 18 A peak the lid path limits
and the hard-wired base takes the rest; if the peak lasts past the LM5069's fault timer the lid path turns off and
retries, and the base carries all 18 A meanwhile (3 A a base cell, under the 8 A discharge rating, spec 3.8). The
LM5069's power limit and timer are sized by board A's owner with SNVS452G's design procedure for the start into VBAT's
capacitance with the base absent, the one case in which the lid path, not the base, charges the node.

**Each pack's graceful line.** CONOPS 4c's line (RSOC 5 percent, or the lowest cell at 3.00 V under load) applies per
pack: the host turns the lid path off when the lid reaches it, and shuts the kit down when the base reaches it with the
lid already out. The model's stores end there. With the capacity split the colder lid reaches its line first at the
basis; if the base reached its line first while the lid still held energy, the kit could keep running on both until the
base's own CUV (2.50 V) opens its discharge FET, energy the model does not credit.

**The join rule** (host, a firmware draft): the lid path is enabled while the lid's gauge voltage is at most 0.20 V
above the base's (50 mV a cell); a lid fuller than that waits, disabled, while the base carries the load (the gap closes)
or while U3 charges the base. At 0.20 V the transfer into an unloaded node is at most **2.5 A** (`.out` 8: loops of 41.7
and 39.2 mOhm on the cells' 35 mOhm class figure, an upper bound because the DC resistance is higher), under U3's 4.0 A
setting and the base's OCC1 5.0 A. In service the capacity-proportional allocation (section 6 of `.out`, policy 'ah')
keeps the two packs' states of charge together, so the gap stays small.

**Without the host** (a crash, or the first power-up): the lid path's enable is the LM5069's UVLO/EN pin (threshold
2.45 / 2.5 / 2.55 V, SNVS452G page 5) held by a divider from LID_IN at about 11.0 V rising (the lid itself at 2.75 V a
cell) and pulled low by the host's LID_DSG_OFF through a 2N7002 (default off, so the path defaults ON) or by the
interlock's AND while U3B may run (3b). A default-off
path would leave a full lid unusable when the base is empty and the sensor controller, which runs from the base's node,
is dead; a default-on path joins at any gap, which the 11.0 A limit keeps inside the base cells' charge rating. The
base's own OCC1 (5.0 A, 2 s) then opens the base's charge FET for a gap above about 0.4 V, a recoverable trip. **Taken by
the session: default ON, limited in hardware** (reverse: a default-off enable and a boot path from the lid).

## 4. Every protection threshold, per pack

Base = board P as generated with section 8a's additions; lid = board PL with GAUGE.md's image. Sources: the gauge rows
from `pcb_pack_protection.yaml` and `PRIMARY-CONFIGURATION.md` section 2 (TI SLUUAQ3A sections named there); the second
level from TI SLUSEG7D (Device Comparison Table, 6.5, 6.6); the fuses from Littelfuse 297 (time-current table, 1000 A at
32 VDC) and Eaton ELX1135; the cell limits from Samsung 35E spec Ver. 1.1.

| function | device | base 4S6P | lid 4S12P | cell limit it answers |
|---|---|---|---|---|
| cell over-voltage | gauge COV | 4.25 V, 2 s (recovery 4.10 V) | same | 4.20 V charge (3.2) |
| cell under-voltage | gauge CUV | 2.50 V, 4 s (recovery 3.00 V) | same | 2.30 V over-discharge protection (guideline) |
| charge over-current | gauge OCC1 / OCC2 | 5.0 A, 2 s (section 8a) / TI | **10.0 A, 2 s / 12.0 A** (5,000 / 6,000 internal) | 2.0 A a cell (3.7): 12 A and 24 A |
| discharge over-current | gauge OCD1 / OCD2 | -20 A, 2 s / -24 A, 1 s | same (-10,000 / -12,000 internal) | 8 A a cell (3.8): 48 A and 96 A |
| overload, short circuit | AFE AOLD, ASCD (mV over R10) | 30 A class, 20 ms; about 55.6 or 66.7 A at 183 to 244 us | same codes (true 2 mOhm) | 13 A pulse a cell (3.8) |
| charge temperature | gauge UTC / OTC; T1 to T4 | 1.0 / 44.0 C; 1, 12, 20, 25, 42, 43 C | same | 0 to 45 C (3.12) |
| discharge temperature | gauge UTD / OTD | -9.0 / 57.5 C | same | -10 to 60 C (3.12) |
| second level OV | BQ7720700 COUT to F2 | 4.325 V +-50 mV, 1 s | same (own U2) | as above |
| second level UV | BQ7720700 DOUT holds Q2 | 2.25 V +-50 mV (W4DP-F1 open) | same | 2.30 V |
| second level OT | BQ7720700 | 70 C (62.7 to 77.5 C at its network; BAT-F16 open) | same | 60 C |
| FET over-temperature | PTC RT1 | 110 to 133 C at the element | same | the FETs' 150 C |
| permanent fails | gauge SOT, SUV | 65.0 C; 1.0 V | same | 1.0 V "do not charge" |
| chemical fuse | F2 SCF9550-30-05 | 30 A, 200 % within 60 s, 80 A breaking | same | |
| gross fault | F1 25 A MINI (297) | 27.5 A holds 360,000 s; 33.75 A opens in 0.75 to 600 s; 1000 A at 32 VDC | same | |
| lid path, forward | LM5069-2, 5.6 mOhm | (none: hard-wired) | **8.7 / 9.8 / 11.0 A** | 2.0 A a BASE cell (the join) |
| lid path, reverse | LM74700-Q1 | (none) | **V(AK) -17 / -11 / -2 mV, under 0.75 us** | no charge from the node |
| board A's end of the lid lead | F_LA, 15 A MINI (297) | (none) | holds 16.5 A (110 %) for 360,000 s; 4.58 mOhm, 270 A2s | the harness, for a double fault |
| lid charge | U3B ChargeCurrent, IIN_HOST | (U3: at most 3.968 A) | **at most 7.936 A; 8.0 A in (8.2 A maximum)** | 2.0 A a cell |

**The lid's prospective fault** (the method `pcb_energy_chain.yaml` uses for board P): 4 x 35 mOhm / 12 + about 15
mOhm of strip and lead = 26.7 mOhm, 630 A at 16.8 V from the AC impedance (the DC figure is lower); inside F1's 1000 A
at 32 VDC. The base 4S6P by the same method: 4 x 35 / 6 + 15 = 38.3 mOhm, 439 A. ESTIMATE, as the source's is.

## 5. How the host sees two gauges and two chargers

- **Base gauge**: as today, board E's sensor controller U10 on its I2C1 (GPIO2 SMBD, GPIO3 SMBC; FW-E01) at the BQ4050's
  default address 0x16 (8-bit form, SLUUAQ3A 12.1, page 73), broadcasts off (SBS Configuration BCAST = 0; with them on
  the gauge would send to 0x12 and 0x14, page 39).
- **Lid gauge: a separate SMBus segment** (authority SESSION; reason: the lid's SMBus crosses the hinge, and a pinched or
  shorted lead on a shared bus would silence the base gauge too, whose host watchdog, HWD 10 s, then stops the base's
  charge, `PRIMARY-CONFIGURATION.md` section 2). Draft for board E: a second pair of U10's GPIOs as a PIO-driven SMBus at
  100 kHz with the same 100 ohm series and clamp parts as J_SMB, a second JST-XH 1x4 **J_SMB2** in board P's pin order,
  and PRES2 on a third GPIO as PRES is. The lid gauge keeps address 0x16 on its own segment. **If U10 has no three free
  GPIOs** (the board E owner's check): the same segment with the lid gauge at a programmed address (SLUUAQ3A 12.1:
  Address and its two's complement in Address Check), 8-bit 0x1A (7-bit 0x0D) proposed, to be checked against the
  SMBus specification's reserved list (not held in the tree), behind a switch that can isolate the lid segment.
- **Chargers**: U3 and U3B are both BQ25731, whose I2C address is fixed at 0x6B (SLUSE66A Device Comparison Table,
  page 4). U3B therefore sits behind a **TI TCA9543A** 2-channel I2C switch (fetched and filed today,
  `v2/vendor/ti/ti-tca9543a.pdf`, SCPS206B; address 1110 0 A1 A0, 0x70 to 0x73 by its pins, 8.6.1 Figure 14, page 14;
  1.65 to 5.5 V; a RESET input frees a stuck downstream bus) at 0x70 on the kit bus, whose map in the tree shows nothing
  at 0x70 to 0x73 (`gen_sch_a/b/c/e.py`, HW-FW-CONTRACT; a search, not a proof: the bus owner confirms). U3B on channel 0,
  channel 1 spare. The panel controller, which configures U3 today, configures U3B through it.

## 6. Fault cases

Energy results are `.out` section 6 (400 Wp, 200 W stage, entry re-rated, base +20 C, lid at 13.23 C unless stated).

| fault | what the hardware does | who acts next | M1 on the model |
|---|---|---|---|
| **lid pack empty** (a long cold spell, or its protection had been open) | its terminal sits below the node, so the ideal diode passes nothing; the base carries the kit | U3B recharges the lid whenever U3's CHRG_OK is up; the host's join rule | from 06 UTC met; from 18 UTC stops at hour 5 (319.5 Wh unserved) |
| **base pack empty** | the base's gauge has opened its discharge FET at CUV; the lid carries the kit through its path, limited at 8.7 to 11.0 A | the host sheds to keep the load under 8.7 A (FW-C09's shedding); U3 recharges the base (CUV_RECOV_CHG) | from 06 met; from 18 stops at hour 8 |
| **lid cold below 0 C** | the lid gauge's UTC (1.0 C) holds its charge FET open, so U3B delivers nothing (it regulates at 16.8 V into an open FET); the lid discharges until UTD (-9.0 C) on the cells' reduced capacity | the host writes U3B's ChargeCurrent 0 on the gauge's ChargingCurrent() of 0; a lid heater is needed for cold operation (open item, section 9) | at -5 C: stops at hour 21 / 10 |
| **base cold below 0 C** | the base gauge holds its charge FET open; U3's ICHG sees no acceptance | the host writes U3's ChargeCurrent 0; U3B still charges a lid at or above 1 C | not run (the base is inside the closed base, REQ-014's +20 C) |
| **lid protection open** (any FET-opening trip, the second level's DOUT, F2 or F1 open) | the lid path sees no source; the ideal diode blocks the node; U3B regulates into nothing | the host reads the lid gauge's flags; on recovery, the join rule | the base alone (4S6P): stops at hour 16 / 5 (section 8's result) |
| **base protection open** | the lid carries through its limited path | as "base pack empty"; on recovery the base (hard-wired) re-joins: if it returns more than 0.20 V below the lid the host disables the lid path until the gap closes | the lid alone: stops at hour 20 / 8 |
| **short across the hinge harness** (LID+ to LID-) | fed by the lid cells through board PL: the AFE's short-circuit comparator opens Q2 in about 183 to 244 us, F1 (1000 A interrupting) backs it; prospective 630 A (section 4). From the node: the ideal diode blocks within its reverse response; U3B limits and stops on its own system-short protection; F_LA backs a double fault | the host sees both lid-side devices lost; the lid gauge records the trip | as "lid protection open" |
| **SMBus lead to the lid damaged** | its segment is separate: the base gauge is unaffected; the lid gauge's HWD (10 s) opens the lid's charge FET, its discharge stays on | the host drops LID_CHG_EN; the lid discharges on its own protection | lid never recharges: like "U3B off", stops at hour 40 / 28 |
| **U3B fault** (off, or a failed switch) | off: the lid only discharges. Two shorted switches (Q7B and Q10B) would join lid and node directly, bypassing the ideal diode: the join is then limited only by the two gauges (OCC1 on either side, 5 and 10 A) | a double fault; the qualified review | U3B off: stops at hour 40 / 28 |
| **Q_LD welded** (the ideal diode's FET shorted) | the node can charge the lid through Q_LS's body diode or channel, unlimited by the LM5069 (it senses forward current); the lid's OCC1 (10 A, 2 s) and its AFE stop a gross case | a single-point failure named for the qualified battery review (D-09) | not run |

## 7. What it asks of board A's entry (the detail is CHARGER.md)

The sun at 400 Wp into a 200 W stage offers the node up to 166.3 W; U3 then delivers up to 166.3 W (load 42.8, base
41.2, U3B 82.3 W; `.out` 7), 8.20 A out of the front end at 20.7 V and 11.47 A out of U3 at 14.5 V. As generated the
front end limits at 5.7 A (118.0 W out), U3's input sense (R16 10 mOhm) caps IIN_HOST at 6.35 A, and U3's L2
(XAL6030-332ME, Isat 12.2 A by its value text) would see a 13.11 A peak at 400 kHz. **With U3's input held under the
front end's limit (IIN_HOST 5.40 A, 111.8 W in) the design case does not meet M1 at a lid of 13.23 C** (it needs the lid
at +17.4 C, or 650 Wp; `.out` 5); with the host contract FW-A16 as written (53.9 W into U3 with the panel on VIN_RAW) it
fails outright. So Option A(i) as the energy record states it needs board A's entry re-rated as well as board E's stage.

## 8. Drafts for the generators' owners (nothing here is applied)

- **`gen_sch_a.py`** (board A): the U3B set of 3b; the lid path of 3c (U_LD, Q_LD, U_LS, Q_LS, R_LS, the UVLO divider,
  the LID_DSG_OFF transistor); F_LA 15 A MINI in a Keystone 3568 holder and the lid lead's entry connector J_LID (XT60
  class, as the base lead's on board E); the TCA9543A at 0x70 with its pull-ups and RESET; the NAND and AND interlock with LID_CHG_EN's pull-down (3b); the entry
  changes of CHARGER.md. New rails LID_IN (lid lead to F_LA, 16.8 V, 11 A), LID_F (behind F_LA), LID_ID (between the
  ideal diode and the switch), VBUS_B (U3B's input, on VBAT), CHB_ACN, LID_CHG (U3B's output to R17B); every one declared
  with its current for the intent checks.
- **`gen_sch_p.py`**: nothing; board PL is a second instance. The golden image is GAUGE.md's.
- **`gen_sch_e.py`** (board E): J_SMB2, the lid SMBus segment on U10's GPIOs, PRES2 (section 5).
- **`pcb_pack_protection.yaml`** (the integrator's): a `pack_lid` section with GAUGE.md's thresholds and the lid path's
  devices; `pcb_energy_chain.yaml`: the lid stages (cells, board PL, harness, F_LA, U_LD, U_LS, VBAT).
- **`HW-FW-CONTRACT.md`** (the integrator's): FW-A02's lid row (U3B ChargeCurrent at most 2 x the lid gauge's
  ChargingCurrent() and at most 7.936 A; the allocation law); FW-A16 revised for the panel (CHARGER.md); FW-E01's twin
  for the lid segment with the x 2 scaling and the IPSCALE2 check; the join rule and LID_DSG_OFF; LID_CHG_EN; FW-P01's
  lid image.

## 9. Assumptions for the mechanical stream (fnd/a1mech) to reconcile, and open items

- **Board PL** is board P's outline (44 x 70 mm as generated; its four-layer regeneration O-11 may change it), mounted in
  the lid module beside the 48 cells with J_CELL, J_TS, J_TS2 and J_SMB as board P's.
- **The hinge harness**: two 12 AWG silicone power conductors (LID+, LID-), one 4-way SMBus lead (board P's JST-XH, 26
  AWG), and a heater pair if the lid gets a heater; **0.6 m each way assumed** (the energy model's loop resistance and
  the join-current bound use it; a longer lead raises the loss and lowers the join current); carries at most 11.0 A
  discharging and 7.936 A charging. Its bend at the hinge, strain relief and flex life are mechanical items.
- **Board A area** for U3B's set, the lid path, F_LA, J_LID, the TCA9543A and the interlock: about 40 x 45 mm (ESTIMATE:
  QFN-32, six 5 x 6 mm FETs, a 10 x 10 mm inductor, three 2512 shunts, a MINI holder, an XT60, small logic). If board A
  has no room, a small daughter board on VBAT near the hinge carries the same circuit (its VBAT feed then carries up to 11
  A out and 8.2 A in).
- **Open**: a heater for the lid pack (the charge window starts at 1 C at the gauge); the lid's temperature under sun
  (the shade rule); the qualified battery review of the whole two-pack design (D-09), including the double faults of
  section 6; TI's answers Q-TI-A1 and Q-TI-A2 (GAUGE.md).
