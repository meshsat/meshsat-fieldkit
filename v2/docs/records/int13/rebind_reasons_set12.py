# The integrator's reasons, read by hand, for the records set 12's circuit change names (MESHSAT-1357, 29 September 2026).
# Board B's changed parts are stream d4emcon's FEA-002 glue logic (U537 to U554, R532 to R550, C668 to C685, and R41, R42,
# R238, R527 and U536's values); GND, +3V3_DEV and +5V_DEV are named because the new parts take their supplies and returns
# from them. Board C's are R52 and D23 on EMCON_HW and TX_INHIBIT_n (D4E-F1). The remedies' technical fit is the set 12
# independent check's; these reasons say only why each record's reading is or is not moved.
# Board B's "CFL-016" reason below was FALSE for CONOPS section 4b (the set 12 check's B1); the entries it wrote are
# corrected by apply_check13_fixes.py, and the text is kept as the record of what was written.
B = {
 "CHO-001": "the change adds glue logic on the radio lines and moves the values of R41, R42, R238, R527 and U536; no device of the ruled set is added, removed or substituted, so the device-set reading is unchanged",
 "CON-003": "the changed parts sit on the RockBLOCK, E72, E22 and 5G power-off lines, none on the voted fabric's selects, output enables or hub resets; GND gains only the new parts' returns",
 "CON-022": "no new part drives a compute module pin from an always-on rail: the E22 gates and buffers that meet slot 3's pins run from slot 3's own 3.3 V (SN74LVC Ioff with the module unpowered), the other new parts drive radio modules, not compute modules",
 "CON-017": "the three I/O supervisors, their symbol values and BOM lines are untouched by the change; the regenerated netlist differs from the committed one only by the drafted FEA-002 parts",
 "REQ-030": "the change is the FEA-002 remedy set this requirement's reading waits on; FEA-002's layout-entry stage stays open (EMCON.md 4d: rows 3 and 4 open on desk items, every other row needs hardware), so the reading stays as it was",
 "REQ-071": "the change is the FEA-002 remedy set this requirement's reading waits on; every row's radio-side timing term still needs a bench test (EMCON.md 4d), so the reading stays as it was",
 "CFL-004": "the compute modules' radio-disable lines (WL_nDIS and BT_nDIS on U30A to U32A) are untouched: RF-002's walk reads their rows as on main",
 "REQ-032": "the change gates the back-feed into the RockBLOCK, the E22 and both E72 and repeats the 5G card's power-off line; whether each radio is off in hardware under EMCON still waits on FEA-002's open rows, so the reading stays as it was",
 "CFL-016": "the published contracts this conflict resolved still describe the circuit: PANEL.md's EMCON_HW row (U9 buffers TX_INHIBIT_n, low while it is low) stays true with U9 now driving through R52 and D23 clamping the line to TX_INHIBIT_n; the R41 and R42 change is the RockBLOCK pull-downs of B-1, which no published contract names",
 "CON-015": "the 5G socket, its key and its three antenna jacks are untouched; U554 repeats U221 on FULL_CARD_POWER_OFF# only",
 "CON-016": "no new part is a one-way surge clamp or a rectifier on board B; the pin-direction reading of this record's tool did not move at the re-take",
}
C = {
 "REQ-012": "the TX lamp's path from the VHF KEY line is untouched; EMCON_HW and TX_INHIBIT_n are named for the EMCON lamp and the line, which D4E-F1 clamps; the reading stays as it was",
 "CON-021": "the EMCON lamp is still driven from the line's state with no processor in its path (U14 reads EMCON_HW and TX_INHIBIT_n; d4emcon's lamp check and readback_d4e hold on the regenerated board C); the face plate's light guide stays open (S-44), so the reading stays as it was",
 "CFL-016": "the published contracts this conflict resolved still describe the circuit: PANEL.md's EMCON_HW row (U9 buffers TX_INHIBIT_n, low while it is low) stays true with U9 now driving through R52 and D23 clamping the line to TX_INHIBIT_n",
 "CON-016": "D23 (BAT46W) is a signal clamp, anode EMCON_HW and cathode TX_INHIBIT_n, drawn on a symbol with a cathode pin, not a surge clamp or a rectifier on a rail; the pin-direction reading of this record's tool did not move at the re-take",
}
GEN = {
 "CHO-001": B["CHO-001"],
 "CON-015": B["CON-015"],
 "CON-017": B["CON-017"],
 "CFL-004": B["CFL-004"],
 "CFL-001": "the change touches no bank adoption line, voted select or output enable of the I/O high-availability fabric; which neighbour adopts each bank is as it was",
 "REQ-052": "the lid sense and the reduced mode's slot assignment are untouched; the change gates the RockBLOCK, E22 and E72 lines against back-feed without changing which module carries which radio",
 "CON-025": "the 5G module's SIM TVS arrays and their placement are untouched; U554 repeats U221 on FULL_CARD_POWER_OFF# only",
}
# Second pass (after S-117 on board A, the check's minors and the census nodes): board A's reasons, board B's FEA-002.
B["FEA-002"] = ("the change is the FEA-002 remedy set with the check's minors; FEA-002 stays FEASIBILITY_OPEN with its layout-entry "
                "stage open (0 of 17 rows closed at desk); d4emcon's read-back differs only on the three values the minors changed "
                "on purpose and readback_chk12 holds on the regenerated board")
A = {
 "CON-019": "the PoE and USB-C outlets' interlock and the PA key path are untouched; set 12 changes only the charger U3's power stage, compensation and the census declarations of IADPT and CH_COMP1",
 "CON-018": "the USB-C CC ESD array by the connector is untouched; set 12 changes only the charger U3's power stage and compensation",
 "CFL-005": "EMCON_HW's pull-down R102 and the slot enables are untouched; set 12 changes only the charger U3's power stage and compensation",
 # m1 of the set 12 check: the L2 below is EMCON.md's line-hold item, not board D's; corrected in the registry
 # by apply_check13_fixes.py.
 "CON-010": "the PA's VGG gate and board D's KEY path are untouched; the L2 this record's evidence names is board D's, not board A's charger inductor that set 12 replaced",
 "REQ-077": "the charger's power stage, frequency row and compensation change (S-117, decisions 56 and 57), not its thermistor input, the gauge's thresholds or the shedding path this reading rests on",
 "CFL-016": "the published contracts this conflict resolved name no charger FET; the Q7 this record names is on another board or unchanged in role, and PANEL.md's rows stay true",
 "CFL-014": "the charger's cell-count strap stays 4S and the loads stay on VSYS; set 12 changes its inductor, FETs and compensation (S-117), which HW-FW-CONTRACT.md's FW-A17 and V-A05 now record",
 "CON-016": "no one-way surge clamp or rectifier changes on board A; Q7 to Q10 are the charger's switching FETs, and the pin-direction reading did not move at the re-take",
}
GEN_BY = {"b": GEN, "a": {k: A[k] for k in ("CON-018", "CON-019", "CFL-014", "REQ-077")}}
