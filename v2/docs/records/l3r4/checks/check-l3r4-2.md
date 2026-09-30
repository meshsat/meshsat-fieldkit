mergeable: yes

# CHECK-2 of layer 3 round 4 (`fnd/l3r4` at `fcfc6007`): the narrow re-check of round 4b

An AI check by a session that wrote none of the round, not a qualified review. Written 30 September 2026, 09:17 CEST.
Scope: `git diff 3afdc2d6..fcfc6007` only (six files: `reissue.py`, `PASSAGE-MAP.md`, `README.md`,
`apply_layer_status_l3_r4.py`, `test_l3r4.py`, `LAYER-STATUS.md`), against CHECK-1's blocking item B1 and minors 1 to
9. Everything below was run in a `--no-local --single-branch` clone of `fnd/l3r4` with the set 17 evidence archive
(`int17-evidence-de11cc4e.tar`) installed, or read from it. Nothing was committed or pushed; the clone is removed.

## Verdict

B1 is answered: the head note now reads two packs only where a passage states a requirement, an intention or a
condition, the one-pack circuit as generated is CURRENT with its own proposed status row, and the D-27 contradiction
CHECK-1 named (one BQ25731 charging each of two packs, a second gauge on `J_SMB`) is gone. Minors 1 to 9 are answered.
The approval loop works as the coordinator described. No blocking item. Five minors, all residuals of the answers.

## B1, the one-pack circuit

- **The map.** `PASSAGE-MAP.md` has 100 passages (counted from its headings): 51 DEFINITION and 49 CURRENT, of which
  19 HF, 17 PACK, 1 SOLAR and 12 CELL. The PACK passages are exactly the lines listed: 306, 311, 312, 313, 320, 335
  to 337, 536 to 541, 547 to 550, 583 to 588, 590 to 594, 598 to 600, 634 to 640, 695, 830 to 837, 854 to 860, 893
  and 928 to 934. A CURRENT passage is now whole lines (`locate()`), and the map quotes every passage whole (the test
  asserts it).
- **The head note** (C02 and B02, read in all three drafts I generated): "Where a passage this re-issue does not restate
  states a requirement, an intention or a condition about "the pack", it reads as each of the two packs of owner ruling
  D-27 ... Where it states the circuit as generated for one pack (one charger, one gauge, one pack node, one protection
  chain), it states the design before that ruling, whose packs each have their own charger path and gauge; the current
  values are kept in `handover/DEFINITION-STATUS.md`." The change record repeats it. Lines 313 and 590 to 594 are CP04
  and CP10 and read as the design before D-27: the contradiction is gone.
- **DC-L3-PACK** is proposed in every draft where row L3-OD1 is `approve`, naming the lines and the circuit (the
  BQ25731 through `R17`, `J_SMB` with `U10` its only host and `CELL_F`, board P's second level, JP1, F2, K3).
- **The new test** (`t_l3r4_every_line_of_the_one_pack_chain_is_a_current_passage`) holds every line before the
  appendix that matches its designator list to a PACK passage, except the rulings table. It does what its docstring
  says. Lines it misses, because they name the chain in words: minor 1.

## Minor 1 of CHECK-1, the approval loop

The draft and record now bind the answers digest (the six rulings and every record citing them); the approving
ruling is outside it. I ran the path by hand on my recommended-answers copy: generated (draft `7a4a488fc3bc1bde`,
record `1bcd4e6426c8999c`, digest `8d2dcae37600df7c`); added D-32 with `decides: definition_reissue` dated 2 October
2026 to the registry copy and filed `definition_reissue` `{record, sha16 1bcd4e6426c8999c, approved_by D-32}` in a copy
of `l3r2.yaml` (`--data`); then:
- `--check` reads both files current (exit 0);
- a write is refused, "the re-issue is approved ... an approved record is only compared (--check), never rewritten"
  (exit 2), and both files are byte identical to before;
- the renderer accepts it: `reissue_ok` returns `(True, '')` and `closure_state` gives L3-C26 CLOSED; before the
  approval it read "not filed" and "OPEN (the session prepares the re-issue for the owner's approval)"; with the
  approving ruling dated 30 September it refuses ("D-32 is dated before the rulings D-26 ... D-31"), and with
  `approved_by: D-27` it refuses ("D-27 does not decide the re-issue").

The README now runs `reissue.py` once before the approval and only `--check` after it. Residual: minor 2.

## Minors 2 to 9 of CHECK-1

- **2, CFL-017.** C21, C29 and B18 now carry CFL-017's state read from the registry: "CFL-017 resolved" under
  `reading-c` (registry CONFLICT_RESOLVED), "CFL-017 kept open" under `measure` and `cells` (CONFLICT_OPEN); C29 says
  "Decided on ..." and B18 "The owner decided row L3-OD5 on them". No "answered CFL-017" is left in any draft.
- **3, the guard.** `guard_out` refuses a link and compares real paths before anything is written. With
  `DEFINITION-REISSUE-DRAFT.md` a symlink to the brief: refused "is a link", exit 2, nothing written, brief unchanged;
  with the record's name a symlink to a scratch file: refused, the target untouched. Residual: minor 3.
- **4, LAYER-STATUS.md.** The paragraph "Whose each remaining item is" ends at the integrator; "A checker: the
  independent check of L3-R2 (L3-C27)" is gone, and the script edits that sentence with the row, each asserted once.
- **5, REQ-072.** The reading "reads FAIL (DESK_REVIEW, SCHEMATIC phase) when this re-issue is written", taken from
  the record's fields, is in C28, C32 and B08 (read in the draft) and in C17 and C18 with "the design as it stands
  does not meet mission M1" (C18 read in the draft, C17 from `energy()`, which appends the same sentence); B15 opens "Does not meet mission M1 as the design stands."; the draft and
  the change record gain a section "M1 as the registry reads it", and DC-L3-M1 carries the reading with release effect BLOCKER
  and the latest evidence entry quoted (every lid fails on the circuit as drawn, only the hypothetical path meets, "No
  figure is demonstrated capability ... the verdict stays FAIL").
- **6, values from the registry.** The array phrase is read from row L3-OD3's option label and asserted against the
  ruling ("400 Wp in 2S2P into board E's 200 W stage"; "400 Wp in 1S4P" in the other set); the tablet size from
  REQ-011; the stage rating from REQ-016; `keep`'s array from its ruling. Residual: minor 5.
- **7, the push.** The test comment and the README name the QMX out, TYP and 20 N as stand-ins, not recommendations.
- **8, the record.** Its paragraphs are separated by blank lines (the test asserts it).
- **9, full quotes.** Every passage, CURRENT included, is quoted whole in the map.

## Generator reruns

On registry copies built by the prepared scripts:
- recommended answers (QMX out, TYP, 20 N as stand-ins): 50 restated (33 CONOPS, 17 brief) and 37 read through
  DEFINITION-STATUS (19 HF, 17 PACK, 1 SOLAR), as stated;
- the tests' other set (WAB, `qmx-outside`, `1s4p`, `reject`, `measure`): 45 restated (29 and 16) and 19 (HF 1095,
  17 PACK, SOLAR 991), as stated;
- my own (TYP, `tablet-out`, `2s2p`, `adopt` at 11.7 N, `cells`): 42 restated and 30 (17 PACK, 1 SOLAR, 12 CELL), with
  DC-L3-CELL and the head note's cell sentence.
No generated file carries an en or em dash.

## Gates

`rules_lib.py requirements`: 144 records, 0 errors, 0 warnings. `rules_render.py --requirements --check`: current.
`render_l3r2.py --check`: 3 pages, 0 out of date. `reissue.py --map --check`: current. `dryrun.py`: byte identical to
`dryrun.out`. Tests: 104 passed, 0 failed, 0 skipped. The 763 added lines of the diff carry no en or em dash, no
internal host name and no absolute path. `CONOPS.md`, `PRODUCT-BRIEF.md`, the registry and `v2/release/` (H3) are
unchanged; the author is the owner's identity with no trailer. The README's integrator run order also ran on a branch
from main `8fec0733` with no failure (104 tests), leaving a tree identical to `fnd/l3r4`.

## Minors

1. **The PACK list misses lines that name the chain in words.** Outside every PACK passage, before the appendix:
   379 ("the gauge's 20 A for 2 s limit and the 25 A blade bound"), 698 (C3: "the gauge's current, or the charger's
   reading in the heat stage as board B is generated"), 822 to 826 ("the pack voltage the charger reads (above) is
   12.8 V"), 881 ("the charger loses its host and falls to 256 mA"), 882 ("the charger has no host"), 887 ("the
   gauge's SMBus shutdown the sensor controller already sends is the one the design has"), 911 ("the charger falls to
   its host-free 256 mA"), 990 ("the pack chain's 10 A continuous rating") and 1106 (the 7a row: "the pack voltage the
   charger reads at 12.8 V"). The head note's general sentence reads them correctly, so nothing contradicts D-27, but
   DC-L3-PACK and the change record list the chain's lines as if complete. One consequence worth fixing: 928 to 934 are
   PACK, so K3's "pack current at most 9.0 A" reads as the design before D-27, while the same 9.0 A on the same
   quantity in C2 and C3 (697, 698) is a condition and reads per pack. Either list these lines, or have DC-L3-PACK say
   that the pack-current limits K3, C2 and C3 are restated per pack or in total downstream.
2. **After approval `--check` goes out of date when a cited record changes.** The digest covers every record citing
   the six rulings as the registry holds it. On my approved copy, one added note on REQ-072 turned `--check` to OUT OF
   DATE (exit 1), and writes stay refused. REQ-072 will change at layer 4. The README says that after approval
   `--check` "reads the approved files current". Either compare the approved files to the sha `definition_reissue`
   files and the draft sha the record names, or state that scope in the README.
3. **A hard link passes the guard.** With `DEFINITION-REISSUE-DRAFT.md` a hard link to `PRODUCT-BRIEF.md` (same file
   system), `islink` is false and the real paths differ: the generator wrote into the brief and only then refused ("a
   baselined file changed while the re-issue ran"). Restored in the clone. Contrived; `os.path.samefile` against the
   two baselined files, or refusing an existing output with more than one link, closes it.
4. **The CELL list is incomplete, and no test holds it.** Lines naming the held cell's limits outside CELL passages:
   CONOPS 339 (the 3.35 Ah specification minimum), 394 (discharge to 60 C, section 3.15), 727, 729 and 730 (the
   cells' 60 C), 1106 (the 2.65 V cut-off); the brief's 158 (their 60 C discharge limit). The head note's cell sentence
   covers them in general (it is written into both documents); DC-L3-CELL's list does not.
5. **`Ctx.store()` is still a typed copy of D-27.** "two separately protected packs of the Samsung INR18650-35E, a base
   4S6P across the two base pockets ... under its own protection board, each with its own charger path and gauge" is
   typed, not read or asserted against D-27's ruling, the same kind as CHECK-1's minor 6 (I missed it then). Under
   `cells`, the restated store passages (C07, C09, C17, C23, B06, B15) keep naming the cell D-31 reopens, and only the
   head note says so; the cell sentence also types "CFL-017 stays open until the cell is chosen" instead of reading
   `cfl017_state`.
