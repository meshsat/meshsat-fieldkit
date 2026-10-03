# L6R2: exact parts for the generic rows of the six boards (Layer 6 criterion 6.1; MESHSAT-1357, 3 October 2026)

Prototype design: nothing is bought, built, powered or measured. Every figure here is printed by `l6r2_passives.py`
(`l6r2_passives.out`, "out N" below), which reads only this tree and the dated catalogue reading in `inputs/`; this page is the
short form. Based on `fnd/int28` at `a1f696de`. Round 3, the same day on `fnd/l6r2` from `6fe27332`: `lcsc_fill.py`'s table
corrected to this record's selections with a property test (F1), and the three Coilcraft rows drawn on another body's footprint
drafted onto their own (F4); section 8.

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
| A | 382 | 318 (71) | 0 | 64 | 0 | 0 | 0 | 318 |
| E | 111 | 86 (43) | 1 | 16 | 8 | 0 | 0 | 86 |
| P | 50 | 43 (15) | 1 | 6 | 0 | 0 | 0 | 43 |
| D | 137 | 122 (22) | 5 | 8 | 2 | 0 | 0 | 122 |
| C | 83 | 40 (17) | 17 | 22 | 4 | 0 | 0 | 40 |
| B | 894 | 831 (54) | 9 | 54 | 0 | 0 | 0 | 831 |
<!-- page-table:end -->

**1440 of the 1657 uncoded fitted rows are SELECTED**: every deciding requirement met on the catalogue line, stock for five kits
on the board and for the set. No selection is short of stock (the narrowest set margin: ROHM GMR100HJAAFD5L00 for board A's R17,
412 against 5). Every selection names its maker, MPN, package, LCSC code, price at 1 and at the need, grade with its basis, and an
alternative from another maker where one meets every requirement (out 2). Of the 222 selections, **132 bind DECODED** on the
maker's own ordering table and **90 are DOCUMENT_OWED** (the catalogue's identity; the maker's sheet is to be filed).

Since round 3 the code `lcsc_fill.py` fills on each of these lines meets every requirement, so rule I-1 takes it first: the drafts
and the finish step write the same code on every row. One consequence: every 100 nF 0603 row now takes YAGEO CC0603KRX7R0BB104
(100 V), the one code that meets the 100 V rows the line also fills, where round 2 kept the 50 V CC0603KRX7R9BB104 on the rows
that allowed it (and the 1 uF, 1 nF and 47 nF 0603 lines likewise; out 2). The table's last column reads 0 on every board.

## 4. Findings (out 3)

**F1. The finish-time codes failed the identity tool's requirements on 170 rows (corrected in round 3, section 8.1).**
`lcsc_fill.py` fills a blank row at finish from its MAP or the certified table; on these rows the code it filled did not meet the
requirement the netlist and the intent derive:

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

*Corrected:* round 3 changed these lines of `lcsc_fill.py` to this record's selections and added a property test; it finds no
miss on any board (section 8.1). The same codes written explicitly into the generators are another matter (F7).

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
among them, settled in round 3 (section 8.2): board B L1 and board E L3 (Coilcraft XAL4030-472ME drawn on the XAL4020 footprint)
and board B L101 to L302 (XAL6030-332ME on the XAL6060 footprint). The copper is the series' one land; the footprint names the
wrong body; two release-guarded drafts move the three footprint keys.

**F5. Grade NOT READ (6 selections):** the 2512 current-sense parts whose catalogue lines print no temperature range (Milliohm
LR2512D, ROHM GMR100, RALEC LR2512, TA-I RLP25); their makers' sheets are owed.

**F6. Tolerance not stated by the generator:** 157 selections over 1272 rows take rule C-T's or R-T1's default, which each selected
part meets (out 3 lists them per board); the generator owner states a tolerance where the circuit needs another. The voltage of 65
capacitor selections is derived from the intent (rule V-1), as allowed; each basis line is in out 2.

**F7. The same failing codes written into the generators (17 rows, round 3; outside this record's uncoded rows):** board A C75
(C14663, 50 V where V-1 asks more), C208 and C209 (C15849, X5R), C69, C134, C141, C191 (C1588, X7R 10 % where C-D2 asks C0G);
board C C1 and C2 (C15850, X5R); board D C61, C64, C65, C71 (C15849); board E C56, C57, C58 (C15849) and C53 (C1588). These carry
an explicit code in their generator call, so `lcsc_fill.py` never fills them; the generator owner restates each code (Layer 8),
or states the dielectric or rating the circuit needs where it is not the rule's default. Not drafted here.

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

Round 3 adds two LAND drafts, `apply_gen_sch_b_xal_land.py` and `apply_gen_sch_e_xal_land.py` (logic in `l6r2_land.py`, the same
release guard), section 8.2. Each commutes with every other pending draft of its generator and with this record's own LCSC draft,
alone and all applied together (out 6).

## 6. The Layer 6 criteria moved (generic rows only)

| Item | Before | Now, for the generic rows of the six boards |
|---|---|---|
| 6.1 maker, MPN, package, grade per fitted part | OPEN (no MPN field) | 1440 of 1657 uncoded rows selected with maker, MPN, package, code and grade; 131 selections DECODED on the maker's table, 91 DOCUMENT_OWED; the specials and open requirements listed: toward PARTLY |
| 6.6 procurement constraints and alternatives | PARTLY | dated stock and price per selection, the set's summed need, an alternative per selection: PARTLY, these rows covered |
| 6.8 a current, versioned BOM with identity per board | PARTLY | NOT MOVED until a board is regenerated with its draft |
| 6.4 a part on the land and body of its own footprint (round 3) | the three Coilcraft rows of F4 on another series' footprint | the copper proven the maker's land; the footprint keys drafted (release-guarded): toward PARTLY until applied |

## 7. Open items, each with its next action

1. The drafts' release: the coordinator names an accepted check in `RELEASE.md`; each board's generator owner applies its draft
   (after or before the Layer 4 drafts: the order does not matter) and regenerates the board on the box.
2. F1: done in round 3 (section 8.1). What follows from it is listed there: three Layer 4 records that pin `lcsc_fill.py` re-pin
   it, the deliverables take the new codes when each board is finished again, the sweep re-takes the "order codes" verdicts.
3. F3: the board owners declare the open nets' voltages in the intents, state the links' currents, verify board D's LPF and state
   the panel lamps' intensity; the selections then follow on the same rules.
4. F5 and the 91 DOCUMENT_OWED identities: file the makers' sheets (Samsung CL, FH, Samwha, CCTC, PSA, Milliohm LR2512, ROHM) or add
   DECODED schemes to `part_identities.SCHEMES` where a maker's ordering table fits the tool's layouts.
5. F4's land findings: compared and drafted in round 3 (section 8.2); the release, the regeneration of boards B and E, and the
   z-stack's re-read of the new models follow.
6. `pcb_part_identities.yaml`'s block: `build_table.py` does not carry it; after a regeneration of the table,
   `apply_part_identities_block.py --write` puts it back (test_l6r2 fails until it does, by design).

## 8. Round 3 (3 October 2026): `lcsc_fill.py`'s table and the Coilcraft lands

### 8.1 F1, a tools defect: the finish-time table

Twelve lines of `lcsc_fill.py`'s MAP changed (eight codes replaced, four lines added), each to this record's selection for the
rows the line fills, so the finish step and the drafts agree:

| MAP line (value, land) | Was | Now | The rule it now meets, the rows |
|---|---|---|---|
| `^100n` 0603 | C14663 YAGEO CC0603KRX7R9BB104, 50 V | C113803 YAGEO CC0603KRX7R0BB104, 100 V X7R 10 % | V-1: E C5, B C29 to C32 need 100 V |
| `^1u$` 0603 | C15849 Samsung CL10A105KB8NNNC, X5R | C559769 YAGEO CC0603KRX7R9BB105, 50 V X7R 10 % | C-D3 |
| `^10u$` 0805 | C15850 Samsung CL21A106KAYNNNE, X5R | C326595 YAGEO CC0805KKX7R7BB106, 16 V X7R 10 % | C-D3 |
| `^22u 6\.3V` 0805 | C6119902 HRE CGA0805X5R226M6R3MT, X5R | C53133025 CCTC TCC0805X7R226M100FT, 10 V X7R 20 % | C-D3 |
| `^2\.2u$` 0603 | C57895 Samsung CL10A225KA8NNNC, X5R | C513691 YAGEO CC0603KRX7R6BB225, 10 V X7R | C-D3 |
| `^1n$` 0603 | C1588 Samsung CL10B102KB8NNNC, X7R 10 % | C113793 YAGEO CC0603JRNPO0BN102, 100 V C0G 5 % | C-D2 |
| `^47n$` 0603 | C1622 Samsung CL10B473KB8NNNC, 50 V | C576852 YAGEO CC0603KRX7R0BB473, 100 V | V-1: A C77 |
| `^0\.47R 1%$` 0603 | C23411 UNI-ROYAL 0603WAF470LT5E, 800 ppm/K | C414503 UNI-ROYAL CS03W5F470LT5E | R-S1: C R43 |
| `^5mOhm 1% 2512 \(RSR` 2512 (new, before the 5 mOhm line) | C500739 LR2512D-3W-5mR-1%, 3 W | C20108830 ROHM GMR100HJAAFD5L00, 5 W | R-P: A R17 |
| `^27 1% 2010$` 2010 (new) | the certified table's C2960829 FRC2010J270, 5 % | C421874 UNI-ROYAL 201007F270JT4E, 1 % | the stated 1 %: D R54, R56 |
| `^600R 2A ferrite` 0805 (new) | the certified table's C1017 GZ2012D601TF, 500 mA | C21519 TDK MPZ2012S601AT000, 2 A | the stated 2 A: D FB1 |
| `^15p NP0` 0603 (new) | no line: the row stayed blank and board A's finish refused | C107037 YAGEO CC0603JRNPO9BN150, 50 V NP0 5 % | A C27 (S-117's CH_COMP2) |

The two X5R lines rule C-D3b keeps (47 uF 25 V and 100 uF 10 V on 1206, F2) are declared in a new dict `CD3B_X5R` beside the MAP:
data for the test, read by nothing in the script. The interface is unchanged: the same arguments (`<bom.csv>`, `--no-components`),
the same environment (`VERDICT_DIR`, `LCSC_ALLOW`), the same files read, the same refusals, exit codes and verdict.

**The property test** (`tests/test_lcsc_fill_requirements.py`) runs the real `lcsc_fill.py` on a one-line-per-reference BOM of each
board's committed netlist (a scratch directory, its own verdict folder, an empty allow list), classifies every uncoded fitted row
with this record's classifier, and judges the code lcsc_fill wrote with this record's check on the identity tool's requirements
over the dated catalogue reading; a generic row it leaves blank, a code it then rejects itself, and a code with no catalogue line
are misses too. **Result: 1440 generic rows judged (A 318, E 86, P 43, D 122, C 40, B 831), 0 misses**; 16 rows whose requirement
is OPEN are counted, not judged. The same test on the table before round 3: 171 misses (A 21, E 7, P 0, D 29, C 5, B 109), the 170
rows of F1 and board A C27. A copy of the script with the 100 nF line put back to the 50 V part is caught on a 100 V fixture row.

**The callers, and what each now gets:**

| Caller | What it gets now |
|---|---|
| `finish_board.sh` (line 22) | A fresh BOM's blank lines take the corrected codes; board A's C27 is filled instead of refusing the finish |
| `gate_sweep.sh` (the "order codes" stage, lines 291 and 301) | It runs on a copy of the deliverable BOM, whose lines already carry codes, and lcsc_fill never refills a coded line: a deliverable cut before this commit keeps the old codes until its board is finished again; the refusals (block list, certified WRONG verdicts, declared mismatches) are as before |
| `make_handoff.py`, `verify_deliverable.py` | They read lcsc_fill's status file and the allow lists: unchanged |
| `rules_status.py` (line 803) | `lcsc_fill.py` is the writer of the "order codes" verdicts and its digest stamps them: the verdicts on file read stale until the sweep re-takes them on the box |
| `export_jlc.sh`, `apply_netlist_values.py`, `jlc_certify.py`, `verdict.py`, `execution_paths.py`, `closer_audit.py`, `kb/kb_parts.py` | They name the script in prose or index it: nothing they compute moves |
| The generators | A row whose generator call carries a code is never filled (F7) |

**Records that read `lcsc_fill.py`** (findings to their authors; no Layer 4 record is edited here):

- `l4e9/l4e9_power_path.py`, `l4e8/ripple_dense.py` and `l4e12/l4e12_thermal.py` pin its sha256 (`6888362e`), so each refuses until
  it is re-pinned. What each reads of it: L4-E8 the 40.2k 0603 line (unchanged) and the 0603 pF and nF capacitor lines for its Cc2
  search, whose pick (3.3 nF, C1613) is unchanged; L4-E12 only the pin; L4-E9 the 10 uF 50 V 1210 line (unchanged) and the `^100n`
  0603 line as board E C5's fill mapping, which it then requires `gen_sch_e.py`'s comment to name ("YAGEO CC0603KRX7R9BB104, LCSC
  <code>"). With the code now C113803 that requirement fails: C5 is now CC0603KRX7R0BB104 (100 V), the same YAGEO X7R K series
  on the same sheet, and the L4-E9 author re-reads C5 on it.
- `l3plane/vbus20_range.py`, `r11dep/r11_dep.py` and `l4e4/l4e4_limits.py` read lines this round did not touch and do not pin the
  file: each was re-run here and reproduces its committed output byte for byte.
- `l4e6/apply_lcsc_fill_r12.py`, L4-E6's draft on this file, still applies (its anchor, the 5 mOhm line, is unchanged and the new
  RSR line sits before it): checked on a copy. Once it is applied and board A is regenerated, the property test judges its
  12 mOhm 3 W line on R12 like any other.

### 8.2 F4's lands, criterion 6.4 (out 6)

| Rows | The value names | Drawn on | The maker's sheet | KiCad 9.0.9 | Defect | Correction |
|---|---|---|---|---|---|---|
| board B L1, board E L3 | Coilcraft XAL4030-472ME, 4.7 uH, at most 3.1 mm high | L_Coilcraft_XAL4020-XXX | one recommended land for XAL40xx: 0.98 x 3.4 mm pads at 2.37 mm (`coilcraft-xal40xx-series.pdf` p.4); XAL4020 ends at -222 (2.2 uH, 2.1 mm), so no 4.7 uH XAL4020 exists (p.1) | XAL4020 and XAL4030 footprints: identical pads, courtyard, fab and silk; models 2.1 and 3.1 mm | the footprint's body is 1.0 mm lower than the part | the footprint key: "L4020" to "L4030" |
| board B L101, L102, L201, L202, L301, L302 (buck33) | Coilcraft XAL6030-332ME, 3.3 uH, at most 3.1 mm high | L_Coilcraft_XAL6060-XXX | one recommended land for XAL60xx: 1.43 x 5.50 mm pads at 4.04 mm (`coilcraft-xal60xx-series.pdf` p.4); XAL6060 starts at -472 (4.7 uH, 6.1 mm), so no 3.3 uH XAL6060 exists (p.1) | XAL6030 and XAL6060 footprints: identical pads, courtyard, fab and silk; models 3.1 and 6.1 mm | the footprint's body is 3.0 mm higher than the part | the footprint key: "L6060" to "L6030" |

So the value is right and the land's copper is right; the footprint key names another body. No Layer 4 record selected these
inductors (they come with the generators' own recipes: board B's AP64500 3.3 V stages and its AP63203 +3V3_DEV buck, board E's
AP63205 +5V_E6 buck), so the correction is this record's draft and not a finding to a Layer 4 author. `apply_gen_sch_b_xal_land.py` adds the "L4030" and
"L6030" keys to board B's footprint map, moves L1 and buck33's inductor to them and corrects buck33's docstring ("3.3 uH XAL6060"
to "XAL6030"); `apply_gen_sch_e_xal_land.py` adds "L4030" to board E's map and moves L3. The keys "L4020" and "L6060" stay (board
B's XAL4020-222ME rows keep "L4020"). Designators, values, nets and codes do not change, and the copper does not move, so a
regenerated board's placement and route need no change. Both refuse the repository's generators until `RELEASE.md` is released;
a second application is refused; each commutes with every pending draft of its generator (board E: the eleven of L4-E9's change
list, d8dec31's pod, this record's LCSC draft, and all of them together; board B: this record's LCSC draft).

The KiCad facts are a reading (`read_kicad_footprints.py` to `inputs/kicad-xal-footprints-9.0.9.json`: the four files' URLs at the
library's 9.0.9 tag, sha256, descriptions, pads, outlines and model paths; the files themselves are not filed).

Downstream, not done here: when boards B and E are regenerated with the drafts, `v2/cad/zstack.py` reads the new models (its
`zstack-models.json` holds no XAL6030 model yet; the box reads it). Board B's six buck33 inductors drop from 6.1 to 3.1 mm, which
removes the item `CASE-FIT-UNCERTAINTIES.md` section 4 counts ("six XAL6060 inductors of 6.10 sat under 6.0 envelopes"), and B L1
and E L3 rise from 2.1 to 3.1 mm.
