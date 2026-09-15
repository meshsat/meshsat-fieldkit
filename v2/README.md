# V2: the Peli 1450 carrier set (MESHSAT-830 generation)

Seven KiCad 9 boards for the kit V2 go-box: a Peli 1450 case with the 1450PF panel frame. The power and compute boards stack on four M3 rods and lift out of the case in one piece; a dock strip on the case floor carries the 9 to 36 V front end, the solar tracker, the sensor controller and the raised contact block that the stack blind-mates onto, with eleven antenna paths mating at the same time. The control face is a 3 mm aluminium plate in the frame (`cad/face_plate.py`, `release/revA/case/face-plate/`) with a Xenarc 709GNK monitor lying on it, the backer board C7 hanging under it and the 30 W VHF module bolted to its underside; the built 4S smart pack lies in the pocket at the east end wall (appendix 32.62) and the eleven antenna couplers sit in the end walls at 88 mm. Nothing here has been built: the boards are designed, generated and checked, and no set has been ordered.

The rulings that bind the design (details in `docs/MESHSAT-709-geometry-appendix.md`, sections 32.49 to 32.61, and the specification `docs/V2-SPEC.md`): three identical Compute Module 5 slots with every radio and sensor a USB device shared by the HAL, k3s across the modules, and each hub bank switchable in hardware between its home module and a neighbour so one module's loss moves its peripherals rather than removing them (`docs/ARCH-PCB-B-IOHA.md`); the pack, the charger and the power control on PCB-A; no vent opening anywhere in the case; EMCON a hardware line from the panel toggle to every transmitter rail gate and to the amplifier keying, plus a software hold; the panel a USB device driven per `docs/PANEL.md`.

| Board | Rev | Size (mm) | Layers | Project | Deliverable folder |
|---|---|---|---|---|---|
| PCB-A POWER + I/O | A24 | 240 x 160 | 6 | `ecad/pcb-a-power-a23/` | `release/revA/boards/meshsat-pcb-a-revA-A24/` |
| PCB-B COMPUTE | B19 | 330 x 200 | 6 | `ecad/pcb-b-compute-b19/` | `release/revA/boards/meshsat-pcb-b-revA-B19-quote/` (quote only: placed, not routed) |
| PCB-C PANEL BACKER | C17 | 344 x 228 ring | 4 | `ecad/pcb-c-display-c8/` | `release/revA/boards/meshsat-pcb-c-revA-C17/` |
| PCB-D VHF APRS | D11 | 100 x 80 | 4 | `ecad/pcb-d-aprs-d9/` | `release/revA/boards/meshsat-pcb-d-revA-D11/` |
| PCB-E1 DOCK STRIP | E9 | 267 x 68 | 4 | `ecad/pcb-e1-dock-e7/` | `release/revA/boards/meshsat-pcb-e-revA-E9/` |
| PCB-E5 DOCK BLOCK | E5 | 43 x 26 | 2 | `ecad/pcb-e5-block/` | `release/revA/boards/meshsat-pcb-e5-revA-E5/` |
| PCB-P PACK BMS | P4 | 70 x 44 | 2 (2 oz) | `ecad/pcb-p-pack-p2/` | `release/revA/boards/meshsat-pcb-p-revA-P4/` |

The previous generation (A21, B15, C6, D7, E4, E5 with a single Compute Module, the Touch Display and a twelve-cell battery module) stays on the `revA` GitHub release and in the git history as the record; its deliverable folders are replaced as the new boards land.

**Build guide: [`BUILD.md`](BUILD.md)** walks from an empty cart to a running kit. This page is the map of the folder.

## Layout

| Path | Content |
|---|---|
| `docs/` | `MESHSAT-709-geometry-appendix.md` (the design record, every number and every ruling), `ASSEMBLY.md` (fasteners, torque, coating, removal procedure, bench-fit lists), `PANEL.md` (the software contract for the control panel, MESHSAT-773), `V2-SPEC.md` (the approved specification of the next generation, MESHSAT-830), `TEST-PLAN.md` (its qualification plan) |
| `ecad/` | the KiCad sources: one project folder per board, `meshsat.pretty/` (project footprints), `tools/` (the generators and the pipeline scripts) |
| `vendor/` | third-party reference CAD and datasheets (see `vendor/README.md`) |
| `release/revA/boards/` | the Rev A deliverables: KiCad project snapshot, Gerber zip, BOM, CPL, DRC report, schematic PDF, renders, 1:1 print |
| `release/revA/order/` | the JLCPCB order set: per-board upload folder with `ORDER-NOTES.txt`, `ORDER-LOG.md` (what was uploaded and what JLCPCB answered), `jlc-rotations.csv` and `jlc_final.py` (the rotation fixes applied to the CPL) |
| `release/revA/review/` | the review prints: 1:1 sheets, assembly drawings, copper layers, schematics, renders at A4 |
| `images/` | downscaled top renders for the README |

## State of the MESHSAT-830 generation (7 September 2026)

The device set was ruled on 6 September 2026 (appendix 32.49 and 32.50), the fabric on 7 September (32.52: three slots, USB devices, k3s), and the five boards were generated from their generators the same day: A22 (the 14.4 V node, the charger, the rails, the outlet, eleven blind-mate sites, the D8 mezzanine site), B16 (three slots with their switches, hubs and drives, the Ethernet and HDMI switches, the radios), C7 (the backer ring with the RP2040 panel controller and the Pervasive Displays e-paper driver), D8 (the SA868 exciter, the amplifier leads, the USB audio path), E6 (the front end, the tracker, the pack entry, the sensor controller; the sensor board of the plan folded into it). Every board routes on a rented build host under `ecad/tools/routeflow.py`; a board is released when it is clean (0 unrouted, 0 hard DRC violations, the numeric gate passing) and its deliverable folder lands in `release/revA/boards/`. `ecad/tools/check_contracts.py` passes across the set (the 2x13 ribbons, the mezzanine harness, the EMCON chain, the four 5 V rails, the dock contacts).

The JLCPCB cart of 3 September holds the previous generation and is not paid; its lines are rebuilt from the new deliverables when the owner declares the set final. Parts fitted at the bench rather than by the assembler are listed per board in `ORDER-NOTES.txt` and in `docs/ASSEMBLY.md` section 9.

## Regenerating a board

The boards are generated by scripts, not drawn by hand. The pipeline runs headless on a rented build host (KiCad 9.0.9 with its Python bindings, Freerouting 1.9.0 built with a per-pass session, Java, Xvfb) driven by `ecad/tools/routeflow.py` with **one profile per board letter** in `ecad/tools/routeflow/<letter>.json`; everything that differs between boards is declared in `ecad/tools/boards/<letter>.json` (the phase, the pair classes and layers, the fanout nets, the finish stages) and the sequence lives once in `full.sh` and `finish.sh` (since 15 September 2026; before that there were 21 chain clones, 15 finish clones and 34 per-phase profiles).

1. `ecad/tools/full.sh <project dir> <letter>` writes the schematic (`gen_sch_<x>.py`, which also emits the netlist and the design-intent file), runs ERC, writes the outline and keep-outs (`gen_pcb_<x>.py`) and the placement, planes and locked rail copper (`gen_pcb_<x>3.py`), then the escapes of the fine-pitch parts, the pair pre-router (`pair_preroute.py`, every differential pair laid coupled before the router runs), the plane fanout, the same-net pin joins, the region-fit and placed-board DRC gates, and the placement predictor (`place_audit.py`); it stops with `PREROUTE-DONE OK` or `BLOCK`.
2. `python3 ecad/tools/routeflow.py run ecad/tools/routeflow/<letter>.json --phase <PHASE>` runs step 1, then Freerouting (single thread, the ground planes as power layers, a session written after every pass so a cut run keeps its best pass), judges the routed board and applies a bounded remedy per round; a run writes its provenance, its resolved configuration and a chained journal under `out/routeflow/<run>/`.
3. `ecad/tools/finish.sh` runs once per board: the knot repair, the dangling clean-up, the plane-pad vias, the pour stitching, the stub router for the last opens, the stitch and rail pruners, the return-current vias (a ground via beside every signal via), the quality pass, the pair length gate, the legend pass; every copper-editing pass runs under one guard (`guarded.sh`: snapshot, run, DRC, hard and unrouted against the board handed in, keep or restore). Then the routed-board gates: the fifteen-type hard DRC set, `check_pcb_<x>.py` with the return-path, decoupling and rail checks, `dc_drop.py`, `impedance_check.py`, `netlist_board.py`, `check_contracts.py`; then `finish_board.sh` cuts the deliverable folder and `verify_deliverable.py` reads it back.
4. `make_handoff.py` rebuilds `release/<rev>/order/` and `release/<rev>/review/` from the deliverable folders; `final_gate.py` re-reads every folder of the seven-board manifest with the contracts and the parts certification and fails closed on any of them.

The rules the tools hold are in `ecad/tools/tests/` (`python3 tools/tests/run.py` from `ecad/`; `tools/tests/run_code_only.sh` runs the same suite on a code-only archive). Prerequisites on the build host: KiCad 9.0.9 with `kicad-packages3d` (`kicad-cli` and `pcbnew` importable from `python3`), Java, the Freerouting 1.9.0 per-pass build (`tools/routeflow/cloud/onstart.sh` builds it from the v1.9.0 source; the stock jar is refused), Xvfb, `python3-numpy`, `python3-scipy`, and a venv with `build123d`, `ezdxf` and `matplotlib` for the CAD generators.

## Case

Peli 1450 without foam plus the 1450PF special application panel frame (CAD in `vendor/peli/1450/`). The frame window is 349.65 x 233.83 mm; the face plate (365.5 x 249.5 x 3, ten M3 at the frame's inserts) sits with its top 101.4 mm above the cavity floor, the backer ring 10 mm under it, and the stack tops out at 49.5 mm at B16's top copper with the three coolers above it. The Xenarc monitor sits IN the plate with its glass level with the aluminium face, its body hanging into the void below (owner ruling 9 September 2026, appendix 32.85), the QMX HF unit rides in a printed tray on the lid's inner face (`release/revA/case/lid-bracket-qmx/`), the pack stands at the west wall, the eleven couplers sit in the end walls at 88 mm (`ecad/tools/panel1450.py` is the single source of every face and wall position), and the connector plate stands upright between the back-wall ribs. The templates are in `release/revA/case/`; the interior numbers in design record 32.56 and 32.60.
