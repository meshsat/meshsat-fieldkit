#!/usr/bin/env python3
"""Stream w4c's registry change (board C: EQ-25 / S-64 / W3T-F1, PWR-001 on board C, finding W4C-F1; MESHSAT-1357,
27 September 2026), applied BY RECORD ID with asserted old text. Prototype framing: nothing is built; every reading
named here is a desk reading of committed or candidate netlists, taken in scratch.

Two files, both the registry writer's, not stream w4c's:
  v2/ecad/tools/pcb_requirements.yaml
    1. one SESSION open item at the NEXT FREE S-nn, finding W4C-F5 of the independent check (U5's headroom under the
       e-paper boost's 0.5 A class figure, read at bring-up), and three SESSION choices, each taking the NEXT FREE SC-nn
       in the tree it is applied to (another branch, fnd/rel2, is adding records too): EQ-25's fix (closes S-64),
       PWR-001's kinds on board C (with +3V3 covering EPD_VCC), and W4C-F1 (RAIL_SENSE);
    2. S-64 leaves open_items for closed_items, closed_by the first of them;
    3. the four records bound to board C's netlist (REQ-012, CON-021, CFL-016, CON-016) are re-read against the
       regenerated file and rebound to its sha with a note that starts with the path (the r8int5 edlib form).
  v2/ecad/tools/pcb_rules_coverage.yaml
    4. RF-002's row gains the reading with board C's fix, after its W3T-F1 sentence.

Run from the repository root (or pass it), AFTER board C's four regenerated files from fnd/w4c are in that tree
(pcb-c-display.kicad_sch, out/pcb-c-display.net, .net.prov.json, -intent.json): step 3 refuses a netlist that is not
the one stream w4c read (sha256/16 3fddbb3edcd4248a, the pass-2 regeneration). Idempotent: a step already applied (found by its marker) is left
alone. --dry-run prints the unified diff and writes nothing. Then, in v2/ecad/tools: `python3 rules_lib.py
requirements` and `python3 rules_render.py --requirements` (the integration recipe: commit the config inputs before
rules_status and rules_render)."""
import difflib, hashlib, os, re, subprocess, sys

import yaml

DRY = "--dry-run" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = args[0] if args else (subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
                              or os.getcwd())
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
REQ = os.path.join(TOOLS, "pcb_requirements.yaml")
COV = os.path.join(TOOLS, "pcb_rules_coverage.yaml")
C_NET = "v2/ecad/pcb-c-display-c8/out/pcb-c-display.net"
C_NET_SHA16 = "3fddbb3edcd4248a"          # the candidate netlist stream w4c regenerated and read (pass 2, 27 September 2026)
MARK_SC = "EQ-25 on board C (stream w4c"   # step 1's marker
MARK_COV = "FIXED ON BOARD C BY STREAM w4c"
MARK_SB = "Which kind does each supply PWR-001 refused on board C take"
MARK_SCC = "Board C's RAIL_SENSE (U3 GPIO26, ADC0)"
MARK_S5 = "Finding W4C-F5 (stream w4c"


def id_of(text, marker):
    """The SC-nn whose question starts with the marker (each marker fits the question's first wrapped line)."""
    head = marker
    m = re.search(r"(?m)^  - id: (SC-\d{2})\n(?:    [^\n]*\n)*?    question: >-\n      " + re.escape(head), text)
    if not m: raise Refused("no session choice starts %r" % head)
    return m.group(1)


class Refused(Exception):
    pass


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def once(text, old, new, where):
    n = text.count(old)
    if n != 1:
        raise Refused("%s: expected the old text once, found it %d times: %r" % (where, n, old[:100]))
    out = text.replace(old, new)
    if out == text:
        raise Refused("%s: the replacement changed nothing" % where)
    return out


def wrap(s, first="      ", rest="      ", width=120):
    words = s.split(); lines = []; cur = first.rstrip()
    for w in words:
        if len(cur) + 1 + len(w) > width and cur.strip():
            lines.append(cur); cur = rest + w
        else:
            cur = (cur + " " + w) if cur.strip() else (first + w)
    return "\n".join(lines + [cur]) + "\n"


def q(s):
    """A YAML double-quoted scalar."""
    return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')


# ------------------------------------------------------------------ 1. the three session choices
def next_sc(text, n):
    have = {int(x) for x in re.findall(r"(?m)^  - id: SC-(\d{2})$", text)}
    out, k = [], (max(have) if have else 0) + 1
    while len(out) < n:
        if k not in have: out.append("SC-%02d" % k)
        k += 1
    return out


def next_s(text):
    have = {int(x) for x in re.findall(r"(?m)^  - id: S-(\d{2,3})$", text)}
    return "S-%02d" % ((max(have) if have else 0) + 1)


def s_id(text):
    m = re.search(r"(?m)^  - id: (S-\d{2,3})\n    class: SESSION\n    status: OPEN\n    title: >-\n      " + re.escape(MARK_S5), text)
    if not m: raise Refused("no open item starts %r" % MARK_S5)
    return m.group(1)


def build_s5(sid):
    """Finding W4C-F5 of stream w4c's independent check: what U5 carries when +3V3 covers EPD_VCC."""
    title = (MARK_S5 + ", 27 September 2026; board C; the stream's independent check): +3V3 declared a 0.20 A peak "
        "while its child EPD_VCC declares 0.521 A (the e-paper boost's 0.5 A switch-current class into L1, PDi driving-circuit "
        "note Rev.02 page 4 note (1)); since the check +3V3 declares 0.149 A typical and 0.72 A peak (its own loads' 0.119 and "
        "0.199 A plus EPD_VCC's 0.030 and 0.521 A), so its copper from U5 and C2 to Q5 is judged at what it can carry: within "
        "each boost on-phase (about 1.6 us, 10 uH to 0.5 A from 3.135 V) C28 behind Q5's at most 85 mOhm (AO3401A) is a "
        "0.40 us time constant, so most of the inductor's current comes through Q5. U5, a TLV75533, is rated 500 mA (IOUT; "
        "ICL 560 mA minimum; TI SBVS320D 5.3 and 5.5): the 0.22 A by which the peak exceeds it, held for no longer than one "
        "on-phase, is at most 0.35 uC, 24 mV on C2, C28 and C29 (14.8 uF nominal) against the rail's 99 mV budget, but what "
        "U5 carries on average through a refresh rests on the boost's output power, which no held document states "
        "(EPD_VCC's 10 mA share is INFERRED). The same reading decides +5V: its declared 1.0 A peak (and "
        "pcb_energy_chain.yaml's B_PANEL_5V peak_a, under board B's F1 at 1.1 A hold) covers U5 only while U5 draws at most "
        "0.508 A beside LED_RAIL_SW's 0.462 A and the sounder's 0.03 A; power_path's feed sum reads +5V's children at 0.94 "
        "A because it scales a rail without an efficiency by its voltage ratio, where an LDO's input current is its output "
        "current. Open until bring-up reads U5's output current, averaged over the boost's switching period, and +3V3 at "
        "U3's IOVDD through a full e-paper refresh (the UC8253c's booster soft start and an update) with the lamps lit at "
        "DAY: closed when +3V3 stays inside its 3 percent budget and U5's average at or under 500 mA; otherwise board C's "
        "next circuit round sizes a local bulk on EPD_VCC from the measured on-phase or feeds the e-paper from a supply "
        "with the headroom, and +5V's peak and B_PANEL_5V's follow the reading. v2/ecad/tools/gen_sch_c.py (the +3V3 "
        "declaration and the check after EPD_VCC's).")
    return "  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % (sid, wrap(title))


def choice(cid, question, taken, why, source, closes=None):
    s = "  - id: %s\n    authority: SESSION\n    under: standing-rule\n    taken_on: \"2026-09-27\"\n" % cid
    s += "    question: >-\n" + wrap(question) + "    taken: >-\n" + wrap(taken) + "    why: >-\n" + wrap(why)
    if closes: s += "    closes: [%s]\n" % ", ".join(closes)
    s += "    source:\n" + "".join("      - %s\n" % q(x) for x in source)
    return s


def build_choices(sa, sb, sc, s5):
    """The three session choices, taking the ids given (the next free ones in the tree)."""
    A = choice(sa,
        MARK_SC + ", 27 September 2026): with board C unpowered, TX_INHIBIT_n read 1.09 V against the 0.8 V VIL the RF-002 walk "
        "applies (W3T-F1, S-64). How is it held under VIL with margin under the walk's worst-case Ioff convention, without "
        "losing the released level or the asserted one while board C is powered?",
        "Option (a) of S-64, on board C alone: R14 10k to 2.2k 1 percent (UNI-ROYAL 0603WAF2201T5E, C4190) and a new R50, 10k 1 "
        "percent (0603WAF1002T5E, C25804), from TX_INHIBIT_n to GND (v2/ecad/tools/gen_sch_c.py, the R14 line and the note at "
        "the end of the design). On the regenerated netlist (%s@%s) the walk reads the line PASS: 0.243 V with board C "
        "unpowered (1.085 V before) and 0.178 V with the A-D mezzanine out as well (1.103 V before); every other fail-safe state "
        "is unchanged, the highest 0.578 V (boards A and D with the A-B ribbon out). Released, 2.57 V nominal and 2.37 V at the "
        "adverse ends (2.54 V and 2.11 V before); asserted, the toggle's contact holds the line at ground and R14 draws 1.59 mA."
        % (C_NET, C_NET_SHA16),
        "One board, the board whose round 8 lamp gate U14 added the Ioff that lifted the line, and the lowest failed-safe level "
        "of the three options S-64 names ((b) board B's R59 at 10k with R14 2.2k, 0.26 V on two boards; (c) the three "
        "pull-downs at 47k with R14 4.7k, 0.51 V on four boards). It also lifts the released level at the adverse ends over "
        "the about 2.15 V VT+ this tree reads for U9 at 3.3 V, which R14 at 10k did not (2.11 V). The toggle's current stays "
        "inside the APEM 5636ADKB's gold-plated contacts' range (10 uA at 5 V to 100 mA at 30 VDC) and under the walk's 4 mA "
        "pull limit. Latency: asserting is the contact itself, settled within its 2 ms bounce; release crosses U9's VT+ after "
        "about 31 us (144 us before); with board C's supply gone R50 and the three pull-downs hold the line with a 78 us time "
        "constant; each far inside REQ-071's 1 s. The FAIL rested on the walk's worst-case convention (an unpowered part passes "
        "its Ioff), so this is margin, not the repair of a demonstrated defect. Reverse by option (b) or (c) if a measured Ioff "
        "(bench E-01, E-11) or a later reader on the line changes the sums.",
        ["v2/ecad/tools/gen_sch_c.py (R14, R50, the EQ-25 note at the end of the design)",
         "v2/ecad/tools/tx_inhibit.py (fail_safe, VIL_LOW, PULL_MA_MAX, TOL_DEFAULT, RAIL_TOL)",
         "v2/docs/records/w4c/readings/after-candidate/fail-safe-states-TX_INHIBIT_n.txt and ../before-main-91894cd7/",
         "v2/docs/records/w3t/HANDOFF.md section 2",
         "v2/vendor/seals/apem-5000-series-datasheet-rs-copy.pdf page 2 (contact ratings, contact resistance, bounce)",
         "v2/vendor/diodes/diodes-74lvc1g17.pdf page 4; v2/vendor/ti/ti-sn74lvc1g57.pdf 6.5"],
        closes=["S-64"])
    B = choice(sb,
        "Which kind does each supply PWR-001 refused on board C take (EQ-19 for board C: C_DVDD, EPD_VCC, LED_RAIL and "
        "LED_RAIL_SW undeclared), and how are the eleven nets it left UNDECIDED settled (EMCLAMP_A, EMCLAMP_K, EPD_RESE, "
        "LIGHT_DAY_n, LIGHT_NIGHT_n, TEST_SW, TX_A, TX_INHIBIT_n, TX_K, TX_LAMPTEST, ZEROIZE_SW)?",
        "Rails: EPD_VCC (the e-paper's switched 3.3 V, Q5 to the panel's VDDIO and VDD and to the boost inductor L1; 30 mA "
        "typical, 0.521 A peak; switch Q5, enable EPD_PWR_n), LED_RAIL_SW (+5V behind the LIGHTING toggle's pole 1: Q1, the "
        "EMCON lamp's R47, the MAIN ring's R39, Q1's gate pull-up R17 and the sense divider; declared always on with the reason "
        "that no line enables it) and LED_RAIL (Q1 to the eighteen lamp resistors; switch Q1, enable Q1_G), each converted "
        "False and fed from its parent. A node for C_DVDD, the RP2040's own core regulator output (1.30 V by VSEL, 1.16 V in "
        "service). Nodes for the eleven undecided nets at the voltages the circuit states (TX_INHIBIT_n, ZEROIZE_SW, TEST_SW, "
        "LIGHT_DAY_n and LIGHT_NIGHT_n at 3.333 V; EMCLAMP_A, EMCLAMP_K, TX_A, TX_K and TX_LAMPTEST at 5.0 V; EPD_RESE by the "
        "panel maker's reference) and for the lamp feed and return nets the rails' named loads reach (the fifteen indicators' "
        "anodes and cathodes, PIRING_A, TESTRING_A, MAINRING_A and Q1_G at 5.0 V, RAIL_SENSE at 2.65 V). +3V3's load Q5 "
        "moves from 1 mA to EPD_VCC's 30 mA, and +3V3's own figures cover its child EPD_VCC (0.149 A typical and 0.72 A peak, "
        "finding W4C-F5 of the stream's independent check; U5's headroom under the boost's 0.5 A class figure is open item "
        "%s, read at bring-up). PWR-001 reads PASS of 6 on the regenerated netlist (census: 5 counted, 57 "
        "declared node, 3 settled, 0 undecided, 74 unmarked); power_path PASS (0 short), power_sequence PASS of 5." % s5,
        "The kinds board D and E's SC-57 and board B's stream w3b used: a rail where a current reaches more than one place or "
        "a switched load, a node where the net is one part's own supply, a lamp's feed or a signal. The figures are the "
        "makers': RP2040 datasheet 2.10.3, Table 189 and Table 634; UltraChip UC8253c A0.6 page 59 (IVDD 0.1, IVDDIO 0.1 and "
        "IVDDA 20.0 mA operating maximum at 3.0 V and 25 C, the only column the sheet gives; the driver PDi's flyer names for the E2370KS0C1) plus 10 mA INFERRED for "
        "the boost, whose output power no held document states, to be read at bring-up; PDi driving-circuit note Rev.02 page "
        "4 note (1) for the boost's 0.5 A switch-current class and page 10 BOM item 9 for the sense resistor (EPD_RESE is "
        "declared by that reference, so no DC figure is invented for a chopped current); TI SBVS320D's 1 percent for +3V3; "
        "TI SCPS131J for the expanders' 5 V tolerant I/O. The lamps carry no part number, so their typical is the 8 mA the "
        "series resistors were chosen for and their peak the 5.25 V / R bound that needs no forward voltage. Reverse any "
        "node by a load on it that is another part's supply, and EPD_VCC's typical by the bench reading.",
        ["v2/ecad/tools/gen_sch_c.py (the PWR-001 declarations at the end of the design, +3V3's loads)",
         "v2/ecad/tools/intent_checks.py (PWR-001 on the netlist)",
         "v2/vendor/rp2040/rpi-rp2040-datasheet.pdf 2.10.3, Tables 189 and 634",
         "v2/vendor/pdi/ultrachip-uc8253c-a0.6.pdf page 59 (filed from v2/docs/records/w4c/vendor/)",
         "v2/vendor/pdi/pdi-epd-driving-circuit-rev02.pdf pages 4 and 10",
         "v2/docs/records/w4c/readings/after-candidate/c-intent_rails.verdict.json",
         "v2/docs/handover/ENGINEERING-QUESTIONS.md EQ-19"])
    C = choice(sc,
        "Board C's RAIL_SENSE (U3 GPIO26, ADC0) sat on the 5 V LED_RAIL_SW through R15 alone, above the RP2040's IOVDD "
        "(finding W4C-F1, read while declaring LED_RAIL_SW for PWR-001). How is it bounded?",
        "R51, 10k (UNI-ROYAL 0603WAF1002T5E, C25804), from RAIL_SENSE to GND, making R15 and R51 the divider PANEL.md section "
        "1's LED-rail row already names: at most 2.65 V at 5.25 V, 0 V at BLACKOUT (pole 1 open, R15 and R51 hold it down).",
        "The maker: 'the voltage on the ADC analogue inputs must not exceed IOVDD ... Voltages greater than IOVDD will result "
        "in leakage currents through the ESD protection diodes' (RP2040 datasheet 2.9.5 and 4.9 notes), with VPIN at most "
        "IOVDD + 0.5 V (Table 622); through 10k alone the pin sat on its diode with about 0.15 mA into +3V3 whenever the lamps "
        "were lit. A larger series resistor only lowers that current, a clamp adds a part and still injects, and moving the "
        "sense to an expander input moves a function the firmware reads today; the divider is one 0603 of a reel the board "
        "carries. The firmware's threshold for 'present' (about 2.5 V, 0 V absent) is the PANEL.md writer's. Reverse by a "
        "measured reason the pin must see the rail undivided.",
        ["v2/ecad/tools/gen_sch_c.py (R51, the W4C-F1 note at the end of the design)",
         "v2/vendor/rp2040/rpi-rp2040-datasheet.pdf 2.9.5, 4.9, Tables 622 and 625",
         "v2/docs/PANEL.md section 1 (LED rail row) and section 3 (GPIO 26)"])
    return A + B + C


def main():
    text0 = open(REQ, encoding="utf-8").read()
    cov0 = open(COV, encoding="utf-8").read()
    text, cov, log = text0, cov0, []

    # ---- step 1a: W4C-F5's open item, at the end of open_items
    if MARK_S5 in text:
        log.append("step 1a: already applied (%s)" % s_id(text))
    else:
        s5 = next_s(text)
        anchor = "\n\n# Items that left the open list, and what closed each"
        text = once(text, anchor, "\n" + build_s5(s5).rstrip("\n") + anchor, "open_items' end")
        log.append("step 1a: %s (W4C-F5) added" % s5)
    S5 = s_id(text)

    # ---- step 1
    if MARK_SC in text:
        m = re.search(r"(?m)^  - id: (SC-\d{2})\n(?:    [^\n]*\n)*?    question: >-\n      EQ-25 on board C \(stream w4c", text)
        if not m: raise Refused("step 1: the marker is present but its choice id cannot be read")
        log.append("step 1: already applied (%s)" % m.group(1))
    else:
        sa, sb, sc = next_sc(text, 3)
        blocks = build_choices(sa, sb, sc, S5)
        anchor = "\n# What is still open. SESSION items are engineering the session decides and records with authority SESSION;"
        text = once(text, anchor, "\n" + blocks + anchor[1:], "the open items' header")
        log.append("step 1: %s (EQ-25), %s (PWR-001 on board C), %s (W4C-F1) added" % (sa, sb, sc))
    SCA, SCB, SCC = (id_of(text, x) for x in (MARK_SC, MARK_SB, MARK_SCC))

    # ---- step 2: S-64 to closed_items
    if re.search(r"(?m)^  - id: S-64\n    closed_by: ", text):
        log.append("step 2: already applied")
    else:
        m = re.search(r"(?ms)^  - id: S-64\n    class: SESSION\n    status: OPEN\n    title: >-\n(.*?)(?=^  - id: )", text)
        if not m: raise Refused("step 2: S-64 is not an OPEN SESSION item in open_items")
        title = m.group(1)
        assert "Finding W3T-F1" in title, "step 2: S-64's title is not W3T-F1's"
        text = text[:m.start()] + text[m.end():]
        closed = "  - id: S-64\n    closed_by: %s\n    title: >-\n%s" % (SCA, title)
        text = once(text, "\n\nrecords:\n", "\n" + closed.rstrip("\n") + "\n\nrecords:\n", "closed_items' end")
        log.append("step 2: S-64 closed by %s" % SCA)

    # ---- step 3: rebinding the four records bound to board C's netlist
    have = sha16(os.path.join(ROOT, C_NET))
    if have != C_NET_SHA16:
        raise Refused("step 3: %s is at %s, not the %s stream w4c read; install fnd/w4c's four board C files first"
                      % (C_NET, have, C_NET_SHA16))
    base = (C_NET + " regenerated by stream w4c on 27 September 2026 (EQ-25 and PWR-001 on board C, MESHSAT-1357) on the "
            "KiCad box with main's chain (handover_exports.py regen, PHASE C24; main's own regeneration at 91894cd7 reads "
            "PARITY_AFTER_NOISE against the committed file and MATCH against an empty change list): compared with the file at "
            "{OLD} component by component and net by net (pin, pinfunction, pintype) by two independent readers (stream w4c's "
            "netcmp_w4c.py against expected-c-netlist.json, MATCH, and stream w3a's netcmp.py; v2/docs/records/w4c/parity/), "
            "it differs only in R14 (10k C25804 to 2.2k 1% C4190), R50 (10k 1%, C25804) added from TX_INHIBIT_n to GND and "
            "R51 (10k, C25804) added from RAIL_SENSE to GND; the intent beside it declares three more rails and forty-seven "
            "nodes and raises +3V3 to cover EPD_VCC, which moves no part (") + SCB + ", " + S5 + ")"
    why = {
        "REQ-012": "no node of TX_A, TX_K, Q3_G, TR_APRS, LED_RAIL, Q1 or Q2 changed, so the TX lamp's anode is still LED_RAIL "
                   "behind Q1 and Q2 and the lamp still needs the controller's PANEL_PWM",
        "CON-021": "D22, R47, Q7, R48, R49 and U14 keep every node; U14's input TX_INHIBIT_n now rests at 2.57 V released (2.37 V "
                   "at the adverse ends, over its about 2.04 V VT+ at 3.3 V; 2.54 V and 2.11 V before) and at ground asserted, "
                   "so the lamp's gate reads both states with more margin and nothing in its path changed; the plate's light "
                   "guide is still owed",
        "CFL-016": "U9 is still the 74LVC1G17 from TX_INHIBIT_n to EMCON_HW and the ZEROIZE toggle still on the local ZEROIZE_SW "
                   "at GPIO 22 with U12 copying it onto ZEROIZE_HW; the LED rail sense is now the divider PANEL.md section 1's "
                   "LED-rail row names (R15 and R51), and the two PANEL.md sentences the change dates (section 1's '77 us time "
                   "constant', section 3's GPIO 26 'through 10k') are drafted for the PANEL.md writer "
                   "(v2/docs/records/w4c/patch_docs.py)",
        "CON-016": "D19 to D21 keep every node and record, and the two parts added are resistors, no clamp and no rectifier",
    }
    res = {r["id"]: r.get("evidence_result") for r in yaml.safe_load(text)["records"]}
    for rid, w in why.items():
        note = base + "; " + w + ", so it stands " + str(res[rid]) + " on the file at {NEW}"
        text, old = rebind(text, rid, C_NET, have, note)
        log.append("step 3: %s %s" % (rid, ("rebound from %s" % old) if old else "already current"))

    # ---- step 4: RF-002's coverage row
    if MARK_COV in cov:
        log.append("step 4: already applied")
    else:
        a = re.search(r"(?m)^ RF-002: \{", cov); b = re.compile(r"(?m)^ [A-Z][A-Z0-9]*-\d+: \{").search(cov, a.end())
        row = cov[a.start():b.start()]
        old = ("not a demonstrated defect (open item W3T-F1 in pcb_requirements.yaml, corrected at the r8int5 integration from "
               "the independent check).")
        new = old + (" " + MARK_COV + " (EQ-25, 27 September 2026, %s, which closes S-64; verdicts in the stream's scratch on "
                     "the KiCad box): R14 2.2k 1 percent and R50 10k 1 percent on board C's candidate netlist %s, the other "
                     "five at main 91894cd7: the TX_INHIBIT_n line PASS (0.243 V with board C unpowered, which read 1.085 V; "
                     "0.178 V with the A-D mezzanine out as well, which read 1.103 V), inhibit_chain A INCONCLUSIVE (0 fail, 7 "
                     "pass, 2 undecided), B FAIL (10 fail, 7 pass, 3 undecided), C PASS (6 of 6), D INCONCLUSIVE (0 fail, 7 pass, "
                     "1 undecided: the SA868 keying back to its own UNDECIDED, the SA_PTT_n threshold its maker does not state), "
                     "E PASS, P PASS; main's own re-take in the same scratch read the committed A FAIL (1, 6, 2), B FAIL (11, "
                     "6, 3), C FAIL (1, 5, 0), D FAIL (2, 6, 0) (v2/docs/records/w4c/readings/)." % (SCA, C_NET_SHA16))
        row2 = once(row, old, new, "RF-002 row")
        cov = cov[:a.start()] + row2 + cov[b.start():]
        log.append("step 4: RF-002 row, reading with board C's fix added")

    yaml.safe_load(text); yaml.safe_load(cov)
    if DRY:
        for p, t0, t1 in ((REQ, text0, text), (COV, cov0, cov)):
            sys.stdout.writelines(difflib.unified_diff(t0.splitlines(True), t1.splitlines(True), p, p, n=1))
    else:
        if text != text0: open(REQ, "w", encoding="utf-8").write(text)
        if cov != cov0: open(COV, "w", encoding="utf-8").write(cov)
    print("apply_registry (w4c): " + "; ".join(log) + (" [dry run, nothing written]" if DRY else ""))


def _rec_span(t, rid):
    i = t.index("\n  - id: %s\n" % rid) + 1
    j = t.find("\n  - id: ", i + 5)
    k = t.find("\n\n# ", i)
    ends = [x for x in (j, k) if x > 0]
    return i, (min(ends) + 1 if ends else len(t))


def rebind(t, rid, relpath, new, note):
    """Move rid's evidence_bound_to entry for relpath to `new` and add the note (which starts with relpath) before
    evidence_bound_to, as the r8int5 edlib.rebind does. Returns (text, old sha16 or None when already current)."""
    assert note.startswith(relpath), note[:60]
    i, j = _rec_span(t, rid); r = t[i:j]
    m = re.search(r'"?%s@([0-9a-f]{16})"?' % re.escape(relpath), r)
    if not m: raise Refused("step 3: %s is not bound to %s" % (rid, relpath))
    old = m.group(1)
    if old == new: return t, None
    r = r.replace("%s@%s" % (relpath, old), "%s@%s" % (relpath, new))
    k = r.index("    evidence_bound_to:")
    r = r[:k] + "      - >-\n" + wrap(note.replace("{NEW}", new).replace("{OLD}", old), "          ", "          ") + r[k:]
    return t[:i] + r + t[j:], old



if __name__ == "__main__":
    try:
        main()
    except Refused as e:
        print("apply_registry (w4c): REFUSED: %s" % e); sys.exit(2)
