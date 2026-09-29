"""Stream s122 (S-122, MESHSAT-1357): the judgement of every inventoried sentence, keyed by the sentence's digest
(sha256/10 of its whitespace-normalised text, `s122lib.sid_digest`).

Each entry is written by the stream after reading the sentence against the committed netlists of set 12 and the
generators; `verdicts.py` evaluates every assertion (`a`) and the names and citation checks itself, and turns a TRUE
into STALE when any of them fails. Kinds:
  T  TRUE: every netlist-derivable claim of the sentence holds; what the sentence says beyond the netlist (a firmware
     rule, a maker's figure, a procedure) is named in `why` and not judged.
  S  STALE: the sentence describes a circuit, a line or a state the netlists or generators no longer carry; `why` gives
     what they carry. Each has its correction in `apply_docs_s122.py`.
  N  NOT DERIVABLE: the claim rests on a held document, a measurement, a firmware or test procedure, or it is a dated
     record of an earlier reading (HISTORY); left as it is.
Assertion language: see `verdicts.run_assert` (B:U536.1=EMCON_HW, B:U536~SN74LVC1G08, B:RB_IEN>J_RB9704,U543,
B:!U111, B:J_QMX?, C:U3@GPIO21=EMCON_RD_R, G@45bde541:gen_sch_a.py:887~R42, DOC:<file>~<words>, SHA:A=<sha16>)."""


def T(why, *a, **kw):
    d = {"v": "T", "why": why, "a": list(a)}
    d.update(kw)
    return d


def N(why, *a, **kw):
    d = {"v": "N", "why": why, "a": list(a)}
    d.update(kw)
    return d


def S(why, *a, **kw):
    d = {"v": "S", "why": why, "a": list(a)}
    d.update(kw)
    return d


H = "HISTORY: a dated record of an earlier reading or wording, true as history, not re-derived against set 12"
FW = "FIRMWARE: the firmware contract or an operating procedure, not a netlist claim"
DOCN = "HELD DOCUMENT: a maker's figure, an analysis, a ruling or a record, not a netlist claim"
TEST = "TEST: a test procedure, a condition or a pass line, not a netlist claim"
CASE = "CASE: a mechanical or case item, not a netlist claim"
BOARDNAME = "a board name as a row label"

# ------------------------------------------------------------------ shared assertion groups
RB = ["B:U503.1=EMCON_HW", "B:U503.2=RB_SW_EN", "B:U503.4=RB_EN", "B:U503.5=+3V3_DEV", "B:R530.1=RB_EN", "B:R530.2=RB_UVLO",
      "B:U24~TPS259631", "B:U24.3=RB_UVLO", "B:U24.4=+5V_DEV", "B:U24.5=+5V_RB", "B:J_RB9704.15=+5V_RB", "B:U6@IO0_2=RB_SW_EN",
      "B:U536~SN74LVC1G08", "B:U536.1=EMCON_HW", "B:U536.2=RB_SW_IEN", "B:U536.4=RB_IEN_DRV", "B:U536.5=+3V3_DEV",
      "B:U6@IO1_6=RB_SW_IEN", "B:R532~2.7k", "B:R532.1=RB_IEN_DRV", "B:R532.2=RB_IEN", "B:R527.1=RB_IEN", "B:R527.2=GND",
      "B:J_RB9704.3=RB_IEN", "B:U543~TPS3808G30", "B:U543.1=RB_IEN", "B:U543.5=+3V3_DEV", "B:U543.6=+5V_DEV",
      "B:U537.1=RB_IEN", "B:U537.2=RB_STATUS", "B:U537.4=RB_GO", "B:J_RB9704.7=RB_STATUS", "B:U538.1=RB_RXD_H",
      "B:U538.2=RB_GO", "B:U538.4=RB_RXD", "B:J_RB9704.14=RB_RXD", "B:U539.1=RB_CTRL_H", "B:U539.2=RB_GO", "B:U539.4=RB_CTRL",
      "B:J_RB9704.6=RB_CTRL"]
LIME = ["B:U501~SN74LVC1G08", "B:U501.1=EMCON_HW", "B:U501.2=LIME_HW_EN", "B:U501.4=LIME_EN_A", "B:U501.5=+3V3_DEV",
        "B:U502.1=LIME_EN_A", "B:U502.2=LIME_SW_EN", "B:U502.4=LIME_EN", "B:U102@PWRCTL1=LIME_HW_EN", "B:U6@IO0_1=LIME_SW_EN",
        "B:R529.1=LIME_EN", "B:R529.2=LIME_UVLO", "B:U23~TPS259631", "B:U23.3=LIME_UVLO", "B:U23.4=+5V_DEV", "B:U23.5=+5V_LIME",
        "B:+5V_LIME>J_LIME"]
E22 = ["B:U504~SN74LVC1G08", "B:U504.1=EMCON_HW", "B:U504.2=LORA_ON", "B:U504.4=E22_EN", "B:U6@IO0_3=LORA_ON",
       "B:R531.1=E22_EN", "B:R531.2=E22_UVLO", "B:U21~TPS22810", "B:U21.5=E22_UVLO", "B:U21.1=+5V_LORA", "B:U12.9=+5V_LORA",
       "B:U12.10=+5V_LORA", "B:U544.2=E22_EN", "B:U544.4=LORA_GO", "B:U544.5=+3V3_CM3", "B:U545.1=LORA_RXEN",
       "B:U545.2=LORA_GO", "B:U545.4=LORA_RXEN_G", "B:U546.1=LORA_TXEN", "B:U546.2=LORA_GO", "B:U546.4=LORA_TXEN_G",
       "B:U547.2=LORA_GO", "B:U548.2=LORA_GO", "B:U549.2=LORA_GO", "B:U550.2=LORA_GO", "B:U12.6=LORA_RXEN_G",
       "B:U12.7=LORA_TXEN_G", "B:R542~100k", "B:R542.1=LORA_TXEN_G", "B:R542.2=GND", "B:R543.1=LORA_RXEN_G", "B:R543.2=GND"]
E72 = ["B:U505~SN74LVC1G08", "B:U505.1=EMCON_HW", "B:U505.2=ZB_ON", "B:U505.4=E72_EN", "B:U6@IO0_4=ZB_ON", "B:U22~TPS22810",
       "B:U22.5=E72_EN", "B:U22.1=+3V3_ZB", "B:U540~SN74LVC2G07", "B:U541~SN74LVC2G07", "B:U542~SN74LVC2G07",
       "B:U540.6=ZBA_RXD", "B:U540.4=ZBA_RST_n", "B:U542.6=ZBB_RXD", "B:U542.4=ZBB_RST_n", "B:U541.6=ZBA_BSL",
       "B:U541.4=ZBB_BSL", "B:+3V3_ZB>R536,R537,U22"]
G5 = ["B:U203~AP64500", "B:U203.3=S2A_EN", "B:U216~SN74LV1T08", "B:U216.1=EMCON_HW", "B:U216.2=PCIE_PWR_EN2",
      "B:U216.4=S2A_EN", "B:U216.5=+5V_S2", "B:U220~SN74LVC2G06", "B:U220.1=EMCON_ON2", "B:U220.6=5G_PWROFF_n",
      "B:U221~TPS3808G30", "B:U221.1=5G_TPR_n", "B:U221.5=+3V3_S2A", "B:U554.1=5G_TPR_n", "B:U554.6=5G_PWROFF_n",
      "B:U215~SN74LVC2G06", "B:U215.1=EMCON_ON2", "B:U215.6=5G_W_DIS_n", "B:U215.3=GND", "B:Q212.1=EMCON_ON2",
      "B:Q212.3=5G_DCHG", "B:R295~15R", "B:R295.1=+3V3_M2C2", "B:R295.2=5G_DCHG"]
WIFI = ["B:U116~SN74LV1T08", "B:U116.1=EMCON_HW", "B:U116.2=PCIE_PWR_EN1", "B:U116.4=S1A_EN", "B:U116.5=+5V_S1",
        "B:U316.1=EMCON_HW", "B:U316.2=PCIE_PWR_EN3", "B:U316.4=S3A_EN", "B:U316.5=+5V_S3", "B:U103.3=S1A_EN",
        "B:U303.3=S3A_EN", "B:U115.1=EMCON_ON1", "B:U115.6=WIFI_W_DIS_n", "B:U115.3=GND", "B:U315.1=EMCON_ON3",
        "B:U315.6=WIFI2_W_DIS_n", "B:U315.3=GND"]
CM5 = ["B:U113.1=EMCON_ON1", "B:U113.3=EMCON_ON1", "B:U113.6=WL_nDIS1", "B:U113.4=BT_nDIS1", "B:U113.5=+3V3_CM1",
       "B:U213.1=EMCON_ON2", "B:U213.6=WL_nDIS2", "B:U213.5=+3V3_CM2", "B:U313.1=EMCON_ON3", "B:U313.6=WL_nDIS3",
       "B:U313.5=+3V3_CM3", "B:U114.1=WL_nDIS1_OFF", "B:U114.6=WL_nDIS1", "B:U114.4=BT_nDIS1", "B:U214.6=WL_nDIS2",
       "B:U214.4=BT_nDIS2", "B:U314.6=WL_nDIS3", "B:U314.4=BT_nDIS3", "B:U6@IO1_0=WL_nDIS1_OFF", "B:U6@IO1_3=BT_nDIS1_OFF"]
INV = ["B:U112~SN74LVC1G04", "B:U112.2=EMCON_HW", "B:U112.4=EMCON_ON1", "B:U112.5=+3V3_CM1", "B:U212.2=EMCON_HW",
       "B:U212.4=EMCON_ON2", "B:U212.5=+3V3_CM2", "B:U312.2=EMCON_HW", "B:U312.4=EMCON_ON3", "B:U312.5=+3V3_CM3"]
CCLAMP = ["C:U9~74LVC1G17", "C:U9.2=TX_INHIBIT_n", "C:U9.4=EMCON_HW_DRV", "C:U9.5=+3V3", "C:R52~330R", "C:R52.1=EMCON_HW_DRV",
          "C:R52.2=EMCON_HW", "C:D23~BAT46W", "C:D23.1=TX_INHIBIT_n", "C:D23.2=EMCON_HW"]
AGATES = ["A:U35~SN74AUP1G08", "A:U35.1=TX_INHIBIT_n", "A:U35.2=EMCON_HW", "A:U35.4=PA_TXOK", "A:U35.5=+3V3_EMCON",
          "A:U36.1=PA_TXOK", "A:U36.2=PA_HOLD", "A:U36.4=PA_EN", "A:U36.5=+3V3_EMCON", "A:U37.1=TX_INHIBIT_n",
          "A:U37.2=EMCON_HW", "A:U37.4=HF_TXOK", "A:U37.5=+3V3_EMCON", "A:U38.1=HF_TXOK", "A:U38.2=HF_HOLD", "A:U38.4=HF_EN",
          "A:U38.5=+3V3_EMCON", "A:U40.6=PA_HOLD", "A:U40.1=PA_SW_EN", "A:U40.4=HF_HOLD", "A:U40.3=HF_SW_EN"]
DKEY = ["D:U12~74LVC1G08", "D:U12.1=PTT_ANY", "D:U12.2=TX_INHIBIT_n", "D:U12.4=KEY", "D:U14.1=KEY", "D:U14.2=PA_EN",
        "D:U14.4=PA_KEY"]
HOTR1 = ["E:Q11.1=HOT_R1_G", "E:Q11.3=BLK_SPARE", "E:J_BLK.12=BLK_SPARE", "A:J_DOCK.12=DOCK_SPARE", "A:U27@IO1_5=DOCK_SPARE",
         "A:R216.1=DOCK_SPARE", "A:R216.2=+3V3"]
FAILSAFE = ["A:R102.1=EMCON_HW", "A:R102.2=GND", "B:R58.1=EMCON_HW", "B:R58.2=GND", "A:R145.1=TX_INHIBIT_n", "A:R145.2=GND",
            "B:R59.1=TX_INHIBIT_n", "B:R59.2=GND", "D:R2.1=TX_INHIBIT_n", "D:R2.2=GND", "A:R117.1=ZEROIZE_HW",
            "A:R117.2=+3V3", "A:R118.1=SHORE_INHIBIT", "A:R118.2=GND"]
SLOTPD = ["A:R30.1=SLOT_EN1", "A:R30.2=GND", "A:SLOT_EN2>R34,U5", "A:SLOT_EN1>R30,U4"]
ZER = ["C:SW_ZERO.1=ZEROIZE_SW", "C:SW_ZERO.2=GND", "C:R10~10k", "C:R10.1=ZEROIZE_SW", "C:R10.2=+3V3", "C:C20~10n",
       "C:C20.1=ZEROIZE_SW", "C:U3@GPIO22=ZEROIZE_SW", "C:U12~74LVC1G17", "C:U12.2=ZEROIZE_SW", "C:U12.4=ZEROIZE_HW",
       "B:ZEROIZE_HW>J_PANEL,J_AB1,TP8", "D:ZEROIZE_HW>J_HARN1,TP9", "A:ZEROIZE_HW>J_AB1,J_MEZZ1,R117", "A:R117~10k"]
PBOARD = ["P:U2~BQ7720700", "P:F2~SCF9550", "P:JP1?", "P:RT1~PRF15BB103RB6RC"]

J = {}
# ================================================================== PANEL.md
J.update({
    "d2e1df041f": T("the controller's parts; TP3 is the RUN line of the SWD set", "C:U3~RP2040", "C:U4~W25Q16", "C:Y1~12 MHz",
                    "C:R5.2=BOOT_J", "C:JP1.1=BOOT_J", "C:TP1.1=SWCLK", "C:TP2.1=SWDIO"),
    "dc87e613e5": T("the LEDs, their sinks and the two lamps' switches; the light guide is a plate item",
                    "C:U1~0x22", "C:U2~0x23", "C:D3.1=TX_K", "C:Q3.3=TX_K", "C:D22~amber", "C:D22.1=EMCLAMP_K",
                    "C:Q7.3=EMCLAMP_K", "C:D1.1=MWARN_K", "C:U1.5=MWARN_K"),
    "c27be131c3": T("D22 is driven by U14 and Q7 from the two EMCON lines, no processor", "C:U14.3=TX_INHIBIT_n",
                    "C:U14.6=EMCON_HW", "C:U14.4=EMCLAMP_Y", "C:R48.1=EMCLAMP_Y", "C:R48.2=EMCLAMP_G", "C:Q7.1=EMCLAMP_G"),
    "598cdf8892": T("the LED rail", "C:SW_LIGHT.2=+5V", "C:SW_LIGHT.1=LED_RAIL_SW", "C:Q1~P-FET", "C:Q1.2=LED_RAIL_SW",
                    "C:Q1.3=LED_RAIL", "C:R19.1=PANEL_PWM", "C:R19.2=Q2_G", "C:Q2.1=Q2_G", "C:R15.1=LED_RAIL_SW",
                    "C:R15.2=RAIL_SENSE"),
    "2add8acf41": T("the switches; sizes and covers are the parts' value texts, the covers a plate item", "C:SW_MAIN~19 mm",
                    "C:SW_PI~16 mm", "C:SW_PI.1=PIJ2_A", "C:SW_PI.2=PIJ2_B", "C:SW_TEST~16 mm", "C:SW_TEST.1=TEST_SW",
                    "C:SW_SOS~APEM", "C:SW_ZERO~APEM", "C:SW_LIGHT~DPDT ON-ON-ON", "A:J_MAINSW?", not_parts=["PIJ2_A"]),
    "fa055147a4": T("the e-paper's parts", "C:J_EPD~24", "C:J_EPD.15=EPD_VCC", "C:Q5.3=EPD_VCC", "C:L1.1=EPD_VCC",
                    "C:Q6.3=EPD_SW", "C:D19.2=EPD_SW"),
    "132968094a": T("the sounder", "C:BZ1.2=+5V", "C:BZ1.1=BZ_K", "C:Q4.3=BZ_K", "C:R44.1=PWM1", "C:R44.2=Q4_G"),
    "d18a3bbf42": T("the light sensor; its 0x10 is the maker's fixed address", "C:U_LIGHT~VEML7700", "C:U_LIGHT.4=SDA",
                    "C:U_LIGHT.1=SCL"),
    "514b8face2": T("the ZEROIZE line; the citation is dated", *ZER),
    "da6c6735f0": S("its citation `gen_sch_c.py:157-166` is undated and those lines now hold decoupling notes (U9 is there at "
                    "45bde541); and since set 12 U9 drives EMCON_HW through R52 with D23 clamping it to TX_INHIBIT_n, which "
                    "the row omits (check-int13-3, n4)", *CCLAMP, not_parts=["C1"]),
    "f4587ac12e": T("R14 and R50 as drawn; the levels and the time constant are the RF-002 walk's figures, not re-derived here",
                    "C:R14~2.2k 1%", "C:R14.1=TX_INHIBIT_n", "C:R14.2=+3V3", "C:R50~10k 1%", "C:R50.1=TX_INHIBIT_n", "C:R50.2=GND"),
    "79b33e8889": T("the read-back and the lamp", "C:U13~74LVC1G17", "C:U13.2=EMCON_HW", "C:U13.4=EMCON_RD", "C:R46~1k",
                    "C:R46.1=EMCON_RD", "C:R46.2=EMCON_RD_R", "C:U3@GPIO21=EMCON_RD_R", "C:U14~SN74LVC1G57",
                    "C:U14.3=TX_INHIBIT_n", "C:U14.6=EMCON_HW", "C:Q7~Si2300DS", "C:R47~470R", "C:R47.1=LED_RAIL_SW",
                    "C:R47.2=EMCLAMP_A", "C:D22.2=EMCLAMP_A", not_parts=["L1"]),
    "f52539503d": N(CASE + " (the light-guide hole in the plate, S-44)", "C:SW_EMCON?"),
    "d757d209e1": T("the leads' ends as drawn; the adapter and SC-HF-06 are a lead item", "B:J_HDMI?", "A:J_MON?", "D:J_USB3?",
                    "C:J_HSJ1?", "C:J_HSJ2?", "D:J_HS1?", "D:J_HS2?", "B:J_CAM?"),
    "436512e5ba": T("J_PANEL pins 1 and 2 on board C", "C:J_PANEL.1=+5V", "C:J_PANEL.2=+5V"),
    "33fdd84538": T("pin 15", "C:J_PANEL.15=USB_PNL_P", "B:J_PANEL.15=USB_PNL_P"),
    "63fa735c4c": T("the pair reaches the slot 1 bank's hub U102; the failover host is the IOHA fabric's", "B:USB_PNL_P>U102,J_PANEL"),
    "e97419f3e8": T("pin 16", "C:J_PANEL.16=USB_PNL_N"),
    "010ebd6b6d": T("pin 6 and GPIO 24", "C:J_PANEL.6=EXP_INT", "C:U3@GPIO24=EXP_INT"),
    "e2d29b9e99": T("pin 7 and GPIO 23", "C:J_PANEL.7=TR_APRS", "C:U3@GPIO23=TR_APRS"),
    "dbd1b086a5": T("TR_APRS is D8's KEY through U18 and R48, and it drives the TX lamp's Q3", "D:U18.2=KEY", "D:U18.4=PTT_MIR",
                    "D:R48.1=PTT_MIR", "D:R48.2=TR_APRS", "D:J_HARN1.7=TR_APRS", "C:R37.1=TR_APRS", "C:R37.2=Q3_G"),
    "428ab166dc": T("pin 8", "C:J_PANEL.8=EMCON_HW", "B:J_PANEL.8=EMCON_HW"),
    "0a41efb05f": T("pin 21 and GPIO 13", "C:J_PANEL.21=SLOT_EN1", "C:U3@GPIO13=SLOT_EN1"),
    "3d8f3fd4e8": T("SLOT_EN1 enables slot 1's buck U4 on board A", "A:U4.3=SLOT_EN1"),
    "a064a6324b": T("pin 22", "C:J_PANEL.22=SLOT_EN2"),
    "737d427bad": T("pin 10", "C:J_PANEL.10=ZEROIZE_HW"),
    "8838b5cf13": T("U12 drives ZEROIZE_HW; on A, B and D only a pull-up, the ribbons and test points", *ZER),
    "21e4b70343": T("pin 23", "C:J_PANEL.23=SLOT_EN3"),
    "5e249213b4": T("pin 11", "C:J_PANEL.11=TX_INHIBIT_n", "C:SW_EMCON.1=TX_INHIBIT_n"),
    "467131a8bf": T("D8's KEY gate reads it", *DKEY),
    "8ecdb03238": T("pin 24 and GPIO 18", "C:J_PANEL.24=PI_SHDN_REQ", "C:U3@GPIO18=PI_SHDN_REQ"),
    "9db27ad4ae": T("pin 12", "C:J_PANEL.12=HDMI_SEL1"),
    "5cc9357372": T("pin 25 and GPIO 19", "C:J_PANEL.25=PI_KILL", "C:U3@GPIO19=PI_KILL"),
    "3b18fafd51": T("PI_KILL drives Q1 onto the LTC2954's KILL on board A", "A:Q1.1=PI_KILL", "A:Q1.3=KILL", "A:U1.8=KILL"),
    "e3b1395bb7": T("pin 13", "C:J_PANEL.13=HDMI_SEL2"),
    "d0d1c3324c": T("pin 26 and GPIO 20", "C:J_PANEL.26=SHORE_INHIBIT", "C:U3@GPIO20=SHORE_INHIBIT"),
    "80bc7b54a1": T("SHORE_INHIBIT reaches board A's dock contact 8 and board E's front end", "A:J_DOCK.8=SHORE_INHIBIT",
                    "E:SHORE_INHIBIT>J_BLK,Q8"),
    "0436f89596": T("GPIO 2 and 3", "C:U3@GPIO2=EPD_SCL", "C:U3@GPIO3=EPD_SDA"),
    "bc46d4958b": T("GPIO 4 to 7", "C:U3@GPIO4=EPD_DC", "C:U3@GPIO5=EPD_CS", "C:U3@GPIO6=EPD_RST", "C:U3@GPIO7=EPD_BUSY"),
    "024798389d": T("GPIO 8", "C:U3@GPIO8=PANEL_PWM"),
    "0474d6812f": T("through Q2 and Q1; the frequency, resolution and boot level are firmware", "C:R19.1=PANEL_PWM", "C:Q2.1=Q2_G"),
    "eb71f5bfaa": T("GPIO 9 through Q4; the pattern is firmware", "C:U3@GPIO9=PWM1", "C:R44.1=PWM1", "C:Q4.1=Q4_G"),
    "60bc5be090": T("HB1 to HB3: GPIO 10 to 12, the level stage Q105, the three supervisors' inputs and B16's pull-up; the 1 Hz "
                    "toggle is firmware", "C:U3@GPIO10=HB1", "C:U3@GPIO11=HB2", "C:U3@GPIO12=HB3",
                    "B:HB1>Q105,U41,U51,U61,R158,J_PANEL", "B:R158.2=+3V3_DEV", "B:U41@PA6=HB1"),
    "dac738f926": T("GPIO 13 to 15", "C:U3@GPIO13=SLOT_EN1", "C:U3@GPIO14=SLOT_EN2", "C:U3@GPIO15=SLOT_EN3"),
    "7d19d484c9": T("each enables its slot's converter on board A", "A:U4.3=SLOT_EN1", "A:U5.1=SLOT_EN2"),
    "9366a20224": T("GPIO 16 and 17", "C:U3@GPIO16=HDMI_SEL1", "C:U3@GPIO17=HDMI_SEL2"),
    "a7d756a9fb": T("the selects reach B16's display switch and its enable muxes", "B:HDMI_SEL1>J_PANEL,U3,U519",
                    "B:HDMI_SEL2>U520"),
    "4ac518fd0e": T("shared with the LTC2954's INT, R3 the pull-up; the timing is firmware", "A:U1~LTC2954", "A:U1.5=PI_SHDN_REQ",
                    "A:R3.1=PI_SHDN_REQ", "A:R3.2=+3V3"),
    "fc3f2c0cca": T("to the LTC2954's KILL through Q1; the 3 s is firmware", "A:Q1.1=PI_KILL", "A:U1.8=KILL"),
    "ab34be3814": S("the charge inhibit is section 10 of this document (section 9 is the indicators)", "C:U3@GPIO20=SHORE_INHIBIT"),
    "fa9eb52c64": T("GPIO 21", "C:U3@GPIO21=EMCON_RD_R"),
    "3215151074": T("U13 and R46", "C:U13.2=EMCON_HW", "C:U13.4=EMCON_RD", "C:R46.1=EMCON_RD", "C:R46.2=EMCON_RD_R"),
    "28808e31a6": T("GPIO 22", "C:U3@GPIO22=ZEROIZE_SW"),
    "460909429a": T("R10, C20 and U12", *ZER),
    "f8a73e0916": T("GPIO 23 reads TR_APRS, D8's KEY through U18", "C:U3@GPIO23=TR_APRS", "D:U18.2=KEY"),
    "2adc9f4a07": T("EXP_INT on GPIO 24; U27's P1.5 is DOCK_SPARE, the HOT-R1 line from board E; the edge behaviour is firmware",
                    "C:U3@GPIO24=EXP_INT", "A:U27@~{INT}=EXP_INT", *HOTR1),
    "81d5174605": T("GPIO 25", "C:U3@GPIO25=LED_STAT"),
    "7f23d7ce92": T("D18 through R6", "C:R6.1=LED_STAT", "C:D18.2=LED_STAT_A"),
    "704baed09c": T("GPIO 26", "C:U3@GPIO26_A0=RAIL_SENSE"),
    "6eccc5366d": T("the R15 and R51 divider; the voltages are computed, not netlist", "C:R15~10k", "C:R15.1=LED_RAIL_SW",
                    "C:R15.2=RAIL_SENSE", "C:R51~10k", "C:R51.1=RAIL_SENSE", "C:R51.2=GND"),
    "ab5c153f31": T("GPIO 27", "C:U3@GPIO27_A1=TEST_SW"),
    "1f29be2cf8": T("R11 and C21", "C:SW_TEST.1=TEST_SW", "C:R11~10k", "C:R11.1=TEST_SW", "C:C21~10n", "C:C21.1=TEST_SW"),
    "8c72785398": T("GPIO 28", "C:U3@GPIO28_A2=SOS_SW"),
    "4982c3d26f": T("R9 and C19", "C:SW_SOS.1=SOS_SW", "C:R9~10k", "C:R9.1=SOS_SW", "C:C19~10n", "C:C19.1=SOS_SW"),
    "138c6b6bc3": T("GPIO 29", "C:U3@GPIO29_A3=EPD_PWR_n"),
    "0608cdb612": T("Q5, a P-FET on +3V3", "C:Q5.1=EPD_PWR_n", "C:Q5.2=+3V3", "C:Q5.3=EPD_VCC"),
    "27d3074deb": N(FW + " (the boot order); PI_KILL and the level stage are the netlist's, the order is firmware",
                    "C:U3@GPIO19=PI_KILL"),
    "55d8f49ec8": T("U519 and U520 take the slots' power-good on their data inputs; R15 and R16 hold the selects low",
                    "B:U519.6=HDMI_SEL1", "B:U519.4=HDMI_EN1", "B:U519.3=PG1_S", "B:U520.6=HDMI_SEL2", "B:U520.4=HDMI_EN2",
                    "B:R15.1=HDMI_SEL1", "B:R15.2=GND", "B:R16.1=HDMI_SEL2", "B:R16.2=GND"),
    "8d9e44bc9c": N(FW + " (the PI button's press lengths)", "C:SW_PI.1=PIJ2_A"),
    "133cca552b": T("SW_MAIN's lead lands on board A's J_MAINSW, the LTC2954's PB input", "A:J_MAINSW.1=MAIN_PB", "A:U1.2=MAIN_PB"),
    "d306ab46ea": T("R14, C24 and R50 on C; the 100k pull-downs on A, B and D; the level is the walk's figure",
                    "C:SW_EMCON.1=TX_INHIBIT_n", "C:R14.1=TX_INHIBIT_n", "C:C24~10n", "C:C24.1=TX_INHIBIT_n",
                    "C:R50.1=TX_INHIBIT_n", "A:R145~100k", "A:R145.1=TX_INHIBIT_n", "B:R59~100k", "B:R59.1=TX_INHIBIT_n",
                    "D:R2~100k", "D:R2.1=TX_INHIBIT_n"),
    "a7e84f7a68": S("board A's round 8 is generated since c0133147, not a candidate; `gen_sch_a.py:1240-1243` now holds other "
                    "code (U35 to U38 are at 1572 to 1575); and U35 and U37 feed U36 and U38 with the software holds, not the "
                    "converters' enables directly", *AGATES, *DKEY),
    "428ab166dc_": T("", ),
    "a3ff8a619c": S("'since board A's round 8 candidate' where round 8 is generated; and R52 and D23 (set 12) omitted beside U9",
                    *CCLAMP, "A:R102~10k 1%", "B:R58~4.7k 1%"),
    "faa935d288": S("board A as generated at 45bde541 (U26) and a round 8 candidate at `gen_sch_a.py:1240-1243`, where U35 to "
                    "U38 are generated (1572 to 1575) and U26 is the outlet interlock alone; U536's RockBLOCK clause omits set "
                    "12's R532 and U543", *AGATES, *RB, *INV, *CM5, *WIFI, *G5, "B:U506.2=EMCON_HW", "B:U506.4=EMCON_SUP",
                    "B:U41@PC5=EMCON_SUP", not_parts=["J3"]),
    "f46acf5130": N(DOCN + " (the rulings 32.50 item 3 and D-05)"),
    "3f55eed50c": N(H + " (the round 8 correction naming the parts round 8 removed)", not_parts=["R513", "Q11", "U19", "U20"]),
    "e5d33f7dc2": T("SW_ZERO and U12", *ZER),
    "b0be55ba0f": T("ZEROIZE_SW's only reader is GPIO 22; ZEROIZE_HW reaches test points on B and D and R117 on A", *ZER),
    "d3bb02455a": N(DOCN + " (the key wrapping, feasibility/ZEROIZE.md)", "B:U8~ATECC608B"),
    "336485f33d": N(DOCN + " (ZEROIZE.md and the bench experiments); B16's U8 is the ATECC608B site", "B:U8~ATECC608B"),
    "4d225c0c87": T("TR_APRS from KEY through U18", "D:U18.2=KEY", "D:R48.2=TR_APRS"),
    "50a302f450": T("the MAIN switch lead", "C:SW_MAIN~J_MAINSW", "A:J_MAINSW.1=MAIN_PB"),
    "f167717fb2": T(BOARDNAME),
    "90da98adce": S("U6's outputs also carry the RockBLOCK's ENABLE request RB_SW_IEN (IO1_6) and its P_EN request RB_CTRL_H "
                    "(IO1_7), which the row leaves out", "B:U6~0x20", "B:U7~0x25", "B:U6@IO1_6=RB_SW_IEN",
                    "B:U6@IO1_7=RB_CTRL_H", "B:U7@IO0_3=RB_STATUS", "B:SDA>U6,U7"),
    "bc215963d1": T(BOARDNAME),
    "0348bf9879": T("U27 and U28 as drawn; P1.5 is DOCK_SPARE with R216, P1.2 EMCON_EF_FLT from U39", "A:U27~0x21",
                    "A:U28~0x24", "A:U27@IO0_0=CHG_INHIBIT", "A:U27@IO0_1=MON_EN", "A:U27@IO0_2=HEAT_EN", "A:U27@IO0_3=D8_EN",
                    "A:U27@IO0_4=POE_SW_EN", "A:U27@IO0_5=PA_SW_EN", "A:U27@IO0_6=HF_SW_EN", "A:U27@IO0_7=DEV_EN",
                    "A:U27@IO1_5=DOCK_SPARE", "A:R216.1=DOCK_SPARE", "A:U28@IO1_0=PD_SW_EN", "A:U28@IO0_0=USBX_EN",
                    "A:U28@IO0_1=USBX_FLT", "A:U28@IO1_2=EMCON_EF_FLT", "A:U39.6=EMCON_EF_FLT", "A:SDA>U27,U28"),
    "0536e7eccf": T(BOARDNAME),
    "e32ddc3033": T(BOARDNAME),
    "12ab5b6b01": T("U5 on the bus with its A3 pin open; the broadcast address is the maker's", "B:U5~TPS23861",
                    "B:U5.23=unconnected-(U5-A3-Pad23)", "B:SDA>U5"),
    "406b1d5e9e": T("U41, U51 and U61 on PB6 and PB7; the addresses are the firmware contract", "B:U41~STM32H743",
                    "B:U41@PB6=SCL", "B:U41@PB7=SDA", "B:U51@PB7=SDA", "B:U61@PB7=SDA"),
    "5f2cf03744": T("U22 with ADDR to GND on the flange lead; the key-down rules are firmware", "D:U22~ADS1115", "D:U22.1=GND",
                    "D:U22.9=SDA", "D:U22.4=FLANGE_AIN0", "D:J_FLANGE?", not_parts=["K2", "C4"]),
    "31ce2cbb07": T("the KSZ9897R on the bus with the strap R57; the fixed address is the maker's", "B:U1~KSZ9897",
                    "B:R57~I2C management", "B:SDA>U1"),
    "7bc4869e25": N(DOCN + " (the fitted part's address, ZEROIZE.md item U4, TBD)", "B:U8~ATECC608B", not_parts=["U4"]),
    "e405a3ce91": T("U9 on B16, CR2032-backed on VBAT_RTC; the order code history is a record", "B:U9~DS3231SN", "B:U9.15=SDA",
                    "B:U9.14=VBAT_RTC"),
    "6caaca3cd6": S("the provenance names 45bde541 and board D's round 8 only, while the U27 row's HOT-R1 (w4ae), the U28 row's "
                    "EMCON_EF_FLT (w3a) and the supervisors' row (board B's round 8) come from later sets; nothing records a "
                    "re-read at set 12"),
    "94bef6640e": N(H),
    "0c8cf23652": N(H + "; the broadcast address is the maker's"),
    "108d13c557": N(DOCN),
    "5b976a9345": N(FW + " (the supervisors' addresses, I3-F01)"),
    "ccaf6c5062": T("the supervisors and the secure element share the kit bus; the command rule is firmware (Z-C3)",
                    "B:SDA>U41,U51,U61,U8"),
    "aedcd950db": N(FW + " (the bus speed)"),
    "4ff7998807": T("R54 and R55 on B16, R7 and R8 on C7; the currents are computed", "B:R54~2.2k", "B:R54.1=SDA",
                    "B:R55~2.2k", "B:R55.1=SCL", "C:R7~2.2k", "C:R7.1=SDA", "C:R8~2.2k", "C:R8.1=SCL"),
    "385ae55b43": N(DOCN + " (the targets' rise-time limits and HF-F01)"),
    "919c0ea875": T("no TCA9517A is drawn on A or B, so the segments are owed, as the paragraph says", "A:!~TCA9517", "B:!~TCA9517",
                    "A:SDA>U27,U28,J_AB1"),
    "b368b57fd0": T("no TCA9517A on A or B", "A:!~TCA9517", "B:!~TCA9517"),
    "0129fb0216": N(DOCN + " (the sensor board inside E6 is not a netlisted board); the sensor controller is E's RP2040",
                    "E:U10~RP2040"),
    "c2b91e4453": T("the fail-safe pulls on A, B and D", *FAILSAFE),
    "1d4232681d": T("R30 and R34 hold the slot enables low", *SLOTPD),
    "73da5fc77a": N(DOCN + " (the charger's host-free behaviour, TI's answer)"),
    "ba3a95b6c7": T("the lamp test's circuit: D17 ties TX_K to U2's TX_LAMPTEST, the PI ring on U2 IO0_2; D22 on no expander",
                    "C:D17.2=TX_K", "C:D17.1=TX_LAMPTEST", "C:U2@IO1_0=TX_LAMPTEST", "C:U2@IO0_2=PIRING_K",
                    "C:SW_MAIN.3=MAINRING_A", "C:D22.1=EMCLAMP_K"),
    "b7ee9bd83e": N(FW + " (the e-paper's use); EPD_PWR_n drives Q5", "C:Q5.1=EPD_PWR_n"),
    "f6d813396d": N(FW + " (the SOS indications)"),
    "3e9e9f47d5": N(FW),
    "6e81e4a9e9": N(FW),
    "b84bc1b43e": N(FW + " (the no-host indication); the bank assignment is the IOHA fabric's"),
    "4f2665c0ff": N(FW),
    "1bc7026f6e": N(FW + " (the ZEROIZE indications)"),
    "9e86900b5a": T("SHORE_INHIBIT from GPIO 20 and ribbon pin 26 to A's dock contact 8 and E's Q8", "C:U3@GPIO20=SHORE_INHIBIT",
                    "C:J_PANEL.26=SHORE_INHIBIT", "A:J_DOCK.8=SHORE_INHIBIT", "E:Q8.1=SHORE_INHIBIT"),
    "eb466c8d5a": T("the strap and the power path; the citations are dated; the percentages are computed",
                    "A:R26~13.3k 1%", "A:R26.1=CH_VDDA", "A:R26.2=CH_CELL", "A:R27~40.2k 1%", "A:R27.1=CH_CELL",
                    "A:R17.1=VBAT", "A:R17.2=CELL_FUSED", "A:F1.1=CELL+", "A:F1.2=CELL_FUSED", "A:U3~BQ25731"),
    "b91071c95b": N(DOCN + " (the charger's behaviour, the charger-state record)"),
    "cba542e37a": N(H),
    "a9c858ec0a": N(FW),
    "bc41670bc5": T("the gauge's SMBus reaches E's J_SMB, not the charger on A", "E:J_SMB.1=SMBC", "E:J_SMB.2=SMBD",
                    "P:J_SMB.1=SMBC", "A:!J_SMB"),
    "f1f111b885": T("both ends' pin orders", "P:J_SMB.1=SMBC", "P:J_SMB.2=SMBD", "P:J_SMB.3=PACK_N", "P:J_SMB.4=PRES_J",
                    "E:J_SMB.1=SMBC", "E:J_SMB.2=SMBD", "E:J_SMB.3=GND", "E:J_SMB.4=PRES_LEAD"),
    "d1a6b91d38": N(H),
})
del J["428ab166dc_"]

# ================================================================== CONOPS.md
J.update({
    "ad42c9eb94": N(DOCN + " (the second pack's location, INFERRED from the board B underside against appendix 32.62)"),
    "82d7099fad": N(DOCN + " (IOHA's acceptance tests)"),
    "534549e3cc": N(DOCN + " (ARCH-PCB-B-IOHA.md section 15)"),
    "8b09cd80ae": N(DOCN + " (the named exceptions of IOHA sections 15 and 15a)"),
    "3118c4d8b8": N(DOCN + " (SC-02, a session ruling)"),
    "a3a4d07e30": N(DOCN),
    "782f2efe06": N(DOCN + " (the reduced mode's slots, IOHA sections 4 and 15)"),
    "378a24dccc": N(DOCN + " (M4's must-hold, REQ-071; the 5G bound is EMCON.md's)"),
    "1922b27e39": N(DOCN + " (ruling D-05)"),
    "66dbfeded9": T("the MAIN lead reaches the LTC2954's PB", "A:J_MAINSW.1=MAIN_PB", "A:U1.2=MAIN_PB"),
    "42a39f0c30": T("ZEROIZE_SW on GPIO 22, the slot enables on GPIO 13 to 15, SHORE_INHIBIT held low by R118; the order is "
                    "firmware", "C:U3@GPIO22=ZEROIZE_SW", "C:U3@GPIO13=SLOT_EN1", "A:R118.1=SHORE_INHIBIT", "A:R118.2=GND"),
    "1a6b46e4c8": T("the slot enables' pull-downs on board A; the 60 s supervision is firmware", *SLOTPD),
    "fe0dc4bdbe": N(FW + " (a classification of the row)"),
    "078d294b3f": S("its generator citations (line 887; lines 260 and 261; 763, 1009, 1112 and 1125; 1041 to 1064; gen_sch_e.py "
                    "524 to 542) are undated and those lines now hold other code (R42 is at 1104, R2 and R184 at 338); they "
                    "held these parts at 45bde541, and the circuit they describe still holds",
                    "A:R42.1=DEV_EN", "A:R42.2=+3V3", "A:R4.1=KILL", "A:R4.2=+3V3", "A:R2.1=RAIL_EN", "A:R184.1=RAIL_EN",
                    "A:R103~4.7k", "A:R21~4.7k", "A:R92~143k", "A:R93~10k", not_parts=["C14", "D02"]),
    "98554054a3": S("its citations `gen_sch_a.py` lines 764 to 771 and 18 to 48 are undated and those lines now hold other text "
                    "(R26 and R27 are at 972); they held the strap and the VSYS note at 45bde541, and the circuit holds",
                    "A:R26~13.3k", "A:R27~40.2k", "A:R17.1=VBAT", "A:R17.2=CELL_FUSED"),
    "401c2f5c6f": T("the hardware holds: Q8 on SHORE_INHIBIT pulls the front end's UVLO, Q6 on CHG_INHIBIT puts the charger in "
                    "HiZ, board P's second level and F2; the gauge's window is its data flash", "E:Q8.1=SHORE_INHIBIT",
                    "E:Q8.3=HS_UVLO", "A:Q6.1=CHG_INHIBIT", "A:Q6.3=CHG_ILIM", *PBOARD),
    "f17b893792": N(DOCN + " (the charger's host-free behaviour, TI SLUSE66A and E2E)"),
    "835e712c2f": T("the EMCON toggle", "C:SW_EMCON~locking toggle", "C:SW_EMCON.1=TX_INHIBIT_n"),
    "7f1fe39d10": T("every rail and disable named, as section 4b; the software hold is firmware", *LIME, *RB[:12], *E22[:12],
                    *E72[:8], *WIFI[:6], *CM5[:5], *G5[:8], *AGATES, *DKEY, "A:R124.1=HF_EN", "A:R58.1=PA_EN"),
    "da066b5a32": T("the hardware parts named; the RockBLOCK's own behaviour is a held-document item, said so", *RB[:20], *DKEY),
    "7778cb996e": N(DOCN + " (the owed list, feasibility/EMCON.md section 4d.5)", "B:U536?", "B:U112?", "B:U115?"),
    "1902260ba4": T("drawn: the 5G supply removal, U536 and the enable dividers R529 to R531 and R530, the back-feed gates; "
                    "'closed at desk' is EMCON.md's", *G5[:6], *RB, "B:R529.2=LIME_UVLO", "B:R530.2=RB_UVLO",
                    "B:R531.2=E22_UVLO", *E22[12:20], *E72[8:]),
    "cdb29268ee": T("the ZEROIZE toggle; the 5 s and the rulings are firmware", "C:SW_ZERO~ZEROIZE", "C:SW_ZERO.1=ZEROIZE_SW"),
    "8f0b7a3857": T("the ZEROIZE path; its citations are dated at 45bde541", *ZER, "G@45bde541:gen_sch_c.py:168-178~U12",
                    "G@45bde541:gen_sch_a.py:1150~R117"),
    "20e78504cb": N(DOCN + " (the ATECC608B precondition, ZEROIZE.md)", "B:U8~ATECC608B"),
    "2b8cdd90ff": N(CASE),
    "2f097181b1": N(FW + " (the D-14 procedure)"),
    "9a868f70ce": N(DOCN + " (references)"),
    "6b2997fde7": S("its citation `gen_sch_a.py` lines 1012 to 1015 and 1151 to 1167 is undated and those lines now hold other "
                    "code (J_USBC_OUT is at 1306, J_USBW at 1668); they held them at 45bde541, and the circuit holds",
                    "A:U32.5=VBUS_WALL", "A:J_USBW?", "A:J_USBC_OUT?"),
    "5e56d89e4a": N(DOCN + " (the power state and its runtimes)"),
    "262d501aa1": T("the four netlists read are these", "SHA:A=6c40250c47195ebb", "SHA:B=3ef9b8c49a01b728",
                    "SHA:C=87b69472ac83ca5a", "SHA:D=a2d48972d171aad1"),
    "10805ed533": S("apply_conops_4b_set12.py asserts 146 pin assignments of 55 parts, not every gate, supply and net the rows "
                    "name (check-int13-3, n1: no pins of U9, R52 or D23, nothing of U214, U314, U22 to U24's pins or "
                    "LIME_HW_EN's source)"),
    "b73681b892": N(DOCN + " (EMCON.md's sections)"),
    "726eb1c25e": T("the preamble's circuit", *CCLAMP, *INV, *AGATES),
    "3abf66595f": T("the LimeSDR's gates and eFuse", *LIME),
    "fca7d9ce89": T("the RockBLOCK's gates", *RB),
    "718784cd36": N(DOCN + " (the module's supercapacitors and its response to ENABLE)", "B:J_RB9704.3=RB_IEN"),
    "30107ef297": T("the E22's gates", *E22),
    "690c3d3e10": T("the E72s' gates", *E72),
    "0cad4d90e9": T("the 5G module's gates", *G5),
    "4f988b639f": T("the WiFi cards' gates", *WIFI),
    "0a33265e16": T("the SA868 and PA gates; the exciter's supply +5V_SA comes from U21 on +3V3_D8's divider, not the EMCON "
                    "lines; the relay's rest state is not a netlist claim", *DKEY, *AGATES, "A:R58.1=PA_EN", "A:R58.2=PA_UVLO",
                    "A:U13~+13V8_PA", "D:U2~SA868", "D:U2.8=+5V_SA", "D:FB1.2=+5V_SA", "D:FB1.1=+5V_TX", "D:U21.1=+5V_TX",
                    "D:U21.5=TXSUP_EN"),
    "58a2b95587": T("the HF gates; J_QMX's VBUS is the hub port's, ungated", *AGATES[9:], "A:R124.1=HF_EN", "A:R124.2=HF_UVLO",
                    "A:U15.1=HF_UVLO", "A:U15~+12V_HF", "B:J_QMX.1=VBUS_QMX"),
    "674fed0ea8": T("the module radios' disables", *CM5),
    "6688b32a1a": N(DOCN + " (ruling D-05)"),
    "98a110f4dd": N(DOCN + " (Quectel's GNSS ports)"),
    "e85bb31663": N(H + " (the design record's list)"),
    "d174af17a0": N(DOCN),
    "26b3f934c1": T("TP10 is on TX_INHIBIT_n; the latency definition is a requirement", "C:TP10.1=TX_INHIBIT_n"),
    "4f38a2cd34": T("the 5G row's parts; the timing bound is EMCON.md's", *G5),
    "f5b087cd8e": N(DOCN + " (the fault set, EMCON.md section 5a)", "A:J_AB1?", "A:J_MEZZ1?", not_parts=["F9"]),
    "07ffe0084f": T("D22 through U14 and Q7 needs no firmware; its light guide is a plate item", "C:U14.3=TX_INHIBIT_n",
                    "C:U14.6=EMCON_HW", "C:Q7.3=EMCLAMP_K", "C:D22.1=EMCLAMP_K"),
    "05689078be": N(DOCN + " (ASM-002 and Review C)"),
    "c20f2e4cda": N(DOCN + " (the banks' hosts, IOHA section 4)"),
    "48f03d5cb4": N(FW + " (a fault row's label)"),
    "7d60fee70d": T("SLOT_EN1 to 3 fall to their pull-downs on board A; the rest is the firmware contract", *SLOTPD),
    "0f2685fa36": N(DOCN + " (a layer-5 design item: nothing but the pull-downs and the converters sits on SLOT_EN)",
                    "A:SLOT_EN1>R30,U4,J_AB1"),
    "2872504a3c": T("the ribbon-out pulls", *FAILSAFE, *SLOTPD),
    "b9f6eebae8": S("+3V3_DEV is made on board B (U25, AP63203, from +5V_DEV through L1), not on board A; board A's U7 makes "
                    "+5V_DEV", "A:U7.12=+5V_DEV", "B:U25.5=DEV_SW", "B:L1.2=+3V3_DEV", "A:!~AP63203"),
    "a8a12c6168": S("the slots' U{s}11 are gone and EMCON.md records L3 closed at desk in board B's round 8: each slot's "
                    "EMCON_ON is made from its own 3.3 V (U112, U212, U312); U543 holds RB_IEN low below 2.79 V on +3V3_DEV",
                    "B:!U111", "B:!U211", "B:!U311", *INV, "B:U543.1=RB_IEN",
                    "DOC:v2/docs/feasibility/EMCON.md~CLOSED at desk on board B's round 8 (section 4b)"),
    "6c5f98fafe": N(DOCN + " (IOHA and ZEROIZE.md R4)"),
    "e1dfc415de": N(DOCN + " (ZEROIZE.md section 3.5)"),
    "e58fe90ad4": S("its citation `gen_sch_e.py` line 503 is undated and that line now holds another comment; it named the fan "
                    "tachometers at 45bde541"),
    "2cdcdadf40": N(FW),
    "48a9631e39": N(FW + " (the designed response; REQ-042)"),
    "cee55e9271": N(FW + " (the hot stop, CONOPS 4c)", "C:U3@GPIO19=PI_KILL"),
    "b0cc968749": N(FW, "B:U10~TMP117"),
    "67da32c859": T("board P's second level, F2 and the PTC element", *PBOARD),
    "0d119cbc54": N(DOCN + " (PWR-F16)"),
    "a519c88ba6": T("KEY's members are U12's output and the inputs of U13, U14, U18 and U19: no hardware timer; the key-down "
                    "rules are firmware", "D:KEY>U12,U13,U14,U18,U19,R49,R84,TP3", "D:U13.2=KEY", "D:U19.2=KEY",
                    not_parts=["K2", "C4"]),
    "66725c9ccc": N(DOCN + " (the heat stage, 4c)"),
    "af87eaaf24": T("the 5G supply removal", *G5[:8]),
    "4fcc861597": S("HOT-R1 is drawn on boards A and E since stream w4ae (E's Q11 on BLK_SPARE, A's DOCK_SPARE on U27 with "
                    "R216), not owed", *HOTR1),
    "6fb0e1ba5d": N(DOCN + " (ruling D-11)"),
    "b0cda524e0": N(DOCN + " (SC-10 and the key-down rules)", not_parts=["K2", "K3", "K4", "K5"]),
    "403303aa15": N(DOCN + " (FEA-004)"),
    "360270daa1": T("U30 and U26 as the interlock; the citation is dated", "A:U30~NAND", "A:U30.1=TR_APRS", "A:U30.2=PA_EN",
                    "A:U30.4=OUTLET_OK", "A:U26.9=POE_SW_EN", "A:U26.10=OUTLET_OK", "A:U26.8=POE_EN", "A:U26.12=PD_SW_EN",
                    "A:U26.13=OUTLET_OK", "A:U26.11=PD_EN", "G@45bde541:gen_sch_a.py:1088-1104~U30"),
    "79efee6cea": N(DOCN, not_parts=["K2", "K5"]),
    "1007cd40f1": N(DOCN),
    "85c9b8a37f": N(FW),
    "73a88e2ff9": N(FW, not_parts=["K4"]),
    "934ca33971": N(FW),
    "56a99bef2a": N(FW),
    "f5af2c97e9": N(DOCN),
    "51400cfd73": N(DOCN),
    "526de24db6": N(DOCN),
})

# ================================================================== V2-SPEC.md
T7 = "HISTORY: the boards table is headed 'as generated on 7 September 2026', a dated record, not re-derived against set 12"
J.update({
    "8ca89fa881": N(DOCN + " (the document's status note)"),
    "d2673a4edc": N(CASE),
    "d45adb955f": N(CASE),
    "e231767e5f": N(CASE),
    "facb104de6": N(CASE),
    "5151a2ab87": N(CASE + " and ruling D-07"),
    "e6fa17db79": N(CASE),
    "c73b56fb81": N(CASE),
    "38a91feb23": N(FW + " (the D-14 procedure) and " + CASE),
    "f6633e61d3": N(DOCN + " (appendix 32.55)"),
    "306d6f0471": N(DOCN + " (the pack, D-06)"),
    "cea8161b55": T("the rails as drawn on board A", "A:U3~BQ25731", "A:U13~+13V8_PA", "A:U21.4=VBAT", "A:U21.5=VMON",
                    "A:U22.4=VBAT", "A:U33~12.0 V", "A:U18~TPS25740A", "A:*~PoE"),
    "5d18d3f4e9": N(DOCN + " (ruling D-05)"),
    "c3dc5405b5": T("the line's effects as generated since 458b2873 and board B's round 8; the counts are feasibility/EMCON.md "
                    "section 0a's, not netlist claims", *LIME[:5], *RB[:10], *E22[:6], *E72[:6], *WIFI[:6], *CM5[:5], *G5[:8],
                    *AGATES[:10], *DKEY, "C:D22~amber", "C:U14.3=TX_INHIBIT_n", "D:U15~PA gate bias", "D:U15.4=PA_KEY",
                    "D:U15.1=VGG_SW", "D:J_VGG.1=VGG_SW"),
    "bd895a6727": N(DOCN + " (the IOHA fabric)"),
    "13651ca141": N(DOCN + " (IOHA sections 15 and 15a)"),
    "63d017d3ba": T("the toggle sensed on C7 with U12 onto the ribbon line; the precondition is ZEROIZE.md's", *ZER),
    "269eb6eecd": T("the RockBLOCK's serial lines on B16", "B:J_RB9704.14=RB_RXD", "B:RB_TXD>J_RB9704"),
    "6ea98bdfa1": T("the key-B socket, the two SIM holders and their TPD4E001 arrays; the SIM pin map is Quectel's",
                    "B:J_M2C2~2199119", "B:*~TPD4E001", "B:U222~TPD4E001", "B:U223~TPD4E001"),
    "5197d59831": N(CASE + " (the jacks)", "B:J_M2C2?"),
    "93fc305d0b": N(CASE + " (the jacks' wall)"),
    "ef6e21d8f1": T("the modules' radio disables through open drains", *CM5),
    "fab095e0a3": T("the E22 on slot 3's SPI through the LORA_GO gates", "B:U12~E22", "B:U548.2=LORA_GO", "B:J_SPI3?"),
    "bd1020ac37": T("the two E72 on B16", "B:U13~E72", "B:U14~E72"),
    "00075b673b": T("the SA868 on D8", "D:U2~SA868"),
    "0163325df3": T("J_QMX on B16 and the 12 V HF rail on A22", "B:J_QMX?", "A:J_HF.1=+12V_HF", "A:U15~+12V_HF"),
    "7047eb808a": T("the LimeSDR's USB 3 receptacle on B16", "B:J_LIME~USB 3.0", "B:J_LIME.1=+5V_LIME"),
    "26424f2f31": N(DOCN + " (the GNSS receiver's maker data)"),
    "ccb40f1128": T("the LG290P on B16", "B:U11~LG290P"),
    "3a7ee237a0": N(CASE),
    "884cd4a8b5": T("sixteen LEDs and the amber D22 lit from the EMCON lines through U14 and Q7; the light guide is a plate item",
                    "C:D16?", "C:D22~amber", "C:U14.3=TX_INHIBIT_n", "C:U14.6=EMCON_HW"),
    "7ef3fa7ff9": N(DOCN + " (ruling D-02a)"),
    "b89f99d383": S("the three cooler fans are driven by their modules (B16 J_FAN1..3 on each CM5's Fan_PWM and Fan_Tacho); the "
                    "sensor controller drives the two mixer fans on E6", "B:J_FAN1.4=FAN_PWM1", "B:U30A@Fan_PWM=FAN_PWM1",
                    "E:U10.13=FAN1_TACH"),
    "d9ae91817c": S("the RockBLOCK 9704's ENABLE is forced low by the EMCON hardware since board B's stream w4b (U536, and "
                    "U543 since set 12); what stays owed is the module's response when ENABLE falls (check-int13-3, B1)", *RB[:20]),
    "e85072845e": N(T7),
    "8b6267524a": N(T7),
    "40489568ae": N(T7),
    "b073b98568": T(BOARDNAME),
    "0a2d2b6e41": N(T7),
    "13c8378a0c": N(H), "32e463a311": N(H), "bfceed26aa": N(H), "79125fde3c": N(H), "69f00e42b6": N(H),
    "98d61fdac2": N(H), "f24449212b": N(H), "09b0290f45": N(H), "a50c9558a0": N(H), "a2dd3da4b9": N(H),
    "caf66e9a0b": N(H), "6bd06a12f8": N(H), "3dce1898a0": N(H), "7aba6fc4cb": N(H), "3d282911cb": N(H),
    "a4bc9c4c53": N(H), "159493d2c6": N(H), "fb3f468c2a": N(H), "eb7d3a156d": N(H), "a94b86ce23": N(H),
    "4e77de78ad": N(H), "61f1da29b2": N(H), "c8178dd548": N(H + " (the H753 and H743 mismatch record; U41's value text now "
                                                          "reads STM32H743VIT6)", "B:U41~STM32H743"),
    "66790359c6": N(H), "f211cada9a": N(H), "4bae2bcb5a": N(H), "c8af65ddfb": N(H), "88040ba1cc": N(H),
    "164b0034a6": N(H), "30bcc6427f": N(H), "83b0b3fdc8": N(H), "32e44f2efa": N(H), "7e2122c8fa": N(H),
    "1a8e99596c": N(H), "ba724f447c": N(H), "f76be55b28": N(H), "c3cfb2621c": N(H), "045032dec5": N(H),
    "8a7c2cc868": S("correction 29 puts both device-rail converters on board A; board A's U7 makes +5V_DEV and board B's U25 "
                    "(AP63203) makes +3V3_DEV from it, as at 45bde541 already", "A:U7.12=+5V_DEV", "B:U25.5=DEV_SW",
                    "B:L1.2=+3V3_DEV", "A:!~AP63203"),
    "6b5ffb2144": N(H), "ce048350b0": N(H), "8186d44a9b": N(H), "adef5b5d31": N(H),
    "48691b711e": N(H + "; U536 and R527 as it says", "B:R527.1=RB_IEN", "B:U536.4=RB_IEN_DRV"),
    "f64abb1173": N(H, "B:U116.5=+5V_S1"),
})

# ================================================================== OPERATING-ENVELOPE.md
J.update({
    "6eb6546bb8": T("board P is gen_sch_p.py's", "P:U2~BQ7720700"),
    "916256cba8": N(DOCN + " (the parts' temperature ratings)", *PBOARD),
    "8f59ec89ff": N(DOCN + " (F2's rating)", "P:F2~SCF9550"),
    "fc58cb90ed": N(DOCN + " (the thermal bounds)"),
    "e20bc8f1b4": N(DOCN + " (the gauge's data flash window)"),
    "31985580ef": T("board P's second level, F2, the arming jumper and the PTC element; the citation is dated",
                    *PBOARD, "G@45bde541:gen_sch_p.py:243~RT1", "G@45bde541:gen_sch_p.py:288~F2",
                    "G@45bde541:gen_sch_p.py:414-502~JP1"),
    "78311d8113": N(FW + " (control C1)"),
    "69c53126c9": N(H),
    "0a6d39484c": S("HOT-R1 is in the generators of boards A and E since stream w4ae (E's Q11 on the dock line BLK_SPARE, A's "
                    "U27 on DOCK_SPARE with R216), and REQ-077 no longer reads FAIL for its absence", *HOTR1),
    "c836951a27": N(DOCN + " (the cold warm-up bound)"),
    "84c26222a6": N(DOCN),
    "ffc36a06e2": N(DOCN + " (the tracker's rating)"),
    "9bab90eb18": N(H),
    "532e78f2df": S("its citation `gen_sch_a.py` line 1003 is undated and that line now holds other code (U18 is at 1267); it "
                    "held the TPS25740A at 45bde541, and the stage holds", "A:U18~TPS25740A", "A:U19~LM5176"),
    "28447175d0": S("EMCON does not gate every transmitter's rail: the SA868's supply +5V_SA is not on the EMCON lines (only its "
                    "KEY is) and the modules' own radios are disabled through their pins, not rail-gated", "D:U2.8=+5V_SA",
                    "D:FB1.1=+5V_TX", "D:U21.5=TXSUP_EN", "B:U113.6=WL_nDIS1"),
    "b719e651bd": T("the dated reading's supply removals hold, and board B's round 8 removes the 5G supply; that the "
                    "radios stop receiving is the modules' behaviour (the RockBLOCK only once its own stored energy is spent, "
                    "CONOPS 4b), not a netlist claim", *LIME[:5], *RB[:10],
                    *E22[:6], *E72[:6], *WIFI[:6], *CM5[:5], *G5[:8], *AGATES[:10]),
    "d23664c78f": N(DOCN + " (ruling D-05)"),
    "e4ba0483d0": S("the RockBLOCK 9704's ENABLE is forced low in hardware since board B's stream w4b; what is left is its "
                    "response when ENABLE falls", *RB[:20]),
    "c98651fe06": N(DOCN),
    "8f3480949a": N(DOCN + " (the single faults the design is expected to survive)"),
    "4acb82ab42": T("no module powers without the panel controller: the slot enables are pulled low on board A", *SLOTPD),
})

# ================================================================== pcb_decisions.yaml, decisions 28 and 40
J.update({
    "27a657c309": N(DOCN + " (the ruling and the route arm P8)"),
    "60324e1220": T("the stackup row is recorded, at 45bde541 and at the base", "G@45bde541:stackup_write.py:46~JLC04162H-7628",
                    "G@HEAD:stackup_write.py:1-400~JLC04162H-7628", cite_ok="stackup_write.py:46 at 45bde541 asserted below"),
    "a4f3639760": T("board P's committed layout has no inner copper and none of the round 4 parts", "P:U2~BQ7720700",
                    "G@HEAD:v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_pcb:1-400~F.Cu"),
    "b690b6e0c5": T("nothing laid on four layers: the committed board P layout is the two-layer P4",
                    "G@HEAD:v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_pcb:1-400~B.Cu"),
    "4698174d5f": N(DOCN + " (the floor as ruled)"),
    "a89adf0d12": N(DOCN + " (the owner's branch)"),
    "4f6b62b753": T("board P's schematic carries the second level, F2, JP1 and the PTC element; the citation is dated",
                    *PBOARD, "G@45bde541:gen_sch_p.py:243~RT1", "G@45bde541:gen_sch_p.py:288~F2",
                    "G@45bde541:gen_sch_p.py:414-502~JP1", cite_ok="gen_sch_p.py lines at 45bde541 asserted below"),
    "c1269c680b": T("the committed layout predates the schematic", "P:U2~BQ7720700"),
    "b7bc3415b2": T("gen_sch_p.py carries them; no layout does", *PBOARD),
})

# ================================================================== TEST-PLAN.md
PFLOOR = ["P:U2~BQ7720700", "P:U2.10=SEC_COUT", "P:R29.1=SEC_COUT", "P:R29.2=FUSE_G", "P:TP11.1=FUSE_G", "P:JP1.1=FUSE_G",
          "P:JP1.2=FUSE_GQ", "P:Q3.1=FUSE_GQ", "P:Q3.3=SCP_HTR", "P:F2.3=SCP_HTR", "P:U2.11=SEC_DOUT", "P:Q5.1=SEC_DOUT",
          "P:Q5.3=DSG_G", "P:Q2.4=DSG_G", "P:R18.1=DSG_G", "P:F1~25 A"]
for _d in ("f1c2c8d45e", "5f30437813", "b9f3eb411b", "fd11388bc4", "6f3c17593a", "6d64bb1f6f", "09181bc249"):
    J[_d] = N(H + " (the plan's revision notes)")
for _d in ("18891567a1", "de793ba193", "ac686a5720", "b7a59d5af7", "076433a5d2", "44b650e543", "a53a23c6b1", "569c2bd4c8",
           "ef099fcece", "a584c80595", "a29d84f018", "2800341bc8", "06b410e9d3", "3511240a06", "4b487b6217", "7e55555dd4",
           "673141c79e", "b2e71f3fc0", "d2a8855204", "7c2fccc23f", "fe768b753d", "7c4049d276", "2db0cac4fc", "59be764e53",
           "8d60af7ae3", "ed742e38eb", "4c093fe530", "8e6c168e29", "22eef71b46", "4fdfa062e2", "1b8dccfacb", "e17ab78c0d",
           "fad4b56351", "5f82acaf26", "fdcf52f2e9", "418798e583", "77b3aec47b", "23e452be7d", "9886698b39", "ad3439526c",
           "090f45e889", "8c3c7d6e37", "e439618286", "5ea11dc0bc", "6c69f837bb", "2456359430", "337dffb651", "dcf98de21b",
           "f6077e2114", "27ff8b75f0", "e843a980ba", "2ee930af13", "c822477434", "6da4e9ef2b", "fa51d4da27", "6e6288eba3",
           "cdc578a336", "af5ac32c91", "de504006ee", "1acaffc839", "24ff834f81", "279158d372", "f90b0c5113", "cd00088a9e",
           "00410dee37", "da5e30e7d5", "075998911f", "65befdb0cf", "9dba163201", "9e5d633260"):
    J[_d] = N(TEST, not_parts=["K2", "C4", "K1"])
J.update({
    "93f1cf837d": N(TEST + " (the test article: the board set as generated at the build's commit)"),
    "b073b98568": T(BOARDNAME),
    "368d0ce813": T("the gauge is board P's U1", "P:U1~BQ4050"),
    "3a01437772": T("U2's COUT reaches F2's heater through R29, JP1 and Q3; the thresholds are TI's", *PFLOOR),
    "8bb25c639e": T("TP11 is FUSE_G, COUT through R29; the procedure and the bounds are the test's", *PFLOOR),
    "05a162614f": T("U2's DOUT holds the discharge FET's gate DSG_G low through Q5", *PFLOOR),
    "edc54cfeab": T("Q5's gate is DOUT; Q2's gate DSG_G on R18's FET-side pad; the procedure is the test's", *PFLOOR),
    "3aa1dc5432": T("U2's own thermistor on J_TS2 through R34 and R33; the thresholds are TI's", "P:J_TS2.1=TS_SEC_J",
                    "P:R34.2=TS_SEC_J", "P:R34.1=TS_SEC", "P:R33.1=TS_SEC", "P:U2~BQ7720700"),
    "2c8801548e": T("F1 is the 25 A blade and F2 the 30 A SCF9550; the fuse curves are the makers'", "P:F1~25 A",
                    "P:F2~30 A"),
    "77b42b7b13": T("the parts that act with no firmware: U2, F2 through JP1 and Q3, Q5, F1", *PFLOOR),
    "ae832a28a0": N(H + " (the S-07 correction as generated at 45bde541)", *PBOARD),
    "a78c5399d6": T("the pack's two leads on board E", "E:J_BATT~XT60", "E:J_SMB.4=PRES_LEAD"),
    "8e69253a79": S("HOT-R1 is drawn in the generators of boards A and E since stream w4ae, so 'without it the run records the "
                    "generated path' describes a replaced state", *HOTR1),
    "5285a45c82": S("as 8e69253a79: HOT-R1 is in the generators of boards A and E since stream w4ae", *HOTR1),
    "d266582a0f": T("J_TS2, TP11 (FUSE_G, COUT) and Q5's gate (DOUT); the procedure is the test's", "P:J_TS2?",
                    "P:TP11.1=FUSE_G", "P:Q5.1=SEC_DOUT"),
    "361295de25": T("the network R34 and R33; the timings are TI's", "P:R34.1=TS_SEC", "P:R33.1=TS_SEC"),
    "38065665bd": T("RT1 on the gauge's PTC input", "P:RT1.1=PTC", "P:U1.23=PTC"),
    "58ad230920": T("J_TS carries TS1 to TS4 and ground; the procedure is the test's", "P:J_TS.1=TS1", "P:J_TS.4=TS4",
                    "P:J_TS.5=GND"),
    "3862859d08": T("board B's TMP117 and the HOT-R1 dock contact; the procedure is the test's", "B:U10~TMP117", *HOTR1),
})

# ================================================================== ASSEMBLY.md
EXISTS = "the part named exists on the board named (the names check); a connector's type is its footprint, not asserted"
for _d in ("b04a6b1603", "e87677183b", "07376ca281", "3fbdea5ae9", "7bb8442324", "a1079ff03a", "f235317b9f", "8cc644c978",
           "b6a3d866f0", "c2655f2943", "0969582f24", "1df73a9266", "b01b1874b5", "7e0af4aa94", "a3226d0e1b", "f1752455cd",
           "ceb537b912", "0b99dbc698", "a07ddb5431", "c2347385d2", "6b6ef36a29", "b42c3197e5", "edfc9fd60e", "454842f9d8",
           "8055befc30", "4ed7debafa", "6c2b997985", "32be340345", "db2c455e92", "89e7df7f4a", "51a31a4272", "06ac025b6c",
           "52ce1f8c71", "daad402b1d", "847a1d81ca", "82a018a5c9", "69aac94488", "999fee59d1", "1db85b209f", "45aad0383c",
           "9c5b940fec", "6d34ea0175", "4209111b84", "9c94802702", "eaad6c91e6", "aca374cf5e", "b949f05d20", "5258fad5f4",
           "3ad2e4231b", "9052faed29", "751ba352d8", "16e24b8857"):
    J[_d] = T(EXISTS, any_board=("J_FAN1", "J_FAN2"))
for _d in ("93fbb849cb", "732459982a", "15ed1aa70d", "928f453201", "f6703b4b72", "b65833d9c5", "ecea5966ca", "3864c187ad",
           "b213108c54", "c82c937aba", "842ee60d42", "2eaf29fb64", "e73bf0c766", "4f23d4bc1d", "9b023f257a", "24c6181ac7",
           "c95f2202d2", "b5e536304e", "97e934a201", "6055ac6d9f", "27280d94b4", "6a22616079", "fb41d688ef", "c534a1735f"):
    J[_d] = N("LEAD: how a lead ends or is made, not a netlist claim")
J.update({
    "6374505c78": T("build step 1's connectors exist on board E, with its three fuse holders F1 to F3; the order is the "
                    "procedure's", "E:J_DCIN?", "E:J_SOLAR?", "E:J_BATT~XT60", "E:J_SMB?", "E:J_TAMP?", "E:J_DCF?",
                    "E:J_GEIGER?", "E:J_LTG?", "E:J_POD?", "E:J_FAN1?", "E:J_FAN2?", "E:F1~Keystone", "E:F2~Keystone",
                    "E:F3~Keystone"),
    "00e44f7f0e": T("build step 6's sockets and pigtails exist on board B, the changeover outputs go to A22's P2P jacks",
                    "B:J_FAN1?", "B:J_FAN3?", "B:J_M2N1?", "B:J_M2N3?", "B:J_M2C1?", "B:J_M2C2?", "B:J_M2C3?", "B:J_W1A?",
                    "B:J_W3B?", "B:J_WOA~P2P", "B:J_WOB?", "A:J_RF6~P2P-A", "A:J_RF7~P2P-B"),
    "88e82bc9f0": T("the pack's two fuses on board P", "P:F1~25 A", "P:F2~SCF9550"),
    "f2abb6956f": T("W_P and W_N at gen_sch_p.py:347-348 at the base", "G@HEAD:gen_sch_p.py:347-348~W_P|W_N",
                    cite_ok="gen_sch_p.py:347-348 asserted below"),
    "a60b800d87": T("P's J_SMB at gen_sch_p.py:514; its order code is a BOM item", "P:J_SMB.3=PACK_N", "P:J_SMB.4=PRES_J",
                    "G@HEAD:gen_sch_p.py:514~J_SMB", cite_ok="gen_sch_p.py:514 asserted below"),
    "415b8a301b": S("its citation `gen_sch_e.py:218` is undated and that line now holds other code (J_SMB is at 273); it held "
                    "J_SMB at 45bde541; the pin order holds", "E:J_SMB.1=SMBC", "E:J_SMB.4=PRES_LEAD"),
    "20f3ba1ddd": N(H),
    "4a38904e7a": T("both ends' pin 3 and the gauge's only host on E", "P:J_SMB.3=PACK_N", "E:J_SMB.3=GND", "A:!J_SMB"),
    "a382a1aaea": T("the D8 5 V eFuse on A", "A:J_MEZZ_PWR1?", "A:*~D8"),
    "db20368ea7": T("the slot rails: AP64500 bucks on slots 1 and 3, an LM5176 stage on slot 2; the citation is dated",
                    "A:U4~AP64500", "A:U6~AP64500", "A:U5~LM5176", "G@45bde541:gen_sch_a.py:840-841~buck5",
                    "G@45bde541:gen_sch_a.py:873~lm5176", cite_ok="dated lines asserted below"),
    "d93d8c24ef": S("its citation `gen_sch_a.py:881` is undated and that line now holds other code (the device rail's U7 is at "
                    "1097); it held U7 at 45bde541; the stage holds", "A:U7~LM5176", "A:U7.12=+5V_DEV"),
    "6a24287f90": T("the PA rail is gated by the EMCON lines", *AGATES[:10], "A:U13~+13V8_PA"),
    "e5381bc58f": N("LEAD: the gate-bias lead", "D:J_VGG?"),
    "cded810b26": T("the HF rail is gated by the EMCON lines", *AGATES[10:15], "A:U15~+12V_HF"),
    "8b920ffb63": T("the monitor's eFuse on the pack node with its OVLO divider; the trip voltages are computed",
                    "A:U21.4=VBAT", "A:U21.5=VMON", "A:R92~143k", "A:R93~10k"),
    "29ab7f6956": N(DOCN + " (the touch lead's port, SC-HF-06)"),
    "86c164b77a": S("its citation `gen_sch_a.py:1015-1026` is undated and those lines now hold other code (U31 is at 1317); "
                    "they held J_USBC_OUT and U31 at 45bde541; the circuit holds", "A:U31.1=PD_CC1", "A:U31.2=PD_CC2"),
    "1edbe04f58": N(H),
    "d89e35b088": S("its citation `gen_sch_a.py:1613-1618` holds nothing at 45bde541 and other code at the base (J_USBW and "
                    "U32 are at 1668 and 1669); the circuit holds", "A:U32.5=VBUS_WALL", "A:U28@IO0_0=USBX_EN"),
    "07c344a956": N(H, not_parts=["J_USBX"]),
    "3b263770ff": S("its citation `gen_sch_a.py:1047-1076` is undated and those lines now hold other code (U33 is at 1373); "
                    "they held the heater stage at 45bde541; the circuit holds", "A:U33~TPS62933", "A:U22.5=VHEAT_IN"),
    "34e8b7c150": S("its citation `gen_sch_e.py:524-542` is undated and those lines now hold other code (J_TAMP is at 796); "
                    "they held the lid switch at 45bde541", "E:J_TAMP?"),
    "f4408c9dd4": S("its citation `gen_sch_b.py:1253-1272` is undated and those lines now hold other code (the SKY13351 "
                    "switches are at 2061); they held them at 45bde541", "B:J_WOA?", "B:*~SKY13351"),
    "53e544156a": N(CASE),
    "22fe281a54": N(CASE),
    "ea68c64a4d": S("J_DOCK's pins 1 to 4 are ground since EQ-16 (stream w3de moved VIN_RAW to its own pins J_VR1 to J_VR4) "
                    "and pin 12 is DOCK_SPARE, the HOT-R1 line, since stream w4ae; and its citations `gen_sch_a.py:225` and "
                    "`gen_sch_e.py:488` are undated, those lines now holding other code (J_DOCK is at 294, J_BLK at 660)",
                    "A:J_DOCK.1=GND", "A:J_VR1.1=VIN_RAW", "A:J_DOCK.12=DOCK_SPARE"),
    "f2fbb5a56a": N(FW + " (the commissioning procedure)"),
    "ebf7b76ff6": S("board A's round 8 makes PA_EN = TX_INHIBIT_n AND EMCON_HW AND PA_HOLD in U35 and U36 (HF likewise in U37 "
                    "and U38), and `gen_sch_a.py:535-537` now hold other code; R102 and R145 hold both lines low with the "
                    "ribbon out", *AGATES, "A:R102.1=EMCON_HW", "A:R145.1=TX_INHIBIT_n"),
    "dc6e921095": N(FW + " (the commissioning procedure)"),
    "b023a2e379": N(TEST + " (the commissioning procedure); D1 to D16, D3's tie D17 and the PI ring as PANEL.md section 9",
                    "C:D17.2=TX_K", "C:U2@IO0_2=PIRING_K"),
    "7857aaa69d": T("SHORE_INHIBIT high pulls the front end's UVLO through Q8 on board E; the second is the test's",
                    "E:Q8.1=SHORE_INHIBIT", "E:Q8.3=HS_UVLO"),
    "0a98178adb": N(TEST, not_parts=["K2", "C4"]),
    "c3f8dd9765": N(H),
    "1b157a50d3": N(FW + " (the procedure)"),
    "857ee4d62b": N(FW + " (the data-flash read-back)"),
    "42ab04ebc5": T("board P's second level and JP1 at gen_sch_p.py:476", *PBOARD, "G@HEAD:gen_sch_p.py:476~JP1"),
    "c54e91925e": N("LEAD: the bench-fit list; the parts named are A's", "A:*~Preci-Dip", "A:J_BM1~R222M00720", "A:*~Keystone 3568"),
    "3fa744781d": N("LEAD: the bench-fit list"),
    "dcfe5ddc9a": N("LEAD: the bench-fit list"),
    "18bf292849": N("LEAD: the bench-fit list"),
    "7211912728": N("LEAD: the bench-fit list"),
    "c648bf2ea2": N("LEAD: the bench-fit list; P's F1, J_CELL, J_TS, J_TS2, J_SMB and JP1 exist", "P:F1?", "P:J_CELL?",
                    "P:J_TS?", "P:J_TS2?", "P:J_SMB?", "P:JP1?"),
    "3d63f552f7": N("LEAD: board E5 is not netlisted"),
    "cd9739a701": N(CASE),
})

# ================================================================== added by the widened finder (rails, "as generated")
INA = ["A:U8~+5V_S1", "A:U8.1=GND", "A:U8.2=GND", "A:U9~+5V_S2", "A:U9.1=GND", "A:U9.2=+3V3", "A:U10~+5V_S3", "A:U10.1=+3V3",
       "A:U10.2=GND", "A:U11~+5V_DEV", "A:U11.1=+3V3", "A:U11.2=+3V3", "A:U14~PA rail", "A:U14.1=+3V3", "A:U14.2=SDA",
       "A:U17~PoE rail", "A:U17.1=+3V3", "A:U17.2=SCL", "A:SDA>U8,U9,U10,U11,U14,U17"]
J.update({
    "713ef78200": T("a row label: the LED rail is Q1's output", "C:Q1.3=LED_RAIL"),
    "827a5f9bfe": T("pins 1 and 2 are the +5V rail", "C:J_PANEL.1=+5V"),
    "dff88584fc": N(FW + " (slot fault supervision)"),
    "3ab575f161": S("the back-feed of SD-EMC-2 into the RockBLOCK, the E22 and the E72 is drawn since set 12 (U537 to U553 on "
                    "board B; check-int13-3, B1)", "B:U537.4=RB_GO", "B:U544.4=LORA_GO", "B:U540.6=ZBA_RXD"),
    "977cb01ecc": T("the six INA226 on board A's bus, their straps giving 0x40, 0x41, 0x44, 0x45, 0x46 and 0x47 by TI's table",
                    *INA),
    "86755cb169": N(DOCN),
    "cd6953b363": N(DOCN + " (the power state's figure)"),
    "5eb590e0b3": N(DOCN + " (REQ-071's latency); the 5G buck's enable is EMCON_HW AND PCIE_PWR_EN2", "B:U216.4=S2A_EN"),
    "caa82ce9b2": N(FW),
    "2468b4e4f8": N(DOCN + " (the heat stage, a column label)"),
    "94a798bc5f": N(DOCN + " (the banks' hosts, IOHA)"),
    "32a58b1f55": N(DOCN + " (the heat stage's shortfall)"),
    "a3abafe64f": N(DOCN + " (the banks' hosts, IOHA)"),
    "2db0811bda": N(DOCN),
    "ad58e8c6bc": N(DOCN),
    "529db80853": T("J_USBW is the Glenair's lead and J_USBC_OUT carries VBUS, CC1 and CC2 only", "A:J_USBW~233-370",
                    "A:J_USBW.2=USB_WALL_N", "A:J_USBC_OUT~power only", "A:J_USBC_OUT.1=PD_VBUS", "A:J_USBC_OUT.2=PD_CC1"),
    "dac478047f": N(H),
    "6d8b58cd7d": N(H),
    "3a41b60ff9": N(DOCN + " (a thermal table's row label)"),
    "33087d52ba": N(DOCN + " (a thermal table's row label)"),
    "af35e56cae": N(DOCN + " (a thermal table's row label)"),
    "b2237301f8": N(DOCN + " (a thermal table's row label)"),
    "22912384cc": N(DOCN + " (the altitude ruling and IEC 60664-1)"),
    "d84bfb5308": N(DOCN),
    "7c692c7420": T("a row label; the signals it lists are on J_MEZZ1 (which also carries EXP_INT and ZEROIZE_HW)",
                    "A:J_MEZZ1.1=USB_D8_P", "A:J_MEZZ1.7=TR_APRS", "A:J_MEZZ1.8=TX_INHIBIT_n", "A:J_MEZZ1.9=PA_EN",
                    "A:J_MEZZ1.10=SDA", "A:J_MEZZ1.13=+3V3"),
    "6a693c8a7f": N(TEST + " (the commissioning measurements)"),
    "8b28be5c56": N(TEST),
    "6f2a8e2a80": N(TEST),
    "9548d33e50": N(TEST),
})
J.update({
    "02d81ab6f6": N(H + " (the section's reading date; at the base its rows are 45bde541's, two of them stale)"),
    "4c1d0b24ec": N(H + " (correction 9's CFL-010 note)"),
})

# ================================================================== the corrected texts (apply_docs_s122.py)
DEVRAIL = ["A:U7~LM5176", "A:U7.12=+5V_DEV", "B:U25~AP63203", "B:U25.2=+5V_DEV", "B:U25.5=DEV_SW", "B:L1.1=DEV_SW",
           "B:L1.2=+3V3_DEV", "A:!~AP63203"]
BACKFEED = ["B:U537.1=RB_IEN", "B:U537.2=RB_STATUS", "B:U537.4=RB_GO", "B:U538.2=RB_GO", "B:U539.2=RB_GO",
            "B:U538.4=RB_RXD", "B:U539.4=RB_CTRL", "B:U544.2=E22_EN", "B:U544.4=LORA_GO", "B:U545.2=LORA_GO",
            "B:U546.2=LORA_GO", "B:U547.2=LORA_GO", "B:U548.2=LORA_GO", "B:U549.2=LORA_GO", "B:U550.2=LORA_GO",
            "B:U540~SN74LVC2G07", "B:U541~SN74LVC2G07", "B:U542~SN74LVC2G07", "B:U540.6=ZBA_RXD", "B:U542.6=ZBB_RXD",
            "B:+3V3_ZB>R536,R537,U22"]
FANS = ["B:J_FAN1.4=FAN_PWM1", "B:U30A@Fan_PWM=FAN_PWM1", "B:J_FAN1.3=FAN_TACHO1", "B:J_FAN2?", "B:J_FAN3?",
        "E:J_FAN1.3=FAN1_TACH", "E:U10.13=FAN1_TACH", "E:U10~RP2040", "E:Q9.3=FAN1_SW", "E:J_FAN1.2=FAN1_SW", "E:J_FAN2?"]
J.update({
    "b205d79502": T("U9 as drawn; the citation is dated at 45bde541, where lines 157 to 166 hold U9", *CCLAMP,
                    "G@45bde541:gen_sch_c.py:157-166~U9", not_parts=["C1"]),
    "59d336fd94": T("set 12's R52 and D23 on board C", *CCLAMP),
    "21cc359d9f": T("SHORE_INHIBIT on GPIO 20 and board A's dock contact; section 10 is the charge inhibit's",
                    "C:U3@GPIO20=SHORE_INHIBIT", "A:J_DOCK.8=SHORE_INHIBIT", "DOC:v2/docs/PANEL.md~## 10. Shore charge inhibit and the pack"),
    "cdbf8e9747": T("D8's KEY gate and board A's four gates; the citation is dated at the base; D22 through U14", *DKEY, *AGATES,
                    "G@e57a7365:gen_sch_a.py:1572-1575~U35|U36|U37|U38", "C:U14.3=TX_INHIBIT_n", "C:U14.6=EMCON_HW",
                    cite_ok="gen_sch_a.py:1572-1575 at e57a7365 asserted below"),
    "180ab5dbff": T("U9 through R52 with D23; B's R58 and A's R102", *CCLAMP, "B:R58~4.7k 1%", "B:R58.1=EMCON_HW",
                    "B:R58.2=GND", "A:R102~10k 1%", "A:R102.1=EMCON_HW", "A:R102.2=GND"),
    "05ad0e2bee": T("board A's gates (U26 dated at 45bde541) and board B's EMCON stages, the RockBLOCK clause with set 12's "
                    "R532, U543 and RB_GO gates; the 5G timing bound is EMCON.md's", *AGATES, "A:U26~outlet interlock",
                    "G@e57a7365:gen_sch_a.py:1572-1575~U35|U36|U37|U38", "G@45bde541:gen_sch_a.py:1102~U26|EMCON gates",
                    *LIME[:9], *RB, *E22[:4], *E72[:4], *INV, *CM5, *WIFI, *G5, "B:U506.2=EMCON_HW", "B:U506.4=EMCON_SUP",
                    "B:U506.5=+3V3_DEV", "B:U41@PC5=EMCON_SUP", "B:Q212~AO3400A", not_parts=["J3"],
                    cite_ok="the two citations asserted below"),
    "5516002037": T("set 12's back-feed gates", *BACKFEED),
    "907a184c68": T("U6's outputs and U7's inputs", "B:U6~0x20", "B:U7~0x25", "B:U6@IO0_0=KSZ_RST", "B:U6@IO0_1=LIME_SW_EN",
                    "B:U6@IO0_6=5G_OFF", "B:U6@IO1_0=WL_nDIS1_OFF", "B:U6@IO1_6=RB_SW_IEN", "B:U6@IO1_7=RB_CTRL_H",
                    "B:U539.1=RB_CTRL_H", "B:U7@IO0_3=RB_STATUS", "B:U7@IO0_1=RB_FLT", "B:SDA>U6,U7"),
    "8ca7a67ddf": T("every device the table names is on its board's SDA net at set 12 (the four netlists' shas); the "
                    "supervisors' and secure element's addresses are firmware or TBD", "SHA:A=6c40250c47195ebb",
                    "SHA:B=3ef9b8c49a01b728", "SHA:C=87b69472ac83ca5a", "SHA:D=a2d48972d171aad1",
                    "C:SDA>U_LIGHT,U1,U2,U3", "B:SDA>U6,U7,U5,U41,U51,U61,U10,U1,U8,U9", "A:SDA>U27,U28,U3", *INA,
                    "D:SDA>U16,U22", "D:U16~0x26", "B:U10~TMP117", "B:U1~KSZ9897", "B:U8~ATECC608B", "B:U9~DS3231SN",
                    "A:U3~BQ25731", "D:U22~ADS1115"),
    "b8b7972904": T("the startup fixes as drawn at the base; every citation is dated at 45bde541 and held these parts there",
                    "A:R42.1=DEV_EN", "A:R42.2=+3V3", "A:R4.1=KILL", "A:R4.2=+3V3", "A:R2.1=RAIL_EN", "A:R2.2=VBAT",
                    "A:R184.1=RAIL_EN", "A:R184.2=GND", "A:R103~4.7k", "A:R103.1=PA_SW_EN", "A:R104.1=HF_SW_EN",
                    "A:R111.1=MON_EN", "A:R112.1=HEAT_EN", "A:R114.1=POE_SW_EN", "A:R143.1=PD_SW_EN", "A:R21~4.7k",
                    "A:R21.1=CHG_INHIBIT", "A:R92~143k", "A:R93~10k", "A:R96~143k", "A:R97~10k",
                    "G@45bde541:gen_sch_a.py:887~R42", "G@45bde541:gen_sch_a.py:260-261~R2|R184|R4",
                    "G@45bde541:gen_sch_a.py:1112~R103", "G@45bde541:gen_sch_a.py:1125~R111",
                    "G@45bde541:gen_sch_a.py:1041-1064~143k|U22", "G@45bde541:gen_sch_e.py:524-542~TAMPER", "E:J_TAMP?",
                    not_parts=["C14"]),
    "0ad25b7483": T("the strap and the power path; the citations are dated", "A:R26~13.3k", "A:R26.2=CH_CELL",
                    "A:R27~40.2k", "A:R17.1=VBAT", "A:R17.2=CELL_FUSED", "A:U3~BQ25731",
                    "G@45bde541:gen_sch_a.py:764-771~R26|R27", "G@45bde541:gen_sch_a.py:18-48~VSYS|VBAT"),
    "9ff574acdc": T("J_USBW behind U32 and J_USBC_OUT power only; the citations are dated", "A:U32.5=VBUS_WALL",
                    "A:J_USBW.1=VBUS_WALL", "A:J_USBC_OUT~power only", "G@45bde541:gen_sch_a.py:1012-1015~J_USBC_OUT",
                    "G@45bde541:gen_sch_a.py:1151-1167~U32"),
    "e62bede18d": T("the count is check-int13-3's reading of the script; verdicts.py asserts the rest (U9, R52, D23 pins, "
                    "U214, U314, U22 to U24, LIME_HW_EN's source) in the 4b rows' judgements", *CCLAMP,
                    "B:U214.6=WL_nDIS2", "B:U214.4=BT_nDIS2", "B:U314.6=WL_nDIS3", "B:U22.5=E72_EN", "B:U22.1=+3V3_ZB",
                    "B:U23.3=LIME_UVLO", "B:U23.5=+5V_LIME", "B:U24.3=RB_UVLO", "B:U24.5=+5V_RB",
                    "B:U102@PWRCTL1=LIME_HW_EN",
                    "DOC:v2/docs/records/int13/checks/check-int13-3.md~\"146 pin assignments\" equals the count in `GATES` (55 parts)"),
    "e87f134a3f": T("the two rows it names describe board B's round 8 and set 12 (U25, U543)", "SHA:B=3ef9b8c49a01b728",
                    "B:U25~AP63203", "B:U543~TPS3808G30"),
    "0ef7259530": T("the two device-rail converters", *DEVRAIL),
    "b928cad57a": T("EMCON_ON per slot from the module's own 3.3 V; U543 on RB_IEN; EMCON.md records L3 closed", *INV,
                    "B:U113.5=+3V3_CM1", "B:U213.5=+3V3_CM2", "B:U313.5=+3V3_CM3", "B:!U111", "B:!U211", "B:!U311",
                    "B:U543.1=RB_IEN", "B:U543.5=+3V3_DEV", "B:U543.6=+5V_DEV",
                    "DOC:v2/docs/feasibility/EMCON.md~CLOSED at desk on board B's round 8 (section 4b)"),
    "7487ce55af": T("the mixer fans' tachometers reach E's RP2040; the citation is dated; the thermal figures are the record's",
                    "E:U10.13=FAN1_TACH", "G@45bde541:gen_sch_e.py:503~fan tachometers", not_parts=["C1"]),
    "e61cba608f": T("board P's second level; HOT-R1 on boards E and A", *PBOARD, *HOTR1),
    "6b8e35c93d": T("the holdover clock is B's DS3231SN on the kit bus that C's RP2040 masters; the time pulses are the "
                    "correction 8 record's", "B:U9~DS3231SN", "B:U9.15=SDA", "C:U3@GPIO0=SDA", "B:SDA>J_PANEL"),
    "286e14a698": T("the fans: the coolers on their modules, the mixers on E's sensor controller; the thermal text is the "
                    "record's", *FANS),
    "0aa470c049": T("U536 forces the ENABLE low; the rest of the list is owed items and history", *RB[:20], "B:J_M2C2~2199119",
                    "B:U222~TPD4E001"),
    "ee30c5f3b0": T("the device-rail converters on A and B; the ribbon, the Ethernet switch and the bus as drawn", *DEVRAIL,
                    "B:J_PANEL?", "B:U1~KSZ9897"),
    "40843cefa1": T("U536 and U543", *RB[:20]),
    "812d88d5de": T("B's DS3231SN on the kit bus", "B:U9~DS3231SN", "B:U9.15=SDA", "C:U3@GPIO0=SDA"),
    "54c522b504": T("the device-rail converters", *DEVRAIL),
    "27245f25a2": T("the fans' drivers", *FANS),
    "4dc19331ec": T("HOT-R1 on E and A; the requirement and the budget are the registry's and the record's", *HOTR1),
    "dfd6170bf6": T("U18 TPS25740A and U19 LM5176; the citation is dated", "A:U18~TPS25740A", "A:U19~LM5176",
                    "G@45bde541:gen_sch_a.py:1003~TPS25740A"),
    "ddf7f04dc3": T("EMCON is a hardware line on every transmitter, as the corrected paragraph below sets out; the modes are "
                    "the design's", *DKEY, *CM5[:5], *LIME[:5], *AGATES[:5]),
    "f7d96bf556": T("the RockBLOCK's ENABLE is forced low by U536; the owed items are EMCON.md's", *RB[:20]),
    "8e9b0a789c": T("HOT-R1 in the generators of E and A; the test procedure is the plan's", *HOTR1),
    "bf19feeb76": T("HOT-R1 in the generators of E and A; the test article is the plan's", *HOTR1),
    "7085887937": T("E's J_SMB pin order; PRES reaches U10 pin 28 (GPIO17 on the RP2040's QFN-56) through R54; the "
                    "citation is dated", "E:J_SMB.1=SMBC", "E:J_SMB.2=SMBD",
                    "E:J_SMB.3=GND", "E:J_SMB.4=PRES_LEAD", "E:R54.1=PRES_LEAD", "E:R54.2=PRES_IO", "E:U10.28=PRES_IO",
                    "G@45bde541:gen_sch_e.py:218~J_SMB"),
    "b4d813c5fb": T("the device rail's LM5176; the citation is dated", "A:U7~LM5176", "A:U7.12=+5V_DEV",
                    "G@45bde541:gen_sch_a.py:881~U7|+5V_DEV",
                    cite_ok="gen_sch_a.py:881 at 45bde541 asserted below"),
    "5cfe79e7d4": T("J_USBC_OUT's five pins and U31 on CC1 and CC2; the citation is dated", "A:J_USBC_OUT.1=PD_VBUS",
                    "A:J_USBC_OUT.2=PD_CC1", "A:J_USBC_OUT.3=PD_CC2", "A:U31.1=PD_CC1", "A:U31.2=PD_CC2",
                    "G@45bde541:gen_sch_a.py:1015-1026~J_USBC_OUT|U31"),
    "738f2d1fa0": T("J_USBW's pins, U32 and its expander enable; the citation is dated at the base; the limit is TI's equation",
                    "A:J_USBW.1=VBUS_WALL", "A:J_USBW.2=USB_WALL_N", "A:J_USBW.3=USB_WALL_P", "A:U32.5=VBUS_WALL",
                    "A:U32.3=USBX_EN", "A:U28@IO0_0=USBX_EN", "A:J_AB2?", "G@e57a7365:gen_sch_a.py:1668-1669~J_USBW|U32"),
    "43b888438d": T("the heater stage U33 behind U22; the citation is dated", "A:U33~TPS62933", "A:U33.3=VHEAT_IN",
                    "A:U22.5=VHEAT_IN", "G@45bde541:gen_sch_a.py:1047-1076~U33|VHEAT"),
    "89f370c964": T("J_TAMP on E; the citation is dated", "E:J_TAMP?", "G@45bde541:gen_sch_e.py:524-542~TAMPER"),
    "ca405f41c2": T("J_WOA and J_WOB and the SKY13351 switches; the citation is dated", "B:J_WOA?", "B:J_WOB?",
                    "B:*~SKY13351", "G@45bde541:gen_sch_b.py:1253-1272~SKY13351|WIFI_SEC",
                    cite_ok="gen_sch_b.py:1253-1272 at 45bde541 asserted below"),
    "2fb6d0d9bc": T("J_DOCK's pins and the VIN_RAW pins; the citations are dated", "A:J_DOCK~Preci-Dip 813", "A:J_DOCK.1=GND",
                    "A:J_DOCK.7=GND", "A:J_DOCK.8=SHORE_INHIBIT", "A:J_DOCK.9=USB_E6_P", "A:J_DOCK.10=USB_E6_N",
                    "A:J_DOCK.11=GND", "A:J_DOCK.12=DOCK_SPARE", "A:J_VR1~9 A", "A:J_VR1.1=VIN_RAW", "A:J_VR4.1=VIN_RAW",
                    "E:J_BLK.12=BLK_SPARE", "G@e57a7365:gen_sch_a.py:294~J_DOCK", "G@e57a7365:gen_sch_e.py:660~J_BLK",
                    "G@45bde541:gen_sch_a.py:225~J_DOCK", "G@45bde541:gen_sch_e.py:488~J_BLK",
                    cite_ok="the four citations asserted below"),
    "7062eeadc4": T("board A's PA and HF gates and the ribbon-out pulls; the citations are dated at the base", *AGATES,
                    "A:R102.1=EMCON_HW", "A:R102.2=GND", "A:R145.1=TX_INHIBIT_n", "A:R145.2=GND",
                    "G@e57a7365:gen_sch_a.py:1572-1575~U35|U36|U37|U38", "G@e57a7365:gen_sch_a.py:1597-1598~R102|R145",
                    cite_ok="the citations asserted below"),
})


# ================================================================== ROUND 2 (the baseline rule, set 13, the check's items)
def B(kept, why, *a, **kw):
    d = {"v": "B", "kept": kept, "why": why, "a": list(a)}
    d.update(kw)
    return d


EMCONMOVE = "the circuit set 12 wrote into CONOPS 4b and its EMCON row, kept in EMCON.md section 0a.1"
# CONOPS.md at c5430071: the passages whose values differ from set 13, or that cite generator lines, are baseline values
J.update({
    "078d294b3f": B("DC-06", "undated generator line citations (gen_sch_a.py 887, 260 and 261, 763, 1009, 1112, 1125, 1041 to 1064; "
                    "gen_sch_e.py 524 to 542): baseline values; the parts they name hold on set 13", "A:R42.1=DEV_EN", "A:R4.1=KILL"),
    "98554054a3": B("DC-06", "undated citations gen_sch_a.py 764 to 771 and 18 to 48: baseline values", "A:R26~13.3k"),
    "6b2997fde7": B("DC-06", "undated citations gen_sch_a.py 1012 to 1015 and 1151 to 1167: baseline values", "A:U32.5=VBUS_WALL"),
    "b9f6eebae8": B("DC-04", "both device-rail converters put on board A; +3V3_DEV is board B's U25", "B:U25.5=DEV_SW"),
    "a8a12c6168": B("DC-05", "U{s}11 and an open L3; each slot makes EMCON_ON from its own 3.3 V since round 8", "B:!U111"),
    "e58fe90ad4": B("DC-06", "the undated citation gen_sch_e.py line 503: a baseline value"),
    "4fcc861597": B("DC-02", "HOT-R1 called owed on boards A and E; drawn since stream w4ae", "E:Q11.3=BLK_SPARE"),
    "7d60fee70d": B("DC-03", "check-s122-1 B3: the TX lamp does not act without the panel controller (D3's feed LED_RAIL needs "
                    "PANEL_PWM); SLOT_EN1 to 3 do fall to their pull-downs", "C:R36.1=LED_RAIL", "C:Q1.3=LED_RAIL",
                    "C:R20.2=GND", *SLOTPD),
    "68adf0cbe9": N(DOCN + " (a table label)"), "558254e36d": N(DOCN), "de5a835322": N(FW + " (M4's sequence)"),
    "edb4c3e127": N(DOCN), "1d9b5fd4ae": N(DOCN + " (the radios' behaviour with their supplies removed)"),
    "7a24129764": B("DC-06", "the undated citation gen_sch_e.py line 213: a baseline value; the SHUTDOWN command is firmware"),
    "9ef4aaf6d5": T("board P's floor; the citation is dated at 45bde541; the PTC behaviour is TI's", *PBOARD,
                    "G@45bde541:gen_sch_p.py:243~RT1", "G@45bde541:gen_sch_p.py:288~F2"),
    "8da8b38408": N(DOCN), "abfff5e29b": N(DOCN + " (board E's always-on domain and the lid log)", counts_ok="no part count"),
    "9a63ddab19": N(DOCN), "09c32df319": N(DOCN), "a00a32d68e": N(DOCN),
    "16bf264783": B("DC-06", "the undated citation gen_sch_e.py lines 524 to 542: a baseline value; J_TAMP holds", "E:J_TAMP?"),
    "8a590ed76e": N(DOCN), "9f161f4104": N(DOCN + " (the banks' hosts, IOHA)"), "5feb94af38": N(DOCN + " (BANK-R1)"),
    "d5d59c71d0": N(FW), "8e2b2ea5c9": N(DOCN + " (FAB-02, FAB-03, IOHA section 6)"), "f743367dd5": N(DOCN),
    "9b1e20e0de": N(DOCN), "82a761d909": N(DOCN), "93c44b9635": N(FW, "B:U10~TMP117"), "9574902452": N(DOCN),
    "b790d7f1a1": N(DOCN), "36447f2d08": N(DOCN), "6fba985383": N(DOCN),
    "262c688460": B("DC-02", "'as generated the hot stop has no path in this stage until HOT-R1 is in the generators of boards A "
                    "and E': HOT-R1 is drawn since stream w4ae (check-s122-1 B1)", "E:Q11.3=BLK_SPARE"),
    "f6ddbeef1e": N(DOCN), "f44ab6405c": N(DOCN), "074bdf07a1": N(DOCN + " (BANK-R1, REQ-052)"), "c69b286435": N(DOCN),
    "769ef9425a": N(DOCN),
    "2cb143c7d1": T("HOT-R1 carries the sensor controller's reading to the panel controller; the thresholds are firmware", *HOTR1),
    "eab5786914": N(FW), "1e105a4e11": N(FW + " (H1 and H2's actions)"), "4237a1ce78": N(DOCN),
    "9da9566684": B("DC-02", "'HOT-R1 is owed on boards A and E ... the hot stop's requirement reads FAIL': drawn since w4ae, and "
                    "REQ-077 reads INCONCLUSIVE (check-s122-1 B1)", "REG:REQ-077.evidence_result=INCONCLUSIVE"),
    "5f7482837f": N(DOCN), "a7ed81b544": N(DOCN), "3ea9638a6b": N(DOCN), "ea18504b75": N(DOCN + " (a table label)"),
    "5c2c10a0f9": T("the removals the cell names hold on set 13", *LIME[:5], *RB[:10], *E22[:6], *E72[:6], *WIFI[:6],
                    *CM5[:5], *G5[:8], *AGATES[:10], *DKEY),
    "47c7434e18": B("DC-01", "the RockBLOCK's ENABLE 'held by firmware until forced low in hardware': forced low since w4b",
                    "B:U536.4=RB_IEN_DRV"),
    "4820fce7d1": N(H + " (the row's sources, dated at 45bde541)"),
    "b320678434": B("DC-01", "the owed list names the RockBLOCK's ENABLE, U501 to U505's supplies and the back-feed paths, which "
                    "w4b and set 12 draw", "B:U537.4=RB_GO"),
    "2311d1e5a3": T("BLACKOUT opens LED_RAIL_SW at SW_LIGHT; the TX lamp is fed from LED_RAIL behind it; the monitor is firmware",
                    "C:SW_LIGHT.1=LED_RAIL_SW", "C:R36.1=LED_RAIL", "C:R17.1=LED_RAIL_SW"),
    "56f2d65de4": N(FW), "caf0c4a9b6": T("the SOS toggle", "C:SW_SOS~APEM", "C:SW_SOS.1=SOS_SW"), "b2e82136b4": N(FW),
    "6eb2169c99": N(FW + " (the graceful shutdown)"), "51f062570a": N(DOCN), "9aeddb2745": N(DOCN), "5154135d03": N(DOCN),
    "880202b398": N(DOCN), "7d0804b534": N(DOCN), "9ae1bb37fb": N(DOCN), "bdd135f6a0": N(DOCN), "fff8a9c868": N(DOCN),
    "3abf30a0b4": N(DOCN), "2ee111473e": N(DOCN), "b8067f4b16": N(DOCN), "3e5b29424e": N(DOCN), "88616c53b8": N(DOCN),
    "28a652dda6": B("DC-01", "section 4b read at 45bde541: a baseline value"),
    "52a4e778cd": B("DC-01", "'board B inverts it once into EMCON_ON': per slot since round 8"),
    "8120d05470": B("DC-01", "the round 8 framing of rows that name parts round 8 removed", *INV),
    "e7f1fe94db": N(DOCN + " (a table header)"), "24e19375d5": N(DOCN + " (a table header)"),
    "fb572a976c": T("the LimeSDR's gates", *LIME), "897ad942fd": T("the RockBLOCK's supply gate", *RB[:12]),
    "e041fe99ae": B("DC-01", "'ENABLE driven only by the firmware expander U6': U536 since w4b", "B:U536.1=EMCON_HW"),
    "6d18087abd": N(DOCN), "a7618b1948": B("DC-01", "'TXEN driven by slot 3 and not on the line': gated by U546 since set 12",
                                           "B:U546.4=LORA_TXEN_G"),
    "9320819e27": T("the E72s' switch", *E72[:8]),
    "ecebddd7eb": B("DC-01", "'the enable of its 3.3 V buck pulled low by U215': U216 drives it since w4b", "B:U216.4=S2A_EN"),
    "4457d2e3b3": N(DOCN + " (the 5G timing bound and Quectel's warning)", *G5[:4]),
    "0cca8b2ab1": T("a row label: the two E-key card sockets", "B:#val~M.2 E-key=2"),
    "7d9a058f84": B("DC-01", "'buck enables pulled low by U115 and U315': U116 and U316 since w4b", "B:U116.4=S1A_EN"),
    "e4b55bda98": B("DC-01", "board A 'as U26' and a round 8 candidate: U35 to U38 since round 8", *AGATES[:5]),
    "1ab30cc2c3": B("DC-01", "board A's HF gate 'as U26' and a candidate at gen_sch_a.py 1240 to 1243", *AGATES[10:15]),
    "e25495282b": T("the module radios' disables", *CM5),
    "884b121988": N(FW), "50bd10e730": N(CASE + " and procedure (the lamp's light guide, S-44)"), "95a2617bb5": N(DOCN),
    "9016ffee8d": B("DC-06", "the undated citation gen_sch_b.py line 543: a baseline value"),
    "595a8adabd": N(DOCN), "1eb6e6d5f1": N(DOCN),
    "f6adfad9fd": T("the reed on board E's J_TAMP reaches the sensor controller", "E:J_TAMP?", "E:R53.2=TAMPER_IO",
                    "E:U10~RP2040"),
    "6f0927f98d": N(FW), "186a997856": N(DOCN), "ed9266a99c": N(DOCN),
    "16ec1f5b7e": B("DC-06", "the undated citation gen_sch_e.py lines 524 to 542: a baseline value"),
    "66308c1c0a": N(FW), "793088207a": N(DOCN), "a9e17ab4ef": N(FW), "54480cee4b": N(DOCN), "41e7a34032": N(DOCN),
    "890ba02017": N(DOCN), "73cfcd90ed": N(DOCN), "e2340ccf73": N(DOCN), "d51e5a087d": N(DOCN), "7120babddf": N(DOCN),
    "1021385ed3": B("DC-06", "the undated citation gen_sch_a.py line 708: a baseline value; the charger is U3 at 0x6B",
                    "A:U3~BQ25731", "A:R17.1=VBAT"),
    "51863c60c0": N(DOCN), "fce8982259": N(DOCN), "5861d3a6dc": N(DOCN), "2cfa3e4456": N(DOCN), "a9c9263a9c": N(DOCN),
    "ec1bcec9ee": N(FW + " (H1's actions)"),
    "ba478072d4": T("PI_KILL drives Q1 onto the LTC2954's KILL, and RAIL_EN is its enable output", "A:Q1.1=PI_KILL",
                    "A:Q1.3=KILL", "A:U1.8=KILL", "A:U1.6=RAIL_EN"),
    "08eb218ebf": N(DOCN), "1d62d9281b": N(DOCN), "59487d3474": N(DOCN),
    "6c3fe4cb16": B("DC-06", "the undated citation gen_sch_a.py line 782: a baseline value; CHG_INHIBIT drives Q6 to CHG_ILIM",
                    "A:Q6.1=CHG_INHIBIT", "A:Q6.3=CHG_ILIM"),
    "a39e29dbec": B("DC-06", "generator line numbers read at a8652172: baseline values", "E:U10~RP2040", "E:J_SMB.1=SMBC"),
    "1a31a2702b": N(DOCN + " (the path through a compute module, without HOT-R1)"),
    "f903e11a1d": B("DC-02", "HOT-R1 'owed', BLK_SPARE's only other node 'TP7': Q11 is on it since w4ae (check-s122-1 B1)",
                    "E:BLK_SPARE>J_BLK,Q11,TP7"),
    "c16b6d1eee": B("DC-02", "'U10 pin 30, not connected as generated': it is HOT_R1_G since w4ae", "E:U10.30=HOT_R1_G"),
    "5f4b8157ee": B("DC-06", "the undated citation gen_sch_b.py line 1050: a baseline value", "B:U10~TMP117"),
    "48ece64cc2": N(DOCN), "1d7e94cee4": N(DOCN), "99436911e7": N(DOCN), "8d098165cb": N(DOCN), "b9ac9cbf8e": N(DOCN),
    "43d35f62a5": N(DOCN),
    "194799b04d": B("DC-06", "the undated citation gen_sch_b.py lines 764 to 766 (PORTS): a baseline value"),
    "1429a7fedf": N(DOCN + " (BANK-R1's proposal)"),
    "7c6db0f4ce": B("DC-06", "the undated citation check_pcb_b.py lines 424 to 431: a baseline value"),
    "21d357abe6": N(DOCN), "eb7aaa0ccb": N(DOCN), "8888bcaa64": N(DOCN), "016ba4851a": N(DOCN),
    "0c553f1199": N(DOCN), "7c5672ad1c": N(DOCN), "c33e60f0c6": N(FW), "44977e52c4": N(DOCN), "ed071e5b5d": N(FW),
    "4c32fc5afa": N(DOCN), "04a3a0de64": N(DOCN), "961444e55b": N(DOCN), "b794f2d604": N(FW), "4acf97c26a": N(FW),
    "3b0e9dedbe": N(DOCN), "b2619366e1": N(DOCN), "d45694c0e4": N(DOCN), "f2898cc56d": N(DOCN),
    "47da113df0": B("DC-02", "'once HOT-R1 is in the generators of boards A and E (the requirement reads FAIL until then)': drawn "
                    "since w4ae, REQ-077 INCONCLUSIVE (check-s122-1 B1)", "REG:REQ-077.evidence_result=INCONCLUSIVE"),
    "0ef7a34880": N(DOCN), "043a292a98": N(DOCN), "2c6403daa6": N(FW), "563441d68e": N(TEST), "c61eb8f91d": N(DOCN),
    "c7a398ef63": N(DOCN), "7afd6cf8ef": N(DOCN), "58c5dd5d14": N(DOCN), "d509f0d43d": N(FW), "025fe974ad": N(FW),
    "26986a1d9d": N(DOCN), "dd37381138": N(FW), "b72e2ec123": N(DOCN), "805be5c76e": N(TEST), "9d93b39b55": N(FW, *PBOARD),
    "c42d5042b3": N(FW), "beabaf8862": N(TEST),
})

# the other documents' new or changed texts
J.update({
    "0d1bf77d7e": N(DOCN + " (a row label)"),
    "be4c0e788e": T("GPIO 2 and 3 since set 13", "C:U3@GPIO2=EPD_SCL_R", "C:U3@GPIO3=EPD_SDA_R"),
    "c0d0d401ee": T("R53 and R54 to J_EPD; the iTC mode is PDi's", "C:R53~27R", "C:R53.1=EPD_SCL_R", "C:R53.2=EPD_SCL",
                    "C:R54~27R", "C:R54.1=EPD_SDA_R", "C:R54.2=EPD_SDA", "C:J_EPD.13=EPD_SCL", "C:J_EPD.14=EPD_SDA"),
    "e0190a4f4c": T("GPIO 4 to 7 since set 13", "C:U3@GPIO4=EPD_DC_R", "C:U3@GPIO5=EPD_CS_R", "C:U3@GPIO6=EPD_RST",
                    "C:U3@GPIO7=EPD_BUSY"),
    "e67f4c1e6c": T("R55 and R56 to J_EPD", "C:R55.1=EPD_DC_R", "C:R55.2=EPD_DC", "C:R56.1=EPD_CS_R", "C:R56.2=EPD_CS",
                    "C:J_EPD.11=EPD_DC", "C:J_EPD.12=EPD_CS", "C:J_EPD.9=EPD_BUSY"),
    "0dec673185": N(FW + " (debounce); the two maintained toggles are SOS and ZEROIZE", "C:#val~maintained=2"),
    "fc8851e8bd": T("per slot HBn in, SLOT_ENn out, the selects", "C:U3@GPIO10=HB1", "C:U3@GPIO13=SLOT_EN1",
                    "C:U3@GPIO16=HDMI_SEL1"),
    "7aab87b020": N(DOCN), "d53cc00f10": N(DOCN), "780f73dd5e": N(H), "e6caa6c8fa": N(FW), "1303e44db8": N(FW),
    "541ce3dddd": T("re-read at set 13: every device of the table on its board's SDA net", "SHA:A=6c40250c47195ebb",
                    "SHA:B=3ef9b8c49a01b728", "SHA:C=c9f7394594201045", "SHA:D=a2d48972d171aad1",
                    "C:SDA>U_LIGHT,U1,U2,U3", "B:SDA>U6,U7,U5,U41,U51,U61,U10,U1,U8,U9", "A:SDA>U27,U28,U3", *INA,
                    "D:SDA>U16,U22"),
    "72057ed854": N(DOCN + " (the requirement, correction 29)"),
    "74b5364ce8": T("the seven-port KSZ9897R on B16; the three slots are the receptacle pairs", "B:U1~seven-port Gigabit",
                    "B:U30A?", "B:U31A?", "B:U32A?", counts_ok="the three slots: U30, U31 and U32 (asserted)"),
    "90a63397b8": T("the attachments as drawn", "B:U548.1=SPI3_MOSI", "B:#val~M.2 E-key=2", "B:SDA>U8,U9,U10",
                    "B:U8~ATECC608B", "B:U9~DS3231SN", "B:U10~TMP117"),
    "d3e7d3ae2a": N(DOCN + " (the panel controller's functions)"),
    "013c77ba2f": T("the switches' makers as their value texts; the covers are a plate item", "C:#val~APEM=3",
                    "C:#val~C&K=3", "C:SW_LIGHT~NKK"),
    "aecdadb86d": N(FW), "1680565a78": N(DOCN + " (the audio path)", "C:#ref~J_HSJ=2", "D:#ref~J_HS=2"),
    "2baa3139db": N(DOCN), "ea18504b75": N(DOCN + " (a table label)"),
    "de16befa62": N(T7 + "; its USB-C clause corrected (correction 32)", "A:U18~TPS25740A", "A:U19~LM5176",
                    "A:#val~rail monitor +5V_S=3"),
    "b1e7494b6d": N(T7 + "; its supervisors' clause corrected (correction 32)", "B:#val~STM32H743=3",
                    "B:#val~PI7C9X2G404=3", "REG:CON-017.evidence_result=PASS"),
    "fa00f9ca7e": N(T7, counts_ok="the 7 September board C's sixteen LEDs; D22 came in board C's round 8"),
    "ac1bd47d91": N(DOCN + " (the cost estimate of 6 September 2026)", counts_ok="the estimate's items, not the netlist"),
    "36abc030f1": N(DOCN + " (the cost estimate of 6 September 2026)", counts_ok="the estimate's items, not the netlist"),
    "287efa15f6": N(DOCN + " (the cost estimate of 6 September 2026)", counts_ok="the estimate's items, not the netlist"),
    "0c3fab1f42": N(H), "93ed4f24e0": N(H), "485179e54c": N(H), "110d02f908": N(H), "a7523e86eb": N(H),
    "49f8f5b4bc": T("the switch chip", "B:U1~seven-port Gigabit"),
    "269867362d": T("the TPS55288 left before 7 September; the outlet's parts", "G@c5de605d:gen_sch_a.py:267~TPS55288",
                    "A:U18~TPS25740A", "A:U19~LM5176", "A:!~TPS55288"),
    "7e0ae0ffa3": T("the supervisors' value texts and CON-017", "B:#val~STM32H743=3", "REG:CON-017.evidence_result=PASS"),
    "5e98fc1920": N(DOCN + " (a table row)", counts_ok="a row label"),
    "ae0e5de42a": N(DOCN + " (a table row)", "B:#val~M.2 M-key=3"),
    "ab5d01673b": N(DOCN, "E:#ref~J_FAN=2", "B:#ref~J_FAN=3"),
    "8a93588273": N(DOCN, "E:#ref~J_FAN=2", "B:#ref~J_FAN=3"),
    "46ff45e4c7": N(FW + " (the cold warm-up)", "B:#val~M.2 E-key=2"),
    "31742badcd": N(H), "b3371cfe6d": N(CASE), "5bc0a319b6": N(CASE), "0c1bffdaf6": N(FW), "bd1fd7b207": N(CASE),
    "cc0ec17c8e": T("board A's seventeen 0858 class pins", "A:#fp~Mill-Max_0858=17", "A:#ref~J_CP=4", "A:#ref~J_CN=4",
                    "A:J_PRE1?", "A:#ref~J_VR=4", "A:#ref~J_VN=4", "A:J_DOCK~Preci-Dip 813-S1-012-10-016101",
                    "A:#ref~J_BM=11"),
    "c35cc9b3e6": T("build step 5's leads exist on A and D; the order is the procedure's", "A:J_MEZZ1?", "D:J_HARN1?",
                    "A:J_MEZZ_PWR1?", "D:J_PWR1?", "D:J_ANT?", "A:J_RF1?", "D:J_PAIN?", "D:J_PAOUT?", "D:J_VGG?", "A:J_PA?"),
    "d392049f19": T("the pack's leads and sockets; the citation holds at the base", "G@HEAD:gen_sch_p.py:347-348~W_P|W_N",
                    "E:J_BATT~XT60", "E:J_SMB.4=PRES_LEAD", cite_ok="gen_sch_p.py:347-348 asserted below"),
    "e458a114de": T("JP1, the arming jumper, open as built", "P:JP1~arming"),
    "ef9f31ab35": N(H + " (dated at 45bde541)"), "c9b8e32045": N(CASE), "d31d56293d": N(CASE), "9c64ead2c3": N(CASE),
    "1356d08c69": N(CASE),
    "8b1e16653a": N(CASE, counts_ok="the plate's sixteen light guides; D22's guide is owed (S-44)"),
    "6a419ebbdc": N(TEST), "643c162767": T("the QMX leads' ends", "B:J_QMX?", "A:J_HF?", "A:J_RF2?"),
    "040a11165b": N(CASE), "08579360c0": T("the two mixer fans' headers on E", "E:#ref~J_FAN=2"),
    "047622834a": N("LEAD: the cards' connectors", "B:#val~M.2 E-key=2"), "3a53e10db7": N("LEAD: the plug"),
    "c8263105e0": T("J_DOCK's twelve pins and the VIN_RAW pins; the citations are dated", "A:J_DOCK.1=GND",
                    "A:J_DOCK.4=GND", "A:J_DOCK.7=GND", "A:J_DOCK.8=SHORE_INHIBIT", "A:J_DOCK.9=USB_E6_P",
                    "A:J_DOCK.10=USB_E6_N", "A:J_DOCK.11=GND", "A:J_DOCK.12=DOCK_SPARE", "A:#ref~J_VR=4", "A:#ref~J_VN=4",
                    "A:J_VR1.1=VIN_RAW", "A:J_VN1.1=GND", "G@e57a7365:gen_sch_a.py:294~J_DOCK",
                    "G@e57a7365:gen_sch_e.py:660~J_BLK", "G@45bde541:gen_sch_a.py:225~J_DOCK",
                    "G@45bde541:gen_sch_e.py:488~J_BLK", cite_ok="the four citations asserted below",
                    counts_ok="twelve contacts: J_DOCK's pins asserted"),
    "e050e55b92": T("the nine pack pins: four on the node, four on the return, one pre-charge", "A:#ref~J_CP=4",
                    "A:#ref~J_CN=4", "A:J_PRE1?"),
    "e8eeaca71e": T("board A's gates and pulls; the citations are dated at the base", *AGATES, "A:R102.1=EMCON_HW",
                    "A:R145.1=TX_INHIBIT_n", "G@e57a7365:gen_sch_a.py:1572-1575~U35|U36|U37|U38",
                    "G@e57a7365:gen_sch_a.py:1597-1598~R102|R145", cite_ok="the citations asserted below"),
    "f6186bbdf0": T("board A's bench-fit counts", "A:#fp~Mill-Max_0858=17", "A:#ref~J_BM=11", "A:J_BM1~R222M00720",
                    "A:F1~Keystone 3568", "A:J_DOCK~Preci-Dip 813-S1-012-10-016101"),
    "a039b91bf4": T("board B's bench-fit counts", "B:#val~M.2 E-key=2", "B:#ref~J_FAN=3", "B:#val~M.2 M-key=3",
                    "B:J_M2C2~2199119", "B:J_LIME?", "B:J_RB9704?"),
    "73ff7b42ab": T("board C's bench-fit counts", "C:#fp~LED_D3.0mm=17", "C:D22~EMCON", "C:#val~APEM=3", "C:#val~C&K=3",
                    "C:#ref~J_HSJ=2", "C:SW_LIGHT~NKK", "C:J_EPD~24"),
    # EMCON.md section 0a.1
    "44fef7001d": T("the four netlists read", "SHA:A=6c40250c47195ebb", "SHA:B=3ef9b8c49a01b728", "SHA:C=c9f7394594201045",
                    "SHA:D=a2d48972d171aad1"),
    "892ede8107": T("what the round 2 script asserted before writing (its list EMCON_A, 497 assertions in its run with the "
                    "edits' own); the parts it names", *CCLAMP, "B:U214.6=WL_nDIS2", "B:U314.6=WL_nDIS3", "B:U22.5=E72_EN",
                    "B:U23.3=LIME_UVLO", "B:U24.3=RB_UVLO", "B:U102@PWRCTL1=LIME_HW_EN", "B:U540.1=ZBA_RXD_H",
                    "B:U547.1=SPI3_IO26", "B:F3.2=VBUS_QMX"),
    "1e5189646e": T("the RockBLOCK's gates", *RB), "9620597168": N(DOCN + " (the module's supercapacitors and ENABLE response)"),
    "3464fb191d": T("the E22's gates", *E22), "ee4a0bea78": T("the E72s' gates", *E72),
    "e0170ac9ad": T("the SA868 and PA gates and the exciter's ungated supply", *DKEY, *AGATES, "D:U2.8=+5V_SA",
                    "D:FB1.1=+5V_TX", "D:U21.1=+5V_TX", "D:U21.5=TXSUP_EN", "D:U15.4=PA_KEY"),
    "ee2e5858d0": T("the hardware paths named; the module's behaviour is a held-document item, said so", *RB[:20], *DKEY),
    "7a52f3cfe3": N(DOCN + " (the owed list, section 4d.5)", "B:U536?", "B:U112?", "B:U115?"),
    "fb71ee863c": T("drawn: the 5G removal, U536 and the dividers, the back-feed gates", *G5[:6], *RB, "B:R529.2=LIME_UVLO",
                    "B:R531.2=E22_UVLO", *E22[12:20], *E72[8:]),
})

# ------------------------------------------------------------------ round 2: the counts each judgement asserts (check-s122-1 B2)
SUP3 = ["B:#val~STM32H743=3"]
CARDS2 = ["B:#val~M.2 E-key=2"]
CX = {
    "d757d209e1": {"a": ["C:#ref~J_HSJ=2"]}, "60bc5be090": {"a": SUP3},
    "fc8851e8bd": {"counts_ok": "three lines per slot: HBn, SLOT_ENn and the select, asserted on U3"},
    "05ad0e2bee": {"a": SUP3 + ["B:#val~SN74LV1T08=3", "B:R529.2=LIME_UVLO", "B:R530.2=RB_UVLO", "B:R531.2=E22_UVLO"]},
    "406b1d5e9e": {"a": SUP3}, "977cb01ecc": {"a": ["A:#val~rail monitor +5V_S=3"]},
    "94bef6640e": {"a": SUP3 + ["A:#val~PCA9555=2"]}, "ccaf6c5062": {"a": SUP3}, "919c0ea875": {"a": SUP3},
    "ba3a95b6c7": {"a": ["C:#fp~LED_D3.0mm=17", "C:D1?", "C:D16?", "C:D22?"],
                   "counts_ok": "sixteen panel LEDs D1 to D16; D22 is the seventeenth"},
    "b023a2e379": {"a": ["C:#fp~LED_D3.0mm=17", "C:D1?", "C:D16?", "C:D22?"],
                   "counts_ok": "sixteen panel LEDs D1 to D16; D22 is the seventeenth"},
    "078d294b3f": {"counts_ok": "the three slots the firmware raises, not a part count"},
    "5feb94af38": {"counts_ok": "slots, not parts"}, "66308c1c0a": {"counts_ok": "slots, not parts"},
    "dc6e921095": {"counts_ok": "slots, not parts"}, "72057ed854": {"counts_ok": "modules, not parts"},
    "d5d59c71d0": {"a": SUP3}, "c42d5042b3": {"a": SUP3}, "bd895a6727": {"a": SUP3},
    "5c2c10a0f9": {"a": CARDS2}, "c3dc5405b5": {"a": CARDS2}, "09b0290f45": {"a": CARDS2}, "b719e651bd": {"a": CARDS2},
    "00e44f7f0e": {"a": CARDS2 + ["B:J_W1A?", "B:J_W3B?"], "counts_ok": "two headers: the fan and card pigtail headers named"},
    "360270daa1": {"counts_ok": "two of U26's four gates, their pins asserted"},
    "e231767e5f": {"counts_ok": "the arrestors are case parts, not a netlist's"},
    "cd9739a701": {"counts_ok": "the arrestors are case parts, not a netlist's"},
    "fb3f468c2a": {"counts_ok": "the 5G jacks are case and board A items under D-07"},
    "5151a2ab87": {"counts_ok": "the 5G jacks are case and board A items under D-07"},
    "c8af65ddfb": {"counts_ok": "case jacks"}, "93fc305d0b": {"counts_ok": "case jacks"},
    "6ea98bdfa1": {"a": ["B:#ref~J_SIM=2"], "counts_ok": "the antenna jacks are case items under D-07"},
    "4c1d0b24ec": {"a": ["B:#ref~J_SIM=2"]}, "93ed4f24e0": {"a": ["B:#ref~J_SIM=2"]},
    "884cd4a8b5": {"a": ["C:#fp~LED_D3.0mm=17", "C:D22~amber"], "counts_ok": "sixteen plus the seventeenth, D22"},
    "286e14a698": {"a": ["E:#ref~J_FAN=2", "B:#ref~J_FAN=3"]}, "27245f25a2": {"a": ["E:#ref~J_FAN=2", "B:#ref~J_FAN=3"]},
    "40489568ae": {"a": ["D:#ref~J_HS=2"]}, "0a2d2b6e41": {"a": ["E:#ref~J_FAN=2"]},
    "6374505c78": {"a": ["E:#val~Keystone=3", "E:#ref~J_FAN=2"]},
    "643c162767": {"counts_ok": "the lid tray's six nut slots, a case item"},
    "3fbdea5ae9": {"a": ["E:J_BLK.1=GND", "E:J_BLK.12=BLK_SPARE"], "counts_ok": "J_BLK's pins 1 to 12"},
    "a1079ff03a": {"counts_ok": "C7's J_MAINSW is a two-land footprint", "a": ["C:J_MAINSW?"]},
    "ca405f41c2": {"a": ["B:#val~SKY13351=2"]},
    "3a53e10db7": {"counts_ok": "the plug's contacts, not a netlist part"},
    "6a693c8a7f": {"a": ["A:#val~rail monitor +5V_S=3"]},
    "7211912728": {"a": ["E:#val~Keystone=3", "E:#ref~J_FAN=2"], "counts_ok": "the clamp bar's tie slots are a case item"},
    "c648bf2ea2": {"a": ["P:W_BP?", "P:W_BN?", "P:W_P?", "P:W_N?"], "counts_ok": "the four lands are W_BP, W_BN, W_P and W_N"},
}
for _d, _x in CX.items():
    if _d not in J: raise SystemExit("judgements: CX names %s, which has no judgement" % _d)
    J[_d] = dict(J[_d]); J[_d]["a"] = list(J[_d].get("a", [])) + list(_x.get("a", []))
    if "counts_ok" in _x: J[_d]["counts_ok"] = _x["counts_ok"]

# ------------------------------------------------------------------ round 2: the texts still unjudged
J.update({
    "31b8c509a8": T("set 12's back-feed gates; MISO through U553", "B:U537.4=RB_GO", "B:U538.2=RB_GO", "B:U539.2=RB_GO",
                    "B:U544.4=LORA_GO", "B:U546.2=LORA_GO", "B:U548.2=LORA_GO", "B:U550.2=LORA_GO", "B:U553.2=LORA_MISO",
                    "B:U553.4=SPI3_MISO", "B:U540.6=ZBA_RXD", "B:U541~SN74LVC2G07", "B:U542.6=ZBB_RXD",
                    "B:+3V3_ZB>R536,R537,U22"),
    "0869c14ca5": N(TEST), "2a664799ad": N(TEST + " (the functional check CFL-016 names)"),
    "cbef354fca": T("the EMCON lines reach every transmitter, the PA rail (U35, U36) and its bias (D's U15 on PA_KEY); the modes "
                    "are the design's", "D:U15.4=PA_KEY", "D:U14.4=PA_KEY", "A:U36.4=PA_EN", "D:U12.2=TX_INHIBIT_n",
                    "B:U113.1=EMCON_ON1"),
    "4ea2048570": T("CONOPS.md is c5430071's file", "FILE:v2/docs/CONOPS.md@6cb7b241cb84d729"),
    "85a57b63a6": T("the EMCON row's removals as generated", *LIME[:5], *RB[:12], *E22[:6], *E72[:6], *WIFI[:6], *CM5[:5],
                    *G5[:8], *AGATES[:10], *DKEY),
    # the status page
    "87eae15aa7": N(DOCN + " (the rule as the status page states it)"),
    "62daee5ea9": T("the five netlists read", "SHA:A=6c40250c47195ebb", "SHA:B=3ef9b8c49a01b728", "SHA:C=c9f7394594201045",
                    "SHA:D=a2d48972d171aad1", "SHA:E=2ed95a0e8069ebf8"),
    "5d7d836971": N(DOCN + " (a pointer to CONOPS passages)"), "8c7aa0e412": N(DOCN + " (a pointer)"),
    "e26b51344a": T("EMCON as set 13 carries it", *RB[:20], "B:U537?", "B:U553?", *WIFI[:6], "B:U216.4=S2A_EN", *AGATES),
    "0a184c8e4a": T("HOT-R1 on E and A, and REQ-077's reading in the registry", *HOTR1,
                    "REG:REQ-077.evidence_result=INCONCLUSIVE", "REG:REQ-077.waits_on~S-58"),
    "53707a7315": T("the lamps' feeds", "C:D3.2=TX_A", "C:R36.2=TX_A", "C:R36.1=LED_RAIL", "C:Q1.3=LED_RAIL",
                    "C:Q1.1=Q1_G", "C:R17.2=Q1_G", "C:R17.1=LED_RAIL_SW", "C:Q2.1=Q2_G", "C:R19.1=PANEL_PWM",
                    "C:U3@GPIO8=PANEL_PWM", "C:R47.1=LED_RAIL_SW", "C:R47.2=EMCLAMP_A", "C:D22.2=EMCLAMP_A",
                    "C:SW_EMCON.1=TX_INHIBIT_n", "C:U9.2=TX_INHIBIT_n", "A:J_MAINSW.1=MAIN_PB", "A:U1.2=MAIN_PB"),
    "9e537fb0a3": N(DOCN + " (a pointer)"), "f2d8c0af6d": N(DOCN + " (a pointer)"), "6eda79c80b": N(DOCN + " (a pointer)"),
    "6a69ca9a17": N(DOCN + " (a pointer)"),
    "5f1751dbcc": T("the device-rail converters", "A:U7~LM5176", "A:U7.12=+5V_DEV", "B:U25~AP63203", "B:U25.2=+5V_DEV",
                    "B:U25.5=DEV_SW", "B:L1.2=+3V3_DEV", "A:!~AP63203"),
    "0a02370f58": T("the +3V3_DEV loss; the threshold is TI's", *INV, "B:U113.5=+3V3_CM1", "B:U213.5=+3V3_CM2",
                    "B:U313.5=+3V3_CM3", "B:U543.1=RB_IEN", "B:U543.5=+3V3_DEV", "B:U543.6=+5V_DEV", "B:!U111",
                    "DOC:v2/docs/feasibility/EMCON.md~CLOSED at desk on board B's round 8 (section 4b)"),
    "388cb94e64": T("the lines stream s122 read at e57a7365", "G@e57a7365:gen_sch_a.py:1104~R42",
                    "G@e57a7365:gen_sch_a.py:338-339~R2|R184|R4", "G@e57a7365:gen_sch_a.py:1598~R103|R104",
                    "G@e57a7365:gen_sch_a.py:1611~R111", "G@e57a7365:gen_sch_a.py:1340~U21",
                    "G@e57a7365:gen_sch_a.py:1372~U22", "G@e57a7365:gen_sch_a.py:972~R26|R27",
                    "G@e57a7365:gen_sch_a.py:1306~J_USBC_OUT", "G@e57a7365:gen_sch_a.py:1668~J_USBW",
                    "G@e57a7365:gen_sch_e.py:796~J_TAMP", cite_ok="each line asserted at e57a7365 below"),
})
J["85a57b63a6"]["a"] = J["85a57b63a6"]["a"] + CARDS2

# ------------------------------------------------------------------ round 2: base texts (e57a7365) the round 2 finder reaches
J["7f1fe39d10"]["a"] = J["7f1fe39d10"]["a"] + CARDS2
J.update({
    "b9c70c510b": N(DOCN + " (the row's sources)"),
    "b5bb1f3502": N(DOCN + " (the module's stored energy, section 4.4)"),
    "7c880bf633": S("the switch chip generated is the seven-port KSZ9897R (U1 on B16), not a five-port part",
                    "B:U1~seven-port Gigabit", counts_ok="the slots are the receptacle pairs"),
    "e85072845e": S("the A22 row names the TPS55288, which had left the design before the 7 September generation "
                    "(gen_sch_a.py line 267 at c5de605d; check-s122-1 m7)", "G@c5de605d:gen_sch_a.py:267~TPS55288",
                    "A:#val~rail monitor +5V_S=3"),
    "8b6267524a": S("the B16 row's closing condition for the supervisors is met: U41, U51 and U61 read STM32H743 and CON-017 "
                    "reads PASS (check-s122-1 m7)", "B:#val~STM32H743=3", "REG:CON-017.evidence_result=PASS",
                    "B:#val~PI7C9X2G404=3"),
    "e8fae1c146": S("board A carries seventeen Mill-Max 0858 class pins, the eight of EQ-16 added (check-s122-1 B2)",
                    "A:#fp~Mill-Max_0858=17"),
    "c54e91925e": S("board A carries seventeen Mill-Max 0858 class pins (check-s122-1 B2)", "A:#fp~Mill-Max_0858=17"),
    "3fa744781d": S("board B carries two WiFi link card sockets, J_M2C1 and J_M2C3 (check-s122-1 B2)", "B:#val~M.2 E-key=2"),
    "dcfe5ddc9a": S("board C carries seventeen 3 mm LEDs, D22 the seventeenth (check-s122-1 B2)", "C:#fp~LED_D3.0mm=17"),
})

# ================================================================== ROUND 3 (check-s122-2: B1, m7, m8, the absent sweep)
# the supervisors' I2C status path (DC-07): targets on the kit bus since 458b2873, before the text was written (95e078a1)
# and at the baseline (c5430071); unconnected at 458b2873's parent 1f614233; the TCA9517A segment of SC-HF-02 not drawn
SUPI2C = ["B:U41@PB7=SDA", "B:U41@PB6=SCL", "B:U51@PB7=SDA", "B:U51@PB6=SCL", "B:U61@PB7=SDA", "B:U61@PB6=SCL",
          "B:U41.93=SDA", "B:U41.92=SCL", "B:SDA>J_PANEL,U41,U51,U61", "B:SCL>J_PANEL,U41,U51,U61", "B:J_PANEL.4=SDA",
          "B@458b2873:U41@PB7=SDA", "B@1f614233:U41@PB7=unconnected-(U41-PB7-Pad93)", "B@95e078a1:U51@PB6=SCL",
          "B@c5430071:U61@PB7=SDA", "B@45bde541:U41@PB6=SCL", "B@a9f212c7:U51@PB7=SDA", "B:!~TCA9517",
          "DOC:v2/docs/ARCH-PCB-B-IOHA.md~CORRECTED at `458b2873`",
          "DOC:v2/docs/ARCH-PCB-B-IOHA.md~move behind a TCA9517A that the panel controller enables from U7 only for its own transactions to them (owed on the generator)"]
# the fabric's back-power gating, FAB-02 (b) and (c), and the break-before-make of FAB-03 (DC-08): drawn in board B's round 8,
# present at 95e078a1 and at c5430071, absent at 45bde541; S-42 open, CON-003 and CON-022 INCONCLUSIVE waiting on it
FABRIC = ["B:R191.1=+3V3_CM1", "B:R191.2=PG1", "B:R191~1k", "B:R192.1=PG1", "B:R192.2=GND", "B:R192~100k",
          "B:U530~74LVC1G17", "B:U530.2=PG1", "B:U530.4=PG1_S", "B:U533~SN74LVC1G04", "B:U533.2=PG1_S", "B:U533.4=PG1_n",
          "B:U513~74LVC1G157", "B:U513.3=PG1_n", "B:U513.1=PG2_n", "B:U513.6=BSEL1_D2", "B:U513.4=PGSEL1_n",
          "B:U516~BBM ? 1", "B:U516.3=PGSEL1_n", "B:U516.6=BBM1", "B:U516.4=BOE1_n", "B:BOE1_n>U109,U110",
          "B:U109~TMUXHS4212", "B:U110~TS3USB221A", "B:BBM1>=U516,U85", "B:BBM1_MOV>U527,U80,U85", "B:BBM1_ARM>U521,U524,U84",
          "B:U507~FAB-03", "B:U510~FAB-03", "B:U521~FAB-03", "B:BSEL1_S>U109,U110,U507",
          "B:U519~74LVC1G157", "B:U519.3=PG1_S", "B:U519.1=PG2_S", "B:U519.6=HDMI_SEL1", "B:U519.4=HDMI_EN1", "B:U3.2=HDMI_EN1",
          "B:U520~74LVC1G157", "B:U520.1=PG3_S", "B:U520.6=HDMI_SEL2", "B:U520.4=HDMI_EN2", "B:U4.2=HDMI_EN2",
          "B@95e078a1:U519~74LVC1G157", "B@95e078a1:U516~BBM ? 1", "B@c5430071:U520~74LVC1G157", "B@c5430071:U513~74LVC1G157",
          "B@45bde541:!U519", "B@45bde541:!U516",
          "G@b874b744:check_pcb_b.py:353-353~U519|U520", "G@b874b744:check_pcb_b.py:412-412~FAB-02 (b)",
          "REG:S-42.status=OPEN", "REG:S-42.title~the back-power gating of FAB-02 (b) and (c)",
          "REG:S-42.title~a true break-before-make sequence", "REG:CON-022.evidence_result=INCONCLUSIVE",
          "REG:CON-022.waits_on~S-42", "REG:CON-003.evidence_result=INCONCLUSIVE", "REG:CON-003.waits_on~S-42"]
# board A's CC array of D-17 (DC-09): drawn since 458b2873
CCARR = ["A:U31~TPD2E2U06", "A:U31.1=PD_CC1", "A:U31.2=PD_CC2", "A:U31.3=GND", "A:J_USBC_OUT.2=PD_CC1",
         "A:J_USBC_OUT.3=PD_CC2", "A@458b2873:U31~TPD2E2U06", "A@c5430071:U31~TPD2E2U06"]
# BANK-R1 not drawn: the generated hub allocation, unchanged since 45bde541; REQ-052 FAIL
BANKR1 = ["B:U102@USB_DP_DN4=RB_DP", "B:RB_DP>=U102,U18", "B:U18~CP2102N", "B:U202@USB_DP_DN4=QMX_DP", "B:QMX_DP>J_QMX,U202",
          "B:U102@USB_DP_DN2=USB_PNL_P", "B:USB_PNL_P>J_PANEL,U102", "B:U302@USB_DP_DN3=USB_WALL_P",
          "B@45bde541:U102@USB_DP_DN4=RB_DP", "B@45bde541:U202@USB_DP_DN4=QMX_DP", "B@45bde541:U102@USB_DP_DN2=USB_PNL_P",
          "B@45bde541:U302@USB_DP_DN3=USB_WALL_P", "REG:REQ-052.evidence_result=FAIL"]
# SLOT_EN as generated: the panel controller's GPIO, the ribbons, test points, the converters' enables and 100 k pull-downs
SLOTEN = ["A:SLOT_EN1>=J_AB1,R30,U4", "A:SLOT_EN2>=J_AB1,R34,U5", "A:SLOT_EN3>=J_AB1,R38,U6", "A:R30~100k", "A:R30.2=GND",
          "A:R34.2=GND", "A:R38.2=GND", "B:SLOT_EN1>=J_AB1,J_PANEL", "B:SLOT_EN2>=J_AB1,J_PANEL", "B:SLOT_EN3>=J_AB1,J_PANEL",
          "C:SLOT_EN1>=J_PANEL,TP31,U3", "C:SLOT_EN2>=J_PANEL,TP32,U3", "C:SLOT_EN3>=J_PANEL,TP33,U3"]
PRE3 = "check-s122-2 B1: "
J.update({
    "8e2b2ea5c9": B(["DC-07", "DC-08"], PRE3 + "all three preconditions are drawn, and were at the text's writing (95e078a1) and at "
                    "the baseline (c5430071): the supervisors are kit bus targets on PB7 and PB6 since 458b2873 (DC-07; the "
                    "TCA9517A segment of SC-HF-02 is what is owed), and board B's round 8 drew the break-before-make of FAB-03 "
                    "and the back-power gating of FAB-02 (b) and (c), the display switches' enables U519 and U520 among it "
                    "(DC-08); S-42 stays open over them (the gate's assertion and its mutation are its terms)",
                    *(SUPI2C + FABRIC)),
    "186a997856": B(["DC-07", "DC-08"], PRE3 + "the three items it calls owed as generated are drawn (DC-07, DC-08)",
                    *(SUPI2C + FABRIC)),
    "a4c8583ce6": B("DC-09", "D-17's CC array is drawn on board A since 458b2873 (U31, TPD2E2U06, on PD_CC1 and PD_CC2 at "
                    "J_USBC_OUT); the row was written at 68bc9e8f, before 458b2873 drew it", *CCARR),
    "41d1053ffe": B("DC-02", "HOT-R1 called owed before layout entry; drawn since stream w4ae; REQ-077 reads INCONCLUSIVE, not FAIL",
                    *HOTR1),
    "000d312aa9": T("BANK-R1 is not in the generator: bank 1 carries the RockBLOCK's bridge U18 on port 4 and the panel "
                    "controller on port 2, bank 2 the QMX on port 4, bank 3 the wall port on port 3, as at 45bde541, and "
                    "REQ-052 reads FAIL; the owner's example and the hand-off are the record's", *BANKR1),
    "0f2685fa36": T("nothing holds SLOT_EN across a controller restart as generated: each line is the panel controller's GPIO "
                    "(U3 pins 16 to 18 on board C), the ribbons, a test point, and on board A the slot converter's enable with "
                    "its 100 k pull-down; the watchdog restart and the boot order are firmware", *SLOTEN,
                    "C:U3.16=SLOT_EN1", "C:U3.17=SLOT_EN2", "C:U3.18=SLOT_EN3"),
    "c530f82b50": N(DOCN + " (a need of section 2)",
                    absent_ok={"cellular infrastructure are absent or down": "the setting the kit serves, not the circuit"}),
    "aa962fffd3": N(FW + " (the build checks; the PA's flange figure is POWER-THERMAL.md PWR-F15's)"),
    "2ec2a400f8": T("board P's arming jumper JP1 and chemical fuse F2 with the second level U2; the commissioning is D-15's "
                    "procedure", "P:JP1.1=FUSE_G", "P:JP1.2=FUSE_GQ", "P:F2~SCF9550", "P:F2.3=SCP_HTR", "P:U2~BQ7720700"),
    "61013cde57": N(FW, "B:#val~STM32H743=3"),
    "f83ed5d19a": N(TEST),
    "488d983a0f": N(H + " (the case choices C1 to C6, CASE-MARGINS.md section 4)",
                    counts_ok={"two WIFI P2P jacks": "the case's WIFI P2P antenna jacks, case items"}),
    "1e990ac1c7": N(H), "edd3aa4d2f": N(H), "c12a46ae87": N(H), "60fc961b25": N(H),
    "d242bb413f": N(FW + " (control C1's thresholds; which module remains is the control's, BANK-R1 not drawn)", *BANKR1),
    "9ba46bddfe": N(FW + " (the cold warm-up)", *CARDS2,
                    counts_ok={"two AW7915-AED WiFi link cards": "asserted: B:#val~M.2 E-key=2"}),
})
# the absent sweep's bound phrases on existing NOT DERIVABLE judgements (each a phrase quoted from its sentence)
R3ABS = {
    "ad42c9eb94": {"no case measurement is owed": "a case measurement the owner's reversal of D-08 removed, not the circuit"},
    "f17b893792": {"bench confirmation owed": "a bench confirmation of TI's charger behaviour, not the circuit"},
    "02d81ab6f6": {"unless a row says a fix is owed": "the section's reading date; each row that says a fix is owed is "
                                                     "inventoried and judged on its own"},
}
# m8: each count bound to its own reason or to one of the judgement's own count assertions of the same number
R3CNT = {
    "05ad0e2bee": ({"three card": "the three card supplies, whose enables U116, U216 and U316 are asserted above",
                    "three reaching their switches": "not a count of parts: the first three of U501 to U505 reaching their "
                                                     "switches U23, U24 and U21, asserted above",
                    "three supervisors": "asserted: B:#val~STM32H743=3"}, ["B:#val~STM32H743=3"]),
    "94bef6640e": ({"three supervisors": "asserted: B:#val~STM32H743=3", "two expanders": "asserted: A:#val~PCA9555=2"}, []),
    "72057ed854": ({"three modules in any slot": "the number of modules fitted in any slot, not a count of parts"}, []),
    "6ea98bdfa1": ({"three antenna jacks": "the 5G antenna jacks are case items under D-07, not a netlist's",
                    "two nano-SIM holders": "asserted: B:#ref~J_SIM=2"}, []),
    "884cd4a8b5": ({"sixteen LEDs": "the LEDs D1 to D16 under the light guides; the sentence names D22 as the seventeenth, and "
                                    "the seventeen LED_D3.0mm footprints are asserted"}, []),
    "286e14a698": ({"five IP68-rated internal fans": "the five fans: J_FAN1 to J_FAN3 on board B and J_FAN1, J_FAN2 on board E, "
                                                     "both counts asserted",
                    "two mixer fans": "asserted: E:#ref~J_FAN=2"}, []),
    "b1e7494b6d": ({"three CM5 slots": "the three slots are the receptacles U30A, U31A and U32A, asserted",
                    "three STM32H743 supervisors": "asserted: B:#val~STM32H743=3"}, ["B:U30A?", "B:U31A?", "B:U32A?"]),
    "ac1bd47d91": ({"Two NVMe drives": "the cost estimate's drives of 6 September 2026, bought items",
                    "two PCIe switches": "the cost estimate's PCIe switches of 6 September 2026; board B carries three, one per "
                                         "slot"}, ["B:#val~PI7C9X2G404=3"]),
    "36abc030f1": ({"Two headset jacks": "the cost estimate's headset jacks of 6 September 2026"}, []),
    "287efa15f6": ({"five IP68 fans": "the cost estimate's fans of 6 September 2026"}, []),
    "27245f25a2": ({"five fans": "the five fans: J_FAN1 to J_FAN3 on board B and J_FAN1, J_FAN2 on board E, both counts asserted",
                    "two mixer fans": "asserted: E:#ref~J_FAN=2"}, []),
    "5e98fc1920": ({"three slots": "a row label naming the three slots, not a count of parts"}, []),
    "ab5d01673b": ({"five fans": "the five fans' temperature documents, which the tree does not hold"}, []),
    "8a93588273": ({"five fans": "appendix 32.53's five fans: J_FAN1 to J_FAN3 on board B and J_FAN1, J_FAN2 on board E, both "
                                 "counts asserted"}, ["B:#ref~J_FAN=3", "E:#ref~J_FAN=2"]),
    "6374505c78": ({"three fuse": "asserted: E:#val~Keystone=3", "two mixer fans": "asserted: E:#ref~J_FAN=2"}, []),
    "cc0ec17c8e": ({"eleven Radiall receptacles": "asserted: A:#ref~J_BM=11",
                    "seventeen Mill-Max 0858 class power pins": "asserted: A:#fp~Mill-Max_0858=17"}, []),
    "00e44f7f0e": ({"two WiFi link cards": "asserted: B:#val~M.2 E-key=2",
                    "two headers": "the two J_AB1 headers, A22's and B16's, each asserted present"}, ["A:J_AB1?", "B:J_AB1?"]),
    "8b1e16653a": ({"two headset jacks": "asserted: C:#ref~J_HSJ=2"}, ["C:#ref~J_HSJ=2"]),
    "3fbdea5ae9": ({"twelve lands": "J_BLK's twelve lands, its pins 1 to 12 (pins 1 and 12 asserted)"}, []),
    "3a53e10db7": ({"four M39029/56-352 size 16 socket": "the Glenair plug's socket contacts, not a netlist part"}, []),
    "c8263105e0": ({"Twelve Preci-Dip 813 contacts": "J_DOCK's twelve contacts, pins 1, 4, 7 and 8 to 12 asserted",
                    "four 9 A spring pins": "asserted: A:#ref~J_VR=4"}, []),
    "e050e55b92": ({"nine Mill-Max 0858 class pins": "the pack's nine pins: J_CP1 to J_CP4, J_CN1 to J_CN4 and J_PRE1, "
                                                     "asserted as four, four and one"},
                   ["A:#ref~J_CP=4", "A:#ref~J_CN=4", "A:J_PRE1?"]),
    "f6186bbdf0": ({"eleven Radiall R222M00720 blind-mate receptacles": "asserted: A:#ref~J_BM=11",
                    "seventeen Mill-Max 0858 class power pins": "asserted: A:#fp~Mill-Max_0858=17"}, []),
    "a039b91bf4": ({"three NVMe drives": "asserted: B:#val~M.2 M-key=3", "three coolers": "asserted: B:#ref~J_FAN=3",
                    "two WiFi link cards": "asserted: B:#val~M.2 E-key=2"}, []),
    "73ff7b42ab": ({"seventeen 3 mm LEDs": "asserted: C:#fp~LED_D3.0mm=17", "three APEM toggles": "asserted: C:#val~APEM=3",
                    "three C&K switches": "asserted: C:#val~C&K=3", "two U-174/U jacks": "asserted: C:#ref~J_HSJ=2"}, []),
    "7211912728": ({"three Keystone holders": "asserted: E:#val~Keystone=3", "two mixer fans": "asserted: E:#ref~J_FAN=2",
                    "two tie slots": "the clamp bar's tie slots, a case item"}, []),
}
for _d, _x in R3ABS.items():
    if _d not in J: raise SystemExit("judgements: R3ABS names %s, which has no judgement" % _d)
    J[_d] = dict(J[_d]); J[_d]["absent_ok"] = _x
for _d, (_c, _a) in R3CNT.items():
    if _d not in J: raise SystemExit("judgements: R3CNT names %s, which has no judgement" % _d)
    J[_d] = dict(J[_d]); J[_d]["a"] = list(J[_d].get("a", [])) + [x for x in _a if x not in J[_d].get("a", [])]
    J[_d]["counts_ok"] = _c
# the dated citation of ASSEMBLY line 90's correction (gen_sch_e.py:193 at 45bde541)
J["ef9f31ab35"] = dict(J["ef9f31ab35"], a=list(J["ef9f31ab35"].get("a", [])) + ["G@45bde541:gen_sch_e.py:193~J_BATT|BTA-70762-2"],
                       cite_ok="the citation asserted at 45bde541 below")

# ------------------------------------------------------------------ round 3: the texts round 3 wrote (apply_docs_s122_r3.py)
WRIT = ["DOC@95e078a1:v2/docs/CONOPS.md~the supervisors' I2C status path, absent as generated",
        "DOC@95e078a1^:v2/docs/CONOPS.md!~the supervisors' I2C status path, absent as generated",
        "DOC@95e078a1:v2/docs/CONOPS.md~and the supervisors' I2C status path (`ARCH-PCB-B-IOHA.md` section 6); they are preconditions",
        "DOC@95e078a1^:v2/docs/CONOPS.md!~and the supervisors' I2C status path (`ARCH-PCB-B-IOHA.md` section 6); they are preconditions"]
PAR1F = ["B@1f614233:U%s@PB%s=unconnected-(U%s-PB%s-Pad%s)" % (u, pb, u, pb, pad)
         for u in ("41", "51", "61") for pb, pad in (("6", "92"), ("7", "93"))]
ROW3N = ["C@45bde541:R36.1=LED_RAIL", "C@45bde541:R36.2=TX_A", "C@45bde541:D3.2=TX_A", "C@45bde541:Q1.3=LED_RAIL",
         "C@a9f212c7:R36.1=LED_RAIL", "C@a9f212c7:Q1.3=LED_RAIL", "C:R36.1=LED_RAIL", "C:D3.2=TX_A"]
ROW4N = ["B@45bde541:U25~AP63203", "B@45bde541:U25.1=+3V3_DEV", "B@45bde541:U25.2=+5V_DEV", "B@a9f212c7:U25.1=+3V3_DEV",
         "B@a9f212c7:U25.2=+5V_DEV", "A@45bde541:U7~LM5176", "A@a9f212c7:U7~LM5176"]
SEC01 = ["DOC:v2/docs/feasibility/EMCON.md~### 0a.1|`U540`|`R536`|`R537`|`U536`|`RB_IEN`|`U543`"]
J.update({
    "5bfe6a8bde": dict(J["31b8c509a8"], why=J["31b8c509a8"]["why"] + "; the citation is EMCON.md section 0a.1 since round 3 "
                       "(check-s122-2 m1), which names the E72 gates and pull-ups", a=J["31b8c509a8"]["a"] + SEC01),
    "90d51e8ca0": dict(J["c3dc5405b5"], why=J["c3dc5405b5"]["why"] + "; the per-radio citation is EMCON.md section 0a.1 since "
                       "round 3 (check-s122-2 m2)", a=J["c3dc5405b5"]["a"] + SEC01),
    "479d562a75": N(H + " (correction 33's heading)"),
    "8c1edc6932": T("CONOPS.md is c5430071's file; EMCON.md 0a.1 carries the circuit; the status page's DC-01 names it",
                    "FILE:v2/docs/CONOPS.md@6cb7b241cb84d729", *SEC01,
                    "DOC:v2/docs/handover/DEFINITION-STATUS.md~| DC-01 | section 4's EMCON row; section 4b's preamble and table |"),
    "73f2e6ddc9": dict(J["53707a7315"], why=J["53707a7315"]["why"] + "; the baseline's value at 45bde541 and a9f212c7 (m3)",
                       a=J["53707a7315"]["a"] + ROW3N),
    "f908d15512": dict(J["5f1751dbcc"], why=J["5f1751dbcc"]["why"] + "; the baseline's value at 45bde541 and a9f212c7 (m3)",
                       a=J["5f1751dbcc"]["a"] + ROW4N),
    "b69a3a82b2": T("the passages DC-07 keeps: CONOPS section 4's Reduced row and section 4c's SLOT_EN1 passage",
                    "DOC:v2/docs/CONOPS.md~and the supervisors' I2C status path, absent as generated",
                    "DOC:v2/docs/CONOPS.md~and the supervisors' I2C status path (`ARCH-PCB-B-IOHA.md` section 6)"),
    "ad17cbd96a": T("the status path on set 13, at 458b2873's parent, at the commits named, and where the passages were written",
                    *(SUPI2C + PAR1F + WRIT), "DOC:v2/docs/HW-FW-CONTRACT.md~### 6.5 The session's choice: three segments (SC-HF-02"),
    "0c80bfc694": T("the places named", "DOC:v2/docs/ARCH-PCB-B-IOHA.md~## 6. The control plane",
                    "DOC:v2/docs/HW-FW-CONTRACT.md~| FW-B08 | supervisors' I2C1: SCL PB6 pin 92, SDA PB7 pin 93 on the kit bus"),
    "3c62f9bf01": T("the passages DC-08 keeps", "DOC:v2/docs/CONOPS.md~the break-before-make order, which the generated circuit "
                    "does not have (FAB-03, CON-003); a bank detached from a host that has lost its power, which nothing does "
                    "as generated (FAB-02, CON-022)", "DOC:v2/docs/CONOPS.md~the break-before-make order (FAB-03, CON-003), a bank "
                    "detached from a host that has lost its power (FAB-02, CON-022)"),
    "0a5b716f9c": T("the fabric on set 13, at 95e078a1 and c5430071, and absent at 45bde541; S-42 and the two records",
                    *(FABRIC + WRIT[:1]), "B:U514~74LVC1G157", "B:U515~74LVC1G157", "B:U517~BBM ? 1", "B:U518~BBM ? 1",
                    "B:U531~74LVC1G17", "B:U532~74LVC1G17", "B:U534~SN74LVC1G04", "B:U535~SN74LVC1G04", "B:U531.4=PG2_S",
                    "B:U532.4=PG3_S", "B:U517.4=BOE2_n", "B:U518.4=BOE3_n", "B:U517.6=BBM2", "B:U518.6=BBM3"),
    "d23056fff8": T("the places named", "DOC:v2/docs/ARCH-PCB-B-IOHA.md~## 5. How the hardware prevents split brain|"
                    "**Drawn in board B's round 8 (27 September 2026):** each slot's power-good",
                    "DOC:v2/docs/feasibility/FAILOVER-FABRIC.md~## 9. Findings of this review|## 9a. Round 8 (27 September 2026",
                    "REG:S-42.status=OPEN", "REG:CON-003.waits_on~S-42", "REG:CON-022.waits_on~S-42"),
    "840195c22c": T("the passage DC-09 keeps", "DOC:v2/docs/CONOPS.md~| D-17 | Board A's USB-C CC pins (decision 31) | RULED "
                    "26 Sep | an external low-capacitance ESD array at the CC pins by the connector, riding on the board A update "
                    "already owed |"),
    "8238c2f0de": T("the array on set 13, at 458b2873, 45bde541 and c5430071, and where the row was written (68bc9e8f, the "
                    "file's first commit, without it)", *CCARR, "A@45bde541:U31~TPD2E2U06", "A@68bc9e8f:!U31",
                    "DOC@68bc9e8f:v2/docs/CONOPS.md~riding on the board A update already owed"),
})
J["ad17cbd96a"]["a"] = J["ad17cbd96a"]["a"] + ["B:#val~STM32H743=3"]
J["ad17cbd96a"]["counts_ok"] = {"three supervisors": "asserted: B:#val~STM32H743=3"}
# the absent sweep on the base's texts (e57a7365's CONOPS.md, which set 12 had edited; verdicts-base.out)
J["7778cb996e"] = T("the owed list is open items and bench tests, not parts the netlists lack: S-01, S-92, S-93 and S-44 open "
                    "in the registry; U536 and the lamp D22 drawn", "B:U536?", "B:U112?", "B:U115?", "B:U536~SN74LVC1G08",
                    "C:D22~EMCON", "REG:S-01.status=OPEN", "REG:S-92.status=OPEN", "REG:S-93.status=OPEN",
                    "REG:S-44.status=OPEN")
J["b73681b892"] = dict(J["b73681b892"], absent_ok={"with each state, fault and proof owed": "the record's proofs, bench and "
                                                                                          "document items, not the circuit"})
# what the registry's CON-003 and CON-022 evidence says against set 13's board B (an observation for the integrator,
# README "What stays open"; S-122 does not change those records)
J["0a5b716f9c"]["a"] = J["0a5b716f9c"]["a"] + [
    "B:R480~10k", "B:R500~10k", "REG:CON-003.evidence~R480 and R500 still 100k",
    "REG:CON-022.evidence~its remedy (b) and (c) is not drawn",
    "REG:CON-003.evidence_bound_to~pcb-b-compute.net@3ef9b8c49a01b728",
    "REG:CON-022.evidence_bound_to~pcb-b-compute.net@3ef9b8c49a01b728"]

# ================================================================== ROUND 4 (set 14: part numbers; check-s122-3's minors)
# Every maker's part number a sentence names is judged by verdicts.check_parts against the six netlists' part values;
# `parts_ok` names each one the netlists do not carry (a kind and a colon, or an own assertion that names it).
DOCK = "document: "
def PK(**kw): return {k.replace("__", "-").replace("_S_", "/"): v for k, v in kw.items()}
CELL = {"INR18650-35E": "bought: Samsung's cell of the built pack, not a board part"}
BANKS = ["B:U109~bank 1: B = slot 1 USB3-0 (home), C = slot 2", "B:U209~bank 2: B = slot 2 USB3-0 (home), C = slot 3",
         "B:U309~bank 3: B = slot 3 USB3-0 (home), C = slot 1", "B:U110~bank 1: port 1 = slot 1 (home), port 2 = slot 2",
         "B:U210~bank 2: port 1 = slot 2 (home), port 2 = slot 3", "B:U310~bank 3: port 1 = slot 3 (home), port 2 = slot 1",
         "B:U102@USB_DP_DN4=RB_DP", "B:U18~CP2102N", "B:U102@USB_DP_DN2=USB_PNL_P", "B:U202@USB_DP_DN1=GNSS_DP",
         "B:U302@USB_DP_DN1=USB_D8_P", "B:U302@USB_DP_DN2=USB_E6_P", "B:U302@USB_DP_DN3=USB_WALL_P",
         "B:U302@USB_DP_DN4=USB_5G_P", "B:USB_5G_P>=J_M2C2,U302", "B:LORA_MOSI>=U12,U548", "B:SPI3_MOSI>=J_SPI3,R549,U32A,U548",
         "B:CARD2_TX_P>J_M2C2", "B:U12~E22-900M30S"]
R4 = "round 4: "
J.update({
    # PANEL.md section 7, the bus table's part cells
    "cbb687f780": T("C7's VEML7700", "C:U_LIGHT~VEML7700"),
    "3d47dcd92b": T("C7's two PCA9555", "C:U1~PCA9555", "C:U2~PCA9555"),
    "8a07cc5c6c": T("D8's PCA9555", "D:U16~PCA9555"),
    "de5bf6a8af": T("B16's TMP117 under the coolers", "B:U10~TMP117", "B:U10~under the coolers"),
    "2773e818ae": T("A22's BQ25731 U3 on the kit bus (pins 12 and 13); no pin of it is on a thermistor or gauge net; the pin "
                    "table is TI's (SLUSE66A)", "A:U3~BQ25731", "A:U3.12=SDA", "A:U3.13=SCL"),
    "4b0726e6eb": N(FW + " (a rule of operation; the clamp is the PCA9555's own behaviour)"),
    # CONOPS.md
    "8b09cd80ae": T("the LoRa module's SPI reaches slot 3's module only (U32A through U548) and the 5G card's PCIe lane is "
                    "slot 2's card socket; the named exceptions are IOHA's record", *BANKS),
    "cbdee784c7": N(DOCN + " (the night's routes, D-01, D-06)",
                    absent_ok={"which has no location found": "a case location for a deferred pack, not the circuit"}),
    "f2b4ff58e0": T("the heat stage as generated: slot 2 hosts bank 1 as its failover (the RockBLOCK's bridge U18 and the "
                    "panel's USB) and bank 2 at home (GNSS), the 5G card is slot 2's; the LoRa module is slot 3's SPI and "
                    "APRS and the pack's readings are bank 3's (slot 3, failover slot 1); the thresholds and D-01 are the "
                    "document's", *BANKS,
                    absent_ok={"it has no ambient sensor in prototype 1's core": "the scope of prototype 1's core (D-01 "
                               "defers the outside pod), not a part the netlists lack"}),
    "96aecf2119": N(DOCN + " (one module running, the consequence of D-02b)",
                    absent_ok={"the kit has no compute redundancy left": "one module running, an operating consequence, "
                               "not a part the netlists lack"}),
    "4971a13c0c": N(DOCN + " (the cell maker's restriction)", parts_ok=dict(CELL)),
    "36447f2d08": T("the heat stage as generated: with slots 1 and 3 off, bank 3 (home slot 3, failover slot 1) has no host, "
                    "and on it are D8 (APRS), E6's sensor controller, the wall port and the 5G module's USB (port 4); the "
                    "LoRa module is slot 3's SPI; the module's update path is Quectel's", *BANKS),
    "074bdf07a1": T("slot 2 has neither the LoRa mesh (slot 3's SPI) nor APRS (D8 on bank 3, slots 3 and 1); BANK-R1 is not "
                    "in the generator (the hub ports as at 45bde541) and REQ-052 reads FAIL", *(BANKS + BANKR1)),
    "8f75710147": N(FW + " (the gauge's firmware and the charger's writes; the charger's pins are TI's)",
                    absent_ok={"it has no thermistor input": "the charger's own pin table (TI SLUSE66A), which no "
                               "netlist states"}),
    "f3cd846998": N(DOCN + " (the row's sources)", parts_ok=PK(SLUSE66A=DOCK + "TI's BQ25731 data sheet number")),
    "20e78504cb": dict(J["20e78504cb"], absent_ok={"a drive unlocks at boot only through the secure element, the panel "
                                                   "controller and the kit I2C bus": "the accepted residual risk of D-03, "
                                                   "a ruling's words"}),
    "84d9aff12f": N(DOCN + " (the storage state, the cell maker's figures)", parts_ok=dict(CELL)),
    "c2eb51a8b1": N(DOCN, absent_ok={"Storage humidity has no number in any held source": "a figure no held document "
                                     "states, not the circuit"}),
    "a4b075a1f3": N(DOCN + " (the runtime method, the cell's specification)", parts_ok=dict(CELL)),
    "9ae1bb37fb": T("slot 3 alone hosts no bank 1 (slots 1 and 2), so neither Iridium's bridge nor the panel's USB; BANK-R1 "
                    "is the record's", *BANKS),
    "3abf30a0b4": dict(J["3abf30a0b4"], parts_ok=dict(CELL)),
    "d9695f53c9": N(DOCN + " (the cell's specification)", parts_ok=dict(CELL)),
    "e2d0db85e8": T("B16's E22-900M30S", "B:U12~E22-900M30S"),
    "89644c8c06": T("B16's two E72 (CC2652P)", "B:U13~E72-2G4M20S1E CC2652P", "B:U14~E72-2G4M20S1E CC2652P"),
    "c1b59fa740": T("the RM520N-GL on board B's key-B socket", "B:J_M2C2~RM520N-GL"),
    "c581f604c7": N(DOCN + " (the maker's datasheet and the Linux driver)",
                    absent_ok={"the mainline Linux driver has no code for it": "a driver's source, not the circuit"}),
    "5990559fb8": T("D8's SA868 and the PA's leads", "D:*~SA868", "D:*~RA30H1317M1"),
    "24f6f52515": T("B16's LG290P; the DCF77 and lightning headers on E6", "B:U11~LG290P", "E:J_DCF?", "E:J_LTG?"),
    "c4d07a0485": T("the transmitters named are on the netlists (D's SA868 and the PA's leads, the RockBLOCK site, the two "
                    "card sockets, the E22, both E72, the LimeSDR bay, the QMX lead)", "D:*~SA868", "B:J_RB9704?",
                    "B:J_M2C1~AW7915", "B:J_M2C3?", "B:U12~E22-900M30S", "B:U13?", "B:U14?", "B:J_LIME?", "B:J_QMX?"),
    "a9e17ab4ef": T("bank 3 hosts E6's sensor controller, whose reed is the lid; the mode rule is the firmware's", *BANKS),
    "e2340ccf73": T("as generated: slot 3 alone hosts neither bank 1 (Iridium's bridge, the panel) nor slot 2's; slot 1 "
                    "alone hosts bank 1 at home and bank 3 as failover, not bank 2 (GNSS)", *BANKS),
    "975e9e1f83": N(DOCN + " (INFERRED from the model; the cell maker's words)", parts_ok=dict(CELL)),
    "1a31a2702b": T("the path through a compute module needs bank 3's host (E6's sensor controller on bank 3), which the "
                    "heat stage as generated (slot 2 alone) does not have", *BANKS),
    "8d098165cb": dict(J["8d098165cb"], parts_ok=PK(**{"103AT-2": "owed: a proposed comparator's thermistor; the part is "
                                                     "board D's and board P's NTC"})),
    "0f4d72d9d5": N(DOCN + " (the core's scope under D-01)",
                    absent_ok={"The kit has no ambient sensor in prototype 1's core": "the scope of prototype 1's core "
                               "(D-01 defers the outside pod), not a part the netlists lack"}),
    "10987af00a": N(DOCN + " (the makers' ranges, PWR-F09)"),
    "c20f2e4cda": T("as generated, with slots 1 and 2 lost, bank 1 (home slot 1, failover slot 2) has no host, and on it are "
                    "the RockBLOCK's bridge and the panel's USB; the drive unlock and BANK-R1 are the records'", *BANKS),
    "48a9631e39": T("in the heat stage as generated (slot 2 alone) bank 3, which carries E6's sensor controller, has no "
                    "host; the response and its thresholds are firmware (TBD)", *BANKS),
    "66ae2dcfc0": N(DOCN + " (the AS3935's estimate; the sensor deferred by D-01)"),
    "caa82ce9b2": T("bank 3, which carries E6's sensor controller, has no host in the heat stage as generated; the alarm is "
                    "firmware (REQ-041)", *BANKS),
    "f61fe4f4f1": N(DOCN + " (Quectel's hardware design figures)"),
    "de89ad0ee9": T("B16's E22-900M30S", "B:U12~E22-900M30S"),
    "3acba2f6fc": N(DOCN + " (the RockBLOCK's datasheet figures)", parts_ok=PK(RB9704=DOCK + "the RockBLOCK 9704 datasheet's "
                                                                              "file name")),
    "c12b61e3ba": N(DOCN + " (a ruling's words, section 7)", absent_ok={"No hardware is added": "a ruling's scope, not a "
                                                                                          "statement of the circuit"}),
    "658f83be64": N(DOCN + " (ruling D-03's words)", absent_ok={"a drive unlocks at boot only through the secure element, the "
                                                                "panel controller and the kit I2C bus": "the accepted "
                                                                "residual risk of D-03, a ruling's words"}),
    "5fda2c0bd4": B("DC-10", "check-s122-3 m1: the D-13 row calls the STM32H753 in the schematic open; U41, U51 and U61 read "
                    "STM32H743VIT6 since 458b2873 and CON-017 reads PASS", "B:U41~STM32H743VIT6", "B:U51~STM32H743VIT6",
                    "B:U61~STM32H743VIT6", "REG:CON-017.evidence_result=PASS"),
    "357b03f343": N(DOCN + " (the pack, a ruling)", absent_ok={"and has no test summary": "a bought item's paperwork, not "
                                                                                          "the circuit"}),
    "680903352b": T("the reed is E6's sensor controller's alone (J_TAMP on board E); board C carries no lid input", "E:J_TAMP?",
                    "C:!J_TAMP"),
    "1e4489cd65": N(DOCN + " (REL-001, D-02c)", absent_ok={"so REL-001 still has no life to judge against": "a rule's "
                                                           "input, not the circuit"}),
    "bdd11249b1": B("DC-02", "section 7a's HOT-R1 row, second cell: 'only through the bridge' as generated; HOT-R1 is drawn "
                    "since w4ae (DC-02 names the row whole)", *HOTR1),
    "bd4ddb1b81": N(H + " (a dated correction of the appendix)", absent_ok={"were driven only by a software I/O expander":
                                                                           "the circuit before 458b2873, a dated record"}),
    "e2d0f2006b": N(H + " (a dated correction of the appendix)", absent_ok={"with no hardware tie to the PA keying":
                                                                           "the circuit before 458b2873, a dated record"}),
})
J["ad42c9eb94"] = dict(J["ad42c9eb94"], absent_ok=dict(J["ad42c9eb94"]["absent_ok"], **{
    "The second pack has no location found yet": "a case location for a deferred pack, not the circuit"}))
J["8b09cd80ae"]["absent_ok"] = {}
J["f3cd846998"] = N(DOCN + " (the row's sources)")
for _d, _p, _a in (
        ("5f2cf03744", {"SBAS444E": DOCK + "TI's ADS1115 data sheet number"}, []),
        ("e405a3ce91", {"C9866": "stock: the LCSC code the DS3231SN is bought under"}, []),
        ("385ae55b43", {"ATECC608B": "elsewhere: board B's U8; board D is named for the ADS1115",
                        "BQ25731": "elsewhere: board A's U3", "TPS23861": "elsewhere: board B's U5"}, []),
        ("919c0ea875", {"TCA9517A": "asserted: B:!~TCA9517A"}, ["A:!~TCA9517A", "B:!~TCA9517A"])):
    J[_d] = dict(J[_d], parts_ok=_p, a=list(J[_d].get("a", [])) + _a)

# V2-SPEC.md
T7P = ("the boards table's row read part by part against set 14's netlists (round 4: the heading's date excuses no part; "
       "each part the row names is on the netlists, or named with its date and asserted there)")
J.update({
    "13ce1d1ded": N(CASE + " (the case and its frame)", parts_ok=PK(**{"1450PF": "case: Peli's panel frame"})),
    "c73b56fb81": dict(J["c73b56fb81"], parts_ok=PK(**{"BB-2590/U": "withdrawn: the bought pack that did not fit (32.62)"})),
    "306d6f0471": dict(J["306d6f0471"], parts_ok=dict(CELL)),
    "cee0d6d5e5": T("board P's BQ4050 gauge; the pack and its ruling are the document's", "P:U1~BQ4050",
                    parts_ok=PK(**{"BB-2590/U": "withdrawn: the bought pack that did not fit (32.62)"})),
    "7827ee0779": T("E6's LT8705A solar tracker; the input's qualification is D-16's", "E:U5~LT8705A",
                    parts_ok=PK(**{"MIL-STD-461": DOCK + "a standard"}) if False else {}),
    "dd4dba6ddd": N(H + " (the withdrawn run time)", parts_ok=PK(**{"BB-2590/U": "withdrawn: the bought pack the figures were for"})),
    "dcf3b13f2a": T("per slot a PI7C9X2G404 feeding an NVMe M-key socket and one card socket; the hubs and the display "
                    "switches are board B's", "B:U101~PI7C9X2G404", "B:U201~PI7C9X2G404", "B:U301~PI7C9X2G404",
                    "B:J_M2N1~M-key 2242", "B:J_M2C1~E-key", "B:J_M2C2~B-key", "B:J_M2C3~E-key"),
    "c69433aac0": T("the supervisors are STM32H743 (U41, U51, U61); the boot floor is D-13's", "B:U41~STM32H743",
                    "B:U51~STM32H743", "B:U61~STM32H743"),
    "b37e8f58fe": T("the RockBLOCK 9704 site on B16; the helical antenna is a case item", "B:J_RB9704~RockBLOCK 9704",
                    parts_ok=PK(**{"M1621HCT-P-SMA": "case: Maxtena's antenna on the east wall"})),
    "26edd0867a": T("two AW7915-AED on card sockets of slots 1 and 3, through the changeover", "B:J_M2C1~AW7915",
                    "B:J_M2C3?", "B:J_WOA?", "B:J_WOB?"),
    "a5aa823360": T("B16's E22-900M30S on SPI; the software cap is the firmware's", "B:U12~E22-900M30S"),
    "d93fb7e9b9": T("B16's E72-2G4M20S1E (CC2652P) coordinator", "B:U13~E72-2G4M20S1E CC2652P (Zigbee coordinator)"),
    "c60dec6ff0": T("round 4's correction of line 47: D8's SA868 and the RA30H1317M1's leads, the PCM2912A U6; the sheet is "
                    "held and a row of OPERATING-ENVELOPE.md section 2", "D:*~SA868", "D:*~RA30H1317M1", "D:U6~PCM2912A",
                    "D:!~WM8960", "PDF:v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf~RA30H1317M1",
                    "DOC:v2/docs/OPERATING-ENVELOPE.md~| Mitsubishi RA30H1317M1 30 W VHF power amplifier |"),
    "26424f2f31": dict(J["26424f2f31"], parts_ok=PK(LG290P="elsewhere: board B's U11; E6 here is the Galileo band",
                                                    YEGD006U1A="case: Quectel's antenna puck on the wall")),
    "3ca8195c32": T("C7's e-paper ZIF for the E2370KS0C1", "C:J_EPD~E2370KS0C1"),
    "181b0ac69c": N(H + " (the open items closed on 7 September)"),
    "de16befa62": T(T7P + "; the TPS55288 is named as having left the design, at c5de605d", "A:U3~BQ25731", "A:U4~AP64500",
                    "A:U18~TPS25740A", "A:U19~LM5176", "A:*~INA226", "A:!~TPS55288",
                    "G@c5de605d:gen_sch_a.py:267~TPS55288",
                    parts_ok=PK(TPS55288="asserted: G@c5de605d:gen_sch_a.py:267~TPS55288")),
    "4d190b7091": T(T7P + "; the two TS3DV642 and the DS3231SN corrected in round 4 (correction 34)",
                    "B:U3~TS3DV642", "B:U4~TS3DV642", "B:U9~DS3231SN", "B:!~TMDS341", "B:U101~PI7C9X2G404",
                    "B:U102~TUSB8041", "B:U109~TMUXHS4212", "B:U110~TS3USB221A", "B:U41~STM32H743", "B:U1~KSZ9897",
                    "B:U11~LG290P", "B:U8~ATECC608B", "B:U10~TMP117", "REG:CON-017.evidence_result=PASS",
                    "DOC@b2709118:v2/ecad/tools/gen_sch_b.py~DS3231M",
                    parts_ok=PK(DS3231M="asserted: DOC@b2709118:v2/ecad/tools/gen_sch_b.py~DS3231M")),
    "ce86a25f41": T(T7P + "; the TUSB2046I corrected in round 4 (correction 34)", "D:*~SA868", "D:*~RA30H1317M1",
                    "D:U6~PCM2912A", "D:U7~TPA6132A2", "D:U4~TUSB2046IBVFR", "D:U3~CP2102N", "D:U21~TPS22810", "D:U16~PCA9555",
                    "DOC@b2709118:v2/ecad/tools/gen_sch_d.py~TUSB2046B",
                    parts_ok=PK(TUSB2046B="asserted: DOC@b2709118:v2/ecad/tools/gen_sch_d.py~TUSB2046B")),
    "86f3aabede": T(T7P + " (board P: the BQ4050 and the two CSD17570Q5B)", "P:U1~BQ4050", "P:Q1~CSD17570Q5B", "P:Q2~CSD17570Q5B"),
    "c69d9ba744": T(T7P + "; the LM5069 U6 and A22's LM5176 U2 corrected in round 4 (correction 34)", "E:U6~LM5069",
                    "E:!~LM5176", "A:U2~LM5176", "E:U5~LT8705A", "E:U14~BME688", "E:U15~BMI270"),
    "5e3035b8b7": N(DOCN + " (the cost estimate of 6 September 2026)"),
    "d807665aa1": N(DOCN + " (the cost estimate of 6 September 2026)"),
    "898c6bd452": N(DOCN + " (the cost estimate of 6 September 2026)"),
    "01d914fdce": N(H + " (the battery correction, D-06)", parts_ok=dict(CELL)),
    "003da078bf": N(H + " (the dividers before 458b2873)", parts_ok=PK(SLVSET8A=DOCK + "TI's TPS2596 data sheet number")),
    "5afecc328b": N(H + " (the run time withdrawn)", parts_ok=PK(**{"BB-2590/U": "withdrawn: the bought pack the figures were for"})),
    "0a081567c0": N(DOCN + " (the secure element's documents, ZEROIZE.md)"),
    "3dce1898a0": T("the LG290P's time pulse on board B, the DCF77 pulse on E's J_DCF; the lines are dated by the correction",
                    "B:U11~LG290P", "E:J_DCF?",
                    parts_ok=PK(LG290P="elsewhere: board B's U11; the sentence names board E for the DCF77")),
    "b32df4fdd7": T("the RM520N-GL on the key-B socket; its key is Quectel's", "B:J_M2C2~RM520N-GL", "B:J_M2C2~B-key"),
    "fe71bf585a": N(H + " (the socket until 458b2873, TE's table)",
                    parts_ok=PK(**{"1-2199119-5": "asserted: PDF:v2/vendor/m2/te-2199119-m2-b-key.pdf~2199119"}),
                    a=["PDF:v2/vendor/m2/te-2199119-m2-b-key.pdf~2199119"]),
    "b8d33d5ffb": N(H + " (D-13's words)"),
    "c8178dd548": dict(J["c8178dd548"], parts_ok=PK(C114409="stock: the LCSC code of the supervisors bought",
                                                    STM32H753="asserted: B@68bc9e8f:U41~STM32H753VITx"),
                       a=list(J["c8178dd548"].get("a", [])) + ["B@68bc9e8f:U41~STM32H753VITx"]),
    "488d983a0f": dict(J["488d983a0f"], parts_ok=PK(**{"1450PF": "case: Peli's panel frame"})),
    "269867362d": dict(J["269867362d"], parts_ok=PK(TPS55288="asserted: G@c5de605d:gen_sch_a.py:267~TPS55288")),
    "da60e25645": T("round 4's correction 34: no schematic generator has held a TMDS341A; gen_sch_b.py held the TS3DV642 at "
                    "b2709118; U3 and U4 are TS3DV642A0RUAR", "B:!~TMDS341", "DOC@b2709118:v2/ecad/tools/gen_sch_b.py~TS3DV642",
                    "B:U3~TS3DV642A0RUAR", "B:U4~TS3DV642A0RUAR", parts_ok=PK(TMDS341A="asserted: B:!~TMDS341A"),
                    **{"a": ["B:!~TMDS341A", "DOC@b2709118:v2/ecad/tools/gen_sch_b.py~TS3DV642", "B:U3~TS3DV642A0RUAR",
                             "B:U4~TS3DV642A0RUAR"]}),
    "0fcfa0f90d": T("round 4's correction 34: at b2709118 gen_sch_e.py carried the LM5069 and sent the bus into A22's LM5176; "
                    "E's U6 and A's U2 today", "DOC@b2709118:v2/ecad/tools/gen_sch_e.py~LM5069 hot-swap",
                    "DOC@b2709118:v2/ecad/tools/gen_sch_e.py~into A22's LM5176 front end", "E:U6~LM5069", "A:U2~LM5176"),
    "aea29035dd": T("round 4's correction 34: the WM8960 left gen_sch_d.py at bdfc7b3f; D's U6 is the PCM2912A; the "
                    "amplifier's sheet held", "DOC@bdfc7b3f^:v2/ecad/tools/gen_sch_d.py~WM8960",
                    "DOC@bdfc7b3f:v2/ecad/tools/gen_sch_d.py!~WM8960", "D:U6~PCM2912A", "D:!~WM8960",
                    "PDF:v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf~RA30H1317M1",
                    parts_ok=PK(WM8960="asserted: D:!~WM8960")),
    "2d74aca5ee": T("round 4's correction 34: the DS3231M and the TUSB2046B at b2709118; B's U9 DS3231SN and D's U4 "
                    "TUSB2046IBVFR today", "DOC@b2709118:v2/ecad/tools/gen_sch_b.py~DS3231M",
                    "DOC@b2709118:v2/ecad/tools/gen_sch_d.py~TUSB2046B", "B:U9~DS3231SN", "D:U4~TUSB2046IBVFR",
                    "DOC:v2/ecad/tools/gen_sch_d.py~THE HUB'S OWN RAIL (W6-F5, 26 September 2026)",
                    parts_ok=PK(DS3231M="asserted: DOC@b2709118:v2/ecad/tools/gen_sch_b.py~DS3231M",
                                TUSB2046B="asserted: DOC@b2709118:v2/ecad/tools/gen_sch_d.py~TUSB2046B")),
    "63d017d3ba": dict(J["63d017d3ba"], parts_ok=PK(ATECC608B="elsewhere: board B's U8; the toggle is C7's")),
    "5290ae6443": dict(J.get("5290ae6443", N(DOCN)), parts_ok={}),
})
def _add(d, parts=None, a=(), counts=None, absent=None, **kw):
    x = dict(J[d]); x["a"] = list(x.get("a", [])) + [y for y in a if y not in x.get("a", [])]
    if parts is not None: x["parts_ok"] = dict(x.get("parts_ok") or {}, **parts)
    if counts is not None: x["counts_ok"] = counts
    if absent is not None: x["absent_ok"] = dict(x.get("absent_ok") or {}, **absent)
    x.update(kw); J[d] = x
_add("d45adb955f", parts={"1450PF": "case: Peli's panel frame"})
_add("26edd0867a", parts={"MT7915": "module: MediaTek's chipset inside the bought AW7915-AED card"})
_add("de16befa62", a=["A:#val~rail monitor +5V_S=3"], counts={"three 5.1 V slot": "asserted: A:#val~rail monitor +5V_S=3"})
_add("4d190b7091", a=["B:U30A?", "B:U31A?", "B:U32A?", "B:#val~STM32H743=3", "B:#val~TS3DV642=2"],
     counts={"three CM5 slots": "the three slots are the receptacles U30A, U31A and U32A, asserted",
             "three STM32H743 supervisors": "asserted: B:#val~STM32H743=3",
             "two TS3DV642 display switches": "asserted: B:#val~TS3DV642=2"})
_add("ce86a25f41", a=["D:#ref~J_HS=2"], counts={"two headset jacks": "asserted: D:#ref~J_HS=2"})
_add("c69d9ba744", a=["E:#ref~J_FAN=2"], counts={"two mixer fan": "asserted: E:#ref~J_FAN=2"})
J["003da078bf"] = N(H + " (the dividers before 458b2873)")
J["fe71bf585a"] = N(H + " (the socket until 458b2873, TE's key table)", "B@1f614233:J_M2C2~1-2199119-5",
                    parts_ok={"TE 1-2199119-5": "asserted: B@1f614233:J_M2C2~1-2199119-5"})

# OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md, decisions and the status page (round 4)
SRC = DOCN + " (the row's source, a held maker's sheet)"
GLENAIR = "case: Glenair's plug, contacts, tools or strain relief, a cable item"
J.update({
    "0fea03e077": T("C7's e-paper ZIF for the E2370KS0C1", "C:J_EPD~E2370KS0C1"),
    "ee3ef3ae81": N(SRC),
    "355e205565": N(SRC, parts_ok=dict(CELL)),
    "e5f22b220e": T("round 4's row: board E's U6, the LM5069MM-2 on the 9 to 36 V input", "E:U6~LM5069MM-2",
                    "E:U6~9 V on, 40 V off"),
    "f51d88cef4": N(SRC + ", its 7.3 read by pdftotext", "PDF:v2/vendor/ti/ti-lm5069.pdf~7.3 Recommended Operating Conditions|SNVS452G",
                    parts_ok={"SNVS452G": DOCK + "TI's LM5069 data sheet number"}),
    "ccb27feb51": T("the RM520N-GL on board B's key-B socket", "B:J_M2C2~RM520N-GL"),
    "617d80160b": N(SRC),
    "97dbd8caef": T("B16's E22-900M30S", "B:U12~E22-900M30S"),
    "19e176369f": N(SRC),
    "2e18543607": T("B16's LG290P", "B:U11~LG290P"),
    "2f7f58223c": T("round 4's row: board B's J_M2C2, the TE 2199119-3 M.2 B-key socket", "B:J_M2C2~TE 2199119-3",
                    "B:J_M2C2~M.2 B-key"),
    "0ad2dab960": N(SRC + ", its Performance Ratings read by pdftotext",
                    "PDF:v2/vendor/m2/te-2199119-m2-b-key.pdf~Service Temperature -40 ~ +80|Product Specifications: 108-115042/ 108-115049",
                    parts_ok={"108-115042": DOCK + "TE's product specification number",
                              "108-115049": DOCK + "TE's product specification number"}),
    "fb87fd6753": T("D8's SA868", "D:*~SA868"),
    "37526b22ec": N(SRC + "s", parts_ok={"ELX1135": DOCK + "Eaton's SCF9550 data sheet number"}),
    "ab9bf69309": T("the two AW7915-AED card sockets of slots 1 and 3", "B:J_M2C1~AW7915", "B:J_M2C3?"),
    "d61d2ad023": N(SRC + "s"),
    "de8421d357": T("the RA30H1317M1's leads on D8", "D:*~RA30H1317M1"),
    "8470300799": N(SRC),
    "75f96bbf14": T("round 4's correction note: no netlist carries a TRACO part; board E's U6 is the LM5069; the generator's "
                    "words; the range TI's 7.3", "A:!~TRACO", "B:!~TRACO", "C:!~TRACO", "D:!~TRACO", "E:!~TRACO", "P:!~TRACO",
                    "E:!~40-2412WIN", "E:U6~LM5069", "DOC:v2/ecad/tools/gen_sch_e.py~the isolated TRACO converter of E4 is gone",
                    "PDF:v2/vendor/ti/ti-lm5069.pdf~7.3 Recommended Operating Conditions|TJ Junction temperature -40 125 °C",
                    parts_ok={"TEN 40-2412WIN": "asserted: E:!~40-2412WIN"}),
    "3641ee0106": T("round 4's correction note: no netlist carries the MDT420B01001; board B's B-key socket is TE 2199119-3 "
                    "J_M2C2 at -40 to +80 C (TE's brochure, and Amphenol's sheet the same), and the Amphenol M-key "
                    "MDT420M02001 is on J_M2N1 to J_M2N3", "B:!~MDT420B01001", "B:J_M2C2~TE 2199119-3",
                    "PDF:v2/vendor/m2/te-2199119-m2-b-key.pdf~Service Temperature -40 ~ +80",
                    "PDF:v2/vendor/m2/amphenol-mdt420b01001-m2-b-key.pdf~Operating Temperature: -40°C to +80°C",
                    "B:J_M2N1~Amphenol MDT420M02001", "B:J_M2N2~Amphenol MDT420M02001", "B:J_M2N3~Amphenol MDT420M02001",
                    parts_ok={"MDT420B01001": "asserted: B:!~MDT420B01001"}),
    "f2fe408269": N(H + " (20 September 2026)"),
    "b6626c78f7": N(H + " (the cell sheet, 26 September 2026)", parts_ok=dict(CELL)),
    "46f0dd0453": N(H + " (the list's history)"),
    "ed340e0341": N(DOCN + " (PWR-F09)"),
    "421b320d94": N(DOCN + " (TI's pin table)"),
    "8f9ef47522": N(FW + " (the cold charge rule)", parts_ok={"PRO 245-556": "bought: the RS PRO heater mat, RS stock number "
                                                                           "245-556, a case item"}),
    "ceb6a5b184": N(DOCN + " (the stored configuration, the cell maker's figures)", parts_ok=dict(CELL)),
    "0f99282a22": T("E6's LT8705A", "E:U5~LT8705A"),
    "5021436cab": N(H + " (the states' history)", parts_ok={"BB-2590/U": "withdrawn: the bought pack of 7 September"}),
    "a4d044e1b0": N(TEST, parts_ok={"CE102": DOCK + "a MIL-STD-461 test method"}),
    "8d0565d141": N(TEST, parts_ok={"CS101": DOCK + "a MIL-STD-461 test method"}),
    "27f1725b81": N(TEST, parts_ok={"CS114": DOCK + "a MIL-STD-461 test method"}),
    "83d8d5a9da": N(TEST, parts_ok={"RE102": DOCK + "a MIL-STD-461 test method"}),
    "f82bf4c812": N(TEST, parts_ok={"RS103": DOCK + "a MIL-STD-461 test method"}),
    "9d1fb48fd2": N(TEST + " (the protection table's derivation); the gauge is board P's BQ4050RSMR", "P:U1~BQ4050RSMR",
                    parts_ok=dict(CELL)),
    "e99719b420": N(TEST + " (the cell maker's ratings)", parts_ok=dict(CELL)),
    "277514ee5e": T("board P's BQ7720700 U2; its window is TI's and the network's", "P:U2~BQ7720700"),
    "c55bd6d85e": N(TEST, parts_ok={"1450PF": "case: Peli's panel frame"}),
    "05c16cdb21": T("E6's DC entry lead comes from the D38999 receptacle", "E:J_DCIN~D38999"),
    "7508456414": T("E6's panel lead comes from the D38999 spare pair", "E:J_SOLAR~D38999"),
    "f15f34a47b": T("the RA30H1317M1's leads on D8", "D:*~RA30H1317M1"),
    "d8da1b19ae": T("C7's two U-174/U jack lands", "C:J_HSJ1~U-174/U", "C:J_HSJ2~U-174/U"),
    "71cd0b1fad": N(CASE + " (the heater mat)", parts_ok={"PRO 245-556": "bought: the RS PRO heater mat, RS stock number "
                                                                         "245-556, a case item"}),
    "9b7ccbd8ec": T("the RM520N-GL on the key-B socket; its ports are Quectel's", "B:J_M2C2~RM520N-GL"),
    "cda4473e43": N(CASE + " (the connector plate's six items)", parts_ok={"PX0833": "case: a candidate RJ45 the row rejects",
                                                                           "PXP4043/C": "case: the sealed USB-C's panel part",
                                                                           "D38999/20": "case: the DC receptacle's shell"}),
    "c5afe71421": N(FW + " (the gauge's charge window; board P's BQ4050)", "P:U1~BQ4050"),
    "a66de8d3b1": N(H + " (the step's correction; TI's pin table)"),
    "1f1b7f0b3f": N(DOCN + " (W2 finding F-DEC40)"),
    "c2d955fc38": T("the passage DC-10 keeps", "DOC:v2/docs/CONOPS.md~the component mismatch with the STM32H753 in the "
                    "schematic closes only when", "B@68bc9e8f:U41~STM32H753VITx",
                    parts_ok={"STM32H753": "asserted: B@68bc9e8f:U41~STM32H753VITx"}),
    "53772fb573": T("DC-10's value: U41, U51 and U61 read STM32H743VIT6 since 458b2873, STM32H753VITx at 68bc9e8f where "
                    "the row was written; CON-017 PASS", "B:U41~STM32H743VIT6", "B:U51~STM32H743VIT6", "B:U61~STM32H743VIT6",
                    "B@458b2873:U41~STM32H743VIT6", "B@68bc9e8f:U41~STM32H753VITx",
                    "DOC@68bc9e8f:v2/docs/CONOPS.md~the component mismatch with the STM32H753 in the schematic closes only when",
                    "REG:CON-017.evidence_result=PASS",
                    "REG:CON-017.statement~the STM32H743VIT6 the project buys, in the schematic text, the symbol value and the BOM",
                    parts_ok={"STM32H753VITx": "asserted: B@68bc9e8f:U41~STM32H753VITx"}),
})
_add("dfd6170bf6", a=["G@c5de605d:gen_sch_a.py:267~TPS55288"], parts={"TPS55288": "asserted: G@c5de605d:gen_sch_a.py:267~TPS55288"})
_add("f7d96bf556", parts={"SA868": "elsewhere: board D's U2 and U13; board B is named for the RockBLOCK"})
_add("93f1cf837d", parts={"1450PF": "case: Peli's panel frame"})
_add("18891567a1", parts=dict(CELL))
_add("00410dee37", parts={"TMP117": "elsewhere: board B's U10; board A is named for its converters"})
_add("ef9f31ab35", parts={"BB-2590/U": "withdrawn: the bought pack of 7 September",
                          "BTA-70762-2": "asserted: G@45bde541:gen_sch_e.py:193~J_BATT|BTA-70762-2"})
_add("643c162767", parts={"DP8005": "bought: 3M's DP8005 adhesive, a case material"})
_add("a60b800d87", parts={"C144395": "stock: the LCSC code of the JST B4B-XH-A", "C594232": "stock: the LCSC code of the gold "
                                                                                          "variant the row sets aside"})
_add("20f3ba1ddd", parts={"BB-2590/U": "withdrawn: the bought pack of 7 September"})
_add("27280d94b4", parts={"R222M80500": "case: Radiall's plug on the float clamp's cable"})
_add("3a53e10db7", parts={k: GLENAIR for k in ("D38999/26FC4SN", "M39029/56-352", "M22520/1-01", "M22520/1-04",
                                               "M81969/14-03", "M85049/38S13N")})
_add("7211912728", parts={"R222M80500": "case: Radiall's plug on the float clamp's cable"})
_add("cd9739a701", parts={"7871EC": "bought: 3M's serial label, a case item", "DP8005": "bought: 3M's DP8005 adhesive, a case material"})
_add("60324e1220", parts={"JLC04162H-7628": "stackup: JLCPCB's stackup code"})
_add("ad17cbd96a", a=["B:!~TCA9517A"], parts={"TCA9517A": "asserted: B:!~TCA9517A"})
J["53772fb573"] = dict(J["53772fb573"], parts_ok={}, a=J["53772fb573"]["a"] + ["B:#val~STM32H743=3"],
                       counts_ok={"three supervisors": "asserted: B:#val~STM32H743=3"})

# the texts round 4 corrected, as they stood on set 14 (1bafab8c) and at the base: STALE, with what the netlists carry
J.update({
    "2d94b4029a": S("the WM8960 left gen_sch_d.py at bdfc7b3f and D8's codec is the PCM2912A U6; the RA30H1317M1's sheet is "
                    "held (corrected in round 4, correction 34)", "D:!~WM8960", "D:U6~PCM2912A",
                    "DOC@bdfc7b3f:v2/ecad/tools/gen_sch_d.py!~WM8960", "PDF:v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf~RA30H1317M1"),
    "b1e7494b6d": S("the TMDS341A no generator has held (board B's display switches are the TS3DV642 U3 and U4, as at "
                    "b2709118) and the DS3231M (board B's U9 is the DS3231SN) (corrected in round 4, correction 34)",
                    "B:!~TMDS341", "B:U3~TS3DV642", "B:U4~TS3DV642", "B:U9~DS3231SN",
                    "DOC@b2709118:v2/ecad/tools/gen_sch_b.py~TS3DV642"),
    "40489568ae": S("the TUSB2046B: board D's U4 is the TUSB2046IBVFR since 26 September 2026 (corrected in round 4, "
                    "correction 34)", "D:U4~TUSB2046IBVFR", "D:!~TUSB2046B"),
    "0a2d2b6e41": S("the LM5176 front end on E6: board E carries the LM5069 U6, and the LM5176 front end is A22's U2, as "
                    "at b2709118 (corrected in round 4, correction 34)", "E:U6~LM5069", "E:!~LM5176", "A:U2~LM5176",
                    "DOC@b2709118:v2/ecad/tools/gen_sch_e.py~into A22's LM5176 front end"),
    "2b5ab8d2af": S("no netlist carries a TRACO part; board E's input part is the LM5069 U6 (replaced in round 4)",
                    "A:!~TRACO", "B:!~TRACO", "C:!~TRACO", "D:!~TRACO", "E:!~TRACO", "P:!~TRACO", "E:U6~LM5069"),
    "40344bc9e0": S("the row's source is Amphenol's MDT420B01001, on no netlist; board B's B-key socket is TE 2199119-3 "
                    "J_M2C2 (replaced in round 4)", "B:!~MDT420B", "B:J_M2C2~TE 2199119-3"),
})
J["9743b00cb6"] = S("the holdover clock is board B's DS3231SN U9 on the kit bus, not the panel controller's (corrected in "
                    "round 1, correction 32); the base's text, inventoried since round 4 by its part number", "B:U9~DS3231SN",
                    "B:U11~LG290P", "C:!~DS3231")

# ================================================================== ROUND 5 (check-s122-4: parts in their roles; m1 to m3)
# a part named in a role is judged by verdicts.check_roles; `roles_ok` binds a role the netlist states in other words to
# one of the judgement's own assertions on the designator that carries the part
A81 = ["A:U3~BQ25731", "A:U3~charger", "A:U4~AP64500", "A:U4~+5V_S1", "A:U6~AP64500", "A:U6~+5V_S3", "A:U5~LM5176",
       "A:U5~+5V_S2", "A:U7~LM5176", "A:U7~+5V_DEV", "A:U8~INA226 rail monitor +5V_S1", "A:U9~INA226 rail monitor +5V_S2",
       "A:U10~INA226 rail monitor +5V_S3", "A:U11~INA226 rail monitor +5V_DEV", "A:U13~+13V8_PA", "A:U15~+12V_HF",
       "A:U13~LM5176", "A:U15~LM5176", "A:U18~TPS25740A", "A:U19~LM5176", "A:U19~PD_VPWR", "A:!~TPS55288",
       "G@c5de605d:gen_sch_a.py:267~TPS55288", "DOC@b2709118:v2/ecad/tools/gen_sch_a.py~SLOT RAIL S2: AP64500 5.1 V",
       'DOC@b2709118:v2/ecad/tools/gen_sch_a.py~buck5("D", "U7", "DEV_EN", "+5V_DEV"', "A:#val~rail monitor +5V_S=3"]
A84 = ["D:*~SA868", "D:*~RA30H1317M1", "D:U6~PCM2912A", "D:U7~TPA6132A2", "D:U4~TUSB2046IBVFR", "D:U3~CP2102N",
       "D:U15~TLV75801", "D:U15~PA gate bias", "D:U15.4=PA_KEY", "D:U21~TPS22810DRV load switch, +5V_TX", "D:U16~PCA9555",
       "DOC@b2709118:v2/ecad/tools/gen_sch_d.py~TUSB2046B",
       "DOC@b2709118:v2/ecad/tools/gen_sch_d.py~PA gate bias switched by a TPS22810 on PA_KEY", "D:#ref~J_HS=2"]
A86 = ["E:U6~LM5069", "E:!~LM5176", "A:U2~LM5176", "A:U2~VBUS20 from VIN_RAW", "E:U5~LT8705A", "E:U5.32=PV_P",
       "E:U14~BME688", "E:U15~BMI270", "E:!~magnetometer", "E:J_POD?", "E:SDA1>J_POD,U14,U15",
       "DOC:v2/ecad/tools/gen_sch_e.py~the magnetometer sits in the outside pod (32.57)", "E:#ref~J_FAN=2"]
A83 = ["C:#fp~LED_D3.0mm=17", "C:D22~EMCON", "REG:S-44.status=OPEN", "C:U1~PCA9555", "C:U2~PCA9555",
       "C:U_LIGHT~VEML7700", "C:J_EPD~E2370KS0C1", "C:*~RP2040"]
FRONT = {"LM5176 front end": "A:U2~VBUS20 from VIN_RAW"}
TRACK = {"LT8705A tracker": "E:U5.32=PV_P"}
T7R = ("the boards table's row read part by part and role by role against set 14's netlists (round 5: each part named "
       "in a role asserted on the designator whose value states it)")
J.update({
    "a77bf9d173": T(T7R + "; line 81 corrected in round 5 (correction 35)", *A81,
                    parts_ok={"TPS55288": "asserted: G@c5de605d:gen_sch_a.py:267~TPS55288"},
                    counts_ok={"three 5.1 V slot": "asserted: A:#val~rail monitor +5V_S=3"}),
    "3f426d1736": T(T7R + "; line 83's seventeen LEDs (correction 35)", *A83,
                    counts_ok={"seventeen 3 mm LEDs": "asserted: C:#fp~LED_D3.0mm=17"}),
    "2955447136": T(T7R + "; line 84's gate bias and load switch corrected in round 5 (correction 35)", *A84,
                    parts_ok={"TUSB2046B": "asserted: DOC@b2709118:v2/ecad/tools/gen_sch_d.py~TUSB2046B"},
                    counts_ok={"two headset jacks": "asserted: D:#ref~J_HS=2"}),
    "ef24592b40": T(T7R + "; line 86's magnetometer placed in round 5 (correction 35)", *A86,
                    roles_ok=dict(FRONT, **TRACK), counts_ok={"two mixer fan": "asserted: E:#ref~J_FAN=2"}),
    "a5dd468127": T("round 5's correction 35: D's U15 TLV75801 on PA_KEY since faf8c981, U21 the TPS22810 load switch of "
                    "+5V_TX, the TPS22810 bias switch at b2709118", "D:U15~TLV75801", "D:U15~PA gate bias", "D:U15.4=PA_KEY",
                    "D:U21~TPS22810DRV load switch, +5V_TX", "DOC@faf8c981:v2/ecad/tools/gen_sch_d.py~TLV75801",
                    "DOC@faf8c981^:v2/ecad/tools/gen_sch_d.py!~TLV75801",
                    "DOC@b2709118:v2/ecad/tools/gen_sch_d.py~PA gate bias switched by a TPS22810 on PA_KEY"),
    "cce8eb40b9": T("round 5's correction 35: A's U4 and U6 AP64500 for slots 1 and 3, U5 and U7 LM5176 for slot 2 and "
                    "the device rail, all four AP64500 at b2709118", "A:U4~AP64500", "A:U4~+5V_S1", "A:U6~AP64500",
                    "A:U6~+5V_S3", "A:U5~LM5176", "A:U5~+5V_S2", "A:U7~LM5176", "A:U7~+5V_DEV",
                    "DOC@b2709118:v2/ecad/tools/gen_sch_a.py~SLOT RAIL S2: AP64500 5.1 V",
                    'DOC@b2709118:v2/ecad/tools/gen_sch_a.py~buck5("D", "U7", "DEV_EN", "+5V_DEV"'),
    "9426065bb9": T("round 5's correction 35: E carries the BME688 U14 and the BMI270 U15 and no magnetometer; the pod "
                    "through J_POD", "E:U14~BME688", "E:U15~BMI270", "E:!~magnetometer", "E:J_POD?",
                    "DOC:v2/ecad/tools/gen_sch_e.py~the magnetometer sits in the outside pod (32.57)"),
    "2d75300367": T("round 5's correction 35: seventeen 3 mm LEDs on C, D22 among them", "C:#fp~LED_D3.0mm=17", "C:D22~EMCON",
                    counts_ok={"sixteen LEDs": "the count line 83 read before round 5, not a count of parts today"}),
    "fda86ae247": N(DOCN + " (D-01's list of what is outside the core)"),
    "1e4516ad21": N(DOCN + " (what EMCON leaves running, D-05)"),
    "9d165f761a": T("E6's SGP41 U17; its response to hydrogen is TBD", "E:U17~SGP41"),
    "70e56e5818": T("the USB devices on the slots' hubs: the bridges U15 to U18 on B, the panel controller on C and the sensor "
                    "controller on E (RP2040), D8's audio set; the HAL is software", "B:U15~CP2102N", "B:U18~CP2102N",
                    "C:*~RP2040", "E:U10~RP2040", "D:U6~PCM2912A"),
    "181b0ac69c": dict(J["181b0ac69c"], parts_ok={"ASM118x": "withdrawn: the PCIe switch candidate the line closes (0 stock)"}),
    "0fcfa0f90d": dict(J["0fcfa0f90d"], a=J["0fcfa0f90d"]["a"] + ["A:U2~VBUS20 from VIN_RAW"], roles_ok=dict(FRONT)),
    "c095df105a": T("E6's SGP41 U17", "E:U17~SGP41"),
    "39d7edd5fb": N(SRC),
    "0ace90f506": T("B16's two E72-2G4M20S1E", "B:U13~E72-2G4M20S1E", "B:U14~E72-2G4M20S1E"),
    "c5648bf2c9": N(DOCN + " (the SGP41's maker range, a row of the thermal table)"),
    "8b5aa200e3": N(DOCN + " (the independent bound, POWER-THERMAL.md)"),
    "0c1acec366": N(H + " (the table kept as the record)"),
    "c9db060f24": N(TEST + " (the pass line; the parts' storage ranges are their makers')"),
    "0db8c79894": N(TEST + " (REQ-052's part ranges)"),
    "2ef464f93e": N(CASE + " (the face parts' heights, lid-tray-qmx-r2-check.out)"),
    "b6d8561165": T("the XT60 pair: board P's and board E's XT60 leads", "E:J_BATT~XT60"),
    "654cac0bee": N(CASE + " (the sealed RJ45 on the connector plate)"),
    "c6b30de010": N(CASE + " (a lead's ends)"),
})
_add("f46acf5130", parts={"DCF77": "elsewhere: board E's J_DCF; board D is named for its transmit gate"})
_add("3d47dcd92b", a=["C:U1~PCA9555PW 0x22: LED sinks, light mode inputs"],
     roles_ok={"PCA9555 expander": "C:U1~PCA9555PW 0x22: LED sinks, light mode inputs"})
J["5f2cf03744"] = dict(J["5f2cf03744"], parts_ok={})
_add("7827ee0779", a=["E:U5.32=PV_P"], roles_ok=dict(TRACK))
_add("6b8e35c93d", parts={"DCF77": "elsewhere: board E's J_DCF, as the sentence says; board B is named for the clock"})
_add("0aa470c049", a=["DOC:v2/ecad/tools/gen_sch_e.py~the magnetometer sits in the outside pod (32.57)", "E:!~LIS3MDL"],
     parts={"LIS3MDL": "owed: the outside pod's magnetometer, in a pod no netlist carries (gen_sch_e.py)"})
J["f51d88cef4"] = dict(J["f51d88cef4"], parts_ok={})
_add("5f30437813", parts={"SGP41": "elsewhere: board E's U17; board A is named for its converters"})
_add("cd9739a701", parts={"GP60": "bought: Silex's silicone washers, a case item", "SO-M3-10": "case: PEM standoffs"})
_add("53772fb573", parts={"STM32H753VITx": "asserted: B@68bc9e8f:U41~STM32H753VITx"})
_add("70e56e5818", parts={"RP2040-class": "module: a class of controller; the RP2040 on boards C and E is asserted"})
_add("cce8eb40b9", a=["A:#val~rail monitor +5V_S=3"], counts={"three slot": "asserted: A:#val~rail monitor +5V_S=3"})
_add("2d75300367", counts={"sixteen LEDs": "the LEDs line 83 counted before round 5, not a count of parts today"})

# the texts round 5 corrected, as they stood at edead832 and on set 14: STALE, with what the netlists carry
J.update({
    "de16befa62": S("check-s122-4 B1: the AP64500 is the buck of slots 1 and 3 only (A's U4, U6); U5 and U7, slot 2 and "
                    "the device rail, are LM5176 stages (corrected in round 5, correction 35)", "A:U4~AP64500", "A:U6~AP64500",
                    "A:U5~LM5176", "A:U5~+5V_S2", "A:U7~LM5176", "A:U7~+5V_DEV"),
    "ce86a25f41": S("check-s122-4 B1: board D's gate bias is U15, a TLV75801 on PA_KEY; the TPS22810 is U21, the load "
                    "switch of +5V_TX (corrected in round 5, correction 35)", "D:U15~TLV75801", "D:U15~PA gate bias",
                    "D:U15.4=PA_KEY", "D:U21~TPS22810DRV load switch, +5V_TX"),
    "c69d9ba744": S("check-s122-4 m2: board E carries no magnetometer; gen_sch_e.py puts it in the outside pod, reached "
                    "through J_POD (corrected in round 5, correction 35)", "E:!~magnetometer", "E:J_POD?",
                    "DOC:v2/ecad/tools/gen_sch_e.py~the magnetometer sits in the outside pod (32.57)",
                    "A:U2~VBUS20 from VIN_RAW", "E:U5.32=PV_P", roles_ok=dict(FRONT, **TRACK)),
    "fa00f9ca7e": S("check-s122-4 m3: board C carries seventeen 3 mm LEDs, D22 the seventeenth; the heading's date excuses "
                    "no count (corrected in round 5, correction 35)", "C:#fp~LED_D3.0mm=17", "C:D22~EMCON"),
    "3f5e49de5a": S("the TRACO sheet of a converter no netlist carries (the row replaced in round 4)", "E:!~TRACO"),
})

# ================================================================== ROUND 6 (check-s122-5: B1 the exciter's rating; the figures)
# every figure-and-unit token on a line of the closing list (close_s122.py's scan: a number with a unit, a range, an
# 'N x M' size, a 'NxM' header, a spelled count) is bound in `figures_ok` (or an 'asserted:' entry of `counts_ok`) to one
# of the judgement's own assertions whose stated content carries its numbers: a netlist value, a board file's outline,
# layers, cutout or zones, a maker's page, or, for a figure about a ruling, the decision's own record
SA868 = "v2/vendor/nicerf/nicerf-sa868-datasheet-v1.3.pdf"
RA30 = "PDF:v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf~RA30H1317M1 RoHS Compliance, 135-175MHz 30W 12.5V"
EX2 = "D:U2~NiceRF SA868 VHF 2 W exciter"
DCIN = "E:J_DCIN~9 to 36 V"
F81 = {"240 x 160 mm": "PCB:A:outline=240x160", "six layers": "PCB:A:layers=6",
       "14.4 V node": "PDF:v2/vendor/battery/ti-bq4050.pdf~VCC = 14.4 V", "9 to 36 V input": DCIN,
       "three 5.1 V slot rails": "A:#val~5.1 V rail to B16=3",
       "all four AP64500 on 7 September": "CNT@b2709118:v2/ecad/tools/gen_sch_a.py~AP64500 5.1 V + INA226=4",
       "13.8 V PA": "A:U13~+13V8_PA", "12 V HF": "A:U15~+12V_HF", "54 V PoE": "A:U16~+54V_POE",
       "45 W USB-C outlet": "A:U18~45 W outlet", "3.3 V logic": "A:U12~3.3 V logic",
       "eleven SMP-MAX blind-mate sites": "A:#fp~Radiall_SMPMAX=11", "2x13 ribbon": "A:J_AB1~IDC 2x13"}
F82 = {"330 x 200 mm": "PCB:B:outline=330x200", "six layers": "PCB:B:layers=6", "In4 the 5 V planes": "PCB:B:zone=In4.Cu~+5V",
       "measured on eight layers first": "DEC:43.outcome~board B is regenerated and routed once on eight layers",
       "three CM5 slots": "B:#fp~CM5_Conn_A_10164227=3", "two CAN-FD fabrics": "B:U41~two CAN-FD fabrics",
       "seven 2-of-3 voters": "B:#net~_CA=7", "two E72": "B:#val~E72-2G4M20S1E=2"}
F83 = {"344 x 228 ring": "PCB:C:outline=344x228", "240 x 176 void": "PCB:C:hole=240x176", "four layers": "PCB:C:layers=4",
       "six ruled by the owner on 25 Sep 2026, decision 27": "DEC:27.outcome~six layers for board C",
       "seventeen 3 mm LEDs": "C:#val~3 mm=17", "two PCA9555": "C:#val~PCA9555=2"}
F84 = {"100 x 80 mm": "PCB:D:outline=100x80", "four layers": "PCB:D:layers=4"}
F86 = {"267 x 68 mm": "PCB:E:outline=267x68", "four layers": "PCB:E:layers=4", "9 to 36 V input": DCIN,
       "25 A fuse": "E:F3~25 A mini blade", "eleven float clamps": "PCB:E:zones~no copper under the float clamp=11"}


def _figs(d, f, extra=(), **kw):
    """Bind a judgement's figures: every value of `f` becomes one of its own assertions and its 'asserted:' figure."""
    _add(d, a=list(f.values()) + list(extra), figures_ok={k: "asserted: " + x for k, x in f.items()}, **kw)


_figs("a77bf9d173", F81, extra=["P:U1~4S balancing"], counts={"three 5.1 V slot": "asserted: A:#val~5.1 V rail to B16=3"})
_figs("4d190b7091", F82, counts={"three CM5 slots": "asserted: B:#fp~CM5_Conn_A_10164227=3",
                                 "three STM32H743 supervisors": "asserted: B:#val~STM32H743=3",
                                 "two TS3DV642 display switches": "asserted: B:#val~TS3DV642=2"})
_figs("3f426d1736", F83, counts={"seventeen 3 mm LEDs": "asserted: C:#val~3 mm=17"})
_figs("2955447136", F84)
_figs("ef24592b40", F86)
_figs("e5f22b220e", {"9 to 36 V input": DCIN})
J.update({
    # line 47 as round 6 corrected it (correction 36)
    "6df916ee4f": T("round 6's correction of line 47 (check-s122-5 B1, correction 36): D8's U2 is the SA868 VHF 2 W exciter, "
                    "which the maker's sheet v1.3 rates 31 to 33 dBm high and 24 to 26 dBm low; the RA30H1317M1's sheet, "
                    "held and a row of OPERATING-ENVELOPE.md section 2; the PCM2912A U6", EX2, "D:*~RA30H1317M1",
                    "D:U6~PCM2912A", "D:!~WM8960", "PDF:%s~31 32.5 33 dBm|24 25 26 dBm" % SA868, RA30,
                    "DOC:v2/docs/OPERATING-ENVELOPE.md~| Mitsubishi RA30H1317M1 30 W VHF power amplifier |",
                    figures_ok={"SA868 VHF 2 W exciter": "asserted: " + EX2, "30 W VHF amplifier stage": "asserted: " + RA30}),
    # line 47 as it stood at edead832 and a6429e66: the 1 W of the device set of 6 September
    "c60dec6ff0": S("check-s122-5 B1: board D's U2 is the SA868 VHF 2 W exciter (the sheet v1.3: 31 to 33 dBm high), not a "
                    "1 W part (corrected in round 6, correction 36)", EX2, "PDF:%s~31 32.5 33 dBm|24 25 26 dBm" % SA868),
    # correction 36's sentences
    "e2179973eb": T("round 6's correction 36: the device set of 6 September (appendix 32.49) named the SA868 a 1 W module, "
                    "and line 47 said 1 W at a6429e66", "DOC:v2/docs/MESHSAT-709-geometry-appendix.md~### 32.49 The V2 device set",
                    "DOC:v2/docs/MESHSAT-709-geometry-appendix.md~**NiceRF SA868 1 W module plus a 30 W VHF amplifier stage**",
                    "DOC@a6429e66:v2/docs/V2-SPEC.md~NiceRF SA868 1 W with a 30 W VHF amplifier stage"),
    "1f465555dc": T("round 6's correction 36: D's U2, the generator's rating since bdfc7b3f (not before it), the sheet v1.3",
                    EX2, "DOC:v2/ecad/tools/gen_sch_d.py~the NiceRF SA868 VHF exciter (bench-fitted, 2 W high / 0.5 W low)",
                    "DOC@bdfc7b3f:v2/ecad/tools/gen_sch_d.py~2 W high / 0.5 W low",
                    "DOC@bdfc7b3f^:v2/ecad/tools/gen_sch_d.py!~2 W high", "PDF:%s~31 32.5 33 dBm|24 25 26 dBm" % SA868),
    # two cells of the closing list's OPERATING-ENVELOPE.md rows that carry a figure and no name, so the inventory does not
    # take them (s122lib.inventory reads a sentence that names something); close_s122.py's scan reads the listed lines
    # whole and runs these judgements' assertions itself
    "056f8a2031": T("board E's U6, the LM5069: its maker's recommended junction range (SNVS452G, 7.3)",
                    "PDF:v2/vendor/ti/ti-lm5069.pdf~Junction temperature|40 125 °C (1) For detailed information on soldering plastic VSSOP",
                    figures_ok={"-40 to +125 C": "asserted: PDF:v2/vendor/ti/ti-lm5069.pdf~Junction temperature|40 125 °C (1) "
                                "For detailed information on soldering plastic VSSOP"}),
    "21f5924adb": T("board B's J_M2C2, TE 2199119-3: its maker's service temperature",
                    "PDF:v2/vendor/m2/te-2199119-m2-b-key.pdf~Service Temperature -40 ~ +80",
                    figures_ok={"-40 to +80 C": "asserted: PDF:v2/vendor/m2/te-2199119-m2-b-key.pdf~Service Temperature -40 ~ +80"}),
})

# ================================================================== ROUND 7 (check-s122-6: B1 the 14.4 V node, m1 signed values, m4 the finder)
# B1: line 81's "14.4 V node" is bound to the generator's declaration of board P's cell node (gen_sch_p.py's rail intent
# CELL4 at 14.4 V nominal, 10.0 to 18.0 V), beside board P's 4S block (J_CELL) and the cell maker's 3.60 V nominal; the
# BQ4050 sheet's test condition (VCC = 14.4 V) is dropped, since it holds whatever pack board P carries
CELL4 = 'DOC:v2/ecad/tools/gen_sch_p.py~_intent.rail("CELL4", 14.4, 10.0, 18.0, "W_BP"'
AH35E = "PDF:v2/vendor/battery/samsung-35e-orbtronic.pdf~3.3 Nominal Voltage 3.60V"
_j = dict(J["a77bf9d173"])
_j["a"] = [x for x in _j["a"] if "ti-bq4050" not in x and x != "P:U1~4S balancing"] + [
    CELL4, "P:J_CELL~4S block", "DOC:v2/ecad/tools/gen_sch_p.py~one 4S3P block of Samsung INR18650-35E", AH35E]
_j["figures_ok"] = dict(_j["figures_ok"], **{"14.4 V node": "asserted: " + CELL4})
J["a77bf9d173"] = _j
F81["14.4 V node"] = CELL4
# m1: the LM5069's junction range asserted with its sign (the PDF reader reads the sheet's U+2013 minus as '-')
LM69 = "PDF:v2/vendor/ti/ti-lm5069.pdf~TJ Junction temperature -40 125 °C|(1) For detailed information on soldering plastic VSSOP"
J["056f8a2031"] = T("board E's U6, the LM5069: its maker's recommended junction range, -40 to 125 C (SNVS452G, 7.3)", LM69,
                    figures_ok={"-40 to +125 C": "asserted: " + LM69})
# m4: the part numbers the finder reads since this round, each excused by what it is
XEN = "bought: the Xenarc monitor, a bought unit wired by its leads, on no board"
CPL = "case: Amphenol's SMA couplers of the case templates, which the case set of 27 September 2026 retired"
_add("d757d209e1", parts={"709GNK": XEN})
_add("facb104de6", parts={"132170": CPL})
_add("26424f2f31", parts={"ANN-MB2": "bought: u-blox's GNSS antenna, the puck's alternative, on no board"})
_add("488d983a0f", parts={"132170": CPL})
_add("cd9739a701", parts={"132170": CPL, "422B": "bought: MG Chemicals' conformal coating, a material"})
_add("1f1b7f0b3f", parts={"S-8261": "withdrawn: ABLIC's single-cell protector, which decision 40 set aside",
                          "bq2970": "withdrawn: TI's single-cell protector, which decision 40 set aside"})
J.update({
    "05b3d33f08": N(DOCN + " (the monitor's maker figure, its product manual)", parts_ok={"709GNK": XEN}),
    "158db4d812": N(CASE + " (the monitor set into the plate, its maker data and appendix 32.85)", parts_ok={"709GNK": XEN}),
    "c64a44b1c1": N(CASE + " (the monitor's name as a row's subject)", parts_ok={"709GNK": XEN}),
    "7fa81a144e": N(H + " (the couplers until 27 September 2026)", parts_ok={"132170": CPL},
                    counts_ok={"eleven Amphenol 132170 couplers": "the couplers of the case until 27 September 2026, "
                               "case items on no netlist"}),
    "9a3c85265f": N(CASE + " (a lead's cable)", parts_ok={"0021917": "bought: Lapp's cable, its article number, a lead"}),
})
