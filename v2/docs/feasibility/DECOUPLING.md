# Decoupling placement: which rule governs, part by part (decision 42)

MESHSAT-1357, 26 September 2026, written 14:45 CEST, corrected 15:25 CEST on the three points a checker found, and
corrected again 16:42 CEST on two more, both in the far-side seat, and at 17:15 CEST on the set of parts that get
an escape fan (section 12). The MeshSat field kit V2 is a prototype design: no board of the set has been built, and nothing here
releases a board to layout or to fabrication. This page answers the review of 26 September, section 4, last
paragraph (`v2/docs/reviews/2026-09-26-foundation-progress-review.md:81`): *"Determine whether the 3 mm rule is
authoritative for the specific part or a project heuristic before treating it as universal."* It rules decision 42
(`v2/ecad/tools/pcb_decisions.yaml`, entry `n: 42`), **taken by the session under the owner's standing rule of 26
September 2026** (`v2/docs/EXECUTION-PLAN.md:86`: the owner is not asked again and the session takes the option the
evidence recommends).

Labels. **VERIFIED**: read in the artefact named. **INFERRED**: derived (a count, a closed-form estimate, a reading
of a figure). **TBD**: not known, with its effect stated instead of a convenient value.

Inputs, pinned. Tools and generators at `1f614233`. Committed boards (the ones the 21 September verdicts judged,
hashes matched): A32 `v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb` (sha256 `58e26c67987b1daa...`), B21
`pcb-b-compute-b19` (`2e64b5bf2d9cd3bc...`), P4 `pcb-p-pack-p2` (`d79865e7b1aceb95...`), and for the set-wide reading
C24 `pcb-c-display-c8` (`2a273803757c68fb...`), D12 `pcb-d-aprs-d9` (`929bf82d2bf6eed4...`), E17 `pcb-e1-dock-e7`
(`a462ac2620b9b8d3...`). The round 6 candidates of boards A and B (worktrees `fnd/r4a` and `fnd/r4b` at `82dd1e4d`
plus their uncommitted generator edits, read 26 September) are cited where they differ from main.

## 1. The answer

1. **The 3 mm number is a project heuristic for every part it is applied to. No maker document gives it.** Fifteen
   documents were read for the parts decision 42 holds (section 4 and section 11), and none gives a distance for
   any capacitor. Across the whole vendor tree (311 PDFs under `v2/vendor/`, scanned by `drafts/dec_mmscan.py` for a
   millimetre or mil figure beside a capacitor clause and a placement word; six hits, each read in context: four are
   track widths or bus-length matching in Quectel and ST documents) there is exactly **one** maker distance for a decoupling capacitor: TI's TPA6132A2 on board D, "Place both capacitors
   within 5 mm of their associated pins" (SLOS597B section 9, p.17). It is looser than 3 mm and it is that part's own
   authority (D6). The registry already records the 3 mm as a heuristic: DEC-001 carries `source_status:
   SOURCE_UNVERIFIED`, `sources: []` and "The project's present 3 mm number is a heuristic and is recorded as one"
   (`v2/ecad/tools/pcb_rules.yaml:599-607`), and the coverage map files it as `HEURISTIC_AS_LAW`
   (`pcb_rules_coverage.yaml:208-212`). The scan reads text only: a figure drawn as an image is not caught by it.
2. **The 2.2 mm escape fan is a project number too, and on every part the tools fan, the two rules never overlap.**
   Measured on the committed text of six boards: the nearest seat whose capacitor courtyard clears the fan is 3.26
   to 5.73 mm (pin to capacitor centre) from the pin it serves, on every one of 98 fanned declarations
   (VERIFIED for the 55 on boards A, B and P; section 3). With the fan set as this ruling defines it (T1: every part
   the escape pass escapes, and every part with eight or more numbered copper pads 1.0 mm apart or less), 83
   declarations are fanned and the range is 3.26 to 5.49 mm (VERIFIED for the 38 on A, B and P). The decision's own
   evidence of 20 September called the window "2.98 to 3.00 mm"; there is no window at all.
3. **The ruling is per class, each clause with its source (section 6).** A converter's own power-stage capacitors
   sit on the IC's side and the fan does not apply to them (class R). A capacitor a maker ties to a supply pin, of
   any value, takes its own-pin window inside the fan (class D). A regulator's output or VCAP capacitor is seated the
   same way and also carries the maker's value and ESR bound (class L). An analog supply pin behind a series resistor
   is judged by topology (class A, provisional for the battery protection parts until their qualified review). Only
   a capacitor the maker itself calls rail bulk goes without a pin distance
   (class B1); microfarad parts no maker places keep the gate's existing 6.0 mm (class B2). The side opposite the
   part is a seat only on the three boards already assembled with SMD parts on both sides, B21, C24 and D12, and
   only under board B's own underside rule, kept as written: never inside the fan box of a part the escape pass
   escapes or the placers fan (T1), on either side, and never over a through-hole part. It is also never used for a
   part whose maker names the same side (the converters, and the STM32H743 in its LQFP, AN4938 9.3 and Figure 21).
   What that leaves is a seat under the pin of a small part the escape pass does not escape (a SOT-23-5, an SOIC-8, a
   sensor), and a fallback seat where the own side is full (D5). It does not
   answer decision 42's conflict at any fine-pitch part: the own-pin window does (D2, D3). It is not used on A32,
   E17 or P4, where it would add an assembly side.
4. **Decision 42's residue is resolved as a rule question** (section 7). Board A's three are a paste-aperture
   artefact and a mis-declaration, not a physics conflict. Board P's three are class A. Board B's 22 fanned
   declarations are converter input capacitors and one PoE controller pin.
5. **Two current PASS readings of DEC-001 are not evidence.** Board B's "PASS of 30" and board P's "PASS of 3"
   are 33 blanket allowances from one reason line written on 8 September; every one of those capacitors is past the
   gate's own limit on the committed board (VERIFIED, section 3.2(f)). They are classed as evidence awaiting
   revalidation under review section 1.
6. **Reading the makers found circuit gaps as well as placement rules** (section 8.3): among them the TPA6132A2 on
   board D is fitted with 1 uF at VDD and HPVDD where its maker asks 2.2 uF, and on D12 those two capacitors sit
   18.1 and 13.6 mm from their pins against the maker's 5 mm; two converter input capacitors (boards B and E) are
   declared against the EN pin; and the STM32H743's VDDA has no capacitor of its own (W6-F7).
7. **Nothing is laid for this ruling yet.** It needs tool changes (section 8.1) and generator changes (section 8.3)
   that other writers own, and a placement re-read after them.

## 2. Where the two numbers come from

| number | where it is applied | what it measures | origin | external source |
|---|---|---|---|---|
| 3.0 mm | `bypass_place.py:17` (`LIMIT`), used at `:97` and `:103` | pin to capacitor CENTRE, every value | 8 September, Stage C: "against the 3 mm the gate asks for" (`bypass_place.py:6`) | none |
| 3.0 mm | `bypass_slots.py:22`, used at `:84` and `:102` | pin to capacitor CENTRE, every value | owner ruling 9 September, appendix 32.74 option 3 (`bypass_slots.py:4`), which ruled that slots be reserved, not the distance | none |
| 3.0 / 6.0 mm | `intent_checks.py:11-13`, `:253`, `:255` | capacitor RAIL PAD to pin; 6.0 when the value string contains `u ` `uf` `u,` or `µ` | Stage C, 8 September | none |
| 2.2 mm | `bypass_slots.py:32-36` (`_fan_box`), `:38-49` (`_needs_fan`), `:51`, `:56-62`; `bypass_place.py:70-77` | courtyard bounding box grown by 2.2 mm, closed to capacitors, for any part with at least eight SMD pads whose closest two are 1.0 mm apart or less | 9 September: capacitors 1.9 to 2.6 mm from a 0.8 mm TQFP cost six of seventeen escapes on D10 and 23 of 57 on C9 (`bypass_slots.py:39-41`, `:56-58`) | none |

The escape pass itself selects a different set. `escape.py` escapes every part whose footprint name holds SOT-23-6
or SOT-23-8, or whose closest two SMD pads are 0.7 mm apart or less, with no pad-count floor (`is_fine`, `escape.py:34-42`),
less a J part over 0.6 mm pitch and the board's `ESCAPE_SKIP` (`:176-177`; board B skips U3, U4 and J_HDMI,
`tools/boards/b.json:13`). So today a six-pin part the escape pass escapes (a SOT-23-6, an MLPD-6) gets no fan, and
T1 makes the fan follow the escape pass (section 8.1).

`return_via.py:36` carries a separate `FAN_MM = 2.2` for its own purpose (which vias are exempt from the return-via
rule); this ruling does not touch it. `reserved.json` protects the packer's region definitions (`reserved.json:76`)
and no line of the three tools above.

## 3. The conflict, measured

### 3.1 Geometry, read from the board text

Method (session record `drafts/dec_geometry.py`, a text reader of `.kicad_pcb` with no pcbnew, mirroring
`bypass_slots._courtyard`, `_fan_box` and `_needs_fan`, and for the fan as ruled also `escape.py`'s selection,
`escaped` and `fan_as_ruled` in the same file): for every declared entry of a board's committed intent
file, the smallest distance from the pin to a capacitor centre at which the capacitor's courtyard, placed at
rotation 0 as `bypass_slots.py:86` places it, clears the part's fan box. The reading is a lower bound set by
geometry alone, before any other part, region or track is considered.

| board | declared entries on the board | on a part fanned today | nearest legal centre outside today's fan | of which fanned today only by paste apertures | on a part fanned as ruled (T1) | nearest legal centre outside the ruled fan |
|---|---:|---:|---|---|---|---|
| A32 | 30 of 40 (10 not on A32, section 3.2(f)) | 30 | 3.50 to 5.73 mm | 8 | 22 | 3.50 to 5.49 mm |
| B21 | 30 of 30 | 22 | 3.81 to 5.73 mm | 12 | 13 (the 12 go; C4 to C6 at the TSOT-23-6 U25 come in) | 3.81 to 4.81 mm |
| P4 | 3 of 4 (C14 added 26 September) | 3 | 3.62 to 4.56 mm | 0 | 3 | 3.62 to 4.56 mm |
| C24 | 18 of 19 | 14 | 3.43 to 4.43 mm | 0 | 14 | 3.43 to 4.43 mm |
| D12 | 24 of 26 | 15 | 3.26 to 4.91 mm | 2: C61 and C62 at the WSON-6-1EP U15, which the escape pass escapes, so they stay | 15 | 3.26 to 4.91 mm |
| E17 | 18 of 21 | 14 | 3.43 to 4.37 mm | 0 | 16 (C30 and C31 at the TSOT-23-6 U12 come in) | 3.43 to 5.41 mm |

VERIFIED for A, B and P, whose intent files match the verdicts' denominators. INFERRED for C, D and E: their intent
files were regenerated in round 4 after the 21 September verdicts, so one to three entries differ.

The per-capacitor rows for the three boards the decision holds (fan: the tool's test today, and the set T1 rules,
which is numbered copper pads or escaped by `escape.py`; d: nearest legal centre outside the fan and outside the courtyard alone; gate: the limit
`intent_checks.py:255` applies to that value string; now: rail pad to pin on the committed board, the gate's own
measure):

| capacitors | value | part.pin | package | fan today | fan as ruled | d fan | d courtyard | gate | now |
|---|---|---|---|---|---|---:|---:|---:|---|
| **A32** | | | | | | | | | |
| C8, C60, C71, C78, C89 | 4.7u | U2/U13/U15/U16/U19.23 (LM5176 VCC) | HTSSOP-28 | yes | yes | 4.89 | 2.69 | 3 | 20.0 to 26.6 |
| C11, C63, C74, C81, C92 | 10u 50V X7R 1210 | the same .2 (VIN) | HTSSOP-28 | yes | yes | 5.33 | 3.12 | 6 | 18.5 to 24.4 |
| C12, C64, C108, C82, C116 | 10u 50V X7R 1210 | the same .3 (VISNS) | HTSSOP-28 | yes | yes | 5.49 | 3.29 | 6 | 18.0 to 30.2 |
| C29/C30, C35/C36, C41/C42, C47/C48 | 10u 25V 1210 | U4, U5, U6, U7.2 (AP64500 VIN) | SOIC-8-1EP | yes | **no** | 5.72 | 3.52 | 6 | 13.4 to 13.7 |
| C4 | 1u | U1.1 (LTC2954) | TSOT-23-8 | yes | yes | 3.65 | 1.46 | 3 | 108.6 |
| C19 | 1u | U3.7 (BQ25731 VDDA) | QFN-32 | yes | yes | 4.33 | 2.13 | 3 | 18.8 |
| C54 | 10u 25V 1210 | U12.3 (TPS62933 VIN) | SOT-583-8 | yes | yes | 4.85 | 2.65 | 6 | 43.2 |
| C94 | 220n | U18.5 (TPS25740 DVDD) | QFN-24 | yes | yes | 4.33 | 2.13 | 3 | 15.9 |
| C104, C106, C107 | 100n | U26.14, U27.24, U28.24 | TSSOP-14/24 | yes | yes | 3.50 to 3.73 | 1.30 to 1.53 | 3 | 113.8 to 138.8 |
| **B21** | | | | | | | | | |
| C112/C113, C119/C120 and the same in slots 2 and 3 (12) | 22u 10V X7R 1210 | U103, U104, U203, U204, U303, U304.2 (AP64500 VIN) | SOIC-8-1EP | yes | **no** | 5.72 | 3.52 | 6 | 9.0 to 32.2 |
| C125, C130, C225, C230, C325, C330, C7 | 10u | U105, U106, U205, U206, U305, U306, U26.3 (TPS62933 VIN) | SOT-583-8 | yes | yes | 4.23 | 2.03 | 3 | 9.4 to 20.9 |
| C36, C37, C38 | 100n | U5.1 (TPS23861 VDD) | TSSOP-28 | yes | yes | 3.81 | 1.60 | 3 | 177.0 to 251.5 |
| C4; C5, C6 | 10u; 22u 6.3V | U25.2 (AP63203 EN), U25.1 (AP63203 FB) | TSOT-23-6 | no | **yes** (escaped: its name holds SOT-23-6) | 4.81; 3.93 | 2.61; 1.73 | 3; 6 | 17.6 to 21.9 |
| C12, C13 | 1u | U27.5, U27.1 (AP2112K) | SOT-23-5 | no | no | | 1.48 | 3 | 12.3 to 13.8 |
| C69; C70, C71 | 100n | U8.8 (ATECC608B); U9.2 (DS3231M) | SOIC-8 | no | no | | 1.52; 2.71 | 3 | 13.2 to 27.7 |
| **P4** | | | | | | | | | |
| C1 | 2.2u | U1.1 (BQ4050 PBI) | QFN-32 | yes | yes | 4.56 | 2.36 | 3 | 10.1 |
| C6, C8 | 100n | U1.32 (BAT), U1.26 (VCC) | QFN-32 | yes | yes | 3.62 | 1.42 | 3 | 11.0, 14.4 |

### 3.2 Seven tool facts that make the conflict larger than the physics (all VERIFIED)

(a) **A paste aperture makes a 1.27 mm part "fine pitch".** KiCad's `SOIC-8-1EP` land carries four unnumbered
paste-only SMD pads 0.942 mm from the exposed pad; `_needs_fan` counts them (`bypass_slots.py:42`) and gives the
AP64500 a fan it does not need. Counting only numbered pads with copper, the closest pitch is 1.27 mm and the fan
goes. This is W2's F-DC-02, confirmed by its challenger from the board text and again here (8 entries on A, 12 on
B). It is the same defect class as a paste aperture read as copper elsewhere in the tools.
- **Two more entries on D, C61 and C62, are fanned today only through paste apertures too, and that fan is not an
  artefact.** The WSON-6-1EP's two paste apertures lift U15 to nine SMD pads, past `_needs_fan`'s floor of eight; on
  copper it has seven. But the escape pass escapes U15 at 0.65 mm (`escape.py:34-42` has no pad-count floor), and
  D12 carries vias of its pins' nets 1.50 mm from pin 3 (/VGG_CT) and 1.58 mm from pin 6 (/+5V_D8)
  (`drafts/dec_escset.out`).
- **So a copper-pad count alone would cut a fan an escaped part needs,** and T1 does not use it alone (section 8.1).

(b) **The placers ask 3.0 mm of every value; the gate asks 6.0 mm of microfarad values.** `bypass_place.py:17` and
`bypass_slots.py:22` have one `LIMIT` for all; `intent_checks.py:255` sets 6.0 for bulk. So the placers refuse a
10 uF input capacitor at a seat the gate would pass.

(c) **The gate's value test misses a bare "u".** `intent_checks.py:255` looks for `u `, `uf`, `u,` or `µ`, so "10u",
"4.7u", "2.2u" and "1u" read as small capacitors at 3.0 mm while "10u 25V 1210" reads 6.0 mm (the table's gate column:
C8, C4, C19 on A, C4, C7, C125 on B, C1 on P). The value is the wrong key in any case: the class is (section 6).

(d) **Two tools, two definitions of distance.** The placers measure to the capacitor CENTRE (`bypass_place.py:97`,
`bypass_slots.py:84`); the gate measures to its RAIL PAD (`intent_checks.py:252-253`). For a 1210 the two differ by
about 1.5 mm.

(e) **The placers try one orientation.** `bypass_slots.py:86` places at rotation 0.0 and only walks the position, so a
capacitor cannot turn its rail pad toward the pin.

(f) **One allow line passes every far capacitor on the board.** `intent_checks.py:244-258` reads
`bypass-allow.txt` and, when the file holds any line, passes every entry past its limit, quoting the file's first
line whatever the capacitor. Boards A, B, C, D and P carry the same line (commit `643b38eb`, 8 September; md5
`cbb5df10...`): "... moving them is a floor-plan change across the whole board set ... and is an owner decision";
board E carries its own blanket line. Measured on the committed boards with the gate's own measure: **all 30 of
A32's declarations on the board, all 30 of B21's and all 3 of P4's are past the gate's limit** (nearest: 13.4, 9.0
and 10.1 mm). So `pcb-b-compute-b19/routed/intent_decoupling.verdict.json` ("PASS", 30 pass, 0 fail, 21 September)
and `pcb-p-pack-p2/routed/...` ("PASS", 3 of 3) are 33 allowances counted as passes. Board A's "FAIL 10 of 40" is
ten `pads found on the board` failures: the LM5176 current-sense filter capacitors that A32 predates
(`boards/a.json:607`), which is history about A32, not a measurement of the candidate.

(g) **The fan and the escape pass select different parts.** `_needs_fan` asks eight SMD pads 1.0 mm apart or less;
`escape.py` escapes any part at 0.7 mm or less, or with SOT-23-6/8 in its name, with no pad floor (section 2). Read
on the six committed boards (`drafts/dec_escset.py`, output `drafts/dec_escset.out`), the parts the escape pass
escapes with fewer than eight numbered copper pads are:
- **A32:** 1 (U29, SOT-23-6).
- **B21:** 14. U82 and U83 (MLPD-6 at 0.35 mm, on the back); U10, U21 and U22 (WSON-6-1EP at 0.65 mm); nine
  SOT-23-6 or TSOT-23-6 (U25, U29, U33, U34, U35, U37, U107, U207, U307).
- **C24:** 5 (SOT-23-6, all on the back).
- **D12:** 2 (U15, WSON-6-1EP; U5, SOT-23-6).
- **E17:** 9 (six TDSON-8-1 FETs, Q1 to Q6; three SOT-23-6 or TSOT-23-6).
- **P4:** 1 (D2, SOT-23-6).

The four WSON-6-1EP and E17's six FETs are fanned today only through their paste apertures. The other 22 have no
fan at all, though the escape pass selects them, and 18 of them carry a via of a signal pad's own net within 3.5 mm
(A32's U29, B21's U29 and U37 and D12's U5 carry none on their signal nets). Every nearest locked via of a signal pad's own net within
3.5 mm of an escaped part's pad lies inside that part's fan box: 1,087 of 1,087 on the six boards
(`drafts/dec_escvias.out`; that these are the escape vias is INFERRED from the net, the lock and the distance).
`escape.py`'s own `is_fine` also counts paste apertures, as (a) describes for `_needs_fan`: E17's TDSON-8-1 FETs,
whose pins are at 1.27 mm, read 0.40 mm and are escaped. Whether they should be is a question for `escape.py`, not
for this ruling. T1 makes the fan follow whatever the escape pass selects.

### 3.3 Which boards are already assembled on both sides (checker item 1, VERIFIED)

Read from the committed board text by `drafts/dec_sides.py` (a footprint is SMD when it carries a copper SMD pad
and no plated hole, THT when it carries a plated hole):

| board | front: SMD / THT | back: SMD / THT | SMD on both sides already |
|---|---|---|---|
| A32 | 343 / 28 | 0 / 21 | **no**. The back carries only through-hole parts: 11 SMP-MAX receptacles R222M00720 (J_BM1 to J_BM11), nine spring pins of the Mill-Max 0858 class (J_CN1 to J_CN4, J_CP1 to J_CP4, J_PRE1) and the 2x6 pogo block J_DOCK |
| B21 | 431 / 31 | 464 / 5 | **yes** |
| C24 | 31 / 24 | 135 / 0 | **yes**. The RP2040 (U3), its flash and its regulator sit on the back, with their capacitors |
| D12 | 128 / 8 | 71 / 0 | **yes**. Decision 37 moved both crystals and their load capacitors to the back "which board D already assembles"; decision 44 records nine back-side parts inside the codec's pin field |
| E17 | 148 / 13 | 0 / 0 | **no** |
| P4 | 48 / 8 | 0 / 0 | **no** |

Declared decoupling entries whose capacitor sits on the side OPPOSITE the part it serves (`drafts/dec_sides_decl.py`
against each board's committed intent file): A32 0, B21 0, C24 0 (its 15 back-side declarations all serve parts on
the back), E17 0, P4 0, and **D12 11**: C51 to C55, C8, C9 and C15 to C18, all on B.Cu serving F.Cu parts. None sits
inside its own part's courtyard. Read against the escape fans (`drafts/dec_farside.py`, output
`drafts/dec_farside.out`: the fan box of every part in the set T1 rules, which is every part the escape pass escapes
and every part with eight or more numbered copper pads 1.0 mm apart or less, and every through-hole courtyard):
- **C15 and C16 overlap the fan box of U7**, the TPA6132A2 in its QFN-16 at 0.5 mm, which is where U7's escape vias
  come through.
- **C17 overlaps the fan box of U5**, a SOT-23-6 the escape pass escapes. The 16:42 reading used the copper-pad set
  alone, which holds no SOT-23-6, and called C17 clear.
- The other eight are clear of every fan box and every through-hole courtyard.

Their treatment is in section 7.

Board B's underside rule has never been enforced by a packer (decision 44's evidence), and the committed boards
show it. Counted with the same reader:
- **B21:** 103 SMD footprints on the back overlap the fan box of a front part, and 5 on the front overlap the fan
  box of a back part.
- **D12:** 20 on the back do, among them decision 44's nine inside the codec's pin field.
- **C24:** none.

(The 16:42 reading, on the copper-pad set alone, counted 92 and 18: `drafts/dec_farside.before-17h15.out`.)

Appendix 32.174 counted 71 back-side parts under the three 0.40 mm PCIe switches alone on B19, by a narrower
measure (under the part rather than inside its fan).

## 4. What each part's maker requires

Every quotation below was read in the document named (VERIFIED). "Number" is a millimetre figure for placement. Page
numbers are the PDF's own pages.

| part (board, references) | package, pitch (board text) | maker document | what it says about placement | number | value and count it asks, against the design |
|---|---|---|---|---|---|
| STM32H743VI (B, U41/U51/U61) | LQFP-100, 0.5 mm | ST AN4938 Rev 7, Oct 2024 | "each power supply pair must be decoupled with filtering ceramic capacitors (100 nF) and one single tantalum or ceramic capacitor (min. 4.7 μF) connected in parallel. These capacitors need to be placed as close as possible to, or below, the appropriate pins on the underside of the PCB" (7.4, p.32, a general recommendation); for these devices 9.3 states the package rule: "The following recommendations shall be followed: Place the decoupling capacitors as close as possible to the power and ground pins of the MCU. For BGA packages, it is recommended to place the decoupling capacitors on the other side of the PCB (see Figure 21)" (p.38), and Figure 21 (p.39) is captioned "Decoupling capacitor and STM32 MCU on the same side of the package (all packages except BGA)" against "on the opposite sides of the package (BGA package)". **For the LQFP-100 on board B the maker names the same side**; "Connect the decoupling capacitor pad to the power and ground plane with a wider, short trace/via" (p.38) | none | 100 nF per VDD pin and one 4.7 uF minimum for the package; VDDA 100 nF + 1 uF; VCAP1 and VCAP2 2.2 uF each, ESR under 100 mOhm (2.2, p.12). VBAT: "it is mandatory to connect this pin to an external power supply: as an example, VBAT pin can be connected to VDD through a 100 nF external ceramic decoupling capacitor" (p.12): the connection is required, the 100 nF is an example. Design: 5 x 100 nF for 5 VDD pins, 10 uF, 2 x 2.2 uF VCAP, VBAT tied to the 3.3 V rail: met. **VDDA is tied to the 3.3 V rail with no capacitor of its own** (`gen_sch_b.py:806`, `:811`; `fnd/r4b` `:1119`, `:1124`). That is W6-F7 as it stands (`wt/w6/drafts/w6-findings.md:34`, `:243-244`, which withdrew the VBAT 100 nF as a shortfall) |
| PI7C9X2G404SL (B, U101/U201/U301) | LQFP-128-EP, 0.4 mm | Diodes DS40068 Rev 5-2 | nothing: section 3.5 lists the supply pins (p.14) and no clause, figure or table covers decoupling | none | **TBD**: no maker requirement in the tree. Design: 6 x 100 nF at 3.3 V and 6 x 100 nF at 1.0 V, 10 uF each (`gen_sch_b.py:450-451`), for 26 supply pads |
| TUSB8041 (B, U102/U202/U302) | QFN-64, 0.5 mm | TI SLLSEE4E, Jun 2016 | "These bulk capacitors can be placed anywhere on the power rail. The smaller decoupling capacitors should be placed as close to the TUSB8041 power pins as possible with an optimal grouping of two of differing values per pin" (10.1, p.37); "A 0.1 uF capacitor should be placed as close as possible on each VDD and VDD33 power pin" and bulk "as close as possible to the voltage regulators" (11.1.1, p.38) | none | one 0.1 uF per pin: 8 VDD, 4 VDD33. Design: **4 on the 1.1 V core for 8 VDD pins** (`gen_sch_b.py:534`), 4 on 3.3 V, 10 uF on 1.1 V |
| KSZ9897R (B, U1) | TQFP-128-EP, 0.4 mm | Microchip DS00002330D | 4.7: "An example power connection diagram can be seen in Figure 4-8"; the figure (p.51, read as an image) draws one 0.1 uF at each supply pin, 22 uF on DVDDL, AVDDL and AVDDH, 10 uF on VDDIO, AVDDL and AVDDH fed through ferrites | none | the example's 27 x 0.1 uF (DVDDL 8, AVDDL 9, AVDDH 7, VDDIO 3). Design: **10 x 100 nF** (4 at 3.3 V, 3 at 1.2 V for 17 pins, 3 at 2.5 V for 7) and 10 uF on 1.2 and 2.5 V (`gen_sch_b.py:619-620`) |
| TMUXHS4212 (B, U109/U209/U309) | VQFN-20, 0.5 mm | TI SLASEP7A, May 2022 | "TI also recommends to place ample decoupling capacitors at the device VCC near the pin" (10, p.18); Figure 11-1: "Place VCC decoupling capacitors as close to VCC pins as possible" | none | met: 100 nF + 1 uF per mux (`gen_sch_b.py:549`) |
| TS3DV642 (B, U3/U4) | WQFN-42, 0.5 mm | TI SCDS343F, Aug 2018 | "Decoupling capacitors should be used between power supply pin and ground pin" (layout, p.23) | none | 0.1 uF VCC (pp.18-21). Design: C37 and C38 exist in the switch block (`gen_sch_b.py:658`) but are **declared against U5 pin 1, the PoE controller** (`:990-991`) |
| CP2102N (B, U15 to U18) | QFN-28, 0.5 mm | Silicon Labs CP2102N data sheet Rev 1.5 | "4.7 uF and 0.1 uF bypass capacitors required for each power pin placed as close to the pins as possible" (p.5); the same figure draws VDD as the internal regulator's "3.3 V (out)" fed from VREGIN | none | VDD, the regulator's output (board B wires VREGIN from the slot's bus rail and VDD as "its own 3.3 V out", `gen_sch_b.py:352-354`), has 4.7 uF + 100 nF (`:356`); **VREGIN has none of its own** |
| TPS23861 (B, U5) | TSSOP-28, 0.65 mm | TI SLUSBX9I | "CVDD: 0.1 uF, 50 V, X7R ceramic at pin 1 (VDD)" (8.3.4.1, p.90) | none | met by C36 |
| AP64500 (A, U4/U6 in the candidate; B, six) | SO-8EP, 1.27 mm | Diodes DS41979 Rev 5-2, Dec 2024 | "Place the input capacitors as closely across VIN and GND as possible" (Layout, p.23); Figure 32 puts C1 against VIN | none | "a ceramic capacitor greater than 10 uF is sufficient for most applications" (13). Met |
| AP63203, AP63205 (B, U25; E, U12) | TSOT-26, 0.95 mm | Diodes DS41326 Rev 3-2, Nov 2024 | pin table: 1 FB "Feedback sensing terminal", 2 EN, 3 VIN "Bypass VIN to GND with a suitably large capacitor", 4 GND (p.2); "Place the VIN capacitors as close to the device as possible", "Place the feedback components as close to FB as possible" (Layout items 4 and 5, p.15) | none | input 10 uF met, but **declared against pin 2, EN**, on B (C4, `gen_sch_b.py:984`) and on E (C31, `gen_sch_e.py:622`); B's output capacitors C5 and C6 are **declared against pin 1, FB** (`gen_sch_b.py:985-986`) |
| TPS62933 (A, U12/U33; B, seven) | SOT-583, 0.5 mm | TI SLUSEA4D, Aug 2022 | "the most critical PCB feature is the loop formed by the input capacitors and power ground"; "Place the inductor, input and output capacitors, and the IC on the same layer"; "Place a 0.1-uF ceramic decoupling capacitor or capacitors as close as possible to VIN and GND pins, which is key to EMI reduction" (12.1, p.40) | none | **the 0.1 uF is absent on A's U12 (only C54, 10 uF, `gen_sch_a.py:440`) and on all seven of B's** (`gen_sch_b.py:350`); A's U33 has C160 (candidate `gen_sch_a.py:957`) |
| LM5176 (A, seven stages in the candidate) | HTSSOP-28, 0.65 mm | TI SNVSAI1D, Aug 2021 | CIN, QL1, QH1 and RSENSE "close together to minimize the loop area"; "Place the VCC bypass capacitor close to the controller IC, between the VCC and PGND pins"; BIAS 0.1 uF; "Bypass the VIN pin to AGND with a low ESR ceramic capacitor located close to the controller IC" (10.1, p.30). VCC is "Output of the VCC bias regulator" (pin table, p.3) and takes "a value between 1 µF and 4.7 µF" (p.15). Pin 3 is VISNS, "VIN sense input. Connect to power stage input rail" (p.3) | none | VCC 4.7 uF met; the candidate adds BIAS 0.1 uF on all seven and a 1 uF VIN-pin capacitor behind the blocking diode on FE, PA and HF (`fnd/r4a` `gen_sch_a.py:379`, `:453-456`); **S2, SD, POE and PD have no VIN-pin capacitor** (their 10 uF CIN is declared at pin 2, `:458`), and **every stage declares a 10 uF CIN against VISNS** (`:456`, `:458`) |
| BQ25731 (A, U3) | QFN-32, 0.4 mm | TI SLUSE66A, Jan 2021 | Table 12-1 (p.93): the input loop "best to put them on the same side ... Move part of CBUS to the other side of PCB for high density design"; "10 nF + 1 nF (0402 package) decoupling capacitors as close as possible to IC"; "Place VBUS cap, VCC cap, REGN caps near IC" | none | the candidate carries C190/C191 (10 nF + 1 nF, `fnd/r4a` `gen_sch_a.py:649`), undeclared |
| BQ4050 (P, U1) | QFN-32, 0.5 mm | TI SLUSC67B, Oct 2017 | "The bq4050 gauge has an internal LDO that is internally compensated and does not require an external decoupling capacitor"; PBI 2.2 uF (8.2.2.2.2, p.33); "Place all filter components as close as possible to the device" and keep high-current traces away from the gauge's signal traces (10.1, pp.42-43); protector FET and pack terminal bypass capacitors on wide copper (10.1.1, p.44) | none | PBI 2.2 uF met; BAT and VCC are RC filters (R5 100 ohm with C6, R7 1 kOhm with C8, `gen_sch_p.py:168-170`) |
| BQ77207 (P, U2) | the DSS land | TI SLUSEG7D, May 2026 (`drafts/datasheets/`) | RVD 100 to 1000 ohm, CVD 0.05 to 1 uF (Table 8-1, p.14); "Ensure the RC filters for the Vn and VDD pins are placed as close as possible to the target terminal" (8.4.1, p.17) | none | met: R23 300 ohm, C14 100 nF (`gen_sch_p.py:390`) |
| RP2040 (C, U3; E, U10) | QFN-56, 0.4 mm | Raspberry Pi RP2040 hardware design guide, build 20/08/2026 | "it is important to place decoupling close to the power pins. Ordinarily, we recommend the use of a 100 nF capacitor per power pin"; room for all of them "could be overcome if we used ... a four layer PCB with components on both the top and bottom sides" (2.1.2, pp.8-9); "We must place 1 μF capacitors close to both the input (VREG_IN) and the output (VREG_OUT), in order to provide a stable 1.1 V supply" (2.1.3, p.9) | none | ADC_AVDD and USB_VDD have none of their own (round 4 open item O-C1); the two 1 uF on the regulator's output net are **declared against the DVDD pins 23 and 50**, not VREG_VOUT pin 45 (`gen_sch_c.py:349`, `gen_sch_e.py:620`; pin map `gen_sch_c.py:54-55`) |
| TLV755P (C, U5; D, U1; E, U13) | SOT-23-5, 0.95 mm | TI SBVS320D, Sep 2024 | "requires an output capacitance of 0.47µF or larger for stability"; "Place a 1µF or greater capacitor on the input pin" (7.1.1, p.15); "Place input and output capacitors as close as possible to the device" (layout, p.21) | none | met: 1 uF in, 1 uF out on C and E; 1 uF in, 1 uF + 10 uF out on D (`gen_sch_d.py:593-595`) |
| AP2112K (B, U27 and the three supervisor LDOs) | SOT-23-5, 0.95 mm | Diodes DS39724 Rev 2-2 | "Stable with 1.0µF Flexible Cap" (features, p.1); no layout clause | none | met: 1 uF in, 1 uF out on U27 (`gen_sch_b.py:987-988`) |
| TUSB2046B (D, U4) | LQFP-32, 0.8 mm | TI SLLS413L, Jun 2017 | the TUSB8041's words: bulk "can be placed anywhere on the power rail", smaller ones "as close to the TUSB2046x power pins as possible" (p.17); "A 0.1-μF should be placed as close as possible on VCC power pin" and bulk "as close as possible to the voltage regulators" (p.18) | none | 2 x 100 nF and 10 uF declared at pin 3 (`gen_sch_d.py:596-598`) |
| PCM2912A (D, U6) | TQFP-32, 0.8 mm | TI SLES230A, Aug 2015 | "The decoupling capacitors must be as close as possible to the PCM2912A pins" (p.27); 1 μF ceramic capacitors in the application circuit (p.24) | none | 1 uF per supply pin (C18 to C23, `gen_sch_d.py:336`, declared at `:603-608`) |
| TPA6132A2 (D, U7) | QFN-16, 0.5 mm | TI SLOS597B, Jul 2017 | "Connect the HPVDD pin only to a 2.2 μF, X5R or better, capacitor ... Place both capacitors within 5 mm of their associated pins on the TPA6132A2. Ensure that the ground connection of each of the capacitors has a minimum length return path to the device" (9, p.17); "Place a 2.2 μF capacitor within 5 mm of the VDD pin ... Use 0402 or smaller size capacitors if possible"; an additional 10 uF "or higher" on VDD is optional and "unnecessary in most applications" (9.1, p.17); both 2.2 uF drawn in the application figures (pp.14, 16) | **5 mm** | **HPVDD has 1 uF (C31) where the maker asks 2.2 uF; VDD has 1 uF (C32) where the maker asks 2.2 uF**, plus the optional 10 uF (C33) (`gen_sch_d.py:379`). The generator cites "SLOS553" (`gen_sch_d.py:148`); the document in the tree is SLOS597B |
| general | | TI SCAA082A, rev. Aug 2017 | "Place the lowest valued capacitor as close as possible to the device"; "Connect the pad of the capacitor directly with a via to the ground plane. Use two or three vias" (2.4, p.13) | none | |
| general | | Altera AN 574, AN-574-1.0, May 2009 (`drafts/datasheets/`) | spreading inductance depends on the plane dielectric h and the distance d; "Minimizing the dielectric thickness (h) reduces the capacitor location sensitivity and allows you to place the capacitors farther away" (p.6); vias "as close as possible to the capacitor", "Place the capacitors on the PCB surface (top and bottom) closest to their corresponding power/ground planes" (p.13); a bottom 0402 through long vias 2.3 nH against a top 0402 "slightly far away" at 0.57 + 0.2 + 0.05 nH (p.16) | none | |

**Conclusion of the table.** For the parts decision 42 holds, not one maker gives a distance; across the vendor tree
one maker does (TPA6132A2, 5 mm, board D). The makers' words split the capacitors by role, not by value: the
converter makers fix the input capacitor to the IC's own side and the switching loop (TPS62933, BQ25731, LM5176,
AP64500, AP63200); a maker that ties a capacitor to a pin says so whatever its value (AN4938's 4.7 uF "placed as
close as possible to ... the appropriate pins", 7.4, on the MCU's side for a non-BGA package by 9.3; the CP2102N's 4.7 uF "required for each power pin placed as close to
the pins as possible"); a regulator's output capacitor carries a stability condition (TLV755P, AP2112, AN4938's VCAP,
LM5176 VCC, RP2040 VREG_VOUT, TPA6132A2 HPVDD); only TI's two USB hubs call bulk free to sit "anywhere on the power
rail"; TI says the BQ4050 needs no decoupling capacitor at all. On the side, three makers name the capacitor's
side and one names both:
- **Same side, AN4938:** section 7.4 speaks generally of "below ... on the underside", but section 9.3, whose
  recommendations "shall be followed", and its Figure 21 allow the other side for BGA packages only and put the
  capacitor on the MCU's side for every other package. The STM32H743VI on board B is an LQFP-100, so for it the
  maker names the same side.
- **Same side, the converters:** TPS62933 ("Place the inductor, input and output capacitors, and the IC on the same
  layer", 12.1, p.40) and BQ25731 (for the input loop, "best to put them on the same side", Table 12-1, p.93).
- **Both sides, the RP2040 guide:** it names "a four layer PCB with components on both the top and bottom sides" as
  the way to bring its decoupling closer (2.1.2, p.9). It is the one maker's text in the tree that supports the other
  side for a part of this set.

## 5. The electrical constraints

### 5.1 What decides the loop

A decoupling capacitor serves a pin up to the frequency where its mounted inductance, not its capacitance, sets its
impedance; above series resonance "the impedance is independent of the value of the capacitor" (AN 574, p.6). The
mounted loop is the capacitor's own ESL (common to every option, so it cancels in a comparison), the track from its
rail pad to the pin over the nearest plane, and the vias to the planes. How much distance costs depends on where the
rail is: on a plane pair with a thin dielectric distance matters little (AN 574, p.6), on a track it matters per
millimetre.

What the stackups give (session record `drafts/dec_loop.py`, output `drafts/dec_loop.out`; INFERRED, closed forms,
not a field solve):

| stackup (source) | boards | outer copper to first plane | track over that plane, w 0.20 / 0.25 / 0.30 / 0.50 mm |
|---|---|---|---|
| JLC06161H-3313 (`jlcpcb-impedance-stackups-2026-09-16.md:33-47`) | A, B; C from decision 27 | 0.0994 mm | 0.30 / 0.26 / 0.23 / 0.16 nH per mm |
| JLC08161H-2116 (`jlcpcb-stackups-2026-09-25.md`) | B's eight-layer measurement | 0.1164 mm | 0.32 / 0.29 / 0.26 / 0.18 nH per mm |
| JLC04161H-7628 (`stackup_write.py:15`; the stackup blocks of the C24 and D12 board files) | C24, D12 | 0.2104 mm | 0.43 / 0.39 / 0.36 / 0.27 nH per mm |
| JLC04162H-7628 (same file as the eight-layer row) | P | 0.2104 mm | 0.43 / 0.39 / 0.36 / 0.27 nH per mm |

Track: Hammerstad and Jensen's microstrip model, L' = Z01/c (independent of the dielectric constant). Via pair from
the far side to the first plane under the part (0.3 mm drill): L = (mu0 l / pi) acosh(s / 2r) gives 0.64, 0.95 and
1.20 nH at 0.5, 0.8 and 1.2 mm via pitch on the six-layer stack (l 1.45 mm), and 0.59, 0.88 and 1.11 nH on
JLC04161H-7628 (l 1.34 mm).

Which rails are planes (VERIFIED from the filled zones of the committed boards, `drafts/dec_planes.py` for C and D):
board A32 has GND on In1, In2 and In4 (and VBAT on part of In2); board B21 has GND on In1 and the 5 V rails on In4; C24 and D12 have GND on
In1 and In2 (and GND pours on both outer layers), with only a 92 mm2 island of +5V_D8 on D12's In2. **The supply
rails that feed the fine-pitch parts are not planes on any board.** So a per-pin capacitor's loop is set by its
track to the pin.

### 5.2 The seats for a per-pin capacitor at a 0.4 to 0.5 mm part (classes D and L)

| seat | rail pad to pin | loop beyond the capacitor's own ESL, 0.25 mm track: six-layer (B) | four-layer (C24, D12) |
|---|---|---|---|
| own-pin window inside the fan (0402, just outside the courtyard) | 1.0 to 1.7 mm (window centres read on B21 with `drafts/dec_fanwin.py`) | 0.26 to 0.44 nH | 0.39 to 0.66 nH |
| nearest seat outside the fan (the rule today) | 3.2 to 3.9 mm | 0.83 to 1.01 nH | 1.25 to 1.52 nH |
| a crowded part's seat outside the fan | about 5 mm | about 1.3 nH | about 1.95 nH |
| the side opposite the part, under the pin: 0.5 mm dog-bone and via pair at 0.8 mm | | about 1.08 nH | about 1.07 nH |

The last row is **not a seat at these parts** (D5). A 0.4 to 0.5 mm part is fanned, and the far side under its pin
lies inside its fan box, where its escape vias come through. Board B's own rule forbids it (section 6, D5). The row
is kept because the same figure prices the far side under the pin of a small part the escape pass does not escape.

The own-pin window forms a third to a half of the loop the seat outside the fan forms, on both stacks. The side
opposite the part costs about the same in nanohenries on both stacks, but what it is worth differs, because the
outer track costs more on the four-layer stack's thicker prepreg. At a part where it is allowed:
- on C24 and D12, a capacitor under the pin on the other side forms a smaller loop than any own-side seat whose rail
  pad is more than about 2.8 mm from the pin;
- on board B, only than an own-side seat more than about 4.2 mm away.

That is AN 574's own point (p.16): the far side pays in via length, and what it buys depends on the stackup. It
would win outright only for a rail carried on a plane next to the far side, which no board has.

**The via allowance.** One number per stackup states the far side's cost in the same unit as every other seat: the
length of 0.25 mm outer track whose inductance equals the via pair at 0.8 mm pitch. It is **3.7 mm on JLC06161H-3313
(B, and C once it goes to six layers under decision 27), 3.3 mm on JLC08161H-2116, and 2.3 mm on JLC04161H-7628 (C24,
D12)** (`drafts/dec_loop.out`, section 4; INFERRED). A seat on the far side then has a loop-equivalent distance equal
to its in-plane rail pad to pin distance plus the allowance, and every seat on either side is compared on that one
figure (D5).

**How far the allowance moves, and AN 574's own example** (`drafts/dec_loop.out`, section 5; INFERRED).
- **Via pitch** moves it most. On the six-layer stack it is 2.5, 3.7 and 4.6 mm at 0.5, 0.8 and 1.2 mm pitch, and on
  JLC04161H-7628 it is 1.5, 2.3 and 2.8 mm.
- **Track width** moves it less. Between 0.20 and 0.30 mm at 0.8 mm pitch it spans 3.2 to 4.1 mm (six layers) and
  2.0 to 2.5 mm (four layers).
- **Plane choice.** The allowance takes the full via height, from the far surface to the first plane under the part.
  A ground plane next to the far side (In2 on C24 and D12, In4 on A32) shortens the ground via only: the loop still
  closes through the rail via and the part's own ground vias, which span the board. A rail on a plane next to the far
  side would shorten it, and no board has one (5.1).
- **The tools' one number.** The tools use the 0.8 mm figure. A placed far-side seat is re-read with its own via
  pitch when it is measured (T9).

AN 574's worked case (pp.15-16) gives 2.3 nH for a bottom 0402 against 0.57 nH on the top, which looks far larger
than the 0.88 to 0.95 nH pair used here. The example does not transfer as a number, because its board is different:
- it is 115 mil thick, with the plane 12 mil from the top and **103 mil (2.62 mm) from the bottom**;
- its 2.3 nH is the whole mounting inductance, capacitor pads and trace included.

What does transfer is its rate: 1.73 nH more for 2.31 mm more via, 0.75 nH per mm. At that rate, the extra via
height of a 1.6 mm board gives:
- 1.31 mm on the six-layer stack, **0.98 nH**, against this model's 0.95 nH;
- 1.10 mm on JLC04161H-7628, **0.82 nH**, against 0.88 nH.

The published example and the closed form agree within about 7 percent on these boards.

### 5.3 A converter's power-stage capacitors (class R)

The input capacitor closes the switching loop, whose current changes at the switch edges; "This loop carries large
transient currents that can cause large transient voltages when reacting with the trace inductance" (TPS62933,
p.40). No via may sit in that loop and the capacitor stays on the IC's side (TPS62933, p.40; BQ25731 rule 2). The
converter's VIN and power-ground pins connect through pour, not through escape vias, so the escape fan protects
nothing there. With the fan gone, the geometry reads a 1210's rail pad about 2.8 mm from an AP64500's VIN pin
(pin to courtyard 1.23 mm plus half the 1210 courtyard's short side, 1.6 mm; long axis along the pin row), inside the
3.0 mm screen (VERIFIED arithmetic on B21's land). The output capacitors carry the inductor's ripple current and sit
with the inductor and the IC on one layer (TPS62933 12.1); the pin that decides nothing for them is the feedback
sense pin, which the AP63200 calls "Feedback sensing terminal" (DS41326 p.2).

### 5.4 An RC-filtered analog supply (class A)

The BQ4050's BAT pin is fed through 100 ohm and its VCC through 1 kOhm, the BQ77207's VDD through 300 ohm; their
corners are 16 kHz, 1.6 kHz and 5.3 kHz with the 100 nF capacitors. At 100 MHz one nanohenry is 0.63 ohm, under one
percent of the smallest of those resistors, so up to that frequency the millimetres between a seat in the fan and a
seat outside it do not change what the filter does (INFERRED arithmetic). The PBI capacitor is a hold-up reservoir
for brief outages, where the value matters and the loop does not. What the makers ask is placement near the device
and separation from the high-current path (BQ4050 pp.42-43, BQ77207 p.17): the track from the capacitor to the pin
carries the filtered supply, and what it picks up there the filter no longer removes.

### 5.5 Effective capacitance at bias

**TBD.** No maker DC-bias curve for these ceramics is in the tree; `derate.py:19-21` and `PCB-GOLDEN-RULES.md:320`
record DC-bias derating as an open gap, and round 4's loop design uses INFERRED bands for the same reason. Its effect
is on value and count (how much of a 25 V X7R's capacitance is left at the pack's 16.8 V is exactly what is not
known, and for class L whether the regulator's minimum is still met at bias), not on placement: above series
resonance the impedance does not depend on the value (AN 574, p.6). It stays with DEC-001's value half and with
`derate.py`.

## 6. The ruling

Decision 42 is **taken by the session under the owner's standing rule of 26 September 2026**. It replaces the one
3 mm rule and the uniform fan with rules per class. A capacitor's class is its ROLE as its maker describes it, never
its value string. Every clause names its source.

**Class R, a converter's own power-stage capacitors** (AP64500, AP63203/AP63205, TPS62933, the LM5176 power stage,
the BQ25731 input loop).
- R1. The input capacitor that closes the switching loop sits on the IC's own side, across VIN and the IC's power
  ground (pin or exposed pad), connected by surface copper with no via in the loop (TPS62933 12.1, p.40; AP64500
  Layout item 2, p.23; AP63200 Layout item 4, p.15; BQ25731 Table 12-1 rule 2, p.93). Its rail pad is within 3.0 mm
  of the VIN pin; the 3.0 mm is kept as a screen and is reachable (section 5.3). It is declared against the VIN pin,
  never against EN or a sense pin.
- R2. The escape fan does not apply to a converter's own power-stage parts placed against that converter: its input,
  output and bootstrap capacitors, inductor and, for a controller, its FETs and sense resistor. It stays closed to
  every other part.
- R3. Never on the other side. For BQ25731 only, bulk beyond the loop's own ceramic may go to the other side on a
  board assembled on both sides ("Move part of CBUS to the other side of PCB for high density design", rule 2).
- R4. Sense pins take no capacitor declaration. LM5176: CIN is declared against the power loop (QH1, QL1, RSENSE),
  not against a controller pin (SNVSAI1D 10.1), and VISNS (pin 3) takes none. A converter's output capacitors are
  declared against the output loop (the inductor's output pad), on the IC's layer (TPS62933 12.1), with their rail
  pad within the 3.0 mm screen of that pad, and not against FB (AP63200 pin 1). The LM5176's VIN (pin 2) and BIAS
  (pin 24) take their own small capacitors under class D, and VCC (pin 23) under class L.

**Class D, a capacitor a maker ties to a supply pin, of any value** (the per-pin 100 nF of the STM32H743,
PI7C9X2G404SL, TUSB8041, TUSB2046B, KSZ9897R, TMUXHS4212, TS3DV642, TPS23861, PCM2912A, RP2040, INA226 and the
logic parts; AN4938's 4.7 uF minimum per package, which 7.4 ties to "the appropriate pins"; the CP2102N's 4.7 uF and
0.1 uF at VREGIN; an LDO's input capacitor; the TPA6132A2's 2.2 uF at VDD; the LM5176 VIN and BIAS capacitors).
- D1. Value and count are the maker's (section 4); where the maker states none (PI7C9X2G404SL) the count is TBD
  and the generator's own count stands, said as such.
- D2. The seat is the **own-pin window**: on the part's side, directly in front of the pin it serves, long axis along
  the pin row, rail pad within 3.0 mm of the pin (screen), ground pad taken to the ground plane directly with its own
  via (SCAA082A 2.4, p.13; AN 574, p.13; AN4938 9.3, p.38). **The gate does not check that today.** Its reach test
  (`intent_checks.py:23`, `:230-240`, applied at `:262`) passes a pad that has any via of its net within 1.5 mm,
  whether or not another part's pad shares it, or that lies in a pour of its own net on any copper layer. It asks
  nothing of a pad whose net has no pour on the board: a track-carried rail, whose loop is the pad-to-pin distance
  alone. So "its own via" is a new check (T10), not an existing one.
- D3. The window is the only part of the fan opened: a strip one capacitor courtyard wide, centred on that pin, from
  the courtyard edge to the fan edge. The escape pass reports per part the escapes each window costs. A window that
  costs an escape the part needs is closed again and the capacitor takes D4 or D5. Opening the whole fan is not
  ruled: that cost 49 escapes on board A on 20 September (A81, appendix 32.311).
- D4. Fallback: the seat with the smallest loop-equivalent distance the placement leaves, recorded per capacitor as
  a justified deviation with its distance and estimated extra loop (section 5.2), under DEC-001's own waiver policy
  (authority SESSION, scope one capacitor, expiry the next placement, residual risk measured at the prototype,
  `pcb_rules.yaml:617-618`).
- D5. **The side opposite the part**, under board B's underside rule kept as written.
  - **Boards.** The other side is a seat only on the boards already assembled with SMD parts on both sides: **B21, C24
    and D12** (section 3.3). It is not taken on **A32, E17 or P4**: A32's back carries only through-hole parts and
    E17's and P4's nothing, so a first SMD part there adds an assembly side, which is money and not the session's.
  - **The rule it is bound by, quoted.** Board B's region comment reads "decoupling and pull-ups on the UNDERSIDE (B16
    is assembled on both sides), never beneath a fine-pitch part whose escapes need the vias" (`gen_pcb_b3.py:155`).
    The B16 generator record reads "never under a fine-pitch part (its escapes need the vias) and never under a
    through-hole header" (appendix, `MESHSAT-709-geometry-appendix.md:3010`).
  - **The harm when it is not kept, measured three times.**
    - Placed B19 had 71 back-side parts under the three 0.40 mm PCIe switches (`gen_pcb_b3.py:346-353`; appendix
      32.174 item 3).
    - "no stub path at via" at those parts is the pair pre-router's largest remaining failure class: 18 of the 48
      pairs it could not lay.
    - On board D, stepping a back-side region clear of a front fanned IC gave escapes 71 added and 4 skipped against
      68 and 7 (decision 44's evidence).
  - **Kept as written, it means two refusals.** A far-side seat is refused inside the fan box of every part in the
    fanned set, on either side of the board. The fan box is the courtyard grown by 2.2 mm (`_fan_box`). The fanned set
    is the one T1 rules, the union of two terms:
    - **Every part the escape pass escapes.** That is `escape.py`'s `is_fine` (`escape.py:34-42`: SOT-23-6 or
      SOT-23-8 in the footprint name, or closest two SMD pads 0.7 mm apart or less, with no pad-count floor), less
      the two exemptions it already applies: a J part over 0.6 mm pitch, and the board's `ESCAPE_SKIP` (`:176-177`).
      That is the purpose the fan's own docstring states: "Any part that will be escaped needs the room its fan
      takes" (`bypass_slots.py:39`).
    - **Every part `_needs_fan` selects when counted on numbered copper pads** (eight or more, closest two 1.0 mm
      apart or less). This term keeps the 0.8 mm TQFP and LQFP fans of the 9 September lesson (D12's U4 and U6),
      which the escape pass does not escape. It also keeps the parts board B's `ESCAPE_SKIP` leaves to the router
      (U3, U4, J_HDMI).
    - **The 16:42 version used the second term alone.** That left out the parts the escape pass escapes with fewer
      than eight copper pads (section 3.2(g)): 14 on B21 (U82 and U83, MLPD-6 at 0.35 mm; U10, U21 and U22,
      WSON-6-1EP; nine SOT-23-6), 5 on C24 and 2 on D12 (U15, WSON-6-1EP; U5, SOT-23-6), and 1 on A32, 9 on E17 and
      1 on P4, where no far side is offered. So board B's rule, "never beneath a fine-pitch part whose escapes need
      the vias", was still narrowed at those parts.
    - **The box holds the escape vias.** Every nearest locked via of a signal pad's own net within 3.5 mm of an
      escaped part's pad lies inside that part's fan box, 1,087 of 1,087 on the six boards (3.2(g)).
    - **The set covers board B's own obstacle knob.** It holds every part `PLACE_NO_UNDER_FINE` would treat as
      fine-pitch (`is_fine`, `gen_pcb_b3.py:356-364`, with 16 or more SMD pads, `:396`). Read on B21, C24 and D12
      there is no exception: 38, 4 and 3 parts, all inside the fanned sets of 75, 10 and 8
      (`drafts/dec_finesets.out`).
    - A far-side seat is also refused over any through-hole part's courtyard.
    - **What it keeps and what it changes against today's placers** (`drafts/dec_escset.out`). Both placers already
      test the fan boxes they build with no side filter (`bypass_slots.py:59-62` builds them, `:94-95` tests them;
      `bypass_place.py:74-77` and `:88-89`). The ruled set:
      - drops only the SOIC-8-1EP lands (7 on A32, 8 on B21), fanned today by their paste apertures alone (3.2(a))
        and not escaped;
      - keeps the four WSON-6-1EP (B21's U10, U21 and U22, D12's U15) and E17's six TDSON-8-1 FETs, which a
        copper-pad count alone would have dropped;
      - adds a box at 22 parts the escape pass escapes and no placer protects today: 1 on A32, 11 on B21, 5 on C24,
        1 on D12, 3 on E17 and 1 on P4.

      So no seat the rule admits, on either side, lies inside the box that holds an escaped part's escape vias.
    - **What the added boxes cost today's declared seats** (`drafts/dec_newfans.out`). C24's C3 and C4, the
      TLV75533's capacitors on the back, sit inside the fan box of U11, a SOT-23-6 beside them. D12's C17 sits inside
      U5's (section 7). The ruled placers seat those elsewhere on the next placement, or record a D4 deviation. The
      added boxes at B21's U25 and E17's U12 fall on their own converters' capacitors, which R2 exempts.
  - **Excluded whatever the geometry.** The other side is never used for a part whose maker names the same side:
    - the STM32H743 in its LQFP-100 (AN4938 9.3, "The following recommendations shall be followed", with Figure 21's
      "same side ... (all packages except BGA)", pp.38-39; section 4);
    - a converter's power stage (R3: TPS62933 12.1, BQ25731 Table 12-1).
  - **The test where it is allowed.** It is judged like every seat: its loop-equivalent distance is its in-plane rail
    pad to pin distance plus the board's via allowance (section 5.2: 3.7 mm on the six-layer stack, 2.3 mm on
    JLC04161H-7628, with their sensitivity). The seat with the smallest loop-equivalent distance wins on either side,
    and the 3.0 mm screen and D4 apply to that figure.
  - **What that leaves of the far-side seat** (`drafts/dec_farside.out`, on the committed boards and their intent
    files).
    - **At every fanned part, the far side under the pin is gone.** That covers every 0.4 to 0.5 mm part decision 42
      is about: the STM32H743, the PCIe switches, the USB hubs, the KSZ9897R, the CP2102N, the RP2040, the TPA6132A2
      and the rest. A far-side seat outside every fan box is at least as far from the pin, in plane, as the nearest
      own-side seat outside the fan (3.26 to 5.49 mm to the centre on the ruled set, section 3.1), and it adds the
      via allowance. So at a fanned part it never forms the smaller loop. It is a D4 fallback where the own side is
      full, recorded as a justified deviation like any other.
    - **At a small part the escape pass does not escape**, the far side under the pin stays open wherever the pin
      lies outside every fan box. That covers SOT-23-5 logic and LDOs, SOIC-8 and the sensors. It does not cover the
      SOT-23-6, WSON-6-1EP and MLPD-6 parts, which the escape pass escapes. On the current declarations:
      - **B21:** 4 of 30 entries (C12 and C13 at the AP2112K, C70 and C71 at the DS3231M). Its other 12 open
        entries are the AP64500 input capacitors, refused by R3 (the AP64500's SOIC-8-1EP is not escaped, so no fan
        refuses them). C4 to C6 at the AP63203, a TSOT-23-6 the escape pass escapes, are refused by its fan as well
        as by R3. C69's pin lies inside U61's fan box.
      - **C24:** 4 of 18 (C3 and C4 at the TLV75533, C25 at the 74LVC1G34, C38 at the VEML7700).
      - **D12:** 7 of 24 (C51 to C53 and C56 at the 74LVC1G gates, C7 to C9 at the TLV75533). C61 and C62 serve
        U15, a WSON-6-1EP the escape pass escapes, so the far side under its pins is refused (the 16:42 version
        counted them open). C54 and C55's pins lie inside U16's fan box.
      This is where D12's C53 already sits, at 2.8 mm loop-equivalent.
    - **So D5 does not resolve decision 42's conflict at any fine-pitch part.** The own-pin window (D2, D3) and D4
      do. D5's value is the small parts' seat and room on a crowded two-sided board.
  - **Escape cost.** Outside every fan box, a far-side seat takes no escaped or fanned part's escape room. At a part
    that is neither (a SOT-23-5, an SOIC-8), whose pins the escape pass leaves to the router, it can take a via site
    of that part's own pins, since nothing reserves one there on either side today. So the escape
    pass reports, per part, the vias refused by a far-side capacitor's pads, as D3 reports for windows (T4). D12
    carries three such seats: C51 to C53, 0.54 to 2.79 mm in plane from the U9 to U11 pins they serve, two of them
    under the neighbouring gates U10 and U11. That phase is recorded at 0 hard and 0 unrouted (decision 44), so on D12
    they cost no connection.
  - **Not ruled here.** A far-side window under a fine-pitch part like D3's own-side one. It would need the per-part
    escape cost D3 reports, and the evidence above starts it from a measured loss.
  - **Sources.**
    - The RP2040 guide 2.1.2, "a four layer PCB with components on both the top and bottom sides" (p.9), for the
      parts it covers. For the RP2040 itself, which is fanned, the kept rule leaves only seats outside its fan box.
    - AN 574 p.13 and pp.15-16 for the via cost.
    - AN4938 is not a source for the other side on board B: for its non-BGA packages it names the same side.
- D6. Where a maker gives a number, the maker's number is the limit: the TPA6132A2's VDD and HPVDD capacitors within
  5 mm of their pins, with a minimum-length ground return to the device (SLOS597B 9, p.17). The 3.0 mm screen stays
  the placers' target there; a D4 deviation may never pass the maker's 5 mm.

**Class L, a regulator's output or VCAP capacitor** (LDO outputs: TLV755P, AP2112K; an internal regulator's output:
STM32H743 VCAP, CP2102N VDD, LM5176 VCC, RP2040 VREG_VOUT, TPS25740 DVDD, TPA6132A2 HPVDD).
- L1. Seated as class D (D2 to D6), declared against the regulator's own output pin (the RP2040's is VREG_VOUT,
  pin 45, not the DVDD pins), its ground pad to the ground the maker names (LM5176: PGND, p.30).
- L2. Its maker's stability condition is checked with it: the value floor and, where stated, the ESR bound (TLV755P
  0.47 uF or larger, p.15; AP2112 1.0 uF, p.1; AN4938 VCAP 2.2 uF with ESR under 100 mOhm, p.12; LM5176 VCC 1 to
  4.7 uF, p.15; RP2040 1 uF, 2.1.3; TPA6132A2 HPVDD "only" 2.2 uF, p.17). Whether the floor holds at DC bias is
  section 5.5's TBD.

**Class A, an analog supply pin behind a series resistor, or a backup reservoir** (BQ4050 BAT, VCC and PBI;
BQ77207 VDD).
- A1. Topology: the capacitor sits at the pin end of its RC, on the IC's side, its ground returns to the IC's own
  ground without sharing a high-current conductor, and no high-current conductor runs between it and the pin or
  alongside the track to the pin (BQ4050 10.1, pp.42-43; BQ77207 8.4.1, p.17).
- A2. Distance: the makers' "as close as possible" made operational as the nearest free seat outside the fan, its
  distance recorded per capacitor. No fixed millimetre bar, because the series resistor dominates any loop
  reactance (section 5.4). The fan stays closed to them.
- A3. **Provisional for the protection parts.** Class A removes any millimetre bar for the BQ77207's VDD filter (the
  secondary protector) and for the BQ4050's BAT and VCC filters and PBI reservoir. That is part of the battery
  protection architecture, which review section 2 sends to a qualified reviewer before pack PCB release. So this
  stream does not treat it as settled: it goes into that review's packet as an item for the reviewer (section 10).
  Until the reviewer answers, A1 and A2 are the session's reading.

**Class B, bulk.**
- B1. **Rail bulk, only where the maker calls it that.**
  - **The makers' two clauses, and both are enforced.**
    - TUSB8041: "All power rails require a 10 µF capacitor or 1 µF capacitors for stability and noise immunity.
      These bulk capacitors can be placed anywhere on the power rail" (SLLSEE4E 10.1, p.37). Its layout list adds
      "In general, the large bulk capacitors associated with each power rail should be placed as close as possible
      to the voltage regulators" (11.1.1 item 7, p.38).
    - TUSB2046B: the same words (SLLS413L p.17, and p.18 item 5).
  - **Declared against the regulator, not the hub.** The entry names the regulator whose output feeds the rail and
    its output pin, not a hub pin. Value and count are checked against the maker's.
  - **No fixed distance.** The makers give no millimetre figure, and "anywhere on the power rail" rules out a pin
    distance to the hub. What is enforced is the direction: the placers seat it toward the named regulator's output
    pad, and the gate prints its rail-pad distance to that pad with the regulator named (T2, T5).
  - **Where it cannot sit near the regulator**, it is recorded as a justified deviation under D4's waiver policy,
    never counted as a pass.
- B2. A microfarad capacitor no maker places, and that closes no loop the makers describe. It keeps a pin distance:
  the gate's existing 6.0 mm from the pin it is declared against, a project screen and named as one, in every tool,
  placers included. Three parts are B2:
  - **KSZ9897R's 22 uF and 10 uF**, drawn on the rails in an example figure with no placement clause (DS00002330D
    Figure 4-8).
  - **The TPA6132A2's optional 10 uF** (SLOS597B 9.1: "connect an additional 10 μF or higher value capacitor between
    VDD and ground").
  - **C24's 4.7 uF (C28) on the e-paper supply.** It is PDi's C1, and the class is now read from the display maker
    (the TBD of the 15:25 version, closed).
    - PDi's EPD driving circuit note Rev. 02 (`v2/vendor/pdi/pdi-epd-driving-circuit-rev02.pdf`, p.4) draws C1 with
      a 0.1 µF beside it on the switched supply node, marked "Connect to Power Switch". That node feeds VDDIO (pin 15),
      VDD (pin 16) and the boost inductor L1.
    - Its table sets C1 at 4.7 µF / 6.3 V for group G2, which holds the 3.7 inch panels.
    - It says "All components and circuits are necessary" (p.3) and gives no placement or distance for any part.
    - So the value and the part are the maker's, and the seat is B2's. C28's declaration against J_EPD pin 16
      (`gen_sch_c.py:356`) stands, and C29 (100 nF, pin 15) is the maker's 0.1 µF (class D, 3.0 mm screen).
- No capacitor a maker ties to a pin, and no regulator output or VCAP capacitor, is class B (section 6a).

### 6a. Every declared microfarad capacitor above 1 uF, and the ones the generators owe (checker item 2)

| capacitors (board) | value, pin | class | clause |
|---|---|---|---|
| C8, C60, C71, C78, C89 (A32) | 4.7u, LM5176 VCC pin 23 | L | SNVSAI1D p.3, p.15, p.30 |
| C11, C63, C74, C81, C92 (A32) | 10u 50V, LM5176 VIN pin 2 | R, re-declared against the power loop (R4) | SNVSAI1D 10.1 |
| C12, C64, C108, C82, C116 (A32) | 10u 50V, LM5176 VISNS pin 3 | R, the VISNS declaration removed (R4) | SNVSAI1D p.3 |
| C29, C30, C35, C36, C41, C42, C47, C48 (A32) | 10u 25V, AP64500 VIN | R | DS41979 p.23 |
| C54 (A32) | 10u 25V, TPS62933 VIN | R | SLUSEA4D 12.1 |
| twelve 22u 10V (B21) | AP64500 VIN | R | DS41979 p.23 |
| C125, C130, C225, C230, C325, C330, C7 (B21) | 10u, TPS62933 VIN | R | SLUSEA4D 12.1 |
| C4 (B21); C31 (E17) | 10u, AP63203 / AP63205 declared at pin 2 (EN) | R, re-declared at pin 3 (VIN) | DS41326 p.2, p.15 |
| C5, C6 (B21) | 22u 6.3V, AP63203 declared at pin 1 (FB) | R, output capacitors, declared against the output loop (R4) | DS41326 p.2; SLUSEA4D 12.1 |
| C9 (D12) | 10u, TLV75533 OUT pin 5 | L | SBVS320D p.15, p.21 |
| C17 (D12) | 10u, TUSB2046B VCC pin 3 | B1, re-declared against U17, the regulator feeding +3V4_HUB in the round 4 generator (`gen_sch_d.py:103`) | SLLS413L p.17, p.18 item 5 |
| C33 (D12) | 10u, TPA6132A2 VDD pin 14 | B2 (the maker's optional additional capacitor) | SLOS597B 9.1 |
| C28 (C24) | 4.7u, J_EPD pin 16 | B2 (PDi's C1: value and part the maker's, no placement given) | PDi EPD driving circuit Rev. 02, pp.3-4 |
| C1 (P4) | 2.2u, BQ4050 PBI | A | SLUSC67B 8.2.2.2.2 |
| STM32H743 bulk, 10u per controller (B, `fnd/r4b` `gen_sch_b.py:1118`) | AN4938's "min. 4.7 μF" | D | AN4938 7.4, p.32 |
| STM32H743 VCAP, 2 x 2.2u per controller (`fnd/r4b` `:1147`) | VCAP | L | AN4938 2.2, p.12 |
| CP2102N VDD 4.7u (B, `gen_sch_b.py:356`) | the internal regulator's output | L | CP2102N Rev 1.5 p.5 |
| CP2102N VREGIN 4.7u + 0.1u (owed, G7) | tied to the pin | D | CP2102N Rev 1.5 p.5 |
| TUSB8041 10u on 1.1 V (B) | rail bulk | B1, declared against the 1.1 V regulator's output | SLLSEE4E 10.1, 11.1.1 item 7 |
| KSZ9897R 22u and 10u (owed, G7) | example figure | B2 | DS00002330D Figure 4-8 |
| TPA6132A2 2.2u at VDD and HPVDD (owed, G12) | tied to the pins, maker's 5 mm | D (VDD), L (HPVDD) | SLOS597B 9, 9.1 |

Against today's gate, which keys its limit on the value string (section 3.2(c)): every class D and L entry keeps
3.0 mm whatever its string (A32's bare "4.7u" at the LM5176 VCC stays at 3.0 mm as class L); the converter input
capacitors the gate reads at 6.0 mm ("10u 25V 1210", "22u 10V") come to class R's 3.0 mm at VIN, or to the loop
declaration for the LM5176; and six entries are relaxed, each by a named clause and none by its value: D12's C17
(bare "10u", 3.0 mm today; B1, TUSB2046B frees rail bulk), D12's C33 and C24's C28 (bare "10u" and "4.7u", 3.0 mm
today; B2 at 6.0 mm, since no maker places them), and P4's C1, C6 and C8 (3.0 mm today; class A).

**The three options of 20 September, and why each is taken where it is:**
- The other side: taken as D5, only in part.
  - **Where.** On the three boards already assembled on both sides (B21, C24, D12), under board B's underside rule
    as written: never inside the fan box of a part the escape pass escapes or the placers fan (T1), on either side,
    and never over a through-hole part. It is
    never used for a part whose maker names the same side (the STM32H743 in its LQFP, AN4938 9.3 and Figure 21;
    the converters, R3).
  - **What it gives.** A seat under the pin only at the small parts the escape pass does not escape: 4 of B21's 30
    current declarations, 4 of C24's 18 and 7 of D12's 24 (`drafts/dec_farside.out`). At a fanned part it gives a
    fallback where the own side is full (D4), never the smaller loop.
  - **What it does not answer.** The fine-pitch capacitors this decision was asked about, where the loop comparison
    of 5.2 alone could favour the far side (on C24 and D12 against an own-side seat past about 2.8 mm, on B past
    about 4.2 mm). That comparison is not used there, because the escape evidence
    (gen_pcb_b3.py:346-353, appendix 32.174, decision 44) says those seats cost the escapes the fan exists to keep.
  - **Not taken** on A32, E17 and P4, where it adds an assembly side.
- Inside the fan: taken as the own-pin window (D2, D3) and for a converter's own parts (R2). Not taken as "anywhere
  in the fan".
- A larger limit: taken only where a source supports it: the maker's own 5 mm for the TPA6132A2 (D6), rail bulk the
  maker frees (B1) and RC-filtered analog pins (A2); B2 keeps the gate's existing 6.0 mm as a project screen. Not
  taken as one larger number for capacitors tied to a pin, where every millimetre costs a quarter to two fifths of a
  nanohenry.
- The register's own recommendation of 20 September (measure the underside on board A's three first) is not taken:
  those three are not fine-pitch decoupling at all (section 7), the other side is forbidden for converter input
  loops, and board A carries no SMD part on its back.

## 7. What it closes in decision 42's residue, and board D's other-side entries

| board | residue named on 20 September | what it is (VERIFIED unless marked) | under the ruling |
|---|---|---|---|
| A | C36 at U5 pin 2, C42 at U6 pin 2, 13.2 mm | AP64500 input capacitors; the fan is a paste-aperture artefact (3.2(a)); the placers held a 10 uF to 3.0 mm the gate judges at 6.0 (3.2(b)). In the candidate U5 is an LM5176 stage (S2) and C36's role changes (`fnd/r4a` `gen_sch_a.py:761`) | class R: R1 and R2 seat it at the pin (about 2.8 mm, section 5.3). For the S2 stage, R4 |
| A | C108 at U15 pin 3, 25.8 mm | a 10 uF power-stage CIN declared against VISNS, a sense input with no decoupling requirement (LM5176 pin table, p.3); W2's F-DC-01 | R4: the declaration is removed and CIN is judged against the power loop |
| P | C1, C6, C8, 11.0 to 11.3 mm after the seat arm | PBI reservoir and two RC filters of a gauge that "does not require an external decoupling capacitor" | class A: the 11 mm seats are within A2 provided they are the nearest free seats outside the fan and A1's topology holds on the four-layer board. P4 is single-sided and stays so |
| B | 19 of 30 with no seat within 12 mm | 22 of the 30 sit on fanned parts: 12 AP64500 inputs (artefact), 7 TPS62933 inputs, 3 at the PoE controller of which 2 are mis-declared (C37, C38 serve the TS3DV642s) | class R for 19, class D for C36 and the re-declared C37/C38. Whether 19 still find no seat within 12 mm under these rules, with the other side now a seat on B under D5, is a floor-plan reading that has to be retaken (decisions 13 and 43), not assumed. The other side does not change it: 19 of the 22 serve converters (R3), and C36 to C38 serve fanned parts, where D5 leaves only seats outside every fan box |

**Board D's eleven other-side entries (checker item 1, and the fan reading of the 16:42 correction).** D12 is not in
decision 42's residue. Decision 44 keeps D12 for this revision: the region change goes into a commit that re-cuts D
for another reason. Under D5 each entry is read two ways:
- **Its seat,** against every fan box and through-hole courtyard (`drafts/dec_farside.out`, VERIFIED from the board
  text).
- **Its loop-equivalent distance:** the in-plane rail pad to pin distance (VERIFIED by `drafts/dec_sides_decl.py`)
  plus D12's 2.3 mm allowance (INFERRED).

| capacitors | serves | class | in plane | loop-equivalent | reading under the ruling |
|---|---|---|---:|---:|---|
| C53 | U11 pin 5 (74LVC1G04) | D | 0.54 mm | 2.8 mm | within the 3.0 mm screen |
| C52, C51 | U10, U9 pin 5 (74LVC1G08) | D | 1.66, 2.79 mm | 4.0, 5.1 mm | past the screen because of their side: on D's next placement an own-side seat (1.48 mm to the centre at best, `drafts/dec_geom_pcb-d-aprs-d9.txt`) is the smaller loop, unless the placement leaves none |
| C54, C55 | U12, U13 pin 5 | D | 12.21, 11.24 mm | 14.5, 13.5 mm | past the screen whatever their side; the pins lie inside U16's fan box, so no far-side seat under them is allowed; a nearer seat has to come from the front or from the back outside that fan box, on D's next placement |
| C8, C9 | U1 pin 5, TLV75533 OUT | L | 9.32, 10.38 mm | 11.6, 12.7 mm | past the screen whatever their side |
| C15, C16 | U4 pin 3, TUSB2046B VCC | D | 17.42, 21.63 mm | 19.7, 23.9 mm | **present seat inadmissible**: both overlap the fan box of U7 (TPA6132A2, QFN-16 at 0.5 mm), where U7's escape vias come through, which is the case board B's rule forbids; also past the screen whatever their side |
| C17 | U4 pin 3 | B1 | 12.48 mm | | rail bulk: no pin distance, so its side does not matter, but **its present seat is inadmissible**: it overlaps the fan box of U5, a SOT-23-6 the escape pass escapes (the 16:42 reading, on the copper-pad set alone, called it clear). Its distance to the hub's regulator (U17 in the round 4 generator, not on D12) is read on D's next cut |
| C18 | U6 pin 2, PCM2912A | D | 21.66 mm | 24.0 mm | past the screen whatever their side |

So of the eleven:
- **one is admissible now** (C53);
- **two are past the screen only because of their side** (C51, C52);
- **seven are past it at any side**, and two of those seven, C15 and C16, also sit where the rule forbids (inside
  U7's fan box);
- **one, C17, is rail bulk with no pin distance**, but it also sits where the rule forbids (inside U5's fan box).

The front side fares no better. **Ten of D12's thirteen own-side declarations** are past their limit, at 5.40 to 32.1
mm (C62 at 5.40 mm is the nearest; `drafts/dec_sides_decl.out`). Two, C56 and C7, are within it. The remaining one,
C61, has no pad on its declared net
(+5V_D8) on D12. The round 4 generator made C61 the new VGG regulator's 1 uF input capacitor (`gen_sch_d.py:524-533`),
while D12 still carries the TPS22810's 4.7 nF slew capacitor under that name, on /VGG_CT. So the gate would fail it on
connectivity, not distance, until D is re-cut.

**D12 fails a maker's number (D6), not only a screen.** C31 (HPVDD) sits 18.1 mm and C32 (VDD) 13.6 mm from their
TPA6132A2 pins, against SLOS597B's "within 5 mm". A D4 deviation cannot justify that. Under this ruling D's DEC-001 is
a FAIL at U7 as soon as T2 carries the maker cap, whatever the allow file says.

D12's present DEC-001 PASS is the blanket allowance of section 3.2(f) and stays evidence awaiting revalidation
(section 9). Nothing on D12 moves for this ruling, because decision 44 keeps D12 for this revision. D's next cut
carries G12 (2.2 uF at both pins, within 5 mm), and moves C15 and C16 out of U7's fan box and C17 out of U5's. That
is named in section 10, not assumed.

So decision 42 holds nothing that needs the owner: every clause above is a rule with a source or a measurement.
What remains is work with named owners (section 10).

## 8. What changes, and who changes it (specified here; not edited by this stream)

### 8.1 Tools (the integrator)

- T1. **The fan set follows the escape pass.** A part is fanned when either term holds:
  - **The escape pass escapes it.** `is_fine`, `min_pitch` and the two exemptions `escape.py` applies (a J part over
    0.6 mm pitch, the board's `ESCAPE_SKIP`) move out of `escape.py:34-49` and `:176-177` into one selection
    function. `escape.py`, `bypass_slots._needs_fan` and `bypass_place.py:74-77` all call it. `escape.py` loads the
    board and lays copper when it is run, so the placers cannot import it as it stands: only the selection moves.
    A later change to what the escape pass escapes then moves the fan with it. The placers read the board's
    `ESCAPE_SKIP` from the same `escape_env` that `full.sh` passes to `escape.py` (`full.sh:27`, `:162`;
    `tools/boards/<x>.json`).
  - **It has eight or more numbered SMD pads that carry copper, the closest two 1.0 mm apart or less.** This is
    today's `_needs_fan` (`bypass_slots.py:38-49`) with the paste apertures no longer counted (3.2(a)). It keeps the
    0.8 mm TQFP and LQFP fans of 9 September, which the escape pass does not escape.

  Against today's set this drops only the SOIC-8-1EP lands and adds a fan at 22 six-pin parts (D5,
  `drafts/dec_escset.out`). Fixtures:
  - a `SOIC-8-1EP` land at 1.27 mm with its four paste apertures is not fanned;
  - a `WSON-6-1EP` at 0.65 mm with its two paste apertures stays fanned: it has seven copper pads, and the escape
    term holds;
  - a SOT-23-6 and B21's MLPD-6 (U82, 0.35 mm) are fanned, with six and seven pads;
  - a TQFP-32 at 0.8 mm (D12's U6) is fanned, though the escape pass does not escape it;
  - an LQFP-100 is fanned;
  - a part in `ESCAPE_SKIP` is fanned only when the copper-pad term holds (B21's U3);
  - `escape.py` and both placers call the same selection function (the test fails if any of the three files carries
    its own copy).
- T2. One limit function, used by `bypass_place.py`, `bypass_slots.py` and `intent_checks.py`, keyed by the entry's
  class (R, D, L, A, B1, B2), never by the value string, measuring rail pad to pin in all three (3.2(b), (c), (d)),
  with a per-part maker cap (the TPA6132A2's 5 mm, D6) that no allowance can exceed. Fixtures: a "10u" and a "10u 25V
  1210" of the same class get the same limit; a class L "4.7u" keeps 3.0 mm; a class B1 entry has none.
- T3. The placers try the four rotations and keep the one that brings the rail pad nearest the pin (3.2(e)).
- T4. The fan is opened for a class R entry's own converter (R2) and for a class D or L entry's own-pin window only
  (D3). The escape pass prints, per part, the escapes lost to each of three causes:
  - to the own-pin windows (D3);
  - to R2's opening: a converter's own power-stage parts inside its fan, where the converter still has signal pins
    to escape (the TPS62933's SOT-583 at 0.5 mm has RT, EN, SS and FB; SLUSEA4D pin table, p.3);
  - to a far-side capacitor's pads under a part that is neither escaped nor fanned (D5), as vias refused at that
    part's pins.

  An R2 opening that costs an escape the converter needs is closed again for the part that costs it, as D3 does for
  a window. Fixtures: a window that blocks a pin's only escape is reported by name, and so is an R2 part.
- T5. `intent.bypass` takes a class and a basis (the maker clause), and `intent.write` refuses an entry without one.
  - A class L entry also carries the maker's value floor and ESR bound.
  - An entry whose maker names the capacitor's side carries that as a flag (the STM32H743 in a non-BGA package, AN4938
    9.3 and Figure 21; every class R entry).
  - A class B1 entry names the regulator and output pin it is declared against.
  - A power-stage loop declaration (input or output capacitor, FETs, sense resistor, inductor) replaces declarations
    against VISNS, FB and EN pins.
- T6. `intent_checks.py:244-258`: an allow line must name its capacitor ("C36: reason"); a line naming none is
  refused; allowed entries are counted as `justified`, printed by name, and never counted as `pass`. The 8 September
  blanket lines are deleted from `v2/ecad/pcb-*/bypass-allow.txt` (the reason they give, "an owner decision", is
  this ruling). The phase snapshot copies under `pcb-*-a23`, `-b19` and the like stay as history.
- T7. The registry entry below replaces DEC-001's sources, status, acceptance and rationale.
  - **The per-device clause stays open.** DEC-001's own clause, "The distance itself is derived per device from the
    current's spectral content, not taken as one project-wide number", is kept and not dropped. This ruling does not
    derive that distance, because it needs each device's supply-current edge rates, which are SI-001's declared edge
    rates (`pcb_rules_coverage.yaml`, DEC-001's `depends_on: [SI-001]`), and most are not declared yet.
  - **So the category stays.** The coverage map keeps `gap_category: HEURISTIC_AS_LAW` until two things hold: T1 to
    T6, T9 and T10 are enforced, and the per-device derivation exists for classes D and L. Until then the 3.0 mm
    screen still separates a pass from a justified deviation for classes D and L, and the page says so. The map also
    names `bypass_seats.py` against the new classes.
- T8. **In the same commit that merges this ruling**, run `python3 tools/rules_render.py` and commit the re-rendered
  `PCB-OPEN-PAIRS.md` with it. It is generated from the register, and on a tree that holds the routeflow journals
  `rules_render.py --check` fails it until it is re-rendered, so the suite's
  `t_the_documents_are_generated_and_not_hand_maintained` fails on the box. This stream's worktree lacks those
  journals, which is why its own suite does not show it. Its effect was isolated
  here on 26 September by rendering twice on the same evidence, once with HEAD's `pcb_decisions.yaml` and once with
  this ruling (session record `drafts/PCB-OPEN-PAIRS.decision-42.isolated.diff`): board A's DEC-001 moves from
  decision-bound to a measured failure, the "By open decision" section goes, and the open-pair total does not
  change. The total itself depends on the evidence present (121 in the 14:45 render, 134 in this worktree, which
  lacks gitignored verdicts), not on this ruling. The rule-set fingerprint does not move: it digests only
  `pcb_rules.yaml`'s deciding fields (`rules_lib.py:230-239`) and reads `ff8151db3576437b` here and on main.
- T9. The other side (D5). Every test below is geometric, so it can run when the seat is chosen, before the packer
  and before the escape pass.
  - **Which boards.** The placers and the gate read a board's two-sided status from its placed board: SMD footprints
    on B.Cu present, as `drafts/dec_sides.py` reads it. They offer far-side seats only there.
  - **Where a seat is refused.** Inside the fan box of every part in T1's fanned set on the board, whichever side it
    is on. Both placers already test their fan boxes this way for the parts on the board at that moment:
    `bypass_slots.reserve` builds its fan list from every footprint (`bypass_slots.py:59-62`) and tests it with no
    side filter (`:94-95`), and `bypass_place` does the same (`:74-77`, `:88-89`). That test is kept, on T1's set,
    and it gains every through-hole part's courtyard, of either side.
  - **Parts placed after the seat.** At reservation only the fixed parts are placed (`bypass_slots.py:8`). So the
    same test runs again in the gate on the placed board, after the packer: a declared capacitor whose courtyard
    overlaps a fan box or a through-hole courtyard on the other side is refused, never allowed.
  - **Parts whose maker names the same side.** Entries with the maker's same-side flag, carried by T5 (the STM32H743
    in any non-BGA package, and class R), are never offered the far side.
  - **The distance.** A far-side seat's distance is its in-plane rail pad to pin distance plus the via allowance. The
    allowance is computed from the board's stackup row in `stackup_write.py` by the two closed forms of
    `drafts/dec_loop.py` (0.25 mm track, 0.3 mm drill, 0.8 mm via pitch). On a placed board it is re-read with the
    seat's own via pitch.
  - **Fixtures.**
    - The allowances: B21 reads 3.7 mm, D12 2.3 mm.
    - The boards: a far-side seat on A32, E17 or P4 is refused.
    - The loop test: D12's C53 reads 2.8 mm.
    - The fan boxes: D12's C15 and C16 read refused (inside U7's fan box), C17 reads refused (inside U5's), and a
      far-side seat under any U4 or U6 pin is refused.
    - The escaped small parts: a far-side seat under D12's U15 (WSON-6-1EP) is refused, and so is one under B21's
      U82 (an MLPD-6 on the back, so the seat is on the front). A far-side seat under D12's U11 (SOT-23-5, not
      escaped) is offered.
    - The maker's side: a far-side seat for an STM32H743 LQFP entry is refused.
- T10. The ground pad's own via (D2). For every class D and L entry the gate names the ground via its capacitor's
  ground pad reaches, whether that via is its own (not also the landing of another part's pad), and the copper
  length between pad and via.
  - An entry with no via of its own is a justified deviation, never a pass.
  - The existing reach test stays for the rail pad. It counts any via of the net within 1.5 mm or a pour of the net
    (`intent_checks.py:230-240`).
  - No millimetre is set for pad to via: SCAA082A asks "directly with a via" and gives no figure, so the length is
    printed and judged with the per-device derivation (T7).
  - Fixtures: a capacitor whose ground pad shares a via with a neighbour's pad reads justified; one with its own via
    reads pass.

### 8.2 The registry text proposed for DEC-001 (`pcb_rules.yaml:588-619`)

```yaml
   source_status: PARTIALLY_VERIFIED
   sources:
    - {title: "AN4938 Getting started with STM32H74xI/G and STM32H75xI/G MCU hardware development", issuer: STMicroelectronics,
       revision: "Rev 7, October 2024", clause: "2.2 (p.12), 7.4 (p.32), 9.3 and Figure 21 (pp.38-39)",
       url_or_path: "v2/vendor/st/st-an4938-rev7.pdf", accessed: "2026-09-26",
       note: "sha256 217b5dcbfdd27cec4f6013cf1f51930bf81c338ccbaf7bf8dce3fa69592bb8b3; per-pin values, the 4.7 uF tied to the pins, no distance; same side as the MCU for every package except BGA (9.3, Figure 21)"}
    - {title: "TPA6132A2 25-mW DirectPath Stereo Headphone Amplifier", issuer: "Texas Instruments", revision: "SLOS597B, July 2017",
       clause: "9 and 9.1 (p.17)", url_or_path: "v2/vendor/ti/ti-tpa6132a2.pdf", accessed: "2026-09-26",
       note: "sha256 e8a23e00bd0bbc178b68696dfa7842bd4063fc085b8e2d8eef024594accf95d7; the only maker distance in the tree, 5 mm"}
    - {title: "High-Speed Layout Guidelines", issuer: "Texas Instruments", revision: "SCAA082A, August 2017", clause: "2.4 (p.13)",
       url_or_path: "v2/vendor/ti/ti-scaa082a-high-speed-layout-guidelines.pdf", accessed: "2026-09-26",
       note: "sha256 24681796ac36e50f...; lowest value closest, pad directly to the plane with two or three vias"}
    - {title: "AN 574 Printed Circuit Board (PCB) Power Delivery Network (PDN) Design Methodology", issuer: "Altera (Intel)",
       revision: "AN-574-1.0, May 2009", clause: "pp.6, 13, 16", url_or_path: "v2/vendor/standards/intel-an574.pdf",
       accessed: "2026-09-26", note: "sha256 9c6cb94e3dcc9fdc...; location sensitivity against plane dielectric; top against bottom mounting"}
    - {title: "the part makers' layout clauses, one per class", issuer: "TI, Diodes, Microchip, Silicon Labs, Raspberry Pi",
       revision: "as listed in v2/docs/feasibility/DECOUPLING.md section 4", clause: "section 4 of that page",
       url_or_path: "v2/docs/feasibility/DECOUPLING.md", accessed: "2026-09-26",
       note: "one maker in the tree gives a millimetre figure (TPA6132A2, 5 mm); the class rules follow the makers' words"}
   acceptance_criteria: >
     Each declared decoupling entry states its pin, its distance, its via count and the loop it forms, and names its
     class, by the role its maker gives it and never by its value, and the maker clause behind it. Class R (a converter's own power-stage capacitor): on the IC's side, the input capacitor's rail
     pad within 3.0 mm of VIN and declared at VIN, no via in the loop, output capacitors declared against the output
     loop; the fan does not apply to the converter's own power-stage parts; never on the other side. Class D (a
     capacitor a maker ties to a supply pin, any value) and class L (a regulator's output or VCAP capacitor, with the
     maker's value floor and ESR bound): rail pad within 3.0 mm in the part's own-pin window, ground pad to the plane
     by its own via; where a maker states a distance, that distance is a hard limit; on a board already assembled
     with SMD parts on both sides, a seat on the other side is judged by its in-plane distance plus the stackup's via
     allowance, and is never inside the escape fan of a fanned part on either side, never over a through-hole part,
     and never used for a part whose maker names the same side; otherwise a justified deviation naming the
     capacitor, its distance and its loop estimate. Class A (a
     supply pin behind a series resistor, or a backup reservoir): the nearest free seat outside the fan at the pin end
     of its RC, with no high-current conductor between or alongside (provisional for the battery protection parts
     until the qualified review of review section 2). Class B1 (bulk the maker calls rail bulk): value and count, no
     pin distance, declared against the regulator that feeds the rail and seated toward it, its distance printed.
     Class B2 (bulk no maker places): 6.0 mm from the pin it is declared against. The 3.0 and 6.0 mm are project
     screens, not maker numbers. The distance itself is derived per device from the current's spectral content, not
     taken as one project-wide number; until that derivation exists for a device, its screen decides only between a
     pass and a justified deviation. A justified deviation is counted as such and never as a pass.
   rationale: >
     Loop inductance decides high-frequency decoupling, and what forms the loop differs by class: the switching
     loop of a converter, the track from a capacitor to its pin where the rail is not a plane, the far-side vias, and
     nothing that matters behind a series resistor. A regulator's output capacitor is also part of its stability. One
     maker document in the tree gives a distance (decision 42, ruled 26 September 2026).
```

The `intel-an574.pdf` path assumes the integrator moves `drafts/datasheets/intel-an574.pdf` into
`v2/vendor/standards/`, with the line from `drafts/datasheets/SOURCES.txt`.

### 8.3 Generators (each board's writer)

| item | board | change | source |
|---|---|---|---|
| G1 | A | remove the VISNS declarations (`fnd/r4a` `gen_sch_a.py:456`, `:458`); give S2, SD, POE and PD a 0.1 uF VIN-pin capacitor to AGND at pin 2, declared class D; declare CIN against the power loop (T5); declare VCC class L | SNVSAI1D 10.1, p.30; pin table p.3; p.15 |
| G2 | A | U12: add the 0.1 uF at VIN and GND, class R; U33: declare C160 class R | SLUSEA4D 12.1, p.40 |
| G3 | A | declare C190/C191 class R against the BQ25731 input loop | SLUSE66A Table 12-1 rule 2 |
| G4 | B | `buck_small` (`gen_sch_b.py:350`): add the 0.1 uF at VIN and GND on all seven TPS62933, class R | SLUSEA4D 12.1 |
| G5 | B | re-declare C37 and C38 against U3 and U4 pin 1 (TS3DV642 VCC) instead of U5 pin 1 (`:990-991`) | SCDS343F pp.18, 23 |
| G6 | B | declare the capacitors of the STM32H743, PI7C9X2G404SL, TUSB8041, KSZ9897R, TMUXHS4212, TS3USB221A and CP2102N with their classes (section 6a); none is declared today, so DEC-001 has never judged them | section 4 |
| G7 | B | STM32H743: VDDA 100 nF + 1 uF of its own (W6-F7; VBAT stays tied to the rail, its 100 nF being AN4938's example). TUSB8041: four more 0.1 uF on the 1.1 V core. KSZ9897R: follow the maker's example, one 0.1 uF per supply pin (27), 22 uF on DVDDL, AVDDL and AVDDH and 10 uF on VDDIO (Figure 4-8). CP2102N: 4.7 uF + 0.1 uF at VREGIN, class D | AN4938 2.2 p.12; SLLSEE4E p.38; DS00002330D p.51; CP2102N Rev 1.5 p.5 |
| G8 | P | declare C1, C6, C8 and C14 class A with their clauses. W2's F-DC-03 (protector FET bypass capacitors on wide copper, BQ4050 10.1.1 p.44; board P has only the terminal pair C11/C12, `gen_sch_p.py:291`) stays with board P's writer, INFERRED from TI's figure labels | SLUSC67B, SLUSEG7D |
| G9 | C | RP2040 ADC_AVDD and USB_VDD 100 nF each, class D (round 4 O-C1) | RP2040 guide 2.1.2 |
| G10 | B | U25 (AP63203): declare C4 at pin 3 (VIN), not pin 2 (EN) (`gen_sch_b.py:984`); declare C5 and C6 against the output loop, not pin 1 (FB) (`:985-986`); U27 (AP2112K): C12 class L, C13 class D (`:987-988`) | DS41326 p.2, p.15; DS39724 p.1 |
| G11 | E | U12 (AP63205): declare C31 at pin 3 (VIN), not pin 2 (EN) (`gen_sch_e.py:622`, whose own comment at `:490` reads "2 EN 3 VIN") | DS41326 p.2, p.15 |
| G12 | D | U7 (TPA6132A2): C31 at HPVDD and C32 at VDD become 2.2 uF, X5R or better, 0402 where the rating allows, both within 5 mm with a minimum-length ground return (on D12 they sit 18.1 mm, C31, and 13.6 mm, C32, from their pins, so the next D placement seats them, and G12 without that seat does not meet SLOS597B); C33 (10 uF) stays, optional, class B2 (`gen_sch_d.py:379`, `:609-611`); correct the citation "SLOS553" (`:148`) to the tree's SLOS597B | SLOS597B 9, 9.1, p.17; figures pp.14, 16 |
| G13 | C, E | RP2040: the DVDD net (C: C_DVDD; E: E6_DVDD) carries two 1 uF today, C14 and C15 on C, C45 and C46 on E, both declared at the DVDD pins 23 and 50 (`gen_sch_c.py:349`, `gen_sch_e.py:620`). The guide asks 1 uF at VREG_VOUT and 100 nF per power pin. So the net needs **three** capacitors: one 1 uF declared against VREG_VOUT (pin 45), class L; and one **100 nF** at each DVDD pin, 23 and 50, class D. The second 1 uF becomes one of the two 100 nF and **one 100 nF part is added**, so the net holds 1 uF + 2 x 100 nF. The VREG_IN 1 uF (C16 on C, C47 on E, pin 44) stays, class D | RP2040 guide 2.1.2 (p.8: "a 100 nF capacitor per power pin"), 2.1.3 (p.9: "1 μF capacitors close to both the input (VREG_IN) and the output (VREG_OUT)") |
| G14 | C, D, E | declare classes on every entry (section 6a for the microfarad ones); D: C8 and C9 class L, C17 class B1 | section 6a |

## 9. Evidence status of DEC-001 today (review section 1)

| board | reading | class |
|---|---|---|
| A | FAIL, 10 of 40 on A32 | valid historical evidence about A32 only; the ten are capacitors A32 predates, the other thirty are allowances |
| B | PASS, 30 of 30 on B21 | **not evidence**: 30 allowances; awaiting revalidation after T6 on the current candidate |
| P | PASS, 3 of 3 on P4 | **not evidence**: 3 allowances; awaiting revalidation |
| C, D, E | PASS on C24, D12, E17 | awaiting revalidation: same blanket files; 17 of 18, 19 of 24 and 16 of 18 entries read past the limit here (INFERRED, section 3.1); on D12, 11 of the entries sit on the other side and are read in section 7, three of them inside a fan box (C15 and C16 in U7's, C17 in U5's), and the TPA6132A2's two capacitors are past the maker's 5 mm, so under this ruling D12 reads FAIL at U7 once T2 lands |

## 10. Open, with bound and owner

| item | bound | owner |
|---|---|---|
| T1 to T10, the tool, registry and page changes, and the re-render of `PCB-OPEN-PAIRS.md` in the merge commit (T8) | until they land, no DEC-001 reading on any board is current evidence | the integrating writer of `v2/ecad/tools/` |
| G1 to G3 | board A's DEC-001 cannot be judged against the candidate | board A's writer (round 6) |
| G4 to G7, G10 | board B's fine-pitch parts carry no declared decoupling; five circuit gaps (the TPS62933 0.1 uF, STM32 VDDA, TUSB8041 core, KSZ9897R, CP2102N VREGIN) and three mis-declared pins | board B's writer (round 6) |
| G8 and F-DC-03 | board P's four entries unclassified; FET bypass INFERRED | board P's writer |
| G9, G13, G14 on C | board C's two RP2040 pins undecoupled; the regulator output declared at DVDD | board C's writer |
| G11, G13, G14 on E | the AP63205 input declared at EN; the regulator output declared at DVDD | board E's writer |
| G12, G14 on D | the TPA6132A2 fitted 1 uF at VDD and HPVDD against the maker's 2.2 uF, and on D12 seated 18.1 and 13.6 mm from its pins against the maker's 5 mm | board D's writer (values), the integrator (the seat, with D's next cut) |
| board D's eleven other-side entries | re-judged by the loop-equivalent distance on D's next placement, with C15 and C16 moved out of U7's fan box and C17 out of U5's, where board B's rule forbids them; nothing moves on D12 (decision 44) | the integrator, with board D's next cut |
| the escape cost of the own-pin windows, of R2's openings and of far-side seats under parts neither escaped nor fanned, per part (T4), and the re-seat of A, B and P and of C24's C3 and C4 out of U11's fan box (T1) | measured on the next placement of each board after T1 to T5, T9 and T10 (placement only, on the rented box) | the integrator |
| PI7C9X2G404SL decoupling requirement | **TBD**: DS40068 Rev 5-2 has none; its 12 capacitors for 26 supply pads stand on the generator's own count. A request for Diodes' reference design is drafted in the session record, to be sent by the session that handles outside contact | the session |
| effective capacitance at DC bias | **TBD**: no maker curve in the tree; affects bulk value and count and whether a class L floor holds, not placement (5.5) | the session, with `derate.py`'s open gap |
| rail noise at each class D part and converter input ripple | the prototype measurement DEC-001's waiver policy names; nothing is built | TEST-PLAN |
| board B's 19 with no seat within 12 mm (20 September) | retaken under these rules on the next placement; its floor plan stays decisions 13 and 43 | the integrator |
| class A for the BQ4050 and BQ77207 (A3) | provisional: it removes any millimetre bar for the secondary protector's VDD filter and the gauge's filters. It goes into the battery/protection qualified-review packet of review section 2 as an item for the reviewer, with the clauses of section 4 and the arithmetic of section 5.4, and is not settled here | the writer of that packet (stream BAT, `v2/docs/review-packets/battery/`, not yet merged) |
| the per-device distance for classes D and L (DEC-001's own clause, T7) | open: it needs each device's supply-current edge rates, which SI-001 declares; until then the 3.0 mm screen separates a pass from a justified deviation and `HEURISTIC_AS_LAW` stays | the session, after SI-001's declarations |

## 11. Sources

In the tree (`v2/vendor/`), sha256 of the file read:

| document | revision | path | sha256 |
|---|---|---|---|
| ST AN4938 | Rev 7, Oct 2024 | `st/st-an4938-rev7.pdf` | `217b5dcbfdd27cec4f6013cf1f51930bf81c338ccbaf7bf8dce3fa69592bb8b3` |
| TI SCAA082A | Aug 2017 | `ti/ti-scaa082a-high-speed-layout-guidelines.pdf` | `24681796ac36e50f9c6ef5e0b98945b6236ddb9fa620da97597ba62a85990206` |
| Diodes AP64500 | DS41979 Rev 5-2, Dec 2024 | `diodes/diodes-ap64500.pdf` | `d3bcdc7dd4ca44cb36ef893d3dbfabbd1742dfc736557777868f6ead5d0a98e8` |
| Diodes AP63200 series | DS41326 Rev 3-2, Nov 2024 | `diodes/diodes-ap63200-series-buck.pdf` | `ef99daa3789d835bc025dfcb4c605c5c2e6d3e7223e86d40b33e6b497ea5a722` |
| Diodes AP2112 | DS39724 Rev 2-2 | `diodes/diodes-ap2112-ldo.pdf` | `ef8d376f2ec356e29172eb9e053819a0ebdcc576dba7fc9ab0505c568427920f` |
| TI LM5176 | SNVSAI1D, Aug 2021 | `ti/lm5176-datasheet.pdf` | `98191bec36d43771affa3e1540f6e1737347c19a1602747ffb4327509550a820` |
| TI TPS62933 | SLUSEA4D, Aug 2022 | `ti/ti-tps62933.pdf` | `16ec2eac43c7374eb9e7edd7df7bdb24de6862f695e1582c68716ced4820e5f6` |
| TI BQ25731 | SLUSE66A, Jan 2021 | `ti/bq25731-datasheet.pdf` | `3e5e927fdf63cf6a2397630987c58e947ebc80d5a1cfc93fb1fb58d98bb58973` |
| TI TLV755P | SBVS320D, Sep 2024 | `power/ti-tlv755p-ldo.pdf` | `7eb7bc6935bf6c1d247b2fce62c9e5a49a474fd94359ddc390a4baf0ac1f5293` |
| Diodes PI7C9X2G404SL | DS40068 Rev 5-2 | `diodes/diodes-pi7c9x2g404sl.pdf` | `675fa7ee40c91ad64db5e25abd75da2bc4c8e8e42f1569079d3b9cf1f2114687` |
| TI TUSB8041 | SLLSEE4E, Jun 2016 | `ti/ti-tusb8041.pdf` | `b715bce72e988310d18dbc8eb041a05b5f15e4a0b690843a873abdc373a1ad87` |
| TI TUSB2046B | SLLS413L, Jun 2017 | `ti/ti-tusb2046b.pdf` | `d02d0b8af5cbdb1b8186f890efdb214cb8edc50d55b9df5eed0650933a08d3db` |
| Microchip KSZ9897R | DS00002330D | `microchip/microchip-ksz9897-datasheet.pdf` | `72b89179ed6a42a7bafa737de31a21fc28db6f0852bcc7964546bc99b0c7d064` |
| TI TMUXHS4212 | SLASEP7A, May 2022 | `ti/ti-tmuxhs4212.pdf` | `34fa7c385e6aa8987e44a346219e15beac36e645e45b01d6542169f5b8e6d729` |
| TI TS3DV642 | SCDS343F, Aug 2018 | `ti/ti-ts3dv642.pdf` | `31e45a0729bc2e7164293fa902dd6daaa9089d51490518f80513a7bcaaea45d8` |
| Silicon Labs CP2102N | Rev 1.5 | `silabs/silabs-cp2102n.pdf` | `32fbab0ba17f394ab76fbbd8129bddad228c1c486a1693d96ea5905936e437fe` |
| TI TPS23861 | SLUSBX9I | `ti/tps23861-datasheet.pdf` | `65262ce4766a5f8e3b9f580ac02782ad7d5e35b39045fa5346288c21e240c093` |
| TI BQ4050 | SLUSC67B, Oct 2017 | `battery/ti-bq4050.pdf` | `2664e33fe6d6ebed3a0f58153d8ba8ce66cb84f07741f6708ae11a224f443f5e` |
| TI PCM2912A | SLES230A, Aug 2015 | `ti/ti-pcm2912a.pdf` | `61d048c255190975933032c6ff712c6b780d8390cbc40821a54fd29b62adbf32` |
| TI TPA6132A2 | SLOS597B, Jul 2017 | `ti/ti-tpa6132a2.pdf` | `e8a23e00bd0bbc178b68696dfa7842bd4063fc085b8e2d8eef024594accf95d7` |
| Raspberry Pi RP2040 hardware design | build 20/08/2026 | `rp2040/rpi-rp2040-hardware-design.pdf` | `51c4f430153fcdbf3209d9b3b41662c8527ff0150bc25777e3fcd6f5221a1c19` |
| Pervasive Displays EPD driving circuit | Rev. 02, Oct 2025 | `pdi/pdi-epd-driving-circuit-rev02.pdf` | `1ea68f814afe04ca5ee0aa64b12aaf00eb26a95e9e8d7b9d424ad4f74a278623` |

Not yet in the tree (session record `drafts/datasheets/`, with `SOURCES.txt`):

| document | revision | from | sha256 |
|---|---|---|---|
| Altera AN 574 | AN-574-1.0, May 2009 | intel.com via web.archive.org (`id_` copy of the publisher's file), fetched 26 September 2026 | `9c6cb94e3dcc9fdc1d2dd49dd56a1a7d1b47c35b29b4abaaef850a49c48b37d0` |
| TI BQ77207 | SLUSEG7D, May 2026 | https://www.ti.com/lit/ds/symlink/bq77207.pdf (round 4 board P stream's copy, hash checked) | `45c1c99e2d303be8bcf1a2b1eea8275f657c7c80170bda7c2778042a688295cb` |

Session records outside the vendor tree: W6's findings, `wt/w6/drafts/w6-findings.md` (lines 34, 58, 237-244, read 26
September) for W6-F7.

Formulas (section 5): E. Hammerstad and O. Jensen, "Accurate models for microstrip computer-aided design", IEEE
MTT-S International Microwave Symposium Digest, 1980 (the microstrip Z01 used for L'), and the two-wire line
inductance L' = (mu0 / pi) acosh(s / 2r). Both are estimates for comparing options, not a substitute for the
prototype measurement.

Session record (not in this repository, offered with section 8): `drafts/dec_geometry.py` (section 3.1),
`drafts/dec_sides.py`, `drafts/dec_sides_decl.py`, `drafts/dec_escset.py`, `drafts/dec_escvias.py` (section 3.2(g)),
`drafts/dec_newfans.py` (section 6, D5),
`drafts/dec_farside.py` and `drafts/dec_finesets.py` (sections 3.3,
6 D5 and 7), `drafts/dec_planes.py` (section 5.1),
`drafts/dec_fanwin.py` (section 5.2), `drafts/dec_loop.py` (sections 5.1 and 5.2), `drafts/dec_mmscan.py` (section 1)
and their outputs.

## 12. Corrections before merge

### 12.1 Corrections of 26 September 15:25

A checker read the 14:45 version against the artefacts and found three blocking errors. Each was checked again here
and each was right.

| item | what the 14:45 page said | what the artefacts show | corrected in |
|---|---|---|---|
| 1 | boards A, C, D, E and P are single-sided, so the other side is allowed on board B only, "on five boards it would add an assembly side" | C24 carries 135 SMD footprints on the back and 31 on the front, D12 71 and 128; eleven of D12's declared capacitors already sit on the back serving front parts; A32's back holds 21 through-hole parts and no SMD; E17 and P4 nothing (`drafts/dec_sides.py`, `drafts/dec_sides_decl.py`, section 3.3) | D5 now admits the other side on B21, C24 and D12 under one loop-equivalent test with a per-stackup via allowance (5.2); D12's eleven are read in section 7; decision 42's authority_why and outcome, the record section |
| 2 | class B was "above 1 uF, not closing a converter's loop", no pin distance, citing AN4938's 4.7 uF "for the package" | AN4938 7.4 p.32 ties the 4.7 uF to "the appropriate pins"; CP2102N p.5 requires 4.7 uF and 0.1 uF "for each power pin placed as close to the pins as possible"; the value cut put the STM32 VCAP, the CP2102N VDD and VREGIN capacitors and the LDO outputs (D's 10 uF at U1) in class B | classes by role (section 6): D any value, a new class L for regulator outputs and VCAP, B1 only where the maker calls it rail bulk, B2 at the existing 6.0 mm; every declared microfarad capacitor classed in 6a |
| 3 | the STM32H743 needs "VBAT to VDD with 100 nF", cited as W6-F7, and G7 told board B's writer to add it | AN4938 p.12 makes the VBAT connection mandatory and gives the 100 nF "as an example"; W6-F7 withdrew the VBAT shortfall and stands for VDDA only (`w6-findings.md:34`, `:58`, `:243-244`) | section 4 STM32 row, G7, section 10, the record section |

Found while correcting: the one maker distance in the vendor tree (TPA6132A2, 5 mm) and board D's value shortfall
against it (G12); the AP63203 and AP63205 input capacitors declared against EN (G10, G11); board B's AP63203 output
capacitors declared against FB (G10); the RP2040 regulator output declared at DVDD (G13).

### 12.2 Corrections of 26 September 16:42

A second checker read the 15:25 version and found two blocking errors, both in the far-side seat. Each was checked
against its primary source here and each was right.

| item | what the 15:25 page said | what the artefacts show | corrected in |
|---|---|---|---|
| 4 | D5: a far-side seat "is never taken over another pin's escape or ground via site (board B's own rule, `gen_pcb_b3.py:155`...)"; section 6's options: the other side "forms the smaller loop ... on nearly every fanned entry" of C24 and D12 | `gen_pcb_b3.py:155` reads "never beneath a fine-pitch part whose escapes need the vias", and the appendix at line 3010 adds "never under a through-hole header". `gen_pcb_b3.py:346-353` and appendix 32.174 record the harm: 71 back-side parts under the three PCIe switches, and "no stub path at via" at them as the pre-router's largest failure class (18 of 48). Decision 44 measured escapes 71/4 against 68/7 on D when a back-side region stepped clear. The page's per-via-site test narrowed that rule on a loop argument alone, and it could not be run when the seat is chosen (`bypass_slots.reserve` runs before the packer and the escape pass). D12's C15 and C16 already sit inside U7's fan box, which the page did not flag | D5 keeps board B's rule as written: never inside a fanned part's fan box, of either side, which both placers already test with no side filter, and never over a through-hole part. It says what that leaves: at fanned parts only a D4 fallback, never the smaller loop; a seat under the pin only at unfanned small parts (4 of B21's 30 entries, 4 of C24's 18, 9 of D12's 24, `drafts/dec_farside.out`). T4 reports the escape cost of far-side seats and of R2. T9's test is geometric and runs at seat time and again on the placed board. Also corrected: sections 1, 3.3, 5.2, 6 (options), 7, 9 and 10, decision 42's outcome, and the record section |
| 5 | Section 4's conclusion: "AN4938 permits 'below ... on the underside' for the STM32"; D5 cited AN4938 7.4 as a far-side source | AN4938 9.3 (p.38): "The following recommendations shall be followed: Place the decoupling capacitors as close as possible to the power and ground pins of the MCU. For BGA packages, it is recommended to place the decoupling capacitors on the other side of the PCB (see Figure 21)". Figure 21 (p.39) is captioned "on the same side of the package (all packages except BGA)". The STM32H743VI on board B is an LQFP-100 | Section 4's STM32 row and conclusion now say AN4938 allows the other side for BGA only. D5 excludes every part whose maker names the same side: the STM32H743 in a non-BGA package, and class R. AN4938 is no longer a far-side source; the RP2040 guide stays one for the parts it covers. T5 carries the flag and T9 has the fixture. The registry text's AN4938 note, decision 42's outcome and the record section are corrected too |

Minor items of the same reading, each fixed or answered here:
- **D12's own-side count.** It is ten of thirteen past the limit (5.40 to 32.1 mm; C62 at 5.40 mm was missed), not
  nine. C61 has no pad on its declared net on D12, because the round 4 generator renamed it (section 7).
- **The TPA6132A2 on D12.** C31 at 18.1 mm and C32 at 13.6 mm are past the maker's 5 mm. That is now stated in
  sections 1, 7, 9 and 10 and in G12, and D12 reads FAIL at U7 under this ruling once T2 lands.
- **R2's escape cost.** It is reported per part (T4). The TPS62933 still has RT, EN, SS and FB to escape.
- **Class A for the protection parts.** It is provisional and goes into the battery/protection qualified-review
  packet (A3, section 10).
- **DEC-001's per-device clause.** It is kept in the registry text and stays open on SI-001. `HEURISTIC_AS_LAW` is
  not retired while the 3.0 mm screen decides for classes D and L (T7).
- **The via allowance.** Its sensitivity to via pitch, track width and plane choice is given, and AN 574's 2.3 nH
  example is reconciled by its via-length rate: 0.98 and 0.82 nH against this model's 0.95 and 0.88 (5.2).
- **C28.** Read from PDi's driving circuit Rev. 02, it is the maker's C1 (4.7 µF / 6.3 V for G2) on the supply node.
  The maker gives no placement, so it stays B2; the TBD is closed.
- **D2's via reach.** The gate's reach test accepts any via or pour of the net and skips track-carried rails, so the
  ground pad's own via is a new check (T10).
- **B1.** The makers' "as close as possible to the voltage regulators" is now enforced as a declaration against the
  regulator, with the distance printed and the placers seating toward it.
- **G13.** The DVDD net needs a third part: 1 uF at VREG_VOUT plus 100 nF at each DVDD pin.
- **Decision 42's outcome.** It no longer says "below", which pointed at nothing on the rendered page.
- **The Diodes draft's "non-commercial prototype".** The wording is confirmed, not changed: it is the owner's
  ruling D-04 of 26 September (`CONOPS.md:395`, `PRODUCT-BRIEF.md:23`). The draft now cites D-04 and adds the
  CERN-OHL-S-2.0 licence (`README.md:71`). It is still not sent.
- **The merge note.** T8 now asks for `PCB-OPEN-PAIRS.md` to be re-rendered in the same commit.

### 12.3 Corrections of 26 September 17:15

A checker read the 16:42 version and found that part of item 4 (12.2) remained: the set of parts that get a fan.
It was checked against `escape.py`, `bypass_slots.py` and the committed board text here, and it was right.

| item | what the 16:42 page said | what the artefacts show | corrected in |
|---|---|---|---|
| 6 | D5 refused a far-side seat inside the fan box of "every part the escape pass fans", defined as `_needs_fan` counted on numbered copper pads (T1); it listed "WSON-6" among the small parts "the escape pass does not fan", counted C61 and C62 under D12's U15 among 9 open far-side seats, and said the rule "keeps what the tools do today". T1's evidence and fixture covered only the 1.27 mm SOIC-8-1EP | `escape.py:34-42` and `:176-177` escape every part at 0.7 mm or less, or with SOT-23-6/8 in its name, with no pad-count floor. Read on the committed boards (`drafts/dec_escset.out`), the parts escaped with fewer than eight copper pads are 14 on B21 (U82 and U83, MLPD-6 at 0.35 mm; U10, U21 and U22, WSON-6-1EP; nine SOT-23-6), 5 on C24 and 2 on D12 (U15, WSON-6-1EP; U5, SOT-23-6), with 1 on A32, 9 on E17 and 1 on P4 besides. D12 carries vias of U15's pin 3 net (/VGG_CT) and pin 6 net (/+5V_D8), 1.50 and 1.58 mm from those pins. Today's `_needs_fan` fans the four WSON-6-1EP through their two paste apertures (nine SMD pads); T1 as written cut them to seven and took their fan away on both sides, which weakened a protection that exists today with no evidence for it | T1 now fans every part the escape pass escapes (its selection moved into one function that `escape.py` and both placers call) together with every part of eight or more numbered copper pads at 1.0 mm or less, with fixtures for the WSON-6-1EP, the SOT-23-6, B21's MLPD-6 and D12's 0.8 mm TQFP. Against today it drops only the SOIC-8-1EP lands and adds 22 fans. D5 quotes the set, says what it keeps and changes against today, and counts 7 open far-side seats on D12 (C61 and C62 refused). T9's fixtures refuse a far-side seat under D12's U15 and under B21's U82. Also corrected: sections 1, 2, 3.1 (the ruled set: 83 fanned declarations, 3.26 to 5.49 mm), 3.2 (a) and a new (g), 3.3, 5.2, 6 (options), 7, 9 and 10, decision 42's authority_why and outcome, and the record section |

Found while correcting, and corrected with it:
- **D12's C17 sits inside U5's fan box.** U5 is a SOT-23-6 the escape pass escapes. So C17's present seat is
  inadmissible too, and of D12's eleven other-side capacitors only C53 is admissible now (section 7). The 16:42
  reading used the narrower set and called C17 clear.
- **`escape.py`'s own `is_fine` counts paste apertures,** the defect 3.2(a) names in `_needs_fan`. So E17's six
  TDSON-8-1 FETs, whose pins are at 1.27 mm, read 0.40 mm and are escaped (3.2(g)). Whether they should be is a
  question for `escape.py`. The fan follows whatever it selects, so the ruled set keeps their fans.
- **The fan boxes hold the escape vias.** Every nearest locked via of a signal pad's own net within 3.5 mm of an
  escaped part's pad lies inside that part's fan box: 1,087 of 1,087 on the six boards (`drafts/dec_escvias.out`).
- **The added boxes cost two declared own-side seats.** C24's C3 and C4 sit inside U11's fan box
  (`drafts/dec_newfans.out`). They are re-seated on C24's next placement (section 10), not moved for this ruling.
