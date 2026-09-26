# The chemical fuse F2 in the assembled pack: rating interpretation, actuation, interruption and arming

MeshSat field kit V2, MESHSAT-1357, review stream BAT, 26 September 2026. Prototype design: nothing is built, no fuse has
been fitted, fired or measured. Labels as in `PROTECTION-ARCHITECTURE.md` (VERIFIED, INFERRED, TBD).

**Part:** Eaton Bussmann SCF9550-30-05, a three-terminal self-control fuse: 30 A, rated voltage 62 Vdc, heater DCR 4.8 to
8.0 ohm, heater operating voltage 10.5 to 23.5 V, breaking capacity 80 A, fuse DCR 1.0 to 2.5 mohm, 4 to 5 cells in series,
cURus (VERIFIED, ELX1135 page 2). F2 on board P, between the 25 A blade F1 and the charge FET Q1 (`gen_sch_p.py:288-289`).
**Document:** Eaton Technical Data ELX1135, effective December 2021 (page 1) and January 2022 (pages 2 to 5),
`v2/vendor/battery/eaton-scf9550-elx1135.pdf`, sha256 3ecc2424...158e, the URL named in the review (R2); the file is the
Wayback capture of that URL, byte-identical to LCSC's copy (round-4 SOURCES record); eaton.com did not answer this host on
26 September 2026, so its currency is not re-checked (stream PKT's SOURCES.yaml entry for F2).

## 1. Every environmental entry of ELX1135, and what it means for the pack

ELX1135 page 4, "General specifications", read in full (VERIFIED):

| Entry (verbatim) | Reading for the assembled pack |
|---|---|
| "Operating temperature: -20 C to +60 C" | **The governing limit for the mounted part.** Soldered into board P, F2 is always in circuit: its element carries the pack current whenever the FETs conduct, and its heater hangs on a live FET, in use and in storage alike. |
| "Storage temperature: -10 C to +40 C < 90% RH" | A storage condition with a humidity bound. |
| "Storage duration: 1 year" | With the line above, the shelf condition of the unmounted part in its packaging. Nothing on the page ties it to the mounted part, and a one-year duration with a humidity bound is the form of a shelf-life and solderability condition. **This reading is the session's interpretation, not a statement by Eaton** (question Q-E1, section 7). |
| "High temperature: +105 C @ 1000 hours" | A qualification exposure. Eaton publishes no acceptance criterion for it (no resistance change limit, no statement that the element or heater still performs). It is **not a rating**, and nothing here relies on it. |
| "Humidity: +85 C @ 85% RH @ 500 hours" | As above: an exposure without published criteria. |
| "Low temperature: -40 C @ 500 hours" | As above. |

The round-4 fix-up read the exposures as covering TEST-PLAN E3's +71 C and E4's -33 C storage. **That reading is
withdrawn** (the review, section 2: "neither the operating maximum nor the stress-test entry alone establishes +71 C
assembled-pack suitability"); `gen_sch_p.py:263-277` says so now.

### 1.1 The pack's temperatures against the -20 to +60 C operating range

| Condition | Temperature at F2 | Against -20 to +60 C | Basis |
|---|---|---|---|
| Kit storage envelope | -20 to +45 C for 3 months | inside | `OPERATING-ENVELOPE.md:141`; the cells bound it (Samsung Ver. 1.1 3.13) |
| Pack's own storage limit | +60 C for 1 month; -20 C (Ver. 1.1) or 0 C (2016 Version 1.0) | at the limit | cells, `PROTECTION-ARCHITECTURE.md` section 1 |
| Use, one module above +35 C ambient | air about +50 C (40 C plus 10 K, D-02b) plus F2's own heating | inside, with margin TBD | F2 dissipates 18 x 18 x 1.0 to 2.5 mohm = 0.32 to 0.81 W at the 18 A peak (INFERRED from ELX1135's fuse DCR); board P's other dissipation at the peak (Q1, Q2, R10, F1) adds to the board temperature; no measurement exists |
| Use at the cells' 60 C discharge limit | about 60 C plus self-heating | **at or above the limit** | the primary stops discharge at 60 C cell surface (`PRIMARY-CONFIGURATION.md`), so F2 sits above 60 C only while the board is hotter than the cells; TBD by the thermal test |
| E3 +71 C storage, E3 +55 C operation, E4 -33 C storage | not applied to the pack | n/a | reconciled for the pack at its cells' limits (`SECONDARY-OT-DECISION.md` section 5) |

**Interpretation (the session's, under the owner's standing rule of 26 September 2026):** the SCF9550-30-05 fits the
assembled pack as long as the pack is held within its cells' rating, which the reconciled test plan does. Two residuals
remain and are stated rather than assumed away:

1. **No current derating is published**, at any temperature (ELX1135 has no derating curve). At 60 % of its 30 A rating
   (18 A peak, 10 A typical) the risk of a nuisance opening is judged low, not proven. The thermal test reads F2's case
   temperature at the pack's hot limit (open item O-8 of the round-4 record; bench list O-9).
2. **The hot corner of use can put F2 at or above 60 C** if board P runs warmer than the cells. Eaton's behaviour above
   60 C (nuisance opening, or a heater that opens more slowly) is not published: question Q-E2.

### 1.2 Alternatives evaluated

| Part | For | Against | Verdict |
|---|---|---|---|
| Littelfuse ITV9550L1430 (4 cells, 30 A, 80 A breaking, heater 6.3 to 9.3 ohm, operating voltage 11.1 to 18.4 V) | publishes a derating (34 A at 25 C, 30 A at 40 C, 25 A at 60 C) and acceptance criteria for its aging runs ("No structural damage and functional failure") | **operating temperature -10 to +65 C** fails the use envelope's -20 C; storage 0 to 35 C for 3 months; heater window 11.1 V minimum (2.78 V per cell), narrower than Eaton's 10.5 V | not taken; the fallback if Eaton cannot answer Q-E2 and the thermal test shows F2 above 60 C (ITV9550 30A datasheet revised 01/22/20, `v2/vendor/battery/littelfuse-itv9550-30a.pdf`, sha256 018e0d53...) |
| Eaton SCF9550-45-04 (4 cells, 45 A, 120 A breaking, fuse 0.5 to 1.5 mohm) | lower self-heating (0.16 to 0.49 W at 18 A), 50 % more breaking capacity, same page 4 | heater operating voltage **13.0 to 18.4 V**, 3.25 V per cell minimum: an open wire or over-temperature event on a pack below about 13 V may not open it | not taken (ELX1135 page 2) |
| Dexerials SFK-1830A | the same electrical figures | no published temperature range or land (round-4 RP-04) | not taken |
| Littelfuse ITV4030, Prosemi DHC45 | | 15 A and -10 C; a two-terminal part | refused in round 4 (`gen_sch_p.py` round-4 record) |

## 2. Actuation: will the heater open F2 when asked?

The heater is fed from the cells through F1 and F2's own element, whatever the FETs do (TI's placement, SLUSC67B Figure
21), and switched to ground by Q3 (AO3400A).

| Quantity | Value | Basis |
|---|---|---|
| Heater operating voltage | 10.5 to 23.5 V, opening within 60 s maximum | ELX1135 page 2 (VERIFIED) |
| Pack voltage per state | 16.8 V full; 14.4 V nominal; 10.6 V at the 2.65 V cut-off; 10.0 V at the primary's CUV; 9.0 V at the secondary's UV | cell figures x 4 (INFERRED) |
| Where the heater is not rated | below 10.5 V, 2.63 V per cell | INFERRED |
| Heater current | 1.3 to 3.5 A (10.5 V / 8.0 ohm to 16.8 V / 4.8 ohm) | INFERRED |
| Q3 gate, U1 FUSE alone driving (COUT inactive, sinking) | 3.78 V | `gen_sch_p.py` fuse-drive comment (round-4 RP-07, corrected) |
| Q3 gate, U2 COUT alone driving | 4.25 V at 88 uA, inside COUT's 100 uA VOH condition | the same |
| AO3400A threshold, RDS(on) | VGS(th) 0.65 to 1.45 V; under 48 mohm at 2.5 V | AOS Rev 3.1 |
| Q3 dissipation while the heater runs | about 0.5 W at 3.5 A, for up to 60 s | INFERRED; RthJA 90 C/W for t under 10 s, 125 C/W steady (AOS Rev 3.1) |
| U1 FUSE drive duration | Fuse Blow Timeout, **default 30 s**, must be at least 60 s | SLUUAQ3A 14.2.2.6; `PRIMARY-CONFIGURATION.md` |
| U2 COUT duration | as long as the fault persists (latch disabled) | SLUSEG7D section 4, 7.3.7 |
| Which events fire F2 | U2: OV, open wire, OT, oscillator. U1: any permanent failure mapped in Permanent Fail Fuse A to D (**default: none**) above Min Blow Fuse Voltage, or a FET failure at any voltage | SLUSEG7D Table 7-1; SLUUAQ3A 3.1, 14.2.2 |
| Why UV does not fire F2 | a block at the secondary's 2.25 V is at 9.0 V, below the heater's rated 10.5 V; UV is recoverable by charging, so U2's DOUT holds Q2 off instead | round-4 RP-02 |

Findings: the actuation margin is good for over-voltage (16.8 V and above) and adequate for open wire or over-temperature
on a pack above 10.5 V. Below 10.5 V, which the pack only reaches after the primary's CUV has already opened the discharge
FET, the fuse is not guaranteed to open (Q-E3).

## 3. Interruption and the prospective fault current

**Prospective fault at board P (INFERRED).** The cell datasheet gives only a maximum AC impedance, 35 mohm at 1 kHz
(Samsung 7.4, both revisions). Four series groups of three cells: at most 4 x 35 / 3 = 46.7 mohm, plus about 15 mohm of
strip, lead and board copper (`pcb_energy_chain.yaml`, PACK_CELLS basis), so at least about 270 A at 16.8 V into a bolted
short. The datasheet gives no MINIMUM impedance, so the upper bound cannot be read from it: the chain's 480 A is a margin
figure, **TBD** by a measured DC resistance of the purchased cells (it moves F1's and the FETs' duty in section 4).

| Element | Rating | Against 270 to 480 A | Basis |
|---|---|---|---|
| F2 SCF9550-30-05 | breaking capacity 80 A | **not rated to interrupt it**; F2 is not meant to clear a hard short | ELX1135 page 2 |
| F1, 25 A MINI blade (Littelfuse 297 in the Keystone 3568 holder) | 1000 A interrupting at 32 VDC; typical I2t 625 A2s; cold resistance 2.36 mohm; -40 to +125 C | interrupts it; melting about 2.7 ms at 480 A to 10.9 ms at 240 A (adiabatic, I2t / I2) | `v2/vendor/keystone/littelfuse-297-ficcorp.pdf`; Keystone 3568 takes "Littelfuse Mini 297 or 997 series/Bussmann ATM" (`v2/vendor/keystone/M65p42.pdf`) |
| Q1, Q2 CSD17570Q5B | IDM 400 A (pulse 100 us or less, duty 2 % or less); SOA Figure 10 | see section 4 | SLPS471D |

**The coordination that must hold:** in a hard short the gauge's AFE opens the FETs first (ASCD). If the FETs have failed
closed, F1 must open before F2's element does, because F2 cannot break the current. ELX1135 publishes no melting I2t or
time-current curve for F2's element (only "200 % of current rating, 60 seconds maximum"), so **the order F1 before F2 is
not proven** (Q-E4; round-4 R-m6 and O-13 carried it; it stays open).

**A record defect found on the way (BAT-F04):** `pcb_energy_chain.yaml` (stages PACK_CELLS, PACK_LEAD, DOCK_ENTRY and board
A's fuse) and `pcb_pack_protection.yaml:74` describe F1 as a "25 A ATOF blade" with the Littelfuse 287 ATOF figures
(I2t 1000 A2s, `v2/vendor/battery/littelfuse-287-atof.pdf`). The ATOF is the regular ATO size; the Keystone 3568 holder the
boards are drawn with takes the MINI size. The fuse that fits is the Littelfuse 297 (MINI) 25 A: the same 1000 A at 32 VDC
interrupting rating, a lower typical I2t (625 A2s). The generators already say "mini blade" (`gen_sch_p.py:246`,
`gen_sch_e.py:194`). The yaml figures and the part row for F1 (O-3: C4661 marked WRONG_MODEL) are for their owners.

## 4. FET and gate behaviour

| Item | Value | Basis |
|---|---|---|
| Gate drive on | CHG and DSG 10.5 to 12 V above BAT and PACK (4.92 to 18 V), through R16 and R18 5.1 kohm | SLUSC67B 6.18; `gen_sch_p.py:291` |
| Gate drive off | within +-0.4 V of the source reference; fall time 40 to 300 us specified into 4.7 nF through 5.1 kohm | SLUSC67B 6.18 |
| FET gate load | Ciss 10.4 nF typical (13.6 maximum), Qg 93 nC at 4.5 V, Qgd 34 nC | SLPS471D |
| UV hold | Q5 pulls DSG_G to VSS: VGS(Q2) = minus V(PACK_P), 3.2 V from the 20 V gate rating at 16.8 V; charging continues through Q2's body diode | `gen_sch_p.py:480-502`; round-4 RP-02 |
| Q5 leakage into the DSG charge pump | IDSS 80 nA maximum at 25 C, none stated above | JCET 2N7002; bench O-9 |

**Turning off a hard short (finding BAT-F07, INFERRED, for the reviewer).** The AFE's short-circuit delay is about 183
to 244 us plus up to 160 us detection (SLUSC67B 6.32 at the steps near 60 A). The FETs then turn off through 5.1 kohm:
at a Miller plateau of about 3 to 4 V the gate discharges at roughly 0.6 to 0.8 mA, so Qgd's 34 nC takes about 40 to 60 us,
and SLUSC67B's own fall-time figure for a smaller 4.7 nF load is up to 300 us. During that time VDS rises along the fault's
load line. With a source resistance of about 35 to 62 mohm (section 3) the peak dissipation is 16.8 V squared over four
times that resistance, about 1.1 to 2.0 kW, reached at about half the pack voltage, 8.4 V, where the fault current is
about 135 to 240 A. SOA Figure 10 of SLPS471D (single pulse, case at 25 C, read from the figure at 300 dpi, so plus or
minus about 20 %) allows about 215 A at 8.4 V for 10 us and about 57 A for 100 us; interpolated on log time, about 85 A
for 50 us. A turn-off lasting 40 to 60 us therefore passes the load line's peak at about 1.6 to 2.8 times the SOA current
for its duration; the triangular shape of the real power pulse relieves some of that, so the result is **marginal to
outside the SOA, not established either way**. Before the turn-off, the fault current (270 to 480 A for up to about 400
us) is at or above IDM's 400 A for longer than its 100 us condition. If the FETs do not survive, a hard short ends with a
FET failed short and F1 clearing it, which is the case the blade exists for, and in which F2's coordination (section 3)
matters. Options for the reviewer: a faster discharge-gate turn-off (a PNP or diode
speed-up on DSG, as high-current pack designs use), paralleled FETs, or accepting F1 as the device that clears a hard short
and designing the rest for it (question Q-P6).

## 5. The arming jumper JP1

JP1 is a solder jumper between FUSE_G and Q3's gate (FUSE_GQ), **open as built** (`gen_sch_p.py:476`), with R32 1 Mohm
holding Q3 off meanwhile. TI's EVM ships its fuse unfitted and warns that the second-level protector "could blow the fuse"
while cells are connected (SLUUBF9 2.5.2); SLUSEG7D 8.1.2.1 says the same of cell attachment.

**What an unarmed pack has and lacks.** With JP1 open, no event can open F2. COUT still reaches U1's FUSE pin through R30,
so a secondary OV, open wire or over-temperature still opens both FETs through U1's 2LVL check if the image enables it
(SLUUAQ3A 3.16), and DOUT still holds Q2 off for UV, open wire and OT. What is lost is every PERMANENT disconnect, including
the one that matters when a FET has failed short. A pack must not leave commissioning unarmed. The gauge cannot see JP1;
the commissioning record and a label are the control (TBD, pack build).

**Commissioning order** (round-4 O-9 and R-B1, extended by this stream; all steps NOT_YET_TESTED):

1. Board P assembled with F1 and F2 fitted, JP1 open, the cell block not yet connected. Prove J_TS2's NTC is in circuit by
   resistance, TP15 to TP8 (PACK_N, joined to VSS through R10), with J_TS2 plugged and then unplugged: about 6.5 kohm
   against about 18.0 kohm at 25 C (`SECONDARY-OT-DECISION.md` section 4). Leave J_TS2 plugged. Then connect the cell
   block (any order: SLUSEG7D 8.1.2.1).
2. Write the golden image and read it back (the data-flash verification D-15 names; content per `PRIMARY-CONFIGURATION.md`):
   a. first read the fresh device's whole data flash and archive it with the pack's serial number: this records the
      defaults TI actually ships for every word the TRM states two ways (`PRIMARY-CONFIGURATION.md` section 1a), and it
      supplies the values of the rows that page leaves to the fresh device (VIMR, VIMA, AFER Delay Period);
   b. write every word of that page's section 2 explicitly, including those whose required value equals every statement
      of TI's default;
   c. reset the gauge (Mfg Status Init is taken only at a reset or seal, SLUUAQ3A 11.1), then compare every word on the
      read-back and read ManufacturingStatus() (13.1.39): FET_EN, PF_EN and FUSE_EN = 1. In particular DA Configuration
      (4 cell), Temperature Enable and Mode, Protection Configuration, Enabled Protections C (HWDF = 1), Enabled PF A to D
      and the Open Thermistor deltas, whose TI defaults are wrong for this pack or stated two ways (BAT-F05, BAT-F13).
3. U2 customer-test-mode checks of COUT and DOUT for OV, UV and open wire (SLUSEG7D 7.4.3), JP1 still open.
4. TP15 with the cells on, by scope against TP8, triggered on the TS bias pulse: its top is 0.246 of the internal reference
   with J_TS2 plugged and 0.474 unplugged at about 25 C (`SECONDARY-OT-DECISION.md` section 4). A DC multimeter reading here
   is not a valid check: at the device's 2 uA typical supply current the TS bias cannot be continuous (SLUSEG7D 6.5 ICC;
   INFERRED, its timing is asked in Q-TI-1). At service, on an imaged pack, this scope reading is the check to use: the
   resistance method needs J_CELL unplugged, and a tap reconnected one pin at a time can raise U2's open-wire COUT, which
   the gauge reads on its FUSE pin as a 2LVL permanent fail once the image enables it (SLUUAQ3A 3.16).
5. RT1 present and not shorted: V(PTCEN) minus V(PTC) is about 2.9 mV at 25 C (290 nA typical into about 10 kohm; SLUSC67B
   6.23; Murata DM-SA16-E056), against 0 for a short (method TBD, bench).
6. TP11 (FUSE_G) read low with the cells on: COUT inactive and FUSE inactive.
7. Close JP1 with solder.
8. Verify the closure: continuity TP11 to TP14 with the meter's COM (black) lead on TP14 and the red lead on TP11, after
   confirming the meter's source polarity and open-circuit voltage (under 12 V) on the range used. With the other
   polarity a closure that did not wet puts the meter's voltage on Q3's gate and can open F2 on a healthy pack (round-4
   R-B1). Do not use TP14 to TP8 (it drives IC pins below VSS when JP1 is closed).

## 6. Summary for the reviewer

| Question from the review | Answer here | State |
|---|---|---|
| Does the SCF9550's +60 C rating fit +71 C storage? | It does not, and it no longer needs to: the pack is bounded by its cells at +60 C and the +71 C margin is reconciled for the pack | interpretation taken; Q-E1, Q-E2 to Eaton |
| Actuation | heater rated from 10.5 V; good at over-voltage; not guaranteed below 10.5 V; gauge's fuse timeout default too short | requirements set (`PRIMARY-CONFIGURATION.md`) |
| Interruption capability versus prospective fault | F2 80 A cannot break a hard short; F1 1000 A can; the order F1 before F2 is unproven | open, Q-E4 |
| FET and gate behaviour | a hard-short turn-off through 5.1 kohm is marginal to outside the FET SOA, not established either way | open, BAT-F07, Q-P6 |
| Commissioning jumper | purpose, what an unarmed pack lacks, the order and the polarity of the check | procedure, bench |

## 7. Questions for Eaton (prepared, not sent; the owner sends or forwards to the reviewer)

- **Q-E1.** Does the ELX1135 line "Storage temperature: -10 C to +40 C < 90% RH / Storage duration: 1 year" apply to the
  part in its packaging before assembly only, or also to a part soldered into a battery pack that is stored?
- **Q-E2.** What is the SCF9550-30-05's behaviour above +60 C: is there a current derating, and does the heater's
  opening time or the element's holding current change? Is there a derating curve not in ELX1135?
- **Q-E3.** Below the 10.5 V operating voltage, does the heater still open the fuse, and in what time, for example at 9.0 V
  and 10.0 V?
- **Q-E4.** What are the melting I2t and the time-current characteristic of the fuse element (not the heater), and what
  prospective current and voltage was the 80 A breaking capacity tested at? We need to know whether a 25 A MINI blade
  (Littelfuse 297, I2t 625 A2s typical) in series opens before the element on a 250 to 500 A fault at 16.8 V.
- **Q-E5.** What are the pass criteria of the +105 C 1000 h, 85 C / 85 % RH 500 h and -40 C 500 h runs?
