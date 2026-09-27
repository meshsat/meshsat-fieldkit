"""The release check of layers 1 to 3 (27 September 2026, MESHSAT-1357, branch fnd/r8int4 at f2b7fa66): the blocking
findings whose fix is wording or a citation, applied once, as the three release reviews state them
(v2/docs/reviews/REVIEW-LAYER-{1,2,3}-RELEASE-2026-09-27.md). Layer 1: B1, B2, B3 (the brief, both READMEs, BUILD.md,
V2-SPEC). Layer 2: B1 (CONOPS 4b.1, 4f and M4, OPERATING-ENVELOPE section 4, TEST-PLAN section 4, PANEL sections 1
and 9), B3 (the filed Review A records, the A06 citation), B4's wording parts (a) and (d) (the reduced mode's
hand-offs; the continuation brief's rows). Every replacement asserts its old text once; a file whose lines other
records cite by number keeps its line count (CONOPS, OPERATING-ENVELOPE, TEST-PLAN, PANEL, V2-SPEC lines 1 to 116).
Usage: edit_release_fixes.py [--write]   (run from the repository root)"""
import sys

WRITE = "--write" in sys.argv
KEEP = {"v2/docs/CONOPS.md", "v2/docs/OPERATING-ENVELOPE.md", "v2/docs/TEST-PLAN.md", "v2/docs/PANEL.md"}
E = []  # (path, old, new)


def rep(path, old, new):
    E.append((path, old, new))


# ---------------------------------------------------------------- layer 1: PRODUCT-BRIEF.md
B = "v2/docs/PRODUCT-BRIEF.md"
rep(B, """The brief is
still a CANDIDATE: that record's finding I5 makes BASELINED wait for a commit that also corrects the EMCON and face
text of `CONOPS.md` and `PANEL.md` (layer 2's part), which is not in this tree yet. History:""",
    """Its finding I5
(layer 2's EMCON and face text in `CONOPS.md` and `PANEL.md`) is answered there since `95e078a1`. The release check
at `f2b7fa66` (`reviews/REVIEW-LAYER-1-RELEASE-2026-09-27.md`, an AI review by a reviewer who wrote none of the
pages) found three blocking items that later merges had caused: B1 (the EMCON count, the 5G module's supply removal,
the EMCON lamp and the 5G socket's land stated as before board B's and board C's round 8), B2 (the case generators
and templates stated as not carrying C1 to C6) and B3 (the night finding of mission M1, requirement REQ-072, missing
from the exclusions and the open items). This revision answers the three at desk; the brief stays a CANDIDATE until a
reviewer who wrote none of the changed lines re-checks them at one pinned commit. History:""")
rep(B, """since `458b2873`, whose land still lacks the
  maker's two locating holes, open item S-12; dual SIM""",
    """since `458b2873`, whose land carries the
  maker's two locating holes since board B's round 8 (`V2-SPEC.md` correction 28); dual SIM""")
rep(B, """  DCF77 and the lightning sensor continue. As generated at `45bde541` the line is drawn to remove the supply of the
  SDR, the RockBLOCK, the LoRa module, both Zigbee and Thread radios, the HF unit and both WiFi link cards, to turn off
  the PA's rail and keying while the VHF exciter keeps receiving, to pull the compute modules' own WiFi and Bluetooth
  disables low, and to put the 5G module in airplane mode through its disable pin, a mode its own firmware carries out
  (`CONOPS.md` section 4b). The session set the latency every inhibit must meet: at most 1 s from the toggle for every
  transmitter, and 20 s for a 5G module that is running, by paths no processor or radio firmware can lengthen
  (SD-EMC-7, requirement REQ-071, `feasibility/EMCON.md` section 5a). Read transmitter by transmitter against that
  (`feasibility/EMCON.md` section 0a, sixth revision), the kit has 17 transmitters and **none is dark end to end, at
  desk or on a bench**:
  - Locally, the radio's own chain closes at desk for 14 of the 17 and is open for three. The SA868 VHF exciter: its
    maker publishes no receive threshold for the PTT pin the design holds at 2.677 V or more (bench E-01). The RockBLOCK
    9704: once its supply is cut it keeps running on its own supercapacitors, about 16 J, with its ENABLE held by a
    firmware-driven expander, so the ENABLE forced low by the EMCON hardware is owed, and what the Iridium module does
    when ENABLE falls is stated in no held document (section 4.4). The 5G module: its staged supply removal (SD-EMC-1,
    open item S-01) is not drawn.
  - End to end, 0 of 17 rows is closed: every row also waits on the items the rows share, the toggle and its conductor
    (accepted by SD-EMC-6 only with a hardware EMCON lamp on board C, which is not drawn) and the EMCON line's own open
    items (sections 3 and 7), and no row is shown to meet the latency.

  No row has been shown on a bench; EMCON is feasibility blocker FEA-002 of the requirements registry. As drawn, no
  panel indication of EMCON is independent of firmware: the TX lamp's supply exists only while the panel controller
  drives its LED dimmer (`feasibility/EMCON.md` section 0; `PANEL.md` section 3, GPIO 8). Blackout and NVG panel modes
  darken the kit.""",
    """  DCF77 and the lightning sensor continue. As generated at `45bde541` the line is drawn to remove the supply of the
  SDR, the RockBLOCK, the LoRa module, both Zigbee and Thread radios, the HF unit and both WiFi link cards, to turn off
  the PA's rail and keying while the VHF exciter keeps receiving, to pull the compute modules' own WiFi and Bluetooth
  disables low, and to put the 5G module in airplane mode through its disable pin, a mode its own firmware carries out;
  since board B's round 8 (27 September 2026) it also removes the 5G module's supply by hardware at once (SD-EMC-1r8,
  `feasibility/EMCON.md` section 4b; `CONOPS.md` section 4b). The session set the latency every inhibit must meet: at
  most 1 s from the toggle for every transmitter, and 20 s for a 5G module that is running, by paths no processor or
  radio firmware can lengthen (SD-EMC-7, requirement REQ-071, `feasibility/EMCON.md` section 5a). Read transmitter by
  transmitter against that (`feasibility/EMCON.md` section 0a, sixth revision, with board B's round 8), the kit has 17
  transmitters and **none is dark end to end, at desk or on a bench**:
  - Locally, the radio's own chain closes at desk for 15 of the 17 and is open for two. The SA868 VHF exciter: its
    maker publishes no receive threshold for the PTT pin the design holds at 2.677 V or more (bench E-01). The RockBLOCK
    9704: once its supply is cut it keeps running on its own supercapacitors, about 16 J, with its ENABLE held by a
    firmware-driven expander, so the ENABLE forced low by the EMCON hardware is owed, and what the Iridium module does
    when ENABLE falls is stated in no held document (section 4.4). The 5G module's chain closes at desk since board B's
    round 8: its supply is removed at once, with RF off within about 1.2 ms plus 1.8 ms per mF of the module's own input
    capacitance, which no held document states (bench E-12), and the maker's warning that cutting a working module's
    supply can corrupt its flash accepted as a residual (section 4b).
  - End to end, 0 of 17 rows is closed: every row also waits on the items the rows share, the toggle and its conductor
    (accepted by SD-EMC-6 only with a hardware EMCON lamp on board C, drawn since board C's round 8 as `D22` with no
    processor in its path, and not yet visible, because its light-guide hole in the face plate is owed, open item
    S-44) and the EMCON line's own open items (sections 3 and 7), and no row is shown to meet the latency.

  No row has been shown on a bench; EMCON is feasibility blocker FEA-002 of the requirements registry. The one panel
  indication of EMCON that is independent of firmware is that lamp, lit while both EMCON lines read low, fed ahead of
  the panel's dimmer and dark in BLACKOUT (`PANEL.md` sections 1 and 4); the TX lamp's supply exists only while the
  panel controller drives its LED dimmer (`feasibility/EMCON.md` section 0; `PANEL.md` section 3, GPIO 8). Blackout and
  NVG panel modes darken the kit.""")
rep(B, """The generators and the committed
  boards still carry the earlier eleven couplers at 88 mm, which is history.""",
    """The case generators carry C1 to C6
  since `c351115d`, and the current case set (CAD, drawings and 1:1 templates) is `v2/release/case-2026-09-27/`; the
  committed board files and the deliverable folders of `v2/release/revA/` predate it and still carry the earlier
  eleven coupler sites at 88 mm, which is history.""")
rep(B, """`CONOPS.md` sections 4a and 6 still carry the earlier
  model's 3.4 h and 1.8 h, which PWR-F07 supersedes. None of these is a claim.
""",
    """`CONOPS.md` sections 4a and 6 carry the same
  PWR-F07 figures since the layer 2 merge (`95e078a1`). None of these is a claim.
- Not able to run through a night on its own pack and solar input. On the one pack of D-06 and the solar input alone
  the kit does not run through a night at 52 N in any state: the aged pack holds about 108 Wh usable, which carries
  the idle state of the runtime requirement (42.8 W) for about 2.5 h against nights of about 7 hours at midsummer and
  about 16 at midwinter, and the shortest night in the lightest state asks about 150 Wh; and the 72 hours of mission
  M1 ask for a panel of about 266 W on the design day, where the solar input takes at most about 100 W (`CONOPS.md`
  M1; requirement REQ-072, part of prototype 1's core, reads FAIL at desk; the figures are PROVISIONAL or INFERRED
  there). The routes that carry the night are an overnight input on the 9 to 36 V vehicle and shore entry, D-01's
  deferred second pack, or a larger pack, which reopens D-06; until the owner rules on the last two, running through
  a night needs that overnight input.
""")
rep(B, """two could change a stated line,
FEA-004 an envelope line and FEA-002 the latency the session set, and their rows say how that is handled.""",
    """three could change a stated line,
FEA-004 an envelope line, FEA-002 the latency the session set and REQ-072 the pack line, and their rows say how that is handled.""")
rep(B, """| FEA-002 EMCON: 0 of 17 transmitters dark end to end; locally 14 of 17 closed at desk and three open, the SA868 (PTT threshold unpublished), the RockBLOCK 9704 (its own stored energy, about 16 J, and an ENABLE firmware holds) and the 5G module (SD-EMC-1 not drawn); the shared items; no panel indication independent of firmware; no bench row |""",
    """| FEA-002 EMCON: 0 of 17 transmitters dark end to end; locally 15 of 17 closed at desk and two open, the SA868 (PTT threshold unpublished) and the RockBLOCK 9704 (its own stored energy, about 16 J, and an ENABLE firmware holds); the 5G module's supply removed by hardware at once since board B's round 8 (SD-EMC-1r8); the shared items, with the hardware EMCON lamp `D22` drawn on board C and its light guide in the face plate owed (S-44); no bench row |""")
rep(B, """| REQ-014's runtime values, measured on the prototype; L-02, the mission duration for the solar balance, which the owner sets later (D-06) | "What it is not, today"; `CONOPS.md` section 6 | The requirement's form is ruled; the values are prototype measurements, and missions longer than the pack are stated to rely on vehicle or solar input. |""",
    """| REQ-014's runtime values, measured on the prototype; L-02, the mission duration for the solar balance, which D-06 left for the owner to set later and for which the session took 72 hours as a planning value under the owner's standing rule (SC-21, which the requirements registry records as closing L-02 and which the owner's own setting replaces; whether the standing rule reaches a value D-06 kept for the owner is recorded as open in `handover/LAYER-STATUS.md`, layer 3) | "What it is not, today"; `CONOPS.md` sections 3 (M1) and 6 | The requirement's form is ruled; the values are prototype measurements, and missions longer than the pack are stated to rely on vehicle or solar input, with the night finding in the next row. |
| REQ-072, M1's energy balance (core, FAIL at desk): on the D-06 pack and the solar input alone the kit does not run through a night at 52 N in any state, and M1's 72 hours ask about 266 W of panel where the solar input takes at most about 100 W | "What it is not, today"; `CONOPS.md` section 3 (M1); registry REQ-072, SC-21 and S-53 | The finding is allocated to layer 4 (the energy architecture: whether the input path is re-rated, S-53, before boards A, E and P enter layout) and to the owner (a larger pack reopens D-06; the second pack is D-01's deferred item). The kit's purpose, its users and the core list stand under either outcome, nothing is claimed, and this brief states the overnight input a night needs today. If the owner reopens D-06 or D-01's second pack, the pack line of "What the V2 kit is" changes and this brief is issued again. |""")

# ---------------------------------------------------------------- layer 1: V2-SPEC.md (lines 1 to 116 keep their numbers)
S = "v2/docs/V2-SPEC.md"
rep(S, """As generated, and in the committed boards and templates, they are still the eleven Amphenol 132170 SMA couplers at Z 88 of 32.56 (west VHF, HF, WIFI 2.4, GNSS, SDR; east 5G MAIN, 5G DIV, IRIDIUM, LORA, WIFI P2P A, WIFI P2P B), which is history until `panel1450.py` and `case_wall_cutouts.py` carry C2;""",
    """The case generators `panel1450.py` and `case_wall_cutouts.py` carry them since `c351115d`, and the current case set is `release/case-2026-09-27/` (correction 30); the committed boards and the templates of `release/revA/case/` still show the eleven Amphenol 132170 SMA couplers at Z 88 of 32.56 (west VHF, HF, WIFI 2.4, GNSS, SDR; east 5G MAIN, 5G DIV, IRIDIUM, LORA, WIFI P2P A, WIFI P2P B), which is history;""")
rep(S, """`CONOPS.md` sections 4a and 6 still carry the earlier model's 32.4 W, 3.4 h aged and 60.1 W, 1.8 h aged, which PWR-F07 supersedes.""",
    """`CONOPS.md` sections 4a and 6 carry the same PWR-F07 figures since the layer 2 merge (correction 30).""")
rep(S, """accepted by SD-EMC-6 only with a hardware EMCON lamp on board C that is not drawn,""",
    """accepted by SD-EMC-6 only with a hardware EMCON lamp on board C, drawn since board C's round 8 (`D22`, no processor in its path) with its light guide in the face plate owed (open item S-44),""")
rep(S, """(`CONOPS.md` section 4b; corrections 4, 19, 26 and 28)""",
    """(`CONOPS.md` section 4b; corrections 4, 19, 26, 28 and 30)""")
rep(S, """| Indicators | sixteen LEDs through IP68 light guides, the Floyd Bell sounder; blackout and NVG modes |""",
    """| Indicators | sixteen LEDs through IP68 light guides and, since board C's round 8, a seventeenth, the amber hardware EMCON lamp lit from the EMCON lines with no processor in its path, whose light guide in the plate is owed (open item S-44; correction 30); the Floyd Bell sounder; blackout and NVG modes |""")
rep(S, """the hardware EMCON lamp on board C (SD-EMC-6)""",
    """the hardware EMCON lamp's light guide in the face plate (SD-EMC-6; the lamp is drawn on board C since its round 8, correction 30)""")
rep(S, """The generators (`panel1450.py`, `case_wall_cutouts.py`) and the templates of
    `release/revA/case/` still carry the eleven couplers at Z 88 and the plate between the ribs.""",
    """The generators (`panel1450.py`, `case_wall_cutouts.py`) and the templates of
    `release/revA/case/` still carried the eleven couplers at Z 88 and the plate between the ribs until `c351115d`
    (correction 30).""")
rep(S, """    points of failure of the kit as generated: the `+5V_DEV` and `+3V3_DEV` converters on board A (one each), the
    `J_PANEL` ribbon, the KSZ9897R Ethernet switch, and the kit I2C bus with the panel controller as its one master.
    None is claimed as covered, none is a risk the owner accepted, and whether each is mitigated is layer 4 work (open
    item S-36). The kit is never described as having no single point of failure.""",
    """    points of failure of the kit as generated: the `+5V_DEV` and `+3V3_DEV` converters on board A (one each), the
    `J_PANEL` ribbon, the KSZ9897R Ethernet switch, and the kit I2C bus with the panel controller as its one master.
    None is claimed as covered, none is a risk the owner accepted, and whether each is mitigated is layer 4 work (open
    item S-36). The kit is never described as having no single point of failure.
30. **The layer 1 release check (lines 10, 23, 24, 59 and 76; correction 20's last sentence).** Session reading after
    the release check of layer 1 at `f2b7fa66` (`reviews/REVIEW-LAYER-1-RELEASE-2026-09-27.md`, an AI review, findings
    B1 to B3), 27 September 2026. Since `c351115d` the case generators carry the case choices C1 to C6:
    `panel1450.py` (the plate 377.2 x 263.0 x 3.0 on ten 6-32 UNC; the twelve PolyPhaser GTH-SFF-AL at Z 59),
    `case_wall_cutouts.py` and `v2/cad/face_plate.py`, and the current case set (CAD, dimensioned drawings, 1:1
    templates and the QMX lid tray) is `release/case-2026-09-27/`; `release/revA/case/` is marked historical and is not
    to be made from. The committed board files and the deliverable folders of `release/revA/boards/` predate C1 to C6.
    Board C's round 8 draws the hardware EMCON lamp of SD-EMC-6 (`D22` through `U14` and `Q7`, lit while both EMCON
    lines read low, with no processor in its path); its light-guide hole in the face plate is owed (open item S-44), and
    until it is cut the lamp cannot be seen. Line 23's cross-reference is corrected: `CONOPS.md` sections 4a and 6 carry
    PWR-F07's figures (42.8 W and 63.0 W at the pack terminals; 2.5 h and 1.7 h aged) since the layer 2 merge. Nothing
    is built.""")

# ---------------------------------------------------------------- layer 1: README.md
R = "README.md"
rep(R, """; the generators and case templates still carry the eleven couplers at 88 mm, which is history.""",
    """; the case generators carry them since `c351115d` and the current case set, CAD, drawings and 1:1 templates, is [`v2/release/case-2026-09-27/`](v2/release/case-2026-09-27/README.md), while the committed board files and the deliverable folders of `v2/release/revA/` predate it.""")
rep(R, """the sixteen LEDs under IP68 light guides,""",
    """the sixteen LEDs under IP68 light guides (and, in the schematic since its round 8, a seventeenth, the hardware EMCON lamp, whose light guide in the plate is owed),""")

# ---------------------------------------------------------------- layer 1: v2/README.md
V = "v2/README.md"
rep(V, """(`cad/face_plate.py`, `release/revA/case/face-plate/`; the session's case choice C1 of `docs/CASE-MARGINS.md` section 4, which the generated plate does not carry yet)""",
    """(`cad/face_plate.py`, `release/case-2026-09-27/face-plate/`; the session's case choice C1 of `docs/CASE-MARGINS.md` section 4, which the case generators carry since `c351115d`)""")
rep(V, """(case choices C2 and C4; the generators and templates still carry eleven couplers at 88 mm, which is history)""",
    """(case choices C2 and C4, carried by the case generators and the case set `release/case-2026-09-27/` since `c351115d`; the committed board files and the deliverable folders of `release/revA/` predate them)""")
rep(V, """and to put the 5G module in airplane mode through its disable pin, a mode its own firmware carries out (`docs/CONOPS.md` section 4b), and read transmitter by transmitter (`docs/feasibility/EMCON.md` section 0a) none of the kit's 17 transmitters is dark end to end: the radio's own chain closes at desk for 14 and is open for the SA868 (its PTT pin's receive threshold is unpublished), the RockBLOCK 9704 (once its supply is cut it runs on its own supercapacitors with its ENABLE held by firmware, so the ENABLE forced low by the EMCON hardware is owed) and the 5G module (its staged supply removal, SD-EMC-1, is owed); every row also waits on the items the rows share and on the latency the session set""",
    """and to put the 5G module in airplane mode through its disable pin, and since board B's round 8 (27 September 2026) it also removes the 5G module's supply by hardware at once (SD-EMC-1r8; `docs/CONOPS.md` section 4b, `docs/feasibility/EMCON.md` section 4b); read transmitter by transmitter (`docs/feasibility/EMCON.md` section 0a) none of the kit's 17 transmitters is dark end to end: the radio's own chain closes at desk for 15 and is open for the SA868 (its PTT pin's receive threshold is unpublished) and the RockBLOCK 9704 (once its supply is cut it runs on its own supercapacitors with its ENABLE held by firmware, so the ENABLE forced low by the EMCON hardware is owed); every row also waits on the items the rows share (the toggle and its conductor, whose hardware EMCON lamp is drawn on board C since its round 8 with its light guide in the plate owed) and on the latency the session set""")
rep(V, """As generated, the face plate (365.5 x 249.5 x 3, ten M3 at the frame's inserts) sits with its top 101.4 mm above the cavity floor, the backer ring 10 mm under it; by the session's case choices C1 and C6 (`docs/CASE-MARGINS.md` section 4) the plate becomes 377.2 x 263.0 x 3.0 on top of the frame over Peli's o-ring, on ten 6-32 screws into Peli's inserts, with the frame on four setting legs and the face top at 106.52 mm, which the generators do not carry yet; and the stack tops out""",
    """By the session's case choices C1 and C6 (`docs/CASE-MARGINS.md` section 4), which the case generators carry since `c351115d`, the face plate is 377.2 x 263.0 x 3.0 on top of the frame over Peli's o-ring, on ten 6-32 screws into Peli's inserts, with the frame on four setting legs and the face top at 106.52 mm (the 7 September generation's plate was 365.5 x 249.5 x 3 on ten M3 at the frame's inserts, its top 101.4 mm above the cavity floor, the backer ring 10 mm under it); and the stack tops out""")
rep(V, """the QMX HF unit rides in a printed tray on the lid's inner face (`release/revA/case/lid-bracket-qmx/`)""",
    """the QMX HF unit rides in a printed tray on the lid's inner face (`release/case-2026-09-27/lid-tray-qmx/`, sheet 14 of its drawings, to be revised against the unit's jacks before it is printed, open item S-63)""")
rep(V, """the eleven couplers sit in the end walls at 88 mm as generated (`ecad/tools/panel1450.py` is the single source of every face and wall position) and are to become twelve arrestors at 59 mm on two RF entry plates (C2, C4), and the connector plate, generated upright between the back-wall ribs, is to be one plate between the hinge fairings outside the back wall (C3). The templates are in `release/revA/case/`;""",
    """twelve arrestors at 59 mm on two RF entry plates are the antenna bulkheads (C2, C4; `ecad/tools/panel1450.py` is the single source of every face and wall position), and one connector plate between the hinge fairings outside the back wall carries the wall items (C3). The current case set, CAD, drawings and 1:1 templates, is `release/case-2026-09-27/`; `release/revA/case/` is the superseded 7 September set, kept as history and not to be made from;""")

# ---------------------------------------------------------------- layer 1: v2/BUILD.md
U = "v2/BUILD.md"
rep(U, """the radio's own chain closes at desk for 14 of the 17 and is open for the SA868, whose PTT threshold is unpublished, the RockBLOCK 9704, which runs on its own supercapacitors with its ENABLE held by firmware once its supply is cut, and the 5G module, which the line only puts in airplane mode through a firmware-mediated pin until its supply removal SD-EMC-1 is drawn;""",
    """the radio's own chain closes at desk for 15 of the 17 and is open for the SA868, whose PTT threshold is unpublished, and the RockBLOCK 9704, which runs on its own supercapacitors with its ENABLE held by firmware once its supply is cut, the 5G module's supply being removed by hardware at once since board B's round 8 (SD-EMC-1r8);""")
rep(U, """the face itself is the aluminium plate of `release/revA/case/face-plate/`""",
    """the face itself is the aluminium plate of `release/case-2026-09-27/face-plate/` (case choice C1)""")
rep(U, """the plate becomes 377.2 x 263.0 x 3.0 mm with a rebated band, which the plate generator does not carry yet. The face plate is a CNC part from the DXF and STEP in `release/revA/case/face-plate/`""",
    """the plate is 377.2 x 263.0 x 3.0 mm with a rebated band, which the plate generator carries since `c351115d`. The face plate is a CNC part from the DXF and STEP in `release/case-2026-09-27/face-plate/`""")
rep(U, """the sixteen LEDs need sixteen Mentor 1282.5004 light guides,""",
    """the sixteen LEDs need sixteen Mentor 1282.5004 light guides (and the hardware EMCON lamp of board C's round 8 a seventeenth once its hole is in the plate, open item S-44),""")
rep(U, """The QMX lid tray is printed from `release/revA/case/lid-bracket-qmx/` (PETG, about 32 g)""",
    """The QMX lid tray is printed from `release/case-2026-09-27/lid-tray-qmx/` (sheet 14; PETG, about 32 g) once it is revised against the unit's jacks on both end panels (open item S-63)""")
rep(U, """The generators and templates (`tools/panel1450.py`, `tools/case_wall_cutouts.py`, `release/revA/case/wall-receptacles-1to1.pdf`) still carry the 7 September layout: eleven Amphenol Connex 132170 couplers in 6.5 mm D-holes at Z 88 and a 54 x 82 plate between the ribs.""",
    """The case generators (`tools/panel1450.py`, `tools/case_wall_cutouts.py`) carry this layout since `c351115d`, with its templates in `release/case-2026-09-27/templates/`; `release/revA/case/wall-receptacles-1to1.pdf` is the superseded 7 September layout (eleven Amphenol Connex 132170 couplers in 6.5 mm D-holes at Z 88 and a 54 x 82 plate between the ribs), kept as history.""")
rep(U, """(`release/revA/case/face-plate/` drawing, to be regenerated for C1)""",
    """(`release/case-2026-09-27/drawings/`, sheet 1 the face plate and sheet 2 the frame and legs)""")
rep(U, """The 1:1 templates of `release/revA/case/` (sheets 3 and 4) still show the eleven 6.5 mm D-holes at Z 88 until `case_wall_cutouts.py` carries C2.""",
    """The east and west wall templates are in `release/case-2026-09-27/templates/case-templates-1to1.pdf`, from `case_wall_cutouts.py`, which carries C2 since `c351115d`; sheets 3 and 4 of `release/revA/case/` show the superseded eleven 6.5 mm D-holes at Z 88.""")
rep(U, """Sheet 1 still shows the 7 September window between the ribs at X -95 and -18.""",
    """The back-wall template is in the same file; sheet 1 of `release/revA/case/` shows the superseded window between the ribs at X -95 and -18.""")

# ---------------------------------------------------------------- layer 2: CONOPS.md (line count kept)
C = "v2/docs/CONOPS.md"
rep(C, """in the documents; the layer is then marked baselined at that commit. The first pass was recorded
(`reviews/REVIEW-A-LAYER-2-2026-09-27.md`: FAIL, seven blocking findings, read on `e3aedb25` with this revision's first
draft) and pass 2 answered it; the second pass (the same record, FAIL, two blocking findings, P2-B1 and P2-B2) is
answered by pass 3, and a pass at the integrating commit decides the baseline. Until a pass""",
    """in the documents; the layer is then marked baselined at that commit. The first pass was recorded (FAIL, seven blocking
findings, read on `e3aedb25` with this revision's first draft; filed at `reviews/REVIEW-A-LAYER-2-2026-09-27-pass1.md`, sha256 `e854c2a46ea3d542`, with the reviewers' brief at `reviews/2026-09-27-review-A-layer2-brief.md`)
and pass 2 answered it; the second pass (`reviews/REVIEW-A-LAYER-2-2026-09-27.md`, FAIL, two blocking findings, P2-B1 and P2-B2) is answered by pass 3; the pass at the integrating
commit `f2b7fa66` (`reviews/REVIEW-LAYER-2-RELEASE-2026-09-27.md`, FAIL, four blocking findings, B1 to B4) is answered in part at desk (`handover/LAYER-STATUS.md`, layer 2), and a later pass decides the baseline. Until a pass""")
rep(C, """software (NEED-08): 1 s for every radio but the 5G module; for a 5G module that has been turned on, 20 s set by
hardware timers at their worst tolerance, with its disable pin pulled at once; 0 at power-up under EMCON (section""",
    """software (NEED-08): 1 s for every radio but the 5G module; for a 5G module that has been turned on, 20 s (REQ-071), where
since board B's round 8 the design removes its supply by hardware at once, RF off within about 1.2 ms plus 1.8 ms per mF of the module's input capacitance (TBD, bench E-12), a local reading and not an end-to-end one; 0 at power-up under EMCON (section""")
rep(C, """`feasibility/POWER-THERMAL.md` section 9.3 | the definition is the session's""",
    """`feasibility/POWER-THERMAL.md` section 9.3, `ARCHITECTURE.md`'s PS-RED row and `HW-FW-CONTRACT.md` FW-C09, which still take the reduced mode as one module and follow this row (hand-offs, section 4c) | the definition is the session's""")
rep(C, """(its working files are not filed in this tree at `e3aedb25`; the records stream files them under
`v2/docs/records/`, and the finding is carried by""",
    """(its working files are filed at `v2/docs/records/adj/A06-pack-geometry/`,
and the finding is carried by""")
rep(C, """| RM520N-GL 5G | **20 s** for a module that has been turned on, set by hardware timers at their worst tolerance (SD-EMC-1's staged supply removal, owed on board B); **0** at power-up under EMCON (its rail never rises); its W_DISABLE1# pulled within 1 s, which is firmware-mediated and not counted |""",
    """| RM520N-GL 5G | **20 s** for a module that has been turned on (REQ-071); **0** at power-up under EMCON (its rail never rises). Since board B's round 8 the design removes its supply by hardware at once, RF off within about 1.2 ms plus 1.8 ms per mF of the module's own input capacitance, which no held document states (bench E-12), the maker's flash warning accepted (SD-EMC-1r8, `feasibility/EMCON.md` section 4b); its W_DISABLE1# is pulled low at the same moment by `U215`, an airplane mode the module's firmware carries out, not counted |""")
rep(C, """element every row shares (the toggle's contact, the `TX_INHIBIT_n` conductor), which the hardware EMCON lamp shows
without firmware once it is drawn on board C (CON-021, S-44).""",
    """element every row shares (the toggle's contact, the `TX_INHIBIT_n` conductor), which the hardware EMCON lamp `D22` shows
without firmware; the lamp is drawn on board C since its round 8, and its light guide in the face plate is owed (CON-021, S-44).""")
rep(C, """before silence is needed while the 5G module is running, or has the 5G module turned off first (INFERRED from the 5G
row's L_max). After setting EMCON""",
    """before silence is needed while the 5G module is running, or has the 5G module turned off first: 20 s is REQ-071's bound for the 5G
row, kept as the operator's lead until bench E-12 measures the drawn circuit's time to RF off. After setting EMCON""")
rep(C, """SD-EMC-6, the procedure lines it owes); until the lamp is drawn no indicator shows the line's state without the panel
controller. **State at `e3aedb25`:** this is a requirement on the design, and no row meets it at desk yet
(`feasibility/EMCON.md` sections 0a and 5a: rows 1, 4 and 5 are open locally and every row inherits the shared items of
its section 3); the registry text for REQ-030 is drafted in its section 8. NEED-08 is not met until the design closes""",
    """SD-EMC-6, the procedure lines it owes); until its light guide is in the plate the lamp cannot be seen, and no indicator the operator can see shows the line's state without the panel
controller. **State at this revision:** this is a requirement on the design (REQ-071), and no row meets it end to end at desk yet
(`feasibility/EMCON.md` sections 0a and 5a: locally 15 of the 17 rows close at desk, rows 1 and 4, the SA868 and the RockBLOCK 9704, are open, and every row inherits the shared items of
its section 3, so 0 of 17 close end to end). NEED-08 is not met until the design closes""")
rep(C, """`feasibility/POWER-THERMAL.md` (sections 1 and 9.3) and `ARCHITECTURE.md` took the reduced mode as slot 3 alone, which""",
    """`feasibility/POWER-THERMAL.md` (sections 1 and 9.3), `ARCHITECTURE.md` (its PS-RED row) and `HW-FW-CONTRACT.md` (FW-C09, C1 as a shed to one module) took the reduced mode as one module (slot 3 alone in the first two), which""")
rep(C, """cannot change that; the hub port each device hangs on can, which is BANK-R1 below.""",
    """cannot change that; the hub port each device hangs on can, which is BANK-R1 below. Those three documents follow this section; their correction is a hand-off to their writers (`records/hc2/handoffs.md` sections 4 and 5; `handover/LAYER-STATUS.md`, layers 4 and 5).""")
rep(C, """held (airplane mode now; supply removal owed, section 4b.1)""",
    """held (dark: its supply removed by hardware at once since board B's round 8, section 4b)""")

# ---------------------------------------------------------------- layer 2: OPERATING-ENVELOPE.md (line count kept)
O = "v2/docs/OPERATING-ENVELOPE.md"
rep(O, """(adjudication A06 of 25 September 2026, whose working files the records stream is to file under `v2/docs/records/`;""",
    """(adjudication A06 of 25 September 2026, whose working files are filed at `v2/docs/records/adj/A06-pack-geometry/`;""")
rep(O, """hardware; and it puts the 5G module in airplane mode through its disable pin, a mode the module's firmware carries out
""",
    """hardware; and it puts the 5G module in airplane mode through its disable pin, a mode the module's firmware carries out; since board B's round 8 (27 September 2026) it also removes the 5G module's supply by hardware at once (SD-EMC-1r8, `feasibility/EMCON.md` section 4b)
""")
rep(O, """is session engineering: the 5G module's supply removal and the items every row of the line shares
(`feasibility/EMCON.md` sections 5 and 7).""",
    """is session engineering: the items every row of the line shares, the SA868's PTT threshold and the RockBLOCK 9704's ENABLE, the 5G module's supply removal being drawn since board B's round 8
(`feasibility/EMCON.md` sections 0a, 5 and 7).""")

# ---------------------------------------------------------------- layer 2: TEST-PLAN.md (line count kept)
T = "v2/docs/TEST-PLAN.md"
rep(T, """EMCON with its latency per row and the EMCON lamp once it is drawn, REQ-030, REQ-031, REQ-032""",
    """EMCON with its latency per row and the hardware EMCON lamp `D22`, REQ-030, REQ-031, REQ-032, REQ-071""")

# ---------------------------------------------------------------- layer 2: PANEL.md (line count kept)
P = "v2/docs/PANEL.md"
rep(P, """a seventeenth, the hardware EMCON lamp `D22` (amber) on `Q7`, which no expander and no firmware drives (section 6)""",
    """a seventeenth LED on the face, the hardware EMCON lamp `D22` (amber) on `Q7`, which no expander and no firmware drives (sections 4 and 6; its light guide in the plate is owed, S-44; section 9's seventeen controller-lit indicators are a different count, which leaves `D22` out)""")
rep(P, """reconciled 27 September 2026, S-39: the "17" was right and section 1's sixteen counts the `D` references only; the hardware EMCON lamp of S-44 is lit by the lamp test only if its circuit is given a test tie, an item for its author)""",
    """reconciled 27 September 2026, S-39: the "17" was right; section 1 counts the face's LEDs, `D1` to `D16` and, since round 8, the hardware EMCON lamp `D22`, which is not among these seventeen: as drawn no expander and no test tie reaches it, so the lamp test cannot light it and setting EMCON is its test, section 4)""")

# ---------------------------------------------------------------- layer 2 B4 (d): CONTINUATION-BRIEF.md section 8
K = "v2/docs/handover/CONTINUATION-BRIEF.md"
MARK = "**Superseded after H1.1 (the release check of 27 September 2026):** "
rep(K, """carry 3.4 h and 1.8 h | edit owed |""",
    """carry 3.4 h and 1.8 h | """ + MARK + """CONOPS sections 4a and 6 carry PWR-F07's figures since the layer 2 merge (`95e078a1`), and V2-SPEC line 23 says so (correction 30) |""")
rep(K, """(10 K and 16 K; stated as design) | edit owed; the numbers wait on EQ-05 |""",
    """(10 K and 16 K; stated as design) | """ + MARK + """OPERATING-ENVELOPE sections 3 and 4 and `pcb_envelope.yaml` carry the per-state bounds and the restrictions as controls on measured temperatures since the layer 2 merge (`95e078a1`), V2-SPEC line 73 since correction 23; the numbers still wait on EQ-05 |""")
rep(K, """ASSEMBLY section "4. Leads" (eleven couplers at Z 88); GROUNDING-AND-SHIELDS section "What the kit is made of, which is what makes this decision what it is" (nine) | edit and regeneration owed |""",
    """ASSEMBLY section "4. Leads" (eleven couplers at Z 88); GROUNDING-AND-SHIELDS section "What the kit is made of, which is what makes this decision what it is" (nine) | """ + MARK + """`panel1450.py`, `case_wall_cutouts.py` and the case set `v2/release/case-2026-09-27/` carry C2 since `c351115d`, ASSEMBLY section 4 since the same commit, and both READMEs, V2-SPEC and `v2/BUILD.md` since the release check; the committed board files and the revA deliverable folders predate it |""")
rep(K, """REQ-047 ("ten M3"), `case_wall_cutouts.py` | CAD owed |""",
    """REQ-047 ("ten M3"), `case_wall_cutouts.py` | """ + MARK + """`panel1450.py`, `v2/cad/face_plate.py`, `case_wall_cutouts.py`, ASSEMBLY and REQ-047 (6-32) carry C1 and C3 since `c351115d`, with the made parts in `v2/release/case-2026-09-27/` |""")
rep(K, """| Storage with or without the pack | open (CFL-017): CONOPS section "4. Operating modes" and TEST-PLAN section "1. Test articles and conditions" (pack out) against REQ-025 and OPERATING-ENVELOPE section "4. The envelope this proposes" (pack fitted) | | a product decision from the need (layer 2) |""",
    """| Storage with or without the pack | open (CFL-017): CONOPS section "4. Operating modes" and TEST-PLAN section "1. Test articles and conditions" (pack out) against REQ-025 and OPERATING-ENVELOPE section "4. The envelope this proposes" (pack fitted) | | """ + MARK + """stored and carried with the pack fitted in the gauge's shutdown, session choice SC-19 (CONOPS section 4's Storage and Transport rows, TEST-PLAN section 1, `95e078a1`); CFL-017 stays open as BAT-F19, the margins with the pack fitted (layer 4 and the owner) |""")
rep(K, """PRODUCT-BRIEF section "What the V2 kit is" ("wrong key") | edit owed |""",
    """PRODUCT-BRIEF section "What the V2 kit is" ("wrong key") | """ + MARK + """the land carries the two locating holes since board B's round 8 (`b76c18cb`, V2-SPEC correction 28), and the brief says so since the release check |""")
rep(K, """PRODUCT-BRIEF section "What the V2 kit is", `v2/README.md` section "V2: the Peli 1450 carrier set (MESHSAT-830 generation)" | edit owed |""",
    """PRODUCT-BRIEF section "What the V2 kit is", `v2/README.md` section "V2: the Peli 1450 carrier set (MESHSAT-830 generation)" | """ + MARK + """board B's round 8 removes the 5G module's supply by hardware at once (SD-EMC-1r8, `b76c18cb`): `feasibility/EMCON.md` section 0a reads 15 of 17 closed locally at desk and 0 of 17 end to end; the brief, both READMEs, `v2/BUILD.md`, V2-SPEC, CONOPS (4b, 4b.1, 4f, M4) and OPERATING-ENVELOPE section 4 say so since the release check |""")
rep(K, """PANEL section "9. Indicator semantics, controls and the e-paper" | decision owed |""",
    """PANEL section "9. Indicator semantics, controls and the e-paper" | """ + MARK + """S-39 closed by SC-30; board C's round 8 draws the hardware EMCON lamp `D22`, so PANEL section 1 counts seventeen LEDs on the face and section 9's lamp test seventeen controller-lit indicators, which leave `D22` out and add the PI ring; V2-SPEC line 59 since correction 30 |""")


def main():
    files = {}
    for path, old, new in E:
        if path not in files:
            files[path] = open(path, encoding="utf-8").read()
        t = files[path]
        n = t.count(old)
        assert n == 1, "%s: old text found %d times: %r" % (path, n, old[:90])
        assert old != new, "%s: no change: %r" % (path, old[:90])
        t2 = t.replace(old, new)
        if path in KEEP:
            assert t2.count("\n") == t.count("\n"), "%s: line count changed at %r" % (path, old[:90])
        files[path] = t2
    for path, t in files.items():
        old = open(path, encoding="utf-8").read()
        if path == "v2/docs/V2-SPEC.md":
            # lines 1 to 116 keep their numbers: every heading and table row starts where it did
            ol, nl = old.split("\n"), t.split("\n")
            for i in range(116):
                assert (ol[i][:1] == nl[i][:1]), "V2-SPEC line %d moved" % (i + 1)
            assert ol[116:118] == nl[116:118], "V2-SPEC lines 117 and 118 moved"
        print("%-45s %4d -> %4d lines%s" % (path, old.count("\n"), t.count("\n"), "" if WRITE else " (dry run)"))
        if WRITE:
            open(path, "w", encoding="utf-8").write(t)
    print("edit_release_fixes: %d replacements in %d files" % (len(E), len(files)))


main()
