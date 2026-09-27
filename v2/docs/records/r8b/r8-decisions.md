# Board B, round 8 (MESHSAT-1357, 26 to 27 September 2026): the circuit stream's record

Base: main fc144600. Worktree `fnd/r8b`. Author of `v2/ecad/tools/gen_sch_b.py`, `v2/ecad/tools/boards/b.json`, board B's
schematic-phase artefacts under `v2/ecad/pcb-b-compute-b19/` and one new land, `v2/ecad/meshsat.pretty/M2_B-Key_Socket_3052_TE2199119.kicad_mod`.
Nothing is committed or pushed. Prototype framing: no board of the set has been built, and nothing here has been measured on
hardware. Every figure below is arithmetic on a maker's published figure, or is marked INFERRED or TBD. This record is a
pinned, source-backed circuit review of the changes; it is not an automated PASS, and it is filed for review, not as one.

**Filed at integration (27 September 2026, round 8 set 3, branch `fnd/r8int3`).** This record is the author's second-pass
file with three changes, each taken by the session under the owner's standing rule of 26 September 2026: the two rows that
named the PCIe switch 'PI7C9X2G304' name the PI7C9X2G404SL, the part the generator draws and DS40068 describes (the first
independent check); the round's `drafts/b/` files are filed beside it, `drafts/b/X` at `v2/docs/records/r8b/X` with the
`b/` level dropped (`tools/`, `evidence/`, `expected_r8b.json`, `decoupling-classes-b.json`, `mk_m2b_te2199119.py`), the
five maker documents in `v2/vendor/` instead (SOURCES.yaml, the round-8 board B entries), and the drafted patches applied
to the files they name; and section 6 at the end says what the integration changed and read. The paths inside the
sections below are the author's.

Second pass (27 September 2026, 01:30 to 02:30 CEST): the independent check found the first pass's FAB-03 cascade was not a
true break-before-make and the integrated candidate failed one suite test on the ERC allow-list draft; section 0 is what
changed and why, and every reading below is the second pass's.

Generator sha256 ae8f25d66ea299c8 (main dedaf34ce285e5ff; first pass 30309ef324cca318). Netlist sha256 3b30b3cc5e75a478
(main 669d02d07aeaae4b). Schematic 3edec4e736caabae, intent 5af19ea259fba27b (274 bypass declarations), sidecar
9d80289a1267a95f (generator identity 9ce909ba882fc223). Land caba4f04104cd06d. `boards/b.json` 0c62cc5c65324e23.

## 0. Second pass: the independent check's two blocking items

**FAB-03 was not a true break-before-make (blocking item 1).** The first pass drove the muxes from BSEL{b}_S (the vote after
RC1 and a Schmitt buffer) and held the enable off while (vote xor select) or (select xor its delayed copy BSEL{b}_D2). The
check showed, by logic simulation, (1) a vote returning after the select moved but before BSEL{b}_D2 followed moves the
select back and clears both terms on that same edge, so the enable is released as the select changes, and (2) on every
normal change the two XOR terms cross on one select edge into one OR gate, a static-1 hazard of their skew while SEL moves;
the record's claims ("every move of the select is followed by T2 with the enable off", "the cascade has no such window")
were false. Both are reproduced here by `drafts/b/tools/bbm_sim_r8b.py`, a simulator that builds each bank from the
netlist's own parts and pins (not from the generator's comments) with the makers' ranges: on the first pass's netlist it
finds 36,272 of 69,018 select moves with the enable off less than 40 us after or less than 1 us before (71,180 of 71,782
with a static-1 hazard modelled in the 74LVC1G157s), and on `main`'s netlist the select moving while the enable is still on.
While reworking it the second pass also found a defect of its own first pass the check did not name: the slow power-good
node PG{s} (the module rail through 1 k / 100 k) went straight into 74LVC1G157 inputs, whose sheet limits the input
transition rate to 10 ns/V at 2.7 to 5.5 V despite their Schmitt action (Nexperia 74LVC1G157 Rev. 12 Table 6), the same
class as FAB-03's own RC edge into the XOR. The circuit now, per bank b (f = b % 3 + 1):

| Net | Made by | Meaning |
|---|---|---|
| BBM{b}_REQ | U80 (SN74LVC86A): BSEL{b} xor BSEL{b}_S | a change is requested |
| BBM{b}_ARM | R522 to R524 10 k, C573 to C575 100 nF, U521 to U523 (74LVC1G17) on BBM{b}_REQ | the request has held for T_ARM; it holds the enable off T_ARM-fall after the request clears |
| BBM{b}_MOV | U80 gate 4, U81 (SN74LVC86A): BSEL{b}_S xor BSEL{b}_D2 | the select has moved and its delayed copy has not followed |
| BSEL{b}_H1, BSEL{b}_H | U524 to U526 (ARM ? vote : select), U527 to U529 (MOV ? select : H1), 74LVC1G157 | THE LOCK: the select's delay is driven by the vote only while ARM is high and MOV low |
| BSEL{b}_S | R474 to R476 10 k (now from BSEL{b}_H), C481 to C483 10 nF, U507 to U509 (74LVC1G17) | the select at U{b}09.9 and U{b}10.9 |
| BSEL{b}_D2 | R519 to R521 10 k, C568 to C570 100 nF (were 10 nF), U510 to U512 (74LVC1G17) | the delayed copy |
| BBM{b}_RA, BBM{b} | U84 (REQ or ARM), U85 (RA or MOV), SN74LVC32A | the fabric is in motion; ARM never shares a gate with MOV |
| PG{s}_S, PG{s}_n | U530 to U532 (74LVC1G17), U533 to U535 (SN74LVC1G04) | the slot's power-good, Schmitt-buffered, and its inverse |
| PGSEL{b}_n | U513 to U515 (74LVC1G157): D2 ? PG{f}_n : PG{b}_n | the host the DELAYED select passes is dark |
| BOE{b}_n | U516 to U518 (74LVC1G157): BBM ? +3V3_DEV : PGSEL{b}_n | the enable at U{b}09.2 and U{b}10.6 |

Why it breaks before it makes, for ANY vote waveform (the argument; the numbers are `bbm_sim_r8b.py --bounds`,
`drafts/b/evidence/bbm-bounds.json`):
- The select can approach its threshold only while the lock passes the vote, that is while ARM is high and MOV is low; the
  enable is held off by ARM from the last unlock through the move (ARM cannot fall while the request is up, and the
  approach needs the request up), and at the move one input of each OR gate (ARM on U84, U84's output on U85) and the
  enable mux's select (BBM) are steady high: no gate in the enable path sees two inputs cross.
- HOLD: every move starts with the delayed copy equal to the select (the MOV half of the lock holds the select while they
  differ), so MOV is high after every move until the copy's node crosses its own buffer's hysteresis band, at least
  tau2 x ln(1 + 0.32 V / (V - VT+)) = 757 us x 0.1388 = 105 us. A vote that returns at any time therefore only starts the
  sequence again; this is item (1).
- LEAD: after the last unlock the select's node must travel back from where the lock held it: either T2 (at least 105 us)
  after the previous move, or ARM's re-arm (its node traversing ARM's own hysteresis band, at least 105 us) after a pause,
  in both cases with the node driven toward the select's own rail: at least 29 us of enable off before any move.
- Against the parts: 2,900 times TS3USB221A's 10 ns OE-to-output disable (SCDS277C 5.8), 29 times the TMUXHS4212's 1 us
  SEL-to-OFF and 21 times its 5 us SEL-to-ON with a common-mode change (SLASEP7A 6.7). The TMUXHS4212 gives no OEn time
  (TBD, A10).
- Residual, stated: the one window left needs the vote to return within about 13 ns of the select buffer's own threshold
  decision (its 7.0 ns delay plus an XOR's 5.8 ns) while a flapping vote has parked ARM's node within about 30 uV of ARM's
  lower threshold (13 ns at the node's fastest fall); the enable pulse it could make is under 13 ns. No single change and
  no single return reaches it; the aimed adversary of the simulation did not.
- A single change from rest: the enable off within 22.1 ns (SN74LVC86A 5.8, SN74LVC32A 5.0 twice, 74LVC1G157 6.3 ns,
  -40 to +125 C maxima), ARM 0.37 to 2.15 ms later, the select 37 to 215 us after ARM, the delayed copy 0.37 to 2.15 ms
  after the select, the enable back no sooner. A failover leaves the bank disconnected about 1 to 5 ms.
- The simulation on the regenerated netlist (seed 27, 1,500 random waveforms per bank): 19,976 runs, 56,342 select moves, 0
  violations, least lead 61.5 us, least hold 198 us; with the static-1 hazard in every 74LVC1G157, 22,121 runs, 63,780
  moves, 0 violations, least lead 46.5 us, least hold 194 us. The families: single changes at 27 corners of supply, thresholds and time constants; the check's own case,
  the vote returning r after it changed, r swept over 6 ms in 20 us steps and at every instant of the circuit plus or
  minus 1 ns to 20 us; an adversary that flips the vote at the circuit's own instants three levels deep; random vote
  waveforms of 1 to 30 changes with gaps from 1 ns to 3 ms, 30 percent of them with power-good toggles. Liveness is
  judged in each: the select ends at the vote and the enable returns.

Rejected, each for a reason: the check's suggested retriggerable monostable on both edges of the select (a new part and
sheet, SN74LVC1G123, with an edge detector in front, and it bounds only the hold, not the lead or the runt); a
fast-attack diode release (analog, and still needs the lock); the first pass's cascade with a consensus term alone
(A xor D2 cures item (2) but not item (1)). The gate draft now checks the structure at the switches' own pins
(section 3), so a rewiring back to either defect fails there.

**The integrated candidate failed one suite test (blocking item 2).** `erc-allow-b-r8.patch` added the QOD allow line to
the phase copy `v2/ecad/pcb-b-compute-b19/erc-allow.txt` only, and `test_driver_hygiene.t_a_phase_copy_declares_what_its_board_declares`
requires the canonical `v2/ecad/pcb-b-compute/erc-allow.txt` to be identical. The draft now carries the line in both files;
the full suite on the integrated candidate is in section 3.

Every session decision below was taken by the session under the owner's standing rule of 26 September 2026 ("never ask;
take the recommended answer"), `ruled_by: SESSION`, and is reversible by a later owner ruling.

## 1. Changes, each tied to its finding

| Finding | Parts | What changed | Maker's clause |
|---|---|---|---|
| FAB-01 | U101, U201, U301 (PI7C9X2G404SL), R190, R290, R390 | TEST2 (pin 16) leaves S{s}_TESTL (330 Ohm to ground) and gets its own 5.1 k to +3V3_S{s}B; TCK (89) and TDI (93) left open; TMS (92) and TRST_L (94) keep the 330 Ohm pull-down | Diodes DS40068 Rev 5-2, 3.3 (PDF p.14): "Test2 should be tied to 3.3V through a 5.1K-ohm pull-up resistor"; 3.4: TCK, TDI "should be left open (NC)", TMS, TRST_L "pulled low through a 330-Ohm pull-down resistor" |
| FAB-02 (b) | R191/R192, R291/R292, R391/R392; U530 to U532 (74LVC1G17) with C585 to C587; U533 to U535 (SN74LVC1G04) with C588 to C590; U513 to U515 (74LVC1G157GW, PGSEL{b}_n) with C518, C519, C560; U516 to U518 shared with FAB-03 | PG{s} = +3V3_CM{s} through 1 k with 100 k to ground, read by logic only through a Schmitt buffer (PG{s}_S) and its inverse (PG{s}_n); each bank's enable is forced off while the host the DELAYED select passes is dark (PGSEL{b}_n) | CM5 datasheet (release 3) pins 84, 86: CM5_3.3V "powered down during power-off or when PMIC_Enable set low"; 4.2.1: "when CM5 is powered-down or off, there must be no external voltage applied to any pin"; Nexperia 74LVC1G157 Rev. 12, Tables 3, 4, 6 (10 ns/V), 7, 8; Diodes DS35124 Rev 8-2 p.3 (no transition limit), p.5; TI SCES214AF (10 ns/V) |
| FAB-02 (c) | U519, U520 (74LVC1G157GW), C564, C565; R14 removed | HDMI_EN1 = PG2_S if HDMI_SEL1 else PG1_S (U3's EN), HDMI_EN2 = PG3_S if HDMI_SEL2 else HDMI_EN1 (U4's EN) | TI TS3DV642 SCDS343F Table 1 p.16 ("L X X: Switch disabled. All channels are Hi-Z"), 6.5 (VIH 1.4 V, IIH +-10 uA) |
| FAB-03 (second pass) | U80 (value), U81, U84, U85 (SN74LVC86APWR, SN74LVC32APWR) with C566, C567, C572; U507 to U512, U521 to U523 (74LVC1G17) with C512 to C517, C576 to C578; U524 to U529 (74LVC1G157GW, the lock) with C579 to C584; R519 to R524, C568 to C570 (100 nF), C573 to C575; R474 to R476 now from BSEL{b}_H; U516 to U518 (74LVC1G157GW, BOE) with C561 to C563 | True break-before-make (section 0): the select's delay is locked unless ARM is high and MOV low, BBM{b} = (REQ or ARM) or MOV, BOE{b}_n = BBM ? 1 : PGSEL{b}_n. U80's value names the part ordered, TI SN74LVC86APWR (C350562) | SCAS288R 5.4 (the 9 ns/V input rule the old RC edge broke), 5.9; SCAS286U 5.9; Diodes DS35124 Rev 8-2 p.3, p.5 (VT+, VT-, hysteresis), p.6 (tpd); Nexperia 74LVC1G157 Rev. 12 Tables 6, 8; TS3USB221A SCDS277C 5.8; TMUXHS4212 SLASEP7A 6.7 |
| FAB-04 | R480 to R500, R15, R16 | 100 k to 10 k: 21 supervisor vote lines and the two HDMI selects read a definite low with their driver dark | SCAS283W 5.7 (II +-5 uA), 5.4 (VIL 0.8 V); STM32H7 DS12110 Rev 10 Table 60 note 4; SCDS343F 6.5 and Table 4 p.21 |
| L1 | U506 (74LVC1G34), C511, R518 | The three supervisors' PC5 read EMCON_SUP, a buffered copy; no firmware-drivable pin remains on EMCON_HW | Diodes DS36108 Rev 10-2 (II +-1 uA, IOFF +-10 uA) |
| L2 | U501 to U505 (SN74LVC1G08), C65, C66, C508 to C510; U19, U20 removed; R58 4.7 k 1 percent | Every EMCON_HW reader states Ioff; the panel-absent level is 0.52 V (R102 at 100 k) or 0.36 V (R102 10 k), below VIL 0.8 V | TI SCES217AA 5.3, 5.5 (Ioff +-10 uA, II +-5 uA); SCAS283W has no Ioff row |
| L3 | U112 to U115, U212 to U215, U312 to U315, C183 to C185, C261, C262, C285, C383 to C385, TP104, TP204, TP304; Q11, R513, U111, U211, U311, Q109, Q110, Q209, Q210, Q309, Q310, R173, R174, R273, R274, R373, R374 removed | EMCON_ON{s} = NOT EMCON_HW made per slot from the module's own +3V3_CM{s}; losing +3V3_DEV no longer releases any module radio | TI SCES214AF (Ioff +-10 uA at VCC 0 V); CM5 datasheet 2.1.1, 2.1.2 ("may only be driven low") |
| L7 | Q106, Q206, Q306, Q111, Q311 removed; U{s}13 to U{s}15 (SN74LVC2G06) | Every FET on the EMCON path replaced by an open-drain gate whose sheet states VOL at the drive applied | TI SCES307J 6.5: VOL 0.1 V at 100 uA, 0.4 V at 16 mA, VCC 3 V, -40 to +85 C |
| SD-EMC-1 | R264, U220 (SN74LVC2G06), C299, U221 (TPS3808G30), R297, C200, Q212 (AO3400A), R295 (15 Ohm 1 W 2512), R296 | 5G supply removed by hardware: S2A_EN (buck U203) pulled low by U215 2Y, FULL_CARD_POWER_OFF# low at once by U220 1Y, rail discharged by Q212 and R295; Tpr held by U221 on release | Quectel RM520N series HD v1.1 3.3.1 p.29 (3.135 V floor), 3.3.2 note (flash warning), 3.5, Figure 9 and Table 10 (Tpr >= 100 ms); Diodes AP64500 DS41979 Rev 5-2 (VEN_L 1.03 V min); TI SBVS050N 6.6, 7.3.3, Table 5-1; AOS AO3400A Rev 3.1 |
| SD-EMC-2 | R194, R294, R394 (100 Ohm in PERST#); U21, U22 QOD tied to VOUT | PERST# back-feed into a card whose supply EMCON removed bounded to 36 mA; the dead LoRa and ZigBee rails are held through RPD | DS40068 Table 12-2 (VOH 2.4 V, no current); HD v1.1 4.3.3, Figure 21 note; TI TPS22810 SLVSDH0C Pin Functions, 9.3.2, 7.5 (RPD 250 to 400 Ohm at 5 V) |
| I3-F01 | U41, U51, U61 (comment and contract only) | TPS23861 answers 0x30 whatever A3 is; the supervisors' firmware contract is 0x34, 0x35, 0x36; the bus is unchanged | TI SLUSBX9I 7.3.13 |
| S-12 | J_M2C2 on `M2_B-Key_Socket_3052_TE2199119` | The land gains the two locating holes (1.1 mm at X -10, 1.6 mm at X +10, on the line 4.5 mm inside the odd row) | TE customer drawing C-2199119 rev F, sheet 3 |
| S-13 | U222, U223 (TPD4E001DBVR) | One TVS array per SIM holder, holder side of the 22 Ohm, VCC on the SIM supply with its 100 nF | HD v1.1 4.1.7 p.42 and Figure 18 (TVS, at most 10 pF); TI SLLS682P 5.4 (1.5 pF), 8.1 items 2 and 4 |
| B_PANEL_5V (PWR-003) | F1 | 2.0 A PPTC to Bourns MF-MSMF110 (1.10 A hold, 2.20 A trip, 1812, C89647), below the 1.23 A conductor | Bourns MF-MSMF data sheet (v2/vendor/power/bourns-mf-msmf-pptc.pdf): ratings table, Thermal Derating Table (0.85 A at 50 C, 0.77 at 60, 0.71 at 70), How to Order |
| G4 | C571, C605, C606, C635, C636, C665, C666 | 100 nF at VIN beside each small buck's input capacitor | TI TPS62933 SLUSEA4D 12.1 p.40: "Place a 0.1-uF ceramic decoupling capacitor or capacitors as close as possible to VIN and GND pins" (class R) |
| G5 | C37, C38 | Declared at the TS3DV642s' VCC (U3, U4 pin 1), not the PoE controller | SCDS343F pp.18, 23 |
| G6 | PI7C9X2G404SL caps, TMUXHS4212 C92, C93, TS3USB221A C94, supervisor caps | Declared per supply group (the maker states none for the PCIe switch: decision 42 D1) | DS40068 3.5; SLASEP7A 10, 11; AN4938 Rev 7 7.4 p.32, 2.2 p.12 |
| G7 | C601 to C604, C631 to C634, C661 to C664 (TUSB8041I); C531 to C550 (KSZ9897); C551 to C558 (CP2102N VREGIN); C412, C413, C432, C433, C452, C453 (STM32 VDDA); C27, C28 to 22 uF | One 100 nF per supply pin where the maker asks it; bulk per the maker's figure | TI SLLSEE4E 11.1.1 p.38, 10.1 p.37; Microchip DS00002330D 4.7 Figure 4-8 p.51; Silicon Labs CP2102N data sheet Rev 1.5 p.5 ("4.7 uF and 0.1 uF bypass capacitors required for each power pin"); ST AN4938 Rev 7 2.2 p.12 |
| G10 | C4, C5, C6, C71 (declarations) | C4 at U25 VIN (pin 3), C5 and C6 at L1's output pad, C71 at the TMP117 (U10 pin 4) | Diodes AP63203 DS41326 p.2 |
| Parts re-take row 1 | U9 | DS3231SN# (C9866) drawn on its own 16 SO land, pins per the maker | Maxim/ADI DS3231 19-5170 Rev 10 (3/15) Pin Description p.8, Ordering Information, Package W16#H2 |
| Parts re-take row 6 | J_W1A, J_W1B, J_W3A, J_W3B, J_WOA, J_WOB | LCSC C434808 to C88373 (U.FL-R-SMT-1(10), the code the reconciliation certifies on this land) | WRONG-MODEL-RECONCILIATION.md row 6 |
| FAB-05 (text only) | TCAN334D comment | 1 Mbps, not 5 | TI SLLSEQ7F Device Options |
| (signal classes) | `boards/b.json` signal_classes | BBM*, PGSEL*, PG?, PG?_S, PG?_n and EMCON_SUP get a class (they read UNKNOWN, judged at RET-001's strictest bar) | RET-001's own table rule (b.json `_signal_classes_why`) |

The netlist differs from main's in exactly these items: `drafts/b/tools/netdiff_r8b.py` (own s-expression reader, no project
tool) against `drafts/b/expected_r8b.json` (built by `drafts/b/tools/expected_r8b.py`, one entry per finding) reads
"parts 1103 -> 1265 (+187 -25 ~36); nets 1929 -> 2002 (+93 -20 ~85, renamed 0); unexplained: 0"
(`drafts/b/evidence/netdiff-expected-r8b.txt`, full report `netdiff-committed-vs-r8b.json`; the same against the netlist
regenerated from `main`'s own generator on the box). Dropping the lock and ARM parts' pattern and the BSEL{b}_H nets from
the list makes it report 15 unexplained differences, so the comparison is not vacuous. Against the first pass's netlist
(`netdiff-pass1-vs-pass2.json`) the second pass adds exactly the 38 parts of section 0 (U85, U521 to U535, R522 to R524,
C572 to C590), changes C568 to C570 (10 nF to 100 nF) and fifteen value texts, adds 40 nets and removes 9 (BBM{b}_X1/X2,
PGSEL{b}), and moves R474 to R476, U513 to U520's inputs and U516 to U518's select, nothing else.

## 2. Session decisions (authority SESSION, standing rule of 26 September 2026)

- **SD-EMC-1r8 (supersedes EMCON.md option (f) and r4b's SD-B-03).** authority_why: the review of 26 September refuses a
  firmware-dependent shutdown bound; Quectel's documents give no other firmware-independent inhibit than supply removal
  (EMCON.md 4.5), so one option stands after the reading. THE BOUND, EMCON asserted to RF off: logic in nanoseconds, the
  AP64500 disabled (its disable delay is not published; one switching period is 0.68 us at 1.47 MHz, INFERRED), then the
  socket rail discharged through 15 Ohm from 3.545 V to the module's 3.135 V floor:
  t = 15 Ohm x (0.63 mF + CINT) x ln(3.545 / 3.135) = 1.16 ms + 1.84 ms per mF of CINT; to 1.0 V: 12.0 ms + 19.0 ms per mF.
  CINT (the module's own input capacitance) is published nowhere held: TBD, bench E-12. Residual accepted and stated: Quectel's
  flash warning ("DON'T cut off power supply directly when the module is working", HD v1.1 3.3.2 note); the bridge's
  cooperative AT+CFUN=0 stays care, not the inhibit.
- **Tpr supervisor U221 (TPS3808G30, CT 49.9 k to VDD: td 180 / 300 / 420 ms).** Recommended over an RC because its delay is
  a published minimum (SBVS050N 6.6) above HD Table 10's 100 ms.
- **PERST# series 100 Ohm (SD-EMC-2).** Bounds the one TBD back-feed term to 36 mA; a 1 percent divider against a 10 k
  internal pull-up (HD v1.1 4.3.3 asks for a push-pull low near 0 V).
- **QOD tied to VOUT on U21, U22 (SD-EMC-2).** The maker's own option; ERC reports it as an output on a power net
  (allow line drafted, `erc-allow-b-r8.patch`).
- **FAB-03, second pass: the locked sequence (section 0) over the first pass's cascade, over the page's remedy (a) and
  over a retriggerable monostable.** authority_why: the independent check showed the cascade (and (a), which it had
  replaced) releases the enable on a select edge and carries a static-1 hazard; of the remedies that stand after the
  reading, only the lock bounds the lead, the hold and the runt together with parts already on the board (74LVC1G17,
  74LVC1G157, SN74LVC32A), so one option stands. The first pass's claim that its cascade "has no such window" is withdrawn.
- **FAB-02: PG{s} through a 74LVC1G17 and an SN74LVC1G04** over a 74LVC1G14 (one part fewer per slot, but a part and a
  sheet this tree does not hold); the bank qualifier reads the DELAYED select, so it never switches within a move, and
  the enable mux carries BBM on its select, so no power-good edge can reach the enable while the fabric moves.
- **FAB-02 (b) and (c) both taken** (bank qualifier and display switch enables), the page's recommended pair.
- **B_PANEL_5V: F1 to MF-MSMF110** over widening the conductor class. The class is layout work (gen_pcb_b3.py 0.8 mm PANEL
  class) and rides on the next placement; the fuse closes the stage on the schematic. Board C's 1.0 A must stay a peak above
  about 35 C (derating table).
- **I3-F01: supervisors at 0x34 to 0x36 as a firmware contract**, the bus unchanged, over an address translator or bus split:
  no part added, and the conflict is with a broadcast address only.
- **L2: R58 4.7 k 1 percent**, with board A's R102 recommended at 10 k 1 percent (board A's stream).
- **Timing (FAB-03, second pass).** RC1 stays main's 10 k / 10 nF (tau 75.7 to 127.8 us); ARM's and the delayed copy's
  are 10 k / 100 nF (C14663 class, tau 757 to 1278 us), so the hold and the re-arm, bounded by a buffer's own hysteresis
  traversal (0.1388 tau at its narrowest), stay above 8 times the TMUXHS4212's 5 us for ANY vote waveform: at least 105 us.
  R 1 percent, X7R 10 percent and +-15 percent over temperature; 74LVC1G17 thresholds from DS35124's -40 to +125 C table,
  minima at the 3 V row at every supply, maxima interpolated toward the 4.5 V row (INFERRED), hysteresis at least 0.32 V;
  input leakage +-5 uA through 10 k and output levels 0.1 V from the rails. The TMUXHS4212 gives no OEn timing: TBD,
  IOHA test A10.

## 3. Readings (box 52646493, /root/r8-b, main fc144600 with its real history from a bundle; gates into scratch verdict directories)

All second-pass readings, on the final generator (ae8f25d66ea299c8). Logs in `drafts/b/evidence/`.

- Regeneration with main's chain (gen_sch_b.py, build_sch.sh, `PHASE=B21`): 1313 symbols drawn (1265 parts in the netlist),
  158 lib symbols, 43 pages, 967 nets, no single-pin net; 68 lands judged, 0 pins on a pad the land does not carry;
  swallowed-calls check empty. Main's own generator regenerated beside it on the same box reproduces the committed files:
  schematic PARITY, netlist and intent PARITY_AFTER_NOISE. Three regenerations of the second pass (the generator's
  comments, then its +3V3_DEV load list, changed between them) give netlists equal record by record and node by node; the
  last one's intent differs from the one before only in the sixteen new +3V3_DEV loads and its timestamp.
- ERC (erc_gate, SCH-001): PASS, 2869 violations, 0 blocking, 7 errors allow-listed (main 2398 and 5; first pass 2690 and
  7): the two QOD lines of SD-EMC-2 and main's five. NOTE for the tools stream: erc_gate's allow parser splits
  `pin_to_pin|#FLG` at `#`, so that line allows every pin_to_pin error; the QOD line is drafted so the reason is explicit
  either way.
- safe_lines PASS of 5; pin_map_lands_b PASS of 1264; derate PASS of 240; power_sequence PASS of 41 rails, 0 deadlocks;
  power_path PASS (114 nodes, 0 undeclared); port_protect PASS of 17 (6 one-way clamps); clock_check PASS of 7;
  review_nets 27 issues (main 27).
- check_contracts: INCONCLUSIVE in the bare commit set (the new land changes every board's generator identity, so boards
  A, C, D, E, P read as absent; inhibit_chain_b PASS of 3 there); on the integrated candidate (every draft,
  `other-boards-sidecars-r8.patch` among them) PASS of 96, inhibit_chain_a to _d PASS (4, 3, 3 and 5), energy_chain_b
  PASS of 3. energy_chain PASS of 98 on the bare set (energy_chain_b FAILs B_PANEL_5V there) and PASS of 98 with 0
  coordination findings on the integrated candidate.
- netlist_board and netlist_parts (SCH-002) FAIL, as on main: the committed layout is stale until layout entry.
- Netlist comparison (`netdiff_r8b.py`, own reader): committed main against this netlist, and main regenerated on the box
  against it, both "parts 1103 -> 1265 (+187 -25 ~36); nets 1929 -> 2002 (+93 -20 ~85)", every difference explained by
  `expected_r8b.json` (0 unexplained; 15 when the lock and ARM entries are dropped). First pass against second pass:
  +38 parts, 18 changed, +40 and -9 nets, each in section 0.
- Break-before-make simulation (`bbm_sim_r8b.py`, seed 27): section 0. This netlist 0 violations in 19,976 runs and in
  22,121 with the 74LVC1G157 hazard model; the first pass's netlist 36,272 and 71,180; main's every move of the swept
  family. Bounds: `evidence/bbm-bounds.json`.
- check_pcb_b: the drafted gate change, emulated on the netlist with the gate's own statements (round 4's emulator):
  261 checks, 0 FAIL on this netlist, 15 FAIL on the first pass's (all break-before-make and power-good), 77 on main's;
  13 of 13 mutations caught (`evidence/check_pcb_b-r8-mutations.txt`). The IOHA invariant block, emulated on a pad map
  built from the netlist: 12 checks, 0 FAIL (main's netlist 3 FAIL: the switches' select is not BSEL{b}_S there).
- Suite, once, on exactly the commit set (t8: main fc144600 plus gen_sch_b.py, b.json, the land and board B's schematic,
  netlist, intent and sidecar): "tests: 1646 passed, 7 failed, 4 skipped", the seven being the registry's bindings and
  generated pages this round's drafts carry (test_requirements x5, test_rule_gate_mapping x2); the suite's own renders
  rewrote the eight generated pages in the tree (the readings they render changed), nothing else. An earlier run on this
  pass's previous generator (before the sixteen +3V3_DEV loads were declared) read 1646 passed, 8 failed, 4 skipped: the
  same seven and the rules_status evidence check.
- Suite, once, on the integrated candidate (t8d: the commit set, every draft applied, the five maker documents filed, the
  requirements rebound by `rebind_r8b.py`, all committed in the scratch clone; the generated pages rendered, `rules_render
  --check`, `--requirements --check` and `decisions_render --check` exit 0, committed): "tests: 1654 passed,
  0 failed, 3 skipped", the tree unchanged by the suite. `test_driver_hygiene.t_a_phase_copy_declares_what_its_board_declares`
  (the check's failure) passes with the QOD line in both allow files. A first run of this candidate read 1653 passed and 1
  failed, `test_import_before_use`: the gate draft's new block named two locals `_v` and `_pg`, which check_pcb_b.py
  imports later at module scope (`verdict as _v`, `pair_gate as _pg`); renamed `_vote` and `_pgm`, re-emulated (261 checks,
  0 FAIL, 13 of 13 mutations) and run again. `drafts/b/pcb_requirements-r8.patch` and `generated-pages-r8.patch` are this
  run's (rules_lib requirements 0 errors).

## 4. Not done, with the reason

- SD-EMC-2 series resistance on the E22, E72 and RockBLOCK lines: no maker publishes an injection limit for those modules'
  pins with their supply removed, so no value can be derived; QOD now bounds the rail. Owed to the EMC stream.
- AW7915-AED back-feed floor: no maker figure (slots 1 and 3).
- L4 case (2) on U501 to U505: they run from +3V3_DEV, whose loss they read correctly (outputs low, 0.10 V), but the band
  under 1.65 V is unspecified; carried as INFERRED from the rail order.
- Board A's R102 and U26, board C's GPIO21 buffer: other boards' streams.
- TMUXHS4212 OEn timing: unpublished (TBD, A10). Module CINT: unpublished (TBD, E-12).
- FAB-03's one residual (section 0): a vote returning within about 13 ns of the select buffer's own decision while a
  flapping vote has parked ARM's node within about 30 uV of its lower threshold. No part this tree holds removes it (an
  asynchronous threshold race always leaves such a window); it is stated, bounded (an enable pulse under 13 ns) and out of
  reach of any single change or return. A10's probe: the select the switches see is BSEL{b}_S, which has no test pad (the
  round-5 pads TP504 to TP506 sit on the vote BSEL{b}); probe R519 to R521 pad 1, or add pads at the next placement.
- The 74LVC1G157's static-1 behaviour on a select change is published nowhere (Nexperia Rev. 12); the design does not rely
  on it (the enable mux's select is BBM, steady at every move), and the simulation ran with and without a modelled hazard.
- Placement regions and conductor classes for the new parts (gen_pcb_b3.py): layout work, not this stage.
- jlc_certify re-take for the new codes (C7666, C7827, C402162, C151394, C526347, C135822, C350562, C465736, C189211,
  C20917, C20087, C89647, C88373, C9866 on its new land): lcsc_fill.py MAP lines and lcsc-allow are other streams' files.
  The second pass adds no code: its 38 parts are 74LVC1G17 (C151394), 74LVC1G157GW (C135822), SN74LVC1G04 (C7827),
  SN74LVC32APWR (C352974), and 10 k, 100 nF and 10 nF passives on the MAP lines board B already uses.
- pcb_reliability, pcb_part_temps, pcb_emc, pcb_sensitive, pcb_rules_coverage: no row needed by a gate this round; the new
  parts' reliability and temperature rows are owed with the parts stream.
- The generated pages patch was rendered in the box's scratch clone with every input committed (the integration recipe),
  on this round's inputs only; after the real merge re-render (`python3 tools/rules_render.py`, `--requirements`) rather
  than applying it byte for byte.
- ASSEMBLY.md: no change needed by these items.

## 5. Drafts for the integrator (all apply cumulatively to main fc144600; checked)

`drafts/b/`: ARCH-PCB-B-IOHA-r8.patch, CONOPS-r8.patch, DECOUPLING-r8.patch, EMCON-r8.patch, FAILOVER-FABRIC-r8.patch,
PANEL-r8.patch, V2-SPEC-r8.patch, check_pcb_b-r8.patch, energy-chain-B_PANEL_5V.patch, erc-allow-b-r8.patch,
other-boards-sidecars-r8.patch, pcb_requirements-r8.patch, sources-yaml-additions.patch, generated-pages-r8.patch,
decoupling-classes-b.json (274 declarations, intent 5af19ea259fba27b), datasheets/ (five maker documents, SHA256SUMS,
SOURCES.txt), expected_r8b.json, tools/ (netdiff_r8b.py, expected_r8b.py, bbm_sim_r8b.py, check_pcb_b_emul.py,
check_pcb_b_r8_mutations.py, rebind_r8b.py, netdiff.py, r8b2_box.sh: the box procedure of this pass), evidence/. Changed by the second pass: FAILOVER-FABRIC-r8.patch
(section 9a, FB-FAB-3 and FB-FAB-4), ARCH-PCB-B-IOHA-r8.patch (section 5 items 3 and 4, the break-before-make
paragraph), check_pcb_b-r8.patch (the break-before-make structure and the IOHA invariant's select net), erc-allow-b-r8.patch
(both allow files), sources-yaml-additions.patch (designators), DECOUPLING-r8.patch (the count), pcb_requirements-r8.patch
and generated-pages-r8.patch (regenerated), decoupling-classes-b.json, expected_r8b.json and the tools named above.

## 6. Integration (27 September 2026, round 8 set 3, branch `fnd/r8int3` on main `84e52461`)

Each choice below was taken by the session under the owner's standing rule of 26 September 2026. Nothing is built or
measured.

- **Regeneration on the build box** (52646493, `/root/r8int3` only, main `84e52461` with its full history, KiCad 9.0.9;
  the procedure and its logs are `integration/` beside this file: `r8int3_box.sh`, `regen.log`, `set.log`, `gates.txt`). Main's own generator reproduces main's committed
  board B files: schematic, netlist, intent and ERC PARITY_AFTER_NOISE, BOM PARITY (the sidecar differs only in the
  schematic sha its date moves). The author's commit set regenerated on main reproduces the author's files: schematic
  PARITY, netlist, intent and sidecar PARITY_AFTER_NOISE. The committed board B files are the integration's own
  regeneration: netlist `adcc3c6736c90e9f`, schematic `535b2643d0b2542b`, intent `1038d0f6ce8104b5`, generator identity
  `6dba22222360b29b`; a second run of the generator gives the same schematic byte for byte.
- **The integration's own comparison** (`integration/indep_cmp.py`, its own s-expression reader, not `tools/netdiff_r8b.py`), committed main against
  the regenerated netlist and main regenerated against it: parts 1103 to 1265 (+187 -25 ~36), nets 1929 to 2002 (+93 -20
  ~85), 0 differences unexplained by `expected_r8b.json`; with the FAB-03 and S-13 part entries dropped it names 56. Against
  the author's netlist it differs in three value texts only (below).
- **One generator change at integration.** U115, U215 and U315's value text read 'card buck EN'; main's round 8 set 2 added
  a census test (`test_rails_census.t_every_power_part_on_the_committed_netlists_has_a_held_row`) that takes a part whose
  value names a buck as a power part and asks for its held row, so it failed on these three open-drain gates. The text now
  reads 'the card supply's enable S{s}A_EN'. No net, pin, footprint or order code moved.
- **The land is generated.** `gen_footprints_b16.py` writes `M2_B-Key_Socket_3052_TE2199119` from its base land (the
  second independent check's item), byte for byte the file `mk_m2b_te2199119.py` wrote (sha256 caba4f04); every footprint
  generator re-run in the three box trees left `meshsat.pretty` unchanged. The new land and the generator change move every
  board's schematic identity, so boards A, C, D, E and P were regenerated in the same tree (schematic, netlist, intent and
  ERC PARITY_AFTER_NOISE, BOM PARITY against their committed files) and their sidecars re-written.
- **Drafts.** Applied as written: `check_pcb_b-r8`, `erc-allow-b-r8`, `ARCH-PCB-B-IOHA-r8`, `V2-SPEC-r8`,
  `FAILOVER-FABRIC-r8`, `energy-chain-B_PANEL_5V` (its test now finds F1's value by parsing the generator, the second
  check's item). Re-derived on main's text, which sets 1 and 2 had moved: `CONOPS-r8`, `DECOUPLING-r8`, `PANEL-r8`,
  `EMCON-r8` (its section 0a is `EMCON.md` section 4b, beside board A's 4a, with the L2 sum re-taken on main's boards A
  and C: 0.36 V), `sources-yaml-additions` (with F1's and Q212's open items), and `pcb_requirements-r8` (every record whose
  bound file moved re-read on this branch's files). Not applied: `other-boards-sidecars-r8` (re-stamped after the parity
  run instead) and `generated-pages-r8` (the pages are rendered from the committed state). The five maker documents are
  filed in `v2/vendor/` at the sha256 above with their `sources.txt` and `vendor-status.txt` lines; `ARCHITECTURE.md`'s
  board B rows follow the round, and the RTC is named DS3231SN there and in `PANEL.md`.
- **Readings on the regenerated netlist** (verdicts outside the tree): ERC PASS of 2869, 7 allowed (main's 5 and the two
  QOD lines); pin_map_lands PASS of 1265; derate PASS of 240; power_sequence PASS of 41; power_path PASS (114 nodes);
  port_protect PASS of 17 (6 one-way clamps, 0 reversed); clock_check, ground_system, emc_sheet, reliability, safe_lines
  PASS; review_nets 27 issues as on main; check_contracts PASS of 96; energy_chain PASS of 98 with 0 coordination
  findings and `energy_chain_b` PASS of 3 with the chain draft; SCH-002's netlist_board and netlist_parts FAIL against the
  stale B21 board, as on main; PWR-001 (`intent_checks.py --netlist`) FAIL 29 of 70 as on main (28 undeclared, 26
  undecided); SI-001 (`edge_length.py --netlist`) INCONCLUSIVE, 888 signal nets (835 on main). RF-002's walk:
  `inhibit_chain_b` FAIL 10, PASS 3, UNDECIDED 7 (main 15, 3, 2): the walk has no SN74LVC2G06 pin map, so every
  open-drain stage reads 'EMCON does not reach it', and U221's value names the RM520N with no census entry claiming it
  (`EMCON.md` section 4b, a tools hand-off); `inhibit_chain_a` and `_c` move from FAIL to INCONCLUSIVE, because the
  supervisors' PC5 have left `EMCON_HW`.
- **The independent checks' residuals, recorded:** the sub-13 ns enable pulse window and the few-ns stale dark flag at a
  move's end (`FAILOVER-FABRIC.md` section 9a and FB-FAB-4, `ARCH-PCB-B-IOHA.md` section 5); the TMUXHS4212's unpublished
  OEn time (A10); no test pad on `BSEL{b}_S` (layout work at the next placement); Q212's rows at 25 C only and U506's
  push-pull drive into an unpowered supervisor (`EMCON.md` section 4b); F1's plain part missing from the held Bourns sheet
  and its 0.95 A hold at 40 C against board C's 1.0 A peak (`v2/vendor/SOURCES.yaml`, `ARCHITECTURE.md` section 4.5); the
  board B decoupling classes held in `decoupling-classes-b.json` until the generator writes them (`DECOUPLING.md` section
  10).
