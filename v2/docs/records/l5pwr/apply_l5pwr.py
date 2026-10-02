#!/usr/bin/env python3
"""apply_l5pwr.py: Layer 5's power pass written into its own contract files (MESHSAT-1357, set 27, 3 October 2026; the Layer 5
author owns the three targets, so this script was RUN ONCE on the tree by that author and is kept beside the record as the exact
statement of what changed; a second run refuses).

What it writes (L5-POWER-CONTRACTS.md gives every figure's Layer 4 source row, its mark and its invalidation trigger):
  pcb_interfaces.yaml   a header comment for the pass; IF-EXT-DC (LH-01, LH-02: levels, current, protection, sequencing, default
                        state, tbd, firmware, bench, the L4 defects); IF-AE-DOCK (LH-03, LH-04 and set 27: vin_raw's voltage and
                        in-service current, properties, pack_pins' charge and service rows, the pin1_vsys_dock field, sequencing,
                        default and cable-out states, firmware, bench); IF-PE-PACK (LH-04: charge, service, sequencing, default
                        state, firmware, bench); IF-EXT-USB (LH-05: levels, current, protection, sequencing, default state,
                        firmware, bench, tbd); IF-AB-POWER (LH-06: the PoE monitor on R227); IF-E-FANS and IF-A-HEAT (the fans'
                        start rule, the mat on measured headroom). The `pins` maps are NOT touched: they stay the committed
                        netlists' (what check_contracts.py reads), and L4-E11's apply_pcb_interfaces_dock.py keeps every anchor
                        it needs, which this script asserts after patching.
  HW-FW-CONTRACT.md     ORDER: after v2/docs/records/l4e5/apply_fw_a16.py (FW-A16 restated, FW-A18, V-A06 to V-A10), which this
                        script requires to have run. Then: the version paragraph and the State legend; LH-07's condition on
                        FW-A16; V-A08 as L4-E11 7a restates it (R-135); FW-C08 and FW-A14 restated (LH-10); FW-A09's U17 row on
                        R227 (LH-06); FW-A19 to FW-A23 (rules R-a to R-d and (B1)'s registers); FW-C15 (the margin hold, LH-11);
                        FW-E11 to FW-E13 (the fans' start, the SGP41's shutdown, DCIN_PGD the entry's fault flag); V-A11, V-C15,
                        V-E11 to V-E16 (LH-08, LH-09, R-176); section 4.1 (the drafts by the rows they move); the change record.
  PANEL.md              section 10: the charge-hold sentence as L4-E11 7a proposes it (LH-10).

Usage:  apply_l5pwr.py TARGET [--check | --write]     (default --check: nothing is written)
Each exact edit's old text must occur exactly once and its new text must not occur yet; a block edit's start and end markers must
each occur exactly once, in order; the result must differ and must re-parse (YAML loads; every table row added has its table's
cell count; the dock draft's anchors survive); no em or en dash anywhere in the result. Exit 0: checked (or written); 3: refused."""
import difflib
import os
import re
import sys

NAME = "apply_l5pwr"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


# ----------------------------------------------------------------------------------------------------- pcb_interfaces.yaml
Y_HEADER_OLD = "board_to_board:\n  schema: 1\n"
Y_HEADER_NEW = """\
# ======================================================================================================================
# LAYER 5'S POWER PASS (MESHSAT-1357, set 27, 3 October 2026; v2/docs/records/l5pwr/). Layer 4's power results (L4-E9's
# LAYER5-HANDOVER.md LH-01 to LH-11 and the set 27 rows) are written into IF-EXT-DC, IF-AE-DOCK, IF-PE-PACK, IF-EXT-USB,
# IF-AB-POWER, IF-E-FANS and IF-A-HEAT. MARKS in those texts: MAKER (a maker's printed row), INFERRED (arithmetic on printed or
# verified figures), MODELED (a record's model), PROVISIONAL (resting on an open condition, its invalidation trigger named
# beside it); DRAFTED (R-nn) marks a figure true of a release-guarded Layer 4 draft that no generator carries yet, so the drawn
# board is stated first where it differs. The `pins` maps stay the committed netlists' (what check_contracts.py reads); the
# drafted assignment of IF-AE-DOCK pin 1 (VSYS_DOCK) is its own field, pin1_vsys_dock, until L4-E11's
# apply_pcb_interfaces_dock.py applies together with the generator drafts. Every figure's Layer 4 source row, mark and trigger:
# v2/docs/records/l5pwr/L5-POWER-CONTRACTS.md, checked by l5pwr_contracts.py. This edit dates every interfaces.py reading
# (CONFIG_INPUTS), so a re-take of interfaces.py on every board follows it, as after H2.
board_to_board:
  schema: 1
"""

DC_LEVELS = '''\
      levels: "DC, as drawn: 9 to 36 V in service (a vehicle or a shore supply; board E's LM5069 U6 starts at 9 V (R21 38.3 k) and
        stops above 40 V (R23 6.65 k)); as drawn the LM5069 cannot start from a 9.00 V plug (L4-E11 3a, finding U4-F2). DC, the
        selected entry (DRAFTED, L4-E11 3c, R-123, apply_gen_sch_e_entry.py, not applied): REQ-015's 9 V taken at the kit's plug
        (L4-E11 3h, SESSION); per source at VBAT at the plug, the losses hot: 9 V 29.09 to 42.52 W, 12 V 32.22 to 47.72 W, 24 V
        69.97 to 90.81 W, 36 V 84.55 to 99.64 W (INFERRED, U3 0.9733); so at a 9.00 V plug the kit runs PS-IDLE-SPEC (42.8 W) with
        the pack supplementing and charges only while it draws under 29.09 W; with no usable pack the shedding sequence of L4-E11
        3g applies (P1 at most 20.51 W, the mat on measured headroom; FW-A21); REQ-015 at 9.00 V at the plug a CONDITIONAL
        CANDIDATE (PROVISIONAL: E11-06 measures P1, the front end's efficiency at least 0.88021 and the pin inside its band, E11-09
        draws the knee, E11-23 the warm-up time); no vehicle surge claim: the entry is recorded as not qualified and is not for
        24 V military vehicle buses (owner ruling D-16); the clamps' 64.5 V at their rated pulse the recorded residual A-N1.
        Solar: REQ-016's window, at most 25 V open circuit at -20 C; as drawn J_SOLAR's value text names a 36-cell 12 V class
        panel, about 22 V open circuit, 100 W; the panel is accepted downstream by PANEL-ACC (L4-E13: one identified SunPower
        SPR-E-Flex-100 measured, Vm20 + U_V at most 25.000 V at -20 C and 1000 W/m2, Voc25 20.315 to 22.156 V for its curve shape;
        no unit accepted yet: PROVISIONAL until PANEL-ACC's measurement, R-35); the panel held at 17.593 V nominal (16.970 to
        18.221 V with EA3 typical, 16.420 to 18.813 V conditioned; L4-E7R, MODELED); the regulation at RIMON_IN 31.6k, 2.5485 A
        nominal and 2.9318 A at its highest on the hold's corners (44.84 W and 53.42 W in); the backstop on SWEN trips at 3.0468
        to 3.7408 A at 25 V; the stage's input at the 25 V corner at most 93.5521 W, CONDITIONAL on G_CM and U18's VIN+ bias
        (break-evens 168.8 percent and 22.0 mA; PROVISIONAL until the makers' answers, R-101), the regulation's own corner
        73.3436 W (L4-E7R, accepted)"
'''
DC_CURRENT_DC = '''\
        dc: "as drawn: the LM5069 U6 limits at 4.85 to 6.15 A (R19 10 mOhm, VCL 48.5 to 61.5 mV, as read for HW-FW-CONTRACT.md
          FW-A16); behind the 10 A blade F1 at DC_IN since round 8 (E netlist 53a98a71). The selected entry (DRAFTED, R-123): in
          service at most 5.983 A from a 9.00 V plug (VIN_RAW 8.148 V), 6.4 percent under the breaker's lowest 6.364 A while the
          front end's efficiency there is at least 0.88021 (L4-E11 E11-06; INFERRED, PROVISIONAL on E11-06's measurement); the
          breaker 6.364 / 6.8 / 7.136 A after 0.247 / 0.37 / 0.49 ms, the short circuit 10.36 / 12.04 / 13.87 A on a filtered
          sense, retry 0.5 s (MAKER, SLUSEE5E); a stiff source's fault at most 900 A (the interconnect's specified floor; 569.8 A
          with the drawn cable; INFERRED); the start 0.382 to 1.219 A for at most 2.5 ms (MODELED)"
        solar: "in operation at most 3.987 A (PANEL-ACC A-3(a), INFERRED), the conservative bound over L4-E7R's regulation
          (RIMON_IN 31.6k, 2.5485 A nominal, at most 2.9337 A at 25 V) and its backstop, which turns the stage off at its trip (at
          most 3.7408 A at 25 V; MODELED); in a sustained input fault the panel's Isc at +70 C with U_I and SunPower's 1.25,
          8.1817 A (A-3(b): the maker's factor on the measured unit), under F2's 10 A and J_SOLAR's VH 10 A with the lead at AWG 16
          on the standard header (L4-E9 R-29); behind the 10 A blade F2 at PV_IN; the drawn value text's 'about 6 A for 100 W at
          18 V' is superseded by these"
        contacts: "as drawn MIL-DTL-38999 size 16 contacts (M39029/56-352); under D-06 the DC pair moves to size 12 contacts
          (insert 17-6, or 13-26 with the solar pair on rated contacts elsewhere; R-129, MISSING DRAFT), the insert's installed
          continuous rating of 20 A at the case's air to be filed (PROVISIONAL: R-129's filing); TBD until then: the fitted
          contacts' rating read into this record from the held Glenair and Amphenol sheets (v2/vendor/d38999/), effect: the
          installed 20 A of D-06 is unproven, and none at the drawn 6.15 A unless the sheets rate size 16 below it"
        vh: "JST-VH: the held catalogue (v2/vendor/connectors/jst-vh-catalogue.pdf, page 1) prints 10 A per contact with AWG 16
          on the standard header and 7 A for AWG 18 with the shrouded header only (MAKER); J_SOLAR's margin at A-3(b)'s 8.1817 A
          holds with the lead at AWG 16 (R-29: Layer 7 names the gauge); J_DCIN leaves VH for a 20 A class under D-06 (R-131,
          MISSING DRAFT): the selected interconnect carries at least 20 A continuous where installed, 35 A for 5 s, 60 A for 0.5 s
          and F1's clearing I2t at 900 A (L4-E11 6; PROVISIONAL on the makers' installed and short-time ratings, R-113, R-115,
          R-129 to R-132)"
'''
DC_SEQ = '''\
      sequencing: "hot-pluggable by design. As drawn: the LM5069 controls inrush and the tracker's LT8705A starts on its own UVLO.
        The selected entry (DRAFTED, R-123; L4-E9 4a): plug in: the entry's UVLO on at 7.87 / 8.14 / 8.44 V of DC_P (MAKER), then
        its slewed start, 0.382 to 1.219 A for at most 2.5 ms (MODELED), U3 in HIZ under the knee (certain below VIN_RAW 7.378 V,
        R-03, a specification), the H3 line from the first cycle, U34 releases the front end above 7.139 V (R-124, DRAFTED); plug
        out: the LM74700-Q1 U3 with Q1 blocks, the pack carries VBAT with no break (under (B1) through the battery FETs Q39 and
        Q40, DRAFTED R-157), U3 on board A resets IIN_HOST to 3.25 A once and firmware rewrites 4.70 A (FW-A16), U34's guard stops
        the front end at 6.754 to 7.139 V, the bank bleeds in 0.455 to 1.494 s (MODELED); panel at dawn: U5's own UVLO and soft
        start, SWEN off while TRK_LDO33 is under 2.662 V (MAKER), the hold 17.593 V, then the regulation; panel at dusk: the panel
        falls under the hold, U4 with Q2 blocks VIN_RAW from TRK_OUT, with no other source VIN_RAW falls into the knee's HIZ; both
        sources together are OR-connected onto VIN_RAW into ONE charger input limit (U3's IIN_HOST), the tracker's ceiling above
        24 V so the panel carries the bus first (at most 4.194 A at a 24 V vehicle, 65.9 percent of the breaker's lowest; L4-E9
        4b, MODELED). SHORE_INHIBIT high (panel GPIO20, FW-C08) holds the entry off (board E's Q8 pulls the entry's UVLO pin low:
        as drawn the LM5069's HS_UVLO, on the selected entry the TPS48110-Q1's EN/UVLO on the same net, DRAFTED R-123): asserted
        only for the operator's 'inputs off' and the water-on-floor isolation, never as a charge hold, with a warning first while
        the pack cannot discharge (L4-E11 7a; FW-C08 restated). DCIN_PGD (E U6 pin 8 to E U10 pin 15, R25 10 k to +3V3_E6) is the
        entry's fault flag on the selected entry (U6's FLT_I and FLT_T, open drain, low on an overcurrent, a short circuit or an
        overtemperature; FW-E13, DRAFTED), no longer a power-good line"
      default_state: "inputs run (SHORE_INHIBIT held low by A R118 and E R26, 100 k each): its reset, boot and cable-out state is
        LOW on both boards, so a dark or absent panel never holds the inputs off; the charger before any host write: as drawn
        ChargeCurrent 256 mA at POR (TI's E2E answer) and after the 175 s watchdog, under (B1) 0 A until firmware writes it
        (SLUSE65A, MAKER; DRAFTED R-157); the solar stage: SWEN off by default below 2.662 V on TRK_LDO33 (L4-E7R, DRAFTED R-19 to
        R-21); DCIN_PGD pulled high by E R25 10 k to +3V3_E6 (no fault) with the lead out or the entry unpowered"
      protection: "as drawn, board E: the 10 A blades F1 and F2, SMCJ40CA D10 at the entry and SMCJ40A D1 after the ideal diode Q1,
        the LM5069's OV at 40 V (faf8c981); the solar input through the LT8705A tracker (IF-AE-DOCK carries the ORed bus up to A).
        The selected entry (DRAFTED, L4-E11 3c, R-123; L4-E9 part A, R-17, R-18): a TPS48110-Q1 breaker (U6) with a CSD19536KTT
        (Q7), R19 4.5 mOhm and L2 SRF1260-1R0Y: UVLO on at 7.87 / 8.14 / 8.44 V and off at 7.46 / 7.66 / 7.95 V of DC_P; OV off
        above 39.6 / 40.36 / 41.22 V, clear of CS101's 38.83 V at 36 V and under D10's 44.4 V; overcurrent 6.364 / 6.8 / 7.136 A
        after 0.247 / 0.37 / 0.49 ms and a short circuit at 10.36 / 12.04 / 13.87 A on a filtered sense, retry 0.5 s (MAKER rows,
        SLUSEE5E); every start inside Q7's derated chart (MODELED); a hard short in service bounded only with the loop's inductance
        at least 2.08 uH (PROVISIONAL: OPEN, R-134); Q1 the CSD19532Q5B (100 V: a reversed 36 V input stands off up to 66.15 V
        across it while the tracker back-feeds DC_P through Q7's body diode; INFERRED; DRAFTED R-17); E-F1's 1 uF input capacitor
        at U3's ANODE; F1 the Littelfuse 0997010.WXN (MINI, 58 V DC, 1000 A at 58 V DC; MAKER) in a holder rated at least 20 A
        (R-132, MISSING DRAFT), against 43.18 V and at most 900 A (the interconnect's specified floor); the interconnect at least
        20 A continuous where installed, 35 A for 5 s, 60 A for 0.5 s and F1's clearing I2t at 900 A (D-06 resolved in design,
        L4-E11 6; PROVISIONAL on R-113, R-115, R-129 to R-132). Solar (L4-E7R and L4-E7's remedies; DRAFTED R-12, R-19 to R-21,
        R-98, R-173, not applied): the 50 V bulk on PV_P ahead of the sense bank; D4 the SMCJ30A (from the SMCJ28A) and C71 to C74
        on TRK_VS; the INB filter, five 100 nF C0G across R66 8.45k (3.960 to 4.496 ms); SWEN off by default below 2.662 V on
        TRK_LDO33; a response inside 1.087 ms after the filter's 0.4205 J held charge, for 10 J in any 0.1 s (the 0.1 s
        interpretation is layer 8's); under CS101 the filtered ripple at most 0.0585 A against a 0.1130 A margin, CONDITIONAL on
        the loop's typical rows (break-even 2.51 times), the bulk's temperature and the bank's pulse capability, M2 verifies it
        (R-122; PROVISIONAL); the solar guard: U21 TPS48110-Q1 with Q12 CSD19532Q5B as an over-voltage cut-off rising at 28.55 to
        31.06 V and falling at 27.07 V or more (aged), Q13 CSD19532Q5B in the return against a reversed panel (CONDITIONAL on its
        leakage above +25 C, printed at 25 C only), D11 SMCJ40CA at the port, the port bank C131, C132, C135, C136 (Samsung
        CL32B225KCJSNNE), C133 and C134 (CL32B106KBJNNNE), R97 28.0k, C126 330 pF; a stiff 36 V source stepping on with the
        guard already on: every rating with its margin only from a source loop of at least 3.30 uH (U5 0.2396 V of +-0.240 V, a
        DESIGN TARGET), NOT under it (at 1.00 uH U5 0.5287 V): PROVISIONAL, NOT CLOSED (B6-ENG-1: R-180, R-186 or R-187; L4-E7's
        round 3 on B6 is running, and its result re-reads this sentence); the band between 25 V and the cut-off a residual for
        layer 8 (R-175)"
'''
DC_TBD = '''\
      tbd: ["the receptacle MPN (CASE-MARGINS.md section 6), and under D-06 the DC pair on size 12 contacts (insert 17-6, or 13-26;
            R-129, MISSING DRAFT); effect: plate cut-out and seal not final, and the pins map A to D above is the drawn one",
            "the interconnect's makers' installed and short-time ratings and F1's total clearing I2t at 900 A and 58 V DC (L4-E9
            R-113, R-115, R-129 to R-132); the loop read four-wire at 58.51 to 64.21 mOhm on every assembly (R-130); effect: D-06's
            resolution rests on them",
            "A-3(c), a COMPONENT_LIMITATION: in a double contingency (an input fault present and F2 holding) J_SOLAR and PV_IN carry
            13.82 A at the design level 2111.4 W/m2, over JST VH's printed 10 A with no short-time overload; effect: their rating or
            a bench row is owed before the panel is accepted (L4-E9 R-148)",
            "the size 16 contact rating as drawn, read into this record; effect: none at 6.15 A unless the sheets rate size 16 below
            it; superseded by R-129's size 12 contacts once drafted",
            "J_SOLAR pin 2 becomes PV_RTN through Q13 under the solar guard (R-173, drafted, not applied); effect: the pins map and
            the end's part text read the drawn board until then"]
      firmware: "HW-FW-CONTRACT.md FW-C08 (SHORE_INHIBIT: boot low, asserted only for 'inputs off' and the water-on-floor isolation,
        a warning first in S2 and S4), FW-E03 (its read-back), FW-E13 (DCIN_PGD as the entry's fault flag, DRAFTED), FW-A16 (IIN_HOST
        4.70 A constant on a board with the H3 network, the 9 V figure no longer a VIN_RAW rule), FW-A18 (OWED: the H3 line on
        ILIM_HIZ), FW-A21 (R-c: the shedding sequence at a 9.00 V plug with no usable pack, the mat on measured headroom, the
        VSYS_UVP recovery); the solar backstop acts on SWEN in hardware and reports to no controller (L4-E7R: no flag line)"
      bench: "HW-FW-CONTRACT.md V-E14 (REQ-015: the reversed supply, the OV trip, the start from 9.00 V through the interconnect at
        its resistance ceiling; LH-08), V-E15 (REQ-016: the backstop's SWEN fall inside 3.0468 to 3.7408 A at 25 V; LH-09), V-E16
        (the solar guard's six rows, R-176; row 3 a pass only for a source loop at or over 3.30 uH until B6-ENG-1 is decided:
        PROVISIONAL), V-A08 (the source steps: the breaker never trips, VIN_RAW never under 7.24 V; R-135), R-85 (the source-only
        start at 9.00 V), M2 CS101 on the solar lead (R-122)"
      l4_defects: "L4-E9's defects at this interface (L4-POWER-ARCHITECTURE.md 8a): D-06 resolved in design (the interconnect, L4-E11
        6, CONDITIONAL on the makers' ratings); D-07 and D-09 superseded (the LM5069 replaced, R-123); D-10 (a stiff 36 V source on
        the solar port) and D-11 (a reversed panel) addressed in drafts by the guard (R-173), D-10's guard-on case NOT CLOSED
        (B6-ENG-1), D-11 CONDITIONAL on Q13's hot leakage; D-12 (CS116 and CS115 on the panel lead) resolved in the drafted entry,
        CS115 CONDITIONAL with the block on (R-174); the band between 25 V and the cut-off the residual R-175"
'''
DC_TBD_OLD = '''\
      tbd: ["the receptacle MPN (CASE-MARGINS.md section 6); effect: plate cut-out and seal not final",
            "the JST-VH rating document; effect: the inside lead's contact margin unproven",
            "the size 16 contact rating read into this record; effect: none at 6.15 A unless it is below it"]
'''

DOCK_VWORK_OLD = '      vin_raw: {voltage: "9 to 36 V (v_work 36 V)",\n'
DOCK_VWORK_NEW = '''\
      vin_raw: {voltage: "as declared 9 to 36 V (v_work 36 V). Layer 4 (L4-E9 1d IF-06; LH-03): solar 7.378 V (the corrected knee's
                  certain HIZ, L4-E9 R-03, a specification) to 30.15 V (the tracker's raised ceiling, R10 232 k; L4-E5, DRAFTED);
                  vehicle 9 to 36 V at the plug (VIN_RAW 8.148 V at 5.983 A from a 9.00 V plug; INFERRED); at most 41.22 V (the
                  selected entry's OV maximum, MAKER; 43.18 V the basis the checks keep); the clamps' 64.5 V at their rated pulse
                  is the recorded residual A-N1 (no surge level ruled, D-16)",
                in_service: "at most 5.983 A (a 9.00 V plug) or 4.22 A (the tracker at the window), INFERRED; the front end's fault
                  current at most 11.65 A at R11 8 mOhm and R12 12 mOhm (13.315 A at 7 mOhm), inside the declared 14.10 A and the
                  four 9 A pins (3.88 A each with one open) (L4-E9 1d IF-06 and IF-07; MODELED; R11 and R12 DRAFTED R-04, R-01)",
                properties: ["the tracker back-feeds board E's DC_P through Q7's body diode whenever it holds VIN_RAW; the vehicle's
                  ideal diode U3 with Q1 blocks it at DC_F (L4-E9 1d IF-04; INFERRED; Q1 the CSD19532Q5B, DRAFTED R-17)",
                  "U34's restart guard falls at 6.754 to 7.139 V (R14 76.8k, L4-E9 R-124, DRAFTED), at least 0.1 V under the knee's
                  certain HIZ 7.378 V; as drawn it falls at up to 8.309 V, over the 9.00 V plug's 8.148 V (IF-07)"],
'''
DOCK_PRE_OLD = '                  precharge: "J_PRE1 mates first, through R1 10R 2 W to CELL+ (gen_sch_a.py:210)"}\n'
DOCK_PRE_NEW = '''\
                  precharge: "J_PRE1 mates first, through R1 10R 2 W to CELL+ (gen_sch_a.py:210)",
                  charge: "at most 3.0 A (FW-A02; REQ-075 3.06 A), under the gauge's OCC 5 A (L4-E9 1d IF-10; LH-04)",
                  service: "10.0 A continuous and 18.0 A peak kept; PS-ALLTX's 18 A at an 11.48 V stack and OCD1's 20 A below
                    10.42 V (pwr_budget.out D-11 line; MODELED); the chain's short-time rating PWR-F12 open (FEA-004): PROVISIONAL
                    until PWR-F12 closes"}
'''
DOCK_HOTR1_END = '        line on both (SCH-004: A listens, safe high by R216; E is its source). Firmware: v2/docs/HW-FW-CONTRACT.md\n        FW-C13, FW-C14 and FW-E10; the path read by v2/docs/records/w4ae/hot_r1_trace.py"\n'
DOCK_PIN1_NEW = DOCK_HOTR1_END + '''\
      pin1_vsys_dock: "SET 27, the selected architecture A1 under D-06 (L4-E11 15a, 16e, 17a; L4-E9 1d IF-06; DRAFTED,
        release-guarded, not applied: R-157 board A, R-177 board E, R-181 the eFuse, R-178 this contract's pins map by L4-E11's
        apply_pcb_interfaces_dock.py, applied together): pin 1 leaves GND for VSYS_DOCK, board A's VSYS (the net VBAT) behind the
        eFuse U42 TI TPS16630PWPR, to board E's VSYS_E, the feed of board E's auxiliary domain (U12, C31, the mixer fans, D7 and D8),
        1.0 A declared (U12 0.8 A, the fans 0.1 A each), one Preci-Dip 813 contact at 28.6 percent of its 3.5 A; the pins map above
        stays the committed netlists' (pin 1 GND) until the drafts apply, which is what check_contracts.py reads. LEVELS: VSYS
        9.688 to 17.375 V (L4-E11 15d; MAKER rows of SLUSE65A, INFERRED at the corners); at the supplement floor 9.688 V with 1.0 A
        the drop is 0.1486 V (U42 53 mOhm, the 813 path 43.4 mOhm, the return's shift), so VSYS_E at least 9.539 V, 11.905 V at
        VSYS_MIN's start (L4-E11 16e; INFERRED). CURRENT AND PROTECTION: U42's I(OL) 1.4713 to 1.8018 A at R(ILIM) 11.0 kOhm 0.1
        percent (between TI's printed 9 and 30 kOhm rows, each over TJ -40 to 125 C: INFERRED from MAKER rows, SLVSET9G), a
        regulated steady setting and not an instantaneous ceiling; in a sustained overload the contact at most 1.802 A, 51.5
        percent of 3.5 A; current limiting at most 202 ms, then off 500 to 800 ms and a retry (MODE to GND); a short applied while
        on at most 566 A for at most 4.5 us (a ceiling, no inductance credited; INFERRED), IN at most 41.1 V with U42 within 20 nH
        of C236 (a layout requirement), OUT's undershoot against -0.3 V open (Q-TI-18); C238 1 uF at IN, C239 0.1 uF at OUT, D23
        B540C-13-F from GND to OUT. DEFAULT AND CABLE-OUT: U42 draws at most 1.7 mA from VSYS; with the stack lifted or pin 1 open
        board E's controller is unpowered, which board A reads on HOT-R1 as the detector lost (a detected state); under (B1) the
        held pack feeds no kit load through this pin (the source carries VSYS_E; the held pack's quantified drain 0.1408 mA, the
        bench at most 1 mA, E11-31). THE FANS' START RULE (E11-39, FW-E11): against U42's least limit 1.471 A with U12's 0.8 A,
        both fans together at most 0.3356 A each, one at a time at most 0.5713 A (the other running at 0.1 A), VSYS_E at the least
        limit at least 9.494 V at the supplement floor, so the fans must start at or under it; firmware starts them one at a time
        with a PWM ramp, never both within 1 s and never while U12 starts (R-188). STATE: sustained-overload remedy drafted, fault
        qualification open (L4-F03, E11-38, R-184): PROVISIONAL, invalidated by a limit read outside 1.471 to 1.802 A, a fan or U12
        current over 1.471 A (E11-35, R-179: no fan is named), or the hard short's qualification failing (E11-38); the ground
        return keeps seven 813 contacts (2.238 A each at the 32.1 A coincidence, 2.406 A with one open, 79.3 C at the 51 C air;
        L4-E11 15a, INFERRED on w3de's model)"
'''
DOCK_END_A_OLD = "        - {board: a, refs: [J_DOCK, J_CP1-4, J_CN1-4, J_PRE1, J_VR1-4, J_VN1-4], src:"
DOCK_END_A_NEW = ("        - {board: a, refs: [J_DOCK, J_CP1-4, J_CN1-4, J_PRE1, J_VR1-4, J_VN1-4], part: \"J_DOCK twelve Preci-Dip 813 spring pins "
                  "(3.5 A operating maximum each); J_CP1-4, J_CN1-4, J_VR1-4, J_VN1-4 and J_PRE1 Mill-Max 0858-class power spring pins (9 A "
                  "each)\", src:")
DOCK_END_E_OLD = "        - {board: e, refs: [J_BLK, P_CP, P_CN, P_VR, P_VN], src:"
DOCK_END_E_NEW = ("        - {board: e, refs: [J_BLK, P_CP, P_CN, P_VR, P_VN], part: \"J_BLK 2x6 lands for the block's twelve 24 AWG leads; "
                  "P_CP, P_CN, P_VR and P_VN 12 AWG lands\", src:")
DOCK_NJ_OLD = '      not_judged: ["clamp orientation and value against the board (A03, A04)"'
DOCK_NJ_NEW = '''\
      levels: "VIN_RAW and the pack pins as vin_raw and pack_pins state; the signal contacts at board A's +3V3 logic (SHORE_INHIBIT,
        HOT-R1) and the USB_E6 pair at USB full speed; pin 1 VSYS_DOCK 9.688 to 17.375 V under (B1) (pin1_vsys_dock, DRAFTED)"
      current: "VIN_RAW 14.10 A declared on four 9 A pins (vin_raw: in service at most 5.983 A, the fault at most 11.65 A); the pack
        pins 10.0 A continuous and 18.0 A peak on four 9 A pins, the charge at most 3.0 A (pack_pins); pin 1 at most 1.802 A behind
        U42 under (B1) (pin1_vsys_dock); the 813 signal contacts at logic currents; the ground return shared as ground_return states"
      harness: "none: a blind-mate dock; board A's spring pins land on the E5 block's plated targets, and the block's lands carry 24
        AWG (J_BLK) and 12 AWG (P_CP, P_CN, P_VR, P_VN) leads to board E (ASSEMBLY.md section 4)"
      mating: "blind-mate on the E5 block's targets at the stack's seating (ASSEMBLY.md section 1); the D-14 procedure for every
        stack lift (hot_plug); the alignment is judged by nothing (IF-AE-RF's gap note)"
      judged_by: "check_contracts.py sections 4 (the 2x6 contact map, SHORE_INHIBIT's reach), 5 and 5a (the pack and VIN_RAW power
        pins and lands); block_contract.py (needs pcbnew) for E5; the alias VSYS_DOCK and VSYS_E arrives with L4-E11's draft"
      tbd: ["the fans' part and so their start current behind U42 (E11-35, R-179); effect: pin1_vsys_dock's fans' start rule is a
            bound, not a part's figure",
            "the 813 contact's pulse capability and its resistance after E11-38's hard-short cases; effect: the dock's VSYS branch's
            fault qualification (L4-F03) stays open"]
      sequencing: "VIN_RAW over the dock: the entry's start (IF-EXT-DC sequencing) and U34's release above 7.139 V on board A; the
        pack pins: J_PRE1 mates first through R1 10 R; under (B1) the pack's connection pulse is 242.9 A peak, time constant 33.8
        us, into VBAT's capacitors through the battery FETs' body diodes, the whole pulse in one FET (TJ 123.3 C from the +70 C
        air on the stated VF bound; MODELED, PROVISIONAL on E11-30's pulse qualification); pin 1 (VSYS_DOCK, DRAFTED): U42's dVdT
        ramp 3.99 to 8.75 ms at C237 22 nF, 24.3 mA into C31's 10 uF, then board E's U12 up, the fans after it one at a time
        (FW-E11); pin 12 HOT-R1 as hot_r1 above; SHORE_INHIBIT on pin 8 reaches E's Q8 and U10 (check_contracts.py section 4)"
      default_state: "VIN_RAW absent until a source is present and the entry starts; pins 1 to 7 and 11 GND as committed; pin 8
        SHORE_INHIBIT LOW (A R118, E R26: the inputs run); pins 9 and 10 the USB pair idle; pin 12 HOT-R1 held high by A R216 until
        E's controller drives it (the lost-detector state); the CELL+ pins live whenever a pack is fitted (the pack's FETs on with
        the battery alone; under (B1) SLUSE65A p.27)"
      cable_out_states: {SHORE_INHIBIT: "LOW on A (R118): the inputs run", HOT_R1: "HIGH on A (R216): the detector lost, FW-C14's
          fallback on board B's TMP117", VSYS_DOCK: "DRAFTED: open at E; board E's auxiliary domain unpowered, its controller dark,
          read as HOT-R1 lost; U42 unloaded", VIN_RAW: "board A unfed; the pack carries VBAT", CELL_PINS: "the pack unreachable
          from A: the kit dark unless a source feeds VIN_RAW"}
      firmware: "FW-C14 (HOT-R1's four states read on A), FW-E10 (its driver), FW-C08 (SHORE_INHIBIT), FW-E11 (the fans' start
        stagger under U42's limit, DRAFTED), FW-A19 to FW-A23 (the charge holds, ChargeCurrent and (B1)'s registers on the charger
        whose VSYS this pin carries)"
      bench: "R-184 (E11-38: the dock's VSYS branch through the whole fault envelope), R-179 (E11-35: the fans' supply range and
        start), R-161 (E11-31: the three modes, the held pack current at most 1 mA), the dock's contact resistances and an 813
        ground contact's temperature (ground_return above); V-E11"
''' + DOCK_NJ_OLD

PACK_CHAIN_OLD = '                :288); the chain\'s short-time rating at 18 A and F2 near +60 C are PWR-F12, open"}\n'
PACK_CHAIN_NEW = '''\
                :288); the chain's short-time rating at 18 A and F2 near +60 C are PWR-F12, open",
              charge: "at most 3.0 A (FW-A02; REQ-075 3.06 A), under the gauge's OCC 5 A (L4-E9 1d IF-10; LH-04); under (B1)
                R-b' precharges a pack under VSYS_MIN at ChargeCurrent 0x0080, at most 0.33616 A with R17's 1 percent, through one
                FET of the pair in LDO mode, no charge under 5.7 V on SRN (L4-E11 15c; MAKER rows, DRAFTED R-157)",
              service: "10.0 A typical and 18.0 A peak kept; PS-ALLTX's 18 A at an 11.48 V stack and OCD1's 20 A below 10.42 V
                (pwr_budget.out D-11 line; MODELED); the chain's short-time rating at 18 A and F2 near +60 C PWR-F12, open
                (FEA-004): PROVISIONAL until it closes"}
'''
PACK_END_P_OLD = "        - {board: p, refs: [W_P, W_N, J_SMB], src:"
PACK_END_P_NEW = "        - {board: p, refs: [W_P, W_N, J_SMB], part: \"W_P and W_N 12 AWG solder lands; J_SMB JST-XH B4B-XH-A 1x4\", src:"
PACK_END_E_OLD = "        - {board: e, refs: [J_BATT, J_SMB], src:"
PACK_END_E_NEW = ("        - {board: e, refs: [J_BATT, J_SMB], part: \"J_BATT Amass XT60 (C98733); J_SMB JST-XH B4B-XH-A(LF)(SN) 1x4 (C144395)\", "
                  "src:")
PACK_HOT_OLD = '        stack lift by the D-14 procedure"\n'
PACK_HOT_NEW = PACK_HOT_OLD + '''\
      levels: "the pack 10.0 to 16.884 V as drawn (4S, 2.5 to 4.2 V a cell), 9.688 to 17.375 V under (B1) at VBAT; the SMBus at the
        gauge's 100 kHz on +3V3_E6 logic (SMBUS_GAUGE); PRES pulled low by P's R14"
      current: "the power lead 10.0 A typical and 18.0 A peak (power), the charge at most 3.0 A (power.charge); the SMBus lead signal
        only"
      harness: "power: 12 AWG, 350 mm, XT60 at E (ASSEMBLY.md section 4); SMBus: a straight XH-to-XH four-way lead, pin for pin
        (smbus.lead)"
      mating: "the XT60 keyed; the XH latches at both ends (smbus); both leads mated with the kit off (hot_plug)"
      judged_by: "check_contracts.py sections 15b (the pack leads' polarity at the XT60) and 15c (J_SMB at both ends, one family, each
        pin's role, the return and the clamps on W_N)"
      tbd: ["the chain's short-time rating at 18 A and F2 near +60 C (PWR-F12, FEA-004); effect: the 18 A service's margin on the
            pack's own path is unstated",
            "the pack's connection pulse in one body diode under (B1), VF and ISM hot (E11-30); effect: the pair's qualification
            before board A's final release"]
      sequencing: "pack connected: the gauge's FETs close onto VBAT; as drawn board E's always-on comes up on CELL_F, under (B1) on
        VSYS_E over the dock's pin 1 (L4-E11 15a, DRAFTED R-177); the inrush into VBAT's capacitors 242.9 A peak, time constant
        33.8 us (over ASCD's 55.6 A for 61.5 us against its 183 us delay; under (B1) the whole pulse in one body diode of the pair,
        TJ 123.3 C from +70 C: MODELED, PROVISIONAL on E11-30); pack disconnected or both FETs open with a source: (B1) the BQ25730
        regulates VSYS at VSYS_MIN (at least 12.054 V with adequate input, MAKER p.10), as drawn U3 holds VBAT at ChargeVoltage
        (CONDITIONAL on TI's D1); the charge held (the hold's flag, FW-A19): (B1) Q39 and Q40 off, VSYS piecewise (SRN under
        12.054 V: at least 12.054 V; SRN over 12.546 V: VSRN + 150 mV within 2 percent; between: at least 11.96 V), the pack feeds
        no kit load (its monitor 0.1398 mA; the held current at most 1 mA on the bench, E11-31); a dead pack (at or under CUV 2.50
        V a cell): as drawn U3 charges through the open discharge FET's body diode at its clamp (384 mA typical, no maximum
        printed), ChargeCurrent 256 mA at POR, (B1) R-b' as above; a cold pack: UTC holds the charge FET, the mat warms the block
        first (FW-A13), under U-01's (II) the kit's hold moves to -7 C (PROVISIONAL on U-01); the graceful stop at 3.00 V a cell
        under load, the gauge's CUV at 2.50 V (2.75 V under U-01's (II)) (L4-E9 4a, 4c, 4d)"
      default_state: "the gauge's FETs on with the battery alone, so the pack feeds VBAT whenever it is fitted; the lead's XT60 is
        the service disconnect; with the XT60 out board E's always-on domain is dark as drawn (CELL_F) and fed from the source
        under (B1) (VSYS_E); PRES reads high with the SMBus lead out (FW-E02)"
      firmware: "FW-A19 (R-a: every charge hold a flag, the state table S1 to S4, the CHRG_INHIBIT bit follows the flag, the
        CHG_INHIBIT line and SHORE_INHIBIT never a hold), FW-A20 (R-b and R-b': ChargeCurrent's two settings under 14.0 V, XDSG or
        PRECHARGE), FW-A22 (R-d: PCHG_COMM 1 and the SUV check in the image), FW-A23 ((B1)'s registers: EN_OOA 0 at boot,
        ChargeCurrent 0 A at POR and after the watchdog), FW-E01 (the gauge's poll inside its 10 s host watchdog), FW-P01 (the
        image)"
      bench: "R-161 (E11-31: pack absent, inhibited, the held current, from cold), R-85 (the dead-pack and no-pack start at 9.00 V),
        E11-30 (the docking pulse on six BUK6Y10-30PX samples at 267.2 A and 37.2 us), V-A11"
'''

USB_KIND_OLD = "      kind: external\n      decision: \"owner ruling D-12, in A's netlist since 458b2873:"
USB_KIND_NEW = '''\
      kind: external
      ends:
        - {board: a, ref: J_USBC_OUT, part: "TBD: a header carrying VBUS, CC1, CC2 and ground with a VBUS rating of at least 4.58 A
           (L4-E9 R-30), effect: the outlet's contact margin is unstated", src: "v2/ecad/tools/gen_sch_a.py:1100-1103"}
        - {board: a, ref: J_USBW, part: "JST-PH 1x4: VBUS_WALL, D-, D+, GND", src: "v2/ecad/tools/gen_sch_a.py:1613-1618"}
        - {case: "the USB-C outlet's receptacle on the connector plate, Bulgin PXP4043/C (5 A per contact, as L4-E4 reads it), and the
           Glenair 233-370 USB 2.0 type A feed-through (owner ruling D-12)"}
      harness: "the outlet's lead from J_USBC_OUT to the Bulgin receptacle and J_USBW's lead to the Glenair feed-through, inside the
        case (ASSEMBLY.md section 4, the wall USB host row); TBD: the outlet lead's construction and gauge at 3 A, effect: its drop
        and its rating are unstated"
      mating: "the Bulgin receptacle and the Glenair coupler are the sealed plate parts; the inside PH housing latches; TBD:
        J_USBC_OUT's housing (R-30), effect: the outlet lead does not mate until the header is named"
      hot_plug: "yes, by design (USB-C and USB type A)"
      decision: "owner ruling D-12, in A's netlist since 458b2873:'''
USB_JB_OLD = '      judged_by: "check_contracts.py section 10 (the wall pair reaches A\'s J_USBW)"\n'
USB_JB_NEW = USB_JB_OLD + '''\
      levels: "the USB-C outlet (J_USBC_OUT, power only): PD contracts 5, 9 and 15 V at 3.0 A each from U19's straps (TI SLVSDG8B
        Tables 2 and 5, Equation 2; MAKER) plus the non-PD 5 V; VBAT 10.0 to 16.884 V into U19 (9.688 to 17.375 V under (B1)); the
        Glenair data port: VBUS_WALL 5 V from +5V_DEV behind U32 (0.9142 A nominal limit)"
      current: "the outlet: 3 A on each contract; with PS-TYP's 45 W at the outlet 112.3 W plan, 7.8 A at 14.4 V from VBAT (L4-E9
        1d IF-12; MODELED). The trip (L4-E4, DRAFTED R-02, apply_gen_sch_a_r138.py, not applied): R138 5 mOhm (HoJLR2512-3W-5mR-1
        percent, C2903482): U18's trip at 3.793 to 4.576 A (VI(TRIP) 19.2 to 22.6 mV, MAKER, with 1 percent and 50 ppm/K over 45
        K), above every 3 A contract and under the Bulgin PXP4043/C receptacle's 5 A; as drawn R138 10 mOhm trips at 1.897 to 2.288
        A, under the 3 A contracts (INFERRED), so the drawn outlet cannot deliver its PDOs until R-02 applies; U19's own average
        limit 4.212 to 5.810 A (R81 10 mOhm, INFERRED) overlaps the trip window, so L4-E4's bench (a) isolates U18's trip from
        U19's; J_USBC_OUT: TBD, a header with a part number and a VBUS rating of at least 4.58 A, effect: the outlet's contact
        margin is unstated (L4-E9 R-30)"
      protection: "U18's OCP (the trip above) and OVP; OUTLET_OK (A U30 NAND) drops the outlet while the PA keys (FW-A05, FW-A06);
        the wall port's eFuse U32 and its USBX_FLT (FW-A07); C2 sheds the outlets at 9.0 A for 10 s or a +50 C cell, USB-C first
        (FW-C09)"
      sequencing: "PD_EN = PD_SW_EN AND OUTLET_OK: the outlet powers only after the panel writes PD_SW_EN (U28 IO1_0) and only while
        the PA is not keyed; after a trip the PD contract is renegotiated (L4-E9 4e); the Glenair port's VBUS on USBX_EN when the
        port is in use (FW-A07)"
      default_state: "off at power-up: PD_SW_EN held low by A R143 (pull-down) and USBX_EN by R190 4.7 k; cable out: the outlet's CC
        lines idle, no contract, no VBUS"
      firmware: "FW-A05 and FW-A06 (the software holds and OUTLET_OK), FW-A07 (the wall port's VBUS and USBX_FLT), FW-C09 (C2's
        shedding order)"
      bench: "L4-E4's outlet procedure: (a) U18's trip isolated from U19's limit, (b) the 3 A row demonstrated at VI(TRIP) 19.2 to
        22.6 mV (L4E4-CURRENT-LIMITS.md); FW-A15 item 8 (the profile changes 15 to 5 V and 9 to 5 V); V-A03"
      tbd: ["J_USBC_OUT's part number and a VBUS contact rating of at least 4.58 A (R-30); effect: the outlet's contact margin is
            unstated"]
'''

POE_OLD = '           enable: "POE_EN = POE_SW_EN AND OUTLET_OK: OFF at power-up and while the PA keys (S-14)"}\n'
POE_NEW = '''\
           enable: "POE_EN = POE_SW_EN AND OUTLET_OK: OFF at power-up and while the PA keys (S-14)",
           monitor: "the PoE monitor U17 senses the stage's INPUT on R227, 5 mOhm from VBAT to POE_VIN (HF-F02 resolved by L4-E9
             R-06, apply_gen_sch_a_u17.py, DRAFTED, not applied), not the 54 V rail: U16's VIN and BIAS on POE_VIN; U17 IN+ on VBAT,
             IN- and VBUS on POE_VIN, its pins at most 20.135 V (the pack-open bound) against the INA226's 36 V; full scale 81.92 mV
             over 5 mOhm is 16.384 A (Current_LSB 0.5 mA, CAL 2048); 3.682 A at a 10.0 V stack for 0.6 A at 54 V over 0.88, 14.33 A
             at the stage's fault bound (72.38 mV); a full-scale sample is a saturated transient (a VBAT step or a hard output
             short), not a current reading; the output power inferred as the input power times the stage's efficiency (0.88,
             undocumented), its alert limit from the stage's input, not its output; accuracy 1.731 percent plus 3.025 mA over the
             IC's -20 to 76.25 C (1.475 percent plus 2 mA at 25 C) (L4-E9 1d IF-13 and part A; MAKER rows of SBOS547C, INFERRED;
             FW-A09 restated); as drawn U17 sits on the 54 V rail over its 40 V absolute maximum (HF-F02 open on the drawn board);
             R227's pulse rating and capacitance envelope PROVISIONAL (R-101)"}
'''

ABP_END_A_OLD = "        - {board: a, refs: [J_5V_S1, J_5V_S2, J_5V_S3, J_5V_DEV, J_54V], src: \"v2/ecad/tools/gen_sch_a.py:1051-1052, 1149\"}"
ABP_END_A_NEW = ("        - {board: a, refs: [J_5V_S1, J_5V_S2, J_5V_S3, J_5V_DEV, J_54V], part: \"JST-VH B2P-VH 1x2 standard header each\", "
                 "src: \"v2/ecad/tools/gen_sch_a.py:1051-1052, 1149\"}")
ABP_END_B_OLD = "        - {board: b, refs: [J_5V_S1, J_5V_S2, J_5V_S3, J_5V_DEV, J_54V], src: \"v2/ecad/tools/gen_sch_b.py:551, 1119, 1210\"}"
ABP_END_B_NEW = ("        - {board: b, refs: [J_5V_S1, J_5V_S2, J_5V_S3, J_5V_DEV, J_54V], part: \"JST-VH B2P-VH 1x2 standard header each\", "
                 "src: \"v2/ecad/tools/gen_sch_b.py:551, 1119, 1210\"}")
ABP_HOT_OLD = ('      hot_plug: "not hot-pluggable (the session\'s choice SC-HF-04 of 27 September 2026 under the owner\'s standing rule, '
               'v2/docs/HW-FW-CONTRACT.md section 8): crimped leads, mate with the kit off"\n')
ABP_HOT_NEW = '''\
      harness: "JST-VH pairs, 16 AWG on the four 5 V leads and 18 AWG on J_54V, 150 mm (cable; ASSEMBLY.md section 4)"
      levels: "+5V_S1, +5V_S2, +5V_S3 and +5V_DEV 5 V rails from board A's converters (converters); +54V_POE 54 V from U16"
      current: "per rail as currents states: the two ends aligned INTERIM since S-98, the PS-ALLTX mode current INCONCLUSIVE at both
        ends (the bench decides it at J_5V_S2 and J_5V_DEV); +54V_POE 0.3 A typical, 0.6 A peak, its input monitored on R227 under
        R-06's draft (currents.monitor)"
      default_state: "the slot rails OFF (SLOT_EN1..3 low at A's pull-downs); +5V_DEV ON by design since 458b2873 (R42); +54V_POE OFF
        (POE_EN low at power-up, R114)"
      sequencing: "DEV_EN with board A's +3V3 (FW-C01), then the charger, then SLOT_EN1..3 one at a time (FW-C01 step 6); POE_EN only
        after the panel has configured U5 and set POE_SW_EN (FW-B14, FW-A06), and dropped while the PA keys (OUTLET_OK)"
      mating: "VH latches at both ends on crimped leads; mated with the kit off (hot_plug)"
      judged_by: "check_contracts.py section 3 (each rail leaves A and enters B on its same-named VH pair)"
      tbd: ["the J_54V contact rating with AWG 18 on the standard header (contact_rating, INCONCLUSIVE); effect: the PoE lead's contact
            margin is unstated",
            "the PS-ALLTX mode current of +5V_S2 and +5V_DEV (I-03, S-98, S-99); effect: the leads' peak basis is INTERIM until the
            bench"]
''' + ABP_HOT_OLD

FANS_SEQ_OLD = '      sequencing: "the sensor controller switches the fans after it boots, on its own thermal policy (FW-E rows)"\n'
FANS_SEQ_NEW = '''\
      sequencing: "the sensor controller switches the fans after it boots, on its own thermal policy (FW-E07, FW-E10); under (B1)
        (DRAFTED R-177, R-181) the fans sit on VSYS_E behind U42's 1.471 to 1.802 A limit: they start one at a time, each with a
        PWM ramp, never both within 1 s and never while U12 starts (FW-E11, E11-39, R-188); one fan's start at most 0.5713 A beside
        U12 and the other fan running, both together at most 0.3356 A each, under U42's least limit 1.471 A; VSYS_E at the least
        limit at least 9.494 V at the supplement floor, so the fans must start at or under it (L4-E11 17a; INFERRED; PROVISIONAL
        until a fan is named, E11-35, R-179)"
'''
FANS_PWR_OLD = '      power: "the pack node is 12 to 16.8 V and the fans are declared 12 V class: rating against 16.8 V TBD (HF-F05)"\n'
FANS_PWR_NEW = '''\
      power: "as drawn the pack node CELL_F, 12 to 16.884 V; under (B1) VSYS_E, 9.539 to 17.375 V (L4-E11 15a, 16e; DRAFTED R-177):
        the fans are declared 12 V class, their maximum supply voltage against 17.375 V and their least operating voltage against
        9.539 V TBD (HF-F05, E11-35, R-179), effect: the fans' selection and board E's final release"
'''
FANS_TBD_OLD = '            "the fan rating at 16.8 V (HF-F05); effect: the fans\' life on the pack node",\n'
FANS_TBD_NEW = ('            "the fan rating at 16.8 V as drawn and at 17.375 V under (B1), and its start at or under 0.5713 A and 9.539 V behind\n'
                '            U42 (HF-F05, E11-35, R-179); effect: the fans\' life on the pack node and their start behind U42",\n')
HEAT_SEQ_OLD = '      sequencing: "HEAT_EN written by the panel; off during every PA key-down (K4, FW-A13)"\n'
HEAT_SEQ_NEW = '''\
      sequencing: "HEAT_EN written by the panel; off during every PA key-down (K4, FW-A13); with no usable pack at a 9.00 V plug the
        mat runs on measured headroom (R-c, FW-A21): on only while the source's measured headroom over the load is at least its
        8.58 W, else cycled, so control is kept whenever P1 alone (at most 20.51 W) is carried (L4-E11 3g; MODELED, PROVISIONAL on
        E11-06)"
'''

YAML_EDITS = [
    ("exact", Y_HEADER_OLD, Y_HEADER_NEW),
    ("block", '      levels: "DC: 9 to 36 V in service', "      current:\n", DC_LEVELS),
    ("block", '        dc: "the LM5069 U6 limits at 4.85 to 6.15 A', '      sequencing: "hot-pluggable by design', DC_CURRENT_DC),
    ("block", '      sequencing: "hot-pluggable by design', '      grounding: "GND_V is board E', DC_SEQ),
    ("exact", DC_TBD_OLD, DC_TBD),
    ("exact", DOCK_END_A_OLD, DOCK_END_A_NEW),
    ("exact", DOCK_END_E_OLD, DOCK_END_E_NEW),
    ("exact", DOCK_VWORK_OLD, DOCK_VWORK_NEW),
    ("exact", DOCK_PRE_OLD, DOCK_PRE_NEW),
    ("exact", DOCK_HOTR1_END, DOCK_PIN1_NEW),
    ("exact", DOCK_NJ_OLD, DOCK_NJ_NEW),
    ("exact", PACK_END_P_OLD, PACK_END_P_NEW),
    ("exact", PACK_END_E_OLD, PACK_END_E_NEW),
    ("exact", PACK_CHAIN_OLD, PACK_CHAIN_NEW),
    ("exact", PACK_HOT_OLD, PACK_HOT_NEW),
    ("exact", USB_KIND_OLD, USB_KIND_NEW),
    ("exact", USB_JB_OLD, USB_JB_NEW),
    ("exact", ABP_END_A_OLD, ABP_END_A_NEW),
    ("exact", ABP_END_B_OLD, ABP_END_B_NEW),
    ("exact", ABP_HOT_OLD, ABP_HOT_NEW),
    ("exact", POE_OLD, POE_NEW),
    ("exact", FANS_SEQ_OLD, FANS_SEQ_NEW),
    ("exact", FANS_PWR_OLD, FANS_PWR_NEW),
    ("exact", FANS_TBD_OLD, FANS_TBD_NEW),
    ("exact", HEAT_SEQ_OLD, HEAT_SEQ_NEW),
]
# The anchors L4-E11's apply_pcb_interfaces_dock.py needs (its YAML_EDITS' old texts): each must still occur exactly once after
# this script, so that draft applies unchanged when the generator drafts apply.
DOCK_DRAFT_ANCHORS = [
    'aliases: [["DOCK_SPARE", "BLK_SPARE"], ["CELL+", "CELL_F", "E\'s pack positive after its F3 blade"]]',
    "pins: {1: GND, 2: GND, 3: GND, 4: GND, 5: GND, 6: GND, 7: GND, 8: SHORE_INHIBIT, 9: USB_E6_P,",
    'the control line since, beside 5 to 7 and 11"',
    'charge_share: "BAT-F06, taken by the session under the owner\'s standing rule (ARCHITECTURE.md section 4.4): board E\'s',
    "findings: [R4A-N13, R4A-N12, R8E-N01, EQ-16, W3DE-DOCK-R1, A04-D2, W3-F09, BAT-F06, PWR-F12]",
]

# ----------------------------------------------------------------------------------------------------- HW-FW-CONTRACT.md
H_VERSION_OLD = "are read at `953f5658`.\n"
H_VERSION_NEW = H_VERSION_OLD + """
**Version 2, 3 October 2026 (Layer 5's power pass, set 27, MESHSAT-1357; `v2/docs/records/l5pwr/`).** Layer 4's power results
are written in: FW-A16 restated and FW-A18, V-A06 to V-A10 applied from L4-E5's draft (`records/l4e5/apply_fw_a16.py`) with
LH-07's condition on FW-A16 and V-A08 as L4-E11 7a restates it for the selected entry (R-135); FW-C08 and FW-A14 restated
(L4-E11 7a, LH-10); FW-A09's U17 row on R227 (L4-E9 R-06, LH-06); FW-A19 to FW-A23 (rules R-a to R-d and (B1)'s registers),
FW-C15 (the margin hold, LH-11), FW-E11 to FW-E13 (the fans' start, the SGP41's shutdown, DCIN_PGD the entry's fault flag),
V-A11, V-C15 and V-E11 to V-E16 (LH-08, LH-09, R-176) added. Every figure is Layer 4's, marked MAKER, INFERRED, MODELED or
PROVISIONAL as its source marks it (its row in `records/l5pwr/L5-POWER-CONTRACTS.md`); a row resting on a release-guarded draft
that no generator carries says DRAFTED with the register row (R-nn) that applies it, and the drawn board stays stated where it
differs; section 4.1 lists the drafts by the rows they move. Nothing here has been built, powered or measured.
"""
H_STATE_OLD = "FIRMWARE: nothing to draw; the obligation is firmware or provisioning.\n"
H_STATE_NEW = ("FIRMWARE: nothing to draw; the obligation is firmware or provisioning. DRAFTED (R-nn): the hardware the row relies\n"
               "  on is a release-guarded Layer 4 draft that no generator carries yet (section 4.1). PROVISIONAL: the row rests on an open\n"
               "  condition and names what would change it.\n")
A16_COND_OLD = ("(a) Hold IIN_HOST at 4.70 A (code 94, 0x5E00; RSNS_RAC = 0b first, FW-A01; L4-E4's setting, provisional with it) and never "
                "write a higher value: the VIN_RAW dependence is FW-A18's pin, not firmware. ")
A16_COND_NEW = (A16_COND_OLD + "IIN_HOST is written 4.70 A only on a board A whose netlist carries the ILIM_HIZ network (H3, FW-A18); on a "
                "board without it the derated 4.00 A of r11dep applies (R11 10 mOhm), or FW-A16 (a)'s scaling (R11 8 mOhm without the network is "
                "not a released configuration) (LH-07; L4-E9 R-25). ")
A16_WHY_OLD = ("| the vehicle entry's LM5069 limits at 4.85 to 6.15 A and its fault timer runs 3.1 to 8.2 ms, a solar deficit empties "
               "VIN_RAW in 1 to 10 ms, and FW-E04's 1 s cannot act inside either; no drawn line tells the tracker from a vehicle on "
               "VIN_RAW (`records/l4e5/L4E5-SOURCE-CONTROL.md`) |")
A16_WHY_NEW = ("| the vehicle entry's LM5069 limits at 4.85 to 6.15 A and its fault timer runs 3.1 to 8.2 ms, a solar deficit empties "
               "VIN_RAW in 1 to 10 ms, and FW-E04's 1 s cannot act inside either; no drawn line tells the tracker from a vehicle on "
               "VIN_RAW (`records/l4e5/L4E5-SOURCE-CONTROL.md`); the selected entry (L4-E11 3c, DRAFTED R-123) breaks at 6.364 A after "
               "0.247 ms at the least, under which the constant 4.70 A keeps 5.983 A at a 9.00 V plug (6.4 percent under; L4-E9 1d IF-05) |")
V_A08_NEW = ("| V-A08 | FW-A16, A18 | transients, recorded apart from steady state: the vehicle supply stepped 24 to 12 V, 36 to 9 V "
             "and 12 to 24 V, plugged and unplugged, and a panel simulator stepped from 100 W into the stage to 50, 30 and 10 W and "
             "back, each under U3's full demand: the entry's U6 never asserts FLT_I (its current over the breaker's lowest 6.364 A for "
             "less than 0.247 ms, its filtered short-circuit sense under 10.36 A), VIN_RAW never falls below 7.24 V (the guard's "
             "highest fall 7.14 V plus 0.1 V), FE_PGOOD never drops; the peak and settling time of U3's input current and of the "
             "entry's current recorded (as L4-E11 7a restates it for the selected entry, E11-21; L4-E9 R-135 and R-76; L4-E5's "
             "LM5069 TIMER and 8.41 V figures superseded, the old millisecond allowance cannot stand against the breaker's 0.247 ms) |")
C08_NEW = ("| FW-C08 | SHORE_INHIBIT on GPIO20 (`C:U3.31`); A R118 and E R26 100 k pull-downs; E's Q8 pulls the entry's UVLO pin low "
           "when it is high (as drawn the LM5069's HS_UVLO; on the selected entry the TPS48110-Q1's EN/UVLO on the same net, DRAFTED "
           "R-123) | Boot low. Asserted only on the operator's 'inputs off' and on the water-on-floor isolation, never for a "
           "temperature or 'no charge' hold (those are FW-A19's flag and the charger's CHRG_INHIBIT bit). When the pack cannot "
           "discharge (states S2 and S4: the gauge's XDSG, no pack, or both FETs open) the bridge first warns that asserting it "
           "removes the kit's supply (L4-E11 7a, rule R-a; LH-10) | `PANEL.md` section 10 (restated 3 October 2026); L4-E11 section 4 "
           "(a hold by SHORE_INHIBIT removes the kit's only supply in S2 and S4); THERMAL-COORDINATION L3's cold hold is FW-A19's "
           "flag, cleared above 3 C with hysteresis | V-C08 | DRAWN |")
A14_NEW = ("| FW-A14 | CHG_INHIBIT `A:U27.4` IO0_0, R21 4.7 k to GND, drives Q6 | Held low (charger enabled) at power-up; asserted "
           "only by firmware, never as a charge hold (a hold is the CHRG_INHIBIT bit or ChargeCurrent 0, FW-A19), and never while "
           "the pack cannot discharge (S2, S4: HIZ stops the converter and removes the kit's only supply) (L4-E11 7a; LH-10) | S-08; "
           "L4-E11 section 4 (rule R-a) | O-CHG-8 | DRAWN |")
A09_NEW = ("| FW-A09 | six INA226 on the kit bus: U8 0x40 (+5V_S1, R31 5 mOhm), U9 0x41 (+5V_S2, R35 6 mOhm), U10 0x44 (+5V_S3, R39 5 "
           "mOhm), U11 0x45 (+5V_DEV, R43 6 mOhm), U14 0x46 (+13V8_PA, R55 6 mOhm), U17 0x47 (as drawn +54V_POE, R71 20 mOhm; DRAFTED "
           "by L4-E9 R-06, `records/l4e9/apply_gen_sch_a_u17.py`, not applied: U17 moved onto R227 5 mOhm from VBAT to POE_VIN, the "
           "PoE stage's INPUT, IN+ on VBAT, IN- and VBUS on POE_VIN, so its pins sit at most at 20.135 V against the INA226's 36 V); "
           "alerts wired-OR on INA_ALERT (`A:U27.19`) | Calibrate each for its own shunt (full scale 81.92 mV over the shunt: 16.38 A, "
           "13.65 A, 16.38 A, 13.65 A, 13.65 A; U17 as drawn 4.10 A, on R227 16.384 A with Current_LSB 0.5 mA and CAL 2048); set the "
           "alert limits from the stage limits. U17 on R227 (L4-E9 1d IF-13 and part A; R-27): its readings are the PoE stage's INPUT "
           "current and POE_VIN (VBUS pin 8 is on POE_VIN; VBAT is POE_VIN plus the shunt's drop); 3.682 A at a 10.0 V stack for 0.6 A "
           "at 54 V over 0.88, 14.33 A at the stage's fault bound (72.38 mV); a full-scale sample is a saturated transient (a VBAT "
           "step or a hard output short), not a current reading; the output power is inferred as the input power times the stage's "
           "efficiency (0.88, undocumented), and its alert limit is set from the stage's input, not its output; accuracy 1.731 "
           "percent plus 3.025 mA over the IC's -20 to 76.25 C (1.475 percent plus 2 mA at 25 C) (MAKER rows of SBOS547C, INFERRED) | "
           "R35, R43 and R55 are the LM5176 ISNS shunts since round 4; U17 on the 54 V rail sits over the INA226's 40 V absolute "
           "maximum (HF-F02), resolved by R-06's draft | V-A04 (on the regenerated board U17 against a reference meter at 10, 50 and "
           "100 percent of the stage's input current, inside 1.731 percent plus 3.025 mA; R-27) | DRAWN; U17's move DRAFTED (R-06), "
           "HF-F02 open on the drawn board |")
FW_A19 = ("| FW-A19 | the charger `A:U3` (as drawn BQ25731; under (B1) BQ25730, DRAFTED R-157): ChargeOption0 bit 0 `CHRG_INHIBIT` and "
          "ChargeCurrent() (REG 0x03/02); the gauge's two FETs (`P:U1` BQ4050, SLUUAQ3A 2.2 and 4.12) give two permissions, charge and "
          "discharge, read by the sensor controller (FW-E01); `CHG_INHIBIT` (FW-A14) and `SHORE_INHIBIT` (FW-C08) each remove the kit's "
          "only supply when the pack cannot discharge | Every charge hold (the cold hold REQ-046, REQ-077's hot hold, the margin hold "
          "FW-C15, the operator's 'no charge') is a FLAG the firmware keeps until its own condition clears it (the cold hold above 3 C "
          "with hysteresis), never cleared by a state change. The state table (L4-E11 section 4, rule R-a): S1 (both FETs on) the bit or "
          "ChargeCurrent 0, the converter keeps carrying the kit from the source (REQ-077 as written); S2 (charge on, discharge off: a "
          "warm CUV trip, an OCD, AOLD or SCD latch) only the bit or ChargeCurrent 0, and whether VSYS stays regulated there is N2 "
          "(Q-TI-3), OPEN until E11-06; S3 (charge off, discharge on: UTD to UTC, OTC, COV) the gauge already holds, a requested hold by "
          "the bit as in S1; S4 (both off: below -9 C, SHUTDOWN, a permanent fail, no pack) the gauge holds and as drawn the bit is NOT "
          "set (the one exception, so that N2 never arises where the source alone carries the kit), the bit written from the flag the "
          "moment a FET closes; under (B1) the bit follows the flag in every state, S4's exception withdrawn (R-158). In every state "
          "the CHG_INHIBIT line (HIZ) and SHORE_INHIBIT are never a charge hold; in S2 and S4 neither is asserted. After a charger POR "
          "the drawn charger can charge at 256 mA before the flag's bit is written, under R-b's bound (FW-A20); under (B1) ChargeCurrent "
          "is 0 A until written | REQ-077 asks the charger to carry the kit while the charge is held and no pack fallback is relied on; "
          "finding U4-F1's holds (L4-E11 2 and 4): a hold made by HIZ or SHORE_INHIBIT in S2 or S4 turns the kit off | V-A11; O-CHG-3; "
          "R-85 | FIRMWARE (R-126; L4-E9 R-125); the (B1) half DRAFTED (R-157, R-158); S2's N2 OPEN (E11-06) |")
FW_A20 = ("| FW-A20 | ChargeCurrent() (REG 0x03/02) with the charge shunt R17 5 mOhm (FW-A02); U3's own SRN reading; the gauge's XDSG "
          "and PRECHARGE flags over SMBus (FW-E01); as drawn the pack's open discharge FET's body diode (`P:Q2`) carries a dead pack's "
          "charge; under (B1) one FET of the pair Q39 and Q40 in LDO mode (DRAFTED R-157) | R-b (as drawn; L4-E11 section 4): while U3's "
          "SRN reading is under 14.0 V, or the gauge reports XDSG or PRECHARGE, ChargeCurrent() takes exactly two settings, 0x0000 (no "
          "charge) and 0x0200 (1024 mA set), and no value under 0x0200 (TI prints no accuracy for one); TI's accuracy row for 0x0200, "
          "-18 percent / +21.5 percent, holds for a 5 mOhm RSR with VBAT above VSYS_MIN at 0 to 85 C (SLUSE66A p.10, MAKER): case (i) "
          "0.8314 to 1.2567 A (R17 at 1 percent, INFERRED), so Q2's diode dissipates at most 1.257 W, its junction at most 124.9 C at "
          "the 62.1 C inside air against 150 C, CONDITIONAL on case (i) and on board P's copper giving TI's 50 C/W (E11-22); cases "
          "(ii) (the charger outside 0 to 85 C) and (iii) (SRN under VSYS_MIN: the clamp, 384 mA typical, no maximum printed) "
          "INCONCLUSIVE (E11-22); the charge power under R-b at most 1.2567 A x 16.884 V = 21.22 W (17.59 W at the 14 V threshold), "
          "drawn only from what DPM leaves after the system; beyond it RT1's PTC beside the FETs opens them (a permanent fail, safe, "
          "named). R-b' (under (B1); L4-E11 15c, R-158): under VSYS_MIN ChargeCurrent 0x0080 only, at most 0.33616 A with R17's 1 "
          "percent, all of it in one FET of the pair in LDO mode; no charge under 5.7 V on SRN | TI prints accuracy for 0x0200 and for "
          "nothing under it; the clamp's maximum is not printed (D7) | V-A11; R-85 (E11-06); E11-22 | FIRMWARE (R-126); PROVISIONAL on "
          "E11-22 (cases (ii) and (iii), board P's copper); the (B1) half DRAFTED (R-157, R-158) |")
FW_A21 = ("| FW-A21 | the source envelope at the plug with no usable pack (L4-E11 3h, INFERRED, U3 0.9733): at VBAT 29.09 to 42.52 W "
          "from a 9.00 V plug, 32.22 to 47.72 W at 12 V, 69.97 to 90.81 W at 24 V, 84.55 to 99.64 W at 36 V; the measured input "
          "(VIN_MON, FW-E04; the charger's input ADC); the switched loads' enables on `A:U27` and `A:U28` and the modules' SLOT_EN; the "
          "mat on `A:U22` and `U33` (FW-A13) | R-c (L4-E11 3g and section 4): while the pack cannot discharge (S2, S4) the bridge keeps "
          "the kit's load under the envelope's minimum at the measured input by the shedding sequence P0 to P3: P0 the bridge boots on "
          "slot 2 (PS-SURV); P1 shed, the two mixer fans, the HF module, the Geiger module and the 5G module held off, the bridge, "
          "GNSS, Iridium and the panel (the SOS path) kept, P1 at most 20.51 W at VBAT (plan 19.57 W; the hi corner 35.24 W is an "
          "estimate's upper bound, not carried); P2 the warm-up, P1 with the regulated mat on MEASURED HEADROOM: the mat on only while "
          "the source's measured headroom over the load is at least its 8.58 W, else cycled (28.12 W plan, 0.98 W in hand at the "
          "source's least 29.09 W); P3 charge once the cells read over 3 C and the cold hold clears, the surplus over P1 to the charge "
          "by DPM within R-b's bounds (FW-A20). On a source-only brown-out the charger may latch off (under (B1) VSYS_UVP: the 7th "
          "failure inside 90 s, at most 3.062 s after the first window, E11-31): the host clears the fault bit when it can, else the "
          "operator re-plugs the source; the first window's success is not bounded on held evidence (0.5 A is an input ceiling, not a "
          "delivered current) | REQ-015's 9 V taken at the kit's plug (L4-E11 3h, SESSION): the source's least at 9.00 V cannot carry "
          "the 42.8 W profile, and REQ-024's cold start needs the mat before any charge (REQ-046) | V-A11; R-85 (E11-06: P1 at most "
          "20.51 W, the front end at least 0.88021); E11-23 (the warm-up time) | FIRMWARE (R-126); PROVISIONAL: REQ-015 at 9.00 V a "
          "CONDITIONAL CANDIDATE until E11-06, E11-09, E11-22 and E11-23; the (B1) latch figures DRAFTED (R-157) |")
FW_A22 = ("| FW-A22 | the gauge's image (FW-P01): PCHG_COMM and the SUV permanent fail (`review-packets/battery/PRIMARY-CONFIGURATION.md`) "
          "| R-d (L4-E11 section 4): the image keeps PCHG_COMM 1 and the SUV check (SUV permanent fail at 1.0 V), with Q-TI-7 open; a "
          "pre-charge path on board P (approach (C), a PCHG FET and resistor) is not taken, so a dead pack's charge is the charger's "
          "(FW-A20) | the comparison of L4-E11 section 4: (C) puts 3.4 to 9.0 W into the sealed case and leaves a resistor path round "
          "both protection FETs | O-CHG-1; P10 to P14 | FIRMWARE (image; R-126) |")
FW_A23 = ("| FW-A23 | under (B1) only (DRAFTED R-157, not applied): `A:U3` BQ25730RSNR (SLUSE65A), pin 21 BATDRV driving the pair Q39 "
          "and Q40 (two BUK6Y10-30PX); its power-on values EN_OOA 1b, ChargeCurrent 0 A, VSYS_MIN at the 4S default, EN_LDO, "
          "EN_PORT_CTRL, BATFET_ENZ and BATFETOFF_HIZ at reset; the device ID D5h; the watchdog 175 s | At every charger POR: EN_OOA "
          "written 0 first (the printed VSYS accuracy holds only after that write, E11-31); ChargeCurrent written for any charge (0 A "
          "at POR and after the watchdog's 175 s, so the watchdog is serviced or WDTMR_ADJ set 00); VSYS_MIN, EN_LDO, EN_PORT_CTRL, "
          "BATFET_ENZ and BATFETOFF_HIZ never written from their power-on values; the device ID D5h checked before any write; R-a's "
          "bit following the hold flag in every state (S4's exception withdrawn, FW-A19); R-b' under VSYS_MIN (FW-A20); IIN_HOST 4.70 "
          "A and VINDPM as FW-A16; every ChargeOption write read-modify-write (FW-A17's rule, with the BQ25730's own register map) | "
          "the three modes' VSYS bounds rest on these registers' power-on values (L4-E11 12c and 15d; MAKER rows): pack absent at "
          "least 12.054 V, held with SRN over 12.546 V VSRN + 150 mV within 2 percent, between at least 11.96 V | V-A11 (R-161, "
          "E11-31: a forced boot, a watchdog expiry and each of the three modes read back the registers as written) | DRAFTED (R-157, "
          "R-158; applied with the charger draft, after its release record) |")
FW_C15 = ("| FW-C15 | the margin hold (L4-E12 section 6, E5's case beyond the envelope; SESSION, PROVISIONAL): the hold's reference, a "
          "temperature sensor in the mixed air near the +70 C parts or board B's TMP117 (`B:U10`, 0x49) with its offset calibrated at "
          "T-H1 to +-0.899099 K; the actors the hot stop already uses (FW-C13: `A:U27`, `A:U28`, the charger's `CHRG_INHIBIT` bit), "
          "board B's `U6` software enables RB_SW_EN (U503), LORA_ON (U504) and ZB_ON (U505), and board E's GEIGER_EN (`E:U10` GPIO18, "
          "U16) over the sensor controller | Trigger: a reading at or over 68.65 C of mixed air plus the reference's calibrated offset, "
          "in two readings in a row; actions: set the charger's CHRG_INHIBIT bit as the hold's flag (FW-A19), never the CHG_INHIBIT "
          "line; board D and the PA rail off through board A's expanders (as H1 does); the RockBLOCK, the LoRa module and both E72 off "
          "through their software enables, the Geiger module off through GEIGER_EN; the running module idled with its logging kept; an "
          "SOS raised meanwhile is queued as under EMCON (D-10) and the operator told; MASTER CAUT and the e-paper 'MARGIN HOLD: "
          "COOLING'. Restore: 5 K under the trigger after 30 minutes (PROVISIONAL). Order against the hot stop: the hold acts under "
          "FW-C09's heat stage and before FW-C13's H1 (the cells' +56.5 C); H1 and H2 override it | L4-E12 section 6: with E3-O's "
          "radios on the mixed air settles at 67.55 C and E5 needs 70.00 C at M7's 2.159 W/K line, a window of 2.45 K that exists only "
          "with a reference within +-0.899099 K of the air at the +70 C parts (the TMP117 across the exhaust's 0 to 5.64 K spread does "
          "not give it: placement or calibration, Layer 9); R-138, R-139 | V-C15 (a forced hold at room temperature); E3-O and E5 "
          "(R-109); T-H1's calibration point (R-104) | FIRMWARE (R-139); PROVISIONAL: the trigger and the restore rest on the hold's "
          "reference (its placement in the mixed air or its calibration at T-H1, U-02's line) and on the 61 s lag ASSUMPTION; a longer "
          "lag or a reference outside +-0.899099 K re-derives 68.65 C |")
FW_E11 = ("| FW-E11 | the mixer fans on `E:J_FAN1`, `J_FAN2` (FW-E07): as drawn on CELL_F; under (B1) on VSYS_E behind board A's eFuse "
          "U42 TPS16630 (I(OL) 1.4713 to 1.8018 A at R221 11.0 kOhm, a regulated steady setting; L4-E11 16e and 17a; DRAFTED R-177, "
          "R-181, not applied), with U12's 0.8 A on the same feed; PWM GPIO8, 9; tach GPIO10, 11 | Start the mixer fans one at a time, "
          "each with a PWM ramp, never both within 1 s and never while U12 starts (E11-39, R-188): one fan's start at most 0.5713 A "
          "beside U12 and the other fan running at 0.1 A, both together at most 0.3356 A each, under U42's least limit 1.471 A; VSYS_E "
          "at the least limit is at least 9.494 V at the supplement floor, so a fan that cannot start at or under 0.5713 A and 9.494 V "
          "is not fitted (E11-35, R-179: no fan is named); a stall reported within 5 s (FW-E07); in H1 and H2 full speed (FW-E10) | a "
          "fan start that trips U42 drops board E's whole auxiliary domain for 500 to 800 ms, which board A reads as HOT-R1 lost | "
          "V-E11 (R-188's acceptance: one fan ramping at a time, the other and U12 settled, the current through J_DOCK pin 1 under "
          "1.471 A at every start, on E11-38's specimen or the first prototype); R-184 (f) | FIRMWARE; DRAFTED (R-177, R-181); "
          "PROVISIONAL: a fan named whose start exceeds 0.5713 A, or U42's limit read outside 1.471 to 1.802 A (E11-38), re-derives "
          "the rule |")
FW_E12 = ("| FW-E12 | the SGP41 `E:U17` (C3659325, I2C 0x59 on the sensor bus SDA1 and SCL1, VDD on SGP_VDD through R57 4.7 R, VDDH on "
          "+3V3_E6; `gen_sch_e.py:825-827`): no load switch from this controller and no TMP117 on its carrier are drawn (L4-E12 section "
          "6 names both: OWED to board E's generator; board E's BME688 `U14` is not the reference, its +-0.5 C a typical); Sensirion's "
          "Table 4 (sensing to +50 C) and Table 5 (absolute +55 C) | Power the SGP41 off at a reading of 54.0 C on a TMP117 on its "
          "carrier (54.095833 C exact, rounded down: the SGP41 then at most 54.904167 C, under Table 5's +55 C); power it on, and use "
          "its output for REQ-042, only at or under 49.0 C (49.095833 C exact); between the two keep it powered with its output logged "
          "as outside Table 4's recommended range and its channel reported as not covered (CFL-002 option C); off at every start until "
          "a reading at or under 49.0 C; after storage outside 5 to 30 C its channel reported as not covered until Sensirion states "
          "otherwise | L4-E12 sections 6 and 17.1 (R-138, R-139): sensing is supported to +50 C only, the +55 C row is a screen; the "
          "0.5 K placement allowance and the 0.254167 K lag (15 K/h times 61 s) are ASSUMPTIONS | V-E12 (a forced shutdown and power-on "
          "at room temperature; the TMP117's lag behind a reference thermocouple at the SGP41 on a ramp of at least 15 K/h at most "
          "0.254167 K at 54.0 C, R-139) | FIRMWARE (R-139); the switch and the carrier TMP117 OWED; PROVISIONAL: a measured lag over "
          "0.254167 K (the sensor's time constant over 83.0 s, 71.0 s on the TMP117N grade) re-derives 54.0 C and 49.0 C before they "
          "are used |")
FW_E13 = ("| FW-E13 | DCIN_PGD on `E:U10.15` with R25 10 k to +3V3_E6: as drawn the LM5069 `E:U6` pin 8 PGD (power good, "
          "`gen_sch_e.py:362-365`); on the selected entry (L4-E11 3c, DRAFTED R-123, `records/l4e11/apply_gen_sch_e_entry.py`, not "
          "applied) the TPS48110-Q1's open-drain fault flags FLT_T (pin 4) and FLT_I (pin 5), both on this net, low on an overcurrent, "
          "a short circuit or an overtemperature | Read it as the entry's FAULT FLAG, no longer a power-good line: low = the breaker "
          "tripped (6.364 / 6.8 / 7.136 A after 0.247 / 0.37 / 0.49 ms, MAKER), a short circuit (10.36 / 12.04 / 13.87 A filtered) or "
          "an overtemperature, with a retry every 0.5 s; report every assertion with a time over USB; the input's presence is the "
          "charger's input-present bit (SHORE, `PANEL.md` section 10) and FE_PGOOD (FW-A16), never this line; on the drawn board the "
          "line still means power good | L4-E11 7a (E11-03, LH-10): the selected entry's pins; a line read as power good would read a "
          "retrying breaker as a dropping input | V-E13 (an injected overcurrent at the entry: the line low within 0.49 ms and the "
          "retry seen every 0.5 s; on the drawn board the power-good sense recorded) | DRAWN (the line); its meaning DRAFTED (R-123) |")
V_A11 = ("| V-A11 | FW-A19 to A23 | R-85 and R-161: at 9.00 V at the plug (the interconnect at its resistance ceiling), 12 V and 24 V, "
         "the shedding sequence P0 to P3 with the pack cold-soaked (S4), at a warm CUV (S2: the charge held by the bit, VSYS stays "
         "up) and absent, P1 at most 20.51 W at VBAT, the front end at least 0.88021; on the (B1) build a forced charger boot, a "
         "watchdog expiry and each of the three modes read back every register as written (EN_OOA 0, ChargeCurrent 0 A at POR, "
         "VSYS_MIN unchanged); R-b' on a pack under VSYS_MIN; the held pack current at most 1 mA; the hold's flag kept across a FET "
         "closing and written to the bit at once; CHG_INHIBIT and SHORE_INHIBIT never asserted in S2 or S4 by any hold |")
V_C15 = ("| V-C15 | FW-C15 | a forced margin hold at room temperature (the reference substituted at 68.65 C plus its offset, two "
         "readings): every action of FW-C15 seen (the bit, board D and the PA rail, the three software enables, GEIGER_EN, the module "
         "idled with its logging kept, the SOS queued and told), the restore after 30 minutes at 5 K under; the hot stop's H1 "
         "overriding it when the cells' reading is substituted at +56.5 C |")
V_E11 = ("| V-E11 | FW-E11 | a forced start on the (B1) build: one fan ramping at a time, the other and U12 settled, never both within "
         "1 s, the current through J_DOCK pin 1 under 1.471 A at every start, VSYS_E at least 9.494 V at the supplement floor (R-188; "
         "R-184 (f) on E11-38's specimen or the first prototype) |")
V_E12 = ("| V-E12 | FW-E12 | a forced SGP41 shutdown and power-on at room temperature (the TMP117 reading substituted at 54.0 C and "
         "49.0 C): off, logged as outside Table 4 between the two, on and used at or under 49.0 C, off at every start until then; the "
         "TMP117's lag behind a reference thermocouple at the SGP41 on a ramp of at least 15 K/h, at most 0.254167 K at 54.0 C "
         "(R-139) |")
V_E13 = ("| V-E13 | FW-E13 | on the regenerated board E (R-123): an injected overcurrent at the entry (a load step past 6.364 A, and a "
         "short at DC_HS): DCIN_PGD low within 0.49 ms, the retry every 0.5 s seen, every assertion reported with a time; on the drawn "
         "board the power-good sense recorded against the LM5069's PGD |")
V_E14 = ("| V-E14 | REQ-015 (IF-EXT-DC, the vehicle entry) | with a panel simulator holding TRK_OUT at its ceiling, the vehicle supply "
         "reversed at -36 V and then at +40 V: no damage; DC_P, DC_F and Q1's VDS recorded (at most 66.2 V reversed); the entry's OV "
         "trip inside 39.6 to 41.22 V (L4-E11); a start from 9.00 V at the plug through the interconnect at its resistance ceiling, "
         "the UVLO on by 8.44 V of DC_P (LH-08) |")
V_E15 = ("| V-E15 | REQ-016 (IF-EXT-DC, the solar backstop) | the input current at which SWEN falls, at 17.6 V and 25 V, inside 3.0468 "
         "to 3.7408 A at 25 V, at commissioning and at layer 8's interval (L4-E7R 7b.15; LH-09); no firmware row: the backstop acts on "
         "SWEN in hardware and reports to no controller |")
V_E16 = ("| V-E16 | the solar guard (IF-EXT-DC; R-176 rows 1 to 6, DRAFTED R-173) | (1) the cut-off's rise and fall on a ramped supply: "
         "28.55 to 31.06 V rising, 27.07 V or more falling; (2) a 36 V supply connected cold: Q12 never conducts, D4 carries nothing, "
         "PV_F at most 75 V; (3) at layer 9, the waveforms at the IC pins: a 36 V supply stepped onto the port with the guard on, from "
         "about 7.5 V and from 25 V, through a loop measured first: U5's CSPIN to CSNIN within +-0.240 V, U21 turning Q12 off (at most "
         "61 A, within 12 us), D4 carrying nothing, PV_P under 31.80 V, a pass only for a loop at or over 3.30 uH until B6-ENG-1 is "
         "decided (PROVISIONAL: L4-E7's round 3 on B6 is running; R-180, R-186 or R-187); (4) a reversed bench panel's curve: no "
         "current, the high side's pins against GND; (5) Q13's leakage at the hot end, under 32.1 uA; (6) no short-circuit trip with "
         "C126 at 330 pF in operation and under CS116 (R-174) |")
SEC41 = """### 4.1 What Layer 4's power drafts change in these rows (set 27, 3 October 2026; none applied)

Every draft is release-guarded (`v2/docs/records/l4e*/apply_*.py`) and applied by its generator owner after its release record;
a row above that rests on one says DRAFTED with the register row (R-nn) that applies it, and the drawn board stays stated where
it differs. The register is `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md`; the marks and triggers are
`v2/docs/records/l5pwr/L5-POWER-CONTRACTS.md`.

| Draft (register row) | Rows it moves | What, and the rows' state until it applies |
|---|---|---|
| R-157 the BQ25730 charger with the battery FET pair Q39 and Q40 and the eFuse U42 (B1) (`records/l4e11/apply_gen_sch_a_charger.py`) | FW-A19, FW-A20, FW-A23, FW-E11, V-A11, V-E11 | the state table's S4 exception withdrawn, R-b', the power-on registers, the dock's VSYS_DOCK feed; as drawn the BQ25731's rules R-a to R-d apply |
| R-177 board E's auxiliary domain on VSYS_E (`apply_gen_sch_e_aux.py`), R-181 U42, R-178 IF-AE-DOCK's pins (`apply_pcb_interfaces_dock.py`) | FW-E11, V-E11 | the fans and U12 on VSYS_E behind U42's 1.471 to 1.802 A; as drawn on CELL_F with no limit |
| R-123 the vehicle entry TPS48110-Q1 (`apply_gen_sch_e_entry.py`) | FW-C08 (the UVLO pin), FW-E13, V-E13, V-E14, V-A08 | DCIN_PGD the entry's fault flag; the breaker's rows; as drawn the LM5069's PGD and 3.1 to 8.2 ms timer |
| R-06 U17 onto R227 (`records/l4e9/apply_gen_sch_a_u17.py`) | FW-A09, V-A04 | U17's calibration and meaning; as drawn U17 over the INA226's 40 V (HF-F02) |
| R-03 the H3 network on ILIM_HIZ (no draft yet), R-124 U34's guard (`records/l4e11/apply_gen_sch_a_guard.py`) | FW-A16, FW-A18, V-A06 to V-A10 | the constant 4.70 A holds only with the network (LH-07's condition); as drawn the derated 4.00 A of r11dep |
| R-173 the solar guard (`records/l4e7/apply_gen_sch_e_solar_guard.py`); R-12, R-19 to R-21, R-98 the stage's settings | V-E15, V-E16 | the backstop's trip and the guard's six bench rows; row 3 a pass only from a 3.30 uH loop until B6-ENG-1 |
| R-02 R138 5 mOhm (`records/l4e4/apply_gen_sch_a_r138.py`) | none here (`pcb_interfaces.yaml` IF-EXT-USB) | the outlet's trip 3.793 to 4.576 A; as drawn 1.897 to 2.288 A, under the 3 A contracts |
| the SGP41's load switch and its carrier TMP117 (L4-E12 section 6; no draft) | FW-E12, V-E12 | OWED to board E's generator; the thresholds stand on L4-E12's arithmetic |

"""
H_SEC5_OLD = "## 5. Verification items this contract adds (V-nn)\n"
H_HEAD_A_OLD = "### 3.1 Board A: power controller, charger, monitors and enables (FW-A01 to FW-A18)\n"
H_HEAD_A_NEW = "### 3.1 Board A: power controller, charger, monitors and enables (FW-A01 to FW-A23)\n"
H_HEAD_C_OLD = "### 3.2 Panel controller, board C (FW-C01 to FW-C14)\n"
H_HEAD_C_NEW = "### 3.2 Panel controller, board C (FW-C01 to FW-C15)\n"
H_HEAD_E_OLD = "### 3.5 Sensor controller, board E (FW-E01 to FW-E10)\n"
H_HEAD_E_NEW = "### 3.5 Sensor controller, board E (FW-E01 to FW-E13)\n"
H_LOG = ("| 2 (L5-PWR) | 3 October 2026 | By Layer 5's power pass (MESHSAT-1357, set 27, `records/l5pwr/`): L4-E5's `apply_fw_a16.py` "
         "applied (FW-A16 restated, FW-A18, V-A06 to V-A10, FW-E04, FW-C01's step 5) with LH-07's condition on FW-A16 and V-A08 as L4-E11 "
         "7a restates it (R-135); FW-C08 and FW-A14 restated (L4-E11 7a, R-125); FW-A09's U17 on R227 (R-06, R-27); FW-A19 to FW-A23 "
         "(rules R-a to R-d and (B1)'s registers, R-126, R-158), FW-C15 (the margin hold, R-138, R-139), FW-E11 (the fans' start, R-188), "
         "FW-E12 (the SGP41's shutdown, R-139), FW-E13 (DCIN_PGD the entry's fault flag, R-125); V-A11, V-C15, V-E11 to V-E16 (LH-08, "
         "LH-09, R-176); section 4.1; the version paragraph and the State legend |")


def cells(line):
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return None
    return [c.strip() for c in s[1:-1].split("|")]


def row_index(lines, first_cell):
    hits = [i for i, l in enumerate(lines) if (cells(l) or [""])[0] == first_cell]
    if len(hits) != 1:
        refuse("row %s occurs %d times, not once" % (first_cell, len(hits)))
    return hits[0]


def patch_hwfw(t):
    if "| FW-A19 |" in t or "| V-E16 |" in t or "Version 2, 3 October 2026" in t:
        refuse("already applied (FW-A19, V-E16 or the version paragraph is present)")
    lines = t.split("\n")
    firsts = [(cells(l) or [""])[0] for l in lines]
    if "FW-A18" not in firsts or "V-A10" not in firsts:
        refuse("ORDER: run v2/docs/records/l4e5/apply_fw_a16.py first (FW-A18 and V-A10 are not rows yet)")
    for what, old in (("the version anchor", H_VERSION_OLD), ("the State legend", H_STATE_OLD), ("FW-A16's (a)", A16_COND_OLD),
                      ("FW-A16's why cell", A16_WHY_OLD), ("section 5's heading", H_SEC5_OLD), ("3.1's heading", H_HEAD_A_OLD),
                      ("3.2's heading", H_HEAD_C_OLD), ("3.5's heading", H_HEAD_E_OLD)):
        if t.count(old) != 1:
            refuse("%s occurs %d times, not once" % (what, t.count(old)))
    # the rows replaced whole, by their first cell
    i_c08, i_a14, i_a09, i_a08 = (row_index(lines, k) for k in ("FW-C08", "FW-A14", "FW-A09", "V-A08"))
    n6 = len(cells(lines[i_c08]))
    n3 = len(cells(lines[i_a08]))
    for row in (C08_NEW, A14_NEW, A09_NEW, FW_A19, FW_A20, FW_A21, FW_A22, FW_A23, FW_C15, FW_E11, FW_E12, FW_E13):
        if len(cells(row)) != n6:
            refuse("a contract row does not have the table's %d cells: %s" % (n6, row[:40]))
    for row in (V_A08_NEW, V_A11, V_C15, V_E11, V_E12, V_E13, V_E14, V_E15, V_E16):
        if len(cells(row)) != n3:
            refuse("a verification row does not have the table's %d cells: %s" % (n3, row[:40]))
    k = len(lines) - 1
    while k >= 0 and not lines[k].strip():
        k -= 1
    last = cells(lines[k])
    if not last or len(cells(H_LOG)) != len(last) or not last[0].startswith("1 ("):
        refuse("the change record's last row is not a version-1 row with the table's cells")
    lines[i_c08] = C08_NEW
    lines[i_a14] = A14_NEW
    lines[i_a09] = A09_NEW
    lines[i_a08] = V_A08_NEW
    # inserts, last first so the earlier indices stay valid
    inserts = [(row_index(lines, "V-E08"), [V_E11, V_E12, V_E13, V_E14, V_E15, V_E16]),
               (row_index(lines, "V-C13"), [V_C15]),
               (row_index(lines, "V-A10"), [V_A11]),
               (row_index(lines, "FW-E10"), [FW_E11, FW_E12, FW_E13]),
               (row_index(lines, "FW-C14"), [FW_C15]),
               (row_index(lines, "FW-A18"), [FW_A19, FW_A20, FW_A21, FW_A22, FW_A23])]
    inserts.append((k, [H_LOG]))
    for idx, rows in sorted(inserts, key=lambda x: -x[0]):
        for r_ in reversed(rows):
            lines.insert(idx + 1, r_)
    out = "\n".join(lines)
    out = out.replace(H_VERSION_OLD, H_VERSION_NEW).replace(H_STATE_OLD, H_STATE_NEW).replace(A16_COND_OLD, A16_COND_NEW)
    out = out.replace(A16_WHY_OLD, A16_WHY_NEW).replace(H_SEC5_OLD, SEC41 + H_SEC5_OLD)
    out = out.replace(H_HEAD_A_OLD, H_HEAD_A_NEW).replace(H_HEAD_C_OLD, H_HEAD_C_NEW).replace(H_HEAD_E_OLD, H_HEAD_E_NEW)
    # re-parse: every row of every table has its header's cell count; every FW and V id is unique
    width, seen = None, {}
    for l in out.split("\n"):
        c = cells(l)
        if c is None:
            width = None
            continue
        if width is None:
            width = len(c)
        elif len(c) != width and not all(x.strip("-") == "" for x in c):
            refuse("a table row has %d cells where its header has %d: %s" % (len(c), width, l[:60]))
        if re.match(r"^(FW|V)-[A-Z]\d\d$", c[0]):
            if c[0] in seen:
                refuse("row %s occurs twice" % c[0])
            seen[c[0]] = 1
    return out


# ------------------------------------------------------------------------------------------------------------ PANEL.md
P_OLD = ('The bridge asks the controller to assert it when the pack temperature (the pack gauge\'s own thermistor, read by the '
         'sensor controller on E6 and reported over USB) is below 0 C, when the operator sets "no charge", and clears it with '
         'hysteresis (charge again above 3 C).')
P_NEW = ("Every charge hold (cold, hot, the margin hold, or the operator's 'no charge') is a flag the firmware keeps until its own "
         "condition clears it (the cold hold, read from the pack gauge's own thermistor by the sensor controller on E6 and reported "
         "over USB, below 0 C and cleared with hysteresis above 3 C), whatever the pack's state. While the pack can take charge or "
         "discharge, the flag sets the charger's CHRG_INHIBIT bit; with both pack FETs open the gauge holds and the bit is left clear, "
         "and it is written from the flag the moment a FET closes. No hold uses the CHG_INHIBIT line or SHORE_INHIBIT. The bridge asks "
         "the controller to assert SHORE_INHIBIT only for 'inputs off' and the water-on-floor isolation, with a warning first while "
         "the pack cannot discharge (L4-E11 7a, rule R-a; HW-FW-CONTRACT.md FW-A19, FW-C08 and FW-A14; restated 3 October 2026, Layer "
         "5's power pass).")


def patch_panel(t):
    if P_NEW in t:
        refuse("already applied")
    if t.count(P_OLD) != 1:
        refuse("PANEL.md section 10's sentence occurs %d times, not once" % t.count(P_OLD))
    out = t.replace(P_OLD, P_NEW)
    if out.count("\n## 10. Shore charge inhibit and the pack\n") != 1:
        refuse("section 10's heading is not where it was")
    return out


# ----------------------------------------------------------------------------------------------------------------- yaml
def patch_yaml(t):
    import yaml
    if "pin1_vsys_dock:" in t or "LAYER 5'S POWER PASS" in t:
        refuse("already applied (pin1_vsys_dock or the pass's header is present)")
    new = t
    for ed in YAML_EDITS:
        if ed[0] == "exact":
            _k, old, rep = ed
            if new.count(old) != 1:
                refuse("the old text occurs %d times, not once: %r" % (new.count(old), old[:70]))
            if rep != old and new.count(rep) != 0:
                refuse("already applied: %r" % rep[:70])
            new = new.replace(old, rep)
        else:
            _k, start, end, rep = ed
            if new.count(start) != 1 or new.count(end) != 1:
                refuse("a block's markers do not occur once each: %r / %r" % (start[:50], end[:50]))
            i, j = new.index(start), new.index(end)
            if j <= i:
                refuse("a block's end marker precedes its start: %r" % start[:50])
            new = new[:i] + rep + new[j:]
    if new == t:
        refuse("the result does not differ")
    try:
        doc = yaml.safe_load(new)
    except yaml.YAMLError as e:
        refuse("the result does not load as YAML: %s" % e)
    cs = doc["board_to_board"]["contracts"]
    dock = cs["IF-AE-DOCK"]
    if dock["pins"][1] != "GND" or "pin1_vsys_dock" not in dock or "VSYS_DOCK" not in dock["pin1_vsys_dock"]:
        refuse("IF-AE-DOCK does not keep pin 1 as the committed GND beside the drafted pin1_vsys_dock field")
    for cid, keys in (("IF-EXT-DC", ("firmware", "bench", "l4_defects")),
                      ("IF-PE-PACK", ("levels", "current", "harness", "mating", "judged_by", "tbd", "sequencing", "default_state", "firmware", "bench")),
                      ("IF-EXT-USB", ("ends", "harness", "mating", "hot_plug", "levels", "current", "protection", "sequencing", "default_state", "firmware", "bench", "tbd")),
                      ("IF-AB-POWER", ("harness", "levels", "current", "default_state", "sequencing", "mating", "judged_by", "tbd")),
                      ("IF-AE-DOCK", ("levels", "current", "harness", "mating", "judged_by", "tbd", "sequencing", "default_state", "cable_out_states", "firmware", "bench"))):
        for k in keys:
            if not cs[cid].get(k):
                refuse("%s lacks %s after the patch" % (cid, k))
    if "monitor" not in cs["IF-AB-POWER"]["currents"][-1]:
        refuse("IF-AB-POWER's +54V_POE row lacks its monitor")
    for a in DOCK_DRAFT_ANCHORS:
        if new.count(a) != 1:
            refuse("L4-E11's dock draft anchor no longer occurs once: %r" % a[:60])
    return new


KINDS = {"pcb_interfaces.yaml": patch_yaml, "HW-FW-CONTRACT.md": patch_hwfw, "PANEL.md": patch_panel}


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    fn = KINDS.get(os.path.basename(target))
    if fn is None:
        refuse("TARGET is none of %s" % ", ".join(sorted(KINDS)))
    text = open(target, encoding="utf-8").read()
    new = fn(text)
    if chr(0x2014) in new or chr(0x2013) in new:
        refuse("a dash character in the result")
    base = os.path.basename(target)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/" + base, "b/" + base, n=0))
    if not write:
        print("%s: CHECK OK %s, nothing written" % (NAME, base))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    if open(target, encoding="utf-8").read() != new:
        refuse("the written file does not read back as the patched text")
    print("%s: WRITTEN %s (+%d lines)" % (NAME, base, new.count("\n") - text.count("\n")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
