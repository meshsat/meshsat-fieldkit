**DONE:** the line citations into the 25 generators W34 edited, re-taken in the live pages (the annex's five `[E11PY:n]`, the ledger's `[PAL:186-255]`), each binding paragraph given its set 32 sentence, test_w3annex's four anchor keys restated with their basis, the supplier page's section 0e pointer written as an apply script, test_w42cite. **NOT DONE:** TP-E11-29's prose citation (pinned by `tp_check.out`, section 3 below) and every citation into an output (no `.out` moves on this branch). **NEXT:** the coordinator runs the apply script on the integrated tree and applies section 3's row before the procedures' checker is regenerated.

# W42: set 32's moved line citations in the live pages, and the supplier page's section 0e pointer (MESHSAT-1357, 6 October 2026)

Written by worker W42 on branch `fnd/w34pdftext` from W37's tip `886704ea`, from 16:14 CEST. Record text only: it changes no figure,
no claim, no class and no verdict, edits no generator, no output and no filed check. Prototype framing: nothing in the kit is built,
bought, powered or measured.

## 1. The method

W34's commits (`aed4bd23` to `6dc69ad2`) changed only how 25 record generators read the makers' PDF text, which moved their lines.
W37's list (`<worktrees>/_runs/int32/PLAN.draft.md`, section 3) found the `<generator>.py:N` citations; it does not read the
`[ALIAS:N]` form, so this record scanned every tracked text file outside `v2/vendor/` for both forms, plus the prose form
"`<generator>.py` line(s) N", mapped each cited line from `aed4bd23` to the tip with difflib's equal blocks, and read the words on
both. Each citation is then one of: re-pointed (a live page whose own citation rule re-cites moved lines), bound (a citation that
names its commit, or a quotation of a filed check), or left (a filed check, a superseded draft, or a page another file pins).

## 2. What is re-pointed

| Page | Old | New | The words on the new lines |
|---|---|---|---|
| `v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md` line 183 | `[E11PY:5957]` | `[E11PY:6019]` | "R17's design target: its line passes with twice its U" |
| same, line 184 | `[E11PY:5967]` | `[E11PY:6029]` | `S["z17_t"] = solve(` |
| same, line 186 | `[E11PY:6120]` | `[E11PY:6182]` | `fmt(S["z17_t"], 3)` |
| same, line 186 | `[E11PY:6313]` | `[E11PY:6375]` | `fmt(S["z17_t"], 3)` |
| same, line 188 | `[E11PY:6382]` | `[E11PY:6444]` | `fmt(R["S26"]["z17_t"], 2)` |
| `v2/docs/records/l4close/REMAINING-ENGINEERING.md` line 169 | `[PAL:186-255]` | `[PAL:201-270]` | `cap()` from its `def` to the PRINTED-rows offset line |

Every old line at `aed4bd23` is the new line at the tip, byte for byte (record l4e11's generator moved by 62 lines, record l9t5's
`l9t5_paloop.py` by 15). Each page's citation-form paragraph gains a set 32 sentence inside its existing line (annex line 135,
ledger line 50), so no line of either page moves and the citations other files make into them still hold. `test_w3annex.py`'s
anchor keys for the four E11PY citations it holds, and its one mutation, are restated with their basis in a comment.

## 3. What is left, and why

- **Bound, kept as written:** the ledger's four line numbers inside cx46's quoted words (lines 128, 131, 249 and 277: cx46's own
  lines of `4d0ff8a2`, the text test_remeng holds to the filed check); `records/int30/NEXT-SET-SMALL-ITEMS.patch.md` line 613
  (`l4e11_power.py:7128`, read "at `c4492dd3`" by the page's own rule; E11-43 is on that line there); on main only,
  `records/int30/CLASSIFICATION.md` lines 41, 43 and 44 and `records/l4close/P0-POWER-LIST.md` lines 43 and 129 (each
  `<commit>:<path>:<line>`, bound to `4d0ff8a2`, `7070f106`, `bca7b0dc`, `6bc4424e`, `bbba3e53` and `6fe398e9`).
- **Filed checks and records as received:** 81 citations in 20 files (every check and record filed as received that cites one of
  the 25 generators, moved or not), never edited; `v2/ecad/tools/tests/test_w15class.py` line 43 quotes cx46's text and stays.
- **Superseded drafts:** 20 citations in `records/int30/CLASSIFICATION.draft.md` and `RESULT.draft2.md` and
  `records/l4close/P0-POWER-LIST.rev3.draft2.md` and `.draft3.md`, and three in the prose form in drafts, left as drafts.
- **`v2/docs/test-procedures/TP-E11-29.md`, a live page, NOT re-pointed:** its line 791 cites "`v2/docs/records/l4e11/l4e11_power.py`,
  lines 5957 and 5967" (now 6019 and 6029) and its line 794 "script's line 6382" (now 6444). The procedures' checker output
  `v2/docs/test-procedures/tp_check.out` prints the page's sha256 and `test_test_procedures` holds that output to the checker, so the
  re-cite needs the checker's output regenerated, which this branch does not do. The row for the coordinator, applied before
  `tp_check.out` is regenerated: line 791, Old `lines 5957 and 5967`, New `lines 6019 and 6029`; line 794, Old
  `script's line 6382`, New `script's line 6444`.
- **Citations into outputs** (`[E11:n]`, `[F01:n]`, `[CON:n]` and the rest): no `.out` moves on this branch; set 32's regeneration
  adds the text input lines to 25 outputs, so those citations are owed a re-take after it.

## 4. Item 2: the supplier page's section 0e

Section 0e exists on main only (set 30's adoption), and the page is the integrator's file, so the sentence is
`apply_supplier_0e_pointer.py`, run on the integrated tree after the merge:
`python3 v2/docs/records/w42cite/apply_supplier_0e_pointer.py`. It appends to section 0e's item 1, inside its last line:

> Where a record reads a held-back sheet as its extracted text rather than as the PDF, that text is held back with the sheet and is
> re-taken after the fetch, before the record's script runs; section 7, item 2 gives the command and the tool versions it needs.

It refuses a page without section 0e, a page whose section 7 lacks the re-take step, and a second run. Read on a three-way merge of
the page (main's, the branch's, their merge base `dd1aed00`, `git merge-file`, clean): applied once, every line in place.

## 5. Decisions taken (SESSION, under the owner's standing rule of 26 September 2026)

- The alias-form and prose-form citations W37's method did not read are in scope (the brief names `[ALIAS:n]`); reverse by
  restoring the old strings in the two pages and test_w3annex.
- TP-E11-29 is left with its row in section 3 rather than edited with a stale checker output; reverse by applying the row.
- Item 2 is an apply script, as the worker rules require for an integrator file the branch does not carry in that form.
