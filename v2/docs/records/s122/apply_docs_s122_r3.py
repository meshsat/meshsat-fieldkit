#!/usr/bin/env python3
"""Stream s122, round 3 (S-122, MESHSAT-1357, 29 September 2026): the answer to the independent check of fnd/s122b at
83cb0640 (`checks/check-s122-2.md`: B1, m1 to m8).

1. B1: CONOPS.md section 4's Reduced row and section 4c's `SLOT_EN1` passage call three board B items owed or absent as
   generated. All three are drawn, and were where the passages were written (95e078a1) and at the baseline (c5430071):
   the supervisors' I2C status path since 458b2873 (DC-07), and board B's round 8 break-before-make of FAB-03 and
   back-power gating of FAB-02 (b) and (c) (DC-08). The absent sweep of `verdicts.py` (every CONOPS sentence stating
   something absent, owed, not drawn or not connected is judged TRUE or BASELINE) found one more: section 7's D-17 row
   calls board A's CC array owed, and board A carries it since 458b2873 (DC-09), and section 7a's HOT-R1 row, which
   DC-02 now names. CONOPS.md is not edited (the baseline rule); the status page gains rows DC-07 to DC-09.
2. m3: DC-03 and DC-04 say that the baseline's value was already wrong at its reading (45bde541, a9f212c7), and the
   section's lead says what such a note means.
3. m4: the baselines table names the file CONOPS.md carries since stream s122 restored it: `6cb7b241cb84d729` at c5430071.
4. m1, m2: PANEL.md line 156 and V2-SPEC.md line 24 cite `feasibility/EMCON.md` section 0a.1 for the per-radio circuit
   in place of `CONOPS.md` section 4b; V2-SPEC.md records it as correction 33.
Every part, pin, net and registry value the new text names is asserted first (the assertion language of `verdicts.py`,
netlists at a commit included); every old passage is found once and every new one reads back once, no dash; each
document re-parses; CONOPS.md is asserted unchanged at c5430071's file. Refuses a second run.
Run: python3 apply_docs_s122_r3.py [--check]."""
import os, re, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import verdicts as V  # noqa: E402
import judgements as J  # noqa: E402

TAG = "apply_docs_s122_r3"
BASE = "83cb0640"          # the tip check-s122-2 read
CON = "v2/docs/CONOPS.md"
EMC = "v2/docs/feasibility/EMCON.md"
DST = "v2/docs/handover/DEFINITION-STATUS.md"
PNL = "v2/docs/PANEL.md"
SPC = "v2/docs/V2-SPEC.md"
DOCS = {PNL: "9acc3b09e25d7b45", SPC: "6e56e0cec9a1db2d", DST: "8f550108215bb8de"}
CONOPS_BASELINE = "6cb7b241cb84d729"
NETS = {"A": "6c40250c47195ebb", "B": "3ef9b8c49a01b728", "C": "c9f7394594201045", "D": "a2d48972d171aad1",
        "E": "2ed95a0e8069ebf8", "P": "20c7b0795593d761"}

# ------------------------------------------------------------------ what the new text names, asserted
ROW7_A = J.SUPI2C + ["B@1f614233:U%s@PB%s=unconnected-(U%s-PB%s-Pad%s)" % (u, pb, u, pb, pad)
                     for u in ("41", "51", "61") for pb, pad in (("6", "92"), ("7", "93"))] + ["DOC:v2/docs/HW-FW-CONTRACT.md~supervisors' I2C1: SCL PB6 pin 92, SDA PB7 pin 93 on the kit bus",
                     "DOC:v2/docs/HW-FW-CONTRACT.md~### 6.5 The session's choice: three segments (SC-HF-02"]
ROW8_A = J.FABRIC + ["B:U514~74LVC1G157", "B:U515~74LVC1G157", "B:U517~BBM ? 1", "B:U518~BBM ? 1",
                     "B:U531~74LVC1G17", "B:U532~74LVC1G17", "B:U534~SN74LVC1G04", "B:U535~SN74LVC1G04",
                     "B:U531.4=PG2_S", "B:U532.4=PG3_S", "B:U517.4=BOE2_n", "B:U518.4=BOE3_n", "B:U517.6=BBM2", "B:U518.6=BBM3",
                     "DOC:v2/docs/ARCH-PCB-B-IOHA.md~**Drawn in board B's round 8 (27 September 2026):** each slot's power-good",
                     "DOC:v2/docs/feasibility/FAILOVER-FABRIC.md~## 9a. Round 8 (27 September 2026, MESHSAT-1357, board B author)"]
ROW9_A = J.CCARR + ["A@45bde541:U31~TPD2E2U06", "A@0d1e2ef6:!U31", "A@68bc9e8f:!U31"]
# where each passage the new rows name was written: present in the commit's CONOPS.md, absent from its parent's
WRITTEN = [("95e078a1", "the supervisors' I2C status path, absent as generated"),
           ("95e078a1", "and the supervisors' I2C status path (`ARCH-PCB-B-IOHA.md` section 6); they are preconditions"),
           ("68bc9e8f", "riding on the board A update already owed")]
PARENTS = [("458b2873", "1f614233")]
ROW2_A = J.HOTR1
ROW3_A = ["C@45bde541:R36.1=LED_RAIL", "C@45bde541:R36.2=TX_A", "C@45bde541:D3.2=TX_A", "C@45bde541:Q1.3=LED_RAIL",
          "C@a9f212c7:R36.1=LED_RAIL", "C@a9f212c7:Q1.3=LED_RAIL", "C:R36.1=LED_RAIL", "C:D3.2=TX_A"]
ROW4_A = ["B@45bde541:U25~AP63203", "B@45bde541:U25.1=+3V3_DEV", "B@45bde541:U25.2=+5V_DEV", "B@a9f212c7:U25.1=+3V3_DEV",
          "B@a9f212c7:U25.2=+5V_DEV", "A@45bde541:U7~LM5176", "A@a9f212c7:U7~LM5176"]
CITE_A = ["B:U540.1=ZBA_RXD_H", "B:R536?", "B:R537?", "B:U536.1=EMCON_HW", "B:U543.1=RB_IEN", "REG:S-122.status=OPEN"]
SEC01_WORDS = ["`U540`", "`R536`", "`R537`", "`U536`", "`RB_IEN`", "`U543`"]

LEAD_OLD = "place is judged against the netlists by `v2/docs/records/s122/verdicts.py`. Read on the committed netlists of"
LEAD_NEW = ("place is judged against the netlists by `v2/docs/records/s122/verdicts.py`. Where the value the baseline\n"
            "carries already differed from the netlists at the commit its passage names or where the passage was written,\n"
            "the row says so: that value was wrong when it was written, not overtaken by a later change (independent check\n"
            "`v2/docs/records/s122/checks/check-s122-2.md`, m3). Read on the committed netlists of")
ROW2_OLD = "| DC-02 | section 4's Heat stage and Hot stop rows; section 4c's HOT-R1 passages; section 4f's row of the pack's safety |"
ROW2_NEW = ("| DC-02 | section 4's Heat stage and Hot stop rows; section 4c's HOT-R1 passages; section 4f's row of the pack's "
            "safety; section 7a's HOT-R1 row |")
ROW3_OLD = "only `Q2` turns on, from `PANEL_PWM` (GPIO 8) |"
ROW3_NEW = ("only `Q2` turns on, from `PANEL_PWM` (GPIO 8); the baseline's text was already wrong at its reading: at `45bde541` "
            "and at `a9f212c7` board C's `R36` fed `D3` from `LED_RAIL`, `Q1`'s drain, as it does now |")
ROW4_OLD = "| DC-04 | section 4e, a device rail lost | `+5V_DEV` is made by board A's `U7` (LM5176) and `+3V3_DEV` by board B's `U25` (AP63203) from `+5V_DEV` |"
ROW4_NEW = ("| DC-04 | section 4e, a device rail lost | `+5V_DEV` is made by board A's `U7` (LM5176) and `+3V3_DEV` by board B's "
            "`U25` (AP63203) from `+5V_DEV`; the baseline's text was already wrong at its reading: at `45bde541` and at "
            "`a9f212c7` board B's `U25` made `+3V3_DEV` from `+5V_DEV`, as it does now |")
ROW6_END = "and `J_TAMP` at `gen_sch_e.py:796` | the generators at the commit read; `v2/docs/records/s122/verdicts.out` |\n"
NEWROWS = (
    "| DC-07 | section 4's Reduced row (its Guarantee cell) and section 4c's `SLOT_EN1` passage: the supervisors' I2C "
    "status path, called absent or owed as generated | the three supervisors are targets on the kit bus the panel "
    "controller masters: `U41`, `U51` and `U61` have pin 93 (PB7) on `SDA` and pin 92 (PB6) on `SCL`, which reach "
    "`J_PANEL`, since `458b2873` (both pins unconnected at its parent `1f614233`); the baseline's text was already wrong "
    "at its reading, at `45bde541`, at `95e078a1` where the passages were written, and at `c5430071`; what is owed is "
    "the TCA9517A segment of SC-HF-02, which board B does not carry | `ARCH-PCB-B-IOHA.md` section 6; `HW-FW-CONTRACT.md` "
    "FW-B08 and section 6.5 |\n"
    "| DC-08 | the same two passages: the break-before-make order (FAB-03, CON-003) and a bank detached from a host that "
    "has lost its power (FAB-02, CON-022), called owed or not done as generated | both drawn in board B's round 8, present "
    "at `95e078a1` where the passages were written and at `c5430071`, absent at `45bde541`: each slot's power-good "
    "`PG{s}` is its module's own 3.3 V through 1 k with 100 k to ground (`R191` and `R192` for slot 1), buffered by a "
    "74LVC1G17 (`U530` to `U532`) and inverted (`U533` to `U535`); per bank a 74LVC1G157 (`U513` to `U515`) selects the "
    "dark flag of the host the delayed select passes, and the bank's enable `BOE{b}_n` (`U516` to `U518`) is forced high "
    "while the break-before-make term `BBM{b}` is up and is that flag otherwise; the display switches' enables are the "
    "power-good of the slot each passes (`U519` for `U3`, `U520` for `U4`); S-42 stays OPEN, its title listing FAB-02 "
    "(b) and (c) and the break-before-make with the gate's assertion and its mutation, and CON-003 and CON-022 read "
    "INCONCLUSIVE, waiting on it | `ARCH-PCB-B-IOHA.md` section 5; `feasibility/FAILOVER-FABRIC.md` sections 9 and 9a; "
    "S-42, CON-003 and CON-022 in the registry |\n"
    "| DC-09 | section 7's D-17 row: board A's USB-C CC pins, the array riding on a board A update called owed | the array "
    "is drawn: board A's `U31` (TPD2E2U06) on `PD_CC1` and `PD_CC2`, the CC pins of `J_USBC_OUT`, since `458b2873`, "
    "and so at `45bde541` and at `c5430071`; the row was written at `68bc9e8f`, before `458b2873` drew it | this row |\n")
DEP_OLD = ("| CONOPS's circuit passages whose values differ from the committed netlists (EMCON, HOT-R1, the TX lamp, the device "
           "rails, generator line numbers) | the section \"Current values of CONOPS's circuit passages (stream s122, 29 "
           "September 2026)\" below | `CONOPS.md` sections 4, 4b, 4c, 4e and 4f |")
DEP_NEW = ("| CONOPS's circuit passages whose values differ from the committed netlists (EMCON, HOT-R1, the TX lamp, the device "
           "rails, generator line numbers, the supervisors' status path, the fabric's break-before-make and back-power "
           "gating, board A's CC array) | the section \"Current values of CONOPS's circuit passages (stream s122, 29 "
           "September 2026)\" below | `CONOPS.md` sections 4, 4b, 4c, 4e, 4f, 7 and 7a |")
BASE_OLD = ("`4483209659dc391c` with its status line written (`62f26a44`, unchanged through `31cd29b9`), the file handover H2 "
            "carries |")
BASE_NEW = ("`4483209659dc391c` with its status line written (`62f26a44`, unchanged through `31cd29b9`), the file handover H2 "
            "carries; `6cb7b241cb84d729` at `c5430071`, the owner's rulings of 28 September on the re-stamped text (D-19, "
            "D-20 and M1's owner instruction, `v2/docs/records/s122/checks/check-s122-2.md`), the file `CONOPS.md` "
            "carries since stream s122 restored it |")
PNL_OLD = "(`U540` to `U542`, `R536`, `R537`; `CONOPS.md` section 4b)."
PNL_NEW = "(`U540` to `U542`, `R536`, `R537`; `feasibility/EMCON.md` section 0a.1)."
SPC_OLD = "feasibility blocker FEA-002 (`CONOPS.md` section 4b; corrections 4, 19, 26, 28 and 30)"
SPC_NEW = "feasibility blocker FEA-002 (`feasibility/EMCON.md` section 0a.1; corrections 4, 19, 26, 28, 30 and 33)"
SPC_ANCHOR = "    by its own module (`J_FAN1..3` on board B), and the sensor controller drives the two mixer fans on board E.\n    Nothing is built.\n"
SPC_ADD = ("\n33. **The EMCON row's per-radio reference (line 24).** Session reading of stream s122, round 3 (29 September 2026,\n"
           "    MESHSAT-1357, open item S-122; its independent check, `v2/docs/records/s122/checks/check-s122-2.md`, m2). Line\n"
           "    24 cited `CONOPS.md` section 4b for the circuit radio by radio. Stream s122 restored `CONOPS.md` to its\n"
           "    baselined text at `c5430071`, where section 4b is a baseline value; the circuit as generated is kept in\n"
           "    `feasibility/EMCON.md` section 0a.1 (`handover/DEFINITION-STATUS.md`, row DC-01), which line 24 now cites.\n"
           "    Nothing is built.\n")
EDITS = [(DST, LEAD_OLD, LEAD_NEW, "the section's lead (m3)"), (DST, ROW2_OLD, ROW2_NEW, "DC-02 names section 7a"),
         (DST, ROW3_OLD, ROW3_NEW, "DC-03 (m3)"), (DST, ROW4_OLD, ROW4_NEW, "DC-04 (m3)"),
         (DST, ROW6_END, ROW6_END + NEWROWS, "DC-07 to DC-09 (B1, the absent sweep)"),
         (DST, DEP_OLD, DEP_NEW, "the dependency row"), (DST, BASE_OLD, BASE_NEW, "the baselines table (m4)"),
         (PNL, PNL_OLD, PNL_NEW, "PANEL.md line 156 (m1)"), (SPC, SPC_OLD, SPC_NEW, "V2-SPEC.md line 24 (m2)"),
         (SPC, SPC_ANCHOR, SPC_ANCHOR + SPC_ADD, "V2-SPEC.md correction 33")]


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    raise SystemExit(2)


def main():
    check = "--check" in sys.argv
    head = subprocess.run(["git", "-C", L.TOP, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
    nls = L.netlists()
    for b, s in NETS.items():
        if nls[b]["sha16"] != s: refuse("board %s's netlist is %s, not set 13's %s" % (b, nls[b]["sha16"], s))
    if L.sha16(CON) != CONOPS_BASELINE: refuse("CONOPS.md is %s, not c5430071's file %s" % (L.sha16(CON), CONOPS_BASELINE))
    c543 = subprocess.run(["git", "-C", L.TOP, "show", "c5430071:%s" % CON], capture_output=True, check=True).stdout
    if open(os.path.join(L.TOP, CON), "rb").read() != c543: refuse("CONOPS.md is not c5430071's file byte for byte")
    for rel, s in DOCS.items():
        if L.sha16(rel) != s: refuse("%s is %s, not the file this script corrects (%s): already applied, or changed" % (rel, L.sha16(rel), s))
    sec01 = " ".join(b[4] for b in L.md_blocks(EMC) if b[0] == "0a.1")
    for w in SEC01_WORDS:
        if w not in sec01: refuse("EMCON.md section 0a.1 does not name %s, which the new citations send the reader to" % w)
    n = 0
    for c, words in WRITTEN:
        at = subprocess.run(["git", "-C", L.TOP, "show", "%s:%s" % (c, CON)], capture_output=True, text=True, check=True).stdout
        before = subprocess.run(["git", "-C", L.TOP, "show", "%s^:%s" % (c, CON)], capture_output=True, text=True).stdout
        if words not in at or words in before: refuse("the passage '%s' was not written at %s" % (words, c))
        n += 1
    for c, parent in PARENTS:
        got = subprocess.run(["git", "-C", L.TOP, "rev-parse", "--short=8", c + "^"], capture_output=True, text=True).stdout.strip()
        if got != parent: refuse("%s's parent is %s, not %s" % (c, got, parent))
        n += 1
    for what, al in (("DC-07", ROW7_A), ("DC-08", ROW8_A), ("DC-09", ROW9_A), ("DC-02", ROW2_A), ("DC-03", ROW3_A),
                     ("DC-04", ROW4_A), ("the citations", CITE_A)):
        for a in al:
            ok, msg = V.run_assert(a, nls)
            if not ok: refuse("%s: assertion fails: %s" % (what, msg))
            n += 1
    texts = {rel: open(os.path.join(L.TOP, rel), encoding="utf-8").read() for rel in DOCS}
    for rel, old, new, why in EDITS:
        if any(d in new for d in L.DASHES): refuse("%s: a dash in the new text" % why)
        if texts[rel].count(old) != 1: refuse("%s: the old passage is found %d times" % (why, texts[rel].count(old)))
        texts[rel] = texts[rel].replace(old, new)
    for rel, old, new, why in EDITS:
        if texts[rel].count(new) != 1: refuse("%s: the new passage does not read back once" % why)
    rows = re.findall(r"(?m)^\| (DC-\d+) \|", texts[DST])
    if rows != ["DC-%02d" % i for i in range(1, 10)]: refuse("the status page's rows read %s" % rows)
    if check:
        print("%s: --check at %s: %d edits located, %d assertions hold (netlists of set 13 and at the commits named); "
              "nothing written" % (TAG, head, len(EDITS), n))
        return 0
    for rel, txt in texts.items():
        open(os.path.join(L.TOP, rel), "w", encoding="utf-8").write(txt)
        L.md_blocks(rel)
    if L.sha16(CON) != CONOPS_BASELINE: refuse("CONOPS.md changed")
    print("%s: at %s %d edits written, %d assertions held first; rows DC-01 to DC-09 on the status page; CONOPS.md "
          "unchanged (%s); %s" % (TAG, head, len(EDITS), n, CONOPS_BASELINE,
                                  ", ".join("%s to %s" % (os.path.basename(r), L.sha16(r)) for r in DOCS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
