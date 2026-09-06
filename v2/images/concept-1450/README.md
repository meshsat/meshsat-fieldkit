# Concept renders, the kit in the Peli 1450 (rendered 6 September 2026, seventh set)

Fifth set, 6 Sep 2026 17:05: the Peli 1450 is modelled from its customer drawing 1451-931 (Peli's STEP bodies are envelopes): seam flanges, lid ladder rails and label recess, latches with pins, padlock protectors, the handle pocket with the U handle and the valve, hinge knuckles, feet pads and end-wall nubs. All nine antenna ports are plain SMA bulkheads; the open views show the Maxtena M1621HCT-P-SMA helical on the Iridium jack and the Quectel YEGD006U1A puck of the LG290P receiver on its lead at the GNSS jack, the closed views none. Rendered on a rented 8x H100 box, Cycles, 256 samples. Prototype design, nothing built.

Seventh set, 6 Sep 2026 18:10 (51 views; the sixth set of 18:05 had the display black because the screen object sat inside the display body): the display shows the MeshSat touchscreen of the tesseract kit; the owner's items of 17:30 (appendix 32.48). Standard views carry no antennas; `antennas-az045`, `antennas-az315`, `antennas-az225` and `antennas-top` show all nine fitted per the picks of appendix 32.46 (the 400 mm VHF whip is a placeholder until the 2 m antenna is picked). `assembly-1-closed` to `assembly-6-dock` are the disassembly sequence for the documentation (closed, lid open, face plate assembly set down east, the rod stack set down west, the battery module set down in front, the empty case with the dock strip and its pigtails); reassembly is the reverse. `back-wall-nocables` and `az135-el40-open-nocables` show the kit without the shore and USB cables. Every one of the nine antenna cables ends at the dock strip (the WiFi P2P paths now blind-mated too), the rods end above the B15 nuts, SOS and ZEROIZE sit under hinged safety covers, the display shows the MeshSat touchscreen. Prototype design, nothing built.

Concept illustrations of the V2 kit as designed on 5 and 6 September 2026 (design record 32.40 to 32.44): the Peli 1450 with the 1450PF frame, the 3 mm aluminium face plate with the four-layer backer board C6 under it, the stack (E4, E5, A21, D7, B15), the battery row along the west end wall, the nine end-wall antenna sockets and the upright connector plate with both cables plugged. Rendered by `v2/cad/render/scene.py` (Blender 4.2, Cycles, 256 samples, eight H100 GPUs of a rented vast.ai box) from the KiCad boards, Peli's 1451-931 CAD and the makers' models; see `v2/cad/render/README.md` for what is real geometry and what is a stand-in. **Nothing in these images has been built.**

Every image carries rulers (white bars, 10 mm ticks, numerals every 50 mm) along the case's edges on the ground and standing at the front corners, a 50 mm floor grid, and a title strip with the view name. Case frame: X along the case, +Y toward the hinge wall, Z from the cavity floor. The nine antenna sockets are drawn as the bulkhead jacks in the end walls; only the two antenna forms the record names are shown (the Iridium patch and the GNSS puck), the others are not chosen yet. The seven blind-mate pigtails run from the couplers down the walls and along the floor to the float clamps on the dock strip, where the SMP-MAX plugs stand up into A21's receptacles; on the west side they pass behind and under the battery module, so the stack and the module lift out without touching a cable. The two WiFi P2P leads go to the M.2 card on B15 (ruling of 5 Sep). The MeshSat mark on the plate is the traced sticker master; the e-paper window sits 8.6 mm above the display glass pocket.

## The inside (27 views)

**stack-no-face-top**: the stack from above with the face plate and backer removed: B15 with the CM5 and its cooler, the LTE card, the M.2 WiFi card, the pigtails to the end walls, the battery row on the west

![stack-no-face-top](meshsat-1450-stack-no-face-top.png)

**stack-no-face**: the stack without the face, three-quarter view

![stack-no-face](meshsat-1450-stack-no-face.png)

**stack-no-face-east**: the same from the east end

![stack-no-face-east](meshsat-1450-stack-no-face-east.png)

**stack-no-face-back**: the same from the hinge side

![stack-no-face-back](meshsat-1450-stack-no-face-back.png)

**level-b15**: B15 on top of the stack

![level-b15](meshsat-1450-level-b15.png)

**level-d7**: B15 removed: D7 (the DMR858M carrier) on A21

![level-d7](meshsat-1450-level-d7.png)

**level-a21**: D7 removed: A21 alone with its SMA nests and the wall pigtails

![level-a21](meshsat-1450-level-a21.png)

**level-a21-top**: A21 from above

![level-a21-top](meshsat-1450-level-a21-top.png)

**level-dock**: A21 removed: the dock strip E4 and the block E5 on the floor, the battery row

![level-dock](meshsat-1450-level-dock.png)

**level-dock-top**: the dock level from above

![level-dock-top](meshsat-1450-level-dock-top.png)

**face-underside**: the face plate and the backer C6 lifted 150 mm on their ribbon and flex, from the front

![face-underside](meshsat-1450-face-underside.png)

**face-underside-top**: the lifted face from above, the plate's top side with the LEDs and the e-paper

![face-underside-top](meshsat-1450-face-underside-top.png)

**top-face**: the face plate from straight above, lid open

![top-face](meshsat-1450-top-face.png)

**face-detail-left**: the toggles, the light switch and the sounder

![face-detail-left](meshsat-1450-face-detail-left.png)

**face-detail-right**: the buttons, the status LED column

![face-detail-right](meshsat-1450-face-detail-right.png)

**battery-row**: the battery module along the west end wall with the face lifted

![battery-row](meshsat-1450-battery-row.png)

**battery-row-inside**: the battery row from inside the cavity

![battery-row-inside](meshsat-1450-battery-row-inside.png)

**dock-joint**: the blind-mate joint on the dock block, A21 removed

![dock-joint](meshsat-1450-dock-joint.png)

**dock-joint-a21**: the same with A21 in place

![dock-joint-a21](meshsat-1450-dock-joint-a21.png)

**west-wall-inside**: the west end wall from inside: UHF, WiFi 2.4, GNSS and SDR couplers and their pigtails

![west-wall-inside](meshsat-1450-west-wall-inside.png)

**east-wall-inside**: the east end wall from inside: LTE, Iridium, LoRa and the two WiFi P2P couplers

![east-wall-inside](meshsat-1450-east-wall-inside.png)

**cutaway**: front wall removed, the face lifted 60 mm: the stack and the battery row

![cutaway](meshsat-1450-cutaway.png)

**cutaway-east**: the same cutaway from the east

![cutaway-east](meshsat-1450-cutaway-east.png)

**connector-plate**: the upright connector plate on the back wall from outside, both cables plugged

![connector-plate](meshsat-1450-connector-plate.png)

**west-wall**: the west end wall from outside, lid closed

![west-wall](meshsat-1450-west-wall.png)

**east-wall**: the east end wall from outside, lid closed

![east-wall](meshsat-1450-east-wall.png)

**back-wall**: the back wall, hinge side, lid closed

![back-wall](meshsat-1450-back-wall.png)

## The case, lid open (eight azimuths at 40 degrees elevation)

Azimuth 0 looks at the front wall (handle and latches), 90 at the east end, 180 at the back wall (hinge, connector plate), 270 at the west end.

| az 0 | az 45 | az 90 | az 135 |
|---|---|---|---|
| ![az000-el40-open](meshsat-1450-az000-el40-open.png) | ![az045-el40-open](meshsat-1450-az045-el40-open.png) | ![az090-el40-open](meshsat-1450-az090-el40-open.png) | ![az135-el40-open](meshsat-1450-az135-el40-open.png) |

| az 180 | az 225 | az 270 | az 315 |
|---|---|---|---|
| ![az180-el40-open](meshsat-1450-az180-el40-open.png) | ![az225-el40-open](meshsat-1450-az225-el40-open.png) | ![az270-el40-open](meshsat-1450-az270-el40-open.png) | ![az315-el40-open](meshsat-1450-az315-el40-open.png) |

## The case, lid closed (four azimuths)

| az 0 | az 90 | az 180 | az 270 |
|---|---|---|---|
| ![az000-el20-closed](meshsat-1450-az000-el20-closed.png) | ![az090-el20-closed](meshsat-1450-az090-el20-closed.png) | ![az180-el20-closed](meshsat-1450-az180-el20-closed.png) | ![az270-el20-closed](meshsat-1450-az270-el20-closed.png) |

The first two sets of 6 September were withdrawn the same day: the first (43 views, mostly outside orbits) drew the closed lid 25 mm too low so the sockets read as lid-mounted and stood invented whips on every socket; the second ended the pigtails at the boards instead of the dock clamps, ran the west ones over the battery module, carried a text stand-in for the mark and left the e-paper window 0.6 mm from the display pocket.
