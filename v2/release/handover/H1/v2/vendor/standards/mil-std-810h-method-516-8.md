# MIL-STD-810H, Method 516.8 (Shock), Procedure IV: the transit drop table the kit's E1 severity rests on

**What this file is.** A transcription of the one table and the two paragraphs this project CITES, not a copy of the
standard. Requirement REQ-023 (the kit's carried mass, session choice of 27 September 2026 under the owner's standing
rule of 26 September 2026) and `v2/docs/V2-SPEC.md` correction 25 read the owner's ruled transit drop E1 of
`v2/docs/TEST-PLAN.md` (D-02c: 26 drops from 1.22 m) against it. Filed 27 September 2026 (MESHSAT-1357, layer 1
closer). The standard is a United States Department of Defense document published through the ASSIST database of
the Defense Logistics Agency; this folder transcribes standards rather than copying them, as for every file here.

| | |
|---|---|
| document | MIL-STD-810H, Environmental Engineering Considerations and Laboratory Tests; Method 516.8, Shock (82 pages) |
| edition read | the base issue of MIL-STD-810H as downloaded from ASSIST on 2019-03-04T16:12Z (every page carries "Source: http://assist.dla.mil -- Downloaded: 2019-03-04T16:12Z"); whether Change Notice 1 of MIL-STD-810H altered this table was not checked |
| source | `quicksearch.dla.mil` did not resolve from this host on 27 September 2026; the file read is a copy of the ASSIST download published at `https://cvgstrategy.com/wp-content/uploads/2019/08/MIL-STD-810H-Method-516.8-Shock.pdf` |
| fetched | 27 September 2026, curl from the runner, 1,526,503 bytes |
| sha256 of the file read | `24686aad175659ec09234b6bba53e80efdc3584966a031d3200555d9cafb197c` |
| clauses transcribed | 2.2.2 d (what Procedure IV is for, first sentence), 4.6.5 (first sentence), Table 516.8-IX (the row for items under 45.4 kg, and the row below it), Note 1 of that table (first two sentences) |

## 2.2.2 d, Procedure IV, Transit Drop (page 516.8-4)

> Procedure IV is a physical drop test, and is intended for materiel either outside of, or within its transit or
> combination case, or as prepared for field use (carried to a combat situation by man, truck, rail, etc.).

## 4.6.5, Transit Drop (Procedure IV) (page 516.8-31)

> The intent of this test is to determine the structural and functional integrity of the materiel to a transit drop
> either outside or in its transit or combination case.

## Table 516.8-IX, Logistic Transit Drop Test (page 516.8-33)

| Weight of test item and case, kg (lb) | Largest dimension, cm (in) | Notes | Height of drop, cm (in) | Number of drops |
|---|---|---|---|---|
| Under 45.4 (100), "Man-packed or man-portable" | Under 91 (36) | | 122 (48) | "Drop on each face, edge and corner; total of 26 drops" (note 5) |
| Under 45.4 (100), "Man-packed or man-portable" | 91 (36) and over | | 76 (30) | as the row above |
| 45.4 to 90.8 (100 to 200) inclusive | Under 91 | | 76 (30) | "Drop on each corner; total of eight drops" |
| 45.4 to 90.8 (100 to 200) inclusive | 91 (36) and over | | 61 (24) | as the row above |

The heavier rows (90.8 kg and more) are not transcribed. Note 5 of the table: "If desired, divide the 26 drops among
no more than five test items (see paragraph 4.6.5.1)."

Note 1 of the table, first two sentences: "Perform drops from a quick-release hook or drop tester. Orient the test item
so that, upon impact, a line from the struck corner or edge to the center of gravity of the case and contents is
perpendicular to the impact surface." The same note makes steel backed by concrete the default drop surface and allows
concrete or 5 cm (2 in) plywood backed by concrete under the conditions it states; `v2/docs/TEST-PLAN.md` E1 names
plywood over concrete.

## What this project reads from it

The owner's E1 (26 drops from 1.22 m, faces, edges and corners) is the first row: an item and case under 45.4 kg with
its largest dimension under 91 cm, man-packed or man-portable. A kit at or above 45.4 kg would fall in the third or
fourth row, a different test (eight corner drops from 76 or 61 cm). REQ-023 therefore states that category as the
kit's carried-mass design target; the kit is weighed at assembly.
