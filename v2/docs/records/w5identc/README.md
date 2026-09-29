# Stream w5identc: board C's part identities (layer 6's exact-part requirement)

MESHSAT-1357, branch `fnd/w5identc` from main `b874b744` (set 13), 29 September 2026, two rounds. Prototype work:
nothing is built, bought or deployed, and nothing here orders anything. Every rule and choice here is the session's
under the owner's standing rules (`authority: SESSION`, reversal stated). The checks named are AI reviews.

## The result, with its denominators

Board C's committed netlist (`v2/ecad/pcb-c-display-c8/out/pcb-c-display.net`, sha256 `c9f73945...`) carries 225
parts; 50 are marked exclude_from_bom (48 test points, the camera module's two screws), so **175 BOM parts** in
**87 selections** (`part_identities.py selections --board c`).

| State | Selections | Rows |
|---|---|---|
| RESOLVED, PRINTED: the maker's document prints the part number on the cited page | 20 | 26 |
| RESOLVED, DECODED: the maker's ordering-code table on the cited page decodes it against the selection | 23 | 89 |
| UNRESOLVED | 40 | 56 |
| NOT_A_PART (two solder jumpers, two lead-land pairs) | 4 | 4 |

UNRESOLVED by reason class:

| Reason class | Selections | What it is | Next action (each selection states its own) |
|---|---|---|---|
| CHOICE_OWED | 22 | the design names a class, not a part: 15 panel lamps (no intensity or angle), the sounder, two U-174/U jacks, the M3 bonding screws (8 rows), and C28, whose requirement is now known and for which no part was chosen | the board C author or the mechanical owner states the requirement, then a part is chosen |
| DOCUMENT_OWED | 13 | maker and part number named, no maker's document in the tree prints or decodes it: BAT54W, the Everlight status LED, FH34SRJ, BH254VS-26P, the APEM, NKK and C&K switches (7), ABM8-272-T3, GZ1608D601TF | file the maker's document |
| DOCUMENT_DOES_NOT_NAME_THE_PART | 5 | a series sheet bound by w5ident that prints no part number and that this stream did not decode: Fenghua 0603B103K500NT and 0402CG150J500NT (the table is a column layout), Murata GRM188R61E475KE11D (general catalogue), Arlitech ATNR4010100MT, Uniroyal CS03W5F470LT5E (its part number does not state the 0603 size on the table page) | a DECODED binding on the maker's table where it decodes, else a document that prints the part |

The page of the table is `BOARD-C-SELECTIONS.md` (`part_identities.py render`). The table is
`v2/ecad/tools/pcb_part_identities.yaml` (scope `[c]`), written by `build_table.py`.

## The tool's identity check on board C

`env -C v2/ecad/tools python3 part_identities.py check --out <this folder>/readings/check-board-c-b874b744.json`,
with the held-back Uniroyal sheet fetched: **175 rows, 87 selections, 0 rows uncovered, RESOLVED bindings READ 20 and
DECODED 23, 0 problems, verdict HOLDS** (reading sha256 `3d3775e2...`, table `febe247b...`, tool `60b3f6db...`).
Without the fetched sheet the same check reads 13 bindings UNREAD and reports 13 problems (`--unfetched-ok` passes them,
and the reading says so).

PRINTED (20): D23 BAT46W-7-F (Diodes, p. 1), three SS2040FL (PANJIT, p. 1), 2N7002 (JSCJ, p. 1), two AO3401A (AOS, p. 1),
two SI2300DS-T1-GE3 (Vishay, p. 1), VEML7700-TR (Vishay, p. 1), three 74LVC1G17W5-7 (Diodes, p. 9), two PCA9555PWR (TI,
p. 31), RP2040 (p. 2), SN74LVC1G57DBVR (TI, p. 14), TLV75533PDBVR (TI, p. 28), USBLC6-2SC6 (ST, p. 1), W25Q16JVUXIQ
(Winbond, p. 73). DECODED (23): ten Yageo CC X7R selections (CC0603KRX7R9BB104, CC0805KKX7R7BB106, CC0603KRX7R8BB105
in seven, CC0603KRX7R7BB105) on YAGEO's V.26 page 2, each establishing value, package, tolerance, voltage, dielectric
and construction; thirteen Uniroyal 0603WAF selections (100R to 100k, R50, R14 and R52 among them) on Uniroyal's part
number page 2, each establishing value, package, tolerance and power.

Tests: `python3 tests/run.py test_part_identities` 21 passed, 0 failed, among them the four the DECODED rule asked for (a
binding that holds; a tolerance that contradicts the selection, refused; a table page that lacks a field, refused; a
distributor's page, refused) and round 1's PRINTED fixture (a document that does not print the part, refused). Lint
tests run once each: test_rule_windows 6/0, test_import_before_use 3/0, test_documented_options 6/0, test_swallowed 6/0,
test_shipped_strings 5/0, test_driver_hygiene 78/0, test_public_tables 2/0, test_decision_register 3/0 (2 skipped).

## The DECODED rule (round 2, the session's decision)

A binding is PRINTED or DECODED. A DECODED binding cites the maker's own ordering-code table, one page; the tool
(`read_decoded`) asserts that the fields' codes spell the whole part number, that each code is in its row on that page
and that the row maps it to the meaning claimed (tolerance, voltage, power, packaging, quantity, special features), it
computes the value from its code by the rule the row states (and the power of ten row for resistors), and it compares
the decoded value, package, tolerance, rated voltage, dielectric and a capacitor's ceramic construction with the
selection. It refuses a field missing from the page, a contradiction, a partial spelling, and a distributor's page (a
distributor as publisher, a page printing a distributor's name, or no maker's mark). Power and temperature coefficient
are compared where the part number carries them and are otherwise recorded as not established. **Limit, stated in the
decision:** a DECODED binding shows what a part number means in the maker's scheme, not that the maker makes that value
at that rating (the range table), which w5ident's check found false for three part numbers. The draft for the registry
is `apply_decision_decoded.py` (decision 59 on `b874b744`, the number computed at apply time; authority SESSION,
authority_why, ruled_by "SESSION under the owner's ruling of 21 September 2026", ruled_on 2026-09-29, reversed_by).
`--check` holds; applied once and refused a second time on a scratch copy.

Documents: `v2/vendor/passives/yageo-cc-series.pdf` is filed (brought from fnd/w5ident; its text layer carries no
reproduction, rights or permission wording). Uniroyal's thick film sheet reads "all rights reserved" with no grant and
is HELD BACK: `v2/vendor/passives/held/` is ignored, `sources.txt` records its address and sha256 `11cd644d...`, and
`fetch_held_back.py` fetches it (run on 29 September 2026 17:49Z, the sha256 matched). Both are the makers' sheets as
LCSC's datasheet server hosts them; neither prints a distributor's name.

## The stale BOM export (round 2, facts only; not regenerated)

`readings/bom-export-history.txt`, parsed with `netlist_sexp` and `csv`:
- The file is `v2/release/handover/_generated/pcb-c-display-c8/NOT_FOR_FAB-pcb-c-display-bom-per-reference.csv`,
  **tracked**, sha256 `e9e7e0a8...`, 167 rows. `git log` names one commit: `6dc4e708` (27 September 2026, the H2
  handover exports), taken from the schematic of `99cde56b` (its `provenance.json`).
- **Its writer** is `v2/ecad/tools/handover_exports.py exports` (kicad-cli `sch export bom` per reference), run on the
  KiCad box from a clean extraction (REGENERATE.md) and committed by the integrator. It is none of the three steps
  named: `build_sch.sh` writes `out/<stem>-bom.csv` (grouped; `out/` is ignored by `.gitignore` line 20),
  `finish_board.sh` works on `out/jlc/<stem>-bom.csv`, and the box regeneration (`handover_exports.py regen`, by its
  docstring) compares a regenerated BOM with `out/<stem>-bom.csv` and writes to its own `--out`, not here.
  Its grouped sibling `NOT_FOR_FAB-pcb-c-display-bom.csv` came from the same commit.
- **It agrees with the netlist until `e28f91a6`** (27 September 2026, R14 to 2.2k 1% and R50, R51 added): the netlist of
  `99cde56b`, `6dc4e708` and `e28f91a6^` (sha256 `11eabc2d...`) matches it part for part. From `e28f91a6` it does not;
  set 12's `e41df395` adds D23 and R52, set 13's `407bf3a3` R53 to R56. At `b874b744`: 8 netlist parts missing from it
  and R14's value and order code differ.

## The defects of w5ident's checks, answered for board C (round 1)

| Defect | Answer |
|---|---|
| ID-B1 to ID-B3 | Rule D-2: `check` reads the cited page and refuses a binding that neither prints nor decodes the part. Every board C selection w5ident called RESOLVED was re-read: 14 hold as PRINTED; of its 25 series-sheet bindings, 20 are now DECODED (10 Yageo, 10 Uniroyal) and 5 still refused; 3 more Uniroyal selections (R50, R14, R52), DOCUMENT_OWED in round 1, are DECODED. None of ID-B1's nine named selections, the Mill-Max pins or the SA868 is on board C |
| V-1, W5I-C2-B1 | Does not touch board C: no board C net is declared at 0.5 V or below above ground, or marked a return (`readings/v1-on-board-c.txt`). Corrected anyway as V-1 (a'), with the check's counter-example as a test; its part (b) as V-1 (g), which moves 21 board C nets to UNBOUNDED and changes no selection key |
| CHK2-DRAFTS-1 | the tool reads its flags with `verdict.opt`; the resolver is not brought over |
| The MPN export draft | not brought over; no schematic, generator or export is touched |
| CHK2-DRAFTS-2 (ZIP) | none of w5ident's readings or vendor files except the Yageo sheet (a vendor document, referenced, not in the ZIP); this stream adds about 75 KB deflated |
| CHK2-DRAFTS-6 (TDK) | not brought over; the Uniroyal sheet is held back by the same reasoning |

## What was brought from w5ident, and what changed

Brought: `part_identities.py` and `tests/test_part_identities.py` (from `c08f4d5a`), the Yageo sheet, board C's 84
identities and w5ident's rules (`w5ident-board-c-identities.json`, trimmed). Not brought: the resolver, the six-board
table, IDENTITIES.md, the readings, the drafts, the other 50 vendor files. The tool now parses the netlist, takes rows
from it and compares the BOM export, carries V-1 (a') and (g), rule D-2 with PRINTED and DECODED bindings, a scoped
`check` that writes a reading, and `render` to a named page (`adapt_tool.py` replays the first eight edits; `git diff
fnd/w5ident -- v2/ecad/tools/part_identities.py` shows all).

## Integrator's run order

1. Merge `fnd/w5identc`.
2. `python3 v2/docs/records/w5identc/fetch_held_back.py` (the Uniroyal sheet into the ignored `held/`).
3. `python3 v2/docs/records/w5identc/build_table.py`, then `env -C v2/ecad/tools python3 part_identities.py check`: both
   reproduce with 0 problems if board C's netlist and intent are still `b874b744`'s. If set 14 changed them, the check
   refuses: re-run the builder, run the check with `--out v2/docs/records/w5identc/readings/check-board-c-b874b744.json`,
   and re-pin `READING_SHA256` in `apply_identities_c.py`.
4. `apply_decision_decoded.py --check`, then without it; `decisions_render.py` (test_decision_register refuses a stale
   OWNER-DECISIONS-OPEN.md).
5. `apply_identities_c.py --check`, then without it (the open item's number is computed, after S-120's S-124 if set 14
   opens it first).
6. Open the stale BOM export item from the facts above; `rules_lib.py validate`, the renderers, the box suite (with the
   Uniroyal sheet fetched on the box, or `check` reads 13 UNREAD).

## What stays open

- 40 UNRESOLVED selections (56 rows), each with its next action in the table.
- The DECODED limit: no range-table citation; a decoded part may not be made at that rating.
- Documents not obtained on 29 September 2026: Abracon's ABM8-272-T3 sheet (404 at abracon.com and the archive),
  Hirose's FH34SRJ page (403).
- Not judged: DC bias, grade against the envelope, surge levels, the TCR of the CS03 shunt (not in its part number),
  the order codes' stock (carried from w5ident's reading of 27 September 2026).
