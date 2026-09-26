# The operating envelope, ADOPTED 21 September 2026

**Status: ADOPTED. Owner decision 34 was ruled by the session on 21 September 2026**, under the owner's
instruction of that evening that an agentic system takes informed engineering decisions on his behalf rather
than queueing them to a non-engineer. What is adopted is **section 4 as the design envelope** and **section
6's first row, IEC 61000-4-2 level 4 (8 kV contact, 15 kV air), as the transient level**; the electrical fast
transient row is recorded as NOT A REQUIREMENT of this project, because nothing in this tree is a source for
one. The altitude, the vibration and shock severities and the service life stayed OPEN that day, for the rules
that genuinely need them, and were not invented here; since 25 and 26 September 2026 the altitude, the
severities, the cold start and direct sun are the owner's rulings and the service life is TBD for prototype 1
(section 8). Reverse by reopening decision 34, which returns this document to a draft.

**What is NOT taken here and stays the owner's:** ADVERTISING the kit to this envelope. That is a claim about
the product and belongs with the public copy, not with the engineering.

**Owner rulings of 25 and 26 September 2026 (section 8).** Seven questions of the foundation re-baseline
(MESHSAT-1357) that bear on this envelope were asked one at a time, each with its options and a
recommendation, and the owner ruled each at the recommendation: `TEST-PLAN.md`'s +55 C operation, +71 C storage
and -33 C storage are QUALIFICATION MARGINS over this envelope, not limits of it (D-02a, 25 September); the kit
operates with its lid closed in a defined REDUCED MODE (D-02b, 25 September); the shock and vibration severities
are `TEST-PLAN.md` E1 and E2, and the altitude is 0 to 3000 m in use and 0 to 4500 m in transport (D-02c, 26
September); a cold start from the pack below about -10 C cell temperature is OUT OF SCOPE (D-02d); the kit is
operated SHADED (D-02e); the vehicle entry is NOT QUALIFIED for vehicle surge (D-16); and the prototype makes no
EMC claim, so its planned MIL-STD-461 runs are characterisation (D-04). No envelope question is open any more; the
service life is TBD for prototype 1, and the pollution degree and the duty cycle are still owed (section 5).

The sentences below were written while it was a draft and stand as they were, because the numbers are the
parts' own and the ruling changed none of them.

This is the envelope the parts'
own datasheets and the owner's rulings already imply, written down for the first time so that the rules
that depend on it have something to resolve against. Nothing in this project has been built or powered,
so every number here is a design intent taken from documents, and the three that are measurements owed
say so in the line where they appear.

Rule **ENV-001** of `tools/pcb_rules.yaml` asks for exactly this document, and it is a BLOCKER: derating,
creepage, current capacity, thermal and reliability rules are all functions of the envelope, and until it
is declared each rule quietly picks its own. Four rules resolve against it today and cannot close without
it: **CMP-001** (absolute maximum never reached), **THM-001** (thermal), **ISO-001** (isolation and
spacing, which needs a pollution degree and an altitude) and **REL-001** (reliability).

## 1. How the numbers were arrived at

Every temperature below is the operating range the part's own maker publishes, read out of the sheet in
`v2/vendor/` named beside it. The inside-air rise is this project's own estimate from appendix 32.53 and
is the one number the whole hot end turns on; it is an estimate and `TEST-PLAN.md` E3 is the measurement
that replaces it. No number in this document was chosen to make a limit come out well.

## 2. The parts that bound the envelope

| part | where it sits | operating range | source |
|---|---|---|---:|
| Pervasive Displays E2370KS0C1 e-paper | behind the plate lens, outside face | **-15 to +60 C** | `pdi/pdi-e2370ks0c1-flyer.pdf` |
| Sensirion SGP41 VOC sensor | battery bay, inside air | **-20 to +55 C** | `sensirion/sgp41-datasheet.pdf` |
| 4S pack cells, charge | east pocket, inside | **0 to +45 C cell surface** | `battery/samsung-35e-orbtronic.pdf`, Samsung INR18650-35E Ver. 1.1, 3.12 (source corrected 26 September 2026) |
| 4S pack cells, discharge | east pocket, inside | **-10 to +60 C cell surface** | as above, 3.12 |
| Xenarc 709GNK monitor | in the plate | -20 to +70 C | `xenarc/xenarc-709gnk-product-manual-v2.pdf` |
| TRACO TEN 40-2412WIN | dock strip, inside | -40 to +75 C | `traco/ten40win_datasheet-3049699.pdf` |
| Quectel RM520N-GL 5G | M.2 slot, inside | -30 to +75 C, extended -40 to +85 | `quectel/quectel-rm520n-gl-5g-specification-brief.pdf` |
| Raspberry Pi CM5 | three slots, inside | -20 to +85 C non-condensing, RF best to +75 | `cm5/cm5-datasheet.pdf` section 4.4 |
| Ebyte E22-900M30S LoRa | inside | -40 to +85 C | `lora/ebyte-e22-900m30s-user-manual-en-v1.20.pdf` |
| Ebyte E72-2G4M20S1E | inside | -40 to +85 C | `zigbee/ebyte-e72-2g4m20s1e-user-manual.pdf` |
| Quectel LG290P GNSS | inside | -40 to +85 C | `quectel/lg290p03-hardware-design-v1.1.pdf` |
| Amphenol M.2 B-key socket | inside | -40 to +80 C | `m2/amphenol-mdt420b01001-m2-b-key.pdf` |
| NiceRF SA868 VHF module | inside | **-30 to +70 C** | `nicerf/nicerf-sa868-datasheet-v1.3.pdf`, working temperature range, -30 / 25 / 70 |
| board P, the pack's protection board (generated by `gen_sch_p.py`) | east pocket, beside the cells | **-20 to +60 C**, set by its chemical fuse F2 (Eaton SCF9550-30-05); the gauge BQ4050 and the second level BQ7720700 are -40 to +85 C | `battery/eaton-scf9550-elx1135.pdf` (operating temperature); `battery/ti-bq4050.pdf` (SLUSC67B 6.3); `battery/ti-bq77207.pdf` (SLUSEG7D, recommended operating conditions) |

**TWO OF THE SEVEN OWED RANGES WERE IN THE TREE ALL ALONG (20 September 2026).** The SA868's own datasheet
states its working range in a table and the pack's protection board states both of its ranges; neither
needed a measurement or a letter. **The pack's CELLS are still owed a sheet** and the protection board's
range is not theirs: the cell limits in this table are the Li-ion class ones and stay until that sheet
exists.

**Corrected 26 September 2026: the cell sheet was in the tree as well.** Samsung's INR18650-35E specification
Ver. 1.1 (`battery/samsung-35e-orbtronic.pdf`, sha256 5ec577b952b9...) states charge 0 to 45 C and discharge -10
to 60 C at the cell surface (its 3.12), and storage of -20 to 45 C for three months and -20 to 25 C for a year
at the ex-factory 30 percent charge (its 3.13). Those are the numbers this table and section 4 already carry,
so no bound moves. The 35E is the pack's cell of record (`pcb_pack_protection.yaml`, its `cell` entry), and the
owner's pack ruling of 26 September 2026 keeps it (D-06: one 4S3P pack of Samsung 35E cells, section 4).

**Corrected 26 September 2026 (open item S-07 of the requirements registry, read at `45bde541`): the protection board
row.** Until this correction the table's last row was a bought protection board (`battery/batteryspace-prod-spec-274.pdf`,
-40 to +85 C, storage -40 to +125 C) from before the kit had its own pack board. The pack's protection is board P;
its narrowest part is the chemical fuse F2 at -20 to +60 C, whose top is the cells' own +60 C discharge limit and
whose bottom is the envelope's -20 C, so no bound moves.

**Still owed, and now named as documents this tree does NOT hold rather than as open questions:** the
LimeSDR Mini 2.4 (the tree holds its drawings and STEP, not a datasheet), the RockBLOCK 9704 (its datasheet
here is three and a half thousand characters and states no temperature at all), the QMX HF unit (the tree
holds its operating and CAT manuals, neither of which states one), the 30 W PA stage and the five fans (the
4S pack's cell sheet was on this list until 26 September 2026, see above). Each is a document to fetch, not a measurement to take, and they can only NARROW this
table.

## 3. The inside is not the outside

Appendix 32.53, the no-vent ruling: heat leaves through the aluminium face plate and the case walls, five
fans couple the inside air to the skin, and the estimated inside-air rise is **about 10 K with one
module and about 16 K with three modules loaded, lid open**. The fans are bought as IP68-rated parts and that rating is not claimed for
the kit, which is designed to an IP67-class construction. With the lid closed the kit runs the reduced
mode. **This rise is an estimate and it decides the whole hot end**, so `TEST-PLAN.md` E3 measures it
before any of the numbers below are asserted rather than proposed.

The consequence, stated as arithmetic rather than as a conclusion:

| condition | inside air | first part to reach its limit | outside ambient at that point |
|---|---|---|---|
| three modules loaded, lid open | ambient + 16 K | SGP41 at +55 C | **+39 C** |
| one module, lid open | ambient + 10 K | SGP41 at +55 C | **+45 C** |
| charging, cells at inside air plus self-heating | ambient + 16 K + a few K | cells at +45 C charge limit | **about +25 C** |

The third row is the sharp one and it is not a fault: a lithium pack may not be charged with its cells
above +45 C, and a sealed case with three loaded modules puts the pack in warm air. It means the kit
charges freely in temperate conditions and charging has to hold off in a hot one. It is written here so that
it is a declared behaviour and not a surprise on a bench, and the owner accepted it on 25 September 2026
(D-02b, section 8).

**Shade is a stated operating condition (D-02e, owner ruling of 26 September 2026).** Every row of this table
assumes the kit is shaded, which is what appendix 32.53 designed it for; the kit is operated shaded, with a
shade accessory (a lid sun shield or a tarp), and a design for full sun is a later qualification item. Nothing
here says what a sunlit plate does.

**Corrected 26 September 2026.** This paragraph said the hold-off was done "in hardware" by "the pack
thermistor on the charger's JEITA input". The charger has no such input: TI's BQ25731 datasheet (SLUSE66A,
Table 7-1, pin functions, `ti/bq25731-datasheet.pdf`) lists no thermistor, TS or JEITA pin. The hold-off is
the pack gauge's own: the BQ4050 on board P opens its charge FET outside 0 to 45 C read at the cell surface
(`pcb_pack_protection.yaml`, CHARGE_TEMPERATURE_WINDOW), a threshold held in the gauge's data flash rather than
fixed in hardware, with the panel's cold-charge inhibit below 0 C on top (`PANEL.md` section 10). Decision 40,
ruled by the owner on 26 September 2026, adds hardware beside the gauge, and board P's schematic carries it since
`faf8c981`: a BQ7720700 second level (cell over-voltage 4.325 V, under-voltage 2.25 V, open wire, and a fixed 70 C
over-temperature on its own thermistor since `d90f30e4`) that blows the Eaton SCF9550 chemical fuse F2 once the arming
jumper is closed at commissioning, and the gauge's PTC input enabled (`gen_sch_p.py` lines 243, 288 and 414 to 502 at
`45bde541`). Its 70 C trip is a permanent backstop above the cells' own limits, not a charge window: the charge window
stays the gauge's, and its over-temperature half acts on the charge FET only when the golden image sets the OTFET bit
(`review-packets/battery/CHARGER-STATE-SEQUENCE.md` section 3). The host path is wired end to end: both ends of the
pack's SMBus lead are the same JST-XH 1x4 since `faf8c981` (`PANEL.md` section 10). **Corrected again 26 September
2026 (S-07):** this paragraph said none of decision 40 was laid and that the SMBus lead did not mate, which was the
circuit before `faf8c981`.

## 4. The envelope this proposes

**Ambient temperature, in use: -20 to +40 C**, with three declared carve-outs, each traceable to a part:

- **below -10 C:** the pack is warmed by its heater mat before charge (the mat is RS PRO 245-556, ruled
  4 September); discharge continues to the cells' own -10 C surface limit. **A cold start from the pack is out
  of scope (D-02d, owner ruling of 26 September 2026):** a kit cold-soaked below about -10 C cell temperature
  needs shore or vehicle power, or warming, before it starts from its pack; once warm, use down to -20 C
  ambient holds. No hardware is added for it.
- **below -15 C:** the e-paper is outside its operating range and is expected to update slowly or not at
  all. It carries identity and status with the power off, so this is a degraded display, not a dead kit.
- **above +35 C:** the kit runs the reduced mode (one module) so the inside air stays under the +55 C
  that the battery-bay sensor and the pack need, and charging holds off on the pack gauge's own thermistor
  window (section 3, corrected 26 September 2026).

**Ambient temperature, in storage: -20 to +45 C for up to three months, -20 to +25 C for a year**, at the
pack's ex-factory 30 percent charge. The pack is the only part that makes storage narrower than use.

**Humidity and ingress:** non-condensing in use, which is the CM5's own wording. The closed case is
Peli's IP67; the face is designed to an IP67-class construction and is never labelled IP68; the seal has
not been tested and no rating is claimed until the bench procedure of appendix 32.34 has run. The inside
climate sensor plus the outside pressure sensor are the seal check.

**Altitude: 0 to 3000 m in use, 0 to 4500 m in transport, ruled by the owner on 26 September 2026 (D-02c,
section 8).** It was proposed here without a source, and it is not free: IEC 60664-1 derates clearance above 2000 m, so the PoE 54 V rail and the isolated converter's
barrier both depend on it, which is why ISO-001 cannot close without it. The case keeps Peli's pressure
equalisation valve, so the enclosure itself does not care.

**Vibration and shock:** a whole-kit test plan to MIL-STD-810 is planned and not one of its tests has been
run, so nothing here is qualified to that standard. The plan (transit drop, vibration, temperature operation
and storage, humidity, immersion) was approved on 6 September 2026 and is the declaration. The severities
were ruled by the owner on 26 September 2026 (D-02c, section 8): shock is `TEST-PLAN.md` E1, 26 transit drops
from 1.22 m, and vibration is `TEST-PLAN.md` E2, the composite wheeled vehicle profile for 1 hour per axis.
Neither test has been run, so nothing is qualified to them.

**Input voltage ranges**, from the design as built in the generators:

| input | range | notes |
|---|---|---|
| vehicle and shore DC | **9 to 36 V** | MIL-STD-461 class line filter, NATO 2-pin cable, the 38999 receptacle. **Not qualified for vehicle surge** (D-16, owner ruling of 26 September 2026): no surge claim is made, the entry is not for 24 V military vehicle buses, and MIL-STD-1275 is revisited only if military vehicles become a market |
| solar | tracker input, LT8705A | the tracker's own window, board E |
| pack | 4S, about 14.4 V nominal | **one 4S3P pack of Samsung 35E 18650 cells, about 145 Wh, shrink-wrapped in the east pocket** (D-06, owner ruling of 26 September 2026); the case measurement it was subject to was withdrawn by the owner on 26 September 2026 (D-08 reversed), and the fit is designed against the worst of Peli's own figures (`CASE-MARGINS.md` M4a to M6; M4a and M5 OPEN until the pack's hold-down and a mock-up at the build). Missions longer than the pack rely on vehicle or solar input. The runtime requirement is battery-only hours in the idle and typical modes at +20 C for an aged pack; that number is not computed yet and no runtime is claimed here. Corrected 26 September 2026: the 4S4P 18650 and 4S3P 21700 packs this row named are not expected to fit beside board P under board B, and the 4S3P 18650 fits only without a rigid enclosure (A06, INFERRED from the committed board heights; the case side at the worst of Peli's figures, `CASE-MARGINS.md`) |
| Power over Ethernet out | 54 V | the rail that makes ISO-001 and the altitude question real |
| USB-C Power Delivery out | 45 W | TPS25740A with an LM5176 stage, 5, 9 and 15 V at 3 A (`gen_sch_a.py` line 1003); corrected 26 September 2026: the TPS55288 this row named left the design on 7 September |

**Operating modes**, each already in the design: full (three modules, lid open), reduced (lid closed, or
above +35 C ambient), blackout (LEDs and sounder muted), NVG (panel lighting), EMCON (a hardware line
gates every transmitter rail and the PA bias), and charge (mains, vehicle or solar, gated by the pack
thermistor and by the cold-charge inhibit). **Corrected 26 September 2026, as generated at `45bde541`:** EMCON removes the
supply of the SDR, the Iridium modem, the LoRa, Zigbee and Thread radios, the HF unit, the two WiFi link cards and
the PA rail, so those stop receiving too; it pulls the compute modules' own WiFi and Bluetooth disables low in
hardware; and it puts the 5G module in airplane mode through its disable pin, a mode the module's firmware carries out
(`PANEL.md` section 6, `CONOPS.md` section 4b). **D-05, owner ruling of 26 September 2026: under EMCON the radios go
DARK.** Every radio with an emission path is powered off or RF-disabled in hardware; the VHF path keeps listening,
because its gate is on transmit only; GNSS, DCF77 and the lightning detector continue. What is left under that ruling
is session engineering: the 5G module's supply removal and the items every row of the line shares
(`feasibility/EMCON.md` sections 5 and 7). This paragraph first recorded the compute modules' own radios and the WiFi
cards' disable pin as gaps; both are closed in the schematic since `458b2873` (S-07). The charge gate
is the pack gauge's thermistor window (section 3). The closed-lid reduced mode is the owner's ruling of 25
September 2026 (D-02b, section 8).

**Single-fault conditions the design is expected to survive**, written as the design's own protections so
that PWR-003 and BAT-002 have something to be judged against: a short on any downstream rail (eFuses), a
reversed or over-voltage input (the ideal diode and the 9 to 36 V front end), a shorted pack lead (the
25 A blade and the pack's own protector), a failed module (the voted I/O fabric and the per-bank USB
ring), a cell driven past its limits with the gauge's firmware wrong or dead (board P's second level and chemical
fuse, decision 40), loss of the panel controller (the hardware EMCON line is independent of any module), and water on
the floor of the case (the floor water sensor with pack shutdown). **Corrected 26 September 2026:** the loss
of the panel controller leaves the transmitters safe but, as generated, no compute module powers without it
(`ARCH-PCB-B-IOHA.md` section 10), so it is survived for EMCON and not for compute. **No fault tree has been drawn and no
coordination study exists**: PWR-003 says so and is open.

## 5. What this document does NOT settle

The altitude number, the vibration and shock severities, the pollution degree that ISO-001 needs, and the
expected service life and duty cycle that REL-001 needs. All four are in decision 34. **Since 26 September
2026** the altitude and the severities are the owner's rulings (section 8), and so are the cold start from the
pack (out of scope) and direct sun (operate shaded); the service life is TBD for prototype 1 by the same
rulings; the pollution degree and the duty cycle stay open. The transient levels
were in this list until 17 September and are section 6 now, because owner decision 31 cannot be ruled without
them: a clamp is chosen against a level.

## 6. The transient levels, proposed (17 September 2026, part of decision 34)

**Nothing in this tree states one, and one thing in it needs one.** Ten conductors on boards D and E reach a
semiconductor with nothing between them (decision 31), and the part that would stand in front of each is
chosen by the level it has to survive. The qualification plan of `TEST-PLAN.md` is an INTENT and nothing in it
has been run, no kit having been built: it names conducted and radiated susceptibility methods (CE102, CS101,
CS114, RE102, RS103) and until today carried **no electrostatic discharge method at all**, so the one transient
a person actually applies to this kit, by touching a connector after walking across a floor, was neither
specified nor planned for.

| what | proposed level | what it is traceable to here | what it costs |
|---|---|---|---|
| Electrostatic discharge, every surface and conductor a person can touch | **IEC 61000-4-2 level 4: 8 kV contact, 15 kV air** | the clamp this design already buys: ST's USBLC6-2SC6 sheet in `v2/vendor/st/` guarantees that level, and five of board B's USB ports and board P's SMBus pair already stand behind it | nothing where a clamp is fitted; it is the number the ten unclamped conductors would be fitted to, and one test method in the plan |
| Surge on the conductors that leave the case on a long lead (shore and vehicle DC, PoE) | what the fitted part survives: the SMCJ40A on board E's inlet is a **1500 W peak pulse part at 10/1000 us** | the Vishay SMCJ series sheet in `v2/vendor/vishay/` | nothing today: it describes what is fitted. Asking instead for an IEC 61000-4-5 installation level is a ruling, and then the coordination between the fuse, the clamp and the front end has to be computed rather than asserted |
| Electrical fast transient on the power leads | 2 kV, the common industrial figure | **NOTHING IN THIS TREE.** It is written here as the number a reader would expect and it has no authority behind it, which under this project's own maturity rule makes it unverified rather than a requirement | a standard this project does not hold, or a test house's own statement |

**The honest shape of this section:** the first row is free and is the one decision 31 needs, the second row
describes the design rather than constraining it, and the third has no source. A ruling that takes the first
row alone is worth having on its own.

**What the owner's rulings of 26 September 2026 add (section 8):** the first row is the DESIGN level every
clamp is chosen against and the level of the test below; it is not a compliance claim, because the prototype
makes no EMC claim (D-04). The second row describes what is fitted; no surge rating is claimed for the vehicle
entry, which is recorded as not qualified for vehicle surge (D-16, section 8).

**The test the plan is missing**, written so the ruling has something to point at: the kit powered from its
pack, every bearer up, discharges applied to the plate, the toggles, the display bezel, every antenna
bulkhead's shell and every exposed conductor of the two headset jacks, the USB-C outlet, the Ethernet jack and
the pod lead; pass is no upset, no reset, no loss of a bearer, no lost secure-element key and no damage.

## 7. Decision 34 as it was asked on 16 September 2026 (ruled by the session on 21 September 2026)

**Kept as the record of the question, not as an open item.** Decision 34 was ruled by the session on 21
September 2026 with option 1 below, which is the status at the top of this document; the altitude question at
the end of this section was answered by the owner on 26 September 2026 (section 8). Until 26 September this
heading still read "Decision 34, open".

**Options, costed, the recommendation first.**

1. **Take the envelope of section 4 as written, RECOMMENDED.** Cost: nothing but the ruling. Buys: four
   blocked rules get their numbers, and the three carve-outs become declared behaviour that the panel
   software and the test plan can both be written against. The residual is that the hot end rests on an
   estimated 16 K rise until `TEST-PLAN.md` E3 measures it, and that two of the three carve-outs are
   visible to whoever carries the kit (a slow e-paper in deep cold, one module in real heat).
2. **Buy a wider hot end by changing two parts.** The battery-bay VOC sensor at +55 C and the e-paper at
   +60 C are the two narrowest parts in the kit; a wide-temperature gas sensor and a wider-range display
   would move the ceiling from +39 C to roughly the pack's own charge limit, which is where it would then
   stop. Cost: two part searches, two footprints, a board E phase and a board C phase, and the e-paper is
   the owner's own hardware. Buys: about six degrees of ambient, and the pack still limits charging.
3. **Declare a narrower envelope that every part meets with no carve-outs at all: -10 to +35 C.** Cost:
   nothing but the ruling, and a kit that is declared unusable in conditions it would in fact survive.
   Buys: an envelope with no footnotes. Not recommended for a field kit.

**A question inside the decision, whichever option is taken:** the altitude. 3000 m in use is proposed
because it is the common industrial number and because the kit is carried rather than flown; if the kit
is ever expected in an unpressurised aircraft, say so now, because it changes the PoE rail's spacing and
the isolated barrier and both of those are copper.

## 8. Owner rulings of 25 and 26 September 2026: margins, the closed lid, severities, altitude, cold start, sun, surge and EMC

Asked as questions D-02a to D-02e, D-04 and D-16 of the foundation re-baseline (MESHSAT-1357), one at a time,
each with its options, the reasoning behind each and a recommendation, and each ruled at the recommendation.
D-02a and D-02b were ruled on 25 September 2026 between about 23:27 and 23:40 CEST, the others on 26 September
2026 between about 00:05 and 00:55 CEST. These are the owner's rulings, not the session's, and they sit beside
decision 34's adoption rather than replacing it. Nothing has been built, so every line below is a requirement,
a test limit or a stated condition, not a result.

**D-02a (25 September): the test levels above and below this envelope are qualification margins, not limits.**

| `TEST-PLAN.md` level | the envelope limit it goes past | what it is | pass line |
|---|---|---|---|
| E3, operation for 4 hours at +55 C | in use, +40 C | a qualification margin | survive and recover |
| E3, storage for 24 hours at +71 C | storage, +45 C (three months) | a qualification margin | survive and recover |
| E4, storage for 24 hours at -33 C | storage, -20 C | a qualification margin | survive and recover |
| everything inside section 4's envelope, E4's operation at -20 C included | none | acceptance | operate to specification |

The two pass lines are different questions and a result is reported against the one it was run for: inside
the envelope the pass line is operation to specification; at a margin it is survival of the exposure and
recovery to specification once back inside. By this document's own arithmetic (section 3, a 10 to 16 K inside-air rise) an
ambient of +55 C puts the inside air at +65 to +71 C, above the cells' +60 C discharge limit, which is why
operation at that level is a margin and not a specification. No test level is lowered to the envelope.

**D-02b (25 September): the kit operates with its lid closed, in a defined reduced mode.** The example the owner ruled on is
GNSS, the LoRa mesh, Iridium and APRS beacons, the monitor off and one compute module; the exact bearer set and
power state are engineering, fixed against the thermal bound of section 3. A closed-lid state and a closed-lid
thermal test join `TEST-PLAN.md`. A lid sensor is an engineering item, and the case-open tamper switch can serve
as both; under decision 30 it logs and never wipes. **Two consequences the owner accepted with it:** above +35 C
ambient the kit runs one compute module, so there is no compute redundancy in the heat; and with three loaded
modules, charging holds off above about +25 C ambient (section 3).

**D-02c (26 September): severities, altitude and service life.** Shock is `TEST-PLAN.md` E1 (26 transit drops from 1.22 m) and
vibration is `TEST-PLAN.md` E2 (the composite wheeled vehicle profile, 1 hour per axis). The altitude is 0 to
3000 m in use and 0 to 4500 m in transport. The service life is TBD for prototype 1, and until it is set REL-001
has no life to judge against.

**D-02d (26 September): a cold start from the pack is OUT OF SCOPE, and stated.** The cells may not be
discharged below -10 C at their surface (section 2), while the in-use floor is -20 C ambient. A kit cold-soaked
below about -10 C cell temperature needs shore or vehicle power, or warming, before it starts from its pack; once
warm, use down to -20 C ambient holds. No hardware is added. The statement belongs in the ConOps as well as here.

**D-02e (26 September): the kit is operated SHADED, and that is stated.** Shade is the condition appendix 32.53
designed for and section 3's arithmetic assumes; a shade accessory (a lid sun shield or a tarp) goes with the
kit, and a design for full sun is a later qualification item. No board change.

**D-16 (26 September): no vehicle surge claim.** No surge rating is claimed: the vehicle and shore entry is recorded as
NOT QUALIFIED for vehicle surge, with a warning against 24 V military vehicle buses, and MIL-STD-1275 would be
revisited only if military vehicles become a market. What is fitted (section 6, second row) is described and not claimed.

**D-04 (26 September), the part that bears on this envelope:** prototype 1 is a non-commercial prototype in
the Netherlands and the EU, operated by a licensed radio amateur. No CE or RED marking and no EMC claim is made,
so the MIL-STD-461 runs of `TEST-PLAN.md` are characterisation, not qualification, and section 6's first row is
a design level, not a claim; the design keeps an EU route open. Every transmitter is configured to the
operator's licence and the EU limits, and the VHF path gets a band lock. The pack's UN 38.3 status is unknown,
so how it is transported is stated rather than assumed. **Corrected 26 September 2026** (the review of that day,
`reviews/2026-09-26-foundation-progress-review.md` section 5): an unknown status permits no route by itself, road included, since road carriage has its own
dangerous-goods rules (the ADR); the pack's classification, the conditions that apply to it or an exception that
applies are to be established before any transport route is claimed acceptable (TBD, a bounded item, not a broad
compliance project; `CONOPS.md` section 4, Transport row).

**What these rulings leave open:** the service life (TBD for prototype 1), the pollution degree ISO-001 needs
and the duty cycle REL-001 needs.
