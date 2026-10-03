#!/usr/bin/env python3
"""apply_l5r2.py: Layer 5's second round written into its two contract files (MESHSAT-1357, 3 October 2026; the Layer 5 author owns
both, so this script was RUN ONCE on the tree by that author and is kept beside the record as the exact statement of the change; a
second run refuses).

What it writes (L5-INTERFACES-R2.md gives every field's source, mark and trigger):
  pcb_interfaces.yaml   (1) the pass-2 fields (current, default_state, harness, hot_plug, judged_by, levels, mating, sequencing, tbd
                        and a `part` on every connector end) for the eight first-twelve contracts that lacked them: IF-BC-PANEL,
                        IF-AB-RIBBON, IF-AB-WALL, IF-AD-HARNESS, IF-AC-MAINSW, IF-AE-RF, IF-A-PA, IF-LID-HF. Each is a block replaced
                        whole; the content under the older keys (cable, power, power_lead, note, map_identity.judged_by) MOVES into
                        the field, and the script refuses if any string or number of the old block is not found in the new one (no
                        loss). IF-AE-DOCK's E5 end gains its part, ref and src. (2) The fans after Layer 7's D-18 and L4-E11
                        section 18 (b929d8be): IF-E-FANS and IF-B-FANS restated, IF-AE-DOCK's pin1_vsys_dock and two power lines
                        extended, a power line for U22's RUN added. (3) Record l8gnd (226e9143): SLOT_EN1..3's line restated with the
                        keeper's hold and cable-out state; IF-BC-PANEL and IF-AB-RIBBON per its 3g; GND-002's interface text on
                        IF-EXT-ETH, IF-EXT-DC and IF-AE-DOCK and a new contract IF-A-CHASSIS (the one bond). The `pins` maps are not
                        touched; every anchor of L4-E11's apply_pcb_interfaces_dock.py still occurs once (asserted).
  HW-FW-CONTRACT.md     FW-C02 and V-C02 (l8gnd 3f, 3h), FW-C01's step 6, FW-C14's start-up read and section 9's open item (3f);
                        FW-E07 and FW-E11 (L4-E11 section 18; FW-E11's ILIM resistor named R228 after L4-E11's 787e7b15); two rows
                        in section 4.1; the version paragraph; the change record.

Usage:  apply_l5r2.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (a block or an anchor is not the expected text, the change is already applied, a leaf of an
old block is lost, the result does not re-parse, or a dash character)."""
import difflib
import os
import re
import sys

NAME = "apply_l5r2"
L8 = "record l8gnd at 226e9143 (`v2/docs/records/l5r2/inputs/l8gnd-sections-2-3-226e9143.md`)"
E18 = "L4-E11 section 18 at b929d8be (`v2/docs/records/l5r2/inputs/l4e11-section-18-b929d8be.md`)"


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


# ====================================================================================================== the eight contracts
NEW_BLOCKS = {}
NEW_BLOCKS["IF-BC-PANEL"] = '''\
    IF-BC-PANEL:
      title: "panel ribbon, board B J_PANEL to board C J_PANEL"
      kind: board_to_board
      ends:
        - {board: b, ref: J_PANEL, part: "IDC 2x13 2.54 mm box header: Wurth WR-BHD 61202621621 (session pick HC6-SC-7, JLCPCB
           C17586777; 3 A per contact at 25 C, -40 to +105 C, 30 mating cycles; land meshsat:IDC-Header_2x13_P2.54mm_Vertical_NarrowPad,
           B netlist)", src: "v2/ecad/tools/gen_sch_b.py:1061-1063"}
        - {board: c, ref: J_PANEL, part: "IDC 2x13 SMD box header, underside: XFCN BH254VS-26P (session pick HC6-SC-7, C48687640, no
           maker sheet read; land Connector_IDC:IDC-Header_2x13_P2.54mm_Vertical_SMD, C netlist)", src: "v2/ecad/tools/gen_sch_c.py:99-101"}
      harness: {what: "26-way 1.27 mm flat ribbon, IDC both ends, 350 mm", src: "v2/docs/ASSEMBLY.md section 4, panel ribbon row",
              rating: "as first written: TBD: no ribbon or IDC contact datasheet is held; effect: the PANEL_5V fault-current check below
                cannot close. Since HC6-SC-7 (v2/docs/parts/PROCUREMENT.md section 5) the sheets are held: sockets Wurth WR-BHD
                61202623021 (1 A per contact max, -40 to +105 C, 30 mating cycles) on flat cable WR-CAB 63912615521CAB (1.27 mm, 28 AWG,
                1 A per conductor max, -25 to +105 C, 300 V RMS); the check is current.per_conductor"}
      aliases: [["PANEL_5V", "+5V"]]
      map_identity: {status: VERIFIED}
      judged_by: "check_contracts.py section 1 (the J_PANEL map); the lines of the inhibit group it carries by sections 2 and 12 to
        15 (inhibit_chain_<letter>)"
      pins: {1: PANEL_5V, 2: PANEL_5V, 3: GND, 4: SDA, 5: SCL, 6: EXP_INT, 7: TR_APRS, 8: EMCON_HW, 9: GND,
             10: ZEROIZE_HW, 11: TX_INHIBIT_n, 12: HDMI_SEL1, 13: HDMI_SEL2, 14: GND, 15: USB_PNL_P, 16: USB_PNL_N, 17: GND,
             18: HB1, 19: HB2, 20: HB3, 21: SLOT_EN1, 22: SLOT_EN2, 23: SLOT_EN3, 24: PI_SHDN_REQ, 25: PI_KILL,
             26: SHORE_INHIBIT}
      current:
        PANEL_5V: {rail: PANEL_5V, from: "+5V_DEV through B's F1, 2.0 A hold polyfuse (as first written; since b76c18cb F1 is the
                Bourns MF-MSMF110-2, 1.1 A hold: see protection)", declared_a: 0.60,
              src: "gen_sch_b.py:1053-1060", note: "the panel's only supply; +5V_DEV starts by design since 458b2873 (R42 on A)"}
        per_conductor: "PANEL_5V on pins 1 and 2: 0.60 A declared is 0.30 A a conductor, 30 percent of the cable's and the socket's
          1 A (MAKER, WR-CAB 63912615521CAB and WR-BHD 61202623021); F1 holds 1.10 A (0.55 A a conductor) and trips at 2.20 A at 23 C
          (Bourns MF-MSMF sheet, every MF-MSMF110 variant), so a fault between 2.0 and 2.2 A may sit on the ribbon at up to 1.1 A a
          conductor, 10 percent over the 1 A, until F1 trips (INFERRED): see tbd; the returns on GND pins 3, 9, 14 and 17"
        signals: "the control lines, the kit I2C (at most 3 mA a line, the weakest sinks' rating: HW-FW-CONTRACT.md section 6.2), the
          USB pair and HB1..3 at logic currents"
      protection: "NOT COORDINATED on board B (B_PANEL_5V, ARCHITECTURE.md sections 4.5 and 13.2): F1 holds 2.0 A and
                trips at 3.5 A, and B21's 0.4 mm PWR-class PANEL_5V track is rated 1.23 A at 10 K, so the copper is the weaker
                element. Rule PWR-003 reads FAIL on board B (energy_chain_b; pcb_energy_chain.yaml stage B_PANEL_5V and its
                known finding, :217-245, :306-313), and a re-run on the corrected netlists repeats it (F1 is unchanged,
                gen_sch_b.py:1053). Closes on B's next placement and route with the 0.8 mm PANEL class of gen_pcb_b3.py:563-567
                (2.03 A at 10 K), or with an MF-MSMF110 (1.1 A hold, 2.2 A trip) in F1's place. As first written; since b76c18cb
                F1 IS the MF-MSMF110 (B19 netlist: '1.1A hold 1812 (Bourns MF-MSMF110-2)'), Ihold 1.10 A and Itrip 2.20 A at 23 C,
                and PWR-003 reads PASS on board B (v2/docs/handover/LAYER-STATUS.md 5.5)"
      levels: "PANEL_5V a 5 V class rail (+5V_DEV at 5.0 V from board A's LM5176 stage, A intent; board C budgets 5 percent on its
        +5V, C intent); the control lines at 3.3 V CMOS (the panel controller's IOVDD from board C's TLV75533 U5; the pulls on A
        to A's +3V3 and on B to +3V3_DEV, cable_out_states); the kit I2C at 3.3 V with 2.2 k pull-ups on B and C (bus);
        USB_PNL at USB full speed (the RP2040; pcb_interfaces.yaml USB_FULL_SPEED on board C); HB1..3 from each module's 3.3 V
        through board B's level stages (HW-FW-CONTRACT.md section 2)"
      default_state: "the lines the panel drives (SLOT_EN1..3, PI_KILL, PI_SHDN_REQ's release, SHORE_INHIBIT, HDMI_SEL1..2) sit at
        their pulls until the panel's firmware drives them (FW-C01); the lines the toggles make (EMCON_HW, TX_INHIBIT_n,
        ZEROIZE_HW) follow the toggles in hardware once board C's 3.3 V is up and sit at their pulls until then; every pull is on
        board A or B, so the states are cable_out_states' whether the ribbon is in or out; PANEL_5V is up whenever +5V_DEV is (R42
        on A); SLOT_EN's hold across a panel reset: slot_power_semantics"
      sequencing: "PANEL_5V from +5V_DEV, ON by design at power-up (R42 on A), so the panel boots with board A's main rail after a
        MAIN press (IF-AC-MAINSW); the panel then runs FW-C01's order: PI_KILL low, PI_SHDN_REQ released, ZEROIZE_SW read, the
        expanders' outputs before their configuration, the charger, SLOT_EN1..3 one at a time; HB1..3 toggle once each module's
        bridge runs (FW-B01); with the hold applied the panel first reads and adopts each SLOT_EN's held level (FW-C02)"
      mating: "IDC sockets Wurth WR-BHD 61202623021 crimped on WR-CAB 63912615521CAB into the box headers at both ends (HC6-SC-7; 30
        mating cycles each); mated and unmated with the kit off (hot_plug)"
      bus: "the kit I2C bus: C's RP2040 (GPIO0/1) is its ONLY master; pull-ups 2.2k on B (R54, R55, gen_sch_b.py:1044) and
        on C; every target and its address, read from the netlists' straps: v2/docs/ARCHITECTURE.md section 5.5. The three
        supervisors are I2C targets on I2C1 since 458b2873, and the TPS23861 (B U5, A3 unconnected) answers the broadcast
        address 0x30: the supervisors take 0x34 to 0x36 (I3-F01, the session's choice, firmware only). Speed, pull-ups and
        the capacitance budget: v2/docs/HW-FW-CONTRACT.md section 6. Standard-mode, 100 kHz programmed (SC-HF-03); as one
        segment the bus cannot meet the 300 ns rise its BQ25731, TPS23861 and ATECC608B require (HF-F01), so the session took
        three segments behind two TCA9517A (SC-HF-02), owed on boards A and B"
      cable_out_states:   # VERIFIED from the pulls cited; what each far board sees with the ribbon out
        EMCON_HW: "LOW, EMCON asserted (A R102 10k 1% since board A's round 8 candidate, 100k before; B R58 10k to GND;
          gen_sch_a.py:1253, gen_sch_b.py:1024); the hold with the source gone is UNDECIDED as drawn on B (feasibility/EMCON.md
          L2: remedy R58 4.7k 1% with single gates); on A alone it holds at 12 mV against A's two SN74AUP1G08 inputs (EMCON.md
          section 4a)"
        TX_INHIBIT_n: "LOW, transmit inhibited (A R145, B R59, D R2, 100k to GND)"
        ZEROIZE_HW: "HIGH, no wipe (A R117 10k to A's +3V3, gen_sch_a.py:1292); nothing acts on this line since faf8c981: C
          reads its own ZEROIZE_SW and U12 drives a buffered copy here (gen_sch_c.py:168-178)"
        SLOT_EN1..3: "as generated LOW, every compute slot OFF (A R30, R34, R38, 100k to GND; gen_sch_a.py:916-917, :956); with the
          hold applied (record l8gnd at 226e9143, DRAFTED, not applied; PROVISIONAL until its release) the LAST DRIVEN LEVEL, kept
          by A's U43 while A's +3V3 is up (held high at least 2.547 V, held low at most 0.266 V, the worst cases of l8gnd 3b), LOW
          from a power-up; the ribbons are mated with the kit off (SC-61) and MAIN stops the kit without them"
        SHORE_INHIBIT: "LOW, shore and vehicle inputs allowed (A R118, E R26)"
        PI_KILL: "LOW, no kill (A R5 1k, gen_sch_a.py:273; three back-driving slots stay under Q1's threshold, INFERRED)"
        PI_SHDN_REQ: "HIGH, no request (A R3 10k to A's +3V3, gen_sch_a.py:271; open-drain drivers only, by contract FW-A10)"
        HDMI_SEL1..2: "LOW nominally (B R15, R16 100k, gen_sch_b.py:903); not a guaranteed low at the switch's input current
          (feasibility/FAILOVER-FABRIC.md FAB-04: remedy 10k)"
        HB1..3: "HIGH on B (10k to +3V3_DEV per slot, FAILOVER-FABRIC.md section 4.9): a dark module reads as a held-high
          line, so liveness is the 1 Hz toggle; no pull on C"
      zeroize_semantics: "owner ruling D-03 (decision 30): a crypto-erase through the secure element; the ONLY wipe trigger is
        the covered toggle held 5 s, read on the local net ZEROIZE_SW by the panel controller's GPIO22 (gen_sch_c.py:217,
        :126-127); LEVEL-SENSITIVE after power loss (read at boot before any slot powers). ZEROIZE_HW on this ribbon is a
        buffered copy for test points; no board acts on it. Design: v2/docs/feasibility/ZEROIZE.md (blocker FB-ZER-1)"
      slot_power_semantics: "the panel is the only path to slot power, by D-03's boot order; SLOT_EN powers up OFF. OWED
        (the session's choice, ARCHITECTURE.md section 4.3): SLOT_EN holds its state across a panel reset (for example a
        latch the panel sets and clears), so a panel reset or update no longer drops the running slots; in no generator.
        DRAFTED since 3 October 2026 by record l8gnd at 226e9143 (its section 3g), not applied, PROVISIONAL until its release:
        keepers U43 (SN74LVC08A, one gate a line) with R230 to R232 (4.7 k) on board A keep each line at its last driven level
        while the panel's pad is in its reset state (R30, R34, R38 and the pad pull-downs stay), so a panel reset or in-system
        update no longer drops the running slots; the panel reads each line at boot before driving it (FW-C02); the hold vanishes
        with A's +3V3 (PI_KILL, the hot stop's H2) and with a loss of the panel's own supply (l8gnd 3d)"
      emcon_semantics: "owner ruling D-05: radios dark. Since 458b2873 EMCON_HW gates the three CM5 radios through open drains
        and removes the two WiFi cards' supplies (via Q11 and EMCON_ON on B). The per-transmitter table and what is open
        (L1 to L4, L7, SD-EMC-1 for the 5G module, SD-EMC-2 back-feed) is v2/docs/feasibility/EMCON.md (blocker FB-EMC)"
      hot_plug: "not hot-pluggable (the session's choice SC-HF-04 of 27 September 2026 under the owner's standing rule, v2/docs/HW-FW-CONTRACT.md section 8): mate and unmate with the kit off; PANEL.md section 7 already forbids
        switching the panel's 3.3 V with the ribbon attached"
      back_power: "INFERRED risk: EXP_INT (A R110, B R56) and PI_SHDN_REQ (A R3) are pulled to rails that can be up while C
        is unpowered; up to about 0.33 mA per line into an unpowered RP2040 pad (IOVDD + 0.5 V allowed, RP2040 Table 622).
        ZEROIZE_HW no longer back-feeds C: U12's Ioff disables its output with C unpowered (faf8c981)"
      not_judged: ["pull state of SLOT_EN, ZEROIZE_HW and SHORE_INHIBIT", "back-power", "PANEL_5V conductor current in the cable",
                   "which radios EMCON_HW actually reaches (RF-002 judges the line, not every transmitter)"]
      tbd: ["the ribbon's and the socket's capability above their 1 A maximum for F1's time to trip between 2.0 and 2.2 A (Wurth prints
            a maximum at laboratory conditions only); effect: a PANEL_5V fault in that band is not shown to stay inside the cable's
            rating (current.per_conductor)",
            "board C's XFCN BH254VS-26P: no maker sheet read (HC6-SC-7 names it the weakest pick); effect: its contact rating,
            temperature range and land are not shown",
            "the SLOT_EN hold (record l8gnd's keeper U43): DRAFTED, not applied; effect: until applied a panel reset drops every
            module (slot_power_semantics)"]
      findings: [W5-F4, I3-F01, FAB-04, EMCON-L1, EMCON-L2, B_PANEL_5V, HF-F01, L8G-F13]
      serves: [NEED-03, NEED-04, NEED-08, NEED-10, NEED-19]

'''
NEW_BLOCKS["IF-AB-RIBBON"] = '''\
    IF-AB-RIBBON:
      title: "A to B control ribbon, A J_AB1 (top) to B J_AB1 (underside), same case XY"
      kind: board_to_board
      ends:
        - {board: a, ref: J_AB1, part: "IDC 2x13, top side: Wurth WR-BHD 61202621621 (session pick HC6-SC-7, JLCPCB C17586777; 3 A per
           contact, -40 to +105 C), land meshsat:IDC-Header_2x13_P2.54mm_Vertical_NarrowPad (A netlist)", src: "v2/ecad/tools/gen_sch_a.py:1285-1287"}
        - {board: b, ref: J_AB1, part: "IDC 2x13, underside: Wurth WR-BHD 61202621621 (HC6-SC-7), the same land (B netlist)", src: "v2/ecad/tools/gen_sch_b.py:1077-1079"}
      harness: {what: "26-way 1.27 mm flat ribbon, 80 mm, folded once", src: "v2/docs/ASSEMBLY.md section 4, A to B ribbon row",
              parts: "sockets Wurth WR-BHD 61202623021 (1 A per contact max, 30 mating cycles) on WR-CAB 63912615521CAB (1.27 mm, 28 AWG,
                1 A per conductor max) (HC6-SC-7)"}
      map_identity: {status: VERIFIED}
      judged_by: "check_contracts.py section 7 (the J_AB1 map); the shutdown pair by section 6, the D8 USB pair by section 9, the
        inhibit lines by sections 12 to 15"
      pins: {1: USB_D8_P, 2: USB_D8_N, 3: GND, 4: GND, 5: GND, 6: GND, 7: GND, 8: GND, 9: PI_SHDN_REQ, 10: PI_KILL,
             11: SDA, 12: SCL, 13: EXP_INT, 14: TR_APRS, 15: EMCON_HW, 16: TX_INHIBIT_n, 17: SLOT_EN1, 18: SLOT_EN2,
             19: SLOT_EN3, 20: ZEROIZE_HW, 21: SHORE_INHIBIT, 22: GND, 23: GND, 24: GND, 25: USB_E6_P, 26: USB_E6_N}
      usb: "USB_D8 is B bank 3 hub port 1 to board D's TUSB2046I (full speed); USB_E6 is B bank 3 hub port 2 to board E's
        RP2040 through A and the dock (gen_sch_b.py:764-766); each pair on an END row"
      levels: "the control lines at 3.3 V CMOS as IF-BC-PANEL (the pulls on board A to A's +3V3); the kit I2C at 3.3 V (IF-BC-PANEL's
        bus; SEG-A's buffer U_A sits at J_AB1 under SC-HF-02, owed on board A); USB_D8 and USB_E6 at USB full speed (usb;
        USB_FULL_SPEED on boards D and E)"
      current: "no power crosses it (hot_plug): the nine GND pins carry the signals' returns; the control lines and the kit I2C at
        logic currents (at most 3 mA a line on the kit bus, HW-FW-CONTRACT.md section 6.2); the two USB pairs signal only, each
        hub's VBUS on its own board"
      default_state: "every control line at its pull on board A until the panel drives it (cable_out_states; IF-BC-PANEL
        default_state); the USB pairs idle until their hub ports enumerate"
      sequencing: "the lines follow IF-BC-PANEL's sequencing (the panel drives them through board B); USB_D8 enumerates when bank 3's
        host module boots and board D's +5V_D8 is up (D8_EN, IF-AD-HARNESS); USB_E6 when bank 3's host boots and board E's
        controller runs on its own feed"
      mating: "IDC sockets into the box headers at both ends, the ribbon folded once over 80 mm (harness); mated with the kit off
        (hot_plug)"
      cable_out_states: "as IF-BC-PANEL for every control line: the pulls sit on board A (VERIFIED). TR_APRS also feeds A's
        outlet interlock (U30); R116 holds it low with the ribbon out, so the outlets are not dropped. SLOT_EN1..3 with the hold
        applied (record l8gnd at 226e9143, DRAFTED, not applied; PROVISIONAL until its release): the LAST DRIVEN LEVEL, kept by A's
        U43 while A's +3V3 is up, LOW from a power-up (IF-BC-PANEL cable_out_states)"
      hot_plug: "not hot-pluggable (the session's choice SC-HF-04 of 27 September 2026 under the owner's standing rule, v2/docs/HW-FW-CONTRACT.md section 8): no power crosses it, but a partly seated ribbon can assert PI_KILL or drop SLOT_EN;
        with the hold applied (record l8gnd, DRAFTED) it no longer drops SLOT_EN: the lines keep their last level and MAIN still
        stops the kit (IF-AC-MAINSW)"
      tbd: ["SEG-A's buffer U_A at J_AB1 (SC-HF-02, owed on board A); effect: the kit bus's rise time over this ribbon stays HF-F01's
            until it is drawn",
            "the SLOT_EN hold (record l8gnd), DRAFTED, not applied; effect: as IF-BC-PANEL's"]
      findings: [W5-F4, EMCON-L2, L8G-F13]
      serves: [NEED-03, NEED-08]

'''
NEW_BLOCKS["IF-AB-WALL"] = '''\
    IF-AB-WALL:
      title: "A to B wall-port ribbon, A J_AB2 to B J_AB2, then A's lead to the sealed Glenair 233-370"
      kind: board_to_board
      ends:
        - {board: a, ref: J_AB2, part: "IDC 2x5 vertical box header: Wurth WR-BHD 61201021621 (session pick HC6-SC-7, JLCPCB C4355000;
           3 A per contact, -40 to +105 C), land meshsat:IDC-Header_2x05_P2.54mm_Vertical_NarrowPad (A netlist)", src: "v2/ecad/tools/gen_sch_a.py:1596-1597"}
        - {board: b, ref: J_AB2, part: "IDC 2x5: Wurth WR-BHD 61201021621 (HC6-SC-7), the same land (B netlist)", src: "v2/ecad/tools/gen_sch_b.py:1637-1638"}
      harness: {what: "10-way ribbon", length: "TBD: no J_AB2 row in the leads table (v2/docs/ASSEMBLY.md section 4); effect: the
                ribbon's length and its route past board D (mechanical, W4-F17) are not fixed",
              parts: "sockets Wurth WR-BHD 61201023021 (1 A per contact max) on WR-CAB 63911015521CAB (1.27 mm, 28 AWG, 1 A per conductor
                max) (HC6-SC-7)"}
      map_identity: {status: VERIFIED}
      judged_by: "check_contracts.py sections 7b (the J_AB2 map) and 10 (the pair reaches A's J_USBW)"
      pins: {1: USB_WALL_P, 2: USB_WALL_N, 3: GND, 4: GND, 5: GND, 6: GND, 7: GND, 8: GND, 9: GND, 10: GND}
      usb: "B bank 3 hub port 3 to A's J_USBW (JST-PH 1x4: VBUS_WALL, D-, D+, GND), the Glenair 233-370 feed-through's lead
        (a USB 2.0 type A coupler), a HOST port and the console and key-fill port (owner ruling D-12, in the netlist since
        458b2873; now gen_sch_a.py:1613-1618). VBUS_WALL comes from +5V_DEV through A's eFuse U32 (limit 0.9142 A nominal, TPS2596 equation 7), switched and
        watched by U28's USBX_EN and USBX_FLT; ESD on A (U29) and B. No impedance target declared for the ribbon (a bring-up
        link-speed test is owed). The USB-C outlet is power only (IF-EXT-USB)"
      levels: "USB 2.0 data only, at the speed the wall device negotiates on board B's bank 3 hub port 3; board A judges the pair
        as USB2_CM5 (boards.a, USB_WALL*: 90 ohm, 10 percent); pins 3 to 10 GND"
      current: "n/a: data only; VBUS_WALL does not cross this ribbon (it leaves board A on J_USBW behind the eFuse U32, 0.9142 A
        nominal limit: IF-EXT-USB)"
      default_state: "the pair idle until bank 3's hub runs; no control line on this ribbon; the wall port's VBUS off at power-up
        (USBX_EN held low by A R190 4.7 k, FW-A07)"
      sequencing: "the wall device enumerates after bank 3's host module boots and the panel sets USBX_EN (FW-A07)"
      mating: "IDC sockets into the box headers at both ends (HC6-SC-7); the A end's body stands into board D's outline (mechanical,
        W4-F17), so the header and its socket do not fit as placed until that is resolved"
      hot_plug: "not hot-pluggable (the session's choice in record l5r2, 3 October 2026, under the owner's standing rule, by
        SC-HF-04's reasoning for the other ribbons: an internal ribbon mated and unmated with the kit off)"
      mechanical: "COLLISION: A's J_AB2 stands inside board D's outline, its body to about Z 25.7 against D's underside on
        6 mm standoffs (positions VERIFIED, height INFERRED; W4-F17, adjudication A09; ASSEMBLY.md section 1)"
      tbd: ["the ribbon's length (harness.length); effect: its route past board D is not fixed",
            "W4-F17, A's J_AB2 inside board D's outline (mechanical); effect: the header and its socket do not fit as placed",
            "the bring-up link-speed test (usb); effect: the wall path's achieved speed is not shown"]
      findings: [W4-F17]
      serves: [NEED-10, NEED-14]

'''
NEW_BLOCKS["IF-AD-HARNESS"] = '''\
    IF-AD-HARNESS:
      title: "A to D mezzanine harness, A J_MEZZ1 to D J_HARN1 (IDC 2x8, 60 mm), and the 5 V lead A J_MEZZ_PWR1 to D J_PWR1 (VH, 18 AWG, 60 mm)"
      kind: board_to_board
      ends:
        - {board: a, refs: [J_MEZZ1, J_MEZZ_PWR1], part: "J_MEZZ1 IDC 2x8 box header Wurth WR-BHD 61201621621 (session pick HC6-SC-7,
           JLCPCB C5364137; 3 A per contact), land meshsat:IDC-Header_2x08_P2.54mm_Vertical_NarrowPad; J_MEZZ_PWR1 JST-VH B2P-VH 1x2
           (C274411) (A netlist)", src: "v2/ecad/tools/gen_sch_a.py:1387, 1598-1599"}
        - {board: d, refs: [J_HARN1, J_PWR1], part: "J_HARN1 IDC 2x8 box header Wurth WR-BHD 61201621621 (HC6-SC-7), the same land;
           J_PWR1 JST-VH B2P-VH 1x2 (C274411) (D netlist)", src: "v2/ecad/tools/gen_sch_d.py:259-261"}
      harness: {src: "v2/docs/ASSEMBLY.md section 4, mezzanine harness and mezzanine 5 V rows",
              what: "the harness a 16-way ribbon, 60 mm, IDC 2x8 both ends; the 5 V lead 18 AWG, 60 mm, VH both ends (ASSEMBLY.md
                section 4)",
              parts: "sockets Wurth WR-BHD 61201623021 (1 A per contact max) on WR-CAB 63911615521CAB (1 A per conductor max)
                (HC6-SC-7); VH housings and crimps"}
      map_identity: {status: VERIFIED}
      judged_by: "check_contracts.py section 8 (J_MEZZ1 and J_HARN1); section 11 (+3V3 on both ends); sections 9 and 12 to 14 (the D8
        USB pair, TX_INHIBIT_n's reach and pull on D)"
      pins: {1: USB_D8_P, 2: USB_D8_N, 3: GND, 4: GND, 5: GND, 6: GND, 7: TR_APRS, 8: TX_INHIBIT_n, 9: PA_EN, 10: SDA,
             11: SCL, 12: EXP_INT, 13: "+3V3", 14: GND, 15: ZEROIZE_HW, 16: AB_SPARE}
      current:
        power_lead: {net: "+5V_D8", from: "A U23 eFuse, ILM 2.0 A, enable D8_EN, its input +5V_D8IN from board A's buck U41 on VBAT since decision 55 (gen_sch_a.py:1387)", declared_a: 1.0,
                   power_up: "D8_EN held OFF by R113 4.7k until the panel firmware writes U27 (458b2873)",
                   contact: "JST-VH: 10 A per contact with AWG 16 on the standard header, 7 A with AWG 18 on the shrouded header only
                     (v2/vendor/connectors/jst-vh-catalogue.pdf, page 1); the fitted lead is 18 AWG on the standard B2P-VH, a
                     combination the catalogue does not rate (INCONCLUSIVE, as IF-AB-POWER's J_54V); U23 limits the lead at 2.0 A"}
        signals: "+3V3 on pin 13, one conductor: board A declares J_MEZZ1 0.1 A on its +3V3 (A intent) and board D's loads on it sum
          0.0654 A (D intent: U16 0.06, U19 and U20 0.002 each, U22 0.0002, R92 0.0012), 10 percent of the ribbon's 1 A at A's
          figure; no limiter on the branch (see tbd); the USB pair, the kit I2C and the control lines at logic currents"
      levels: "+5V_D8 from U41 at 4.872 to 5.133 V behind U23 (A intent, stream s99a), board D's codec 4.44 to 4.48 V at the 1.0 A
        typical, 0.09 to 0.13 V over its 4.35 V, and under it at the 2.0 A peak (S-116, open); +3V3 board A's 3.3 V; TX_INHIBIT_n,
        PA_EN, TR_APRS, EXP_INT and ZEROIZE_HW at 3.3 V logic; the kit I2C at 3.3 V (SEG-A under SC-HF-02, owed); USB_D8 at full
        speed to board D's TUSB2046I (USB_FULL_SPEED)"
      default_state: "+5V_D8 OFF (D8_EN held OFF by R113 until the panel writes U27: current.power_lead.power_up); PA_EN LOW (PA_SW_EN
        held LOW by R103: power_up); with the harness out TX_INHIBIT_n and PA_EN LOW on D (cable_out_states); +3V3 up with board A's
        main rail"
      sequencing: "+3V3 with board A's rail after MAIN; then the panel writes U27's D8_EN: U23 raises +5V_D8, board D's hub and codec
        start and USB_D8 enumerates on bank 3's host; PA_EN only with TX_INHIBIT_n, EMCON_HW and PA_SW_EN (power_up); KEY and
        PA_KEY hold low with their gates unpowered (back_power)"
      mating: "IDC 2x8 sockets into the box headers with board D 6.0 mm above board A (mechanical); the VH lead latches at both ends"
      hot_plug: "not hot-pluggable (the session's choice in record l5r2, 3 October 2026, under the owner's standing rule, by
        SC-HF-04's reasoning: +5V_D8 at up to 2.0 A on the VH lead and the inhibit line on the ribbon): mate with the kit off"
      cable_out_states: {TX_INHIBIT_n: "LOW (D R2 100k)", PA_EN: "LOW (D R3 100k)",
                         note: "KEY and PA_KEY carry only logic inputs and passive pulls since 458b2873 (RF-002, R6D-1): the KEY gate cannot key"}
      power_up: "PA_EN = TX_INHIBIT_n AND EMCON_HW AND PA_SW_EN on A (U35 and U36, SN74AUP1G08, since board A's round 8
        candidate; EMCON_HW AND PA_SW_EN in U26 before); PA_SW_EN is held LOW by R103 4.7k until the panel writes U27 (F-SQ-07
        corrected, 458b2873). TR_APRS is D's KEY line through R48 and feeds A's outlet interlock U30"
      mechanical: "board D sits on 6 mm standoffs with its underside 6.0 mm above A's top (v2/cad/render/scene.py, appendix
        32.85); ASSEMBLY.md is corrected to 6 mm; v2/BUILD.md still gives 22.6 mm (line 45 'M3 x 22.6 standoffs', line 75
        '22.6 mm standoffs'), an absolute Z read as a length (A09)"
      back_power: "INFERRED risk: D's harness-side logic is on A's +3V3 while its SA868 side is on +5V_D8 behind A's eFuse;
        KEY and PA_KEY hold low with their own gates unpowered (R84, R85, R4T-F9); EMCON.md L4 (gate supplies outside their
        specified range) applies to D's single gates"
      not_judged: ["the J_MEZZ_PWR1 to J_PWR1 lead", "heights under board B"]
      tbd: ["the 18 AWG lead on the standard VH header: no stated rating (JST VH catalogue page 1); effect: the 5 V lead's contact
            margin at U23's 2.0 A limit is unproven",
            "a +3V3 fault on board D: no branch limiter, so it is bounded only by board A's +3V3 converter (the TPS62933 at L7) through
            one 1 A ribbon conductor, its limit not read here; effect: the conductor's rating in that fault is not shown",
            "S-116, board D's codec under 4.35 V at the lead's 2.0 A peak; effect: the codec's floor at the peak"]
      findings: [W4-F17, EMCON-L4, PWR-F15]
      serves: [NEED-01, NEED-08]

'''
NEW_BLOCKS["IF-AC-MAINSW"] = '''\
    IF-AC-MAINSW:
      title: "panel MAIN button lead, C J_MAINSW (solder lands) to A J_MAINSW (JST-XH 1x2)"
      kind: board_to_board
      ends:
        - {board: c, ref: J_MAINSW, part: "two solder lands on board C's underside (meshsat:LeadLands_1x02), the lead soldered and
           beaded (C netlist)", pins: {1: MAINSW_A2, 2: MAINSW_B2}, src: "v2/ecad/tools/gen_sch_c.py:219-221"}
        - {board: a, ref: J_MAINSW, part: "JST-XH B2B-XH-A 1x2 (C158012; 3 A per contact with AWG 22, JST XH catalogue) (A netlist)",
           pins: {1: MAIN_PB, 2: GND}, src: "v2/ecad/tools/gen_sch_a.py:278"}
      harness: "a 24 AWG twisted pair, soldered at C, an XH2.5 housing at A where it unplugs (ASSEMBLY.md section 4, MAIN button
        row); TBD: its length (the row gives none), effect: its route past board B is not fixed"
      levels: "MAIN_PB is the LTC2954ITS8-1's PB input (A U1): open-circuit 1 to 2 V at -1 uA, falling threshold 0.6 to 1 V, pin
        range -1 to 26.4 V (Analog Devices 2954fb, p.3, MAKER); the button shorts it to GND"
      current: "the PB pull-up current through the closed button: -3 to -15 uA at 0.6 V and -1 to -12 uA at 1 V (2954fb p.3,
        MAKER); at 0 V not printed; against the XH's 3 A, negligible"
      default_state: "open (released): PB at its open-circuit 1 to 2 V; with the lead unplugged the same, so MAIN can neither start
        nor force the kit off"
      sequencing: "the start of the power-up sequence: a MAIN press releases the LTC2954ITS8-1's EN; PDT carries C152 680 nF, so a
        forced power-off needs about 4.4 s held (458b2873, W5-F2 corrected); a tap while running raises PI_SHDN_REQ (FW-A10, FW-A12)"
      mating: "the XH latch at A; soldered and beaded at C (ASSEMBLY.md: it unplugs at A)"
      hot_plug: "the lead is unplugged at A only with the kit off (the session's choice in record l5r2, 3 October 2026, under the
        owner's standing rule): a bouncing contact can read as a MAIN tap"
      judged_by: "none (no contract names J_MAINSW)"
      tbd: ["the lead's length (ASSEMBLY.md's MAIN button row gives none); effect: its route past board B is not fixed"]
      findings: []
      serves: [NEED-04, NEED-05]

'''
NEW_BLOCKS["IF-AE-RF"] = '''\
    IF-AE-RF:
      title: "eleven RF blind-mate joints as generated (twelve under D-07): A J_BM1..11 (Radiall SMP-MAX R222M00720, underside) onto E's float-clamped plugs, RG-316 to the end-wall arrestor bulkheads"
      kind: board_to_board
      ends:
        - {board: a, refs: "J_RF1..11 (SMA, top) and J_BM1..11 (SMP-MAX, underside)", part: "SMA jacks Amphenol 132134-11 vertical
           (C3174425) at J_RF1..11; Radiall SMP-MAX slide-on receptacles R222M00720 (land meshsat:Radiall_SMPMAX_R222M00720) at
           J_BM1..11 (A netlist)", src: "v2/ecad/tools/gen_sch_a.py:1310-1314"}
        - {board: e, ref: "none: the clamp bar is a board-file feature with no schematic designator", part: "the float clamp bar
           holding eleven Radiall R222M80500 right-angle SMP-MAX plugs, crimped and tied into the clamp (ASSEMBLY.md section 4, the
           RF jumpers row)", what: "the float clamp bar, one bar with twelve cavities, D-07's at X 46 among them (since 45f6d83f); no RF net on E", src: "v2/ecad/tools/gen_pcb_e.py:44-48, 110-131"}
        - {case: "the ruled gas-discharge arrestors as the antenna bulkheads on one RF entry plate per end wall (CASE-MARGINS.md C2, C4)"}
      harness: "RG-316 jumpers, each cut to its route plus 20 mm, 252 to 432 mm, bend radius 12.5 mm, an SMP-MAX plug at the clamp
        and a right-angle SMA male crimp plug at the arrestor's inner jack (the pick OPEN: M17g, M17x) (ASSEMBLY.md section 4, the
        RF jumpers row); on board A's top each radio's pigtail to its SMA jack (ASSEMBLY.md's pigtail rows)"
      levels: "RF at 50 ohm on RG-316; RF_VHF carries the 30 W PA output at 144 MHz (power_handling); whether any joint carries a DC
        antenna feed is not stated by this contract (see tbd)"
      current: "n/a: the joints carry RF only, no supply current; the highest RF power is RF_VHF's 30 W at 144 MHz (power_handling)"
      default_state: "n/a: passive joints; what transmits through them is each radio's EMCON state (CONOPS section 4b)"
      sequencing: "the joints mate as the stack seats on its spacer tubes inside the 12.4 to 14.4 mm window (gap), before any power
        (the D-14 procedure, IF-AE-DOCK hot_plug), and part when it lifts"
      mating: "blind-mate SMP-MAX slide-on: the receptacles on A's underside onto the float-clamped plugs on E as the stack seats
        (gap, nests); the SMA jumpers on the arrestors' inner jacks"
      hot_plug: "no: the stack is lifted only with the kit off by D-14's procedure (IF-AE-DOCK hot_plug); an SMP-MAX parted while a
        radio transmits is not rated here"
      sites_case_x_from_a: {VHF: -52, HF: -38, WIFI24: -24, GNSS: -10, SDR: 4, P2P-A: 18, P2P-B: 32, 5G-1: 60, 5G-2: 74,
                            IRIDIUM: 88, LORA: 100}
      site_source: "board A's RF_X (gen_pcb_a.py:38); board E's RF_SITES mirror it since faf8c981 (gen_pcb_e.py:30, LORA at
        100), and check_pcb_e.py parses board A's RF_X and refuses a board whose clamp holes are not on it (W4-F16 corrected
        in the generator; the committed E17 board still carries 102)"
      nests: "the separate float_clamp.py nests (16 mm along X at a 14 mm pitch, 12 mm from IRIDIUM to LORA) overlapped and
        the LORA nest reached the rod keep-out (A09); since 45f6d83f one clamp bar with twelve cavities and M3 holes at
        mid-pitch replaces them (R4E-07, gen_pcb_e.py:44-48 and 110-131)"
      walls: "chosen (CASE-MARGINS.md 3.4, the session's choices): west VHF -93, HF -62, WIFI 2.4 -31, GNSS 0, SDR +31, WIFI
        P2P A +62, WIFI P2P B +93; east 5G MAIN (ANT0) -62, 5G DIV (ANT2) -31, 5G ANT3 0, IRIDIUM +31, LORA +62; 31 mm pitch,
        Z 59; the jumpers 232 to 412 mm on their planned routes, each link budget at its own length"
      five_g_ports: "the RM520N-GL has four ports ANT0..ANT3 and no MAIN or DIV connector. Owner ruling D-07: three jacks,
        ANT0, ANT2 and ANT3, at board A's free site (X +46) if the case measurement confirms that site and a board E clamp
        there; otherwise two, ANT0 and ANT2. The owner reversed D-08 on 26 September 2026, so no case measurement will
        come, and the condition is judged on paper at the worst of Peli's figures (ARCHITECTURE.md section 9.2, the
        session's reading under the standing rule): the case half is laid out (ANT3 the east wall's arrestor at Y 0, Z 59;
        no case row NOT MET; the east jumpers' layering under the plugs, M17g and M17x, OPEN until the jumper plug is
        picked); the board half is board A's site at X +46, in no generator yet, and board E's cavity there, drawn since
        45f6d83f. The three
        jacks stand unless the picked plug or board E's clamp bar makes a row NOT MET that no lever closes. The legends
        5G-MAIN and 5G-DIV of gen_sch_a.py:1311 follow the module's port names when A is regenerated"
      gap: "13.4 mm blind-mate gap, 12.4 to 14.4 window, on spacer tubes (appendix 32.21 and 32.30; ASSEMBLY.md section 1);
        CASE-MARGINS.md judges no blind-mate alignment, and nominal CAD establishes none"
      power_handling: "RF_VHF carries the 30 W PA output; SMP-MAX and RG-316 power handling at 144 MHz TBD"
      judged_by: "check_pcb_e.py (the clamp sites against board A's RF_X, and the cavity at X 46 required on E, check_pcb_e.py:75-84); nothing judges board A's twelfth site, which is in no generator"
      tbd: ["SMP-MAX and RG-316 power handling at 144 MHz for RF_VHF's 30 W (power_handling); effect: the VHF joint's rating is
            unproven",
            "the right-angle SMA plug at the arrestors (M17g, M17x); effect: the east jumpers' layering under the plugs is OPEN",
            "board A's twelfth site at X +46 (D-07), in no generator; effect: the 5G ANT3 joint does not exist on board A yet",
            "a DC antenna feed on any joint; effect: the arrestors' and the joints' DC rating is not stated"]
      findings: [W4-F10, W4-F12, A09, R4E-07]
      serves: [NEED-01, NEED-02, NEED-11, NEED-17]

'''
NEW_BLOCKS["IF-A-PA"] = '''\
    IF-A-PA:
      title: "board to device: the PA module on the face plate (A J_PA 13.8 V; D J_VGG gate bias, J_PAIN drive, J_PAOUT output)"
      kind: board_to_device
      ends:
        - {board: a, ref: J_PA, part: "JST-VH 1x2: 1 +13V8_PA, 2 GND", src: "v2/ecad/tools/gen_sch_a.py:1006"}
        - {board: d, refs: [J_VGG, J_PAIN, J_PAOUT], part: "J_VGG JST-PH B2B-PH-K 1x2 (C131337); J_PAIN U.FL Hirose U.FL-R-SMT-1
           (C88373); J_PAOUT SMA Amphenol 132134 vertical (C3174425) (D netlist)", src: "v2/ecad/tools/gen_sch_d.py:601-602, 682"}
        - {device: "Mitsubishi RA30H1317M1 on the plate; every lead soldered at the module (ASSEMBLY.md section 4, the four PA rows)"}
      harness: "the PA rail 16 AWG, 300 mm, VH at A, soldered at the module; the gate bias 24 AWG twisted, 250 mm, PH at D; the drive
        RG-178, 250 mm, U.FL at D; the output RG-316, 250 mm, bend radius 12.5 mm, SMA at D (ASSEMBLY.md section 4, the four PA
        rows)"
      levels: "+13V8_PA 13.8 V (U13, EMCON gated) against the module's VDD absolute maximum 17 V; VGG 4.48 V (bias) against its
        absolute 6 V; the drive: the SA868 at 0.5 W (H/L held low by PA_EN) into a 10 dB T-pad, 50 mW at J_PAIN (gen_sch_d.py),
        against the module's Pin absolute 100 mW; Pout over 30 W at VDD 12.5 V, VGG 5 V and Pin 50 mW (RA30H1317M1 datasheet)"
      current: {typ_a: 5.0, peak_a: 6.0, src: "gen_sch_a.py:121-122",
                note: "the stage's own average current loop limits at 7.2 to 9.5 A (F-PR-01, 458b2873); the drain current is not
                  characterised (F-PR-02: 75 to 113 W, POWER-THERMAL.md)",
                contact: "JST-VH 10 A per contact with AWG 16 on the standard header (v2/vendor/connectors/jst-vh-catalogue.pdf, page
                  1): the 6.0 A peak is 60 percent of it"}
      default_state: "the rail OFF: PA_SW_EN held LOW by A R103 4.7k until the panel writes U27, so PA_EN is low (IF-AD-HARNESS
        power_up); VGG off until PA_KEY; the T/R relay K1 at rest routes the exciter to the antenna, not to the PA (gen_sch_d.py)"
      sequencing: "the rail on with PA_EN = TX_INHIBIT_n AND EMCON_HW AND PA_SW_EN (emcon); VGG on with PA_KEY; the relay routes the
        drive to the PA only while keyed; every key-down at most 60 s and the outlets dropped while keyed (peak, FW-A05)"
      mating: "the VH latch at A, soldered at the module; PH at D for the bias; U.FL pushed on at D for the drive; SMA at D for the
        output"
      bias: "VGG from a TLV75801P at 4.48 V on board D, enabled by PA_KEY (faf8c981), inside the RA30H1317M1's VGG under 5 V"
      emcon: "PA_EN = TX_INHIBIT_n AND EMCON_HW AND PA_SW_EN (board A's round 8 candidate: U35, U36; EN/UVLO at 0.6 of PA_EN
        through R58/R59) switches the rail; D's KEY gate drops the relay and the VGG regulator: CLOSED at desk on the
        gate-bias path (EMCON.md row 2), and the drain-supply path dominant end to end through TX_INHIBIT_n (EMCON.md
        section 4a); single-fault tolerant only downstream of SW_EMCON and TX_INHIBIT_n"
      peak: "owner ruling D-11: the outlet interlock is in A's netlist (U30, U26, 458b2873); every key-down at most 60 s, gated
        at +55 C cells and +75 C on the PA's flange and cut at +85 C (POWER-THERMAL.md section 7.2, PROVISIONAL); no board
        carries a flange sensor (PWR-F15): its lead would join this contract. As first written; since round 8 board D carries the
        flange sensor's lead J_FLANGE (IF-D-FLANGE)"
      licence: "owner ruling D-04: the VHF path gets a band lock and runs inside the operator's licence and the EU limits (owed)"
      hot_plug: "never unplug J_PA with the kit on (the session's choice SC-HF-04 of 27 September 2026 under the owner's standing rule, v2/docs/HW-FW-CONTRACT.md section 8): 13.8 V at up to 6 A"
      judged_by: "none"
      tbd: ["the drain current (F-PR-02: 75 to 113 W, uncharacterised); effect: the rail's and the lead's peak basis",
            "the band lock (licence, D-04, owed); effect: the VHF path's operation inside the operator's licence"]
      findings: [F-PR-02, PWR-F15]
      serves: [NEED-01, NEED-08, NEED-16]

'''
NEW_BLOCKS["IF-LID-HF"] = '''\
    IF-LID-HF:
      title: "board to device: the lid harness to the QMX HF unit (A J_HF 12 V, B J_QMX USB, A J_RF2 HF antenna)"
      kind: board_to_device
      ends:
        - {board: a, refs: [J_HF, J_RF2], part: "J_HF JST-VH B2P-VH 1x2 (C274411); J_RF2 SMA jack Amphenol 132134-11 vertical
           (C3174425) (A netlist)", src: "v2/ecad/tools/gen_sch_a.py:1015, 1310-1314"}
        - {board: b, ref: J_QMX, part: "PH 1x4: 1 VBUS_QMX, 2 QMX_DM, 3 QMX_DP, 4 GND; bank 2 hub port 4. As generated the land is a
           2.54 mm pin header (gen_sch_b.py's land key PH1x4 is Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical, B
           netlist), not a JST-PH 2.00 mm part (finding L5R2-F04)", src: "v2/ecad/tools/gen_sch_b.py:964-966"}
        - {device: "QMX HF transceiver in the lid tray (ASSEMBLY.md section 1, QMX tray row, and section 2, step 10)"}
      harness: "the HF rail 18 AWG, 500 mm, least bend radius 20 or under, VH at A, a straight 2.1 x 5.5 plug at the unit; the QMX USB
        lead, 500 mm, PH at B, USB-C at the unit; the HF antenna RG-316, 500 mm, BNC male at the unit, SMA male at A; a service loop
        at the hinge (ASSEMBLY.md section 4, the HF rail, QMX USB and HF antenna rows)"
      levels: "+12V_HF 12.0 V, the QMX's maximum supply (current.note, F-PR-07); VBUS_QMX 5 V behind board B's 0.5 A polyfuse F3
        (B intent: 0.30 A declared); the QMX's USB on bank 2 hub port 4 at the speed it negotiates; RF: the QMX's 3 to 5 W output at
        a 12 V supply (QRP Labs' product page) on J_RF2"
      current: {rail: "+12V_HF", typ_a: 1.0, peak_a: 2.0, src: "gen_sch_a.py:123-124", note: "set at 12.0 V, the QMX's maximum supply (F-PR-07, minor)",
                maker: "receive 80 mA, transmit around 0.7 A for 5 W with a 12 V supply (QRP Labs' product page,
                  v2/vendor/qrp-labs/qmx-product-page-2026-09-27.txt), under the 1.0 A typical and 2.0 A peak declared"}
      default_state: "+12V_HF OFF until HF_SW_EN (HF_EN = TX_INHIBIT_n AND EMCON_HW AND HF_SW_EN: emcon); VBUS_QMX on with +5V_DEV,
        not gated (emcon)"
      sequencing: "+12V_HF only with HF_EN; the QMX enumerates on bank 2's host after its module boots; the lid harness is plugged
        before the kit is started (hot_plug)"
      mating: "the VH latch and the SMA at A; at B the lead's housing on a 2.54 mm pin header as generated (the end's part, finding
        L5R2-F04); at the unit a 2.1 x 5.5 barrel, a USB-C plug and a BNC (ASSEMBLY.md section 4)"
      emcon: "EMCON switches +12V_HF off (board A's round 8 candidate: HF_EN = TX_INHIBIT_n AND EMCON_HW AND HF_SW_EN, U37 and
        U38, EN/UVLO at 0.6 of HF_EN; dominant end to end through TX_INHIBIT_n, EMCON.md section 4a); VBUS_QMX from B is not
        gated, and the QMX does not connect USB VBUS inside (QRP Labs' schematics, EMCON.md row 3: back-feed CLOSED)"
      hot_plug: "the lid harness is unplugged when the lid comes off its hinge (ASSEMBLY.md section 7); only with the kit off (the session's choice SC-HF-04 of 27 September 2026 under the owner's standing rule, v2/docs/HW-FW-CONTRACT.md section 8)"
      judged_by: "none"
      prototype_1: "deferred (owner ruling D-01, 25 September 2026: HF is built where possible and reported NOT_YET_TESTED)"
      tbd: ["J_QMX's land, a 2.54 mm pin header as generated against PH 1x4 in this contract and ASSEMBLY.md (L5R2-F04); effect: the
            lead's housing does not mate as written",
            "the 18 AWG HF lead on the standard VH header: no stated rating (JST VH catalogue page 1); effect: J_HF's contact margin
            at the 2.0 A peak",
            "the QMX's supply current at 12 V from QRP Labs' manual (the product page's 'around 0.7 A' is approximate); effect: the
            1.0 A declaration's basis"]
      findings: [W3-F25]
      serves: [NEED-01, NEED-16]

'''
BLOCK_ORDER = ["IF-BC-PANEL", "IF-AB-RIBBON", "IF-AB-WALL", "IF-AB-POWER", "IF-AD-HARNESS", "IF-AE-DOCK", "IF-PE-PACK",
               "IF-AC-MAINSW", "IF-AE-RF", "IF-A-PA", "IF-LID-HF", "IF-EXT-USB"]

# ====================================================================================================== exact yaml edits
Y_HEADER_OLD = "board_to_board:\n  schema: 1\n"
Y_HEADER_NEW = """\
# LAYER 5'S SECOND ROUND (MESHSAT-1357, 3 October 2026; v2/docs/records/l5r2/). The eight first-twelve contracts carry the pass-2
# fields (their older keys' content moved, not lost); the fans after D-18 and L4-E11 section 18 (b929d8be); the SLOT_EN keeper and
# GND-002 after record l8gnd (226e9143), with IF-A-CHASSIS added. Those two commits are not in this branch's history: their
# sections are copied into the record's inputs/, and every figure resting on them is DRAFTED and PROVISIONAL until their release.
board_to_board:
  schema: 1
"""
E5_END_OLD = '        - {board: e5, what: "no schematic; targets and lands generated from board A\'s file by position (gen_pcb_e5.py)"}\n'
E5_END_NEW = ('        - {board: e5, ref: "none: the block has no schematic and so no designators", part: "the dock block E5: twelve plated\n'
              '           contact targets, four pack targets, a pre-charge target, eight VIN_RAW targets and the wire lands beneath them",\n'
              '           what: "no schematic; targets and lands generated from board A\'s file by position (gen_pcb_e5.py)", src: "v2/ecad/tools/gen_pcb_e5.py"}\n')
PIN1_END_OLD = ('        current over 1.471 A (E11-35, R-179: no fan is named), or the hard short\'s qualification failing (E11-38); the ground\n'
                '        return keeps seven 813 contacts (2.238 A each at the 32.1 A coincidence, 2.406 A with one open, 79.3 C at the 51 C air;\n'
                '        L4-E11 15a, INFERRED on w3de\'s model)"\n')
PIN1_END_NEW = PIN1_END_OLD[:-2] + ('. ROUND 2 (record l5r2; L4-E11 section 18 at b929d8be, DRAFTED, not in this tree,\n'
                '        PROVISIONAL until its release): the fans leave VSYS_E for the regulated +12V_FAN rail from U22 (LTC3115EFE-1), so the branch\n'
                '        is declared 1.3208 A (U12 0.8 A, U22 0.5208 A at the floor with both fans at full speed), 89.8 percent of U42\'s least\n'
                '        limit 1.4713 A with 0.1504 A in hand, R228 (renamed from R221 by L4-E11 at 787e7b15) kept at 11.0 kOhm, the contact at\n'
                '        37.7 percent of 3.5 A, VSYS_E 9.508 V at the floor; the start rule above (0.5713 A and 0.3356 A on VSYS_E) is superseded\n'
                '        by section 18b: with one fan running and U12 on, U42 leaves 0.1504 A of room, 1.21 W at the rail for the other fan\'s\n'
                '        start, the start current NOT READ (E11-35)"\n')
DOCK_NJ = '      not_judged: ["clamp orientation and value against the board (A03, A04)"'
DOCK_GND = ('      grounding: "the dock\'s ground contacts carry GND, never CHASSIS: board E carries no chassis net (GND-002 point 6; record\n'
            '        l8gnd 2d), and the kit\'s one bond to the case is board A\'s R229 near the dock (IF-A-CHASSIS; DRAFTED by record l8gnd at\n'
            '        226e9143, not applied, PROVISIONAL until its release)"\n')
DC_GND_OLD = '      grounding: "GND_V is board E\'s vehicle return; GND-002\'s chassis bond is not drawn (ARCHITECTURE.md 6.5)"\n'
DC_GND_NEW = ('      grounding: "GND_V is board E\'s vehicle return; GND-002\'s chassis bond is not drawn (ARCHITECTURE.md 6.5); since 3 October\n'
              '        2026 it is DRAFTED on board A as IF-A-CHASSIS (record l8gnd at 226e9143, R229 the one bond; PROVISIONAL until its\n'
              '        release); board E carries no chassis net (GND-002 point 6, l8gnd 2d): the DC receptacle\'s shell terminates on the\n'
              '        connector plate (GND-002 point 3), never on GND_V"\n')
ETH_GND_OLD = ('      grounding: "the jack\'s shield is on GND in the netlist; GND-002 puts the RJ45 shell on CHASSIS with a 1 nF 2 kV common node\n'
               '        (GROUNDING-AND-SHIELDS.md), not drawn in any generator"\n')
ETH_GND_NEW = ETH_GND_OLD[:-2] + ('. As generated C33 (1n 2kV) returns the centre taps\' common node BOB to GND and\n'
               '        J_ETH\'s shield tabs sit on GND (B netlist). DRAFTED since 3 October 2026 by record l8gnd at 226e9143\n'
               '        (apply_gen_sch_b_gnd002.py, changes 2 and 3; not applied, PROVISIONAL until its release): C33 to CHASSIS and J_ETH SH\n'
               '        to CHASSIS, Microchip DS00004151A p.10 (\'connected to chassis ground through a 1000 pF, 2 kV capacitor\'; \'The metal case\n'
               '        shield of the RJ45 connector is also tied to chassis ground\'); board B\'s CHASSIS has no DC bond on board B and reaches\n'
               '        the kit\'s one bond (R229 on board A, IF-A-CHASSIS) only over the patch lead\'s shield, the sealed wall RJ45 and the\n'
               '        connector plate, so the wall RJ45 pick must carry the shield to the plate (l8gnd F01: the held Bulgin PX0833 has a\n'
               '        plastic body and its PX0888 shielding backshell is sold separately; the pick OPEN): until it does, C33 and the shell\n'
               '        float"\n')
ETH_TBD_OLD = '      tbd: ["the sealed RJ45 part; effect: plate, seal and shield bond not final",\n            "the PoE class the kit offers'
ETH_TBD_NEW = ('      tbd: ["the sealed RJ45 part; effect: plate, seal and shield bond not final",\n'
               '            "the wall RJ45\'s shield path to the plate (record l8gnd F01: the PX0833\'s plastic body, the PX0888 backshell); effect:\n'
               '            C33 and the shell float under GND-002 until a pick carries the shield",\n'
               '            "the PoE class the kit offers')
ETH_FIND_OLD = "      findings: [GND-002, HF-F08]\n      serves: [NEED-05, NEED-14]\n\n    IF-MON:\n"
ETH_FIND_NEW = "      findings: [GND-002, HF-F08, L8G-F01]\n      serves: [NEED-05, NEED-14]\n\n" + '''\
    IF-A-CHASSIS:
      title: "board to case: the one chassis bond, the connector plate's stud F to board A's CHASSIS pad H1 (GND-002)"
      kind: board_to_case
      ends:
        - {board: a, ref: H1, part: "M4 bonding pad, land meshsat:ChassisLug_M4_CHASSIS (plated hole 4.3, 12.0 ring both sides), on
           the net CHASSIS, joined to GND by R229 (0R 2512) alone, the ONE defined impedance; DRAFTED by record l8gnd at 226e9143
           (apply_gen_sch_a_gnd002.py), not in this tree's generator, PROVISIONAL until its release",
           src: "v2/docs/records/l5r2/inputs/l8gnd-sections-2-3-226e9143.md, section 2b"}
        - {case: "the connector plate's M6 ground stud F (ASSEMBLY.md section 4's connector plate row, F at +34.6, 64.5;
           CASE-MARGINS.md: inside a washer of 12, the ring lug of the one bonding strap, and a Nyloc)"}
        - {cable: "the bonding strap, an M4 ring lug at H1 and a ring lug at the stud. TBD: the strap and the lugs (Layer 7's pick,
           l8gnd F07), effect: the bond's resistance and its current capacity are not stated"}
      harness: "one strap from the plate's stud F to H1 near the dock on the back-wall side (l8gnd 2b; H1's placement beside J_DOCK a
        layout-entry item, l8gnd F08)"
      levels: "n/a: a bond, no signal or supply: CHASSIS sits at board A's GND through R229 (0 Ohm) and carries cable-borne
        common-mode and discharge current, never a supply or a return (l8gnd 2b)"
      current: "no service current (GND-002 point 6 keeps the pack's return off the case metal); a fault current only if a wall
        receptacle's shell meets its own supply inside a plug, cleared by the vehicle fuse F1 (l8gnd 2b, INFERRED); TBD: R229's
        rating with its BOM code (C25469 to be confirmed, l8gnd F09), effect: the link's fault capability"
      default_state: "bonded whenever the strap is fitted; with the strap off the plate is bonded only through the antenna leads
        (l8gnd L8G-D1)"
      sequencing: "n/a: a passive bond, fitted at assembly before the first power"
      mating: "the M4 ring lug under a screw on H1's 12.0 ring; the stud's ring lug under its washer and Nyloc (CASE-MARGINS.md)"
      hot_plug: "n/a: a bolted bond, not disconnected in service"
      judged_by: "record l8gnd's check_gnd002_netlist.py on the regenerated netlist (board A: CHASSIS carries exactly H1 and R229,
        R229 the only part on both CHASSIS and GND); on the committed netlists it reads NOT DRAWN on A and B (l8gnd 2e)"
      tbd: ["the strap and the lugs (Layer 7, l8gnd F07); effect: the bond's resistance and current capacity",
            "R229's BOM code C25469 to be confirmed on the regenerated BOM (l8gnd F09); effect: the link's rating",
            "the bond resistance read four-wire at pre-compliance (GROUNDING-AND-SHIELDS.md's list); effect: none until the chamber",
            "record l8gnd's release; effect: until applied board A has no CHASSIS net and GND-002 reads NOT DRAWN"]
      findings: [GND-002, L8G-F01]
      serves: [NEED-18]

    IF-MON:
'''

FANS_OLD_START = "    IF-E-FANS:\n"
FANS_NEW = '''\
    IF-E-FANS:
      title: "board to device: the two mixer fans to board E J_FAN1 and J_FAN2"
      kind: board_to_device
      ends:
        - {board: e, refs: [J_FAN1, J_FAN2], part: "pin header 1x3, 2.54 mm: 1 CELL_F (the pack node), 2 FANn_SW (2N7002 Q9, Q10
           low-side, SS14 flyback D7, D8), 3 FANn_TACH (R46, R47 10 k to +3V3_E6), as generated. DRAFTED by L4-E11 section 18 at
           b929d8be (apply_gen_sch_e_aux.py rewritten, not in this tree; PROVISIONAL until its release): four pins, 12 V on
           +12V_FAN, GND, PWM (Q9, Q10 as open-drain drivers), TACH (the 10 k pull-up kept); D7, D8 and the FANn_SW nodes removed",
           src: "E netlist (53a98a71); v2/docs/records/l5r2/inputs/l4e11-section-18-b929d8be.md, section 18a"}
        - {device: "two Sanyo Denki 9WL0612P4H001 (San Ace 60W, 60 x 60 x 25, IP68, 12 V, 10.8 to 13.2 V, 0.17 A, 2.04 W, -20 to +70
           C, four leads: 12 V, GND, pulse sensor, PWM; D-18 settled by the session, record l7pwr) on brackets at the stack's ends
           (ruling of 7 September 2026)"}
      harness: "the fans' own four leads; their termination NOT READ (the maker's manual M0011876C is behind a form); ASSEMBLY.md says
        SH housing against the netlist's 2.54 mm header (HF-F04)"
      levels: "as generated: the pack node CELL_F, 12 to 16.884 V, switched low side by Q9 and Q10, which the fans' 13.2 V maximum
        does not cover (record l7pwr). Under L4-E11 section 18 (DRAFTED at b929d8be, PROVISIONAL until its release): +12V_FAN 12.001
        V (11.512 to 12.431 V at FB's limits) from U22 on VSYS_E, inside the fans' 10.8 to 13.2 V by 0.71 V below and 0.77 V above;
        PWM into the fan's PWM input from Q9 and Q10 as open-drain drivers (the PWM input level NOT READ); the tachometer an open
        collector with 10 k to +3V3_E6"
      current: "0.17 A each at 12 V, 2.04 W (Sanyo Denki's page, record l7pwr); at U22's input 0.5208 A for both at full speed at
        VSYS_E's floor (4.08 W over 0.85 at 9.508 V plus 16 mA), the dock branch 1.3208 A with U12, 89.8 percent of U42's least
        limit 1.4713 A (L4-E11 18b, MODELED, the 0.85 an ASSUMPTION); the start current NOT READ (no maker prints one): with one
        fan running and U12 on, U42 leaves 1.21 W at the rail for the other's start (18b)"
      power: "+12V_FAN from U22 (ADI LTC3115EFE-1 as ADI's TA04, 1 MHz, L4 Coilcraft XAL6060-103ME), RUN on at 8.33 V and off at 6.89 V
        of VSYS_E, so a fan fault that drives U22 to its limit against U42's lets VSYS_E fall only to U22's disable, a rail hiccup
        and not a controller reset (INFERRED); U22's heat 0.72 W at full speed (MODELED); behind U42, the branch's limiter, no fuse
        of its own (L4-E11 18a, DRAFTED at b929d8be, PROVISIONAL)"
      sequencing: "the sensor controller switches the fans after it boots (FW-E07); U22's 9 ms soft start covers the rail's own rise
        only: the fans start one at a time, each by a PWM-duty ramp into the fan's PWM input, never while U12 or U22 starts (FW-E11,
        E11-39, R-188; L4-E11 18c)"
      default_state: "as generated off: Q9 and Q10's gates held low at reset only by the RP2040's pad pull-downs (no discrete
        pull-down, HF-F07). Under the draft +12V_FAN is up whenever VSYS_E is over 8.33 V, so at reset the fans see their PWM input
        with the open-drain driver off: whether a fan runs, and how fast, with its PWM input released is NOT READ (the maker's
        manual); see tbd"
      mating: "TBD: the fans' lead termination (four leads, NOT READ) against board E's header (a 2.54 mm 1x3 as generated, four pins
        under the draft; ASSEMBLY.md says SH, HF-F04), effect: the fan lead does not mate as written"
      hot_plug: "no"
      judged_by: "none"
      tbd: ["the fans' start current (NOT READ; E11-35, R-179 the bench); effect: the stagger's margin under U42",
            "the fans' PWM input level and their behaviour with PWM released (NOT READ, manual M0011876C); effect: Q9 and Q10's
            open-drain drive and the default state",
            "the lead termination and board E's header (HF-F04); effect: the lead does not mate as written",
            "the rail U22 and the four-pin headers are DRAFTED by L4-E11 at b929d8be, not in this tree; effect: as generated the fans
            sit on CELL_F, over their 13.2 V"]
      findings: [HF-F04, HF-F05, F-L7-01]
      serves: [NEED-06, NEED-07]

'''
BFANS_OLD_START = "    IF-B-FANS:\n"
BFANS_NEW = '''\
    IF-B-FANS:
      title: "board to device: the three compute modules' cooler fans, board B J_FAN1 to J_FAN3"
      kind: board_to_device
      ends:
        - {board: b, refs: [J_FAN1, J_FAN2, J_FAN3], part: "JST-SH BM04B-SRSS-TB (C160390): 1 +5V_Sx, 2 GND, 3 FAN_TACHOx (module pin 16), 4 FAN_PWMx (module pin 19, R{s}51 10 k to the module's +3V3_CMx)", src: "B netlist"}
        - {device: "three Sanyo Denki 9WPA0412P6G001 (San Ace 40W, 40 x 40 x 20, IP68, 12 V, 10.8 to 13.2 V, 0.17 A, 2.0 W, -20 to +70 C,
           pulse sensor and PWM; D-18 settled by the session, record l7pwr) on the Raspberry Pi CM5 Coolers, one a slot"}
      harness: "the fan's own lead, SH at B; its termination NOT READ (the maker's manual behind a form)"
      levels: "supply as generated: the slot's +5V_Sn at 5.1 V on pin 1 (B netlist; L4-E11 18d), OUTSIDE the fans' 10.8 to 13.2 V:
        finding E11-40 for board B's owner, OPEN; PWM and tachometer at the module's 3.3 V logic (R{s}51 pulls FAN_PWMx to +3V3_CMx)"
      current: "0.17 A at 12 V, 2.0 W each (Sanyo Denki's page, record l7pwr); from a per-slot step-up on +5V_Sn about 0.436 A each at
        full speed (record l7pwr, F-L7-02, INFERRED); as generated the header declares 0.1 A on +5V_Sn (L4-E11 18d); the start
        current NOT READ"
      power: "as generated from the slot's own rail +5V_Sn, which does not cover the fans' 10.8 to 13.2 V: E11-40 needs a regulated
        12.0 V, a per-slot step-up from +5V_Sn (keeping an empty slot's fan off) or a 12 V feed from board A over the bay harness
        (L4-E11 18d, record l7pwr F-L7-02); PROVISIONAL until board B's owner draws one"
      control: "the module's own fan control (the module OS), the PWM on its Fan_PWM pin"
      sequencing: "the fan powers with its slot (SLOT_EN); the module's OS sets the speed after boot"
      default_state: "off with the slot; with the slot on and before the module drives FAN_PWMx, R{s}51 holds PWM high (INFERRED:
        full speed on a 4-wire fan)"
      mating: "SH latch at B; TBD: the fan's lead termination against the SH header (NOT READ), effect: whether the lead mates"
      hot_plug: "no"
      judged_by: "none"
      tbd: ["E11-40: the coolers' 10.8 to 13.2 V not met by +5V_Sn as generated (L4-E11 18d, record l7pwr F-L7-02); PROVISIONAL until
            board B's owner draws a 12.0 V feed; effect: the cooler fans cannot run as generated",
            "the start current and the PWM input level (NOT READ); effect: the slot budget's fan row at start",
            "the fan's lead termination against the SH header; effect: whether the lead mates"]
      findings: [E11-40, F-L7-02]
      serves: [NEED-03, NEED-07]

'''

SLOT_OLD_START = "    SLOT_EN1..3: {"
SLOT_OLD_END = "    SHORE_INHIBIT: {"
SLOT_NEW = '''\
    SLOT_EN1..3: {reset: "LOW (A R30, R34, R38 100 k to GND; the RP2040's pads reset as inputs)", default: "every slot OFF until the
        panel's boot order raises them one at a time after ZEROIZE_SW is read (FW-C01 step 6)", cable_out: "as generated LOW: every
        slot off (IF-BC-PANEL, IF-AB-RIBBON); with the keeper applied the LAST DRIVEN LEVEL while A's +3V3 is up, LOW from a
        power-up (record l8gnd 3g; DRAFTED, PROVISIONAL until its release)", hold: "DRAFTED by record l8gnd at 226e9143 (its
        sections 3a to 3g, copied into v2/docs/records/l5r2/inputs/), not applied, PROVISIONAL until its release: keepers U43
        (SN74LVC08A, one gate a line, inputs on SLOT_ENn) with R230 to R232 (4.7 k) from the gate's output back onto SLOT_ENn on
        board A hold each line at its last driven level across a panel reset (a RUN or SWD reset, the ROM bootloader, a brownout
        that resets the RP2040 while IOVDD stays up): held HIGH at least 2.547 V (the pad's pull-down at 50 k), held LOW at most
        0.266 V (at 80 k), against VIH 2.0 V and VIL 0.8 V and the enables' thresholds (l8gnd 3b); NOT across a loss of the
        panel's supply (the unpowered pad clamps a held high under VIL and the slots drop) nor across PI_KILL (A's +3V3 falls and
        the lines fall to 0 V through R30, R34, R38) (l8gnd 3d); until applied a panel reset or update drops every module (FW-C02),
        so criterion 5.6's item stays open", firmware: "FW-C01, FW-C02 (read and adopt the held level at boot), FW-C13 (H1 drops
        them), FW-C14 (a slot found held up at boot), FW-C04 (the wipe cuts them at 3.0 s)", source: "L4-E9 4c (the cold start);
        record l8gnd 3b, 3d, 3f, 3g (L8G-F13)"}
'''
FANLINE_OLD = '''starts, under U42's least limit 1.471 A (DRAFTED under (B1))", firmware: "FW-E07, FW-E11, FW-E10 (full speed in H1 and H2)",'''
FANLINE_NEW = '''starts, under U42's least limit 1.471 A (DRAFTED under (B1)); under L4-E11 section 18 (b929d8be, PROVISIONAL) Q9 and Q10 are
        open-drain drivers of four-wire fans on +12V_FAN, the ramp a PWM-duty ramp, never while U12 or U22 starts", firmware:
        "FW-E07, FW-E11, FW-E10 (full speed in H1 and H2)",'''
U34_LINE_START = "    U34_restart_guard: {"
U22_LINE = '''\
    U22_RUN_12V_FAN: {reset: "DRAFTED by L4-E11 section 18 at b929d8be (not in this tree; PROVISIONAL until its release): U22's RUN
        divider R103 1.5M over R104 255k, on at 8.33 V of VSYS_E (7.98 to 8.67 V) and off at 6.89 V (6.55 to 7.23 V); a 9 ms soft
        start", default: "+12V_FAN up whenever VSYS_E is over 8.33 V", cable_out: "n/a: board E's own rail; with the dock's pin 1
        open VSYS_E and +12V_FAN are down", firmware: "none (hardware); FW-E11 sequences the fans' PWM after the rail is up",
        source: "L4-E11 18a (v2/docs/records/l5r2/inputs/l4e11-section-18-b929d8be.md)"}
'''
VSYSDOCK_OLD = '''under its limit), FW-C14", source: "L4-E11 16e, 17a; IF-AE-DOCK pin1_vsys_dock"}'''
VSYSDOCK_NEW = '''under its limit), FW-C14", source: "L4-E11 16e, 17a; IF-AE-DOCK pin1_vsys_dock; round 2: the branch 1.3208 A declared
        with the fans on U22's +12V_FAN (L4-E11 18b at b929d8be, DRAFTED, PROVISIONAL)"}'''

# The anchors L4-E11's apply_pcb_interfaces_dock.py needs: each must still occur exactly once after this script.
DOCK_DRAFT_ANCHORS = [
    'aliases: [["DOCK_SPARE", "BLK_SPARE"], ["CELL+", "CELL_F", "E\'s pack positive after its F3 blade"]]',
    "pins: {1: GND, 2: GND, 3: GND, 4: GND, 5: GND, 6: GND, 7: GND, 8: SHORE_INHIBIT, 9: USB_E6_P,",
    'the control line since, beside 5 to 7 and 11"',
    'charge_share: "BAT-F06, taken by the session under the owner\'s standing rule (ARCHITECTURE.md section 4.4): board E\'s',
    "findings: [R4A-N13, R4A-N12, R8E-N01, EQ-16, W3DE-DOCK-R1, A04-D2, W3-F09, BAT-F06, PWR-F12]",
]
PASS2 = ["title", "kind", "ends", "harness", "levels", "current", "default_state", "sequencing", "mating", "hot_plug", "judged_by",
         "tbd", "findings", "serves"]


def flat(s):
    return " ".join(str(s).split())


def leaves(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from leaves(v)
    elif isinstance(o, list):
        for v in o:
            yield from leaves(v)
    elif o is not None:
        yield flat(o)


def block_span(text, cid):
    """[start, end) of a contract block: from its key line to the next contract's key line (or the section comment after it)."""
    key = "    %s:\n" % cid
    if text.count(key) != 1:
        refuse("%s's key line occurs %d times" % (cid, text.count(key)))
    i = text.index(key)
    m = re.compile(r"^    (IF-[A-Z0-9-]+):\n|^    # =", re.M).search(text, i + len(key))
    if not m:
        refuse("no block after %s" % cid)
    return i, m.start()


def patch_yaml(t):
    import yaml
    if "LAYER 5'S SECOND ROUND" in t or "IF-A-CHASSIS:" in t:
        refuse("already applied (the round's header or IF-A-CHASSIS is present)")
    old_doc = yaml.safe_load(t)
    old_cs = old_doc["board_to_board"]["contracts"]
    new = t
    for cid in NEW_BLOCKS:
        i, j = block_span(new, cid)
        nb = NEW_BLOCKS[cid]
        if not nb.startswith("    %s:\n" % cid):
            refuse("%s's new block does not start with its key" % cid)
        new = new[:i] + nb + new[j:]
    for cid, blk in (("IF-E-FANS", FANS_NEW), ("IF-B-FANS", BFANS_NEW)):
        i, j = block_span(new, cid)
        new = new[:i] + blk + new[j:]
    for what, old, rep in (("the header", Y_HEADER_OLD, Y_HEADER_NEW), ("E5's end", E5_END_OLD, E5_END_NEW),
                           ("pin1_vsys_dock's end", PIN1_END_OLD, PIN1_END_NEW), ("IF-AE-DOCK's not_judged", DOCK_NJ, DOCK_GND + DOCK_NJ),
                           ("IF-EXT-DC's grounding", DC_GND_OLD, DC_GND_NEW), ("IF-EXT-ETH's grounding", ETH_GND_OLD, ETH_GND_NEW),
                           ("IF-EXT-ETH's tbd", ETH_TBD_OLD, ETH_TBD_NEW), ("IF-EXT-ETH's findings", ETH_FIND_OLD, ETH_FIND_NEW),
                           ("the fans' power line", FANLINE_OLD, FANLINE_NEW), ("VSYS_DOCK's power line", VSYSDOCK_OLD, VSYSDOCK_NEW),
                           ("U34's power line", U34_LINE_START, U22_LINE + U34_LINE_START)):
        if new.count(old) != 1:
            refuse("%s: the old text occurs %d times, not once" % (what, new.count(old)))
        new = new.replace(old, rep)
    if new.count(SLOT_OLD_START) != 1 or new.count(SLOT_OLD_END) != 1:
        refuse("SLOT_EN1..3's power line is not where it was")
    i, j = new.index(SLOT_OLD_START), new.index(SLOT_OLD_END)
    new = new[:i] + SLOT_NEW + new[j:]
    if new == t:
        refuse("the result does not differ")
    try:
        doc = yaml.safe_load(new)
    except yaml.YAMLError as e:
        refuse("the result does not load as YAML: %s" % e)
    cs = doc["board_to_board"]["contracts"]
    # NO LOSS: every string and number of each replaced first-twelve block is found in its new block
    for cid in NEW_BLOCKS:
        nl = list(leaves(cs[cid]))
        lost = [x for x in leaves(old_cs[cid]) if not any(x in y for y in nl)]
        if lost:
            refuse("%s loses %d leaf(s) of its old block, the first %r" % (cid, len(lost), lost[0][:80]))
        if any(k not in cs[cid] for k in PASS2):
            refuse("%s lacks a pass-2 field: %s" % (cid, [k for k in PASS2 if k not in cs[cid]]))
        for e in cs[cid]["ends"]:
            if "board" in e and not e.get("part"):
                refuse("%s: a board end has no part" % cid)
        if cs[cid].get("pins") != old_cs[cid].get("pins"):
            refuse("%s's pins map moved" % cid)
    if cs["IF-AE-DOCK"]["pins"] != old_cs["IF-AE-DOCK"]["pins"]:
        refuse("IF-AE-DOCK's pins map moved")
    for a in DOCK_DRAFT_ANCHORS:
        if new.count(a) != 1:
            refuse("L4-E11's dock draft anchor no longer occurs once: %r" % a[:60])
    pls = doc["board_to_board"]["power_line_states"]
    if "2.547" not in pls["SLOT_EN1..3"]["hold"] or "0.266" not in pls["SLOT_EN1..3"]["hold"] or "U22_RUN_12V_FAN" not in pls:
        refuse("the power lines are not restated")
    if set(old_cs) - set(cs) or set(cs) - set(old_cs) != {"IF-A-CHASSIS"}:
        refuse("the contract set changed other than by IF-A-CHASSIS")
    return new


# ====================================================================================================== HW-FW-CONTRACT.md
H_VER_ANCHOR = "differs; section 4.1 lists the drafts by the rows they move. Nothing here has been built, powered or measured.\n"
H_VER_ADD = H_VER_ANCHOR + """
**Version 2, round 2 (3 October 2026, record `v2/docs/records/l5r2/`).** FW-C02, FW-C01's step 6, FW-C14's start-up read, section
9's open item and V-C02 take the SLOT_EN keeper drafted by record l8gnd at `226e9143` (its sections 3f and 3h); FW-E07 and FW-E11
take the mixers' regulated +12V_FAN rail drafted by L4-E11 section 18 at `b929d8be` (and FW-E11 names U42's ILIM resistor R228, as
L4-E11 renamed it at `787e7b15`). Neither commit is in this branch's history: their sections are copied into the record's
`inputs/`, and every row resting on them reads DRAFTED and PROVISIONAL until their release.
"""
C01_OLD = "6. SLOT_EN1..3 one at a time."
C01_NEW = ("6. SLOT_EN1..3 one at a time, each after the keeper's held level has been read and adopted (FW-C02; with the hold applied, "
           "record l8gnd).")
C14_OLD = "held high, start under the TMP117's two steps."
C14_NEW = ("held high, start under the TMP117's two steps. With the SLOT_EN hold applied (FW-C02, record l8gnd, DRAFTED): a slot "
           "found held up at boot is acted on by the same rules once the line's state is known: held low, PI_KILL; at 5 Hz, H1's "
           "shutdown of that slot.")
SEC9_OLD = "- The SLOT_EN hold across a panel reset (FW-C02) is not drawn; while it is not, a panel reset powers off every module."
SEC9_NEW = ("- The SLOT_EN hold is drafted on board A (record l8gnd at `226e9143`, U43 and R230 to R232; PROVISIONAL until its "
            "release), not applied; until applied a panel reset powers off every module.")
FW_C02 = ("| FW-C02 | RP2040 watchdog; SLOT_EN held low by A's R30, R34, R38 (100 k) and the pad pull-downs. DRAFTED by record l8gnd at "
          "`226e9143` (`records/l5r2/inputs/l8gnd-sections-2-3-226e9143.md` 3a to 3f; not applied, PROVISIONAL until its release): "
          "SLOT_EN1..3 held at their last driven level across a panel reset by board A's keepers U43 (SN74LVC08A) with R230 to R232 "
          "(4.7 k), under R30, R34, R38 and the pad pull-downs (the hold of ARCHITECTURE.md 4.3): held high at least 2.547 V, held "
          "low at most 0.266 V (l8gnd 3b) | Hardware watchdog on, with PADS_BANK0, IO_BANK0 and SIO excluded from its reset scope "
          "(PSM and RESETS WDSEL), boot reason logged; update by SWD or in-application, never through the ROM bootloader while slots "
          "run. With the hold applied: at boot, before the GPIO13 to 15 pads are made outputs, read each as an input (the pull-down "
          "may stay on: a held high reads at least 2.55 V) and drive it at the level read, so a reset never glitches a running slot; "
          "then FW-C01's order applies to every slot read low. A wipe pending or ZEROIZE_SW closed at boot drives all three low "
          "first (D-03). The watchdog scope rule stays | a pad reset drops every slot (W5-F4); the SLOT_EN hold across a panel reset "
          "is not drawn; with the keeper it survives a RUN, SWD or ROM-bootloader reset and a brownout that resets the RP2040 while "
          "IOVDD stays up, not a loss of the panel's supply nor PI_KILL (l8gnd 3d) | V-C02 | FIRMWARE; the hold DRAFTED (record "
          "l8gnd), not applied |")
V_C02 = ("| V-C02 | FW-C02 | watchdog reset with three slots running: no slot rail drops. With the hold applied (record l8gnd 3h): "
         "watchdog reset, RUN reset and SWD reset with three slots running, and the panel's firmware reloaded by SWD: no slot rail "
         "drops; each SLOT_EN read on a scope at or above 2.5 V throughout (the held high); then a MAIN tap and PI_KILL: every rail "
         "off, and at the next MAIN every SLOT_EN at 0 V before the panel runs |")
FW_E07_OLD = "| FW-E07 | mixer fans on `E:J_FAN1`, `J_FAN2` (CELL_F, low-side switch, tachometer): PWM GPIO8, 9; tach GPIO10, 11 |"
FW_E07_NEW = ("| FW-E07 | mixer fans on `E:J_FAN1`, `J_FAN2` (CELL_F, low-side switch, tachometer): PWM GPIO8, 9; tach GPIO10, 11; "
              "DRAFTED by L4-E11 section 18 at `b929d8be` (PROVISIONAL until its release): four-wire fans (12 V, GND, PWM, TACH) "
              "on +12V_FAN from U22, Q9 and Q10 open-drain drivers of the fans' PWM inputs, D7 and D8 removed |")
FW_E11 = ("| FW-E11 | the mixer fans, Sanyo Denki 9WL0612P4H001 (D-18, record l7pwr: 12 V, 10.8 to 13.2 V, 0.17 A; the start current "
          "and the PWM input level NOT READ), on `E:J_FAN1`, `J_FAN2` (FW-E07): DRAFTED by L4-E11 section 18 at `b929d8be` "
          "(`records/l5r2/inputs/l4e11-section-18-b929d8be.md`; not in this tree, PROVISIONAL until its release) on the regulated "
          "+12V_FAN from U22 LTC3115EFE-1 (9 ms soft start; RUN on at 8.33 V and off at 6.89 V of VSYS_E) on VSYS_E behind board A's "
          "eFuse U42 TPS16630 (I(OL) 1.4713 to 1.8018 A at R228 11.0 kOhm, renamed from R221 by L4-E11 at `787e7b15`; DRAFTED R-177, "
          "R-181), with U12's 0.8 A on the same feed, the branch 1.3208 A declared; Q9, Q10 open-drain drivers of the fans' PWM "
          "inputs (GPIO8, 9); tach GPIO10, 11 | Start the mixer fans one at a time, each by a PWM-duty ramp into the fan's PWM input, "
          "never both within 1 s and never while U12 or U22 starts (E11-39, R-188; L4-E11 18c); with one fan running and U12 on, U42 "
          "leaves 0.1504 A of room, 1.21 W at the rail for the other fan's start (18b); a fan whose measured start would exceed it is "
          "not fitted (E11-35, R-179); a stall reported within 5 s (FW-E07); in H1 and H2 full speed (FW-E10) | a fan start that "
          "trips U42 drops board E's whole auxiliary domain for 500 to 800 ms, which board A reads as HOT-R1 lost; with U22 a fan "
          "fault lets VSYS_E fall only to U22's disable, a rail hiccup and not a controller reset (18a, INFERRED) | V-E11 (R-188's "
          "acceptance: one fan ramping at a time, the other and U12 settled, the current through J_DOCK pin 1 under 1.471 A at every "
          "start, on E11-38's specimen or the first prototype); R-184 (f) | FIRMWARE; DRAFTED (R-177, R-181; the rail L4-E11 section "
          "18 at `b929d8be`); PROVISIONAL: the start current NOT READ (E11-35, R-179), the PWM input level NOT READ (F-L7-11), U42's "
          "limit read outside 1.471 to 1.802 A (E11-38) re-derives the rule |")
SEC41_ANCHOR = "| the SGP41's load switch and its carrier TMP117 (L4-E12 section 6; no draft) | FW-E12, V-E12 |"
SEC41_ROWS = [
    ("| record l8gnd at `226e9143` (copied into `records/l5r2/inputs/`): the SLOT_EN keepers U43 with R230 to R232 "
     "(`apply_gen_sch_a_hotr1.py`); GND-002's R229 and H1 on board A (`apply_gen_sch_a_gnd002.py`) and C33 and J_ETH SH to CHASSIS on "
     "board B (`apply_gen_sch_b_gnd002.py`) | FW-C01, FW-C02, FW-C14, V-C02 (and `pcb_interfaces.yaml` IF-BC-PANEL, IF-AB-RIBBON, "
     "IF-EXT-ETH, IF-A-CHASSIS) | the hold across a panel reset and the one chassis bond; as generated a panel reset drops every "
     "module and GND-002 reads NOT DRAWN |"),
    ("| L4-E11 section 18 at `b929d8be` (copied into `records/l5r2/inputs/`): U22 LTC3115EFE-1 and +12V_FAN, four-pin J_FAN1 and "
     "J_FAN2 (`apply_gen_sch_e_aux.py` rewritten) | FW-E07, FW-E11, V-E11 (and IF-E-FANS, IF-AE-DOCK pin1_vsys_dock) | the mixers on a "
     "regulated 12.0 V, the branch 1.3208 A; as generated the fans sit on CELL_F, over their 13.2 V |"),
]
H_LOG = ("| 2 (L5-R2) | 3 October 2026 | By Layer 5's second round (MESHSAT-1357, `records/l5r2/`): FW-C02, FW-C01's step 6, "
         "FW-C14's start-up read, V-C02 and section 9's open item take record l8gnd's SLOT_EN keeper (DRAFTED, PROVISIONAL); FW-E07 "
         "and FW-E11 take L4-E11 section 18's +12V_FAN (DRAFTED, PROVISIONAL), FW-E11's ILIM resistor R228; two rows in section 4.1; "
         "the version paragraph |")


def cells(line):
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return None
    return [c.strip() for c in s[1:-1].split("|")]


def patch_hwfw(t):
    if "| 2 (L5-R2) |" in t or "Version 2, round 2" in t:
        refuse("already applied")
    lines = t.split("\n")

    def idx(first):
        hits = [i for i, l in enumerate(lines) if (cells(l) or [""])[0] == first]
        if len(hits) != 1:
            refuse("row %s occurs %d times" % (first, len(hits)))
        return hits[0]
    w6 = len(cells(lines[idx("FW-C02")]))
    w3 = len(cells(lines[idx("V-C02")]))
    for r_ in (FW_C02, FW_E11):
        if len(cells(r_)) != w6:
            refuse("a contract row lacks the table's %d cells" % w6)
    if len(cells(V_C02)) != w3:
        refuse("V-C02 lacks the table's cells")
    lines[idx("FW-C02")] = FW_C02
    lines[idx("V-C02")] = V_C02
    lines[idx("FW-E11")] = FW_E11
    k = len(lines) - 1
    while k >= 0 and not lines[k].strip():
        k -= 1
    if not (cells(lines[k]) or [""])[0].startswith("2 (L5-PWR)") or len(cells(H_LOG)) != len(cells(lines[k])):
        refuse("the change record's last row is not the first round's")
    lines.insert(k + 1, H_LOG)
    out = "\n".join(lines)
    for what, old, rep in (("the version anchor", H_VER_ANCHOR, H_VER_ADD), ("FW-C01's step 6", C01_OLD, C01_NEW),
                           ("FW-C14's start-up read", C14_OLD, C14_NEW), ("section 9's line", SEC9_OLD, SEC9_NEW),
                           ("FW-E07's hardware cells", FW_E07_OLD, FW_E07_NEW)):
        if out.count(old) != 1:
            refuse("%s occurs %d times, not once" % (what, out.count(old)))
        out = out.replace(old, rep)
    ls = out.split("\n")
    hits = [i for i, l in enumerate(ls) if l.startswith(SEC41_ANCHOR)]
    if len(hits) != 1:
        refuse("section 4.1's last row is not where it was")
    w = len(cells(ls[hits[0]]))
    for r_ in SEC41_ROWS:
        if len(cells(r_)) != w:
            refuse("a section 4.1 row lacks the table's cells")
    ls[hits[0] + 1:hits[0] + 1] = SEC41_ROWS
    out = "\n".join(ls)
    width, seen = None, set()
    for l in out.split("\n"):
        c = cells(l)
        if c is None:
            width = None
            continue
        if width is None:
            width = len(c)
        elif len(c) != width and not all(x.strip("-") == "" for x in c):
            refuse("a table row has %d cells under a header of %d: %s" % (len(c), width, l[:60]))
        if re.match(r"^(FW|V)-[A-Z]\d\d$", c[0]):
            if c[0] in seen:
                refuse("row %s occurs twice" % c[0])
            seen.add(c[0])
    return out


KINDS = {"pcb_interfaces.yaml": patch_yaml, "HW-FW-CONTRACT.md": patch_hwfw}


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
