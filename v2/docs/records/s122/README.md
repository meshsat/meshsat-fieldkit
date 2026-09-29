# Stream s122: the documents CFL-016 names, re-read whole against set 12's netlists (S-122, MESHSAT-1357)

Prototype design: nothing here is built, bought or measured. Base `main` at `e57a7365` (set 12 promoted), branch
`fnd/s122`, 29 September 2026. The stream changes documents only; no generator, netlist or registry file is edited on
this branch (the registry changes are `apply_registry_s122.py` and `close_s122.py`, for the integrator).

## Why

CFL-016 reads FAIL on set 12 and waits on S-122. Three rounds of set 12 failed on the same defect: a registry entry
said a document had been read when no script had read it and no filed check said so. This stream does not patch the
named lines. It parses every document CFL-016 names, lists every sentence that names a part, a net, a board, a rail,
a gate function or a generator line, judges each one against the committed netlists and the generators with a script
that evaluates every assertion it makes, and corrects each STALE sentence with a script that asserts every part its
new text names before it writes. Every statement below about what was read is what one of these scripts read, or a
filed check's own words, quoted with its file.

## Files

| File | What it is |
|---|---|
| `s122lib.py` | the parser (headings, table cells, list items, paragraphs, sentences), the name finder and `SCOPE`; reads the six netlists with `tx_inhibit.parse_netlist`; `S122_AT=<commit>` makes it read the documents at a commit |
| `inventory.py` | step 1: writes `inventory.out` (every inventoried sentence with its id, digest and names, and the count per document) |
| `judgements.py` | the stream's judgement of each sentence, keyed by its digest, with the assertions that back it |
| `verdicts.py` | step 2: for every sentence it looks up every named part on the netlists, reads every cited generator line (at the commit the sentence dates it to, or at this commit), evaluates the judgement's assertions, and writes `verdicts.out` |
| `inventory-base.out`, `verdicts-base.out` | the same at the base `e57a7365` (run with `S122_AT=e57a7365`): 599 sentences, 34 STALE |
| `inventory.out`, `verdicts.out` | after the corrections: 605 sentences, 0 STALE, 0 UNJUDGED |
| `apply_docs_s122.py` | step 3: the 43 corrected passages, run on this branch (commit `cb446b03`); refuses a second run |
| `apply_registry_s122.py` | step 4, for the integrator: rebinds, CFL-016's entries, S-122's title correction, the envelope re-pin |
| `close_s122.py` | S-122's closure, for the integrator, last |
| `LOG.md` | the stream's log |

## Scope (`s122lib.SCOPE`)

Taken from CFL-016's statement and notes and the brief: PANEL.md sections 1, 2, 3, 5, 6, 7, 9 and 10; CONOPS.md
sections 2a, M2, M4, 4 (the Startup, Charging, EMCON, ZEROIZE and Service rows), 4a (the PS-EMCON row), 4b, 4b.1, 4e,
4f and 5; V2-SPEC.md whole; OPERATING-ENVELOPE.md sections 2 to 4; TEST-PLAN.md whole; ASSEMBLY.md section 4, build
steps 1 and 6 (section 2), and sections 8 and 9; decisions 28 and 40 of `pcb_decisions.yaml` (their outcome and
reversed_by fields). Not read by the scripts: PANEL.md's head and sections 4, 8 and 11; the other CONOPS.md sections
(among them 4c and 7a); OPERATING-ENVELOPE.md sections 1 and 5 to 8; the rest of ASSEMBLY.md.

The finder is a token parser: a sentence is inventoried when it names a part designator, a net of any netlist, a
board (A22, B16, board B, "as generated" and the like), a rail (a rail net or the word rail), a gate function (AND,
buffer, open drain, pull-up, load switch, back-feed and the like) or a generator line. A sentence that names a part
only by its role is outside the inventory: V2-SPEC.md line 35 ("a holdover RTC on the panel controller") was found by
reading, not by the finder, and was corrected with the rest.

## What the verdicts mean

* **TRUE**: the stream judged the sentence true on reading it against the netlists, and every check `verdicts.py`
  runs on it holds: every named part is on a netlisted board, every cited generator line holds a part or net the
  sentence names (at the commit it is dated to), and every assertion of its judgement holds (2115 assertions after the
  corrections, 1832 at the base). What a TRUE sentence says beyond the netlists (a firmware rule, a maker's figure, a procedure) is
  named in the judgement's text and not judged. For the connector rows of ASSEMBLY.md section 4 the check is that the
  part exists on the board named; the connector's type is its footprint and is not asserted.
* **STALE**: the sentence describes a circuit, a line number or a state the netlists or generators no longer carry;
  each has its correction in `apply_docs_s122.py`.
* **NOT DERIVABLE**: the claim rests on something that is not a netlist: HISTORY (a dated record of an earlier
  reading, such as V2-SPEC.md's numbered corrections and its boards table headed "as generated on 7 September 2026"),
  FIRMWARE (the firmware contract or a procedure), HELD DOCUMENT (a maker's figure, an analysis, a ruling), TEST (a test
  procedure or pass line), CASE (a mechanical item) or LEAD (how a lead is made). Left as it stands.
* **UNJUDGED**: no judgement for that text; the closure refuses on any.

## Counts per document

| Document | Base: sentences | Base: STALE | After: sentences | TRUE | STALE | NOT DERIVABLE |
|---|---|---|---|---|---|---|
| PANEL.md | 150 | 8 | 151 | 123 | 0 | 28 |
| CONOPS.md | 98 | 8 | 98 | 39 | 0 | 59 |
| V2-SPEC.md | 93 | 3 | 98 | 28 | 0 | 70 |
| OPERATING-ENVELOPE.md | 27 | 4 | 27 | 8 | 0 | 19 |
| TEST-PLAN.md | 97 | 2 | 97 | 17 | 0 | 80 |
| ASSEMBLY.md | 125 | 9 | 125 | 75 | 0 | 50 |
| pcb_decisions.yaml (28, 40) | 9 | 0 | 9 | 6 | 0 | 3 |
| total | 599 | 34 | 605 | 296 | 0 | 309 |

## What was STALE, and the correction (43 passages)

* **PANEL.md**: line 63 (an undated citation `gen_sch_c.py:157-166`, now dated at `45bde541`; R52 and D23 of set 12
  added); line 98 (GPIO 20 pointed at section 9; it is section 10); line 155 (board A's round 8 called a candidate, the
  citation `gen_sch_a.py:1240-1243`, U36 and U38 left out); line 156, source cell (the candidate framing; R52 and D23);
  line 156, effect cell (board A at `45bde541` with U26 and a candidate, now U35 to U38 at `gen_sch_a.py:1572-1575`; the
  RockBLOCK clause without set 12's R532, U543 and RB_GO gates; "Open: the back-feed ...", which set 12 draws); line
  166 (U6's RockBLOCK ENABLE and P_EN requests left out); line 180 (the bus table's provenance named `45bde541` only;
  the re-read at set 12 is added, and `verdicts.py` asserts every device of the table on its board's SDA net).
* **CONOPS.md**: section 4's Startup, Charging and Service rows (undated generator citations that now point at other
  code; each is dated at `45bde541`, where the script asserts they held the parts, and the circuit they describe is
  asserted on the netlists); section 4b's preamble (it said every gate, supply and net was asserted by
  `apply_conops_4b_set12.py`; the check-int13-3 count, 146 pins of 55 parts, and this stream's assertions of the rest
  now); section 4e's device-rail row (both converters put on board A: `+3V3_DEV` is board B's `U25`, and was at
  `45bde541` too), the next row (`U{s}11` and an open L3: each slot makes `EMCON_ON` from its own 3.3 V since round 8,
  and `U543` holds the RockBLOCK's ENABLE), the fan row's undated citation, and the section's header; section 4f
  (HOT-R1 "owed" on boards A and E, drawn since stream w4ae).
* **V2-SPEC.md**: line 73 (all five fans driven by the sensor controller; the cooler fans are on their modules'
  Fan_PWM); line 76 (the RockBLOCK's ENABLE listed as owed, drawn since w4b); correction 29 (both device-rail
  converters on board A); line 35 (found by reading, above); correction 32 records these.
* **OPERATING-ENVELOPE.md**: section 4's HOT-R1 sentence; the USB-C row's undated citation; the EMCON mode ("gates
  every transmitter rail": the SA868's supply and the modules' radios are not rail-gated); the RockBLOCK item. No number
  changed.
* **TEST-PLAN.md**: E3-H and P15 treated HOT-R1 as absent from the generated boards.
* **ASSEMBLY.md**: section 4's undated citations (dated at `45bde541`, or re-pointed to the base where the old lines
  held nothing); the dock contacts (`VIN_RAW` on pins 1 to 4 and pin 12 a spare, where EQ-16 moved `VIN_RAW` to
  `J_VR1` to `J_VR4` and w4ae put HOT-R1 on pin 12); section 8 step 3 (`PA_EN = EMCON_HW AND PA_SW_EN`, now
  `TX_INHIBIT_n` AND `EMCON_HW` AND `PA_HOLD` in U35 and U36).

`apply_docs_s122.py` asserts 398 part, pin, net, value and generator-line facts before it writes, checks each old
passage is found once and each new one reads back once, carries no dash, re-parses each document and refuses when the
diff touches a line outside the corrected passages.

## The scripts for the integrator, and what they assert

* `apply_registry_s122.py`: (1) rebinds the 13 records bound to the six changed documents (CFL-001, CFL-005, CFL-007,
  CFL-008, CFL-009, CFL-010, CFL-013, CFL-014, CFL-015, CFL-016, CON-018, REQ-005, REQ-050), each with an entry whose
  reason it reads from the diff (the changed lines and their sections, and how many of the removed and added sentences
  the two verdict files hold STALE, TRUE, NOT DERIVABLE or outside the inventory) and from the record's own evidence
  text (which of the sections it names are among the changed ones); it moves CONOPS.md's needs pin after asserting the
  diff starts after the needs table; (2) appends to CFL-016 the entry naming the inventory and verdict files with the
  counts it reads from them; (3) corrects check-int13-4's minors: n1 and n2 by an entry on CFL-016, n3 and n4 by a
  sentence appended to S-122's title; (4) re-pins `pcb_envelope.yaml` and ENV-001's `verified_sha` to the new
  OPERATING-ENVELOPE.md after asserting that no number of the envelope left the document. Every other record and item
  is asserted unchanged; the files re-parse; it refuses a second run. Replayed on a scratch clone of this branch:
  `rules_lib.py requirements` 144 records, 0 errors, 0 warnings; `test_envelope_data` 6 passed; `test_requirements`
  65 passed, 0 failed, after `rules_render.py --requirements` (before the render, the two trace-page tests fail, as
  expected).
* `close_s122.py <check>`: refuses unless the rebinds are in and current, its own re-run of the inventory and the
  verdicts reads 0 STALE and 0 UNJUDGED and equals the committed `inventory.out` and `verdicts.out`, and the named check
  is committed, starts `mergeable: yes` and names every document and `verdicts.out`. Then it closes S-122, sets
  CFL-016 to PASS and drops its waits_on. Replayed on the scratch clone with a fixture check (not filed): it closed
  S-122 and refused a second run; `rules_lib.py requirements` 0 errors and `test_requirements` 65 passed after the
  render.

## Integrator's run order

1. Merge `fnd/s122`.
2. `python3 v2/docs/records/s122/apply_registry_s122.py`
3. `rules_render.py --requirements`; then the evidence pages the envelope pin touches (`rules_status.py`,
   `rules_render.py`: ENV-001 reads the new `verified_sha`; the PCB-RULE-STATUS pages and LAYER-STATUS carry the
   document's sha).
4. An independent check of the corrected documents, filed under `v2/docs/records/s122/checks/`, stating in its own
   words which documents and lines it read.
5. `python3 v2/docs/records/s122/close_s122.py v2/docs/records/s122/checks/<the check>`
6. `rules_render.py --requirements` again.

If any of the six documents changes on main before step 2, `apply_registry_s122.py` still rebinds from the base shas
it names and refuses if they are not the ones bound; the inventory and the verdicts must then be re-run and any new
text judged (`judgements.py`) before step 5, or the closure refuses.

## Seen outside the scope, not corrected

* CONOPS.md section 4c (about line 740) still says the design acts "once HOT-R1 is in the generators of boards A and
  E (the requirement reads FAIL on the generated boards until then)", and the head (about line 27) asks whether the
  generators of boards A and E carry HOT-R1: both are the sentence corrected in OPERATING-ENVELOPE.md section 4.
* V2-SPEC.md's boards table is headed "as generated on 7 September 2026" and was judged HISTORY; its A22 row names the
  TPS55288 that OPERATING-ENVELOPE.md says left the design on 7 September, and its B16 row the STM32H753 where U41's
  value text now reads STM32H743VIT6.
