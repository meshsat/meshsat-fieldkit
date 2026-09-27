# A09 adjudication: the LoRa blind-mate X and the D8 mezzanine height (MESHSAT-1357)

Tree read: main `82dd1e4d` (runner clone, read only). Box clone `/root/r2/A09-rf-x-and-d8-z/repo` at the same commit, pcbnew 9.0.9, read only; output `drafts/box/a09_geom.out`, script `drafts/box/a09_geom.py`. Text parser for the runner: `drafts/tools/fpread.py`, `drafts/tools/underside.py`. External sources in `drafts/src/` with sha256 below.

Case frame throughout (X east, Y north, Z above the cavity floor, mm).

## (a) LoRa blind-mate X

**Verdict: X 100 is right. Board E is stale since 7 Sep 2026 05:45 (commit 273c5431).** Status VERIFIED.

| Item | Value | Source |
|---|---|---|
| The ruling | "the LORA blind-mate site moves from X 102 to X 100 (its east wall jack does not move)" | appendix 32.58, `v2/docs/MESHSAT-709-geometry-appendix.md:2992` (committed in 3564940a, 7 Sep 02:48) |
| A generator | `RF_X = [..., 88, 100]`, comment "LORA at 100 since the ribbon moved to the east strip, 32.58" | `v2/ecad/tools/gen_pcb_a.py:38`, `gen_pcb_a3.py:65`, both from 273c5431 (7 Sep 05:45) whose diff changes 102 to 100 |
| A32 committed board | `J_BM11` (R222M00720, underside) pad 1 at (100.000, -66.000); `J_RF11` at (100, -56) | `v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb` at b7e0d28f (silk "REV A (A32)", sha256 58e26c67987b1daa); pcbnew read `drafts/box/a09_geom.out` |
| A22 committed board | `J_BM11` at (100, -66) | `v2/ecad/pcb-a-power/pcb-a-power.kicad_pcb` at cbe75988 |
| E generator | `RF_SITES = [..., (88.0, "IRIDIUM"), (102.0, "LORA")]`, comment "mirroring A22 (32.56)" | `v2/ecad/tools/gen_pcb_e.py:16` (3564940a; 273c5431 edited this file and left the line) |
| E gate | enforces 102: `for x, cy in [..., (102, -66)]` | `v2/ecad/tools/check_pcb_e.py:45` |
| E17 committed board | LORA clamp holes (102, -76) and (102, -56); rule area "clamp LORA" X 96 to 108 | `v2/ecad/pcb-e1-dock-e7/pcb-e1-dock.kicad_pcb` at bed211b6, sha256 a462ac2620b9b8d3 (the E17 identity); same on `routed/pcb-e1-dock.kicad_pcb` (E9 silk) and on E6 `pcb-e1-dock/pcb-e1-dock.kicad_pcb` |
| Render | `SMA_X = (..., 88, 102)` | `v2/cad/render/scene.py:278` |
| Superseded table | "J_BM11, +102" and "The LORA site at X 102" | appendix 32.56, lines 2956 and 2958; corrected by 32.58 (the record is append-only) |

**The 1.0 mm float.** The nest is 8.5 mm square for the plug's 6.5 mm body, so 1.0 mm each way (`v2/cad/float_clamp.py:18`, docstring lines 8 to 9; appendix 2468, ruling 5, "an 8.5 mm square cavity for 1 mm of radial float"). The nominal error A against E is 2.0 mm along X. With the nest centred on 102, the plug body gets no closer than X 101.0, which leaves 1.0 mm off the receptacle axis at zero manufacturing tolerance. The nominal error alone uses up the whole float budget and then 1.0 mm more (VERIFIED arithmetic). The R222M00720 funnel is 8.3 mm across with a 1.8 mm lead-in (TDS issue 1107 B, page 1, rendered `drafts/src/r720-1.png`). The held TDS gives no plug-to-receptacle connecting range. The only connecting-range figure is on the bullet adapter's sheet (R222M40050, page 3, `drafts/src/r4005-3.png`), with no number, and it says "A blind assembly is guaranteed if radial misalignment is smaller than connecting range. Otherwise a manual lead-in is necessary". The funnel would push the plug against the nest wall, so a blind mate at 102 is not assured (INFERRED).

**Board E cannot be fixed by changing one number (INFERRED, found here, not raised in round 1):**
- The nest is 16 mm along X (`float_clamp.py:17`, L = 16; E draws it as x +-8 in `gen_pcb_e.py:80`). At the 14 mm pitch it already overlaps each neighbour by 2 mm. With LORA at 100 beside IRIDIUM at 88 the pitch is 12 mm and the overlap is 4 mm.
- Near rod H2 (110.5, -73), a nest at 100 spans X 92 to 108. That clears the bare M3 rod (edge 109.0) by 1.0 mm. It overlaps scene.py's 6 mm spacer tube (`scene.py:268`, edge 107.5) by 0.5 mm, and E's own 9 mm standoff keep-out (rule area X 106 to 115, `gen_pcb_e.py:19,73`) by 2.0 mm. A nest at 102 overlaps the bare rod itself by 1.0 mm. The spacer OD is not specified anywhere in the tree (ASSEMBLY.md:11 says "spacer tubes"): TBD.
- So E needs its LORA clamp at 100 and a nest drawing that fits a 12 mm pitch beside the rod. The cavity stays 8.5 mm, which leaves 1.75 mm walls. By the 21 Sep ruling this is the session's engineering decision, not the owner's.

## (b) D8 height

**Verdict: the record's geometry is D8 on 6 mm standoffs, underside at Z 22.6. "M3 x 22.6 mm standoffs" in ASSEMBLY.md and BUILD.md takes an absolute Z and writes it down as a standoff length.** Status VERIFIED for the record. New finding: the 6 mm reading collides with A32's J_AB2 (VERIFIED geometry, header height taken from a same-class part).

Evidence for 6 mm:
- `scene.py:275-277`: D8 imported with its bottom at 22.6 (`import_board` puts the board bottom at z, `scene.py:121`); standoffs 6.0 tall centred at 19.6 (16.6 to 22.6); SA868 from 24.2 to 27.4. At the first commit 9e63ec37 (5 Sep) the standoff centre was written as `16.6 + 3.0`, that is A's top plus half of 6.
- Appendix 2550 (D7, "Height"): the DMR858M heatsink top at about 49.7 is consistent only with D at 24.2 top copper. The 5 Sep scene has the module box from 35.2 = 24.2 + 11.
- Appendix 3524 (32.85) and `panel1450.py:24-25`: "the tallest thing under B16 is D8's SA868 at Z 27.4" = 16.6 + 6.0 + 1.6 + 3.2.
- No appendix section rules a 22.6 mm standoff (grep "22.6": no D8 hit). ASSEMBLY.md:18, :43 (ba329a1c, 7 Sep 10:41) and BUILD.md:45, :75 (4b58ec9e, 7 Sep 10:29) are the only sources for it.

Stack: E 0 to 1.6, 13.4 mm dock gap (ASSEMBLY.md:11, `scene.py:268`), A 15.0 to 16.6 (`scene.py:274`; A32 1.6 mm thick). B top copper 49.5 (`panel1450.py:23`, B_TOP_Z), so B's underside is at 47.9 (B21 1.6 mm thick). `scene.py:283` puts B's underside at 48.1, a 0.2 mm render difference. The A-to-B bay is 31.3 mm. ASSEMBLY.md:11 and :44 still say 38 mm bay spacers (stale since 32.85, round-1 W4-F6).

| | Reading 1: 22.6 mm standoffs (ASSEMBLY, BUILD) | Reading 2: 6 mm standoffs (scene.py, 32.85, D7 height) |
|---|---|---|
| D8 underside / top copper | 39.2 / 40.8 | 22.6 / 24.2 |
| D8 top copper to B's underside | **7.1 mm** (7.3 against scene.py) | **23.7 mm** (23.9) |
| J_PWR1 JST VH top entry, mounted height 16.5 (JST eVH.pdf) | -9.4 | +7.2 left for the 18 AWG lead to turn (bend room TBD) |
| J_HARN1 IDC 2x8 box header body, 9.1 +-0.15 unmated (Wurth WR-BHD 61201621621; the tree uses 9.5 for a 2x13, `panel1450.py` B16_TALL J_PANEL) | -2.0 before any socket | +14.6 for the socket and the ribbon fold (socket height TBD) |
| J_HS1, J_HS2, J_USB3, J_VGG JST PH, mounted height 8 (JST ePH.pdf) | -0.9 | +15.7 |
| K1 G6K-2F-Y 5.2 (vendor/omron) | +1.9 | +18.5 |
| U2 SA868 3.2 (footprint descr, V1.3 section 8) | +3.9 | +20.5 |
| J_ANT, J_PAOUT Amphenol 132134 (LCSC C3174425) with a mated plug and RG-316 at a 12.5 mm bend radius (ASSEMBLY.md:77) | TBD (the drawing is blocked, HTTP 403, and not in the Wayback Machine). The 12.5 mm bend radius alone is more than the 7.1 mm gap, so no vertical cable exit fits | TBD. A right-angle plug fits (INFERRED) |

Both readings measure to B21's copper. B21's underside over D8's footprint carries only 0402, 0603 and 0805 passives (66 parts, among them 0805 C309 and C374 at (41, -22.6) and (36.3, -22.6); `drafts/box/a09_geom.out`), so the local clearance is about 1 mm less where they sit (heights TBD). If the strip's VHB 5952 pads (BUILD.md:47) lift the stack while B_TOP_Z holds, every clearance under B shrinks by their thickness (TBD; round 1 says 1.1 mm).

**Reading 1 is infeasible:** an unmated IDC header, a mated VH and a mated PH each need more height than there is. The ASSEMBLY and BUILD lines are the stale ones.

**Reading 2 now collides under D8 (new, not in round 1):** A32 has `J_AB2`, a vertical IDC 2x5 box header for the wall-port ribbon. It was added on 12 Sep in 205bd0b6 at `gen_pcb_a3.py:74` "J_AB2": (95, -11, 180). Pin 1 is at (95.752, -16.080) and its bbox is X 89.51 to 100.49, Y -21.71 to -0.30, inside D8's outline (case X 0 to 100.1, Y -40 to 40, D12 board `pcb-d-aprs-d9`, sha256 929bf82d2bf6eed4). The gap is 6.0 mm and the WR-BHD class body is 9.1 mm (the 2x5 member is taken to share the 2x8 height: INFERRED). That is 3.1 mm of overlap before its ribbon socket, which must plug from above. D8's J_HS2 (PH, through-hole) sits directly above at (95.95, -16.0). No gate checks heights under the mezzanine: `check_pcb_a.py:48` checks the holes, `:57` the 2D regions. The rest of A's top under D8 is low (three 1210 capacitors C65 to C67, R55 2512, U14, Q1, test points).

With J_AB2 where it is, no single standoff height works, and this is INFERRED because the socket height and bend room are TBD. The header plus its socket under D8, and J_PWR1's 16.5 mm plus its lead bend over D8, need at least 9.1 + 1.6 + 16.5 = 27.2 mm of the 31.3 mm bay before the IDC socket, the ribbon fold, the VH lead bend and B's underside passives. That leaves at most 4.1 mm for all four.

## Corrections

- W4: `wt/w4/drafts/w4-mech-thermal-rf.md:244` J_BM11 +102 becomes +100. `w4-measurement-request.md:69` cord X +102 becomes +100. `w4-measurement-request.md:57` "22.6 mm above A" becomes "on 6 mm standoffs, underside Z 22.6, 6.0 mm above A's top", with J_AB2 marked as the open collision.
- W3: `wt/w3/drafts/w3-interfaces.yaml` IF-AE-RF names one site table (A's RF_X, LORA X 100), the float budget of +-1.0 mm, and `checked_by: check_pcb_e.py:45 (stale, enforces 102)`.
- Integrator (tree items, one writer): E `gen_pcb_e.py:16` and `check_pcb_e.py:45` go to 100 or are derived from A's RF_X. The float nest is redrawn for a 12 mm pitch and the rod keep-out (`float_clamp.py`). `scene.py:278` goes to 100. ASSEMBLY.md:18, :43 and BUILD.md:45, :75 say M3 x 6 standoffs. The line "tallest thing under B16 is D8's SA868" in `panel1450.py:24-25` is wrong in both readings: J_PWR1 mated reaches Z 40.7. A32's J_AB2 moves out from under D8, or D8's height is re-derived. A mezzanine height rule is added to the A gate. Board E's hold is not lifted by any of this (condition 6).
