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
import intent as _intent
_intent.rail("+5V_D8", 5.0, 1.0, 2.0, "J_PWR1", budget=0.03,
             note="the mezzanine's 5 V from A22. Budget 3 percent, not the 2 percent default, and the reason is the load list: every consumer "
                  "either regulates this rail or tolerates a wide range. It feeds the TLV75533 3.3 V LDO (3.5 V minimum in, 1.5 V of headroom), "
                  "the CP2102N bridge (4.0 V minimum), the ESD reference and, through FB1, the exciter's own boost. D10 measures 108 mV at "
                  "1.0 A, 2.16 percent, leaving 4.89 V at the tightest consumer (9 September 2026).")
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
