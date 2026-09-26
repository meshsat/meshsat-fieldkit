# Review packets

**UNBUILT PROTOTYPE DESIGN. No V2 board has been fabricated, ordered, assembled or tested, and nothing in these
folders is physical evidence. A review packet is a review input for a qualified reviewer: it does NOT release any board
to layout, fabrication or ordering, and it approves nothing.**

**READINESS OF THESE PACKETS: QUARANTINED, NOT_FOR_FAB.** Every packet says so on its front page and in its
`MANIFEST.json` (`readiness`), and its two BOM files carry `NOT_FOR_FAB` in their names, the one marker that travels
with a copied file without changing its bytes. Boards D and E are held by decision 31 (`v2/ecad/tools/pcb_board_holds.yaml`),
whose hold permits exactly "a review package clearly quarantined as NOT_FOR_FAB"; their packets quote the hold's four
status fields and its permitted and forbidden lines verbatim.

The review of 26 September 2026 (`v2/docs/reviews/2026-09-26-foundation-progress-review.md`, section 5) asked for a
compact packet from the exact candidate revision of each corrected board, so that a reviewer can check the corrections
without KiCad and without the project's history. Each folder here is one board at one revision, built by
`v2/ecad/tools/review_packet.py` (its docstring says how, and what it does not do). The routes by which qualified
people would review them are in `v2/docs/reviews/REVIEW-ROUTES.md`.

## The packets

All four are built from main at `1f614233998c3087a53abfa977be134465ce9f47` and compared with
`82dd1e4dc44efabeee1164a995cda4e866610f3d`, the revision before the round 4 and 5 circuit corrections merged in
`faf8c981`. They were built on 26 September 2026 (15:50 to 15:56 UTC, the last build of that day) with KiCad 9.0.9,
`review_packet.py` sha256 `7913d0a57567d896...` and `v2/vendor/SOURCES.yaml` sha256 `2b192f2bb8ded051...` (both as
committed beside these folders); each `MANIFEST.json` carries the
full hashes, and each packet's `changes/attribution-read-by-hand.yaml` is byte-identical to the file of the same board
in `attribution/` here.

This build exists only because SOURCES.yaml changed after the third build of the day (15:04 UTC, SOURCES.yaml
`f3dcbb6d01de68b5...`): two prose fields of its `usb-esd-array` entry had cited the wrong generator lines (that file's
header lists the three citations corrected), and no code, board, `where`, identity or document field changed. The two
builds were compared file by file. In all four packets `bom/parts-identity.json`, `bom/sources-coverage.json` and
`bom/NOT_FOR_FAB-parts-identity.csv` are byte-identical, and so are the change reports, the native files, the netlists
and the counts. The only differences are the SOURCES.yaml hash, the build time, KiCad's ERC report date, the sheet
PDF's CreationDate, the random temporary directory names in the contract and KiCad log tails, and the hashes that
record those files. A rebuild from the same inputs can also differ in the order in which the revision's
`check_contracts.py` lists two absent boards in `contracts/check_contracts.log` ("A, B" or "B, A"): it passes a
contract's boards as a Python set, so the order follows the per-process hash seed, and one of the two intermediate
rebuilds of that afternoon showed it on board P.

| Folder | Board | Components | Changes against 82dd1e4d | With a finding ID | Only a ruling, decision or rule | No ID of any kind | Contracts naming the board |
|---|---|---|---|---|---|---|---|
| `C-C24-1f614233/` | C, panel backer | 194 to 204 | 10 added, 10 changed | 9 | 8 (TP41, TP42, TP43, TP44, TP45, TP46, TP47, TP48) | 3 (C31, Q6, U9) | 7: 7 PASS, 0 FAIL, 0 UNJUDGED |
| `D-D12-1f614233/` | D, VHF APRS mezzanine | 213 to 221 | 8 added, 15 changed | 22 | 0 | 1 (TP25) | 11: 11 PASS, 0 FAIL, 0 UNJUDGED |
| `E-E17-1f614233/` | E1, dock strip | 163 to 179 | 16 added, 11 changed | 27 | 0 | 0 | 9: 9 PASS, 0 FAIL, 0 UNJUDGED |
| `P-P4-1f614233/` | P, pack BMS | 56 to 82 | 30 added, 4 removed, 9 changed | 17 | 24 (C13, C14, C15, C16, C17, C18, C19, F2, JP1, Q1, Q3, R17, R23, R24, R25, R26, R27, R29, R30, R31, R32, RT1, TP14, U2) | 2 (TP12, TP13) | 4: 4 PASS, 0 FAIL, 0 UNJUDGED |

"Finding ID" means an ID the change answers: a review finding (S-09, F-IN-01, W6-F5), an adjudication (A01 to A11) or a
round record's own item ID (R4E-02, RP-17). A change that carries only an owner ruling (D-15), a decision number or a
rule ID (TST-001) is counted apart from it, and so is a change whose generator statement carries no ID at all; the
packet lists each of those with its reason in words and, where the round record names something the generator does
not, that record's words.

What each packet shows about itself (its `README.md` and `MANIFEST.json`):

- **Schematic.** The paged A3 PDF (`schematic/<stem>-schematic.pdf`, the same paging `build_sch.sh` publishes), the
  whole sheet, the native `.kicad_sch` and `.kicad_pro`, the committed netlist with its intent and provenance files
  (`native/netlist/`), and the generator `gen_sch_<letter>.py`, which is the design's source of truth. The netlist KiCad
  exports from the committed schematic reads PARITY_AFTER_NOISE against the committed netlist on all four boards, and
  so does the same comparison at 82dd1e4d, so both ends of each change report are schematic content and not a stale file.
- **Changes, read by hand.** One row per changed reference: what changed (value, footprint, LCSC code, each pin whose
  net moved), the IDs that are the change's own cause, and the lines of the generator at `1f614233` that carry them.
  Every row was read by hand from the generator at both revisions and the round records (the files in `attribution/`),
  because the first cycle's mechanical fallbacks credited some changes with a neighbouring statement's IDs (a checker
  found it: board P's D1 read "none" with a neighbour's rule, its TP11 to TP14 carried the J_SMB block's S-05, board E's
  D2 carried L2's findings, board C's C31 the rectifiers'). The build now refuses a hand-read file unless every ID is
  written on its cited lines and every cited range is tied to the part (it names the part or one of its own nets, is the
  part's own comment or section header, or the row says in words why it applies). The mechanical reading stays beside
  each row in `changes/changes.json` with a flag for whether it agrees; it no longer credits anything but the part's
  own comment, and every weaker reading is marked UNVERIFIED_ATTRIBUTION with its IDs as candidates only.
- **Parts.** The exported BOM (`bom/NOT_FOR_FAB-<stem>-bom.csv`, byte for byte as KiCad wrote it) and a part identity
  and footprint map (`bom/NOT_FOR_FAB-parts-identity.csv`, `bom/parts-identity.json`), joined to `v2/vendor/SOURCES.yaml`
  with each held document's revision and sha256. A line WITH an LCSC code joins by that exact code. A line WITHOUT one
  joins only an entry that names the board and either points its `where`, read at the revision its line number was
  written against (`where_rev`), at the line's defining statement while naming the reference or the part, or writes its
  fitted order code in the value; every such join says how it was made, and the README lists these lines apart, because
  no order code fixes their maker. Until the third cycle of 26 September 2026 code-less lines never joined, so board E's
  corrected choke L2 (SRF1260-1R5Y, F-IN-02) appeared without the entry filed for it; now it joins, as do board E's U16
  (TPS22810, a new entry), board P's J_CELL and J_SMB (JST XH) and board D's U2 (SA868, order code not pinned).
  `bom/sources-coverage.json` lists every entry that names the board and what it joined; an entry that names the board
  and joins nothing is listed with its reason (none on these four), and an entry for a part placed on no schematic (the
  pack cells, the PA module bolted to the plate) is listed as such. Most passives carry no entry by design (the entry
  criteria are in SOURCES.yaml's header); `JLC-CERTIFIED.tsv` predates these netlists and a CERTIFIED row is not proof
  of identity.
- **Contracts.** The contracts of `check_contracts.py` (the revision's own) that name the board, each as the checker
  decided it. For boards C, D and E, boards A and B are regenerated from their generators at `1f614233` in the build's
  work copy, because their committed netlists predate the widened generator identity (their contracts read UNJUDGED in
  the tree); each regenerated netlist reads PARITY_AFTER_NOISE against the committed one. So those contracts are judged
  against A's and B's circuits AS COMMITTED at `1f614233`, before their round 6 corrections.
- **ERC** as a report of every severity (warnings only on all four boards: library symbol notes, off-grid endpoints and
  unconnected wire ends), not a verdict; `erc_gate.py` with each board's allow list is the gate. kicad-cli also prints
  "schematic has annotation errors" on the netlist and BOM exports of all four boards without naming a symbol; a text
  reading of each committed schematic finds no repeated (reference, unit) and no unannotated reference, so the cause is
  not established, and each packet says so beside its netlist parity.
- **No change marks on the sheets.** The PDFs are plain exports of the committed schematic; the change table in each
  README marks what changed, by reference, with the generator lines that carry each finding ID.
- **Completeness against the repository's own `.gitignore`.** The build asks git's own matcher whether any packet file
  would be left out of a commit; all four answer none. (The first cycle put the native netlists under `native/out/`,
  which the tree's `out/` rule ignores; they are under `native/netlist/` now.)

## What these packets do not settle

- **The layouts.** The declared phases C24, D12, E17 and P4 name the committed board files, which predate these
  netlists: rule SCH-002 reads FAIL against them (commit `faf8c981`), and every board is re-laid at layout entry.
- **Calculations and fault-state diagrams.** For board P they are the battery review stream's packet,
  `v2/docs/review-packets/battery/` (pending merge when this page was written), which also changes board P's circuit
  (the second level's over-temperature is restored); see "Boards not here yet".
- **The pack SMBus lead has no contract.** No check in `check_contracts.py` at `1f614233` compares board E's `J_SMB`
  with board P's `J_SMB`, the harness round 4 corrected (A07, S-05). Read by hand from the two committed netlists on
  26 September 2026 (a desk reading, not a gate): pins 1 to 4 are SMBC, SMBD, the return (E: `GND`; P: `PACK_N`, the
  pack side of the shunt) and PRES (E: `PRES_LEAD`; P: `PRES_J`) on both ends, so the lead is straight-through by
  function. A contract for it is owed by the owner of `check_contracts.py`.

## Boards not here yet

- **A and B**: their circuit corrections are round 6 candidates and are not on main at `1f614233`. Their packets are
  built with the same tool at the revision that merges them, compared with `1f614233`, each with its own hand-read
  `attribution/<letter>-<revision>.yaml`.
- **D's keying remedy** is also in round 6; when it merges, board D gets a new packet at that revision and this one
  stays as the record of `1f614233`.
- **P after the battery review stream merges**: that stream's candidate changes U2's TS network (and adds its socket and
  test point). Board P gets a new packet at the revision that merges it, compared with `1f614233`, and that packet, with
  the battery packet, is what route R-BAT sends. `P-P4-1f614233` stays as the record of `1f614233` and is not sent.
- **E5** has no schematic by construction: its targets are generated from board A's board file, and its contract is
  judged between the two boards by `block_contract.py`.

## Checking and rebuilding a packet

    python3 v2/ecad/tools/review_packet.py verify v2/release/review-packets/P-P4-1f614233

re-hashes every artefact against `MANIFEST.json` and `SHA256SUMS` and fails on a changed byte or a stray file
(`sha256sum -c SHA256SUMS` inside a folder checks the same list). To rebuild one, on a host with git:

    python3 v2/ecad/tools/review_packet.py stage --repo . --rev 1f614233 --prev 82dd1e4d --out /tmp/stage

and on a KiCad 9 host (mutool installed; the stage is all it needs), from a copy of the stage's own tools directory
with this `review_packet.py` placed in it, so the tool imports the revision's `regen_compare.py` and its helpers:

    cp -r /tmp/stage/rev/v2/ecad/tools toolrun && cp v2/ecad/tools/review_packet.py toolrun/
    python3 toolrun/review_packet.py build --stage /tmp/stage --board c --out-root <dir> --sources v2/vendor/SOURCES.yaml \
        --attribution v2/release/review-packets/attribution/c-1f614233.yaml --regen-siblings a,b

Board P was built without `--regen-siblings`, because none of its contracts names A or B.
