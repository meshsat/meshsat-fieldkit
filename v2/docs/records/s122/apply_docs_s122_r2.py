#!/usr/bin/env python3
"""Stream s122, round 2 (S-122, MESHSAT-1357, 29 September 2026): the answer to the independent check of fnd/s122 at
dac1b672 (`checks/check-s122-1.md`: B1 to B3, m1 to m12) and to the coordinator's ruling on CONOPS.md's baseline.

1. CONOPS.md is a BASELINED layer 2 definition (its head, and `handover/DEFINITION-STATUS.md`): a circuit correction
   goes to the status page and the records it names, not to the baseline. Set 12's two circuit commits (`a46db71b`,
   `7a9f7b5b`) and stream s122's round 1 edited it against that rule, so the script RESTORES CONOPS.md to its text at
   `c5430071` (the owner's rulings of 28 September, the last change the rule allows) and asserts the file equals
   `git show c5430071:v2/docs/CONOPS.md` byte for byte, with the needs table unchanged.
2. The current circuit goes where the rule's dependency list says: the section 4b table and the EMCON row as `7a9f7b5b`
   wrote them (the text of `records/int13/apply_conops_4b_set12.py`, asserted there equal to what 7a9f7b5b committed)
   become `feasibility/EMCON.md` section 0a.1, re-asserted here on set 13's netlists; the status page gains a section
   that says CONOPS's circuit passages are baseline values and names where each current value is kept (EMCON, HOT-R1,
   the TX lamp, the device rails, the +3V3_DEV loss, generator line numbers), and a row in its dependency table.
3. The five correctable documents: PANEL.md section 3's GPIO 2 to 5 rows (set 13's R53 to R56), line 156's E22 lines
   (m6), line 180's provenance (set 13's netlists); OPERATING-ENVELOPE.md line 286's PA bias (m2); ASSEMBLY.md lines 87,
   217, 218 and 219 (B2), 180 (m5) and 204 (m4); V2-SPEC.md lines 30, 81 and 82 (m7) and correction 32 under its own
   dated heading with line 3 naming it (m8).
Every part, pin, net, count and generator line the new text names is asserted on the committed netlists (tx_inhibit
.parse_netlist) and the generators before anything is written (the assertion language of `verdicts.py`); each old
passage is found once, each new one reads back once, no dash; each document re-parses; the diff touches only the
corrected passages. Refuses a second run. Run: python3 apply_docs_s122_r2.py [--check]."""
import hashlib, os, re, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import verdicts as V  # noqa: E402

sys.path.insert(0, os.path.join(L.TOP, "v2/docs/records/int13"))
import apply_conops_4b_set12 as C12  # noqa: E402

TAG = "apply_docs_s122_r2"
BASE = "4d3a9708"          # fnd/s122 with set 13's candidate merged
CON = "v2/docs/CONOPS.md"
EMC = "v2/docs/feasibility/EMCON.md"
DST = "v2/docs/handover/DEFINITION-STATUS.md"
DOCS = {"v2/docs/PANEL.md": "9d2a685ac4c43d38", "v2/docs/V2-SPEC.md": "ad40490efe51731b",
        "v2/docs/OPERATING-ENVELOPE.md": "33506f34caf6ec6f", "v2/docs/ASSEMBLY.md": "0269bc353f29ba47",
        EMC: "e919e9b2c633deef", DST: "0ac85070530ef7a6"}
NETS = {"A": "6c40250c47195ebb", "B": "3ef9b8c49a01b728", "C": "c9f7394594201045", "D": "a2d48972d171aad1",
        "E": "2ed95a0e8069ebf8", "P": "20c7b0795593d761"}

# ------------------------------------------------------------------ what the moved EMCON text names, asserted
EMCON_A = ["%s:%s.%s=%s" % (b, r, p, n) for b, r, _v, pins in C12.GATES for p, n in pins.items()] + \
          ["%s:%s~%s" % (b, r, v) for b, r, v, _p in C12.GATES if v] + \
          ["%s:%s?" % (b, r) for b, r, _v, _p in C12.GATES] + [
    # what apply_conops_4b_set12.py's GATES did not assert (check-int13-3 n1; check-s122-1 m1)
    "C:U9.5=+3V3", "C:D23~BAT46W", "B:U112.5=+3V3_CM1", "B:U501.5=+3V3_DEV", "B:U503.5=+3V3_DEV", "B:U536.5=+3V3_DEV",
    "B:U102@PWRCTL1=LIME_HW_EN", "B:R529.1=LIME_EN", "B:R529.2=LIME_UVLO", "B:U23~TPS259631", "B:U23.3=LIME_UVLO",
    "B:U23.4=+5V_DEV", "B:U23.5=+5V_LIME", "B:+5V_LIME>J_LIME", "B:R530.1=RB_EN", "B:R530.2=RB_UVLO", "B:U24~TPS259631",
    "B:U24.3=RB_UVLO", "B:U24.4=+5V_DEV", "B:U24.5=+5V_RB", "B:J_RB9704.15=+5V_RB", "B:J_RB9704.14=RB_RXD",
    "B:J_RB9704.6=RB_CTRL", "B:U6@IO0_2=RB_SW_EN", "B:U6@IO1_6=RB_SW_IEN", "B:R527.1=RB_IEN", "B:R531.1=E22_EN",
    "B:R531.2=E22_UVLO", "B:U21~TPS22810", "B:U21.5=E22_UVLO", "B:U21.1=+5V_LORA", "B:U12.9=+5V_LORA",
    "B:U547.1=SPI3_IO26", "B:U548.1=SPI3_MOSI", "B:U549.1=SPI3_SCLK", "B:U550.1=SPI3_CE1", "B:U553~74LVC1G34",
    "B:U22~TPS22810", "B:U22.5=E72_EN", "B:U22.1=+3V3_ZB", "B:U22.6=+3V3_DEV", "B:U540.1=ZBA_RXD_H", "B:U540.3=ZBA_RST_H",
    "B:U540.5=+3V3_DEV", "B:U542.1=ZBB_RXD_H", "B:U542.3=ZBB_RST_H", "B:U541.1=ZBA_BSL_H", "B:U541.3=ZBB_BSL_H",
    "B:U541.5=+3V3_DEV", "B:U203.2=+5V_S2", "B:U214.1=WL_nDIS2_OFF", "B:U214.3=BT_nDIS2_OFF", "B:U214.6=WL_nDIS2",
    "B:U214.4=BT_nDIS2", "B:U314.1=WL_nDIS3_OFF", "B:U314.3=BT_nDIS3_OFF", "B:U314.6=WL_nDIS3", "B:U314.4=BT_nDIS3",
    "B:U103.3=S1A_EN", "B:U303.3=S3A_EN", "B:U11~LG290P", "B:U11.23=+3V3_DEV", "B:J_QMX.1=VBUS_QMX", "B:F3.1=+5V_DEV", "B:F3.2=VBUS_QMX",
    "A:U36.4=PA_EN", "A:R58.1=PA_EN", "A:R58.2=PA_UVLO", "A:U13~+13V8_PA", "A:R124.1=HF_EN", "A:R124.2=HF_UVLO",
    "A:U15~+12V_HF", "A:U40.6=PA_HOLD", "A:U40.4=HF_HOLD", "D:U2~SA868", "D:U2.8=+5V_SA", "D:FB1.2=+5V_SA",
    "D:FB1.1=+5V_TX", "D:U21.1=+5V_TX", "D:U21.5=TXSUP_EN", "D:U15.4=PA_KEY", "D:U15.1=VGG_SW",
    "SHA:A=6c40250c47195ebb", "SHA:B=3ef9b8c49a01b728", "SHA:C=c9f7394594201045", "SHA:D=a2d48972d171aad1"]
HOTR1 = ["E:Q11~2N7002", "E:Q11.1=HOT_R1_G", "E:Q11.3=BLK_SPARE", "E:U10.30=HOT_R1_G", "E:R58.1=HOT_R1_G", "E:R58.2=GND",
         "E:J_BLK.12=BLK_SPARE", "A:J_DOCK.12=DOCK_SPARE", "A:R216.1=DOCK_SPARE", "A:R216.2=+3V3", "A:U27.18=DOCK_SPARE",
         "A:U27@IO1_5=DOCK_SPARE", "REG:REQ-077.evidence_result=INCONCLUSIVE", "REG:REQ-077.waits_on~S-58"]
TXLAMP = ["C:D3.2=TX_A", "C:R36.2=TX_A", "C:R36.1=LED_RAIL", "C:Q1.3=LED_RAIL", "C:Q1.1=Q1_G", "C:R17.2=Q1_G",
          "C:R17.1=LED_RAIL_SW", "C:Q2.1=Q2_G", "C:R19.1=PANEL_PWM", "C:R19.2=Q2_G", "C:R20.2=GND", "C:U3@GPIO8=PANEL_PWM",
          "C:D22.1=EMCLAMP_K", "C:R47.1=LED_RAIL_SW", "C:Q7.3=EMCLAMP_K", "C:U14.3=TX_INHIBIT_n", "C:U14.6=EMCON_HW"]
DEVRAIL = ["A:U7~LM5176", "A:U7.12=+5V_DEV", "B:U25~AP63203", "B:U25.2=+5V_DEV", "B:U25.5=DEV_SW", "B:L1.1=DEV_SW",
           "B:L1.2=+3V3_DEV", "A:!~AP63203"]
DEVLOSS = ["B:U112.4=EMCON_ON1", "B:U112.5=+3V3_CM1", "B:U212.5=+3V3_CM2", "B:U312.5=+3V3_CM3", "B:U113.5=+3V3_CM1",
           "B:U213.5=+3V3_CM2", "B:U313.5=+3V3_CM3", "B:U543.1=RB_IEN", "B:U543.5=+3V3_DEV", "B:U543.6=+5V_DEV",
           "B:!U111", "B:!U211", "B:!U311",
           "DOC:v2/docs/feasibility/EMCON.md~CLOSED at desk on board B's round 8 (section 4b)"]
LINES = ["G@e57a7365:gen_sch_a.py:1104~R42", "G@e57a7365:gen_sch_a.py:338-339~R2|R184|R4",
         "G@e57a7365:gen_sch_a.py:1598~R103|R104", "G@e57a7365:gen_sch_a.py:1611~R111",
         "G@e57a7365:gen_sch_a.py:1340~U21", "G@e57a7365:gen_sch_a.py:1372~U22", "G@e57a7365:gen_sch_a.py:972~R26|R27",
         "G@e57a7365:gen_sch_a.py:1306~J_USBC_OUT", "G@e57a7365:gen_sch_a.py:1668~J_USBW",
         "G@e57a7365:gen_sch_e.py:796~J_TAMP"]


def moved_emcon():
    """Section 0a.1 of EMCON.md: the text 7a9f7b5b put in CONOPS 4b and its EMCON row, with EMCON.md's self references
    written as section numbers."""
    t = C12.SEC4B
    i = t.index('"Asserted" means')
    j = t.index("\n| Radio |")
    pre, table = t[i:j].strip(), t[j:].strip()
    def selfref(x):
        x = x.replace("`feasibility/EMCON.md` sections", "sections").replace("`feasibility/EMCON.md` section", "section")
        return x.replace("EMCON.md sections", "sections").replace("EMCON.md section", "section")
    return (
        "### 0a.1 What EMCON does to each radio, as generated (kept here since 29 September 2026)\n\n"
        "`CONOPS.md` is a baselined definition: by the rule its head states and `../handover/DEFINITION-STATUS.md` keeps, a\n"
        "circuit correction goes to this page and the records the status page names, not to the baseline. On 29 September\n"
        "2026 stream s122 restored `CONOPS.md` to its text at `c5430071`, withdrawing the circuit rewrite of its section 4b\n"
        "and of section 4's EMCON row that set 12 had made (`a46db71b`, `7a9f7b5b`). That rewrite, as `7a9f7b5b` committed\n"
        "it, is kept below, read on the committed netlists of integration set 13 (board A `6c40250c47195ebb`, board B\n"
        "`3ef9b8c49a01b728`, board C `c9f7394594201045`, board D `a2d48972d171aad1`). `v2/docs/records/s122/apply_docs_s122_r2.py`\n"
        "asserted, before writing it, every pin, value and net its rows name on those netlists (its list `EMCON_A`: the 146\n"
        "pin assignments of `v2/docs/records/int13/apply_conops_4b_set12.py` and the parts that script did not assert, among\n"
        "them `U9`, `R52` and `D23`'s pins, `U214` and `U314`, `U22` to `U24`, the source of `LIME_HW_EN`, the inputs of `U540`\n"
        "to `U542` and `U547` to `U550`, and the supplies the rows call not gated), and `v2/docs/records/s122/verdicts.py`\n"
        "judges each sentence again. The receive column and the module behaviour in the removal column rest on the makers'\n"
        "documents and sections 4.4, 4b and 4c, not on the netlists.\n\n"
        + selfref(pre) + "\n\n" + selfref(table) + "\n\n"
        "**Section 4's EMCON row of `CONOPS.md`, as generated (the cells `7a9f7b5b` wrote).** What is off or held: "
        + selfref(C12.CELL4) + ". Hardware or software: " + selfref(C12.CELL5) + ". What is owed: " + selfref(C12.CELL8)
        + "\n\n")


def status_section():
    return (
        "## %s\n\n" % L.STATUS_KEY +
        "`CONOPS.md` is restored to its text at `c5430071` (the owner's rulings of 28 September, the last change the rule\n"
        "above allows; stream s122 withdrew set 12's circuit edits `a46db71b` and `7a9f7b5b` and its own round 1), and its\n"
        "circuit statements are read through this page (CFL-016 and S-122 of the requirements registry). A statement of\n"
        "`CONOPS.md` about the circuit, and a figure, a commit, a generator line or an \"as generated\" remark inside it, is its\n"
        "value when the document was baselined or last reopened. Where the committed netlists now differ, or where the value\n"
        "is a line number of a generator that has since moved, the current value is kept where the row below says, and that\n"
        "place is judged against the netlists by `v2/docs/records/s122/verdicts.py`. Read on the committed netlists of\n"
        "integration set 13: board A `6c40250c47195ebb`, B `3ef9b8c49a01b728`, C `c9f7394594201045`, D `a2d48972d171aad1`, E\n"
        "`2ed95a0e8069ebf8`.\n\n"
        "| Row | `CONOPS.md` passage | The current value | Where it is kept |\n|---|---|---|---|\n"
        "| DC-01 | section 4's EMCON row; section 4b's preamble and table | what EMCON drives and removes, radio by radio, "
        "as set 12 draws it and set 13 keeps it: the RockBLOCK's ENABLE forced low in hardware (`U536`, `U543`), the "
        "back-feed gates of the RockBLOCK, the E22 and the E72 (`U537` to `U553`), the card bucks' enables from `U116`, "
        "`U216` and `U316`, and board A's PA and HF gates `U35` to `U38` | `feasibility/EMCON.md` section 0a.1; FEA-002, "
        "REQ-030 and REQ-071 in the registry |\n"
        "| DC-02 | section 4's Heat stage and Hot stop rows; section 4c's HOT-R1 passages; section 4f's row of the pack's "
        "safety | HOT-R1 is drawn on boards A and E since stream w4ae: board E's `Q11` (2N7002), its gate on `HOT_R1_G` "
        "from `U10` pin 30 and held off by `R58`, pulls the dock line `BLK_SPARE` at `J_BLK` pin 12; board A reads it as "
        "`DOCK_SPARE` at `J_DOCK` pin 12, pulled up by `R216`, on `U27` pin 18 (IO1_5); REQ-077 reads INCONCLUSIVE and "
        "waits on S-58 | REQ-077 in the registry |\n"
        "| DC-03 | section 4e, the panel controller lost | EMCON and MAIN PWR act without the panel controller, and so does "
        "the EMCON lamp `D22`, fed from `LED_RAIL_SW` through `R47`; the TX lamp `D3` does not: its feed `LED_RAIL` is "
        "`Q1`'s drain, which only `Q2` turns on, from `PANEL_PWM` (GPIO 8) | `PANEL.md` sections 1 and 4; "
        "`feasibility/EMCON.md` section 8 |\n"
        "| DC-04 | section 4e, a device rail lost | `+5V_DEV` is made by board A's `U7` (LM5176) and `+3V3_DEV` by board "
        "B's `U25` (AP63203) from `+5V_DEV` | this row; `V2-SPEC.md` correction 32 |\n"
        "| DC-05 | section 4e, a device rail lost, what the loss releases | a loss of `+3V3_DEV` releases no module radio: "
        "each slot makes `EMCON_ON1..3` from its own 3.3 V (`U112`, `U212`, `U312`; EMCON.md L3, closed at desk in board "
        "B's round 8), and `U543`, run from `+5V_DEV`, holds the RockBLOCK's ENABLE (`RB_IEN`) low while `+3V3_DEV` is "
        "below its threshold | `feasibility/EMCON.md` sections 0a.1 and 7 |\n"
        "| DC-06 | every generator or tool line number the definition cites (sections 4, 4c and 4e among them) | the "
        "line of the commit the citation names, or, undated, of the commit its passage was written at; where stream s122 "
        "read the parts at `e57a7365`: `R42` at `gen_sch_a.py:1104`, `R2`, `R184` and `R4` at 338 to 339, `R103` and "
        "`R104` at 1598, `R111` at 1611, `U21` at 1340, `U22` at 1372, `R26` and `R27` at 972, `J_USBC_OUT` at 1306, "
        "`J_USBW` at 1668, and `J_TAMP` at `gen_sch_e.py:796` | the generators at the commit read; "
        "`v2/docs/records/s122/verdicts.out` |\n\n")


STATUS_ROW = ("| CONOPS's circuit passages whose values differ from the committed netlists (EMCON, HOT-R1, the TX lamp, the "
              "device rails, generator line numbers) | the section \"%s\" below | `CONOPS.md` sections 4, 4b, 4c, 4e and "
              "4f |\n" % L.STATUS_KEY)

EDITS = [
    {"doc": "v2/docs/PANEL.md", "why": "section 3, GPIO 2 and 3: set 13 puts U3's pins on EPD_SCL_R and EPD_SDA_R through R53 and R54 (S-122, set 13)",
     "old": "| 2, 3 | EPD_SCL, EPD_SDA | e-paper SPI (the iTC's 4-wire mode; MOSI only, the display's read path is unused) |",
     "new": "| 2, 3 | EPD_SCL_R, EPD_SDA_R | e-paper SPI (the iTC's 4-wire mode; MOSI only, the display's read path is unused), each "
            "through its 27 Ohm series resistor (`R53`, `R54`, since set 13) to `EPD_SCL` and `EPD_SDA` at `J_EPD` |",
     "a": ["C:U3@GPIO2=EPD_SCL_R", "C:U3@GPIO3=EPD_SDA_R", "C:R53~27R", "C:R53.1=EPD_SCL_R", "C:R53.2=EPD_SCL",
           "C:R54~27R", "C:R54.1=EPD_SDA_R", "C:R54.2=EPD_SDA", "C:J_EPD.13=EPD_SCL", "C:J_EPD.14=EPD_SDA"]},
    {"doc": "v2/docs/PANEL.md", "why": "section 3, GPIO 4 to 7: set 13 puts U3's pins for DC and CS on EPD_DC_R and EPD_CS_R through R55 and R56",
     "old": "| 4, 5, 6, 7 | EPD_DC, EPD_CS, EPD_RST, EPD_BUSY | e-paper control; BUSY is high while the display refreshes |",
     "new": "| 4, 5, 6, 7 | EPD_DC_R, EPD_CS_R, EPD_RST, EPD_BUSY | e-paper control, DC and CS each through its 27 Ohm series "
            "resistor (`R55`, `R56`, since set 13) to `EPD_DC` and `EPD_CS` at `J_EPD`; BUSY is high while the display refreshes |",
     "a": ["C:U3@GPIO4=EPD_DC_R", "C:U3@GPIO5=EPD_CS_R", "C:U3@GPIO6=EPD_RST", "C:U3@GPIO7=EPD_BUSY", "C:R55~27R",
           "C:R55.1=EPD_DC_R", "C:R55.2=EPD_DC", "C:R56~27R", "C:R56.1=EPD_CS_R", "C:R56.2=EPD_CS", "C:J_EPD.11=EPD_DC",
           "C:J_EPD.12=EPD_CS"]},
    {"doc": "v2/docs/PANEL.md", "why": "section 6 (m6): MISO is not gated by LORA_GO; it reaches the host through U553",
     "old": "the E22's TXEN, RXEN, NRST and SPI lines only while `LORA_GO` (`U544` to `U550`),",
     "new": "the E22's TXEN, RXEN, NRST, MOSI, SCK and NSS only while `LORA_GO` (`U544` to `U550`), its MISO reaching the host "
            "through the buffer `U553`,",
     "a": ["B:U544.4=LORA_GO", "B:U545.2=LORA_GO", "B:U546.2=LORA_GO", "B:U547.2=LORA_GO", "B:U548.2=LORA_GO",
           "B:U548.4=LORA_MOSI", "B:U549.4=LORA_SCLK", "B:U550.4=LORA_NSS", "B:U553~74LVC1G34", "B:U553.2=LORA_MISO",
           "B:U553.4=SPI3_MISO", "B:LORA_MISO>U12,U553"]},
    {"doc": "v2/docs/PANEL.md", "why": "section 7: the provenance named set 12's netlists; board C changed at set 13",
     "old": "re-read on 29 September 2026 against the netlists of integration set 12 (A `6c40250c47195ebb`, B "
            "`3ef9b8c49a01b728`, C `87b69472ac83ca5a`, D `a2d48972d171aad1`)",
     "new": "re-read on 29 September 2026 against the netlists of integration set 13 (A `6c40250c47195ebb`, B "
            "`3ef9b8c49a01b728`, C `c9f7394594201045`, D `a2d48972d171aad1`)",
     "a": ["SHA:A=6c40250c47195ebb", "SHA:B=3ef9b8c49a01b728", "SHA:C=c9f7394594201045", "SHA:D=a2d48972d171aad1",
           "C:SDA>U_LIGHT,U1,U2,U3"]},
    {"doc": "v2/docs/OPERATING-ENVELOPE.md", "why": "section 4 (m2): round 1 dropped the PA bias, which the EMCON lines do gate (board D's U15 on PA_KEY)",
     "old": "EMCON (a hardware line on every transmitter; what it removes is set out below)",
     "new": "EMCON (a hardware line on every transmitter and on the PA's rail and bias; what it removes is set out below)",
     "a": ["D:U15~PA gate bias", "D:U15.4=PA_KEY", "D:U14.4=PA_KEY", "D:U14.1=KEY", "D:U12.2=TX_INHIBIT_n", "A:U36.4=PA_EN",
           "A:U35.1=TX_INHIBIT_n", "A:U35.2=EMCON_HW"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 2, build step 4 (B2): board A carries seventeen Mill-Max 0858 class pins since EQ-16",
     "old": "A22 with the Preci-Dip 813-S1-012-10-016101 connector and the nine Mill-Max 0858 class power pins soldered in",
     "new": "A22 with the Preci-Dip 813-S1-012-10-016101 connector and the seventeen Mill-Max 0858 class power pins (nine for "
            "the pack, `J_CP1` to `J_CP4`, `J_CN1` to `J_CN4` and `J_PRE1`, and since EQ-16 eight for the input, `J_VR1` to "
            "`J_VR4` and `J_VN1` to `J_VN4`) soldered in",
     "a": ["A:#fp~Mill-Max_0858=17", "A:#ref~J_CP=4", "A:#ref~J_CN=4", "A:J_PRE1?", "A:#ref~J_VR=4", "A:#ref~J_VN=4",
           "A:J_VR1.1=VIN_RAW", "A:J_VN1.1=GND", "A:J_DOCK~Preci-Dip 813-S1-012-10-016101"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 4 (m5): the dock paragraph names VIN_RAW's pins but not their returns",
     "old": "on four 9 A spring pins of its own, `J_VR1` to `J_VR4`, since EQ-16",
     "new": "on four 9 A spring pins of its own, `J_VR1` to `J_VR4`, with its return on four more, `J_VN1` to `J_VN4`, since EQ-16",
     "a": ["A:#ref~J_VR=4", "A:#ref~J_VN=4", "A:J_VR1.1=VIN_RAW", "A:J_VN1.1=GND", "A:J_VN4.1=GND", "A:J_VR1~9 A",
           "A:J_VN1~9 A"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 8 step 3 (m4): the short citation carried no commit",
     "old": "(`:1597-1598`)",
     "new": "(`:1597-1598` at `e57a7365`)",
     "a": ["G@e57a7365:gen_sch_a.py:1597-1598~R102|R145"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 9, A22 (B2): seventeen Mill-Max 0858 class pins",
     "old": "- A22: the Preci-Dip 813-S1-012-10-016101 spring connector and the nine Mill-Max 0858 class power pins on the underside",
     "new": "- A22: the Preci-Dip 813-S1-012-10-016101 spring connector and the seventeen Mill-Max 0858 class power pins on the "
            "underside (nine for the pack and, since EQ-16, eight for the input, section 4)",
     "a": ["A:#fp~Mill-Max_0858=17", "A:#ref~J_BM=11", "A:J_BM1~R222M00720", "A:F1~Keystone 3568"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 9, B16 (B2): two WiFi link cards in J_M2C1 and J_M2C3",
     "old": "the three coolers with their fan leads, the WiFi link card, the 5G module",
     "new": "the three coolers with their fan leads, the two WiFi link cards (`J_M2C1`, `J_M2C3`), the 5G module",
     "a": ["B:#val~M.2 E-key=2", "B:J_M2C1~M.2 E-key", "B:J_M2C3~M.2 E-key", "B:#ref~J_FAN=3", "B:#val~M.2 M-key=3",
           "B:J_M2C2~2199119"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 9, C7 (B2): seventeen 3 mm LEDs, the seventeenth the hardware EMCON lamp D22",
     "old": "the sixteen 3 mm LEDs standing on the top face",
     "new": "the seventeen 3 mm LEDs (`D1` to `D16` and, since board C's round 8, the hardware EMCON lamp `D22`) standing on the top face",
     "a": ["C:#fp~LED_D3.0mm=17", "C:D22~EMCON", "C:D16?", "C:#val~C&K=3", "C:#val~APEM=3", "C:#ref~J_HSJ=2",
           "C:SW_LIGHT~NKK"]},
    {"doc": "v2/docs/V2-SPEC.md", "why": "line 30: the switch chip generated is the seven-port KSZ9897R, not a five-port part",
     "old": "joined by a five-port Gigabit switch chip with the sealed wall port and a spare header",
     "new": "joined by a Gigabit switch chip, the seven-port KSZ9897R (`U1` on B16; correction 32), with the sealed wall port "
            "and a spare header",
     "a": ["B:U1~KSZ9897", "B:U1~seven-port Gigabit", "B:SDA>U1"]},
    {"doc": "v2/docs/V2-SPEC.md", "why": "line 81 (m7): the TPS55288 had left the design before the 7 September generation",
     "old": "the 45 W USB-C outlet (TPS25740 and TPS55288)",
     "new": "the 45 W USB-C outlet (TPS25740A and an LM5176 stage; the TPS55288 had left the design on 7 September, correction 32)",
     "a": ["A:U18~TPS25740A", "A:U19~LM5176", "A:!~TPS55288", "G@c5de605d:gen_sch_a.py:267~TPS55288|left the design"]},
    {"doc": "v2/docs/V2-SPEC.md", "why": "line 82 (m7): the schematic text reads H743 and CON-017 reads PASS",
     "old": "three STM32H753 supervisors (the part bought is the STM32H743, which the owner accepted under D-13; the mismatch "
            "closes only when the schematic text and the BOM say H743 and regeneration parity has been shown again, correction 14)",
     "new": "three STM32H743 supervisors (the part bought, which the owner accepted under D-13; the schematic text of `U41`, "
            "`U51` and `U61` reads H743 and CON-017 reads PASS in the requirements registry, corrections 14 and 32)",
     "a": ["B:U41~STM32H743", "B:U51~STM32H743", "B:U61~STM32H743", "B:!~STM32H753", "B:#val~STM32H743=3",
           "REG:CON-017.evidence_result=PASS"]},
    {"doc": "v2/docs/V2-SPEC.md", "why": "line 3 (m8): the corrections lists include the 29 September one",
     "old": "listed under \"Corrections, 26 September 2026\" and \"Corrections, 27 September 2026\" at the end",
     "new": "listed under \"Corrections, 26 September 2026\", \"Corrections, 27 September 2026\" and \"Corrections, 29 September "
            "2026\" at the end",
     "a": []},
    {"doc": "v2/docs/V2-SPEC.md", "why": "correction 32 (m8): its own dated heading; lines 30, 81 and 82 added",
     "old": "32. **Set 12 (lines 35, 73 and 76, correction 29).** Session reading of stream s122 (29 September 2026,\n"
            "    MESHSAT-1357, open item S-122) against the committed netlists of integration set 12\n"
            "    (`v2/docs/records/s122/verdicts.out`). Line 76 listed the",
     "new": "## Corrections, 29 September 2026\n\n"
            "Stream s122 (MESHSAT-1357, open item S-122) read the lines above against the committed netlists of integration sets\n"
            "12 and 13 (`v2/docs/records/s122/verdicts.out`); nothing is built.\n\n"
            "32. **Sets 12 and 13 (lines 30, 35, 73, 76, 81 and 82, correction 29).** Session reading of stream s122 (29 September\n"
            "    2026, MESHSAT-1357, open item S-122) against the committed netlists of integration sets 12 and 13\n"
            "    (`v2/docs/records/s122/verdicts.out`). Line 30 named a five-port switch chip; the chip generated is the\n"
            "    seven-port KSZ9897R (`U1` on B16). Line 81 named the TPS55288, which had left the design before the 7\n"
            "    September generation (`gen_sch_a.py` line 267 at `c5de605d`); the USB-C outlet is the TPS25740A with an LM5176\n"
            "    stage. Line 82's closing condition for the supervisors is met: the schematic text of `U41`, `U51` and `U61`\n"
            "    reads STM32H743 and CON-017 reads PASS. Line 76 listed the",
     "a": ["B:U1~seven-port Gigabit", "G@c5de605d:gen_sch_a.py:267~TPS55288", "A:U18~TPS25740A", "A:U19~LM5176",
           "B:#val~STM32H743=3", "REG:CON-017.evidence_result=PASS"]},
]


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    sys.exit(2)


def pattern(old):
    return re.compile(r"\s+".join(re.escape(w) for w in old.split()))


def needs_table(txt):
    i = txt.index("## 2. Needs")
    return txt[i:txt.index("### 2a.", i)]


def main():
    check = "--check" in sys.argv
    nls = L.netlists()
    for k, s in NETS.items():
        if nls[k]["sha16"] != s: refuse("board %s's netlist is %s, not set 13's %s" % (k, nls[k]["sha16"], s))
    head = subprocess.run(["git", "-C", L.TOP, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
    base_con = subprocess.run(["git", "-C", L.TOP, "show", "%s:%s" % (BASE, CON)], capture_output=True, check=True).stdout
    c543 = subprocess.run(["git", "-C", L.TOP, "show", "c5430071:%s" % CON], capture_output=True, check=True).stdout
    cur_con = open(os.path.join(L.TOP, CON), "rb").read()
    if cur_con not in (base_con, c543): refuse("CONOPS.md is neither the base's nor c5430071's")
    for rel, s in DOCS.items():
        if s and L.sha16(rel) != s: refuse("%s is %s, not the file this script corrects (%s): already applied, or changed" % (rel, L.sha16(rel), s))
    if L.STATUS_KEY in open(os.path.join(L.TOP, DST), encoding="utf-8").read(): refuse("the status page already carries the section")
    # 1. what 7a9f7b5b committed is what the moved text says
    at7a = subprocess.run(["git", "-C", L.TOP, "show", "7a9f7b5b:%s" % CON], capture_output=True, text=True, check=True).stdout
    if C12.SEC4B not in at7a: refuse("apply_conops_4b_set12.SEC4B is not what 7a9f7b5b committed")
    for cell in (C12.CELL4, C12.CELL5, C12.CELL8):
        if cell not in at7a: refuse("an EMCON cell is not what 7a9f7b5b committed")
    if needs_table(c543.decode("utf-8")) != needs_table(base_con.decode("utf-8")): refuse("the needs table differs")
    n = 0
    groups = [("the moved EMCON text", EMCON_A), ("HOT-R1", HOTR1), ("the TX lamp", TXLAMP), ("the device rails", DEVRAIL),
              ("the +3V3_DEV loss", DEVLOSS), ("the generator lines", LINES)] + [(e["why"], e["a"]) for e in EDITS]
    for what, al in groups:
        for a in al:
            ok, msg = V.run_assert(a, nls)
            if not ok: refuse("%s: assertion fails: %s" % (what, msg))
            n += 1
    em = moved_emcon()
    st = status_section()
    for txt in [em, st, STATUS_ROW] + [e["new"] for e in EDITS]:
        if any(d in txt for d in L.DASHES): refuse("a dash in the new text")
    # the edits of the correctable documents
    texts = {rel: open(os.path.join(L.TOP, rel), encoding="utf-8").read() for rel in DOCS}
    for e in EDITS:
        hits = list(pattern(e["old"]).finditer(texts[e["doc"]]))
        if len(hits) != 1: refuse("%s: the old passage is found %d times" % (e["why"], len(hits)))
        new = e["new"] if "\n" in e["old"] else " ".join(e["new"].split("\n"))
        texts[e["doc"]] = texts[e["doc"]][:hits[0].start()] + new + texts[e["doc"]][hits[0].end():]
    for e in EDITS:
        if len(list(pattern(e["new"]).finditer(texts[e["doc"]]))) != 1: refuse("%s: the new passage does not read back once" % e["why"])
    t = texts[EMC]
    k = t.index("\n## 1. Evidence base\n")
    texts[EMC] = t[:k + 1] + em + t[k + 1:]
    t = texts[DST]
    row_at = t.index("| Each layer of the handover and its reviews |")
    row_end = t.index("\n", row_at) + 1
    t = t[:row_end] + STATUS_ROW + t[row_end:]
    k = t.index("## What the two documents carried at their baselines")
    texts[DST] = t[:k] + st + t[k:]
    if check:
        print("%s: --check: %d edits located, CONOPS restorable, %d assertions hold on set 13's netlists; nothing written" % (TAG, len(EDITS), n))
        return 0
    open(os.path.join(L.TOP, CON), "wb").write(c543)
    if open(os.path.join(L.TOP, CON), "rb").read() != c543: refuse("CONOPS.md does not equal c5430071's")
    for rel, txt in texts.items():
        open(os.path.join(L.TOP, rel), "w", encoding="utf-8").write(txt)
        L.md_blocks(rel)
    print("%s: at %s CONOPS.md restored to c5430071 (%s, byte for byte, needs table unchanged); %d passages corrected; "
          "EMCON.md section 0a.1 and the status page's section written; %d assertions held first; %s" % (
              TAG, head, hashlib.sha256(c543).hexdigest()[:16], len(EDITS), n,
              ", ".join("%s to %s" % (os.path.basename(r), L.sha16(r)) for r in DOCS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
