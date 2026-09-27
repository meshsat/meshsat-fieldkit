#!/usr/bin/env python3
"""r8int6 re-derivation of stream w4ae's edit_docs.py (beside it in this folder), written by derive_w4ae_r8int6.py with the independent check's corrections: FW-E10's watchdog bound counts the edge-to-kick interval, and the sheet's sources line says its confidence is lower. The stream's text follows.

The document half of stream w4ae (MESHSAT-1357, 27 September 2026): what HOT-R1 drawn on boards A and E (the
registry's HOT-R1 choice, SC_HOT_R1 in ids.json) and board E's flyback sheet (SC_FAN) change in pages other streams own.
Run AFTER apply_registry.py (it reads the ids that script took, because every SC- id a page of v2/docs/ cites must be
one the registry defines). Every edit asserts its old text once and refuses a page that moved under it; each file is
idempotent by its own marker. Nothing here is the owner's: the session's choices under his standing rule of 26
September 2026.

  conops      v2/docs/CONOPS.md (BASELINED as layer 2 at 79963b3b): a post-baseline revision note under the title,
              section 4c's HOT-R1 paragraph (the parts as drawn, the FAIL sentence answered), the feasibility sentence of
              section 4c that said "until then", section 7a's HOT-R1 row. No need, mode, trigger, threshold or product
              decision changes; the layer 2 owner decides whether the baseline needs a re-check for it.
  hwfw        v2/docs/HW-FW-CONTRACT.md: FW-C13, FW-C14 and FW-E10 go OWED to DRAWN with the designators; FW-C14 gains the
              EXP_INT service (U27 port 1 read, the PCA9555 errata) and a once-a-second poll, FW-E10 the watchdog bound
              (a hang with GPIO19 high clears inside FW-C14's 3 s); section 9's hot stop line; a change-record row.
  panel       v2/docs/PANEL.md: GPIO24's row and the 0x21 row of section 7 name HOT-R1 on U27 P1.5.
  interfaces  v2/ecad/tools/pcb_interfaces.yaml IF-AE-DOCK: a hot_r1 entry for pin 12 (the pin map is unchanged).
  sources     v2/vendor/sources.txt: the line for v2/vendor/zhengxin/zhengxin-ss12-ss120-c51897884.pdf.
  grade       v2/docs/parts/grade-sources.yaml: C51897884's row gains its maker, its Tj range and the filed sheet
              (then re-run v2/docs/parts/grade_check.py for GRADE-CHECK.md, the parts stream's page).
  eq          v2/docs/handover/ENGINEERING-QUESTIONS.md: EQ-22's index row and its Attempts and Recommended rows.

Usage: edit_docs.py <tree root> [ids.json] [--only a,b,...]"""
import json, os, sys, textwrap

ROOT = os.path.abspath(sys.argv[1])
args = [a for a in sys.argv[2:] if not a.startswith("--only")]
IDS = args[0] if args else os.path.join(ROOT, "v2/docs/records/w4ae/ids.json")
ONLY = None
for i, a in enumerate(sys.argv):
    if a == "--only": ONLY = set(sys.argv[i + 1].split(","))
    elif a.startswith("--only="): ONLY = set(a.split("=", 1)[1].split(","))
ids = json.load(open(IDS))
SCA, SCB = ids["SC_HOT_R1"], ids["SC_FAN"]
MARK = "stream w4ae"


def md(text, width=118, indent=""):
    return "\n".join(textwrap.wrap(" ".join(text.split()), width=width, initial_indent=indent, subsequent_indent=indent,
                                   break_long_words=False, break_on_hyphens=False))


def patch(rel, edits, marker=MARK):
    p = os.path.join(ROOT, rel)
    t = open(p, encoding="utf-8").read()
    if marker in t:
        print("edit_docs (w4ae): %s already carries this stream's edits" % rel); return
    o = t
    for old, new in edits:
        n = t.count(old)
        assert n == 1, "edit_docs (w4ae): %s: expected the old text once, found %d: %r" % (rel, n, old[:100])
        t = t.replace(old, new)
    assert t != o
    open(p, "w", encoding="utf-8").write(t)
    print("edit_docs (w4ae): %s, %d edit(s)" % (rel, len(edits)))


def row_edit(rel, row_id, edits, marker=MARK):
    """Edits confined to one table row (a line starting with '| <row_id> |')."""
    p = os.path.join(ROOT, rel)
    lines = open(p, encoding="utf-8").read().split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith("| %s |" % row_id)]
    assert len(hits) == 1, "edit_docs (w4ae): %s: row %s found %d times" % (rel, row_id, len(hits))
    l = lines[hits[0]]
    for old, new in edits:
        assert l.count(old) == 1, "edit_docs (w4ae): %s row %s: %r found %d times" % (rel, row_id, old[:80], l.count(old))
        l = l.replace(old, new)
    lines[hits[0]] = l
    open(p, "w", encoding="utf-8").write("\n".join(lines))


def conops():
    rel = "v2/docs/CONOPS.md"
    note = md("**Revised after its baseline, 27 September 2026 (%s, MESHSAT-1357):** HOT-R1 is drawn on boards A and E "
              "(%s: `Q11` and `R58` on board E, `R216` on board A); section 4c's HOT-R1 paragraph and its feasibility "
              "sentence, and section 7a's HOT-R1 row, say so. No need, mode, trigger, threshold, bearer set or product "
              "decision changed; whether the baseline needs a re-check for this revision is the layer 2 owner's call "
              "(`handover/LAYER-STATUS.md`)." % (MARK, SCA))
    old_p1 = """**HOT-R1, the line that makes the path independent of the modules (taken by the session on 27 September 2026 as a
board A and board E design item, owed before their layout entry; section 7a).** The dock already carries a spare
contact from board E's `J_BLK` pin 12 (`BLK_SPARE`, whose only other node as generated is the test point `TP7`,
`gen_sch_e.py` lines 562 and 693) through the dock block to board A's `J_DOCK` pin 12 (`DOCK_SPARE`, `gen_sch_a.py`
line 226), which lands on `U27` pin 18, an input of the expander whose change raises `EXP_INT` (`U27` pin 1 with
`R110`, line 1267), the panel controller's interrupt (`J_AB1` pin 13, board B, `J_PANEL` pin 6, `U3` GPIO24). HOT-R1
drives that contact from the sensor controller's free GPIO19 (`U10` pin 30, not connected as generated) through an
open-drain 2N7002 with a gate pull-down on board E, and pulls it up to board A's 3.3 V with 10 k beside `U27`; the
dock contract `IF-AE-DOCK` (`v2/ecad/tools/pcb_interfaces.yaml`, its pin 12) names it. No part number is new to either
board and no contact is added. One wire carries four states: toggled at 1 Hz, each edge after a fresh reading of all
"""
    new_p1 = md("**HOT-R1, the line that makes the path independent of the modules (taken by the session on 27 September "
                "2026 as a board A and board E design item, section 7a; drawn on both boards the same day, %s).** The "
                "dock carries a contact from board E's `J_BLK` pin 12 (`BLK_SPARE`, with the test point `TP7`) through "
                "the dock block to board A's `J_DOCK` pin 12 (`DOCK_SPARE`, with `TP21`), which lands on `U27` pin 18 "
                "(P1.5), an input of the expander whose change raises `EXP_INT` (`U27` pin 1 with `R110`), the panel "
                "controller's interrupt (`J_AB1` pin 13, board B, `J_PANEL` pin 6, `U3` GPIO24). HOT-R1 drives that "
                "contact from the sensor controller's GPIO19 (`U10` pin 30) through `Q11`, an open-drain 2N7002 whose "
                "gate `R58` (100 k) holds to ground, on board E, and `R216` (10 k) pulls it up to board A's 3.3 V beside "
                "`U27` (`gen_sch_e.py` and `gen_sch_a.py`, each at its HOT-R1 comment; the path from the gauge's reader "
                "to `PI_KILL` read hop by hop on the committed netlists by `records/w4ae/hot_r1_trace.py`); the dock "
                "contract `IF-AE-DOCK` (`v2/ecad/tools/pcb_interfaces.yaml`, its pin 12) names it. No part number is new "
                "to either board and no contact is added. One wire carries four states: toggled at 1 Hz, each edge after a "
                "fresh reading of all" % SCA) + "\n"
    old_p2 = """toggle. **Until HOT-R1 is in both generators the hot stop's requirement reads FAIL on the generated boards,** a finding
reported to the owner, not asked: the stop then acts only where the bridge links the two controllers (the normal and
reduced modes, and the heat stage after BANK-R1, up to H1 itself), and falls back to the `TMP117` elsewhere. The
hand-offs are layer 5's: the dock contract's pin 12, and the four states in the sensor controller's and the panel
controller's firmware contracts (`PANEL.md`)."""
    new_p2 = md("toggle. **HOT-R1 is in both generators since 27 September 2026 (%s; S-57 closed):** the path "
                          "REQ-077's desk acceptance asks for is on the committed netlists, and the requirement reads "
                          "INCONCLUSIVE at desk, held by FEA-004 (whether the stop acts inside the envelope), where it read "
                          "FAIL for want of the line; until then the stop acted only where the bridge links the two "
                          "controllers (the normal and reduced modes, and the heat stage after BANK-R1, up to H1 itself) "
                          "and fell back to the `TMP117` elsewhere. The hand-offs are layer 5's: the dock contract's pin "
                          "12, and the four states in the sensor controller's and the panel controller's firmware "
                          "contracts (`HW-FW-CONTRACT.md` FW-C13, FW-C14 and FW-E10; `PANEL.md`)." % SCA)
    old_p3 = """input, and the design intends it to do so at any conductance once HOT-R1 is in the generators of boards A and E (the
requirement reads FAIL on the generated boards until then) and on the provisional error budget (H2 leaves 0.93 K for"""
    new_p3 = """input, and the design intends it to do so at any conductance, HOT-R1 being in the generators of boards A and E since
27 September 2026 (%s), and on the provisional error budget (H2 leaves 0.93 K for""" % SCA
    old_p4 = ("owed before the layout entry of boards A and E, with the dock contract's pin 12 and the two firmware contracts; "
              "until then the hot stop's requirement reads FAIL on the generated boards, a finding reported to the owner |")
    new_p4 = ("drawn on both boards on 27 September 2026 (%s: `Q11` and `R58` on board E, `R216` on board A), with the dock "
              "contract's pin 12 and the two firmware contracts (`HW-FW-CONTRACT.md` FW-C14 and FW-E10); until then the "
              "hot stop's requirement read FAIL on the generated boards |" % SCA)
    old_h = "# MeshSat field kit V2: concept of operations\n\n**Status: BASELINED"
    new_h = "# MeshSat field kit V2: concept of operations\n\n" + note + "\n\n**Status: BASELINED"
    patch(rel, [(old_h, new_h), (old_p1, new_p1), (old_p2, new_p2), (old_p3, new_p3), (old_p4, new_p4)])


def hwfw():
    rel = "v2/docs/HW-FW-CONTRACT.md"
    p = os.path.join(ROOT, rel)
    if MARK in open(p, encoding="utf-8").read():
        print("edit_docs (w4ae): %s already carries this stream's edits" % rel); return
    row_edit(rel, "FW-C13", [("| FIRMWARE; its line OWED (HOT-R1, S-57) |", "| FIRMWARE; its line DRAWN (HOT-R1, %s) |" % SCA)])
    row_edit(rel, "FW-C14", [
        ("the line's 10 k pull-up to board A's 3.3 V and board E's driver are not drawn (FW-E10)",
         "the line's pull-up is `A:R216` (10 k to +3V3, U27's own VCC) and its driver board E's open drain `E:Q11` "
         "(FW-E10), drawn by %s (%s)" % (MARK, SCA)),
        (" | REQ-077; SC-50; ",
         ". Service every `EXP_INT` by reading `A:U27`'s input port 1, which clears the interrupt that port raised (TI "
         "SCPS131J 8.4.1), then write a command byte other than 00h (the errata of 8.4.1.1): `EXP_INT` is wired-OR across "
         "boards A, B and C, and a toggling line asserts it twice a second (ten times in H1), so an unserviced U27 would "
         "hold it low for every other source; poll the port at least once a second as well, because a held line makes no "
         "edge | REQ-077; SC-50; %s; " % SCA),
        ("| P15; V-C13 | OWED (HOT-R1, S-57) |", "| P15; V-C13 | DRAWN (%s) |" % SCA)])
    row_edit(rel, "FW-E10", [
        ("`E:U10` GPIO19 (pin 30) is not connected as generated and board E's contact `BLK_SPARE` (`J_BLK` pin 12) reaches "
         "only `TP7` (`gen_sch_e.py` lines 562, 581 and 693); the open-drain 2N7002 with its gate pull-down that drives the "
         "contact is not drawn",
         "`E:U10` GPIO19 (pin 30) drives `HOT_R1_G`, the gate of `E:Q11` (2N7002, `R58` 100 k to GND), whose open drain "
         "pulls board E's contact `BLK_SPARE` (`J_BLK` pin 12, `TP7`) low; drawn by %s (%s)" % (MARK, SCA)),
        (" | REQ-077; SC-49, SC-50; ",
         "; keep the watchdog's period plus the longest interval between an edge of the line and the next watchdog kick "
         "under FW-C14's 3 s (for example a period of at most 1.5 s with the kick in the reading loop; the timeout runs "
         "from the last kick while the held-line clock runs from the last edge), so a controller that hangs with GPIO19 high is reset, and its "
         "pads released, before the panel controller reads the line as held low | REQ-077; SC-49, SC-50, %s; " % SCA),
        ("| P15; V-C13 | OWED (HOT-R1, S-57) |", "| P15; V-C13 | DRAWN (%s) |" % SCA)])
    patch(rel, [
        ("""- The hot stop's rows (FW-C13, FW-C14, FW-E10) rest on HOT-R1, which neither board A's nor board E's generator draws
  (S-57): until both do, the line is OWED and REQ-077 reads FAIL at desk.""",
         md("- The hot stop's rows (FW-C13, FW-C14, FW-E10) rest on HOT-R1, drawn on boards A and E since 27 September "
            "2026 (%s; `records/w4ae/hot_r1_trace.py` reads the path on the committed netlists); the rows themselves are "
            "firmware, verified at P15 and E3-H (V-C13), and REQ-077 reads INCONCLUSIVE at desk, held by FEA-004." % SCA,
            indent="").replace("\n", "\n  ")),
    ], marker="\x00never")
    t = open(p, encoding="utf-8").read()
    last = [l for l in t.split("\n") if l.startswith("| 1 (second release attempt) |")]
    assert len(last) == 1, "the change record's last row moved"
    row = ("| 1 (HOT-R1 drawn) | 27 September 2026 | By %s after HOT-R1 was drawn on boards A and E (%s): FW-C13, FW-C14 "
           "and FW-E10 read DRAWN with the parts' designators (`A:R216`, `E:Q11`, `E:R58`); FW-C14 gains the `EXP_INT` "
           "service (the port read, the PCA9555 errata) and the once-a-second poll, FW-E10 the watchdog bound under FW-C14's "
           "3 s; section 9's hot stop line follows |" % (MARK, SCA))
    t = t.replace(last[0], last[0] + "\n" + row, 1)
    open(p, "w", encoding="utf-8").write(t)
    print("edit_docs (w4ae): %s, rows FW-C13, FW-C14, FW-E10, section 9 and the change record" % rel)


def panel():
    rel = "v2/docs/PANEL.md"
    patch(rel, [
        ("| 24 | EXP_INT | the expanders' interrupt, active low |",
         "| 24 | EXP_INT | the expanders' interrupt, active low; it also carries the edges of the hot stop line HOT-R1, "
         "which A22's `U27` reads on P1.5 (`HW-FW-CONTRACT.md` FW-C14; %s, %s) |" % (SCA, MARK)),
        ("inputs: faults and status) and `U28`",
         "inputs: faults and status, and on P1.5 the hot stop line HOT-R1 from board E, pulled up by `R216`) and `U28`"),
    ])


def interfaces():
    rel = "v2/ecad/tools/pcb_interfaces.yaml"
    old = """      pins_history: "1 to 4 carried VIN_RAW until EQ-16 (27 September 2026); they are ground returns for the USB pair and
        the control line since, beside 5 to 7 and 11"
"""
    body = ("pin 12 (DOCK_SPARE on A, BLK_SPARE on E) carries the hot stop line HOT-R1 since 27 September 2026 (%s, %s): "
            "E's sensor controller GPIO19 (U10 pin 30) drives Q11 (2N7002, R58 100 k gate pull-down), an open drain onto "
            "BLK_SPARE; A's R216 10 k pulls DOCK_SPARE up to A's +3V3 and U27 pin 18 (P1.5) reads it, its INT on EXP_INT. "
            "Four states: 1 Hz below H1, 5 Hz H1, held low H2 (a shorted line stops the kit), held high the detector lost "
            "(E absent, unpowered, in reset or the contact open). Only E pulls down and only A pulls up, so neither board "
            "back-powers the other; a slow logic level (LOW_SPEED_OR_DC in both board tables) and a declared safety line on "
            "both (SCH-004: A listens, safe high by R216; E is its source). Firmware: v2/docs/HW-FW-CONTRACT.md FW-C13, "
            "FW-C14 and FW-E10; the path read by v2/docs/records/w4ae/hot_r1_trace.py" % (SCA, MARK))
    new = old + "\n".join(textwrap.wrap('      hot_r1: "%s"' % body, width=120, subsequent_indent="        ",
                                        break_long_words=False, break_on_hyphens=False)) + "\n"
    patch(rel, [(old, new)])
    import yaml
    y = yaml.safe_load(open(os.path.join(ROOT, rel), encoding="utf-8"))
    def find(x):
        if isinstance(x, dict):
            if "IF-AE-DOCK" in x: return x["IF-AE-DOCK"]
            for v in x.values():
                r = find(v)
                if r: return r
        return None
    d = find(y)
    assert d and "HOT-R1" in d.get("hot_r1", "") and d["pins"][12] == "DOCK_SPARE", "IF-AE-DOCK did not parse as intended"


def sources():
    rel = "v2/vendor/sources.txt"
    p = os.path.join(ROOT, rel); t = open(p, encoding="utf-8").read()
    if "zhengxin/zhengxin-ss12-ss120-c51897884.pdf" in t:
        print("edit_docs (w4ae): %s already names the sheet" % rel); return
    line = ("zhengxin/zhengxin-ss12-ss120-c51897884.pdf   # https://jlcpcb.com/api/file/downloadByFileSystemAccessId/"
            "8756866952981819392 (the JLCPCB parts record of LCSC C51897884, 'SS14 | Zhengxin | SMB(DO-214AA)': its data "
            "manual, the record naming no official link; LCSC's product API holds no record of the code and no maker's own "
            "copy was found), fetched 2026-09-27T14:05Z by %s, sha256 a9f62a305c3afb75 (SS12 THRU SS120, 3 pages, footer "
            "ZHENGXINSEMICONDUCTORS; cited by gen_sch_e.py D7, D8 and the FAN1_SW and FAN2_SW nodes, %s; lower confidence: "
            "a distributor-served copy whose PDF title names another product and which reads IO 1.0 A in its ratings and "
            "2.0 A on FIG1)" % (MARK, SCB))
    open(p, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + line + "\n")
    print("edit_docs (w4ae): %s, one line" % rel)


def grade():
    rel = "v2/docs/parts/grade-sources.yaml"
    old = """- code: C51897884
  part: SS14 (Zhengxin, SMB)
  maker: ''
  where: inside
  source:
    class: none read
  note: 'no range read in any sheet or record this session: TBD'
"""
    new = """- code: C51897884
  part: SS14 (Zhengxin, SMB)
  maker: Zhengxin
  min_c: -55
  max_c: 125
  kind: TJ
  where: inside
  source:
    class: maker sheet as JLCPCB serves it
    document: v2/vendor/zhengxin/zhengxin-ss12-ss120-c51897884.pdf
    url: https://jlcpcb.com/api/file/downloadByFileSystemAccessId/8756866952981819392
    sha256: a9f62a305c3afb750242a3d33eb66272dcdbff9ff8bf13ab00d8a7dda3edece2
    fetched_utc: '2026-09-27T14:05:57Z'
    clause: p.1
    quote: 'Junction temperature Tj -55~+125 (the SS12 to SS14 column; SS15 to SS120 read -55 ~+150)'
  note: 'filed by %s (%s); storage -55 ~+150'
""" % (MARK, SCB)
    patch(rel, [(old, new)])


def eq():
    rel = "v2/docs/handover/ENGINEERING-QUESTIONS.md"
    p = os.path.join(ROOT, rel); t = open(p, encoding="utf-8").read()
    if MARK in t:
        print("edit_docs (w4ae): %s already carries this stream's edits" % rel); return
    old_i = ("| EQ-22 | The hot stop's signal path HOT-R1 is in neither board A's nor board E's generator | A. design work | "
             "2, 3, 5, 8 | A, E | REQ-077 (FAIL until drawn); the layout entry of A and E |")
    new_i = ("| EQ-22 | The hot stop's signal path HOT-R1 is in neither board A's nor board E's generator (drawn since 27 "
             "September 2026, %s) | A. design work | 2, 3, 5, 8 | A, E | answered at desk: REQ-077 reads INCONCLUSIVE, "
             "held by FEA-004; the firmware rows and P15 remain |" % SCA)
    assert t.count(old_i) == 1, "EQ-22's index row moved"
    t = t.replace(old_i, new_i)
    s = t.index("### EQ-22."); e = t.index("\n### ", s + 5)
    sec = t[s:e]
    lines = sec.split("\n")
    def upd(prefix, add):
        hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
        assert len(hits) == 1, (prefix, len(hits))
        l = lines[hits[0]]
        assert l.endswith(" |"), l[-20:]
        lines[hits[0]] = l[:-2] + " " + add + " |"
    upd("| **Attempts and results** |",
        "**Drawn on 27 September 2026 by %s (%s, S-57 closed):** board E's `U10` pin 30 drives `Q11` (2N7002, `R58` "
        "100 k gate pull-down) onto `BLK_SPARE`, board A's `R216` (10 k) pulls `DOCK_SPARE` up to `+3V3`; both boards "
        "regenerated on the KiCad box with main's chain, main's generators reproducing main's files and the candidates "
        "differing from them only in those parts, `U10` pin 30, D7 and D8's order code and the two connectors' values "
        "(`records/w4ae/parity/`); `records/w4ae/hot_r1_trace.py` reads every hop from the gauge's reader to `PI_KILL` and "
        "the LTC2954's `KILL` on the committed netlists with no compute module in the path (it stops at `U10` pin 30 on "
        "main's netlists at `91894cd7`); PWR-001, PWR-002, SCH-004 and the contracts on A and E read unchanged or PASS "
        "(`records/w4ae/readings/`). REQ-077 goes FAIL to INCONCLUSIVE at desk, held by FEA-004." % (MARK, SCA))
    upd("| **Recommended next action** |",
        "Since the drawing: the panel and sensor controller firmware of FW-C13, FW-C14 and FW-E10, then P15 and E3-H on "
        "the bench; S-58 stays with the D-09 reviewer.")
    t = t[:s] + "\n".join(lines) + t[e:]
    open(p, "w", encoding="utf-8").write(t)
    print("edit_docs (w4ae): %s, EQ-22's index row and two rows of its section" % rel)


STEPS = [("conops", conops), ("hwfw", hwfw), ("panel", panel), ("interfaces", interfaces), ("sources", sources),
         ("grade", grade), ("eq", eq)]
for name, fn in STEPS:
    if ONLY is None or name in ONLY:
        fn()
