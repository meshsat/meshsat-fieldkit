accepted: yes

# Layer 4, L4-E12: Claude's check of the thermal reconciliation at bf572635 (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. The owner (item 1 of the 14:20 amendment) asked for the reconciliation of the claim that a T-H1 point
passing at 1.509 W/K establishes operation at +40 C. The round (section 16, output section 11) answers point by point.

**The correction, and the coordinator's own error:** the claim is withdrawn. 1.509 W/K is the profile's +70 C class at +40 C
(43.413 W over 30 K = 1.447 W/K, plus a 4.1 % expanded uncertainty), and no requirement asks for that state.
- REQ-024 (read on `pcb_requirements.yaml`): the kit sheds "on measured inside-air (+50 C) and cell (+55 C) temperatures ... to its
  reduced mode and then its heat stage (C1)". Its acceptance: "part_temps.py finds no part outside its range".
- The decision register (`pcb_decisions.yaml` lines 542 and 565): the reduced mode above +35 C ambient.
- At +40 C the required state is the heat stage, 27.086 W. The coordinator's check 6 accepted the earlier framing and the
  coordinator reported it to the owner. That was wrong, and it is corrected here and in the next report.

**Verified by the coordinator:**
- *Reproduction:* `l4e12_thermal.py` re-run at `bf572635`, its output equal to the committed `.out` byte for byte.
- *The +55 C inside-air limit exists and is the SGP41's:* REQ-052 reads "an SGP41 above +55 C fails", and REQ-024's acceptance puts
  every part in its range. K1 (the heat stage at +40 C against the SGP41's +55 C) needs 27.086 / 15 = 1.806 W/K. The owner's 2.83 W/K
  (42.4 W over 15 K) belongs to no required mode, because the profile is shed before +50 C inside air.
- *The bench pass line:* 1.958 W/K, with heaters at 25.136 W plus the fans' measured draw, and a 7.8 % expanded uncertainty
  (1 - 1.806 / 1.958). The heat table counts the fans once.
- *The translation from room to +40 C* raises the conductance by x1.016 to x1.037 at the same rise, so the room reading is the
  conservative side. The sun is excluded on D-02e (operated shaded) and on TEST-PLAN having no Method 505 row.

**A dependency the round lists but does not draw out (material for the owner):** the limits are tabled separately as K1 (the SGP41 on
its Table 5, +55 C: 1.806 W/K), K2 (the SGP41 on its Table 4, +50 C: 2.709 W/K) and K3 (the +70 C class in the heat stage: 0.903 W/K).
- The round itself records that K1's need lies at or over the case's cap at the conservative ends.
- While the SGP41 stays in the bay powered (CFL-002 option C), K1 governs, and the case can only just meet it, if at all.
- With option A (a gas sensor rated to +85 C in its place) or B (the bay VOC channel dropped), K1 and K2 fall away, and K3's 0.903 W/K
  governs: about half, a bench pass line near 0.98 W/K.
- So the owner's CFL-002 decides which thermal line the sealed case must meet at +40 C. This goes to the consolidation and the owner.

**Accepted** as the reconciliation. The section-15 charging need is corrected to 1.627 to 1.977 W/K with the charge path counted. What
one passing point closes and what remains is tabled: K1, K3, K4 and K9 by one point; K5, K6, K7, K8 and K10 by further points; the
SGP41's Table 4, hot spots, the fans' rating, full sun and the cells at +40 C remain open. The procedure's endpoint (a drift of at most
0.1 K per hour, or a first-order fit over at least three time constants) and its pass, fail and inconclusive criteria are stated.
Authorisation to run the test is the owner's; acceptance of its result goes through the coordinator's check against section 16.
