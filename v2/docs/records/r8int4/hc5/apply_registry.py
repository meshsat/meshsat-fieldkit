#!/usr/bin/env python3
"""Layer 5 closer hc5 (MESHSAT-1357, 27 September 2026): its edits to v2/ecad/tools/pcb_requirements.yaml, as a script the
integrator can re-apply after other streams move the file. Text edits only; the file's formatting is kept. Idempotent:
each edit is skipped when its result is already there, and otherwise asserts that its anchor occurs exactly once. New
records take the next free number at the time they are applied and carry the marker `hc5-layer5` in their text, which is
how a second run finds them.

  1. CON-020: the supervisors' address block is 0x34 to 0x36 (I3-F01), never 0x30 to 0x32; the page citations follow.
  2. S-41: the same block in the H743 compatibility matrix.
  3. a new open item: SC-HF-02 (the kit bus in three segments) drawn on boards A and B, with the layout allowances.
  4. a new open item: finding HF-F02, INA226 U17 on the 54 V PoE rail over its 40 V absolute maximum.
  5. a new constraint: the kit I2C bus meets its strictest target's rise time on every segment (FAIL at desk as drawn).
  6. (pass 2, after review) two new open items: the monitor's touch USB on board D's J_USB3 (SC-HF-06) with its costs on
     board D (HF-F06), and the Geiger pulse level and the fan gate pull-downs on board E (HF-F07).

Run from the repository root:  python3 drafts/hc5/apply_registry.py
Then:  (cd v2/ecad/tools && python3 rules_lib.py requirements && python3 rules_render.py --requirements)"""
import hashlib, os, re, sys

ROOT = os.getcwd()
P = os.path.join(ROOT, "v2/ecad/tools/pcb_requirements.yaml")
MARK = "hc5-layer5"
s = open(P, encoding="utf-8").read()
log = []


def sha16(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:16]


def rep(old, new, marker=None):
    global s
    m = marker or new
    if m in s:
        log.append("already: " + m.strip()[:70]); return
    n = s.count(old)
    assert n == 1, "anchor found %d times, expected 1: %r" % (n, old[:100])
    s = s.replace(old, new); log.append("edited: " + old.strip()[:70])


def next_id(prefix):
    nums = [int(x) for x in re.findall(r"\n  - id: %s-(\d+)\n" % prefix, s)]
    return "%s-%03d" % (prefix, max(nums) + 1) if prefix == "CON" else "%s-%d" % (prefix, max(nums) + 1)


# 1. CON-020 ---------------------------------------------------------------------------------------------------------
rep('''      The three STM32H743 I/O supervisors' firmware is an I2C target on the kit bus at 0x30 to 0x32 only: never a
      master, never at address 0x60 (firmware rule Z-C3), so only the panel controller commands the secure element.''',
    '''      The three STM32H743 I/O supervisors' firmware is an I2C target on the kit bus at 0x34, 0x35 and 0x36 only: never a
      master, never at address 0x60 (firmware rule Z-C3) and never at 0x30 to 0x32, where the TPS23861's broadcast
      address 0x30 sits (I3-F01), so only the panel controller commands the secure element.''')
rep('''      review of the firmware shows no master transaction and no response at 0x60; the Z-EXP-C held-bus cases C-H1 to''',
    '''      review of the firmware shows no master transaction and no response at 0x60 or at 0x30 to 0x32 (bench V-B08 of
      v2/docs/HW-FW-CONTRACT.md); the Z-EXP-C held-bus cases C-H1 to''')
# r8int4 (27 September 2026): the layer-3 closer's re-anchoring (53292f81) moved these two citations to board B's round 8
# lines, gen_sch_b.py:1140 to :1381 and ARCH-PCB-B-IOHA.md:96 to :102; the anchor and the kept line follow them.
rep('''      - "v2/ecad/tools/gen_sch_b.py:1381"
      - "v2/docs/ARCH-PCB-B-IOHA.md:102"''',
    '''      - "v2/ecad/tools/gen_sch_b.py:1381"
      - "v2/docs/ARCH-PCB-B-IOHA.md section 6"
      - "v2/docs/ARCHITECTURE.md section 5.5 (I3-F01)"
      - "v2/docs/HW-FW-CONTRACT.md FW-B08"''')
rep('''      part, so it is the supervisors' address that has to move, in their firmware.

  - id: REQ-036''',
    '''      part, so it is the supervisors' address that has to move, in their firmware. Corrected 27 September 2026 by the
      layer 5 closer (hc5-layer5): the session's block 0x34 to 0x36 of ARCHITECTURE.md section 5.5 (I3-F01) replaces
      0x30 to 0x32 here, with the same block drafted into PANEL.md section 7, ARCH-PCB-B-IOHA.md section 6 and
      ZEROIZE.md Z-C3; the rule itself is unchanged. The kit bus these targets share is budgeted in
      v2/docs/HW-FW-CONTRACT.md section 6 (the session's three segments, SC-HF-02, put the supervisors behind a buffer
      the panel opens, which narrows R7 without replacing Z-C3).

  - id: REQ-036''', marker="Corrected 27 September 2026 by the\n      layer 5 closer (hc5-layer5)")

# 2. S-41 --------------------------------------------------------------------------------------------------------------
# On a8652172 the layer 6 closer (hc6, 99cde56b) rewrote S-41 around the delivered compatibility matrix, and its text
# already reads "I2C1 a target only at 0x34 to 0x36": the same block, so this edit is then skipped (c5, 27 September 2026).
_s41 = s[s.index("\n  - id: S-41\n"):s.find("\n  - id: ", s.index("\n  - id: S-41\n") + 1)]
if "0x34 to 0x36" in _s41 and "0x30 to 0x32" not in _s41:
    log.append("already: S-41 carries the 0x34 to 0x36 block (hc6's wording on a8652172, or this script's)")
else:
    rep('''      I2C1 as a target at 0x30 to 0x32, GPIO, the independent watchdog, SWD) retained with its DS12110 sources, and the''',
        '''      I2C1 as a target at 0x34 to 0x36, GPIO, the independent watchdog, SWD) retained with its DS12110 sources, and the''')

# 3 and 4. two open items, before the closed list ----------------------------------------------------------------------
ANCHOR = "\n# Items that left the open list, and what closed each"
assert s.count(ANCHOR) == 1, "the closed-items comment moved"
if ("%s: SC-HF-02" % MARK) in s:
    s_seg = re.search(r"\n  - id: (S-\d+)\n    class: SESSION\n    status: OPEN\n    title: >-\n      \(%s: SC-HF-02\)" % MARK, s).group(1)
    s_ina = re.search(r"\n  - id: (S-\d+)\n    class: SESSION\n    status: OPEN\n    title: >-\n      \(%s: HF-F02\)" % MARK, s).group(1)
    log.append("already: %s and %s" % (s_seg, s_ina))
else:
    s_seg = next_id("S"); s_ina = "S-%d" % (int(s_seg[2:]) + 1)
    block = '''  - id: %s
    class: SESSION
    status: OPEN
    title: >-
      (%s: SC-HF-02) The kit I2C bus drawn as the session's three segments of v2/docs/HW-FW-CONTRACT.md section 6.5:
      board A's targets and board D behind a TCA9517A on A (its A side local, 1.2 k pull-ups to A's +3V3, EN high);
      board B's three supervisors, TPS23861 and KSZ9897R behind a TCA9517A on B (its B side theirs, 1.5 k pull-ups, EN
      from U7 IO1_7 with a 10 k pull-down); the copper allowances of section 6.6 handed to layout. Until drawn, finding
      HF-F01 stands: as one segment the bus cannot meet the 300 ns rise of its BQ25731, TPS23861 and ATECC608B.
  - id: %s
    class: SESSION
    status: OPEN
    title: >-
      (%s: HF-F02) Board A's INA226 U17 senses the 54 V PoE rail with IN+ and IN- at the rail, over the part's 40 V
      absolute maximum and 36 V input range (TI SBOS547 5.1, 5.5 note 1); a damaged monitor can hold the kit bus. Open
      until board A's author moves the sense to the stage's VBAT side or the rail's return, or fits a part rated for the
      rail on its maker's document (v2/docs/HW-FW-CONTRACT.md section 7).
''' % (s_seg, MARK, s_ina, MARK)
    s = s.replace(ANCHOR, "\n" + block.rstrip("\n") + "\n" + ANCHOR, 1)
    # the blank line that separated the last open item from the comment is kept by the leading newline above
    s = s.replace("\n\n" + block.rstrip("\n") + "\n" + ANCHOR, "\n" + block.rstrip("\n") + "\n" + ANCHOR)
    log.append("added %s and %s" % (s_seg, s_ina))

# 5. the kit bus constraint, after CON-020 -----------------------------------------------------------------------------
if ("%s: kit I2C bus" % MARK) in s:
    log.append("already: the kit bus constraint")
else:
    cid = next_id("CON")
    out = "v2/docs/records/hc5/kit_i2c_budget.out.txt"; scr = "v2/docs/records/hc5/kit_i2c_budget.py"
    rec = '''  - id: %s
    kind: constraint
    parent: NEED-10
    statement: >-
      Every segment of the kit I2C bus meets, at its published-maximum pin capacitance and its copper, the rise time of
      the strictest target on it (300 ns for the BQ25731, the TPS23861, the ATECC608B and the ADS1115), with pull-ups no
      stronger than its weakest target's 3 mA sink at 0.4 V allows, at Standard-mode 100 kHz programmed and at least
      90 kHz achieved.
    acceptance: >-
      kit_i2c_budget.py reads every segment within its limit on the current netlists; after layout, the field-solver
      reading of each segment's copper is within the allowance of v2/docs/HW-FW-CONTRACT.md section 6.6; on the
      prototype, bench V-K01 measures tr at most 300 ns, tf between 12 and 100 ns and fSCL at least 90 kHz at each
      segment's farthest pin.
    allocated_to: [a, b, c, d, fw_panel]
    verification_method: [CALCULATION, MANUAL_REVIEW, PROTOTYPE_MEASUREMENT]
    verification_phase: SCHEMATIC
    final_phase: PROTOTYPE
    prototype_1: core
    prototype_1_basis: NAMED
    prototype_1_why: >-
      A condition of ZEROIZE of the secure element, which D-01 names as core: the panel controller reaches the secure
      element only over the kit bus (feasibility/ZEROIZE.md section 3.4), and the same bus carries every rail and radio
      enable and the charger's configuration.
    satisfied_by:
      rules: []
      decisions: []
    rule_coverage: NONE
    rulings: [D-03]
    waits_on: [%s]
    status: DEFINED
    evidence_result: FAIL
    evidence_phase: SCHEMATIC
    evidence_class: DESK_REVIEW
    evidence:
      - >-
          %s run on the netlists at e3aedb25 (%s): as one segment the pins and ribbons alone take 290 pF (SDA, published
          maxima) against the 269 pF the TPS23861's 0.8 to 2.3 V rise allows through the drawn 1.1 k, and 166 pF at typical
          pin capacitance leave 137 pF for copper where the committed layouts carry 1,568 mm (157 to 345 pF); the pull-ups
          already draw 2.94 mA of the weakest sinks' 3 mA. FAIL at desk, labelled as the session's AI desk review.
    evidence_bound_to: ["%s@%s", "%s@%s"]
    release_effect: BLOCKER
    source:
      - "v2/docs/HW-FW-CONTRACT.md section 6"
      - "v2/vendor/ti/bq25731-datasheet.pdf"
      - "v2/vendor/ti/tps23861-datasheet.pdf"
      - "v2/vendor/microchip/microchip-atecc608b-summary-DS40002239B.pdf"
      - "v2/vendor/ti/ti-tca9517a-i2c-buffer.pdf"
    source_check: VERIFIED
    notes: >-
      Created by the layer 5 closer (%s: kit I2C bus), 27 September 2026. The session took three segments behind two
      TCA9517A (SC-HF-02 of v2/docs/HW-FW-CONTRACT.md section 8), which reads within every limit at desk with the copper
      allowances of section 6.6; the constraint stays FAIL until boards A and B draw it (%s). The bus clock (100 kHz
      programmed, 90 kHz achieved at least) is the one feasibility/ZEROIZE.md's time budget holds at, re-run at 90 kHz.
''' % (cid, s_seg, scr, out, out, sha16(out), scr, sha16(scr), MARK, s_seg)
    a = "\n  - id: REQ-036\n"
    assert s.count(a) == 1, "REQ-036 anchor moved"
    s = s.replace(a, "\n" + rec + a, 1)
    log.append("added %s" % cid)

# 6. two more open items (pass 2), before the closed list ---------------------------------------------------------------
if ("%s: SC-HF-06" % MARK) in s:
    log.append("already: the touch USB and board E items")
else:
    nums = [int(x) for x in re.findall(r"\n  - id: S-(\d+)\n", s)]
    s_tch, s_gei = "S-%d" % (max(nums) + 1), "S-%d" % (max(nums) + 2)
    block = '''  - id: %s
    class: SESSION
    status: OPEN
    title: >-
      (%s: SC-HF-06, HF-F06) The monitor's touch USB takes board D's spare hub port J_USB3 (the session's choice
      SC-HF-06 of v2/docs/HW-FW-CONTRACT.md section 8; no board B change; the HAL shares it to the display owner, FW-B19).
      Owed on board D: a current limit on J_USB3's VBUS, which is +5V_D8 with no port switch, so a fault on the touch
      lead trips board A's U23 and takes board D down; and the J_USB3 budget line (0.05 A) set from the touch
      controller's measured draw, which USB 2.0 section 7.2.1 bounds at 100 mA unconfigured and 500 mA configured (V-B19).
  - id: %s
    class: SESSION
    status: OPEN
    title: >-
      (%s: HF-F07) Board E: the Geiger module's pulse reaches GPIO7 through 22 R only, and a 5 V class module can exceed
      the RP2040's IOVDD + 0.5 V absolute maximum (datasheet Table 622): pick the module, read its output stage, and add a
      divider or a clamp if needed; and give the fan switches Q9, Q10 discrete gate pull-downs instead of the RP2040's pad
      pull-down (v2/docs/HW-FW-CONTRACT.md section 7).
''' % (s_tch, MARK, s_gei, MARK)
    assert s.count(ANCHOR) == 1
    s = s.replace(ANCHOR, "\n" + block.rstrip("\n") + "\n" + ANCHOR, 1)
    s = s.replace("\n\n" + block.rstrip("\n") + "\n" + ANCHOR, "\n" + block.rstrip("\n") + "\n" + ANCHOR)
    log.append("added %s and %s" % (s_tch, s_gei))

assert chr(0x2014) not in s and chr(0x2013) not in s
open(P, "w", encoding="utf-8").write(s)
print("\n".join(log))
