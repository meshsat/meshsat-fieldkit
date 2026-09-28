# Open item text for the integrator's registry script: board D's codec supply floor at the +5V_D8 peak

Stream s99a, MESHSAT-1357, 29 September 2026, from the independent check of the stream (minor item 1). AI
engineering arithmetic; prototype design, nothing built or measured. Figures: `codec_floor.out` (script
`codec_floor.py`, which reuses `u41_divider.py`). No declared figure was changed to make anything pass. Proposed
entry for `v2/ecad/tools/pcb_requirements.yaml` (the next free number after S-115 is S-116; the integrator assigns it):

    - id: S-116
      class: SESSION
      status: OPEN
      disposition: DECLARATION
      disposition_why: >-
        A question of the declared drop budgets and the declared peak of one conductor that crosses boards A and D; each
        option below is a declaration or a set-point change, with a layout reading behind the first.
      title: >-
        (stream s99a, S-99 follow-up) Board D's +5V_D8 supply at the PCM2912A codec falls under the codec's 4.35 V
        recommended minimum (TI SLES230A, revised August 2015, 7.3 p.5) at the declared 2.0 A peak once U23's drop and
        the budgets are counted. The chain from U41's regulation point: U41's DC set-point minimum 4.872 V (56.2k over
        10.7k at 0.1 percent, SLUSEA4D p.6), +5V_D8IN's copper (declared budget 2 percent, 0.100 V), U23's pass FET
        (SLVSET8A printed p.7, VIN above 4 V: 89 mOhm typical, 115.3 mOhm maximum over -40 to 85 C, 131 mOhm maximum
        to 125 C), and +5V_D8's copper on boards A and D (declared budget 6 percent, 0.300 V). At the 1.0 A typical the
        codec gets 4.44 to 4.48 V, 0.09 to 0.13 V over 4.35 V; with +5V_D8IN's whole 2 percent spent, 0.007 V (U23 at
        its 85 C maximum) to -0.009 V (125 C). At the 2.0 A peak, reading each budget as a fixed bar: 4.341 V (-0.009 V)
        with the 6 percent alone at U23's 85 C maximum, 4.241 V (-0.109 V) with +5V_D8IN's 2 percent too; dc_drop
        judges each budget at the rail's typical current (dc_drop.py lines 258 to 264), so a copper drop that spends its
        budget at 1.0 A doubles at 2.0 A and the floor reads 3.84 V. The shortfall PREDATES the split: U23 was in series
        before it, and the LM5176 source's bottom was 4.875 V (VREF 0.788 V, SNVSAI1D p.5, 53.6k over 10k at 1 percent,
        100 ppm/C over 65 K), which gives 4.344 V (-0.006 V) at 2.0 A with the 6 percent bar alone. Owners: board A
        (U41's set point, +5V_D8IN's budget and its layout reading) and board D (its +5V_D8 declarations and the codec's
        supply). Options for them, each with its figure at 2.0 A, the 6 percent bar and U23 at its 85 C maximum:
        (1) tighten +5V_D8IN's drop budget to about 0.5 percent (0.025 V) and add its reading at layout to S-115: 4.316 V
        (-0.034 V) at 2.0 A, 4.432 V (+0.082 V) at 1.0 A, so it closes the typical case and not the peak alone;
        (2) raise U41's set point within the 5.23 V ceiling (board D's v_work; the codec's 5.25 V recommended maximum):
        with this resistor class a top of 5.23 V gives a bottom of 4.964 V; the 53.6k over 10k pair at 0.1 percent
        (4.956 to 5.221 V, neither code certified today) gives 4.401 V (+0.051 V) at 2.0 A with option 1's 0.5 percent
        and 4.326 V (-0.024 V) with the present 2 percent, and 4.369 V (+0.019 V) at U23's 125 C maximum with 0.5
        percent; the top then sits 9 mV under 5.23 V as a DC band, before ripple and overshoot;
        (3) show by board D's declarations or a document that the codec's operation does not coincide with the 2.0 A
        peak: 2.0 A is U23's current limit, not a load; board D's own heaviest figure in stream s99's P-tier is 1.59 A
        (v2/docs/records/s99/ANALYSIS.md 3b), where the floor is 4.389 V (+0.039 V) with the 6 percent bar alone and
        4.289 V (-0.062 V) with +5V_D8IN's 2 percent. On the fixed-bar reading (1) with (2) clears 4.35 V at
        U23's 85 and 125 C maxima, and (1) with (3) only to 85 C (+0.014 V at 1.59 A, -0.012 V at 125 C); every option also needs the routed boards' drop at the peak current (the budgets
        are judged at the typical), which board A's layout (S-115) and board D's layout reading supply. Closed by the
        owners' declarations and those readings giving the codec at least 4.35 V at the declared peak, or by a document
        or a board D declaration that bounds the peak the codec must operate through.
