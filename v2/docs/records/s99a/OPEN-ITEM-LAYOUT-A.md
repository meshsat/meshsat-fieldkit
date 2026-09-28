# Open item text for the integrator's registry script: board A's layout generator after decision 55

Stream s99a, MESHSAT-1357, 28 September 2026. AI engineering work; prototype design, nothing built or measured.
The layout generator `v2/ecad/tools/gen_pcb_a3.py` is NOT changed by this stream (the task's instruction). The
schematic-phase regeneration of board A is not affected by it: `gen_pcb_a3.py` runs only when board A's layout is
drawn. Proposed entry for `v2/ecad/tools/pcb_requirements.yaml` (the next free S number on set 8's line is S-115;
the integrator assigns it):

    - id: S-115
      class: SESSION
      status: OPEN
      disposition: LAYOUT_STAGE
      disposition_why: >-
        Board A's layout generator, run when board A's layout is drawn. No schematic-phase record rests on it: the
        schematic, netlist and intent of board A carry the new parts and nets from gen_sch_a.py (stream s99a).
      title: >-
        (S-99, decision 55, stream s99a) Board A's layout generator gen_pcb_a3.py does not know the D8 mezzanine's own
        buck. Two consequences, both at its next run: (1) it refuses the board, because its placement ends with
        `missing = [r for r in comps if r not in placed ...]; if missing: raise SystemExit("unplaced: ...")` (line 312
        on set 8's line) and none of the ten new parts U41, L13, C227 to C232, R217 and R218 has a region or a fixed
        site (the fixed table at line 208 places U21, U22 and U23 at (70, 66), (80, 66) and (90, 66); the region list
        "EFS" at line 280 holds the eFuse passives); (2) the +5V_DEV outlet-cluster island of lines 583 to 586
        (`bank_col(out, ["R100", "C103", "U23"])` on F.Cu and `pads_rect(net_pads(out, ["R100", "C103", "U23",
        "U18"]), ...)` on In3, inside the `n == "D"` branch where out is +5V_DEV) names three parts whose +5V_DEV pads
        moved to +5V_D8IN (U23 pin 4 IN, R100 the OVLO divider's top, C103 the input capacitor), so `net_pads` refuses
        or the island is built on the wrong net. The owner is board A's layout generator owner in board A's layout
        phase: place U41's buck (U41, L13, C227 to C232, R217, R218) beside U23 with the input loop C229/C230 at U41
        pin 3 (SLUSEA4D 12.1 p.40, the bypass pairs the generator declares), re-derive the outlet-cluster island for
        +5V_DEV from the parts still on it (U32's input, U18 pin 17 and the J_5V_DEV path) and give +5V_D8IN its own
        island from L13 to U23 pin 4, then run the pre-route and read /+5V_DEV and /+5V_D8IN at PREROUTE-DONE. Also
        at layout: dc_density on +5V_DEV at its 6.9142 A declared peak and on +5V_D8IN at 2.0 A, and U41's loss and
        temperature on the routed copper (SLUSEA4D gives RthJA 112.2 C/W JEDEC and 60.2 C/W on TI's EVM only, p.6).
        Closed by a gen_pcb_a3.py run that places every part of board A's netlist and reads both rails at
        PREROUTE-DONE, and by the layout-phase copper and thermal readings above.
