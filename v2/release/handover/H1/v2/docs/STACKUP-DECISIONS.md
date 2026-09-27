# Stackup decisions, board by board

MESHSAT-1357, pre-PCB layer 9 of the handover (`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`, section 3).
Written 27 September 2026 against `main` at `e3aedb25`. **Prototype design: no V2 board has been fabricated, ordered,
assembled or powered, and no price for any stackup has been quoted.**

This page is the per-board stackup record the P0 rule of 11 September 2026 and rule STK-002 ask for: for each board
the stackup code, the use of every copper layer, the copper weights, the measurement that forced the layer count, its
price status, the authority behind it, and whether it is decided. It is a **view over the records**, never a new
authority: every line names the record it is read from. It **supersedes as a summary** the closing paragraphs of
`v2/docs/LAYER-DECISIONS-2026-09-11.md`, which predate owner decisions 27, 28 and 43 of 25 September 2026 and still
say "B six stands", "C four decided" and "P two decided"; that page stays the evidence record for the measurements it
holds. The stackup and the layer count are a reserved class (`v2/ecad/tools/reserved.json`, class "layer count and
stackup"); nothing on this page edits `stackup_write.STACKS` or any generator.

Evidence labels as in `v2/docs/B-FEASIBILITY.md`: VERIFIED (read in the artefact cited), RECORDED (a measurement in
the record whose run is not in this tree), INFERRED (reasoned from verified facts, stated how), TBD (no source).

## 1. The rule

- **P0 (owner, 11 September 2026; `LAYER-DECISIONS-2026-09-11.md` opening, `OWNER-DECISIONS-2026-09-11.md` section 2,
  appendix 32.106):** every board's layer count needs its own
  written decision carrying the measurement that forced it and the cost it adds; a stackup is never inherited from a
  sibling board and never promoted silently when a route fails; a session decision taken inside an owner rulings list
  is marked as the session's.
- **STK-002** (`v2/ecad/tools/pcb_rules.yaml`, verification phase RELEASE_PACKAGE): "a dated decision naming the
  measurement (a route at the lower count, or a requirement the lower count cannot meet) and the price difference from
  the fabricator".
- **STK-001** (ROUTED_BOARD): the board file carries a named, dated fabricator stackup and every impedance, current
  and spacing rule resolves against it.
- **Owner section 5 of 27 September 2026** (the handover prompt): layout entry requires the reviewed stackup among its
  inputs. No rule in the registry checks that at layout entry today (section 7 below).

## 2. The seven boards

Copper thickness is the finished figure in the fabricator's layer table (`stackup_write.STACKS`; outer 0.035 mm is
1 oz, 0.070 mm is 2 oz; inner 0.0152 mm is JLCPCB's 0.5 oz inner, read from `v2/vendor/fabricator/`).

| Board | Layers | Stackup code (a `STACKS` row) | Outer / inner copper | Layer use | Measurement that forced the count | Authority | Price | Decided? |
|---|---:|---|---|---|---|---|---|---|
| A power | 6 | JLC06161H-3313 | 0.035 / 0.0152 | F sig+power bands, In1 GND, In2 sig+VBAT/GND pours, In3 sig+power pours, In4 GND, B sig+power bands | four-layer arm: 0 hard, **345 unrouted**, autoroute completed in 51 min, against 0 and 0 at six (A24) | SESSION write-up under owner ruling 2 of 12 Sep ("write up all seven ... TEST board A only") | none | **count DECIDED; copper weight UNDECIDED** (section 3.1) |
| B compute | 6 as built; 8 under measurement | JLC06161H-3313 as built; JLC08161H-2116 recorded for decision 43 | 0.035 / 0.0152 (both) | as built: F sig, In1 GND, In2 sig, In3 sig, In4 four split 5 V planes, B sig | 93 opens at 8 passes with a board-wide In1 keep-out (5 Sep); Q-B-ESC-1 eight-layer region arm 18 open (EXPERIMENTAL, INCONCLUSIVE) | OWNER decision 43: measure eight layers first | none | **UNDECIDED** (section 4) |
| C panel backer | 6 (ruled); board file still 4 | JLC06161H-3313 | 0.035 / 0.0152 | F sig, In1 GND, In2 sig, In3 sig, In4 GND, B sig (decision 27's option 1 as written) | C24: 18 B.Cu nets fail RET-001/002 with only In2, a routing layer, beside them; two layers left 14 to 35 open (6 Sep); six-layer arm 0 and 0 in 14.7 min (16 Sep) | OWNER decision 27 (25 Sep) | none; the decision itself asks for the quote before anything is paid | **DECIDED** (count and use); not regenerated |
| D APRS | 4 | JLC04161H-7628 | 0.035 / 0.0152 | F sig, In1 GND, In2 plane (+5V_D8 and GND pours; 6 track segments on D12), B sig | the RF reason: a solid ground plane under the SA868 exciter, the PA stage and the filter; the In2-as-plane arm routed 0 and 0 (15 Sep) | SESSION write-up under owner ruling 2 of 12 Sep | none | **DECIDED** |
| E1 dock | 4 | JLC04161H-7628 | 0.035 / 0.0152 | F sig+pours, In1 GND, In2 power pours (CELL_F, PV_P, TRK_OUT, VIN_RAW) plus GND fill, B sig+pours | the routing half (267 mm strip, end-to-end nets USB_E6_P 196 mm and GEIGER_IN 214 mm) and In1; the power half REFUTED (In2's 5,500 mm2 worth 13 and 28 mV) | SESSION write-up under owner ruling 2 of 12 Sep | none | **DECIDED** (see the 2 oz contradiction, section 6 item 5) |
| P pack BMS | 4 (ruled); board file still 2 | JLC04162H-7628 recorded (0.5 oz inner, the fabricator's default) | 0.070 / 0.0152 | F sig+pack bands, In1 GND, In2 GND, B sig+pack bands (the P8 arm) | two layers leave 43, 45, 47 open at the fabricator's 0.16 mm floor; four layers 0 and 0 (P8, 18 Sep) | OWNER decision 28 (25 Sep) and ruling 7 (12 Sep, 2 oz) | none | **count and outer weight DECIDED; inner weight UNDECIDED** (section 3.6) |
| E5 dock block | 2 | 2L-2oz | 0.070 / none | contact targets, wire lands | nothing inner to weigh; 112 mm of copper | OWNER ruling 7 (12 Sep, 2 oz) | none | **DECIDED** (STK-001 residue: Dk 4.6 in the board file against 4.5 in the row) |

Sources for the table, row by row: `LAYER-DECISIONS-2026-09-11.md` (the measurements, the "decisions as they stand"
section and its 19 September correction); `v2/ecad/tools/pcb_decisions.yaml` n 27, 28, 43 (owner, 25 September 2026);
`v2/docs/OWNER-DECISIONS-2026-09-11.md` decision 7 and its "What each ruling commits us to" list, decision 27 option
1 (the six-layer C layer use); `v2/ecad/tools/stackup_write.py` STACKS (sha256/16 `b55a3c0f58c805c2`); the zone and
segment census of each committed board file read for this page (A32 `58e26c67987b1daa`, B21 `2e64b5bf2d9cd3bc`, C24
`2a273803757c68fb`, D12 `929bf82d2bf6eed4`, E17 `a462ac2620b9b8d3`, P4 `d79865e7b1aceb95`, E5 `686b29a734c55b9a`);
`v2/docs/B-FEASIBILITY.md` sections 3.2, 4, 7.8; `v2/ecad/tools/boards/p.json` `_p8_route_why`.

The authority of the SESSION rows: owner ruling 2 of 12 September 2026 on the P0, "write up all seven from the
evidence that exists, and TEST board A only (four layers against six). The other six are documentation, not
experiments" (`OWNER-DECISIONS-2026-09-11.md` line 477). The write-ups are the session's; the owner's later rulings
27, 28 and 43 superseded them for boards C, P and B.

**Price, for every row: no quote exists.** JLCPCB publishes no PCB price endpoint (its paths return 404 without a
session) and the runner never logs into JLCPCB by standing rule (`LAYER-DECISIONS-2026-09-11.md`, last section). The
quote is one per board, at the real outline and quantity 5, at each candidate count, from the owner's ordering session.
That is the only input STK-002 still lacks on boards C, D, E and E5, and one of two on A, B and P.

## 3. Board by board

### 3.1 Board A: six layers decided; the copper weight is not

- **Layer count: DECIDED at six, measured.** The four-layer arm of 12 September (same tools, same router, 18 passes)
  ended 0 hard and **345 unrouted** with its autoroute completed in 51 minutes, where the six-layer A24 closed 0 and 0
  (`LAYER-DECISIONS-2026-09-11.md`, "THE ROUTE IS RUN AND THE ANSWER IS NO", VERIFIED in that record; the run itself is
  RECORDED). `boards/a.json` `_copper_layers_why` still says "OPEN ... no four-layer rerun with unknot.py was ever
  done"; that is stale, and a correction of the line (not of the count) is drafted for the integrator.
- **Layer use as committed (A32):** In1 and In4 carry no track (the two GND planes); In2 carries 554 track segments
  plus a VBAT pour and GND pours; In3 carries 365 segments plus power pours; F.Cu and B.Cu carry the generator's power
  bands (VBAT, VIN_RAW, CELL+, the slot rails) and the router's signals (census of the committed board file).
- **Copper weight: UNDECIDED.** The pack path (CELL+, CELL_FUSED, VBAT) is judged at 18 A under the session's ruling
  PWR-F12 (`v2/docs/feasibility/POWER-THERMAL.md` section 10) until a transient analysis at 60 s says otherwise. Under
  decision 35's model (`track_current.width_for_current`, 10 K) that is:

  | Copper for the 18 A pack path | Width needed | Source |
  |---|---:|---|
  | one outer face, 1 oz | **23.91 mm** | `track_current.py`, reproduced by `v2/docs/layout-constraints/calc/rail_widths.py` |
  | two outer faces at 1 oz sharing equally | 6.72 mm each (13.44 mm of band in all) | the same model at 9 A per face; INFERRED equal share, see below |
  | one outer face, 2 oz | **11.95 mm** | the same |
  | two outer faces at 2 oz sharing equally | 3.36 mm each | the same |
  | an inner layer, 0.0152 mm | 195.8 mm (not a conductor this board can hold) | the same |

  `POWER-THERMAL.md` lines 468 and 971 and `v2/docs/records/rv-pwr/pwr-chain-redeclaration.yaml` quote 16.18 mm and
  8.09 mm (appendix 32.244, the IPC-2221A fit), which decision 35 replaced on 21 September; a correction is drafted
  for the integrator, with the re-pin of the two registry readings bound to that page.

  **The two-face row is the finding this page adds, and it is INFERRED, not measured.** The ruled model is a
  single-conductor curve fit and it is strongly sublinear above its crossover, so two bands each carrying half the
  current need far less copper in total than one band carrying all of it. Two things the fit does not model decide
  whether the row holds: the share each face actually carries (a dc_drop reading on the routed board gives it per
  layer; on board E7, with its In2 pours deleted, B.Cu carried 97 percent of CELL_F's current, so an equal share is
  not automatic) and the heating of two bands stacked through 1.6 mm of laminate, which the single-conductor curve does not include.

  **What decides it:** (1) the transient analysis of the pack-path copper at 18 A for 60 s that PWR-F12 names (board
  A's stream; none exists at `e3aedb25`); (2) whether board A's floor plan holds the 1 oz bands (23.91 mm on one face,
  or about 6.7 mm on each face with vias tying them at both ends, sized by `via_current.barrels_for`: 21 barrels of
  0.4 mm at each transition carrying 18 A); (3) only if 2 oz is the answer, the price, which is the owner's (the P0
  rule; `pcb_requirements.yaml` FEA-004's layout-entry stage names it so).

  **What 2 oz outer would cost besides money** (VERIFIED against `v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md`,
  "The 2 oz rows of the capability page"): minimum track and space 0.15 / 0.15 mm on a multilayer board at 2 oz, a
  0.20 mm solder-mask bridge and a 0.254 mm PTH annular ring. Every class in board A's committed project file carries
  a 0.127 mm clearance except HV and RF (0.18 mm), and its USB class is 0.127 / 0.13 mm (read from
  `pcb-a-power-a23/pcb-a-power.kicad_pro`), so 2 oz outer would move board A's class table, which is on the same
  reserved floor, and its USB pair geometry. **No six-layer 2 oz row is in `STACKS`**; JLCPCB's impedance page serves
  six-layer rows at 2 oz outer through its selector (`B-FEASIBILITY.md` section 4, the first source row), and one would
  have to be transcribed under an authority before board A could be generated on it.

- **Session recommendation, not taken here** (the choice belongs to board A's stream with the transient analysis):
  keep 1 oz and carry the pack path as generator-laid bands on both outer faces, stitched at both ends, with the share
  per face read by dc_drop on the routed board; go to 2 oz only if the transient analysis and the floor plan together
  refuse that. Reason: it spends no money, moves no reserved class, and keeps the USB class buildable. Reversal: if
  the per-face share or the stacked-band heating defeats the two-face row, the 2 oz row is the fallback, with its price
  to the owner.

### 3.2 Board B: undecided, and what each option gives

See section 4.

### 3.3 Board C: six layers decided, not yet generated

- **DECIDED (owner decision 27, 25 September 2026):** six layers on JLC06161H-3313, regenerated as its next phase;
  the six-layer price quoted in the ordering session before anything is paid (`pcb_decisions.yaml` n 27).
- **Layer use:** F sig, In1 GND, In2 and In3 routing, In4 GND, B sig: "Every signal layer then has a plane next to it
  (In2 against In1, In3 against In4)" (decision 27's option 1 in `OWNER-DECISIONS-2026-09-11.md`, which the ruling
  took). In2 and In3 are 0.1088 mm apart through the 2116 prepreg, so a long parallel run on the two is broadside
  coupling; board C carries no impedance-targeted pair (its USB is full speed, `pcb_interfaces.yaml` board c) and its
  fastest nets are the RP2040's QSPI and crystal (`boards/c.json` signal classes), so this is a routing guideline
  (cross In2 and In3 runs at right angles where they overlap), not a hold.
- **Measurement:** C24's eighteen failing nets are all B.Cu runs whose only neighbour is In2, the routing layer, the
  longest 172.9 mm of SCL (decision 27 evidence); two routing layers left 14 to 35 open in the driver cluster
  (6 September); the six-layer arm routed 0 and 0 in 14.7 minutes (16 September, `boards/c.json`).
- **Stale records:** `boards/c.json` `_copper_layers_why` says "OWNER DECISION 27 IS OPEN"; a correction is drafted.
  The line stays `copper_layers: 4` until board C is regenerated, because it declares the board this tree holds
  (the same convention `boards/p.json` states for P).

### 3.4 Board D: four layers decided on the RF reason

- **DECIDED at four** (JLC04161H-7628): "a solid ground plane under the SA868 exciter, the PA stage and the filter is
  an RF requirement and the return path for every one of those stages" (`LAYER-DECISIONS-2026-09-11.md`, "D APRS: four
  layers, decided on the ground plane rather than on routing").
- **Layer use:** In1 GND; In2 a plane (on D12: +5V_D8 and GND pours and 6 track segments), which is decision 27's D
  measurement, In2 as a ground plane with two routing layers, routed 0 hard and 0 unrouted over three rounds on
  15 September (`OWNER-DECISIONS-2026-09-11.md`, decision 27, "Measured since"; `boards/d.json` `_copper_layers_why`).
  The same measurement read 13 of 127 signal nets over the RET-001 screen by 0.3 to 11.7 mm, every millimetre over the
  nets' own via anti-pads.

### 3.5 Board E: four layers decided on routing and In1

- **DECIDED at four** (JLC04161H-7628). The power half of the old argument is refuted: deleting In2's 5,500 mm2 of
  power pour cost CELL_F 13 mV and VIN_RAW 28 mV on E7 (`LAYER-DECISIONS-2026-09-11.md`, "E, measured 12 September
  2026"). What holds four layers is In1 (the solid ground) and routing on a 267 mm strip whose open nets were
  end-to-end (USB_E6_P 196 mm, GEIGER_IN 214 mm).
- **Layer use as committed (E17):** no router track on In1 or In2 (the committed board file carries 9 locked,
  generator-laid In2 segments on CELL_F at P_CP); In2 carries CELL_F, PV_P, TRK_OUT and VIN_RAW
  pours and a GND fill (decision 27's E treatment, `boards/e.json` `_copper_layers_why`).
- **The tracker's maker on layer use** (`v2/vendor/power/lt8705a.pdf` p.35, Circuit Board Layout Checklist): a ground
  plane layer with no traces, as close as possible to the layer carrying the power MOSFETs, which In1 is (0.2104 mm
  under F.Cu); and no GND or VIN copper under the SW1 and SW2 regions, which cuts In2's PV_P pour and GND fill (and any
  B.Cu pour) back from under the tracker's switch nodes (`layout-constraints/E.md` section 1). Neither changes the
  count.
- **Contradiction to carry (section 6 item 5):** the energy chain declares board E's pack-path bands as 2 oz; board E's
  stack is 1 oz outer.

### 3.6 Board P: four layers at 2 oz outer decided; the inner weight is not

- **DECIDED (owner decision 28 and ruling 7):** four layers, 2 oz outer. P8 (four layers, In1 and In2 as ground
  planes, the fabricator's 0.16 mm floor) routed 0 hard and 0 unrouted of 35 nets with 98 vias in six minutes; two
  layers left 43, 45 and 47 open at the same floor (`pcb_decisions.yaml` n 28 evidence).
- **Stackup row recorded:** JLC04162H-7628 (0.5 oz inner, the fabricator's default), in `STACKS` since `d468613e`.
- **Inner copper weight: UNDECIDED.** `stackup_write.py` says so in its own comment ("choosing one is an engineering
  decision that has not been taken"). The candidates are the fabricator's own codes at four layers, 1.6 mm, 2 oz outer
  (VERIFIED, `jlcpcb-stackups-2026-09-25.md`): 0.5 oz inner JLC04162H-7628 (default, recorded); 1 oz inner
  JLC041621-7628 (default of its group, 1.636 mm); 2 oz inner JLC041622-3313 (1.589 mm). Only the first is in `STACKS`
  layer by layer.
- **What decides it:** whether the inner GND planes carry a meaningful share of the pack current. On board P the pack
  current returns from PACK_N through the 2 mOhm shunt R10 onto GND, the cell block's negative
  (`PCB-BRING-UP.md` board P; `boards/p.json` `_pack_n_is_declared_and_measured`), so with In1 and In2 as GND planes
  the return between R10 and the block lead shares onto the inner copper through every GND via. The deciding reading
  is dc_drop on board P's first four-layer candidate with GND declared as a return of PACK_P (the `returns=`
  declaration `intent.rail` has taken since 20 September): if the inner planes carry less than the share at which a
  0.0152 mm plane's density passes at 18 A, 0.5 oz stands and no new row is needed; if not, the 1 oz inner row is
  transcribed into `STACKS` (a reserved-floor edit that decision 28's own authority covers only for the recorded row,
  so it needs its own line in `pcb_decisions.yaml`) and its price is the owner's.
- **The pack path at 18 A on 2 oz outer** (PWR-F12 carried to board P's chain stages PACK_CELLS and PACK_FETS): 11.95
  mm on one face, or 3.36 mm on each face if both share equally (INFERRED as for board A). Board P carried its pack
  current "in 3 mm bands on both faces" (`LAYER-DECISIONS-2026-09-11.md`, the P row), which is under 3.36 mm; the
  next generation's bands are sized in `v2/docs/layout-constraints/P.md`.

### 3.7 Board E5: two layers at 2 oz decided

- **DECIDED (owner ruling 7 of 12 September 2026):** 2L-2oz. The board carries the pack current through four CELL+
  and four return spring-pin targets (`pcb_energy_chain.yaml` stage DOCK_BLOCK, 36 A for the pin set) and has no
  inner layer to weigh.
- **STK-001 residue:** the board file carries epsilon_r 4.6 where the 2L-2oz row says 4.5; it closes with the re-cut
  of its deliverable folder, not alone (`boards/e5.json` `_stk001_residue_why`).

## 4. Board B: six re-assigned or eight, solved

Board B's layer question is the one of the seven that is genuinely open. The owner ruled on 25 September to measure
the eight-layer option first (decision 43), and `B-FEASIBILITY.md` section 5 names a second legal option on the same
six layers (A2: In3 becomes a ground plane). Neither had a pair-width solve behind it (`B-FEASIBILITY.md` section 4,
last paragraph: "the layer assignment and pair widths are TBD from a solve on that row"). This page supplies it.

**The solve** (`v2/docs/layout-constraints/calc/stack_solves.py`, output `stack_solves.out` beside it; atlc 4.6.1 at
200 px/mm on the rented box, 27 September 2026 00:23 UTC (02:23 CEST), the driver's sha256 printed in the output's
first line; EXPERIMENTAL desk evidence, it authorises no layout). The driver follows `v2/ecad/tools/impedance_2d.py`'s
convention and colour code and adds one thing that tool lacks: two dielectrics with their own constants above and below an inner trace. **It reproduces both of the tree's recorded
calibration solves exactly** (6L outer 0.127 / 0.127 masked 90.7 ohm; inner symmetric h 0.6057 102.0 ohm). Widths
are interpolated between solved points; the 200 px/mm grid is 5 um, so a single step in width moves a result by up to
about 2 ohm (INFERRED from the table's own steps).

Width (mm) for the differential target at each gap, 1 oz outer with solder mask, 0.0152 mm inner:

| Cross-section | 85 ohm (PCIe at the M.2 module) at gap 0.127 / 0.152 / 0.200 | 90 ohm (USB, PCIe at the CM5) | 100 ohm (Ethernet links, HDMI) |
|---|---|---|---|
| 6L outer (F over In1, B over In4), as built | 0.153 / 0.166 / 0.180 | 0.130 / 0.145 / 0.160 | 0.098 / 0.112 / 0.125 |
| 6L In2 as B21 uses it (In1 GND 0.55 above, In4 split 5 V 0.674 below, In3 routing) | not reached at 0.21 | 0.208 at 0.127; not reached at the wider gaps | 0.144 / 0.173 / not reached |
| 6L option A2: In2 between In3 GND (0.1088) and In1 GND (0.55) | 0.139 / 0.148 / 0.163 | 0.121 / 0.132 / 0.143 | 0.090 / 0.099 / 0.112 |
| 8L JLC08161H-2116 outer (F over In1, B over In6, 0.1164) | 0.170 / 0.184 / above 0.20 | 0.148 / 0.162 / 0.180 | 0.107 / 0.122 / 0.141 |
| 8L inner (a plane 0.1528 away through 2 x 1080, the other 0.3 away through the core) | 0.171 / 0.185 / 0.206 | 0.148 / 0.163 / 0.182 | 0.112 / 0.129 / 0.143 |

Where the as-built In2 reads 110.5 ohm at B21's 0.127 / 0.152 DIFF100 geometry with the In4 plane under it, it reads
140.5 ohm where In4's split leaves no copper under the pair (`boards/b.json` `_pair_inner_layer_why`, RECORDED); both
miss 100. The fabricator's standard impedance tolerance is plus or minus 10 percent and its track-width tolerance plus
or minus 20 percent (`jlcpcb-pcb-capabilities-2026-09-16.md`); its multilayer 1 oz floor is 0.09 / 0.09 mm, so every
width above is buildable, A2's 100 ohm at gap 0.127 sitting on the floor.

**What the numbers say** (INFERRED from the table):

1. **Both candidates give one class width per target on every routing layer.** On the eight-layer row the outer and
   inner widths agree within 0.005 mm at gap 0.127 (85 ohm 0.170 against 0.171; 90 ohm 0.148 against 0.148; 100 ohm
   0.107 against 0.112), and on A2 within 0.008 to 0.014 mm (90 ohm 0.130 against 0.121). That removes the trade `boards/b.json` `_pair_inner_layer_why`
   names, that a KiCad class applies one width to every layer so the outer and inner geometries fight.
2. **A2 costs a routing layer on the board that does not route with four.** A2 keeps three controlled routing layers
   (F, In2, B), losing In3, which carried 3,379 track segments on the routed B21 (`B-FEASIBILITY.md` section 3.2), and
   B.Cu still sits over the four split 5 V planes on In4. Board B left 416 connections open with four routing layers
   (B21); A2 is therefore not a candidate on its own, only with a floor plan that cuts the routing demand
   (`B-FEASIBILITY.md` option A4).
3. **Eight layers give four controlled routing layers.** With JLC08161H-2116 the tightly spaced pairs are (F, In1),
   (In2, In3), (In4, In5) and (In6, B), and the three 0.3 mm cores separate them. Four routing layers each with a
   plane on its prepreg side leave one power layer, and one inner routing layer then has the power layer as its near
   reference: for S G S G P S G S it is In5, 0.1528 mm under In4. A pair on that layer holds its impedance only while
   In4 is solid under it; where In4 splits between the 5 V domains the near reference is gone. So either pairs on In5
   stay inside one 5 V region or each crossing carries the stitching capacitor RET-003 asks for at a reference change
   between potentials. The alternative S G S G S G G S puts no plane on power and carries the four 5 V domains (up to
   5 A peak each, `rail_widths.out`) as bands on routing layers, which board B's floor plan has no room for
   (`B-FEASIBILITY.md` section 3.3).

**What decides board B's stackup, in order:**

1. The corrected netlist on `main` (round 8's board B stream; FB-FAB-1 to FB-FAB-5), because every route before it
   measures a circuit that is not the design (`B-FEASIBILITY.md` Appendix A).
2. Q-B-ESC-2 (`B-FEASIBILITY.md` section 7.9), which tests the escape and placement remedy on the corrected inputs,
   and decision 43's whole-board eight-layer route. **This page's recommendation for that run's input, the session's
   and not a stackup decision:** S G S G P S G S on JLC08161H-2116, with the four 5 V domains on In4, the pair classes
   at 0.148 / 0.127 mm (90 ohm, the USB class, which also meets the M.2 module's 85 plus or minus 10 percent) and
   0.112 / 0.127 mm (100 ohm, DIFF100; at 0.112 the outer layers interpolate to about 98.8 ohm, inside the
   plus or minus 10 percent), pairs on In5 kept inside one 5 V region. Reason: it is the only layer use in the table
   with four controlled routing layers. Reversal: the run's own reading.
3. If eight layers route and six do not, the owner receives the eight-layer price with the quote before any order
   (decision 43). If eight layers do not route either, decision 43 returns with that number; since the owner's standing
   rule of 26 September the choice that comes back is taken by the session on the evidence and only a price goes to
   the owner (`B-FEASIBILITY.md` section 6 item 4).
4. **The fabricator row it needs is recorded** (JLC08161H-2116, `STACKS` since `d468613e`, equal layer by layer to the
   filed transcription). One question to JLCPCB stays open and is not blocking: which dielectric constants it designs
   to on that code, the calculator's per-layer 4.16 / 3.91 / 4.41 or the impedance page's single core 4.6
   (`B-FEASIBILITY.md` section 4 and section 6 item 6; the inquiry text is the session's, sending it is the owner's).

## 5. Everything still owed, in one list

| Item | Board | Kind | Closes when | Owner |
|---|---|---|---|---|
| copper weight of the pack path | A | engineering, then money if 2 oz | the 60 s transient analysis and the floor plan (section 3.1) | board A stream; the owner for a 2 oz price only |
| layer count and layer use | B | measurement, then money | corrected netlist, Q-B-ESC-2, decision 43's run (section 4) | integrator for the run order; the owner for the price |
| inner copper weight | P | engineering | dc_drop on the first four-layer P with GND declared as a return (section 3.6) | board P stream |
| six-layer regeneration | C | work | board C's next phase on JLC06161H-3313 | board C stream |
| price at each candidate count, real outline, quantity 5 | all seven | money (a quote, no spend) | the owner's ordering session | owner |
| Dk the fabricator designs to on JLC08161H-2116 | B | question to a supplier | JLCPCB's answer | owner sends; session drafts |
| Dk 4.6 against 4.5 in the board files of the two-layer boards | E5 (and P4 until P is regenerated) | record | the re-cut of the deliverable folder | board E5 / P streams |

## 6. Contradictions this page names

1. `LAYER-DECISIONS-2026-09-11.md` ("B compute: six layers, evidenced, stands"; "C panel backer: four layers,
   decided"; P "two layers, decided") against owner decisions 43, 27 and 28 of 25 September 2026. This page carries the
   decisions; that page's measurements stand.
2. `boards/a.json` `_copper_layers_why` ("OPEN ... no four-layer rerun ... was ever done") against the four-layer arm of
   12 September (345 unrouted); `boards/c.json` `_copper_layers_why` ("OWNER DECISION 27 IS OPEN") against decision 27
   ruled. Corrections of both lines, and of `boards/b.json` and `boards/p.json`, are drafted for the integrator.
3. The STK-002 rows of every `PCB-RULE-STATUS-<board>.md` read "an owner decision is open" where decisions 27, 28 and
   43 are ruled; what is missing is the price. A correction of the coverage note that page renders is drafted for
   the registry writer.
4. `POWER-THERMAL.md` (lines 468 and 971) and `records/rv-pwr/pwr-chain-redeclaration.yaml` give board A's pack path as
   7.19 / 16.18 mm at 1 oz and 3.60 / 8.09 mm at 2 oz (IPC-2221A, appendix 32.244); decision 35's model gives 8.15 /
   23.91 and 4.08 / 11.95 (`power_copper.py` docstring). A correction is drafted for the integrator.
5. **New:** `pcb_energy_chain.yaml` stage DOCK_ENTRY declares "board E's 2 oz power bands ... IPC-2221 at 2 oz",
   rating 25 A, and the draft `pwr-chain-redeclaration.yaml` lists "board P and board E 2 oz bands" as rated above 18 A;
   board E is JLC04161H-7628 with 0.035 mm outer copper (its committed board file, and no owner ruling puts E at 2 oz:
   ruling 7 covers P and E5). At 18 A for 60 s the band needs 23.91 mm on one 1 oz face. Named for the energy-chain
   writer (the battery-protection stream); the constraint is in `layout-constraints/E.md`.

## 7. Rule gaps this page found

- **No layout-entry check that a stackup is decided.** STK-001 is ROUTED_BOARD and STK-002 RELEASE_PACKAGE, so the
  staged layout-entry test (`rules_status.layout_entry`) can admit a board whose stackup is undecided, although the
  owner's section 5 names the stackup among the inputs layout entry requires. A draft rule, STK-003, is with the
  registry writer.
- **No pre-layout impedance feasibility check.** IMP-001 is ROUTED_BOARD; the question "can the chosen stack meet each
  pair class's target at a buildable width" (the one section 4 answers for board B) has no layout-entry gate. A draft
  rule, IMP-003, is with the registry writer (the registry already has an IMP-002 about class clearances).

## 8. How to re-run what this page quotes

- Pack-path and rail widths: `python3 v2/docs/layout-constraints/calc/rail_widths.py --markdown` (stdlib plus
  `v2/ecad/tools/track_current.py` and `via_current.py`; any host, under a second).
- The board B solve: `v2/docs/layout-constraints/calc/stack_solves.py --jobs 12` on a host with atlc 4.6.1 and
  Pillow (on the rented box it was run from `/root/hc9` with atlc extracted from Ubuntu's `atlc_4.6.1-6build1` package;
  30 s wall time on 12 workers). The runner has no atlc.
