# Diagrams of the V2 field kit (handover layer 4)

MESHSAT-1357, 27 September 2026. **Every diagram here is a design diagram of an unbuilt prototype.** No V2 board has
been fabricated, ordered or powered, no kit has been built, fitted to a case or field deployed, and nothing drawn here
has been measured. Each rendered file says so in its own title or footer.

**Status: drawn at `b7f96784`, with round 8 on all six boards and set 5 on boards A, B, D and E.** The r8int5 integration
(27 September 2026, branch `fnd/r8int5`) rebuilt every diagram again from the tree at `b7f96784` (netlists A `da05dc02bc1e612f`, B
`8b78c59754a6a0c7`, C `11eabc2dddca5161`, D `76700a687eb6187f`, E `d6137f50059e5cbc`, P `085f833362fbbda8`; `pcb_energy_chain.yaml` `a09ca0293afd1f7c`), after set 5 changed
the netlists of A, B, D and E. `power_tree.py` refused them as stream w3g left it, and follows them now: board E's
tracker stage names Q3, U5 and Q6 (R5 senses in the bottom switches' leg since S-47, off the PV_P to TRK_OUT path),
the VIN_RAW lead runs from board E's P_VR to board A's J_VR1 to J_VR4 (EQ-16), and the legend calls board B's
coin-cell net VBAT_RTC (W3B-R1). The case drawings now read r8int4's case release (`c351115d`). The rest of this page
is stream w3g's record of its rebuild at `38dcd764`, with the counts and findings of `b7f96784` given where they differ.
`build.py --check` reads 11 of 11 current against `MANIFEST.json`, whose `tree` is `b7f96784`.

Stream w3g's rebuild: every diagram was rebuilt on 27 September 2026 from
the tree at `38dcd764` (netlists A `3a786cf31614fe63`, B `adcc3c6736c90e9f`, C `11eabc2dddca5161`, D
`0dad82b4b6a79290`, E `f3c1ad6153002976`, P `085f833362fbbda8`; `pcb_energy_chain.yaml` `97c6afce242a590b`), each
netlist's sha256/16 in its own board box, with this folder's tools and the `ARCHITECTURE.md` reference lines of the
same rebuild. `python3 v2/docs/diagrams/tools/build.py --check` reads 11 of 11 current against `MANIFEST.json`, whose
`tree` is `38dcd764` and whose `inputs_differing_from_the_tree` names exactly the files this rebuild changed
(`ARCHITECTURE.md` and the tools); once they are committed as they stand, the check stays at 11 of 11 until an input
moves. The drawings made at `e3aedb25`, before round 8, are replaced: round 8 put board D's transmit chain behind a
load switch (`+5V_TX`, U21), split board B's EMCON line per slot (`EMCON_ON1..3`) and replaced the gates on the EMCON
lines of boards A, B and C, and the power tree and the control lines now show that.

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
| `svg/battery-charger-states.svg` | the charger's state sequence with its host present or silent | `review-packets/battery/CHARGER-STATE-SEQUENCE.md` (the block sits under its section 7 heading, which the title quotes) | bench results (FW-A15 is open) |
| `svg/control-lines.svg` | TX_INHIBIT_n, EMCON_HW, board B's per-slot EMCON_ON1..3, ZEROIZE_SW, ZEROIZE_HW, SLOT_EN1..3, PI_KILL and SHORE_INHIBIT across boards C, B, A, D and E: the part driving each line and every part it reaches, followed through logic gates (pin maps from the makers' sheets, `netlist.py`), FET gates and series resistors, with the pulls, filters and connector pins | the committed netlists, read by `tools/control_lines.py`; pins checked at both ends and against `v2/ecad/tools/pcb_interfaces.yaml` | direction as firmware sets it, timing, test points (listed in `control-lines.md`), PI_SHDN_REQ, HDMI selects, heartbeats, the kit I2C bus, the SLOT_EN hold (in no generator); whether a line's state is proved (`feasibility/EMCON.md`) |
| `svg/power-tree.svg` | board P's cells to every rail on boards E, A, B, C and D, the three inputs, the leads between boards, the loads that leave the boards; board D's `+5V_TX` behind U21; the stages of `pcb_energy_chain.yaml` in red with their declared currents | the committed netlists and `v2/ecad/tools/pcb_energy_chain.yaml`, read by `tools/power_tree.py`; which parts make each stage is typed in the tool and checked against the netlist on every build (method and limits in `power-tree.md`) | currents drawn, losses, heat, which rail is on in which power state, grounds and returns, clamps, the CM5 modules' own rails |
| `svg/case-plan.svg` | the Peli 1450 cavity, the 1450PF window, face plate C1, the setting legs C6, boards A, B, C (backer strips), D, E, E5, the 4S3P block and board P, the rods, the blind-mate row, the arrestors of C2 and the connector plate of C3; the superseded as-coded plate and wall jacks in grey | `v2/vendor/peli/frame_seat.py` and its output, `v2/vendor/peli/case_margins.py`, `v2/ecad/tools/panel1450.py`, the board generators' constants, `pcb_board_facts.yaml` (checked) | parts on the boards, cables, the pack's hold-down (not designed, S-27), the lid, tolerance bands; board P's position is INFERRED |
| `svg/case-zstack.svg` | the same arrangement in Z along X: floor, walls, rim, shoulder, rib tops, every board, the CM5 heatsinks, the pack block, the legs, the 1450PF frame in section (ring on the leg pads, skirt down to its bottom 86.00, outer face, gasket step and flange), the face plate with its range, the Xenarc body and margin M1, the arrestor axis; the as-coded face top and jacks in grey; detail A enlarges the frame at the end wall with M20 and M21d | as above, plus `v2/cad/render/scene.py` for the heights of E5, A and D | the backer ring, the e-paper, the PA under the plate, cables, the lid tray, tolerance stacks, the frame's corner arcs, insert bores and gasket, what the pack block stands on (S-27) |

Each diagram has a PDF copy in `pdf/`, printed at the drawing's natural size (the wide ones are large-format pages:
the power tree 6360 x 1476 pt, the control lines 4940 x 1202 pt; zoom to fit or print in tiles). The Mermaid sources
the SVGs were rendered from are in `src/`: the seven copied out of the documents carry only an added title (document,
section, line range and the document's sha256/16; the tree revision is in `MANIFEST.json`, since a file cannot name
the commit that contains it); `control-lines.mmd` and `power-tree.mmd` are generated. The netlist readings behind the
generated diagrams are in `control-lines.md` and `power-tree.md`, and every number of the case drawings with its
source is in `case-drawings.md`.

Round 8 changed none of the seven Mermaid blocks (`extract_mermaid.py --check` read them identical to the sources of
`e3aedb25`) and none of the figures the case drawings read, so those nine differ from the drawings of `e3aedb25` only
in their titles' document identities, the PDFs' page size and, on the case plan, a footer that now wraps inside the
page and one label set on white. At `b7f96784` two Mermaid blocks differ from w3g's sources, the board interconnect's and the
power tree's dock edges (VIN_RAW on four 9 A pins at 14.10 A, EQ-16), and the case drawings read `c351115d`'s case
release (the plate's VHB lift 0.0, the as-coded plate and jacks moved; `case-drawings.md` names each input's commit).

## Findings the drawings surfaced

**At `b7f96784`** the build prints three disagreements (items 1, 3 and 4 below) and no netlist finding: item 2 is gone
because r8int4 re-declared the chain's pack for D-06, item 5 because W3B-R1 renamed board B's coin-cell net VBAT_RTC,
and item 6 because set 5 (board A stream w3a) made R74 and R133 the top legs of U16's and U19's enable dividers
(POE_UVLO, PD_UVLO), as the stage table's Enable column shows. Item 4 still prints because the SHORE_INPUT note names
the SMCJ33A as the clamp corrected away at `faf8c981` (stream w3de's rewording), which the check reads as a claim.

At `38dcd764`, reading the netlists against the declared energy chain (`power-tree.md`, first sections) finds the
same four disagreements with `v2/ecad/tools/pcb_energy_chain.yaml` as at `e3aedb25`, all in the chain file, none in a
circuit, plus one naming note:

1. Board P's chemical fuse F2 (Eaton SCF9550-30-05) is in series between FUSED and SCP_OUT; the chain has no F2 stage
   and runs its PACK_FETS stage from FUSED (PWR-F12; the re-declaration exists as a draft,
   `v2/docs/records/rv-pwr/pwr-chain-redeclaration.yaml`).
2. The chain's PACK_CELLS stage still reads "4S3P or 4S4P, about 200 Wh"; owner ruling D-06 made the pack one 4S3P block
   of Samsung 35E (about 145 Wh).
3. Stages B_PANEL_5V, B_HDMI_5V and B_QMX_5V take their prospective fault current from "board A's AP64500 buck U7"; board
   A's U7 is an LM5176PWPR making +5V_DEV, limited by its own current loop (ARCHITECTURE.md 4.1).
4. SHORE_INPUT's note names an SMCJ33A clamp; board E carries SMCJ40A and SMCJ40CA clamps since `faf8c981`.
5. Not a chain item: board B's net `VBAT` is its CR2032 backup, not board A's VBAT: one name on two boards, never joined.

They were handed to the owner of the energy chain as `v2/docs/records/hc4/energy-chain-disagreements.md`; nothing in the
chain file is changed here. The rebuild adds one netlist finding, printed by `power_tree.py` on every build:

6. **Board A's R74 (on POE_EN) and R133 (on PD_EN) each have both pins on one net.** They are the half of R4T-F3
   (`v2/docs/records/r4t/r4-decisions.md`) that round 8 did not close. Round 8 closed the other half on the PA and HF
   converters: R58 and R124 (10k 1%) now run from PA_EN and HF_EN to PA_UVLO and HF_UVLO over R59 and R125 (15k 1%)
   to GND, so U13 and U15 take 0.6 of their enable line. R74 and R133 do nothing, so the PoE and USB-C PD converters
   U16 and U19 sit on POE_EN and PD_EN directly, with R75 and R134 (10k 1%) as pull-downs: the way U5 (SLOT_EN2, R34
   100k to GND) and U7 (DEV_EN, R42 100k up to +3V3, S-08) are driven by design (`en_div=False` in `gen_sch_a.py`).
   U2 takes 0.68 of FE_RUN through its own supervisor network (R199 47k, R206 100k, C213 2.2n). `power-tree.md`
   prints how each LM5176's EN/UVLO pin is driven, read from the netlist on every build. For the board A author; no
   generator is changed here.

## How they are made

Toolchain used for the committed files (the runner, 27 September 2026; `MANIFEST.json` records the same): Python
3.11.2 with matplotlib 3.10.9 and PyYAML 6.0.3; Node 20.20.2 with `@mermaid-js/mermaid-cli@11.12.0` through npx, whose
bundle carries the ELK layout (used for every Mermaid diagram through `tools/mermaid.json`) and which loads Mermaid from
its own `node_modules`: npx resolved **Mermaid 11.17.2** and Puppeteer 23.11.1 for it (mermaid-cli asks only for
Mermaid ^11, so a fresh npx cache may resolve a later 11.x; `build.py` records what it found); Chrome for Testing
151.0.7922.34 (Playwright's `chrome-headless-shell`) as the browser mermaid-cli drives; Playwright 1.58.0 and poppler's
`pdftoppm` and `pdfinfo` 22.12.0 for the readback. No KiCad and no CAD kernel is needed: the netlists are read as
text, the geometry sources are plain Python.

```
export CHROME_BIN=/path/to/chrome-headless-shell   # or leave unset: Puppeteer then downloads its own Chromium
python3 v2/docs/diagrams/tools/build.py            # extract, generate, render, write MANIFEST.json (about a minute)
python3 v2/docs/diagrams/tools/build.py --check    # names every diagram whose inputs changed since MANIFEST.json
python3 v2/docs/diagrams/tools/readback.py /tmp/rb  # checks each SVG and PDF and rasterises both for a person or agent to look at
```

`build.py --check` exits 1 when an input has moved: after any change to a netlist, to `pcb_energy_chain.yaml`, to
`pcb_interfaces.yaml`, to `ARCHITECTURE.md` or the battery packet, or to a geometry source, rebuild before the diagrams
go into a handover snapshot. The SVG pass keeps Mermaid's `useMaxWidth`, so a browser scales a diagram to its window;
the PDF pass turns it off (`render.sh`), so each PDF page carries the drawing at its natural size.

**`control_lines.py`** refuses (exit 1, the problems on its page) a connector pin that differs between a cable's two
ends or from `pcb_interfaces.yaml`; a logic part on a line (value text starting SN74, 74LVC, 74AUP, 74AHC or 74HC) with
no pin map in `netlist.GATES`, which would otherwise be drawn as a plain IC with the line stopping there unnoticed; and
a FET on a line whose symbol does not name exactly one G, S and D pin or that is not N-channel by its library symbol
and value text (the drawing's "high pulls low" and "level stage" hold for an N-channel FET only; the FET pins are read
by their names, no longer assumed to be SOT-23's 1 G, 2 S, 3 D). Five pin maps were added for round 8's single gates,
each from the TI sheet held in `v2/vendor/ti/`: SN74LVC1G04 (SCES214AF), SN74LVC1G08 (SCES217AA), SN74AUP1G08
(SCES502Q), SN74LVC2G06 (SCES307J) and SN74LVC1G57 (SCES414P); `control-lines.md` lists every map with its source. A
line is followed through a series resistor (an enable divider's top leg, such as board A's R58 to U13's EN/UVLO), never
through a resistor to a rail, a ground, another drawn line, a power conductor (a net of more than eight nodes or one
carrying a power FET) or an indicator LED.

**`power_tree.py`** does not find a stage's parts: they are typed in its `TREE`, and every build checks that typing
against the netlist and writes nothing when a check fails. The path from the stage's first net to its second must run
only through the named parts, the FETs a named controller drives (by their gates, directly or through one series
resistor) and the inductors on their switching nodes; a controller must be an IC (a U reference), so a resistor on a
FET's gate is never one, and a two-pin LED reference is never taken as an inductor (both rules added at this rebuild);
every named part must be needed for the path; a part whose value text names a rail must name the stage's end; an
enable net named in a stage's label must be met by a named IC, directly or through one series resistor (added at this
rebuild); and every negative control must be refused (2823 at `b7f96784`, 2841 at `38dcd764`, among them the five wrong controller entries
of the first review of 27 September 2026, 168 entries where the path still exists and only the controller is wrong,
and 130 with another stage's enable in the label). It checks the drawn stages' connectivity and labels, not that a
stage works, and a named IC is crossed between any of its pins. **Its attribution check is not complete.** Every build
now runs the second review's sweep itself (one named part replaced by a part on a net the stage's walk touched, or the
stage cut down to one such part) and lists what it accepts: at `b7f96784`, 2656 entries tried, 15 accepted, 5 on the stage's
own path and the same 10 wrong attributions listed next; at `38dcd764`, 2665 entries tried, 17 accepted; 7 name
only parts of the typed stage's own path (a FET or an inductor in place of the controller that drives it), and 10 are
wrong attributions the check cannot see, each a part bridging the stage's two nets in place of its shunt or regulator
(board A's INA226 monitors U8 to U11, U14 and U17 and feedback resistors R28 and R36, board B's KSZ9897 U1 in place of
LDO U27, board D's TPA6132A2 U7 in place of LDO U1). `power-tree.md` lists all 17. The attributions drawn at `38dcd764`
were therefore also read by hand at this rebuild (an AI reading, not a qualified review): each of the 68 stages'
named parts by its value text against the stage, and each of the 17 enable pins the check reports against the maker's
pin table held in `v2/vendor/` (AP64500 EN pin 3, LM5176 EN/UVLO pin 1, TPS62933 EN pin 2, TPS25963x EN/UVLO pin 3,
TPS22810 DRV EN/UVLO pin 5, TLV758P DRV EN pin 4); no attribution was found wrong. `case_drawings.py` stops when a
generator's outline disagrees with `pcb_board_facts.yaml` or when `frame_seat.py`'s frame bottom disagrees with its
committed output, and it reads the margin tally and M1's worst case from `frame_seat.out` instead of typing them.

## How they were checked

At `b7f96784` the r8int5 integration read every rendered file back again (`tools/readback.py`: problems none, every PDF at
1.00 to 1.01 of its drawing's natural size) and looked at the case plan's raster and at the stages set 5 moved in
`power-tree.md` (board E's tracker, the VIN_RAW lead, U16's and U19's enables through R74 and R133): an AI check, not a
qualified review. Each rendered file was read back at `38dcd764` (`tools/readback.py`): every SVG parsed as XML, no HTML labels, the
"unbuilt prototype" statement present in its text, and rasterised in headless Chromium; every PDF measured with
`pdfinfo` against its SVG's natural size (all eleven at 1.00 to 1.01 of it, one page each) and rasterised with
`pdftoppm` at the same 2400 px. The session then looked at every raster, and at the power tree and the control lines
in tiles of the PDF rasterised 14000 and 11000 px wide: board D's new stages, board B's card rails and per-slot EMCON
stages, board A's gates and enable dividers, board C's buffered read and lamp gate, and the legends. That is an AI
check of legibility and of agreement with the sources, not a qualified engineering review, and it does not make any
drawn design correct. It found one fault, fixed before the files above were written: the case plan's second footer
line ran past the page's right edge, and the "C panel backer ring" label sat on the frame window's line. An
independent check of the rebuild then found two more, both fixed in the files above and read back again: board D's
FB1, a 600R ferrite bead on `+5V_TX` to `+5V_SA`, was drawn orange, the legend's colour for a fuse, because the colour
rule read the designator's first letter (it now reads the part from the netlist and refuses a stage whose description
and parts disagree on being a fuse); and finding 6 gave round 8's R58 and R124 as 62k legs and called U16 and U19 the
only LM5176 stages without an enable divider, where U5 and U7 have none by design (now worded from the netlist, above).

Three rendering choices come from the first readback (hc4, at `e3aedb25`): labels are SVG text, not HTML
(`htmlLabels: false`), so any SVG viewer shows them; the ELK layout replaced Mermaid's default because the default
overlapped edge labels in the protection-state and lanes diagrams; and edge labels sit on opaque white boxes
(`themeCSS` in `tools/mermaid.json`), because Mermaid draws their background at half opacity and every edge line ran
through its own label's text.

## The reviews of the first drawing, and what the rebuild did with them

Two AI reviews of 27 September 2026 read the drawing of `e3aedb25` (`v2/docs/records/handover/hc4-reviews.md`). Their
two blocking findings were fixed before that drawing merged: the power-tree walk that accepted a wrong controller (now
the path rules above), and the Z stack's frame drawn without its skirt (now drawn in section from `frame_seat.py`,
with detail A). The rebuild at `38dcd764` acted on these of their other findings:

- **Round 8** (both reviews): `TREE` follows board D's transmit chain; the control lines follow round 8's gates.
- **Unmapped logic parts drawn as plain ICs** (first review): the five pin maps, and the refusal described above.
- **The attribution check's classes (1) and (3)** (second review): closed; class (2), a part bridging the stage's two
  nets, stays open and is measured on every build.
- **The PDFs fitted to a 600 pt page** (both reviews): natural size, checked by the readback.
- **FET pins assumed to be SOT-23's** (second review): read by name, polarity checked.
- **Capacitors listed as pulls** (second review): the section is "pulls and filters" and says which is which.
- **"35 of 70 OPEN" typed in the case plan** (second review): read from `frame_seat.out`.
- **The case plan's clipped footer and the backer-ring label** (second review): fixed.
- **The pack block's base not in the Z stack's NOT SHOWN** (both reviews): stated in the table above; the drawing's own
  legend still does not name it (open, `case_drawings.py`).
- **The fifth energy-chain item is not a chain item** (second review): numbered and worded apart above.
- **Board A's R74 and R133** (second review's circuit lead): printed by the build as a netlist finding.

## Session choices at this rebuild

Taken by the session under the owner's standing rule of 26 September 2026 (`ruled_by: SESSION`); none changes a
requirement, a function, a protection or the scope of any drawing.

| Id | Choice | Why | Reversal |
|---|---|---|---|
| SC-W3G-1 | Board D's transmit supply drawn as three stages, `+5V_D8` to `+5V_TX` through U21, then FB1 to `+5V_SA` and U15 to `VGG_SW`, with U21's label naming what the netlist gates it on: TXSUP_EN, set by R90 and R91 from `+3V3_D8`, the EMCON gates' supply (EMCON L4), not an EMCON line itself | it is what board D's round 8 netlist carries (`gen_sch_d.py`, the EMCON L4 block at U21); a label saying "EMCON" would claim a path the netlist does not have | change `TREE` when board D's generator gates U21 differently |
| SC-W3G-2 | The power-tree check tightened (controller an IC, no LED as inductor, the enable-label check and its negative class) and the second review's substitution sweep run and listed on every build as a measurement, not a refusal | the review's counts were at `e3aedb25`; wording that stays honest at each new commit needs the count of that commit; the two closed classes are the review's own recommendations | restore `power_tree.py` of `38dcd764`: the drawing is unchanged, only the check's reach shrinks |
| SC-W3G-3 | Board B's card rails labelled with their enables (S1A_EN, S2A_EN, S3A_EN) and the EMCON_ON line that pulls each low | round 8 made those enables EMCON's supply removal (SD-EMC-1r8); the enable part of each label is now checked, and `control-lines.svg` shows the EMCON_ON{s} stage that drives it | drop the parenthesis from the three labels |
| SC-W3G-4 | Control lines drawn per slot (EMCON_ON1..3) and followed through series resistors, with the refusals above | without them the round 8 gates ended each line at a plain IC or at a divider, one hop short of the converter the line switches | remove the series hop in `downstream()`; the refusals stay |
| SC-W3G-5 | PDFs at natural size, SVGs still fitted to the window | the reviews' finding: PDF text at 1 to 2 pt | render the PDF pass with `mermaid.json` |
| SC-W3G-6 | A power-tree edge is orange only when every part it names is a fuse as the netlist gives it (KiCad's `Device:Fuse` or `Device:Polyfuse`, or board P's F2, the Eaton SCF9550 on a connector symbol, by its value text), and the build refuses a stage whose typed description and parts disagree on being a fuse; the grey legend names every other kind of series stage the tree carries | the designator rule drew FB1, a ferrite bead, as overcurrent protection the exciter supply does not have (independent check, pass 2) | restore the designator rule of `38dcd764` (it redraws FB1 orange) |
| SC-R8I5-1 | At the r8int5 integration, `power_tree.py`'s TREE and LEADS follow set 5's netlists: the tracker stage without R5, the VIN_RAW lead on P_VR and J_VR1, E5 routing for P_VR, the legend's VBAT_RTC and PWR-F12 sentences | the build refused set 5's netlists (R5 no longer on the path; J_BLK and J_DOCK pins 1 to 4 on GND) and writes nothing when it refuses | restore w3g's entries, which set 5's netlists refuse |
| SC-W3G-7 | Board A's R4T-F3 paragraph in `power-tree.md` printed from a census of every LM5176 EN/UVLO pin read from the netlist, its comparison sentence printed only while the census still bears it out | the typed paragraph carried a pre-round-8 value and a wrong comparison (independent check, pass 2); read values cannot go stale | return to a typed paragraph |

## Open items

- The pack block's base and hold-down are not in the Z stack's own NOT SHOWN legend (S-27 owes the design).
- The power-tree legend's sentence (since r8int5: "The chain file does not yet carry PWR-F12's F2 stage") is typed; it
  holds while finding 1 prints and must go when the chain owner adds the F2 stage.
- Class (2) of the attribution check stays open: a named IC is crossed between any of its pins because the netlists
  carry no pin roles (3301 of the 3498 IC pins in the six netlists are typed passive), so each rebuild repeats the reading
  by hand of the typed attributions.
- The diagrams show the netlists, not their correctness: the circuit reviews, the EMCON bench rows and the rest of
  layer 4's items are in `v2/docs/handover/LAYER-STATUS.md`.
