#!/usr/bin/env python3
"""PCB-D APRS MEZZANINE, phase D8 (MESHSAT-830; appendix 32.56 PA on the plate, 32.57 device set, 32.59): generate the KiCad 9 schematic (netlist
style: every pin gets a stub and a net label; GND pins get power symbols). Runs where the KiCad symbol libraries are (the vast.ai box).
Usage: gen_sch_d.py <out.kicad_sch> <project>

The mezzanine sits on A22's standoffs (case X 0..100, Y -40..40) and is a USB device set of the kit: A22's J_MEZZ1 harness brings one USB 2.0 pair,
the kit I2C bus, the hardware inhibit TX_INHIBIT_n (the panel's EMCON toggle), the PA rail state PA_EN and the PTT mirror TR_APRS; J_MEZZ_PWR1 brings
5 V (2 A eFuse on A22). On the board: a TUSB2046B four-port hub (port 1 the PCM2912A USB audio codec, port 2 a CP2102N bridge to the SA868's UART with
RTS as the software PTT, port 3 a spare header), the NiceRF SA868 VHF exciter (bench-fitted, 2 W high / 0.5 W low), a G6K-2F-Y DPDT T/R relay,
a 10 dB pad to the PA drive lead, the PA output lead into a 5-element low-pass filter and the antenna SMA (pigtail to A22's VHF jack), the PA gate
bias switched by a TPS22810 on PA_KEY, a TPA6132A2 headphone amplifier driving the two headset leads (U-174/U jacks on the face plate) with the
receive audio and the codec's playback, a TLV9062 microphone summing preamplifier into the exciter's MIC_IN together with the codec's transmit audio,
the PTT logic in single-gate 74LVC1G parts (KEY = any PTT AND TX_INHIBIT_n; PA_KEY = KEY AND PA_EN), a PCA9555 at 0x26 on the kit I2C bus (harness
+3V3, level stages into the mezzanine's own 3.3 V domain), LEDs and test points. The RA30H1317M1 PA module bolts to the face plate (32.56): its
13.8 V comes from A22's J_PA lead directly, its drive and output coax and its VGG lead from this board's north edge.
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-d-aprs"
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
# 10 September 2026 (MESHSAT-862, red team C2): the schematic engine lives in kisch.py, one copy for the six boards.
# What stays here is this board: its part tables, its nets, its sheet layout. `ic()` is strict for every board again.
import kisch
from kisch import (U, c, emit_part, emit_pwr_flag, ensure, esd, extents, find_sym, flatten, flatten_raw, ic, label, lib_tree, noconn, parse, part, pins_of, place_symbol, q, r, rename_units, ser, synth_symbol, text, tps22810, uq, usb_c_recept, wire)
import intent as _intent
_intent.rail("+5V_D8", 5.0, 1.0, 2.0, "J_PWR1", budget=0.03, note="the mezzanine's 5 V from A22. Budget 3 percent, not the 2 percent default: every consumer either regulates this rail or tolerates a wide range (the TLV75533 3.3 V LDO with 1.5 V of headroom, the CP2102N bridge at a 4.0 V minimum, the ESD reference, and the exciter's own boost behind FB1). D10 measures 108 mV at 1.0 A, 2.16 percent, leaving 4.89 V at the tightest consumer (9 September 2026).")
SYMDIR = "/usr/share/kicad/symbols/"

# ----------------------------------------------------------------- s-expression helpers (as B13/B15)
LIBCACHE = {}

# ----------------------------------------------------------------- synthetic box symbols (parts with no library symbol): odd pins left, even pins right
# NiceRF SA868 (V1.x manual, 18 castellations); TI PCM2912A (SLES230A, TQFP-32); TI TPA6132A2 (SLOS553, QFN-16, pin 17 the pad); TI TUSB2046B (SLLS413L, LQFP-32);
# Silicon Labs CP2102N QFN28 (as B16)
SA868 = {1: "AUDIO_ON_n", 2: "NC", 3: "AF_OUT", 4: "NC", 5: "PTT_n", 6: "PD", 7: "H/L", 8: "VBAT", 9: "GND", 10: "GND", 11: "NC", 12: "ANT", 13: "NC", 14: "NC", 15: "NC", 16: "RXD", 17: "TXD", 18: "MIC_IN"}
PCM2912A = {1: "BGND", 2: "VBUS", 3: "D-", 4: "D+", 5: "VDD", 6: "DGND", 7: "XTO", 8: "XTI", 9: "FL", 10: "FR", 11: "VCOM1", 12: "VCOM2", 13: "AGND", 14: "NC", 15: "VCCA", 16: "VIN", 17: "MBIAS", 18: "VOUTL",
            19: "VCCL", 20: "HGND", 21: "VCCR", 22: "VOUTR", 23: "MAMP", 24: "POWER", 25: "PGND", 26: "VCCP", 27: "TEST1", 28: "TEST0", 29: "SSPND", 30: "MMUTE", 31: "REC", 32: "PLAY"}
TPA6132A2 = {1: "INL-", 2: "INL+", 3: "INR+", 4: "INR-", 5: "OUTR", 6: "G0", 7: "G1", 8: "HPVSS", 9: "CPN", 10: "PGND", 11: "CPP", 12: "HPVDD", 13: "EN", 14: "VDD", 15: "SGND", 16: "OUTL", 17: "PAD"}
TUSB2046B = {1: "DP0", 2: "DM0", 3: "VCC", 4: "RESET_n", 5: "EECLK", 6: "EEDATA/GANGED", 7: "GND", 8: "BUSPWR", 9: "PWRON1_n", 10: "OVRCUR1_n", 11: "DM1", 12: "DP1", 13: "PWRON2_n", 14: "OVRCUR2_n", 15: "DM2", 16: "DP2",
             17: "PWRON3_n", 18: "OVRCUR3_n", 19: "DM3", 20: "DP3", 21: "PWRON4_n", 22: "OVRCUR4_n", 23: "DM4", 24: "DP4", 25: "VCC", 26: "EXTMEM", 27: "TSTPLL/48MCLK", 28: "GND", 29: "XTAL2", 30: "XTAL1", 31: "TSTMODE", 32: "SUSPND"}
CP2102 = {1:"DCD",2:"RI_CLK",3:"GND",4:"D+",5:"D-",6:"VDD",7:"VREGIN",8:"VBUS",9:"RSTb",10:"NC",11:"SUSPENDb",12:"SUSPEND",13:"CHREN",14:"CHR1",15:"CHR0",16:"GPIO3",17:"GPIO2",18:"GPIO1",19:"GPIO0",20:"GPIO6",21:"GPIO5",22:"GPIO4",23:"CTS",24:"RTS",25:"RXD",26:"TXD",27:"DSR",28:"DTR",29:"GND"}
SYNTH = {"SA868": SA868, "PCM2912A": PCM2912A, "TPA6132A2": TPA6132A2, "TUSB2046B": TUSB2046B, "CP2102N": CP2102}

# ----------------------------------------------------------------- footprints
FP = {
 "R": "Resistor_SMD:R_0603_1608Metric", "R2010": "Resistor_SMD:R_2010_5025Metric", "C": "Capacitor_SMD:C_0603_1608Metric", "C0402": "Capacitor_SMD:C_0402_1005Metric",
 "C10u": "Capacitor_SMD:C_0805_2012Metric", "C1206": "Capacitor_SMD:C_1206_3216Metric", "C1210": "Capacitor_SMD:C_1210_3225Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "SOT23": "Package_TO_SOT_SMD:SOT-23", "SOT235": "Package_TO_SOT_SMD:SOT-23-5", "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "WSON6": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
 "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "IDC16": "Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical",
 "TP": "TestPoint:TestPoint_Pad_D1.5mm", "QFN28": "Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm", "TQFP32": "Package_QFP:TQFP-32_7x7mm_P0.8mm", "LQFP32": "Package_QFP:LQFP-32_7x7mm_P0.8mm",
 "QFN16": "Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.75x1.75mm", "VSSOP8": "Package_SO:VSSOP-8_3x3mm_P0.65mm", "TSSOP24": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
 "SA868": "meshsat:NiceRF_SA868", "RELAY": "Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y", "SMA": "Connector_Coaxial:SMA_Amphenol_132134_Vertical", "UFL": "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical",
 "L1812": "Inductor_SMD:L_1812_4532Metric", "L0805": "Inductor_SMD:L_0805_2012Metric",
 "FB": "Inductor_SMD:L_0805_2012Metric", "SOD123": "Diode_SMD:D_SOD-123", "SMB": "Diode_SMD:D_SMB",
 "PH2": "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", "PH4": "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical", "PH5": "Connector_JST:JST_PH_B5B-PH-K_1x05_P2.00mm_Vertical",
 "JP": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
}
kisch.configure(fp=FP, synth=SYNTH)   # the engine needs the tables before the first part
P = kisch.P                           # one list, shared with the engine (not a copy)
def synth(ref, name, value, fp, nets, lcsc=""):
    full = {str(k): nets.get(k, nets.get(str(k), "NC")) for k in SYNTH[name]}
    part(ref, "Connector_Generic", name, value, fp, full, lcsc)
def led(ref, colour, anode, cathode): part(ref, "Device", "LED", colour, "LED", {"2": anode, "1": cathode})
def nfet(ref, gate, source, drain, value="2N7002"): part(ref, "Transistor_FET", "2N7002", value, "SOT23", {"1": gate, "2": source, "3": drain}, "C8545")   # 1 G 2 S 3 D (SOT-23 order, appendix 32.36)
def level(ref, rn, far, near, near_rail, far_rail=None, rf=None):
    """Bidirectional 2N7002 stage between a module-domain line (near, pulled up to the module's rail) and the always-on side (far); the module off = gate low, nothing flows."""
    nfet(ref, near_rail, near, far); r(rn, "10k", near, near_rail)
    if far_rail: r(rf, "10k", far, far_rail)
def tps2065(ref, rail, en, out, flt): part(ref, "Power_Management", "TPS2065CDBV", "TPS2065CDBV", "SOT235", {"5": rail, "4": en, "1": out, "3": flt, "2": "GND"})
def cp2102(uref, tag, vusb, dp, dm, txd, rxd, rts="NC", dtr="NC", refs=()):
    """CP2102N-A02-GQFN28 bridge: bus sense and regulator input from the slot rail whose hub carries it, its own 3.3 V out (VDD) bypassed, RSTb pulled to VDD."""
    synth(uref, "CP2102N", "CP2102N-A02-GQFN28 USB-UART bridge (%s)" % tag, "QFN28", {3: "GND", 29: "GND", 4: dp, 5: dm, 6: tag + "_3V3", 7: vusb, 8: vusb, 9: tag + "_RST", 25: rxd, 26: txd, 24: rts, 28: dtr}, "C964632")
    rr, c1, c2 = refs
    r(rr, "1k", tag + "_RST", tag + "_3V3"); c(c1, "4.7u", tag + "_3V3", "GND", "C10u"); c(c2, "100n", tag + "_3V3", "GND")


# ================================================================= the design (nets are root-sheet labels; GND is the only power symbol)
# --- harness and power entry (A22 J_MEZZ1 mirror, J_MEZZ_PWR1 5 V behind A22's 2 A eFuse U23)
# 10 September 2026 (MESHSAT-862): USB_D8 moves to pins 3/4, one column of the header with ground on both sides; it was on
# pins 2/3, which are diagonal neighbours 3.59 mm apart. A22's J_MEZZ1 carries the same map (check_contracts.py compares them).
part("J_HARN1", "Connector_Generic", "Conn_02x08_Odd_Even", "A22 mezzanine harness J_MEZZ1 (IDC 2x8): USB pair, PTT mirror, inhibit, PA rail state, I2C, 3.3 V", "IDC16", {
 "1": "GND", "2": "GND", "3": "USB_D8_P", "4": "USB_D8_N", "5": "GND", "6": "GND", "7": "TR_APRS", "8": "TX_INHIBIT_n", "9": "PA_EN", "10": "SDA", "11": "SCL", "12": "EXP_INT", "13": "+3V3", "14": "GND", "15": "ZEROIZE_HW", "16": "AB_SPARE"})
part("J_PWR1", "Connector_Generic", "Conn_01x02", "5 V from A22 J_MEZZ_PWR1 (JST-VH, 2 A eFuse on A22): + -", "VH2", {"1": "+5V_D8", "2": "GND"})
part("D1", "Device", "D_TVS", "SMBJ5.0A", "SMB", {"1": "GND", "2": "+5V_D8"})
c("C1", "47u 6.3V X5R 1210", "+5V_D8", "GND", "C1210"); c("C2", "47u 6.3V X5R 1210", "+5V_D8", "GND", "C1210"); c("C3", "10u", "+5V_D8", "GND", "C10u"); c("C4", "100n", "+5V_D8", "GND")
part("FB1", "Device", "FerriteBead", "600R 2A ferrite (the exciter's 1 A transmit pulses)", "FB", {"1": "+5V_D8", "2": "+5V_SA"})
c("C5", "47u 6.3V X5R 1210", "+5V_SA", "GND", "C1210"); c("C6", "100n", "+5V_SA", "GND")
ic("U1", 5, "TLV75533PDBV 3.3 V 500 mA LDO (1 IN 2 GND 3 EN 4 NC 5 OUT)", "SOT235", {"1": "+5V_D8", "2": "GND", "3": "+5V_D8", "4": "NC", "5": "+3V3_D8"})
c("C7", "1u", "+5V_D8", "GND"); c("C8", "1u", "+3V3_D8", "GND"); c("C9", "10u", "+3V3_D8", "GND", "C10u")
led("LED1", "green power", "LED_PWR_A", "GND"); r("R1", "2.2k", "+3V3_D8", "LED_PWR_A")
r("R2", "100k", "TX_INHIBIT_n", "GND"); r("R3", "100k", "PA_EN", "GND")   # a disconnected harness reads inhibited and PA off
# --- the SA868 exciter (bench-fitted): PD from the expander (default on), H/L pulled low by PA_EN (0.5 W into the pad when the PA rail is up; 2 W to the antenna without the PA)
synth("U2", "SA868", "NiceRF SA868 VHF 2 W exciter, bench-fitted (castellated; VBAT 3.3 to 5.5 V, TX 1 A)", "SA868",
      {1: "SA_AUDIO_ON_n", 3: "AF_OUT", 5: "SA_PTT_n", 6: "SA_PD", 7: "SA_HL", 8: "+5V_SA", 9: "GND", 10: "GND", 12: "RF_SA", 16: "SA_RXD", 17: "SA_TXD", 18: "MIC_IN"})
nfet("Q1", "PA_EN", "GND", "SA_HL", "2N7002 PA_EN -> H/L low (never tie H/L high)")
cp2102("U3", "SAU", "+5V_D8", "USB2_P", "USB2_N", "SA_RXD", "SA_TXD", rts="PTT_SW_n", refs=("R4", "C10", "C11"))   # the bridge's TXD into the exciter's RXD; RTS low = software PTT
r("R5", "10k", "PTT_SW_n", "+3V3_D8")
# --- USB hub TUSB2046B (self-powered, no EEPROM, 6 MHz crystal): upstream from the harness pair, port 1 the codec, port 2 the bridge, port 3 a spare header, port 4 terminated
esd("U5", "USB_D8_P", "USB_D8_N", "+5V_D8")
r("R6", "22", "USB_D8_P", "HUB_DP0"); r("R7", "22", "USB_D8_N", "HUB_DM0"); r("R8", "1.5k", "HUB_DP0", "+3V3_D8")
synth("U4", "TUSB2046B", "TUSB2046BI four-port USB 2.0 full-speed hub (LQFP-32; BUSPWR low = self-powered, EXTMEM high, GANGED high, TSTMODE low)", "LQFP32",
      {1: "HUB_DP0", 2: "HUB_DM0", 3: "+3V3_D8", 25: "+3V3_D8", 4: "HUB_RST_n", 6: "+3V3_D8", 7: "GND", 28: "GND", 8: "GND", 10: "HUB_OVRCUR_n", 14: "HUB_OVRCUR_n", 18: "HUB_OVRCUR_n", 22: "HUB_OVRCUR_n",
       11: "HUB_DM1", 12: "HUB_DP1", 15: "HUB_DM2", 16: "HUB_DP2", 19: "HUB_DM3", 20: "HUB_DP3", 23: "HUB_DM4", 24: "HUB_DP4", 26: "+3V3_D8", 27: "GND", 29: "HUB_XTAL2", 30: "HUB_XTAL1", 31: "GND"})
r("R9", "10k", "HUB_OVRCUR_n", "+3V3_D8"); r("R10", "10k", "HUB_RST_n", "+3V3_D8"); c("C12", "1u", "HUB_RST_n", "GND")
part("Y1", "Device", "Crystal_GND24", "6 MHz 3225 (CL 20 pF; C1 = C2 = 27 pF and Rd 1.5k per SLLS413 figure 6)", "XTAL", {"1": "HUB_XTAL1", "3": "HUB_XTAL2R", "2": "GND", "4": "GND"})
r("R11", "1.5k", "HUB_XTAL2R", "HUB_XTAL2"); c("C13", "27p NP0", "HUB_XTAL1", "GND", "C0402"); c("C14", "27p NP0", "HUB_XTAL2R", "GND", "C0402")
c("C15", "100n", "+3V3_D8", "GND"); c("C16", "100n", "+3V3_D8", "GND"); c("C17", "10u", "+3V3_D8", "GND", "C10u")
for port, (dp, dm, tp, tm, rs) in {1: ("HUB_DP1", "HUB_DM1", "USB1_P", "USB1_N", 12), 2: ("HUB_DP2", "HUB_DM2", "USB2_P", "USB2_N", 16), 3: ("HUB_DP3", "HUB_DM3", "USB3_P", "USB3_N", 20)}.items():
    r("R%d" % rs, "22", dp, tp); r("R%d" % (rs + 1), "22", dm, tm); r("R%d" % (rs + 2), "15k", tp, "GND"); r("R%d" % (rs + 3), "15k", tm, "GND")
r("R24", "15k", "HUB_DP4", "GND"); r("R25", "15k", "HUB_DM4", "GND")
part("J_USB3", "Connector_Generic", "Conn_01x04", "spare hub port 3 (JST-PH 1x4): 5V D- D+ GND", "PH4", {"1": "+5V_D8", "2": "USB3_N", "3": "USB3_P", "4": "GND"})
# --- USB audio codec PCM2912A (VBUS 5 V, its regulator feeds VDD and the VCC pins: decoupling only; MAMP off = line level, POWER low, TEST1 high, TEST0 low)
r("R26", "33", "USB1_P", "USB1_PR"); r("R27", "33", "USB1_N", "USB1_NR"); r("R28", "1.5k", "USB1_PR", "PCM_VDD")
synth("U6", "PCM2912A", "TI PCM2912A USB audio codec (TQFP-32): mono input from the exciter, stereo output to the headphone amplifier and the transmit sum", "TQFP32",
      {1: "GND", 2: "+5V_D8", 3: "USB1_NR", 4: "USB1_PR", 5: "PCM_VDD", 6: "GND", 7: "PCM_XTO", 8: "PCM_XTI", 11: "PCM_VCOM1", 12: "PCM_VCOM2", 13: "GND", 15: "PCM_VCCA", 16: "PCM_VIN", 18: "PCM_VOUTL",
       19: "PCM_VCCL", 20: "GND", 21: "PCM_VCCR", 22: "PCM_VOUTR", 23: "GND", 24: "GND", 25: "GND", 26: "PCM_VCCP", 27: "PCM_VDD", 28: "GND", 30: "MMUTE", 31: "LED_REC_K", 32: "LED_PLAY_K"})
c("C18", "1u", "+5V_D8", "GND"); c("C19", "1u", "PCM_VDD", "GND"); c("C20", "1u", "PCM_VCCA", "GND"); c("C21", "1u", "PCM_VCCL", "GND"); c("C22", "1u", "PCM_VCCR", "GND"); c("C23", "1u", "PCM_VCCP", "GND")
c("C24", "10u", "PCM_VCOM1", "GND", "C10u"); c("C25", "10u", "PCM_VCOM2", "GND", "C10u")
part("Y2", "Device", "Crystal_GND24", "6 MHz 3225 (codec clock; 18 pF loads, to confirm on the EVM sheet)", "XTAL", {"1": "PCM_XTI", "3": "PCM_XTO", "2": "GND", "4": "GND"})
c("C26", "18p NP0", "PCM_XTI", "GND", "C0402"); c("C27", "18p NP0", "PCM_XTO", "GND", "C0402")
led("LED2", "amber record", "LED_REC_A", "LED_REC_K"); r("R29", "1k", "+3V3_D8", "LED_REC_A"); led("LED3", "green playback", "LED_PLAY_A", "LED_PLAY_K"); r("R30", "1k", "+3V3_D8", "LED_PLAY_A")
r("R31", "10k", "AF_OUT", "AF_DIV"); r("R32", "10k", "AF_DIV", "GND"); c("C28", "1u", "AF_DIV", "PCM_VIN")   # 700 mV receive audio halved into the ADC
r("R33", "4.7k", "X_MMUTE", "MMUTE"); r("R34", "100k", "MMUTE", "GND")   # mute only when the expander drives it high (the codec pulls it down itself)
# --- headphone amplifier TPA6132A2 (G0 high, G1 low = 0 dB): the receive mix (exciter AF_OUT + codec playback L) to both headset earpieces
synth("U7", "TPA6132A2", "TI TPA6132A2 headphone amplifier (QFN-16), receive audio to the two headset leads", "QFN16",
      {1: "AMP_INL_N", 2: "AMP_INL_P", 3: "AMP_INR_P", 4: "AMP_INR_N", 5: "HS2_SPK", 6: "+3V3_D8", 7: "GND", 8: "AMP_HPVSS", 9: "AMP_CPN", 10: "GND", 11: "AMP_CPP", 12: "AMP_HPVDD", 13: "AMP_EN", 14: "+5V_D8", 15: "GND", 16: "HS1_SPK", 17: "GND"})
c("C29", "1u", "AMP_HPVSS", "GND"); c("C30", "1u", "AMP_CPP", "AMP_CPN"); c("C31", "1u", "AMP_HPVDD", "GND"); c("C32", "1u", "+5V_D8", "GND"); c("C33", "10u", "+5V_D8", "GND", "C10u")
r("R35", "10k", "AF_OUT", "RX_MIX"); c("C34", "1u", "PCM_VOUTL", "PCM_L_AC"); r("R36", "10k", "PCM_L_AC", "RX_MIX"); r("R37", "10k", "RX_MIX", "GND")
c("C35", "1u", "RX_MIX", "AMP_INL_P"); c("C36", "1u", "RX_MIX", "AMP_INR_P"); c("C37", "1u", "AMP_INL_N", "GND"); c("C38", "1u", "AMP_INR_N", "GND")
# --- microphone summing preamplifier TLV9062 (33 dB, both headset microphones; electret bias by solder jumper) into the exciter's MIC_IN with the codec's transmit audio (R)
ic("U8", 8, "TLV9062IDGK dual op amp (1 OUT1 2 IN1- 3 IN1+ 4 V- 5 IN2+ 6 IN2- 7 OUT2 8 V+): A the mic sum, B unused as a follower", "VSSOP8",
   {"1": "MICAMP_OUT", "2": "MICAMP_IN_N", "3": "VREF", "4": "GND", "5": "VREF", "6": "OPB_OUT", "7": "OPB_OUT", "8": "+5V_D8"})
c("C39", "100n", "+5V_D8", "GND"); r("R38", "10k", "+5V_D8", "VREF"); r("R39", "10k", "VREF", "GND"); c("C40", "10u", "VREF", "GND", "C10u")
c("C41", "1u", "HS1_MIC", "HS1_MIC_AC"); r("R40", "4.7k", "HS1_MIC_AC", "MICAMP_IN_N"); c("C42", "1u", "HS2_MIC", "HS2_MIC_AC"); r("R41", "4.7k", "HS2_MIC_AC", "MICAMP_IN_N")
r("R42", "220k", "MICAMP_OUT", "MICAMP_IN_N"); c("C43", "100p NP0", "MICAMP_OUT", "MICAMP_IN_N", "C0402")
part("JP1", "Jumper", "SolderJumper_2_Open", "electret bias headset 1 (close for an electret microphone)", "JP", {"1": "HS1_MIC", "2": "HS1_BIAS_R"}); r("R43", "2.2k", "HS1_BIAS_R", "+5V_D8")
part("JP2", "Jumper", "SolderJumper_2_Open", "electret bias headset 2", "JP", {"1": "HS2_MIC", "2": "HS2_BIAS_R"}); r("R44", "2.2k", "HS2_BIAS_R", "+5V_D8")
c("C44", "1n NP0", "HS1_MIC", "GND", "C0402"); c("C45", "1n NP0", "HS2_MIC", "GND", "C0402")   # RF bypass beside a 30 W transmitter
c("C46", "1u", "MICAMP_OUT", "MICAMP_AC"); r("R45", "10k", "MICAMP_AC", "MIC_SUM"); c("C47", "1u", "PCM_VOUTR", "PCM_R_AC"); r("R46", "10k", "PCM_R_AC", "MIC_SUM"); r("R47", "10k", "MIC_SUM", "GND"); c("C48", "1u", "MIC_SUM", "MIC_IN")
# --- headset leads to the face plate's two U-174/U jacks (JST-PH 1x5): SPK GND MIC GND PTT
part("J_HS1", "Connector_Generic", "Conn_01x05", "headset 1 lead (JST-PH 1x5 to the face plate U-174/U jack): SPK GND MIC GND PTT", "PH5", {"1": "HS1_SPK", "2": "GND", "3": "HS1_MIC", "4": "GND", "5": "PTT_HS1_n"})
part("J_HS2", "Connector_Generic", "Conn_01x05", "headset 2 lead (JST-PH 1x5 to the face plate U-174/U jack): SPK GND MIC GND PTT", "PH5", {"1": "HS2_SPK", "2": "GND", "3": "HS2_MIC", "4": "GND", "5": "PTT_HS2_n"})
c("C49", "100n", "PTT_HS1_n", "GND"); c("C50", "100n", "PTT_HS2_n", "GND")
# --- PTT and EMCON logic (74LVC1G, 3.3 V): KEY = (PTT headset 1 OR 2 OR software) AND TX_INHIBIT_n; the exciter keys on KEY; PA_KEY = KEY AND PA_EN drives the relay and the gate bias switch
ic("U9", 5, "74LVC1G08 AND (1 A 2 B 3 GND 4 Y 5 VCC): both headset PTT lines idle high", "SOT235", {"1": "PTT_HS1_n", "2": "PTT_HS2_n", "3": "GND", "4": "PTT_HS_n", "5": "+3V3_D8"})
ic("U10", 5, "74LVC1G08 AND: headsets AND software PTT (RTS)", "SOT235", {"1": "PTT_HS_n", "2": "PTT_SW_n", "3": "GND", "4": "PTT_ANY_n", "5": "+3V3_D8"})
ic("U11", 5, "74LVC1G04 inverter (2 A 4 Y): PTT_ANY", "SOT235", {"1": "NC", "2": "PTT_ANY_n", "3": "GND", "4": "PTT_ANY", "5": "+3V3_D8"})
ic("U12", 5, "74LVC1G08 AND: KEY = PTT_ANY AND TX_INHIBIT_n (the panel's hardware EMCON)", "SOT235", {"1": "PTT_ANY", "2": "TX_INHIBIT_n", "3": "GND", "4": "KEY", "5": "+3V3_D8"})
ic("U13", 5, "74LVC1G04 inverter: KEY -> SA868 PTT (low = transmit)", "SOT235", {"1": "NC", "2": "KEY", "3": "GND", "4": "SA_PTT_n", "5": "+3V3_D8"})
ic("U14", 5, "74LVC1G08 AND: PA_KEY = KEY AND PA_EN (A22's PA rail state)", "SOT235", {"1": "KEY", "2": "PA_EN", "3": "GND", "4": "PA_KEY", "5": "+3V3_D8"})
# one 100 nF per gate, tied to its gate as data so the decoupling gate measures the loop instead of trusting the schematic order
# (8 Sep 2026: the note below that these six gates carried no bypass capacitor was wrong, the capacitors existed since D8; what was
# missing was the intent entry, so no gate ever measured the distance on the chain that keys a 30 W transmitter)
for _i, _u in enumerate(("U9", "U10", "U11", "U12", "U13", "U14")): c("C%d" % (51 + _i), "100n", "+3V3_D8", "GND", bypass=(_u, "5"))
r("R48", "100", "KEY", "TR_APRS")   # the PTT mirror to A22 (100k pull-down there): the TX lamp follows the real key line
led("LED4", "red transmit", "LED_TX_A", "GND"); r("R49", "1k", "KEY", "LED_TX_A"); led("LED5", "amber PA keyed", "LED_PA_A", "GND"); r("R50", "1k", "PA_KEY", "LED_PA_A")
led("LED6", "green receive (AUDIO_ON low)", "LED_RX_A", "SA_AUDIO_ON_n"); r("R51", "2.2k", "+3V3_D8", "LED_RX_A")
# --- T/R relay G6K-2F-Y (5 V coil; top view pins 8 7 6 5 over 1 2 3 4: coil 1 (+) 8 (-), pole 3-2-4 and 6-7-5 with 2 and 7 the rest contacts):
#     rest: exciter ANT (3) -> 2 = RX node = 7 -> 6 = antenna SMA (receive, and the exciter's 2 W direct when the PA is off); keyed with the PA: 3 -> 4 = pad -> PA drive, PA output -> LPF -> 5 -> 6
part("K1", "Relay", "G6K-2", "Omron G6K-2F-Y 5 VDC DPDT signal relay, T/R", "RELAY", {"1": "+5V_D8", "8": "RLY_K", "3": "RF_SA", "2": "RF_RX", "4": "RF_PAD_IN", "6": "RF_ANT", "7": "RF_RX", "5": "RF_LPF_OUT"})
nfet("Q2", "RLY_DRV", "GND", "RLY_K", "2N7002 relay coil"); r("R52", "1k", "PA_KEY", "RLY_DRV"); r("R53", "100k", "RLY_DRV", "GND")
part("D2", "Diode", "1N4148W", "1N4148W coil flyback", "SOD123", {"1": "+5V_D8", "2": "RLY_K"}); c("C57", "100n", "+5V_D8", "GND")
r("R54", "27 1% 2010", "RF_PAD_IN", "RF_PAD_M", "R2010"); r("R55", "36 1% 2010", "RF_PAD_M", "GND", "R2010"); r("R56", "27 1% 2010", "RF_PAD_M", "RF_DRV", "R2010")   # 10 dB T-pad, 0.5 W in, 50 mW to the PA
part("J_PAIN", "Connector", "Conn_Coaxial", "PA drive (U.FL, coax to the RA30H1317M1 input on the plate)", "UFL", {"1": "RF_DRV", "2": "GND"})
part("J_PAOUT", "Connector", "Conn_Coaxial", "PA output (SMA, coax from the RA30H1317M1 output on the plate)", "SMA", {"1": "RF_PAOUT", "2": "GND"})
# L1 and L2 leave the 1812 land. The IMC1812EB68NK they were drawn as is rated 450 mA and the
# 30 W PA puts about 775 mA RMS through this filter (sqrt(30/50) into a matched load), so the
# part was under-rated for its own job independently of being out of stock, and every other
# 68 nH in 1812 is the same 450 mA family. The Murata LQW2BAN68NG00L is 1.2 A and 2 percent,
# which a fifth-order corner wants, at 120 mW of dissipation in its 200 mOhm. Confirm the
# current under a mismatched antenna when MESHSAT-818 simulates this filter.
c("C58", "22p 500V NP0 1206", "RF_PAOUT", "GND", "C1206"); part("L1", "Device", "L", "68nH 0805 (LPF, 145 MHz 5th order; values to be verified in MESHSAT-818)", "L0805", {"1": "RF_PAOUT", "2": "RF_LPF_M"})
c("C59", "39p 500V NP0 1206", "RF_LPF_M", "GND", "C1206"); part("L2", "Device", "L", "68nH 0805 (LPF)", "L0805", {"1": "RF_LPF_M", "2": "RF_LPF_OUT"}); c("C60", "22p 500V NP0 1206", "RF_LPF_OUT", "GND", "C1206")
part("J_ANT", "Connector", "Conn_Coaxial", "antenna (SMA, pigtail to A22's VHF jack J_RF1)", "SMA", {"1": "RF_ANT", "2": "GND"})
tps22810("U15", "+5V_D8", "PA_KEY", "VGG_SW", "VGG_CT"); c("C61", "4.7n", "VGG_CT", "GND", "C0402"); c("C62", "100n", "VGG_SW", "GND")
part("J_VGG", "Connector_Generic", "Conn_01x02", "PA gate bias lead (JST-PH 1x2 to the RA30H1317M1 VGG): VGG GND", "PH2", {"1": "VGG_SW", "2": "GND"})
# --- expander PCA9555 0x26 on the kit bus (harness +3V3) with 2N7002 level stages into the mezzanine's 3.3 V domain
part("U16", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x26: COS, PTT states, KEY, PA_KEY in; exciter PD, amplifier EN, codec mute out; eight spares", "TSSOP24", {
 "1": "EXP_INT", "2": "+3V3", "3": "+3V3", "21": "GND", "22": "SCL", "23": "SDA", "24": "+3V3", "12": "GND",
 "4": "X_COS_n", "5": "X_PTT_HS1_n", "6": "X_PTT_HS2_n", "7": "X_KEY", "8": "X_PA_KEY", "9": "X_SA_PD", "10": "X_AMP_EN", "11": "X_MMUTE",
 "13": "EXP_SPARE1", "14": "EXP_SPARE2", "15": "EXP_SPARE3", "16": "EXP_SPARE4", "17": "EXP_SPARE5", "18": "EXP_SPARE6", "19": "EXP_SPARE7", "20": "EXP_SPARE8"})
c("C63", "100n", "+3V3", "GND")
for i, (far, near) in enumerate((("X_COS_n", "SA_AUDIO_ON_n"), ("X_PTT_HS1_n", "PTT_HS1_n"), ("X_PTT_HS2_n", "PTT_HS2_n"), ("X_KEY", "KEY"), ("X_PA_KEY", "PA_KEY"), ("X_SA_PD", "SA_PD"), ("X_AMP_EN", "AMP_EN")), 3):
    level("Q%d" % i, "R%d" % (60 + 2 * i), far, near, "+3V3_D8", "+3V3", "R%d" % (61 + 2 * i))
for i, net in enumerate(("AF_OUT", "MIC_SUM", "KEY", "PA_KEY", "+3V3_D8", "+5V_D8", "VGG_SW", "RX_MIX", "ZEROIZE_HW", "AB_SPARE", "SA_TXD", "SA_RXD", "PTT_SW_n", "SA_PD", "TX_INHIBIT_n", "PA_EN") + tuple("EXP_SPARE%d" % k for k in range(1, 9)), 1):
    part("TP%d" % i, "Connector", "TestPoint", net, "TP", {"1": net})
for i, net in enumerate(("+5V_D8", "+5V_SA", "+3V3_D8", "+3V3", "GND", "PCM_VDD", "SAU_3V3"), 1): part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})
# ----------------------------------------------------------------- emit (as B15)
POWER = {"GND": ("power", "GND")}
libsyms = kisch.libsyms; out = kisch.out; pf_n = kisch.pf_n   # the engine's objects, by reference
ROOT = str(uuid.uuid5(kisch.UUID_NS, "root:" + PROJECT))   # deterministic: a board regenerates byte for byte (10 Sep 2026)
STUB = 5.08
kisch.configure(power=POWER, stub=STUB, root=ROOT, project=PROJECT, seed=PROJECT)
byref = {p["ref"]: p for p in P}

def refs_matching(pred): return [p["ref"] for p in P if pred(p["ref"])]
SECTIONS = [("HARNESS, 5 V ENTRY, 3.3 V LDO, EXCITER SUPPLY", ["J_HARN1", "J_PWR1", "D1", "C1", "C2", "C3", "C4", "FB1", "C5", "C6", "U1", "C7", "C8", "C9", "LED1", "R1", "R2", "R3"]),
            ("SA868 EXCITER, UART BRIDGE, T/R RELAY, 10 dB PAD, LPF, PA LEADS, GATE BIAS SWITCH", ["U2", "Q1", "U3", "R4", "C10", "C11", "R5", "K1", "Q2", "R52", "R53", "D2", "C57", "R54", "R55", "R56", "J_PAIN", "J_PAOUT", "C58", "L1", "C59", "L2", "C60", "J_ANT", "U15", "C61", "C62", "J_VGG"]),
            ("USB HUB TUSB2046B, PORT TERMINATIONS, SPARE PORT", ["U5", "R6", "R7", "R8", "U4", "R9", "R10", "C12", "Y1", "R11", "C13", "C14", "C15", "C16", "C17"] + ["R%d" % k for k in range(12, 26)] + ["J_USB3"]),
            ("USB AUDIO CODEC PCM2912A, HEADPHONE AMPLIFIER, MIC PREAMP, HEADSET LEADS", ["R26", "R27", "R28", "U6"] + ["C%d" % k for k in range(18, 28)] + ["Y2", "LED2", "R29", "LED3", "R30", "R31", "R32", "C28", "R33", "R34", "U7"] + ["C%d" % k for k in range(29, 34)] +
             ["R35", "C34", "R36", "R37", "C35", "C36", "C37", "C38", "U8", "C39", "R38", "R39", "C40", "C41", "R40", "C42", "R41", "R42", "C43", "JP1", "R43", "JP2", "R44", "C44", "C45", "C46", "R45", "C47", "R46", "R47", "C48", "J_HS1", "J_HS2", "C49", "C50"])]
placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}
SECTIONS.append(("PTT AND EMCON LOGIC, PTT MIRROR, LEDS, EXPANDER 0x26 WITH LEVEL STAGES, TEST POINTS, FLAGS", [p["ref"] for p in P if p["ref"] not in placed_refs]))
def layout(page_h):
    global out, pf_n
    out = kisch.reset_body(); placed = set(); COLW = 92.0; x = 20.0; y = 30.0
    for title, refs in SECTIONS:
        hs = []
        for ref in refs:
            p = byref[ref]; x0, x1, y0, y1 = extents(ensure(p["lib"], p["sym"])); hs.append((y1 - y0) + 2 * STUB + 12.0)
        if y + 20 > page_h and y > 30.0: x += COLW; y = 30.0
        text(title, round((x - 15.0) / 1.27) * 1.27, round((y - 4.0) / 1.27) * 1.27); y += 4.0
        for ref, h in zip(refs, hs):
            p = byref[ref]; x0, x1, y0, y1 = extents(ensure(p["lib"], p["sym"]))
            if y + h > page_h: x += COLW; y = 34.0
            cy = y + (y1 + STUB) + 4.0; gx = round((x + 20.0) / 1.27) * 1.27; gy = round(cy / 1.27) * 1.27
            if p["sym"] == "PWR_FLAG": emit_pwr_flag(p, gx, gy)
            else: emit_part(p, gx, gy)
            placed.add(ref); y += h
        y += 8.0
    missing = [p["ref"] for p in P if p["ref"] not in placed]
    if missing: raise SystemExit("unplaced parts: %s" % missing)
    return x + COLW
max_x = layout(800.0); PAPER = "A0"
print("layout width %.0f mm -> paper %s (A0 landscape is 1189 wide; the schematic PDF is a netlist record, not a drawing)" % (max_x, PAPER))
hdr = '(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "%s")\n\t(paper "%s")\n' % (ROOT, PAPER)
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-D APRS MEZZANINE") (date "2026-09-07") (rev "A") (company "MeshSat") (comment 1 "Phase D8 schematic (SA868 exciter, T/R relay and low-pass filter, the 30 W PA on the face plate, USB audio and control set; appendix 32.56, 32.57, 32.59), generated by tools/gen_sch_d.py"))\n'
hdr += '\t(lib_symbols\n' + "".join("\t\t" + ser(v, 2).replace("\n", "\n\t\t") + "\n" for v in libsyms.values()) + '\t)\n'
body = "".join("\t" + s.replace("\n", "\n\t").rstrip("\t") for s in out)
open(OUT, "w").write(hdr + body + '\t(sheet_instances (path "/" (page "1")))\n)\n')
print("wrote", OUT, "parts:", len(P), "lib symbols:", len(libsyms))
nets = {}
for p in P:
    for num, net in p["nets"].items():
        if net != "NC": nets.setdefault(net, []).append("%s.%s" % (p["ref"], num))
single = [n for n, v in nets.items() if len(v) == 1]
print("nets:", len(nets), "single-pin nets (should be empty or intentional):", single)

# --- decoupling as data (8 Sep 2026, MESHSAT-862 Stage C): which capacitor serves which supply pin, so `intent_checks.py` can measure the
# pad-to-pin distance and the loop instead of trusting that the schematic order means anything. Read out of this file's own order (each
# capacitor sits directly after the part it serves) and filtered to supply pins: crystal loads, reset networks, the codec's VCOM reservoirs
# and the amplifier's charge-pump and input capacitors are not decoupling and are not listed. intent.py refuses an entry whose capacitor is
# not on that pin's net, so a wrong line here stops the generator.
# CORRECTED 8 Sep 2026: an earlier note here said U9 to U14 had no bypass capacitor. They do, C51 to C56, one per gate, and they are
# now declared above with their gate so the proximity rule reaches them; the placement is what has to be judged, not the count.
_intent.bypass("C7", "U1", "1", "+5V_D8")
_intent.bypass("C8", "U1", "5", "+3V3_D8")
_intent.bypass("C9", "U1", "5", "+3V3_D8")
_intent.bypass("C15", "U4", "3", "+3V3_D8")
_intent.bypass("C16", "U4", "3", "+3V3_D8")
_intent.bypass("C17", "U4", "3", "+3V3_D8")
_intent.bypass("C18", "U6", "2", "+5V_D8")
_intent.bypass("C19", "U6", "5", "PCM_VDD")
_intent.bypass("C20", "U6", "15", "PCM_VCCA")
_intent.bypass("C21", "U6", "19", "PCM_VCCL")
_intent.bypass("C22", "U6", "21", "PCM_VCCR")
_intent.bypass("C23", "U6", "26", "PCM_VCCP")
_intent.bypass("C31", "U7", "12", "AMP_HPVDD")
_intent.bypass("C32", "U7", "14", "+5V_D8")
_intent.bypass("C33", "U7", "14", "+5V_D8")
_intent.bypass("C39", "U8", "8", "+5V_D8")
_intent.write(OUT, PROJECT, P)   # 8 Sep 2026 (MESHSAT-862): design intent as data, out/<project>-intent.json
