"""Round-2 patch of drafts/w1-requirements.yaml: replace named records, append new ones. Run once; it
asserts every target exists and that the result re-parses."""
import re, sys, yaml, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(root, "drafts/w1-requirements.yaml")
text = open(path, encoding="utf-8").read()


class D(yaml.SafeDumper):
    pass


def _list(dumper, data):
    flow = all(isinstance(x, (str, int, float)) for x in data) and sum(len(str(x)) + 2 for x in data) < 90
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=flow)


D.add_representer(list, _list)


def block(rec):
    s = yaml.dump([rec], Dumper=D, sort_keys=False, width=150, allow_unicode=True, default_flow_style=False)
    lines = s.rstrip("\n").split("\n")
    return "\n".join(lines) + "\n"


def replace(cid, rec):
    global text
    m = re.search(r"^- id: %s\n(?:(?!^- id: |^# ).*\n?)*" % re.escape(cid), text, re.M)
    assert m, cid
    body = m.group(0)
    trail = body[len(body.rstrip("\n")):]
    text = text[:m.start()] + block(rec) + trail[1:] + text[m.end():]


R = {}

R["CAND-002"] = dict(
    id="CAND-002", **{"class": "implementation_choice"}, parent="NEED-02",
    statement="The device set is the owner's ruling of 6 September 2026: CM5 8 GB / 64 GB wireless; RockBLOCK 9704 SMA with the Maxtena helical; 5G on M.2 B-key (RM520N-GL); E22-900M30S LoRa; two E72 CC2652P; AW7915-AED WiFi link cards; SA868 with a RA30H1317M1 30 W stage; LimeSDR Mini 2.4; Xenarc 709GNK; PDi E2370KS0C1; LG290P GNSS; QMX HF; BME688 inside and in the outside pod, SGP41 in the battery bay (32.54).",
    acceptance="Every listed device appears in the generated schematic of its board with the ordered part number (checked against the BOM), or as a named receptacle device where it is not soldered; every socket or land matches the device's own key and drawing.",
    allocated_to=["b", "c", "d", "a", "e", "kit"], verification_method=["SCRIPT", "MANUAL_REVIEW"],
    verification_phase="SCHEMATIC", rules=["CMP-002", "SUP-001"], rule_coverage="PARTIAL",
    source=["v2/docs/MESHSAT-709-geometry-appendix.md:2756-2771", "v2/docs/MESHSAT-709-geometry-appendix.md:2813-2816",
            "v2/docs/MESHSAT-709-geometry-appendix.md:2896 (32.54 sensor picks)", "v2/docs/V2-SPEC.md:37-51"],
    source_check="VERIFIED",
    notes="Owner rulings bind the picks; changing one is an owner decision. Round 2: two picks are not what the generators carry: the SGP41 is in no generator (C-05), and the 5G socket bought (TE 1-2199119-5, LCSC C574849) is key M while the RM520N-GL is key B (C-19, adjudication A08).")

R["CAND-024"] = dict(
    id="CAND-024", **{"class": "requirement"}, parent="NEED-05",
    statement="The kit runs from its internal 4S pack for a stated minimum time in stated power states at a stated temperature and pack age.",
    acceptance="TBD (owner, D-06). PROVISIONAL figures for the 4S3P 18650 pack that is expected to fit (CONOPS section 4a): PS-IDLE-SPEC 4.2 h new and 3.4 h aged; PS-TYP 2.2 h new and 1.8 h aged, at +20 C. None is a requirement.",
    tbd_effect="Pack configuration, mass, the M1 energy balance with solar and the charge time wait on the target; the 4S4P columns describe a configuration not shown to fit (A06).",
    allocated_to=["p", "a", "e", "kit", "owner"], verification_method=["CALCULATION", "PROTOTYPE_MEASUREMENT"],
    verification_phase="SCHEMATIC", final_phase="PROTOTYPE", rules=[], rule_coverage="NONE",
    source=["v2/docs/MESHSAT-709-geometry-appendix.md:3056 (research gate: 4S, about 100 to 150 Wh)", "v2/docs/MESHSAT-709-geometry-appendix.md:3062", "v2/docs/MESHSAT-709-geometry-appendix.md:2846", "v2/docs/CONOPS.md section 4a"],
    source_check="INFERRED",
    notes="Round 2: the round-1 '200 Wh / 50 W = about 4 h' is withdrawn. The per-state figures are the foundation power budget (adjudication A05), arithmetic over datasheet figures, generator declarations and placeholders; 12.2 of PS-IDLE's 29.4 W and 29.7 of PS-TYP's 60.1 W are TBD.")

R["CAND-030"] = dict(
    id="CAND-030", **{"class": "derived_constraint"}, parent="NEED-05",
    statement="The pack, its board P, the heater mat and their mounting fit the east pocket, about 58 x 240 x 48 mm (X +120 to +178, Y -120 to +120), under board B's underside at Z 47.9.",
    acceptance="A named pack build (cells, wrap, board P position, mat, pads) fits with a stated clearance in every axis against the committed board B underside and the case CAD, and against the measured case (D-08).",
    allocated_to=["p", "case", "b"], verification_method=["CALCULATION", "MANUAL_REVIEW", "PROTOTYPE_MEASUREMENT"],
    verification_phase="PLACED_BOARD", final_phase="ASSEMBLY", rules=["MEC-001"], rule_coverage="PARTIAL",
    source=["v2/docs/MESHSAT-709-geometry-appendix.md:3060-3062", "v2/docs/ASSEMBLY.md section 3"],
    source_check="INFERRED", conflict_ref="C-11",
    notes="Adjudication A06 (box reading of B21's underside): 4S3P 18650 fits east, shrink-wrapped, with 1.35 mm spare across the pocket (less than the case wall uncertainty); 4S2P 21700 is marginal; no 4S4P fits either pocket with board P beside the cells; pack_4s.py's walled box does not fit; nothing fits the west pocket, so 32.62's second pack there is not available as drawn.")

R["CAND-031"] = dict(
    id="CAND-031", **{"class": "requirement"}, parent="NEED-05",
    statement="Every transmitter may key at the same time: no transmit serialisation is required of the hardware (the bridge may keep one as a receiver-protection preference).",
    acceptance="PS-ALLTX (about 227 W at the battery with the outlets off, PROVISIONAL) is supplied with every rail in regulation for a stated duration down to a stated state of charge; the duration and the charge floor are TBD (owner, D-11).",
    tbd_effect="At 2.5 V per cell the node is 10 V and 227 W needs about 23 A at the pack, above the 18 A declared peak and the gauge's 20 A (2 s) trip; with the ~145 Wh pack that fits (A06) the headroom at low charge is smaller than W2's 4S4P case assumed. Either the duration, the charge floor, the thresholds or a load-shed rule moves.",
    allocated_to=["a", "p", "e", "e5", "owner"], verification_method=["CALCULATION", "PROTOTYPE_MEASUREMENT"],
    verification_phase="SCHEMATIC", final_phase="PROTOTYPE", rules=["PWR-001", "PI-002", "BAT-002"], rule_coverage="PARTIAL",
    source=["v2/docs/MESHSAT-709-geometry-appendix.md:2337", "v2/docs/MESHSAT-709-geometry-appendix.md:2465",
            "v2/docs/MESHSAT-709-geometry-appendix.md:2846", "v2/ecad/tools/pcb_energy_chain.yaml:48-49", "v2/docs/TEST-PLAN.md:64-66"],
    source_check="INFERRED", conflict_ref="C-21",
    notes="The ruling was made for the 1S node of 4 September and has not been re-stated for the 4S node, so it stands until the owner says otherwise (D-11). The outlet interlock is the session's (S-14).")

R["CAND-032"] = dict(
    id="CAND-032", **{"class": "assumption"}, parent="NEED-05",
    statement="The power budget of 32.52 item 3 is a battery-side design estimate: its listed loads sum to 45.0 W typical and 178 W peak, and with the 12 % allowance give 50.4 W and 199 W, the record's 'about 50 W' and 'about 200 W'; the 'up to 290 W' adds 90 W of outlets without the allowance. No figure is measured.",
    acceptance="Superseded for design use by the per-state budget of CONOPS section 4a (PROVISIONAL), then by prototype measurement.",
    allocated_to=["a", "kit"], verification_method=["CALCULATION", "PROTOTYPE_MEASUREMENT"],
    verification_phase="SCHEMATIC", final_phase="PROTOTYPE", rules=["PWR-001"], rule_coverage="PARTIAL",
    source=["v2/docs/MESHSAT-709-geometry-appendix.md:2846", "v2/docs/MESHSAT-709-geometry-appendix.md:2932"],
    source_check="VERIFIED",
    notes="Round 2 (challenger, adjudication A05): round 1 said the reference point was not stated; the arithmetic answers it. One line item is above its datasheet: RockBLOCK 0.5 / 5 W against 60 mW idle, 1.4 W max (rb9704-datasheet-RB9704-001-JUN26.pdf).")

R["CAND-049"] = dict(
    id="CAND-049", **{"class": "conflict"}, parent="NEED-07",
    statement="The envelope's hot end is set by the Sensirion SGP41 battery-bay sensor (-20 to +55 C), which appendix 32.54 picked for the battery bay beside the BME688 inside and in the pod; no generator fits the SGP41.",
    acceptance="The SGP41 is fitted where the battery bay's air is sampled, or an owner ruling drops it; the envelope's hot end is not recomputed until one of the two happens.",
    allocated_to=["e", "p", "kit"], verification_method=["SCRIPT", "MANUAL_REVIEW"],
    verification_phase="SCHEMATIC", rules=["ENV-001", "CMP-001", "CMP-002"], rule_coverage="PARTIAL",
    source=["v2/docs/MESHSAT-709-geometry-appendix.md:2896 (32.54)", "v2/docs/OPERATING-ENVELOPE.md:42",
            "v2/docs/OPERATING-ENVELOPE.md:82-83", "v2/ecad/tools/gen_sch_e.py:367-369", "v2/docs/V2-SPEC.md:86"],
    source_check="VERIFIED", conflict_ref="C-05",
    notes="Round 2 (challenger): round 1 treated the omission as the design and proposed recomputing the hot end from the BME688; withdrawn.")

R["CAND-051"] = dict(
    id="CAND-051", **{"class": "requirement"}, parent="NEED-08",
    statement="One operator action (the EMCON locking toggle) silences every transmitter in the kit through a hardware line that needs no processor, and the line reads 'inhibited' when the panel ribbon is disconnected or a board is unpowered.",
    acceptance="(1) Netlist: every transmitter in the CONOPS section 4b table has a supply, enable or disable pin driven by EMCON_HW or TX_INHIBIT_n, and the rule instrument enumerates them (RF-002 fails on any radio without one). (2) Bench: with EMCON closed and every processor held in reset, no emission at any antenna port above a threshold TBD, measured per TEST-PLAN; the same with the ribbon unplugged; the two WiFi link cards shown RF-silent with W_DISABLE1# low, or their supplies gated.",
    tbd_effect="The bench pass line has no number; RF-002 reads PASS today while three CM5 radios and possibly two WiFi cards are not silenced (C-03, C-28).",
    allocated_to=["a", "b", "c", "d", "kit"], verification_method=["SCRIPT", "PROTOTYPE_MEASUREMENT"],
    verification_phase="SCHEMATIC", final_phase="PROTOTYPE", rules=["RF-002", "SCH-004", "SCH-003"], rule_coverage="PARTIAL",
    source=["v2/docs/MESHSAT-709-geometry-appendix.md:2787 (item 3)", "v2/docs/PANEL.md:110-111", "v2/docs/TEST-PLAN.md:46",
            "v2/docs/PCB-RULE-STATUS-B.md:53", "v2/ecad/tools/pcb_rules_coverage.yaml:607-615"],
    source_check="VERIFIED", conflict_ref="C-03")

R["CAND-052"] = dict(
    id="CAND-052", **{"class": "conflict"}, parent="NEED-08",
    statement="The three CM5 modules' own WiFi and Bluetooth radios are disabled only through the PCA9555 expander U6 on the kit I2C bus (software), not by EMCON_HW; and U6 drives pins the CM5 datasheet allows only to be driven low, from an always-on rail, so it can back-feed an unpowered module.",
    acceptance="No driver sources current into WL_nDIS1..3 or BT_nDIS1..3: each is pulled low through open-drain elements released only when both the software control and EMCON_HW are high; U6's output and its internal pull-up never reach the CM5 pin.",
    allocated_to=["b"], verification_method=["SCRIPT", "MANUAL_REVIEW"],
    verification_phase="SCHEMATIC", rules=["RF-002", "PWR-002"], rule_coverage="PARTIAL",
    source=["v2/ecad/tools/gen_sch_b.py:378", "v2/ecad/tools/gen_sch_b.py:740-743",
            "v2/vendor/cm5/cm5-datasheet.pdf (release 3, sections 2.1.1, 2.1.2 and 3.1)",
            "v2/vendor/ti/ti-pca9555.pdf (SCPS131J section 8.1, Fig 8-2: internal pull-up on every I/O)"],
    source_check="VERIFIED", conflict_ref="C-03",
    notes="Round 2 (challenger): round 1 kept U6 push-pull 'for normal control'; withdrawn.")

R["CAND-054"] = dict(
    id="CAND-054", **{"class": "requirement"}, parent="NEED-08",
    statement="What the kit does while EMCON is closed: keep receivers listening where that can be done without any emission, or put every radio dark.",
    acceptance="TBD (owner, D-05). As generated (adjudication A11): power is removed from the LimeSDR, RockBLOCK, E22, both E72 and the QMX; the 5G module is in airplane mode (receive stops); the two WiFi cards get W_DISABLE1# with an unproven effect; only VHF keeps receiving; the CM5 radios are not gated.",
    tbd_effect="Mission M4 (listen under EMCON) is possible today only on VHF; a listening option needs design changes on boards A and B and a proof that each remaining transmit gate emits nothing.",
    allocated_to=["owner", "a", "b"], verification_method=["MANUAL_REVIEW"],
    verification_phase="SCHEMATIC", rules=["RF-002"], rule_coverage="PARTIAL",
    source=["v2/ecad/tools/gen_sch_b.py:724-728", "v2/ecad/tools/gen_sch_a.py:535-537", "v2/ecad/tools/gen_sch_d.py:270-287",
            "v2/docs/MESHSAT-709-geometry-appendix.md:2930", "v2/docs/PANEL.md:111"],
    source_check="VERIFIED", conflict_ref="C-20")

R["CAND-055"] = dict(
    id="CAND-055", **{"class": "conflict"}, parent="NEED-08",
    statement="PANEL.md section 7 says A22 pulls EMCON_HW HIGH through R102 and that a panel-less kit 'charges and computes'; the netlists pull EMCON_HW LOW (inhibited) and SLOT_EN1..3 LOW (no slot powers), and the charger does not charge a 4S pack without its host.",
    acceptance="PANEL.md section 7 matches the netlists and the charger's behaviour after the session fixes S-03, S-04 and S-08.",
    allocated_to=["a", "c"], verification_method=["SCRIPT", "MANUAL_REVIEW"],
    verification_phase="SCHEMATIC", rules=["DOC-002", "SCH-004"], rule_coverage="PARTIAL",
    source=["v2/docs/PANEL.md:130", "v2/docs/PANEL.md:110", "v2/ecad/tools/gen_sch_a.py:537",
            "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net (R102 pin 2 on GND; SLOT_EN pull-downs R30, R34, R38)"],
    source_check="VERIFIED", conflict_ref="C-04")

R["CAND-060"] = dict(
    id="CAND-060", **{"class": "requirement"}, parent="NEED-10",
    statement="A sealed case-open (tamper) switch under the frame logs lid events, senses the lid for the reduced mode, and feeds the ZEROIZE logic in the role the owner rules.",
    acceptance="The switch appears in a board netlist on an always-powered input (the approved floor plan sites it on E6), and the log records a lid event in the functional check, with the kit on and off; whether it triggers ZEROIZE or only logs is TBD (owner, D-03).",
    tbd_effect="No generator carries the switch today, so the functional check line 'the tamper switch logs the lid' cannot pass and the reduced mode has no lid sensor.",
    allocated_to=["e", "case", "fw_sensor"], verification_method=["SCRIPT", "PROTOTYPE_MEASUREMENT"],
    verification_phase="SCHEMATIC", final_phase="PROTOTYPE", rules=["SCH-004"], rule_coverage="PARTIAL",
    source=["v2/docs/MESHSAT-709-geometry-appendix.md:2790 (item 6)", "v2/docs/MESHSAT-709-geometry-appendix.md:2848 (E6: the tamper switch input)",
            "v2/docs/V2-SPEC.md:34", "v2/docs/TEST-PLAN.md:46"],
    source_check="VERIFIED", conflict_ref="C-10",
    notes="grep of v2/ecad/tools/gen_sch_*.py for tamper, case-open, lid and reed returns nothing. Implementation is the session's (S-11); round 1 wrongly listed the function as an owner question.")

R["CAND-064"] = dict(
    id="CAND-064", **{"class": "requirement"}, parent="NEED-11",
    statement="A second time source (DCF77, 77.5 kHz) and a holdover clock keep time when GNSS is lost.",
    acceptance="Holdover drift per day TBD; the DCF77 time reaches every running module (as a pulse, per V2-SPEC, or through the sensor controller, per the generator: C-26).",
    tbd_effect="No holdover accuracy target, so the RTC choice (DS3231M on the kit I2C bus) cannot be judged against 32.50 item 11's 'TCXO-disciplined RTC fed by the LG290P pulse'; DCF77 is receivable only within its transmitter's range (inferred), which is a market question.",
    allocated_to=["b", "e", "sw"], verification_method=["MANUAL_REVIEW", "PROTOTYPE_MEASUREMENT"],
    verification_phase="SCHEMATIC", final_phase="PROTOTYPE", rules=["CLK-001"], rule_coverage="PARTIAL",
    source=["v2/docs/MESHSAT-709-geometry-appendix.md:2795-2797 (items 11 and 13)", "v2/docs/PANEL.md:127", "v2/docs/V2-SPEC.md:35",
            "v2/ecad/tools/gen_sch_e.py:349", "v2/ecad/tools/gen_sch_e.py:381"],
    source_check="VERIFIED", conflict_ref="C-26",
    notes="Round 2 (challenger): round 1 adopted the generator's routing silently; the conflict is now recorded.")

R["CAND-066"] = dict(
    id="CAND-066", **{"class": "requirement"}, parent="NEED-12",
    statement="Water on the case floor, and hydrogen or VOC in the battery bay, raise an alarm and shut the pack down.",
    acceptance="Thresholds TBD; the sensor for the battery bay is the SGP41 picked in 32.54 (whether it answers to hydrogen at the relevant levels is TBD); the path from the sensor to the device that opens the pack (the gauge's discharge FET, or another) TBD.",
    tbd_effect="No hardware path from the sensor controller to pack shutdown is recorded; if it goes through the gauge's SMBus it is firmware-only, which bears on decision 40; if the SGP41 does not sense hydrogen, the approved hydrogen sensing has no part.",
    allocated_to=["e", "p", "fw_sensor"], verification_method=["SCRIPT", "VENDOR_CONFIRMATION", "PROTOTYPE_MEASUREMENT"],
    verification_phase="SCHEMATIC", final_phase="PROTOTYPE", rules=["BAT-001", "SCH-004"], rule_coverage="PARTIAL",
    source=["v2/docs/MESHSAT-709-geometry-appendix.md:2802 (sensors 2 and 4)", "v2/docs/MESHSAT-709-geometry-appendix.md:2896 (32.54)",
            "v2/docs/V2-SPEC.md:65", "v2/docs/OPERATING-ENVELOPE.md:141"],
    source_check="VERIFIED", conflict_ref="C-05")

R["CAND-071"] = dict(
    id="CAND-071", **{"class": "requirement"}, parent="NEED-13",
    statement="The cells are charged only between 0 and +45 C and discharged only between -10 and +60 C at the cell surface; below 0 C the pack is warmed by its heater mat before charge.",
    acceptance="TEST-PLAN section 5 rows 7 and 8 (chamber at -5 and +50 C with the charger live; -15 and +65 C under a 2 A load): the pack gauge's charge and discharge FETs follow the windows of pcb_pack_protection.yaml; the bridge's own hold clears above 3 C (PANEL.md section 10).",
    allocated_to=["p", "a", "e", "fw_panel"], verification_method=["SCRIPT", "PROTOTYPE_MEASUREMENT"],
    verification_phase="SCHEMATIC", final_phase="PROTOTYPE", rules=["BAT-001", "ENV-001"], rule_coverage="PARTIAL",
    source=["v2/docs/OPERATING-ENVELOPE.md:43-44", "v2/docs/TEST-PLAN.md:69-70", "v2/docs/PANEL.md:155",
            "v2/ecad/tools/pcb_pack_protection.yaml:142-157 (CHARGE_ and DISCHARGE_TEMPERATURE_WINDOW)"],
    source_check="VERIFIED",
    notes="Round 2: the charger BQ25731 has no thermistor input (SLUSE66A pin table, adjudication A02), so the charge window is the gauge's alone. The cold-soak start-up case (round 1 C-14) is owner question D-02d; C-14 is withdrawn as a conflict.")

R["CAND-072"] = dict(
    id="CAND-072", **{"class": "conflict"}, parent="NEED-13",
    statement="The pack headers say 'about 200 Wh' without naming the cell ('4S3P or 4S4P'; '4S4P 18650 or 4S3P 21700'); no 21700 cell sheet is held; and at most about 145 Wh is expected to fit (A06).",
    acceptance="One named cell and one parallel count, with the cell's own sheet in v2/vendor/battery/, used by the energy chain, the protection table, the runtime and the enclosure.",
    allocated_to=["p", "owner"], verification_method=["CALCULATION", "VENDOR_CONFIRMATION"],
    verification_phase="SCHEMATIC", rules=["BAT-001", "BAT-002"], rule_coverage="PARTIAL",
    source=["v2/docs/V2-SPEC.md:20", "v2/docs/MESHSAT-709-geometry-appendix.md:3062", "v2/ecad/tools/pcb_pack_protection.yaml:17-27",
            "v2/ecad/tools/pcb_energy_chain.yaml:46", "v2/ecad/tools/gen_sch_p.py:7"],
    source_check="INFERRED", conflict_ref="C-15",
    notes="Round 2 (challenger): 3P is the protection table's declared worst case (pcb_pack_protection.yaml:17-18), not 'a configuration nobody proposed'.")

R["CAND-084"] = dict(
    id="CAND-084", **{"class": "derived_constraint"}, parent="NEED-16",
    statement="The CM5's radio certification holds with Raspberry Pi's approved antenna kit; the kit carries that antenna through a blind-mate and a bulkhead (J_BM3, WIFI 2.4), and three wireless modules share one wall jack.",
    acceptance="TBD: which slot's radio feeds the wall jack, what the other two use (internal PCB antenna inside the sealed case, or disabled), and whether the cable path keeps the certification.",
    tbd_effect="Three transmitters have no stated antenna and no certification position.",
    allocated_to=["b", "a", "case", "owner"], verification_method=["MANUAL_REVIEW", "VENDOR_CONFIRMATION"],
    verification_phase="SCHEMATIC", rules=["RF-001"], rule_coverage="PARTIAL",
    source=["v2/vendor/cm5/cm5-datasheet.pdf (release 3: 'If you use a third-party antenna, you must obtain your own separate certification')",
            "v2/docs/MESHSAT-709-geometry-appendix.md:2718", "v2/docs/MESHSAT-709-geometry-appendix.md:2948", "v2/docs/MESHSAT-709-geometry-appendix.md:2764 (item 7)"],
    source_check="INFERRED", conflict_ref="C-17",
    notes="Round 2 (challenger): whether the intermediate path voids the certification is an inference; the datasheet does not say.")

R["CAND-090"] = dict(
    id="CAND-090", **{"class": "conflict"}, parent="NEED-07",
    statement="The reduced mode is 'one module' in the envelope (PS-RED, 19.7 W) and 'monitor off, cluster idle' in 32.53 (PS-RED-b, 25.4 W, both PROVISIONAL); its trigger is 'lid closed or above +35 C' but nothing in the generators senses the lid.",
    acceptance="One definition (which modules, which bearers, monitor state) and a named trigger source.",
    allocated_to=["owner", "sw", "fw_panel", "e"], verification_method=["MANUAL_REVIEW"],
    verification_phase="SCHEMATIC", rules=["ENV-001"], rule_coverage="PARTIAL",
    source=["v2/docs/OPERATING-ENVELOPE.md:100-101", "v2/docs/OPERATING-ENVELOPE.md:131-132", "v2/ecad/tools/pcb_envelope.yaml:30",
            "v2/docs/MESHSAT-709-geometry-appendix.md:2860"],
    source_check="VERIFIED", conflict_ref="C-16")

R["CAND-094"] = dict(
    id="CAND-094", **{"class": "conflict"}, parent="NEED-05",
    statement="Peak draw 'about 150 W with everything transmitting' (V2-SPEC, the one-module set of 32.49) against 'about 200 W peak without the outlets, up to 290 W with them' (32.52 item 3, battery-side) and the re-derived PS-ALLTX 227.0 W and PS-ALLTX-OUT 316.4 W (PROVISIONAL).",
    acceptance="V2-SPEC line 23 carries the current per-state figures, marked PROVISIONAL, once the owner has set the runtime target (D-06).",
    allocated_to=["kit"], verification_method=["CALCULATION"],
    verification_phase="SCHEMATIC", rules=["PWR-001"], rule_coverage="PARTIAL",
    source=["v2/docs/V2-SPEC.md:23", "v2/docs/MESHSAT-709-geometry-appendix.md:2775", "v2/docs/MESHSAT-709-geometry-appendix.md:2846"],
    source_check="VERIFIED", conflict_ref="C-01")

NEW = [
    dict(id="CAND-095", **{"class": "requirement"}, parent="NEED-19",
         statement="One deliberate, covered action (SOS closed 2 s) raises a distress or assistance alert; what it sends, over which bearers, to whom, and whether it may transmit while EMCON is closed are stated.",
         acceptance="TBD (owner, D-10). Once ruled: in the functional check, SOS closed 2 s produces the stated message on the stated bearers, MASTER WARN and the sounder pattern, and flipping back cancels, with the e-paper confirming both.",
         tbd_effect="The panel has the switch, the lamp and the sounder pattern but no defined action; if SOS may override EMCON, a hardware path through the EMCON gates is needed, which none of the boards has.",
         allocated_to=["c", "fw_panel", "sw", "owner"], verification_method=["MANUAL_REVIEW", "PROTOTYPE_MEASUREMENT"],
         verification_phase="SCHEMATIC", final_phase="PROTOTYPE", rules=[], rule_coverage="NONE",
         source=["v2/docs/PANEL.md:14", "v2/docs/PANEL.md:61", "v2/docs/PANEL.md:145", "v2/docs/PANEL.md:147", "v2/docs/PANEL.md:151", "v2/docs/V2-SPEC.md:58"],
         source_check="VERIFIED", conflict_ref="C-31"),
    dict(id="CAND-096", **{"class": "requirement"}, parent="NEED-18",
         statement="A ground stud on the case wall gives the kit one bonding point, and the RF arrestors and cable shields bond to it by a stated conductor.",
         acceptance="The stud appears in the case CAD and the connector plate; the bonding conductor from the arrestors and shields to the stud is named; which board net, if any, meets it is decided once (GND-002). TBD until GND-002 is decided.",
         tbd_effect="No board declares a chassis, shield or earth net (session memory, grounding census of 21 Sep 2026), so the arrestors have no earth path and the stud of 32.50 item 12 has no conductor.",
         allocated_to=["case", "a", "e"], verification_method=["MANUAL_REVIEW", "SCRIPT"],
         verification_phase="SCHEMATIC", final_phase="ASSEMBLY", rules=["GND-002"], rule_coverage="PARTIAL",
         source=["v2/docs/MESHSAT-709-geometry-appendix.md:2796 (32.50 item 12)"], source_check="VERIFIED"),
    dict(id="CAND-097", **{"class": "requirement"}, parent="NEED-03",
         statement="The panel controller supervises each slot: a slot whose heartbeat stays flat for 60 s after its rail came up is shown as a slot fault, power-cycled once (rail off 5 s), then left off until the operator acts.",
         acceptance="In the functional check, a slot with its heartbeat forced flat is flagged (MASTER CAUT, the e-paper names the slot), cycled once and left off; the other slots keep running.",
         allocated_to=["fw_panel", "a", "b", "c"], verification_method=["PROTOTYPE_MEASUREMENT"],
         verification_phase="PROTOTYPE", rules=[], rule_coverage="NONE",
         source=["v2/docs/PANEL.md:102"], source_check="VERIFIED"),
    dict(id="CAND-098", **{"class": "requirement"}, parent="NEED-18",
         statement="Conducted emissions and susceptibility on the power leads, bulk cable injection, radiated emissions and radiated susceptibility are tested to MIL-STD-461 methods (TEST-PLAN M1 to M5) against the limit curves of a stated edition and platform.",
         acceptance="TBD: the edition and platform curve (session, after the markets decision D-04 says whether any EMC claim is wanted). Until then every run is characterisation and supports no claim (ENV-002).",
         tbd_effect="Without a limit curve no M1 to M5 result can PASS or FAIL; no MIL-STD-461 edition is held in the tree.",
         allocated_to=["kit"], verification_method=["PROTOTYPE_MEASUREMENT"],
         verification_phase="PROTOTYPE", rules=["ENV-002", "EMC-001"], rule_coverage="PARTIAL",
         source=["v2/docs/MESHSAT-709-geometry-appendix.md:2804 (32.50 item 16e)", "v2/docs/TEST-PLAN.md section 3 (M1 to M5)"],
         source_check="VERIFIED"),
    dict(id="CAND-099", **{"class": "requirement"}, parent="NEED-06",
         statement="Deployed, the kit survives 6 hours of blowing dust with no dust inside, and its latches, pressure valve and connectors still operate.",
         acceptance="TEST-PLAN E8 (MIL-STD-810 method 510) at a laboratory; the functional check and the seal check pass afterwards.",
         allocated_to=["case", "kit"], verification_method=["PROTOTYPE_MEASUREMENT"],
         verification_phase="PROTOTYPE", rules=["REL-001", "ENV-002"], rule_coverage="PARTIAL",
         source=["v2/docs/TEST-PLAN.md:23"], source_check="VERIFIED",
         notes="E8's 'vent' is read as Peli's pressure valve, which 32.53 keeps (challenger); W5 settles the wording."),
    dict(id="CAND-100", **{"class": "assumption"}, parent="NEED-13",
         statement="The owner's 'MIL-STD if possible' for the pack (32.62) is met by qualifying the built pack with the kit under TEST-PLAN; no MIL-STD battery specification is claimed for the pack itself.",
         acceptance="The pack is fitted in the kit for every TEST-PLAN environmental test that the kit runs with its pack.",
         allocated_to=["p", "kit"], verification_method=["MANUAL_REVIEW", "PROTOTYPE_MEASUREMENT"],
         verification_phase="SCHEMATIC", final_phase="PROTOTYPE", rules=["ENV-002"], rule_coverage="PARTIAL",
         source=["v2/docs/MESHSAT-709-geometry-appendix.md:3056", "v2/docs/MESHSAT-709-geometry-appendix.md:3058", "v2/docs/V2-SPEC.md:20"],
         source_check="VERIFIED"),
    dict(id="CAND-101", **{"class": "requirement"}, parent="NEED-10",
         statement="Firmware integrity: what may run on the compute modules and on the controllers (the three I/O supervisors, the panel and sensor controllers) is protected against reflashing by an attacker with the kit in hand, to a stated level.",
         acceptance="TBD (owner, D-13: the level for the prototype, and whether a hardware-isolated root of trust is required, which decides the H753 against H743 mismatch).",
         tbd_effect="Encrypted drives without verified boot protect data at rest from a stolen kit, not from an attacker who reflashes a module; the H753/H743 part question stays open until the level is set (plan condition 1).",
         allocated_to=["b", "sw", "fw_ioctrl", "fw_panel", "fw_sensor", "owner"], verification_method=["MANUAL_REVIEW", "PROTOTYPE_MEASUREMENT"],
         verification_phase="SCHEMATIC", final_phase="PROTOTYPE", rules=[], rule_coverage="NONE",
         source=["v2/docs/RED-TEAM-2026-09-09.md:363 (S2)", "v2/ecad/tools/gen_sch_b.py:567-571 (J_FLASH, J_RPIBOOT, J_DBG per slot)"], source_check="VERIFIED"),
    dict(id="CAND-102", **{"class": "conflict"}, parent="NEED-11",
         statement="V2-SPEC says the DCF77 pulse is fanned out to every slot; the generator takes it only to the sensor controller RP2040 (GPIO6).",
         acceptance="The pulse reaches every slot, or V2-SPEC says the sensor controller serves DCF77 time over USB.",
         allocated_to=["b", "e"], verification_method=["SCRIPT", "MANUAL_REVIEW"],
         verification_phase="SCHEMATIC", rules=["SCH-003"], rule_coverage="PARTIAL",
         source=["v2/docs/V2-SPEC.md:35", "v2/ecad/tools/gen_sch_e.py:349", "v2/ecad/tools/gen_sch_e.py:353", "v2/ecad/tools/gen_sch_e.py:381"],
         source_check="VERIFIED", conflict_ref="C-26"),
    dict(id="CAND-103", **{"class": "conflict"}, parent="NEED-05",
         statement="Four documents credit the charger with hardware behaviour it does not have: charging with a crashed panel, a thermistor or JEITA input, and reading the pack gauge; as generated its cell-count strap selects 2S and the kit's loads sit behind its sense resistor.",
         acceptance="PANEL.md, OPERATING-ENVELOPE.md (with its pin re-set), the appendix entry that corrects 32.62, and CONOPS describe the charger as generated after the session fixes S-03 and S-04; a hostless kit's charge behaviour is stated and bench-confirmed.",
         allocated_to=["a", "fw_panel"], verification_method=["SCRIPT", "MANUAL_REVIEW", "PROTOTYPE_MEASUREMENT"],
         verification_phase="SCHEMATIC", final_phase="PROTOTYPE", rules=["DOC-002", "PWR-001"], rule_coverage="PARTIAL",
         source=["v2/docs/PANEL.md:128", "v2/docs/PANEL.md:155", "v2/docs/OPERATING-ENVELOPE.md:88-89", "v2/docs/MESHSAT-709-geometry-appendix.md:3062",
                 "v2/ecad/tools/gen_sch_a.py:350", "v2/vendor/ti/bq25731-datasheet.pdf (SLUSE66A)"],
         source_check="VERIFIED", conflict_ref="C-27",
         notes="Adjudication A02: the 256 mA hostless default rests on TI E2E 1316778 (23 Jan 2024), INFERRED with bench confirmation owed."),
    dict(id="CAND-104", **{"class": "conflict"}, parent="NEED-13",
         statement="The pack SMBus lead has no single connector: board P is JST-XH 1x4 (SMBC, SMBD, GND, PRES), board E is a 2.54 mm 1x6 pin header (two SMBus sections, no PRES), and ASSEMBLY.md names 'XH2.5 x 6'.",
         acceptance="Both ends are the same family, pitch and pin count, pin n meets pin n with clock, data and ground aligned, P's ground pin is on the pack side of the shunt, and check_contracts.py carries a J_SMB contract.",
         allocated_to=["e", "p"], verification_method=["SCRIPT"],
         verification_phase="SCHEMATIC", rules=["SCH-003", "INT-001"], rule_coverage="PARTIAL",
         source=["v2/ecad/tools/gen_sch_p.py:172", "v2/ecad/tools/gen_sch_e.py:136", "v2/docs/ASSEMBLY.md:60"],
         source_check="VERIFIED", conflict_ref="C-29",
         notes="Adjudication A07. A straight lead would swap clock and data, hold the sensor bus data line at 0 V and carry no ground."),
    dict(id="CAND-105", **{"class": "derived_constraint"}, parent="NEED-03",
         statement="Every enable line has a defined state from power-up until firmware writes it, set by external resistors that dominate any device's internal pull-up; the shared device rail comes up by design, not by an unspecified expander parameter.",
         acceptance="For every PCA9555-driven enable, the node voltage at power-up with the expander's pull-up at its weakest and strongest is below the load's OFF threshold or above its ON threshold, computed from datasheet limits; DEV_EN is driven high by a resistor to board A's 3.3 V.",
         allocated_to=["a", "b", "fw_panel"], verification_method=["CALCULATION", "SCRIPT"],
         verification_phase="SCHEMATIC", rules=["PWR-002", "SCH-004"], rule_coverage="PARTIAL",
         source=["v2/ecad/tools/gen_sch_a.py:407", "v2/ecad/tools/gen_sch_a.py:429", "v2/vendor/ti/ti-pca9555.pdf (SCPS131J 6.5 and 8.1)",
                 "v2/vendor/diodes/diodes-ap64500.pdf (DS41979)"],
         source_check="INFERRED", conflict_ref="C-32",
         notes="Adjudication A01: DEV_EN sits at about 1.71 V nominally against a 1.25 V turn-on maximum and fails only above about 181 k of internal pull-up; PA_SW_EN, HF_SW_EN and CHG_INHIBIT sit in undefined bands; POE_EN and PD_EN are OFF (guaranteed)."),
    dict(id="CAND-106", **{"class": "requirement"}, parent="NEED-14",
         statement="Lifting the stack for service does not leave a person touching live input or pack conductors, by a stated combination of procedure, covers and interlock.",
         acceptance="TBD (owner, D-14: whether the operator-dependent residual risk of a procedure-only answer is accepted). The session's floor, whatever the answer: ASSEMBLY section 7 says what is disconnected first, and an insulating cap covers the dock block while the stack is out.",
         tbd_effect="The stack lifts off spring contacts whose targets carry VIN_RAW and the pack current (ASSEMBLY.md:117, :131); a hardware interlock would touch boards A, E and possibly P and decision 40.",
         allocated_to=["procedure", "e", "e5", "a", "owner"], verification_method=["MANUAL_REVIEW", "PROTOTYPE_MEASUREMENT"],
         verification_phase="SCHEMATIC", final_phase="ASSEMBLY", rules=[], rule_coverage="NONE",
         source=["v2/docs/ASSEMBLY.md:117", "v2/docs/ASSEMBLY.md:131"], source_check="VERIFIED"),
    dict(id="CAND-107", **{"class": "derived_constraint"}, parent="NEED-02",
         statement="The 5G module sits in a key-B M.2 3052 socket, and if the kit has two 5G jacks they carry the module's ANT0 and ANT2 (three jacks: ANT0, ANT2, ANT3).",
         acceptance="The socket's part number is key B on the maker's drawing and its land matches that drawing; the pigtail and jack map names each ANTx port.",
         allocated_to=["b", "a", "e", "case"], verification_method=["MANUAL_REVIEW", "SCRIPT"],
         verification_phase="SCHEMATIC", rules=["CMP-002", "RF-001"], rule_coverage="PARTIAL",
         source=["v2/vendor/quectel/quectel-rm520n-series-hardware-design-v1.1.pdf (key B p.15 and p.20; Table 32)", "v2/ecad/tools/gen_sch_b.py:479",
                 "v2/docs/ASSEMBLY.md:99"],
         source_check="VERIFIED", conflict_ref="C-19",
         notes="Adjudication A08: TE 1-2199119-5 is key M (TE drawing C-2199119 rev F); ANT0+ANT2 keeps both n77/n78 transmit paths, ANT0+ANT1 leaves n78's primary path unconnected. The pairing is engineering; the count is the owner's (D-07)."),
]

for cid, rec in R.items():
    replace(cid, rec)
text = text.rstrip("\n") + "\n\n# ---------------------------------------------------------------- round 2 additions (25 Sep 2026)\n"
for rec in NEW:
    text += block(rec) + "\n"
text = text.replace("# Counts are checked by the validator at the end of the W1 session (see the StructuredOutput summary).",
                    "# Counts are checked by the validator at the end of the W1 session (see the StructuredOutput summary).\n# Round 2 (25 Sep 2026): records revised after the challenge and adjudications A01 to A11; CAND-095 to CAND-107 added.")
yaml.safe_load(text)
open(path, "w", encoding="utf-8").write(text)
print("patched", len(R), "added", len(NEW))
