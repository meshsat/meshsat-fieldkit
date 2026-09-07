# V2: the Peli 1450 carrier set (MESHSAT-830 generation)

Seven KiCad 9 boards for the kit V2 go-box: a Peli 1450 case with the 1450PF panel frame. The power and compute boards stack on four M3 rods and lift out of the case in one piece; a dock strip on the case floor carries the 9 to 36 V front end, the solar tracker, the sensor controller and the raised contact block that the stack blind-mates onto, with eleven antenna paths mating at the same time. The control face is a 3 mm aluminium plate in the frame (`cad/face_plate.py`, `release/revA/case/face-plate/`) with a Xenarc 709GNK monitor lying on it, the backer board C7 hanging under it and the 30 W VHF module bolted to its underside; the built 4S smart pack lies in the pocket at the east end wall (appendix 32.62) and the eleven antenna couplers sit in the end walls at 88 mm. Nothing here has been built: the boards are designed, generated and checked, and no set has been ordered.

The rulings that bind the design (details in `docs/MESHSAT-709-geometry-appendix.md`, sections 32.49 to 32.61, and the specification `docs/V2-SPEC.md`): three identical Compute Module 5 slots with every radio and sensor a USB device shared by the HAL, k3s across the modules; the pack, the charger and the power control on PCB-A; no vent opening anywhere in the case; EMCON a hardware line from the panel toggle to every transmitter rail gate and to the amplifier keying, plus a software hold; the panel a USB device driven per `docs/PANEL.md`.

| Board | Rev | Size (mm) | Layers | Project | Deliverable folder |
|---|---|---|---|---|---|
| PCB-A POWER + I/O | A22 | 240 x 160 | 6 | `ecad/pcb-a-power/` | `release/revA/boards/meshsat-pcb-a-revA-A22/` |
| PCB-B COMPUTE | B16 | 330 x 200 | 6 | `ecad/pcb-b-compute/` | `release/revA/boards/meshsat-pcb-b-revA-B16/` |
| PCB-C PANEL BACKER | C7 | 344 x 228 ring | 4 | `ecad/pcb-c-display/` | `release/revA/boards/meshsat-pcb-c-revA-C7/` |
| PCB-D VHF APRS | D8 | 100 x 80 | 4 | `ecad/pcb-d-aprs/` | `release/revA/boards/meshsat-pcb-d-revA-D8/` |
| PCB-E1 DOCK STRIP | E6 | 267 x 68 | 4 | `ecad/pcb-e1-dock/` | `release/revA/boards/meshsat-pcb-e-revA-E6/` |
| PCB-E5 DOCK BLOCK | E5 | 43 x 26 | 2 | `ecad/pcb-e5-block/` | `release/revA/boards/meshsat-pcb-e5-revA-E5/` |
| PCB-P PACK BMS | P1 | 70 x 44 | 2 (2 oz) | `ecad/pcb-p-pack/` | `release/revA/boards/meshsat-pcb-p-revA-P1/` |

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

The boards are generated by scripts, not drawn by hand. The pipeline runs headless on a rented build host (KiCad 9.0.9 with its Python bindings, Freerouting 1.9.0, Java, Xvfb) driven by `ecad/tools/routeflow.py` with one profile per board in `ecad/tools/routeflow/`; the steps a profile runs:

1. `ecad/tools/full_<board>.sh` writes the schematic and the placed board from `gen_sch_<x>.py`, `gen_pcb_<x>.py` and `gen_pcb_<x>3.py` (placement, planes, keep-outs), then runs the numeric gate `check_pcb_<x>.py` against the appendix numbers.
2. `ecad/tools/route_parallel.sh <projectdir> <name> '<attempt list>'` runs Freerouting (one attempt, single thread, the ground planes handed to the router as power layers); the escapes of the fine-pitch parts, the same-net pin joins and the plane fanout vias are placed and locked before the route.
3. `finish_<board>.sh`: the knot repair (`unknot.py`), the stub router for the last opens, the dangling clean-up, the quality pass, the pair gate, the legend pass, the routed-board gate; then `finish_board.sh <projectdir> <name> <postfix or -> <deliverable dirname>` runs the DRC, exports the fabrication files and writes the deliverable folder into `release/<rev>/boards/` (`MESHSAT_FK_REV`, default `revA`).
4. `make_handoff.py` rebuilds `release/<rev>/order/` and `release/<rev>/review/` from the deliverable folders, applying the JLCPCB rotation offsets and removing bench-fitted parts from the JLC BOM and CPL.
5. `check_contracts.py` reads every board's netlist and checks what no single board can see: the panel ribbon and the A to B ribbon maps, the mezzanine harness, the transmit inhibit chain, the three rails, the dock contacts, the I2S and wall-port pairs. Read the head of a chain log, not only its tail: a generator that stops leaves the previous schematic in place and the rest of the chain rebuilds from it.

Prerequisites on the build host: KiCad 9.0.9 with `kicad-packages3d` (`kicad-cli` and `pcbnew` importable from `python3`), Java with `~/bin/freerouting-1.9.0.jar`, Xvfb for the headless router, `python3-numpy`, and a venv with `build123d`, `ezdxf` and `matplotlib` for the case parts in `cad/` and the STEP probes in `vendor/probes/`. The renders (`cad/render/scene.py`, Blender 4.2 with CUDA) run on a rented GPU host. Route sessions, logs and per-user KiCad state are ignored by git (`out/`, `logs/`, `*.kicad_prl`).

## Case

Peli 1450 without foam plus the 1450PF special application panel frame (CAD in `vendor/peli/1450/`). The frame window is 349.65 x 233.83 mm; the face plate (365.5 x 249.5 x 3, ten M3 at the frame's inserts) sits with its top 101.4 mm above the cavity floor, the backer ring 10 mm under it, and the stack tops out at 56 mm at B16's top copper with the three coolers above it. The Xenarc monitor lies on the plate over a cutout for its connector block, the QMX HF unit rides in a printed tray on the lid's inner face (`release/revA/case/lid-bracket-qmx/`), the pack stands at the west wall, the eleven couplers sit in the end walls at 88 mm (`ecad/tools/panel1450.py` is the single source of every face and wall position), and the connector plate stands upright between the back-wall ribs. The templates are in `release/revA/case/`; the interior numbers in design record 32.56 and 32.60.
