accepted: yes

# Layer 4, L4-E12: Claude's check of the U-02 round at 625e7222 (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1478 under MESHSAT-1357, 2 October 2026. On the owner's instruction of the same day, the round states what supports the
2.159 W/K line, the configuration it assumes, where the fans' power enters the energy budget, who performs T-H1 and how, and
what a failed reading changes, with its fallback. It is section 13 of the page, section 8 of the output and
`T-H1-PROCEDURE-DRAFT.md`.

**Verified by the coordinator:**
- *Reproduction:* `l4e12_thermal.py` re-run at `625e7222`, its output equal to the committed `.out` byte for byte;
  `test_l4e12` with `test_public_hygiene` 25 passed, 0 failed, 0 skipped. No em or en dash in the page or the procedure.
- *The basis, in separate arithmetic:*
  - the heat in E5 under the hold is 14.671 + 3.445 + 0.036 + 1.345 = 19.497 W, and with L4-E8's 2.09 W of ballasts 21.587 W;
  - over the 10 K from E5's +60 C dwell to the +70 C parts' class that is 2.1587 W/K, with no margin;
  - the sensitivity is 0.1 W/K per W and 0.2159 W/K per K; a 1 K margin needs 2.399 W/K and 2 K needs 2.698 W/K;
  - E3-O is 27.086 / 15 = 1.8057 W/K.
- *The fans are counted, not in the undocumented share,* read on `records/rv-pwr/pwr_budget.py`: "cooler fan slot 1..3" at
  0.36 / 0.51 / 0.56 W (line 195) and "two mixer fans" at 0.78 / 1.44 / 3.0 W (line 298). The hold's 2.0 W is one running
  cooler fan and the mixers at nominal. They are stand-ins until D-18's pick; the round prints the line's spread over them
  (2.071 to 2.333 W/K).
- *A stopped fan:* the fans' own 2.0 W leaves with them. (21.587 - 2.0) W over 1.57 and 0.77 W/K gives 72.48 and 85.44 C, the
  round's 72.4 to 85.4 C.
- *The deeper hold:* (13.429 + 2.09) / 10 = 1.552 W/K, the round's line. The plate-coupling and fin figures are a stated model
  (classed MODELED and ASSUMPTION) for a bench to confirm, not measured values.
- *T-H1:* the procedure measures conductance as heat over rise on an empty Peli 1450 with the frame, a plate blank and
  distributed dummy heaters, at two powers, both lid states, fans on and off. It passes only if the reading less its expanded
  uncertainty reaches 2.159 W/K (a reading of at least 2.416 W/K at a 10 K rise under the assumed uncertainty budget, which the
  bench replaces with its own).

**Accepted** as the U-02 statement at the engineering level. The physical measurement (T-H1) and D-18's fan pick stay open, and
a feasible fallback (the plate coupling with the deeper hold, both the session's) is documented. Only below E3-O's floor does
the remaining option become the owner's (a deviation of E3-O or a device-set re-pick). L4-E9 must re-pin L4-E12's output and
insert the drafted fan register row.
