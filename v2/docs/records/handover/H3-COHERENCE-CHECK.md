<!-- Filed by the integrating session on 27 September 2026 (MESHSAT-1357) from the checker's own working folder, byte for byte below this line (sha256/16 of the checker's file: ea23c187b793a0ba). The checker worked from its own extraction of H3.zip and the dependencies the package declares, in workflow run wf_7bec9c82-e4c. An AI check, never a qualified engineering review. -->

# AI check

## Narrow coherence check of layers 1 to 3 of handover snapshot H3 (MESHSAT-1357)

This is an AI check by one AI session that built none of H3 and wrote none of its pages. It is not a qualified
engineering review, it replaces no review a record requires, and it says nothing about whether any circuit is right.
Nothing of this kit has been built, ordered or measured.

| Item | Value |
|---|---|
| Package | `H3.zip`, 52,187,825 bytes, 2275 entries |
| sha256 | `6922a96d732442e99a65d8db3f0734378bd7ea636894fca283a4b3ca424dd07a` |
| Source commit (SOURCE.txt) | `75ad6ee5bc98d7213b9a61d1f64cfa7ea19cc669`, marked `public yes` |
| Date of this check | 27 September 2026, 21:20 to 21:50 UTC (`date -u` read at the start: Sun Sep 27 21:20:49 UTC 2026) |
| Working folder | `/home/claude-runner/worktrees/meshsat-fieldkit/_h3check/coherence` (the ZIP, its `.sha256`, the extraction `H3/`, my outputs under `work/`) |
| Host | the shared runner, Python 3.11.2, PyYAML 6.0.3, no KiCad. The rented KiCad host was not used and no folder was made on it |

**Scope.** This is not a new review of the three layers. It asks one thing: does what the package says about layers
1, 2 and 3 agree with itself and with the files the package carries.

**Result.** No blocking finding. Thirteen minor findings (section 9) and three observations. The statements of
status, baseline commit and review record for layers 1, 2 and 3 agree across every page I was told to read, every
quoted hash of a file the package carries matches that file, every quoted hash of an older file matches the public
repository at the commit the page names, and the registry's counts match every page and the filed count record. The
one place where a current page contradicts layer 3's status without a mark is a fixed sentence of the generated
evidence page (finding m1).

## 1. What I read

From the extraction `H3/` only, plus the declared dependency named in section 2:

- `SOURCE.txt`, `MANIFEST.tsv`, `EXCLUDED.tsv`, `REFERENCED-SOURCES.tsv` (tables read by script).
- `START-HERE.md` in full.
- `LAYER-STATUS.md`: lines 1 to 298 in full (head, "Status at handover H3", "Status at handover H2", "Status at
  handover H1", the summary at `e3aedb25`, the sections of layers 1, 2 and 3 with their acceptance tables), and the
  integrator lines of layers 1, 2 and 3 (lines 542, 684, 836), start and end. Appendix A otherwise by search only.
- `CONTINUATION-BRIEF.md` lines 1 to 160 and by search; `ENGINEERING-QUESTIONS.md` head, index and EQ-27 to EQ-30 in
  full; `GLOSSARY.md` by search; `REGENERATE.md` lines 1 to 172 and section 7's table.
- `v2/docs/handover/RELEASE-H3.md` and `DEFINITION-STATUS.md` in full; the head of `H2-RESPONSE.md`.
- `v2/docs/PRODUCT-BRIEF.md`: head, "What it is not, today" to the appendix head, appendix A1. `v2/docs/CONOPS.md`:
  head, headings, appendix A1, and every line naming REQ-072, REQ-077 or HOT-R1.
- `v2/ecad/tools/pcb_requirements.yaml`: the header comment in full (lines 1 to 277), then parsed with PyYAML.
- `v2/docs/REQUIREMENTS-TRACE.md`: head and summary tables, and the entries of REQ-072, REQ-077, CON-010, REQ-052,
  CON-026 (read by script).
- `v2/docs/EXECUTION-PLAN.md`: lines 1 to 100 and the two checkpoints of 27 September (18:30 and 23:02 CEST).
- `v2/docs/CURRENT-EVIDENCE.md` lines 1 to 40.
- Review records under `v2/docs/reviews/`: `TARGETED-RECHECK-LAYER-3-2026-09-27.md` and
  `DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md` in full; the verdict sections and acceptance tables of the three second
  release checks; the headings of all thirteen layer records; sections 1 to 6 of
  `2026-09-27-h2-independent-review.md`.
- `v2/docs/records/h3/`: `design_difference.py` (lines 1 to 140), `design_difference.out`, `handover_counts.out`,
  `public_check.out`; `v2/docs/records/README.md` (rows read by script).
- For the errata: the heads of the seven layout constraint sheets and their README, `A.md` section 7,
  `v2/ecad/tools/boards/a.json` (`external_ports`), board A's committed netlist (parsed), `PCB-RULE-STATUS-A.md` by
  search.

## 2. What I ran, with the exact result

All commands ran in my working folder. Tools that write were run in a copy of the extraction (`work/H3run`, removed
at the end) with `VERDICT_DIR` pointed outside it and `PYTHONDONTWRITEBYTECODE=1`; `H3/` itself was verified
unchanged at the end.

| # | Command | Result |
|---|---|---|
| 1 | `sha256sum -c H3.zip.sha256` | `H3.zip: OK` |
| 2 | from `H3/`: `python3 v2/ecad/tools/handover_pack.py verify ../H3.zip` | `handover_pack: verify ../H3.zip: OK`, exit 0. The packer runs from the extraction |
| 3 | from `H3/`: `python3 v2/ecad/tools/handover_pack.py verify .` (run twice, before and after the other checks) | `handover_pack: verify .: OK`, exit 0, both times |
| 4 | my own comparison of every file of `H3/` with `MANIFEST.tsv` | 2275 files on disk, 2274 manifest rows, the one extra file is `MANIFEST.tsv`; 0 missing; 0 sha256 mismatches |
| 5 | from `H3/`: `python3 v2/ecad/tools/sch_prov.py read v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net p` | `sch_prov: pcb-p-pack.net was written by this tree's own generator (ee62fdb195a9f217)` |
| 6 | from `H3/`: `python3 v2/docs/records/h3/handover_counts.py`, compared with the filed `handover_counts.out` by `cmp` | exit 0, nothing on stderr, 7965 bytes, byte-identical. `git status` in that folder answers "not a git repository", so the script needs no git |
| 7 | PyYAML parse of the registry, my own counts | 19 needs; 144 records (REQ 77, CON 26, CFL 18, ASM 7, FEA 7, SPD 6, CHO 3; by `kind`: requirement 77, constraint 26, conflict 18, assumption 7, feasibility 7, superseded 6, choice 3); 29 owner rulings; 63 session choices SC-01 to SC-63; 58 open items (SESSION 50, LATER 6, OWNER_ACTION 1, CONDITIONAL 1); 53 closed items; no id in both lists. `evidence_result`: PASS 21, FAIL 15, INCONCLUSIVE 14, NOT_JUDGED 80, NOT_YET_TESTED 8, NOT_APPLICABLE 6 |
| 8 | sha256 (first 16 hex digits) of the thirteen layer records, the two saved outside reviews, `PRODUCT-BRIEF.md`, `CONOPS.md`, `pcb_requirements.yaml`, `REQUIREMENTS-TRACE.md`, `DEFINITION-STATUS.md`, `CURRENT-EVIDENCE.md` | section 4 |
| 9 | a scan of sixteen pages for every 16-hex value quoted within 160 characters of a layer 1 to 3 file name, each compared with the sha256/16 of every file in `MANIFEST.tsv` | 37 values: 23 are the hash of a file the package carries, 14 are not, and each of the 14 is explained where it stands as the hash of the file at an earlier commit (section 4) |
| 10 | every `evidence_bound_to` entry of the registry against the package's files | 121 bindings: 118 match the file carried, 0 stale, 3 name CON-017's ST documents, which the package references and does not bundle |
| 11 | in the copy: `python3 v2/ecad/tools/rules_lib.py requirements` | exit 1, `rules_lib: 144 requirement record(s), 13 error(s), 20 warning(s)`. Every error names a maker document that is referenced and not bundled. 21 lines begin `warn`: 20 closed-by-commit checks and one line on `out/rule-audit` |
| 12 | in the copy: `python3 v2/ecad/tools/rules_render.py --requirements --check` | exit 1, `REQUIREMENTS-TRACE.md REFUSED: pcb_requirements.yaml does not validate (13 error(s))`, as START-HERE section 6 says for the ZIP alone |
| 13 | in the copy: the code block of REGENERATE.md section 1a for the validator's documents | `REF=75ad6ee5`; eleven files fetched, 59,946,127 bytes, every line `OK` by git blob sha |
| 14 | after 13: the validator and the trace check again | `rules_lib: 144 requirement record(s), 0 error(s), 20 warning(s)`, exit 0; `rules_render: v2/docs/REQUIREMENTS-TRACE.md is current`, exit 0 |
| 15 | in the copy: `python3 v2/docs/layout-constraints/calc/rail_widths.py --markdown`, compared with the filed `rail_widths.out` | byte-identical (without `--markdown` the script prints JSON, which is not the filed form) |
| 16 | my own parse of board A's committed netlist (sha256/16 `da05dc02bc1e612f`) and of `boards/a.json` | section 8, erratum f |
| 17 | `git ls-remote https://github.com/meshsat/meshsat-fieldkit.git` at 21:32 UTC | `refs/heads/main` is `bd96bb614ff000cca446df69091bbd2f6117589f` |

**Declared dependency used: the public repository.** SOURCE.txt and REGENERATE.md section 1 name
`https://github.com/meshsat/meshsat-fieldkit` and its raw file URL, and SOURCE.txt marks the commits below
`public yes`. I fetched from it, and from nowhere else:

| # | What | Result |
|---|---|---|
| 18 | `v2/release/handover/H2.MANIFEST.tsv` at `75ad6ee5` (listed in `EXCLUDED.tsv` with blob `c880d0f4...`) | HTTP 200, 755,733 bytes, git blob sha equal to the one `EXCLUDED.tsv` gives |
| 19 | the H2 manifest against H3's, row by row | 2233 rows against 2274; 41 added, 0 removed, 41 changed. Outside `v2/docs/` and the root pages the differences are: added `v2/cad/render/scene.py`; changed `v2/ecad/tools/handover_pack.py`, `tools/tests/test_handover_pack.py`, `tools/pcb_requirements.yaml`, `tools/pcb_interfaces.yaml`, `pcb-e5-block/routed/interfaces_e5.verdict.json`, `README.md`, `v2/README.md`. The thirteen layer records: eleven byte-identical in H2 and H3, two new in H3 |
| 20 | sixteen files at the commits the pages name (section 4) | every quoted hash reproduced |
| 21 | GitHub commit API for `75ad6ee5` | it changes five files, all under `v2/docs/records/h3/`: `design_difference.out`, `design_difference.py`, `public_check.out`, `same_patches.out`, `zip_size_estimate.out`. Parent `089f7f27` |
| 22 | GitHub compare API `b89b50b4...75ad6ee5` | ahead by 25 commits, 82 files. Outside `v2/docs/`: the two overviews, INT-001's seven `routed/` readings, the packer and its test, the two registries, and H2's three snapshot files. The same list as `design_difference.out` |
| 23 | GitHub commits API, last commit that changed each of sixteen files, as of `75ad6ee5` | all sixteen equal the commit RELEASE-H3.md gives beside the file |
| 24 | the registry, the trace, `RELEASE-H3.md`, `H3.zip.sha256` and `H3.MANIFEST.tsv` at `bd96bb61` | observation O1 |

## 3. Every statement of status, baseline and review record, layers 1 to 3

| Source | Layer 1, product definition | Layer 2, concept of operations | Layer 3, requirements |
|---|---|---|---|
| START-HERE, opening and section 1a | COMPLETE; baselined at `6b2a9965`; re-stamped BASELINED at `a9f212c7`, no definition change, CONTENT_PRESERVED | COMPLETE; `79963b3b`; re-stamped at `a9f212c7` | COMPLETE since `24e7bf5a`; BASELINED at `a54b793b`, written in `2c12be91`; re-check B-1 CLOSED at `2c12be91`; S-51, S-78, S-80 closed; H3 is item 3.18; S-79 still open in the registry carried |
| START-HERE section 3 (H2's, with **H3** marks) and section 5 | COMPLETE, BASELINED (`6b2a9965`), H3 mark for the re-stamp; "COMPLETE since H2" | COMPLETE, BASELINED (`79963b3b`), H3 mark; "COMPLETE since H2" | "IN_PROGRESS in H2. H3: COMPLETE since commit `24e7bf5a`"; "COMPLETE in H3", BASELINED at `a54b793b` |
| LAYER-STATUS, head and "Status at handover H3" | COMPLETE; baseline stays `6b2a9965`; brief `85513b92ed0daf55` | COMPLETE; baseline stays `79963b3b`; CONOPS `6ebe6760c4312bca` | COMPLETE since `24e7bf5a`; as START-HERE; 144 records, 58 open, 53 closed |
| LAYER-STATUS "Status at handover H2" | COMPLETE since `6b2a9965`, four records named, H3 mark | COMPLETE at `79963b3b` (recorded in `62f26a44`), four records named, H3 mark | COMPLETE in the commit that files the re-check, `24e7bf5a` (after H2); five records named; item 3.18 "the next snapshot, H3", H3 mark |
| LAYER-STATUS, the layers' own sections | "At H2: COMPLETE ... H3: COMPLETE"; items 1.1 to 1.12 all MET | same; items 2.1 to 2.17 all MET | "After H2: COMPLETE ... At H2: IN_PROGRESS"; 3.14 "OPEN at H2; MET since after H2"; 3.15 "MET in substance"; 3.18 "OPEN at H2; met by H3" |
| LAYER-STATUS "Status at handover H1", summary at `e3aedb25`, Appendix A | IN_PROGRESS then, each section headed as history | same | same |
| CONTINUATION-BRIEF, head and section 0 | COMPLETE, BASELINED in `6b2a9965` | COMPLETE, BASELINED at `79963b3b` | "In H2 layer 3 was IN_PROGRESS"; "H3: ... COMPLETE since commit `24e7bf5a`", same commits; S-79 explained |
| ENGINEERING-QUESTIONS index | EQ-27 answered, brief BASELINED, layer 1 COMPLETE | EQ-29 answered for layers 1 and 2 by H2 | EQ-28 and EQ-30 answered; EQ-29: "S-79 stays open until a snapshot is cut ..., and the snapshot is H3" |
| RELEASE-H3 | COMPLETE; `6b2a9965`, `a9f212c7`; five records by hash | COMPLETE; `79963b3b`, `a9f212c7`; five records by hash | COMPLETE since `24e7bf5a`; `a54b793b` (file there `c8fded5cb0a165d6`), `2c12be91`; file carried `6eb35694e300abff`; five records by hash |
| DEFINITION-STATUS | BASELINED at `a9f212c7`, re-stamped; first baselined at `6b2a9965` | BASELINED at `a9f212c7`, re-stamped; first baselined at `79963b3b` | not its subject |
| PRODUCT-BRIEF and CONOPS, status paragraphs | "BASELINED at `a9f212c7`", text baselined at `6b2a9965` | "BASELINED at `a9f212c7`", text baselined at `79963b3b` | |
| The registry | | `needs_document_sha256` is the sha256 of the CONOPS carried | `baseline_state: "BASELINED at a54b793b"`; `baseline_reviews`: five records, five hashes |
| REQUIREMENTS-TRACE | | pin `6ebe6760c4312bca` | "Registry state **BASELINED at a54b793b**"; 144, 19, 29, 63, 58 open, 53 closed |
| EXECUTION-PLAN, checkpoint 23:02 CEST | COMPLETE | COMPLETE | COMPLETE |
| GLOSSARY | definition baseline `6b2a9965` | `79963b3b` | `a54b793b`; "H3 is H2's design with layer 3 released" |
| SOURCE.txt | | | 144 records, 58 open, 53 closed; all the commits above are `public yes` and in history |
| CURRENT-EVIDENCE (generated, H2's file) | | | "the requirements and architecture baselines are still open": finding m1 |

Older statements (layer IN_PROGRESS, `READY_FOR_REVIEW_B`, CANDIDATE, DRAFT) stand only in sections, appendices or
records that the package marks as history where they stand, with two kinds of exception: the "Exact issue" rows of
EQ-28 and EQ-29, which erratum d covers and whose index rows and attempts rows give the newer state, and finding m1.

## 4. Hashes

**Files the package carries, sha256 first 16 hex digits, computed here.** Every one equals every value the pages,
the registry and `handover_counts.out` quote for it.

| File | sha256/16 |
|---|---|
| `v2/docs/PRODUCT-BRIEF.md` | `85513b92ed0daf55` |
| `v2/docs/CONOPS.md` | `6ebe6760c4312bca` (equal to the registry's `needs_document_sha256`) |
| `v2/ecad/tools/pcb_requirements.yaml` | `6eb35694e300abff` |
| `v2/docs/REQUIREMENTS-TRACE.md` | `88ef20b14e1ee12e` |
| `v2/docs/handover/DEFINITION-STATUS.md` | `0ac85070530ef7a6` |
| `v2/docs/CURRENT-EVIDENCE.md` | `7a834fe55aea6ccd` (the same in H2's manifest) |
| `REVIEW-A-LAYER-1-2026-09-27.md` | `d469a268fe0b8768` |
| `REVIEW-LAYER-1-RELEASE-2026-09-27.md` | `2bd065d12f50298d` |
| `REVIEW-LAYER-1-RELEASE-2-2026-09-27.md` | `a0d8e6be2dcebcf6` |
| `REVIEW-A-LAYER-2-2026-09-27-pass1.md` | `e854c2a46ea3d542` |
| `REVIEW-A-LAYER-2-2026-09-27.md` | `77b20ca4042f0855` |
| `REVIEW-LAYER-2-RELEASE-2026-09-27.md` | `cb7c773b9b193e1f` |
| `REVIEW-LAYER-2-RELEASE-2-2026-09-27.md` | `a4f0e88e48c304ee` |
| `REVIEW-B-LAYER-3-2026-09-27.md` | `7a6c679f446b1baa` |
| `REVIEW-LAYER-3-RELEASE-2026-09-27.md` | `1c3bc2d99f9efb51` |
| `REVIEW-LAYER-3-RELEASE-2-2026-09-27.md` | `cf8c73fb288be2fb` |
| `TARGETED-CHECK-LAYERS-1-3-2026-09-27.md` | `ae70b1a7811ecea1` |
| `TARGETED-RECHECK-LAYER-3-2026-09-27.md` | `7831358b96b6f5ca` |
| `DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md` | `4c09af64cb214448` |
| `2026-09-27-h2-independent-review.md` | `58e9142de8e085f0` (no page quotes a hash for it) |
| `2026-09-27-third-checkpoint-review.md` | `7db0b9157fa5cc75` (no page quotes a hash for it) |

Every one of the thirteen layer records is headed "AI review" or "AI check" with "not a qualified engineering
review", as START-HERE says.

**Quoted hashes that match no file of the package.** Each is explained by the page as the file at an earlier commit.
Where that commit is public I fetched the file and hashed it.

| Quoted | Where | The page's explanation | Reproduced on the public repository |
|---|---|---|---|
| `d36bf76b3dea8b30` | RELEASE-H3, DEFINITION-STATUS | the brief at `6b2a9965`, the file H2 carries | yes, and it is the brief in H2's manifest |
| `c1bb3fe5e082b57e` | registry S-77, trace, brief appendix A1 | the brief at `cecfd0f1` | yes |
| `026d9ab493d35ed8` | DEFINITION-STATUS | the brief at `a9f212c7` | yes |
| `4483209659dc391c` | RELEASE-H3, DEFINITION-STATUS | CONOPS at `62f26a44`, the file H2 carries | yes, and it is CONOPS in H2's manifest |
| `3ff59edc96a3f8f4` | CONOPS appendix A1, DEFINITION-STATUS | CONOPS at `79963b3b` and at `eb9f9030` | yes at `79963b3b`; `eb9f9030` is not public (HTTP 404, as SOURCE.txt marks it) |
| `bbcab7c9876f7993` | DEFINITION-STATUS, records README | CONOPS at `a9f212c7` | yes |
| `c8fded5cb0a165d6` | RELEASE-H3, registry S-51, S-78, S-80 | the registry at `a54b793b` | yes |
| `0c87f065a2c9defd`, `58b77b5d15b2fc7d`, `9a3aed63341c8eaa` | the re-check record, the registry header, `design_difference.out` | the registry at `2c12be91`, `3e4799eb`, `ef144760` and `b89b50b4` | yes, all four |
| `285612fedd4cf81d`, `8896c5caeb246d30` | registry S-78 and S-80, the re-check record | the trace page at `a54b793b` and at `2c12be91` | yes, both |
| `fb819e939f2895da`, `6351a72c7966c4b9` | registry header | the registry and CURRENT-EVIDENCE at `eb9f9030` | not checkable: the commit is not public |
| `ab9b3ec1e590a41a` | registry header, LAYER-STATUS, records README | the re-check record as its checker wrote it, before one phrase was rewritten at filing | not checkable: that copy is not in the package |
| `f09185c8635af1d4`, `b9080983ccc03a84`, `acd19f7bfc50b7ad`, `6788c517b898c86a`, `49119f89f2d98920` | LAYER-STATUS Appendix A, registry evidence entries | files at `b69f20db`, `9a151c78`, `a6f87e9d` and at board A's round 8, in tables headed as the audit at `e3aedb25` or in dated evidence entries | not fetched: history, marked as such |

No quoted hash for a layer 1 to 3 file is left unexplained. The unexplained hashes I found are those of finding m2,
which concern five records of `v2/docs/records/h3/`, not a layer record.

## 5. The registry and the counts

My counts (section 2, row 7) equal, figure for figure: START-HERE section 4 ("19 needs, 144 records (REQ 77, CON 26,
CFL 18, ASM 7, FEA 7, SPD 6, CHO 3), 29 owner rulings, 63 session choices (SC-01 to SC-63), 58 open and 53 closed
items, counted for H3"), LAYER-STATUS "Status at handover H3" ("144 records, 58 open and 53 closed items"),
SOURCE.txt, the head of REQUIREMENTS-TRACE.md (which also gives the same counts by status, by evidence result and by
release effect as my parse), and `handover_counts.out` (needs 19, records 144, rulings 29, choices 63, open 58,
closed 53, open by class CONDITIONAL 1, LATER 6, OWNER_ACTION 1, SESSION 50, and the same 58 open ids in the same
order). `handover_counts.py` reproduces its filed output byte for byte without git.

H2's figures, "60 open and 50 closed at H2", are those of the registry at `b89b50b4` as I parsed it from the public
repository. The difference of H2's and H3's count records is what START-HERE section 3 says it is: the registry's
state and items, the two definition documents' hashes and the review records listed; no count of the design.

My own field by field comparison of the registry, taken from the public repository at each commit:

| From | To H3's file | What differs |
|---|---|---|
| `a54b793b`, the baselined file | `6eb35694e300abff` | `baseline_state` and `baseline_reviews`; `needs_document_sha256`; S-51, S-78, S-80 moved from open to closed; S-79's title; `evidence` and `evidence_bound_to` of REQ-005, CFL-014, CFL-016. No need, ruling or choice; no other field of any record |
| `b89b50b4`, H2's source | same | the same, with S-81 added and CON-010's `evidence` |
| `24e7bf5a`, where layer 3 is called COMPLETE | same | `needs_document_sha256` and the three rebound readings only |

This is what RELEASE-H3.md and `design_difference.out` state.

## 6. Layer 3's completeness as the package defines it

LAYER-STATUS defines COMPLETE as acceptance items met, the required review held and a versioned package.

- **Acceptance items.** In the tables of layers 1 and 2 every item reads MET. In layer 3's table three rows are not
  a plain MET: 3.14 ("OPEN at H2; MET since after H2 (`2c12be91`, re-check B-1 CLOSED)"), 3.18 ("OPEN at H2; met by
  H3") and 3.15 ("MET in substance", "the letter is not met (n7: open items in no record's `waits_on`)"). For 3.15 the
  package says why it does not hold the layer: the second release check classed n7 as a minor finding, and the H2
  row lists "the release-2 record's minors n2 to n9" as "Carried, not holding it". See finding m6 for what the table
  does not say. No item of layers 1 to 3 reads PARTLY.
- **The review.** The re-check record is limited to B-1 and says so ("Out of scope, and not judged: ... S-79 (the
  package)"). Its result, B-1 CLOSED at `2c12be91` with seven PASS rows, is quoted correctly by every page. The pages
  call it an AI check each time.
- **The package, item 3.18, and S-79.** A reader of the ZIP alone is told clearly. START-HERE section 1a, LAYER-STATUS
  "Status at handover H3", CONTINUATION-BRIEF section 0 and RELEASE-H3.md each say that H3 is the package, that the
  registry inside it still lists S-79 as open, and why ("it is closed in the commit that files the snapshot, after
  the build"). S-79's own title in the registry says "the package is the next snapshot, H3, ... and this item closes
  with it". The condition S-79 states is met by what I hold: a snapshot whose SOURCE.txt names a commit that is
  public (the public repository serves files at `75ad6ee5`) and whose history carries `a54b793b`, `2c12be91` and
  `24e7bf5a`. What the ZIP cannot give is the id of the filing commit; on the public repository it is `bd96bb61`,
  whose registry differs from H3's in one thing only, S-79 moved to the closed items with `closed_by: commit
  75ad6ee5` (observation O1). Points of use that are generated or were not edited for H3 (the open items table of
  REQUIREMENTS-TRACE.md line 3579, EQ-29, SOURCE.txt's "open items: 58") show S-79 open with no note; each agrees
  with the registry inside the ZIP.

## 7. Defined but unmet requirements stay visible, and none is lowered

- The registry reads REQ-072 `evidence_result: FAIL`, core, BLOCKER, waiting on S-53 and M-02; REQ-077 FAIL, core,
  BLOCKER, waiting on S-57 and S-58. The trace page shows both as "FAIL at SCHEMATIC; PROTOTYPE not yet judged".
  CON-010, REQ-052 and CON-026 also read FAIL. Fifteen records read FAIL in all.
- The definitions keep the failures in their maintained text: PRODUCT-BRIEF "What it is not, today" ("requirement
  REQ-072, part of prototype 1's core, reads FAIL at desk"); CONOPS M1 (line 188), section 4c (lines 732 to 734, "the
  requirement reads FAIL on the generated boards until then") and section 7a (HOT-R1 row, line 1104).
- The handover pages say it: START-HERE section 1a ("They do not claim that the design meets a requirement: where it
  does not (REQ-072 reads FAIL at desk, for one), the registry says so"); LAYER-STATUS layer 3 row ("REQ-077 FAIL
  until HOT-R1 (S-57)"); RELEASE-H3 (REQ-072 and CON-010); EQ-13 and EQ-22 in the index.
- I searched every `.md`, `.yaml` and `.txt` file of the package for a line that names REQ-072 or REQ-077 together
  with PASS, met, closed or satisfied, and read each hit. None presents either requirement as met. The hits are the
  review records' rows on other matters, the test plan's pass rules ("A step that did not act reads NOT_VERIFIED for
  REQ-077, never PASS") and history.
- Nothing is lowered: between H2's registry and H3's no record's statement, acceptance, allocation, verification or
  release effect differs (section 5), so REQ-072 still asks 72 hours and REQ-077 still asks the stop before +60 C.
  M-02 says "neither REQ-016 nor REQ-072 is restated to fit".
- The figure "about 270 W" (S-53, REQ-016's notes) against "about 266 W" (the brief, EQ-13) is already recorded by
  the package as a carried minor (LAYER-STATUS line 542, R2-m7). Not a new finding.

## 8. "H3's design content is H2's", and the errata

**The sentence.** `design_difference.out` lists 82 files that differ, none in a class marked DESIGN or TOOL: 3 files
of the H2 snapshot, 7 tracked INT-001 readings (each PASS to PASS), the packer and its test, two registries, 66 pages
and records under `v2/docs`, 2 overviews; 31 schematic, netlist, intent and provenance files compared and the same;
the six exports name the schematic and netlist carried. It supports the sentence. Three independent checks agree
with it (section 2, rows 19, 21 and 22). Two limits are findings m3 and m10: the record stops one commit short of
the snapshot's source, and the wording.

How the sentence is worded, place by place:

| Place | Names the packer's change |
|---|---|
| START-HERE section 1a, lines 106 to 111 | yes: "the packer and its test" |
| LAYER-STATUS lines 80 to 83 | yes |
| REGENERATE.md "Edition H3", lines 48 to 53 | yes, with its commit `a54b1f4d` |
| RELEASE-H3.md, section "H3's design content equals H2's" | yes, with a table |
| START-HERE opening, lines 24 to 25 | no, but it points to section 1a. True as worded: "checking tool" |
| CONTINUATION-BRIEF lines 18 to 19; EXECUTION-PLAN line 263 | no. True as worded: "checking tool" |

**The errata of START-HERE section 1a.**

| # | Is the defect real in the package | Does the point of use say enough |
|---|---|---|
| a | Yes. Each of the seven constraint sheets opens by saying what was re-read at the H2 line and that "Every other line below is the reading at `e3aedb25`". The power tables are current: `rail_widths.py --markdown` on the intents carried reproduces the filed output byte for byte | Yes. The mark is at the head of each sheet, and `A.md` section 7 carries the corrected row marked "corrected for H3 from the committed netlist" |
| b | Yes. `LAYER-STATUS.md` is 295,964 bytes, with Appendix A from line 446 | Yes. The page's head says which section is current and which are history |
| c | Stated in REGENERATE.md section 9 (line 525). Not run by me | Yes |
| d | Yes. The five blocks carry "Corrected for H3" where they stand (EQ-01, EQ-04, EQ-10, EQ-16, EQ-17), seven marks with the head and the index. EQ-28's and EQ-29's "Exact issue" rows still speak in the present of a state that has passed, which is what the erratum warns of; their attempts rows and the index give the newer state | Yes, through the page's head and the index |
| e | Cannot be checked from the package: `a76a246e` and `760d7f41` are marked `public no`, not in history. The package presents set 6 as not evidence | Yes |
| f | Yes. `boards/a.json` declares `J_DOCK` pins 1 and 2. In the committed netlist `J_DOCK` pins 1 to 7 and 11 are GND, 8 is SHORE_INHIBIT, 9 and 10 the USB pair, 12 DOCK_SPARE; VIN_RAW is on `J_VR1` to `J_VR4` pin 1, D2 pin 1, C11, C12, D19, Q2 pin 5, R14, R195, R196, R200 and TP13; `J_VN1` to `J_VN4` and D2 pin 2 are GND. This is what `A.md` section 7 says, net for net | In START-HERE and in `A.md` section 7, yes. Not in LAYER-STATUS items 8.10 and 8.14 or in the generated rule page: finding m11 |

## 9. Findings

### BLOCKING

None.

### MINOR

**m1. The generated evidence page still says the requirements baseline is open.**
`v2/docs/CURRENT-EVIDENCE.md` lines 8 to 9: "The foundations are incomplete because the requirements and
architecture baselines are still open (review of 26 September 2026, section 6 item 1), whatever this page counts."
The sentence is fixed text of `v2/ecad/tools/rules_render.py` lines 1408 to 1409, so it does not follow the registry.
The registry reads `baseline_state: "BASELINED at a54b793b"` and every handover page calls layer 3 COMPLETE. No page
marks the sentence and it is not among the errata, although START-HERE, LAYER-STATUS and EXECUTION-PLAN quote this
page's headline as current. Why I class it minor and not blocking: the headline itself stays true (the architecture
baseline is open and LAYER-STATUS says FOUNDATIONS_BASELINED is not reached); the sentence dates itself by the review
it cites; START-HERE names the registry as the single authority for requirements; and the error is on the cautious
side. It is the one unmarked contradiction of layer 3's status in a current page, so it belongs in the errata that
travel with H3, and in the renderer at the next tool change.

**m2. Five records of `v2/docs/records/h3/` no longer match their index rows, and one quoted time is off.**
`v2/docs/records/README.md` lines 333, 334, 337, 339 and 341 give for `design_difference.out`,
`design_difference.py`, `public_check.out`, `same_patches.out` and `zip_size_estimate.out` the sha256 values
`d48a7b52...`, `288f2d34...`, `11c9c50b...`, `9f4fee64...` and `f9418128...`; the files carried are `b687163f...`,
`834da59b...`, `ccc3ece5...`, `9add3fd6...` and `9b7899b1...` (and 15,434 bytes against 13,764, 3270 against 3276).
Cause, read on the public repository: the snapshot's source commit `75ad6ee5` re-took exactly these five files and
changed no other file. Of 832 index rows with a sha256, 817 match. START-HERE section 4 says the records are "filed
byte for byte with sha256 (`v2/docs/records/README.md`)". The same re-take left RELEASE-H3.md line 99 and
REGENERATE.md line 439 saying the public check was "Asked on 27 September 2026 at 20:38 UTC", where
`public_check.out` begins "asked at 2026-09-27 21:04 UTC". The facts the record states are those the pages give; the
index and the time are not. No page explains either. `MANIFEST.tsv` carries the right hashes.

**m3. `design_difference.out` compares with the commit before the snapshot's source.**
Its first line reads "b89b50b4 (H2's source commit) to HEAD (089f7f27)". The snapshot is built from `75ad6ee5`.
`089f7f27` is not in SOURCE.txt's timeline, so a reader of the ZIP cannot place it. LAYER-STATUS lines 80 to 83 cite
the record for "Between H2's source commit `b89b50b4` and H3's". RELEASE-H3.md words it more exactly ("the commit
these pages were written on"). I closed the gap: `75ad6ee5` changes only five files under `v2/docs/records/h3/`.

**m4. "17 warnings" is H2's figure; H3 reads 20.**
START-HERE line 225 and lines 415 to 417, and LAYER-STATUS line 134, give "from the ZIP alone 13 errors and 17
warnings" in rows that carry H3 marks for other things. REGENERATE.md lines 144, 391 and 403 to 406 give 17 as well,
and its paragraph "Edition H3" (lines 57 to 62) gives the figure for H3: 20, read by the re-check on an export of
`2c12be91`, with section 7's other counts "inferred ... not run". My run from the H3 ZIP: 13 errors and 20 warnings;
after the fetch of section 1a, 0 errors and 20 warnings. So the right figure is in the package, in one place, and the
three other places are not marked.

**m5. The registry's header does not state what changed in the registry after the re-check.**
The header ends with the paragraph on the re-check of the baseline. After it, `fa89c7c6` and `edd3c848` re-took
`needs_document_sha256` twice and rebound the readings of REQ-005, CFL-014 and CFL-016, and the header has no
paragraph on it (a search of the file for "restructur", `a9f212c7`, `fa89c7c6`, `edd3c848` finds only the three
records' evidence entries). The header did state the same kind of change when `62f26a44` made it, and a registry
difference the header did not state is what reversed the baseline once (S-80). The change is stated elsewhere in the
package (the three entries, RELEASE-H3.md, DEFINITION-STATUS.md, `design_difference.out`) and my comparison finds no
protected field changed.

**m6. Item 3.15 was judged on ten unlinked open items; the registry carried has twenty-four.**
LAYER-STATUS line 292 keeps "MET in substance" from the second release check, which counted ten open items in no
record's `waits_on`. In H3's registry they are: L-01, S-13, S-23, S-47, S-56, S-60, S-61, S-62, S-63, S-64 to S-76,
S-79 and S-81. The thirteen of set 5 were added after the review read the file. One of them decides a verdict: S-64
(W3T-F1) is the item under which CON-010, core and BLOCKER, reads FAIL, and CON-010 has no `waits_on`. The review's
own note n7 proposed restating the item as "every open item that can change a record's verdict is carried by it".
The failure is not hidden (CON-010's newest evidence entry names S-64 and EQ-25); the link is missing, and the table
does not give the count.

**m7. "COMPLETE since commit `24e7bf5a`" dates completeness before one acceptance item was met.**
By the page's own definition COMPLETE needs the versioned package, and the second release check's verdict says
"What closes it: the B-1 commit ..., then B-2 (pushed, and a snapshot cut from it)". At `24e7bf5a` item 3.18 and
S-79 were open. The pages state 3.18 apart each time, and layers 1 and 2 were dated the same way, so a reader of H3
is not misled about H3: in H3 all three conditions hold. It is a matter of wording.

**m8. "No definition change" is stated without the two exceptions its own check names.**
The check of the restructure says two moved blocks "carry definition content as well as a result" (m1: "after the
move the brief's definition names neither SC-04 nor the fit as a core condition"; m2: "the brief no longer describes
the lamp") and that the content stays in kept CONOPS text. DEFINITION-STATUS.md reports both and the decision taken.
START-HERE section 1a, LAYER-STATUS "Status at handover H3", RELEASE-H3.md and the brief's own status paragraph
("found every definition statement of that text here word for word") give the verdict without them. Related: the
sentence and the open-items row that closed layer 1's blocking finding R2-B1 (seven core blockers, FEA-007) now
stand on DEFINITION-STATUS.md (entry B-S8) and in the brief's appendix, headed "Nothing below is maintained", and
LAYER-STATUS rows 1.5 and 1.7 do not say so; the integrator line does. My own word by word comparison agrees with
the check on its main point: below the two heads, the brief and CONOPS of H3 are the texts of `6b2a9965` and
`62f26a44` with deletions only, no word added or moved.

**m9. A pointer in EXECUTION-PLAN.md is stale since the restructure.**
Line 82: "`CONOPS.md` carries the same definition at its top." Since the restructure that paragraph is CONOPS
appendix A2 (line 1151).

**m10. "The last tool change `7dfbfb16`" is not marked for H3.**
START-HERE lines 212 to 213 and LAYER-STATUS line 124, in sections whose rule is "What H3 changes in it is marked
H3". The packer changed after it, at `a54b1f4d`. True if "tool" means a checking tool; the sections do not say. The
two short forms of the design sentence (section 8) do not name the packer.

**m11. Erratum f is not at two points of use.** Outside layers 1 to 3.
LAYER-STATUS line 407 (item 8.10, "TRN-001 and PWR-003 now PASS") and line 411 (item 8.14, "fitted parts and TRN-001
PASS on current evidence") and `PCB-RULE-STATUS-A.md` line 70 state the PASS without saying that it does not judge
VIN_RAW's entry. The erratum is in START-HERE, in RELEASE-H3.md and in `A.md` section 7, and LAYER-STATUS "Status at
handover H3" names it in its list. Board A is held from layout by seven other reasons, decision 31's review among
them.

**m12. The records index names ten files that are not in the commit.** Outside layers 1 to 3.
`v2/docs/records/README.md` lines 268 onward list `r8int5/logs/*.log` (ten rows, each with sha256 and size). None is
in `MANIFEST.tsv`, `EXCLUDED.tsv` or `REFERENCED-SOURCES.tsv`, which together list every file of the commit. The
`.gitignore` the package carries has the rule `logs/`.

**m13. Two numberings for one item.** Presentation.
"Acceptance item 14" (LAYER-STATUS H2 row of layer 1, EQ-27, EQ-29, S-79) is row 14 of the release check, which is
item 1.12 of the acceptance table. The layer 1 section says the record "maps its rows to these items"; the places
that say "item 14" do not.

### Observations, not findings

**O1. The filing commit, read on the public repository at 21:32 UTC.** `main` is `bd96bb61` ("snapshot H3 ...
built from 75ad6ee5, and S-79 closed with it"), parent `75ad6ee5`. `H3.zip.sha256` there names the sha256 I hold, and
`H3.MANIFEST.tsv` there is byte-identical to the `MANIFEST.tsv` inside the package. Its registry differs from H3's
by S-79 alone (open 57, closed 54, `closed_by: commit 75ad6ee5`). `RELEASE-H3.md` there is byte-identical to the
draft inside the ZIP (sha256/16 `f23cbd8e1e7f9cc9`, eight `TBD-BY-INTEGRATOR`), so the build figures START-HERE tells
a reader to look for outside the ZIP are, at that commit, in the files beside the ZIP and in S-79's closing evidence
only. That evidence says "the two fresh checks of H3 are recorded in v2/docs/handover/RELEASE-H3.md"; at `bd96bb61`
they are not yet. This check is one of the two.

**O2. One review record was edited at filing.** `TARGETED-RECHECK-LAYER-3-2026-09-27.md` was filed "with one phrase
rewritten" by the integrating session. The package says so in the registry header, on LAYER-STATUS and in the records
index, with both hashes.

**O3. The commit the second release checks read is not public.** `eb9f9030` answers HTTP 404, as SOURCE.txt marks
it. The package says where its content landed (`79963b3b`). For CONOPS the file at `79963b3b` has the hash the
record gives for the file it read.

## 10. What I did not check

- The content of layers 1 to 3. I re-judged no review and no requirement, and I did not read the definitions or the
  registry's records in full.
- Layers 4 to 9, except where an erratum pointed.
- Anything that needs KiCad: regeneration, parity, the exports, the ERC, the re-take, the test suite. I ran no suite.
- The energy chain, the power and case scripts, the battery packet's manifest check, the diagrams' manifest check.
- Erratum c, and everything the package says about set 6, wave 5a and their suites: those branches are not public.
- That every block moved out of the brief and CONOPS stands word for word in an appendix or on DEFINITION-STATUS.md.
  I checked only that nothing was added below the two heads.
- Hashes quoted for files at commits that are not public, and the hashes in the audit tables of LAYER-STATUS
  Appendix A (section 4, last three rows).
- ENGINEERING-QUESTIONS.md blocks other than the head, the index and EQ-27 to EQ-30, except the seven "Corrected for
  H3" marks. LAYER-STATUS Appendix A and the trace page were searched, not read.
- GitLab. I read the public GitHub repository only.
- My scan for quoted hashes looks 160 characters back from each value for a file name. A hash quoted farther from
  its file's name would be missed; I read RELEASE-H3.md and DEFINITION-STATUS.md in full to cover the two pages that
  quote the most.

## 11. What I decided

- I used the public repository as a declared dependency, at commits SOURCE.txt marks public, and the GitHub API for
  commit lists. `H2.MANIFEST.tsv` is not bundled; I fetched it because `EXCLUDED.tsv` lists it with its blob sha.
- I read `main` of the public repository as it stood after the build (`bd96bb61`), because the pages send the reader
  to "the commit that files the snapshot". What I found there is an observation, not a finding against the package.
- I did not read the project's working repository, any other worktree, the tracker or the memory. The session's
  harness had placed the project's instruction files in my context before the task began; I opened none of them and
  took no fact from them.
- I asked nobody anything.
- I changed nothing outside my working folder, committed nothing and pushed nothing. `H3/` verifies against its
  manifest after the checks. My copy `work/H3run` with the eleven fetched documents is removed; `work/` keeps my
  outputs and the small files fetched from the public repository.
