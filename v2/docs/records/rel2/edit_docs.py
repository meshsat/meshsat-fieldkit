"""The documents' half of the second release attempt of layers 1 to 3 (27 September 2026, MESHSAT-1357, branch fnd/rel2
from main 953f5658). Every edit replaces asserted old text; the ids it writes (the session choices SC-HF-01 to SC-HF-06
entered as, the owner action, the engineering question, the test row) are the ones apply_registry.py took, read from the
JSON file it wrote (the only argument). The pages that other pages or records cite by line (CONOPS, POWER-THERMAL,
ARCHITECTURE, the product brief, OPERATING-ENVELOPE, GLOSSARY) keep their line counts; TEST-PLAN gains one row after
every line the registry cites; HW-FW-CONTRACT, ENGINEERING-QUESTIONS and the records README gain rows. Session wording
under the owner's standing rule of 26 September 2026. Run from the worktree root after apply_registry.py.

  layer 2 B2 / layer 3 R4  TEST-PLAN: the forced trigger (a new section 7 row), E3-H's stepped run and its NOT_VERIFIED
                           rule, E3-L unchanged; CONOPS's Hot stop row and HW-FW-CONTRACT's verification list name it
  layer 2 B3               the first Review A pass cited by its filed name wherever a page still named pass 2's file for
                           it (CONOPS lines 20 and 1138, TEST-PLAN line 3, OPERATING-ENVELOPE line 36; CONOPS lines 45 to
                           48 already did); records/README rows with sha256 for it and its brief
  layer 2 B4               C1 one way: POWER-THERMAL sections 1, 9.1, 9.2, 9.3 and 11, ARCHITECTURE 8.1, 8.2 and 8.3,
                           HW-FW-CONTRACT FW-C09, which also gains the hot stop's and HOT-R1's rows; CONOPS 4c and its
                           Reduced row say the three follow; (e) the engineering question for BAT-F19
  layer 3 R2               M1's duration governed by SC-21: ENGINEERING-QUESTIONS EQ-13, CONOPS M1 and 7a, the brief
  layer 3 R5               HW-FW-CONTRACT section 8 and GLOSSARY point at the registry's ids
  layer 1 m4, m5, m7, m8   the brief's closing rule, the FEA-002 row's "the case", the ruling of 21 September 2026 located,
                           the two key-encryption keys as SC-08's
"""
import json, re, sys

IDS = json.load(open(sys.argv[1]))
SC, M, EQ, PT = IDS['SC'], IDS['M'], IDS['EQ'], IDS['PT']
S1, S2, S3, S4, S5, S6 = (SC['SC-HF-%02d' % k] for k in range(1, 7))
KEEP = ('v2/docs/CONOPS.md', 'v2/docs/feasibility/POWER-THERMAL.md', 'v2/docs/ARCHITECTURE.md',
        'v2/docs/PRODUCT-BRIEF.md', 'v2/docs/OPERATING-ENVELOPE.md', 'v2/docs/handover/GLOSSARY.md')
files = {}


def rep(path, a, b, n=1):
    if path not in files: files[path] = open(path, encoding='utf-8').read()
    s = files[path]
    assert s.count(a) == n, (path, s.count(a), a[:100]); assert a != b
    files[path] = s.replace(a, b)


# ================================================================ CONOPS
C = 'v2/docs/CONOPS.md'
rep(C, "answer the seven blocking findings of Review A's first pass (`reviews/REVIEW-A-LAYER-2-2026-09-27.md`, B1 to B7) and",
    "answer the seven blocking findings of Review A's first pass (`reviews/REVIEW-A-LAYER-2-2026-09-27-pass1.md`, B1 to B7) and")
rep(C, "is answered in part at desk (`handover/LAYER-STATUS.md`, layer 2), and a later pass decides the baseline.",
    "is answered at desk in two steps (`handover/LAYER-STATUS.md`, layer 2: the wording and citations in `08f3665a`; then, "
    "in the second release attempt of the same day, B2's forced trigger of the hot stop, `TEST-PLAN.md` %s, and B4's one "
    "definition of C1 in the documents that follow section 4c), and a later pass decides the baseline." % PT)
rep(C, "were taken, or changed, later that day to answer the first pass of Review A (`reviews/REVIEW-A-LAYER-2-2026-09-27.md`);",
    "were taken, or changed, later that day to answer the first pass of Review A (`reviews/REVIEW-A-LAYER-2-2026-09-27-pass1.md`);")
rep(C, "`feasibility/POWER-THERMAL.md` (sections 1 and 9.3), `ARCHITECTURE.md` (its PS-RED row) and `HW-FW-CONTRACT.md` (FW-C09, C1 as a shed to one module) took the reduced mode as one module (slot 3 alone in the first two), which\n",
    "`feasibility/POWER-THERMAL.md` (sections 1 and 9.3), `ARCHITECTURE.md` (its PS-RED row) and `HW-FW-CONTRACT.md` (FW-C09, C1 as a shed to one module) first took the reduced mode as one module (slot 3 alone in the first two), which\n")
rep(C, "cannot change that; the hub port each device hangs on can, which is BANK-R1 below. Those three documents follow this section; their correction is a hand-off to their writers (`records/hc2/handoffs.md` sections 4 and 5; `handover/LAYER-STATUS.md`, layers 4 and 5).\n",
    "cannot change that; the hub port each device hangs on can, which is BANK-R1 below. Those three documents follow this section since 27 September 2026 (the second release attempt of layers 1 to 3, layer 2's finding B4; `records/hc2/handoffs.md` sections 4 and 5): C1 sheds to the reduced mode of slots 2 and 3 and, reached again there, to the heat stage's one module, in `feasibility/POWER-THERMAL.md` sections 1 and 9.3, `ARCHITECTURE.md` section 8 and `HW-FW-CONTRACT.md` FW-C09, and `HW-FW-CONTRACT.md` carries the hot stop and HOT-R1 as firmware rows (FW-C13, FW-C14, FW-E10).\n")
rep(C, "`feasibility/POWER-THERMAL.md` section 9.3, `ARCHITECTURE.md`'s PS-RED row and `HW-FW-CONTRACT.md` FW-C09, which still take the reduced mode as one module and follow this row (hand-offs, section 4c)",
    "`feasibility/POWER-THERMAL.md` section 9.3, `ARCHITECTURE.md` section 8 and `HW-FW-CONTRACT.md` FW-C09, which follow this row since 27 September 2026 (section 4c)")
rep(C, "`feasibility/POWER-THERMAL.md` still takes the reduced mode as slot 3 alone (its sections 1 and 9.3, C1's shed target) and is to follow this definition (a hand-off to its owner)",
    "`feasibility/POWER-THERMAL.md` follows this definition since 27 September 2026 (its sections 1 and 9.3: C1 sheds here first, and its PS-RED rows model one module, slot 3, the heat stage's case)")
rep(C, "the thresholds are PROVISIONAL (`TEST-PLAN.md` P14 and E3-H);",
    "the thresholds are PROVISIONAL (`TEST-PLAN.md` P14 and E3-H), and `TEST-PLAN.md` %s forces both steps at room temperature on the pack and on shore, so the stop is verified whatever a chamber reaches;" % PT)
rep(C, "D-06. The first changes M1's setting and the other two are the owner's rulings to reopen, so M1 stays as set and the\n",
    "D-06. The first changes M1's setting and the other two are the owner's rulings to reopen (with accepting the residual, the requirements registry's owner action %s, decided before boards A, E and P enter layout; `handover/ENGINEERING-QUESTIONS.md` EQ-13), so M1 stays as set and the\n" % M)
rep(C, "D-06 left it for the owner to set later and the standing rule forbids asking.",
    "D-06 left it for the owner to set later and the standing rule forbids asking, so this choice governs M1's duration, recorded as the session's (the registry's SC-21, which closes L-02).")

# ================================================================ TEST-PLAN
T = 'v2/docs/TEST-PLAN.md'
rep(T, "**Pass 2, later on 27 September 2026, answering the first pass of Review A (`reviews/REVIEW-A-LAYER-2-2026-09-27.md`):**",
    "**Pass 2, later on 27 September 2026, answering the first pass of Review A (`reviews/REVIEW-A-LAYER-2-2026-09-27-pass1.md`):**")
rep(T, "the transport and stored states have every input unplugged (m5).\n",
    "the transport and stored states have every input unplugged (m5). **The second release attempt of layers 1 to 3, later "
    "on 27 September 2026 (the release checks' layer 2 B2 and layer 3 R4):** %s (section 7) forces the hot stop at room "
    "temperature on the pack and on shore, so REQ-077 is verifiable whatever a chamber reaches; E3-H gains a stepped run "
    "beyond the envelope and the rule that a step that acted in no run reads NOT_VERIFIED; E3-L's pass line is "
    "unchanged.\n" % PT)
rep(T, "the pass lines of E3-A and E3-L are unchanged. Each exposure runs in the configuration of the",
    "the pass lines of E3-A and E3-L are unchanged. **Since the second release attempt of the same day** the hot stop's "
    "steps are also forced at room temperature (%s, section 7), because a chamber run may never drive the cells to its "
    "thresholds, and E3-H has a stepped run of its own beyond the envelope. Each exposure runs in the configuration of the" % PT)
rep(T, "| E3-H | the hot stop (`CONOPS.md` section 4c), read during E3-A's and E3-L's runs with no chamber time of its own: pack fitted,",
    "| E3-H | the hot stop (`CONOPS.md` section 4c), read during E3-A's and E3-L's runs and, beyond the envelope, in a stepped run of its own: pack fitted,")
rep(T, "| as E3-A and E3-L; at +40 C with the lid closed the level is held until the hot stop has acted or its 4 h have passed; once more with the sensor controller held in reset |",
    "| as E3-A and E3-L; at +40 C with the lid closed the level is held until the hot stop has acted or its 4 h have passed; once more with the sensor controller held in reset; then the stepped run, a protection test beyond the envelope and not an envelope claim: lid closed, the heat stage running, the chamber raised from +40 C by 2 K an hour to at most +55 C until H1 and then H2 have acted, first on shore (where idle cells sit at the inside air) and then on the pack |")
rep(T, "| acceptance of the hot stop inside the envelope; the ambient at which each step acts is characterisation, the measured bound that replaces `CONOPS.md` section 4c's |",
    "| acceptance of the hot stop inside the envelope; the ambient at which each step acts is characterisation, the measured bound that replaces `CONOPS.md` section 4c's; the stepped run is a protection test beyond the envelope |")
rep(T, "E3-L's own pass line is unchanged | acceptance; the step ambients characterisation | REQ-077 (the hot stop), REQ-052, REQ-024, FEA-004 |",
    "E3-L's own pass line is unchanged. **Whatever the chamber reaches, REQ-077 is decided with %s (section 7):** %s forces every step at room temperature on the pack and on shore; a thermal run, the stepped run included, in which the hottest cell never reached a threshold is recorded with its peak readings as NOT_REACHED and stands in for nothing; a step that acted in no run reads NOT_VERIFIED, never PASS | acceptance; the step ambients characterisation; the stepped run protection | REQ-077 (the hot stop, with %s), REQ-052, REQ-024, FEA-004 |" % (PT, PT, PT))
rep(T, "supply, a fire blanket, the cell taps on a datalogger, and a thermocouple on every cell.\n",
    "supply, a fire blanket, the cell taps on a datalogger, and a thermocouple on every cell. %s is not a layer of the pack: "
    "it forces the kit's hot stop, which reads the same four cell thermistors (`CONOPS.md` section 4c), on the assembled "
    "kit at room temperature (added 27 September 2026, the second release attempt of layers 1 to 3).\n" % PT)
P15 = ("| %s | the kit's hot stop, forced at room temperature (`CONOPS.md` section 4c: H1, H2 and HOT-R1), so that it is "
       "verified whatever a chamber reaches (E3-H) | the assembled kit with its pack, HOT-R1 drawn on boards A and E "
       "(without it the run records the generated path and REQ-077 reads FAIL at desk), at room temperature, first on the "
       "pack and then on shore. The gauge's hottest cell reading is driven by substituting one cell thermistor input: a "
       "make-before-break decade resistance in place of one 103AT-2 at board P's `J_TS` (TS1 to TS4 and VSS), through an "
       "adapter lead that passes the other three thermistors, so that no TS input is ever open (an open thermistor is a "
       "permanent failure of the gauge once its permanent fails are armed, TI SLUUAQ3A section 3.20); each setting is the "
       "one at which the gauge's `DAStatus2()` (`ManufacturerAccess()` 0x0072, SLUUAQ3A section 13.1.48) reads the target "
       "on that input, about 3.49, 3.33, 3.27 and 4.61 kohm for +55.0, +56.5, +57.0 and +46.5 C on the 103AT-2's B25/85 "
       "of 3435 K (Semitec, `v2/vendor/battery/semitec-103at-2-kempston.pdf`; INFERRED), because the gauge's own "
       "External 1 to 4 Temp Offset (SLUUAQ3A section 11.2.1.4, at most 12.7 K) cannot reach the thresholds from room "
       "temperature. Steps: +55.0 C (C1's cell trigger), +56.5 C (H1), +57.0 C (H2), never at or above the gauge's OTD "
       "of +57.5 C; after H1 the reading set to +50.0 C and then to +46.0 C; after H2 MAIN pressed with the reading at "
       "+50.0 C and again at +46.0 C. Then, with the sensor controller held in reset, board B's TMP117 driven past +55.0 "
       "C and +56.0 C by local heating of its package alone (a reference thermocouple beside it) and back below +45.0 C; "
       "and HOT-R1 held low, and left open, at the dock contact | on the pack and on shore alike: at +55.0 C C1 sheds to "
       "the reduced mode and then the heat stage; H1 acts on the second reading a second apart at or above +56.5 C: "
       "every running module shut down on `PI_SHDN_REQ` and `SLOT_EN1` to `SLOT_EN3` dropped within 60 s, the switched "
       "loads off, the charge held by the charger's `CHRG_INHIBIT` bit with the charger still carrying the kit on shore, "
       "the mixer fans at full speed, MASTER WARN flashing and the e-paper \"HOT STOP: COOLING\" with the reading, HOT-R1 "
       "at 5 Hz (1 Hz before); no module returns at +50.0 C, nor at +46.0 C before 30 minutes have passed since the stop, "
       "and the heat stage's module returns once both hold; H2 acts on the second reading at or above +57.0 C with H1 "
       "acting: the e-paper \"HOT SHUTDOWN: RESTART WITH MAIN WHEN COOL\" written, then `PI_KILL`, every converter on "
       "board A stopped, HOT-R1 held low, and the kit staying off on shore; MAIN at +50.0 C raises no slot, and at "
       "+46.0 C the kit starts; with the sensor controller in reset HOT-R1 reads high and the same two steps act on the "
       "TMP117 at +55.0 and +56.0 C, released at +45.0 C; HOT-R1 held low stops the kit (H2), and left open it reads as "
       "the sensor controller lost; after every run the gauge's `SafetyStatus()` and `PFStatus()` show no OTD and no "
       "permanent failure, and the second level (on `J_TS2`, untouched) and F2 have not acted. The time of every step "
       "and the readings are logged. **A step that did not act reads NOT_VERIFIED for REQ-077, never PASS** | acceptance "
       "of the hot stop's detection and action, whatever a chamber reaches | REQ-077 (the hot stop) |\n" % PT)
rep(T, "those thresholds come down by the excess before any other test is judged | protection | REQ-046; FEA-004 |\n",
    "those thresholds come down by the excess before any other test is judged | protection | REQ-046; FEA-004 |\n" + P15)

# ================================================================ POWER-THERMAL (C1 one way; line count kept)
PW = 'v2/docs/feasibility/POWER-THERMAL.md'
rep(PW, "  - **The reduced mode's one module is slot 3**, because the LoRa mesh the owner named for it (D-02b) is on slot 3's\n"
        "    SPI (`V2-SPEC.md` line 32).\n",
    "  - **The reduced mode is slots 2 and 3, and the heat stage past it is one module** (`CONOPS.md` section 4c; corrected 27 September 2026, the second release attempt of layers 1 to 3, layer 2's finding B4: the first version took the reduced mode as slot 3 alone, because the LoRa mesh the owner named for it, D-02b, is on slot 3's SPI, `V2-SPEC.md` line 32). C1 and C3 shed to the reduced mode first and, reached again there, to the heat stage (section 9.3).\n"
    "    The heat stage is slot 3 alone once board B's hub ports are exchanged (BANK-R1), which is this page's PS-RED with the APRS beacons (PS-SURV-R, 23.3 W), and slot 2 alone as board B is generated (PS-SURV, 21.7 W), because there slot 3 alone has no host for Iridium or the SOS path; the reduced mode is PS-RED2, 31.4 W (17.6 to 55.6); all three are in `v2/docs/records/hc2/pwr_red2.out`, on this page's model. Where this page says PS-RED, read the one-module stage.\n")
rep(PW, "- lid closed with fans for the reduced mode (D-02b) and for PS-RED-b in transport;\n",
    "- lid closed with fans for PS-RED, the one-module stage (section 1; the reduced mode of D-02b is PS-RED2), and for PS-RED-b in transport;\n")
rep(PW, "fans-off rows of 9.1 and above), and C1 sheds to slot 3. So on the design record's own conductance PS-TYP at +20 C\n",
    "fans-off rows of 9.1 and above), and C1 sheds (to the reduced mode, then the heat stage, section 9.3). So on the design record's own conductance PS-TYP at +20 C\n")
rep(PW, "- **In the reduced mode** (lid closed), charging holds off above +15 to +33 C on the bound, and +25 to +29 C on 32.53's\n"
        "  conductance. The envelope does not say so today.\n",
    "- **In the one-module stage** (PS-RED, lid closed), charging holds off above +15 to +33 C on the bound, and +25 to +29 C on 32.53's\n"
    "  conductance; in the reduced mode (PS-RED2, slots 2 and 3) above +5.3 to +29.2 C and +18.4 to +24.5 C, which `OPERATING-ENVELOPE.md` section 3 carries since 27 September 2026 (`v2/docs/records/hc2/pwr_red2.out`).\n")
rep(PW, "- **C1, module shedding (firmware, panel and bridge):** shed to one module (slot 3) when the inside air reaches +50 C\n"
        "  (the SGP41's recommended maximum) or any cell thermistor reaches +55 C. Restore 5 K below.\n",
    "- **C1, module shedding (firmware, panel and bridge):** shed to the reduced mode (slots 2 and 3) when the inside air reaches +50 C\n"
    "  (the SGP41's recommended maximum) or any cell thermistor reaches +55 C, and, if the triggers are reached again there, to the heat stage (one module: slot 3 after BANK-R1, slot 2 as board B is generated; `CONOPS.md` section 4c). Restore 5 K below.\n")
rep(PW, "  - The trigger: with both outlets already off, a 10 s average pack current above 9.0 A for 30 s sheds to one\n"
        "    module, as C1 does. It bounds",
    "  - The trigger: with both outlets already off, a 10 s average pack current above 9.0 A for 30 s sheds as C1\n"
    "    does (to the reduced mode, then the heat stage). It bounds")
rep(PW, "   - add \"in the reduced mode, lid closed, charging holds off above about +15 to +33 C\" (INFERRED; +25 to +29 C on\n",
    "   - add \"in the one-module stage (PS-RED), lid closed, charging holds off above about +15 to +33 C\" (INFERRED; +25 to +29 C on\n")

# ================================================================ ARCHITECTURE (line count kept)
A = 'v2/docs/ARCHITECTURE.md'
rep(A, "| PS-RED, slot 3 only, monitor off (the closed-lid reduced mode of D-02b) | lid closed, fans | 22.2 (12.7 to 45.9) | 22.4 (46.7) |\n",
    "| PS-RED2, slots 2 and 3, monitor off (the closed-lid reduced mode of D-02b, `CONOPS.md` section 4c; `records/hc2/pwr_red2.out`) | lid closed, fans | 31.4 (17.6 to 55.6) | 31.7 (HIGH not computed) |\n")
rep(A, "(`POWER-THERMAL.md` section 5). Sun on the open face (84.8 to 93.9 W absorbed, INFERRED, W4) and on a closed lid is outside the\n",
    "(`POWER-THERMAL.md` section 5). The heat stage past the reduced mode is one module (C1's second step, `CONOPS.md` section 4c): PS-SURV-R, slot 3 alone after BANK-R1, 23.3 W (12.8 to 46.9) with 23.4 W of heat inside, and PS-SURV, slot 2 alone as board B is generated, 21.7 W (12.4 to 42.0) with 21.9 W; `POWER-THERMAL.md`'s PS-RED (slot 3 alone in its own model, 22.2 W, 12.7 to 45.9, heat 22.4 W) is that one-module case, not the reduced mode (`records/hc2/pwr_red2.out`; corrected 27 September 2026, the second release attempt of layers 1 to 3). Sun on the open face (84.8 to 93.9 W absorbed, INFERRED, W4) and on a closed lid is outside the\n")
rep(A, "| PS-RED, lid closed, fans | 9.0 to 21.1 | 11.2 to 14.9 |\n",
    "| PS-RED2 (the reduced mode), lid closed, fans | 12.7 to 29.9 | 15.8 to 21.1 |\n")
rep(A, "  (e-paper degraded) and above +35 C (reduced mode, one module).\n",
    "  (e-paper degraded) and above +35 C (one module: the heat stage past the reduced mode, `CONOPS.md` section 4c).\n")

# ================================================================ HW-FW-CONTRACT
H = 'v2/docs/HW-FW-CONTRACT.md'
rep(H, "facts stay cited at `e3aedb25`; the rows added after review (FW-B19, SC-HF-06, HF-F06 to F08) are read at `84e52461`.\n",
    "facts stay cited at `e3aedb25`; the rows added after review (FW-B19, SC-HF-06, HF-F06 to F08) are read at `84e52461`. "
    "The rows of the second release attempt of layers 1 to 3 (27 September 2026: FW-C09's C1 target, FW-C13, FW-C14, "
    "FW-E10 and V-C13 for the hot stop and HOT-R1, section 8's registry ids) are read at `953f5658`.\n")
rep(H, "(`feasibility/ZEROIZE.md` section 5), A1 to A14 (`ARCH-PCB-B-IOHA.md` section 13), P10 to P14 (`TEST-PLAN.md` section 7",
    "(`feasibility/ZEROIZE.md` section 5), A1 to A14 (`ARCH-PCB-B-IOHA.md` section 13), P10 to %s (`TEST-PLAN.md` section 7; %s, the hot stop forced at room temperature, since 27 September 2026," % (PT, PT))
rep(H, "### 3.2 Panel controller, board C (FW-C01 to FW-C12)", "### 3.2 Panel controller, board C (FW-C01 to FW-C14)")
rep(H, "| Keep C1 (shed to one module at +50 C air or +55 C cell), C2",
    "| Keep C1 (at +50 C inside air or +55 C on any cell, shed to the reduced mode of slots 2 and 3; reached again there, to the heat stage's one module, slot 3 after BANK-R1 and slot 2 as board B is generated; restore 5 K below; `CONOPS.md` section 4c, corrected 27 September 2026), C2")
rep(H, "shed to the reduced mode with both outlets off | `POWER-THERMAL.md` 7.2, 9.3; `THERMAL-COORDINATION.md` section 7 (round 8) |",
    "shed to the reduced mode with both outlets off; past the heat stage, the hot stop is FW-C13 and FW-C14 | `POWER-THERMAL.md` 7.2, 9.3; `THERMAL-COORDINATION.md` section 7 (round 8); `CONOPS.md` section 4c (C1's target) |")
FWC = (
    "| FW-C13 | the hot stop's actor (read at `953f5658`; `CONOPS.md` section 4c): `SLOT_EN1..3` on GPIO13 to 15, `PI_SHDN_REQ` "
    "on GPIO18 and `PI_KILL` on GPIO19 (`C:U3`; `PI_KILL` through `J_AB1` pin 10 to `A:Q1` and the LTC2954's `KILL`, "
    "`gen_sch_a.py` lines 269 and 273); the switched loads' software enables on `A:U27` (0x21) and `A:U28` (0x24); the "
    "charger at 0x6B, ChargeOption0 bit 0 `CHRG_INHIBIT` (TI SLUSE66A 9.4.1 and 9.6.1) | H1, on HOT-R1 at 5 Hz (FW-C14) "
    "or, with the line held high, board B's TMP117 at +55.0 C in two readings in a row: ask every running module for a "
    "clean shutdown on `PI_SHDN_REQ` and drop `SLOT_EN1..3` once each has stopped or 60 s have passed; turn off the "
    "monitor, the pack heater, board D, PoE, the USB-C outlet, the wall port's VBUS and the PA and HF software holds "
    "through `A:U27` and `A:U28`; set `CHRG_INHIBIT`, never board A's `CHG_INHIBIT` line (it puts the charger in HIZ, "
    "whose converter stops, and moves the kit's load onto the pack, `gen_sch_a.py` line 782); keep `+3V3_DEV`, which "
    "feeds this controller; MASTER WARN flashing and the e-paper \"HOT STOP: COOLING\" with the hottest reading. Leave "
    "H1 only when the line is back at 1 Hz (or the TMP117 reads +45.0 C or less) and 30 minutes have passed since the "
    "stop, then raise the heat stage's one module. H2, on the line held low or, with it held high, the TMP117 at +56.0 C "
    "in two readings in a row with H1 acting: write the e-paper \"HOT SHUTDOWN: RESTART WITH MAIN WHEN COOL\", then "
    "drive `PI_KILL` high as FW-C03 does | REQ-077; SC-49; `CONOPS.md` section 4c | %s and E3-H (`TEST-PLAN.md`); V-C13 | "
    "FIRMWARE; its line OWED (HOT-R1, S-57) |\n"
    "| FW-C14 | HOT-R1 at the panel controller (read at `953f5658`): board A's `DOCK_SPARE` (`A:J_DOCK` pin 12, "
    "`gen_sch_a.py` line 226) lands on `A:U27` pin 18, whose change raises `EXP_INT` (`A:U27` pin 1 with `R110`, line "
    "1267), this controller's interrupt (`J_AB1` pin 13, `B:J_PANEL` pin 6, GPIO24); the line's 10 k pull-up to board A's "
    "3.3 V and board E's driver are not drawn (FW-E10) | Decode the line's four states from `A:U27`'s input at each "
    "`EXP_INT`: toggling at 1 Hz, the cells read and below H1; at 5 Hz, H1; held low, H2 (a line shorted to ground "
    "included); held high, the sensor controller lost (unpowered, in reset, hung or the contact open); a line is held "
    "when no edge comes for 3 s, the rule FW-C05 applies to a heartbeat. Read it at every start-up before any slot is "
    "raised, as `ZEROIZE_SW` is read (FW-C01): held low, write the H2 page and drive `PI_KILL` again; at 5 Hz, raise no "
    "slot until it is back at 1 Hz; held high, start under the TMP117's two steps. With the line held high apply FW-C13's "
    "steps to board B's TMP117 (`B:U10`, 0x49 on the kit bus) at +55.0 C and +56.0 C, released at +45.0 C, together with "
    "`THERMAL-COORDINATION.md` section 7's fallback (the reduced mode, the outlets off) | REQ-077; SC-50; `CONOPS.md` "
    "section 4c | %s; V-C13 | OWED (HOT-R1, S-57) |\n" % (PT, PT))
rep(H, "| `PANEL.md` section 11 | V-C12 | FIRMWARE (format not in the tree) |\n",
    "| `PANEL.md` section 11 | V-C12 | FIRMWARE (format not in the tree) |\n" + FWC)
rep(H, "### 3.5 Sensor controller, board E (FW-E01 to FW-E09)", "### 3.5 Sensor controller, board E (FW-E01 to FW-E10)")
FWE = (
    "| FW-E10 | HOT-R1 at the sensor controller (read at `953f5658`): `E:U10` GPIO19 (pin 30) is not connected as "
    "generated and board E's contact `BLK_SPARE` (`J_BLK` pin 12) reaches only `TP7` (`gen_sch_e.py` lines 562, 581 and "
    "693); the open-drain 2N7002 with its gate pull-down that drives the contact is not drawn | Read the four cell "
    "thermistors in the gauge's `DAStatus2()` (TS1 to TS4, `ManufacturerAccess()` 0x0072, TI SLUUAQ3A 13.1.48) once a "
    "second (FW-E01's poll) and drive the line: toggled at 1 Hz, each edge after a fresh reading of all four, while the "
    "hottest is below +56.5 C; at 5 Hz from the second reading in a row at or above +56.5 C until the hottest reads +46.5 "
    "C or less; held low (the 2N7002 on) from the second reading in a row at or above +57.0 C for as long as it stays "
    "there, then 5 Hz; release the line (held high by the pull-up: the lost-controller state) after 3 s without a good "
    "gauge reading, and never hold it low on a fault: the RP2040 watchdog's reset leaves GPIO19 an input, and the gate "
    "pull-down keeps the line high; run the mixer fans at full speed in H1 and H2 | REQ-077; SC-49, SC-50; `CONOPS.md` "
    "section 4c | %s; V-C13 | OWED (HOT-R1, S-57) |\n" % PT)
rep(H, "| Hardware watchdog on; for storage command the gauge's SHUTDOWN over SMBus | standby drain | V-E08 | FIRMWARE |\n",
    "| Hardware watchdog on; for storage command the gauge's SHUTDOWN over SMBus | standby drain | V-E08 | FIRMWARE |\n" + FWE)
rep(H, "| V-C12 | FW-C12 | the bridge protocol exercised end to end once MESHSAT-837's format is in the tree |\n",
    "| V-C12 | FW-C12 | the bridge protocol exercised end to end once MESHSAT-837's format is in the tree |\n"
    "| V-C13 | FW-C13, C14, E10 | `TEST-PLAN.md` %s at room temperature on the pack and on shore (every step of the hot stop "
    "forced by a substituted cell thermistor, the release rules, the four line states, the start-up read, the TMP117 "
    "stand-in) and E3-H; a step that did not act reads NOT_VERIFIED |\n" % PT)
rep(H, "### 6.5 The session's choice: three segments (SC-HF-02)\n",
    "### 6.5 The session's choice: three segments (SC-HF-02, the registry's %s)\n" % S2)
rep(H, "## 8. Session choices taken here (under the owner's standing rule of 26 September 2026)\n\n| ID | Question | Taken | Why | Reversed by |\n|---|---|---|---|---|\n",
    "## 8. Session choices taken here (under the owner's standing rule of 26 September 2026)\n\n"
    "**Entered in the registry (27 September 2026, the second release attempt of layers 1 to 3; layer 3's release check, "
    "R5).** The requirements registry (`v2/ecad/tools/pcb_requirements.yaml`, `session_choices`) is the one record of a "
    "session choice: these six are its %s to %s, each naming its ID here as `drafted_as`, and `rules_lib.py requirements` "
    "refuses any SC- id the registry or a page of `v2/docs/` or `v2/docs/handover/` cites that no registry entry defines. "
    "The IDs below are the drafts' names, kept so that the pages citing them still read.\n\n"
    "| ID | Registry | Question | Taken | Why | Reversed by |\n|---|---|---|---|---|---|\n" % (S1, S6))
for k, s in ((1, S1), (2, S2), (3, S3), (4, S4), (5, S5), (6, S6)):
    rep(H, "\n| SC-HF-%02d | " % k, "\n| SC-HF-%02d | %s | " % (k, s))
rep(H, "- The kit bus figures are desk arithmetic: 10 pF per pin where a maker publishes no maximum, 1.0 to 2.2 pF/cm of copper by\n"
       "  closed form. A field-solver reading and V-K01 on the built boards are owed.\n",
    "- The kit bus figures are desk arithmetic: 10 pF per pin where a maker publishes no maximum, 1.0 to 2.2 pF/cm of copper by\n"
    "  closed form. A field-solver reading and V-K01 on the built boards are owed.\n"
    "- The hot stop's rows (FW-C13, FW-C14, FW-E10) rest on HOT-R1, which neither board A's nor board E's generator draws\n"
    "  (S-57): until both do, the line is OWED and REQ-077 reads FAIL at desk.\n")
rep(H, "the handover pages carry SC-HF-06 where they named the touch lead |\n",
    "the handover pages carry SC-HF-06 where they named the touch lead |\n"
    "| 1 (second release attempt) | 27 September 2026 | After the release checks of layers 1 to 3 (`fnd/rel2`, at "
    "`953f5658`): FW-C09 takes C1 as `CONOPS.md` section 4c defines it (the reduced mode of slots 2 and 3, then the heat "
    "stage's one module); FW-C13, FW-C14 and FW-E10 carry the hot stop and HOT-R1 (layer 2's finding B4 and the layer 3 "
    "release check's note for layer 5), with V-C13 on `TEST-PLAN.md` %s; section 8's six choices are the registry's %s to "
    "%s (layer 3's R5), and section 0 names %s |\n" % (PT, S1, S6, PT))

# ================================================================ ENGINEERING-QUESTIONS
E = 'v2/docs/handover/ENGINEERING-QUESTIONS.md'
rep(E, "EQ-05 carries the hot stop's firing inside the envelope and EQ-20 its merge; their citations are at that branch's commits.",
    "EQ-05 carries the hot stop's firing inside the envelope and EQ-20 its merge; their citations are at that branch's commits. "
    "**The second release attempt of layers 1 to 3 (27 September 2026, branch `fnd/rel2`)** rewrites EQ-13 as what the "
    "session took under the standing rule (SC-21) and what only the owner may reverse or decide (%s), and adds %s "
    "(BAT-F19); their citations are at that branch's commits." % (M, EQ))
rep(E, "| EQ-13 | The M1 mission duration (L-02), reserved to the owner | C. external authorisation | 2, 3 | none once REQ-016 is split | nothing, once REQ-016 is split |",
    "| EQ-13 | M1's mission duration, the session's 72 hours (SC-21, which the owner may replace), and M1's failing energy balance | C. external authorisation | 2, 3, 4 | A, E, P (the pack pocket) | REQ-072 (FAIL at desk); the owner's routes (%s), decided before A, E and P enter layout |" % M)
rep(E, "| EQ-24 | The QMX lid tray does not fit the unit's connector layout (jacks on both end panels) | A. design work | 7 | none (a made part) | printing the tray (S-63) |\n",
    "| EQ-24 | The QMX lid tray does not fit the unit's connector layout (jacks on both end panels) | A. design work | 7 | none (a made part) | printing the tray (S-63) |\n"
    "| %s | The kit with its own pack cannot take the +55 C operating, +60 C humid or storage margins (BAT-F19, CFL-017) | C. external authorisation | 2, 3, 4 | P (the pack pocket) | nothing before layout; REQ-051's margins with the pack, and how the qualification report states them |\n" % EQ)
s = open(E, encoding='utf-8').read() if E not in files else files[E]
a = s.index("### EQ-13. The M1 mission duration (L-02)\n"); b = s.index("### EQ-14.")
old13 = s[a:b]
assert "Option (c) is not recommended because D-06 reserves the value to the owner" in old13
EQ13 = """### EQ-13. M1's mission duration (L-02, governed by SC-21) and M1's failing energy balance

Rewritten on 27 September 2026 (the second release attempt of layers 1 to 3; layer 3's release check, R2, and layer 2's,
B4 (c)): this is the statement of what the session took and what the owner may reverse or decide, not a question put to
him. The first version advised against the session setting the duration because D-06 reserves it; the registry had set
it (SC-21), and the two now say the same.

| | |
|---|---|
| **Exact issue** | Owner ruling D-06 left the mission duration of M1's pack-plus-solar balance for the owner to set later. Under his standing rule of 26 September 2026 the session took 72 hours on the PS-IDLE-SPEC basis (session choice SC-21), which governs M1's duration, is recorded as the session's, closes L-02, and is replaced by the owner's own setting whenever he gives one. On that duration and D-06's one 4S3P pack, requirement REQ-072 (M1's energy, prototype 1's core) reads FAIL at desk on two limits. The night binds: the aged pack's about 108 Wh bridges 2.5 h at PS-IDLE-SPEC's 42.8 W against nights of about 7 to 16 h at 52 N, whatever the panel. The day follows: 72 hours ask a panel of about 266 W on the reference day (SC-37), where the solar window of REQ-016 takes at most 100 W. On D-06's architecture REQ-016 as stated and REQ-072 cannot both hold (both records say so). |
| **Affected** | Decisions D-06 (the one pack), D-01 (its deferred second pack), SC-21, SC-36 (REQ-016's split) and SC-37 (the reference day); requirements REQ-016 and REQ-072; open items S-53 (the session's part) and %(M)s (the owner's part); boards A (the input front end), E (the LT8705A stage: D4, F2, J_SOLAR) and P, and the pack pocket; mission M1 of `v2/docs/CONOPS.md`. |
| **Evidence** | `v2/ecad/tools/pcb_requirements.yaml`: SC-21, L-02 (closed items), REQ-016, REQ-072 (its desk reading), S-53, %(M)s; `v2/docs/CONOPS.md` sections 3 (M1) and 4a (the aged runtimes); `v2/docs/feasibility/POWER-THERMAL.md` section 4 (PS-IDLE-SPEC, 42.8 W); `v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json` (4.0 kWh/m2 a day in September on the optimally inclined plane); `v2/ecad/tools/gen_sch_e.py` (the stage's 25 V window, its 17.6 V point, F2 and J_SOLAR at 10 A). |
| **Attempts and results** | REQ-016 split (SC-36), so the hardware window is a core requirement that does not depend on the duration; the duration set (SC-21) and the reference day chosen (SC-37); the balance computed: FAIL on both limits, carried as it stands, and the mission not shortened. The night's arithmetic (INFERRED, from CONOPS M1's figures): the shortest night at 52 N asks about 150 Wh in the lightest state (21.7 W for 7 h) and about 300 Wh at PS-IDLE-SPEC; the longest about 685 Wh at PS-IDLE-SPEC, about six times the aged pack. A second pack of D-06's size (about 216 Wh aged, the two together) carries the shortest night in the lightest state only. |
| **Viable options, and who may take each** | (a) Re-rate the input path (board E's stage and board A's front end) for the day's energy: the session's, judged at layer 4 (S-53); it carries the day, not the night. (b) An overnight input on the 9 to 36 V entry (a vehicle, a shore supply or any DC source inside the entry's window, an external battery included; no board change): it changes M1's setting from pack and solar, so CONOPS M1 states it and does not take it. (c) D-01's deferred second pack, which has no location found: the owner's (it reopens D-01's deferral). (d) A larger pack: the owner's (it reopens D-06; the case never changes). (e) Record that prototype 1 does not meet M1 on pack and solar alone: a residual only the owner can accept. (c) to (e) are the owner action %(M)s. A shorter mission is not an option: it would lower the requirement. |
| **Recommended next action** | The session's, under the owner's standing rule: judge (a) at layer 4 before boards A and E enter layout (S-53), because the day limit binds whatever the pack; keep (b) stated in CONOPS M1 as the way a night is carried today; report (c) to (e) to the owner at the next checkpoint with the arithmetic above, not asked, as %(M)s, decided before boards A, E and P enter layout. Until then REQ-072 reads FAIL and neither record is restated to fit. SC-21 stands until the owner gives his own duration, which replaces it. |
| **Expertise or equipment** | Power electronics for (a), at desk (the LT8705A stage and the front end); none for (b); the owner's judgement for (c) to (e). |
| **Cost and lead time** | (a) parts TBD (the stage's inductor and switches, the input fuse and the connector re-rated), no purchase before layout; (b) none; (c) and (d) cells and a pack build, and for (c) a location in the case, TBD; (e) none. |

""" % {'M': M}
s = s[:a] + EQ13 + s[b:]
EQB = """
### %(EQ)s. The kit with its own pack cannot take the +55 C, +60 C humid or storage margins (BAT-F19, CFL-017)

Added on 27 September 2026 (the second release attempt of layers 1 to 3; layer 2's release check, B4 (e)).

| | |
|---|---|
| **Exact issue** | With its own pack fitted the kit cannot meet owner ruling D-02a's +55 C operating margin, `TEST-PLAN.md` E5's +60 C humidity dwell, or the +71 C and -33 C storage margins (the stored kit keeps its pack, SC-19): the Samsung INR18650-35E cells are rated to +60 C in discharge and storage and their maker forbids use above it, the storage floor is -20 C, and at +55 C ambient the inside air is +61.6 to +74.2 C even in the heat stage with the lid open. `TEST-PLAN.md` runs those levels as stated deviations without the cells in the chamber, which measures the rest of the kit and does not close this finding. |
| **Affected** | Conflict record CFL-017 (open, ADVISORY, deferred with the qualification tests, SC-04) and requirement REQ-051; the deviations E3-S, E3-O, E4-S and E5; owner rulings D-02a (the margins) and D-06 (the pack); board P and the pack pocket only if the cells or the pocket's thermal arrangement change. No board or interface today. |
| **Evidence** | `v2/docs/review-packets/battery/THERMAL-COORDINATION.md` section 9a (the finding and its three routes); `v2/docs/OPERATING-ENVELOPE.md` section 8 (+61.6 to +74.2 C of inside air at +55 C ambient on the current bounds); `v2/docs/TEST-PLAN.md` sections 1 and 6 (the deviations and their arrangement); `v2/vendor/battery/samsung-35e-orbtronic.pdf` (Ver. 1.1, +60 C); `v2/ecad/tools/pcb_requirements.yaml` CFL-017. |
| **Attempts and results** | The battery stream wrote E3-O and E5 as deviations with the pack outside the chamber (SC-12), and the storage margins followed once the stored kit kept its pack (SC-19); both are reported as the rest of the kit's results, never as the kit's margin with its pack. A qualification margin is not an error (the owner's condition of 25 September 2026), so nothing is lowered and no test level is chosen so that the circuit passes. |
| **Viable options** | (a) The bounded enclosure heat experiment (`feasibility/POWER-THERMAL.md` section 10, run inside the empty-case heat-balance test of EQ-05): whether a pack pocket insulated from the electronics' heat keeps the cells under OTD at +55 C ambient; with 2.5 K between that ambient and OTD's 57.5 C it is marginal at best (INFERRED); the session's to take if the measurement closes it. (b) Cells rated above +60 C: the owner's (it reopens D-06 and spends money). (c) A reading of D-02a that its +55 C margin applies to the kit without its cells: the owner's reading of his own ruling. |
| **Recommended next action** | The session's, under the owner's standing rule: keep the finding open and the deviations as written; run (a) inside the empty-case heat-balance test before board P's layout entry and the pack pocket's freeze; report (b) and (c) to the owner with that result at the next checkpoint, not asked. If (a) does not close it, the finding stands as the qualification result it is: the kit with its pack does not take the +55 C margin. |
| **Expertise or equipment** | Thermal measurement (the empty-case test's chamber, heaters and thermocouples); battery qualification judgement for (b) (the D-09 battery reviewer, EQ-10). |
| **Cost and lead time** | (a) rides on the case and chamber time of EQ-05 and the mock-up's purchase (L-07, the owner's approval); (b) a cell qualification and a pack rebuild, TBD; (c) none. |
""" % {'EQ': EQ}
assert s.endswith("\n")
s = s + EQB
files[E] = s

# ================================================================ the product brief (line count kept)
B = 'v2/docs/PRODUCT-BRIEF.md'
rep(B, "reviewer who wrote none of the changed lines re-checks them at one pinned commit. History: written\n",
    "reviewer who wrote none of the changed lines re-checks them at one pinned commit. The second release attempt of the same day (branch `fnd/rel2`) compared the three fixes with the reviewer's exact fixes and completed B3 (this is not the re-check a fresh reviewer owes), states M1's duration as governed by the session's SC-21 with the owner's part as the requirements registry's %s, and takes the release check's minors m1, m4, m5, m7 and m8. History: written\n" % M)
rep(B, "  the pack rely on the vehicle or solar input (D-06). For accessories, a USB-C outlet that carries power only and\n",
    "  the pack rely on the vehicle or solar input (D-06), and on the pack and solar input alone the kit does not run through a night (REQ-072, \"What it is not, today\"). For accessories, a USB-C outlet that carries power only and\n")
rep(B, "  secure element holds, both needed to unlock a drive; holding the covered ZEROIZE toggle for 5 s, the only trigger,\n",
    "  secure element holds, both needed to unlock a drive (the two-key scheme is the session's, SC-08, under D-03's crypto-erase); holding the covered ZEROIZE toggle for 5 s, the only trigger,\n")
rep(B, "  the owner (ruling of 21 September 2026).\n",
    "  the owner (ruling of 21 September 2026, design appendix section 32.362, near its line 18606).\n")
rep(B, "publication, money and advertising the kit to its envelope stay with the owner (ruling of 21 September 2026).\n",
    "publication, money and advertising the kit to its envelope stay with the owner (ruling of 21 September 2026, design appendix section 32.362, near its line 18606).\n")
rep(B, "(SC-21, which the requirements registry records as closing L-02 and which the owner's own setting replaces; whether the standing rule reaches a value D-06 kept for the owner is recorded as open in `handover/LAYER-STATUS.md`, layer 3)",
    "(SC-21, which governs it under that rule, is recorded as the session's and closes L-02 in the requirements registry; the owner's own setting replaces it; `handover/ENGINEERING-QUESTIONS.md` EQ-13)")
rep(B, "and to the owner (a larger pack reopens D-06; the second pack is D-01's deferred item).",
    "and to the owner (a larger pack reopens D-06; the second pack is D-01's deferred item; accepting the residual is his alone: the requirements registry's owner action %s, decided before boards A, E and P enter layout)." % M)
rep(B, "and none of them changes a ruled radio, the case or a board-to-board interface.",
    "and none of them changes a ruled radio, the Peli case or a board-to-board interface (the hardware lamp's remedy adds a light-guide hole to the made face plate, S-44).")
rep(B, "- **Closing:** blocking findings are fixed and re-checked once by the same reviewer; after two unsuccessful passes on\n",
    "- **Closing:** blocking findings are fixed and re-checked once (SC-16's words); after two unsuccessful passes on\n")

# ================================================================ OPERATING-ENVELOPE, GLOSSARY
O = 'v2/docs/OPERATING-ENVELOPE.md'
rep(O, "September 2026 (pass 2, answering Review A's first pass, `reviews/REVIEW-A-LAYER-2-2026-09-27.md`):**",
    "September 2026 (pass 2, answering Review A's first pass, `reviews/REVIEW-A-LAYER-2-2026-09-27-pass1.md`):**")
G = 'v2/docs/handover/GLOSSARY.md'
rep(G, "| SC-nn | a session choice under the owner's standing rule (`pcb_requirements.yaml` `session_choices`); SC-L2-nn, SC-HF-nn are a closer's own drafts of such choices |",
    "| SC-nn | a session choice under the owner's standing rule (`pcb_requirements.yaml` `session_choices`); SC-L2-nn, SC-HF-nn are a closer's own drafts of such choices, and a draft a page still cites is entered in the registry under its own SC-nn with the draft's name as `drafted_as` (SC-HF-01 to SC-HF-06 are %s to %s since 27 September 2026); `rules_lib.py requirements` refuses an SC- id cited in the registry or a page of `v2/docs/` or `v2/docs/handover/` that no entry defines |" % (S1, S6))

# ================================================================ write, keeping line counts where others cite by line
for p, s in files.items():
    old = open(p, encoding='utf-8').read()
    if p in KEEP:
        assert old.count('\n') == s.count('\n'), (p, old.count('\n'), s.count('\n'))
    open(p, 'w', encoding='utf-8').write(s)
    print('edit_docs: %s (%+d lines)' % (p, s.count('\n') - old.count('\n')))
