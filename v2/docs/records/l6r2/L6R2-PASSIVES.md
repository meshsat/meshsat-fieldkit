# L6R2: exact parts for the generic rows of the six boards (Layer 6 criterion 6.1; MESHSAT-1357, 3 October 2026)

Prototype design: nothing is bought, built, powered or measured. Every figure here is printed by `l6r2_passives.py`
(`l6r2_passives.out`, "out N" below), which reads only this tree and the dated catalogue reading in `inputs/`; this page is the
short form. Based on `fnd/int28` at `a1f696de`. Round 3, the same day on `fnd/l6r2` from `6fe27332`: `lcsc_fill.py`'s table
corrected to this record's selections with a property test (F1), and the three Coilcraft rows drawn on another body's footprint
drafted onto their own (F4); section 8. Round 4, from `b257a730`: the codes written in the generators' calls corrected in the LCSC
drafts and the property test extended to them (F7); section 8.3. Round 5, from `f8328b5b`: the open requirements of F3 derived at
the desk where the circuit bounds them, drafted as intent declarations, and the rows they close selected; section 8.4. Since round
5 the record judges its rows as if those declarations were applied (`l6r2_intent.overlay`).

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
| A | 382 | 318 (71) | 0 | 64 | 0 | 0 | 0 | 331 |
| E | 111 | 87 (44) | 0 | 16 | 8 | 0 | 0 | 91 |
| P | 50 | 44 (15) | 0 | 6 | 0 | 0 | 0 | 44 |
| D | 137 | 125 (24) | 2 | 8 | 2 | 0 | 0 | 129 |
| C | 83 | 40 (17) | 17 | 22 | 4 | 0 | 0 | 42 |
| B | 894 | 840 (56) | 0 | 54 | 0 | 0 | 0 | 841 |
<!-- page-table:end -->

**1454 of the 1657 uncoded fitted rows are SELECTED** (1440 before round 5's declarations): every deciding requirement met on the catalogue line, stock for five kits
on the board and for the set. No selection is short of stock (the narrowest set margin: ROHM GMR100HJAAFD5L00 for board A's R17,
412 against 5). Every selection names its maker, MPN, package, LCSC code, price at 1 and at the need, grade with its basis, and an
alternative from another maker where one meets every requirement (out 2). Of the 227 selections, **134 bind DECODED** on the
maker's own ordering table and **93 are DOCUMENT_OWED** (the catalogue's identity; the maker's sheet is to be filed).

Since round 3 the code `lcsc_fill.py` fills on each of these lines meets every requirement, so rule I-1 takes it first: the drafts
and the finish step write the same code on every row. One consequence: every 100 nF 0603 row now takes YAGEO CC0603KRX7R0BB104
(100 V), the one code that meets the 100 V rows the line also fills, where round 2 kept the 50 V CC0603KRX7R9BB104 on the rows
that allowed it (and the 1 uF, 1 nF and 47 nF 0603 lines likewise; out 2). The column of finish-time failures reads 0 on every board; the drafts' designators include round 4's corrections (section 8.3).

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

**F3. Requirements open, never guessed (33 rows; 14 closed in round 5, section 8.4, 19 stay open):** board P C9 and board D C46 to C48 and board B C161, C162, C500 to C505 (no
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

**F7. Failing codes written into the generators' calls (corrected in round 4, section 8.3):** round 3 found 17 rows carrying the
same failing codes as `lcsc_fill.py`'s old table, written explicitly in their generator calls, which lcsc_fill never fills. Round 4
judged every code a generator call writes on a generic row (370 rows) and found 26 that fail: the 17, seven more, and two with no
meeting line in the reading. 24 are corrected in the boards' LCSC drafts; two stay findings (section 8.3).

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
   F7: done in round 4 (section 8.3) but for board B C529 and C530, whose tolerance no catalogue line read prints in percent.
3. F3: round 5 drafted the declarations a desk can derive (section 8.4) and selected the 14 rows they and the held Uniroyal jumper
   table close; the integrator applies the three intent drafts at set 28. Open: board D L1 and L2 (the PA's mismatch case and the
   inductor's SRF and Q), board C's 17 lamps (the required luminance and the light guide's transmission).
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

### 8.3 Round 4: the codes the generators' calls write (F7, out 7)

Every fitted generic row whose generator call writes a code is judged by the same checks on the same dated reading (supplemented on
3 October 2026 with the 76 written codes it lacked and 14 keywords). A failing code gets a correction by this record's preference:
its round 2 selection for the same line (value and land) on the same board, then on another board, then the code `lcsc_fill.py`
fills on that line, then a line of the keyword searches; every requirement met, stock for five kits, never a refused code. The
corrections are entries in the boards' LCSC drafts with a third field, the code they replace: the block changes a part's code only
where its value is the committed one AND it carries exactly that code (a part whose value or code another draft has moved keeps
what it has, and the generator prints it). Nothing is reselected that a Layer 4 record selected: no Layer 4 record names any of the
replaced codes as its own choice.

| Board, rows | Value | Written (fails) | Corrected to | Source |
|---|---|---|---|---|
| A C75 | 100 nF 0603 | C14663 YAGEO CC0603KRX7R9BB104, 50 V (100 V needed) | C113803 YAGEO CC0603KRX7R0BB104, 100 V | round 2, same line |
| A C208, C209 | 1 uF 0603 | C15849 Samsung CL10A105KB8NNNC, X5R | C559769 YAGEO CC0603KRX7R9BB105, X7R | round 2, same line |
| A C69, C134, C141, C191 | 1 nF 0603 | C1588 Samsung CL10B102KB8NNNC, X7R 10 % | C113793 YAGEO CC0603JRNPO0BN102, C0G 5 % 100 V | round 2, same line |
| C C1, C2 | 10 uF 0805 | C15850 Samsung CL21A106KAYNNNE, X5R | C326595 YAGEO CC0805KKX7R7BB106, X7R | round 2, same line (board D) |
| D C61, C64, C65, C71 | 1 uF 0603 | C15849, X5R | C559769, X7R | round 2, same line |
| E C56, C57, C58 | 1 uF 0603 | C15849, X5R | C559769, X7R | round 2, same line |
| E C53 | 1 nF 0603 | C1588, X7R 10 % | C113793, C0G 5 % | round 2, same line |
| A C5, C86 (found by the extended test) | 220 nF 0603 | C160828 Samsung CL10B224KO8NNNC, 16 V (50 V and 35 V needed) | C344195 CCTC TCC0603X7R224K500CT, 50 V X7R 10 % | round 2, same line |
| A C7 (found) | 4.7 uF 0805 | C354262 YAGEO CC0805KKX7R8BB475, 25 V (50 V needed) | C694229 TDK CGA4J1X7R1H475KT0Y0N, 50 V X7R | keyword search |
| A C76 (found) | 470 pF 0603 | C27694 Samsung CL10C471JB8NNNC, 50 V (100 V needed) | C326973 YAGEO CC0603JRNPO0BN471, 100 V C0G | keyword search |
| A C150 (found) | 560 pF 0603 | C43962 FH 0603CG561J500NT, 50 V (100 V needed) | C513644 YAGEO CC0603JRNPO0BN561, 100 V C0G | keyword search |
| A C152 (found) | 680 nF 0603 | C107067 YAGEO CC0603KRX7R7BB684, 16 V (25 V needed) | C2838708 YAGEO CC0603KRX7R8BB684, 25 V | keyword search |
| B C35 (found) | 10 uF 100 V 1210 | C576517 Murata GRM32EC72A106KE05L, X7S | C49296968 TDK C3225X7R2A106KT000E, X7R 100 V | keyword search |
| B C529, C530 | 9.1 pF and 4.7 pF 50 V C0G 0402 | C526972, C325453 YAGEO CC0402BRNPO9BN9R1 and 4R7 | none: FINDING | no line read prints the tolerance in percent (rule C-T asks 5 % of a C0G); the generator's code stands, the owner states the tolerance in pF |
| C C31 | 4.7 uF 25 V 0603 | C90057 Murata GRM188R61E475KE11D, X5R | kept | rule C-D3b: no X7R line read meets the value, land and rating with stock; the hot-spot question OPEN |

The rated voltages asked are the identity tool's (rule V-1 on the intent or the nets' bound at the 20 percent margin); where a
generator comment states a lower working voltage than the bound (A C152: "PDT is rated 2.7 V"), the owner can declare it in the
intent and the requirement follows, but a higher-rated part of the same value, dielectric and tolerance is never worse. One
correction sits inside a Layer 4 record's subject: A C5 is the front-end stage's Cc1 (220 nF), which L4-E8 keeps as drawn ("Rc1 15k
and Cc1 220n stay"); its value, X7R class and 10 % tolerance are unchanged, only the rating (16 V to 50 V) and the maker, and
L4-E8's draft on the same call (`apply_gen_sch_a_bank.py`) still applies and commutes.

**Composition:** each corrected board's LCSC draft (A, B, C, D, E) commutes with every pending draft of its generator (A: L4-E9's
seven and d8dec31's mainpb; E: the eleven and d8dec31's pod; D: d8dec31's ptt), and with this record's XAL land drafts on B and E,
alone and all together (out 4 and 6). Of the corrected designators only A C5 sits on a line a pending draft changes (L4-E8's, above,
which keeps its value and code, so the entry still applies after it).

**The extended property test** (`t_every_code_a_generator_call_writes_meets_the_requirements_as_the_drafts_leave_it`): for every
fitted generic row whose call writes a code, the code as this record's draft leaves it meets every requirement on the reading; a
code may stay failing only where NO line of the whole reading meets the requirement with stock (checked against the reading, not
taken from the record). **Result: 370 written codes judged (A 101, E 28, P 6, D 41, C 66, B 128), 0 misses**; 9 rows with an OPEN
requirement counted, not judged; three kept by the rule (C C31 under C-D3b, B C529 and C530 with no meeting line). On the committed
generators without the drafts the same judge reads 24 misses (A 13, E 4, D 4, C 2, B 1).

**For set 28's merge (not done here):** `l4e9/l4e9_power_path.py`, `l4e8/ripple_dense.py` and `l4e12/l4e12_thermal.py` pin
`lcsc_fill.py`'s old sha256 `6888362e`; the integrator re-pins them at the merge. L4-E9's reading of board E C5's fill mapping
(the `^100n` 0603 line) now gives **C113803, YAGEO CC0603KRX7R0BB104, 100 V** (it was C14663, CC0603KRX7R9BB104, 50 V): the same
YAGEO X7R K series on the same sheet, so its tolerance, temperature and endurance figures are the same rows; the comment in
`gen_sch_e.py` (line 713) that L4-E9 requires to name C5's part still names C14663 and is the generator owner's to restate.

### 8.4 Round 5: the open requirements of F3 (out 8)

Each figure below is derived from the circuit (the generator), the board's committed intent (the rails that drive the net, read
from the intent file when the declarations are built) and the makers' documents in the tree, with its operating case. They are
drafted as `intent.node` declarations in `apply_gen_sch_{p,d,b}_intent.py` (inserted once before `_intent.write(OUT, PROJECT, P)`,
release-guarded like the record's other drafts; each commutes with every pending draft of its generator: board D's ptt, and this
record's LCSC and XAL land drafts). The record now judges its rows under them (`l6r2_intent.overlay`), so the rows they close are
selected on the same rules.

| Rows | Net, derived figure | Basis and operating case | Part selected |
|---|---|---|---|
| P C9 (100 nF) | SRP_F and SRN_F, -0.2 to +0.2 V each; 0.40 V across C9 | the BQ4050's SRP and SRN inputs through R8 and R9 (100 R) from the two ends of the 2 mOhm shunt R10: SLUSC67B 6.3 recommends both within +-0.2 V; 36 mV at the pack's 18 A peak; the short-circuit trips SCD1 and SCC at most 200 mV (6.31). Case: discharge or charge up to the trip | C113803 YAGEO CC0603KRX7R0BB104 (the 100 nF 0603 line; 6.3 V asked) |
| D C46 (1 uF) | MICAMP_AC, -2.615 to +2.615 V | U8 (TLV9062) sits at VREF, half of +5V_D8's declared 5.23 V, and swings within its supply; the coupled side's DC is ground (R45, R47). Case: full-scale transmit audio. 7.85 V across C46 by rule V-1's node bound | C559769 YAGEO CC0603KRX7R9BB105 (10 V asked) |
| D C47 (1 uF) | PCM_R_AC, -3.6 to +3.6 V | the PCM2912A's VOUTR swings within PCM_VCCR (declared 3.6 V); the full regulator output is taken, not half (the output's centre is not taken from the sheet). Case: full-scale playback. 8.83 V across C47 | C559769 (16 V asked) |
| D C48 (1 uF) | MIC_SUM, -3.6 to +3.6 V | the summing node of R45, R46, R47 (10k each, R47 to ground) cannot exceed the larger of its two sources. 8.60 V across C48 against MIC_IN (the SA868's pin, bounded at 5.0 V) | C559769 (16 V asked) |
| B C161, C162 (100 nF) | LIME_SSTX_P and _N, 0 to +5.0 V | the LimeSDR Mini 2.4 behind J_LIME has no supply but the receptacle's VBUS, +5V_LIME (declared 5.0 V), so its receive pins stay within it (rule V-1's premise for an active part, applied to the module behind the connector; its USB 3.0 controller is an FTDI FT601, whose sheet refused the runner, 403). Case: enumerated at USB 3 speed. 5.0 V across | C60474 YAGEO CC0402KRX7R7BB104 (the board's 100 nF 0402 selection; 6.3 V asked) |
| B C500 to C505 (22 pF) | W1A/W3A/WA and W1B/W3B/WB card and antenna leads, -10.62 to +10.62 V; the SKY13351 ports SWA/SWB O1, O2, IN, -10.62 to +13.92 V | the AW7915-AED's highest output, 23 dBm +1.5 dB (11b, its datasheet V1.0 p.3) = 24.5 dBm, 5.31 V peak into 50 Ohm and 10.62 V on a fully reflecting lead (the case LORA_ANT declares); the switch's ports, which its sheet requires DC blocked, at most their control voltage (+3V3_DEV, 3.3 V) plus that peak. Case: transmit at full power into any load. 24.54 V across | C106203 YAGEO CC0402JRNPO9BN220, 50 V NP0 (35 V asked) |
| B R13 (0 R 2512) | POE_P, 0.60 A | already declared: the POE_P rail's peak, its load T1 (the PoE port's 0.60 A). No new declaration | C25469 UNI-ROYAL 25121WJ0000T4E: a 2512 jumper's rated current 2 A (the held Uniroyal sheet's section 7 table) |
| E R51 (0 R 0603) | IMU_CSB, 0.60 A taken | R51 feeds only U15's CSB input (BMI270); its real current is that pin's leakage. The record keeps the identity tool's conservative 0.60 A (+3V3_E6's declared peak): a tighter figure needs IMU_CSB declared as a rail, which the intent treats as a supply (drop budgets, PWR-001), so it is not drafted | C21189 UNI-ROYAL 0603WAF0000T5E: a 0603 jumper's rated current 1 A (same table) |

The two links were open because no catalogue line prints a jumper's current; the held Uniroyal thick-film sheet does (section 7,
"Rated Current of Jumper": 0603 1 A, 2512 2 A), and the check now reads it for UNI-ROYAL zero-ohm lines only (`jumper_rating`).

**Board D L1 and L2 stay OPEN, the filter VERIFIED.** The ladder C58 22 pF, L1 68 nH, C59 39 pF, L2 68 nH, C60 22 pF is a
fifth-order 0.1 dB Chebyshev low-pass with a corner near 166 MHz (g = 1.1468, 1.3712, 1.9750 give 22 pF, 66 nH and 38 pF at 50
Ohm). With ideal parts into 50 Ohm, at the corners of L +-2 % and C +-5 %: at most 0.05 dB lost from 144 to 146 MHz with at least
19.8 dB return loss; the second harmonic (290 MHz) down at least 27.2 dB, the third (435 MHz) 47.1 dB. So the values fit the
stated purpose. The current the inductors carry is not the generator comment's 775 mA (the load current): at 30 W into a matched
load the shunt capacitors' reactive current flows through them, **1.03 A RMS in L1 and 1.10 A RMS in L2** at 145 MHz, against the
1.2 A of the Murata LQW2BAN68NG00L the comment names. The exact questions that keep them open: (1) is the PA's operation into a
fully reflecting antenna (the case the 110 V declarations of the filter nets take) a sustained case, and at what forward power does
the PA's own protection hold it (MESHSAT-818)? (2) the inductor's self-resonance above 435 MHz and its Q at 145 MHz, from the
maker's sheet, which is not held.

**Board C's 17 panel lamps stay OPEN** (a Layer 7, panel, matter). The missing facts: the luminance (or intensity) each lamp must
give at the face plate in DAY ("sunlight viewable") and the most it may give in NVG; PANEL.md section 8 states the dimming duties
(100, 15 and 2 percent) and no luminance; and the transmission of the Mentor LL14 light guide, whose held sheet prints the guide's
geometry and a table of LEDs but no transmission. The lamp's intensity is then the required luminance over that transmission.

**For set 28:** the integrator applies `apply_gen_sch_p_intent.py`, `apply_gen_sch_d_intent.py` and `apply_gen_sch_b_intent.py`
with the record's other drafts of those generators (the order does not matter); the regenerated intents then carry what the record
already judges under. The property tests run lcsc_fill's choice under the declarations too (1454 rows judged, 0 misses).
