mergeable: yes

# CHECK-3 of layer 3 round 4 (`fnd/l3r4` at `e8e3ef57`): the delta check of round 4c

An AI check by a session that wrote none of the round, not a qualified review. Written 30 September 2026, 09:57 CEST.
Scope: `git diff fcfc6007..e8e3ef57` only (four files: `reissue.py`, `PASSAGE-MAP.md`, `README.md`, `test_l3r4.py`),
against CHECK-2's five minors. Everything below was run in a `--no-local --single-branch` clone of `fnd/l3r4` with the
set 17 evidence archive (`int17-evidence-de11cc4e.tar`) installed, or read from it. Nothing was committed or pushed; the
clone is removed.

## Verdict

The five minors of CHECK-2 are answered, with one residual on the completeness test. The after-approval check, the
hard-link guard, the store wording under `cells`, the counts and the gates all hold as stated. No blocking item: nothing
in the proposed texts misstates the design or D-27. Four minors.

## 1. The PACK group, 17 to 32 passages

- The map has 121 passages (counted from its headings): 51 DEFINITION, 19 HF, 32 PACK, 1 SOLAR, 18 CELL. The PACK
  additions are the lines listed: 379, 529, 566 to 569, 571 to 578, 697 to 698, 822 to 827, 881, 882, 887, 889, 911,
  990, 991, 1097 and 1106.
- DC-L3-PACK now reads, in the drafts I generated: "whether the pack-current limits of K3, C2 and C3 (9.0 A) apply per
  pack or in total is set downstream". CHECK-2's K3 against C2 and C3 point is closed.
- **The eight exemptions are sound.** Each line reads as an operation, a power state, a behaviour or an intention that
  the head note reads per pack, as its reason says: 307 (Deploy: a pack in the gauge's shutdown woken by an input),
  308 (Startup: starts only once an input has woken the gauge), 321 (Storage), 348 (PS-SHUT, which also names the
  second level's supply current, readable per pack), 561 (the gauge's charge hold and discharge cut opening the pack's
  FETs), 817 (graceful shutdown on the gauge's state of charge, its charger fallback in PACK), 1100 and 1111 (the 7a
  choices).
- **The stale-exemption check works.** An exemption added for a line with none of the vocabulary fails it.
- **The completeness test is self-referential** (minor 1). It searches for the exact phrases found in the PACK
  passages, not for `VOCAB_RX` itself. So a line naming the gauge or charger by a phrase that no PACK passage carries
  escapes. Removing a PACK passage also removes its own phrases, so the test cannot see that removal. Both are shown
  under minor 1.

## 2. `--check` after the approval

`--check` with `definition_reissue` filed now calls `approved_check()`. It confirms that the record in the out-dir is
the file filed, at the sha filed, and that the draft is at the sha the record names. Nothing is recomputed from the
registry, and the check runs before the baselined files are read. I ran the path by hand on my recommended-answers
copy:
- Setup: record `3fd3661404b6a060`; D-32 added with `decides: definition_reissue`; `definition_reissue` filed in a
  copy of `l3r2.yaml` passed with `--data`.
- Approved, then `--check`: "the approved draft and change record are the files definition_reissue names".
- A note and an evidence entry added to REQ-072, then `--check`: the same, current. CHECK-2's minor 2 is closed.
- A write: refused (exit 2), and both files are byte identical.
- The draft changed on disk (one newline): "DIFFER: DEFINITION-REISSUE-DRAFT.md is not at the sha256/16 the record
  names (269b4a516294c79b)".
- The record changed on disk: "DIFFER: ... not at the sha256/16 definition_reissue files (3fd3661404b6a060)".
- An out-dir other than the one filed: DIFFER.
- The renderer on the approved state with the changed REQ-072: `reissue_ok` returns `(True, '')` and L3-C26 reads
  CLOSED.

## 3. Hard links

`guard_out` now refuses, before anything is written, an output that is a symlink, resolves to a baselined file, is
the same file as one (`samefile`), or has more than one link. Every case below refused before writing:
- The draft name hard linked to the brief (inside the clone): "is the same file as a baselined file (a hard link)",
  exit 2.
- The record name hard linked to the brief (from the scratch directory, same file system): refused the same way, and
  the draft was not written either.
- The draft name hard linked to an unrelated scratch file: "has more than one link", exit 2, the file untouched.
- The draft name hard linked to CONOPS with `--check`: refused.

`CONOPS.md` and `PRODUCT-BRIEF.md` stayed at `6cb7b241cb84d729` and `85513b92ed0daf55`, and the clone was clean after.

## 4. The CELL group, 12 to 18 passages

It now covers CONOPS 338 to 339, 394, 548, 727 to 730, 1012 and 1106, and brief line 158. DC-L3-CELL names
`PRODUCT-BRIEF.md` line 158 beside the CONOPS lines. Brief line 67 is exempt because B06 restates it: B06 now names
the cell through `Ctx.cell()`, reopened under `cells`, so the reason is sound. The same vocabulary test covers CELL.
Residual: minor 2.

## 5. The store

- `Ctx.d27()` reads the cell and the base block from D-27's ruling ("two separately protected packs of the (.+?), a
  base pack of (4S\d+P) across the two base pockets") and asserts two more phrases in its text: "a lid pack under its
  own protection board" and "each with its own charger path and gauge". `store()` builds the passages from those
  values.
- Under `cells` (the tests' third set and my own), C07, C17, C23, B06 and B15 read "the Samsung INR18650-35E as held,
  the cell of D-06 that owner ruling D-31 on row L3-OD5 reopens (CFL-017 kept open)".
- C09 adds "Row L3-OD5's answer reopens that cell (...)", and C27 adds "the held cell's figure, which ... reopens".
- The head note's cell sentence reads "CFL-017 is kept open in the requirements registry", from the registry.
- Under `reading-c` none of this appears (the test asserts it).

## 6. Reruns

On registry copies built by the prepared scripts:

| Answer set | Restated | CURRENT | Split of CURRENT |
|---|---|---|---|
| Recommended answers (stand-ins) | 50 (33 CONOPS, 17 brief) | 52 | 19 HF, 32 PACK, 1 SOLAR |
| The tests' other set | 45 | 34 | 1 HF, 32 PACK, 1 SOLAR |
| The tests' third set (tablet out, `keep`, `cells`) | 41 | 50 | 32 PACK, 18 CELL |
| My own set (tablet out, `2s2p`, `adopt` at 11.7 N, `cells`) | 42 | 51 | 32 PACK, 1 SOLAR, 18 CELL |

The first three are as stated. No generated file carries an en or em dash.

## 7. Gates

- `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings.
- `rules_render.py --requirements --check`: current.
- `render_l3r2.py --check`: 0 out of date.
- `reissue.py --map --check`: current.
- `dryrun.py`: byte identical.
- Tests: 105 passed, 0 failed, 0 skipped. The hard-link test ran; it did not skip.
- The 409 added lines carry no en or em dash, no internal host name and no absolute path.
- `CONOPS.md`, `PRODUCT-BRIEF.md`, the registry and `v2/release/` (H3) are unchanged.
- The author is the owner's identity, with no trailer.
- The README's integrator run order ran on a branch from main `8fec0733` with no failure (105 tests). It left a tree
  identical to `fnd/l3r4`.

## Minors

1. **The PACK completeness test cannot see what it does not already hold.**
   - **How it works.** `uncovered()` searches for the phrases `vocabulary()` finds in the PACK passages, not for the
     pattern `VOCAB_RX`.
   - **Lines that escape.** Searching `VOCAB_RX` itself outside the PACK passages, the rulings table and EXEMPT finds
     205 ("the gauge holds"), 289 ("the pack gauge holds"), 349 ("the gauge's 336 uA", PS-OFF), 468 ("the pack gauge's
     readings"), 819 ("the gauge's state of charge"), 890 ("the hottest cell as the gauge reads it"), 914 ("the gauge
     and board P's second level") and 1014 ("the gauge's learned full-charge capacity").
   - **Judged one by one.** Seven read as behaviours or conditions per pack, like the eight exemptions, and do no harm.
     Two are worth fixing:
     - 349 is a figure of the one generated gauge in a power-state row and belongs in PACK.
     - 890 says what 566 to 569 say ("as the pack gauge reads them", PACK) but is not listed.
   - **The mutation.** Removing the PACK passage at 379, 697 to 698, 881, 882 or 990 leaves the test green, because
     each passage carries phrases no other passage does. Removing 529, 889, 1097 or 1106 is caught.
   - **Remedy.** Search `VOCAB_RX` itself, and list or exempt each hit with its reason; the eight lines above would then
     be listed or exempted.
2. **The CELL group misses the cell sheet's ageing figures.**
   - CONOPS 1015 ("The cell sheet's own floor, 60 % after 500 cycles (7.9)") and 1103 (the "Aged" row: "80 % of the
     cell's specification minimum capacity ... the cell sheet's 60 % after 500 cycles") are figures of the held cell's
     sheet. They are outside the CELL passages.
   - `VOCAB_RX["CELL"]` has no term for them, and it is filtered through the CELL passages the same way as PACK.
3. **B06 lost a word.** Under `reading-c` it now reads "two separately protected 4S lithium-ion packs to be built ...,
   of the Samsung INR18650-35E: a base 4S6P ...", where it read "of Samsung INR18650-35E cells". Cosmetic: "cells"
   after the cell phrase restores it.
4. **The link tests link the tree's own brief.** The symlink and hard-link tests point at `v2/docs/PRODUCT-BRIEF.md`
   in the tree, so if the guard ever regressed, a test run would write into the baselined file before `_generate`'s
   after-check reports it. Low risk while the guard stands.
