#!/usr/bin/env python3
"""DRAFT registry changes of board D and E stream w3de (MESHSAT-1357, 27 September 2026), for the integrator.

Applied to v2/ecad/tools/pcb_requirements.yaml of the tree named on the command line, by record id, with every edited
text asserted first; it takes the NEXT FREE SC-nn and S-nn in that tree, so it composes with other streams' drafts.

  1. three session choices (under the owner's standing rule of 26 September 2026):
       SC-a  EQ-16 / R8E-N01: VIN_RAW crosses the dock on Mill-Max power pins with its own return pins;
       SC-b  board E's LT8705A after S-47: MODE on LDO33, GATEVCC's own 4.7 uF, VIN's 100 nF, four declared bypasses;
       SC-c  PWR-001's kinds on boards D and E (EQ-19), and how the nets it left undecided are settled;
  2. three open items: S-x what of EQ-16 is still in flight once its two schematic halves land together; S-y finding W3DE-DOCK-R1 (the dock's ground-current
     sharing, a bench measurement owed); S-z PWR-001's three nets still UNDECIDED on D and E (the flyback diodes' sheets);
  3. S-47's title records what is done and what is still open (it stays OPEN);
  4. the eleven records bound to board D's or E's netlist, gen_sch_e.py, board A's netlist or gen_sch_a.py are re-read
     against the regenerated files and rebound, each with an evidence line naming what changed and that what it cites
     did not, and the four whose `source` cites gen_sch_a.py by line follow the lines it moved. The rebinding happens
     only when the tree holds exactly the files w3de regenerated, board A's half included (drafts/w3de/a-half/
     install_a_half.py; their sha256/16 are asserted below); otherwise the script refuses, because a binding written for
     other bytes would be the defect this registry exists to catch. EQ-16 has two halves and they land in ONE
     integration (pass 2 of the independent check, 27 September 2026): board E's alone would commit board A's VIN_RAW
     joined to board E's GND across four 813 contacts.

Usage: apply_registry.py <tree root holding v2/ecad> [--no-rebind]"""
import os, re, sys, hashlib, textwrap

ROOT = sys.argv[1]
REG = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_requirements.yaml")
s = open(REG, encoding="utf-8").read(); orig = s

def once(old):
    n = s.count(old)
    if n != 1: raise SystemExit("apply_registry: expected exactly one %r, found %d" % (old[:80], n))

def next_id(prefix, section_pat):
    ids = [int(m) for m in re.findall(r"^  - id: %s-(\d+)$" % prefix, s, re.M)]
    return max(ids) + 1 if ids else 1

def fold(text, indent):
    pad = " " * indent
    return "\n".join(textwrap.wrap(" ".join(text.split()), width=118 - indent, initial_indent=pad, subsequent_indent=pad,
                                   break_long_words=False, break_on_hyphens=False))

def block(key, text, indent=4):
    return " " * indent + key + ": >-\n" + fold(text, indent + 2) + "\n"

sc = next_id("SC", None); sn = next_id("S", None)
SCA, SCB, SCC = ["SC-%02d" % (sc + k) for k in range(3)]
SX, SY, SZ = ["S-%02d" % (sn + k) for k in range(3)]

# ---------------------------------------------------------------------------------------------------------- 1. choices
CHOICES = [
 (SCA,
  "How does VIN_RAW cross the dock at board E's declared 14.10 A, when the four Preci-Dip 813 contacts that carry it read "
  "3.53 A each against their 3.5 A maximum and 4.70 A with one open (EQ-16, R8E-N01, R4A-N13)?",
  "VIN_RAW crosses on four Mill-Max 0858-class power pins with four more for its return, as the pack's CELL+ does: board "
  "A's J_VR1 to J_VR4 (VIN_RAW) and J_VN1 to J_VN4 (GND) on E5 targets, E5's two 12 AWG holes to board E's P_VR and "
  "P_VN; the four 813 contacts that carried VIN_RAW (J_DOCK and J_BLK pins 1 to 4) become ground. Board E's half is in "
  "gen_sch_e.py; board A's, E5's, the IF-AE-DOCK contract's, check_contracts.py's, ASSEMBLY.md's and board E's placement "
  "are drafted for their owners (" + SX + ").",
  "At 14.10 A four 813 contacts run at 101 percent of their maximum and 134 percent with one open, and a fifth (the spare "
  "pin 12) still reads 101 percent with one open; Preci-Dip publishes no current-temperature curve for the 813, only its "
  "85 C music-wire limit, so no count of them can be shown at the desk to hold with one open at the envelope's 51 C "
  "inside air. Mill-Max states 9 A continuous at a 10 C rise, 20 mOhm maximum and -55 to +125 C: four pins carry 3.53 A "
  "each (39 percent), 4.70 A with one open (52 percent) and 7.05 A at a 2:1 resistance spread with one open (78 percent), "
  "under 72 C at the +55 C margin. A hardware input bound on board A would cut the front end's input power at a 9 V bus, "
  "a narrowed function, and one on board E cannot act while the vehicle holds the bus; the input path allows 14.4 A, so "
  "no reduced maximum is justified. The four return pins hold an 813 ground contact's share of the ground current to "
  "about 2.24 A with one open (64 percent) at the conservative 32.1 A. Reverse by a Preci-Dip derating curve that carries "
  "14.10 A on a count of 813 contacts that fits the block with one open inside 85 C, or by a layer 7 finding that the "
  "block cannot carry eight more power targets (then a 2x8 813 with eight VIN_RAW contacts and a bench measurement of "
  "their sharing).",
  ["drafts/w3de/EQ16-dock-vin-raw.md and drafts/w3de/dock_contacts.py",
   "v2/vendor/precidip/precidip-813-spring-loaded-connector-pages-31-34.pdf pp.31 and 34",
   "v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf page 28",
   "v2/ecad/tools/gen_sch_e.py (J_BLK, P_VR, P_VN; VIN_RAW's derivation R4A-N12)",
   "v2/docs/handover/ENGINEERING-QUESTIONS.md EQ-16"]),
 (SCB,
  "Board E's LT8705A tracker, once S-47 moves its current sense to the bottom switches' leg: how are MODE and the "
  "controller's supply-pin bypasses set?",
  "MODE (pin 37) is tied to TRK_LDO33 (discontinuous mode); GATEVCC (pin 15) gets its own 4.7 uF, C63, C19's part and "
  "land; VIN (pin 34) a 100 nF 50 V X7R at the pin, C64 (C14663); C19, C20, C63 and C64 are declared against pins 35, 4, "
  "15 and 34 with classes L, L, D and D.",
  "The maker: MODE low is forced continuous mode, and with the input regulation loop board E runs 'current being drawn "
  "from the output and forced into the input' can result (8705af p.29); the input is a panel; 'tie MODE to a voltage "
  "above 2.3V (i.e., LDO33)' gives discontinuous mode, in which M4 is held off on reverse inductor current (p.18), and a "
  "tie keeps the pin driven where Burst Mode would float it. GATEVCC 'Locally bypass to GND' (p.11), at least ten times "
  "CB (p.28), and the maker's circuits fit a second 4.7 uF there (p.1, p.41); VIN 'must be locally bypassed' (p.12). The "
  "classes follow decision 42's reading of the LM5176 (v2/docs/layout-constraints/E.md section 5). Reverse MODE with a "
  "measured reason forced continuous mode is wanted; the bypasses by a maker's circuit without them.",
  ["v2/vendor/power/lt8705a.pdf pp.11, 12, 18, 28, 29, 36", "v2/docs/layout-constraints/E.md section 5 and 6.1 item 9",
   "v2/ecad/tools/gen_sch_e.py (U5 pin 37, C63, C64, the bypass entries)"]),
 (SCC,
  "Which kind does each supply PWR-001 refused on boards D and E take (EQ-19), and how are the nets it left UNDECIDED "
  "settled?",
  "Nodes for the parts' own regulator outputs, charge pumps and bootstraps: on D PCM_VDD, PCM_VCCA, PCM_VCCL, PCM_VCCR, "
  "PCM_VCCP (3.6 V), SAU_3V3 (3.6 V), AMP_CPP, AMP_CPN and AMP_HPVSS (+-1.9 V, CPN riding on CPP); on E TRK_LDO33 (3.35 "
  "V), E6_DVDD (1.34 V) and E6_BST (riding on E6_SW at 6.0 V). A rail for SGP_VDD, another part's filtered supply "
  "branch, at the SGP41's whole 4.6 mA because the maker does not split VDD from VDDH. TRK_LSENSE is gone with S-47, "
  "and its successor TRK_CS is a node as board A's LM5176 CS nodes are. The undecided nets whose working voltage the "
  "circuit states are declared nodes at it (D: HS1_MIC, HS2_MIC, HS1_BIAS_R, HS2_BIAS_R, PTT_HS1_n, PTT_HS2_n, "
  "X_PTT_HS1_n, X_PTT_HS2_n, RF_ANT, FLANGE_AIN0, FLANGE_REF; E: WATER_SENSE). RLY_K, FAN1_SW and FAN2_SW stay "
  "UNDECIDED (" + SZ + ").",
  "The rule reports a node and refuses one that carries the supply pins of two or more parts: each net declared a node "
  "carries one part's own pins and their capacitors, and each value is its maker's (TI SLES230A 9.5.1.6, Table 6 and "
  "note 10; Silicon Labs CP2102N Rev. 1.5 Table 3.6; TI SLOS597B pin table, 6.1 and 7.2; LT8705A 8705af p.3; RP2040 "
  "2.10.3, Tables 192 and 634; Diodes DS41326 p.4), the charge pump's -1.9 V read from HPVDD's rating and the block "
  "diagram because TI publishes no HPVSS figure. SGP_VDD is not made inside a part, so it is a rail. The undecided nets "
  "are settled the way the rule's text says (declaring a node), as FLANGE_NTC already was, at voltages this generator "
  "already derived; a node declaration takes nothing out of the signal set RET-001 judges. The three left have a peak "
  "one flyback diode drop above their rail, and no sheet for D2, D7 or D8 is held. Reverse any node by a load on it that "
  "is another part's supply.",
  ["v2/ecad/tools/gen_sch_d.py and v2/ecad/tools/gen_sch_e.py (the declarations and their comments)",
   "v2/ecad/tools/intent_checks.py (PWR-001 on the netlist)", "v2/docs/handover/ENGINEERING-QUESTIONS.md EQ-19"]),
]
txt = ""
for cid, q, t, w, src in CHOICES:
    txt += "  - id: %s\n    authority: SESSION\n    under: standing-rule\n    taken_on: \"2026-09-27\"\n" % cid
    txt += block("question", q) + block("taken", t) + block("why", w)
    txt += "    source:\n" + "".join("      - \"%s\"\n" % x for x in src)
anchor = "\n# What is still open. SESSION items are engineering"
once(anchor); s = s.replace(anchor, "\n" + txt.rstrip("\n") + "\n" + anchor, 1)

# ---------------------------------------------------------------------------------------------------------- 2. open items
ITEMS = [
 (SX, "What is still in flight of EQ-16 (" + SCA + ") after its two schematic halves landed in ONE integration: board "
      "A's (J_VR1 to J_VR4, J_VN1 to J_VN4, J_DOCK pins 1 to 4 to GND, VIN_RAW's source and its declared 14.10 A under "
      "R8E-N01; drafts/w3de/a-half/, regenerated on the KiCad box with parity) and board E's (gen_sch_e.py: J_BLK pins "
      "1 to 4 to GND, P_VR, P_VN), with the IF-AE-DOCK contract and check_contracts.py's three dock checks from their "
      "drafts (patch_interfaces_if_ae_dock.py, patch_check_contracts_dock.py). "
      "They land together because board E's half alone reads the dock map DIFFERENT on pins 1 to 4 (A VIN_RAW, E GND), "
      "which would commit board A's VIN_RAW joined to board E's GND across four 813 contacts; with both "
      "check_contracts.py read PASS 99 of 99 in w3de's scratch tree. Still in flight: E5 (eight Mill-Max targets, two 12 "
      "AWG holes, the pours and the block's outline, the layer 7 question the decision rests on), board A's placement of "
      "J_VR1 to J_VR4 and J_VN1 to J_VN4 over E5's targets (gen_pcb_a3.py), board E's placement of P_VR and P_VN "
      "(patch_gen_pcb_e3.py leaves a marker that stops it until they are chosen), ASSEMBLY.md's block lead rows and build "
      "step 2 (patch_assembly_dock.py, with E5's holes), and v2/docs/ARCHITECTURE.md, whose "
      "IF-AE-DOCK lines (the E5 arrow, the VIN_RAW row of its current table and the interface table's row) still "
      "describe four VIN_RAW contacts at 12.31 A (drafts/w3de/EQ16-dock-vin-raw.md section 4)."),
 (SY, "Finding W3DE-DOCK-R1: the dock's ground current (VIN_RAW's return and the pack's) shares the Mill-Max return pins "
      "and the Preci-Dip 813 ground contacts in the ratio of the two groups' resistances, which the makers bound only from "
      "above. As drawn before EQ-16, with the Mill-Max pins at their 20 mOhm maximum, an 813 ground contact carries 3.06 A "
      "at 24.1 A of ground current and 4.08 A at 32.1 A (88 and 117 percent of 3.5 A); with EQ-16 1.57 and 2.09 A, 2.24 A "
      "with one open (drafts/w3de/dock_contacts.py). The residual: at the +55 C margin with the 32.1 A peak and the "
      "Mill-Max pins at their maximum, an 813 ground contact reaches 86 to 90 C on the assumed 60 K rise at 3.5 A, over "
      "its 85 C. Owed to TEST-PLAN.md: each contact group's resistance and one 813 ground contact's temperature at the "
      "declared currents."),
 (SZ, "PWR-001 reads INCONCLUSIVE on board D (RLY_K, the T/R relay coil's switched return) and board E (FAN1_SW and "
      "FAN2_SW, the mixer fans' switched returns) after " + SCC + ": each net's peak is one flyback diode drop above its "
      "rail (+5V_TX, CELL_F), and no maker's sheet for the diodes is held: D2 is a 1N4148W with no order code in "
      "gen_sch_d.py or lcsc_fill.py, D7 and D8 are SS14 filled as C51897884 by lcsc_fill.py with no sheet in v2/vendor. "
      "Open until the sheets are filed (and D2 has an order code, EQ-21's class) and the three nets are declared nodes "
      "at the rail plus the maker's forward drop."),
]
txt = ""
for iid, title in ITEMS:
    txt += "  - id: %s\n    class: SESSION\n    status: OPEN\n" % iid + block("title", title)
anchor = "\n# Items that left the open list, and what closed each"
once(anchor); s = s.replace(anchor, "\n" + txt.rstrip("\n") + "\n" + anchor, 1)

# ---------------------------------------------------------------------------------------------------------- 3. S-47
old = "      GND with the FBIN loop (E.md section 6.1 item 9) and the Schottky boost diodes (item 10).\n"
once(old)
add = ("Progress, 27 September 2026 (board D and E stream w3de): gen_sch_e.py carries the bottom-leg sense (the node TRK_CS, "
       "R5 from it to GND, R6 and R7 from R5's two pads, L1 from TRK_SW1 to TRK_SW2), GATEVCC's C63, the four supply-pin "
       "declarations and MODE on LDO33 (" + SCB + "), regenerated with parity, and boards/e.json's two TRK_LSENSE entries "
       "follow (the switching pre-lay group takes TRK_CS in TRK_LSENSE's place, a switching conductor as board A's LM5176 "
       "CS nodes are under F-PR-04). Still open: the drafted knock-ons in pcb_sensitive.yaml (board e's switch list, "
       "TRK_CS for TRK_LSENSE, and Kelvin rows) and "
       "gen_pcb_e3.py (PATTERNS, the TRKS region, drafts/w3de/), and item 10, the boost diodes (a silicon part with its "
       "sheet and order code, or the BAT54's own sheet read against 8705af p.29).")
s = s.replace(old, old + fold(add, 6) + "\n", 1)

# ---------------------------------------------------------------------------------------------------------- 4. rebinding
NEW = {"v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net": ("0dad82b4b6a79290", "76700a687eb6187f"),
       "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net": ("f3c1ad6153002976", "d6137f50059e5cbc"),
       "v2/ecad/tools/gen_sch_e.py": ("f275102965fafa10", "59abd6365b94c2d6"),
       "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net": ("3a786cf31614fe63", "0de3984133fc3f34"),
       "v2/ecad/tools/gen_sch_a.py": ("5a97fed72c42b79d", "3342e3be0ba560bb")}
DIFF_D = ("board D's netlist, regenerated by w3de on 27 September 2026 (gen_sch_d.py changed in its intent declarations "
          "and comments only), is identical to the file at 0dad82b4b6a79290 in every component and every net's pins "
          "(drafts/w3de/net_compare.py; regen_compare.py pair netlist PARITY_AFTER_NOISE)")
DIFF_E = ("board E's netlist, regenerated by w3de on 27 September 2026, differs from the file at f3c1ad6153002976 only in "
          "C63, C64, P_VR and P_VN added, J_BLK's value and its pins 1 to 4 (VIN_RAW to GND), the tracker's bottom-leg "
          "sense (Q4 and Q5 pins 1 to 3 GND to TRK_CS, R5 TRK_LSENSE/TRK_SW2 to TRK_CS/GND, R6 pin 1 to TRK_CS, R7 pin 1 "
          "to GND, L1 pin 2 to TRK_SW2, the net TRK_LSENSE gone) and U5 pin 37 (GND to TRK_LDO33), every component and "
          "every net's pins compared (drafts/w3de/net_compare.py against drafts/w3de/parity/expected-e-netlist.json)")
DIFF_A = ("board A's half of EQ-16, landed with board E's in one integration: gen_sch_a.py changed only by "
          "drafts/w3de/patch_gen_sch_a_dock.py (three comment lines before _VIN_RAW_A, which becomes board E's 14.10 A "
          "under R8E-N01; VIN_RAW's source J_VR1 to J_VR4 and its note; J_VR1 to J_VR4 and J_VN1 to J_VN4 with their "
          "comment, fourteen lines after R1; J_DOCK's value and pins 1 to 4; the section list), so main's lines 67 to 210 "
          "move down by 3 and every line after 210 by 17; and board A's netlist, regenerated from it on the KiCad box with "
          "main's chain (handover_exports.py regen, whose run on main's own extraction reproduced main's committed files), "
          "differs from the file at 3a786cf31614fe63 only in J_VR1 to J_VR4 (VIN_RAW) and J_VN1 to J_VN4 (GND) added and "
          "J_DOCK's value and pins 1 to 4 (VIN_RAW to GND), every component and every net's pins compared "
          "(drafts/w3de/net_compare.py against drafts/w3de/parity/expected-a-netlist.json)")
REBIND = {
 "CON-019": (DIFF_D + "; and " + DIFF_A, "U14, U18, R48, TR_APRS, KEY and PA_EN on board D are among the unchanged, and "
                                       "on board A U30, U26, OUTLET_OK, POE_EN, PD_EN, U16, U19 and PA_EN (U36's output) "
                                       "are unchanged in the netlist and their lines unchanged in the generator, now "
                                       "gen_sch_a.py:1194-1207 and 1254-1262 (the record's source follows)"),
 "CON-018": (DIFF_A, "U31 (TPD2E2U06QDBZRQ1) on PD_CC1 and PD_CC2 at J_USBC_OUT, and C96 and C97, are unchanged in the "
                     "netlist, and U31's lines are unchanged in the generator, now gen_sch_a.py:1121-1131 (the record's "
                     "source follows)"),
 "CFL-005": (DIFF_A, "R102 (EMCON_HW to GND), R145 on TX_INHIBIT_n and the slot enable pull-downs are unchanged in the "
                     "netlist; R102's line is now gen_sch_a.py:1270 (the record's source follows)"),
 "CFL-014": (DIFF_A, "the strap R26 and R27 from CH_VDDA, R17 from VBAT to CELL_FUSED and F1 from CELL_FUSED to CELL+ "
                     "are unchanged in the netlist, the generator's lines 18 to 48 are byte-identical and the strap's "
                     "lines are unchanged, now gen_sch_a.py:856-862 (the record's source follows); VIN_RAW is not a "
                     "conductor of the charger or pack path this record reads"),
 "CFL-002": (DIFF_E, "U17 (the SGP41), its supply network (R57, C57, C58) and SDA1 and SCL1 are unchanged in the netlist; "
                     "the intent now declares SGP_VDD a rail (" + SCC + "), and U17's statement in the generator is unchanged"),
 "CON-010": (DIFF_D, "U12, U13, U14, U15 and their nets are among the unchanged"),
 "REQ-036": (DIFF_E, "J_TAMP, R52, R53, C52, TAMPER_LEAD, TAMPER_IO and U12's CELL_F pins are unchanged, and no board routes "
                     "the lead to ZEROIZE_HW or the panel controller"),
 "CFL-016": (DIFF_D + "; and " + DIFF_E + "; and " + DIFF_A,
             "none of the parts or nets this record cites on boards A, D and E is among the changes (on board A the "
             "startup enables, the outlet interlock U30 and U26 and the wall data path J_USBW are unchanged)"),
 "CFL-013": (DIFF_E, "DCF_PULSE still runs from J_DCF pin 3 to U10 and nowhere else"),
 "CFL-015": (DIFF_E, "J_SMB and its four nets are unchanged"),
 "CON-016": (DIFF_D + "; and " + DIFF_E, "board E's D1 to D4 and D10 and board D's D1 are unchanged"),
}
# the `source` lines that cite gen_sch_a.py by line follow the lines patch_gen_sch_a_dock.py moved (each block was
# found by its content in the patched file: 1104-1114 -> 1121-1131, 1177-1190 -> 1194-1207, 1237-1245 -> 1254-1262,
# 1253 -> 1270, 839-845 -> 856-862)
SOURCE_LINES = {
 "CON-018": [('"v2/ecad/tools/gen_sch_a.py:1104-1114"', '"v2/ecad/tools/gen_sch_a.py:1121-1131"')],
 "CON-019": [('"v2/ecad/tools/gen_sch_a.py:1177-1190, 1237-1245"', '"v2/ecad/tools/gen_sch_a.py:1194-1207, 1254-1262"')],
 "CFL-005": [('"v2/ecad/tools/gen_sch_a.py:1253"', '"v2/ecad/tools/gen_sch_a.py:1270"')],
 "CFL-014": [('"v2/ecad/tools/gen_sch_a.py:839-845"', '"v2/ecad/tools/gen_sch_a.py:856-862"')],
}
if "--no-rebind" not in sys.argv:
    for path, (old16, new16) in NEW.items():
        have = hashlib.sha256(open(os.path.join(ROOT, path), "rb").read()).hexdigest()[:16]
        if have != new16:
            raise SystemExit("apply_registry: %s is at %s in this tree, not the %s w3de regenerated and compared; install "
                             "w3de's files and board A's half (drafts/w3de/a-half/install_a_half.py) first, or pass "
                             "--no-rebind" % (path, have, new16))
    for rid, (diff, same) in REBIND.items():
        start = s.find("\n  - id: %s\n" % rid)
        if start < 0: raise SystemExit("apply_registry: record %s is not in this tree" % rid)
        end = s.find("\n  - id: ", start + 1); end = len(s) if end < 0 else end
        rec = s[start:end]
        if rec.count("    evidence_bound_to:\n") != 1: raise SystemExit("apply_registry: %s has no single evidence_bound_to" % rid)
        new_rec = rec
        touched = []
        for path, (old16, new16) in NEW.items():
            b = "%s@%s" % (path, old16)
            if b in new_rec: new_rec = new_rec.replace(b, "%s@%s" % (path, new16)); touched.append("%s@%s" % (path, new16))
        if not touched: raise SystemExit("apply_registry: %s carries none of the bindings w3de expected" % rid)
        line = ("re-read at the w3de regeneration of 27 September 2026 (boards D and E, MESHSAT-1357): %s; %s, so this "
                "reading stands on %s" % (diff, same, ", ".join(touched)))
        new_rec = new_rec.replace("    evidence_bound_to:\n", "      - >-\n" + fold(line, 10) + "\n    evidence_bound_to:\n", 1)
        for old_src, new_src in SOURCE_LINES.get(rid, []):
            if new_rec.count(old_src) != 1: raise SystemExit("apply_registry: %s's source %r is not there exactly once" % (rid, old_src))
            new_rec = new_rec.replace(old_src, new_src)
        s = s[:start] + new_rec + s[end:]

    # 4b. CFL-015 reads two files w3de's OTHER drafts change: ASSEMBLY.md (patch_assembly_dock.py: the block lead rows,
    # build step 2 and the fitting lists) and check_contracts.py (patch_check_contracts_dock.py: section 5a). The record
    # cites neither change: it reads the Pack SMBus row and build step 7 of ASSEMBLY.md and check_contracts.py's J_SMB
    # contract. It is rebound to the tree's file only when that file changed AND the texts it cites are byte-identical to
    # main's at 38dcd764 (their sha256/16 below: every ASSEMBLY.md line starting "| Pack SMBus |" or "7. Pack into the
    # east pocket", and every check_contracts.py line naming J_SMB, joined by newlines).
    CITED = {"v2/docs/ASSEMBLY.md": ("30db27eee509212c", "7bd43d0d0782fbf2",
                                     lambda t: "\n".join(l for l in t.splitlines() if l.startswith("| Pack SMBus |")
                                                         or l.startswith("7. Pack into the east pocket")),
                                     "the Pack SMBus row and build step 7"),
             "v2/ecad/tools/check_contracts.py": ("308fdefb90335da4", "190e894f7bddf508",
                                                  lambda t: "\n".join(l for l in t.splitlines() if "J_SMB" in l),
                                                  "the J_SMB contract (every line naming J_SMB)")}
    start = s.find("\n  - id: CFL-015\n"); end = s.find("\n  - id: ", start + 1); end = len(s) if end < 0 else end
    rec = s[start:end]; notes = []
    for path, (old16, cited16, pick, what) in CITED.items():
        t = open(os.path.join(ROOT, path), encoding="utf-8").read()
        have = hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]
        if have == old16 or ("%s@%s" % (path, old16)) not in rec: continue
        if hashlib.sha256(pick(t).encode("utf-8")).hexdigest()[:16] != cited16:
            raise SystemExit("apply_registry: CFL-015 reads %s of %s, and that text changed: re-read it by hand" % (what, path))
        rec = rec.replace("%s@%s" % (path, old16), "%s@%s" % (path, have))
        notes.append("%s changed (w3de's EQ-16 drafts or another stream) and %s is byte-identical to main's at 38dcd764, "
                     "so this reading stands on %s@%s" % (path, what, path, have))
    if notes:
        rec = rec.replace("    evidence_bound_to:\n", "      - >-\n" + fold("re-read on 27 September 2026 (w3de): " +
                                                                           "; ".join(notes), 10) + "\n    evidence_bound_to:\n", 1)
        s = s[:start] + rec + s[end:]

assert s != orig
import yaml; yaml.safe_load(s)
open(REG, "w", encoding="utf-8").write(s)
print("apply_registry: %s: %s, %s, %s added; %s, %s, %s opened; S-47 updated; %s" %
      (REG, SCA, SCB, SCC, SX, SY, SZ, "rebinding skipped" if "--no-rebind" in sys.argv else "%d records rebound" % len(REBIND)))
