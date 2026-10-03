#!/usr/bin/env python3
"""Layer 9 item 9.12 (record l9stk, MESHSAT-1357, 3 October 2026): one stackup decision per board, for
v2/ecad/tools/pcb_decisions.yaml. DRAFT for the integrator: run it once, then python3 v2/ecad/tools/decisions_render.py.
The author ran --check only; the register is not edited by this record.

It appends seven decisions, numbered one above the register's highest at the time it runs (59 on the tree this record
started from, 37bc2f1d; a branch that adds one first moves the numbers, which is why they are not typed), in the order
A, B, C, D, E, P, E5. Each is the session's (authority SESSION) for the part this record decides, and names the owner's
ruling for any part the owner ruled (decision 27 for C's count, 28 and ruling 7 for P, ruling 7 for E5, 43 for B's
measurement and its price). Every decision carries the measurement that forced it, a bound derived by a stated method,
or the words NO MEASUREMENT HELD, in its `measurement` field (the P0 rule of 11 September 2026).

What a run checks before it writes: no decision already carries one of the seven marks "(L9STK <board>)" (a second run
is refused); decisions 27, 28 and 43, which these build on, are in the register; every new text passes int7's screen
(claims_check's CLAIM words, no long dash); the result parses and every existing decision reads back unchanged; each new
entry reads back as written with its authority fields; and, after the write, the file re-parses to the same data.

Usage: python3 apply_decisions_l9stk.py [--check] [--registry PATH]
  --check     compute and verify, write nothing
  --registry  operate on another copy of the register (the test uses a temporary copy)"""
import argparse
import os
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
DEC = os.path.join(TOP, "v2/ecad/tools/pcb_decisions.yaml")
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A  # noqa: E402

ASKED = "2026-10-03"
RULED_BY = "SESSION under the owner's standing rule of 26 September 2026"
RULING_BASIS = ("the owner's ruling of 21 September 2026 makes an engineering decision the session's unless it changes a "
                "reserved line or spends money AND more than one option stands after the measurement; the layer count and "
                "stackup are a reserved class of tools/reserved.json, so where two options still stand the owner's standing "
                "rule of 26 September 2026 has the session take the recommended one and record it, never one that spends "
                "money, orders, or changes what the kit is claimed to be")
OUT = "v2/docs/records/l9stk/l9stk_stackups.out"
PAGE = "v2/docs/records/l9stk/L9-STACKUPS.md"
HOLDS = ("it releases no rule-board pair: STK-002 on this board still needs the fabricator's price at the real outline "
         "and quantity five (EQ-14, the supplier's quotation), and STK-001 a board file on the named stack; the "
         "stackup is the design input handed to the supplier's layout phase (SUPPLIER-HANDOVER.md section 8, phase 3)")

DECISIONS = [
    dict(
        board="a", mark="(L9STK A)",
        title=("Board A's stackup: six layers on JLC06161H-3313 at 1 oz outer and 0.5 oz inner, the pack path and its "
               "return as generator-laid bands shared by both outer faces"),
        measurement_kind="MEASURED (the count); DERIVED BOUND (the copper weight); NO MEASUREMENT HELD (the per-face share and the 60 s transient)",
        measurement=(
            "MEASURED: the four-layer arm of 12 September 2026 (the same tools, router and settings as the six-layer A24, "
            "18 passes) ended 0 hard and 345 unrouted with its autoroute completed in 51 minutes, against 0 and 0 at six "
            "(v2/docs/LAYER-DECISIONS-2026-09-11.md). DERIVED BOUND (" + OUT + " section 2): at PWR-F12's 18 A the pack path "
            "needs 23.91 mm on one 1 oz face, 6.72 mm on each of two 1 oz faces, 11.95 mm on one 2 oz face, and 195.80 mm "
            "on a 0.5 oz inner layer; the pack return on In1 and In4 alone needs 55.05 mm of each at 0.5 oz, inside the "
            "board's 160 mm. NO MEASUREMENT HELD of the per-face share on a routed board or of the 60 s transient PWR-F12 "
            "names."),
        authority_why=(
            RULING_BASIS + ". Two options stand after the bound: 1 oz with the bands shared by both faces, and 2 oz. The "
            "one taken spends nothing (1 oz is the fabricator's base copper, JLC-7 of the record's price readings) and "
            "keeps the board's class table buildable; 2 oz would spend a surcharge no public page prints, move every 0.127 "
            "mm clearance to the stricter 2 oz floor of 0.16 mm (JLC-6), put U3's 0.4 mm pitch pads at the 0.20 mm 2 oz "
            "solder-mask bridge with no mask expansion left, and need a six-layer 2 oz row nobody has transcribed or solved."),
        outcome=(
            "BOARD A IS SIX LAYERS ON JLCPCB'S JLC06161H-3313, 1.6 MM: F.CU 0.035 MM SIGNALS AND GENERATOR-LAID POWER "
            "BANDS; 3313 PREPREG 0.0994 MM DK 4.1; IN1 0.0152 MM SOLID GND, NO TRACKS; CORE 0.55 MM DK 4.6; IN2 SIGNALS "
            "AND POURS; 2116 PREPREG 0.1088 MM DK 4.16; IN3 SIGNALS AND POURS (THE VIN_RAW DIVE UNDER THE VBAT TRUNK, A "
            "CROSSING ONLY); CORE 0.55 MM; IN4 0.0152 MM SOLID GND, NO TRACKS; 3313 PREPREG 0.0994 MM; B.CU 0.035 MM "
            "SIGNALS, BANDS AND THE UNDERSIDE THROUGH-HOLE PARTS. The pack path (CELL+, CELL_FUSED, VBAT) and its return "
            "run as generator-laid bands at least 6.72 mm wide on each of the two outer faces, tied at both ends of every "
            "transition by at least 21 barrels of 0.4 mm drill, or 23.91 mm on a face that carries it alone; VIN_RAW at "
            "14.1 A 4.43 mm on each of two faces or 15.29 mm on one; no inner layer is a conductor of the pack path. "
            "Controlled impedance: the USB2_CM5 ribbon pairs at 90 ohm on F.Cu and B.Cu only, 0.130 mm wide at a 0.127 mm "
            "gap (atlc 90.0 ohm; the class 0.127 / 0.13 mm reads 91.1); the RF drops 50 ohm single-ended on F.Cu at "
            "0.155 mm; no controlled pair on In2 or In3. Floors: 0.09 / 0.09 mm track and space (1 oz multilayer)."),
        reversed_by=(
            "reopen this decision and take JLCPCB's six-layer 2 oz outer stackup if dc_drop on the routed board reads a "
            "face of the pack path or its return over its width's rating, or the 60 s transient analysis or the supplier's "
            "floor plan refuses the two-face bands; that row is not in stackup_write.STACKS, so it is transcribed under its "
            "own decision, its USB geometry solved with layout-constraints/calc/stack_solves.py, the record re-run with "
            "python3 v2/docs/records/l9stk/l9stk_stackups.py, and its price goes to the owner before any order"),
        ask="1 oz outer with the pack path and its return shared by both outer faces, or 2 oz outer",
        recommendation=(
            "1 oz, shared by both faces: it spends nothing, keeps the class table and U3's solder-mask bridges, and the "
            "two-face bands take 6.72 mm each on a 160 mm board"),
        evidence=(
            "v2/docs/LAYER-DECISIONS-2026-09-11.md (the four-layer arm); " + OUT + " sections 2 to 4; " + PAGE + " section 3; "
            "v2/docs/STACKUP-DECISIONS.md section 3.1; v2/docs/layout-constraints/A.md sections 1 to 3; "
            "v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md (the 2 oz rows); the record's price readings JLC-6 and JLC-7"),
    ),
    dict(
        board="b", mark="(L9STK B)",
        title=("Board B's stackup: eight layers on JLC08161H-2116 as S G S G P S G S, 1 oz outer and 0.5 oz inner, the "
               "design input to layout, conditional on decision 43's route"),
        measurement_kind="MEASURED (six refused for the controlled pairs and the route); NO MEASUREMENT HELD (a whole-board route at eight)",
        measurement=(
            "MEASURED: a board-wide In1 keep-out left 93 opens at eight passes (5 September 2026): the three receptacles' "
            "0.4 mm escape needs two inner signal layers; B21 on six layers left 416 open after forty hours (decision 43's "
            "evidence); the region trial Q-B-ESC-1 (26 September 2026, EXPERIMENTAL, INCONCLUSIVE, v2/docs/B-FEASIBILITY.md "
            "7.8) read 33 open with four routing layers when its cap cut it and 18 with six routing layers on eight, 38 "
            "against 18 at matched routing time, its residue read as bounded by placement. atlc (" + OUT + " section 4): on "
            "six as built In2 needs 0.208 mm for 90 ohm, never reaches 85 at a 0.127 mm gap, and reads 140.5 ohm where In4 "
            "splits, while the outer layers need 0.130, so one class width cannot serve both; on eight, 0.148 / 0.127 mm "
            "reads 89.9 and 90.1 ohm and 0.112 / 0.127 mm reads 98.8 and 100.1 ohm on the outer and inner layers. NO "
            "MEASUREMENT HELD of a whole-board route at eight layers."),
        authority_why=(
            RULING_BASIS + ". After the measurements one option is not refused for the controlled pairs: six as built "
            "cannot hold one width per class and loses its inner reference where In4 splits; option A2 (In3 to ground) "
            "leaves three controlled routing layers where four left 416 open; S G S G S G G S puts the four 5 V domains as "
            "bands on routing layers, which board B's floor plan has no room for (B-FEASIBILITY.md section 3.3). Taking "
            "eight as the design input spends nothing now; owner decision 43 keeps the eight-layer price for him before any "
            "order and returns the decision to him if eight does not route, both unchanged here."),
        outcome=(
            "BOARD B'S DESIGN INPUT IS EIGHT LAYERS ON JLCPCB'S JLC08161H-2116, 1.5996 MM: F.CU 0.035 MM SIGNALS; 2116 "
            "0.1164 MM DK 4.16; IN1 GND; CORE 0.3 MM DK 4.41; IN2 SIGNALS; 2 X 1080 0.1528 MM DK 3.91; IN3 GND; CORE 0.3 "
            "MM; IN4 THE FOUR 5 V DOMAINS (+5V_DEV, +5V_S1, +5V_S2, +5V_S3, each region at least as wide as the record's "
            "0.5 oz figure for its current, 6.36 to 13.64 mm); 2 X 1080 0.1528 MM; IN5 SIGNALS; CORE 0.3 MM; IN6 GND; 2116 "
            "0.1164 MM; B.CU 0.035 MM SIGNALS. Inner copper 0.0152 mm (0.5 oz). Controlled impedance, one width per class "
            "on every routing layer: class USB 0.148 mm at a 0.127 mm gap (90 ohm for PCIE_CM5, USB3_CM5 and USB2_CM5, and "
            "within 10 percent of the M.2 module's 85 ohm), class DIFF100 0.112 mm at 0.127 mm (100 ohm for ETHERNET_CM5 "
            "and HDMI_CM5), 50 ohm single-ended 0.181 mm on the outer layers. A pair on In5 stays inside one 5 V region or "
            "carries a stitching capacitor where it crosses between two (RET-003). Floors: 0.09 / 0.09 mm, through vias "
            "only, via-in-pad filled and capped. The whole-board route at eight is decision 43's measurement and now the "
            "supplier's layout phase; if it does not close, decision 43 returns to the owner by its own text."),
        reversed_by=(
            "reopen this decision if the supplier's layout closes board B on six layers with every controlled pair inside "
            "its tolerance (the pairs on F.Cu and B.Cu, or on In2 and In3 at their own solved widths over a solid In4), or "
            "if the eight-layer route does not close; re-run python3 v2/docs/records/l9stk/l9stk_stackups.py on the stack "
            "taken and hand the decision to decision 43's owner path"),
        ask=("six layers as built (pairs on the outer layers only), six with In3 to ground (option A2), or eight layers as "
             "S G S G P S G S"),
        recommendation=(
            "eight layers as S G S G P S G S: the only layer use in the record with four controlled routing layers and one "
            "width per class, and the arm that read 18 open against 38 at matched routing time"),
        evidence=(
            "v2/docs/LAYER-DECISIONS-2026-09-11.md (93 opens); decision 43 (416 open); v2/docs/B-FEASIBILITY.md sections "
            "3.2, 3.3 and 7.8; v2/docs/STACKUP-DECISIONS.md section 4; v2/docs/layout-constraints/calc/stack_solves.out; "
            + OUT + " sections 2 and 4; " + PAGE + " section 4; v2/docs/layout-constraints/B.md sections 1 and 3"),
    ),
    dict(
        board="c", mark="(L9STK C)",
        title=("Board C's stackup under owner decision 27: JLC06161H-3313 with In1 and In4 as ground, 1 oz outer and 0.5 oz "
               "inner, and no impedance-controlled pair"),
        measurement_kind="MEASURED (the count, owner decision 27); DERIVED BOUND (the copper weight)",
        measurement=(
            "MEASURED (decision 27's evidence): C24's eighteen B.Cu nets fail RET-001 and RET-002 with only In2, a routing "
            "layer, beside them, the longest 172.9 mm of SCL; two routing layers left 14 to 35 open in the driver cluster "
            "(6 September 2026), the same two routing layers four layers with two planes would leave (INFERRED); the six-layer arm routed 0 and 0 in "
            "14.7 minutes (16 September 2026). DERIVED BOUND (" + OUT + " section 2): board C's largest rail is +5V at "
            "0.60 A, 0.15 mm on one 1 oz face; pcb_interfaces.yaml declares only USB_FULL_SPEED on board C, with no "
            "impedance target."),
        authority_why=(
            RULING_BASIS + ". The count and the layer use are the owner's (decision 27, which took option 1 of its record "
            "as written); this decision adds the copper weights and the statement that no pair is controlled, where one "
            "option stands: no rail asks more than 0.15 mm of 1 oz copper and no interface asks an impedance."),
        outcome=(
            "BOARD C IS SIX LAYERS ON JLCPCB'S JLC06161H-3313, 1.6 MM (OWNER DECISION 27): F.CU SIGNALS, IN1 SOLID GND, IN2 "
            "SIGNALS, IN3 SIGNALS, IN4 SOLID GND, B.CU SIGNALS, every signal layer beside a plane; the dielectrics of the "
            "row as for board A; 1 oz outer (0.035 mm) and 0.5 oz inner (0.0152 mm). No impedance-controlled pair: "
            "USB_PNL runs as a coupled pair over a plane for its return, not for an impedance. In2 and In3 are 0.1088 mm "
            "apart, so long runs on the two cross at right angles where they overlap. The board exceeds the fabricator's "
            "650 cm2 large board threshold (784.32 cm2), whose fee its public page does not print."),
        reversed_by=(
            "reopen decision 27 itself (regenerate board C on JLC04161H-7628); the copper and the impedance statement of "
            "this decision follow the count and are re-read with python3 v2/docs/records/l9stk/l9stk_stackups.py"),
        ask="the copper weights and whether any pair on board C is controlled",
        recommendation="1 oz outer, 0.5 oz inner, no controlled pair",
        evidence=(
            "decision 27; v2/docs/LAYER-DECISIONS-2026-09-11.md; v2/docs/STACKUP-DECISIONS.md section 3.3; "
            "v2/ecad/tools/pcb_interfaces.yaml (board c); " + OUT + " sections 1, 2 and 4; " + PAGE + " section 5; "
            "v2/docs/layout-constraints/C.md sections 1 to 3"),
    ),
    dict(
        board="d", mark="(L9STK D)",
        title=("Board D's stackup: four layers on JLC04161H-7628 with In1 ground and In2 a plane, 1 oz outer and 0.5 oz "
               "inner, the RF path 50 ohm on F.Cu at 0.332 mm"),
        measurement_kind="MEASURED (four with In2 as a plane routes); DERIVED BOUND (two layers refused by the required planes); NO MEASUREMENT HELD (a two-layer route)",
        measurement=(
            "MEASURED: the In2-as-plane arm routed 0 hard and 0 unrouted over three rounds (15 September 2026, decision "
            "27's D measurement), so two routing layers carry board D. NO MEASUREMENT HELD of a two-layer route of D. "
            "DERIVED BOUND by the required planes: RET-001 and RET-002 ask a reference plane beside every routing layer, "
            "and D routes on both faces (4,332 mm on its outer layers, LAYER-DECISIONS-2026-09-11.md), which a two-layer "
            "board cannot give; the RF path's 50 ohm line needs its ground 0.2104 mm under F.Cu to be 0.332 mm wide "
            "(atlc, stack_solves.out se-4L). Board D's largest rail is +5V_D8 at 1.0 A, 0.30 mm of 1 oz (" + OUT + ")."),
        authority_why=(
            RULING_BASIS + ". After the measurement and the bound one option stands, four layers with In2 a plane; it is "
            "the row board D's file already carries, so it spends nothing and changes no claim."),
        outcome=(
            "BOARD D IS FOUR LAYERS ON JLCPCB'S JLC04161H-7628, 1.6 MM: F.CU 0.035 MM SIGNALS AND THE RF PATH; 7628 "
            "PREPREG 0.2104 MM DK 4.4; IN1 0.0152 MM SOLID GND; CORE 1.065 MM DK 4.6; IN2 0.0152 MM A PLANE (GND AND THE "
            "+5V_D8 POUR, NO ROUTING BEYOND SHORT CROSSINGS); 7628 PREPREG 0.2104 MM; B.CU 0.035 MM SIGNALS. The RF path "
            "(RF_PAOUT, the low-pass filter, K1, RF_ANT, J_ANT) 50 ohm single-ended on F.Cu over In1 at 0.332 mm (the RF "
            "class 0.35 mm reads 48.5 ohm); USB at full speed carries no impedance target. Floors: 0.09 / 0.09 mm."),
        reversed_by=(
            "reopen this decision if a two-layer route of board D holds RET-001 and RET-002 and the RF line on its own "
            "plane; re-run python3 v2/docs/records/l9stk/l9stk_stackups.py on the stack taken"),
        ask="four layers with In2 a plane, or two layers",
        recommendation="four layers with In1 ground and In2 a plane",
        evidence=(
            "decision 27 (the D measurement); v2/docs/LAYER-DECISIONS-2026-09-11.md (the RF reason, the outer lengths); "
            "v2/docs/STACKUP-DECISIONS.md section 3.4; v2/docs/layout-constraints/calc/stack_solves.out (se-4L); "
            + OUT + " sections 2 and 4; " + PAGE + " section 6; v2/docs/layout-constraints/D.md sections 1 to 3"),
    ),
    dict(
        board="e", mark="(L9STK E)",
        title=("Board E's stackup: four layers on JLC04161H-7628 at 1 oz outer and 0.5 oz inner, the pack path, its return "
               "and VIN_RAW as generator-laid bands shared by both outer faces"),
        measurement_kind="MEASURED (the count and the power half refuted); DERIVED BOUND (the copper weight and the return); NO MEASUREMENT HELD (the per-face share)",
        measurement=(
            "MEASURED (v2/docs/LAYER-DECISIONS-2026-09-11.md): the routing half, a 267 mm strip whose open nets were "
            "end-to-end (USB_E6_P 196 mm, GEIGER_IN 214 mm) on two routing layers, and the LT8705A maker's checklist (a "
            "ground plane layer with no traces next to the FET layer, which In1 is, 0.2104 mm under F.Cu); the power half "
            "of the old argument refuted (In2's 5,500 mm2 of pour worth 13 and 28 mV on E7). DERIVED BOUND (" + OUT + " "
            "section 2): the pack path needs 23.91 mm on one 1 oz face or 6.72 mm on each of two; with VIN_RAW, TRK_OUT, the "
            "inlet chain, the solar input and the pack return side by side the bands take 78.72 mm on one 1 oz face, more "
            "than the 68 mm strip, and 23.44 mm on each of two faces (34 percent); the pack return on In1 alone would need "
            "195.80 mm at 0.5 oz and 85.03 mm at 1 oz, so it rides the outer bands at either inner weight. NO MEASUREMENT "
            "HELD of the per-face share on a routed board (on E7 B.Cu carried 97 percent of CELL_F once In2 was emptied, "
            "so an equal share is a layout duty, not a default)."),
        authority_why=(
            RULING_BASIS + ". Two options stand after the bound: 1 oz with the bands shared by both faces, and 2 oz "
            "(JLC04162H-7628, the row recorded for board P). The one taken spends nothing and keeps U10's 0.4 mm pitch "
            "solder-mask bridges and the 0.09 mm floor the routing half needs; 2 oz would spend a surcharge no public page "
            "prints, move the floor to 0.16 mm, and put U10's bridges at the 0.20 mm limit with no mask expansion left."),
        outcome=(
            "BOARD E IS FOUR LAYERS ON JLCPCB'S JLC04161H-7628, 1.6 MM: F.CU 0.035 MM SIGNALS AND BANDS; 7628 0.2104 MM DK "
            "4.4; IN1 0.0152 MM SOLID GND WITH NO TRACKS (the tracker maker's plane); CORE 1.065 MM DK 4.6; IN2 0.0152 MM "
            "POWER POURS (CELL_F, PV_P, TRK_OUT, VIN_RAW) AND A GND FILL, cut back from under the tracker's switch nodes; "
            "7628 0.2104 MM; B.CU 0.035 MM SIGNALS AND BANDS. The pack path (CELL+, CELL_F) and its return at least 6.72 mm "
            "on each outer face, VIN_RAW 4.43 mm, TRK_OUT 2.89 mm, the inlet chain 1.41 mm and the solar input 1.27 mm on "
            "each, tied at both ends of every transition by the record's barrel counts (21, 16, 12, 7 and 7 of 0.4 mm); "
            "In2's pours count only for the share dc_drop solves on them. No impedance target (USB at full speed); no RF "
            "line. Floors: 0.09 / 0.09 mm. The energy chain's 'board E's 2 oz power bands' (pcb_energy_chain.yaml "
            "DOCK_ENTRY) contradicts this and is its writer's to correct."),
        reversed_by=(
            "reopen this decision and take JLC04162H-7628 (2 oz outer) if dc_drop on the routed strip reads a face of the "
            "pack path, its return or VIN_RAW over its width's rating, or the supplier's floor plan cannot lay the two-face "
            "bands; check U10's footprint against the 0.20 mm 2 oz bridge first, re-run python3 "
            "v2/docs/records/l9stk/l9stk_stackups.py, and the 2 oz price goes to the owner before any order"),
        ask="1 oz outer with the high-current bands shared by both faces, or 2 oz outer",
        recommendation=(
            "1 oz, shared by both faces: it spends nothing and keeps the routing floor and U10's bridges; the two-face bands "
            "take about a third of the strip where every conductor crosses one section, under half"),
        evidence=(
            "v2/docs/LAYER-DECISIONS-2026-09-11.md (the routing half, the E experiment); v2/docs/STACKUP-DECISIONS.md "
            "section 3.5 and section 6 item 5; v2/vendor/power/lt8705a.pdf p.35; " + OUT + " sections 2 and 3; " + PAGE +
            " section 7; v2/docs/layout-constraints/E.md sections 1 to 3; the record's price readings JLC-6 and JLC-7"),
    ),
    dict(
        board="p", mark="(L9STK P)",
        title=("Board P's stackup under owner decision 28 and ruling 7: JLC04162H-7628, 2 oz outer, and 0.5 oz inner with "
               "In1 and In2 kept at least 16 mm wide beside the pack return"),
        measurement_kind="MEASURED (the count, owner decision 28); DERIVED BOUND (the inner copper weight); NO MEASUREMENT HELD (the solved share on a routed four-layer P)",
        measurement=(
            "MEASURED (decision 28's evidence): two layers left 43, 45 and 47 open at the fabricator's 0.16 mm floor, four "
            "layers 0 and 0 (P8, 18 September 2026). DERIVED BOUND (" + OUT + " section 2, plane_share): with the outer 2 oz "
            "bands at their two-face minimum of 3.36 mm, the two inner GND planes beside the pack return take a share by "
            "cross-section; at 0.5 oz a plane is over its rating only when necked to 2.80 to 15.45 mm beside the run, and "
            "at the board's own 42 mm a plane carries 6.58 A against 7.76 A. NO MEASUREMENT HELD of the share dc_drop "
            "solves on a routed four-layer P (the model neglects crowding at the via fields)."),
        authority_why=(
            RULING_BASIS + ". The count and the 2 oz outer copper are the owner's (decision 28, ruling 7). Two inner "
            "weights stand after the bound (0.5 oz with a plane width kept, or 1 oz); the one taken is the row already "
            "recorded under decision 28, spends nothing beyond it, and asks only a layout constraint; 1 oz inner "
            "(JLC041621-7628) is a surcharge no public page prints."),
        outcome=(
            "BOARD P IS FOUR LAYERS ON JLCPCB'S JLC04162H-7628, 1.6562 MM (OWNER DECISION 28 AND RULING 7): F.CU 0.070 MM "
            "SIGNALS AND PACK BANDS; 7628 0.2104 MM DK 4.4; IN1 0.0152 MM GND; CORE 1.065 MM DK 4.38; IN2 0.0152 MM GND; 7628 "
            "0.2104 MM; B.CU 0.070 MM SIGNALS AND PACK BANDS. Inner copper 0.5 oz, on a layout constraint: wherever In1 and "
            "In2 run beside the pack return between R10 and the cell block lead, each stays at least 16 mm wide (no neck "
            "into the 2.80 to 15.45 mm band), and the planes' share is tied in by at least 15 barrels of 0.4 mm at each "
            "end. Pack bands 3.36 mm on each face or 11.95 mm on one. Floors at 2 oz: 0.16 mm track and space (the "
            "stricter of the fabricator's two printed figures, 0.15 and 0.16), 0.20 mm solder-mask bridge; U1's 0.4 mm "
            "pitch pads leave exactly 0.20 mm of copper gap, so their bridges hold only with no mask expansion, which the "
            "supplier confirms with the fabricator or accepts as a gang opening. No impedance target (SMBus)."),
        reversed_by=(
            "take JLC041621-7628 (1 oz inner) under its own decision, with its price to the owner, if dc_drop on the routed "
            "four-layer P with GND declared as the return of PACK_P reads an inner plane over its rating, or the layout "
            "cannot keep the 16 mm; re-run python3 v2/docs/records/l9stk/l9stk_stackups.py"),
        ask="0.5 oz inner with the planes kept wide beside the pack return, or 1 oz inner",
        recommendation="0.5 oz inner, the row decision 28 recorded, with In1 and In2 at least 16 mm wide beside the return",
        evidence=(
            "decision 28; v2/docs/STACKUP-DECISIONS.md section 3.6; v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md (the "
            "four-layer 2 oz codes and the 2 oz rows); " + OUT + " sections 2 and 3; " + PAGE + " section 8; "
            "v2/docs/layout-constraints/P.md sections 1 and 2; the record's price reading JLC-6"),
    ),
    dict(
        board="e5", mark="(L9STK E5)",
        title=("Board E5's stackup under owner ruling 7: two layers at 2 oz on the 2L-2oz row, Dk 4.5, both faces carrying "
               "the pack contacts' lands"),
        measurement_kind="DERIVED BOUND (two layers is the least a plated board gives); NO MEASUREMENT HELD (no route; none is needed)",
        measurement=(
            "NO MEASUREMENT HELD of a route: board E5 carries no signal routing (112 mm of copper, contact targets and wire "
            "lands, LAYER-DECISIONS-2026-09-11.md), so no route can force or free a layer. DERIVED BOUND: its plated "
            "contact targets and the wire lands beneath them need copper on both faces joined through plated holes, which "
            "no board under two layers gives; at the dock block's 18 A (pcb_energy_chain.yaml DOCK_BLOCK and PWR-F12) "
            "CELL+ and CELL_N each need 11.95 mm on one 2 oz face or 3.36 mm on each of two (" + OUT + " section 2)."),
        authority_why=(
            RULING_BASIS + ". The two layers and the 2 oz copper are the owner's (ruling 7); this decision adds the row's "
            "dielectric constant and the band widths, where one option stands (the fabricator prints 4.5 for a two-layer "
            "board, v2/vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md)."),
        outcome=(
            "BOARD E5 IS TWO LAYERS ON THE 2L-2OZ ROW: F.CU 0.070 MM, FR-4 CORE 1.44 MM DK 4.5, B.CU 0.070 MM. CELL+ and "
            "CELL_N each 3.36 mm on both faces or 11.95 mm on one, tied by at least 21 barrels of 0.4 mm drill (18 of 0.5 "
            "mm) where a face changes. Floors at 2 oz: 0.16 mm track and space, 0.20 mm solder-mask bridge, 0.254 mm PTH "
            "annular ring. The board file's Dk 4.6 is STK-001's residue and closes with its next re-cut. No impedance target."),
        reversed_by=(
            "reopen ruling 7 for board E5 only on a new owner ruling; the dielectric and the widths of this decision are "
            "re-read with python3 v2/docs/records/l9stk/l9stk_stackups.py"),
        ask="the dielectric constant and the band widths of the ruled two-layer 2 oz board",
        recommendation="Dk 4.5 as the fabricator prints it for two layers; 3.36 mm on each face or 11.95 mm on one",
        evidence=(
            "ruling 7 (OWNER-DECISIONS-2026-09-11.md decision 7); v2/docs/STACKUP-DECISIONS.md section 3.7; "
            "v2/ecad/tools/boards/e5.json _stackup_dk_why; " + OUT + " section 2; " + PAGE + " section 9; "
            "v2/docs/layout-constraints/E5.md sections 1 and 2"),
    ),
]
NEEDED = {27: "board C's count", 28: "board P's count", 43: "board B's measurement and price"}


def refuse(m):
    print("apply_decisions_l9stk: REFUSED: %s" % m)
    sys.exit(2)


def block(n, d):
    def f(key, text):
        return "    %s: >-\n%s" % (key, A.fold(text, 6, 120))
    return ("  - n: %d\n" % n + f("title", d["title"] + " " + d["mark"]) + "    asked: %s\n    status: ruled\n    authority: SESSION\n" % ASKED
            + f("authority_why", d["authority_why"]) + f("ruled_by", RULED_BY) + "    ruled_on: %s\n" % ASKED
            + f("outcome", d["outcome"]) + f("reversed_by", d["reversed_by"]) + f("ask", d["ask"])
            + f("recommendation", d["recommendation"]) + f("measurement", d["measurement"]) + f("evidence", d["evidence"])
            + "    blocks: {}\n" + f("holds_nothing_today", HOLDS))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--registry", default=DEC)
    a = ap.parse_args(argv)
    path = a.registry
    t = open(path, encoding="utf-8").read()
    d = yaml.safe_load(t)
    have = [x for x in d["decisions"] if any(D["mark"] in str(x.get("title", "")) for D in DECISIONS)]
    if have:
        refuse("the register already carries %d of this record's marks (a second run)" % len(have))
    ns = {int(x["n"]) for x in d["decisions"]}
    for n, why in NEEDED.items():
        if n not in ns:
            refuse("decision %d (%s), which this record builds on, is not in the register" % (n, why))
    if [D["board"] for D in DECISIONS] != ["a", "b", "c", "d", "e", "p", "e5"]:
        refuse("the decisions are not one per board in the order A, B, C, D, E, P, E5")
    for D in DECISIONS:
        for key in ("title", "authority_why", "outcome", "reversed_by", "ask", "recommendation", "measurement", "evidence"):
            A.screen(D[key], "board %s's %s" % (D["board"].upper(), key))
        if not any(w in D["measurement"] for w in ("MEASURED:", "MEASURED (", "DERIVED BOUND", "NO MEASUREMENT HELD")):
            refuse("board %s's decision names no measurement and does not say none is held" % D["board"].upper())
        if ".py" not in D["reversed_by"]:
            refuse("board %s's way back names no script" % D["board"].upper())
    A.screen(HOLDS, "holds_nothing_today")
    A.screen(RULED_BY, "ruled_by")
    if not t.endswith("\n"):
        refuse("the register does not end with a newline")
    n0 = max(ns) + 1
    out = t + "".join(block(n0 + i, D) for i, D in enumerate(DECISIONS))
    after = yaml.safe_load(out)
    if after["decisions"][:len(d["decisions"])] != d["decisions"]:
        refuse("an existing decision moved")
    new = after["decisions"][len(d["decisions"]):]
    if len(new) != len(DECISIONS):
        refuse("%d entries read back where %d were written" % (len(new), len(DECISIONS)))
    for i, (e, D) in enumerate(zip(new, DECISIONS)):
        for k, v in (("n", n0 + i), ("status", "ruled"), ("authority", "SESSION"), ("ruled_by", RULED_BY), ("blocks", {}),
                     ("title", D["title"] + " " + D["mark"]), ("outcome", D["outcome"]), ("measurement", D["measurement"])):
            if e.get(k) != v:
                refuse("board %s's entry reads back %s as %r" % (D["board"].upper(), k, e.get(k)))
        for k in ("authority_why", "reversed_by", "outcome", "ask", "recommendation", "evidence", "holds_nothing_today", "measurement"):
            if len(str(e.get(k) or "")) < 30:
                refuse("board %s's %s is short" % (D["board"].upper(), k))
    print("apply_decisions_l9stk: decisions %d to %d appended, one per board (A, B, C, D, E, P, E5); %d decisions to %d; nothing else moved" % (
        n0, n0 + len(DECISIONS) - 1, len(d["decisions"]), len(after["decisions"])))
    if a.check:
        print("CHECK ONLY: %s not written. Next after the write: python3 v2/ecad/tools/decisions_render.py" % os.path.relpath(path, TOP) if path.startswith(TOP) else "CHECK ONLY: not written")
        return 0
    open(path, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(path, encoding="utf-8").read()) != after:
        refuse("re-parse differs")
    print("APPLIED: decisions %d to %d in %s. Next: python3 v2/ecad/tools/decisions_render.py" % (n0, n0 + len(DECISIONS) - 1, path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
