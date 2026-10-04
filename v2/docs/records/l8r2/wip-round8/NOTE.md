# Round 8 work in progress (checkpoint of 4 October 2026, about 21:45 CEST, stopped at the session's usage limit)

Not a finished record: these three files are the unassembled remainder of `l8r2_gndret.py`'s `main()` for round 8, kept so the
work is not lost. Nothing here has been run.

- `tail_a.py.txt`: section 2c on the merged figures (one budget, the copy at `841e6c7e`; C-DEV rev 1's total 20.9888 A, the largest
  state 22.8711 A, the declared upper bound 27.9108 A). It replaces the code from `w("2c. the three figures` to the line before
  `# ---- 3`.
- `tail_b.py.txt`: sections 3a to 3f (the makers' figures with the two Amass XT60 sheets, both copper ends, the division as drawn
  with every vertex enumerated, the recheck's corner reproduced, what round 7's sampling missed, the supply pins). It needs
  `F["cab_tmax"]` added to `figures()` (the ribbon sheet's "Operating Temperature -25 C up to +105 C").
- `tail_c.py.txt`: section 3j (three approaches, the dedicated return selected at six conductors, three XT60 leads), section 4,
  section 5 (four drafts, board B in four orders, board A in L4-E9's order, the checks on both boards, thirteen mutations). It
  needs `apply_p(path, target, flag)`, `compose_a(paths, d, tag)` (mainpb last with board A's committed netlist, then Layer 6's
  `apply_gen_sch_a_lcsc.py`), `run_gen(gen, board="b")` and `import importlib.util` in the script's helpers.

Still to write: sections 3g to 3i moved or kept (the ground copper belongs after the acceptance), section 6 (the acceptance table
from the composed netlists' census with `design(..., enum=True)`, the XT60 ageing allowance by bisection on `ret_hi`, one lead
unmated, J_54V at AWG 18 and at AWG 16), sections 7 to 9, the tests, the page's section 3g and the README.
