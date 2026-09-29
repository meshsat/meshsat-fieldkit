# Stream a1mech: running log (MESHSAT-1357, Option A(i) mechanical work package)

Worker: one Claude author, worktree `a1mech`, branch `fnd/a1mech` from `13b5352b`. Brief:
`_runs/claude/a1mech/20260929T0228/BRIEF.md`. Prototype design, AI review: nothing built, bought or fitted.

- 02:11 CEST: brief and WORKER-RULES read; ENERGY-RECONCILIATION sections 8 and 9, CASE-MARGINS sections 2 and 3 (the M rows),
  ASSEMBLY steps 10 and 11, the r2 QMX set and its check record, the lid STEP's face list, panel1450's face parts read.
- 02:20: makers' heights read for the parts that stand into the lid: APEM 5000 series (RS copy) page 13, lever -2V 14.75 over a 9.00
  bushing; APEM switch guards page 2, 22.00 to 28.00 closed (the held series is for the 12 mm bushings, the CSG for the 5000 is not held:
  class bound); Floyd Bell MC-09-530-Q page 2 (ring 35.8 x 7.9, thread 11.7, gasket 1.57, +-0.76). The U-174/U jack has no drawing
  held: its footprint is kept clear (TBD height). The tablet: no maker sheet reachable (Samsung's pages refused or absent from the
  Wayback index); the 8 and 10 inch rugged classes are carried as INFERRED envelopes.
- 02:25: first layout by hand: one layer of lying cells in holders (21.9 deep) gave about 33 cells beside the QMX set; the A06 block
  construction (cells touching at 18.55, 0.5 wrap, 1.0 end joints, the ruled base block's own basis) with a second layer nested in
  the grooves (16.065 higher) makes a 40.06 module that the worst room (44.39) takes over every face part up to 0.69 high, with the
  Xenarc window (0.8) at 3.10 worst, OPEN at the sensitivity reading.
- 02:30 to 02:36: `v2/cad/lid_pack_a1.py` written and run (`lid_pack_a1.out`): per-slice south edges from the face (the headset jacks
  and the sounder limit only the west slice), layer-2 places refused where a face part is too tall (the XFRAME screws), P2 placed at
  the corner costing fewest cells, the tablet's band searched in 1 mm steps. Results: A (HF and 8 inch tablet) 35 cells, 4S8P; B (HF,
  no tablet) 56, 4S14P; C (8 inch tablet, no HF) 54, 4S13P; C10 (10 inch tablet, no HF) 47, 4S11P; D (neither) 77, 4S19P.
  Stability: the open case stands on level ground to 120 degrees of opening in every swept case and tips from 135 with a light base.
- 02:38 to 02:45: drawing set A1-1 to A1-6 (`lid_pack_a1_drawing.py`, matplotlib) rendered and read back as images; fixes after the
  read-back: layer-2 cells hatched so both layers show; board P and the east block at their ruled place (group 205.5 centred, P
  south); the M5 and M6w rows. Retention rows added (3.46 kg module, 0.073 MPa mean on the bond, no held strength on PP: OPEN).
- 02:43: `lid_pack_a1_cad.py` run on the rented box under /root/a1mech (build123d 0.13.0, the d7fit venv, `pip freeze` equal to
  the lock): the boolean check agrees with the arithmetic for A, B, C, C10, D, both controls fail as they must; B's STEP and STL.
- 02:46: README written. The lid stay's second anchor moved from the frame's skirt (under the sealed plate, out of reach) to the
  plate's rebated back band.
- 02:50: the tablet search widened (landscape and portrait, every place 1.0 mm in X and 0.5 mm in Y, both bounds; the bracket may
  overhang the cover by 10 at most): A stays 35 (4S8P), C rises to 58 (4S14P, the tablet in the south-east), C10 47 (a 2 mm grid
  had missed its 0.47 mm window). The tablet's sounder and guard plan rows now print only where the tablet lies beside them.
- 02:52: the plate-side harness tie moved from the rebated band (5.0 wide under the lid wall at Y 130.9: a 4.4 lead does not fit)
  to the full face at Y 122; the lead grows to 169.7, bending at R 94 to 102. A tipping-line sensitivity added (feet 14.5 further
  in: 5.7 degrees at 100 degrees of opening). Hand counts of two other constructions (holders, cells along Y) recorded as ESTIMATE.
- 02:53: the solids and their check re-run on the box at `91f9f749`: PASS for A, B, C, C10, D, both controls fail as they must.
- 02:54: `DECISION-A1.md` (274 words) drafted for the integrator; the lid's growth stated from 1.4 kg (shell and QMX set).
- 02:55: the QMX DC lead's start corrected to the jack's place (X 106.3: the unit spans X 95.6 to 158.6, its knob edge west, the
  DC jack 10.2 to 11.2 from it; the first issue used 94.5); the case's centre of mass printed for the central estimate.
- 02:56: the light toggle's height read from NKK's sheet (M2044SD3A01: S bat 10.5 on a D3 bushing 8.9, 16.40 above the face) in
  place of the APEM bound; no arrangement moves (it lies under no lid item). README: REQ-023's margin, the lid pack's temperature
  handed to the thermal and energy streams.
- 02:57: the solids and their check re-run on the box at `80ab97b1`: PASS for A, B,
  C, C10 and D, both controls fail as they must. The box's `/root/a1mech/` keeps only this stream's clone and outputs.
- 02:59: a sensitivity of the counts to the module's INFERRED allowances added to the generator (most and least favourable
  settings, every face row re-judged): A 35, B 56, C 58 at both ends; C10 47 and 45; D 77 and 74. The finding does not hinge on them.
- 03:00: the solids and their check re-run at `f2432732`, where `lid_pack_a1.py` has its final content: PASS, both controls fail.
