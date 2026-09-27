# Diagrams of the V2 field kit (handover layer 4)

MESHSAT-1357, 27 September 2026. **Every diagram here is a design diagram of an unbuilt prototype.** No V2 board has
been fabricated, ordered or powered, no kit has been built, fitted to a case or field deployed, and nothing drawn here
has been measured. Each rendered file says so in its own title or footer.

**Status at handover H1: drawn at `e3aedb25`, before round 8, and not rebuilt since.** Round 8 regenerated the
schematics of boards A, C, D, E and P and changed `pcb_interfaces.yaml`, `ARCHITECTURE.md`, the battery packet and
`gen_pcb_e.py`, so `python3 v2/docs/diagrams/tools/build.py --check` reads 0 of 11 diagrams current at the handover
commit. Every diagram shows the design as it stood at `e3aedb25`, with the netlist sha256/16 it was drawn from in its
own box; where round 8 changed a circuit, the committed netlist and `ARCHITECTURE.md` are the authority, not the
drawing. A rebuild needs `power_tree.py`'s `TREE` updated first: at the round 8 netlists it refuses two board D stages
(`+5V_D8` to `+5V_SA` through FB1, and `+5V_D8` to `VGG_SW` through U15), because round 8 put board D's transmit
supply behind EMCON. The rebuild itself needs Node with `@mermaid-js/mermaid-cli` and a Chromium (`tools/render.sh`).

The editable originals stay where they are: the Mermaid blocks in `v2/docs/ARCHITECTURE.md` and in the battery review
packet, the netlists under `v2/ecad/pcb-*/out/`, and the geometry sources named below. This folder holds readable
renderings of them, the tools that make them, and `MANIFEST.json`, which ties every rendered file to the sha256/16 of
each input it was made from.

## What is here

| Diagram | Shows | Drawn from | Does not show |
|---|---|---|---|
| `svg/arch-2-context.svg` | the kit in its context: operator, local networks, bearers, power inputs | `ARCHITECTURE.md` section 2 (its Mermaid block, unchanged) | anything the page's own block does not |
| `svg/arch-3-2-board-interconnect.svg` | the seven boards and the contracts between them | `ARCHITECTURE.md` section 3.2 | pin maps (they are in `pcb_interfaces.yaml`) |
| `svg/arch-4-1-power-tree.svg` | the power tree as the page summarises it | `ARCHITECTURE.md` section 4.1 | the netlist check of each stage (see `power-tree` below) |
| `svg/arch-4-3-power-up.svg` | power-up states S0 to S5 | `ARCHITECTURE.md` section 4.3 | timing; the SLOT_EN hold, which is in no generator |
| `svg/arch-5-5-lanes-and-fabric.svg` | PCIe, USB banks, Ethernet and display per slot | `ARCHITECTURE.md` section 5.5 | the supervisors and their CAN fabrics; channel budgets (FB-FAB-7) |
| `svg/battery-protection-states.svg` | the pack's protection states | `review-packets/battery/PROTECTION-ARCHITECTURE.md` section 4 | thresholds (in `PRIMARY-CONFIGURATION.md`) |
| `svg/battery-charger-states.svg` | the charger's state sequence with its host present or silent | `review-packets/battery/CHARGER-STATE-SEQUENCE.md` section 7 | bench results (FW-A15 is open) |
| `svg/control-lines.svg` | TX_INHIBIT_n, EMCON_HW, EMCON_ON, ZEROIZE_SW, ZEROIZE_HW, SLOT_EN1..3, PI_KILL and SHORE_INHIBIT across boards C, B, A, D and E: the part driving each line, every part it reaches (followed through logic gates and FETs), the pulls, the connector pins | the committed netlists, read by `tools/control_lines.py`; pins checked at both ends and against `v2/ecad/tools/pcb_interfaces.yaml` | direction as firmware sets it, timing, test points (listed in `control-lines.md`), PI_SHDN_REQ, HDMI selects, heartbeats, the kit I2C bus, the SLOT_EN hold and the EMCON remedies L1 to L4 and L7 (in no generator) |
| `svg/power-tree.svg` | board P's cells to every rail on boards E, A, B, C and D, the three inputs, the leads between boards, the loads that leave the boards; the stages of `pcb_energy_chain.yaml` in red with their declared currents | the committed netlists and `v2/ecad/tools/pcb_energy_chain.yaml`, read by `tools/power_tree.py`; which parts make each stage is typed in the tool and checked against the netlist on every build (method and limits in `power-tree.md`) | currents drawn, losses, heat, which rail is on in which power state, grounds and returns, clamps, the CM5 modules' own rails |
| `svg/case-plan.svg` | the Peli 1450 cavity, the 1450PF window, face plate C1, the setting legs C6, boards A, B, C (backer strips), D, E, E5, the 4S3P block and board P, the rods, the blind-mate row, the arrestors of C2 and the connector plate of C3; the superseded as-coded plate and wall jacks in grey | `v2/vendor/peli/frame_seat.py` and its output, `v2/vendor/peli/case_margins.py`, `v2/ecad/tools/panel1450.py`, the board generators' constants, `pcb_board_facts.yaml` (checked) | parts on the boards, cables, the pack's hold-down (not designed, S-27), the lid, tolerance bands; board P's position is INFERRED |
| `svg/case-zstack.svg` | the same arrangement in Z along X: floor, walls, rim, shoulder, rib tops, every board, the CM5 heatsinks, the pack block, the legs, the 1450PF frame in section (ring on the leg pads, skirt down to its bottom 86.00, outer face, gasket step and flange), the face plate with its range, the Xenarc body and margin M1, the arrestor axis; the as-coded face top and jacks in grey; detail A enlarges the frame at the end wall with M20 and M21d | as above, plus `v2/cad/render/scene.py` for the heights of E5, A and D | the backer ring, the e-paper, the PA under the plate, cables, the lid tray, tolerance stacks, the frame's corner arcs, insert bores and gasket |

Each diagram has a PDF copy in `pdf/`. The Mermaid sources the SVGs were rendered from are in `src/`: the seven copied
out of the documents carry only an added title (document, section, line range, the document's sha256/16 and the tree
revision); `control-lines.mmd` and `power-tree.mmd` are generated. The netlist readings behind the generated diagrams are
in `control-lines.md` and `power-tree.md`, and every number of the case drawings with its source is in
`case-drawings.md`.

Revisions: everything here was drawn from the tree at `e3aedb25` (netlists A `7b08510106687b3d`, B `669d02d07aeaae4b`,
C `2834f0d8c4071d56`, D `f13d8b70099ab03e`, E `d910e49c5f5f50b2`, P `4342c4cbe1b43dc4`), with `ARCHITECTURE.md` carrying
the diagram references added with this folder. `MANIFEST.json` records the exact input and output identities.

## Findings the drawings surfaced

Reading the netlists against the declared energy chain (`power-tree.md`, first section) found five disagreements, all
in `v2/ecad/tools/pcb_energy_chain.yaml` or in naming, none in a circuit:

1. Board P's chemical fuse F2 (Eaton SCF9550-30-05) is in series between FUSED and SCP_OUT; the chain has no F2 stage
   and runs its PACK_FETS stage from FUSED (PWR-F12; the re-declaration exists as a draft,
   `v2/docs/records/rv-pwr/pwr-chain-redeclaration.yaml`).
2. The chain's PACK_CELLS stage still reads "4S3P or 4S4P, about 200 Wh"; owner ruling D-06 made the pack one 4S3P block
   of Samsung 35E (about 145 Wh).
3. Stages B_PANEL_5V, B_HDMI_5V and B_QMX_5V take their prospective fault current from "board A's AP64500 buck U7"; board
   A's U7 is an LM5176PWPR making +5V_DEV, limited by its own current loop (ARCHITECTURE.md 4.1).
4. SHORE_INPUT's note names an SMCJ33A clamp; board E carries SMCJ40A and SMCJ40CA clamps since `faf8c981`.
5. Board B's net `VBAT` is its CR2032 backup, not board A's VBAT: one name on two boards, never joined.

They are handed to the owner of the energy chain as `v2/docs/records/hc4/energy-chain-disagreements.md` (filed with
this folder on 27 September 2026); nothing in the chain file was changed here.

## How they are made

Toolchain used for the committed files (runner nllei01claude01, 27 September 2026): Python 3.11.2 with matplotlib
3.10.9 and PyYAML 6.0.3; Node 20.20.2 with `@mermaid-js/mermaid-cli@11.12.0` through npx (it bundles Mermaid and the
ELK layout engine, used for every Mermaid diagram through `tools/mermaid.json`); Chrome for Testing 151.0.7922.34
(Playwright's `chrome-headless-shell`) as the browser mermaid-cli drives; Playwright 1.58.0 and poppler's `pdftoppm`
22.12.0 for the readback. No KiCad and no CAD kernel is needed: the netlists are read as text, the geometry sources are
plain Python.

```
export CHROME_BIN=/path/to/chrome-headless-shell   # or leave unset: Puppeteer then downloads its own Chromium
python3 v2/docs/diagrams/tools/build.py            # extract, generate, render, write MANIFEST.json (about a minute)
python3 v2/docs/diagrams/tools/build.py --check    # names every diagram whose inputs changed since MANIFEST.json
python3 v2/docs/diagrams/tools/readback.py /tmp/rb  # checks each SVG and rasterises it for a person or agent to look at
```

`build.py --check` exits 1 when an input has moved: after any change to a netlist, to `pcb_energy_chain.yaml`, to
`pcb_interfaces.yaml`, to `ARCHITECTURE.md` or the battery packet, or to a geometry source, rebuild before the diagrams
go into a handover snapshot. `control_lines.py` refuses to be quiet about a connector pin that differs between a
cable's two ends or from `pcb_interfaces.yaml`. `power_tree.py` does not find a stage's parts: they are typed in its
`TREE`, and every build checks that typing against the netlist and writes nothing when a check fails. The path from
the stage's first net to its second must run only through the named parts, the FETs a named controller drives (by
their gates, directly or through one series resistor) and the inductors on their switching nodes; every named part
must be needed for the path; a part whose value text names a rail must name the stage's end; and every negative control
must be refused (2697 at `e3aedb25`, among them the five wrong controller entries the review of 27 September 2026 found
the first walk accepted, and 168 entries where the path still exists and only the controller is wrong). It checks the
drawn stages' connectivity and labels, not that a stage works, and a named IC is crossed between any of its pins. Its
attribution check is not complete: the second review of 27 September 2026 (an AI review) tried 3822 single-part
substitutions and cut-downs at `e3aedb25` and `power_tree.py` accepted 27 of them, 18 distinct wrong attributions. A
part that bridges the stage's two nets (an INA226 monitor, a feedback resistor, a load's supply pins, such as board B's
KSZ9897 in place of LDO U27) is accepted, and so is a passive on a FET gate named as the controller (board E's R1 in
place of U3, board P's R16 in place of U1); two-pin references starting with L are taken as inductors, LEDs included.
The attributions drawn at `e3aedb25` were therefore also checked by hand. `power-tree.md` states the method and its
limits. `case_drawings.py` stops when a generator's outline disagrees with
`pcb_board_facts.yaml` or when `frame_seat.py`'s frame bottom disagrees with its committed output.

## How they were checked

Each rendered SVG was read back as an image (`tools/readback.py`: parsed as XML, no HTML labels, the "unbuilt
prototype" statement present in its text, rasterised in headless Chromium) and looked at by the session on 27 September
2026, at full size and in crops for the wide ones. That is an AI check of legibility and of agreement with the sources,
not a qualified engineering review, and it does not make any drawn design correct. Three rendering choices came out
of it: labels are SVG text, not HTML (`htmlLabels: false`), so any SVG viewer shows them; the ELK layout replaced
Mermaid's default because the default overlapped edge labels in the protection-state and lanes diagrams; and, in the
second pass, edge labels sit on opaque white boxes (`themeCSS` in `tools/mermaid.json`), because Mermaid draws their
background at half opacity and every edge line ran through its own label's text. A white text halo was tried first
and dropped: at 4 px it left the line showing in the word gaps (`EMCON_ON` read as `EMCON-ON`), and at 10 px it
painted over the row above (the Q of `CSD19532Q5B` read as an O).

A review of this folder on 27 September 2026 (an AI review, run against `e3aedb25`) found two faults, both fixed here:

1. The first power-tree walk flooded from the source net through every inductor and power FET on the board and accepted
   a stage once its end was reached and each named part had been touched, so it accepted a wrong controller: all five
   of the reviewer's wrong entries (for example board A's U4 with R43 for +5V_DEV). The claim on the page, in the SVG's
   legend and in `ARCHITECTURE.md` 4.1 said every stage was proved. The walk now crosses only the named parts, the FETs
   a named controller drives and the inductors on their switching nodes, requires every named part, and refuses the
   five entries and the other negative-control classes on every build; the wording in all four places now says the
   stage's parts are typed and checked. The attributions drawn at `e3aedb25` did not change: the reviewer had checked
   them by hand and this check agrees. The second review found the attribution check still incomplete (the paragraph
   above); the wording here and in `ARCHITECTURE.md` 4.1 was corrected at integration to say so.
2. The Z stack labelled the frame's ring with the skirt's bottom (86.00) and did not draw the skirt, so face plate C1
   seemed to overhang empty space at the end walls. The frame is now drawn in section from `frame_seat.py`'s constants
   and its own outer-face profile: ring from the C6 pad tops (94.13) to 103.52, skirt from its inner face (X 183.34)
   to the outer face (X 189.18 at the bottom, 189.48 at its widest) down to 86.00 (84.38 to 87.62 on the legs),
   gasket step and flange; detail A enlarges it at the end wall with M20 and M21d, and `case_drawings.py` stops if
   `frame_seat.py` and its committed output disagree on the frame bottom.
