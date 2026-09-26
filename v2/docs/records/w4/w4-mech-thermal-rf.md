# W4 draft: mechanical, thermal and RF integration budgets (MESHSAT-1357), round 2

Draft for the integrator, for `ARCHITECTURE.md` (budgets) and for candidate requirement records. Round 2 written 26 Sep 2026 in worktree `fnd/w4` at main `82dd1e4d`. Prototype design: nothing in this kit has been built, powered, measured or field deployed. Every number below is read from a file in this tree or a manufacturer document (VERIFIED), derived by arithmetic from such numbers (INFERRED, with the derivation), or TBD with its effect stated. An internal document check here is never a certification. Runtime and power figures are PROVISIONAL (owner condition 2).

Scripts in `drafts/` (stdlib, sub-second, runner-safe; each prints every figure it is cited for, output saved beside it as `.out`):
- `w4-scratch-thermal.py`: conductance and rise bounds, A05 power states, the split solar load.
- `w4-zbudget-vhb.py`: the face Z budget with the VHB pads, worst case and RSS, and the bay alternative.
- `w4-pocket-fillet.py`: the floor fillet against the pack block.

Box evidence in `drafts/box/` (read-only pcbnew pass on the rented KiCad 9 box, clone `/root/r2/w4/repo` at `82dd1e4d`): `w4_heights.py`, `w4_heights.txt`, `w4_heights.json`.

Adjudications applied as settled facts: A05 (power states), A06 (pack geometry), A08 (RM520N antenna ports, read from its source extracts), A09 (LoRa blind-mate X, D8 height). Their folders are under the programme scratchpad `adj/<key>/`.

## R. What changed from round 1

| Challenger item | Round 2 |
|---|---|
| LoRa blind-mate X, 100 on A against 102 on E (A09) | New finding F16. Table 5.1 corrected to X 100. Mock-up cords corrected. |
| D8 standoff reading (A09) | F6 widened. New finding F17 (A32's J_AB2 under D8). New section 2.2b, the A-to-B bay, with box-read heights. The mock-up marks D8's height as open. |
| F9 overstated (Delta lists 40 mm IP68) | F9 restated. Owner question Q3 withdrawn: research first. |
| F10 assumed an ANT0 + ANT1 pairing | F10 restated as a port choice. The tree records no pairing. ANT0 + ANT2 is the two-jack pairing that keeps the n77/n78 primary path. `open-picks.txt:23` is flagged for correction. |
| M11 asked the owner to weigh COTS parts; K1 asked him to design the rod feet | M11 removed. Masses become a datasheet lookup (T7). K1 now checks the session's own proposal RF-1 (section 2.8). The frame measurements and RF checks also leave the owner request (to the STEP record and TEST-PLAN). |
| VHB, laminate and mat sources called "not filed" | VHB 5952 1.1 mm +-10 % and JLC +-10 % are cited and VERIFIED. The mat thickness stays TBD (0.6 to 1.4 mm). |
| VHB missing from the face Z budget | F5 recomputed with the VHB and an RSS (section 2.2): 1.14 nominal, -0.15 worst, 0.56 RSS low. The 1.1 mm must be paid for somewhere; the options are in section 2.2. |
| Floor fillet left out | Added to F1, 2.5 and 2.6 with `w4-pocket-fillet.py`. |
| Solar load attributed to the plate | Split into aluminium, monitor glass and e-paper lens (4.2). Plate rise recomputed. SGP41 judged at +40 C. |
| Arrestor placement called engineering; no earth bond | Now owner question Q5 (scope). Bonding is a prerequisite of every option (5.3). |
| F12 did not cite 32.21 | 32.21's ruling cited (appendix 2337). |
| A06 pack geometry | F1 rewritten on A06's search. Section 2.5 replaced. B21's underside heights read with pcbnew on the box (F2). |
| Missing items | Bottom Nyloc (F7), Xenarc rear frame as a Z item (F18), lid-closed heat sources (4.2), T12 closed from the held APEM 5000 datasheet (F13). |

## 0. Findings, most consequential first

| # | Finding | Status | Evidence |
|---|---|---|---|
| F1 | **The pack as designed fits neither pocket under board B, and only a shrink-wrapped 4S3P of 18650 cells fits at all.** Adjudication A06 searched every 4S layout under the committed B21 (underside at Z 47.9): 4S3P and 4S4P of 18650, 4S2P and 4S3P of 21700; one-height rigid box, stepped box and shrink-wrapped block; board P at the end, beside or on top. **The pack_4s.py rigid box (and any rigid box of its wall, lid and boss construction) fits in no configuration.** 4S4P fits in no packaging in either pocket. The west pocket fits nothing. The fits are all in the east pocket, with board P mounted separately at the block's south end: **4S3P 18650 as a 3 x 2 cross-section of two six-cell sections (56.65 x 133.5 x 38.1 wrapped)**, X spare 1.35 mm, Z clearance 4.53 mm nominal and 3.32 mm with the pads on the mat, against the U.FL leads of WIFISW (3.53 to 6.90 mm across A06's allowance sensitivity). And **4S2P 21700**, marginal: 1.42 / 0.21 mm, -0.29 to -0.79 mm at the pessimistic allowances. | INFERRED (A06 arithmetic on VERIFIED positions; the wrap, joint and fastener allowances are TBD) | A06 `pack_fit.out` SUMMARY, `sens.out`; box read `drafts/box/w4_heights.txt` (1) |
| F2 | **Board B's underside parts over the east pocket**, with heights now read from each footprint's KiCad 9 model on the box: J_AB2 2x5 vertical IDC header body 9.1 mm (Z 38.8), plus a mated socket and ribbon to about Z 31 (INFERRED in A06); six U.FL receptacles 1.25 mm unmated (Hirose catalogue 2.5 mm mated maximum, A06); the pin tails of J_ZBDBG1, J_ZBDBG2 and J_CAM 1.4 mm; the four M4 bracket holes H17 to H20 (hardware under B TBD, 1.8 to 6 mm); J_LIME's tails and pegs TBD. West pocket: U41 LQFP-100 1.5 mm, C33 1812 2.5 mm, ten TSSOP-14 at 1.0 mm, J_ETH and J_PANEL tails. **The box read found no part that A06's obstruction list missed.** | VERIFIED positions and sides (pcbnew); heights INFERRED (generic models, not the makers' maxima) | `drafts/box/w4_heights.txt` (1), `gen_pcb_b3.py:89`, `:92`, `:221` |
| F3 | **pack_4s.py cannot hold its declared contents.** The cell block (Y -116 to +79) and the BMS bay (Y +43 to +113) overlap by 36 mm. The block is declared 52 mm wide, but three 18650 cells need 3 x 18.55 = 55.65 mm at Samsung's maximum diameter. | VERIFIED | `v2/cad/pack_4s.py:11-27`; Samsung INR18650-35E spec 3.13 to 3.14 (`vendor/battery/samsung-35e-akkuzentrum.pdf`) |
| F4 | **No path is drawn for the six east-wall RF leads past the pack.** With A06's fit, board P fills the floor-level chase beside J_AB2 (X 120 to 126, Y -75 to -57). A candidate exists on paper: from the clamps (Y -66) south to the band between B's south edge (Y -100) and the front wall, up above the pack, east to the band between B's east edge (X 165) and the east wall, then north to the jacks at Z 88. Leads on that path run about 210 to 450 mm, against the 150 to 250 mm the wall template assumes. | INFERRED; mock-up K3 checks it | `case_wall_cutouts.py` note; A06 `pack_fit.py` CHASE; `panel1450.py:116-118` |
| F5 | **The face Z budget leaves out the dock strip's VHB pads, and the 1.1 mm has to be paid for somewhere.** The model sums strip, gap, A, spacer and B from the floor (`panel1450.py:23`, appendix 32.41 line 2605). The strip stands on VHB 5952 pads (`ASSEMBLY.md:30`), which 3M lists at 1.1 mm +-10 %. **(a) If the pads lift the stack as written,** the display-to-heatsink margin is +1.14 mm nominal, below the C gate's 2.0 mm floor (`z_budget.py:16`), so the budget would read NOT MET. The worst case over the tolerances with a published number is **-0.15 mm (interference)** and the RSS low is +0.56 mm. **(b) If a 1.1 mm shorter bay spacer holds B_TOP_Z at 49.5,** the face keeps +2.24 nominal (worst +0.95, RSS low +1.66). The A-to-B bay then drops from 31.3 to 30.2 mm and every D8-to-B gap loses 1.1 mm (F17). **(c)** Or the datum changes (section 2.8). This is an engineering decision for the session, not the owner. | VERIFIED inputs; margins INFERRED | `drafts/w4-zbudget-vhb.out`; `v2/vendor/seals/3m-vhb-tapes-family-2018.pdf` 5952 row; `v2/vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md:29` |
| F6 | **ASSEMBLY.md and BUILD.md build the stack with two stale heights.** (1) 38 mm bay spacers with B at 56 mm (`ASSEMBLY.md:11`, `:44`), against B_TOP_Z 49.5 since 9 Sep. The roughly 31.3 mm spacer that realises 49.5 is named nowhere. (2) "M3 x 22.6 mm standoffs" for D8 (`ASSEMBLY.md:18`, `:43`; `BUILD.md:45`, `:75`), where the record's geometry is D8 on 6 mm standoffs with its underside at Z 22.6 (`scene.py:275-277`; appendix 2550 and 3524; A09). 22.6 is an absolute Z written down as a standoff length. | VERIFIED conflicts | A09 adjudication (b); files as cited |
| F7 | **Nothing holds the rod stack to the case except VHB pads, and the record contradicts itself on the rod ends.** Strip E has rod holes only at Y -73 (`gen_pcb_e.py:19`). A and B carry four rods at (+-110.5, +-73) (`gen_pcb_a.py:18`, `gen_pcb_b.py:22`), so the two north rods have no documented foot. `ASSEMBLY.md:11` says "Nyloc nuts top and bottom" on rods that run from the floor, but a strip on 1.1 mm pads leaves no room for a bottom nut. The held 3M sheet places polypropylene in its low-surface-energy group, where 5952 "primer may be needed for good adhesion". So the bond to the Peli floor is TBD; 3M's 620 kPa tensile figure is to aluminium. TEST-PLAN E1 (26 drops from 1.22 m) and E2 load these joints. Proposal RF-1 is in section 2.8. | VERIFIED gap; retention strength TBD | as cited; `3m-vhb-tapes-family-2018.pdf` surface-energy chart and performance table |
| F8 | **The inside-air rise that decides the hot end sits at the optimistic end of an independent range.** Lid open with fans, 32.53 quotes 3.0 to 3.3 W/K; the lumped bound gives 1.22 to 2.85 W/K. On the bound, 32.53's three loaded modules (50 W) rise 17.5 to 40.9 K against its 16 K. A05's PROVISIONAL PS-TYP (60.1 W at the battery) rises 21.1 to 49.2 K. The bound is not pessimistic everywhere: lid closed, its high end (2.49 W/K) is above 32.53's 1.5 to 2. | INFERRED estimate, not a measurement; TEST-PLAN E3 decides | `drafts/w4-scratch-thermal.out`; appendix 2860; `pcb_envelope.yaml:32-37` |
| F9 | **The fans the thermal basis relies on have no part number yet, and the two mixer fans have no position.** 32.53 item 2 rules IP68 fans: one per CM5 cooler and two mixers. `open-picks.txt:17` records that Same Sky and Orion start at 60 mm and ebm-papst at 92 mm, while **Delta lists 40 mm in its IP68 line** but serves part numbers only through a scripted filter. Delta's IP68 page, fetched 26 Sep 2026, still shows 40 x 40 frame filters and no part numbers. The cooler fan rectangles are 30 x 30 mm (`panel1450.py` B16_TALL), so a 40 mm fan changes the face Z plan as well. No file places the two 60 mm mixers: the only mentions are `gen_sch_e.py:376` "under the plate" and the J_FAN headers. | VERIFIED (sources); part number TBD | `open-picks.txt:17`; https://www.delta-fan.com/applications/industrial/industrial-fans-with-ip68.html (26 Sep 2026); `panel1450.py` |
| F10 | **The RM520N-GL has four live antenna ports, and no file records which two the design's two pigtails use.** Quectel's Table 32 (RM520N Series HD v1.1, doc pp. 58-59) and Table 29 (RM520N-GL HD v1.0) agree on the port map. ANT0: LB and MHB TX0/PRX, n41 TX0/PRX, n77/n78/n79 TX1/DRX. ANT1: PRX MIMO and GNSS L5. ANT2: UHB and n77/n78/n79 TX0/PRX, MHB DRX MIMO. ANT3: LB TX1/DRX, MHB DRX, n77/n78/n79 DRX MIMO, GNSS L1. `ASSEMBLY.md:99` names the module's "MAIN and DIV connectors", names the RM520N-GL does not carry. **Two jacks on ANT0 + ANT2** keep the LB, MHB and n77/n78 transmit paths (TX0 and TX1) and lose PRX MIMO, DRX MIMO and the LB diversity path. **ANT0 + ANT1** loses the n77/n78 primary TX0/PRX. `open-picks.txt:23` misreads the table ("ANT0 TX0/PRX low, mid and ultra-high band", "the east wall carries eleven bulkheads"; the east wall carries six) and needs correcting. The RM520N-EU variant differs: n77/n78 TX0/PRX is on ANT0, and it has a fifth GNSS port (Table 33). | VERIFIED (documents); pairing consequence INFERRED | `vendor/quectel/quectel-rm520n-series-hardware-design-v1.1.pdf` sha256 2bae882148b45172; `quectel-rm520n-gl-hardware-design-v1.0.pdf` sha256 139583b38ce1fd47; A08 extracts |
| F11 | **The recommended lightning arrestor fits the wall pitch only just, reaches the frame skirt, and needs an earth bond the design does not have.** PolyPhaser GTH-SFF-AL: 53.34 x 22.86 x 30.48 mm, 113.4 g, 0.6 dB insertion loss maximum. At the 24 mm pitch it leaves 1.14 mm in its best orientation. Centred on Z 88, its 30.48 mm body reaches Z 103, into the frame skirt (Z 100 to 109). Eleven weigh 1.25 kg (thirteen 1.47 kg). A gas-discharge arrestor works only when bonded to earth, but no board declares a chassis or earth net and the ground stud is unpicked (`open-picks.txt:16`). | VERIFIED dimensions and absence; fit INFERRED | `vendor/polyphaser/polyphaser-gth-sff-al-sma-surge-protector.pdf` sha256 ae3f031d7ecb8783 |
| F12 | **High-power antennas share end walls with receiver jacks 24 to 144 mm away.** West: VHF 30 W at Y -72; HF 24 mm, WIFI 2.4 48 mm, GNSS 96 mm, SDR 144 mm. East: LoRa (1 W class) at Y -24; 5G jacks 48 and 72 mm away, Iridium 24 mm. The 6th harmonic of 144.8 MHz is 868.8 MHz, inside EU868. The SDR limiter of `V2-SPEC.md:49` is in no generator and no open pick. The owner's ruling on 32.21 (appendix 2337) made transmit serialisation "no longer a hardware requirement", and "the bridge may keep it as a receiver-protection preference". A receive-protection policy fits inside that allowance. Making it a requirement is a change to W1's modes and goes to the owner as one. | VERIFIED placement and absence; coupling INFERRED | `panel1450.py:117-118`; `V2-SPEC.md:49`; appendix 2337, 2465 |
| F13 | **The recommended toggle guard does not fit the fitted toggle.** The held APEM guard sheet reads "For switch series 12000 - 3500 - 600H - 6000" and "Designed for Diameter 11.9 or 12 mm bushing". The held APEM 5000 series datasheet gives the 5636 a "threaded bushing Diameter 6.35 mm", 1/4-40UNS. `open-picks.txt:10`'s claim that APEM's page covers the 5000M is not in the held sheet. T12 is closed: a guard for a 1/4-40 bushing is owed. | VERIFIED mismatch (two held sheets) | `vendor/switches/apem-switch-guards-series.pdf` sha256 75b96785599eca5d pp. 1-2; `vendor/seals/apem-5000-series-datasheet-rs-copy.pdf` sha256 87fc25f583563940 p. 5; `panel1450.py:67` |
| F14 | **Peli's sources disagree by up to 2 mm on the depth the face depends on, and publish no tolerance.** Base depth: drawing 109, STEP 109.4 (32.42), web page 111. The drawing's note 1 reads "dimensions are for reference only; typical industry-standard tolerances apply". | VERIFIED | `vendor/peli/1450/1451-931-customer-drawing-2025-01-15.pdf` sha256 389facc842e41397; Pelican 1450 page (Wayback id_ capture 2025-11-09) |
| F15 | **The printable case files predate the 9 Sep face change.** `release/revA/case/face-plate/` is from 1f46cf83 (7 Sep), older than `panel1450.py` c2333029 (9 Sep). `case_wall_cutouts.py` lines 2, 19 and 115 say "nine" jacks, and lines 118, 130 and 146 draw the retired battery row. | VERIFIED | `git log` of both paths |
| F16 | **A and E disagree on the LoRa blind-mate X by 2 mm, twice the float, and E's gate enforces the stale value.** Appendix 32.58 (line 2992) moved the LORA site from X 102 to 100. A follows it (`gen_pcb_a.py:38` RF_X; committed A32 `J_BM11` at (100, -66)). E does not: `gen_pcb_e.py:16` RF_SITES and `check_pcb_e.py:45` both use 102, as do the E17 board and `scene.py:278`. The float nest gives 1.0 mm each way (`float_clamp.py:18`), so 2.0 mm of nominal offset uses the whole float and 1.0 mm more, and a blind mate is not assured. **One number does not fix E.** The nest is 16 mm along X (`float_clamp.py:17`): at the 12 mm pitch between IRIDIUM (88) and LORA (100) it overlaps its neighbour by 4 mm, and at X 100 it overlaps the 6 mm spacer tube on rod H2 by 0.5 mm and E's own 9 mm keep-out by 2.0 mm. | VERIFIED (A09, pcbnew read) | A09 adjudication (a); files as cited |
| F17 | **A32 has a tall header under D8, so no D8 standoff height works as the boards stand.** A32's `J_AB2` (2x5 vertical IDC header for the wall-port ribbon, added 12 Sep in 205bd0b6) spans case X 89.5 to 100.5, Y -21.7 to -0.3, inside D8's outline (X 0 to 100.1). Its body reaches Z 25.7 (9.1 mm over A's 16.6). With D8 on 6 mm standoffs, D8's underside is at 22.6, so the header runs 3.1 mm into D8 before its socket, directly under D8's `J_HS2`, whose tails reach down to Z 20.8. D8's through-hole tails (J_HARN1, J_HS1, J_HS2, J_VGG, J_USB3) also cut the A-to-D8 gap to 4.2 to 4.6 mm locally. Upward, J_PWR1 (JST VH, 16.5 mm mounted, A09) leaves 7.2 mm to B's underside for its 18 AWG lead to turn, and 6.1 mm under F5 (b). No gate checks heights under the mezzanine (`check_pcb_a.py:48`, `:57`, A09). | VERIFIED positions (pcbnew); heights INFERRED (KiCad stand-in model; Wurth WR-BHD 9.1 in A09) | `drafts/box/w4_heights.txt` (2); A09 adjudication (b) |
| F18 | **The Xenarc's steel rear frame is a Z item under the plate that no budget carries.** Its drawing is owed (`open-picks.txt:19`). Under the monitor body (bottom Z 72.74) it has about 18.7 mm over the M.2 cards (top Z 54.0). Over the CM5 heatsinks it has only the 2.24 mm margin, 1.14 under F5 (a), where the body overlaps them at Y +32 to +45.7. So its drawing must keep it south of Y +32 or enter the budget. | INFERRED from `panel1450.py` | `panel1450.py` XENARC, B16_TALL; `z_budget.py` run |

## 1. Sources

| Source | Revision or date | Identity | What it gives |
|---|---|---|---|
| Peli 1451-931 customer drawing | dated 1.15.25 (PDF title "1451-931 PID 7-24-2025", created 31 Jul 2025) | `vendor/peli/1450/1451-931-customer-drawing-2025-01-15.pdf` sha256 389facc842e41397 | exterior 411 x 329; sections A-A 259/261, B-B 371/375, 154, lid 45, base 109; note 1 reference only |
| Peli 1450 and 1450PF STEP bodies | 24 Jul 2025 files | `vendor/peli/1450/*.STEP`, probed in 32.41 and 32.42 | floor 360 x 246, under the rim 381 x 267, base 109.4, lid 45.5; floor fillet about 10 mm; frame window 349.65 x 233.83, plate 365.5 x 249.5, lip 8 |
| Pelican 1450 product page | archived 2025-11-09 | Wayback id_ capture (pelican.com answers 403) | empty 2.5 kg, bottom 11.1 cm, lid 4.4 cm, -40 to +88 C, IP67 |
| 3M VHB tapes family | 2018 | `vendor/seals/3m-vhb-tapes-family-2018.pdf` sha256 8ee2ae3acb1ac9ea | 5952: 1.1 mm +-10 %; normal tensile 620 kPa typical to aluminium; polypropylene in the low-surface-energy group, "primer may be needed" |
| JLCPCB capabilities | fetched 16 Sep 2026 | `vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md:29` | thickness +-10 % at 1.0 mm and above |
| RS heater mats | leaflet V9322; RS PRO 245-556 sheet | `vendor/battery/heater/` | 245-556: 50 x 150 mm, 7.5 W, 12 V, **no thickness**; the range leaflet gives 0.7 +-0.1 mm for a different (glass-cloth) range; `battery_module.py` docstring says 1.4 |
| Quectel RM520N | Series HD v1.1 (2023-03-16); GL HD v1.0 (2022-07-15) | sha256 2bae882148b45172; 139583b38ce1fd47 | Table 32 / Table 29 port map, IPEX 20579-001E receptacles on the module, about 8.7 g |
| APEM | guard series sheet; 5000 series datasheet (RS copy, 2018) | sha256 75b96785599eca5d; 87fc25f583563940 | guard for 11.9 / 12 mm bushings; 5636 bushing 6.35 mm 1/4-40UNS |
| PolyPhaser GTH-SFF-AL | sheet in tree | sha256 ae3f031d7ecb8783 | 53.34 x 22.86 x 30.48 mm, 113.4 g, 0.6 dB max |
| Mitsubishi RA30H1317M1 | sheet in tree | sha256 9fda757a | 30 W at 40 % minimum total efficiency; 2nd -35, 3rd -45 dBc max |
| KiCad 9.0.0 generic 3D models | gitlab.com/kicad/libraries/kicad-packages3D tag 9.0.0, fetched 26 Sep 2026 on the box | sha256 per model in `drafts/box/w4_heights.txt` | nominal body heights for F2 and F17 (IDC NarrowPad variants read from the plain header model as a stand-in) |
| Project geometry | main 82dd1e4d | `panel1450.py`, `z_budget.py`, `case_wall_cutouts.py`, `v2/cad/*.py`, generators, appendix 32.41, 32.42, 32.53, 32.56, 32.58, 32.62, 32.85 | the face, stack, walls, pocket |
| Adjudications | 25 Sep 2026 | scratchpad `adj/A05`, `A06`, `A08`, `A09` | power states, pack fit, port map, RF X and D8 Z |

## 2. Dimensional and tolerance budget

### 2.1 The case, three sources side by side

| Dimension | 1451-931 drawing (reference) | STEP as probed (32.41, 32.42) | Pelican web page | Spread | Used by the design |
|---|---|---|---|---|---|
| Exterior L x W | 411 x 329 | 411 x 329 | 418 x 330 | 7 x 1 | not load-bearing |
| Base depth, floor to rim | 109 | 109.4 | 111 | 2.0 | **109.4** (`FACE_TOP_Z = 101.4` = 109.4 less the frame lip 8) |
| Lid depth | 45 | 45.5 | 44 | 1.5 | 46.5 mm plate to lid inner face (`ASSEMBLY.md` step 11) |
| Interior L x W | 371 x 259 (read as at the rim in 32.42) | 381 x 267 under the rim, 360 x 246 at the floor | 372 x 260 | about 10 at the rim | frame and plate from the 1450PF STEP; pockets from the floor figure |
| Floor fillet | not dimensioned | "about 10 mm" (32.42) | | | `case_wall_cutouts.py:32` CHAMFER 10.0; radius or chamfer TBD (M3) |
| Tolerance | "reference only" | none (a model) | none | | **TBD**: the only bound held is the spread of Peli's own figures |

### 2.2 The face Z budget with the VHB pads (monitor body against the CM5 heatsinks)

`z_budget.py` (run 25 Sep 2026) prints body bottom Z 72.74, heatsink top Z 70.50, margin +2.24 mm, against the C gate's 2.0 mm floor (`z_budget.py:16`). `w4-zbudget-vhb.py` adds the VHB and the tolerances:

| Contributor | Nominal | Tolerance used | Source | Status |
|---|---|---|---|---|
| VHB 5952 under the strip | 1.1 (0 in the model) | +-0.11 | 3M family sheet, 5952 row | VERIFIED |
| Strip E, A, B laminates | 3 x 1.6 | +-0.16 each | JLC capabilities: +-10 % at 1.0 mm and above | VERIFIED |
| Case floor to rim | 109.4 | -0.4 (drawing 109; the web page's 111 is on the favourable side) | 32.42, 1451-931 | VERIFIED spread, no tolerance published |
| Board B bow, 40 mm from the nearest rod | 0 | 0.3 (0.75 %) | IPC-6012 class figure, standard not held | INFERRED |
| Frame lip | 8.0 | TBD | 1450PF STEP, frame not bought | TBD |
| PORON 4701-30 ring | 0.53 free | TBD | `ASSEMBLY.md:12`; whether 101.4 includes it is not stated | TBD |
| Xenarc body depth | 28.66 | TBD | drawing v3 at 400 dpi (32.85) | TBD |
| CM5 heatsink over B | 21.0 | TBD | render scene (`scene.py:288-290`), not a Raspberry Pi drawing | UNVERIFIED source |
| Blind-mate gap spacer | 13.4 | TBD (SMP-MAX window 12.4 to 14.4) | appendix 2327 | part not named |
| A-to-B bay spacer | about 31.3 | TBD | derived | part not named (F6) |
| Xenarc steel rear frame | 0 if south of Y +32 | TBD | `open-picks.txt:19` | F18 |

| Case | Nominal | Worst case, published tolerances only | RSS spread | RSS low | Against the 2.0 floor |
|---|---|---|---|---|---|
| (0) today's model, no VHB | +2.24 | +0.95 | +-0.58 | +1.66 | MET nominal |
| (a) VHB lifts the stack (`ASSEMBLY.md:30` as written) | **+1.14** | **-0.15** | +-0.58 | +0.56 | **NOT MET** |
| (b) bay spacer 1.1 mm shorter, B_TOP_Z kept at 49.5 | +2.24 | +0.95 | +-0.58 | +1.66 | MET nominal; A-to-B bay 30.2 mm |

Every TBD row widens both figures. They are optimistic bounds, not limits. The RSS treats each published bound as a three-sigma bound. **Under (a) the stack would interfere at the tolerance extremes that have numbers.** Under (b) the face keeps its margin and the bay pays (section 2.2b). Under (c) the datum changes (section 2.8). Choosing among (a) to (c) is an engineering decision for the session under the 21 Sep ruling. Recommendation: (b) or (c), never (a). Whichever is chosen, `z_budget.py` needs a VHB (or foot) row in its datum chain. That is an engineering change for the one writer of `panel1450.py` and `z_budget.py`, not a relaxation of the gate.

Other Z pairs (VERIFIED by `panel1450.py`, 25 Sep): every deep face part other than the monitor clears B's tall parts by 11.9 to 22.9 mm. The PA flange sits 9.0 mm over the CM5 fans. Above the plate, 46.5 mm to the lid's inner face takes the QMX tray (28 mm), the tablet and its bracket (not drawn, `open-picks.txt:24`) and, if fitted, toggle guards (F13: the held guard does not fit the toggle, so its 22 mm height is not the design's).

### 2.2b The A-to-B bay (new; A09 and the box read)

Datum as `panel1450.py` (no VHB): E 0 to 1.6, gap 13.4, A 15.0 to 16.6, D8 underside 22.6 (6 mm standoffs), D8 top 24.2, B underside 47.9. Heights from `drafts/box/w4_heights.txt` (KiCad models) or A09 (maker sheets).

| Item | Z range | Clearance | Status |
|---|---|---|---|
| A32 `J_AB2` 2x5 IDC header under D8 (X 89.5 to 100.5, Y -21.7 to -0.3) | 16.6 to 25.7 | **-3.1 mm into D8** (D8 underside 22.6) before its socket | positions VERIFIED; height INFERRED (F17) |
| D8 through-hole tails below D8 (J_HARN1, J_HS1, J_HS2, J_VGG, J_USB3) | down to 20.8 to 21.2 | 4.2 to 4.6 mm to A's top; A's tallest top part elsewhere under D8 is C65 to C67 (1210, top Z 19.1), 2.65 mm or more away in plan | INFERRED |
| D8 `J_PWR1` JST VH vertical, 16.5 mounted (JST eVH, A09) | 24.2 to 40.7 | 7.2 mm to B's underside for the lead bend; 6.1 under F5 (b) | bend room TBD |
| D8 `J_HARN1` IDC 2x8 body 9.1 | 24.2 to 33.3 | 14.6 mm for the socket and ribbon fold; 13.5 under (b) | socket height TBD |
| D8 K1 relay, SA868 | to 29.8, 27.4 | 18.1, 20.5 mm | INFERRED |
| D8 `J_ANT`, `J_PAOUT` SMA vertical (Amphenol 132134) with mated plugs and RG-316 at a 12.5 mm bend radius | TBD (drawing blocked, A09) | a right-angle plug fits (INFERRED) | TBD |
| B21 underside parts over D8 | lowest 46.65 (0805 C309, C374) | none over J_PWR1 or J_HARN1 in plan | VERIFIED positions |

The line in `panel1450.py:24-25`, "the tallest thing under B16 is D8's SA868 at Z 27.4", is wrong on either standoff reading. J_PWR1 mated reaches Z 40.7. A32's `J_AB2` has to move out from under D8, or D8's position has to be re-derived. That is an engineering item for A's next regeneration. A mezzanine height check belongs in the A gate (A09).

### 2.3 Plan (XY) items

| Item | Numbers | Margin | Status |
|---|---|---|---|
| Stack lift-out through the frame window | B 330 x 200 through 349.65 x 233.83 | 9.8 mm per side in X, 16.9 in Y | INFERRED; the frame leaves with the plate (32.42 b), so the case at the rim may be the limit |
| Face plate in the frame | 365.5 x 249.5 inside the skirt's 366.7 x 250.8 | 0.6 mm per side | STEP only |
| Connector plate between ribs at X -95 and -18 | `case_wall_cutouts.py:25-28` | about 7 mm to each rib | rib positions TBD on the unit (M6) |
| End-wall jacks at Z 88, 24 mm pitch; nubs at Y 0 and +-83.5; frame-leg bosses at Y +-76 | `panel1450.py:116-118`, template notes | SMA hex 9.5 mm | nub size TBD (M7) |

### 2.4 Connector engagement

| Joint | Tolerance it accepts | What sets its position | Status |
|---|---|---|---|
| SMP-MAX blind-mate (eleven today) | axial 12.4 to 14.4 mm, 3 degrees tilt (appendix 2327); radial 1.0 mm by the float nest (`float_clamp.py:18`) | A's receptacle row (`gen_pcb_a.py:38`) against E's clamp row (`gen_pcb_e.py:16`) | **LORA offset 2.0 mm, beyond the float (F16)**; the other ten rows agree; the R222M00720 funnel is 8.3 mm with a 1.8 mm lead-in, and the held TDS gives no connecting range (A09) |
| Spring pins, A onto the E5 block | "forgive 0.5 mm" (appendix 1413) | the gap spacer and the E5 standoffs | pin travel TBD |
| Ribbons A to B (2x13) and B to A (2x5) | cables | | socket and ribbon heights TBD (F2, F17) |
| Pigtails to the wall couplers | torqued once at the wall | | MHF4 and U.FL mating cycles low (TBD per part) |

### 2.5 The pack pocket (A06 applied)

History: 32.62 measured an east pocket (X +120 to +178, Y -120 to +120, Z 1 to 49) and a west pocket (X -178 to -120, Y -40 to +120), both with B's underside at Z 54.4. B dropped to underside 47.9 on 9 Sep (32.85). `V2-SPEC.md:20`, `ASSEMBLY.md:31`, `:53` and `pack_4s.py:2` put the pack east. The fieldkit handover and the plan's W2 row name the 58 x 160 x 48 west pocket. **A06: the west pocket fits no 4S pack in any packaging, so the record conflict resolves to east.**

| Configuration | Rigid box (pack_4s.py construction) | Stepped box | Shrink-wrapped block, board P separate |
|---|---|---|---|
| 4S3P 18650 | no, width (60.65 against 58) | no, width | **east: fits.** 3 x 2 cross-section, two sections, 56.65 x 133.5 x 38.1; X spare 1.35; Z 4.53 nominal, 3.32 worst base |
| 4S4P 18650 | no | no | no, either pocket (width -17.4 or length) |
| 4S2P 21700 (Molicel P50B used as the representative; the record names no 21700 cell) | no | no, height (-5.5 at WIFISW) | east: marginal, Z 1.42 nominal, 0.21 worst, negative at the pessimistic wrap and joint allowances |
| 4S3P 21700 | no | no | no |

In A06's fitting placement, board P (44 x 70, top about Z 20.2 with the fuse fitted) sits at the south end under B's `J_AB2` socket zone, and the cell block runs north of it under WIFISW. **The floor fillet does not change the verdict:** `w4-pocket-fillet.py` shows the wrapped round corner (radius about 9.8 mm) clears a 10 mm radius fillet by 1.92 mm (and also clears a 10 mm 45 degree chamfer), while a square-cornered box at the same X would ride 1.13 mm up the fillet. The fillet's shape is measurement M3.

Consequences for other workstreams:
- W2's pack-size question (4S3P against 4S4P) has **one physical option standing as the pocket is: 4S3P of 18650 in shrink-wrapped packaging.** 4S4P needs a pack outside these pockets or a board B change that frees about 17 mm of width. That is a scope question for W2 and the integrator to put to the owner only if more energy is wanted.
- **Changing from a rigid box to a shrink-wrapped block is an engineering decision (session).** It moves retention, puncture protection and the heater mat's contact into the design of straps or a cradle. TEST-PLAN E1 and E2 then load the cells directly, a W5 input.
- `pack_4s.py`, `ASSEMBLY.md` section 3 (56 x 236 x 46) and `V2-SPEC.md:20` describe a pack that does not fit (W7 disposition: MODIFY).

### 2.6 Cable bend and routing space

| Path | Space the CAD shows | Status |
|---|---|---|
| East-wall RF leads (6 today, 8 with four 5G jacks) | no drawn path; candidate via the south band and the east band (F4) | mock-up K3 |
| West-wall RF leads (5) | west pocket empty | K3 |
| Pack power and SMBus leads, 350 mm to E's west end (`ASSEMBLY.md` section 4) | the 10 mm between E's south edge (Y -113) and the floor-level front wall (Y -123) lies **entirely inside the floor fillet**, so the leads cannot run at floor level. Above the strip, south of A's edge (Y -80), there is room up to B | INFERRED; K4 |
| RG-316 bend radius | 12.5 mm (`ASSEMBLY.md:77` for the PA lead; appendix line 171, the V1 CAD's validator) | RG-316 loss per metre TBD (cable sheet not held) |
| Lid harness service loop | not drawn | K5 |
| Xenarc HDMI, USB touch and 12 V leads | 2.24 mm over the heatsinks (1.14 under F5 a); the connector side from Xenarc's drawing is owed | TBD |

### 2.7 What CAD can show and what only the physical case can

| Question | CAD in this tree | Physical case |
|---|---|---|
| Parts collide at nominal | yes (`clearance_report`, `z_budget.py`, `check_pcb_c.py`; no mezzanine height check, F17) | |
| The unit in hand matches the 2025 drawing | no | M1 to M9 |
| Accumulated tolerances | only as the budget of 2.2 | by measuring the datum chain |
| Floor flatness, fillet shape | no (the STEP is an envelope) | M3 |
| Wall thickness at the jack line | no | M7 |
| Seal of the face and the walls | no | after build: `ASSEMBLY.md` step 9, TEST-PLAN E6, E7 |
| Lid closure over tray, tablet and guards | only with parts not drawn | K5 |
| Cable routes and bend radii | no drawn cable model | K3, K4 |
| Retention under drop and vibration | no | test only (E1, E2) |

### 2.8 Proposal RF-1: holding the stack without a hole in the case (session engineering, not ruled)

Recorded here so that the mock-up (K1) and the analysis check a concrete design rather than asking the owner to design one. It honours the lift-out ruling ("no connector is unscrewed", `ASSEMBLY.md:131`), so the stack must leave the case without undoing a floor fixing.

1. **Located in plan by a bonded floor plate.** A 1.0 mm aluminium plate sits under the stack's footprint, inside the flat floor (clear of the 10 mm fillet), bonded over its whole area. It carries four rod sockets at (+-110.5, +-73) that locate the rod ends and do not fasten them. The dock strip sits on the plate. A whole-area bond replaces four pads, so the large area buys margin against the unknown adhesion to polypropylene. The 3M sheet asks for a primer on low-surface-energy plastics, so the primer and a bond test on a scrap of the case material become TEST-PLAN items (W5).
2. **Held down by the face.** Each rod ends in a compliant cap, and the face plate compresses the caps about 1 mm when its ten screws go into the 1450PF frame. The frame is fixed to the case rim, so upward drop loads go into the frame rather than into an adhesive. Removing the plate frees the stack.
3. **Z cost.** Plate plus bond is 1.4 to 2.1 mm (VHB 5915 at 0.4 mm is in the tree, 5952 at 1.1 mm) against today's 1.1 mm pads. It is paid through the bay spacer as in F5 (b), which costs the D8 bay the same amount (2.2b).
4. **Open checks, from `panel1450.py` and `gen_pcb_b.py:11` (INFERRED).**
   - The columns above rods (-110.5, +73) and (+110.5, +73) look clear to the plate's underside (Z 98.4).
   - Rod (-110.5, -73) passes 7.9 mm from the Xenarc body's west edge and 9 mm from the rear frame's M4 at (-110.875, -64). The frame drawing is owed.
   - **Rod R2 (+110.5, -73) is covered by the RockBLOCK bracket plate**, which gen_pcb_b.py:11 puts "over rod nut R2" on 8 mm standoffs. Its cap must bear on the bracket, or the bracket moves.
   - Cap stiffness, preload, and the plate's own deflection between its ten screws are TBD.
5. **What the mock-up checks (K1):** the plate footprint against the floor and fillet, the four columns, and a lift-out with the caps in place.

## 3. Mass budget

Sourced masses only. No total is claimed; the sourced subtotal is a floor. **Masses without a manufacturer figure are a datasheet lookup (W6), not a request to the owner**, and the built kit is weighed as a TEST-PLAN item.

| Item | Qty | Each | Subtotal | Source | Status |
|---|---|---|---|---|---|
| Peli 1450 case, empty | 1 | 2.5 kg | 2.50 kg | Pelican page (archived 2025-11-09) | VERIFIED |
| 1450PF panel frame | 1 | TBD | TBD | not in the held sources | TBD, W6 lookup |
| Xenarc 709GNK | 1 | 1.20 kg | 1.20 kg | Xenarc manual v2 | VERIFIED |
| Xenarc steel rear frame | 1 | TBD | TBD | drawing owed | TBD |
| Face plate, 3 mm aluminium | 1 | 448 g | 0.45 kg | area from `panel1450.py` at 2.70 g/cm3 | INFERRED |
| Cells, INR18650-35E, 4S3P (the only fit, F1) | 12 | 50 g max | 0.60 kg | Samsung spec 3.13 | VERIFIED per cell |
| Bare laminate A, B, C ring, D, E, P | 6 | | 0.52 kg | outlines at 1.6 mm, about 1.9 g/cm3 | INFERRED |
| RM520N-GL | 1 | about 8.7 g | 0.01 kg | HD v1.1 | VERIFIED |
| RockBLOCK 9704 (no antenna) | 1 | 35 g | 0.04 kg | RB9704 datasheet | VERIFIED |
| LG290P; E72 x 2 | | 0.9 g; 1.9 g | | module sheets | VERIFIED |
| Arrestors GTH-SFF-AL, if fitted at every jack | 11 (13) | 113.4 g | 1.25 (1.47) kg | PolyPhaser sheet | VERIFIED per part |
| **Sourced subtotal** (4S3P, arrestors fitted) | | | **about 6.6 kg** | | a floor |
| CM5, CM5 Cooler, LimeSDR Mini 2.4, AW7915-AED, NVMe, E22-900M30S, SA868, RA30H1317M1, QMX, fans, connectors, harness, rods, mat, gaskets | | TBD | TBD | datasheet lookup (W6); where no maker publishes a mass it stays TBD and the built-kit weighing closes it | TBD |

## 4. Thermal budget

### 4.1 What the tree already says

- **32.53 (appendix 2860):** plate about 1 W/K surface to ambient at a 30 to 40 K plate rise. Walls and floor about 1.1 W/K still and 2.0 with fans. Totals about 2.1 still and 3.0 to 3.3 with fans (lid open); lid closed 1.5 to 2 with fans. Rises: one CM5 (30 W) +14 still / +10 fans; three loaded (50 W) +24 / +16. Black plate in full sun about 60 W: "the kit runs shaded".
- **`pcb_envelope.yaml:32-37`** carries 10 and 16 K, and `part_temps.py` derives 51 C inside air = max(40 + 10, 35 + 16). The envelope runs one module up to +40 C and the reduced mode above +35 C (`OPERATING-ENVELOPE.md:94`, `:100`).

### 4.2 Heat inside per state

A05's battery-side watts are PROVISIONAL (owner condition 2) and carry a large TBD share. Heat inside is taken as the battery-side watts, which slightly overstates it by what the antennas radiate and the monitor's glass sheds outward.

| State | Heat inside (W) | Basis |
|---|---|---|
| PS-RED, one module, monitor off (lid closed) | 19.7 | A05 |
| PS-RED-b, cluster idle, monitor off (lid closed) | 25.4 | A05 |
| PS-IDLE / PS-IDLE-SPEC (lid open) | 29.4 / 32.4 | A05 |
| 32.53 one module / three loaded | 30 / 50 | appendix 2860 |
| PS-EMCON as generated | 47.6 | A05 |
| PS-TYP, three modules typical | 60.1 | A05 |
| Charge on shore, added | TBD (W2) | the pack sits in the warmest band under B |
| VHF PA key-down, 30 W out | up to 45 into the plate for the key-down time | RA30H1317M1: 40 % minimum total efficiency |
| **Lid closed, also** | QMX transmit loss in its tray in the plate-to-lid gap; the PA's key-down heat into the plate under a closed lid (beacons in transport) | TBD: duty cycles are W1's; missing from round 1 |
| Solar, lid open, full sun (1120 W/m2) | aluminium 43.6 to 46.2; **monitor glass 25.8 to 30.7**; e-paper lens 6.4 to 7.6; the frame ring band 9.0 to 9.5 if black; whole face 84.8 to 93.9 | `w4-scratch-thermal.out`; glass absorptance TBD 0.80 to 0.95 |
| Solar, lid closed | 129 to 144 (black case) or 61 to 91 (light) on the lid top | case colour M9 |

### 4.3 Conductance and rise, an independent bound

| Case | Conductance (W/K) | 32.53 |
|---|---|---|
| Fans on, lid open | 1.22 to 2.85 | 3.0 to 3.3 |
| Fans on, lid closed | 1.06 to 2.49 | 1.5 to 2 |
| Fans off, lid open | 0.77 to 1.57 | 2.1 |
| Fans off, lid closed | 0.70 to 1.45 | not stated |

| State | Rise, fans on (K) | Rise, fans off (K) | 32.53 |
|---|---|---|---|
| 32.53 one module, 30 W, lid open | 10.5 to 24.5 | 19.1 to 39.2 | 10 / 14 |
| 32.53 three loaded, 50 W, lid open | 17.5 to 40.9 | 31.9 to 65.3 | 16 / 24 |
| A05 PS-TYP, 60.1 W, lid open | 21.1 to 49.2 | 38.3 to 78.5 | none |
| A05 PS-RED, 19.7 W, lid closed | 7.9 to 18.6 | 13.6 to 28.1 | none |
| A05 PS-RED-b, 25.4 W, lid closed | 10.2 to 24.0 | 17.5 to 36.2 | none |

**Neither set is a measurement.** The inside-air rise is the most consequential unknown of the hot end. TEST-PLAN E3 must measure it per state, with the floor condition recorded, before `pcb_envelope.yaml`'s 10 and 16 K are used for acceptance. The solar load on the plate also drives heat into the case, which this model does not include.

### 4.4 Parts against the envelope under these bounds

| Part | Range | Under the independent bound | Status |
|---|---|---|---|
| Sensirion SGP41 | -20 to +55 C | One module at +40 C ambient (the envelope's edge): 50.5 to 64.5 C (32.53's 30 W) or 51.4 to 66.5 C (PS-IDLE-SPEC). PS-RED lid closed at +40 C: 47.9 to 58.6 C. Three loaded at +35 C: 52.5 to 75.9 C (50 W), 56.1 to 84.2 C (PS-TYP). **Every state can exceed +55 C at the bound's upper end.** | at risk; E3 decides |
| Board B T1, Pulse H5007NL | 0 to +70 C | at -20 C ambient with 30 W and fans on, inside air about -9.5 to +4.5 C | known (`pcb_part_temps.yaml`) |
| Pack cells | charge 0 to +45 C | the fitted block sits under B in the warmest band; the charge hold-off is the BQ4050's, not the charger's (A02) | W2 |
| CM5 | -20 to +85 C | three loaded reach the throttle point at about +15 to +38 C ambient on 32.53's 29 K die-to-air | INFERRED |
| Xenarc 709GNK | -20 to +70 C | its own glass absorbs 25.8 to 30.7 W in full sun; its temperature is TBD (no thermal data in the manual) | Q4 |
| Face plate aluminium | | 43.6 to 46.2 W in full sun into 32.53's 1.0 to 1.5 W/K: **29 to 46 K over ambient** before any heat from inside; a touch-temperature question for the operator's hand | Q4 |
| RA30H1317M1 PA | case -30 to +100 C | 45 W into a 403 J/K plate: 6.7 K per minute before any loss | INFERRED; voice duty is W1's |

## 5. RF integration

### 5.1 The jack plan as it stands

`panel1450.py:116-118` is the single source: **eleven** SMA bulkheads at Z 88. Each has a blind-mate path J_BM1 to J_BM11 on board A (32.56, corrected by 32.58). The "nine" of 32.42 and 32.46 is history (F15).

| Wall | Y | Path | A's blind-mate site X (`gen_pcb_a.py:38`) | E's clamp X (`gen_pcb_e.py:16`) | Antenna of record |
|---|---|---|---|---|---|
| West | -72 | VHF 144 to 146 MHz, 30 W | J_BM1, -52 | -52 | none picked (`open-picks.txt:18`) |
| West | -48 | HF (QMX) | J_BM2, -38 | -38 | wire kit, BNC at the feed |
| West | -24 | WIFI 2.4 | J_BM3, -24 | -24 | Raspberry Pi antenna kit |
| West | +24 | GNSS (LG290P) | J_BM4, -10 | -10 | YEGD006U1A puck on 5 m (32.46) |
| West | +72 | SDR | J_BM5, +4 | +4 | YECM001L1AH whip (32.46) |
| East | -96 | 5G "MAIN" (port TBD, F10) | J_BM8, +60 | +60 | not picked for 5G |
| East | -72 | 5G "DIV" (port TBD, F10) | J_BM9, +74 | +74 | not picked for 5G |
| East | -48 | IRIDIUM | J_BM10, +88 | +88 | Maxtena M1621HCT-P-SMA |
| East | -24 | LORA (1 W class) | **J_BM11, +100** | **+102 (stale, F16)** | YECT003W1A (32.46) |
| East | +48 | WIFI P2P A | J_BM6, +18 | +18 | YEBT064W1AM |
| East | +96 | WIFI P2P B | J_BM7, +32 | +32 | YEBT064W1AM |

A monopole stubby on an SMA bulkhead in a polypropylene wall has no ground plane. Its match then depends on the cable and the stack, so a return-loss sweep on the case belongs in TEST-PLAN (a W5 input). It is not an owner request.

### 5.2 The 5G jack count

| Option | RF (from Table 32, INFERRED consequence) | Board A | Board E | East wall |
|---|---|---|---|---|
| Two jacks on ANT0 + ANT2 (the best pairing) | keeps LB, MHB, n41 and n77/n78 transmit paths (TX0 and TX1) and their primary receive; loses PRX MIMO (ANT1), DRX MIMO and LB and MHB diversity (ANT3), and the module's GNSS ports | no change | no change | 6 jacks |
| Two jacks on ANT0 + ANT1 | loses the n77/n78/n79 and UHB primary TX0/PRX (on ANT2) | | | |
| Four jacks | DL 4x4, UL 2x2 as Quectel specifies | 13 sites: one fits at X +46 in the 28 mm gap between +32 and +60; the second needs a layout change | 13 clamps, and the nest redesign of F16 | 8 jacks, candidates at Y +24 and +72 (72 is 11.5 mm from the nub at +83.5, M7) |

Whichever option is taken, **the port pairing must be written into `ASSEMBLY.md:99`** in Quectel's port names, not as "MAIN and DIV". Recommendation: four jacks if the owner wants the 5G capability Quectel specifies (Q1). Otherwise two on ANT0 + ANT2, which is the session's engineering choice. The socket key question of W6 and A08 does not change the antenna count, because the four IPEX 20579-001E receptacles are on the module (HD v1.1 section 5.2.1; GL HD v1.0 the same).

### 5.3 Lightning arrestors

`open-picks.txt:20` recommends one GTH-SFF-AL per jack, and the owner-approved gap list (32.50) names "RF arrestors". Options:
- (a) At every wall jack. Needs a mounting drawing, and a Z below the frame skirt or a lower jack line.
- (b) Inline on the external leads of the antennas that go to a mast or outdoors on a lead. The walls stay as they are, and the 1.25 kg leaves the carried mass when no mast is used.
- (c) None on the terminal-mount stubbies.

**Every option needs an earth bond first.** That means the ground stud (`open-picks.txt:16`, unpicked), a bonded arrestor bracket, and a declared chassis or earth net on the boards that meet it (the 21 Sep grounding census in the project memory found no board declaring one). Moving the arrestors from the case to the leads turns an approved kit feature into accessories, which is scope: owner question Q5. Each arrestor's 0.6 dB maximum goes into its path's loss budget.

### 5.4 Path losses

No end-to-end RF loss is recorded for any path (`rf_line.py` judges track width against 50 ohm only). Each path is: device connector, pigtail, top-side jack on A, A's track, the SMP-MAX joint, RG-316 (150 to 250 mm assumed; up to about 450 mm on the east candidate path, F4), the wall coupler, and optionally an arrestor. Every term is TBD until the cable and connector sheets are filed. The measurement is a VNA insertion-loss sweep per path on the built kit, a TEST-PLAN row (W5).

### 5.5 Coexistence of simultaneous transmitters

| Aggressor to victim | Mechanism | Numbers (INFERRED) | Mitigation options |
|---|---|---|---|
| VHF 30 W to HF, SDR, GNSS, WiFi 2.4 on the west wall | front-end overload at 24 to 144 mm from a 30 W whip (2.07 m wavelength) | a few tens of dB of isolation at best | the SDR limiter of `V2-SPEC.md:49` (absent, F12); receive blanking on key-down; VHF antenna off-case on a lead; receiver maximum input levels TBD (T11) |
| VHF 6th harmonic to LoRa | 6 x 144.800 = 868.8 MHz, inside EU868 | the PA sheet specifies only the 2nd (-35 dBc) and 3rd (-45 dBc); D8's low-pass filter decides the 6th (TBD) | LPF attenuation at 868 MHz on the bench; LoRa receive blanking during VHF key-down |
| VHF 11th harmonic to GNSS | 1592.8 MHz, in L1 | very weak against signals near -130 dBm | LPF; separation (both on the west wall, 96 mm apart) |
| LoRa 1 W to 5G/LTE receive, and B20/B8 uplink to LoRa | blocking and desense; 48 and 72 mm at 345 mm wavelength | 10 to 15 dB isolation: up to about +15 dBm at the 5G port | the RM520N's maximum RF input (TBD); power cap; time division |
| Iridium to GNSS | 10 MHz above GLONASS L1 | opposite walls, about 0.41 m: 26 to 29 dB free space | GNSS filtering; time division |
| 2.4 GHz crowding | up to three CM5 radios, an AW7915, two E72, the tablet | contention rather than damage | channel plan |
| EMCON coverage | `V2-SPEC.md:24` omits the CM5 radios, the E72 pair and the LimeSDR transmitter; A05 finds the generators gate LIME_EN, RB_EN, E22_EN, E72_EN and HF_EN in hardware | W5 owns the list | |

None of this has been measured. For the architecture: **simultaneous transmission on every radio, with every antenna on the case walls at the current spacings, is not an achievable default without receive protection.** The owner's 32.21 ruling already allows the bridge to keep a receiver-protection preference. Making a simultaneity rule a requirement is W1's and the owner's.

## 6. TBD register (each with its effect)

| # | Item | Effect while TBD | How it closes |
|---|---|---|---|
| T1 | The unit's floor-to-rim depth; frame lip with the 1450PF fitted | face margin (2.2) unbounded | M2; the fitted-height check when the frame is bought |
| T2 | CM5 Cooler height from Raspberry Pi's drawing | margin row from the render scene | W6 lookup |
| T3 | Heater mat thickness (RS 245-556 sheet gives none; 0.6 to 1.4 mm between the leaflet and the docstring) | pack base, F1 (A06 carried 1.21 to 2.61 mm) | W6 lookup or the maker's answer |
| T4 | Heights of B's J_AB2 socket and ribbon, A's J_AB2 socket, the U.FL leads, H17 to H20 hardware, J_LIME tails | pocket and D8 bay | maker sheets (W6); the box read gives the bodies |
| T5 | Gap and bay spacer parts and tolerances | Z budget | name the parts (session) |
| T6 | Adhesion of VHB to the Peli polypropylene; cap preload of RF-1 | retention under E1, E2 | bond test (TEST-PLAN, W5); RF-1 analysis |
| T7 | Masses of CM5, cooler, LimeSDR, cards, drives, fans, PA, QMX, frame, harness | no kit mass | datasheet lookup (W6); the built kit weighed (TEST-PLAN) |
| T8 | Per-state dissipation (A05 PROVISIONAL, large TBD share) | section 4 | W2 |
| T9 | Inside-air rise per state, lid open and closed, floor recorded | the hot end | TEST-PLAN E3; the optional empty-case heat test (M12) earlier |
| T10 | Antenna match on the polymer case; path losses; RG-316 loss per metre | link budgets | TEST-PLAN rows (W5); cable sheet (W6) |
| T11 | Receiver maximum input levels (LimeSDR, QMX, RM520N, LG290P LNA) | damage risk in F12 | sheets (W6) |
| T12 | **closed:** the held guard does not fit the 5636's 6.35 mm bushing (F13) | | a guard for 1/4-40 bushings: W6 lookup |
| T13 | Case colour; whether the unit has the 1450PF inserts | solar load; face mounting | M1, M9 |
| T14 | Delta 40 mm IP68 part number and height | fan pick, face Z plan | W6 via a distributor |
| T15 | Floor fillet radius or chamfer | pack corner, lead channel | M3 |
| T16 | A32 J_AB2's new position, or D8's re-derived height | D8 bay (F17) | session engineering at A's next regeneration |
| T17 | The float nest redrawn for a 12 mm pitch beside rod H2; E's LORA clamp at X 100 | LORA blind mate (F16) | session engineering at E's next regeneration |

## 7. Owner questions (product, money, scope or risk only; asked one at a time)

Engineering items that were owner questions in round 1 are now the session's (21 Sep ruling): the VHB payment (F5), RF-1, the pack packaging, E's clamp row and nest, A's J_AB2, the two-jack pairing and the mixer-fan positions.

**Q1. 5G capability (what the kit is claimed to be).** Evidence: F10, 5.2. Options:
- (a) Two jacks on ANT0 + ANT2: keep every transmit path and lose MIMO and LB and MHB diversity.
- (b) Four jacks through blind-mate, costing a site on A, E's nest redesign and two wall holes.
- (c) Four jacks, two by direct pigtail, giving up the no-cable lift-out for those two.

**Recommendation: (b)** if the kit is to offer the 5G performance Quectel specifies, otherwise (a).

**Q2. A measurement and mock-up session with the owner's case, and buying the 1450PF frame (money and time).** Evidence: F14, 2.7, `drafts/w4-measurement-request.md` (case measurements and a cardboard mock-up only). Options:
- (a) The case and the mock-up now, the frame's fitted-height check later.
- (b) Buy the frame first.
- (c) No physical check before ordering.

**Recommendation: (a).**

**Q3 (withdrawn from round 1).** The IP68 fan question is not an owner question yet. Delta lists 40 mm IP68 frames (F9), so W6 first retrieves a part number. The question returns to the owner only if no 40 mm IP68 part is obtainable, because relaxing IP68 changes his ruling of 32.53.

**Q4. "The kit runs shaded" as a stated operating condition (residual risk).** Evidence: 4.2, 4.4. In full sun the aluminium runs 29 to 46 K over ambient before any heat from inside, and the monitor glass absorbs 26 to 31 W. Options:
- (a) Record it as an operating condition with a shade accessory.
- (b) Design for full sun.
- (c) Leave it unstated.

**Recommendation: (a) now, (b) as a later qualification item.**

**Q5. Where the RF arrestors go (scope of an approved feature).** Evidence: F11, 5.3. Options:
- (a) At every wall jack.
- (b) On the external leads of mast or outdoor antennas, as accessories.
- (c) None on terminal-mount stubbies.

**Every option needs the earth bond (ground stud and bonding path) first.** **Recommendation: (b)**, with the bond designed into the connector plate.

## 8. Candidate requirement records for the integrator (no final IDs)

| Kind | Statement | Acceptance | Method, phase |
|---|---|---|---|
| constraint | Every face and stack part keeps at least 2.0 mm to its neighbour in Z after the datum chain includes every mounting layer (pads, plate, gaskets) | `z_budget.py` with the mounting row; M2's measured depth | analysis, then inspection at first assembly |
| constraint | Nothing on A's top under the D8 mezzanine, and nothing on D8's underside, crosses the gap between them; nothing on D8's top comes within its lead bend room of B's underside | a mezzanine height check in the A gate | analysis |
| requirement | The rod stack is retained without a hole in the case skin, survives TEST-PLAN E1 and E2, and still lifts out without unscrewing a connector | no loosened joint, seal check passes | test, qualification |
| requirement | Every blind-mate receptacle on A and its clamp on E share one coordinate table | E's sites derived from A's RF_X, or one table both read | inspection (gate) |
| requirement | The pack, board P, the pocket and the leads that pass it are drawn together with B's underside parts | a CAD check against the current B and mock-up K2 to K4 | inspection, before layout entry |
| assumption | Inside-air rise per state is TBD within 7.9 to 49.2 K (fans on) until measured | E3 per state | test |
| constraint | The kit is operated shaded in direct sun (if Q4 (a)) | an operating statement in CONOPS | review |
| requirement | Antennas that transmit above 1 W are not co-located with receiver jacks without a receive-protection measure on each affected receiver | per-receiver protection listed, or a simultaneity rule | analysis, then test |
| requirement | The 5G module's ports that are wired are named in Quectel's port names, and the pairing keeps the n77/n78 primary TX0/PRX path | `ASSEMBLY.md` harness table | inspection |
