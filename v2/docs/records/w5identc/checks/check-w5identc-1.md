<!-- Filed by stream w5identc (MESHSAT-1357, 29 September 2026) from the checker's report CHECK.md, sha256 8009c535473ae8ed; local paths scrubbed: none found. The text below is the checker's, unedited otherwise. -->

mergeable: no

# Check of stream w5identc (board C's part identities), MESHSAT-1357

AI review, labelled as such: an independent check by a Claude session that did not write the work. It is not a
qualified engineering review. 29 September 2026, 19:56 to 20:25 CEST (read from `date`).

Branch `fnd/w5identc`, tip `6b03ef6f` (confirmed with `git rev-parse`), five commits on main `b874b744`, all authored and
committed as the owner with no trailer, no dash characters added. Checked in this shared clone at the tip, and in a second
clone of `fnd/int15` at `1f3dd306` with the branch's files laid on it (the merge is clean: `git merge-tree` gives tree
`16665af7`; that clone was removed afterwards to free disk). The held Uniroyal sheet was fetched here with the stream's
`fetch_held_back.py` (467557 bytes, sha256 `11cd644d...` matched) and is identical to the worktree's copy.

## Blocking items

### B1. The check judges a DECODED binding against the table's own requirements, not the netlist's

`v2/ecad/tools/part_identities.py` line 1183: `read_binding(..., req=s["requirements"])` takes the requirements the table
states. Line 1175 compares only the key string; nothing compares the table's `requirements` with the requirements the
tool derives from the netlist (it has them: `rs` at line 1156). Mutant run here: in a copy of the table, C37's selection
(`1u 25V`, stated 25 V) got `v_rating_min: 6.3` and the identity `CC0603KRX7R5BB105` with its voltage field `5 = 6.3 V`,
key untouched. `part_identities.py check <mutant>`: `0 problems`, HOLDS. A 6.3 V capacitor is certified on a row the
schematic states at 25 V.
Fix: pass the requirements derived from the netlist for the selection's rows (and refuse a selection whose table
`requirements` differ from them, or whose rows disagree), with a test built on this mutant.

### B2. The DECODED predicate accepts part numbers outside the maker's scheme

`read_decoded` (lines 1032 to 1109) asserts that the codes concatenate to the part number and that each code is a token of
its row, but not WHERE in the scheme each field sits, and a `series`, `process` or `literal` field (line 959) passes on
token presence alone. Run here on the real pages (Yageo V.26 p. 2, Uniroyal V.3 p. 2), each read DECODED:
1. tolerance and packing swapped, `CC0603RKX7R9BB104`;
2. a padding literal `X` appended (the scheme row prints `X` placeholders), `CC0603KRX7R9BB104X`;
3. an extra `BB` after `CC`, `CCBB0603KRX7R9BB104`;
4. Uniroyal packaging and special swapped, `0603WAF1002E5T`;
5. a decode that establishes nothing: board C's MAIN PWR pushbutton selection (and the Y1 crystal) RESOLVED to the Yageo
   100 nF capacitor on the Yageo page, `established: []`. Put into a table copy with the counts adjusted, `check` reads
   `0 problems`, HOLDS.
The order mutant as a table edit also HOLDS. Decision 59's draft says the tool "decodes the part number field by field";
as written it accepts permutations and padding that are no part number of the maker's.
Fix: each field carries its position in the printed scheme (Yageo's `CC XXXX X X X7R X BB XXX` slots; Uniroyal's own "1st
to 4th", "5th to 6th", "7th", "8th to 11th", "12th", "13th", "14th" codes) and the tool aligns the fields to it in order,
with literal codes equal to the scheme's literal at that slot; refuse a DECODED binding that does not establish every
deciding property of a kind the rule knows (capacitor, resistor) and refuse other kinds; one test per mutant above.

### B3. On set 14, decision 59 makes a PASS record stale: `rules_lib.py requirements` reads 1 error

`fnd/int15` at `1f3dd306` reads CFL-016 `evidence_result: PASS`, bound to
`v2/ecad/tools/pcb_decisions.yaml@a41df5d12ff95995`. `rules_lib.py` line 1055 makes a stale binding an ERROR on a PASS
record (a warning otherwise, which is why main shows only a warning). Full checkout of int15 plus the branch: before
`apply_decision_decoded.py` 0 errors; after it `ERROR CFL-016: its reading is bound to ... a41df5d12ff95995 and the tree
holds 29d0437df0db483f`; `rules_render.py --requirements` then refuses to render; `test_requirements` and
`test_layout_entry_stages` read 6 failures. Rebinding CFL-016's line to `29d0437df0db483f` (a probe only) gives 0 errors,
the trace renders, and `test_requirements test_layout_entry_stages test_decision_register test_part_identities` read
99 passed, 0 failed, 3 skipped. The run order (README lines 120 to 125) does not name this.
Fix: README step 4 (or `apply_decision_decoded.py`) names every record whose `evidence_bound_to` cites
`pcb_decisions.yaml` (only CFL-016 on main and on int15) and has it re-read and rebound after the append, with the
reason decision 59 does not touch what CFL-016 judges.

### B4. The table's own rule D-2 and `what` still say RESOLVED means PRINTED

`v2/docs/records/w5identc/build_table.py` lines 200 to 213 (committed at `pcb_part_identities.yaml` line 180): "A series
sheet that prints an ordering scheme and not the part number does not name the part: the selection is UNRESOLVED
(DOCUMENT_DOES_NOT_NAME_THE_PART)", and its `reversal`: accepting a decoded scheme "is a change of this rule, taken by the
integrator, not a reading of it". `what` (builder lines 336 to 341, table line 3) says every RESOLVED selection has a
document "whose cited page prints that part number". 23 selections of the same file are DECODED on series sheets.
Fix: rewrite D-2 and `what` with the PRINTED and DECODED bindings, citing decision 59 and its limit, and re-run the builder.

### B5. Four carried UNRESOLVED reasons are not true against the tree

The builder re-read only RESOLVED identities; UNRESOLVED reasons came over from w5ident verbatim.
1. J_EPD (`S-13d7058c0e`, table line 951), DOCUMENT_OWED "no document held in this tree prints the part number", next
   action "file Hirose's document"; README line 131 "Hirose's FH34SRJ page (403)" among documents not obtained. The tree
   holds Hirose's own FH34 catalogue, `v2/vendor/hirose/hirose-fh34-series-ffc-connectors.pdf` (author "Hirose Electric"):
   page 6 prints `FH34SRJ-24S-0.5SH(##)` with the key `(##) : (50)`, page 5 decodes "(50): Standard (5,000pcs)". It is
   resolvable from a maker's document already in the tree (PRINTED on the base number with the packing code, or DECODED).
2. BZ1 (`S-a5c3762a4c`, line 213): "the value names no part number"; the value is "(Floyd Bell MC-09-530-Q class)"
   (`gen_sch_c.py` line 390, `jlc-handfit.txt` line 76), and Floyd Bell's own sheet for it is held,
   `v2/vendor/seals/floydbell-mc-09-530-q-spec.pdf` (prints MC-09-530-Q: panel mount, continuous, 5 to 30 V DC, IP68,
   quick connect blades). Next action "read the order code in Floyd Bell's own catalogue and file the page" names a page
   the tree has. CHOICE_OWED can stand (the value asks two flying leads, the sheet gives blades) but on true facts.
3. C31 (`S-62ab53c6e1`, line 2985): chosen_by "the incumbent (generator) meets every requirement"; the selection needs
   X7R (rule C-D3) and GRM188R61E475KE11D is X5R by `gen_sch_c.py` line 365's own words. The next action (file a Murata
   document that prints it) would RESOLVE an X5R part on an X7R selection, and a PRINTED binding does not compare the
   dielectric. State the mismatch, or record rule C-D3b and its open hot-spot question.
4. README line 25 defines DOCUMENT_OWED as "no maker's document in the tree prints or decodes it". The makers' series
   sheets with ordering schemes are held for SW_MAIN (`v2/vendor/switches/ck-atp19-series-datasheet.pdf`: its "ATP19 - x -
   xx - x - xx - xx - x - x - xx - x" categories account for every field of ATP19-SL1-603-B0SA-03G as I read the text
   layer; box order not confirmed from the drawing), SW_PI and SW_TEST (C&K ATP16 sheet) and SW_LIGHT (NKK M series
   sheet, prints M2044). Decoding them was never tried, so "or decodes" is not established.
Fix: re-read the carried UNRESOLVED reasons against the tree; correct these four in DECISIONS; name the held series
sheets in the switches' reasons and next actions; correct README line 131.

## Minors

1. README line 24: "15 panel lamps"; there are 17 lamp selections (D1 to D16, D22), and 22 CHOICE_OWED adds up only with 17.
2. Decision 59's title doubles its marker: "a DECODED binding (DECODED binding (stream w5identc))" (`apply_decision_decoded.py`
   lines 23 and 24); it is rendered into OWNER-DECISIONS-OPEN.md.
3. Decision 59's `authority_why` omits the residual risk half of the two part test. It is still the session's: no class
   of `reserved.json` (all nine read) names the identity files, no money, no claim, and the range table risk is
   removable by a measurement in this tree. I read Yageo's X7R range tables (pp. 5 and 6 of the filed sheet): 0603 50 V
   100 nF, 0603 25 V 1 uF, 0603 16 V 1 uF and 0805 16 V 10 uF are all listed. Say so in `authority_why`.
4. Decision 59's `ask` states Yageo and Uniroyal "do not publish" a document printing these part numbers; nothing in the
   stream reads that. Its `outcome` says "each code is in its cited row"; the value code is not asserted in its row
   (only the rule words, line 1060 onward).
5. `apply_decision_decoded.py` docstring: "asserts the file ends where it did when drafted (the last decision's final
   line)"; the code asserts only that the highest number is last and that its entry line exists.
6. The open item's disposition LAYOUT_STAGE: its two uses on main mean "applied when the layout is drawn"; EXECUTION-PLAN
   line 72 makes exact part identities a precondition of "that board's layout entry". As drafted it does not hold board
   C's layout entry in `rules_status`. The script's own alternative (stage it on board C's feasibility record at
   LAYOUT_ENTRY) is the truer binding.
7. Yageo's `sources.txt` line says its text layer "carries no reproduction, rights or permission wording". Page 29 (LEGAL
   DISCLAIMER) reads "YAGEO reserves all the rights for revising this content without further notification". That is about
   revision; no copyright notice, no reproduction or redistribution term anywhere in the text layer, and no distributor
   name. The terms are silent, and filing follows the tree's a1solar precedent ("the maker's own public specification
   sheet, no terms stated on it"). Reword the line and cite that precedent.
8. `check --unfetched-ok` writes verdict HOLDS with 13 bindings UNREAD and no field recording the flag.
9. C1 and C2 (`S-6d1de2f8e8`, table line 2093): the identity is Yageo CC0805KKX7R7BB106 (order code C326595, rule I-1),
   but `gen_sch_c.py` line 124 draws both with C15850, which the tree's catalogue reading
   (`v2/docs/parts/readings/lcsc-2026-09-27.json`) names Samsung CL21A106KAYNNNE, X5R. The table does not record that
   the design orders another part than its identity.
10. Six order codes of RESOLVED selections (C485080, C326595, C106858, C106248, C25190, C23138) are not in this tree's
    catalogue reading; their code to part number mapping rests on w5ident's reading, which was not brought over (R52's
    DECISIONS reason cites it).
11. The five DOCUMENT_DOES_NOT_NAME_THE_PART next actions ask for "a part specification, not a series sheet"; the README
    (line 26) gives the DECODED route first. Table and README disagree.
12. Rule D-2 says nothing on packing suffixes: SS2040FL is PRINTED as a column header of PANJIT's series page (the
    orderable reel code is not in the part number), while J_EPD's part number carries Hirose's packing code (50) and is
    refused.

## Observations outside this stream

* `v2/vendor/power/panjit-ss2020fl-series.pdf` (on main since `ccf5808e`, 26 September) reads "Reproducing and modifying
  information of the document is prohibited without permission from Panjit International Inc."; under the owner's rule
  of 27 September it would be held back. A separate item, not this merge.
* Rendering OWNER-DECISIONS-OPEN.md off the box on int15 changed "338" to "339" rule board pairs (the scratch tree has no
  assembly_set or final_gate; `test_decision_register` skips for the same reason). Not the stream's.

## Answers to the seven questions

1. HOLDS with 0 problems reproduced: 175 rows, 87 selections, 0 uncovered, READ 20, DECODED 23; the reading is byte
   identical (sha256 `3d3775e2...`), table `febe247b...`, tool `60b3f6db...`; `build_table.py` rewrites the table byte
   identical; `render` rewrites BOARD-C-SELECTIONS.md identical; on the int15 merge state the same reading, byte identical.
   Without the held sheet: 13 UNREAD, 13 problems, as claimed. By hand, text layer: all 13 PRINTED documents (20
   selections) print their part numbers on the cited pages (Diodes BAT46W p. 1, PANJIT p. 1, JSCJ p. 1, AOS p. 1, Vishay
   Si2300DS p. 1, VEML7700 p. 1, Diodes 74LVC1G17 p. 9, TI PCA9555 p. 31, RP2040 p. 2, TI SN74LVC1G57 p. 14, TI TLV755P
   p. 28, ST USBLC6 p. 1, Winbond p. 73), and all 23 DECODED selections decode on the pages I read, with my own decoder,
   meeting value, package, tolerance, voltage and dielectric (Yageo, 10) or value, package, tolerance and power (Uniroyal,
   13), R14 (0603WAF2201T5E, 2.2 kOhm 1 percent), R50 (0603WAF1002T5E, 10 kOhm 1 percent), R52 (0603WAF3300T5E, 330 Ohm
   1 percent) and R53 to R56 (in the 27R selection with R2 and R3, 0603WAF270JT5E, 27 Ohm 1 percent) among them.
2. Resolvable from a document in the tree: J_EPD (Hirose FH34 catalogue). Reasons not true: J_EPD, BZ1, C31, the
   switches' "or decodes" (B5). No CHOICE_OWED row carries an order code or a maker's part number in the netlist; BZ1's
   value names Floyd Bell MC-09-530-Q as a class and its sheet is held; C28 is drawn as "4.7u" 0805 with no code, the
   lamps as hand fitted parts with no number, the jacks as a class with the drawing owed, H1 to H8 as a generic M3 x 6.
3. The four requested mutant classes are refused (a tolerance code mapped to the wrong meaning, a 16 V code on a 25 V
   selection, a wrong value and a wrong size, page 3 and page 1 cited, a distributor publisher, both sheets bound as
   PRINTED, a wrong sha256, another maker, a 5 percent code on a 1 percent selection, a missing field, an unknown kind).
   Not refused: B1 and B2. The 21 tests pass; V-1 (a') and (g) each fail their test when removed (mutation run here), and
   (g) moves 21 board C nets to UNBOUNDED with 0 keys changed, as claimed.
4. Decision 59 is truly the session's under the two part test (minor 3); the draft overstates the decode (B2) and its
   title, `ask` and `authority_why` need the fixes in minors 2 to 4. The stated limit is there.
5. Main: decision 59 at n 59, open item S-124, second runs refused, `rules_lib.py requirements` 0 errors (1 warning,
   CFL-016), `validate` 0 errors, test_requirements and test_layout_entry_stages 75 passed after `rules_render.py
   --requirements`, test_decision_register 3 passed 2 skipped after `decisions_render.py`. int15: n 59, S-125, second runs
   refused, `requirements` 1 error (B3).
6. Uniroyal: page 9 reads "Uniroyal Electronics Global Co., Ltd. , all rights reserved", no grant; `.gitignore` line 51
   ignores `v2/vendor/passives/held/`; the `sources.txt` line (URL, bytes, sha256) matches my fetch; no held file tracked
   (`git ls-files v2/vendor/passives` lists only the Yageo sheet). Yageo: terms silent (minor 7); neither sheet prints a
   distributor's name anywhere in its text layer.
7. The file `v2/release/handover/_generated/pcb-c-display-c8/NOT_FOR_FAB-pcb-c-display-bom-per-reference.csv`, tracked,
   sha256 `e9e7e0a8...`, 167 rows, one commit `6dc4e708` (27 September, H2 exports at `99cde56b`, provenance commit
   `99cde56b`, netlist `11eabc2d...`), written by `handover_exports.py exports` (lines 136 to 138). The netlist is
   `11eabc2d...` at `99cde56b`, `6dc4e708` and `e28f91a6^`, and differs from `e28f91a6` (27 September 19:57 CEST) on; at
   `b874b744` eight parts are missing and R14's value and code differ. Only `part_identities.py` (compares) and
   `handover_exports.py` read it. It is a dated handover snapshot that names its own commit: no item; regenerate at the
   next handover (REGENERATE.md section 5). README step 6's "open the stale BOM export item" should say so.

## Counts

Blocking 5, minors 12, observations 2. Bindings read by hand: 43 of 43 (20 PRINTED, 23 DECODED). Mutants: 19 refused as
required; 5 predicate probes and 3 table edits accepted (B1, B2). Tests run: test_part_identities 21/0; lint modules as
named 6, 3, 6, 6, 5, 78, 2 passed; test_agent_contract 48, test_verdict_channel 44, test_stale_readings 7,
test_swallowed_code 3, test_swallowed_calls 3, test_kb_isolation 3, test_shell_parses 1 passed. The box suite was not run.
