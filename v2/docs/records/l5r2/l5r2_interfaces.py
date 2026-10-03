#!/usr/bin/env python3
"""l5r2_interfaces.py: Layer 5's second round, read back (MESHSAT-1357, 3 October 2026).

Reads the two contract files Layer 5 owns (pcb_interfaces.yaml and HW-FW-CONTRACT.md) as the tree holds them and as this branch's
base held them (BASE, in this branch's own history), the two copied inputs (`inputs/`), and the in-tree sources the round drew on
(netlists, intent files, generators, ASSEMBLY.md, PROCUREMENT.md, records l7pwr and l4e11, the makers' sheets under v2/vendor), and
prints:
  0. every file read, pinned by sha256 (the base's as "<commit>@<path>");
  1. hc5's field contract on every contract, before (BASE) and after (the tree), and the fields each touched contract gained;
  2. the no-loss proof for the eight first-twelve contracts (every string and number of the old block found in the new);
  3. the table: contract, field, the text written (an excerpt, verbatim in its target), its source with the figures the source
     prints, its mark, its invalidation trigger and the Layer 5 criterion it moves;
  4. every tbd entry of the touched contracts with its owner;
  5. the PROVISIONAL entries and their triggers; 6. the criteria moved; 7. the table as the page's markdown.
It REFUSES (exit 3) when an excerpt is not in its target, a figure is not printed by a cited source, a copied input's body does not
hash to the sha its header declares, a touched contract fails hc5's field contract, a leaf of an old block is lost, or a tbd entry
has no owner. Needs pdftotext (poppler) and PyYAML; a few seconds. Run from anywhere:
`python3 v2/docs/records/l5r2/l5r2_interfaces.py`. Nothing here is measured: it is a check of text against text."""
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
BASE = "a1f696de"   # fnd/int28's prepared line, this branch's base (in its own history)

TARGETS = {"yaml": "v2/ecad/tools/pcb_interfaces.yaml", "hwfw": "v2/docs/HW-FW-CONTRACT.md"}
SOURCES = {
    "e18": "v2/docs/records/l5r2/inputs/l4e11-section-18-b929d8be.md",
    "l8gnd": "v2/docs/records/l5r2/inputs/l8gnd-sections-2-3-226e9143.md",
    "l7pwr": "v2/docs/records/l7pwr/L7-FANS-AND-TH1.md",
    "sanyo": "v2/vendor/fans/sanyo-denki-splash-proof-fan-pages-2026-10-03.md",
    "l4e11md": "v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md",
    "assembly": "v2/docs/ASSEMBLY.md",
    "proc": "v2/docs/parts/PROCUREMENT.md",
    "net_a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net",
    "net_b": "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net",
    "net_c": "v2/ecad/pcb-c-display-c8/out/pcb-c-display.net",
    "net_d": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net",
    "intent_a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json",
    "intent_d": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs-intent.json",
    "genb": "v2/ecad/tools/gen_sch_b.py",
    "gend": "v2/ecad/tools/gen_sch_d.py",
    "qmx": "v2/vendor/qrp-labs/qmx-product-page-2026-09-27.txt",
    "ifaces": "v2/ecad/tools/pcb_interfaces.yaml",
    "hdr2x13": "v2/vendor/connectors/wurth-wr-bhd-box-header-61202621621.pdf",
    "sock2x13": "v2/vendor/connectors/wurth-wr-bhd-idc-socket-61202623021.pdf",
    "cab26": "v2/vendor/connectors/wurth-wr-cab-ribbon-63912615521cab.pdf",
    "vh": "v2/vendor/connectors/jst-vh-catalogue.pdf",
    "msmf": "v2/vendor/power/bourns-mf-msmf-pptc.pdf",
    "ltc2954": "v2/vendor/power/ltc2954.pdf",
    "ra30": "v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf",
}
HC5 = "v2/docs/records/hc5/check_contract_fields.py"
EIGHT = ["IF-BC-PANEL", "IF-AB-RIBBON", "IF-AB-WALL", "IF-AD-HARNESS", "IF-AC-MAINSW", "IF-AE-RF", "IF-A-PA", "IF-LID-HF"]
TOUCHED = EIGHT + ["IF-AE-DOCK", "IF-E-FANS", "IF-B-FANS", "IF-EXT-ETH", "IF-EXT-DC", "IF-A-CHASSIS"]
CRITERIA = {
    "5.2": "every interface owned at both ends with its connector",
    "5.4": "electrical levels stated per interface",
    "5.5": "power capacity of each power interface with margin",
    "5.6": "sequencing across interfaces",
    "5.7": "reset, default and cable-out states for every control line",
    "5.9": "harnesses defined and consistent",
    "5.10": "mechanical mating of every interface",
    "5.11": "firmware obligations affecting hardware explicit",
    "5.12": "GND-002 implemented everywhere",
    "5.13": "interface contracts consistent with the tree",
}
CRITERIA_STATE = {
    "5.2": "PARTLY, further: every contract in the file (31, IF-A-CHASSIS added) carries both ends with a part on every board end and "
           "every pass-2 field (hc5's checker, section 1), the IDC headers, sockets and cable named by HC6-SC-7; not claimed MET: no "
           "census shows that every interface of the netlists has a contract, and the generators still write no MPN (EQ-21)",
    "5.4": "PARTLY, further: levels stated for the eight first-twelve contracts, the fans (+12V_FAN DRAFTED, the coolers' +5V_Sn "
           "outside their range) and the chassis bond; the kit I2C's three segments still owed (SC-59)",
    "5.5": "PARTLY, further: the panel ribbon's PANEL_5V per conductor against the cable's 1 A with F1's trip band (a TBD), the "
           "mezzanine's +3V3 conductor, the PA lead at 60 percent of its VH contact, the MAIN lead's microamps, the fans' branch "
           "1.3208 A at 89.8 percent of U42's least limit (DRAFTED); open: the 18 AWG VH leads' rating, the fans' start current",
    "5.6": "PARTLY: the SLOT_EN hold is DRAFTED (record l8gnd, the keeper U43) and written into the contracts and FW-C02 as PROVISIONAL; "
           "H2's named item stays open until the keeper is in a generator; the fans' stagger and U22's RUN as power lines",
    "5.7": "PARTLY, further: default_state for the eight contracts, SLOT_EN's cable-out state with the keeper (2.547 V, 0.266 V), U22's "
           "RUN line; EQ-25 unchanged",
    "5.9": "PARTLY, further: harness fields for the eight contracts from ASSEMBLY.md section 4 and HC6-SC-7's parts; found: J_QMX's land "
           "a 2.54 mm pin header against the PH lead (L5R2-F04), J_AB2's length (TBD)",
    "5.10": "OPEN, further: mating fields for every contract; W4-F17 (J_AB2 into board D), J_QMX's land and the fans' lead terminations "
            "keep it open",
    "5.11": "PARTLY, further: FW-C02, FW-C01, FW-C14, V-C02 for the keeper, FW-E07 and FW-E11 for +12V_FAN (DRAFTED, PROVISIONAL); "
            "the reduced-mode duties of layer 2's m13 still owed",
    "5.12": "OPEN: GND-002's four changes are DRAFTED by record l8gnd, not in a generator; the contracts carry them as PROVISIONAL "
            "(IF-A-CHASSIS, IF-EXT-ETH, IF-EXT-DC, IF-AE-DOCK); the wall RJ45's shield path (l8gnd F01) open",
    "5.13": "PARTLY, further: stale texts corrected in place with their history kept (IF-BC-PANEL's F1, IF-A-PA's flange sensor, "
            "FW-E11's R228); check_contracts.py reads PASS 99 of 99 before and after; interfaces.py's readings owe a re-take (the yaml "
            "is its configuration input)",
}

T = []


def row(i, c, f, tg, tx, src, where, figs, mark, trig, crit):
    T.append(dict(id=i, contract=c, field=f, target=tg, text=tx, sources=src, where=where, figures=figs, mark=mark, trigger=trig,
                  criteria=crit))


L8 = "record l8gnd's release (its drafts applied after a release record); a change of U43, R230 to R232, R229 or the two board B changes in that record"
E18 = "L4-E11 section 18's release (b929d8be merged and its draft applied); a change of U22's network or the fans' declared draw"
row("R2-01", "IF-BC-PANEL", "ends.b part", "yaml",
    "Wurth WR-BHD 61202621621 (session pick HC6-SC-7, JLCPCB C17586777; 3 A per contact at 25 C, -40 to +105 C, 30 mating cycles",
    ["proc", "hdr2x13", "net_b"], "PROCUREMENT.md 5 (HC6-SC-7); the header's sheet; B netlist",
    ["61202621621", "C17586777", "@ 25 °C 3 A max", "Durability 30 Mating cycles", "IDC-Header_2x13_P2.54mm_Vertical_NarrowPad"],
    "MAKER", "a different pick under HC6-SC-7's reversal (a failed land comparison)", ["5.2"])
row("R2-02", "IF-BC-PANEL", "ends.c part", "yaml", "XFCN BH254VS-26P (session pick HC6-SC-7, C48687640, no maker sheet read",
    ["proc", "net_c"], "PROCUREMENT.md 5; C netlist", ["BH254VS-26P", "C48687640", "IDC-Header_2x13_P2.54mm_Vertical_SMD"],
    "NETLIST; the part's sheet NOT READ", "none: a TBD (the sheet), owner Layer 6", ["5.2"])
row("R2-03", "IF-BC-PANEL", "harness.rating (moved from cable)", "yaml",
    "sockets Wurth WR-BHD 61202623021 (1 A per contact max, -40 to +105 C, 30 mating cycles) on flat cable WR-CAB 63912615521CAB (1.27 mm, 28 AWG, 1 A per conductor max, -25 to +105 C, 300 V RMS)",
    ["sock2x13", "cab26", "proc"], "the socket's and the cable's sheets; HC6-SC-7",
    ["61202623021", "63912615521CAB", "Rated Current IR 1 A max", "Operating Temperature -40 up to +105", "-25 °C up to +105", "300"],
    "MAKER", "none", ["5.9"])
row("R2-04", "IF-BC-PANEL", "current.per_conductor", "yaml",
    "F1 holds 1.10 A (0.55 A a conductor) and trips at 2.20 A at 23 C (Bourns MF-MSMF sheet, every MF-MSMF110 variant)",
    ["msmf", "net_b"], "the MF-MSMF table; B netlist's F1", ["MF-MSMF110/16 16 100 1.10 2.20", "Bourns MF-MSMF110-2"],
    "MAKER, INFERRED (the per-conductor split); a TBD for the 2.0 to 2.2 A band", "none: a TBD (the cable's capability above 1 A), owner Layer 6", ["5.5"])
row("R2-05", "IF-BC-PANEL", "protection (a stale statement corrected, kept)", "yaml",
    "since b76c18cb F1 IS the MF-MSMF110 (B19 netlist: '1.1A hold 1812 (Bourns MF-MSMF110-2)')", ["net_b"], "B netlist's F1",
    ["1.1A hold 1812 (Bourns MF-MSMF110-2)"], "NETLIST", "none", ["5.13"])
row("R2-06", "IF-BC-PANEL", "cable_out_states.SLOT_EN1..3", "yaml",
    "held high at least 2.547 V, held low at most 0.266 V, the worst cases of l8gnd 3b", ["l8gnd"], "l8gnd 3b",
    ["**2.547 V**", "**0.266 V**"], "INFERRED (record l8gnd's arithmetic on MAKER rows); DRAFTED; PROVISIONAL", L8, ["5.7"])
row("R2-07", "IF-BC-PANEL", "slot_power_semantics", "yaml",
    "keepers U43 (SN74LVC08A, one gate a line) with R230 to R232 (4.7 k) on board A keep each line at its last driven level",
    ["l8gnd"], "l8gnd 3a, 3g", ["U43, an SN74LVC08APWR", "R230, R231, R232", "4.7 k"], "NETLIST (the draft's text); DRAFTED; PROVISIONAL", L8, ["5.6"])
row("R2-08", "IF-AB-RIBBON", "ends.a part", "yaml", "IDC 2x13, top side: Wurth WR-BHD 61202621621 (session pick HC6-SC-7, JLCPCB C17586777",
    ["proc", "net_a"], "HC6-SC-7; A netlist", ["61202621621", "IDC-Header_2x13_P2.54mm_Vertical_NarrowPad"], "MAKER", "as R2-01", ["5.2"])
row("R2-09", "IF-AB-RIBBON", "hot_plug", "yaml", "with the hold applied (record l8gnd, DRAFTED) it no longer drops SLOT_EN",
    ["l8gnd"], "l8gnd 3g", ["with the hold applied it no longer drops SLOT_EN"], "DRAFTED; PROVISIONAL", L8, ["5.7"])
row("R2-10", "IF-AB-WALL", "ends.a part", "yaml",
    "IDC 2x5 vertical box header: Wurth WR-BHD 61201021621 (session pick HC6-SC-7, JLCPCB C4355000", ["proc", "net_a"],
    "HC6-SC-7; A netlist", ["61201021621", "C4355000", "IDC-Header_2x05_P2.54mm_Vertical_NarrowPad"], "MAKER", "as R2-01", ["5.2"])
row("R2-11", "IF-AB-WALL", "current", "yaml",
    "VBUS_WALL does not cross this ribbon (it leaves board A on J_USBW behind the eFuse U32, 0.9142 A", ["assembly"],
    "ASSEMBLY.md section 4, the wall USB host row", ["0.9142 A", "J_USBW"], "VERIFIED", "none", ["5.5"])
row("R2-12", "IF-AB-WALL", "hot_plug (a session choice)", "yaml", "not hot-pluggable (the session's choice in record l5r2", [], "this record, section 8",
    [], "RULE (SESSION)", "an interlock that makes live mating safe", ["5.10"])
row("R2-13", "IF-AD-HARNESS", "ends parts", "yaml", "J_MEZZ1 IDC 2x8 box header Wurth WR-BHD 61201621621 (session pick HC6-SC-7,",
    ["proc", "net_a", "net_d"], "HC6-SC-7; A and D netlists",
    ["61201621621", "C5364137", "IDC-Header_2x08_P2.54mm_Vertical_NarrowPad", "JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "C274411"], "MAKER, NETLIST", "as R2-01", ["5.2"])
row("R2-14", "IF-AD-HARNESS", "current.power_lead.contact", "yaml",
    "the fitted lead is 18 AWG on the standard B2P-VH, a combination the catalogue does not rate", ["vh", "assembly"],
    "JST VH catalogue p.1; ASSEMBLY.md's mezzanine 5 V row", ["Current rating: 10 A", "When using AWG #16 with the standard type header",
    "When using AWG #18 with the shrouded type header", "18 AWG, 60 mm"], "MAKER (INCONCLUSIVE for the fitted combination)", "none: a TBD, owner Layer 6", ["5.5"])
row("R2-15", "IF-AD-HARNESS", "current.signals", "yaml",
    "board D's loads on it sum 0.0654 A (D intent: U16 0.06, U19 and U20 0.002 each, U22 0.0002, R92 0.0012)", ["intent_d", "intent_a"],
    "D's and A's intent files", ['"U16": 0.06', '"U22": 0.0002', '"R92": 0.0012', '"J_MEZZ1": 0.1'], "NETLIST (the intents' declarations)", "none", ["5.5"])
row("R2-16", "IF-AD-HARNESS", "levels", "yaml",
    "+5V_D8 from U41 at 4.872 to 5.133 V behind U23 (A intent, stream s99a), board D's codec 4.44 to 4.48 V at the 1.0 A typical",
    ["intent_a"], "A's intent, +5V_D8 and +5V_D8IN", ["4.872 to 5.133 V", "4.44 to 4.48 V"], "INFERRED (stream s99a)", "none (S-116 open, a TBD)", ["5.4"])
row("R2-17", "IF-AC-MAINSW", "ends parts", "yaml", "JST-XH B2B-XH-A 1x2 (C158012; 3 A per contact with AWG 22, JST XH catalogue) (A netlist)",
    ["net_a", "net_c"], "A and C netlists", ["C158012", "JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "meshsat:LeadLands_1x02"], "NETLIST", "none", ["5.2"])
row("R2-18", "IF-AC-MAINSW", "levels", "yaml",
    "open-circuit 1 to 2 V at -1 uA, falling threshold 0.6 to 1 V, pin range -1 to 26.4 V (Analog Devices 2954fb, p.3, MAKER)",
    ["ltc2954"], "2954fb p.3", ["PB Open Circuit Voltage", "PB Input Threshold", "26.4", "2954fb"], "MAKER", "none", ["5.4"])
row("R2-19", "IF-AC-MAINSW", "current", "yaml", "-3 to -15 uA at 0.6 V and -1 to -12 uA at 1 V (2954fb p.3,", ["ltc2954"], "2954fb p.3",
    ["PB Input Current", "VPB = 0.6V", "VPB = 1V"], "MAKER", "none", ["5.5"])
row("R2-20", "IF-AC-MAINSW", "sequencing (moved from note)", "yaml",
    "a tap while running raises PI_SHDN_REQ (FW-A10, FW-A12)", [], "HW-FW-CONTRACT.md FW-A10, FW-A12", [], "VERIFIED (the contract's own rows)", "none", ["5.6"])
row("R2-21", "IF-AE-RF", "ends.a part", "yaml",
    "Radiall SMP-MAX slide-on receptacles R222M00720 (land meshsat:Radiall_SMPMAX_R222M00720)", ["net_a"], "A netlist",
    ["R222M00720", "meshsat:Radiall_SMPMAX_R222M00720", "SMA_Amphenol_132134-11_Vertical", "C3174425"], "NETLIST", "none", ["5.2"])
row("R2-22", "IF-AE-RF", "ends.e part", "yaml", "holding eleven Radiall R222M80500 right-angle SMP-MAX plugs", ["assembly"],
    "ASSEMBLY.md section 4, the RF jumpers row", ["R222M80500"], "VERIFIED", "none", ["5.2"])
row("R2-23", "IF-AE-RF", "harness", "yaml", "RG-316 jumpers, each cut to its route plus 20 mm, 252 to 432 mm, bend radius 12.5 mm",
    ["assembly"], "ASSEMBLY.md section 4, the RF jumpers row", ["252 to 432 mm", "bend radius 12.5 mm"], "VERIFIED", "the jumper plug's pick (M17g, M17x)", ["5.9"])
row("R2-24", "IF-A-PA", "ends.d part", "yaml",
    "J_VGG JST-PH B2B-PH-K 1x2 (C131337); J_PAIN U.FL Hirose U.FL-R-SMT-1 (C88373); J_PAOUT SMA Amphenol 132134 vertical (C3174425)",
    ["net_d"], "D netlist", ["C131337", "C88373", "U.FL_Hirose_U.FL-R-SMT-1_Vertical", "SMA_Amphenol_132134_Vertical"], "NETLIST", "none", ["5.2"])
row("R2-25", "IF-A-PA", "levels (the drive)", "yaml",
    "50 mW at J_PAIN (gen_sch_d.py), against the module's Pin absolute 100 mW", ["gend", "ra30"], "gen_sch_d.py's pad; the module's sheet",
    ["0.5 W in, 50 mW to the PA", "Pin Input Power 100 mW", "Pin=50mW"], "MAKER, NETLIST", "none", ["5.4"])
row("R2-26", "IF-A-PA", "current.contact", "yaml", "the 6.0 A peak is 60 percent of it", ["vh", "intent_a"], "the VH catalogue; A's intent",
    ["Current rating: 10 A", '"J_PA": 6.0'], "MAKER, INFERRED", "F-PR-02 (the drain current characterised)", ["5.5"])
row("R2-27", "IF-LID-HF", "ends.b part (finding L5R2-F04)", "yaml",
    "gen_sch_b.py's land key PH1x4 is Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", ["genb", "net_b"],
    "gen_sch_b.py's footprint table; B netlist", ['"PH1x4": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"'], "NETLIST",
    "board B's land changed to a JST-PH part, or the contract and ASSEMBLY.md to the pin header", ["5.10", "5.13"])
row("R2-28", "IF-LID-HF", "current.maker", "yaml", "receive 80 mA, transmit around 0.7 A for 5 W with a 12 V supply", ["qmx"],
    "QRP Labs' product page", ["Receive current 80mA", "around 0.7A for 5W with 12V supply"], "MAKER (approximate)", "QRP Labs' manual's figure", ["5.5"])
row("R2-29", "IF-LID-HF", "levels (RF)", "yaml", "the QMX's 3 to 5 W output at a 12 V supply", ["qmx"], "QRP Labs' product page",
    ["3-5W output at 12V supply"], "MAKER", "none", ["5.4"])
row("R2-30", "IF-E-FANS", "ends.device", "yaml",
    "two Sanyo Denki 9WL0612P4H001 (San Ace 60W, 60 x 60 x 25, IP68, 12 V, 10.8 to 13.2 V, 0.17 A, 2.04 W, -20 to +70", ["sanyo", "l7pwr"],
    "the maker's page as transcribed; l7pwr 2d", ["9WL0612P4H001", "10.8 to 13.2", "0.17", "2.04", "-20 to +70"], "MAKER", "a fan printing a covering range (D-18's reversal)", ["5.2"])
row("R2-31", "IF-E-FANS", "levels", "yaml",
    "+12V_FAN 12.001 V (11.512 to 12.431 V at FB's limits) from U22 on VSYS_E, inside the fans' 10.8 to 13.2 V by 0.71 V below and 0.77 V above",
    ["e18"], "L4-E11 18a", ["12.001 V", "11.512 to 12.431 V", "0.71 V below and 0.77 V above"], "MODELED; DRAFTED; PROVISIONAL", E18, ["5.4"])
row("R2-32", "IF-E-FANS", "current", "yaml",
    "at U22's input 0.5208 A for both at full speed at VSYS_E's floor (4.08 W over 0.85 at 9.508 V plus 16 mA), the dock branch 1.3208 A with U12, 89.8 percent of U42's least limit 1.4713 A",
    ["e18"], "L4-E11 18b", ["0.5208 A", "4.08 W over 0.85 at 9.508 V", "1.3208 A", "89.8 %", "1.4713 A"], "MODELED (0.85 an ASSUMPTION); DRAFTED; PROVISIONAL",
    E18 + "; the start current read (E11-35, R-179)", ["5.5"])
row("R2-33", "IF-E-FANS", "power", "yaml", "RUN on at 8.33 V and off at 6.89 V of VSYS_E", ["e18"], "L4-E11 18a",
    ["**8.33 V**", "**6.89 V**", "**0.72 W**"], "INFERRED (the comparator's limits); DRAFTED; PROVISIONAL", E18, ["5.6"])
row("R2-34", "IF-E-FANS", "sequencing", "yaml", "never while U12 or U22 starts (FW-E11, E11-39, R-188; L4-E11 18c)", ["e18"], "L4-E11 18c",
    ["never while U12 or U22 starts"], "RULE (L4-E11, SESSION); PROVISIONAL", E18, ["5.6", "5.11"])
row("R2-35", "IF-B-FANS", "ends.device", "yaml",
    "three Sanyo Denki 9WPA0412P6G001 (San Ace 40W, 40 x 40 x 20, IP68, 12 V, 10.8 to 13.2 V, 0.17 A, 2.0 W", ["sanyo", "l7pwr"],
    "the maker's page; l7pwr 2d", ["9WPA0412P6G001", "40 x 20"], "MAKER", "as R2-30", ["5.2"])
row("R2-36", "IF-B-FANS", "levels (E11-40)", "yaml", "the slot's +5V_Sn at 5.1 V on pin 1 (B netlist; L4-E11 18d), OUTSIDE the fans' 10.8 to 13.2 V",
    ["e18"], "L4-E11 18d", ["**5.1 V**", "E11-40"], "NETLIST; PROVISIONAL (E11-40 open)", "board B's owner drawing a regulated 12.0 V feed (E11-40)", ["5.4"])
row("R2-37", "IF-B-FANS", "current", "yaml", "about 0.436 A each at full speed (record l7pwr, F-L7-02, INFERRED)", ["e18"], "L4-E11 18d",
    ["0.436 A"], "INFERRED; PROVISIONAL", "E11-40's feed drawn (a step-up's efficiency or a 12 V feed changes the figure)", ["5.5"])
row("R2-38", "IF-AE-DOCK", "pin1_vsys_dock (round 2)", "yaml",
    "is declared 1.3208 A (U12 0.8 A, U22 0.5208 A at the floor with both fans at full speed), 89.8 percent of U42's least limit 1.4713 A with 0.1504 A in hand",
    ["e18"], "L4-E11 18b", ["1.3208 A", "0.1504 A", "37.7 %", "9.508 V", "1.21 W"], "MODELED; DRAFTED; PROVISIONAL", E18, ["5.5"])
row("R2-39", "IF-AE-DOCK", "ends.e5 part", "yaml",
    "the dock block E5: twelve plated contact targets, four pack targets, a pre-charge target, eight VIN_RAW targets", ["ifaces"],
    "this file's boards.e5 and IF-AE-DOCK not_judged", ["twelve plated contact targets, four pack targets, a pre-charge target", "eight VIN_RAW targets"],
    "VERIFIED (the file's own statements)", "none", ["5.2"])
row("R2-40", "power_line_states", "SLOT_EN1..3 hold", "yaml",
    "held HIGH at least 2.547 V (the pad's pull-down at 50 k), held LOW at most 0.266 V (at 80 k)", ["l8gnd"], "l8gnd 3b, 3d",
    ["**2.547 V**", "**0.266 V**", "the pad at 50 k", "the pad at 80 k"], "INFERRED; DRAFTED; PROVISIONAL", L8, ["5.6", "5.7"])
row("R2-41", "power_line_states", "U22_RUN_12V_FAN", "yaml", "on at 8.33 V of VSYS_E (7.98 to 8.67 V) and off at 6.89 V (6.55 to 7.23 V)",
    ["e18"], "L4-E11 18a", ["7.98 to 8.67 V", "6.55 to 7.23 V", "R103 1.5M / R104 255k"], "INFERRED; DRAFTED; PROVISIONAL", E18, ["5.7"])
row("R2-42", "IF-EXT-ETH", "grounding", "yaml", "C33 to CHASSIS and J_ETH SH to CHASSIS, Microchip DS00004151A p.10", ["l8gnd"], "l8gnd 2a, 2c",
    ["DS00004151A p.10", "connected to chassis ground through a 1000 pF, 2 kV capacitor", "The metal case shield of the RJ45 connector is also tied to chassis ground"],
    "MAKER (the clause); DRAFTED; PROVISIONAL", L8, ["5.12"])
row("R2-43", "IF-EXT-ETH", "tbd (l8gnd F01)", "yaml", "the PX0833's plastic body, the PX0888 backshell", ["l8gnd"], "l8gnd 2c",
    ["Polyester (PET), Plastic Body", "PX0888"], "VERIFIED (record l8gnd's reading of the held sheet)", "the wall RJ45's pick", ["5.12"])
row("R2-44", "IF-A-CHASSIS", "ends.a part", "yaml",
    "M4 bonding pad, land meshsat:ChassisLug_M4_CHASSIS (plated hole 4.3, 12.0 ring both sides)", ["l8gnd"], "l8gnd 2b",
    ["meshsat:ChassisLug_M4_CHASSIS", "plated hole 4.3, 12.0 ring both sides", "R229"], "NETLIST (the draft's text); DRAFTED; PROVISIONAL", L8, ["5.2", "5.12"])
row("R2-45", "FW-C02", "the keeper", "hwfw",
    "SLOT_EN1..3 held at their last driven level across a panel reset by board A's keepers U43 (SN74LVC08A) with R230 to R232", ["l8gnd"], "l8gnd 3f",
    ["held at their last driven level across a panel reset by board A's keepers U43"], "DRAFTED; PROVISIONAL", L8, ["5.11"])
row("R2-46", "V-C02", "extended", "hwfw", "each SLOT_EN read on a scope at or above 2.5 V throughout (the held high)", ["l8gnd"], "l8gnd 3h",
    ["each SLOT_EN read on a scope at or above 2.5 V throughout"], "TEST; PROVISIONAL", L8, ["5.11"])
row("R2-47", "FW-E11", "U42's ILIM resistor", "hwfw", "R228 11.0 kOhm, renamed from R221 by L4-E11 at `787e7b15`", ["l4e11md"],
    "L4-E11's record (in this tree since 787e7b15)", ["R228"], "VERIFIED", "none", ["5.13"])
row("R2-48", "FW-E11", "the start's room", "hwfw", "leaves 0.1504 A of room, 1.21 W at the rail for the other fan's start (18b)", ["e18"],
    "L4-E11 18b", ["0.1504 A", "1.21 W"], "MODELED; DRAFTED; PROVISIONAL", E18 + "; the start current read (E11-35)", ["5.11"])

# Every tbd entry of the touched contracts, matched by a substring to its owner.
OWNERS = [
    ("IF-BC-PANEL", "capability above their 1 A maximum", "Layer 6 (Wurth's statement) or the bench (Layer 9)"),
    ("IF-BC-PANEL", "XFCN BH254VS-26P", "Layer 6 components"),
    ("IF-BC-PANEL", "the SLOT_EN hold", "Layer 8 board A (record l8gnd's release)"),
    ("IF-AB-RIBBON", "SEG-A's buffer U_A", "Layer 8 board A (SC-HF-02)"),
    ("IF-AB-RIBBON", "the SLOT_EN hold", "Layer 8 board A (record l8gnd's release)"),
    ("IF-AB-WALL", "the ribbon's length", "Layer 7 (ASSEMBLY.md's leads table)"),
    ("IF-AB-WALL", "W4-F17", "Layer 7 and Layer 8 board A"),
    ("IF-AB-WALL", "link-speed test", "Layer 9 bench (bring-up)"),
    ("IF-AD-HARNESS", "18 AWG lead on the standard VH header", "Layer 6 (JST's rating) or Layer 7 (a 16 AWG lead)"),
    ("IF-AD-HARNESS", "a +3V3 fault on board D", "Layer 8 board A"),
    ("IF-AD-HARNESS", "S-116", "Layer 8 boards A and D (S-116)"),
    ("IF-AC-MAINSW", "the lead's length", "Layer 7"),
    ("IF-AE-RF", "power handling at 144 MHz", "Layer 6 components"),
    ("IF-AE-RF", "right-angle SMA plug", "Layer 7 (M17g, M17x)"),
    ("IF-AE-RF", "twelfth site", "Layer 8 board A (D-07)"),
    ("IF-AE-RF", "a DC antenna feed", "Layer 6 components"),
    ("IF-A-PA", "the drain current", "Layer 9 bench (F-PR-02)"),
    ("IF-A-PA", "the band lock", "the firmware owner (FW-D03, D-04)"),
    ("IF-LID-HF", "J_QMX's land", "Layer 8 board B and ASSEMBLY.md's owner (L5R2-F04)"),
    ("IF-LID-HF", "18 AWG HF lead", "Layer 6 or Layer 7"),
    ("IF-LID-HF", "QMX's supply current", "Layer 6 (QRP Labs' manual)"),
    ("IF-AE-DOCK", "the fans' part", "Layer 9 bench (E11-35, R-179)"),
    ("IF-AE-DOCK", "the 813 contact's pulse capability", "Layer 6 (Preci-Dip's statement) and Layer 9 (E11-38)"),
    ("IF-E-FANS", "start current", "Layer 9 bench (E11-35, R-179)"),
    ("IF-E-FANS", "PWM input level", "Layer 6 (the maker's manual, F-L7-11)"),
    ("IF-E-FANS", "lead termination", "Layer 7 (HF-F04)"),
    ("IF-E-FANS", "the rail U22", "the Layer 4 coordinator and Layer 8 board E (L4-E11 section 18's release)"),
    ("IF-B-FANS", "E11-40", "Layer 8 board B"),
    ("IF-B-FANS", "start current and the PWM input level", "Layer 6 and Layer 9"),
    ("IF-B-FANS", "lead termination", "Layer 7"),
    ("IF-EXT-ETH", "the sealed RJ45 part", "Layer 7"),
    ("IF-EXT-ETH", "shield path to the plate", "Layer 7 (the wall RJ45's pick, l8gnd F01)"),
    ("IF-EXT-ETH", "the PoE class", "the firmware owner (FW-B14)"),
    ("IF-EXT-ETH", "magnetics' surge rating", "Layer 6 components"),
    ("IF-EXT-ETH", "the MDI side", "Layer 8 board B"),
    ("IF-EXT-DC", "the receptacle MPN", "Layer 7 (R-129)"),
    ("IF-EXT-DC", "installed and short-time ratings", "Layer 6 and Layer 7 (R-113, R-115, R-129 to R-132)"),
    ("IF-EXT-DC", "A-3(c)", "Layer 6 (R-148)"),
    ("IF-EXT-DC", "size 16 contact rating", "Layer 6"),
    ("IF-EXT-DC", "PV_RTN", "Layer 8 board E (R-173)"),
    ("IF-A-CHASSIS", "the strap and the lugs", "Layer 7 (l8gnd F07)"),
    ("IF-A-CHASSIS", "R229's BOM code", "Layer 6 (l8gnd F09)"),
    ("IF-A-CHASSIS", "bond resistance", "Layer 9 (pre-compliance)"),
    ("IF-A-CHASSIS", "record l8gnd's release", "Layer 8 (the integrator of l8gnd)"),
]


def flat(s):
    return " ".join(str(s).split())


def leaves(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from leaves(v)
    elif isinstance(o, list):
        for v in o:
            yield from leaves(v)
    elif o is not None:
        yield flat(o)


def refuse(msg):
    sys.stderr.write("l5r2_interfaces: %s\n" % msg)
    sys.exit(3)


def git_base(rel):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (BASE, rel)], capture_output=True)
    if r.returncode != 0:
        refuse("%s is not readable at %s (a git checkout holding this branch's history is needed)" % (rel, BASE))
    return r.stdout


def read_source(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        refuse("missing %s" % rel)
    raw = open(p, "rb").read()
    if rel.endswith(".pdf"):
        if shutil.which("pdftotext") is None:
            refuse("pdftotext is needed for %s" % rel)
        r = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True)
        if r.returncode != 0:
            refuse("pdftotext failed on %s" % rel)
        return raw, r.stdout.decode("utf-8", "replace")
    return raw, raw.decode("utf-8", "replace")


def copied_body(text, rel):
    m = re.search(r"the body's own sha256 is ([0-9a-f]{64})", text)
    i, j = text.find("<!-- BODY BEGIN -->\n"), text.find("<!-- BODY END -->")
    if not m or i < 0 or j < i:
        refuse("%s does not carry its declared body" % rel)
    body = text[i + len("<!-- BODY BEGIN -->\n"):j]
    if hashlib.sha256(body.encode("utf-8")).hexdigest() != m.group(1):
        refuse("%s's body does not hash to the sha its header declares" % rel)
    return body, m.group(1)


def hc5():
    p = os.path.join(ROOT, HC5)
    sp = importlib.util.spec_from_file_location("hc5_fields", p)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def field_reading(m, cs):
    out = {}
    for cid, c in cs.items():
        errs = m.check(cid, c, False)
        top = sorted(set(e.split("`")[1] for e in errs if e.startswith(cid + ": no `")))
        other = [e.split(": ", 1)[1] for e in errs if not e.startswith(cid + ": no `")]
        out[cid] = ("carries every field" if not top else "no key for " + ", ".join(top)) + ("; " + "; ".join(other) if other else "")
    return out


def compute():
    pins, texts = {}, {}
    base_raw = {k: git_base(rel) for k, rel in TARGETS.items()}
    for k, rel in TARGETS.items():
        raw = open(os.path.join(ROOT, rel), "rb").read()
        texts[k] = flat(raw.decode("utf-8"))
        pins[k] = (rel, hashlib.sha256(raw).hexdigest())
        pins["base_" + k] = ("%s@%s" % (BASE, rel), hashlib.sha256(base_raw[k]).hexdigest())
    copies = {}
    for k, rel in SOURCES.items():
        raw, txt = read_source(rel)
        pins[k] = (rel, hashlib.sha256(raw).hexdigest())
        if "/inputs/" in rel:
            body, bsha = copied_body(txt, rel)
            copies[k] = bsha
            txt = body
        texts[k] = flat(txt)
    raw_hc5 = open(os.path.join(ROOT, HC5), "rb").read()
    pins["hc5"] = (HC5, hashlib.sha256(raw_hc5).hexdigest())
    m = hc5()
    old_doc = yaml.safe_load(base_raw["yaml"].decode("utf-8"))
    new_doc = yaml.safe_load(open(os.path.join(ROOT, TARGETS["yaml"]), encoding="utf-8").read())
    old_cs, new_cs = old_doc["board_to_board"]["contracts"], new_doc["board_to_board"]["contracts"]
    before, after = field_reading(m, old_cs), field_reading(m, new_cs)
    bad = [c for c in new_cs if after[c] != "carries every field" and c not in m.NEW]
    bad += [c for c in m.NEW if m.check(c, new_cs[c], True)]
    if bad:
        refuse("contracts failing hc5's field contract after the round: %s" % bad)
    gained = {}
    for cid in TOUCHED:
        o = old_cs.get(cid, {})
        n = new_cs[cid]
        keys = [k for k in n if k not in o]
        parts = sum(1 for e in n.get("ends", []) if isinstance(e, dict) and "board" in e and e.get("part")) - \
            sum(1 for e in o.get("ends", []) if isinstance(e, dict) and "board" in e and e.get("part"))
        moved = [k for k in o if k not in n]
        gained[cid] = (keys, parts, moved)
    noloss = {}
    for cid in EIGHT:
        nl = list(leaves(new_cs[cid]))
        ol = list(leaves(old_cs[cid]))
        lost = [x for x in ol if not any(x in y for y in nl)]
        if lost:
            refuse("%s lost %r" % (cid, lost[0][:80]))
        noloss[cid] = len(ol)
    errs, results = [], []
    seen = set()
    for e in T:
        if e["id"] in seen:
            errs.append("%s: duplicate id" % e["id"])
        seen.add(e["id"])
        if flat(e["text"]) not in texts[e["target"]]:
            errs.append("%s: the excerpt is not in %s: %r" % (e["id"], TARGETS[e["target"]], e["text"][:70]))
        src = " ".join(texts[s] for s in e["sources"])
        lost = [f for f in e["figures"] if flat(f) not in src]
        if lost:
            errs.append("%s: figures not printed by %s: %s" % (e["id"], ", ".join(e["sources"]), lost))
        if set(e["criteria"]) - set(CRITERIA):
            errs.append("%s: unknown criterion" % e["id"])
        if "PROVISIONAL" in e["mark"] and not e["trigger"].strip():
            errs.append("%s: PROVISIONAL with no trigger" % e["id"])
        results.append(e)
    tbds = []
    for cid in TOUCHED:
        for t_ in new_cs[cid].get("tbd") or []:
            hit = [o for c, sub, o in OWNERS if c == cid and sub in flat(t_)]
            if len(hit) != 1:
                errs.append("%s: tbd entry with %d owners: %r" % (cid, len(hit), flat(t_)[:70]))
                continue
            tbds.append((cid, flat(t_), hit[0]))
    unused = [(c, s) for c, s, _o in OWNERS if not any(c == x and s in t for x, t, _ in tbds)]
    if unused:
        errs.append("owner rows that match no tbd entry: %s" % unused)
    if errs:
        for x in errs:
            sys.stderr.write("l5r2_interfaces: %s\n" % x)
        sys.exit(3)
    prov = [(e["id"], e["contract"], e["trigger"]) for e in T if "PROVISIONAL" in e["mark"]]
    by_crit = {c: [e["id"] for e in T if c in e["criteria"]] for c in CRITERIA}
    return dict(pins=pins, copies=copies, before=before, after=after, gained=gained, noloss=noloss, rows=results, tbds=tbds,
                prov=prov, by_crit=by_crit, nfig=sum(len(e["figures"]) for e in T), ncon=len(new_cs), ncon0=len(old_cs))


def md_rows(R):
    keys = dict(TARGETS, **SOURCES)
    out = ["| id | contract | field | text written (excerpt, verbatim in the target) | source (file; where) | mark | invalidation trigger | criterion (5.x) |",
           "|---|---|---|---|---|---|---|---|"]
    for e in R["rows"]:
        src = "; ".join(os.path.basename(keys[s]) for s in e["sources"])
        src = (src + "; " if src else "") + e["where"]
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (e["id"], e["contract"], e["field"], e["text"].replace("|", "/"), src,
                                                                e["mark"], e["trigger"], ", ".join(e["criteria"])))
    return out


def render(R):
    L = []
    p = L.append
    p("L5-R2: LAYER 5'S SECOND ROUND, READ BACK (MESHSAT-1357, 3 October 2026). Prototype design: nothing built, powered or measured;")
    p("a check of the contracts' text against their sources' text. Marks: MAKER, NETLIST, VERIFIED, INFERRED, MODELED, RULE, TEST,")
    p("NOT READ; DRAFTED: true of a release-guarded draft no generator carries; PROVISIONAL: resting on an open condition, its trigger named.")
    p("")
    p("0. INPUTS (sha256)")
    for k in list(TARGETS) + ["base_yaml", "base_hwfw"] + list(SOURCES) + ["hc5"]:
        rel, h = R["pins"][k]
        p("   %-10s %s  %s" % (k, h, rel))
    for k, b in sorted(R["copies"].items()):
        p("   copied input %s: body sha256 %s, equal to the sha its header declares" % (k, b))
    p("")
    p("1. HC5'S FIELD CONTRACT ON EVERY CONTRACT, BEFORE (%s, %d contracts) AND AFTER (the tree, %d contracts)" % (BASE, R["ncon0"], R["ncon"]))
    for cid in sorted(R["after"]):
        b = R["before"].get(cid, "(not in the file)")
        p("   %-14s before: %s" % (cid, b))
        p("   %-14s after:  %s" % ("", R["after"][cid]))
    p("")
    p("   The fields each touched contract gained (keys new to it; board ends that gained a part; keys moved out):")
    for cid in TOUCHED:
        keys, parts, moved = R["gained"][cid]
        p("   %-14s gained %s; parts added %d; moved %s" % (cid, ", ".join(keys) or "none", parts, ", ".join(moved) or "none"))
    p("")
    p("2. NO LOSS: every string and number of the eight old blocks is found in the new ones")
    for cid in EIGHT:
        p("   %-14s %d leaves, all found" % (cid, R["noloss"][cid]))
    p("")
    p("3. THE TABLE (%d entries, %d figures; every excerpt found in its target, every figure printed by a cited source)" % (len(R["rows"]), R["nfig"]))
    for e in R["rows"]:
        p("   %s | %s | %s | target %s" % (e["id"], e["contract"], e["field"], TARGETS[e["target"]]))
        p("      text: %s" % e["text"])
        p("      source: %s%s" % (", ".join(dict(SOURCES)[s] for s in e["sources"]) + ("; " if e["sources"] else ""), e["where"]))
        p("      figures: %s" % (", ".join(e["figures"]) if e["figures"] else "none (a rule, a choice or a state)"))
        p("      mark: %s" % e["mark"])
        p("      trigger: %s" % e["trigger"])
        p("      criteria: %s" % ", ".join(e["criteria"]))
    p("")
    p("4. THE TBD ENTRIES OF THE TOUCHED CONTRACTS, WITH THEIR OWNERS (%d)" % len(R["tbds"]))
    for cid, t_, o in R["tbds"]:
        p("   %s | %s | owner: %s" % (cid, t_, o))
    p("")
    p("5. THE PROVISIONAL ENTRIES AND THEIR TRIGGERS (%d)" % len(R["prov"]))
    for i, c, t_ in R["prov"]:
        p("   %s (%s): %s" % (i, c, t_))
    p("")
    p("6. THE LAYER 5 CRITERIA THIS ROUND MOVES (Layer 5's reading; LAYER-STATUS.md is the integrator's page)")
    for c in sorted(CRITERIA, key=lambda x: float(x)):
        p("   %s %s: %d entries (%s)" % (c, CRITERIA[c], len(R["by_crit"][c]), ", ".join(R["by_crit"][c]) or "none"))
        p("      %s" % CRITERIA_STATE[c])
    p("")
    p("7. THE TABLE AS MARKDOWN (L5-INTERFACES-R2.md carries these lines)")
    for ln in md_rows(R):
        p("   " + ln)
    p("")
    p("8. RESULT: every contract carries every pass-2 field; the eight old blocks lose nothing; every excerpt is in its target and")
    p("   every figure is printed by a cited source; every tbd entry of the touched contracts has an owner.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.stdout.write(render(compute()))
