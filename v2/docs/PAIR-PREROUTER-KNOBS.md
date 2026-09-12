# The pair pre-router's knobs, and which of them has a number behind it

12 September 2026 (MESHSAT-862). `tools/pair_preroute.py` is 2,063 lines and reads **43 environment knobs**.
This is the map: what each one does, what it defaults to, and **what it measured**, because a knob with no
measurement is a decision someone made once and nobody has checked since. Every number here is on one board
with one placement, named beside it; the record's standing caution applies to all of them, that a value which
wins one draw is a measurement and not a law.

The measurements are on B19's placed board (113 pairs) unless a row says otherwise. `boards/<letter>.json` is
where a board's own values live (`pair_env`), never the tool's defaults.

## Measured

| knob | default | what it does | what it measured |
|---|---|---|---|
| `PAIR_CORRIDOR_SLACK` | `0.12` | how much wider than the pair the corridor must be | **the one real lever.** Ten arms, 12 Sep: 0.03 lays 41, 0.04 44, 0.05 53, **0.06 57**, 0.07 52, 0.08 47, 0.10 48, 0.12 46, 0.14 49, 0.16 47. One peak, then a noisy plateau from 0.10 out. `boards/b.json` carries 0.06 |
| `PAIR_CORRIDOR_SLACK_SLIM` | `0.05` | the retry for a pair that found no corridor | a per-pair second chance; a board-wide 0.05 was worse than the retry (42 against 49 on the old tools) |
| `PAIR_FAST_STUBS` | on where numba is | the stub search on `pairsearch`'s compiled kernel | **the same board, faster:** B19 47 of 113 either way, the pass 1586 s to 976 s, the stub search 675 s to 46 s, **0 of 7,706 items differ**. D: 5 of 5 either way, 9 s to 3 s |
| `PAIR_FAST_SEARCH` | `1` | the corridor search on the same kernel | 13.5x compiled (2.26 M expansions a second against 167 k); `pairsearch.py selftest` refuses any difference |
| `PAIR_LAYERS` | `F.Cu,B.Cu` | the layers a pair may use | four layers lay 71 of 113 against 56, and every impedance-correct variant lands at or below 56; the per-class split is the answer (32.102) |
| `PAIR_INNER` | none | per-class inner geometry | 0.13/0.127 on In2/In3 reads 102 ohm on a 100 ohm class, inside tolerance; it is what makes the four-layer split legal |
| `PAIR_COVER_LEGS` | `0` | the corridor covers its own legs plus a grid cell | 45 of 113 against 47: the rounding class falls 25 to 10 and the failures move to the search. Off |
| `PAIR_LEG_EXACT` | `0` | re-test a blocked leg point against the polygons | 47 either way. The rounding is real and worth no pairs here. Off |
| `PAIR_SWAP` | `1` | exchange a station's two passives when the fans cross | D lays 2 of 5 without it and 5 of 5 with it |
| `PAIR_SWAP_BOTH_SIDES` | `0` | refuse a swap that crosses the parts' OTHER pads | D 3 of 5 against 5 of 5, and it prints why: the two sides of a series-resistor pair are mirror images, so uncrossing one crosses the other at every one of these stations. Off, kept for the sentence |
| `PAIR_MITRE_LIMIT` | `1.2` | above this multiple the outer join is arced | a right angle puts the mitre at 1.414 of the offset, 41 percent further out than the straights; the arc is strictly closer |
| `PAIR_EXPANSIONS` | `12000000` | the pair's whole search budget, counted in work | replaced a wall clock that decided results (32.90). 3 M laid 21 where a 300 s clock laid 38, so 12 M |
| `PAIR_RIPUP` | `0` | rip-up as a trial kept only when it pays | 29 of 113 as first written, and as an accept-if-better trial 106 episodes with **not one kept**. Off |
| `PAIR_ORDER` | `span` | longest pair first | it lays greedily and never rips up, so whichever pair goes first takes the room; alphabetical was an accident |
| `PAIR_ENTRY_VIA` | `0` | end a pair at the escape vias rather than the pads | +27 on B when it was first measured, **zero** on B19 later, and it costs D two of five. A per-pair fallback, not a mode |
| `PAIR_MAP_MODE` | `counts` | the occupancy maps counted once for the whole board | proved identical to the per-pair rebuild on all 75 of D's calls; the map share of a pass fell from 76 percent to 44 |
| `PAIR_STAIRCASE` | `1` | accept the corridor as the search found it | thirteen of the first twenty four failures were the refusal to; a staircase pair is coupled and can be straightened later |

## Measured at zero, which is worth as much

Seven arms at the peak slack on B19, 12 September (32.132), baseline **57 of 113**:

| knob | value | pairs |
|---|---|---:|
| `PAIR_LEG_EXACT` | 1 | 57 |
| `PAIR_EXPANSIONS` | 48 M against 12 M | 57 |
| `PAIR_STUB_EXPANSIONS` | 4 M against 400 k | 57 |
| `PAIR_STATION_OWN` | 1 | 57 |
| `PAIR_END_CANDS` | 48 against 12 | **53** |
| the per-class two-pass split | at 0.06 | **54** |

**Every knob that changes how hard the search works measures zero, and two measure worse.** The two that have
ever moved the number, `PAIR_CORRIDOR_SLACK` and `PAIR_LAYERS`, change the geometry the search is given. That
is the shape of the whole table: this tool's remaining levers are not in it.

## Declared and never measured

`PAIR_BUDGET` (the outer clock, 600 s a pair), `PAIR_END_CANDS` (12), `PAIR_END_LEGS`, `PAIR_END_OFFSET`,
`PAIR_GRID_LONG` and `PAIR_LONG_MM` (a coarser grid for long pairs, off), `PAIR_HOP_LAYERS`,
`PAIR_INNER_WIDTH` and `PAIR_INNER_GAP` (the pre-class form), `PAIR_ORDER_FILE`, `PAIR_PRESENT`,
`PAIR_RIP_MARGIN` / `PAIR_RIP_MAX` / `PAIR_RIP_TOTAL` (the rip-up shape, which never paid),
`PAIR_STATION_OWN` (new, its arm is running), `PAIR_STRIP_MM` (6.0), `PAIR_STUB_EXPANSIONS` (new, 400,000
inherited from a constant), `PAIR_WINDOW` (25 mm; 40 mm measured worse, 45 of 113), and the plumbing:
`PAIR_VENV`, `PAIR_DEBUG`, `PAIR_MAP_CHECK`, `PAIR_PLAN_MODE` / `PAIR_PLAN_IN` / `PAIR_PLAN_OUT` /
`PAIR_HIST_IN` / `PAIR_CONFLICT_OUT` (the negotiated router, measured and rejected at 22 to 25 of 113).

**That is seventeen knobs with a number and twenty six without**, in a tool whose output is the gate on four
boards. The ones worth measuring next are the ones that touch the two biggest failure classes of 32.131:
`PAIR_END_CANDS` and `PAIR_STUB_EXPANSIONS` at the station stubs, `PAIR_STATION_OWN` at the legs.

## 12 September 2026: the four knobs of the own-legs work (MESHSAT-862, appendix 32.135)

A pair that shorts its own partner was laid, kept and shipped into the pre-route DRC, and the repairs are four
guards. Each has a knob because each can cost pairs and the only way to know is to measure it on B19.

| knob | default | what it does |
|---|---|---|
| `PAIR_OWN_CLEAR` | 1 | the three emissions that used to lay copper unasked ask whether it lies on the partner |
| `PAIR_FOLD_TEST` | 1 | the two offset legs of a run judged against each other in the candidate ladder |
| `PAIR_UNMERGE` | 1 | a merge of two runs whose legs then fold is dropped and the runs laid one by one |
| `PAIR_FAN_BACK` | 1.0 mm | how far a diving leg is pulled back from the station before the other leg's fan is laid |
| `PAIR_CROSS_NET` | report | a laid pair sampled against a map that exempts its own two nets: `report` names the counterparty and the emission, `block` refuses the pair, `off` says nothing |

**`PAIR_CROSS_NET` reports rather than blocks, and that default is a measurement.** The test asks a RASTER grown
by the clearance plus half a leg, and the emitters deliberately relax that near a station (a direct leg runs pad
to pad past its neighbours' pads), so a cell it calls blocked is not yet a DRC violation: as a verdict it refused
one of D10's five pairs and one of A's three, on boards whose DRC reads 0 hard. The pre-route DRC remains the
authority on clearance; what this adds is the NAME of the counterparty and of the emission at the moment the pair
is laid, which is what turned twelve silent DRC items on A into one line naming `/USB_WALL`.

**A sixth knob is not a knob:** `legs_clear`'s entry region (the first and last 1.2 mm of a leg at an entry
station) asks the pads-only map and then, where that map refuses, asks the GEOMETRY through `_nearest_edge`
before the pair is lost. Asking the raster alone there cost B19's DIFF100 pass fourteen pairs.

**The bar inside all of them is half the pair's own pitch, not the class clearance**, and that distinction is
worth thirteen pairs: written as a second clearance test, the fold test took B19's DIFF100 pass from 22 of 48
to 9. A correctly coupled pair runs AT the class number on the inner-layer geometry (0.13 on 0.127), so a
clearance test inside the candidate ladder refuses the tool's own design. The class number is judged exactly
once, on the copper that was actually laid.

