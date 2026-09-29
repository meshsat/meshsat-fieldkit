# Option A(i) mechanical work package: the lid pack, its harness, the open case's stability, the base pockets

MESHSAT-1357, stream a1mech, 29 September 2026 (branch `fnd/a1mech` from `13b5352b`). **Prototype design, AI review: nothing
here has been built, bought, printed or fitted. Every result is analytical: it is not physical verification and not
fabrication readiness.** M1 and REQ-072 are unchanged (REQ-072 reads FAIL as before); no requirement, purchase or shared file
is changed by this stream. The owner's instruction of 29 September 2026: engineer 4S18P of the ruled Samsung INR18650-35E as
the base pockets' 4S6P (ENERGY-RECONCILIATION section 8) plus a lid module of 4S12P under its own protection board,
preserving the HF set (appendix 32.50 item 16a, the QMX in its r2 lid tray) and the tablet bracket (16d), or naming the
owner decision required.

## The answer in brief

**Corrected 29 September 2026 after the independent AI check (`_scratch/chk-a1mech/CHECK.md`, acceptable: no): its B1 and M1
to M11 are answered in place; section 11 lists each.**

1. **48 cells do not fit in the lid with both the QMX set and a tablet bracket.** At the worst of Peli's figures (44.39 from
   the face top to the lid's ceiling) the lid holds **39 cell places with both kept: 4S9P, 4S15P with the base**. (The first
   issue read 35: an unstated rule kept P2 off the tablet's plan; it is dropped, B1.) On a1elec's two-pack model, run by the
   coordinator for a 4S9P lid (fnd/a1int's `v2/docs/records/a1int/reconcile_lid.out` (commit `b6e5ee70`, lines 21 to 28)) (September reference day, 200 W stage, the lid's charge current scaled per string): **with the
   lid at its 13.23 C basis M1 is NOT met at 400, 650 or 1000 Wp** (164.8, 110.9 and 41.7 Wh unserved); with the lid at +20 C
   it is not met at 400 Wp (39.7 Wh unserved) and is met at 650 Wp (2.0 Wh left) and 1000 Wp (29.4 Wh left). So both kept
   carries M1 neither at the lid's temperature basis nor at A(i)'s 400 Wp. Nothing found reaches 48 with both kept.
2. **What fits 4S12P costs one owner-approved lid function:** B keeps HF and takes the tablet bracket out of the lid (**56
   places, 4S14P**); C keeps an 8 inch tablet and takes the QMX set out of the lid (**61 places, 4S15P**). A 10 inch tablet
   fits only with HF out, and then exactly 48 places (4S12P). With neither: 77 places (4S19P). **That choice is the owner
   decision** (section 3): it removes an item he approved on 6 September 2026, and it reopens D-01, which defers HF, the
   tablet bracket and a second pack from prototype 1.
3. The module that does it: the cells lie flat on a bonded 5052 lid plate (the plate follows the slices), in the ruled base
   block's construction (A06: cells touching, 0.5 wrap, 1.0 end joints), three slices end to end along X with a **second
   layer nested in the grooves** (a module 40.06 deep) wherever the worst margin over the face part under it stays 1.0 or more
   (parts up to 2.90 high: over the LEDs it reads 2.40); one layer (24.00 deep) elsewhere. Every face row meets 1.0 at the
   worst; the tightest are the nested layer over the Xenarc window (3.10) and over the LEDs (2.40), OPEN at the sensitivity
   reading. The counts hold at both ends of a sensitivity reading of the module's inferred allowances, except C10: its 48 is
   exactly 4S12P with no spare place and reads 46 (4S11P) at the least favourable end (m6). A boolean check on the
   solids agrees with the arithmetic for all five arrangements and fails on both controls (`cad/lid_pack_a1_cad.out`).
4. The hinge harness: 12 AWG, assumed 10 A continuous and 18 A for 60 s, a free lead of 169.7 between two ties 150 apart
   along the back channel, bending at about R 94 to R 102 over the lid's travel; disconnect (XT60 and XH) in the back channel
   at X -168 to -134, Z 126 to 136 closed, west of the lid tie. **The crossing of the sealed face plate is not designed** (S-95, EQ-31, which the QMX leads need too).
5. Stability: the lid grows from about 1.4 kg (shell and QMX set) to 4.9 kg in B and 5.5 kg in C (every place filled). The
   open case stands on level ground up to 120 degrees of opening in B's every swept case (110 in C) and tips beyond it with a
   light base. Peli's stop angle is in no held file. **Fix (the session's): a lid stay at 100 degrees**, sized at 53 to 63 N
   static. With it the open case stands on a back slope of 9.5 degrees (B) or 7.0 (C) if it tips on its flat bottom's edge, and
   of only **3.6 (B) or 1.2 (C) if Peli's feet stand 14.5 inboard**, the bound the interim limit takes (B2): option 1 under
   about 3 degrees, option 2 level ground only, until T-A1-3 measures the feet. A backward push of 9 to 13 N at the QMX's point,
   or 6.1 N normal to C's tablet screen at its far edge (7.3 at its centre), tips the lightest swept case.
6. The base pockets: section 8's 4S6P keeps every east row (M4a 1.85 OPEN, M4b, M4c, M6 MET, M5 1.77 OPEN) and mirrors them
   at the west; the west block's top clears board B's C33 by 3.99 at the worst (OPEN). **The west RF jumpers fail as
   assumed:** five of seven cables fall onto the west block, and the only drop past it is its 2.0 gap to board A, under one
   RG-316 (2.49). It stays OPEN as section 8b has it: the west RF entry is re-planned before the west block is taken.

## Files

| File | What |
|---|---|
| `v2/cad/lid_pack_a1.py` | the generator: every input with its source, the arrangements, every face row, the harness, the mass and stability, the base rows (plain Python; imports `panel1450.py`) |
| `lid_pack_a1.out` | its record (sections 1 to 5), regenerated by `python3 v2/cad/lid_pack_a1.py v2/docs/records/a1mech/lid_pack_a1.out` |
| `v2/cad/lid_pack_a1_drawing.py`, `lid-pack-a1-drawings.pdf` | the drawing set, six A3 sheets from the generator (A1-1 arrangement B in plan, A1-2 sections, A1-3 the arrangements and the decision, A1-4 the hinge harness, A1-5 mass and stability, A1-6 the base pockets); read back as images after rendering |
| `v2/cad/lid_pack_a1_cad.py`, `cad/` | the solids (build123d 0.13.0): `lid-pack-a1-B-module.step`/`.stl` (plate, 56 cells at the sheet's maxima, P2's envelope, case frame, lid closed, ceiling Z 154.44), `lid-pack-a1-B-envelope.step` (the zones the face rows are judged on), `lid_pack_a1_cad.out` (the boolean check) |
| `DECISION-A1.md` | the owner's decision sheet, drafted (under 300 words counted by `wc -w` over the whole file; the integrator's to send) |
| `LOG.md` | the stream's running log |

## 1. The lid, at Peli's figures (`lid_pack_a1.out` section 1)

- **Room:** face top Z 106.52 nominal (104.77 to 108.27, C1 on C6) to the ceiling Z 154.44 (152.66 at the worst, the web
  page's 44.45 lid depth on the rim at 108.97 - 0.76): **47.92 nominal, 44.39 worst, 42.11 with every unstated allowance
  taken twice** (`frame_seat.out` M3, the r2 record B).
- **Ceiling:** flat 346.16 x 231.86 (lid STEP #736), then R 16.26 fillets (#594, #1539, #644, #1432) and a small R 1.27 step
  to the drafted walls (373.88 x 261.87 at the parting plane). Every lid item stays 1.0 inside the flat ceiling.
- **Ribs:** none. The lid STEP's cavity faces are the walls, the fillets, the step and the ceiling (face list
  `v2/vendor/peli/1450/1451-931-top.faces.txt`).
- **Gasket land:** the lid seals on the base's tongue outboard of the cavity (X 195.56 to 201.96, CASE-MARGINS 2.3); no lid
  item reaches the cavity walls, so none bears on the seal.
- **Plan clearance at the 28.00 guard caps** (M3): the module's west edge and the tablet bracket stand 1.0 beyond the caps' edge
  and the plan allowance (X -140.94), as every Z row keeps 1.0; no count moves.
- **Plan allowance** between a lid item and a face part: 1.06 (the lid's place on the base 0.76 in the case class, and a
  bonded plate set by a printed locator 0.30; both INFERRED). Minimum clearance 1.0, as every face-room row of the r2 record.

**Face parts standing into the lid** (height above the face top; the full table is in the record):

| Part | Height | From |
|---|---|---|
| SOS, EMCON, ZEROIZE toggles with guards (X -150) | 28.00 | APEM switch guards page 2 (series 20PN closed; the held series is for 12 mm bushings, the CSG for the 5000 is not held: a class bound); without a guard the lever stands 20.75 (APEM 5000 series, RS copy, page 13: -2V lever 14.75 over a 9.00 bushing, less the 3.0 plate) |
| light toggle NKK M2044SD3A01 (X -150) | 16.40 | NKK Series M sheet, PDF page 3 (ordering table): S bat 10.5 on a D3 bushing 8.9, less the 3.0 plate; under no lid item |
| sounder BZ1 | 10.23 | Floyd Bell MC-09-530-Q page 2: max(11.7 - 3.0, 7.9 + 1.57) + 0.76 |
| headset jacks J_HSJ1, J_HSJ2 | **TBD** | U-174/U: no drawing held; their 30 x 30 plan is kept clear of every lid item |
| XFRAME screw heads (the Xenarc rear frame) | 4.00 | cap head class (the r2 record's bound) |
| SW_MAIN, SW_PI, SW_TEST | 3.50, 2.50, 2.50 | C&K ATP19 and ATP16 sheets with their O-rings (the r2 record) |
| status and battery-bar light guides, light sensor | 1.50 | Mentor 1282.5004 (sheet ll14-14) |
| Xenarc window | 0.80 | a bound: the ruling of 2 September 2026 (appendix 14.6) |
| e-paper lens, camera window | 0.05 | panel1450 (camera INFERRED as the e-paper's) |
| plate screws (6-32 pan heads) | 2.40 | class, INFERRED; outside the flat ceiling |
| the QMX set r2 (a lid item) | to 29.30 (unit), 32.30 (frame), 40.90 (knob tips) | the r2 record; its own face rows are unchanged |

## 2. The lid module (`lid_pack_a1.out` section 2; sheets A1-1 and A1-2)

- **Cell:** Samsung INR18650-35E, 18.55 maximum diameter, 65.25 maximum length, 50 g maximum (spec Ver. 1.1, 3.10 and the
  drawing), 3.35 Ah minimum.
- **Construction, the ruled base block's (A06, D-06):** cells touching at 18.55, wrapped 0.5 a side, 1.0 at each end joint
  along the axis for the nickel strip and the fish paper ring. The cells lie with their axis along X, three slices end to end
  (four without the QMX set). A second layer sits in the grooves of the first, 16.065 further from the ceiling; its places are
  taken wherever the face under them allows. Each slice's south edge is set by the face (the headset jacks, TBD, stop the west
  slice at Y -75.07; the other slices run to Y -112.17). No holder brackets: at a 20 mm holder pitch a single layer held about
  33 cells beside the QMX set.
- **Stack from the ceiling:** DP8005 bond 0.20, 5052-H32 lid plate 2.00 (the r2 set's recipe; no hole in the case; one
  rectangle per slice from the slice's south edge, so no plate stands over the TBD headset jacks, M2, and the plate is judged
  as a zone of its own), the block
  (19.55 one layer, 35.61 two), a PORON 4701-30 pad 1.00, a cover 1.25 (a printed UL94 V-0 class shell 1.0 with 0.25
  insulation, INFERRED). **Depth 24.00 (one layer), 40.06 (two).** The module's own allowances (bond, plate, standoff, cover)
  0.43 in all, INFERRED.
- **Busbars or nickel:** every cell end lies in one of the slices' end planes, each with its 1.0 joint; the series and
  parallel strips and the group links lie in those joints and in the two 7.0 end bays, where the balance taps leave. The map
  of four series groups is the electrical stream's (the current in each link too).
- **P2**, the lid pack's protection board (**ASSUMPTION** until `fnd/a1elec` reports): board P's outline, 44 x 70, and its
  tallest part 16.17 (Keystone 3568 with its blade, `packfit_west.out`), on 2.5 standoffs: 22.47 deep, 0.28 inside the
  cover's inner face (22.75; the first issue's 3.0 standoffs reached 0.22 into the cover, M1). It is placed at the module corner
  that costs the fewest cells, over the tablet's plan where one is kept (the tablet hangs below the cover; B1); in B the west
  slice, where the XFRAME screws already refuse layer-2 places: 6 cells.
- **Insulation:** the block's wrap on the plate side, the 0.25 liner in the cover, fish paper at every joint.
- **Hold-down:** the block bonded to the plate (cell glue and a fillet, the adhesive TBD: 49 N a cell at 100 g), the cover on
  eight M3 standoffs in the end bays as a catch (343 N each at 100 g if the glue lets go), the pad's preload. The module is
  3.46 kg (56 cells): 3390 N at the r2 set's 100 g load case, a mean 0.073 MPa on the plate's bond. DP8005's sheet gives no
  strength on polypropylene, so the bond is bounded by no held figure: **OPEN at T8 and E1**, as the r2 set's bond is.
- **Venting:** the cell maker names venting as a failure outcome (spec 8.1.2) and states no clearance. Every cell end faces
  its 1.0 joint, the end bays are open slots, and gas reaches the closed case, which Peli's pressure valve relieves (ruling of
  7 September 2026 00:52). The sheet also asks that the pack stand away from heat sources (page 17): the lid is away from the
  PA and the CM5s.
- **Heater:** the lid pack's own mat (section 9h: the charge window starts at 0 C) is not placed; a 1.0 mat under the block
  deepens both depths by 1.0, and the tightest rows still meet 1.0 at the worst (2.10 and 1.40).

**The arrangements** (each the generator's best: the tablet tried landscape and portrait at every place 1.0 mm apart in X and 0.5 mm in Y, P2 at its best corner):

| | Lid functions kept | Places | Lid pack | With the base 4S6P | Face rows at the worst |
|---|---|---|---|---|---|
| A | HF (QMX r2) and an 8 inch tablet | 39 | 4S9P | 4S15P | 0 NOT MET, 16 OPEN |
| B | HF (QMX r2); the tablet bracket out of the lid | 56 | 4S14P (4S12P used, 8 spare) | 4S18P as instructed (4S20P possible) | 0 NOT MET, 26 OPEN |
| C | an 8 inch tablet; the QMX set out of the lid | 61 | 4S15P (4S12P used, 13 spare) | 4S18P as instructed (4S21P possible) | 0 NOT MET, 18 OPEN |
| C10 | a 10 inch tablet; the QMX set out of the lid | 48 | 4S12P | 4S18P | 0 NOT MET, 15 OPEN |
| D | neither | 77 | 4S19P | 4S25P | 0 NOT MET, 44 OPEN |

**Other constructions, counted by hand (ESTIMATE, not in the generator):** holder brackets at a 20 mm pitch, one layer 21.9
deep, hold about 33 cells beside the QMX set with no tablet; the cells' axis along Y (three rows of 66.25 across the lid's
depth) gives arrangement A about 30 (a first-issue hand count, P2 kept off the tablet), because the headset jacks cost the south row in four columns and an 8 inch tablet's band
(133) spans two of the three rows. Neither beats the generator's layout, so the finding is stated for this construction
family: **no arrangement found holds more than 39 with both functions kept** (the check's bound with P2 costing nothing: 43). The counts do not hinge on the module's
INFERRED allowances: with every one set to its most favourable value (plan 0.76, bays 5.0, lips 2.0, own allowances halved)
and to its least favourable (plan 1.50, bays 9.0, joints 1.5, wrap 0.6, lips 4.0, own allowances doubled) A reads 39 and B 56
at both ends, C 61 and 60, C10 48 and 46 (`lid_pack_a1.out` section 2, SENSITIVITY; a sensitivity reading, not a bound).

The tablet, where kept, hangs under the module's one-layer part in a bracket (3.0 lips, 1.0 back, 1.5 below the screen),
36.60 below the ceiling; it costs the two-layer places above its band. The design envelopes are the rugged classes (8 inch
214 x 127 x 10.1, 10 inch 243 x 170 x 10.2; INFERRED, no maker sheet held; the model is a pick, SC-45). **With the QMX set in
the lid a 10 inch tablet does not fit at all** (it needs 249 in X, 223.14 is free between the guard caps, with 1.0 beside them, and
the tray).

## 3. The owner decision, stated precisely

**Question:** Option A(i) needs 48 cells in the lid. The lid holds them only if one of the two lid functions the owner
approved on 6 September 2026 leaves the lid. Which one?

1. **Keep HF (16a, the QMX r2 set as released); the tablet bracket (16d) leaves the lid** (arrangement B, 56 places, 48
   used): the tablet is carried outside the case and still works on the kit's WiFi and the USB-C outlet; REQ-011's bracket is
   not met. Lid 4.9 kg with every place filled; with the stay the open case stands on a back slope under 3.6 degrees if
   Peli's feet stand 14.5 inboard (the interim basis, B2), 9.5 if it tips on its flat bottom's edge.
2. **Keep the tablet bracket (8 inch class); the QMX set leaves the lid** (arrangement C, 61 places, 48 used): HF inside
   (16a) is lost, because the base has no volume for it (appendix 32.60: no bay on B16 cleared the unit, the reason it went to
   the lid; the west pocket now takes the second block); outside the case it would need a lead through the back wall, which
   the ruled connector plate does not carry. Lid 5.48 kg with every place filled, 4.83 kg with 48 fitted; with the stay the
   open case stands only on about level ground (1.2 degrees) if the feet stand 14.5 inboard (the interim basis, B2), on 7.0
   degrees if it tips on its flat bottom's edge.
3. **Keep both and a 4S9P lid pack** (arrangement A, 39 places, 36 used; 4S15P in all): not Option A(i). On a1elec's two-pack
   model (the coordinator's run, fnd/a1int's `v2/docs/records/a1int/reconcile_lid.out` (commit `b6e5ee70`, lines 21 to 28); September reference day, 200 W stage) M1 is not met with the lid at its 13.23 C basis at
   400, 650 or 1000 Wp, and with the lid at +20 C only from 650 Wp (2.0 Wh left). It does not carry M1 at the lid's
   temperature basis or at A(i)'s 400 Wp.

Whichever is taken, D-01 (which defers HF, the tablet bracket and the second pack from prototype 1) is reopened by Option
A(i) itself. The session's engineering view, for the owner's sheet only: option 1 keeps a radio bearer inside the kit and
leaves 8 spare places. The energy figures that go with 4S18P are section 9e's (91.0 Wh left at +20 C, down to about +12.9 C,
with 400 Wp in a 200 W window), not this stream's.

## 4. The hinge harness (`lid_pack_a1.out` section 3; sheet A1-4)

- **Current (ASSUMPTION for `fnd/a1elec`):** the lid pack alone carries the kit's 10 A continuous and 18 A for 60 s (the base
  pack isolated; PWR-F12, section 8a) and up to 8.6 A of charge (section 9g). **Conductor:** 12 AWG fine-strand silicone, OD
  4.4 (INFERRED class; no wire sheet held), as the pack lead of ASSEMBLY.md section 3: a 1.6 m loop of 8.34 mOhm, 150 mV and
  2.7 W at 18 A, an adiabatic rise of 8.9 K over 60 s.
- **Route (B):** from P2 through the module's west bay north to the back channel (between the module's north edge Y 114.93
  and the lid's back wall), east along it on bonded tie mounts to the lid tie T_L at X -121 on the lid's inner back wall
  (Y 128.0, Z 111.5), then a free lead to the plate tie T_P at X 29 on the face plate's full-thickness face near its back edge
  (Y 122.0, Z 106.52; the 5.0 rebated band beyond it cannot take a 4.4 lead under the lid wall at Y 130.9), then to the crossing. About 0.45 m in the lid.
- **Travel:** the hinge axis is not in any Peli file: ESTIMATE Y 155 +-8, Z 111 +-5, inside the fairings. T_L turns at R 27.0
  about it; the chord T_L to T_P runs from 150.2 (closed) to 161.6 (180 degrees). The lead between the ties is 169.7: closed
  it bows 33.1 in the back channel's X-Z plane (16 wide in Y, about 40 tall), radius about 102; open it forms an S across 60.1
  over 150, radius about 94. **Requirement on the pick:** a flexing radius of 10 x OD (44) or less.
- **Strain relief:** a bonded tie mount at T_L, at T_P and every 60 mm or less on both runs (the r2 set's rule); a printed
  guide on the lid's back wall keeps the free lead inboard of the lid wall (Y under 130.9) so that closing folds it toward the
  face, never over the rim or the seal.
- **Disconnect** (M9, m5): an XT60 pair and a JST XH 1x4 for SMBus in the back channel (Y 114.93 to about 130.9, 16 wide, about
  40 tall) at X -168 to -134, Y 118 to 126, Z 126 to 136 closed (18 to 28 below the ceiling), 13 west of the lid tie T_L (X -121,
  Z 111.5) and west of the free lead's bow, lying along X, so the lid comes off its hinge as ASSEMBLY.md section 7 has it; the lead is fused at
  P2. The held sheet (Amass XT60-F, V1.2, `v2/vendor/battery/amass-xt60-spec-tme.pdf`): 30 A rated, 60 A instantaneous, 12 AWG
  recommended, 1000 mating cycles, -20 to 120 C, 0.55 mOhm: it carries the assumed 10 A and 18 A. From P2 the two 4.4 leads run
  one above the other in the 7.0 west bay (8.8 of its 22.5 depth under the plate), beside the cover's standoffs at the bay's
  ends, the group links and the balance taps (thin leads); no cross-section of the bay is drawn beyond that (OPEN at T9).
- **Bend radius source** (M9): no conductor sheet is held; the 10 x OD flexing radius and any flex life are INFERRED
  requirements on the pick, not a maker's figure.
- **Not designed: the crossing of the sealed face.** It is S-95's crossing (EQ-31), which the QMX leads already need; this
  harness adds two power poles of 25 A or more and four signal contacts, sealed mated and unmated, at a site clear of the
  frame's ring, the backer's top strip and B16's tall parts. Until it is designed the lid pack cannot be connected with the
  lid closed and sealed.
- **The QMX's DC lead:** the r2 set loops it back at R 20 west of the tray, where the pack now lies. It is re-routed east:
  from its plug's end (Y -92.9) an R 20 turn east along Y -112.9, then R 20 north in the fillet lane X 174 to 184 to the hinge
  (sheet A1-4). A change to ASSEMBLY.md step 10's wording, proposed here, not made.

## 5. Mass and stability (`lid_pack_a1.out` section 4; sheet A1-5)

- **Added to the lid by the pack (B):** 3.54 kg (56 cells 2.80 at the sheet's maximum; plate, cover, strip, wrap and glue, P2,
  harness; ESTIMATE but the cells). The lid in all: 4.89 kg with the QMX set and the shell (0.99, an area share of Peli's 2.5
  kg, ESTIMATE). A: 4.53 kg. C: 5.48 kg with its 61 places filled, 4.83 kg with 48 fitted.
- **Base:** shell 1.51 kg; contents swept 7 to 14 kg at Z 45 to 65 and Y -20 to +20 (ARCHITECTURE.md 11 sources a floor of
  about 7.0 kg). Tipping line Y 114.49 (the outer flat bottom's edge, INFERRED), feet at Z -8.38. The hinge axis (ESTIMATE, no
  Peli figure) is swept over Y 147 to 163 **and Z 106 to 116** (check M4).
- **Centre of mass (B, central estimate: base contents 9 kg at (0, 0, 55)):** the case 15.41 kg; lid closed (-2.2, 3.0, 80.1),
  lid at 90 degrees (-2.2, 58.1, 117.7), at 100 degrees (-2.2, 66.0, 115.4); the lid alone closed (-6.8, 9.4, 138.5).
- **Result (worst over the full sweep):** B stands on level ground at 90 to 120 degrees of opening and tips from 135; A from
  135; C from 120. Critical back slope at 100 degrees: 9.5 (B), 10.7 (A), 7.0 (C). With the feet 14.5 inboard (Y 100, an
  INFERRED bound) B stands on 3.6 degrees at 100 and tips on level ground from 110; A on 4.8; **C on 1.2** (B2).
- **Fix, the session's: a lid stay at 100 degrees** (check M5): 12 mm polyester webbing centred at X -176 (X -182 to -170, 3.3
  inside the lid's end wall at X -185.3 and 13 clear of the guard caps; m2), its slack folded closed against the lid's ceiling
  and fillet at X -185 to -150, Y 55 to 80, 6 deep or less under a bonded elastic keeper (10.4 over the guard caps), from a tab bonded with DP8005 to the lid's
  inner west end wall at (Y 60, Z 140) closed, to a stainless tab under the face plate's 6-32 pan head at (X -179.07, Y
  75.95), which loads Peli's brass insert toward its shoulder (its strong direction, CASE-MARGINS 2.5). The lid's moment about
  the hinge at 100 degrees is 2.1 to 3.2 N m over the hinge sweep; the strap's lever is 39 to 51 mm, so its tension is 53 to
  63 N static and 159 to 190 N at an arrest (a factor of 3, ESTIMATE). Neither anchor has a held strength (DP8005 gives none
  on polypropylene; Peli gives none for its inserts): OPEN at T8 (the tab pulled at 3 times the largest tension) and T-A1-3.
  About EUR 10 (ESTIMATE). **Slope condition (B2):** the feet's place is in no Peli file, so until T-A1-3 has measured the feet,
  the stop and the hinge axis the operator's sheet takes the feet-inboard bound: option 1 open only on ground sloping under about
  3 degrees toward the hinge side (3.6 at the worst), option 2 on level ground only (1.2); with the case tipping on its flat
  bottom's edge the limits would be 9.5 and 7.0.
- **Operator loads** (check M6, m1): a horizontal backward push at the QMX set's point (Z about 251) tips the lightest swept case
  on level ground above 11.7 N (B), 12.8 N (A) or 9.3 N (C, the same point); a push normal to the tablet's screen tips it above
  7.3 N at the screen's centre and 6.1 N at its far edge in C (13.7 and 10.8 N in A): the QMX's controls, its jacks or a lid tablet are worked with a
  hand on the case or with the case's back against something; a use limit on the operator's sheet.
- **REQ-023** (under 45.4 kg closed): the central estimate is 15.41 kg with the lid pack; the pack adds about 4.3 kg (3.54 in
  the lid, 0.75 in the base), far inside the limit; the kit's total stays TBD (ARCHITECTURE.md 11).
- **The lid pack's temperature** (section 9h) is not a mechanical result: the cells lie 2.2 (plate and bond) under the lid's
  skin, which faces the sky when the lid is closed and faces backward, away from the operator, when it is open; the lid in
  the sun (D-02e's shade rule) and the cells' temperature basis are the thermal and energy streams' items.

**The tamper magnet** (M10): ASSEMBLY.md's lead table puts the Littelfuse 57140 magnet in the lid for the 59140 reed under the
frame. With the 57140 the 59140's normally open option S pulls in at 9 to 16 mm (Littelfuse sheet 2022-03-25, table 5). The
reed's place is not fixed in the tree; the lid keeps two places no lid item covers, the west end zone south of the stay (X -186
to -173, Y -110 to 40; the stay and its folded slack take Y 55 to 80) and the east end zone beside the QMX DC lead (X 172 to
185, Y 100 to 115, north of the lead's turn), each near the parting plane (Z about 110). A reed under
the frame's ring (Z 94 or lower) is 16 mm or more below them, at or past the far end of that range: the reed's place, on the
plate's underside near an end (Z about 103.5, 6.5 below the magnet), is an item for the face's next issue. OPEN.

## 6. The base pockets (`lid_pack_a1.out` section 5; sheet A1-6)

| Row | Worst | x2 | Verdict |
|---|---|---|---|
| M4a east / west mirror | 1.85 | 0.85 | OPEN (placed by hand; T4) |
| M4b east / west | 7.38 | 6.38 | MET |
| M4c east / west (entry plate screw heads) | 3.18 | 1.80 | MET |
| M5 east (group between the legs) | 1.77 | 0.27 | OPEN (T4) |
| M5w west (block alone) | 37.77 | 36.89 | MET (its Y place is not ruled; centred) |
| M6 east | 3.66 | 2.90 | MET |
| M6w west (C33 on board B) | 3.99 | n/a | OPEN (A06's tool reads no x2; T4) |

The west mirror rows hold because Peli's cavity is the same at both ends (end-wall ribs at Y 0 and +-76.2 on both walls, R
15.88 on all four floor edges: VERIFIED in CASE-MARGINS 2.3) and both RF entry plates share one outline (panel1450 C4).
**The west RF jumpers fail as assumed** (sites at Y -62 to +62 fall onto the block; the only drop past it is 2.0 against a 2.49
cable): OPEN in the M17 class, the west RF entry to be re-planned before the west block is taken (section 8b). The hold-down
(S-27) and the second heater mat (8d) stay open for both blocks.

## 7. What is shown at desk, what needs the mock-up, what is the owner's

**Shown at desk (analytical):** the lid's volumes from Peli's STEP and web figures; every face part's height from its maker's
sheet where one is held; the five arrangements and their face rows (arithmetic, and the same verdicts by booleans on solids);
the harness geometry over the lid's travel; the mass and tipping sweep; the base rows by mirror of `frame_seat.out`.

**Needs the mock-up** (the new case of the current moulding, OD-01's purchase; `TEST-PLAN.md` and `CASE-MARGINS.md` section 5):

| Check | What it closes |
|---|---|
| T1 at receipt (OD-01's checkout list) | the moulding the lid figures come from |
| T-A1-1 (new): the lid's depth from the rim to the ceiling at the module's footprint, and the flat ceiling's extent | the 44.39 the whole module rests on (the web page's 44.45 against the STEP's 45.47) |
| T9, extended: chalk on the module's cover (a dummy of the envelope STEP), the face parts and the tablet's bracket, lid closed | the OPEN face rows (the window 3.10, the battery bar 2.40 at the worst) |
| T8, extended: a pull test of a 5052 plate bonded with DP8005 on Peli's polypropylene after a thermal cycle, loaded to the module's 3.4 kN | the bond |
| T-A1-2 (new): the U-174/U jack in hand or its drawing | whether the west slice may run further south (TBD) |
| T-A1-3 (new): the lid's stop angle, the hinge axis, the open case on a slope with ballast at the module's mass | the stability sweep and the stay |
| T-A1-4 (new): the lid opened and closed 200 times with a 3.5 kg dummy module and the harness dummy, then E1's drops | Peli's hinges and stop, the harness's bow and ties, no pinch at the rim |
| E1, E2 (TEST-PLAN) with an accelerometer on the lid | the retention at 100 g, the lid's response |
| T10, T5 (west wall) | the west RF re-plan for the west block |

**The owner's:** section 3's choice (HF or the tablet bracket in the lid), and with it D-01's reopening. Nothing is bought.

## 8. Decisions taken by the session (authority SESSION, the owner's standing rule of 26 September 2026)

| Id | Decision | Reason | Reverse by |
|---|---|---|---|
| SC-A1-01 | The lid module is built in the ruled base block's construction (A06), a second layer nested in the grooves | a holder at a 20 mm pitch fits about 33 cells beside the QMX set; the block's basis is already ruled for this cell | a maker's holder whose stated pitch and height fit the rows |
| SC-A1-02 | Cells along X in three slices (four without the QMX set), anchored at the hinge side, each slice's south edge set by the face | the face's tall parts are at the west strip and the south-west corner; the hinge side is flat | a slice layout that keeps more places at the same rows |
| SC-A1-03 | P2 at the corner that costs the fewest cells, over the tablet's plan where one is kept | board size is an assumption; the corner is re-chosen when P2 reports; P2 lies above the cover, the tablet below it | the electrical stream's board outline |
| SC-A1-04 | The tablet, where kept, hangs under the one-layer zone, not in the lid's west third | the west third holds the guarded toggles (28.00), which no lid item may cover; the 32.51 placement (clear of the boxed Xenarc) predates the monitor's recess of 9 September 2026 | a tablet place that keeps more cells |
| SC-A1-05 | The tablet's design envelopes are the 8 and 10 inch rugged classes | no maker sheet held; the model is a pick (SC-45) | the pick's sheet |
| SC-A1-06 | The QMX DC lead re-routed east of the tray | the pack lies west of it | an arrangement without the pack west of the tray |
| SC-A1-07 | Harness: 12 AWG, two ties 150 apart along the back channel, disconnect beside P2 | the lid's travel becomes a gentle bend of a long run instead of a tight loop at the hinge | the electrical stream's conductor and a mock-up (T-A1-4) |
| SC-A1-08 | A lid stay at 100 degrees, 12 mm webbing at X -176 between a bonded tab and a tab under a plate screw | the open case tips from 120 (C) and 135 degrees (B) in the sweep; Peli's stop is not stated | Peli's stop measured at 100 or less (T-A1-3) |
| SC-A1-09 | Plan allowance 1.06 between lid items and face parts | the lid's place (0.76, the case class) and a bonded plate's (0.30) | a measured place (T3, T9) |

## 9. For the coordinator: electrical assumptions to reconcile with `fnd/a1elec`

- P2: board P's outline 44 x 70 and tallest part 16.17, 80 g, on 2.5 standoffs (22.47 deep, 0.28 inside the cover); any board up to that envelope
  drops in at the chosen corner; a larger one is re-placed by the generator (its `P2` constant).
- Harness current: 10 A continuous, 18 A for 60 s (the lid pack alone), 8.6 A charge; 12 AWG; a fuse at P2 (8a's string fuse
  class); the crossing: two power poles of 25 A or more and four signal contacts.
- The series and parallel map of the 48 cells (four groups of 12 across three slices) and each link's current.
- The lid pack's heater mat (1.0 thick fits) and its supply; the lid pack's temperature basis (9h).
- Transport (S-52): the lid pack alone is 579 Wh nominal (48 x 3.35 Ah x 3.60 V); nothing is claimed here.

## 10. Proposed changes to shared files (not made; the integrator's)

- ASSEMBLY.md step 10: the QMX DC lead's route east of the tray (section 4 above); step 10 or a new step: the lid pack, its
  harness and the lid stay, once the owner has chosen.
- CASE-MARGINS.md: new rows for the lid module (the face rows of `lid_pack_a1.out` section 2 for the chosen arrangement), the
  new checks T-A1-1 to T-A1-4, T8 and T9 extended.
- REQUIREMENTS-TRACE REQ-011 (the tablet bracket) and appendix 32.50 items 16a and 16d: nothing until the owner decides.

## 11. The independent check's items, answered (commit `1aefa027` and the README and sheet commit after it)

| Item | Answer |
|---|---|
| B1 | The rule that kept P2 off the tablet's plan had no reason: P2 lies above the one-layer cover, the tablet below it. Dropped; A reads 39 (4S9P, 4S15P in all). DECISION-A1.md and sections 1 and 3 restated from the coordinator's two-pack run: both kept does not carry M1 at the lid's 13.23 C basis or at 400 Wp |
| M1 | P2 on 2.5 standoffs: 22.47 deep, 0.28 inside the cover's inner face (a plan row prints it) |
| M2 | The lid plate is one rectangle per slice, so none stands over the headset jacks; the plate is judged as a zone and built so in the solids |
| M3 | 1.0 in plan beside the guard caps for the module and the tablet (X -140.94); no count moves |
| M4 | The hinge Z swept too (106 to 116): 9.5 degrees at 100 for B; feet inboard 3.6 and tips from 110 |
| M5 | The stay sized: moment, lever, tension (53 to 63 N static, 159 to 190 N at an arrest), anchors and their open strength, the slope condition |
| M6 | Operator pushes: 9.3 to 12.8 N at the QMX's height tip the lightest case; a use limit |
| M7 | C's lid 5.48 kg (61 places), 4.83 kg with 48; tips from 120 degrees, 7.0 degrees at 100 |
| M8 | Item 3 and LOG corrected: layer 2 wherever the worst margin stays 1.0 (parts up to 2.90) |
| M9 | XT60 figures quoted; the disconnect in the back channel; the west bay's content; the bend radius labelled INFERRED |
| M10 | The magnet's two free places and the reed's distance; OPEN on the reed's place |
| M11 | The back channel is 16 wide everywhere; the sheet's word count method stated |

## 12. The focused re-check's items, answered (`_scratch/chk-a1mech/CHECK-2.md`)

| Item | Answer |
|---|---|
| B2 | The interim slope limit takes the feet-inboard bound: option 1 under about 3 degrees (3.6), option 2 level ground only (1.2), both readings with their condition in section 5, the output and the sheet |
| m1 | C's push computed normal to its tablet's screen: 7.3 N at the centre, 6.1 N at the far edge (A: 13.7 and 10.8) |
| m2 | 12 mm webbing centred at X -176, 3.3 inside the end wall; the slack's fold and the magnet's west place (south of the stay) stated |
| m3 | The two-pack figures cite fnd/a1int's `reconcile_lid.out` at `b6e5ee70`, lines 21 to 28 |
| m4 | 223.14, 2.5 standoffs and 22.47 everywhere, the generator's comment included |
| m5 | The disconnect at X -168 to -134, Z 126 to 136 closed, west of T_L |
| m6 | C10's 48 has no spare and reads 46 at the least favourable end |

## Sources

Peli 1451-931 top and bottom STEP, 1450PF STEP and sheet, drawing 1451-931 (`v2/vendor/peli/1450/`); the Pelican 1450 product
page (Wayback, 29 March 2026) as CASE-MARGINS section 1 cites it; `frame_seat.out`; the r2 QMX set and its record
(`v2/release/case-2026-09-27/lid-tray-qmx-r2/`); Samsung SDI INR18650-35E specification Ver. 1.1 (`v2/vendor/battery/`);
APEM 5000 series data sheet (RS copy, `v2/vendor/seals/apem-5000-series-datasheet-rs-copy.pdf`, page 13) and switch guards
(`v2/vendor/switches/apem-switch-guards-series.pdf`, page 2); Floyd Bell MC-09-530-Q (`v2/vendor/seals/`, page 2); C&K ATP19
and ATP16, Mentor 1282.5004 (as the r2 record); 3M DP8005 (`v2/vendor/adhesives/`); Amass XT60 (`v2/vendor/battery/`);
`panel1450.py` (face positions); ENERGY-RECONCILIATION sections 8 and 9; `packfit_west.out`; CASE-MARGINS sections 2 to 5;
ARCHITECTURE.md section 11. No new maker document was filed: Samsung's tablet pages could not be reached from this host
(one refused, none in the Wayback index).

Generated on the rented CAD box (Ubuntu 24.04.5 LTS, Python 3.12.3, the d7fit CAD venv whose `pip freeze` equals
`v2/cad/requirements-cad.lock` line for line apart from its comment line; build123d 0.13.0) from the branch's correction commits
(the solids and `cad/lid_pack_a1_cad.out`; the commit is named in the log's last line), where `lid_pack_a1_cad.py` and the geometry of
`v2/cad/lid_pack_a1.py` have their final content (its later changes, for the focused re-check, are printed lines only). `lid_pack_a1.out` and the drawing set are regenerated on the runner at the
branch's last commit (plain Python 3; matplotlib 3.10.9 for the sheets). AI review only; no qualified mechanical or battery engineer has reviewed this work (D-09's qualified battery
review applies to both packs).
