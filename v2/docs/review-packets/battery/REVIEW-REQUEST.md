# Battery and protection review packet: index, questions and review route

MeshSat field kit V2, board P (the 4S3P pack's BMS) and the pack's charge path on board A. MESHSAT-1357, prepared by the
integrating agent session's review stream BAT on 26 September 2026.

**Status of what is reviewed: a prototype design. No board of this set has been fabricated, assembled, programmed or
tested; no cell, fuse or gauge has been measured. All reviews to date are by AI agent sessions; no qualified human
engineer has reviewed this revision.** Generating this packet does not release board P or the pack to fabrication. Owner
ruling D-09 (26 September 2026): a paid battery-and-protection review by a qualified electronics engineer happens before
the pack is built; the session prepares the packet and the request; any spend needs a quote and the owner's approval.
**Nothing in this file has been sent to anyone.**

## 1. Packet index

| File | What it answers |
|---|---|
| `PROTECTION-ARCHITECTURE.md` | the cells and their limits (two maker revisions), the protection layers, primary/secondary independence, operating states (storage, transport, charge, discharge, cold, hot, fault latched), sensor faults, loss of the primary controller, and the fault-state table with the protective action and the part that performs it |
| `SECONDARY-OT-DECISION.md` | the secondary over-temperature decision: evidence, options, the circuit taken, the netlist change verified on the KiCad box, and the test-margin reconciliation for the pack |
| `FUSE-INTERPRETATION.md` | the Eaton SCF9550-30-05's environmental entries read for the assembled pack, alternatives, heater actuation, interruption against the prospective fault, FET and gate behaviour in a hard short, and the arming jumper JP1 with its commissioning order |
| `PRIMARY-CONFIGURATION.md` | the BQ4050 data-flash (golden image) settings this protection depends on, against TI's defaults, and which protections exist without the image |
| `CHARGER-STATE-SEQUENCE.md` | the BQ25731 charger on board A as a state sequence: power-up defaults, watchdog expiry, temperature inhibition, termination, recovery, and the controller crashing in each state |
| `candidate/pcb-p-pack-schematic.pdf` | board P's schematic, two A3 pages, as regenerated for this packet (the corrected candidate) |
| `candidate/pcb-p-pack.kicad_sch`, `pcb-p-pack.net`, `pcb-p-pack.net.prov.json`, `pcb-p-pack-intent.json` | the matching native KiCad 9 schematic, netlist, provenance and design-intent data |
| `candidate/pcb-p-pack-bom.csv`, `pcb-p-pack-jlc-bom.filled.csv` | the bill of materials (KiCad export) and the JLC order BOM with LCSC codes |
| `candidate/pcb-p-pack-erc.rpt` | KiCad ERC report: 123 warnings (library-table and wire-endpoint warnings of the generator), 0 errors |
| `candidate/netlist-diff-vs-main.txt`, `netlist-diff-vs-first-cycle.txt` | the change against main's board P, part by part and net by net, and against this packet's first cycle (the TS network's two values) |
| `candidate/ts_network.py`, `ts_network.out` | the arithmetic behind the secondary's temperature network (OT window and UT margin under one accuracy model) |
| `v2/ecad/tools/tests/test_pack_secondary_ts.py` | the fixture that holds the secondary's TS property on the generator and the netlist (it fails on main's fixed resistor and on the first cycle's 22 kohm shunt) |
| `evidence/regeneration/` | the KiCad box run behind `candidate/`: driver, log, environment, parity of main's files, change records, gate verdicts before and after, output hashes, the fixture's recorded runs |
| `evidence/trm_defaults_check.py`, `trm_defaults_check.out` | the mechanical sweep of the BQ4050 manual for defaults it states two ways (BAT-F13) |
| `evidence/jlc-queries-bat.json` | the JLC parts API readings for R33, R34 and J_TS2 |
| `MANIFEST.md`, `evidence/check_manifest.py` | the exact revision and the sha256 of every file above and of every document cited, and the release check that they are all present (section 5) |

**Changes in this revision of board P, each with its finding** (the first seven merged on main in `faf8c981`, described in
the generator's own comments; the last made by this packet):

| Change | Finding | Where |
|---|---|---|
| the gauge moved to TI's RSM0032A land (4 x 4 mm, 0.4 mm) | W6-F2 | `gen_sch_p.py:112-118, 165-167` |
| four cell thermistors (one per series group) instead of one plus fixed resistors | F-PK-02 | `:210-221` |
| terminal clamp D1 turned the right way round (cathode on PACK_P) | S-09, A03 | `:307-346` (D1) |
| SMBus clamps replaced (the USBLC6 held the gauge's VCC at its breakdown) | F-BP-01 | `:317-342` |
| SMBus lead ground on the pack side of the shunt; PRES through 1 kohm | S-05 | `:224-227, 505-514` |
| second level BQ7720700, chemical fuse SCF9550-30-05, fuse drive, arming jumper, UV hold, PTC element, test points | decision 40 / D-15 | `:228-244` (PTC), `:247-289` (F2), `:351-502` (second level, fuse drive, UV hold) |
| terminal capacitors in series | O-12 | `:295-305` |
| the second level's over-temperature restored (own NTC on J_TS2, R34 270 ohm, R33 18 kohm, TP15; the first cycle's 200 ohm / 22 kohm withdrawn) | BAT-F01 | `:373-419`; `SECONDARY-OT-DECISION.md` section 6 |

The committed board P layout (P4) predates all of these and is not for review; board P is to be re-placed and routed at
4 layers, 2 oz (decision 28).

## 2. Findings of this packet

| ID | Finding | State |
|---|---|---|
| BAT-F01 | the second level's over-temperature was disabled by a fixed 10 kohm to meet a +71 C storage margin | **closed in the design**: restored with its own NTC; the network re-dimensioned in the second cycle so that it is indifferent to UT at the chip's own UT accuracy (TUT_ACC), 15.0 % margin (13.8 % on the slope of TI's own UT thresholds, the most conservative view); regenerated and diffed on the box; held by `tests/test_pack_secondary_ts.py` |
| BAT-F02 | TEST-PLAN E3/E4 store and run the pack outside its cells' rating (and E3 contradicts its own "pack under 60 C") | proposed reconciliation for the pack at the cells' limits (TEST-PLAN owner) |
| BAT-F03 | the fuse's temperature rating had been read through its +105 C stress exposure | **closed as an interpretation**: the operating range governs; the pack stays within it; Q-E1, Q-E2 open |
| BAT-F04 | the records call F1 a 25 A ATOF (regular) blade in a Keystone 3568 MINI holder | open for the yaml owners; the MINI 297 figures stated |
| BAT-F05 | TI's BQ4050 image holds both FETs off (FET_EN = 0), so a pack on it is inert; once FET control is on, TI's other defaults conflict with this pack (COV 4.30 V above the secondary's 4.275 V low trip; OCD1 6 A; OTC 55 C; no FET action on over-temperature; no PF or FUSE enabled; fuse timeout 30 s against Eaton's 60 s; precharge FET selected where none is fitted; a 3-cell count; TS2 read as a FET temperature; shutdown at 1.75 V per cell against Samsung's 2.00 V) | requirements set in `PRIMARY-CONFIGURATION.md`; open until the golden image exists |
| BAT-F06 | board E's always-on loads sit on the pack side of board A's charge shunt and take most of the host-free 256 mA | open (board A and E authors, architecture page) |
| BAT-F07 | turning off a hard short through 5.1 kohm gate resistors is marginal to outside the protection FETs' SOA | open (Q-P6) |
| BAT-F08 | stale records: OPERATING-ENVELOPE row for a COTS protection board; CONOPS Charging row on main's topology | open (their owners) |
| BAT-F09 | the two Samsung 35E specification revisions differ on the storage floor (-20 C against 0 C) | TBD (pack purchase) |
| BAT-F10 | the gauge's host watchdog ties charging to board E's sensor controller | **decided**: enabled at 10 s by an explicit write (Enabled Protections C[HWDF] = 1, HWD Delay = 10 s) confirmed by the commissioning read-back, not left to a default the TRM states two ways (BAT-F13); taken by the session under the owner's standing rule |
| BAT-F11 | the gauge's measurement and balancing share the tap wires with the second level's open-wire detection | question Q-P1 |
| BAT-F12 | SLUSE66A 9.6.3 says charging starts on a host write; the register default says 256 mA | bench and Q-TI-2 |
| BAT-F13 | SLUUAQ3A states defaults two ways for thirteen settings and six permanent-fail thresholds: FET Options (CHGFET), Temperature Enable, Protection Configuration, Enabled Protections B, C (HWDF) and D, Enabled PF A to D, LED Configuration, Initial Battery Mode, ZVCHG Exit Threshold, Open Thermistor FET and Cell Delta, VIMR and VIMA thresholds, AFER Delay Period (`PRIMARY-CONFIGURATION.md` section 1a, from a mechanical sweep of the whole of chapter 14; the second cycle had reported only two of them) | **requirement changed**: every word of `PRIMARY-CONFIGURATION.md` section 2 is written explicitly and read back after a reset, with the fresh device's data flash archived first; Q-TI-6 prepared |
| BAT-F14 | precharge through the charge FET (PCHG_COMM = 1, needed because board P has no precharge FET) also enables the gauge's 0-V charging (SLUUAQ3A 4.9), against Samsung's "Under 1.0V voltage, do not charge the cell" | **requirement set by the session**: SUV permanent fail at 1.0 V, checked at wake with both FETs off (SUV_MODE), never mapped to the fuse; whether the hardware 0-V circuit can conduct before that check is Q-TI-7 and a bench item |

## 3. Questions for the qualified reviewer

Please answer each with: acceptable as designed, acceptable with a change (which), or blocking. Where a question names a
document, the document is in this packet or in the repository at the revision in `MANIFEST.md`.

1. **Architecture (Q-P0).** Is the layering in `PROTECTION-ARCHITECTURE.md` sections 2 and 3 (BQ4050 primary with high-side
   common-drain FETs; BQ7720700 second level driving the chemical fuse through COUT and the discharge FET through DOUT;
   PTC element; 25 A blade) adequate for a 4S3P Samsung 35E pack of about 145 Wh at 10 A typical and 18 A peak, in a sealed
   case whose inside air runs 10 to 16 K above ambient? What would you require before pack PCB release?
2. **Shared actuators (Q-P0b).** Q2 serves both levels' discharge action and Q3/F2 both levels' fuse action. Acceptable?
3. **Secondary over-temperature (Q-P7).** The TS network (`SECONDARY-OT-DECISION.md` section 4: 270 ohm series, 18 kohm
   shunt) restores a trip of 62.7 to 77.5 C (conservative reading of TI's accuracy) that permanently opens F2. Is a permanent disconnect at that temperature appropriate for this pack? Is the network
   (made to be indifferent to an under-temperature function TI does not state for this variant) preferable to TI's bare
   NTC? Where on a shrink-wrapped 4S3P block should this sensor sit?
4. **The test-margin reconciliation (Q-P13).** Is excluding the pack from the kit's +71 C, +55 C and -33 C margins, and
   testing it at its cells' own limits instead, the right reading of "survive and recover" for a Li-ion pack?
5. **Balancing against open-wire detection (Q-P1).** SLUSEG7D 8.2 warns that the BQ77207's open-wire feature "may be affected
   if the primary protector or monitor device is actively measuring the cells". Here the BQ4050 measures and balances on the
   same tap wires through 100 ohm filters. Is open wire still reliable, and can balancing raise a false open wire (which
   would open F2)?
6. **Over-voltage coordination (Q-P2).** Primary COV at 4.25 V (2 s) against the secondary's 4.325 V +-20 mV (0 to 60 C),
   +-50 mV over its full range (1 s). Is 25 mV of worst-case separation enough given the BQ4050's own cell-voltage accuracy?
7. **Permanent fails, the fuse and the image (Q-P3, Q-P4).** Which BQ4050 permanent failures should be enabled and which
   should drive FUSE? The image's interim values are Enabled PF A 0x53 (SUV, SOV, SOT, SOTF), B 0x00 (the imbalance
   checks, whose thresholds the TRM states two ways), C 0xFB and D 0xF0, with SOCC, SOCD and OPNCELL off
   (`PRIMARY-CONFIGURATION.md` section 2). Should the gauge attempt a fuse blow below the heater's rated 10.5 V (Min Blow
   Fuse Voltage), or not at all? The TRM states defaults two ways for nineteen settings and thresholds (BAT-F13), so the
   image writes every word explicitly and the fresh device's data flash is archived first: is there any word you would add
   to that list, and do you agree with the reserved-bit values taken from Table 14-1?
8. **Loss of the primary (Q-P5).** Is the AFE watchdog's behaviour on a firmware hang (SLUSC67B 6.8: tWDT, tFETOFF) enough to
   rely on the FETs opening? What does the pack lack if U1 is dead with its FETs on (`PROTECTION-ARCHITECTURE.md` section 6)?
9. **Hard short (Q-P6).** `FUSE-INTERPRETATION.md` section 4 estimates that the gauge turning off a 270 to 480 A short
   through 5.1 kohm gate resistors is marginal to outside the CSD17570Q5B's SOA. Do you agree, and would you add a faster
   discharge-gate turn-off, parallel FETs, or accept the blade F1 as the device that clears a hard short?
10. **Fuse coordination and rating (Q-P12).** F2 (80 A breaking) cannot clear a hard short; F1 (MINI 297 25 A, 1000 A at 32
    VDC) can, but Eaton publishes no melting I2t for F2. Is the order F1 before F2 a blocking item, and is the SCF9550-30-05
    acceptable with its -20 to +60 C operating range and no published derating (`FUSE-INTERPRETATION.md` sections 1 to 3)?
11. **UV hold on a high-side FET (Q-P8).** Q5 pulls DSG_G to the cell negative, so Q2's gate sits at minus V(PACK_P) during an
    under-voltage hold: 3.2 V from its 20 V rating at 16.8 V, with nothing preventing a charger fault above 20 V from exceeding
    it. Acceptable, or add a gate-source clamp (which loads the gauge's charge pump)?
12. **Open wire fires the fuse (Q-P9).** A tap lead that stays open for 4 s opens F2 for good (round-4 RP-18, kept on
    purpose). Acceptable for a kit that must pass drop and vibration tests (TEST-PLAN E1, E2)?
13. **Commissioning (Q-P11).** Is the arming order and the polarity-sensitive closure check of JP1
    (`FUSE-INTERPRETATION.md` section 5) sound? Is an arming jumper the right control at all?
14. **Charging with the controller crashed (Q-P10).** `CHARGER-STATE-SEQUENCE.md` concludes: safe (all cell limits are the
    pack's own) provided the golden image turns on FET action for over-temperature; not useful (the pack is held, not charged).
    Do you agree, and is BAT-F06 (board E's always-on loads on the pack side of the charge shunt) something to fix before the
    board A/E interface is frozen?
15. **Over-discharged cells (Q-P14).** With the charge FET doing precharge (PCHG_COMM = 1) the gauge also 0-V charges
    below its own supply minimum (SLUUAQ3A 4.9). This packet enforces Samsung's "do not charge under 1.0 V" with an SUV
    permanent fail at 1.0 V checked at wake with both FETs off (SUV_MODE = 1), Shutdown Voltage at Samsung's 2.00 V, and a
    bench check that a 4S string at 0.9 V per cell takes no charge current (BAT-F14). Is that sufficient, or would you drop
    precharge altogether (PCHG_COMM = 0: no path) and accept that a pack below the precharge start voltage cannot be
    recharged in the field?
16. **Anything else (Q-P99).** Any item you would block pack PCB release on that these questions miss.

## 4. Questions for the part makers (prepared, not sent)

To TI (E2E forum or TI support), each with the part and the document:
- **Q-TI-1.** BQ7720700 (SLUSEG7D Rev. D): the data sheet lists an under-temperature detection (6.5, TUT -30 to 0 C) that
  drives both outputs (7.1), but the Device Comparison Table has no UT column. Is UT enabled on the BQ7720700, and if so at
  which threshold? Is TUT_ACC (+-5 C) the device's UT accuracy with RUT_ACC (+-2 %) the external-resistance tolerance
  footnote (1) assumes, or does TUT_ACC already include it? (SFFS317A Table 4-3 lists an open TS as "No OT detection"
  only.) How is TS biased in time: with ICC 2 uA typical the pull-up RTC cannot be on continuously, so what are the bias
  pulse's width, period and level, which our commissioning check reads on a scope?
- **Q-TI-2.** BQ25731 (SLUSE66A): with no host write after power-on, does the charger charge at the 256 mA register default,
  or does 9.6.3's "the charge will start when the host writes the charging current to ChargeCurrent() register" apply?
- **Q-TI-3.** BQ25731: with CHRG_INHIBIT = 1 and no battery FET (VSYS tied to the battery through RSR), what does the
  converter regulate while an adapter is present?
- **Q-TI-4.** BQ4050 (SLUSC67B 6.8, SLUUAQ3A 5.4): if the gauge's processor stops, does the AFE watchdog turn CHG and DSG off
  (tFETOFF), and within what worst-case time?
- **Q-TI-5.** BQ77207 with a BQ4050 on the same tap wires: guidance on open-wire detection while the gauge balances.
- **Q-TI-6.** BQ4050 (SLUUAQ3A Rev. A): the manual states these defaults two ways; which is shipped in each case?
  FET Options 0x20 against CHGFET "0 = FET active (default)" (14.2.1.1); Temperature Enable 0x6 against TS3 and TS4
  enabled (14.2.1.12); Protection Configuration 0x00 against CUV_RECOV_CHG and SUV_MODE enabled (14.2.4.1); Enabled
  Protections B, C and D 0xFF in 14.2.4.3 to 14.2.4.5 against 0x3f, 0xd5 (HWDF = 0) and 0x0f in Table 14-1; Enabled PF A
  to D 0x00 against bit texts that mark most checks enabled, with Enabled PF A's text naming bit 4 twice and calling bits 3
  and 2 reserved beside SOCD and SOCC (14.2.5.1 to 14.2.5.4); LED Configuration 0x0D0 against LEDC "0,0 (default)";
  Initial Battery Mode 0x0081 against CHGM and ICC's marks (14.14.1.4); ZVCHG Exit Threshold 0 mV against 2200 mV
  (14.2.7); Open Thermistor FET and Cell Delta 1500 against 200 (14.10.7.3, 14.10.7.4); VIMR Delta Threshold 200 against
  500 mV; VIMA Delta Threshold 300 against 200 mV and Delay 5 against 2 s; AFER Delay Period 5 against 2 s. And: should the
  reserved bits of Enabled Protections B (7, 6), C (5, 3) and D (7 to 4) be written 0, as Table 14-1 has them, or 1, as
  the section headers' 0xFF and the "RSVD_ONE ... programmed to 1" bits of Enabled Protections A and B suggest?
- **Q-TI-7.** BQ4050 with FET Options[PCHG_COMM] = 1 and no precharge FET: 4.9 says the gauge "enables the hardware 0-V
  charging circuit automatically when the battery stack voltage is below the minimum operation voltage". Can that circuit
  conduct before the woken firmware has run the SUV check of 3.2.1 with SUV_MODE = 1? What ZVCHG Exit Threshold (14.2.7)
  disables 0-V charging, and what does a value of 0 mV do? The cell maker forbids charging a cell below 1.0 V.

To Eaton: Q-E1 to Q-E5 in `FUSE-INTERPRETATION.md` section 7.

To the cell supplier: **Q-S1.** Which Samsung INR18650-35E specification revision (Ver. 1.1 of 9 July 2015, or Version 1.0
applied 2016/04/11, which differ on the storage floor) covers the cells supplied?

## 5. The review route (for the owner)

**What kind of reviewer.** An electronics engineer, independent of this project, with demonstrable Li-ion pack protection
design experience: smart-battery packs with a TI gas gauge (BQ40z50/BQ4050 class) and a second-level protector firing a
chemical fuse; packs of this size (3S to 5S, 10 to 30 A); working knowledge of pack design practice under IEC 62133-2 and
UN 38.3. A battery-pack design house with shipped smart packs fits; a general PCB layout reviewer does not.

**Shortlist (session recommendation under the owner's standing rule of 26 September 2026; from public pages read on 26
September 2026; NOT CONTACTED).** Each page was saved as an HTML snapshot the same day and the quoted words were read back
from those files. The snapshots are third-party web pages the reviewer does not need, so they stay in the session's record
and are not published with the packet; their URLs and sha256 are in `MANIFEST.md` ("Route evidence").

| # | Candidate | Why it fits the profile (their own words) | What to ask them first | Contact channel (published) |
|---|---|---|---|---|
| 1 | **Accutronics Ltd** (an Ultralife company), Unit 20, Loomer Road, Chesterton, Newcastle-under-Lyme ST5 7LB, United Kingdom. https://accutronics.co.uk/ | "specialising in the development and manufacture of 'smart batteries'", with Government and Defence among its markets; "Our in-house mechanical and electrical engineers design batteries and/or chargers" (custom page). Its ND4054HD50 is a "4 series / 1 parallel", "14.4V (nominal)" Li-ion battery whose BMS is "System Management Bus (SMBus) and Smart Battery System (SBS) compliant" with an "impedance tracking fuel gauge", UN 38.3 "Yes" (https://accutronics.co.uk/product/nd4054hd50/): the same architecture class and series count as board P. | whether they take a design-review-only engagement (they are a maker); a shipped design with a second-level protector and a chemical fuse (the ND4054HD50 page names neither, and lists IEC 62133-2 "No") | Tel +44 (0) 1782 566622; https://accutronics.co.uk/contact/ |
| 2 | **Engineering Spirit B.V.**, Dorpsstraat 81, 3941 JL, the Netherlands. https://engineering-spirit.nl/en/ | an electronics development house in the owner's country with its own battery and BMS line: "Certification for UN38.3 and IEC 62133-2:2017" (home page); custom BMS "12 ~ 48V (3 to 16S)", "CAN communication (opt. I2C, LIN, Serial)", "Suitable for UN38.3, UL2849, IEC62133, EN50604-1" (https://engineering-spirit.nl/en/bms/custom-bms-battery-management-system/) | a comparable project with a TI SBS gauge (BQ4050 or BQ40z50 class), a BQ77207-class second level and a chemical fuse; their published BMS is their own CAN design | +31 85 2733462; info at engineering-spirit.nl; "Request a call/meeting", https://engineering-spirit.nl/en/contact/book_a_call/ |
| 3 | **Jauch Quartz GmbH**, battery technology, In der Lache 24, 78056 Villingen-Schwenningen, Germany. https://www.jauch.com/en-INT/products/battery_technology | "Customized battery systems with a battery management system", "from simple cells to intelligent battery packs"; on UN 38.3, IEC 62133 and UL 2054: "We advise you on the different standards and also carry out the corresponding tests in advance" | a review-only engagement; experience with TI gauges and chemical fuses (the page names neither) | batterytechnology@jauch.com; +49 77 20 / 9 45-0 |

A fourth can be found in TI's partner directory (https://www.ti.com/design-development/partner-directory.html), which lets
one "filter by service type, location, product domain, or application"; the page itself names no battery partner, so a
filtered search (battery management, Europe) is the owner's to run if he wants one. The session's recommendation: send the
same request to all three at once (a quote costs nothing, and D-09 requires one before any spend), then choose on two
facts from the answers: a shipped pack with a TI SBS gauge, a second-level protector and a chemical fuse, and a
review-only offer. On published evidence Accutronics is the closest technical match and Engineering Spirit the closest
geographically; Jauch is the third because its page shows the standards work but not the protection architecture.

**What the reviewer needs.** This folder at the commit named in `MANIFEST.md` (public on GitHub, licence CERN-OHL-S-2.0, so
no NDA is needed), the PDFs (KiCad 9 is only needed for the native files), the questions of section 3, and the part
documents cited, which are filed under `v2/vendor/` at the paths `MANIFEST.md` lists ("Documents cited"). No hardware
exists to inspect.

**Release condition (taken by the session under the owner's standing rule of 26 September 2026).** Most of the cited part
documents (the BQ7720700 data sheet SLUSEG7D and its failure-mode analysis SFFS317A, the BQ4050 technical reference manual
SLUUAQ3A, Eaton's ELX1135, the ITV9550 sheet, the AO3400A, 2N7002, PRF and JST PH sheets and TI's EVM guide) are filed
under `v2/vendor/` by stream PKT of the same review, byte-identical to this stream's copies; the two TI E2E answers are
filed by this stream. **The packet is not sent until `python3 v2/docs/review-packets/battery/evidence/check_manifest.py`
prints `RELEASE CHECK PASS` at the commit whose link is sent**: every packet file and every cited document present at its
path with the sha256 `MANIFEST.md` lists. At this stream's own commit, before stream PKT's merge, it prints FAIL on those
rows by design.

**What the owner asks for.** A written report answering each question of section 3 with a classification, a list of
blocking items, and any marked-up schematic pages. Effort and price: TBD by the reviewer's quote.

**How it is sent.**
1. Once the release check above passes, the owner sends the request below, unchanged except for the name, to the three
   candidates of the shortlist (he may drop or add one); the packet link is the GitHub mirror of
   `v2/docs/review-packets/battery/` at the commit the check passed on.
2. Each is asked for a quote, a date and the two facts above.
3. The owner approves one quote (D-09: spend needs his approval).
4. The reviewer's report is saved in `v2/docs/reviews/` and each item is logged and executed like the review of 26
   September.
5. Pack PCB release waits on every blocking item being closed.

### Ready-to-send request (English; placeholders in square brackets; not sent)

Subject: Request for quote: independent review of a 4S Li-ion pack protection design (prototype)

Dear [name],

I am building MeshSat, an open-hardware field communications kit (a prototype; nothing has been built yet). Before the
battery pack is built I want its protection design reviewed by a qualified engineer, and I would like a quote from you.

The pack is 4S3P Samsung INR18650-35E, about 145 Wh, 10 A typical and 18 A peak, in a sealed case. The protection board
uses a TI BQ4050 gauge with high-side charge and discharge FETs, a TI BQ7720700 second-level protector firing an Eaton
SCF9550-30-05 chemical fuse, a PTC element at the FETs and a 25 A blade fuse. The charger is a TI BQ25731 on another board.

The review packet, with the schematic PDF, the native KiCad 9 files, the bill of materials, the protection architecture,
the fault-state tables and sixteen specific questions, is here:
[link to v2/docs/review-packets/battery/ at commit ...]

What I am asking for:
- a written answer to each question in section 3 of REVIEW-REQUEST.md (acceptable, acceptable with a change, or blocking);
- a list of the items you would block the pack board's release on;
- your quote, your earliest date and an estimate of the effort.

The design has so far been reviewed only by AI tools; that is why I want a human specialist. The files are public
(CERN-OHL-S-2.0), so no NDA is needed. I would publish your report in the repository only with your consent.

Kind regards,
[owner's name]
[contact details]
