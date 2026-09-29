# Integration set 14 (MESHSAT-1357, 29 September 2026)

Branch `fnd/int15`, from main `b874b744`. The checks under `checks/` are AI reviews, not a qualified engineering review.

## What the set carries

- **Stream s120** (`records/s120/`, checked four times): the charge bus VBUS20 bounded at 23.40 V, INFERRED, against
  the 30 V charger FETs. S-120 closed; S-124 opened for the switch nodes, closed only on the prototype.
- **Stream s122** (`records/s122/`, checked three times): the documents CFL-016 names re-read against the netlists.
  - The stale sentences its inventory found are corrected; five more, found by set 14's check, stay with S-122.
  - CONOPS is restored to its baseline text (`c5430071`), with its current values on the status page
    (`handover/DEFINITION-STATUS.md` rows DC-01 to DC-09) and in `feasibility/EMCON.md` section 0a.1.
  - The 20 records bound to the corrected documents are rebound, and ENV-001 is re-pinned.
- **S-122 stays open and CFL-016 reads FAIL on it.** The closure run at `1f3dd306` was dropped: the branch was rewound
  to `9eaf406f` after this set's integration check.

## Checks and answers

| Check | Result | Answered by |
|---|---|---|
| `checks/check-int15-1.md` (the integration check at `1f3dd306`) | not mergeable. B1: five sentences in CFL-016's scope name parts no generator carries, and S-122's inventory does not read part numbers. B2: CFL-016 is not bound to three files its reading rests on. Eight minors. | the rewind; `apply_check15_fixes.py` (B1, B2, m4, m5, m7 into S-122); this README (m1, m2, m6, m8) |
| `checks/check-int15-2.md` (the re-check at `097d2517`) | not mergeable. B1: `close_s122.py` never read S-122's extension and would close it again on the old check, and the extension let a false sentence close as dated. Six minors. | `apply_check15b_fixes.py` (the gate in `close_s122.py`, S-122's title on dated sentences, n3 to n6), this README (n1, n2) |

## Carried from check-int15-1

- **m1:** `9eaf406f`'s commit message describes its pages loosely. The evidence page it committed was a transient
  render, taken while SGN-001 was stale after the coverage file's ENV-001 re-pin. The status writer converges back to
  main's page.
- **m2:** S-120's registry text calls the merged records the "third issue"; they are the fourth.
- **m6:** the rebind entries of `records/s122/apply_registry_s122.py` cut their name lists at 15 without saying so.
- **m8:** a stale date in the coverage file's note beside ENV-001.
- **check-int15-2 n1:** CFL-016's set 14 entry heads the five sentences with the check's own words, "name parts no
  generator carries"; for V2-SPEC.md line 86 the LM5176 is carried, on board A, and the sentence puts it on E6.
- **check-int15-2 n2:** check-int15-1's m3 (S-122 inserted at the head of the closed items) concerned the dropped closure
  `1f3dd306`; nothing on this line closes S-122.
