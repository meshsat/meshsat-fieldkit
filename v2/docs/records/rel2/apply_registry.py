"""The registry half of the second release attempt of layers 1 to 3 (27 September 2026, MESHSAT-1357, branch fnd/rel2
from main 953f5658). Every edit is made by record id with its old text asserted, and every new id is the next free one
of its kind in the file it runs on, so the script re-applies on a main that has moved (another branch, set 5, also adds
SC and S records): the ids it took are printed and written to the JSON file named as its argument, which the
documents' edit script reads. Run from the worktree root. Taken by the session under the owner's standing rule of 26
September 2026; nothing here is the owner's.

  - layer 3 R2 (layer 2 B4 (c)): SC-21 governs M1's duration, stated once in the header's id paragraph, in SC-21 and in
    L-02; the owner's part of M1's failing balance becomes the owner action M-nn (REQ-072 waits on it); S-53 keeps the
    session's part; REQ-016 and REQ-072 record that they cannot both hold on D-06's architecture; REQ-072 stays FAIL.
  - layer 2 B2 and layer 3 R4: REQ-077's prototype acceptance gains the forced trigger at room temperature (TEST-PLAN
    P15) and E3-H's stepped run; its desk half and its FAIL are unchanged.
  - layer 3 R5: SC-HF-01 to SC-HF-06 of HW-FW-CONTRACT.md section 8 become the registry's session choices at the next
    free SC numbers, each with question, taken, why (with its "Reverse by") and `drafted_as`; S-59 and S-61 cite them.
  - layer 1 m1: SC-13's reason no longer says CFL-010 stays open.
  - layer 2 B4 (e): CFL-017 names the engineering question written for it.
"""
import json, re, sys

P = 'v2/ecad/tools/pcb_requirements.yaml'
t = open(P, encoding='utf-8').read()
t0 = t


def rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1
    j = t.find('\n  - id: ', i + 5)
    k = t.find('\n\n#', i)                      # a section's closing comment ends its last entry
    ends = [x for x in (j, k) if x > 0]
    return i, (min(ends) + 1 if ends else len(t))


def sub_in(t, rid, a, b):
    i, j = rec(t, rid); r = t[i:j]
    assert r.count(a) == 1, (rid, r.count(a), a[:90]); assert a != b
    return t[:i] + r.replace(a, b) + t[j:]


def sub(t, a, b):
    assert t.count(a) == 1, (t.count(a), a[:90]); assert a != b
    return t.replace(a, b)


def wrap(text, indent=6, width=120):
    words = text.split(); lines = []; cur = ' ' * indent
    for w in words:
        if len(cur) + 1 + len(w) > width and cur.strip(): lines.append(cur); cur = ' ' * indent + w
        else: cur = (cur + ' ' + w) if cur.strip() else cur + w
    lines.append(cur)
    return '\n'.join(lines) + '\n'


def folded(key, text, indent=4):
    return ' ' * indent + key + ': >-\n' + wrap(text, indent + 2)


def next_free(prefix, t):
    n = [int(m) for m in re.findall(r'\n  - id: %s-(\d{2})\n' % prefix, t)]
    return max(n) + 1


SC0 = next_free('SC', t)
M = 'M-%02d' % next_free('M', t)
# the engineering question and the test row this change names, next free in the pages that will carry them
EQ = 'EQ-%02d' % (max(int(x) for x in re.findall(r'^### EQ-(\d{2})\.', open('v2/docs/handover/ENGINEERING-QUESTIONS.md',
                                                                         encoding='utf-8').read(), re.M)) + 1)
PT = 'P%d' % (max(int(x) for x in re.findall(r'^\| P(\d+) \|', open('v2/docs/TEST-PLAN.md', encoding='utf-8').read(),
                                              re.M)) + 1)
SC = {'SC-HF-%02d' % k: 'SC-%02d' % (SC0 + k - 1) for k in range(1, 7)}
print('apply_registry: session choices', SC, 'owner action', M, 'question', EQ, 'test row', PT)

# ---- (1) R2: one governing ruling for M1's duration ------------------------------------------------------------
t = sub(t, """# decisions), session choices SC-nn, open items S-nn (session), M-nn (an owner action), L-nn (later, money) and D-18
# (conditional). L-02 keeps its id: its class was corrected to OWNER_ACTION (D-06 leaves the value to the owner).
""", """# decisions), session choices SC-nn, open items S-nn (session), M-nn (an owner action), L-nn (later, money) and D-18
# (conditional). A closer's draft name for a session choice (SC-HF-02 of HW-FW-CONTRACT.md section 8) is recorded as
# that choice's `drafted_as`, and the validator refuses any SC- id the registry or a page of v2/docs/ or
# v2/docs/handover/ cites that no entry defines. L-02 keeps its id: D-06 left M1's mission duration for the owner to set
# later (its class was corrected from LATER to OWNER_ACTION), and under the owner's standing rule of 26 September 2026
# the session's SC-21 (72 hours) governs it and closes it, recorded as the session's and replaced by the owner's own
# setting whenever he gives one; what only the owner can decide about M1's failing energy balance is %s.
""" % M)

t = sub(t, """#
# PART NAMES IN STATEMENTS.""", """#
# THE SECOND RELEASE ATTEMPT OF LAYERS 1 TO 3 (27 September 2026, MESHSAT-1357, after the release checks at f2b7fa66,
# v2/docs/reviews/REVIEW-LAYER-{1,2,3}-RELEASE-2026-09-27.md). By record id through
# v2/docs/records/rel2/apply_registry.py: M1's duration governed by SC-21 (layer 3, R2) with the owner's part of its
# failing balance as %s; REQ-077's forced trigger at room temperature (layer 2 B2, layer 3 R4); SC-HF-01 to SC-HF-06
# entered as %s to %s with their draft names, and the validator refusing an SC- id no entry defines (layer 3, R5).
#
# PART NAMES IN STATEMENTS.""" % (M, SC['SC-HF-01'], SC['SC-HF-06']))

t = sub(t, """# What is still open. SESSION items are engineering the session decides and records with authority SESSION;
# OWNER_ACTION is something the owner has ruled that he does or sets himself; LATER a money item he approves from a
# quote; CONDITIONAL arises only if its condition does. A record that depends on one says so in `waits_on`.
""", """# What is still open. SESSION items are engineering the session decides and records with authority SESSION;
# OWNER_ACTION is something the owner has ruled that he does or sets himself, or that only he can do because it reopens
# his own ruling or accepts a residual risk (reported to him, never asked, under his standing rule of 26 September
# 2026); LATER a money item he approves from a quote; CONDITIONAL arises only if its condition does. A record that
# depends on one says so in `waits_on`.
""")

t = sub_in(t, 'SC-21', """      9 to 36 V entry, D-01's deferred second pack, a larger pack (D-06). Reported to the owner as a consequence of D-06
      with the session's 72 hours, not asked; the mission is not shortened. Reverse: the owner's own setting replaces
      it.
""", """      9 to 36 V entry, D-01's deferred second pack, a larger pack (D-06). Reported to the owner as a consequence of D-06
      with the session's 72 hours, not asked; the mission is not shortened. Reverse: the owner's own setting replaces
      it. Stated once on 27 September 2026 (the second release attempt of layers 1 to 3; layer 3's release check,
      finding R2): this choice GOVERNS M1's duration. D-06 left the value for the owner to set later, and his standing
      rule of 26 September 2026 has the session take the recommended option where a value is left and record it as its
      own; it is recorded so, it closes L-02, and the owner's own setting replaces it whenever he gives one. It decides
      nothing about the routes that would carry the failing balance by reopening an owner ruling or by accepting a
      residual, which are the owner's (%s); the session's part is S-53. ENGINEERING-QUESTIONS EQ-13 states the same.
""" % M)

t = sub_in(t, 'L-02', """      The mission duration for M1's pack-plus-solar energy balance, which D-06 leaves for the owner to set later (the id
      is kept; its class was LATER, which is for money). The session set a planning value under the owner's standing
      rule; the owner's own setting replaces it.
""", """      The mission duration for M1's pack-plus-solar energy balance, which D-06 leaves for the owner to set later (the id
      is kept; its class was LATER, which is for money, then OWNER_ACTION). SC-21 governs it: under the owner's
      standing rule of 26 September 2026 the session set 72 hours, recorded as the session's, and the owner's own
      setting replaces it whenever he gives one (stated once on 27 September 2026, layer 3's release check, R2). What
      only the owner can decide about M1's failing balance is %s.
""" % M)

t = sub_in(t, 'S-53', """    title: >-
      M1's energy judged at layer 4 (REQ-072; the layer-2 closer's finding, SC-21). Binding: the aged
      pack's about 108 Wh bridges 2.5 to 5.0 h of darkness against nights of about 7 to 16 h at 52 N, so on pack and
      solar alone M1 stops every night whatever the solar rating (D-06's one pack; D-01's deferred second pack). Second:
      the solar path's rating, board A's front end and board E's LT8705A stage taking 100 W where M1's 72 hours in
      PS-IDLE-SPEC on the reference day need a panel of about 270 W. Routes, none taken: an overnight input on the 9 to
      36 V entry, D-01's deferred second pack, a larger pack (D-06), a re-rated input path; or record that prototype 1
      does not meet M1, a residual only the owner can accept. A shorter mission is not the remedy (CONOPS section 3,
      M1). The reference day is the design month's (September, SC-37); a month with less sun asks more of the
      panel, and the judgement records that beside it. Reported to the owner at the next checkpoint, not asked.
""", """    title: >-
      M1's energy judged at layer 4, the session's part (REQ-072; the layer-2 closer's finding, SC-21). Binding: the
      aged pack's about 108 Wh bridges 2.5 to 5.0 h of darkness against nights of about 7 to 16 h at 52 N, so on pack
      and solar alone M1 stops every night whatever the solar rating (D-06's one pack; D-01's deferred second pack).
      Second: the solar path's rating, board A's front end and board E's LT8705A stage taking 100 W where M1's 72 hours
      in PS-IDLE-SPEC on the reference day need a panel of about 270 W. The session's route is the re-rated input path,
      judged before boards A and E enter layout (it carries the day, not the night); an overnight input on the 9 to 36 V
      entry needs no board change but changes M1's setting, so it is stated in CONOPS M1 and not taken. The routes that
      reopen an owner ruling (D-01's deferred second pack, a larger pack under D-06) and recording that prototype 1 does
      not meet M1, a residual only the owner can accept, are the owner action %s (split out on 27 September 2026,
      layer 3's release check, R2). A shorter mission is not the remedy (CONOPS section 3, M1). The reference day is the
      design month's (September, SC-37); a month with less sun asks more of the panel, and the judgement records that
      beside it. Reported to the owner at the next checkpoint, not asked.
""" % M)

t = sub(t, """      made part: no board moves (J_QMX, J_HF and J_RF2 stay) and nothing is bought. ENGINEERING-QUESTIONS EQ-24.

# Items that left the open list""", """      made part: no board moves (J_QMX, J_HF and J_RF2 stay) and nothing is bought. ENGINEERING-QUESTIONS EQ-24.
  - id: %s
    class: OWNER_ACTION
    status: OPEN
%s
# Items that left the open list""" % (M, folded('title', (
    "M1's failing energy balance, the owner's part (27 September 2026, the second release attempt of layers 1 to 3; "
    "layer 3's release check, R2; reported to the owner, not asked, under his standing rule of 26 September 2026). "
    "On D-06's one 4S3P pack the kit does not run M1 through a single night on pack and solar alone, whatever the "
    "panel's rating, and REQ-072 reads FAIL at desk (S-53 is the session's part: the input path's rating). Only the "
    "owner can take the routes that carry the night by reopening his own rulings, a larger pack (D-06) or the second "
    "pack D-01 defers, which has no location found; or accept, as a residual risk, that prototype 1 does not meet "
    "M1 on pack and solar alone. The session's recommendation and the arithmetic are ENGINEERING-QUESTIONS EQ-13. "
    "Decided before boards A, E and P enter layout, because the answer can move the pack pocket, board E's solar stage "
    "(D4, F2, J_SOLAR) and board A's front end. Until then REQ-072 stays FAIL, CONOPS M1 states that a night needs an "
    "overnight input on the 9 to 36 V entry, and nothing is lowered: neither REQ-016 nor REQ-072 is restated to fit."))))

# ---- (2) R2: REQ-016 and REQ-072 cannot both hold on D-06's architecture -----------------------------------------
t = sub_in(t, 'REQ-016', """      the generator declares for the panel entry (gen_sch_e.py, the PV_P and PV_IN rails), not the clamp's 28 V
      standoff.
""", """      the generator declares for the panel entry (gen_sch_e.py, the PV_P and PV_IN rails), not the clamp's 28 V
      standoff. Recorded on 27 September 2026 (the second release attempt of layers 1 to 3; layer 3's release check,
      R2): on D-06's architecture (one 4S3P pack and this 100 W window) this record as stated and REQ-072 cannot both
      hold. REQ-072 fails the night whatever the panel, and its day asks about 266 W of panel where this window takes
      100 W. Which one gives way is decided by the input path's judgement (S-53, the session's, layer 4) and the
      owner's part (%s: a larger or second pack, or the residual), before boards A, E and P enter layout; until then
      neither record is restated and nothing is lowered.
""" % M)
t = sub_in(t, 'REQ-072', "    waits_on: [S-53]\n", "    waits_on: [S-53, %s]\n" % M)
t = sub_in(t, 'REQ-072', """      is the design month's (September); M1 carries no season, and a month with less sun asks more of the input path,
      which layer 4 records beside it (SC-37, second pass after Review B finding B5).
""", """      is the design month's (September); M1 carries no season, and a month with less sun asks more of the input path,
      which layer 4 records beside it (SC-37, second pass after Review B finding B5). Since 27 September 2026 (the
      second release attempt of layers 1 to 3; layer 3's release check, R2): SC-21 governs the duration, the record
      waits on the session's input-path judgement (S-53) and on the owner's part (%s), and on D-06's architecture it
      and REQ-016 as stated cannot both hold (REQ-016's notes). The FAIL at desk is carried as it stands.
""" % M)

# ---- (3) B2 and R4: REQ-077's forced trigger ------------------------------------------------------------------------
OLD_ACC = ("Desk (schematic): the committed netlists carry a path from the pack gauge's cell temperatures to the control "
           "that removes the kit's load which needs no compute module (HOT-R1, SC-50: board E's sensor controller to board "
           "A's expander input on the dock's spare contact, and on to the panel controller that owns the slot enables, the "
           "switched loads and PI_KILL), and the two thresholds sit, in the gauge's own reading, under its discharge "
           "over-temperature of 57.5 C and inside +60 C by the published terms of the battery packet's error budget "
           "(THERMAL-COORDINATION.md section 3; CONOPS section 4c); a configuration in which the cells' temperature "
           "reaches no controller that can remove load reads FAIL.")
OLD_PROTO = (" Prototype: TEST-PLAN E3-H, during E3-A and E3-L at +40 C, first on the pack and then on shore: where the "
             "hottest cell as the gauge reads it reaches the first threshold the kit sheds to its minimum load within 60 "
             "s, and where it reaches the second the kit shuts itself down, both before any cell surface reaches +59 C on "
             "the reference thermocouples and with no permanent protection action (the second level's over-temperature, "
             "the gauge's SOT, the chemical fuse F2); a run in which a cell surface reaches +59 C is ended at once and "
             "reads FAIL.")
NEW_PROTO = (" Prototype, on the pack and then on shore, in two parts. (1) Whatever a chamber reaches, the forced trigger "
             "at room temperature (TEST-PLAN @PT@): the gauge's hottest cell reading is driven past +56.5 C and then +57.0 "
             "C, and never to its discharge over-temperature of +57.5 C, by substituting one cell thermistor input, each "
             "setting read back in the gauge's DAStatus2(); at the second reading at or above +56.5 C the kit sheds to its "
             "minimum load within 60 s (every running module shut down on PI_SHDN_REQ and SLOT_EN1 to SLOT_EN3 dropped, "
             "the switched loads off, the charge held by the charger's CHRG_INHIBIT with the charger still carrying the "
             "kit on shore) with MASTER WARN and the e-paper naming the step and the reading, and the heat stage's module "
             "returns only once the reading is at or below +46.5 C and 30 minutes have passed since the stop; at the "
             "second reading at or above +57.0 C with H1 acting the kit shuts itself down through PI_KILL and stays off, "
             "on shore as well, until MAIN is pressed, and then raises no slot while the reading is above +46.5 C; HOT-R1 "
             "carries its four states (1 Hz below H1, 5 Hz in H1, held low in H2, held high with the sensor controller "
             "held in reset), a line held low stops the kit, and with the line held high the same two steps act on board "
             "B's TMP117 at +55.0 C and +56.0 C, released at +45.0 C; after each run the gauge's SafetyStatus() and "
             "PFStatus() show no discharge over-temperature and no permanent failure. (2) TEST-PLAN E3-H, during E3-A and "
             "E3-L at +40 C and in its stepped run beyond the envelope to at most +55 C: where the hottest cell as the "
             "gauge reads it reaches the first threshold the kit sheds to its minimum load within 60 s, and where it "
             "reaches the second the kit shuts itself down, both before any cell surface reaches +59 C on the reference "
             "thermocouples and with no permanent protection action (the second level's over-temperature, the gauge's "
             "SOT, the chemical fuse F2); a run in which a cell surface reaches +59 C is ended at once and reads FAIL. A "
             "step that acted in neither part reads NOT_VERIFIED, never PASS; a thermal run in which no threshold was "
             "reached is recorded with its peak readings and does not stand in for (1).").replace('@PT@', PT)
i, j = rec(t, 'REQ-077'); r = t[i:j]
a0 = r.index('    acceptance: >-\n'); a1 = r.index('    provisional: >-\n')
assert ' '.join(r[a0 + len('    acceptance: >-\n'):a1].split()) == OLD_ACC + OLD_PROTO, 'REQ-077 acceptance moved'
r = r[:a0] + folded('acceptance', OLD_ACC + NEW_PROTO) + r[a1:]
t = t[:i] + r + t[j:]
t = sub_in(t, 'REQ-077', """      - "v2/docs/CONOPS.md section 4c"
      - "session choice SC-49"
""", """      - "v2/docs/CONOPS.md section 4c"
      - "v2/docs/TEST-PLAN.md sections 6 (E3-H) and 7 (%s)"
      - "v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf sections 2.7, 3.20, 11.2.1.4 and 13.1.48"
      - "session choice SC-49"
""" % PT)
t = sub_in(t, 'REQ-077', """      there, recorded and not waived, while this record's own line (the cells inside +60 C) still holds.
""", """      there, recorded and not waived, while this record's own line (the cells inside +60 C) still holds. Since 27
      September 2026 (the second release attempt of layers 1 to 3; layer 2's release check, B2, and layer 3's, R4) the
      prototype acceptance has the forced trigger %s, so the stop is verifiable whatever a chamber reaches: the gauge's
      own External 1 to 4 Temp Offset (TI SLUUAQ3A section 11.2.1.4, at most 12.7 K) cannot reach the thresholds from
      room temperature, so one thermistor input is substituted and never left open, because an open thermistor is a
      permanent failure of the gauge (section 3.20); E3-H gains a stepped run beyond the envelope, and E3-L's pass line
      is unchanged.
""" % PT)

# ---- (4) R5: SC-HF-01 to SC-HF-06 as the registry's session choices --------------------------------------------------
HF = 'v2/docs/HW-FW-CONTRACT.md'
ENTRIES = [
    ('SC-HF-01', "Which heartbeat source the hardware-firmware contract takes (HW-FW-CONTRACT.md section 2).",
     "The compute module's GPIO16 under the bridge software drives its slot's heartbeat line (HB1 to HB3); the panel "
     "controller (GPIO10 to 12) and the three I/O supervisors (pins 30 to 32) only listen, and a slot is alive while its "
     "line toggles at 1 Hz (FW-B01, FW-B11, FW-C05).",
     "The netlist settles it: HB_CM1 is the CM5's GPIO16 (gen_sch_b.py:257), joined through the level stage Q105 "
     "(gen_sch_b.py:822) to HB1, which the panel controller and every supervisor only read; ARCHITECTURE.md section 10.1 "
     "already says so, and PANEL.md section 3's supervisor-driven wording was corrected with the contract.",
     "a generator change that moves the heartbeat's source",
     [HF + " sections 2 and 8"]),
    ('SC-HF-02', "How the kit I2C bus meets its targets' 300 ns rise time (HW-FW-CONTRACT.md sections 6.3 to 6.7; "
     "finding HF-F01).",
     "Three segments behind two TI TCA9517A: the TRUNK (the master, board C, and on board B the expanders U6 and U7, the "
     "ATECC608B, the DS3231 and the TMP117); SEG-A (board A's targets and board D's) behind a TCA9517A on board A, its A "
     "side local, EN tied high, 1.2 k pull-ups to board A's +3V3; SEG-S (board B's three supervisors, the TPS23861 and "
     "the KSZ9897R) behind a TCA9517A on board B, its B side theirs, EN from U7 IO1_7 through a delay and isolated by "
     "default, 1.5 k pull-ups to +3V3_DEV; the copper allowances of section 6.6 handed to layout. Owed on boards A and B "
     "(S-59).",
     "As one segment the bus cannot meet the 300 ns rise of its BQ25731, TPS23861 and ATECC608B (section 6.3, "
     "v2/docs/records/hc5/kit_i2c_budget.out.txt) and its pull-ups are at the 3 mA floor; the held TCA9517A "
     "(v2/vendor/ti/ti-tca9517a-i2c-buffer.pdf, SCPS245E) takes 400 pF a side, and SEG-S also isolates the supervisors "
     "from the secure element outside the panel's status windows, which narrows ZEROIZE's R7.",
     "a part with no static offset on either side, or a rise-time accelerator on one segment, either taken only on a "
     "maker's document showing it meets the 300 ns targets at the bound (section 6.5)",
     [HF + " sections 6.3 to 6.7 and 8", "v2/docs/records/hc5/kit_i2c_budget.out.txt"]),
    ('SC-HF-03', "The kit I2C bus clock (HW-FW-CONTRACT.md section 6.4).",
     "Standard-mode: 100 kHz programmed, at least 90 kHz achieved on every segment (FW-K01, V-K01).",
     "Nothing on the bus needs more than the ZEROIZE budget's clock, and that budget, re-run at 90 kHz "
     "(v2/docs/records/hc5/zer/zer_budget.py and its outputs), holds every pass line (nominal sequence 0.521 s, longest "
     "transfer 6.72 ms against the 10 ms HAL timeout).",
     "a measured rise time that allows Fast-mode on every segment, together with a need for it",
     [HF + " sections 6.4 and 8", "v2/docs/records/hc5/zer/zer_budget.py"]),
    ('SC-HF-04', "The hot-plug rules pcb_interfaces.yaml marked '(proposed)' (HW-FW-CONTRACT.md section 8).",
     "Adopted as written: IF-BC-PANEL, IF-AB-RIBBON, IF-AB-POWER, IF-A-PA and IF-LID-HF are mated and unmated with the "
     "kit off.",
     "A partly seated ribbon can assert PI_KILL or drop SLOT_EN, and the VH leads carry up to 6 A; ARCHITECTURE.md "
     "section 12 marks the rules as the session's since the same day.",
     "an interlock that makes live mating safe",
     [HF + " section 8", "v2/ecad/tools/pcb_interfaces.yaml"]),
    ('SC-HF-05', "The I/O supervisors' clock stretch on the kit bus and the master's SCL hold (HW-FW-CONTRACT.md "
     "sections 3.7 and 8).",
     "Each supervisor stretches SCL for at most 1 ms (FW-B08, V-B08); the master never holds SCL low for more than "
     "10 ms, and recovers a stuck bus with nine SCL pulses and a STOP (FW-K04, V-K02).",
     "The BQ25731, the INA226 and the ATECC608B reset their bus interface after 25 to 35 ms of SCL low (their SMBus "
     "timeouts: TI SLUSE66A 8.6, TI SBOS547, Microchip DS40002239B), so a hold under 10 ms keeps them attached.",
     "a target with a shorter bus timeout, which would lower both bounds (the contract's draft says none is needed)",
     [HF + " sections 3.7 and 8"]),
    ('SC-HF-06', "Where the Xenarc 709GNK monitor's touch USB connects, and how it follows the display owner "
     "(HW-FW-CONTRACT.md section 8; the audit's unresolved decision, ASSEMBLY.md having named 'a B16 slot hub header' "
     "with no designator).",
     "Board D's spare hub port J_USB3 (PH 1x4), through a USB A receptacle to PH adapter lead made up at build; the "
     "touch follows the display owner by the HAL's network share (FW-B19); carried in pcb_interfaces.yaml IF-MON, "
     "ARCHITECTURE.md section 12, ASSEMBLY.md section 4 and build step 9, and PANEL.md section 1. Its costs are finding "
     "HF-F06, owed on board D before its layout entry (S-61).",
     "Every one of board B's twelve hub ports is allocated (gen_sch_b.py:764-766); J_USB3 exists for a lead made up at "
     "build, needs no board B change (board B's floor plan is open under FB-FAB-6), matches the leads table's PH "
     "housing, and a full-speed hub carries a HID touch (USB 2.0 section 7.1 Table 7-1, "
     "v2/docs/records/hc5/usb-2-0-clauses-cited.md); appendix 32.52 makes the HAL's network share the kit's way to reach "
     "a device on another module.",
     "a board B port reallocation or added downstream capacity on board B, after which J_USB3 returns to spare",
     [HF + " section 8", "v2/docs/records/hc5/usb-2-0-clauses-cited.md"]),
]
new = ''
for draft, q, taken, why, rev, src in ENTRIES:
    why = (why + " Drafted as %s in HW-FW-CONTRACT.md section 8 on 27 September 2026 by the layer 5 closer, and entered "
           "here by the second release attempt of layers 1 to 3 the same day (layer 3's release check, R5), so that "
           "the registry is the one record of it. Reverse by %s." % (draft, rev))
    new += ('  - id: %s\n    authority: SESSION\n    under: standing-rule\n    taken_on: "2026-09-27"\n'
            '    drafted_as: %s\n' % (SC[draft], draft)) + folded('question', q) + folded('taken', taken) + \
           folded('why', why) + '    source: [%s]\n' % ', '.join('"%s"' % s for s in src)
t = sub(t, """    source: ["v2/docs/CONOPS.md section 4c", "v2/docs/ARCH-PCB-B-IOHA.md section 8", "owner ruling D-02b"]

# What is still open.""", """    source: ["v2/docs/CONOPS.md section 4c", "v2/docs/ARCH-PCB-B-IOHA.md section 8", "owner ruling D-02b"]
%s
# What is still open.""" % new)

t = sub_in(t, 'S-59', """      (hc5-layer5: SC-HF-02) The kit I2C bus drawn as the session's three segments of v2/docs/HW-FW-CONTRACT.md section 6.5:
""", """      (hc5-layer5: %s, drafted as SC-HF-02) The kit I2C bus drawn as the session's three segments of v2/docs/HW-FW-CONTRACT.md section 6.5:
""" % SC['SC-HF-02'])
t = sub_in(t, 'S-61', """      (hc5-layer5: SC-HF-06, HF-F06) The monitor's touch USB takes board D's spare hub port J_USB3 (the session's choice
      SC-HF-06 of v2/docs/HW-FW-CONTRACT.md section 8; no board B change; the HAL shares it to the display owner, FW-B19).
""", """      (hc5-layer5: %s, drafted as SC-HF-06; HF-F06) The monitor's touch USB takes board D's spare hub port J_USB3 (the
      session's choice %s, drafted as SC-HF-06 in v2/docs/HW-FW-CONTRACT.md section 8; no board B change; the HAL shares it
      to the display owner, FW-B19).
""" % (SC['SC-HF-06'], SC['SC-HF-06']))

# ---- (5) layer 1 m1: SC-13's reason, and layer 2 B4 (e): CFL-017's engineering question ------------------------------
t = sub_in(t, 'SC-13', """      The SIM TVS array of at most 10 pF (section 4.1.7) and the eSIM variant's code stay owed under S-13, so CFL-010
      stays open. Reverse by making the eSIM configuration the default build once that code is named; no board change
      either way.
""", """      When it was taken the SIM TVS array of at most 10 pF (section 4.1.7) and the eSIM variant's code were owed under
      S-13, and CFL-010 was open; board B's round 8 draws the arrays (U222 and U223, CON-025) and CFL-010 is resolved on
      this description, so S-13 holds only the eSIM variant's order code (restated 27 September 2026, layer 1's release
      check, m1). Reverse by making the eSIM configuration the default build once that code is named; no board change
      either way.
""")
t = sub_in(t, 'CFL-017', """      hardware, cells rated beyond +60 C reopen D-06, and D-02a's scope is the owner's to read.
""", """      hardware, cells rated beyond +60 C reopen D-06, and D-02a's scope is the owner's to read. Its three routes, the
      session's recommendation and their cost are ENGINEERING-QUESTIONS %s (27 September 2026, the second release
      attempt of layers 1 to 3; layer 2's release check, B4 (e)).
""" % EQ)

assert t != t0
open(P, 'w', encoding='utf-8').write(t)
out = {'SC': SC, 'M': M, 'EQ': EQ, 'PT': PT}
if len(sys.argv) > 1: json.dump(out, open(sys.argv[1], 'w'), indent=1)
print('apply_registry: done', out)
