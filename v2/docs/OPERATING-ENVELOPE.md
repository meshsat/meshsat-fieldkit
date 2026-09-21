# The operating envelope, ADOPTED 21 September 2026

**Status: ADOPTED. Owner decision 34 was ruled by the session on 21 September 2026**, under the owner's
instruction of that evening that an agentic system takes informed engineering decisions on his behalf rather
than queueing them to a non-engineer. What is adopted is **section 4 as the design envelope** and **section
6's first row, IEC 61000-4-2 level 4 (8 kV contact, 15 kV air), as the transient level**; the electrical fast
transient row is recorded as NOT A REQUIREMENT of this project, because nothing in this tree is a source for
one. The altitude, the vibration and shock severities and the service life stay OPEN, for the rules that
genuinely need them, and are not invented here. Reverse by reopening decision 34, which returns this document
to a draft.

**What is NOT taken here and stays the owner's:** ADVERTISING the kit to this envelope. That is a claim about
the product and belongs with the public copy, not with the engineering.

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
| 4S pack cells, charge | east pocket, inside | **0 to +45 C cell surface** | Li-ion class limit; the 4S pack's own sheet is owed |
| 4S pack cells, discharge | east pocket, inside | **-10 to +60 C cell surface** | as above |
| Xenarc 709GNK monitor | in the plate | -20 to +70 C | `xenarc/xenarc-709gnk-product-manual-v2.pdf` |
| TRACO TEN 40-2412WIN | dock strip, inside | -40 to +75 C | `traco/ten40win_datasheet-3049699.pdf` |
| Quectel RM520N-GL 5G | M.2 slot, inside | -30 to +75 C, extended -40 to +85 | `quectel/quectel-rm520n-gl-5g-specification-brief.pdf` |
| Raspberry Pi CM5 | three slots, inside | -20 to +85 C non-condensing, RF best to +75 | `cm5/cm5-datasheet.pdf` section 4.4 |
| Ebyte E22-900M30S LoRa | inside | -40 to +85 C | `lora/ebyte-e22-900m30s-user-manual-en-v1.20.pdf` |
| Ebyte E72-2G4M20S1E | inside | -40 to +85 C | `zigbee/ebyte-e72-2g4m20s1e-user-manual.pdf` |
| Quectel LG290P GNSS | inside | -40 to +85 C | `quectel/lg290p03-hardware-design-v1.1.pdf` |
| Amphenol M.2 B-key socket | inside | -40 to +80 C | `m2/amphenol-mdt420b01001-m2-b-key.pdf` |
| NiceRF SA868 VHF module | inside | **-30 to +70 C** | `nicerf/nicerf-sa868-datasheet-v1.3.pdf`, working temperature range, -30 / 25 / 70 |
| the pack's protection board | east pocket | **-40 to +85 C** (storage -40 to +125) | `battery/batteryspace-prod-spec-274.pdf` |

**TWO OF THE SEVEN OWED RANGES WERE IN THE TREE ALL ALONG (20 September 2026).** The SA868's own datasheet
states its working range in a table and the pack's protection board states both of its ranges; neither
needed a measurement or a letter. **The pack's CELLS are still owed a sheet** and the protection board's
range is not theirs: the cell limits in this table are the Li-ion class ones and stay until that sheet
exists.

**Still owed, and now named as documents this tree does NOT hold rather than as open questions:** the
LimeSDR Mini 2.4 (the tree holds its drawings and STEP, not a datasheet), the RockBLOCK 9704 (its datasheet
here is three and a half thousand characters and states no temperature at all), the QMX HF unit (the tree
holds its operating and CAT manuals, neither of which states one), the 30 W PA stage, the five fans and the
4S pack's cell sheet. Each is a document to fetch, not a measurement to take, and they can only NARROW this
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
charges freely in temperate conditions and the charger has to hold off in a hot one, which the pack
thermistor on the charger's JEITA input already does in hardware. It is written here so that it is a
declared behaviour and not a surprise on a bench.

## 4. The envelope this proposes

**Ambient temperature, in use: -20 to +40 C**, with three declared carve-outs, each traceable to a part:

- **below -10 C:** the pack is warmed by its heater mat before charge (the mat is RS PRO 245-556, ruled
  4 September); discharge continues to the cells' own -10 C surface limit.
- **below -15 C:** the e-paper is outside its operating range and is expected to update slowly or not at
  all. It carries identity and status with the power off, so this is a degraded display, not a dead kit.
- **above +35 C:** the kit runs the reduced mode (one module) so the inside air stays under the +55 C
  that the battery-bay sensor and the pack need, and the charger holds off on the pack thermistor.

**Ambient temperature, in storage: -20 to +45 C for up to three months, -20 to +25 C for a year**, at the
pack's ex-factory 30 percent charge. The pack is the only part that makes storage narrower than use.

**Humidity and ingress:** non-condensing in use, which is the CM5's own wording. The closed case is
Peli's IP67; the face is designed to an IP67-class construction and is never labelled IP68; the seal has
not been tested and no rating is claimed until the bench procedure of appendix 32.34 has run. The inside
climate sensor plus the outside pressure sensor are the seal check.

**Altitude: proposed 0 to 3000 m in use, 0 to 4500 m in transport.** This number has no source yet and it
is not free: IEC 60664-1 derates clearance above 2000 m, so the PoE 54 V rail and the isolated converter's
barrier both depend on it, which is why ISO-001 cannot close without it. The case keeps Peli's pressure
equalisation valve, so the enclosure itself does not care.

**Vibration and shock:** a whole-kit test plan to MIL-STD-810 is planned and not one of its tests has been
run, so nothing here is qualified to that standard. The plan (transit drop, vibration, temperature operation
and storage, humidity, immersion) was approved on 6 September 2026 and is the declaration. No
severity is chosen yet; choosing one is part of decision 34.

**Input voltage ranges**, from the design as built in the generators:

| input | range | notes |
|---|---|---|
| vehicle and shore DC | **9 to 36 V** | MIL-STD-461 class line filter, NATO 2-pin cable, the 38999 receptacle |
| solar | tracker input, LT8705A | the tracker's own window, board E |
| pack | 4S, about 14.4 V nominal | 4S4P 18650 or 4S3P 21700, about 200 Wh |
| Power over Ethernet out | 54 V | the rail that makes ISO-001 and the altitude question real |
| USB-C Power Delivery out | 45 W | TPS25740 and TPS55288 |

**Operating modes**, each already in the design: full (three modules, lid open), reduced (lid closed, or
above +35 C ambient), blackout (LEDs and sounder muted), NVG (panel lighting), EMCON (a hardware line
gates every transmitter rail and the PA bias), and charge (mains, vehicle or solar, gated by the pack
thermistor and by the cold-charge inhibit).

**Single-fault conditions the design is expected to survive**, written as the design's own protections so
that PWR-003 and BAT-002 have something to be judged against: a short on any downstream rail (eFuses), a
reversed or over-voltage input (the ideal diode and the 9 to 36 V front end), a shorted pack lead (the
25 A blade and the pack's own protector), a failed module (the voted I/O fabric and the per-bank USB
ring), loss of the panel controller (the hardware EMCON line is independent of any module), and water on
the floor of the case (the floor water sensor with pack shutdown). **No fault tree has been drawn and no
coordination study exists**: PWR-003 says so and is open.

## 5. What this document does NOT settle

The altitude number, the vibration and shock severities, the pollution degree that ISO-001 needs, and the
expected service life and duty cycle that REL-001 needs. All four are in decision 34. The transient levels
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

**The test the plan is missing**, written so the ruling has something to point at: the kit powered from its
pack, every bearer up, discharges applied to the plate, the toggles, the display bezel, every antenna
bulkhead's shell and every exposed conductor of the two headset jacks, the USB-C outlet, the Ethernet jack and
the pod lead; pass is no upset, no reset, no loss of a bearer, no lost secure-element key and no damage.

## 7. Decision 34, open: the envelope, and whether to buy a wider one

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
