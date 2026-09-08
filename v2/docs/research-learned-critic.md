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

(filled by the campaign; every figure comes from `results.csv` and the journal, none typed by hand)
