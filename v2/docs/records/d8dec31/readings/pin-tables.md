
### Board A: every connector pin (pcb-a-power.net, sha256 0a2b59087bcc2678)

56 connector-class parts, 156 pins, of which 82 carry a supply or a signal and 74 are ground.

| connector | pins that carry a supply or a signal (pin: net) | ground pins | class | where the lead goes |
|---|---|---|---|---|
| J_54V | 1: +54V_POE | 2 | INTERNAL | the 54 V lead to board B's PoE injector, inside the case (IF-AB-POWER); the conductor that leaves the case is board B's Ethernet jack, which board B declares |
| J_5V_DEV | 1: +5V_DEV | 2 | INTERNAL | a rail lead to board B, inside the case (IF-AB-POWER) |
| J_5V_S1 | 1: +5V_S1 | 2 | INTERNAL | a rail lead to board B, inside the case (IF-AB-POWER) |
| J_5V_S2 | 1: +5V_S2 | 2 | INTERNAL | a rail lead to board B, inside the case (IF-AB-POWER) |
| J_5V_S3 | 1: +5V_S3 | 2 | INTERNAL | a rail lead to board B, inside the case (IF-AB-POWER) |
| J_AB1 | 1: USB_D8_P; 2: USB_D8_N; 9: PI_SHDN_REQ; 10: PI_KILL; 11: SDA; 12: SCL; 13: EXP_INT; 14: TR_APRS; 15: EMCON_HW; 16: TX_INHIBIT_n; 17: SLOT_EN1; 18: SLOT_EN2; 19: SLOT_EN3; 20: ZEROIZE_HW; 21: SHORE_INHIBIT; 25: USB_E6_P; 26: USB_E6_N | 3 to 8, 22 to 24 | INTERNAL | the control ribbon to board B above this board, inside the case (IF-AB-RIBBON) |
| J_AB2 | 1: USB_WALL_P; 2: USB_WALL_N | 3 to 10 | INTERNAL | the wall-port ribbon to board B, inside the case (IF-AB-WALL): it carries the wall USB pair on from J_USBW, which is declared external and clamped on this board by U29 |
| J_BM1 | 1: RF_VHF | 2 | EXTERNAL, protection claimed off this board, not judged here | the VHF antenna conductor: it crosses this board from the SMA jack J_RF1 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM2 | 1: RF_HF | 2 | EXTERNAL, protection claimed off this board, not judged here | the HF antenna conductor: it crosses this board from the SMA jack J_RF2 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM3 | 1: RF_WIFI24 | 2 | EXTERNAL, protection claimed off this board, not judged here | the WIFI 2.4 antenna conductor: it crosses this board from the SMA jack J_RF3 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM4 | 1: RF_GNSS | 2 | EXTERNAL, protection claimed off this board, not judged here | the GNSS antenna conductor: it crosses this board from the SMA jack J_RF4 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM5 | 1: RF_SDR | 2 | EXTERNAL, protection claimed off this board, not judged here | the SDR antenna conductor: it crosses this board from the SMA jack J_RF5 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM6 | 1: RF_P2PA | 2 | EXTERNAL, protection claimed off this board, not judged here | the WIFI P2P A antenna conductor: it crosses this board from the SMA jack J_RF6 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM7 | 1: RF_P2PB | 2 | EXTERNAL, protection claimed off this board, not judged here | the WIFI P2P B antenna conductor: it crosses this board from the SMA jack J_RF7 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM8 | 1: RF_5G1 | 2 | EXTERNAL, protection claimed off this board, not judged here | the 5G MAIN antenna conductor: it crosses this board from the SMA jack J_RF8 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM9 | 1: RF_5G2 | 2 | EXTERNAL, protection claimed off this board, not judged here | the 5G DIV antenna conductor: it crosses this board from the SMA jack J_RF9 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM10 | 1: RF_IRIDIUM | 2 | EXTERNAL, protection claimed off this board, not judged here | the IRIDIUM antenna conductor: it crosses this board from the SMA jack J_RF10 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_BM11 | 1: RF_LORA | 2 | EXTERNAL, protection claimed off this board, not judged here | the LORA antenna conductor: it crosses this board from the SMA jack J_RF11 to this blind-mate receptacle with no part on it, and leaves through the dock plug and the end wall |
| J_CN1 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_CN2 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_CN3 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_CN4 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_CP1 | 1: CELL+ | none | INTERNAL | the pack's positive over the dock block, from board P by board E's F3, all inside the case (IF-AE-DOCK, IF-PE-PACK); the pack's own protection is on board P |
| J_CP2 | 1: CELL+ | none | INTERNAL | the pack's positive over the dock block, from board P by board E's F3, all inside the case (IF-AE-DOCK, IF-PE-PACK); the pack's own protection is on board P |
| J_CP3 | 1: CELL+ | none | INTERNAL | the pack's positive over the dock block, from board P by board E's F3, all inside the case (IF-AE-DOCK, IF-PE-PACK); the pack's own protection is on board P |
| J_CP4 | 1: CELL+ | none | INTERNAL | the pack's positive over the dock block, from board P by board E's F3, all inside the case (IF-AE-DOCK, IF-PE-PACK); the pack's own protection is on board P |
| J_DOCK | 8: SHORE_INHIBIT; 9: USB_E6_P; 10: USB_E6_N; 12: DOCK_SPARE | 1 to 7, 11 | INTERNAL | signals between board A and board E inside the case, through the dock block E5 (interface contract IF-AE-DOCK): SHORE_INHIBIT on pin 8, the sensor controller's USB pair on pins 9 and 10, the hot stop line HOT-R1 on pin 12; the other pins are ground |
| J_HEAT | 1: VHEAT | 2 | INTERNAL | the pack heater mat in the pack bay, inside the case (IF-A-HEAT) |
| J_HF | 1: +12V_HF | 2 | INTERNAL | 12 V to the QMX HF unit in the lid tray, in the lid harness (IF-LID-HF). The lead stays inside the case; the unit's own panel is touched by the operator, and what reaches this lead through the unit is recorded in the review of decision 31 as not judged at the desk |
| J_MAINSW | 1: MAIN_PB | 2 | EXTERNAL, protected off this board (read on board C's netlist) | the MAIN button's lead from the panel: a person presses the button on the face, and its contact reaches the LTC2954's PB pin on this board |
| J_MEZZ1 | 1: USB_D8_P; 2: USB_D8_N; 7: TR_APRS; 8: TX_INHIBIT_n; 9: PA_EN; 10: SDA; 11: SCL; 12: EXP_INT; 13: +3V3; 15: ZEROIZE_HW; 16: AB_SPARE | 3 to 6, 14 | INTERNAL | the mezzanine harness to board D, inside the case (IF-AD-HARNESS) |
| J_MEZZ_PWR1 | 1: +5V_D8 | 2 | INTERNAL | board D's 5 V lead behind the eFuse U23, inside the case (IF-AD-HARNESS) |
| J_MON | 1: VMON | 2 | INTERNAL | the supply lead of the Xenarc monitor on the face, behind the eFuse U21 (IF-MON). The lead stays inside the case; the monitor's glass and bezel are touched by the operator, and what reaches this lead through the monitor is recorded in the review of decision 31 as not judged at the desk |
| J_PA | 1: +13V8_PA | 2 | INTERNAL | 13.8 V to the power amplifier module on the inside of the face plate (IF-A-PA); the lead stays inside the case |
| J_PRE1 | 1: PRECHG | none | INTERNAL | the pre-charge pin of the pack's positive over the dock block, inside the case: it mates first and reaches CELL+ through R1 (10 R) |
| J_RF1 | 1: RF_VHF | 2 | INTERNAL | the SMA jack of the pigtail to the VHF radio inside the case: the same conductor as J_BM1, which is declared external, and no part of this board is on it |
| J_RF2 | 1: RF_HF | 2 | INTERNAL | the SMA jack of the pigtail to the HF radio inside the case: the same conductor as J_BM2, which is declared external, and no part of this board is on it |
| J_RF3 | 1: RF_WIFI24 | 2 | INTERNAL | the SMA jack of the pigtail to the WIFI 2.4 radio inside the case: the same conductor as J_BM3, which is declared external, and no part of this board is on it |
| J_RF4 | 1: RF_GNSS | 2 | INTERNAL | the SMA jack of the pigtail to the GNSS radio inside the case: the same conductor as J_BM4, which is declared external, and no part of this board is on it |
| J_RF5 | 1: RF_SDR | 2 | INTERNAL | the SMA jack of the pigtail to the SDR radio inside the case: the same conductor as J_BM5, which is declared external, and no part of this board is on it |
| J_RF6 | 1: RF_P2PA | 2 | INTERNAL | the SMA jack of the pigtail to the WIFI P2P A radio inside the case: the same conductor as J_BM6, which is declared external, and no part of this board is on it |
| J_RF7 | 1: RF_P2PB | 2 | INTERNAL | the SMA jack of the pigtail to the WIFI P2P B radio inside the case: the same conductor as J_BM7, which is declared external, and no part of this board is on it |
| J_RF8 | 1: RF_5G1 | 2 | INTERNAL | the SMA jack of the pigtail to the 5G MAIN radio inside the case: the same conductor as J_BM8, which is declared external, and no part of this board is on it |
| J_RF9 | 1: RF_5G2 | 2 | INTERNAL | the SMA jack of the pigtail to the 5G DIV radio inside the case: the same conductor as J_BM9, which is declared external, and no part of this board is on it |
| J_RF10 | 1: RF_IRIDIUM | 2 | INTERNAL | the SMA jack of the pigtail to the IRIDIUM radio inside the case: the same conductor as J_BM10, which is declared external, and no part of this board is on it |
| J_RF11 | 1: RF_LORA | 2 | INTERNAL | the SMA jack of the pigtail to the LORA radio inside the case: the same conductor as J_BM11, which is declared external, and no part of this board is on it |
| J_USBC_OUT | 1: PD_VBUS; 2: PD_CC1; 3: PD_CC2 | 4, 5 | EXTERNAL | the USB-C outlet on the connector plate, out of the case: VBUS meets D4 (SMBJ18A) and CC1 and CC2 meet U31 (TPD2E2U06QDBZRQ1, the owner's D-17 array) at the connector, and port_protect judges both |
| J_USBW | 1: VBUS_WALL; 2: USB_WALL_N; 3: USB_WALL_P | 4 | EXTERNAL | the wall USB host port through the MIL-DTL-38999 receptacle: a person plugs a stranger's stick into this |
| J_VN1 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_VN2 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_VN3 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_VN4 | none | 1 | carries no conductor | a return: every pin is on GND |
| J_VR1 | 1: VIN_RAW | none | EXTERNAL | shore and vehicle DC (VIN_RAW) arriving over the dock from board E, which takes it from the wall receptacle: one of the four 9 A power pins that carry VIN_RAW since session choice SC-55 (EQ-16, 27 September 2026). Until then the entry named J_DOCK pins 1 and 2, which are ground since, so it judged nothing. D2 (SMCJ40A) sits on these pins' own net |
| J_VR2 | 1: VIN_RAW | none | EXTERNAL | shore and vehicle DC (VIN_RAW) arriving over the dock from board E, which takes it from the wall receptacle: one of the four 9 A power pins that carry VIN_RAW since session choice SC-55 (EQ-16, 27 September 2026). Until then the entry named J_DOCK pins 1 and 2, which are ground since, so it judged nothing. D2 (SMCJ40A) sits on these pins' own net |
| J_VR3 | 1: VIN_RAW | none | EXTERNAL | shore and vehicle DC (VIN_RAW) arriving over the dock from board E, which takes it from the wall receptacle: one of the four 9 A power pins that carry VIN_RAW since session choice SC-55 (EQ-16, 27 September 2026). Until then the entry named J_DOCK pins 1 and 2, which are ground since, so it judged nothing. D2 (SMCJ40A) sits on these pins' own net |
| J_VR4 | 1: VIN_RAW | none | EXTERNAL | shore and vehicle DC (VIN_RAW) arriving over the dock from board E, which takes it from the wall receptacle: one of the four 9 A power pins that carry VIN_RAW since session choice SC-55 (EQ-16, 27 September 2026). Until then the entry named J_DOCK pins 1 and 2, which are ground since, so it judged nothing. D2 (SMCJ40A) sits on these pins' own net |

Not connectors, and on no lead: test points (25: TP3 to TP27).


### Board D: every connector pin (pcb-d-aprs.net, sha256 7a2c0ac2190b141a)

10 connector-class parts, 42 pins, of which 26 carry a supply or a signal and 16 are ground.

| connector | pins that carry a supply or a signal (pin: net) | ground pins | class | where the lead goes |
|---|---|---|---|---|
| J_ANT | 1: RF_ANT | 2 | EXTERNAL, protection claimed off this board, not judged here | the VHF antenna SMA: an outdoor conductor with a 30 W transmitter behind it, arrested in the wall rather than on the board |
| J_FLANGE | 1: FLANGE_NTC | 2 | INTERNAL | the thermistor lead of the power amplifier's flange, inside the case (IF-D-FLANGE) |
| J_HARN1 | 1: USB_D8_P; 2: USB_D8_N; 7: TR_APRS; 8: TX_INHIBIT_n; 9: PA_EN; 10: SDA; 11: SCL; 12: EXP_INT; 13: +3V3; 15: ZEROIZE_HW; 16: AB_SPARE | 3 to 6, 14 | INTERNAL | the mezzanine harness from board A, inside the case (IF-AD-HARNESS) |
| J_HS1 | 1: HS1_SPK; 3: HS1_MIC; 5: PTT_HS1_n | 2, 4 | EXTERNAL | a headset jack on the face, which a person plugs a headset into |
| J_HS2 | 1: HS2_SPK; 3: HS2_MIC; 5: PTT_HS2_n | 2, 4 | EXTERNAL | the second headset jack |
| J_PAIN | 1: RF_DRV | 2 | INTERNAL | the drive coax to the power amplifier module on the inside of the face plate (IF-A-PA) |
| J_PAOUT | 1: RF_PAOUT | 2 | EXTERNAL, protection claimed off this board, not judged here | the power amplifier output to the antenna path, which reaches the same arrested bulkhead |
| J_PWR1 | 1: +5V_D8 | 2 | INTERNAL | the 5 V lead from board A's eFuse U23, inside the case (IF-AD-HARNESS) |
| J_USB3 | 1: +5V_D8; 2: USB3_N; 3: USB3_P | 4 | INTERNAL | the touch USB lead of the Xenarc monitor on the face (IF-MON, session choice SC-HF-06). The lead stays inside the case; the monitor's glass and bezel are touched by the operator, no clamp stands on this pair, and the review of decision 31 records it as finding D-F3, not judged at the desk |
| J_VGG | 1: VGG_SW | 2 | INTERNAL | the gate bias lead to the power amplifier module on the inside of the face plate (IF-A-PA) |

Not connectors, and on no lead: solder jumpers (2: JP1 to JP2); the relay (1: K1); indicator LEDs on the board (6: LED1 to LED6); test points (27: TP1 to TP27).


### Board E: every connector pin (pcb-e1-dock.net, sha256 56adc9746d61c4e0)

18 connector-class parts, 51 pins, of which 32 carry a supply or a signal and 19 are ground.

| connector | pins that carry a supply or a signal (pin: net) | ground pins | class | where the lead goes |
|---|---|---|---|---|
| J_BATT | 2: CELL+ | 1 | INTERNAL | the pack's power lead from board P on its XT60, inside the case (IF-PE-PACK); the pack's own protection is on board P |
| J_BLK | 8: SHORE_INHIBIT; 9: USB_E6_P; 10: USB_E6_N; 12: BLK_SPARE | 1 to 7, 11 | INTERNAL | the twelve signal wires to the dock block E5 and through it to board A, inside the case (IF-AE-DOCK): SHORE_INHIBIT, the sensor controller's USB pair and the hot stop line HOT-R1 |
| J_DCF | 1: +3V3_E6; 3: DCF_PULSE | 2 | INTERNAL | the DCF77 receiver module beside this board, inside the case (IF-E-SENSORS) |
| J_DCIN | 1: DC_IN | 2 | EXTERNAL | shore and vehicle DC entry from the MIL-DTL-38999 wall receptacle |
| J_FAN1 | 1: CELL_F; 2: FAN1_SW; 3: FAN1_TACH | none | INTERNAL | mixer fan 1 under the plate, inside the sealed case (IF-E-FANS) |
| J_FAN2 | 1: CELL_F; 2: FAN2_SW; 3: FAN2_TACH | none | INTERNAL | mixer fan 2 under the plate, inside the sealed case (IF-E-FANS) |
| J_GEIGER | 1: +5V_GEIGER; 3: GEIGER_PULSE | 2 | INTERNAL | the Geiger counter module beside this board, inside the case (IF-E-SENSORS) |
| J_LTG | 1: +3V3_E6; 3: SDA1; 4: SCL1; 5: LTG_IRQ | 2 | INTERNAL | the lightning sensor module beside this board, inside the case (IF-E-SENSORS). It shares the sensor bus SDA1 and SCL1 with the outside pod J_POD, which is declared external |
| J_POD | 1: +3V3_E6; 3: SDA1; 4: SCL1 | 2 | EXTERNAL | the outside climate and ultraviolet sensor pod, through an M8 sealed receptacle on the connector plate |
| J_SMB | 1: SMBC; 2: SMBD; 4: PRES_LEAD | 3 | INTERNAL | the SMBus lead to board P's gauge, inside the case (IF-PE-PACK) |
| J_SOLAR | 1: PV_IN | 2 | EXTERNAL | the solar input, a long outdoor lead by definition |
| J_TAMP | 1: TAMPER_LEAD | 2 | INTERNAL | the lid and tamper reed sensor's lead under the frame, inside the case (IF-E-TAMP) |
| PAD_W1 | 1: WATER_A | none | INTERNAL | water electrode A on the case floor, bare copper under the plate, inside the sealed case (IF-E-WATER): fed from +3V3_E6 through R38 (1 M) |
| PAD_W2 | 1: WATER_SENSE | none | INTERNAL | water electrode B on the case floor, bare copper under the plate, inside the sealed case (IF-E-WATER): into the sensor controller's ADC0 past R39 (1 M) and C51 (100 nF) |
| P_CN | none | 1 | carries no conductor | a return: every pin is on GND |
| P_CP | 1: CELL_F | none | INTERNAL | the pack's positive to the dock block E5 on a 12 AWG wire, inside the case (IF-AE-DOCK) |
| P_VN | none | 1 | carries no conductor | a return: every pin is on GND |
| P_VR | 1: VIN_RAW | none | INTERNAL | VIN_RAW to the dock block E5 on a 12 AWG wire, inside the case (IF-AE-DOCK): the bus behind this board's own entry protection, which board A declares external at J_VR1 to J_VR4 |

Not connectors, and on no lead: solder jumpers (1: JP1); indicator LEDs on the board (2: LED1 to LED2); test points (13: TP1 to TP13).

