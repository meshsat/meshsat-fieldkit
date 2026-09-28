## Board A, v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json: 4 commit(s) since e3aedb25
  c0133147 fix(v2): board A gates its PA and HF rails on both EMCON lines, with decision 42's decoupling and the part codes its makers list [MESHSAT-1357]
  ffca0771 fix(pcb-a): the PoE and USB-C enables get their own EN/UVLO node, the EMCON gates run behind their own eFuse, and PWR-001 reads PASS on board A [MESHS
  b7f96784 fix(pcb-d,pcb-e): declare the supplies PWR-001 refused, sense the tracker's current on its bottom leg, and carry VIN_RAW across the dock on power pins
  c4ad8350 feat(boards-a-e): the hot stop line HOT-R1 drawn on boards A and E, and board E's fan flyback sheet filed so PWR-001 reads PASS there [MESHSAT-1357]
  - VIN_RAW          (12.31, 12.31) -> (14.1, 14.1), first in b7f96784
      note: shore, vehicle and panel input from E6 over the dock: board E's vehicle entry (LM5069 U6, 6.15 A at VCL max, 10 A fuse) and its panel tracker (TRK_OUT, 6.16 A) ORed onto one bus, 12.31 A together at those two figures (third fix-up of round 4, 26 September 2026, reconciled with board E's F-IN-02), declared at board E's 14.10 A since R8E-N01 (27 September 2026: this board's front end at its ISNS limit drawing from a 9.0 V bus, R4A-N12) and crossing the dock on the Mill-Max power pins J_VR1 to J_VR4 (EQ-16); the current enters the front end at Q2's drain and the input caps (the LM5176 U2 draws only its bias: a load named U2 put 8 A into two QFN pins and read 3.3 percent, 32.69)
  - PRECHG           None -> (0.0, 1.68), first in ffca0771
      note: the pre-charge pin's conductor to R1 (10 Ohm) and CELL+: 1.68 A at most, the pack's 16.8 V into a discharged node, decaying as CELL+ charges; 0 A once the main pins have mated
  - VMON             None -> (0.69, 1.0), first in ffca0771
      note: the Xenarc 709GNK monitor's supply behind the eFuse U21 (limit 1.2 A, MON_EN), out at the J_MON lead: 10 W at most (maker's manual), 0.69 A at 14.4 V and 1.0 A at the monitor's 10 V floor
  - +3V3_EMCON_EF    None -> (0.0004, 0.002), first in ffca0771
      note: EQ-17, 27 September 2026: the EMCON gates' supply behind the eFuse U39 (OVLO cut at 3.83 to 4.11 V of +3V3, EN on RAIL_EN), before its 100 R filter R213
  - +3V3_EMCON       None -> (0.0004, 0.002), first in ffca0771
      note: EQ-17, 27 September 2026: the four SN74AUP1G08 EMCON gates' own supply behind R213, with their four 100 nF and the software holds' 10 k pull-ups R214 and R215

## Board B, v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json: 3 commit(s) since e3aedb25
  b76c18cb fix(pcb-b): the bank fabric breaks before it makes on a locked sequence, and EMCON runs on each module's own rail and removes the 5G supply in hardwar
  caba1876 fix(pcb-b): every supply of board B declared for PWR-001 from its maker's sheet, decision 42's class and basis on every decoupling entry, the TPS23861
  910da406 fix(board-b): EMCON forces the RockBLOCK's ENABLE low, holds the radio switches off in their gates' supply band and drives each card rail's enable fro
  - VBUS_FLASH1      None -> (1e-08, 1.5e-07), first in caba1876
      note: slot 1's flashing receptacle VBUS: it feeds only the USBLC6-2SC6's VBUS reference (pin 5), at most 150 nA at VRM 5.25 V (ST DS4260 Rev 7, p.2); the module is powered from the slot rail, never from this
  - SIM1_VCC         None -> (0.01, 0.05), first in caba1876
      note: SIM 1's supply from the module's USIM1_VDD (1.8 or 3.0 V by card class, HD v1.1 pin table) to the holder J_SIM1 and the ESD array U222's VCC; 50 mA peak INFERRED from SIMCom's figure for the same output (A7672X/A7670X HD V1.03), the RM520N HD giving none; declared at 3.3 V worst like the card lines
  - SIM2_VCC         None -> (0.01, 0.05), first in caba1876
      note: SIM 2's supply from the module's USIM2_VDD (1.8 or 3.0 V by card class, HD v1.1 pin table) to R272, the eSIM option link at the module (HD 4.1.6 Figure 19); 50 mA peak INFERRED from SIMCom's figure for the same output (A7672X/A7670X HD V1.03), the RM520N HD giving none; declared at 3.3 V worst like the card lines
  - SIMC2_VCC        None -> (0.01, 0.05), first in caba1876
      note: SIM 2's supply at the holder, past the 0 Ohm eSIM option link R272: the same current as SIM2_VCC, to J_SIM2 and the ESD array U223's VCC (ICC at most 100 nA, SLLS682P 5.5)
  - VBUS_FLASH2      None -> (1e-08, 1.5e-07), first in caba1876
      note: slot 2's flashing receptacle VBUS: it feeds only the USBLC6-2SC6's VBUS reference (pin 5), at most 150 nA at VRM 5.25 V (ST DS4260 Rev 7, p.2); the module is powered from the slot rail, never from this
  - VBUS_FLASH3      None -> (1e-08, 1.5e-07), first in caba1876
      note: slot 3's flashing receptacle VBUS: it feeds only the USBLC6-2SC6's VBUS reference (pin 5), at most 150 nA at VRM 5.25 V (ST DS4260 Rev 7, p.2); the module is powered from the slot rail, never from this
  - VBAT_RTC         None -> (8e-06, 0.00065), first in caba1876
      note: the CR2032's 3 V to the three modules' RTC inputs (pin 76), the DS3231SN's VBAT (pin 14) and the LG290P's V_BCKP (pin 22): about 8 uA with everything powered (3 x 1.7 + 3 + 0.1), 650 uA at the coincident worst (a DS3231 temperature conversion), 3 x 6 + 3.0 + 57 = 78 uA with the kit stored
  - POE_P            None -> (0.3, 0.6), first in caba1876
      note: the port's positive feed from the 0 Ohm link R13 to T1's centre tap MCT1 (pin 24), a series segment of +54V_POE at the port's 0.60 A peak; VVPWR at most 57 V (SLUSBX9I 6.3)
  - MDI_A_P          None -> (0.15, 0.3), first in caba1876
      note: half the port's feed from T1's cable-side winding to the jack's pin 1 (802.3 Alternative A, pair 1-2): a series segment of POE_P carrying half its current, and a 1000BASE-T signal conductor
  - MDI_A_N          None -> (0.15, 0.3), first in caba1876
      note: half the port's feed from T1's cable-side winding to the jack's pin 2 (802.3 Alternative A, pair 1-2): a series segment of POE_P carrying half its current, and a 1000BASE-T signal conductor
  - MDI_B_P          None -> (0.15, 0.3), first in caba1876
      note: half the port's return from the jack's pin 3 into T1's cable-side winding (pair 3-6), at the sense voltage with the port on (0.60 A x 0.25 Ohm) and up to 57 V with it off; the TPS23861 turns the port on through Q1's gate, POE_GATE; also a 1000BASE-T signal conductor
  - MDI_B_N          None -> (0.15, 0.3), first in caba1876
      note: half the port's return from the jack's pin 6 into T1's cable-side winding (pair 3-6), at the sense voltage with the port on (0.60 A x 0.25 Ohm) and up to 57 V with it off; the TPS23861 turns the port on through Q1's gate, POE_GATE; also a 1000BASE-T signal conductor
  - POE_DRAIN        None -> (0.3, 0.6), first in caba1876
      note: the port's return from T1's centre tap MCT2 (pin 21) to the drain of the port switch Q1, with the TPS23861's DRAIN1 monitor on it through R526: near the sense voltage with the port on, up to 57 V with it off (the FET's drain is the one node the powered device lifts)
  - POE_SEN          None -> (0.3, 0.6), first in caba1876
      note: the port's return from Q1's source to the 0.25 Ohm sense resistor R12: 0.15 V at 0.60 A, and the part cuts the port at VSHORT2X, 357 to 408 mV (SLUSBX9I 6.5), so a part on it sees at most 0.41 V; the TPS23861's SEN1 reads it through R525
  - GNSS_VDD_RF      None -> (0.02, 0.03), first in caba1876
      note: the active antenna's supply from the LG290P's VDD_RF to R23; 20 mA typical and 30 mA peak INFERRED (no held antenna datasheet states it); an antenna short is bounded by R23, 3.3 V / 10 Ohm, a fault current
  - GNSS_BIAS        None -> (0.02, 0.03), first in caba1876
      note: the antenna feed between R23 (the maker's short-circuit resistor R2) and the bias inductor L3: a series segment of GNSS_VDD_RF
  - GNSS_ANT         None -> (0.02, 0.03), first in caba1876
      note: the antenna feed from L3 to the U.FL J_GNSS1, shared with the RF the antenna returns (DC-blocked from RF_IN by C42): a series segment of GNSS_VDD_RF

## Board C, v2/ecad/pcb-c-display-c8/out/pcb-c-display-intent.json: 2 commit(s) since e3aedb25
  9f28c238 fix(pcb-c): one-way EMCON read, hardware EMCON lamp and per-pin decoupling with the maker's clause on every entry [MESHSAT-1357]
  e28f91a6 fix(board-c): TX_INHIBIT_n fails safe with the panel unpowered (R14 2.2k, R50 10k), PWR-001 declarations with +3V3 covering EPD_VCC, and the RAIL_SENS
  - +3V3             (0.12, 0.2) -> (0.149, 0.72), first in e28f91a6
      note: the panel's logic 3.3 V from the LDO U5: the RP2040 controller, its QSPI flash, the two expanders, the buffers, the EMCON lamp's gate, the light sensor and the e-paper's supply switch. Budget 3 percent, because every load is a logic part with a wide supply range. Since 27 September 2026 (W4C-F5) the figures cover the child EPD_VCC: its own loads' 0.119 A typical and 0.199 A peak plus EPD_VCC's 0.030 and 0.521 A, because within each boost on-phase (about 1.6 us) Q5 carries most of the inductor's current (C28 behind Q5 is a 0.40 us time constant). U5 is rated 500 mA (TI SBVS320D): the excess at the peak is 0.35 uC per on-phase, 24 mV on C2, C28 and C29 at most; U5's average through a refresh is an open item read at bring-up
  - EPD_VCC          None -> (0.03, 0.521), first in e28f91a6
      note: the e-paper's switched supply: Q5 (AO3401A) from +3V3 to the panel's VDDIO and VDD and to the boost inductor L1. 30 mA typical = the UC8253c's 20.2 mA operating maximum (IVDD 0.1, IVDDIO 0.1, IVDDA 20.0 mA at 3.0 V and 25 C, UltraChip UC8253c A0.6 page 59) plus 10 mA INFERRED for the boost, read at bring-up; 0.5 A peak into L1 = the boost switch's current class (PDi Rev.02 page 4 note 1). Budget 3 percent as +3V3's: the driver's supply range is 2.3 to 3.6 V (UC8253c page 59)
  - LED_RAIL_SW      None -> (0.1593, 0.4619), first in e28f91a6
      note: the lighting supply behind the LIGHTING toggle: Q1 to LED_RAIL, the EMCON lamp D22 through R47, the MAIN ring through R39, Q1's gate pull-up R17 and the sense divider R15 and R51. Typical: the lamps at their design currents; peak: every lamp with no forward drop at 5.25 V. Budget 5 percent as +5V's: every load is a lamp behind its own resistor
  - LED_RAIL         None -> (0.144, 0.437), first in e28f91a6
      note: the PWM'd lamp rail: Q1 (AO3401A) from LED_RAIL_SW, its gate Q1_G pulled down through R18 by Q2 from PANEL_PWM; 18 lamps behind their series resistors, 8 mA each by design, 0.437 A with every lamp's forward drop at zero at 5.25 V

## Board D, v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs-intent.json: 3 commit(s) since e3aedb25
  76235aad fix(v2): board D powers its transmit chain only while its EMCON gates are in range, reads the PA flange temperature, and fits the TPA6132A2's 2.2 uF [
  b7f96784 fix(pcb-d,pcb-e): declare the supplies PWR-001 refused, sense the tracker's current on its bottom leg, and carry VIN_RAW across the dock on power pins
  932cf9d7 fix(boards): board D's flyback diode ordered with its sheet, board P's supplies declared with the fuse gate bounded by TI's 6 V drive, BAT-001's table
  - +5V_TX           None -> (0.37, 1.15), first in 76235aad
      note: the transmit chain's 5 V behind the TPS22810 load switch U21 (TI SLVSDH0C): on while +3V3_D8 is above 2.23 to 2.78 V (EN/UVLO divider R90 11k over R91 10k, VENR 1.13 to 1.30 V and VENF 1.08 to 1.18 V, 7.5), off below the switch's own VIN UVLO (VUVR 2.00 to 2.62 V, 7.5). RON at most 105 mOhm at 5 V to +85 C (7.5): 0.12 V at the 1.15 A peak. Budget 3 percent for this rail's copper; its loads regulate or tolerate a wide range (the exciter 3.3 to 5.5 V behind FB1, U15 only lower in dropout, the relay's must-operate 4.0 V, 80 percent of its 5 V coil)

## Board E, v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock-intent.json: 3 commit(s) since e3aedb25
  bc0f562f fix(v2): board E declares its raw bus from both feeds, classes every decoupling capacitor and fits the four its makers ask for, regenerated with parit
  b7f96784 fix(pcb-d,pcb-e): declare the supplies PWR-001 refused, sense the tracker's current on its bottom leg, and carry VIN_RAW across the dock on power pins
  c4ad8350 feat(boards-a-e): the hot stop line HOT-R1 drawn on boards A and E, and board E's fan flyback sheet filed so PWR-001 reads PASS there [MESHSAT-1357]
  - VIN_RAW          (6.15, 6.15) -> (14.1, 14.1), first in bc0f562f
      note: the raw bus to the dock block: the vehicle and shore entry after the filter choke (L2 pad 3, 10 A fuse) AND the panel tracker through its ideal diode (Q2's drain), ORed on the same copper to P_VR, the 12 AWG pad to the dock's four VIN_RAW power pins (EQ-16, 27 September 2026; until then J_BLK pins 1 to 4). Declared at 14.10 A typical and peak (R4A-N12, 26 September 2026): board A's front end at its ISNS limit (5.7 A at 20.7 V, 0.93) drawing from a 9.0 V bus, which the two feeds can supply together (vehicle up to 6.15 A at U6's VCL max, tracker 10.33 A at the panel's 93 W). The vehicle path alone stays 6.15 A (F-IN-02) and its five segments are declared at that. THIS BOARD'S SHARE is 0.5 of the rail's 2 percent (16 September 2026): the entry, the choke and the dock block are a short run on this strip and measured 0.16 percent at the old 8 A, while board A carries the same current from the
  - TRK_OUT          (6.16, 6.16) -> (10.33, 10.33), first in bc0f562f
      note: the LT8705A tracker's regulated output, set by R10 and R11 (115k over 10.0k), carrying the panel's 100 W into the pack bus through the ideal diode U4. Declared at 10.33 A typical and peak (R4A-N12, 26 September 2026): the panel's 93 W at the 9 V bus floor, when a vehicle holds the bus under 15.1 V; 6.16 A is the figure at 15.1 V. volts x amps therefore overstates the power (93 W at any bus voltage)
  - SGP_VDD          None -> (0.0046, 0.0046), first in b7f96784
      note: the SGP41's VDD behind its RC element (R57 4.7 Ohm, C57 1 uF; Sensirion SGP41 v1.0 2.5 and Figure 6), declared at the whole part's 4.6 mA maximum (Table 2, VDD and VDDH together at 3.3 V), which bounds this pin's share; R57 drops at most 22 mV at it

## Board P, v2/ecad/pcb-p-pack-p2/out/pcb-p-pack-intent.json: 2 commit(s) since e3aedb25
  7bef62bd fix(pcb-p): pack headers order the JST parts the catalogues list, supply filters declare class A, FET bypass pair read from TI [MESHSAT-1357]
  932cf9d7 fix(boards): board D's flyback diode ordered with its sheet, board P's supplies declared with the fuse gate bounded by TI's 6 V drive, BAT-001's table
  - BAT_F            None -> (0.00034, 0.00034), first in 932cf9d7
      note: U1's primary supply (SLUSC67B pin 32, 'Primary power supply input pin'): 336 uA typical in NORMAL mode (6.5; no maximum stated), 75 and 52 uA in SLEEP, 1.6 uA in SHUTDOWN; R5 100 ohm and C6 100 nF are the board's own filter (R8P-05, a question for the qualified battery review)
  - VCC_F            None -> (0.0, 0.00034), first in 932cf9d7
      note: U1's secondary supply (SLUSC67B pin 26, 'Secondary power supply input'), from the pack terminal through R7 1 kohm: it takes over below BAT's 1.95 to 2.2 V switchover (6.6), so its typical current is zero and its peak the gauge's 336 uA NORMAL current (6.5); live whenever PACK_P is, which the gauge's DSG drive switches (PACK_P's declaration) or a charger holds up. TI's figure feeds VCC from the FETs' common drain through 100 ohm; this board's PACK_P feed is the difference R8P-05 puts to the qualified battery review
  - SEC_VDD          None -> (3.5e-06, 0.00018), first in 932cf9d7
      note: U2's supply (SLUSEG7D pin 1 VDD; RVD 300 ohm and CVD 100 nF, Table 8-1): ICC 3.5 uA at most without a fault, 25 uA at most with one (6.5), plus the COUT and DOUT drive while a fault holds them high, about 88 uA into the fuse gate divider and 60 uA into R28; 0.18 mA declared as the peak
  - SW               None -> (10.0, 18.0), first in 932cf9d7
      note: the common drain of Q1 and Q2 (CSD17570Q5B, TI SLPS471D), the pack's whole current: 10 A typical and 18 A peak as SCP_OUT and PACK_P carry it; discharge current enters through Q1 (its channel, or its body diode while the gauge holds CHG off: BAT-F20, S-46, open) and leaves through Q2, and charge current the other way
  - SCP_HTR          None -> (3.5, 3.5), first in 932cf9d7
      note: the chemical fuse's heater return (Eaton SCF9550-30-05, ELX1135: heater 4.8 to 8.0 ohm, operating 10.5 to 23.5 V, opens the fuse within 60 s): 1.3 to 3.5 A for up to 60 s while Q3 (AO3400A) is on, zero otherwise; declared at 3.5 A typical as well as peak because a 60 s event is a steady state for copper

