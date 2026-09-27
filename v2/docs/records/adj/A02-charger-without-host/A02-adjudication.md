# A02 charger-without-host: adjudication (MESHSAT-1357, round 2)

Adjudicator A02, 25 Sep 2026. Tree read at main `82dd1e4d`; nothing in it was edited, no gate or suite was run, the box was not used.
Everything here is under `scratchpad/adj/A02-charger-without-host/`.

## Question

Does the BQ25731 charge without a host? W2 says ChargeCurrent is 0 A at POR and the 175 s watchdog resets it to 0 A. W5 said
256 mA; the challenger refuted W5 because SLUSE66A 9.6.2 contradicts itself. Also settle W2 F-CH-01 (does board A's
CELL_BATPRESZ strap select 2S or 4S) and F-CH-03 (no BATFET, no TS pin).

## Sources read

| source | identity | status |
|---|---|---|
| BQ25731 datasheet held | `v2/vendor/ti/bq25731-datasheet.pdf`, SLUSE66A (June 2020, revised January 2021), 105 pages, sha256 `3e5e927f...58973`, added in `908ede32` | read in full on POR, watchdog, ChargeCurrent, ChargeVoltage, CELL_BATPRESZ, SYSOVP, BATOVP, pins, register defaults, application |
| BQ25731 datasheet current at TI | `https://www.ti.com/lit/ds/symlink/bq25731.pdf`, fetched 2026-09-25T21:27Z, HTTP last-modified 04 Sep 2026 | **byte-identical** to the held copy (same sha256): SLUSE66A is TI's current revision |
| BQ25730 datasheet (sibling part, same register map, has a BATFET) | `https://www.ti.com/lit/ds/symlink/bq25730.pdf`, SLUSE65A (February 2021, revised January 2024), fetched 2026-09-25, sha256 `e41ef289...57153f` (`bq25730-ref.pdf` here) | read at the same sections, used only to tell BQ25731-specific text from inherited text |
| TI E2E thread 1316778 "BQ25731 ChargeCurrent Start Up Behavior" | `https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1316778/bq25731-bq25731-chargecurrent-start-up-behavior`, question 23 Jan 2024, TI__Expert reply 23 Jan 2024 (page datetime 2024-01-23T21:39Z), fetched 2026-09-25 (`e2e/1316778.html`, `.txt`) | read |
| TI E2E threads 1324205, 1190474, 1312308, 1117992 | same forum, 2022 to 2024, fetched 2026-09-25 (`e2e/`) | read; hashes in `SHA256SUMS` |
| Board A generator | `v2/ecad/tools/gen_sch_a.py` at `82dd1e4d`, lines 161, 314 to 350 | read |
| Board A committed netlist | `v2/ecad/pcb-a-power-a23/out/pcb-a-power.net`, last commit `0d1e2ef6` (20 Sep 2026) | parsed for R26, R27, R17, F1, U3 and every node of VIN_RAW, VBUS20, CH_ACN, CH_SRP, CELL+ |
| PCA9555 datasheet | `v2/vendor/ti/ti-pca9555.pdf`, SCPS131J | read on the internal pull-up only |

## Verdict in one paragraph

**The BQ25731 itself does charge without a host, at a 256 mA register default, and its watchdog does not stop it.** TI's
applications engineer answered the exact contradiction on 23 Jan 2024: "Looks like there is a mistake in the description.
The POR value is indeed 256mA. You can take a look at BQ25730 which provides POR charge current of 0mA." The datasheet
diff confirms it: every sentence in SLUSE66A that says 0 A is copied word for word from the BQ25730 datasheet, and every
sentence TI edited for the BQ25731 says 256 mA. So W2's "0 A at POR, and the watchdog resets it" is **refuted** as a
statement about the part. W5's 256 mA value is right, but it was not VERIFIED from the datasheet alone, as the challenger
said. **On board A as designed, though, no charge reaches the pack with or without a host**, so W2's conclusion (PANEL.md's
"a kit with a crashed panel still charges" is false) **stands on other grounds**. (1) F-CH-01 is **VERIFIED**: the strap
is 2S (40.0 %), so SYSOVP is 12 V and BATOVP about 8.74 V, below any 4S pack voltage. (2) Once the strap is fixed, the
256 mA passes through the charge shunt R17, and every kit load sits on the pack side of R17 (F-CH-03, **VERIFIED**). The
shore therefore delivers at most 256 mA (3.1 to 4.3 W) into load plus pack together. Every declared operating mode draws
more than that, so the pack discharges net while shore is connected and no host is running. The only host-free path that
charges usefully is a host that disabled the watchdog before it stopped. The charger then keeps its last ChargeCurrent
until the adapter is removed, which clears it.

## 1. ChargeCurrent at POR and after the watchdog: every statement, and where it comes from

SLUSE66A page numbers are the PDF's. "Inherited" means the same words appear in BQ25730 SLUSE65A, whose POR value is 0 A.

| # | SLUSE66A statement | page | value | in BQ25730 SLUSE65A? |
|---|---|---|---|---|
| 1 | 9.6.2 header "ChargeCurrent Register (I2C address = 03/02h) [reset = 0080h]" | 45 | 256 mA | no: SLUSE65A 8.6.2 header is `[reset = 0000h]`: **BQ25731-specific edit** |
| 2 | Table 9-11, bit 7 "Charge Current, bit 1", RESET **1b**, "Adds 256 mA" | 45 | 256 mA | no: SLUSE65A has RESET 0b: **BQ25731-specific edit** |
| 3 | 9.3.21.1 "When watchdog timeout occurs ... ChargeCurrent() resets to 256 mA" | 33 | 256 mA (watchdog) | no: SLUSE65A says "resets to 0 A" and adds "New non-zero charge current value has to be written ... to resume charging": **BQ25731-specific edit** |
| 4 | 9.4.1 "(WDTMR_ADJ=00 should be configured to disable watch dog timer, otherwise charge current will reset to 256 mA after watch dog timer expires)" | 35 | 256 mA (watchdog) | no: SLUSE65A 8.4.1 ends at "setting ChargeCurrent() to zero.": **BQ25731-specific addition** |
| 5 | Table 9-8 WDTMR_ADJ "the charger will be suspended by setting the REG0x14() to 0 mA 256 mA (BQ25731)" (rendered exactly so, page image `p42_wdt.png`) | 42 | 256 mA (watchdog), edit residue | SLUSE65A reads "to 0 mA.": **BQ25731 edit with the old value left in** |
| 6 | 9.6.2 text "Upon POR, ChargeCurrent() is 0 A. Below scenarios will also reset Charge current to zero: ... Watch dog event is triggered." | 45 | 0 A (POR, watchdog, adapter removal, CELL low, RESET_REG, ChargeVoltage 0) | **yes, word for word** (SLUSE65A 8.6.2): inherited |
| 7 | Figure 9-15 caption "[reset = 0000h]" | 45 | 0 A | yes (SLUSE65A Figure 8-17): inherited. This datasheet's captions disagree with their own headers in three other places (ChargeOption1 3F00h against 3300h, IIN_HOST 2000h against 4100h, Vmin Active Protection 006Ch against 0070h), so a caption carries the least weight |
| 8 | 9.6.3 "After CHRG_OK goes high, the charge will start when the host writes the charging current to ChargeCurrent() register" | 47 | implies 0 until written | yes, word for word: inherited |

Supporting, not decisive: Table 9-9 CHRG_INHIBIT (page 44) "When this bit is 0, battery charging will start with valid
values in the ChargeVoltage() register and the ChargeCurrent register", and its POR default is 0b (enable charge).
9.3.1 (page 24) loads "the default value of ... ChargeCurrent register (Reg0x03/02)" at power-up from the CELL
configuration. AUTO_WAKEUP_EN (page 61) defaults to 0b, so the 128 mA wake-up charge is not a host-free path.

TI E2E 1316778 (23 Jan 2024): the asker lists statements 1, 3 and 6 as the contradiction. TI__Expert Md Munir Hasan
answers "there is a mistake in the description. The POR value is indeed 256mA" and points to the BQ25730 for a 0 mA POR.
In the same thread he adds that "you can use the CELL_BATPRESZ=0V at startup with BQ25731 as well because it will disable
battery charging". E2E 1324205 (Feb 2024, a user report and not TI's) describes a BQ25731 charging at about 180 to
185 mA "at the default value" before the user's register writes took effect. That matches a live 256 mA default with the
loose accuracy of the lowest code (SLUSE66A 8.5, page 10, specifies ICHRG_REG_ACC only down to 1024 mA, at -18 to +21.5 %;
the 256 mA code has no stated accuracy).

**Finding A02-1 (INFERRED, strong).** The BQ25731 powers up with ChargeCurrent = 0080h, which is 256 mA with the 5 mOhm
RSR the POR default RSNS_RSR = 1b assumes (page 59; board A's R17 is 5 mOhm, so that assumption holds). With CHRG_INHIBIT
= 0b it charges at that rate without a host write. The watchdog (175 s default, 140 to 210 s, page 18) returns
ChargeCurrent to 256 mA, not 0 A. The status is INFERRED rather than VERIFIED for two reasons: the datasheet stays
self-contradictory, and the resolving statement is a TI engineer's forum answer, not a datasheet revision (TI still
serves SLUSE66A as current, fetched 25 Sep 2026) and not a bench measurement. It is owed at bring-up: read
REG0x03/02 at power-up and after a 175 s silence, and measure the SRP-SRN current.

**Finding A02-2 (UNRESOLVED).** It is not settled what an adapter removal (STAT_AC invalid) resets ChargeCurrent to on the
BQ25731. Statement 6's list says zero, but that is the same inherited paragraph TI called a mistake for POR, and TI did
not address this case. Effect: whether a kit whose host disabled the watchdog and then crashed still charges after a
shore unplug and replug: at 0 A, at 256 mA, or at the last host value. It is owed at bring-up.

## 2. W2 F-CH-01, the cell-count strap: **VERIFIED, 2S**

- Netlist: R26 60.4k 1% from `/CH_VDDA` (U3 pin 7) to `/CH_CELL` (U3 pin 18); R27 40.2k 1% from `/CH_CELL` to GND
  (`pcb-a-power-a23/out/pcb-a-power.net` @ `0d1e2ef6`; generator `gen_sch_a.py:350` @ `82dd1e4d` is identical, whose own
  label reads "4S per Table").
- Ratio 40.2 / 100.6 = **39.96 %**, and 39.48 to 40.44 % at the 1 % extremes (`strap_calc.out`). SLUSE66A 8.5 (page 18):
  VCELL_2S 35 / 40 / 48.5 %, VCELL_3S 51.7 / 55 / 65 %, VCELL_4S 68.4 / 75 / 81.5 %. The strap sits wholly inside the 2S
  window. It even matches TI's own 2S example (Figure 10-1, page 83: 350k over 250k = 41.7 %, "8400 mV for 2s battery").
- 2S loads ChargeVoltage 8.400 V, SYSOVP 12 V and VSYS_MIN 6.6 V (Table 9-2, page 26). SYSOVP rises at 11.7 / 12 / 12.2 V
  (page 14) and "latches off the converter" (9.3.21.4, page 34). BATOVP rises at 102.3 / 104 / 105 % of 8.4 V, which is 8.59
  to 8.82 V (page 14), and with charge enabled "converter should shut down" (9.3.21.5, page 34). VSYS (U3 pin 22) is
  `/CH_SRP`, joined to `/CELL+` through the 5 mOhm R17, so VSYS sits at the pack voltage. **No register moves SYSOVP**: it
  is set from the CELL pin when the converter starts. A host that writes ChargeVoltage = 16.8 V therefore still hits the
  12 V latch. Result: no charge into a 4S pack above about 12 V, with or without a host. W2's statement holds exactly.
- Nuance W2 did not state: **swapping R26 and R27 is not a fix**. 60.04 % (59.56 to 60.52 %) selects **3S** (12.6 V). W2's
  proposed 13.3k over 40.2k gives 75.14 % (74.76 to 75.51 %), inside the 4S window.

## 3. W2 F-CH-03, no BATFET and no TS pin: **VERIFIED**, with a consequence W2 understated

- No BATFET is the part's architecture: Features "No battery MOSFET" (page 1), and the Device Comparison Table "BATFET Power
  Path: No" (page 4). The generator says so itself (`gen_sch_a.py:314`).
- No thermistor input: the pin table (pages 5 to 7) has no TS or NTC pin, and the whole datasheet has no occurrence of
  thermistor, TS pin, JEITA or NTC. Its only temperature function is junction TSHUT (9.3.21.9). So "the pack thermistor on
  the charger's JEITA input already does in hardware" (`OPERATING-ENVELOPE.md:89`), CONOPS "HW (charger TS input)" (W1
  worktree `v2/docs/CONOPS.md:137`) and PANEL.md:155's "pack thermistor (read by the BQ25731 over the bus)" are all false
  for this part. PANEL.md:155 is doubly false: the BQ25731 is an I2C **target** at 6Bh (pages 4 and 35), not an SMBus
  charger at 09h, so it reads nothing over the bus.
- Topology (netlist @ `0d1e2ef6`): `/CH_SRP` = {Q10.5, C23 to C25, R149, **R17.1**, U3.22}; `/CELL+` = {**R17.2**, F1.1,
  J_CP1 to J_CP4, R1, R148, TP14}; `/VBAT` begins at F1.2. Every kit load sits on VBAT, the pack side of R17. TI's
  application puts the system on VSYS, the converter side of RSR (Figure 10-1 and 10.1, page 83: "all capacitors connected
  to VSYS net can be counted including the input capacitor of the next stage converters"). A TI__Expert on E2E 1190474
  (Jan 2023) puts it as "the system gets connected directly to the battery", with only RSR between them.
- **Consequence (VERIFIED from netlist and datasheet, no bench):** the only path from shore or vehicle to any load is
  VIN_RAW, U2 (FE), VBUS20, R16, the charger's bridge, CH_SRP, R17, CELL+, F1, VBAT. VIN_RAW and VBUS20 have no other
  consumer toward VBAT. The charger's ICHG loop regulates SRP-SRN, so **shore can deliver no more than ChargeCurrent into
  load plus pack together.** With a 2S strap it delivers nothing above about 12 V: on board A as designed, the kit runs from
  its pack while shore is connected, host or no host.

## 4. So, does board A charge without a host?

| state | host | pack gets | basis |
|---|---|---|---|
| as designed (2S strap) | any | nothing above about 12 V pack; the converter latches (SYSOVP) or shuts down (BATOVP), and CHRG_OK goes low | section 2, VERIFIED |
| strap fixed to 4S, host never ran or has stopped (watchdog enabled) | none | the charger supplies 256 mA nominal (3.1 / 3.7 / 4.3 W at 12 / 14.4 / 16.8 V) through R17; the pack gets 256 mA **minus** the residual VBAT load, which is negative for any load above 256 mA | A02-1 plus section 3, INFERRED |
| strap fixed, host wrote ChargeCurrent and WDTMR_ADJ = 00b, then crashed | none | the host's value continues until adapter removal (then A02-2), CELL_BATPRESZ low or POR | 9.4.1 (page 35), 9.6.2 (page 45), INFERRED |
| strap fixed, CHG_INHIBIT gate undefined at power-up | none | possibly nothing: U27 (PCA9555, 0x21) pin 4 is an input with an internal pull-up at POR ("pulls the I/O to a default high when configured as an input and undriven", SCPS131J 8.1; IIL up to -100 uA), against R21 100k to ground, so Q6 (2N7002) sees about 1.6 V, and Q6 conducting pulls ILIM_HIZ below 0.4 V (HiZ) | W5 F1; 2N7002 VGS(th) datasheet not held: TBD |

Every mode W2 declares (provisional, owner condition 2) is far above 256 mA: reduced about 21 W, M1 29.4 W. The residual
load of a kit whose panel controller is hung is declared nowhere: **TBD**. So PANEL.md:155's "a kit with a crashed panel
still charges" and CONOPS:137's "(by design)" are false as wired. The fix is an engineering choice for W2 (a W2 or W5
decision, not an owner one; no money or claim changes). The options: move the kit loads to the VSYS side of R17 so
ChargeCurrent governs the pack alone and DPM gives the system priority (TI's topology; then the 256 mA default is a real
trickle and shore carries the kit); or keep the topology and have the host write ChargeCurrent = load + wanted charge
(W2's F-CH-03 recommendation), accepting that a crashed host leaves the pack carrying the kit.

## 5. A side fact the round-1 analyses missed (VERIFIED facts, INFERRED effect)

RSNS_RAC defaults to 1b, meaning 5 mOhm (ChargeOption1, page 59; 9.3.5, page 25: "if 10-mΩ sensing is used please
configure RSNS_RAC=0b"). Board A's input shunt R16 is **10 mOhm** (`gen_sch_a.py:322`; netlist R16 VBUS20 to CH_ACN).
Until a host writes RSNS_RAC = 0b, every input-current number the charger uses (IIN_HOST, IIN_DPM, the IADPT gain, the
ADC, the ACOC thresholds) is scaled for 5 mOhm and reads half the true current. The input limit in real amperes then
differs from the register. W2's challenger computed an IIN_HOST cap of 3.25 A (about 65 W) at VBUS20 on the assumption
that the scaling is right: it needs re-deriving with the mismatch, TBD. It does not change A02-1, because RSNS_RSR = 1b
matches R17's 5 mOhm.

## 6. Rulings on the round-1 claims

- **W2 F-CH-01:** upheld, VERIFIED. Add: a swap gives 3S; the fix is a 75 % pair.
- **W2 F-CH-02:** the premise "ChargeCurrent is 0 A at POR and the watchdog resets it" is **refuted** (A02-1: 256 mA both).
  The conclusion "PANEL.md's crashed-panel claim is false" is **upheld** on F-CH-01 and F-CH-03 grounds. W2's own draft
  hedged ("either value stops a useful charge"), which was right in outcome and wrong in mechanism.
- **W2 F-CH-03:** upheld, VERIFIED. Strengthen it: shore cannot carry the kit's load beyond ChargeCurrent at all.
- **W5 F10:** the 256 mA value is upheld as INFERRED (TI E2E), not VERIFIED (the challenger was right about the datasheet).
  "Charging without the panel is a 256 mA trickle" is **refuted in effect**: the 256 mA feeds load plus pack, and on the
  current strap it feeds nothing.
- **Challenger of W5:** right that the datasheet contradicts itself and that "a crashed panel still charges" may be false
  outright; its "may be 0 A" reading of the device is superseded by TI's statement and the sibling-datasheet diff.

## 7. Remaining unknowns

1. Bench confirmation on the fitted silicon: REG0x03/02 at POR and after 175 s without a write, and the SRP-SRN current
   at the default (A02-1).
2. What ChargeCurrent becomes after an adapter removal on the BQ25731 (A02-2).
3. The kit's residual VBAT load with the panel controller hung (it decides whether a fixed-strap, host-free kit gains or
   loses charge).
4. CHG_INHIBIT at power-up: the 2N7002 threshold (datasheet not held) against the PCA9555 pull-up and R21.
5. The real input current limit with RSNS_RAC = 1b on a 10 mOhm R16, including the ILIM_HIZ pin path (EN_EXTILIM = 1b
   default, page 63; R19 16.5k and R20 34.8k from REGN put 4.07 V on the pin).
