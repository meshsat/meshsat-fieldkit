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
                    *AGATES[:10], *DKEY, "C:D22~amber", "C:U14.3=TX_INHIBIT_n"),
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
    "b719e651bd": T("the dated reading's effects hold, and board B's round 8 removes the 5G supply", *LIME[:5], *RB[:10],
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
