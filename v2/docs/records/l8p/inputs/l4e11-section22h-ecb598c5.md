### 22h. The minors (V2-m1 to m5 and m9, this record's part)

- **V2-m1:** 21b (ii) takes Vishay's printed maxima for the SQJ403EP (4.5 nF) and the SQJ407EP (10.7 nF) and prints the typical
  figures beside them; the verdict is unchanged.
- **V2-m2:** Nexperia's hot IDSS row (10 uA at Tj 125 C) is quoted in 20e and 22b where the record said "not printed".
- **V2-m3:** the dd7 draft's comment carries 22c's figures (3.85 mA at the set, 4.32 mA with CELL+ at SYSOVP, 6.45 mA only at the clamp).
- **V2-m4, V1's two minors that no record carried:**
  1. *The TPS37's hysteresis accuracy (+-1.5 %) read as percentage points, not relative.* The return reads held under 0.7642 V (board
     P holds 0.055 V), the loop reads powered over 2.008 V at most (8 mV over the interface's 2.0 V; the held loop reads 0.536 V over
     it at 7.6 V), the window's bound is 25.1 kOhm: every margin still holds (V1's figures, reproduced by the script).
     **Owner:** this record. **Next action:** Q-TI-19 (`clarification/TI-QUESTIONS.md`, drafted, NOT SENT) and E11-45 (e), which reads
     U48's thresholds on the unit; the interface's 2.0 V is record l8p's to restate if TI answers "percentage points".
  2. *The CONOPS wording of the named residual.* Drafted sentence, for the CONOPS owner: "If the pack's breaker latches while a
     source carries the kit and no charge over 0.368 to 1.213 A flows, the pack stays isolated: the kit runs on the source alone, and
     the pack returns only on a redocking or when an input returns to a dark kit." **Owner:** the CONOPS owner with record l9stk (the
     battery stream), as V1 named them. **Next action:** L4-E9's next round takes the sentence as a register row; a controlled
     amendment of an accepted Layer 2 page is the coordinator's.
- **V2-m5:** E11-29's coupon also reads the PTC's site (RT1) against each junction with one FET heated alone at the worst split's
  1.513 W (the row in section 8 and block E11-29 in 17d), so the guard's trip side is judged on the hottest FET.
- **V2-m9:** the tests compose board A in main's order, with record l8r2's d8v3 and vbus20ov. The candidate's change list (L4-E9
  rows 24 to 33) names l8r2's packrtn, slotlm and fb01 instead; those three drafts are **not in this branch's tree** (`fnd/l8r3` at
  `89924e40`), so the tests keep the order this tree can show. **The list's order, shown where its drafts are:** on a scratch copy of
  the candidate's files (`fnd/v2cand` at `dfa1eef2`) with this round's drafts laid over them, `compose_in_list_order.py` composed the
  list's order (16 drafts, each exit 0), the generator ran to its end (778 parts, intent written), `check_dd7_netlist.py` read DRAWN
  and three mutations read FAIL (a scratch run of 4 October 2026). `test_l4e11` runs that script: in this tree it reports the missing
  drafts; once they are in the tree (the candidate's line) it requires the list's order to compose and read DRAWN.

