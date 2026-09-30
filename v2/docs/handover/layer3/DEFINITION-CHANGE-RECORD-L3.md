# Change record: the definition re-issue on the owner's layer 3 answers

**Status: AUTHORISED by owner ruling D-38 (his closure instructions of 30 September 2026); its acceptance is the targeted independent review of layer 3's closure (closure item L3-C27); not yet written into the baselined documents** (closure item L3-C26 of `L3-RECONCILIATION.md`). Written by `v2/docs/records/l3r4/reissue.py` from the owner's rulings on the rows and the records citing them (answers digest `156a2e742bda1892`); the passages, with their baselined and proposed texts, are `DEFINITION-REISSUE-DRAFT.md` (sha256/16 `a04b0a6cc7400635`).

## Why the definition reopens

`handover/DEFINITION-STATUS.md`, the rule: a definition baseline is reopened only when a requirement, the scope, the operating concept or another relevant decision changes, and the affected document is issued again with the change stated in it. The owner's rulings below restate requirements `CONOPS.md` and `PRODUCT-BRIEF.md` trace to.

## M1 as the registry reads it

Requirement REQ-072, part of prototype 1's core, reads FAIL (DESK_REVIEW, SCHEMATIC phase) when this re-issue is written: the design as it stands does not meet M1's runtime objective (design risk DR-01, layer 4); its current reading is kept in the requirements registry and `handover/DEFINITION-STATUS.md`.

## The answers and the records each ruling is cited by

| Row | Option | Owner ruling | Ruled on | Records citing the ruling (the registry) | Passages it changes |
|---|---|---|---|---|---|
| L3-OD7 | `objective-48-72` | D-32 | 30 September 2026 | REQ-072 | S01, S02, S03, S04, S05, S06, S09, S10 |
| L3-OD2 | `both-kept` | D-33 | 30 September 2026 | none | S07, S08 |
| L3-OD3 | `unchanged` | D-34 | 30 September 2026 | none | none |
| L3-OD4 | `reject` | D-35 | 30 September 2026 | none | none |
| L3-OD5 | `layer4-obligation` | D-36 | 30 September 2026 | REQ-051, CFL-017, FEA-008 | S11, C29, B18 |
| L3-OD6 | `mean-day` | D-37 | 30 September 2026 | none | S03 |

Every answer also changes the head of both documents (C01, C02, B01, B02) and section 7's table of rulings (C31).

## The passages restated

| Passage | Document | Lines | What | Baselined sha256/16 | Proposed sha256/16 |
|---|---|---|---|---|---|
| C01 | `v2/docs/CONOPS.md` | 3 | the status line of the head | `d2ebde05859b59a3` | `83f1a8263da7bcee` |
| C02 | `v2/docs/CONOPS.md` | 15 to 16 | the head, after the rule of reopening: the re-issue note | `17f4068da8551b4b` | `57a071ab96dec672` |
| S07 | `v2/docs/CONOPS.md` | 67 | section 1, the local end users: the lid tablet | `1e10aa523ffc2762` | `eedb85dbba916163` |
| S01 | `v2/docs/CONOPS.md` | 152 | section 3, M1's title | `3ed5b6263e2d595b` | `cdd513334e10f26e` |
| S02 | `v2/docs/CONOPS.md` | 163 to 165 | section 3, M1's duration and who set it | `af711941076494cf` | `4945e4adaa3b1933` |
| S03 | `v2/docs/CONOPS.md` | 167 to 198 | section 3, M1's energy: the objective, its profile and the modelled baseline | `1b8e56e02d353d0b` | `861400df30f46f3e` |
| S04 | `v2/docs/CONOPS.md` | 215 to 216 | section 3, M1: the owner's instruction D-20 | `bf2301d0fd240158` | `22bff144c089a085` |
| S11 | `v2/docs/CONOPS.md` | 321 | section 4, the Storage row: D-02a's storage margins against the current cell | `8e98c8939573240e` | `99a5541b316c2b79` |
| S05 | `v2/docs/CONOPS.md` | 1019 to 1024 | section 6, missions longer than the pack and M1's night | `035db3d5c5131ba6` | `649d151078b2417a` |
| C29 | `v2/docs/CONOPS.md` | 1040 | section 7, the D-02a row | `3c076635f1ef2a1a` | `7ddc446c82bed290` |
| C31 | `v2/docs/CONOPS.md` | 1062 | section 7, the D-20 row and the owner's rulings on layer 3 | `865fafb8d009d98d` | `ee8f01e288acc07e` |
| S06 | `v2/docs/CONOPS.md` | 1101 | section 7a, M1's mission duration row: its reversal | `085c5c6bbf7c0d91` | `efd2814b37c36c0f` |
| B01 | `v2/docs/PRODUCT-BRIEF.md` | 3 | the status line of the head | `9d9f6e8a4b043ed8` | `75c75b47f0d9eb18` |
| B02 | `v2/docs/PRODUCT-BRIEF.md` | 15 | the head, after the rule of reopening: the re-issue note | `6d236db6cc886fa1` | `01cf992b81acca01` |
| S08 | `v2/docs/PRODUCT-BRIEF.md` | 60 | who it is for, the local end users: the tablet in the lid | `991b95ed81f773a3` | `42c1b17959007343` |
| S09 | `v2/docs/PRODUCT-BRIEF.md` | 171 to 179 | what it is not today: the night on the pack and solar input | `164fc509876b28aa` | `1e494ddb0dfb6873` |
| B18 | `v2/docs/PRODUCT-BRIEF.md` | 207 to 209 | what the first prototype has to show: the qualification margins | `cde649c9ed471b2a` | `ac61323fa8974cb2` |
| S10 | `v2/docs/PRODUCT-BRIEF.md` | 309 | the open items table: L-02, M1's duration | `3f5aee2712acbc17` | `c5919bc95fce9fb9` |

## What the re-issue does not restate

M1's reading: `handover/DEFINITION-STATUS.md`'s current values gain the row DC-L3-M1, carrying REQ-072's reading as the draft proposes it.

Row L3-OD1's store is layer 4 architecture (the closure, D-21 and D-28): D-06's one pack stands, and the passages that state it stay as baselined.

## The documents

| Document | Baselined sha256/16 | Proposed sha256/16 |
|---|---|---|
| `v2/docs/CONOPS.md` | `6cb7b241cb84d729` | `92f9425e8d31924b` |
| `v2/docs/PRODUCT-BRIEF.md` | `85513b92ed0daf55` | `7052556f8f35ae7f` |

## Approval

**Authority:** owner ruling D-38, the owner's closure instructions of 30 September 2026, quoted word for word in `handover/layer3/OWNER-INSTRUCTION-2026-09-30.md`: the affected CONOPS and product-brief passages are generated from his choices and accepted by one targeted acceptance review, without a further review from him (the session's reading, labelled as such there); this record restates exactly the passages his rulings on the rows change and nothing beyond them. **Acceptance:** the targeted independent review of layer 3's closure (L3-C27), filed in `handover/layer3/l3r2.yaml`'s `independent_check`. **Filing:** `handover/layer3/l3r2.yaml`'s `definition_reissue` names this record with its sha256/16 and that ruling (`{record, sha16, approved_by}`); the ruling does not change the answers digest, so this record and its draft stay current, and `reissue.py` never rewrites them once `definition_reissue` is filed. **The baselined documents:** the proposed texts are written into `CONOPS.md` and `PRODUCT-BRIEF.md` by their re-stamp through layers 1 and 2 (closure item L3-C63), a follow-on of this closure; until then, where either document differs from this record, this record governs, and `handover/DEFINITION-STATUS.md` says so.
