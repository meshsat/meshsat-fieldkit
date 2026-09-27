# Finding for the board E author: six N-channel FETs drawn with a P-channel symbol

Draft by w3g (MESHSAT-1357, 27 September 2026), found while the diagram tools were taught to read a FET's polarity
from its library symbol. Not a change to any file: board E's generator is not this stream's.

**What the netlist at `38dcd764` carries** (`v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net`, sha256/16
`f3c1ad6153002976`): Q1 to Q6 use KiCad's `Transistor_FET:IRF7404` symbol, whose library description and keywords say
"P-Channel HEXFET Power MOSFET", while each part's value text names an N-channel Infineon part: Q1, Q2 and Q4, Q6
BSC039N06NS, Q3 and Q5 BSC028N06NS ("60 V ... N-FET"). The generator lines are `v2/ecad/tools/gen_sch_e.py:335`
(Q1, Q2, the ideal-diode FETs) and `:476` to `:479` (Q3 to Q6, the LT8705A tracker's four switches).

**What is right.** The pin map is the TDSON-8 one the value text states (1 to 3 S, 4 G, 5 to 8 D), which is also the
IRF7404's SO-8 order, so the netlist's pin functions S, G and D and the land are consistent with the N-channel part;
`power_tree.py` reads the gate by the symbol's pin name and draws these stages correctly.

**What is wrong.** The native schematic and its PDF draw a P-channel device (arrow and body diode the other way) in
positions that need an N-channel FET (an LM74700 ideal diode drives an N-FET; so does the LT8705A's four-switch
stage). A reviewer reading the schematic PDF sees the wrong polarity, and any tool that takes polarity from the symbol
(the diagram tools now do, for control lines only) is misled. Layer 8's item "exact part and land mapping" and the
readable-schematic item both rest on the drawn symbol agreeing with the part.

**Recommended change** (for the board E author, with parity): draw Q1 to Q6 with an N-channel symbol whose pins carry
the same numbers and names (a project symbol, as board A draws its CSD power FETs from `meshsat_ic`, or an N-channel
eight-pin symbol from the KiCad library the box's KiCad 9 carries, checked there), keep every pin's net, and prove
by netlist comparison that only the six `libsource` entries change (LM74700-Q1 and LT8705A both drive N-channel
FETs: `v2/vendor/ti/ti-lm74700-q1.pdf`, `v2/vendor/power/lt8705a.pdf`). No other board has a FET whose symbol polarity disagrees with its value text at `38dcd764` (all six
netlists read).
