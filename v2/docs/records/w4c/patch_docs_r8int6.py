#!/usr/bin/env python3
"""r8int6 re-derivation of stream w4c's patch_docs.py (beside it in this folder), written by derive_w4c_r8int6.py: EQ-25's attempts name board B's own failures as stream w4b's, FEA-002's re-read note lists what remains after stream w4b, and the HW-FW-CONTRACT row follows the fnd/w4b row and says no FW-C row covers RAIL_SENSE yet (the independent check); its three ENGINEERING-QUESTIONS.md edits are re-anchored on the text main holds after H2. The stream's text follows.

Stream w4c's drafted text for five documents it does not own (MESHSAT-1357, 27 September 2026), by asserted old text.

  v2/docs/PANEL.md                          three rows: section 1's EMCON logic row (R14 2.2 k, R50, the 17 us rise),
                                            section 3's GPIO 26 row (RAIL_SENSE through the R15/R51 divider, W4C-F1) and
                                            section 6's TX_INHIBIT_n row (its source column: R14 2.2k 1 % and R50 on C7):
                                            the PANEL.md writer
  v2/docs/feasibility/EMCON.md              section 2's Source, conductor and pull-down bullets (R14's value, R50), section
                                            4.1's Default bullet (R50 beside R2, R145 and R59, the walk's reading) and
                                            section 4b's W3T-F1 paragraph (one closing sentence): the EMCON.md writer
  v2/docs/ARCHITECTURE.md                   section 6.2's TX_INHIBIT_n row (R14 2.2 k 1 %, R50 on C): the architecture writer
  v2/docs/handover/ENGINEERING-QUESTIONS.md EQ-25's index row, attempts and next action; EQ-19's board C sentence, with
                                            +3V3 covering EPD_VCC and U5's headroom item (W4C-F5): the questions writer
  v2/docs/HW-FW-CONTRACT.md                 section 4's candidate table gains fnd/w4c's row: the contract writer
and v2/ecad/tools/pcb_requirements.yaml, where every record bound to an edited document is re-read against the edit and
rebound with a note that starts with the path (the r8int5 edlib form). The script finds the bound records itself and
REFUSES when a record is bound to an edited document and has no re-read note here, so no binding is left stale; on main
91894cd7 and on main 62f26a44 the bound records are the five on PANEL.md (CFL-001, CFL-005, CFL-014, CFL-015, CFL-016) and
the seven on EMCON.md (REQ-012, REQ-030, REQ-071, REQ-032, CON-010, CON-021, FEA-002); no record binds ARCHITECTURE.md,
ENGINEERING-QUESTIONS.md or HW-FW-CONTRACT.md (every record's evidence_bound_to read). ARCHITECTURE.md is bound elsewhere
by v2/docs/diagrams/MANIFEST.json only, as an input of the five arch-* diagrams (sections 2, 3.2, 4.1, 4.3 and 5.5, none
of which this edit touches); the script reports that and leaves the rebuild to the diagrams writer (build.py renders).

Run AFTER apply_registry.py (the text names the session choices and the open item it adds, read from the registry by
their markers). Each block is idempotent by its own marker and refuses a file whose old text is not there exactly once.
Prototype framing: nothing is built; every figure is a desk reading. Usage: patch_docs.py [<tree root>] [--dry-run]"""
import difflib, hashlib, json, os, re, subprocess, sys

DRY = "--dry-run" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = args[0] if args else (subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
                              or os.getcwd())
REQ = os.path.join(ROOT, "v2/ecad/tools/pcb_requirements.yaml")
C_NET = "v2/ecad/pcb-c-display-c8/out/pcb-c-display.net"
_reqt = open(REQ, encoding="utf-8").read()


def _sc(marker, what):
    m = re.search(r"(?m)^  - id: (SC-\d{2})\n(?:    [^\n]*\n)*?    question: >-\n      " + re.escape(marker), _reqt)
    if not m: raise SystemExit("patch_docs (w4c): run apply_registry.py first (no session choice for %s in the registry)" % what)
    return m.group(1)


SC = _sc("EQ-25 on board C (stream w4c", "EQ-25")
SC_PWR = _sc("Which kind does each supply PWR-001 refused on board C take", "PWR-001 on board C")
_m = re.search(r"(?m)^  - id: (S-\d{2})\n    class: SESSION\n    status: OPEN\n    title: >-\n      Finding W4C-F5 \(stream w4c", _reqt)
if not _m: raise SystemExit("patch_docs (w4c): run apply_registry.py first (no open item for W4C-F5 in the registry)")
S_F5 = _m.group(1)


def _sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


CNET = _sha16(os.path.join(ROOT, C_NET))


def para(s, first="- ", rest="  ", width=118):
    """A markdown bullet wrapped the way EMCON.md wraps its bullets (about 118 columns, two-space continuation)."""
    words = s.split(); lines = []; cur = first
    for w in words:
        if len(cur) + len(w) + (0 if cur in (first, rest) else 1) > width and cur.strip() not in ("", first.strip()):
            lines.append(cur); cur = rest + w
        else:
            cur = cur + w if cur in (first, rest) else cur + " " + w
    return "\n".join(lines + [cur]) + "\n"


# ------------------------------------------------------------------ EMCON.md sections 2 and 4.1 (independent check, pass 2)
EM_SOURCE_OLD = (
    "- **Source.** `SW_EMCON` on board C, an APEM 5636ADKB-2V locking toggle, single pole ON-NONE-ON (lug 1\n"
    "  `TX_INHIBIT_n`, lug 2 GND, lug 3 unconnected; `gen_sch_c.py:115` to `117`, `:211`). Closed pulls `TX_INHIBIT_n` low\n"
    "  against R14 (10 k to C's +3V3) and C24 (10 nF) (`gen_sch_c.py:150`; `main-pcb-c-display.net:4113`).\n")
EM_SOURCE_NEW = para(
    "**Source.** `SW_EMCON` on board C, an APEM 5636ADKB-2V locking toggle, single pole ON-NONE-ON (lug 1 `TX_INHIBIT_n`, "
    "lug 2 GND, lug 3 unconnected; `gen_sch_c.py:115` to `117`, `:211`). Closed pulls `TX_INHIBIT_n` low against R14 and "
    "C24 (10 nF) (`gen_sch_c.py:150`; `main-pcb-c-display.net:4113`), where R14 was 10 k to C's +3V3. Since EQ-25 (stream "
    "w4c, 27 September 2026, " + SC + ") R14 is 2.2 k 1 percent and R50, 10 k 1 percent, holds the node to GND on board C "
    "as well (`gen_sch_c.py`, the R14 line and the EQ-25 note at the end of the design; board C's netlist at sha256/16 "
    + CNET + ").")
EM_COND_OLD = (
    "- **`TX_INHIBIT_n` is one conductor across four boards and three ribbons:** board C (R14, C24, TP10, U9's input) to\n"
    "  `J_PANEL` pin 11, board B (R59), `J_AB1` pin 16, board A (R145), `J_MEZZ1` pin 8, board D (R2, U12 pin 2)\n"
    "  (`main-pcb-c-display.net:4113`, `B-r6cand-pcb-b-compute.net:22317`, `A-r6cand-pcb-a-power.net:10816`,\n"
    "  `D-r6cand-pcb-d-aprs.net:4514`). Its neighbours on the flat cables are `ZEROIZE_HW` and `HDMI_SEL1` (panel ribbon\n"
    "  pins 10 and 12), `EMCON_HW` and `SLOT_EN1` (`J_AB1` pins 15 and 17), `TR_APRS` and `PA_EN` (`J_MEZZ1` pins 7 and 9)\n"
    "  (`v2/docs/records/rv-emc/readings/tx-inhibit-conductor.txt`).\n")
EM_COND_NEW = para(
    "**`TX_INHIBIT_n` is one conductor across four boards and three ribbons:** board C (R14, C24, TP10, U9's input, and R50 "
    "since EQ-25) to `J_PANEL` pin 11, board B (R59), `J_AB1` pin 16, board A (R145), `J_MEZZ1` pin 8, board D (R2, U12 "
    "pin 2) (`main-pcb-c-display.net:4113`, `B-r6cand-pcb-b-compute.net:22317`, `A-r6cand-pcb-a-power.net:10816`, "
    "`D-r6cand-pcb-d-aprs.net:4514`). Its neighbours on the flat cables are `ZEROIZE_HW` and `HDMI_SEL1` (panel ribbon "
    "pins 10 and 12), `EMCON_HW` and `SLOT_EN1` (`J_AB1` pins 15 and 17), `TR_APRS` and `PA_EN` (`J_MEZZ1` pins 7 and 9) "
    "(`v2/docs/records/rv-emc/readings/tx-inhibit-conductor.txt`).")
EM_PULL_OLD = (
    "- **Pull-downs that assert the lines with the source gone:** `TX_INHIBIT_n` has 100 k on A (R145), B (R59) and D (R2).\n"
    "  `EMCON_HW` has B's R58 at 10 k (candidate) and A's R102 at 100 k (`B-r6cand-pcb-b-compute.net:19944`,\n"
    "  `A-r6cand-pcb-a-power.net:9736`). Board A's round 8 netlist makes R102 10 k 1% (section 4a).\n")
EM_PULL_NEW = para(
    "**Pull-downs that assert the lines with the source gone:** `TX_INHIBIT_n` has 100 k on A (R145), B (R59) and D (R2), "
    "and since EQ-25 (stream w4c, 27 September 2026, " + SC + ") 10 k 1 percent on C (R50): with board C unpowered and the "
    "panel ribbon in, the three 100 k alone let the stated Ioff of the gates on the line lift it to 1.09 V against the 0.8 V "
    "VIL the RF-002 walk applies (W3T-F1, section 4b), and with R50 it reads 0.24 V. `EMCON_HW` has B's R58 at 10 k "
    "(candidate) and A's R102 at 100 k (`B-r6cand-pcb-b-compute.net:19944`, `A-r6cand-pcb-a-power.net:9736`). Board A's "
    "round 8 netlist makes R102 10 k 1% (section 4a).")
EM_DEF_OLD = (
    "- **Default.** `TX_INHIBIT_n` follows the toggle. With the panel unpowered or any ribbon cut, R2, R145 and R59 hold it\n"
    "  low (tool: the `TX_INHIBIT_n` line PASS). R84 (10 k) holds KEY low against the gates' leakage when their own rail is at\n"
    "  0 V: 0.43 V at most against U19's 0.8 V VIL, 0.51 V with the harness +3V3 down too (`gen_sch_d.py:592`; r6d R6D-3).\n")
EM_DEF_NEW = para(
    "**Default.** `TX_INHIBIT_n` follows the toggle. With the panel unpowered or any ribbon cut, R2, R145 and R59 hold it "
    "low, and board C's R50 (10 k 1 percent, since EQ-25) with them wherever the panel ribbon stays in (tool: the "
    "`TX_INHIBIT_n` line PASS on board C's netlist with R50, 0.243 V with the panel unpowered; without R50 it read FAIL at "
    "1.085 V, W3T-F1, section 4b). R84 (10 k) holds KEY low against the gates' leakage when their own rail is at 0 V: 0.43 V "
    "at most against U19's 0.8 V VIL, 0.51 V with the harness +3V3 down too (`gen_sch_d.py:592`; r6d R6D-3).")

# (file, marker proving the block is applied, old text, new text); markers are checked to be in the new text below
EDITS = [
 ("v2/docs/PANEL.md", "Since EQ-25 (stream w4c",
  "far outside the 74LVC1G34's input slew limit, `gen_sch_c.py:157-166`).",
  "far outside the 74LVC1G34's input slew limit, `gen_sch_c.py:157-166`). Since EQ-25 (stream w4c, 27 September 2026, "
  + SC + ") `R14` is 2.2 k 1 % and `R50` (10 k 1 %) holds `TX_INHIBIT_n` down on this board too: with the panel unpowered "
  "the line reads 0.24 V under the RF-002 walk's worst-case Ioff sums (1.09 V before), released it rests at 2.57 V (2.37 V "
  "at the adverse ends), and it rises with a 17 us time constant."),
 ("v2/docs/PANEL.md", "the `R15`/`R51` 10k/10k divider",
  "| 26 (ADC0) | RAIL_SENSE | `LED_RAIL_SW` through 10k: the LED rail is present when the LIGHTING toggle is not at BLACKOUT |",
  "| 26 (ADC0) | RAIL_SENSE | `LED_RAIL_SW` through the `R15`/`R51` 10k/10k divider (W4C-F1, 27 September 2026: through "
  "`R15` alone the pin sat above IOVDD, RP2040 datasheet 2.9.5): about 2.5 V (2.65 V at most) while the LED rail is present, "
  "0 V at BLACKOUT; the pin is an ADC input (IE low, OD high); the rail is present above 1.25 V |"),
 ("v2/docs/PANEL.md", "and `R50` (10k 1 %, since EQ-25) down on C7",
  "| TX_INHIBIT_n | `SW_EMCON` closed = low (10k pull-up `R14` on C7, 10 nF `C24`; A22, B16 and D8 each hold it down with 100k "
  "so a cut ribbon inhibits) |",
  "| TX_INHIBIT_n | `SW_EMCON` closed = low (pull-up `R14` on C7, 2.2k 1 % since EQ-25 and 10k before, 10 nF `C24`, and `R50` "
  "(10k 1 %, since EQ-25) down on C7, so the line reads inhibited with the panel unpowered, 0.24 V under the RF-002 walk's "
  "worst-case Ioff sums (section 1); A22, B16 and D8 each hold it down with 100k so a cut ribbon inhibits) |"),
 ("v2/docs/feasibility/EMCON.md", "where R14 was 10 k to C's +3V3", EM_SOURCE_OLD, EM_SOURCE_NEW),
 ("v2/docs/feasibility/EMCON.md", "U9's input, and R50", EM_COND_OLD, EM_COND_NEW),
 ("v2/docs/feasibility/EMCON.md", "1 percent on C (R50)", EM_PULL_OLD, EM_PULL_NEW),
 ("v2/docs/feasibility/EMCON.md", "and board C's R50 (10 k 1 percent, since EQ-25) with them", EM_DEF_OLD, EM_DEF_NEW),
 ("v2/docs/feasibility/EMCON.md", "**Since stream w4c (EQ-25",
  "S-64, engineering question EQ-25, for board C's next circuit round (`v2/docs/records/w3t/`).",
  "S-64, engineering question EQ-25, for board C's next circuit round (`v2/docs/records/w3t/`). **Since stream w4c (EQ-25, "
  "27 September 2026, " + SC + ", which closes S-64)** board C carries option (a): `R14` 2.2 k 1 percent and `R50`, 10 k 1 "
  "percent, from `TX_INHIBIT_n` to GND. On the regenerated netlist the walk reads the line PASS: 0.243 V with board C "
  "unpowered (1.085 V before) and 0.178 V with the A-D mezzanine out as well (1.103 V before); board D's SA868 keying returns "
  "to its own UNDECIDED (the SA_PTT_n threshold its maker does not state). Released, the line rests at 2.57 V (2.37 V at the "
  "adverse ends, 2.11 V before); asserted, the toggle's contact holds it at ground. Latency is unchanged in kind: asserting "
  "is the contact (settled within its 2 ms bounce); the release crosses U9's VT+ after about 31 us (`v2/docs/records/w4c/`)."),
 ("v2/docs/ARCHITECTURE.md", "R50 (C), 10 k 1 % since EQ-25",
  "| TX_INHIBIT_n | C's SW_EMCON (to GND) with R14 10 k up on C | D's KEY gate; A and B | LOW: inhibited | R145 (A), R59 (B), "
  "R2 (D), 100 k each |",
  "| TX_INHIBIT_n | C's SW_EMCON (to GND) with R14 up on C: 2.2 k 1 % since EQ-25 (stream w4c, 27 September 2026), 10 k at "
  "`eadbe571` | D's KEY gate; A and B | LOW: inhibited | R145 (A), R59 (B), R2 (D), 100 k each; and R50 (C), 10 k 1 % since "
  "EQ-25, which holds the line with the panel connected but unpowered (0.24 V against the 0.8 V VIL under the RF-002 walk's "
  "worst-case Ioff sums; 1.09 V before, W3T-F1) |"),
 ("v2/docs/handover/ENGINEERING-QUESTIONS.md", "answered on board C by stream w4c",
  "| RF-002 on boards A to D and board D's SA868 keying (S-64) |",
  "| answered on board C by stream w4c (" + SC + ", S-64 closed): R14 2.2 k and R50 10 k, the line PASS on the candidate; board "
  "D's SA868 keying back to its own UNDECIDED |"),
 ("v2/docs/handover/ENGINEERING-QUESTIONS.md", "**Stream w4c (27 September 2026):**",
  "board D's SA868 then returns to its own UNDECIDED (its maker states no PTT threshold). |",
  "board D's SA868 then returns to its own UNDECIDED (its maker states no PTT threshold). **Stream w4c (27 September 2026):** "
  "option (a) drawn on board C (`R14` 2.2 k 1 percent, `R50` 10 k 1 percent) in `gen_sch_c.py` and regenerated on the KiCad "
  "box with parity (main's generator reproduces main's files; the candidate differs by R14's value and code and R50 and R51 "
  "alone, every component and every net's pins compared). On the candidate the walk reads the line PASS (0.243 V where it "
  "read 1.085 V, 0.178 V where it read 1.103 V): inhibit_chain A INCONCLUSIVE (0 fail, 7 pass, 2 undecided), B FAIL (its own "
  "ten on main's walk, which are stream w4b's: its rows and circuit landed ahead of this change in the same integration, "
  "EMCON.md section 4c), C PASS (6 of 6), D INCONCLUSIVE (the SA868's own threshold). Released 2.57 V (2.37 V at the adverse ends, over U9's "
  "about 2.15 V VT+, which R14 10k missed at 2.11 V); asserted at ground; latency the contact's 2 ms bounce, release about 31 "
  "us. " + SC + " closes S-64 (`v2/docs/records/w4c/`). **Status:** answered on the candidate; the consolidated re-take "
  "makes it current in the tree. |"),
 ("v2/docs/handover/ENGINEERING-QUESTIONS.md", "(a) drawn by stream w4c",
  "| **Recommended next action** | (a) at board C's next circuit round, regenerated with parity, then the RF-002 re-take on boards A to D. |",
  "| **Recommended next action** | (a) drawn by stream w4c (" + SC + "); the RF-002 re-take on boards A to D at the "
  "integration that merges it, then bench E-01 and E-11 for the lines' real levels. |"),
 ("v2/docs/handover/ENGINEERING-QUESTIONS.md", "**Board C (stream w4c, 27 September 2026):**",
  "Board E's tracker senses on its bottom leg since S-47's core (SC-56). **Status:** A and B read PASS and D and E "
  "INCONCLUSIVE in the streams' scratch; the consolidated re-take takes them in the tree. |",
  "Board E's tracker senses on its bottom leg since S-47's core (SC-56). **Board C (stream w4c, 27 September 2026):** the "
  "consolidated re-take read FAIL of 7 on C's committed netlist (C_DVDD, EPD_VCC, LED_RAIL and LED_RAIL_SW undeclared, "
  "eleven nets undecided); declared by their makers' kinds (" + SC_PWR + "): EPD_VCC, LED_RAIL_SW and LED_RAIL as rails, "
  "C_DVDD as the RP2040's own regulator node, the eleven nets and the lamp feeds as nodes at the voltages the circuit "
  "states, EPD_RESE by the panel maker's reference; PWR-001 read PASS of 6 in the stream's scratch on the regenerated "
  "netlist (0 undecided). +3V3's own figures cover its child EPD_VCC (0.149 A typical, 0.72 A peak, finding W4C-F5 of the "
  "stream's independent check), and U5's headroom under the e-paper boost's 0.5 A class figure is open item " + S_F5 + ", "
  "read at bring-up. Declaring LED_RAIL_SW found W4C-F1 (RAIL_SENSE above IOVDD), drawn as the R15/R51 divider. "
  "**Status:** A, B and C read PASS and D and E INCONCLUSIVE in the streams' scratch; the consolidated re-take takes them "
  "in the tree. |"),
 ("v2/docs/HW-FW-CONTRACT.md", "| `fnd/w4c` |",
  "| `fnd/w4b` (r8int6) | FW-B13 | the RockBLOCK's ENABLE is EMCON_HW AND U6's request RB_SW_IEN in U536; the panel raises the request only with +5V_RB up and, after an EMCON, only once RB_STATUS reads low (`feasibility/EMCON.md` 4c) |",
  "| `fnd/w4b` (r8int6) | FW-B13 | the RockBLOCK's ENABLE is EMCON_HW AND U6's request RB_SW_IEN in U536; the panel raises the request only with +5V_RB up and, after an EMCON, only once RB_STATUS reads low (`feasibility/EMCON.md` 4c) |\n"
  "| `fnd/w4c` | FW-C07; RAIL_SENSE, which no FW-C row covers yet (the contract writer's) | TX_INHIBIT_n's `R14` 2.2 k 1 % and `R50` 10 k 1 % (EQ-25): no firmware duty, nothing drives the line; "
  "RAIL_SENSE (GPIO 26, ADC0) now reads `LED_RAIL_SW` through the `R15`/`R51` divider (W4C-F1): about 2.5 V present, 0 V at "
  "BLACKOUT (PANEL.md section 3) |"),
]
# r8int6: three ENGINEERING-QUESTIONS.md anchors moved on main after 62f26a44 (H2 appended to EQ-19's attempts and
# EQ-25's next action, and rewrote EQ-25's index row); the stream's three edits are re-anchored on the current text,
# the H2 sentences kept as the history they are, with the stream's own words and markers.
def _r8int6_reanchor(edits):
    out = []
    for rel, mk, old, new in edits:
        if mk == "answered on board C by stream w4c":
            old = ("| RF-002 FAIL on current evidence on boards A to D, a layout-entry reason on each; board D's SA868 "
                   "keying; CON-010 FAIL (S-64) |")
            new = ("| answered on board C by stream w4c (" + SC + ", S-64 closed): R14 2.2 k and R50 10 k, the line PASS "
                   "on the candidate; board D's SA868 keying back to its own UNDECIDED; RF-002 and CON-010 wait on the "
                   "re-take |")
        elif mk == "(a) drawn by stream w4c":
            old = ("| **Recommended next action** | (a) at board C's next circuit round, regenerated with parity, then the "
                   "RF-002 re-take on boards A to D. **H2:**")
            new = ("| **Recommended next action** | (a) drawn by stream w4c (" + SC + ", after H2); the RF-002 re-take on "
                   "boards A to D at the integration that merges it, then bench E-01 and E-11 for the lines' real "
                   "levels. **At H2:**")
        elif mk == "**Board C (stream w4c, 27 September 2026):**":
            mid = new[new.index("(SC-56). ") + len("(SC-56). "):new.index(" **Status:**")]
            assert mid.startswith(mk), mid[:60]
            old = "which now need the same declarations. |"
            new = ("which now need the same declarations. " + mid + " **Status after stream w4c:** C reads PASS of 6 "
                   "in the stream's scratch; the consolidated re-take takes it in the tree. |")
        out.append((rel, mk, old, new))
    return out


EDITS = _r8int6_reanchor(EDITS)


def has(text, marker):
    """A marker is found across the line breaks a wrapped paragraph puts in it."""
    return marker in re.sub(r"\s+", " ", text)


for _rel, _mk, _old, _new in EDITS:
    assert has(_new, _mk) and not has(_old, _mk), (_rel, _mk)
    assert chr(0x2014) not in _new, (_rel, _mk)


# THE RECORDS BOUND TO THE EDITED DOCUMENTS: each re-read against the edit and rebound to the file's new sha with a note
# that starts with the path. Every changed region is named in the file's note, so "every other line is byte-identical" is
# true by construction (each edit replaces its asserted old text and nothing else); rebind_all refuses a bound record
# that has no note here.
PANEL_NOTE = ("v2/docs/PANEL.md re-read after stream w4c's edit of 27 September 2026 (read against the file at {OLD}): three "
              "table rows change, section 1's EMCON logic row, which gains one sentence on board C's R14 (2.2 k 1 %) and R50 "
              "(10 k 1 %) with the line's failed-safe and released levels and its 17 us rise, section 3's GPIO 26 row, which "
              "describes RAIL_SENSE through the R15/R51 divider (W4C-F1), and section 6's TX_INHIBIT_n row, whose source "
              "column now names R14 at 2.2k 1 % and R50 (10k 1 %) on C7 beside the three consumer pull-downs (it named a 10k "
              "pull-up and the three 100k only), as board C's regenerated netlist at {CNET} carries them; every other line "
              "is byte-identical; ")
EMCON_NOTE = ("v2/docs/feasibility/EMCON.md re-read after stream w4c's edit of 27 September 2026 (read against the file at "
              "{OLD}): five places change, all about the TX_INHIBIT_n line on board C: section 2's Source, conductor and "
              "pull-down bullets (rewrapped), which name R14 at 2.2 k 1 percent and R50 (10 k 1 percent) to GND and the "
              "line's level with board C unpowered (0.24 V, 1.09 V before, W3T-F1); section 4.1's Default bullet "
              "(rewrapped), which names R50 beside R2, R145 and R59 and the walk's reading with and without it; and section "
              "4b's W3T-F1 paragraph, which gains one closing sentence (the line PASS on board C's regenerated netlist at "
              "{CNET}, board D's SA868 keying back to its own UNDECIDED, the released and asserted levels and the latency); "
              "every other line is byte-identical, among them sections 0, 0a, 1, 3, 4 with 4.2 to 4.18, 4a, the rest of 4b, "
              "5, 5a, 6, 7, 8 and 9 to 9d; ")
NOTES = {
 "v2/docs/PANEL.md": (PANEL_NOTE, {
   "CFL-001": "line 5 (bank 1's home and failover hosts), the rest of section 1 and section 2's ribbon table with its pin 15 "
              "row, which this reading rests on, are unchanged: none of the three changed rows names a bank or a host",
   "CFL-005": "section 7's panel-absent paragraph, which this reading cites, is byte-identical; section 6's EMCON_HW row is "
              "unchanged and its TX_INHIBIT_n row still names R145 on board A, and with the panel's ribbon out board C's R50 "
              "is not on the conductor that paragraph describes",
   "CFL-014": "section 10, which this reading cites, is byte-identical",
   "CFL-015": "section 10's SMBus sentences, which this reading cites, are byte-identical",
   "CFL-016": "two changed rows are in sections 1 and 6, which this record's acceptance asks to describe the circuit as "
              "generated, and both now name R14 at 2.2 k 1 % and R50 as the regenerated netlist carries them; section 3's "
              "GPIO 26 row names the divider the same netlist carries; section 6's other rows and section 7 are "
              "byte-identical"}),
 "v2/docs/feasibility/EMCON.md": (EMCON_NOTE, {
   "REQ-012": "section 0's TX-lamp sentence and bench E-02, on which this reading rests, are byte-identical",
   "REQ-030": "what the FAIL rests on is unchanged (the RockBLOCK's local chain, the SA868's missing receive threshold, L3 and "
              "RF-002's reading of board B); the changed places move the TX_INHIBIT_n line's fail-safe state with board C "
              "unpowered to PASS on the candidate, which this record's 'a board is unpowered' clause needs and none of those "
              "depends on",
   "REQ-071": "section 5a and section 0a's end-to-end column are byte-identical; the added sentence states the line's own "
              "latency (the contact's 2 ms bounce, a release of about 31 us) and sections 2 and 4.1 state R14's value and "
              "R50, none of which closes a row",
   "REQ-032": "sections 4.4 and 4.5, L3 and L4 and 4b's paragraphs on the 5G module and the back-feed, on which this reading "
              "rests, are byte-identical; the changed places are about TX_INHIBIT_n's pulls and fail-safe state",
   "CON-010": "section 4.1's Default bullet now names board C's R50 beside R2, R145 and R59 and the walk's reading of the "
              "line on board C's netlist with it (PASS) and without it (FAIL at 1.085 V, W3T-F1), where it read PASS with no "
              "figure; the gate's trace this reading cites (KEY = PTT_ANY AND TX_INHIBIT_n, U14, U15, U13), the rest of 4.1 "
              "and section 4.2 are byte-identical, and the SA868's row stays open on its maker's missing threshold (bench "
              "E-01)",
   "CON-021": "section 7's common-element row (board C's lamp D22, U14 and Q7, its plate light guide still owed), which this "
              "reading cites, is byte-identical",
   "FEA-002": "section 7 is byte-identical and none of the items this reading names as remaining after stream w4b moves "
              "(the Iridium 9704's response to its ENABLE, the SA868's threshold, L4 case (2) on U536, the back-feed, the "
              "plate's light guide, the RF-002 walk's unread classes on board B, every bench test); the changed places close "
              "W3T-F1 on the candidate only"}),
 "v2/docs/ARCHITECTURE.md": ("", {}),
 "v2/docs/handover/ENGINEERING-QUESTIONS.md": ("", {}),
 "v2/docs/HW-FW-CONTRACT.md": ("", {}),
}


def _wrap(s, first="          ", rest="          ", width=120):
    words = s.split(); lines = []; cur = first.rstrip()
    for w in words:
        if len(cur) + 1 + len(w) > width and cur.strip():
            lines.append(cur); cur = rest + w
        else:
            cur = (cur + " " + w) if cur.strip() else (first + w)
    return "\n".join(lines + [cur]) + "\n"


def _rebind(t, rid, relpath, new, note):
    assert note.startswith(relpath), note[:60]
    i = t.index("\n  - id: %s\n" % rid) + 1
    ends = [x for x in (t.find("\n  - id: ", i + 5), t.find("\n\n# ", i)) if x > 0]
    j = min(ends) + 1 if ends else len(t)
    r = t[i:j]
    m = re.search(r'"?%s@([0-9a-f]{16})"?' % re.escape(relpath), r)
    if not m: raise SystemExit("patch_docs (w4c): %s is not bound to %s" % (rid, relpath))
    old = m.group(1)
    if old == new: return t, None
    r = r.replace("%s@%s" % (relpath, old), "%s@%s" % (relpath, new))
    k = r.index("    evidence_bound_to:")
    r = r[:k] + "      - >-\n" + _wrap(note.replace("{NEW}", new).replace("{OLD}", old)) + r[k:]
    return t[:i] + r + t[j:], old


def rebind_all(edited, dry):
    import yaml
    t0 = open(REQ, encoding="utf-8").read(); t = t0; log = []
    recs = yaml.safe_load(t0)["records"]
    res = {r["id"]: r.get("evidence_result") for r in recs}
    for rel in sorted(edited):
        base, per = NOTES[rel]
        bound = [r["id"] for r in recs if any(str(b).startswith(rel + "@") for b in (r.get("evidence_bound_to") or []))]
        missing = sorted(set(bound) - set(per))
        if missing:
            raise SystemExit("patch_docs (w4c): %s is bound by %s, which have no re-read note here; re-read them against "
                             "the edit and add their notes before applying" % (rel, ", ".join(missing)))
        if not bound:
            log.append("%s: bound by no record" % os.path.basename(rel)); continue
        new = _sha16(os.path.join(ROOT, rel))
        for rid in bound:
            t, old = _rebind(t, rid, rel, new, base.replace("{CNET}", CNET) + per[rid] + ", so it stands " + str(res[rid])
                             + " on the file at {NEW}")
            log.append("%s:%s %s" % (rid, os.path.basename(rel), "rebound" if old else "current"))
    yaml.safe_load(t)
    if t != t0:
        if dry: sys.stdout.writelines(difflib.unified_diff(t0.splitlines(True), t.splitlines(True), REQ, REQ, n=0))
        else: open(REQ, "w", encoding="utf-8").write(t)
    return log


def diagrams_note():
    """ARCHITECTURE.md is an input of the diagrams' MANIFEST.json: say which diagrams read it and whether it moved."""
    p = os.path.join(ROOT, "v2/docs/diagrams/MANIFEST.json")
    if not os.path.exists(p): return "diagrams: no MANIFEST.json"
    man = json.load(open(p, encoding="utf-8"))
    rel = "v2/docs/ARCHITECTURE.md"; now = _sha16(os.path.join(ROOT, rel))
    names = sorted(n for n, rec in man["diagrams"].items() if rel in rec["inputs"])
    moved = [n for n in names if man["diagrams"][n]["inputs"][rel] != now]
    return ("diagrams: %d read ARCHITECTURE.md (%s), %d of them against another sha than the file's %s; their Mermaid "
            "blocks (sections 2, 3.2, 4.1, 4.3, 5.5) are not touched by this edit; the rebuild (build.py) is the diagrams "
            "writer's" % (len(names), ", ".join(names), len(moved), now))


def main():
    log = []
    by_file = {}
    for rel, marker, old, new in EDITS:
        p = os.path.join(ROOT, rel)
        t = by_file.get(p) or open(p, encoding="utf-8").read()
        if has(t, marker):
            log.append("%s: already has %r" % (rel, marker[:30])); by_file[p] = t; continue
        n = t.count(old)
        if n != 1: raise SystemExit("patch_docs (w4c): %s: expected the old text once, found %d: %r" % (rel, n, old[:80]))
        t2 = t.replace(old, new)
        assert t2 != t
        by_file[p] = t2; log.append("%s: %r" % (rel, marker[:30]))
    edited = set()
    for p, t in by_file.items():
        t0 = open(p, encoding="utf-8").read()
        edited.add(os.path.relpath(p, ROOT))
        if t == t0: continue
        if DRY: sys.stdout.writelines(difflib.unified_diff(t0.splitlines(True), t.splitlines(True), p, p, n=0))
        else: open(p, "w", encoding="utf-8").write(t)
    log += rebind_all(edited, DRY) if not DRY else ["rebinding shown after the edits are written (run without --dry-run)"]
    log.append(diagrams_note())
    print("patch_docs (w4c, %s, %s, %s): %s%s" % (SC, SC_PWR, S_F5, "; ".join(log), " [dry run]" if DRY else ""))


main()
