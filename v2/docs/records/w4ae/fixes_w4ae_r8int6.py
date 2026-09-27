#!/usr/bin/env python3
"""r8int6 (the integrator of set 6 of the handover, 27 September 2026), after stream w4ae's drafts:
  1. the independent check's observation on board B's PI_KILL conductor (w4ae check 1, an AI check) recorded as an open
     SESSION item at the next free S number: it is not new with stream w4ae and is not in its scope, and the check asked
     that it be recorded for board B and the module firmware contract;
  2. ENGINEERING-QUESTIONS.md EQ-19's attempts row gains board E's answer (stream w4ae's FAN1_SW and FAN2_SW nodes with
     D7 and D8's sheet), after board C's (stream w4c), so the question names what set 6 changed.
Idempotent by marker. Usage: fixes_w4ae_r8int6.py <repo root>"""
import json, os, re, sys, textwrap
import yaml

T = sys.argv[1]
REG = os.path.join(T, "v2/ecad/tools/pcb_requirements.yaml")
ids = json.load(open(os.path.join(T, "v2/docs/records/w4ae/ids.json")))
MARK = "Board B's PI_KILL conductor carries the drains of the three"
s = open(REG, encoding="utf-8").read()
if MARK not in s:
    have = {int(x) for x in re.findall(r"(?m)^  - id: S-(\d{2,3})$", s)}
    sid = "S-%02d" % (max(have) + 1)
    title = (MARK + " bidirectional 2N7002 level shifters Q103, Q203 and Q303 (gates on +3V3_CM1 to +3V3_CM3, sources on "
             "PI_KILL_CM1 to PI_KILL_CM3, each compute module's GPIO17; gen_sch_b.py level()), so a powered module that "
             "drives GPIO17 low can hold PI_KILL low against the panel controller's kill; H1 normally drops SLOT_EN first, "
             "but H2 can come inside H1's 60 s shutdown window. Found by the independent check of stream w4ae (27 September "
             "2026, an AI check) while it traced HOT-R1's H2 path (%s); not new with that stream and outside its scope. For "
             "board B's author and the module firmware contract: GPIO17 held an input on every module (HW-FW-CONTRACT.md), "
             "or a one-way stage from the panel's PI_KILL to the modules." % ids["SC_HOT_R1"])
    blk = "  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s\n" % (sid, "\n".join(textwrap.wrap(
        title, width=118, initial_indent=" " * 6, subsequent_indent=" " * 6, break_long_words=False, break_on_hyphens=False)))
    anchor = "\n\n# Items that left the open list"
    assert s.count(anchor) == 1
    s = s.replace(anchor, "\n" + blk.rstrip("\n") + anchor, 1)
    yaml.safe_load(s)
    open(REG, "w", encoding="utf-8").write(s)
    print("fixes_w4ae: %s added (board B's PI_KILL level shifters)" % sid)
EQ = os.path.join(T, "v2/docs/handover/ENGINEERING-QUESTIONS.md")
t = open(EQ, encoding="utf-8").read()
M2 = "**Board E (stream w4ae, 27 September 2026):**"
if M2 not in t:
    a = "**Status after stream w4c:** C reads PASS of 6 in the stream's scratch; the consolidated re-take takes it in the tree. |"
    assert t.count(a) == 1, "EQ-19: board C's status sentence is not there (apply stream w4c first)"
    b = (a[:-2] + " " + M2 + " FAN1_SW and FAN2_SW declared nodes at 17.35 V (CELL_F's 16.8 V plus the SS14's 0.55 V), D7 "
         "and D8 given their order code C51897884 with the sheet filed (%s); PWR-001 on E read PASS of 16 in the stream's "
         "scratch (INCONCLUSIVE of 16 before), S-76's board E half answered. |" % ids["SC_FAN"])
    t = t.replace(a, b)
    open(EQ, "w", encoding="utf-8").write(t)
    print("fixes_w4ae: EQ-19 carries board E's answer")
