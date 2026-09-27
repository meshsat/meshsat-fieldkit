#!/usr/bin/env python3
"""DRAFT for the owner of v2/ecad/tools/pcb_sensitive.yaml (board e): the knock-on of S-47 (w3de, 27 September 2026).

gen_sch_e.py (w3de) moved the LT8705A's current-sense resistor R5 from the inductor's leg (TRK_LSENSE to TRK_SW2) to
the bottom switches' leg (TRK_CS to GND), as the maker draws it. The net TRK_LSENSE is gone, so board e's switch list
and its two Kelvin rows follow: R5.1 and R6.1 now sit on TRK_CS, R5.2 and R7.1 on GND. The switch list takes TRK_CS in
TRK_LSENSE's place (pass 2 of the independent check, 27 September 2026): TRK_CS is the common source of the bottom FETs
Q4 and Q5 above R5 and carries their chopped current, which is exactly how board A declares its LM5176 CS nodes (FE_CS,
PA_CS, HF_CS, PD_CS, POE_CS, S2_CS, SD_CS, F-PR-04); removing TRK_LSENSE without it would shrink ANA-001's switching
denominator for the TRK_CSP/TRK_CSN pair, and switch_list.py reads "CANDIDATE WEAK TRK_CS: Q4,Q5" (FAIL) without it
and PASS with it. Without this patch,
tests/test_kelvin_check.py t_every_declared_pad_is_a_pad_of_its_own_rail_on_that_boards_netlist fails on the
regenerated netlist ("board e declares a tap on TRK_LSENSE and no such net is in its netlist").

Usage: patch_pcb_sensitive_e.py <tree root holding v2/ecad>   (edits by asserted old text; refuses a changed file)"""
import os, sys
p = os.path.join(sys.argv[1], "v2", "ecad", "tools", "pcb_sensitive.yaml")
s = open(p, encoding="utf-8").read(); o = s
EDITS = [
 ('''   switch_nets: ["TRK_SW1", "TRK_SW2", "E6_SW", "FAN1_SW", "FAN2_SW", "TRK_LSENSE"]   # TRK_LSENSE is the inductor's second terminal, 5 mOhm from TRK_SW2: a switching conductor (18 September 2026)''',
  '''   switch_nets: ["TRK_SW1", "TRK_SW2", "E6_SW", "FAN1_SW", "FAN2_SW", "TRK_CS"]   # S-47, 27 September 2026 (w3de): TRK_LSENSE (the inductor's second terminal, a switching conductor since 18 September 2026) left the netlist when L1 came to join TRK_SW1 to TRK_SW2 directly, and TRK_CS takes its place: the common source of the bottom FETs Q4 and Q5 above the shunt R5, carrying their chopped current, declared as board A declares its LM5176 CS nodes (F-PR-04)'''),
 ('''   # filter resistor tapping each side. R5 is 5 mOhm between TRK_LSENSE and TRK_SW2, R6 taps the high side
   # into TRK_CSP and R7 the low side into TRK_CSN, with C16 across the pair at U5 pin 3.''',
  '''   # filter resistor tapping each side. R5 is 5 mOhm between TRK_LSENSE and TRK_SW2, R6 taps the high side
   # into TRK_CSP and R7 the low side into TRK_CSN, with C16 across the pair at U5 pin 3.
   # S-47, 27 September 2026 (board E stream w3de): R5 MOVED TO THE BOTTOM SWITCHES' LEG, as the LT8705A's maker draws
   # it (8705af Figure 1 p.13, Figure 14 p.35, the circuits on p.1 and p.41): the joined sources of Q4 and Q5 are the
   # node TRK_CS, R5 runs from TRK_CS to GND, R6 taps R5's TRK_CS pad into TRK_CSP and R7 R5's ground pad into TRK_CSN
   # ("Ensure accurate current sensing with Kelvin connections at the RSENSE resistors", p.36). The two rows follow.'''),
 ('''    - {sense: TRK_CSP, rail: TRK_LSENSE, element: "R5.1", tap: "R6.1", full_scale_mv: 51.7,''',
  '''    - {sense: TRK_CSP, rail: TRK_CS, element: "R5.1", tap: "R6.1", full_scale_mv: 51.7,'''),
 ('''         nowhere else and in the boost region it is not the output current, so the percentage is read against
         51.7 mV knowing that"}''',
  '''         nowhere else and in the boost region it is not the output current, so the percentage is read against
         51.7 mV knowing that. S-47 (27 September 2026): R5 now carries the bottom switches' current, which is the
         inductor's current while M2 (buck region, the valley the controller regulates) or M3 (boost region, the
         peak) conducts, so the same 51.7 mV full scale stands; the tap is R5's TRK_CS pad"}'''),
 ('''    - {sense: TRK_CSN, rail: TRK_SW2, element: "R5.2", tap: "R7.1", full_scale_mv: 51.7,
       why: "the other half of the same pair, and the sharper one: the low side taps TRK_SW2, which is the
         boost-side SWITCHING NODE, so the same conductor is both the sense reference and a node that swings
         every cycle. Its drop between R5.2 and R7.1 is current the LT8705A reads that is not there. This is
         18 September's finding measured instead of argued"}''',
  '''    - {sense: TRK_CSN, rail: GND, element: "R5.2", tap: "R7.1", full_scale_mv: 51.7,
       why: "the other half of the same pair: since S-47 (27 September 2026) the low side is R5's GROUND pad, where
         it had been TRK_SW2, the boost-side switching node. The shunt's ground end carries the whole bottom-switch
         current into the plane, so a tap taken anywhere but R5's own pad reads the plane's drop as current: the
         Kelvin connection the maker asks for (8705af p.36)"}'''),
 ('''       filter: "10 R (R6) from the shunt's inductor end with 1 nF (C16) across the pair at the controller (LT8705A 8705af Figure 13a)",''',
  '''       filter: "10 R (R6) from the shunt's TRK_CS pad with 1 nF (C16) across the pair at the controller (LT8705A 8705af Figure 13a; S-47 moved the shunt to the bottom switches' leg)",'''),
 ('''       filter: "10 R (R7) from the shunt's bridge end with 1 nF (C16) across the pair", kelvin_with: TRK_CSP, keep_mm: 0.5}''',
  '''       filter: "10 R (R7) from the shunt's ground pad with 1 nF (C16) across the pair (S-47)", kelvin_with: TRK_CSP, keep_mm: 0.5}'''),
]
for old, new in EDITS:
    if s.count(old) != 1: raise SystemExit("patch_pcb_sensitive_e: the old text is not there exactly once: %r" % old[:90])
    s = s.replace(old, new)
assert s != o
import yaml; yaml.safe_load(s)   # the file must still parse
open(p, "w", encoding="utf-8").write(s); print("patch_pcb_sensitive_e: %s edited, %d hunks" % (p, len(EDITS)))
