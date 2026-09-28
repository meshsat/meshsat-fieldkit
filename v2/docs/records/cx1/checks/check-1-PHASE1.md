# PHASE 1 (blind): the checker's own reading of IF-AB-POWER, finding I-03

AI review, MESHSAT-1357, written 28 September 2026 19:22 CEST by an independent checker session BEFORE any file
under `v2/docs/records/cx1/` was opened. Prototype framing: nothing built, ordered or measured. Every figure below
is from a document held in the cx1 worktree (commit b1c744db, base 6b419b02) or is arithmetic on such a figure;
the script `phase1.py` beside this page reproduces the arithmetic (its output `phase1.out`, inputs pinned by sha256).

## 0. The named mode

PS-ALLTX, CONOPS.md section 5 case S3: "every transmitter keyed" over S2 ("three modules loaded, 5G and WiFi link
passing traffic, Iridium and LoRa sending"), the monitor full, the fans on, **the outlets off** (0 W, the D-11
interlock: `U30` OUTLET_OK low while the PA keys, POE_EN and PD_EN gated, S-14), the standby WiFi card off, the
other loads at typical. Requirement REQ-018 (`pcb_requirements.yaml:6203`), rulings D-11, choices SC-10 and SC-35.
The mode's rail currents in the record: `feasibility/POWER-THERMAL.md` lines 178 to 181 and 706 to 710 (PS-ALLTX
PLAN / HIGH: +5V_S1 4.65 / 4.66 A, +5V_DEV 5.89 / 7.8 A; +5V_S2 is NOT PLOTTED there, line 197).

## 1. The interface as written

`pcb_interfaces.yaml` `board_to_board.contracts.IF-AB-POWER` (line 367): five JST-VH pairs, "16 and 18 AWG, 150 mm";
pins 1 = rail, 2 = GND on both ends. Converters on A: +5V_S1 and +5V_S3 on AP64500 (U4, U6), +5V_S2 and +5V_DEV on
LM5176 stages (U5, U7) "with a 7.2 to 9.5 A average current limit", +54V_POE on an LM5176 boost (U16).
`contact_rating: "JST-VH is a 10 A class family per the generator descriptions; datasheet not held (TBD)"`: the
catalogue IS held at `v2/vendor/connectors/jst-vh-catalogue.pdf` (6 pages), so that TBD is stale.

Leads (ASSEMBLY.md section 4): rows 132 to 134: slot rails 16 AWG 150 mm, device rail 16 AWG 150 mm, PoE feed
18 AWG 150 mm, "VH crimp both ends". Both ends fit the footprint `JST_VH_B2P-VH_1x02_P3.96mm_Vertical` (gen_sch_a.py:155,
193; gen_sch_b.py:323), the B2P-VH top-entry STANDARD header (catalogue p.3 row "2 B2P-VH").

Declarations, parsed from the intent files (A written 2026-09-27 14:51, B 15:05):

| rail | A typ / peak (A) | A loads | B typ / peak (A) | B loads sum |
|---|---|---|---|---|
| +5V_S1 | 2.5 / 5.0 | J_5V_S1 5.0 | 2.5 / 5.0 | 4.751 (6 loads) |
| +5V_S2 | 2.5 / 5.0 | J_5V_S2 5.0 | 4.2 / 5.0 | 4.751 (6 loads) |
| +5V_S3 | 2.5 / 5.0 | J_5V_S3 5.0 | 2.5 / 5.0 | 4.751 (6 loads) |
| +5V_DEV | 4.0 / 6.9 | J_5V_DEV 3.2, U23 0.5, U32 0.3 | 3.8 / 6.0 | 5.180 (19 loads) |
| +54V_POE | 0.3 / 0.6 | J_54V 0.3 | 0.3 / 0.6 | 0.600 (R13 0.593, U5 0.007) |

Where the declarations are written: gen_sch_a.py:104-113 (slot rails, one loop for S1 to S3, "5 A peak at the
module", the AP64500-era text kept for S2 after its converter changed at F-PR-04), :120 (+5V_DEV), :132 (+54V_POE);
gen_sch_b.py:47-54 (`_SLOT_LOADS`), :79 (slot rails, 4.2 A for slot 2, peak 5.0 for all three), :85-97 (+5V_DEV),
:256 (+54V_POE). Sense resistors on A: S2 `isns="6m"` R35 (gen_sch_a.py:1006), SD `isns="6m"` R43 (:1015), POE
`isns="20m"` R71 (:1112); the 5 mOhm R170 / R177 are the cycle-by-cycle CS shunts, not the average loop's.

## 2. The maker figures used (document, revision, page)

| figure | document | where |
|---|---|---|
| VSNS average current loop regulation target 43 / 50 / 57 mV (min / typ / max, -40 to 125 C junction) | TI LM5176 SNVSAI1D, June 2017 revised August 2021 | 6.5 Electrical Characteristics, PDF p.7, CONSTANT CURRENT LOOP |
| what the loop does: "the output voltage of the converter decreases to limit the input or output current", ICL(AVG) = 50 mV / RSNS (Equation 4) | same | 7.3.6, PDF p.17 |
| "5A Continuous Output Current" | Diodes AP64500 DS41979 Rev. 5-2 | p.1 Features |
| IPEAK_LIMIT HS peak current limit 6.8 / 8 / 9.2 A; theta-JA 45 C/W SO-8EP | same | p.6 Electrical Characteristics; p.5 Thermal Resistance |
| "Current rating: 10 A AC/DC *When using AWG #16 with the standard type header"; "7A AC/DC *When using AWG #18 with the shrouded type header"; contact resistance initial 10 mOhm max, after test 20 mOhm max; applicable wire AWG 22 to 16 | JST VH catalogue (held, 6 pages) | p.1 |
| contact SVH-41T-P1.1 "#20 to #16 (0.5 to 1.25)" mm2; SVH-21T-P1.1 "#22 to #18 (0.33 to 0.83)" mm2 | same | p.2 |
| "Ensure the continuous current capability of the power supply is 3.0 A at least" | Quectel RM520N-GL Hardware Design V1.0, 2022-07-15 | 3.3.1, PDF p.28 (printed 27) |
| "the peak current capability of the power supply is 4 A at least" | Quectel RM520N Series Hardware Design V1.1, 2023-03-16 (held beside the -GL v1.0; the v1.0 -GL text has NO peak figure, and v1.1's history p.5 item 4 says the peak requirement was ADDED in 1.1) | 3.3.1, PDF p.30 (printed 29) |
| averaged current consumption, largest row 1512 mA (LTE CA, 24 dBm) | RM520N-GL HD V1.0 | Table 37, PDF p.66-67 (printed 65-66) |
| CM5 "Operating power consumption is typically around 900 mA"; Table 9 Iload 900 mA typical, no minimum, no maximum, "Actual figures greatly depend on the end application" | Raspberry Pi CM5 datasheet, release 3 (27 Nov 2024) | 3.3 PDF p.16 (printed 15); 4.3.3 Table 9 PDF p.27-28 (printed 26-27) |
| "Single 5 V power input with USB power delivery support for up to 5 A at 5 V" (an input capability, not a draw) | same | 1.3 PDF p.6 |
| rho_cu 1.72e-8 ohm m | the tree's own constant, `v2/ecad/tools/dc_drop.py:23` | (the tree holds no AWG resistance table; the conductor areas come from the JST catalogue p.2, and the ASTM B258 formula, not held, gives 1.309 and 0.823 mm2) |

## 3. Per rail

### +5V_S2 (the first disagreement)

Loads behind board B's end, in PS-ALLTX (slot 2 loaded, the RM520N-GL transmitting), each with its kind:

| load | figure at the load | kind | at 5.1 V on the slot rail |
|---|---|---|---|
| CM5 U31A | 0.9 A operating | maker's TYPICAL, no maximum published | 0.9 A (project allowance 1.6 A: "typical with headroom", gen_sch_b.py:44) |
| 5G card buck U203 (3.456 V, 0.88, a project floor efficiency: DS41979 plots VIN 12 V, not 5 V) | 3.0 A continuous; 4 A peak | maker's SUPPLY REQUIREMENT (v1.0 p.28 / v1.1 p.30) | 2.310 A; 3.080 A (largest averaged consumption 1.512 A gives 1.164 A) |
| NVMe + PCIe switch 3.3 V buck U204 | 0.9 / 1.8 A at 3.3 V | project ALLOWANCE (no drive document; the switch's own draw not separated) | 0.662 / 1.324 A |
| switch core 1.0 V buck U205 | 0.8 / 1.2 A | project ALLOWANCE | 0.185 / 0.277 A |
| fan J_FAN2 | 0.1 A | TBD (contract line 1057: "the fan's draw, with the part") | 0.1 A |
| EN gate U216 | 1 mA | maker's maximum (SCLS739F) | 0.001 A |

Sums: typical (CM5 0.9, card 3.0 A) 4.157 A, board B's 4.2 A reproduced; coincident (CM5 at the 1.6 A allowance,
card at 4 A) 5.628 A, the contract's 5.63 A reproduced; every branch at its peak or allowance 6.382 A, a bound.
Board A's limit on this rail: LM5176 U5, VSNS / R35 = 43 / 50 / 57 mV / 6 mOhm = **7.167 / 8.333 / 9.500 A**; the
header 10 A (AWG 16, standard header); the wire 16 AWG. Margins to the MINIMUM limit: 1.54 A at the coincident
figure, 0.79 A at the all-peak bound; 3.6 A to the header at the bound.
Drop in the lead pair (300 mm of 16 AWG at 1.25 mm2: 4.13 mOhm): 17 mV (0.34 percent) at 4.2 A, 23 mV (0.46 percent)
at 5.63 A. The four VH contacts at the catalogue's initial maximum of 10 mOhm each: 168 mV (3.3 percent) at 4.2 A,
225 mV (4.4 percent) at 5.63 A; at the after-test 20 mOhm twice that. A bound, not a measurement, and the contract's
2 percent budget carries NO share for the lead and its contacts (A 0.5 point plus B 1.5 points is the whole 2).

Verdict by the predicate: no sourced demand exceeds a sourced limit (the largest sourced demand, the card at its
maker's 4 A peak, is 3.08 A at 5.1 V; the whole coincident sum 5.63 A and the all-peak bound 6.38 A are both under the
maker's minimum loop limit 7.17 A and the header's 10 A). PASS cannot be earned: the CM5 publishes no maximum, the
NVMe drive and the fan have no document, the buck efficiency at 5.1 V in is not plotted, and the 4 A peak is stated
only in the series document v1.1, not in the -GL v1.0 that SOURCES names for the part. **INCONCLUSIVE, with the
declaration change supported:** board A's 2.5 / 5.0 A is the AP64500-era text (the "5 A peak at the module" note
belongs to the 5 A part slot 2 no longer has) and understates B's own sourced derivation by 1.66 A typical and 0.63 A
at the coincident peak. I would set A's +5V_S2 to typ 4.2, peak 5.63 (coincident, the record's own definition) with
the lead load J_5V_S2 5.63, and B's peak from 5.0 to 5.63 as well (B's declared peak sits BELOW the coincident
figure its own comment derives, gen_sch_b.py:78-79), recording the all-peak bound 6.38 A in the note. The stage's
input load on VBAT (`Q28: 2.0` in gen_sch_a.py) follows: 5.63 A x 5.1 V / 0.90 / 14.4 V = 2.22 A.

### +5V_DEV (the second disagreement)

Board B's end declares 3.8 A typical, 6.0 A peak arriving; its 19 apportioned loads sum to 5.18 A (branch peaks and
protection limits mixed with typicals, by the generator's own rule "the sum is held under the rail's declared peak").
Kinds: LimeSDR U23 1.2 A (project; the maker's 4.5 W is a web reading, `sdr-limesdr-mini-v2` is listed missing in
SOURCES.yaml line 149); +3V3_DEV buck U25 0.9 A (from a 1.2 / 2.0 A declaration, the 2.0 the AP63203's rating); LoRa
U21 0.6 A (Ebyte 650 mA transmit, held manual); panel F1 0.6 A (board C's declaration; ARCHITECTURE.md:449 names a
1.0 A peak); RockBLOCK U24 0.45 A (the 2.0 A burst peak is a project figure; the held RB9704 sheet gives 1.4 W);
QMX VBUS F3 0.3; camera U28 0.25 (0.5 USB limit); HDMI F2 0.2 (0.5 fuse); KSZ core U26 0.15 (PWR-F03: the maker's
1.21 A at 1.2 V is 0.34 A here, the declaration is BELOW it); three hub cores 0.1 each; three LDOs 0.05; four
bridges 0.02.
Board A's end: 4.0 A typical = J_5V_DEV 3.2 + U23 (D8 eFuse, ILM 2.0 A) 0.5 + U32 (wall port eFuse, ILM 0.89 A) 0.3;
peak 6.9 A = B's 6.0 + the wall port's 0.9, the D8 mezzanine at zero. Board D declares +5V_D8 at 1.0 A typical, 2.0 A
peak (its loads sum 0.96 A, the exciter keyed through U21 0.52 A; in PS-ALLTX the APRS exciter is keyed).
Board A's limit: LM5176 U7, VSNS / R43 6 mOhm = **7.167 / 8.333 / 9.500 A**; header 10 A; wire 16 AWG.
Sums at the converter: the ends' typicals B 3.8 + D 1.0 + wall 0.3 = 5.10 A (A declares 4.0); the ends' peaks
B 6.0 + D 2.0 + wall 0.89 = 8.89 A, 1.72 A OVER the minimum limit (a bound: the 2.0 and 0.89 are protection limits,
the 6.0 a project peak); POWER-THERMAL.md's PS-ALLTX 5.89 A PLAN under, 7.8 A HIGH over the minimum by 0.63 A (the
page says so at lines 709 and 1037). What the loop does above its target is a fold-back of the output voltage
(SNVSAI1D 7.3.6), a brown-out of the device rail that feeds the panel controller's PANEL_5V, not a trip.
Lead: 300 mm of 16 AWG, 4.13 mOhm: 16 mV (0.31 percent of 5.0 V) at 3.8 A, 25 mV at 6.0 A; the four contacts at the
10 mOhm maximum 152 mV (3.0 percent) at 3.8 A.

Verdict by the predicate: no sourced maker demand exceeds a sourced limit at the lead (the disagreement is 0.6 A of
project typicals, 3.2 against 3.8). At the converter the sum of the ends' declared peaks and the record's own HIGH
case exceed the minimum loop limit; both are bounds, so this is the model's answer, not a circuit defect, but it is
also not a PASS. **INCONCLUSIVE, with the lead figure change supported and a converter-side inconsistency exposed:**
A's J_5V_DEV 3.2 A cannot stand beside B's 3.8 A typical arriving on the same conductor. I would set A's J_5V_DEV to
3.8 A and A's typical to 3.8 + 1.0 (D's declared typical, not 0.5) + 0.3 = 5.1 A, and either raise A's peak to the
coincident 6.0 + 1.0 + 0.89 = 7.89 A with the fold-back recorded as the limiter, or keep 6.9 A only with a written
reason why D8 and the wall port cannot coincide with B's peak (there is none in the record: neither is dropped by
the D-11 interlock). That is an engineering decision (session authority), not a document.

### +5V_S1 and +5V_S3 (no disagreement; noted for completeness)

Both ends 2.5 / 5.0 A. Behind B: CM5 0.9 A typical (1.6 A allowance); WiFi card AW7915-AED at AsiaRF's 9.1 W maximum
(PWR-F01, VERIFIED there; the AsiaRF sheets are held under `v2/vendor/wifi/`, not re-read in this check) is 2.03 A at
5.1 V; NVMe + switch 0.66 / 1.32 A; core 0.19 / 0.28 A; fan 0.1 A. PS-ALLTX PLAN 4.65 A (POWER-THERMAL PWR-F02,
7 percent margin) against the AP64500's 5 A continuous RATING; the all-peak bound 5.33 A is over that rating and
under the 6.8 A minimum peak limit. B's declared load sum 4.75 A against 2.5 A typical on both ends: the typical is
low on both ends, consistently. INCONCLUSIVE (the CM5 maximum, the drive, the fan); no I-03 change needed; the
thermal side of a 5 A SO-8EP part at 45 C/W is PWR-F02's, outside this finding.

### +54V_POE (no disagreement)

Both ends 0.3 / 0.6 A; B's loads R13 0.593 (the port) + U5 0.007 (the TPS23861's own VPWR, "SLUSBX9I 6.5"; that
document is listed MISSING in SOURCES.yaml line 149, so the 0.6 A demand is not sourced in the tree). Limit: LM5176
U16 boost, VSNS / R71 20 mOhm = 2.15 / 2.50 / 2.85 A, margin 1.55 A at 0.6 A. In the named mode the rail is OFF by
hardware, 0 A. Lead 18 AWG: the catalogue's 10 A is for AWG 16 on the standard header and its 7 A for AWG 18 on the
shrouded header; for AWG 18 on the B2P-VH standard header the catalogue states no figure (a gap of the document, not a
risk at 0.6 A). INCONCLUSIVE on the strict predicate (the demand's document is not held); no declaration change.

## 4. Summary of my verdicts and the changes the sources support

| rail | verdict | change supported by held sources |
|---|---|---|
| +5V_S1, +5V_S3 | INCONCLUSIVE | none for I-03 (typicals low on both ends, consistently) |
| +5V_S2 | INCONCLUSIVE | A: typ 2.5 to 4.2, peak 5.0 to 5.63, J_5V_S2 5.0 to 5.63; B: peak 5.0 to 5.63; note the 6.38 A all-peak bound; VBAT load Q28 2.0 to 2.22 |
| +5V_DEV | INCONCLUSIVE | A: J_5V_DEV 3.2 to 3.8, typ 4.0 to 5.1; A's peak needs a session decision (7.89 A coincident against the 7.17 A minimum loop limit, or a reason D8 and the wall port cannot coincide) |
| +54V_POE | INCONCLUSIVE | none (fetch TI SLUSBX9I to source the 0.6 A; note the catalogue's AWG 18 gap) |

Not one rail is decided by the held documents in either direction. What decides them: a CM5 maximum (none published;
a bench reading of a loaded module at the prototype, TEST-PLAN power tests), the NVMe drive's figure (a drive is not
picked), the fan's figure (part not picked), a bench reading of the 5G card buck's efficiency at 5.1 V in (FW-A15 in
POWER-THERMAL), and for +5V_DEV the coincidence decision above.
