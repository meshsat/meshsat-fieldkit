<!-- Filed by stream w5identc (MESHSAT-1357, 29 September 2026) from the checker's report CHECK-2.md, sha256 a14469859502590d; local paths scrubbed: 1 reference to the first report's scratch path replaced by its filed path. The text below is the checker's, unedited otherwise. -->

mergeable: no

# Second check of stream w5identc (board C's part identities), MESHSAT-1357

AI review, labelled as such: an independent check by a Claude session that did not write the work. It is not a
qualified engineering review. 29 September 2026, 20:45 to 21:05 CEST (read from `date`).

Branch `fnd/w5identc` at `633697a7` (confirmed), three commits on `6b03ef6f`, all authored and committed as the owner,
no trailer, no dash characters added, no held file tracked (`git ls-tree` lists only the Yageo sheet under
`v2/vendor/passives`). Checked in this shared clone at the tip, and in a sparse clone of `fnd/int15` at `1bafab8c` with the
branch merged (clean, tree `761922aa`; the clone was removed afterwards, the disk is at 99 percent). The held Uniroyal
sheet is the one fetched in the first check with `fetch_held_back.py` (sha256 `11cd644d...`).

## Blocking items

### BB1. A DECODED code need not be a code of its row

`read_decoded` still maps a code to its meaning with the round 1 pattern (`part_identities.py`, the `MEANING_KINDS`
branch of the position loop): `code`, an OPTIONAL `=` or `:`, then `means`, anywhere in the row. The code only has to be
a token of the row, so a unit letter or an abbreviation can stand as a code and swallow the next entry. On the makers'
own pages, read here:
1. Yageo, voltage code `V` with row `5 = 6.3 V 0 = 100 V` and means `0 = 100 V`: `CC0603KRX7RVBB104` reads DECODED at
   100 V; on C37's selection (`CC0603KRX7RVBB105`, needs 25 V) also DECODED. Yageo's voltage codes are 5, 6, 7, 8, 9, 0,
   A and Y; V is not one.
2. Uniroyal, tolerance code `E` with means `.g.: D=±0.5%` (the row begins "E.g.:"): `0603WAE1002T5E` reads DECODED at
   0.5 percent. Uniroyal's tolerance codes are D, F, G and J.
As table edits (100n selection and R50) both give `0 problems`, HOLDS. Decision 59's outcome says the tool "reads each
code ... in a row of its own part of the page that maps it to the meaning claimed" and refuses part numbers outside the
scheme; these two are outside it.
Fix: parse each position's rows into their `code = meaning` entries (separator required, the meaning running to the next
entry), require the field's code to be one of those entry codes and its meaning that entry's; a test for each probe above.

### BB2. J_PIJ2 is NOT_A_PART though the tree names its wire

`build_table.py` (`reread`, the `LeadLands_1x02` branch) keeps J_PIJ2 NOT_A_PART because "the netlist's value names no
wire, plug or housing". `v2/docs/ASSEMBLY.md` line 127, section 4 "Leads": "| PI button | SW_PI's contacts | C7 `J_PIJ2`
lands (the panel controller reads it; nothing leaves the backer) | 24 AWG | soldered, beaded |". The table's rule N-1:
"What is bought is never NOT_A_PART: a wire soldered in ... UNRESOLVED until named". J_MAINSW, the same kind of row, was
moved to UNRESOLVED; its reason says the wire is not named, while ASSEMBLY.md line 126 gives "24 AWG twisted" and "XH2.5
at the A22 end". As it stands the open item's closing condition never asks for this wire.
Fix: J_PIJ2 to UNRESOLVED CHOICE_OWED on ASSEMBLY.md line 127 (gauge named; insulation, length, maker not), J_MAINSW's
reason citing line 126; counts become UNRESOLVED 41, NOT_A_PART 2; re-pin the reading.

## Minors

1. PRINTED is identity only: nothing in `check` compares a PRINTED part with the selection's derived kind or
   requirements. Table edits here: C28 (4.7 uF X7R 0805) RESOLVED PRINTED as PCA9555PWR on TI p. 31, HOLDS; J_EPD
   (24 way) RESOLVED as `FH34SRJ-26S-0.5SH(50)` on Hirose p. 6, HOLDS. No PRINTED selection on board C is wrong today
   (every one's value names its part), but README's B1 row "judges every binding on the derived ones" is true of DECODED
   only. Say so, or require a PRINTED part number (less its packing code) to be named in the selection's value or order
   code reading.
2. The stated limit bites on board C: `CC0603KRX7R8BB475` decodes against C31's selection and a table giving it HOLDS,
   while Yageo's range table (p. 5) lists 4.7 uF 0603 X7R at 6.3 V only. The tree holds both makers' range tables
   (Yageo pp. 4 to 9; Uniroyal, held, p. 4: 0603 1/10 W 1 percent 0.01 Ohm to 10 MOhm, which covers all 13 values);
   `authority_why` names only Yageo's. Add the range table row to a DECODED binding before one lands on C31 or C28.
3. `scan_vendor.py` does not replay byte for byte: the committed reading carries an empty `FH34SRJ-24S-0.5SH(50)` taken
   while J_EPD was UNRESOLVED; a re-run writes 22 part numbers. The builder reads the committed scan (the table rebuilds
   identically with either), and the scan is not in the run order, so the DOCUMENT_OWED facts are as fresh as that file.
4. Decision 59's `evidence` cites `v2/docs/records/w5identc/checks/check-w5identc-1.md`, which is outside the repository.
5. A size code may be cited on the metric column's row (`0201 (0603)` for 0603 reads DECODED); the package still decodes
   right, so harmless, but the row check is weaker than it reads.

## Answers to the six questions

1. B1. I derived by hand, from the netlist nets, the intent and the value text under the table's rules: C37 (1 uF 0603,
   X7R by C-D3, stated 25 V not checked on EPD_VCOM which the intent declares with no maximum, 10 percent); C31 (4.7 uF
   0603 X7R, stated 25 V not checked on EPD_PUMP and EPD_SW, 10 percent); C1 and C2 (10 uF 0805 X7R, 6.3 V from +5 V and
   +3V3 at the margin, 20 percent); C28 (4.7 uF 0805 X7R, 6.3 V from EPD_VCC 3.3 V, 10 percent); C5 and C6 (15 pF 0402
   C0G stated, 6.3 V, 5 percent); C44 (100 nF on C_DVDD 1.3 V, one selection with the +3V3 ones at 6.3 V); R14 (2.2 k 1
   percent, 0.1 W, bound 3.33 V); R50 (10 k 1 percent, 3.333 V to ground, power checked); R52 (330 R 1 percent, 3.33 V);
   R53 to R56 with R2 and R3 (27 R 0603, 5 percent, 0.1 W, working voltage unbounded through the connectors, rule (g));
   R43 (0.47 R, current sense, 200 ppm, 0.1 W underived). All equal the table's and the check's derived requirements.
   Table edits refused: C37 lowered to 6.3 V, R50 widened to 5 percent with a J part, a kind edited, a requirement raised.
2. B2. Refused on the makers' pages: every round 1 probe (tolerance and packing swapped three ways, padding, an extra BB,
   Uniroyal packaging and special swapped three ways, power and tolerance swapped), a pushbutton and a crystal, a Yageo
   part on a resistor, a Uniroyal part on a capacitor and on the R43 shunt, an X7R part on the C0G selection, a wrong
   literal (BN, X5R), a scheme named for another document or page, an unknown scheme, rows cited from another position.
   A scheme written into the table is ignored (true part still DECODED, table still HOLDS). Accepted: BB1's two.
3. B3 on `1bafab8c` plus the branch: before, `rules_lib.py requirements` 0 errors 0 warnings; `apply_decision_decoded.py`
   wrote decision 59 and rebound CFL-016 `a41df5d12ff95995` to `c8c51927de7e345b` (evidence entry names decisions 28 and
   40 identical); second runs of it and of the rebind script refused; after it 0 errors 0 warnings; `apply_identities_c.py`
   opened S-125 and refused a second run; `validate` 0 errors; both renderers wrote; test_requirements,
   test_layout_entry_stages, test_decision_register, test_part_identities 102 passed, 0 failed, 3 skipped. The check
   reading on that tree is byte identical to the committed one.
4. B5 against the tree, by hand: J_EPD (Hirose FH34 catalogue p. 6 prints `FH34SRJ-24S-0.5SH(##)` and `(##) : (50)`,
   p. 5 "(50): Standard", Hirose Electric's own catalogue: resolution true); C31 (gen_sch_c.py line 365 X5R against C-D3's
   X7R: true); BZ1 (Floyd Bell sheet p. 1 prints MC-09-530-Q and Quick Connect Blades; value asks two flying leads: true);
   D17 (netlist code C7502705, no PDF prints BAT54W: true); J_PANEL (no code in the netlist, no PDF prints BH254VS-26P:
   true); the lamps (ASSEMBLY.md line 58, 17 Mentor 1282.5004 guides: true); SW_MAIN (ATP19 scheme on p. 2), SW_PI and
   SW_TEST (ATP16 "To order" on p. 1), SW_LIGHT (NKK "ORDERING EXAMPLE" on p. 4): true; Y1 (RP2040 datasheet pp. 217 and
   218, hardware design p. 11, not Abracon's: true); L1 (Arlitech p. 4 prints `ATNR4010100□T`: true); Fenghua (p. 4 "How
   To Order": true); R43 (CS03 part number page names CS03, 0603 given on p. 3: true as worded); J_PIJ2: not true (BB2).
5. C1 and C2: `C326595` is YAGEO CC0805KKX7R7BB106, 10 uF, plus or minus 10 percent, 16 V, X7R, 0805, in w5ident's JLCPCB
   and LCSC readings of 27 September (fnd/w5ident `c08f4d5a`, `identities-2026-09-27.json` lines 9600 and 15172), not in
   this tree's reading, as the README says. It meets the selection (10 uF, 0805, X7R, at least 6.3 V, at most 20 percent),
   its part number decodes to the same on Yageo p. 2, and Yageo's range table p. 6 lists 0805 X7R 16 V 10 uF. The draft
   runs in check mode and writes nothing. Not judged by the table: it replaces a 25 V part with a 16 V one on +5 V, so DC
   bias loss is larger; decide that at regeneration.
6. Replay: the check reading (`602b2c24...`), the table (`2dce2a39...`), `builder-document-reads.json` and
   BOARD-C-SELECTIONS.md reproduce byte for byte with the Uniroyal sheet present; without it 13 UNREAD, `--unfetched-ok`
   writes HOLDS_WITH_UNREAD with `unfetched_ok: true`, which `apply_identities_c.py` refuses (it asserts HOLDS and the
   pinned sha256). Tests 24 of 24 (23 and 1 skipped without the sheet); twelve lint and sweep modules pass.

## What is answered from the first check

B1, B3 and B4 hold. B2 holds for order, padding, literals, positions, kinds and the table's own schemes, not for the code
to meaning map (BB1). B5 holds for every reason I sampled but J_PIJ2 (BB2). Minors 1 to 12 of the first check: answered
(17 lamps, the title, the residual risk half of `authority_why`, the docstring, LAYOUT_ENTRY_PACKET with an honest why,
the Yageo `sources.txt` line quoting p. 29, the unfetched verdict, C1 and C2 recorded with `netlist_agrees: false`, the
seven codes outside this tree's reading, next actions, packing placeholders).

## Counts

Blocking 2, minors 5. Probes on the makers' pages: 27 of 27 as expected in the first set; in the second set, 2 accepted
that must be refused (BB1), 4 valid decodes accepted, 1 refused. Table edits through `check`: 7 refused as they should be,
1 scheme edit ignored as it should be, 5 held (2 are BB1, 2 are minor 1, 1 is minor 2). Selections derived by hand: 11
(C37, C31 and R53 to R56 among them). Reasons checked by hand: 15. The box suite was
not run.
