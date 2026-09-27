#!/usr/bin/env python3
"""DRAFT registry changes of stream w4dp (boards D and P and the pack-protection table; MESHSAT-1357, 27 September 2026),
for the integrator.

Applied to v2/ecad/tools/pcb_requirements.yaml of the tree named on the command line, by record id, with every edited text
asserted first; it takes the NEXT FREE SC-nn and S-nn in that tree, so it composes with other streams' drafts (fnd/rel2
adds records too).

  1. three session choices (under the owner's standing rule of 26 September 2026):
       SC-a  board D's D2: the 1N4148W the order code names, its maker's sheet filed (S-76's order-code half);
       SC-b  PWR-001's kinds on board D (RLY_K) and board P (BAT_F, VCC_F, SEC_VDD, SW, SCP_HTR as rails; PBI, CELL1 to
             CELL3, FUSE_G, FUSE_GQ as nodes);
       SC-c  BAT-001's table brought to the drawn circuit, its hardware level judged against the cell maker's limits with
             the requirement's words kept literal;
  2. two open items: S-x BAT-001's hardware level misses the cell maker's limits on three functions (W4DP-F1 under-voltage,
     BAT-F16 over-temperature, W4DP-F2 over-current); S-y the documents that cite pcb_pack_protection.yaml by line or
     describe its old F1 and R10 rows, and pcb_energy_chain.yaml's F1 figures (BAT-F04's other half);
  3. S-45 closed by SC-c; S-76's board D half recorded as done (S-76 stays OPEN for board E's FAN1_SW and FAN2_SW);
  4. REQ-044 and FEA-005 wait on S-x instead of the closed S-45; REQ-044's and REQ-046's `source` lines follow the lines
     the table (and, with the TEST-PLAN draft, TEST-PLAN.md) moved;
  5. the records bound to board D's or P's netlist, gen_sch_p.py, pcb_pack_protection.yaml and (only when
     drafts/w4dp/patch_test_plan.py has been applied) TEST-PLAN.md are re-read against the regenerated files and rebound,
     each with an evidence line naming what changed and that what it cites did not. The rebinding happens only when the
     tree holds exactly the files w4dp regenerated (their sha256/16 asserted below); otherwise the script refuses.

Usage: apply_registry.py <tree root holding v2/ecad> [--no-rebind]
Order: w4dp's files, then drafts/w4dp/patch_test_plan.py, then this, then rules_lib.py requirements and
rules_render.py --requirements."""
import os, re, sys, hashlib, textwrap

ROOT = sys.argv[1]
REG = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_requirements.yaml")
s = open(REG, encoding="utf-8").read(); orig = s


def once(old, where=None):
    t = s if where is None else where
    n = t.count(old)
    if n != 1: raise SystemExit("apply_registry: expected exactly one %r, found %d" % (old[:90], n))


def next_id(prefix):
    ids = [int(m) for m in re.findall(r"^  - id: %s-(\d+)$" % prefix, s, re.M)]
    return max(ids) + 1 if ids else 1


def fold(text, indent):
    pad = " " * indent
    return "\n".join(textwrap.wrap(" ".join(text.split()), width=118 - indent, initial_indent=pad, subsequent_indent=pad,
                                   break_long_words=False, break_on_hyphens=False))


def block(key, text, indent=4):
    return " " * indent + key + ": >-\n" + fold(text, indent + 2) + "\n"


def sha16(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:16]


sc = next_id("SC"); sn = next_id("S")
SCA, SCB, SCC = ["SC-%02d" % (sc + k) for k in range(3)]
SX, SY = ["S-%02d" % (sn + k) for k in range(2)]
TEST_PLAN = "v2/docs/TEST-PLAN.md"
TP_OLD, TP_NEW = "701c1020053e7903", "5ccadd6607a87df4"      # main's, and main's with drafts/w4dp/patch_test_plan.py applied
tp_patched = sha16(TEST_PLAN) == TP_NEW
if not tp_patched and sha16(TEST_PLAN) != TP_OLD:
    raise SystemExit("apply_registry: %s is at %s, neither main's %s nor main's with patch_test_plan.py (%s); read it "
                     "again before rebinding" % (TEST_PLAN, sha16(TEST_PLAN), TP_OLD, TP_NEW))

# ---------------------------------------------------------------------------------------------------------- 1. choices
CHOICES = [
 (SCA,
  "Which part is board D's relay flyback diode D2, whose schematic line named the class '1N4148W' with no order code and "
  "no maker (S-76; EQ-21's class)?",
  "LCSC C81598: the 1N4148W of SEMTECH ELECTRONICS LTD. (LCSC's brand 'ST(Semtech)', not Semtech Corporation), SOD-123, a "
  "JLC basic part (JLC API 2026-09-27: stock 5,220,610), the code lcsc_fill.py already filled and jlc_certify.py's "
  "order table lists for the same (Comment, Footprint) row, a dated reading of JLC's catalogue of 26 September 2026. gen_sch_d.py "
  "carries the code on D2's line; the "
  "maker's sheet as LCSC serves it (Rev 05, 20/09/2016, sha256 54de8e40, the file v2/docs/parts/grade-sources.yaml read) "
  "is filed as v2/vendor/power/st-semtech-1n4148w-c81598.pdf. The value text is unchanged, so no pin, net or land moves.",
  "A class name orders whatever a fill decides; the code that fill already chose is in JLC's catalogue reading, in stock "
  "and on the land the schematic draws (the sheet's pinning table: pin 1 cathode, pin 2 anode, SOD-123, which is KiCad's "
  "Diode:1N4148W "
  "and D_SOD-123), and its ratings (VR 75 V, IF(AV) 150 mA, IFSM 1 A for 1 ms, VF 1.0 V at 50 mA and 1.25 V at 150 mA) "
  "cover a 5 V relay coil's release at about 30 mA with room. Reverse by a Diodes Incorporated or other maker's part "
  "whose sheet this tree already holds, if the ordering session prefers one.",
  ["v2/ecad/tools/gen_sch_d.py (D2's line and its comment)", "v2/vendor/power/st-semtech-1n4148w-c81598.pdf",
   "v2/release/revA/order/JLC-CERTIFIED.tsv (row '1N4148W coil flyback', D_SOD-123, C81598)",
   "v2/docs/parts/grade-sources.yaml (C81598)"]),
 (SCB,
  "Which kind does each supply PWR-001 left on board D (RLY_K, UNDECIDED) and board P (BAT_F, PBI, SEC_VDD, SW and VCC_F "
  "undeclared; CELL1 to CELL3, FUSE_G, FUSE_GQ and SCP_HTR undecided) take (EQ-19)?",
  "Board D: RLY_K, the relay coil's switched low end, a node at 6.5 V (+5V_TX's 5.23 V plus D2's 1.25 V maximum forward "
  "drop at 150 mA, SC-a's sheet; v_work 5.23 V). Board P: rails for the supply branches fed through board parts, BAT_F "
  "(the gauge's primary supply behind R5 from CELL4, 336 uA, always on), VCC_F (its secondary supply behind R7 from "
  "PACK_P, 0 A typical and 336 uA peak, switched with PACK_P by the gauge's DSG drive), SEC_VDD (the second level's VDD "
  "behind R23 from CELL4, 3.5 uA typical and 0.18 mA peak with its outputs driving, always on), SW (the protection FETs' "
  "common drain, 10 A and 18 A, a series segment of SCP_OUT) and SCP_HTR (the chemical fuse's heater return, 3.5 A "
  "declared typical and peak because the event lasts up to 60 s, switched by Q3 on FUSE_GQ); nodes for the gauge's own "
  "backup reservoir PBI (16.8 V), the cell taps CELL1 to CELL3 (4.375 V a cell, 4.20 V in service) and the fuse gate "
  "drive FUSE_G and FUSE_GQ (7.7 and 7.6 V bounds, set by the gauge's FUSE output at its 8.65 V maximum through its "
  "2 kohm minimum impedance and R30 into R31, or R31 || R32 once JP1 is closed, 7.61 and 7.56 V with 1 percent "
  "resistors at their worst; 4.25 V with COUT driving). Nothing electrical changes on board P.",
  "The rule's text: a rail where a part is fed through a board part (as SC-57 took board E's SGP_VDD), a node where it "
  "is a part's own supply, a tap or a switch's current path; every figure is the maker's (TI SLUSC67B pin table, 6.3, "
  "6.5, 6.6, 6.20, 8.2.2.2.2; TI SLUSEG7D 12-Pin Functions, Device Comparison Table, 6.5; Eaton ELX1135; Omron G6K "
  "5 VDC coil row; SEMTECH 1N4148W; SLUSEG7D 7.3.6 and 8.2 for the fuse gate). SCP_HTR is a rail rather than a node so that PI-001 and PI-003 judge the heater "
  "path's copper at its 3.5 A: a path that must stay intact until F2 opens is the one current on board P whose loss "
  "defeats a protection. The fuse gate's bound takes COUT as what TI names it, the Active High 6V option's 'active "
  "HIGH with drive to 6V' (SLUSEG7D 7.3.6; 8.2 drives FET gates with it directly; 6.5 gives 6 V minimum at 100 uA and "
  "no maximum), not its VDD, which is the separate Active High VDD option: the node is a weighted mean of the gauge's "
  "branch and COUT's, so it stays under 7.7 and 7.6 V for any COUT high level up to 7.6 V, and Q3's gate under the "
  "AO3400A's +-12 V VGS with 4.4 V to spare. A VDD basis would have been wrong in the state that drives COUT: an "
  "over-voltage holds a cell above 4.325 V, the stack at about 17.3 to 17.5 V, and COUT at that VDD would put FUSE_GQ "
  "at 12.25 to 12.4 V, past Q3's rating. Reverse the fuse gate's bound by a TI maximum for the 6V drive above 7.6 V, or a "
  "bench reading of that output above it (TP11 with COUT driving, or TP12, DOUT's identical stage); Q3's gate rating "
  "would then need a clamp, a circuit change for the qualified battery review. Board P's protection circuit is frozen in front of the qualified battery review, so the intent file is "
  "the only file that moves. Reverse any node by a load on it that is another part's supply, and SCP_HTR's typical by a "
  "tool that judges an event current as such.",
  ["v2/ecad/tools/gen_sch_d.py (RLY_K)", "v2/ecad/tools/gen_sch_p.py (the PWR-001 block before the bypass entries)",
   "v2/ecad/tools/intent_checks.py (PWR-001 on the netlist)", "v2/docs/handover/ENGINEERING-QUESTIONS.md EQ-19",
   "v2/vendor/battery/ti-bq77207.pdf (SLUSEG7D Device Comparison Table, 6.5 VOUT_AH, 7.3.6, 8.2)",
   "v2/vendor/battery/ti-bq4050.pdf (SLUSC67B 6.20, FUSE drive)"]),
 (SCC,
  "How does BAT-001's table describe board P as generated (S-45), and against what are the parts that act without "
  "firmware judged?",
  "pcb_pack_protection.yaml declares decision 40's floor present and names its parts (U2, F2, Q3, JP1, Q5, RT1, J_TS2, "
  "F1), each in `devices` and on board P's netlist, and tests/test_pack_protection.py holds the declaration to the "
  "netlist's connections both ways. The F1 row is the 25 A MINI blade (Littelfuse 297) the Keystone 3568 holds, not the "
  "ATOF (BAT-F04), and R10's row is the shunt it is, the thermistors moving to J_TS. BAT-001's five functions are judged "
  "a second time on those parts, as rows with `level: hardware`, against the same cell limits as the gauge's rows: "
  "over-voltage (U2, 4.325 V against 4.20 V with a 0.175 V allowance that keeps it above the gauge's 4.25 V) and short "
  "circuit (F1, 150 A against a 240 A lowest prospective fault) pass; under-voltage (U2, 2.25 V against the guideline's "
  "2.30 V), over-temperature (U2, 70 C and no cold trip against -10 to 60 C) and over-current (F1, 33.75 A against 24 A "
  "at 3P) fail, each naming its finding (" + SX + "). The gauge's nine rows are byte-identical. BAT-F20 stays open on "
  "Q1's row.",
  "The requirement asks for all five in hardware, independent of any software, with the trip points set from the cell "
  "maker's own limits; it does not relax the limit for a second level, and reading it as 'a protector independent of the "
  "gauge exists' would lower it (the handover prompt's section 2). THERMAL-COORDINATION.md section 8 already names "
  "BAT-001's words as the reversal of the session's choice not to add a hold now (S-45), so the table keeps them "
  "literal and the gate reads FAIL for what the circuit does not do, where it read FAIL for what the table no longer "
  "said. Reverse by an owner ruling that restates BAT-001 for a second level (the rule is the owner's, pcb_rules.yaml), "
  "or by the circuit changes of " + SX + ".",
  ["v2/ecad/tools/pcb_pack_protection.yaml", "v2/ecad/tools/tests/test_pack_protection.py",
   "v2/docs/review-packets/battery/PROTECTION-ARCHITECTURE.md sections 2, 3, 6 and 8",
   "v2/docs/review-packets/battery/THERMAL-COORDINATION.md section 8",
   "v2/docs/review-packets/battery/FUSE-INTERPRETATION.md section 3 (BAT-F04)",
   "v2/vendor/battery/ti-bq77207.pdf (SLUSEG7D Device Comparison Table, 6.5, 6.6)",
   "v2/vendor/keystone/littelfuse-297-ficcorp.pdf (time-current table)",
   "v2/vendor/battery/samsung-35e-orbtronic.pdf (3.8, 3.12, Pack Design Guideline)"]),
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
 (SX, "BAT-001's hardware level misses the cell maker's limits on three of its five functions (" + SCC + "; "
      "pack_protection on board P as generated reads FAIL, 3 of 63 checks, each a `level: hardware` row): (1) W4DP-F1, "
      "the BQ7720700's under-voltage, 2.25 V +-50 mV, is up to 100 mV below the Samsung Pack Design Guideline's 2.30 V "
      "'min. voltage of over-discharging protection' (the only released variant whose over-voltage clears the gauge's "
      "4.25 V); (2) BAT-F16, its fixed 70 C over-temperature (62.7 to 77.5 C at its network, no cold trip) acts only "
      "above the cells' 60 C and 45 C limits (THERMAL-COORDINATION.md section 8; S-58 and Q-P15 carry the hold that "
      "would meet it); (3) W4DP-F2, no element that acts without firmware opens at or below the cells' 24 A at 3P (the "
      "gauge's AFE comparators take their thresholds from data flash; F1 opens from 33.75 A in up to 600 s, F2 is 30 A). "
      "Options: a custom BQ77207xy at 4.325 V and 2.35 V (TI, 'contact TI': an outside contact, the owner's); a 4S "
      "protector with fixed under-voltage at or above 2.30 V and a fixed discharge over-current on the shunt; the "
      "comparator hold of THERMAL-COORDINATION.md section 8 at 57.5 C and 44.0 C; or the owner restating BAT-001 for a "
      "second level. Recommendation: put (1) and (3) to the qualified battery reviewer beside Q-P15, since the circuit "
      "is frozen in front of that review, and specify the chosen circuit at board P's four-layer regeneration (O-11). "
      "BAT-001 on board P reads FAIL until each is answered."),
 (SY, "Documents that cite pcb_pack_protection.yaml by line, or describe the rows " + SCC + " corrected, now point at "
      "other text: the battery packet (SECONDARY-OT-DECISION.md ':142-158', PRIMARY-CONFIGURATION.md ':51-65', ':54' and "
      "':55', PROTECTION-ARCHITECTURE.md ':51-65' and ':125-132', FUSE-INTERPRETATION.md ':74' and its BAT-F04 paragraph, "
      "THERMAL-COORDINATION.md's 'R10 row') and its manifest if those files are edited. At w4dp the old lines map to: "
      "51-65 (the limits) to 78-92, 54 to 81, 55 to 82, 74 (F1) to 109-117, 125-132 (PACK_SHORT_CIRCUIT_DISCHARGE) to "
      "198-205, 142-158 (CHARGE_ and DISCHARGE_TEMPERATURE_WINDOW) to 215-231, and the R10 row's thermistors to the J_TS "
      "row. BAT-F04's other half is open too: pcb_energy_chain.yaml "
      "(stages PACK_CELLS, PACK_LEAD, DOCK_ENTRY and board A's fuse) still gives F1 the Littelfuse 287 ATOF figures "
      "(I2t 1000 A2s) where the Keystone 3568 holds the 297 MINI (625 A2s typical). For the packet's owner and the energy "
      "chain's owner."),
]
txt = ""
for iid, title in ITEMS:
    txt += "  - id: %s\n    class: SESSION\n    status: OPEN\n" % iid + block("title", title)
anchor = "\n# Items that left the open list, and what closed each"
once(anchor); s = s.replace(anchor, "\n" + txt.rstrip("\n") + "\n" + anchor, 1)

# ---------------------------------------------------------------------------------------------------------- 3. S-45, S-76
S45 = ("  - id: S-45\n    class: SESSION\n    status: OPEN\n    title: >-\n"
       "      BAT-001's instrument brought to board P as generated: pack_protection still reads FAIL on the regenerated board\n"
       "      P (\"no second protector and no chemical fuse\", battery packet evidence gates-new/pack_protection.log), because\n"
       "      its inputs describe the old pack.\n")
once(S45); s = s.replace(S45, "", 1)
closed = ("  - id: S-45\n    closed_by: %s\n" % SCC
          + block("closing_evidence",
                  "v2/ecad/tools/pcb_pack_protection.yaml at w4dp (27 September 2026) declares decision 40's floor present "
                  "with its parts, each on board P's netlist, and tests/test_pack_protection.py holds the declaration to the "
                  "netlist's connections both ways (the second level on the taps, COUT and FUSE at the fuse gate, JP1, Q3 on "
                  "F2's heater, F2 in the cell path, Q5 on Q2's gate, RT1 with PTCEN on BAT). pack_protection re-taken in "
                  "scratch on board P as regenerated reads FAIL, 3 of 63 checks, and every failure is a hardware row's "
                  "(" + SX + "); no failure says the floor is absent.")
          + "    title: >-\n"
            "      BAT-001's instrument brought to board P as generated: pack_protection still reads FAIL on the regenerated board\n"
            "      P (\"no second protector and no chemical fuse\", battery packet evidence gates-new/pack_protection.log), because\n"
            "      its inputs describe the old pack.\n")
anchor = "\nrecords:\n"          # the closed list ends with a blank line before `records:`, which stays after S-45
once(anchor); s = s.replace(anchor, closed + anchor, 1)

old76 = ("      sheet in v2/vendor. Open until the sheets are filed (and D2 has an order code, EQ-21's class) and the\n"
         "      three nets are declared nodes at the rail plus the maker's forward drop.\n")
once(old76)
add76 = ("Progress, 27 September 2026 (stream w4dp): board D's half is done. D2 carries LCSC C81598, SEMTECH ELECTRONICS' "
         "1N4148W, with its sheet filed as v2/vendor/power/st-semtech-1n4148w-c81598.pdf (" + SCA + "), and RLY_K is a "
         "declared node at 6.5 V (" + SCB + "); PWR-001 on board D as regenerated reads PASS in scratch. Still open: board "
         "E's FAN1_SW and FAN2_SW (D7 and D8, SS14 C51897884, no sheet in v2/vendor).")
s = s.replace(old76, old76 + fold(add76, 6) + "\n", 1)

# ---------------------------------------------------------------------------------------------------------- 4. waits_on, source lines
def edit_record(rid, pairs):
    global s
    start = s.find("\n  - id: %s\n" % rid)
    if start < 0: raise SystemExit("apply_registry: record %s is not in this tree" % rid)
    end = s.find("\n  - id: ", start + 1); end = len(s) if end < 0 else end
    rec = s[start:end]
    for old, new in pairs:
        once(old, rec); rec = rec.replace(old, new, 1)
    s = s[:start] + rec + s[end:]

edit_record("REQ-044", [("    waits_on: [S-45, L-03]\n", "    waits_on: [%s, L-03]\n" % SX),
                        ('      - "v2/ecad/tools/pcb_pack_protection.yaml:17-40"\n',
                         '      - "v2/ecad/tools/pcb_pack_protection.yaml:17-67"\n')]
            + ([('      - "v2/docs/TEST-PLAN.md:58-94"\n', '      - "v2/docs/TEST-PLAN.md:58-104"\n')] if tp_patched else []))
edit_record("FEA-005", [("    waits_on: [L-03, S-34, S-45, S-46]\n", "    waits_on: [L-03, S-34, S-46, %s]\n" % SX)])
edit_record("REQ-046", [('"v2/ecad/tools/pcb_pack_protection.yaml:142-157 (CHARGE_ and DISCHARGE_TEMPERATURE_WINDOW)"',
                         '"v2/ecad/tools/pcb_pack_protection.yaml:215-231 (CHARGE_ and DISCHARGE_TEMPERATURE_WINDOW)"')])

# ---------------------------------------------------------------------------------------------------------- 5. rebinding
NEW = {"v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net": ("76700a687eb6187f", "7a2c0ac2190b141a"),
       "v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net": ("085f833362fbbda8", "760ac6f74d62d194"),
       "v2/ecad/tools/gen_sch_p.py": ("91ccbb922c427d43", "740817ada5c8e14a"),
       "v2/ecad/tools/pcb_pack_protection.yaml": ("1cd670d6c7685645", "ab1dbc3f3f69aa46")}
if tp_patched: NEW[TEST_PLAN] = (TP_OLD, TP_NEW)
DIFF_D = ("board D's netlist, regenerated by w4dp on 27 September 2026 on the KiCad box with main's chain "
          "(handover_exports.py regen, PHASE D37P, whose run on main's own clone reproduced main's files), differs from "
          "the file at 76700a687eb6187f only in D2's LCSC field and property (C81598, SC-a), every component and every "
          "net's pins compared (drafts/w4dp/parity: w3de's net_compare.py against expected-d-netlist.json, 'ONLY THE "
          "EXPECTED CHANGES')")
DIFF_P = ("board P's netlist, regenerated by w4dp on 27 September 2026 the same way (PHASE P4; gen_sch_p.py changed in its "
          "intent declarations and comments only), is identical to the file at 085f833362fbbda8 in every component and "
          "every net's pins (content16 efe60479293f0004 on both; net_compare.py 'ONLY THE EXPECTED CHANGES' against an "
          "empty list)")
DIFF_GEN_P = ("gen_sch_p.py changed by w4dp only after the section list: a block of intent declarations (PWR-001, SC-b) "
              "before the bypass entries; every line up to 551, the part lines and the U2 section this reading cites among "
              "them, is byte-identical")
DIFF_TABLE = ("pcb_pack_protection.yaml changed by w4dp (SC-c): the header gains a paragraph, secondary_protection declares "
              "the floor, the devices F1, R10 and Q1 to Q2 are corrected or annotated and eight are added, and five "
              "`level: hardware` rows follow the gauge's; the pack block (topology, series, parallel counts, currents, "
              "lines 40 to 47), the cell block and the gauge's nine rows are byte-identical")
DIFF_TP = ("TEST-PLAN.md changed by drafts/w4dp/patch_test_plan.py only in section 5: rows 10 to 14 after row 9 and its "
           "closing paragraph's first two sentences and one clause restated; lines 1 to 81 are byte-identical and every "
           "later line moves down by 10 with its text unchanged")
REBIND = {
 "CON-019": ([DIFF_D], "U14, U18, R48, TR_APRS, KEY and PA_EN on board D are unchanged"),
 "CON-010": ([DIFF_D], "U12, U13, U14, U15 and their nets are unchanged"),
 "CON-016": ([DIFF_D, DIFF_P], "board D's D1 and board P's D1 are unchanged, and D2's pin 1, its cathode by the sheet SC-a "
                               "files, stays on +5V_TX"),
 "CFL-015": ([DIFF_P], "J_SMB and its four nets are unchanged"),
 "CFL-016": ([DIFF_D, DIFF_P] + ([DIFF_TP] if tp_patched else []),
             "none of the parts, nets or test-plan lines this record cites on boards D and P is among the changes"),
 "REQ-044": ([DIFF_P, DIFF_GEN_P],
             "the netlist clause holds as before; pack_protection re-taken in scratch on board P as regenerated reads FAIL, "
             "3 of 63 checks, on the hardware level's under-voltage, over-temperature and over-current rows (" + SX
             + "), and no longer on the floor's absence (S-45 closed by " + SCC + "); the qualified review of D-09 is still "
             "not engaged"),
 "CFL-006": ([DIFF_TABLE], "the 4S3P block of Samsung INR18650-35E, about 145 Wh, and the one parallel count 3 are the "
                           "same text"),
}
if tp_patched:
    for rid in ("CON-018", "REQ-050", "CFL-007", "CFL-008", "CFL-009"):
        REBIND[rid] = ([DIFF_TP], "the rows and sections this record cites (sections 1 to 4, rows E3 to E8, M7) are among "
                                  "the unchanged text, and every added row states its Purpose and the requirement it "
                                  "Verifies")

if "--no-rebind" not in sys.argv:
    for path, (old16, new16) in NEW.items():
        have = sha16(path)
        if have != new16:
            raise SystemExit("apply_registry: %s is at %s in this tree, not the %s w4dp regenerated and compared; install "
                             "w4dp's files first, or pass --no-rebind" % (path, have, new16))
    for rid, (diffs, same) in REBIND.items():
        start = s.find("\n  - id: %s\n" % rid)
        if start < 0: raise SystemExit("apply_registry: record %s is not in this tree" % rid)
        end = s.find("\n  - id: ", start + 1); end = len(s) if end < 0 else end
        rec = s[start:end]
        if rec.count("    evidence_bound_to:\n") != 1: raise SystemExit("apply_registry: %s has no single evidence_bound_to" % rid)
        new_rec = rec; touched = []
        for path, (old16, new16) in NEW.items():
            b = "%s@%s" % (path, old16)
            if b in new_rec: new_rec = new_rec.replace(b, "%s@%s" % (path, new16)); touched.append("%s@%s" % (path, new16))
        if not touched: raise SystemExit("apply_registry: %s carries none of the bindings w4dp expected" % rid)
        line = ("re-read at the w4dp regeneration of 27 September 2026 (boards D and P and the pack-protection table, "
                "MESHSAT-1357): %s; %s, so this reading stands on %s" % ("; and ".join(diffs), same, ", ".join(touched)))
        new_rec = new_rec.replace("    evidence_bound_to:\n", "      - >-\n" + fold(line, 10) + "\n    evidence_bound_to:\n", 1)
        s = s[:start] + new_rec + s[end:]

assert s != orig
open(REG, "w", encoding="utf-8").write(s)
print("apply_registry: %s, %s, %s added; %s, %s opened; S-45 closed by %s; S-76 progress; %d record(s) rebound%s"
      % (SCA, SCB, SCC, SX, SY, SCC, 0 if "--no-rebind" in sys.argv else len(REBIND),
         " (TEST-PLAN.md with them)" if tp_patched else " (TEST-PLAN.md is main's: its records are not rebound)"))
