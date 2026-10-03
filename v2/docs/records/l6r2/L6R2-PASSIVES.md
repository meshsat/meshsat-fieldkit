# L6R2: exact parts for the generic rows of the six boards (Layer 6 criterion 6.1; MESHSAT-1357, 3 October 2026)

Prototype design: nothing is bought, built, powered or measured. Every figure here is printed by `l6r2_passives.py`
(`l6r2_passives.out`, "out N" below), which reads only this tree and the dated catalogue reading in `inputs/`; this page is the
short form. Based on `fnd/int28` at `a1f696de`.

## 1. What was asked, and the denominator (out 1)

The supplier package's reader (`inputs/bom_from_netlist.py`, copied from `fnd/int27` at `e2a8df59`, sha256 recorded) reads
**2707 references, 1879 without an LCSC field** from the six committed netlists. It counts every `(comp)` block, the parts the
schematics mark `exclude_from_bom` (mounting holes, test points, fiducials) included. This record's denominator is the identity
tool's: the **fitted** rows (`part_identities.rows`), **2485, of which 1657 carry no LCSC field**. Each board's uncoded rows are
grouped into the identity tool's selections (one key per value, land and deciding requirement) and classified:

- **Generic, selected here:** multilayer ceramic capacitors, resistors (general, current sense, zero-ohm), ferrite beads, small
  diodes of a generic type (SMBJ, BAT54), 0603 indicator LEDs.
- **Special, not re-selected:** ICs, modules, transistors, named inductors, connectors, switches, fuses and their holders, wires,
  screws. Each is listed as a finding with what its value names (out 3).
- **OPEN:** a generic part whose deciding requirement the generator and the intent leave open (a net with no bound, an RF
  inductor's unstated properties, a lamp's intensity). Each is a finding with its line, never a guess.
- **NOT_A_PART:** copper on the board itself (rule N-1: solder jumpers, pads, lead lands, pogo targets).

## 2. The rules each selection is judged by

| Property | The requirement | Its source |
|---|---|---|
| Capacitor voltage | the stated rating, or the voltage across the part from the board's intent (DECLARED) or its nets' bound (BOUND), at the 20 percent derate margin, rounded up to a standard rating | rule V-1 (`part_identities.py`; derate.py's MARGIN, the CMP-001 screen); an UNBOUNDED net leaves it OPEN |
| Capacitor dielectric | stated; else C0G for a crystal's load (C-D1) and for 1 nF and below on 0805 or smaller (C-D2); else X7R, with X8R and C0G accepted (C-D3); X5R only where stated or by C-D3b | `pcb_part_identities.yaml` rules; `DIELECTRIC_ACCEPTS` |
| Tolerance | stated; else C0G 5 %, class 2 10 % (below 10 uF) or 20 %; a resistor 5 % | rules C-T and R-T1 (each such line is a finding, out 3) |
| Resistor power | a shunt at least twice its I^2 R at the declared peak rail current; any other its package's standard rating | rule R-P |
| Shunt temperature coefficient | at most 200 ppm/K where none is stated | rule R-S1 |
| Resistor working voltage | the catalogue line's maximum at or above the bound of its nets, where the line prints one | rule V-1's bound |
| Temperature grade | the maker's operating range against the envelope's -20 to +62.1 C board air (`pcb_envelope.yaml`): a resistor's, diode's, LED's or ferrite's as its catalogue line prints it; a ceramic's by its dielectric class code (X7R and C0G -55 to +125 C, X5R -55 to +85 C) | the envelope; INSIDE, AT_LIMIT, OUTSIDE or NOT READ |
| Stock | JLCPCB's stock at least the five-kit need (rows on the board x 5); also summed over the boards that share a code (out 3) | the owner's "minimum 5 of each" |
| Order of preference | the code the design already carries (lcsc_fill.py's MAP, then the certified table, then the identity table), then JLCPCB's basic library, then a preferred part, then a maker whose own sheet is public, then stock | rule I-1 |
| Refusals | a code in `lcsc-blocked.txt` for the land or declared in `jlc-mismatch.yaml` for the row is never selected | lcsc_fill.py's own checks |
| Identity | DECODED on the maker's ordering table where the part is a YAGEO CC ... X7R ... BB capacitor (`yageo-cc-series.pdf` p.2) or a UNI-ROYAL 0603WAF or 1206W4F resistor (the held Uniroyal sheet p.2), judged by `part_identities.read_binding` (rule D-2); else the catalogue line's identity, recorded DOCUMENT_OWED | rule D-2 |

A property the catalogue line does not print counts as not met, except where a maker's series sheet held in this tree prints it:
the Milliohm HoJLR2512 sheet's p.2 gives the series' +-50 ppm/K (2 to 500 mOhm) and its -50 to +170 C range, and the script reads
both phrases off the page before it uses them.

## 3. Coverage per board (out 2 and 5; the table is the script's `--page-table`, held equal by test_l6r2)

<!-- page-table:begin -->
| Board | Uncoded fitted rows | SELECTED rows (selections) | Open: OPEN requirement | Open: SPECIAL (not re-selected) | NOT_A_PART | NO_MATCH | Rows whose finish-time code (lcsc_fill.py) fails a requirement | Designators in the draft |
|---|---|---|---|---|---|---|---|---|
| A | 382 | 318 (71) | 0 | 64 | 0 | 0 | 20 | 318 |
| E | 111 | 86 (43) | 1 | 16 | 8 | 0 | 7 | 86 |
| P | 50 | 43 (15) | 1 | 6 | 0 | 0 | 0 | 43 |
| D | 137 | 122 (22) | 5 | 8 | 2 | 0 | 29 | 122 |
| C | 83 | 40 (17) | 17 | 22 | 4 | 0 | 5 | 40 |
| B | 894 | 831 (54) | 9 | 54 | 0 | 0 | 109 | 831 |
<!-- page-table:end -->

**1440 of the 1657 uncoded fitted rows are SELECTED**: every deciding requirement met on the catalogue line, stock for five kits
on the board and for the set. No selection is short of stock (the narrowest set margin: ROHM GMR100HJAAFD5L00 for board A's R17,
412 against 5). Every selection names its maker, MPN, package, LCSC code, price at 1 and at the need, grade with its basis, and an
alternative from another maker where one meets every requirement (out 2). Of the 222 selections, **131 bind DECODED** on the
maker's own ordering table and **91 are DOCUMENT_OWED** (the catalogue's identity; the maker's sheet is to be filed).

## 4. Findings (out 3)

**F1. The finish-time codes fail the identity tool's requirements on 170 rows.** `lcsc_fill.py` fills a blank row at finish from
its MAP or the certified table; on these rows the code it would fill does not meet the requirement the netlist and the intent
derive (the drafts below write a meeting code into the generator, which lcsc_fill then leaves alone):

| The design's code | What it is | Where | Why it fails |
|---|---|---|---|
| C15849 CL10A105KB8NNNC | 1 uF X5R 0603 | A C4, C19; E C20, C34, C35, C45, C47; D 19 rows; C C3, C4, C14, C16; B 14 rows | rule C-D3: an unstated class 2 is X7R |
| C15850 CL21A106KAYNNNE | 10 uF X5R 0805 | D 7 rows; B 42 rows | as above |
| C6119902 CGA0805X5R226M6R3MT | 22 uF X5R 0805 | B 27 rows | as above |
| C57895 CL10A225KA8NNNC | 2.2 uF X5R 0603 | B 6 rows | as above |
| C1588 CL10B102KB8NNNC | 1 nF X7R 10 % 0603 | A 14 rows; E C16; B C45, C52 | rule C-D2: 1 nF on 0603 is C0G (5 %) |
| C14663 CC0603KRX7R9BB104 | 100 nF 50 V | E C5 (TIMER); B C29 to C32 | rule V-1: 100 V needed |
| C1622 CL10B473KB8NNNC | 47 nF 50 V | A C77 | rule V-1: 100 V needed |
| C403725, C6119961 | 47 uF and 100 uF X5R 1206 | A C1, C2; B 14 rows | no X7R line meets: rule C-D3b keeps the X5R part (F2) |
| C500739 LR2512D-3W-5mR-1% | 5 mOhm 3 W | A R17 | rule R-P: 5 W needed (the selection is a 5 W ROHM GMR100) |
| C2960829 FRC2010J270 | 27 Ohm 5 % 2010 | D R54, R56 | the value states 1 % |
| C1017 GZ2012D601TF | 600 Ohm ferrite, 500 mA | D FB1 | the value states 2 A (TDK MPZ2012S601AT000 selected) |
| C23411 0603WAF470LT5E | 0.47 Ohm, 800 ppm/K | C R43 | rule R-S1: 200 ppm/K (UNI-ROYAL CS03W5F470LT5E selected) |

*Affects:* `lcsc_fill.py`'s MAP (a tools edit, not made here) and every board's finish until the drafts are applied.

**F2. Rule C-D3b, X5R taken, the hot-spot question OPEN:** board A C1, C2 (47 uF 25 V 1206) and board B's 14 rows of 100 uF 10 V
1206: no X7R line read meets the value, land and rating with stock; the design's own X5R parts (Murata GRM31CR61E476ME44L, HRE
CGA1206X5R107M100NT) are kept and the question whether their hot spot stays under +85 C is recorded OPEN.

**F3. Requirements open, never guessed (33 rows):** board P C9 and board D C46 to C48 and board B C161, C162, C500 to C505 (no
declared or bounded voltage on their nets); board E R51 and board B R13 (zero-ohm links whose current rating no catalogue line
states); board D L1 and L2 (68 nH LPF inductors: tolerance, Q, self-resonance and current unstated, "values to be verified in
MESHSAT-818"); board C's 17 panel lamps (intensity and viewing angle through the light guides unstated, w5identc's CHOICE_OWED).

**F4. Special parts without an LCSC code (170 rows), listed with what their value names (out 3):** the CSD FETs, 2N7002 and BC857
transistors, the TPS22810, TPS2065C, AP2112K and TLV75533 regulators and the other ICs named by part number; the Coilcraft
inductors (hand-fit, not in JLCPCB's catalogue); the IDC headers and Mill-Max pins whose identities PROCUREMENT.md HC6-SC-7 and
HC6-SC-8 already chose (rule I-3); the Radiall R222M00720 receptacles, Preci-Dip 813 pins, Keystone 3568 blade holders and 3034
cell holder, the panel switches (C&K, APEM, NKK), the relay, the sounder; and those whose value names no part by number (the pin
headers for leads and bench jumpers, the 24 MHz crystals, the 0.5 A PTCs, the 12 AWG wires, the M3 screws). Two land findings
among them: board B L1 and board E L3 (Coilcraft XAL4030 on an XAL4020 land) and board B L101 to L302 (XAL6030 on an XAL6060
land): the makers' land patterns are to be compared before layout.

**F5. Grade NOT READ (6 selections):** the 2512 current-sense parts whose catalogue lines print no temperature range (Milliohm
LR2512D, ROHM GMR100, RALEC LR2512, TA-I RLP25); their makers' sheets are owed.

**F6. Tolerance not stated by the generator:** 157 selections over 1272 rows take rule C-T's or R-T1's default, which each selected
part meets (out 3 lists them per board); the generator owner states a tolerance where the circuit needs another. The voltage of 65
capacitor selections is derived from the intent (rule V-1), as allowed; each basis line is in out 2.

## 5. The drafts (out 4)

`apply_gen_sch_{a,e,p,d,c,b}_lcsc.py`, one per board, each with its board's table of designator to (committed value, LCSC code),
inserted once before `import schlayout, time as _time`. A part keeps its own code where it has one, and a part whose value another
draft has changed keeps none from the table (the generator prints those designators): designators are never changed. Release
guard: `RELEASE.md` reads `released: no`, and each draft refuses the repository's own generator until it names an accepted check.

**Composition, proven on scratch copies:** board A's draft commutes with Layer 4's seven drafts in their change order (L4-E9's
change list: r12, guard, charger, r11, bank, r138, u17) and with d8dec31's mainpb; board E's with the eleven of its change list
(cin, q1, u5_grade, hold, input_limit, backstop, f1, hotswap, entry, solar_guard, aux) and d8dec31's pod; board D's with
d8dec31's ptt; boards P, C and B have no other pending draft. "Commutes" means the generator text after the other drafts then this
one is byte-identical to the text after this one then the others, and it parses. The designators the pending drafts' part calls
change (board A R138, R139, R149, R16, R17; board E 22) are named in out 4: their value key decides at the regeneration.

## 6. The Layer 6 criteria moved (generic rows only)

| Item | Before | Now, for the generic rows of the six boards |
|---|---|---|
| 6.1 maker, MPN, package, grade per fitted part | OPEN (no MPN field) | 1440 of 1657 uncoded rows selected with maker, MPN, package, code and grade; 131 selections DECODED on the maker's table, 91 DOCUMENT_OWED; the specials and open requirements listed: toward PARTLY |
| 6.6 procurement constraints and alternatives | PARTLY | dated stock and price per selection, the set's summed need, an alternative per selection: PARTLY, these rows covered |
| 6.8 a current, versioned BOM with identity per board | PARTLY | NOT MOVED until a board is regenerated with its draft |

## 7. Open items, each with its next action

1. The drafts' release: the coordinator names an accepted check in `RELEASE.md`; each board's generator owner applies its draft
   (after or before the Layer 4 drafts: the order does not matter) and regenerates the board on the box.
2. F1: the tools owner corrects lcsc_fill.py's MAP lines (C15849, C15850, C6119902, C57895, C1588, and the voltage-blind
   `^100n`, `^47n$`) or lets the drafts' codes stand; a regeneration of the certified table follows.
3. F3: the board owners declare the open nets' voltages in the intents, state the links' currents, verify board D's LPF and state
   the panel lamps' intensity; the selections then follow on the same rules.
4. F5 and the 91 DOCUMENT_OWED identities: file the makers' sheets (Samsung CL, FH, Samwha, CCTC, PSA, Milliohm LR2512, ROHM) or add
   DECODED schemes to `part_identities.SCHEMES` where a maker's ordering table fits the tool's layouts.
5. F4's land findings: compare Coilcraft's XAL4020/XAL4030 and XAL6030/XAL6060 land patterns before layout.
6. `pcb_part_identities.yaml`'s block: `build_table.py` does not carry it; after a regeneration of the table,
   `apply_part_identities_block.py --write` puts it back (test_l6r2 fails until it does, by design).
