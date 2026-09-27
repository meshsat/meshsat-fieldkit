#!/usr/bin/env python3
"""r8int6 re-derivation of stream w4ae's apply_registry.py (beside it in this folder), written by derive_w4ae_r8int6.py with the independent check's corrections: REQ-077's detection time under FW-C14's 3 s rule, the MBRS140T3G quoted as far as its LCSC record states, and the line shift in gen_sch_a.py's note. The stream's text follows.

The registry half of stream w4ae (MESHSAT-1357, 27 September 2026): HOT-R1 drawn on boards A and E (S-57, SC-50,
REQ-077) and board E's half of S-76 (the fan flyback diodes' sheet and the FAN1_SW and FAN2_SW nodes).

Run LAST, from anywhere, on a tree that already holds (1) w4ae's own files (gen_sch_a.py, gen_sch_e.py, boards/a.json,
boards/e.json, the A and E schematic, netlist, provenance and intent files, v2/vendor/zhengxin/) and (2) this stream's
drafts filed under v2/docs/records/w4ae/ (hot_r1_trace.py is bound as evidence). It refuses a tree without them, by
content (the netlists must carry R216, Q11 and R58). It edits by record id with asserted old text, so it refuses a
registry whose text moved under it, and it is idempotent by a marker.

  1. Two session choices at the next free SC- numbers of the registry it runs on (another branch, fnd/rel2, adds
     choices too): SC-A, HOT-R1 as drawn and how H2 reaches PI_KILL (closes S-57); SC-B, D7 and D8's identity and the
     fan nodes (board E's half of S-76).
  2. S-57 leaves open_items for closed_items, closed by SC-A.
  3. S-76's title records board E's half answered by SC-B; board D's RLY_K and D2 stay open.
  4. REQ-077: waits_on loses S-57, choices gain SC-A, a desk reading of the committed netlists (the hop-by-hop trace) is
     added and the result goes FAIL to INCONCLUSIVE at SCHEMATIC (DESK_REVIEW, an AI desk review, not a qualified one):
     the desk acceptance's two parts hold, and FEA-004 (open) holds the record, so it cannot read PASS (rules_lib: a
     record an open feasibility blocks never reads PASS; the other held records read INCONCLUSIVE or NOT_JUDGED); it is
     rebound to gen_sch_e.py and newly bound to gen_sch_a.py, both netlists and the trace.
  5. The twelve other records bound to the changed files are re-read and rebound, each with the unchanged sections
     named (CON-010, CON-016, CON-018, CON-019, CFL-002, CFL-005, CFL-013, CFL-014, CFL-015, CFL-016, REQ-036, REQ-072).
Writes the ids it took to <ids.json> (second argument, default v2/docs/records/w4ae/ids.json) for edit_docs.py.

Taken by the session under the owner's standing rule of 26 September 2026; nothing here is the owner's.
Usage: apply_registry.py <tree root> [ids.json]"""
import hashlib, json, os, re, sys

ROOT = os.path.abspath(sys.argv[1])
IDS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "v2/docs/records/w4ae/ids.json")
sys.path.insert(0, os.path.join(ROOT, "v2", "docs", "records", "r8int5"))
import edlib
import yaml

REG = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_requirements.yaml")
MARK = "HOT-R1 as drawn on boards A and E (stream w4ae)"
t = open(REG, encoding="utf-8").read()
if MARK in t:
    raise SystemExit("apply_registry (w4ae): already applied")

A_NET, A_GEN = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "v2/ecad/tools/gen_sch_a.py"
E_NET, E_GEN = "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net", "v2/ecad/tools/gen_sch_e.py"
TRACE = "v2/docs/records/w4ae/hot_r1_trace.py"
SHEET = "v2/vendor/zhengxin/zhengxin-ss12-ss120-c51897884.pdf"


def sha16(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:16]


# ---- the tree must hold w4ae's files and its filed records
for rel in (A_NET, A_GEN, E_NET, E_GEN, TRACE, SHEET):
    if not os.path.exists(os.path.join(ROOT, rel)):
        raise SystemExit("apply_registry (w4ae): %s is not in the tree; install w4ae's files and file drafts/w4ae as "
                         "v2/docs/records/w4ae first" % rel)
an, en = open(os.path.join(ROOT, A_NET)).read(), open(os.path.join(ROOT, E_NET)).read()
for ref, txt, what in (("R216", an, "board A"), ("Q11", en, "board E"), ("R58", en, "board E")):
    if '(ref "%s")' % ref not in txt:
        raise SystemExit("apply_registry (w4ae): %s's netlist carries no %s: it is not w4ae's regenerated file" % (what, ref))
if '"HOT_R1_G"' not in en and "/HOT_R1_G" not in en:
    raise SystemExit("apply_registry (w4ae): board E's netlist has no HOT_R1_G net")
sha = {rel: sha16(rel) for rel in (A_NET, A_GEN, E_NET, E_GEN, TRACE)}


def next_free(prefix, text):
    return max(int(m) for m in re.findall(r"\n  - id: %s-(\d{2})\n" % prefix, text)) + 1


def wrap(text, indent=6, width=120):
    words = text.split(); lines = []; cur = " " * indent
    for w in words:
        if len(cur) + 1 + len(w) > width and cur.strip(): lines.append(cur); cur = " " * indent + w
        else: cur = (cur + " " + w) if cur.strip() else cur + w
    lines.append(cur)
    return "\n".join(lines) + "\n"


def sub(text, a, b):
    assert text.count(a) == 1, ("apply_registry (w4ae): expected once, found %d" % text.count(a), a[:100])
    assert a != b
    return text.replace(a, b)


def rec_span(text, rid):
    i = text.index("\n  - id: %s\n" % rid) + 1
    j = text.find("\n  - id: ", i + 5); k = text.find("\n\n# ", i)
    e = min(x for x in (j, k) if x > 0) + 1
    return i, e


n = next_free("SC", t)
SCA, SCB = "SC-%02d" % n, "SC-%02d" % (n + 1)
d0 = yaml.safe_load(t)
assert any(x["id"] == "S-57" for x in d0["open_items"]), "S-57 is not open here"
assert any(x["id"] == "S-76" for x in d0["open_items"]), "S-76 is not open here"
print("apply_registry (w4ae): session choices %s (HOT-R1 as drawn) and %s (D7, D8 and the fan nodes)" % (SCA, SCB))

# ------------------------------------------------------------------------------------------------ 1. the two choices
CHOICES = """  - id: {SCA}
    authority: SESSION
    under: standing-rule
    taken_on: "2026-09-27"
    closes: [S-57]
    question: >-
{qa}    taken: >-
{ta}    why: >-
{wa}    source:
      - "v2/ecad/tools/gen_sch_e.py (U10 pin 30, Q11, R58, J_BLK, TP7; the HOT-R1 comment after the PRES pair)"
      - "v2/ecad/tools/gen_sch_a.py (R216 after the expanders, J_DOCK, U27, R110, Q1, U1)"
      - "v2/ecad/tools/boards/a.json and boards/e.json (signal classes and safety lines DOCK_SPARE, BLK_SPARE, HOT_R1_G)"
      - "v2/vendor/power/jscj-2n7002-c8545.pdf (Vth(GS), IDSS, typical curves p.3)"
      - "v2/vendor/ti/ti-pca9555.pdf (SCPS131J 6.3, 6.5, 8.3.2, 8.4.1)"
      - "v2/vendor/rp2040/rpi-rp2040-datasheet.pdf (1.4.1 Figure 3, 2.19.6.3, 5.5.3 Table 625)"
      - "v2/docs/records/w4ae/hot_r1_trace.py and readings/hot_r1_trace-candidate.txt"
  - id: {SCB}
    authority: SESSION
    under: standing-rule
    taken_on: "2026-09-27"
    question: >-
{qb}    taken: >-
{tb}    why: >-
{wb}    source:
      - "v2/vendor/zhengxin/zhengxin-ss12-ss120-c51897884.pdf (SS12 THRU SS120, Maximum Ratings and Electrical Characteristics p.1, FIG3 p.2, Outline Dimensions p.3)"
      - "v2/docs/records/w4ae/jlc/q-SS14_SMB.json and lcsc-api-C51897884.json (the code's identity, 27 September 2026)"
      - "v2/ecad/tools/gen_sch_e.py (D7, D8 and the FAN1_SW and FAN2_SW node declarations after the fan loop)"
      - "v2/ecad/tools/intent_checks.py (PWR-001 on the netlist)"
"""
QA = ("How HOT-R1 (" + "SC-50" + ") is drawn on boards A and E (S-57), and how its held-low state (H2) reaches PI_KILL on "
      "board A. " + MARK + ".")
TA = ("Board E: the sensor controller's GPIO19 (U10 pin 30) drives HOT_R1_G, the gate of Q11, a 2N7002 (the JSCJ part "
      "lcsc_fill.py fills as C8545 for Q8 to Q10), source on GND, drain on BLK_SPARE (J_BLK pin 12, TP7); R58, 100 k "
      "(C25803), holds the gate to ground. Board A: R216, 10 k 0603 (filled as C25804 like R110 beside it), pulls "
      "DOCK_SPARE (J_DOCK pin 12, U27 pin 18 = P15, TP21) up to +3V3, U27's own VCC. No series resistor, no part number "
      "new to either board, no contact added; the net names BLK_SPARE and DOCK_SPARE kept, the part values and both board "
      "tables naming the function. The line is a declared safety line on both boards (SCH-004): board A listens, safe "
      "state high by R216 (the detector-lost state); board E is its source. H2 reaches PI_KILL through the panel "
      "controller: an edge on P15 sets U27's INT (EXP_INT: A J_AB1 pin 13, board B, J_PANEL pin 6) at the panel "
      "controller's GPIO24 (board C U3 pin 36); it reads U27 on the kit bus (J_AB1 pins 11 and 12, J_PANEL pins 4 and 5, "
      "U3 GPIO0 and GPIO1) and, on a held low that has lasted longer than the sensor controller's watchdog, writes the "
      "e-paper and raises PI_KILL (U3 pin 30 = GPIO19, J_PANEL pin 25, board B, J_AB1 pin 10) into Q1's gate on board "
      "A, whose drain takes the LTC2954 U1's KILL low, which drops RAIL_EN and every converter it enables. No compute "
      "module is in the path: U27 is on board A's +3V3 (U12, enabled by RAIL_EN), the panel controller on C's +3V3 from "
      "+5V_DEV through board B's F1 (U7, enabled by DEV_EN with R42's pull-up), the sensor controller always on from "
      "CELL_F; read hop by hop on the committed netlists and the contracts IF-AE-DOCK, IF-AB-RIBBON, IF-BC-PANEL and "
      "IF-AB-POWER by v2/docs/records/w4ae/hot_r1_trace.py, which stops at U10 pin 30 on main's netlists at 91894cd7.")
WA = ("SC-50's line needed a driver on E and a pull-up on A and nothing else, and these are parts each board already "
      "buys. An open drain cannot back-power board A while A is off, and it fails released (held high, SC-49's "
      "fallback on board B's TMP117) whenever E's controller is unpowered, in reset or booting (R58 and the RP2040's "
      "reset pad pull-down, PADS_BANK0 PDE reset 0x1). 10 k gives 0.33 mA, three times the expander's own pull-up "
      "(IIL at most 100 uA, SCPS131J 6.5) and far inside the 2N7002's typical capability at a 3.3 V gate (about 150 mA "
      "at VGS 3 V, JSCJ p.3); the sheet states RDS(on) only at 5 and 10 V, so the low at a 3.3 V gate is INFERRED from "
      "its typical curves shifted to the 2.5 V worst threshold and is measured at E3-H. A controller that hangs with "
      "GPIO19 high holds the line low until its watchdog resets it, hence the panel's persistence rule. Renaming the "
      "nets would touch IF-AE-DOCK's alias, check_contracts.py and gen_pcb_e5.py, which other streams own, for no "
      "electrical change. Readings: PWR-001, PWR-002, SCH-004 and the contracts on A and E unchanged or PASS on the "
      "regenerated netlists (v2/docs/records/w4ae/readings/). Reverse by S-58's hardware stage (a decode of the "
      "held-low state on board A, or a comparator over a second contact), which would add to this line, not remove "
      "it, or by a USB-only path (SC-50's reversal).")
QB = ("Which part D7 and D8 are (board E's fan flyback diodes), and the kind and peak of FAN1_SW and FAN2_SW, which "
      "PWR-001 left UNDECIDED for want of their sheet (S-76, board E's half; SC-57).")
TB = ("D7 and D8 keep the part lcsc_fill.py already filled, LCSC C51897884, which JLCPCB's parts API resolves to 'SS14 | "
      "Zhengxin | SMB(DO-214AA)' (read 27 September 2026; LCSC's own product API holds no record of the code). The code is "
      "written into gen_sch_e.py and the maker's sheet, as JLCPCB serves it (the record's data manual, no official link), "
      "is filed at v2/vendor/zhengxin/zhengxin-ss12-ss120-c51897884.pdf. FAN1_SW and FAN2_SW are declared nodes at 17.35 "
      "V: CELL_F's 16.8 V plus the sheet's maximum forward drop, 0.55 V at IFM 2.0 A and 25 C, twenty times each fan's "
      "declared 0.1 A.")
WB = ("The code resolves to an SS14 in the land the generator already names (DO-214AA, pp.1 and 3; the cathode line; K on "
      "CELL_F), VRRM 40 V, IO 1.0 A, IFSM 50 A, Tj -55 to +125 C, so nothing is substituted. A switched low side's peak is "
      "its rail plus one forward drop (S-76's recipe, SC-57's kind); the sheet publishes no cold forward curve, FIG3 reads "
      "about 0.37 V typical at the fan's 0.1 A, and every part on the nets is rated far above the figure (D7, D8 40 V; "
      "Q9, Q10 60 V). PWR-001 on board E reads PASS with 0 undecided on the regenerated netlist (it read INCONCLUSIVE on "
      "these two nets). Reverse by a fan above 2.0 A, a cold forward curve beyond the margin, or the part by onsemi's "
      "MBRS140T3G (LCSC C133091, whose record gives SMB, 40 V, 1 A, VF 600 mV at 1 A and Tj -65 to +125 C; no onsemi "
      "sheet is filed, so its forward curve is owed before it is used; corrected at integration from the independent "
      "check), the documented alternative on the same land.")
block = CHOICES.format(SCA=SCA, SCB=SCB, qa=wrap(QA), ta=wrap(TA), wa=wrap(WA), qb=wrap(QB), tb=wrap(TB), wb=wrap(WB))
anchor = "\n\n# What is still open. SESSION items are engineering the session decides"
assert t.count(anchor) == 1, "the open-items header moved"
t = t.replace(anchor, "\n" + block.rstrip("\n") + anchor, 1)

# ------------------------------------------------------------------------------------------------ 2. S-57 closed
i, e = rec_span(t, "S-57")
s57 = t[i:e]
assert s57.startswith("  - id: S-57\n    class: SESSION\n    status: OPEN\n    title: >-\n"), s57[:120]
title = s57.split("    title: >-\n", 1)[1]
t = t[:i] + t[e:]
closed = "  - id: S-57\n    closed_by: %s\n    title: >-\n%s" % (SCA, title.rstrip("\n") + "\n")
ci = t.index("\nclosed_items:\n") + len("\nclosed_items:\n")
t = t[:ci] + closed + t[ci:]

# ------------------------------------------------------------------------------------------------ 3. S-76's title
t = sub(t, """      sheet in v2/vendor. Open until the sheets are filed (and D2 has an order code, EQ-21's class) and the
      three nets are declared nodes at the rail plus the maker's forward drop.
""", wrap("sheet in v2/vendor. Open until the sheets are filed (and D2 has an order code, EQ-21's class) and the "
          "three nets are declared nodes at the rail plus the maker's forward drop. Board E's half answered by %s (27 "
          "September 2026, stream w4ae): D7 and D8's maker's sheet filed with their code C51897884, FAN1_SW and FAN2_SW "
          "declared nodes at 17.35 V, PWR-001 on board E PASS with 0 undecided; board D's RLY_K and its D2 stay open." % SCB))

# ------------------------------------------------------------------------------------------------ 4. REQ-077
i, e = rec_span(t, "REQ-077")
r = t[i:e]
r = sub(r, "    choices: [SC-49, SC-50, SC-18]\n", "    choices: [SC-49, SC-50, SC-18, %s]\n" % SCA)
r = sub(r, "    waits_on: [S-57, S-58]\n", "    waits_on: [S-58]\n")
r = sub(r, "    evidence_result: FAIL\n    evidence_phase: SCHEMATIC\n    evidence_class: DESK_REVIEW\n",
        "    evidence_result: INCONCLUSIVE\n    evidence_phase: SCHEMATIC\n    evidence_class: DESK_REVIEW\n")
t = t[:i] + r + t[e:]
note = (E_GEN + " re-read with " + A_GEN + ", " + E_NET + " and " + A_NET + " after stream w4ae drew HOT-R1 (" + SCA +
        ", 27 September 2026; the netlists regenerated on the KiCad box with main's chain and compared with main's "
        "component by component and net by net, v2/docs/records/w4ae/parity/): the desk acceptance's two parts hold on "
        "the committed netlists. (1) The path, read hop by hop by " + TRACE + " on the netlists of boards A, B, C and E "
        "and the contracts IF-AE-DOCK, IF-AB-RIBBON, IF-BC-PANEL and IF-AB-POWER (every hop found; on main's netlists "
        "at 91894cd7 it stops at U10 pin 30, a negative control; v2/docs/records/w4ae/readings/): E U10 pin 30 "
        "(GPIO19), the pack gauge's SMBus host, on HOT_R1_G to Q11's gate with R58 to GND; Q11's drain on BLK_SPARE, "
        "J_BLK pin 12; IF-AE-DOCK pin 12 to A J_DOCK pin 12, DOCK_SPARE, on U27 pin 18 (P15) with R216 to U27's own "
        "+3V3; U27 pin 1 EXP_INT to J_AB1 pin 13, B J_PANEL pin 6 and C U3 pin 36 (GPIO24), U27's SDA and SCL to C U3 "
        "GPIO0 and GPIO1; C U3 pin 30 (GPIO19) PI_KILL through J_PANEL pin 25 and B to A J_AB1 pin 10, Q1's gate (R5 "
        "to GND), Q1's drain KILL on the LTC2954 U1 pin 8 (R4 to +3V3), U1 pin 6 RAIL_EN on U12's EN; no compute "
        "module part on any board B conductor of the path, U27 on +3V3 (U12, RAIL_EN), the panel controller on "
        "+5V_DEV through B's F1 (U7, DEV_EN with R42), the sensor controller on CELL_F. (2) The thresholds: 56.5 and "
        "57.0 C in the gauge's reading under its OTD of 57.5 C, and the hottest cell at most 58.57 and 59.07 C (0.06 K "
        "more with the stop's own detection as hotstop_bounds.py counts it, 1.2 s; with FW-C14's 3 s held-line rule "
        "the detection is about 4.2 s, 0.22 K at 3.2 K/min, so the worst H2 cell is 59.29 C with 0.71 K left for the "
        "TBD terms, still inside +60 C and still ahead of OTD, and a re-run of hotstop_bounds.py with the 3 s rule is "
        "owed to its owner; corrected at integration from the independent check) inside +60 C on the published terms of 2.07 K "
        "(v2/docs/records/hc2/hotstop_bounds.out; THERMAL-COORDINATION.md section 3). The FAIL this record read on the "
        "generated boards (no path that needs no compute module) is answered; it reads INCONCLUSIVE, not PASS, because "
        "FEA-004 holds it (whether the stop acts inside the envelope, open until the heat-balance test), a desk review "
        "of the committed netlists (an AI desk review, not a qualified one). The path is firmware in two "
        "controllers (the panel's and the sensor controller's HOT-R1 rows of HW-FW-CONTRACT.md as stream w4ae drafts "
        "them); whether a firmware-free stage must stand behind it stays S-58, and the prototype acceptance (TEST-PLAN "
        "P15 and E3-H) is untouched. It stands INCONCLUSIVE on the file at {NEW}")
open(REG, "w", encoding="utf-8").write(t)
old = edlib.rebind(REG, "REQ-077", E_GEN, ROOT, note)
assert old, "REQ-077 was already bound to this gen_sch_e.py"
t = open(REG, encoding="utf-8").read()
i, e = rec_span(t, "REQ-077")
r = t[i:e]
bound = '      - "%s@%s"\n' % (E_GEN, sha[E_GEN])
assert r.count(bound) == 1, "REQ-077's rebind did not land"
r = r.replace(bound, bound + "".join('      - "%s@%s"\n' % (p, sha[p]) for p in (A_GEN, E_NET, A_NET, TRACE)))
t = t[:i] + r + t[e:]
open(REG, "w", encoding="utf-8").write(t)

# ------------------------------------------------------------------------------------------------ 5. the twelve rebinds
WHEN = "by stream w4ae on 27 September 2026 (HOT-R1, " + SCA + "; board E's half of S-76, " + SCB + ")"
BASE = {
 A_NET: A_NET + " regenerated " + WHEN + " on the KiCad box with main's chain (handover_exports.py regen, PHASE A65; "
        "main's generator reproduced main's file, PARITY): compared with the file at {OLD} component by component and "
        "net by net (v2/docs/records/w3de/net_compare.py against v2/docs/records/w4ae/parity/expected-a-netlist.json, "
        "'ONLY THE EXPECTED CHANGES'), it differs only in R216 added (10 k, DOCK_SPARE to +3V3) and J_DOCK's value",
 A_GEN: A_GEN + " re-read " + WHEN + ": R216 and its comment after the expanders' line, J_DOCK's value and R216 in the "
        "section list, and nothing else; the lines after R110's line move down by 19 (corrected at integration from the "
        "independent check, the stream's note said 18)",
 E_NET: E_NET + " regenerated " + WHEN + " on the KiCad box with main's chain (PHASE E42P; main's generator reproduced "
        "main's file, PARITY): compared with the file at {OLD} component by component and net by net "
        "(v2/docs/records/w3de/net_compare.py against v2/docs/records/w4ae/parity/expected-e-netlist.json, 'ONLY THE "
        "EXPECTED CHANGES'), it differs only in Q11 and R58 added, U10 pin 30 moved from no connection to the new net "
        "HOT_R1_G, D7 and D8 carrying their order code C51897884, and J_BLK's value",
 E_GEN: E_GEN + " re-read " + WHEN + ": U10 pin 30 on HOT_R1_G, Q11 and R58 with their comment after the PRES pair, D7 "
        "and D8's order code and the FAN1_SW and FAN2_SW node declarations after the fan loop, J_BLK's value, the GPIO "
        "list comment and the section list, and nothing else",
}
WHY = {
 "REQ-072": {E_GEN: "the solar stage this reading rests on (J_SOLAR, F2, D4, U5 and the FBIN point) is unchanged"},
 "CON-019": {A_GEN: "the interlock's lines (U26, U30, OUTLET_OK) are unchanged in content",
             A_NET: "U30, U26, OUTLET_OK, POE_EN, PD_EN, U16, U19 and PA_EN are unchanged"},
 "CON-018": {A_GEN: "U31's lines are unchanged in content",
             A_NET: "U31 on PD_CC1 and PD_CC2 at J_USBC_OUT, and C96 and C97, are unchanged"},
 "CFL-002": {E_GEN: "U17 (the SGP41) and its supply network are unchanged",
             E_NET: "U17, R57, C57, C58, SDA1 and SCL1 are unchanged"},
 "CFL-005": {A_NET: "R102 (EMCON_HW to GND), R145 on TX_INHIBIT_n and the slot enable pull-downs are unchanged"},
 "CON-010": {A_NET: "board A's PA_EN (U35, U36) and its gates are unchanged"},
 "REQ-036": {E_GEN: "the tamper block's lines are unchanged in content, and HOT-R1 does not touch the lid switch",
             E_NET: "J_TAMP, R52, R53, C52, TAMPER_LEAD, TAMPER_IO and U12's CELL_F pins are unchanged, and no board routes "
                    "the lead to ZEROIZE_HW or the panel controller"},
 "CFL-016": {E_NET: "none of the parts or nets this record cites on board E is among the changes",
             A_NET: "on board A the startup enables, the outlet interlock U30 and U26 and the wall data path J_USBW are "
                    "unchanged"},
 "CFL-013": {E_NET: "DCF_PULSE still runs from J_DCF pin 3 to U10 and nowhere else"},
 "CFL-014": {A_GEN: "the generator's charger lines and the strap's lines are unchanged in content",
             A_NET: "the strap R26 and R27 from CH_VDDA, R17 from VBAT to CELL_FUSED and F1 from CELL_FUSED to CELL+ are "
                    "unchanged"},
 "CFL-015": {E_NET: "J_SMB and its four nets are unchanged"},
 "CON-016": {A_NET: "board A's D1 to D4 are unchanged",
             E_NET: "board E's D1 to D10 keep their symbols, pins and nets (D7 and D8 gain their order code only, K on "
                    "CELL_F)"},
}
res = {x["id"]: x.get("evidence_result") for x in yaml.safe_load(open(REG, encoding="utf-8"))["records"]}
done = []
for rid, per in WHY.items():
    for path, why in per.items():
        o = edlib.rebind(REG, rid, path, ROOT, BASE[path] + "; " + why + ", so it stands " + str(res[rid]) +
                         " on the file at {NEW}")
        done.append("%s:%s%s" % (rid, os.path.basename(path), "" if o else " (already current)"))
yaml.safe_load(open(REG, encoding="utf-8"))
os.makedirs(os.path.dirname(IDS), exist_ok=True)
json.dump({"SC_HOT_R1": SCA, "SC_FAN": SCB}, open(IDS, "w"), indent=1); open(IDS, "a").write("\n")
print("apply_registry (w4ae): %s and %s added, S-57 closed by %s, S-76 updated, REQ-077 FAIL to INCONCLUSIVE (held by FEA-004; rebound to "
      "%d files), rebound %s; ids in %s" % (SCA, SCB, SCA, 5, ", ".join(done), IDS))
