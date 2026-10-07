#!/usr/bin/env python3
"""K-15, K-17, K-20 and K-21 (record l4k, MESHSAT-1357, W131, 7 October 2026): the remaining-engineering ledger's section 6 items
A, B, C and F, each written on 5 October 2026 about the tip `1c6d56f5` in the present tense, gain a dated note saying where the
gap or contradiction they name was answered, so no reader of the ledger meets a closed gap as a current one. FOR THE INTEGRATOR,
on set 33's integrated tree; not applied on fnd/l4k. The ledger's own text of each item is kept as written (history); nothing
is settled by this ledger that a record had not settled first.

  A (K-20): be07863b:v2/docs/records/l4close/REMAINING-ENGINEERING.md:709 "One finding identifier, two findings." Answered by W9
     (fnd/w9l9t5 02b0d30d, merged into set 31 at 0ed29a78): be07863b:v2/docs/records/l9t5/T10-ROUND5.md:227 "renamed from
     L9T5-F26", be07863b:v2/docs/records/l9t5/README.md:196 "The identifier is this finding's alone".
  B (K-21): be07863b:v2/docs/records/l4close/REMAINING-ENGINEERING.md:712 "Two figures for the declared upper bound of the return."
     Answered by W9: be07863b:v2/docs/records/l9t5/README.md:59 "27.9108 A in this one-node model",
     be07863b:v2/docs/records/l8r2/L8R2-KNOWN-DEFECTS.md:1081 "every 'declared upper bound' of this paragraph is that figure".
  C (K-17): be07863b:v2/docs/records/l4close/REMAINING-ENGINEERING.md:714 "The stability condition on the tip read (CO-14)."
     The gap closed at CANDIDATE 3, ac8efbca (5 October 2026 23:04 CEST), which re-took DIGESTS-cr3 with
     be07863b:v2/docs/records/l9t5/stability/DIGESTS-cr3.txt:15 "v2/docs/records/l9t5/l9t5_f01.out pass 1: sha256=2aa78a957e497677"
     (at 1c6d56f5 the same file read 2c590640 there); at the candidate 6bc4424e the file and the connected output's pin read
     2aa78a957e497677, and on main be07863b the pin and the file read f1aa6ae62223e936 (sha256/16, read with git show).
  F (K-15): be07863b:v2/docs/records/l4close/REMAINING-ENGINEERING.md:732 "The P0 list is revision 2 (RE-1)". Revision 3 was
     adopted at 836f711b: be07863b:v2/docs/records/l4close/P0-POWER-LIST.md:1 "revision 3: the state after cx46 and the
     disposition".
  D (K-22) is not touched: its text already says both readings and that neither changes a state (lines 719 to 722).

Each note is appended inside the item's last line (no line moves), in the ledger's own citation form ([ALIAS:N] with aliases of
its table, lines that set 32 does not move: T10R, T5R, L8R2, STAB, P0L) and with quotations found in those files, as
test_remeng's citation and quotation predicates read them; no repository path with a line number in a code span (test_remeng
reads every `v2/...` code span as a path).

Why a script (authority SESSION, W131; reversed by running the four edits by hand on set 33's tree): the ledger is changed by set
32 (fnd/int32 4c8196a0, re-cites at 20 places, among them item G's line 735 to 736); the four lines edited here are not, so each
old text reads the same there. Outputs that move: none (record l4e9's output names the ledger without a digest).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _l4k_apply import run  # noqa: E402

REM = "v2/docs/records/l4close/REMAINING-ENGINEERING.md"

A_OLD = "for the decisions D9 and D10 ([T5R:174-176]).\n- **B. Two figures"
A_NEW = ("for the decisions D9 and D10 ([T5R:174-176]). Dated note, 7 October 2026 (record l4k, the DESK-gate assessment's K-20): "
         "answered on the records' side by W9, merged into set 31 at `0ed29a78`: `T10-ROUND5.md` names the second finding "
         "L9T5-F28, \"renamed from L9T5-F26\" ([T10R:227]), and record l9t5's README says of J_PA's finding \"The identifier is this "
         "finding's alone\" ([T5R:196]); this item is history from `1c6d56f5`.\n- **B. Two figures")

B_OLD = "is the declared peak 1.4749 A ([CON:151]).\n- **C. The stability"
B_NEW = ("is the declared peak 1.4749 A ([CON:151]). Dated note, 7 October 2026 (record l4k, K-21): answered on the records' side "
         "by W9 (merged at `0ed29a78`): record l9t5's README names 27.9108 A the one-node model's ([T5R:59]) and uses the study's own "
         "27.8159 A where the study is meant ([T5R:147]), and record l8r2 states \"every 'declared upper bound' of this paragraph is "
         "that figure\", 27.8159 A ([L8R2:1081]); this item is history from `1c6d56f5`.\n- **C. The stability")

C_OLD = "digests on this tip ([STAB]).\n- **D. The response time"
C_NEW = ("digests on this tip ([STAB]). Dated note, 7 October 2026 (record l4k, K-17): the gap closed at CANDIDATE 3 (`ac8efbca`), "
         "which re-took the digests with `l9t5_f01.out` at `2aa78a957e497677` ([STAB:15]), the file's sha256 and the connected "
         "output's pin at the candidate `6bc4424e`; on main `be07863b` the connected output's pin of `l9t5_f01.out` and the file read "
         "`f1aa6ae62223e936` alike; this item is history from `1c6d56f5`, and cx46's reading of CO-14 stands as given.\n"
         "- **D. The response time")

F_OLD = "while the records carry the cx46 disposition ([T5R:1]).\n- **G. E11-37's"
F_NEW = ("while the records carry the cx46 disposition ([T5R:1]). Dated note, 7 October 2026 (record l4k, K-15): revision 3 was "
         "adopted as the P0 list at set 30's adoption (`836f711b`; its first line, [P0L:1]) and revision 2 kept as dated history in "
         "`v2/docs/records/l4close/P0-POWER-LIST.rev2-2026-10-05.md`; this item is history.\n- **G. E11-37's")

EDITS = [(REM, A_OLD, A_NEW), (REM, B_OLD, B_NEW), (REM, C_OLD, C_NEW), (REM, F_OLD, F_NEW)]

if __name__ == "__main__":
    sys.exit(run("apply_l4k_remeng (K-15, K-17, K-20, K-21)", EDITS))
