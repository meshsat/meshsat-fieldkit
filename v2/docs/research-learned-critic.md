# A learned critic for placement: what fits this pipeline, what does not (MESHSAT-862 Stage E, 8 Sep 2026)

Prototype design; nothing here has been built or ordered. This note records the research behind the owner's ruling of 8 Sep 2026 (no JEPA arm,
no paid solver) and the design of the data campaign that replaces them. The numbers section is filled by the scripts as the campaign runs.

## 1. The question

The pipeline's only feedback from the router to the placement was a full route: A22's INA226 row was found colliding after run 10, B16's HDMI
switches after a 3 h 20 min route (appendix 32.64 W3). The learnable question is therefore "where will the router fail, given this placement",
asked before a route is bought. Everything else the audit found missing (impedance, DC drop, return paths, decoupling loops) is computed by
closed-form or field solvers, not learned (Stage C).

## 2. What the literature does

- Chip design has treated this as a supervised problem since RouteNet (2018: a CNN on pin-density and RUDY maps predicting DRC hotspots),
  PGNN (2022: a GNN with a U-Net for pin accessibility and congestion), a placement-image framework trained on 26,000 placements from 372
  benchmarks at 97 percent accuracy, and DRV-hotspot predictors through 2026. None is self-supervised.
- Learned routing: PCBWorld (arXiv 2607.05915, July 2026) is a KiCad-native environment with 679 real boards and two synthetic generators,
  eight engine-checked DRC metrics; its reinforcement-learning routers, trained on synthetic boards, transfer zero-shot to real ones and
  approach a rule-based router without beating it. Quilter trains reinforcement learning against a physics engine written in JAX, never on
  human designs (the OnTrack interview of 27 May 2026). The engine that judges is the asset in both.
- JEPA (I-JEPA, V-JEPA 2, Graph-JEPA, Point-JEPA, HEP-JEPA): self-supervised encoders whose low-data advantage rests on a large unlabeled
  corpus (V-JEPA 2: a million hours of video before 62 hours of robot data). No published application to board or chip layout exists
  (searched 8 Sep 2026).

## 3. Why not a JEPA here

The data regime is the inverse of JEPA's premise. The corpus is six base boards, 34 board-file revisions and 236 bench rows; the router is
deterministic, so labels are cheap (a D8, E6 or P1 route takes minutes and a 16-thread box runs a dozen at once: thousands of labelled
jittered placements for about 10 USD), while board diversity, which no self-supervised objective creates, is what is scarce. A JEPA arm
would cost 35 to 50 USD of H100 time for a result the supervised arm would likely match. The condition under which it becomes the right tool
is recorded: thousands of distinct boards (PCBWorld's 679 plus its generators) and a slow evaluator producing few labels (openEMS at hours per
pair), at which point an encoder pretrained on the unlabeled corpus and probed with few labels is textbook. Neither holds.

## 4. The campaign (Stage E)

- E1, data: `tools/place_jitter.py` makes a neighbour of a placement (every unfixed footprint moved by up to 1 mm, same-footprint pairs within
  15 mm swapped with probability 0.3); `tools/jitter_campaign.sh` runs the board's own pre-route chain with `PLACE_JITTER=<seed>` (the
  predictor reports but does not block), routes each sample once under the board's routeflow profile, and `tools/tile_labels.py` writes one
  row per 10 mm tile: features from the pre-route board (pads, fine-pitch pads, escape vias, locked length, escape-envelope overlap, nets
  crossing, rule-area coverage) and labels from the routed board and its DRC (opens, hard, router vias, router length). Samples the chain
  refuses are recorded as refused.
- E2, the analytical arm: `tools/place_audit.py` (escape-fan envelopes e = 2.2 + 0.12 mm per pad, calibrated on the two recorded collisions)
  scored on the same tiles: precision and recall of "opens in this tile" against the envelope-overlap feature.
- E3, the supervised arm: a small U-Net (or a gradient-boosted model on the tile features first) trained on five boards, tested on the sixth;
  the same metric.
- E5, placement search: the winning arm scores candidate placements (jitter and part order) and the best candidate is routed as a bench row;
  the router remains the judge; released boards are not moved by this stage.

## 5. Numbers

Every figure below is printed by `tools/critic_e2.py` over the campaign's tile rows in `tools/routeflow/bench/jitter/` (8 Sep 2026: D8 60 jittered placements on the 128-thread box plus 557 tile rows from the 16-thread box, E6 40, P1 60 plus 234; C7 gave no rows because every one of its 40 jittered routes ended at the campaign's time limit without a session). A row is one 10 mm tile of one jittered placement; its label is what the production router left in that tile (opens, hard violations); its features are what `place_audit.py` and `tile_labels.py` read off the pre-route board (pads, fine-pitch pads, pads without an escape, escape vias, locked copper length, escape-envelope overlap, nets crossing the tile, rule areas).

### 5.1 Stage E2, the analytical arm as a tile predictor

```
$ python3 tools/critic_e2.py tools/routeflow/bench/jitter/jitter-pcb-d-aprs.csv tools/routeflow/bench/jitter/jitter-pcb-e1-dock.csv tools/routeflow/bench/jitter/jitter-pcb-p-pack.csv tools/routeflow/bench/jitter/jitter-pcb-d-aprs-smallbox.csv tools/routeflow/bench/jitter/jitter-pcb-p-pack-smallbox.csv
== all rows (5 files): 9033 tiles, 294 (3.3%) with an open or a hard violation
   unescaped_pads > 0                     flags    74 tiles  precision 0.11  recall 0.03
   env_overlap > 0                        flags   131 tiles  precision 0.02  recall 0.01
   nets_crossing > 0                      flags  8906 tiles  precision 0.03  recall 0.98
   fine_pads > 0                          flags   957 tiles  precision 0.07  recall 0.24
   pads >= 12                             flags  1405 tiles  precision 0.05  recall 0.25
   nets_crossing >= 8                     flags  6984 tiles  precision 0.03  recall 0.82
   fine_pads > 0 and nets_crossing >= 8   flags   957 tiles  precision 0.07  recall 0.24
== pcb-d-aprs-preroute.kicad_pcb: 2705 tiles, 36 (1.3%) with an open or a hard violation
   unescaped_pads > 0                     flags    34 tiles  precision 0.00  recall 0.00
   env_overlap > 0                        flags    91 tiles  precision 0.01  recall 0.03
   nets_crossing > 0                      flags  2699 tiles  precision 0.01  recall 0.83
   fine_pads > 0                          flags   408 tiles  precision 0.03  recall 0.39
   pads >= 12                             flags   774 tiles  precision 0.02  recall 0.47
   nets_crossing >= 8                     flags  2159 tiles  precision 0.01  recall 0.83
   fine_pads > 0 and nets_crossing >= 8   flags   408 tiles  precision 0.03  recall 0.39
== pcb-e1-dock-preroute.kicad_pcb: 5563 tiles, 205 (3.7%) with an open or a hard violation
   unescaped_pads > 0                     flags    40 tiles  precision 0.20  recall 0.04
   env_overlap > 0                        flags    40 tiles  precision 0.03  recall 0.00
   nets_crossing > 0                      flags  5563 tiles  precision 0.04  recall 1.00
   fine_pads > 0                          flags   480 tiles  precision 0.11  recall 0.25
   pads >= 12                             flags   508 tiles  precision 0.07  recall 0.19
   nets_crossing >= 8                     flags  4480 tiles  precision 0.04  recall 0.87
   fine_pads > 0 and nets_crossing >= 8   flags   480 tiles  precision 0.11  recall 0.25
== pcb-p-pack-preroute.kicad_pcb: 765 tiles, 53 (6.9%) with an open or a hard violation
   unescaped_pads > 0                     flags     0 tiles  precision 0.00  recall 0.00
   env_overlap > 0                        flags     0 tiles  precision 0.00  recall 0.00
   nets_crossing > 0                      flags   644 tiles  precision 0.08  recall 1.00
   fine_pads > 0                          flags    69 tiles  precision 0.06  recall 0.08
   pads >= 12                             flags   123 tiles  precision 0.15  recall 0.34
   nets_crossing >= 8                     flags   345 tiles  precision 0.10  recall 0.62
   fine_pads > 0 and nets_crossing >= 8   flags    69 tiles  precision 0.06  recall 0.08
```

Reading: the base rate is 3.3 percent of tiles (294 of 9,033). No analytical feature predicts a failing tile: the escape-envelope overlap, the very rule that caught the INA226 row on A22 and the HDMI switches on B16 at board level, flags 131 tiles with a precision of 0.02; pads without an escape 74 tiles at 0.11; the crossing-net count is nearly everywhere (recall 0.98 at precision 0.03) and its high end (8 or more) no better; fine-pitch presence and pad density reach a recall of a quarter at a precision of 0.05 to 0.07. Per board the picture is the same (D8 1.3 percent failing tiles, E6 3.7, P1 6.9; the E6 escape rule is the best single feature at precision 0.20 and recall 0.04). So on these three boards the router's residual opens and hard items do not sit where the placement features say; they sit where the router's global choices (layer, ripup order) leave them, and a tile-local predictor cannot see that. **The analytical predictor stays what it was designed as: a board-level gate for escape-fan collisions of fine-pitch parts (a placement defect it does catch), not a router-outcome predictor.**

### 5.2 Stage E3, the supervised arm

Not run. With 294 positive tiles at a 3.3 percent base rate and no feature above 0.2 precision, a U-Net trained on these rasters would learn the base rate; the negative result of 5.1 is the result, and the condition for a learned critic (thousands of distinct boards, a slow evaluator producing few labels) is the one section 3 states for a JEPA as well. The five USD of GPU time stay unspent.

### 5.3 What the campaign did produce

The campaign infrastructure (`place_jitter.py`, `jitter_campaign.sh`, `tile_labels.py`, `critic_e2.py`) and 9,033 labelled tile rows; the finding that on D8, E6 and P1 the router's leftovers are not placement-local; and the C7 negative (its jittered routes exceed the campaign's limit: the backer ring is the one board whose route time, not its placement, is the constraint). The placement instrument's real yield was the board-level collision rule (32.66 and 32.70) and, on D9, the station rule for pairs (two series resistors side by side, pads across the pair axis, on the pair's layer) that the pair pre-router derived from the same kind of measurement.
