# l9stk: one stackup decision per board, with its measurement and its cost (Layer 9 item 9.12, MESHSAT-1357)

3 October 2026, the Layer 9 author of item 9.12, worktree `l9stk` on branch `fnd/l9stk` from set 28's tip `37bc2f1d`.
Prototype design and desk work: no V2 board has been fabricated, ordered, assembled or powered; nothing was routed, no
quote was requested, nothing was bought. This record writes one stackup decision per board (A, B, C, D, E, P, E5) as the
design input the supplier's layout phase receives: the layer count with the measurement that forced it (or a bound derived
by a stated method, or the words NO MEASUREMENT HELD), the cost it adds from dated public price readings (or NOT READ),
the stackup itself (layer roles, copper weights, the fabricator's row, the impedance targets with their geometry from the
repository's 2D field solves) and the decision with its authority. No registry, generator, `stackup_write.STACKS`, board
file, constraint sheet or `LAYER-STATUS.md` is edited; the decisions reach `pcb_decisions.yaml` through the apply script,
run by the integrator.

| File | What it is |
|---|---|
| `L9-STACKUPS.md` | The page: the rule and the labels, the seven decisions in one table, one section per board (measurement, copper, stackup, impedance, decision), the price readings and the per-board cost table, the owner decisions, the findings for other authors, how to re-run |
| `l9stk_stackups.py` | The calculation, from the repository root: `python3 v2/docs/records/l9stk/l9stk_stackups.py` (stdlib plus `track_current.py` and `via_current.py`; no KiCad, no network). It pins 22 inputs by sha256 and computes the outlines from the committed board files, the band widths at 1 oz and 2 oz under decision 35's model, the bounds on board E's cross-section, on the pack return on the inner planes of A and E and on board P's inner planes' share, the 2 oz floors and the 0.4 mm pitch gaps, the impedance geometry from `stack_solves.out`, the price figures and deltas at their printed conditions, and the predicates the test reads |
| `l9stk_stackups.out` | Its output, committed; regenerated only through `_bin/regen_out.py <worktree> v2/docs/records/l9stk/l9stk_stackups.py v2/docs/records/l9stk/l9stk_stackups.out` |
| `apply_decisions_l9stk.py` | The seven decisions and the open owner decision `(L9STK CU)` as data, and the script that appends them to `v2/ecad/tools/pcb_decisions.yaml` (numbered one above the register's highest when it runs; the marks `(L9STK A)` to `(L9STK E5)` and `(L9STK CU)`); it screens every text, refuses a second run, checks nothing else moved and re-parses the file. It checks by default and writes only with `--write`; `--registry PATH` works on a copy. The integrator runs it once with `--write`, then `python3 v2/ecad/tools/decisions_render.py` |
| `l9stk_copper.py` | The copper question (page section 14, revised 4 October 2026 after the check COPPER: NOT CONFIRMED; a candidate copper-sizing result, not completed fault-protection verification), from the repository root: `python3 v2/docs/records/l9stk/l9stk_copper.py` (PyYAML, pdftotext and the tool modules; no KiCad, no network). It pins 25 inputs by sha256 and prints the currents by class, decision 35's model applied to a band's two outer faces and its adjacent return as one conductor, the parts' printed limits from the worst inside air, the split and both barrel conventions, the widths per conductor at 1 oz and 2 oz, every class on the band families with its failing rows, the series parts, board E's cross-section, the owner's coordination table with a disposition per row, and the predicates the test reads |
| `l9stk_copper.out` | Its output, committed; regenerated only through `_bin/regen_out.py <worktree> v2/docs/records/l9stk/l9stk_copper.py v2/docs/records/l9stk/l9stk_copper.out` |
| `apply_energy_chain_l9stk.py` | The energy chain's DOCK_ENTRY, SHORE_INPUT and BOARD_A_NODE conductor texts at the revised widths and the 25 A blade's citation (MINI 297 for ATOF 287, six stages), for the integrator: it refuses until the register carries `(L9STK A)` and `(L9STK E)`, accepts the tree's texts or record l8r2's, and is a no-op on a second run; it REPLACES record l8r2's `apply_energy_chain_e1oz.py`. `--check` (the default) writes nothing |
| `apply_blade_plating_l9stk.py` | Pins the 25 A MINI blade's silver terminals (0297025.WXNV) in `v2/vendor/SOURCES.yaml`, for Layer 6; `--check` is the default |
| `l9stk_protection.py` | The pack path's protection (page section 15, the owner's correction of 4 October 2026), from the repository root: `python3 v2/docs/records/l9stk/l9stk_protection.py` (PyYAML, pdftotext and the copper script; no KiCad, no network). It pins 19 inputs by sha256 and prints board P's existing protection with its FETs welded, Q39/Q40's 150 C current with its uncertainty, the selected LM5069-2 breaker on board P (sense window, power limit, fault timer, dv/dt start, retry, the CSD18510Q5B's SOA derated by SLVA673A equations 4 to 7, the clamps, the charge direction), the docking correction (the make-last enable into UVLO) with the uncorrected excursion, the battery FETs' junction limit and the third FET selected, every series part at the breaker's largest limit, the owner's protection table, the design defects with owners, the interface demands, the missing evidence with specimen, acceptance and task, and the predicates the test reads |
| `l9stk_protection.out` | Its output, committed; regenerated only through `_bin/regen_out.py <worktree> v2/docs/records/l9stk/l9stk_protection.py v2/docs/records/l9stk/l9stk_protection.out`, after `l9stk_copper.out` |
| `fetch_held_back.py` | Fetches TI's SLVA673A (the owner's named calculation basis, no grant to redistribute) into the ignored `v2/vendor/ti/held/` and checks its sha256; never run by a test |
| `inputs/csd18510q5b-figure-readings-2026-10-04.json` | The CSD18510Q5B's Figure 10 (SOA) and Figure 8 (RDS(on) against temperature) read at 300 dpi: the segments' pixel ends, the axes, the reading uncertainty and the sheet's sha256/16 |
| `inputs/price-readings-2026-10-03.json` | The public pages read on 3 October 2026 (JLCPCB and NextPCB), each with its URL, read time, the page's own date where printed and the sha256/16 of the page as fetched; the sentence carrying each figure kept verbatim, never the page; what was not read |

The predicates are held by `v2/ecad/tools/tests/test_l9stk.py`: `env -C v2/ecad/tools/tests python3 run.py test_l9stk test_energy_chain test_public_hygiene` (the protection tests skip, named, where SLVA673A is not held).

## The decisions in short

| Board | Stackup | Measurement | Cost at five boards, real outline | Authority |
|---|---|---|---|---|
| A | 6 layers, JLC06161H-3313, 0.5 oz inner, 1 oz outer as the design input; the pack path and its return at the blades' 25 A, a band's faces and its return as one conductor: 38.79 to 39.14 mm a face at 1 oz (a 78.29 mm corridor), 19.39 to 19.57 mm at 2 oz; the outer weight open to the owner (L9STK CU) | MEASURED: four layers 345 unrouted, six 0 and 0; DERIVED BOUND (section 14) | NOT READ | count SESSION; outer copper OWNER (L9STK CU) |
| B | 8 layers, JLC08161H-2116, S G S G P S G S, 1 oz / 0.5 oz; USB 0.148 / 0.127 mm, DIFF100 0.112 / 0.127 mm | MEASURED: 93 opens without two inner signal layers, 416 open on six, six cannot hold one width per class; NO MEASUREMENT HELD of a route at eight | NOT READ; the eight-layer price to the owner before any order (decision 43) | SESSION, conditional on decision 43's route |
| C | 6 layers, JLC06161H-3313, In1 and In4 GND, 1 oz / 0.5 oz, no controlled pair | MEASURED (decision 27) | NOT READ; before payment (decision 27) | count OWNER (27); copper SESSION |
| D | 4 layers, JLC04161H-7628, In1 GND, In2 a plane; RF 50 ohm at 0.332 mm | MEASURED: In2 as a plane routes 0 and 0; DERIVED BOUND: two layers cannot give a plane beside both routing faces; NO MEASUREMENT HELD of a two-layer route | NOT READ | SESSION |
| E | 4 layers, JLC04161H-7628, 0.5 oz inner, 1 oz outer as the design input; the pack path, its return and the shore input at their coordination currents, a band's faces and its return as one conductor: the pack end 78.29 mm a face at 1 oz (over the 68 mm strip), 39.14 mm at 2 oz | MEASURED: the routing half and the tracker maker's plane; DERIVED BOUND (section 14) | NOT READ | count SESSION; outer copper OWNER (L9STK CU) |
| P | 4 layers, JLC04162H-7628, 2 oz outer, 0.5 oz inner with In1 and In2 at least 16 mm wide beside the pack return | MEASURED (decision 28); DERIVED BOUND: a plane is over its rating only when necked to 2.80 to 15.45 mm | NOT READ | count and 2 oz OWNER (28, ruling 7); inner SESSION |
| E5 | 2 layers, 2L-2oz, Dk 4.5 | DERIVED BOUND: a plated board needs two layers; NO MEASUREMENT HELD (no routing) | NOT READ | count and 2 oz OWNER (ruling 7); Dk and widths SESSION |

**One open owner decision, `(L9STK CU)`** (section 14.7): the outer copper weight of boards A and E's pack path and shore
input, 2 oz or 1 oz with a layout change, because the 1 oz widths (a band and its return 78.29 mm a face) do not fit board E's
strip and are not shown on board A's floor plan; the session recommends 2 oz on E and 1 oz on A if the corridor is shown. P's
inner weight stays the session's. The owner gates that stand: decision 43's eight-layer price for board B and decision 27's six-layer price for
board C, both before any order or payment; and A to 2 oz, E to 2 oz, P to 1 oz inner if a reversal fires
(`L9-STACKUPS.md` section 11). Every price at a board's real outline is NOT READ and left to the supplier's quotation
(EQ-14).

**W4DP-F2's element, designed (section 15; drafted, not drawn; revised after the recheck PROTECTION: NOT CONFIRMED):** an
LM5069-2 circuit breaker on board P from Q2's source to PACK_P, with two CSD18510Q5B and a 2.6087 mOhm sense (4 and 7.5 mOhm in
parallel): its actual limit 18.32 to 23.93 A, so the 10 A and the 18 A for 60 s never trip it and the cells' 24 A is never
passed; above a unit's limit it clears within 1.29 ms with no firmware and with Q1/Q2 welded; a 0.659 A dv/dt start; the FET's
SOA at 0.57 and 0.58 of the derated curve (TI asks 0.67). B-P1: a make-last dock contact into its UVLO (C-1b, TI's Figure 45)
turns every docking into that start; without it a docking reached 2.64 times the derated 10 us line and 0.634 V across the
sense. B-P2: the battery FETs' target is a junction limit with the band and R17 in place (150 C at 23.93 A from 76.25 C); a
third BUK6Y10-30P is selected, (Zself + 2 Zmut) at most 45.88 K/W with R17 designed apart, the pair at 20.39 K/W the fallback,
E11-37 deciding its Ciss. Open: DD-1 to DD-6 with their owners, IF-1 to IF-6, the evidence E-1 to E-11 and the maker questions
Q-TI-L9S-1 and Q-TI-17. (L9STK CU) lists option (4), the zero-cost route with each return laid apart, not credited by decision
35's model and waiting on a coupon.

## Proposed LAYER-STATUS row (for the integrator; `LAYER-STATUS.md` is not edited here)

| Item | Criterion | Status | Evidence |
|---|---|---|---|
| 9.12 | stackup decided per board with measurement and cost | PARTLY | one decision per board in `v2/docs/records/l9stk/` with its measurement, derived bound or NO MEASUREMENT HELD (A 6L 1 oz with two-face bands; B 8L as the design input, conditional on decision 43's route; C 6L by decision 27; D 4L; E 4L 1 oz with two-face bands; P 4L 2 oz, 0.5 oz inner with 16 mm planes; E5 2L 2 oz), appended by `apply_decisions_l9stk.py`; the cost half NOT READ at any real outline (the public readings of 3 October 2026 print start prices and rates only), EQ-14 open for the supplier's quotation |

The row in that page's long table (line 1713) would read the same way: "no" becomes "partly: decided per board with
measurement or bound (records/l9stk); no price at any real outline; B conditional on decision 43's route".

## What other authors own (from `L9-STACKUPS.md` sections 12, 14.9 and 15.7)

- L9C-F16 to L9C-F22 (section 14.9, from section 15): the breaker drawn into board P with its layout and its energy chain
  stage; E11-29 restated as a junction limit with a third battery FET; board A's loads held off during the breaker's start;
  the power limit's accuracy, its limits at the pack's voltage and the hot short (Q-TI-L9S-1, the supplier's evidence); the
  make-last dock enable; BAT-F20 at the breaker's held current; the pack's terminal live only while docked.
- L9C-F1 to L9C-F15 (section 14.9): the energy chain's texts through `apply_energy_chain_l9stk.py` instead of record l8r2's
  draft; BOARD_A_CONVERTERS' 25 A claim for the branches; the series parts in the blade's held band with the gauge failed
  (R17, the XT60, the dock pins, Q39 and Q40, the 3568 holder's missing rating) beside W4DP-F2; R19 in F1's 600 s window;
  P_CP and P_CN as plated-through lands; the pack return as GND with l8r2's drafts; TRK_OUT and the solar input outside the
  energy chain; the plane screen's limit; the laminate's maximum and the 2 oz price in the supplier's quotation.

- Boards A and E declare no return of the pack path on their intents; the return needs the pack path's bands (the board
  A and board E streams).
- `pcb_energy_chain.yaml` DOCK_ENTRY's "board E's 2 oz power bands" against board E at 1 oz (the energy chain's writer).
- The 2 oz multilayer floor: 0.15 mm in the tree's transcription and `layout-constraints/P.md`, 0.16 mm in JLCPCB's copper
  weight guide of 9 September 2026 (the transcription's owner, the constraint sheets' writer).
- Board P's U1 (RSM0032A) leaves exactly the 0.20 mm 2 oz solder-mask bridge (board P stream, the supplier).
- `STACKUP-DECISIONS.md` and `layout-constraints/A.md`, `B.md`, `E.md`, `P.md` section 1 still read UNDECIDED where this
  record decides (the integrator, after the apply).
- The quotation request's price lines per board (the supplier handover's author).
- STK-003 and IMP-003, named in `STACKUP-DECISIONS.md` section 7, are not in `pcb_rules.yaml` (the registry writer).
