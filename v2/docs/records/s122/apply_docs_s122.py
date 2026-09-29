#!/usr/bin/env python3
"""Step 3 of stream s122 (S-122, MESHSAT-1357, 29 September 2026): correct every sentence that `verdicts.py` judged STALE
in the documents CFL-016 names, from the committed netlists of integration set 12 and the generators at the base
`e57a7365`.

Before it writes anything the script:
  1. checks that each document and each netlist is the file stream s122 read (sha256/16 at the base);
  2. ASSERTS, on the parsed netlists (`tx_inhibit.parse_netlist`) and on the generators, every part, pin, net and
     generator line the new text names (`EDITS[...]["a"]`, the same assertion language as `verdicts.py`), and refuses
     on the first that does not hold;
  3. finds each old passage exactly once (whitespace between words may be a line break in a wrapped paragraph), and
     checks the new text differs and carries no dash character.
It then writes each document, re-parses it with `s122lib.md_blocks`, checks that every new passage is present once and
every old one is gone, and that the diff against the base touches no line outside the corrected passages. It refuses a
second run (an old passage no longer found). It changes documents only: no generator, netlist or registry.

Run: python3 apply_docs_s122.py [--check]   (--check asserts and locates everything, writes nothing)."""
import os, re, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import verdicts as V  # noqa: E402

TAG = "apply_docs_s122"
BASE = "e57a7365"
DOCS = {"v2/docs/PANEL.md": "4647782f5aca7c13", "v2/docs/CONOPS.md": "3c5d49078ba6dbfd",
        "v2/docs/V2-SPEC.md": "e1fdcebe8638e471", "v2/docs/OPERATING-ENVELOPE.md": "43361b02743cf3af",
        "v2/docs/TEST-PLAN.md": "ae57da0b57e214f7", "v2/docs/ASSEMBLY.md": "ee4eff52fc5df307"}
NETS = {"A": "6c40250c47195ebb", "B": "3ef9b8c49a01b728", "C": "87b69472ac83ca5a", "D": "a2d48972d171aad1",
        "E": "2ed95a0e8069ebf8", "P": "20c7b0795593d761"}

# Common assertion groups
A_BOARD_A_GATES = ["A:U35~SN74AUP1G08", "A:U35.1=TX_INHIBIT_n", "A:U35.2=EMCON_HW", "A:U35.4=PA_TXOK", "A:U35.5=+3V3_EMCON",
                   "A:U36~SN74AUP1G08", "A:U36.1=PA_TXOK", "A:U36.2=PA_HOLD", "A:U36.4=PA_EN", "A:U36.5=+3V3_EMCON",
                   "A:U37~SN74AUP1G08", "A:U37.1=TX_INHIBIT_n", "A:U37.2=EMCON_HW", "A:U37.4=HF_TXOK", "A:U37.5=+3V3_EMCON",
                   "A:U38~SN74AUP1G08", "A:U38.1=HF_TXOK", "A:U38.2=HF_HOLD", "A:U38.4=HF_EN", "A:U38.5=+3V3_EMCON",
                   "G@e57a7365:gen_sch_a.py:1572-1575~U35|U36|U37|U38"]
A_C_CLAMP = ["C:U9~74LVC1G17", "C:U9.2=TX_INHIBIT_n", "C:U9.4=EMCON_HW_DRV", "C:R52~330R", "C:R52.1=EMCON_HW_DRV",
             "C:R52.2=EMCON_HW", "C:D23~BAT46W", "C:D23.1=TX_INHIBIT_n", "C:D23.2=EMCON_HW"]
A_RB = ["B:U536~SN74LVC1G08", "B:U536.1=EMCON_HW", "B:U536.2=RB_SW_IEN", "B:U536.4=RB_IEN_DRV", "B:R532.1=RB_IEN_DRV",
        "B:R532.2=RB_IEN", "B:J_RB9704.3=RB_IEN", "B:U543~TPS3808G30", "B:U543.1=RB_IEN", "B:U543.5=+3V3_DEV",
        "B:U543.6=+5V_DEV"]
A_BACKFEED = ["B:U537.1=RB_IEN", "B:U537.2=RB_STATUS", "B:U537.4=RB_GO", "B:U538.2=RB_GO", "B:U539.2=RB_GO",
              "B:U538.4=RB_RXD", "B:U539.4=RB_CTRL", "B:U544.2=E22_EN", "B:U544.4=LORA_GO", "B:U545.2=LORA_GO",
              "B:U546.2=LORA_GO", "B:U547.2=LORA_GO", "B:U548.2=LORA_GO", "B:U549.2=LORA_GO", "B:U550.2=LORA_GO",
              "B:U540~SN74LVC2G07", "B:U541~SN74LVC2G07", "B:U542~SN74LVC2G07", "B:U540.6=ZBA_RXD", "B:U542.6=ZBB_RXD",
              "B:R536?", "B:R537?", "B:+3V3_ZB>R536,R537,U22"]
A_HOTR1 = ["E:Q11.1=HOT_R1_G", "E:Q11.3=BLK_SPARE", "E:J_BLK.12=BLK_SPARE", "A:J_DOCK.12=DOCK_SPARE",
           "A:U27@IO1_5=DOCK_SPARE", "A:R216.1=DOCK_SPARE", "A:R216.2=+3V3"]

EDITS = [
    # ---------------------------------------------------------------- PANEL.md
    {"doc": "v2/docs/PANEL.md", "why": "section 1, EMCON logic: an undated citation of lines that now hold decoupling notes, and R52 and D23 omitted",
     "old": "far outside the 74LVC1G34's input slew limit, `gen_sch_c.py:157-166`).",
     "new": "far outside the 74LVC1G34's input slew limit, `gen_sch_c.py:157-166` at `45bde541`). Since set 12 (stream d4emcon, "
            "finding D4E-F1) `U9` drives the line through `R52` (330 Ohm) and `D23` (BAT46W) clamps `EMCON_HW` to `TX_INHIBIT_n`, "
            "so `EMCON_HW` still follows `TX_INHIBIT_n`.",
     "a": A_C_CLAMP + ["G@45bde541:gen_sch_c.py:157-166~U9"]},
    {"doc": "v2/docs/PANEL.md", "why": "section 3, GPIO 20: the charge inhibit is section 10, not section 9",
     "old": "| 20 | SHORE_INHIBIT | charge inhibit to A22 and the dock, section 9 |",
     "new": "| 20 | SHORE_INHIBIT | charge inhibit to A22 and the dock, section 10 |",
     "a": ["C:U3@GPIO20=SHORE_INHIBIT", "A:J_DOCK.8=SHORE_INHIBIT", "DOC:v2/docs/PANEL.md~## 10. Shore charge inhibit and the pack"]},
    {"doc": "v2/docs/PANEL.md", "why": "section 6, TX_INHIBIT_n: board A's round 8 called a candidate, a citation of lines that hold other code, and U36 and U38 left out",
     "old": "since board A's round 8 candidate (26 September 2026) A22 also reads it, ANDed with `EMCON_HW` into the enables of the PA "
            "and HF converters (`U35`, `U37`, SN74AUP1G08, `gen_sch_a.py:1240-1243`), so those two rails",
     "new": "since board A's round 8 (26 September 2026) A22 also reads it, ANDed with `EMCON_HW` in `U35` and `U37` (SN74AUP1G08, "
            "on their own supply `+3V3_EMCON`) and then with the software holds `PA_HOLD` and `HF_HOLD` in `U36` and `U38` into "
            "the enables of the PA and HF converters (`gen_sch_a.py:1572-1575` at `e57a7365`), so those two rails",
     "a": A_BOARD_A_GATES},
    {"doc": "v2/docs/PANEL.md", "why": "section 6, EMCON_HW source: board A's round 8 called a candidate, and R52 and D23 omitted",
     "old": "`U9` buffer, low while TX_INHIBIT_n is low; with the ribbon out B16's `R58` (4.7 k 1 percent since board B's round 8; "
            "10k before) and A22's `R102` (10k 1% since board A's round 8 candidate; 100k before) hold it low",
     "new": "`U9` buffer, through `R52` with `D23` clamping it to `TX_INHIBIT_n` since set 12, low while TX_INHIBIT_n is low; with "
            "the ribbon out B16's `R58` (4.7 k 1 percent since board B's round 8; 10k before) and A22's `R102` (10k 1% since "
            "board A's round 8; 100k before) hold it low",
     "a": A_C_CLAMP + ["B:R58~4.7k 1%", "B:R58.1=EMCON_HW", "B:R58.2=GND", "A:R102~10k 1%", "A:R102.1=EMCON_HW", "A:R102.2=GND"]},
    {"doc": "v2/docs/PANEL.md", "why": "section 6, EMCON_HW effect: board A as generated at 45bde541 (U26) and a round 8 candidate, where U35 to U38 are generated",
     "old": "as generated at `45bde541` on A22 it is ANDed into the enables of the PA and HF converters (`U26`, `gen_sch_a.py:1102`), "
            "and in board A's round 8 candidate it is the second input of `U35` and `U37`, beside `TX_INHIBIT_n` (`gen_sch_a.py:1240-1243`);",
     "new": "on A22 it is the second input of `U35` and `U37`, beside `TX_INHIBIT_n`, whose outputs `U36` and `U38` AND with the "
            "software holds into the enables of the PA and HF converters (since board A's round 8, `gen_sch_a.py:1572-1575` at "
            "`e57a7365`; at `45bde541` it was ANDed in `U26`, `gen_sch_a.py:1102`, which is now the outlet interlock alone);",
     "a": A_BOARD_A_GATES + ["G@45bde541:gen_sch_a.py:1102~U26|EMCON gates", "A:U26~outlet interlock", "A:U26.9=POE_SW_EN",
                             "A:U26.12=PD_SW_EN", "A:U26.8=POE_EN", "A:U26.11=PD_EN"]},
    {"doc": "v2/docs/PANEL.md", "why": "section 6, EMCON_HW effect: the RockBLOCK's ENABLE without set 12's R532, U543 and RB_GO gates",
     "old": "so no firmware holds the module enabled on its capacitors (stream w4b);",
     "new": "so no firmware holds the module enabled on its capacitors (stream w4b; since set 12 through `R532`, with `U543` holding "
            "`RB_IEN` low while `+3V3_DEV` is below 2.79 V, and the module's logic inputs passed only while `RB_GO`, `U537` to "
            "`U539`);",
     "a": A_RB + ["B:U537.4=RB_GO", "B:U538.2=RB_GO", "B:U539.2=RB_GO"]},
    {"doc": "v2/docs/PANEL.md", "why": "section 6, EMCON_HW effect: the back-feed of SD-EMC-2 listed as open, which set 12 draws",
     "old": "Open: the back-feed of SD-EMC-2 into the RockBLOCK, the E22 and the E72 (the load switches now discharge their outputs; "
            "the lines' series resistance is not drawn).",
     "new": "The back-feed of SD-EMC-2 into the RockBLOCK, the E22 and the E72 is drawn since set 12 (stream d4emcon): the "
            "RockBLOCK's RXD and P_EN pass only while `RB_GO` (`U537` to `U539`), the E22's TXEN, RXEN, NRST and SPI lines only "
            "while `LORA_GO` (`U544` to `U550`), and the E72s' receive, reset and boot-select lines only through open drains, "
            "the receive lines pulled up to the modules' own switched rail `+3V3_ZB` (`U540` to `U542`, `R536`, `R537`; "
            "`CONOPS.md` section 4b).",
     "a": A_BACKFEED},
    {"doc": "v2/docs/PANEL.md", "why": "section 7, the 0x20 and 0x25 row: U6's RockBLOCK ENABLE request and P_EN request left out",
     "old": "PCA9555 `U6` (outputs: switch reset, rail enables, the module radio off requests into the open drains `U{s}14`, 5G control)",
     "new": "PCA9555 `U6` (outputs: switch reset, rail enables, the module radio off requests into the open drains `U{s}14`, 5G "
            "control, and the RockBLOCK's ENABLE request `RB_SW_IEN` and P_EN request `RB_CTRL_H`)",
     "a": ["B:U6@IO0_0=KSZ_RST", "B:U6@IO1_0=WL_nDIS1_OFF", "B:U6@IO0_6=5G_OFF", "B:U6@IO1_6=RB_SW_IEN", "B:U6@IO1_7=RB_CTRL_H",
           "B:U539.1=RB_CTRL_H", "B:U539.4=RB_CTRL", "B:J_RB9704.6=RB_CTRL"]},
    {"doc": "v2/docs/PANEL.md", "why": "section 7: the table's provenance named 45bde541 only, while its U27, U28 and supervisor rows come from later sets",
     "old": "the 0x48 row from board D's netlist of round 8 (MESHSAT-1357, stream d), whose SDA and SCL gain U22 and nothing else.",
     "new": "the 0x48 row from board D's netlist of round 8 (MESHSAT-1357, stream d), whose SDA and SCL gain U22 and nothing else; "
            "re-read on 29 September 2026 against the netlists of integration set 12 (A `6c40250c47195ebb`, B "
            "`3ef9b8c49a01b728`, C `87b69472ac83ca5a`, D `a2d48972d171aad1`) by `v2/docs/records/s122/verdicts.py`, which "
            "asserts that every device the table names is on its board's SDA net (the supervisors' and the secure element's "
            "addresses are firmware or TBD, as their rows say).",
     "a": ["A:SDA>U3,U8,U9,U10,U11,U14,U17,U27,U28", "B:SDA>U1,U5,U6,U7,U8,U9,U10,U41,U51,U61", "C:SDA>U1,U2,U3,U_LIGHT",
           "D:SDA>U16,U22"]},
    # ---------------------------------------------------------------- CONOPS.md
    {"doc": "v2/docs/CONOPS.md", "why": "section 4, Startup: undated citations of gen_sch_a.py and gen_sch_e.py lines that now hold other code",
     "old": "(`R42`, `gen_sch_a.py` line 887)",
     "new": "(`R42`, `gen_sch_a.py` line 887 at `45bde541`)",
     "a": ["G@45bde541:gen_sch_a.py:887~R42", "A:R42.1=DEV_EN", "A:R42.2=+3V3", "A:U7.1=DEV_EN"]},
    {"doc": "v2/docs/CONOPS.md", "why": "section 4, Startup (continued)",
     "old": "(`R2` over `R184`, lines 260 and 261)",
     "new": "(`R2` over `R184`, lines 260 and 261 at `45bde541`)",
     "a": ["G@45bde541:gen_sch_a.py:260-261~R2|R184|R4", "A:R2.1=RAIL_EN", "A:R2.2=VBAT", "A:R184.1=RAIL_EN", "A:R184.2=GND",
           "A:R4.1=KILL", "A:R4.2=+3V3"]},
    {"doc": "v2/docs/CONOPS.md", "why": "section 4, Startup (continued)",
     "old": "until the firmware writes the expanders (lines 763, 1009, 1112 and 1125)",
     "new": "until the firmware writes the expanders (lines 763, 1009, 1112 and 1125 at `45bde541`)",
     "a": ["G@45bde541:gen_sch_a.py:1112~R103", "G@45bde541:gen_sch_a.py:1125~R111", "A:R103~4.7k", "A:R103.1=PA_SW_EN",
           "A:R104.1=HF_SW_EN", "A:R111.1=MON_EN", "A:R112.1=HEAT_EN", "A:R114.1=POE_SW_EN", "A:R143.1=PD_SW_EN",
           "A:R21~4.7k", "A:R21.1=CHG_INHIBIT", "A:R21.2=GND"]},
    {"doc": "v2/docs/CONOPS.md", "why": "section 4, Startup (continued)",
     "old": "(143 k over 10 k, lines 1041 to 1064)",
     "new": "(143 k over 10 k, lines 1041 to 1064 at `45bde541`)",
     "a": ["G@45bde541:gen_sch_a.py:1041-1064~143k|U22", "A:R92~143k", "A:R92.2=U21_OVLO", "A:R93~10k", "A:R96~143k",
           "A:R96.2=U22_OVLO", "A:R97~10k"]},
    {"doc": "v2/docs/CONOPS.md", "why": "section 4, Startup (continued)",
     "old": "(the reed lands on the sensor controller alone, `gen_sch_e.py` lines 524 to 542,",
     "new": "(the reed lands on the sensor controller alone, `gen_sch_e.py` lines 524 to 542 at `45bde541`,",
     "a": ["G@45bde541:gen_sch_e.py:524-542~TAMPER", "E:J_TAMP?", "E:R53.2=TAMPER_IO"]},
    {"doc": "v2/docs/CONOPS.md", "why": "section 4, Charging: undated citations of gen_sch_a.py lines that now hold other code",
     "old": "`gen_sch_a.py` lines 764 to 771)",
     "new": "`gen_sch_a.py` lines 764 to 771 at `45bde541`)",
     "a": ["G@45bde541:gen_sch_a.py:764-771~R26|R27", "A:R26~13.3k", "A:R26.2=CH_CELL", "A:R27~40.2k", "A:R27.1=CH_CELL"]},
    {"doc": "v2/docs/CONOPS.md", "why": "section 4, Charging (continued)",
     "old": "(VSYS, the net `VBAT`, lines 18 to 48)",
     "new": "(VSYS, the net `VBAT`, lines 18 to 48 at `45bde541`)",
     "a": ["G@45bde541:gen_sch_a.py:18-48~VSYS|VBAT", "A:R17.1=VBAT", "A:R17.2=CELL_FUSED", "A:F1.2=CELL_FUSED"]},
    {"doc": "v2/docs/CONOPS.md", "why": "section 4, Service: undated citations of gen_sch_a.py lines that now hold other code",
     "old": "(`gen_sch_a.py` lines 1012 to 1015 and 1151 to 1167)",
     "new": "(`gen_sch_a.py` lines 1012 to 1015 and 1151 to 1167 at `45bde541`)",
     "a": ["G@45bde541:gen_sch_a.py:1012-1015~J_USBC_OUT", "G@45bde541:gen_sch_a.py:1151-1167~U32", "A:U32.3=USBX_EN",
           "A:U32.5=VBUS_WALL", "A:J_USBC_OUT?"]},
    {"doc": "v2/docs/CONOPS.md", "why": "section 4b preamble: it said every gate, supply and net was asserted by apply_conops_4b_set12.py, which asserts 146 pins of 55 parts (check-int13-3, n1)",
     "old": "Every gate, supply and net the rows\nbelow name was asserted on those netlists by `v2/docs/records/int13/apply_conops_4b_set12.py` before this text was\nwritten.",
     "new": "`v2/docs/records/int13/apply_conops_4b_set12.py` asserted 146 pin\nassignments of 55 of the parts the rows below name on those netlists before this text was written, and stream s122's\n`v2/docs/records/s122/verdicts.py` asserts the rest of the gates, supplies and nets the rows name on the same\nnetlists (among them the pins of `U9`, `R52` and `D23`, `U214`, `U314`, `U22` to `U24` and the source of `LIME_HW_EN`).",
     "a": A_C_CLAMP + ["B:U214.6=WL_nDIS2", "B:U314.6=WL_nDIS3", "B:U22.5=E72_EN", "B:U23.3=LIME_UVLO", "B:U24.3=RB_UVLO",
                       "B:U102@PWRCTL1=LIME_HW_EN", "DOC:v2/docs/records/int13/checks/check-int13-3.md~\"146 pin assignments\" equals the count in `GATES` (55 parts)"]},
    {"doc": "v2/docs/CONOPS.md", "why": "section 4e: U{s}11 and an open L3, where round 8 makes EMCON_ON per slot from its own 3.3 V and set 12 adds U543",
     "old": "a loss of `+3V3_DEV` releases every EMCON gate hung on `EMCON_ON` or on a slot's `U{s}11` (EMCON.md L3, open under S-01)",
     "new": "a loss of `+3V3_DEV` releases no module radio, because since board B's round 8 each slot makes `EMCON_ON{s}` from its "
            "own 3.3 V (`U112`, `U212`, `U312`; EMCON.md L3, closed at desk in that round), and since set 12 `U543`, run from "
            "`+5V_DEV`, holds the RockBLOCK's ENABLE low while `+3V3_DEV` is below 2.79 V",
     "a": ["B:U112.2=EMCON_HW", "B:U112.4=EMCON_ON1", "B:U112.5=+3V3_CM1", "B:U212.4=EMCON_ON2", "B:U212.5=+3V3_CM2",
           "B:U312.4=EMCON_ON3", "B:U312.5=+3V3_CM3", "B:U113.5=+3V3_CM1", "B:U213.5=+3V3_CM2", "B:U313.5=+3V3_CM3",
           "B:!U111", "B:!U211", "B:!U311", "B:U543.1=RB_IEN", "B:U543.5=+3V3_DEV", "B:U543.6=+5V_DEV",
           "DOC:v2/docs/feasibility/EMCON.md~CLOSED at desk on board B's round 8 (section 4b)"]},
    {"doc": "v2/docs/CONOPS.md", "why": "section 4e: an undated citation of a gen_sch_e.py line that now holds other text",
     "old": "(`gen_sch_e.py` line 503)",
     "new": "(`gen_sch_e.py` line 503 at `45bde541`)",
     "a": ["G@45bde541:gen_sch_e.py:503~fan tachometers"]},
    {"doc": "v2/docs/CONOPS.md", "why": "section 4f: HOT-R1 called owed on boards A and E, drawn there since stream w4ae",
     "old": "(firmware; HOT-R1 owed on boards A and E, section 4c)",
     "new": "(firmware; HOT-R1 drawn on boards A and E since stream w4ae: board E's `Q11` pulls the dock line `BLK_SPARE`, which "
            "board A reads as `DOCK_SPARE` on `U27`, section 4c)",
     "a": A_HOTR1},
    # ---------------------------------------------------------------- V2-SPEC.md
    {"doc": "v2/docs/V2-SPEC.md", "why": "line 35, Time: the holdover clock put on the panel controller; it is board B's DS3231SN on the kit bus",
     "old": "a holdover RTC on the panel controller, chrony on each module",
     "new": "a holdover RTC on the kit I2C bus that the panel controller masters (board B's DS3231SN `U9`; correction 32), chrony on each module",
     "a": ["B:U9~DS3231SN", "B:U9.15=SDA", "B:U9.16=SCL", "C:U3@GPIO0=SDA"]},
    {"doc": "v2/docs/V2-SPEC.md", "why": "line 76: the RockBLOCK's ENABLE forced low listed as owed, drawn since stream w4b",
     "old": "the RockBLOCK 9704's ENABLE forced low by the EMCON hardware with its stored energy bounded,",
     "new": "the RockBLOCK 9704's response to its ENABLE, which the EMCON hardware forces low since board B's stream w4b (`U536`; "
            "a maker's document or bench E-04; correction 32),",
     "a": A_RB},
    {"doc": "v2/docs/V2-SPEC.md", "why": "the corrections list gains the record of lines 35 and 76",
     "old": "slot's own 5 V (`U116`, `U216`, `U316`). The counts do not change: 15 of 17 close locally at desk and 0 of 17 end to\n    end. Nothing is built.\n",
     "new": "slot's own 5 V (`U116`, `U216`, `U316`). The counts do not change: 15 of 17 close locally at desk and 0 of 17 end to\n    end. Nothing is built.\n"
            "32. **Set 12 (lines 35 and 76).** Session reading of stream s122 (29 September 2026, MESHSAT-1357, open item S-122)\n"
            "    against the committed netlists of integration set 12 (`v2/docs/records/s122/verdicts.out`). Line 76 listed the\n"
            "    RockBLOCK 9704's ENABLE forced low by the EMCON hardware as owed; it is drawn since board B's stream w4b (`U536`,\n"
            "    correction 31), and since set 12 `U543` also holds it low while `+3V3_DEV` is below 2.79 V; what stays owed is\n"
            "    the module's response when ENABLE falls (a maker's document or bench E-04). Line 35 put the holdover clock on the\n"
            "    panel controller; it is board B's DS3231SN `U9` on the kit I2C bus, which the panel controller masters. Nothing\n"
            "    is built.\n",
     "a": A_RB + ["B:U9~DS3231SN", "B:U9.15=SDA"]},
    # ---------------------------------------------------------------- OPERATING-ENVELOPE.md
    {"doc": "v2/docs/OPERATING-ENVELOPE.md", "why": "section 4: HOT-R1 called absent from the generators of boards A and E, drawn there since stream w4ae",
     "old": "do that once HOT-R1 is in the generators of boards A and E (the requirement reads FAIL on the generated boards until then) and on",
     "new": "do that with HOT-R1, which the generators of boards A and E carry since stream w4ae (board E's `Q11` on the dock line, read on board A's `U27`), and on",
     "a": A_HOTR1},
    {"doc": "v2/docs/OPERATING-ENVELOPE.md", "why": "section 4, USB-C row: an undated citation of a gen_sch_a.py line that now holds other code",
     "old": "(`gen_sch_a.py` line 1003)",
     "new": "(`gen_sch_a.py` line 1003 at `45bde541`)",
     "a": ["G@45bde541:gen_sch_a.py:1003~TPS25740A", "A:U18~TPS25740A", "A:U19~LM5176"]},
    {"doc": "v2/docs/OPERATING-ENVELOPE.md", "why": "section 4, operating modes: EMCON said to gate every transmitter rail, where the SA868's supply and the modules' radios are not rail-gated",
     "old": "EMCON (a hardware line gates every transmitter rail and the PA bias)",
     "new": "EMCON (a hardware line on every transmitter; what it removes is set out below)",
     "a": ["D:U12.2=TX_INHIBIT_n", "D:U12.4=KEY", "B:U113.1=EMCON_ON1"]},
    {"doc": "v2/docs/OPERATING-ENVELOPE.md", "why": "section 4: the RockBLOCK 9704's ENABLE listed as left, forced low in hardware since stream w4b",
     "old": "the SA868's PTT threshold and the RockBLOCK 9704's ENABLE, the 5G module's",
     "new": "the SA868's PTT threshold and the RockBLOCK 9704's response to its ENABLE (forced low in hardware since board B's stream w4b), the 5G module's",
     "a": A_RB},
    # ---------------------------------------------------------------- TEST-PLAN.md
    {"doc": "v2/docs/TEST-PLAN.md", "why": "section 6, E3-H: HOT-R1 treated as absent from the generated boards",
     "old": "with HOT-R1 on boards A and E (without it the run records the generated path, and the requirement reads FAIL at desk)",
     "new": "with HOT-R1 on boards A and E (drawn in their generators since stream w4ae)",
     "a": A_HOTR1},
    {"doc": "v2/docs/TEST-PLAN.md", "why": "section 7, P15: HOT-R1 treated as absent from the generated boards",
     "old": "HOT-R1 drawn on boards A and E (without it the run records the generated path and REQ-077 reads FAIL at desk)",
     "new": "HOT-R1 drawn on boards A and E (in their generators since stream w4ae)",
     "a": A_HOTR1},
    # ---------------------------------------------------------------- ASSEMBLY.md
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 4, SMBus lead: an undated citation of a gen_sch_e.py line that now holds other code",
     "old": "to the sensor controller's GPIO17; `gen_sch_e.py:218`)",
     "new": "to the sensor controller's GPIO17; `gen_sch_e.py:218` at `45bde541`)",
     "a": ["G@45bde541:gen_sch_e.py:218~J_SMB", "E:J_SMB.1=SMBC", "E:J_SMB.2=SMBD", "E:J_SMB.3=GND", "E:J_SMB.4=PRES_LEAD"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 4, device rail: an undated citation",
     "old": "an LM5176 stage with a 7.2 A minimum limit, `gen_sch_a.py:881`)",
     "new": "an LM5176 stage with a 7.2 A minimum limit, `gen_sch_a.py:881` at `45bde541`)",
     "a": ["G@45bde541:gen_sch_a.py:881~U7|+5V_DEV", "A:U7~LM5176", "A:U7.12=+5V_DEV"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 4, USB-C outlet: an undated citation",
     "old": "D-17, `gen_sch_a.py:1015-1026`, to be placed",
     "new": "D-17, `gen_sch_a.py:1015-1026` at `45bde541`, to be placed",
     "a": ["G@45bde541:gen_sch_a.py:1015-1026~J_USBC_OUT|U31", "A:U31.1=PD_CC1", "A:U31.2=PD_CC2"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 4, the Glenair lead: a citation of lines that hold nothing at 45bde541 and other code at the base",
     "old": "switched by A22's expander; `gen_sch_a.py:1613-1618`)",
     "new": "switched by A22's expander; `gen_sch_a.py:1668-1669` at `e57a7365`)",
     "a": ["G@e57a7365:gen_sch_a.py:1668-1669~J_USBW|U32", "A:U32.5=VBUS_WALL", "A:U32.3=USBX_EN", "A:U28@IO0_0=USBX_EN"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 4, heater mat: an undated citation",
     "old": "the mat's own 12 V and 7.5 W rating, `gen_sch_a.py:1047-1076`)",
     "new": "the mat's own 12 V and 7.5 W rating, `gen_sch_a.py:1047-1076` at `45bde541`)",
     "a": ["G@45bde541:gen_sch_a.py:1047-1076~U33|VHEAT", "A:U33~TPS62933", "A:U33.3=VHEAT_IN", "A:U22.5=VHEAT_IN"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 4, lid switch: an undated citation",
     "old": "E6 `J_TAMP` (JST-XH 1x2, `gen_sch_e.py:524-542`)",
     "new": "E6 `J_TAMP` (JST-XH 1x2, `gen_sch_e.py:524-542` at `45bde541`)",
     "a": ["G@45bde541:gen_sch_e.py:524-542~TAMPER", "E:J_TAMP?"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 4, changeover outputs: an undated citation",
     "old": "under the voted changeover, `gen_sch_b.py:1253-1272`)",
     "new": "under the voted changeover, `gen_sch_b.py:1253-1272` at `45bde541`)",
     "a": ["G@45bde541:gen_sch_b.py:1253-1272~SKY13351|WIFI_SEC", "B:J_WOA?", "B:J_WOB?"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 4, the dock contacts: undated citations",
     "old": "(`gen_sch_a.py:225`, `gen_sch_e.py:488`;",
     "new": "(`gen_sch_a.py:225` and `gen_sch_e.py:488` at `45bde541`;",
     "a": ["G@45bde541:gen_sch_a.py:225~J_DOCK", "G@45bde541:gen_sch_e.py:488~J_BLK", "A:J_DOCK.8=SHORE_INHIBIT",
           "A:J_DOCK.9=USB_E6_P", "A:J_DOCK.10=USB_E6_N", "A:J_DOCK.12=DOCK_SPARE"]},
    {"doc": "v2/docs/ASSEMBLY.md", "why": "section 8 step 3: PA_EN = EMCON_HW AND PA_SW_EN at lines that now hold other code; board A's round 8 made it TX_INHIBIT_n AND EMCON_HW AND PA_HOLD",
     "old": "the line is active low, `PA_EN = EMCON_HW AND PA_SW_EN` in `gen_sch_a.py:535-536`, and `R102` pulls it low (`:537`) "
            "with the ribbon out, so on a bare A22 the two rails stay off until the line is driven high).",
     "new": "the line is active low; since board A's round 8 `PA_EN` = `TX_INHIBIT_n` AND `EMCON_HW` AND `PA_HOLD` in `U35` and "
            "`U36`, and `HF_EN` likewise in `U37` and `U38` (`gen_sch_a.py:1572-1575` at `e57a7365`), and with the ribbon out "
            "`R102` pulls `EMCON_HW` low and `R145` pulls `TX_INHIBIT_n` low (`:1597-1598`), so on a bare A22 the two rails "
            "stay off until both lines are driven high).",
     "a": A_BOARD_A_GATES + ["G@e57a7365:gen_sch_a.py:1597-1598~R102|R145", "A:R102.1=EMCON_HW", "A:R102.2=GND",
                             "A:R145.1=TX_INHIBIT_n", "A:R145.2=GND"]},
]


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    sys.exit(2)


def pattern(old):
    return re.compile(r"\s+".join(re.escape(w) for w in old.split()))


def main():
    check = "--check" in sys.argv
    head = subprocess.run(["git", "-C", L.TOP, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
    nls = L.netlists()
    for k, s in NETS.items():
        if nls[k]["sha16"] != s: refuse("board %s's netlist is %s, not set 12's %s" % (k, nls[k]["sha16"], s))
    for rel, s in DOCS.items():
        if L.sha16(rel) != s: refuse("%s is %s, not the file stream s122 read (%s): already applied, or changed" % (rel, L.sha16(rel), s))
    n = 0
    for e in EDITS:
        if any(d in e["new"] for d in L.DASHES): refuse("a dash in the new text for %s" % e["why"])
        if " ".join(e["old"].split()) == " ".join(e["new"].split()): refuse("new text equals old: %s" % e["why"])
        for a in e["a"]:
            ok, msg = V.run_assert(a, nls)
            if not ok: refuse("%s: assertion fails: %s" % (e["why"], msg))
            n += 1
    texts = {rel: open(os.path.join(L.TOP, rel), encoding="utf-8").read() for rel in DOCS}
    spans = {rel: [] for rel in DOCS}
    for e in EDITS:
        hits = list(pattern(e["old"]).finditer(texts[e["doc"]]))
        if len(hits) != 1: refuse("%s: the old passage is found %d times" % (e["why"], len(hits)))
        new = e["new"] if "\n" in e["old"] else " ".join(e["new"].split("\n"))
        spans[e["doc"]].append((hits[0].start(), hits[0].end(), new, e))
    out, touched = {}, {}
    for rel, sp in spans.items():
        t0 = texts[rel]
        sp.sort(key=lambda x: x[0])
        if any(a[1] > b[0] for a, b in zip(sp, sp[1:])): refuse("%s: two passages overlap" % rel)
        touched[rel] = set()
        for a, b, _n, _e in sp:
            touched[rel] |= set(range(t0.count("\n", 0, a) + 1, t0.count("\n", 0, b) + 2))
        t1 = t0
        for a, b, nw, _e in reversed(sp):
            t1 = t1[:a] + nw + t1[b:]
        out[rel] = t1
    for e in EDITS:
        if len(list(pattern(e["new"]).finditer(out[e["doc"]]))) != 1: refuse("%s: the new passage does not read back once" % e["why"])
        grows = " ".join(e["old"].split()) in " ".join(e["new"].split())
        if len(list(pattern(e["old"]).finditer(out[e["doc"]]))) != (1 if grows else 0): refuse("%s: the old passage survives" % e["why"])
    if check:
        print("%s: --check: %d edits located, %d assertions hold on set 12's netlists and the generators; nothing written" % (TAG, len(EDITS), n))
        return 0
    changed = sorted(rel for rel in DOCS if spans[rel])
    for rel in changed:
        open(os.path.join(L.TOP, rel), "w", encoding="utf-8").write(out[rel])
        L.md_blocks(rel)   # re-parse
        d = subprocess.run(["git", "-C", L.TOP, "diff", "-U0", BASE, "--", rel], capture_output=True, text=True, check=True).stdout
        for m in re.finditer(r"(?m)^@@ -(\d+)(?:,(\d+))? ", d):
            a, c = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
            lines = set(range(a, a + c)) if c else {a}
            if c and not lines <= touched[rel]: refuse("%s: the diff touches old lines %s outside the corrected passages" % (rel, sorted(lines - touched[rel])))
    print("%s: %d passages corrected in %d documents at %s, %d assertions held first; %s" % (
        TAG, len(EDITS), len(changed), head, n, ", ".join("%s %s to %s" % (os.path.basename(r), DOCS[r], L.sha16(r)) for r in changed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
